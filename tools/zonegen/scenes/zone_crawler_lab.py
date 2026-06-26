#!/usr/bin/env python3
"""CRAWLER LAB (96x96): two walled pens for fighting the long crawlers — centipedes on the left,
millipedes on the right — separated by a central aisle you spawn in. Stone walls block players AND
bugs so each species stays penned; a 3-cell door off the aisle lets you walk in.

Spawn config MIRRORS the working zones (bug_lab/village): `static: false` + a `min_population` floor
per species, so the ecology director keeps each pen topped up (the initial-seed path can't place bugs
because chunks aren't loaded yet at match init — the director reseeds once you're in and nearby chunks
load). No band/cull fields -> the director ONLY refills, never culls or runs weather, so it stays a
clean arena.

  python3 tools/zonegen/scenes/zone_crawler_lab.py    # build + save + lint
  python3 tools/view_world.py crawler_lab             # pixel overview
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

# Quarter the old area (~half each dimension). Outer wall rect inclusive; interior is one cell in.
PEN_A = (6, 8, 32, 64)      # centipede pen (left)   -> interior 7..31 x 9..63  (25 x 55)
PEN_B = (44, 8, 70, 64)     # millipede pen (right)
DOOR_Y = (35, 36, 37)       # 3-cell door, centered, on each pen's aisle-facing wall


def pen_walls(Z, rect, door_cells):
    x0, y0, x1, y1 = rect
    door = set(door_cells)
    for x in range(x0, x1 + 1):
        if (x, y0) not in door: Z.place_occupant("wall_stone", x, y0)
        if (x, y1) not in door: Z.place_occupant("wall_stone", x, y1)
    for y in range(y0 + 1, y1):
        if (x0, y) not in door: Z.place_occupant("wall_stone", x0, y)
        if (x1, y) not in door: Z.place_occupant("wall_stone", x1, y)


def build(zone_id="crawler_lab"):
    Z = ZoneBuilder(zone_id, W, H, base_tile="grass", name="Crawler Lab", seed=23)

    pen_walls(Z, PEN_A, [(PEN_A[2], y) for y in DOOR_Y])   # door on Pen A's RIGHT (aisle) wall
    pen_walls(Z, PEN_B, [(PEN_B[0], y) for y in DOOR_Y])   # door on Pen B's LEFT (aisle) wall

    # Director keeps each pen at its min_population floor; no cull/event fields -> refill only.
    Z.bug_spawning = {
        "static": False,
        "species_caps": {
            # swarm_size 1 -> each centipede is its OWN swarm (own center + ActionState), so they
            # windup/surge/wander INDEPENDENTLY instead of a knot of 4 lunging in unison. max is the
            # swarm COUNT cap, so it must be >= min_population now that each centipede is one swarm.
            # initial == the floor: spawn the whole arena at once at match start (now that initial spawn
            # works), and min_population lets the director top it back up after you kill some.
            "centipede_garden": {"initial": 12, "max": 40, "swarm_size": 1, "spawn_interval": 999999.0,
                                 "min_population": 12, "max_population": 40},
            "millipede":        {"initial": 16, "max": 40, "swarm_size": 1, "spawn_interval": 999999.0,
                                 "min_population": 16, "max_population": 40},
        },
        "spawn_areas": [
            {"id": "centipede_pen", "species": ["centipede_garden"], "type": "circle", "cx": 19, "cy": 36, "radius": 10},
            {"id": "millipede_pen", "species": ["millipede"],        "type": "circle", "cx": 57, "cy": 36, "radius": 10},
        ],
    }

    Z.spawn = [38, 36]   # center aisle, between the two doors
    return Z


if __name__ == "__main__":
    Z = build()
    out = Z.save()
    cfg_path = os.path.join(out, "zone.json")
    cfg = json.load(open(cfg_path)); cfg["row"], cfg["col"] = 0, 0
    cfg["ephemeral_swarms"] = True   # combat lab: never persist/restore — always fresh from this config
    json.dump(cfg, open(cfg_path, "w"), indent=2)
    print("saved 96x96 zone ->", out, "| spawn", Z.spawn, "| occupants", len(Z.occ))
    print("warnings:", Z.warnings or "none")
    print("lint:", Z.lint() or "clean")
