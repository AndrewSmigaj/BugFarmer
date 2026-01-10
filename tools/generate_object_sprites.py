#!/usr/bin/env python3
"""Generate world object sprites for Bug Farmer.

Design principles:
- 45-degree top-down perspective
- Light source: top-left
- Shadows: bottom-right
- Trees show canopy from above, trunk at bottom
- Rocks show top surface with lighting gradient

Sprites from architecture_items.md:
- tree_oak: 32x48 (2x2 footprint)
- tree_pine: 32x52 (2x2 footprint)
- tree_dead: 16x32 (1x1 footprint)
- bush: 16x16 (1x1 footprint)
- rock_small: 16x16 (1x1 footprint)
- rock_large: 32x32 (2x2 footprint)
"""

from PIL import Image
import os

# Colors (RGBA)
T = (0, 0, 0, 0)  # Transparent

# Tree trunk (wood) - from SPRITE_GENERATION_GUIDE.md
Wd = (70, 50, 35, 255)     # Wood dark (shadow side)
W  = (120, 90, 60, 255)    # Wood base
Wl = (160, 130, 95, 255)   # Wood light (lit side)

# Tree canopy (green foliage)
Ld = (40, 85, 40, 255)     # Leaf dark (shadow)
L  = (55, 120, 55, 255)    # Leaf base
Ll = (80, 150, 70, 255)    # Leaf light (highlights)

# Pine foliage (darker, bluer green)
Pd = (30, 70, 45, 255)     # Pine dark
P  = (40, 95, 60, 255)     # Pine base
Pl = (60, 125, 75, 255)    # Pine light

# Dead tree (gray-brown)
Dd = (60, 55, 50, 255)     # Dead dark
D  = (95, 85, 75, 255)     # Dead base
Dl = (130, 120, 105, 255)  # Dead light

# Rock/Stone - from SPRITE_GENERATION_GUIDE.md
Rd = (85, 85, 90, 255)     # Rock dark
R  = (120, 120, 125, 255)  # Rock base
Rl = (155, 155, 160, 255)  # Rock light

# Palm tree (yellow-green tropical)
PAd = (50, 100, 45, 255)   # Palm dark
PA  = (70, 130, 60, 255)   # Palm base
PAl = (100, 160, 80, 255)  # Palm light

# Fruit (red apples/berries)
Fd = (150, 40, 40, 255)    # Fruit dark
F  = (200, 60, 50, 255)    # Fruit base
Fl = (230, 100, 80, 255)   # Fruit light

# Tall grass/reeds
Gd = (55, 115, 55, 255)    # Grass dark
G  = (72, 140, 72, 255)    # Grass base
Gl = (95, 165, 85, 255)    # Grass light

# Mushroom red
MRd = (140, 30, 30, 255)   # Mushroom cap dark
MR  = (180, 50, 45, 255)   # Mushroom cap base
MRl = (210, 80, 70, 255)   # Mushroom cap light
MS  = (220, 210, 200, 255) # Mushroom stem/spots

# Mushroom glow (cyan/green bioluminescent)
MGd = (40, 120, 100, 255)  # Glow dark
MG  = (80, 180, 150, 255)  # Glow base
MGl = (140, 230, 200, 255) # Glow light (brightest)

# Flowers
FLRd = (150, 40, 50, 255)  # Red flower dark
FLR  = (200, 60, 70, 255)  # Red flower base
FLRl = (240, 100, 110, 255)# Red flower light

FLBd = (40, 60, 150, 255)  # Blue flower dark
FLB  = (70, 100, 200, 255) # Blue flower base
FLBl = (120, 150, 240, 255)# Blue flower light

FLYd = (180, 150, 30, 255) # Yellow flower dark
FLY  = (230, 200, 50, 255) # Yellow flower base
FLYl = (255, 230, 100, 255)# Yellow flower light

FLWd = (150, 100, 160, 255)# Wild flower dark (purple)
FLW  = (190, 140, 200, 255)# Wild flower base
FLWl = (220, 180, 230, 255)# Wild flower light

# Sunflower
SFd = (180, 140, 30, 255)  # Sunflower petal dark
SF  = (230, 190, 50, 255)  # Sunflower petal base
SFl = (255, 220, 90, 255)  # Sunflower petal light
SFc = (90, 60, 30, 255)    # Sunflower center (brown)

# Crystal (cave)
Cd = (100, 140, 180, 255)  # Crystal dark
C  = (150, 190, 220, 255)  # Crystal base
Cl = (200, 230, 250, 255)  # Crystal light

# Bone
Bd = (180, 175, 160, 255)  # Bone dark
B  = (220, 215, 200, 255)  # Bone base
Bl = (245, 240, 230, 255)  # Bone light

# Ant mound (dirt-brown)
Ad = (100, 70, 40, 255)    # Ant mound dark
A  = (130, 95, 55, 255)    # Ant mound base
Al = (160, 120, 75, 255)   # Ant mound light


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
# TREES - 45° top-down view (canopy dominates, trunk at bottom)
# Light source: top-left, shadows: bottom-right
# =============================================================================

def build_tree_oak():
    """Oak tree: 32x48 (2x2 footprint) - round canopy

    Canopy shows top surface (lit), trunk has front face (dark), grounded
    """
    grid = [[T] * 32 for _ in range(48)]

    # Canopy: oval shape centered, rows 0-35
    # Top portion (rows 0-22) is lit top surface, bottom (rows 23-35) is front/shadow
    for y in range(36):
        cy, cx = 16, 16
        ry, rx = 16, 14

        dy = abs(y - cy)
        if dy <= ry:
            ratio = 1 - (dy / ry) ** 2
            if ratio > 0:
                x_range = int(rx * (ratio ** 0.5))
                x_start = cx - x_range
                x_end = cx + x_range

                for x in range(max(0, x_start), min(32, x_end + 1)):
                    # Top vs bottom distinction (plane contrast)
                    if y < 22:  # Top surface of canopy
                        if x < 10:
                            grid[y][x] = Ll
                        elif x < 22:
                            grid[y][x] = L
                        else:
                            grid[y][x] = Ld
                    else:  # Front/underside of canopy (darker)
                        if x < 10:
                            grid[y][x] = L
                        else:
                            grid[y][x] = Ld

    # Edge between canopy top and front
    for x in range(6, 26):
        if grid[22][x] != T:
            grid[22][x] = Ld

    # Trunk: rows 32-47, centered with clear front face
    # Trunk top portion (32-40) visible, front (41-47) darker
    for y in range(32, 48):
        trunk_half_width = 4 if y < 40 else 3
        trunk_center = 16

        for x in range(trunk_center - trunk_half_width, trunk_center + trunk_half_width):
            if y < 41:  # Upper trunk visible
                if x < trunk_center - 1:
                    grid[y][x] = Wl
                elif x > trunk_center:
                    grid[y][x] = Wd
                else:
                    grid[y][x] = W
            else:  # Front face of trunk (darker)
                if x < trunk_center:
                    grid[y][x] = W
                else:
                    grid[y][x] = Wd

    # Ground contact - extra dark base
    ground = (max(0, Wd[0]-25), max(0, Wd[1]-25), max(0, Wd[2]-25), 255)
    for x in range(13, 19):
        grid[47][x] = ground

    return grid


def build_tree_pine():
    """Pine tree: 32x52 (2x2 footprint) - triangular/conical

    Layered canopy with top/front distinction, grounded trunk
    """
    grid = [[T] * 32 for _ in range(52)]

    # Pine: triangular canopy, rows 0-42
    # Top portion is lit, lower portion darker
    for y in range(42):
        half_width = 2 + int(y * 0.62)
        center = 16

        for x in range(max(0, center - half_width), min(32, center + half_width)):
            rel_x = x - center

            # Add layered effect - alternating bands of light/dark
            layer = y // 8
            in_top_of_layer = (y % 8) < 5

            if in_top_of_layer:  # Top of each "tier"
                if rel_x < -half_width // 2:
                    grid[y][x] = Pl
                elif rel_x < half_width // 3:
                    grid[y][x] = P
                else:
                    grid[y][x] = Pd
            else:  # Front/shadow of each tier
                if rel_x < 0:
                    grid[y][x] = P
                else:
                    grid[y][x] = Pd

    # Trunk: rows 38-51 with front face
    for y in range(38, 52):
        trunk_half_width = 3
        trunk_center = 16

        for x in range(trunk_center - trunk_half_width, trunk_center + trunk_half_width):
            if y < 45:  # Upper trunk
                if x < trunk_center - 1:
                    grid[y][x] = Wl
                elif x > trunk_center:
                    grid[y][x] = Wd
                else:
                    grid[y][x] = W
            else:  # Front face (darker)
                if x < trunk_center:
                    grid[y][x] = W
                else:
                    grid[y][x] = Wd

    # Ground contact
    ground = (max(0, Wd[0]-25), max(0, Wd[1]-25), max(0, Wd[2]-25), 255)
    for x in range(13, 19):
        grid[51][x] = ground

    return grid


def build_tree_dead():
    """Dead tree: 16x32 (1x1 footprint) - bare branches with ground contact"""
    grid = [[T] * 16 for _ in range(32)]

    # Main trunk: center, full height
    for y in range(32):
        trunk_x = 8
        if y < 8:
            width = 2
        elif y < 20:
            width = 3
        else:
            width = 4

        for x in range(trunk_x - width // 2, trunk_x + (width + 1) // 2):
            # Front face distinction in lower half
            if y >= 22:  # Front face region
                if x < trunk_x:
                    grid[y][x] = D
                else:
                    grid[y][x] = Dd
            else:
                if x < trunk_x:
                    grid[y][x] = Dl
                elif x > trunk_x:
                    grid[y][x] = Dd
                else:
                    grid[y][x] = D

    # Branches extending left and right
    for i in range(6):
        y = 6 + i // 2
        x = 6 - i
        if 0 <= x < 16 and 0 <= y < 32:
            grid[y][x] = Dl if i < 3 else D

    for i in range(6):
        y = 8 + i // 2
        x = 10 + i
        if 0 <= x < 16 and 0 <= y < 32:
            grid[y][x] = Dd if i > 2 else D

    for i in range(4):
        y = 3 + i // 2
        x = 5 - i
        if 0 <= x < 16 and 0 <= y < 32:
            grid[y][x] = Dl

    for i in range(4):
        y = 4 + i // 2
        x = 11 + i
        if 0 <= x < 16 and 0 <= y < 32:
            grid[y][x] = D

    # Ground contact - dark base
    ground = (max(0, Dd[0]-20), max(0, Dd[1]-20), max(0, Dd[2]-20), 255)
    for x in range(6, 11):
        grid[31][x] = ground

    return grid


def build_bush():
    """Bush: 16x16 (1x1 footprint) - chunky shrub with top/front planes

    Top surface (65%) + front face (35%), grounded
    """
    grid = [[T] * 16 for _ in range(16)]

    # Bush structure: top surface rows 0-9, front face rows 10-15
    top_end = 10

    # Top surface (rows 0-9) - rounded horizontally
    for y in range(top_end):
        # Horizontal extent varies for rounded shape
        margin = max(0, int(2 * (abs(y - 4) / 5)))
        x_start = 2 + margin
        x_end = 14 - margin

        for x in range(x_start, x_end):
            # Left-right gradient on top
            if x < 6:
                grid[y][x] = Ll
            elif x < 11:
                grid[y][x] = L
            else:
                grid[y][x] = Ld

    # Front face (rows 10-15) - darker
    for y in range(10, 16):
        # Front tapers at bottom
        margin = (y - 10) // 2
        x_start = 3 + margin
        x_end = 13 - margin

        for x in range(x_start, x_end):
            if x < 6:
                grid[y][x] = L  # Left edge catches some light
            else:
                grid[y][x] = Ld  # Rest is shadow

    # Edge between top and front
    for x in range(3, 13):
        grid[9][x] = Ld

    # Ground contact - darker bottom
    darker = (max(0, Ld[0]-20), max(0, Ld[1]-20), max(0, Ld[2]-20), 255)
    for x in range(5, 11):
        grid[15][x] = darker

    return grid


# =============================================================================
# ROCKS - 45° top-down view (top surface visible)
# =============================================================================

def build_rock_small():
    """Small rock: 16x16 (1x1 footprint) - 3/4 perspective

    Top surface (65%) + front face (35%), chunky and grounded
    """
    grid = [[T] * 16 for _ in range(16)]

    # Rock is a chunky 3D object: top surface rows 0-9, front face rows 10-15
    top_rows = 10  # 62.5% top
    front_rows = 6  # 37.5% front

    # Top surface (rounded-ish, lighter)
    for y in range(top_rows):
        # Horizontal extent varies to create rounded top
        margin = max(0, int(2 * (abs(y - 4) / 5)))
        x_start = 2 + margin
        x_end = 14 - margin

        for x in range(x_start, x_end):
            # Left-right gradient on top surface
            if x < 6:
                grid[y][x] = Rl
            elif x < 11:
                grid[y][x] = R
            else:
                grid[y][x] = Rd

    # Front face (darker, rows 10-15)
    darker = (max(0, Rd[0]-25), max(0, Rd[1]-25), max(0, Rd[2]-25), 255)
    for y in range(10, 16):
        # Front face tapers at bottom
        margin = max(0, (y - 10) // 2)
        x_start = 3 + margin
        x_end = 13 - margin

        for x in range(x_start, x_end):
            if x < 6:
                grid[y][x] = Rd  # Left of front gets some light
            else:
                grid[y][x] = darker  # Rest is deep shadow

    # Ground contact - extra dark bottom edge
    ground = (max(0, Rd[0]-40), max(0, Rd[1]-40), max(0, Rd[2]-40), 255)
    for x in range(5, 11):
        grid[15][x] = ground

    # Edge line between top and front
    for x in range(3, 13):
        grid[9][x] = Rd

    return grid


def build_rock_large():
    """Large rock: 32x32 (2x2 footprint) - 3/4 perspective

    Top surface (65%) + front face (35%), chunky and grounded
    """
    grid = [[T] * 32 for _ in range(32)]

    # Rock structure: top surface rows 0-20, front face rows 21-31
    top_rows = 21  # 65% top
    front_start = 21

    # Top surface (irregular rounded shape)
    for y in range(top_rows):
        # Horizontal extent with slight irregularity
        base_margin = max(0, int(4 * (abs(y - 10) / 12)))
        wobble = ((y * 3) % 3) - 1  # Minor edge variation
        x_start = 3 + base_margin + wobble
        x_end = 29 - base_margin - wobble

        for x in range(max(0, x_start), min(32, x_end)):
            # Left-right gradient on top surface
            if x < 12:
                grid[y][x] = Rl
            elif x < 22:
                grid[y][x] = R
            else:
                grid[y][x] = Rd

    # Add clustered texture on top surface
    clusters = [(8, 6), (18, 10), (24, 5), (12, 14)]
    for cx, cy in clusters:
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < 32 and 0 <= ny < 21 and grid[ny][nx] != T:
                    grid[ny][nx] = Rd

    # Front face (darker, rows 21-31)
    darker = (max(0, Rd[0]-25), max(0, Rd[1]-25), max(0, Rd[2]-25), 255)
    for y in range(front_start, 32):
        # Front face tapers toward bottom
        margin = (y - front_start) // 2
        x_start = 5 + margin
        x_end = 27 - margin

        for x in range(x_start, x_end):
            if x < 12:
                grid[y][x] = Rd  # Left side gets some reflected light
            else:
                grid[y][x] = darker

    # Edge line between top and front (strong contrast)
    for x in range(5, 27):
        grid[20][x] = Rd

    # Ground contact - extra dark bottom edge
    ground = (max(0, Rd[0]-40), max(0, Rd[1]-40), max(0, Rd[2]-40), 255)
    for x in range(10, 22):
        grid[31][x] = ground

    return grid


# =============================================================================
# ADDITIONAL TREES
# =============================================================================

def build_tree_palm():
    """Palm tree: 32x48 (2x2 footprint) - tropical fronds"""
    grid = [[T] * 32 for _ in range(48)]

    # Trunk: curved, rows 20-47, thinner than oak
    for y in range(20, 48):
        # Slight curve
        offset = int((y - 34) * 0.1)
        trunk_center = 16 + offset
        width = 3 if y < 35 else 4

        for x in range(trunk_center - width, trunk_center + width):
            if 0 <= x < 32:
                if x < trunk_center - 1:
                    grid[y][x] = Wl
                elif x > trunk_center:
                    grid[y][x] = Wd
                else:
                    grid[y][x] = W

    # Palm fronds radiating from top center
    frond_positions = [
        (-12, 8), (-10, 4), (-8, 0), (-4, -2), (0, -4),
        (4, -2), (8, 0), (10, 4), (12, 8)
    ]

    for fx, fy in frond_positions:
        # Draw frond as elongated shape
        start_x, start_y = 16, 18
        end_x, end_y = 16 + fx, 18 + fy

        for t in range(15):
            progress = t / 14
            px = int(start_x + (end_x - start_x) * progress)
            py = int(start_y + (end_y - start_y) * progress - 4 * progress * (1 - progress))

            width = 3 - int(progress * 2)
            for dx in range(-width, width + 1):
                nx = px + dx
                if 0 <= nx < 32 and 0 <= py < 48:
                    if dx < 0:
                        grid[py][nx] = PAl
                    elif dx > 0:
                        grid[py][nx] = PAd
                    else:
                        grid[py][nx] = PA

    return grid


def build_tree_fruit():
    """Fruit tree: 32x44 (2x2 footprint) - oak-like with fruit"""
    grid = [[T] * 32 for _ in range(44)]

    # Canopy similar to oak, rows 0-32
    for y in range(33):
        cy, cx = 15, 16
        ry, rx = 14, 13

        dy = abs(y - cy)
        if dy <= ry:
            ratio = 1 - (dy / ry) ** 2
            if ratio > 0:
                x_range = int(rx * (ratio ** 0.5))
                x_start = cx - x_range
                x_end = cx + x_range

                for x in range(max(0, x_start), min(32, x_end + 1)):
                    diag = (x - 16) + (y - 15)
                    if diag < -7:
                        grid[y][x] = Ll
                    elif diag < 3:
                        grid[y][x] = L
                    else:
                        grid[y][x] = Ld

    # Add fruit (red spots on canopy)
    fruit_positions = [(8, 10), (20, 8), (12, 18), (22, 16), (6, 22), (18, 24)]
    for fx, fy in fruit_positions:
        if 0 <= fx < 31 and 0 <= fy < 32:
            grid[fy][fx] = Fl
            grid[fy][fx + 1] = F
            grid[fy + 1][fx] = F
            grid[fy + 1][fx + 1] = Fd

    # Trunk: rows 30-43
    for y in range(30, 44):
        trunk_half_width = 3
        trunk_center = 16

        for x in range(trunk_center - trunk_half_width, trunk_center + trunk_half_width):
            if x < trunk_center - 1:
                grid[y][x] = Wl
            elif x > trunk_center:
                grid[y][x] = Wd
            else:
                grid[y][x] = W

    return grid


# =============================================================================
# SMALL VEGETATION
# =============================================================================

def build_tall_grass():
    """Tall grass: 16x20 (1x1 footprint) - grass clumps"""
    grid = [[T] * 16 for _ in range(20)]

    # Several grass blades
    blades = [(4, 8), (8, 6), (12, 9), (6, 10), (10, 7)]

    for bx, height in blades:
        for y in range(20 - height, 20):
            progress = (y - (20 - height)) / height
            sway = int(2 * progress * ((bx % 3) - 1))

            x = bx + sway
            if 0 <= x < 16:
                if x < 8:
                    grid[y][x] = Gl
                elif x > 8:
                    grid[y][x] = Gd
                else:
                    grid[y][x] = G

            # Width at base
            if y > 16 and 0 <= x - 1 < 16:
                grid[y][x - 1] = G
            if y > 17 and 0 <= x + 1 < 16:
                grid[y][x + 1] = G

    return grid


def build_reeds():
    """Reeds: 16x24 (1x1 footprint) - water edge plants"""
    grid = [[T] * 16 for _ in range(24)]

    # Tall reed stalks with fuzzy tops
    reed_positions = [(4, 18), (8, 20), (12, 16), (6, 14)]

    for rx, height in reed_positions:
        # Stalk
        for y in range(24 - height, 24):
            x = rx
            if 0 <= x < 16:
                grid[y][x] = G if x < 8 else Gd

        # Fuzzy top (cattail-like)
        top_y = 24 - height
        for dy in range(4):
            for dx in range(-1, 2):
                ny, nx = top_y + dy, rx + dx
                if 0 <= nx < 16 and 0 <= ny < 24:
                    # Brown fuzzy top
                    brown = (100, 70, 45, 255)
                    grid[ny][nx] = brown

    return grid


def build_mushroom_red():
    """Red mushroom: 16x16 (1x1 footprint) - with ground contact"""
    grid = [[T] * 16 for _ in range(16)]

    # Cap (dome shape, top half) with top/front distinction
    for y in range(10):
        cy, cx = 5, 8
        ry, rx = 5, 6

        dy = y - cy
        if abs(dy) <= ry:
            ratio = 1 - (dy / ry) ** 2
            if ratio > 0:
                x_range = int(rx * (ratio ** 0.5))
                for x in range(cx - x_range, cx + x_range + 1):
                    if 0 <= x < 16:
                        # Top vs front of cap (y-based)
                        if y < 6:  # Top of cap
                            if x < 6:
                                grid[y][x] = MRl
                            elif x < 10:
                                grid[y][x] = MR
                            else:
                                grid[y][x] = MRd
                        else:  # Front/underside of cap
                            if x < 7:
                                grid[y][x] = MR
                            else:
                                grid[y][x] = MRd

    # White spots on cap top
    spots = [(5, 3), (10, 4), (7, 2)]
    for sx, sy in spots:
        if 0 <= sx < 16 and 0 <= sy < 6:
            grid[sy][sx] = MS

    # Stem with front face
    stem_dark = (180, 175, 165, 255)
    for y in range(8, 16):
        for x in range(6, 10):
            if y < 12:  # Upper stem
                if x < 8:
                    grid[y][x] = MS
                else:
                    grid[y][x] = stem_dark
            else:  # Front face of stem
                grid[y][x] = stem_dark

    # Ground contact
    ground = (160, 155, 145, 255)
    for x in range(6, 10):
        grid[15][x] = ground

    return grid


def build_mushroom_glow():
    """Glowing mushroom: 16x16 (1x1 footprint) - bioluminescent with ground contact"""
    grid = [[T] * 16 for _ in range(16)]

    # Cap (dome shape) with top/front distinction
    for y in range(10):
        cy, cx = 5, 8
        ry, rx = 5, 6

        dy = y - cy
        if abs(dy) <= ry:
            ratio = 1 - (dy / ry) ** 2
            if ratio > 0:
                x_range = int(rx * (ratio ** 0.5))
                for x in range(cx - x_range, cx + x_range + 1):
                    if 0 <= x < 16:
                        # Top vs front of cap
                        if y < 6:  # Top of cap (brightest)
                            if x < 6:
                                grid[y][x] = MGl
                            elif x < 10:
                                grid[y][x] = MG
                            else:
                                grid[y][x] = MGd
                        else:  # Front/underside
                            if x < 7:
                                grid[y][x] = MG
                            else:
                                grid[y][x] = MGd

    # Stem with front face (also glowing)
    stem_light = (70, 150, 130, 255)
    stem_dark = (50, 120, 100, 255)
    for y in range(8, 16):
        for x in range(6, 10):
            if y < 12:  # Upper stem
                if x < 8:
                    grid[y][x] = stem_light
                else:
                    grid[y][x] = stem_dark
            else:  # Front face
                grid[y][x] = stem_dark

    # Ground contact
    ground = (40, 100, 85, 255)
    for x in range(6, 10):
        grid[15][x] = ground

    return grid


def build_flower(color_d, color_b, color_l):
    """Generic flower: 16x16 (1x1 footprint) - iconic shape with ground contact"""
    grid = [[T] * 16 for _ in range(16)]

    # Petals (simple 4-petal flower from above)
    # Top petal (lit)
    for y in range(2, 6):
        for x in range(6, 10):
            if x < 8:
                grid[y][x] = color_l
            else:
                grid[y][x] = color_b

    # Left petal (lit side)
    for y in range(4, 8):
        for x in range(2, 6):
            grid[y][x] = color_l if x < 4 else color_b

    # Right petal (shadow side)
    for y in range(4, 8):
        for x in range(10, 14):
            grid[y][x] = color_b if x < 12 else color_d

    # Bottom petal (front face, darker)
    for y in range(7, 11):
        for x in range(6, 10):
            grid[y][x] = color_b if y < 9 else color_d

    # Center (yellow)
    yellow = (230, 200, 50, 255)
    for y in range(5, 8):
        for x in range(7, 10):
            grid[y][x] = yellow

    # Stem with ground contact
    for y in range(10, 16):
        if y < 14:
            grid[y][8] = Gl  # Lit part of stem
        else:
            grid[y][8] = Gd  # Darker base

    # Ground contact
    grid[15][8] = (45, 95, 45, 255)

    return grid


def build_sunflower():
    """Sunflower: 16x24 (1x1 footprint) - tall flower"""
    grid = [[T] * 16 for _ in range(24)]

    # Large flower head at top
    center_x, center_y = 8, 6

    # Petals radiating out
    for angle in range(12):
        import math
        rad = angle * math.pi / 6
        for dist in range(3, 7):
            px = int(center_x + math.cos(rad) * dist)
            py = int(center_y + math.sin(rad) * dist)
            if 0 <= px < 16 and 0 <= py < 12:
                if dist < 5:
                    grid[py][px] = SFl
                else:
                    grid[py][px] = SF if angle < 6 else SFd

    # Brown center
    for y in range(4, 9):
        for x in range(6, 11):
            dx, dy = x - 8, y - 6
            if dx * dx + dy * dy <= 6:
                grid[y][x] = SFc

    # Tall stem
    for y in range(10, 24):
        grid[y][8] = G
        if y > 16:
            grid[y][7] = Gd  # Thicker at base

    return grid


# =============================================================================
# CAVE/UNDERGROUND OBJECTS
# =============================================================================

def build_crystal_small():
    """Small crystal: 16x20 (1x1 footprint)"""
    grid = [[T] * 16 for _ in range(20)]

    # Crystal cluster (3 pointed crystals)
    crystals = [
        (6, 4, 14),   # left crystal: x, top_y, bottom_y
        (8, 0, 16),   # center crystal (tallest)
        (10, 6, 18),  # right crystal
    ]

    for cx, top_y, bottom_y in crystals:
        for y in range(top_y, bottom_y):
            progress = (y - top_y) / (bottom_y - top_y)
            width = int(1 + progress * 2)

            for dx in range(-width, width + 1):
                x = cx + dx
                if 0 <= x < 16 and 0 <= y < 20:
                    if dx < 0:
                        grid[y][x] = Cl
                    elif dx > 0:
                        grid[y][x] = Cd
                    else:
                        grid[y][x] = C

    return grid


def build_crystal_large():
    """Large crystal: 32x28 (2x2 footprint)"""
    grid = [[T] * 32 for _ in range(28)]

    # Multiple large crystals
    crystals = [
        (8, 6, 24),
        (14, 0, 20),
        (20, 4, 26),
        (26, 8, 28),
    ]

    for cx, top_y, bottom_y in crystals:
        for y in range(top_y, bottom_y):
            progress = (y - top_y) / (bottom_y - top_y)
            width = int(2 + progress * 3)

            for dx in range(-width, width + 1):
                x = cx + dx
                if 0 <= x < 32 and 0 <= y < 28:
                    if dx < -1:
                        grid[y][x] = Cl
                    elif dx > 1:
                        grid[y][x] = Cd
                    else:
                        grid[y][x] = C

    return grid


def build_stalagmite():
    """Stalagmite: 16x24 (1x1 footprint) - cave formation"""
    grid = [[T] * 16 for _ in range(24)]

    # Pointed cone shape, wider at base
    for y in range(24):
        progress = y / 23
        width = int(1 + progress * 5)
        center = 8

        for dx in range(-width, width + 1):
            x = center + dx
            if 0 <= x < 16:
                if dx < -width // 2:
                    grid[y][x] = Rl
                elif dx > width // 2:
                    grid[y][x] = Rd
                else:
                    grid[y][x] = R

    return grid


def build_bone_pile():
    """Bone pile: 16x12 (1x1 footprint) - scattered bones"""
    grid = [[T] * 16 for _ in range(12)]

    # Scattered bone segments
    bones = [
        (2, 8, 6, 10),   # (x1, y1, x2, y2)
        (4, 4, 10, 6),
        (8, 6, 14, 8),
        (3, 6, 5, 10),
        (10, 4, 12, 8),
    ]

    for x1, y1, x2, y2 in bones:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if 0 <= x < 16 and 0 <= y < 12:
                    if x < 8:
                        grid[y][x] = Bl
                    elif x > 8:
                        grid[y][x] = Bd
                    else:
                        grid[y][x] = B

    return grid


def build_ant_mound():
    """Ant mound: 32x24 (2x2 footprint) - dirt mound with hole"""
    grid = [[T] * 32 for _ in range(24)]

    # Mound shape (dome)
    for y in range(24):
        cy, cx = 14, 16
        ry, rx = 10, 14

        dy = y - cy
        if abs(dy) <= ry:
            ratio = 1 - (dy / ry) ** 2
            if ratio > 0:
                x_range = int(rx * (ratio ** 0.5))
                for x in range(cx - x_range, cx + x_range + 1):
                    if 0 <= x < 32:
                        diag = (x - 16) + (y - 14)
                        if diag < -8:
                            grid[y][x] = Al
                        elif diag < 4:
                            grid[y][x] = A
                        else:
                            grid[y][x] = Ad

    # Dark hole at top
    hole_color = (40, 30, 20, 255)
    for y in range(8, 14):
        for x in range(13, 19):
            dx, dy = x - 16, y - 11
            if dx * dx + dy * dy <= 8:
                grid[y][x] = hole_color

    return grid


# =============================================================================
# VILLAGE PROPS
# =============================================================================

def build_stump():
    """Tree stump: 16x16 (1x1 footprint) - cut tree top view with rings"""
    grid = [[T] * 16 for _ in range(16)]

    # Outer bark ring (irregular circle)
    for y in range(16):
        for x in range(16):
            dx, dy = x - 8, y - 8
            dist = (dx * dx + dy * dy) ** 0.5

            if dist < 7:
                # Inner wood with rings
                if dist < 2:
                    grid[y][x] = Wl  # Center (lightest)
                elif dist < 4:
                    grid[y][x] = W   # Middle ring
                elif dist < 5.5:
                    grid[y][x] = Wl  # Light ring
                else:
                    grid[y][x] = W   # Outer wood

            elif dist < 8:
                # Bark edge
                grid[y][x] = Wd

    # Add shadow on right side
    for y in range(4, 12):
        for x in range(10, 14):
            if grid[y][x] != T:
                grid[y][x] = Wd

    return grid


def build_log_pile():
    """Log pile: 32x16 (2x1 footprint) - stacked horizontal logs"""
    grid = [[T] * 32 for _ in range(16)]

    # Three logs stacked (viewed from front/above at angle)
    logs = [
        (8, 12, 6),   # (center_x, center_y, radius) - bottom left
        (24, 12, 6),  # bottom right
        (16, 6, 6),   # top center
    ]

    for cx, cy, r in logs:
        for y in range(16):
            for x in range(32):
                dx, dy = x - cx, y - cy
                dist = (dx * dx + dy * dy) ** 0.5

                if dist < r:
                    # Log cross-section with rings
                    if dist < r * 0.3:
                        grid[y][x] = Wl  # Center
                    elif dist < r * 0.6:
                        grid[y][x] = W   # Middle
                    elif dist < r * 0.85:
                        grid[y][x] = Wl  # Ring
                    else:
                        grid[y][x] = Wd  # Bark

        # Shadow on bottom right of each log
        for y in range(cy, cy + r):
            for x in range(cx, cx + r):
                if 0 <= x < 32 and 0 <= y < 16:
                    dx, dy = x - cx, y - cy
                    if (dx * dx + dy * dy) ** 0.5 < r:
                        grid[y][x] = Wd

    return grid


def build_compost_pile():
    """Compost pile: 32x32 (2x2 footprint) - dark mound with debris"""
    grid = [[T] * 32 for _ in range(32)]

    # Compost colors (dark brown/greenish decay)
    CPd = (50, 40, 25, 255)   # Dark compost
    CP  = (70, 55, 35, 255)   # Base compost
    CPl = (90, 70, 45, 255)   # Light compost

    # Mound shape
    for y in range(8, 32):
        cy, cx = 20, 16
        ry, rx = 12, 14

        dy = y - cy
        if abs(dy) <= ry:
            ratio = 1 - (dy / ry) ** 2
            if ratio > 0:
                x_range = int(rx * (ratio ** 0.5))
                for x in range(cx - x_range, cx + x_range + 1):
                    if 0 <= x < 32:
                        diag = (x - 16) + (y - 20)
                        if diag < -6:
                            grid[y][x] = CPl
                        elif diag < 4:
                            grid[y][x] = CP
                        else:
                            grid[y][x] = CPd

    # Add debris bits (leaves, twigs)
    debris_color = (60, 80, 40, 255)  # Greenish
    debris_positions = [(10, 14), (22, 16), (14, 10), (18, 12), (8, 20), (24, 22)]
    for dx, dy in debris_positions:
        if grid[dy][dx] != T:
            grid[dy][dx] = debris_color
            if dx + 1 < 32:
                grid[dy][dx + 1] = debris_color

    return grid


def build_apple_crate():
    """Apple crate: 16x16 (1x1 footprint) - wooden crate with apples visible"""
    grid = [[T] * 16 for _ in range(16)]

    # Crate structure (top-down view of open crate)
    # Outer frame
    for y in range(2, 14):
        for x in range(2, 14):
            # Frame edges
            if y < 4 or y > 11 or x < 4 or x > 11:
                if x < 6:
                    grid[y][x] = Wl
                elif x > 9:
                    grid[y][x] = Wd
                else:
                    grid[y][x] = W

    # Apples inside (red circles)
    apple_positions = [(6, 6), (10, 6), (8, 9), (6, 10), (10, 10)]
    for ax, ay in apple_positions:
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx, ny = ax + dx, ay + dy
                if 4 <= nx <= 11 and 4 <= ny <= 11:
                    if dx + dy < 0:
                        grid[ny][nx] = Fl  # Apple light
                    elif dx + dy > 1:
                        grid[ny][nx] = Fd  # Apple dark
                    else:
                        grid[ny][nx] = F   # Apple base

    return grid


def build_broken_net():
    """Broken net: 32x16 (2x1 footprint) - torn netting on ground"""
    grid = [[T] * 32 for _ in range(16)]

    # Net colors (fiber/rope)
    Nd = (80, 70, 50, 255)    # Net dark
    N  = (120, 105, 80, 255)  # Net base
    Nl = (150, 135, 110, 255) # Net light

    # Tangled net strands (irregular mesh pattern)
    # Horizontal strands
    for y in [3, 7, 11]:
        for x in range(4, 28):
            if (x + y) % 5 != 0:  # Gaps for broken look
                grid[y][x] = Nl if x < 12 else (N if x < 20 else Nd)

    # Vertical/diagonal strands
    for x in [6, 12, 18, 24]:
        for y in range(2, 14):
            if (x + y) % 4 != 0:  # Gaps
                if grid[y][x] == T:
                    grid[y][x] = N

    # Torn edges (frayed bits)
    frays = [(3, 5), (28, 4), (5, 13), (26, 12), (15, 2), (17, 14)]
    for fx, fy in frays:
        if 0 <= fx < 32 and 0 <= fy < 16:
            grid[fy][fx] = Nl
            if fx + 1 < 32:
                grid[fy][fx + 1] = Nd

    return grid


def build_ladder():
    """Ladder: 16x24 (1x1 footprint) - leaning wooden ladder"""
    grid = [[T] * 16 for _ in range(24)]

    # Two side rails (slightly angled/leaning)
    for y in range(24):
        # Left rail
        x_left = 4 + (y // 8)
        if 0 <= x_left < 16:
            grid[y][x_left] = Wl
            if x_left + 1 < 16:
                grid[y][x_left + 1] = W

        # Right rail
        x_right = 10 + (y // 8)
        if 0 <= x_right < 16:
            grid[y][x_right] = W
            if x_right + 1 < 16:
                grid[y][x_right + 1] = Wd

    # Rungs (horizontal bars)
    for rung_y in [4, 9, 14, 19]:
        x_start = 5 + (rung_y // 8)
        x_end = 11 + (rung_y // 8)
        for x in range(x_start, x_end + 1):
            if 0 <= x < 16:
                grid[rung_y][x] = W
                grid[rung_y + 1][x] = Wd

    return grid


def build_net_post():
    """Net post: 16x24 (1x1 footprint) - wooden post with net attachment"""
    grid = [[T] * 16 for _ in range(24)]

    # Vertical post
    for y in range(24):
        for x in range(6, 10):
            if x < 7:
                grid[y][x] = Wl
            elif x > 8:
                grid[y][x] = Wd
            else:
                grid[y][x] = W

    # Crossbar at top
    for x in range(2, 14):
        for y in range(2, 4):
            if x < 6:
                grid[y][x] = Wl
            elif x > 9:
                grid[y][x] = Wd
            else:
                grid[y][x] = W

    # Net remnant hanging from crossbar
    net_color = (120, 105, 80, 255)
    for x in [3, 6, 9, 12]:
        for y in range(4, 8):
            if (y + x) % 2 == 0:
                grid[y][x] = net_color

    return grid


def build_bait_basket():
    """Bait basket: 16x16 (1x1 footprint) - small woven basket"""
    grid = [[T] * 16 for _ in range(16)]

    # Basket colors (woven material)
    Bkd = (90, 70, 40, 255)   # Basket dark
    Bk  = (130, 100, 60, 255) # Basket base
    Bkl = (170, 140, 90, 255) # Basket light

    # Basket body (round from above)
    for y in range(4, 14):
        for x in range(4, 12):
            dx, dy = x - 8, y - 9
            dist = (dx * dx + dy * dy) ** 0.5

            if dist < 4:
                # Woven pattern
                if (x + y) % 2 == 0:
                    grid[y][x] = Bkl if x < 8 else Bk
                else:
                    grid[y][x] = Bk if x < 8 else Bkd

    # Rim at top
    for x in range(4, 12):
        grid[4][x] = Bkl
        grid[5][x] = Bk

    # Handle
    for x in range(6, 10):
        grid[2][x] = Bk
        grid[3][x] = Bkd

    # Dark interior visible
    for y in range(6, 12):
        for x in range(5, 11):
            dx, dy = x - 8, y - 9
            if (dx * dx + dy * dy) ** 0.5 < 2.5:
                grid[y][x] = (50, 40, 25, 255)  # Dark inside

    return grid


# Build all sprites
TREE_OAK = build_tree_oak()
TREE_PINE = build_tree_pine()
TREE_DEAD = build_tree_dead()
TREE_PALM = build_tree_palm()
TREE_FRUIT = build_tree_fruit()
BUSH = build_bush()
ROCK_SMALL = build_rock_small()
ROCK_LARGE = build_rock_large()
TALL_GRASS = build_tall_grass()
REEDS = build_reeds()
MUSHROOM_RED = build_mushroom_red()
MUSHROOM_GLOW = build_mushroom_glow()
FLOWER_RED = build_flower(FLRd, FLR, FLRl)
FLOWER_BLUE = build_flower(FLBd, FLB, FLBl)
FLOWER_YELLOW = build_flower(FLYd, FLY, FLYl)
FLOWER_WILD = build_flower(FLWd, FLW, FLWl)
SUNFLOWER = build_sunflower()
CRYSTAL_SMALL = build_crystal_small()
CRYSTAL_LARGE = build_crystal_large()
STALAGMITE = build_stalagmite()
BONE_PILE = build_bone_pile()
ANT_MOUND = build_ant_mound()

# Village props
STUMP = build_stump()
LOG_PILE = build_log_pile()
COMPOST_PILE = build_compost_pile()
APPLE_CRATE = build_apple_crate()
BROKEN_NET = build_broken_net()
LADDER = build_ladder()
NET_POST = build_net_post()
BAIT_BASKET = build_bait_basket()


def main():
    output_dir = "/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Sprites/Objects"
    os.makedirs(output_dir, exist_ok=True)

    sprites = [
        # Trees
        ("tree_oak.png", TREE_OAK),
        ("tree_pine.png", TREE_PINE),
        ("tree_dead.png", TREE_DEAD),
        ("tree_palm.png", TREE_PALM),
        ("tree_fruit.png", TREE_FRUIT),
        # Rocks
        ("rock_small.png", ROCK_SMALL),
        ("rock_large.png", ROCK_LARGE),
        # Vegetation
        ("bush.png", BUSH),
        ("tall_grass.png", TALL_GRASS),
        ("reeds.png", REEDS),
        # Mushrooms
        ("mushroom_red.png", MUSHROOM_RED),
        ("mushroom_glow.png", MUSHROOM_GLOW),
        # Flowers
        ("flower_red.png", FLOWER_RED),
        ("flower_blue.png", FLOWER_BLUE),
        ("flower_yellow.png", FLOWER_YELLOW),
        ("flower_wild.png", FLOWER_WILD),
        ("sunflower.png", SUNFLOWER),
        # Cave objects
        ("crystal_small.png", CRYSTAL_SMALL),
        ("crystal_large.png", CRYSTAL_LARGE),
        ("stalagmite.png", STALAGMITE),
        ("bone_pile.png", BONE_PILE),
        # Special
        ("ant_mound.png", ANT_MOUND),
        # Village props
        ("stump.png", STUMP),
        ("log_pile.png", LOG_PILE),
        ("compost_pile.png", COMPOST_PILE),
        ("apple_crate.png", APPLE_CRATE),
        ("broken_net.png", BROKEN_NET),
        ("ladder.png", LADDER),
        ("net_post.png", NET_POST),
        ("bait_basket.png", BAIT_BASKET),
    ]

    for filename, grid in sprites:
        img = create_sprite_from_grid(grid)
        path = f"{output_dir}/{filename}"
        img.save(path)
        print(f"Created: {path} ({img.size[0]}x{img.size[1]})")

    print(f"\nGenerated {len(sprites)} object sprites")
    print("\nUnity import settings:")
    print("  - Pixels Per Unit: 16")
    print("  - Filter Mode: Point (no filter)")
    print("  - Compression: None")
    print("  - Pivot: Bottom Center (for trees)")


if __name__ == "__main__":
    main()
