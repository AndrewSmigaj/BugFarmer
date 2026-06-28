#!/usr/bin/env python3
"""Building piece — the STONEMASON ("Dougal's Stoneworks"). A compact, dusty STONE WORKSHOP (store of
raw blocks + a cutting room with the stonecutter, a chisel bench, and a half-carved statue) opening
onto a generous OPEN DISPLAY YARD — the yard IS the feature: a central path lined with marble columns,
rows of finished statues, a working fountain as the focal point, and stacks of cut stone.

`place_stonemason(b, ox, oy)` drops it; run directly to preview ->
tools/_generated/previews/zones/village_21_B/scenes/stonemason.png.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder                                   # noqa: E402
from features.tilemap import stamp                                   # noqa: E402

# Building 12 wide x 9 tall (smith-sized, stone). STORE (N, raw blocks + tool rack + brick pile +
# crate) over a CUTTING ROOM (stonecutter, chisel bench, the work-in-progress statue, the mason).
# 2-wide pieces = anchor char + '.' for the rest of the footprint.
BUILDING = """
WWWWWWWWWWWW
Ws.s.t.b..cW
W.s..b...s.W
WWWDWWWWDWWW
WK...H...U.W
W..........W
W...N......W
W..........W
WWWWWDWWWWWW
"""
LEG = {
    "W": ("occ", "wall_stone"), "D": ("occ", "door_square"),
    "K": ("occ", "stonecutter"),       # cut station (2-wide)
    "H": ("occ", "chisel_bench"),       # fine-work bench (2-wide)
    "U": ("occ", "statue_unfinished"),  # WIP storytelling prop
    "s": ("occ", "stone_block"), "b": ("occ", "brick_pile"),
    "t": ("occ", "tool_rack"), "c": ("occ", "crate"),
    "N": ("npc", "scholar_down"), ".": ("floor",),
}

BW, BH, DOORX = 12, 9, 5

# OPEN DISPLAY YARD, south of the building (dy < 0 from the front wall at oy). Statues in rows, a
# marble-column gateway, a focal fountain at the far end, material stacks. Each = (id, dx, dy) of
# the SW anchor relative to (ox, oy); placed on grass.
YARD = [
    ("column_marble", 2, -1), ("column_marble", 8, -1),   # gateway columns flanking the path
    ("statue_founder", 1, -4),                            # grand civic statue (2x2), left
    ("cat_statue", 8, -3), ("statue_bug", 8, -5),         # right display row
    ("birdbath", 8, -7),
    ("statue_stone", 1, -7),                              # left display row
    ("fountain", 4, -8),                                  # focal fountain at the far end (2x2)
    ("brick_pile", 1, -2), ("stone_block", 9, -2),        # material stacks by the building
]
# central stone path from the door out into the yard (2 wide)
PATH = [(4, dy) for dy in range(-1, -8, -1)] + [(5, dy) for dy in range(-1, -8, -1)]


def place_stonemason(b, ox, oy):
    """Drop the stonemason (building SW corner ox,oy) + its open display yard to the south."""
    stamp(b, BUILDING, LEG, ox=ox, oy=oy, floor="stone_floor")
    for dx, dy in PATH:
        if b.in_bounds(ox + dx, oy + dy):
            b.set_ground(ox + dx, oy + dy, "stone_path", surface="path")
    for oid, dx, dy in YARD:
        x, y = ox + dx, oy + dy
        if all(b.is_free(x + ddx, y + ddy)
               for ddx in range(b.footprint(oid)[0]) for ddy in range(b.footprint(oid)[1])):
            b.place_occupant(oid, x, y, surface="grass")
        else:
            b.warn(f"yard {oid} @({dx},{dy}) blocked")
    from features.village import shop_frontage
    shop_frontage(b, ox, oy, sign_id="sign_mason", sign_x=DOORX - 2, items=[])
    return (ox, oy, ox + BW - 1, oy + BH - 1)


PREVIEW = "zones/village_21_B/scenes"
SCALE = 6


def build():
    b = ZoneBuilder("scene_stonemason", BW + 8, BH + 14, base_tile="grass", name="Stonemason")
    place_stonemason(b, 4, 11)
    b.spawn = [4 + DOORX, 1]
    return b


if __name__ == "__main__":
    from scene_preview import render
    b = build()
    print("LINT:", b.lint() or "0 defects", "| missing_art:", b.missing_art())
    render(b, __file__, PREVIEW, SCALE)
