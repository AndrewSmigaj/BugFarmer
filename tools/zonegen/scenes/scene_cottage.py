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

# 16 wide x 12 tall — FOUR rooms (the full-home standard, 2026-06): BEDROOM (NW)
# | BATHROOM (NE) over KITCHEN (SW) | LIVING (SE, front door). Interior doors
# hand-authored; the lint checks every doorway.
COT = """
WWWWWWWWWWWWWWW
W..n..r.Wh.y.kW
W.......W.....W
W.......D....mW
WE......W.....W
WWWWWWDWWWWWDWW
Wv..k...W.....W
Wc......W.....W
W..t....D.....W
Wa.a....W..p..W
W.......W.....W
WWWWWWWWWWDWWWW
"""
LEG = {"W": ("occ", "wall_wood"), "D": ("occ", "door_square"), "E": ("occ", "bed_basic"),
       "n": ("occ", "nightstand"), "r": ("occ", "dresser"), "v": ("occ", "stove"),
       "k": ("occ", "sink"), "c": ("occ", "cupboard"), "t": ("occ", "table_wood"),
       "a": ("occ", "chair_wood"), "p": ("occ", "potted_plant"),
       "h": ("occ", "bathtub"), "y": ("occ", "vanity"), "m": ("occ", "mirror_standing"),
       ".": ("floor",)}

BW, BH, DOORX = 15, 12, 10


def place_cottage(b, ox, oy, npc="farmer_down", yard_style="modest"):
    """Drop the 4-room cottage (SW corner ox,oy) in a STYLED yard (default modest:
    picket + veggie plot). Door faces south at ox+DOORX."""
    from features.yard import styled_yard
    stamp(b, COT, LEG, ox=ox, oy=oy)
    b.place_player(npc, ox + 11.0, oy + 4)           # the resident, in the living room
    return styled_yard(b, ox, oy, ox + BW - 1, oy + BH - 1, ox + DOORX,
                       style=yard_style, seed=ox)


def build():
    b = ZoneBuilder("scene_cottage", BW + 10, BH + 12, base_tile="grass", name="Cottage")
    place_cottage(b, 3, 6)
    b.spawn = [3 + DOORX, 1]
    return b


if __name__ == "__main__":
    b = build()
    out = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "tests", "scene_cottage.png"))
    render_builder(b, out, scale=12)
    print(dump(b, 3, 6, 3 + BW - 1, 6 + BH - 1))
    print("LINT:", b.lint() or "0 defects", "| warnings:", len(b.warnings), "| missing_art:", b.missing_art())
    print("rendered ->", out)
