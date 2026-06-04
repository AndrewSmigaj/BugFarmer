#!/usr/bin/env python3
"""Generate the Starting Village zone (2,1).

The village occupies the center with meadow, forests, and lakes around it.

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
    zone.path_ground([(center, center + 30), (center, ZONE_SIZE - 20)], "dirt", width=3)

    # Main E-W road - stone near center, dirt extending to borders
    zone.path_ground([(center - 30, center), (center + 30, center)], "stone_path", width=3)
    # West road to border
    zone.path_ground([(center - 30, center), (20, center)], "dirt", width=3)
    # East road to border
    zone.path_ground([(center + 30, center), (ZONE_SIZE - 20, center)], "dirt", width=3)

    # Spur to orchard (NE)
    zone.path_ground([
        (center + 25, center - 15),
        (center + 40, center - 35),
        (center + 55, center - 50)
    ], "dirt", width=2)

    # Spur to fly farm (SE)
    zone.path_ground([
        (center + 15, center + 25),
        (center + 30, center + 45),
        (center + 45, center + 55)
    ], "dirt", width=2)

    # Spur to woodcutter (NW)
    zone.path_ground([
        (center - 15, center - 12),
        (center - 25, center - 20)
    ], "dirt", width=2)


def build_village_square(zone, center):
    """Build the civic square with well, benches, notice board."""
    # Well (center of square)
    zone.place_occupant(center - 1, center - 1, "well")

    # Notice board at north entrance
    zone.place_occupant(center + 2, center - 5, "notice_board")

    # Benches around the square edges
    zone.place_occupant(center - 4, center - 3, "bench")  # West side
    zone.place_occupant(center + 3, center + 2, "bench")  # East side

    # Planter boxes near square corners (on grass, not stone)
    zone.place_occupant(center - 8, center - 8, "planter_box")  # NW corner
    zone.place_occupant(center + 7, center + 7, "planter_box")  # SE corner

    # Signposts at road entrances
    zone.place_occupant(center - 8, center, "signpost")   # West entrance
    zone.place_occupant(center, center - 8, "signpost")   # North entrance

    # Lamps at square corners
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

    # Interior
    zone.place_occupant(ch_x + 5, ch_y + 8, "table_wood")  # Main desk
    zone.place_occupant(ch_x + 6, ch_y + 6, "chair_wood")   # Behind desk
    zone.place_occupant(ch_x + 4, ch_y + 4, "chair_wood")   # Visitor
    zone.place_occupant(ch_x + 7, ch_y + 4, "chair_wood")   # Visitor
    zone.place_occupant(ch_x + 11, ch_y + 3, "bookshelf")
    zone.place_occupant(ch_x + 11, ch_y + 7, "bookshelf")
    zone.place_occupant(ch_x + 2, ch_y + 9, "chest_wood")
    zone.place_occupant(ch_x + 2, ch_y + 3, "crate")
    zone.place_occupant(ch_x + 3, ch_y + 3, "crate")

    # Exterior
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
    for x in range(shop_x, shop_x + 12):
        zone.place_occupant(x, shop_y + 9, "wall_wood")
    for y in range(shop_y, shop_y + 10):
        zone.place_occupant(shop_x + 11, y, "wall_wood")
    for y in range(shop_y, shop_y + 10):
        zone.place_occupant(shop_x, y, "wall_wood")

    # Interior
    zone.place_occupant(shop_x + 4, shop_y + 6, "table_wood")
    zone.place_occupant(shop_x + 2, shop_y + 7, "bookshelf")
    zone.place_occupant(shop_x + 8, shop_y + 7, "bookshelf")
    zone.place_occupant(shop_x + 8, shop_y + 4, "chest_wood")
    zone.place_occupant(shop_x + 2, shop_y + 4, "barrel")
    zone.place_occupant(shop_x + 3, shop_y + 4, "barrel")

    # Exterior
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

    # Interior
    zone.place_occupant(eco_x + 2, eco_y + 4, "table_wood")
    zone.place_occupant(eco_x + 2, eco_y + 2, "bookshelf")
    zone.place_occupant(eco_x + 5, eco_y + 4, "chest_wood")
    zone.place_occupant(eco_x + 5, eco_y + 2, "potted_plant")

    # Exterior - test plots
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

    # Exterior - signs of active wood harvesting
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

    # Stumps (show active clearing)
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

    # A few trees remain (sparse - active work area)
    zone.place_occupant(wood_x - 15, wood_y - 12, "tree_oak")
    zone.place_occupant(wood_x + 20, wood_y + 12, "tree_pine")

    # Rock debris
    zone.place_occupant(wood_x + 6, wood_y - 3, "stone_block")
    zone.place_occupant(wood_x - 2, wood_y + 8, "stone_block")


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
    orchard_x, orchard_y = center + 55, center - 55

    # Clearing at orchard entrance
    zone.circle_ground(orchard_x, orchard_y + 5, 5, "dirt")

    # Grid of fruit trees (4 rows x 4 cols, 7-cell spacing)
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

    # Scattered flowers between rows
    for _ in range(10):
        fx = orchard_x + random.randint(-15, 15)
        fy = orchard_y + random.randint(-30, 8)
        if zone.get_ground(fx, fy) == "grass" and not zone.is_blocked(fx, fy):
            zone.place_occupant(fx, fy, random.choice(["flower_wild", "flower_yellow"]))


def build_fly_farm(zone, center):
    """Fly Farm - A proper farming operation for raising flies.

    Has fruit trees (flies love rotting fruit), garden plots, pens/enclosures,
    compost areas, and collection infrastructure.
    """
    farm_cx, farm_cy = center + 45, center + 60

    # === FRUIT TREE SECTION ===
    tree_positions = [
        (farm_cx - 25, farm_cy - 15),
        (farm_cx - 18, farm_cy - 18),
        (farm_cx - 22, farm_cy - 8),
        (farm_cx - 15, farm_cy - 12),
    ]
    for tx, ty in tree_positions:
        zone.place_occupant(tx, ty, "tree_fruit")

    zone.place_occupant(farm_cx - 28, farm_cy - 10, "apple_crate")
    zone.place_occupant(farm_cx - 12, farm_cy - 15, "apple_crate")

    # === FLY PENS ===
    # Pen 1 - small breeding pen
    pen1_x, pen1_y = farm_cx - 5, farm_cy - 8
    zone.rect_ground(pen1_x, pen1_y, 10, 8, "garden_plot")
    zone.place_rect_border(pen1_x, pen1_y, 10, 8, "fence_wood", skip_corners=False)
    zone.remove_occupant(pen1_x + 4, pen1_y)
    zone.place_occupant(pen1_x + 4, pen1_y, "gate_wood")
    zone.place_occupant(pen1_x + 2, pen1_y + 3, "compost_pile")
    zone.place_occupant(pen1_x + 6, pen1_y + 4, "compost_pile")

    # Pen 2 - larger collection pen
    pen2_x, pen2_y = farm_cx + 8, farm_cy - 5
    zone.rect_ground(pen2_x, pen2_y, 12, 10, "garden_plot")
    zone.place_rect_border(pen2_x, pen2_y, 12, 10, "fence_wood", skip_corners=False)
    zone.remove_occupant(pen2_x, pen2_y + 4)
    zone.place_occupant(pen2_x, pen2_y + 4, "gate_wood")
    zone.place_occupant(pen2_x + 3, pen2_y + 3, "collection_tray")
    zone.place_occupant(pen2_x + 7, pen2_y + 5, "collection_tray")
    zone.place_occupant(pen2_x + 5, pen2_y + 7, "compost_pile")

    # === NET CATCHING AREA ===
    net_area_x, net_area_y = farm_cx - 15, farm_cy + 10
    zone.place_occupant(net_area_x, net_area_y, "net_post")
    zone.place_occupant(net_area_x + 4, net_area_y + 1, "net_post")
    zone.place_occupant(net_area_x + 8, net_area_y - 1, "net_post")
    zone.place_occupant(net_area_x + 12, net_area_y + 2, "net_post")
    zone.place_occupant(net_area_x + 2, net_area_y + 3, "bait_basket")
    zone.place_occupant(net_area_x + 6, net_area_y + 4, "bait_basket")
    zone.place_occupant(net_area_x + 10, net_area_y + 3, "bait_basket")

    # === COMPOST/PROCESSING AREA ===
    compost_x, compost_y = farm_cx + 5, farm_cy + 15
    zone.circle_ground(compost_x, compost_y, 6, "dirt")
    zone.place_occupant(compost_x - 3, compost_y - 2, "compost_pile")
    zone.place_occupant(compost_x + 2, compost_y + 1, "compost_pile")
    zone.place_occupant(compost_x, compost_y + 4, "collection_tray")
    zone.place_occupant(compost_x - 5, compost_y + 2, "barrel")
    zone.place_occupant(compost_x + 5, compost_y - 1, "crate")

    # === FAILURE EVIDENCE ===
    zone.place_occupant(farm_cx + 22, farm_cy + 8, "broken_net")
    zone.place_occupant(farm_cx - 8, farm_cy + 18, "broken_net")

    # === SCATTERED FLOWERS ===
    for _ in range(12):
        fx = farm_cx + random.randint(-30, 25)
        fy = farm_cy + random.randint(-20, 25)
        if zone.get_ground(fx, fy) == "grass" and not zone.is_blocked(fx, fy):
            zone.place_occupant(fx, fy, random.choice(["flower_wild", "sunflower"]))


def place_forest(zone, cx, cy, radius=30):
    """Place a proper forest mass with core/mid/edge bands."""
    tree_types = ["tree_oak", "tree_oak", "tree_oak", "tree_pine"]  # 75% oak

    num_bumps = random.randint(4, 6)
    bump_phases = [random.random() * 2 * math.pi for _ in range(num_bumps)]
    bump_amps = [random.uniform(0.1, 0.2) for _ in range(num_bumps)]

    def get_radius_at_angle(angle):
        r = radius
        for i in range(num_bumps):
            r += radius * bump_amps[i] * math.sin((i + 2) * angle + bump_phases[i])
        return max(radius * 0.7, min(radius * 1.3, r))

    def get_density(x, y):
        dx, dy = x - cx, y - cy
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 1:
            return 1.0
        angle = math.atan2(dy, dx)
        local_r = get_radius_at_angle(angle)
        if dist > local_r:
            return 0.0
        return 1.0 - (dist / local_r)

    # Create a clearing inside the forest
    clearing_angle = random.random() * 2 * math.pi
    clearing_dist = radius * 0.4
    clearing_cx = int(cx + clearing_dist * math.cos(clearing_angle))
    clearing_cy = int(cy + clearing_dist * math.sin(clearing_angle))
    clearing_radius = random.randint(6, 10)

    def in_clearing(x, y):
        dx, dy = x - clearing_cx, y - clearing_cy
        return (dx * dx + dy * dy) < clearing_radius * clearing_radius

    avoid_tiles = {"water_deep", "water_shallow", "sand", "mud", "dirt", "stone_path", "wood_floor", "garden_plot"}

    scan_radius = int(radius * 1.4)
    for dy in range(-scan_radius, scan_radius + 1):
        for dx in range(-scan_radius, scan_radius + 1):
            x, y = cx + dx, cy + dy
            if x < 0 or y < 0 or x >= ZONE_SIZE or y >= ZONE_SIZE:
                continue

            ground = zone.get_ground(x, y)
            if ground in avoid_tiles:
                continue

            density = get_density(x, y)
            if density < 0.15 or in_clearing(x, y):
                continue

            roll = random.random()

            if density > 0.70:
                if roll < 0.25:
                    zone.place_occupant(x, y, random.choice(tree_types))
                elif roll < 0.30:
                    zone.place_occupant(x, y, "bush")
            elif density > 0.45:
                if roll < 0.12:
                    zone.place_occupant(x, y, random.choice(tree_types))
                elif roll < 0.20:
                    zone.place_occupant(x, y, "bush")
                elif roll < 0.23:
                    zone.place_occupant(x, y, "mushroom_red")
            else:
                if roll < 0.04:
                    zone.place_occupant(x, y, random.choice(tree_types))
                elif roll < 0.12:
                    zone.place_occupant(x, y, "bush")
                elif roll < 0.20:
                    zone.place_occupant(x, y, "tall_grass")

    # Clearing understory
    zone.place_occupant(clearing_cx, clearing_cy, "stump")
    zone.place_occupant(clearing_cx + 3, clearing_cy + 2, "mushroom_red")
    zone.place_occupant(clearing_cx - 2, clearing_cy + 3, "mushroom_red")


def place_rocky_clump(zone, cx, cy, radius=10, rock_count=20):
    """Place a DENSE rocky outcrop."""
    rock_types = [
        ("stone_block", 1.0),
    ]

    core_radius = radius * 0.6
    placed = 0
    attempts = 0

    while placed < rock_count and attempts < rock_count * 15:
        attempts += 1

        if random.random() < 0.7:
            dist = random.random() * core_radius
        else:
            dist = core_radius + random.random() * (radius - core_radius)

        angle = random.random() * 2 * math.pi
        rx = int(cx + dist * math.cos(angle))
        ry = int(cy + dist * math.sin(angle))

        roll = random.random()
        rock_type = "stone_block"
        cumulative = 0
        for rtype, weight in rock_types:
            cumulative += weight
            if roll < cumulative:
                rock_type = rtype
                break

        if zone.place_occupant(rx, ry, rock_type):
            placed += 1


def place_forests(zone, center, seed=2100):
    """Place several proper forest masses."""
    random.seed(seed + 100)

    # Force one forest near village (SW quadrant)
    forest_angle = random.uniform(math.pi * 1.1, math.pi * 1.4)
    forest_dist = random.randint(55, 70)
    near_forest_x = int(center + forest_dist * math.cos(forest_angle))
    near_forest_y = int(center - forest_dist * math.sin(forest_angle))
    place_forest(zone, near_forest_x, near_forest_y, radius=random.randint(32, 40))

    # Forest positions - same radii, repositioned for 256x256 zone
    forest_positions = [
        (35, 35, 30),       # NW corner
        (220, 35, 30),      # NE corner
        (35, 220, 32),      # SW corner
        (220, 220, 30),     # SE corner
        (20, center, 25),   # W edge
        (ZONE_SIZE - 20, center + 10, 25),  # E edge
    ]

    avoid_positions = [
        (center, center),
        (center + 55, center - 55),          # Orchard
        (center + 45, center + 60),          # Fly farm
        (center - 30, center - 25),          # Woodcutter
        (near_forest_x, near_forest_y),
    ]

    for fx, fy, radius in forest_positions:
        skip = False
        for ax, ay in avoid_positions:
            if abs(fx - ax) < 60 and abs(fy - ay) < 60:
                skip = True
                break
        if skip:
            continue

        place_forest(zone, fx, fy, radius)


def place_rocky_outcrops(zone, center):
    """Place several dense rocky outcrops around the zone."""
    rock_positions = [
        (55, 80, 12, 18),    # NW area
        (200, 90, 10, 15),   # NE area
        (190, 200, 14, 20),  # SE area
        (50, 190, 11, 16),   # SW area
    ]

    avoid_positions = [
        (center, center),
        (center + 55, center - 55),
        (center + 45, center + 60),
        (center - 30, center - 25),
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
    """Place a proper lake with deep/shallow water, shore ring, and decorations."""
    if seed is not None:
        random.seed(seed)

    num_bumps = random.randint(2, 4)
    bump_phases = [random.random() * 2 * math.pi for _ in range(num_bumps)]
    bump_amps = [random.uniform(0.05, 0.12) for _ in range(num_bumps)]

    def get_radius_at_angle(angle):
        r = radius
        for i in range(num_bumps):
            r += radius * bump_amps[i] * math.sin((i + 2) * angle + bump_phases[i])
        return max(radius * 0.6, min(radius * 1.4, r))

    scan_r = int(radius * 1.6)
    deep_ratio = random.uniform(0.50, 0.65)

    for dy in range(-scan_r, scan_r + 1):
        for dx in range(-scan_r, scan_r + 1):
            x, y = cx + dx, cy + dy
            if x < 0 or y < 0 or x >= ZONE_SIZE or y >= ZONE_SIZE:
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
                arc_style = shore_style
                if shore_style == "mixed":
                    arc = int((angle + math.pi) / (2 * math.pi) * 4) % 4
                    arc_style = ["sand", "mud", "sand", "mud"][arc]

                if arc_style == "mud":
                    if random.random() < 0.7:
                        zone.set_ground(x, y, "mud")
                else:
                    if random.random() < 0.6:
                        zone.set_ground(x, y, "sand")

    # Reeds in clumps on muddy shores
    reed_anchors = random.randint(4, 8)
    for _ in range(reed_anchors):
        angle = random.random() * 2 * math.pi
        local_r = get_radius_at_angle(angle)
        dist = local_r + random.uniform(1, 3)
        ax = int(cx + dist * math.cos(angle))
        ay = int(cy + dist * math.sin(angle))

        if zone.get_ground(ax, ay) == "mud":
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
            zone.place_occupant(rx, ry, "stone_block")
            zone.place_occupant(rx + 1, ry + 1, "stone_block")


def place_lakes(zone, center, seed=2100):
    """Place natural lakes around the zone."""
    random.seed(seed + 500)

    # Force one large lake near village (NW quadrant)
    near_angle = random.uniform(math.pi * 0.6, math.pi * 0.9)
    near_dist = random.randint(55, 70)
    near_x = int(center + near_dist * math.cos(near_angle))
    near_y = int(center - near_dist * math.sin(near_angle))
    place_lake(zone, near_x, near_y, radius=random.randint(18, 24), seed=seed + 501)
    # Fishing spot near this lake
    approach_x = int(near_x + 30 * math.cos(near_angle + math.pi))
    approach_y = int(near_y - 30 * math.sin(near_angle + math.pi))
    zone.circle_ground(approach_x, approach_y, 3, "dirt")
    zone.place_occupant(approach_x, approach_y, "bench")

    # Large lakes - same radii, repositioned for 256x256
    large_lake_positions = [
        (45, 45, 22),       # NW corner
        (210, 45, 24),      # NE corner
        (40, 210, 20),      # SW area
    ]

    # Small ponds
    small_pond_positions = [
        (90, 25, 12),       # N edge
        (ZONE_SIZE - 20, center, 11),  # E edge
        (25, 100, 10),      # W edge
    ]

    avoid_positions = [
        (center, center),
        (center + 55, center - 55),
        (center + 45, center + 60),
        (center - 30, center - 25),
        (near_x, near_y),
    ]

    for lx, ly, radius in large_lake_positions:
        skip = False
        for ax, ay in avoid_positions:
            if abs(lx - ax) < 55 and abs(ly - ay) < 55:
                skip = True
                break
        if skip:
            continue
        place_lake(zone, lx, ly, radius, seed=seed + lx + ly)

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

    # Quartered counts for smaller zone area
    zone.scatter("flower_wild", count=75, min_spacing=3, avoid_tiles=avoid)
    zone.scatter("flower_red", count=20, min_spacing=4, avoid_tiles=avoid)
    zone.scatter("flower_yellow", count=20, min_spacing=4, avoid_tiles=avoid)
    zone.scatter("flower_blue", count=15, min_spacing=4, avoid_tiles=avoid)
    zone.scatter("sunflower", count=8, min_spacing=6, avoid_tiles=avoid)

    zone.scatter("tall_grass", count=38, min_spacing=2, avoid_tiles=avoid)
    zone.scatter("bush", count=25, min_spacing=5, avoid_tiles=avoid)
    zone.scatter("stone_block", count=10, min_spacing=12, avoid_tiles=avoid)
    zone.scatter("mushroom_red", count=4, min_spacing=20, avoid_tiles=avoid)


def main():
    zone = ZoneBuilder(
        zone_id="village_21",
        row=2,
        col=1,
        name="Starting Village",
        biome="village",
        seed=2100
    )

    center = ZONE_SIZE // 2

    # =========================================================================
    # 1. BASE TERRAIN
    # =========================================================================
    zone.fill_ground("grass")

    # =========================================================================
    # 2. ROADS
    # =========================================================================
    build_roads(zone, center)

    # =========================================================================
    # 3. VILLAGE CORE
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
    # 5. ORCHARD
    # =========================================================================
    build_orchard(zone, center)

    # =========================================================================
    # 6. FLY FARM
    # =========================================================================
    build_fly_farm(zone, center)

    # =========================================================================
    # 7. NATURAL FEATURES
    # =========================================================================
    place_lakes(zone, center)
    place_forests(zone, center)
    place_rocky_outcrops(zone, center)

    # =========================================================================
    # 8. MEADOW SCATTER
    # =========================================================================
    scatter_meadow(zone, center)

    # =========================================================================
    # SPAWN POINT
    # =========================================================================
    zone.set_spawn(center, center - 15)

    # =========================================================================
    # BUG SPAWNING (quartered counts for smaller zone)
    # =========================================================================
    zone.set_bug_spawning(
        species_caps={
            "fly_common": {"initial": 25, "max": 75, "spawn_interval": 45.0},
            "butterfly_meadow": {"initial": 15, "max": 50, "spawn_interval": 90.0}
        }
    )
    zone.add_spawn_area("zone_wide", ["fly_common"], "zone")
    zone.add_spawn_area("fly_farm", ["fly_common"], "circle", cx=center+45, cy=center+60, radius=40)
    # Butterflies in open meadow areas - repositioned for 256x256
    zone.add_spawn_area("meadow_nw", ["butterfly_meadow"], "circle", cx=50, cy=50, radius=35)
    zone.add_spawn_area("meadow_sw", ["butterfly_meadow"], "circle", cx=50, cy=200, radius=35)

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
