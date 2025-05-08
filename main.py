from renderer import ConsoleRenderer
import random

x = 0
y = 0
xm = 1
ym = 1

color = (random.randint(20, 255), random.randint(20, 255), random.randint(20, 255))
maxShadow = 100
shadows = [None]*maxShadow

def changedSize(size):
    global shadows, x, y

    x = min(size[0], x)
    y = min(size[1], y)
    for shadowIndex in range(len(shadows)):
        if shadows[shadowIndex] != None:
            shadows[shadowIndex] = (min(shadows[shadowIndex][0], size[0]), min(shadows[shadowIndex][1], size[1]), shadows[shadowIndex][2])

def tick(size):
    global color, x, y, xm ,ym, maxShadow, shadows

    screen = [[(0,0,0) for _ in range(size[0]+1)] for _ in range(size[1]*2+1)]
    screen[y][x] = color
    screen[y][x+1] = color
    screen[y][x+2] = color
    screen[y+1][x] = color
    screen[y+1][x+1] = color
    screen[y+1][x+2] = color
    screen[y+2][x] = color
    screen[y+2][x+1] = color
    screen[y+2][x+2] = color

    if len(shadows)-1 >= maxShadow:
        shadows = shadows[1:]
    shadows.append((x, y, color))
    
    for shadowIndex in range(len(shadows)):
        shadow = shadows[shadowIndex]
        if shadow == None:
            continue

        shadowIndex = maxShadow - shadowIndex
        shadowIndex += 1

        screen[shadow[1]][shadow[0]] = (
            shadow[2][0] - shadowIndex*(shadow[2][0]//(maxShadow)),
            shadow[2][1] - shadowIndex*(shadow[2][1]//(maxShadow)),
            shadow[2][2] - shadowIndex*(shadow[2][2]//(maxShadow))
        )
        screen[shadow[1]][shadow[0]+1] = (
            shadow[2][0] - shadowIndex*(shadow[2][0]//(maxShadow)),
            shadow[2][1] - shadowIndex*(shadow[2][1]//(maxShadow)),
            shadow[2][2] - shadowIndex*(shadow[2][2]//(maxShadow))
        )
        screen[shadow[1]][shadow[0]+2] = (
            shadow[2][0] - shadowIndex*(shadow[2][0]//(maxShadow)),
            shadow[2][1] - shadowIndex*(shadow[2][1]//(maxShadow)),
            shadow[2][2] - shadowIndex*(shadow[2][2]//(maxShadow))
        )
        
        screen[shadow[1]+1][shadow[0]] = (
            shadow[2][0] - shadowIndex*(shadow[2][0]//(maxShadow)),
            shadow[2][1] - shadowIndex*(shadow[2][1]//(maxShadow)),
            shadow[2][2] - shadowIndex*(shadow[2][2]//(maxShadow))
        )
        screen[shadow[1]+1][shadow[0]+1] = (
            shadow[2][0] - shadowIndex*(shadow[2][0]//(maxShadow)),
            shadow[2][1] - shadowIndex*(shadow[2][1]//(maxShadow)),
            shadow[2][2] - shadowIndex*(shadow[2][2]//(maxShadow))
        )
        screen[shadow[1]+1][shadow[0]+2] = (
            shadow[2][0] - shadowIndex*(shadow[2][0]//(maxShadow)),
            shadow[2][1] - shadowIndex*(shadow[2][1]//(maxShadow)),
            shadow[2][2] - shadowIndex*(shadow[2][2]//(maxShadow))
        )
        
        screen[shadow[1]+2][shadow[0]] = (
            shadow[2][0] - shadowIndex*(shadow[2][0]//(maxShadow)),
            shadow[2][1] - shadowIndex*(shadow[2][1]//(maxShadow)),
            shadow[2][2] - shadowIndex*(shadow[2][2]//(maxShadow))
        )
        screen[shadow[1]+2][shadow[0]+1] = (
            shadow[2][0] - shadowIndex*(shadow[2][0]//(maxShadow)),
            shadow[2][1] - shadowIndex*(shadow[2][1]//(maxShadow)),
            shadow[2][2] - shadowIndex*(shadow[2][2]//(maxShadow))
        )
        screen[shadow[1]+2][shadow[0]+2] = (
            shadow[2][0] - shadowIndex*(shadow[2][0]//(maxShadow)),
            shadow[2][1] - shadowIndex*(shadow[2][1]//(maxShadow)),
            shadow[2][2] - shadowIndex*(shadow[2][2]//(maxShadow))
        )

    y += ym
    x += xm

    if x >= size[0]-3:
        xm *= -1
        x = size[0]-3
    elif x <= 0:
        xm *= -1
        x = 0
    
    if y >= size[1]*2-3:
        ym *= -1
        y = size[1]*2-3
    elif y <= 0:
        ym *= -1
        y = 0

    if (x >= size[0]-3)+(y >= size[1]*2-3)+(x <= 0)+(y <= 0) > 1:
        color = (random.randint(20, 255), random.randint(20, 255), random.randint(20, 255))
    return screen

renderer = ConsoleRenderer(tick, changedSize)
renderer.run(60)
