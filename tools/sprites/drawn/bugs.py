"""Bugs drawn in code, top-down, with procedural walk cycles.

The body is drawn once; the legs are a rig animated per frame (insects walk in a TRIPOD gait: front-left,
middle-right and back-left step together, then the other three), so every frame is consistent by
construction and a new species reuses the rig.

Species here: the burying beetle (Nicrophorus) — the game's `beetle_carrion`: glossy black, two jagged
orange bands across the wing cases, orange-tipped clubbed antennae.
"""
import math

import numpy as np

from . import canvas as K
from . import palette as P

S = 32   # frame size (one grid cell)


def _elytron(W, H, cx, cy, rx, ry):
    return K.dome(W, H, cx, cy, rx, ry, power=0.8)


def _body(c):
    """The beetle's body (head, pronotum, wing cases) facing north, centred in a 32x32 frame."""
    W = H = S
    xs, ys = K.grid(W, H)
    ch, org = P.ramp("chitin"), P.ramp("orange")

    # abdomen tip peeking out below the wing cases (short elytra, like the real beetle)
    tip = K.ellipse(W, H, 16, 28.0, 3.6, 2.8)
    c.shade(tip, K.lambert(K.dome(W, H, 16, 28.0, 3.6, 2.8), 4.0), "chitin", cuts=[0.4, 0.6, 0.8], hi=2)
    for yy in (27, 29):                                             # segment lines
        c.fill(K.rect(W, H, 13, yy, 18, yy) & tip, ch[0])

    # wing cases: two domes side by side with a dark seam, glossy
    def squarish(cx, cy, rx, ry):              # squarer than an ellipse: the wing cases are boxy
        return np.abs((xs - cx) / rx) ** 3.2 + np.abs((ys - cy) / ry) ** 2.4 <= 1.0
    left = squarish(12.8, 20.0, 4.5, 7.2) & (xs < 16)
    right = squarish(19.2, 20.0, 4.5, 7.2) & (xs >= 16)
    hl = _elytron(W, H, 12.6, 20.0, 4.6, 7.4)
    hr = _elytron(W, H, 19.4, 20.0, 4.6, 7.4)
    val = np.where(xs < 16, K.lambert(hl, 5.0), K.lambert(hr, 5.0))
    wings = left | right
    c.shade(wings, val, "chitin", cuts=[0.42, 0.62, 0.80, 0.93])
    # the two jagged orange bands (sampled against the same lighting, so they are glossy too)
    band1 = wings & (ys > 15.6) & (ys < 17.8 + 0.7 * np.sin(xs * 1.7))
    band2 = wings & (ys > 21.2 + 0.7 * np.sin(xs * 1.3 + 1.0)) & (ys < 23.6)
    for b in (band1, band2):
        c.shade(b, val, "orange", cuts=[0.40, 0.60, 0.80, 0.94])
    c.fill(K.rect(W, H, 15, 13, 16, 27) & wings, ch[0])            # the seam between the wing cases
    # specular streaks on each wing case (top-left of each dome)
    for (x, y) in ((11, 15), (11, 16), (12, 15), (18, 15), (18, 16)):
        c.put(x, y, ch[4])

    # pronotum (the shield behind the head)
    pro = K.ellipse(W, H, 16, 12.2, 5.6, 3.4)
    c.shade(pro, K.lambert(K.dome(W, H, 16, 12.2, 5.6, 3.4), 5.0), "chitin", cuts=[0.42, 0.62, 0.8, 0.93])
    c.put(13, 10, ch[4]); c.put(14, 10, ch[3])
    # head
    head = K.ellipse(W, H, 16, 7.6, 3.4, 2.6)
    c.shade(head, K.lambert(K.dome(W, H, 16, 7.6, 3.4, 2.6), 4.0), "chitin", cuts=[0.42, 0.62, 0.8], hi=3)
    c.put(13, 7, ch[3]); c.put(19, 7, ch[2])                        # eyes catch light
    # mandibles
    c.put(14, 5, ch[1]); c.put(15, 4, ch[1]); c.put(18, 5, ch[1]); c.put(17, 4, ch[1])


LEGS = [  # (side, attach x, attach y, knee dx, knee dy, foot dx, foot dy, group)
    ("L", 11.0, 12.0, -3.0, -1.5, -5.5, -4.0, 0),   # front-left
    ("R", 21.0, 12.0, 3.0, -1.5, 5.5, -4.0, 1),     # front-right
    ("L", 10.0, 17.0, -4.0, 0.0, -7.0, 1.0, 1),     # middle-left
    ("R", 22.0, 17.0, 4.0, 0.0, 7.0, 1.0, 0),       # middle-right
    ("L", 10.5, 22.0, -3.5, 2.0, -6.0, 6.5, 0),     # hind-left
    ("R", 21.5, 22.0, 3.5, 2.0, 6.0, 6.5, 1),       # hind-right
]


def _legs(c, frame, nframes):
    """Tripod gait: group 0 and group 1 alternate. A planted foot slides back; a lifted foot swings forward."""
    ch = P.ramp("chitin")
    for (side, ax, ay, kdx, kdy, fdx, fdy, g) in LEGS:
        ph = 2 * math.pi * (frame / nframes) + (math.pi if g else 0)
        swing = math.sin(ph)                 # +1 = foot furthest forward
        lifted = math.cos(ph) > 0.2          # the swing phase: foot off the ground, pulled in slightly
        fx = ax + fdx * (0.85 if lifted else 1.0)
        fy = ay + fdy - 2.2 * swing
        kx = ax + kdx
        ky = ay + kdy - 1.1 * swing
        c.line(round(ax), round(ay), round(kx), round(ky), ch[1])
        c.line(round(kx), round(ky), round(fx), round(fy), ch[0] if not lifted else ch[1])
        c.put(round(kx), round(ky), ch[3])   # the knee catches the light


def beetle_frames(nframes=6):
    frames = []
    for f in range(nframes):
        c = K.Canvas(S, S)
        _legs(c, f, nframes)
        body = K.Canvas(S, S)
        _body(body)
        body.clean_orphans(passes=1)
        body.outline(P.OUTLINE)
        c.paste(body)
        # antennae drawn last: thin, bending outward, orange clubbed tips
        o = P.ramp("orange")
        sway = 1 if f % 3 == 0 else 0
        for (x0, y0, x1, y1, tx, ty) in ((14, 5, 12, 2, 11 - sway, 1), (18, 5, 20, 2, 21 + sway, 1)):
            c.line(x0, y0, x1, y1, P.ramp("chitin")[1])
            c.put(tx, ty, o[3]); c.put(tx, ty + 1, o[2]); c.put(tx + (1 if tx > 16 else -1), ty, o[1])
        frames.append(c)
    return frames
