#!/usr/bin/env python3
"""dug_context_sheet.py - render dug-tile CANDIDATES in context for owner review.

Each candidate (from gen_dug_tiles.py raws) is box-downscaled to 32px (preserves the directional
shadow, unlike the seamless-tile devignette clean) and shown alone + centered in a 5x5 patch of each
neighbour ground (grass / dirt / stone / sand), so we can judge whether the "sunken" illusion reads in
context. One labelled sheet -> tools/_generated/previews/dug_experiment/CONTEXT_SHEET.png
"""
import os
from PIL import Image, ImageDraw

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(TOOLS, "_generated", "raw")
TILES = os.path.join(os.path.dirname(TOOLS), "BugFarmerClient", "Assets", "Resources", "Tiles")
OUT = os.path.join(TOOLS, "_generated", "previews", "dug_experiment", "CONTEXT_SHEET.png")

CANDS = ["dug_shallow", "dug_medium", "dug_deep", "dug_subsoil", "dug_bedrock", "dug_clay"]
NEIGHBORS = ["grass", "dirt", "stone_floor", "sand"]
T = 32          # tile px
N = 5           # patch is NxN
UP = 5          # final upscale
LBL = 90        # left label column (px, pre-upscale)
HDR = 16        # header row


def box(path, size=T, crop_frac=0.0):
    im = Image.open(path).convert("RGBA")
    if crop_frac > 0:                       # trim the near-white generation frame off the dug raws
        w, h = im.size
        c = int(w * crop_frac)
        im = im.crop((c, c, w - c, h - c))
    return im.resize((size, size), Image.BOX)


def patch(dug, neighbor):
    c = Image.new("RGBA", (N * T, N * T))
    for y in range(N):
        for x in range(N):
            c.paste(neighbor, (x * T, y * T))
    c.paste(dug, (N // 2 * T, N // 2 * T))   # dug in the centre
    return c


def main():
    dug = {k: box(os.path.join(RAW, f"dug_exp_{k}.png"), crop_frac=0.07) for k in CANDS}
    nb = {n: box(os.path.join(TILES, f"{n}.png")) for n in NEIGHBORS}

    cell_w = N * T            # each context cell
    col_alone = T * 2         # "alone" column (2x tile)
    cols = [("alone", col_alone)] + [(n, cell_w) for n in NEIGHBORS]
    row_h = N * T

    W = LBL + sum(w for _, w in cols) + 10 * len(cols)
    H = HDR + len(CANDS) * (row_h + 8)
    sheet = Image.new("RGBA", (W, H), (245, 245, 245, 255))
    d = ImageDraw.Draw(sheet)

    # header
    x = LBL
    for name, w in cols:
        d.text((x + 2, 2), name, fill=(30, 30, 30, 255))
        x += w + 10

    y = HDR
    for k in CANDS:
        d.text((2, y + row_h // 2), k, fill=(20, 20, 20, 255))
        x = LBL
        # alone (2x)
        sheet.paste(dug[k].resize((col_alone, col_alone), Image.NEAREST), (x, y))
        x += col_alone + 10
        for n in NEIGHBORS:
            sheet.paste(patch(dug[k], nb[n]), (x, y))
            x += cell_w + 10
        y += row_h + 8

    sheet = sheet.resize((W * UP, H * UP), Image.NEAREST)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sheet.save(OUT)
    print(f"-> {OUT}  ({sheet.size[0]}x{sheet.size[1]})")


if __name__ == "__main__":
    main()
