#!/usr/bin/env python3
"""Generate the Starting Village zone (village_21).

Design philosophy:
- COMPACT village core (~60x60 cells in the center)
- Rich natural surroundings (meadows, groves, ponds)
- Roads connecting to adjacent zones
- Following ZONE_GENERATION_GUIDE.md specifications
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generate_zone import ZoneBuilder

# Small cottage template (6x5)
SMALL_COTTAGE = {
    "width": 6,
    "height": 5,
    "floor": "wood_floor",
    "occupants": [
        {"id": "door_wood", "x": 2, "y": 0, "dir": 0},
        {"id": "bed_basic", "x": 0, "y": 1, "dir": 0},
        {"id": "chest_wood", "x": 4, "y": 3, "dir": 0},
    ]
}

# Tiny shack template (4x4)
TINY_SHACK = {
    "width": 4,
    "height": 4,
    "floor": "wood_floor",
    "occupants": [
        {"id": "door_wood", "x": 1, "y": 0, "dir": 0},
        {"id": "crate", "x": 2, "y": 2, "dir": 0},
    ]
}

# Shop template (7x6)
VILLAGE_SHOP = {
    "width": 7,
    "height": 6,
    "floor": "wood_floor",
    "occupants": [
        {"id": "door_wood", "x": 3, "y": 0, "dir": 0},
        {"id": "chest_wood", "x": 0, "y": 4, "dir": 0},
        {"id": "chest_wood", "x": 5, "y": 4, "dir": 0},
        {"id": "shelf", "x": 2, "y": 4, "dir": 0},
        {"id": "barrel", "x": 0, "y": 1, "dir": 0},
        {"id": "barrel", "x": 6, "y": 1, "dir": 0},
    ]
}

# Barn/storage building (8x6)
VILLAGE_BARN = {
    "width": 8,
    "height": 6,
    "floor": "wood_floor",
    "occupants": [
        {"id": "door_wood", "x": 3, "y": 0, "dir": 0},
        {"id": "crate", "x": 0, "y": 1, "dir": 0},
        {"id": "crate", "x": 1, "y": 1, "dir": 0},
        {"id": "crate", "x": 0, "y": 2, "dir": 0},
        {"id": "barrel", "x": 6, "y": 1, "dir": 0},
        {"id": "barrel", "x": 7, "y": 1, "dir": 0},
        {"id": "barrel", "x": 6, "y": 2, "dir": 0},
        {"id": "chest_large", "x": 3, "y": 4, "dir": 0},
    ]
}


def main():
    builder = ZoneBuilder(
        zone_id="village_21",
        row=2,
        col=1,
        name="Starting Village",
        biome="village",
        seed=42
    )

    # Spawn at village center
    builder.set_spawn(256, 256)

    # =========================================================================
    # BASE TERRAIN - All grass (no random dirt noise!)
    # =========================================================================
    builder.fill_ground("grass")

    # =========================================================================
    # MAIN ROADS (Connect to zone edges for adjacent zones)
    # =========================================================================
    # North-South road (connects to Butterfly Fields at row 1)
    builder.path_ground([(256, 0), (256, 511)], "stone_path", width=3)

    # East-West road (connects to Bee Meadow west, Wasp Thicket east)
    builder.path_ground([(0, 256), (511, 256)], "stone_path", width=3)

    # =========================================================================
    # COMPACT VILLAGE CORE (centered at 256, 256, ~60x60 area)
    # Village spans roughly 226-286 x 226-286
    # =========================================================================

    # Central square - small paved area 20x20
    builder.rect_ground(246, 246, 20, 20, "stone_path")

    # Well at center (2x2)
    builder.place_occupant(255, 255, "well")

    # Signpost (fast travel)
    builder.place_occupant(250, 250, "signpost")

    # Workbench for new players
    builder.place_occupant(261, 250, "workbench")

    # Anvil nearby
    builder.place_occupant(261, 253, "anvil")

    # -------------------------------------------------------------------------
    # Player's cottage (northeast of center)
    # -------------------------------------------------------------------------
    builder.place_building(272, 235, SMALL_COTTAGE)
    # Dirt path from cottage to road
    builder.path_ground([(274, 240), (274, 256)], "dirt", width=2)
    # Small garden next to cottage
    builder.rect_ground(278, 237, 4, 3, "garden_plot")
    # Fence around garden
    builder.place_line(277, 236, 282, 236, "fence_wood")  # Bottom
    builder.place_line(277, 240, 282, 240, "fence_wood")  # Top
    builder.place_line(277, 237, 277, 239, "fence_wood")  # Left
    builder.place_line(283, 237, 283, 239, "fence_wood")  # Right

    # -------------------------------------------------------------------------
    # Beekeeper's cottage (northwest of center)
    # -------------------------------------------------------------------------
    builder.place_building(228, 235, SMALL_COTTAGE)
    builder.path_ground([(232, 240), (232, 256)], "dirt", width=2)
    # Beehives near cottage
    builder.place_occupant(220, 238, "beehive_basic")
    builder.place_occupant(222, 235, "beehive_medium")
    builder.place_occupant(218, 241, "beehive_basic")

    # -------------------------------------------------------------------------
    # Fisherman's shack (south of center, near future pond)
    # -------------------------------------------------------------------------
    builder.place_building(250, 275, TINY_SHACK)
    builder.path_ground([(252, 275), (252, 266)], "dirt", width=2)
    # Barrel and crate outside
    builder.place_occupant(255, 277, "barrel")
    builder.place_occupant(248, 276, "crate")

    # -------------------------------------------------------------------------
    # Village shop (southwest of center)
    # -------------------------------------------------------------------------
    builder.place_building(225, 268, VILLAGE_SHOP)
    builder.path_ground([(228, 268), (228, 256)], "dirt", width=2)
    # Decorations outside
    builder.place_occupant(233, 270, "potted_plant")
    builder.place_occupant(224, 270, "barrel")

    # -------------------------------------------------------------------------
    # Village barn (east of center)
    # -------------------------------------------------------------------------
    builder.place_building(285, 250, VILLAGE_BARN)
    builder.path_ground([(288, 250), (288, 256)], "dirt", width=2)
    # Hay bales / crates outside
    builder.place_occupant(294, 252, "crate")
    builder.place_occupant(294, 254, "crate")

    # =========================================================================
    # NATURAL FEATURES - Rich meadow surroundings
    # =========================================================================

    # -------------------------------------------------------------------------
    # 8 DENSE TREE GROVES (around the zone)
    # -------------------------------------------------------------------------

    # Grove 1: Northwest corner - DENSE mixed oak and pine
    builder.scatter_grove(
        cx=70, cy=70, radius=45,
        tree_types=[("tree_oak", 3), ("tree_pine", 2), ("tree_dead", 1)],
        tree_count=55,
        understory=[("bush", 3), ("tall_grass", 2), ("mushroom_red", 1)],
        understory_count=80
    )

    # Grove 2: Northeast corner - oak dominant
    builder.scatter_grove(
        cx=440, cy=60, radius=40,
        tree_types=[("tree_oak", 4), ("tree_fruit", 2)],
        tree_count=45,
        understory=[("bush", 2), ("flower_wild", 2), ("tall_grass", 2)],
        understory_count=70
    )

    # Grove 3: Southwest corner - pine grove
    builder.scatter_grove(
        cx=60, cy=440, radius=45,
        tree_types=[("tree_pine", 4), ("tree_oak", 1)],
        tree_count=50,
        understory=[("bush", 2), ("tall_grass", 3), ("mushroom_glow", 1)],
        understory_count=75
    )

    # Grove 4: Southeast corner - fruit orchard
    builder.scatter_grove(
        cx=450, cy=450, radius=40,
        tree_types=[("tree_fruit", 3), ("tree_oak", 2)],
        tree_count=40,
        understory=[("bush", 2), ("flower_yellow", 2), ("tall_grass", 1)],
        understory_count=60
    )

    # Grove 5: North center-west - along road
    builder.scatter_grove(
        cx=150, cy=80, radius=30,
        tree_types=[("tree_oak", 3), ("tree_pine", 1)],
        tree_count=30,
        understory=[("bush", 3), ("tall_grass", 2)],
        understory_count=45
    )

    # Grove 6: North center-east
    builder.scatter_grove(
        cx=350, cy=90, radius=30,
        tree_types=[("tree_oak", 2), ("tree_pine", 2)],
        tree_count=28,
        understory=[("bush", 2), ("tall_grass", 3)],
        understory_count=40
    )

    # Grove 7: South center-west
    builder.scatter_grove(
        cx=140, cy=430, radius=30,
        tree_types=[("tree_pine", 3), ("tree_dead", 1)],
        tree_count=25,
        understory=[("bush", 3), ("mushroom_red", 1), ("tall_grass", 2)],
        understory_count=40
    )

    # Grove 8: South center-east
    builder.scatter_grove(
        cx=360, cy=440, radius=30,
        tree_types=[("tree_oak", 3), ("tree_fruit", 1)],
        tree_count=25,
        understory=[("bush", 2), ("flower_wild", 2)],
        understory_count=35
    )

    # -------------------------------------------------------------------------
    # 6 DENSE FLOWER MEADOWS
    # -------------------------------------------------------------------------

    # Meadow 1: West of village - large wildflower field
    builder.scatter_meadow(
        cx=120, cy=280, radius=35,
        flower_types=[("flower_wild", 3), ("flower_yellow", 2), ("flower_blue", 1)],
        density=0.35
    )

    # Meadow 2: East of village - sunflower field
    builder.scatter_meadow(
        cx=380, cy=260, radius=30,
        flower_types=[("sunflower", 3), ("flower_yellow", 2)],
        density=0.30
    )

    # Meadow 3: North meadow - colorful mix
    builder.scatter_meadow(
        cx=340, cy=140, radius=28,
        flower_types=[("flower_red", 2), ("flower_blue", 2), ("flower_wild", 1)],
        density=0.30
    )

    # Meadow 4: South meadow near fisherman
    builder.scatter_meadow(
        cx=320, cy=380, radius=25,
        flower_types=[("flower_wild", 2), ("flower_yellow", 2)],
        density=0.28
    )

    # Meadow 5: Northwest meadow
    builder.scatter_meadow(
        cx=180, cy=180, radius=22,
        flower_types=[("flower_blue", 3), ("flower_wild", 2)],
        density=0.25
    )

    # Meadow 6: Southeast meadow
    builder.scatter_meadow(
        cx=380, cy=380, radius=22,
        flower_types=[("flower_red", 3), ("sunflower", 1)],
        density=0.25
    )

    # -------------------------------------------------------------------------
    # 2 PONDS
    # -------------------------------------------------------------------------

    # Pond 1: Southwest - fisherman's pond (larger)
    builder.create_pond(cx=130, cy=360, radius=12, reed_count=18)

    # Pond 2: East side - small natural pond
    builder.create_pond(cx=420, cy=320, radius=8, reed_count=10)

    # -------------------------------------------------------------------------
    # 3 ROCK/ORE PATCHES
    # -------------------------------------------------------------------------

    # Rock patch 1: Northwest
    builder.scatter_rock_patch(cx=150, cy=150, radius=15, total_count=12)

    # Rock patch 2: Southeast
    builder.scatter_rock_patch(cx=400, cy=380, radius=12, total_count=10)

    # Rock patch 3: Near center-east (starter mining)
    builder.scatter_rock_patch(
        cx=350, cy=200, radius=10, total_count=8,
        rock_types=[("rock_small", 3), ("stone_block", 2), ("ore_coal_block", 1)]
    )

    # -------------------------------------------------------------------------
    # SCATTERED VEGETATION (fill ALL open areas densely)
    # -------------------------------------------------------------------------

    # Individual trees spread across the zone
    builder.scatter("tree_oak", count=60, min_spacing=15)
    builder.scatter("tree_pine", count=40, min_spacing=18)
    builder.scatter("tree_dead", count=15, min_spacing=25)
    builder.scatter("tree_fruit", count=20, min_spacing=20)

    # Bushes EVERYWHERE - key to making it look full
    builder.scatter("bush", count=250, min_spacing=5)

    # Tall grass in open areas - LOTS of it
    builder.scatter("tall_grass", count=400, min_spacing=3)

    # Small rocks scattered
    builder.scatter("rock_small", count=80, min_spacing=10)

    # Additional flowers (sparse, outside meadows)
    builder.scatter("flower_wild", count=150, min_spacing=6)
    builder.scatter("flower_yellow", count=100, min_spacing=7)
    builder.scatter("flower_blue", count=80, min_spacing=8)
    builder.scatter("flower_red", count=60, min_spacing=8)

    # =========================================================================
    # DECORATIVE TOUCHES
    # =========================================================================

    # Potted plants near village center
    builder.place_occupant(247, 260, "potted_plant")
    builder.place_occupant(265, 260, "potted_plant")

    # Lamp posts along main road in village
    builder.place_occupant(250, 240, "lamp_floor")
    builder.place_occupant(262, 240, "lamp_floor")
    builder.place_occupant(250, 270, "lamp_floor")
    builder.place_occupant(262, 270, "lamp_floor")

    # =========================================================================
    # VALIDATION AND EXPORT
    # =========================================================================

    # Print stats
    stats = builder.stats()
    print(f"\nVillage Zone Stats:")
    print(f"  Seed: {stats['seed']}")
    print(f"  Total occupants: {stats['total_occupants']}")
    print(f"  Blocked cells: {stats['blocked_cells']}")

    print(f"\n  Ground tiles:")
    for tile, count in sorted(stats['tile_counts'].items()):
        pct = 100 * count / stats['total_cells']
        print(f"    {tile}: {count:,} ({pct:.1f}%)")

    print(f"\n  Top occupants:")
    sorted_occs = sorted(stats['occupant_counts'].items(), key=lambda x: -x[1])[:15]
    for occ, count in sorted_occs:
        print(f"    {occ}: {count}")

    # Validate
    issues = builder.validate()
    if issues:
        print("\nValidation issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\nValidation passed!")

    # Export
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "nakama", "data", "zones", "village_21"
    )
    builder.export(output_dir)


if __name__ == "__main__":
    main()
