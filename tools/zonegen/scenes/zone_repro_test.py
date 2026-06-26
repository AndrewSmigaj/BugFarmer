#!/usr/bin/env python3
"""FLY LIFECYCLE test zone (96x96): a GATED pen (gate blocks bugs, passes the player) containing
a fast-tuned apple tree (`tree_apple_test`: grow 10s, drop 15s, rot 30s), a compost bin, and one
6-bug fly swarm. Fruit drops + rots inside the pen -> flies feed (satiation) -> reproduce
(doubling via SWARM_REPRODUCED) -> over the 20 limit -> SIZE SPLIT -> population boom until the
food is consumed. The player can walk in through the gate, pick up fruit, and deposit it in the
compost bin (right-click) to sustain the colony.

  python3 tools/zonegen/scenes/zone_repro_test.py     # build + save + lint
  python3 tools/world/view_world.py repro_test              # pixel overview
"""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
sys.path.insert(0, HERE)
from zonebuilder import ZoneBuilder                                   # noqa: E402
from features.yard import fence_rect                                  # noqa: E402

W = H = 96


def build(zone_id="repro_test"):
    Z = ZoneBuilder(zone_id, W, H, base_tile="grass", name="Repro Test", seed=42)

    # The PEN: 16x16 ring with ONE gate on the south side (gate blocks bugs, passes players).
    fence_rect(Z, 40, 40, 56, 56, gate=(48, 40))

    # Inside: the fast test tree (fruit engine) + the compost bin (player-fed station).
    Z.place_occupant("tree_apple_test", 45, 50)
    Z.place_occupant("compost_bin", 52, 46)

    # One 6-bug fly swarm spawned INSIDE the pen. Dynamic (not static) so the population pass
    # (split/merge) runs; spawn_interval huge so no continuous-spawn noise muddies the curve.
    Z.bug_spawning = {
        "species_caps": {
            "fly_common": {"initial": 1, "max": 8, "spawn_interval": 999999.0, "swarm_size": 6},
        },
        "spawn_areas": [
            {"id": "pen", "species": ["fly_common"], "type": "circle", "cx": 48, "cy": 48, "radius": 3},
        ],
    }

    Z.spawn = [48, 32]  # south of the pen, in front of the gate
    return Z


if __name__ == "__main__":
    Z = build()
    out = Z.save()
    cfg_path = os.path.join(out, "zone.json")
    cfg = json.load(open(cfg_path)); cfg["row"], cfg["col"] = 0, 0
    json.dump(cfg, open(cfg_path, "w"), indent=2)
    print("saved 96x96 zone ->", out, "| spawn", Z.spawn, "| occupants", len(Z.occ))
    print("lint:", Z.lint() or "clean")
