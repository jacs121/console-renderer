from termgfx import colors
from termgfx import renderer
from termgfx import vectors
from termgfx import textures

def tick(resolution: vectors.Vector2) -> textures.Texture:
    img = textures.Image(resolution // 10, colors.RGB_BLUE)
    img.set_pixel(resolution // 20, colors.RGB_YELLOW)
    return textures.Texture(img, textures.REPEAT_MODE.INFINITE)

render = renderer.ConsoleRenderer(tick)
render.run(fps=30)