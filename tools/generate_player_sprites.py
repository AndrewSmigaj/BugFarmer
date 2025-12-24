#!/usr/bin/env python3
"""Generate cute chibi-style player sprites for Bug Farmer.

Creates 32x32 pixel sprites for 4 directions.
Uses block-based drawing for clean pixel art.
Chibi style: big head, small body, rosy cheeks.
"""

from PIL import Image

# Colors (RGBA)
T = (0, 0, 0, 0)           # Transparent
O = (35, 25, 25, 255)      # Outline/dark
H = (70, 45, 30, 255)      # Hair
S = (255, 210, 170, 255)   # Skin
D = (225, 185, 150, 255)   # Skin shadow
C = (255, 150, 150, 255)   # Cheek blush
E = (45, 35, 35, 255)      # Eye dark (pupil)
W = (255, 255, 255, 255)   # Eye white (highlight)
B = (55, 95, 205, 255)     # Shirt (blue)
b = (40, 70, 160, 255)     # Shirt shadow
P = (50, 50, 70, 255)      # Pants
p = (35, 35, 55, 255)      # Pants shadow

def create_sprite_from_grid(grid):
    """Create a 32x32 image from a 16x16 grid (each cell = 2x2 pixels)."""
    img = Image.new('RGBA', (32, 32), T)
    pixels = img.load()

    for y, row in enumerate(grid):
        for x, color in enumerate(row):
            # Each grid cell becomes 2x2 pixels
            px, py = x * 2, y * 2
            pixels[px, py] = color
            pixels[px + 1, py] = color
            pixels[px, py + 1] = color
            pixels[px + 1, py + 1] = color

    return img

# 16x16 grids (each cell = 2x2 pixels = 32x32 final)
# Chibi style: big round head, small body, rosy cheeks

# Player facing DOWN (toward camera)
PLAYER_DOWN = [
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, O, O, O, O, O, O, T, T, T, T, T],
    [T, T, T, T, O, H, H, H, H, H, H, O, T, T, T, T],
    [T, T, T, O, H, H, H, H, H, H, H, H, O, T, T, T],
    [T, T, T, O, H, H, H, H, H, H, H, H, O, T, T, T],
    [T, T, T, O, S, S, S, S, S, S, S, S, O, T, T, T],
    [T, T, T, O, S, W, E, S, S, W, E, S, O, T, T, T],
    [T, T, T, O, S, E, E, S, S, E, E, S, O, T, T, T],
    [T, T, T, O, C, S, S, S, S, S, S, C, O, T, T, T],
    [T, T, T, O, S, S, S, D, D, S, S, S, O, T, T, T],
    [T, T, T, T, O, O, S, S, S, S, O, O, T, T, T, T],
    [T, T, T, T, T, O, B, B, B, B, O, T, T, T, T, T],
    [T, T, T, T, T, O, B, b, b, B, O, T, T, T, T, T],
    [T, T, T, T, T, O, B, b, b, B, O, T, T, T, T, T],
    [T, T, T, T, T, O, P, O, O, P, O, T, T, T, T, T],
    [T, T, T, T, T, O, O, T, T, O, O, T, T, T, T, T],
]

# Player facing UP (away from camera)
PLAYER_UP = [
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, O, O, O, O, O, O, T, T, T, T, T],
    [T, T, T, T, O, H, H, H, H, H, H, O, T, T, T, T],
    [T, T, T, O, H, H, H, H, H, H, H, H, O, T, T, T],
    [T, T, T, O, H, H, H, H, H, H, H, H, O, T, T, T],
    [T, T, T, O, H, H, H, H, H, H, H, H, O, T, T, T],
    [T, T, T, O, H, H, H, H, H, H, H, H, O, T, T, T],
    [T, T, T, O, H, H, H, H, H, H, H, H, O, T, T, T],
    [T, T, T, O, S, H, H, H, H, H, H, S, O, T, T, T],
    [T, T, T, O, S, S, S, S, S, S, S, S, O, T, T, T],
    [T, T, T, T, O, O, S, S, S, S, O, O, T, T, T, T],
    [T, T, T, T, T, O, B, B, B, B, O, T, T, T, T, T],
    [T, T, T, T, T, O, B, b, b, B, O, T, T, T, T, T],
    [T, T, T, T, T, O, B, b, b, B, O, T, T, T, T, T],
    [T, T, T, T, T, O, P, O, O, P, O, T, T, T, T, T],
    [T, T, T, T, T, O, O, T, T, O, O, T, T, T, T, T],
]

# Player facing LEFT
PLAYER_LEFT = [
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, O, O, O, O, O, O, T, T, T, T, T, T],
    [T, T, T, O, H, H, H, H, H, H, O, T, T, T, T, T],
    [T, T, O, H, H, H, H, H, H, H, H, O, T, T, T, T],
    [T, T, O, H, H, H, H, H, H, H, H, O, T, T, T, T],
    [T, T, O, S, S, S, H, H, H, H, H, O, T, T, T, T],
    [T, T, O, S, W, E, S, H, H, H, H, O, T, T, T, T],
    [T, T, O, S, E, E, S, S, H, H, H, O, T, T, T, T],
    [T, T, O, C, S, S, S, S, S, S, S, O, T, T, T, T],
    [T, T, O, S, S, S, D, S, S, S, S, O, T, T, T, T],
    [T, T, T, O, O, S, S, S, S, O, O, T, T, T, T, T],
    [T, T, T, T, T, O, B, B, B, O, T, T, T, T, T, T],
    [T, T, T, T, T, O, B, b, B, O, T, T, T, T, T, T],
    [T, T, T, T, T, O, B, b, B, O, T, T, T, T, T, T],
    [T, T, T, T, T, O, P, O, P, O, T, T, T, T, T, T],
    [T, T, T, T, T, O, O, T, O, O, T, T, T, T, T, T],
]

# Player facing RIGHT
PLAYER_RIGHT = [
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, O, O, O, O, O, O, T, T, T, T],
    [T, T, T, T, T, O, H, H, H, H, H, H, O, T, T, T],
    [T, T, T, T, O, H, H, H, H, H, H, H, H, O, T, T],
    [T, T, T, T, O, H, H, H, H, H, H, H, H, O, T, T],
    [T, T, T, T, O, H, H, H, H, H, S, S, S, O, T, T],
    [T, T, T, T, O, H, H, H, H, S, W, E, S, O, T, T],
    [T, T, T, T, O, H, H, H, S, S, E, E, S, O, T, T],
    [T, T, T, T, O, S, S, S, S, S, S, S, C, O, T, T],
    [T, T, T, T, O, S, S, S, S, S, D, S, S, O, T, T],
    [T, T, T, T, T, O, O, S, S, S, S, O, O, T, T, T],
    [T, T, T, T, T, T, O, B, B, B, O, T, T, T, T, T],
    [T, T, T, T, T, T, O, B, b, B, O, T, T, T, T, T],
    [T, T, T, T, T, T, O, B, b, B, O, T, T, T, T, T],
    [T, T, T, T, T, T, O, P, O, P, O, T, T, T, T, T],
    [T, T, T, T, T, T, O, O, T, O, O, T, T, T, T, T],
]

def main():
    output_dir = "/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Sprites/Player"

    sprites = [
        ("player_down.png", PLAYER_DOWN),
        ("player_up.png", PLAYER_UP),
        ("player_left.png", PLAYER_LEFT),
        ("player_right.png", PLAYER_RIGHT),
    ]

    for filename, grid in sprites:
        img = create_sprite_from_grid(grid)
        path = f"{output_dir}/{filename}"
        img.save(path)
        print(f"Created: {path}")

    # Create sprite sheet (4x1, 128x32) - order: Down, Left, Right, Up (matches Direction enum)
    sheet = Image.new('RGBA', (128, 32), T)
    sheet_order = [PLAYER_DOWN, PLAYER_LEFT, PLAYER_RIGHT, PLAYER_UP]
    for i, grid in enumerate(sheet_order):
        sprite = create_sprite_from_grid(grid)
        sheet.paste(sprite, (i * 32, 0))

    sheet_path = f"{output_dir}/player_spritesheet.png"
    sheet.save(sheet_path)
    print(f"Created sprite sheet: {sheet_path}")

    print("\nUnity import settings:")
    print("  - Texture Type: Sprite (2D and UI)")
    print("  - Sprite Mode: Single (or Multiple for sheet)")
    print("  - Pixels Per Unit: 8")
    print("  - Filter Mode: Point (no filter)")
    print("  - Compression: None")

if __name__ == "__main__":
    main()
