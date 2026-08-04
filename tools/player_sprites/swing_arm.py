"""swing_arm.py — swings where THE HAND TRAVELS and the blade pivots at the wrist. FREE, no API.

  python3 tools/player_sprites/swing_arm.py

Writes the options into `tools/_generated/player/reviews/<date>-swing-arm/`.

WHAT WAS WRONG WITH EVERY PREVIOUS SWING
----------------------------------------
`swing_frames` computes one angle, places the TOOL at a fixed small radius from the body centre, then
sticks the hand onto the tool's grip point. So the tool leads and the hand is downstream of it — the fist
stays parked next to the shoulder and *rotates in place* while the blade sweeps round it like a clock
hand bolted to his chest.

Owner, 2026-08-04: *"do people take a sword in their fist, hold their fist up to their shoulder and rotate
their fist to swing it? ever?"* No. Nobody does.

A real swing is the other way round. **The hand travels** — shoulder and elbow drive it out through an arc
away from the body — and the blade pivots about the **wrist**. The blade's rotation is mostly a consequence
of the arm's direction changing, not a rotation applied at the shoulder.

`DESIGN.md` already said this ("Drive the HAND, then hang the tool off it") and the renderer did the
opposite for weeks.

WHY IT WAS BUILT WRONG
----------------------
The same doc says: "The armless design caps how far the hand may travel... Keep the hand within roughly a
third of a cell of the shoulder", because a fist out at arm's length was thought to look detached with no
arm drawn. That constraint is what pinned the hand at the shoulder, and it is incompatible with a swing
that reads as a swing. Owner overturned it: *"dont care about the arm missing, though it doesnt have to be
realistic just out some"*.

HOW THIS ONE WORKS
------------------
  shoulder    fixed point, from `FACINGS` (side view: 0.06 forward, 0.40 up, in cell units)
  hand        shoulder + reach(t) * (cos theta(t), sin theta(t))   <- THE HAND TRAVELS
  blade       points along the arm, plus a wrist offset            <- pivots at the WRIST
  tool sprite positioned so its measured GRIP lands on the hand    <- tool FOLLOWS the hand

Reach is in CELL units (a cell is half the body height), so it scales with the character.
"""
import datetime
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gait                                              # noqa: E402
import render_animations as R                            # noqa: E402
import swing_lab as S                                    # noqa: E402
from compare_hands import rgba                           # noqa: E402

OUTFIT, TOOL = "bronze", "sword"
BG = (150, 160, 150)
PAD = 200
FPS = 30

SHOULDER = (0.06, 0.40)      # cell units, +x forward / +y up — from swing_lab.FACINGS "side"


def ease_out(u):
    return 1 - (1 - u) ** 3


def ease_in(u):
    return u * u * u


def ease_in_out(u):
    return 3 * u * u - 2 * u * u * u


# Each variant returns (theta_deg, reach_cells, wrist_deg) for t in 0..1.
# theta: the ARM's direction from the shoulder. 90 = straight up, 0 = forward, -90 = straight down.
# reach: how far the hand is from the shoulder, in cells.
# wrist: the blade's angle relative to the arm direction — 0 means the blade continues the arm.

# REACH IS IN CELLS, AND A CELL IS HALF THE BODY HEIGHT — so 1.0 is enormous, about a whole torso away.
# The character's half-width is only ~0.28 cell. Anything past ~0.7 stops reading as attached to him and
# becomes a sword floating in space next to a man, which is the first thing this file got wrong.
def v_short(t):
    """A — the hand travels, but stays close. The conservative reading of "just out some"."""
    th = 105 + (-70 - 105) * ease_in_out(t)
    return th, 0.34, -18


def v_far(t):
    """B — the same path, hand well clear of the body. About as far as it can go and still read."""
    th = 105 + (-70 - 105) * ease_in_out(t)
    return th, 0.60, -18


def v_elbow(t):
    """C — the elbow: tucked on the wind-up, extends THROUGH contact, folds back on recovery.

    What an arm actually does, and the only variant where the reach itself carries the impact.
    """
    th = 110 + (-72 - 110) * ease_in_out(t)
    if t < 0.30:
        reach = 0.26 + (0.32 - 0.26) * ease_out(t / 0.30)
    elif t < 0.68:
        reach = 0.32 + (0.66 - 0.32) * ease_in((t - 0.30) / 0.38)
    else:
        reach = 0.66 + (0.38 - 0.66) * ease_out((t - 0.68) / 0.32)
    return th, reach, -14


def v_overhead(t):
    """D — over the top: up and behind first, then all the way down in front."""
    th = 145 + (-80 - 145) * ease_in_out(t)
    reach = 0.34 + 0.22 * math.sin(math.pi * min(1.0, max(0.0, t)))
    return th, reach, -10


def v_wrist(t):
    """E — moderate travel, with the wrist snapping the blade through contact.

    The blade lags the arm on the way down and whips past it at the bottom.
    """
    th = 100 + (-64 - 100) * ease_in_out(t)
    reach = 0.32 + 0.26 * ease_in(t)
    wrist = 30 - 95 * ease_in(t)
    return th, reach, wrist


# ---------------------------------------------------------------------------------------------------
# 2026-08-04, second pass. Owner: "you dont need to have the wrist angle with respect to the pommel of
# the sword, its awkward, it should start a little behind the head and swing down, but the sword can be
# angled back more, similar to far but the sword is angle back more so that the hand is perpendicular
# with the pommel".
#
# So: NO per-frame wrist articulation. The blade sits at a FIXED angle behind the arm for the whole
# swing, and the fist grips ACROSS the handle — perpendicular to the blade — instead of being rotated
# to some offset of its own. The only thing that varies between these is how far back the blade is set.
#
# `HAND_PERP` replaces `HAND_ROT` (225), which was tuned for the old shoulder-pivot swing and has no
# meaning once the hand travels.
# OWNER'S PICK, 2026-08-04: "hand perp 180". Chosen off `HAND_ROTATION_which_way.png` in the review
# folder, which renders 0 / 90 / 180 / 270 side by side at the same frame.
# 90 was wrong — "dude you turned the hand the wrong way" — and 270 was my guess at the opposite, also
# not it. Do not re-derive this from reasoning about wrists; it was picked by eye against the render.
HAND_PERP = 180.0
START_TH, END_TH = 128.0, -74.0     # a little behind the head, swinging down
BACK_REACH = 0.60                   # B_far's reach — the one he pointed at


def _back(deg):
    """Blade held `deg` behind the arm direction for the whole swing. No wrist articulation."""
    def f(t):
        th = START_TH + (END_TH - START_TH) * ease_in_out(t)
        return th, BACK_REACH, deg
    return f


VARIANTS = [("F1_back25", _back(25)), ("F2_back45", _back(45)),
            ("F3_back65", _back(65)), ("F4_back85", _back(85))]

PREV_VARIANTS = [("A_short", v_short), ("B_far", v_far), ("C_elbow", v_elbow),
                 ("D_overhead", v_overhead), ("E_wrist_snap", v_wrist)]

DUR = 0.30


def build(name, fn, two_handed):
    hands, prov = R.load_hands(OUTFIT)
    body = R.load_bank(OUTFIT, "side", 1)[1]
    ny0, ny1, cx, _ = gait.anchor(body)
    bh = ny1 - ny0 + 1
    cell = bh / 2.0

    art0 = S.scale_h(rgba(os.path.join(R.RES, "Items", S.TOOLS[TOOL]["icon"])), cell)
    grip = (S.grip_of(art0) + S.DIAG * S.GRIP_EXTRA) * art0.shape[0]

    W, H = body.shape[1] + 2 * PAD, body.shape[0] + 2 * PAD
    n = max(14, int(DUR * FPS * 3))
    out, ms = [], []
    for i in range(n):
        t = i / (n - 1)
        th, reach, wrist = fn(t)
        sc = np.zeros((H, W, 4), np.uint8)
        bx, by = W / 2, H / 2
        ox, oy = bx - body.shape[1] / 2, by - body.shape[0] / 2

        # Shoulder, in image coords. FACINGS gives it in CELL UNITS OFFSET FROM BODY CENTRE
        # (+x forward, +y up) — NOT as a fraction of body height. Reading it as a fraction put the
        # shoulder in the wrong place and the whole arm with it.
        bcy = oy + ny0 + (ny1 - ny0) / 2.0
        sx = ox + cx + SHOULDER[0] * cell
        sy = bcy - SHOULDER[1] * cell

        # THE HAND TRAVELS
        r = math.radians(th)
        hx = sx + math.cos(r) * reach * cell
        hy = sy - math.sin(r) * reach * cell

        blade = th + wrist                       # blade continues the arm, plus wrist
        art = S.rot(art0, blade - S.ART_ANGLE)

        # place the TOOL so its measured grip lands ON the hand — the tool follows, it does not lead
        rr = math.radians(-(blade - S.ART_ANGLE))
        gx = grip[0] * math.cos(rr) - grip[1] * math.sin(rr)
        gy = grip[0] * math.sin(rr) + grip[1] * math.cos(rr)

        gait._paste(sc, body, bx, by)
        gait._paste(sc, art, hx - gx, hy - gy)

        fists = [(hands["grip_back"], 0.0)]
        if two_handed:
            fists.append((hands["grip_palm"], 0.17))
        for fist, up in fists:
            fx = hx + math.cos(math.radians(blade)) * up * art0.shape[0]
            fy = hy - math.sin(math.radians(blade)) * up * art0.shape[0]
            # The fist grips ACROSS the handle — perpendicular to the blade. Not S.HAND_ROT (225),
            # which was tuned for the old shoulder-pivot swing and is meaningless once the hand travels.
            gait._paste(sc, gait._sz(S.rot(fist, blade + HAND_PERP), bh, gait.RUN["ratio"]), fx, fy)

        im = Image.new("RGBA", (W, H), BG + (255,))
        im.alpha_composite(Image.fromarray(sc, "RGBA"))
        out.append(im.convert("RGB"))
        ms.append(int(DUR * 1000 / n))
    return out, ms, prov


def crop_union(frames, margin=14):
    bg = np.array(BG, np.int16)
    x0 = y0 = 10 ** 9
    x1 = y1 = -1
    for f in frames:
        d = np.abs(np.asarray(f, np.int16) - bg).sum(2) > 24
        if not d.any():
            continue
        ys, xs = np.where(d)
        x0, x1 = min(x0, xs.min()), max(x1, xs.max())
        y0, y1 = min(y0, ys.min()), max(y1, ys.max())
    if x1 < 0:
        return frames
    W, H = frames[0].size
    box = (max(0, x0 - margin), max(0, y0 - margin),
           min(W, x1 + 1 + margin), min(H, y1 + 1 + margin))
    return [f.crop(box) for f in frames]


def main():
    d = os.path.join(R.PLAYER, "reviews", f"{datetime.date.today().isoformat()}-swing-arm2")
    os.makedirs(d, exist_ok=True)
    made = []
    for name, fn in VARIANTS:
        for two in (False, True):
            frames, ms, prov = build(name, fn, two)
            frames = crop_union(frames)
            lbl = "2h" if two else "1h"
            p = os.path.join(d, f"sword_{lbl}_{name}.gif")
            frames[0].save(p, save_all=True, append_images=frames[1:], duration=ms, loop=0)
            made.append((f"{lbl}  {name}", frames))
            print(f"  {os.path.basename(p):34} {len(frames)} frames   hands = {prov}")

    cols = len(VARIANTS)
    W = max(f[0].size[0] for _, f in made)
    H = max(f[0].size[1] for _, f in made)
    rows = (len(made) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * W, rows * (H + 22)), (28, 28, 34))
    dr = ImageDraw.Draw(sheet)
    order = [m for m in made if m[0].startswith("1h")] + [m for m in made if m[0].startswith("2h")]
    for k, (lbl, frames) in enumerate(order):
        im = frames[int(len(frames) * 0.66)]
        x, y = (k % cols) * W, (k // cols) * (H + 22)
        bg = Image.new("RGB", (W, H), BG)
        bg.paste(im, ((W - im.size[0]) // 2, (H - im.size[1]) // 2))
        sheet.paste(bg, (x, y + 22))
        dr.text((x + 6, y + 6), lbl, fill=(255, 220, 140))
    sheet.save(os.path.join(d, "ALL_TEN.png"))
    print(f"\n  {d.replace('/mnt/c/', 'C:/')}")
    return d


if __name__ == "__main__":
    main()
