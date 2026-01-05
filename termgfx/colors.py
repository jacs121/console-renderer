from typing import Literal, Union

class ColorModeError(Exception): pass

_Number = Union[int, float]
_ColorMode = Literal["RGB", "RGBA", "HSV", "GRAY"]
class Color:
    def __init__(self, mode: _ColorMode, val: list[_Number]):
        self.__mode__ = mode.upper()
        self._components = []
        
        if self.__mode__ == "RGB":
            if len(val) != 3:
                raise ValueError("RGB mode requires 3 values")
            self._components = [int(val[0]), int(val[1]), int(val[2]), 1]
            self._r, self._g, self._b, self._a = self._components

        elif self.__mode__ == "RGBA":
            if len(val) != 4:
                raise ValueError("RGBA mode requires 4 values")
            self._components = [int(val[0]), int(val[1]), int(val[2]), int(val[3])]
            self._r, self._g, self._b, self._a = self._components

        elif self.__mode__ == "HSV":
            if len(val) != 3:
                raise ValueError("HSV mode requires 3 values")
            
            # Convert HSV to RGB for rendering
            self.__convert_hsv_to_rgb__(val[0], val[1], val[2])

        elif self.__mode__ == "GRAY":
            if len(val) != 1:
                raise ValueError("GRAY mode requires 1 value")
            gray = int(val[0])
            self._components = [gray, gray, gray, 1]
            self._r, self._g, self._b, self._a = self._components
            self.__mode__ = "RGB"  # Treat as RGB for rendering

        else:
            raise ColorModeError(f"Unsupported mode: {mode}")

    def __convert_hsv_to_rgb__(self, h, s, v):
        """Convert HSV to RGB for rendering"""
        h, s, v = h, s / 100.0, v / 100.0
        
        if s == 0:
            r = g = b = int(v * 255)
        else:
            h = h / 60.0
            i = int(h)
            f = h - i
            p = v * (1 - s)
            q = v * (1 - s * f)
            t = v * (1 - s * (1 - f))
            
            if i == 0:
                r, g, b = v, t, p
            elif i == 1:
                r, g, b = q, v, p
            elif i == 2:
                r, g, b = p, v, t
            elif i == 3:
                r, g, b = p, q, v
            elif i == 4:
                r, g, b = t, p, v
            else:
                r, g, b = v, p, q
                
            r, g, b = int(r * 255), int(g * 255), int(b * 255)
        
        self._components = [r, g, b, 1]
        self._r, self._g, self._b, self._a = self._components
        self.__mode__ = "RGB"

    def __iter__(self):
        return iter(self._components)

    def __getitem__(self, index: int):
        return self._components[index]

    def __len__(self):
        return len(self._components)

    def __eq__(self, other):
        if not isinstance(other, Color):
            return False
        return self._components == other._components

    def __repr__(self) -> str:
        return f"Color({self.__mode__}: {self._components})"
    
    @property
    def HSV(self) -> tuple[_Number, _Number, _Number]:
        r, g, b, a = self._components
        r /= 255
        g /= 255
        b /= 255
        
        Cmax = max(r, g, b)
        Cmin = min(r, g, b)
        Delta = Cmax - Cmin
        
        V = Cmax
        if Cmax == 0:
            S = 0
        else:
            S = Delta / Cmax
        if Delta == 0:
            H = 0
        elif Cmax == r:
            H = 60 * (((g - b) / Delta) % 6)
        elif Cmax == g:
            H = 60 * (((b - r) / Delta) + 2)
        else:
            H = 60 * (((r - g) / Delta) + 4)
        
        return (H, S, V)
    
    @property
    def R(self):
        return self._r
    
    @property
    def G(self):
        return self._g
    
    @property
    def B(self):
        return self._b
    
    @property
    def alpha(self):
        return self._a

RGB_RED = Color("RGB", [255, 0, 0])
RGB_GREEN = Color("RGB", [0, 255, 0])
RGB_BLUE = Color("RGB", [0, 0, 255])
RGB_LIGHTBLUE = Color("RGB", [0, 255, 255])
RGB_PURPLE = Color("RGB", [255, 0, 255])
RGB_YELLOW = Color("RGB", [255, 255, 0])
RGB_WHITE = Color("RGB", [255, 255, 255])
RGB_BLACK = Color("RGB", [0, 0, 0])
RGB_GRAY = Color("RGB", [255//2, 255//2, 255//2])
RGB_DARKBLUE = Color("RGB", [0, 0, 255//2])
RGB_DARKRED = Color("RGB", [255//2, 0, 0])
RGB_DARKGREEN = Color("RGB", [0, 255//2, 0])
RGB_DARKPURPLE = Color("RGB", [255//2, 0, 255//2])

RGBA_RED = Color("RGBA", [255, 0, 0, 1.0])
RGBA_GREEN = Color("RGBA", [0, 255, 0, 1.0])
RGBA_BLUE = Color("RGBA", [0, 0, 255, 1.0])
RGBA_PURPLE = Color("RGBA", [255, 0, 255, 1.0])
RGBA_LIGHTBLUE = Color("RGBA", [0, 255, 255, 1.0])
RGBA_YELLOW = Color("RGBA", [255, 255, 0, 1.0])
RGBA_WHITE = Color("RGBA", [255, 255, 255, 1.0])
RGBA_BLACK = Color("RGBA", [0, 0, 0, 1.0])
RGBA_DARKBLUE = Color("RGBA", [0, 0, 255//2, 1.0])
RGBA_DARKRED = Color("RGBA", [255//2, 0, 0, 1.0])
RGBA_DARKGREEN = Color("RGBA", [0, 255//2, 0, 1.0])
RGBA_DARKPURPLE = Color("RGBA", [255//2, 0, 255//2, 1.0])