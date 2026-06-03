#!/usr/bin/env python3
"""Generate player character sprites for Bug Farmer.

STYLE: Zelda/Terraria-ish top-down RPG character.
SIZE: 16x32 px = 1 cell wide x 2 cells tall at PPU 16 (one footprint wide, two tall).
(Previously 32x48 = 2 wide x 3 tall; shrunk per design.)

Characters: farmer (default), ranger, scholar, merchant.
4 directions each (down/up/left/right); right is the mirror of left.
Output -> Resources/Player (what make_scene + the game load).
"""

from PIL import Image
import os

W, H = 16, 32  # sprite frame

# === SHARED COLORS ===
T   = (0, 0, 0, 0)           # Transparent
O   = (24, 20, 24, 255)      # Outline (dark)
BLK = (0, 0, 0, 255)         # Pupils
EW  = (255, 255, 255, 255)   # Eye white

SK  = (248, 200, 144, 255)   # Skin light
SKd = (208, 152, 104, 255)   # Skin shadow
BT  = (80, 56, 40, 255)      # Boots

PALETTES = {
    'farmer':   {'hair': ((144, 88, 56, 255), (96, 56, 32, 255)),
                 'shirt': ((64, 176, 144, 255), (40, 120, 96, 255)),
                 'pants': ((144, 104, 64, 255), (96, 64, 40, 255))},
    'ranger':   {'hair': ((170, 95, 70, 255), (120, 55, 35, 255)),
                 'shirt': ((95, 150, 100, 255), (60, 105, 65, 255)),
                 'pants': ((100, 75, 55, 255), (65, 45, 30, 255))},
    'scholar':  {'hair': ((55, 55, 65, 255), (30, 30, 40, 255)),
                 'shirt': ((100, 130, 185, 255), (65, 90, 140, 255)),
                 'pants': ((115, 115, 120, 255), (80, 80, 85, 255))},
    'merchant': {'hair': ((210, 175, 110, 255), (170, 135, 75, 255)),
                 'shirt': ((185, 85, 85, 255), (140, 55, 55, 255)),
                 'pants': ((175, 150, 110, 255), (135, 110, 75, 255))},
}


def img(grid):
    for i, row in enumerate(grid):
        assert len(row) == W, f"row {i} has {len(row)} cols, expected {W}"
    assert len(grid) == H, f"grid has {len(grid)} rows, expected {H}"
    im = Image.new('RGBA', (W, H), T)
    px = im.load()
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            px[x, y] = c
    return im


def make_down(h, hd, c, cd, p, pd):
    _ = T; o = O; b = BLK; s, sd = SK, SKd; bt = BT
    return [
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],  # 0
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],  # 1
        [_,_,_,_,o,o,o,o,o,o,o,o,_,_,_,_],  # 2 hair top
        [_,_,_,o,h,h,h,h,h,h,h,h,o,_,_,_],  # 3
        [_,_,_,o,h,h,h,h,h,h,h,h,o,_,_,_],  # 4
        [_,_,_,o,h,h,h,h,h,h,h,h,o,_,_,_],  # 5
        [_,_,_,o,h,h,s,s,s,s,h,h,o,_,_,_],  # 6 face
        [_,_,_,o,h,s,s,s,s,s,s,h,o,_,_,_],  # 7
        [_,_,_,o,h,s,b,s,s,b,s,h,o,_,_,_],  # 8 eyes
        [_,_,_,o,h,s,s,s,s,s,s,h,o,_,_,_],  # 9
        [_,_,_,o,h,s,s,s,s,s,s,h,o,_,_,_],  # 10
        [_,_,_,_,o,s,s,s,s,s,s,o,_,_,_,_],  # 11 chin
        [_,_,_,_,_,o,sd,s,s,sd,o,_,_,_,_,_],# 12 jaw
        [_,_,_,_,_,o,s,s,s,s,o,_,_,_,_,_],  # 13 neck
        [_,_,_,o,o,o,o,o,o,o,o,o,o,_,_,_],  # 14 shoulders
        [_,_,o,o,c,c,c,c,c,c,c,c,o,o,_,_],  # 15 arm caps
        [_,_,o,c,c,c,c,c,c,c,c,c,c,o,_,_],  # 16 arms
        [_,_,o,s,c,c,c,c,c,c,c,c,s,o,_,_],  # 17 hands
        [_,_,_,o,c,c,c,c,c,c,c,c,o,_,_,_],  # 18
        [_,_,_,o,c,c,c,c,c,c,c,c,o,_,_,_],  # 19
        [_,_,_,o,c,c,cd,cd,cd,cd,c,c,o,_,_,_],# 20
        [_,_,_,o,c,cd,cd,cd,cd,cd,cd,c,o,_,_,_],# 21
        [_,_,_,o,cd,cd,cd,cd,cd,cd,cd,cd,o,_,_,_],# 22
        [_,_,_,_,o,o,o,o,o,o,o,o,_,_,_,_],  # 23 belt
        [_,_,_,o,pd,pd,pd,pd,pd,pd,pd,pd,o,_,_,_],# 24 waist
        [_,_,_,o,p,p,p,o,o,p,p,p,o,_,_,_],  # 25 legs
        [_,_,_,o,p,p,p,o,o,p,p,p,o,_,_,_],  # 26
        [_,_,_,o,p,p,p,o,o,p,p,p,o,_,_,_],  # 27
        [_,_,_,o,p,p,pd,o,o,pd,p,p,o,_,_,_],# 28
        [_,_,_,o,pd,pd,pd,o,o,pd,pd,pd,o,_,_,_],# 29
        [_,_,_,o,bt,bt,bt,o,o,bt,bt,bt,o,_,_,_],# 30 boots
        [_,_,_,o,o,o,o,_,_,o,o,o,o,_,_,_],  # 31 soles
    ]


def make_up(h, hd, c, cd, p, pd):
    _ = T; o = O; s, sd = SK, SKd; bt = BT
    return [
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],  # 0
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],  # 1
        [_,_,_,_,o,o,o,o,o,o,o,o,_,_,_,_],  # 2
        [_,_,_,o,h,h,h,h,h,h,h,h,o,_,_,_],  # 3
        [_,_,_,o,h,h,h,h,h,h,h,h,o,_,_,_],  # 4
        [_,_,_,o,h,h,h,h,h,h,h,h,o,_,_,_],  # 5
        [_,_,_,o,h,h,h,h,h,h,h,h,o,_,_,_],  # 6
        [_,_,_,o,h,h,h,h,h,h,h,h,o,_,_,_],  # 7
        [_,_,_,o,h,h,h,h,h,h,h,h,o,_,_,_],  # 8
        [_,_,_,o,h,h,h,h,h,h,h,h,o,_,_,_],  # 9
        [_,_,_,o,hd,h,h,h,h,h,h,hd,o,_,_,_],# 10
        [_,_,_,_,o,hd,h,h,h,h,hd,o,_,_,_,_],# 11
        [_,_,_,_,_,o,hd,hd,hd,hd,o,_,_,_,_,_],# 12
        [_,_,_,_,_,o,s,s,s,s,o,_,_,_,_,_],  # 13 neck
        [_,_,_,o,o,o,o,o,o,o,o,o,o,_,_,_],  # 14
        [_,_,o,o,c,c,c,c,c,c,c,c,o,o,_,_],  # 15
        [_,_,o,c,c,c,c,c,c,c,c,c,c,o,_,_],  # 16
        [_,_,o,s,c,c,c,c,c,c,c,c,s,o,_,_],  # 17 hands
        [_,_,_,o,c,c,c,c,c,c,c,c,o,_,_,_],  # 18
        [_,_,_,o,c,c,c,c,c,c,c,c,o,_,_,_],  # 19
        [_,_,_,o,c,c,cd,cd,cd,cd,c,c,o,_,_,_],# 20
        [_,_,_,o,c,cd,cd,cd,cd,cd,cd,c,o,_,_,_],# 21
        [_,_,_,o,cd,cd,cd,cd,cd,cd,cd,cd,o,_,_,_],# 22
        [_,_,_,_,o,o,o,o,o,o,o,o,_,_,_,_],  # 23 belt
        [_,_,_,o,pd,pd,pd,pd,pd,pd,pd,pd,o,_,_,_],# 24
        [_,_,_,o,p,p,p,o,o,p,p,p,o,_,_,_],  # 25
        [_,_,_,o,p,p,p,o,o,p,p,p,o,_,_,_],  # 26
        [_,_,_,o,p,p,p,o,o,p,p,p,o,_,_,_],  # 27
        [_,_,_,o,p,p,pd,o,o,pd,p,p,o,_,_,_],# 28
        [_,_,_,o,pd,pd,pd,o,o,pd,pd,pd,o,_,_,_],# 29
        [_,_,_,o,bt,bt,bt,o,o,bt,bt,bt,o,_,_,_],# 30
        [_,_,_,o,o,o,o,_,_,o,o,o,o,_,_,_],  # 31
    ]


def make_left(h, hd, c, cd, p, pd):
    _ = T; o = O; b = BLK; s, sd = SK, SKd; bt = BT
    return [
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],  # 0
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],  # 1
        [_,_,_,_,o,o,o,o,o,o,o,o,_,_,_,_],  # 2
        [_,_,_,o,h,h,h,h,h,h,h,h,o,_,_,_],  # 3
        [_,_,_,o,h,h,h,h,h,h,h,h,o,_,_,_],  # 4
        [_,_,_,o,s,s,h,h,h,h,h,h,o,_,_,_],  # 5 face front (left)
        [_,_,_,o,s,s,s,h,h,h,h,h,o,_,_,_],  # 6
        [_,_,_,o,s,b,s,s,h,h,h,h,o,_,_,_],  # 7 eye
        [_,_,_,o,s,s,s,s,h,h,h,h,o,_,_,_],  # 8
        [_,_,_,o,sd,s,s,s,h,h,h,h,o,_,_,_],  # 9 nose hint
        [_,_,_,_,o,s,s,s,h,h,h,o,_,_,_,_],  # 10
        [_,_,_,_,o,s,s,s,sd,h,o,_,_,_,_,_],  # 11 chin
        [_,_,_,_,_,o,s,s,s,o,_,_,_,_,_,_],  # 12 jaw
        [_,_,_,_,_,o,s,s,s,o,_,_,_,_,_,_],  # 13 neck
        [_,_,_,_,o,o,o,o,o,o,o,_,_,_,_,_],  # 14 shoulders (narrow)
        [_,_,_,o,c,c,c,c,c,c,c,o,_,_,_,_],  # 15
        [_,_,_,o,s,c,c,c,c,c,c,o,_,_,_,_],  # 16 front hand
        [_,_,_,o,s,c,c,c,c,c,c,o,_,_,_,_],  # 17
        [_,_,_,o,c,c,c,c,c,c,c,o,_,_,_,_],  # 18
        [_,_,_,o,c,c,cd,cd,cd,cd,c,o,_,_,_,_],# 19
        [_,_,_,o,c,cd,cd,cd,cd,cd,c,o,_,_,_,_],# 20
        [_,_,_,o,cd,cd,cd,cd,cd,cd,cd,o,_,_,_,_],# 21
        [_,_,_,o,cd,cd,cd,cd,cd,cd,cd,o,_,_,_,_],# 22
        [_,_,_,_,o,o,o,o,o,o,o,_,_,_,_,_],  # 23 belt
        [_,_,_,o,pd,pd,pd,pd,pd,pd,pd,o,_,_,_,_],# 24
        [_,_,_,o,p,p,p,pd,p,p,p,o,_,_,_,_],  # 25 leg (side, single)
        [_,_,_,o,p,p,p,pd,p,p,p,o,_,_,_,_],  # 26
        [_,_,_,o,p,p,p,pd,p,p,p,o,_,_,_,_],  # 27
        [_,_,_,o,p,p,pd,pd,pd,p,p,o,_,_,_,_],# 28
        [_,_,_,o,pd,pd,pd,pd,pd,pd,pd,o,_,_,_,_],# 29
        [_,_,_,o,bt,bt,bt,bt,bt,bt,bt,o,_,_,_,_],# 30 boot (forward)
        [_,_,_,_,o,o,o,o,o,o,o,o,_,_,_,_],  # 31 sole
    ]


def make_right(h, hd, c, cd, p, pd):
    return [row[::-1] for row in make_left(h, hd, c, cd, p, pd)]


def generate_character(name, palette, output_dir):
    h, hd = palette['hair']; c, cd = palette['shirt']; p, pd = palette['pants']
    sprites = [
        (f"{name}_down.png", make_down(h, hd, c, cd, p, pd)),
        (f"{name}_up.png", make_up(h, hd, c, cd, p, pd)),
        (f"{name}_left.png", make_left(h, hd, c, cd, p, pd)),
        (f"{name}_right.png", make_right(h, hd, c, cd, p, pd)),
    ]
    for filename, grid in sprites:
        img(grid).save(f"{output_dir}/{filename}")
        print(f"Created: {output_dir}/{filename}")
    sheet = Image.new('RGBA', (W * 4, H), T)
    for i, (_, grid) in enumerate(sprites):
        sheet.paste(img(grid), (i * W, 0))
    sheet.save(f"{output_dir}/{name}_spritesheet.png")


def main():
    output_dir = "/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Resources/Player"
    os.makedirs(output_dir, exist_ok=True)
    print("Generating 16x32 player sprites...")
    for name, palette in PALETTES.items():
        print(f"\n{name.upper()}:")
        generate_character(name, palette, output_dir)
    print(f"\nDone: {len(PALETTES)} chars x 5 files. PPU 16 -> 1x2 cells.")


if __name__ == "__main__":
    main()
