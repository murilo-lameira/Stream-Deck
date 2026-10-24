import ctypes
import logging
from typing import Any, Union, List, Tuple

logger = logging.getLogger("streamdeck.window")

def simulate_key(vk_code: int) -> None:
    """Simula o pressionamento e soltura de uma tecla virtual do Windows (keybd_event)."""
    try:
        ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
        ctypes.windll.user32.keybd_event(vk_code, 0, 2, 0)
    except Exception as e:
        logger.error(f"Erro ao simular tecla {vk_code}: {e}")

def bring_to_foreground(target: Union[str, List[str], Tuple[str, ...]], is_window_title: bool = False) -> bool:
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

        if is_window_title:
            target_lower = str(target).lower()
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
                target_names = {str(t).lower() for t in target}
            else:
                target_names = {str(target).lower()}

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
