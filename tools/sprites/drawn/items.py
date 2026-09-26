"""Item icons drawn in code (32x32).

Tools follow the DIAGONAL contract (object_pipeline.md): grip at the bottom-left, head at the top-right,
so the same sprite is both the inventory icon and the in-hand swing art.
"""
import numpy as np

from . import canvas as K
from . import palette as P

S = 32


def _v(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def axe(metal="copper"):
    """A felling axe: a wooden haft on the diagonal, a broad metal blade square to it at the top."""
    c = K.Canvas(S, S)
    xs, ys = K.grid(S, S)
    wood, m, red = P.ramp("wood"), P.ramp(metal), P.ramp("red")
    grip, top = (5.0, 27.5), (21.5, 10.5)
    d = np.array([top[0] - grip[0], top[1] - grip[1]]); d /= np.linalg.norm(d)   # along the haft
    n = np.array([-d[1], d[0]])                                                   # square to it (down-right)
    if n[0] < 0:
        n = -n

    # haft
    haft = K.capsule(S, S, grip[0], grip[1], top[0] + d[0] * 2, top[1] + d[1] * 2, 2.0)
    hv = K.lambert(K.capsule_height(S, S, grip[0], grip[1], top[0], top[1], 2.0), 3.0)
    c.shade(haft, hv, "wood", cuts=[0.35, 0.55, 0.78], hi=3)
    for t in (0.06, 0.15, 0.24):                                                 # leather grip wrap
        p = _v(grip, top, t)
        band = K.capsule(S, S, p[0] - n[0] * 2.5, p[1] - n[1] * 2.5, p[0] + n[0] * 2.5, p[1] + n[1] * 2.5, 1.0)
        c.fill(band & haft, red[1] if t != 0.15 else red[2])

    # blade: from the haft outward along n, flaring toward a curved cutting edge
    H = np.array(top) + d * -1.0
    base_a, base_b = H + d * 3.0, H - d * 3.0
    tip_a, tip_b = H + n * 10.0 + d * 6.5, H + n * 10.0 - d * 6.0
    pts = [tuple(base_a), tuple(tip_a)]
    for k in range(1, 6):                                                        # the curved edge
        t = k / 6.0
        q = tip_a + (tip_b - tip_a) * t + n * (1.8 * np.sin(np.pi * t))
        pts.append(tuple(q))
    pts += [tuple(tip_b), tuple(base_b)]
    blade = K.polygon(S, S, pts)
    poll = K.polygon(S, S, [tuple(H + d * 2.5), tuple(H - d * 2.5), tuple(H - d * 2.5 - n * 3.5),
                            tuple(H + d * 2.5 - n * 3.5)])
    head = blade | poll
    # shading: darker by the haft, brightening toward the edge, lit from the top-left
    along = ((xs - H[0]) * n[0] + (ys - H[1]) * n[1]) / 10.0
    across = ((xs - H[0]) * d[0] + (ys - H[1]) * d[1]) / 6.5
    val = 0.25 + 0.55 * np.clip(along, 0, 1) + 0.18 * across
    c.shade(head, val, metal, cuts=[0.28, 0.5, 0.72], lo=0, hi=3)
    # the ground edge: a bright 1-2 px bevel along the curve, a darker line just inside it
    edge_in = K.polygon(S, S, [tuple(tip_a - n * 2.2)] +
                        [tuple(tip_a + (tip_b - tip_a) * (k / 6.0) + n * (1.8 * np.sin(np.pi * k / 6.0) - 2.2))
                         for k in range(1, 6)] + [tuple(tip_b - n * 2.2), tuple(tip_b), tuple(tip_a)])
    ring = head & ~K.polygon(S, S, [tuple(base_a), tuple(tip_a - n * 1.2)] +
                             [tuple(tip_a + (tip_b - tip_a) * (k / 6.0) + n * (1.8 * np.sin(np.pi * k / 6.0) - 1.2))
                              for k in range(1, 6)] + [tuple(tip_b - n * 1.2), tuple(base_b)])
    c.fill(ring, m[4])
    inner = head & edge_in & ~ring
    c.fill(inner, m[3])
    # the eye of the axe where the haft passes through
    ex, ey = int(H[0]), int(H[1])
    c.put(ex, ey, wood[1]); c.put(ex + 1, ey, wood[2]); c.put(ex, ey + 1, wood[1])
    c.clean_orphans(passes=1)
    c.outline(P.OUTLINE)
    return c


def honey_jar():
    """A glass honey jar: straight glass sides full of amber honey, a cloth cover tied with string, a drip."""
    c = K.Canvas(S, S)
    xs, ys = K.grid(S, S)
    g, h, ln, red = P.ramp("glass"), P.ramp("honey"), P.ramp("linen"), P.ramp("red")
    # jar: a rounded-rectangle body, a narrower neck, a glass lip
    body = K.rect(S, S, 8, 12, 23, 28)
    for (x, y) in ((8, 12), (23, 12), (8, 28), (23, 28), (9, 28), (22, 28), (8, 27), (23, 27)):
        body[y, x] = False
    neck = K.rect(S, S, 10, 9, 21, 11)
    cyl = np.clip(1 - ((xs - 15.5) / 8.5) ** 2, 0, 1) ** 0.5            # a vertical cylinder
    lit = K.lambert(cyl, 5.0)
    honey = body & (ys > 14.5)
    c.shade(honey, lit, "honey", cuts=[0.40, 0.60, 0.80], lo=1)
    c.shade(body & ~honey, lit, "glass", cuts=[0.45, 0.7], lo=2)          # clear glass above the honey
    c.fill(K.rect(S, S, 9, 15, 22, 15) & body, h[4])                     # the honey's surface
    c.fill(K.rect(S, S, 9, 27, 22, 27) & body, h[0])                     # the bottom, in shadow
    c.shade(neck, lit, "glass", cuts=[0.45, 0.7], lo=2)
    # glass highlights
    c.fill(K.rect(S, S, 10, 17, 10, 24), h[4])
    c.fill(K.rect(S, S, 11, 17, 11, 19), g[4])
    c.put(21, 18, h[3]); c.put(21, 19, h[3])
    # cloth cover, puffed over the mouth, tied with red string and a little bow
    cloth = K.ellipse(S, S, 15.5, 7.0, 9.0, 4.2) | K.rect(S, S, 8, 8, 23, 10)
    cloth &= ys < 11
    cv = K.lambert(K.dome(S, S, 14, 6, 10, 5, power=0.7), 3.0)
    c.shade(cloth, cv, "linen", cuts=[0.40, 0.62, 0.82], lo=1)
    c.fill(K.rect(S, S, 8, 10, 23, 10), ln[1])                           # cloth hem
    c.fill(K.rect(S, S, 9, 9, 22, 9), red[2])                            # string
    for (x, y, col) in ((23, 8, red[3]), (24, 8, red[2]), (24, 10, red[1]), (25, 11, red[1]), (23, 9, red[1])):
        c.put(x, y, col)
    # a drip running down the outside from the lip
    for y in range(11, 17):
        c.put(21, y, h[3] if y < 15 else h[2])
    c.put(21, 17, h[1])
    c.clean_orphans(passes=1)
    c.outline(P.OUTLINE)
    return c
