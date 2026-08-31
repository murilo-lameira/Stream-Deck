import os
import subprocess
import logging
import ctypes
from typing import Dict, List, Optional

logger = logging.getLogger("streamdeck.apps")

# Mapeamento de aplicativos suportados (ID -> Comando e argumentos)
APPS_MAP: Dict[str, List[str]] = {
    "vscode": [
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe")
    ],
    "discord": [
        os.path.expandvars(r"%LOCALAPPDATA%\Discord\Update.exe"),
        "--processStart",
        "Discord.exe"
    ],
    "chrome": [
        os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe")
    ],
    "spotify": [
        os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe")
    ],
    "gemini": [
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\apps do Chrome\Gemini.lnk")
    ],
    "lol": [
        os.path.expandvars(r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs\Riot Games\League of Legends.lnk")
    ],
    "steam": [
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Steam\Steam.lnk")
    ],
    "obsidian": [
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Obsidian.lnk")
    ],
    "whatsapp": [
        "explorer.exe",
        "whatsapp:"
    ],
    "shutdown_pc": [
        "shutdown", "/s", "/t", "0"
    ]
}

# Códigos virtuais do Windows para Mídia e Volume
SYSTEM_KEYS = {
    "sys_vol_up": 0xAF,
    "sys_vol_down": 0xAE,
    "sys_vol_mute": 0xAD,
    "sys_media_next": 0xB0,
    "sys_media_prev": 0xB1,
    "sys_media_playpause": 0xB3
}

def simulate_key(vk_code: int):
    ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
    ctypes.windll.user32.keybd_event(vk_code, 0, 2, 0)

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
        try:
            simulate_key(SYSTEM_KEYS[app_key])
            logger.info(f"Comando de sistema executado com sucesso: {app_key}")
            return True
        except Exception as e:
            logger.error(f"Erro ao executar comando de sistema '{app_key}': {e}", exc_info=True)
            return False

    # Fluxo normal para aplicativos
    command = APPS_MAP.get(app_key)
    if not command:
        logger.warning(f"Aplicativo '{app_key}' nao encontrado no mapeamento.")
        return False

    try:
        cmd_str = command[0].lower()
        # Se for um link (.lnk) ou um protocolo/URI nativo (whatsapp:, spotify:, etc)
        if os.name == 'nt' and (cmd_str.endswith(".lnk") or cmd_str.endswith(":") or len(command) == 1):
            # os.startfile abre a janela visível usando o Shell do Windows
            # E se len(command) == 1 (sem argumentos extras), startfile é o jeito mais confiável
            os.startfile(command[0])
        else:
            # Caso tenha argumentos (como o Discord), usamos Popen
            creation_flags = 0
            startupinfo = None
            if os.name == 'nt':
                creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP
                # Força a janela a abrir visível mesmo se o Python estiver rodando oculto (VBS)
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
