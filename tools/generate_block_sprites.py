#!/usr/bin/env python3
"""Generate 3D block sprites (Minecraft-style cubes) for Bug Farmer.

Design principles from SPRITE_GENERATION_GUIDE.md:
- 45-degree top-down perspective (see top + front face)
- Light source: top-left
- 3-5 colors per material using guide palettes
- No pure black outlines

Block structure (16x20):
- Rows 0-11: Top face (lit, visible from above)
- Rows 12-19: Front face (darker, vertical surface)
- Light falls top-left, shadows bottom-right
"""

from PIL import Image
import os

# Colors (RGBA) - from SPRITE_GENERATION_GUIDE.md
T = (0, 0, 0, 0)  # Transparent

# Dirt - from guide
DIRT = {
    'dark':  (110, 75, 40, 255),
    'base':  (140, 95, 50, 255),
    'light': (165, 120, 70, 255),
}

# Stone - from guide
STONE = {
    'dark':  (85, 85, 90, 255),
    'base':  (120, 120, 125, 255),
    'light': (155, 155, 160, 255),
}

# Copper - from guide
COPPER = {
    'dark':  (140, 80, 50, 255),
    'base':  (180, 110, 70, 255),
    'light': (210, 150, 100, 255),
}

# Gold - from guide
GOLD = {
    'dark':  (180, 140, 40, 255),
    'base':  (230, 190, 60, 255),
    'light': (255, 220, 100, 255),
}

# Iron/Steel - from guide
IRON = {
    'dark':  (60, 65, 70, 255),
    'base':  (100, 105, 110, 255),
    'light': (150, 155, 160, 255),
}

# Coal - dark with slight blue tint
COAL = {
    'dark':  (25, 25, 30, 255),
    'base':  (45, 45, 50, 255),
    'light': (70, 70, 75, 255),
}

# Silver - bright metallic gray
SILVER = {
    'dark':  (140, 140, 150, 255),
    'base':  (180, 180, 190, 255),
    'light': (220, 220, 230, 255),
}

# Platinum - blue-tinted silver
PLATINUM = {
    'dark':  (160, 165, 175, 255),
    'base':  (200, 205, 215, 255),
    'light': (235, 240, 250, 255),
}

# Diamond - cyan/blue crystal
DIAMOND = {
    'dark':  (80, 180, 200, 255),
    'base':  (120, 220, 240, 255),
    'light': (180, 245, 255, 255),
}

# Clay - gray-brown
CLAY = {
    'dark':  (100, 90, 85, 255),
    'base':  (140, 125, 115, 255),
    'light': (170, 155, 145, 255),
}


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


def build_solid_block(material):
    """Build a 16x20 solid block (dirt, stone, clay) - 3/4 perspective.

    Top face (rows 0-11): HORIZONTAL surface, left-right shading
    Front face (rows 12-19): VERTICAL surface, darker with left-right shading
    """
    d, b, l = material['dark'], material['base'], material['light']
    grid = [[T] * 16 for _ in range(20)]

    # Top face (rows 0-11) - horizontal surface viewed from above
    # Left-right shading: left=light, right=shadow
    for y in range(12):
        for x in range(16):
            if x < 5:
                grid[y][x] = l   # Left - lit
            elif x < 11:
                grid[y][x] = b   # Center - base
            else:
                grid[y][x] = d   # Right - shadow

    # Top edge highlight
    for x in range(16):
        grid[0][x] = l

    # Front face (rows 12-19) - vertical surface, darker
    # Left-right shading (left catches some light)
    for y in range(12, 20):
        for x in range(16):
            if x < 4:
                grid[y][x] = b  # Left edge catches some light
            elif x < 12:
                grid[y][x] = d  # Middle is dark
            else:
                # Far right is very dark
                darker = (max(0, d[0]-20), max(0, d[1]-20), max(0, d[2]-20), 255)
                grid[y][x] = darker

    # Edge between top and front (row 11-12 transition)
    for x in range(16):
        grid[11][x] = d  # Dark line at edge

    return grid


def build_ore_block(stone_mat, ore_mat, ore_density='medium'):
    """Build a 16x20 ore block (stone with ore veins) - 3/4 perspective.

    Stone base with ore material spots/veins.
    ore_density: 'low', 'medium', 'high'
    """
    sd, sb, sl = stone_mat['dark'], stone_mat['base'], stone_mat['light']
    od, ob, ol = ore_mat['dark'], ore_mat['base'], ore_mat['light']

    # Start with solid stone block
    grid = [[T] * 16 for _ in range(20)]

    # Top face (rows 0-11) - left-right shading
    for y in range(12):
        for x in range(16):
            if x < 5:
                grid[y][x] = sl   # Left - lit
            elif x < 11:
                grid[y][x] = sb   # Center
            else:
                grid[y][x] = sd   # Right - shadow

    # Top edge highlight
    for x in range(16):
        grid[0][x] = sl

    # Front face (rows 12-19) - darker with left-right shading
    for y in range(12, 20):
        for x in range(16):
            if x < 4:
                grid[y][x] = sb
            elif x < 12:
                grid[y][x] = sd
            else:
                darker = (max(0, sd[0]-20), max(0, sd[1]-20), max(0, sd[2]-20), 255)
                grid[y][x] = darker

    # Edge
    for x in range(16):
        grid[11][x] = sd

    # Add ore deposits based on density
    if ore_density == 'low':
        # 2 small spots on top face
        ore_spots_top = [(4, 3), (10, 7)]
        ore_spots_front = [(6, 14)]
    elif ore_density == 'medium':
        # 3-4 spots
        ore_spots_top = [(3, 2), (9, 4), (5, 8), (11, 6)]
        ore_spots_front = [(4, 14), (10, 16)]
    else:  # high
        # More prominent ore
        ore_spots_top = [(2, 2), (6, 3), (10, 2), (4, 6), (8, 7), (12, 5), (6, 9)]
        ore_spots_front = [(3, 13), (7, 15), (11, 14), (5, 17)]

    # Draw ore on top face (2x2 pixel spots with lighting)
    for (ox, oy) in ore_spots_top:
        if oy < 12:  # Top face
            for dy in range(2):
                for dx in range(2):
                    nx, ny = ox + dx, oy + dy
                    if 0 <= nx < 16 and 0 <= ny < 12:
                        # Light direction on ore
                        if dx == 0 and dy == 0:
                            grid[ny][nx] = ol
                        elif dx == 1 and dy == 1:
                            grid[ny][nx] = od
                        else:
                            grid[ny][nx] = ob

    # Draw ore on front face (2x2 pixel spots, darker)
    for (ox, oy) in ore_spots_front:
        if oy >= 12:  # Front face
            for dy in range(2):
                for dx in range(2):
                    nx, ny = ox + dx, oy + dy
                    if 0 <= nx < 16 and 12 <= ny < 20:
                        # Front face ore is darker overall
                        if dx == 0:
                            grid[ny][nx] = ob
                        else:
                            grid[ny][nx] = od

    return grid


def main():
    output_dir = "/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Sprites/Blocks"
    os.makedirs(output_dir, exist_ok=True)

    sprites = []

    # Solid blocks
    sprites.append(("dirt_block.png", build_solid_block(DIRT)))
    sprites.append(("stone_block.png", build_solid_block(STONE)))
    sprites.append(("clay_block.png", build_solid_block(CLAY)))

    # Ore blocks (stone + ore veins)
    sprites.append(("ore_coal_block.png", build_ore_block(STONE, COAL, 'high')))
    sprites.append(("ore_copper_block.png", build_ore_block(STONE, COPPER, 'medium')))
    sprites.append(("ore_iron_block.png", build_ore_block(STONE, IRON, 'medium')))
    sprites.append(("ore_silver_block.png", build_ore_block(STONE, SILVER, 'medium')))
    sprites.append(("ore_gold_block.png", build_ore_block(STONE, GOLD, 'low')))
    sprites.append(("ore_platinum_block.png", build_ore_block(STONE, PLATINUM, 'low')))
    sprites.append(("ore_diamond_block.png", build_ore_block(STONE, DIAMOND, 'low')))

    for filename, grid in sprites:
        img = create_sprite_from_grid(grid)
        path = f"{output_dir}/{filename}"
        img.save(path)
        print(f"Created: {path} ({img.size[0]}x{img.size[1]})")

    print(f"\nGenerated {len(sprites)} block sprites")
    print("\nUnity import settings:")
    print("  - Pixels Per Unit: 16")
    print("  - Filter Mode: Point (no filter)")
    print("  - Compression: None")
    print("  - Pivot: Bottom Center")


if __name__ == "__main__":
    main()
