#!/usr/bin/env python3
"""Underground primitives — carving tunnels/caverns out of solid rock + rarity-based ore fill.
See docs/guides/authoring/caves.md for the spatial heuristics these encode. The convention: the
builder's ground is `cave_floor`; "carving" = recording cells to LEAVE OPEN; everything else gets
a block occupant via `fill_solid`. All coords are (x, y) cells.
"""
import math
import random


def _dims(b):
    return len(b.ground[0]), len(b.ground)        # (W, H)


def _disk(cx, cy, r):
    rr = int(math.ceil(r))
    return {(x, y) for y in range(cy - rr, cy + rr + 1) for x in range(cx - rr, cx + rr + 1)
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + 0.5}


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
    """Carve a cavern of a given SHAPE (never a clean ellipse). Returns carved cells.
    blob = overlapping disks; long = a fat meander; rocky = blob with a bitten edge (leave interior
    rock columns via the scene); lobed = a few merged blobs."""
    rng = random.Random(seed)
    if shape == "long":
        return carve_tunnel(b, (cx - size, cy), (cx + size, cy),
                            style="natural", width=5, seed=seed, wobble=0.3)
    n = {"blob": 4, "rocky": 5, "lobed": 3}.get(shape, 4)
    centers = [(cx, cy)] + [(cx + rng.randint(-size // 2, size // 2),
                             cy + rng.randint(-size // 2, size // 2)) for _ in range(n - 1)]
    carved = set()
    for (bx, by) in centers:
        for c in _disk(bx, by, rng.uniform(size * 0.4, size * 0.6)):
            if b.in_bounds(*c):
                carved.add(c)
    if shape == "rocky":
        edge = [c for c in carved if any((c[0] + dx, c[1] + dy) not in carved
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        for c in edge:
            if rng.random() < 0.15:
                carved.discard(c)
    return carved


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


def fill_solid(b, carved, table, *, seed=0):
    """Fill every non-carved cell with a block. `table` = {'base':id, 'veins':[(id,count,lo,hi)...],
    'pockets':[(id,count,radius,zone)...]} where zone in {'top','bottom','any'} (top=high-y/entrance,
    bottom=low-y/deep). Ore goes in random-walk VEINS; pockets are clustered patches; rest is base."""
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
        b.place_occupant(assign.get(c, base), *c)
    return solidset
