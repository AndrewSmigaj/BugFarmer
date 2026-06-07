#!/usr/bin/env python3
"""Context render: a mining micro-scene for the GROUND blocks — a stepped cliff cross-section of dirt
(upper layers) over stone (below), grass on top, a pond, and a cave opening floored with TILES (cave_floor),
not blocks, as the ore test bed. Renders to previews/scene_block_mine.png.
Uses whatever block sprites are live so the harness can swap each approach's variant. Free (no API).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder              # noqa: E402
from render import render_builder                # noqa: E402
from features.terrain import pond                # noqa: E402

W, H = 46, 26
# Renderer is +Y NORTH, so HIGH y renders at the top. Grass surface sits at a high y per cliff step;
# blocks fill BELOW it (lower y). Three stepped "cliffs" of decreasing surface height.
STEPS = [(0, 16, 17), (16, 31, 14), (31, 46, 11)]   # (x0, x1, surface_y)


def build():
    b = ZoneBuilder("scene_block_mine", W, H, base_tile="grass", name="Block mine test")

    # cave opening cut into the block mass, floored with a TILE (dirt), not blocks
    cave = {(x, y) for x in range(19, 27) for y in range(3, 11)}

    for (x0, x1, sy) in STEPS:
        for x in range(x0, x1):
            for y in range(0, sy):                 # blocks below the grass surface
                if (x, y) in cave:
                    continue
                key = "dirt_block" if y >= sy - 3 else "stone_block"   # dirt just under the surface, stone deeper
                b.place_occupant(key, x, y, surface=None, reserve=False)

    # the cave interior: tile floor (NOT blocks) — cave_floor is broken (chest), use the dirt tile
    for (x, y) in cave:
        if b.in_bounds(x, y):
            b.set_ground(x, y, "dirt", surface=None)

    # a pond on the top grass shelf (right side, highest cliff)
    pond(b, 38, 20, 3, 2, seed=2)

    b.spawn = [2, 20]
    return b


if __name__ == "__main__":
    b = build()
    out = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "scene_block_mine.png"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    render_builder(b, out, scale=12)
    print("placeholders:", b.missing_art(), "warnings:", len(b.warnings))
    print("wrote", out)
