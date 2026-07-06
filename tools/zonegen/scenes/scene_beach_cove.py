#!/usr/bin/env python3
"""Scene — BEACH COVE (the Bee Meadow's west sea boundary): a deep-water sea strip whose edge
wanders by noise, a SAND band, cove BITES arcing into the beach, one tiny offshore ISLAND (an
unreachable tease), and the beach set — driftwood, seashell piles, a sandcastle someone left,
a beached boat, reeds in the cove shallows.

`sea_edge(b, ...)` is the reusable carver the ZONE imports (the place_boat_store pattern):
it lays the west sea + sand band + coves + island on ANY builder, driven by that builder's H.
Renders to tools/_generated/previews/zones/bee_meadow_20/scenes/beach_cove.png.
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder              # noqa: E402


def _water(b, x, y, deep=True):
    b.set_ground(x, y, "water_deep" if deep else "water_shallow", surface="water")
    b.reserve(x, y, surface="water")


def sea_edge(b, *, water_w=10, sand_w=6, coves=((0.30, 9), (0.62, 7), (0.85, 11)), island=(0.47, 4),
             seed=7, headlands=True):
    """Carve the WEST edge of `b` into a sea: a deep strip (width `water_w` ± noise per row, shallow
    lip on its east edge), a SAND band, cove BITES (fraction-of-H center, extra-reach pairs) where the
    water arcs further inland, and one offshore sand ISLAND. Between coves the coast does what real
    coasts do (coasts research §1: material follows convexity): the sand PINCHES thin on the convex
    stretch and ROCK stands on it — sandstone headlands. Returns the per-row beach x (the first
    grass column) so callers keep buildings east of it."""
    rng = random.Random(seed)
    H, W = b.H, b.W
    # Low-frequency wobble of the waterline (never a straight rule).
    phase, phase2 = rng.uniform(0, 6.28), rng.uniform(0, 6.28)
    beach_x = [0] * H
    cove_ys = sorted(int(frac * H) for frac, _ in coves)
    head_ys = [(a + c) // 2 for a, c in zip(cove_ys, cove_ys[1:])] if headlands else []
    for y in range(H):
        wob = 2.0 * math.sin(y / 17.0 + phase) + 1.2 * math.sin(y / 7.0 + phase2)
        ww = max(4, int(water_w + wob))
        # Cove bites: water pushes further east in a smooth arc around each cove center.
        for frac, reach in coves:
            cy = int(frac * H)
            half = max(6, reach)  # vertical half-extent of the bite
            d = abs(y - cy)
            if d < half:
                ww += int(reach * math.cos(d / half * math.pi / 2))
        sw = max(3, int(sand_w + 1.5 * math.sin(y / 11.0 + phase2)))
        for hy in head_ys:                       # the convex point: sand pinches to a lip
            if abs(y - hy) < 4:
                sw = max(2, sw - 2)
        # The deep/shallow boundary gets its own per-row drift (cold-grade: a ruled
        # vertical color line ran the length of a cove) — shoals, not a lane divider.
        deep_lim = ww - 2 - (1 if rng.random() < 0.4 else 0) - (1 if rng.random() < 0.15 else 0)
        for x in range(0, min(ww, W)):
            _water(b, x, y, deep=x < deep_lim)
        for x in range(ww, min(ww + sw, W)):
            b.set_ground(x, y, "sand")
        beach_x[y] = ww + sw
    # Headland ROCK: sandstone formations shouldering the waterline on each convex
    # stretch (2x2 — quad-checked), one or two per point, never in a cove's crescent.
    for hy in head_ys:
        put = 0
        for dy in (0, -2, 2, -3, 3):
            y = hy + dy
            if not (0 <= y < H - 1) or put >= 2:
                continue
            x = beach_x[y] - min(3, sand_w)      # near the waterline, on sand
            if all(b.in_bounds(x + qx, y + qy) and b.ground[y + qy][x + qx] == "sand"
                   and b.is_free(x + qx, y + qy) for qx in (0, 1) for qy in (0, 1)):
                b.place_occupant("sandstone_formation", x, y)
                put += 1
    # The island: TWO offset sand blobs (organic union, not a rasterized circle),
    # a lone palm, and the driftwood that snags on any obstruction (coasts §5).
    if island:
        frac, r = island
        icx, icy = max(3, water_w // 2 - 1), int(frac * H)
        blobs = [(icx, icy, r), (icx + rng.choice((-1, 1)) * max(2, r - 2),
                                 icy + rng.choice((-2, 2)), max(2.0, r * 0.62))]
        for y in range(icy - r - 3, icy + r + 4):
            for x in range(max(0, icx - r - 3), icx + r + 4):
                if not b.in_bounds(x, y):
                    continue
                d = min(math.hypot(x - bx, y - by) / br for bx, by, br in blobs)
                if d <= 0.78:
                    b.set_ground(x, y, "sand")
                    b.reserved[y][x] = False
                    b.surface[y][x] = "grass"  # islands hold decor (driftwood), not spawns
                elif d <= 1.0 and b.surface[y][x] == "water":
                    b.set_ground(x, y, "water_shallow", surface="water")
        # A windswept DEAD tree, not a palm (cold-grade: a palm on a temperate flower
        # coast reads as an asset-pack drop) — the lone snag a storm left standing.
        if b.is_free(icx + 1, icy - 1):
            b.place_occupant("tree_dead", icx + 1, icy - 1)
        b.place_occupant("driftwood", icx - 1, icy + 1)
    return beach_x


def _sand_run(b, y, bx):
    """The sand cells of row y walking west from the grass edge bx: returns (water_side_x, cells)."""
    cells = []
    x = bx - 1
    while x >= 0 and b.ground[y][x] == "sand":
        cells.append(x)
        x -= 1
    return (cells[-1] if cells else None), cells


def dress_beach(b, beach_x, *, seed=8, density=0.05):
    """The beach dressing, with STRUCTURE instead of even spray:
    - a WRACK LINE — flotsam (shells, driftwood, starfish, the odd bottle) concentrated in the
      2-3 sand cells nearest the water, the way tides actually leave it; only stray pieces above;
    - DUNE GRASS — tall-grass/dandelion clumps breaking the hard sand→grass boundary;
    - reeds in the cove shallows; exactly one guaranteed sandcastle up on the dry sand."""
    rng = random.Random(seed)
    H = b.H
    placed_castle = False
    for y in range(2, H - 2):
        bx = beach_x[y]
        wx, sand = _sand_run(b, y, bx)
        if wx is None:
            continue
        # The wrack line: the last 2 sand cells before water, denser + varied.
        for x in [c for c in sand if c <= wx + 1]:
            if not b.is_free(x, y):
                continue
            r = rng.random()
            if r < density * 2.3:
                pick = rng.choice(["seashell_pile", "driftwood", "starfish",
                                   "seashell_pile", "starfish"])
                if pick == "driftwood" and not (b.in_bounds(x + 1, y) and b.is_free(x + 1, y)):
                    pick = "seashell_pile"  # driftwood is 2 wide — don't shove it into water
                b.place_occupant(pick, x, y)
            elif r < density * 2.45:
                b.place_occupant("message_bottle", x, y)
        # Dry sand above: only the occasional piece (and the one sandcastle).
        for x in [c for c in sand if c > wx + 2]:
            if not b.is_free(x, y):
                continue
            r = rng.random()
            if r < density * 0.35:
                b.place_occupant(rng.choice(["driftwood", "seashell_pile"]), x, y)
            elif not placed_castle and r < density * 0.5 and 0.3 * H < y < 0.7 * H:
                b.place_occupant("sandcastle", x, y)
                placed_castle = True
        # The DUNE BELT: a real 2-3-cell deep band at the seam — dense marram-style
        # grass with sand HUMMOCKS blowing through into the meadow (no hard sand→grass
        # rule anywhere), a dead bush where the salt wind bites.
        if rng.random() < 0.55:
            for x in (bx, bx + 1, bx + 2):
                if b.in_bounds(x, y) and b.surface[y][x] == "grass" and b.is_free(x, y) \
                   and rng.random() < (0.7 if x <= bx + 1 else 0.35):
                    b.place_occupant(rng.choice(["tall_grass", "tall_grass", "tall_grass",
                                                 "dandelion", "dead_bush"]), x, y)
        if rng.random() < 0.22:                     # wind-blown sand pockets in the grass
            hx = bx + rng.randint(1, 3)
            for dx in range(rng.randint(1, 2)):
                if b.in_bounds(hx + dx, y) and b.surface[y][hx + dx] == "grass" \
                   and b.ground[y][hx + dx] == "grass":
                    b.set_ground(hx + dx, y, "sand")
    if not placed_castle:
        for y in range(H // 2, H - 2):
            x = beach_x[y] - 3
            if b.in_bounds(x, y) and b.ground[y][x] == "sand" and b.is_free(x, y):
                b.place_occupant("sandcastle", x, y)
                break
    # Reeds at the waterline near each cove mouth.
    for y in range(0, H, 5):
        bx = beach_x[y]
        wx = bx - (bx and 1)
        for x in range(max(0, wx - 9), wx - 2):
            if b.in_bounds(x, y) and b.surface[y][x] == "water" and b.ground[y][x] == "water_shallow" \
               and rng.random() < 0.18:
                b.reserved[y][x] = False
                b.place_occupant("reeds", x, y, surface="water")
                b.reserve(x, y, surface="water")


def _float_put(b, oid, x, y):
    """Stand a prop in open water (buoys): un-reserve its cell, place, re-reserve."""
    if not b.in_bounds(x, y) or b.surface[y][x] != "water":
        return False
    b.reserved[y][x] = False
    ok = b.place_occupant(oid, x, y, surface="water")
    b.reserve(x, y, surface="water")
    return ok


def place_beach_landmarks(b, beach_x, *, wreck_y=None, picnic_y=None, buoy_ys=(), bottle_island=None,
                          pool_y=None):
    """The coast's named little features (deterministic, never dice):
    - the SHIPWRECK — not just a hull but a DEBRIS FIELD: spilled cargo (crates, a barrel)
      and driftwood strewn down-tide of it, half its story in what scattered;
    - a PICNIC spot up on the dry sand (picnic_y): parasol + bench + shell pile, and the
      evening half — a campfire ring with a log seat a few steps off;
    - striped BUOYS floating off the cove mouths (buoy_ys);
    - a message bottle on the tease ISLAND (bottle_island=(x,y)) — visible loot you can't reach;
    - a TIDE POOL (pool_y): still shallow water cupped in dry sand, life crowded on its rim."""
    if wreck_y is not None:
        wx, sand = _sand_run(b, wreck_y, beach_x[wreck_y])
        if wx is not None:
            for x in range(wx, wx + 4):
                if b.is_free(x, wreck_y) and b.is_free(x + 1, wreck_y):
                    b.place_occupant("shipwreck_hull", x, wreck_y)
                    # THE ROCK SHE STRUCK — a sandstone head at the hull's waterline
                    # shoulder (the sprite alone reads as a rowboat; the rock plus the
                    # timber field make it a WRECK). 2x2 on sand, quad-checked; water-
                    # side cells are reserved sea, so the reef sits half-buried at the
                    # tideline instead (verified in data: the sea-side variants never fit).
                    for rdx, rdy in [(-2, -2), (2, -2), (-1, -3), (3, 2)]:
                        rx_, ry_ = x + rdx, wreck_y + rdy
                        if all(b.in_bounds(rx_ + qx, ry_ + qy)
                               and b.ground[ry_ + qy][rx_ + qx] == "sand"
                               and b.is_free(rx_ + qx, ry_ + qy) for qx in (0, 1) for qy in (0, 1)):
                            b.place_occupant("sandstone_formation", rx_, ry_)
                            break
                    # The cargo spill, strewn DOWN-TIDE (south) of the hull the way the
                    # current would rake it: crates then barrels then broken timbers.
                    for oid, dx, dy in [("crate", -1, 1), ("crate", 1, 2), ("barrel", 3, 1),
                                        ("barrel", -2, 3), ("driftwood", -2, 2), ("driftwood", 2, 3),
                                        ("driftwood", 4, -1), ("driftwood", 0, 4),
                                        ("seashell_pile", 0, 3),
                                        ("starfish", -2, -1), ("starfish", 5, 2)]:
                        tx, ty = x + dx, wreck_y + dy
                        if b.in_bounds(tx, ty) and b.ground[ty][tx] == "sand" and b.is_free(tx, ty):
                            b.place_occupant(oid, tx, ty)
                    break
    if picnic_y is not None:
        bx = beach_x[picnic_y]
        for x in range(bx - 4, bx - 1):
            if b.in_bounds(x, picnic_y) and b.ground[picnic_y][x] == "sand" and b.is_free(x, picnic_y) \
               and b.is_free(x + 1, picnic_y - 1):
                b.place_occupant("beach_umbrella", x, picnic_y)
                b.place_occupant("bench", x + 1, picnic_y - 1)
                if b.is_free(x - 1, picnic_y - 2):
                    b.place_occupant("seashell_pile", x - 1, picnic_y - 2)
                # Somebody's beachcombing haul, lined up by the bench.
                for sx, sy in [(x + 2, picnic_y + 1), (x + 3, picnic_y + 1)]:
                    if b.in_bounds(sx, sy) and b.ground[sy][sx] == "sand" and b.is_free(sx, sy):
                        b.place_occupant("starfish", sx, sy)
                # The evening half: last night's fire ring, a log seat pulled up to it.
                for fx, fy in [(x + 3, picnic_y + 3), (x + 2, picnic_y + 4), (x + 4, picnic_y + 2)]:
                    if b.in_bounds(fx, fy) and b.ground[fy][fx] == "sand" \
                       and b.is_free(fx, fy) and b.is_free(fx + 1, fy):
                        b.place_occupant("campfire", fx, fy)
                        b.place_occupant("log_seat", fx + 1, fy)
                        break
                break
    for by in buoy_ys:
        bx = beach_x[by]
        _float_put(b, "buoy", max(1, bx - 12), by)
    if bottle_island is not None:
        ix, iy = bottle_island
        for dx in range(-2, 3):
            if b.in_bounds(ix + dx, iy) and b.ground[iy][ix + dx] == "sand" and b.is_free(ix + dx, iy):
                b.place_occupant("message_bottle", ix + dx, iy)
                break
    if pool_y is not None:
        # Still water cupped in the sand — sealed from the sea by a full sand ring
        # (coasts §5: mud/still water only where the energy stops). Searches nearby
        # rows/offsets so dressing can't silently starve it out (a promised landmark
        # that isn't in the pixels is a bug, not a shrug).
        placed_pool = False
        for ry in (pool_y, pool_y + 1, pool_y - 1, pool_y + 2, pool_y - 2, pool_y + 3):
            if placed_pool or not (1 <= ry < b.H - 2):
                continue
            wx, sand = _sand_run(b, ry, beach_x[ry])
            if wx is None or len(sand) < 5:
                continue
            for px in (wx + 3, wx + 2, wx + 4):
                cells = [(px, ry), (px + 1, ry), (px, ry + 1)]
                if all(b.in_bounds(cx, cy) and b.ground[cy][cx] == "sand" and b.is_free(cx, cy)
                       for cx, cy in cells):
                    for cx, cy in cells:
                        b.set_ground(cx, cy, "water_shallow", surface="water")
                        b.reserve(cx, cy, surface="water")
                    for oid, ox, oy in [("starfish", px - 1, ry), ("seashell_pile", px + 2, ry + 1),
                                        ("starfish", px + 1, ry - 1)]:
                        if b.in_bounds(ox, oy) and b.ground[oy][ox] == "sand" and b.is_free(ox, oy):
                            b.place_occupant(oid, ox, oy)
                    placed_pool = True
                    break


def backshore(b, beach_x, *, path_y=None, seed=9, depth=None):
    """The LAND half of a beach scene (a beach isn't a strip floating on a void): a worn
    sandy footpath wandering in from the east to the seam, and the meadow's first
    columns textured — the grass gets sparser decor the further from the salt.
    `depth` caps how far inland the scrub reaches (pass ~10 when a ZONE calls this —
    its meadows own the rest; None = dress to the scene's east edge)."""
    rng = random.Random(seed)
    H, W = b.H, b.W
    if path_y is not None:
        x = W - 1
        y = path_y
        while x > beach_x[y] + 1:
            for cell in ((x, y), (x, y + 1)):
                if b.in_bounds(*cell) and b.surface[cell[1]][cell[0]] == "grass" \
                   and b.ground[cell[1]][cell[0]] in ("grass", "sand") and not b.reserved[cell[1]][cell[0]]:
                    b.set_ground(cell[0], cell[1], "sand")     # sand-worn track, not a road
            x -= 1
            if rng.random() < 0.3:
                y += rng.choice((-1, 1))
                y = max(2, min(H - 3, y))
    # Scrub: bushes/flowers thickening near the dune belt, thinning inland — and a
    # sparse meadow floor beyond (no screen of pure void; a zone's own flower
    # meadows take over past `depth`).
    for y in range(1, H - 1):
        row_lim = (beach_x[y] + depth) if depth is not None else (W - 1)
        for x in range(beach_x[y] + 2, min(row_lim, W - 1)):
            if b.surface[y][x] != "grass" or not b.is_free(x, y):
                continue
            fade = 1.0 - (x - beach_x[y]) / 12.0
            p = 0.035 * fade if fade > 0.15 else 0.008
            if rng.random() < p:
                b.place_occupant(rng.choice(["tall_grass", "bush", "dandelion", "tall_grass",
                                             "flower_wild"]), x, y)


PREVIEW = "zones/bee_meadow_20/scenes"
SCALE = 5


def build():
    b = ZoneBuilder("scene_beach_cove", 48, 44, base_tile="grass", name="Beach cove", biome="coast")
    beach = sea_edge(b, water_w=11, sand_w=6, coves=((0.35, 8), (0.75, 10)), island=(0.55, 4), seed=7)
    dress_beach(b, beach, seed=8, density=0.06)
    place_beach_landmarks(b, beach, wreck_y=33, picnic_y=12, buoy_ys=(15, 33),
                          bottle_island=(4, 24), pool_y=17)
    backshore(b, beach, path_y=13, seed=9)
    # A beached (working) boat on the far south stretch — away from the wreck, so the
    # two tell different stories. Boat is 2x3: verify the WHOLE footprint on dry sand
    # (a reserved corner cell silently sank the old placement — builder warning).
    for y0 in (6, 7, 8, 5):
        placed_boat = False
        for x0 in range(beach[y0] - 3, beach[y0] + 2):
            if all(b.in_bounds(x0 + fx, y0 + fy) and b.ground[y0 + fy][x0 + fx] == "sand"
                   and b.is_free(x0 + fx, y0 + fy) and not b.reserved[y0 + fy][x0 + fx]
                   for fx in (0, 1) for fy in (0, 1, 2)):
                b.place_occupant("boat", x0, y0)
                placed_boat = True
                break
        if placed_boat:
            break
    b.spawn = [beach[22] + 4, 22]
    return b


if __name__ == "__main__":
    from scene_preview import render
    b = build()
    print("LINT:", b.lint() or "0 defects", "| missing_art:", b.missing_art())
    render(b, __file__, PREVIEW, SCALE)
