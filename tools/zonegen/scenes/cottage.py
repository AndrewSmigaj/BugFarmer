#!/usr/bin/env python3
"""Example scene: a cottage + fenced yard.

A worked example for the zone-authoring guides and a catalog/QA vignette: it exercises
the room, scatter, and occupant-placement primitives and shows feature interaction
(scatter fills only free yard grass, avoiding the fence/path/buildings). Renders straight
to a preview PNG (no zone files). Run: python3 tools/zonegen/scenes/cottage.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)  # tools/zonegen
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder          # noqa: E402
from render import render_builder             # noqa: E402
from features.room import place_room          # noqa: E402
from features.scatter import scatter          # noqa: E402


def build():
    b = ZoneBuilder("scene_cottage", 40, 24, base_tile="grass", name="Cottage example", biome="meadow")

    # --- cottage shell (top-left), door on the bottom wall ---
    ix0, iy0, ix1, iy1 = place_room(b, 2, 2, 12, 11, door_side="bottom")
    b.place_occupant("bed_fancy", ix0, iy0 + 1)         # left wall (2-wide)
    b.place_occupant("bookshelf", ix0, iy0)             # back-left
    b.place_occupant("fireplace", ix1 - 1, iy0)         # back-right (2-wide)
    b.place_occupant("chest_wood", ix1 - 1, iy0 + 2)    # right side (2-wide -> stay off the wall)
    b.place_occupant("table_wood", ix0 + 3, iy1 - 1)    # 2x2 -> keep its bottom row off the wall
    b.place_occupant("chair_wood", ix0 + 2, iy1 - 1)
    b.place_occupant("chair_wood", ix0 + 6, iy1 - 1)
    b.place_occupant("lamp_floor", ix1, iy1)            # corner

    # --- path out the door, down to the yard gate ---
    b.fill_ground(6, 12, 7, 23, "stone_path", surface="path")

    # --- fenced yard to the right (gate gap in the top run) ---
    fx0, fy0, fx1, fy1 = 15, 3, 37, 20
    gate_x = (fx0 + fx1) // 2
    for x in range(fx0, fx1 + 1):
        if x != gate_x:
            b.place_occupant("fence_wood", x, fy0)
        b.place_occupant("fence_wood", x, fy1)
    for y in range(fy0 + 1, fy1):
        b.place_occupant("fence_wood", fx0, y)
        b.place_occupant("fence_wood", fx1, y)
    b.place_occupant("gate_wood", gate_x, fy0)

    # yard features
    b.place_occupant("planter_box", 18, 9)
    b.place_occupant("planter_box", 21, 9)
    b.place_occupant("well", 29, 14)
    b.place_occupant("signpost", 17, 18)
    b.place_occupant("bench", 32, 18)
    b.place_occupant("tree_oak", 34, 8)
    b.place_occupant("tree_apple", 25, 7)

    # scatter decor on the leftover yard grass (avoids fence/path/features automatically)
    scatter(b, fx0 + 1, fy0 + 1, fx1 - 1, fy1 - 1,
            {"flower_red": 3, "flower_blue": 3, "flower_yellow": 3, "bush": 2,
             "sunflower": 1, "tall_grass": 2},
            density=0.10, min_spacing=2, seed=7)
    return b


if __name__ == "__main__":
    b = build()
    out = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "scene_cottage.png"))
    render_builder(b, out, scale=8)
    print("missing_art:", b.missing_art())
    print("validate:", b.validate())
