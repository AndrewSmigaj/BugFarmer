#!/usr/bin/env python3
# SUPERSEDED by the Bug Zoo (tools/zonegen/scenes/zone_bug_zoo.py) — its 3 empty staging pens do this
# (spawn any species with F8 in a sealed pen). Kept for now; safe to delete pending owner OK (2026-07-14).
"""COMBAT ARENA (64x64): one stone-walled pen you spawn in, for testing enemies via the F8 debug
spawner ("spawn any species at cursor"). Walls block players AND bugs, so spawned enemies stay penned
and you can test line-of-sight stings against the wall.

Unlike the lab zones this does NOT auto-spawn anything — `initial`/`min_population` are 0, so the ecology
director never fills it; you spawn what you want with the debug panel. Every species still gets a
generous `species_caps` entry so a debug spawn is never cap-blocked (debugSpawnSwarm enforces the
population + swarm-count caps). `ephemeral_swarms` -> always fresh from this config, never persisted.

  python3 tools/zonegen/scenes/zone_arena.py        # build + save + lint
  python3 tools/world/view_world.py arena                 # pixel overview
"""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
sys.path.insert(0, HERE)
from zonebuilder import ZoneBuilder                                   # noqa: E402

W = H = 64
PEN = (8, 8, 56, 56)   # outer wall rect (inclusive); interior 9..55

# All spawnable server species (species.json) — generous caps so a debug spawn is never blocked;
# initial/min_population 0 so nothing auto-spawns (you spawn via F8).
SPECIES = [
    "fly_common", "butterfly_meadow", "wasp_common", "centipede_garden", "millipede",
    "beetle_carrion", "bee_honey", "dragonfly_blue", "firefly", "ant_worker", "ant_scout",
]


def pen_walls(Z, rect):
    x0, y0, x1, y1 = rect
    for x in range(x0, x1 + 1):
        Z.place_occupant("wall_stone", x, y0)
        Z.place_occupant("wall_stone", x, y1)
    for y in range(y0 + 1, y1):
        Z.place_occupant("wall_stone", x0, y)
        Z.place_occupant("wall_stone", x1, y)


def build(zone_id="arena"):
    Z = ZoneBuilder(zone_id, W, H, base_tile="grass", name="Combat Arena", seed=7)
    pen_walls(Z, PEN)
    # No auto-spawn: director never fills (initial/min 0). Generous caps for debug spawns.
    Z.bug_spawning = {
        "static": False,
        "species_caps": {
            s: {"initial": 0, "max": 60, "swarm_size": 0, "spawn_interval": 999999.0,
                "min_population": 0, "max_population": 200}
            for s in SPECIES
        },
        "spawn_areas": [],
    }
    Z.spawn = [32, 32]   # centre of the pen
    return Z


if __name__ == "__main__":
    Z = build()
    out = Z.save()
    cfg_path = os.path.join(out, "zone.json")
    cfg = json.load(open(cfg_path)); cfg["row"], cfg["col"] = 0, 0
    cfg["ephemeral_swarms"] = True   # combat arena: never persist/restore — always fresh
    json.dump(cfg, open(cfg_path, "w"), indent=2)
    print("saved 64x64 arena ->", out, "| spawn", Z.spawn, "| occupants", len(Z.occ))
    print("warnings:", Z.warnings or "none")
    print("lint:", Z.lint() or "clean")
