#!/usr/bin/env python3
"""Scene — MINING CAMP: a worked-out cavern the miners have made home. A rail track climbs in from
the south (the way down from the village); ore veins streak the surrounding rock; tunnels branch off
to active digs. Inside, the camp reads in ZONES — a rail-head loading bay (carts, ore piles, sacks),
an ore-processing corner (sluice, forge + anvil, the haul in rows), a cooking/social hearth (fires +
log seats), a sleeping row of tents at the back, and tool storage — all lit by wall torches, a lantern,
and clusters of glow mushrooms. Cave-floor rubble/fungus/moss/bones fill the rest naturally.

Renders to tools/_generated/previews/underground/scene_underground_mining_camp.png (via registry.py).
Run: python3 tools/zonegen/scenes/scene_underground_mining_camp.py
"""
import os
import math
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder                                   # noqa: E402
from render import render_builder                                     # noqa: E402
from features.cave import carve_tunnel, carve_cavern, fill_solid      # noqa: E402

W, H = 56, 60
ORE = {"base": "stone_block",
       "veins": [("ore_copper_block", 6, 3, 5), ("ore_coal_block", 6, 3, 5), ("ore_iron_block", 3, 2, 4)],
       "pockets": [("dirt_block", 8, 4, "top"), ("hard_stone_block", 3, 3, "bottom")]}

# cave-floor dressing (all existing art): weighted bag, clusters glow fungus + rubble
FLOOR_BAG = [("rubble", 10), ("cave_moss", 8), ("mushroom_glow", 6), ("mushroom_blue", 3),
             ("mushroom_brown", 3), ("mushroom_puffball", 2), ("bone_pile", 3), ("quartz_block", 2)]


def build():
    b = ZoneBuilder("scene_underground_mining_camp", W, H, base_tile="cave_floor", name="Mining camp")
    rng = random.Random(9)
    rx, cav_y = W // 2, 24

    # cavern + the rail tunnel climbing from the south + branch digs
    cavern = carve_cavern(b, rx, cav_y, shape="blob", size=15, seed=1)
    rail = carve_tunnel(b, (rx, H - 2), (rx, cav_y + 6), style="straight", width=5)
    outs = set()
    outs |= carve_tunnel(b, (rx - 8, cav_y), (1, cav_y - 4), style="natural", width=2, seed=2)     # west dig
    outs |= carve_tunnel(b, (rx + 8, cav_y), (W - 2, cav_y + 3), style="natural", width=2, seed=3)  # east dig
    outs |= carve_tunnel(b, (rx, cav_y - 9), (rx + 4, 1), style="natural", width=2, seed=4)         # deep dig
    carved = cavern | rail | outs
    fill_solid(b, carved, ORE, seed=5)

    def free_fp(oid, x, y):
        fw, fh = b.footprint(oid)
        return all((x + dx, y + dy) in carved and b.is_free(x + dx, y + dy)
                   for dx in range(fw) for dy in range(fh))

    def put(oid, x, y):
        return b.place_occupant(oid, x, y, surface=None) if free_fp(oid, x, y) else False

    # --- the rail down the track + timber supports flanking it (mining infrastructure) ---
    for y in range(cav_y + 6, H - 1):
        if b.is_free(rx, y):
            b.place_occupant("mine_rail", rx, y, surface=None, reserve=False)
    for y in range(cav_y + 8, H - 2, 5):
        for sx in (rx - 2, rx + 2):
            put("wall_wood", sx, y)

    # === RAIL-HEAD LOADING BAY (where the track meets the cavern, south-centre) ===========
    put("sign_camp", rx + 3, cav_y + 5)
    put("mine_cart", rx - 1, cav_y + 6)
    for oid, x, y in [("ore_pile", rx - 3, cav_y + 5), ("ore_sack", rx - 4, cav_y + 6),
                      ("ore_sack", rx - 3, cav_y + 6), ("wheelbarrow", rx + 1, cav_y + 5),
                      ("mining_bucket", rx + 2, cav_y + 6)]:
        put(oid, x, y)

    # === ORE-PROCESSING CORNER (east) — sluice, forge+anvil, the haul in rows ============
    put("ore_sluice", rx + 7, cav_y - 3)
    put("forge", rx + 8, cav_y + 1)
    put("anvil", rx + 7, cav_y + 3)
    for i, oid in enumerate(["ore_sack", "ore_sack", "ore_pile", "powder_keg"]):
        put(oid, rx + 8 + (i % 2), cav_y - 1 + (i // 2))
    put("crate", rx + 9, cav_y + 3)

    # === COOKING / SOCIAL HEARTH (centre-west) — the warm heart of the camp ==============
    put("campfire_spit", rx - 6, cav_y)
    for s in [(rx - 8, cav_y - 1), (rx - 8, cav_y + 1), (rx - 4, cav_y - 1), (rx - 4, cav_y + 1)]:
        put("log_seat", *s)
    put("campfire", rx + 5, cav_y + 4)
    for s in [(rx + 4, cav_y + 5), (rx + 6, cav_y + 5)]:
        put("log_seat", *s)

    # === SLEEPING ROW (tents along the back / north wall) ================================
    for tx in (rx - 9, rx - 3, rx + 3):
        put("tent", tx, cav_y - 6)

    # === TOOL STORAGE (west edge) =========================================================
    for oid, x, y in [("tool_rack", rx - 10, cav_y + 3), ("crate", rx - 9, cav_y + 4),
                      ("barrel", rx - 8, cav_y + 4), ("ladder", rx - 11, cav_y - 2)]:
        put(oid, x, y)

    # === LIGHTING: wall torches on rock faces, a lantern, glow-fungus clusters ===========
    def is_rock(x, y):
        return b.in_bounds(x, y) and (x, y) not in carved
    faces = [(x, y) for (x, y) in carved if b.is_free(x, y)
             and any(is_rock(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for c in rng.sample(faces, k=min(10, len(faces))):
        b.place_occupant("torch_wall", *c, surface=None)
    put("lantern", rx + 2, cav_y)

    # === CAVE-FLOOR DRESSING (rubble/fungus/moss/bones) — clustered, fills the bare floor ==
    bag = [k for k, n in FLOOR_BAG for _ in range(n)]
    free = [(x, y) for (x, y) in carved if b.is_free(x, y) and (x, y) not in rail]  # keep the track clear
    rng.shuffle(free)
    centers = rng.sample(free, k=min(6, len(free))) if free else []
    placed, target = 0, int(0.12 * len(free))
    for (x, y) in free:
        if placed >= target:
            break
        near = min((math.hypot(x - cx, y - cy) for cx, cy in centers), default=99)
        if rng.random() > (0.85 if near < 3 else 0.18):     # dense in clusters, sparse outside
            continue
        oid = rng.choice(["mushroom_glow", "cave_moss"]) if near < 3 else rng.choice(bag)
        if b.place_occupant(oid, x, y, surface=None, reserve=False):
            placed += 1

    # === CAVE BUGS (mixed facing) =========================================================
    spots = rng.sample(free, k=min(9, len(free))) if free else []
    bugs = ["beetle_common", "beetle_rhino", "cave_spider", "centipede", "cricket", "beetle_stag"]
    for i, (x, y) in enumerate(spots):
        b.place_bug(rng.choice(bugs), float(x), float(y), scale=0.45, flip=(i % 2 == 0))

    # === MINERS at work ===================================================================
    b.place_player("miner_down", rx - 6, cav_y - 2)     # at the cooking fire
    b.place_player("miner_left", rx - 1, cav_y + 7)     # loading the cart
    b.place_player("miner_down", rx + 7, cav_y + 1)     # at the forge

    b.spawn = [rx, H - 3]
    return b


if __name__ == "__main__":
    b = build()
    out = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "underground",
                                       "scene_underground_mining_camp.png"))
    render_builder(b, out, scale=6)
    print("placeholders:", b.missing_art())
    print("warnings:", len(b.warnings))
    print("validate:", b.validate() or "OK")
