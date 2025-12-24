#!/usr/bin/env python3
"""Generate object sprites for Bug Farmer.

Objects:
- Tree: 24x32 pixels (3x4 blocks) - bird's eye view, trunk at bottom
- Fly: 8x8 pixels (1 block)
- Fence segment: 16x8 pixels (2x1 blocks, horizontal ranch-style)
"""

from PIL import Image

# Colors (RGBA)
T = (0, 0, 0, 0)           # Transparent

# Tree colors
Tk = (60, 40, 30, 255)     # Trunk dark
Tl = (90, 60, 45, 255)     # Trunk light
Lf = (45, 120, 50, 255)    # Leaf dark
Ll = (70, 160, 70, 255)    # Leaf mid
Lb = (95, 190, 90, 255)    # Leaf bright

# Fly colors
Fb = (30, 30, 35, 255)     # Fly body
Fw = (200, 210, 230, 180)  # Fly wing (semi-transparent)
Fe = (180, 50, 50, 255)    # Fly eye

# Fence colors
Fn = (140, 100, 60, 255)   # Fence main
Fd = (100, 70, 45, 255)    # Fence dark
Fl = (170, 130, 85, 255)   # Fence light


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


# Tree: 24x32 pixels (3 blocks wide x 4 blocks tall)
# Bird's eye view: circular canopy with trunk visible at bottom
TREE = [
    # Row 0-7: Top of canopy
    [T,  T,  T,  T,  T,  T,  T,  Lf, Lf, Lf, Lf, Lf, Lf, Lf, Lf, Lf, Lf, T,  T,  T,  T,  T,  T,  T ],
    [T,  T,  T,  T,  T,  Lf, Lf, Ll, Ll, Ll, Lb, Lb, Lb, Ll, Ll, Ll, Lf, Lf, T,  T,  T,  T,  T,  T ],
    [T,  T,  T,  T,  Lf, Ll, Ll, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Ll, Ll, Lf, Lf, T,  T,  T,  T,  T ],
    [T,  T,  T,  Lf, Ll, Ll, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Ll, Ll, Lf, T,  T,  T,  T,  T ],
    [T,  T,  Lf, Ll, Ll, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Ll, Ll, Lf, T,  T,  T,  T ],
    [T,  T,  Lf, Ll, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Ll, Lf, T,  T,  T,  T ],
    [T,  Lf, Ll, Ll, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Ll, Ll, Lf, T,  T,  T ],
    [T,  Lf, Ll, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Ll, Lf, T,  T,  T ],
    # Row 8-15: Middle canopy
    [Lf, Ll, Ll, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Ll, Ll, Lf, T,  T ],
    [Lf, Ll, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Ll, Lf, T,  T ],
    [Lf, Ll, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Ll, Lf, Lf, T ],
    [Lf, Ll, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Ll, Ll, Lf, T ],
    [Lf, Ll, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Ll, Ll, Lf, Lf],
    [Lf, Ll, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Ll, Ll, Lf],
    [Lf, Ll, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Ll, Ll, Lf],
    [Lf, Ll, Ll, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Ll, Ll, Lf, Lf],
    # Row 16-23: Lower canopy
    [Lf, Lf, Ll, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Ll, Ll, Lf, Lf, T ],
    [T,  Lf, Ll, Ll, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Ll, Ll, Lf, Lf, T,  T ],
    [T,  Lf, Lf, Ll, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Ll, Ll, Lf, Lf, T,  T,  T ],
    [T,  T,  Lf, Ll, Ll, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Ll, Ll, Lf, Lf, T,  T,  T,  T ],
    [T,  T,  Lf, Lf, Ll, Ll, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Ll, Ll, Lf, Lf, T,  T,  T,  T,  T ],
    [T,  T,  T,  Lf, Lf, Ll, Ll, Lb, Lb, Lb, Lb, Lb, Lb, Lb, Ll, Ll, Lf, Lf, T,  T,  T,  T,  T,  T ],
    [T,  T,  T,  T,  Lf, Lf, Ll, Ll, Ll, Ll, Ll, Ll, Ll, Ll, Ll, Lf, Lf, T,  T,  T,  T,  T,  T,  T ],
    [T,  T,  T,  T,  T,  Lf, Lf, Lf, Ll, Ll, Ll, Ll, Ll, Lf, Lf, Lf, T,  T,  T,  T,  T,  T,  T,  T ],
    # Row 24-31: Trunk at bottom (visible from bird's eye)
    [T,  T,  T,  T,  T,  T,  T,  Lf, Lf, Tk, Tl, Tl, Tk, Lf, Lf, T,  T,  T,  T,  T,  T,  T,  T,  T ],
    [T,  T,  T,  T,  T,  T,  T,  T,  Lf, Tk, Tl, Tl, Tk, Lf, T,  T,  T,  T,  T,  T,  T,  T,  T,  T ],
    [T,  T,  T,  T,  T,  T,  T,  T,  T,  Tk, Tl, Tl, Tk, T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T ],
    [T,  T,  T,  T,  T,  T,  T,  T,  T,  Tk, Tl, Tl, Tk, T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T ],
    [T,  T,  T,  T,  T,  T,  T,  T,  T,  Tk, Tl, Tl, Tk, T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T ],
    [T,  T,  T,  T,  T,  T,  T,  T,  T,  Tk, Tl, Tl, Tk, T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T ],
    [T,  T,  T,  T,  T,  T,  T,  T,  Tk, Tk, Tl, Tl, Tk, Tk, T,  T,  T,  T,  T,  T,  T,  T,  T,  T ],
    [T,  T,  T,  T,  T,  T,  T,  T,  Tk, Tk, Tk, Tk, Tk, Tk, T,  T,  T,  T,  T,  T,  T,  T,  T,  T ],
]

# Fly: 8x8 pixels - small bug with wings spread
FLY = [
    [T,  T,  Fw, T,  T,  Fw, T,  T ],
    [T,  Fw, Fw, T,  T,  Fw, Fw, T ],
    [T,  Fw, Fw, Fb, Fb, Fw, Fw, T ],
    [T,  T,  Fb, Fb, Fb, Fb, T,  T ],
    [T,  T,  Fe, Fb, Fb, Fe, T,  T ],
    [T,  T,  Fb, Fb, Fb, Fb, T,  T ],
    [T,  T,  T,  Fb, Fb, T,  T,  T ],
    [T,  T,  T,  T,  T,  T,  T,  T ],
]

# Fence segment: 16x8 pixels (2 blocks wide, 1 block tall)
# Horizontal ranch-style fence with two rails and gap between
FENCE_SEGMENT = [
    [Fd, Fn, Fn, Fn, Fn, Fn, Fn, Fd, Fd, Fn, Fn, Fn, Fn, Fn, Fn, Fd],
    [Fn, Fl, Fn, Fn, Fn, Fn, Fl, Fn, Fn, Fl, Fn, Fn, Fn, Fn, Fl, Fn],
    [Fn, Fn, Fn, Fn, Fn, Fn, Fn, Fn, Fn, Fn, Fn, Fn, Fn, Fn, Fn, Fn],
    [Fd, Fn, Fn, Fn, Fn, Fn, Fn, Fd, Fd, Fn, Fn, Fn, Fn, Fn, Fn, Fd],
    [T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T ],
    [Fd, Fn, Fn, Fn, Fn, Fn, Fn, Fd, Fd, Fn, Fn, Fn, Fn, Fn, Fn, Fd],
    [Fn, Fl, Fn, Fn, Fn, Fn, Fl, Fn, Fn, Fl, Fn, Fn, Fn, Fn, Fl, Fn],
    [Fd, Fn, Fn, Fn, Fn, Fn, Fn, Fd, Fd, Fn, Fn, Fn, Fn, Fn, Fn, Fd],
]


def main():
    output_dir = "/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Sprites/Objects"

    sprites = [
        ("tree.png", TREE),
        ("fly.png", FLY),
        ("fence_segment.png", FENCE_SEGMENT),
    ]

    for filename, grid in sprites:
        img = create_image_from_grid(grid)
        path = f"{output_dir}/{filename}"
        img.save(path)
        print(f"Created: {path} ({img.width}x{img.height})")

    # Create objects spritesheet
    # Layout: tree (24x32) | fly (8x8) | fence (16x8)
    sheet_width = 24 + 8 + 16  # 48
    sheet_height = 32
    sheet = Image.new('RGBA', (sheet_width, sheet_height), T)

    tree_img = create_image_from_grid(TREE)
    fly_img = create_image_from_grid(FLY)
    fence_img = create_image_from_grid(FENCE_SEGMENT)

    sheet.paste(tree_img, (0, 0))
    sheet.paste(fly_img, (24, 0))
    sheet.paste(fence_img, (32, 0))

    sheet_path = f"{output_dir}/objects_spritesheet.png"
    sheet.save(sheet_path)
    print(f"Created spritesheet: {sheet_path} ({sheet_width}x{sheet_height})")

    print("\nUnity import settings:")
    print("  - Pixels Per Unit: 8")
    print("  - Filter Mode: Point (no filter)")
    print("  - Compression: None")


if __name__ == "__main__":
    main()
