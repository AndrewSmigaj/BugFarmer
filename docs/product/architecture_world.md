# World Building Architecture

## Overview

BugFarmer uses a tile-based world with fixed-size zones. World data is authored at design-time using LLM assistance, saved as data files, and committed to the repository. Players can modify the world by placing and breaking tiles/objects.

---

## 1. World Structure

### Layout

```
                                 NORTH
                                   ↑
         Col 0        Col 1        Col 2        Col 3
       ┌───────────┬───────────┬───────────┬───────────┐
Row 0  │   HARD    ≈   HARD    │ EXTRA HARD│  EX-EX HD │
       │ Locust    ≈ Millipede │ Spider    │ Spider    │
       │ Farmland  ≈ Forest    │ Vale West │ Vale East │
       ├───────────┼─────────≈≈┼───────────┼───────────┤
Row 1  │  MEDIUM   │  MEDIUM  ≈≈   HARD    │ EXTRA HARD│
       │  Meadow   │ Butterfly≈≈ Scorpion  │ Deep      │
       │  (Bees)   │ Fields   ≈≈ Rocks     │ Swamp     │
       ├───────────┼──────────≈╞≈≈≈≈≈≈≈≈≈≈≈┼───────────┤
Row 2  │   EASY    │   EASY    │  MEDIUM  ≈≈   HARD    │
       │   Bee     │  Village  │  Wasp    ≈≈  Shallow  │
       │  Meadow   │  (start)  │ Thicket  ≈≈  Swamp    │
       ╞═══════════╪═══════════╪══════════≋╪═══════════╡  ← CLIFF WALL
Row 3  │   EASY    │   EASY    │  MEDIUM  ≋≋   HARD    │
UNDER- │ Ant Colony│ Underground│ Underground│ Ant       │
GROUND │  (intro)  │ Passages  │  River   ≋≋  Outpost   │
       ├───────────┼───────────┼──────────≈┼───────────┤
Row 4  │  MEDIUM   │  MEDIUM   │   HARD    │ EXTRA HARD│
DEEP   │ Ant Colony│ Centipede │ Underground│  Deadly   │
       │  +QUEEN   │  Cavern   │  River    │   Ants    │
       └───────────┴───────────┴───────────┴───────────┘
                                 SOUTH

≈ = River (shallow crossings, separates Medium from Hard areas)
≋ = Waterfall (river meets cliff edge)

> **Restructure (2026-06-25, see `economy/DECISIONS.md` D2/D3/D9):** the world is currently **rows 0–4** —
> the old **row 5** "deep cliff" tier (Centipede Depths / Deep Passages / Deep River / Ant Queen Chamber) is
> **deferred** (re-add later). Underground **col 0** is now an **Ant Colony** (intro: easy + medium, the
> medium tier holds a **Queen** mini-boss) instead of centipedes; the **Centipede Cavern** moved to **(4,1)**;
> the **Deadly Ant** colony (col 3) shifted **up** with a **surface outpost** that forages into the col-3
> Swamp. The big Ant **Queen Chamber** boss returns with row 5. **Two ant colonies** are intentional: a gentle
> intro one (col 0 west) + the deadly endgame one (col 3 east).

## Zone Species Guide (0-indexed)

### Row 0 - HARD (North)

**Col 0 - Locust Farmland** (HARD)
No river barrier to medium zones - locusts swarm south freely
- Locusts (swarm behavior, crop destroyers)
- Grasshoppers
- Crickets
- Crop beetles

**Col 1 - Millipede Forest** (HARD)
- Millipedes (many varieties)
- Forest centipedes (easy tier)
- Bark beetles
- Stag beetles

**Col 2 - Spider Vale West** (EXTRA HARD)
- Orb weavers
- Wolf spiders
- Harder centipedes
- Jumping spiders

**Col 3 - Spider Vale East** (EXTRA EXTRA HARD)
- Black widows
- Tarantulas
- Trapdoor spiders
- Giant huntsman

### Row 1 - MEDIUM/HARD

**Col 0 - Meadow** (MEDIUM)
Medium-tier bees, more aggressive than village
- Bumblebees
- Wasps
- Carpenter bees
- Hornets

**Col 1 - Butterfly Fields** (MEDIUM)
- Butterflies (various)
- Moths
- Fireflies
- Cicadas

**Col 2 - Scorpion Rocks** (HARD)
Rocky terrain east of river
- Scorpions
- Ticks
- Harvestmen (daddy longlegs)
- Vinegaroons

**Col 3 - Deep Swamp** (EXTRA HARD)
- Mosquitoes (aggressive swarms)
- Dragonflies
- Water striders
- Giant water bugs

### Row 2 - EASY/MEDIUM

**Col 0 - Bee Meadow** (EASY)
Gentle introduction to bees
- Honeybees
- Mason bees
- Leafcutter bees
- Sweat bees

**Col 1 - Starting Village** (EASY)
Tutorial area, basic bugs
- Flies
- Ladybugs
- Aphids
- Pill bugs
- Basic ants

**Col 2 - Wasp Thicket** (MEDIUM)
Dense brush east of river
- Paper wasps
- Mud daubers
- Earwigs
- Silverfish

**Col 3 - Shallow Swamp** (HARD)
- Damselflies
- Pond skaters
- Whirligig beetles
- Leeches

### Row 3–4 - UNDERGROUND (Cliff Entrance / Deep)

> Row 5 (deep cliff) is **deferred** — see the restructure note up top. Its rarest ores now compress into
> **row 4**; the grand Ant Queen Chamber boss returns when row 5 does.

**Col 0 - Ant Colony — intro** (EASY → MEDIUM, +Queen)
The gentle introduction to ants: a tunneled colony of chambers and an `ant_mound` network, 2+ tunnels to
surface. The **medium tier (row 4) holds the colony Queen** — a mid-game mini-boss, distinct from the
deferred grand Queen.
- Garden ants, black ants (easy, row 3)
- Harvester ants, soldier ants (medium, row 4)
- **Colony Queen** (mini-boss, row 4) + ant guards

**Col 1 - Underground Passages → Centipede Cavern** (EASY → MEDIUM)
Row 3 is connecting passages; **(4,1)** is the relocated **Centipede Cavern** (stalactites, side caverns).
- Cave spiders, blind beetles, mole crickets, springtails (row 3 passages)
- **Giant centipedes**, cave beetles, glowworms, camel crickets (row 4 cavern)

**Col 2 - Underground River** (MEDIUM → HARD)
Waterfall feeds into the underground river system.
- Cave crayfish, water beetles, aquatic larvae, albino insects

**Col 3 - Deadly Ants** (HARD → EXTRA HARD)
A second, dangerous ant colony. The **outpost (row 3)** has surface access, foraging into the col-3 Swamp;
the **core (row 4)** is the deadly heart.
- Bullet ants, soldier ants (outpost, row 3)
- Army ants, fire ants (deep core, row 4)

### Surface Zones (Rows 0-2)

- Open areas with varied biomes (farmland, forest, meadows, swamps)
- Bug catching, farming, building gameplay
- Pre-generated terrain with trees, water, paths
- River separates Medium from Hard difficulty areas (shallow crossings allowed)
- No barrier between Locust Farmland and Medium zones - locusts swarm freely

### Underground Zones (Rows 3–4)

- Cliff wall at Row 3 boundary (between surface and underground)
- Players dig INTO the cliff horizontally (going south = deeper into cliff)
- Top-down view, but represents carving into a cliff face
- Pre-generated like Terraria:
  - Ore veins placed at design time (rarer ores deeper south — now bottoming out in **row 4**)
  - Caverns carved out (Ant Colony col 0, Centipede Cavern at 4,1, Underground River, Deadly Ants col 3)
  - Tunnels connecting caverns to surface (the col-0 & col-3 ant colonies forage up)
  - Boss areas — the grand Ant Queen Chamber — **return with the deferred row 5**
- Difficulty scales with column AND row (**row 4** hardest now, Col 3 hardest)

### Zone Connections

- Surface zones connect via paths, gaps in barriers, river crossings
- Underground entered through cliff wall openings
- Centipede Cavern has 2+ tunnels to surface
- Ant Colony has some surface access for foraging
- Hard boundaries between zones (no seamless transitions)

### Road & Signpost System

Roads branch out from the Starting Village (2,1) to each surface zone. Each zone has a small hub area along the road with:
- **Signpost**: Fast travel point (unlocks after first visit)
- **Thematic structure**: NPC house or landmark relevant to the zone
- **Starter resources**: Hints at what the zone offers

| Zone | Hub Area | Structure | Purpose |
|------|----------|-----------|---------|
| Village (2,1) | Central square | Player house, main signpost | Home base, tutorial |
| Bee Meadow (2,0) | Meadow edge | Beekeeper's cottage + hives | Shows bee farming, sells bee supplies |
| Wasp Thicket (2,2) | Forest clearing | Abandoned shack | Warning signs, wasp nests visible |
| Shallow Swamp (2,3) | Dock area | Fisher's hut | Swamp gear, boat access? |
| Butterfly Fields (1,1) | Flower garden | Collector's cabin | Bug net upgrades, specimen jars |
| Meadow (1,0) | Hilltop | Apiary tower | Advanced bee stuff, wasps as pest control |
| Scorpion Rocks (1,2) | Rocky outcrop | Miner's camp | Mining tips, first pickaxe upgrades |
| Deep Swamp (1,3) | Stilted platform | Hermit's hut | Swamp survival gear |
| Locust Farmland (0,0) | Farm gate | Ruined farmhouse | Shows locust devastation, crop seeds |
| Millipede Forest (0,1) | Forest entrance | Ranger station | Forest navigation, millipede lore |
| Spider Vale West (0,2) | Cave mouth | Hunter's lodge | Spider silk trade, warnings |
| Spider Vale East (0,3) | Dark hollow | Abandoned camp | Loot, signs of previous explorers |

**Underground Hub Areas (accessible via cliff entry):**

| Zone | Hub Area | Structure | Purpose |
|------|----------|-----------|---------|
| Ant Colony – intro (3,0) | Cavern entrance | Myrmecologist's camp | Ant lore, ant-egg trade, signpost |
| Underground Passages (3,1) | Junction chamber | Miner's outpost | Sells picks, torches, mine goes deeper |
| Underground River (3,2) | Waterfall pool | Fisher's platform | Aquatic gear, cave fish |
| Deadly Ants outpost (3,3) | Tunnel mouth | Exterminator's base | Ant repellent, warnings, bounty board |
| Ant Colony + Queen (4,0) | Deep chamber | (mini-boss) | Colony Queen fight, ant-derived drops |
| Centipede Cavern (4,1) | Stalactite hall | Hermit researcher | Rare specimens, centipede lore |
| Underground River deep (4,2) | Underground lake | Sunken ruins | Treasure, water bugs |
| Deadly Ants core (4,3) | Colony heart | (No friendly NPC) | Deadly endgame ant area |

### Road Layout

```
                    [Locust Farm]----[Millipede Forest]
                          |                |
                          |          [Spider Vale W]--[Spider Vale E]
                          |                |
                    [Meadow/Bees]----[Butterfly Fields]----[Scorpion]----[Deep Swamp]
                          |                |                   |              |
                          |                |                   |              |
                    [Bee Meadow]-----[VILLAGE]------------[Wasp Thicket]--[Shallow Swamp]
                                         |
                                    [Cliff Entry]
```

Roads provide safe-ish travel corridors. Bugs generally avoid roads but may cross them.

---

## 1b. Resource & Material Dispersion

Where each crafting material comes from — the geographic spine that paces progression. Per
`economy/DECISIONS.md` **D7/D8**: surface **floor** tiles are never dug; materials come from diggable **block
clumps** + harvestable **nature occupants** + the **mining cliff** + **bug drops**. "Terraforming" = *placing*
a floor tile on top, never a hole. Water is placed with care — `water_shallow` (wade) vs `water_deep` (blocks).

### Surface (rows 0–2) — harvest occupants & dig block-clumps on fixed floor
| Material | Source | Where (zones) | Tool |
|---|---|---|---|
| wood | tree_oak/pine/palm, log, stump | Millipede Forest (0,1), village & meadow trees | Axe |
| fiber | bush, tall_grass, **reeds**, clover | meadows everywhere; **reeds** in the Swamps (2,3 / 1,3) + riverbanks | Hand |
| flower / herb / mushroom | flower, mushroom | Bee Meadow (2,0), Meadow (1,0), Butterfly Fields (1,1), Village | Hand |
| stone (shallow) | rock_small/large, boulder | rocky surfaces, esp. Scorpion Rocks (1,2) | Pickaxe (Wood→Stone) |
| clay | **clay_block** clumps | riverbanks (river, cols 1–2) | Shovel |
| **sand** | **sand_block** clumps | **beach / sandy edges** (river mouth, swamp shore) | Shovel |
| coal (shallow) | surface coal seams | scattered surface rock | Pickaxe (Wood) |

### Underground (rows 3–4) — dig the cliff
| Material | Source | Row | Tool tier |
|---|---|---|---|
| copper, coal, iron | ore_* tiles | row 3 | Wood → Stone |
| iron, silver, gold | ore_* tiles | row 4 | Stone → Iron |
| platinum, diamond | ore_* tiles | row 4 (east cols) | Gold → Platinum |
| stone, hard_stone, granite | solid tiles | rows 3–4 | Pickaxe Wood → Iron |
| crystal / gem | crystal_small/large | row 4 | Stone → Iron |
| cave_mushroom, silk (web), bone | nature occupants | rows 3–4 | Hand |
| ant_egg | ant_mound | ant colonies (col 0 & 3) | Shovel |

### Bug-derived (from the species farmed/hunted in each region)
| Material | From | Zones |
|---|---|---|
| honey, beeswax | bees | Bee Meadow (2,0), Meadow (1,0) |
| silk | spiders, webs | Spider Vales (0,2 / 0,3), underground webs |
| venom, stinger | wasps, scorpions, bees | Meadow (1,0), Wasp Thicket (2,2), Scorpion Rocks (1,2) |
| chitin / carapace | beetles | forests, caverns |
| ant_egg, formic acid | ants | Ant colonies (col 0 & 3) |

*(The full bug-drop → item table lives in `economy/crafting.md`; this is the geographic key.)*

**Starting-village basics:** the Village (2,1) and its immediate surrounds give only **wood, fiber, flowers,
shallow stone & coal, and copper** — enough for tier-1 tools + basic furniture. Iron+, clay/sand artisan
inputs, deeper ores, and bug-derived gear all require travelling to the regions above/below. This gating is
the progression spine — paced in `economy/progression.md`.

---

## 2. Gameplay Loops & Terrain Puzzles

### Core Loop: Catch → Farm → Produce → Upgrade

The world design supports this loop:

1. **Catch**: Explore zones to find bug species
2. **Farm**: Build pens/structures with right conditions (plants, terrain, fencing)
3. **Produce**: Bugs produce resources (honey, silk, etc.) based on conditions
4. **Upgrade**: Craft better tools → access harder zones → new species

### How Zones Support Bug Farming

| Zone | Key Species | Farming Potential | Required Conditions |
|------|-------------|-------------------|---------------------|
| Village (2,1) | Flies, Ladybugs | Tutorial farms | Basic fencing, any plants |
| Bee Meadow (2,0) | Honeybees | Honey production | Flowers, beehives, keep wasps out |
| Butterfly Fields (1,1) | Butterflies, Fireflies | Aesthetic, silk? | Open meadow, flowers |
| Meadow (1,0) | Bumblebees, Wasps | Wax, pest control | Wildflowers, sturdy fencing |
| Swamp (2,3 / 1,3) | Dragonflies, Water bugs | Aquatic farming | Water features, reeds |
| Ant Colony (Row 3-5, Col 3) | Ants | Excavation labor? | Underground chambers, food |

### Example: Bee Farming

- Place beehive → attracts bee swarms
- Beehive supports ~3 swarms
- Honey production scales with swarm size
- Plant flowers nearby → bees visit flowers (supplements swarming behavior)
- Keep wasps OUT with fencing/barriers or they hunt your bees
- Optimization: more flowers + bigger swarms + wasp protection = max honey

### Terrain-Based Puzzles

**River Crossings**
- Shallow sections allow crossing but slow movement
- Build bridges for efficient travel
- River blocks most bug movement → natural pest barrier
- Strategic: farm on one side, pests stuck on other

**Cliff Mining Decisions**
- Where to dig first? Resources vs danger tradeoff
- Creating tunnels affects bug migration underground
- Dig toward Centipede Cavern or Ant Colony?
- Mining path = permanent world change

**Zone Barriers**
- Natural barriers (water, rocks) contain bug populations
- Breaking barriers lets bugs flow → intentional or disaster?
- Locust Farmland has NO barrier → constant pressure on medium zones
- Player-built fencing to create safe farming areas

**Environmental Conditions**
- Bees need flowers → plant them or find flower zones
- Some bugs need shade (forest) vs sun (meadow)
- Water bugs need ponds → dig or find natural water
- Underground bugs need darkness → covered pens on surface?

### Surprise & Discovery

**Pre-generated Secrets**
- Hidden caverns revealed by mining
- Rare ore veins in unexpected locations
- Tunnel connections between zones
- Boss lairs (Ant Queen, Centipede Depths)

**Random Events** (see architecture_bugs.md)
- Meteor strikes → zombie bug infection zones
- Locust swarms invading from Farmland
- Ant raids on surface
- Infection spreads then becomes mineable terrain

**Emergent Situations**
- Wasps escape pen → devastate bee farm
- Mining into ant tunnel → ants flood your base
- Breaking river barrier → floods lower area
- Bugs following player back to village

### Progression Through Discovery

- Inspect bugs with magnifying glass → learn conditions
- More inspection → more knowledge about preferences
- Knowledge → better farming setups
- Blueprints/recipes unlock from item drops
- Discovery feels earned, not wiki-dependent

---

## 3. Grid System

### Base Unit

- **Cell size**: 16×16 pixels
- **1 grid unit** = 1 cell = 16×16 pixels

### Entity Sizes

| Entity | Pixels (W×H) | Grid Cells (W×H) |
|--------|--------------|------------------|
| Grid cell | 16×16 | 1×1 |
| Player | 48×32 | 3×2 |

**Perspective:** Bird's eye / top-down with slightly higher angle.

### Two Layers

The world has exactly two tile layers:

**Layer 1: Ground**
- Terrain tiles: grass, dirt, sand, water, stone, wood_floor, etc.
- Always filled (no empty ground)
- Determines walkability, appearance
- Player can place floor tiles on top of natural terrain

**Layer 2: Occupants**
- What sits on that cell: wall, furniture, tree, rock, or empty
- Only ONE occupant per cell
- Occupants have a **footprint** (which cells they block)
- Cannot place where another occupant exists

```
Example: 4×4 area with a 2×2 table

Ground layer:        Occupant layer:
[grass][grass][dirt][dirt]    [    ][    ][    ][    ]
[grass][grass][dirt][dirt]    [    ][table][table][    ]
[grass][stone][stone][dirt]   [    ][table][table][    ]
[grass][stone][stone][dirt]   [    ][    ][    ][    ]
```

### Ground Tile Types

Ground tiles fall into two categories:

**Floor tiles** - walkable surfaces (surface zones, cleared mining areas)
**Solid tiles** - must be broken to pass through (mining zone cliff face)

#### Floor Tiles (Surface Zones)

| Tile | Biome | Movement | Breakable | Notes |
|------|-------|----------|-----------|-------|
| grass | Meadow, Forest | Normal | No | Basic surface |
| dirt | All | Normal | No | Paths, farmland base |
| sand | Desert, Beach | Normal | No | Decorative floor — NOT a material source; dig `sand_block` clumps for sand (see §1b) |
| mud | Swamp | Slow | No | Reduces movement speed |
| stone_path | Placed | Normal | Yes (pickaxe) | Player-built paths |
| wood_floor | Placed | Normal | Yes (axe) | Player-built floors |
| water_shallow | Rivers, Ponds | Slow | No | Players wade, blocks insects |
| water_deep | Lakes, Rivers | Blocks | No | Blocks players and insects |

#### Solid Tiles (Mining Zone)

These represent the cliff face. Players break them to carve tunnels.

| Tile | Depth | Tool | Tier | Drops | HP |
|------|-------|------|------|-------|-----|
| dirt | 0-10 | Shovel | Wood | dirt ×1 | 2 |
| clay | 5-20 | Shovel | Wood | clay ×1 | 3 |
| stone | 10-30 | Pickaxe | Wood | stone ×1 | 4 |
| hard_stone | 20-50 | Pickaxe | Stone | stone ×2 | 6 |
| granite | 40+ | Pickaxe | Iron | granite ×1 | 10 |

#### Ore Tiles (Mining Zone)

Embedded in solid tiles. Rarer ores found deeper into cliff (higher row numbers).

| Tile | Rows | Tool | Tier | Drops |
|------|------|------|------|-------|
| ore_copper | 3 | Pickaxe | Wood | copper_ore ×1-2 |
| ore_coal | 3-4 | Pickaxe | Wood | coal ×1-3 |
| ore_iron | 3-4 | Pickaxe | Stone | iron_ore ×1-2 |
| ore_silver | 4 | Pickaxe | Iron | silver_ore ×1-2 |
| ore_gold | 4 | Pickaxe | Iron | gold_ore ×1-2 |
| ore_platinum | 4 (east cols) | Pickaxe | Gold | platinum_ore ×1 |
| ore_diamond | 4 (east cols) | Pickaxe | Platinum | diamond ×1 |

**Ore distribution by row (rows 0–4 layout):**
- Row 3 (cliff entrance): Copper, Coal, Iron (common)
- Row 4 (deep — now the deepest): Iron, Silver, Gold, **Platinum, Diamond** (rare) — the old row-5 ores
  compress up here, concentrated in the harder **east columns** (col 2–3)
- *(Row 5's dedicated rare-ore tier returns when row 5 is re-added)*

**Column modifier:** Harder columns (2-3) have rarer ores appear slightly earlier.

#### Tile Properties

```csharp
public class GroundTileDefinition : ScriptableObject
{
    public string tileId;
    public string displayName;
    public Sprite sprite;
    public Sprite[] variants;          // Visual variety

    // Category
    public bool isSolid;               // Must break to pass (mining zone)

    // Movement
    public bool blocksPlayers;
    public bool blocksInsects;
    public float movementMultiplier;   // 1.0 = normal, 0.5 = slow

    // Breaking (if breakable)
    public bool isBreakable;
    public string requiredToolType;    // "shovel", "pickaxe", "axe", ""
    public int requiredToolTier;       // 0=hand, 1=wood, 2=stone, 3=iron
    public int hp;                     // Hits to break
    public string dropItemId;
    public int dropCountMin;
    public int dropCountMax;

    // Placement rules
    public bool playerCanPlace;
    public string[] validOccupants;    // What can be placed on this
    public string[] invalidOccupants;  // What cannot be placed on this

    // After breaking (solid tiles only)
    public string revealsFloorTile;    // What floor tile appears after breaking
}
```

#### Special Placement Rules

| Ground Tile | Can Place | Cannot Place |
|-------------|-----------|--------------|
| water_shallow | bridge, dock, lily_pad | furniture, walls |
| water_deep | bridge | everything else |
| mud | all | - |
| Any solid tile | nothing | - (must break first) |

#### After Breaking Solid Tiles

When a solid tile is broken, it reveals a floor tile underneath:

| Solid Tile | Reveals |
|------------|---------|
| dirt | cave_floor |
| clay | cave_floor |
| stone | cave_floor |
| hard_stone | cave_floor |
| granite | cave_floor |
| ore_* | cave_floor |

`cave_floor` is a walkable floor tile specific to the mining zone.

---

## 4. Item Prefabs

Each placeable item has two components:

### Sprite
- Visual representation
- Can be any pixel size (tree sprite is tall)
- Rendered at item's anchor position

### Footprint
- Which grid cells the item occupies
- Used for placement collision
- Defined as a boolean grid

```
Example footprints:

Chair (1×1):     Table (2×2):     L-Shaped Desk (3×2):
[X]              [X][X]           [X][X][X]
                 [X][X]           [X][_][_]
```

### ScriptableObject Definition

```csharp
[CreateAssetMenu(fileName = "Item", menuName = "BugFarmer/ItemDefinition")]
public class ItemDefinition : ScriptableObject
{
    public string itemId;
    public string displayName;
    public Sprite icon;           // Inventory icon
    public GameObject prefab;     // World prefab with sprite

    // Footprint
    public Vector2Int footprintSize;  // e.g., (2, 2) for table
    public bool[] footprintCells;     // Row-major, true = occupied

    // Placement
    public bool isPlaceable;          // Can player place this?
    public string[] validGround;      // Ground types it can be placed on
    public string[] invalidGround;    // Ground types it cannot be placed on

    // Breaking
    public bool isBreakable;
    public string requiredToolType;   // "axe", "pickaxe", "hammer", ""
    public int requiredToolTier;      // 0=hand, 1=wood, etc.
    public int hp;
    public string dropItemId;         // What drops when broken
    public int dropCountMin;
    public int dropCountMax;

    // Movement blocking
    public bool blocksPlayers;
    public bool blocksInsects;

    // Category
    public string category;           // "nature", "furniture", "wall", "structure", "utility"
}
```

### Occupant Categories

#### Nature (Generated, not player-placed)

Found in surface zones, placed at design time.

| Occupant | Footprint | Tool | Tier | Drops | Blocks |
|----------|-----------|------|------|-------|--------|
| tree_oak | 2×2 | Axe | Wood | wood ×5-8 | Both |
| tree_pine | 2×2 | Axe | Wood | wood ×5-8 | Both |
| tree_palm | 2×2 | Axe | Wood | wood ×4-6 | Both |
| tree_dead | 1×1 | Axe | Wood | wood ×2-3 | Both |
| bush | 1×1 | Hand | - | fiber ×1-2 | Neither |
| rock_small | 1×1 | Pickaxe | Wood | stone ×1-2 | Insects |
| rock_large | 2×2 | Pickaxe | Stone | stone ×3-5 | Both |
| boulder | 2×2 | Pickaxe | Stone | stone ×4-6 | Both |
| flower | 1×1 | Hand | - | flower ×1 | Neither |
| mushroom | 1×1 | Hand | - | mushroom ×1 | Neither |
| tall_grass | 1×1 | Hand | - | fiber ×0-1 | Neither |
| reeds | 1×1 | Hand | - | fiber ×1-2 | Neither |
| log | 2×1 | Axe | Wood | wood ×2-3 | Insects |
| stump | 1×1 | Axe | Wood | wood ×1 | Neither |

#### Mining Zone Nature

Found in caves/tunnels after breaking solid tiles.

| Occupant | Footprint | Tool | Tier | Drops | Blocks |
|----------|-----------|------|------|-------|--------|
| stalagmite | 1×1 | Pickaxe | Wood | stone ×1 | Insects |
| crystal_small | 1×1 | Pickaxe | Stone | crystal ×1 | Neither |
| crystal_large | 2×1 | Pickaxe | Iron | crystal ×2-3 | Insects |
| web | 1×1 | Hand | - | silk ×1 | Neither |
| cave_mushroom | 1×1 | Hand | - | cave_mushroom ×1 | Neither |
| bone_pile | 1×1 | Hand | - | bone ×1-2 | Neither |
| ant_mound | 2×2 | Shovel | Stone | dirt ×3, ant_egg ×0-1 | Both |

#### Walls (Player-placed)

Block movement, form buildings.

| Occupant | Footprint | Tool | Tier | Drops | Materials to Craft |
|----------|-----------|------|------|-------|-------------------|
| wall_wood | 1×1 | Hammer | Wood | wood ×1 | wood ×1 |
| wall_stone | 1×1 | Hammer | Stone | stone ×1 | stone ×1 |
| wall_brick | 1×1 | Hammer | Stone | brick ×1 | brick ×1 |
| wall_iron | 1×1 | Hammer | Iron | iron_bar ×1 | iron_bar ×1 |
| fence_wood | 1×1 | Hammer | Wood | wood ×1 | wood ×1 |
| door_wood | 1×2 | Hammer | Wood | door_wood ×1 | wood ×4 |
| door_iron | 1×2 | Hammer | Iron | door_iron ×1 | iron_bar ×4 |

Doors: Toggle open/closed. Open = doesn't block movement. Closed = blocks insects, not players.

#### Furniture (Player-placed)

Functional or decorative items for buildings.

| Occupant | Footprint | Tool | Tier | Function |
|----------|-----------|------|------|----------|
| table_wood | 2×2 | Hammer | Wood | Decoration, crafting surface |
| chair_wood | 1×1 | Hammer | Wood | Decoration |
| bed | 2×4 | Hammer | Wood | Set spawn point |
| chest | 2×1 | Hammer | Wood | Storage (inventory) |
| sign | 1×1 | Hammer | Wood | Display text |
| torch | 1×1 | Hand | - | Light source |
| lamp | 1×1 | Hammer | Wood | Better light source |
| rug | 2×2 | Hand | - | Decoration (doesn't block) |

#### Crafting Stations (Player-placed)

Required for crafting recipes.

| Occupant | Footprint | Tool | Tier | Unlocks |
|----------|-----------|------|------|---------|
| workbench | 2×2 | Hammer | Wood | Basic recipes |
| furnace | 2×2 | Hammer | Stone | Smelting ore → bars |
| anvil | 2×1 | Hammer | Iron | Metal tools, weapons |
| loom | 2×2 | Hammer | Wood | Cloth, rope |
| cooking_pot | 2×1 | Hammer | Wood | Food recipes |

#### Utility (Player-placed)

Special function items.

| Occupant | Footprint | Ground | Function |
|----------|-----------|--------|----------|
| bridge_wood | 2×2 | water_shallow, water_deep | Allows crossing water |
| bridge_stone | 2×2 | water_shallow, water_deep | Stronger bridge |
| fence_gate | 1×1 | any | Toggles like door |

#### Barriers (Generated or Player-placed)

Specifically for insect containment.

| Occupant | Footprint | Tool | Tier | Notes |
|----------|-----------|------|------|-------|
| barrier_stone | 1×1 | Pickaxe | Wood | Blocks insects, not players |
| barrier_iron | 1×1 | Pickaxe | Iron | Stronger barrier |

These form the natural boundaries between bug zones. Players can break them to allow insect flow.

### Occupant Interactions

Some occupants have special behaviors:

| Occupant | Interaction |
|----------|-------------|
| door_* | Click to toggle open/closed |
| chest | Click to open storage UI |
| bed | Click to set spawn point |
| sign | Click to read/edit text |
| fence_gate | Click to toggle open/closed |
| torch, lamp | Provides light radius |

### Mining Zone Caverns (Pre-generated)

The mining zone is fully pre-generated at design time:

1. Caverns carved out as empty space (cave_floor tiles)
2. Occupants placed in caverns (crystals, mushrooms, stalagmites, etc.)
3. Player breaks through solid tiles, discovers existing caverns

**Underground generation guidelines (by row/column):**

| Location | Typical Contents | Ores |
|----------|------------------|------|
| Row 3 (cliff entrance) | cave_mushroom, bone_pile, web, small caverns | Copper, Coal, Iron |
| Row 4 (deep) | stalagmite, crystal_small/large, larger caverns, mini-boss chambers | Iron, Silver, Gold, Platinum, Diamond |
| Col 0 (Ant Colony – intro) | Ant tunnels, ant_mound, chambers, Colony Queen mini-boss (row 4), tunnels to surface | |
| Col 1 (Passages → Centipede Cavern) | Narrow tunnels + cave spiders (row 3); centipede cavern w/ stalactites + glowworms (row 4) | |
| Col 2 (Underground River) | Water features, aquatic insects, wet cave floor | |
| Col 3 (Deadly Ants) | Ant tunnels, ant_mound, organized chambers; outpost forages to the surface swamp | |

No runtime spawning - everything is baked into the zone data.

---

## 5. Tools & Breaking

### Tool Types

| Tool Type | Used For |
|-----------|----------|
| Hand | Picking flowers, small plants |
| Axe | Wood, wood floors, trees |
| Pickaxe | Stone, ore, hard materials |
| Shovel | Dirt, clay, sand |
| Hammer | Walls, furniture, structures |

### Tool Tiers

| Tier | Materials | Can Break |
|------|-----------|-----------|
| 0 (Hand) | - | Flowers, grass, weak plants |
| 1 (Wood) | Wood | Dirt, clay, copper ore, coal |
| 2 (Stone) | Stone | Stone, hard stone |
| 3 (Copper) | Copper bars | Iron ore |
| 4 (Iron) | Iron bars | Silver ore, gold ore |
| 5 (Steel) | Steel bars (iron + coal) | Granite, harder stone |
| 6 (Silver) | Silver bars | Platinum ore |
| 7 (Gold) | Gold bars | Diamond ore |
| 8 (Platinum) | Platinum bars | All materials (faster) |
| 9 (Diamond) | Diamond | All materials (fastest) |

### Breaking Rules

1. Player equips tool from hotbar
2. Player clicks on tile/occupant
3. Check: Does tool type match requirement?
4. Check: Does tool tier meet minimum?
5. If both pass: Deal 1 damage to tile/occupant HP
6. When HP reaches 0: Break, drop items, reveal floor (if solid tile)

### Tool Definition

```csharp
public class ToolDefinition : ScriptableObject
{
    public string toolId;
    public string displayName;
    public Sprite icon;

    public string toolType;        // "axe", "pickaxe", "shovel", "hammer"
    public int tier;               // 0=hand, 1=wood, 2=stone, 3=iron, 4=gold
    public float speedMultiplier;  // Higher tier = faster breaking
    public int durability;         // Uses before breaking (0 = infinite)
}
```

### Breaking Feedback

- Wrong tool type: "Needs [pickaxe]" message
- Tool tier too low: "Needs stronger [pickaxe]" message
- Correct tool: Show damage particles, HP bar on tile
- Break: Drop items, play break animation/sound

---

## 6. Placement System

### Grid Overlay

When player enters placement mode:
1. Show grid lines over world
2. Ghost sprite follows cursor, snapped to grid
3. Footprint cells highlighted green (valid) or red (blocked)

### Placement Validation

```csharp
public bool CanPlace(ItemDefinition item, Vector2Int gridPos)
{
    for (int y = 0; y < item.footprintSize.y; y++)
    {
        for (int x = 0; x < item.footprintSize.x; x++)
        {
            int index = y * item.footprintSize.x + x;
            if (!item.footprintCells[index]) continue; // Skip empty cells in footprint

            Vector2Int cell = gridPos + new Vector2Int(x, y);

            // Check bounds
            if (!IsInBounds(cell)) return false;

            // Check occupant layer
            if (GetOccupant(cell) != null) return false;

            // Check ground is valid (can't place on water, etc.)
            if (!IsPlaceableGround(cell)) return false;
        }
    }
    return true;
}
```

### Placement Flow

1. Player selects item from inventory
2. Enter placement mode (grid overlay visible)
3. Move cursor, ghost snaps to grid
4. Click to place → client sends `PlaceItem` message to server
5. Server validates and broadcasts placement
6. All clients add occupant to grid

---

## 7. Zone Structure

### Zone Definition

Zones are fixed-size areas with defined boundaries:

```json
{
  "zone_id": "meadow_01",
  "display_name": "Sunny Meadow",
  "biome": "grassland",
  "size": { "width": 64, "height": 64 },
  "spawn_point": { "x": 32, "y": 32 },
  "connections": [
    { "edge": "north", "target": "forest_01", "portal_x": 32 }
  ]
}
```

### Chunk Storage

Zones are divided into 16×16 chunks for streaming:

```
zones/
  meadow_01/
    zone.json           # Zone metadata
    chunk_0_0.json      # Ground + occupants for cells (0,0) to (15,15)
    chunk_1_0.json
    ...
```

### Chunk Format

```json
{
  "chunk_x": 0,
  "chunk_y": 0,
  "ground": [
    ["grass", "grass", "grass", "dirt", ...],
    ["grass", "grass", "dirt", "dirt", ...],
    ...
  ],
  "occupants": [
    [null, null, "tree_oak", null, ...],
    [null, "rock_small", null, null, ...],
    ...
  ]
}
```

For multi-cell occupants, only the anchor cell (bottom-left) contains the ID. Other cells in footprint are marked as blocked:

```json
"occupants": [
  [null, null, null, null],
  [null, "table_wood", "@", null],   // @ = blocked by adjacent occupant
  [null, "@", "@", null],
  [null, null, null, null]
]
```

---

## 8. LLM Generation Workflow

Zone data is authored at design-time with LLM assistance and committed to the repository. Zones have hard boundaries.

### Two Levels

**World Level (design-time only):**
- Zone layout: which zones exist, their sizes, how they connect
- World-spanning features: rivers, major roads that cross zone boundaries
- This is a working document for LLM generation - **not loaded by Nakama**

**Zone Level (committed to repo, loaded by Nakama):**
- Ground tiles + occupants for each zone
- Generated respecting the world-level features (rivers/roads already placed)

### Generation Order

1. **Define zone layout** - User describes zones and connections
2. **Generate world-spanning features** - LLM creates rivers, major roads across zones
3. **Generate each zone** - LLM fills in ground + occupants, working around rivers/roads
4. **Review and iterate** - User gives feedback, LLM adjusts

### Workflow

1. User provides high-level description (e.g., "grassland zone, 64x64, river runs through it, some ruins in the northeast")
2. LLM generates complete zone data
3. User reviews, provides feedback
4. LLM regenerates or adjusts specific areas
5. Final zone JSON files committed to repository

### Output

Only the zone chunk files are committed and used at runtime. The world map is a scratchpad for maintaining consistency across zones during generation.

---

## 9. Nakama Integration

### World State

```go
type WorldState struct {
    ZoneID     string
    Ground     map[string]string      // "x,y" -> ground type
    Occupants  map[string]string      // "x,y" -> occupant ID or ""
    Modified   map[string]bool        // Cells modified from base data
}
```

### Network Messages

```go
// Placement
OpCode_PlaceItem     = 40  // Client → Server
OpCode_BreakItem     = 41  // Client → Server
OpCode_WorldUpdate   = 42  // Server → Clients (broadcast change)

// Chunk streaming
OpCode_RequestChunk  = 43  // Client → Server
OpCode_ChunkData     = 44  // Server → Client
```

### Message Structures

```go
type PlaceItemMessage struct {
    ItemID  string  `json:"item_id"`
    GridX   int     `json:"grid_x"`
    GridY   int     `json:"grid_y"`
}

type BreakItemMessage struct {
    GridX   int     `json:"grid_x"`
    GridY   int     `json:"grid_y"`
}

type WorldUpdateMessage struct {
    GridX      int     `json:"grid_x"`
    GridY      int     `json:"grid_y"`
    Occupant   string  `json:"occupant"`   // "" for removed
}
```

### Persistence

- Base zone data: loaded from committed JSON files
- Player modifications: stored in Nakama storage per world instance
- On load: apply modifications on top of base data

---

## 10. Summary

| Concept | Implementation |
|---------|----------------|
| Grid cell | 16×16 pixels |
| Player | 48×32 pixels (3×2 cells) |
| Layers | Ground + Occupant |
| World layout | **5 rows × 4 cols**: Surface (rows 0–2) + Underground (rows 3–4); row 5 deferred (see `economy/DECISIONS.md` D2) |
| Difficulty | Easy/Medium west of river, Hard/Extra Hard east of river |
| River | Separates Medium from Hard, becomes underground river at cliff |
| Ground tiles | Floor (walkable) + Solid (breakable) |
| Tools | 10 tiers (wood → stone → copper → iron → steel → silver → gold → platinum → diamond), typed (axe, pickaxe, shovel, hammer) |
| Item footprint | Boolean grid on ScriptableObject |
| Placement | Grid snap, collision check, server validation |
| Zone data | JSON files, chunk-based (16×16 cells) |
| LLM workflow | World-level features first, then per-zone content |
| Multiplayer | Nakama validates and broadcasts changes |
