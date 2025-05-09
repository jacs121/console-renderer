from typing import Literal, Union, Optional
from vectors import Vector2d
from enum import Enum

_ColorMode = Literal["RGB", "RGBA", "HSV", "GRAY"]
_Number = Union[int, float]


class REPEAT_MODE(str, Enum):
    INFINITE = "INFINITE"
    FINITE = "FINITE"
    DISABLE = "DISABLE"

class Color:
    mode: _ColorMode

    def __init__(self, mode: _ColorMode, *args: _Number):
        self.mode = mode.upper()  # type: ignore
        if self.mode == "RGB":
            if len(args) != 3:
                raise ValueError("RGB mode requires 3 values")
            self.r: _Number
            self.g: _Number
            self.b: _Number
            self.rg = self.r, self.g
            self.gb = self.g, self.b
            self.rb = self.b, self.r
            self.rgb = args
            self.r, self.g, self.b = args
        elif self.mode == "RGBA":
            if len(args) != 4:
                raise ValueError("RGBA mode requires 4 values")
            self.r: _Number
            self.g: _Number
            self.b: _Number
            self.a: _Number
            self.rg = self.r, self.g
            self.gb = self.g, self.b
            self.br = self.b, self.r
            self.rga = self.r, self.g, self.a
            self.gba = self.g, self.b, self.a
            self.bra = self.b, self.r, self.a
            self.rgb = self.r, self.g, self.b
            self.rgba = self.r, self.g, self.b, self.a
            self.r, self.g, self.b, self.a = args
        elif self.mode == "HSV":
            if len(args) != 3:
                raise ValueError("HSV mode requires 3 values")
            self.h: _Number
            self.s: _Number
            self.v: _Number
            self.hs: _Number
            self.sv: _Number
            self.vh: _Number
            self.h, self.s, self.v = args
        elif self.mode == "GRAY":
            if len(args) != 1:
                raise ValueError("GRAY mode requires 1 value")
            self.gray: _Number
            self.gray = args[0]
        else:
            raise ValueError(f"Unsupported mode: {mode}")

    def __repr__(self) -> str:
        if self.mode == "RGB":
            return f"Color(RGB: {self.r}, {self.g}, {self.b})"
        elif self.mode == "RGBA":
            return f"Color(RGBA: {self.r}, {self.g}, {self.b}, {self.a})"
        elif self.mode == "HSV":
            return f"Color(HSV: {self.h}, {self.s}, {self.v})"
        elif self.mode == "GRAY":
            return f"Color(GRAY: {self.gray})"
        return "Color(Invalid)"

class Image():
    pass

class Texture():
    def __init__(self, data: Color | Image, repeatMode: Optional[REPEAT_MODE] = None):
        self.__repeat_mode__ = repeatMode
        if data == Color:
            self.__size__ = Vector2d(1,1)
            if self.__repeat_mode__ == None:
                self.__repeat_mode__ = REPEAT_MODE.INFINITE
            self.met = [[data]]
        elif data == Image:
            if self.__repeat_mode__ == None:
                self.__repeat_mode__ = REPEAT_MODE.DISABLE
            self.met = data.dataArray
        else:
            raise TypeError("data type can only be Color or Image")
        if self.__repeat_mode__ == REPEAT_MODE.FINITE:
            if repeatMode not in ["INFINITE", "FINITE", "DISABLE"]:
                raise ValueError("second argument expected to be REPEAT_MODE")
        self.__repeat_vector__ = Vector2d(1, 1)

    def __ror__(self, value: Vector2d): # self[Vector2d(x, y)]
        maximum = Vector2d(len(max(self.met, key=len)), len(self.met))
        if self.__repeat_mode__ == REPEAT_MODE.FINITE:
            maximum = self.__size__*self.__repeat_vector__
            if maximum.x >= abs(value.x) or maximum.y >= abs(value.y):
                raise IndexError(f"{value} is outside of the maximum texture size ({maximum})")
            # make a copy of met repeated until it matches size
            x = value.x % maximum.x
            y = value.y % maximum.y

        elif self.__repeat_mode__ == REPEAT_MODE.DISABLE:
            maximum = self.__size__
            if maximum.x >= abs(value.x) or maximum.y >= abs(value.y):
                raise IndexError(f"{value} is outside of the maximum texture size ({maximum})")
            # make a copy of met repeated until it matches size
            x = value.x
            y = value.y
        else:
            x = value.x % maximum.x
            y = value.y % maximum.y
        return self.met[y][x]