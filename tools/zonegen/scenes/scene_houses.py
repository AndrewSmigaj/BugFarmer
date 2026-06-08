#!/usr/bin/env python3
"""Scene — HOUSE SHOWCASE: a grid of houses varying by room count and furniture collection,
each in a fenced yard with an approach path. This is the worked example + visual QA for the
house system (layouts + collections + yards).

Grid: columns = room count (3 / 4 / 5 via row_/t_/plus_house), rows = collection (basic, fancy).
A standing signpost marks each yard. Renders to tools/_generated/previews/scene_houses.png.
Run: python3 tools/zonegen/scenes/scene_houses.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder                       # noqa: E402
from render import render_builder                         # noqa: E402
from features.house import place_house, styled_rooms      # noqa: E402
from features.yard import yard                            # noqa: E402
from features.house import row_house, t_house, plus_house, bbox  # noqa: E402

LAYOUTS = [row_house, t_house, plus_house]   # 3, 4, 5 rooms
COLLECTIONS = ["basic", "fancy"]
COL_X = [3, 46, 89]      # local origin x of each column's house
ROW_Y = [3, 33]          # local origin y of each row's house (basic, fancy)
W, H = 128, 60


def place_one(b, layout_fn, coll, ox, oy):
    specs, front = layout_fn(ox, oy)
    rooms = styled_rooms(specs, collection=coll)
    place_house(b, rooms, front=front)

    # fenced yard one cell around the house bbox, gate centered on the south wall
    bx0, by0, bx1, by1 = bbox(specs)
    yx0, yy0, yx1, yy1 = bx0 - 1, by0 - 1, bx1 + 1, by1 + 1
    gx = (yx0 + yx1) // 2
    yard(b, yx0, yy0, yx1, yy1, gate=(gx, yy0), path_to=(gx, max(0, yy0 - 2)))
    # dressings OUTSIDE the south fence, flanking the path (placed after the fence so
    # is_free reflects it); a standing signpost labels the plot.
    for (oid, x, y) in [("lamp_post", gx - 2, yy0 - 1), ("lamp_post", gx + 2, yy0 - 1),
                        ("signpost", gx + 3, yy0 - 1), ("planter_box", yx0 + 1, yy0 + 1)]:
        if b.in_bounds(x, y) and b.is_free(x, y):
            b.place_occupant(oid, x, y, surface="grass")


def build():
    b = ZoneBuilder("scene_houses", W, H, base_tile="grass", name="House showcase")
    for ri, coll in enumerate(COLLECTIONS):
        for ci, layout_fn in enumerate(LAYOUTS):
            place_one(b, layout_fn, coll, COL_X[ci], ROW_Y[ri])
    return b


if __name__ == "__main__":
    b = build()
    out = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "scene_houses.png"))
    r = render_builder(b, out, scale=5)
    print("missing_art:", b.missing_art())
    print("warnings:", len(b.warnings))
    issues = b.validate()
    print("validate:", issues if issues else "OK")
