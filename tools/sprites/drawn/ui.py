"""UI pieces drawn in code: a framed parchment panel (9-slice ready), an inventory slot, hearts.

Warm Apico-like theme (D28): a wooden frame, parchment inside, recessed item squares, punchy red hearts.
"""
import numpy as np

from . import canvas as K
from . import palette as P


def panel(w=112, h=72, frame=4):
    """A wooden-framed parchment panel. The 4 corners + edges + centre slice cleanly for 9-slice use."""
    c = K.Canvas(w, h)
    xs, ys = K.grid(w, h)
    wood, pa = P.ramp("wood"), P.ramp("parch")
    outer = K.rect(w, h, 0, 0, w - 1, h - 1)
    for (x, y) in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):      # rounded outer corners
        outer[y, x] = False
    for (x, y) in ((1, 0), (0, 1), (w - 2, 0), (w - 1, 1), (0, h - 2), (1, h - 1), (w - 2, h - 1), (w - 1, h - 2)):
        outer[y, x] = False
    # frame: bevelled wood (lit top/left edges, dark bottom/right)
    v = 0.62 - 0.3 * ys / h - 0.15 * xs / w
    c.shade(outer, v, "wood", cuts=[0.2, 0.4, 0.58], hi=3)
    c.fill(K.rect(w, h, 2, 1, w - 3, 1), wood[3])
    c.fill(K.rect(w, h, 1, 2, 1, h - 3), wood[3])
    c.fill(K.rect(w, h, 2, h - 2, w - 3, h - 2), wood[1])
    c.fill(K.rect(w, h, w - 2, 2, w - 2, h - 3), wood[1])
    # parchment inside, with an inner shadow along the top and left (it sits below the frame)
    inner = K.rect(w, h, frame, frame, w - frame - 1, h - frame - 1)
    rng = np.random.default_rng(3)
    c.fill(inner, pa[3])
    n = K.value_noise(w, h, 6, 9, octaves=2)
    c.fill(inner & (n > 0.72), pa[4])
    c.fill(inner & (n < 0.24), pa[2])
    c.fill(K.rect(w, h, frame, frame, w - frame - 1, frame), pa[1])      # inner shadow
    c.fill(K.rect(w, h, frame, frame, frame, h - frame - 1), pa[1])
    c.fill(K.rect(w, h, frame + 1, frame + 1, w - frame - 1, frame + 1), pa[2])
    c.fill(K.rect(w, h, frame - 1, frame - 1, w - frame, frame - 1), wood[0])   # frame's inner rim
    c.fill(K.rect(w, h, frame - 1, frame - 1, frame - 1, h - frame), wood[0])
    c.fill(K.rect(w, h, frame - 1, h - frame, w - frame, h - frame), wood[4])
    c.fill(K.rect(w, h, w - frame, frame - 1, w - frame, h - frame), wood[4])
    # four brass corner studs
    g = P.ramp("gold")
    for (x, y) in ((2, 2), (w - 4, 2), (2, h - 4), (w - 4, h - 4)):
        c.put(x, y, g[4]); c.put(x + 1, y, g[2]); c.put(x, y + 1, g[2]); c.put(x + 1, y + 1, g[0])
    c.outline(P.OUTLINE)
    return c


def slot(size=36, selected=False):
    """A recessed item square (sized for a 32x32 icon). Selected = a gold ring."""
    c = K.Canvas(size, size)
    pa, wood, g = P.ramp("parch"), P.ramp("wood"), P.ramp("gold")
    c.fill(K.rect(size, size, 0, 0, size - 1, size - 1), pa[2])
    c.fill(K.rect(size, size, 0, 0, size - 1, 1), pa[0])                  # inset: dark top-left
    c.fill(K.rect(size, size, 0, 0, 1, size - 1), pa[0])
    c.fill(K.rect(size, size, 2, 2, size - 3, 2), pa[1])
    c.fill(K.rect(size, size, 2, 2, 2, size - 3), pa[1])
    c.fill(K.rect(size, size, 1, size - 1, size - 1, size - 1), pa[4])    # light bottom-right
    c.fill(K.rect(size, size, size - 1, 1, size - 1, size - 1), pa[4])
    if selected:
        ring = K.rect(size, size, 0, 0, size - 1, size - 1) & ~K.rect(size, size, 2, 2, size - 3, size - 3)
        c.fill(ring, g[3])
        c.fill(K.rect(size, size, 0, 0, size - 1, 0), g[4])
        c.fill(K.rect(size, size, 0, size - 1, size - 1, size - 1), g[1])
    c.outline(wood[0])
    return c


HEART = [
    "..XXX...XXX..",
    ".XXXXX.XXXXX.",
    "XXXXXXXXXXXXX",
    "XXXXXXXXXXXXX",
    "XXXXXXXXXXXXX",
    ".XXXXXXXXXXX.",
    "..XXXXXXXXX..",
    "...XXXXXXX...",
    "....XXXXX....",
    ".....XXX.....",
    "......X......",
]


def heart(fill=1.0):
    """A heart icon; fill = 1 full, 0.5 half (left half red), 0 empty (dark socket)."""
    w, h = len(HEART[0]), len(HEART)
    c = K.Canvas(w, h)
    m = np.array([[ch == "X" for ch in row] for row in HEART])
    xs, ys = K.grid(w, h)
    hr = P.ramp("heart")
    lit = K.lambert(K.dome(w, h, 6.5, 4.5, 7.5, 7.0, power=0.8), 3.0)
    empty = m.copy()
    c.fill(empty, P.ramp("chitin")[1])
    c.fill(empty & (ys < 3), P.ramp("chitin")[2])
    red = m & (xs < w * fill) if fill < 1 else m
    if fill > 0:
        c.shade(red, lit, "heart", cuts=[0.35, 0.6, 0.85], lo=1)
        for (x, y) in ((3, 2), (2, 3), (4, 2)):
            if red[y, x]:
                c.put(x, y, hr[4])
    c.outline(P.OUTLINE)
    return c
