#!/usr/bin/env python3
"""TILING CHECK — renders every block as a 3x3 patch and every wall as a small house, using the REAL
renderer (so the overhang/tiling matches the game). Bright base so any seam/gap shows through. Labels
each. Use this to confirm blocks tile like wall_stone before/after regenerating.
Renders to tools/_generated/previews/block_tiling.png.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder              # noqa: E402
from render import render_builder                # noqa: E402
from features.room import place_room             # noqa: E402

BLOCKS = ["dirt_block", "stone_block", "clay_block", "hard_stone_block", "sand_block", "sandstone_block",
          "ore_coal_block", "ore_copper_block", "ore_iron_block", "ore_tin_block", "ore_silver_block",
          "ore_gold_block", "ore_platinum_block", "ore_diamond_block", "quartz_block"]
WALLS = ["wall_stone", "wall_wood", "wall_brick", "wall_wood2", "wall_brick2"]

COLS = 5            # block patches per row
PATCH = 3           # 3x3
GAP = 2
MARGIN = 2
WALL_PITCH = 6
W = MARGIN + max(COLS * (PATCH + GAP), len(WALLS) * WALL_PITCH) + MARGIN   # fit blocks OR walls row
BLOCK_ROWS = (len(BLOCKS) + COLS - 1) // COLS
WALL_Y = MARGIN + BLOCK_ROWS * (PATCH + GAP) + 3
H = WALL_Y + 4 + MARGIN

LABELS = []         # (text, cell_x, cell_y) filled during build


def build():
    b = ZoneBuilder("scene_block_tiling", W, H, base_tile="grass", name="Block tiling check")
    # block patches
    for i, key in enumerate(BLOCKS):
        col, row = i % COLS, i // COLS
        x0 = MARGIN + col * (PATCH + GAP)
        y0 = MARGIN + row * (PATCH + GAP)
        for dx in range(PATCH):
            for dy in range(PATCH):
                b.place_occupant(key, x0 + dx, y0 + dy, surface=None, reserve=False)
        LABELS.append((key, x0, y0))
    # wall mini-houses
    for j, key in enumerate(WALLS):
        hx = MARGIN + j * WALL_PITCH
        place_room(b, hx, WALL_Y, hx + 3, WALL_Y + 2, floor="stone_floor", wall=key,
                   door="door_square", door_side="bottom")
        LABELS.append((key, hx, WALL_Y))
    return b


def label(out):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.open(out).convert("RGBA")
    cpx = img.width / W
    d = ImageDraw.Draw(img)
    f = ImageFont.load_default()
    for text, cx, cy in LABELS:
        px, py = int(cx * cpx), int((H - 1 - cy) * cpx)        # +Y north -> flip
        d.rectangle([px - 1, py - 1, px + 7 * len(text), py + 11], fill=(0, 0, 0, 200))
        d.text((px, py), text, fill=(255, 240, 150), font=f)
    img.save(out)


if __name__ == "__main__":
    b = build()
    out = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "block_tiling.png"))
    render_builder(b, out, scale=7)
    label(out)
    print("placeholders:", b.missing_art())
    print("warnings:", len(b.warnings))
    print("wrote", out)
