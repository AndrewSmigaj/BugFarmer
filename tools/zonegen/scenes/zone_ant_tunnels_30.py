#!/usr/bin/env python3
"""ZONE — ant_tunnels_30 (world slot 3,0; the EASY half-outside ant zone).

Brief: docs/product/zones/ant_tunnels_30.md rev 2. Structure fits the real neighbors
(read from their saved data, not guessed):
- NORTH  = bee_meadow_20: its south edge is OCEAN in the NW (water x0-9, sand x13-19) →
  this zone's NW corner is a sea cove; the rest of the north edge is meadow.
- EAST   = underground_passages_31: its west edge is DIRT+ORE with open tunnels at
  y 95-100 / 122-124 / 158-160 / 168-170 / 201-203 (+ the grass surface strip y237-255).
  This zone's tunnels MEET those rows so the two zones connect.
- SOUTH  = ant_colony_40 (unbuilt): the ant tunnels dig into DIRT and DESCEND south toward
  the colony — the main arteries run to the south edge.
- WEST   = world edge.

ORIENTATION (pinned — burned us 3x): HIGH y = NORTH = top; LOW y = SOUTH = deep.
x=0 = WEST, x=255 = EAST. (zone.go "+Y = north"; sanity: village lake (46,48) IS SW.)
The GAME loads the SAVE not this script: after editing, `--save` + verify north-up with
`view_world ant_tunnels_30`; reset the persisted zone_state record if it won't update.
"""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
sys.path.insert(0, HERE)
from zonebuilder import ZoneBuilder                                   # noqa: E402
from features.terrain import _vnoise, forest                         # noqa: E402
from features.scatter import scatter                                 # noqa: E402
from features.cave import carve_tunnel, carve_chamber, cave_pool     # noqa: E402
from render import render_builder                                    # noqa: E402

ZW = ZH = 256
# EAST tunnel-connection rows (must meet underground_passages_31's west openings):
EAST_STUBS = [97, 123, 159, 169, 202]
SEAM_X = 220          # east of here = the ore-rich rock seam (matches the mining zone)


def surface_y(x, n):
    """The surface↔underground boundary at column x. Rises toward the EAST so the
    underground reaches the high east-edge connection rows (y up to ~210); the WEST stays
    mostly open surface (the forage grounds). Noise-warped — never a ruled line."""
    t = max(0.0, (x - 34)) / (ZW - 1 - 34)
    base = 112 + 126 * (t ** 1.5)                      # west ~112, east ~238
    return base + (n(0.055 * x, 0.0) - 0.5) * 15


def build():
    b = ZoneBuilder("ant_tunnels_30", ZW, ZH, base_tile="grass",
                    name="Ant Tunnels", biome="meadow")
    nb = _vnoise(31)     # boundary warp
    ng = _vnoise(57)     # gradient warp

    # ===== 1. CARVE THE TUNNEL NETWORK (collect carved cells; fill around it after) =====
    # The ants dig into DIRT and descend SOUTH. A main artery drops from the entrance mouth
    # toward the colony (south edge); an east trunk reaches the 5 connection rows; branches
    # end in chambers. Meandering (burrowed), never straight.
    carved = set()
    MOUTH = (112, int(surface_y(112, nb)))             # main mouth on the surface boundary
    # main artery: mouth -> deep south (toward ant_colony_40)
    carved |= carve_tunnel(b, MOUTH, (98, 8), width=3, seed=201, wobble=0.6)
    # a crossroads a little below the mouth
    JUNC = (120, 108)
    carved |= carve_tunnel(b, MOUTH, JUNC, width=3, seed=202, wobble=0.5)
    # east trunk from the junction toward the seam, then a spur to each east stub row
    ETRUNK = (206, 150)
    carved |= carve_tunnel(b, JUNC, ETRUNK, width=3, seed=203, wobble=0.5)
    for i, ys in enumerate(EAST_STUBS):
        # width 3 so the connection to the mining zone stays open (never tapers to 1 at x255)
        carved |= carve_tunnel(b, ETRUNK, (ZW - 1, ys), width=3, seed=210 + i, wobble=0.4)
    # southern branches (the colony thickens down): two descending side tunnels
    carved |= carve_tunnel(b, JUNC, (150, 10), width=2, seed=220, wobble=0.6)
    carved |= carve_tunnel(b, (100, 70), (60, 8), width=2, seed=221, wobble=0.6)
    # CHAMBERS off the network (fungus garden / granary / brood / crossroads pocket)
    CH = {"crossroads": (120, 106), "fungus": (150, 78), "granary": (92, 60), "brood": (128, 40)}
    for name, (cx, cy) in CH.items():
        carved |= carve_chamber(b, cx, cy, 7 if name != "brood" else 6, seed=hash(name) % 999)

    # ===== 2. FILL THE UNDERGROUND MASS around the tunnels (dirt soil + east ore seam) ====
    # Below the surface boundary: solid dirt_block ants dig (C2 diggable); the far east is
    # the ORE-rich rock seam (dirt_block + veins + stone) that matches the mining zone.
    rng = random.Random(30)
    ore_common = ["ore_copper_block", "ore_coal_block", "ore_iron_block"]
    ore_rare = ["ore_silver_block", "ore_gold_block"]
    for y in range(ZH):
        for x in range(ZW):
            yc = surface_y(x, nb)
            if y > yc:
                continue                                # surface handled below
            if (x, y) in carved:
                b.set_ground(x, y, "cave_floor", surface="grass")
                continue
            b.set_ground(x, y, "cave_floor", surface="grass")
            # block choice: dirt soil everywhere; the east seam adds stone + ore veins
            if x >= SEAM_X:
                r = rng.random()
                if r < 0.10: blk = rng.choice(ore_common)
                elif r < 0.13: blk = rng.choice(ore_rare)
                elif r < 0.45: blk = "stone_block"
                else: blk = "dirt_block"
            else:
                # stray ore scattered thinly in the soil (owner: "stray ore is great")
                r = rng.random()
                blk = rng.choice(ore_common) if r < 0.03 else "dirt_block"
            b.place_occupant(blk, x, y)

    # a damp POOL in a low chamber (echoes the mining zone's west water body)
    cave_pool(b, 150, 78, 4, carved, seed=61)

    # ===== 3. SURFACE: ocean cove (NW), grass→dirt gradient, forage grounds ==============
    # 3a. The SEA COVE in the NW — continues bee_meadow's south-edge ocean (water x0-9 at the
    # north edge) into a small cove with a sand beach.
    for y in range(ZH):
        for x in range(ZW):
            if y <= surface_y(x, nb):
                continue
            # cove: a small sea in the NW corner that MATCHES bee_meadow's south-edge
            # profile at the seam (water x0-9, shallow x10-12, sand x13-19), widening a
            # little as it reaches south into the zone.
            d = math.hypot((x - 0) / 12.0, (y - 256) / 22.0)
            edge = 1.0 + (ng(0.12 * x, 0.12 * y) - 0.5) * 0.4
            if d < edge * 0.82:
                b.set_ground(x, y, "water_deep", surface="water")
            elif d < edge:
                b.set_ground(x, y, "water_shallow", surface="water")
            elif d < edge + 0.18:
                b.set_ground(x, y, "sand", surface="grass")

    # 3b. grass→dirt gradient: grass at the north (bee seam), dirtying toward the underground
    for y in range(ZH):
        for x in range(ZW):
            if y <= surface_y(x, nb) or b.surface[y][x] == "water":
                continue
            yc = surface_y(x, nb)
            north_span = max(1.0, (ZH - 1) - yc)
            t = (y - yc) / north_span                   # 0 at boundary, 1 at north edge
            dirtiness = (1.0 - t) + (ng(0.05 * x, 0.05 * y) - 0.5) * 0.5
            if b.ground[y][x] == "grass" and dirtiness > 0.5:
                b.set_ground(x, y, "dirt", surface="grass")

    # 3c. FORAGE GROUNDS: spread forest stands (clearings between — C16/C7), fruit trees with
    # windfall rings, berry scrub. Light density — the trail show wants open room.
    for (fx, fy, fw, fh, dens, seed) in [
        (60, 215, 22, 15, 0.42, 71), (150, 210, 24, 16, 0.40, 72),
        (40, 165, 18, 13, 0.38, 73), (110, 175, 20, 13, 0.36, 74),
        (185, 205, 15, 11, 0.40, 75),
    ]:
        forest(b, fx, fy, fw, fh, density=dens, seed=seed)
    for (tx, ty) in [(70, 195), (120, 185), (170, 198), (50, 150), (150, 158)]:
        if b.in_bounds(tx, ty) and b.is_free(tx, ty) and b.surface[ty][tx] == "grass":
            b.place_occupant("tree_apple", tx, ty)
    scatter(b, 30, 130, 232, 250, {"wild_berry_bush": 3, "tall_grass": 5, "bush": 2, "clover": 3},
            density=0.03, min_spacing=3, seed=76, clumping=0.6, cluster_radius=5)

    # ===== 4. THE MOUTH lip (dirt-block mound forms framing the main mouth, per owner) =====
    mx, my = MOUTH
    for dx in (-2, -1, 2, 3):
        for dy in (0, 1):
            px, py = mx + dx, my + dy
            if b.in_bounds(px, py) and b.is_free(px, py) and b.surface[py][px] == "grass":
                b.place_occupant("dirt_block", px, py)

    # ===== 5. bug_spawning (ants on the surface forage; a light centipede den) ============
    b.bug_spawning = {
        "species_caps": {
            "ant_worker": {"initial": 4, "max": 10, "max_population": 40, "min_population": 2, "swarm_size": 3},
            "ant_scout":  {"initial": 2, "max": 4,  "max_population": 8,  "min_population": 1, "swarm_size": 1},
            "centipede_garden": {"initial": 1, "max": 2, "max_population": 4, "min_population": 0, "swarm_size": 1},
        },
        "spawn_areas": [
            {"id": "ants_outside", "species": ["ant_worker"], "type": "circle", "cx": 110, "cy": 185, "radius": 42, "weight": 1.0},
            {"id": "scouts", "species": ["ant_scout"], "type": "circle", "cx": 120, "cy": 175, "radius": 55, "weight": 1.0},
            {"id": "cent_den", "species": ["centipede_garden"], "type": "circle", "cx": 200, "cy": 205, "radius": 12, "weight": 0.5},
        ],
        "initial_carrion": [
            {"item": "dead_beetle", "x": 80, "y": 190, "count": 2},
            {"item": "rotten_fruit", "x": 122, "y": 186, "count": 2},
        ],
    }

    b.grid = (3, 0)
    b.neighbors = {"north": "bee_meadow_20", "east": "underground_passages_31"}
    b.spawn = [140, 246]    # arrive on the north meadow (bee seam)
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
