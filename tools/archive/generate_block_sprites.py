#!/usr/bin/env python3
"""Generate 3D block sprites (Minecraft-style cubes) for Bug Farmer.

Design principles from sprite_guidelines.md:
- 45-degree top-down perspective (see top + front face)
- Light source: top-left
- 3-5 colors per material using guide palettes
- No pure black outlines
- Thickness: 55-65% top, 25-35% front
- Texture: clustered patterns, not random noise

Block structure (16x20):
- Rows 0-12: Top face (13px = 65%, lit, horizontal surface)
- Rows 13-19: Front face (7px = 35%, darker, vertical surface)
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


def build_solid_block(material, texture_type='smooth'):
    """Build a 16x20 solid block (dirt, stone, clay) - 3/4 perspective.

    Top face (rows 0-12): HORIZONTAL surface, 13px = 65%
    Front face (rows 13-19): VERTICAL surface, 7px = 35%
    texture_type: 'smooth', 'dirt_strata', 'stone_cluster'
    """
    d, b, l = material['dark'], material['base'], material['light']
    grid = [[T] * 16 for _ in range(20)]

    # Top face (rows 0-12) - 13px, horizontal surface viewed from above
    # Base fill with left-right gradient
    for y in range(13):
        for x in range(16):
            if x < 5:
                grid[y][x] = l   # Left - lit
            elif x < 11:
                grid[y][x] = b   # Center - base
            else:
                grid[y][x] = d   # Right - shadow

    # Top edge highlight (row 0)
    for x in range(16):
        grid[0][x] = l

    # Apply texture patterns on top face
    if texture_type == 'dirt_strata':
        # Horizontal strata bands with pebble clusters
        strata_rows = [3, 7, 10]
        for row in strata_rows:
            for x in range(0, 16, 3):
                if x + 1 < 16:
                    grid[row][x] = d
                    grid[row][x + 1] = d
        # Pebble clusters
        pebble_clusters = [(2, 5), (8, 2), (12, 8), (5, 10)]
        for px, py in pebble_clusters:
            if py < 13:
                grid[py][px] = d
                if px + 1 < 16:
                    grid[py][px + 1] = d

    elif texture_type == 'stone_cluster':
        # Clustered noise pattern for stone
        cluster_centers = [(3, 3), (10, 5), (6, 9), (13, 10)]
        for cx, cy in cluster_centers:
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < 16 and 0 <= ny < 13:
                        # Vary shade within cluster
                        if dx == 0 and dy == 0:
                            grid[ny][nx] = d
                        elif abs(dx) + abs(dy) == 1:
                            grid[ny][nx] = b if grid[ny][nx] == l else d

    # Front face (rows 13-19) - 7px, vertical surface, darker overall
    # Much darker than top to show strong plane contrast
    darker = (max(0, d[0] - 25), max(0, d[1] - 25), max(0, d[2] - 25), 255)
    for y in range(13, 20):
        for x in range(16):
            if x < 3:
                grid[y][x] = d  # Left edge catches some reflected light
            else:
                grid[y][x] = darker  # Rest is deep shadow

    # Edge line between top and front (row 12) - strong contrast
    for x in range(16):
        grid[12][x] = darker

    # Ground contact - bottom row extra dark
    bottom_dark = (max(0, d[0] - 35), max(0, d[1] - 35), max(0, d[2] - 35), 255)
    for x in range(16):
        grid[19][x] = bottom_dark

    return grid


def build_ore_block(stone_mat, ore_mat, ore_density='medium'):
    """Build a 16x20 ore block (stone with ore veins) - 3/4 perspective.

    Stone base with ore material veins (clustered, not scattered).
    Top face: rows 0-12 (13px = 65%)
    Front face: rows 13-19 (7px = 35%)
    ore_density: 'low', 'medium', 'high'
    """
    sd, sb, sl = stone_mat['dark'], stone_mat['base'], stone_mat['light']
    od, ob, ol = ore_mat['dark'], ore_mat['base'], ore_mat['light']

    # Start with solid stone block base
    grid = [[T] * 16 for _ in range(20)]

    # Top face (rows 0-12) - 13px with clustered stone texture
    for y in range(13):
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

    # Add stone texture clusters on top
    stone_clusters = [(2, 4), (9, 6), (13, 3)]
    for cx, cy in stone_clusters:
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < 16 and 0 <= ny < 13:
                    if dx == 0 and dy == 0:
                        grid[ny][nx] = sd

    # Front face (rows 13-19) - 7px, much darker for plane contrast
    darker = (max(0, sd[0] - 25), max(0, sd[1] - 25), max(0, sd[2] - 25), 255)
    for y in range(13, 20):
        for x in range(16):
            if x < 3:
                grid[y][x] = sd  # Left edge reflects some light
            else:
                grid[y][x] = darker

    # Edge line between top and front
    for x in range(16):
        grid[12][x] = darker

    # Ground contact - extra dark bottom
    bottom_dark = (max(0, sd[0] - 35), max(0, sd[1] - 35), max(0, sd[2] - 35), 255)
    for x in range(16):
        grid[19][x] = bottom_dark

    # Define ore vein clusters (connected, not scattered spots)
    if ore_density == 'low':
        # One small vein cluster on top, one on front
        ore_veins_top = [
            [(5, 4), (6, 4), (6, 5), (7, 5)],  # L-shaped vein
        ]
        ore_veins_front = [
            [(7, 15), (8, 15)],  # Small cluster
        ]
    elif ore_density == 'medium':
        # Two vein clusters on top, one on front
        ore_veins_top = [
            [(3, 3), (4, 3), (4, 4), (5, 4)],  # Diagonal vein
            [(10, 7), (11, 7), (11, 8), (10, 8)],  # Square cluster
        ]
        ore_veins_front = [
            [(5, 14), (6, 14), (5, 15)],  # L-shape
        ]
    else:  # high
        # Large connected vein across top
        ore_veins_top = [
            [(2, 2), (3, 2), (3, 3), (4, 3), (4, 4)],  # Main diagonal vein
            [(8, 5), (9, 5), (9, 6), (10, 6), (10, 7), (11, 7)],  # Second vein
            [(5, 9), (6, 9), (6, 10), (7, 10)],  # Third cluster
        ]
        ore_veins_front = [
            [(4, 14), (5, 14), (5, 15), (6, 15)],  # Front vein
            [(10, 16), (11, 16)],  # Small cluster
        ]

    # Draw ore veins on top face with proper lighting
    for vein in ore_veins_top:
        for i, (ox, oy) in enumerate(vein):
            if 0 <= ox < 16 and 0 <= oy < 13:
                # First pixel in vein is lit, last is dark, middle is base
                if i == 0:
                    grid[oy][ox] = ol
                elif i == len(vein) - 1:
                    grid[oy][ox] = od
                else:
                    grid[oy][ox] = ob

    # Draw ore veins on front face (darker overall)
    for vein in ore_veins_front:
        for i, (ox, oy) in enumerate(vein):
            if 0 <= ox < 16 and 13 <= oy < 20:
                # Front face ore is darker
                if i == 0:
                    grid[oy][ox] = ob
                else:
                    grid[oy][ox] = od

    return grid


def main():
    output_dir = "/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Sprites/Blocks"
    os.makedirs(output_dir, exist_ok=True)

    sprites = []

    # Solid blocks with appropriate textures
    sprites.append(("dirt_block.png", build_solid_block(DIRT, 'dirt_strata')))
    sprites.append(("stone_block.png", build_solid_block(STONE, 'stone_cluster')))
    sprites.append(("clay_block.png", build_solid_block(CLAY, 'smooth')))

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
