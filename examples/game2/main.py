import random
import noise
import keyboard
from termgfx import ConsoleRenderer # custom console rendering API
import os
import time
import zlib
import pickle
import lmdb

# parameters
scale = 200.0
octaves = 5
persistence = 0.5
lacunarity = 2.0
seed = 0 # debug seed
seed = int(random.random()*1000)

# Biome thresholds (0..1)
water_level = 0.4
sand_level = 0.45
grass_level = 0.7
rock_level = 0.85
snow_level = 0.93

# biome collision index
CI_WATER = 0
CI_SAND = 1
CI_GRASS = 2
CI_ROCK = 3
CI_SNOW = 4
CI_SNOW_TOP = 5

# generated chunks info
DB_PATH = "world_cache"
env = None
collisionIndexCache = {}
terrain_cache = {}

# player info
current_position = [0, 0]  # Use list for mutable updates
player_position = [0, 0]  # Player's position within the world
chunk_size = (80, 40)  # Size of each cached chunk
move_speed = 1

# inventory settings
INVENTORY_SIZE = 9
inventory = [None] * INVENTORY_SIZE  # Each slot can hold an item (represented by a color)
selected_slot = 0  # Currently selected inventory slot
inventory_height = 4

# keyboard info
keybinds = {
    "saveFile": "f5",
    "reloadSaveFile": "f9",
    "walkForward": "w",
    "walkBackward": "s",
    "walkLeft": "a",
    "walkRight": "d",
    "increaseInventoryIndex": "right",
    "decreaseInventoryIndex": "left",
    "collectResource": "space",
}

pressedKeys = []

def collect_resources(player_ci):
    """Collect resources based on the terrain the player is standing on"""
    global inventory
    
    # Define what resources can be collected from each terrain type
    resource_map = {
        CI_GRASS: (50, 200, 50),  # Green (plant fiber)
        CI_ROCK: (150, 150, 150),  # Gray (stone)
        CI_SAND: (210, 180, 140),  # Tan (sand)
        CI_WATER: (100, 150, 255),  # Light blue (water)
        CI_SNOW: (220, 220, 255),   # Light blue-white (snow)
        CI_SNOW_TOP: (255, 255, 255)  # White (ice)
    }
    
    # Get the resource for the current terrain
    resource = resource_map.get(player_ci)
    
    if resource:
        # Try to add to existing stack
        for i, item in enumerate(inventory):
            if item and item[0] == resource:
                # Item already exists in inventory, increase count
                inventory[i] = (resource, item[1] + 1)
                return
        
        # Find an empty slot
        if inventory[selected_slot] is None:
            inventory[selected_slot] = (resource, 1)
        for i in range(INVENTORY_SIZE):
            if inventory[i] is None:
                inventory[i] = (resource, 1)  # (color, count)
                return

def showInventory(pixels, size):
    # Draw inventory at the bottom of the screen
    if size[1] > INVENTORY_SIZE*2:  # Ensure we have enough space
        
        # Draw inventory background
        for y in range(size[1] - inventory_height, size[1]):
            for x in range(size[0]):
                if y < len(pixels) and x < len(pixels[y]):
                    pixels[y][x] = (40, 40, 40)  # Dark gray background
        
        # Calculate inventory slot width
        slot_width = size[0] // INVENTORY_SIZE
        
        # Draw inventory slots
        for i in range(INVENTORY_SIZE):
            slot_start = i * slot_width
            slot_end = (i + 1) * slot_width
            
            # Draw slot border
            for y in range(size[1] - inventory_height, size[1]):
                if slot_start < len(pixels[y]):
                    pixels[y][slot_start] = (100, 100, 100)  # Slot border
                if slot_end - 1 < len(pixels[y]):
                    pixels[y][slot_end - 1] = (100, 100, 100)  # Slot border
            
            # Highlight selected slot
            if i == selected_slot:
                for x in range(slot_start + 1, slot_end - 1):
                    for y in range(size[1] - inventory_height, size[1]):
                        if y < len(pixels) and x < len(pixels[y]):
                            # Highlight with a brighter color
                            pixels[y][x] = tuple(min(255, c + 40) for c in pixels[y][x])
            
            # Draw item in slot
            if inventory[i] is not None:
                item_color, _ = inventory[i]
                _ = slot_start + slot_width // 2
                
                # Draw item representation
                for y in range(size[1] - inventory_height, size[1]):
                    for x in range(slot_start + 1, slot_end - 1):
                        if y < len(pixels) and x < len(pixels[y]):
                            pixels[y][x] = item_color
    return pixels

def height_to_rgb(h):
    if h < water_level:
        t = h / water_level
        r = int(10 + t * (70 - 10))
        g = int(20 + t * (140 - 20))
        b = int(100 + t * (220 - 100))
        return [r, g, b], CI_WATER
    if h < sand_level:
        t = (h - water_level) / (sand_level - water_level)
        r = int(180 + t * (220 - 180))
        g = int(160 + t * (200 - 160))
        b = int(100 + t * (140 - 100))
        return [r, g, b], CI_SAND
    if h < grass_level:
        t = (h - sand_level) / (grass_level - sand_level)
        r = int(40 + t * (120 - 40))
        g = int(100 + t * (200 - 100))
        b = int(30 + t * (80 - 30))
        return [r, g, b], CI_GRASS
    if h < rock_level:
        t = (h - grass_level) / (rock_level - grass_level)
        r = int(100 + t * (120 - 100))
        g = int(90 + t * (110 - 90))
        b = int(80 + t * (90 - 80))
        return [r, g, b], CI_ROCK
    if h < snow_level:
        t = (h - rock_level) / (snow_level - rock_level)
        r = int(140 + t * (200 - 140))
        g = int(140 + t * (200 - 140))
        b = int(140 + t * (255 - 140))
        return [r, g, b], CI_SNOW
    t = (h - snow_level) / (1.0 - snow_level) if snow_level < 1.0 else 1.0
    r = int(220 + t * (35))
    g = int(220 + t * (35))
    b = int(230 + t * (25))
    return [min(255, r), min(255, g), min(255, b)], CI_SNOW_TOP

def get_chunk_key(world_pos):
    """Convert world position to chunk coordinates"""
    return (world_pos[0] // chunk_size[0], world_pos[1] // chunk_size[1])

def generate_chunk(chunk_key):
    cx, cy = chunk_key

    # Try loading from cache first
    if chunk_key in terrain_cache:
        return terrain_cache[chunk_key]

    # Otherwise generate new
    chunk = []
    chunkCollisionIndex = []
    start_x = cx * chunk_size[0]
    start_y = cy * chunk_size[1]

    for y in range(chunk_size[1]):
        row = []
        rowCollisionIndex = []
        for x in range(chunk_size[0]):
            nx = (x + start_x) / scale
            ny = (y + start_y) / scale
            h_raw = noise.pnoise2(nx, ny,
                                  octaves=octaves,
                                  persistence=persistence,
                                  lacunarity=lacunarity,
                                  repeatx=1024,
                                  repeaty=1024,
                                  base=seed)
            h = (h_raw + 1.0) / 2.0
            rgb, ci = height_to_rgb(h)
            row.append(rgb)
            rowCollisionIndex.append(ci)
        chunk.append(row)
        chunkCollisionIndex.append(rowCollisionIndex)

    # Save into RAM + DB
    terrain_cache[chunk_key] = chunk
    collisionIndexCache[chunk_key] = chunkCollisionIndex

    return chunk

def get_env() -> lmdb.Environment:
    global env
    if env is None:
        env = lmdb.open(DB_PATH, map_size=int(1e9))
    return env

def save_chunk_to_db(cx, cy, chunk, ci_chunk):
    key = f"{cx},{cy}".encode()
    data = zlib.compress(pickle.dumps((chunk, ci_chunk)))
    safe_put(key, data)


def load_chunk_from_db(cx, cy):
    try:
        key = f"{cx},{cy}".encode()
        with get_env().begin() as txn:
            data = txn.get(key)
            if data:
                return pickle.loads(zlib.decompress(data))
    except:
        return None

def safe_put(key: bytes, data: bytes):
    try:
        with get_env().begin(write=True) as txn:
            txn.put(key, data)
    except lmdb.MapFullError:
        # Double the map size and retry
        new_size = get_env().info()["map_size"] * 2
        get_env().set_mapsize(new_size)
        safe_put(key, data)

def load_game():
    """Load game state from file"""
    global terrain_cache, collisionIndexCache, player_position
    global seed, scale, octaves, persistence, lacunarity, selected_slot


    # save the previous data if the load function fails
    prev_terrain_cache = terrain_cache.copy()
    prev_collisionIndexCache = collisionIndexCache.copy()
    prev_player_position = player_position.copy()
    prev_lacunarity = lacunarity
    prev_persistence = persistence
    prev_octaves = octaves
    prev_scale = scale
    prev_seed = seed
    prev_selected_slot = selected_slot

    try:
        if not os.path.exists(DB_PATH):
            return "not exists"
        
        with get_env().begin() as txn:
            # Load metadata
            data = txn.get(b"metadata")
            if not data:
                return "not exists"
            state = pickle.loads(data)

            # Restore player + world
            player_position = state["player"]["position"]
            inventory[:] = state["player"]["inventory"]
            selected_slot = state["player"]["selected_slot"]
            seed = state["world"]["seed"]
            scale = state["world"]["scale"]
            octaves = state["world"]["octaves"]
            persistence = state["world"]["persistence"]
            lacunarity = state["world"]["lacunarity"]

            # Restore chunks
            with txn.cursor() as cursor:
                for key, value in cursor:
                    if key.startswith(b"chunk:"):
                        coords = tuple(map(int, key.decode().split(":")[1].split(",")))
                        chunk, ci_chunk = pickle.loads(zlib.decompress(value))
                        terrain_cache[coords] = chunk
                        collisionIndexCache[coords] = ci_chunk
        return "loaded"
    except Exception as e: # revert to the previous data when the function failed to load the save
        terrain_cache = prev_terrain_cache
        collisionIndexCache = prev_collisionIndexCache
        player_position = prev_player_position
        lacunarity = prev_lacunarity
        persistence = prev_persistence
        octaves = prev_octaves
        scale = prev_scale
        seed = prev_seed
        selected_slot = prev_selected_slot
        return "error", str(e)

def load_metadata():
    global player_position, inventory, selected_slot
    global seed, scale, octaves, persistence, lacunarity

    with get_env().begin() as txn:
        data = txn.get(b"metadata")
        if data:
            state = pickle.loads(data)
            # Player
            player_position = state["player"]["position"]
            inventory[:] = state["player"]["inventory"]
            selected_slot = state["player"]["selected_slot"]
            # World
            seed = state["world"]["seed"]
            scale = state["world"]["scale"]
            octaves = state["world"]["octaves"]
            persistence = state["world"]["persistence"]
            lacunarity = state["world"]["lacunarity"]
            return "loaded"
    return "error", "save file not exists"

def save_game():
    # Save metadata
    data = {
        "player": {
            "position": player_position,
            "inventory": inventory,
            "selected_slot": selected_slot
        },
        "world": {
            "seed": seed,
            "scale": scale,
            "octaves": octaves,
            "persistence": persistence,
            "lacunarity": lacunarity
        }
    }
    safe_put(b"metadata", pickle.dumps(data))

    # Save chunks
    for (cx, cy), chunk in terrain_cache.items():
        ci_chunk = collisionIndexCache[(cx, cy)]
        key = f"chunk:{cx},{cy}".encode()
        blob = zlib.compress(pickle.dumps((chunk, ci_chunk)))
        safe_put(key, blob)

def save_metadata():
    data = {
        "player": {
            "position": player_position,
            "inventory": inventory,
            "selected_slot": selected_slot
        },
        "world": {
            "seed": seed,
            "scale": scale,
            "octaves": octaves,
            "persistence": persistence,
            "lacunarity": lacunarity
        }
    }
    blob = pickle.dumps(data)
    safe_put(b"metadata", blob)

def get_terrain_at(position, size):
    """Get terrain for viewport, using cached chunks when available"""
    viewport_terrain = []
    
    for y in range(size[1]):
        row = []
        for x in range(size[0]):
            world_x = position[0] + x
            world_y = position[1] + y
            
            # Get chunk key for this position
            chunk_key = get_chunk_key((world_x, world_y))
            
            # Generate chunk if not cached
            if chunk_key not in terrain_cache:
                generate_chunk(chunk_key)
                
            # Get local position within chunk
            chunk_x = world_x % chunk_size[0]
            chunk_y = world_y % chunk_size[1]
            
            # Retrieve cached pixel
            chunk = terrain_cache[chunk_key]
            row.append(chunk[chunk_y][chunk_x])

        viewport_terrain.append(row)
    
    return viewport_terrain

def handle_input():
    """Check for keyboard input and update position"""
    global selected_slot
    moved = [0, 0]
    
    for key in pressedKeys:
        if not keyboard.is_pressed(key):
            pressedKeys.remove(key)
    
    # Process keyboard input
    if keyboard.is_pressed(keybinds["saveFile"]) and keybinds["saveFile"] not in pressedKeys:
        save_game()
        pressedKeys.append(keybinds["saveFile"])
    elif keyboard.is_pressed(keybinds["reloadSaveFile"]) and keybinds["reloadSaveFile"] not in pressedKeys:
        load_game()
        pressedKeys.append(keybinds["reloadSaveFile"])

    # Handle inventory selection (without keybinds)
    elif keyboard.is_pressed('1') and "1" not in pressedKeys:
        selected_slot = 0
        pressedKeys.append("1")
    elif keyboard.is_pressed('2') and "2" not in pressedKeys:
        selected_slot = 1
        pressedKeys.append("2")
    elif keyboard.is_pressed('3') and "3" not in pressedKeys:
        selected_slot = 2
        pressedKeys.append("3")
    elif keyboard.is_pressed('4') and "4" not in pressedKeys:
        selected_slot = 3
        pressedKeys.append("4")
    elif keyboard.is_pressed('5') and "5" not in pressedKeys:
        selected_slot = 4
        pressedKeys.append("5")
    elif keyboard.is_pressed('6') and "6" not in pressedKeys:
        selected_slot = 5
        pressedKeys.append("6")
    elif keyboard.is_pressed('7') and "7" not in pressedKeys:
        selected_slot = 6
        pressedKeys.append("7")
    elif keyboard.is_pressed('8') and "8" not in pressedKeys:
        selected_slot = 7
        pressedKeys.append("8")
    elif keyboard.is_pressed('9') and "9" not in pressedKeys:
        selected_slot = 8
        pressedKeys.append("9")
    
    # Handle inventory selection (with keybinds)
    elif keyboard.is_pressed(keybinds["decreaseInventoryIndex"]) and selected_slot > 0 and keybinds["decreaseInventoryIndex"] not in pressedKeys:
        selected_slot -= 1
        pressedKeys.append(keybinds["decreaseInventoryIndex"])
    elif keyboard.is_pressed(keybinds["increaseInventoryIndex"]) and selected_slot < 8 and keybinds["increaseInventoryIndex"] not in pressedKeys:
        selected_slot += 1
        pressedKeys.append(keybinds["increaseInventoryIndex"])
    
    # Collect resources when pressing space
    elif keyboard.is_pressed(keybinds["collectResource"]) and keybinds["collectResource"] not in pressedKeys:
        player_ci = get_collision_at(player_position[0], player_position[1])
        collect_resources(player_ci)
        pressedKeys.append(keybinds["collectResource"])
    
    elif keyboard.is_pressed(keybinds["walkRight"]):
        moved[0] += move_speed
    elif keyboard.is_pressed(keybinds["walkLeft"]):
        moved[0] -= move_speed
    elif keyboard.is_pressed(keybinds["walkBackward"]):
        moved[1] += move_speed
        pressedKeys.append(keybinds["walkBackward"])
    elif keyboard.is_pressed(keybinds["walkForward"]):
        moved[1] -= move_speed
    
    return moved

def get_collision_at(world_x, world_y):
    """Get collision index at a specific world position"""
    chunk_key = get_chunk_key((world_x, world_y))
    
    # Generate chunk if not cached
    if chunk_key not in collisionIndexCache:
        generate_chunk(chunk_key)
        
    # Get local position within chunk
    chunk_x = world_x % chunk_size[0]
    chunk_y = world_y % chunk_size[1]
    
    # Retrieve collision index
    return collisionIndexCache[chunk_key][chunk_y][chunk_x]

def tick(size):
    """Render function called each frame"""
    global current_position, player_position, selected_slot
    
    moved = handle_input()
    
    # Calculate potential new player position
    new_player_x = player_position[0] + moved[0]
    new_player_y = player_position[1] + moved[1]
    
    # Check collision at new position
    collision_index = get_collision_at(new_player_x, new_player_y)
    
    # Only update position if new location is walkable
    walkable_terrains = [CI_GRASS, CI_ROCK, CI_SAND, CI_WATER, CI_SNOW, CI_SNOW_TOP]
    if collision_index in walkable_terrains:
        player_position[0] = new_player_x
        player_position[1] = new_player_y
    
    # Center viewport on player
    viewport_width, viewport_height = size[0], size[1]
    current_position[0] = player_position[0] - viewport_width // 2
    current_position[1] = player_position[1] - viewport_height // 2
    
    # Get terrain for current viewport
    terrain = get_terrain_at(current_position, size)
    
    # Convert to pixel format
    pixels = []
    for y in range(size[1]):
        pixels.append([])
        for x in range(size[0]):
            pixels[y].append(tuple(terrain[y][x]))
    
    # Draw player marker at center of screen
    center_x = size[0] // 2
    center_y = size[1] // 2
    
    # Get collision index at player's current position
    player_collision = get_collision_at(player_position[0], player_position[1])
    
    # Set player color based on terrain
    if 0 <= center_y < len(pixels) and 0 <= center_x < len(pixels[0]):
        if player_collision == CI_WATER:
            player_color = (155, 0, 75)  # Blue in water
        else:
            player_color = (255, 0, 0)  # Red on other terrains
        
        # Draw player (top and bottom pixels)
        pixels[center_y][center_x] = player_color
        if center_y - 1 >= 0:  # Ensure we don't go above the top
            pixels[center_y-1][center_x] = player_color
    
    pixels = showInventory(pixels, size)
    
    return pixels

if __name__ == "__main__":
    # Try to load game on startup
    startup_state = load_game()
    if startup_state == "not exists":
        print("Starting new game..")
    elif startup_state == "loaded":
        print("Loading saved game..")
    elif isinstance(startup_state, tuple) and startup_state[0] == "error":
        print(f"Corrupted save file detected: {startup_state[1]}\nOverriding file...")
    
    time.sleep(1)
    
    # Initialize and run renderer
    render = ConsoleRenderer(tick)
    render.run()