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

    def __init__(self, mode: _ColorMode, val: list[_Number]):
        self.mode = mode.upper()  # type: ignore
        if self.mode == "RGB":
            if len(val) != 3:
                raise ValueError("RGB mode requires 3 values")
            self.r: _Number = val[0]
            self.g: _Number = val[1]
            self.b: _Number = val[2]
            self.rg = self.r, self.g
            self.gb = self.g, self.b
            self.rb = self.b, self.r
            self.rgb = val
            self.r, self.g, self.b = val
        elif self.mode == "RGBA":
            if len(val) != 4:
                raise ValueError("RGBA mode requires 4 values")
            self.r: _Number = val[0]
            self.g: _Number = val[1]
            self.b: _Number = val[2]
            self.a: _Number = val[3]
            self.rg = self.r, self.g
            self.gb = self.g, self.b
            self.br = self.b, self.r
            self.rga = self.r, self.g, self.a
            self.gba = self.g, self.b, self.a
            self.bra = self.b, self.r, self.a
            self.rgb = self.r, self.g, self.b
            self.rgba = self.r, self.g, self.b, self.a
        elif self.mode == "HSV":
            if len(val) != 3:
                raise ValueError("HSV mode requires 3 values")
            self.h: _Number = val[0]
            self.s: _Number = val[1]
            self.v: _Number = val[2]
            self.hs: _Number = val[0], val[1]
            self.sv: _Number = val[1], val[2]
            self.vh: _Number = val[2], val[0]
        elif self.mode == "GRAY":
            if len(val) != 1:
                raise ValueError("GRAY mode requires 1 value")
            self.gray: _Number
            self.gray = val[0]
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
        if type(data) == Color:
            self.__size__ = Vector2d(1,1)
            if self.__repeat_mode__ == None:
                self.__repeat_mode__ = REPEAT_MODE.INFINITE
            self.__met__ = [[data]]
        elif type(data) == Image:
            if self.__repeat_mode__ == None:
                self.__repeat_mode__ = REPEAT_MODE.DISABLE
            self.__met__ = data.dataArray
        else:
            raise TypeError("data type can only be Color or Image")
        if self.__repeat_mode__ == REPEAT_MODE.FINITE:
            if repeatMode not in ["INFINITE", "FINITE", "DISABLE"]:
                raise ValueError("second argument expected to be REPEAT_MODE")
        self.__repeat_vector__ = Vector2d(1, 1)

    def __getitem__(self, value: Vector2d): # self[Vector2d(x, y)]
        maximum = Vector2d(len(max(self.__met__, key=len)), len(self.__met__))
        if self.__repeat_mode__ == REPEAT_MODE.FINITE:
            maximum = self.__size__*self.__repeat_vector__
            if maximum.x >= abs(value.x) or maximum.y >= abs(value.y):
                raise IndexError(f"{value} is outside of the maximum texture size ({maximum})")
            # make a copy of __met__ repeated until it matches size
            x = value.x % maximum.x
            y = value.y % maximum.y

        elif self.__repeat_mode__ == REPEAT_MODE.DISABLE:
            maximum = self.__size__
            if maximum.x >= abs(value.x) or maximum.y >= abs(value.y):
                raise IndexError(f"{value} is outside of the maximum texture size ({maximum})")
            # make a copy of __met__ repeated until it matches size
            x = value.x
            y = value.y
        else:
            x = value.x % maximum.x
            y = value.y % maximum.y
        return self.__met__[y][x]