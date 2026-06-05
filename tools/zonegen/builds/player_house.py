#!/usr/bin/env python3
"""Scene: the player's house — an upside-down-T (⊥) cottage (part of scene 1).

A horizontal bar of three rooms — BEDROOM (left) · MAIN/living (center) · KITCHEN (right)
— with a CRAFTING nook as the stem rising north out of the main room. Rooms are varied in
size and connected by squashed interior doors; the front door is on the main room's south
wall. Furniture is placed against the walls by the room templates in features/house.py.
Run: python3 tools/zonegen/builds/player_house.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder                                    # noqa: E402
from render import render_builder                                      # noqa: E402
from features.house import (place_house, living_template,             # noqa: E402
                            bedroom_template, kitchen_template, crafting_template)


def build():
    # NOTE: world +Y is NORTH (up on screen), matching the game. So higher row numbers are
    # toward the top of the rendered image. The three-room bar sits in the middle, the crafting
    # nook rises NORTH (higher rows) out of the main room, and the front door faces SOUTH (the
    # low-row "top" wall in place_house's array-naming) toward the approach path.
    b = ZoneBuilder("scene_player_house", 40, 30, base_tile="grass", name="Player house")

    rooms = [
        {"name": "bedroom",  "rect": (4, 8, 13, 17),   "fill": bedroom_template},
        {"name": "main",     "rect": (13, 8, 24, 17),  "fill": living_template},
        {"name": "kitchen",  "rect": (24, 8, 34, 17),  "fill": kitchen_template},
        {"name": "crafting", "rect": (15, 17, 23, 25), "fill": crafting_template},
    ]
    place_house(b, rooms, floor="wood_floor", front=("main", "top"))

    # a short path from the front (south) door out toward the approach
    for y in range(4, 8):
        b.set_ground(18, y, "stone_path", surface="path")
        b.set_ground(19, y, "stone_path", surface="path")
    return b


if __name__ == "__main__":
    b = build()
    out = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "scene_player_house.png"))
    render_builder(b, out, scale=7)
    print("missing_art:", b.missing_art())
    print("warnings:", len(b.warnings))
