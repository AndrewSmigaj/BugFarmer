"""gait.py — THE approved walk and run hand motion. Committed so it cannot be lost again.

    from gait import walk_frame, run_frame

WHY THIS FILE EXISTS, and it is not a nice reason.

The walk and run hand motion was designed and approved on 2026-07-28 over many iterations — the owner
picked `walk_b`/`walk_ref` for walking and `r75` for running. The script that produced them was written
into a session scratch directory, run, and **never committed**. Only its output gifs survived, in the
gitignored art folder. When the motion was needed again it got re-derived by eye from those gifs, badly,
and shipped in a showcase — fists at the wrong height, three times the travel, the wrong hand sprite, and
a 55 degree roll that never existed. Owner: "those look insane like flapping weird shit ... we completely
agreed on that hand pattern and now you just went and threw it away?"

He had also said, the day before, that he was nervous decisions were not being written down. He was right.

The constants below are **recovered verbatim** from that session's transcript, not re-derived:

    render(name, note, amp, ay, base_rot, tilt, ratio, waist, ms)
    r75      0.58, 0.032, 75, 14, 0.19, 0.46,  90   <- APPROVED RUN
    walk_ref 0.52, 0.013,  0, 22, 0.17, 0.60, 150   <- APPROVED WALK ("accepted")

⚠ DO NOT re-tune these by eye. If they need to change, change them here, deliberately, and say so.
"""
import math
import os

import numpy as np
from PIL import Image

# --- the approved parameters. Recovered, not invented. ---------------------------------------------
WALK = dict(amp=0.52,      # fore/aft travel, as a fraction of TORSO WIDTH at chest height
            ay=0.013,      # how much the fist rises at the extremes, as a fraction of body height
            rot=0.0,       # base rotation: a walking fist hangs, it does not point
            tilt=22.0,     # extra rotation swung through, times sin(phase)
            ratio=0.17,    # fist height as a fraction of body height
            waist=0.60,    # how far DOWN the body the fists ride — a walk is at the waist
            ms=150)
RUN = dict(amp=0.58, ay=0.032, rot=75.0, tilt=14.0, ratio=0.19,
           waist=0.46,     # a run carries them higher, at the chest
           ms=90)

# Beat phases. NOT [0, 0.5, 1.0, 1.5] — that inversion put the hands at full reach on the PASSING frames
# instead of the strides, and was one of the four walk failures before this was settled.
PHASE = [0.5, 0.0, 1.5, 1.0]
CYCLE = [1, 2, 3, 2]        # frame 4 came back a second stride, so it is dropped
CHEST_ROW = 0.42            # where the torso centre and width are measured, ONCE, from the neutral frame
DIM = 0.62                  # the far fist is darkened, not just drawn behind


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
    """Cuff up, hand hanging. The generated gauntlet sprites are drawn the other way up."""
    return a[::-1, ::-1]


def anchor(neutral):
    """Torso centre and width, measured ONCE from the neutral frame.

    Measuring per frame makes the fists jitter, because the legs change the silhouette underneath and the
    anchor starts following the legs instead of the chest.
    """
    y0, y1, _, _ = _bbox(neutral)
    row = y0 + int((y1 - y0) * CHEST_ROW)
    xs = np.where(neutral[..., 3][row] > 0)[0]
    if not len(xs):
        _, _, x0, x1 = _bbox(neutral)
        return y0, y1, (x0 + x1) / 2.0, x1 - x0
    return y0, y1, (xs.min() + xs.max()) / 2.0, xs.max() - xs.min()


def pose(body, neutral, back_hand, palm_hand, beat, p):
    """One posed frame: body plus its two fists, swinging THROUGH the body around the torso centre.

    The far fist is drawn first and dimmed, the body over it, the near fist last — so the arms read as
    passing behind and in front rather than both floating on top.
    """
    ny0, ny1, cx, tw = anchor(neutral)
    bh = ny1 - ny0 + 1
    wy = ny0 + int((ny1 - ny0) * p["waist"])
    s = math.sin(PHASE[beat % len(PHASE)] * math.pi)
    dx = p["amp"] * tw * s
    dy = -p["ay"] * bh * abs(s)
    ang = p["rot"] + p["tilt"] * s

    out = np.zeros_like(body)
    _paste(out, _sz(_rot(_dim(palm_hand), ang), bh, p["ratio"]), cx - dx, wy + dy)
    m = body[..., 3] > 0
    out[m] = body[m]
    _paste(out, _sz(_rot(back_hand, ang), bh, p["ratio"]), cx + dx, wy + dy)
    return out


def walk_frame(body, neutral, back_hand, palm_hand, beat):
    return pose(body, neutral, back_hand, palm_hand, beat, WALK)


def run_frame(body, neutral, back_hand, palm_hand, beat):
    return pose(body, neutral, back_hand, palm_hand, beat, RUN)


def hands_for(outfit_dir):
    """(back-of-hand, palm) for an outfit, flipped cuff-up.

    The gauntlet sheet is prompted as four views in order: back of hand, palm, profile, three-quarter —
    cut to front/back/side/grip. So `front` is the BACK of the hand and `back` is the palm, which reads
    backwards and has caused mistakes; hence this function rather than inline indexing.
    """
    def rgba(p):
        return np.asarray(Image.open(p).convert("RGBA"), np.uint8)
    g = os.path.join(outfit_dir, "gauntlet")
    return flip(rgba(os.path.join(g, "front.png"))), flip(rgba(os.path.join(g, "back.png")))
