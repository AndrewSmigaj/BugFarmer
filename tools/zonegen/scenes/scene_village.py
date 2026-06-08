#!/usr/bin/env python3
"""Scene — the STARTING VILLAGE (`village_21`), composed from the REAL building pieces. Layout logic:
a central market SQUARE on the main N-S street; the SHOPS (market, smith, carpenter) cluster around the
square on the commercial E-W street — OPEN-FRONTED, no fences; the HOMES (mayor, ecologist + a cottage
per NPC) line a residential street to the north, each FENCED with a garden; the boat store sits on the
SW lake. Buildings are placed CLEAR of every road (no road runs through a building).

Renders via registry.py to tools/_generated/previews/surface/scene_village.png.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
sys.path.insert(0, HERE)
from zonebuilder import ZoneBuilder                                   # noqa: E402
from render import render_builder                                     # noqa: E402
from features.terrain import pond                                     # noqa: E402
from features.scatter import scatter                                  # noqa: E402
from scene_smith import place_smith                                   # noqa: E402
from scene_carpenter import place_carpenter                           # noqa: E402
from scene_market import place_market                                 # noqa: E402
from scene_mayor import place_mayor                                   # noqa: E402
from scene_cottage import place_cottage                               # noqa: E402
from scene_lakeside import place_boat_store                           # noqa: E402
from player_house import place_player_house                           # noqa: E402
from features.yard import property_yard                               # noqa: E402
from features.garden import flower_patch                              # noqa: E402

W, H = 120, 116
MAINX = 58                                   # N-S main street (x57-59)
COMM_Y = 59                                  # commercial E-W street (y58-60), the square sits here
RES_Y = 85                                   # residential E-W street (y84-86)


def safe(b, oid, x, y, **k):
    fw, fh = b.footprint(oid)
    return b.place_occupant(oid, x, y, **k) if all(b.is_free(x + dx, y + dy)
                                                   for dx in range(fw) for dy in range(fh)) else False


def road_h(b, ys, x0=0, x1=W - 1, tile="stone_path"):
    for y in ys:
        for x in range(x0, x1 + 1):
            if b.in_bounds(x, y) and b.is_free(x, y):
                b.set_ground(x, y, tile, surface="path")


def road_v(b, xs, y0=0, y1=H - 1, tile="stone_path"):
    for x in xs:
        for y in range(y0, y1 + 1):
            if b.in_bounds(x, y) and b.is_free(x, y):
                b.set_ground(x, y, tile, surface="path")


def connect(b, gx, gy, road_y, tile="stone_path"):
    lo, hi = sorted((gy, road_y))
    for y in range(lo, hi + 1):
        for x in (gx - 1, gx):
            if b.in_bounds(x, y) and b.is_free(x, y):
                b.set_ground(x, y, tile, surface="path")


def square(b, cx, cy, r=4):
    b.fill_ground(cx - r, cy - r, cx + r, cy + r, "stone_path", surface="path")
    for x in range(cx - r, cx + r + 1):
        for yy in (cy - r, cy + r):
            if x not in (cx - 1, cx, cx + 1):
                safe(b, "hedge", x, yy)
    for y in range(cy - r, cy + r + 1):
        for xx in (cx - r, cx + r):
            if y not in (cy - 1, cy, cy + 1):
                safe(b, "hedge", xx, y)
    safe(b, "fountain", cx - 1, cy - 1)
    safe(b, "bench", cx - 2, cy + 3); safe(b, "bench", cx + 1, cy + 3)
    safe(b, "bench", cx - 2, cy - 3); safe(b, "bench", cx + 1, cy - 3)
    safe(b, "notice_board", cx - 3, cy + 3); safe(b, "signpost", cx + 3, cy - 3)
    safe(b, "lamp_post", cx - 3, cy - 3); safe(b, "lamp_post", cx + 3, cy + 3)


def build():
    b = ZoneBuilder("scene_village", W, H, base_tile="grass", name="Starting Village")

    # 1) LAKE (SW corner)
    pond(b, 13, 13, 10, 8)                                           # ~x3-23, y5-21

    # 2) STRAIGHT ROADS + the square
    road_v(b, (MAINX - 1, MAINX, MAINX + 1))                         # main N-S street
    road_h(b, (COMM_Y - 1, COMM_Y, COMM_Y + 1))                      # commercial E-W street
    road_h(b, (RES_Y - 1, RES_Y))                                   # residential E-W street
    square(b, MAINX, COMM_Y, r=4)
    b.spawn = [MAINX, COMM_Y - 6]

    # 3) SHOPS clustered at the square (commercial street, open-fronted) ========================
    place_market(b, 36, 63);    connect(b, 36 + 5, 63, COMM_Y + 1)      # W of square
    place_smith(b, 64, 63);     connect(b, 64 + 5, 63, COMM_Y + 1)      # E of square
    place_carpenter(b, 82, 63); connect(b, 82 + 5, 63, COMM_Y + 1)      # E of square

    # 4) HOMES on the residential street (fenced gardens) ======================================
    place_mayor(b, 8, 95);   connect(b, 8 + 9, 88, RES_Y)               # grand estate, far W
    place_cottage(b, 32, 92, npc="miner_down");    connect(b, 36, 88, RES_Y)   # W of the main street
    place_player_house(b, 58, 85)                                       # ⊥ 4-room cottage (like the player's), E
    property_yard(b, 62, 93, 92, 110, 76, side=2, front=5, back=4,
                  fence="fence_picket", gate_id="gate_picket", seed=3); connect(b, 76, 88, RES_Y)
    place_cottage(b, 98, 92, npc="merchant_down"); connect(b, 102, 88, RES_Y)  # far E

    # 5) BOAT STORE on the SW lake, reached by a dirt path up to the commercial street
    place_boat_store(b, 8, 26)
    connect(b, 13, 38, COMM_Y - 1, tile="dirt")

    # 6) TREE CLUMPS in the open areas (where there are no houses) + a few flower patches
    forest = {"tree_oak": 4, "tree_pine": 2, "bush": 1}
    for (a, c, e, f, sd) in [(30, 30, 50, 48, 11), (66, 30, 84, 48, 12), (98, 28, 116, 50, 13),
                             (98, 60, 116, 82, 14), (28, 8, 50, 22, 16), (104, 96, 118, 114, 5),
                             (2, 96, 18, 114, 9), (104, 0, 118, 18, 7)]:
        scatter(b, a, c, e, f, forest, density=0.22, min_spacing=1, seed=sd, clumping=0.85, cluster_radius=4)
    meadow = {"tall_grass": 6, "flower_wild": 2, "bush": 1}
    for (a, c, e, f, sd) in [(34, 50, 82, 58, 21), (34, 78, 56, 84, 22), (90, 60, 116, 82, 23)]:
        scatter(b, a, c, e, f, meadow, density=0.10, min_spacing=2, seed=sd, clumping=0.85)
    for (x0, y0, x1, y1, sd) in [(40, 42, 48, 46, 31), (70, 42, 80, 46, 32), (26, 70, 34, 76, 33),
                                 (96, 66, 110, 72, 34)]:                # flower patches in the open
        flower_patch(b, x0, y0, x1, y1, ["flower_red", "flower_blue", "flower_yellow", "poppy"], 10, seed=sd)
    return b


if __name__ == "__main__":
    b = build()
    out = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "surface", "scene_village.png"))
    render_builder(b, out, scale=4)
    print("LINT:", b.lint() or "0 defects")
    print("warnings:", len(b.warnings), "| missing_art:", b.missing_art())
