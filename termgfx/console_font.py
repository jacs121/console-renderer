import ctypes
from ctypes import wintypes
import shutil
from vectors import Vector2

class CONSOLE_FONT_INFOEX(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.ULONG),
        ("nFont", wintypes.DWORD),
        ("dwFontSize", wintypes._COORD),
        ("FontFamily", wintypes.UINT),
        ("FontWeight", wintypes.UINT),
        ("FaceName", wintypes.WCHAR * 32)
    ]

def get_console_info():
    """Get current console information"""
    kernel32 = ctypes.windll.kernel32
    hConsole = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
    
    # Get font info
    font_info = CONSOLE_FONT_INFOEX()
    font_info.cbSize = ctypes.sizeof(CONSOLE_FONT_INFOEX)
    kernel32.GetCurrentConsoleFontEx(hConsole, False, ctypes.byref(font_info))
    fontSize = Vector2(font_info.dwFontSize.X*2, font_info.dwFontSize.Y)
    
    # Get current terminal size using shutil
    terminal_size = shutil.get_terminal_size()
    terminalSize = Vector2(terminal_size.columns*2, terminal_size.lines*2)
    
    return hConsole, (fontSize, terminalSize)

def set_console_font_size(fontSize: Vector2 = Vector2(8, 16)):
    kernel32 = ctypes.windll.kernel32
    hConsole, (original_font_size, originalTerminalSize) = get_console_info()
    input(f"prev size: {original_font_size}")
    
    # Set font size
    font_info = CONSOLE_FONT_INFOEX()
    font_info.cbSize = ctypes.sizeof(CONSOLE_FONT_INFOEX)
    kernel32.GetCurrentConsoleFontEx(hConsole, False, ctypes.byref(font_info))
    
    font_info.dwFontSize.X = fontSize.x
    font_info.dwFontSize.Y = fontSize.y
    kernel32.SetCurrentConsoleFontEx(hConsole, False, ctypes.byref(font_info))
    newWindowSize = (originalTerminalSize)//(fontSize/(original_font_size))
    # newWindowSize = Vector2(newWindowSize.x, newWindowSize.y)
    
    # Set buffer size first (must be at least as large as window size)
    buffer_size = wintypes._COORD(int(newWindowSize.y), int(newWindowSize.x))
    kernel32.SetConsoleScreenBufferSize(hConsole, buffer_size)
    
    # Set window size to maintain dimensions
    window_rect = wintypes.SMALL_RECT(0, 0, int(newWindowSize.x) - 1, int(newWindowSize.y) - 1)
    kernel32.SetConsoleWindowInfo(hConsole, True, ctypes.byref(window_rect))
    
    return original_font_size

s = set_console_font_size(Vector2(8, 8))
input(f"original font: {s}\nnew size {Vector2(8, 8)}\n")
set_console_font_size(s)
input(">>>")