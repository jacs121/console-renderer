def create_console(font_size: int, window_name: str = "Term-GFX Accurate Console", font_name: str = "Consolas"):
    import platform
    import sys

    if platform.system() == "Windows":
        
        import subprocess
        import time
        import ctypes
        from ctypes import wintypes

        # --- Structures ---
        class COORD(ctypes.Structure):
            _fields_ = [("X", wintypes.SHORT), ("Y", wintypes.SHORT)]

        class CONSOLE_FONT_INFOEX(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.ULONG),
                ("nFont", wintypes.DWORD),
                ("dwFontSize", COORD),
                ("FontFamily", wintypes.UINT),
                ("FontWeight", wintypes.UINT),
                ("FaceName", wintypes.WCHAR * 32)
            ]

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        STD_OUTPUT_HANDLE = -11
        GetStdHandle = kernel32.GetStdHandle
        GetCurrentConsoleFontEx = kernel32.GetCurrentConsoleFontEx

        def get_console_font_pixels():
            handle = GetStdHandle(STD_OUTPUT_HANDLE)
            font = CONSOLE_FONT_INFOEX()
            font.cbSize = ctypes.sizeof(CONSOLE_FONT_INFOEX)
            if not GetCurrentConsoleFontEx(handle, False, ctypes.byref(font)):
                raise ctypes.WinError(ctypes.get_last_error())
            width = max(1, font.dwFontSize.X)
            height = max(1, font.dwFontSize.Y)
            return width, height

        def get_console_size_chars():
            """Return current console size in (cols, lines)."""
            csbi = ctypes.create_string_buffer(22)
            handle = GetStdHandle(STD_OUTPUT_HANDLE)
            if not kernel32.GetConsoleScreenBufferInfo(handle, csbi):
                return (80, 25)
            import struct
            (bufx, bufy, curx, cury, wattr,
            left, top, right, bottom,
            maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            cols = right - left + 1
            lines = bottom - top + 1
            return cols, lines
    
        # --- Get current console metrics ---
        old_cols, old_lines = get_console_size_chars()
        old_char_width, old_char_height = get_console_font_pixels()

        # --- Clamp font size to minimum 8px ---
        new_font_height = max(8, font_size)

        # --- Total window pixels ---
        total_width_px = old_cols * old_char_width
        total_height_px = old_lines * old_char_height

        # --- Compute new character pixel size ---
        new_char_width = max(1, int(old_char_width * new_font_height / old_char_height))
        new_char_height = new_font_height

        # --- Compute new cols/lines ---
        new_cols = max(1, total_width_px // new_char_width)
        new_lines = max(1, total_height_px // new_char_height)

        # --- Registry subkey for console ---
        subkey_path = rf"Console\{window_name}"
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey_path, 0, winreg.KEY_ALL_ACCESS)
        except FileNotFoundError:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, subkey_path)

        # --- Save old settings ---
        try:
            old_font_size, _ = winreg.QueryValueEx(key, "FontSize")
        except FileNotFoundError:
            old_font_size = None
        try:
            old_face_name, _ = winreg.QueryValueEx(key, "FaceName")
        except FileNotFoundError:
            old_face_name = None

        # --- Apply new font ---
        font_dword = (new_font_height << 16) | 0
        winreg.SetValueEx(key, "FontSize", 0, winreg.REG_DWORD, font_dword)
        winreg.SetValueEx(key, "FaceName", 0, winreg.REG_SZ, font_name)
        winreg.CloseKey(key)

        # --- Launch console ---
        popen = subprocess.Popen(
            f'start "{window_name}" cmd /k mode con:cols={new_cols} lines={new_lines}',
            shell=True,
            text=True,
            stdout=subprocess.STDOUT
        )

        time.sleep(0.3)

        # --- Restore old settings ---
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey_path, 0, winreg.KEY_ALL_ACCESS)
        if old_font_size is not None:
            winreg.SetValueEx(key, "FontSize", 0, winreg.REG_DWORD, old_font_size)
        if old_face_name is not None:
            winreg.SetValueEx(key, "FaceName", 0, winreg.REG_SZ, old_face_name)
        winreg.CloseKey(key)
        return popen
    else:
        continueProcess = input("this program is using a windows only feature!\nif you would like to continue remember that you many experience some issues.\n(Y/n)>>>")
        if continueProcess.lower() != "y":
            sys.exit(-1)