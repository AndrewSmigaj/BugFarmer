#!/usr/bin/env python3
"""Generate furniture and crafting station sprites for Bug Farmer.

Design principles:
- 45-degree top-down perspective
- Light source: top-left
- Show TOP surface of furniture (table tops, etc.)
- Vertical objects slightly foreshortened

Includes:
- Crafting stations: workbench, furnace, anvil, forge
- Furniture: tables, chairs, beds, bookshelves, lamps
"""

from PIL import Image
import os

# Colors (RGBA)
T = (0, 0, 0, 0)  # Transparent

# Wood - from SPRITE_GENERATION_GUIDE.md
Wd = (70, 50, 35, 255)     # Wood dark
W  = (120, 90, 60, 255)    # Wood base
Wl = (160, 130, 95, 255)   # Wood light

# Stone
Sd = (85, 85, 90, 255)     # Stone dark
S  = (120, 120, 125, 255)  # Stone base
Sl = (155, 155, 160, 255)  # Stone light

# Metal (Iron)
Md = (60, 65, 70, 255)     # Metal dark
M  = (100, 105, 110, 255)  # Metal base
Ml = (150, 155, 160, 255)  # Metal light

# Fire/Glow
Fd = (180, 60, 20, 255)    # Fire dark
F  = (230, 120, 40, 255)   # Fire base
Fl = (255, 200, 80, 255)   # Fire light/glow

# Fabric (bed)
Bd = (100, 70, 100, 255)   # Blanket dark (purple-ish)
B  = (140, 100, 140, 255)  # Blanket base
Bl = (180, 140, 180, 255)  # Blanket light

# Pillow (white-ish)
Pd = (180, 180, 175, 255)  # Pillow dark
P  = (220, 220, 215, 255)  # Pillow base
Pl = (245, 245, 240, 255)  # Pillow light

# Lamp glow
Ld = (200, 180, 100, 255)  # Lamp dark
L  = (240, 220, 140, 255)  # Lamp base
Ll = (255, 250, 200, 255)  # Lamp light


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
# CRAFTING STATIONS
# =============================================================================

def build_workbench():
    """Workbench: 32x20 (2x1 footprint) - 3/4 perspective work surface

    Structure:
    - Top surface: HORIZONTAL plane (left-right shading)
    - Front apron: VERTICAL plane (darker)
    - Legs with support shelf
    """
    grid = [[T] * 32 for _ in range(20)]

    # === TOP SURFACE (horizontal, viewed from above) ===
    for y in range(6):
        for x in range(32):
            if x < 10:
                grid[y][x] = Wl  # Left - lit
            elif x < 22:
                grid[y][x] = W   # Center - base
            else:
                grid[y][x] = Wd  # Right - shadow

    # Top edge highlight
    for x in range(32):
        grid[0][x] = Wl

    # === FRONT APRON (vertical, darker) ===
    for y in range(6, 10):
        for x in range(32):
            if x < 10:
                grid[y][x] = W
            else:
                grid[y][x] = Wd

    # Edge line
    for x in range(32):
        grid[6][x] = Wd

    # === LEGS (4 corners) ===
    for y in range(10, 20):
        # Front left leg
        grid[y][2] = W; grid[y][3] = W; grid[y][4] = Wd
        # Front right leg
        grid[y][27] = W; grid[y][28] = Wd; grid[y][29] = Wd
        # Back legs (partially visible)
        if y < 16:
            grid[y][6] = W; grid[y][7] = Wd
            grid[y][24] = W; grid[y][25] = Wd

    # Shelf/support bar
    for x in range(4, 28):
        grid[14][x] = Wd

    return grid


def build_furnace():
    """Furnace: 32x28 (2x2 footprint) - stone smelting oven"""
    grid = [[T] * 32 for _ in range(28)]

    # Main body (stone block)
    for y in range(24):
        for x in range(4, 28):
            diag = (x - 16) + (y - 12)
            if diag < -10:
                grid[y][x] = Sl
            elif diag < 8:
                grid[y][x] = S
            else:
                grid[y][x] = Sd

    # Top opening (darker)
    for y in range(2, 6):
        for x in range(10, 22):
            grid[y][x] = Sd

    # Front opening (fire visible)
    for y in range(12, 20):
        for x in range(12, 20):
            # Fire glow inside
            if y < 14 or y > 18:
                grid[y][x] = Sd
            elif x < 14 or x > 17:
                grid[y][x] = Sd
            else:
                diag = (x - 16) + (y - 16)
                if diag < -1:
                    grid[y][x] = Fl
                elif diag < 1:
                    grid[y][x] = F
                else:
                    grid[y][x] = Fd

    # Base (darker stone)
    for x in range(4, 28):
        grid[24][x] = Sd
        grid[25][x] = Sd
        grid[26][x] = Sd
        grid[27][x] = Sd

    return grid


def build_anvil():
    """Anvil: 32x20 (2x1 footprint) - metal anvil on wood base"""
    grid = [[T] * 32 for _ in range(20)]

    # Anvil top (horn shape - wider on left, tapers right)
    # Left horn
    for x in range(4, 10):
        grid[2][x] = Ml if x < 7 else M
        grid[3][x] = M if x < 7 else Md
    # Main face
    for y in range(1, 6):
        for x in range(10, 24):
            diag = (x - 17) + (y - 3)
            if diag < -5:
                grid[y][x] = Ml
            elif diag < 3:
                grid[y][x] = M
            else:
                grid[y][x] = Md
    # Right horn (short)
    for x in range(24, 28):
        grid[2][x] = M if x < 26 else Md
        grid[3][x] = M if x < 26 else Md

    # Body
    for y in range(6, 12):
        for x in range(11, 23):
            grid[y][x] = M if x < 17 else Md

    # Base (wood)
    for y in range(12, 20):
        for x in range(8, 26):
            diag = (x - 17) + (y - 16)
            if diag < -6:
                grid[y][x] = Wl
            elif diag < 4:
                grid[y][x] = W
            else:
                grid[y][x] = Wd

    return grid


def build_forge():
    """Forge: 32x32 (2x2 footprint) - advanced furnace with bellows"""
    grid = [[T] * 32 for _ in range(32)]

    # Main furnace body (larger than regular furnace)
    for y in range(4, 28):
        for x in range(4, 26):
            diag = (x - 15) + (y - 16)
            if diag < -12:
                grid[y][x] = Sl
            elif diag < 6:
                grid[y][x] = S
            else:
                grid[y][x] = Sd

    # Fire pit (top-center)
    for y in range(6, 12):
        for x in range(10, 20):
            if y < 7 or y > 10 or x < 11 or x > 18:
                grid[y][x] = Sd
            else:
                diag = (x - 15) + (y - 9)
                if diag < -2:
                    grid[y][x] = Fl
                elif diag < 2:
                    grid[y][x] = F
                else:
                    grid[y][x] = Fd

    # Chimney (back)
    for y in range(0, 6):
        for x in range(12, 18):
            grid[y][x] = Sd if x > 15 else S

    # Bellows (right side)
    for y in range(16, 24):
        for x in range(26, 32):
            grid[y][x] = Wd if y > 20 else W

    # Base
    for y in range(28, 32):
        for x in range(2, 28):
            grid[y][x] = Sd

    return grid


def build_loom():
    """Loom: 32x28 (2x2 footprint) - weaving loom for crafting fabric

    3/4 perspective structure:
    - Top crossbar: HORIZONTAL surface (viewed from above)
    - Frame sides: VERTICAL surfaces (darker)
    - Warp threads: visible hanging vertically
    - Woven fabric: at bottom, shows progress
    """
    grid = [[T] * 32 for _ in range(28)]

    # Thread color
    Thread = (200, 190, 170, 255)

    # === TOP CROSSBAR (horizontal surface) ===
    for y in range(0, 3):
        for x in range(4, 28):
            if x < 12:
                grid[y][x] = Wl  # Left - lit
            elif x < 20:
                grid[y][x] = W   # Center
            else:
                grid[y][x] = Wd  # Right - shadow

    # Top edge highlight
    for x in range(4, 28):
        grid[0][x] = Wl

    # === FRAME SIDES (vertical surfaces, darker) ===
    # Left upright
    for y in range(3, 28):
        grid[y][4] = W
        grid[y][5] = W
        grid[y][6] = Wd

    # Right upright
    for y in range(3, 28):
        grid[y][25] = W
        grid[y][26] = Wd
        grid[y][27] = Wd

    # Edge between top and uprights
    grid[3][4] = Wd; grid[3][5] = Wd; grid[3][6] = Wd
    grid[3][25] = Wd; grid[3][26] = Wd; grid[3][27] = Wd

    # === HEDDLE BAR (horizontal, middle) ===
    for y in range(11, 13):
        for x in range(7, 25):
            if x < 13:
                grid[y][x] = Wl
            elif x < 19:
                grid[y][x] = W
            else:
                grid[y][x] = Wd

    # === WARP THREADS (vertical lines) ===
    for x in range(9, 23, 2):
        for y in range(3, 11):
            grid[y][x] = Thread
        for y in range(13, 18):
            grid[y][x] = Thread

    # === WOVEN FABRIC (horizontal surface at bottom, shows progress) ===
    fabric_d = (100, 75, 55, 255)
    fabric = (130, 100, 80, 255)
    fabric_l = (160, 130, 100, 255)

    for y in range(18, 26):
        for x in range(8, 24):
            # Weave pattern with left-right shading
            if x < 13:
                grid[y][x] = fabric_l
            elif x < 18:
                grid[y][x] = fabric
            else:
                grid[y][x] = fabric_d

    # Edge line at top of fabric
    for x in range(8, 24):
        grid[18][x] = fabric_d

    return grid


def build_cooking_pot():
    """Cooking pot: 32x20 (2x1 footprint) - pot over fire for cooking

    3/4 perspective structure:
    - Pot opening: HORIZONTAL (viewed from above, see inside)
    - Pot body: curves away, darker front face
    - Tripod legs: vertical, darker
    - Fire underneath: visible glow
    """
    grid = [[T] * 32 for _ in range(20)]

    # Pot colors (cast iron)
    Pd = (50, 45, 40, 255)   # Pot dark
    P  = (70, 65, 60, 255)   # Pot base
    Pl = (95, 90, 85, 255)   # Pot light

    # Contents (stew color)
    stew_d = (120, 70, 50, 255)
    stew = (150, 95, 65, 255)
    stew_l = (175, 115, 85, 255)

    # === POT OPENING/TOP (horizontal, viewed from above) ===
    # Rim
    for y in range(0, 2):
        for x in range(8, 24):
            if x < 13:
                grid[y][x] = Pl  # Left - lit
            elif x < 19:
                grid[y][x] = P   # Center
            else:
                grid[y][x] = Pd  # Right - shadow

    # Top edge highlight
    for x in range(8, 24):
        grid[0][x] = Pl

    # Contents visible inside
    for y in range(2, 5):
        for x in range(9, 23):
            if x < 14:
                grid[y][x] = stew_l
            elif x < 18:
                grid[y][x] = stew
            else:
                grid[y][x] = stew_d

    # === POT BODY FRONT (vertical surface, darker) ===
    for y in range(5, 12):
        for x in range(7, 25):
            if x < 12:
                grid[y][x] = P   # Left side - less dark
            elif x < 20:
                grid[y][x] = Pd  # Center - dark
            else:
                grid[y][x] = Pd  # Right - dark

    # Edge between top and front
    for x in range(7, 25):
        grid[5][x] = Pd

    # Handles on sides
    grid[3][6] = P; grid[4][5] = P
    grid[3][25] = Pd; grid[4][26] = Pd

    # === TRIPOD LEGS (vertical, darker) ===
    for y in range(12, 20):
        # Left leg (angled)
        lx = 8 + (y - 12) // 2
        if lx < 32:
            grid[y][lx] = Md
        # Right leg (angled)
        rx = 23 - (y - 12) // 2
        if rx >= 0:
            grid[y][rx] = Md

    # === FIRE (visible underneath) ===
    for y in range(14, 20):
        for x in range(11, 21):
            if y < 17:
                diag = (x - 16) + (y - 15)
                if diag < -2:
                    grid[y][x] = Fl
                elif diag < 1:
                    grid[y][x] = F
                else:
                    grid[y][x] = Fd

    return grid


def build_cauldron():
    """Cauldron: 32x28 (2x2 footprint) - large magical brewing cauldron

    3/4 perspective structure:
    - Opening: HORIZONTAL (viewed from above, bubbling liquid visible)
    - Body: large round, front face darker
    - Ornate rim and legs
    """
    grid = [[T] * 32 for _ in range(28)]

    # Cauldron metal (dark magical looking)
    Cd = (35, 30, 40, 255)   # Dark
    C  = (55, 50, 60, 255)   # Base
    Cl = (80, 75, 85, 255)   # Light

    # Potion colors (green)
    potion_d = (30, 80, 50, 255)
    potion = (50, 120, 70, 255)
    potion_l = (80, 160, 100, 255)

    # === RIM (horizontal surface at top) ===
    for y in range(0, 3):
        for x in range(6, 26):
            if x < 12:
                grid[y][x] = Cl  # Left - lit
            elif x < 20:
                grid[y][x] = C   # Center
            else:
                grid[y][x] = Cd  # Right - shadow

    # Top edge highlight
    for x in range(6, 26):
        grid[0][x] = Cl

    # === BUBBLING POTION (horizontal, inside) ===
    for y in range(3, 8):
        for x in range(8, 24):
            if x < 13:
                grid[y][x] = potion_l
            elif x < 19:
                grid[y][x] = potion
            else:
                grid[y][x] = potion_d

    # Bubbles
    grid[4][11] = potion_l; grid[5][17] = potion_l; grid[6][14] = potion_l

    # === CAULDRON BODY (vertical front face, darker) ===
    for y in range(8, 24):
        # Bulbous shape
        if y < 12:
            start_x, end_x = 6, 26
        elif y < 18:
            start_x, end_x = 4, 28
        else:
            start_x, end_x = 6, 26

        for x in range(start_x, end_x):
            if x < 12:
                grid[y][x] = C   # Left - less dark
            elif x < 20:
                grid[y][x] = Cd  # Center - dark
            else:
                grid[y][x] = Cd  # Right - dark

    # Edge between rim and body
    for x in range(6, 26):
        grid[8][x] = Cd

    # Decorative band
    for x in range(5, 27):
        grid[14][x] = Cl if x < 16 else Cd

    # === LEGS (three ornate feet) ===
    for y in range(24, 28):
        # Left leg
        grid[y][8] = C; grid[y][9] = Cd
        # Center leg
        grid[y][15] = C; grid[y][16] = Cd
        # Right leg
        grid[y][22] = C; grid[y][23] = Cd

    return grid


def build_sawmill():
    """Sawmill: 48x28 (3x2 footprint) - wood processing station

    3/4 perspective structure:
    - Work table top: HORIZONTAL surface (viewed from above)
    - Saw blade: circular, angled to show teeth
    - Housing: front face darker
    - Log on table
    """
    grid = [[T] * 48 for _ in range(28)]

    # === HOUSING/FRAME (back portion) ===
    # Top surface
    for y in range(0, 6):
        for x in range(0, 24):
            if x < 8:
                grid[y][x] = Wl  # Left - lit
            elif x < 16:
                grid[y][x] = W   # Center
            else:
                grid[y][x] = Wd  # Right - shadow

    # Top edge highlight
    for x in range(0, 24):
        grid[0][x] = Wl

    # Front face (vertical, darker)
    for y in range(6, 20):
        for x in range(0, 24):
            if x < 8:
                grid[y][x] = W   # Left - less dark
            else:
                grid[y][x] = Wd  # Right - dark

    # Edge between top and front
    for x in range(0, 24):
        grid[6][x] = Wd

    # === SAW BLADE (circular) ===
    blade_cx, blade_cy = 12, 10
    blade_radius = 7

    for y in range(28):
        for x in range(48):
            dx = x - blade_cx
            dy = y - blade_cy
            dist = (dx * dx + dy * dy) ** 0.5

            if dist <= blade_radius:
                if dist > blade_radius - 1.5:
                    # Teeth at edge (alternating)
                    if int(dx + dy) % 2 == 0:
                        grid[y][x] = Ml
                    else:
                        grid[y][x] = Md
                elif dist > 1.5:
                    # Inner blade with shading
                    if dx + dy < 0:
                        grid[y][x] = Ml
                    else:
                        grid[y][x] = M
                else:
                    # Center hub
                    grid[y][x] = Md

    # === WORK TABLE (horizontal surface) ===
    for y in range(12, 18):
        for x in range(22, 48):
            if x < 30:
                grid[y][x] = Wl  # Left - lit
            elif x < 40:
                grid[y][x] = W   # Center
            else:
                grid[y][x] = Wd  # Right - shadow

    # Top edge highlight
    for x in range(22, 48):
        grid[12][x] = Wl

    # Table front (vertical, darker)
    for y in range(18, 28):
        for x in range(22, 48):
            if x < 30:
                grid[y][x] = W
            else:
                grid[y][x] = Wd

    # Edge between top and front
    for x in range(22, 48):
        grid[18][x] = Wd

    # === LOG ON TABLE ===
    log_d = (90, 60, 40, 255)
    log = (130, 90, 60, 255)
    log_l = (160, 120, 85, 255)

    for y in range(14, 17):
        for x in range(28, 46):
            if x < 34:
                grid[y][x] = log_l
            elif x < 40:
                grid[y][x] = log
            else:
                grid[y][x] = log_d

    # === LEGS ===
    for y in range(20, 28):
        grid[y][2] = W; grid[y][3] = Wd
        grid[y][20] = W; grid[y][21] = Wd
        grid[y][44] = W; grid[y][45] = Wd

    return grid


def build_stonecutter():
    """Stonecutter: 32x28 (2x2 footprint) - stone processing station

    3/4 perspective structure:
    - Work surface: HORIZONTAL (viewed from above, stone slab on top)
    - Base: front face darker
    - Tools visible: chisel and hammer
    """
    grid = [[T] * 32 for _ in range(28)]

    # Stone block being worked (on top of work surface)
    block_d = (80, 75, 70, 255)
    block = (110, 105, 100, 255)
    block_l = (140, 135, 130, 255)

    # === STONE BLOCK ON TOP ===
    for y in range(0, 6):
        for x in range(8, 24):
            if x < 13:
                grid[y][x] = block_l  # Left - lit
            elif x < 19:
                grid[y][x] = block    # Center
            else:
                grid[y][x] = block_d  # Right - shadow

    # Top edge highlight
    for x in range(8, 24):
        grid[0][x] = block_l

    # Chisel marks
    grid[2][15] = block_d
    grid[3][14] = block_d
    grid[4][16] = block_d

    # === WORK SURFACE (horizontal) ===
    for y in range(6, 12):
        for x in range(2, 30):
            if x < 10:
                grid[y][x] = Sl  # Left - lit
            elif x < 22:
                grid[y][x] = S   # Center
            else:
                grid[y][x] = Sd  # Right - shadow

    # Top edge highlight
    for x in range(2, 30):
        grid[6][x] = Sl

    # === BASE (vertical front, darker) ===
    for y in range(12, 28):
        for x in range(2, 30):
            if x < 10:
                grid[y][x] = S   # Left - less dark
            elif x < 22:
                grid[y][x] = Sd  # Center - dark
            else:
                grid[y][x] = Sd  # Right - dark

    # Edge between work surface and base
    for x in range(2, 30):
        grid[12][x] = Sd

    # Mortar lines on base
    mortar = (70, 70, 75, 255)
    for y in [16, 22]:
        for x in range(2, 30):
            grid[y][x] = mortar

    # === TOOLS (on work surface) ===
    # Chisel (left side)
    for y in range(7, 11):
        grid[y][4] = Ml
        grid[y][5] = M

    # Hammer (right side)
    for x in range(25, 29):
        grid[8][x] = Wd
        grid[9][x] = W
    for y in range(10, 14):
        if y < 12:
            grid[y][26] = W
            grid[y][27] = Wd

    return grid


# =============================================================================
# FURNITURE
# =============================================================================

def build_table_wood():
    """Wooden table: 32x24 (2x2 footprint) - 3/4 perspective

    Structure:
    - Top surface: HORIZONTAL plane, viewed from above (left-right shading)
    - Front apron: VERTICAL plane, darker (shows depth)
    - Legs: visible below
    """
    grid = [[T] * 32 for _ in range(24)]

    # === TABLE TOP (horizontal surface, viewed from above) ===
    # Left side lit, right side shadowed
    for y in range(8):
        for x in range(32):
            if x < 10:
                grid[y][x] = Wl  # Left - lit
            elif x < 22:
                grid[y][x] = W   # Center - base
            else:
                grid[y][x] = Wd  # Right - shadow

    # Top edge highlight
    for x in range(32):
        grid[0][x] = Wl

    # === FRONT APRON (vertical surface, darker) ===
    for y in range(8, 12):
        for x in range(32):
            if x < 10:
                grid[y][x] = W   # Left - less dark
            elif x < 22:
                grid[y][x] = Wd  # Center - dark
            else:
                grid[y][x] = Wd  # Right - dark

    # Edge line between top and apron
    for x in range(32):
        grid[8][x] = Wd

    # === LEGS (four corners) ===
    for y in range(12, 24):
        # Front left leg
        grid[y][2] = W; grid[y][3] = W; grid[y][4] = Wd
        # Front right leg
        grid[y][27] = W; grid[y][28] = Wd; grid[y][29] = Wd
        # Back left leg (partially visible)
        if y < 18:
            grid[y][6] = W; grid[y][7] = Wd
        # Back right leg (partially visible)
        if y < 18:
            grid[y][24] = W; grid[y][25] = Wd

    return grid


def build_chair_wood():
    """Wooden chair: 16x20 (1x1 footprint) - 3/4 perspective

    Structure:
    - Back: VERTICAL surface (we see its front face, left-right shading)
    - Seat: HORIZONTAL surface (viewed from above)
    - Legs: visible below
    """
    grid = [[T] * 16 for _ in range(20)]

    # === CHAIR BACK (vertical front face) ===
    for y in range(0, 8):
        for x in range(4, 12):
            if x < 6:
                grid[y][x] = Wl  # Left - lit
            elif x < 10:
                grid[y][x] = W   # Center - base
            else:
                grid[y][x] = Wd  # Right - shadow

    # Top edge of back
    for x in range(4, 12):
        grid[0][x] = Wl

    # === SEAT (horizontal surface, viewed from above) ===
    for y in range(8, 12):
        for x in range(2, 14):
            if x < 6:
                grid[y][x] = Wl  # Left - lit
            elif x < 10:
                grid[y][x] = W   # Center - base
            else:
                grid[y][x] = Wd  # Right - shadow

    # Front edge of seat (shows thickness)
    for x in range(2, 14):
        grid[12][x] = Wd

    # === LEGS ===
    for y in range(13, 20):
        # Front left leg
        grid[y][3] = W; grid[y][4] = Wd
        # Front right leg
        grid[y][11] = W; grid[y][12] = Wd

    return grid


def build_bed_basic():
    """Basic bed: 32x48 (2x4 footprint) - 3/4 perspective

    3/4 view structure:
    - Headboard: VERTICAL surface, we see its FRONT FACE (rows 0-14)
    - Mattress top: HORIZONTAL surface, viewed from above (rows 12-32)
    - Mattress front: VERTICAL surface, darker/shadow (rows 32-40)
    - Footboard: Small vertical element at bottom (rows 38-48)
    """
    grid = [[T] * 32 for _ in range(48)]

    # === HEADBOARD (vertical front face) - rows 0-14 ===
    # This is a vertical plane - draw it FRONTALLY
    # Left side lighter (top-left light), right side darker
    for y in range(0, 14):
        for x in range(4, 28):
            if x < 12:
                grid[y][x] = Wl  # Left third - lit
            elif x < 20:
                grid[y][x] = W   # Middle - base
            else:
                grid[y][x] = Wd  # Right third - shadow

    # Headboard top edge (horizontal top surface, thin)
    for x in range(4, 28):
        grid[0][x] = Wl  # Top edge catches light

    # Headboard decorative panel (inset)
    for y in range(3, 11):
        for x in range(8, 24):
            grid[y][x] = Wd  # Recessed panel is darker

    # === PILLOW (on horizontal mattress surface) - rows 12-18 ===
    for y in range(12, 18):
        for x in range(8, 24):
            if x < 14:
                grid[y][x] = Pl  # Left - lit
            elif x < 18:
                grid[y][x] = P   # Center - base
            else:
                grid[y][x] = Pd  # Right - shadow

    # === BLANKET TOP SURFACE (horizontal plane) - rows 16-32 ===
    # Viewed from above - light on top-left, dark on bottom-right
    for y in range(16, 32):
        for x in range(4, 28):
            # Skip pillow area
            if y < 18 and 8 <= x < 24:
                continue
            if y < 22:
                # Upper part of blanket - lighter
                if x < 14:
                    grid[y][x] = Bl
                elif x < 20:
                    grid[y][x] = B
                else:
                    grid[y][x] = Bd
            else:
                # Lower part - slightly darker overall
                if x < 12:
                    grid[y][x] = B
                else:
                    grid[y][x] = Bd

    # Blanket fold line (adds detail)
    for x in range(6, 26):
        grid[24][x] = Bd

    # === MATTRESS FRONT FACE (vertical plane, in shadow) - rows 32-40 ===
    # This shows the DEPTH - front face is darker than top
    mattress_dark = (70, 40, 70, 255)   # Darker purple for front
    mattress_shadow = (55, 30, 55, 255)  # Even darker for right side

    for y in range(32, 40):
        for x in range(4, 28):
            if x < 12:
                grid[y][x] = Bd  # Left - less shadow
            elif x < 20:
                grid[y][x] = mattress_dark  # Center
            else:
                grid[y][x] = mattress_shadow  # Right - deep shadow

    # Edge line between top and front (strong contrast)
    for x in range(4, 28):
        grid[32][x] = (60, 35, 60, 255)  # Dark edge line

    # === FOOTBOARD (small vertical element) - rows 38-48 ===
    for y in range(38, 48):
        for x in range(4, 28):
            if x < 12:
                grid[y][x] = Wl
            elif x < 20:
                grid[y][x] = W
            else:
                grid[y][x] = Wd

    # Footboard top edge
    for x in range(4, 28):
        grid[38][x] = Wl

    # === CORNER POSTS (visible at front) ===
    for y in range(38, 48):
        # Left post
        grid[y][4] = Wl
        grid[y][5] = W
        # Right post
        grid[y][26] = W
        grid[y][27] = Wd

    return grid


def build_bookshelf():
    """Bookshelf: 16x24 (1x2 footprint)"""
    grid = [[T] * 16 for _ in range(24)]

    # Frame
    for y in range(24):
        grid[y][1] = Wd
        grid[y][2] = W if y < 20 else Wl
        grid[y][13] = W
        grid[y][14] = Wd

    # Top
    for x in range(1, 15):
        grid[0][x] = Wl
        grid[1][x] = W

    # Shelves (3 of them)
    for shelf_y in [7, 14, 21]:
        for x in range(2, 14):
            grid[shelf_y][x] = W
            grid[shelf_y + 1][x] = Wd if x > 8 else W

    # Books on shelves (simplified colored rectangles)
    book_colors = [
        (140, 60, 60, 255),   # Red
        (60, 100, 140, 255),  # Blue
        (60, 120, 60, 255),   # Green
        (140, 120, 60, 255),  # Yellow/brown
    ]
    for shelf_y in [3, 10, 17]:
        for i, x in enumerate(range(4, 12, 2)):
            color = book_colors[i % len(book_colors)]
            for by in range(shelf_y, shelf_y + 4):
                grid[by][x] = color
                grid[by][x + 1] = color

    return grid


def build_lamp_table():
    """Table lamp: 16x20 (1x1 footprint)"""
    grid = [[T] * 16 for _ in range(20)]

    # Lampshade (top)
    for y in range(0, 8):
        width = 3 + y
        start_x = 8 - width
        end_x = 8 + width
        for x in range(max(0, start_x), min(16, end_x)):
            diag = (x - 8) + (y - 4)
            if diag < -3:
                grid[y][x] = Ll
            elif diag < 2:
                grid[y][x] = L
            else:
                grid[y][x] = Ld

    # Neck
    for y in range(8, 12):
        grid[y][7] = Md
        grid[y][8] = M

    # Base
    for y in range(12, 16):
        for x in range(5, 11):
            diag = (x - 8) + (y - 14)
            if diag < -2:
                grid[y][x] = Ml
            elif diag < 1:
                grid[y][x] = M
            else:
                grid[y][x] = Md

    # Stand base (wider)
    for y in range(16, 20):
        for x in range(4, 12):
            grid[y][x] = Md if x > 8 else M

    return grid


# =============================================================================
# ADDITIONAL FURNITURE
# =============================================================================

def build_table_stone():
    """Stone table: 32x24 (2x2 footprint) - 3/4 perspective

    Structure:
    - Top surface: HORIZONTAL plane, viewed from above (left-right shading)
    - Front apron: VERTICAL plane, darker (shows depth)
    - Legs: visible below
    """
    grid = [[T] * 32 for _ in range(24)]

    # === TABLE TOP (horizontal surface, viewed from above) ===
    for y in range(8):
        for x in range(32):
            if x < 10:
                grid[y][x] = Sl  # Left - lit
            elif x < 22:
                grid[y][x] = S   # Center - base
            else:
                grid[y][x] = Sd  # Right - shadow

    # Top edge highlight
    for x in range(32):
        grid[0][x] = Sl

    # === FRONT APRON (vertical surface, darker) ===
    for y in range(8, 12):
        for x in range(32):
            if x < 10:
                grid[y][x] = S   # Left - less dark
            elif x < 22:
                grid[y][x] = Sd  # Center - dark
            else:
                grid[y][x] = Sd  # Right - dark

    # Edge line between top and apron
    for x in range(32):
        grid[8][x] = Sd

    # === LEGS (four corners) ===
    for y in range(12, 24):
        # Front left leg
        grid[y][2] = S; grid[y][3] = S; grid[y][4] = Sd
        # Front right leg
        grid[y][27] = S; grid[y][28] = Sd; grid[y][29] = Sd
        # Back left leg (partially visible)
        if y < 18:
            grid[y][6] = S; grid[y][7] = Sd
        # Back right leg (partially visible)
        if y < 18:
            grid[y][24] = S; grid[y][25] = Sd

    return grid


def build_chair_fancy():
    """Fancy chair: 16x22 (1x1 footprint) - 3/4 perspective with ornate back

    Structure:
    - Ornate back: VERTICAL surface (taller, decorative)
    - Cushion seat: HORIZONTAL surface (viewed from above)
    - Legs: visible below
    """
    grid = [[T] * 16 for _ in range(22)]

    # === ORNATE BACK (vertical front face, taller) ===
    for y in range(0, 10):
        for x in range(4, 12):
            if x < 6:
                grid[y][x] = Wl  # Left - lit
            elif x < 10:
                grid[y][x] = W   # Center - base
            else:
                grid[y][x] = Wd  # Right - shadow

    # Decorative curved top (notches)
    grid[0][4] = T; grid[0][5] = T; grid[0][10] = T; grid[0][11] = T
    grid[1][4] = Wl; grid[1][11] = Wd

    # Top edge highlight
    for x in range(6, 10):
        grid[0][x] = Wl

    # === CUSHION SEAT (horizontal surface) ===
    cushion_d = (120, 50, 50, 255)
    cushion = (160, 70, 70, 255)
    cushion_l = (190, 100, 100, 255)

    for y in range(10, 14):
        for x in range(2, 14):
            if x < 6:
                grid[y][x] = cushion_l  # Left - lit
            elif x < 10:
                grid[y][x] = cushion    # Center - base
            else:
                grid[y][x] = cushion_d  # Right - shadow

    # Front edge of seat
    for x in range(2, 14):
        grid[14][x] = cushion_d

    # === LEGS ===
    for y in range(15, 22):
        # Front left leg
        grid[y][3] = W; grid[y][4] = Wd
        # Front right leg
        grid[y][11] = W; grid[y][12] = Wd

    return grid


def build_bed_fancy():
    """Fancy bed: 32x52 (2x4 footprint) - 3/4 perspective with ornate details

    Structure:
    - Ornate headboard: VERTICAL surface with decorative top
    - Two pillows: on horizontal mattress surface
    - Patterned blanket: HORIZONTAL surface
    - Mattress front: VERTICAL surface (darker, shows depth)
    - Ornate footboard: VERTICAL surface with posts
    """
    grid = [[T] * 32 for _ in range(52)]

    # === ORNATE HEADBOARD (vertical front face) - rows 0-16 ===
    for y in range(0, 16):
        for x in range(4, 28):
            if x < 12:
                grid[y][x] = Wl  # Left - lit
            elif x < 20:
                grid[y][x] = W   # Center - base
            else:
                grid[y][x] = Wd  # Right - shadow

    # Decorative headboard top (ornate curved shape)
    for x in range(4, 28):
        if x < 8 or x > 23:
            grid[0][x] = T  # Notched corners
            grid[1][x] = T
        else:
            grid[0][x] = Wl

    # Decorative panel inset
    for y in range(4, 12):
        for x in range(8, 24):
            grid[y][x] = Wd  # Recessed panel

    # Finial details at top
    grid[0][8] = Wl; grid[0][23] = W

    # === FANCY PILLOWS (two pillows) - rows 14-20 ===
    for y in range(14, 20):
        # Left pillow
        for x in range(6, 14):
            if x < 9:
                grid[y][x] = Pl
            elif x < 12:
                grid[y][x] = P
            else:
                grid[y][x] = Pd
        # Right pillow
        for x in range(18, 26):
            if x < 21:
                grid[y][x] = Pl
            elif x < 24:
                grid[y][x] = P
            else:
                grid[y][x] = Pd

    # === PATTERNED BLANKET TOP (horizontal surface) - rows 18-36 ===
    stripe_dark = (115, 75, 115, 255)  # Darker stripe

    for y in range(18, 36):
        for x in range(4, 28):
            # Skip pillow area
            if y < 20 and 6 <= x < 26:
                continue

            # Base color with left-right shading
            if x < 12:
                base = Bl
            elif x < 20:
                base = B
            else:
                base = Bd

            # Add horizontal stripes
            if (y // 4) % 2 == 1:
                base = stripe_dark if x >= 12 else B

            grid[y][x] = base

    # Blanket fold line
    for x in range(6, 26):
        grid[28][x] = Bd

    # === MATTRESS FRONT FACE (vertical plane, darker) - rows 36-44 ===
    mattress_dark = (70, 40, 70, 255)
    mattress_shadow = (55, 30, 55, 255)

    for y in range(36, 44):
        for x in range(4, 28):
            if x < 12:
                grid[y][x] = Bd
            elif x < 20:
                grid[y][x] = mattress_dark
            else:
                grid[y][x] = mattress_shadow

    # Edge line between blanket and front
    for x in range(4, 28):
        grid[36][x] = (60, 35, 60, 255)

    # === ORNATE FOOTBOARD - rows 42-52 ===
    for y in range(42, 52):
        for x in range(4, 28):
            if x < 12:
                grid[y][x] = Wl
            elif x < 20:
                grid[y][x] = W
            else:
                grid[y][x] = Wd

    # Footboard top edge
    for x in range(4, 28):
        grid[42][x] = Wl

    # Decorative corner posts
    for y in range(44, 52):
        # Left post
        grid[y][4] = Wl; grid[y][5] = W; grid[y][6] = W
        # Right post
        grid[y][25] = W; grid[y][26] = Wd; grid[y][27] = Wd

    return grid


def build_chest_wood():
    """Wooden chest: 32x20 (2x1 footprint) - 3/4 perspective

    Structure:
    - Lid top: HORIZONTAL surface (viewed from above)
    - Front face: VERTICAL surface (darker)
    """
    grid = [[T] * 32 for _ in range(20)]

    # === LID TOP (horizontal surface) ===
    for y in range(0, 6):
        for x in range(4, 28):
            if x < 12:
                grid[y][x] = Wl  # Left - lit
            elif x < 20:
                grid[y][x] = W   # Center - base
            else:
                grid[y][x] = Wd  # Right - shadow

    # Lid top edge highlight
    for x in range(4, 28):
        grid[0][x] = Wl

    # Lid front edge (shows curve)
    for x in range(4, 28):
        grid[5][x] = W if x < 16 else Wd

    # === FRONT FACE (vertical, darker) ===
    for y in range(6, 20):
        for x in range(2, 30):
            if x < 10:
                grid[y][x] = W   # Left - less dark
            elif x < 22:
                grid[y][x] = Wd  # Center - dark
            else:
                grid[y][x] = Wd  # Right - dark

    # Edge line between lid and body
    for x in range(2, 30):
        grid[6][x] = Wd

    # Metal bands
    for x in range(2, 30):
        grid[3][x] = Md
        grid[12][x] = Md

    # Lock on front
    grid[8][15] = Ml; grid[8][16] = M
    grid[9][15] = M; grid[9][16] = Md

    return grid


def build_chest_iron():
    """Iron chest: 32x20 (2x1 footprint) - 3/4 perspective"""
    grid = [[T] * 32 for _ in range(20)]

    # === LID TOP (horizontal surface) ===
    for y in range(0, 6):
        for x in range(4, 28):
            if x < 12:
                grid[y][x] = Ml  # Left - lit
            elif x < 20:
                grid[y][x] = M   # Center - base
            else:
                grid[y][x] = Md  # Right - shadow

    # Lid top edge highlight
    for x in range(4, 28):
        grid[0][x] = Ml

    # === FRONT FACE (vertical, darker) ===
    for y in range(6, 20):
        for x in range(2, 30):
            if x < 10:
                grid[y][x] = M   # Left - less dark
            elif x < 22:
                grid[y][x] = Md  # Center - dark
            else:
                grid[y][x] = Md  # Right - dark

    # Edge line
    for x in range(2, 30):
        grid[6][x] = Md

    # Reinforcement bands (vertical)
    for y in range(6, 20):
        grid[y][6] = Md
        grid[y][25] = Md

    # Lock (larger)
    for y in range(8, 12):
        for x in range(14, 18):
            grid[y][x] = (40, 45, 50, 255)  # Dark lock

    return grid


def build_chest_large():
    """Large chest: 32x28 (2x2 footprint) - 3/4 perspective"""
    grid = [[T] * 32 for _ in range(28)]

    # === LID TOP (horizontal surface) ===
    for y in range(0, 8):
        for x in range(4, 28):
            if x < 12:
                grid[y][x] = Wl  # Left - lit
            elif x < 20:
                grid[y][x] = W   # Center - base
            else:
                grid[y][x] = Wd  # Right - shadow

    # Lid top edge highlight
    for x in range(4, 28):
        grid[0][x] = Wl

    # === FRONT FACE (vertical, darker) ===
    for y in range(8, 28):
        for x in range(2, 30):
            if x < 10:
                grid[y][x] = W   # Left - less dark
            elif x < 22:
                grid[y][x] = Wd  # Center - dark
            else:
                grid[y][x] = Wd  # Right - dark

    # Edge line between lid and body
    for x in range(2, 30):
        grid[8][x] = Wd

    # Metal bands
    for x in range(2, 30):
        grid[4][x] = Md
        grid[16][x] = Md
        grid[24][x] = Md

    # Large lock
    for y in range(10, 14):
        for x in range(14, 18):
            grid[y][x] = M if x < 16 else Md

    return grid


def build_barrel():
    """Barrel: 16x20 (1x1 footprint) - 3/4 perspective

    Barrel is cylindrical - show top circle + front curve
    """
    grid = [[T] * 16 for _ in range(20)]

    # === TOP (circular, viewed from above) - rows 0-6 ===
    for y in range(0, 6):
        # Circular shape
        radius = 5 - abs(y - 2)
        for x in range(8 - radius, 8 + radius + 1):
            if 0 <= x < 16:
                if x < 6:
                    grid[y][x] = Wl  # Left - lit
                elif x < 10:
                    grid[y][x] = W   # Center - base
                else:
                    grid[y][x] = Wd  # Right - shadow

    # Top edge highlight
    for x in range(4, 12):
        grid[0][x] = Wl

    # === FRONT CURVED SURFACE (vertical, darker) - rows 6-20 ===
    for y in range(6, 20):
        # Slightly bulging shape
        bulge = 1 if 8 < y < 16 else 0
        for x in range(3 - bulge, 13 + bulge):
            if 0 <= x < 16:
                if x < 5:
                    grid[y][x] = W   # Left edge - some light
                elif x < 11:
                    grid[y][x] = Wd  # Center-right - darker
                else:
                    grid[y][x] = Wd  # Right edge - dark

    # Edge between top and front
    for x in range(3, 13):
        grid[6][x] = Wd

    # Metal bands
    for x in range(3, 13):
        grid[2][x] = Md   # Top band
        grid[10][x] = Md  # Middle band
        grid[17][x] = Md  # Bottom band

    return grid


def build_crate():
    """Crate: 16x18 (1x1 footprint) - 3/4 perspective cube

    Shows top surface + front face like a block
    """
    grid = [[T] * 16 for _ in range(18)]

    # === TOP SURFACE (horizontal) - rows 0-6 ===
    for y in range(0, 6):
        for x in range(16):
            if x < 5:
                grid[y][x] = Wl  # Left - lit
            elif x < 11:
                grid[y][x] = W   # Center - base
            else:
                grid[y][x] = Wd  # Right - shadow

    # Top edge highlight
    for x in range(16):
        grid[0][x] = Wl

    # === FRONT FACE (vertical, darker) - rows 6-18 ===
    for y in range(6, 18):
        for x in range(16):
            if x < 5:
                grid[y][x] = W   # Left - less dark
            elif x < 11:
                grid[y][x] = Wd  # Center
            else:
                grid[y][x] = Wd  # Right - dark

    # Edge between top and front
    for x in range(16):
        grid[6][x] = Wd

    # Plank lines (vertical on front)
    for y in range(6, 18):
        grid[y][5] = Wd
        grid[y][10] = Wd

    # Horizontal plank line on front
    for x in range(16):
        grid[12][x] = Wd

    return grid


def build_shelf():
    """Wall shelf: 32x16 (2x1 footprint)"""
    grid = [[T] * 32 for _ in range(16)]

    # Shelf surface
    for y in range(4, 10):
        for x in range(32):
            diag = (x - 16) + (y - 7)
            if diag < -10:
                grid[y][x] = Wl
            elif diag < 6:
                grid[y][x] = W
            else:
                grid[y][x] = Wd

    # Brackets
    for y in range(8, 16):
        grid[y][4] = Wd
        grid[y][5] = W
        grid[y][26] = W
        grid[y][27] = Wd

    return grid


def build_lamp_floor():
    """Floor lamp: 16x24 (1x1 footprint)"""
    grid = [[T] * 16 for _ in range(24)]

    # Lampshade
    for y in range(0, 8):
        width = 2 + y
        for x in range(8 - width, 8 + width):
            if 0 <= x < 16:
                diag = (x - 8) + (y - 4)
                if diag < -2:
                    grid[y][x] = Ll
                elif diag < 2:
                    grid[y][x] = L
                else:
                    grid[y][x] = Ld

    # Pole
    for y in range(8, 22):
        grid[y][7] = Md
        grid[y][8] = M

    # Base
    for y in range(20, 24):
        for x in range(4, 12):
            grid[y][x] = Md if x > 8 else M

    return grid


def build_torch_wall():
    """Wall torch: 16x16 (1x1 footprint)"""
    grid = [[T] * 16 for _ in range(16)]

    # Flame
    flame_colors = [
        (255, 200, 80, 255),   # Bright
        (230, 120, 40, 255),   # Orange
        (180, 60, 20, 255),    # Dark
    ]
    for y in range(0, 6):
        width = 3 - y // 2
        for x in range(8 - width, 8 + width):
            if 0 <= x < 16:
                idx = min(2, (x - 6) // 2)
                grid[y][x] = flame_colors[max(0, idx)]

    # Torch handle
    for y in range(6, 14):
        grid[y][7] = Wd
        grid[y][8] = W

    # Wall mount
    for y in range(12, 16):
        for x in range(5, 11):
            grid[y][x] = Md

    return grid


def build_chandelier():
    """Chandelier: 32x28 (2x2 footprint) - hanging light"""
    grid = [[T] * 32 for _ in range(28)]

    # Chain at top
    for y in range(0, 6):
        grid[y][15] = Md
        grid[y][16] = M

    # Central hub
    for y in range(6, 12):
        for x in range(12, 20):
            diag = (x - 16) + (y - 9)
            if diag < -2:
                grid[y][x] = Ml
            elif diag < 2:
                grid[y][x] = M
            else:
                grid[y][x] = Md

    # Arms extending out
    for x in range(4, 28):
        if 8 < x < 14 or 18 < x < 24:
            grid[10][x] = M
            grid[11][x] = Md

    # Candles on arms
    candle_x = [6, 12, 20, 26]
    for cx in candle_x:
        # Candle
        for y in range(8, 12):
            grid[y][cx] = (230, 220, 200, 255)
        # Flame
        grid[6][cx] = (255, 200, 80, 255)
        grid[7][cx] = (230, 120, 40, 255)

    return grid


def build_fireplace():
    """Fireplace: 32x28 (2x2 footprint)"""
    grid = [[T] * 32 for _ in range(28)]

    # Stone frame
    for y in range(28):
        for x in range(32):
            diag = (x - 16) + (y - 14)
            if diag < -12:
                grid[y][x] = Sl
            elif diag < 6:
                grid[y][x] = S
            else:
                grid[y][x] = Sd

    # Fire opening (dark)
    for y in range(8, 24):
        for x in range(8, 24):
            grid[y][x] = (30, 25, 20, 255)

    # Fire inside
    for y in range(12, 22):
        for x in range(10, 22):
            diag = (x - 16) + (y - 17)
            if diag < -4:
                grid[y][x] = Fl
            elif diag < 2:
                grid[y][x] = F
            else:
                grid[y][x] = Fd

    # Mantle top
    for y in range(0, 4):
        for x in range(2, 30):
            grid[y][x] = Sl if x < 16 else S

    return grid


def build_rug_small():
    """Small rug: 32x32 (2x2 footprint) - flat on ground"""
    grid = [[T] * 32 for _ in range(32)]

    # Rug colors
    rug_d = (120, 50, 50, 255)
    rug = (160, 70, 70, 255)
    rug_l = (190, 100, 100, 255)
    border = (80, 40, 40, 255)

    # Rug body with border
    for y in range(32):
        for x in range(32):
            # Border
            if x < 3 or x > 28 or y < 3 or y > 28:
                grid[y][x] = border
            else:
                diag = (x - 16) + (y - 16)
                if diag < -8:
                    grid[y][x] = rug_l
                elif diag < 4:
                    grid[y][x] = rug
                else:
                    grid[y][x] = rug_d

    return grid


def build_rug_large():
    """Large rug: 48x48 (3x3 footprint)"""
    grid = [[T] * 48 for _ in range(48)]

    rug_d = (50, 80, 120, 255)
    rug = (70, 110, 160, 255)
    rug_l = (100, 140, 190, 255)
    border = (40, 60, 90, 255)

    for y in range(48):
        for x in range(48):
            if x < 4 or x > 43 or y < 4 or y > 43:
                grid[y][x] = border
            else:
                diag = (x - 24) + (y - 24)
                if diag < -12:
                    grid[y][x] = rug_l
                elif diag < 6:
                    grid[y][x] = rug
                else:
                    grid[y][x] = rug_d

    return grid


def build_painting_small():
    """Small painting: 16x16 (1x1 footprint)"""
    grid = [[T] * 16 for _ in range(16)]

    # Frame
    frame_d = (60, 45, 30, 255)
    frame = (100, 75, 50, 255)

    for y in range(16):
        for x in range(16):
            if x < 2 or x > 13 or y < 2 or y > 13:
                grid[y][x] = frame if x < 8 else frame_d
            else:
                # Simple landscape
                if y < 8:
                    grid[y][x] = (100, 160, 220, 255)  # Sky
                else:
                    grid[y][x] = (60, 120, 60, 255)  # Ground

    return grid


def build_painting_large():
    """Large painting: 32x16 (2x1 footprint)"""
    grid = [[T] * 32 for _ in range(16)]

    frame_d = (60, 45, 30, 255)
    frame = (100, 75, 50, 255)

    for y in range(16):
        for x in range(32):
            if x < 2 or x > 29 or y < 2 or y > 13:
                grid[y][x] = frame if x < 16 else frame_d
            else:
                if y < 7:
                    grid[y][x] = (100, 160, 220, 255)
                else:
                    grid[y][x] = (60, 120, 60, 255)

    return grid


def build_statue_stone():
    """Stone statue: 16x24 (1x1 footprint)"""
    grid = [[T] * 16 for _ in range(24)]

    # Base pedestal
    for y in range(18, 24):
        for x in range(3, 13):
            diag = (x - 8) + (y - 21)
            if diag < -2:
                grid[y][x] = Sl
            elif diag < 2:
                grid[y][x] = S
            else:
                grid[y][x] = Sd

    # Statue body (simple figure)
    for y in range(4, 18):
        width = 3 if y < 12 else 4
        for x in range(8 - width, 8 + width):
            if 0 <= x < 16:
                diag = (x - 8) + (y - 11)
                if diag < -2:
                    grid[y][x] = Sl
                elif diag < 2:
                    grid[y][x] = S
                else:
                    grid[y][x] = Sd

    # Head
    for y in range(0, 6):
        for x in range(5, 11):
            diag = (x - 8) + (y - 3)
            if diag < -1:
                grid[y][x] = Sl
            elif diag < 1:
                grid[y][x] = S
            else:
                grid[y][x] = Sd

    return grid


def build_potted_plant():
    """Potted plant: 16x20 (1x1 footprint)"""
    grid = [[T] * 16 for _ in range(20)]

    # Plant (green leaves)
    leaf_d = (40, 85, 40, 255)
    leaf = (55, 120, 55, 255)
    leaf_l = (80, 150, 70, 255)

    for y in range(0, 12):
        cy = 6
        radius = 5 - abs(y - cy) // 2

        for x in range(8 - radius, 8 + radius):
            if 0 <= x < 16:
                diag = (x - 8) + (y - 6)
                if diag < -2:
                    grid[y][x] = leaf_l
                elif diag < 2:
                    grid[y][x] = leaf
                else:
                    grid[y][x] = leaf_d

    # Pot
    pot_d = (130, 70, 50, 255)
    pot = (170, 95, 65, 255)
    pot_l = (200, 125, 90, 255)

    for y in range(12, 20):
        width = 4 + (y - 12) // 2
        for x in range(8 - width, 8 + width):
            if 0 <= x < 16:
                diag = (x - 8) + (y - 16)
                if diag < -2:
                    grid[y][x] = pot_l
                elif diag < 2:
                    grid[y][x] = pot
                else:
                    grid[y][x] = pot_d

    return grid


def build_banner():
    """Banner: 16x24 (1x1 footprint)"""
    grid = [[T] * 16 for _ in range(24)]

    # Pole at top
    for x in range(4, 12):
        grid[0][x] = Wd
        grid[1][x] = W

    # Banner fabric
    banner_d = (120, 30, 30, 255)
    banner = (160, 50, 50, 255)
    banner_l = (190, 80, 80, 255)

    for y in range(2, 22):
        width = 5 + ((y - 2) % 4 - 2)  # Slight wave
        for x in range(8 - width, 8 + width):
            if 0 <= x < 16:
                diag = (x - 8) + (y - 12)
                if diag < -2:
                    grid[y][x] = banner_l
                elif diag < 2:
                    grid[y][x] = banner
                else:
                    grid[y][x] = banner_d

    # Pointed bottom
    grid[22][7] = banner; grid[22][8] = banner
    grid[23][7] = banner_d; grid[23][8] = banner_d

    return grid


def build_clock():
    """Wall clock: 16x16 (1x1 footprint)"""
    grid = [[T] * 16 for _ in range(16)]

    # Clock frame (circular)
    for y in range(16):
        for x in range(16):
            dx, dy = x - 8, y - 8
            dist = (dx * dx + dy * dy) ** 0.5

            if dist <= 7:
                if dist > 5.5:
                    # Frame
                    grid[y][x] = Wd if x > 8 else W
                else:
                    # Face
                    grid[y][x] = (240, 235, 220, 255)

    # Clock hands
    grid[4][8] = (30, 30, 30, 255)  # 12
    grid[8][12] = (30, 30, 30, 255)  # 3 (hour hand)
    grid[8][8] = (30, 30, 30, 255)  # Center

    return grid


def build_mirror():
    """Mirror: 16x24 (1x2 footprint)"""
    grid = [[T] * 16 for _ in range(24)]

    # Frame
    for y in range(24):
        for x in range(16):
            if x < 2 or x > 13 or y < 2 or y > 21:
                grid[y][x] = Wl if x < 8 else Wd
            else:
                # Mirror surface (reflective blue-ish)
                diag = (x - 8) + (y - 12)
                if diag < -6:
                    grid[y][x] = (200, 210, 220, 255)
                elif diag < 4:
                    grid[y][x] = (180, 190, 200, 255)
                else:
                    grid[y][x] = (160, 170, 180, 255)

    return grid


def main():
    output_dir = "/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Sprites/Furniture"
    os.makedirs(output_dir, exist_ok=True)

    sprites = [
        # Crafting stations
        ("workbench.png", build_workbench()),
        ("furnace.png", build_furnace()),
        ("anvil.png", build_anvil()),
        ("forge.png", build_forge()),
        ("loom.png", build_loom()),
        ("cooking_pot.png", build_cooking_pot()),
        ("cauldron.png", build_cauldron()),
        ("sawmill.png", build_sawmill()),
        ("stonecutter.png", build_stonecutter()),
        # Tables
        ("table_wood.png", build_table_wood()),
        ("table_stone.png", build_table_stone()),
        # Seating
        ("chair_wood.png", build_chair_wood()),
        ("chair_fancy.png", build_chair_fancy()),
        # Beds
        ("bed_basic.png", build_bed_basic()),
        ("bed_fancy.png", build_bed_fancy()),
        # Storage
        ("bookshelf.png", build_bookshelf()),
        ("chest_wood.png", build_chest_wood()),
        ("chest_iron.png", build_chest_iron()),
        ("chest_large.png", build_chest_large()),
        ("barrel.png", build_barrel()),
        ("crate.png", build_crate()),
        ("shelf.png", build_shelf()),
        # Lighting
        ("lamp_table.png", build_lamp_table()),
        ("lamp_floor.png", build_lamp_floor()),
        ("torch_wall.png", build_torch_wall()),
        ("chandelier.png", build_chandelier()),
        ("fireplace.png", build_fireplace()),
        # Decorative
        ("rug_small.png", build_rug_small()),
        ("rug_large.png", build_rug_large()),
        ("painting_small.png", build_painting_small()),
        ("painting_large.png", build_painting_large()),
        ("statue_stone.png", build_statue_stone()),
        ("potted_plant.png", build_potted_plant()),
        ("banner.png", build_banner()),
        ("clock.png", build_clock()),
        ("mirror.png", build_mirror()),
    ]

    for filename, grid in sprites:
        img = create_sprite_from_grid(grid)
        path = f"{output_dir}/{filename}"
        img.save(path)
        print(f"Created: {path} ({img.size[0]}x{img.size[1]})")

    print(f"\nGenerated {len(sprites)} furniture sprites")
    print("\nUnity import settings:")
    print("  - Pixels Per Unit: 16")
    print("  - Filter Mode: Point (no filter)")
    print("  - Compression: None")
    print("  - Pivot: Bottom Center (for tall items)")


if __name__ == "__main__":
    main()
