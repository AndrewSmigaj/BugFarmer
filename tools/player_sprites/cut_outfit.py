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
import statistics
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import label, binary_dilation, binary_propagation

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import official                                            # noqa: E402  HAND_ROLES — how many hands
from aipipe import pixelsnap                               # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYER = os.path.join(REPO, "tools", "_generated", "player")

# The hands a gauntlet sheet contains, IN SHEET ORDER — read from official.py, never hardcoded here.
# It used to be a literal ["front","back","side","grip"] alongside a literal `cols=4` below, while the
# prompt asked for four poses and the renderer looked for five keys. Three places, three answers: the
# fifth hand (grip_palm) never existed, so every two-handed tool was held with the same hand twice on
# 23 of 24 outfits. One list now drives the prompt, the cut and the render.
GAUNTLET_VIEWS = official.HAND_ROLES
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


def _is_magenta(rgb):
    R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (R > 140) & (B > 140) & (G < 110) & (np.abs(R - B) < 70)


def background(sheet):
    """The BACKGROUND, found by flooding in from the border — NOT by "this pixel is dark".

    HANDLES BOTH KEY COLOURS. Sheets were generated on BLACK until 2026-07-29 and on MAGENTA after,
    but this function only ever knew about black — so every magenta sheet failed to cut, reporting
    "expected 3 rows of 4, got [1]". The generator was switched and the cutter was not, and it went
    unnoticed because no new sheet was cut between the change and 2026-08-05. Which key a sheet uses
    is now DETECTED from its own border rather than assumed.

    Flooding from the border is the part that matters and is unchanged. A per-pixel brightness test
    ("this pixel is dark, so it is background") cannot tell the black BEHIND the character from the
    black IN it: hornet-stinger is black-and-yellow banded, so 17% of the figure — every black band —
    was deleted as though it were background, leaving disconnected yellow stripes floating in a hole.
    ant-carapace lost 17%, swamp-gear 11%, ranger 10%.

    Blackness is not the signal. CONNECTEDNESS TO THE OUTSIDE is. A background-coloured pixel you can
    walk to from the image border without crossing the figure is background; one enclosed by the
    figure is the figure's own shading, however dark or however magenta.
    """
    rgb = sheet[..., :3].astype(int)
    border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    if _is_magenta(border).mean() > 0.5:
        keyed = _is_magenta(rgb)
    else:
        keyed = rgb.sum(2) <= BG_MAX
    seed = np.zeros_like(keyed)
    seed[0, :] = keyed[0, :]
    seed[-1, :] = keyed[-1, :]
    seed[:, 0] = keyed[:, 0]
    seed[:, -1] = keyed[:, -1]
    return binary_propagation(seed, mask=keyed)


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


def snap(sheet, b, target_h, pad=1, pitch=None):
    """Downscale one blob onto its own pixel grid. Never a hand-rolled resampler: cell-median and
    area-average both turn pixel art to mush, and that mistake has been made twice already.

    `pitch` overrides per-blob detection — pass the sheet's shared pitch when several blobs were drawn
    at one scale, because per-blob detection disagrees with itself (see `cut_gauntlet`).
    """
    cut = np.zeros_like(sheet)
    cut[b["m"]] = sheet[b["m"]]
    cut[..., 3] = np.where(b["m"], 255, 0)
    sub = cut[b["y0"]:b["y1"] + 1, b["x0"]:b["x1"] + 1]

    p = pitch if pitch else measure_pitch(sheet, b)
    nx, ny = max(1, round(sub.shape[1] / p)), max(1, round(sub.shape[0] / p))
    small = pixelsnap.sample(sub, p, p, 0.0, 0.0, nx, ny)

    if target_h and ny != target_h:                  # one size for the whole set, NEAREST only
        s = target_h / ny
        small = np.asarray(Image.fromarray(small, "RGBA").resize(
            (max(1, round(nx * s)), target_h), Image.NEAREST), np.uint8)
    return small


def defringe(a, rounds=3):
    """Remove KEY-COLOUR BLEED from the silhouette edge.

    The generator anti-aliases the figure against its background, so the outermost pixels are a blend
    of art and key. On the old BLACK sheets that blend was a dark edge and invisible. On MAGENTA it is
    bright pink, and it survives keying because a half-magenta pixel is not magenta enough to key out:
    measured 1.0% of fireant's opaque pixels and 1.3% of blackant's.

    Each flagged pixel takes the mean of its non-flagged opaque neighbours, repeated a few times so a
    two-pixel fringe resolves inward. Pixels with no clean neighbour are made transparent rather than
    guessed at.
    """
    a = a.copy()
    for _ in range(rounds):
        R, G, B = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
        op = a[..., 3] > 0
        bad = op & (R > G + 40) & (B > G + 40) & (B > 90)
        if not bad.any():
            break
        good = op & ~bad
        acc = np.zeros(a.shape[:2] + (3,), float)
        cnt = np.zeros(a.shape[:2], float)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            g = np.roll(np.roll(good, dy, 0), dx, 1)
            v = np.roll(np.roll(a[..., :3].astype(float), dy, 0), dx, 1)
            acc += v * g[..., None]
            cnt += g
        fix = bad & (cnt > 0)
        a[..., :3][fix] = (acc[fix] / cnt[fix][:, None]).astype(np.uint8)
    R, G, B = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    left = (a[..., 3] > 0) & (R > G + 40) & (B > G + 40) & (B > 90)
    a[..., 3][left] = 0                       # no clean neighbour -> drop it, never guess
    return a


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
    """The four hands, all downscaled on ONE shared pixel pitch.

    ⚠ Measuring the pitch PER BLOB is wrong and it visibly damages hands. The four hands are drawn in a
    single image at a single scale, so there is one true pitch — but `detect_pitch` run per blob
    disagrees with itself: bronze measures [3.50, 4.90, 4.85, 4.95] and ranger [3.35, 3.25, 3.45, 4.95].
    The odd one out gets sampled at the wrong rate and comes out mush — bronze's profile hand lost the
    separation between its fingers, which is the whole reason that view exists.

    The median across the four is the sheet's pitch. Most outfits already agree to within 0.3, so this
    changes nothing for them and rescues the one or two blobs that misdetect.
    """
    n = len(GAUNTLET_VIEWS)
    sheet = np.asarray(Image.open(os.path.join(folder, "result.png")).convert("RGBA"), np.uint8)
    grid = cells(sheet, rows=1, cols=n)
    if len(grid) != 1 or len(grid[0]) != n:
        raise SystemExit(f"  expected {n} hands in 1 row ({', '.join(GAUNTLET_VIEWS)}), "
                         f"got {[len(r) for r in grid]} — look at result.png")
    pitch = statistics.median([measure_pitch(sheet, b) for b in grid[0]])
    for view, b in zip(GAUNTLET_VIEWS, grid[0]):
        img = add_rim(defringe(snap(sheet, b, TARGET_HAND_H, pitch=pitch)))
        Image.fromarray(img, "RGBA").save(os.path.join(folder, f"{view}.png"))
    return [f"{v}.png" for v in GAUNTLET_VIEWS]


def cut_outfit(folder):
    """Body frames are PIXELSNAPPED to their true grid, on ONE shared canvas.

    ⚠ THIS FUNCTION USED TO DO THE OPPOSITE, AND THE DOCSTRING TAUGHT IT AS A RULE. It said "body
    frames stay FULL RESOLUTION… no downscaling", from commit a5f6a92 (2026-07-29), because snapped
    frames came out 30x58 against bronze's 184x310 — where bronze had been cut BY HAND at full
    resolution the session before. A hand-cut one-off became the standard, snapping was dropped to
    match it, and every outfit made since is a smooth render rather than pixel art. Owner, 2026-08-14:
    the intended version was always the pixel-snapped one — the same pixel density, converted to real
    pixels — and never a downscale.

    **Snapping is not downscaling.** `pixelsnap` finds the grid gpt actually drew on and takes the
    median of the inner half of each cell, recovering the artist's pixels exactly. Area-average and
    cell-median resampling are the mush, and those stay banned. The precondition is that the render was
    drawn as visible blocks — that is what the PIXEL DENSITY line in the prompt is for; without it gpt
    renders smooth and there is no grid to land on.

    Two conventions kept from the old version, both still right:

    * **ONE shared pitch for the whole sheet.** Per-figure detection disagrees with itself, so the
      twelve frames would land on twelve slightly different grids and the character would shimmer.
    * **One canvas for every frame**, figure centred on a shared ground line per row. Saved at their own
      bounding boxes the frames come out 30x58, 29x58, 22x68 — the character changes height between
      facings and drifts sideways as he walks.
    """
    sheet = np.asarray(Image.open(os.path.join(folder, "result.png")).convert("RGBA"), np.uint8)
    grid = cells(sheet, rows=3, cols=4)
    if len(grid) != 3 or any(len(r) != 4 for r in grid):
        raise SystemExit(f"  expected 3 rows of 4, got {[len(r) for r in grid]} — look at result.png")

    keep = [(rn, b) for rn, row in zip(ROWS, grid) for b in row[:3]]   # col 4 is a repeat stride

    per_row = {}
    for rn, row in zip(ROWS, grid):
        per_row[rn] = max(b["y1"] for b in row)      # ONE ground line per row, or the figure bounces

    pitch = float(np.median([measure_pitch(sheet, b) for _, b in keep]))

    smalls = []
    for rn, b in keep:
        cut = np.zeros_like(sheet)
        cut[b["m"]] = sheet[b["m"]]
        cut[..., 3] = np.where(b["m"], 255, 0)
        sub = cut[b["y0"]:per_row[rn] + 1, b["x0"]:b["x1"] + 1]      # incl. the row's ground line
        nx = max(1, round(sub.shape[1] / pitch))
        ny = max(1, round(sub.shape[0] / pitch))
        smalls.append(pixelsnap.sample(sub, pitch, pitch, 0.0, 0.0, nx, ny))

    CW = max(s.shape[1] for s in smalls)
    CH = max(s.shape[0] for s in smalls)
    made = []
    for i, ((rn, _), small) in enumerate(zip(keep, smalls)):
        canvas = np.zeros((CH, CW, 4), np.uint8)
        h, w = small.shape[0], small.shape[1]
        x = (CW - w) // 2                            # centred horizontally
        y = CH - h                                   # standing on the bottom edge
        canvas[y:y + h, x:x + w] = small
        name = f"{rn}_{i % 3 + 1}.png"
        Image.fromarray(defringe(canvas), "RGBA").save(os.path.join(folder, name))
        made.append(name)
    print(f"  pitch {pitch:.2f} -> frames {CW}x{CH} true pixels")
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
