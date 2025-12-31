#!/usr/bin/env python3
"""Generate building sprites (fences, walls, doors) for Bug Farmer.

Design principles:
- 45-degree top-down perspective
- Light source: top-left
- Top edge visible (looking down at fence/wall)
- Posts/rails clear, must tile horizontally
"""

from PIL import Image
import os

# Colors (RGBA)
T = (0, 0, 0, 0)  # Transparent

# Wood
Wd = (70, 50, 35, 255)
W  = (120, 90, 60, 255)
Wl = (160, 130, 95, 255)

# Stone
Sd = (85, 85, 90, 255)
S  = (120, 120, 125, 255)
Sl = (155, 155, 160, 255)

# Iron
Md = (60, 65, 70, 255)
M  = (100, 105, 110, 255)
Ml = (150, 155, 160, 255)

# Brick
Bd = (120, 60, 50, 255)
B  = (160, 85, 70, 255)
Bl = (190, 115, 95, 255)

# Electric (blue glow)
Ed = (40, 80, 140, 255)
E  = (80, 140, 200, 255)
El = (140, 200, 255, 255)


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


# =============================================================================
# FENCES - 16x20 (tileable horizontally)
# =============================================================================

def build_fence_wood():
    """Wooden fence: 16x20"""
    grid = [[T] * 16 for _ in range(20)]

    # Top rail
    for x in range(16):
        grid[0][x] = Wl if x < 8 else W
        grid[1][x] = W
        grid[2][x] = Wd

    # Posts (left and right edges for tiling)
    for y in range(20):
        grid[y][0] = Wl
        grid[y][1] = W
        grid[y][2] = Wd if y > 2 else W
        grid[y][13] = Wl if y < 10 else W
        grid[y][14] = W
        grid[y][15] = Wd

    # Middle rail
    for x in range(16):
        grid[8][x] = Wl if x < 8 else W
        grid[9][x] = W
        grid[10][x] = Wd

    # Vertical slats between posts
    for y in range(3, 20):
        grid[y][5] = W
        grid[y][6] = Wd if y > 10 else W
        grid[y][9] = W
        grid[y][10] = Wd if y > 10 else W

    return grid


def build_fence_corner_wood():
    """Wooden fence corner: 16x20 (1x1 footprint)

    3/4 perspective structure:
    - Corner post: VERTICAL, center of tile
    - Rails extend toward viewer (south) and to the right (east)
    - Top of post and rails visible (horizontal surfaces)
    """
    grid = [[T] * 16 for _ in range(20)]

    # === CORNER POST (center, larger than regular posts) ===
    # Post top (horizontal surface, viewed from above)
    for y in range(0, 3):
        for x in range(5, 11):
            if x < 7:
                grid[y][x] = Wl  # Left - lit
            elif x < 9:
                grid[y][x] = W   # Center
            else:
                grid[y][x] = Wd  # Right - shadow

    # Top edge highlight
    for x in range(5, 11):
        grid[0][x] = Wl

    # Post front face (vertical, darker)
    for y in range(3, 20):
        for x in range(5, 11):
            if x < 7:
                grid[y][x] = W   # Left - less dark
            elif x < 9:
                grid[y][x] = Wd  # Center
            else:
                grid[y][x] = Wd  # Right - dark

    # Edge between top and front
    for x in range(5, 11):
        grid[3][x] = Wd

    # === RAIL EXTENDING RIGHT (east) ===
    # Top rail (horizontal surface)
    for x in range(11, 16):
        grid[1][x] = Wl if x < 13 else W
        grid[2][x] = W
    # Rail front (vertical)
    for x in range(11, 16):
        grid[3][x] = Wd

    # Middle rail
    for x in range(11, 16):
        grid[8][x] = Wl if x < 13 else W
        grid[9][x] = W
        grid[10][x] = Wd

    # === RAIL EXTENDING DOWN (south, toward viewer) ===
    # These rails are seen more from above as they come toward us
    # Top rail
    for y in range(3, 8):
        grid[y][7] = Wl
        grid[y][8] = W

    # Middle rail
    for y in range(10, 14):
        grid[y][7] = Wl
        grid[y][8] = W

    # Bottom rail / fence slats going south
    for y in range(14, 20):
        grid[y][6] = W
        grid[y][7] = W
        grid[y][8] = Wd
        grid[y][9] = Wd

    return grid


def build_fence_stone():
    """Stone fence: 16x20 - 3/4 perspective

    Shows top cap + front face
    """
    grid = [[T] * 16 for _ in range(20)]

    # === TOP CAP (horizontal surface) - rows 0-4 ===
    for y in range(0, 4):
        for x in range(16):
            if x < 5:
                grid[y][x] = Sl  # Left - lit
            elif x < 11:
                grid[y][x] = S   # Center - base
            else:
                grid[y][x] = Sd  # Right - shadow

    # Top edge highlight
    for x in range(16):
        grid[0][x] = Sl

    # === FRONT FACE (vertical, darker) - rows 4-18 ===
    for y in range(4, 18):
        for x in range(16):
            if x < 5:
                grid[y][x] = S   # Left - less dark
            elif x < 11:
                grid[y][x] = Sd  # Center
            else:
                grid[y][x] = Sd  # Right - dark

    # Edge between top and front
    for x in range(16):
        grid[4][x] = Sd

    # Base (darker)
    for x in range(16):
        grid[18][x] = Sd
        grid[19][x] = Sd

    return grid


def build_fence_iron():
    """Iron fence: 16x20"""
    grid = [[T] * 16 for _ in range(20)]

    # Top rail
    for x in range(16):
        grid[1][x] = Ml if x < 8 else M
        grid[2][x] = M
        grid[3][x] = Md

    # Spikes at top
    for x in [2, 5, 8, 11, 14]:
        grid[0][x] = Ml
        grid[0][x-1] = M if x > 1 else Ml

    # Bars
    for y in range(4, 18):
        for x in [2, 5, 8, 11, 14]:
            grid[y][x] = M
            if x > 0:
                grid[y][x-1] = Ml if y < 10 else M

    # Bottom rail
    for x in range(16):
        grid[16][x] = M
        grid[17][x] = Md

    # Base stones
    for x in range(16):
        grid[18][x] = Sd
        grid[19][x] = Sd

    return grid


def build_fence_electric():
    """Electric fence: 16x20"""
    grid = [[T] * 16 for _ in range(20)]

    # Posts (metal with insulators)
    for y in range(20):
        # Left post
        grid[y][1] = Ml if y < 10 else M
        grid[y][2] = Md
        # Right post
        grid[y][13] = M
        grid[y][14] = Md

    # Electric wires (glowing)
    for x in range(3, 13):
        grid[4][x] = El if x < 8 else E
        grid[5][x] = E if x < 8 else Ed
        grid[10][x] = El if x < 8 else E
        grid[11][x] = E if x < 8 else Ed
        grid[16][x] = El if x < 8 else E
        grid[17][x] = E if x < 8 else Ed

    # Insulators (white)
    insulator = (220, 220, 210, 255)
    for y in [4, 10, 16]:
        grid[y][2] = insulator
        grid[y][13] = insulator

    return grid


def build_gate_wood():
    """Wooden gate: 16x20 (closed state)"""
    grid = [[T] * 16 for _ in range(20)]

    # Frame posts
    for y in range(20):
        grid[y][0] = Wl
        grid[y][1] = W
        grid[y][2] = Wd
        grid[y][13] = Wl
        grid[y][14] = W
        grid[y][15] = Wd

    # Gate panels (cross-braced)
    for y in range(2, 18):
        for x in range(3, 13):
            grid[y][x] = W

    # Cross brace (diagonal)
    for i in range(10):
        y = 3 + i
        x = 4 + i
        if y < 18 and x < 13:
            grid[y][x] = Wd

    # Hinges
    hinge = (80, 70, 65, 255)
    for y in [4, 10, 16]:
        grid[y][3] = hinge
        grid[y][4] = hinge

    # Handle
    grid[10][11] = Md
    grid[10][12] = M
    grid[11][12] = M

    return grid


def build_gate_iron():
    """Iron gate: 16x20"""
    grid = [[T] * 16 for _ in range(20)]

    # Frame
    for y in range(20):
        grid[y][0] = Ml if y < 10 else M
        grid[y][1] = M
        grid[y][14] = M
        grid[y][15] = Md

    # Top/bottom rails
    for x in range(2, 14):
        grid[1][x] = Ml
        grid[2][x] = M
        grid[17][x] = M
        grid[18][x] = Md

    # Vertical bars
    for y in range(3, 17):
        for x in [4, 7, 10, 13]:
            grid[y][x] = M

    # Decorative curl at center
    grid[8][6] = M; grid[8][7] = Ml; grid[8][8] = M
    grid[9][5] = M; grid[9][9] = M
    grid[10][6] = M; grid[10][7] = Md; grid[10][8] = M

    return grid


# =============================================================================
# WALLS - 16x18 (tileable horizontally)
# =============================================================================

def build_wall_wood():
    """Wooden wall: 16x18 - 3/4 perspective

    Shows thin top edge + front face with vertical planks
    """
    grid = [[T] * 16 for _ in range(18)]

    # === TOP EDGE (horizontal, thin) - rows 0-2 ===
    for y in range(0, 2):
        for x in range(16):
            if x < 5:
                grid[y][x] = Wl  # Left - lit
            elif x < 11:
                grid[y][x] = W   # Center
            else:
                grid[y][x] = Wd  # Right - shadow

    # Top highlight
    for x in range(16):
        grid[0][x] = Wl

    # === FRONT FACE with planks - rows 2-18 ===
    for y in range(2, 18):
        for x in range(16):
            plank = x // 4
            # Left-right shading, alternating plank tones
            if x < 5:
                grid[y][x] = Wl if plank % 2 == 0 else W
            elif x < 11:
                grid[y][x] = W if plank % 2 == 0 else Wd
            else:
                grid[y][x] = Wd

    # Edge between top and front
    for x in range(16):
        grid[2][x] = Wd

    # Gaps between planks (vertical dark lines)
    for y in range(2, 18):
        grid[y][3] = Wd
        grid[y][7] = Wd
        grid[y][11] = Wd

    return grid


def build_wall_stone():
    """Stone wall: 16x18 - 3/4 perspective"""
    grid = [[T] * 16 for _ in range(18)]

    # === TOP EDGE (horizontal) - rows 0-2 ===
    for y in range(0, 2):
        for x in range(16):
            if x < 5:
                grid[y][x] = Sl
            elif x < 11:
                grid[y][x] = S
            else:
                grid[y][x] = Sd

    # Top highlight
    for x in range(16):
        grid[0][x] = Sl

    # === FRONT FACE with stone blocks - rows 2-18 ===
    for y in range(2, 18):
        for x in range(16):
            # Left-right shading
            if x < 5:
                grid[y][x] = S   # Left - less dark
            elif x < 11:
                grid[y][x] = Sd  # Center
            else:
                grid[y][x] = Sd  # Right - dark

    # Edge between top and front
    for x in range(16):
        grid[2][x] = Sd

    # Mortar lines (horizontal)
    mortar = (70, 70, 75, 255)
    for y in [5, 9, 13, 17]:
        for x in range(16):
            grid[y][x] = mortar

    # Mortar lines (vertical, staggered)
    for y in range(2, 18):
        row = (y - 2) // 4
        offset = 0 if row % 2 == 0 else 4
        for bx in [offset, offset + 8]:
            if 0 <= bx < 16:
                grid[y][bx] = mortar

    return grid


def build_wall_brick():
    """Brick wall: 16x18 - 3/4 perspective"""
    grid = [[T] * 16 for _ in range(18)]

    # === TOP EDGE (horizontal) - rows 0-2 ===
    for y in range(0, 2):
        for x in range(16):
            if x < 5:
                grid[y][x] = Bl
            elif x < 11:
                grid[y][x] = B
            else:
                grid[y][x] = Bd

    # Top highlight
    for x in range(16):
        grid[0][x] = Bl

    # === FRONT FACE with bricks - rows 2-18 ===
    for y in range(2, 18):
        for x in range(16):
            # Left-right shading
            if x < 5:
                grid[y][x] = B   # Left - less dark
            elif x < 11:
                grid[y][x] = Bd  # Center
            else:
                grid[y][x] = Bd  # Right - dark

    # Edge between top and front
    for x in range(16):
        grid[2][x] = Bd

    # Mortar lines (horizontal)
    mortar = (160, 155, 145, 255)
    for y in [4, 7, 10, 13, 16]:
        for x in range(16):
            grid[y][x] = mortar

    # Mortar lines (vertical, staggered)
    for y in range(2, 18):
        row = (y - 2) // 3
        offset = 0 if row % 2 == 0 else 4
        for bx in [offset, offset + 8]:
            if 0 <= bx < 16:
                grid[y][bx] = mortar

    return grid


# =============================================================================
# DOORS - 16x24 (1x2 footprint)
# =============================================================================

def build_door_wood():
    """Wooden door: 16x24 - 3/4 perspective

    Door is mostly front-facing vertical surface with thin top edge
    """
    grid = [[T] * 16 for _ in range(24)]

    # === TOP FRAME (horizontal, thin) - rows 0-2 ===
    for y in range(0, 2):
        for x in range(16):
            if x < 5:
                grid[y][x] = Wl
            elif x < 11:
                grid[y][x] = W
            else:
                grid[y][x] = Wd

    # Top edge highlight
    for x in range(16):
        grid[0][x] = Wl

    # === DOOR FRAME (sides) - vertical surfaces ===
    for y in range(2, 24):
        grid[y][0] = Wl  # Left frame - lit
        grid[y][1] = W
        grid[y][14] = Wd  # Right frame - shadow
        grid[y][15] = Wd

    # === DOOR PANELS (front face, left-right shading) ===
    for y in range(2, 24):
        for x in range(2, 14):
            if x < 6:
                grid[y][x] = Wl  # Left - lit
            elif x < 10:
                grid[y][x] = W   # Center
            else:
                grid[y][x] = Wd  # Right - shadow

    # Edge between top and door
    for x in range(2, 14):
        grid[2][x] = W

    # Panel insets (recessed, darker)
    for y in range(5, 11):
        for x in range(4, 12):
            grid[y][x] = Wd

    for y in range(14, 21):
        for x in range(4, 12):
            grid[y][x] = Wd

    # Handle
    grid[13][10] = Md
    grid[13][11] = M
    grid[14][11] = M

    return grid


def build_door_iron():
    """Iron door: 16x24 - 3/4 perspective"""
    grid = [[T] * 16 for _ in range(24)]

    # === TOP FRAME (horizontal, thin) - rows 0-2 ===
    for y in range(0, 2):
        for x in range(16):
            if x < 5:
                grid[y][x] = Ml
            elif x < 11:
                grid[y][x] = M
            else:
                grid[y][x] = Md

    # Top edge highlight
    for x in range(16):
        grid[0][x] = Ml

    # === DOOR FRAME (sides) ===
    for y in range(2, 24):
        grid[y][0] = Ml  # Left - lit
        grid[y][1] = M
        grid[y][14] = Md  # Right - shadow
        grid[y][15] = Md

    # === DOOR BODY (front face, left-right shading) ===
    for y in range(2, 24):
        for x in range(2, 14):
            if x < 6:
                grid[y][x] = Ml  # Left - lit
            elif x < 10:
                grid[y][x] = M   # Center
            else:
                grid[y][x] = Md  # Right - shadow

    # Edge between top and door
    for x in range(2, 14):
        grid[2][x] = M

    # Rivets
    rivet = (50, 55, 60, 255)
    for ry in [4, 12, 20]:
        for rx in [4, 11]:
            grid[ry][rx] = rivet

    # Viewing slot
    for y in range(6, 10):
        for x in range(6, 10):
            grid[y][x] = (30, 30, 35, 255)  # Dark inside

    # Handle
    grid[14][10] = Md
    grid[14][11] = Ml
    grid[15][11] = M

    return grid


def main():
    output_dir = "/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Sprites/Buildings"
    os.makedirs(output_dir, exist_ok=True)

    sprites = [
        # Fences
        ("fence_wood.png", build_fence_wood()),
        ("fence_corner_wood.png", build_fence_corner_wood()),
        ("fence_stone.png", build_fence_stone()),
        ("fence_iron.png", build_fence_iron()),
        ("fence_electric.png", build_fence_electric()),
        ("gate_wood.png", build_gate_wood()),
        ("gate_iron.png", build_gate_iron()),
        # Walls
        ("wall_wood.png", build_wall_wood()),
        ("wall_stone.png", build_wall_stone()),
        ("wall_brick.png", build_wall_brick()),
        # Doors
        ("door_wood.png", build_door_wood()),
        ("door_iron.png", build_door_iron()),
    ]

    for filename, grid in sprites:
        img = create_sprite_from_grid(grid)
        path = f"{output_dir}/{filename}"
        img.save(path)
        print(f"Created: {path} ({img.size[0]}x{img.size[1]})")

    print("\nUnity import settings:")
    print("  - Pixels Per Unit: 16")
    print("  - Filter Mode: Point (no filter)")
    print("  - Compression: None")


if __name__ == "__main__":
    main()
