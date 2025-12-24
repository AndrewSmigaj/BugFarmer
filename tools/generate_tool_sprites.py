#!/usr/bin/env python3
"""Generate tool sprites for Bug Farmer.

Tools: 8x16 pixels (1x2 blocks) - long and thin
- Hoe: farming tool with horizontal blade
- Axe: chopping tool with chunky blade
- Butterfly net: catching tool with small net, long handle
"""

from PIL import Image

# Colors (RGBA)
T = (0, 0, 0, 0)           # Transparent

# Handle colors (wood)
Hw = (140, 100, 60, 255)   # Handle wood
Hd = (100, 70, 45, 255)    # Handle dark
Hl = (170, 130, 85, 255)   # Handle light

# Metal colors
Mt = (160, 165, 175, 255)  # Metal main
Md = (100, 105, 115, 255)  # Metal dark
Ml = (200, 205, 215, 255)  # Metal light

# Net colors
Nt = (220, 220, 230, 200)  # Net mesh (semi-transparent)
Nr = (80, 140, 80, 255)    # Net rim (green)
Nd = (60, 110, 60, 255)    # Net rim dark


def create_image_from_grid(grid):
    """Create an image from a 2D grid of colors."""
    height = len(grid)
    width = len(grid[0])
    img = Image.new('RGBA', (width, height), T)
    pixels = img.load()
    for y, row in enumerate(grid):
        for x, color in enumerate(row):
            pixels[x, y] = color
    return img


# Hoe: 8x16 - flat horizontal blade at top, handle below
HOE = [
    [Md, Mt, Mt, Mt, Mt, Mt, Ml, T ],
    [Md, Mt, Mt, Mt, Mt, Mt, Ml, T ],
    [T,  T,  T,  Md, Mt, T,  T,  T ],
    [T,  T,  T,  Hd, Hw, T,  T,  T ],
    [T,  T,  T,  Hd, Hw, T,  T,  T ],
    [T,  T,  T,  Hd, Hw, T,  T,  T ],
    [T,  T,  T,  Hd, Hw, T,  T,  T ],
    [T,  T,  T,  Hd, Hw, T,  T,  T ],
    [T,  T,  T,  Hd, Hw, T,  T,  T ],
    [T,  T,  T,  Hd, Hw, T,  T,  T ],
    [T,  T,  T,  Hd, Hw, T,  T,  T ],
    [T,  T,  T,  Hd, Hw, T,  T,  T ],
    [T,  T,  T,  Hd, Hw, T,  T,  T ],
    [T,  T,  T,  Hd, Hw, T,  T,  T ],
    [T,  T,  T,  Hd, Hl, T,  T,  T ],
    [T,  T,  T,  Hd, Hl, T,  T,  T ],
]

# Axe: 8x16 - chunky blade at top-right, handle below
AXE = [
    [T,  T,  T,  Md, Mt, Mt, T,  T ],
    [T,  T,  Md, Mt, Mt, Mt, Ml, T ],
    [T,  T,  Md, Mt, Mt, Mt, Ml, T ],
    [T,  T,  Md, Mt, Mt, Mt, Ml, T ],
    [T,  T,  Hd, Hw, Md, Ml, T,  T ],
    [T,  T,  Hd, Hw, T,  T,  T,  T ],
    [T,  T,  Hd, Hw, T,  T,  T,  T ],
    [T,  T,  Hd, Hw, T,  T,  T,  T ],
    [T,  T,  Hd, Hw, T,  T,  T,  T ],
    [T,  T,  Hd, Hw, T,  T,  T,  T ],
    [T,  T,  Hd, Hw, T,  T,  T,  T ],
    [T,  T,  Hd, Hw, T,  T,  T,  T ],
    [T,  T,  Hd, Hw, T,  T,  T,  T ],
    [T,  T,  Hd, Hw, T,  T,  T,  T ],
    [T,  T,  Hd, Hl, T,  T,  T,  T ],
    [T,  T,  Hd, Hl, T,  T,  T,  T ],
]

# Butterfly net: 8x16 - small net at top (5 rows), long handle
NET = [
    [T,  T,  Nr, Nr, Nr, Nr, T,  T ],
    [T,  Nr, Nt, Nt, Nt, Nt, Nr, T ],
    [T,  Nr, Nt, Nt, Nt, Nt, Nr, T ],
    [T,  Nr, Nt, Nt, Nt, Nt, Nr, T ],
    [T,  T,  Nd, Nr, Nr, Nd, T,  T ],
    [T,  T,  T,  Hd, Hw, T,  T,  T ],
    [T,  T,  T,  Hd, Hw, T,  T,  T ],
    [T,  T,  T,  Hd, Hw, T,  T,  T ],
    [T,  T,  T,  Hd, Hw, T,  T,  T ],
    [T,  T,  T,  Hd, Hw, T,  T,  T ],
    [T,  T,  T,  Hd, Hw, T,  T,  T ],
    [T,  T,  T,  Hd, Hw, T,  T,  T ],
    [T,  T,  T,  Hd, Hw, T,  T,  T ],
    [T,  T,  T,  Hd, Hw, T,  T,  T ],
    [T,  T,  T,  Hd, Hl, T,  T,  T ],
    [T,  T,  T,  Hd, Hl, T,  T,  T ],
]


def main():
    output_dir = "/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Sprites/Tools"

    # Create directory if needed
    import os
    os.makedirs(output_dir, exist_ok=True)

    sprites = [
        ("hoe.png", HOE),
        ("axe.png", AXE),
        ("net.png", NET),
    ]

    for filename, grid in sprites:
        img = create_image_from_grid(grid)
        path = f"{output_dir}/{filename}"
        img.save(path)
        print(f"Created: {path} ({img.width}x{img.height})")

    # Create tools spritesheet (3 tools side by side: 24x16)
    sheet_width = 8 * 3  # 24
    sheet_height = 16
    sheet = Image.new('RGBA', (sheet_width, sheet_height), T)

    for i, (_, grid) in enumerate(sprites):
        img = create_image_from_grid(grid)
        sheet.paste(img, (i * 8, 0))

    sheet_path = f"{output_dir}/tools_spritesheet.png"
    sheet.save(sheet_path)
    print(f"Created spritesheet: {sheet_path} ({sheet_width}x{sheet_height})")

    print("\nUnity import settings:")
    print("  - Pixels Per Unit: 8")
    print("  - Filter Mode: Point (no filter)")
    print("  - Compression: None")


if __name__ == "__main__":
    main()
