#!/usr/bin/env python3
"""Building piece — the CARPENTER (woodworker). A WORKSHOP main room (workbench + sawhorse + sawmill,
the carpenter at the bench, tool racks, a table in progress) over a back TIMBER/SUPPLY room (lumber
racks, wood chests, log seats, crates), connected by an internal door, in a fenced work-yard with a
lumber stack + trees.

`place_carpenter(b, ox, oy)` drops it into any builder; run directly to preview standalone ->
tools/_generated/previews/tests/scene_carpenter.png.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder                                   # noqa: E402
from render import render_builder                                     # noqa: E402
from features.tilemap import stamp, dump                              # noqa: E402
from features.yard import property_yard                               # noqa: E402

# 12 wide x 14 tall: TIMBER/SUPPLY room (north) over the WORKSHOP (south, with the front door).
SHOP = """
WWWWWWWWWWWW
WL..h..L...W
W..........W
Wg.c..b..c.W
WWWWWDWWWWWW
W..........W
Wt.B....S.tW
W..M.......W
W..........W
W...H......W
W.....T....W
W..........W
Wb..c..g..bW
WWWWWDWWWWWW
"""
LEG = {"W": ("occ", "wall_wood"), "D": ("occ", "door_square"), "L": ("occ", "lumber_rack"),
       "h": ("occ", "chest_wood"), "g": ("occ", "log_seat"), "c": ("occ", "crate"),
       "b": ("occ", "barrel"), "t": ("occ", "tool_rack"), "B": ("occ", "workbench"),
       "S": ("occ", "sawmill"), "M": ("npc", "farmer_down"), "H": ("occ", "sawhorse"),
       "T": ("occ", "table_wood"), ".": ("floor",)}

BW, BH, DOORX = 12, 14, 5


def place_carpenter(b, ox, oy):
    """Drop the carpenter's shop (SW corner ox,oy). Open-fronted (no fence) — building, sign, and a
    lumber stack out front. Door faces south at ox+DOORX. Returns the building rect."""
    stamp(b, SHOP, LEG, ox=ox, oy=oy)
    b.place_occupant("sign_plank", ox + DOORX - 2, oy - 1, surface="grass")
    for (oid, x, y) in [("lumber_rack", ox + 1, oy - 2), ("sawhorse", ox + BW - 3, oy - 2)]:  # lumber outside, no fence
        fw, fh = b.footprint(oid)
        if all(b.in_bounds(x + dx, y + dy) and b.is_free(x + dx, y + dy)
               for dx in range(fw) for dy in range(fh)):
            b.place_occupant(oid, x, y, surface="grass")
    return (ox, oy, ox + BW - 1, oy + BH - 1)


def build():
    b = ZoneBuilder("scene_carpenter", BW + 8, BH + 12, base_tile="grass", name="Carpenter")
    place_carpenter(b, 4, 7)
    b.spawn = [4 + DOORX, 1]
    return b


if __name__ == "__main__":
    b = build()
    out = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "tests", "scene_carpenter.png"))
    render_builder(b, out, scale=10)
    print(dump(b, 4, 7, 15, 20))
    print("LINT:", b.lint() or "0 defects", "| warnings:", len(b.warnings), "| missing_art:", b.missing_art())
    print("rendered ->", out)
