#!/usr/bin/env python3
"""scene_houses — the HOUSE-SHAPE showcase (house.md's test card).

v2 (2026-06, "not squares — natural, and mostly square"): the grid shows the
NON-CONVEX shapes — a true L (with a PORCH), a courtyard U (dressed court), a Z
with an annex shed — and two GENERATIVE `sculpt_plan` seeds, across basic/fancy
collections, each in a yard. Rendering this card is the proof that a street built
from these never reads as clone boxes.

Run: python3 tools/zonegen/scenes/scene_houses.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
sys.path.insert(0, HERE)
from zonebuilder import ZoneBuilder                                    # noqa: E402
from render import render_builder                                      # noqa: E402
from features.house import (place_house, styled_rooms, bbox, porch,    # noqa: E402
                            l_house, u_house, z_house, sculpt_plan, courtyard_rect)
from features.yard import yard, styled_yard                            # noqa: E402

W, H = 150, 105


def place_one(b, specs, front, coll, *, with_porch=False, court=None, yard_style="modest"):
    rooms = styled_rooms(specs, collection=coll)
    place_house(b, rooms, front=front)
    bx0, by0, bx1, by1 = bbox(specs)
    # the gate aligns with the ACTUAL front door (the front room's south-wall
    # middle — the bbox center is wrong for offset shapes like the Z)
    south = min(r[1][1] for r in specs)
    fr = max((r for r in specs if r[1][1] == south), key=lambda r: r[1][2] - r[1][0])
    gx = (fr[1][0] + fr[1][2]) // 2
    styled_yard(b, bx0, by0, bx1, by1, gx, style=yard_style)
    if with_porch:
        porch(b, specs)
    if court:
        cx0, cy0, cx1, cy1 = court
        for (oid, x, y) in [("birdbath", (cx0 + cx1) // 2, cy0 + 1),
                            ("poppy", cx0, cy0), ("chamomile", cx1, min(cy1, cy0 + 3))]:
            if b.in_bounds(x, y) and b.is_free(x, y):
                b.place_occupant(oid, x, y)


PREVIEW = "examples/buildings"
SCALE = 2


def build():
    b = ZoneBuilder("scene_houses", W, H, base_tile="grass", name="House shapes")
    # Row 1 (south): the fixed natural shapes
    specs, front = l_house(8, 8)
    place_one(b, specs, front, "basic", with_porch=True, yard_style="modest")
    specs, front = u_house(42, 8)
    place_one(b, specs, front, "fancy", court=courtyard_rect(specs), yard_style="grand")
    specs, front = z_house(82, 8)
    place_one(b, specs, front, "basic", yard_style="small_plot")
    # Row 2 (north): generative seeds — a different silhouette every seed
    specs, front = sculpt_plan(10, 58, seed=3, rooms=4)
    place_one(b, specs, front, "fancy", with_porch=True, yard_style="unfenced")
    specs, front = sculpt_plan(75, 58, seed=11, rooms=5)
    place_one(b, specs, front, "basic", yard_style="modest")
    return b


if __name__ == "__main__":
    from scene_preview import render
    b = build()
    print("LINT:", b.lint() or "0 defects", "| missing_art:", b.missing_art())
    render(b, __file__, PREVIEW, SCALE)
