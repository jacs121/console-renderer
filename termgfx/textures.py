from typing import Optional, List
from .vectors import *
from .colors import *
from enum import Enum

class REPEAT_MODE(str, Enum):
    INFINITE = "INFINITE"
    FINITE = "FINITE"
    DISABLE = "DISABLE"

class Image:
    def __init__(self, size: Vector2, initial_color: Optional[Color] = None):
        self.width = int(size.x)
        self.height = int(size.y)
        if initial_color is None:
            initial_color = Color("RGB", [0, 0, 0])
        
        # Create a 2D list of Color objects
        self.dataArray: List[List[Color]] = [
            [Color(initial_color.mode, list(initial_color)) for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def set_pixel(self, position: Vector2, color: Color):
        x, y = int(position.x), int(position.y)
        if 0 <= x < self.width and 0 <= y < self.height:
            self.dataArray[y][x] = color

    def get_pixel(self, position: Vector2) -> Color:
        x, y = int(position.x), int(position.y)
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.dataArray[y][x]
        return Color("RGB", [0, 0, 0])

    def fill(self, color: Color):
        for y in range(self.height):
            for x in range(self.width):
                self.dataArray[y][x] = Color(color.mode, list(color))

    def __getitem__(self, index: Vector2) -> List[Color]:
        return self.dataArray[index.x][index.y]

    def __len__(self) -> int:
        return self.height

    @classmethod
    def from_list(cls, data: List[List[Color]]):
        if not data or not data[0]:
            raise ValueError("Image data cannot be empty")
        
        height = len(data)
        width = len(data[0])
        
        image = cls(Vector2(width, height))
        image.dataArray = data
        return image


class Texture:
    def __init__(self, data: Color | Image, repeatMode: Optional[REPEAT_MODE] = None):
        self.__repeat_mode__ = repeatMode
        
        if isinstance(data, Color):
            self.__size__ = Vector2(1, 1)
            if self.__repeat_mode__ is None:
                self.__repeat_mode__ = REPEAT_MODE.INFINITE
            self.__met__ = [[data]]
        elif isinstance(data, Image):
            self.__size__ = Vector2(data.width, data.height)
            if self.__repeat_mode__ is None:
                self.__repeat_mode__ = REPEAT_MODE.DISABLE
            self.__met__ = data.dataArray
        else:
            raise TypeError("data type can only be Color or Image")
            
        self.__repeat_vector__ = Vector2(1, 1)

    def __getitem__(self, value: Vector2) -> Color:
        width = len(self.__met__[0]) if self.__met__ else 0
        height = len(self.__met__) if self.__met__ else 0
        
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
            
        return self.__met__[y][x]

    @property
    def size(self) -> Vector2:
        return self.__size__

    @property
    def repeat_mode(self) -> REPEAT_MODE:
        return self.__repeat_mode__