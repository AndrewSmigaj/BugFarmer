#!/usr/bin/env python3
"""Generate player character sprites for Bug Farmer.

STYLE: User-approved Zelda/Terraria style
=========================================
Based on user's hand-edited farmer_down-1.png

Characters:
- Farmer: Brown hair, Teal shirt, Brown pants (default)
- Ranger: Auburn hair, Green shirt, Dark brown pants
- Scholar: Black hair, Blue shirt, Gray pants
- Merchant: Blonde hair, Red shirt, Tan pants
"""

from PIL import Image
import os

# === SHARED COLORS ===
T   = (0, 0, 0, 0)           # Transparent
O   = (24, 20, 24, 255)      # Outline (dark)
BLK = (0, 0, 0, 255)         # Pure black (pupils)
EW  = (255, 255, 255, 255)   # Eye white

# Skin (shared by all characters)
SK  = (248, 200, 144, 255)   # Skin light
SKd = (208, 152, 104, 255)   # Skin shadow

# Boots (shared)
BT  = (80, 56, 40, 255)      # Boots

# === CHARACTER COLOR PALETTES ===
PALETTES = {
    'farmer': {
        'hair':  ((144, 88, 56, 255), (96, 56, 32, 255)),      # Brown
        'shirt': ((64, 176, 144, 255), (40, 120, 96, 255)),    # Teal
        'pants': ((144, 104, 64, 255), (96, 64, 40, 255)),     # Brown
    },
    'ranger': {
        'hair':  ((170, 95, 70, 255), (120, 55, 35, 255)),     # Auburn
        'shirt': ((95, 150, 100, 255), (60, 105, 65, 255)),    # Green
        'pants': ((100, 75, 55, 255), (65, 45, 30, 255)),      # Dark brown
    },
    'scholar': {
        'hair':  ((55, 55, 65, 255), (30, 30, 40, 255)),       # Black
        'shirt': ((100, 130, 185, 255), (65, 90, 140, 255)),   # Blue
        'pants': ((115, 115, 120, 255), (80, 80, 85, 255)),    # Gray
    },
    'merchant': {
        'hair':  ((210, 175, 110, 255), (170, 135, 75, 255)),  # Blonde
        'shirt': ((185, 85, 85, 255), (140, 55, 55, 255)),     # Red
        'pants': ((175, 150, 110, 255), (135, 110, 75, 255)),  # Tan
    },
}


def img(grid):
    height, width = len(grid), len(grid[0])
    im = Image.new('RGBA', (width, height), T)
    px = im.load()
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            px[x, y] = c
    return im


def make_down(h, hd, c, cd, p, pd):
    """Generate down-facing sprite with given colors."""
    _ = T
    o = O
    b = BLK
    s, sd = SK, SKd
    w = EW
    bt = BT

    return [
        # Row 0-7: Hair (big rectangular head top)
        [_,_,_,_,_,_,_,_,_,_,_,o,o,o,o,o,o,o,o,o,o,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,o,h,h,h,h,h,h,h,h,h,h,o,o,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,o,h,h,h,h,h,h,h,h,h,h,h,h,h,h,o,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,o,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,o,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,o,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,o,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,o,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,o,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,hd,o,_,_,_,_,_,_],
        # Row 8-10: Hair framing face
        [_,_,_,_,_,_,o,h,h,h,o,o,o,o,o,o,o,o,o,o,o,o,h,h,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,o,h,h,o,s,s,s,s,s,s,s,s,s,s,s,s,o,h,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,o,h,h,o,s,s,s,s,s,s,s,s,s,s,s,s,o,h,hd,o,_,_,_,_,_,_],
        # Row 11-14: Eyes (white with outlined pupils)
        [_,_,_,_,_,_,o,h,h,o,s,w,w,w,s,s,s,s,w,w,w,s,o,h,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,o,h,o,s,s,w,o,o,s,s,s,s,o,o,w,s,s,o,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,o,hd,o,s,s,w,o,o,s,s,s,s,o,o,w,s,s,o,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,o,hd,o,s,s,w,b,b,s,s,s,s,b,b,w,s,s,o,hd,o,_,_,_,_,_,_],
        # Row 15-17: Lower face
        [_,_,_,_,_,_,o,hd,o,s,s,s,s,s,s,s,s,s,s,s,s,s,s,o,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,o,hd,o,s,s,s,s,s,s,s,s,s,s,s,s,s,s,o,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,o,o,s,s,s,s,s,s,s,s,s,s,s,s,s,s,o,o,_,_,_,_,_,_,_],
        # Row 18-20: Chin/neck
        [_,_,_,_,_,_,_,_,o,sd,s,s,s,s,s,s,s,s,s,s,s,s,sd,o,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,o,sd,s,s,s,s,s,s,s,s,sd,o,o,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,o,o,sd,s,s,s,s,s,s,sd,o,o,_,_,_,_,_,_,_,_,_,_],
        # Row 21: Shoulder line
        [_,_,_,_,_,_,_,o,o,o,o,o,o,o,o,o,o,o,o,o,o,o,o,o,o,_,_,_,_,_,_,_],
        # Row 22-28: Shirt/body
        [_,_,_,_,_,_,b,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,_,_,_,_,_,_],
        [_,_,_,_,_,_,c,b,s,s,o,c,c,c,c,c,c,c,c,c,c,o,sd,sd,o,c,_,_,_,_,_,_],
        [_,_,_,_,_,_,c,b,s,s,o,c,c,c,c,c,c,c,c,c,c,o,sd,sd,o,c,_,_,_,_,_,_],
        [_,_,_,_,_,_,c,b,s,sd,o,c,c,c,c,c,c,c,c,c,c,o,sd,sd,o,cd,_,_,_,_,_,_],
        [_,_,_,_,_,_,c,b,sd,sd,o,c,c,c,c,c,c,c,c,c,c,o,sd,sd,o,cd,_,_,_,_,_,_],
        [_,_,_,_,_,_,b,o,o,o,o,cd,cd,cd,cd,cd,cd,cd,cd,cd,cd,o,o,o,o,o,_,_,_,_,_,_],
        # Row 29: Belt
        [_,_,_,_,_,_,_,_,_,_,o,o,o,o,o,o,o,o,o,o,o,o,_,_,_,_,_,_,_,_,_,_],
        # Row 30-36: Pants/legs
        [_,_,_,_,_,_,_,_,_,o,pd,pd,pd,pd,pd,o,o,pd,pd,pd,pd,pd,o,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,p,p,p,p,p,o,o,p,p,p,p,p,o,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,p,p,p,p,pd,o,o,p,p,p,p,pd,o,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,p,p,p,pd,o,_,_,o,p,p,p,pd,o,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,p,p,p,pd,o,_,_,o,p,p,p,pd,o,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,p,p,pd,pd,o,_,_,o,p,p,pd,pd,o,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,pd,pd,pd,o,o,_,_,o,pd,pd,pd,o,o,_,_,_,_,_,_,_,_,_],
        # Row 37-39: Feet
        [_,_,_,_,_,_,_,_,o,bt,bt,bt,bt,bt,o,_,_,o,bt,bt,bt,bt,bt,o,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,o,bt,bt,bt,bt,bt,o,_,_,o,bt,bt,bt,bt,bt,o,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,o,o,o,o,_,_,_,_,o,o,o,o,o,_,_,_,_,_,_,_,_,_],
        # Row 40-47: Bottom padding
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    ]


def make_up(h, hd, c, cd, p, pd):
    """Generate up-facing sprite (back view) with given colors."""
    _ = T
    o = O
    s, sd = SK, SKd
    bt = BT
    b = BLK

    return [
        # Row 0-7: Hair top (same as front)
        [_,_,_,_,_,_,_,_,_,_,_,o,o,o,o,o,o,o,o,o,o,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,o,h,h,h,h,h,h,h,h,h,h,o,o,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,o,h,h,h,h,h,h,h,h,h,h,h,h,h,h,o,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,o,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,o,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,o,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,o,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,o,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,o,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,hd,o,_,_,_,_,_,_],
        # Row 8-20: Back of head (all hair)
        [_,_,_,_,_,_,o,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,o,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,o,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,o,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,o,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,o,hd,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,o,hd,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,o,hd,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,o,hd,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,o,o,h,h,h,h,h,h,h,h,h,h,h,h,h,h,o,o,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,o,hd,h,h,h,h,h,h,h,h,h,h,h,h,hd,o,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,o,hd,h,h,h,h,h,h,h,h,hd,o,o,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,o,o,hd,h,h,h,h,h,h,hd,o,o,_,_,_,_,_,_,_,_,_,_],
        # Row 21: Shoulder line
        [_,_,_,_,_,_,_,o,o,o,o,o,o,o,o,o,o,o,o,o,o,o,o,o,o,_,_,_,_,_,_,_],
        # Row 22-28: Back of shirt
        [_,_,_,_,_,_,b,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,_,_,_,_,_,_],
        [_,_,_,_,_,_,c,b,s,s,o,c,c,c,c,c,c,c,c,c,c,o,sd,sd,o,c,_,_,_,_,_,_],
        [_,_,_,_,_,_,c,b,s,s,o,c,c,c,c,c,c,c,c,c,c,o,sd,sd,o,c,_,_,_,_,_,_],
        [_,_,_,_,_,_,c,b,s,sd,o,c,c,c,c,c,c,c,c,c,c,o,sd,sd,o,cd,_,_,_,_,_,_],
        [_,_,_,_,_,_,c,b,sd,sd,o,c,c,c,c,c,c,c,c,c,c,o,sd,sd,o,cd,_,_,_,_,_,_],
        [_,_,_,_,_,_,b,o,o,o,o,cd,cd,cd,cd,cd,cd,cd,cd,cd,cd,o,o,o,o,o,_,_,_,_,_,_],
        # Row 29: Belt
        [_,_,_,_,_,_,_,_,_,_,o,o,o,o,o,o,o,o,o,o,o,o,_,_,_,_,_,_,_,_,_,_],
        # Row 30-36: Pants/legs
        [_,_,_,_,_,_,_,_,_,o,pd,pd,pd,pd,pd,o,o,pd,pd,pd,pd,pd,o,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,p,p,p,p,p,o,o,p,p,p,p,p,o,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,p,p,p,p,pd,o,o,p,p,p,p,pd,o,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,p,p,p,pd,o,_,_,o,p,p,p,pd,o,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,p,p,p,pd,o,_,_,o,p,p,p,pd,o,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,p,p,pd,pd,o,_,_,o,p,p,pd,pd,o,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,pd,pd,pd,o,o,_,_,o,pd,pd,pd,o,o,_,_,_,_,_,_,_,_,_],
        # Row 37-39: Feet
        [_,_,_,_,_,_,_,_,o,bt,bt,bt,bt,bt,o,_,_,o,bt,bt,bt,bt,bt,o,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,o,bt,bt,bt,bt,bt,o,_,_,o,bt,bt,bt,bt,bt,o,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,o,o,o,o,_,_,_,_,o,o,o,o,o,_,_,_,_,_,_,_,_,_],
        # Row 40-47: Bottom padding
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    ]


def make_left(h, hd, c, cd, p, pd):
    """Generate left-facing sprite with given colors."""
    _ = T
    o = O
    b = BLK
    s, sd = SK, SKd
    w = EW
    bt = BT

    return [
        # Row 0-7: Hair
        [_,_,_,_,_,_,_,_,_,_,o,o,o,o,o,o,o,o,o,o,o,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,o,o,h,h,h,h,h,h,h,h,h,h,h,o,o,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,o,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,o,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,o,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,o,_,_,_,_,_,_,_],
        [_,_,_,_,_,o,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,o,_,_,_,_,_,_],
        [_,_,_,_,_,o,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,o,_,_,_,_,_,_],
        [_,_,_,_,_,o,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,o,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,hd,o,_,_,_,_,_,_],
        # Row 8-10: Face opening on left side
        [_,_,_,_,_,o,h,h,o,o,o,o,o,o,o,o,o,h,h,h,h,h,h,h,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,o,h,o,s,s,s,s,s,s,s,s,o,h,h,h,h,h,h,h,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,o,h,o,s,s,s,s,s,s,s,s,o,h,h,h,h,h,h,h,hd,o,_,_,_,_,_,_],
        # Row 11-14: Eye (one visible on left)
        [_,_,_,_,_,o,h,o,s,w,w,w,s,s,s,s,o,h,h,h,h,h,h,h,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,o,h,o,s,w,o,o,s,s,s,s,s,o,h,h,h,h,h,h,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,o,hd,o,s,w,o,o,s,s,s,s,s,o,h,h,h,h,h,h,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,o,hd,o,s,w,b,b,s,s,s,s,s,o,h,h,h,h,h,h,hd,o,_,_,_,_,_,_],
        # Row 15-17: Lower face
        [_,_,_,_,_,o,hd,o,s,s,s,s,s,s,s,s,s,o,h,h,h,h,h,h,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,o,hd,o,s,s,s,s,s,s,s,s,s,o,h,h,h,h,h,h,hd,o,_,_,_,_,_,_],
        [_,_,_,_,_,_,o,o,s,s,s,s,s,s,s,s,o,h,h,h,h,h,h,o,o,_,_,_,_,_,_,_],
        # Row 18-20: Chin
        [_,_,_,_,_,_,_,o,sd,s,s,s,s,s,s,s,o,h,h,h,h,h,hd,o,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,o,o,sd,s,s,s,s,o,o,h,h,h,hd,o,o,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,o,o,sd,sd,o,o,o,hd,hd,o,o,o,_,_,_,_,_,_,_,_,_,_],
        # Row 21: Shoulder line
        [_,_,_,_,_,_,_,o,o,o,o,o,o,o,o,o,o,o,o,o,o,o,o,o,_,_,_,_,_,_,_,_],
        # Row 22-28: Shirt/body
        [_,_,_,_,_,_,b,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,o,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,c,b,s,s,o,c,c,c,c,c,c,c,c,c,o,sd,sd,o,c,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,c,b,s,s,o,c,c,c,c,c,c,c,c,c,o,sd,sd,o,c,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,c,b,s,sd,o,c,c,c,c,c,c,c,c,c,o,sd,sd,o,cd,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,c,b,sd,sd,o,c,c,c,c,c,c,c,c,c,o,sd,sd,o,cd,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,b,o,o,o,o,cd,cd,cd,cd,cd,cd,cd,cd,cd,o,o,o,o,o,_,_,_,_,_,_,_],
        # Row 29: Belt
        [_,_,_,_,_,_,_,_,_,o,o,o,o,o,o,o,o,o,o,o,o,_,_,_,_,_,_,_,_,_,_,_],
        # Row 30-36: Pants/legs
        [_,_,_,_,_,_,_,_,_,o,pd,pd,pd,pd,o,o,pd,pd,pd,pd,o,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,p,p,p,p,o,o,p,p,p,p,o,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,p,p,p,pd,o,o,p,p,p,pd,o,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,p,p,pd,o,_,_,o,p,p,pd,o,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,p,p,pd,o,_,_,o,p,p,pd,o,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,p,pd,pd,o,_,_,o,p,pd,pd,o,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,pd,pd,o,o,_,_,o,pd,pd,o,o,_,_,_,_,_,_,_,_,_,_,_],
        # Row 37-39: Feet
        [_,_,_,_,_,_,_,_,o,bt,bt,bt,bt,o,_,_,o,bt,bt,bt,bt,o,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,o,bt,bt,bt,bt,o,_,_,o,bt,bt,bt,bt,o,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,o,o,o,o,_,_,_,_,o,o,o,o,_,_,_,_,_,_,_,_,_,_,_],
        # Row 40-47: Bottom padding
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
        [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    ]


def make_right(h, hd, c, cd, p, pd):
    """Generate right-facing sprite (mirror of left)."""
    return [row[::-1] for row in make_left(h, hd, c, cd, p, pd)]


def generate_character(name, palette, output_dir):
    """Generate all 4 directions for a character."""
    h, hd = palette['hair']
    c, cd = palette['shirt']
    p, pd = palette['pants']

    sprites = [
        (f"{name}_down.png", make_down(h, hd, c, cd, p, pd)),
        (f"{name}_up.png", make_up(h, hd, c, cd, p, pd)),
        (f"{name}_left.png", make_left(h, hd, c, cd, p, pd)),
        (f"{name}_right.png", make_right(h, hd, c, cd, p, pd)),
    ]

    for filename, grid in sprites:
        i = img(grid)
        path = f"{output_dir}/{filename}"
        i.save(path)
        print(f"Created: {path}")

    # Spritesheet
    sheet = Image.new('RGBA', (128, 48), T)
    for i, (_, grid) in enumerate(sprites):
        sheet.paste(img(grid), (i * 32, 0))
    sheet_path = f"{output_dir}/{name}_spritesheet.png"
    sheet.save(sheet_path)
    print(f"Created: {sheet_path}")


def main():
    output_dir = "/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Sprites/Player"
    os.makedirs(output_dir, exist_ok=True)

    print("Generating player character sprites...")
    print("=" * 50)

    for name, palette in PALETTES.items():
        print(f"\n{name.upper()}:")
        generate_character(name, palette, output_dir)

    print("\n" + "=" * 50)
    print(f"Generated {len(PALETTES)} characters x 5 files = {len(PALETTES) * 5} total files")
    print("\nUnity import settings:")
    print("  - Pixels Per Unit: 16")
    print("  - Filter Mode: Point (no filter)")
    print("  - Compression: None")


if __name__ == "__main__":
    main()
