# Biome Palettes

This document defines the tile and occupant combinations for each biome type. Use these palettes when generating zones to ensure visual and thematic consistency.

---

## Palette Structure

Each biome palette includes:
- **Ground Tiles**: Primary and secondary terrain
- **Occupants**: Weighted lists for scatter functions
- **Features**: Unique elements for that biome
- **Avoid**: Things that don't belong

---

## Surface Biomes

### Meadow (`meadow`)

Used for: `bee_meadow_20`, `meadow_10`, `butterfly_fields_11`

**Ground Tiles**
| Tile | Usage | Weight |
|------|-------|--------|
| `grass` | Primary base | 85% |
| `dirt` | Paths, patches | 10% |
| `garden_plot` | Cultivated areas | 3% |
| `stone_path` | Formal paths | 2% |

**Occupants - Trees** (sparse)
```python
trees_meadow = {
    "tree_oak": 2,
    "tree_fruit": 3,
    "tree_dead": 1,
}
# Density: 15-25 per zone
```

**Occupants - Plants** (heavy)
```python
plants_meadow = {
    "flower_red": 3,
    "flower_yellow": 3,
    "flower_blue": 2,
    "flower_wild": 4,
    "sunflower": 2,
    "tall_grass": 5,
    "bush": 3,
}
# Density: 200-400 per zone
```

**Occupants - Other**
```python
other_meadow = {
    "rock_small": 2,
    "mushroom_red": 1,
}
# Density: 20-40 per zone
```

**Features**
- Beehives near flower clusters
- Beekeeper's cottage (bee_meadow only)
- Butterfly specimen displays (butterfly_fields only)
- Gentle flower gradients (red->yellow->blue)

**Avoid**
- Dense tree clusters
- Swamp tiles
- Cave elements
- Large rocks

---

### Forest (`forest`)

Used for: `millipede_forest_01`

**Ground Tiles**
| Tile | Usage | Weight |
|------|-------|--------|
| `grass` | Primary base | 60% |
| `dirt` | Under trees, paths | 35% |
| `mud` | Damp areas | 5% |

**Occupants - Trees** (dense)
```python
trees_forest = {
    "tree_oak": 4,
    "tree_pine": 5,
    "tree_dead": 1,
    "tree_palm": 0,  # Not in forest
}
# Density: 150-200 per zone
```

**Occupants - Plants**
```python
plants_forest = {
    "bush": 5,
    "tall_grass": 3,
    "flower_wild": 1,
    "reeds": 0,
}
# Density: 100-150 per zone
```

**Occupants - Forest Floor**
```python
floor_forest = {
    "mushroom_red": 4,
    "mushroom_glow": 2,
    "rock_small": 2,
    "bone_pile": 1,
}
# Density: 50-80 per zone
```

**Features**
- Dense tree clusters with clearings
- Fallen logs and stumps
- Mushroom rings (circular patterns)
- Ranger station hub
- Millipede hiding spots (under logs)

**Avoid**
- Open meadow areas
- Cultivated plants
- Water features (except small streams)
- Desert elements

---

### Village (`village`)

Used for: `village_21`

**Ground Tiles**
| Tile | Usage | Weight |
|------|-------|--------|
| `grass` | Yards, edges | 50% |
| `dirt` | Unpaved areas | 20% |
| `stone_path` | Roads, squares | 25% |
| `garden_plot` | Player farms | 5% |

**Occupants - Trees** (decorative)
```python
trees_village = {
    "tree_oak": 3,
    "tree_fruit": 4,
    "tree_pine": 1,
}
# Density: 30-50 per zone, avoid center
```

**Occupants - Plants**
```python
plants_village = {
    "flower_red": 2,
    "flower_yellow": 2,
    "flower_blue": 2,
    "bush": 3,
    "sunflower": 1,
}
# Density: 50-80 per zone
```

**Occupants - Structures** (placed, not scattered)
```python
structures_village = [
    "well",           # Center
    "signpost",       # Near center
    "workbench",      # Starter crafting
    "chest",          # Storage
    "fence_wood",     # Property boundaries
    "torch",          # Lighting
]
```

**Buildings**
- Player cottage (northeast quadrant)
- NPC cottages (2-3 around edges)
- Market stall area
- Fishing dock (if near water)

**Features**
- Central square with well
- Cross-pattern main roads
- Fenced garden plots
- Starting equipment (workbench, chest)
- Tutorial signposts

**Avoid**
- Dangerous creatures
- Dense wilderness
- Cave elements
- Swamp tiles

---

### Thicket (`thicket`)

Used for: `wasp_thicket_22`

**Ground Tiles**
| Tile | Usage | Weight |
|------|-------|--------|
| `grass` | Primary | 50% |
| `dirt` | Paths, bare | 30% |
| `mud` | Wet areas | 15% |
| `water_shallow` | Streams | 5% |

**Occupants - Trees**
```python
trees_thicket = {
    "tree_dead": 4,
    "tree_oak": 2,
    "tree_pine": 1,
}
# Density: 40-60 per zone
```

**Occupants - Plants** (overgrown)
```python
plants_thicket = {
    "bush": 6,
    "tall_grass": 8,
    "reeds": 3,
    "flower_wild": 2,
}
# Density: 250-350 per zone (dense!)
```

**Occupants - Other**
```python
other_thicket = {
    "rock_small": 2,
    "mushroom_red": 2,
    "bone_pile": 1,
}
# Density: 30-50 per zone
```

**Features**
- Abandoned shack (ruined building)
- Wasp nests (visual markers)
- Overgrown paths (narrow dirt trails)
- Warning signs
- Dense undergrowth

**Avoid**
- Open clearings
- Cultivated gardens
- Friendly structures
- Bright flowers

---

### Swamp (`swamp`)

Used for: `shallow_swamp_23`, `deep_swamp_13`

**Ground Tiles**
| Tile | Usage | Weight |
|------|-------|--------|
| `mud` | Primary | 45% |
| `water_shallow` | Pools, streams | 30% |
| `water_deep` | Deep pools | 10% |
| `grass` | Dry islands | 10% |
| `dirt` | Raised paths | 5% |

**Occupants - Trees**
```python
trees_swamp = {
    "tree_dead": 5,
    "tree_palm": 2,  # Swamp palms
    "tree_oak": 1,
}
# Density: 30-50 per zone
```

**Occupants - Plants**
```python
plants_swamp = {
    "reeds": 6,
    "tall_grass": 4,
    "mushroom_glow": 3,
    "mushroom_red": 2,
    "flower_wild": 1,
}
# Density: 150-200 per zone
```

**Occupants - Other**
```python
other_swamp = {
    "rock_small": 1,
    "bone_pile": 3,
}
# Density: 40-60 per zone
```

**Features**
- Raised wooden walkways
- Fishing platforms
- Stilted huts
- Fog effects (visual only)
- Bioluminescent mushrooms (deep_swamp)

**Avoid**
- Stone paths
- Bright flowers
- Dense tree clusters
- Cave elements

---

### Rocky (`rocky`)

Used for: `scorpion_rocks_12`

**Ground Tiles**
| Tile | Usage | Weight |
|------|-------|--------|
| `sand` | Primary | 50% |
| `dirt` | Packed earth | 25% |
| `stone_path` | Natural stone | 20% |
| `grass` | Sparse patches | 5% |

**Occupants - Rocks** (heavy)
```python
rocks_rocky = {
    "rock_large": 4,
    "rock_small": 6,
    "stalagmite": 2,  # Surface formations
    "crystal_small": 1,
}
# Density: 100-150 per zone
```

**Occupants - Plants** (sparse)
```python
plants_rocky = {
    "bush": 2,
    "tall_grass": 1,
    "flower_wild": 1,
}
# Density: 30-50 per zone
```

**Occupants - Trees** (very sparse)
```python
trees_rocky = {
    "tree_dead": 3,
    "tree_pine": 1,
}
# Density: 10-20 per zone
```

**Features**
- Cave entrances (visual, connect to underground)
- Mining camp hub
- Ore veins visible on surface
- Scorpion dens (rock clusters)

**Avoid**
- Lush vegetation
- Water features
- Flowers
- Dense forests

---

### Farmland (`farmland`)

Used for: `locust_farmland_00`

**Ground Tiles**
| Tile | Usage | Weight |
|------|-------|--------|
| `dirt` | Primary (fields) | 50% |
| `grass` | Field edges | 30% |
| `garden_plot` | Cultivated | 15% |
| `stone_path` | Farm roads | 5% |

**Occupants - Crops** (in garden_plot)
```python
crops_farmland = {
    "flower_yellow": 3,  # Sunflowers as crops
    "sunflower": 5,
    "tall_grass": 2,     # Wheat-like
}
# Density: In designated farm areas only
```

**Occupants - Trees** (field edges)
```python
trees_farmland = {
    "tree_oak": 2,
    "tree_fruit": 3,
    "tree_dead": 2,      # Locust damage
}
# Density: 20-30 per zone
```

**Occupants - Farm Debris**
```python
debris_farmland = {
    "rock_small": 2,
    "bush": 1,
    "bone_pile": 1,      # Old livestock
}
# Density: 40-60 per zone
```

**Features**
- Ruined farmhouse hub
- Destroyed crop fields
- Broken fences
- Locust swarm damage visible
- Signs of devastation

**Avoid**
- Thriving crops (locusts ate them)
- Pristine buildings
- Dense forests
- Water features

---

## Underground Biomes

### Cave (`cave`)

Used for: `centipede_cavern_30`, `underground_passages_31`

**Ground Tiles**
| Tile | Usage | Weight |
|------|-------|--------|
| `cave_floor` | Primary | 85% |
| `stone_floor` | Cleared areas | 10% |
| `water_shallow` | Pools | 5% |

**Occupants - Formations**
```python
formations_cave = {
    "stalagmite": 5,
    "crystal_small": 3,
    "crystal_large": 1,
    "rock_small": 4,
    "rock_large": 2,
}
# Density: 80-120 per zone
```

**Occupants - Cave Life**
```python
life_cave = {
    "mushroom_glow": 4,
    "mushroom_red": 2,
    "bone_pile": 3,
}
# Density: 50-80 per zone
```

**Features**
- Large caverns (centipede_cavern)
- Narrow tunnels (passages)
- Ore veins in walls (visual)
- Underground camps
- Glowworm clusters

**Avoid**
- Surface plants
- Trees
- Flowers
- Bright lighting areas

---

### Cave Water (`cave_water`)

Used for: `underground_river_32`, `underground_river_42`, `deep_river_52`

**Ground Tiles**
| Tile | Usage | Weight |
|------|-------|--------|
| `cave_floor` | Banks | 40% |
| `water_shallow` | River edges | 25% |
| `water_deep` | River center | 30% |
| `sand` | Beaches | 5% |

**Occupants - Formations**
```python
formations_cave_water = {
    "stalagmite": 3,
    "crystal_small": 4,
    "crystal_large": 2,
    "rock_small": 3,
}
# Density: 50-70 per zone
```

**Occupants - Aquatic**
```python
aquatic_cave = {
    "reeds": 3,          # Cave reeds
    "mushroom_glow": 5,  # Light sources
    "bone_pile": 2,
}
# Density: 60-80 per zone
```

**Features**
- Underground river (wide)
- Waterfall at north (Row 3)
- Underground lake (Row 5)
- Fishing platforms
- Bioluminescent lighting

**Avoid**
- Dry cave elements
- Surface plants
- Flowers

---

### Ant Colony (`ant_colony`)

Used for: `deadly_ants_33`, `deadly_ants_43`, `ant_queen_53`

**Ground Tiles**
| Tile | Usage | Weight |
|------|-------|--------|
| `cave_floor` | Primary | 60% |
| `dirt` | Tunnels | 35% |
| `mud` | Damp areas | 5% |

**Occupants - Ant Structures**
```python
ant_structures = {
    "ant_mound": 4,
    "rock_small": 2,
    "bone_pile": 3,
}
# Density: 40-60 per zone
```

**Occupants - Tunnel Elements**
```python
tunnel_elements = {
    "mushroom_red": 2,
    "mushroom_glow": 3,
    "stalagmite": 1,
}
# Density: 30-50 per zone
```

**Features**
- Organized tunnel grid
- Ant mound clusters
- Egg chambers (visual)
- Food storage areas
- Queen chamber (Row 5 only)

**Avoid**
- Random layouts (ants are organized)
- Water features
- Surface elements

---

## Difficulty Modifiers

### Easy Zones
- More open space
- Fewer obstacles
- Clear paths
- Friendly hub structures
- Abundant resources

### Medium Zones
- Moderate obstacle density
- Some narrow passages
- Resources require searching
- Some dangerous areas

### Hard Zones
- Dense obstacles
- Limited visibility (tall grass, rocks)
- Sparse resources
- Many dangerous areas
- Difficult terrain (mud, water)

### Extra Hard / Boss Zones
- Extreme obstacle density
- Maze-like layouts
- Very sparse resources
- Constant danger
- Unique boss arena features

---

## Weighted Scatter Examples

### Meadow Zone (Easy)
```python
# Trees (sparse, decorative)
builder.scatter_weighted(trees_meadow, count=20)

# Plants (heavy flowering)
builder.scatter_weighted(plants_meadow, count=300, min_spacing=2)

# Rocks (occasional)
builder.scatter_weighted(other_meadow, count=25)
```

### Forest Zone (Hard)
```python
# Trees (dense coverage)
builder.scatter_weighted(trees_forest, count=180, min_spacing=3)

# Undergrowth
builder.scatter_weighted(plants_forest, count=120)

# Forest floor details
builder.scatter_weighted(floor_forest, count=60)
```

### Cave Zone (Medium)
```python
# Rock formations
builder.scatter_weighted(formations_cave, count=100, min_spacing=2)

# Cave life
builder.scatter_weighted(life_cave, count=60)
```

---

## Color/Theme Guidelines

### Surface Themes

| Biome | Primary Colors | Mood |
|-------|---------------|------|
| Meadow | Green, Yellow, Blue | Bright, cheerful |
| Forest | Dark green, Brown | Dense, mysterious |
| Village | Green, Brown, Gray | Homey, safe |
| Thicket | Brown, Gray, Dull green | Overgrown, dangerous |
| Swamp | Dark green, Brown, Gray | Murky, eerie |
| Rocky | Brown, Gray, Orange | Harsh, barren |
| Farmland | Brown, Yellow, Dead green | Devastated, sad |

### Underground Themes

| Biome | Primary Colors | Mood |
|-------|---------------|------|
| Cave | Gray, Brown, Blue glow | Dark, mysterious |
| Cave Water | Blue, Gray, Cyan glow | Wet, ethereal |
| Ant Colony | Brown, Red, Orange | Organized, threatening |

---

## Transition Zones

When zones meet, blend palettes at edges:

```python
# Forest meeting meadow (5 cell transition)
for x in range(507, 512):
    # Gradually reduce tree density
    if random.random() < (512 - x) / 10:
        builder.place_occupant(x, y, "tree_oak")
    # Increase flower density
    if random.random() < (x - 507) / 5:
        builder.place_occupant(x, y, "flower_wild")
```

---

## Quick Reference

| Biome | Ground | Trees | Plants | Special |
|-------|--------|-------|--------|---------|
| meadow | grass | sparse | flowers heavy | beehives |
| forest | grass/dirt | dense | bushes, mushrooms | logs, stumps |
| village | stone_path/grass | decorative | light | buildings |
| thicket | grass/mud | dead trees | overgrown | wasp nests |
| swamp | mud/water | dead trees | reeds | walkways |
| rocky | sand/stone | very sparse | minimal | rocks heavy |
| farmland | dirt | fruit/dead | crops (ruined) | farm debris |
| cave | cave_floor | none | mushrooms | formations |
| cave_water | cave_floor/water | none | reeds, glow mushrooms | river |
| ant_colony | cave_floor/dirt | none | minimal | ant mounds |
