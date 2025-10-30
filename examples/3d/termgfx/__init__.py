__version__ = "1.0.0"
__author__ = "Nitzan Soriano"

# Import main classes for easier access
from .vectors import Vector2
from .colors import Color, RGB_RED, RGB_GREEN, RGB_BLUE, RGB_WHITE, RGB_BLACK
from .textures import Image, Texture, REPEAT_MODE
from .renderer import ConsoleRenderer

# Define what gets imported with "from console_gfx import *"
__all__ = [
    'Vector2',
    'Color',
    'RGB_RED', 'RGB_GREEN', 'RGB_BLUE', 'RGB_WHITE', 'RGB_BLACK',
    'Image',
    'Texture',
    'REPEAT_MODE',
    'ConsoleRenderer'
]