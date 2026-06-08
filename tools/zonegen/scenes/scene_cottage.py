#!/usr/bin/env python3
"""Building piece — a small NPC COTTAGE (a home): a bedroom over a living-room/kitchen, an internal door
between, in a fenced yard with a front garden + trees. One per villager NPC.

`place_cottage(b, ox, oy, npc="farmer_down")` drops it into any builder; run directly to preview ->
tools/_generated/previews/tests/scene_cottage.png.
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

# 10 wide x 12 tall: BEDROOM (north) over a LIVING/KITCHEN (south, front door).
COT = """
WWWWWWWWWW
W...n.r..W
W........W
W........W
WE.......W
WWWWDWWWWW
Wv.k...c.W
W........W
W.t......W
Wa.a...p.W
W........W
WWWWDWWWWW
"""
LEG = {"W": ("occ", "wall_wood"), "D": ("occ", "door_square"), "E": ("occ", "bed_basic"),
       "n": ("occ", "nightstand"), "r": ("occ", "dresser"), "v": ("occ", "stove"),
       "k": ("occ", "sink"), "c": ("occ", "cupboard"), "t": ("occ", "table_wood"),
       "a": ("occ", "chair_wood"), "p": ("occ", "potted_plant"), ".": ("floor",)}

BW, BH, DOORX = 10, 12, 4


def place_cottage(b, ox, oy, npc="farmer_down"):
    """Drop the cottage (SW corner ox,oy) in a fenced garden yard. Door faces south at ox+DOORX."""
    stamp(b, COT, LEG, ox=ox, oy=oy)
    b.place_player(npc, ox + 6.0, oy + 4)            # the resident, in the living room
    return property_yard(b, ox, oy, ox + BW - 1, oy + BH - 1, ox + DOORX,
                         side=2, front=4, back=3, fence="fence_picket", gate_id="gate_picket", seed=ox)


def build():
    b = ZoneBuilder("scene_cottage", BW + 8, BH + 10, base_tile="grass", name="Cottage")
    place_cottage(b, 3, 6)
    b.spawn = [3 + DOORX, 1]
    return b


if __name__ == "__main__":
    b = build()
    out = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "tests", "scene_cottage.png"))
    render_builder(b, out, scale=12)
    print(dump(b, 3, 6, 12, 17))
    print("LINT:", b.lint() or "0 defects", "| warnings:", len(b.warnings), "| missing_art:", b.missing_art())
    print("rendered ->", out)
