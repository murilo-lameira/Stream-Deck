import os
import subprocess
import logging
import asyncio
from typing import Optional

from config.apps_registry import (
    APPS_MAP,
    APP_PROCESS_NAMES,
    SYSTEM_KEYS,
    WINDOW_TITLE_KEYWORDS,
)
from services.window_service import simulate_key, bring_to_foreground

logger = logging.getLogger("streamdeck.process")

def launch_app(app_key: str) -> bool:
    """
    Abre o aplicativo ou executa comando de sistema (Mídia/Volume).
    """
    app_key = app_key.lower().strip()

    if app_key == "sys_mic_mute":
        try:
            from audio_service import toggle_mic_mute
            toggle_mic_mute()
            logger.info("Comando de sistema executado com sucesso: sys_mic_mute")
            return True
        except Exception as e:
            logger.error(f"Erro ao alternar mic: {e}")
            return False

    # Intercepta comandos nativos de mídia/volume
    if app_key in SYSTEM_KEYS:
        # Tenta controle nativo via WinRT para comandos de mídia
        if app_key in ("sys_media_playpause", "sys_media_next", "sys_media_prev"):
            try:
                from services.media_service import control_media_action_sync
                if control_media_action_sync(app_key):
                    logger.info(f"Comando de mídia executado via WinRT nativo: {app_key}")
                    return True
            except Exception as e:
                logger.debug(f"WinRT media control indisponível, usando fallback: {e}")

        try:
            simulate_key(SYSTEM_KEYS[app_key])
            logger.info(f"Comando de sistema executado com sucesso: {app_key}")
            return True
        except Exception as e:
            logger.error(f"Erro ao executar comando de sistema '{app_key}': {e}", exc_info=True)
            return False

    # Fluxo normal para aplicativos
    # Verifica se o aplicativo já está rodando e traz para frente por título
    if app_key in WINDOW_TITLE_KEYWORDS:
        if bring_to_foreground(WINDOW_TITLE_KEYWORDS[app_key], is_window_title=True):
            logger.info(f"Janela encontrada e focada para: {app_key}")
            return True

    # Verifica se o aplicativo já está rodando e traz para frente por processo
    process_name = APP_PROCESS_NAMES.get(app_key)
    if process_name and bring_to_foreground(process_name):
        logger.info(f"Aplicativo já estava rodando, trazido para o primeiro plano: {app_key}")
        return True

    command = APPS_MAP.get(app_key)
    if not command:
        logger.warning(f"Aplicativo '{app_key}' nao encontrado no mapeamento.")
        return False

    try:
        cmd_str = command[0].lower()
        # Se for um link (.lnk) ou um protocolo/URI nativo (whatsapp:, spotify:, etc)
        if os.name == 'nt' and (cmd_str.endswith(".lnk") or cmd_str.endswith(":") or len(command) == 1):
            os.startfile(command[0])
        else:
            creation_flags = 0
            startupinfo = None
            if os.name == 'nt':
                creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 1 # SW_SHOWNORMAL

            subprocess.Popen(
                command,
                creationflags=creation_flags,
                startupinfo=startupinfo,
                close_fds=True
            )
            
        logger.info(f"Aplicativo disparado com sucesso: {app_key} -> {command}")
        return True
    except Exception as e:
        logger.error(f"Erro ao disparar aplicativo '{app_key}': {e}", exc_info=True)
        return False

async def launch_app_async(app_key: str) -> bool:
    """
    Versão assíncrona não-bloqueante de launch_app.
    Executa a verificação e abertura de processos em thread separada
    para nunca bloquear o loop de eventos principal do FastAPI/WebSockets.
    """
    return await asyncio.to_thread(launch_app, app_key)
