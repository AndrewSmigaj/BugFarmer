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
             seed=7):
    """Carve the WEST edge of `b` into a sea: a deep strip (width `water_w` ± noise per row, shallow
    lip on its east edge), a SAND band, cove BITES (fraction-of-H center, extra-reach pairs) where the
    water arcs further inland, and one offshore sand ISLAND. Returns the per-row beach x (the first
    grass column) so callers keep buildings east of it."""
    rng = random.Random(seed)
    H, W = b.H, b.W
    # Low-frequency wobble of the waterline (never a straight rule).
    phase, phase2 = rng.uniform(0, 6.28), rng.uniform(0, 6.28)
    beach_x = [0] * H
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
        for x in range(0, min(ww, W)):
            _water(b, x, y, deep=x < ww - 2)
        for x in range(ww, min(ww + sw, W)):
            b.set_ground(x, y, "sand")
        beach_x[y] = ww + sw
    # The island: a small sand blob offshore in open water (unreachable tease).
    if island:
        frac, r = island
        icx, icy = max(3, water_w // 2 - 1), int(frac * H)
        for y in range(icy - r, icy + r + 1):
            for x in range(max(0, icx - r), icx + r + 1):
                if not b.in_bounds(x, y):
                    continue
                d = math.hypot(x - icx, y - icy)
                if d <= r - 1.2:
                    b.set_ground(x, y, "sand")
                    b.reserved[y][x] = False
                    b.surface[y][x] = "grass"  # islands hold decor (driftwood), not spawns
                elif d <= r:
                    b.set_ground(x, y, "water_shallow", surface="water")
        b.place_occupant("driftwood", icx - 1, icy)
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
        # Dune grass: clumps at the sand→grass seam.
        if rng.random() < 0.30:
            for x in (bx, bx + 1):
                if b.in_bounds(x, y) and b.surface[y][x] == "grass" and b.is_free(x, y) \
                   and rng.random() < 0.7:
                    b.place_occupant(rng.choice(["tall_grass", "tall_grass", "dandelion"]), x, y)
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


def place_beach_landmarks(b, beach_x, *, wreck_y=None, picnic_y=None, buoy_ys=(), bottle_island=None):
    """The coast's named little features (deterministic, never dice):
    - a SHIPWRECK HULL half-buried at the waterline (wreck_y) with strewn driftwood;
    - a PICNIC spot up on the dry sand (picnic_y): parasol + bench + a shell pile;
    - striped BUOYS floating off the cove mouths (buoy_ys);
    - a message bottle on the tease ISLAND (bottle_island=(x,y)) — visible loot you can't reach."""
    if wreck_y is not None:
        wx, sand = _sand_run(b, wreck_y, beach_x[wreck_y])
        if wx is not None:
            for x in range(wx, wx + 4):
                if b.is_free(x, wreck_y) and b.is_free(x + 1, wreck_y):
                    b.place_occupant("shipwreck_hull", x, wreck_y)
                    for dx, dy in [(-2, 1), (3, -1), (1, 2)]:
                        if b.in_bounds(x + dx, wreck_y + dy) and \
                           b.ground[wreck_y + dy][x + dx] == "sand" and b.is_free(x + dx, wreck_y + dy):
                            b.place_occupant("driftwood", x + dx, wreck_y + dy)
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


PREVIEW = "zones/bee_meadow_20/scenes"
SCALE = 5


def build():
    b = ZoneBuilder("scene_beach_cove", 48, 44, base_tile="grass", name="Beach cove", biome="coast")
    beach = sea_edge(b, water_w=11, sand_w=6, coves=((0.35, 8), (0.75, 10)), island=(0.55, 4), seed=7)
    dress_beach(b, beach, seed=8, density=0.06)
    place_beach_landmarks(b, beach, wreck_y=33, picnic_y=12, buoy_ys=(15, 33),
                          bottle_island=(4, 24))
    # A beached (working) boat on the far south stretch — away from the wreck, so the two
    # tell different stories.
    for x, y in [(beach[6] - 3, 6)]:
        if b.is_free(x, y):
            b.place_occupant("boat", x, y)
    b.spawn = [beach[22] + 4, 22]
    return b


if __name__ == "__main__":
    from scene_preview import render
    b = build()
    print("LINT:", b.lint() or "0 defects", "| missing_art:", b.missing_art())
    render(b, __file__, PREVIEW, SCALE)
