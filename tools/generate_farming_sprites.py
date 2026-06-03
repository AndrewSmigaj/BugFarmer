#!/usr/bin/env python3
"""Generate farming-related sprites for Bug Farmer.

Creates:
- Watering can tool sprites (16x16) + inventory icons
- Seed item icons (16x16)
- Produce item icons (16x16)
- Crop plant sprites at different growth stages (16x16 to 16x32)
- Fruit tree variants (apple, orange)
- Rotten fruit items

Design principles:
- 45-degree top-down perspective
- Light source: top-left
- Shadows: bottom-right
"""

from PIL import Image
import os

# Colors (RGBA)
T = (0, 0, 0, 0)  # Transparent

# === MATERIAL PALETTES ===

# Wood handle
Hd = (70, 50, 35, 255)     # Handle dark
H  = (120, 90, 60, 255)    # Handle base
Hl = (160, 130, 95, 255)   # Handle light

# Metal (for watering can)
Md = (70, 75, 85, 255)     # Metal dark
M  = (120, 125, 135, 255)  # Metal base
Ml = (170, 175, 185, 255)  # Metal light

# Water
Wd = (50, 100, 150, 255)   # Water dark
W  = (80, 150, 200, 255)   # Water base
Wl = (130, 200, 240, 255)  # Water light

# Plant greens
Gd = (40, 85, 40, 255)     # Green dark
G  = (55, 120, 55, 255)    # Green base
Gl = (80, 150, 70, 255)    # Green light

# Soil/dirt
Sd = (70, 50, 35, 255)     # Soil dark
S  = (100, 75, 50, 255)    # Soil base
Sl = (130, 100, 70, 255)   # Soil light

# Tomato red
TRd = (150, 40, 40, 255)   # Tomato dark
TR  = (200, 60, 50, 255)   # Tomato base
TRl = (230, 100, 80, 255)  # Tomato light

# Corn yellow
CYd = (180, 150, 40, 255)  # Corn dark
CY  = (230, 200, 60, 255)  # Corn base
CYl = (255, 230, 100, 255) # Corn light

# Wheat tan
WTd = (160, 130, 60, 255)  # Wheat dark
WT  = (200, 170, 90, 255)  # Wheat base
WTl = (230, 200, 130, 255) # Wheat light

# Apple red
ARd = (140, 30, 30, 255)   # Apple dark
AR  = (180, 50, 45, 255)   # Apple base
ARl = (210, 80, 70, 255)   # Apple light

# Orange
ORd = (180, 90, 30, 255)   # Orange dark
OR  = (230, 130, 50, 255)  # Orange base
ORl = (255, 170, 80, 255)  # Orange light

# Rotten (brown-green decay)
ROd = (60, 50, 30, 255)    # Rotten dark
RO  = (90, 75, 45, 255)    # Rotten base
ROl = (110, 95, 60, 255)   # Rotten light


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
# WATERING CAN
# =============================================================================

def build_watering_can():
    """Watering can: 16x16 - classic garden can with spout"""
    grid = [[T] * 16 for _ in range(16)]

    # Main body (bucket shape, rows 5-14)
    for y in range(5, 15):
        # Width varies for rounded bottom
        width = 6 if y < 12 else (5 if y < 14 else 4)
        center = 7

        for x in range(center - width, center + width):
            if 0 <= x < 16:
                if x < center - 2:
                    grid[y][x] = Ml
                elif x < center + 2:
                    grid[y][x] = M
                else:
                    grid[y][x] = Md

    # Water visible inside (top portion)
    for y in range(6, 10):
        for x in range(3, 11):
            if grid[y][x] != T:
                grid[y][x] = Wl if x < 6 else (W if x < 9 else Wd)

    # Spout (angled to the right)
    for i in range(6):
        y = 4 - i // 2
        x = 12 + i // 2
        if 0 <= x < 16 and 0 <= y < 16:
            grid[y][x] = Ml
            if x + 1 < 16:
                grid[y][x + 1] = M

    # Spout head (rose/sprinkler)
    grid[1][14] = Md
    grid[1][15] = Md
    grid[2][14] = Md
    grid[2][15] = Md

    # Handle (top arc)
    for x in range(4, 10):
        grid[3][x] = H
        grid[4][x] = Hl if x < 7 else Hd
    grid[2][4] = Hd
    grid[2][9] = Hd

    # Ground contact
    ground = (max(0, Md[0]-20), max(0, Md[1]-20), max(0, Md[2]-20), 255)
    for x in range(3, 11):
        grid[15][x] = ground

    return grid


def build_watering_can_icon():
    """Watering can icon: 24x24 for inventory display"""
    grid = [[T] * 24 for _ in range(24)]

    # Larger version of watering can
    # Main body (rows 8-21)
    for y in range(8, 22):
        width = 8 if y < 18 else (7 if y < 20 else 6)
        center = 10

        for x in range(center - width, center + width):
            if 0 <= x < 24:
                if x < center - 3:
                    grid[y][x] = Ml
                elif x < center + 3:
                    grid[y][x] = M
                else:
                    grid[y][x] = Md

    # Water inside
    for y in range(9, 14):
        for x in range(4, 16):
            if grid[y][x] != T:
                grid[y][x] = Wl if x < 8 else (W if x < 13 else Wd)

    # Spout
    for i in range(8):
        y = 6 - i // 2
        x = 17 + i // 2
        if 0 <= x < 24 and 0 <= y < 24:
            grid[y][x] = Ml
            if x + 1 < 24:
                grid[y][x + 1] = M

    # Spout head
    for dy in range(3):
        for dx in range(2):
            if 21 + dx < 24 and dy + 1 < 24:
                grid[dy + 1][21 + dx] = Md

    # Handle
    for x in range(5, 14):
        grid[5][x] = H
        grid[6][x] = Hl if x < 9 else Hd
    grid[4][5] = Hd
    grid[4][13] = Hd

    return grid


# =============================================================================
# SEEDS
# =============================================================================

def build_seed_packet(seed_color_d, seed_color, seed_color_l, packet_color):
    """Generic seed packet icon: 16x16"""
    grid = [[T] * 16 for _ in range(16)]

    # Packet background (small pouch shape)
    Pd = (max(0, packet_color[0]-30), max(0, packet_color[1]-30), max(0, packet_color[2]-30), 255)
    P = packet_color
    Pl = (min(255, packet_color[0]+30), min(255, packet_color[1]+30), min(255, packet_color[2]+30), 255)

    # Packet body (rows 3-13)
    for y in range(3, 14):
        # Rounded bottom
        margin = 0 if y < 12 else (y - 11)
        for x in range(4 + margin, 12 - margin):
            if x < 7:
                grid[y][x] = Pl
            elif x < 9:
                grid[y][x] = P
            else:
                grid[y][x] = Pd

    # Top fold
    for x in range(5, 11):
        grid[3][x] = Pd
        grid[4][x] = P

    # Seeds visible on packet (3 seeds in a row)
    for sx in [6, 8, 10]:
        grid[7][sx] = seed_color_l
        grid[8][sx] = seed_color
        grid[8][sx-1] = seed_color_l
        grid[9][sx] = seed_color_d

    return grid


def build_tomato_seed():
    """Tomato seed packet: 16x16"""
    packet_color = (180, 60, 50, 255)  # Reddish packet
    return build_seed_packet(TRd, TR, TRl, packet_color)


def build_corn_seed():
    """Corn seed packet: 16x16"""
    packet_color = (200, 160, 60, 255)  # Yellow packet
    return build_seed_packet(CYd, CY, CYl, packet_color)


def build_wheat_seed():
    """Wheat seed packet: 16x16"""
    packet_color = (180, 150, 80, 255)  # Tan packet
    return build_seed_packet(WTd, WT, WTl, packet_color)


# =============================================================================
# PRODUCE
# =============================================================================

def build_tomato():
    """Tomato produce: 16x16"""
    grid = [[T] * 16 for _ in range(16)]

    # Round tomato shape
    for y in range(3, 14):
        cy, cx = 8, 8
        ry, rx = 5, 5

        dy = abs(y - cy)
        if dy <= ry:
            ratio = 1 - (dy / ry) ** 2
            if ratio > 0:
                x_range = int(rx * (ratio ** 0.5))
                for x in range(cx - x_range, cx + x_range + 1):
                    if 0 <= x < 16:
                        # Lighting gradient
                        if x < 6:
                            grid[y][x] = TRl
                        elif x < 10:
                            grid[y][x] = TR
                        else:
                            grid[y][x] = TRd

    # Stem/calyx at top
    grid[3][7] = Gd
    grid[3][8] = Gd
    grid[2][8] = G
    grid[2][7] = Gl

    return grid


def build_corn():
    """Corn ear: 16x16"""
    grid = [[T] * 16 for _ in range(16)]

    # Corn cob shape (elongated oval)
    for y in range(2, 14):
        cy, cx = 8, 8
        ry, rx = 6, 3

        dy = abs(y - cy)
        if dy <= ry:
            ratio = 1 - (dy / ry) ** 2
            if ratio > 0:
                x_range = int(rx * (ratio ** 0.5))
                for x in range(cx - x_range, cx + x_range + 1):
                    if 0 <= x < 16:
                        # Kernel rows pattern
                        if (y + x) % 2 == 0:
                            grid[y][x] = CYl
                        else:
                            grid[y][x] = CY

    # Husk at bottom
    grid[14][7] = Gd
    grid[14][8] = Gd
    grid[14][9] = Gd
    grid[15][7] = Gl
    grid[15][8] = G
    grid[15][9] = Gd

    # Silk at top
    grid[1][7] = (200, 180, 140, 255)
    grid[1][8] = (180, 160, 120, 255)

    return grid


def build_wheat_bundle():
    """Wheat bundle: 16x16"""
    grid = [[T] * 16 for _ in range(16)]

    # Multiple wheat stalks bundled
    for stalk_x in [5, 8, 11]:
        # Stalk
        for y in range(6, 15):
            if y < 10:
                grid[y][stalk_x] = WTl
            else:
                grid[y][stalk_x] = WT

        # Wheat head (grain kernels)
        for y in range(2, 7):
            for dx in [-1, 0, 1]:
                x = stalk_x + dx
                if 0 <= x < 16:
                    if y < 4:
                        grid[y][x] = WTl
                    else:
                        grid[y][x] = WT if dx == 0 else WTd

    # Binding at bottom
    grid[13][5] = Hd
    grid[13][8] = Hd
    grid[13][11] = Hd

    return grid


def build_apple():
    """Apple produce: 16x16"""
    grid = [[T] * 16 for _ in range(16)]

    # Round apple shape
    for y in range(4, 14):
        cy, cx = 9, 8
        ry, rx = 5, 5

        dy = abs(y - cy)
        if dy <= ry:
            ratio = 1 - (dy / ry) ** 2
            if ratio > 0:
                x_range = int(rx * (ratio ** 0.5))
                for x in range(cx - x_range, cx + x_range + 1):
                    if 0 <= x < 16:
                        if x < 6:
                            grid[y][x] = ARl
                        elif x < 10:
                            grid[y][x] = AR
                        else:
                            grid[y][x] = ARd

    # Stem
    grid[3][8] = Hd
    grid[4][8] = H

    # Leaf
    grid[3][9] = Gl
    grid[3][10] = G
    grid[2][10] = Gd

    return grid


def build_orange():
    """Orange produce: 16x16"""
    grid = [[T] * 16 for _ in range(16)]

    # Round orange shape
    for y in range(4, 14):
        cy, cx = 9, 8
        ry, rx = 5, 5

        dy = abs(y - cy)
        if dy <= ry:
            ratio = 1 - (dy / ry) ** 2
            if ratio > 0:
                x_range = int(rx * (ratio ** 0.5))
                for x in range(cx - x_range, cx + x_range + 1):
                    if 0 <= x < 16:
                        if x < 6:
                            grid[y][x] = ORl
                        elif x < 10:
                            grid[y][x] = OR
                        else:
                            grid[y][x] = ORd

    # Stem nub
    grid[4][8] = Gd
    grid[3][8] = G

    return grid


def build_rotten_apple():
    """Rotten apple: 16x16"""
    grid = [[T] * 16 for _ in range(16)]

    # Irregular shape (decayed)
    for y in range(4, 14):
        cy, cx = 9, 8
        ry, rx = 5, 5

        dy = abs(y - cy)
        if dy <= ry:
            ratio = 1 - (dy / ry) ** 2
            if ratio > 0:
                x_range = int(rx * (ratio ** 0.5))
                # Irregular edges
                x_range = x_range - ((y + cx) % 2)
                for x in range(cx - x_range, cx + x_range + 1):
                    if 0 <= x < 16:
                        if x < 6:
                            grid[y][x] = ROl
                        elif x < 10:
                            grid[y][x] = RO
                        else:
                            grid[y][x] = ROd

    # Brown spots (decay)
    spots = [(6, 7), (9, 10), (7, 11)]
    for sx, sy in spots:
        if 0 <= sx < 16 and 0 <= sy < 16:
            grid[sy][sx] = (50, 40, 25, 255)

    # Stem (wilted)
    grid[4][8] = ROd

    return grid


def build_rotten_orange():
    """Rotten orange: 16x16"""
    grid = [[T] * 16 for _ in range(16)]

    # Irregular shape
    for y in range(4, 14):
        cy, cx = 9, 8
        ry, rx = 5, 5

        dy = abs(y - cy)
        if dy <= ry:
            ratio = 1 - (dy / ry) ** 2
            if ratio > 0:
                x_range = int(rx * (ratio ** 0.5))
                x_range = x_range - ((y + cx) % 2)
                for x in range(cx - x_range, cx + x_range + 1):
                    if 0 <= x < 16:
                        # Mix of orange-brown decay
                        if x < 6:
                            grid[y][x] = ROl
                        elif x < 10:
                            grid[y][x] = RO
                        else:
                            grid[y][x] = ROd

    # Mold spots
    spots = [(7, 8), (10, 9), (6, 11)]
    for sx, sy in spots:
        if 0 <= sx < 16 and 0 <= sy < 16:
            grid[sy][sx] = (60, 70, 50, 255)  # Greenish mold

    return grid


# =============================================================================
# CROP PLANTS
# =============================================================================

def build_crop_stage0(soil_color=True):
    """Stage 0: Just planted seed (small mound): 16x16"""
    grid = [[T] * 16 for _ in range(16)]

    # Small soil mound with seed barely visible
    for y in range(10, 16):
        width = 3 + (y - 10)
        center = 8
        for x in range(center - width, center + width):
            if 0 <= x < 16:
                if x < 6:
                    grid[y][x] = Sl
                elif x < 10:
                    grid[y][x] = S
                else:
                    grid[y][x] = Sd

    # Tiny green sprout just emerging
    grid[9][8] = Gl
    grid[10][8] = G

    return grid


def build_tomato_stage1():
    """Tomato stage 1: Small sprout: 16x20"""
    grid = [[T] * 16 for _ in range(20)]

    # Soil base
    for y in range(14, 20):
        for x in range(4, 12):
            if x < 7:
                grid[y][x] = Sl
            elif x < 9:
                grid[y][x] = S
            else:
                grid[y][x] = Sd

    # Small stem
    for y in range(10, 15):
        grid[y][8] = G
        grid[y][7] = Gl

    # Two small leaves
    grid[10][6] = Gl
    grid[10][7] = G
    grid[10][9] = G
    grid[10][10] = Gd
    grid[9][7] = Gl
    grid[9][9] = Gd

    return grid


def build_tomato_stage2():
    """Tomato stage 2: Growing plant: 16x24"""
    grid = [[T] * 16 for _ in range(24)]

    # Soil base
    for y in range(18, 24):
        for x in range(4, 12):
            if x < 7:
                grid[y][x] = Sl
            elif x < 9:
                grid[y][x] = S
            else:
                grid[y][x] = Sd

    # Taller stem
    for y in range(8, 19):
        grid[y][8] = G
        grid[y][7] = Gl

    # Multiple leaf clusters
    leaves = [(5, 12), (11, 10), (4, 8), (12, 6)]
    for lx, ly in leaves:
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nx, ny = lx + dx, ly + dy
                if 0 <= nx < 16 and 0 <= ny < 24:
                    if dx < 0:
                        grid[ny][nx] = Gl
                    elif dx > 0:
                        grid[ny][nx] = Gd
                    else:
                        grid[ny][nx] = G

    # Small flower buds
    grid[6][8] = (200, 180, 60, 255)

    return grid


def build_tomato_stage3():
    """Tomato stage 3: Mature with fruit: 16x28"""
    grid = [[T] * 16 for _ in range(28)]

    # Soil base
    for y in range(22, 28):
        for x in range(4, 12):
            if x < 7:
                grid[y][x] = Sl
            elif x < 9:
                grid[y][x] = S
            else:
                grid[y][x] = Sd

    # Full stem
    for y in range(6, 23):
        grid[y][8] = G
        grid[y][7] = Gl

    # Larger leaf clusters
    leaves = [(4, 16), (12, 14), (3, 10), (13, 8)]
    for lx, ly in leaves:
        for dx in range(-2, 3):
            for dy in range(-1, 2):
                nx, ny = lx + dx, ly + dy
                if 0 <= nx < 16 and 0 <= ny < 28:
                    if dx < 0:
                        grid[ny][nx] = Gl
                    elif dx > 0:
                        grid[ny][nx] = Gd
                    else:
                        grid[ny][nx] = G

    # Tomatoes (red fruit)
    tomatoes = [(5, 18), (11, 16), (6, 12), (10, 10)]
    for tx, ty in tomatoes:
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nx, ny = tx + dx, ty + dy
                if 0 <= nx < 16 and 0 <= ny < 28:
                    if dx + dy < 0:
                        grid[ny][nx] = TRl
                    elif dx + dy > 1:
                        grid[ny][nx] = TRd
                    else:
                        grid[ny][nx] = TR

    return grid


def build_corn_stage1():
    """Corn stage 1: Small shoot: 16x20"""
    grid = [[T] * 16 for _ in range(20)]

    # Soil base
    for y in range(14, 20):
        for x in range(4, 12):
            if x < 7:
                grid[y][x] = Sl
            else:
                grid[y][x] = S if x < 9 else Sd

    # Single straight shoot
    for y in range(9, 15):
        grid[y][8] = G
        grid[y][7] = Gl

    # Two leaves
    for i in range(4):
        grid[9 + i // 2][6 - i] = Gl if i < 2 else G
        grid[10 + i // 2][10 + i] = G if i < 2 else Gd

    return grid


def build_corn_stage2():
    """Corn stage 2: Growing stalk: 16x28"""
    grid = [[T] * 16 for _ in range(28)]

    # Soil base
    for y in range(22, 28):
        for x in range(4, 12):
            grid[y][x] = Sl if x < 7 else (S if x < 9 else Sd)

    # Taller stalk
    for y in range(8, 23):
        grid[y][8] = G
        grid[y][7] = Gl
        if y > 15:
            grid[y][9] = Gd  # Thicker at base

    # Multiple leaves
    leaf_heights = [10, 14, 18]
    for ly in leaf_heights:
        for i in range(5):
            lx = 6 - i
            if 0 <= lx < 16:
                grid[ly + i // 2][lx] = Gl if i < 2 else G
            rx = 10 + i
            if 0 <= rx < 16:
                grid[ly + i // 2][rx] = G if i < 2 else Gd

    return grid


def build_corn_stage3():
    """Corn stage 3: Mature with ears: 16x36"""
    grid = [[T] * 16 for _ in range(36)]

    # Soil base
    for y in range(30, 36):
        for x in range(4, 12):
            grid[y][x] = Sl if x < 7 else (S if x < 9 else Sd)

    # Full stalk
    for y in range(4, 31):
        grid[y][8] = G
        grid[y][7] = Gl
        if y > 20:
            grid[y][9] = Gd

    # Leaves at multiple heights
    leaf_heights = [8, 14, 20, 26]
    for ly in leaf_heights:
        for i in range(6):
            lx = 5 - i
            if 0 <= lx < 16 and ly + i // 2 < 36:
                grid[ly + i // 2][lx] = Gl if i < 3 else G
            rx = 11 + i
            if 0 <= rx < 16 and ly + i // 2 < 36:
                grid[ly + i // 2][rx] = G if i < 3 else Gd

    # Corn tassel at top
    for y in range(2, 5):
        grid[y][7] = WTl
        grid[y][8] = WT
        grid[y][9] = WTd
    grid[1][8] = WT

    # Corn ears
    ear_positions = [(10, 18), (6, 24)]
    for ex, ey in ear_positions:
        for dy in range(4):
            for dx in range(-1, 2):
                nx, ny = ex + dx, ey + dy
                if 0 <= nx < 16 and 0 <= ny < 36:
                    grid[ny][nx] = CYl if dx < 0 else (CY if dx == 0 else CYd)
        # Husk
        grid[ey + 4][ex] = Gd

    return grid


def build_wheat_stage1():
    """Wheat stage 1: Small shoots: 16x16"""
    grid = [[T] * 16 for _ in range(16)]

    # Soil
    for y in range(12, 16):
        for x in range(4, 12):
            grid[y][x] = Sl if x < 7 else (S if x < 9 else Sd)

    # Multiple thin shoots
    for sx in [6, 8, 10]:
        for y in range(9, 13):
            grid[y][sx] = Gl if sx < 8 else G

    return grid


def build_wheat_stage2():
    """Wheat stage 2: Growing stalks: 16x20"""
    grid = [[T] * 16 for _ in range(20)]

    # Soil
    for y in range(16, 20):
        for x in range(4, 12):
            grid[y][x] = Sl if x < 7 else (S if x < 9 else Sd)

    # Multiple stalks
    for sx in [5, 7, 9, 11]:
        for y in range(8, 17):
            grid[y][sx] = Gl if sx < 8 else G

    return grid


def build_wheat_stage3():
    """Wheat stage 3: Mature with grain heads: 16x24"""
    grid = [[T] * 16 for _ in range(24)]

    # Soil
    for y in range(20, 24):
        for x in range(4, 12):
            grid[y][x] = Sl if x < 7 else (S if x < 9 else Sd)

    # Full stalks with grain heads
    for sx in [5, 7, 9, 11]:
        # Stalk
        for y in range(6, 21):
            grid[y][sx] = WT

        # Wheat head
        for y in range(2, 7):
            grid[y][sx] = WTl if y < 4 else WT
            if sx - 1 >= 0:
                grid[y][sx - 1] = WTl if y < 5 else WTd
            if sx + 1 < 16:
                grid[y][sx + 1] = WTd

    return grid


# =============================================================================
# FRUIT TREES - Distinct visual designs
# =============================================================================

# Apple tree: Darker, richer green (traditional orchard)
ALd = (35, 75, 35, 255)     # Apple leaf dark
AL  = (50, 105, 50, 255)    # Apple leaf base
ALl = (70, 135, 60, 255)    # Apple leaf light

# Orange tree: Lighter, yellowy-green (citrus/tropical)
OLd = (50, 90, 40, 255)     # Orange leaf dark
OL  = (70, 125, 55, 255)    # Orange leaf base
OLl = (100, 160, 70, 255)   # Orange leaf light

# Tree trunk
TRKd = (70, 50, 35, 255)
TRK  = (120, 90, 60, 255)
TRKl = (160, 130, 95, 255)


def build_tree_apple():
    """Apple tree: 32x48 - Round full canopy, darker green, red apples

    Distinctly different from tree_fruit - rounder shape, darker foliage,
    larger more prominent apples, stockier appearance.
    """
    grid = [[T] * 32 for _ in range(48)]

    # ROUND canopy - more circular than oak (rows 2-34)
    for y in range(2, 35):
        cy, cx = 18, 16
        ry, rx = 16, 15  # Nearly circular

        dy = abs(y - cy)
        if dy <= ry:
            ratio = 1 - (dy / ry) ** 2
            if ratio > 0:
                x_range = int(rx * (ratio ** 0.5))
                x_start = cx - x_range
                x_end = cx + x_range

                for x in range(max(0, x_start), min(32, x_end + 1)):
                    # Top vs front shading
                    if y < 20:  # Top of canopy
                        if x < 10:
                            grid[y][x] = ALl
                        elif x < 22:
                            grid[y][x] = AL
                        else:
                            grid[y][x] = ALd
                    else:  # Front/underside darker
                        if x < 10:
                            grid[y][x] = AL
                        else:
                            grid[y][x] = ALd

    # Edge highlight between top and front
    for x in range(4, 28):
        if grid[19][x] != T:
            grid[19][x] = ALd

    # LARGE red apples - 3x3 each, more prominent
    apple_positions = [(7, 8), (22, 10), (10, 22), (24, 20), (5, 28), (19, 26), (14, 5), (16, 16)]
    for ax, ay in apple_positions:
        # 3x3 apple with shading
        for dy in range(3):
            for dx in range(3):
                px, py = ax + dx, ay + dy
                if 0 <= px < 32 and 0 <= py < 35 and grid[py][px] != T:
                    if dx == 0 and dy == 0:
                        grid[py][px] = ARl  # Top-left highlight
                    elif dx == 2 and dy == 2:
                        grid[py][px] = ARd  # Bottom-right shadow
                    else:
                        grid[py][px] = AR

    # Stocky trunk (rows 32-47) - wider than orange tree
    for y in range(32, 48):
        trunk_half_width = 4
        trunk_center = 16

        for x in range(trunk_center - trunk_half_width, trunk_center + trunk_half_width):
            if y < 40:  # Upper trunk
                if x < trunk_center - 2:
                    grid[y][x] = TRKl
                elif x > trunk_center + 1:
                    grid[y][x] = TRKd
                else:
                    grid[y][x] = TRK
            else:  # Lower trunk (front face darker)
                if x < trunk_center:
                    grid[y][x] = TRK
                else:
                    grid[y][x] = TRKd

    # Ground contact
    ground = (max(0, TRKd[0]-20), max(0, TRKd[1]-20), max(0, TRKd[2]-20), 255)
    for x in range(12, 20):
        grid[47][x] = ground

    return grid


def build_tree_orange():
    """Orange tree: 32x48 - Oval/elongated canopy, lighter citrus-green, oranges

    Distinctly different from apple - more vertical oval shape,
    lighter yellowy-green tropical foliage, thinner trunk.
    """
    grid = [[T] * 32 for _ in range(48)]

    # OVAL canopy - taller and narrower (rows 0-36)
    for y in range(0, 37):
        cy, cx = 18, 16
        ry, rx = 18, 12  # Taller than wide (oval)

        dy = abs(y - cy)
        if dy <= ry:
            ratio = 1 - (dy / ry) ** 2
            if ratio > 0:
                x_range = int(rx * (ratio ** 0.5))
                x_start = cx - x_range
                x_end = cx + x_range

                for x in range(max(0, x_start), min(32, x_end + 1)):
                    # Lighter, more gradient shading for tropical feel
                    if y < 20:  # Top of canopy
                        if x < 11:
                            grid[y][x] = OLl
                        elif x < 21:
                            grid[y][x] = OL
                        else:
                            grid[y][x] = OLd
                    else:  # Front/lower
                        if x < 11:
                            grid[y][x] = OL
                        else:
                            grid[y][x] = OLd

    # Subtle highlight at top
    for x in range(10, 22):
        if grid[3][x] != T:
            grid[3][x] = OLl

    # ORANGES - round 3x3, bright orange
    orange_positions = [(8, 12), (20, 8), (12, 24), (22, 22), (6, 30), (18, 28), (14, 6), (10, 18)]
    for ox, oy in orange_positions:
        # 3x3 orange with shading
        for dy in range(3):
            for dx in range(3):
                px, py = ox + dx, oy + dy
                if 0 <= px < 32 and 0 <= py < 37 and grid[py][px] != T:
                    if dx == 0 and dy == 0:
                        grid[py][px] = ORl  # Top-left highlight
                    elif dx == 2 and dy == 2:
                        grid[py][px] = ORd  # Bottom-right shadow
                    else:
                        grid[py][px] = OR

    # Thinner trunk (rows 34-47) - narrower than apple
    for y in range(34, 48):
        trunk_half_width = 3
        trunk_center = 16

        for x in range(trunk_center - trunk_half_width, trunk_center + trunk_half_width):
            if y < 42:  # Upper trunk
                if x < trunk_center - 1:
                    grid[y][x] = TRKl
                elif x > trunk_center:
                    grid[y][x] = TRKd
                else:
                    grid[y][x] = TRK
            else:  # Lower trunk
                if x < trunk_center:
                    grid[y][x] = TRK
                else:
                    grid[y][x] = TRKd

    # Ground contact
    ground = (max(0, TRKd[0]-20), max(0, TRKd[1]-20), max(0, TRKd[2]-20), 255)
    for x in range(13, 19):
        grid[47][x] = ground

    return grid


# =============================================================================
# MAIN
# =============================================================================

def main():
    items_dir = "/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Resources/Items"
    objects_dir = "/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Resources/Objects"

    os.makedirs(items_dir, exist_ok=True)
    os.makedirs(objects_dir, exist_ok=True)

    sprites_created = []

    # === TOOLS ===
    print("Creating tool sprites...")

    # Watering can (16x16 for world)
    watering_can = build_watering_can()
    img = create_sprite_from_grid(watering_can)
    img.save(f"{items_dir}/watering_can_basic.png")
    sprites_created.append("watering_can_basic.png")

    # Watering can icon (24x24 for inventory)
    watering_can_icon = build_watering_can_icon()
    img = create_sprite_from_grid(watering_can_icon)
    img.save(f"{items_dir}/watering_can_basic_icon.png")
    sprites_created.append("watering_can_basic_icon.png")

    # === SEEDS ===
    print("Creating seed sprites...")

    tomato_seed = build_tomato_seed()
    img = create_sprite_from_grid(tomato_seed)
    img.save(f"{items_dir}/seed_tomato.png")
    sprites_created.append("seed_tomato.png")

    corn_seed = build_corn_seed()
    img = create_sprite_from_grid(corn_seed)
    img.save(f"{items_dir}/seed_corn.png")
    sprites_created.append("seed_corn.png")

    wheat_seed = build_wheat_seed()
    img = create_sprite_from_grid(wheat_seed)
    img.save(f"{items_dir}/seed_wheat.png")
    sprites_created.append("seed_wheat.png")

    # === PRODUCE ===
    print("Creating produce sprites...")

    tomato = build_tomato()
    img = create_sprite_from_grid(tomato)
    img.save(f"{items_dir}/tomato.png")
    sprites_created.append("tomato.png")

    corn = build_corn()
    img = create_sprite_from_grid(corn)
    img.save(f"{items_dir}/corn.png")
    sprites_created.append("corn.png")

    wheat = build_wheat_bundle()
    img = create_sprite_from_grid(wheat)
    img.save(f"{items_dir}/wheat.png")
    sprites_created.append("wheat.png")

    apple = build_apple()
    img = create_sprite_from_grid(apple)
    img.save(f"{items_dir}/apple.png")
    sprites_created.append("apple.png")

    orange = build_orange()
    img = create_sprite_from_grid(orange)
    img.save(f"{items_dir}/orange.png")
    sprites_created.append("orange.png")

    rotten_apple = build_rotten_apple()
    img = create_sprite_from_grid(rotten_apple)
    img.save(f"{items_dir}/rotten_apple.png")
    sprites_created.append("rotten_apple.png")

    rotten_orange = build_rotten_orange()
    img = create_sprite_from_grid(rotten_orange)
    img.save(f"{items_dir}/rotten_orange.png")
    sprites_created.append("rotten_orange.png")

    # === CROP PLANTS ===
    print("Creating crop plant sprites...")

    # Generic stage 0 (same for all crops)
    stage0 = build_crop_stage0()
    img = create_sprite_from_grid(stage0)
    img.save(f"{objects_dir}/plant_stage0.png")
    sprites_created.append("plant_stage0.png")

    # Tomato stages
    tomato_s1 = build_tomato_stage1()
    img = create_sprite_from_grid(tomato_s1)
    img.save(f"{objects_dir}/plant_tomato_stage1.png")
    sprites_created.append("plant_tomato_stage1.png")

    tomato_s2 = build_tomato_stage2()
    img = create_sprite_from_grid(tomato_s2)
    img.save(f"{objects_dir}/plant_tomato_stage2.png")
    sprites_created.append("plant_tomato_stage2.png")

    tomato_s3 = build_tomato_stage3()
    img = create_sprite_from_grid(tomato_s3)
    img.save(f"{objects_dir}/plant_tomato_stage3.png")
    sprites_created.append("plant_tomato_stage3.png")

    # Corn stages
    corn_s1 = build_corn_stage1()
    img = create_sprite_from_grid(corn_s1)
    img.save(f"{objects_dir}/plant_corn_stage1.png")
    sprites_created.append("plant_corn_stage1.png")

    corn_s2 = build_corn_stage2()
    img = create_sprite_from_grid(corn_s2)
    img.save(f"{objects_dir}/plant_corn_stage2.png")
    sprites_created.append("plant_corn_stage2.png")

    corn_s3 = build_corn_stage3()
    img = create_sprite_from_grid(corn_s3)
    img.save(f"{objects_dir}/plant_corn_stage3.png")
    sprites_created.append("plant_corn_stage3.png")

    # Wheat stages
    wheat_s1 = build_wheat_stage1()
    img = create_sprite_from_grid(wheat_s1)
    img.save(f"{objects_dir}/plant_wheat_stage1.png")
    sprites_created.append("plant_wheat_stage1.png")

    wheat_s2 = build_wheat_stage2()
    img = create_sprite_from_grid(wheat_s2)
    img.save(f"{objects_dir}/plant_wheat_stage2.png")
    sprites_created.append("plant_wheat_stage2.png")

    wheat_s3 = build_wheat_stage3()
    img = create_sprite_from_grid(wheat_s3)
    img.save(f"{objects_dir}/plant_wheat_stage3.png")
    sprites_created.append("plant_wheat_stage3.png")

    # === FRUIT TREES ===
    print("Creating fruit tree sprites...")

    tree_apple = build_tree_apple()
    img = create_sprite_from_grid(tree_apple)
    img.save(f"{objects_dir}/tree_apple.png")
    sprites_created.append("tree_apple.png")

    tree_orange = build_tree_orange()
    img = create_sprite_from_grid(tree_orange)
    img.save(f"{objects_dir}/tree_orange.png")
    sprites_created.append("tree_orange.png")

    print(f"\n=== Created {len(sprites_created)} farming sprites ===")
    for name in sprites_created:
        print(f"  - {name}")

    print(f"\nItem sprites: {items_dir}")
    print(f"Object sprites: {objects_dir}")
    print("\nUnity import settings:")
    print("  - Pixels Per Unit: 16")
    print("  - Filter Mode: Point (no filter)")
    print("  - Compression: None")
    print("  - Pivot: Bottom Center (for plants)")


if __name__ == "__main__":
    main()
