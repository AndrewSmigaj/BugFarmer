#!/usr/bin/env python3
"""ZONE — BEE MEADOW (2,0 · bee_meadow_20): the EASY flower coast west of the village.
Design contract: docs/product/zones/bee_meadow_20.md. Geometry contract with village_21_B:
the ROAD exits our EAST edge at y=124 (their west lane reaches (2,124)); the STREAM exits
east at y=76 (they declare it entering at (0,76), feeding their lake).

Compose-in-place (the zone_village_21_B pattern): sea/beach → stream + lakes → roads +
BRIDGES (smooth once) → the bee farm + the fishing hamlet (the REAL pieces) → gardens →
meadows/forests/scatter → bug_spawning → grid/neighbors → save.

  python3 tools/zonegen/scenes/zone_bee_meadow_20.py           # build + lint + render preview
  python3 tools/zonegen/scenes/zone_bee_meadow_20.py --save    # also write nakama/data/zones/
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder                                    # noqa: E402
from render import render_builder                                      # noqa: E402
from features.terrain import (stream, lake, pond, forest, path,        # noqa: E402
                              smooth_paths, bridge, shore_dress)
from features.garden import flower_patch                               # noqa: E402
from features.scatter import scatter                                   # noqa: E402
from scene_beach_cove import sea_edge, dress_beach, place_beach_landmarks  # noqa: E402
from scene_fishing_docks import place_fishing_hamlet, _dock            # noqa: E402
from scene_beekeeper_cottage import place_bee_farm                     # noqa: E402

W = H = 256
ROAD_Y = 124   # east-edge road row (village contract)
STREAM_Y = 76  # east-edge stream row (village contract)


def _water_span(b, fixed, lo, hi, *, row=True):
    """The [min,max] extent of water cells on a row (row=True: y=fixed, x in lo..hi) or a column.
    Returns None if the scan line holds no water — the bridge caller must then rethink."""
    cells = []
    for v in range(lo, hi + 1):
        x, y = (v, fixed) if row else (fixed, v)
        if b.in_bounds(x, y) and b.surface[y][x] == "water":
            cells.append(v)
    return (min(cells), max(cells)) if cells else None


def build():
    b = ZoneBuilder("bee_meadow_20", W, H, base_tile="grass", seed=20, name="Bee Meadow",
                    biome="meadow")
    rng = random.Random(20)

    # ---- 1. WATER ----------------------------------------------------------
    # The SEA (west boundary): coves at the hamlet bay (y≈64), mid-coast (y≈141) and the
    # north beach (y≈205); the tease island off the point between the first two.
    beach = sea_edge(b, water_w=11, sand_w=6,
                     coves=((0.25, 9), (0.55, 8), (0.80, 11)), island=(0.40, 4), seed=7)
    # The HAMLET BAY: a lake blob merged into the SW cove so the water reaches inland far
    # enough to float real docks (lake() flows into existing water).
    lake(b, 34, 56, 13, seed=21, shore="sand", reeds=8)

    # The STREAM: rises at a NW spring pondlet, descends south-east through the west-center,
    # then runs east to the village at STREAM_Y. Laid as chained segments so the course is
    # controlled (one road crossing, one footpath crossing) but still meanders.
    pond(b, 38, 208, 5, 4, seed=22)                       # the spring
    for seg_start, seg_end in [((38, 204), (58, 172)), ((58, 172), (76, 142)),
                               ((76, 142), (92, 108)), ((92, 108), (150, 84)),
                               ((150, 84), (255, STREAM_Y))]:
        stream(b, seg_start, seg_end, width=2, seed=23, wobble=0.25)
    # THE EDGE SEAM: stream() stops within a cell of its endpoint — stamp the last column so the
    # water actually TOUCHES x=255 at the contract row (the village declares it entering at (0,76)).
    for sx in (253, 254, 255):
        for sy in (STREAM_Y - 1, STREAM_Y, STREAM_Y + 1):
            b.set_ground(sx, sy, "water_shallow" if sy != STREAM_Y else "water_deep", surface="water")
            b.reserve(sx, sy, surface="water")

    # The BIG FISHING LAKE (south-center) + the NE pond.
    fl = lake(b, 152, 42, 15, seed=24, shore="sand", reeds=14)
    shore_dress(b, fl, [(150, 260, "sand"), (260, 40, "reeds"), (40, 150, "forest")], seed=25)
    pond(b, 212, 204, 7, 5, seed=26)

    # ---- 2. ROADS + BRIDGES (then smooth ONCE) ------------------------------
    # Main road: east edge → west, bridging the stream where it crosses ROAD_Y.
    span = _water_span(b, ROAD_Y, 60, 130)
    assert span, "the stream must cross the road row"
    east_bank, west_bank = span[1] + 1, span[0] - 1
    path(b, (255, ROAD_Y), (east_bank + 2, ROAD_Y), width=2, tile="dirt", wobble=0.18, seed=27)
    for by in (ROAD_Y, ROAD_Y + 1):                       # a 2-wide deck matching the road
        bridge(b, (east_bank + 1, by), (west_bank - 1, by))
    path(b, (west_bank - 1, ROAD_Y), (52, 104), width=2, tile="dirt", wobble=0.14, seed=28,
         taper_ends=4)                                     # west leg dwindles toward the hamlet

    # The farm spur: north from the road to Maren's gate (the farm sits north of the road) —
    # stop a cell short of the fence row, then a single doorstep cell kisses the gate.
    path(b, (137, ROAD_Y + 1), (137, 142), width=2, tile="dirt", wobble=0.05, seed=29)
    b.set_ground(137, 143, "dirt", surface="path")

    # The hamlet spur: from the west leg AROUND cottage B (x48-62, y81-92), down the gap
    # between the two cottages to the dock head — low wobble so it stays in the gap.
    path(b, (52, 104), (43, 97), width=2, tile="dirt", wobble=0.06, seed=30)
    path(b, (43, 97), (42, 76), width=1, tile="dirt", wobble=0.04, seed=30, taper_ends=2)

    # The north-band footpath: up the west side, bridging the stream's descent.
    cspan = _water_span(b, 56, 140, 200, row=False)
    if cspan:
        s0, s1 = cspan
        path(b, (56, 128), (56, s0 - 1), width=1, tile="dirt", wobble=0.08, seed=31)
        bridge(b, (56, s0 - 1), (56, s1 + 1))
        path(b, (56, s1 + 1), (60, 196), width=1, tile="dirt", wobble=0.12, seed=32, taper_ends=4)
    smooth_paths(b)

    # ---- 3. BUILDINGS (the real pieces) -------------------------------------
    place_bee_farm(b, 100, 124)          # apiary x124-150 y144-162, cottage NW, gate at (137,144)
    place_fishing_hamlet(b, 24, 70)      # cottages above the bay, dock south into it

    # The lake dock: a stub pier + moored boat on the fishing lake's north shore.
    _dock(b, 150, 60, max_len=9)

    # ---- 4. MEADOWS, FORESTS, WILDLIFE ANCHORS ------------------------------
    common = ["flower_red", "flower_blue", "flower_yellow", "flower_wild", "clover", "dandelion"]
    rarer = ["lavender", "chamomile", "poppy", "sunflower"]
    # The great meadows: east of the farm, the road margins, and the north band.
    flower_patch(b, 160, 100, 250, 150, common + rarer, 90, seed=33)
    flower_patch(b, 170, 155, 246, 195, common, 60, seed=34)
    flower_patch(b, 70, 150, 118, 200, common + rarer, 40, seed=35)
    flower_patch(b, 96, 88, 150, 118, common, 30, seed=36)
    flower_patch(b, 60, 210, 130, 244, common, 36, seed=37)
    flower_patch(b, 66, 16, 140, 58, common, 34, seed=46)   # the south meadow (below the bay road)
    # Milkweed clumps (butterfly breeding hosts).
    for mx, my in [(180, 160), (183, 158), (186, 162), (84, 176), (87, 174), (90, 178)]:
        if b.is_free(mx, my):
            b.place_occupant("milkweed", mx, my)

    # Forests: the NE stand, the stream-bank strip, the north-west band.
    forest(b, 214, 172, 26, 18, seed=38, density=0.5)
    forest(b, 176, 96, 18, 8, seed=39, density=0.45)
    forest(b, 42, 182, 16, 12, seed=40, density=0.5)
    # Forest floor: leaf litter (millipede food) + mushrooms in each stand.
    for (x0, y0, x1, y1, sd) in [(190, 156, 240, 190, 41), (160, 88, 194, 104, 42),
                                 (28, 172, 58, 194, 43)]:
        scatter(b, x0, y0, x1, y1,
                {"leaf_litter": 5, "mushroom_brown": 2, "fern": 3, "tall_grass": 2},
                density=0.05, min_spacing=2, seed=sd, surfaces=("grass",))

    # WILD HIVES + WASP NESTS are ECOLOGY ANCHORS — never skip one silently; spiral to the
    # nearest free grass cell if the exact spot got taken by a tree/flower.
    def _place_near(oid, x, y, r=5):
        for d in range(r + 1):
            for dy in range(-d, d + 1):
                for dx in range(-d, d + 1):
                    if max(abs(dx), abs(dy)) == d and b.in_bounds(x + dx, y + dy) \
                       and b.surface[y + dy][x + dx] == "grass" and b.is_free(x + dx, y + dy):
                        return b.place_occupant(oid, x + dx, y + dy)
        raise SystemExit(f"no free cell near ({x},{y}) for {oid} — rework the layout")

    # The free colonies (each auto-founds; the flowers nearby are their economy).
    for hx, hy in [(168, 152), (206, 118), (78, 202)]:
        _place_near("bee_hive_wild", hx, hy)
    # The raiders, at forest edges AWAY from the farm (this is the EASY zone).
    for wx, wy in [(232, 158), (186, 90)]:
        _place_near("wasp_nest", wx, wy)

    # The beach set + the coast's NAMED features: the shipwreck at the mid-coast cove, the
    # picnic spot on the north beach, buoys off the cove mouths, the bottle on the island.
    dress_beach(b, beach, seed=44, density=0.05)
    place_beach_landmarks(b, beach, wreck_y=141, picnic_y=206, buoy_ys=(64, 141),
                          bottle_island=(5, 102))

    # WAYFINDING — signposts + light at the junctions (arriving must read instantly):
    # the east entrance, the stream bridge, the farm spur, the hamlet fork.
    for sx, sy in [(249, ROAD_Y + 3), (135, ROAD_Y + 3), (57, 108)]:
        if b.is_free(sx, sy) and b.surface[sy][sx] == "grass":
            b.place_occupant("signpost", sx, sy)
    for lx, ly in [(247, ROAD_Y - 2), (98, ROAD_Y - 2)]:
        if b.is_free(lx, ly):
            b.place_occupant("lamp_post", lx, ly)

    # WATER DRESSING — reeds wherever shallow water meets grass (stream banks, lake rims,
    # the ponds; the sea keeps its own beach treatment), lily pads on the calm lake shallows.
    rng_w = random.Random(47)
    reeds_n = pads_n = 0
    for y in range(4, H - 4):
        for x in range(30, W - 4):
            if b.ground[y][x] != "water_shallow" or not b.in_bounds(x, y):
                continue
            nb_grass = any(b.in_bounds(x + dx, y + dy) and b.surface[y + dy][x + dx] == "grass"
                           for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if nb_grass and reeds_n < 90 and rng_w.random() < 0.05:
                b.reserved[y][x] = False
                if b.place_occupant("reeds", x, y, surface="water"):
                    reeds_n += 1
                b.reserve(x, y, surface="water")
            elif not nb_grass and pads_n < 10 and 100 < x < 240 and rng_w.random() < 0.02:
                b.reserved[y][x] = False
                if b.place_occupant("lily_pad", x, y, surface="water"):
                    pads_n += 1
                b.reserve(x, y, surface="water")

    # The NE pond is the QUIET SPOT: a bench facing the water under the evening fireflies.
    for bx, by in [(220, 198), (221, 197), (219, 197)]:
        if b.is_free(bx, by):
            b.place_occupant("bench", bx, by)
            break

    # The south-east fills: a wild-berry thicket + driftwood washed up the stream mouth.
    for tx, ty in [(214, 54), (217, 56), (212, 57), (219, 53), (215, 50)]:
        if b.is_free(tx, ty):
            b.place_occupant("wild_berry_bush", tx, ty)
    for dx, dy in [(246, 72), (240, 80)]:
        if b.in_bounds(dx, dy) and b.surface[dy][dx] == "grass" and b.is_free(dx, dy):
            b.place_occupant("driftwood", dx, dy)

    scatter(b, 60, 40, 250, 246,
            {"bush": 3, "tall_grass": 5, "wild_berry_bush": 1, "dandelion": 2, "clover": 2},
            density=0.02, min_spacing=3, seed=45, surfaces=("grass",))

    # ---- 5. BUG SPAWNING ----------------------------------------------------
    b.bug_spawning = {
        "static": False,
        "species_caps": {
            # Bees are NEST-FOUNDED ONLY: never free-spawned, never Director-reseeded (min 0).
            # 3 wild hives + Maren's 5 boxes = room under max_nests 8 for a full apiary.
            "bee_honey":        {"initial": 0, "max": 15, "swarm_size": 4, "max_population": 60,
                                 "min_population": 0, "cull_at": 0, "max_nests": 8,
                                 "spawn_interval": 999999.0},
            "butterfly_meadow": {"initial": 6, "max": 20, "swarm_size": 6, "max_population": 90,
                                 "min_population": 10, "event_low": 20, "event_high": 60,
                                 "cull_at": 80, "spawn_interval": 600.0},
            "fly_common":       {"initial": 3, "max": 10, "swarm_size": 6, "max_population": 60,
                                 "min_population": 6, "spawn_interval": 600.0},
            # Wasps come from their 2 forest nests (raiders); the Director may cull, never seed.
            "wasp_common":      {"initial": 0, "max": 6, "swarm_size": 5, "max_population": 24,
                                 "min_population": 0, "cull_at": 20, "max_nests": 3,
                                 "spawn_interval": 999999.0},
            "dragonfly_blue":   {"initial": 2, "max": 4, "swarm_size": 2, "max_population": 8,
                                 "min_population": 1, "spawn_interval": 1200.0},
            "firefly":          {"initial": 4, "max": 8, "swarm_size": 5, "max_population": 40,
                                 "min_population": 4, "spawn_interval": 900.0},
            "millipede":        {"initial": 2, "max": 6, "swarm_size": 1, "max_population": 16,
                                 "min_population": 2, "spawn_interval": 1200.0},
            "beetle_carrion":   {"initial": 1, "max": 4, "swarm_size": 1, "max_population": 10,
                                 "min_population": 1, "spawn_interval": 1200.0},
        },
        "spawn_areas": [
            {"id": "meadow_e",  "species": ["butterfly_meadow"], "type": "circle", "cx": 200, "cy": 125, "radius": 16},
            {"id": "meadow_n",  "species": ["butterfly_meadow"], "type": "circle", "cx": 95,  "cy": 175, "radius": 14},
            {"id": "farm_fly",  "species": ["fly_common"],       "type": "circle", "cx": 140, "cy": 132, "radius": 10},
            {"id": "bay_fly",   "species": ["fly_common"],       "type": "circle", "cx": 52,  "cy": 96,  "radius": 9},
            {"id": "lake_drag", "species": ["dragonfly_blue"],   "type": "circle", "cx": 152, "cy": 64,  "radius": 9},
            {"id": "stream_ff", "species": ["firefly"],          "type": "circle", "cx": 120, "cy": 96,  "radius": 10},
            {"id": "spring_ff", "species": ["firefly"],          "type": "circle", "cx": 52,  "cy": 196, "radius": 9},
            {"id": "wood_mill", "species": ["millipede"],        "type": "circle", "cx": 214, "cy": 170, "radius": 12},
            {"id": "wood_beet", "species": ["beetle_carrion"],   "type": "circle", "cx": 180, "cy": 96,  "radius": 9},
        ],
        "initial_carrion": [
            {"item": "dead_fly", "x": 182, "y": 98, "count": 2},
            {"item": "dead_millipede", "x": 216, "y": 168, "count": 1},
        ],
    }

    # Arriving from the village reads naturally: spawn on the road just inside the east edge.
    b.spawn = [246, ROAD_Y + 2]
    b.grid = (2, 0)
    b.neighbors = {"east": "village_21_B"}
    return b


PREVIEW = "zones/bee_meadow_20"
SCALE = 2


if __name__ == "__main__":
    b = build()
    defects = b.lint()
    print("LINT:", *(["0 defects ✓"] if not defects else ["\n  - " + "\n  - ".join(defects)]))
    print("warnings:", len(b.warnings), "| missing_art:", b.missing_art())
    zdir = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "zones", "bee_meadow_20"))
    os.makedirs(zdir, exist_ok=True)
    render_builder(b, os.path.join(zdir, "full.png"), scale=2)
    print("preview ->", os.path.join(zdir, "full.png"))
    if "--save" in sys.argv:
        out_dir = b.save()
        print("saved ->", out_dir)
