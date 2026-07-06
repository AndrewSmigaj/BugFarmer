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
                              smooth_paths, bridge, shore_dress, rock_mass)
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
    # THE INLET (the hamlet's harbor): a TRUE arm of the sea — carved east from the SW cove
    # through the sand bar, widening into a basin where the docks sit. Open water end to end:
    # a boat can row from the docks out past the buoys. (The old landlocked bay was a bug.)
    import math as _m
    for x in range(10, 53):
        cy = 62 + int(round(1.5 * _m.sin(x / 7.0)))
        half = 4 if x < 38 else 6                       # the arm, then the basin bulge
        for y in range(cy - half - 1, cy + half + 2):
            if not b.in_bounds(x, y):
                continue
            d = abs(y - cy)
            if d <= half:
                deep = d <= half - 2
                b.set_ground(x, y, "water_deep" if deep else "water_shallow", surface="water")
                b.reserve(x, y, surface="water")
            elif b.surface[y][x] == "grass":
                b.set_ground(x, y, "sand")

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

    # ---- 1b. ANT COUNTRY (the south band) ------------------------------------
    # The zone TRANSITIONS toward the Ant Colony below (3,0): torn dirt ground spreading up
    # from the south edge, ant mounds dotted through it, and mineable earth outcrops with
    # rocky cores (dirt aprons + stone_block fill + common ore veins via rock_mass).
    rng_a = random.Random(51)
    for bx, by, br in [(70, 12, 10), (105, 18, 8), (145, 8, 12), (185, 16, 8),
                       (225, 10, 9), (48, 18, 6), (255, 14, 8)]:
        for y in range(by - br - 2, by + br + 3):
            for x in range(bx - br - 2, bx + br + 3):
                if not b.in_bounds(x, y) or b.surface[y][x] != "grass":
                    continue
                d = ((x - bx) ** 2 + (y - by) ** 2) ** 0.5
                if d <= br + rng_a.uniform(-2.0, 2.0):
                    b.set_ground(x, y, "dirt")
    rock_mass(b, 100, 13, 7, 5, seed=52, veins=3)
    rock_mass(b, 190, 11, 8, 5, seed=53, veins=3)
    for mx, my in [(66, 14), (82, 9), (116, 20), (140, 6), (152, 12), (176, 18),
                   (222, 8), (233, 14)]:
        for dx in range(0, 9):
            if b.in_bounds(mx + dx, my) and b.ground[my][mx + dx] == "dirt" \
               and b.is_free(mx + dx, my):
                b.place_occupant("ant_mound", mx + dx, my)
                break

    # ---- 1c. THE ROCKY GORGE (the stream's east exit) -------------------------
    # Where the stream leaves for the village it cuts THROUGH rock: mineable stone masses
    # pressed right against BOTH banks (the stream is reserved water, so the fill stops at
    # the channel), salted with common veins by rock_mass — plus HAND-SET rare ores for the
    # sharp-eyed, and loose bank stones tracing the waterline between the masses.
    rock_mass(b, 224, 90, 9, 7, seed=54, veins=4)   # north bank, apron on the water
    rock_mass(b, 231, 66, 9, 7, seed=55, veins=4)   # south bank, apron on the water
    # Hand-set rare ores: spiral outward from the target until a free cell — robust against
    # the run-to-run placement drift (reed/shore sets iterate hash-randomized).
    def _place_ore(oid, cx_, cy_, r=8):
        for d in range(r + 1):
            for dy in range(-d, d + 1):
                for dx in range(-d, d + 1):
                    if max(abs(dx), abs(dy)) == d and b.in_bounds(cx_ + dx, cy_ + dy) \
                       and b.surface[cy_ + dy][cx_ + dx] != "water" and b.is_free(cx_ + dx, cy_ + dy):
                        return b.place_occupant(oid, cx_ + dx, cy_ + dy)
        raise SystemExit(f"no room for {oid} near ({cx_},{cy_}) — rework the gorge")
    _place_ore("ore_silver_block", 214, 90)
    _place_ore("ore_gold_block", 237, 70)
    _place_ore("ore_ruby_block", 228, 56)
    # Bank stones: hug the actual waterline column by column through the gorge reach.
    rng_g = random.Random(58)
    for gx in range(204, 252, 3):
        span = _water_span(b, gx, 56, 104, row=False)
        if not span:
            continue
        for gy in (span[0] - 1, span[1] + 1):
            if rng_g.random() < 0.6 and b.in_bounds(gx, gy) \
               and b.surface[gy][gx] == "grass" and b.is_free(gx, gy):
                b.place_occupant("stone_block", gx, gy)

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

    # The hamlet spur: from the west leg down to the north quay by the footbridge.
    path(b, (52, 104), (50, 72), width=1, tile="dirt", wobble=0.08, seed=30, taper_ends=2)

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
    place_fishing_hamlet(b, 24, 69, 55)  # split shores across the inlet, footbridge at x50

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
    flower_patch(b, 66, 32, 160, 52, common, 34, seed=46)   # the south meadow, above ant country
    # Milkweed clumps (butterfly breeding hosts).
    for mx, my in [(180, 160), (183, 158), (186, 162), (84, 176), (87, 174), (90, 178)]:
        if b.is_free(mx, my):
            b.place_occupant("milkweed", mx, my)

    # Forests (dark forest floors — dirt=True): the NE stand, the stream-bank strip, the
    # north-west band, and TWO NEW NORTH STANDS framing the top of the zone. The gap between
    # the north stands is deliberate — travellers pass through here, and the open corridor
    # around y≈200-215 stays wide and readable.
    forest(b, 214, 172, 26, 18, seed=38, density=0.5, dirt=True)
    forest(b, 176, 96, 18, 8, seed=39, density=0.45, dirt=True)
    forest(b, 42, 182, 16, 12, seed=40, density=0.5, dirt=True)
    forest(b, 158, 236, 26, 13, seed=48, density=0.55, dirt=True)
    forest(b, 96, 232, 15, 11, seed=49, density=0.5, dirt=True)
    # THE HONEY GLADE — the clearing between the north stands: a wild hive in a ring of
    # flowers (you hear it before you see it). Overhead can't do hilltops; it CAN do glades.
    flower_patch(b, 118, 224, 142, 244, common + rarer, 26, seed=50)
    _glade_hive = (128, 234)
    # THE MUSHROOM HOLLOW — the damp clearing between the NW band and the west north stand.
    scatter(b, 62, 206, 88, 226,
            {"mushroom_brown": 4, "mushroom_chanterelle": 2, "leaf_litter": 4, "fern": 3},
            density=0.07, min_spacing=2, seed=56, surfaces=("grass",))
    # Forest floor: leaf litter (millipede food) + mushrooms in each stand.
    for (x0, y0, x1, y1, sd) in [(190, 156, 240, 190, 41), (160, 88, 194, 104, 42),
                                 (28, 172, 58, 194, 43), (146, 226, 184, 248, 57)]:
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

    # The free colonies (each auto-founds; the flowers nearby are their economy) — including
    # the honey-glade hive between the north stands.
    for hx, hy in [(168, 152), (206, 118), (78, 202), _glade_hive]:
        _place_near("bee_hive_wild", hx, hy)
    # The raiders, at forest edges AWAY from the farm (this is the EASY zone).
    for wx, wy in [(232, 158), (186, 90)]:
        _place_near("wasp_nest", wx, wy)

    # The beach set + the coast's NAMED features: the shipwreck at the mid-coast cove, the
    # picnic spot on the north beach, buoys off the cove mouths, the bottle on the island.
    dress_beach(b, beach, seed=44, density=0.05)
    place_beach_landmarks(b, beach, wreck_y=141, picnic_y=206, buoy_ys=(64, 141),
                          bottle_island=(5, 102))

    # WAYFINDING — signposts WITH TEXT at the junctions (arriving must read instantly), and
    # one at the ant-country edge that earns its keep as foreshadowing.
    for sx, sy, txt in [
        (249, ROAD_Y + 3, "BEE MEADOW — the flower coast.\nThe Village →"),
        (135, ROAD_Y + 3, "↑ Maren's Bee Farm\n↓ Dragonfly Lake\n→ The Village"),
        (57, 108, "↓ Gullwash Landing — mind the tide."),
        (148, 29, "⚠ The ground hums here.\nMind the mounds."),
    ]:
        placed_sign = False
        for dy in (0, 1, -1):
            for dx in range(0, 9):
                if b.is_free(sx + dx, sy + dy) and b.surface[sy + dy][sx + dx] == "grass":
                    b.place_occupant("signpost", sx + dx, sy + dy, text=txt)
                    placed_sign = True
                    break
            if placed_sign:
                break
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
                                 "min_population": 0, "cull_at": 0, "max_nests": 10,
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
