#!/usr/bin/env python3
"""Generate minimal test_debug zone for deterministic sync debugging.

This zone is designed to minimize noise:
- Single swarm with exactly 2 bugs
- No continuous spawning (999999s interval)
- Spawn point at center with visible dirt marker

Usage:
    cd tools && python gen_test_debug.py
"""

from generate_zone import ZoneBuilder, ZONE_SIZE

def main():
    zone = ZoneBuilder(
        "test_debug",
        row=0,
        col=0,
        name="Debug Test Zone",
        biome="debug",
        seed=1
    )

    # Simple grass terrain
    zone.fill_ground("grass")

    # Visible spawn marker (dirt circle at center)
    zone.circle_ground(256, 256, 3, "dirt")

    # Spawn point at center
    zone.set_spawn(256, 256)

    # Minimal spawning: 1 swarm of fly_common, never respawns
    zone.set_bug_spawning(
        species_caps={
            "fly_common": {
                "initial": 1,
                "max": 1,
                "spawn_interval": 999999.0
            }
        }
    )
    zone.add_spawn_area("center", ["fly_common"], "circle", cx=256, cy=256, radius=10)

    zone.export("../nakama/data/zones/test_debug")
    print("Generated test_debug zone for deterministic sync debugging")


if __name__ == "__main__":
    main()
