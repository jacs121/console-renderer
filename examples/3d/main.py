import math
import termgfx
import cProfile
import pstats
import io

from termgfx.textures import Image

def render_sphere_ascii(width=80, height=80, radius=1.0, light_dir=(1, -1, 1), light_strength=1):
    W, H = width, height
    zbuffer = [[-1e9 for _ in range(W)] for __ in range(H)]
    colors: list[list[termgfx.Color]] = [[termgfx.Color("RGB", [0,0,0]) for _ in range(W)] for __ in range(H)]
    lx, ly, lz = light_dir
    lnorm = math.sqrt(lx*lx + ly*ly + lz*lz)
    lx, ly, lz = lx/lnorm, ly/lnorm, lz/lnorm

    lat_steps = int(80*radius)
    lon_steps = int(160*radius)
    for i in range(lat_steps+1):
        theta = math.pi * (i / lat_steps)
        sin_t = math.sin(theta)
        cos_t = math.cos(theta)
        for j in range(lon_steps):
            phi = 2 * math.pi * (j / lon_steps)
            sin_p = math.sin(phi)
            cos_p = math.cos(phi)
            x = radius * sin_t * cos_p
            y = radius * cos_t
            z = radius * sin_t * sin_p

            # Rotation for better view
            rot_y = 0.4
            cosr, sinr = math.cos(rot_y), math.sin(rot_y)
            xr = x*cosr + z*sinr
            zr = -x*sinr + z*cosr

            cam_z = 3.0
            if cam_z - zr == 0:
                continue
            proj_x = xr / (cam_z - zr)
            proj_y = y / (cam_z - zr)
            sx = int((proj_x * 20) + W//2)
            sy = int((proj_y * 20) + H//2)

            if 0 <= sx < W and 0 <= sy < H:
                nx, ny, nz = x/radius, y/radius, z/radius
                dp = (nx*lx + ny*ly + nz*lz) * light_strength
                dp = max(0, min(1, dp))
                depth = zr
                
                if depth > zbuffer[sy][sx]:
                    zbuffer[sy][sx] = depth
                    colors[sy][sx] = termgfx.Color("RGB", [255*dp, 255*dp, 255*dp])
    return colors

def update(size: termgfx.Vector2):
    global Iframe
    # Iframe += 1
    light_dir = (
        math.cos(Iframe/10 * 0.7),
        -0.5 + 0.25 * math.sin(Iframe/10 * 0.3),
        math.sin(Iframe/10 * 0.9)
    )
    # radius behaves naturally now
    frame = render_sphere_ascii(
        width=size.y,
        height=size.x,
        radius=2.0,  # bigger = actually bigger now
        light_dir=light_dir,
    )
    img = Image.from_list(frame)
    return termgfx.Texture(img)

Iframe = 10
# --- Profile it ---
total_calls = []
total_times = []
threadCounts = []

for threadCount in range(50):
    profiler = cProfile.Profile()
    profiler.enable()

    renderer = termgfx.ConsoleRenderer(update, threadCount=threadCount+1)
    renderer.showFrame()

    profiler.disable()

    # --- Extract only total time and call count ---
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).strip_dirs().sort_stats("cumulative")

    total_calls.append(sum(stat[1] for stat in ps.stats.values()))  # total number of calls
    total_times.append(sum(stat[3] for stat in ps.stats.values()))    # total time spent (seconds)
    threadCounts.append(threadCount+1)

open("data.txt", "w")
for calls, time, threadCount in zip(total_calls, total_times, threadCounts):
    open("data.txt", "a").write(f"threadCounts ({threadCount}): calls:{calls} time:{time}\n")