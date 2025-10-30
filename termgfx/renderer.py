import shutil
import sys
import colorama
import time
from .colors import *
from .textures import *
from .vectors import *
import types
import ctypes
import threading
import os
from typing import List, Tuple, Optional

class ConsoleRenderer():
    def __init__(self, tick: Optional[types.FunctionType] = None, 
                 sizeChange: Optional[types.FunctionType] = None, 
                 bg: Color = Color("RGB", [0, 0, 0]),
                 disableConsoleCursor: bool = True, threadCount: int = min(os.cpu_count(), 6)):
        colorama.just_fix_windows_console()
        self.__running__ = False

        self.onTick = tick
        self.onSizeChange = sizeChange
        self.__bg__ = bg
        self.__prevFrameStr__ = ""

        self.__frameStr__ = ""
        self.__frameOut__ = None
        self.threadCount = threadCount
        self.__frameThreads__: list[threading.Thread] = []
        
        self.__disable_console_cursor__ = disableConsoleCursor
        self.__prevFrame__ = None
        self.__prevFrameStr__ = ""  # Store the previous frame as string for comparison

    def stop(self):
        self.__running__ = False
    
    
    def __displayThreadFunc__(self, start: Vector2, end: Vector2):
        """
        Display a portion of the frame (from start.x to end.x, covering all y) in a separate thread.
        This function continuously updates the assigned region until rendering stops.
        """
        while self.__running__:
            # If no frame data yet, wait briefly
            if self.__frameOut__ is None:
                time.sleep(0.01)
                continue

            pixel_data = self.__frameOut__
            height = len(pixel_data)
            if height == 0:
                time.sleep(0.01)
                continue
            width = len(pixel_data[0])

            start_x = int(start.x)
            end_x = int(min(end.x, width))

            lines = []

            for y in range(0, height, 2):
                line_parts = []
                prev_colors = None

                for x in range(start_x, end_x):
                    top_color = pixel_data[y][x]
                    bottom_color = pixel_data[y + 1][x] if y + 1 < height else self.__bg__

                    if prev_colors is None or prev_colors[0] != top_color:
                        line_parts.append(f"\033[38;2;{top_color.r};{top_color.g};{top_color.b}m")
                    if prev_colors is None or prev_colors[1] != bottom_color:
                        line_parts.append(f"\033[48;2;{bottom_color.r};{bottom_color.g};{bottom_color.b}m")

                    line_parts.append("\u2580")
                    prev_colors = (top_color, bottom_color)

                # Move cursor to correct location before writing line
                lines.append(f"\033[{(y // 2) + 1};{start_x + 1}H" + "".join(line_parts) + "\033[0m")

            # Write all lines for this thread slice
            output = "".join(lines)
            sys.stdout.write(output)
            sys.stdout.flush()

            # Slight delay to sync FPS loop
            time.sleep(0.001)


    def __startThreads__(self):
        threadScreenSize = int(self.screenResolution.x // self.threadCount)
        self.__running__ = False
        for t in self.__frameThreads__:
            if t.is_alive():
                t.join(timeout=0.01)

        self.__running__ = True
        self.__frameThreads__ = []

        for threadNum in range(self.threadCount):
            start = Vector2(threadScreenSize * threadNum, 0)
            end = Vector2(threadScreenSize * (threadNum + 1), self.screenResolution.y)
            thread = threading.Thread(target=self.__displayThreadFunc__, args=(start, end))
            self.__frameThreads__.append(thread)
            thread.start()
        
    def run(self, fps: int = 60):
        size = self.screenResolution
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
        
        self.__startThreads__()
        
        while self.__running__:
            _size = self.screenResolution
            if size != _size:
                size = _size
                if self.onSizeChange:
                    out = self.onSizeChange(Vector2(size.y, size.x))
                    self.__prevFrame__ = out
                    self.__frameStr__ = self.__get_pixel_display_list__(pixels)
                    self.__startThreads__()
            
            out = self.onTick(Vector2(size.y, size.x))
            if self.__prevFrame__ != out:
                pixels = self.onTick(Vector2(size.y, size.x))
                self.__frameOut__ = self.__get_pixel_display_list__(pixels)
            time.sleep(1/fps)
            
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    def showFrame(self):
        size = self.screenResolution
        pixels = self.onTick(Vector2(size.y, size.x))
        self.__frameOut__ = self.__get_pixel_display_list__(pixels)
        self.__frameStr__ = pixels

        threadScreenSize = int(self.screenResolution.x // self.threadCount)

        self.__running__ = True
        for threadNum in range(self.threadCount):
            start = Vector2(threadScreenSize * threadNum, 0)
            end = Vector2(threadScreenSize * (threadNum + 1), self.screenResolution.y)
            thread = threading.Thread(target=self.__displayThreadFunc__, args=(start, end))
            self.__frameThreads__.append(thread)
            thread.start()

        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        
        for t in self.__frameThreads__:
            if t.is_alive():
                t.join(timeout=0.01)
        self.__running__ = False

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

    @property
    def screenResolution(self) -> Vector2:
        """Get the resolution in pixels (width, height)"""
        size = shutil.get_terminal_size()
        # Each character row displays 2 pixel rows
        return Vector2(size.columns, size.lines * 2)

    def __get_pixel_display_list__(self, texture: Texture) -> List[List[Color]]:
        """Convert texture to displayable pixel list"""
        resolution = self.screenResolution
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
    
    def __show_pixels__(self, pixel_data):
        height = len(pixel_data)
        if height == 0:
            return
        width = len(pixel_data[0])

        frame_lines = []

        for y in range(0, height, 2):
            line_parts = []  # build line in a list instead of +=
            prev_colors = None

            for x in range(width):
                top_color = pixel_data[y][x]
                bottom_color = pixel_data[y + 1][x] if y + 1 < height else self.__bg__

                # Only append color codes if different from previous
                if prev_colors is None or prev_colors[0] != top_color:
                    line_parts.append(f"\033[38;2;{top_color.r};{top_color.g};{top_color.b}m")
                if prev_colors is None or prev_colors[1] != bottom_color:
                    line_parts.append(f"\033[48;2;{bottom_color.r};{bottom_color.g};{bottom_color.b}m")

                line_parts.append("\u2580")
                prev_colors = (top_color, bottom_color)

            line_parts.append("\033[0m")  # reset at end of line
            frame_lines.append("".join(line_parts))

        frame_str = "\n".join(frame_lines)

        if frame_str != self.__prevFrameStr__:
            sys.stdout.write("\033c"+frame_str)
            sys.stdout.flush()
            self.__prevFrameStr__ = frame_str