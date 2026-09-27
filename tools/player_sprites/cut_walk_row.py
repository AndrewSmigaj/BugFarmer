"""cut_walk_row.py — turn a ONE-DIRECTION render into pixel-snapped frames. FREE, no API.

This is the cutter for the current generation approach: one call per direction, four walk frames in
a row on a single canvas, plus one call for the gauntlets. It replaced the 3x4 twelve-frame sheet,
which never produced convertible pixel art — see `docs/guides/art/CHARACTER_DESIGN_GUIDE.md`.

    from cut_walk_row import cut_walk, cut_gauntlet_column
    cut_walk(render, frames_dir, "front", pitch=10.25)
    cut_walk(render, frames_dir, "side",  pitch=9.70, mirror=True)   # side is generated facing left
    cut_gauntlet_column(render, hands_dir, pitch=18.50)

THE ONE RULE: SNAP THE WHOLE CANVAS ON ONE GRID, THEN SPLIT
-----------------------------------------------------------
Never detect a pitch per frame. Every frame in a render was drawn at one scale, so there is one true
grid. Detecting per frame gives four slightly different answers, the feet land a sub-pixel apart, and
the character shimmers as it walks. Snap once, split after.

PITCH IS PASSED IN, NOT DETECTED
--------------------------------
`pixelsnap.detect_pitch` takes the LARGEST pitch scoring within 90% of the best (older notes here said
"smallest"; the code says largest), and it is still wrong often: the gauntlet column measured 9.25 when the
truth was 18.50, a hand sheet 4.65 against a true 23.00, bronze's pick 12.8 against 13.0. `procedure.py grids`
draws a shortlist of candidates to judge by eye; pass the chosen `pitch` explicitly. `pitch=None` falls back
to the detector and will sometimes be wrong.
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "aipipe"))
import pixelsnap as PS                       # noqa: E402
import preview_explore as PE                 # noqa: E402
from scipy.ndimage import binary_dilation, label as ndlabel   # noqa: E402
from cut_outfit import defringe              # noqa: E402


def sample_masked(img, px, py, x0, y0, nx, ny):
    """Snap to a grid, taking each cell's COLOUR from the figure pixels only.

    `pixelsnap.sample` medians all four channels together. A cell straddling the silhouette then gets
    a middling alpha AND a background-coloured RGB median, which is where the semi-transparent magenta
    fringe around the first fire-ant frames came from. Here alpha decides the cell (median over the
    whole cell, then hard 0/255 — a sprite pixel is on or off) and the colour is the median of
    whatever figure pixels are in it, so an edge cell takes the character's colour, not the key's.
    """
    H, W = img.shape[:2]
    out = np.zeros((ny, nx, 4), np.uint8)
    for gy in range(ny):
        cy = y0 + (gy + 0.5) * py
        ylo = max(0, int(round(cy - 0.25 * py)))
        yhi = min(H, max(ylo + 1, int(round(cy + 0.25 * py))))
        for gx in range(nx):
            cx = x0 + (gx + 0.5) * px
            xlo = max(0, int(round(cx - 0.25 * px)))
            xhi = min(W, max(xlo + 1, int(round(cx + 0.25 * px))))
            win = img[ylo:yhi, xlo:xhi].reshape(-1, 4)
            if not win.size or np.median(win[:, 3]) < 128:
                continue                                   # background cell: leave it clear
            ink = win[win[:, 3] >= 128]
            out[gy, gx, :3] = np.round(np.median((ink if ink.size else win)[:, :3], axis=0))
            out[gy, gx, 3] = 255
    return out


def _runs(mask, axis, gap=1):
    """Index ranges of the occupied bands along one axis, split at empty gaps."""
    occ = mask.any(axis=axis)
    out, start = [], None
    for i, v in enumerate(occ):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start > gap:
                out.append((start, i))
            start = None
    if start is not None:
        out.append((start, len(occ)))
    return out


def split_n(mask, n):
    """Column ranges for exactly `n` evenly-spaced figures, cutting at the THINNEST column near each
    expected boundary.

    Not at empty gaps. A long stride puts the leading foot of one frame right up against the next —
    on one black-ant side render frames 3 and 4 touched with no clear column at all, and both a
    minimum-gap rule and a widest-gap rule reported "3 frames" on a render that plainly had four.
    The frames are evenly spaced by construction, so look near where each boundary must be and cut
    where the least ink crosses.
    """
    ink = mask.sum(axis=0)
    xs = np.where(ink > 0)[0]
    lo, hi = xs.min(), xs.max() + 1
    step = (hi - lo) / n
    cuts = []
    for k in range(1, n):
        centre = lo + step * k
        half = max(2, int(step * 0.22))
        a, b = int(centre - half), int(centre + half) + 1
        a, b = max(lo + 1, a), min(hi - 1, b)
        cuts.append(a + int(np.argmin(ink[a:b])))
    e = [lo] + sorted(cuts) + [hi]
    out = []
    for i in range(n):
        a, b = e[i], e[i + 1]
        col = np.where(ink[a:b] > 0)[0]          # tighten to this frame's own ink
        if not len(col):
            return []
        out.append((a + col.min(), a + col.max() + 1))
    return out


def snap_whole(src, pitch=None):
    """The whole render, keyed and snapped on ONE grid. Returns (pitch, snapped RGBA)."""
    rgb = np.asarray(Image.open(src).convert("RGB"), np.uint8)
    art = PE.key(np.asarray(Image.open(src).convert("RGB"), int))
    rgba = np.dstack([rgb, (art * 255).astype(np.uint8)]).astype(float)
    ex, ey = PS.edge_energy(rgba)
    if pitch is None:
        pitch = PS.detect_pitch([ex, ey])
    x0, y0 = PS._best_phase(ex, pitch), PS._best_phase(ey, pitch)
    H, W = rgba.shape[:2]
    snapped = sample_masked(rgba, pitch, pitch, x0, y0,
                            int((W - x0) / pitch), int((H - y0) / pitch))
    return pitch, snapped


def drop_neighbour_bits(f, reach=3):
    """Drop specks that belong to the frame NEXT DOOR.

    When two frames touch, the split runs through open space beside a figure and carries a pixel or
    two of its neighbour — a dot beside the black-ant's head that showed in every side frame.

    Keep whatever is REACHABLE from the body, not whatever is big. THE ANTENNAE ARE DRAWN AS
    DISCONNECTED PIXELS — a chain of 1-5px blobs — so a size filter deletes the antenna outright
    (figure height dropped 75 -> 70 the first time), and an x-range filter misses the speck whenever
    a contact pose spans the full frame width. Dilating by `reach` links each antenna dot to the next
    and to the head, while a stray from the next frame stays its own island.
    """
    m = f[..., 3] > 0
    if not m.any():
        return f
    lab, n = ndlabel(m)
    if n <= 1:
        return f
    grown, _ = ndlabel(binary_dilation(m, np.ones((2 * reach + 1, 2 * reach + 1), bool)))
    areas = np.bincount(lab.ravel())
    areas[0] = 0
    body = grown[lab == int(areas.argmax())][0]      # the group the biggest blob belongs to
    out = f.copy()
    out[m & (grown != body)] = 0
    return out


def _torso_centre(f, lo=0.36, hi=0.48):
    """Centre of the ink across the CHEST band, as a fraction of the figure's own height.

    Three alignments were tried and only this one is right:

    * by BOUNDING BOX — the box tracks the legs, so the torso slides sideways as the character steps.
    * by HEAD — looks fine until the headgear overhangs. In a side view the ant hood juts forward, so
      head-aligning pushed the black-ant torso 6px off from where `gait.anchor` measured it, and the
      far fist — which the compositor hangs off the TORSO centre — floated clear of the body.
    * by TORSO, here. `gait.anchor` takes the hand anchor from the chest row of the neutral frame, so
      aligning the frames on the same thing is what makes the fists land on the body in every frame.
    """
    m = f[..., 3] > 0
    ys = np.where(m.any(axis=1))[0]
    y0, y1 = ys.min(), ys.max()
    band = m[y0 + int((y1 - y0) * lo): y0 + int((y1 - y0) * hi) + 1]
    xs = np.where(band.any(axis=0))[0]
    if not len(xs):
        xs = np.where(m.any(axis=0))[0]
    return (xs.min() + xs.max()) / 2.0


def to_common_canvas(frames):
    """Pad every frame onto one canvas, aligned on the torso so the fists land on the body."""
    cs = [_torso_centre(f) for f in frames]
    left = max(cs)
    right = max(f.shape[1] - 1 - c for f, c in zip(frames, cs))
    W, H = int(np.ceil(left + right)) + 1, frames[0].shape[0]
    out = []
    for f, c in zip(frames, cs):
        can = np.zeros((H, W, 4), np.uint8)
        x = int(round(left - c))
        can[:, x:x + f.shape[1]] = f
        out.append(can)
    return out


def cut_walk(src, frames_dir, bank, pitch=None, mirror=False):
    """Four walk frames in a row -> `<bank>_1..4.png` on one shared canvas and one baseline.

    `mirror` flips the frames before writing. The side view is generated facing LEFT but `gait`'s
    wrist-lean maths assumes the character faces +x, so the mirror must happen HERE, on the body
    frames — mirroring the finished animation instead puts the wrists on backwards.
    """
    pitch, snapped = snap_whole(src, pitch)
    m = snapped[..., 3] > 0
    cols = split_n(m, 4)
    if len(cols) != 4:
        raise SystemExit(f"{src}: expected 4 frames in a row, found {len(cols)} — look at the render")
    rows = np.where(m.any(axis=1))[0]
    top, bot = rows.min(), rows.max()          # ONE ground line for all four
    cut = []
    for c0, c1 in cols:
        g = drop_neighbour_bits(snapped[top:bot + 1, c0:c1])
        xs = np.where((g[..., 3] > 0).any(axis=0))[0]
        cut.append(g[:, xs.min():xs.max() + 1])
    frames = to_common_canvas(cut)

    os.makedirs(frames_dir, exist_ok=True)
    for i, f in enumerate(frames, 1):
        im = Image.fromarray(f, "RGBA")
        if mirror:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        im.save(os.path.join(frames_dir, f"{bank}_{i}.png"))
    return pitch, frames[0].shape[1], frames[0].shape[0]


def check_alternation(frames_dir, bank):
    """FRONT/BACK only: frames 1 and 3 must lift OPPOSITE feet. Returns a list of problems.

    ALWAYS RUN THIS on the camera-facing banks. The model happily returns a cycle where both stepping
    frames lift the SAME leg, and it does not look wrong in a still — only once it loops, as one foot
    tapping twice instead of a walk. It shipped before anyone spotted it (owner: "it is not correct in
    how it loops"), and it was caught by measuring, not by looking.

    The SIDE bank cannot be checked this way and returns nothing. In profile both feet are planted in
    a contact frame, so foot HEIGHT says nothing; which leg leads is carried by shading (near leg vs
    far leg), not by the silhouette. Check the side by eye.
    """
    if bank == "side":
        return []
    lifted = []
    for i in (1, 2, 3, 4):
        a = np.asarray(Image.open(os.path.join(frames_dir, f"{bank}_{i}.png")).convert("RGBA"))
        m = a[..., 3] > 0
        # Split at the TORSO, not at the canvas midline. `to_common_canvas` aligns the frames on the
        # torso centre, which is not the middle of the canvas — measuring either side of W//2 put a
        # planted leg on the "raised" side and reported a perfectly good cycle as broken. That cost
        # two correction calls on art that was already right.
        mid = int(round(_torso_centre(a)))
        low = []
        for sl in (slice(0, mid), slice(mid, m.shape[1])):
            ys = np.where(m[:, sl].any(axis=1))[0]
            low.append(ys.max() if len(ys) else -1)
        lifted.append("L" if low[0] < low[1] - 1 else ("R" if low[1] < low[0] - 1 else "-"))
    bad = []
    if lifted[0] == "-" or lifted[2] == "-":
        bad.append(f"{bank}: frames 1 and 3 should each lift a foot, got {lifted}")
    elif lifted[0] == lifted[2]:
        bad.append(f"{bank}: frames 1 and 3 lift the SAME foot ({lifted}) — not a walk, reroll")
    if lifted[1] != "-" or lifted[3] != "-":
        bad.append(f"{bank}: frames 2 and 4 should be feet-together, got {lifted}")
    bad += check_lift(frames_dir, bank)
    return bad


# How far the raised foot should clear the planted one, as a fraction of the figure's height.
#
# Leg HEIGHT was the one thing in this pipeline with no gate on it. `check_alternation` asks only WHICH
# foot is up, on a 1px threshold, so a 2px shuffle and a 14px stride passed identically. Measured on the
# three outfits built under the old "Lift the knee HIGH" wording: bronze 19.1% front / 16.2% back,
# fire-ant 18.2 / 15.4, black-ant 13.8 / 19.8 — a 6-point spread across the set and 3-6 points between
# front and back of the SAME outfit. Owner: *"its lifting the knees really high which is ok for running
# but not walking"*, and the prompt now asks for MEDIUM-HIGH (`outfits.WALK_KNEE`).
#
# ⚠ The band is provisional — derived from that instruction, not from a picked number. It is a WARNING,
# not a hard fail: it is a taste range, and the rule is to look at the render, not to trust a threshold.
LIFT_BAND = (0.07, 0.15)


def check_lift(frames_dir, bank):
    """FRONT/BACK only: how high the raised foot clears the planted one, against `LIFT_BAND`.

    The SIDE bank is excluded for the same reason as alternation — in profile both feet are planted in
    a contact frame, so foot height carries no information there.
    """
    if bank == "side":
        return []
    heights = []
    for i in (1, 3):
        a = np.asarray(Image.open(os.path.join(frames_dir, f"{bank}_{i}.png")).convert("RGBA"))
        m = a[..., 3] > 0
        mid = int(round(_torso_centre(a)))
        low = []
        for sl in (slice(0, mid), slice(mid, m.shape[1])):
            ys = np.where(m[:, sl].any(axis=1))[0]
            low.append(ys.max() if len(ys) else -1)
        heights.append(abs(low[0] - low[1]))
    ys = np.where((np.asarray(Image.open(
        os.path.join(frames_dir, f"{bank}_2.png")).convert("RGBA"))[..., 3] > 0).any(axis=1))[0]
    body = max(1, ys.max() - ys.min() + 1)
    frac = max(heights) / body
    lo, hi = LIFT_BAND
    if not lo <= frac <= hi:
        how = "HIGHER than" if frac > hi else "LOWER than"
        return [f"{bank}: foot lift {max(heights)}px on a {body}px body = {frac:.1%}, {how} the "
                f"{lo:.0%}-{hi:.0%} band — look at it before accepting"]
    return []


def cut_gauntlet_column(src, hands_dir, pitch=None, target_h=13, roles=None):
    """The character-plus-hand-column render -> one PNG per hand role.

    The render puts the character on the left and the five hands stacked on the right, on ONE canvas,
    so the hands are drawn at the character's own pixel density rather than a density of their own.
    Only the hands are cut out; the character is there to set the grid.

    Heights come back within a pixel of `target_h` rather than exactly on it, so each hand is padded
    or trimmed AT THE WRIST to match. That costs at most one row of cuff and leaves every other pixel
    untouched — rescaling to fit would touch all of them, and rescaling player art is banned.
    """
    import official as O
    roles = roles or O.HAND_ROLES
    pitch, snapped = snap_whole(src, pitch)
    m = snapped[..., 3] > 0
    cols = _runs(m, 0, gap=1)
    if len(cols) < 2:
        raise SystemExit(f"{src}: expected a character and a hand column, found {len(cols)} groups")
    c0, c1 = cols[-1]                                   # rightmost group = the hands
    col = snapped[:, c0:c1]
    bands = _runs(col[..., 3] > 0, 1, gap=1)
    if len(bands) != len(roles):
        raise SystemExit(f"{src}: expected {len(roles)} hands in the column, found {len(bands)}")

    os.makedirs(hands_dir, exist_ok=True)
    out = []
    for role, (r0, r1) in zip(roles, bands):
        p = col[r0:r1]
        ys, xs = np.where(p[..., 3] > 0)
        p = p[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        raw = p.shape[0]
        if raw > target_h:
            p = p[:target_h]                                                    # trim the cuff
        elif raw < target_h:
            p = np.concatenate([p, np.zeros((target_h - raw, p.shape[1], 4), np.uint8)])
        img = defringe(p)
        Image.fromarray(img, "RGBA").save(os.path.join(hands_dir, f"{role}.png"))
        out.append((role, raw, img.shape[1], img.shape[0]))
    return pitch, out
