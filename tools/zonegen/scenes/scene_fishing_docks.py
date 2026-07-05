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
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder              # noqa: E402
from features.terrain import lake                # noqa: E402
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
    """A 2-wide plank dock from oy walking SOUTH (y decreasing): bridge_wood over water cells,
    sand/grass cells left alone (butt the dock to the shore). Mooring posts every 3, a lantern
    midway, a boat moored at the far end."""
    end = None
    for y in range(oy, oy - max_len, -1):
        if not b.in_bounds(x0, y):
            break
        for x in (x0, x0 + 1):
            if b.in_bounds(x, y) and b.surface[y][x] == "water":
                b.set_ground(x, y, "bridge_wood", surface="path")
                b.reserved[y][x] = False
                end = y
    if end is not None:
        for y in range(oy - 2, end + 1, -3):
            _water_put(b, "mooring_post", x0 - 1, y)
            _water_put(b, "mooring_post", x0 + 2, y)
        _water_put(b, "lantern", x0 + 2, (oy + end) // 2)
        _water_put(b, "boat", x0 - 1, end)
    return end


def place_fishing_hamlet(b, ox, oy):
    """The hamlet piece (SW anchor ox,oy — oy is the shoreline row): two cottages NORTH of the
    shore (staggered, different yards), the dock at ox+18 running south into the cove, and the
    working clutter between the cottages and the water."""
    place_cottage(b, ox, oy + 8, npc="fisher_down", yard_style="small_plot")
    place_cottage(b, ox + 24, oy + 11, npc="farmer_down", yard_style="unfenced")

    # The dock, south into the cove; a second stub dock WEST of it keeps it a HAMLET, not one
    # pier (both sit over the bay — a stub east of the cove mouth would find no water).
    _dock(b, ox + 18, oy, max_len=12)
    _dock(b, ox + 8, oy + 1, max_len=6)

    # Working shore: the catch crated IN A ROW (the rows rule), barrels by the dock head.
    for i in range(3):
        if b.is_free(ox + 14 + i, oy + 2):
            b.place_occupant("fish_crate", ox + 14 + i, oy + 2)
    for x, y in [(ox + 21, oy + 2), (ox + 22, oy + 3)]:
        if b.is_free(x, y):
            b.place_occupant("barrel", x, y)
    if b.is_free(ox + 27, oy + 2):
        b.place_occupant("crate", ox + 27, oy + 2)
    if b.is_free(ox + 12, oy + 1):
        b.place_occupant("driftwood", ox + 12, oy + 1)
    if b.is_free(ox + 33, oy + 2):
        b.place_occupant("seashell_pile", ox + 33, oy + 2)
    if b.is_free(ox + 16, oy + 3):
        b.place_occupant("lamp_post", ox + 16, oy + 3)
    return oy


PREVIEW = "zones/bee_meadow_20/scenes"
SCALE = 5


def build():
    b = ZoneBuilder("scene_fishing_docks", 52, 46, base_tile="grass", name="Fishing hamlet", biome="coast")
    # The cove: a lake hugging the south edge (the zone supplies the real sea cove).
    lake(b, 25, 5, 14, seed=5, shore="sand", reeds=10)
    place_fishing_hamlet(b, 4, 12)
    b.spawn = [24, 20]
    return b


if __name__ == "__main__":
    from scene_preview import render
    b = build()
    print("LINT:", b.lint() or "0 defects", "| missing_art:", b.missing_art())
    render(b, __file__, PREVIEW, SCALE)
