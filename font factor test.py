import ctypes
from ctypes import wintypes
import shutil

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
    
    # Get current terminal size using shutil
    terminal_size = shutil.get_terminal_size()
    columns, rows = terminal_size.columns, terminal_size.lines
    
    return hConsole, font_info, columns, rows

def set_console_font_size(font_width=8, font_height=12, maintain_window_size=True):
    """
    Set font size and optionally maintain window dimensions
    
    Parameters:
    - font_width, font_height: Font dimensions
    - maintain_window_size: If True, keeps the same window dimensions in characters
    """
    kernel32 = ctypes.windll.kernel32
    hConsole, original_font_info, original_columns, original_rows = get_console_info()
    
    # Store original settings for restoration
    original_settings = {
        'font_size': (original_font_info.dwFontSize.X, original_font_info.dwFontSize.Y),
        'columns': original_columns,
        'rows': original_rows
    }
    
    # Set font size
    font_info = CONSOLE_FONT_INFOEX()
    font_info.cbSize = ctypes.sizeof(CONSOLE_FONT_INFOEX)
    kernel32.GetCurrentConsoleFontEx(hConsole, False, ctypes.byref(font_info))
    
    font_info.dwFontSize.X = font_width
    font_info.dwFontSize.Y = font_height
    kernel32.SetCurrentConsoleFontEx(hConsole, False, ctypes.byref(font_info))
    
    # Maintain window size if requested
    if maintain_window_size:
        new_columns = int(2*original_columns/(font_width/original_font_info.dwFontSize.X))
        new_rows = int(original_rows/(font_height/original_font_info.dwFontSize.Y))
        print("new size:", (new_columns, new_rows))
        # Set buffer size first (must be at least as large as window size)
        buffer_size = wintypes._COORD(new_columns, new_rows)
        kernel32.SetConsoleScreenBufferSize(hConsole, buffer_size)
        
        # Set window size to maintain dimensions
        window_rect = wintypes.SMALL_RECT(0, 0, new_columns - 1, new_rows - 1)
        kernel32.SetConsoleWindowInfo(hConsole, True, ctypes.byref(window_rect))
    
    return original_settings

input()
s = set_console_font_size(8, 8)
input(s)
set_console_font_size(*s['font_size'])
input(">>>")