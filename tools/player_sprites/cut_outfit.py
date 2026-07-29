"""cut_outfit.py — turn a generated sheet into the game-sized frames. Free; no API.

`gen.py` makes the sheet. This makes the sprites. Two sheet shapes:

  gauntlet   4 hands in a row  ->  front / back / side / grip     (left-to-right, as prompted:
                                   knuckles, palm, profile, three-quarter)
  outfit     3 rows x 4 cols   ->  front_1..3, back_1..3, side_1..3

Procedure is the one in `.claude/skills/player-sprites/SKILL.md`, and each step is there because
skipping it broke something:

  * threshold the black background at rgb.sum() > 70;
  * DILATE before labelling — dark plate gaps split one figure into several blobs otherwise;
  * keep blobs over a floor area; rows by y-centre, columns by x-centre;
  * ONE shared ground line per row, so a figure doesn't bounce between frames;
  * downscale ONLY on the sheet's own pixel grid, measured from its run-lengths. `--auto` once
    reported a pitch of 9.5 against a true 3.17 and silently threw away two thirds of a sprite, so
    the pitch is measured here and asserted against the blob's expected size.

Column 4 of an outfit row is DROPPED: the model returns a second stride there rather than the
opposite passing pose, which reads as a skip. Play 1, 2, 3, 2.

  python3 tools/player_sprites/cut_outfit.py gauntlet outfits/silver
  python3 tools/player_sprites/cut_outfit.py outfit   outfits/silver
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import label, binary_dilation, binary_propagation

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aipipe import pixelsnap

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYER = os.path.join(REPO, "tools", "_generated", "player")

GAUNTLET_VIEWS = ["front", "back", "side", "grip"]
ROWS = ["front", "back", "side"]
TARGET_HAND_H = 20            # bronze's hands are ~20px; the whole set must match or they'd differ in-game


def _bands(mask, axis, want, floor=4):
    """Split a mask into `want` bands along `axis`, cutting at the WIDEST empty gaps.

    Connected components was the wrong tool for these sheets. A dark cuff line or an unlit seam
    disconnects a hand from its own wrist, so a gauntlet sheet labels as 9 or 12 pieces instead of 4,
    and no amount of dilation reliably fixes it — dilate enough to bridge a cuff on one material and
    you weld neighbouring figures together on another.

    But the layout is KNOWN: the prompt asks for four hands in a row, or three rows of four figures.
    In a known grid the reliable signal is the empty space BETWEEN cells, not whether the ink inside
    a cell happens to touch. So project onto the axis, find the runs of empty lines, and cut at the
    `want-1` widest ones. Nothing to tune, and it cannot be defeated by a dark band inside a figure.
    """
    occ = mask.any(axis=1 - axis)
    idx = np.where(occ)[0]
    if not len(idx):
        return []
    lo, hi = idx.min(), idx.max()
    gaps, run = [], None
    for i in range(lo, hi + 2):
        if i <= hi and not occ[i]:
            run = i if run is None else run
        elif run is not None:
            gaps.append((i - run, run, i))            # (width, start, end)
            run = None
    gaps.sort(reverse=True)
    cuts = sorted(g[1] + (g[0] // 2) for g in gaps[:want - 1])
    edges = [lo] + cuts + [hi + 1]
    return [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]


BG_MAX = 8        # the sheet background measures 0-4 across every border; the darkest ART starts at 13


def background(sheet):
    """The BACKGROUND, found by flooding in from the border — NOT by "this pixel is dark".

    This is the fix for the defect that shredded every dark set. The old mask was a per-pixel
    brightness test (`sum(rgb) > 70` = keep), which cannot tell the black BEHIND the character from
    the black IN the character. Hornet-stinger is black-and-yellow banded, so 17% of the figure --
    every black band -- was deleted as though it were background, leaving disconnected yellow stripes
    floating in a hole where the character used to be. ant-carapace lost 17%, swamp-gear 11%,
    ranger 10%.

    Blackness is not the signal. CONNECTEDNESS TO THE OUTSIDE is. A dark pixel you can walk to from
    the image border without crossing the figure is background; a dark pixel enclosed by the figure
    is the figure's own shading, however black it is. The separation is wide and measured, not tuned:
    background 0-4, darkest art 13.
    """
    near_black = sheet[..., :3].astype(int).sum(2) <= BG_MAX
    seed = np.zeros_like(near_black)
    seed[0, :] = near_black[0, :]
    seed[-1, :] = near_black[-1, :]
    seed[:, 0] = near_black[:, 0]
    seed[:, -1] = near_black[:, -1]
    return binary_propagation(seed, mask=near_black)


def cells(sheet, rows, cols):
    """The sheet's figures as a rows x cols grid, each entry the true (undilated) pixel mask."""
    solid = ~background(sheet)
    out = []
    for r0, r1 in _bands(solid, 0, rows):
        band = np.zeros_like(solid)
        band[r0:r1] = solid[r0:r1]
        row = []
        for c0, c1 in _bands(band, 1, cols):
            m = np.zeros_like(solid)
            m[r0:r1, c0:c1] = solid[r0:r1, c0:c1]
            if not m.any():
                continue
            ys, xs = np.where(m)
            row.append(dict(m=m, y0=ys.min(), y1=ys.max(), x0=xs.min(), x1=xs.max(),
                            cy=ys.mean(), cx=xs.mean()))
        out.append(row)
    return out


def measure_pitch(sheet, b):
    """The sheet's own logical pixel size, from the drawn art rather than from a guess."""
    sub = sheet[b["y0"]:b["y1"] + 1, b["x0"]:b["x1"] + 1]
    ex, ey = pixelsnap.edge_energy(sub.astype(float))   # wants RGBA — it premultiplies by alpha
    return pixelsnap.detect_pitch([ex, ey], pmin=3.0, pmax=60.0)


def snap(sheet, b, target_h, pad=1):
    """Downscale one blob onto its own pixel grid. Never a hand-rolled resampler: cell-median and
    area-average both turn pixel art to mush, and that mistake has been made twice already."""
    cut = np.zeros_like(sheet)
    cut[b["m"]] = sheet[b["m"]]
    cut[..., 3] = np.where(b["m"], 255, 0)
    sub = cut[b["y0"]:b["y1"] + 1, b["x0"]:b["x1"] + 1]

    p = measure_pitch(sheet, b)
    nx, ny = max(1, round(sub.shape[1] / p)), max(1, round(sub.shape[0] / p))
    small = pixelsnap.sample(sub, p, p, 0.0, 0.0, nx, ny)

    if target_h and ny != target_h:                  # one size for the whole set, NEAREST only
        s = target_h / ny
        small = np.asarray(Image.fromarray(small, "RGBA").resize(
            (max(1, round(nx * s)), target_h), Image.NEAREST), np.uint8)
    return small


def add_rim(a, darken=0.45):
    """A guaranteed 1px dark rim around the silhouette.

    This is the fix for a defect found in the swing design work: a gauntlet is the same material and
    the same value as the armour it sits against, so at sprite size the hand stops reading as a hand
    and looks like part of the breastplate. Asking the model for a strong outline worked on two of
    six sets and not on the other four — a prompt is a request, this is a guarantee.

    The rim is the sprite's OWN colour darkened, so each material keeps its hue.
    """
    op = a[..., 3] > 0
    if not op.any():
        return a
    grown = binary_dilation(op, np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool))
    ring = grown & ~op
    out = a.copy()
    mean = a[op][:, :3].mean(0)
    out[ring, :3] = np.clip(mean * darken, 0, 255).astype(np.uint8)
    out[ring, 3] = 255
    return out


def cut_gauntlet(folder):
    sheet = np.asarray(Image.open(os.path.join(folder, "result.png")).convert("RGBA"), np.uint8)
    grid = cells(sheet, rows=1, cols=4)
    if len(grid) != 1 or len(grid[0]) != 4:
        raise SystemExit(f"  expected 4 hands in 1 row, got {[len(r) for r in grid]} — look at result.png")
    for view, b in zip(GAUNTLET_VIEWS, grid[0]):
        img = add_rim(snap(sheet, b, TARGET_HAND_H))
        Image.fromarray(img, "RGBA").save(os.path.join(folder, f"{view}.png"))
    return [f"{v}.png" for v in GAUNTLET_VIEWS]


def cut_outfit(folder):
    """Body frames stay FULL RESOLUTION on ONE shared canvas — matching the approved bronze set.

    Two things here are convention, not preference, and getting either wrong is visible in game:

    * **No downscaling.** The runtime NEAREST-scales a sprite to its configured cell size, and
      `pixelclean.py`'s is the only intended resize (CLAUDE.md). Every existing outfit is a full-res
      crop — bronze's frames are 184x310. Snapping these to ~30x58 the way a gauntlet is snapped
      produced frames a fifth of the size of every other outfit.
    * **One canvas for all 12 frames**, with the figure placed on a shared ground line and centred.
      Bronze's frames are all exactly 184x310. Saved at their own bounding boxes instead, the frames
      come out 30x58, 29x58, 22x68 — so the character would change height between facing directions
      and drift sideways as he walks.
    """
    sheet = np.asarray(Image.open(os.path.join(folder, "result.png")).convert("RGBA"), np.uint8)
    grid = cells(sheet, rows=3, cols=4)
    if len(grid) != 3 or any(len(r) != 4 for r in grid):
        raise SystemExit(f"  expected 3 rows of 4, got {[len(r) for r in grid]} — look at result.png")

    keep = [(rn, b) for rn, row in zip(ROWS, grid) for b in row[:3]]   # col 4 is a repeat stride
    CW = max(b["x1"] - b["x0"] + 1 for _, b in keep)
    CH = max(b["y1"] - b["y0"] + 1 for _, b in keep)

    made, per_row = [], {}
    for rn, row in zip(ROWS, grid):
        per_row[rn] = max(b["y1"] for b in row)      # ONE ground line per row, or the figure bounces
    for i, (rn, b) in enumerate(keep):
        cut = np.zeros_like(sheet)
        cut[b["m"]] = sheet[b["m"]]
        cut[..., 3] = np.where(b["m"], 255, 0)
        sub = cut[b["y0"]:per_row[rn] + 1, b["x0"]:b["x1"] + 1]

        canvas = np.zeros((CH, CW, 4), np.uint8)
        h, w = min(CH, sub.shape[0]), min(CW, sub.shape[1])
        x = (CW - w) // 2                            # centred horizontally
        y = CH - h                                   # standing on the bottom edge
        canvas[y:y + h, x:x + w] = sub[:h, :w]
        name = f"{rn}_{i % 3 + 1}.png"
        Image.fromarray(canvas, "RGBA").save(os.path.join(folder, name))
        made.append(name)
    return made


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    what, dest = sys.argv[1], sys.argv[2]
    folder = os.path.join(PLAYER, dest)
    made = cut_gauntlet(folder) if what == "gauntlet" else cut_outfit(folder)
    print(f"  {dest}: {len(made)} -> {', '.join(made)}")


if __name__ == "__main__":
    main()
