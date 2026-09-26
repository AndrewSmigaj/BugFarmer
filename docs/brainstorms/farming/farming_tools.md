# Crop-Farming Tools & Infrastructure — Brainstorm

Everything for the *crop* side of "farm crops AND bugs": hand tools, water, soil/fertility,
protection, plant support, structures, processing, and automation hints. Design only — no
code/data/art.

Read alongside:
- `docs/product/design/game_design.md` §8/§10/§11 (private-plot farming + automation rules).
- `docs/brainstorms/materials/ores_metals.md` for the **material tier ladder** (Wood → Copper →
  Iron → Steel → Gold/exotic) that hand tools are graded on.
- Existing crops: `tomato`, `corn`, `wheat` (`nakama/data/entities/crops.json`).
- Existing related ids: `planter_box`, `scarecrow`, `compost_bin`, `well`, `hand_pump`,
  `water_bucket`, `garden_arch`, `hedge`, `windmill`, `sawmill`, `fence_*`, `gate_*`.

## Rules this file follows
- Tools tier by **material**, and better tools = more reach/speed/yield, never replacing the basic
  one (§7.3 spirit applies to farming tools too).
- Automation is slow, capacity-capped, and plot-only (§11). No instant free harvest.
- Variety across poor→fancy; "quality" is just value/material tier.

---

## 1. HAND TOOLS (held — item icons, tiered by material)

Each tool comes in the material ladder: `wood`/`stone` (starter) → `copper` → `iron` → `steel` →
`gold`/`gilded` (fancy/prestige). Listed once with the tier axis called out.

| base id | one-line | tier axis | bonus / role |
|---------|----------|-----------|--------------|
| `hoe` | a tilling hoe for breaking soil into beds | wood→steel→gold | higher tier tills a wider area per swing |
| `watering_can` | a spouted can for watering crops | tin→copper→steel→gold | bigger tier = larger tank + wider splash |
| `trowel` | a small hand trowel for transplanting | wood→iron→steel | digs/plants single tiles precisely |
| `seed_dibber` | a pointed dibber for poking seed holes | wood→iron | speeds sowing rows |
| `sickle` | a curved blade for cutting grass/wheat | stone→iron→steel→gold | tier = wider clear + faster harvest |
| `scythe` | a long two-hand reaping scythe | iron→steel | big-area grain harvest (bigger than sickle) |
| `shears` | hand shears for trimming/pruning | copper→steel | prune plants, shear hedges, harvest herbs |
| `pruning_saw` | a folding saw for woody stems | iron→steel | cut back trellised/orchard growth |
| `pitchfork` | a fork for moving hay/compost/mulch | wood→iron | spread mulch, turn compost, gather hay |
| `rake` | a rake for clearing debris & leveling | wood→iron | tidy beds, gather cut grass, level soil |
| `spade` | a digging spade | iron→steel | dig planters/ponds, move earth |
| `harvest_basket` | a held basket that batches picked crops | wicker→sturdy | carry more before a trip to storage |

(Note: a starter set — `hoe`, `watering_can`, `sickle` — should be among the first tools the player
gets, matching the hands-on early loop.)

---

## 2. IRRIGATION & WATER

Water is a chore; these reduce it (slow/passive, not free). Crossover with `well`, `hand_pump`.
| id | one-line | tier | role |
|----|----------|------|------|
| `watering_can` *(see §1)* | hand watering | — | the baseline manual verb |
| `water_barrel` | a rain-catching barrel | poor | refill cans without walking to the well |
| `well` *(exists)* | stone water well | common | water source point |
| `hand_pump` *(exists)* | a manual pump | common | draw water at a spot |
| `water_trough` | a long stone/iron water channel | mid | feeds adjacent beds' moisture |
| `irrigation_channel` | a dug ditch tile that carries water | mid | route water from a source across beds |
| `sprinkler_basic` | a small spinning sprinkler stake | mid | auto-waters a few adjacent tiles, slow |
| `sprinkler_iron` | an iron sprinkler with wider arc | high | waters a larger radius |
| `sprinkler_steel` | a pressurized steel sprinkler | high | big radius; pairs with pump/power (§11.6) |
| `drip_line` | a laid drip-irrigation hose | high | efficient row watering; placed like a line |
| `rain_collector` | a fancy cistern + gutter | fancy | large reserve; refills sprinklers passively |

---

## 3. SOIL FERTILITY — fertilizer / compost / mulch

Extends `compost_bin`. Boost growth speed/quality; consumed when applied.
| id | one-line | role |
|----|----------|------|
| `compost_bin` *(exists)* | slatted bin turning scraps to compost | makes compost over time from scraps |
| `compost_tumbler` | a cranked rotating compost drum | faster compost than the open bin |
| `worm_farm` | a stacked tray vermicompost bin | premium "worm casting" fertilizer (bug crossover!) |
| `manure_pile` | a heap of aged manure | cheap bulk fertilizer |
| `fertilizer_basic` | a sack of basic plant food (consumable) | small growth-speed boost on a bed |
| `fertilizer_quality` | refined fertilizer (consumable) | bigger speed + quality boost |
| `mulch_straw` | spread straw mulch (consumable) | retains moisture, slows weeds |
| `mulch_bark` | decorative bark mulch (consumable) | tidy beds + moisture, fancier |
| `bone_meal` | ground-bone fertilizer (uses `bone`) | boosts flowering/fruiting |
| `bug_frass_bag` | insect-droppings fertilizer (bug crossover) | premium fertilizer from penned bugs |
| `lime_bag` | a soil-amendment lime sack | adjusts soil for fussy crops |

---

## 4. CROP PROTECTION

Extends `scarecrow`, `fence_*`, `gate_*`, `hedge`.
### 4.1 Pest/animal deterrents
| id | one-line | role |
|----|----------|------|
| `scarecrow` *(exists)* | straw figure on a cross-post | scares crop-raiding birds/bugs in a radius |
| `scarecrow_fancy` | a dressed, hatted scarecrow | larger protection radius; decorative |
| `whirligig` | a spinning garden pinwheel | small deterrent, cheap, decorative |
| `wind_chime` | a hung chime that rattles pests | minor deterrent + ambiance |
| `owl_decoy` | a perched fake owl on a post | bird deterrent |
| `garden_netting` | a draped crop net on hoops | physically blocks pest bugs from a bed |
| `cloche` | a glass bell jar over a single plant | protects a seedling; mini cold frame |

### 4.2 Fences & gates (garden-grade — extends the pen ladder for crops)
| id | one-line | tier | role |
|----|----------|------|------|
| `fence_picket` | a white picket garden fence | poor/decor | tidy garden border |
| `fence_wood` *(exists)* | split-rail wood fence | poor | basic enclosure |
| `fence_woven` | a low woven willow hurdle fence | poor/decor | rustic bed border |
| `fence_iron` *(exists)* | wrought-iron fence | mid | sturdy, decorative |
| `fence_electric` *(exists)* | wired electric fence | high | keeps animals/big pests out; needs power (§11.6) |
| `gate_wood` / `gate_iron` *(exist)* | matching gates | — | the openable section |
| `gate_picket` | a little picket garden gate | poor/decor | matches picket fence |
| `hedge` *(exists)* | trimmed shrub wall | decor | living fence/windbreak |
| `arbor_gate` | an arched gate with climbing vines | decor | pretty garden entrance (cf. `garden_arch`) |

---

## 5. PLANT SUPPORT (trellises, stakes, beds)

Extends `planter_box`, `garden_arch`.
| id | one-line | tier | role |
|----|----------|------|------|
| `plant_stake` | a single wooden support stake | poor | props up a tall plant |
| `tomato_cage` | a wire cone cage | common | supports vining crops (tomato) |
| `trellis_wood` | a wooden lattice trellis panel | common | climbing crops (beans, peas, vines) |
| `trellis_iron` | a wrought-iron trellis | mid | sturdy climber support, decorative |
| `bean_teepee` | a tripod of poles for climbers | poor | rustic climbing support |
| `garden_arch` *(exists)* | vine-covered archway | decor | decorative climber arch |
| `pergola` | a posted overhead beam frame | fancy | grows shade vines/grapes; sit under |
| `raised_bed` | a low wooden raised planting bed | common | tidy fertile plot; small growth bonus |
| `raised_bed_stone` | a stone-edged raised bed | mid | durable, decorative raised plot |
| `planter_box` *(exists)* | wooden planter trough | common | contained planting (decor + crops) |
| `planter_tall` | a tall standing planter on legs | mid | waist-height planting, decorative |
| `seed_tray` | a divided seed-starting tray | poor | start seedlings to transplant |

---

## 6. STRUCTURES — greenhouses, cold frames, sheds

| id | one-line | tier | role |
|----|----------|------|------|
| `cold_frame` | a low glass-lidded box over a bed | poor | extends growing season for a small bed |
| `cloche_row` | a row tunnel of hoop-and-film | common | protects a row of crops |
| `greenhouse_small` | a small glass greenhouse | mid | grows out-of-season crops inside |
| `greenhouse_large` | a big glass-and-iron greenhouse | high | many beds, climate-protected |
| `greenhouse_grand` | an ornate Victorian glasshouse | fancy | showpiece + top growing conditions |
| `potting_shed` | a small shed with a potting bench | mid | crafting/storage hub for the garden |
| `potting_bench` | a workbench with soil bins & shelf | common | pot up plants, mix soil (cf. `workbench`) |
| `hay_barn` | an open-sided hay store | mid | stores hay/straw; rustic |

---

## 7. PROCESSING (turn raw crops into goods)

Extends `sawmill`, `loom`, `keg`, `wine_rack`, `honey_extractor`.
| id | one-line | tier | makes |
|----|----------|------|-------|
| `drying_rack` | a slatted rack for drying herbs/fruit | poor | dried herbs, dried fruit, hay |
| `herb_dryer_cabinet` | a screened drying cabinet | mid | bulk-dries herbs cleanly |
| `grain_mill` | a hand-crank grain mill | common | flour from `wheat` (feeds cooking_food.md) |
| `windmill` *(exists)* | a tall windmill | high | grinds grain at scale (power, §11.6) |
| `oil_press` | a screw press for seeds | mid | oil from `sunflower_seed`, etc. |
| `cider_press` | a fruit press | mid | juice/cider from fruit |
| `fermentation_keg` (cf. `keg`) | a tapped brewing cask | mid | cider, mead (with honey), country wine |
| `wine_rack` *(exists)* | bottle storage rack | decor | ages/stores bottles |
| `cheese_press` | a screw cheese press | mid | (if dairy added) cheese |
| `seed_maker` | a bench that extracts seeds from crops | mid | recover seeds for replanting |
| `bundling_table` | a table that bundles produce for sale | common | packs crops into higher-value bundles |
| `pickling_crock` | a stoneware crock | poor | preserves/pickles (shelf-stable, value-add) |

---

## 8. AUTOMATION HINTS (plot-only, slow, capacity-capped — §11)

These are *hints* for the automation system, not finished specs. All inherit §11's rules: slow,
fill-then-stop capacity, never out-producing hands-on play. Detail lives in
`docs/brainstorms/objects/storage_automation.md`.
- `auto_sprinkler` network — covered tiles get watered on a slow tick (water source + coverage aura).
- `auto_harvester` — a slow collector that gathers ripe crops in range into an output chest; capped.
- `seed_hopper` / `auto_planter` — refills empty tilled tiles from a seed buffer, slowly.
- `compost_auto_feed` — routes farm scraps into the compost bin via a hopper.
- NPC workers (§11.2): a **Farmhand** could water/weed slowly; never fully solves the plot.
- Power/fuel: sprinklers/harvesters that need it get the §11.6 flag *when that system ships* — not
  before. Manual → fuel → electric is the intended ramp.

---

## Open questions / follow-ups
- Which crops exist is tiny right now (3). A crops brainstorm (separate) should expand the list so
  these tools have things to act on (root crops, vines, grains, herbs, flowers, gourds, berries).
- Growth-speed/quality bonus numbers belong in the ecology/economy proposal, not here.
- Decide which of greenhouse/pergola/raised beds also count as idle-boost furniture (§11.5).
