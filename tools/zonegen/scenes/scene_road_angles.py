#!/usr/bin/env python3
"""scene_road_angles — the road-angle system's test card (roads.md).

Four road shapes, RAW on the left half vs SMOOTHED (terrain.smooth_paths) on the
right, same seeds: a straight run, a gentle bend, a 45° diagonal run, and an S-curve.
The smoothed side should show every stair-step corner bevelled by a diagonal
transition tile (stone_path_d_*/dirt_path_d_*, composited by
tools/make_diagonal_tiles.py) — curves read as curves, not staircases.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from zonebuilder import ZoneBuilder           # noqa: E402
from features.terrain import path, smooth_paths  # noqa: E402

W, H = 96, 64


def lay_roads(b, ox):
    """The four test shapes, offset to start at column ox (half-board)."""
    # 1. straight (control: smoothing must not touch it)
    path(b, (ox + 4, 6), (ox + 40, 6), width=3, wobble=0.0, seed=1)
    # 2. gentle bend (the village main-road case)
    path(b, (ox + 4, 16), (ox + 40, 26), width=3, wobble=0.14, seed=7)
    # 3. 45° diagonal run (the worst case for square tiles)
    path(b, (ox + 4, 30), (ox + 28, 54), width=3, wobble=0.05, seed=3)
    # 4. S-curve, dirt road (the lane material)
    path(b, (ox + 30, 34), (ox + 42, 58), width=2, tile="dirt", wobble=0.3, seed=11)


def build():
    b = ZoneBuilder("scene_road_angles", W, H, base_tile="grass")
    lay_roads(b, 0)            # RAW half
    lay_roads(b, 48)           # SMOOTHED half
    # smooth only the right half: temporarily mask the left by running the pass on a
    # cropped view — simplest correct way is to run globally then revert left-half fills
    filled = smooth_paths(b)
    for (x, y) in filled:
        if x < 48:
            b.set_ground(x, y, "grass", surface="grass")
    print(f"smooth_paths filled {sum(1 for (x, _) in filled if x >= 48)} corners (right half)")
    return b


if __name__ == "__main__":
    from registry import render_one
    render_one("scene_road_angles")
