#!/usr/bin/env python3
"""Building piece — the ECOLOGIST'S HOUSE as a FULL HOME: four rooms (a study/main room with the front
door, plus a bedroom, a kitchen and a bathroom off it via internal doors), set in a fenced yard with
garden plots out front (the ecologist grows living plant specimens). Authored as a TEXT GRID; the lint
verifies every door (front + internal) has a clear cell to walk through.

`place_ecologist(b, ox, oy)` drops the whole home + yard into any builder (the village composes it);
run directly to preview standalone -> tools/_generated/previews/tests/scene_ecologist.png.
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

# 18 wide x 13 tall. NORTH rooms (bedroom | kitchen | bathroom) over a full-width STUDY with the front door.
# Internal doors in the cross-wall (cols 3/9/14) connect each back room to the study.
HOME = """
WWWWWWWWWWWWWWWWWW
W...r.Wv.f.Wh..y.W
W.....W....W.....W
W.....Wc.k.Wk..m.W
WE.n..W....W.....W
W.....Wt...W.....W
WWWDWWWWWDWWWWDWWW
WS..e.e...q.L....W
W................W
W.g.Y..G..T..N..pW
Wo..............oW
W................W
WWWWWWWWWDWWWWWWWW
"""
LEG = {"W": ("occ", "wall_wood"), "D": ("occ", "door_square"),
       "E": ("occ", "bed_basic"), "n": ("occ", "nightstand"), "r": ("occ", "dresser"),
       "v": ("occ", "stove"), "f": ("occ", "fridge"), "c": ("occ", "counter"), "k": ("occ", "sink"),
       "t": ("occ", "table_wood"), "h": ("occ", "bathtub"), "y": ("occ", "vanity"),
       "m": ("occ", "mirror_standing"), "S": ("occ", "specimen_shelf"), "e": ("occ", "bug_terrarium"),
       "q": ("occ", "aquarium"), "L": ("occ", "bookshelf"), "g": ("occ", "globe"),
       "Y": ("npc", "scholar_down"), "G": ("occ", "desk"), "T": ("occ", "telescope"),
       "N": ("occ", "fishing_net"), "p": ("occ", "plant_large"), "o": ("occ", "potted_plant"), ".": ("floor",)}

BW, BH = 18, 13           # building footprint in cells
DOORX = 9                 # front-door column (relative to ox)
FKINDS = ["flower_red", "flower_blue", "flower_yellow", "poppy", "lavender"]


def place_ecologist(b, ox, oy, fenced=True):
    """Drop the home (SW corner at ox,oy). Door at ox+DOORX, oy. `fenced=True` wraps it in a garden
    yard; `fenced=False` leaves it bare (e.g. a cabin set in the forest). Returns the footprint rect."""
    stamp(b, HOME, LEG, ox=ox, oy=oy)
    b.place_occupant("sign_leaf", ox + DOORX - 2, oy - 1, surface="grass")   # leaf sign by the door
    if fenced:
        return property_yard(b, ox, oy, ox + BW - 1, oy + BH - 1, ox + DOORX,
                             side=2, front=5, back=4, fence="fence_picket", gate_id="gate_picket",
                             flowers=FKINDS, seed=4)
    return (ox, oy, ox + BW - 1, oy + BH - 1)


def build():
    b = ZoneBuilder("scene_ecologist", BW + 8, BH + 14, base_tile="grass", name="Ecologist's house")
    place_ecologist(b, 4, 8)
    b.spawn = [4 + DOORX, 1]
    return b


if __name__ == "__main__":
    b = build()
    out = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "tests", "scene_ecologist.png"))
    render_builder(b, out, scale=10)
    print(dump(b, 3, 9, 20, 21))
    print("LINT:", b.lint() or "0 defects", "| warnings:", len(b.warnings), "| missing_art:", b.missing_art())
    print("rendered ->", out)
