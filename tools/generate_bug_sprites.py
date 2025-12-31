#!/usr/bin/env python3
"""Generate bug/insect sprites for Bug Farmer.

Design principles:
- 45-degree top-down perspective (seeing top/back of bugs)
- Body shape is key identifier
- Wings semi-transparent where applicable
- Eyes as accent color
- Sizes from 8×8 to 16×16
"""

from PIL import Image
import os

# Colors (RGBA)
T = (0, 0, 0, 0)  # Transparent

# Common bug colors
BLACK = (30, 30, 35, 255)
DARK = (50, 50, 55, 255)
BROWN = (100, 70, 50, 255)
BROWN_D = (70, 50, 35, 255)
BROWN_L = (140, 100, 70, 255)

# Bee colors
BEE_Y = (220, 180, 40, 255)   # Yellow stripes
BEE_B = (40, 35, 30, 255)      # Black stripes
BEE_W = (200, 210, 230, 180)   # Wings (semi-transparent)

# Butterfly colors
WING_O = (240, 140, 40, 255)   # Orange (monarch)
WING_B = (80, 120, 200, 255)   # Blue
WING_W = (240, 240, 250, 200)  # White
WING_D = (180, 100, 30, 255)   # Dark orange
BODY_B = (40, 40, 45, 255)     # Body black

# Moth colors
MOTH_B = (140, 130, 120, 255)  # Moth base (tan/gray)
MOTH_D = (100, 95, 90, 255)    # Moth dark
MOTH_L = (180, 175, 165, 255)  # Moth light

# Spider colors
SPIDER_B = (60, 50, 45, 255)   # Spider base
SPIDER_D = (40, 35, 30, 255)   # Spider dark
SPIDER_L = (90, 80, 70, 255)   # Spider light
SPIDER_E = (60, 20, 20, 255)   # Spider eyes (red-ish)

# Beetle colors
BEETLE_G = (50, 100, 50, 255)  # Green beetle
BEETLE_D = (30, 70, 30, 255)   # Dark green
BEETLE_L = (80, 130, 70, 255)  # Light green
STAG_B = (80, 50, 30, 255)     # Stag brown
STAG_D = (50, 35, 25, 255)     # Stag dark
STAG_L = (120, 80, 50, 255)    # Stag light

# Ant colors
ANT_B = (50, 40, 35, 255)      # Ant base
ANT_D = (30, 25, 22, 255)      # Ant dark
ANT_L = (80, 65, 55, 255)      # Ant light

# Eye colors
EYE = (200, 50, 50, 255)       # Red eyes
EYE_B = (20, 20, 25, 255)      # Black eyes

# Fly colors
FLY_B = (45, 45, 50, 255)      # Fly body
FLY_D = (30, 30, 35, 255)      # Fly dark
FLY_W = (180, 190, 210, 160)   # Fly wings (transparent)
FLY_E = (180, 40, 40, 255)     # Fly eyes (red)

# Ladybug colors
LADY_R = (200, 50, 40, 255)    # Red shell
LADY_D = (150, 35, 30, 255)    # Dark red
LADY_B = (30, 30, 35, 255)     # Black spots/head

# Firefly colors
FIRE_B = (50, 45, 40, 255)     # Body
FIRE_G = (180, 220, 80, 255)   # Glow (yellow-green)
FIRE_GL = (220, 250, 120, 255) # Glow light

# Wasp colors
WASP_Y = (230, 190, 40, 255)   # Yellow
WASP_B = (30, 30, 35, 255)     # Black
WASP_W = (180, 190, 200, 150)  # Wings

# Grasshopper/locust colors
GRASS_G = (70, 120, 50, 255)   # Green body
GRASS_D = (50, 90, 35, 255)    # Dark green
GRASS_L = (100, 150, 70, 255)  # Light green
GRASS_BR = (110, 80, 50, 255)  # Brown variant

# Cricket colors
CRICK_B = (60, 50, 40, 255)    # Brown body
CRICK_D = (40, 35, 30, 255)    # Dark
CRICK_L = (90, 75, 60, 255)    # Light

# Millipede/centipede colors
MILLI_BR = (80, 50, 40, 255)   # Brown
MILLI_D = (50, 35, 30, 255)    # Dark brown
MILLI_L = (110, 75, 55, 255)   # Light brown
MILLI_O = (180, 100, 40, 255)  # Orange legs (centipede)

# Scorpion colors
SCORP_B = (90, 70, 50, 255)    # Tan body
SCORP_D = (60, 45, 35, 255)    # Dark
SCORP_L = (130, 100, 70, 255)  # Light

# Dragonfly colors
DRAG_B = (60, 120, 160, 255)   # Blue body
DRAG_D = (40, 90, 130, 255)    # Dark blue
DRAG_L = (100, 160, 200, 255)  # Light blue
DRAG_W = (180, 200, 220, 140)  # Wings (transparent)

# Black widow colors
WIDOW_B = (25, 25, 30, 255)    # Black body
WIDOW_R = (200, 40, 40, 255)   # Red hourglass

# Tarantula colors
TARAN_B = (70, 55, 50, 255)    # Brown fuzzy
TARAN_D = (45, 35, 30, 255)    # Dark
TARAN_L = (100, 80, 70, 255)   # Light

# Cave spider colors
CAVE_B = (55, 55, 60, 255)     # Gray body
CAVE_D = (35, 35, 40, 255)     # Dark gray
CAVE_E = (140, 140, 160, 255)  # Pale eyes


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


# =============================================================================
# ANTS (8×8)
# =============================================================================

def build_ant_worker():
    """Worker ant: 8×8"""
    return [
        [T,      T,      ANT_D,  ANT_B,  ANT_B,  ANT_D,  T,      T     ],
        [T,      ANT_L,  ANT_B,  ANT_B,  ANT_B,  ANT_B,  ANT_D,  T     ],
        [ANT_L,  ANT_B,  T,      ANT_B,  ANT_B,  T,      ANT_B,  ANT_D ],
        [T,      T,      ANT_L,  ANT_B,  ANT_B,  ANT_D,  T,      T     ],
        [ANT_L,  ANT_B,  T,      ANT_B,  ANT_B,  T,      ANT_B,  ANT_D ],
        [T,      T,      ANT_L,  ANT_B,  ANT_B,  ANT_D,  T,      T     ],
        [ANT_L,  ANT_B,  T,      ANT_B,  ANT_B,  T,      ANT_B,  ANT_D ],
        [T,      T,      T,      ANT_B,  ANT_D,  T,      T,      T     ],
    ]


# =============================================================================
# BEES (10×10 - 12×12)
# =============================================================================

def build_honeybee():
    """Honeybee: 10×10"""
    grid = [[T] * 10 for _ in range(10)]
    # Wings (back)
    for x in range(2, 8):
        grid[1][x] = BEE_W
        grid[2][x] = BEE_W

    # Body (striped)
    for y in range(3, 9):
        for x in range(3, 7):
            stripe = (y - 3) % 2
            if stripe == 0:
                grid[y][x] = BEE_Y if x < 5 else BEE_B
            else:
                grid[y][x] = BEE_B if x < 5 else BEE_Y

    # Head
    grid[2][4] = BEE_B
    grid[2][5] = BEE_B

    # Stinger
    grid[9][4] = BEE_B
    grid[9][5] = BEE_B

    return grid


def build_bumblebee():
    """Bumblebee: 12×12 (fuzzier, rounder)"""
    grid = [[T] * 12 for _ in range(12)]

    # Wings
    for y in range(1, 4):
        for x in range(2, 10):
            grid[y][x] = BEE_W

    # Fuzzy body
    for y in range(4, 11):
        for x in range(3, 9):
            stripe = (y - 4) % 2
            c = BEE_Y if stripe == 0 else BEE_B
            grid[y][x] = c

    # Extra fluff (sides)
    for y in range(5, 10):
        grid[y][2] = BEE_Y if (y - 4) % 2 == 0 else BEE_B
        grid[y][9] = BEE_Y if (y - 4) % 2 == 0 else BEE_B

    # Head
    grid[3][5] = BEE_B
    grid[3][6] = BEE_B

    return grid


# =============================================================================
# BUTTERFLIES (16×16)
# =============================================================================

def build_butterfly_common():
    """Common butterfly: 16×16 (blue wings)"""
    grid = [[T] * 16 for _ in range(16)]

    # Left wing (upper)
    for y in range(2, 8):
        for x in range(1, 7):
            dist = abs(x - 4) + abs(y - 5)
            if dist < 5:
                grid[y][x] = WING_B if dist < 3 else WING_W

    # Right wing (upper)
    for y in range(2, 8):
        for x in range(9, 15):
            dist = abs(x - 11) + abs(y - 5)
            if dist < 5:
                grid[y][x] = WING_B if dist < 3 else WING_W

    # Left wing (lower)
    for y in range(8, 14):
        for x in range(2, 7):
            dist = abs(x - 4) + abs(y - 11)
            if dist < 4:
                grid[y][x] = WING_B if dist < 2 else WING_W

    # Right wing (lower)
    for y in range(8, 14):
        for x in range(9, 14):
            dist = abs(x - 11) + abs(y - 11)
            if dist < 4:
                grid[y][x] = WING_B if dist < 2 else WING_W

    # Body (center)
    for y in range(3, 14):
        grid[y][7] = BODY_B
        grid[y][8] = BODY_B

    # Antennae
    grid[1][6] = BODY_B
    grid[0][5] = BODY_B
    grid[1][9] = BODY_B
    grid[0][10] = BODY_B

    return grid


def build_butterfly_monarch():
    """Monarch butterfly: 16×16 (orange with black edges)"""
    grid = [[T] * 16 for _ in range(16)]

    # Wings (orange with black border)
    # Upper left
    for y in range(2, 8):
        for x in range(1, 7):
            dist = abs(x - 4) + abs(y - 5)
            if dist < 5:
                if dist >= 4:
                    grid[y][x] = BLACK
                else:
                    grid[y][x] = WING_O if dist < 3 else WING_D

    # Upper right
    for y in range(2, 8):
        for x in range(9, 15):
            dist = abs(x - 11) + abs(y - 5)
            if dist < 5:
                if dist >= 4:
                    grid[y][x] = BLACK
                else:
                    grid[y][x] = WING_O if dist < 3 else WING_D

    # Lower left
    for y in range(8, 14):
        for x in range(2, 7):
            dist = abs(x - 4) + abs(y - 11)
            if dist < 4:
                if dist >= 3:
                    grid[y][x] = BLACK
                else:
                    grid[y][x] = WING_O if dist < 2 else WING_D

    # Lower right
    for y in range(8, 14):
        for x in range(9, 14):
            dist = abs(x - 11) + abs(y - 11)
            if dist < 4:
                if dist >= 3:
                    grid[y][x] = BLACK
                else:
                    grid[y][x] = WING_O if dist < 2 else WING_D

    # White spots on wing edges
    grid[3][2] = WING_W
    grid[4][1] = WING_W
    grid[3][13] = WING_W
    grid[4][14] = WING_W

    # Body
    for y in range(3, 14):
        grid[y][7] = BODY_B
        grid[y][8] = BODY_B

    # Antennae
    grid[1][6] = BODY_B
    grid[0][5] = BODY_B
    grid[1][9] = BODY_B
    grid[0][10] = BODY_B

    return grid


# =============================================================================
# MOTHS (14×14)
# =============================================================================

def build_moth_common():
    """Common moth: 14×14 (tan/gray)"""
    grid = [[T] * 14 for _ in range(14)]

    # Wings (triangular shape)
    # Left wing
    for y in range(2, 10):
        width = 5 - abs(y - 6)
        for x in range(7 - width, 7):
            grid[y][x] = MOTH_B if x > 4 else MOTH_D

    # Right wing
    for y in range(2, 10):
        width = 5 - abs(y - 6)
        for x in range(7, 7 + width):
            grid[y][x] = MOTH_B if x < 9 else MOTH_L

    # Body
    for y in range(2, 12):
        grid[y][6] = MOTH_D
        grid[y][7] = MOTH_B

    # Fuzzy head
    grid[1][5] = MOTH_L
    grid[1][6] = MOTH_B
    grid[1][7] = MOTH_B
    grid[1][8] = MOTH_L

    # Antennae (feathery)
    grid[0][4] = MOTH_D
    grid[0][3] = MOTH_D
    grid[0][9] = MOTH_D
    grid[0][10] = MOTH_D

    return grid


# =============================================================================
# BEETLES (10×10 - 14×14)
# =============================================================================

def build_beetle_common():
    """Common beetle: 10×10"""
    grid = [[T] * 10 for _ in range(10)]

    # Shell (oval)
    for y in range(2, 9):
        for x in range(2, 8):
            dist = ((x - 5) ** 2 + (y - 5) ** 2) ** 0.5
            if dist < 3.5:
                if x < 5:
                    grid[y][x] = BEETLE_L if y < 5 else BEETLE_G
                else:
                    grid[y][x] = BEETLE_G if y < 5 else BEETLE_D

    # Wing line (center)
    for y in range(3, 8):
        grid[y][5] = BEETLE_D

    # Head
    grid[1][4] = BEETLE_D
    grid[1][5] = BEETLE_D
    grid[0][4] = BEETLE_D  # Antenna
    grid[0][5] = BEETLE_D

    # Legs
    grid[4][1] = BEETLE_D; grid[4][8] = BEETLE_D
    grid[6][1] = BEETLE_D; grid[6][8] = BEETLE_D

    return grid


def build_stag_beetle():
    """Stag beetle: 14×14 (with mandibles)"""
    grid = [[T] * 14 for _ in range(14)]

    # Mandibles (horns)
    grid[0][3] = STAG_D; grid[0][10] = STAG_D
    grid[1][2] = STAG_D; grid[1][3] = STAG_B; grid[1][10] = STAG_B; grid[1][11] = STAG_D
    grid[2][3] = STAG_B; grid[2][4] = STAG_B; grid[2][9] = STAG_B; grid[2][10] = STAG_B

    # Head
    for x in range(5, 9):
        grid[3][x] = STAG_B
        grid[4][x] = STAG_D if x > 6 else STAG_B

    # Body/shell
    for y in range(5, 13):
        for x in range(3, 11):
            dist = ((x - 7) ** 2 * 0.5 + (y - 9) ** 2) ** 0.5
            if dist < 4:
                if x < 7:
                    grid[y][x] = STAG_L if y < 9 else STAG_B
                else:
                    grid[y][x] = STAG_B if y < 9 else STAG_D

    # Wing seam
    for y in range(6, 12):
        grid[y][7] = STAG_D

    # Legs
    grid[7][2] = STAG_D; grid[7][11] = STAG_D
    grid[9][2] = STAG_D; grid[9][11] = STAG_D
    grid[11][3] = STAG_D; grid[11][10] = STAG_D

    return grid


# =============================================================================
# SPIDERS (16×16)
# =============================================================================

def build_wolf_spider():
    """Wolf spider: 16×16"""
    grid = [[T] * 16 for _ in range(16)]

    # Body (two segments)
    # Cephalothorax (front)
    for y in range(4, 9):
        for x in range(6, 10):
            dist = ((x - 8) ** 2 + (y - 6) ** 2) ** 0.5
            if dist < 2.5:
                grid[y][x] = SPIDER_L if x < 8 else SPIDER_B

    # Abdomen (back, larger)
    for y in range(7, 14):
        for x in range(4, 12):
            dist = ((x - 8) ** 2 + (y - 10) ** 2) ** 0.5
            if dist < 4:
                if x < 8:
                    grid[y][x] = SPIDER_L if y < 10 else SPIDER_B
                else:
                    grid[y][x] = SPIDER_B if y < 10 else SPIDER_D

    # Eyes (2 rows)
    grid[3][7] = SPIDER_E
    grid[3][8] = SPIDER_E
    grid[4][6] = EYE_B
    grid[4][9] = EYE_B

    # Legs (8 total, splayed out)
    # Front legs
    grid[4][3] = SPIDER_D; grid[3][2] = SPIDER_D; grid[2][1] = SPIDER_D
    grid[4][12] = SPIDER_D; grid[3][13] = SPIDER_D; grid[2][14] = SPIDER_D
    # Mid-front legs
    grid[6][2] = SPIDER_D; grid[5][1] = SPIDER_D
    grid[6][13] = SPIDER_D; grid[5][14] = SPIDER_D
    # Mid-back legs
    grid[9][2] = SPIDER_D; grid[10][1] = SPIDER_D
    grid[9][13] = SPIDER_D; grid[10][14] = SPIDER_D
    # Back legs
    grid[11][3] = SPIDER_D; grid[12][2] = SPIDER_D; grid[13][1] = SPIDER_D
    grid[11][12] = SPIDER_D; grid[12][13] = SPIDER_D; grid[13][14] = SPIDER_D

    return grid


def build_jumping_spider():
    """Jumping spider: 10×10 (cute, big eyes)"""
    grid = [[T] * 10 for _ in range(10)]

    # Body
    for y in range(3, 8):
        for x in range(3, 7):
            grid[y][x] = SPIDER_B

    # Big front eyes
    grid[2][3] = (200, 200, 220, 255)  # White
    grid[2][4] = EYE_B
    grid[2][5] = EYE_B
    grid[2][6] = (200, 200, 220, 255)

    # Legs (stubby)
    grid[4][1] = SPIDER_D; grid[4][8] = SPIDER_D
    grid[5][1] = SPIDER_D; grid[5][8] = SPIDER_D
    grid[6][2] = SPIDER_D; grid[6][7] = SPIDER_D
    grid[7][2] = SPIDER_D; grid[7][7] = SPIDER_D

    return grid


# =============================================================================
# ADDITIONAL BUGS
# =============================================================================

def build_fly_common():
    """Common fly: 8×8"""
    return [
        [T,      FLY_W,  T,      T,      T,      T,      FLY_W,  T     ],
        [FLY_W,  FLY_W,  FLY_E,  FLY_B,  FLY_B,  FLY_E,  FLY_W,  FLY_W ],
        [T,      FLY_W,  FLY_B,  FLY_B,  FLY_B,  FLY_B,  FLY_W,  T     ],
        [T,      T,      FLY_B,  FLY_B,  FLY_B,  FLY_B,  T,      T     ],
        [T,      T,      FLY_D,  FLY_B,  FLY_B,  FLY_D,  T,      T     ],
        [T,      FLY_D,  T,      FLY_B,  FLY_B,  T,      FLY_D,  T     ],
        [T,      T,      T,      FLY_D,  FLY_D,  T,      T,      T     ],
        [T,      T,      T,      T,      T,      T,      T,      T     ],
    ]


def build_ladybug():
    """Ladybug: 10×10"""
    grid = [[T] * 10 for _ in range(10)]

    # Head
    for x in range(3, 7):
        grid[1][x] = LADY_B
    grid[0][4] = LADY_B; grid[0][5] = LADY_B

    # Shell (oval)
    for y in range(2, 9):
        for x in range(2, 8):
            dist = ((x - 5) ** 2 + (y - 5) ** 2) ** 0.5
            if dist < 3.5:
                grid[y][x] = LADY_R if x < 5 else LADY_D

    # Wing line
    for y in range(2, 8):
        grid[y][5] = LADY_B

    # Spots
    grid[3][3] = LADY_B; grid[3][6] = LADY_B
    grid[5][3] = LADY_B; grid[5][7] = LADY_B
    grid[7][4] = LADY_B; grid[7][6] = LADY_B

    # Legs
    grid[4][1] = LADY_B; grid[4][8] = LADY_B
    grid[6][1] = LADY_B; grid[6][8] = LADY_B

    return grid


def build_firefly():
    """Firefly: 8×8 (with glowing tail)"""
    return [
        [T,      T,      FIRE_B, FIRE_B, T,      T,      T,      T     ],
        [T,      FIRE_B, FIRE_B, FIRE_B, FIRE_B, T,      T,      T     ],
        [FIRE_B, T,      FIRE_B, FIRE_B, T,      FIRE_B, T,      T     ],
        [T,      T,      FIRE_B, FIRE_B, T,      T,      T,      T     ],
        [FIRE_B, T,      FIRE_B, FIRE_B, T,      FIRE_B, T,      T     ],
        [T,      T,      FIRE_G, FIRE_G, T,      T,      T,      T     ],
        [T,      T,      FIRE_GL,FIRE_G, T,      T,      T,      T     ],
        [T,      T,      FIRE_G, FIRE_G, T,      T,      T,      T     ],
    ]


def build_wasp_common():
    """Common wasp: 12×12"""
    grid = [[T] * 12 for _ in range(12)]

    # Head
    grid[0][5] = WASP_B; grid[0][6] = WASP_B
    grid[1][4] = WASP_B; grid[1][5] = WASP_B; grid[1][6] = WASP_B; grid[1][7] = WASP_B

    # Thorax
    for y in range(2, 5):
        for x in range(4, 8):
            grid[y][x] = WASP_B

    # Wings
    grid[2][2] = WASP_W; grid[2][3] = WASP_W
    grid[2][8] = WASP_W; grid[2][9] = WASP_W
    grid[3][1] = WASP_W; grid[3][2] = WASP_W
    grid[3][9] = WASP_W; grid[3][10] = WASP_W

    # Narrow waist
    grid[5][5] = WASP_B; grid[5][6] = WASP_B

    # Abdomen (striped)
    for y in range(6, 11):
        for x in range(4, 8):
            if (y - 6) % 2 == 0:
                grid[y][x] = WASP_Y
            else:
                grid[y][x] = WASP_B

    # Stinger
    grid[11][5] = WASP_B; grid[11][6] = WASP_B

    # Legs
    grid[4][2] = WASP_B; grid[4][9] = WASP_B
    grid[6][3] = WASP_B; grid[6][8] = WASP_B
    grid[8][3] = WASP_B; grid[8][8] = WASP_B

    return grid


def build_hornet():
    """Hornet: 14×14 (larger wasp)"""
    grid = [[T] * 14 for _ in range(14)]

    # Head
    for x in range(5, 9):
        grid[0][x] = WASP_B
        grid[1][x] = WASP_B

    # Thorax
    for y in range(2, 6):
        for x in range(4, 10):
            grid[y][x] = WASP_B

    # Wings (larger)
    for y in range(2, 5):
        grid[y][2] = WASP_W; grid[y][3] = WASP_W
        grid[y][10] = WASP_W; grid[y][11] = WASP_W

    # Narrow waist
    grid[6][6] = WASP_B; grid[6][7] = WASP_B

    # Large abdomen (striped)
    for y in range(7, 13):
        for x in range(4, 10):
            if (y - 7) % 2 == 0:
                grid[y][x] = WASP_Y
            else:
                grid[y][x] = WASP_B

    # Stinger
    grid[13][6] = WASP_B; grid[13][7] = WASP_B

    # Legs
    grid[4][2] = WASP_B; grid[4][11] = WASP_B
    grid[8][3] = WASP_B; grid[8][10] = WASP_B
    grid[10][3] = WASP_B; grid[10][10] = WASP_B

    return grid


def build_locust():
    """Locust: 14×14 (brown grasshopper)"""
    grid = [[T] * 14 for _ in range(14)]

    # Head
    grid[0][5] = GRASS_BR; grid[0][6] = GRASS_BR
    grid[1][4] = GRASS_BR; grid[1][5] = GRASS_BR
    grid[1][6] = GRASS_BR; grid[1][7] = GRASS_BR

    # Eye
    grid[1][5] = EYE_B

    # Thorax
    for y in range(2, 6):
        for x in range(4, 9):
            grid[y][x] = GRASS_BR

    # Abdomen
    for y in range(6, 12):
        for x in range(5, 9):
            grid[y][x] = GRASS_BR if x < 7 else (110, 70, 45, 255)

    # Back legs (large, bent)
    grid[5][2] = GRASS_BR; grid[4][1] = GRASS_BR; grid[3][0] = GRASS_BR
    grid[5][11] = GRASS_BR; grid[4][12] = GRASS_BR; grid[3][13] = GRASS_BR
    grid[7][2] = GRASS_BR; grid[8][1] = GRASS_BR; grid[9][0] = GRASS_BR
    grid[7][11] = GRASS_BR; grid[8][12] = GRASS_BR; grid[9][13] = GRASS_BR

    # Front legs
    grid[4][3] = GRASS_BR; grid[4][10] = GRASS_BR

    return grid


def build_grasshopper():
    """Grasshopper: 14×14 (green)"""
    grid = [[T] * 14 for _ in range(14)]

    # Head
    grid[0][5] = GRASS_G; grid[0][6] = GRASS_G
    grid[1][4] = GRASS_L; grid[1][5] = GRASS_G
    grid[1][6] = GRASS_G; grid[1][7] = GRASS_D

    # Eye
    grid[1][5] = EYE_B

    # Thorax
    for y in range(2, 6):
        for x in range(4, 9):
            grid[y][x] = GRASS_L if x < 6 else GRASS_G

    # Abdomen
    for y in range(6, 12):
        for x in range(5, 9):
            grid[y][x] = GRASS_L if x < 7 else GRASS_D

    # Back legs (large, bent)
    grid[5][2] = GRASS_G; grid[4][1] = GRASS_G; grid[3][0] = GRASS_L
    grid[5][11] = GRASS_D; grid[4][12] = GRASS_D; grid[3][13] = GRASS_D
    grid[7][2] = GRASS_G; grid[8][1] = GRASS_G; grid[9][0] = GRASS_L
    grid[7][11] = GRASS_D; grid[8][12] = GRASS_D; grid[9][13] = GRASS_D

    # Front legs
    grid[4][3] = GRASS_G; grid[4][10] = GRASS_D

    return grid


def build_cricket():
    """Cricket: 12×12"""
    grid = [[T] * 12 for _ in range(12)]

    # Antennae
    grid[0][3] = CRICK_D; grid[0][8] = CRICK_D

    # Head
    for x in range(4, 8):
        grid[1][x] = CRICK_B
        grid[2][x] = CRICK_L if x < 6 else CRICK_D

    # Thorax
    for y in range(3, 6):
        for x in range(4, 8):
            grid[y][x] = CRICK_L if x < 6 else CRICK_B

    # Abdomen
    for y in range(6, 11):
        for x in range(4, 8):
            grid[y][x] = CRICK_B if x < 6 else CRICK_D

    # Back legs
    grid[5][2] = CRICK_D; grid[4][1] = CRICK_D
    grid[5][9] = CRICK_D; grid[4][10] = CRICK_D
    grid[7][2] = CRICK_D; grid[8][1] = CRICK_D
    grid[7][9] = CRICK_D; grid[8][10] = CRICK_D

    return grid


def build_millipede():
    """Millipede: 12×24 (many segments)"""
    grid = [[T] * 12 for _ in range(24)]

    # Head
    for x in range(4, 8):
        grid[0][x] = MILLI_L
        grid[1][x] = MILLI_BR

    # Antennae
    grid[0][3] = MILLI_D; grid[0][8] = MILLI_D

    # Body segments (many)
    for y in range(2, 22):
        # Body
        for x in range(4, 8):
            grid[y][x] = MILLI_L if x < 6 else MILLI_D

        # Legs (many pairs)
        if y % 2 == 0:
            grid[y][3] = MILLI_BR
            grid[y][8] = MILLI_BR

    # Tail
    grid[22][5] = MILLI_D; grid[22][6] = MILLI_D
    grid[23][5] = MILLI_D; grid[23][6] = MILLI_D

    return grid


def build_centipede():
    """Centipede: 10×20 (segmented, orange legs)"""
    grid = [[T] * 10 for _ in range(20)]

    # Head
    grid[0][3] = MILLI_D; grid[0][6] = MILLI_D  # Antennae
    for x in range(3, 7):
        grid[1][x] = MILLI_BR

    # Body segments
    for y in range(2, 18):
        for x in range(3, 7):
            grid[y][x] = MILLI_L if x < 5 else MILLI_D

        # Orange legs
        if y % 2 == 0:
            grid[y][1] = MILLI_O; grid[y][2] = MILLI_O
            grid[y][7] = MILLI_O; grid[y][8] = MILLI_O

    # Tail
    grid[18][4] = MILLI_D; grid[18][5] = MILLI_D
    grid[19][4] = MILLI_O; grid[19][5] = MILLI_O

    return grid


def build_scorpion():
    """Scorpion: 14×14"""
    grid = [[T] * 14 for _ in range(14)]

    # Pincers
    grid[0][2] = SCORP_B; grid[0][3] = SCORP_B
    grid[0][10] = SCORP_B; grid[0][11] = SCORP_B
    grid[1][1] = SCORP_L; grid[1][2] = SCORP_B; grid[1][3] = SCORP_D
    grid[1][10] = SCORP_L; grid[1][11] = SCORP_B; grid[1][12] = SCORP_D
    grid[2][2] = SCORP_B; grid[2][11] = SCORP_B

    # Head
    for x in range(5, 9):
        grid[3][x] = SCORP_L if x < 7 else SCORP_B

    # Body
    for y in range(4, 10):
        for x in range(4, 10):
            grid[y][x] = SCORP_L if x < 7 else SCORP_D

    # Tail (curved up)
    grid[8][6] = SCORP_B; grid[8][7] = SCORP_B
    grid[9][5] = SCORP_B; grid[9][6] = SCORP_B
    grid[10][4] = SCORP_B; grid[10][5] = SCORP_B
    grid[11][4] = SCORP_B
    grid[12][5] = SCORP_B  # Stinger
    grid[13][5] = SCORP_D

    # Legs
    grid[5][2] = SCORP_D; grid[5][11] = SCORP_D
    grid[6][2] = SCORP_D; grid[6][11] = SCORP_D
    grid[7][3] = SCORP_D; grid[7][10] = SCORP_D
    grid[8][3] = SCORP_D; grid[8][10] = SCORP_D

    return grid


def build_dragonfly():
    """Dragonfly: 16×20"""
    grid = [[T] * 16 for _ in range(20)]

    # Head (large eyes)
    grid[0][6] = DRAG_L; grid[0][7] = DRAG_B; grid[0][8] = DRAG_B; grid[0][9] = DRAG_D
    grid[1][5] = DRAG_L; grid[1][6] = DRAG_B; grid[1][9] = DRAG_B; grid[1][10] = DRAG_D

    # Thorax
    for y in range(2, 6):
        for x in range(6, 10):
            grid[y][x] = DRAG_L if x < 8 else DRAG_D

    # Wings (4, spread out)
    # Upper wings
    for y in range(2, 6):
        for x in range(1, 6):
            grid[y][x] = DRAG_W
        for x in range(10, 15):
            grid[y][x] = DRAG_W

    # Lower wings
    for y in range(5, 9):
        for x in range(2, 6):
            grid[y][x] = DRAG_W
        for x in range(10, 14):
            grid[y][x] = DRAG_W

    # Long abdomen
    for y in range(6, 19):
        grid[y][7] = DRAG_L
        grid[y][8] = DRAG_D

    # Tail
    grid[19][7] = DRAG_D; grid[19][8] = DRAG_D

    return grid


def build_black_widow():
    """Black widow: 14×14"""
    grid = [[T] * 14 for _ in range(14)]

    # Cephalothorax (front)
    for y in range(2, 6):
        for x in range(5, 9):
            grid[y][x] = WIDOW_B

    # Large round abdomen
    for y in range(5, 13):
        for x in range(3, 11):
            dist = ((x - 7) ** 2 + (y - 9) ** 2) ** 0.5
            if dist < 4:
                grid[y][x] = WIDOW_B

    # Red hourglass
    grid[8][6] = WIDOW_R; grid[8][7] = WIDOW_R
    grid[9][7] = WIDOW_R
    grid[10][6] = WIDOW_R; grid[10][7] = WIDOW_R

    # Legs (8, thin and long)
    grid[3][2] = WIDOW_B; grid[2][1] = WIDOW_B; grid[1][0] = WIDOW_B
    grid[3][11] = WIDOW_B; grid[2][12] = WIDOW_B; grid[1][13] = WIDOW_B
    grid[5][1] = WIDOW_B; grid[4][0] = WIDOW_B
    grid[5][12] = WIDOW_B; grid[4][13] = WIDOW_B
    grid[8][1] = WIDOW_B; grid[9][0] = WIDOW_B
    grid[8][12] = WIDOW_B; grid[9][13] = WIDOW_B
    grid[10][2] = WIDOW_B; grid[11][1] = WIDOW_B
    grid[10][11] = WIDOW_B; grid[11][12] = WIDOW_B

    return grid


def build_tarantula():
    """Tarantula: 24×24 (large, fuzzy)"""
    grid = [[T] * 24 for _ in range(24)]

    # Cephalothorax
    for y in range(6, 12):
        for x in range(8, 16):
            dist = ((x - 12) ** 2 + (y - 9) ** 2) ** 0.5
            if dist < 4:
                grid[y][x] = TARAN_L if x < 12 else TARAN_B

    # Large abdomen
    for y in range(10, 20):
        for x in range(6, 18):
            dist = ((x - 12) ** 2 + (y - 15) ** 2) ** 0.5
            if dist < 6:
                grid[y][x] = TARAN_L if x < 12 else TARAN_D

    # Eyes (cluster)
    grid[5][10] = EYE_B; grid[5][11] = EYE_B
    grid[5][12] = EYE_B; grid[5][13] = EYE_B

    # Legs (8, thick and hairy)
    for i in range(4):
        # Left legs
        grid[7 + i][6 - i] = TARAN_B
        grid[8 + i][5 - i] = TARAN_B
        grid[7 + i][4 - i] = TARAN_D if i > 1 else TARAN_B
        # Right legs
        grid[7 + i][17 + i] = TARAN_B
        grid[8 + i][18 + i] = TARAN_B
        grid[7 + i][19 + i] = TARAN_D if i > 1 else TARAN_B

    # Back legs
    for i in range(4):
        grid[12 + i][4 - i] = TARAN_B
        grid[13 + i][3 - i] = TARAN_D
        grid[12 + i][19 + i] = TARAN_B
        grid[13 + i][20 + i] = TARAN_D

    return grid


def build_giant_centipede():
    """Giant centipede: 16×32 (boss creature)"""
    grid = [[T] * 16 for _ in range(32)]

    # Head
    for x in range(5, 11):
        grid[0][x] = MILLI_L
        grid[1][x] = MILLI_BR

    # Mandibles
    grid[0][4] = MILLI_O; grid[0][11] = MILLI_O

    # Eyes
    grid[1][6] = EYE; grid[1][9] = EYE

    # Body segments (armored)
    for y in range(2, 30):
        for x in range(4, 12):
            if (y - 2) % 2 == 0:
                grid[y][x] = MILLI_L if x < 8 else MILLI_BR
            else:
                grid[y][x] = MILLI_BR if x < 8 else MILLI_D

        # Many legs (orange)
        if y % 2 == 0:
            grid[y][2] = MILLI_O; grid[y][3] = MILLI_O
            grid[y][12] = MILLI_O; grid[y][13] = MILLI_O

    # Tail segments
    grid[30][6] = MILLI_D; grid[30][7] = MILLI_D; grid[30][8] = MILLI_D; grid[30][9] = MILLI_D
    grid[31][7] = MILLI_O; grid[31][8] = MILLI_O

    return grid


def build_cave_spider():
    """Cave spider: 12×12 (pale, adapted to darkness)"""
    grid = [[T] * 12 for _ in range(12)]

    # Cephalothorax
    for y in range(2, 6):
        for x in range(4, 8):
            grid[y][x] = CAVE_B

    # Abdomen
    for y in range(5, 10):
        for x in range(3, 9):
            dist = ((x - 6) ** 2 + (y - 7) ** 2) ** 0.5
            if dist < 3:
                grid[y][x] = CAVE_B if x < 6 else CAVE_D

    # Pale eyes
    grid[2][4] = CAVE_E; grid[2][5] = CAVE_E
    grid[2][6] = CAVE_E; grid[2][7] = CAVE_E

    # Long thin legs
    grid[3][1] = CAVE_D; grid[2][0] = CAVE_D
    grid[3][10] = CAVE_D; grid[2][11] = CAVE_D
    grid[5][1] = CAVE_D; grid[4][0] = CAVE_D
    grid[5][10] = CAVE_D; grid[4][11] = CAVE_D
    grid[7][1] = CAVE_D; grid[8][0] = CAVE_D
    grid[7][10] = CAVE_D; grid[8][11] = CAVE_D
    grid[8][2] = CAVE_D; grid[9][1] = CAVE_D
    grid[8][9] = CAVE_D; grid[9][10] = CAVE_D

    return grid


def build_ant_queen():
    """Ant queen: 32×32 (large ant with wings)"""
    grid = [[T] * 32 for _ in range(32)]

    # Head (large)
    for y in range(2, 8):
        for x in range(12, 20):
            dist = ((x - 16) ** 2 + (y - 5) ** 2) ** 0.5
            if dist < 4:
                grid[y][x] = ANT_L if x < 16 else ANT_B

    # Antennae
    grid[0][12] = ANT_D; grid[1][11] = ANT_D
    grid[0][19] = ANT_D; grid[1][20] = ANT_D

    # Eyes
    grid[4][13] = EYE_B; grid[4][18] = EYE_B

    # Thorax
    for y in range(8, 14):
        for x in range(10, 22):
            grid[y][x] = ANT_L if x < 16 else ANT_B

    # Wings (translucent, folded)
    wing_color = (180, 180, 200, 120)
    for y in range(6, 14):
        for x in range(4, 10):
            grid[y][x] = wing_color
        for x in range(22, 28):
            grid[y][x] = wing_color

    # Narrow waist
    for y in range(14, 17):
        grid[y][15] = ANT_B; grid[y][16] = ANT_B

    # Large abdomen
    for y in range(17, 30):
        for x in range(8, 24):
            dist = ((x - 16) ** 2 * 0.5 + (y - 23) ** 2) ** 0.5
            if dist < 7:
                grid[y][x] = ANT_L if x < 16 else ANT_D

    # Legs
    grid[10][6] = ANT_D; grid[11][5] = ANT_D
    grid[10][25] = ANT_D; grid[11][26] = ANT_D
    grid[12][7] = ANT_D; grid[13][6] = ANT_D
    grid[12][24] = ANT_D; grid[13][25] = ANT_D
    grid[19][7] = ANT_D; grid[20][6] = ANT_D
    grid[19][24] = ANT_D; grid[20][25] = ANT_D

    return grid


def main():
    output_dir = "/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Sprites/Bugs"
    os.makedirs(output_dir, exist_ok=True)

    sprites = [
        # Ants
        ("ant_worker.png", build_ant_worker()),
        ("ant_queen.png", build_ant_queen()),
        # Bees
        ("honeybee.png", build_honeybee()),
        ("bumblebee.png", build_bumblebee()),
        # Wasps
        ("wasp_common.png", build_wasp_common()),
        ("hornet.png", build_hornet()),
        # Butterflies
        ("butterfly_common.png", build_butterfly_common()),
        ("butterfly_monarch.png", build_butterfly_monarch()),
        # Moths
        ("moth_common.png", build_moth_common()),
        # Beetles
        ("beetle_common.png", build_beetle_common()),
        ("stag_beetle.png", build_stag_beetle()),
        ("ladybug.png", build_ladybug()),
        # Flies
        ("fly_common.png", build_fly_common()),
        ("firefly.png", build_firefly()),
        ("dragonfly.png", build_dragonfly()),
        # Grasshoppers/Crickets
        ("grasshopper.png", build_grasshopper()),
        ("locust.png", build_locust()),
        ("cricket.png", build_cricket()),
        # Multi-legged
        ("millipede.png", build_millipede()),
        ("centipede.png", build_centipede()),
        ("giant_centipede.png", build_giant_centipede()),
        # Spiders
        ("wolf_spider.png", build_wolf_spider()),
        ("jumping_spider.png", build_jumping_spider()),
        ("black_widow.png", build_black_widow()),
        ("tarantula.png", build_tarantula()),
        ("cave_spider.png", build_cave_spider()),
        # Arachnids
        ("scorpion.png", build_scorpion()),
    ]

    for filename, grid in sprites:
        img = create_sprite_from_grid(grid)
        path = f"{output_dir}/{filename}"
        img.save(path)
        print(f"Created: {path} ({img.size[0]}x{img.size[1]})")

    print("\nUnity import settings:")
    print("  - Pixels Per Unit: 16 (or 8 for small bugs)")
    print("  - Filter Mode: Point (no filter)")
    print("  - Compression: None")


if __name__ == "__main__":
    main()
