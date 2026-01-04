#!/usr/bin/env python3
"""Generate tool sprites (16x16) for Bug Farmer.

Design principles:
- 45-degree angle for dynamic look
- Handle and head clearly distinct
- Material colors indicate tier
- Light source: top-left

Tool types: Axes, Pickaxes, Shovels, Hoes, Bug Nets
Tiers: Wood, Stone, Copper, Iron, Steel, Silver, Gold, Platinum, Diamond
"""

from PIL import Image
import os

# Colors (RGBA)
T = (0, 0, 0, 0)  # Transparent

# Handle (wood) - all tools use wood handles
Hd = (70, 50, 35, 255)     # Handle dark
H  = (120, 90, 60, 255)    # Handle base
Hl = (160, 130, 95, 255)   # Handle light

# Material palettes: (dark, base, light)
MATERIALS = {
    "wood":     ((70, 50, 35),   (120, 90, 60),   (160, 130, 95)),
    "stone":    ((85, 85, 90),   (120, 120, 125), (155, 155, 160)),
    "copper":   ((140, 80, 50),  (180, 110, 70),  (210, 150, 100)),
    "iron":     ((60, 65, 70),   (100, 105, 110), (150, 155, 160)),
    "steel":    ((70, 75, 85),   (120, 125, 135), (170, 175, 185)),
    "silver":   ((140, 140, 150),(180, 180, 190), (220, 220, 230)),
    "gold":     ((180, 140, 40), (230, 190, 60),  (255, 220, 100)),
    "platinum": ((160, 165, 175),(200, 205, 215), (235, 240, 250)),
    "diamond":  ((80, 180, 200), (120, 220, 240), (180, 245, 255)),
}

# Net colors (for bug nets)
Nt = (220, 220, 230, 200)  # Net mesh (semi-transparent)
Nr = (80, 140, 80, 255)    # Net rim (green)
Nd = (60, 110, 60, 255)    # Net rim dark


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


def build_axe(material):
    """Axe: 16x16 - angled 45°, blade top-right, handle bottom-left"""
    md, m, ml = [(c[0], c[1], c[2], 255) for c in MATERIALS[material]]
    grid = [[T] * 16 for _ in range(16)]

    # Blade (top-right, angled)
    # Row 0-1: blade tip
    grid[0][11] = ml; grid[0][12] = ml
    grid[1][10] = ml; grid[1][11] = m; grid[1][12] = m; grid[1][13] = ml
    # Row 2-4: blade body
    grid[2][9] = md; grid[2][10] = m; grid[2][11] = m; grid[2][12] = m; grid[2][13] = ml
    grid[3][8] = md; grid[3][9] = m; grid[3][10] = m; grid[3][11] = m; grid[3][12] = ml
    grid[4][7] = md; grid[4][8] = m; grid[4][9] = m; grid[4][10] = m; grid[4][11] = ml
    # Row 5: blade-handle junction
    grid[5][6] = md; grid[5][7] = m; grid[5][8] = m; grid[5][9] = ml

    # Handle (diagonal from junction to bottom-left)
    for i in range(10):
        y = 6 + i
        x = 5 - (i // 2)
        if 0 <= x < 16 and 0 <= y < 16:
            grid[y][x] = Hd
            if x + 1 < 16:
                grid[y][x + 1] = H if i < 8 else Hl

    return grid


def build_pickaxe(material):
    """Pickaxe: 16x16 - horizontal head, vertical handle"""
    md, m, ml = [(c[0], c[1], c[2], 255) for c in MATERIALS[material]]
    grid = [[T] * 16 for _ in range(16)]

    # Pickaxe head (horizontal, slightly curved)
    # Left pick
    grid[1][2] = md; grid[1][3] = m
    grid[2][1] = md; grid[2][2] = m; grid[2][3] = m
    grid[3][2] = md; grid[3][3] = m; grid[3][4] = m
    # Center/mount
    grid[3][5] = md; grid[3][6] = m; grid[3][7] = m; grid[3][8] = m; grid[3][9] = m; grid[3][10] = ml
    grid[4][6] = md; grid[4][7] = m; grid[4][8] = m; grid[4][9] = ml
    # Right pick
    grid[2][11] = m; grid[2][12] = m; grid[2][13] = ml
    grid[1][12] = m; grid[1][13] = ml
    grid[3][11] = m; grid[3][12] = ml

    # Handle (vertical, centered)
    for y in range(5, 16):
        grid[y][7] = Hd
        grid[y][8] = H if y < 14 else Hl

    return grid


def build_shovel(material):
    """Shovel: 16x16 - spade head at bottom, handle up"""
    md, m, ml = [(c[0], c[1], c[2], 255) for c in MATERIALS[material]]
    grid = [[T] * 16 for _ in range(16)]

    # Handle (top portion)
    for y in range(0, 8):
        grid[y][7] = Hd
        grid[y][8] = H if y < 6 else Hl

    # Shaft collar
    grid[8][6] = md; grid[8][7] = m; grid[8][8] = m; grid[8][9] = ml

    # Spade head (rounded)
    grid[9][5] = md; grid[9][6] = m; grid[9][7] = m; grid[9][8] = m; grid[9][9] = m; grid[9][10] = ml
    grid[10][4] = md; grid[10][5] = m; grid[10][6] = m; grid[10][7] = m; grid[10][8] = m; grid[10][9] = m; grid[10][10] = ml
    grid[11][4] = md; grid[11][5] = m; grid[11][6] = m; grid[11][7] = m; grid[11][8] = m; grid[11][9] = m; grid[11][10] = ml
    grid[12][4] = md; grid[12][5] = m; grid[12][6] = m; grid[12][7] = m; grid[12][8] = m; grid[12][9] = m; grid[12][10] = ml
    grid[13][5] = md; grid[13][6] = m; grid[13][7] = m; grid[13][8] = m; grid[13][9] = ml
    grid[14][6] = md; grid[14][7] = m; grid[14][8] = m; grid[14][9] = ml
    grid[15][7] = md; grid[15][8] = ml

    return grid


def build_hoe(material):
    """Hoe: 16x16 - flat blade, angled"""
    md, m, ml = [(c[0], c[1], c[2], 255) for c in MATERIALS[material]]
    grid = [[T] * 16 for _ in range(16)]

    # Hoe blade (flat, horizontal at top)
    grid[2][3] = md; grid[2][4] = m; grid[2][5] = m; grid[2][6] = m; grid[2][7] = m
    grid[2][8] = m; grid[2][9] = m; grid[2][10] = m; grid[2][11] = ml
    grid[3][4] = md; grid[3][5] = m; grid[3][6] = m; grid[3][7] = m
    grid[3][8] = m; grid[3][9] = m; grid[3][10] = ml

    # Handle mount
    grid[4][7] = md; grid[4][8] = m

    # Handle (diagonal going down-left)
    for i in range(11):
        y = 5 + i
        x = 7 - (i // 2)
        if 0 <= x < 16 and 0 <= y < 16:
            grid[y][x] = Hd
            if x + 1 < 16:
                grid[y][x + 1] = H if i < 9 else Hl

    return grid


def build_bugnet(tier):
    """Bug net: 16x16 - net hoop at top, long handle"""
    # Net rim color varies slightly by tier (nicer materials = nicer rim)
    tier_idx = list(MATERIALS.keys()).index(tier) if tier in MATERIALS else 0
    rim_green = 80 + tier_idx * 8
    rim_r = (60 + tier_idx * 6, 110 + tier_idx * 6, 60 + tier_idx * 4, 255)
    rim = (rim_green, 140 + tier_idx * 5, rim_green, 255)

    grid = [[T] * 16 for _ in range(16)]

    # Net hoop (oval)
    grid[0][5] = rim; grid[0][6] = rim; grid[0][7] = rim; grid[0][8] = rim; grid[0][9] = rim; grid[0][10] = rim
    grid[1][4] = rim; grid[1][5] = Nt; grid[1][6] = Nt; grid[1][7] = Nt; grid[1][8] = Nt; grid[1][9] = Nt; grid[1][10] = Nt; grid[1][11] = rim
    grid[2][3] = rim; grid[2][4] = Nt; grid[2][5] = Nt; grid[2][6] = Nt; grid[2][7] = Nt; grid[2][8] = Nt; grid[2][9] = Nt; grid[2][10] = Nt; grid[2][11] = Nt; grid[2][12] = rim
    grid[3][3] = rim; grid[3][4] = Nt; grid[3][5] = Nt; grid[3][6] = Nt; grid[3][7] = Nt; grid[3][8] = Nt; grid[3][9] = Nt; grid[3][10] = Nt; grid[3][11] = Nt; grid[3][12] = rim
    grid[4][3] = rim; grid[4][4] = Nt; grid[4][5] = Nt; grid[4][6] = Nt; grid[4][7] = Nt; grid[4][8] = Nt; grid[4][9] = Nt; grid[4][10] = Nt; grid[4][11] = Nt; grid[4][12] = rim
    grid[5][4] = rim_r; grid[5][5] = rim; grid[5][6] = rim; grid[5][7] = rim; grid[5][8] = rim; grid[5][9] = rim; grid[5][10] = rim; grid[5][11] = rim_r

    # Handle attachment
    grid[6][7] = Hd; grid[6][8] = H

    # Handle (vertical)
    for y in range(7, 16):
        grid[y][7] = Hd
        grid[y][8] = H if y < 14 else Hl

    return grid


def main():
    output_dir = "/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Resources/Items"
    os.makedirs(output_dir, exist_ok=True)

    tools_generated = []

    # Generate all tiers for each tool type
    for material in MATERIALS.keys():
        # Axe
        grid = build_axe(material)
        filename = f"axe_{material}.png"
        img = create_sprite_from_grid(grid)
        img.save(f"{output_dir}/{filename}")
        tools_generated.append(filename)

        # Pickaxe
        grid = build_pickaxe(material)
        filename = f"pickaxe_{material}.png"
        img = create_sprite_from_grid(grid)
        img.save(f"{output_dir}/{filename}")
        tools_generated.append(filename)

        # Shovel
        grid = build_shovel(material)
        filename = f"shovel_{material}.png"
        img = create_sprite_from_grid(grid)
        img.save(f"{output_dir}/{filename}")
        tools_generated.append(filename)

        # Hoe
        grid = build_hoe(material)
        filename = f"hoe_{material}.png"
        img = create_sprite_from_grid(grid)
        img.save(f"{output_dir}/{filename}")
        tools_generated.append(filename)

        # Bug net
        grid = build_bugnet(material)
        filename = f"bugnet_{material}.png"
        img = create_sprite_from_grid(grid)
        img.save(f"{output_dir}/{filename}")
        tools_generated.append(filename)

    print(f"Created {len(tools_generated)} tool sprites:")
    for i, name in enumerate(tools_generated):
        if i % 5 == 0:
            print(f"  {name.replace('.png', '')}", end="")
        if (i + 1) % 5 == 0:
            print()

    print(f"\nOutput: {output_dir}")
    print("\nUnity import settings:")
    print("  - Pixels Per Unit: 16")
    print("  - Filter Mode: Point (no filter)")
    print("  - Compression: None")


if __name__ == "__main__":
    main()
