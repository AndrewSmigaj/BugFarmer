# DEPRECATED - Item Database

> **This file is deprecated.** The authoritative data sources are now:
> - `nakama/data/occupants.json` - World occupants (trees, furniture, structures)
> - `nakama/data/tiles.json` - Ground tiles
> - `nakama/data/bugs.json` - Bug entities
> - `nakama/data/items.json` - Inventory items and tools
>
> Use `BugFarmer > Build TileDatabase` in Unity to populate TileDatabase from JSON.

---

*Original content below kept for historical reference:*

# Item Database for World Building

Structured for LLM parsing during world generation.

## Schema Reference

### Placeable Items
```
id | sprite_path | sprite_size | footprint | pivot | dir | category | status
```
- `id`: Unique identifier, used in world data
- `sprite_path`: Relative to Assets/
- `sprite_size`: WxH pixels
- `footprint`: WxH grid cells (collision area)
- `pivot`: `bc` (bottom-center), `c` (center)
- `dir`: Direction support:
  - `0` = Fixed (no rotation)
  - `4` = 4-way rotation (N/S/E/W)
  - `2h` = 2-way horizontal (E/W)
  - `2v` = 2-way vertical (N/S)
- `category`: Grouping for generation
- `status`: DONE / EXISTS / MISSING

### Direction Values (from backend entities.Direction)
```
0 = Down/South (facing camera, default)
1 = Left/West
2 = Right/East
3 = Up/North
```

### World Layers
```
1. Ground Layer: Flat 16x16 terrain tiles (grass, dirt, floors)
2. Blocks Layer: 3D breakable cubes (16x20) sitting ON ground (dirt_block, stone_block, ores)
3. Occupants Layer: Objects placed on ground (trees, furniture, walls)
```

### World Data Format
For non-rotatable items: `"tree_oak"`
For rotatable items: `{"id": "bookshelf", "dir": 2}`

### Placement Math
Given grid position (gx, gy), footprint (fw, fh), and pivot:

**bc (bottom-center):** Tall objects, sprite above footprint
- Sprite position: `((gx + fw/2) * 16, gy * 16)`
- Sprite draws upward from anchor

**c (center):** Flat objects, sprite centered on footprint
- Sprite position: `((gx + fw/2) * 16, (gy + fh/2) * 16)`

### Y-Sort Order
- Sort by footprint bottom Y (ascending)
- Player walks behind objects with higher Y

---

## TERRAIN TILES

Ground layer. Always 1x1 footprint. Tileable. 16x16 flat tiles.

| id | sprite_path | sprite_size | footprint | pivot | dir | status |
|----|-------------|-------------|-----------|-------|-----|--------|
| grass | Sprites/Terrain/grass.png | 16x16 | 1x1 | c | 0 | DONE |
| dirt | Sprites/Terrain/dirt.png | 16x16 | 1x1 | c | 0 | DONE |
| stone_path | Sprites/Terrain/stone_path.png | 16x16 | 1x1 | c | 0 | DONE |
| water_shallow | Sprites/Terrain/water_shallow.png | 16x16 | 1x1 | c | 0 | DONE |
| water_deep | Sprites/Terrain/water_deep.png | 16x16 | 1x1 | c | 0 | DONE |
| cave_floor | Sprites/Terrain/cave_floor.png | 16x16 | 1x1 | c | 0 | DONE |
| mud | Sprites/Terrain/mud.png | 16x16 | 1x1 | c | 0 | DONE |
| sand | Sprites/Terrain/sand.png | 16x16 | 1x1 | c | 0 | DONE |
| rock | Sprites/Terrain/rock.png | 16x16 | 1x1 | c | 0 | EXISTS |
| rock_cracked | Sprites/Terrain/rock_cracked.png | 16x16 | 1x1 | c | 0 | EXISTS |
| wood_floor | Sprites/Terrain/wood_floor.png | 16x16 | 1x1 | c | 0 | DONE |
| stone_floor | Sprites/Terrain/stone_floor.png | 16x16 | 1x1 | c | 0 | DONE |
| garden_plot | Sprites/Terrain/garden_plot.png | 16x16 | 1x1 | c | 0 | DONE |

---

## BLOCKS

3D cube-like objects (Minecraft-style) that sit ON ground. Breakable for resources.
16x20 sprites showing top face (rows 0-11) + front face (rows 12-19) from 45-degree perspective.

| id | sprite_path | sprite_size | footprint | pivot | dir | status |
|----|-------------|-------------|-----------|-------|-----|--------|
| dirt_block | Sprites/Blocks/dirt_block.png | 16x20 | 1x1 | bc | 0 | DONE |
| stone_block | Sprites/Blocks/stone_block.png | 16x20 | 1x1 | bc | 0 | DONE |
| clay_block | Sprites/Blocks/clay_block.png | 16x20 | 1x1 | bc | 0 | DONE |
| ore_coal_block | Sprites/Blocks/ore_coal_block.png | 16x20 | 1x1 | bc | 0 | DONE |
| ore_copper_block | Sprites/Blocks/ore_copper_block.png | 16x20 | 1x1 | bc | 0 | DONE |
| ore_iron_block | Sprites/Blocks/ore_iron_block.png | 16x20 | 1x1 | bc | 0 | DONE |
| ore_silver_block | Sprites/Blocks/ore_silver_block.png | 16x20 | 1x1 | bc | 0 | DONE |
| ore_gold_block | Sprites/Blocks/ore_gold_block.png | 16x20 | 1x1 | bc | 0 | DONE |
| ore_platinum_block | Sprites/Blocks/ore_platinum_block.png | 16x20 | 1x1 | bc | 0 | DONE |
| ore_diamond_block | Sprites/Blocks/ore_diamond_block.png | 16x20 | 1x1 | bc | 0 | DONE |

---

## NATURAL OBJECTS

Generated at design time. Not player-placeable (except bush).

| id | sprite_path | sprite_size | footprint | pivot | dir | status |
|----|-------------|-------------|-----------|-------|-----|--------|
| tree_oak | Sprites/Objects/tree_oak.png | 32x48 | 2x2 | bc | 0 | DONE |
| tree_pine | Sprites/Objects/tree_pine.png | 32x52 | 2x2 | bc | 0 | DONE |
| tree_dead | Sprites/Objects/tree_dead.png | 16x32 | 1x1 | bc | 0 | DONE |
| tree_palm | Sprites/Objects/tree_palm.png | 32x48 | 2x2 | bc | 0 | DONE |
| tree_fruit | Sprites/Objects/tree_fruit.png | 32x44 | 2x2 | bc | 0 | DONE |
| bush | Sprites/Objects/bush.png | 16x16 | 1x1 | c | 0 | DONE |
| tall_grass | Sprites/Objects/tall_grass.png | 16x20 | 1x1 | bc | 0 | DONE |
| rock_small | Sprites/Objects/rock_small.png | 16x16 | 1x1 | c | 0 | DONE |
| rock_large | Sprites/Objects/rock_large.png | 32x32 | 2x2 | c | 0 | DONE |
| reeds | Sprites/Objects/reeds.png | 16x24 | 1x1 | bc | 0 | DONE |
| mushroom_red | Sprites/Objects/mushroom_red.png | 16x16 | 1x1 | bc | 0 | DONE |
| mushroom_glow | Sprites/Objects/mushroom_glow.png | 16x16 | 1x1 | bc | 0 | DONE |
| flower_wild | Sprites/Objects/flower_wild.png | 16x16 | 1x1 | c | 0 | DONE |
| flower_red | Sprites/Objects/flower_red.png | 16x16 | 1x1 | c | 0 | DONE |
| flower_blue | Sprites/Objects/flower_blue.png | 16x16 | 1x1 | c | 0 | DONE |
| flower_yellow | Sprites/Objects/flower_yellow.png | 16x16 | 1x1 | c | 0 | DONE |
| sunflower | Sprites/Objects/sunflower.png | 16x24 | 1x1 | bc | 0 | DONE |
| crystal_small | Sprites/Objects/crystal_small.png | 16x20 | 1x1 | bc | 0 | DONE |
| crystal_large | Sprites/Objects/crystal_large.png | 32x28 | 2x2 | bc | 0 | DONE |
| stalagmite | Sprites/Objects/stalagmite.png | 16x24 | 1x1 | bc | 0 | DONE |
| bone_pile | Sprites/Objects/bone_pile.png | 16x12 | 1x1 | c | 0 | DONE |
| ant_mound | Sprites/Objects/ant_mound.png | 32x24 | 2x2 | bc | 0 | DONE |

---

## FENCES

Tileable. Blocks bugs not players. 4-way for corner posts.

| id | sprite_path | sprite_size | footprint | pivot | dir | status |
|----|-------------|-------------|-----------|-------|-----|--------|
| fence_wood | Sprites/Buildings/fence_wood.png | 16x20 | 1x1 | bc | 2h | DONE |
| fence_stone | Sprites/Buildings/fence_stone.png | 16x20 | 1x1 | bc | 2h | DONE |
| fence_iron | Sprites/Buildings/fence_iron.png | 16x20 | 1x1 | bc | 2h | DONE |
| fence_electric | Sprites/Buildings/fence_electric.png | 16x20 | 1x1 | bc | 2h | DONE |
| gate_wood | Sprites/Buildings/gate_wood.png | 16x20 | 1x1 | bc | 2h | DONE |
| gate_iron | Sprites/Buildings/gate_iron.png | 16x20 | 1x1 | bc | 2h | DONE |
| fence_corner_wood | Sprites/Buildings/fence_corner_wood.png | 16x20 | 1x1 | bc | 4 | MISSING |

---

## WALLS

Solid barriers. Tileable.

| id | sprite_path | sprite_size | footprint | pivot | dir | status |
|----|-------------|-------------|-----------|-------|-----|--------|
| wall_wood | Sprites/Buildings/wall_wood.png | 16x18 | 1x1 | bc | 2h | DONE |
| wall_stone | Sprites/Buildings/wall_stone.png | 16x18 | 1x1 | bc | 2h | DONE |
| wall_brick | Sprites/Buildings/wall_brick.png | 16x18 | 1x1 | bc | 2h | DONE |

---

## DOORS

1x2 footprint. Toggleable (open/closed state). Front faces direction.

| id | sprite_path | sprite_size | footprint | pivot | dir | status |
|----|-------------|-------------|-----------|-------|-----|--------|
| door_wood | Sprites/Buildings/door_wood.png | 16x24 | 1x2 | bc | 4 | DONE |
| door_iron | Sprites/Buildings/door_iron.png | 16x24 | 1x2 | bc | 4 | DONE |

---

## CRAFTING STATIONS

Player-placed. Front faces direction for interaction.

| id | sprite_path | sprite_size | footprint | pivot | dir | status |
|----|-------------|-------------|-----------|-------|-----|--------|
| workbench | Sprites/Furniture/workbench.png | 32x20 | 2x1 | bc | 4 | DONE |
| furnace | Sprites/Furniture/furnace.png | 32x28 | 2x2 | bc | 4 | DONE |
| anvil | Sprites/Furniture/anvil.png | 32x20 | 2x1 | bc | 4 | DONE |
| forge | Sprites/Furniture/forge.png | 32x32 | 2x2 | bc | 4 | DONE |
| loom | Sprites/Furniture/loom.png | 32x28 | 2x2 | bc | 4 | MISSING |
| cooking_pot | Sprites/Furniture/cooking_pot.png | 32x20 | 2x1 | bc | 4 | MISSING |
| cauldron | Sprites/Furniture/cauldron.png | 32x28 | 2x2 | bc | 4 | MISSING |
| sawmill | Sprites/Furniture/sawmill.png | 48x28 | 3x2 | bc | 4 | MISSING |
| stonecutter | Sprites/Furniture/stonecutter.png | 32x28 | 2x2 | bc | 4 | MISSING |

---

## FURNITURE - Tables

Can face any direction. Interaction from any side.

| id | sprite_path | sprite_size | footprint | pivot | dir | status |
|----|-------------|-------------|-----------|-------|-----|--------|
| table_wood | Sprites/Furniture/table_wood.png | 32x24 | 2x2 | bc | 0 | DONE |
| table_stone | Sprites/Furniture/table_stone.png | 32x24 | 2x2 | bc | 0 | DONE |

---

## FURNITURE - Seating

Chairs face a direction. Player sits facing that way.

| id | sprite_path | sprite_size | footprint | pivot | dir | status |
|----|-------------|-------------|-----------|-------|-----|--------|
| chair_wood | Sprites/Furniture/chair_wood.png | 16x20 | 1x1 | bc | 4 | DONE |
| chair_fancy | Sprites/Furniture/chair_fancy.png | 16x22 | 1x1 | bc | 4 | DONE |

---

## FURNITURE - Beds

2x4 footprint. Head faces direction.

| id | sprite_path | sprite_size | footprint | pivot | dir | status |
|----|-------------|-------------|-----------|-------|-----|--------|
| bed_basic | Sprites/Furniture/bed_basic.png | 32x48 | 2x4 | bc | 4 | DONE |
| bed_fancy | Sprites/Furniture/bed_fancy.png | 32x52 | 2x4 | bc | 4 | DONE |

---

## FURNITURE - Storage

Chests/shelves face a direction for access.

| id | sprite_path | sprite_size | footprint | pivot | dir | status |
|----|-------------|-------------|-----------|-------|-----|--------|
| chest_wood | Sprites/Furniture/chest_wood.png | 32x20 | 2x1 | bc | 4 | DONE |
| chest_iron | Sprites/Furniture/chest_iron.png | 32x20 | 2x1 | bc | 4 | DONE |
| barrel | Sprites/Furniture/barrel.png | 16x20 | 1x1 | bc | 0 | DONE |
| crate | Sprites/Furniture/crate.png | 16x18 | 1x1 | c | 0 | DONE |
| bookshelf | Sprites/Furniture/bookshelf.png | 16x24 | 1x2 | bc | 4 | DONE |
| shelf | Sprites/Furniture/shelf.png | 32x16 | 2x1 | bc | 4 | DONE |

---

## FURNITURE - Lighting

Most are symmetrical (no rotation).

| id | sprite_path | sprite_size | footprint | pivot | dir | status |
|----|-------------|-------------|-----------|-------|-----|--------|
| lamp_table | Sprites/Furniture/lamp_table.png | 16x20 | 1x1 | bc | 0 | DONE |
| lamp_floor | Sprites/Furniture/lamp_floor.png | 16x28 | 1x1 | bc | 0 | DONE |
| torch_wall | Sprites/Furniture/torch_wall.png | 16x16 | 1x1 | c | 4 | DONE |
| chandelier | Sprites/Furniture/chandelier.png | 32x24 | 2x2 | bc | 0 | DONE |
| fireplace | Sprites/Furniture/fireplace.png | 32x28 | 2x2 | bc | 4 | DONE |

---

## FURNITURE - Decorative

| id | sprite_path | sprite_size | footprint | pivot | dir | status |
|----|-------------|-------------|-----------|-------|-----|--------|
| rug_small | Sprites/Furniture/rug_small.png | 32x32 | 2x2 | c | 0 | DONE |
| rug_large | Sprites/Furniture/rug_large.png | 48x48 | 3x3 | c | 0 | DONE |
| painting_small | Sprites/Furniture/painting_small.png | 16x16 | 1x1 | c | 4 | DONE |
| painting_large | Sprites/Furniture/painting_large.png | 32x20 | 2x1 | c | 4 | DONE |
| statue_stone | Sprites/Furniture/statue_stone.png | 16x28 | 1x1 | bc | 4 | DONE |
| potted_plant | Sprites/Furniture/potted_plant.png | 16x20 | 1x1 | bc | 0 | DONE |
| banner | Sprites/Furniture/banner.png | 16x28 | 1x1 | bc | 4 | DONE |
| clock | Sprites/Furniture/clock.png | 16x16 | 1x1 | c | 4 | DONE |
| mirror | Sprites/Furniture/mirror.png | 16x24 | 1x2 | bc | 4 | DONE |

---

## BEEKEEPING

| id | sprite_path | sprite_size | footprint | pivot | dir | status |
|----|-------------|-------------|-----------|-------|-----|--------|
| beehive_basic | Sprites/Beekeeping/beehive_basic.png | 16x20 | 1x1 | bc | 4 | DONE |
| beehive_medium | Sprites/Beekeeping/beehive_medium.png | 32x24 | 2x1 | bc | 4 | DONE |
| beehive_large | Sprites/Beekeeping/beehive_large.png | 32x28 | 2x2 | bc | 4 | DONE |
| beehive_deluxe | Sprites/Beekeeping/beehive_deluxe.png | 32x32 | 2x2 | bc | 4 | DONE |
| honey_extractor | Sprites/Beekeeping/honey_extractor.png | 32x32 | 2x2 | bc | 4 | DONE |

---

## STRUCTURES

Hub and special structures.

| id | sprite_path | sprite_size | footprint | pivot | dir | status |
|----|-------------|-------------|-----------|-------|-----|--------|
| signpost | Sprites/Structures/signpost.png | 16x24 | 1x1 | bc | 4 | DONE |
| well | Sprites/Structures/well.png | 32x32 | 2x2 | bc | 0 | DONE |
| bridge_wood | Sprites/Structures/bridge_wood.png | 32x32 | 2x2 | c | 2h | DONE |
| bridge_stone | Sprites/Structures/bridge_stone.png | 32x32 | 2x2 | c | 2h | DONE |

---

## TOOLS (Inventory Only)

No footprint. Sprite shown in hotbar/hand.

| id | sprite_path | sprite_size | tier | status |
|----|-------------|-------------|------|--------|
| axe_wood | Sprites/Tools/axe_wood.png | 16x16 | 1 | DONE |
| axe_stone | Sprites/Tools/axe_stone.png | 16x16 | 2 | DONE |
| axe_copper | Sprites/Tools/axe_copper.png | 16x16 | 3 | DONE |
| axe_iron | Sprites/Tools/axe_iron.png | 16x16 | 4 | DONE |
| axe_steel | Sprites/Tools/axe_steel.png | 16x16 | 5 | DONE |
| axe_silver | Sprites/Tools/axe_silver.png | 16x16 | 6 | DONE |
| axe_gold | Sprites/Tools/axe_gold.png | 16x16 | 7 | DONE |
| axe_platinum | Sprites/Tools/axe_platinum.png | 16x16 | 8 | DONE |
| axe_diamond | Sprites/Tools/axe_diamond.png | 16x16 | 9 | DONE |
| pickaxe_wood | Sprites/Tools/pickaxe_wood.png | 16x16 | 1 | DONE |
| pickaxe_stone | Sprites/Tools/pickaxe_stone.png | 16x16 | 2 | DONE |
| pickaxe_copper | Sprites/Tools/pickaxe_copper.png | 16x16 | 3 | DONE |
| pickaxe_iron | Sprites/Tools/pickaxe_iron.png | 16x16 | 4 | DONE |
| pickaxe_steel | Sprites/Tools/pickaxe_steel.png | 16x16 | 5 | DONE |
| pickaxe_silver | Sprites/Tools/pickaxe_silver.png | 16x16 | 6 | DONE |
| pickaxe_gold | Sprites/Tools/pickaxe_gold.png | 16x16 | 7 | DONE |
| pickaxe_platinum | Sprites/Tools/pickaxe_platinum.png | 16x16 | 8 | DONE |
| pickaxe_diamond | Sprites/Tools/pickaxe_diamond.png | 16x16 | 9 | DONE |
| shovel_wood | Sprites/Tools/shovel_wood.png | 16x16 | 1 | DONE |
| shovel_stone | Sprites/Tools/shovel_stone.png | 16x16 | 2 | DONE |
| shovel_copper | Sprites/Tools/shovel_copper.png | 16x16 | 3 | DONE |
| shovel_iron | Sprites/Tools/shovel_iron.png | 16x16 | 4 | DONE |
| shovel_steel | Sprites/Tools/shovel_steel.png | 16x16 | 5 | DONE |
| shovel_silver | Sprites/Tools/shovel_silver.png | 16x16 | 6 | DONE |
| shovel_gold | Sprites/Tools/shovel_gold.png | 16x16 | 7 | DONE |
| shovel_platinum | Sprites/Tools/shovel_platinum.png | 16x16 | 8 | DONE |
| shovel_diamond | Sprites/Tools/shovel_diamond.png | 16x16 | 9 | DONE |
| hoe_wood | Sprites/Tools/hoe_wood.png | 16x16 | 1 | DONE |
| hoe_stone | Sprites/Tools/hoe_stone.png | 16x16 | 2 | DONE |
| hoe_copper | Sprites/Tools/hoe_copper.png | 16x16 | 3 | DONE |
| hoe_iron | Sprites/Tools/hoe_iron.png | 16x16 | 4 | DONE |
| hoe_steel | Sprites/Tools/hoe_steel.png | 16x16 | 5 | DONE |
| hoe_silver | Sprites/Tools/hoe_silver.png | 16x16 | 6 | DONE |
| hoe_gold | Sprites/Tools/hoe_gold.png | 16x16 | 7 | DONE |
| hoe_platinum | Sprites/Tools/hoe_platinum.png | 16x16 | 8 | DONE |
| hoe_diamond | Sprites/Tools/hoe_diamond.png | 16x16 | 9 | DONE |
| bugnet_wood | Sprites/Tools/bugnet_wood.png | 16x16 | 1 | DONE |
| bugnet_stone | Sprites/Tools/bugnet_stone.png | 16x16 | 2 | DONE |
| bugnet_copper | Sprites/Tools/bugnet_copper.png | 16x16 | 3 | DONE |
| bugnet_iron | Sprites/Tools/bugnet_iron.png | 16x16 | 4 | DONE |
| bugnet_steel | Sprites/Tools/bugnet_steel.png | 16x16 | 5 | DONE |
| bugnet_silver | Sprites/Tools/bugnet_silver.png | 16x16 | 6 | DONE |
| bugnet_gold | Sprites/Tools/bugnet_gold.png | 16x16 | 7 | DONE |
| bugnet_platinum | Sprites/Tools/bugnet_platinum.png | 16x16 | 8 | DONE |
| bugnet_diamond | Sprites/Tools/bugnet_diamond.png | 16x16 | 9 | DONE |

---

## BUGS

Free-moving entities. Spawn in zones. Sprite size only.

| id | sprite_path | sprite_size | zone | status |
|----|-------------|-------------|------|--------|
| ant_worker | Sprites/Bugs/ant_worker.png | 8x8 | Village | DONE |
| ant_queen | Sprites/Bugs/ant_queen.png | 32x32 | Ant Queen Chamber | DONE |
| honeybee | Sprites/Bugs/honeybee.png | 10x10 | Bee Meadow | DONE |
| bumblebee | Sprites/Bugs/bumblebee.png | 12x12 | Meadow | DONE |
| wasp_common | Sprites/Bugs/wasp_common.png | 12x12 | Wasp Thicket | DONE |
| hornet | Sprites/Bugs/hornet.png | 14x14 | Wasp Thicket | DONE |
| butterfly_common | Sprites/Bugs/butterfly_common.png | 16x16 | Butterfly Fields | DONE |
| butterfly_monarch | Sprites/Bugs/butterfly_monarch.png | 16x16 | Butterfly Fields | DONE |
| moth_common | Sprites/Bugs/moth_common.png | 14x14 | Butterfly Fields | DONE |
| beetle_common | Sprites/Bugs/beetle_common.png | 10x10 | Various | DONE |
| stag_beetle | Sprites/Bugs/stag_beetle.png | 14x14 | Millipede Forest | DONE |
| ladybug | Sprites/Bugs/ladybug.png | 10x10 | Village | DONE |
| fly_common | Sprites/Bugs/fly_common.png | 8x8 | Village | DONE |
| firefly | Sprites/Bugs/firefly.png | 8x8 | Butterfly Fields | DONE |
| dragonfly | Sprites/Bugs/dragonfly.png | 16x20 | Deep Swamp | DONE |
| grasshopper | Sprites/Bugs/grasshopper.png | 14x14 | Locust Farmland | DONE |
| locust | Sprites/Bugs/locust.png | 14x14 | Locust Farmland | DONE |
| cricket | Sprites/Bugs/cricket.png | 12x12 | Locust Farmland | DONE |
| millipede | Sprites/Bugs/millipede.png | 12x24 | Millipede Forest | DONE |
| centipede | Sprites/Bugs/centipede.png | 10x20 | Millipede Forest | DONE |
| giant_centipede | Sprites/Bugs/giant_centipede.png | 16x32 | Centipede Cavern | DONE |
| wolf_spider | Sprites/Bugs/wolf_spider.png | 16x16 | Spider Vale W | DONE |
| jumping_spider | Sprites/Bugs/jumping_spider.png | 10x10 | Spider Vale W | DONE |
| black_widow | Sprites/Bugs/black_widow.png | 14x14 | Spider Vale E | DONE |
| tarantula | Sprites/Bugs/tarantula.png | 24x24 | Spider Vale E | DONE |
| cave_spider | Sprites/Bugs/cave_spider.png | 12x12 | Underground | DONE |
| scorpion | Sprites/Bugs/scorpion.png | 14x14 | Scorpion Rocks | DONE |

---

## PLAYER SPRITES

Player character sprites. 32x48 pixels (2x3 cells). 4-direction sprites for movement.

| id | sprite_path | sprite_size | footprint | pivot | dir | status |
|----|-------------|-------------|-----------|-------|-----|--------|
| farmer_down | Sprites/Player/farmer_down.png | 32x48 | 2x3 | bc | 0 | DONE |
| farmer_up | Sprites/Player/farmer_up.png | 32x48 | 2x3 | bc | 3 | DONE |
| farmer_left | Sprites/Player/farmer_left.png | 32x48 | 2x3 | bc | 1 | DONE |
| farmer_right | Sprites/Player/farmer_right.png | 32x48 | 2x3 | bc | 2 | DONE |
| farmer_spritesheet | Sprites/Player/farmer_spritesheet.png | 128x48 | - | - | 4 | DONE |

---

## SUMMARY

| Category | Total | Done | Missing |
|----------|-------|------|---------|
| Terrain | 13 | 11 | 2 (EXISTS) |
| Blocks | 10 | 10 | 0 |
| Natural Objects | 22 | 22 | 0 |
| Fences | 7 | 6 | 1 |
| Walls | 3 | 3 | 0 |
| Doors | 2 | 2 | 0 |
| Crafting Stations | 9 | 4 | 5 |
| Furniture - Tables | 2 | 2 | 0 |
| Furniture - Seating | 2 | 2 | 0 |
| Furniture - Beds | 2 | 2 | 0 |
| Furniture - Storage | 7 | 7 | 0 |
| Furniture - Lighting | 5 | 5 | 0 |
| Furniture - Decorative | 9 | 9 | 0 |
| Beekeeping | 5 | 5 | 0 |
| Structures | 4 | 4 | 0 |
| Tools | 45 | 45 | 0 |
| Bugs | 27 | 27 | 0 |
| Player | 5 | 5 | 0 |

**Placeable sprites:** 102 listed, 94 done, 8 missing
**Inventory sprites:** 45 done
**Bug sprites:** 27 done
**Player sprites:** 5 done (farmer character + spritesheet)

---

## World Data Example

```json
{
  "chunk_x": 0,
  "chunk_y": 0,
  "ground": [
    ["grass", "grass", "dirt", "stone_path"],
    ["grass", "wood_floor", "wood_floor", "stone_path"],
    ["grass", "garden_plot", "garden_plot", "grass"],
    ["grass", "grass", "grass", "grass"]
  ],
  "blocks": [
    [null, null, null, null],
    [null, null, null, null],
    [null, null, null, "dirt_block"],
    [null, null, "stone_block", "ore_iron_block"]
  ],
  "occupants": [
    [null, null, "tree_oak", null],
    [null, "@", "@", "@"],
    [{"id": "bookshelf", "dir": 0}, {"id": "chair_wood", "dir": 2}, null, null],
    ["@", null, "rock_small", null]
  ]
}
```

Notes:
- `@` = Cell blocked by multi-cell occupant anchored elsewhere
- `"tree_oak"` = Fixed direction object (just ID string)
- `{"id": "bookshelf", "dir": 0}` = Rotatable object with direction
- Anchor cell is always bottom-left of footprint
- `ground` = flat terrain tiles (walk on these)
- `blocks` = 3D breakable cubes on top of ground (mine these)
- `occupants` = objects/furniture on ground (interact with these)
