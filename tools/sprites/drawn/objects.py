"""World objects drawn in code: the storage chest and the flowering tree.

Style (matches the current game art): Stardew-like face-on 3/4 view — the front face dominates, a thin
top band shows depth, light from the top-left, dark warm outlines, chunky and slightly overbuilt.
"""
import numpy as np

from . import canvas as K
from . import palette as P


def _round_corners(mask, x0, y0, x1, r):
    """Cut quarter-circle corners of radius r off the top edge of a rectangle mask."""
    for dy in range(r):
        cut = r - int(round(np.sqrt(max(0, r * r - (r - dy - 0.5) ** 2))))
        for dx in range(cut):
            mask[y0 + dy, x0 + dx] = False
            mask[y0 + dy, x1 - dx] = False


# ----------------------------------------------------------------------------- chest (2x1 cells)
def chest():
    """Wooden storage chest, footprint 2x1 cells -> 64 px wide at 32 px/cell.

    The classic farm-game chest: a domed lid (a half-cylinder seen from the front-top, rounded ends),
    a plank body, dark iron end-bands with rivets, a brass lock on the lid's lip. Light from the top-left."""
    W, H = 64, 44
    c = K.Canvas(W, H)
    xs, ys = K.grid(W, H)
    rng = np.random.default_rng(7)
    wood, iron, gold = P.ramp("wood"), P.ramp("iron"), P.ramp("gold")

    x0, x1 = 2, 61
    lid0, lid1 = 3, 16
    body0, body1 = 19, 40

    # ---- lid: rounded ends (radius 6), cylinder shading with the crest ~a third of the way down
    lid = K.rect(W, H, x0, lid0, x1, lid1)
    _round_corners(lid, x0, lid0, x1, 6)
    t = (ys - lid0) / (lid1 - lid0)
    crest = np.exp(-((t - 0.34) / 0.46) ** 2)
    v = 0.30 + 0.66 * crest - 0.16 * (xs - x0) / (x1 - x0)
    v = v - 0.30 * np.clip((t - 0.78) / 0.22, 0, 1)            # only the last rows turn dark
    c.shade(lid, v, "wood", cuts=[0.30, 0.48, 0.66, 0.86])
    c.fill(K.rect(W, H, x0 + 7, 9, x1 - 7, 9), wood[2])          # one lid seam, softly
    c.fill(K.rect(W, H, x0, lid1, x1, lid1), wood[0])            # the lid's lip
    c.fill(K.rect(W, H, x0, lid1 + 1, x1, lid1 + 2), P.OUTLINE)   # shadow under the overhang

    # ---- body: three boards
    body = K.rect(W, H, x0 + 1, body0, x1 - 1, body1)
    v = 0.64 - 0.44 * (ys - body0) / (body1 - body0) - 0.16 * (xs - x0) / (x1 - x0)
    c.shade(body, v, "wood", cuts=[0.14, 0.30, 0.50], hi=3)
    for py in (26, 33):
        c.fill(K.rect(W, H, x0 + 1, py, x1 - 1, py), wood[0])
        c.fill(K.rect(W, H, x0 + 1, py + 1, x1 - 1, py + 1), wood[3] if py == 26 else wood[2])
    for (jx, jy0, jy1) in ((22, body0, 25), (41, 28, 32), (29, 35, body1 - 1)):
        c.fill(K.rect(W, H, jx, jy0, jx, jy1), wood[0])
        c.fill(K.rect(W, H, jx + 1, jy0, jx + 1, jy1), wood[2])
    for _ in range(34):
        gy = int(rng.integers(body0 + 1, body1 - 1))
        if gy in (26, 27, 33, 34):
            continue
        gx = int(rng.integers(x0 + 8, x1 - 12))
        col = c.colour(gx, gy)
        i = wood.index(col) if col in wood else 2
        c.fill(K.rect(W, H, gx, gy, gx + int(rng.integers(2, 7)), gy), wood[max(0, i - 1)])
    c.fill(K.rect(W, H, x0 + 1, body1, x1 - 1, body1), wood[0])

    # ---- dark iron end-bands over lid + body (5 px), following the lid's rounded ends
    for left in (True, False):
        bx0, bx1 = (x0, x0 + 5) if left else (x1 - 5, x1)
        band = K.rect(W, H, bx0, lid0, bx1, body1) & (lid | body | K.rect(W, H, 0, body0, W, body1))
        vv = (0.50 if left else 0.30) + 0.3 * np.exp(-((ys - lid0 - 4) / 5.0) ** 2) - 0.25 * (ys - lid0) / (body1 - lid0)
        c.shade(band, vv, "iron", cuts=[0.24, 0.42, 0.62], hi=3)
        edge_x = bx1 if left else bx0
        c.fill(K.rect(W, H, edge_x, lid0, edge_x, body1) & band, iron[0])      # inner edge of the band
        c.fill(K.rect(W, H, bx0, lid1 + 1, bx1, lid1 + 2), P.OUTLINE)
        rx = bx0 + 2 if left else bx0 + 3
        for ry in (lid0 + 7, body0 + 3, body0 + 10, body1 - 3):
            c.put(rx, ry, iron[4] if left else iron[3])
            c.put(rx, ry + 1, iron[0])

    # ---- brass lock hanging from the lid lip
    lx0, lx1, ly0, ly1 = 27, 36, lid1 - 4, body0 + 6
    c.fill(K.rect(W, H, lx0 + 1, ly1 + 1, lx1 + 1, ly1 + 1), wood[0])
    c.fill(K.rect(W, H, lx1 + 1, ly0 + 2, lx1 + 1, ly1 + 1), wood[0])
    m = K.rect(W, H, lx0, ly0, lx1, ly1)
    _round_corners(m, lx0, ly0, lx1, 2)
    v = 0.92 - 0.55 * (ys - ly0) / (ly1 - ly0) - 0.25 * (xs - lx0) / (lx1 - lx0)
    c.shade(m, v, "gold", cuts=[0.22, 0.42, 0.62, 0.82])
    c.inner_edge(m, gold[0])
    c.fill(K.rect(W, H, lx0 + 2, ly0 + 1, lx1 - 3, ly0 + 1), gold[4])
    c.fill(K.rect(W, H, 31, ly0 + 5, 32, ly0 + 6), P.OUTLINE)
    c.fill(K.rect(W, H, 31, ly0 + 7, 32, ly0 + 9), P.OUTLINE)
    c.put(32, ly0 + 9, gold[1])

    c.clean_orphans()
    c.outline(P.OUTLINE)
    return c


# ----------------------------------------------------------------------------- flowering tree (2x3 cells)
CROWN_LOBES = [  # (cx, cy, r) — the hand-placed crown silhouette
    (32, 17, 14), (19, 25, 12), (45, 25, 12), (12, 38, 10), (52, 38, 10),
    (32, 40, 18), (20, 49, 10), (44, 49, 10), (32, 52, 10),
]


def flowering_tree():
    """A flowering fruit tree: footprint 2 cells -> 64x96 at 32 px/cell, trunk at the bottom centre.

    Crown = a hand-placed silhouette packed with leaf clumps, each shaded as its own dome under one light,
    drawn back-to-front so front clumps cast a shadow onto the ones behind."""
    W, H = 64, 96
    c = K.Canvas(W, H)
    rng = np.random.default_rng(31)
    xs, ys = K.grid(W, H)
    leaf, bark, pink = P.ramp("leaf"), P.ramp("bark"), P.ramp("pink")

    # ---- trunk: tapered, flaring into roots
    tx, ttop, tbot = 32, 56, 92
    trunk = np.zeros((H, W), bool)
    th = np.zeros((H, W))
    for y in range(ttop, tbot + 1):
        t = (y - ttop) / (tbot - ttop)
        half = 5.0 + 1.4 * t + (7.0 * ((t - 0.74) / 0.26) ** 2 if t > 0.74 else 0)
        d = (xs[y] - tx - 0.5) / half
        inside = np.abs(d) <= 1
        trunk[y, inside] = True
        th[y, inside] = np.sqrt(1 - d[inside] ** 2)
    v = K.lambert(th, strength=5.0) * 1.08 - 0.55 * np.clip((70 - ys) / 12.0, 0, 1)
    c.shade(trunk, v, "bark", cuts=[0.34, 0.52, 0.70, 0.86], hi=3)
    for _ in range(26):                                         # bark ridges + their lit edges
        x = int(rng.integers(tx - 5, tx + 6))
        y = int(rng.integers(ttop + 6, tbot - 3))
        ln = int(rng.integers(3, 8))
        for yy in range(y, min(y + ln, tbot - 1)):
            if trunk[yy, x] and trunk[yy, x - 1]:
                c.put(x, yy, bark[0] if x > tx - 2 else bark[1])
                if x < tx and trunk[yy, x - 1]:
                    c.put(x - 1, yy, bark[3])
    for (rx0, ry0, rx1, ry1) in ((29, 84, 22, 93), (35, 84, 42, 93)):   # root toes
        m = K.capsule(W, H, rx0, ry0, rx1, ry1, 2.2)
        hh = K.capsule_height(W, H, rx0, ry0, rx1, ry1, 2.2)
        rv = K.lambert(hh, strength=3.0)
        c.shade(m & ~trunk, rv, "bark", cuts=[0.34, 0.52, 0.70, 0.86], hi=3)
    for (x, y0, y1) in ((27, 88, 92), (37, 88, 92)):             # root separations
        for yy in range(y0, y1 + 1):
            c.put(x, yy, bark[0])
    kx, ky = 29, 72                                                 # a knot
    c.put(kx, ky, bark[0]); c.put(kx + 1, ky, bark[1]); c.put(kx, ky + 1, bark[1]); c.put(kx - 1, ky - 1, bark[3])

    # ---- crown silhouette
    crown = np.zeros((H, W), bool)
    for (cx, cy, r) in CROWN_LOBES:
        crown |= K.ellipse(W, H, cx, cy, r, r * 0.95)
    # clumps: jittered hex packing inside the crown, plus edge bumps along the silhouette
    clumps = []
    for row, cy in enumerate(np.arange(4, 64, 5.5)):
        off = 0 if row % 2 == 0 else 3.2
        for cx in np.arange(2 + off, 64, 6.4):
            jx, jy = cx + rng.uniform(-1.4, 1.4), cy + rng.uniform(-1.2, 1.2)
            ix, iy = int(jx), int(jy)
            if 0 <= ix < W and 0 <= iy < H and crown[iy, ix]:
                clumps.append((jx, jy, rng.uniform(4.4, 5.8)))
    clumps.sort(key=lambda k: (k[1], k[0]))                    # back (top) first
    owner = -np.ones((H, W), int)
    local = np.zeros((H, W))
    for i, (cx, cy, r) in enumerate(clumps):
        d = K.dome(W, H, cx, cy, r, r * 0.9, power=0.75)
        m = (d > 0) & crown
        owner[m] = i
        local[m] = K.lambert(d, strength=5.5)[m]
    body = owner >= 0
    # the crown as one big dome gives the global light (bright top-left, deep bottom-right)
    big = np.zeros((H, W))
    for (cx, cy, r) in CROWN_LOBES:
        big = np.maximum(big, K.dome(W, H, cx, cy, r, r))
    glob = K.lambert(big, strength=14.0)
    glob = np.clip(glob * 1.05 - 0.28 * (ys - 10) / 50, 0, 1)
    val = 0.42 * local + 0.70 * glob - 0.08
    # cast shadow under each front clump onto the clump behind
    pad = np.pad(owner, ((2, 0), (0, 0)), constant_values=-1)
    a1, a2 = pad[1:-1], pad[:-2]
    shadowed = body & (((a1 > owner) & (a1 >= 0)) | ((a2 > owner) & (a2 >= 0)))
    val = np.where(shadowed, val - 0.26, val)
    c.shade(body, val, "leaf", cuts=[0.30, 0.47, 0.63, 0.80])

    # ---- blossoms: small five-petal flowers, clustered, favouring lit clumps
    placed = []
    tries = 0
    while len(placed) < 30 and tries < 4000:
        tries += 1
        x, y = int(rng.integers(5, 59)), int(rng.integers(5, 58))
        if not body[y, x] or shadowed[y, x] or val[y, x] < 0.42:
            continue
        if any((x - px) ** 2 + (y - py) ** 2 < 26 for px, py in placed):
            continue
        placed.append((x, y))
        lit = val[y, x] > 0.64
        top, side, low = (pink[4], pink[3], pink[2]) if lit else (pink[3], pink[2], pink[1])
        c.put(x, y - 1, top); c.put(x - 1, y, side); c.put(x + 1, y, low); c.put(x, y + 1, low)
        c.put(x, y, P.ramp("gold")[3] if lit else pink[3])

    c.clean_orphans(passes=1)
    before = c.alpha()
    c.outline(P.EXTRA["outline_leaf"])
    ring = c.alpha() & ~before
    c.px[ring & (ys > 60) & ~K.ellipse(W, H, 32, 52, 12, 10)] = (*bark[0], 255)
    return c
