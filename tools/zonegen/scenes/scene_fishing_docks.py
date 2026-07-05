#!/usr/bin/env python3
"""Scene — FISHING HAMLET (the Bee Meadow's SW cove): two full-home cottages drowsing above the
water, a plank DOCK running south over the cove with mooring posts, a lantern and moored boats,
and working-shore clutter — fish crates in a row, barrels, drying nets' worth of driftwood and
reeds. No NPC yet: fishing is a future slice (the village fisherman already says so).

`place_fishing_hamlet(b, ox, oy)` is the composable piece (the place_boat_store pattern): cottages
on the grass at/above oy, the dock walking SOUTH (y decreasing) from oy into whatever water the
caller laid. Renders to tools/_generated/previews/zones/bee_meadow_20/scenes/fishing_docks.png.
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder              # noqa: E402
from features.terrain import lake, path          # noqa: E402
from scene_cottage import place_cottage          # noqa: E402


def _water_put(b, oid, x, y, **k):
    """Stand an object in the water (un-reserve its footprint first) — the dock-furniture idiom."""
    fw, fh = b.footprint(oid)
    if not all(b.in_bounds(x + dx, y + dy) for dx in range(fw) for dy in range(fh)):
        return False
    for dx in range(fw):
        for dy in range(fh):
            b.reserved[y + dy][x + dx] = False
    return b.place_occupant(oid, x, y, surface="water", **k)


def _dock(b, x0, oy, max_len=14):
    """A 2-wide plank dock from oy walking SOUTH (y decreasing). Decks EVERY cell down to the
    last water cell — land cells become a BOARDWALK ramp, so the pier always connects visually
    to the shore instead of floating detached when the waterline wanders. Refuses to build at
    all if there's no water within max_len (returns None). Mooring posts every 3, a lantern
    midway, a boat moored at the far end."""
    water_ys = [y for y in range(oy, oy - max_len, -1)
                if b.in_bounds(x0, y) and (b.surface[y][x0] == "water" or
                                           b.surface[y][x0 + 1] == "water")]
    if not water_ys:
        return None
    end = min(water_ys)
    for y in range(oy, end - 1, -1):
        for x in (x0, x0 + 1):
            if not b.in_bounds(x, y):
                continue
            if b.surface[y][x] == "water" or b.is_free(x, y):
                b.set_ground(x, y, "bridge_wood", surface="path")
                b.reserved[y][x] = False
    for y in range(oy - 2, end + 1, -3):
        _water_put(b, "mooring_post", x0 - 1, y)
        _water_put(b, "mooring_post", x0 + 2, y)
    _water_put(b, "lantern", x0 + 2, (oy + end) // 2)
    _water_put(b, "boat", x0 - 1, end)
    return end


def place_fishing_hamlet(b, ox, oy):
    """The hamlet piece (SW anchor ox,oy — oy is the shoreline row): two cottages NORTH of the
    shore (staggered, different yards), a working dock at ox+18 + a stub dock at ox+8 (both
    boardwalk-ramped to the shore), and a WORKING SHORE between the cottages and the water —
    the catch drying/crated in rows, nets and pots by the dock heads, the lived-in bits
    (laundry line, a shared fire) behind."""
    # PRECEDENCE: the door→shore paths go down FIRST (roads before buildings — the door
    # positions are deterministic: cottage door at its ox+10), starting BELOW the future
    # yards so they meet the yard gates rather than threading the buildings.
    path(b, (ox + 11, oy + 4), (ox + 19, oy + 1), width=1, tile="dirt", wobble=0.05, seed=ox + 1)
    path(b, (ox + 33, oy + 8), (ox + 27, oy + 4), width=1, tile="dirt", wobble=0.08, seed=ox + 2)

    place_cottage(b, ox, oy + 8, npc="fisher_down", yard_style="small_plot")
    place_cottage(b, ox + 24, oy + 11, npc="farmer_down", yard_style="unfenced")

    _dock(b, ox + 18, oy, max_len=12)
    _dock(b, ox + 8, oy + 1, max_len=6)

    # THE WORKING SHORE (rows rule — this is a workplace, not clutter):
    # the catch: drying racks in a row WEST of the door paths, by the stub dock.
    for i in range(2):
        if b.is_free(ox + 2 + i * 3, oy + 3) and b.is_free(ox + 3 + i * 3, oy + 3):
            b.place_occupant("drying_rack_fish", ox + 2 + i * 3, oy + 3)
    for i in range(3):
        if b.is_free(ox + 14 + i, oy + 1):
            b.place_occupant("fish_crate", ox + 14 + i, oy + 1)
    # Gear by the dock heads: heaped nets + a lobster-pot stack + barrels.
    for x, y in [(ox + 22, oy + 3), (ox + 11, oy + 2)]:
        if b.is_free(x, y):
            b.place_occupant("net_pile", x, y)
    for i in range(3):
        if b.is_free(ox + 23 + i, oy + 2):
            b.place_occupant("lobster_pot", ox + 23 + i, oy + 2)
    for x, y in [(ox + 21, oy + 3), (ox + 27, oy + 2)]:
        if b.is_free(x, y):
            b.place_occupant("barrel", x, y)
    if b.is_free(ox + 15, oy + 5):
        b.place_occupant("lamp_post", ox + 15, oy + 5)
    if b.is_free(ox + 12, oy + 1):
        b.place_occupant("driftwood", ox + 12, oy + 1)
    if b.is_free(ox + 33, oy + 2):
        b.place_occupant("seashell_pile", ox + 33, oy + 2)

    # Lived-in: laundry behind cottage B (open grass — cottage A's fenced yard has no room),
    # a shared fire between the homes.
    for lx in range(ox + 26, ox + 34):
        if b.is_free(lx, oy + 25) and b.is_free(lx + 1, oy + 25):
            b.place_occupant("laundry_line", lx, oy + 25)
            break
    if b.is_free(ox + 20, oy + 12):
        b.place_occupant("campfire", ox + 20, oy + 12)

    # The bay itself: lily pads in the calm shallows + a buoy off the mouth.
    rng = random.Random(oy * 7 + ox)
    placed_pads = 0
    for y in range(oy - 2, oy - 9, -1):
        for x in range(ox + 2, ox + 34, 3):
            if placed_pads >= 5:
                break
            if b.in_bounds(x, y) and b.surface[y][x] == "water" \
               and b.ground[y][x] == "water_shallow" and rng.random() < 0.35:
                b.reserved[y][x] = False
                if b.place_occupant("lily_pad", x, y, surface="water"):
                    placed_pads += 1
                b.reserve(x, y, surface="water")
    for x in range(ox + 2, ox + 30):
        if b.in_bounds(x, oy - 10) and b.surface[oy - 10][x] == "water" \
           and b.ground[oy - 10][x] == "water_deep":
            b.reserved[oy - 10][x] = False
            b.place_occupant("buoy", x, oy - 10, surface="water")
            b.reserve(x, oy - 10, surface="water")
            break
    return oy


PREVIEW = "zones/bee_meadow_20/scenes"
SCALE = 5


def build():
    b = ZoneBuilder("scene_fishing_docks", 52, 46, base_tile="grass", name="Fishing hamlet", biome="coast")
    # The cove: a lake hugging the south edge (the zone supplies the real sea cove). Sized so
    # its top edge sits just SOUTH of the piece's shoreline row — the piece assumes water
    # below oy, like the zone's real bay.
    lake(b, 25, 2, 12, seed=5, shore="sand", reeds=10)
    place_fishing_hamlet(b, 4, 12)
    b.spawn = [24, 20]
    return b


if __name__ == "__main__":
    from scene_preview import render
    b = build()
    print("LINT:", b.lint() or "0 defects", "| missing_art:", b.missing_art())
    render(b, __file__, PREVIEW, SCALE)
