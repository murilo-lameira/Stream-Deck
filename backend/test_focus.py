import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

def focus_window_by_title_substring(substring):
    found_hwnds = []
    
    def enum_windows_callback(hwnd, extra):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                title = buff.value
                if substring.lower() in title.lower():
                    found_hwnds.append((hwnd, title))
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(WNDENUMPROC(enum_windows_callback), 0)
    
    if found_hwnds:
        hwnd, title = found_hwnds[0]
        print(f"Janela encontrada: {title} (HWND: {hwnd})")
        # Restaura se estiver minimizada
        user32.ShowWindow(hwnd, 9) # SW_RESTORE
        user32.SetForegroundWindow(hwnd)
        return True
    return False

print("Testando foco no Obsidian:", focus_window_by_title_substring("Obsidian"))
