#!/usr/bin/env python3
"""Building piece — the SMITH (blacksmith). A FORGE main room (furnace + forge + anvil, the smith at
work, tool racks + a suit of armor) over a back SUPPLY room (iron chests, coal, ore, barrels, crates),
connected by an internal door, set in a fenced work-yard with an ore/coal pile and trees.

`place_smith(b, ox, oy)` drops the whole thing into any builder; run directly to preview standalone ->
tools/_generated/previews/tests/scene_smith.png.
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

# 12 wide x 14 tall: SUPPLY room (north) over the FORGE room (south, with the front door).
SMITH = """
WWWWWWWWWWWW
Wh..k.o.q.bW
W..........W
Wc..b..c.k.W
WWWWWDWWWWWW
W..........W
Wt.F...G..tW
W........S.W
W...N..w...W
W...M......W
W..........W
Wk.o......bW
W.c......c.W
WWWWWDWWWWWW
"""
LEG = {"W": ("occ", "wall_stone"), "D": ("occ", "door_square"), "F": ("occ", "furnace"),
       "G": ("occ", "forge"), "N": ("occ", "anvil"), "M": ("npc", "miner_down"),
       "w": ("occ", "water_bucket"), "t": ("occ", "tool_rack"), "S": ("occ", "suit_of_armor"),
       "k": ("occ", "coal_bin"), "o": ("occ", "ore_pile"), "q": ("occ", "ore_sack"),
       "h": ("occ", "chest_iron"), "b": ("occ", "barrel"), "c": ("occ", "crate"), ".": ("floor",)}

BW, BH, DOORX = 12, 14, 5


def place_smith(b, ox, oy):
    """Drop the smithy (SW corner ox,oy). A workshop is OPEN-FRONTED (no fence) — just the building, its
    sign, and outdoor ore/coal out front. Door faces south at ox+DOORX. Returns the building rect."""
    stamp(b, SMITH, LEG, ox=ox, oy=oy)
    from features.village import shop_frontage
    shop_frontage(b, ox, oy, sign_id="sign_anvil", sign_x=DOORX - 2,
                  items=[("ore_pile", 1, -2), ("coal_bin", BW - 4, -2), ("barrel", BW - 2, -2)])
    for (oid, x, y) in []:                                            # (folded into the frontage line)
        fw, fh = b.footprint(oid)
        if all(b.in_bounds(x + dx, y + dy) and b.is_free(x + dx, y + dy)
               for dx in range(fw) for dy in range(fh)):
            b.place_occupant(oid, x, y, surface="grass")
    return (ox, oy, ox + BW - 1, oy + BH - 1)


def build():
    b = ZoneBuilder("scene_smith", BW + 8, BH + 12, base_tile="grass", name="Smith")
    place_smith(b, 4, 7)
    b.spawn = [4 + DOORX, 1]
    return b


if __name__ == "__main__":
    b = build()
    out = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "tests", "scene_smith.png"))
    render_builder(b, out, scale=10)
    print(dump(b, 4, 7, 15, 20))
    print("LINT:", b.lint() or "0 defects", "| warnings:", len(b.warnings), "| missing_art:", b.missing_art())
    print("rendered ->", out)
