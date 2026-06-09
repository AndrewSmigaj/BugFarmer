#!/usr/bin/env python3
"""Phase-1 COLLISION TEST zone (96x96): a small house, a yard with a TREE (blocks) and CORN on a garden
bed (passable), a fully-CLOSED fly pen plus a GATED pen, and two fly_common swarms (one inside the closed
pen, one outside). Built to verify player + bug collision headlessly via the sync-harness.

  python3 tools/zonegen/scenes/zone_collision_test.py     # build + save + lint
  python3 tools/view_world.py collision_test              # whole-zone pixel overview
"""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
sys.path.insert(0, HERE)
from zonebuilder import ZoneBuilder                                   # noqa: E402
from features.room import place_room                                  # noqa: E402
from features.yard import fence_rect                                  # noqa: E402
from features.garden import crop_bed                                  # noqa: E402

W = H = 96


def build(zone_id="collision_test"):
    Z = ZoneBuilder(zone_id, W, H, base_tile="grass", name="Collision Test", seed=42)  # fixed seed -> reproducible spawns

    # 1) A small HOUSE (NW) — a one-room shell with a south door (tests wall collision if walked into).
    place_room(Z, 8, 40, 24, 56, door_side="bottom")

    # 2) The player's NORTHWARD path from spawn (48,8) crosses, in order:
    #    - CORN on a garden bed — plant_corn is PASSABLE, so the player walks THROUGH it,
    crop_bed(Z, 44, 18, 52, 24, ["plant_corn"])
    #    - a TREE — blocks_players/bugs=true, so the player is STOPPED one cell short of it.
    Z.place_occupant("tree_oak", 48, 30)

    # 3) CLOSED fly pen (SE) — a gap-free fence_wood ring (NO gate). The inside swarm must never leave;
    #    its center is raycast-clamped inside and per-bug collision keeps the bugs in.
    fence_rect(Z, 60, 20, 74, 34)

    # 4) GATED pen (E) — a fence ring with ONE passable gate_wood; reserved for the Phase-2 split test.
    fence_rect(Z, 60, 50, 74, 64, gate=(60, 57))

    # 5) BUG SPAWNING — fly_common only (the species.json-defined species). STATIC: spawn once, no
    #    continuous spawn / merge / split, so the collision test is deterministic. One spawn circle inside
    #    the closed pen, one out in the open NW.
    Z.bug_spawning = {
        "static": True,
        "species_caps": {
            "fly_common": {"initial": 3, "max": 3, "spawn_interval": 999999.0, "swarm_size": 8},
        },
        "spawn_areas": [
            {"id": "in_closed_pen", "species": ["fly_common"], "type": "circle", "cx": 67, "cy": 27, "radius": 3},
            {"id": "outside", "species": ["fly_common"], "type": "circle", "cx": 24, "cy": 74, "radius": 4},
        ],
    }

    Z.spawn = [48, 8]                                                 # south-centre, due south of corn + tree
    return Z


if __name__ == "__main__":
    Z = build()
    out = Z.save()
    cfg_path = os.path.join(out, "zone.json")                        # save() writes row/col 0,0 — fine for a test zone
    cfg = json.load(open(cfg_path)); cfg["row"], cfg["col"] = 0, 0
    json.dump(cfg, open(cfg_path, "w"), indent=2)
    print("saved 96x96 zone ->", out, "| spawn", Z.spawn, "| occupants", len(Z.occ))
    defects = Z.lint()
    print("lint:", defects or "clean")
    print("warnings:", len(Z.warnings))
