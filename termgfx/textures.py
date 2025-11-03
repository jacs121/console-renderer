from typing import Optional, List
from .vectors import *
from .colors import *
from enum import Enum
import numpy as np
from PIL import Image as pillowImage

class SliceError(Exception): pass

class REPEAT_MODE(str, Enum):
    INFINITE = "INFINITE"
    FINITE = "FINITE"
    DISABLE = "DISABLE"

class Image:
    def __init__(self, size: Vector2, initial_color: Optional[Color] = None):
        self.__width__ = int(size.x)
        self.__height__ = int(size.y)
        if initial_color is None:
            initial_color = Color("RGB", [0, 0, 0])
        # NumPy array for RGB
        self.__dataArray__ = np.full((self.__height__, self.__width__, 3),
                                 [initial_color.r, initial_color.g, initial_color.b],
                                 dtype=np.uint8)

    def set_pixel(self, position: Vector2, color: Color):
        x, y = int(position.x), int(position.y)
        if 0 <= x < self.__width__ and 0 <= y < self.__height__:
            self.__dataArray__[y, x] = [color.r, color.g, color.b]

    def get_pixel(self, position: Vector2) -> Color:
        x, y = int(position.x), int(position.y)
        if 0 <= x < self.__width__ and 0 <= y < self.__height__:
            rgb = self.__dataArray__[y, x]
            return Color("RGB", [int(rgb[0]), int(rgb[1]), int(rgb[2])])
        return Color("RGB", [0, 0, 0])

    def fill(self, color: Color):
        self.__dataArray__[:, :] = [color.r, color.g, color.b]

    def __getitem__(self, index: Vector2 | slice):
        # Ensure we return a Color object for compatibility
        if isinstance(index, Vector2):
            x, y = int(index.x), int(index.y)
            if 0 <= x < self.__width__ and 0 <= y < self.__height__:
                rgb = self.__dataArray__[y, x]
                return Color("RGB", [int(rgb[0]), int(rgb[1]), int(rgb[2])])
            return Color("RGB", [0, 0, 0])
        elif isinstance(index, slice) and not index.step:
            x1, y1 = int(index.start.x), int(index.start.y)
            x2, y2 = int(index.stop.x), int(index.stop.y)
            newData = Image(Vector2(self.__width__, self.__height__), RGB_BLACK)
            for x in range(x1, x2):
                for y in range(y1, y2):
                    if 0 <= x < self.__width__ and 0 <= y < self.__height__:
                        rgb = self.__dataArray__[y, x]
                        newData.set_pixel(Vector2(x, y), rgb)
            return newData
        elif isinstance(index, slice) and index.step:
            raise SliceError("step size is not recognized as a slice value")

    @classmethod
    def from_list(cls, data: List[List[Color]]):
        if not data or not data[0]:
            raise ValueError("Image data cannot be empty")
        height = len(data)
        width = len(data[0])
        image = cls(Vector2(width, height))
        for y in range(height):
            for x in range(width):
                c = data[y][x]
                image.set_pixel(Vector2(y, x), Color("RGB", [c.r, c.g, c.b]))
        return image
    
    @classmethod
    def from_pillow(cls, img: pillowImage.Image):
        ImageData = cls(Vector2(img.size[0], img.size[1]), RGB_BLACK)
        for x in range(img.size[0]):
            for y in range(img.size[1]):
                color = None
                if img.mode == "L":
                    color = Color("GRAY", list(img.getpixel(x, y)))
                elif img.mode == "RGB":
                    color = Color("RGB", list(img.getpixel(x, y)))
                elif img.mode == "RGBA":
                    color = Color("RGBA", list(img.getpixel(x, y)))
                elif img.mode == "HSV":
                    color = Color("HSV", list(img.getpixel(x, y)))
                if not color:
                    raise ColorModeError(f"Unsupported mode: {img.mode}")
                ImageData.set_pixel(Vector2(x, y), color)
        return ImageData
    
    @property
    def size(self):
        return Vector2(self.__width__, self.__height__)

    @property
    def dataArray(self):
        return self.__dataArray__

class Texture:
    def __init__(self, data: Color | Image, repeatMode: Optional[REPEAT_MODE] = None):
        self.__repeat_mode__ = repeatMode
        
        if isinstance(data, Color):
            self.__size__ = Vector2(1, 1)
            if self.__repeat_mode__ is None:
                self.__repeat_mode__ = REPEAT_MODE.INFINITE
            self.__met__ = np.full((1, 1, 3), [data.r, data.g, data.b], dtype=np.uint8)
        elif isinstance(data, Image):
            self.__size__ = data.size
            if self.__repeat_mode__ is None:
                self.__repeat_mode__ = REPEAT_MODE.DISABLE
            self.__met__ = data.dataArray
        else:
            raise TypeError("data type can only be Color or Image")
            
        self.__repeat_vector__ = Vector2(1, 1)

    def __getitem__(self, value: Vector2) -> Color:
        height, width = self.__met__.shape[:2]
        
        if width == 0 or height == 0:
            raise IndexError("Texture has no data")
        
        if self.__repeat_mode__ == REPEAT_MODE.FINITE:
            max_x = int(self.__size__.x * self.__repeat_vector__.x)
            max_y = int(self.__size__.y * self.__repeat_vector__.y)
            
            if value.x < 0 or value.x >= max_x or value.y < 0 or value.y >= max_y:
                raise IndexError(f"{value} is outside of texture bounds")
                
            x = int(value.x) % width
            y = int(value.y) % height

        elif self.__repeat_mode__ == REPEAT_MODE.DISABLE:
            if value.x < 0 or value.x >= width or value.y < 0 or value.y >= height:
                raise IndexError(f"{value} is outside of texture bounds")
            x = int(value.x)
            y = int(value.y)
        else:  # INFINITE mode
            x = int(value.x) % width
            y = int(value.y) % height

        r, g, b = self.__met__[y, x]
        return Color("RGB", [int(r), int(g), int(b)])

    def __setitem__(self, value: Vector2, color: Color):
        height, width = self.__met__.shape[:2]
        
        if width == 0 or height == 0:
            raise IndexError("Texture has no data")
        
        if self.__repeat_mode__ == REPEAT_MODE.FINITE:
            max_x = int(self.__size__.x * self.__repeat_vector__.x)
            max_y = int(self.__size__.y * self.__repeat_vector__.y)
            
            if value.x < 0 or value.x >= max_x or value.y < 0 or value.y >= max_y:
                raise IndexError(f"{value} is outside of texture bounds")
                
            x = int(value.x) % width
            y = int(value.y) % height

        elif self.__repeat_mode__ == REPEAT_MODE.DISABLE:
            if value.x < 0 or value.x >= width or value.y < 0 or value.y >= height:
                raise IndexError(f"{value} is outside of texture bounds")
            x = int(value.x)
            y = int(value.y)
        else:  # INFINITE mode
            x = int(value.x) % width
            y = int(value.y) % height

        self.__met__[y, x] = [color.r, color.g, color.b]

    @property
    def size(self) -> Vector2:
        return self.__size__

    @property
    def repeat_mode(self) -> REPEAT_MODE:
        return self.__repeat_mode__