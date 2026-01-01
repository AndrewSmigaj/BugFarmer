#!/usr/bin/env python3
"""Generate break stage sprites (crack overlays) for Bug Farmer.

Creates 4 stages of crack overlay sprites that show progressive damage.
These overlay on top of breakable objects during mining/breaking.

Design principles:
- Semi-transparent black cracks on transparent background
- 16x16 pixels to match cell size
- 4 stages: light cracks -> severe cracks
- Cracks spread from corners/edges toward center
- Consistent style with other game sprites
"""

from PIL import Image
import os

# Colors (RGBA)
T = (0, 0, 0, 0)        # Transparent
C = (0, 0, 0, 200)      # Crack color (black with high alpha)
Cl = (0, 0, 0, 120)     # Crack light (thinner/lighter cracks)

# Stage 1: Initial damage - corner crack
# Just a small crack from top-left corner
BREAK_STAGE_1 = [
    [Cl, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, Cl, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, Cl, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, Cl, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
]

# Stage 2: Light damage - cracks from two corners
BREAK_STAGE_2 = [
    [C,  T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [Cl, C, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, Cl, C, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, Cl, C, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, Cl, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T,Cl, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T,Cl, C,Cl, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T,Cl, C,Cl, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T,Cl, C,Cl, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T,Cl, C, C],
]

# Stage 3: Heavy damage - cracks spreading across
BREAK_STAGE_3 = [
    [C,  C, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [Cl, C, C, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, Cl, C, C, T, T, T, T, T, T, T, T, T, T, T,Cl],
    [T, T, Cl, C, C, T, T, T, T, T, T, T, T, T,Cl, C],
    [T, T, T, Cl, C, C, T, T, T, T, T, T, T,Cl, C, T],
    [T, T, T, T, Cl, C, T, T, T, T, T, T,Cl, C,Cl, T],
    [T, T, T, T, T, Cl, T, T, T, T, T,Cl, C, T, T, T],
    [T, T, T, T, T, T, T, T, T, T,Cl, C,Cl, T, T, T],
    [T, T, T, T, T, T, T, T, T,Cl, C, T, T, T, T, T],
    [T, T, T,Cl, T, T, T, T,Cl, C, T, T, T, T, T, T],
    [T, T,Cl, C, T, T, T,Cl, C,Cl, T, T, T, T, T, T],
    [T,Cl, C,Cl, T, T,Cl, C,Cl, T, T,Cl, T, T, T, T],
    [Cl, C, T, T, T,Cl, C,Cl, T, T,Cl, C,Cl, T, T, T],
    [C,Cl, T, T,Cl, C,Cl, T, T, T, T,Cl, C,Cl, T, T],
    [T, T, T,Cl, C,Cl, T, T, T, T, T, T,Cl, C,Cl, T],
    [T, T, T, C, T, T, T, T, T, T, T, T, T,Cl, C, C],
]

# Stage 4: Critical damage - about to break
BREAK_STAGE_4 = [
    [C,  C, C, T, T, T, T, T, T, T, T, T, T,Cl, C, C],
    [C,  C, C, C, T, T, T, T, T, T, T, T,Cl, C, C, C],
    [Cl, C, C, C, C, T, T, T, T, T, T,Cl, C, C, C,Cl],
    [T, Cl, C, C, C, C, T, T, T, T,Cl, C, C, C,Cl, T],
    [T, T, Cl, C, C, C, C, T, T,Cl, C, C, C,Cl, T, T],
    [T, T, T, Cl, C, C, C, T,Cl, C, C, C,Cl, T, T, T],
    [T, T, T, T, Cl, C, C, C, C, C, C,Cl, T, T, T, T],
    [T, T, T, T, T, Cl, C, C, C, C,Cl, T, T, T, T, T],
    [T, T, T, T, T,Cl, C, C, C, C,Cl, T, T, T, T, T],
    [T, T, T, T,Cl, C, C, C, C, C, C,Cl, T, T, T, T],
    [T, T, T,Cl, C, C, C, T, T, C, C, C,Cl, T, T, T],
    [T, T,Cl, C, C, C,Cl, T, T,Cl, C, C, C,Cl, T, T],
    [T,Cl, C, C, C,Cl, T, T, T, T,Cl, C, C, C,Cl, T],
    [Cl, C, C, C,Cl, T, T, T, T, T, T,Cl, C, C, C,Cl],
    [C,  C, C,Cl, T, T, T, T, T, T, T, T,Cl, C, C, C],
    [C,  C,Cl, T, T, T, T, T, T, T, T, T, T,Cl, C, C],
]


def create_sprite(data, path):
    """Create a 16x16 sprite from pixel data."""
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    pixels = img.load()

    for y in range(16):
        for x in range(16):
            pixels[x, y] = data[y][x]

    img.save(path)
    print(f"Created: {path}")


def main():
    # Output directory
    output_dir = "../BugFarmerClient/Assets/Sprites/Effects"
    os.makedirs(output_dir, exist_ok=True)

    # Generate break stage sprites
    sprites = [
        ("break_stage_1.png", BREAK_STAGE_1),
        ("break_stage_2.png", BREAK_STAGE_2),
        ("break_stage_3.png", BREAK_STAGE_3),
        ("break_stage_4.png", BREAK_STAGE_4),
    ]

    for filename, data in sprites:
        path = os.path.join(output_dir, filename)
        create_sprite(data, path)

    print(f"\nGenerated {len(sprites)} break stage sprites in {output_dir}")
    print("\nUnity setup:")
    print("1. Import sprites with 'Pixels Per Unit: 16'")
    print("2. Set 'Filter Mode: Point (no filter)'")
    print("3. Load via: Resources.LoadAll<Sprite>(\"Sprites/Effects\") and filter by name")


if __name__ == "__main__":
    main()
