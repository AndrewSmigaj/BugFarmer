#!/usr/bin/env python3
"""Generate terrain block sprites (8x8 pixels each) for Bug Farmer.

Design principles:
- Tileable: edges designed to match when repeated
- Simple: clear silhouettes at small size
- Distinct: each terrain type visually unique
"""

from PIL import Image

# Colors (RGBA)
T = (0, 0, 0, 0)  # Transparent

# Grass - lush green with blade hints
G  = (72, 140, 72, 255)    # Grass base
Gl = (95, 165, 85, 255)    # Grass light (blade tips)
Gd = (55, 115, 55, 255)    # Grass dark (shadows)

# Dirt - brown earth
D  = (140, 95, 50, 255)    # Dirt base
Dl = (165, 120, 70, 255)   # Dirt light (pebbles)
Dd = (110, 75, 40, 255)    # Dirt dark (cracks)

# Rock - gray stone with clear lighting
R  = (120, 120, 125, 255)  # Rock base
Rl = (155, 155, 160, 255)  # Rock highlight (top-left)
Rd = (85, 85, 90, 255)     # Rock shadow (bottom-right)
Rm = (100, 100, 105, 255)  # Rock mid

def create_sprite_from_grid(grid):
    """Create an 8x8 image from an 8x8 grid."""
    img = Image.new('RGBA', (8, 8), T)
    pixels = img.load()
    for y, row in enumerate(grid):
        for x, color in enumerate(row):
            pixels[x, y] = color
    return img

# Grass - tileable with subtle blade pattern
# Light pixels suggest grass blade tips catching light
GRASS = [
    [G,  Gl, G,  G,  G,  Gl, G,  G ],
    [G,  G,  G,  Gl, G,  G,  G,  Gl],
    [Gl, G,  G,  G,  G,  G,  Gl, G ],
    [G,  G,  Gd, G,  Gl, G,  G,  G ],
    [G,  Gl, G,  G,  G,  G,  G,  Gl],
    [G,  G,  G,  Gl, G,  Gd, G,  G ],
    [Gl, G,  G,  G,  G,  G,  Gl, G ],
    [G,  G,  Gl, G,  G,  G,  G,  G ],
]

# Dirt - tileable with pebble accents
DIRT = [
    [D,  D,  D,  Dl, D,  D,  D,  D ],
    [D,  Dd, D,  D,  D,  D,  Dl, D ],
    [D,  D,  D,  D,  Dd, D,  D,  D ],
    [D,  D,  Dl, D,  D,  D,  D,  Dd],
    [Dl, D,  D,  D,  D,  Dl, D,  D ],
    [D,  D,  D,  Dd, D,  D,  D,  D ],
    [D,  D,  D,  D,  D,  D,  Dd, D ],
    [D,  Dl, D,  D,  D,  D,  D,  D ],
]

# Rock - solid stone with top-left lighting
# Gradient: light top-left to dark bottom-right
ROCK = [
    [Rl, Rl, Rl, R,  R,  R,  Rm, Rm],
    [Rl, Rl, R,  R,  R,  R,  Rm, Rm],
    [Rl, R,  R,  R,  R,  R,  Rm, Rd],
    [R,  R,  R,  R,  R,  Rm, Rm, Rd],
    [R,  R,  R,  R,  Rm, Rm, Rd, Rd],
    [R,  R,  R,  Rm, Rm, Rm, Rd, Rd],
    [Rm, Rm, Rm, Rm, Rm, Rd, Rd, Rd],
    [Rm, Rm, Rd, Rd, Rd, Rd, Rd, Rd],
]

# Rock variant - cracked/textured
ROCK_CRACKED = [
    [Rl, Rl, R,  Rd, R,  R,  Rm, Rm],
    [Rl, R,  R,  R,  Rd, R,  Rm, Rm],
    [R,  R,  Rd, R,  R,  R,  Rm, Rd],
    [R,  Rd, R,  R,  R,  Rm, Rm, Rd],
    [R,  R,  R,  Rd, Rm, Rm, Rd, Rd],
    [R,  R,  Rm, Rm, Rm, Rd, Rd, Rd],
    [Rm, Rm, Rm, Rm, Rd, Rd, Rd, Rd],
    [Rm, Rm, Rd, Rd, Rd, Rd, Rd, Rd],
]

def main():
    output_dir = "/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Sprites/Terrain"

    sprites = [
        ("grass.png", GRASS),
        ("dirt.png", DIRT),
        ("rock.png", ROCK),
        ("rock_cracked.png", ROCK_CRACKED),
    ]

    for filename, grid in sprites:
        img = create_sprite_from_grid(grid)
        path = f"{output_dir}/{filename}"
        img.save(path)
        print(f"Created: {path}")

    # Create tileset (4x1, 32x8)
    sheet = Image.new('RGBA', (32, 8), T)
    tiles = [GRASS, DIRT, ROCK, ROCK_CRACKED]
    for i, grid in enumerate(tiles):
        sprite = create_sprite_from_grid(grid)
        sheet.paste(sprite, (i * 8, 0))

    sheet_path = f"{output_dir}/terrain_tileset.png"
    sheet.save(sheet_path)
    print(f"Created tileset: {sheet_path}")

    print("\nUnity import settings:")
    print("  - Pixels Per Unit: 8")
    print("  - Filter Mode: Point (no filter)")
    print("  - Compression: None")

if __name__ == "__main__":
    main()
