#!/usr/bin/env python3
"""Generate Underground Passages zone (3,1).

This zone is fundamentally different from surface zones:
- Ground layer: cave_floor everywhere (revealed when blocks mined)
- Occupant layer: mostly solid blocks (Terraria-style)
- Pre-carved areas: mine entrance, tunnel, natural caverns
"""

import sys
import os
import math
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generate_zone import ZoneBuilder, ZONE_SIZE


def main():
    seed = 3100
    random.seed(seed)

    zone = ZoneBuilder(
        zone_id="underground_passages_31",
        row=3,
        col=1,
        name="Underground Passages",
        biome="cave",
        seed=seed
    )

    center = ZONE_SIZE // 2

    # =========================================================================
    # BASE TERRAIN - cave_floor everywhere (revealed when blocks mined)
    # =========================================================================
    zone.fill_ground("cave_floor")

    # =========================================================================
    # FILL WITH BLOCKS - the entire zone is solid rock
    # =========================================================================
    print("Filling zone with blocks (this takes a moment)...")

    for y in range(ZONE_SIZE):
        if y % 100 == 0:
            print(f"  Row {y}/{ZONE_SIZE}...")
        for x in range(ZONE_SIZE):
            # Determine block type based on depth (y increases = deeper into cliff)
            depth_ratio = y / ZONE_SIZE
            roll = random.random()

            if depth_ratio < 0.15:
                # Near surface: mostly dirt
                if roll < 0.75:
                    block = "dirt_block"
                elif roll < 0.95:
                    block = "stone_block"
                else:
                    block = "clay_block"
            elif depth_ratio < 0.4:
                # Mid depth: mixed
                if roll < 0.25:
                    block = "dirt_block"
                elif roll < 0.92:
                    block = "stone_block"
                else:
                    block = "clay_block"
            else:
                # Deep: mostly stone
                if roll < 0.08:
                    block = "dirt_block"
                elif roll < 0.88:
                    block = "stone_block"
                else:
                    block = "clay_block"

            zone.place_occupant(x, y, block)

    # =========================================================================
    # ROCKY CLIFF EDGE AT NORTH (transition to village)
    # =========================================================================
    print("Creating rocky cliff edge...")
    create_cliff_edge(zone)

    # =========================================================================
    # CLIFF OUTCROPPINGS (along all edges)
    # =========================================================================
    print("Adding cliff outcroppings...")
    create_outcroppings(zone)

    # =========================================================================
    # SCATTER ORE VEINS (quartered for smaller zone)
    # =========================================================================
    print("Placing ore veins...")

    # Coal and copper - common throughout
    place_ore_veins(zone, "ore_coal_block", count=25, min_y=20, max_y=ZONE_SIZE)
    place_ore_veins(zone, "ore_copper_block", count=22, min_y=20, max_y=ZONE_SIZE)

    # Iron - more common in mid-south
    place_ore_veins(zone, "ore_iron_block", count=12, min_y=ZONE_SIZE // 4, max_y=ZONE_SIZE)

    # Silver - rare, south only
    place_ore_veins(zone, "ore_silver_block", count=5, min_y=ZONE_SIZE // 2, max_y=ZONE_SIZE)

    # Gold - very rare, deep south
    place_ore_veins(zone, "ore_gold_block", count=2, min_y=int(ZONE_SIZE * 0.7), max_y=ZONE_SIZE)

    # =========================================================================
    # CARVE ORGANIC MINE TUNNEL (from north, going south)
    # =========================================================================
    print("Carving organic mine tunnel...")

    entrance_x = center
    tunnel_length = int(ZONE_SIZE * 0.4)

    carve_organic_tunnel(zone, entrance_x, 0, tunnel_length)

    # =========================================================================
    # CIRCULAR MINER'S CAMP (about 50 cells in)
    # =========================================================================
    print("Creating miner's camp...")

    camp_x = center
    camp_y = 55
    camp_radius = 14

    carve_organic_cavern(zone, camp_x, camp_y, camp_radius, irregularity=0.2)

    # Stone floor in camp center
    zone.circle_ground(camp_x, camp_y, camp_radius - 2, "stone_floor")

    # Camp objects
    zone.place_occupant(camp_x - 5, camp_y - 2, "workbench")
    zone.place_occupant(camp_x + 4, camp_y - 3, "chest_wood")
    zone.place_occupant(camp_x + 4, camp_y + 1, "chest_wood")
    zone.place_occupant(camp_x - 6, camp_y + 4, "signpost")
    zone.place_occupant(camp_x + 2, camp_y + 5, "anvil")
    zone.place_occupant(camp_x - 3, camp_y + 3, "barrel")
    zone.place_occupant(camp_x - 2, camp_y + 3, "barrel")
    zone.place_occupant(camp_x - 4, camp_y + 6, "crate")

    # Torches around camp perimeter
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        tx = int(camp_x + (camp_radius - 2) * math.cos(rad))
        ty = int(camp_y + (camp_radius - 2) * math.sin(rad))
        zone.place_occupant(tx, ty, "torch_wall")

    # =========================================================================
    # BRANCH TUNNELS (organic)
    # =========================================================================
    print("Carving branch tunnels...")

    # East branch
    carve_organic_branch(zone, center + 3, 90, direction="east", length=70)

    # West branch
    carve_organic_branch(zone, center - 3, 130, direction="west", length=80)

    # Southeast branch (deeper)
    carve_organic_branch(zone, center + 2, 180, direction="southeast", length=50)

    # =========================================================================
    # NATURAL CAVERNS (organic shapes, various sizes)
    # =========================================================================
    print("Carving natural caverns...")

    caverns = [
        # (cx, cy, radius, has_water, has_crystals, irregularity)
        # Western caverns
        (50, 120, 18, False, True, 0.35),    # Large crystal cavern
        (70, 200, 14, True, False, 0.3),     # Water cavern
        (45, 225, 20, False, False, 0.4),    # Large empty cavern

        # Eastern caverns
        (200, 100, 15, False, True, 0.3),    # Crystal cavern
        (210, 185, 12, True, True, 0.25),    # Mixed cavern
        (190, 215, 22, True, False, 0.35),   # Large water cavern

        # Central/South caverns
        (130, 200, 16, False, True, 0.3),    # Crystal cavern
        (160, 160, 13, False, False, 0.25),  # Medium cavern
        (100, 175, 18, True, True, 0.35),    # Large mixed cavern

        # Small hidden caverns
        (100, 235, 10, False, False, 0.2),   # Small hidden
        (155, 140, 11, True, False, 0.25),   # Small water
    ]

    for cx, cy, radius, has_water, has_crystals, irreg in caverns:
        carve_organic_cavern(zone, cx, cy, radius, irregularity=irreg)

        if has_water:
            # Organic water pool
            pool_r = radius // 2
            create_organic_pool(zone, cx, cy, pool_r)

        place_cavern_objects(zone, cx, cy, radius, has_crystals)

    # =========================================================================
    # ORE EXPOSED IN TUNNEL WALLS
    # =========================================================================
    print("Exposing ore in tunnel walls...")
    expose_ore_in_tunnels(zone, center, tunnel_length)

    # =========================================================================
    # SPAWN POINT (in miner's camp)
    # =========================================================================
    zone.set_spawn(camp_x, camp_y)

    # =========================================================================
    # EXPORT
    # =========================================================================
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "nakama", "data", "zones", "underground_passages_31"
    )
    zone.export(output_dir)

    stats = zone.stats()
    print(f"\nOccupant counts:")
    for occ_id, count in sorted(stats["occupant_counts"].items()):
        print(f"  {occ_id}: {count}")


def create_cliff_edge(zone):
    """Create a rocky, uneven cliff edge at the north (transition from village)."""
    for x in range(ZONE_SIZE):
        # Vary the cliff depth using noise
        base_depth = 8
        noise = math.sin(x * 0.05) * 4 + math.sin(x * 0.13) * 2 + random.uniform(-2, 2)
        cliff_start = int(base_depth + noise)

        # Remove blocks above cliff line to create uneven top
        for y in range(min(cliff_start, 15)):
            zone.remove_occupant(x, y)

        # Add scattered stone blocks just below the cliff edge
        if random.random() < 0.15 and cliff_start < 12:
            zone.remove_occupant(x, cliff_start)
            zone.place_occupant(x, cliff_start, "stone_block")


def create_outcroppings(zone):
    """Add natural rock outcroppings along zone edges."""
    # West edge outcroppings
    for _ in range(4):
        y = random.randint(50, ZONE_SIZE - 50)
        depth = random.randint(8, 20)
        height = random.randint(15, 35)
        carve_outcropping(zone, 0, y, depth, height, direction="east")

    # East edge outcroppings
    for _ in range(4):
        y = random.randint(50, ZONE_SIZE - 50)
        depth = random.randint(8, 20)
        height = random.randint(15, 35)
        carve_outcropping(zone, ZONE_SIZE - 1, y, depth, height, direction="west")

    # South edge outcroppings (fewer, leads to deeper zones)
    for _ in range(2):
        x = random.randint(50, ZONE_SIZE - 50)
        depth = random.randint(6, 15)
        width = random.randint(12, 30)
        carve_outcropping(zone, x, ZONE_SIZE - 1, depth, width, direction="north")


def carve_outcropping(zone, start_x, start_y, depth, size, direction):
    """Carve a small cave/outcropping from an edge."""
    if direction == "east":
        for d in range(depth):
            width = int(size * (1 - d / depth) * random.uniform(0.7, 1.0))
            for w in range(-width // 2, width // 2):
                y = start_y + w
                x = start_x + d
                if 0 <= x < ZONE_SIZE and 0 <= y < ZONE_SIZE:
                    zone.remove_occupant(x, y)
    elif direction == "west":
        for d in range(depth):
            width = int(size * (1 - d / depth) * random.uniform(0.7, 1.0))
            for w in range(-width // 2, width // 2):
                y = start_y + w
                x = start_x - d
                if 0 <= x < ZONE_SIZE and 0 <= y < ZONE_SIZE:
                    zone.remove_occupant(x, y)
    elif direction == "north":
        for d in range(depth):
            width = int(size * (1 - d / depth) * random.uniform(0.7, 1.0))
            for w in range(-width // 2, width // 2):
                x = start_x + w
                y = start_y - d
                if 0 <= x < ZONE_SIZE and 0 <= y < ZONE_SIZE:
                    zone.remove_occupant(x, y)


def carve_organic_tunnel(zone, start_x, start_y, length):
    """Carve a natural-looking tunnel that widens and narrows."""
    x = start_x
    y = start_y

    base_width = 6

    for i in range(length):
        # Wander slightly left/right
        x += random.choice([-1, 0, 0, 0, 1])
        x = max(20, min(ZONE_SIZE - 20, x))

        # Vary width organically
        width_noise = math.sin(i * 0.08) * 2 + math.sin(i * 0.2) * 1.5
        width = int(base_width + width_noise + random.uniform(-1, 1))
        width = max(4, min(10, width))

        # Carve this section
        for dx in range(-width // 2, width // 2 + 1):
            # Add slight height variation too
            height_var = random.randint(0, 1)
            for dy in range(-height_var, height_var + 1):
                nx, ny = x + dx, y + i + dy
                if 0 <= nx < ZONE_SIZE and 0 <= ny < ZONE_SIZE:
                    zone.remove_occupant(nx, ny)

        # Occasionally widen into small chambers
        if random.random() < 0.03 and i > 20:
            chamber_radius = random.randint(5, 8)
            for cy in range(-chamber_radius, chamber_radius + 1):
                for cx in range(-chamber_radius, chamber_radius + 1):
                    if cx*cx + cy*cy <= chamber_radius * chamber_radius:
                        nx, ny = x + cx, y + i + cy
                        if 0 <= nx < ZONE_SIZE and 0 <= ny < ZONE_SIZE:
                            zone.remove_occupant(nx, ny)


def carve_organic_branch(zone, start_x, start_y, direction, length):
    """Carve a branch tunnel in the given direction."""
    x, y = start_x, start_y

    dx_map = {"east": 1, "west": -1, "southeast": 1, "southwest": -1}
    dy_map = {"east": 0, "west": 0, "southeast": 1, "southwest": 1}

    dx_base = dx_map.get(direction, 1)
    dy_base = dy_map.get(direction, 0)

    for i in range(length):
        # Move in direction with slight variation
        x += dx_base + random.choice([-1, 0, 0, 0, 0, 1]) if dx_base == 0 else dx_base
        y += dy_base + random.choice([0, 0, 0, 1]) if dy_base == 0 else dy_base + random.choice([-1, 0, 0, 1])

        x = max(10, min(ZONE_SIZE - 10, x))
        y = max(10, min(ZONE_SIZE - 10, y))

        # Width varies
        width = 4 + int(math.sin(i * 0.1) * 1.5) + random.randint(-1, 1)
        width = max(3, min(6, width))

        for w in range(-width // 2, width // 2 + 1):
            if dx_base != 0:  # Horizontal-ish
                ny = y + w
                if 0 <= x < ZONE_SIZE and 0 <= ny < ZONE_SIZE:
                    zone.remove_occupant(x, ny)
            else:  # Vertical-ish
                nx = x + w
                if 0 <= nx < ZONE_SIZE and 0 <= y < ZONE_SIZE:
                    zone.remove_occupant(nx, y)


def carve_organic_cavern(zone, cx, cy, radius, irregularity=0.3):
    """Carve an organic, non-circular cavern."""
    num_bumps = random.randint(5, 9)
    bump_phases = [random.random() * 2 * math.pi for _ in range(num_bumps)]
    bump_amplitudes = [random.uniform(0.1, irregularity) for _ in range(num_bumps)]

    def get_radius_at_angle(angle):
        r = radius
        for i in range(num_bumps):
            freq = i + 2
            r += radius * bump_amplitudes[i] * math.sin(freq * angle + bump_phases[i])
        return max(radius * 0.4, min(radius * 1.5, r))

    max_r = int(radius * 1.6)
    for dy in range(-max_r, max_r + 1):
        for dx in range(-max_r, max_r + 1):
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 0.1:
                continue
            angle = math.atan2(dy, dx)
            local_radius = get_radius_at_angle(angle)

            if dist <= local_radius:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < ZONE_SIZE and 0 <= ny < ZONE_SIZE:
                    zone.remove_occupant(nx, ny)


def create_organic_pool(zone, cx, cy, radius):
    """Create an organic-shaped water pool."""
    num_bumps = random.randint(3, 6)
    bump_phases = [random.random() * 2 * math.pi for _ in range(num_bumps)]
    bump_amplitudes = [random.uniform(0.15, 0.35) for _ in range(num_bumps)]

    def get_radius_at_angle(angle):
        r = radius
        for i in range(num_bumps):
            freq = i + 2
            r += radius * bump_amplitudes[i] * math.sin(freq * angle + bump_phases[i])
        return max(radius * 0.4, r)

    max_r = int(radius * 1.5)
    for dy in range(-max_r, max_r + 1):
        for dx in range(-max_r, max_r + 1):
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 0.1:
                dist = 0.1
            angle = math.atan2(dy, dx)
            local_radius = get_radius_at_angle(angle)

            if dist <= local_radius * 0.5:
                zone.set_ground(cx + dx, cy + dy, "water_deep")
            elif dist <= local_radius:
                zone.set_ground(cx + dx, cy + dy, "water_shallow")


def place_ore_veins(zone, ore_id, count, min_y, max_y):
    """Place ore blocks in small vein clusters."""
    for _ in range(count):
        vx = random.randint(15, ZONE_SIZE - 15)
        vy = random.randint(min_y, max_y - 1)

        vein_size = random.randint(4, 9)
        for _ in range(vein_size):
            ox = vx + random.randint(-3, 3)
            oy = vy + random.randint(-3, 3)
            if 0 <= ox < ZONE_SIZE and min_y <= oy < max_y:
                zone.remove_occupant(ox, oy)
                zone.place_occupant(ox, oy, ore_id)


def expose_ore_in_tunnels(zone, tunnel_x, tunnel_length):
    """Place visible ore deposits along tunnel walls."""
    # Main tunnel walls
    for y in range(20, tunnel_length + 50):
        # Check both sides of tunnel
        for side_offset in [-5, -4, 4, 5]:
            x = tunnel_x + side_offset
            if 0 <= x < ZONE_SIZE and 0 <= y < ZONE_SIZE:
                if zone.is_blocked(x, y) and random.random() < 0.08:
                    zone.remove_occupant(x, y)
                    ore = random.choices(
                        ["ore_coal_block", "ore_copper_block", "ore_iron_block"],
                        weights=[5, 4, 2]
                    )[0]
                    zone.place_occupant(x, y, ore)


def place_cavern_objects(zone, cx, cy, radius, has_crystals):
    """Place objects inside a carved cavern."""
    # Mushrooms
    for _ in range(random.randint(5, 12)):
        angle = random.random() * 2 * math.pi
        dist = random.random() * (radius - 2)
        ox = int(cx + dist * math.cos(angle))
        oy = int(cy + dist * math.sin(angle))
        if not zone.is_blocked(ox, oy):
            mtype = "mushroom_glow" if random.random() < 0.4 else "mushroom_red"
            zone.place_occupant(ox, oy, mtype)

    # Stone blocks around edges (cavern walls)
    for _ in range(random.randint(4, 8)):
        angle = random.random() * 2 * math.pi
        dist = radius * random.uniform(0.6, 0.95)
        ox = int(cx + dist * math.cos(angle))
        oy = int(cy + dist * math.sin(angle))
        if not zone.is_blocked(ox, oy):
            zone.place_occupant(ox, oy, "stone_block")

    if has_crystals:
        # Crystal clusters
        for _ in range(random.randint(3, 7)):
            angle = random.random() * 2 * math.pi
            dist = random.random() * (radius - 3)
            ox = int(cx + dist * math.cos(angle))
            oy = int(cy + dist * math.sin(angle))
            if not zone.is_blocked(ox, oy):
                ctype = "crystal_large" if random.random() < 0.3 else "crystal_small"
                zone.place_occupant(ox, oy, ctype)

    # Bone piles (rare)
    if random.random() < 0.4:
        for _ in range(random.randint(1, 3)):
            angle = random.random() * 2 * math.pi
            dist = random.random() * (radius - 2)
            ox = int(cx + dist * math.cos(angle))
            oy = int(cy + dist * math.sin(angle))
            if not zone.is_blocked(ox, oy):
                zone.place_occupant(ox, oy, "bone_pile")


if __name__ == "__main__":
    main()
