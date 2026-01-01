#!/usr/bin/env python3
"""Generate the Starting Village zone (2,1)."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generate_zone import ZoneBuilder, ZONE_SIZE

def main():
    zone = ZoneBuilder(
        zone_id="village_21",
        row=2,
        col=1,
        name="Starting Village",
        biome="village",
        seed=2100
    )

    center = ZONE_SIZE // 2  # 256

    # =========================================================================
    # BASE TERRAIN
    # =========================================================================
    zone.fill_ground("grass")

    # =========================================================================
    # ROADS - cross pattern, 3 cells wide
    # =========================================================================
    zone.path_ground([(center, 0), (center, ZONE_SIZE - 1)], "stone_path", width=3)
    zone.path_ground([(0, center), (ZONE_SIZE - 1, center)], "stone_path", width=3)

    # Widen center into a village square (20x20)
    zone.rect_ground(center - 10, center - 10, 20, 20, "stone_path")

    # =========================================================================
    # VILLAGE SQUARE FEATURES (on the stone path intersection)
    # =========================================================================
    zone.place_occupant(center - 1, center - 1, "well")  # Well near center (2x2)
    zone.place_occupant(center - 6, center - 6, "signpost")
    zone.place_occupant(center + 5, center - 5, "workbench")  # Public workbench

    # Lamps at corners of square
    zone.place_occupant(center - 9, center - 9, "lamp_floor")
    zone.place_occupant(center + 8, center - 9, "lamp_floor")
    zone.place_occupant(center - 9, center + 8, "lamp_floor")
    zone.place_occupant(center + 8, center + 8, "lamp_floor")

    # =========================================================================
    # CITY HALL - NE quadrant (larger building, stone walls)
    # =========================================================================
    ch_x, ch_y = center + 20, center - 50

    # Clear and floor
    zone.rect_ground(ch_x, ch_y, 14, 12, "wood_floor")

    # Stone walls around perimeter
    zone.place_rect_border(ch_x, ch_y, 14, 12, "wall_stone")

    # Door (south side, facing square)
    zone.remove_occupant(ch_x + 6, ch_y)
    zone.remove_occupant(ch_x + 7, ch_y)
    zone.place_occupant(ch_x + 6, ch_y, "door_wood")

    # Interior
    zone.place_occupant(ch_x + 5, ch_y + 7, "table_wood")  # Big desk
    zone.place_occupant(ch_x + 5, ch_y + 5, "chair_wood")  # Behind desk
    zone.place_occupant(ch_x + 5, ch_y + 3, "chair_wood")  # Visitor chair
    zone.place_occupant(ch_x + 7, ch_y + 3, "chair_wood")  # Visitor chair
    zone.place_occupant(ch_x + 11, ch_y + 3, "bookshelf")
    zone.place_occupant(ch_x + 2, ch_y + 8, "chest_wood")

    # =========================================================================
    # MERCHANT SHOP - SE quadrant
    # =========================================================================
    shop_x, shop_y = center + 25, center + 25

    zone.rect_ground(shop_x, shop_y, 10, 8, "wood_floor")
    zone.place_rect_border(shop_x, shop_y, 10, 8, "wall_wood")

    # Door facing west (toward square)
    zone.remove_occupant(shop_x, shop_y + 3)
    zone.remove_occupant(shop_x, shop_y + 4)
    zone.place_occupant(shop_x, shop_y + 3, "door_wood")

    # Interior - shop counter and goods
    zone.place_occupant(shop_x + 3, shop_y + 4, "table_wood")  # Counter
    zone.place_occupant(shop_x + 6, shop_y + 2, "chest_wood")
    zone.place_occupant(shop_x + 6, shop_y + 5, "barrel")
    zone.place_occupant(shop_x + 7, shop_y + 5, "barrel")
    zone.place_occupant(shop_x + 2, shop_y + 2, "crate")

    # =========================================================================
    # NPC COTTAGES - SW and NW quadrants
    # =========================================================================

    # Cottage 1 - SW quadrant
    c1_x, c1_y = center - 45, center + 25
    zone.rect_ground(c1_x, c1_y, 8, 7, "wood_floor")
    zone.place_rect_border(c1_x, c1_y, 8, 7, "wall_wood")
    zone.remove_occupant(c1_x + 3, c1_y)
    zone.remove_occupant(c1_x + 4, c1_y)
    zone.place_occupant(c1_x + 3, c1_y, "door_wood")
    zone.place_occupant(c1_x + 2, c1_y + 3, "bed_basic")
    zone.place_occupant(c1_x + 5, c1_y + 3, "table_wood")

    # Cottage 2 - NW quadrant
    c2_x, c2_y = center - 50, center - 45
    zone.rect_ground(c2_x, c2_y, 8, 7, "wood_floor")
    zone.place_rect_border(c2_x, c2_y, 8, 7, "wall_wood")
    zone.remove_occupant(c2_x + 3, c2_y)
    zone.remove_occupant(c2_x + 4, c2_y)
    zone.place_occupant(c2_x + 3, c2_y, "door_wood")
    zone.place_occupant(c2_x + 2, c2_y + 3, "bed_basic")
    zone.place_occupant(c2_x + 5, c2_y + 4, "chest_wood")

    # =========================================================================
    # FLY FARM - further SE, past the shop
    # =========================================================================
    farm_x, farm_y = center + 60, center + 60
    farm_w, farm_h = 20, 16

    # Fence border
    zone.place_rect_border(farm_x, farm_y, farm_w, farm_h, "fence_wood")

    # Gate at north side
    zone.remove_occupant(farm_x + farm_w // 2, farm_y)
    zone.place_occupant(farm_x + farm_w // 2, farm_y, "gate_wood")

    # Garden plots inside
    zone.rect_ground(farm_x + 2, farm_y + 2, farm_w - 4, farm_h - 4, "garden_plot")

    # Plants in rows
    for row in range(3):
        for col in range(4):
            px = farm_x + 4 + col * 4
            py = farm_y + 4 + row * 4
            zone.place_occupant(px, py, "flower_wild")

    # =========================================================================
    # WOODCUTTER'S CABIN - north, along the north road
    # =========================================================================
    wood_x, wood_y = center - 25, 60  # Far north, west of road

    # Small cabin
    zone.rect_ground(wood_x, wood_y, 7, 6, "wood_floor")
    zone.place_rect_border(wood_x, wood_y, 7, 6, "wall_wood")
    zone.remove_occupant(wood_x + 3, wood_y)
    zone.place_occupant(wood_x + 3, wood_y, "door_wood")
    zone.place_occupant(wood_x + 2, wood_y + 3, "bed_basic")
    zone.place_occupant(wood_x + 5, wood_y + 2, "chest_wood")

    # Tree cluster around cabin
    zone.place_occupant(wood_x - 12, wood_y - 5, "tree_oak")
    zone.place_occupant(wood_x - 8, wood_y + 10, "tree_oak")
    zone.place_occupant(wood_x + 12, wood_y - 3, "tree_pine")
    zone.place_occupant(wood_x + 15, wood_y + 8, "tree_oak")
    zone.place_occupant(wood_x - 5, wood_y + 15, "tree_pine")
    zone.place_occupant(wood_x + 10, wood_y + 12, "tree_oak")

    # =========================================================================
    # SECRET MERCHANT - far SW corner, hidden in trees
    # =========================================================================
    secret_x, secret_y = 60, 420

    # Small mysterious cottage
    zone.rect_ground(secret_x, secret_y, 6, 5, "wood_floor")
    zone.place_rect_border(secret_x, secret_y, 6, 5, "wall_wood")
    zone.remove_occupant(secret_x + 2, secret_y)
    zone.place_occupant(secret_x + 2, secret_y, "door_wood")
    zone.place_occupant(secret_x + 3, secret_y + 3, "chest_wood")

    # Hidden in trees - no obvious path
    zone.place_occupant(secret_x - 10, secret_y - 8, "tree_oak")
    zone.place_occupant(secret_x + 10, secret_y - 5, "tree_oak")
    zone.place_occupant(secret_x - 8, secret_y + 10, "tree_pine")
    zone.place_occupant(secret_x + 12, secret_y + 8, "tree_oak")
    zone.place_occupant(secret_x - 5, secret_y + 18, "tree_pine")
    zone.place_occupant(secret_x + 8, secret_y + 15, "tree_oak")
    zone.place_occupant(secret_x - 15, secret_y + 3, "tree_pine")

    # =========================================================================
    # MEADOW TREE CLUSTERS - scattered around zone
    # =========================================================================
    tree_clusters = [
        (80, 120), (420, 80), (450, 200), (80, 280),
        (400, 320), (180, 430), (350, 440), (120, 180),
        (380, 140), (60, 350), (450, 380), (300, 80),
    ]

    for cx, cy in tree_clusters:
        # Skip if too close to village center or existing features
        if abs(cx - center) < 70 and abs(cy - center) < 70:
            continue
        if abs(cx - secret_x) < 30 and abs(cy - secret_y) < 30:
            continue
        if abs(cx - wood_x) < 25 and abs(cy - wood_y) < 25:
            continue

        zone.place_occupant(cx, cy, "tree_oak")
        zone.place_occupant(cx + 5, cy + 4, "tree_oak")
        zone.place_occupant(cx - 3, cy + 6, "tree_pine")

    # =========================================================================
    # MEADOW SCATTER - flowers, grass, bushes
    # =========================================================================
    avoid = {"stone_path", "wood_floor", "garden_plot"}

    zone.scatter("flower_wild", count=200, min_spacing=3, avoid_tiles=avoid)
    zone.scatter("flower_red", count=50, min_spacing=4, avoid_tiles=avoid)
    zone.scatter("flower_yellow", count=50, min_spacing=4, avoid_tiles=avoid)
    zone.scatter("flower_blue", count=40, min_spacing=4, avoid_tiles=avoid)
    zone.scatter("tall_grass", count=120, min_spacing=2, avoid_tiles=avoid)
    zone.scatter("bush", count=80, min_spacing=5, avoid_tiles=avoid)
    zone.scatter("rock_small", count=30, min_spacing=10, avoid_tiles=avoid)

    # =========================================================================
    # SPAWN POINT - on road just north of village square
    # =========================================================================
    zone.set_spawn(center, center - 15)

    # =========================================================================
    # EXPORT
    # =========================================================================
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "nakama", "data", "zones", "village_21"
    )
    zone.export(output_dir)

    stats = zone.stats()
    print(f"\nOccupant counts:")
    for occ_id, count in sorted(stats["occupant_counts"].items()):
        print(f"  {occ_id}: {count}")


if __name__ == "__main__":
    main()
