#!/usr/bin/env python3
"""House example: the player's ⊥ cottage (bedroom · main · kitchen bar + crafting stem).

Reusable: `place_player_house(b, ox, oy)` drops the whole house into any builder at an
offset, so scenes can compose it with the rest of the world. Run this file directly to
render just the house. Guide: docs/guides/authoring/house.md.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder                                    # noqa: E402
from render import render_builder                                      # noqa: E402
from features.house import (place_house, styled_rooms, living_template,   # noqa: E402
                            bedroom_template, kitchen_template, crafting_template)

# Bounding box of the house (incl. the approach path) in its own local frame.
HOUSE_W, HOUSE_H = 38, 28


def place_player_house(b, ox=0, oy=0):
    """Place the ⊥ cottage offset by (ox, oy). Front door faces SOUTH (low local-y); a
    short path runs out from it. Returns the room list."""
    def R(x0, y0, x1, y1):
        return (x0 + ox, y0 + oy, x1 + ox, y1 + oy)

    # The player's home is the "rich showcase" -> the fancy collection.
    rooms = styled_rooms([
        ("bedroom",  R(4, 8, 13, 17),  bedroom_template),
        ("main",     R(13, 8, 24, 17), living_template),
        ("kitchen",  R(24, 8, 34, 17), kitchen_template),
        ("crafting", R(15, 17, 23, 25), crafting_template),
    ], collection="fancy")
    place_house(b, rooms, floor="wood_floor", front=("main", "top"))
    for y in range(4, 8):  # approach path south of the front door
        b.set_ground(18 + ox, y + oy, "stone_path", surface="path")
        b.set_ground(19 + ox, y + oy, "stone_path", surface="path")
    return rooms


def build():
    b = ZoneBuilder("scene_player_house", 40, 30, base_tile="grass", name="Player house")
    place_player_house(b, 0, 0)
    return b


if __name__ == "__main__":
    b = build()
    out = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "scene_player_house.png"))
    render_builder(b, out, scale=7)
    print("missing_art:", b.missing_art())
    print("warnings:", len(b.warnings))
