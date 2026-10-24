import os
from typing import Dict, List, Tuple

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
        os.getenv(
            "CHECKUP_EXE_PATH",
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "Projeto CheckUP", "dist", "CheckUP Windows 1.2.0.exe"))
        )
    ]
}

APP_PROCESS_NAMES: Dict[str, Tuple[str, ...]] = {
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
SYSTEM_KEYS: Dict[str, int] = {
    "sys_vol_up": 0xAF,
    "sys_vol_down": 0xAE,
    "sys_vol_mute": 0xAD,
    "sys_media_next": 0xB0,
    "sys_media_prev": 0xB1,
    "sys_media_playpause": 0xB3
}

WINDOW_TITLE_KEYWORDS: Dict[str, str] = {
    "gemini": "gemini",
    "youtube": "youtube",
    "github": "github"
}
