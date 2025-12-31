#!/usr/bin/env python3
"""Generate terrain block sprites (16x16 pixels each) for Bug Farmer.

Design principles:
- Tileable: edges designed to match when repeated
- 45-degree top-down perspective
- Light source: top-left (consistent across all sprites)
- Shadows: bottom-right
- Simple: clear silhouettes at game scale
- Distinct: each terrain type visually unique
"""

from PIL import Image

# Colors (RGBA)
T = (0, 0, 0, 0)  # Transparent

# Grass - lush green with blade hints
G  = (72, 140, 72, 255)    # Grass base
Gl = (95, 165, 85, 255)    # Grass light (blade tips, top-left)
Gd = (55, 115, 55, 255)    # Grass dark (shadows, bottom-right)

# Dirt - brown earth
D  = (140, 95, 50, 255)    # Dirt base
Dl = (165, 120, 70, 255)   # Dirt light (pebbles)
Dd = (110, 75, 40, 255)    # Dirt dark (cracks)

# Rock/Stone - gray stone with clear lighting
R  = (120, 120, 125, 255)  # Rock base
Rl = (155, 155, 160, 255)  # Rock highlight (top-left)
Rd = (85, 85, 90, 255)     # Rock shadow (bottom-right)
Rm = (100, 100, 105, 255)  # Rock mid

# Water - shallow blue
W  = (70, 130, 180, 255)   # Water base
Wl = (100, 160, 210, 255)  # Water light (ripple highlights)
Wd = (50, 100, 150, 255)   # Water dark (depth)

# Cave floor - dark stone
C  = (70, 70, 75, 255)     # Cave base
Cl = (90, 90, 95, 255)     # Cave light
Cd = (50, 50, 55, 255)     # Cave dark

# Mud - wet brown
M  = (100, 70, 45, 255)    # Mud base
Ml = (120, 90, 60, 255)    # Mud light
Md = (80, 55, 35, 255)     # Mud dark

# Sand - warm beige
S  = (210, 190, 140, 255)  # Sand base
Sl = (230, 215, 170, 255)  # Sand light
Sd = (180, 160, 110, 255)  # Sand dark

# Water deep - darker blue
Wp = (40, 80, 140, 255)    # Deep water base
Wpl = (60, 100, 160, 255)  # Deep water light
Wpd = (25, 55, 110, 255)   # Deep water dark

# Wood floor - planks
Wd = (100, 75, 50, 255)    # Wood base
Wdl = (130, 100, 70, 255)  # Wood light
Wdd = (70, 50, 35, 255)    # Wood dark (gaps)

# Stone floor - polished tiles
Sf = (140, 140, 145, 255)  # Stone floor base
Sfl = (170, 170, 175, 255) # Stone floor light
Sfd = (110, 110, 115, 255) # Stone floor dark

def create_sprite_from_grid(grid):
    """Create an image from a pixel grid (any size)."""
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0
    img = Image.new('RGBA', (width, height), T)
    pixels = img.load()
    for y, row in enumerate(grid):
        for x, color in enumerate(row):
            pixels[x, y] = color
    return img

# =============================================================================
# 16x16 TERRAIN TILES
# =============================================================================
# All tiles follow these conventions:
# - Top-left lighting (Gl/Xl = light variants in top-left quadrant)
# - Bottom-right shadows (Gd/Xd = dark variants in bottom-right quadrant)
# - Tileable edges (left edge matches right, top matches bottom)
# =============================================================================

# Grass - 16x16 tileable with blade pattern
# Light top-left, shadows bottom-right, blade tips scattered throughout
GRASS_16 = [
    [Gl, Gl, G,  Gl, G,  G,  G,  G,  G,  Gl, G,  G,  G,  G,  G,  G ],
    [Gl, G,  G,  G,  Gl, G,  Gl, G,  G,  G,  G,  Gl, G,  G,  G,  G ],
    [G,  Gl, G,  G,  G,  G,  G,  G,  Gl, G,  G,  G,  G,  G,  G,  G ],
    [Gl, G,  G,  Gl, G,  G,  G,  G,  G,  G,  Gl, G,  G,  G,  G,  G ],
    [G,  G,  G,  G,  G,  Gl, G,  G,  G,  G,  G,  G,  G,  G,  G,  G ],
    [G,  Gl, G,  G,  G,  G,  G,  G,  G,  Gl, G,  G,  G,  G,  G,  G ],
    [G,  G,  G,  Gl, G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G ],
    [G,  G,  G,  G,  G,  G,  Gl, G,  G,  G,  G,  G,  G,  G,  G,  G ],
    [G,  G,  Gl, G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G ],
    [G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  Gd, G,  G ],
    [G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G ],
    [G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  Gd, G,  G,  Gd, G ],
    [G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  Gd],
    [G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  Gd, G,  G,  Gd, G,  Gd],
    [G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  Gd, G,  Gd, Gd],
    [G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  Gd, G,  Gd, Gd, Gd],
]

# Dirt - 16x16 tileable with pebble accents
DIRT_16 = [
    [Dl, Dl, D,  Dl, D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D ],
    [Dl, D,  D,  D,  Dl, D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D ],
    [D,  Dl, D,  D,  D,  D,  Dl, D,  D,  D,  D,  D,  D,  D,  D,  D ],
    [Dl, D,  D,  D,  D,  D,  D,  D,  D,  Dl, D,  D,  D,  D,  D,  D ],
    [D,  D,  Dl, D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D ],
    [D,  D,  D,  D,  Dl, D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D ],
    [D,  Dl, D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D ],
    [D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D ],
    [D,  D,  D,  Dl, D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D ],
    [D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  Dd, D,  D,  D ],
    [D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  Dd],
    [D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  Dd, D,  D,  Dd, D,  D ],
    [D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  Dd, D,  Dd, D ],
    [D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  Dd, D,  D,  Dd, Dd],
    [D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  Dd, Dd, D,  Dd],
    [D,  D,  D,  D,  D,  D,  D,  D,  D,  D,  Dd, D,  D,  Dd, Dd, Dd],
]

# Stone path - 16x16 cobblestone pattern
STONE_PATH_16 = [
    [Rl, Rl, Rl, Rl, R,  R,  R,  R,  R,  R,  R,  R,  Rm, Rm, Rm, Rm],
    [Rl, Rl, Rl, R,  R,  R,  Rd, R,  R,  R,  R,  R,  R,  Rm, Rm, Rm],
    [Rl, Rl, R,  R,  R,  R,  R,  R,  Rd, R,  R,  R,  R,  R,  Rm, Rm],
    [Rl, R,  R,  R,  R,  R,  R,  R,  R,  R,  R,  R,  R,  R,  R,  Rm],
    [Rd, Rd, Rd, Rd, Rl, Rl, Rl, R,  R,  R,  R,  R,  R,  R,  R,  R ],
    [R,  R,  R,  R,  Rl, Rl, R,  R,  R,  R,  Rd, R,  R,  R,  R,  R ],
    [R,  R,  R,  R,  Rl, R,  R,  R,  R,  R,  R,  R,  R,  R,  R,  Rm],
    [R,  R,  R,  R,  R,  R,  R,  R,  R,  R,  R,  R,  R,  R,  Rm, Rm],
    [R,  R,  R,  R,  R,  R,  R,  R,  Rd, Rd, Rd, Rl, Rl, R,  Rm, Rm],
    [R,  R,  Rd, R,  R,  R,  R,  R,  R,  R,  R,  Rl, R,  R,  R,  Rm],
    [R,  R,  R,  R,  R,  R,  R,  R,  R,  R,  R,  R,  R,  R,  R,  R ],
    [R,  R,  R,  R,  Rd, R,  R,  R,  R,  R,  R,  R,  R,  R,  Rd, Rd],
    [Rm, R,  R,  R,  R,  R,  R,  R,  R,  R,  R,  R,  Rd, Rd, Rd, Rd],
    [Rm, Rm, R,  R,  R,  R,  R,  Rd, R,  R,  R,  Rd, Rd, Rd, Rd, Rd],
    [Rm, Rm, Rm, R,  R,  R,  R,  R,  R,  R,  Rd, Rd, Rd, Rd, Rd, Rd],
    [Rm, Rm, Rm, Rm, R,  R,  R,  R,  R,  Rd, Rd, Rd, Rd, Rd, Rd, Rd],
]

# Water shallow - 16x16 with ripple pattern
WATER_SHALLOW_16 = [
    [Wl, Wl, W,  Wl, W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W ],
    [Wl, W,  W,  W,  Wl, W,  W,  W,  W,  Wl, W,  W,  W,  W,  W,  W ],
    [W,  Wl, W,  W,  W,  W,  Wl, W,  W,  W,  W,  W,  W,  W,  W,  W ],
    [Wl, W,  W,  W,  W,  W,  W,  W,  W,  W,  Wl, W,  W,  W,  W,  W ],
    [W,  W,  Wl, W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W ],
    [W,  W,  W,  Wl, W,  W,  W,  W,  W,  Wl, W,  W,  W,  W,  W,  W ],
    [W,  Wl, W,  W,  W,  W,  Wl, W,  W,  W,  W,  W,  W,  W,  W,  W ],
    [W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W ],
    [W,  W,  W,  Wl, W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W ],
    [W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  Wd, W,  W,  W ],
    [W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  Wd],
    [W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  Wd, W,  W,  Wd, W,  W ],
    [W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  Wd, W,  Wd, W ],
    [W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  Wd, W,  W,  Wd, Wd],
    [W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  Wd, Wd, W,  Wd],
    [W,  W,  W,  W,  W,  W,  W,  W,  W,  W,  Wd, W,  W,  Wd, Wd, Wd],
]

# Cave floor - 16x16 dark rough stone
CAVE_FLOOR_16 = [
    [Cl, Cl, C,  Cl, C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C ],
    [Cl, C,  C,  C,  Cl, C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C ],
    [C,  Cl, C,  C,  C,  C,  Cl, C,  C,  C,  C,  C,  C,  C,  C,  C ],
    [Cl, C,  C,  C,  C,  C,  C,  C,  C,  Cl, C,  C,  C,  C,  C,  C ],
    [C,  C,  Cl, C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C ],
    [C,  C,  C,  C,  Cl, C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C ],
    [C,  Cl, C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C ],
    [C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C ],
    [C,  C,  C,  Cl, C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C ],
    [C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  Cd, C,  C,  C ],
    [C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  Cd],
    [C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  Cd, C,  C,  Cd, C,  C ],
    [C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  Cd, C,  Cd, C ],
    [C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  Cd, C,  C,  Cd, Cd],
    [C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  Cd, Cd, C,  Cd],
    [C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  Cd, C,  C,  Cd, Cd, Cd],
]

# Mud - 16x16 wet earth
MUD_16 = [
    [Ml, Ml, M,  Ml, M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M ],
    [Ml, M,  M,  M,  Ml, M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M ],
    [M,  Ml, M,  M,  M,  M,  Ml, M,  M,  M,  M,  M,  M,  M,  M,  M ],
    [Ml, M,  M,  M,  M,  M,  M,  M,  M,  Ml, M,  M,  M,  M,  M,  M ],
    [M,  M,  Ml, M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M ],
    [M,  M,  M,  M,  Ml, M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M ],
    [M,  Ml, M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M ],
    [M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M ],
    [M,  M,  M,  Ml, M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M ],
    [M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  Md, M,  M,  M ],
    [M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  Md],
    [M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  Md, M,  M,  Md, M,  M ],
    [M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  Md, M,  Md, M ],
    [M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  Md, M,  M,  Md, Md],
    [M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  Md, Md, M,  Md],
    [M,  M,  M,  M,  M,  M,  M,  M,  M,  M,  Md, M,  M,  Md, Md, Md],
]

# Sand - 16x16 beach/desert sand
SAND_16 = [
    [Sl, Sl, S,  Sl, S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S ],
    [Sl, S,  S,  S,  Sl, S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S ],
    [S,  Sl, S,  S,  S,  S,  Sl, S,  S,  S,  S,  S,  S,  S,  S,  S ],
    [Sl, S,  S,  S,  S,  S,  S,  S,  S,  Sl, S,  S,  S,  S,  S,  S ],
    [S,  S,  Sl, S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S ],
    [S,  S,  S,  S,  Sl, S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S ],
    [S,  Sl, S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S ],
    [S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S ],
    [S,  S,  S,  Sl, S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S ],
    [S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  Sd, S,  S,  S ],
    [S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  Sd],
    [S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  Sd, S,  S,  Sd, S,  S ],
    [S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  Sd, S,  Sd, S ],
    [S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  Sd, S,  S,  Sd, Sd],
    [S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  Sd, Sd, S,  Sd],
    [S,  S,  S,  S,  S,  S,  S,  S,  S,  S,  Sd, S,  S,  Sd, Sd, Sd],
]

# Water deep - 16x16 darker water
WATER_DEEP_16 = [
    [Wpl,Wpl,Wp, Wpl,Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp ],
    [Wpl,Wp, Wp, Wp, Wpl,Wp, Wp, Wp, Wp, Wpl,Wp, Wp, Wp, Wp, Wp, Wp ],
    [Wp, Wpl,Wp, Wp, Wp, Wp, Wpl,Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp ],
    [Wpl,Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wpl,Wp, Wp, Wp, Wp, Wp ],
    [Wp, Wp, Wpl,Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp ],
    [Wp, Wp, Wp, Wpl,Wp, Wp, Wp, Wp, Wp, Wpl,Wp, Wp, Wp, Wp, Wp, Wp ],
    [Wp, Wpl,Wp, Wp, Wp, Wp, Wpl,Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp ],
    [Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp ],
    [Wp, Wp, Wp, Wpl,Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp ],
    [Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wpd,Wp, Wp, Wp ],
    [Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wpd],
    [Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wpd,Wp, Wp, Wpd,Wp, Wp ],
    [Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wpd,Wp, Wpd,Wp ],
    [Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wpd,Wp, Wp, Wpd,Wpd],
    [Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wpd,Wpd,Wp, Wpd],
    [Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wp, Wpd,Wp, Wp, Wpd,Wpd,Wpd],
]

# Wood floor - 16x16 plank pattern
WOOD_FLOOR_16 = [
    [Wdl,Wdl,Wdl,Wdd,Wdl,Wdl,Wdl,Wdd,Wdl,Wd, Wd, Wdd,Wd, Wd, Wd, Wdd],
    [Wdl,Wdl,Wd, Wdd,Wdl,Wd, Wd, Wdd,Wd, Wd, Wd, Wdd,Wd, Wd, Wd, Wdd],
    [Wdl,Wd, Wd, Wdd,Wd, Wd, Wd, Wdd,Wd, Wd, Wd, Wdd,Wd, Wd, Wd, Wdd],
    [Wd, Wd, Wd, Wdd,Wd, Wd, Wd, Wdd,Wd, Wd, Wd, Wdd,Wd, Wd, Wd, Wdd],
    [Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd],
    [Wd, Wd, Wdl,Wdd,Wd, Wdl,Wdl,Wdd,Wd, Wd, Wd, Wdd,Wd, Wd, Wd, Wdd],
    [Wd, Wd, Wd, Wdd,Wdl,Wdl,Wd, Wdd,Wd, Wd, Wd, Wdd,Wd, Wd, Wd, Wdd],
    [Wd, Wd, Wd, Wdd,Wdl,Wd, Wd, Wdd,Wd, Wd, Wd, Wdd,Wd, Wd, Wd, Wdd],
    [Wd, Wd, Wd, Wdd,Wd, Wd, Wd, Wdd,Wd, Wd, Wd, Wdd,Wd, Wd, Wd, Wdd],
    [Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd],
    [Wd, Wd, Wd, Wdd,Wd, Wd, Wd, Wdd,Wd, Wdl,Wdl,Wdd,Wd, Wd, Wd, Wdd],
    [Wd, Wd, Wd, Wdd,Wd, Wd, Wd, Wdd,Wdl,Wdl,Wd, Wdd,Wd, Wd, Wd, Wdd],
    [Wd, Wd, Wd, Wdd,Wd, Wd, Wd, Wdd,Wdl,Wd, Wd, Wdd,Wd, Wd, Wd, Wdd],
    [Wd, Wd, Wd, Wdd,Wd, Wd, Wd, Wdd,Wd, Wd, Wd, Wdd,Wd, Wd, Wd, Wdd],
    [Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd,Wdd],
    [Wd, Wd, Wd, Wdd,Wd, Wd, Wd, Wdd,Wd, Wd, Wd, Wdd,Wd, Wd, Wd, Wdd],
]

# Stone floor - 16x16 polished tile pattern
STONE_FLOOR_16 = [
    [Sfl,Sfl,Sfl,Sfl,Sfl,Sfl,Sfl,Sfd,Sf, Sf, Sf, Sf, Sf, Sf, Sf, Sfd],
    [Sfl,Sfl,Sfl,Sf, Sf, Sf, Sf, Sfd,Sf, Sf, Sf, Sf, Sf, Sf, Sf, Sfd],
    [Sfl,Sfl,Sf, Sf, Sf, Sf, Sf, Sfd,Sf, Sf, Sf, Sf, Sf, Sf, Sf, Sfd],
    [Sfl,Sf, Sf, Sf, Sf, Sf, Sf, Sfd,Sf, Sf, Sf, Sf, Sf, Sf, Sf, Sfd],
    [Sfl,Sf, Sf, Sf, Sf, Sf, Sf, Sfd,Sf, Sf, Sf, Sf, Sf, Sf, Sf, Sfd],
    [Sf, Sf, Sf, Sf, Sf, Sf, Sf, Sfd,Sf, Sf, Sf, Sf, Sf, Sf, Sfd,Sfd],
    [Sf, Sf, Sf, Sf, Sf, Sf, Sf, Sfd,Sf, Sf, Sf, Sf, Sf, Sfd,Sfd,Sfd],
    [Sfd,Sfd,Sfd,Sfd,Sfd,Sfd,Sfd,Sfd,Sfd,Sfd,Sfd,Sfd,Sfd,Sfd,Sfd,Sfd],
    [Sfl,Sfl,Sfl,Sfl,Sfl,Sfl,Sfl,Sfd,Sf, Sf, Sf, Sf, Sf, Sf, Sf, Sfd],
    [Sfl,Sfl,Sf, Sf, Sf, Sf, Sf, Sfd,Sf, Sf, Sf, Sf, Sf, Sf, Sf, Sfd],
    [Sfl,Sf, Sf, Sf, Sf, Sf, Sf, Sfd,Sf, Sf, Sf, Sf, Sf, Sf, Sf, Sfd],
    [Sf, Sf, Sf, Sf, Sf, Sf, Sf, Sfd,Sf, Sf, Sf, Sf, Sf, Sf, Sf, Sfd],
    [Sf, Sf, Sf, Sf, Sf, Sf, Sf, Sfd,Sf, Sf, Sf, Sf, Sf, Sf, Sf, Sfd],
    [Sf, Sf, Sf, Sf, Sf, Sf, Sf, Sfd,Sf, Sf, Sf, Sf, Sf, Sf, Sfd,Sfd],
    [Sf, Sf, Sf, Sf, Sf, Sf, Sfd,Sfd,Sf, Sf, Sf, Sf, Sf, Sfd,Sfd,Sfd],
    [Sfd,Sfd,Sfd,Sfd,Sfd,Sfd,Sfd,Sfd,Sfd,Sfd,Sfd,Sfd,Sfd,Sfd,Sfd,Sfd],
]

# Garden plot - 16x16 hoed dirt rows
# Tilled rows running horizontally
Hp = (90, 60, 35, 255)     # Hoed plot base (darker tilled soil)
Hpl = (110, 75, 45, 255)   # Hoed plot light (ridge tops)
Hpd = (65, 45, 25, 255)    # Hoed plot dark (furrows)

GARDEN_PLOT_16 = [
    [Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl],
    [Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp ],
    [Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd],
    [Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl],
    [Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp ],
    [Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd],
    [Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl],
    [Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp ],
    [Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd],
    [Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl],
    [Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp ],
    [Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd],
    [Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl,Hpl],
    [Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp ],
    [Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd,Hpd],
    [Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp, Hp ],
]

def main():
    import os
    output_dir = "/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Sprites/Terrain"

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # 16x16 terrain tiles
    sprites_16 = [
        ("grass.png", GRASS_16),
        ("dirt.png", DIRT_16),
        ("stone_path.png", STONE_PATH_16),
        ("water_shallow.png", WATER_SHALLOW_16),
        ("water_deep.png", WATER_DEEP_16),
        ("cave_floor.png", CAVE_FLOOR_16),
        ("mud.png", MUD_16),
        ("sand.png", SAND_16),
        ("wood_floor.png", WOOD_FLOOR_16),
        ("stone_floor.png", STONE_FLOOR_16),
        ("garden_plot.png", GARDEN_PLOT_16),
    ]

    for filename, grid in sprites_16:
        img = create_sprite_from_grid(grid)
        path = f"{output_dir}/{filename}"
        img.save(path)
        print(f"Created: {path}")

    # Create tileset (11 tiles in a row, 176x16)
    tiles = [GRASS_16, DIRT_16, STONE_PATH_16, WATER_SHALLOW_16, WATER_DEEP_16,
             CAVE_FLOOR_16, MUD_16, SAND_16, WOOD_FLOOR_16, STONE_FLOOR_16, GARDEN_PLOT_16]
    sheet = Image.new('RGBA', (len(tiles) * 16, 16), T)
    for i, grid in enumerate(tiles):
        sprite = create_sprite_from_grid(grid)
        sheet.paste(sprite, (i * 16, 0))

    sheet_path = f"{output_dir}/terrain_tileset.png"
    sheet.save(sheet_path)
    print(f"Created tileset: {sheet_path}")

    print("\nUnity import settings:")
    print("  - Pixels Per Unit: 16")
    print("  - Filter Mode: Point (no filter)")
    print("  - Compression: None")
    print("  - Sprite Mode: Multiple (for tileset)")

if __name__ == "__main__":
    main()
