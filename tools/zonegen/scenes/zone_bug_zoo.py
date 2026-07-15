#!/usr/bin/env python3
"""ZONE — bug_zoo: ONE observation zone that replaces the scattered per-bug labs.

A tidy 3x3 grid of small SEALED pens (one chunk / 32x32 each — big enough to spawn a wasp in and watch a
hunt), each holding its species' REAL habitat, with walkways to stroll between them and study each pen from
over the fence. The zone is PEACEFUL (bugs ignore the player), so lifecycles play out naturally while you
watch — flies going to food and laying into a shared ground brood, wasps homing to their nest, etc. Spawn
extra bugs into a pen with the F8 debug spawner to stage a matchup (drop a wasp into the fly pen).

Standalone test zone (world-grid row/col 0,0); load in-game via world_create {"zone_id": "bug_zoo"}.
Only the six species in nakama/data/species.json spawn; peaceful + ephemeral_swarms ride the additive
ZoneBuilder.save() flags.

    python3 tools/zonegen/scenes/zone_bug_zoo.py            # build + lint + render to /tmp
    python3 tools/zonegen/scenes/zone_bug_zoo.py --save     # also write nakama/data/zones/bug_zoo/
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
sys.path.insert(0, HERE)
from zonebuilder import ZoneBuilder                        # noqa: E402
from render import render_builder                          # noqa: E402
from features.yard import fence_rect                       # noqa: E402

ZW = ZH = 128            # 4x4 chunks (~1/4 of a real zone; ~25 s to cross)
PEN = 32                 # each pen = one chunk
STEP = 46                # pen-origin stride: 32 pen + 14 walkway
ORIGIN = 2               # first pen origin (2-cell border)
TREES = ["tree_plum", "tree_cherry", "tree_apple"]   # mixed fruit -> a steadier fly-food supply


def pen_box(col, row):
    x0 = ORIGIN + col * STEP
    y0 = ORIGIN + row * STEP
    return x0, y0, x0 + PEN - 1, y0 + PEN - 1   # inclusive


def build(zone_id="bug_zoo"):
    b = ZoneBuilder(zone_id, ZW, ZH, base_tile="grass", biome="meadow", name="Bug Zoo", seed=4242)
    b.peaceful = True             # observation zone: bugs ignore the player
    b.ephemeral_swarms = True     # re-seed the initial population each load (a reproducible study)
    b.spawn = [ZW // 2, 40]       # a central walkway between the top two pen rows

    species_caps, spawn_areas = {}, []

    def seal(col, row, fence="fence_wood"):
        """Fence a SEALED pen (no gate — observed over the low fence); return its centre cell."""
        x0, y0, x1, y1 = pen_box(col, row)
        fence_rect(b, x0, y0, x1, y1, gate=None, fence=fence)
        return (x0 + x1) // 2, (y0 + y1) // 2

    def cap(species, initial, mx, mxpop, swarm, minpop=0, **extra):
        c = {"initial": initial, "max": mx, "max_population": mxpop, "swarm_size": swarm,
             "min_population": minpop, "spawn_interval": 999999.0}
        c.update(extra)
        species_caps[species] = c

    def spawn(sid, species, cx, cy, r=6):
        spawn_areas.append({"id": sid, "species": [species], "type": "circle",
                            "cx": cx, "cy": cy, "radius": r, "weight": 1.0})

    def trees(cx, cy, cells):
        for i, (dx, dy) in enumerate(cells):
            b.place_occupant(TREES[i % len(TREES)], cx + dx, cy + dy)

    # -- Row 0: the easy ground-brood breeders + the wasp -------------------------------------------
    cx, cy = seal(0, 0)                                    # FLY: compost + orchard rot -> a shared ground brood
    b.place_occupant("compost_bin", cx, cy)
    trees(cx, cy, [(-7, -6), (7, -6), (-7, 6), (7, 6)])
    cap("fly_common", 24, 12, 80, 6, minpop=12); spawn("fly_pen", "fly_common", cx, cy)

    cx, cy = seal(1, 0)                                    # BUTTERFLY: breeds on milkweed, sips nectar
    b.place_occupant("milkweed", cx, cy)
    for dx, dy in [(-6, -5), (6, -5), (-6, 5), (6, 5)]:
        b.place_occupant("flower_wild", cx + dx, cy + dy)
    cap("butterfly_meadow", 6, 6, 30, 6); spawn("butterfly_pen", "butterfly_meadow", cx, cy)

    cx, cy = seal(2, 0)                                    # WASP: nest-founded, hunting a resident fly base
    b.place_occupant("wasp_nest", cx, cy - 5)
    trees(cx, cy + 3, [(-7, 0), (0, 4), (7, 0)])
    cap("wasp_common", 0, 8, 40, 4, max_nests=2); spawn("wasp_pen", "wasp_common", cx, cy - 5, r=4)
    spawn("wasp_prey", "fly_common", cx, cy + 6)

    # -- Row 1: the hunter + the two detritivores ---------------------------------------------------
    cx, cy = seal(0, 1, fence="fence_stone")              # CENTIPEDE (stone: it gnaws wood): hunts flies
    trees(cx, cy, [(-7, -6), (7, -6), (0, 6)])
    cap("centipede_garden", 2, 6, 20, 1); spawn("centipede_pen", "centipede_garden", cx, cy - 6)
    spawn("centipede_prey", "fly_common", cx, cy + 6)

    cx, cy = seal(1, 1)                                    # MILLIPEDE: detritus (leaf litter)
    for dx, dy in [(-6, -6), (6, -6), (0, 0), (-6, 6), (6, 6)]:
        b.place_occupant("leaf_litter", cx + dx, cy + dy)
    cap("millipede", 4, 8, 40, 1); spawn("millipede_pen", "millipede", cx, cy)

    cx, cy = seal(2, 1)                                    # BEETLE: carrion (flies die -> corpses it eats)
    trees(cx, cy, [(-7, -6), (7, -6), (0, 6)])
    cap("beetle_carrion", 4, 8, 40, 1); spawn("beetle_pen", "beetle_carrion", cx, cy - 6)
    spawn("beetle_prey", "fly_common", cx, cy + 6)

    # -- Row 2: empty staging pens (fence only) — spawn anything here (F8) to stage a matchup --------
    seal(0, 2); seal(1, 2); seal(2, 2)

    b.bug_spawning = {"species_caps": species_caps, "spawn_areas": spawn_areas}
    return b


if __name__ == "__main__":
    b = build()
    print("LINT:", *(["0 defects ✓"] if not (defects := b.lint()) else ["\n  - " + "\n  - ".join(defects)]))
    print("warnings:", len(b.warnings), "| missing_art:", b.missing_art())
    out = "/tmp/zone_bug_zoo.png"
    render_builder(b, out, scale=4)
    print("render ->", out)
    if "--save" in sys.argv:
        out_dir = b.save()
        print("saved ->", out_dir)
        zdir = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "zones", "bug_zoo"))
        os.makedirs(zdir, exist_ok=True)
        render_builder(b, os.path.join(zdir, "full.png"), scale=3)
        print("preview ->", zdir)
