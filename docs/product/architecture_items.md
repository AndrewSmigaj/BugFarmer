# Item Architecture

## Overview

All items in BugFarmer have a footprint (grid cells for placement) and a sprite size (visual pixels). The base grid unit is 16×16 pixels.

**Reference sizes:**
- Grid cell: 16×16 pixels
- Player: 48×32 pixels (3×2 cells) - bird's eye view, slightly higher angle
- Smallest bugs: 8×8 pixels (don't use grid)

**Perspective:** Top-down / bird's eye with slightly higher angle. Sprites show tops/backs of objects. Tall objects (trees, lamps) have foreshortened height but player walks behind them.

**Item properties:**
- **Footprint**: Cells the item occupies for collision/placement (W×H in grid cells)
- **Sprite**: Recommended visual size (W×H in pixels) - can exceed footprint
- Items with tall sprites: player walks behind them (tree, lamp post, etc.)

---

## 1. Basic Blocks

Ground tiles and raw materials. Footprint always 1×1.

| Item | Description | Footprint | Sprite | Drops From |
|------|-------------|-----------|--------|------------|
| dirt | Basic earth block | 1×1 | 16×16 | Mining dirt tiles |
| stone | Gray rock block | 1×1 | 16×16 | Mining stone, rocks |
| clay | Reddish clay block | 1×1 | 16×16 | Mining clay tiles |
| sand | Sandy block | 1×1 | 16×16 | Beaches, desert |
| gravel | Rocky debris | 1×1 | 16×16 | Mining, caves |
| mud | Wet earth block | 1×1 | 16×16 | Swamp areas |

### Ore Blocks

| Item | Description | Footprint | Sprite | Found In |
|------|-------------|-----------|--------|----------|
| copper_ore | Raw copper | 1×1 | 16×16 | Row 3-4 |
| coal | Black fuel ore | 1×1 | 16×16 | Row 3-5 |
| iron_ore | Raw iron | 1×1 | 16×16 | Row 3-5 |
| silver_ore | Raw silver | 1×1 | 16×16 | Row 4-5 |
| gold_ore | Raw gold | 1×1 | 16×16 | Row 4-5 |
| platinum_ore | Raw platinum | 1×1 | 16×16 | Row 5 |
| diamond | Precious gem | 1×1 | 16×16 | Row 5, rare |

### Processed Blocks

| Item | Description | Footprint | Sprite | Crafted From |
|------|-------------|-----------|--------|--------------|
| copper_bar | Smelted copper | 1×1 | 16×16 | copper_ore × 3 |
| iron_bar | Smelted iron | 1×1 | 16×16 | iron_ore × 3 |
| steel_bar | Iron-carbon alloy | 1×1 | 16×16 | iron_bar + coal |
| silver_bar | Smelted silver | 1×1 | 16×16 | silver_ore × 3 |
| gold_bar | Smelted gold | 1×1 | 16×16 | gold_ore × 3 |
| platinum_bar | Smelted platinum | 1×1 | 16×16 | platinum_ore × 3 |
| brick | Fired clay | 1×1 | 16×16 | clay × 2 |
| glass | Transparent block | 1×1 | 16×16 | sand × 2 |

---

## 2. Tools

Handheld items, no footprint (inventory only). Sprite shown in hotbar/hand.

### Axes (Wood harvesting)

| Item | Description | Sprite | Tier | Durability |
|------|-------------|--------|------|------------|
| axe_wood | Basic wood axe | 16×16 | 1 | 50 |
| axe_stone | Stone axe | 16×16 | 2 | 100 |
| axe_copper | Copper axe | 16×16 | 3 | 150 |
| axe_iron | Iron axe | 16×16 | 4 | 200 |
| axe_steel | Steel axe | 16×16 | 5 | 300 |
| axe_silver | Silver axe | 16×16 | 6 | 250 |
| axe_gold | Gold axe | 16×16 | 7 | 200 |
| axe_platinum | Platinum axe | 16×16 | 8 | 400 |
| axe_diamond | Diamond axe | 16×16 | 9 | 500 |

### Pickaxes (Mining)

| Item | Description | Sprite | Tier | Durability |
|------|-------------|--------|------|------------|
| pickaxe_wood | Basic pickaxe | 16×16 | 1 | 50 |
| pickaxe_stone | Stone pickaxe | 16×16 | 2 | 100 |
| pickaxe_copper | Copper pickaxe | 16×16 | 3 | 150 |
| pickaxe_iron | Iron pickaxe | 16×16 | 4 | 200 |
| pickaxe_steel | Steel pickaxe | 16×16 | 5 | 300 |
| pickaxe_silver | Silver pickaxe | 16×16 | 6 | 250 |
| pickaxe_gold | Gold pickaxe | 16×16 | 7 | 200 |
| pickaxe_platinum | Platinum pickaxe | 16×16 | 8 | 400 |
| pickaxe_diamond | Diamond pickaxe | 16×16 | 9 | 500 |

### Shovels (Dirt, clay, sand)

| Item | Description | Sprite | Tier | Durability |
|------|-------------|--------|------|------------|
| shovel_wood | Basic shovel | 16×16 | 1 | 50 |
| shovel_stone | Stone shovel | 16×16 | 2 | 100 |
| shovel_copper | Copper shovel | 16×16 | 3 | 150 |
| shovel_iron | Iron shovel | 16×16 | 4 | 200 |
| shovel_steel | Steel shovel | 16×16 | 5 | 300 |
| shovel_silver | Silver shovel | 16×16 | 6 | 250 |
| shovel_gold | Gold shovel | 16×16 | 7 | 200 |
| shovel_platinum | Platinum shovel | 16×16 | 8 | 400 |
| shovel_diamond | Diamond shovel | 16×16 | 9 | 500 |

### Hammers (Structures, furniture)

| Item | Description | Sprite | Tier | Durability |
|------|-------------|--------|------|------------|
| hammer_wood | Basic hammer | 16×16 | 1 | 50 |
| hammer_stone | Stone hammer | 16×16 | 2 | 100 |
| hammer_copper | Copper hammer | 16×16 | 3 | 150 |
| hammer_iron | Iron hammer | 16×16 | 4 | 200 |
| hammer_steel | Steel hammer | 16×16 | 5 | 300 |

---

## 3. Weapons

Combat items for dealing with aggressive bugs.

| Item | Description | Sprite | Tier | Damage | Range |
|------|-------------|--------|------|--------|-------|
| stick | Basic melee | 16×16 | 0 | 1 | 1 cell |
| sword_wood | Wooden sword | 16×16 | 1 | 2 | 1 cell |
| sword_stone | Stone sword | 16×16 | 2 | 3 | 1 cell |
| sword_copper | Copper sword | 16×16 | 3 | 4 | 1 cell |
| sword_iron | Iron sword | 16×16 | 4 | 5 | 1 cell |
| sword_steel | Steel sword | 16×16 | 5 | 7 | 1 cell |
| sword_silver | Silver sword | 16×16 | 6 | 6 | 1 cell |
| sword_gold | Gold sword | 16×16 | 7 | 5 | 1 cell |
| sword_platinum | Platinum sword | 16×16 | 8 | 8 | 1 cell |
| sword_diamond | Diamond sword | 16×16 | 9 | 10 | 1 cell |
| spear_wood | Wooden spear | 16×32 | 1 | 2 | 2 cells |
| spear_iron | Iron spear | 16×32 | 4 | 4 | 2 cells |

---

## 4. Nets & Catching

Bug catching equipment.

| Item | Description | Sprite | Tier | Catch Radius | Notes |
|------|-------------|--------|------|--------------|-------|
| net_basic | Starter net | 24×24 | 1 | 0.5 | Slow swing |
| net_wide | Wide net | 32×32 | 2 | 1.0 | Larger catch area |
| net_quick | Quick net | 24×24 | 2 | 0.5 | Fast swing |
| net_reinforced | Strong net | 24×24 | 3 | 0.75 | Won't break on hard bugs |
| net_master | Master net | 32×32 | 4 | 1.5 | Best all-around |
| jar_empty | Empty specimen jar | 16×16 | - | - | For caught bugs |
| jar_bug | Jar with bug | 16×16 | - | - | Contains 1 bug |
| magnifying_glass | Inspection tool | 16×16 | - | - | Learn bug conditions |

---

## 5. Construction & Crafting Stations

Placeable structures for crafting.

| Item | Description | Footprint | Sprite | Unlocks |
|------|-------------|-----------|--------|---------|
| workbench | Basic crafting | 2×1 | 32×20 | Basic recipes |
| furnace | Ore smelting | 2×2 | 32×28 | Bars from ore |
| anvil | Metalworking | 2×1 | 32×20 | Metal tools, weapons |
| forge | Advanced smelting | 2×2 | 32×32 | Steel, alloys |
| loom | Fiber crafting | 2×2 | 32×28 | Cloth, rope, nets |
| cooking_pot | Food prep | 2×1 | 32×20 | Cooked food |
| cauldron | Advanced cooking | 2×2 | 32×28 | Potions, repellents |
| sawmill | Wood processing | 3×2 | 48×28 | Planks, furniture |
| stonecutter | Stone shaping | 2×2 | 32×28 | Bricks, carved stone |

---

## 6. Health & Consumables

| Item | Description | Sprite | Effect |
|------|-------------|--------|--------|
| apple | Basic food | 16×16 | +10 HP |
| cooked_meat | Grilled meat | 16×16 | +25 HP |
| honey | Bee product | 16×16 | +15 HP, slow heal |
| mushroom | Cave fungus | 16×16 | +5 HP |
| cave_mushroom | Glowing fungus | 16×16 | +10 HP, night vision 30s |
| potion_health | Red potion | 16×16 | +50 HP instant |
| potion_speed | Blue potion | 16×16 | +speed 60s |
| antidote | Green potion | 16×16 | Cure poison |
| repellent_ant | Ant spray | 16×16 | Ants avoid you 120s |
| repellent_wasp | Wasp spray | 16×16 | Wasps avoid you 120s |

---

## 7. Decoration

Aesthetic items for player buildings.

| Item | Description | Footprint | Sprite | Notes |
|------|-------------|-----------|--------|-------|
| rug_small | Small floor rug | 2×2 | 32×32 | No collision |
| rug_large | Large floor rug | 3×3 | 48×48 | No collision |
| painting_small | Wall art | 1×1 | 16×16 | Wall mount |
| painting_large | Big wall art | 2×1 | 32×16 | Wall mount |
| statue_stone | Stone figure | 1×1 | 16×24 | Decorative |
| statue_bug | Bug sculpture | 1×1 | 16×24 | Unlocked per species |
| potted_plant | Indoor plant | 1×1 | 16×20 | Decorative |
| banner | Hanging banner | 1×1 | 16×24 | Wall mount |
| trophy_centipede | Centipede boss | 2×1 | 32×28 | Boss drop |
| trophy_ant_queen | Ant queen boss | 2×1 | 32×28 | Boss drop |

---

## 8. Beekeeping

Bee farming equipment.

| Item | Description | Footprint | Sprite | Capacity |
|------|-------------|-----------|--------|----------|
| beehive_basic | Starter hive | 1×1 | 16×20 | 1 swarm |
| beehive_medium | Medium hive | 2×1 | 32×24 | 2 swarms |
| beehive_large | Large hive | 2×2 | 32×28 | 3 swarms |
| beehive_deluxe | Best hive | 2×2 | 32×32 | 4 swarms, +honey |
| smoker | Calms bees | 16×16 | - | Tool, inventory |
| bee_suit | Protection | - | - | Armor slot |
| honey_extractor | Harvest honey | 2×2 | 32×32 | Auto-collect |
| royal_jelly | Rare bee product | 16×16 | - | Special crafting |
| beeswax | Wax product | 16×16 | - | Crafting material |

---

## 9. Fencing & Barriers

Bug containment and player structures.

| Item | Description | Footprint | Sprite | Blocks |
|------|-------------|-----------|--------|--------|
| fence_wood | Basic fence | 1×1 | 16×20 | Insects |
| fence_stone | Stone fence | 1×1 | 16×20 | Insects |
| fence_iron | Iron fence | 1×1 | 16×20 | Insects, strong |
| fence_electric | Powered fence | 1×1 | 16×20 | All bugs, zaps |
| gate_wood | Wooden gate | 1×1 | 16×20 | Toggle open/close |
| gate_iron | Iron gate | 1×1 | 16×20 | Toggle, stronger |
| wall_wood | Wooden wall | 1×1 | 16×18 | All movement |
| wall_stone | Stone wall | 1×1 | 16×18 | All movement |
| wall_brick | Brick wall | 1×1 | 16×18 | All movement |
| door_wood | Wooden door | 1×2 | 16×24 | Toggle |
| door_iron | Iron door | 1×2 | 16×24 | Toggle, stronger |
| barrier_bug | Bug-only barrier | 1×1 | 16×16 | Bugs not players |

---

## 10. Webbing & Spider Products

From spider farming or harvesting.

| Item | Description | Footprint | Sprite | Source |
|------|-------------|-----------|--------|--------|
| web | Spider web | 1×1 | 16×16 | Spiders, slows bugs |
| silk | Spider silk | - | 16×16 | Processed web |
| silk_thread | Refined silk | - | 16×16 | silk × 2 |
| silk_cloth | Woven silk | - | 16×16 | silk_thread × 4 |
| web_trap | Sticky trap | 1×1 | 16×16 | Catches small bugs |
| web_net | Silk net | 24×24 | - | Stronger net |
| rope_silk | Strong rope | - | 16×16 | Crafting material |

---

## 11. Insects

All bug species. Not grid-based. Sizes are sprite only.

### Easy Tier (Village, Bee Meadow, Tutorial)

| Species | Description | Sprite | Zone | Drops |
|---------|-------------|--------|------|-------|
| fly_common | Basic fly | 8×8 | Village | - |
| fly_fruit | Fruit fly | 6×6 | Village | - |
| ladybug | Red spotted | 10×10 | Village | luck_charm? |
| aphid | Tiny green | 4×4 | Village | - |
| pill_bug | Roly-poly | 8×8 | Village | chitin |
| ant_worker | Basic ant | 8×8 | Village | - |
| honeybee | Basic bee | 10×10 | Bee Meadow | honey (via hive) |
| mason_bee | Solitary bee | 10×10 | Bee Meadow | - |
| leafcutter_bee | Leaf carrier | 10×10 | Bee Meadow | - |
| sweat_bee | Small bee | 8×8 | Bee Meadow | - |

### Medium Tier

| Species | Description | Sprite | Zone | Drops |
|---------|-------------|--------|------|-------|
| butterfly_common | Basic butterfly | 16×16 | Butterfly Fields | wing_dust |
| butterfly_monarch | Orange butterfly | 16×16 | Butterfly Fields | wing_dust |
| moth_common | Basic moth | 14×14 | Butterfly Fields | wing_dust |
| firefly | Glowing bug | 8×8 | Butterfly Fields | glow_gland |
| cicada | Loud bug | 12×12 | Butterfly Fields | shell |
| bumblebee | Fuzzy bee | 12×12 | Meadow | honey, wax |
| wasp_common | Yellow jacket | 12×12 | Meadow, Wasp Thicket | stinger |
| carpenter_bee | Wood borer | 12×12 | Meadow | - |
| hornet | Large wasp | 14×14 | Meadow | stinger × 2 |
| paper_wasp | Nest builder | 12×12 | Wasp Thicket | paper |
| mud_dauber | Mud wasp | 12×12 | Wasp Thicket | mud |
| earwig | Pincer bug | 10×10 | Wasp Thicket | pincer |
| silverfish | Shiny crawler | 8×8 | Wasp Thicket | scales |

### Hard Tier

| Species | Description | Sprite | Zone | Drops |
|---------|-------------|--------|------|-------|
| locust | Swarming pest | 14×14 | Locust Farmland | chitin, leg |
| grasshopper | Jumping bug | 14×14 | Locust Farmland | leg |
| cricket | Chirping bug | 12×12 | Locust Farmland | leg |
| crop_beetle | Farm pest | 10×10 | Locust Farmland | shell |
| millipede_common | Many legs | 12×24 | Millipede Forest | leg × many |
| centipede_forest | Fast predator | 10×20 | Millipede Forest | leg, venom |
| bark_beetle | Tree borer | 8×8 | Millipede Forest | - |
| stag_beetle | Horned beetle | 14×14 | Millipede Forest | horn, shell |
| scorpion | Stinging | 14×14 | Scorpion Rocks | stinger, venom |
| tick | Blood sucker | 6×6 | Scorpion Rocks | - |
| harvestman | Daddy longlegs | 12×16 | Scorpion Rocks | leg |
| vinegaroon | Whip scorpion | 16×16 | Scorpion Rocks | acid |
| damselfly | Small dragonfly | 12×14 | Shallow Swamp | wing |
| pond_skater | Water walker | 10×10 | Shallow Swamp | - |
| whirligig | Spinning beetle | 8×8 | Shallow Swamp | - |
| leech | Blood sucker | 8×16 | Shallow Swamp | - |

### Extra Hard Tier

| Species | Description | Sprite | Zone | Drops |
|---------|-------------|--------|------|-------|
| orb_weaver | Web spinner | 14×14 | Spider Vale W | silk, venom |
| wolf_spider | Fast hunter | 16×16 | Spider Vale W | fang, silk |
| jumping_spider | Leaping | 10×10 | Spider Vale W | fang |
| centipede_hard | Armored | 12×24 | Spider Vale W | armor, venom |
| mosquito | Swarm pest | 8×8 | Deep Swamp | - |
| dragonfly | Fast flyer | 16×20 | Deep Swamp | wing × 2 |
| water_strider | Surface walker | 12×12 | Deep Swamp | - |
| giant_water_bug | Toe biter | 18×18 | Deep Swamp | pincer |

### Extra Extra Hard Tier

| Species | Description | Sprite | Zone | Drops |
|---------|-------------|--------|------|-------|
| black_widow | Deadly spider | 14×14 | Spider Vale E | venom_deadly, silk |
| tarantula | Giant spider | 24×24 | Spider Vale E | fang_large, silk |
| trapdoor_spider | Ambusher | 16×16 | Spider Vale E | silk, fang |
| giant_huntsman | Fast giant | 28×28 | Spider Vale E | fang_large × 2 |

### Underground - Rows 3-4

| Species | Description | Sprite | Zone | Drops |
|---------|-------------|--------|------|-------|
| giant_centipede | Cave predator | 16×32 | Centipede Cavern | leg × many, venom |
| cave_beetle | Blind beetle | 10×10 | Centipede Cavern | shell |
| glowworm | Bioluminescent | 8×16 | Centipede Cavern | glow_gland |
| camel_cricket | Cave hopper | 12×12 | Centipede Cavern | leg |
| cave_spider | Web in dark | 12×12 | Underground Passages | silk |
| blind_beetle | No eyes | 8×8 | Underground Passages | - |
| mole_cricket | Burrowing | 12×12 | Underground Passages | claw |
| springtail | Tiny jumper | 4×4 | Underground Passages | - |
| cave_crayfish | Aquatic | 14×14 | Underground River | claw, shell |
| water_beetle | Diving beetle | 10×10 | Underground River | shell |
| aquatic_larva | Bug baby | 6×10 | Underground River | - |
| bullet_ant | Painful sting | 10×10 | Ant Colony | stinger_bullet |
| soldier_ant | Guard ant | 12×12 | Ant Colony | mandible |
| army_ant | Swarm ant | 8×8 | Ant Colony | - |
| fire_ant | Burning sting | 8×8 | Ant Colony | stinger_fire |

### Underground - Row 5 (Deep)

| Species | Description | Sprite | Zone | Drops |
|---------|-------------|--------|------|-------|
| giant_cave_centipede | Boss tier | 24×48 | Centipede Depths | leg_giant, venom_potent |
| crystal_beetle | Gem shell | 12×12 | Centipede Depths | crystal_shard |
| bioluminescent_worm | Glowing | 8×24 | Centipede Depths | glow_gland × 2 |
| cave_scorpion | Underground | 16×16 | Centipede Depths | venom, stinger |
| albino_centipede | Pale predator | 14×28 | Deep Passages | - |
| deep_cave_spider | Ancient | 14×14 | Deep Passages | silk_ancient |
| rock_borer | Stone eater | 12×12 | Deep Passages | stone_dust |
| giant_cave_crayfish | Boss aquatic | 20×20 | Deep River | claw_giant, shell |
| cave_eel | Slippery | 8×32 | Deep River | - |
| water_centipede | Aquatic | 12×24 | Deep River | - |
| ant_queen | Colony boss | 32×32 | Ant Queen Chamber | royal_jelly, crown |
| royal_guard | Elite ant | 14×14 | Ant Queen Chamber | mandible_royal |
| winged_ant | Flying ant | 10×12 | Ant Queen Chamber | wing |

---

## 12. Containers

Storage items.

| Item | Description | Footprint | Sprite | Slots |
|------|-------------|-----------|--------|-------|
| chest_wood | Basic storage | 2×1 | 32×20 | 20 |
| chest_iron | Better storage | 2×1 | 32×20 | 30 |
| chest_large | Big storage | 2×2 | 32×28 | 50 |
| barrel | Liquid/bulk | 1×1 | 16×20 | 10 |
| crate | Stackable | 1×1 | 16×16 | 10 |
| bag | Portable | - | 16×16 | 5, carryable |
| backpack | Worn storage | - | - | +10 inventory |

---

## 13. Furniture

Indoor structures.

| Item | Description | Footprint | Sprite | Function |
|------|-------------|-----------|--------|----------|
| table_wood | Basic table | 2×2 | 32×24 | Surface |
| table_stone | Stone table | 2×2 | 32×24 | Surface |
| chair_wood | Basic chair | 1×1 | 16×20 | Sit |
| chair_fancy | Nice chair | 1×1 | 16×20 | Sit |
| bed_basic | Starter bed | 2×4 | 32×48 | Set spawn |
| bed_fancy | Nice bed | 2×4 | 32×48 | Set spawn, +regen |
| shelf | Wall storage | 2×1 | 32×16 | Display items |
| bookshelf | Book storage | 1×2 | 16×24 | Decoration |
| lamp_table | Light source | 1×1 | 16×20 | Light radius 3 |
| lamp_floor | Tall lamp | 1×1 | 16×24 | Light radius 4 |
| torch | Wall light | 1×1 | 16×16 | Light radius 2 |
| chandelier | Ceiling light | 2×2 | 32×28 | Light radius 6 |
| fireplace | Hearth | 2×2 | 32×28 | Light, warmth |
| carpet | Floor cover | 2×2 | 32×32 | No collision |
| clock | Time display | 1×1 | 16×16 | Shows time |
| mirror | Reflection | 1×2 | 16×24 | Character view |

---

## 14. Plants

Growable and decorative plants.

### Crops

| Item | Description | Footprint | Sprite (grown) | Harvest |
|------|-------------|-----------|----------------|---------|
| wheat | Grain crop | 1×1 | 16×20 | wheat × 2-3 |
| carrot | Root veggie | 1×1 | 16×16 | carrot × 1-2 |
| potato | Root veggie | 1×1 | 16×16 | potato × 1-3 |
| tomato | Vine fruit | 1×1 | 16×20 | tomato × 1-2 |
| corn | Tall grain | 1×1 | 16×24 | corn × 1-2 |
| pumpkin | Large fruit | 2×2 | 32×24 | pumpkin × 1 |
| berry_bush | Berry plant | 1×1 | 16×20 | berries × 3-5 |

### Flowers (Bee attractants)

| Item | Description | Footprint | Sprite | Effect |
|------|-------------|-----------|--------|--------|
| flower_wild | Basic flower | 1×1 | 16×16 | Attracts bees |
| flower_red | Red bloom | 1×1 | 16×16 | Attracts bees |
| flower_blue | Blue bloom | 1×1 | 16×16 | Attracts butterflies |
| flower_yellow | Yellow bloom | 1×1 | 16×16 | Attracts bees ++ |
| sunflower | Tall yellow | 1×1 | 16×24 | Attracts bees +++ |
| lavender | Purple herb | 1×1 | 16×18 | Repels wasps |

### Trees

| Item | Description | Footprint | Sprite | Drops |
|------|-------------|-----------|--------|-------|
| tree_oak | Common tree | 2×2 | 32×48 | wood × 5-8 |
| tree_pine | Evergreen | 2×2 | 32×52 | wood × 5-8 |
| tree_palm | Tropical | 2×2 | 32×48 | wood × 4-6, coconut |
| tree_dead | Bare tree | 1×1 | 16×32 | wood × 2-3 |
| tree_fruit | Apple tree | 2×2 | 32×44 | wood × 4, apple × 3-5 |
| bush | Small shrub | 1×1 | 16×16 | fiber × 1-2 |
| tall_grass | Wild grass | 1×1 | 16×20 | fiber × 0-1 |
| reeds | Water plant | 1×1 | 16×24 | fiber × 1-2 |
| mushroom_red | Forest fungus | 1×1 | 16×16 | mushroom |
| mushroom_glow | Cave fungus | 1×1 | 16×16 | cave_mushroom |

---

## 15. Other Items

Miscellaneous.

| Item | Description | Footprint | Sprite | Use |
|------|-------------|-----------|--------|-----|
| signpost | Travel point | 1×1 | 16×24 | Fast travel |
| torch_held | Carried light | - | 16×16 | Light in hand |
| lantern | Better light | - | 16×16 | Light, placeable |
| glowworm_lantern | Bug-powered | - | 16×16 | Long-lasting light |
| rope | Crafting material | - | 16×16 | Utility |
| bridge_wood | Water crossing | 2×2 | 32×32 | Cross water |
| bridge_stone | Strong bridge | 2×2 | 32×32 | Cross water |
| minecart | Ore transport | 1×1 | 16×16 | On rails |
| rail | Cart track | 1×1 | 16×8 | Minecart path |
| bomb | Explosive | 1×1 | 16×16 | Blast mining |
| key_copper | Unlock door | - | 16×16 | Zone key |
| key_iron | Better key | - | 16×16 | Zone key |
| key_boss | Boss room | - | 16×16 | Boss access |
| blueprint | Recipe unlock | - | 16×16 | Learn crafting |
| fossil | Ancient bug | 1×1 | 16×16 | Decoration, lore |
| geode | Hidden gems | - | 16×16 | Crack open |
| coin_copper | Currency | - | 8×8 | Money |
| coin_silver | Currency | - | 8×8 | Money |
| coin_gold | Currency | - | 8×8 | Money |

---

## Summary

| Category | Count | Notes |
|----------|-------|-------|
| Basic Blocks | ~20 | Ores, processed |
| Tools | ~40 | 9 tiers × 4 types + hammers |
| Weapons | ~15 | Swords, spears |
| Nets & Catching | ~8 | Nets, jars, magnifying glass |
| Construction | ~10 | Crafting stations |
| Health | ~12 | Food, potions |
| Decoration | ~12 | Rugs, paintings, trophies |
| Beekeeping | ~10 | Hives, tools |
| Fencing | ~12 | Fences, walls, doors |
| Webbing | ~8 | Spider products |
| Insects | ~80+ | All species |
| Containers | ~8 | Storage |
| Furniture | ~18 | Tables, beds, lights |
| Plants | ~25 | Crops, flowers, trees |
| Other | ~20 | Misc utility |

**Total: ~300+ unique items**
