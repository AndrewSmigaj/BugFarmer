#!/usr/bin/env python3
"""Context render: a one-room house for the WALL blocks — wood floor, grass outside, a bed + chair.
Two rooms so we see wall_wood and wall_stone in-world. Renders to previews/blocklab/block_house.png
(override with $BLOCKLAB_OUT). Uses whatever wall sprites are live, so the bake-off harness can swap
in each approach's variant and re-render. Free (no API).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder              # noqa: E402
from render import render_builder                # noqa: E402
from features.room import place_room             # noqa: E402

W, H = 38, 22


def build():
    b = ZoneBuilder("scene_block_house", W, H, base_tile="grass", name="Block house test")
    # left room: WOOD walls
    place_room(b, 3, 4, 14, 13, floor="wood_floor", wall="wall_wood", door="door_wood", door_side="bottom")
    for oid, x, y in [("bed_basic", 5, 5), ("chair_wood", 12, 6), ("table_wood", 10, 10)]:
        if b.is_free(x, y):
            b.place_occupant(oid, x, y, surface=None)
    # right room: STONE walls
    place_room(b, 22, 4, 33, 13, floor="wood_floor", wall="wall_stone", door="door_wood", door_side="bottom")
    for oid, x, y in [("bed_basic", 24, 5), ("chair_wood", 31, 6), ("table_wood", 29, 10)]:
        if b.is_free(x, y):
            b.place_occupant(oid, x, y, surface=None)
    b.spawn = [18, 18]
    return b


if __name__ == "__main__":
    b = build()
    out = os.environ.get("BLOCKLAB_OUT") or os.path.abspath(
        os.path.join(ZG, "..", "_generated", "previews", "blocklab", "block_house.png"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    render_builder(b, out, scale=14)
    print("placeholders:", b.missing_art(), "warnings:", len(b.warnings))
    print("wrote", out)
