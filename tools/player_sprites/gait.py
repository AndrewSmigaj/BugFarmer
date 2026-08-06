"""gait.py — THE approved walk and run hand motion, verbatim. Committed so it cannot be lost again.

This is the script from 2026-07-28 that produced the gifs the owner approved — `walk_ref`/`walk_b` for
walking and `r75` for running — recovered from that session's transcript. The maths below is a
transcription, not a reimplementation.

WHY IT HAD TO BE RECOVERED: the original was written into a session scratch directory, run, and never
committed. Only its output gifs survived, and those live in a gitignored folder. When the motion was
needed again it was rebuilt BY HAND from those gifs, got the height, travel and hand sprite wrong, and
then — the worst part — the owner's tuned constants were EDITED to compensate for bugs in the
rebuild. Owner: "we spent so long perfecting this and you just go fuckoff and delete it".

⚠ THE NUMBERS IN `WALK` AND `RUN` ARE THE OWNER'S. Do not adjust them to make some other code look
right; fix that other code. If they genuinely need to change, that is a decision to raise, not a tweak.
"""
import math
import os

import numpy as np
from PIL import Image

# render(name, note, amp, ay, base_rot, tilt, ratio, waist, ms) — the two he picked, verbatim:
#   r75      0.58, 0.032, 75, 14, 0.19, 0.46,  90
#   walk_ref 0.52, 0.013,  0, 22, 0.17, 0.60, 150
WALK = dict(amp=0.52, ay=0.013, rot=0.0, tilt=22.0, ratio=0.17, waist=0.60, ms=150)
RUN = dict(amp=0.58, ay=0.032, rot=75.0, tilt=14.0, ratio=0.19, waist=0.46, ms=90)

PHASE = [0.5, 0.0, 1.5, 1.0]   # NOT [0,.5,1,1.5] — that inversion put the fists at full reach on the
                               # passing frames, one of the four walk failures before this was settled
CYCLE = [1, 2, 3, 2]           # frame 4 came back a second stride, so it is dropped
CHEST_ROW = 0.42               # torso centre and width are measured ONCE, here, on the neutral frame
DIM = 0.62                     # the far fist is darkened as well as drawn behind


def _bbox(a):
    ys, xs = np.where(a[..., 3] > 0)
    return ys.min(), ys.max(), xs.min(), xs.max()


def _paste(dst, src, cx, cy):
    h, w = src.shape[:2]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    a0, b0 = max(0, x0), max(0, y0)
    a1, b1 = min(dst.shape[1], x0 + w), min(dst.shape[0], y0 + h)
    if a1 <= a0 or b1 <= b0:
        return
    s = src[b0 - y0:b1 - y0, a0 - x0:a1 - x0]
    m = s[..., 3] > 0
    dst[b0:b1, a0:a1][m] = s[m]


def _sz(a, bh, r):
    th = max(4, round(bh * r))
    s = th / a.shape[0]
    return np.asarray(Image.fromarray(a, "RGBA").resize(
        (max(4, round(a.shape[1] * s)), th), Image.NEAREST), np.uint8)


def _rot(a, deg):
    return np.asarray(Image.fromarray(a, "RGBA").rotate(deg, resample=Image.NEAREST, expand=True), np.uint8)


def _dim(a, f=DIM):
    o = a.copy()
    m = o[..., 3] > 0
    o[..., :3][m] = (o[..., :3][m] * f).astype(np.uint8)
    return o


def flip(a):
    """`down()` in the original — cuff up, hand hanging."""
    return a[::-1, ::-1]


def anchor(neutral):
    """(top, bottom, torso centre x, torso width) measured ONCE from the neutral frame.

    Per frame it jitters, because the legs change the silhouette and the anchor follows them.
    """
    y0, y1, x0, x1 = _bbox(neutral)
    row = y0 + int((y1 - y0) * CHEST_ROW)
    xs = np.where(neutral[..., 3][row] > 0)[0]
    if not len(xs):
        return y0, y1, (x0 + x1) / 2.0, x1 - x0
    return y0, y1, (xs.min() + xs.max()) / 2.0, xs.max() - xs.min()


def pose_into(scene, bx, by, body, neutral, back_hand, palm_hand, beat, p):
    """The original `render()` inner loop, drawing into a scene instead of a body-sized canvas.

    TWO deliberate differences from the transcript, both bug fixes. THE OWNER'S NUMBERS IN `WALK` AND
    `RUN` ARE UNTOUCHED — neither of these changes a constant.

    1. It composes into a scene instead of `np.zeros_like(frame)`, which clipped the fists on outfits
       cropped tighter than bronze (ranger and hornet-stinger lost them entirely).

    2. THE TWO HANDS TILT IN OPPOSITE DIRECTIONS. The transcript gave both the same `ang`, so the hand
       swinging FORWARD and the hand swinging BACK leaned the same way — the wrists read as locked
       together rather than as an arm swing. Owner, 2026-08-03: "the rotations are wrong for the hands
       when they are swinging in the walking (the back hand for example is rotating the wrong way when
       forward)". `back_hand` sits at `+dx`, so it is the forward one when s > 0 — the hand he named.
       Each hand now tilts with ITS OWN direction of travel: forward hand `-tilt*s`, rear hand `+tilt*s`.
       `p["tilt"]` itself is unchanged.
    """
    ny0, ny1, cx, tw = anchor(neutral)
    bh = ny1 - ny0 + 1
    h, w = body.shape[:2]
    ox, oy = bx - w / 2.0, by - h / 2.0
    wy = ny0 + int((ny1 - ny0) * p["waist"])
    s = math.sin(PHASE[beat % len(PHASE)] * math.pi)
    dx = p["amp"] * tw * s
    dy = -p["ay"] * bh * abs(s)
    near_ang = p["rot"] - p["tilt"] * s      # back_hand, at +dx: forward when s > 0
    far_ang = p["rot"] + p["tilt"] * s       # palm_hand, at -dx: the opposite phase

    _paste(scene, _sz(_rot(_dim(palm_hand), far_ang), bh, p["ratio"]), ox + cx - dx, oy + wy + dy)
    _paste(scene, body, bx, by)
    _paste(scene, _sz(_rot(back_hand, near_ang), bh, p["ratio"]), ox + cx + dx, oy + wy + dy)


def walk_into(scene, bx, by, body, neutral, back_hand, palm_hand, beat):
    pose_into(scene, bx, by, body, neutral, back_hand, palm_hand, beat, WALK)


# --- the FRONT walk is a SEPARATE implementation, not the side one re-aimed ---------------------------
# `GAIT_front_D3_bigger.gif`, owner: "for walking forward gait_front_d3_bigger.gif is great".
# It shares almost nothing with the side walk and applying the side one instead was immediately obvious:
#   * a different fist — D3, not the back/palm pair
#   * hands sit OUTSIDE the body edges, they do not swing through the torso centre
#   * the edges are measured PER FRAME at 0.62 down, not once from the neutral frame
#   * one hand rises while the other drops (±0.15 of body span)
#   * phase [1, 0, -1, 0], not the side walk's [0.5, 0, 1.5, 1.0]
#   * the left hand is MIRRORED; neither is rotated or dimmed
FRONT = dict(ratio=0.17, row=0.62, gap=0.03, dx=0.06, dy=0.15, ms=150)
FRONT_PHASE = [1, 0, -1, 0]


def _edges(a, frac):
    """Row at `frac` down the figure, and the body's left/right edge ON THAT ROW. Per frame."""
    y0, y1, x0, x1 = _bbox(a)
    row = y0 + int((y1 - y0) * frac)
    xs = np.where(a[..., 3][row] > 0)[0]
    return (row, xs.min(), xs.max()) if len(xs) else (row, x0, x1)


def walk_front_into(scene, bx, by, body, neutral, hand_d3, beat):
    p = FRONT
    ny0, ny1, _, _ = _bbox(neutral)
    bh = ny1 - ny0 + 1
    h, w = body.shape[:2]
    ox, oy = bx - w / 2.0, by - h / 2.0
    hand = _sz(hand_d3, bh, p["ratio"])
    r, lx, rx = _edges(body, p["row"])
    span = rx - lx
    s = FRONT_PHASE[beat % len(FRONT_PHASE)]
    gap = max(2, int(span * p["gap"]))

    # WHICH HAND IS MIRRORED. The RIGHT one is, not the left — that turns both openings INWARD toward
    # the body. Mirroring the left instead faces both palms OUT, away from him, which is what shipped
    # until 2026-08-05: "the gauntlets for red and black ants for walk front need to be flipped
    # horizontally, the palms are facing out". It was never ant-specific; every outfit had it, bronze
    # included, and it was invisible while the gauntlets were featureless slabs with no readable palm.
    _paste(scene, body, bx, by)
    _paste(scene, hand,          ox + lx - gap - s * span * p["dx"], oy + r - s * span * p["dy"])
    _paste(scene, hand[:, ::-1], ox + rx + gap + s * span * p["dx"], oy + r + s * span * p["dy"])


def run_into(scene, bx, by, body, neutral, back_hand, palm_hand, beat):
    pose_into(scene, bx, by, body, neutral, back_hand, palm_hand, beat, RUN)


def hands_for(outfit_dir):
    """(back-of-hand, palm), flipped cuff-up.

    The original used bronze's `hand-D-pixel/h1.png` (back) and `h2.png` (palm) — the fist design that
    was being chosen at the time. Per-outfit gauntlets came later: their sheet is prompted as back of
    hand, palm, profile, three-quarter, cut to front/back/side/grip. So `front` is the BACK of the hand
    and `back` is the palm — which reads backwards, hence this function rather than inline indexing.
    """
    def rgba(p):
        return np.asarray(Image.open(p).convert("RGBA"), np.uint8)
    # ONE SOURCE FOR EVERY OUTFIT. Preferring bronze's hand-D-pixel fists where they existed made
    # bronze's hands a different SHAPE from everyone else's (aspect 0.80 vs 0.55-0.60), so across a
    # five-set reel the hands were visibly different sizes and proportions. Only bronze has those
    # fists, so the only consistent choice is each outfit's own gauntlet.
    g = os.path.join(outfit_dir, "gauntlet")
    return flip(rgba(os.path.join(g, "front.png"))), flip(rgba(os.path.join(g, "back.png")))


def front_hand_for(outfit_dir):
    """The single fist the FRONT and BACK walks use — the PROFILE view, `gauntlet/side.png`.

    NOT the back of the hand. Facing the camera you see the hand edge-on, and both hands turn INWARD
    toward the body. Owner: "walk front needs to actually have it's hands sideways (turned inward)",
    and APPROVED/DECISIONS.md lists `h3 — profile` as the front-facing walk's hand.

    `flip()` is a 180 degree rotation, so the profile ends up fingers-down pointing INWARD for the right
    hand; `walk_front_into` mirrors it for the left, which points that one inward too.
    """
    def rgba(p):
        return np.asarray(Image.open(p).convert("RGBA"), np.uint8)
    g = os.path.join(outfit_dir, "gauntlet")
    side = os.path.join(g, "side.png")
    return flip(rgba(side if os.path.exists(side) else os.path.join(g, "front.png")))
