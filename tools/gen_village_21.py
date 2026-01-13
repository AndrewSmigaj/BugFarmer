#!/usr/bin/env python3
"""Generate the Starting Village zone (2,1).

The village is SMALL compared to the 512x512 zone size.
Most of the zone is meadow with the village occupying ~100 cell radius from center.

Key areas:
- Village Core: Civic square with well, benches, notice board
- City Hall: NE of center, stone walls
- Country Store: SE of center, open front
- Ecologist's House: W of center, surrounded by flowers
- Woodcutter Cabin: NW, work cabin with stumps/logs (no bed)
- Cottages: SW, 2-3 small homes
- Orchard: Far NE, structured grid of fruit trees
- Fly Farm: Far S, open landscape (NO FENCE)
"""

import sys
import os
import random
import math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generate_zone import ZoneBuilder, ZONE_SIZE


def build_roads(zone, center):
    """Build road network with degradation from center outward.

    Stone path in core, dirt extending to zone borders.
    """
    # Village square (smaller - 12x12)
    zone.rect_ground(center - 6, center - 6, 12, 12, "stone_path")
    # Slight imperfection at corners
    zone.rect_ground(center - 7, center - 7, 2, 2, "dirt")
    zone.rect_ground(center + 5, center + 5, 2, 2, "dirt")

    # Main N-S road - stone near center, dirt extending to borders
    zone.path_ground([(center, center - 30), (center, center + 30)], "stone_path", width=3)
    # North road to border
    zone.path_ground([(center, center - 30), (center, 20)], "dirt", width=3)
    # South road to border
    zone.path_ground([(center, center + 30), (center, 492)], "dirt", width=3)

    # Main E-W road - stone near center, dirt extending to borders
    zone.path_ground([(center - 30, center), (center + 30, center)], "stone_path", width=3)
    # West road to border
    zone.path_ground([(center - 30, center), (20, center)], "dirt", width=3)
    # East road to border
    zone.path_ground([(center + 30, center), (492, center)], "dirt", width=3)

    # Spur to orchard (NE) - shorter path since orchard is closer
    zone.path_ground([
        (center + 25, center - 15),
        (center + 40, center - 35),
        (center + 55, center - 50)
    ], "dirt", width=2)

    # Spur to fly farm (SE) - shorter path since farm is closer
    zone.path_ground([
        (center + 15, center + 25),
        (center + 30, center + 45),
        (center + 45, center + 55)
    ], "dirt", width=2)

    # Spur to woodcutter (NW) - shorter path
    zone.path_ground([
        (center - 15, center - 12),
        (center - 25, center - 20)
    ], "dirt", width=2)


def build_village_square(zone, center):
    """Build the civic square with well, benches, notice board.

    Smaller square (12x12) with intentional decoration placement.
    """
    # Well (center of square)
    zone.place_occupant(center - 1, center - 1, "well")

    # Notice board at north entrance (intentional - players see it when entering)
    zone.place_occupant(center + 2, center - 5, "notice_board")

    # Benches around the square edges (intentional positions)
    zone.place_occupant(center - 4, center - 3, "bench")  # West side
    zone.place_occupant(center + 3, center + 2, "bench")  # East side

    # Planter boxes near square corners (on grass, not stone)
    zone.place_occupant(center - 8, center - 8, "planter_box")  # NW corner
    zone.place_occupant(center + 7, center + 7, "planter_box")  # SE corner

    # Signposts at road entrances - pointing to landmarks
    zone.place_occupant(center - 8, center, "signpost")   # West entrance
    zone.place_occupant(center, center - 8, "signpost")   # North entrance

    # Lamps at square corners (intentional - provides light coverage)
    zone.place_occupant(center - 5, center - 5, "lamp_floor")
    zone.place_occupant(center + 4, center - 5, "lamp_floor")
    zone.place_occupant(center - 5, center + 4, "lamp_floor")
    zone.place_occupant(center + 4, center + 4, "lamp_floor")


def build_city_hall(zone, center):
    """City Hall - NE of center, stone walls, administrative feel."""
    ch_x, ch_y = center + 15, center - 20

    # Floor
    zone.rect_ground(ch_x, ch_y, 14, 12, "wood_floor")

    # Stone walls
    zone.place_rect_border(ch_x, ch_y, 14, 12, "wall_stone")

    # Door (south side, off-center)
    zone.remove_occupant(ch_x + 5, ch_y)
    zone.remove_occupant(ch_x + 6, ch_y)
    zone.place_occupant(ch_x + 5, ch_y, "door_wood")

    # Side door (east)
    zone.remove_occupant(ch_x + 13, ch_y + 5)
    zone.place_occupant(ch_x + 13, ch_y + 5, "door_wood")

    # Interior - big desk, chairs, bookshelf, papers (crates)
    zone.place_occupant(ch_x + 5, ch_y + 8, "table_wood")  # Main desk
    zone.place_occupant(ch_x + 6, ch_y + 6, "chair_wood")   # Behind desk
    zone.place_occupant(ch_x + 4, ch_y + 4, "chair_wood")   # Visitor
    zone.place_occupant(ch_x + 7, ch_y + 4, "chair_wood")   # Visitor
    zone.place_occupant(ch_x + 11, ch_y + 3, "bookshelf")
    zone.place_occupant(ch_x + 11, ch_y + 7, "bookshelf")
    zone.place_occupant(ch_x + 2, ch_y + 9, "chest_wood")
    zone.place_occupant(ch_x + 2, ch_y + 3, "crate")  # Document pile
    zone.place_occupant(ch_x + 3, ch_y + 3, "crate")

    # Exterior - signpost, lamp at door, crates
    zone.place_occupant(ch_x + 3, ch_y - 2, "signpost")
    zone.place_occupant(ch_x + 8, ch_y - 1, "lamp_floor")
    zone.place_occupant(ch_x + 10, ch_y - 2, "crate")
    zone.place_occupant(ch_x + 11, ch_y - 2, "barrel")


def build_country_store(zone, center):
    """Country Store - SE of center, open front (no south wall)."""
    shop_x, shop_y = center + 18, center + 12

    # Floor
    zone.rect_ground(shop_x, shop_y, 12, 10, "wood_floor")

    # Wood walls on 3 sides only (open front = south)
    # North wall
    for x in range(shop_x, shop_x + 12):
        zone.place_occupant(x, shop_y + 9, "wall_wood")
    # East wall
    for y in range(shop_y, shop_y + 10):
        zone.place_occupant(shop_x + 11, y, "wall_wood")
    # West wall
    for y in range(shop_y, shop_y + 10):
        zone.place_occupant(shop_x, y, "wall_wood")

    # Interior - counter, shelves, goods
    zone.place_occupant(shop_x + 4, shop_y + 6, "table_wood")  # Counter
    zone.place_occupant(shop_x + 2, shop_y + 7, "bookshelf")   # Shelves
    zone.place_occupant(shop_x + 8, shop_y + 7, "bookshelf")
    zone.place_occupant(shop_x + 8, shop_y + 4, "chest_wood")
    zone.place_occupant(shop_x + 2, shop_y + 4, "barrel")
    zone.place_occupant(shop_x + 3, shop_y + 4, "barrel")

    # Exterior - signpost, delivery clutter
    zone.place_occupant(shop_x + 6, shop_y - 2, "signpost")
    zone.place_occupant(shop_x + 8, shop_y - 2, "crate")
    zone.place_occupant(shop_x + 9, shop_y - 2, "barrel")
    zone.place_occupant(shop_x + 2, shop_y - 1, "barrel")


def build_ecologist_house(zone, center):
    """Ecologist's House - W of center, surrounded by flowers."""
    eco_x, eco_y = center - 25, center - 8

    # Floor
    zone.rect_ground(eco_x, eco_y, 8, 7, "wood_floor")

    # Wood walls
    zone.place_rect_border(eco_x, eco_y, 8, 7, "wall_wood")

    # Door (east side, facing village)
    zone.remove_occupant(eco_x + 7, eco_y + 3)
    zone.place_occupant(eco_x + 7, eco_y + 3, "door_wood")

    # Interior - research feel
    zone.place_occupant(eco_x + 2, eco_y + 4, "table_wood")
    zone.place_occupant(eco_x + 2, eco_y + 2, "bookshelf")
    zone.place_occupant(eco_x + 5, eco_y + 4, "chest_wood")
    zone.place_occupant(eco_x + 5, eco_y + 2, "potted_plant")

    # Exterior - test plots (planter boxes), flower scatter
    zone.place_occupant(eco_x + 9, eco_y + 2, "planter_box")
    zone.place_occupant(eco_x + 9, eco_y + 4, "planter_box")
    zone.place_occupant(eco_x - 3, eco_y + 3, "planter_box")

    # Dense flower scatter around the house
    for _ in range(25):
        fx = eco_x + random.randint(-8, 12)
        fy = eco_y + random.randint(-6, 12)
        if zone.get_ground(fx, fy) == "grass" and not zone.is_blocked(fx, fy):
            zone.place_occupant(fx, fy, random.choice([
                "flower_wild", "flower_red", "flower_blue", "flower_yellow", "sunflower"
            ]))


def build_woodcutter_cabin(zone, center):
    """Woodcutter Cabin - NW, work cabin (NO BED), stumps and logs around."""
    wood_x, wood_y = center - 30, center - 25

    # Floor
    zone.rect_ground(wood_x, wood_y, 7, 6, "wood_floor")

    # Wood walls
    zone.place_rect_border(wood_x, wood_y, 7, 6, "wall_wood")

    # Door (south, facing village)
    zone.remove_occupant(wood_x + 3, wood_y)
    zone.place_occupant(wood_x + 3, wood_y, "door_wood")

    # Interior - work cabin, NOT residential (no bed!)
    zone.place_occupant(wood_x + 2, wood_y + 3, "workbench")
    zone.place_occupant(wood_x + 5, wood_y + 3, "chest_wood")
    zone.place_occupant(wood_x + 5, wood_y + 1, "crate")

    # CRITICAL EXTERIOR - signs of active wood harvesting
    # Log piles (scattered, not aligned)
    zone.place_occupant(wood_x - 6, wood_y + 2, "log_pile")
    zone.place_occupant(wood_x + 9, wood_y + 1, "log_pile")
    zone.place_occupant(wood_x - 4, wood_y - 4, "log_pile")
    zone.place_occupant(wood_x + 8, wood_y + 5, "log_pile")

    # Chopping blocks
    zone.place_occupant(wood_x + 10, wood_y + 3, "chopping_block")
    zone.place_occupant(wood_x - 3, wood_y + 4, "chopping_block")

    # Sawhorses
    zone.place_occupant(wood_x - 5, wood_y + 5, "sawhorse")
    zone.place_occupant(wood_x + 11, wood_y - 2, "sawhorse")

    # Stumps (show active clearing - FEWER trees nearby, more stumps)
    stump_positions = [
        (wood_x - 10, wood_y - 8),
        (wood_x + 15, wood_y - 6),
        (wood_x - 8, wood_y + 10),
        (wood_x + 12, wood_y + 10),
        (wood_x - 12, wood_y + 3),
        (wood_x + 18, wood_y + 4),
    ]
    for sx, sy in stump_positions:
        zone.place_occupant(sx, sy, "stump")

    # A few trees remain (sparse - this is an active work area)
    zone.place_occupant(wood_x - 15, wood_y - 12, "tree_oak")
    zone.place_occupant(wood_x + 20, wood_y + 12, "tree_pine")

    # Rock debris
    zone.place_occupant(wood_x + 6, wood_y - 3, "rock_small")
    zone.place_occupant(wood_x - 2, wood_y + 8, "rock_small")


def build_cottages(zone, center):
    """2-3 cottages in SW area, slightly varied."""

    # Cottage 1
    c1_x, c1_y = center - 22, center + 18
    zone.rect_ground(c1_x, c1_y, 8, 7, "wood_floor")
    zone.place_rect_border(c1_x, c1_y, 8, 7, "wall_wood")
    zone.remove_occupant(c1_x + 3, c1_y)
    zone.place_occupant(c1_x + 3, c1_y, "door_wood")
    zone.place_occupant(c1_x + 2, c1_y + 3, "bed_basic")
    zone.place_occupant(c1_x + 5, c1_y + 4, "table_wood")
    zone.place_occupant(c1_x + 6, c1_y + 2, "chair_wood")

    # Cottage 2 (offset, not grid aligned)
    c2_x, c2_y = center - 32, center + 28
    zone.rect_ground(c2_x, c2_y, 8, 7, "wood_floor")
    zone.place_rect_border(c2_x, c2_y, 8, 7, "wall_wood")
    zone.remove_occupant(c2_x + 4, c2_y)
    zone.place_occupant(c2_x + 4, c2_y, "door_wood")
    zone.place_occupant(c2_x + 2, c2_y + 3, "bed_basic")
    zone.place_occupant(c2_x + 5, c2_y + 4, "chest_wood")
    zone.place_occupant(c2_x + 5, c2_y + 2, "barrel")

    # Cottage 3 (smaller, different interior)
    c3_x, c3_y = center - 18, center + 32
    zone.rect_ground(c3_x, c3_y, 7, 6, "wood_floor")
    zone.place_rect_border(c3_x, c3_y, 7, 6, "wall_wood")
    zone.remove_occupant(c3_x + 3, c3_y)
    zone.place_occupant(c3_x + 3, c3_y, "door_wood")
    zone.place_occupant(c3_x + 2, c3_y + 2, "bed_basic")
    zone.place_occupant(c3_x + 4, c3_y + 3, "chair_wood")
    zone.place_occupant(c3_x + 5, c3_y + 3, "chair_wood")


def build_orchard(zone, center):
    """Orchard - NE quadrant, structured grid of fruit trees."""
    # Orchard is close but outside the village core
    orchard_x, orchard_y = center + 55, center - 55

    # Clearing at orchard entrance
    zone.circle_ground(orchard_x, orchard_y + 5, 5, "dirt")

    # Grid of fruit trees (4 rows x 4 cols, 7-cell spacing - smaller grid)
    tree_spacing = 7
    for row in range(4):
        for col in range(4):
            tx = orchard_x + col * tree_spacing - 10
            ty = orchard_y - row * tree_spacing - 8
            if zone.can_place(tx, ty, "tree_fruit"):
                zone.place_occupant(tx, ty, "tree_fruit")

    # Apple crates at row ends
    zone.place_occupant(orchard_x - 14, orchard_y - 6, "apple_crate")
    zone.place_occupant(orchard_x + 12, orchard_y - 6, "apple_crate")
    zone.place_occupant(orchard_x - 14, orchard_y - 20, "apple_crate")
    zone.place_occupant(orchard_x + 12, orchard_y - 20, "apple_crate")

    # Ladders leaning against some trees
    zone.place_occupant(orchard_x - 8, orchard_y - 10, "ladder")
    zone.place_occupant(orchard_x + 4, orchard_y - 22, "ladder")

    # Compost piles at corners
    zone.place_occupant(orchard_x - 16, orchard_y - 28, "compost_pile")
    zone.place_occupant(orchard_x + 14, orchard_y + 3, "compost_pile")

    # Scattered flowers between rows (less dense than meadow)
    for _ in range(10):
        fx = orchard_x + random.randint(-15, 15)
        fy = orchard_y + random.randint(-30, 8)
        if zone.get_ground(fx, fy) == "grass" and not zone.is_blocked(fx, fy):
            zone.place_occupant(fx, fy, random.choice(["flower_wild", "flower_yellow"]))


def build_fly_farm(zone, center):
    """Fly Farm - A proper farming operation for raising flies.

    Has fruit trees (flies love rotting fruit), garden plots, pens/enclosures,
    compost areas, and collection infrastructure. Looks like a working farm.
    """
    farm_cx, farm_cy = center + 45, center + 60

    # === FRUIT TREE SECTION (flies love rotting fruit) ===
    # Small grove of fruit trees - apples fall and rot, attracting flies
    tree_positions = [
        (farm_cx - 25, farm_cy - 15),
        (farm_cx - 18, farm_cy - 18),
        (farm_cx - 22, farm_cy - 8),
        (farm_cx - 15, farm_cy - 12),
    ]
    for tx, ty in tree_positions:
        zone.place_occupant(tx, ty, "tree_fruit")

    # Apple crates near the trees (harvesting/collecting)
    zone.place_occupant(farm_cx - 28, farm_cy - 10, "apple_crate")
    zone.place_occupant(farm_cx - 12, farm_cy - 15, "apple_crate")

    # === FLY PENS (fenced enclosures for breeding) ===
    # Pen 1 - small breeding pen
    pen1_x, pen1_y = farm_cx - 5, farm_cy - 8
    zone.rect_ground(pen1_x, pen1_y, 10, 8, "garden_plot")
    zone.place_rect_border(pen1_x, pen1_y, 10, 8, "fence_wood", skip_corners=False)
    zone.remove_occupant(pen1_x + 4, pen1_y)  # Gate
    zone.place_occupant(pen1_x + 4, pen1_y, "gate_wood")
    # Compost inside pen (attracts flies)
    zone.place_occupant(pen1_x + 2, pen1_y + 3, "compost_pile")
    zone.place_occupant(pen1_x + 6, pen1_y + 4, "compost_pile")

    # Pen 2 - larger collection pen
    pen2_x, pen2_y = farm_cx + 8, farm_cy - 5
    zone.rect_ground(pen2_x, pen2_y, 12, 10, "garden_plot")
    zone.place_rect_border(pen2_x, pen2_y, 12, 10, "fence_wood", skip_corners=False)
    zone.remove_occupant(pen2_x, pen2_y + 4)  # Gate on west side
    zone.place_occupant(pen2_x, pen2_y + 4, "gate_wood")
    # Collection equipment inside
    zone.place_occupant(pen2_x + 3, pen2_y + 3, "collection_tray")
    zone.place_occupant(pen2_x + 7, pen2_y + 5, "collection_tray")
    zone.place_occupant(pen2_x + 5, pen2_y + 7, "compost_pile")

    # === NET CATCHING AREA (open, with posts and nets) ===
    # Net posts in a rough line for catching wild flies
    net_area_x, net_area_y = farm_cx - 15, farm_cy + 10
    zone.place_occupant(net_area_x, net_area_y, "net_post")
    zone.place_occupant(net_area_x + 4, net_area_y + 1, "net_post")
    zone.place_occupant(net_area_x + 8, net_area_y - 1, "net_post")
    zone.place_occupant(net_area_x + 12, net_area_y + 2, "net_post")
    # Bait baskets to lure flies
    zone.place_occupant(net_area_x + 2, net_area_y + 3, "bait_basket")
    zone.place_occupant(net_area_x + 6, net_area_y + 4, "bait_basket")
    zone.place_occupant(net_area_x + 10, net_area_y + 3, "bait_basket")

    # === COMPOST/PROCESSING AREA ===
    compost_x, compost_y = farm_cx + 5, farm_cy + 15
    # Small dirt work area
    zone.circle_ground(compost_x, compost_y, 6, "dirt")
    zone.place_occupant(compost_x - 3, compost_y - 2, "compost_pile")
    zone.place_occupant(compost_x + 2, compost_y + 1, "compost_pile")
    zone.place_occupant(compost_x, compost_y + 4, "collection_tray")
    zone.place_occupant(compost_x - 5, compost_y + 2, "barrel")
    zone.place_occupant(compost_x + 5, compost_y - 1, "crate")

    # === FAILURE EVIDENCE ===
    zone.place_occupant(farm_cx + 22, farm_cy + 8, "broken_net")
    zone.place_occupant(farm_cx - 8, farm_cy + 18, "broken_net")

    # === SCATTERED FLOWERS (flies like flowers too) ===
    for _ in range(12):
        fx = farm_cx + random.randint(-30, 25)
        fy = farm_cy + random.randint(-20, 25)
        if zone.get_ground(fx, fy) == "grass" and not zone.is_blocked(fx, fy):
            zone.place_occupant(fx, fy, random.choice(["flower_wild", "sunflower"]))


def place_forest(zone, cx, cy, radius=30):
    """Place a proper forest mass with core/mid/edge bands.

    Following trees_and_ponds.md:
    - Core (density > 0.70): dense trees, small gaps
    - Mid (0.45-0.70): trees + bushes
    - Edge (0.20-0.45): bushes, tall grass, occasional tree
    - Clearings inside the forest
    """
    tree_types = ["tree_oak", "tree_oak", "tree_oak", "tree_pine"]  # 75% oak

    # Generate bumps for organic edge (not perfectly circular)
    num_bumps = random.randint(4, 6)
    bump_phases = [random.random() * 2 * math.pi for _ in range(num_bumps)]
    bump_amps = [random.uniform(0.1, 0.2) for _ in range(num_bumps)]

    def get_radius_at_angle(angle):
        r = radius
        for i in range(num_bumps):
            r += radius * bump_amps[i] * math.sin((i + 2) * angle + bump_phases[i])
        return max(radius * 0.7, min(radius * 1.3, r))

    def get_density(x, y):
        """Get forest density at point - 1.0 at center, 0 at edge."""
        dx, dy = x - cx, y - cy
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 1:
            return 1.0
        angle = math.atan2(dy, dx)
        local_r = get_radius_at_angle(angle)
        if dist > local_r:
            return 0.0
        return 1.0 - (dist / local_r)

    # Create a clearing inside the forest (negative space)
    clearing_angle = random.random() * 2 * math.pi
    clearing_dist = radius * 0.4
    clearing_cx = int(cx + clearing_dist * math.cos(clearing_angle))
    clearing_cy = int(cy + clearing_dist * math.sin(clearing_angle))
    clearing_radius = random.randint(6, 10)

    def in_clearing(x, y):
        dx, dy = x - clearing_cx, y - clearing_cy
        return (dx * dx + dy * dy) < clearing_radius * clearing_radius

    # Tiles to avoid placing trees on
    avoid_tiles = {"water_deep", "water_shallow", "sand", "mud", "dirt", "stone_path", "wood_floor", "garden_plot"}

    # Place trees/bushes based on density bands
    scan_radius = int(radius * 1.4)
    for dy in range(-scan_radius, scan_radius + 1):
        for dx in range(-scan_radius, scan_radius + 1):
            x, y = cx + dx, cy + dy
            if x < 0 or y < 0 or x >= 512 or y >= 512:
                continue

            # Skip water, roads, and other non-grass tiles
            ground = zone.get_ground(x, y)
            if ground in avoid_tiles:
                continue

            density = get_density(x, y)
            if density < 0.15 or in_clearing(x, y):
                continue

            roll = random.random()

            # Core band: dense trees
            if density > 0.70:
                if roll < 0.25:  # 25% chance per cell
                    zone.place_occupant(x, y, random.choice(tree_types))
                elif roll < 0.30:
                    zone.place_occupant(x, y, "bush")

            # Mid band: trees + bushes
            elif density > 0.45:
                if roll < 0.12:
                    zone.place_occupant(x, y, random.choice(tree_types))
                elif roll < 0.20:
                    zone.place_occupant(x, y, "bush")
                elif roll < 0.23:
                    zone.place_occupant(x, y, "mushroom_red")

            # Edge band: mostly bushes, tall grass, rare trees
            else:
                if roll < 0.04:
                    zone.place_occupant(x, y, random.choice(tree_types))
                elif roll < 0.12:
                    zone.place_occupant(x, y, "bush")
                elif roll < 0.20:
                    zone.place_occupant(x, y, "tall_grass")

    # Add understory to clearing (stump, log pile, mushrooms)
    zone.place_occupant(clearing_cx, clearing_cy, "stump")
    zone.place_occupant(clearing_cx + 3, clearing_cy + 2, "mushroom_red")
    zone.place_occupant(clearing_cx - 2, clearing_cy + 3, "mushroom_red")


def place_rocky_clump(zone, cx, cy, radius=10, rock_count=20):
    """Place a DENSE rocky outcrop - rocks packed tightly, filled in.

    These look like actual rock formations, not scattered pebbles.
    """
    # Mix of rock sizes
    rock_types = [
        ("rock_small", 0.6),
        ("rock_large", 0.25),
        ("stone_block", 0.15),
    ]

    # Core area is very dense
    core_radius = radius * 0.6
    placed = 0
    attempts = 0

    while placed < rock_count and attempts < rock_count * 15:
        attempts += 1

        # Bias toward center for dense core
        if random.random() < 0.7:
            dist = random.random() * core_radius
        else:
            dist = core_radius + random.random() * (radius - core_radius)

        angle = random.random() * 2 * math.pi
        rx = int(cx + dist * math.cos(angle))
        ry = int(cy + dist * math.sin(angle))

        # Pick rock type by weight
        roll = random.random()
        rock_type = "rock_small"
        cumulative = 0
        for rtype, weight in rock_types:
            cumulative += weight
            if roll < cumulative:
                rock_type = rtype
                break

        if zone.place_occupant(rx, ry, rock_type):
            placed += 1


def place_forests(zone, center, seed=2100):
    """Place several proper forest masses with one near village."""
    random.seed(seed + 100)

    # FIRST: Force one forest near village (SW quadrant, ~75 cells from center)
    # Opposite direction from the near-village lake (which is NE)
    forest_angle = random.uniform(math.pi * 1.1, math.pi * 1.4)  # SW direction
    forest_dist = random.randint(70, 85)
    near_forest_x = int(center + forest_dist * math.cos(forest_angle))
    near_forest_y = int(center - forest_dist * math.sin(forest_angle))
    place_forest(zone, near_forest_x, near_forest_y, radius=random.randint(32, 40))

    # Forest positions - (x, y, radius) - larger radii for real forests
    forest_positions = [
        # Corner forests - big
        (65, 65, 38),       # NW corner
        (445, 65, 40),      # NE corner
        (65, 445, 42),      # SW corner
        (445, 445, 38),     # SE corner
        # Edge forests - medium
        (40, 256, 30),      # W edge
        (470, 280, 32),     # E edge
        (256, 35, 28),      # N edge
        (340, 480, 30),     # S edge
    ]

    avoid_positions = [
        (center, center),                    # Village core
        (center + 55, center - 55),          # Orchard (new closer position)
        (center + 45, center + 60),          # Fly farm (new closer position)
        (center - 30, center - 25),          # Woodcutter (new closer position)
        (near_forest_x, near_forest_y),      # Near-village forest we just placed
    ]

    for fx, fy, radius in forest_positions:
        # Skip if too close to key areas
        skip = False
        for ax, ay in avoid_positions:
            if abs(fx - ax) < 70 and abs(fy - ay) < 70:
                skip = True
                break
        if skip:
            continue

        place_forest(zone, fx, fy, radius)


def place_rocky_outcrops(zone, center):
    """Place several dense rocky outcrops around the zone."""

    # Rocky outcrop positions
    rock_positions = [
        (100, 150, 12, 18),   # NW area
        (420, 180, 10, 15),   # NE area
        (380, 400, 14, 20),   # SE area
        (90, 380, 11, 16),    # SW area
        (300, 60, 10, 14),    # N edge
        (480, 350, 12, 15),   # E edge
    ]

    avoid_positions = [
        (center, center),                    # Village core
        (center + 55, center - 55),          # Orchard (new closer position)
        (center + 45, center + 60),          # Fly farm (new closer position)
        (center - 30, center - 25),          # Woodcutter (new closer position)
    ]

    for rx, ry, radius, count in rock_positions:
        skip = False
        for ax, ay in avoid_positions:
            if abs(rx - ax) < 50 and abs(ry - ay) < 50:
                skip = True
                break
        if skip:
            continue

        place_rocky_clump(zone, rx, ry, radius, count)


def place_lake(zone, cx, cy, radius, shore_style="mixed", seed=None):
    """Place a proper lake with deep/shallow water, shore ring, and decorations.

    Following trees_and_ponds.md:
    - Deep interior (water_deep)
    - Shallow rim (water_shallow) with variable thickness
    - Shore ring (sand/mud) with variation
    - Reeds in clumps on muddy shores
    - Approach path or clearing for some lakes
    """
    if seed is not None:
        random.seed(seed)

    # Generate organic shape with bumps - fewer bumps and lower amplitude for rounder lakes
    num_bumps = random.randint(2, 4)
    bump_phases = [random.random() * 2 * math.pi for _ in range(num_bumps)]
    bump_amps = [random.uniform(0.05, 0.12) for _ in range(num_bumps)]

    def get_radius_at_angle(angle):
        r = radius
        for i in range(num_bumps):
            r += radius * bump_amps[i] * math.sin((i + 2) * angle + bump_phases[i])
        return max(radius * 0.6, min(radius * 1.4, r))

    # Paint the lake - deep center, shallow ring, shore ring
    scan_r = int(radius * 1.6)
    deep_ratio = random.uniform(0.50, 0.65)  # Vary per lake

    for dy in range(-scan_r, scan_r + 1):
        for dx in range(-scan_r, scan_r + 1):
            x, y = cx + dx, cy + dy
            if x < 0 or y < 0 or x >= 512 or y >= 512:
                continue

            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 0.5:
                dist = 0.5
            angle = math.atan2(dy, dx)
            local_r = get_radius_at_angle(angle)

            if dist <= local_r * deep_ratio:
                zone.set_ground(x, y, "water_deep")
            elif dist <= local_r:
                zone.set_ground(x, y, "water_shallow")
            elif dist <= local_r + 2:
                # Shore ring - vary style by arc
                arc_style = shore_style
                if shore_style == "mixed":
                    # Different shore styles at different angles
                    arc = int((angle + math.pi) / (2 * math.pi) * 4) % 4
                    arc_style = ["sand", "mud", "sand", "mud"][arc]

                if arc_style == "mud":
                    if random.random() < 0.7:
                        zone.set_ground(x, y, "mud")
                else:
                    if random.random() < 0.6:
                        zone.set_ground(x, y, "sand")

    # Shore decoration - reeds in CLUMPS on muddy shores
    # Pick 4-8 anchor points and grow streaks from them
    reed_anchors = random.randint(4, 8)
    for _ in range(reed_anchors):
        angle = random.random() * 2 * math.pi
        local_r = get_radius_at_angle(angle)
        # Place just outside water
        dist = local_r + random.uniform(1, 3)
        ax = int(cx + dist * math.cos(angle))
        ay = int(cy + dist * math.sin(angle))

        # Only on mud
        if zone.get_ground(ax, ay) == "mud":
            # Grow a small streak of reeds
            streak_len = random.randint(3, 6)
            streak_dir = angle + random.uniform(-0.3, 0.3)
            for i in range(streak_len):
                rx = int(ax + i * math.cos(streak_dir))
                ry = int(ay + i * math.sin(streak_dir))
                zone.place_occupant(rx, ry, "reeds")

    # Small rock clusters on sandy shores
    rock_clusters = random.randint(1, 3)
    for _ in range(rock_clusters):
        angle = random.random() * 2 * math.pi
        local_r = get_radius_at_angle(angle)
        dist = local_r + random.uniform(2, 4)
        rx = int(cx + dist * math.cos(angle))
        ry = int(cy + dist * math.sin(angle))
        if zone.get_ground(rx, ry) == "sand":
            zone.place_occupant(rx, ry, "rock_small")
            zone.place_occupant(rx + 1, ry + 1, "rock_small")


def place_lakes(zone, center, seed=2100):
    """Place 10 natural lakes - 5 large, 5 small - with one near village."""
    random.seed(seed + 500)

    # FIRST: Force one large lake near village (NW quadrant - avoid orchard which is NE)
    near_angle = random.uniform(math.pi * 0.6, math.pi * 0.9)  # NW direction
    near_dist = random.randint(65, 80)
    near_x = int(center + near_dist * math.cos(near_angle))
    near_y = int(center - near_dist * math.sin(near_angle))
    place_lake(zone, near_x, near_y, radius=random.randint(18, 24), seed=seed + 501)
    # Fishing spot near this lake
    approach_x = int(near_x + 30 * math.cos(near_angle + math.pi))
    approach_y = int(near_y - 30 * math.sin(near_angle + math.pi))
    zone.circle_ground(approach_x, approach_y, 3, "dirt")
    zone.place_occupant(approach_x, approach_y, "bench")

    # Large lakes (radius 20-30) - 4 more spread around zone
    large_lake_positions = [
        (85, 85, 24),       # NW corner
        (420, 80, 26),      # NE corner
        (70, 400, 22),      # SW area
        (440, 420, 25),     # SE corner
    ]

    # Small ponds (radius 10-16) - 5 total
    small_pond_positions = [
        (180, 55, 12),      # N edge
        (480, 280, 11),     # E edge
        (45, 200, 10),      # W edge
        (350, 470, 13),     # S edge
        (200, 400, 11),     # SW inner
    ]

    avoid_positions = [
        (center, center),                    # Village core
        (center + 55, center - 55),          # Orchard (new closer position)
        (center + 45, center + 60),          # Fly farm (new closer position)
        (center - 30, center - 25),          # Woodcutter (new closer position)
        (near_x, near_y),                    # Near-village lake we just placed
    ]

    # Place large lakes
    for lx, ly, radius in large_lake_positions:
        skip = False
        for ax, ay in avoid_positions:
            if abs(lx - ax) < 55 and abs(ly - ay) < 55:
                skip = True
                break
        if skip:
            continue
        place_lake(zone, lx, ly, radius, seed=seed + lx + ly)

    # Place small ponds
    for lx, ly, radius in small_pond_positions:
        skip = False
        for ax, ay in avoid_positions:
            if abs(lx - ax) < 40 and abs(ly - ay) < 40:
                skip = True
                break
        if skip:
            continue
        place_lake(zone, lx, ly, radius, seed=seed + lx + ly + 1000)


def scatter_meadow(zone, center):
    """Scatter meadow vegetation, respecting buildings and paths."""

    avoid = {"stone_path", "wood_floor", "garden_plot", "dirt"}

    # Flowers (denser away from center)
    zone.scatter("flower_wild", count=300, min_spacing=3, avoid_tiles=avoid)
    zone.scatter("flower_red", count=80, min_spacing=4, avoid_tiles=avoid)
    zone.scatter("flower_yellow", count=80, min_spacing=4, avoid_tiles=avoid)
    zone.scatter("flower_blue", count=60, min_spacing=4, avoid_tiles=avoid)
    zone.scatter("sunflower", count=30, min_spacing=6, avoid_tiles=avoid)

    # Tall grass in patches
    zone.scatter("tall_grass", count=150, min_spacing=2, avoid_tiles=avoid)

    # Bushes (prefer edges of clearings)
    zone.scatter("bush", count=100, min_spacing=5, avoid_tiles=avoid)

    # Scattered rocks (sparse)
    zone.scatter("rock_small", count=40, min_spacing=12, avoid_tiles=avoid)

    # A few mushrooms in shaded areas
    zone.scatter("mushroom_red", count=15, min_spacing=20, avoid_tiles=avoid)


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
    # 1. BASE TERRAIN
    # =========================================================================
    zone.fill_ground("grass")

    # =========================================================================
    # 2. ROADS (with degradation from center outward)
    # =========================================================================
    build_roads(zone, center)

    # =========================================================================
    # 3. VILLAGE CORE (civic square)
    # =========================================================================
    build_village_square(zone, center)

    # =========================================================================
    # 4. BUILDINGS
    # =========================================================================
    build_city_hall(zone, center)
    build_country_store(zone, center)
    build_ecologist_house(zone, center)
    build_woodcutter_cabin(zone, center)
    build_cottages(zone, center)

    # =========================================================================
    # 5. ORCHARD (structured, NE)
    # =========================================================================
    build_orchard(zone, center)

    # =========================================================================
    # 6. FLY FARM (landscape, NOT fenced)
    # =========================================================================
    build_fly_farm(zone, center)

    # =========================================================================
    # 7. NATURAL FEATURES
    # =========================================================================
    # Lakes/ponds first (before forests so trees don't block water)
    place_lakes(zone, center)

    # Dense forest clumps (actual forests, not sparse trees)
    place_forests(zone, center)

    # Rocky outcrops (dense rock formations)
    place_rocky_outcrops(zone, center)

    # =========================================================================
    # 8. MEADOW SCATTER (respects buildings)
    # =========================================================================
    scatter_meadow(zone, center)

    # =========================================================================
    # SPAWN POINT - on road just north of village square
    # =========================================================================
    zone.set_spawn(center, center - 15)

    # =========================================================================
    # BUG SPAWNING
    # =========================================================================
    zone.set_bug_spawning(
        species_caps={
            "fly_common": {"initial": 100, "max": 300, "spawn_interval": 45.0},
            "butterfly_meadow": {"initial": 60, "max": 200, "spawn_interval": 90.0}
        }
    )
    # Flies spawn zone-wide
    zone.add_spawn_area("zone_wide", ["fly_common"], "zone")
    # Fly farm concentration
    zone.add_spawn_area("fly_farm", ["fly_common"], "circle", cx=center+45, cy=center+60, radius=40)
    # Butterflies in open meadow areas (between village, forests, lakes)
    zone.add_spawn_area("meadow_nw", ["butterfly_meadow"], "circle", cx=180, cy=180, radius=50)
    zone.add_spawn_area("meadow_ne", ["butterfly_meadow"], "circle", cx=330, cy=180, radius=40)
    zone.add_spawn_area("meadow_sw", ["butterfly_meadow"], "circle", cx=180, cy=330, radius=50)
    zone.add_spawn_area("meadow_se", ["butterfly_meadow"], "circle", cx=380, cy=380, radius=40)

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
