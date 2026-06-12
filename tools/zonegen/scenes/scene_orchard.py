#!/usr/bin/env python3
"""scene_orchard — garden.orchard's test card AND the guide's worked vignette.

A fenced orchard plot: jittered apple rows (post-jitter spacing enforced), walking
lanes, crates + a ladder at the row ends, fallen fruit under some trees (render-only
decor — the live loop is the server fruit sim). A dirt lane runs past the gate the
way it would in the village.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from zonebuilder import ZoneBuilder          # noqa: E402
from features.terrain import path            # noqa: E402
from features.garden import orchard          # noqa: E402
from features.yard import fence_rect         # noqa: E402

W, H = 56, 44


def build():
    b = ZoneBuilder("scene_orchard", W, H, base_tile="grass")
    # the lane FIRST (roads before farms), running past the south fence
    path(b, (2, 5), (W - 3, 7), width=2, tile="dirt", wobble=0.12, seed=4)
    # the plot: fence with a south gate onto the lane
    fence_rect(b, 6, 10, 49, 38, gate=(27, 10))
    trees = orchard(b, 7, 11, 48, 37, seed=9)
    print(f"orchard planted {len(trees)} apple trees")
    return b


if __name__ == "__main__":
    from registry import render_one
    render_one("scene_orchard")
