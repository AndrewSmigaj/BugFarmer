#!/usr/bin/env python3
"""ANT LAB (96x96): the observation arena for the ant colony loop + THE TRAIL FEEL-BAR
(underground-arc P3: "a visible line of workers forms nest→carrion within ~2 game-days").

Geometry is the experiment: the BROOD (nest anchor) sits west with its fungus garden
(the staple — pool-flagged mushrooms), and the carrion bonanza sits FAR EAST, so a
trail must visibly CROSS the open arena to exist at all. A few dirt-block clumps stand
mid-field so we can watch routes bend (the breadcrumb-waypoint mechanic of P3.2).

No director reseeding for workers (min_population 0): the colony must sustain ITSELF
via provisioning — b_reseed staying 0 is part of the pass bar. Scouts get a tiny
director floor (they are spawned, not hatched, in v1).

  python3 tools/zonegen/scenes/zone_ant_lab.py     # build + save + lint
  python3 tools/world/view_world.py ant_lab              # pixel overview
"""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
sys.path.insert(0, HERE)
from zonebuilder import ZoneBuilder                                   # noqa: E402

W = H = 96
NEST = (24, 48)            # the brood pile (west)
CARRION = (72, 48)         # the bonanza (far east) — the trail's far terminus


def build(zone_id="ant_lab"):
    Z = ZoneBuilder(zone_id, W, H, base_tile="dirt", name="Ant Lab", seed=31)

    # THE COLONY CORNER: brood anchor + the fungus garden around it (pool-flagged
    # mushrooms = the staple larder inside home range).
    Z.place_occupant("ant_brood", *NEST)
    # THREE pools only (the first run's six fed 60 workers forever — the local larder
    # must run DRY periodically or nobody ever marches and no trail can exist).
    for mx, my, mid in [(20, 44, "mushroom_inkcap"), (27, 43, "mushroom_morel"),
                        (23, 55, "mushroom_inkcap"), (30, 50, "mushroom_morel")]:
        Z.place_occupant(mid, mx, my)

    # MID-FIELD OBSTACLES: three dirt-block clumps the trail must route around —
    # the visible test of breadcrumb routes bending with terrain.
    for cx, cy in [(46, 44), (52, 52), (48, 58)]:
        for dx in range(-2, 3):
            for dy in range(-1, 2):
                if (dx * dx + dy * dy) <= 4:
                    Z.place_occupant("dirt_block", cx + dx, cy + dy)

    # Spawn config: workers self-sustain (NO reseed floor); scouts get a tiny floor.
    Z.bug_spawning = {
        "static": False,
        "species_caps": {
            "ant_worker": {"initial": 0, "max": 20, "spawn_interval": 999999.0,
                           "min_population": 0, "max_population": 60},
            "ant_scout":  {"initial": 2, "max": 4, "swarm_size": 1, "spawn_interval": 999999.0,
                           "min_population": 2, "max_population": 6},
        },
        "spawn_areas": [
            {"id": "scout_range", "species": ["ant_scout"], "type": "circle",
             "cx": 48, "cy": 48, "radius": 34},   # covers the WHOLE arena incl. the east carrion
        ],
        "initial_carrion": [
            {"item": "dead_fly", "x": CARRION[0], "y": CARRION[1], "count": 8},
            {"item": "dead_beetle", "x": CARRION[0] + 2, "y": CARRION[1] - 2, "count": 6},
            {"item": "dead_fly", "x": CARRION[0] - 1, "y": CARRION[1] + 3, "count": 6},
        ],
    }

    Z.spawn = [48, 30]   # observer's perch, off the trail line
    return Z


if __name__ == "__main__":
    Z = build()
    out = Z.save()
    cfg_path = os.path.join(out, "zone.json")
    cfg = json.load(open(cfg_path)); cfg["row"], cfg["col"] = 0, 0
    cfg["ephemeral_swarms"] = True   # lab: never persist — always fresh from this config
    json.dump(cfg, open(cfg_path, "w"), indent=2)
    print("saved 96x96 zone ->", out, "| spawn", Z.spawn, "| occupants", len(Z.occ))
    print("warnings:", Z.warnings or "none")
    print("lint:", Z.lint() or "clean")