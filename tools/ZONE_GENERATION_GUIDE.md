# Zone Generation Guide

This document provides the authoritative reference for generating zones using `generate_zone.py`. The LLM reads this guide to create consistent, properly structured zone data.

---

## World Grid Layout

The BugFarmer world is a 6x4 grid (6 rows, 4 columns):

```
                                 NORTH
                                   ^
         Col 0        Col 1        Col 2        Col 3
       +------------+------------+------------+------------+
Row 0  |   HARD     ~   HARD     |  EX-HARD   | EX-EX HARD |
       |   Locust   ~  Millipede |  Spider    |  Spider    |
       |  Farmland  ~   Forest   | Vale West  | Vale East  |
       +------------+-----~~~~~~~+------------+------------+
Row 1  |  MEDIUM    |  MEDIUM  ~~|   HARD     | EX-HARD    |
       |   Meadow   | Butterfly~~| Scorpion   |   Deep     |
       |   (Bees)   |  Fields  ~~|  Rocks     |   Swamp    |
       +------------+----------~~+~~~~~~~~~~--+------------+
Row 2  |   EASY     |   EASY     |  MEDIUM  ~~|   HARD     |
       |    Bee     |  Village   |   Wasp   ~~|  Shallow   |
       |   Meadow   |  (start)   |  Thicket ~~|   Swamp    |
       +============+============+===========W+============+  <- CLIFF WALL
Row 3  |   EASY     |   EASY     |  MEDIUM  WW|   HARD     |
UNDER- | Centipede  | Underground| Underground|  Deadly    |
GROUND |  Cavern    |  Passages  |   River  WW|   Ants     |
       +------------+------------+----------~-+------------+
Row 4  |  MEDIUM    |  MEDIUM    |   HARD     | EX-HARD    |
       | Centipede  | Underground| Underground|  Deadly    |
       |  Cavern    |  Passages  |   River    |   Ants     |
       +------------+------------+------------+------------+
Row 5  |   HARD     |   HARD     | EX-HARD    | EX-EX HARD |
DEEP   | Centipede  |   Deep     |   Deep     |    Ant     |
CLIFF  |  Depths    |  Passages  |   River    |   Queen    |
       +------------+------------+------------+------------+
                                 SOUTH

Legend:
~ = River (shallow crossings, separates Medium from Hard areas)
W = Waterfall (river meets cliff edge)
= = Cliff wall boundary between surface and underground
```

---

## River System

The river is a major world feature that:
- Separates Medium difficulty zones (west) from Hard difficulty zones (east)
- Runs primarily between columns 1 and 2 on the surface
- Allows shallow crossings but slows movement
- Becomes a waterfall at the cliff wall (Row 2/3 boundary)
- Continues underground as the Underground River (Col 2, Rows 3-5)

### River Path (Surface)

The river flows from north to south with these waypoints:

| Row | West Bank | East Bank | Notes |
|-----|-----------|-----------|-------|
| Row 0 | Millipede Forest (1,0) east edge | Spider Vale West (2,0) west edge | River forms natural barrier |
| Row 1 | Butterfly Fields (1,1) east edge | Scorpion Rocks (2,1) west edge | Diagonal section near zone boundary |
| Row 2 | Wasp Thicket (2,2) east edge | Shallow Swamp (3,2) west edge | River shifts east here |

### Waterfall (Cliff Edge)

At the boundary between Row 2 and Row 3:
- Surface river becomes a dramatic waterfall
- Water cascades down the cliff face
- Creates the Underground River entry point
- Zone (2,2) Wasp Thicket has waterfall overlook area
- Zone (2,3) Underground River has waterfall pool at north

### Underground River (Col 2, Rows 3-5)

The river continues underground:
- **Row 3**: Waterfall pool, cave stream, aquatic bugs
- **Row 4**: Wider underground river, islands, aquatic dangers
- **Row 5**: Underground lake, deep aquatic creatures, boss area

### River Tile Usage

| Tile ID | Use Case | Movement |
|---------|----------|----------|
| `water_shallow` | Shallow crossings, river edges | Slow (0.5x) |
| `water_deep` | River center, lakes | Blocks players |
| `sand` | River banks, beaches | Normal |
| `mud` | Swamp river edges | Slow |

### Generating River in Zones

When generating zones that contain the river:

```python
# Example: Adding river to zone
builder = ZoneBuilder("millipede_forest_01", row=0, col=1, seed=1001)
builder.fill_ground("grass")

# River along east edge (x = 480-511 for a 512-cell zone)
# Use varying width for natural look
for y in range(0, 512):
    river_center = 495 + (y % 20) - 10  # Meander
    for x in range(river_center - 3, river_center + 4):
        if abs(x - river_center) <= 1:
            builder.set_ground(x, y, "water_deep")
        else:
            builder.set_ground(x, y, "water_shallow")
    # Sand banks
    builder.set_ground(river_center - 4, y, "sand")
    builder.set_ground(river_center + 4, y, "sand")
```

---

## Zone Naming Convention

Zone IDs follow the pattern: `{biome}_{row}{col}`

| Zone ID | Location | Biome Type |
|---------|----------|------------|
| `locust_farmland_00` | Row 0, Col 0 | farmland |
| `millipede_forest_01` | Row 0, Col 1 | forest |
| `spider_vale_west_02` | Row 0, Col 2 | vale |
| `spider_vale_east_03` | Row 0, Col 3 | vale |
| `meadow_10` | Row 1, Col 0 | meadow |
| `butterfly_fields_11` | Row 1, Col 1 | meadow |
| `scorpion_rocks_12` | Row 1, Col 2 | rocky |
| `deep_swamp_13` | Row 1, Col 3 | swamp |
| `bee_meadow_20` | Row 2, Col 0 | meadow |
| `village_21` | Row 2, Col 1 | village |
| `wasp_thicket_22` | Row 2, Col 2 | thicket |
| `shallow_swamp_23` | Row 2, Col 3 | swamp |
| `centipede_cavern_30` | Row 3, Col 0 | cave |
| `underground_passages_31` | Row 3, Col 1 | cave |
| `underground_river_32` | Row 3, Col 2 | cave_water |
| `deadly_ants_33` | Row 3, Col 3 | ant_colony |
| `centipede_cavern_40` | Row 4, Col 0 | cave |
| `underground_passages_41` | Row 4, Col 1 | cave |
| `underground_river_42` | Row 4, Col 2 | cave_water |
| `deadly_ants_43` | Row 4, Col 3 | ant_colony |
| `centipede_depths_50` | Row 5, Col 0 | cave_deep |
| `deep_passages_51` | Row 5, Col 1 | cave_deep |
| `deep_river_52` | Row 5, Col 2 | cave_water |
| `ant_queen_53` | Row 5, Col 3 | ant_colony |

---

## Coordinate System

### Global Coordinates
- **Cell**: 16x16 pixels, the smallest unit
- **Chunk**: 32x32 cells (512x512 pixels)
- **Zone**: 16x16 chunks (512x512 cells = 8192x8192 pixels)

### Zone Grid Position
- Row 0 = NORTH (top of world)
- Row 5 = SOUTH (bottom of world, deep underground)
- Col 0 = WEST
- Col 3 = EAST

### Within a Zone
- Origin (0,0) is top-left (northwest corner)
- X increases eastward (right)
- Y increases southward (down)
- Zone width/height default to 512 cells (16 chunks x 32 cells)

---

## Zone Structure

Each zone contains:

1. **zone.json** - Metadata
```json
{
  "zone_id": "village_21",
  "name": "Starting Village",
  "row": 2,
  "col": 1,
  "width": 512,
  "height": 512,
  "spawn_point": [256, 256],
  "biome_type": "village"
}
```

2. **chunk_X_Y.json** - Tile data for each 32x32 chunk
```json
{
  "chunk_x": 0,
  "chunk_y": 0,
  "ground": [["grass", "grass", ...], ...],
  "occupants": [[null, {"id": "tree_oak", "dir": 0}, "@", ...], ...]
}
```

---

## Two-Layer System

### Layer 1: Ground
- Always filled (no empty cells)
- Tile IDs: `grass`, `dirt`, `sand`, `mud`, `stone_path`, `water_shallow`, `water_deep`, `cave_floor`, etc.
- Determines walkability and movement speed

### Layer 2: Occupants
- Can be empty (`null`), blocked (`"@"`), or contain an occupant object
- Occupant object: `{"id": "tree_oak", "dir": 0}`
- Multi-cell occupants: anchor at bottom-left, other cells store `"@"`

---

## Occupant Footprints

Common footprint sizes (from `generate_zone.py`):

| Category | Occupant | Footprint (WxH) |
|----------|----------|-----------------|
| Trees | tree_oak, tree_pine, tree_palm | 2x2 |
| Trees | tree_dead, tree_fruit | 1x1 |
| Rocks | rock_large, boulder | 2x2 |
| Rocks | rock_small | 1x1 |
| Plants | bush, flower_*, tall_grass, reeds | 1x1 |
| Plants | sunflower | 1x2 |
| Mushrooms | mushroom_red, mushroom_glow | 1x1 |
| Cave | stalagmite, crystal_small | 1x1 |
| Cave | crystal_large, ant_mound | 2x2 |
| Structures | fence_wood, fence_stone | 1x1 |
| Structures | door_wood, door_iron | 1x2 |
| Furniture | workbench, furnace, table_wood | 2x2 |
| Furniture | chest, anvil, cooking_pot | 2x1 |
| Buildings | cottage (template) | 8x8 |
| Buildings | shack (template) | 6x5 |

---

## Multi-Cell Occupant Rules

1. **Anchor Position**: Bottom-left cell of the footprint
2. **Blocked Cells**: Non-anchor cells store `"@"` marker
3. **Chunk Boundary**: Multi-cell occupants CANNOT cross chunk boundaries
4. **Validation**: `place_occupant()` checks all cells are empty before placing

Example: 2x2 tree_oak at position (10, 10)
```
Cell (10, 10): {"id": "tree_oak", "dir": 0}  <- anchor
Cell (11, 10): "@"  <- blocked
Cell (10, 11): "@"  <- blocked
Cell (11, 11): "@"  <- blocked
```

---

## Using generate_zone.py

### Basic Usage

```python
from generate_zone import ZoneBuilder

# Create builder with explicit seed for reproducibility
builder = ZoneBuilder("village_21", row=2, col=1, seed=12345)

# Fill base terrain
builder.fill_ground("grass")

# Add paths
builder.add_path((256, 0), (256, 511), "stone_path", width=3)

# Place individual occupants
builder.place_occupant(100, 100, "tree_oak")

# Scatter occupants randomly
builder.scatter_occupants("flower_red", count=50)

# Use weighted scatter for variety
builder.scatter_weighted({
    "tree_oak": 3,
    "tree_pine": 2,
    "tree_dead": 1
}, count=100)

# Place building from template
builder.place_building(200, 200, "cottage")

# Export zone files
builder.export("/path/to/zones/village_21")
```

### Seeds for Variants

Use explicit seeds to create reproducible variants:

```python
# Base village
builder = ZoneBuilder("village_21", row=2, col=1, seed=1000)

# Variant with different tree placement
builder = ZoneBuilder("village_21_v2", row=2, col=1, seed=2000)
```

---

## Road Network

Roads connect from the Starting Village (2,1) to all surface zones:

### Main Roads from Village

| Direction | Destination | Road Pattern |
|-----------|-------------|--------------|
| North | Butterfly Fields (1,1) | Vertical `stone_path` |
| West | Bee Meadow (2,0) | Horizontal `stone_path` |
| East | Wasp Thicket (2,2) | Horizontal `stone_path` |
| South | Cliff Entry | Short path to cliff wall |

### Road Implementation

```python
# Main north-south road through village
builder.add_path((256, 0), (256, 511), "stone_path", width=3)

# East-west road
builder.add_path((0, 256), (511, 256), "stone_path", width=3)

# Intersection already handled by add_path overlap
```

---

## Hub Areas

Each zone has a hub area with:
- Signpost (fast travel point)
- Thematic structure (NPC building)
- Starter resources

### Village Hub (Central Square)
```python
# Clear area for village center
builder.fill_region(240, 240, 32, 32, "stone_path")

# Place well in center
builder.place_occupant(254, 254, "well")

# Signpost
builder.place_occupant(248, 248, "signpost")

# Workbench for new players
builder.place_occupant(260, 248, "workbench")
```

### Zone Hub Template
```python
def create_hub(builder, cx, cy, structure_id):
    """Create a standard hub area at center (cx, cy)"""
    # Clear area
    builder.fill_region(cx-8, cy-8, 16, 16, "dirt")

    # Signpost
    builder.place_occupant(cx-2, cy-2, "signpost")

    # Main structure
    builder.place_building(cx+2, cy-4, structure_id)
```

---

## Biome Generation Guidelines

### Surface Biomes

#### Meadow (bee_meadow_20, meadow_10, butterfly_fields_11)
- Base: `grass`
- Paths: `dirt` trails, occasional `stone_path`
- Occupants: flowers (heavy), tall_grass, bushes, scattered trees
- Features: beehives, flower patches, gentle hills (visual only)

#### Forest (millipede_forest_01)
- Base: `grass` with `dirt` patches
- Paths: `dirt` trails
- Occupants: dense trees, bushes, mushrooms, logs, stumps
- Features: clearings, fallen logs, mushroom rings

#### Village (village_21)
- Base: `grass` with `dirt` and `stone_path`
- Paths: `stone_path` roads in grid
- Occupants: buildings, fences, crafting stations, gardens
- Features: central square, player house area, NPC cottages

#### Thicket (wasp_thicket_22)
- Base: `grass` with `mud` patches
- Paths: narrow `dirt` trails
- Occupants: dense bushes, tall_grass, thorny plants, dead trees
- Features: abandoned shack, wasp nests, overgrown areas

#### Swamp (shallow_swamp_23, deep_swamp_13)
- Base: `mud` with `water_shallow` pools
- Paths: raised `dirt` or wooden walkways
- Occupants: reeds, dead trees, mushrooms, lily pads
- Features: water features, fishing spots, foggy areas

#### Rocky (scorpion_rocks_12)
- Base: `sand` with `stone` outcrops
- Paths: `dirt` trails between rocks
- Occupants: rocks (many), boulders, dead bushes, crystals
- Features: cave entrances, mining spots, scorpion dens

### Underground Biomes

#### Cave (centipede_cavern_30, underground_passages_31)
- Base: `cave_floor`
- Paths: natural corridors
- Occupants: stalagmites, crystals, mushrooms, webs, bones
- Features: large caverns, narrow tunnels, ore veins

#### Cave Water (underground_river_32, deep_river_52)
- Base: `cave_floor` with `water_deep` river
- Paths: along river banks
- Occupants: wet-themed, aquatic plants, crystals
- Features: underground river, waterfalls, pools

#### Ant Colony (deadly_ants_33, ant_queen_53)
- Base: `cave_floor` with `dirt` tunnels
- Paths: organized tunnel network
- Occupants: ant_mound, egg chambers, food storage
- Features: regular tunnel grid, queen chamber (Row 5)

---

## Zone Connections

Zones connect at their edges. Ensure paths align:

| Zone A | Zone B | Connection |
|--------|--------|------------|
| village_21 | bee_meadow_20 | West edge, y=256 |
| village_21 | butterfly_fields_11 | North edge, x=256 |
| village_21 | wasp_thicket_22 | East edge, y=256 |

### Edge Alignment

When zone A's east edge connects to zone B's west edge:
- Zone A: path ends at x=511
- Zone B: path starts at x=0
- Both at same y-coordinate

```python
# In village_21 (east road to wasp_thicket)
builder.add_path((256, 256), (511, 256), "stone_path", width=3)

# In wasp_thicket_22 (west road from village)
builder.add_path((0, 256), (256, 256), "dirt", width=2)
```

---

## Generation Workflow

1. **Read this guide** and BIOME_PALETTES.md
2. **Create ZoneBuilder** with zone_id, row, col, explicit seed
3. **Fill base ground** for biome
4. **Add major features** (rivers if applicable, roads)
5. **Place hub area** (signpost, structure)
6. **Scatter natural occupants** by biome
7. **Place specific features** (buildings, unique landmarks)
8. **Validate** chunk boundaries for multi-cell occupants
9. **Export** zone files
10. **Review** and iterate if needed

---

## Example: Complete Village Generation

```python
from generate_zone import ZoneBuilder

builder = ZoneBuilder("village_21", row=2, col=1, seed=42)

# Base terrain
builder.fill_ground("grass")

# Main roads (cross pattern)
builder.add_path((256, 0), (256, 511), "stone_path", width=3)  # N-S
builder.add_path((0, 256), (511, 256), "stone_path", width=3)  # E-W

# Central square
builder.fill_region(248, 248, 16, 16, "stone_path")

# Village features
builder.place_occupant(256, 256, "well")
builder.place_occupant(240, 248, "signpost")
builder.place_occupant(264, 248, "workbench")

# Player house area (northeast)
builder.place_building(320, 180, "cottage")
builder.fill_region(318, 210, 12, 4, "garden_plot")

# NPC buildings
builder.place_building(180, 180, "cottage")  # Beekeeper
builder.place_building(180, 320, "shack")    # Fisherman

# Scatter trees around edges (avoid center)
builder.scatter_weighted(
    {"tree_oak": 3, "tree_pine": 2, "bush": 4},
    count=80,
    avoid_region=(200, 200, 112, 112)
)

# Flowers near paths
builder.scatter_occupants("flower_yellow", 30, region=(0, 0, 200, 200))
builder.scatter_occupants("flower_red", 30, region=(312, 0, 200, 200))

# Fencing around gardens
builder.add_fence_rect(316, 208, 16, 8, "fence_wood")

builder.export("nakama/data/zones/village_21")
```

---

## Validation Checklist

Before exporting a zone:

- [ ] Zone ID matches naming convention (`{biome}_{row}{col}`)
- [ ] Spawn point is walkable and not blocked
- [ ] Roads connect to neighboring zones at correct positions
- [ ] River tiles match adjacent zones (if applicable)
- [ ] No multi-cell occupants cross chunk boundaries
- [ ] Hub area has signpost and thematic structure
- [ ] Biome-appropriate occupant distribution
- [ ] Difficulty-appropriate hazard placement
