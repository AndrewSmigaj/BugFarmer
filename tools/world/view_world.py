#!/usr/bin/env python3
"""World visualization tool for Bug Farmer.

Renders the entire world grid as a PNG image for development/debugging.
Shows ground terrain, occupants, roads, buildings, and zone boundaries.

Usage:
    python view_world.py                    # Render all zones
    python view_world.py village_21         # Render single zone detail
    python view_world.py --scale 4          # Change pixels per cell
    python view_world.py --chunks           # Show chunk grid lines
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Error: Pillow is required. Install with: pip install Pillow")
    sys.exit(1)

# Zone grid dimensions
ZONE_SIZE = 512  # Cells per zone side
CHUNK_SIZE = 32  # Cells per chunk side

# Ground tile colors (RGB)
GROUND_COLORS = {
    "grass": (170, 210, 140),        # Lighter green - occupants contrast better
    "dirt": (139, 119, 101),         # Brown
    "stone_path": (169, 169, 169),   # Gray
    "water_shallow": (135, 206, 250), # Light blue
    "water_deep": (65, 105, 225),    # Royal blue
    "mud": (101, 67, 33),            # Dark brown
    "sand": (238, 214, 175),         # Tan
    "wood_floor": (160, 120, 90),    # Light brown
    "stone_floor": (128, 128, 128),  # Medium gray
    "cave_floor": (60, 60, 60),      # Dark gray
    "garden_plot": (89, 60, 31),     # Tilled brown
}
DEFAULT_GROUND_COLOR = (200, 200, 200)  # Light gray for unknown

# Occupant category colors - simplified for clarity
OCCUPANT_CATEGORIES = {
    # Trees (dark green shades)
    "tree_oak": "tree",
    "tree_pine": "tree",
    "tree_dead": "tree",
    "tree_palm": "tree",
    "tree_fruit": "tree",

    # Flowers (pink/colorful)
    "flower_wild": "flower",
    "flower_red": "flower",
    "flower_blue": "flower",
    "flower_yellow": "flower",
    "sunflower": "flower",

    # Plants (light green)
    "bush": "plant",
    "tall_grass": "plant",
    "reeds": "plant",

    # Rocks (gray)
    "rock_small": "rock",
    "rock_large": "rock",
    "crystal_small": "crystal",
    "crystal_large": "crystal",
    "stalagmite": "rock",

    # Mushrooms
    "mushroom_red": "mushroom",
    "mushroom_glow": "mushroom",

    # Cave/underground
    "bone_pile": "cave",
    "ant_mound": "cave",

    # Village props
    "stump": "tree",
    "log_pile": "tree",
    "compost_pile": "plant",
    "apple_crate": "storage",
    "broken_net": "structure",
    "notice_board": "structure",

    # Blocks
    "dirt_block": "block",
    "stone_block": "block",
    "clay_block": "block",
    "ore_coal_block": "ore",
    "ore_copper_block": "ore",
    "ore_iron_block": "ore",
    "ore_silver_block": "ore",
    "ore_gold_block": "ore",
    "ore_platinum_block": "ore",
    "ore_diamond_block": "ore",

    # Structures
    "fence_wood": "fence",
    "fence_stone": "fence",
    "fence_corner_wood": "fence",
    "fence_iron": "fence",
    "gate_wood": "fence",
    "gate_iron": "fence",
    "wall_wood": "wall",
    "wall_stone": "wall",
    "wall_brick": "wall",
    "door_wood": "building",
    "door_iron": "building",
    "signpost": "structure",
    "well": "structure",
    "bridge_wood": "structure",
    "bridge_stone": "structure",

    # Furniture
    "workbench": "furniture",
    "furnace": "furniture",
    "anvil": "furniture",
    "forge": "furniture",
    "table_wood": "furniture",
    "table_stone": "furniture",
    "chair_wood": "furniture",
    "chair_fancy": "furniture",
    "bed_basic": "furniture",
    "bed_fancy": "furniture",
    "chest_wood": "storage",
    "chest_iron": "storage",
    "barrel": "storage",
    "crate": "storage",

    # Beekeeping
    "beehive_basic": "beehive",
    "beehive_medium": "beehive",
    "beehive_large": "beehive",
    "beehive_deluxe": "beehive",
    "honey_extractor": "beehive",
}

CATEGORY_COLORS = {
    "tree": (20, 60, 20),         # Very dark green - stands out from grass
    "flower": (255, 50, 150),     # Bright magenta - very visible
    "plant": (50, 120, 50),       # Medium dark green
    "rock": (80, 80, 90),         # Dark blue-gray
    "crystal": (200, 100, 255),   # Bright purple
    "mushroom": (255, 80, 80),    # Bright red
    "cave": (60, 40, 30),         # Dark brown
    "block": (100, 80, 60),       # Dark tan
    "ore": (255, 200, 50),        # Bright gold
    "fence": (120, 70, 30),       # Dark wood brown
    "wall": (100, 100, 110),      # Dark stone gray
    "building": (180, 140, 100),  # Tan
    "structure": (160, 120, 80),  # Light brown
    "furniture": (140, 80, 40),   # Medium brown
    "storage": (120, 70, 30),     # Dark wood
    "beehive": (255, 220, 50),    # Bright yellow
}
DEFAULT_CATEGORY = "unknown"
DEFAULT_OCCUPANT_COLOR = (255, 0, 255)  # Magenta for unknown

# UI colors
ZONE_BORDER_COLOR = (50, 50, 50)
ZONE_MISSING_COLOR = (30, 30, 30)
CHUNK_GRID_COLOR = (80, 80, 80)
SPAWN_MARKER_COLOR = (255, 255, 0)
LEGEND_BG_COLOR = (20, 20, 20)
TEXT_COLOR = (255, 255, 255)


def get_occupant_color(occ_id: str) -> Tuple[int, int, int]:
    """Get color for an occupant based on its category."""
    category = OCCUPANT_CATEGORIES.get(occ_id, DEFAULT_CATEGORY)
    return CATEGORY_COLORS.get(category, DEFAULT_OCCUPANT_COLOR)


def load_zone_data(zones_dir: Path, zone_id: str) -> Optional[Dict[str, Any]]:
    """Load zone metadata and all chunk data."""
    zone_path = zones_dir / zone_id
    if not zone_path.exists():
        return None

    zone_json_path = zone_path / "zone.json"
    if not zone_json_path.exists():
        return None

    try:
        with open(zone_json_path) as f:
            zone_config = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

    # Load all chunks
    chunks = {}
    for cy in range(16):
        for cx in range(16):
            chunk_path = zone_path / f"chunk_{cx}_{cy}.json"
            if chunk_path.exists():
                try:
                    with open(chunk_path) as f:
                        chunks[(cx, cy)] = json.load(f)
                except (json.JSONDecodeError, IOError):
                    continue

    return {"config": zone_config, "chunks": chunks}


def scan_available_zones(zones_dir: Path) -> Dict[Tuple[int, int], str]:
    """Scan zones directory and map (row, col) to zone_id."""
    available = {}
    if not zones_dir.exists():
        return available

    for zone_folder in zones_dir.iterdir():
        if not zone_folder.is_dir():
            continue
        zone_json = zone_folder / "zone.json"
        if zone_json.exists():
            try:
                with open(zone_json) as f:
                    config = json.load(f)
                    row = config.get("row", -1)
                    col = config.get("col", -1)
                    if row >= 0 and col >= 0:
                        available[(row, col)] = zone_folder.name
            except (json.JSONDecodeError, IOError):
                continue
    return available


def render_zone(zone_data: Dict[str, Any], scale: int = 2,
                show_chunks: bool = False, show_roof: bool = False) -> Image.Image:
    """Render a single zone to an image at the zone's ACTUAL size (not a fixed 512 canvas)."""
    cfg = zone_data.get("config", {})
    zw = int(cfg.get("width", ZONE_SIZE))
    zh = int(cfg.get("height", ZONE_SIZE))
    img_w, img_h = zw * scale, zh * scale
    img = Image.new('RGB', (img_w, img_h), GROUND_COLORS["grass"])
    draw = ImageDraw.Draw(img)

    chunks = zone_data["chunks"]

    # Draw ground layer
    for (cx, cy), chunk in chunks.items():
        base_x = cx * CHUNK_SIZE * scale
        base_y = cy * CHUNK_SIZE * scale
        ground = chunk.get("ground", [])

        for ly, row in enumerate(ground):
            for lx, tile_id in enumerate(row):
                color = GROUND_COLORS.get(tile_id, DEFAULT_GROUND_COLOR)
                px = base_x + lx * scale
                py = base_y + ly * scale
                if scale == 1:
                    img.putpixel((px, py), color)
                else:
                    draw.rectangle([px, py, px + scale - 1, py + scale - 1], fill=color)

    # Draw occupants on top
    for (cx, cy), chunk in chunks.items():
        base_x = cx * CHUNK_SIZE * scale
        base_y = cy * CHUNK_SIZE * scale
        occupants = chunk.get("occupants", [])

        for ly, row in enumerate(occupants):
            for lx, occ in enumerate(row):
                if occ is None or occ == "@":
                    continue

                if isinstance(occ, dict):
                    occ_id = occ.get("id", "")
                else:
                    occ_id = str(occ)

                color = get_occupant_color(occ_id)
                px = base_x + lx * scale
                py = base_y + ly * scale

                # Draw occupant filling cell (no margin - we want visibility)
                draw.rectangle([px, py, px + scale - 1, py + scale - 1], fill=color)

    # Roof overlay (lighting darkness): tint every roofed cell so the ORGANIC underground boundary is
    # visible headlessly (no Unity needed). Drawn before the north-up flip so it aligns + flips with the map.
    if show_roof:
        overlay = Image.new('RGBA', (img_w, img_h), (0, 0, 0, 0))
        odraw = ImageDraw.Draw(overlay)
        for (cx, cy), chunk in chunks.items():
            roof = chunk.get("roof")
            if not roof:
                continue
            base_x = cx * CHUNK_SIZE * scale
            base_y = cy * CHUNK_SIZE * scale
            for ly, row in enumerate(roof):
                for lx, r in enumerate(row):
                    if not r:
                        continue
                    px = base_x + lx * scale
                    py = base_y + ly * scale
                    odraw.rectangle([px, py, px + scale - 1, py + scale - 1], fill=(20, 40, 130, 125))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)  # rebind for the chunk grid below

    # Draw chunk grid if requested
    if show_chunks:
        for i in range(1, zw // CHUNK_SIZE):
            pos = i * CHUNK_SIZE * scale
            draw.line([(pos, 0), (pos, img_h - 1)], fill=CHUNK_GRID_COLOR, width=1)
        for i in range(1, zh // CHUNK_SIZE):
            pos = i * CHUNK_SIZE * scale
            draw.line([(0, pos), (img_w - 1, pos)], fill=CHUNK_GRID_COLOR, width=1)

    # The game/scene renders are NORTH-up (high +Y at the top); view_world builds rows top-down from
    # y=0 (south-up), so flip vertically to match the rest of the toolchain.
    return img.transpose(Image.FLIP_TOP_BOTTOM)


def add_legend(img: Image.Image, scale: int) -> Image.Image:
    """Add a color legend to the image."""
    legend_width = 200
    legend_height = img.height

    # Create new image with legend space
    new_img = Image.new('RGB', (img.width + legend_width, img.height), LEGEND_BG_COLOR)
    new_img.paste(img, (0, 0))

    draw = ImageDraw.Draw(new_img)
    x_start = img.width + 10
    y = 10
    line_height = 18
    swatch_size = 12

    # Ground tiles legend
    draw.text((x_start, y), "GROUND TILES", fill=TEXT_COLOR)
    y += line_height + 5

    for tile_id, color in sorted(GROUND_COLORS.items()):
        draw.rectangle([x_start, y, x_start + swatch_size, y + swatch_size], fill=color)
        draw.text((x_start + swatch_size + 5, y), tile_id, fill=TEXT_COLOR)
        y += line_height

    y += 15

    # Occupant categories legend
    draw.text((x_start, y), "OCCUPANTS", fill=TEXT_COLOR)
    y += line_height + 5

    for category, color in sorted(CATEGORY_COLORS.items()):
        draw.rectangle([x_start, y, x_start + swatch_size, y + swatch_size], fill=color)
        draw.text((x_start + swatch_size + 5, y), category, fill=TEXT_COLOR)
        y += line_height

    y += 15

    # Special markers
    draw.text((x_start, y), "MARKERS", fill=TEXT_COLOR)
    y += line_height + 5

    draw.ellipse([x_start, y, x_start + swatch_size, y + swatch_size],
                 outline=SPAWN_MARKER_COLOR, width=2)
    draw.text((x_start + swatch_size + 5, y), "spawn point", fill=TEXT_COLOR)
    y += line_height

    draw.rectangle([x_start, y, x_start + swatch_size, y + swatch_size],
                   fill=ZONE_MISSING_COLOR, outline=ZONE_BORDER_COLOR)
    draw.text((x_start + swatch_size + 5, y), "missing zone", fill=TEXT_COLOR)

    return new_img


def render_world(zones_dir: Path, scale: int = 2, max_rows: int = 3,
                 max_cols: int = 4, show_chunks: bool = False) -> Tuple[Image.Image, Dict]:
    """Render the entire world grid to an image."""
    zone_px = ZONE_SIZE * scale
    img_width = max_cols * zone_px
    img_height = max_rows * zone_px

    img = Image.new('RGB', (img_width, img_height), ZONE_MISSING_COLOR)
    draw = ImageDraw.Draw(img)

    available_zones = scan_available_zones(zones_dir)

    stats = {
        "zones_found": 0,
        "zones_total": max_rows * max_cols,
        "total_occupants": 0,
        "tile_counts": {},
        "occupant_counts": {},
        "category_counts": {},
    }

    for row in range(max_rows):
        for col in range(max_cols):
            zone_id = available_zones.get((row, col))
            zone_x = col * zone_px
            zone_y = row * zone_px

            if zone_id:
                zone_data = load_zone_data(zones_dir, zone_id)
                if zone_data:
                    stats["zones_found"] += 1

                    # Render and paste zone
                    zone_img = render_zone(zone_data, scale, show_chunks)
                    img.paste(zone_img, (zone_x, zone_y))

                    # Collect stats
                    for chunk in zone_data["chunks"].values():
                        for row_data in chunk.get("ground", []):
                            for tile in row_data:
                                stats["tile_counts"][tile] = stats["tile_counts"].get(tile, 0) + 1
                        for row_data in chunk.get("occupants", []):
                            for occ in row_data:
                                if occ and occ != "@":
                                    occ_id = occ.get("id") if isinstance(occ, dict) else str(occ)
                                    stats["occupant_counts"][occ_id] = stats["occupant_counts"].get(occ_id, 0) + 1
                                    stats["total_occupants"] += 1
                                    cat = OCCUPANT_CATEGORIES.get(occ_id, "unknown")
                                    stats["category_counts"][cat] = stats["category_counts"].get(cat, 0) + 1

                    # Draw spawn marker
                    config = zone_data["config"]
                    spawn = config.get("spawn_point", [ZONE_SIZE // 2, ZONE_SIZE // 2])
                    spawn_px_x = zone_x + spawn[0] * scale
                    spawn_px_y = zone_y + spawn[1] * scale
                    marker_size = max(4, scale * 2)
                    draw.ellipse([
                        spawn_px_x - marker_size, spawn_px_y - marker_size,
                        spawn_px_x + marker_size, spawn_px_y + marker_size
                    ], outline=SPAWN_MARKER_COLOR, width=2)

                    # Zone label
                    draw.text((zone_x + 5, zone_y + 5), f"{zone_id}", fill=TEXT_COLOR)

            # Draw zone border
            draw.rectangle([zone_x, zone_y, zone_x + zone_px - 1, zone_y + zone_px - 1],
                          outline=ZONE_BORDER_COLOR, width=2)

    return img, stats


def print_stats(stats: Dict[str, Any]):
    """Print world statistics to console."""
    print("\n" + "=" * 60)
    print("WORLD STATISTICS")
    print("=" * 60)

    print(f"\nZones: {stats['zones_found']} / {stats['zones_total']} found")
    print(f"Total occupants: {stats['total_occupants']:,}")

    if stats['tile_counts']:
        print("\nGround tile distribution:")
        total_tiles = sum(stats['tile_counts'].values())
        for tile, count in sorted(stats['tile_counts'].items(), key=lambda x: -x[1]):
            pct = 100 * count / total_tiles
            bar = "#" * int(pct / 2)
            print(f"  {tile:15} {count:8,} ({pct:5.1f}%) {bar}")

    if stats['category_counts']:
        print("\nOccupant categories:")
        for cat, count in sorted(stats['category_counts'].items(), key=lambda x: -x[1]):
            print(f"  {cat:15} {count:6,}")

    if stats['occupant_counts']:
        print("\nTop 15 occupants:")
        for occ, count in sorted(stats['occupant_counts'].items(), key=lambda x: -x[1])[:15]:
            print(f"  {occ:20} {count:5,}")


def main():
    parser = argparse.ArgumentParser(
        description="Visualize Bug Farmer world as PNG image",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python view_world.py                  # Render world overview
  python view_world.py village_21       # Render single zone detail
  python view_world.py --scale 4        # Larger image (4px per cell)
  python view_world.py --chunks         # Show chunk grid lines
  python view_world.py --legend         # Add color legend
        """
    )
    parser.add_argument("zone", nargs="?", help="Specific zone to render")
    parser.add_argument("--scale", type=int, default=2, help="Pixels per cell (default: 2)")
    parser.add_argument("--rows", type=int, default=3, help="Zone rows to render (default: 3)")
    parser.add_argument("--cols", type=int, default=4, help="Zone columns to render (default: 4)")
    parser.add_argument("--chunks", action="store_true", help="Show chunk grid lines")
    parser.add_argument("--roof", action="store_true", help="Tint roofed (underground) cells — the lighting roof mask")
    parser.add_argument("--legend", action="store_true", help="Add color legend")
    parser.add_argument("--output", "-o", type=str, help="Output filename")
    args = parser.parse_args()

    # Find zones directory ("script_dir" stays = tools/, even though this file lives in tools/world/)
    script_dir = Path(__file__).parent.parent
    project_root = script_dir.parent
    zones_dir = project_root / "nakama" / "data" / "zones"

    # Output lands in the zone's own preview folder (tools/README.md): previews/zones/<zone>/.
    output_dir = script_dir / "_generated" / "previews" / "zones" / args.zone
    output_dir.mkdir(parents=True, exist_ok=True)

    if not zones_dir.exists():
        print(f"Error: Zones directory not found: {zones_dir}")
        sys.exit(1)

    if args.zone:
        # Single zone detail view
        zone_data = load_zone_data(zones_dir, args.zone)
        if not zone_data:
            print(f"Error: Zone '{args.zone}' not found")
            print(f"Available zones: {list(scan_available_zones(zones_dir).values())}")
            sys.exit(1)

        scale = args.scale if args.scale > 2 else 4  # Default to 4 for detail
        img = render_zone(zone_data, scale, args.chunks, args.roof)

        if args.legend:
            img = add_legend(img, scale)

        output_file = output_dir / (args.output or f"{args.zone}_detail.png")
        img.save(output_file)

        config = zone_data["config"]
        print(f"Zone: {config.get('zone_id', args.zone)}")
        print(f"Name: {config.get('name', 'Unknown')}")
        print(f"Position: row={config.get('row')}, col={config.get('col')}")
        print(f"Spawn: {config.get('spawn_point', 'Not set')}")
        print(f"\nSaved: {output_file} ({img.width}x{img.height}px)")

    else:
        # World overview
        img, stats = render_world(zones_dir, args.scale, args.rows, args.cols, args.chunks)

        if args.legend:
            img = add_legend(img, args.scale)

        output_file = output_dir / (args.output or "world_view.png")
        img.save(output_file)

        print(f"Saved: {output_file} ({img.width}x{img.height}px)")
        print_stats(stats)


if __name__ == "__main__":
    main()
