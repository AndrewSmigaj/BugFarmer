#!/usr/bin/env python3
"""ZONE — underground_passages_31: the first underground "Mining Camp" (world slot 3,1; north→village_21_B).

Layout (per docs/product/economy/zones/underground_passages.md + DECISIONS D17–D21):
a thin SURFACE strip at the north edge (the seam from the village) holds a small open-air mining CAMP —
tents, forge+anvil, the ore_sluice + hand_pump drawing from a small POND, containers, a signpost — then a
straight RAIL tunnel descends south into the carved mine: a main camp cavern, a few natural caverns joined
by burrowed tunnels, side digs, the rail continuing a little deeper. The LEFT third is soft DIRT (where the
ant tunnels reach in from the col-0 colony), blending through a natural interface into ROCK to the right and
deeper. Cave critters (centipedes / millipedes / cave beetles) live in the caverns on a glow-mushroom +
carrion food base.

    python3 tools/zonegen/scenes/zone_underground_passages.py            # build + lint + render to /tmp
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
from features.terrain import noise_field, pond, route_road                  # noqa: E402
from features.cave import carve_tunnel, carve_cavern, fill_solid, place_pool  # noqa: E402

ZW = ZH = 256
SURF = 30          # north surface strip y < SURF (grass + the open-air camp + pond)
DIRT_X = 78        # left of here is soft dirt (wobbled); the dirt↔rock interface

# Ore for the beginning mining zone (caves.md table): copper/coal common, iron uncommon, tin/silver rare.
ORE = {
    "base": "stone_block",
    "veins": [("ore_copper_block", 46, 3, 6), ("ore_coal_block", 46, 3, 6), ("ore_iron_block", 26, 3, 5),
              ("ore_tin_block", 12, 2, 3), ("ore_silver_block", 10, 2, 3)],
    "pockets": [("hard_stone_block", 12, 4, "bottom")],   # tougher rock deep/south (dirt is the substrate)
}

FLOOR_BAG = [("rubble", 10), ("cave_moss", 8), ("mushroom_glow", 7), ("mushroom_blue", 3),
             ("mushroom_brown", 3), ("bone_pile", 3), ("quartz_block", 2), ("crystal_small", 2)]


def build(zone_id="underground_passages_31"):
    b = ZoneBuilder(zone_id, ZW, ZH, base_tile="cave_floor", name="Underground Passages", biome="cave", seed=31)
    rng = random.Random(31)
    sub_nf = noise_field(ZW, ZH, wavelength=20, octaves=3, seed=131)   # wobble the dirt/rock interface

    def substrate(x, y):
        edge = DIRT_X + int(20 * (float(sub_nf[y][x]) - 0.5) * 2)
        if x < edge:
            return "dirt_block"
        if y > 188:
            return "hard_stone_block"
        return "stone_block"

    carved = set()

    # --- NORTH SURFACE STRIP: grass apron + the open-air camp + a pond --------------------------------
    for y in range(0, SURF):
        for x in range(ZW):
            b.set_ground(x, y, "grass", surface="grass")
            carved.add((x, y))
    # a small pond on the east of the camp (the sluice's water source), ~7x5 of water
    pcx, pcy = 168, 16
    pond(b, pcx, pcy, 4, 3, seed=7)
    # a short dirt road from the north edge (the village seam) down to the cave mouth
    route_road(b, (128, 1), (128, SURF - 1), width=3, tile="dirt", seed=9)

    # --- THE MINE: a straight rail tunnel down + caverns joined by burrowed tunnels -------------------
    mouth = carve_cavern(b, 128, SURF + 6, shape="rocky", size=12, seed=2)        # cave mouth at the surface
    rail = carve_tunnel(b, (128, SURF - 1), (128, 104), style="straight", width=5)  # rail descends
    camp = carve_cavern(b, 128, 112, shape="rocky", size=30, seed=3)             # main camp cavern
    rail2 = carve_tunnel(b, (128, 130), (132, 176), style="straight", width=4)    # rail continues deeper
    cav = {
        "w":  carve_cavern(b, 62, 150, shape="blob",  size=26, seed=11),
        "e":  carve_cavern(b, 190, 138, shape="lobed", size=24, seed=12),
        "sw": carve_cavern(b, 96, 206, shape="blob",  size=26, seed=13),
        "se": carve_cavern(b, 188, 200, shape="rocky", size=22, seed=14),
        "deep": carve_cavern(b, 134, 196, shape="blob", size=20, seed=15),
    }
    tunnels = set()
    tunnels |= carve_tunnel(b, (104, 112), (78, 150),  style="natural", width=2, seed=21)  # camp→W
    tunnels |= carve_tunnel(b, (152, 112), (176, 138), style="natural", width=2, seed=22)  # camp→E
    tunnels |= carve_tunnel(b, (118, 134), (100, 192), style="natural", width=2, seed=23)  # camp→SW
    tunnels |= carve_tunnel(b, (176, 150), (188, 188), style="natural", width=2, seed=24)  # E→SE
    tunnels |= carve_tunnel(b, (132, 176), (134, 190), style="natural", width=2, seed=25)  # rail2→deep
    # side digs (short dead-end mining tunnels into the rock)
    for sd in [((150, 108), (180, 92), 31), ((108, 116), (84, 96), 32), ((196, 142), (224, 150), 33),
               ((80, 158), (40, 150), 34), ((96, 220), (90, 248), 35)]:
        tunnels |= carve_tunnel(b, sd[0], sd[1], style="natural", width=2, seed=sd[2])
    # ANT TUNNELS — two narrow burrows through the left dirt, reaching in from the col-0 edge (ants deferred)
    ant = set()
    ant |= carve_tunnel(b, (0, 120), (62, 138), style="natural", width=2, seed=41, wobble=0.7)
    ant |= carve_tunnel(b, (0, 170), (70, 160), style="natural", width=2, seed=42, wobble=0.7)

    carved |= mouth | rail | camp | rail2 | tunnels | ant
    for c in cav.values():
        carved |= c

    # a still pool in the SW cavern low spot
    place_pool(b, 96, 210, 5, 3, carved, seed=6)

    fill_solid(b, carved, ORE, seed=5, substrate=substrate)

    # ---- placement helpers (only onto open, free cave/grass cells) ----------------------------------
    def free_fp(oid, x, y):
        fw, fh = b.footprint(oid)
        return all((x + dx, y + dy) in carved and b.is_free(x + dx, y + dy)
                   for dx in range(fw) for dy in range(fh))

    def put(oid, x, y):
        return b.place_occupant(oid, x, y, surface=None) if free_fp(oid, x, y) else False

    # ---- SURFACE CAMP (open-air, at the entrance) ---------------------------------------------------
    put("signpost", 122, 6)
    put("notice_board", 134, 6)
    for tx in (108, 116, 124):
        put("tent", tx, 8)
    put("forge", 144, 10)
    put("anvil", 148, 12)
    put("ore_sluice", 160, 12)             # beside the pond, water source to its east
    put("hand_pump", 164, 14)              # draws from the pond (the tube; crank-charged later)
    for oid, x, y in [("coal_bin", 150, 16), ("coal_bin", 152, 16), ("powder_keg", 154, 16)]:  # the "crushing bins" (dedicated rock_crusher art = TODO)
        put(oid, x, y)
    for oid, x, y in [("crate", 112, 14), ("barrel", 114, 16), ("coal_bin", 140, 16),
                      ("tool_rack", 106, 12), ("ore_sack", 156, 18), ("ore_pile", 158, 18)]:
        put(oid, x, y)

    # ---- RAIL down the man-made tunnel + timber supports -------------------------------------------
    for y in range(SURF, 130):
        if (128, y) in carved and b.is_free(128, y):
            b.place_occupant("mine_rail", 128, y, surface=None, reserve=False)
    for y in range(SURF + 4, 128, 6):
        for sx in (125, 131):
            put("mine_support", sx, y) or put("wall_wood", sx, y)
    for y in range(132, 176, 4):
        if (132, y) in carved and b.is_free(132, y):
            b.place_occupant("mine_rail", 132, y, surface=None, reserve=False)

    # ---- MAIN CAMP CAVERN (down in the mine): outpost + equipment ----------------------------------
    put("sign_camp", 134, 106)
    put("mine_cart", 124, 108)
    for oid, x, y in [("ore_pile", 118, 110), ("ore_sack", 116, 112), ("wheelbarrow", 138, 110),
                      ("mining_bucket", 140, 112), ("campfire", 120, 118), ("crate", 144, 116),
                      ("barrel", 146, 116), ("lantern", 130, 114), ("lumber_rack", 112, 118)]:
        put(oid, x, y)
    for s in [(118, 120), (122, 120), (118, 116)]:
        put("log_seat", *s)

    # ---- LIGHTING: wall torches on rock faces around every cavern ---------------------------------
    def is_rock(x, y):
        return b.in_bounds(x, y) and (x, y) not in carved
    faces = [(x, y) for (x, y) in carved if b.is_free(x, y)
             and any(is_rock(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for c in rng.sample(faces, k=min(60, len(faces))):
        b.place_occupant("torch_wall", *c, surface=None, reserve=False)

    # ---- DRESSING: glow fungus / moss / bones / crystals, clustered through the caverns ------------
    bag = [k for k, n in FLOOR_BAG for _ in range(n)]
    railset = rail | rail2
    free = [(x, y) for (x, y) in carved if b.is_free(x, y) and (x, y) not in railset and y >= SURF]
    rng.shuffle(free)
    centers = rng.sample(free, k=min(40, len(free))) if free else []
    placed, target = 0, int(0.10 * len(free))
    for (x, y) in free:
        if placed >= target:
            break
        near = min((abs(x - cx) + abs(y - cy) for cx, cy in centers), default=99)
        if rng.random() > (0.8 if near < 4 else 0.10):
            continue
        oid = rng.choice(["mushroom_glow", "cave_moss"]) if near < 4 else rng.choice(bag)
        if b.place_occupant(oid, x, y, surface=None, reserve=False):
            placed += 1

    # ---- BUGS + spawning ---------------------------------------------------------------------------
    b.place_player("miner_down", 122, 116)
    b.place_player("miner_left", 158, 12)
    b.spawn = [128, 10]    # the surface apron, by the road in from the village

    # caverns as the spawn habitats; centipede=cave centipede, beetle_carrion=cave beetle, millipede=cave millipede
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
            circ(62, 150, 20, "millipede", 3.0, "milli_w"),
            circ(96, 206, 20, "millipede", 3.0, "milli_sw"),
            circ(190, 138, 18, "beetle_carrion", 3.0, "beetle_e"),
            circ(188, 200, 16, "beetle_carrion", 3.0, "beetle_se"),
            circ(128, 112, 22, "centipede_garden", 3.0, "cent_camp"),
            circ(134, 196, 16, "centipede_garden", 3.0, "cent_deep"),
            {"id": "milli_wild", "species": ["millipede"], "type": "zone", "weight": 0.4},
            {"id": "beetle_wild", "species": ["beetle_carrion"], "type": "zone", "weight": 0.4},
            {"id": "cent_wild", "species": ["centipede_garden"], "type": "zone", "weight": 0.4},
        ],
        "initial_carrion": [
            {"item": "dead_millipede", "x": 96, "y": 206, "count": 2},
            {"item": "dead_beetle", "x": 190, "y": 138, "count": 2},
        ],
    }
    return b


if __name__ == "__main__":
    b = build()
    print("LINT:", *(["0 defects"] if not (defects := b.lint()) else ["\n  - " + "\n  - ".join(defects[:20])]))
    print("warnings:", len(b.warnings), "| missing_art:", b.missing_art())
    print("validate:", b.validate() or "ok")
    # Canonical preview location — tools/_generated/previews/zones/<zone>/ (surfaced in previews/index.html),
    # NOT /tmp. Renders here on every run so the PNG is always findable next to the other zones.
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
