#!/usr/bin/env python3
"""Ground/terrain primitives shared across scenes: paths and an organic pond.
All coordinate through the builder's ground grid + surface mask (paths -> surface 'path',
water -> reserved 'water'), so roads route around water and scatter avoids both."""
import math
import random


def hpath(b, x0, x1, y, tile="stone_path"):
    """Horizontal path strip on row y from x0..x1 (inclusive), surface='path'."""
    for x in range(x0, x1 + 1):
        if b.in_bounds(x, y):
            b.set_ground(x, y, tile, surface="path")


def vpath(b, x, y0, y1, tile="stone_path"):
    """Vertical path strip on column x from y0..y1 (inclusive), surface='path'."""
    for y in range(y0, y1 + 1):
        if b.in_bounds(x, y):
            b.set_ground(x, y, tile, surface="path")


def path(b, start, end, *, width=3, tile="stone_path", edge_tile=None,
         wobble=0.16, seed=0, taper_ends=0):
    """An ORGANIC road from start to end — NOT a dead-straight line. Wanders gently toward the
    goal (same wander rule as `stream`, but low wobble so it still reads as a deliberate road),
    paints a ~`width`-cell band with slightly uneven edges, and skips `reserved` cells (so it
    parts around water/buildings instead of clobbering them). surface='path'.

    - `edge_tile`: if given, the outermost band cells sometimes get this tile instead — the road
      FRAYS into dirt/trampled grass at its shoulders (e.g. edge_tile='dirt_path').
    - `taper_ends`: cells at each end where the band narrows to 1 — roads dwindle as they leave
      town rather than stopping square.
    Returns the painted cells. Keep wobble small (≈0.1–0.25); higher reads as a trail, not a road."""
    import math
    rng = random.Random(seed)
    (x, y), (ex, ey) = start, end
    total = abs(ex - x) + abs(ey - y)
    heading = math.atan2(ey - y, ex - x)
    cells, steps, traveled = set(), 0, 0
    while abs(x - ex) + abs(y - ey) > 1 and steps < 4 * total + 60:
        steps += 1
        traveled += 1
        goal = math.atan2(ey - y, ex - x)
        heading += 0.3 * math.atan2(math.sin(goal - heading), math.cos(goal - heading))
        heading += rng.uniform(-wobble, wobble)
        x += int(round(math.cos(heading)))
        y += int(round(math.sin(heading)))
        # narrow the band near the two ends if taper requested
        w = width
        if taper_ends:
            near = min(traveled, total - traveled)
            if near < taper_ends:
                w = max(1, int(round(width * (near + 1) / (taper_ends + 1))))
        r = w / 2.0
        rr = int(math.ceil(r))
        for dy in range(-rr, rr + 1):
            for dx in range(-rr, rr + 1):
                px, py = x + dx, y + dy
                dd = (dx * dx + dy * dy) ** 0.5
                if dd > r + 0.4 or not b.in_bounds(px, py) or b.reserved[py][px]:
                    continue
                t = tile
                if edge_tile and dd > r - 0.7 and rng.random() < 0.45:   # fray the shoulders
                    t = edge_tile
                b.set_ground(px, py, t, surface="path")
                cells.add((px, py))
    return cells


def stream(b, start, end, *, width=1, seed=0, wobble=0.5):
    """A meandering surface WATER channel from start to end (never straight). Sets water tiles +
    reserves; returns the water cells. Reuse the same wander rule as tunnels."""
    import math
    rng = random.Random(seed)
    x, y = start
    ex, ey = end
    heading = math.atan2(ey - y, ex - x)
    cells = set()
    steps = 0
    while abs(x - ex) + abs(y - ey) > 1 and steps < 4 * (abs(ex - x) + abs(ey - y)) + 60:
        steps += 1
        goal = math.atan2(ey - y, ex - x)
        heading += 0.3 * math.atan2(math.sin(goal - heading), math.cos(goal - heading))
        heading += rng.uniform(-wobble, wobble)
        x += int(round(math.cos(heading)))
        y += int(round(math.sin(heading)))
        r = max(0.5, width / 2.0 + rng.choice([-0.5, 0, 0]))
        rr = int(math.ceil(r))
        for dy in range(-rr, rr + 1):
            for dx in range(-rr, rr + 1):
                if dx * dx + dy * dy <= r * r + 0.5 and b.in_bounds(x + dx, y + dy):
                    deep = dx == 0 and dy == 0 and width >= 2
                    b.set_ground(x + dx, y + dy, "water_deep" if deep else "water_shallow", surface="water")
                    b.reserve(x + dx, y + dy, surface="water")
                    cells.add((x + dx, y + dy))
    return cells


def pond(b, cx, cy, rx, ry, seed=3):
    """An ORGANIC water feature: irregular shallow blob with a smaller deep centre + reeds."""
    rng = random.Random(seed)
    bank = []
    for y in range(cy - ry - 1, cy + ry + 2):
        for x in range(cx - rx - 1, cx + rx + 2):
            if not b.in_bounds(x, y):
                continue
            nx, ny = (x - cx) / (rx + 0.5), (y - cy) / (ry + 0.5)
            d = (nx * nx + ny * ny) ** 0.5
            if d <= 1.0 + rng.uniform(-0.15, 0.15):
                b.set_ground(x, y, "water_deep" if d <= 0.5 else "water_shallow", surface="water")
                b.reserve(x, y, surface="water")
            elif d <= 1.5:
                bank.append((x, y))
    for (x, y) in bank:
        if b.is_free(x, y) and b.surface[y][x] == "grass" and rng.random() < 0.3:
            b.place_occupant("reeds", x, y)


def forest(b, cx, cy, rx, ry, *, species=("tree_oak", "tree_pine"),
           understory=("bush", "bush", "bush", "fern", "mushroom_cluster"),
           density=0.6, seed=0, spacing=2, dirt=False):
    """An organic FOREST blob centred at (cx,cy), radii (rx,ry). Trees thin from a DENSE CORE to a
    ragged, sparse EDGE (so it reads as a natural stand, not a uniform spray); they're grid-aligned and
    kept `spacing` apart so the ~2-tall sprites don't overlap. Scattered understory (bushes/ferns) fills
    some gaps and natural clearings are left where the falloff/noise dips. Skips reserved/path/water and
    only plants on grass. `dirt=True` darkens the forest floor to dirt under the canopy. Returns the
    placed tree cells."""
    rng = random.Random(seed)
    placed = set()

    def spaced(x, y):
        return all((x + dx, y + dy) not in placed
                   for dx in range(-(spacing - 1), spacing) for dy in range(-(spacing - 1), spacing))

    cells = []
    for y in range(cy - ry - 2, cy + ry + 3):
        for x in range(cx - rx - 2, cx + rx + 3):
            if not b.in_bounds(x, y):
                continue
            nx, ny = (x - cx) / (rx + 0.5), (y - cy) / (ry + 0.5)
            d = (nx * nx + ny * ny) ** 0.5
            if d <= 1.0 + rng.uniform(-0.28, 0.18):                  # ragged organic edge
                cells.append((x, y, d))
    if dirt:
        for (x, y, d) in cells:
            if b.is_free(x, y) and b.surface[y][x] == "grass" and rng.random() < 0.5:
                b.set_ground(x, y, "dirt")
    rng.shuffle(cells)
    for (x, y, d) in cells:
        if not b.is_free(x, y) or b.surface[y][x] not in ("grass",):
            continue
        p = density * (1.18 - d)                                    # dense core -> ~0 at the rim
        if rng.random() < p and spaced(x, y):
            b.place_occupant(rng.choice(species), x, y)
            placed.add((x, y))
        elif understory and rng.random() < 0.12:                    # understory + clearings in the gaps
            b.place_occupant(rng.choice(understory), x, y)
    return placed


def lake(b, cx, cy, radius, *, seed=0, shore="sand", reeds=16):
    """A natural LAKE with an ORGANIC, lobed shoreline (per trees-and-ponds.md) — NOT a circle. Multiple
    angular harmonics (freqs 2..n) bump the radius around the perimeter for bays + spits; deep core ->
    shallow rim -> a `shore` beach ring (sand/mud) with gaps -> reeds clumped just outside the water,
    following the shape. Reserves the water. Returns reeds placed."""
    rng = random.Random(seed)
    n = rng.randint(4, 7)
    phases = [rng.random() * 2 * math.pi for _ in range(n)]
    amps = [rng.uniform(0.15, 0.30) for _ in range(n)]

    def rad(angle):
        r = radius
        for i in range(n):
            r += radius * amps[i] * math.sin((i + 2) * angle + phases[i])
        return max(radius * 0.5, min(radius * 1.45, r))

    mr = int(radius * 1.5) + 2
    for dy in range(-mr, mr + 1):
        for dx in range(-mr, mr + 1):
            x, y = cx + dx, cy + dy
            if not b.in_bounds(x, y) or b.reserved[y][x]:
                continue                                            # preserve buildings + flow INTO existing water
            dist = max(0.1, (dx * dx + dy * dy) ** 0.5)
            local = rad(math.atan2(dy, dx))
            if dist <= local * 0.6:
                b.set_ground(x, y, "water_deep", surface="water"); b.reserve(x, y, surface="water")
            elif dist <= local:
                b.set_ground(x, y, "water_shallow", surface="water"); b.reserve(x, y, surface="water")
            elif dist <= local + 2.2 and b.is_free(x, y) and b.surface[y][x] == "grass" and rng.random() < 0.72:
                b.set_ground(x, y, shore)                            # beach ring with gaps
    placed = 0
    for _ in range(reeds * 5):
        a = rng.random() * 2 * math.pi
        d = rad(a) + rng.uniform(0.4, 2.4)
        x, y = int(round(cx + d * math.cos(a))), int(round(cy + d * math.sin(a)))
        if b.in_bounds(x, y) and b.is_free(x, y) and b.surface[y][x] != "water" and rng.random() < 0.6:
            if b.place_occupant("reeds", x, y):
                placed += 1
                if placed >= reeds:
                    break
    return placed


def rock_patch(b, cx, cy, radius, *, ground="stone_floor", seed=0, ore_chance=0.28):
    """A rocky OUTCROP / quarry that introduces MINING: bare rocky ground (stone/dirt) replaces the
    grass, with a DENSE CORE of mineable stone blocks thinning to a ragged edge, salted with ore
    deposits (coal/copper/iron/tin) and the odd crystal/geode. Everything is grid-aligned + spaced
    (pickaxe targets). Skips reserved/path/water. Returns the placed block cells."""
    rng = random.Random(seed)
    placed = set()

    def spaced(x, y):
        return all((x + dx, y + dy) not in placed for dx in (-1, 0, 1) for dy in (-1, 0, 1))

    cells = []
    for y in range(cy - radius - 2, cy + radius + 3):
        for x in range(cx - radius - 2, cx + radius + 3):
            if not b.in_bounds(x, y):
                continue
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / (radius + 0.5)
            if d <= 1.0 + rng.uniform(-0.25, 0.15):
                cells.append((x, y, d))
    for (x, y, d) in cells:                                          # bare rocky ground (stony core, dirt rim)
        if b.is_free(x, y) and b.surface[y][x] == "grass":
            b.set_ground(x, y, ground if d < 0.7 else "dirt")
    rng.shuffle(cells)
    ores = ["ore_coal_block", "ore_coal_block", "ore_copper_block", "ore_iron_block", "ore_tin_block"]
    gems = ["crystal_small", "geode", "ore_pile"]
    for (x, y, d) in cells:
        if not b.is_free(x, y) or b.surface[y][x] in ("water", "path"):
            continue                                                # never drop rocks on roads/paths
        if rng.random() < 0.78 * (1.12 - d) and spaced(x, y):       # dense core -> sparse edge
            r = rng.random()
            oid = (rng.choice(gems) if r < ore_chance * 0.35
                   else rng.choice(ores) if r < ore_chance
                   else rng.choice(["stone_block", "stone_block", "hard_stone_block"]))
            b.place_occupant(oid, x, y)
            placed.add((x, y))
    return placed
