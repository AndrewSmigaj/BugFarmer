#!/usr/bin/env python3
"""Building piece — the MAYOR'S MANSION as a FULL HOME: a grand marble hall/office (the mayor at his
desk, fancy seating, bookshelves, clock, globe) over a fancy bedroom, kitchen and bathroom off it via
internal doors — set in an IRON-fenced estate with a formal front garden (fountain + statues + beds),
side yards, a backyard and trees.

`place_mayor(b, ox, oy)` drops the whole estate into any builder; run directly to preview standalone ->
tools/_generated/previews/tests/scene_mayor.png.
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

# Same room shell as the ecologist home (footprints line up); marble walls + a fancy furniture legend.
HALL = """
WWWWWWWWWWWWWWWWWW
W...r.Wv.f.Wh..y.W
W.....W....W.....W
W.....Wc.k.Wk..m.W
WE.n..W....W.....W
W.....Wt...W.....W
WWWDWWWWWDWWWWDWWW
WS..G.g...K.L....W
W................W
W..Y.X.....N..A.pW
Wo..............oW
W................W
WWWWWWWWWDWWWWWWWW
"""
LEG = {"W": ("occ", "wall_marble"), "D": ("occ", "door_square"),
       "E": ("occ", "bed_fancy"), "n": ("occ", "nightstand_fancy"), "r": ("occ", "dresser_fancy"),
       "v": ("occ", "range_stove"), "f": ("occ", "fridge"), "c": ("occ", "counter_fancy"),
       "k": ("occ", "sink"), "t": ("occ", "dining_table_fancy"), "h": ("occ", "bathtub"),
       "y": ("occ", "vanity"), "m": ("occ", "mirror_standing"), "S": ("occ", "bookshelf_fancy"),
       "G": ("occ", "grandfather_clock"), "g": ("occ", "globe"), "K": ("occ", "cabinet"),
       "L": ("occ", "bookshelf_fancy"), "X": ("occ", "desk"), "Y": ("npc", "scholar_down"),
       "A": ("occ", "armchair_fancy"), "N": ("occ", "sofa_fancy"), "p": ("occ", "plant_large"),
       "o": ("occ", "potted_plant"), ".": ("floor",)}

BW, BH, DOORX = 18, 13, 9
FK = ["flower_red", "flower_blue", "flower_yellow", "poppy", "lavender"]


def _safe(b, oid, x, y, **k):
    fw, fh = b.footprint(oid)
    return b.place_occupant(oid, x, y, **k) if all(b.is_free(x + dx, y + dy)
                                                   for dx in range(fw) for dy in range(fh)) else False


def place_mayor(b, ox, oy):
    """Drop the mansion (SW corner ox,oy) in an iron-fenced estate with a formal front garden."""
    stamp(b, HALL, LEG, ox=ox, oy=oy)
    rect = property_yard(b, ox, oy, ox + BW - 1, oy + BH - 1, ox + DOORX,
                         side=3, front=7, back=4, fence="fence_iron", gate_id="gate_iron", flowers=None)
    # formal front garden: a fountain + flanking statues + edged beds (front yard is 7 deep)
    _safe(b, "fountain", ox + 2, oy - 4)
    _safe(b, "statue_founder", ox + DOORX - 4, oy - 3); _safe(b, "statue_founder", ox + DOORX + 3, oy - 3)
    from features.garden import flower_patch
    flower_patch(b, ox + DOORX + 2, oy - 6, ox + BW - 2, oy - 5, FK, 8, seed=5)
    _safe(b, "column_marble", ox, oy - 1); _safe(b, "column_marble", ox + BW - 1, oy - 1)  # flank the entrance
    return rect


def build():
    b = ZoneBuilder("scene_mayor", BW + 10, BH + 15, base_tile="grass", name="Mayor's estate")
    place_mayor(b, 5, 9)
    b.spawn = [5 + DOORX, 1]
    return b


if __name__ == "__main__":
    b = build()
    out = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "tests", "scene_mayor.png"))
    render_builder(b, out, scale=8)
    print(dump(b, 5, 9, 22, 21))
    print("LINT:", b.lint() or "0 defects", "| warnings:", len(b.warnings), "| missing_art:", b.missing_art())
    print("rendered ->", out)
