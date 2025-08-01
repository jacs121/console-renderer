import shutil
import sys
import colorama
import time
import subprocess
import types
import ctypes

class ConsoleRenderer():
    def __init__(self, tick:types.FunctionType = None, sizeChange:types.FunctionType = None, bg: tuple[int, int, int] = (0,0,0), disableConsoleCursor: bool = True):
        colorama.init()
        self.__running__ = False

        self.onTick = tick
        self.onSizeChange = sizeChange
        self.__bg__ = bg
        self.__disable_console_cursor__ = disableConsoleCursor
        self.__prevFrame__ = [[]]

    def onTick(self, size: tuple[int, int]) -> list[list[tuple[int, int, int]]]:
        return [[]]

    def stop(self):
        self.__running__ = False
    
    def run(self, fps: int = 60):
        size = self.__get_console_size__()
        self.__running__ = True
        
        if self.__disable_console_cursor__:
            kernel32 = ctypes.windll.kernel32
            h_stdin = kernel32.GetStdHandle(-10)

            # Get current console mode
            mode = ctypes.c_uint32()
            kernel32.GetConsoleMode(h_stdin, ctypes.byref(mode))

            # Remove QUICK_EDIT_MODE (0x40)
            new_mode = mode.value & ~0x40
            kernel32.SetConsoleMode(h_stdin, new_mode)

        while self.__running__:
            _size = self.__get_console_size__()
            if size != _size:
                size = _size
                if self.onSizeChange:
                    out = self.onSizeChange((size[1], size[0]*2))
                    if out is not None:
                        self.__show_pixels__(self.__get_pixel_display_list__(out))
                        self.__prevFrame__ = out
            pixels = self.onTick((size[1], size[0]*2))
            if self.__prevFrame__ != pixels:
                self.__show_pixels__(self.__get_pixel_display_list__(pixels))
                self.__prevFrame__ = pixels
            time.sleep(1/fps)
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    def showFrame(self):
        size = self.__get_console_size__()
        pixels = self.onTick((size[1], size[0]*2))
        self.__show_pixels__(self.__get_pixel_display_list__(pixels))

    def overlayOnCanvas(self, canvas: list[list[tuple[int, int, int]]], layer: list[list[tuple[int, int, int]]], position: tuple[int, int]):
        for y in range(len(layer)):
            for x in range(len(layer[0])):
                if x < len(canvas[0]) and y < len(canvas):
                    alpha = layer[y][x][3] if len(layer[y][x]) == 4 else 1
                    alpha = min(max(alpha, 0), 1)
                    blend = lambda base, overlay, alpha: int(base*max(min(1-alpha, 1), 0) + overlay * max(min(alpha, 1), 0))
                    canvas[y+position[1]][x+position[0]] = (
                        blend(canvas[y+position[1]][x+position[0]][0], layer[y][x][0], alpha),
                        blend(canvas[y+position[1]][x+position[0]][1], layer[y][x][1], alpha),
                        blend(canvas[y+position[1]][x+position[0]][2], layer[y][x][2], alpha)
                    )
        return canvas

    def __pixel__(self, colorTop: tuple[tuple[int, int, int], tuple[int, int, int]] = (255, 255, 255), colorBottom: tuple[tuple[int, int, int], tuple[int, int, int]] = (0, 0, 0), pre = None):
        if pre == None:
            return "\x1b[48;2;{};{};{}m".format(*colorTop) + "\x1b[38;2;{};{};{}m".format(*colorBottom) + "\u2580"
        pix = ""

        if pre[0] != colorTop:
            pix += "\x1b[48;2;{};{};{}m".format(*colorTop)
        if pre[1] != colorBottom:
            pix += "\x1b[38;2;{};{};{}m".format(*colorBottom)
        return pix+"\u2580"

    def __clear__(self):
        if sys.platform not in ('win32', 'cygwin'):
            command = 'clear'
        else:
            command = 'cls'
        subprocess.call(command, shell=True)

    def __get_console_size__(self):
        size = shutil.get_terminal_size()
        return size.lines, size.columns

    def __get_pixel_display_list__(self, original: list[list[tuple[int, int, int]]]):
        console_height, console_width = self.__get_console_size__()

        # Each terminal row shows 2 pixels vertically, so actual vertical space = console_height * 2
        display_height = console_height * 2
        display_width = console_width

        original_height = len(original)
        original_width = len(original[0]) if original_height > 0 else 0

        # Create a blank pixel display
        pixelList = [[self.__bg__ for _ in range(display_width)] for _ in range(display_height)]

        # Calculate offsets to center the original image
        offset_y = max((display_height - original_height) // 2, 0)
        offset_x = max((display_width - original_width) // 2, 0)

        # Copy original pixel data into the center of the display
        for y in range(original_height):
            for x in range(original_width):
                if 0 <= y + offset_y < display_height and 0 <= x + offset_x < display_width:
                    pixelList[y + offset_y][x + offset_x] = (original[y][x][0], original[y][x][1], original[y][x][2])

        return pixelList

    def __show_pixels__(self, pixelData: list[list[tuple[tuple[int, int, int], tuple[int, int, int]]]]):
        self.__clear__()
        height = len(pixelData)
        width = len(pixelData[0]) if height > 0 else 0
        text = ""
        prev = None
        for y in range(0, height, 2):
            for x in range(width):
                bottom = pixelData[y][x]
                top = pixelData[y+1][x] if y+1 < height else self.__bg__
                text += self.__pixel__(top, bottom, prev)
                prev = (top, bottom)
            if x + 1 < width:
                text += "\n"
        sys.stdout.write(text+"\u001b[0m\033[?25l")
        sys.stdout.flush()