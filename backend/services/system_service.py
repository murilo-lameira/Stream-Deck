import asyncio
import logging
import psutil
from typing import List, Set
from apps_config import APP_PROCESS_NAMES

logger = logging.getLogger("streamdeck.system")

import ctypes
from typing import List, Set, Tuple

WINDOW_KEYWORDS = {
    "youtube": ["youtube - google chrome", "youtube"],
    "gemini": ["google gemini", "gemini"],
    "github": ["github - google chrome", "github"]
}

def get_visible_window_titles_sync() -> List[str]:
    """
    Enumera as janelas visíveis no desktop ativo do usuário (Default),
    permitindo identificar abas ativas do navegador (YouTube, Gemini, GitHub).
    """
    titles: List[str] = []
    try:
        user32 = ctypes.windll.user32
        hdesk = user32.OpenDesktopW('Default', 0, False, 0x1FF)
        if hdesk:
            user32.SetThreadDesktop(hdesk)

        def enum_cb(hwnd, _lparam):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buff, length + 1)
                    titles.append(buff.value.lower())
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
    except Exception as e:
        logger.debug(f"Erro ao enumerar títulos de janelas: {e}")
    return titles

def get_running_app_keys_sync() -> List[str]:
    """
    Varre os processos ativos no Windows e as janelas visíveis abertas
    para retornar quais chaves de aplicativos do Stream Deck estão em execução.
    """
    try:
        active_exes: Set[str] = set()
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info.get('name')
                if name:
                    active_exes.add(name.lower())
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        running_keys: Set[str] = set()
        for app_key, exe_names in APP_PROCESS_NAMES.items():
            if isinstance(exe_names, (list, tuple)):
                if any(exe.lower() in active_exes for exe in exe_names):
                    running_keys.add(app_key)
            else:
                if exe_names.lower() in active_exes:
                    running_keys.add(app_key)

        # Se o Chrome ou outro navegador estiver ativo, inspeciona as janelas
        # para acender YouTube, Gemini ou GitHub quando abertos
        if "chrome" in running_keys or "chrome.exe" in active_exes:
            titles = get_visible_window_titles_sync()
            for title in titles:
                for app_key, keywords in WINDOW_KEYWORDS.items():
                    if any(kw in title for kw in keywords):
                        running_keys.add(app_key)

        return list(running_keys)
    except Exception as e:
        logger.debug(f"Erro ao verificar processos em execucao: {e}")
        return []

async def get_running_app_keys() -> List[str]:
    """Versao assincrona para nao travar o loop de eventos."""
    return await asyncio.to_thread(get_running_app_keys_sync)

