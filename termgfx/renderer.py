import shutil
import sys
import colorama
import time
from .colors import *
from .textures import *
from .vectors import *
import types
import ctypes
from typing import List, Tuple, Optional

class ConsoleRenderer():
    def __init__(self, tick: Optional[types.FunctionType] = None, 
                 sizeChange: Optional[types.FunctionType] = None, 
                 bg: Color = Color("RGB", [0, 0, 0]), 
                 disableConsoleCursor: bool = True):
        colorama.just_fix_windows_console()
        self.__running__ = False

        self.onTick = tick
        self.onSizeChange = sizeChange
        self.__bg__ = bg
        self.__disable_console_cursor__ = disableConsoleCursor
        self.__prevFrame__ = None
        self.__prevFrameStr__ = ""  # Store the previous frame as string for comparison

    def stop(self):
        self.__running__ = False
    
    def run(self, fps: int = 60):
        size = self.get_resolution()
        self.__running__ = True
        
        if self.__disable_console_cursor__ and sys.platform.startswith('win'):
            try:
                kernel32 = ctypes.windll.kernel32
                h_stdin = kernel32.GetStdHandle(-10)
                mode = ctypes.c_uint32()
                kernel32.GetConsoleMode(h_stdin, ctypes.byref(mode))
                new_mode = mode.value & ~0x40
                kernel32.SetConsoleMode(h_stdin, new_mode)
            except Exception:
                pass
        
        sys.stdout.write("\033c")
        while self.__running__:
            _size = self.get_resolution()
            if size != _size:
                size = _size
                if self.onSizeChange:
                    out = self.onSizeChange(Vector2(size.y, size.x))
                    if out is not None:
                        self.__show_pixels__(self.__get_pixel_display_list__(out))
                        self.__prevFrame__ = out
            
            pixels = self.onTick(Vector2(size.y, size.x))
            self.__show_pixels__(self.__get_pixel_display_list__(pixels))
            time.sleep(1/fps)
            
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    def showFrame(self):
        size = self.get_resolution()
        pixels = self.onTick(Vector2(size.y, size.x))

        sys.stdout.write("\033c")
        self.__show_pixels__(self.__get_pixel_display_list__(pixels))

    def overlayOnCanvas(self, canvas: List[List[Tuple[int, int, int]]], 
                       layer: List[List[Tuple[int, int, int]]], 
                       position: Tuple[int, int]) -> List[List[Tuple[int, int, int]]]:
        for y in range(len(layer)):
            for x in range(len(layer[0])):
                canvas_y = y + position[1]
                canvas_x = x + position[0]
                
                if 0 <= canvas_x < len(canvas[0]) and 0 <= canvas_y < len(canvas):
                    overlay_pixel = layer[y][x]
                    alpha = overlay_pixel[3] if len(overlay_pixel) == 4 else 1.0
                    alpha = min(max(alpha, 0), 1)
                    
                    base_pixel = canvas[canvas_y][canvas_x]
                    canvas[canvas_y][canvas_x] = (
                        int(base_pixel[0] * (1 - alpha) + overlay_pixel[0] * alpha),
                        int(base_pixel[1] * (1 - alpha) + overlay_pixel[1] * alpha),
                        int(base_pixel[2] * (1 - alpha) + overlay_pixel[2] * alpha)
                    )
        return canvas

    def __pixel__(self, colorTop: Color, colorBottom: Color, 
                 pre: Optional[Tuple[Color, Color]] = None) -> str:
        """Generate a terminal pixel with proper color formatting"""
        # Ensure colors are in RGB format
        top_r, top_g, top_b = colorTop.r, colorTop.g, colorTop.b
        bottom_r, bottom_g, bottom_b = colorBottom.r, colorBottom.g, colorBottom.b
        
        if pre is None:
            return f"\033[38;2;{top_r};{top_g};{top_b}m" \
                   f"\033[48;2;{bottom_r};{bottom_g};{bottom_b}m\u2580"
        
        pix = ""
        pre_top, pre_bottom = pre
        
        # Only update colors if they changed from previous pixel
        if pre_top != colorTop:
            pix += f"\033[38;2;{top_r};{top_g};{top_b}m"
        if pre_bottom != colorBottom:
            pix += f"\033[48;2;{bottom_r};{bottom_g};{bottom_b}m"

        return pix + "\u2580"

    def get_resolution(self) -> Vector2:
        """Get the resolution in pixels (width, height)"""
        size = shutil.get_terminal_size()
        # Each character row displays 2 pixel rows
        return Vector2(size.columns, size.lines * 2)

    def __get_pixel_display_list__(self, texture: Texture) -> List[List[Color]]:
        """Convert texture to displayable pixel list"""
        resolution = self.get_resolution()
        width, height = int(resolution.x), int(resolution.y)

        # Create display buffer with background color
        pixel_list = []
        for y in range(height):
            row = []
            for x in range(width):
                try:
                    # Sample texture at current position
                    color = texture[Vector2(x, y)]
                    row.append(color)
                except (IndexError, ValueError):
                    # Fallback to background color
                    row.append(self.__bg__)
            pixel_list.append(row)
            
        return pixel_list

    def __show_pixels__(self, pixel_data: List[List[Color]]): # -< to slow
        """Render pixel data to console with optimized updates"""
        height = len(pixel_data)
        if height == 0:
            return
        width = len(pixel_data[0])
        
        # Build the frame string
        frame_str = ""
        
        for y in range(0, height, 2):
            line_str = ""
            prev_colors = None
            
            for x in range(width):
                top_color = pixel_data[y][x]
                bottom_color = pixel_data[y + 1][x] if y + 1 < height else self.__bg__
                
                pixel_str = self.__pixel__(top_color, bottom_color, prev_colors)
                line_str += pixel_str
                prev_colors = (top_color, bottom_color)
            
            frame_str += line_str + "\033[0m\n"  # Reset colors at end of line
        
        # Only redraw if the frame changed
        if frame_str != self.__prevFrameStr__:
            colorama.just_fix_windows_console()
            sys.stdout.write("\033[0;0H"+frame_str[:-1])
            sys.stdout.flush()
            self.__prevFrameStr__ = frame_str