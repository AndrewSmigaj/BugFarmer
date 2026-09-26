#!/usr/bin/env python3
"""ZONE — ant_colony_40 (4,0): the colony CITY, fully underground, MEDIUM. Built the CORRECT way:
crafted landmark SCENES (scene_queen_cathedral + scene_colony_districts) composed-in-place over
material-rich terrain (layout C — root branches, owner-picked).

ORIENTATION (pinned): HIGH y = NORTH = top (shafts to (3,0)); LOW y = SOUTH = deep (Queen). x=0 =
WEST (sea), x=255 = EAST (paths to (4,1)). GAME loads the SAVE not this script.

Terrain rulings (owner): soil digging must FIND things (ore VEINS + stone throughout — caves.md
Rule 4/§4, MEASURED); a full-width BOTTOM ROCK band extended all the way LEFT + the organic SE
intrusion (one NE->SW rock field w/ row-4 ore); a real ROCKY SHORE on the west coast; PATHS driven
east into (4,1). Bugs backlogged (spawns PLANNED). No ceilings.
"""
import os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__)); ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG); sys.path.insert(0, HERE)
from zonebuilder import ZoneBuilder                                          # noqa: E402
from features.terrain import noise_field, rock_mass                         # noqa: E402
from features.cave import carve_tunnel, carve_cavern, carve_chamber, cave_pool, fill_solid  # noqa: E402
from render import render_builder                                           # noqa: E402
from scene_queen_cathedral import place_queen_cathedral                     # noqa: E402
from scene_colony_districts import (place_fungus_terrace, place_brood_nursery,  # noqa: E402
                                    place_granary, place_ore_wall, place_deep_sump)

ZW = ZH = 256
NORTH_SHAFTS = [60, 104, 150, 182]
GATHER = (118, 206)            # the gathering gallery (root system's crown)
QUEEN = (118, 34)
# layout C district TIPS (cx, cy, kind, place_fn)
DISTRICTS = [(56, 150, "fungus", place_fungus_terrace), (186, 150, "fungus", place_fungus_terrace),
             (78, 98, "granary", place_granary), (168, 100, "nursery", place_brood_nursery),
             (116, 122, "nursery", place_brood_nursery), (150, 176, "compost", place_granary)]
# ORE — light commons throughout the SOIL (digging finds things), row-4 rares DEEP (the rock field).
ORE = {"base": "dirt_block", "veins": [
    ("ore_copper_block", 104, 4, 9, "any"), ("ore_coal_block", 94, 4, 9, "any"),
    ("ore_iron_block", 88, 4, 9, "any"),
    ("ore_copper_block", 32, 4, 8, "surface"), ("ore_coal_block", 26, 4, 8, "surface"),
    ("ore_copper_block", 58, 4, 8, "top"), ("ore_iron_block", 62, 4, 9, "top"),
    ("ore_coal_block", 50, 4, 8, "top"),
    ("ore_iron_block", 74, 4, 9, "mid"), ("ore_tin_block", 48, 3, 7, "mid"),
    ("ore_copper_block", 50, 4, 8, "mid"),
    ("ore_iron_block", 80, 4, 9, "bottom"), ("ore_silver_block", 56, 3, 7, "bottom"),
    ("ore_coal_block", 48, 4, 8, "bottom"),
    ("ore_silver_block", 68, 3, 7, "deep"), ("ore_gold_block", 54, 3, 6, "deep"),
    ("ore_platinum_block", 34, 2, 5, "deep"), ("ore_diamond_block", 26, 2, 5, "deep"),
    ("ore_iron_block", 62, 4, 8, "deep")]}


def build():
    b = ZoneBuilder("ant_colony_40", ZW, ZH, base_tile="cave_floor", name="Ant Colony", biome="cave")
    rng = random.Random(40)
    stone_nf = noise_field(ZW, ZH, wavelength=7, octaves=2, seed=140)
    seam_nf = noise_field(ZW, ZH, wavelength=30, octaves=2, seed=142)
    coast_nf = noise_field(ZW, ZH, wavelength=24, octaves=2, seed=143)
    deep_nf = noise_field(ZW, ZH, wavelength=16, octaves=2, seed=141)
    shore_nf = noise_field(ZW, ZH, wavelength=9, octaves=2, seed=144)

    def coast_x(y):
        return 16 + 10 * (1 - y / 255.0) + (coast_nf[y][0] - 0.5) * 12

    def is_rock(x, y):
        # ONE rock field = the full-width BOTTOM band (deep) + the NE->SW SE intrusion, noise-faded.
        bottom = y < 46 + (seam_nf[y][x] - 0.5) * 34
        se = (x - y) + (seam_nf[y][x] - 0.5) * 205 > 150
        return bottom or se

    def substrate(x, y):
        if is_rock(x, y):
            return "stone_block"
        return "stone_block" if float(stone_nf[y][x]) < 0.12 else "dirt_block"

    def ground_tile(x, y):
        if y < 14 and float(deep_nf[y][x]) < (14 - y) / 14.0:
            return "mud"
        return "cave_floor" if is_rock(x, y) else "dirt"

    # ===== 1. CARVE layout C (root branches) — collect carved =============================
    carved = set()

    def tun(a, c, w, seed, wob=0.5):
        cc = carve_tunnel(b, a, c, width=w, seed=seed, wobble=wob); carved.update(cc); return cc

    for i, sx in enumerate(NORTH_SHAFTS):                          # shafts -> gathering gallery
        tun((sx, ZH - 1), (sx + (i - 1) * 5, 224), 3, 300 + i, 0.7)
        tun((sx + (i - 1) * 5, 224), GATHER, 3, 310 + i, 0.6)
    carved |= carve_cavern(b, GATHER[0], GATHER[1], shape="lobed", size=13, seed=315)
    for i, (dx, dy, kind, fn) in enumerate(DISTRICTS):            # roots branch out to the district tips
        tun(GATHER, (dx, dy), 3, 320 + i, 0.6)
        carved |= carve_chamber(b, dx, dy, 10, seed=330 + i)
    tun(GATHER, QUEEN, 6, 350, 0.4)                              # the trunk down to the Queen
    tun((116, 122), QUEEN, 3, 351, 0.5)
    # the Queen's cruciform DOME (main + E/W transepts + N narthex + S apse; the cathedral composes in)
    for (ddx, ddy, sz) in [(0, 0, 16), (-13, 4, 10), (13, 4, 10), (0, 11, 8), (0, -10, 7)]:
        carved |= carve_cavern(b, QUEEN[0] + ddx, QUEEN[1] + ddy, shape="lobed", size=sz, seed=360 + ddx)
    # EAST PATHS driven INTO (4,1) (the raid seam) + a couple SW branches
    for i, ey in enumerate([150, 100, 60]):
        tun((196, ey), (ZW - 1, ey), 3, 370 + i, 0.4)
    tun((78, 98), (56, 150), 2, 380, 0.6); tun((168, 100), (150, 176), 2, 381, 0.6)
    # DEEP SUMP gallery + scattered ISOLATED caverns (variety; mostly unlinked — mine to them)
    SUMP = (150, 20)
    carved |= carve_cavern(b, SUMP[0], SUMP[1], shape="lobed", size=8, seed=390)
    icrng = random.Random(70); ISO = []
    while len(ISO) < 16 and len(ISO) < 999:
        cx, cy = icrng.randint(30, 210), icrng.randint(24, 232)
        if is_rock(cx, cy) or cx < coast_x(cy) + 8: continue
        if any((cx - dx) ** 2 + (cy - dy) ** 2 < 30 ** 2 for (dx, dy, _, _) in DISTRICTS): continue
        if any((cx - ix) ** 2 + (cy - iy) ** 2 < 22 ** 2 for (ix, iy, _) in ISO): continue
        cells = carve_cavern(b, cx, cy, size=icrng.randint(3, 7), seed=800 + len(ISO),
                             shape=icrng.choice(["blob", "rocky", "lobed"]))
        carved.update(cells)
        ISO.append((cx, cy, icrng.choice(["pool", "crystal", "fungus", "bone", "bare", "bare"])))
        if len(ISO) >= 16: break
        if len([1]) > 400: break

    # ===== 2. GROUND + ONE fill_solid (ore veins throughout — digging finds things) =======
    for (x, y) in carved:
        if b.in_bounds(x, y):
            b.set_ground(x, y, ground_tile(x, y))
    fill_solid(b, carved, ORE, seed=5, substrate=substrate)

    # ===== 3. WEST COAST + ROCKY SHORE (rock_mass overlapping the beach — actual rocks) ====
    for y in range(ZH):
        cx = coast_x(y)
        for x in range(ZW):
            if x < cx - 2:
                b.occ.pop((x, y), None); b.reserved[y][x] = False; b.set_ground(x, y, "water_deep", surface="water")
            elif x < cx:
                b.occ.pop((x, y), None); b.reserved[y][x] = False; b.set_ground(x, y, "water_shallow", surface="water")
            # (rocky-shore rework — sand edge + stone masses + individual stones + south stone cliff
            #  + sea-caves + less-straight coast + secret harbor — done in the dedicated shore pass)
    # a rocky shore: rock outcrops STRADDLING the waterline + sea-stacks poking from the shallows
    # (owner: "rocky shores should have actual rocks") — headlands every ~28 cells down the coast.
    shrng = random.Random(430)
    for my in range(24, 236, 28):
        cxw = coast_x(my)
        mx = int(cxw) + shrng.randint(-1, 2)                       # centred ON the waterline
        rx, ry = shrng.randint(3, 6), shrng.randint(4, 8)
        rock_mass(b, mx, my, rx, ry, seed=my, shell="stone_block", floor="stone_floor",
                  core="stone_block", gap_chance=0.14,
                  vein_spec=[("ore_copper_block", 2, 3, 5, "any"), ("ore_iron_block", 1, 2, 4, "any")])
        for _ in range(shrng.randint(1, 3)):                       # lone sea-stacks just offshore
            sx, sy = int(cxw) - shrng.randint(1, 4), my + shrng.randint(-5, 5)
            if b.in_bounds(sx, sy) and b.ground[sy][sx].startswith("water") and b.is_free(sx, sy):
                b.place_occupant("stone_block", sx, sy, surface=None, reserve=False)

    # ===== 4. COMPOSE the crafted SCENES at their anchors =================================
    place_queen_cathedral(b, QUEEN[0], QUEEN[1], R=15)
    for (dx, dy, kind, fn) in DISTRICTS:
        fn(b, dx, dy)
    place_deep_sump(b, SUMP[0], SUMP[1])
    place_ore_wall(b, 214, 40)                                    # the secret, inside the SE rock field
    # dress the isolated caverns by kind (crystals/pools/fungus/bone/bare)
    IB = {"crystal": ["crystal_small", "quartz_block", "mushroom_glow"],
          "fungus": ["mushroom_glow", "mushroom_inkcap", "moss_clump"],
          "bone": ["bone_pile", "rubble", "standing_stone"], "bare": ["moss_clump", "rubble"]}
    drng = random.Random(72)
    for (icx, icy, kind) in ISO:
        cells = [(x, y) for x in range(icx - 8, icx + 9) for y in range(icy - 8, icy + 9)
                 if b.in_bounds(x, y) and (x, y) in carved and b.is_free(x, y)]
        if kind == "pool" and cells:
            cave_pool(b, icx, icy, 3, carved, seed=icx); cells = [c for c in cells if b.is_free(*c)]
        for c in drng.sample(cells, k=int(len(cells) * (0.10 if kind == "bare" else 0.28))) if cells else []:
            if b.is_free(*c):
                b.place_occupant(drng.choice(IB.get(kind, ["moss_clump"])), c[0], c[1], surface=None, reserve=False)
    # worker-file preview down the trunk (live traffic is backlogged)
    for i in range(20):
        t = i / 19.0
        b.place_bug("ant_worker", GATHER[0] + (i % 3 - 1), int(GATHER[1] + (QUEEN[1] - GATHER[1]) * t), scale=2.1)

    # ===== 5. bug_spawning (PLANNED; existing species spawn — new bugs backlogged) ========
    b.bug_spawning = {
        "species_caps": {
            "ant_worker": {"initial": 10, "max": 20, "max_population": 70, "min_population": 5, "swarm_size": 3},
            "ant_scout": {"initial": 2, "max": 4, "max_population": 8, "min_population": 1, "swarm_size": 1},
            # PLANNED backlogged (underground roster): ant_queen @ throne (118,35) STATIONARY/chills;
            # warrior_ant guard-ring @ Queen dome; cave_fly @ granaries; raid_centipede (green) @ east seam.
        },
        "spawn_areas": [
            {"id": "colony_workers", "species": ["ant_worker"], "type": "circle", "cx": 118, "cy": 130, "radius": 80, "weight": 1.0},
            {"id": "colony_scouts", "species": ["ant_scout"], "type": "circle", "cx": 118, "cy": 150, "radius": 90, "weight": 1.0}],
        "initial_carrion": [{"item": "dead_beetle", "x": 78, "y": 98, "count": 2},
                            {"item": "dead_ant", "x": 200, "y": 100, "count": 3}]}
    b.grid = (4, 0)
    b.neighbors = {"north": "ant_tunnels_30", "east": "centipede_cavern_41"}
    b.spawn = [NORTH_SHAFTS[1], ZH - 4]
    return b


if __name__ == "__main__":
    b = build()
    print("LINT:", *(["0 defects"] if not (d := b.lint()) else ["\n  - " + "\n  - ".join(d[:20])]))
    print("warnings:", len(b.warnings), "| missing_art:", b.missing_art())
    zdir = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "zones", "ant_colony_40"))
    os.makedirs(zdir, exist_ok=True)
    render_builder(b, os.path.join(zdir, "full.png"), scale=2)
    print("preview ->", os.path.join(zdir, "full.png"))
    if "--save" in sys.argv:
        print("saved ->", b.save())
