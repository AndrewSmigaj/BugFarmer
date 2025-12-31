#!/usr/bin/env python3
"""Generate beekeeping and structure sprites for Bug Farmer.

Design principles from SPRITE_GENERATION_GUIDE.md:
- 45-degree top-down perspective
- Light source: top-left
- 3-5 colors per material
"""

from PIL import Image
import os

# Colors (RGBA)
T = (0, 0, 0, 0)  # Transparent

# Wood - from guide
Wd = (70, 50, 35, 255)
W  = (120, 90, 60, 255)
Wl = (160, 130, 95, 255)

# Stone
Sd = (85, 85, 90, 255)
S  = (120, 120, 125, 255)
Sl = (155, 155, 160, 255)

# Honey (golden yellow)
Hd = (180, 120, 30, 255)
H  = (220, 160, 50, 255)
Hl = (250, 200, 80, 255)

# Wax (pale yellow)
WXd = (180, 170, 120, 255)
WX  = (210, 200, 150, 255)
WXl = (235, 225, 180, 255)

# Metal
Md = (60, 65, 70, 255)
M  = (100, 105, 110, 255)
Ml = (150, 155, 160, 255)


def create_sprite_from_grid(grid):
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0
    img = Image.new('RGBA', (width, height), T)
    pixels = img.load()
    for y, row in enumerate(grid):
        for x, color in enumerate(row):
            pixels[x, y] = color
    return img


# =============================================================================
# BEEKEEPING
# =============================================================================

def build_beehive_basic():
    """Basic beehive: 16x20 (1x1 footprint) - 3/4 perspective box hive"""
    grid = [[T] * 16 for _ in range(20)]

    # === ROOF (horizontal top) - rows 0-4 ===
    for y in range(0, 4):
        for x in range(1, 15):
            if x < 5:
                grid[y][x] = Wl  # Left - lit
            elif x < 11:
                grid[y][x] = W   # Center
            else:
                grid[y][x] = Wd  # Right - shadow

    # Roof top edge
    for x in range(1, 15):
        grid[0][x] = Wl

    # === MAIN BOX (front face, darker) - rows 4-18 ===
    for y in range(4, 18):
        for x in range(2, 14):
            if x < 5:
                grid[y][x] = W   # Left - less dark
            elif x < 11:
                grid[y][x] = Wd  # Center
            else:
                grid[y][x] = Wd  # Right - dark

    # Edge between roof and box
    for x in range(2, 14):
        grid[4][x] = Wd

    # Entrance hole
    grid[14][7] = (30, 25, 20, 255)
    grid[14][8] = (30, 25, 20, 255)
    grid[15][7] = (30, 25, 20, 255)
    grid[15][8] = (30, 25, 20, 255)

    # Base
    for x in range(3, 13):
        grid[18][x] = Wd
        grid[19][x] = Wd

    return grid


def build_beehive_medium():
    """Medium beehive: 32x24 (2x1 footprint) - 3/4 perspective langstroth style"""
    grid = [[T] * 32 for _ in range(24)]

    # === ROOF (horizontal top) - rows 0-5 ===
    for y in range(0, 5):
        for x in range(2, 30):
            if x < 10:
                grid[y][x] = Wl  # Left - lit
            elif x < 22:
                grid[y][x] = W   # Center
            else:
                grid[y][x] = Wd  # Right - shadow

    # Roof top edge
    for x in range(2, 30):
        grid[0][x] = Wl

    # === TWO STACKED BOXES (front face) - rows 5-22 ===
    for y in range(5, 22):
        for x in range(4, 28):
            if x < 10:
                grid[y][x] = W   # Left - less dark
            elif x < 22:
                grid[y][x] = Wd  # Center
            else:
                grid[y][x] = Wd  # Right - dark

    # Edge between roof and box
    for x in range(4, 28):
        grid[5][x] = Wd

    # Dividing line between boxes
    for x in range(4, 28):
        grid[13][x] = Wd

    # Entrance
    for x in range(14, 18):
        grid[19][x] = (30, 25, 20, 255)
        grid[20][x] = (30, 25, 20, 255)

    # Base
    for x in range(6, 26):
        grid[22][x] = Wd
        grid[23][x] = Wd

    return grid


def build_beehive_large():
    """Large beehive: 32x28 (2x2 footprint) - 3/4 perspective multi-story"""
    grid = [[T] * 32 for _ in range(28)]

    # === ROOF (horizontal top) - rows 0-5 ===
    for y in range(0, 5):
        for x in range(2, 30):
            if x < 10:
                grid[y][x] = Wl
            elif x < 22:
                grid[y][x] = W
            else:
                grid[y][x] = Wd

    # Roof top edge
    for x in range(2, 30):
        grid[0][x] = Wl

    # === THREE STACKED BOXES (front face) - rows 5-26 ===
    for y in range(5, 26):
        for x in range(4, 28):
            if x < 10:
                grid[y][x] = W
            elif x < 22:
                grid[y][x] = Wd
            else:
                grid[y][x] = Wd

    # Edge between roof and box
    for x in range(4, 28):
        grid[5][x] = Wd

    # Dividing lines
    for x in range(4, 28):
        grid[12][x] = Wd
        grid[18][x] = Wd

    # Entrance
    for x in range(14, 18):
        grid[22][x] = (30, 25, 20, 255)
        grid[23][x] = (30, 25, 20, 255)

    # Base
    for x in range(6, 26):
        grid[26][x] = Wd
        grid[27][x] = Wd

    return grid


def build_beehive_deluxe():
    """Deluxe beehive: 32x32 (2x2 footprint) - 3/4 perspective ornate"""
    grid = [[T] * 32 for _ in range(32)]

    # === ORNATE ROOF with peak - rows 0-7 ===
    for y in range(0, 8):
        width = 14 - y
        for x in range(16 - width, 16 + width):
            if 0 <= x < 32:
                if x < 12:
                    grid[y][x] = Wl
                elif x < 20:
                    grid[y][x] = W
                else:
                    grid[y][x] = Wd

    # Roof top edge
    for x in range(4, 28):
        if grid[0][x] != T:
            grid[0][x] = Wl

    # === MAIN BODY (front face) - rows 8-28 ===
    for y in range(8, 28):
        for x in range(4, 28):
            if x < 10:
                grid[y][x] = W
            elif x < 22:
                grid[y][x] = Wd
            else:
                grid[y][x] = Wd

    # Edge between roof and body
    for x in range(4, 28):
        grid[8][x] = Wd

    # Decorative bands
    for x in range(4, 28):
        grid[14][x] = Hl  # Honey-colored accent
        grid[22][x] = Hl

    # Gold trim entrance
    for x in range(13, 19):
        grid[24][x] = H
        grid[25][x] = (30, 25, 20, 255)
        grid[26][x] = (30, 25, 20, 255)

    # Base (fancier)
    for x in range(6, 26):
        grid[28][x] = W
        grid[29][x] = Wd
        grid[30][x] = Wd
        grid[31][x] = Wd

    return grid


def build_honey_extractor():
    """Honey extractor: 32x32 (2x2 footprint) - 3/4 perspective metal drum"""
    grid = [[T] * 32 for _ in range(32)]

    # === LID (horizontal top) - rows 0-5 ===
    for y in range(0, 5):
        for x in range(8, 24):
            if x < 12:
                grid[y][x] = Ml  # Left - lit
            elif x < 20:
                grid[y][x] = M   # Center
            else:
                grid[y][x] = Md  # Right - shadow

    # Lid top edge
    for x in range(8, 24):
        grid[0][x] = Ml

    # Handle on top
    for x in range(14, 18):
        grid[0][x] = M
        grid[1][x] = Md

    # === CYLINDRICAL BODY (front face) - rows 5-28 ===
    for y in range(5, 28):
        radius = 10 if 10 < y < 24 else 8

        for x in range(32):
            dx = abs(x - 16)
            if dx <= radius:
                # Left-right shading
                if x < 10:
                    grid[y][x] = M   # Left - some light
                elif x < 22:
                    grid[y][x] = Md  # Center-right - dark
                else:
                    grid[y][x] = Md  # Right - dark

    # Edge between lid and body
    for x in range(8, 24):
        grid[5][x] = Md

    # Spout at bottom
    for y in range(24, 30):
        grid[y][20] = M
        grid[y][21] = Md

    # Legs
    for y in range(26, 32):
        grid[y][8] = M; grid[y][9] = Md
        grid[y][22] = M; grid[y][23] = Md

    return grid


# =============================================================================
# STRUCTURES
# =============================================================================

def build_signpost():
    """Signpost: 16x24 (1x1 footprint) - 3/4 perspective"""
    grid = [[T] * 16 for _ in range(24)]

    # Sign board (front face, left-right shading)
    for y in range(2, 10):
        for x in range(2, 14):
            if x < 6:
                grid[y][x] = Wl
            elif x < 10:
                grid[y][x] = W
            else:
                grid[y][x] = Wd

    # Top edge of sign
    for x in range(2, 14):
        grid[2][x] = Wl

    # Post
    for y in range(10, 24):
        grid[y][7] = Wl
        grid[y][8] = W
        grid[y][9] = Wd

    return grid


def build_well():
    """Well: 32x32 (2x2 footprint) - 3/4 perspective stone well with roof"""
    grid = [[T] * 32 for _ in range(32)]

    # === ROOF (horizontal top) - rows 0-5 ===
    for y in range(0, 5):
        width = 14 - y
        for x in range(16 - width, 16 + width):
            if 0 <= x < 32:
                if x < 12:
                    grid[y][x] = Wl
                elif x < 20:
                    grid[y][x] = W
                else:
                    grid[y][x] = Wd

    # Roof top edge
    for x in range(4, 28):
        if grid[0][x] != T:
            grid[0][x] = Wl

    # Posts
    for y in range(4, 16):
        grid[y][6] = Wl; grid[y][7] = W
        grid[y][24] = W; grid[y][25] = Wd

    # === STONE BASE (circular, front face) - rows 12-28 ===
    for y in range(12, 28):
        for x in range(32):
            dx, dy = x - 16, y - 20
            dist = (dx * dx + dy * dy) ** 0.5

            if dist <= 10:
                if dist > 7:
                    # Left-right shading for stone rim
                    if x < 12:
                        grid[y][x] = Sl
                    elif x < 20:
                        grid[y][x] = S
                    else:
                        grid[y][x] = Sd
                else:
                    # Dark water inside
                    grid[y][x] = (30, 50, 70, 255)

    # Bucket/rope (simple)
    grid[8][16] = M
    for y in range(9, 14):
        grid[y][16] = (80, 70, 50, 255)  # Rope

    # Base stones
    for x in range(6, 26):
        grid[28][x] = Sd
        grid[29][x] = Sd
        grid[30][x] = Sd
        grid[31][x] = Sd

    return grid


def build_bridge_wood():
    """Wooden bridge: 32x32 (2x2 footprint) - 3/4 perspective"""
    grid = [[T] * 32 for _ in range(32)]

    # Bridge planks (horizontal surface, left-right shading)
    for y in range(8, 24):
        for x in range(32):
            plank = y // 4
            if plank % 2 == 0:
                if x < 10:
                    grid[y][x] = Wl
                elif x < 22:
                    grid[y][x] = W
                else:
                    grid[y][x] = Wd
            else:
                if x < 12:
                    grid[y][x] = W
                else:
                    grid[y][x] = Wd

    # Plank gaps
    for x in range(32):
        grid[11][x] = Wd
        grid[15][x] = Wd
        grid[19][x] = Wd

    # Railings
    for x in range(32):
        grid[6][x] = W
        grid[7][x] = Wd
        grid[24][x] = W
        grid[25][x] = Wd

    # Support posts at edges
    for y in range(6, 28):
        grid[y][2] = Wl; grid[y][3] = W
        grid[y][28] = W; grid[y][29] = Wd

    return grid


def build_bridge_stone():
    """Stone bridge: 32x32 (2x2 footprint) - 3/4 perspective"""
    grid = [[T] * 32 for _ in range(32)]

    # Bridge surface (horizontal, left-right shading)
    for y in range(8, 24):
        for x in range(32):
            if x < 10:
                grid[y][x] = Sl
            elif x < 22:
                grid[y][x] = S
            else:
                grid[y][x] = Sd

    # Stone pattern
    for y in range(8, 24, 4):
        for x in range(32):
            grid[y][x] = Sd

    for x in range(0, 32, 6):
        for y in range(8, 24):
            if 0 <= x < 32:
                grid[y][x] = Sd

    # Low walls
    for x in range(32):
        for y in range(4, 8):
            grid[y][x] = S if x < 16 else Sd
        for y in range(24, 28):
            grid[y][x] = S if x < 16 else Sd

    # Arch supports at edges
    for y in range(4, 32):
        grid[y][0] = Sd; grid[y][1] = S
        grid[y][30] = S; grid[y][31] = Sd

    return grid


def main():
    # Beekeeping sprites
    beekeeping_dir = "/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Sprites/Beekeeping"
    os.makedirs(beekeeping_dir, exist_ok=True)

    beekeeping_sprites = [
        ("beehive_basic.png", build_beehive_basic()),
        ("beehive_medium.png", build_beehive_medium()),
        ("beehive_large.png", build_beehive_large()),
        ("beehive_deluxe.png", build_beehive_deluxe()),
        ("honey_extractor.png", build_honey_extractor()),
    ]

    for filename, grid in beekeeping_sprites:
        img = create_sprite_from_grid(grid)
        path = f"{beekeeping_dir}/{filename}"
        img.save(path)
        print(f"Created: {path} ({img.size[0]}x{img.size[1]})")

    # Structure sprites
    structures_dir = "/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Sprites/Structures"
    os.makedirs(structures_dir, exist_ok=True)

    structure_sprites = [
        ("signpost.png", build_signpost()),
        ("well.png", build_well()),
        ("bridge_wood.png", build_bridge_wood()),
        ("bridge_stone.png", build_bridge_stone()),
    ]

    for filename, grid in structure_sprites:
        img = create_sprite_from_grid(grid)
        path = f"{structures_dir}/{filename}"
        img.save(path)
        print(f"Created: {path} ({img.size[0]}x{img.size[1]})")

    print(f"\nGenerated {len(beekeeping_sprites)} beekeeping + {len(structure_sprites)} structure sprites")
    print("\nUnity import settings:")
    print("  - Pixels Per Unit: 16")
    print("  - Filter Mode: Point (no filter)")
    print("  - Compression: None")


if __name__ == "__main__":
    main()
