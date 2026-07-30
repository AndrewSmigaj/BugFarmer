"""net_options.py — every way the net swing could be oriented, on one page. FREE, no API.

  python3 tools/player_sprites/net_options.py

Writes `tools/_generated/player/NET_OPTIONS.png`.

WHY THIS EXISTS. The net swing has been wrong for five rounds. Each round produced a THEORY about what
"backwards" meant — the sweep direction, the sprite rotation, the hoop facing the camera — and each
theory was wrong; the last one was invented outright. Owner: "it is consistently net first, not the
opening but the net part ... you dont get it to the point of making up phantom things I might be
talking about."

So this stops arguing and enumerates. Eight combinations of the only three things that can actually
change, rendered identically, captioned, three frames each so the DIRECTION OF TRAVEL is visible:

  * which way the arc sweeps  — forward (toward the character's facing) or backward
  * what the sprite does      — as drawn / mirrored left-right / flipped top-bottom
  * which end leads           — head-out (normal) or head-flipped so the net TRAILS the hand

He points at a cell. That answer becomes the net motion. No more reasoning about nets.

The grip is recomputed on each TRANSFORMED sprite, so mirroring or flipping never leaves the fist
clamped on the wrong end — the bug that made an earlier attempt look worse rather than different.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swing_lab as S                                     # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYER = os.path.join(REPO, "tools", "_generated", "player")
OUTFIT = os.path.join(PLAYER, "outfits", "bronze")
RES = os.path.join(REPO, "BugFarmerClient", "Assets", "Resources")

# (label, sweep_forward, sprite transform, head flipped 180)
VARIANTS = [
    ("1  forward · as drawn        (what you are seeing now)", True,  None,     0),
    ("2  BACKWARD · as drawn",                                 False, None,     0),
    ("3  forward · mirrored L-R",                              True,  "mirror", 0),
    ("4  BACKWARD · mirrored L-R",                             False, "mirror", 0),
    ("5  forward · flipped top-bottom",                        True,  "flip",   0),
    ("6  BACKWARD · flipped top-bottom",                       False, "flip",   0),
    ("7  forward · NET TRAILS the hand",                       True,  None,     180),
    ("8  BACKWARD · NET TRAILS the hand",                      False, None,     180),
]
SHOTS = (0.15, 0.5, 0.85)          # three points through the swing, so travel direction is readable


def transformed(art, how):
    """Apply the sprite transform. The grip is measured AFTER this, never before."""
    if how == "mirror":
        return np.ascontiguousarray(art[:, ::-1])
    if how == "flip":
        return np.ascontiguousarray(art[::-1, :])
    return art


def build():
    side = S.rgba(os.path.join(OUTFIT, "side_2.png"))
    BH = S.bbox(side)[1] - S.bbox(side)[0] + 1
    CELL = BH / 2.0
    hand = S.scale_h(S.rgba(os.path.join(OUTFIT, "gauntlet", "front.png")), BH * S.HAND_FRAC)
    tiles = [S.rgba(os.path.join(RES, "Tiles", n)) for n in ("grass.png", "grass_v2.png", "grass_v3.png")]

    CW, CH = int(CELL * 2.6), int(CELL * 2.7)
    rng = np.random.RandomState(5)
    tile = np.zeros((CH, CW, 4), np.uint8)
    TS = int(CELL)
    for gy in range(0, CH + TS, TS):
        for gx in range(0, CW + TS, TS):
            S.paste(tile, S.scale_h(tiles[rng.randint(len(tiles))], TS), gx + TS / 2, gy + TS / 2)

    raw = S.rgba(os.path.join(RES, "Items", "small_net_icon.png"))
    LABEL = 26
    cells = []
    for label, fwd, how, headflip in VARIANTS:
        art = S.scale_h(transformed(raw, how), CELL)
        g = (S.grip_of(art) + S.DIAG * S.GRIP_EXTRA) * art.shape[0]   # grip of the TRANSFORMED sprite
        strip = Image.new("RGB", (CW * len(SHOTS), CH + LABEL), (24, 26, 24))
        for i, t in enumerate(SHOTS):
            sc = tile.copy()
            a = (140.0 - 180.0 * t) if fwd else (-40.0 + 180.0 * t)
            base = int(CH * 0.86)
            cy = base - BH // 2
            px = int(CW * 0.42)
            S.paste(sc, side, px, cy)
            ad = a + headflip
            r = math.radians(a)
            tx = px + math.cos(r) * 0.62 * CELL
            ty = cy - math.sin(r) * 0.62 * CELL
            S.paste(sc, S.rot(art, ad - S.ART_ANGLE), tx, ty)
            rr = math.radians(-(ad - S.ART_ANGLE))
            S.paste(sc, S.rot(hand, ad - S.ART_ANGLE + S.HAND_ROT),
                    tx + g[0] * math.cos(rr) - g[1] * math.sin(rr),
                    ty + g[0] * math.sin(rr) + g[1] * math.cos(rr))
            im = Image.new("RGBA", (CW, CH), (24, 26, 24, 255))
            im.alpha_composite(Image.fromarray(sc, "RGBA"))
            strip.paste(im.convert("RGB"), (i * CW, LABEL))
        d = ImageDraw.Draw(strip)
        d.text((6, 7), label, fill=(240, 240, 240))
        d.text((6, CH + LABEL - 18), "left = start of swing,  right = end", fill=(150, 150, 150))
        cells.append(strip)

    COLS = 2
    rows = (len(cells) + COLS - 1) // COLS
    w, h = cells[0].size
    page = Image.new("RGB", (w * COLS + 12 * (COLS - 1), h * rows + 12 * (rows - 1)), (12, 14, 12))
    for i, c in enumerate(cells):
        page.paste(c, ((i % COLS) * (w + 12), (i // COLS) * (h + 12)))
    out = os.path.join(PLAYER, "NET_OPTIONS.png")
    page.save(out)
    print(f"  {len(cells)} options -> {out.replace('/mnt/c/', 'C:/')}  ({page.size[0]}x{page.size[1]})")
    return out


if __name__ == "__main__":
    build()
