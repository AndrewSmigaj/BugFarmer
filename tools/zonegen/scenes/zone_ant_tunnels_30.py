#!/usr/bin/env python3
"""ZONE — ant_tunnels_30 (world slot 3,0; the EASY half-outside ant zone).

Brief: docs/product/zones/ant_tunnels_30.md rev 2. Built to MATCH its neighbours' real
techniques (not reinvented) — the underground uses the SAME depth-substrate + one
depth-ramped fill_solid ore pass as underground_passages_31 (caves.md §4 doctrine), and the
west COAST is a natural sea border with rocky/dirt cliffs that rocken heading south.

Neighbours (read from their saved data):
- NORTH bee_meadow_20: south edge is OCEAN in the NW (water x0-9) -> this zone's coast.
- EAST  underground_passages_31: its west edge is the ANT DIRT SEAM (~67% dirt_block + stone
  chunks + ore veins) with tunnels at y 95-100/122-124/158-160/168-170/201-203. This zone's
  soil + tunnels MEET it (same substrate model, same rows).
- SOUTH ant_colony_40 (unbuilt): the ant tunnels dig into DIRT and DESCEND south to the colony.
- WEST  world edge = the SEA (natural border).

ORIENTATION (pinned): HIGH y = NORTH = top; LOW y = SOUTH = deep. x=0 = WEST, x=255 = EAST.
The GAME loads the SAVE not this script: after editing, `--save` + verify north-up with
`view_world ant_tunnels_30`, and reset the persisted zone_state record if it won't update.
"""
import os, sys, random, math
HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
sys.path.insert(0, HERE)
from zonebuilder import ZoneBuilder                                            # noqa: E402
from features.terrain import _vnoise, noise_field, forest                     # noqa: E402
from features.scatter import scatter                                          # noqa: E402
from features.cave import carve_tunnel, carve_cavern, carve_chamber, cave_pool, fill_solid  # noqa: E402
from render import render_builder                                             # noqa: E402
import scene_ant_entrance as ENT                                             # noqa: E402

ZW = ZH = 256
EAST_STUBS = [97, 123, 159, 169, 202]     # tunnel rows that meet the mining zone's west edge

# ANT-ZONE ORE — light (EASY: mostly soil) but RAMPS with depth toward the colony/mining seam,
# grid-seeded veins (caves.md §4), so no dead walls and the deep south is the richest.
ORE_ANT = {
    "base": "dirt_block",
    "veins": [
        ("ore_copper_block", 16, 8, 16, "any"), ("ore_coal_block", 14, 8, 16, "any"),
        ("ore_iron_block", 10, 8, 14, "any"),
        ("ore_iron_block", 14, 8, 16, "mid"), ("ore_copper_block", 10, 6, 12, "mid"),
        ("ore_iron_block", 16, 8, 16, "bottom"), ("ore_coal_block", 10, 6, 12, "bottom"),
        ("ore_silver_block", 10, 6, 12, "bottom"),
        ("ore_iron_block", 14, 8, 16, "deep"), ("ore_silver_block", 12, 6, 12, "deep"),
        ("ore_gold_block", 7, 4, 9, "deep"),
    ],
}


def build():
    b = ZoneBuilder("ant_tunnels_30", ZW, ZH, base_tile="grass", name="Ant Tunnels", biome="meadow")
    rng = random.Random(30)
    nb = _vnoise(31)                                                     # boundary warp
    ng = _vnoise(57)                                                     # gradient warp
    coast_nf = noise_field(ZW, ZH, wavelength=26, octaves=2, seed=71)   # wobbles the coastline
    depth_nf = noise_field(ZW, ZH, wavelength=20, octaves=3, seed=131)  # fuzzes dirt<->stone
    stone_nf = noise_field(ZW, ZH, wavelength=8, octaves=2, seed=133)   # stone chunks in the dirt
    deep_nf = noise_field(ZW, ZH, wavelength=14, octaves=2, seed=134)   # mottles the deep mud floor
    inlet_nf = noise_field(ZW, ZH, wavelength=34, octaves=2, seed=78)   # dirt fingers into deep stone

    def surface_y(x):
        """Surface<->underground boundary. Rises toward the EAST (underground reaches the high
        east connection rows y<=202); the west stays open surface. HEAVILY noise-warped so the
        grass/dirt line is wavy + natural, never a straight diagonal (two octaves; kept high
        enough on the east that the y202 connection stays underground)."""
        t = max(0.0, (x - 34)) / (ZW - 1 - 34)
        base = 112 + 126 * (t ** 1.5)
        return base + (nb(0.09 * x, 0.0) - 0.5) * 24 + (nb(0.23 * x, 3.0) - 0.5) * 14

    def coast_x(y):
        """The coastline: SEA west of it (natural border, full height). Matches bee_meadow's
        NW ocean at the north edge, widens a little heading south."""
        base = 9 + 10 * (1.0 - y / 255.0)                              # ~9 north -> ~19 south
        return base + (coast_nf[y][0] - 0.5) * 12

    # ---- depth-substrate model (Terraria layers), the SAME shape as the mining zone --------
    def substrate(x, y):
        # The UPPER ant zone is DIRT all the way down (ants dig soil; the ROCK is the EAST
        # neighbour — zone 31's dirt is its WEST side, so rock can't be here). Dirt with
        # INTEGRATED stone chunks + stray ore, exactly like zone 31's west dirt seam. No
        # separate rock region.
        return "stone_block" if float(stone_nf[y][x]) < 0.13 else "dirt_block"

    def ground_tile(x, y):                                             # floor revealed in open cells
        if y < 22 and float(deep_nf[y][x]) < (22 - y) / 22.0:
            return "mud"                                               # a few damp deep spots
        return "dirt"                                                  # ant tunnels are dug in dirt

    # ==================== 1. GROUND PASS: sea / surface / underground-floor =================
    for y in range(ZH):
        cx = coast_x(y)
        for x in range(ZW):
            if x < cx:                                                 # THE SEA (west border)
                if x < cx - 2.2:
                    b.set_ground(x, y, "water_deep", surface="water")
                else:
                    b.set_ground(x, y, "water_shallow", surface="water")
            elif x < cx + 4.0:                                         # the beach (wide, matches bee)
                b.set_ground(x, y, "sand", surface="grass")
            elif y > surface_y(x):
                b.set_ground(x, y, "grass", surface="grass")           # surface land (gradient below)
            else:
                b.set_ground(x, y, ground_tile(x, y))                  # underground floor by depth

    # ==================== 2. CARVE THE TUNNEL NETWORK (dirt, descending SOUTH) ===============
    # Ant tunnels dig through the DIRT and DESCEND to the SOUTH EDGE (y~2) — the arteries
    # continue into ant_colony_40 where the real colony is. A SECOND entrance gives another
    # way in/out. Little natural caverns pock the soil.
    carved = set()
    MOUTH = (112, int(surface_y(112)))
    MOUTH2 = (172, int(surface_y(172)))                                           # a 2nd entrance
    JUNC = (120, 108)
    ETRUNK = (206, 150)
    # arteries down to the south edge (into the colony below)
    carved |= carve_tunnel(b, MOUTH, JUNC, width=3, seed=202, wobble=0.5)
    carved |= carve_tunnel(b, JUNC, (104, 2), width=3, seed=201, wobble=0.6)      # main artery -> south edge
    carved |= carve_tunnel(b, JUNC, (150, 2), width=2, seed=220, wobble=0.6)      # branch -> south edge
    carved |= carve_tunnel(b, (104, 66), (60, 2), width=2, seed=221, wobble=0.65) # branch -> south edge
    # the 2nd entrance descends + links to the network
    carved |= carve_tunnel(b, MOUTH2, (182, 4), width=2, seed=230, wobble=0.6)    # 2nd exit -> south edge
    carved |= carve_tunnel(b, MOUTH2, ETRUNK, width=2, seed=231, wobble=0.5)
    # the east trunk + spurs that MEET the mining zone's west openings
    carved |= carve_tunnel(b, JUNC, ETRUNK, width=3, seed=203, wobble=0.5)
    for i, ys in enumerate(EAST_STUBS):
        carved |= carve_tunnel(b, ETRUNK, (ZW - 1, ys), width=3, seed=210 + i, wobble=0.4)
    # chambers off the network
    CH = {"crossroads": (120, 106), "fungus": (150, 78), "granary": (92, 60), "brood": (128, 40)}
    for name, (cx0, cy0) in CH.items():
        carved |= carve_chamber(b, cx0, cy0, 7 if name != "brood" else 6, seed=hash(name) % 999)
    # LITTLE natural caverns pocking the soil (like zone 31's scattered voids)
    for i, (cx0, cy0, sz) in enumerate([(72, 34, 4), (162, 48, 5), (94, 92, 4), (182, 96, 4),
                                        (52, 56, 4), (198, 62, 5), (134, 24, 4), (86, 122, 4),
                                        (168, 118, 4), (60, 96, 4)]):
        carved |= carve_cavern(b, cx0, cy0, shape="blob", size=sz, seed=400 + i)
    # the arteries BREACH the SOUTH EDGE (y0) so the trails continue into ant_colony_40 below
    for sx in (104, 150, 60, 182):
        for yy in range(0, 5):
            for dx in (-1, 0, 1):
                if b.in_bounds(sx + dx, yy):
                    carved.add((sx + dx, yy))

    # ==================== 3. ONE depth-ramped fill_solid over the underground rock ==========
    # carved-so-fill-skips = the tunnels + ALL surface land + ALL sea (only the underground
    # rock gets blocks). Then fill_solid lays dirt(+stone chunks)+ore veins via the substrate.
    skip = set(carved)
    for y in range(ZH):
        cx = coast_x(y)
        for x in range(ZW):
            if x < cx + 4.0 or y > surface_y(x):
                skip.add((x, y))
    fill_solid(b, skip, ORE_ANT, seed=5, substrate=substrate)

    # ==================== 4. THE COASTAL CLIFF (dirt north -> rocky south) ===================
    # Where land meets the sea, a broken cliff lip + scree; DIRT blocks in the north, STONE in
    # the rockier south (owner: "rocky/dirt cliffs along the coast, rockier going south").
    for y in range(ZH):
        cx = int(coast_x(y))
        rocky = y < 150 - 40 * (coast_nf[y][1] - 0.5)                  # south + noise -> rocky
        for x in range(cx + 4, cx + 7):
            if not b.in_bounds(x, y) or not b.is_free(x, y) or b.surface[y][x] == "water":
                continue
            if b.surface[y][x] == "grass" and rng.random() < (0.7 if x == cx + 2 else 0.3):
                b.place_occupant("stone_block" if rocky else "dirt_block", x, y)
    # scree/rubble spilling from the cliff feet onto the beach
    for y in range(ZH):
        cx = int(coast_x(y))
        if rng.random() < 0.22 and b.in_bounds(cx + 1, y) and b.is_free(cx + 1, y):
            b.place_occupant(rng.choice(["rubble", "rubble", "standing_stone"]), cx + 1, y)

    # ==================== 5. SURFACE: grass->dirt gradient + forage grounds =================
    for y in range(ZH):
        for x in range(ZW):
            if b.surface[y][x] != "grass" or b.ground[y][x] != "grass" or not b.is_free(x, y):
                continue
            yc = surface_y(x)
            if y <= yc:
                continue
            t = (y - yc) / max(1.0, (ZH - 1) - yc)                     # 0 at boundary, 1 at north
            # dirt is strongest AT the boundary and FADES up into grass on a NOISY line (never a
            # straight cutoff); the top stays mostly grass toward the bee_meadow seam.
            if (0.78 - t * 1.3) + (ng(0.07 * x, 0.07 * y) - 0.5) * 1.1 > 0.0:
                b.set_ground(x, y, "dirt", surface="grass")

    # WOODED forage grounds (C16: wild zones wooded by default) — denser stands with clearings
    # (C7) + lone trees threading the whole band, fruit trees, berry scrub. The trail food.
    for (fx, fy, fw, fh, dens, seed) in [
        (68, 218, 24, 16, 0.52, 71), (150, 214, 26, 17, 0.50, 72),
        (42, 172, 22, 15, 0.48, 73), (108, 182, 24, 15, 0.46, 74), (190, 208, 18, 13, 0.50, 75),
        (86, 208, 16, 11, 0.46, 81), (168, 178, 20, 13, 0.44, 82), (58, 142, 18, 12, 0.44, 83),
        (128, 150, 18, 12, 0.42, 85),
    ]:
        forest(b, fx, fy, fw, fh, density=dens, seed=seed)
    # extra stands + lone trees on the dirt-TRANSITION strip (the brown band above the mouths),
    # so it reads WOODED, not bare — but KEPT CLEAR of the entrance column (x88-128; a clearing
    # goes there for the station).
    for (fx, fy, fw, fh, dens, seed) in [
        (36, 158, 18, 13, 0.42, 91), (150, 150, 22, 13, 0.40, 92), (44, 128, 16, 11, 0.40, 93),
        (196, 152, 16, 11, 0.42, 94), (150, 138, 18, 11, 0.38, 95), (28, 176, 16, 11, 0.40, 96),
    ]:
        forest(b, fx, fy, fw, fh, density=dens, seed=seed)
    scatter(b, 30, 122, 232, 252, {"tree_oak": 2, "tree_pine": 1, "bush": 1}, density=0.014, min_spacing=4, seed=84)
    for (tx, ty) in [(78, 198), (122, 188), (172, 200), (56, 150), (150, 160), (100, 205)]:
        if b.in_bounds(tx, ty) and b.is_free(tx, ty) and b.surface[ty][tx] == "grass":
            b.place_occupant("tree_apple", tx, ty)
    scatter(b, 34, 128, 232, 250, {"wild_berry_bush": 3, "tall_grass": 6, "bush": 3, "clover": 4},
            density=0.04, min_spacing=3, seed=76, clumping=0.6, cluster_radius=5)

    # dirt-block mound lips framing the SECOND mouth (the station handles the main mouth's lips)
    for (mox, moy) in (MOUTH2,):
        for dx in (-2, -1, 2, 3):
            for dy in (0, 1):
                if b.in_bounds(mox + dx, moy + dy) and b.is_free(mox + dx, moy + dy) \
                   and b.surface[moy + dy][mox + dx] == "grass":
                    b.place_occupant("dirt_block", mox + dx, moy + dy)

    # ==================== 5b. THE MYRMECOLOGY STATION at the MAIN ENTRANCE ===================
    # The prominent doorstep. The ZONE owns the tunnel (the MOUTH artery, carved above); the
    # station places ONLY the SURFACE compound around the mouth (building to the WEST, clearing
    # its own trees), so nothing overlaps the throat.
    mx, my = MOUTH
    # a REAL, generous CLEARING for the whole entrance (compound + mouth + road head) — no trees
    # crowding the doorstep or the throat.
    for yy in range(my - 4, my + 40):
        for xx in range(mx - 40, mx + 18):
            if not b.in_bounds(xx, yy):
                continue
            c = b.occ.get((xx, yy))
            if c and c.get("id") not in ("dirt_block", "stone_block") and "ore_" not in c.get("id", ""):
                del b.occ[(xx, yy)]
                b.reserved[yy][xx] = False
    ENT.place_ant_entrance(b, mx, my)
    # the ROAD from the north edge (meets bee_meadow's harbour road) down to the entrance,
    # arriving just WEST of the mouth — never through the building. Trees on the road are cleared.
    rng_r = random.Random(88)
    rx = mx - 4
    for yy in range(ZH - 1, my + 6, -1):
        # clear trees in a BAND around the road (so tall sprites never overhang the roadway)
        for xx in range(rx - 1, rx + 3):
            for yy2 in (yy, yy - 1):
                c = b.occ.get((xx, yy2))
                if c and c.get("id") not in ("dirt_block", "stone_block") and "ore_" not in c.get("id", ""):
                    del b.occ[(xx, yy2)]
                    b.reserved[yy2][xx] = False
        for dx in (0, 1):                               # pave the 2-wide road
            xx = rx + dx
            if b.in_bounds(xx, yy) and b.is_free(xx, yy) and b.surface[yy][xx] == "grass":
                b.set_ground(xx, yy, "mud", surface="path")
        rx += rng_r.choice((-1, 0, 0, 1))
        rx = max(mx - 12, min(mx + 1, rx))
    b.spawn = [rx, ZH - 4]                                   # arrive on the road at the north seam
    for sx in (mx - 8, mx + 4):                              # a waymarker BESIDE the road (not on it)
        if b.in_bounds(sx, ZH - 26) and b.is_free(sx, ZH - 26) and b.surface[ZH - 26][sx] == "grass":
            b.place_occupant("signpost", sx, ZH - 26)
            break

    # ==================== 6. bug_spawning ===================================================
    b.bug_spawning = {
        "species_caps": {
            "ant_worker": {"initial": 4, "max": 10, "max_population": 40, "min_population": 2, "swarm_size": 3},
            "ant_scout":  {"initial": 2, "max": 4,  "max_population": 8,  "min_population": 1, "swarm_size": 1},
            "centipede_garden": {"initial": 1, "max": 2, "max_population": 4, "min_population": 0, "swarm_size": 1},
        },
        "spawn_areas": [
            {"id": "ants_outside", "species": ["ant_worker"], "type": "circle", "cx": 120, "cy": 185, "radius": 42, "weight": 1.0},
            {"id": "scouts", "species": ["ant_scout"], "type": "circle", "cx": 130, "cy": 175, "radius": 55, "weight": 1.0},
            {"id": "cent_den", "species": ["centipede_garden"], "type": "circle", "cx": 205, "cy": 205, "radius": 12, "weight": 0.5},
        ],
        "initial_carrion": [
            {"item": "dead_beetle", "x": 90, "y": 190, "count": 2},
            {"item": "rotten_fruit", "x": 122, "y": 186, "count": 2},
        ],
    }
    b.grid = (3, 0)
    b.neighbors = {"north": "bee_meadow_20", "east": "underground_passages_31",
                   "south": "ant_colony_40"}
    return b


if __name__ == "__main__":
    b = build()
    print("LINT:", *(["0 defects"] if not (d := b.lint()) else ["\n  - " + "\n  - ".join(d[:20])]))
    print("warnings:", len(b.warnings), "| missing_art:", b.missing_art())
    zdir = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "zones", "ant_tunnels_30"))
    os.makedirs(zdir, exist_ok=True)
    render_builder(b, os.path.join(zdir, "full.png"), scale=2)
    print("preview ->", os.path.join(zdir, "full.png"))
    if "--save" in sys.argv:
        print("saved ->", b.save())
