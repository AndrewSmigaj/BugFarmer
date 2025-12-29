#!/usr/bin/env python3
"""Generate simple pixel art player sprites for Bug Farmer.

Creates 32x32 pixel sprites for 4 directions.
Uses block-based drawing for clean pixel art.
Style: Simple, proportional, classic pixel art (think Stardew Valley / SNES RPG).
"""

from PIL import Image

# Colors (RGBA)
T = (0, 0, 0, 0)           # Transparent
O = (35, 25, 25, 255)      # Outline/dark
H = (90, 60, 40, 255)      # Hair
h = (65, 42, 28, 255)      # Hair shadow
S = (255, 220, 180, 255)   # Skin
D = (235, 195, 155, 255)   # Skin shadow
E = (35, 30, 30, 255)      # Eye (simple dark dot)
B = (70, 130, 100, 255)    # Shirt (muted green)
b = (50, 100, 75, 255)     # Shirt shadow
P = (65, 55, 80, 255)      # Pants (muted purple)
p = (45, 38, 60, 255)      # Pants shadow
K = (90, 75, 55, 255)      # Shoes

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
# Simple proportional style: smaller head, longer body, no blush

# Player facing DOWN (toward camera)
PLAYER_DOWN = [
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, O, O, O, O, T, T, T, T, T, T],
    [T, T, T, T, T, O, H, H, H, H, O, T, T, T, T, T],
    [T, T, T, T, O, H, H, H, H, H, H, O, T, T, T, T],
    [T, T, T, T, O, H, H, H, H, H, H, O, T, T, T, T],
    [T, T, T, T, O, S, S, S, S, S, S, O, T, T, T, T],
    [T, T, T, T, O, S, E, S, S, E, S, O, T, T, T, T],
    [T, T, T, T, O, S, S, S, S, S, S, O, T, T, T, T],
    [T, T, T, T, T, O, S, D, D, S, O, T, T, T, T, T],
    [T, T, T, T, T, T, O, S, S, O, T, T, T, T, T, T],
    [T, T, T, T, T, O, B, B, B, B, O, T, T, T, T, T],
    [T, T, T, T, O, B, B, b, b, B, B, O, T, T, T, T],
    [T, T, T, T, O, B, B, b, b, B, B, O, T, T, T, T],
    [T, T, T, T, T, O, P, P, P, P, O, T, T, T, T, T],
    [T, T, T, T, T, O, P, p, p, P, O, T, T, T, T, T],
    [T, T, T, T, T, O, K, O, O, K, O, T, T, T, T, T],
]

# Player facing UP (away from camera)
PLAYER_UP = [
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, O, O, O, O, T, T, T, T, T, T],
    [T, T, T, T, T, O, H, H, H, H, O, T, T, T, T, T],
    [T, T, T, T, O, H, H, H, H, H, H, O, T, T, T, T],
    [T, T, T, T, O, H, H, H, H, H, H, O, T, T, T, T],
    [T, T, T, T, O, H, H, H, H, H, H, O, T, T, T, T],
    [T, T, T, T, O, H, H, H, H, H, H, O, T, T, T, T],
    [T, T, T, T, O, S, H, H, H, H, S, O, T, T, T, T],
    [T, T, T, T, T, O, S, S, S, S, O, T, T, T, T, T],
    [T, T, T, T, T, T, O, S, S, O, T, T, T, T, T, T],
    [T, T, T, T, T, O, B, B, B, B, O, T, T, T, T, T],
    [T, T, T, T, O, B, B, b, b, B, B, O, T, T, T, T],
    [T, T, T, T, O, B, B, b, b, B, B, O, T, T, T, T],
    [T, T, T, T, T, O, P, P, P, P, O, T, T, T, T, T],
    [T, T, T, T, T, O, P, p, p, P, O, T, T, T, T, T],
    [T, T, T, T, T, O, K, O, O, K, O, T, T, T, T, T],
]

# Player facing LEFT
PLAYER_LEFT = [
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, O, O, O, O, T, T, T, T, T, T, T],
    [T, T, T, T, O, H, H, H, H, O, T, T, T, T, T, T],
    [T, T, T, O, H, H, H, H, H, H, O, T, T, T, T, T],
    [T, T, T, O, H, H, H, H, H, H, O, T, T, T, T, T],
    [T, T, T, O, S, S, S, H, H, H, O, T, T, T, T, T],
    [T, T, T, O, S, E, S, S, H, H, O, T, T, T, T, T],
    [T, T, T, O, S, S, S, S, S, S, O, T, T, T, T, T],
    [T, T, T, T, O, S, S, D, S, O, T, T, T, T, T, T],
    [T, T, T, T, T, O, S, S, O, T, T, T, T, T, T, T],
    [T, T, T, T, T, O, B, B, B, O, T, T, T, T, T, T],
    [T, T, T, T, O, B, B, b, B, B, O, T, T, T, T, T],
    [T, T, T, T, O, B, B, b, B, B, O, T, T, T, T, T],
    [T, T, T, T, T, O, P, P, P, O, T, T, T, T, T, T],
    [T, T, T, T, T, O, P, p, P, O, T, T, T, T, T, T],
    [T, T, T, T, T, O, K, O, K, O, T, T, T, T, T, T],
]

# Player facing RIGHT
PLAYER_RIGHT = [
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, O, O, O, O, T, T, T, T, T],
    [T, T, T, T, T, T, O, H, H, H, H, O, T, T, T, T],
    [T, T, T, T, T, O, H, H, H, H, H, H, O, T, T, T],
    [T, T, T, T, T, O, H, H, H, H, H, H, O, T, T, T],
    [T, T, T, T, T, O, H, H, H, S, S, S, O, T, T, T],
    [T, T, T, T, T, O, H, H, S, S, E, S, O, T, T, T],
    [T, T, T, T, T, O, S, S, S, S, S, S, O, T, T, T],
    [T, T, T, T, T, T, O, S, D, S, S, O, T, T, T, T],
    [T, T, T, T, T, T, T, O, S, S, O, T, T, T, T, T],
    [T, T, T, T, T, T, O, B, B, B, O, T, T, T, T, T],
    [T, T, T, T, T, O, B, B, b, B, B, O, T, T, T, T],
    [T, T, T, T, T, O, B, B, b, B, B, O, T, T, T, T],
    [T, T, T, T, T, T, O, P, P, P, O, T, T, T, T, T],
    [T, T, T, T, T, T, O, P, p, P, O, T, T, T, T, T],
    [T, T, T, T, T, T, O, K, O, K, O, T, T, T, T, T],
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
