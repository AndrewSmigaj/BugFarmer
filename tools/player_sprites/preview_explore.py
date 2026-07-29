"""preview_explore.py — judge an `explore` sheet the way the game will show it. FREE, no API.

  python3 tools/player_sprites/preview_explore.py beetle-shell
  python3 tools/player_sprites/preview_explore.py --all

Writes `explore/<name>/REVIEW.png`: the three options large on grey, and underneath the SAME three
shrunk to real game height and standing on grass.

The bottom row is the row that decides. The ranger sheet's third option was the best-looking design
on the page and the worst one in the game — its gold filigree turned to noise the moment it was
shrunk, while the two plainer designs kept working. Big and pretty is not the same as legible, and
only one of those two things ships, so a design is not judged until it has been judged small.

Keying is by MAGENTA flooded in from the border. Two separate ideas, both load-bearing:
  * magenta, because it is a colour the armour never contains — on the old black sheets 8.9% of the
    ranger was indistinguishable from its own background, and the cutter deleted it;
  * from the BORDER, because a magenta-ish pixel enclosed by the figure is the figure's, not
    background. Per-pixel colour tests cannot tell those apart.
"""
import glob
import os
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import binary_propagation

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYER = os.path.join(REPO, "tools", "_generated", "player")
EXPLORE = os.path.join(PLAYER, "explore")
GRASS = os.path.join(REPO, "BugFarmerClient", "Assets", "Resources", "Tiles", "grass.png")
BASE = os.path.join(PLAYER, "bases", "armless_front.png")

GAME_H = 71          # the base sprite's height — the size these actually ship at
BIG = 2              # zoom for the top (large) row
SMALL = 6            # zoom for the bottom (game-size) row


def key(rgb):
    """True where the pixel is the FIGURE. Magenta reachable from the border is background."""
    R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mag = (R > 140) & (B > 140) & (G < 110) & (np.abs(R - B) < 70)
    seed = np.zeros_like(mag)
    seed[0, :], seed[-1, :] = mag[0, :], mag[-1, :]
    seed[:, 0], seed[:, -1] = mag[:, 0], mag[:, -1]
    return ~binary_propagation(seed, mask=mag)


def split(art, want=3):
    """Column ranges for `want` figures, cutting at the widest empty columns."""
    cols = art.any(0)
    idx = np.where(cols)[0]
    gaps, run = [], None
    for i in range(idx.min(), idx.max() + 2):
        if i <= idx.max() and not cols[i]:
            run = i if run is None else run
        elif run is not None:
            gaps.append((i - run, run))
            run = None
    gaps.sort(reverse=True)
    cuts = sorted(g[1] + g[0] // 2 for g in gaps[:want - 1])
    e = [idx.min()] + cuts + [idx.max() + 1]
    return [(e[i], e[i + 1]) for i in range(len(e) - 1)]


def figures(path, want=3):
    rgb = np.asarray(Image.open(path).convert("RGB"), int)
    art = key(rgb)
    rgba = np.dstack([rgb.astype(np.uint8), (art * 255).astype(np.uint8)])
    out = []
    for c0, c1 in split(art, want):
        m = np.zeros_like(art)
        m[:, c0:c1] = art[:, c0:c1]
        if not m.any():
            continue
        ys, xs = np.where(m)
        crop = rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
        crop[..., 3] = np.where(m[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
        out.append(Image.fromarray(crop, "RGBA"))
    return out


def review(name, want=3):
    src = os.path.join(EXPLORE, name, "result.png")
    if not os.path.exists(src):
        print(f"  {name}: no result.png")
        return None
    figs = figures(src, want)
    if len(figs) != want:
        print(f"  {name}: found {len(figs)} figures, expected {want} — look at result.png")
    small = [f.resize((max(1, round(f.width * GAME_H / f.height)), GAME_H), Image.LANCZOS)
             for f in figs]
    small.insert(0, Image.open(BASE).convert("RGBA"))          # the bare character, for scale

    cw = max(f.width for f in figs) * BIG + 40
    top_h = max(f.height for f in figs) * BIG
    bot_h = GAME_H * SMALL
    sw = max(len(figs) * cw, len(small) * (max(s.width for s in small) * SMALL + 40))
    sheet = Image.new("RGBA", (sw, top_h + bot_h + 30), (58, 58, 64, 255))

    g = Image.open(GRASS).convert("RGBA")
    g = g.resize((g.width * SMALL, g.height * SMALL), Image.NEAREST)
    for y in range(top_h + 30, sheet.height, g.height):
        for x in range(0, sheet.width, g.width):
            sheet.alpha_composite(g, (x, y))

    for i, f in enumerate(figs):
        b = f.resize((f.width * BIG, f.height * BIG), Image.NEAREST)
        sheet.alpha_composite(b, (i * cw + 20, top_h - b.height))
    step = max(s.width for s in small) * SMALL + 40
    for i, s in enumerate(small):
        b = s.resize((s.width * SMALL, s.height * SMALL), Image.NEAREST)
        sheet.alpha_composite(b, (i * step + 20, sheet.height - b.height - 6 * SMALL))

    out = os.path.join(EXPLORE, name, "REVIEW.png")
    sheet.convert("RGB").save(out)
    print(f"  {name}: {len(figs)} options -> REVIEW.png  (bottom row: bare base, then each at game size)")
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    names = ([os.path.basename(p) for p in sorted(glob.glob(os.path.join(EXPLORE, "*")))
              if os.path.isdir(p)] if "--all" in args else args)
    for n in names:
        review(n)
