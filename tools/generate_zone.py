#!/usr/bin/env python3
"""Zone generation library for Bug Farmer.

Provides building blocks for procedurally generating game zones.
Zones are 16x16 chunks, each chunk is 32x32 cells (512x512 cells total).

Usage:
    from generate_zone import ZoneBuilder

    zone = ZoneBuilder("village_21", row=2, col=1, seed=12345)
    zone.fill_ground("grass")
    zone.rect_ground(100, 100, 50, 50, "stone_path")
    zone.place_occupant(128, 128, "tree_oak")
    zone.scatter("bush", count=50, min_spacing=5)
    zone.export("nakama/data/zones/village_21")
"""

import json
import math
import os
import random
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple, Set, Any

# Constants matching server zone.go
CHUNK_SIZE = 32  # 32x32 cells per chunk
ZONE_CHUNKS = 8   # 8x8 chunks per zone
ZONE_SIZE = CHUNK_SIZE * ZONE_CHUNKS  # 256x256 cells per zone

# Occupant footprints from item_database.md
# Format: (width, height) in cells
FOOTPRINTS = {
    # Natural objects
    "tree_oak": (2, 2),
    "tree_pine": (2, 2),
    "tree_dead": (1, 1),
    "tree_palm": (2, 2),
    "tree_fruit": (2, 2),
    "bush": (1, 1),
    "tall_grass": (1, 1),
    "rock_small": (1, 1),
    "rock_large": (2, 2),
    "reeds": (1, 1),
    "mushroom_red": (1, 1),
    "mushroom_glow": (1, 1),
    "flower_wild": (1, 1),
    "flower_red": (1, 1),
    "flower_blue": (1, 1),
    "flower_yellow": (1, 1),
    "sunflower": (1, 1),
    "crystal_small": (1, 1),
    "crystal_large": (2, 2),
    "stalagmite": (1, 1),
    "bone_pile": (1, 1),
    "ant_mound": (2, 2),

    # Blocks (1x1)
    "dirt_block": (1, 1),
    "stone_block": (1, 1),
    "clay_block": (1, 1),
    "ore_coal_block": (1, 1),
    "ore_copper_block": (1, 1),
    "ore_iron_block": (1, 1),
    "ore_silver_block": (1, 1),
    "ore_gold_block": (1, 1),
    "ore_platinum_block": (1, 1),
    "ore_diamond_block": (1, 1),

    # Fences/Walls
    "fence_wood": (1, 1),
    "fence_stone": (1, 1),
    "fence_iron": (1, 1),
    "fence_electric": (1, 1),
    "fence_corner_wood": (1, 1),
    "gate_wood": (1, 1),
    "gate_iron": (1, 1),
    "wall_wood": (1, 1),
    "wall_stone": (1, 1),
    "wall_brick": (1, 1),

    # Doors
    "door_wood": (1, 2),
    "door_iron": (1, 2),

    # Crafting stations
    "workbench": (2, 1),
    "furnace": (2, 2),
    "anvil": (2, 1),
    "forge": (2, 2),
    "loom": (2, 2),
    "cooking_pot": (2, 1),
    "cauldron": (2, 2),
    "sawmill": (3, 2),
    "stonecutter": (2, 2),

    # Furniture - Tables
    "table_wood": (2, 2),
    "table_stone": (2, 2),

    # Furniture - Seating
    "chair_wood": (1, 1),
    "chair_fancy": (1, 1),

    # Furniture - Beds
    "bed_basic": (2, 4),
    "bed_fancy": (2, 4),

    # Furniture - Storage
    "chest_wood": (2, 1),
    "chest_iron": (2, 1),
    "chest_large": (2, 2),
    "barrel": (1, 1),
    "crate": (1, 1),
    "bookshelf": (1, 2),
    "shelf": (2, 1),

    # Furniture - Lighting
    "lamp_table": (1, 1),
    "lamp_floor": (1, 1),
    "torch_wall": (1, 1),
    "chandelier": (2, 2),
    "fireplace": (2, 2),

    # Furniture - Decorative
    "rug_small": (2, 2),
    "rug_large": (3, 3),
    "painting_small": (1, 1),
    "painting_large": (2, 1),
    "statue_stone": (1, 1),
    "potted_plant": (1, 1),
    "banner": (1, 1),
    "clock": (1, 1),
    "mirror": (1, 2),

    # Beekeeping
    "beehive_basic": (1, 1),
    "beehive_medium": (2, 1),
    "beehive_large": (2, 2),
    "beehive_deluxe": (2, 2),
    "honey_extractor": (2, 2),

    # Structures
    "signpost": (1, 1),
    "well": (2, 2),
    "bridge_wood": (2, 2),
    "bridge_stone": (2, 2),

    # Village props (natural)
    "stump": (1, 1),
    "log_pile": (2, 1),
    "compost_pile": (2, 2),
    "apple_crate": (1, 1),
    "broken_net": (2, 1),
    "notice_board": (1, 2),

    # Village props (placeable)
    "bench": (2, 1),
    "planter_box": (2, 1),
    "chopping_block": (1, 1),
    "sawhorse": (2, 1),
    "ladder": (1, 1),
    "net_post": (1, 1),
    "bait_basket": (1, 1),
    "collection_tray": (2, 1),
}

# Valid ground tiles
GROUND_TILES = {
    "grass", "dirt", "stone_path", "water_shallow", "water_deep",
    "cave_floor", "mud", "sand", "wood_floor", "stone_floor", "garden_plot"
}


@dataclass
class PlacedOccupant:
    """An occupant placed in the zone."""
    id: str
    gx: int  # Global X (cell coordinate)
    gy: int  # Global Y (cell coordinate)
    dir: int = 0  # Direction: 0=down, 1=left, 2=right, 3=up

    def footprint(self) -> Tuple[int, int]:
        """Get (width, height) for this occupant, accounting for rotation."""
        w, h = FOOTPRINTS.get(self.id, (1, 1))
        # Swap W/H for 90-degree rotations (left/right)
        if self.dir in (1, 2):
            return (h, w)
        return (w, h)

    def blocked_cells(self) -> List[Tuple[int, int]]:
        """Get all cells blocked by this occupant."""
        w, h = self.footprint()
        cells = []
        for dy in range(h):
            for dx in range(w):
                cells.append((self.gx + dx, self.gy + dy))
        return cells


class ZoneBuilder:
    """Builder for creating game zones.

    Zones are 512x512 cells (16x16 chunks of 32x32 cells each).
    Two layers: ground (terrain tiles) and occupants (objects on top).
    """

    def __init__(self, zone_id: str, row: int = 0, col: int = 0,
                 name: str = None, biome: str = "meadow", seed: int = None):
        """Initialize a zone builder.

        Args:
            zone_id: Unique identifier for the zone
            row: Zone grid row position
            col: Zone grid column position
            name: Display name (defaults to zone_id titlecased)
            biome: Biome type for theming
            seed: Random seed for reproducibility (required for scatter operations)
        """
        self.zone_id = zone_id
        self.row = row
        self.col = col
        self.name = name or zone_id.replace("_", " ").title()
        self.biome = biome
        self.seed = seed
        self.spawn_point = (ZONE_SIZE // 2, ZONE_SIZE // 2)

        # Ground layer: 512x512 grid of tile IDs
        self.ground: List[List[str]] = [
            ["grass" for _ in range(ZONE_SIZE)]
            for _ in range(ZONE_SIZE)
        ]

        # Occupants: tracked by anchor position
        self.occupants: Dict[Tuple[int, int], PlacedOccupant] = {}

        # Blocked cells (for collision detection during placement)
        self._blocked: Set[Tuple[int, int]] = set()

        # Track which occupant owns each blocked cell (for footprint output)
        self._cell_to_occupant: Dict[Tuple[int, int], PlacedOccupant] = {}

        # Bug spawning configuration (optional)
        self.bug_spawning: Optional[Dict] = None
        self._meadows: List[Dict] = []  # Track meadows for auto-spawn-area generation

        # Initialize random with seed if provided
        if seed is not None:
            random.seed(seed)

    def reseed(self, seed: int):
        """Reset the random seed (for deterministic generation)."""
        self.seed = seed
        random.seed(seed)

    def set_spawn(self, gx: int, gy: int):
        """Set the player spawn point."""
        self.spawn_point = (gx, gy)

    # =========================================================================
    # GROUND LAYER OPERATIONS
    # =========================================================================

    def fill_ground(self, tile_id: str):
        """Fill the entire zone with a ground tile."""
        if tile_id not in GROUND_TILES:
            print(f"Warning: Unknown tile '{tile_id}'")
        for y in range(ZONE_SIZE):
            for x in range(ZONE_SIZE):
                self.ground[y][x] = tile_id

    def set_ground(self, gx: int, gy: int, tile_id: str):
        """Set a single ground tile."""
        if 0 <= gx < ZONE_SIZE and 0 <= gy < ZONE_SIZE:
            self.ground[gy][gx] = tile_id

    def get_ground(self, gx: int, gy: int) -> str:
        """Get the ground tile at a position."""
        if 0 <= gx < ZONE_SIZE and 0 <= gy < ZONE_SIZE:
            return self.ground[gy][gx]
        return ""

    def rect_ground(self, gx: int, gy: int, width: int, height: int, tile_id: str):
        """Fill a rectangular region with a ground tile."""
        for dy in range(height):
            for dx in range(width):
                self.set_ground(gx + dx, gy + dy, tile_id)

    def circle_ground(self, cx: int, cy: int, radius: int, tile_id: str):
        """Fill a circular region with a ground tile."""
        r2 = radius * radius
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx*dx + dy*dy <= r2:
                    self.set_ground(cx + dx, cy + dy, tile_id)

    def path_ground(self, points: List[Tuple[int, int]], tile_id: str, width: int = 1):
        """Draw a path through a series of points."""
        if len(points) < 2:
            return

        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            self._line_ground(x1, y1, x2, y2, tile_id, width)

    def _line_ground(self, x1: int, y1: int, x2: int, y2: int,
                     tile_id: str, width: int):
        """Draw a line of ground tiles (Bresenham's algorithm with width)."""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        x, y = x1, y1
        half_w = width // 2

        while True:
            # Draw a square of tiles centered on the line
            for wx in range(-half_w, half_w + 1):
                for wy in range(-half_w, half_w + 1):
                    self.set_ground(x + wx, y + wy, tile_id)

            if x == x2 and y == y2:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def noise_ground(self, tile_id: str, probability: float = 0.1,
                     region: Tuple[int, int, int, int] = None):
        """Randomly scatter a ground tile with given probability.

        Requires seed to be set for reproducibility.
        """
        if region:
            gx, gy, w, h = region
        else:
            gx, gy, w, h = 0, 0, ZONE_SIZE, ZONE_SIZE

        for dy in range(h):
            for dx in range(w):
                if random.random() < probability:
                    self.set_ground(gx + dx, gy + dy, tile_id)

    # =========================================================================
    # OCCUPANT OPERATIONS
    # =========================================================================

    def get_footprint(self, occupant_id: str, dir: int = 0) -> Tuple[int, int]:
        """Get the footprint (width, height) for an occupant type."""
        w, h = FOOTPRINTS.get(occupant_id, (1, 1))
        if dir in (1, 2):
            return (h, w)
        return (w, h)

    def can_place(self, gx: int, gy: int, occupant_id: str, dir: int = 0) -> bool:
        """Check if an occupant can be placed at the given position."""
        w, h = self.get_footprint(occupant_id, dir)

        # Check bounds
        if gx < 0 or gy < 0 or gx + w > ZONE_SIZE or gy + h > ZONE_SIZE:
            return False

        # Check all cells are free
        for dy in range(h):
            for dx in range(w):
                if (gx + dx, gy + dy) in self._blocked:
                    return False

        # Check chunk boundary constraint for multi-cell occupants
        if w > 1 or h > 1:
            chunk_x = gx // CHUNK_SIZE
            chunk_y = gy // CHUNK_SIZE
            end_chunk_x = (gx + w - 1) // CHUNK_SIZE
            end_chunk_y = (gy + h - 1) // CHUNK_SIZE
            if chunk_x != end_chunk_x or chunk_y != end_chunk_y:
                return False

        return True

    def place_occupant(self, gx: int, gy: int, occupant_id: str, dir: int = 0) -> bool:
        """Place an occupant at the given position.

        Returns True if placed successfully, False if blocked.
        """
        if occupant_id not in FOOTPRINTS:
            print(f"Warning: Unknown occupant '{occupant_id}', using 1x1 footprint")

        if not self.can_place(gx, gy, occupant_id, dir):
            return False

        occ = PlacedOccupant(id=occupant_id, gx=gx, gy=gy, dir=dir)
        self.occupants[(gx, gy)] = occ

        # Mark all cells as blocked and track which occupant owns them
        for cell in occ.blocked_cells():
            self._blocked.add(cell)
            self._cell_to_occupant[cell] = occ

        return True

    def remove_occupant(self, gx: int, gy: int) -> bool:
        """Remove an occupant at the given anchor position."""
        if (gx, gy) not in self.occupants:
            return False

        occ = self.occupants.pop((gx, gy))
        for cell in occ.blocked_cells():
            self._blocked.discard(cell)
            self._cell_to_occupant.pop(cell, None)
        return True

    def is_blocked(self, gx: int, gy: int) -> bool:
        """Check if a cell is blocked by an occupant."""
        return (gx, gy) in self._blocked

    def scatter(self, occupant_id: str, count: int,
                region: Tuple[int, int, int, int] = None,
                min_spacing: int = 2,
                avoid_tiles: Set[str] = None,
                require_tiles: Set[str] = None,
                dir: int = 0,
                random_dir: bool = False) -> int:
        """Randomly scatter occupants in a region.

        Args:
            occupant_id: The occupant type to place
            count: Target number to place
            region: (gx, gy, width, height) or None for entire zone
            min_spacing: Minimum cells between occupant anchors
            avoid_tiles: Ground tiles to avoid placing on
            require_tiles: Only place on these ground tiles (if set)
            dir: Direction for all placed occupants
            random_dir: If True, randomize direction (0-3)

        Returns:
            Number actually placed
        """
        if region:
            rx, ry, rw, rh = region
        else:
            rx, ry, rw, rh = 0, 0, ZONE_SIZE, ZONE_SIZE

        avoid_tiles = avoid_tiles or {"water_shallow", "water_deep"}
        w, h = self.get_footprint(occupant_id, dir)

        placed = 0
        attempts = 0
        max_attempts = count * 50  # More attempts for dense placement

        while placed < count and attempts < max_attempts:
            attempts += 1

            # Random position within region
            gx = random.randint(rx, max(rx, rx + rw - w))
            gy = random.randint(ry, max(ry, ry + rh - h))

            # Check ground tile
            tile = self.get_ground(gx, gy)
            if tile in avoid_tiles:
                continue
            if require_tiles and tile not in require_tiles:
                continue

            # Check spacing from other occupants
            too_close = False
            for (ox, oy) in self.occupants.keys():
                dist = abs(gx - ox) + abs(gy - oy)  # Manhattan distance
                if dist < min_spacing:
                    too_close = True
                    break

            if too_close:
                continue

            # Determine direction
            d = random.randint(0, 3) if random_dir else dir

            if self.place_occupant(gx, gy, occupant_id, d):
                placed += 1

        return placed

    def scatter_weighted(self, occupants: List[Tuple[str, float]], total_count: int,
                         **kwargs) -> Dict[str, int]:
        """Scatter multiple occupant types with weighted probabilities.

        Args:
            occupants: List of (occupant_id, weight) tuples
            total_count: Total number to place
            **kwargs: Passed to scatter()

        Returns:
            Dict of occupant_id -> count placed
        """
        total_weight = sum(w for _, w in occupants)
        results = {}

        for occ_id, weight in occupants:
            count = int(total_count * weight / total_weight)
            results[occ_id] = self.scatter(occ_id, count, **kwargs)

        return results

    def place_line(self, x1: int, y1: int, x2: int, y2: int,
                   occupant_id: str, dir: int = 0, spacing: int = 1) -> int:
        """Place occupants in a line (for fences, walls).

        Args:
            x1, y1: Start position
            x2, y2: End position
            occupant_id: Occupant type to place
            dir: Direction for occupants
            spacing: Cells between each occupant (1 = adjacent)

        Returns:
            Number placed
        """
        placed = 0
        dx = 0 if x1 == x2 else (1 if x2 > x1 else -1)
        dy = 0 if y1 == y2 else (1 if y2 > y1 else -1)

        x, y = x1, y1
        step = 0
        while True:
            if step % spacing == 0:
                if self.place_occupant(x, y, occupant_id, dir):
                    placed += 1

            if x == x2 and y == y2:
                break
            x += dx
            y += dy
            step += 1

        return placed

    def place_rect_border(self, gx: int, gy: int, width: int, height: int,
                          occupant_id: str, skip_corners: bool = False) -> int:
        """Place occupants around a rectangle border (for fences, walls).

        Args:
            gx, gy: Bottom-left corner
            width, height: Rectangle dimensions
            occupant_id: Occupant type for edges
            skip_corners: If True, leave corners empty (for corner posts)

        Returns:
            Number placed
        """
        placed = 0

        # Bottom edge
        for x in range(gx + (1 if skip_corners else 0),
                       gx + width - (1 if skip_corners else 0)):
            if self.place_occupant(x, gy, occupant_id):
                placed += 1

        # Top edge
        for x in range(gx + (1 if skip_corners else 0),
                       gx + width - (1 if skip_corners else 0)):
            if self.place_occupant(x, gy + height - 1, occupant_id):
                placed += 1

        # Left edge (excluding corners already handled)
        for y in range(gy + 1, gy + height - 1):
            if self.place_occupant(gx, y, occupant_id):
                placed += 1

        # Right edge (excluding corners already handled)
        for y in range(gy + 1, gy + height - 1):
            if self.place_occupant(gx + width - 1, y, occupant_id):
                placed += 1

        return placed

    def clear_region(self, gx: int, gy: int, width: int, height: int):
        """Remove all occupants in a rectangular region."""
        to_remove = []
        for (ox, oy), occ in self.occupants.items():
            for (cx, cy) in occ.blocked_cells():
                if gx <= cx < gx + width and gy <= cy < gy + height:
                    to_remove.append((ox, oy))
                    break

        for pos in to_remove:
            self.remove_occupant(*pos)

    def clear_circle(self, cx: int, cy: int, radius: int):
        """Remove all occupants in a circular region."""
        r2 = radius * radius
        to_remove = []
        for (ox, oy), occ in self.occupants.items():
            for (px, py) in occ.blocked_cells():
                dx, dy = px - cx, py - cy
                if dx*dx + dy*dy <= r2:
                    to_remove.append((ox, oy))
                    break

        for pos in to_remove:
            self.remove_occupant(*pos)

    # =========================================================================
    # NATURAL FEATURES
    # =========================================================================

    def scatter_grove(self, cx: int, cy: int, radius: int,
                      tree_types: List[Tuple[str, float]],
                      tree_count: int,
                      understory: List[Tuple[str, float]] = None,
                      understory_count: int = 0) -> Dict[str, int]:
        """Create a natural tree grove with understory plants.

        Args:
            cx, cy: Center of the grove
            radius: Approximate radius of the grove
            tree_types: List of (tree_id, weight) tuples
            tree_count: Target number of trees
            understory: List of (plant_id, weight) for bushes/flowers under trees
            understory_count: Target number of understory plants

        Returns:
            Dict of occupant_id -> count placed
        """
        results = {}
        total_weight = sum(w for _, w in tree_types)

        # Place trees in circular region - tighter spacing for dense groves
        for tree_id, weight in tree_types:
            count = int(tree_count * weight / total_weight)
            placed = self.scatter(
                tree_id, count,
                region=(cx - radius, cy - radius, radius * 2, radius * 2),
                min_spacing=3  # Tighter packing for visible groves
            )
            results[tree_id] = placed

        # Add understory plants between trees
        if understory and understory_count > 0:
            total_u_weight = sum(w for _, w in understory)
            for plant_id, weight in understory:
                count = int(understory_count * weight / total_u_weight)
                placed = self.scatter(
                    plant_id, count,
                    region=(cx - radius, cy - radius, radius * 2, radius * 2),
                    min_spacing=2
                )
                results[plant_id] = placed

        return results

    def scatter_meadow(self, cx: int, cy: int, radius: int,
                       flower_types: List[Tuple[str, float]],
                       density: float = 0.15) -> Dict[str, int]:
        """Create a dense flower meadow in a CIRCULAR area with organic edges.

        Uses distance-based placement for natural circular shape instead of square.

        Args:
            cx, cy: Center of the meadow
            radius: Radius of the meadow
            flower_types: List of (flower_id, weight) tuples
            density: Approximate fill ratio (0.0-1.0)

        Returns:
            Dict of flower_id -> count placed
        """
        # Track meadow for auto-spawn-area generation
        self._meadows.append({"cx": cx, "cy": cy, "radius": radius})

        results = {}
        area = 3.14159 * radius * radius
        total_count = int(area * density)
        total_weight = sum(w for _, w in flower_types)

        for flower_id, weight in flower_types:
            target = int(total_count * weight / total_weight)
            placed = 0

            # Place flowers using polar coordinates for circular shape
            attempts = 0
            max_attempts = target * 30

            while placed < target and attempts < max_attempts:
                attempts += 1

                # Random point in circle using rejection sampling
                angle = random.random() * 2 * math.pi
                # Use sqrt for uniform distribution in circle
                dist = math.sqrt(random.random()) * radius

                # Add some noise to edge for organic feel
                edge_noise = random.gauss(0, radius * 0.1)
                dist = min(radius, max(0, dist + edge_noise * (dist / radius)))

                gx = int(cx + dist * math.cos(angle))
                gy = int(cy + dist * math.sin(angle))

                # Check bounds and placement
                if 0 <= gx < ZONE_SIZE and 0 <= gy < ZONE_SIZE:
                    if self.place_occupant(gx, gy, flower_id):
                        placed += 1

            results[flower_id] = placed

        return results

    def create_pond(self, cx: int, cy: int, radius: int,
                    with_reeds: bool = True,
                    reed_count: int = 12) -> int:
        """Create a natural pond with ORGANIC irregular shape.

        Uses noise-based edge distortion for natural-looking shorelines.

        Args:
            cx, cy: Center of the pond
            radius: Approximate radius
            with_reeds: Whether to add reeds around edges
            reed_count: Number of reeds to scatter

        Returns:
            Number of reeds placed
        """
        # Generate noise-based radius variation for organic shape
        # Use multiple frequency "bumps" around the edge
        num_bumps = random.randint(4, 7)
        bump_phases = [random.random() * 2 * math.pi for _ in range(num_bumps)]
        bump_amplitudes = [random.uniform(0.15, 0.3) for _ in range(num_bumps)]

        def get_radius_at_angle(angle):
            """Get the pond radius at a given angle (organic variation)."""
            r = radius
            for i in range(num_bumps):
                # Add harmonic variations
                freq = i + 2  # frequencies 2, 3, 4, ...
                r += radius * bump_amplitudes[i] * math.sin(freq * angle + bump_phases[i])
            return max(radius * 0.5, min(radius * 1.4, r))  # Clamp

        # Paint the pond using the organic shape
        max_r = int(radius * 1.5)
        for dy in range(-max_r, max_r + 1):
            for dx in range(-max_r, max_r + 1):
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < 0.1:
                    dist = 0.1
                angle = math.atan2(dy, dx)

                local_radius = get_radius_at_angle(angle)
                inner_radius = local_radius * 0.6

                if dist <= inner_radius:
                    self.set_ground(cx + dx, cy + dy, "water_deep")
                elif dist <= local_radius:
                    self.set_ground(cx + dx, cy + dy, "water_shallow")
                elif dist <= local_radius + 2:
                    # Mud bank with random gaps
                    if self.get_ground(cx + dx, cy + dy) == "grass":
                        if random.random() < 0.65:
                            self.set_ground(cx + dx, cy + dy, "mud")

        # Add reeds around the edge (following organic shape)
        reeds_placed = 0
        if with_reeds:
            for _ in range(reed_count * 3):  # Extra attempts for organic placement
                angle = random.random() * 2 * math.pi
                local_r = get_radius_at_angle(angle)
                # Place reeds just outside water
                dist = local_r + random.uniform(0.5, 2.5)
                gx = int(cx + dist * math.cos(angle))
                gy = int(cy + dist * math.sin(angle))

                tile = self.get_ground(gx, gy)
                if tile in {"mud", "grass"}:
                    if self.place_occupant(gx, gy, "reeds"):
                        reeds_placed += 1
                        if reeds_placed >= reed_count:
                            break

        return reeds_placed

    def scatter_rock_patch(self, cx: int, cy: int, radius: int,
                           rock_types: List[Tuple[str, float]] = None,
                           total_count: int = 10) -> Dict[str, int]:
        """Create a patch of rocks and ore deposits - DENSE center, sparse edges.

        Args:
            cx, cy: Center of the patch
            radius: Approximate radius
            rock_types: List of (block_id, weight) - defaults to common rocks/ores
            total_count: Target number of blocks

        Returns:
            Dict of block_id -> count placed
        """
        if rock_types is None:
            rock_types = [
                ("rock_small", 4.0),
                ("rock_large", 2.0),
                ("stone_block", 2.0),
                ("ore_coal_block", 1.0),
                ("ore_copper_block", 0.5),
            ]

        results = {}
        total_weight = sum(w for _, w in rock_types)

        # Create DENSE core (inner 60% of radius) with tight spacing
        inner_radius = int(radius * 0.6)
        core_count = int(total_count * 0.7)  # 70% of rocks in core

        for rock_id, weight in rock_types:
            count = max(1, int(core_count * weight / total_weight))
            placed = self.scatter(
                rock_id, count,
                region=(cx - inner_radius, cy - inner_radius,
                        inner_radius * 2, inner_radius * 2),
                min_spacing=1  # Very tight packing in core
            )
            results[rock_id] = placed

        # Add sparse outer ring
        outer_count = total_count - core_count
        for rock_id, weight in rock_types:
            count = max(1, int(outer_count * weight / total_weight))
            # Only place in outer ring area
            for _ in range(count * 10):  # More attempts for ring placement
                angle = random.random() * 6.28318
                dist = inner_radius + random.random() * (radius - inner_radius)
                gx = int(cx + dist * math.cos(angle))
                gy = int(cy + dist * math.sin(angle))
                if self.place_occupant(gx, gy, rock_id):
                    results[rock_id] = results.get(rock_id, 0) + 1
                    if results.get(rock_id, 0) >= count:
                        break

        return results

    # =========================================================================
    # BUG SPAWNING
    # =========================================================================

    def set_bug_spawning(self, species_caps: Dict[str, Dict], spawn_areas: List[Dict] = None):
        """Configure bug spawning for this zone.

        Args:
            species_caps: Dict of species_id -> {initial, max, spawn_interval}
                Example: {"fly_common": {"initial": 5, "max": 15, "spawn_interval": 45.0}}
            spawn_areas: Optional list of spawn areas. Can also use add_spawn_area().
        """
        self.bug_spawning = {
            "species_caps": species_caps,
            "spawn_areas": spawn_areas or []
        }

    def add_spawn_area(self, id: str, species: List[str], area_type: str, **kwargs):
        """Add a bug spawn area.

        Args:
            id: Unique identifier for the spawn area
            species: List of species that can spawn here
            area_type: "zone" (anywhere in zone) or "circle"
            **kwargs: For circle type: cx, cy, radius
        """
        if self.bug_spawning is None:
            self.bug_spawning = {"species_caps": {}, "spawn_areas": []}

        area = {"id": id, "species": species, "type": area_type}
        area.update(kwargs)
        self.bug_spawning["spawn_areas"].append(area)

    def auto_spawn_areas_from_meadows(self, species: str = "butterfly_meadow"):
        """Generate spawn areas from all tracked meadows.

        Call this after creating meadows with scatter_meadow() to automatically
        create butterfly spawn circles matching the meadow locations.

        Args:
            species: Species ID to assign to meadow spawn areas
        """
        for i, meadow in enumerate(self._meadows):
            self.add_spawn_area(
                id=f"meadow_{i}",
                species=[species],
                area_type="circle",
                cx=meadow["cx"],
                cy=meadow["cy"],
                radius=meadow["radius"]
            )

    # =========================================================================
    # BUILDING TEMPLATES
    # =========================================================================

    def place_building(self, gx: int, gy: int, template: Dict[str, Any]) -> bool:
        """Place a building from a template.

        Template format:
        {
            "width": 8,
            "height": 8,
            "floor": "wood_floor",
            "wall": "wall_wood",  # Optional: places walls around border
            "occupants": [
                {"id": "door_wood", "x": 3, "y": 0, "dir": 0},
                {"id": "bed_basic", "x": 1, "y": 4, "dir": 0},
            ]
        }
        """
        w = template.get("width", 8)
        h = template.get("height", 8)

        # Check if building fits
        if gx + w > ZONE_SIZE or gy + h > ZONE_SIZE:
            return False

        # Clear the region first
        self.clear_region(gx, gy, w, h)

        # Place floor
        floor_tile = template.get("floor", "wood_floor")
        self.rect_ground(gx, gy, w, h, floor_tile)

        # Place walls if specified
        if "wall" in template:
            wall_id = template["wall"]
            self.place_rect_border(gx, gy, w, h, wall_id)

        # Place occupants
        for occ_data in template.get("occupants", []):
            ox = gx + occ_data["x"]
            oy = gy + occ_data["y"]
            self.place_occupant(ox, oy, occ_data["id"], occ_data.get("dir", 0))

        return True

    # =========================================================================
    # VALIDATION
    # =========================================================================

    def validate(self) -> List[str]:
        """Validate the zone for common issues.

        Returns:
            List of warning/error messages (empty if valid)
        """
        issues = []

        # Check spawn point is accessible
        sx, sy = self.spawn_point
        if self.is_blocked(sx, sy):
            issues.append(f"Spawn point ({sx}, {sy}) is blocked by an occupant")

        tile = self.get_ground(sx, sy)
        if tile in {"water_deep"}:
            issues.append(f"Spawn point ({sx}, {sy}) is on impassable tile '{tile}'")

        # Check for unknown tiles
        unknown_tiles = set()
        for row in self.ground:
            for tile in row:
                if tile not in GROUND_TILES:
                    unknown_tiles.add(tile)
        if unknown_tiles:
            issues.append(f"Unknown ground tiles: {unknown_tiles}")

        # Check for unknown occupants
        unknown_occs = set()
        for occ in self.occupants.values():
            if occ.id not in FOOTPRINTS:
                unknown_occs.add(occ.id)
        if unknown_occs:
            issues.append(f"Unknown occupants (using 1x1 footprint): {unknown_occs}")

        return issues

    # =========================================================================
    # EXPORT
    # =========================================================================

    def export(self, output_dir: str, validate: bool = True):
        """Export the zone to JSON files.

        Creates:
            output_dir/zone.json
            output_dir/chunk_0_0.json ... chunk_15_15.json
        """
        if validate:
            issues = self.validate()
            for issue in issues:
                print(f"Warning: {issue}")

        os.makedirs(output_dir, exist_ok=True)

        # Export zone config
        zone_config = {
            "zone_id": self.zone_id,
            "name": self.name,
            "row": self.row,
            "col": self.col,
            "width": ZONE_SIZE,
            "height": ZONE_SIZE,
            "spawn_point": list(self.spawn_point),
            "biome_type": self.biome
        }

        # Include bug spawning config if set
        if self.bug_spawning:
            zone_config["bug_spawning"] = self.bug_spawning

        with open(os.path.join(output_dir, "zone.json"), "w") as f:
            json.dump(zone_config, f, indent=2)

        # Export chunks
        for cy in range(ZONE_CHUNKS):
            for cx in range(ZONE_CHUNKS):
                chunk = self._build_chunk(cx, cy)
                filename = f"chunk_{cx}_{cy}.json"
                with open(os.path.join(output_dir, filename), "w") as f:
                    json.dump(chunk, f, separators=(',', ':'))

        print(f"Exported zone '{self.zone_id}' to {output_dir}")
        print(f"  - {ZONE_CHUNKS * ZONE_CHUNKS} chunks")
        print(f"  - {len(self.occupants)} occupants")

    def _build_chunk(self, cx: int, cy: int) -> Dict:
        """Build chunk data for export."""
        base_x = cx * CHUNK_SIZE
        base_y = cy * CHUNK_SIZE

        # Ground layer
        ground = []
        for ly in range(CHUNK_SIZE):
            row = []
            for lx in range(CHUNK_SIZE):
                gx, gy = base_x + lx, base_y + ly
                row.append(self.ground[gy][gx])
            ground.append(row)

        # Occupants layer
        occupants = []
        for ly in range(CHUNK_SIZE):
            row = []
            for lx in range(CHUNK_SIZE):
                gx, gy = base_x + lx, base_y + ly

                if (gx, gy) in self.occupants:
                    # Anchor cell - include anchor:true
                    occ = self.occupants[(gx, gy)]
                    row.append({"id": occ.id, "dir": occ.dir, "anchor": True})
                elif (gx, gy) in self._blocked:
                    # Footprint cell - include occupant data (no anchor = false)
                    occ = self._cell_to_occupant.get((gx, gy))
                    if occ:
                        row.append({"id": occ.id, "dir": occ.dir})
                    else:
                        row.append(None)
                else:
                    # Empty
                    row.append(None)
            occupants.append(row)

        return {
            "chunk_x": cx,
            "chunk_y": cy,
            "ground": ground,
            "occupants": occupants
        }

    def stats(self) -> Dict[str, Any]:
        """Get statistics about the zone."""
        tile_counts = {}
        for row in self.ground:
            for tile in row:
                tile_counts[tile] = tile_counts.get(tile, 0) + 1

        occ_counts = {}
        for occ in self.occupants.values():
            occ_counts[occ.id] = occ_counts.get(occ.id, 0) + 1

        return {
            "zone_id": self.zone_id,
            "seed": self.seed,
            "total_cells": ZONE_SIZE * ZONE_SIZE,
            "tile_counts": tile_counts,
            "occupant_counts": occ_counts,
            "total_occupants": len(self.occupants),
            "blocked_cells": len(self._blocked)
        }


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_zone_manifest(zones: List[Dict], output_path: str):
    """Create the zone manifest file.

    Args:
        zones: List of zone info dicts with {id, row, col, name}
        output_path: Path to zone_manifest.json
    """
    manifest = {"zones": zones}
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Created zone manifest: {output_path}")


# =============================================================================
# MAIN (Example usage)
# =============================================================================

if __name__ == "__main__":
    # Example: Create a simple test zone
    zone = ZoneBuilder("test_zone", row=0, col=0, biome="meadow", seed=12345)

    # Fill with grass
    zone.fill_ground("grass")

    # Add some paths
    zone.path_ground([(50, 256), (256, 256), (256, 50)], "stone_path", width=3)

    # Add water pond
    zone.circle_ground(400, 400, 15, "water_shallow")
    zone.circle_ground(400, 400, 8, "water_deep")

    # Scatter trees
    zone.scatter("tree_oak", count=30, min_spacing=8)
    zone.scatter("tree_pine", count=20, min_spacing=8)

    # Scatter smaller objects
    zone.scatter("bush", count=50, min_spacing=3)
    zone.scatter("flower_wild", count=100, min_spacing=2)
    zone.scatter("rock_small", count=30, min_spacing=4)

    # Place a workbench at spawn
    zone.set_spawn(256, 256)
    zone.place_occupant(260, 260, "workbench", dir=0)
    zone.place_occupant(265, 260, "chest_wood", dir=0)

    # Validate
    issues = zone.validate()
    if issues:
        print("Validation issues:")
        for issue in issues:
            print(f"  - {issue}")

    # Print stats
    stats = zone.stats()
    print(f"\nZone stats:")
    print(f"  Seed: {stats['seed']}")
    print(f"  Total cells: {stats['total_cells']}")
    print(f"  Total occupants: {stats['total_occupants']}")
    print(f"  Blocked cells: {stats['blocked_cells']}")

    # Export
    zone.export("/mnt/c/Users/emily/BugFarmer/nakama/data/zones/test_zone")
