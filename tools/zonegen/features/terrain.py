#!/usr/bin/env python3
"""Ground/terrain primitives shared across scenes: paths and an organic pond.
All coordinate through the builder's ground grid + surface mask (paths -> surface 'path',
water -> reserved 'water'), so roads route around water and scatter avoids both."""
import math
import random


# Road material -> its diagonal-transition tile family (made by
# tools/make_diagonal_tiles.py; ids carry "path" so load() classifies them).
_DIAG_FAMILY = {"stone_path": "stone_path_d", "dirt": "dirt_path_d"}


def smooth_paths(b):
    """The road-angle pass (run AFTER all roads, BEFORE buildings): every stair-step
    corner a wobbling `path()` leaves — a grass cell whose N/S and E/W neighbors are
    both road of one material — gets the matching 45° diagonal-transition tile
    (road_d_<corner>, road triangle pointing into the corner the road wraps), so
    curves render as bevelled edges instead of hard right angles.

    Fill-concave only: it only ever ADDS road surface, never narrows one. The cell
    becomes surface='path' (scatter then avoids it). Only plain-grass cells qualify
    (the diagonal art is grass-backed — shores/floors are left alone), and mixed-
    material corners (stone meets dirt) are skipped. Returns the filled cells."""
    filled = []
    todo = []
    for y in range(b.H):
        for x in range(b.W):
            if b.surface[y][x] != "grass" or b.reserved[y][x] or (x, y) in b.occ:
                continue
            if b.ground[y][x] != "grass":
                continue

            def road_mat(nx, ny):
                if not b.in_bounds(nx, ny) or b.surface[ny][nx] != "path":
                    return None
                return _DIAG_FAMILY.get(b.ground[ny][nx])

            north = road_mat(x, y + 1)   # +y is NORTH (game orientation)
            south = road_mat(x, y - 1)
            east = road_mat(x + 1, y)
            west = road_mat(x - 1, y)

            # exactly one vertical + one horizontal road neighbor, same material
            vs = [(m, c) for m, c in ((north, "n"), (south, "s")) if m]
            hs = [(m, c) for m, c in ((east, "e"), (west, "w")) if m]
            if len(vs) != 1 or len(hs) != 1 or vs[0][0] != hs[0][0]:
                continue
            todo.append((x, y, f"{vs[0][0]}_{vs[0][1]}{hs[0][1]}"))

    # apply after the scan so fills don't cascade off each other within one pass
    for (x, y, tile) in todo:
        b.set_ground(x, y, tile, surface="path")
        filled.append((x, y))

    # POTHOLE HEAL: edge_tile fraying on a WOBBLING centerline leaves dirt specks
    # that end up interior once the line moves on — exactly what the checkered-road
    # lint flags. A dirt path cell with ≥3 orthogonal stone-road path neighbors is
    # inside the road, not on its shoulder: repave it.
    heal = []
    for y in range(b.H):
        for x in range(b.W):
            if b.surface[y][x] != "path" or b.ground[y][x] != "dirt":
                continue
            stony = sum(1 for (nx, ny) in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
                        if b.in_bounds(nx, ny) and b.surface[ny][nx] == "path"
                        and b.ground[ny][nx].startswith("stone_path"))
            if stony >= 3:
                heal.append((x, y))
    for (x, y) in heal:
        b.set_ground(x, y, "stone_path", surface="path")
    return filled


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
    """A natural LAKE shaped like one: the UNION of 2-4 elongated, offset blobs strung
    along a random long axis — a real lake's read (a long body with bays and a bowed
    shoreline), never the symmetric harmonic STAR the old version produced (high-freq
    radius bumps made 5-7 evenly spaced points). Each blob is a mild ellipse with its
    own tilt; two low-frequency, low-amplitude harmonics roughen the union's edge just
    enough to kill any geometry read. Deep core -> shallow rim -> a `shore` beach ring
    with gaps -> reeds clumped on the banks. Reserves the water; flows INTO existing
    water (skips reserved). Returns {"center", "radius", "reeds"} — feed it to
    `shore_dress()` for per-arc treatments."""
    rng = random.Random(seed)
    axis = rng.random() * 2 * math.pi
    nblobs = rng.randint(2, 4)
    blobs = []
    for i in range(nblobs):
        t = (i / max(1, nblobs - 1) - 0.5) * 1.15        # spread along the long axis
        bx = cx + math.cos(axis) * radius * t * 0.85 + rng.uniform(-0.18, 0.18) * radius
        by = cy + math.sin(axis) * radius * t * 0.85 + rng.uniform(-0.18, 0.18) * radius
        br = radius * rng.uniform(0.45, 0.68)
        ecc = rng.uniform(0.65, 0.95)                    # mild per-blob ellipse
        ang = axis + rng.uniform(-0.6, 0.6)
        blobs.append((bx, by, br, ecc, ang))
    ph1, ph2 = rng.random() * 2 * math.pi, rng.random() * 2 * math.pi

    def signed(x, y):
        """>0 inside the union; ~0 at the shoreline (max blob field, noisy edge)."""
        best = -9.0
        for (bx, by, br, ecc, ang) in blobs:
            dx, dy = x - bx, y - by
            ca, sa = math.cos(-ang), math.sin(-ang)
            u = dx * ca - dy * sa
            v = (dx * sa + dy * ca) / ecc
            a = math.atan2(dy, dx)
            rr = br * (1 + 0.07 * math.sin(2 * a + ph1) + 0.05 * math.sin(3 * a + ph2))
            best = max(best, 1.0 - math.hypot(u, v) / rr)
        return best

    mr = int(radius * 1.6) + 3
    for dy in range(-mr, mr + 1):
        for dx in range(-mr, mr + 1):
            x, y = cx + dx, cy + dy
            if not b.in_bounds(x, y) or b.reserved[y][x]:
                continue                                  # preserve buildings + merge with existing water
            s = signed(x, y)
            if s > 0.40:
                b.set_ground(x, y, "water_deep", surface="water"); b.reserve(x, y, surface="water")
            elif s > 0.0:
                b.set_ground(x, y, "water_shallow", surface="water"); b.reserve(x, y, surface="water")
            elif s > -0.14 and b.is_free(x, y) and b.surface[y][x] == "grass" and rng.random() < 0.72:
                b.set_ground(x, y, shore)                 # beach ring with gaps
    # Reeds: shape-agnostic — random dry cells touching the water.
    placed = 0
    for _ in range(reeds * 12):
        if placed >= reeds:
            break
        x = cx + rng.randint(-mr, mr)
        y = cy + rng.randint(-mr, mr)
        if not b.in_bounds(x, y) or not b.is_free(x, y) or b.surface[y][x] == "water":
            continue
        touches = any(b.in_bounds(x + ax, y + ay) and b.surface[y + ay][x + ax] == "water"
                      for ax in (-1, 0, 1) for ay in (-1, 0, 1))
        if touches and rng.random() < 0.6 and b.place_occupant("reeds", x, y):
            placed += 1
    return {"center": (cx, cy), "radius": radius, "reeds": placed}


def shore_dress(b, info, arcs, *, seed=0):
    """Per-arc shoreline treatments — the trees-and-ponds rule ("split the shoreline
    into arcs, no two banks identical") as a primitive. `info` is the dict `lake()`
    returns, or a plain (cx, cy, radius) tuple. `arcs` is [(a0_deg, a1_deg,
    treatment), ...] with treatment in {"sand", "mud", "reeds", "forest", "rocks"}.

    ANGLES (read this twice): the builder's +y is NORTH, and angles are standard
    math atan2(dy, dx) — so 0° = the EAST shore, 90° = the NORTH shore, 180° = WEST,
    270° = SOUTH. An arc may wrap (e.g. (300, 60, "sand") spans east through north).

    The shoreline is RE-DERIVED by adjacency scan (dry, unreserved cells 8-adjacent
    to water), NOT taken from the lake call — lakes merge into existing water by
    design, so only the scan sees the composite bank. Treatments: sand/mud retile
    the ring (+ a sparse outer fringe); reeds plant clumped reeds/cattail; forest
    pulls trees + bushes down to the bank; rocks scatter small mineable
    stone_block clusters. Returns the dressed cells."""
    if isinstance(info, dict):
        (cx, cy), radius = info["center"], info["radius"]
    else:
        cx, cy, radius = info
    rng = random.Random(seed)

    def in_arc(angle_deg, a0, a1):
        a = angle_deg % 360
        a0, a1 = a0 % 360, a1 % 360
        return (a0 <= a <= a1) if a0 <= a1 else (a >= a0 or a <= a1)

    # the composite shoreline by adjacency scan
    mr = int(radius * 1.7) + 3
    shore = []  # (x, y, angle_deg)
    for dy in range(-mr, mr + 1):
        for dx in range(-mr, mr + 1):
            x, y = cx + dx, cy + dy
            if not b.in_bounds(x, y) or b.surface[y][x] == "water" or b.reserved[y][x]:
                continue
            touches = any(
                b.in_bounds(x + ax, y + ay) and b.surface[y + ay][x + ax] == "water"
                for ay in (-1, 0, 1) for ax in (-1, 0, 1) if (ax, ay) != (0, 0))
            if touches:
                shore.append((x, y, math.degrees(math.atan2(dy, dx))))

    dressed = []
    for (x, y, ang) in shore:
        treatment = next((t for (a0, a1, t) in arcs if in_arc(ang, a0, a1)), None)
        if treatment is None:
            continue
        if treatment in ("sand", "mud"):
            b.set_ground(x, y, treatment)
            # sparse outer fringe so the ring isn't a hard band
            ox, oy = x + (1 if math.cos(math.radians(ang)) > 0.3 else -1 if math.cos(math.radians(ang)) < -0.3 else 0), \
                     y + (1 if math.sin(math.radians(ang)) > 0.3 else -1 if math.sin(math.radians(ang)) < -0.3 else 0)
            if b.in_bounds(ox, oy) and b.surface[oy][ox] == "grass" and rng.random() < 0.45:
                b.set_ground(ox, oy, treatment)
        elif treatment == "reeds":
            # streaks, not singles: run-length clumping along the scan order
            if rng.random() < 0.5 and b.is_free(x, y):
                b.place_occupant(rng.choice(["reeds", "reeds", "cattail"]), x, y)
        elif treatment == "forest":
            # trees pulled down to the bank (spaced), bushes filling between
            if rng.random() < 0.35 and b.is_free(x, y):
                near_tree = any(c["id"].startswith("tree") for (px, py), c in b.occ.items()
                                if abs(px - x) <= 2 and abs(py - y) <= 2 and c.get("anchor"))
                if not near_tree:
                    b.place_occupant(rng.choice(["tree_oak", "tree_pine"]), x, y, surface="forest")
                elif rng.random() < 0.5:
                    b.place_occupant("bush", x, y, surface="forest")
        elif treatment == "rocks":
            if rng.random() < 0.25 and b.is_free(x, y):
                b.place_occupant("stone_block", x, y)
        dressed.append((x, y))
    return dressed


def rock_mass(b, cx, cy, rx, ry, *, seed=0, veins=4):
    """A SOLID rock mass — the surface sneak-peek of the mining underworld. Unlike
    `rock_patch` (a sparse quarry floor you walk through), this is FILLED: every
    interior cell carries a mineable block (stone, hard stone toward the core — the
    insides go dark later), salted with short ORE VEINS (runs of 3-5, the caves.md
    rule: veins, not specks). The shape is the same multi-blob union as `lake()`, so
    masses read as rocky hills, not circles. Edges get a ragged dirt apron with
    spilled blocks. Returns the filled cells."""
    rng = random.Random(seed)
    axis = rng.random() * 2 * math.pi
    nblobs = rng.randint(2, 3)
    blobs = []
    for i in range(nblobs):
        t = (i / max(1, nblobs - 1) - 0.5)
        bx = cx + math.cos(axis) * rx * t * 0.8 + rng.uniform(-0.15, 0.15) * rx
        by = cy + math.sin(axis) * ry * t * 0.8 + rng.uniform(-0.15, 0.15) * ry
        blobs.append((bx, by, rx * rng.uniform(0.5, 0.75), ry * rng.uniform(0.5, 0.75)))
    ph = rng.random() * 2 * math.pi

    def signed(x, y):
        best = -9.0
        for (bx, by, brx, bry) in blobs:
            dx, dy = (x - bx) / max(1.0, brx), (y - by) / max(1.0, bry)
            a = math.atan2(y - by, x - bx)
            n = 1 + 0.08 * math.sin(3 * a + ph)
            best = max(best, 1.0 - math.hypot(dx, dy) / n)
        return best

    filled = []
    mr = int(max(rx, ry) * 1.4) + 2
    for dy in range(-mr, mr + 1):
        for dx in range(-mr, mr + 1):
            x, y = cx + dx, cy + dy
            if not b.in_bounds(x, y):
                continue
            s = signed(x, y)
            if s > 0 and b.is_free(x, y) and b.surface[y][x] == "grass":
                b.set_ground(x, y, "stone_floor")
                block = "hard_stone_block" if (s > 0.45 and rng.random() < 0.6) else "stone_block"
                if b.place_occupant(block, x, y):
                    filled.append((x, y))
            elif -0.12 < s <= 0 and b.is_free(x, y) and b.surface[y][x] == "grass":
                if rng.random() < 0.5:
                    b.set_ground(x, y, "dirt")            # the ragged apron
                if rng.random() < 0.12:
                    b.place_occupant("stone_block", x, y)  # spilled blocks

    # Ore veins: short random-walk runs through the filled mass.
    ores = ["ore_copper_block", "ore_coal_block", "ore_copper_block", "ore_iron_block"]
    for v in range(veins):
        if not filled:
            break
        x, y = filled[rng.randrange(len(filled))]
        ore = ores[v % len(ores)]
        for _ in range(rng.randint(3, 5)):
            cell = b.occ.get((x, y))
            if cell and cell["id"] in ("stone_block", "hard_stone_block"):
                cell["id"] = ore                          # swap the block in place
            x += rng.choice((-1, 0, 1))
            y += rng.choice((-1, 0, 1))
            if not b.in_bounds(x, y):
                break
    return filled


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
