#!/usr/bin/env python3
"""
Basic demo showing how to use Term GFX
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from termgfx import ConsoleRenderer, Vector2, Image, Color, RGB_RED, RGB_GREEN, RGB_BLUE

def basic_tick(resolution: Vector2):
    # Create a simple pattern
    img = Image(resolution, Color("RGB", [50, 50, 100]))
    
    # Draw a red square
    for y in range(10):
        for x in range(10):
            img.set_pixel(Vector2(x + 5, y + 5), RGB_RED)
    
    # Draw a green line
    for i in range(min(20, resolution.x)):
        img.set_pixel(Vector2(i + 10, 20), RGB_GREEN)
    
    return img

if __name__ == "__main__":
    renderer = ConsoleRenderer(tick=basic_tick)
    try:
        renderer.run(fps=10)
    except KeyboardInterrupt:
        renderer.stop()
        print("\nDemo stopped.")