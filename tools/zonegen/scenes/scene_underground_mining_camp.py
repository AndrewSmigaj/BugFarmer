#!/usr/bin/env python3
"""Scene — MINING HUB: the deep, second mining camp the rail tunnel from the surface entrance feeds into.
A torch-lit man-made RAIL shaft drops in from the north (the way up to the village); it opens into a big
worked cavern. The hub reads in distinct WORK-ZONES (camps.md cluster rules):
- RAIL-HEAD LOADING BAY at the shaft mouth (a cart ON the rail, ore piles/sacks, wheelbarrow, sign);
- an ORE-PROCESSING LINE along the east wall — crusher -> wash -> smelt in sequence (stonecutter crushes,
  ore_sluice washes, furnace smelts) fed by ore bins, with the bar/sack haul staged out;
- a COOKING/SOCIAL hearth (campfire + log seats + pot) in the warm centre;
- a SLEEPING row of tents along the deep wall (+ stash + lantern);
- TOOL STORAGE on the west wall.
Lit by wall torches around the cavern faces + clustered glow-fungus. Ore is in rarity VEINS.
(Dedicated rock_crusher art is backlogged; stonecutter stands in.)

Terrain vs. props are split so the ZONE (zone_underground_passages) can own the rock/ore: `carve_hub(b,ox,oy)`
carves the cavern + rail tunnel + branch digs + pool + interior columns (returns a dict); `place_hub(b, hub)`
drops the work-zone props + lighting + bugs (NO timber struts). `build()` renders the standalone vignette.
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
from features.cave import carve_tunnel, carve_cavern, fill_solid, place_pool   # noqa: E402

W, H = 56, 60
ORE = {"base": "stone_block",
       "veins": [("ore_copper_block", 7, 3, 6), ("ore_coal_block", 7, 3, 6), ("ore_iron_block", 4, 2, 4)],
       "pockets": [("dirt_block", 6, 4, "top")]}

# open-floor dressing — EARTHTONES ONLY + sparse (rubble/moss/bone); ALL fungus stays in the wall clumps
# below, never sprinkled mid-floor as green confetti. (quartz is a WALL mineral — embedded in rock faces.)
FLOOR_BAG = [("rubble", 12), ("cave_moss", 7), ("bone_pile", 3)]


PREVIEW = "zones/underground_passages_31/scenes"
SCALE = 6


def carve_hub(b, ox, oy):
    """Carve the worked cavern (overlapping lobes = organic outline + work-zone alcoves), the man-made rail
    tunnel dropping in from the north, branch digs, a still pool, and a few interior rock columns. All in
    GLOBAL coords at offset (ox,oy). Returns a dict the caller uses to lay rail + dress. Does NOT fill_solid
    (the caller owns the rock) and does NOT lay rail occupants/struts (the caller lays the rail)."""
    rx, cy = ox + W // 2, oy + 22                          # shaft centreline + cavern centre (north-ish)
    cavern = carve_cavern(b, rx, cy, shape="blob", size=15, seed=1)
    cavern |= carve_cavern(b, rx - 11, cy + 1, shape="blob", size=6, seed=11)    # west alcove (hearth/tools)
    cavern |= carve_cavern(b, rx + 11, cy, shape="rocky", size=6, seed=12)       # east alcove (processing)
    cavern |= carve_cavern(b, rx - 2, cy - 10, shape="long", size=7, seed=13)    # deep-south alcove (sleeping)
    rail = carve_tunnel(b, (rx, oy + H - 2), (rx, cy + 8), style="straight", width=5)
    rail_head = cy + 8                                     # where the shaft meets the cavern (north end)
    outs = set()
    outs |= carve_tunnel(b, (rx - 11, cy + 2), (ox + 1, cy - 3), style="natural", width=2, seed=2)     # west
    outs |= carve_tunnel(b, (rx + 11, cy + 1), (ox + W - 2, cy + 5), style="natural", width=2, seed=3)  # east
    outs |= carve_tunnel(b, (rx - 4, cy - 11), (rx + 5, oy + 1), style="natural", width=2, seed=4)      # deep
    carved = cavern | rail | outs
    pool = place_pool(b, rx - 9, cy - 7, 3, 2, carved, seed=6)        # a still pool in a deep corner
    for (cxp, cyp) in [(rx - 5, cy - 4), (rx + 5, cy + 6), (rx - 4, cy - 7)]:    # interior columns
        for dy in (0, 1):
            if (cxp, cyp + dy) in cavern and (cxp, cyp + dy) not in pool and b.is_free(cxp, cyp + dy):
                b.place_occupant("stone_block", cxp, cyp + dy)
    return {"carved": carved, "cavern": cavern, "rail": rail, "pool": pool,
            "rail_head": rail_head, "rx": rx, "cy": cy}


def place_hub(b, hub):
    """Drop the hub's work-zone props + lighting + cave bugs (no timber struts). Call AFTER carve_hub +
    fill_solid so `is_free` rejects anything landing on rock or water."""
    rng = random.Random(9)
    rx, cy, rail_head = hub["rx"], hub["cy"], hub["rail_head"]
    carved, rail, pool = hub["carved"], hub["rail"], hub["pool"]

    def is_rock(x, y):
        return b.in_bounds(x, y) and (x, y) not in carved

    def free_fp(oid, x, y):
        fw, fh = b.footprint(oid)
        return all(b.is_free(x + dx, y + dy) for dx in range(fw) for dy in range(fh))

    def put(oid, x, y):
        return b.place_occupant(oid, x, y, surface=None) if free_fp(oid, x, y) else False

    # === RAIL-HEAD LOADING BAY (north, at the shaft mouth) — a cart ON the rail + the haul =========
    put("sign_camp", rx + 3, rail_head + 1)
    if free_fp("mine_cart", rx, rail_head + 2):
        b.place_occupant("mine_cart", rx, rail_head + 2, surface=None)     # a cart sitting ON the rail
    put("mine_cart", rx - 3, rail_head)                                    # a second cart on a siding
    for oid, x, y in [("ore_pile", rx - 4, rail_head + 1), ("ore_sack", rx - 5, rail_head),
                      ("ore_sack", rx - 4, rail_head), ("wheelbarrow", rx + 2, rail_head + 2),
                      ("mining_bucket", rx + 4, rail_head + 1), ("ladder", rx + 5, rail_head)]:
        put(oid, x, y)

    # === ORE-PROCESSING LINE (east wall) — a clean vertical SEQUENCE: crusher -> wash -> smelt ======
    px = rx + 9
    put("coal_bin", px, cy + 6)                           # raw-ore bin feeding the head of the line
    put("stonecutter", px, cy + 4)                        # CRUSHER (stonecutter stands in — see header)
    put("ore_sluice", px, cy + 1)                         # WASH
    put("furnace", px, cy - 2)                            # SMELT
    put("anvil", px, cy - 5)                              # work the bars
    put("compost_bin", px + 2, cy + 4)                    # tailings/spoil bin beside the crusher
    put("ore_pile", px - 2, cy + 4)                       # raw haul waiting at the crusher
    put("ore_sack", px - 2, cy + 5)
    for i, oid in enumerate(["crate", "ore_sack", "barrel"]):
        put(oid, px + 2, cy - 1 - i)                      # finished goods staged out past the smelter
    put("powder_keg", px + 2, cy + 1)
    b.place_player("miner_down", px - 1, cy + 1)          # working the wash
    b.place_player("miner_down", px - 1, cy - 2)          # working the smelter

    # === COOKING / SOCIAL HEARTH (warm centre-west) ===============================================
    hx, hy = rx - 7, cy + 1
    put("campfire_spit", hx, hy)
    put("cooking_pot", hx + 1, hy)
    for s in [(hx - 2, hy - 1), (hx - 2, hy + 1), (hx + 2, hy - 1), (hx, hy + 2)]:
        put("log_seat", *s)
    put("barrel", hx - 2, hy + 2)
    b.place_player("miner_left", hx + 1, hy - 1)          # at the fire

    # === SLEEPING ROW (tents along the deep / south wall) + stash =================================
    for tx in (rx - 8, rx - 2, rx + 4):
        put("tent", tx, cy - 8)
    put("chest_wood", rx + 7, cy - 8)
    put("lantern", rx - 5, cy - 7)

    # === TOOL STORAGE (west wall) =================================================================
    for oid, x, y in [("tool_rack", rx - 12, cy + 1), ("crate", rx - 11, cy + 2),
                      ("barrel", rx - 12, cy + 3), ("ladder", rx - 13, cy - 2)]:
        put(oid, x, y)

    # === LIGHTING: wall torches generously around the cavern faces + a lantern ====================
    faces = [(x, y) for (x, y) in carved if b.is_free(x, y) and (x, y) not in pool
             and any(is_rock(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    rng.shuffle(faces)
    lit = []
    for c in faces:
        if len(lit) >= 16:
            break
        if any(math.hypot(c[0] - lx, c[1] - ly) < 5 for lx, ly in lit):   # spaced out, not bunched
            continue
        if b.place_occupant("torch_wall", *c, surface=None):
            lit.append(c)
    put("lantern", rx + 1, rail_head)
    # quartz seams embedded in the rock faces (a wall mineral, sparse)
    for c in faces:
        if c not in lit and b.is_free(*c) and rng.random() < 0.025:
            b.place_occupant("quartz_block", *c, surface=None)

    # === CAVE-FLOOR DRESSING — SPARSE; glow-fungus in a few wall clumps, rubble/moss elsewhere ====
    bag = [k for k, n in FLOOR_BAG for _ in range(n)]
    free = [(x, y) for (x, y) in carved if b.is_free(x, y) and (x, y) not in rail and (x, y) not in pool]
    rng.shuffle(free)
    # glow-fungus clumps tucked against the rock walls (light pools, not floor confetti)
    wall_cells = [c for c in free if any(is_rock(c[0] + dx, c[1] + dy)
                  for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    clumps = []
    for c in wall_cells:
        if len(clumps) >= 6:
            break
        if any(math.hypot(c[0] - gx, c[1] - gy) < 6 for gx, gy in clumps):
            continue
        clumps.append(c)
    glowset = set()
    for (gx, gy) in clumps:
        for (x, y) in free:
            if math.hypot(x - gx, y - gy) <= 2.0 and rng.random() < 0.55 and b.is_free(x, y):
                if b.place_occupant(rng.choice(["mushroom_glow", "mushroom_glow", "mushroom_blue",
                                                "mushroom_brown", "cave_moss"]), x, y, surface=None):
                    glowset.add((x, y))
    # the rest: a light rubble/moss/bone scatter (low density, keeps the camp readable)
    placed, target = 0, int(0.05 * len(free))
    for (x, y) in free:
        if placed >= target:
            break
        if (x, y) in glowset or not b.is_free(x, y):
            continue
        if rng.random() < 0.5 and b.place_occupant(rng.choice(bag), x, y, surface=None, reserve=False):
            placed += 1

    # === CAVE BUGS (mixed facing, off the track) ==================================================
    spots = rng.sample([c for c in free if b.is_free(*c)], k=min(8, len(free)))
    bugs = ["beetle_common", "beetle_rhino", "cave_spider", "centipede", "cricket", "beetle_stag"]
    for i, (x, y) in enumerate(spots):
        b.place_bug(rng.choice(bugs), float(x), float(y), scale=0.45, flip=(i % 2 == 0))


def build():
    b = ZoneBuilder("scene_underground_mining_camp", W, H, base_tile="cave_floor", name="Mining hub")
    hub = carve_hub(b, 0, 0)
    fill_solid(b, hub["carved"], ORE, seed=5)
    # the rail down the shaft + WALL TORCHES flanking it (lit, built infrastructure — no timber struts)
    rx, rail_head = hub["rx"], hub["rail_head"]
    for y in range(rail_head, H - 1):
        if b.is_free(rx, y):
            b.place_occupant("mine_rail", rx, y, surface=None, reserve=False)
    for y in range(rail_head + 5, H - 2, 6):
        for sx in (rx - 2, rx + 2):
            if (sx, y) in hub["carved"] and b.is_free(sx, y) \
                    and ((sx - 1, y) not in hub["carved"] or (sx + 1, y) not in hub["carved"]):
                b.place_occupant("torch_wall", sx, y, surface=None)
    place_hub(b, hub)
    b.spawn = [rx, H - 3]
    return b


if __name__ == "__main__":
    from scene_preview import render
    b = build()
    print("LINT:", b.lint() or "0 defects", "| missing_art:", b.missing_art())
    render(b, __file__, PREVIEW, SCALE)
