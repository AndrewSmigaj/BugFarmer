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


def carve_chamber(b, cx, cy, size, *, seed=0):
    """An IRREGULAR cavern = a union of 2-3 offset organic blobs strung along a random long axis (kidney /
    peanut / lumpy outlines), each `carve_cavern`'d so the edge is fBm+CA organic — never a single round
    bowl. Overall extent ≈ `size`. Use this instead of a lone carve_cavern when you want a chamber that
    doesn't read as a circle. Returns the carved cells."""
    rng = random.Random(seed)
    axis = rng.random() * 2 * math.pi
    n = 2 if size < 12 else 3
    cells = set()
    for i in range(n):
        t = (i / max(1, n - 1) - 0.5) * 1.3                 # spread the blobs along the long axis
        bx = int(round(cx + math.cos(axis) * size * t * 0.7))
        by = int(round(cy + math.sin(axis) * size * t * 0.7))
        bsz = max(4, int(size * rng.uniform(0.52, 0.82)))
        shp = rng.choice(["blob", "rocky", "lobed"])
        cells |= carve_cavern(b, bx, by, shape=shp, size=bsz, seed=seed + i * 7)
    return cells


def cave_pool(b, cx, cy, size, carved, *, seed=0, shore=True):
    """An underground POOL with an IRREGULAR waterline — the `lake()` recipe (a union of 2-3 offset,
    tilted blobs + a couple of concave BAYS), but CLIPPED to a cavern's carved cells so the water fills a
    low corner and bows along the rock. Deep core → shallow rim; the shoreline is then RE-DERIVED by an
    adjacency scan and dressed as a wet rock bank (damp `mud` ground with gaps + scattered pebbles/moss),
    NOT a clean ellipse with a uniform fringe. Returns the set of water cells. (Cf. terrain.lake.)"""
    rng = random.Random(seed)
    axis = rng.random() * 2 * math.pi
    nb = rng.randint(2, 3)
    blobs = []
    for i in range(nb):
        t = (i / max(1, nb - 1) - 0.5) * 1.1
        bx = cx + math.cos(axis) * size * t * 0.8 + rng.uniform(-0.2, 0.2) * size
        by = cy + math.sin(axis) * size * t * 0.8 + rng.uniform(-0.2, 0.2) * size
        br = size * rng.uniform(0.50, 0.75)
        ecc = rng.uniform(0.6, 0.95)
        ang = axis + rng.uniform(-0.6, 0.6)
        blobs.append((bx, by, br, ecc, ang))
    ph1, ph2 = rng.random() * 2 * math.pi, rng.random() * 2 * math.pi

    def union(x, y):
        best = -9.0
        for (bx, by, br, ecc, ang) in blobs:
            dx, dy = x - bx, y - by
            ca, sa = math.cos(-ang), math.sin(-ang)
            u, v = dx * ca - dy * sa, (dx * sa + dy * ca) / ecc
            a = math.atan2(dy, dx)
            rr = br * (1 + 0.08 * math.sin(2 * a + ph1) + 0.05 * math.sin(3 * a + ph2))
            best = max(best, 1.0 - math.hypot(u, v) / rr)
        return best

    bays = []                                               # concave notches → a believable shoreline
    for _ in range(rng.randint(2, 4)):
        a = rng.random() * 2 * math.pi
        d = 1.0
        while d < size * 1.6 and union(cx + d * math.cos(a), cy + d * math.sin(a)) > 0:
            d += 1.0
        bays.append((cx + (d - 1.0) * math.cos(a), cy + (d - 1.0) * math.sin(a), size * rng.uniform(0.18, 0.34)))

    def signed(x, y):
        s = union(x, y)
        for (bx, by, br) in bays:
            cut = 1.0 - math.hypot(x - bx, y - by) / br
            if cut > 0:
                s = min(s, -cut)
        return s

    mr = int(size * 1.7) + 2
    water = set()
    for dy in range(-mr, mr + 1):
        for dx in range(-mr, mr + 1):
            x, y = cx + dx, cy + dy
            if (x, y) not in carved or not b.in_bounds(x, y) or not b.is_free(x, y):
                continue                                    # water only inside the cavern void, off columns
            s = signed(x, y)
            if s > 0.42:
                b.set_ground(x, y, "water_deep", surface="water")
                b.reserve(x, y, surface="water")
                water.add((x, y))
            elif s > 0.0:
                b.set_ground(x, y, "water_shallow", surface="water")
                b.reserve(x, y, surface="water")
                water.add((x, y))
    if shore and water:                                     # re-derive the bank (dry carved cells touching water)
        for (x, y) in sorted(carved):
            if (x, y) in water or not b.is_free(x, y):
                continue
            if not any((x + ax, y + ay) in water for ax in (-1, 0, 1) for ay in (-1, 0, 1) if ax or ay):
                continue
            r = rng.random()
            if r < 0.6:
                b.set_ground(x, y, "mud")                   # damp bank, with gaps (not a solid ring)
            if r < 0.22:
                b.place_occupant(rng.choice(["rubble", "cave_moss", "moss_clump"]), x, y,
                                 surface=None, reserve=False)
    return water


def _vein(start, length, rng, *, turn=0.55, fork_chance=0.11):
    """Ore VEIN as a momentum random-walk (not a directionless blob): pick a heading and step along it,
    nudging the heading only a little each step so the vein STREAKS across the rock; occasionally FORK a
    shorter branch off the side (the 'motherlode + branches' pattern). Yields the (x, y) cells it crosses.
    A pair of adjacent cells per step gives the vein a little thickness so it reads, not a hairline."""
    branches = [(float(start[0]), float(start[1]), rng.uniform(0, 2 * math.pi), int(length))]
    while branches:
        fx, fy, ang, steps = branches.pop()
        for i in range(steps):
            ix, iy = int(round(fx)), int(round(fy))
            yield ix, iy
            if rng.random() < 0.5:                                  # a touch of thickness (1–2 cells wide)
                yield ix + rng.choice((-1, 1)), iy
            ang += rng.uniform(-turn, turn)                         # momentum: mostly keep the heading
            fx += math.cos(ang)
            fy += math.sin(ang)
            if steps - i > 4 and rng.random() < fork_chance:        # fork a shorter branch to the side
                branches.append((fx, fy, ang + rng.choice((-1, 1)) * rng.uniform(0.7, 1.3), (steps - i) // 2))


def _band_range(band, H):
    """y-range for a depth band. top = high y (shallow/north/entrance); bottom = low y (deep/south).
    `deep` is the bottom FIFTH (the richest seam); `surface` the top fifth."""
    return {"surface": (4 * H // 5, H), "top": (H // 2, H), "mid": (H // 4, 3 * H // 4),
            "bottom": (0, H // 2), "deep": (0, H // 5)}.get(band, (0, H))


def _grid_seeds(solidset, W, ylo, yhi, n, rng):
    """`n` vein-start points spread on a JITTERED GRID over [0,W]×[ylo,yhi], each snapped to the nearest
    solid cell. Even coverage by construction — no big ore-free walls the way pure rng.choice leaves them."""
    if n <= 0 or yhi <= ylo:
        return []
    h = yhi - ylo
    cols = max(1, int(round(math.sqrt(n * W / float(h)))))
    rows = max(1, int(math.ceil(n / float(cols))))
    cw, ch = W / float(cols), h / float(rows)
    order = [(c, r) for r in range(rows) for c in range(cols)]
    rng.shuffle(order)
    seeds = []
    for (c, r) in order:
        if len(seeds) >= n:
            break
        bx, by = c * cw + rng.random() * cw, ylo + r * ch + rng.random() * ch
        ix, iy = int(bx), int(by)
        for rad in range(0, 6):                                # snap to nearest solid cell
            cand = [(ix + dx, iy + dy) for dx in range(-rad, rad + 1) for dy in range(-rad, rad + 1)
                    if (ix + dx, iy + dy) in solidset]
            if cand:
                seeds.append(min(cand, key=lambda p: (p[0] - bx) ** 2 + (p[1] - by) ** 2))
                break
    return seeds


def fill_solid(b, carved, table, *, seed=0, substrate=None):
    """Fill every non-carved cell with a block. `table` = {'base':id, 'veins':[(id,count,lo,hi[,band])...],
    'pockets':[(id,count,radius,zone)...]} where band/zone in {'top','mid','bottom','any'} (top=high-y/
    shallow, bottom=low-y/deep). Ore goes in random-walk VEINS whose START points are spread on a jittered
    grid over the band (even coverage — no dead stone walls); deeper/richer ore = more veins in the 'bottom'
    band (data, in the table). Pockets are clustered patches; the rest is the base block. `substrate(x, y) ->
    block_id` (optional) overrides the base PER CELL — pass it to paint the dirt↔stone depth gradient."""
    W, H = _dims(b)
    rng = random.Random(seed)
    solid = [(x, y) for y in range(H) for x in range(W) if (x, y) not in carved]
    solidset = set(solid)
    assign = {}
    for entry in table.get("veins", []):
        bid, count, lo, hi = entry[0], entry[1], entry[2], entry[3]
        band = entry[4] if len(entry) > 4 else "any"
        ylo, yhi = _band_range(band, H)
        for (sx, sy) in _grid_seeds(solidset, W, ylo, yhi, count, rng):
            for (vx, vy) in _vein((sx, sy), rng.randint(lo, hi), rng):
                if (vx, vy) in solidset:
                    assign[(vx, vy)] = bid
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
