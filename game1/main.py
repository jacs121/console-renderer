import renderer
import math
import json
import copy
import keyboard
import os

def generate_light(object, roomSize, lightsList):
    # create an empty stamp
    lightPixels:list[list] = []
    
    # calc where the lightPixels list is stamped on the map
    lightRegionPos = (object["pos"][0]-object["radius"], object["pos"][1]-object["radius"])
    lightsList["offsets"].append(lightRegionPos)
    
    # expand the room size if needed (for adding the stamps later)
    if roomSize[0] < object["pos"][0]+object["radius"]+1:
        roomSize = (object["pos"][0]+object["radius"]+1, roomSize[1])
    if roomSize[1] < object["pos"][1]+object["radius"]+1:
        roomSize = (roomSize[0], object["pos"][1]+object["radius"]+1)
    visible_pixels, blocked_pixels = cast_light_rays(object["pos"], object["radius"], object.get("angleRange", 360), object.get("angle", 0))

    # create the lightPixels stamp
    for yi, y in enumerate(range(-object["radius"], object["radius"] + 1)):
        lightPixels.append([])
        for x in range(-object["radius"], object["radius"] + 1):
            distance = math.sqrt(x * x + y * y)
            if distance <= object["radius"] and (object["pos"][0]+x,object["pos"][1]+y) in visible_pixels:
                intensity = 1 - (distance / object["radius"])
                r = min(int(object["color"][0]), 255)
                g = min(int(object["color"][1]), 255)
                b = min(int(object["color"][2]), 255)
                lightPixels[yi].append([r, g, b, intensity])
            elif distance <= object["radius"] and (object["pos"][0]+x,object["pos"][1]+y) in blocked_pixels:
                intensity = 1 - (distance / object["radius"])
                r = min(int(object["color"][0]), 255)
                g = min(int(object["color"][1]), 255)
                b = min(int(object["color"][2]), 255)
                lightPixels[yi].append([r, g, b, intensity])
            else:
                # add a background color if no light can reach from current stamp
                lightPixels[yi].append([1, 1, 1, 0])
    lightsList["pixels"].append(lightPixels)
    return roomSize, lightsList, blocked_pixels

playerPos = (0,0)
walls = {"pixels":[], "offsets":[]}
lights = {"pixels": [], "offsets":[]}
lightBlocking = []
playerRot = 40
roomSize = (0,0)
visibleWalls = []
visibleWallsCanvas = [[]]

def get_outline(radius, angleRange, angle):
    outline_points = []
    for angle_deg in range(angleRange):
        angle_rad = math.radians(angle_deg+angle)
        x = int(round(radius * math.cos(angle_rad)))
        y = int(round(radius * math.sin(angle_rad)))
        outline_points.append((x, y))
    # Remove duplicates (some angles may map to same pixel)
    return outline_points

def cast_light_rays(light_pos, radius, angleRange, angle):
    visible_pixels = []
    blocked_pixels = []
    outline = get_outline(radius, angleRange, angle)

    for dx, dy in outline:
        target = (light_pos[0] + dx, light_pos[1] + dy)
        ray_pixels = bresenham_line(light_pos[0], light_pos[1], target[0], target[1])
        blockedIndex = -1
        for px, py in ray_pixels:
            if (px, py) in lightBlocking:
                blockedIndex = 2

            if blockedIndex > -1:
                if (px, py) in lightBlocking:
                    blocked_pixels.append((px, py))
                blockedIndex -= 1

            if blockedIndex == 0:
                break  # light blocked
            
            if blockedIndex == -1:
                visible_pixels.append((px, py))


    return visible_pixels, blocked_pixels

def bresenham_line(x0, y0, x1, y1):
    """
    Returns a list of (x, y) points from (x0, y0) to (x1, y1) using Bresenham's algorithm.
    """
    points = []

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)

    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1

    err = dx - dy

    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

    return points

def load_room(pos: tuple[int, int]):
    global walls, roomSize, lights, collisions, lightBlocking, playerPos, visibleWallsCanvas
    if not os.path.isfile(f"./rooms/{pos[0]}_{pos[1]}.json"):
        return
    room = json.load(open(f"./rooms/{pos[0]}_{pos[1]}.json"))
    walls = {"pixels":[], "offsets":[]}
    lights = {"pixels": [], "offsets":[]}
    collisions = []
    playerPos = room["init"]["playerPos"]
    roomSize = (0,0)
    for object in room["objects"]:
        if object["type"] == "wall":
            wallPixels:list[list] = []
            wallPos = (min(object["B"][0], object["A"][0]), min(object["B"][1], object["A"][1]))
            walls["offsets"].append(wallPos)
            if roomSize[0] < object["A"][0]+1:
                roomSize = (object["A"][0]+1, roomSize[1])
            if roomSize[1] < object["A"][1]+1:
                roomSize = (roomSize[0], object["A"][1]+1)

            if roomSize[0] < object["B"][0]+1:
                roomSize = (object["B"][0]+1, roomSize[1])
            if roomSize[1] < object["B"][1]+1:
                roomSize = (roomSize[0], object["B"][1]+1)

            for y in range(abs(object["B"][1] - object["A"][1]) + 1):
                wallPixels.append([])
                for x in range(abs(object["B"][0] - object["A"][0]) + 1):
                    if object["collision"]:
                        collisions.append((wallPos[0]+x, wallPos[1]+y))
                    if object["blockLight"]:
                        lightBlocking.append((wallPos[0]+x, wallPos[1]+y))
                    wallPixels[y].append(object["color"])
            walls["pixels"].append(wallPixels)
        elif object["type"] == "light":
            roomSize, lights = generate_light(object, roomSize, lights)
    visibleWallsCanvas = [[(1,1,1,0) for x in range(roomSize[0])] for y in range(roomSize[1])]

def onResize(size):
    return tick(size)

load_room((0,0))
def tick(size):
    global playerPos, playerRot, visibleWalls, visibleWallsCanvas

    player_angle_rad = math.radians(playerRot)
    if (keyboard.is_pressed("w") or keyboard.is_pressed("up")) and (playerPos[0]+round(math.cos(player_angle_rad)), playerPos[1]+round(math.sin(player_angle_rad))) not in collisions:
        playerPos = (playerPos[0]+round(math.cos(player_angle_rad)), playerPos[1]+round(math.sin(player_angle_rad)))
    elif (keyboard.is_pressed("s") or keyboard.is_pressed("down")) and (playerPos[0]-round(math.cos(player_angle_rad)), playerPos[1]-round(math.sin(player_angle_rad))) not in collisions:
        playerPos = (playerPos[0]-round(math.cos(player_angle_rad)), playerPos[1]-round(math.sin(player_angle_rad)))
    if keyboard.is_pressed("a") and (playerPos[0]-round(math.cos(player_angle_rad+math.radians(90))), playerPos[1]-round(math.sin(player_angle_rad+math.radians(90)))) not in collisions:
        playerPos = (playerPos[0]-round(math.cos(player_angle_rad+math.radians(90))), playerPos[1]-round(math.sin(player_angle_rad+math.radians(90))))
    elif keyboard.is_pressed("d") and (playerPos[0]+round(math.cos(player_angle_rad+math.radians(90))), playerPos[1]+round(math.sin(player_angle_rad+math.radians(90)))) not in collisions:
        playerPos = (playerPos[0]+round(math.cos(player_angle_rad+math.radians(90))), playerPos[1]+round(math.sin(player_angle_rad+math.radians(90))))
    playerRot += 10*(keyboard.is_pressed("right") - keyboard.is_pressed("left"))

    roomSizeTick, lightsTick, visiblePixels = generate_light({"type": "light","angleRange": 50,"angle": playerRot-25,"color": [255,255,210],"pos": playerPos,"radius": 13}, roomSize, copy.deepcopy(lights))
    newVisiblePixels = False
    for visiblePixel in visiblePixels:
        if visiblePixel not in visibleWalls:
            newVisiblePixels = True
            visibleWalls.append(visiblePixel)

    # canvas creation (last step)
    canvas = [[(1,1,1) for _ in range(roomSizeTick[0])] for _ in range(roomSizeTick[1])]

    for wall, offset in zip(walls["pixels"], walls["offsets"]):
        canvas = render.overlayOnCanvas(canvas, wall, offset)
    
    if newVisiblePixels:
        visibleWallsCanvas = [[(1,1,1, ((x, y) not in visibleWalls)-0.1) for x in range(roomSizeTick[0])] for y in range(roomSizeTick[1])]
    canvas = render.overlayOnCanvas(canvas, visibleWallsCanvas, (0, 0))

    for lightPixels, offset in zip(lightsTick["pixels"], lightsTick["offsets"]):
        canvas = render.overlayOnCanvas(canvas, lightPixels, offset)
    return canvas

render = renderer.ConsoleRenderer(tick, onResize, bg=(1,1,1))
render.run(60)
