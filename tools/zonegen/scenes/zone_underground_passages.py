#!/usr/bin/env python3
"""ZONE — underground_passages_31: the first underground mining zone (world slot 3,1; north→village_21_B).

NORTH-UP, Terraria-style depth model. The ZONE owns ALL terrain (surface, caves, one depth-banded substrate,
ONE dense ore pass); the two reviewed camps contribute PROPS only (scene_mine_entrance.place_camp +
scene_underground_mining_camp.{carve_hub,place_hub}).

Depth (high y = north/shallow, low y = deep), all boundaries noise-FADED (never a ruler line):
- a full-width irregular grass CLIFF across the north; below it generous surface DIRT easing into rock;
- a TRANSITION band where dirt and stone blend; then solid STONE deep, with MORE & richer ORE the deeper you go;
- the SW is soft DIRT on a SW→NE diagonal seam (ant territory: wandering burrows + dirt caverns) — dirt at any depth.
There is ONE rock you mine (stone_block); going deeper changes the floor tile + ore, not the block.

North = HIGH y = TOP of the render (make_scene flips Y; zone.go "+Y = north"). NEVER author it upside-down.

    python3 tools/zonegen/scenes/zone_underground_passages.py            # build + lint + render full.png
    python3 tools/zonegen/scenes/zone_underground_passages.py --save     # also write nakama/data/zones/
"""
import os
import sys
import random

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
sys.path.insert(0, HERE)
from zonebuilder import ZoneBuilder                                          # noqa: E402
from render import render_builder                                           # noqa: E402
from features.terrain import noise_field                                    # noqa: E402
from features.cave import carve_tunnel, carve_cavern, carve_chamber, cave_pool, fill_solid  # noqa: E402
import scene_mine_entrance, scene_underground_mining_camp                   # noqa: E402

ZW = ZH = 256
RAIL_X = 129
E_OX, E_OY = RAIL_X - 33, 196          # entrance camp: mx=33 -> mouth/rail at RAIL_X; camp on the north surface
H_OX, H_OY = RAIL_X - 28, 118          # hub: rx=28 -> rail at RAIL_X; sits below the entrance
CLIFF_Y = 232                          # the grass↔rock cliff line (matches the camp's surface level)

# Ore — DENSE + depth-RAMPED (band: top=shallow/high-y, bottom=deep/low-y). Even grid seeding (fill_solid) keeps
# coverage gap-free, so there are no dead stone walls; rares concentrate deep ("more iron and other things").
ORE = {
    "base": "stone_block",
    "veins": [
        # BASELINE everywhere (grid-seeded) so no stretch of rock is a dead grind — a 1-wide tunnel keeps
        # hitting commons. Then density + value RAMP with depth; the deepest fifth is the richest seam.
        ("ore_iron_block", 46, 12, 24, "any"), ("ore_copper_block", 28, 12, 22, "any"),
        ("ore_coal_block", 28, 12, 22, "any"),
        ("ore_copper_block", 22, 12, 22, "top"), ("ore_coal_block", 22, 12, 22, "top"),
        ("ore_iron_block", 18, 12, 22, "top"),
        ("ore_iron_block", 22, 12, 22, "mid"), ("ore_copper_block", 16, 10, 20, "mid"),
        ("ore_tin_block", 16, 8, 16, "mid"),
        ("ore_iron_block", 24, 12, 22, "bottom"), ("ore_coal_block", 18, 10, 20, "bottom"),
        ("ore_silver_block", 16, 8, 14, "bottom"),
        # DEEP = bottom 1/5: dense commons + the rares concentrated (the reward for digging down)
        ("ore_iron_block", 22, 12, 22, "deep"), ("ore_coal_block", 18, 10, 20, "deep"),
        ("ore_copper_block", 16, 10, 20, "deep"),
        ("ore_silver_block", 22, 8, 16, "deep"), ("ore_gold_block", 18, 8, 16, "deep"),
        ("ore_platinum_block", 12, 6, 12, "deep"), ("ore_diamond_block", 9, 5, 10, "deep"),
    ],
}
FLOOR_BAG = [("rubble", 10), ("cave_moss", 8), ("mushroom_glow", 7), ("mushroom_blue", 3),
             ("mushroom_brown", 3), ("bone_pile", 3), ("quartz_block", 2), ("crystal_small", 2)]


def build(zone_id="underground_passages_31"):
    b = ZoneBuilder(zone_id, ZW, ZH, base_tile="cave_floor", name="Underground Passages", biome="cave", seed=31)
    rng = random.Random(31)
    depth_nf = noise_field(ZW, ZH, wavelength=20, octaves=3, seed=131)      # fuzzes the dirt↔stone gradient
    sub_nf = noise_field(ZW, ZH, wavelength=22, octaves=3, seed=132)        # wobbles the ant dirt seam
    stone_nf = noise_field(ZW, ZH, wavelength=8, octaves=2, seed=133)       # chunky stone speckle within the dirt
    deep_nf = noise_field(ZW, ZH, wavelength=14, octaves=2, seed=134)       # mottles the deep floor-tile change
    inlet_nf = noise_field(ZW, ZH, wavelength=40, octaves=2, seed=77)       # big lobes -> dirt inlets
    cliff_nf = noise_field(ZW, 8, wavelength=16, octaves=2, seed=4)         # wobbles the full-width cliff line

    # --- ANT TERRITORY: a SW→NE DIAGONAL dirt seam (NOT vertical), wobbled, with inlets ----------------
    SLOPE, EDGE = 0.45, 18                                                  # dirt where x - SLOPE*y is small (SW)
    def is_dirt(x, y):
        d = (x - SLOPE * y) - (EDGE + 26 * (float(sub_nf[y][x]) - 0.5))
        if d < 0:
            return True
        return d < 22 and inlet_nf[y][x] > 0.66                             # occasional dirt INLET into rock

    # --- Terraria depth: dirt at the surface, a fuzzy dirt↔stone transition, solid stone deep ----------
    def dirt_here(x, y):
        if is_dirt(x, y):                                                   # ant seam: dirt at any depth
            return True
        if y >= 205:                                                        # surface topsoil (generous)
            return True
        if y < 110:                                                         # deep: solid stone
            return False
        return float(depth_nf[y][x]) < (y - 110) / 95.0                     # fuzzy gradient (more dirt higher)

    def substrate(x, y):
        if dirt_here(x, y):                                                # dirt isn't pure — chunks of stone in it
            return "stone_block" if float(stone_nf[y][x]) < 0.30 else "dirt_block"
        return "stone_block"

    def ground_tile(x, y):                                                 # the floor revealed in open cells
        if dirt_here(x, y):
            return "dirt"
        if y < 34 and float(deep_nf[y][x]) < (34 - y) / 34.0:              # deep floor shifts near the bottom
            return "mud"                                                   # (a damp deep layer -> hints the zone south)
        return "cave_floor"

    # --- full-width irregular CLIFF; flatten over the camp span so the camp sits on level ground -------
    camp_base, camp_surf = scene_mine_entrance.cliff_surface()             # the camp's own local cliff line
    surf_y = [CLIFF_Y + int(round(6 * (float(cliff_nf[0][x]) - 0.5) * 2)) for x in range(ZW)]
    for x in range(E_OX, E_OX + 64):
        surf_y[x] = E_OY + camp_surf[x - E_OX]

    grass = set()
    for x in range(ZW):
        for y in range(surf_y[x], ZH):
            b.set_ground(x, y, "grass", surface="grass")
            grass.add((x, y))
        for y in range(0, surf_y[x]):                                      # floor tile by depth (Terraria layers)
            b.set_ground(x, y, ground_tile(x, y))

    carved = set(grass)

    # --- the mine MOUTH bitten into the cliff + the continuous descending RAIL shaft -> hub -----------
    mouth = carve_cavern(b, RAIL_X, E_OY + camp_base - 3, shape="rocky", size=9, seed=2)
    shaft = carve_tunnel(b, (RAIL_X, E_OY + camp_base - 1), (RAIL_X, H_OY + 58), style="straight", width=5)
    hub = scene_underground_mining_camp.carve_hub(b, H_OX, H_OY)
    carved |= mouth | shaft | hub["carved"]

    # --- isolated CAVERNS you MINE to (deliberately NOT tunnel-linked — connecting them defeats mining).
    #     `carve_chamber` = irregular multi-blob outlines (never a bowl); ~half get a `cave_pool` (lake-grade
    #     irregular waterline + re-derived wet-rock shore), seated off-centre in a low corner. ------------
    def carve_cave(cx, cy, size, seed, *, water=False):
        cells = carve_chamber(b, cx, cy, size, seed=seed)
        if water:
            wr = random.Random(seed + 600)
            px, py = cx + wr.randint(-size // 3, size // 3), cy + wr.randint(-size // 3, size // 3)
            cave_pool(b, px, py, max(3, int(size * 0.55)), cells, seed=seed + 700)
        return cells

    # (cx, cy, size, seed, water): 2 big features w/ water; the rest small/medium; ~half watered.
    STONE_CAVES = [
        (200, 72, 22, 311, True), (85, 80, 20, 312, True),               # the two big feature caverns
        (150, 95, 12, 313, True), (175, 132, 11, 314, False),
        (222, 110, 10, 315, True), (110, 60, 11, 316, False),
        (160, 52, 10, 317, False), (236, 160, 8, 318, False),
        (190, 165, 8, 319, True), (236, 52, 7, 320, False),
        (95, 104, 7, 321, False), (128, 44, 9, 322, True),
        (60, 44, 8, 323, False), (215, 44, 7, 324, True),
        (170, 22, 10, 325, True), (90, 25, 9, 326, False),               # deep caverns (show the mud floor)
    ]
    DIRT_CAVES = [(30, 185, 12, 331, True), (40, 145, 10, 332, False), (24, 110, 9, 333, True)]
    for (cx, cy, sz, sd, wtr) in STONE_CAVES + DIRT_CAVES:
        carved |= carve_cave(cx, cy, sz, sd, water=wtr)

    # ANT burrows: the ants' OWN dug paths through the soft SW dirt (wanted — the dirt's nuance). Several run
    # OUT THROUGH THE LEFT EDGE (x=0) so the colony continues into the zone to the WEST; a couple branch back.
    for i, (root, end, wob) in enumerate([((30, 185), (0, 200), 0.8), ((24, 110), (0, 124), 0.85),
                                          ((40, 145), (0, 158), 0.85), ((30, 185), (0, 168), 0.9),
                                          ((24, 110), (0, 96), 0.8), ((40, 145), (50, 138), 0.9)]):
        carved |= carve_tunnel(b, root, end, style="natural", width=2, seed=340 + i, wobble=wob)

    b.spawn = [RAIL_X, ZH - 6]

    # --- ONE depth-ramped ore fill over ALL the rock (even coverage; no dead walls) -------------------
    fill_solid(b, carved, ORE, seed=5, substrate=substrate)

    # --- rail + WALL TORCHES down the whole shaft (continuous mouth->hub; NO timber struts) -----------
    def is_rock(x, y):
        return b.in_bounds(x, y) and (x, y) not in carved
    rail_lo, rail_hi = hub["rail_head"], E_OY + camp_base - 1
    for y in range(rail_lo, rail_hi + 1):
        if (RAIL_X, y) in carved and b.is_free(RAIL_X, y):
            b.place_occupant("mine_rail", RAIL_X, y, surface=None, reserve=False)
    for y in range(rail_lo + 3, rail_hi, 6):
        for sx in (RAIL_X - 2, RAIL_X + 2):
            if (sx, y) in carved and b.is_free(sx, y) and (is_rock(sx - 1, y) or is_rock(sx + 1, y)):
                b.place_occupant("torch_wall", sx, y, surface=None, reserve=False)

    # --- camps: props only (terrain above is the zone's) ----------------------------------------------
    scene_mine_entrance.place_camp(b, E_OX, E_OY, camp_surf, 33, camp_base, 60)
    scene_underground_mining_camp.place_hub(b, hub)

    # --- cavern dressing: glow fungus clumps + scattered earthtones (caves only, off the rail) --------
    bag = [k for k, n in FLOOR_BAG for _ in range(n)]
    cave_free = [(x, y) for (x, y) in (carved - grass)
                 if b.is_free(x, y) and (x, y) not in shaft]
    rng.shuffle(cave_free)
    centers = rng.sample(cave_free, k=min(40, len(cave_free))) if cave_free else []
    placed, target = 0, int(0.10 * len(cave_free))
    for (x, y) in cave_free:
        if placed >= target:
            break
        near = min((abs(x - cx) + abs(y - cy) for cx, cy in centers), default=99)
        if rng.random() > (0.8 if near < 4 else 0.10):
            continue
        oid = rng.choice(["mushroom_glow", "cave_moss"]) if near < 4 else rng.choice(bag)
        if b.place_occupant(oid, x, y, surface=None, reserve=False):
            placed += 1

    # --- broken rubble along the full-width cliff base (outside the camp, which dresses its own) -------
    for x in range(1, ZW - 1):
        if E_OX <= x < E_OX + 64:
            continue
        for y in (surf_y[x] - 1, surf_y[x] - 2):
            if b.is_free(x, y) and (x, y) in grass and rng.random() < 0.10:
                b.place_occupant(rng.choice(["rubble", "rubble", "standing_stone"]), x, y,
                                 surface=None, reserve=False)

    # --- bug spawning (centred on the caverns) --------------------------------------------------------
    def circ(cx, cy, r, sp, w=3.0, sid=None):
        return {"id": sid or f"{sp}_{cx}_{cy}", "species": [sp], "type": "circle",
                "cx": cx, "cy": cy, "radius": r, "weight": w}
    b.bug_spawning = {
        "species_caps": {
            "centipede_garden": {"initial": 18, "max": 60, "spawn_interval": 6000.0, "swarm_size": 2,
                                 "max_population": 160, "min_population": 4},
            "millipede":        {"initial": 20, "max": 120, "spawn_interval": 6000.0, "swarm_size": 2,
                                 "max_population": 180, "min_population": 4},
            "beetle_carrion":   {"initial": 16, "max": 60, "spawn_interval": 6000.0, "swarm_size": 2,
                                 "max_population": 150, "min_population": 3},
        },
        "spawn_areas": [
            circ(85, 80, 18, "millipede", 3.0, "milli_w"),
            circ(150, 95, 12, "millipede", 3.0, "milli_mid"),
            circ(200, 72, 18, "beetle_carrion", 3.0, "beetle_e"),
            circ(175, 132, 11, "beetle_carrion", 3.0, "beetle_se"),
            circ(RAIL_X, H_OY + 22, 20, "centipede_garden", 3.0, "cent_hub"),
            circ(30, 150, 14, "centipede_garden", 3.0, "cent_ant"),
            {"id": "milli_wild", "species": ["millipede"], "type": "zone", "weight": 0.4},
            {"id": "beetle_wild", "species": ["beetle_carrion"], "type": "zone", "weight": 0.4},
            {"id": "cent_wild", "species": ["centipede_garden"], "type": "zone", "weight": 0.4},
        ],
        "initial_carrion": [
            {"item": "dead_millipede", "x": 85, "y": 80, "count": 2},
            {"item": "dead_beetle", "x": 200, "y": 72, "count": 2},
        ],
    }
    return b


if __name__ == "__main__":
    b = build()
    print("LINT:", *(["0 defects"] if not (defects := b.lint()) else ["\n  - " + "\n  - ".join(defects[:20])]))
    print("warnings:", len(b.warnings), "| missing_art:", b.missing_art())
    zdir = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "zones", "underground_passages_31"))
    os.makedirs(zdir, exist_ok=True)
    render_builder(b, os.path.join(zdir, "full.png"), scale=2)
    print("preview ->", os.path.join(zdir, "full.png"))
    if "--save" in sys.argv:
        out_dir = b.save()
        import json
        zj = os.path.join(out_dir, "zone.json")
        cfg = json.load(open(zj))
        cfg["row"], cfg["col"] = 3, 1
        cfg["neighbors"] = {"north": "village_21_B"}
        json.dump(cfg, open(zj, "w"), indent=2)
        print("saved ->", out_dir)
