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
from features.terrain import path, lake, shore_dress, smooth_paths, rock_patch, forest  # noqa: E402
from features.scatter import scatter                                  # noqa: E402
from features.garden import crop_bed, flower_patch, orchard           # noqa: E402
from features.village import plaza, shop_building                     # noqa: E402
from features.yard import fence_rect                                  # noqa: E402
from scene_smith import place_smith                                   # noqa: E402
from scene_carpenter import place_carpenter                           # noqa: E402
from scene_market import place_market                                 # noqa: E402
from scene_mayor import place_mayor                                   # noqa: E402
from scene_cottage import place_cottage                               # noqa: E402
from scene_lakeside import place_boat_store                           # noqa: E402
from scene_ecologist import place_ecologist                           # noqa: E402

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
            if rng.random() < 0.7 and b.is_free(x, y0):
                safe(b, "bush", x, y0)
    else:
        for y in range(min(y0, y1), max(y0, y1) + 1):
            if rng.random() < 0.7 and b.is_free(x0, y):
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
    shore_dress(b, se, [(180, 300, "sand"), (300, 60, "reeds")], seed=vseed + 4)

    # ================= 2) ROADS (one bending main + lanes) =================
    # Main road: S edge → quarry fork → THE BEND at the plaza → farm fork → N taper.
    path(b, (118, 2), (140, 48), width=4, edge_tile="dirt", wobble=0.10, seed=21, taper_ends=6)
    path(b, (140, 48), (128, 116), width=4, edge_tile="dirt", wobble=0.10, seed=22)
    path(b, (126, 130), (114, 180), width=4, edge_tile="dirt", wobble=0.10, seed=23)
    path(b, (114, 180), (100, 253), width=3, edge_tile="dirt", wobble=0.12, seed=24, taper_ends=10)
    # Lanes (dirt): W to the edge, E past the ecologist, quarry spur, farm lane, lake lane.
    path(b, (120, 124), (2, 130), width=2, tile="dirt", wobble=0.16, seed=25, taper_ends=8)
    path(b, (134, 124), (192, 142), width=2, tile="dirt", wobble=0.16, seed=26)
    path(b, (192, 142), (253, 148), width=2, tile="dirt", wobble=0.16, seed=27, taper_ends=8)
    path(b, (138, 50), (154, 42), width=2, tile="dirt", wobble=0.12, seed=28)
    path(b, (114, 182), (88, 196), width=2, tile="dirt", wobble=0.15, seed=29)
    path(b, (47, 128), (44, 112), width=2, tile="dirt", wobble=0.10, seed=30)
    # (the residential lane is laid AFTER its cottages — see §4: path() routes
    # around their reserved yards, so the lane hugs the fences naturally)

    # ================= 3) THE PLAZA (at the bend) + spawn =================
    px, py = PLAZA
    plaza(b, px, py, r=6, seed=vseed + 9)
    b.spawn = [px - 1, py - 5]      # S paving edge, facing the fountain

    # ================= 4) BUILDINGS (real pieces, clear of roads) =================
    # Civic cluster W of the plaza, fronting the W lane (doors south → gate spurs).
    place_mayor(b, 96, 134)                                  # the town hall (grandest)
    spur(b, 105, 133, 105, 128, tile="stone_path")
    place_market(b, 72, 134)
    spur(b, 77, 133, 77, 129, tile="stone_path")
    # The general store — composed (no piece existed; intent doc lists it separately).
    shop_building(b, 52, 134, 62, 145, sign_id="sign_plank", npc="merchant_down",
                  wall="wall_wood", shelf_rows=2)
    for (oid, x, y) in [("barrel", 53, 132), ("crate", 55, 132), ("crate", 56, 132)]:
        safe(b, oid, x, y)                                   # delivery clutter out front
    spur(b, 57, 133, 57, 130, tile="stone_path")

    # Production cluster SE of the plaza on its own short lane off the main road.
    path(b, (133, 106), (170, 104), width=2, tile="dirt", wobble=0.10, seed=32)
    place_smith(b, 138, 108)
    spur(b, 143, 107, 143, 106, tile="dirt")
    place_carpenter(b, 156, 108)
    spur(b, 161, 107, 161, 106, tile="dirt")

    # Residential cottages NW of the plaza, NORTH of the town hall's compound
    # (the hall + yard spans ≈(92-117, 127-151) — iteration 2 put cottage 1 right
    # on it). THEN the lane is routed past their gates — path() flows around the
    # reserved yards, hugging the fences.
    place_cottage(b, 100, 158, npc="farmer_down")   # the main road slants NW: its
    place_cottage(b, 84, 162, npc="merchant_down")  # corridor is x≈117-124 at these
    place_cottage(b, 68, 166, npc="scholar_down")   # rows — yards stay ≤ x115
    path(b, (123, 131), (66, 160), width=2, wobble=0.12, seed=31)
    for gx, gy in ((104, 152), (88, 156), (72, 160)):   # gate → lane spurs
        spur(b, gx, gy, gx, gy - 4, tile="stone_path")
    smooth_paths(b)   # the road-angle pass: stair-steps → 45° bevels (after ALL roads)

    # Boat store on the big lake's N shore, dock running S into the water (the
    # store hugs the shore so the dock actually crosses onto it).
    place_boat_store(b, 40, 103, dock_len=18)

    # Ecologist in its grove on the E lane (unfenced — the documented exception).
    place_ecologist(b, 188, 146, fenced=False)
    forest(b, 200, 160, 22, 14, density=0.5, seed=vseed + 13)
    forest(b, 172, 130, 14, 10, density=0.45, seed=vseed + 14)

    # ================= 5) FARMS + ORCHARD + FLY FARM + PREDATORS (N) =================
    # Windmill AT the farm fork (the landmark at the decision point) + signpost.
    safe(b, "windmill", 117, 184)
    safe(b, "signpost", 113, 178)
    # Three irregular fields, hedgerows between, wheat beside the windmill.
    crop_bed(b, 90, 188, 110, 198, ["plant_wheat"])
    hedgerow(b, 86, 200, 112, 200, seed=41)
    crop_bed(b, 92, 202, 112, 212, ["plant_corn", "plant_corn", "plant_tomato"])
    hedgerow(b, 88, 214, 110, 214, seed=42)
    crop_bed(b, 96, 216, 114, 224, ["plant_tomato", "plant_corn"])
    safe(b, "scarecrow", 100, 193)
    # Farmhouse NW of the fields.
    place_cottage(b, 70, 226, npc="farmer_down")
    for (oid, x, y) in [("compost_bin", 88, 228), ("wheelbarrow", 90, 224), ("water_bucket", 92, 226)]:
        safe(b, oid, x, y)

    # Orchard W of the fields (compact: keeps the wasp buffer geometry).
    orchard(b, 62, 196, 86, 214, seed=vseed + 17)

    # Fly farm E of the main road (a landscape, with FAILURE evidence).
    b.fill_ground(116, 200, 126, 210, "dirt")                 # darkened worked soil
    for (x, y) in [(118, 202), (122, 206), (119, 209)]:
        safe(b, "compost_pile", x, y)
    for (x, y) in [(117, 200), (125, 200), (117, 210), (125, 210)]:
        safe(b, "net_post", x, y)
    for (x, y) in [(120, 200), (121, 210)]:
        safe(b, "fly_netting", x, y)
    for (x, y) in [(118, 205), (124, 203)]:
        safe(b, "bait_basket", x, y)
    for (x, y) in [(120, 204), (123, 208)]:
        safe(b, "collection_tray", x, y)
    safe(b, "broken_net", 126, 207)                           # failure reads
    safe(b, "broken_net", 116, 203)
    b.set_ground(121, 203, "water_shallow")                   # a puddle (1 cell, walk-around)

    # Wasp nest №1 in the wild-fly buffer between orchard and fly farm + the
    # observation pen (deliberately WOOD: fences don't stop wings — the lesson).
    # North of crop field 3 (iteration 2 overlapped its rows).
    safe(b, "wasp_nest", 98, 232)
    fence_rect(b, 94, 228, 103, 236, gate=(98, 228))
    flower_patch(b, 93, 225, 104, 227, ["chamomile", "clover", "poppy"], 8, seed=43)

    # ================= 6) THE NE FOREST-EDGE GLOOM (centipede country) =================
    forest(b, 168, 236, 26, 14, species=("tree_pine", "tree_pine", "tree_oak"),
           density=0.6, seed=vseed + 19)
    forest(b, 200, 246, 20, 9, species=("tree_pine",), density=0.55, seed=vseed + 20)
    scatter(b, 150, 222, 215, 252, {"fern": 4, "mushroom_cluster": 3, "stump": 1, "bush": 2},
            density=0.10, min_spacing=2, seed=44, clumping=0.85)
    safe(b, "log_fallen", 160, 230)
    safe(b, "wasp_nest", 178, 244)                            # nest №2, deep in
    # The carrion gully + the ruined stone pen (the "stone is the answer" story).
    b.fill_ground(163, 233, 167, 235, "dirt")
    safe(b, "bone_pile", 165, 234)
    for (x, y) in [(156, 240), (157, 240), (158, 240), (156, 241), (156, 242)]:
        safe(b, "stone_block", x, y)                          # a broken L of old pen wall

    # ================= 7) MINING (S): terraced quarry + rails + camp =================
    rock_patch(b, 152, 38, 16, seed=vseed + 23)
    rock_patch(b, 172, 52, 11, seed=vseed + 24)
    rock_patch(b, 136, 26, 9, seed=vseed + 25)
    for y in range(20, 42, 1):                                # the rail line into the quarry
        safe(b, "mine_rail", 154, y, surface=None)
    safe(b, "mine_cart", 154, 24)
    for y in (22, 30, 38):
        safe(b, "mine_support", 153, y)
    for (oid, x, y) in [("tent", 162, 46), ("campfire", 166, 44), ("crate", 165, 47),
                        ("lantern", 163, 44), ("ore_sack", 167, 46)]:
        safe(b, oid, x, y)                                    # the workers' camp
    safe(b, "signpost", 137, 52)                              # the quarry fork

    # ================= 8) SE BEEHIVE MEADOW (future-bees hook) =================
    for i, (x, y) in enumerate([(212, 70), (215, 71), (218, 70), (221, 71)]):
        safe(b, "beehive_basic", x, y)
    flower_patch(b, 206, 64, 224, 76, ["lavender", "flower_aster", "clover"], 16, seed=45)

    # ================= 9) WAYFINDING + LAMPS (main road through town only) ========
    for (x, y) in [(119, 126), (134, 125)]:                   # W + E lane mouths
        safe(b, "signpost", x, y, surface=None)

    def flank_road(y, scan=(112, 142)):
        """Lamps at the road's actual edges on row y (the road wobbles)."""
        cells = [x for x in range(*scan) if b.surface[y][x] == "path"]
        if cells:
            safe(b, "lamp_post", cells[0] - 1, y)
            safe(b, "lamp_post", cells[-1] + 1, y)
    for y in (98, 110, 136, 148, 160):                        # the town stretch
        flank_road(y)

    # ================= 10) FOREST RING + MEADOW SCATTER (last) =================
    # The RING is real forest MASSES (a chain of overlapping blobs around the rim,
    # gaps only at the four road mouths) — scatter alone read as speckle, not a
    # boundary. Density-gradient: the masses are the wall, the scatter between
    # them is the fade.
    rim = [
        # south rim (gap at the main road mouth x≈110-126)
        (24, 8, 22, 9), (66, 8, 20, 8), (150, 8, 20, 9), (196, 8, 22, 9), (242, 10, 16, 9),
        # east rim (gap at the E lane mouth y≈140-156)
        (246, 40, 14, 12), (244, 86, 13, 14), (246, 120, 12, 9),
        (246, 178, 13, 13), (244, 215, 14, 12),
        # north rim (gap at the main road mouth x≈92-108)
        (240, 248, 18, 8), (140, 250, 22, 7), (60, 250, 24, 7), (16, 248, 16, 8),
        # west rim above the lake (the lake itself walls the SW)
        (8, 130, 10, 12), (10, 168, 11, 13), (8, 242, 12, 8),
    ]
    for i, (cx, cy, rx, ry) in enumerate(rim):
        forest(b, cx, cy, rx, ry, density=0.55, seed=70 + i)
    ring = {"tree_oak": 4, "tree_pine": 3, "bush": 2}
    # The fade between the masses (sparser, clumped).
    for (x0, y0, x1, y1, sd) in [(0, 0, 255, 20, 51), (0, 235, 255, 255, 52),
                                 (0, 100, 18, 234, 53), (234, 21, 255, 234, 54)]:
        scatter(b, x0, y0, x1, y1, ring, density=0.12, min_spacing=3, seed=sd,
                clumping=0.85, cluster_radius=5)
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
    for (x, y) in [(196, 168), (197, 169), (195, 169)]:   # a cairn on the knoll —
        safe(b, "stone_block", x, y)                      # standing_stone lands here (V4)
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

    # ================= 11) BUG SPAWNING (habitat-tied circles) =================
    b.bug_spawning = {
        "species_caps": {
            "fly_common":       {"initial": 40, "max": 75, "spawn_interval": 45.0,
                                 "swarm_size": 2, "max_population": 400},
            "butterfly_meadow": {"initial": 15, "max": 50, "spawn_interval": 90.0,
                                 "max_population": 300},
            "wasp_common":      {"initial": 0, "max": 3, "spawn_interval": 9999.0,
                                 "max_population": 12},
            "centipede_garden": {"initial": 2, "max": 3, "spawn_interval": 600.0,
                                 "swarm_size": 2, "max_population": 8},
        },
        "spawn_areas": [
            {"id": "zone_wide", "species": ["fly_common"], "type": "zone"},
            {"id": "fly_farm", "species": ["fly_common"], "type": "circle",
             "cx": 121, "cy": 205, "radius": 14},
            {"id": "beehive_meadow", "species": ["butterfly_meadow"], "type": "circle",
             "cx": 215, "cy": 72, "radius": 20},
            {"id": "meadow_w", "species": ["butterfly_meadow"], "type": "circle",
             "cx": 28, "cy": 134, "radius": 28},
            {"id": "meadow_sw", "species": ["butterfly_meadow"], "type": "circle",
             "cx": 30, "cy": 196, "radius": 22},
            {"id": "ne_gloom", "species": ["centipede_garden"], "type": "circle",
             "cx": 170, "cy": 238, "radius": 12},
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
