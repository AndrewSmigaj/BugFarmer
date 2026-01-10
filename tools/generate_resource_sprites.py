#!/usr/bin/env python3
"""Generate resource item sprites (16x16) for Bug Farmer.

Design principles:
- 3/4 top-down perspective (see top AND front)
- Light source: top-left (highlights top-left, shadows bottom-right)
- 3-shade system per material (dark, base, light)
- Clear silhouette at 16x16
- Matches style of generate_tool_sprites.py

Resource types:
- Natural: wood, stone, fiber, flower, crystal, bone
- Mining: coal, copper_ore, iron_ore, silver_ore, gold_ore, platinum_ore, diamond
- Crafted: clay, dirt, iron_bar, brick, torch, sunflower_seed
"""

from PIL import Image
import os

# Transparent
T = (0, 0, 0, 0)

# === MATERIAL PALETTES (dark, base, light) ===

# Wood - warm brown tones
WOOD = ((70, 50, 35), (120, 90, 60), (160, 130, 95))

# Stone - gray tones
STONE = ((85, 85, 90), (120, 120, 125), (155, 155, 160))

# Fiber/Plant - green tones
FIBER = ((50, 90, 45), (85, 130, 70), (120, 165, 95))

# Flower - pink/red petals, yellow center
PETAL = ((180, 70, 90), (230, 100, 120), (255, 150, 160))
CENTER = ((200, 170, 40), (240, 210, 60), (255, 235, 100))
STEM = ((50, 100, 50), (70, 130, 60), (95, 160, 80))

# Crystal - purple tones
CRYSTAL = ((90, 50, 130), (140, 90, 180), (190, 150, 220))

# Bone - cream/white tones
BONE = ((180, 170, 155), (220, 210, 195), (245, 240, 230))

# Clay - terracotta/orange-brown
CLAY = ((130, 80, 60), (170, 110, 80), (200, 145, 110))

# Coal - very dark gray/black
COAL = ((25, 25, 30), (45, 45, 50), (70, 70, 75))

# Dirt - brown earth tones (from guide)
DIRT = ((110, 75, 40), (140, 95, 50), (165, 120, 70))

# Ores (dark, base, light for ore spots)
COPPER = ((140, 80, 50), (180, 110, 70), (210, 150, 100))
IRON = ((100, 75, 70), (140, 110, 105), (175, 145, 140))
SILVER = ((145, 145, 155), (185, 185, 195), (220, 220, 230))
GOLD = ((180, 140, 40), (230, 190, 60), (255, 220, 100))
PLATINUM = ((165, 170, 180), (200, 205, 215), (235, 240, 250))
DIAMOND_ORE = ((60, 160, 180), (100, 200, 220), (160, 235, 250))

# Refined materials
IRON_BAR = ((70, 75, 80), (110, 115, 120), (155, 160, 165))
BRICK = ((140, 65, 55), (180, 95, 75), (210, 130, 105))

# Torch
FLAME = ((255, 100, 20), (255, 160, 40), (255, 220, 80))

# Seed - dark striped
SEED = ((35, 30, 25), (60, 55, 45), (90, 80, 65))


def create_sprite_from_grid(grid):
    """Create an image from a pixel grid."""
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0
    img = Image.new('RGBA', (width, height), T)
    pixels = img.load()
    for y, row in enumerate(grid):
        for x, color in enumerate(row):
            pixels[x, y] = color
    return img


def c(rgb):
    """Convert RGB tuple to RGBA."""
    return (rgb[0], rgb[1], rgb[2], 255)


def build_wood():
    """Wood log: 16x16 - horizontal log showing rings on left end, bark on body."""
    d, m, l = [c(x) for x in WOOD]
    ring = (90, 65, 45, 255)
    grid = [[T] * 16 for _ in range(16)]

    # Log body (horizontal cylinder, rows 4-11)
    for y in range(4, 12):
        for x in range(4, 14):
            if y == 4 or y == 5:
                grid[y][x] = l  # Top lit
            elif y >= 10:
                grid[y][x] = d  # Bottom shadow
            else:
                grid[y][x] = m  # Middle

    # Left end cap (showing tree rings)
    for y in range(5, 11):
        for x in range(2, 5):
            if y == 5:
                grid[y][x] = l
            elif y == 10:
                grid[y][x] = d
            else:
                grid[y][x] = m
    # Ring detail
    grid[7][3] = ring
    grid[8][3] = ring

    # Bark texture lines on top
    grid[5][6] = d
    grid[5][9] = d
    grid[5][12] = d

    # Right edge
    grid[6][13] = d
    grid[7][13] = d
    grid[8][13] = d
    grid[9][13] = d

    return grid


def build_stone():
    """Stone chunk: 16x16 - chunky rock with top/front planes and ground contact."""
    d, m, l = [c(x) for x in STONE]
    grid = [[T] * 16 for _ in range(16)]

    # Rock shape - top surface (rows 3-9, ~60%) and front face (rows 10-13, ~30%)
    # Top surface
    top_shape = [
        (3, 6, 10),
        (4, 5, 11),
        (5, 4, 12),
        (6, 3, 13),
        (7, 3, 13),
        (8, 3, 13),
        (9, 4, 12),
    ]
    for y, x_start, x_end in top_shape:
        for x in range(x_start, x_end):
            if x < 6:
                grid[y][x] = l  # Left lit
            elif x > 10:
                grid[y][x] = m  # Right slightly darker
            else:
                grid[y][x] = l if y < 5 else m

    # Clustered texture on top (not random)
    grid[5][5] = m
    grid[5][6] = m
    grid[7][8] = d
    grid[7][9] = d

    # Front face (darker, rows 10-13)
    front_shape = [
        (10, 4, 12),
        (11, 5, 11),
        (12, 6, 10),
        (13, 7, 9),
    ]
    for y, x_start, x_end in front_shape:
        for x in range(x_start, x_end):
            grid[y][x] = d

    # Ground contact - extra dark bottom
    ground = (max(0, d[0]-20), max(0, d[1]-20), max(0, d[2]-20), 255)
    grid[13][7] = ground
    grid[13][8] = ground

    return grid


def build_fiber():
    """Fiber bundle: 16x16 - tied bundle of plant fibers."""
    d, m, l = [c(x) for x in FIBER]
    tie = c(WOOD[0])
    grid = [[T] * 16 for _ in range(16)]

    # Vertical fiber strands
    strands = [(5, 3, 13), (7, 2, 14), (9, 2, 14), (11, 3, 13)]
    for x, y_start, y_end in strands:
        for y in range(y_start, y_end):
            if y < 5:
                grid[y][x] = l
            elif y > 11:
                grid[y][x] = d
            else:
                grid[y][x] = m
            # Skip tie area
            if 7 <= y <= 8:
                continue

    # Tie in middle (horizontal band)
    for x in range(4, 12):
        grid[7][x] = tie
        grid[8][x] = tie

    return grid


def build_flower():
    """Flower: 16x16 - simple 5-petal flower with center."""
    pd, pm, pl = [c(x) for x in PETAL]
    cd, cm, cl = [c(x) for x in CENTER]
    sd, sm, sl = [c(x) for x in STEM]
    grid = [[T] * 16 for _ in range(16)]

    # Petals (5 around center at row 6)
    # Top petal
    grid[2][7] = pl; grid[2][8] = pm
    grid[3][7] = pm; grid[3][8] = pm
    grid[4][7] = pm; grid[4][8] = pd

    # Left-top petal
    grid[4][4] = pl; grid[4][5] = pm
    grid[5][4] = pm; grid[5][5] = pd

    # Right-top petal
    grid[4][10] = pm; grid[4][11] = pl
    grid[5][10] = pd; grid[5][11] = pm

    # Left-bottom petal
    grid[7][4] = pm; grid[7][5] = pd
    grid[8][4] = pd; grid[8][5] = pd

    # Right-bottom petal
    grid[7][10] = pd; grid[7][11] = pm
    grid[8][10] = pd; grid[8][11] = pd

    # Center
    grid[5][7] = cl; grid[5][8] = cm
    grid[6][7] = cm; grid[6][8] = cd
    grid[7][7] = cd; grid[7][8] = cd

    # Stem
    for y in range(9, 15):
        grid[y][7] = sm if y < 13 else sd
        grid[y][8] = sl if y < 11 else sm

    return grid


def build_crystal():
    """Crystal gem: 16x16 - faceted gem shape."""
    d, m, l = [c(x) for x in CRYSTAL]
    shine = (255, 255, 255, 200)
    grid = [[T] * 16 for _ in range(16)]

    # Diamond/crystal shape (pointed top and bottom)
    # Top point (rows 2-4)
    grid[2][7] = l; grid[2][8] = l
    grid[3][6] = l; grid[3][7] = l; grid[3][8] = m; grid[3][9] = m

    # Upper body (rows 4-7)
    for y in range(4, 8):
        width = 3 + (y - 4)
        for x in range(8 - width, 8 + width):
            if x < 7:
                grid[y][x] = l
            elif x > 8:
                grid[y][x] = d
            else:
                grid[y][x] = m

    # Lower body (rows 8-12, tapering)
    for y in range(8, 13):
        width = 6 - (y - 8)
        if width <= 0:
            width = 1
        for x in range(8 - width, 8 + width):
            if x < 7:
                grid[y][x] = m
            elif x > 8:
                grid[y][x] = d
            else:
                grid[y][x] = d

    # Bottom point
    grid[13][7] = d; grid[13][8] = d

    # Shine highlight
    grid[4][5] = shine
    grid[5][6] = shine

    return grid


def build_bone():
    """Bone: 16x16 - horizontal bone with knobs on ends."""
    d, m, l = [c(x) for x in BONE]
    grid = [[T] * 16 for _ in range(16)]

    # Left knob
    grid[5][2] = l; grid[5][3] = l
    grid[6][1] = l; grid[6][2] = l; grid[6][3] = m
    grid[7][1] = m; grid[7][2] = m; grid[7][3] = m
    grid[8][1] = m; grid[8][2] = m; grid[8][3] = m
    grid[9][1] = d; grid[9][2] = d; grid[9][3] = d
    grid[10][2] = d; grid[10][3] = d

    # Middle shaft
    for x in range(4, 12):
        grid[6][x] = l
        grid[7][x] = m
        grid[8][x] = m
        grid[9][x] = d

    # Right knob
    grid[5][12] = l; grid[5][13] = l
    grid[6][12] = m; grid[6][13] = l; grid[6][14] = l
    grid[7][12] = m; grid[7][13] = m; grid[7][14] = m
    grid[8][12] = m; grid[8][13] = m; grid[8][14] = d
    grid[9][12] = d; grid[9][13] = d; grid[9][14] = d
    grid[10][12] = d; grid[10][13] = d

    return grid


def build_clay():
    """Clay ball: 16x16 - rounded lump with top/front planes and ground contact."""
    d, m, l = [c(x) for x in CLAY]
    grid = [[T] * 16 for _ in range(16)]

    # Top surface (rows 4-9, ~55%)
    top_shape = [
        (4, 6, 10),
        (5, 5, 11),
        (6, 4, 12),
        (7, 4, 12),
        (8, 4, 12),
        (9, 5, 11),
    ]
    for y, x_start, x_end in top_shape:
        for x in range(x_start, x_end):
            if x < 7:
                grid[y][x] = l  # Left lit
            elif x > 9:
                grid[y][x] = m
            else:
                grid[y][x] = l if y < 6 else m

    # Front face (rows 10-12, ~30%)
    front_shape = [
        (10, 4, 12),
        (11, 5, 11),
        (12, 6, 10),
    ]
    for y, x_start, x_end in front_shape:
        for x in range(x_start, x_end):
            grid[y][x] = d

    # Ground contact
    ground = (max(0, d[0]-20), max(0, d[1]-20), max(0, d[2]-20), 255)
    for x in range(6, 10):
        grid[12][x] = ground

    return grid


def build_coal():
    """Coal chunk: 16x16 - dark irregular chunk with clustered texture and ground contact."""
    d, m, l = [c(x) for x in COAL]
    grid = [[T] * 16 for _ in range(16)]

    # Top surface (rows 4-9, ~55%)
    top_shape = [
        (4, 5, 11),
        (5, 4, 12),
        (6, 3, 13),
        (7, 3, 13),
        (8, 4, 12),
        (9, 5, 11),
    ]
    for y, x_start, x_end in top_shape:
        for x in range(x_start, x_end):
            if x < 7 and y < 7:
                grid[y][x] = l  # Top-left highlight
            else:
                grid[y][x] = m

    # Clustered highlight spots (not random)
    grid[5][5] = l
    grid[5][6] = l
    grid[6][5] = l
    grid[7][9] = l
    grid[7][10] = l

    # Front face (rows 10-13, ~35%)
    front_shape = [
        (10, 4, 12),
        (11, 5, 11),
        (12, 6, 10),
        (13, 7, 9),
    ]
    for y, x_start, x_end in front_shape:
        for x in range(x_start, x_end):
            grid[y][x] = d

    # Ground contact
    ground = (max(0, d[0]-15), max(0, d[1]-15), max(0, d[2]-15), 255)
    grid[13][7] = ground
    grid[13][8] = ground

    return grid


def build_dirt():
    """Dirt pile: 16x16 - mound with top/front planes and ground contact."""
    d, m, l = [c(x) for x in DIRT]
    grid = [[T] * 16 for _ in range(16)]

    # Top surface (rows 5-9, ~55%)
    top_shape = [
        (5, 6, 10),
        (6, 5, 11),
        (7, 4, 12),
        (8, 4, 12),
        (9, 4, 12),
    ]
    for y, x_start, x_end in top_shape:
        for x in range(x_start, x_end):
            if x < 7:
                grid[y][x] = l  # Left lit
            elif x > 9:
                grid[y][x] = m
            else:
                grid[y][x] = l if y < 7 else m

    # Horizontal strata texture (patterned, not random)
    grid[6][6] = m
    grid[6][7] = m
    grid[8][5] = d
    grid[8][6] = d
    grid[8][9] = d

    # Front face (rows 10-13, ~35%)
    front_shape = [
        (10, 3, 13),
        (11, 4, 12),
        (12, 5, 11),
        (13, 6, 10),
    ]
    for y, x_start, x_end in front_shape:
        for x in range(x_start, x_end):
            grid[y][x] = d

    # Ground contact - extra dark
    ground = (max(0, d[0]-25), max(0, d[1]-25), max(0, d[2]-25), 255)
    for x in range(6, 10):
        grid[13][x] = ground

    return grid


def build_ore(ore_palette):
    """Generic ore: 16x16 - stone base with connected ore veins and ground contact."""
    sd, sm, sl = [c(x) for x in STONE]
    od, om, ol = [c(x) for x in ore_palette]
    grid = [[T] * 16 for _ in range(16)]

    # Top surface (rows 3-9, ~60%)
    top_shape = [
        (3, 6, 10),
        (4, 5, 11),
        (5, 4, 12),
        (6, 3, 13),
        (7, 3, 13),
        (8, 3, 13),
        (9, 4, 12),
    ]
    for y, x_start, x_end in top_shape:
        for x in range(x_start, x_end):
            if x < 6:
                grid[y][x] = sl
            elif x > 10:
                grid[y][x] = sm
            else:
                grid[y][x] = sl if y < 5 else sm

    # Front face (rows 10-13, ~35%)
    front_shape = [
        (10, 4, 12),
        (11, 5, 11),
        (12, 6, 10),
        (13, 7, 9),
    ]
    for y, x_start, x_end in front_shape:
        for x in range(x_start, x_end):
            grid[y][x] = sd

    # Connected ore vein on top (L-shaped cluster)
    vein_top = [(5, 5), (5, 6), (6, 6), (6, 7), (7, 7)]
    for x, y in vein_top:
        if grid[y][x] != T:
            grid[y][x] = ol if x < 6 else om

    # Second cluster
    vein_top2 = [(9, 7), (9, 8), (10, 8)]
    for x, y in vein_top2:
        if grid[y][x] != T:
            grid[y][x] = om

    # Ore on front face (darker)
    vein_front = [(6, 10), (7, 10), (7, 11)]
    for x, y in vein_front:
        if grid[y][x] != T:
            grid[y][x] = od

    # Ground contact
    ground = (max(0, sd[0]-20), max(0, sd[1]-20), max(0, sd[2]-20), 255)
    grid[13][7] = ground
    grid[13][8] = ground

    return grid


def build_diamond():
    """Cut diamond: 16x16 - brilliant cut gem."""
    d, m, l = [c(x) for x in DIAMOND_ORE]
    shine = (255, 255, 255, 255)
    grid = [[T] * 16 for _ in range(16)]

    # Top crown (rows 3-7)
    grid[3][7] = l; grid[3][8] = l
    grid[4][6] = l; grid[4][7] = l; grid[4][8] = m; grid[4][9] = m
    grid[5][5] = l; grid[5][6] = l; grid[5][7] = m; grid[5][8] = m; grid[5][9] = m; grid[5][10] = d
    grid[6][4] = l; grid[6][5] = l; grid[6][6] = m; grid[6][7] = m; grid[6][8] = m; grid[6][9] = d; grid[6][10] = d; grid[6][11] = d
    grid[7][4] = m; grid[7][5] = m; grid[7][6] = m; grid[7][7] = m; grid[7][8] = m; grid[7][9] = m; grid[7][10] = d; grid[7][11] = d

    # Girdle (row 8)
    for x in range(4, 12):
        grid[8][x] = d

    # Pavilion (rows 9-13)
    grid[9][5] = m; grid[9][6] = m; grid[9][7] = m; grid[9][8] = d; grid[9][9] = d; grid[9][10] = d
    grid[10][5] = m; grid[10][6] = m; grid[10][7] = d; grid[10][8] = d; grid[10][9] = d; grid[10][10] = d
    grid[11][6] = m; grid[11][7] = d; grid[11][8] = d; grid[11][9] = d
    grid[12][7] = d; grid[12][8] = d
    grid[13][7] = d

    # Shine
    grid[4][6] = shine
    grid[5][5] = shine

    return grid


def build_iron_bar():
    """Iron bar/ingot: 16x16 - metal ingot with ground contact."""
    d, m, l = [c(x) for x in IRON_BAR]
    grid = [[T] * 16 for _ in range(16)]

    # Top face (trapezoid, rows 4-6, ~30%)
    grid[4][4] = l; grid[4][5] = l; grid[4][6] = l; grid[4][7] = l
    grid[4][8] = l; grid[4][9] = l; grid[4][10] = m; grid[4][11] = m
    grid[5][4] = l; grid[5][5] = l; grid[5][6] = l; grid[5][7] = m
    grid[5][8] = m; grid[5][9] = m; grid[5][10] = m; grid[5][11] = m
    grid[6][4] = l; grid[6][5] = m; grid[6][6] = m; grid[6][7] = m
    grid[6][8] = m; grid[6][9] = m; grid[6][10] = m; grid[6][11] = d

    # Front face (darker, rows 7-11)
    for y in range(7, 12):
        for x in range(3, 13):
            if x == 3:
                grid[y][x] = m
            elif x >= 11:
                grid[y][x] = d
            else:
                grid[y][x] = m if y < 9 else d

    # Edge highlight
    grid[7][4] = l
    grid[7][5] = l

    # Ground contact
    ground = (max(0, d[0]-20), max(0, d[1]-20), max(0, d[2]-20), 255)
    for x in range(3, 13):
        grid[11][x] = ground

    return grid


def build_brick():
    """Brick: 16x16 - single brick with ground contact."""
    d, m, l = [c(x) for x in BRICK]
    grid = [[T] * 16 for _ in range(16)]

    # Top face (rectangle, rows 4-6, ~30%)
    for y in range(4, 7):
        for x in range(3, 13):
            if y == 4:
                grid[y][x] = l
            else:
                grid[y][x] = l if x < 6 else m

    # Front face (rows 7-11, ~50%)
    for y in range(7, 12):
        for x in range(3, 13):
            if x == 3:
                grid[y][x] = m
            elif x >= 11:
                grid[y][x] = d
            else:
                grid[y][x] = m if y < 10 else d

    # Edge lines
    grid[7][3] = d

    # Ground contact - extra dark bottom
    ground = (max(0, d[0]-25), max(0, d[1]-25), max(0, d[2]-25), 255)
    for x in range(3, 13):
        grid[11][x] = ground

    return grid


def build_sunflower_seed():
    """Sunflower seed: 16x16 - striped seed."""
    d, m, l = [c(x) for x in SEED]
    stripe = (80, 70, 55, 255)
    grid = [[T] * 16 for _ in range(16)]

    # Teardrop/oval shape
    shape = [
        (3, 7, 9),
        (4, 6, 10),
        (5, 6, 10),
        (6, 5, 11),
        (7, 5, 11),
        (8, 5, 11),
        (9, 5, 11),
        (10, 6, 10),
        (11, 6, 10),
        (12, 7, 9),
        (13, 7, 9),
    ]

    for y, x_start, x_end in shape:
        for x in range(x_start, x_end):
            if x < 7:
                grid[y][x] = l
            elif x > 8:
                grid[y][x] = d
            else:
                grid[y][x] = m

    # Vertical stripe
    for y in range(4, 13):
        if grid[y][7] != T:
            grid[y][7] = stripe
        if grid[y][8] != T:
            grid[y][8] = stripe

    return grid


def build_torch():
    """Torch: 16x16 - wooden handle with flame."""
    wd, wm, wl = [c(x) for x in WOOD]
    fd, fm, fl = [c(x) for x in FLAME]
    grid = [[T] * 16 for _ in range(16)]

    # Flame (top)
    grid[1][7] = fl; grid[1][8] = fl
    grid[2][6] = fl; grid[2][7] = fl; grid[2][8] = fm; grid[2][9] = fm
    grid[3][6] = fm; grid[3][7] = fm; grid[3][8] = fm; grid[3][9] = fd
    grid[4][6] = fm; grid[4][7] = fd; grid[4][8] = fd; grid[4][9] = fd
    grid[5][7] = fd; grid[5][8] = fd

    # Handle
    for y in range(6, 15):
        grid[y][7] = wd
        grid[y][8] = wm if y < 12 else wl

    return grid


def main():
    output_dir = "/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Resources/Items"
    os.makedirs(output_dir, exist_ok=True)

    resources = []

    # Basic resources
    items = [
        ("wood", build_wood),
        ("stone", build_stone),
        ("fiber", build_fiber),
        ("flower", build_flower),
        ("crystal", build_crystal),
        ("bone", build_bone),
        ("clay", build_clay),
        ("coal", build_coal),
        ("dirt", build_dirt),
        ("diamond", build_diamond),
        ("iron_bar", build_iron_bar),
        ("brick", build_brick),
        ("sunflower_seed", build_sunflower_seed),
        ("torch", build_torch),
    ]

    for name, func in items:
        grid = func()
        img = create_sprite_from_grid(grid)
        path = f"{output_dir}/{name}.png"
        img.save(path)
        resources.append(name)
        print(f"Created: {name}.png")

    # Ore variants
    ores = [
        ("copper_ore", COPPER),
        ("iron_ore", IRON),
        ("silver_ore", SILVER),
        ("gold_ore", GOLD),
        ("platinum_ore", PLATINUM),
    ]

    for name, palette in ores:
        grid = build_ore(palette)
        img = create_sprite_from_grid(grid)
        path = f"{output_dir}/{name}.png"
        img.save(path)
        resources.append(name)
        print(f"Created: {name}.png")

    print(f"\nCreated {len(resources)} resource sprites in {output_dir}")
    print("\nUnity import settings:")
    print("  - Texture Type: Sprite (2D and UI)")
    print("  - Sprite Mode: Single")
    print("  - Pixels Per Unit: 16")
    print("  - Filter Mode: Point (no filter)")
    print("  - Compression: None")


if __name__ == "__main__":
    main()
