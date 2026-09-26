"""Ground tiles drawn in code: grass, dirt and the 16 grass/dirt transition ("Wang corner") tiles.

32x32 per cell. Every tile is SEAMLESS: all noise and scatter wrap around the tile edges, so any two
tiles of a family sit side by side with no visible seam. The base stays deliberately quiet (big soft
patches, few colours); the life comes from small tufts/pebbles — the lesson of the 2026-07 grass research.

Transitions: each tile knows which of its 4 corners are grass (1) or dirt (0). A pixel's material comes
from the corners blended across the tile plus a shared wrapping noise field, so the grass edge wanders
naturally AND lines up across neighbouring tiles (both sides see the same corners and the same noise).
"""
import numpy as np

from . import canvas as K
from . import palette as P

T = 32


def _wrap_scatter(rng, n, min_d, size=T, margin=0):
    """Poisson-ish points on a torus. margin>0 keeps points that far from the tile edge instead (used
    for details that must never be cut by a seam between two DIFFERENT tile variants)."""
    pts = []
    tries = 0
    while len(pts) < n and tries < n * 60:
        tries += 1
        x, y = rng.uniform(margin, size - margin), rng.uniform(margin, size - margin)
        ok = True
        for (px, py) in pts:
            dx = min(abs(x - px), size - abs(x - px))
            dy = min(abs(y - py), size - abs(y - py))
            if dx * dx + dy * dy < min_d * min_d:
                ok = False
                break
        if ok:
            pts.append((x, y))
    return pts


def _put_wrap(c, x, y, col):
    c.put(int(x) % T, int(y) % T, col)


def _small_clusters(seed, lo_col, mid_col, hi_col, lo=0.30, hi=0.70, cells=8):
    """Base texture: small 2-4 px clusters of a darker and a lighter tone on a mid tone.
    Small scale on purpose: big patches repeat visibly every tile (the macro variation belongs to
    the ground shader's world-space tint, not to the tile)."""
    n = K.value_noise(T, T, cells, seed, octaves=2)
    c = K.Canvas(T, T)
    c.px[:] = (*mid_col, 255)
    c.fill(n < lo, lo_col)
    c.fill(n > hi, hi_col)
    c.clean_orphans(passes=1)
    return c


def grass(seed=1):
    """A lawn tile: a quiet base of small clusters + little blade tufts (lit tips, dark roots)."""
    g = P.ramp("grass")
    c = _small_clusters(100 + seed, g[1], g[2], g[3], lo=0.22, hi=0.79, cells=6)
    rng = np.random.default_rng(seed * 7 + 3)
    for (x, y) in _wrap_scatter(rng, 9, 7.0, margin=3):
        blades = rng.integers(2, 4)
        for b in range(blades):
            bx = x + (b - (blades - 1) / 2) * 1.6
            h = rng.integers(2, 4)
            lean = rng.choice([-1, 0, 1])
            for k in range(h):
                col = g[4] if k == h - 1 else g[3]
                _put_wrap(c, bx + (lean if k == h - 1 else 0), y - k, col)
            _put_wrap(c, bx, y + 1, g[1])
    return c


def dirt(seed=1, pebbles=True):
    """Bare earth, Stardew-style: a flat base with sparse soft specks, a pebble or two, a little grit."""
    d, st = P.ramp("dirt"), P.ramp("stone")
    c = K.Canvas(T, T)
    c.px[:] = (*d[2], 255)
    rng = np.random.default_rng(seed * 11 + 5)
    for (x, y) in _wrap_scatter(rng, 9, 6.0):                  # soft darker clods (2-3 px)
        x, y = int(x), int(y)
        _put_wrap(c, x, y, d[1]); _put_wrap(c, x + 1, y, d[1])
        if rng.random() < 0.5:
            _put_wrap(c, x, y + 1, d[1])
        _put_wrap(c, x, y - 1, d[3])                           # lit rim above the clod
    for (x, y) in _wrap_scatter(rng, 8, 5.0):                  # light grit
        _put_wrap(c, x, y, d[3])
    if pebbles:
        for (x, y) in _wrap_scatter(rng, int(rng.integers(1, 3)), 12, margin=3):
            x, y = int(x), int(y)
            c.put(x, y, st[3]); c.put(x + 1, y, st[2])
            c.put(x, y + 1, st[2]); c.put(x + 1, y + 1, st[1])
            c.put(x, y + 2, d[0]); c.put(x + 1, y + 2, d[0]); c.put(x + 2, y + 1, d[1])
    return c


def _grass_field(corners, seed=5, pad=1):
    """Grass/dirt decision on an EXTENDED grid (-pad .. T-1+pad), so edge effects at the tile border see
    what the neighbouring tile will actually have (it shares these corners and the wrapping noise)."""
    tl, tr, bl, br = corners
    n = T + 2 * pad
    xs = (np.arange(n) - pad + 0.5)[None, :].repeat(n, 0)
    ys = (np.arange(n) - pad + 0.5)[:, None].repeat(n, 1)
    u, v = np.clip(xs / T, 0, 1), np.clip(ys / T, 0, 1)
    field = tl * (1 - u) * (1 - v) + tr * u * (1 - v) + bl * (1 - u) * v + br * u * v
    noise = K.value_noise(T, T, 2, seed, octaves=2)
    nz = noise[(ys.astype(int) - 0) % T, (xs.astype(int)) % T]
    return field + (nz - 0.5) * 0.6 > 0.5


def transition(corners, grass_tile, dirt_tile, seed=5):
    """One Wang-corner tile. corners = (top-left, top-right, bottom-left, bottom-right), 1 = grass."""
    ext = _grass_field(corners, seed)
    is_grass = ext[1:-1, 1:-1]
    up, down = ext[:-2, 1:-1], ext[2:, 1:-1]
    left, right = ext[1:-1, :-2], ext[1:-1, 2:]
    c = K.Canvas(T, T)
    c.px[:] = dirt_tile.px
    c.px[is_grass] = grass_tile.px[is_grass]
    g, d = P.ramp("grass"), P.ramp("dirt")
    edge_grass = is_grass & ~(up & down & left & right)
    c.fill(edge_grass & ~down, g[1])                          # the grass lip over the dirt
    c.fill(edge_grass & down & (~left | ~right), g[2])
    c.fill(~is_grass & up, d[0])                              # 1-px shadow cast by the raised grass
    c.fill(~is_grass & ~up & (left | right), d[1])
    return c


def wang_set(grass_tile, dirt_tile):
    """All 16 corner tiles, keyed by (tl, tr, bl, br)."""
    out = {}
    for k in range(16):
        corners = ((k >> 3) & 1, (k >> 2) & 1, (k >> 1) & 1, k & 1)
        out[corners] = transition(corners, grass_tile, dirt_tile)
    return out


def render_terrain(cell_grass, variants, dirt_tile, wang):
    """Compose a terrain image from a (rows+1) x (cols+1) CORNER grid of 1/0 (grass/dirt).
    Pure-grass cells pick a grass variant by position hash (like the game's VariantTileId)."""
    rows, cols = len(cell_grass) - 1, len(cell_grass[0]) - 1
    out = K.Canvas(cols * T, rows * T)
    for r in range(rows):
        for q in range(cols):
            k = (cell_grass[r][q], cell_grass[r][q + 1], cell_grass[r + 1][q], cell_grass[r + 1][q + 1])
            h = (q * 73856093 ^ r * 19349663) & 0xFFFF
            if k == (1, 1, 1, 1):
                tile = variants[h % len(variants)]
            elif k == (0, 0, 0, 0):
                tile = dirt_tile[h % len(dirt_tile)] if isinstance(dirt_tile, list) else dirt_tile
            else:
                tile = wang[k]
            out.px[r * T:(r + 1) * T, q * T:(q + 1) * T] = tile.px
    return out
