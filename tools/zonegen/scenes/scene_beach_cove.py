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


def dress_beach(b, beach_x, *, seed=8, density=0.04):
    """Scatter the beach set along the sand band: driftwood, seashell piles, one sandcastle,
    clumps of reeds at the cove waterlines."""
    rng = random.Random(seed)
    H = b.H
    placed_castle = False
    for y in range(2, H - 2, 3):
        bx = beach_x[y]
        for x in range(max(2, bx - 7), bx):
            if b.ground[y][x] != "sand" or not b.is_free(x, y):
                continue
            r = rng.random()
            if r < density:
                b.place_occupant("seashell_pile", x, y)
            elif r < density * 1.7:
                b.place_occupant("driftwood", x, y)
            elif not placed_castle and r < density * 1.9 and 0.3 * H < y < 0.7 * H:
                b.place_occupant("sandcastle", x, y)
                placed_castle = True
    # The sandcastle is a landmark, not a dice roll — guarantee exactly one, mid-beach.
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


PREVIEW = "zones/bee_meadow_20/scenes"
SCALE = 5


def build():
    b = ZoneBuilder("scene_beach_cove", 48, 44, base_tile="grass", name="Beach cove", biome="coast")
    beach = sea_edge(b, water_w=11, sand_w=6, coves=((0.35, 8), (0.75, 10)), island=(0.55, 4), seed=7)
    dress_beach(b, beach, seed=8, density=0.06)
    # A beached old boat above the south cove — somebody's given up on it.
    for x, y in [(beach[30] - 3, 30)]:
        if b.is_free(x, y):
            b.place_occupant("boat", x, y)
    b.spawn = [beach[22] + 4, 22]
    return b


if __name__ == "__main__":
    from scene_preview import render
    b = build()
    print("LINT:", b.lint() or "0 defects", "| missing_art:", b.missing_art())
    render(b, __file__, PREVIEW, SCALE)
