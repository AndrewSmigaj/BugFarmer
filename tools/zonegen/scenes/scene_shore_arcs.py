#!/usr/bin/env python3
"""scene_shore_arcs — shore_dress's test card (water.md).

One lobed lake dressed with FOUR different banks (the trees-and-ponds rule "no two
shores identical", now a primitive): sand beach on the south arc, reed bank east,
forested bank west, muddy bank north. Angles are math-convention with +y north:
0°=E, 90°=N, 180°=W, 270°=S.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from zonebuilder import ZoneBuilder              # noqa: E402
from features.terrain import lake, shore_dress   # noqa: E402

W, H = 72, 72


def build():
    b = ZoneBuilder("scene_shore_arcs", W, H, base_tile="grass")
    info = lake(b, 36, 36, 16, seed=5, reeds=0)   # reeds come from the arc, not the lake
    shore_dress(b, info, [
        (225, 315, "sand"),     # south arc: beach
        (315, 45, "reeds"),     # east arc: reed bank
        (45, 135, "mud"),       # north arc: muddy bank
        (135, 225, "forest"),   # west arc: forested bank
    ], seed=2)
    return b


if __name__ == "__main__":
    from registry import render_one
    render_one("scene_shore_arcs")
