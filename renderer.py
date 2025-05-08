import shutil
import sys
import colorama
import time
import subprocess
import types

class ConsoleRenderer():
    def __init__(self, tick:types.FunctionType = None, sizeChange:types.FunctionType = None):
        colorama.init()
        self.running = False

        self.onTick = tick
        self.onSizeChange = sizeChange

    def onTick(self, size: tuple[int, int]):
        return [[]]

    def stop(self):
        self.running = False
    
    def run(self, fps: int = 60):
        size = self.__get_console_size__()
        self.running = True

        while self.running:
            _size = self.__get_console_size__()
            if size != _size:
                size = _size
                self.onSizeChange((size[1], size[0]))
            pixels = self.onTick((size[1], size[0]))
            self.__show_pixels__(self.__get_pixel_display_list__(pixels))
            time.sleep(1/fps)

    def onSizeChange(self, size: tuple[int, int]):
        pass

    def addLayer(self, layer1: list[list[tuple[int, int, int]]], layer2: list[list[tuple[int, int, int]]], position1: tuple[int, int], position2: tuple[int, int]):
        layer: list[list[tuple[int, int, int]]] = []
        console_height, console_width = self.__get_console_size__()
        for y in range(console_height*2):
            layer.append([])
            for x in range(len(console_width)):
                if position2[0] > x and len(layer2[y])+position2[0] < x and position2[1] > y and len(layer2)+position2[1] < y:
                    layer[y].append(layer2[y][x])
                elif position1[0] > x and len(layer1[y])+position1[0] < x and position1[1] > y and len(layer1)+position1[1] < y:
                    layer[y].append(layer1[y][x])
                else:
                    layer[y].append((0,0,0))
        return layer

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

        # Create a blank screen buffer
        pixelList = [[(0, 0, 0) for _ in range(display_width)] for _ in range(display_height)]

        # Calculate offsets to center the original image
        offset_y = max((display_height - original_height) // 2, 0)
        offset_x = max((display_width - original_width) // 2, 0)

        # Copy original pixel data into the center of the display buffer
        for y in range(original_height):
            for x in range(original_width):
                if 0 <= y + offset_y < display_height and 0 <= x + offset_x < display_width:
                    pixelList[y + offset_y][x + offset_x] = original[y][x]

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
                top = pixelData[y+1][x] if y+1 < height else (0, 0, 0)
                text += self.__pixel__(top, bottom, prev)
                prev = (top, bottom)
            if x + 1 < width:
                text += "\n"
        sys.stdout.write(text)
        sys.stdout.flush()


"""

###
###
###


"""