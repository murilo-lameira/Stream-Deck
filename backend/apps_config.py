import os
import subprocess
import logging
import ctypes
import asyncio
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
        "whatsapp:"
    ],
    "shutdown_pc": [
        "shutdown", "/s", "/t", "0"
    ],
    "obs": [
        os.path.expandvars(r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs\OBS Studio.lnk")
    ],
    "blitz": [
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Blitz.lnk")
    ],
    "youtube": [
        os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
        "https://youtube.com"
    ],
    "github": [
        os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
        "https://github.com"
    ],
    "ghub": [
        os.path.expandvars(r"%PROGRAMFILES%\LGHUB\lghub.exe")
    ],
    "vms": [
        os.path.expandvars(r"%PROGRAMFILES%\VMS\VMS.exe")
    ],
    "checkup": [
        r"F:\Faculdade\Projetos\Projeto CheckUP\dist\CheckUP Windows 1.2.0.exe"
    ]
}

APP_PROCESS_NAMES = {
    "vscode": ("code.exe",),
    "discord": ("discord.exe",),
    "chrome": ("chrome.exe",),
    "spotify": ("spotify.exe",),
    "obsidian": ("obsidian.exe",),
    "whatsapp": ("whatsapp.exe", "whatsapp.root.exe"),
    "steam": ("steam.exe",),
    "lol": ("leagueclient.exe", "leagueclientux.exe", "riotclientservices.exe"),
    "obs": ("obs64.exe", "obs32.exe", "obs.exe"),
    "blitz": ("blitz.exe",),
    "ghub": ("lghub.exe", "lghub_agent.exe", "lghub_system_tray.exe"),
    "vms": ("vms.exe",),
    "checkup": ("checkup windows 1.2.0.exe", "checkup.exe")
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

def bring_to_foreground(target: str, is_window_title: bool = False) -> bool:
    """
    Traz a janela do aplicativo para o primeiro plano.
    Pode buscar por nome do processo (ex: 'code.exe') ou por palavra-chave no título (ex: 'gemini', 'youtube').
    """
    import psutil
    try:
        user32 = ctypes.windll.user32
        hdesk = user32.OpenDesktopW('Default', 0, False, 0x1FF)
        if hdesk:
            user32.SetThreadDesktop(hdesk)

        SW_RESTORE = 9
        GW_OWNER = 4
        found_hwnd = None
        target_lower = target.lower()

        if is_window_title:
            def enum_title_proc(hwnd, _lParam):
                nonlocal found_hwnd
                if not user32.IsWindowVisible(hwnd):
                    return 1
                length = user32.GetWindowTextLengthW(hwnd)
                if length == 0:
                    return 1
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                if target_lower in buff.value.lower():
                    found_hwnd = hwnd
                    return 0
                return 1

            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)
            user32.EnumWindows(WNDENUMPROC(enum_title_proc), 0)
        else:
            if isinstance(target, (list, tuple)):
                target_names = {t.lower() for t in target}
            else:
                target_names = {target_lower}

            target_pids = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] and proc.info['name'].lower() in target_names:
                        target_pids.append(proc.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            if not target_pids:
                return False
                
            def enum_windows_proc(hwnd, _lParam):
                nonlocal found_hwnd
                if not user32.IsWindowVisible(hwnd):
                    return 1
                if user32.GetWindow(hwnd, GW_OWNER) != 0:
                    return 1
                length = user32.GetWindowTextLengthW(hwnd)
                if length == 0:
                    return 1
                process_id = ctypes.c_ulong()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
                if process_id.value in target_pids:
                    found_hwnd = hwnd
                    return 0
                return 1
                
            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)
            user32.EnumWindows(WNDENUMPROC(enum_windows_proc), 0)
        
        if found_hwnd:
            if user32.IsIconic(found_hwnd):
                user32.ShowWindow(found_hwnd, SW_RESTORE)
            
            user32.keybd_event(0x12, 0, 0, 0)
            user32.keybd_event(0x12, 0, 2, 0)
            user32.SetForegroundWindow(found_hwnd)
            return True
            
        return False
    except Exception as e:
        logger.error(f"Erro ao focar {target}: {e}")
        return False

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
    # Verifica se o aplicativo já está rodando e traz para frente
    WINDOW_TITLE_KEYWORDS = {
        "gemini": "gemini",
        "youtube": "youtube",
        "github": "github"
    }
    if app_key in WINDOW_TITLE_KEYWORDS:
        if bring_to_foreground(WINDOW_TITLE_KEYWORDS[app_key], is_window_title=True):
            logger.info(f"Janela encontrada e focada para: {app_key}")
            return True

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


async def launch_app_async(app_key: str) -> bool:
    """
    Versão assíncrona não-bloqueante de launch_app.
    Executa a verificação e abertura de processos em thread separada
    para nunca bloquear o loop de eventos principal do FastAPI/WebSockets.
    """
    return await asyncio.to_thread(launch_app, app_key)

