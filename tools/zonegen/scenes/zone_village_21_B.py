#!/usr/bin/env python3
"""ZONE — village_21_B: the natural rebuild of the Starting Village.

Spec: docs/product/zones/village_21_B.md. Same macro-geography as village_21 (big
lake SW, mining S, farms+predators N, core at center, spawn ≈(126,123)) composed in
place along ONE bending main road — no blitted square, no ruler lines. Uses the
road-angle system (smooth_paths), shore_dress arcs, the orchard primitive, and the
upgraded plaza().

    python3 tools/zonegen/scenes/zone_village_21_B.py            # build+lint+render to /tmp
    python3 tools/zonegen/scenes/zone_village_21_B.py --save     # also write nakama/data/zones/
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
sys.path.insert(0, HERE)
from zonebuilder import ZoneBuilder                                   # noqa: E402
from render import render_builder                                     # noqa: E402
from features.terrain import (path, lake, shore_dress, smooth_paths, rock_mass,  # noqa: E402
                              forest, stream, route_road, ring_mask, noise_field,
                              _hash_noise, clear_road_margins)
from features.scatter import scatter                                  # noqa: E402
from features.garden import crop_bed, flower_patch, orchard           # noqa: E402
from features.village import plaza, shop_building                     # noqa: E402
from features.yard import fence_rect, property_yard                   # noqa: E402
from features.house import (place_house, styled_rooms, bbox, porch,  # noqa: E402
                            l_house, u_house, courtyard_rect)
from scene_smith import place_smith                                   # noqa: E402
from scene_carpenter import place_carpenter                           # noqa: E402
from scene_market import place_market                                 # noqa: E402
from scene_mayor import place_mayor                                   # noqa: E402
from scene_cottage import place_cottage                               # noqa: E402
from scene_lakeside import place_boat_store                           # noqa: E402
from scene_ecologist import place_ecologist                           # noqa: E402
from scene_fly_farm import place_fly_farm                             # noqa: E402

ZW = ZH = 256
PLAZA = (127, 123)          # the road's main bend; spawn snaps to its S paving


def safe(b, oid, x, y, **k):
    fw, fh = b.footprint(oid)
    return b.place_occupant(oid, x, y, **k) if all(b.is_free(x + dx, y + dy)
                                                   for dx in range(fw) for dy in range(fh)) else False


def spur(b, x0, y0, x1, y1, tile="stone_path"):
    """A short straight 2-wide connector (door/gate → road). Deliberately straight."""
    if x0 == x1:
        for y in range(min(y0, y1), max(y0, y1) + 1):
            for x in (x0 - 1, x0):
                if b.in_bounds(x, y) and b.is_free(x, y):
                    b.set_ground(x, y, tile, surface="path")
    else:
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in (y0 - 1, y0):
                if b.in_bounds(x, y) and b.is_free(x, y):
                    b.set_ground(x, y, tile, surface="path")


def hedgerow(b, x0, y0, x1, y1, seed=0):
    """A bush line separating fields (gappy, not a wall)."""
    import random
    rng = random.Random(seed)
    if abs(x1 - x0) >= abs(y1 - y0):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            if rng.random() < 0.7 and b.is_free(x, y0) and b.surface[y0][x] == "grass":
                safe(b, "bush", x, y0)
    else:
        for y in range(min(y0, y1), max(y0, y1) + 1):
            if rng.random() < 0.7 and b.is_free(x0, y) and b.surface[y][x0] == "grass":
                safe(b, "bush", x0, y)


def build(zone_id="village_21_B", vseed=0):
    b = ZoneBuilder(zone_id, ZW, ZH, base_tile="grass", biome="village",
                    name="Starting Village B", seed=vseed)

    # ================= 1) WATER (always first) =================
    big = lake(b, 46, 48, 52, seed=vseed + 3, shore="sand", reeds=10)   # SW, the lake
    nw = lake(b, 44, 214, 16, seed=vseed + 5, shore="mud", reeds=14)    # NW quiet pond
    se = lake(b, 226, 58, 14, seed=vseed + 7, shore="sand", reeds=8)    # SE pond
    ne = lake(b, 206, 232, 9, seed=vseed + 11, shore="mud", reeds=18)   # NE reedy pond (dragonflies)

    # No two banks alike (angles: 0°=E shore, 90°=N, 180°=W, 270°=S).
    shore_dress(b, big, [
        (225, 315, "sand"),      # S beach
        (315, 30, "reeds"),      # E reed bank
        (135, 225, "forest"),    # W forested bank
    ], seed=vseed + 1)           # N arc stays plain — the boat store + dock live there
    shore_dress(b, nw, [(0, 360, "reeds")], seed=vseed + 2)
    safe(b, "rowboat_beached", 66, 14)    # abandoned on the lake's S beach (story prop)
    shore_dress(b, se, [(180, 300, "sand"), (300, 60, "reeds")], seed=vseed + 4)
    # A stream entering from the WEST edge and feeding the big lake (it continues
    # into the neighbor zone; laid after the lake so it merges into the water).
    stream(b, (0, 76), (28, 66), width=2, seed=vseed + 6, wobble=0.3)

    # ================= 2) ROADS (one bending main + lanes) =================
    # Main road: S edge → quarry fork → THE BEND at the plaza → farm fork → N taper.
    # THE TOWN GRID RULE (roads.md, 2026-06 — after three failed rounds of
    # organic-meets-buildings, Emily's call adopted): wherever anything is BUILT,
    # roads are STRAIGHT horizontal/vertical with L-elbow corners (smooth_paths
    # bevels them). route_road meander lives ONLY in the empty wilds.
    route_road(b, (118, 2), (140, 48), width=4, seed=21)          # WILD: S approach
    # quarry fork -> town: one elbow onto the straight main street
    path(b, (140, 48), (127, 50), width=4, wobble=0.0, seed=22)
    path(b, (127, 50), (127, 116), width=4, wobble=0.0, seed=22)  # MAIN STREET (V)
    path(b, (127, 130), (127, 176), width=4, wobble=0.0, seed=23) # V north of plaza
    path(b, (127, 176), (115, 178), width=4, wobble=0.0, seed=23) # elbow at the farm fork
    path(b, (115, 178), (115, 240), width=3, wobble=0.0, seed=24) # V through the farm belt
    route_road(b, (114, 240), (100, 253), width=3, seed=36)       # WILD: the N taper
    # Lanes (dirt): W to the edge, E past the ecologist, quarry spur, farm lane, lake lane.
    path(b, (120, 127), (60, 127), width=2, tile="dirt", wobble=0.0, seed=25)  # straight past the civic row
    route_road(b, (60, 127), (2, 124), width=2, tile="dirt", seed=25)           # dirt is informal: meanders west
    # E lane: straight past EVERYTHING built (incl. the ecologist — the rule),
    # one elbow up to the cabin's row, wild only beyond it.
    path(b, (134, 124), (206, 124), width=2, tile="dirt", wobble=0.0, seed=26)
    path(b, (206, 124), (206, 144), width=2, tile="dirt", wobble=0.0, seed=26)
    route_road(b, (206, 144), (253, 148), width=2, tile="dirt", seed=27)         # WILD: past the cabin
    path(b, (138, 50), (154, 42), width=2, tile="dirt", wobble=0.12, seed=28)
    path(b, (113, 186), (86, 186), width=2, tile="dirt", wobble=0.0, seed=29)  # straight farm lane
    path(b, (43, 128), (42, 122), width=2, tile="dirt", wobble=0.10, seed=30)
    # (the residential lane is laid in §4 — STRAIGHT, in a scan-verified clear
    # corridor. path() does NOT route around reserved areas, it skip-paints and
    # marches on — never lay it across a built-up band.)

    # ================= 3) THE PLAZA (at the bend) + spawn =================
    px, py = PLAZA
    plaza(b, px, py, r=6, seed=vseed + 9)
    b.spawn = [px - 1, py - 5]      # S paving edge, facing the fountain

    # ================= 4) BUILDINGS (real pieces, clear of roads) =================
    # Civic cluster W of the plaza, fronting the W lane (doors south → gate spurs).
    place_mayor(b, 96, 136)                                  # the town hall (grandest)
    spur(b, 105, 135, 105, 127, tile="stone_path")
    place_market(b, 72, 138)
    spur(b, 77, 137, 77, 127, tile="stone_path")
    # The general store — composed (no piece existed; intent doc lists it
    # separately). Set back 2 from the lane so frontage clutter sits BESIDE the
    # spur, never on the roadway.
    shop_building(b, 52, 140, 62, 151, sign_id="sign_plank", npc="merchant_down",
                  wall="wall_wood", shelf_rows=2)
    for (oid, x, y) in [("barrel", 53, 138), ("crate", 54, 138), ("crate", 55, 138)]:
        safe(b, oid, x, y)                                   # delivery clutter out front
    spur(b, 57, 139, 57, 127, tile="stone_path")

    # Production cluster SE of the plaza on its own short lane off the main road
    # (set back so the smith's ore/coal frontage at oy-2 stays off the roadway).
    path(b, (133, 104), (170, 104), width=2, tile="dirt", wobble=0.0, seed=32)
    place_smith(b, 138, 109)
    spur(b, 143, 108, 143, 103, tile="dirt")
    place_carpenter(b, 156, 109)
    spur(b, 161, 108, 161, 103, tile="dirt")

    # Residential houses NW of the plaza, NORTH of the town hall's compound —
    # VARIED, not three clone boxes: a ⊥ 4-room composer house (basic), the
    # text-grid cottage (picket), and a 3-room bar house (fancy, weathered
    # fence). The lane runs STRAIGHT at y≈154 under their gates and connects
    # SOUTH to the W lane via the clear x≈44 column (the mayor estate + this
    # U-house's yard interlock at x76-116, so no east connection exists).
    # Main-road corridor is x≈117-124 here: yards ≤ x115.
    # The LANDMARK BUDGET (research: most homes simple, ONE showpiece): a U
    # courtyard house (fancy, the street's landmark), an L with a PORCH
    # (mid-tier), and the proven cottage (simple). No clone boxes, no bars.
    specs, front = u_house(78, 160)                  # the showpiece: courtyard U
    place_house(b, styled_rooms(specs, collection="fancy"), front=front)
    tb = bbox(specs)
    from features.yard import styled_yard
    # grand belongs to the MAYOR estate (this slot is too tight for a 7-deep
    # backyard vs the farm lane); the courtyard already crowns this house.
    styled_yard(b, tb[0], tb[1], tb[2], tb[3], 89, style="modest", seed=7)
    court = courtyard_rect(specs)
    if court:
        cx0, cy0, cx1, cy1 = court
        for (oid, x, y) in [("birdbath", (cx0 + cx1) // 2, cy0 + 1),
                            ("poppy", cx0, cy0 + 3), ("chamomile", cx1, cy0 + 5)]:
            safe(b, oid, x, y)
    b.place_player("scholar_down", 89.0, 164)

    place_cottage(b, 49, 162, npc="merchant_down", yard_style="small_plot")  # simple tier, tight plot

    specs2, front2 = l_house(18, 160)                # mid-tier: a true L + porch
    place_house(b, styled_rooms(specs2, collection="basic"), front=front2)
    rb = bbox(specs2)
    styled_yard(b, rb[0], rb[1], rb[2], rb[3], 24, style="modest", seed=8)
    porch(b, specs2)
    b.place_player("farmer_down", 24.0, 164)

    # The residential lane: STRAIGHT at y154 under the three gates (scan-
    # verified clear band — civic backs end y152, yard fronts start y156+),
    # joined SOUTH to the W lane through the clear column at x44. The previous
    # diagonal path((123,131),(12,170)) threaded the L-house's living room,
    # two civic interiors and the mayor's backyard — path() skip-paints
    # reserved cells but marches straight on. NEVER route a lane across a
    # built-up band; lay it in a clear corridor and spur the gates to it.
    path(b, (91, 154), (16, 154), width=2, wobble=0.0, seed=31)
    path(b, (44, 154), (44, 128), width=2, wobble=0.0, seed=31)   # connector to the W lane
    spur(b, 59, 158, 59, 155, tile="stone_path")        # cottage gate (x59) → lane
    smooth_paths(b)   # the road-angle pass: stair-steps → 45° bevels (after ALL roads)

    # Boat store on the big lake's N shore, dock running S into the water (the
    # store hugs the shore so the dock actually crosses onto it).
    place_boat_store(b, 38, 108, dock_len=14)

    # Ecologist in its grove on the E lane (unfenced — the documented exception).
    place_ecologist(b, 188, 146, fenced=False)
    forest(b, 200, 160, 22, 14, density=0.5, seed=vseed + 13)
    forest(b, 172, 130, 14, 10, density=0.45, seed=vseed + 14)

    # ================= 5) FARMS + ORCHARD + FLY FARM + PREDATORS (N) =================
    # Windmill AT the farm fork (the landmark at the decision point) + signpost.
    safe(b, "windmill", 118, 186)
    safe(b, "signpost", 111, 180, surface=None)
    # Three irregular fields, hedgerows between, wheat beside the windmill.
    crop_bed(b, 90, 188, 110, 198, ["plant_wheat"])
    hedgerow(b, 86, 200, 112, 200, seed=41)
    crop_bed(b, 92, 202, 112, 212, ["plant_corn", "plant_corn", "plant_tomato"])
    hedgerow(b, 88, 214, 110, 214, seed=42)
    crop_bed(b, 90, 216, 106, 224, ["plant_tomato", "plant_corn"])
    safe(b, "scarecrow", 100, 193)
    for (x, y) in [(87, 190), (88, 192), (112, 195)]:     # hay bales by the wheat
        safe(b, "hay_bale", x, y)
    # Farmhouse NW of the fields.
    place_cottage(b, 68, 226, npc="farmer_down", yard_style="small_plot")
    for (oid, x, y) in [("compost_bin", 88, 228), ("wheelbarrow", 90, 224), ("water_bucket", 92, 226)]:
        safe(b, oid, x, y)

    # Orchard W of the fields (compact: keeps the wasp buffer geometry).
    orchard(b, 62, 196, 86, 214, seed=vseed + 17)

    # THE FLY FARM (the piece — scenes/scene_fly_farm.py): mini orchard feeding
    # two big pens (compost-bin rows inside; fences genuinely CONTAIN flies), net
    # lines, auto-catchers, trays. The spawn circle centers on the pens below.
    ff_center, ff_r = place_fly_farm(b, 118, 194)
    spur(b, 117, 200, 117, 199, tile="dirt")  # joins the V road at x113-116

    # Wasp nest №1 in the wild-fly buffer between orchard and fly farm + the
    # observation pen (deliberately WOOD: fences don't stop wings — the lesson).
    # North of crop field 3 (iteration 2 overlapped its rows).
    safe(b, "wasp_nest", 104, 230)
    fence_rect(b, 100, 226, 109, 234, gate=(104, 226))
    flower_patch(b, 99, 223, 110, 225, ["chamomile", "clover", "poppy"], 8, seed=43)

    # ================= 6) THE NE FOREST-EDGE GLOOM (centipede country) =================
    forest(b, 168, 236, 26, 14, species=("tree_pine", "tree_pine", "tree_oak"),
           density=0.6, seed=vseed + 19, dirt=True)    # DEEP forest: dark dirt floor
    forest(b, 200, 246, 20, 9, species=("tree_pine",), density=0.55, seed=vseed + 20,
           dirt=True)
    scatter(b, 150, 222, 215, 252, {"fern": 4, "mushroom_cluster": 3, "stump": 1, "bush": 2},
            density=0.10, min_spacing=2, seed=44, clumping=0.85)
    safe(b, "log_pile", 160, 230); safe(b, "stump", 162, 229)
    safe(b, "wasp_nest", 178, 244)                            # nest №2, deep in
    # The carrion gully + the ruined stone pen (the "stone is the answer" story).
    b.fill_ground(163, 233, 167, 235, "dirt")
    safe(b, "bone_pile", 165, 234)
    for (x, y) in [(156, 240), (157, 240), (158, 240), (156, 241), (156, 242)]:
        safe(b, "stone_block", x, y)                          # a broken L of old pen wall

    # ================= 7) MINING (S): SOLID rock masses (the sneak peek of the
    # underworld — filled, not walkable quarries; insides go dark later), the first
    # ABUTTING the big lake's SE shore like the original map. Rails go down FIRST so
    # the masses form around the line — a rail cutting into the rock face.
    for y in range(18, 40):
        safe(b, "mine_rail", 154, y, surface=None)
    safe(b, "mine_cart", 154, 22)
    for y in (20, 28, 36):
        safe(b, "mine_support", 153, y)
    rock_mass(b, 88, 24, 21, 15, seed=vseed + 23)             # OVERLAPS the lake's SE shore
    rock_mass(b, 130, 30, 20, 15, seed=vseed + 24)            # the rail face (touches #1)
    rock_mass(b, 162, 24, 19, 13, seed=vseed + 25)            # third, completing the belt
    for (oid, x, y) in [("tent", 162, 46), ("campfire", 166, 44), ("crate", 165, 47),
                        ("lantern", 163, 44), ("ore_sack", 167, 46)]:
        safe(b, oid, x, y)                                    # the workers' camp at the face
    safe(b, "signpost", 137, 52, surface=None)                              # the quarry fork

    # ================= 8) SE BEEHIVE MEADOW (future-bees hook) =================
    for i, (x, y) in enumerate([(212, 70), (215, 71), (218, 70), (221, 71)]):
        safe(b, "beehive_basic", x, y)
    flower_patch(b, 206, 64, 224, 76, ["lavender", "flower_aster", "clover"], 16, seed=45)

    # ================= 9) WAYFINDING + LAMPS (main road through town only) ========
    for (x, y) in [(119, 126), (134, 125)]:                   # W + E lane mouths
        safe(b, "signpost", x, y, surface=None)

    def flank_road(y, scan=(118, 137)):
        """Lamps at the road's actual edges on row y (the road wobbles)."""
        cells = [x for x in range(*scan) if b.surface[y][x] == "path"]
        if cells:
            for lx in (cells[0] - 1, cells[-1] + 1):
                if b.in_bounds(lx, y) and b.surface[y][lx] != "path":
                    safe(b, "lamp_post", lx, y)
    for y in (98, 110, 136, 148, 160):                        # the town stretch
        flank_road(y)

    # ================= 10) FOREST RING + MEADOW SCATTER (last) =================
    # The RING is a NOISE MASK (research_procgen.md §1: an edge-distance band
    # jittered by fBm — ragged inner edge, natural gaps; roads cut through it
    # automatically because painted/reserved cells are skipped). Tree probability
    # and the dirt floor deepen with the field, so the rim thins inward exactly
    # like a real forest edge.
    # FOREST MASSES, not a donut (2026-06): edge-favoring noise — big distinct
    # forests with real gaps; the world continues past the edges.
    import numpy as np
    fld = noise_field(ZW, ZH, wavelength=28, seed=70)
    nx = 2 * np.arange(ZW) / (ZW - 1) - 1
    ny = 2 * np.arange(ZH) / (ZH - 1) - 1
    dd = 1 - (1 - nx[None, :] ** 2) * (1 - ny[:, None] ** 2)   # 0 center -> 1 edge
    score = fld + 0.45 * dd
    mask = score > 1.02
    placed_trees = []

    def spaced2(x, y):
        return all(abs(x - px) > 1 or abs(y - py) > 1 for (px, py) in placed_trees[-60:])

    for y in range(ZH):
        for x in range(ZW):
            if not mask[y][x] or not b.is_free(x, y) or b.surface[y][x] != "grass":
                continue
            depth = float(fld[y][x])
            r = _hash_noise(x, y, 71)
            if r < 0.30 + depth * 0.35 and spaced2(x, y):
                tree = "tree_pine" if _hash_noise(x, y, 72) < 0.45 else "tree_oak"
                if b.place_occupant(tree, x, y, surface="forest"):
                    placed_trees.append((x, y))
                    if depth > 0.55:
                        b.set_ground(x, y, "dirt")
            elif r > 0.93:
                safe(b, "bush", x, y, surface="forest")
    # Inner accent groves.
    for (cx, cy, rx, ry, sd) in [(70, 150, 12, 9, 56), (160, 80, 13, 9, 57),
                                 (60, 70, 10, 8, 58), (210, 110, 12, 9, 59),
                                 (190, 180, 11, 9, 60), (150, 60, 10, 8, 66)]:
        forest(b, cx, cy, rx, ry, density=0.42, seed=sd)
    # Deliberate clearings get a feature each (the log pile, a mushroom ring, a
    # boulder knoll where the standing stone will land).
    safe(b, "log_pile", 70, 148)
    for (x, y) in [(160, 78), (162, 80), (158, 81)]:
        safe(b, "mushroom_cluster", x, y)
    safe(b, "standing_stone", 196, 168)                   # the lone megalith on the knoll
    # Meadow flowers, clumped, per region; tall-grass ribbons along the roads.
    scatter(b, 4, 100, 60, 170, {"poppy": 3, "clover": 3, "tall_grass": 4, "bush": 1},
            density=0.13, min_spacing=2, seed=61, clumping=0.85)        # W meadow
    scatter(b, 10, 180, 70, 245, {"clover": 3, "chamomile": 2, "tall_grass": 4},
            density=0.12, min_spacing=2, seed=62, clumping=0.85)        # SW→NW meadow
    scatter(b, 185, 60, 235, 100, {"lavender": 3, "flower_aster": 2, "tall_grass": 3},
            density=0.12, min_spacing=2, seed=63, clumping=0.85)        # SE meadow
    scatter(b, 135, 150, 230, 215, {"yarrow": 2, "chamomile": 2, "tall_grass": 4, "bush": 1},
            density=0.11, min_spacing=2, seed=64, clumping=0.85)        # E meadow
    scatter(b, 60, 30, 110, 90, {"tall_grass": 5, "flower_wild": 2},
            density=0.09, min_spacing=2, seed=65, clumping=0.85)        # lakeside fringe
    scatter(b, 130, 115, 175, 175, {"tall_grass": 4, "flower_wild": 2, "chamomile": 1},
            density=0.08, min_spacing=2, seed=67, clumping=0.85)        # core-edge fringe
    for (x0, y0, x1, y1, sd) in [(30, 150, 40, 158, 68), (200, 90, 212, 98, 69),
                                 (140, 168, 152, 176, 75)]:             # flower patches
        flower_patch(b, x0, y0, x1, y1, ["poppy", "flower_blue", "chamomile"], 10, seed=sd)

    # ---- NO DEAD GRASS: little finds in the in-between spaces (a walk should keep
    # passing SOMETHING — berry clumps, a picnic log, an old fence line, glades).
    for (x, y) in [(36, 172), (37, 173), (150, 188), (151, 190), (222, 122), (223, 124),
                   (58, 132), (96, 96), (97, 95)]:
        safe(b, "wild_berry_bush", x, y)
    safe(b, "log_seat", 64, 118); safe(b, "campfire", 66, 117)      # an old picnic spot
    for x in range(176, 188, 2):                                     # a broken fence line
        safe(b, "fence_picket_weathered", x, 119)
    for (x, y) in [(48, 178), (50, 180), (47, 181)]:                 # a mushroom patch
        safe(b, "mushroom_puffball", x, y)
    safe(b, "log_pile", 210, 157)
    safe(b, "stump", 213, 159)
    scatter(b, 120, 60, 180, 100, {"tall_grass": 4, "clover": 2, "bush": 1},
            density=0.10, min_spacing=2, seed=76, clumping=0.85)     # S-center fill
    scatter(b, 60, 110, 115, 135, {"tall_grass": 3, "poppy": 2, "flower_wild": 1},
            density=0.10, min_spacing=2, seed=77, clumping=0.85)     # between core + lake
    scatter(b, 130, 215, 165, 250, {"fern": 2, "tall_grass": 3, "bush": 2},
            density=0.11, min_spacing=2, seed=78, clumping=0.85)     # farm→gloom seam

    # ================= 10.5) FOOD for the 6-species bug ECOLOGY (breeding substrate) =========
    # Populations are BRED, not spawned, so each species needs its food where it lives:
    #  - butterflies BREED on milkweed (host) → milkweed patches inside each nectar meadow
    #  - millipedes eat leaf_litter (forest-floor detritus) → leaf_litter in the NE gloom + a grove
    #  - flies breed on rotten fruit → orchard variety (mixed rot waves) by the farm belt
    flower_patch(b, 18, 120, 44, 148, ["milkweed"], 7, seed=vseed + 81)    # W meadow
    flower_patch(b, 24, 196, 52, 222, ["milkweed"], 6, seed=vseed + 82)    # SW meadow
    flower_patch(b, 204, 60, 226, 82, ["milkweed"], 6, seed=vseed + 83)    # SE beehive meadow
    flower_patch(b, 160, 162, 196, 198, ["milkweed"], 7, seed=vseed + 84)  # E meadow
    scatter(b, 150, 224, 212, 250, {"leaf_litter": 5}, density=0.09, min_spacing=2,
            seed=vseed + 85, clumping=0.85)                                # NE gloom detritus
    scatter(b, 58, 142, 84, 164, {"leaf_litter": 4}, density=0.07, min_spacing=2,
            seed=vseed + 86, clumping=0.8)                                 # SW grove detritus
    for (oid, x, y) in [("tree_plum", 60, 198), ("tree_plum", 84, 210), ("tree_cherry", 64, 212),
                        ("tree_cherry", 82, 198), ("tree_plum", 70, 222), ("tree_cherry", 78, 220)]:
        safe(b, oid, x, y)                                                 # fruit variety by the orchard

    # The visual-clipping guarantee: nothing tall within 1 cell of a road.
    cleared = clear_road_margins(b)
    if cleared:
        print(f"  clear_road_margins: removed {len(cleared)} road-margin plants")

    # ================= 11) BUG SPAWNING — BREEDING-DRIVEN, habitat-clustered =================
    # MODEL (2026-06, the real-zone rebuild): populations grow by BREEDING on the food placed above and
    # decline by natural death/predation/starvation — NOT by a spawner pump. So:
    #  - spawn_interval is a RARE wild-immigration TRICKLE (thousands of sim-sec; 1 game-day = 840s), not
    #    the 45s pump that masked everything. `initial` seeds the breeding stock.
    #  - WEIGHTED spawn areas: high-weight habitat circles at each species' food + a low-weight zone-wide
    #    wild-card (~3:1) → mostly clusters at its habitat, a few wander in anywhere; survival sorts the rest.
    #  - NO culls / drought bands (nothing deletes bugs). The ONLY Director action is the `min_population`
    #    re-seed floor (anti-extinction ADD). max_population is a generous safety ceiling, not the target.
    #  - wasps are nest-driven: hand-placed nests (104,230 / 178,244) seed colonies; thriving ones found
    #    daughter hives beside distant prey (findNestSiteWithPrey).
    HAB, WILD = 2.0, 1.0  # habitat-circle vs zone-wide weights (predators/decomposers use 3:1, set inline)
    b.bug_spawning = {
        "species_caps": {
            # prey base — flies breed on the orchard/fly-farm/compost rot
            "fly_common":       {"initial": 30, "max": 200, "spawn_interval": 2000.0,
                                 "swarm_size": 8, "max_population": 1500, "min_population": 12},
            # nectar/host — butterflies breed on milkweed in the meadows
            "butterfly_meadow": {"initial": 20, "max": 140, "spawn_interval": 3000.0,
                                 "swarm_size": 6, "max_population": 800, "min_population": 10},
            # predators (nest / hunter) + decomposers — small populations, rare trickle, low floor
            "wasp_common":      {"initial": 4, "max": 12, "spawn_interval": 9000.0,
                                 "swarm_size": 4, "max_population": 120, "min_population": 3, "max_nests": 5},
            "centipede_garden": {"initial": 8, "max": 40, "spawn_interval": 6000.0,
                                 "swarm_size": 2, "max_population": 140, "min_population": 3},
            "millipede":        {"initial": 10, "max": 60, "spawn_interval": 6000.0,
                                 "swarm_size": 2, "max_population": 200, "min_population": 3},
            "beetle_carrion":   {"initial": 6, "max": 40, "spawn_interval": 6000.0,
                                 "swarm_size": 2, "max_population": 140, "min_population": 2},
        },
        "spawn_areas": [
            # FLY — orchard + fly farm + farmhouse compost (the searchable hotspots) + sparse wild
            {"id": "fly_orchard",  "species": ["fly_common"], "type": "circle", "cx": 74, "cy": 205, "radius": 14, "weight": HAB},
            {"id": "fly_farm",     "species": ["fly_common"], "type": "circle", "cx": ff_center[0], "cy": ff_center[1], "radius": ff_r, "weight": HAB},
            {"id": "fly_compost",  "species": ["fly_common"], "type": "circle", "cx": 88, "cy": 228, "radius": 10, "weight": HAB},
            {"id": "fly_wild",     "species": ["fly_common"], "type": "zone", "weight": WILD},
            # BUTTERFLY — the four nectar+milkweed meadows + sparse wild
            {"id": "bf_meadow_w",  "species": ["butterfly_meadow"], "type": "circle", "cx": 30, "cy": 134, "radius": 24, "weight": HAB},
            {"id": "bf_meadow_sw", "species": ["butterfly_meadow"], "type": "circle", "cx": 38, "cy": 209, "radius": 22, "weight": HAB},
            {"id": "bf_beehive",   "species": ["butterfly_meadow"], "type": "circle", "cx": 215, "cy": 71, "radius": 20, "weight": HAB},
            {"id": "bf_meadow_e",  "species": ["butterfly_meadow"], "type": "circle", "cx": 178, "cy": 180, "radius": 28, "weight": HAB},
            {"id": "bf_wild",      "species": ["butterfly_meadow"], "type": "zone", "weight": WILD},
            # WASP — at the two nests (near the farm-belt fly prey) + sparse wild
            {"id": "wasp_n1",      "species": ["wasp_common"], "type": "circle", "cx": 104, "cy": 230, "radius": 12, "weight": HAB},
            {"id": "wasp_n2",      "species": ["wasp_common"], "type": "circle", "cx": 178, "cy": 244, "radius": 12, "weight": HAB},
            {"id": "wasp_wild",    "species": ["wasp_common"], "type": "zone", "weight": WILD},
            # CENTIPEDE — the NE forest gloom (hunts flies that stray in) + sparse wild
            {"id": "cent_gloom",   "species": ["centipede_garden"], "type": "circle", "cx": 178, "cy": 240, "radius": 16, "weight": 3.0},
            {"id": "cent_wild",    "species": ["centipede_garden"], "type": "zone", "weight": WILD},
            # MILLIPEDE — the leaf-litter detritus (gloom + SW grove) + sparse wild
            {"id": "milli_gloom",  "species": ["millipede"], "type": "circle", "cx": 178, "cy": 238, "radius": 18, "weight": 3.0},
            {"id": "milli_grove",  "species": ["millipede"], "type": "circle", "cx": 70, "cy": 152, "radius": 14, "weight": 2.0},
            {"id": "milli_wild",   "species": ["millipede"], "type": "zone", "weight": WILD},
            # BEETLE — the carrion gully + predator areas (eats dead_<bug> corpses) + sparse wild
            {"id": "beetle_gully", "species": ["beetle_carrion"], "type": "circle", "cx": 165, "cy": 234, "radius": 16, "weight": 3.0},
            {"id": "beetle_wild",  "species": ["beetle_carrion"], "type": "zone", "weight": WILD},
        ],
    }
    return b


if __name__ == "__main__":
    b = build()
    print("LINT:", *(["0 defects ✓"] if not (defects := b.lint()) else ["\n  - " + "\n  - ".join(defects)]))
    print("warnings:", len(b.warnings), "| missing_art:", b.missing_art())
    issues = b.validate()
    print("validate:", issues or "ok")
    out = "/tmp/zone_b_full.png"
    render_builder(b, out, scale=3)
    print("render ->", out)
    if "--save" in sys.argv:
        out_dir = b.save()
        # save() writes row/col 0,0 — patch to the world-grid slot (2,1).
        import json
        zj = os.path.join(out_dir, "zone.json")
        cfg = json.load(open(zj))
        cfg["row"], cfg["col"] = 2, 1
        json.dump(cfg, open(zj, "w"), indent=2)
        print("saved ->", out_dir)
        # THE VISIBLE VILLAGE: real-art renders land in the previews on every
        # save (full overview + readable region crops) — they can never go
        # stale relative to the shipped chunks.
        zdir = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews",
                                            "zones", "village_21_B"))
        os.makedirs(zdir, exist_ok=True)
        render_builder(b, os.path.join(zdir, "full.png"), scale=2)
        for nm, bounds in [("plaza", (100, 100, 165, 150)),
                           ("residential", (10, 140, 120, 195)),
                           ("fly_farm", (105, 185, 160, 245)),
                           ("farms_orchard", (55, 175, 120, 240)),
                           ("lake_boatstore", (5, 55, 105, 125)),
                           ("mining", (80, 5, 200, 60))]:
            render_builder(b, os.path.join(zdir, f"{nm}.png"), scale=5, bounds=bounds)
        print("zone renders ->", zdir)
