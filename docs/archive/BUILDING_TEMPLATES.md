# Building Templates

This document defines pre-made building layouts for use with `generate_zone.py`. Buildings are placed as groups of occupants with specific arrangements.

---

## Template Format

Each template specifies:
- **Size**: Width x Height in cells
- **Ground**: Floor tile pattern
- **Occupants**: Positioned objects
- **Anchor**: Bottom-left cell of the building footprint

Buildings are placed with `builder.place_building(x, y, template_name)` where (x, y) is the anchor position.

---

## Residential Buildings

### Cottage (`cottage`)

A small cozy home for NPCs or the player.

**Size**: 8x8 cells (128x128 pixels)

**Layout**:
```
. . . . . . . .
. W W D D W W .    W = wall_wood
. W . . . . W .    D = door_wood (1x2)
. W . . . . W .    . = wood_floor (ground)
. W . T . B W .    T = table_wood (2x2)
. W . @ . @ W .    B = bed (2x4)
. W . . . . W .    @ = blocked by multi-cell
. . . . . . . .
```

**Implementation**:
```python
def place_cottage(builder, x, y):
    # Ground: wood floor interior
    builder.fill_region(x+1, y+1, 6, 6, "wood_floor")

    # Walls
    for i in range(8):
        builder.place_occupant(x+i, y, "wall_wood")      # North
        builder.place_occupant(x+i, y+7, "wall_wood")    # South
    for i in range(1, 7):
        builder.place_occupant(x, y+i, "wall_wood")      # West
        builder.place_occupant(x+7, y+i, "wall_wood")    # East

    # Door (north wall, center) - remove walls, place door
    builder.clear_occupant(x+3, y)
    builder.clear_occupant(x+4, y)
    builder.place_occupant(x+3, y, "door_wood")

    # Furniture
    builder.place_occupant(x+2, y+4, "table_wood")  # 2x2
    builder.place_occupant(x+5, y+3, "bed")         # 2x4, placed vertically
    builder.place_occupant(x+2, y+2, "chest")       # 2x1
```

---

### Shack (`shack`)

A small, simple structure. Often abandoned or in disrepair.

**Size**: 6x5 cells (96x80 pixels)

**Layout**:
```
. . . . . .
. W D D W .    W = wall_wood
. W . . W .    D = door_wood
. W C . W .    C = chest (2x1)
. . . . . .
```

**Implementation**:
```python
def place_shack(builder, x, y):
    # Ground: wood floor interior
    builder.fill_region(x+1, y+1, 4, 3, "wood_floor")

    # Walls
    for i in range(6):
        builder.place_occupant(x+i, y, "wall_wood")      # North
        builder.place_occupant(x+i, y+4, "wall_wood")    # South
    for i in range(1, 4):
        builder.place_occupant(x, y+i, "wall_wood")      # West
        builder.place_occupant(x+5, y+i, "wall_wood")    # East

    # Door (north wall)
    builder.clear_occupant(x+2, y)
    builder.clear_occupant(x+3, y)
    builder.place_occupant(x+2, y, "door_wood")

    # Furniture
    builder.place_occupant(x+1, y+3, "chest")
```

---

### Ruined Shack (`ruined_shack`)

A damaged version of the shack with missing walls.

**Size**: 6x5 cells

**Layout**:
```
. . . . . .
. W . . . .    W = wall_wood (partial)
. . . . W .    Missing walls, no door
. W . . . .
. . . . . .
```

**Implementation**:
```python
def place_ruined_shack(builder, x, y):
    # Ground: dirt (no floor)
    builder.fill_region(x+1, y+1, 4, 3, "dirt")

    # Partial walls (random gaps)
    builder.place_occupant(x+1, y+1, "wall_wood")
    builder.place_occupant(x+4, y+2, "wall_wood")
    builder.place_occupant(x+1, y+3, "wall_wood")

    # Debris
    builder.place_occupant(x+3, y+2, "rock_small")
    builder.place_occupant(x+2, y+3, "bone_pile")
```

---

## Commercial Buildings

### Market Stall (`market_stall`)

An open-air trading post.

**Size**: 4x3 cells (64x48 pixels)

**Layout**:
```
. F F .    F = fence_wood
. T @ .    T = table_wood (2x2)
. @ @ .
```

**Implementation**:
```python
def place_market_stall(builder, x, y):
    # Ground: stone path
    builder.fill_region(x, y, 4, 3, "stone_path")

    # Back fence
    builder.place_occupant(x+1, y, "fence_wood")
    builder.place_occupant(x+2, y, "fence_wood")

    # Counter table
    builder.place_occupant(x+1, y+1, "table_wood")
```

---

### Shop (`shop`)

A larger building for NPC merchants.

**Size**: 10x8 cells (160x128 pixels)

**Layout**:
```
. . . . . . . . . .
. W W W D D W W W .    W = wall_wood
. W . . . . . . W .    D = door_wood
. W T @ . . C @ W .    T = table_wood (counter)
. W @ @ . . . . W .    C = chest (storage)
. W . . . . . . W .    S = sign
. W . . S . . . W .
. . . . . . . . . .
```

**Implementation**:
```python
def place_shop(builder, x, y):
    # Ground
    builder.fill_region(x+1, y+1, 8, 6, "wood_floor")

    # Walls
    for i in range(10):
        builder.place_occupant(x+i, y, "wall_wood")
        builder.place_occupant(x+i, y+7, "wall_wood")
    for i in range(1, 7):
        builder.place_occupant(x, y+i, "wall_wood")
        builder.place_occupant(x+9, y+i, "wall_wood")

    # Door
    builder.clear_occupant(x+4, y)
    builder.clear_occupant(x+5, y)
    builder.place_occupant(x+4, y, "door_wood")

    # Counter
    builder.place_occupant(x+2, y+3, "table_wood")

    # Storage
    builder.place_occupant(x+6, y+3, "chest")

    # Shop sign
    builder.place_occupant(x+4, y+6, "signpost")
```

---

## Utility Buildings

### Well (`well_area`)

A village water source with surrounding area.

**Size**: 5x5 cells (80x80 pixels)

**Layout**:
```
. . . . .
. P . P .    P = stone_path (ground)
. . W . .    W = well (1x1)
. P . P .
. . . . .
```

**Implementation**:
```python
def place_well_area(builder, x, y):
    # Stone path around well
    builder.fill_region(x, y, 5, 5, "stone_path")

    # Well in center
    builder.place_occupant(x+2, y+2, "well")
```

---

### Crafting Area (`crafting_area`)

An outdoor workspace with multiple stations.

**Size**: 8x6 cells (128x96 pixels)

**Layout**:
```
. . . . . . . .
. W @ . F @ . .    W = workbench (2x2)
. @ @ . @ @ . .    F = furnace (2x2)
. . . . . . . .    A = anvil (2x1)
. A @ . C @ . .    C = chest (2x1)
. . . . . . . .
```

**Implementation**:
```python
def place_crafting_area(builder, x, y):
    # Ground: stone
    builder.fill_region(x, y, 8, 6, "stone_path")

    # Stations
    builder.place_occupant(x+1, y+1, "workbench")
    builder.place_occupant(x+4, y+1, "furnace")
    builder.place_occupant(x+1, y+4, "anvil")
    builder.place_occupant(x+4, y+4, "chest")
```

---

### Storage Shed (`storage_shed`)

A small building for storing items.

**Size**: 5x4 cells (80x64 pixels)

**Layout**:
```
. . . . .
. W D W .    W = wall_wood
. W C W .    D = door_wood
. . @ . .    C = chest (2x1)
```

**Implementation**:
```python
def place_storage_shed(builder, x, y):
    # Ground
    builder.fill_region(x+1, y+1, 3, 2, "wood_floor")

    # Walls
    for i in range(5):
        builder.place_occupant(x+i, y, "wall_wood")
        builder.place_occupant(x+i, y+3, "wall_wood")
    builder.place_occupant(x, y+1, "wall_wood")
    builder.place_occupant(x, y+2, "wall_wood")
    builder.place_occupant(x+4, y+1, "wall_wood")
    builder.place_occupant(x+4, y+2, "wall_wood")

    # Door (top center)
    builder.clear_occupant(x+2, y)
    builder.place_occupant(x+2, y, "door_wood")

    # Chest
    builder.place_occupant(x+1, y+2, "chest")
```

---

## Natural Structures

### Beehive Cluster (`beehive_cluster`)

A group of beehives for honey production.

**Size**: 6x4 cells (96x64 pixels)

**Layout**:
```
. H . . H .    H = beehive (1x1)
. . . . . .
. . H . . .
F F . F F F    F = flower_* (various)
```

**Implementation**:
```python
def place_beehive_cluster(builder, x, y):
    # Beehives
    builder.place_occupant(x+1, y, "beehive")
    builder.place_occupant(x+4, y, "beehive")
    builder.place_occupant(x+2, y+2, "beehive")

    # Surrounding flowers
    flowers = ["flower_red", "flower_yellow", "flower_blue"]
    for i in range(6):
        builder.place_occupant(x+i, y+3, random.choice(flowers))
```

---

### Tree Grove (`tree_grove`)

A small cluster of trees.

**Size**: 8x8 cells (128x128 pixels)

**Layout**:
```
. . . . . . . .
. T @ . . T @ .    T = tree_oak (2x2)
. @ @ . . @ @ .
. . . . . . . .
. . T @ . . . .
. . @ @ . T @ .
. . . . . @ @ .
. . . . . . . .
```

**Implementation**:
```python
def place_tree_grove(builder, x, y):
    builder.place_occupant(x+1, y+1, "tree_oak")
    builder.place_occupant(x+5, y+1, "tree_oak")
    builder.place_occupant(x+2, y+4, "tree_oak")
    builder.place_occupant(x+5, y+5, "tree_oak")
```

---

### Rock Formation (`rock_formation`)

A cluster of rocks and boulders.

**Size**: 6x6 cells (96x96 pixels)

**Layout**:
```
. . r . . .    r = rock_small (1x1)
. R @ . r .    R = rock_large (2x2)
. @ @ . . .
. . . R @ .
. r . @ @ .
. . . . . .
```

**Implementation**:
```python
def place_rock_formation(builder, x, y):
    builder.place_occupant(x+2, y, "rock_small")
    builder.place_occupant(x+4, y+1, "rock_small")
    builder.place_occupant(x+1, y+1, "rock_large")
    builder.place_occupant(x+3, y+3, "rock_large")
    builder.place_occupant(x+1, y+4, "rock_small")
```

---

### Mushroom Ring (`mushroom_ring`)

A fairy ring of mushrooms.

**Size**: 5x5 cells (80x80 pixels)

**Layout**:
```
. . M . .    M = mushroom_red or mushroom_glow
. M . M .
M . . . M
. M . M .
. . M . .
```

**Implementation**:
```python
def place_mushroom_ring(builder, x, y):
    positions = [
        (2, 0), (1, 1), (3, 1), (0, 2), (4, 2),
        (1, 3), (3, 3), (2, 4)
    ]
    for dx, dy in positions:
        mtype = "mushroom_glow" if random.random() < 0.3 else "mushroom_red"
        builder.place_occupant(x+dx, y+dy, mtype)
```

---

## Underground Structures

### Cave Camp (`cave_camp`)

An underground explorer's camp.

**Size**: 8x6 cells (128x96 pixels)

**Layout**:
```
. . . . . . . .
. T T . . C @ .    T = torch
. . . . . . . .    C = chest
. . B . . W @ .    B = bed
. . @ . . @ @ .    W = workbench
. . . . . . . .
```

**Implementation**:
```python
def place_cave_camp(builder, x, y):
    # Stone floor area
    builder.fill_region(x, y, 8, 6, "stone_floor")

    # Lighting
    builder.place_occupant(x+1, y+1, "torch")
    builder.place_occupant(x+2, y+1, "torch")

    # Furniture
    builder.place_occupant(x+5, y+1, "chest")
    builder.place_occupant(x+2, y+3, "bed")
    builder.place_occupant(x+5, y+3, "workbench")
```

---

### Mining Shaft (`mining_shaft`)

An entrance to deeper areas.

**Size**: 4x6 cells (64x96 pixels)

**Layout**:
```
. . . .
. L L .    L = ladder (visual marker)
. . . .
. T . .    T = torch
. . . .
. . . .
```

**Implementation**:
```python
def place_mining_shaft(builder, x, y):
    # Cleared stone floor
    builder.fill_region(x, y, 4, 6, "stone_floor")

    # Ladder markers (use sign as placeholder)
    builder.place_occupant(x+1, y+1, "signpost")  # "Ladder down"

    # Lighting
    builder.place_occupant(x+1, y+3, "torch")
```

---

### Crystal Chamber (`crystal_chamber`)

A room with valuable crystal formations.

**Size**: 10x10 cells (160x160 pixels)

**Layout**:
```
. . . . . . . . . .
. S . . . . . . S .    S = stalagmite
. . . C @ . . . . .    C = crystal_large (2x2)
. . . @ @ . c . . .    c = crystal_small
. . . . . . . . . .
. . . . . . . . . .
. . c . . . C @ . .
. . . . . . @ @ . .
. S . . . . . . S .
. . . . . . . . . .
```

**Implementation**:
```python
def place_crystal_chamber(builder, x, y):
    # Cave floor
    builder.fill_region(x, y, 10, 10, "cave_floor")

    # Corner stalagmites
    builder.place_occupant(x+1, y+1, "stalagmite")
    builder.place_occupant(x+8, y+1, "stalagmite")
    builder.place_occupant(x+1, y+8, "stalagmite")
    builder.place_occupant(x+8, y+8, "stalagmite")

    # Large crystals
    builder.place_occupant(x+3, y+2, "crystal_large")
    builder.place_occupant(x+6, y+6, "crystal_large")

    # Small crystals
    builder.place_occupant(x+6, y+3, "crystal_small")
    builder.place_occupant(x+2, y+6, "crystal_small")
```

---

### Ant Chamber (`ant_chamber`)

A room in the ant colony.

**Size**: 8x8 cells (128x128 pixels)

**Layout**:
```
. . . . . . . .
. . . . . . . .
. . M @ . . . .    M = ant_mound (2x2)
. . @ @ . M @ .
. . . . . @ @ .
. . . . . . . .
. . . . . . . .
. . . . . . . .
```

**Implementation**:
```python
def place_ant_chamber(builder, x, y):
    # Dirt floor
    builder.fill_region(x, y, 8, 8, "dirt")

    # Ant mounds
    builder.place_occupant(x+2, y+2, "ant_mound")
    builder.place_occupant(x+5, y+3, "ant_mound")
```

---

## Hub Area Templates

### Village Hub (`village_hub`)

The central area of the starting village.

**Size**: 16x16 cells (256x256 pixels)

**Layout**:
```
(Road from north)
      |
P P P P P P P P P P P P P P P P
P . . . . . . P P . . . . . . P
P . . . . . . P P . . . . . . P
P . . . . . . . . . . . . . . P    P = stone_path (ground)
P . . . . . . . . . . . . . . P    W = well
P . . . S . . . . . W . . . . P    S = signpost
P . . . . . . . . . . . . . . P    B = workbench
P P . . . . . . . . . . . . P P    C = chest
P P . . . . . . . . . . B @ P P
P . . . . . . . . . . . @ @ . P
P . . . . . . . . . . . . . . P
P . . . . . . . . . C @ . . . P
P . . . . . . . . . . . . . . P
P . . . . . . P P . . . . . . P
P . . . . . . P P . . . . . . P
P P P P P P P P P P P P P P P P
      |
(Road south)
```

**Implementation**:
```python
def place_village_hub(builder, x, y):
    # Stone path border
    for i in range(16):
        builder.set_ground(x+i, y, "stone_path")
        builder.set_ground(x+i, y+15, "stone_path")
        builder.set_ground(x, y+i, "stone_path")
        builder.set_ground(x+15, y+i, "stone_path")

    # Road through center
    for i in range(16):
        builder.set_ground(x+7, y+i, "stone_path")
        builder.set_ground(x+8, y+i, "stone_path")

    # Key elements
    builder.place_occupant(x+4, y+5, "signpost")
    builder.place_occupant(x+10, y+5, "well")
    builder.place_occupant(x+11, y+8, "workbench")
    builder.place_occupant(x+10, y+11, "chest")
```

---

### Zone Hub (`zone_hub`)

A generic hub area template for non-village zones.

**Size**: 12x12 cells (192x192 pixels)

**Components**:
- Signpost for fast travel
- Thematic structure (passed as parameter)
- Clear area for players

**Implementation**:
```python
def place_zone_hub(builder, x, y, structure_type="shack", ground="dirt"):
    # Clear ground area
    builder.fill_region(x, y, 12, 12, ground)

    # Signpost
    builder.place_occupant(x+2, y+5, "signpost")

    # Structure (varies by zone)
    if structure_type == "cottage":
        place_cottage(builder, x+4, y+2)
    elif structure_type == "shack":
        place_shack(builder, x+5, y+3)
    elif structure_type == "ruined_shack":
        place_ruined_shack(builder, x+5, y+3)
    elif structure_type == "market_stall":
        place_market_stall(builder, x+6, y+4)
```

---

## Template Registry

Templates available in `generate_zone.py`:

| Template Name | Size | Category |
|---------------|------|----------|
| `cottage` | 8x8 | Residential |
| `shack` | 6x5 | Residential |
| `ruined_shack` | 6x5 | Residential |
| `market_stall` | 4x3 | Commercial |
| `shop` | 10x8 | Commercial |
| `well_area` | 5x5 | Utility |
| `crafting_area` | 8x6 | Utility |
| `storage_shed` | 5x4 | Utility |
| `beehive_cluster` | 6x4 | Natural |
| `tree_grove` | 8x8 | Natural |
| `rock_formation` | 6x6 | Natural |
| `mushroom_ring` | 5x5 | Natural |
| `cave_camp` | 8x6 | Underground |
| `mining_shaft` | 4x6 | Underground |
| `crystal_chamber` | 10x10 | Underground |
| `ant_chamber` | 8x8 | Underground |
| `village_hub` | 16x16 | Hub |
| `zone_hub` | 12x12 | Hub |

---

## Placement Guidelines

### Spacing
- Leave at least 2 cells between buildings
- Roads should be 3 cells wide minimum
- Hub areas need 4+ cell clearance around signpost

### Chunk Boundaries
- Buildings cannot cross chunk boundaries (32 cell grid)
- Plan building placement to fit within chunks
- Use `builder.validate_placement()` before placing

### Orientation
- Buildings default to facing south (door at top)
- Use `dir` parameter for rotation if needed
- Ensure doors face walkable areas

### Validation
```python
# Check if building fits
if builder.can_place_building(x, y, "cottage"):
    builder.place_building(x, y, "cottage")
else:
    # Find alternative position
    pass
```
