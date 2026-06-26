#!/usr/bin/env python3
"""Underground primitives — carving tunnels/caverns out of solid rock + rarity-based ore fill.
See docs/guides/authoring/caves.md for the spatial heuristics these encode. The convention: the
builder's ground is `cave_floor`; "carving" = recording cells to LEAVE OPEN; everything else gets
a block occupant via `fill_solid`. All coords are (x, y) cells.
"""
import math
import random

from features.terrain import noise_field


def _dims(b):
    return len(b.ground[0]), len(b.ground)        # (W, H)


def _disk(cx, cy, r):
    rr = int(math.ceil(r))
    return {(x, y) for y in range(cy - rr, cy + rr + 1) for x in range(cx - rr, cx + rr + 1)
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + 0.5}


def _ca_smooth(cells, x0, y0, x1, y1, *, passes=2, survive=4, birth=5):
    """Cellular-automata smoothing (the 4-5 rule) over a bbox: an open cell stays open with
    >= `survive` open 8-neighbours; a solid one opens with >= `birth`. Removes salt-and-pepper
    specks and rounds blob edges organically (the natural-cave finishing pass)."""
    cur = set(cells)
    for _ in range(passes):
        nxt = set()
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                n = sum(((x + dx, y + dy) in cur)
                        for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy)
                if ((x, y) in cur and n >= survive) or ((x, y) not in cur and n >= birth):
                    nxt.add((x, y))
        cur = nxt
    return cur


def carve_tunnel(b, start, end, *, style="natural", width=2, seed=0, wobble=0.55):
    """Carve a tunnel from start to end. style='natural' MEANDERS (momentum toward the goal + wobble,
    varying width); style='straight' is a clean man-made corridor (pair it with rail + supports).
    Returns the set of carved (open) cells."""
    W, H = _dims(b)
    rng = random.Random(seed)
    x, y = start
    ex, ey = end
    heading = math.atan2(ey - y, ex - x)
    carved = set()
    maxsteps = 4 * (abs(ex - x) + abs(ey - y)) + 60
    steps = 0
    while abs(x - ex) + abs(y - ey) > 1 and steps < maxsteps:
        steps += 1
        if style == "straight":
            if abs(ex - x) >= abs(ey - y):
                x += (ex > x) - (ex < x)
            else:
                y += (ey > y) - (ey < y)
            w = width
        else:
            goal = math.atan2(ey - y, ex - x)
            heading += 0.4 * math.atan2(math.sin(goal - heading), math.cos(goal - heading))
            heading += rng.uniform(-wobble, wobble)
            x += int(round(math.cos(heading)))
            y += int(round(math.sin(heading)))
            w = max(1, width + rng.choice([-1, 0, 0, 1]))
        x = max(0, min(W - 1, x))
        y = max(0, min(H - 1, y))
        for c in _disk(x, y, w / 2.0):
            if b.in_bounds(*c):
                carved.add(c)
    return carved


def carve_cavern(b, cx, cy, *, shape="blob", size=8, seed=0):
    """Carve a NATURAL cavern — a soft radial mask blended with fBm noise, thresholded, then
    cellular-automata smoothed (see docs/guides/authoring/caves.md). This replaces the old
    union-of-circles, which read as symmetric lobes. `shape` tunes elongation + edge roughness;
    `long` stays a fat meander gallery. Returns the set of carved (open) cells.
    `rough` = how noise-driven (irregular) the outline is vs. the radial mask."""
    W, H = _dims(b)
    if shape == "long":
        return carve_tunnel(b, (cx - size, cy), (cx + size, cy),
                            style="natural", width=5, seed=seed, wobble=0.3)
    # (x-radius mult, y-radius mult, edge-roughness): the cavern's radius ≈ `size`.
    ex, ey, rough = {"lobed": (1.45, 0.80, 0.38),
                     "rocky": (1.00, 1.00, 0.46),
                     "blob":  (1.00, 1.00, 0.36)}.get(shape, (1.00, 1.00, 0.36))
    rx, ry = size * ex, size * ey
    R = int(max(rx, ry) * 1.3)
    x0, y0, x1, y1 = cx - R, cy - R, cx + R, cy + R
    span = 2 * R + 1
    nf = noise_field(span, span, wavelength=max(5, int(size * 0.8)), octaves=3, seed=seed)
    cells = set()
    for j in range(span):
        for i in range(span):
            gx, gy = x0 + i, y0 + j
            if not b.in_bounds(gx, gy):
                continue
            d = math.hypot((i - R) / rx, (j - R) / ry)   # 1.0 at the ellipse edge (radius ≈ size)
            val = (1.0 - d) + rough * (2.0 * float(nf[j][i]) - 1.0)
            if val > 0.0:
                cells.add((gx, gy))
    cells = _ca_smooth(cells, x0, y0, x1, y1, passes=2)
    if shape == "rocky":                                  # leave a few interior rock columns
        rng = random.Random(seed ^ 0x5151)
        interior = [c for c in cells if all((c[0] + dx, c[1] + dy) in cells
                    for dx in (-1, 0, 1) for dy in (-1, 0, 1))]
        for c in rng.sample(interior, k=min(len(interior), max(1, size // 4))):
            cells.discard(c)
    return {c for c in cells if b.in_bounds(*c)}


def place_pool(b, cx, cy, rx, ry, carved, *, seed=0):
    """A still pool inside a carved area (deep core + shallow rim). Returns the pool cells."""
    pool = set()
    for y in range(cy - ry - 1, cy + ry + 2):
        for x in range(cx - rx - 1, cx + rx + 2):
            if (x, y) not in carved or not b.in_bounds(x, y):
                continue
            if not b.is_free(x, y):            # don't flood a wall/occupant cell
                continue
            nx, ny = (x - cx) / (rx + 0.5), (y - cy) / (ry + 0.5)
            if nx * nx + ny * ny <= 1.0:
                deep = nx * nx + ny * ny <= 0.4
                b.set_ground(x, y, "water_deep" if deep else "water_shallow", surface="water")
                b.reserve(x, y, surface="water")
                pool.add((x, y))
    return pool


def fill_solid(b, carved, table, *, seed=0, substrate=None):
    """Fill every non-carved cell with a block. `table` = {'base':id, 'veins':[(id,count,lo,hi)...],
    'pockets':[(id,count,radius,zone)...]} where zone in {'top','bottom','any'} (top=high-y/entrance,
    bottom=low-y/deep). Ore goes in random-walk VEINS; pockets are clustered patches; the rest is the
    base block. `substrate(x, y) -> block_id` (optional) overrides the base PER CELL — pass it to paint
    dirt-left / rock-right / hard-stone-deep regions (the dirt↔rock interface)."""
    W, H = _dims(b)
    rng = random.Random(seed)
    solid = [(x, y) for y in range(H) for x in range(W) if (x, y) not in carved]
    solidset = set(solid)
    assign = {}
    for (bid, count, lo, hi) in table.get("veins", []):
        for _ in range(count):
            x, y = rng.choice(solid)
            for _ in range(rng.randint(lo, hi)):
                if (x, y) in solidset:
                    assign[(x, y)] = bid
                x += rng.choice([-1, 0, 1])
                y += rng.choice([-1, 0, 1])
    for (bid, count, r, zone) in table.get("pockets", []):
        for _ in range(count):
            cx = rng.randrange(W)
            if zone == "top":
                cy = rng.randint(H // 2, H - 1)
            elif zone == "bottom":
                cy = rng.randint(0, H // 2)
            else:
                cy = rng.randrange(H)
            for c in _disk(cx, cy, r):
                if c in solidset and rng.random() < 0.8:
                    assign[c] = bid
    base = table.get("base", "stone_block")
    for c in solid:
        bid = assign.get(c)
        if bid is None:
            bid = substrate(*c) if substrate else base
        b.place_occupant(bid, *c)
    return solidset
