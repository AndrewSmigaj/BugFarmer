# Materials Catalog — BugFarmer Economy

> **Status:** design aggregate. Source of truth for crafting *materials & ingredients* across all 17 zone
> content sheets in [`../zones/`](../zones/) plus the existing canonical ids. **Design only — nothing wired
> in yet.** New ids are `snake_case`. ✅ = existing canonical id (already in `crafting.md` / the live data).
>
> **Scope:** raw materials, gatherables, ore/metal, bug-drop reagents, and crafted **intermediates** (bars,
> planks, cloth, cut gems, refined silk, alchemy bases). It deliberately **excludes finished gear,
> weapons, consumables, food, décor, structures, and placeables** — those live in the gear/weapon/consumable
> catalogs and the per-zone "items" ledgers. Carcasses (`dead_*`) are bug-meat cooking inputs and are folded
> into one row rather than enumerated per-species.
>
> **Columns:** `id` · `type` · `source` (forage / mine / chop / strip / drop@species / craft@station) ·
> `zone(s)` · `tier` (T1–T5) · `used for`.
>
> **Dedup note:** where two zones coined different ids for the same concept, the catalog lists a **canonical
> id** and folds the alias (called out inline as *alias:* / *fold:*). See the "Aliases to fold" subsection
> under each affected type and the consolidated list at the end.

---

## ore

Raw mineable ore — smelts to a metal bar at the furnace. The ore ladder runs copper → bronze (alloy) → iron →
steel → silver → gold → platinum, plus the cave/swamp "flavor" iron sources.

| id | type | source | zone(s) | tier | used for |
|---|---|---|---|---|---|
| `copper_ore` ✅ | ore | mine | Ant Colony (intro underground metal), Bee/Hilltop Meadow (era) | T2 | → `copper_bar` (first metal); bronze alloy |
| `coal` ✅ | ore (fuel) | mine | Ant Colony, Scorpion Rocks, Centipede Cavern, Underground Passages, Deadly Ants | T2–T3 | furnace/forge fuel; black-powder/`blast_charge`; steel heat |
| `iron_ore` ✅ | ore | mine | Scorpion Rocks (mining intro), Underground Passages (mined in volume) | T3 | → `iron_bar`; the T3 metal spine |
| `bog_iron` ✅ | ore (flavor-iron) | mine/dredge | Shallow Swamp, Deep Swamp | T3 | swamp route → `iron_bar` (no deep mine) |
| `cold_iron_ore` | ore (flavor-iron) | mine | Underground River | T3 | cave route → `iron_bar` (tackle/spear) |
| `silver_ore` ✅ | ore | mine | Spider Vale West (cave-mouth veins), Underground Passages (deep veins) | T4→T5 | → `silver_bar`; T5 bridge metal, jeweler line |
| `raw_gem` ✅ | ore (gem) | mine/drop | Underground Passages (clings to vein, glow_grub) | T3 | cut → gem; gem-luck payoff |
| `gem_geode` | ore (gem nodule) | mine | Scorpion Rocks | T3 | cracks → `quartz`/`crystal`; the `gem_luck` node |
| `cave_crystal_geode` | ore (gem nodule) | mine | Centipede Cavern | T3 | cracks → `crystal`/`quartz`/`glow_crystal`; `gem_luck` node |
| `quartz` ✅ | ore (gem) | mine/crack | Scorpion Rocks, Bee Meadow, Hilltop Meadow, Underground Passages | T2–T3 | jeweler inlay; abrasive; cut → `cut_quartz` |
| `crystal` ✅ | ore (gem) | mine/crack | Scorpion Rocks, Centipede Cavern, Underground Passages, Deadly Ants | T3+ | jeweler/lens; gem-cut intermediates |
| `glow_crystal` | ore (gem, luminous) | mine | Centipede Cavern | T3 | self-lighting crystal; cut → `cut_glow_crystal`; `light`/`gem_luck` |
| `raw_emerald` | ore (colored gem) | mine | Underground Passages | T3 | first colored gem; cut → `cut_emerald` |
| `raw_sapphire` | ore (colored gem) | mine | Underground Passages | T3→T5 | deeper/rarer gem; cut → `cut_sapphire` |
| `acid_crystal` | ore (corrosive gem) | mine | Deadly Ants | T5 | etch agent, armor-shred throwable, acid-temper |
| `granite` ✅ | ore/stone | mine | Deadly Ants (reuse), Underground Passages (crusher input) | T4 | hard building stone; forge/crusher input |
| `diamond` ✅ | ore (gem-major) | mine | Deadly Ants, Spider Vale East (gear input) | T5 | apex jewelry (`huntsman_charm`, `widow_locket`) |
| `gold_ore` (implied) ✅ | ore | mine | Deadly Ants tier (→ `gold_bar`) | T5 | → `gold_bar`; endgame jewelry/weapon |
| `platinum_ore` (implied) ✅ | ore | mine | Deadly Ants (opens the top of the ladder) | T5 | → `platinum_bar`; endgame armor |

> *(`gold_ore`/`platinum_ore` are referenced by their bars rather than mined-id in the sheets — listed for
> ladder completeness. Deadly Ants "opens the top of that ladder" but reuses the bars, not new ore ids.)*

---

## Blocks & deposits — AS-BUILT (the mineable/buildable world)

The real placeables/occupants you mine and place today (an exception to the "excludes placeables" scope above —
these *are* the raw mineral world, and they're the source of the `ore` rows). Blocks **drop themselves**
(Terraria-style): mine a `stone_block` → get a `stone_block`. **Depth shows via the floor tile + ore richness,
NOT harder block tiers** — there is exactly ONE rock, `stone_block` (no boulders/stalagmites; decided repeatedly).
**✅ = exists in the data today.**

### Building blocks (placeables — drop themselves)
| id | name | source | notes |
|---|---|---|---|
| `dirt_block` ✅ | Dirt Block | dig (shovel) | surface substrate |
| `stone_block` ✅ | Stone Block | mine (pickaxe) | **the one rock** — all stone is this |
| `sand_block` ✅ | Sand Block | dig (shovel) | desert/beach |
| `clay_block` ✅ | Clay Block | dig (shovel) | → bricks/pottery |
| `sandstone_block` ✅ | Sandstone Block | mine | desert building stone |
| `quartz_block` ✅ | Quartz Block | mine | gem-bearing stone (→ `quartz`) |
| `boulder` ✅ | Boulder | — | a `natural`-category placeable; **rocks were retired** — flagged for **your** removal/keep call |

### Ore deposits (occupants — mine for the raw ore, scaled deposit sprite via `icon_from`)
| id | name | yields | notes |
|---|---|---|---|
| `ore_copper_block` ✅ | Copper Deposit | `copper_ore` | T2 |
| `ore_tin_block` ✅ | Tin Deposit | `tin_ore` ✅ | T2 (bronze line) |
| `ore_coal_block` ✅ | Coal Deposit | `coal` | fuel |
| `ore_iron_block` ✅ | Iron Deposit | `iron_ore` | T3 |
| `ore_silver_block` ✅ | Silver Deposit | `silver_ore` | T4–T5 |
| `ore_gold_block` ✅ | Gold Deposit | `gold_ore` | T4 |
| `ore_platinum_block` ✅ | Platinum Deposit | `platinum_ore` | T5 (top, no diamond tools) |
| `ore_diamond_block` ✅ | Diamond Deposit | gem | richest deep deposit |

*Depth ramps the **count/richness** of these deposits (richest in the deepest band), not the block hardness — see
the underground-zone design. `tin_ore` ✅ is the as-built raw item.*

---

## metal-bar (smelted / crafted intermediate)

Smelted at the furnace, or alloyed/tempered at the forge. The bar ladder is the backbone tier gate.

| id | type | source | zone(s) | tier | used for |
|---|---|---|---|---|---|
| `copper_bar` ✅ | metal-bar | craft@furnace | Ant Colony, Bee/Hilltop Meadow | T2 | first metal gear/tools; bronze alloy |
| `bronze_bar` ✅ | metal-bar (alloy) | craft@furnace | Wasp Thicket, Butterfly Fields | T2 | T2 weapons/armor (venom dagger, prism goggles) |
| `iron_bar` ✅ | metal-bar | craft@furnace | Scorpion Rocks, Underground Passages, the swamps, the meadows | T3 | the T3 spine — tools, weapons, armor, lamps |
| `steel_bar` ✅ | metal-bar | craft@forge | Centipede Cavern, Millipede Forest, Locust Farmland, Deep Swamp, Spider Vales, Deadly Ants | T4 | T4 weapons/armor; alloy base for `flame_alloy` |
| `silver_bar` ✅ | metal-bar | craft@furnace | Spider Vale West/East, Underground Passages, Centipede Cavern, Locust Farmland | T4→T5 | bridge-tier accessories, buckles, jeweler line |
| `gold_bar` ✅ | metal-bar | craft@furnace | Deadly Ants, Spider Vale East/West, Butterfly Fields | T5 | endgame jewelry/weapons (Widow's set, firebrand) |
| `platinum_bar` ✅ | metal-bar | craft@furnace | Deadly Ants | T5 | endgame heavy armor (`firewarden_plate`) |
| `flame_alloy` | metal-bar (fire-tempered) | craft@forge (`steel_bar`+`ember_resin`×2+`fire_ant_gland`) | Deadly Ants | T5 | fire weapons + fire-resist armor cores; T4→T5 bridge |

### Mining refine intermediates (the gather→process→refine chain, D13)

The metal spine now runs `raw ore → [rock_crusher] → paydirt → [ore_sluice] → refined ore → [furnace/forge +coal] → bar`
(per-mineral, all 6 metals). Paydirt + refined-ore are the two new intermediate rungs between ore and bar.

| id | type | source | tier | used for |
|---|---|---|---|---|
| `copper_paydirt` ✅ | refine-intermediate | craft@rock_crusher (`copper_ore`) | T2 | → `refined_copper_ore` @ ore_sluice |
| `iron_paydirt` ✅ | refine-intermediate | craft@rock_crusher (`iron_ore`) | T3 | → `refined_iron_ore` @ ore_sluice |
| `tin_paydirt` ✅ | refine-intermediate | craft@rock_crusher (`tin_ore`) | T2 | → `refined_tin_ore` @ ore_sluice |
| `silver_paydirt` ✅ | refine-intermediate | craft@rock_crusher (`silver_ore`) | T4 | → `refined_silver_ore` @ ore_sluice |
| `gold_paydirt` ✅ | refine-intermediate | craft@rock_crusher (`gold_ore`) | T5 | → `refined_gold_ore` @ ore_sluice |
| `platinum_paydirt` ✅ | refine-intermediate | craft@rock_crusher (`platinum_ore`) | T5 | → `refined_platinum_ore` @ ore_sluice |
| `refined_copper_ore` ✅ | refined-ore | craft@ore_sluice (`copper_paydirt`) | T2 | + coal → `copper_bar` @ furnace |
| `refined_iron_ore` ✅ | refined-ore | craft@ore_sluice (`iron_paydirt`) | T3 | + coal → `iron_bar` @ furnace |
| `refined_tin_ore` ✅ | refined-ore | craft@ore_sluice (`tin_paydirt`) | T2 | → `bronze_bar` @ forge (no tin bar) |
| `refined_silver_ore` ✅ | refined-ore | craft@ore_sluice (`silver_paydirt`) | T4 | + coal → `silver_bar` @ furnace |
| `refined_gold_ore` ✅ | refined-ore | craft@ore_sluice (`gold_paydirt`) | T5 | + coal → `gold_bar` @ furnace |
| `refined_platinum_ore` ✅ | refined-ore | craft@ore_sluice (`platinum_paydirt`) | T5 | + coal → `platinum_bar` @ furnace |
| `charcoal` ✅ | fuel (coal substitute) | craft@furnace (`wood`×5) | T1 | furnace/forge fuel when coal is short |

### Gem chain (block → mine → raw gem → gem_cutter → cut gem)

Minecraft/Terraria-style: mine a **gem block** for the raw gem, then cut it at the new **`gem_cutter`** station.
Gems are sellable; their jeweler/accessory consumers are backlogged.

| raw gem | gem block (occupant) | cut gem | tier |
|---|---|---|---|
| `diamond` ✅ | `ore_diamond_block` ✅ | `cut_diamond` ✅ | T5 |
| `ruby` ✅ | `ore_ruby_block` ✅ | `cut_ruby` ✅ | T4 |
| `sapphire` ✅ | `ore_sapphire_block` ✅ | `cut_sapphire` ✅ | T4 |
| `emerald` ✅ | `ore_emerald_block` ✅ | `cut_emerald` ✅ | T3 |
| `quartz` ✅ | `quartz_block` ✅ | `cut_quartz` ✅ | T2 |

---

## wood

Common timber, the premium hardwood line, and salvaged/specialty woods.

| id | type | source | zone(s) | tier | used for |
|---|---|---|---|---|---|
| `wood` ✅ | wood | chop/forage | Village + every zone (era base) | T1 | the universal cheap structure/haft/tool base |
| `plank` ✅ | wood (milled) | craft@sawmill | Village + every zone | T1 | milled board — furniture, structures, hafts |
| `hardwood` | wood (premium) | chop | Millipede Forest | T4 | premium old-growth timber → `hardwood_plank`, hafts |
| `hardwood_plank` | wood (premium, milled) | craft@sawmill (`hardwood`×2) | Millipede Forest | T4 | T4 structures, beams, weapon hafts, set frame |
| `bark_strip` | wood (bark) | strip | Millipede Forest | T4 | tannin source → tannic leather/dye; alchemy base; binder |
| `bored_bark` | wood (galleried bark) | drop@bark_beetle | Millipede Forest | T4 | bark alchemy + rustic décor |
| `sunken_log` | wood (bog-oak) | dredge/dive | Deep Swamp | T4 | water-resistant `bogwood_plank`; stilt/boat line; dark haft |
| `bogwood_plank` | wood (water-resistant, milled) | craft@sawmill (`sunken_log`) | Deep Swamp | T3 | stilt platforms, boats, weapon hafts |
| `thatch` | wood/reed (roofing) | craft@sawmill (`reed_stalk`×4) | Shallow Swamp | T1–T2 | swamp-shack roofing/walls |

---

## fiber

Plant/animal raw cordage fibers and their thread intermediate. (Cloth bolts are under **cloth**.)

| id | type | source | zone(s) | tier | used for |
|---|---|---|---|---|---|
| `fiber` ✅ | fiber | forage/drop | Village + every zone | T1 | the universal cheap cordage/weave base |
| `thread` ✅ | fiber (spun) | craft@loom | every cloth zone | T1–T3 | spun thread — the bridge fiber→cloth |
| `reed_stalk` | fiber (reed) | forage@reeds | Shallow Swamp | T2 | → `reed_fiber`; thatch; snorkel tube |
| `reed_fiber` | fiber (reed cordage) | craft (`reed_stalk`×3) | Shallow Swamp, Deep Swamp, Underground River | T2 | coarse cordage/matting; wader weaves, nets, traps |
| `cattail_fluff` | fiber (buoyant) | forage@cattail | Shallow Swamp, Deep Swamp | T2 | float/cork substitute (water-walk soles, life-vest); padding |
| `pale_root` | fiber (cave plant) | forage | Underground River | T3 | `pale_line` cordage; angler-line/net weave; anti-cold note |
| `leaf_disc` | fiber (leaf, meadow) | drop@leafcutter_bee | Bee Meadow | T1 | meadow `fiber` substitute (wraps, woven mats, wax-wrap) |
| `milkweed_silk` | fiber (plant floss) | forage@milkweed | Butterfly Fields | T2 | plant silk; soft cloth filler, cushion stuffing |
| `thistle_down` | fiber (fluff) | forage@thistle/dandelion | Hilltop Meadow | T1 | stuffing, fire-tinder, parachute-seed décor; cheap `fiber` |
| `bumble_fuzz` | fiber (bee-pile) | drop@bumblebee | Hilltop Meadow | T2 | insulating felt; pollinator-outfit lining; hand-pollinator brush |
| `nymph_husk` | fiber (molt) | drop@swarmling_nymph | Locust Farmland | T4 | cheap bulk filler (mulch, paper-chitin, bait); compost |
| `hardened_husk` | fiber (plate) | forage/mine | Locust Farmland | T4 | tough fibrous plate (between plank & chitin); walls, armor backing |
| `cobweb` ✅ | fiber (raw web) | drop@web_tender / forage | Spider Vale West | T4 | cheap bulk web — web-traps, binder, net-mesh, stuffing |

### Aliases to fold (fiber)
- `pale_line` (Underground River loom output) and `reed_fiber` (Shallow Swamp) are both "cave/water plant
  cordage cloth-substitute." Keep both (different plant source) **or** fold `pale_line` → `reed_fiber` if
  pruning; `pale_line` is the cave-native variant.

---

## cloth

Spun/woven bolts: the common cloth ladder and the silk-cloth line (see **silk ladder** at end).

| id | type | source | zone(s) | tier | used for |
|---|---|---|---|---|---|
| `cloth` ✅ | cloth | craft@loom | every cloth zone | T2 | the canonical cloth bolt; beekeeper/marsh/diver weaves |
| `silk` ✅ | cloth (silk) | craft@loom (`spun_silk`) | Butterfly Fields, Spider Vales | T3 | premium soft-good; cloaks, sashes, nets |
| `spun_silk` ✅ | cloth (silk, spun) | craft@loom (raw cocoon/thread) | Butterfly Fields, Spider Vales | T2–T3 | gateway: raw thread → usable `silk` |
| `silk_cloth` ✅ | cloth (silk bolt) | craft@loom | Butterfly Fields, Spider Vale East | T2 | premium cloth bolt (= `moth_silk_cloth`) |
| `kelp_weave` | cloth (sealing) | craft@loom (`deepwater_kelp`×4) | Deep Swamp, Underground River | T3 | stretchy sealing fabric; wet-suit/diver weave (`cloth` sub) |
| `chitin_weave` | cloth (scale-mesh) | craft@loom (`crop_beetle_shell`+`locust_wing`+`thread`) | Locust Farmland | T4 | chitin-scale armor textile; the warden set weave |
| `tanned_hide` ✅ | cloth (leather) | craft@dye_vat/cauldron (hide/`reed_fiber`+`tannin`) | Shallow/Deep Swamp, Underground River | T2 | water-resistant leather; wader/diver set base |
| `tanned_leather` | cloth (tannic leather) | craft@dye_vat (`bark_strip`×3 + hide/`fiber`) | Millipede Forest | T4 | tannic-cured leather; warden underweave, straps |
| `refined_silk` | cloth (top-grade silk, spun) | craft@loom (`orb_silk`/`broodmother_silk`+`silk_gland`) | Spider Vale West | T4 | top-grade usable silk; gateway to premium cloth |
| `spider_silk_cloth` | cloth (premium silk bolt) | craft@loom (`refined_silk`+`thread`) | Spider Vale West | T4 | best cloth so far; all silk armor/artisan goods |
| `gossamer_cloth` | cloth (quality silk bolt) | craft@loom (`spider_silk_cloth`+`gossamer_dew`) | Spider Vale West | T4→T5 | dew-lightened cloth; gates the T5 cape |
| `royal_silk_cloth` | cloth (endgame silk bolt) | craft@loom (`royal_silk`+`spun_silk`) | Spider Vale East | T5 | endgame cloth; the Widow's-set keystone |
| `glow_thread` | cloth (luminous thread) | craft@loom (`glow_silk`×2+`thread`) | Centipede Cavern | T3 | glow-trim textile base; set underweave, glow décor |

### Aliases to fold (cloth)
- **`silk_cloth` ✅ = `moth_silk_cloth`** (Butterfly Fields names the recipe `moth_silk_cloth` but maps it to
  the canonical `silk_cloth`). Canonical = `silk_cloth`; fold `moth_silk_cloth`.
- **`emperor_silk_cloth`** (Butterfly Fields, premium T3) is a distinct higher tier — keep separate or fold
  into the `silk_cloth`→`spider_silk_cloth` ladder as the bridge rung.
- `tanned_hide` ✅ (swamp) vs `tanned_leather` (forest): same concept, different tannin source (swamp
  reed/hide vs forest bark). Canonical = `tanned_hide` for water gear; `tanned_leather` for the forest
  tannic line. Fold to one (`tanned_hide`) on prune.

---

## flora (herbs, flowers, plant gatherables)

Foraged plants — dye/alchemy/cooking ingredients. The canonical herb/flower set + zone-specific flora.

| id | type | source | zone(s) | tier | used for |
|---|---|---|---|---|---|
| `chamomile` ✅ | flora (herb) | forage | Village, Bee Meadow, Butterfly Fields | T1 | calm/dye; pollination dust; luck draught |
| `lavender` ✅ | flora (herb) | forage | Village, Bee Meadow, Butterfly Fields, Locust | T1 | calm_spray/incense; swarm repellent |
| `yarrow` ✅ | flora (herb) | forage | Village, Bee/Hilltop Meadow, Scorpion Rocks, Locust | T1 | salve/`hp_regen`; antidote; blight antidote |
| `milkweed` ✅ | flora (host plant) | forage | Butterfly Fields | T2 | monarch host; → `milkweed_silk` floss |
| `poppy` ✅ | flora (flower) | forage | Village, Bee Meadow | T1 | red dye; cooking |
| `dandelion` ✅ | flora (flower) | forage | Village, Bee Meadow, Butterfly Fields, Hilltop | T1 | yellow dye; amber dye; thistle-down forage |
| `clover` ✅ | flora (flower) | forage | Village, Bee/Hilltop Meadow | T1 | green dye; `clover_honey`; meadow_mead |
| `mint` ✅ | flora (herb) | forage | Village, Butterfly Fields, Deep Swamp, Spider Vales | T1 | nightsight/nimble brews; cooling; antidote |
| `sage` ✅ | flora (herb) | forage | Village, Butterfly Fields, Millipede Forest, Spider Vales, Deep Swamp | T1 | incense; jerky cure; antidote |
| `thyme` ✅ | flora (herb) | forage | Village, Butterfly Fields, Locust | T1 | steady-hand tea; cricket skewer |
| `fennel` ✅ | flora (herb) | forage | Village | T1 | green dye |
| `nettle_leaf` | flora (irritant) | forage | Wasp Thicket, Hilltop Meadow | T2 | poison + antidote (counter-irritant) |
| `cave_nettle` | flora (irritant, hardy) | forage | Spider Vale East | T5 | heavy-`envenomed` antivenom counter-irritant |
| `bramble_vine` | flora (thorn cordage) | cut | Wasp Thicket, Hilltop Meadow | T2 | thorns mechanic; thicket armor/traps; hornet lance |
| `gorse_thorn` | flora (thorn) | forage/mine | Spider Vale West | T4 | thorns accessory; trap barb; astringent brew |
| `aloe_leaf` | flora (succulent) | forage | Scorpion Rocks, Deadly Ants (reuse) | T3 | heat-salve + antivenom; cures corroded/envenomed |
| `dust_lichen` | flora (lichen) | forage | Scorpion Rocks | T3 | cheap dye/binder; canteen water-purifier note |
| `cave_moss` ✅ | flora (cave) | forage/strip | Ant Colony, Centipede Cavern, Underground Passages/River, Spider Vale West | T1 | green/glow dye/binder; poultice; soft décor moss |
| `forest_moss` | flora (moss) | forage | Millipede Forest | T4 | green dye/binder; bark-salve poultice; décor moss |
| `gloom_moss` | flora (luminescent) | forage | Spider Vale East | T5 | glow-lamp; night_vision tonic; glow-dye (cheap survival) |
| `nectar_bloom` | flora (flower bundle) | forage@flower_patch | Bee Meadow | T1 | cooking sweetener; calm_spray base; floral mead |
| `swamp_lotus` | flora (deep bloom) | forage/dive | Deep Swamp | T3–T4 | → `lotus_essence`; calm + anti-disease base; dye |
| `litter_mulch` | flora (leaf-litter) | forage | Millipede Forest | T4 | premium compost; mushroom substrate; armor padding |
| `leaf_litter` | flora (mulch) | drop@pill_bug / forage | Village | T1 | compost; growth mulch; gardener-glove input |
| `frog_spawn` | flora-adjacent (alchemy) | forage/skim | Shallow Swamp | T2 | rare dodge/agility brew reagent; bait |
| `frog_toxin` | flora-adjacent (poison) | milk@bog frogs | Deep Swamp | T4 | poison weapon-coat; antidote component; agility note |

### Canonical flora set (per the brief)
`chamomile, lavender, yarrow, milkweed, poppy, dandelion, clover, mint, sage, thyme, fennel` — all ✅ existing.

---

## mushroom (fungus)

Foraged fungi — alchemy/cooking/light/farming inputs. Includes the unique ant-farmed fungus chain.

| id | type | source | zone(s) | tier | used for |
|---|---|---|---|---|---|
| `mushroom_brown` ✅ | mushroom | forage | Village, Wasp Thicket | T1 | forager stew; antidote filter |
| `mushroom_glow` ✅ | mushroom (bioluminescent) | forage | Ant Colony, Centipede Cavern, Underground Passages/River, Deep Swamp | T1 | free cave light; glow-fungus alchemy; night_vision note |
| `mushroom_bracket` ✅ | mushroom (shelf) | forage | Millipede Forest | T1 | forest fungus alchemy; `hp_regen` tonic; tanning note |
| `mushroom_morel` ✅ | mushroom (prized) | forage | Millipede Forest | T2 | premium forest food/potion; luck cooking note |
| `glowshroom` | mushroom (bright cave) | forage | Underground Passages | T1 | lantern fuel; night-eye potion; light meal; dye |
| `serpent_glow_cap` | mushroom (deep bog glow) | forage | Deep Swamp | T3 | sustained `light_radius` reagent; glowcap oil; dye |
| `ant_fungus` ✅ | mushroom (ant-farmed) | forage@gardens / drop@black_ant | Ant Colony | T2 | the fungus food chain; fungus-leather armor binder |
| `mycelium_mat` | mushroom (root-web) | forage | Ant Colony | T2 | premium fungus-leather; compost substrate; farm "seed" |
| `fungal_spore` | mushroom (spore pod) | forage | Ant Colony | T2 | inoculant (seed a fungus garden); bait; spore-bomb base |

### Aliases to fold (mushroom)
- `glowshroom` (Underground Passages) and `mushroom_glow` ✅ are near-identical bioluminescent caps — keep
  `glowshroom` as the "brighter cultivated" variant **or** fold into `mushroom_glow`. `serpent_glow_cap` /
  `glow_spore` (Underground River) are the same family; `glow_spore` is the harvested fungal light reagent.

---

## fruit

Tree fruit and pressed/specialty fruit. (Most fruit/crops are canonical farm produce reused everywhere.)

| id | type | source | zone(s) | tier | used for |
|---|---|---|---|---|---|
| `apple` ✅ | fruit | forage/farm | Village, Hilltop Meadow | T1 | apple tart; bumble butter; cider |
| `berries` ✅ | fruit | forage | Butterfly Fields | T2 | glowberry tart |
| `pressed_apple` | fruit (pressed) | forage/press | Village | T1 | early "cider must" cooking input; sweet bait |
| `plum` ✅ | fruit | farm/tree | (tree_plum art) | T1 | cooking; rot → fly food (ecology) |
| `cherry` ✅ | fruit | farm/tree | (tree_cherry art) | T1 | cooking; rot → fly food (ecology) |

### As-built rotten fruit + seeds (ecology / forage)
| id | type | source | used for |
|---|---|---|---|
| `rotten_apple` ✅ | rotten fruit | fruit rots on ground | **detritivore/fly food** (ecology); compost |
| `rotten_orange` ✅ | rotten fruit | fruit rots on ground | detritivore/fly food; compost |
| `rotten_plum` ✅ | rotten fruit | fruit rots on ground | detritivore/fly food; compost |
| `rotten_cherry` ✅ | rotten fruit | fruit rots on ground | detritivore/fly food; compost |
| `sunflower_seed` ✅ | seed/forage | forage `sunflower` | bird/bug feed; oil; replant |

*(Crop **seeds** — `seed_wheat`/`seed_carrot`/… — are catalogued with the grow loop in [`plants.md`](plants.md).)*

---

## crop

Farmed produce — the seed/grow loop. All canonical; reused across cooking recipes.

| id | type | source | zone(s) | tier | used for |
|---|---|---|---|---|---|
| `wheat` ✅ | crop | farm | Village + cooking everywhere | T1 | bread, cakes, tarts, biscuits |
| `corn` ✅ | crop | farm | Village, Butterfly Fields, Locust | T1 | monarch feast; harvester feast; porridge |
| `carrot` ✅ | crop | farm | Village, Locust | T1 | salad; fungus stew; warden stew |
| `cabbage` ✅ | crop | farm | Village, Locust | T1 | salad; warden stew |
| `pumpkin` ✅ | crop | farm | Village, Butterfly Fields, Locust | T1 | monarch feast; harvester feast |
| `tomato` ✅ | crop | farm | Village | T1 | cooking staple |
| `eggplant` ✅ | crop | farm | Locust | T4 | cricket skewer |
| `blighted_grain` | crop (devastated) | forage | Locust Farmland | T4 | swarm food/bait; grim ration; compost |

---

## gem (cut / processed gemstone)

Crafted gem intermediates — cut at the jeweler/stonecutter from raw ore/geodes. (Raw gem ore is under **ore**.)

| id | type | source | zone(s) | tier | used for |
|---|---|---|---|---|---|
| `cut_quartz` | gem (cut) | craft@jeweler (`quartz`×2+`vinegaroon_acid`) | Scorpion Rocks | T3 | jewelry/inlay; quartz pendant; prospector band |
| `cut_glowquartz` | gem (cut, luminous) | craft@jeweler (`glow_quartz`×2+`formic_etch`) | Ant Colony | T2→T3 | self-glowing quartz; lamp/inlay; colonist charm |
| `cut_glow_crystal` | gem (cut, luminous) | craft@jeweler (`glow_crystal`×2+`cave_nitre`) | Centipede Cavern | T3 | glowstone amulet; lantern lens; set inlay |
| `cut_emerald` | gem (cut, green) | craft@jeweler (`raw_emerald`×2+`quartz`) | Underground Passages | T3 | fortune drill; spelunker band; lamp lens |
| `cut_sapphire` | gem (cut, blue) | craft@jeweler (`raw_sapphire`×2+`cave_nitre`) | Underground Passages | T3→T5 | marquee accessory; headlamp focusing lens |
| `prism_dust` | gem (refractive grit) | craft@jeweler (`glass_scale`+`quartz`) | Butterfly Fields | T2→T3 | prism lens; `gem_luck` charm core; shimmer glaze |
| `nacre_inlay` | gem (mother-of-pearl) | craft@jeweler (`freshwater_nacre`+`larva_case`) | Underground River | T3 | charm inlay; luxury décor; pearlescent finish |
| `cave_pearl` | gem (freshwater pearl) | dive/drop | Underground River | T4 | gem-minor jeweler core; pearl accessory; treasure |
| `bog_pearl` | gem (dark pearl) | dive/drop | Deep Swamp | T4 | gem-minor; deep-water charm cores; luxury sell |
| `cave_quartz` | gem (swamp-native quartz) | mine | Deep Swamp, Underground River (reuse) | T3 | jeweler ladder w/o dry mine; diver-helm lens, charm core |
| `cave_nitre` | gem (clear druse) / mineral | mine | Centipede Cavern, Underground Passages | T2–T3 | lens/optics crystal; gem-cut etch; light line |

> *Note:* `glow_quartz` (Ant Colony) is mined ore → cuts to `cut_glowquartz`; `glow_crystal` (Centipede
> Cavern) is mined ore → cuts to `cut_glow_crystal`. Both raw forms are listed under **ore**; the cut forms here.

### Aliases to fold (gem)
- `glow_quartz` / `cut_glowquartz` (Ant Colony) and `glow_crystal` / `cut_glow_crystal` (Centipede Cavern)
  are the same "self-lighting cuttable crystal" concept one tier apart. Keep as a tier ladder
  (`glow_quartz` T2 → `glow_crystal` T3) **or** fold to one luminous-crystal line on prune.
- `cave_nitre` appears as both a "lens/optics crystal" (gem-class, Underground Passages) and a
  "preservation/etch evaporite" (Centipede Cavern). Same id, dual use — keep one id, note both uses.

---

## bug-drop (species-signature reagents)

Reagents dropped by bugs — the combat/catch loot that feeds gear lines. Carcasses (`dead_*`) are folded into
one row at the end. Grouped loosely by theme; venom/silk/chitin/formic *ladders* are summarized at the end.

### Venom & poison drops
| id | type | source | zone(s) | tier | used for |
|---|---|---|---|---|---|
| `venom_sac` ✅ | bug-drop (venom, mid) | drop@paper_wasp/mud_dauber | Wasp Thicket | T2 | venom dagger/vial; the mid venom tier |
| `royal_venom` | bug-drop (venom, boss) | drop@thicket_matriarch | Wasp Thicket | T2 | upgraded venom; forward hook to T3 |
| `venom` ✅ | bug-drop (venom, generic) | drop | Deadly Ants, ecology | T4 | generic venom reagent (cost-model "venom") |
| `scorpion_venom` | bug-drop (venom, strong) | drop@bark_scorpion | Scorpion Rocks | T3 | strong venom weapons/coatings; antivenom base |
| `potent_venom` ✅ | bug-drop (venom, apex) | drop@den_matron / huntsman | Scorpion Rocks, Spider Vale East (reuse) | T3→T4 | marquee venom weapon; forward hook to next tier |
| `mosquito_proboscis` ✅ | bug-drop (venom-adjacent) | drop@marsh/swamp_mosquito | Shallow/Deep Swamp | T2–T3 | cheap poison coatings; bait |
| `mosquito_venom` | bug-drop (fever venom) | drop@swamp_mosquito | Deep Swamp | T3 | cheap T3 venom reagent; fever-bombs; bait |
| `spider_venom` | bug-drop (venom, strong/light) | drop@orb_weaver/wolf_spider; cave_spider | Spider Vale West (strong), Underground Passages (light) | T3–T4 | venom weapons/coatings; antivenom/antidote base |
| `centipede_venom` | bug-drop (venom, paralytic) | drop@armored_centipede | Spider Vale West | T4 | slow/stun coating; paralytic trap charge |
| `centipede_venom_gland` | bug-drop (venom, strong) | drop@giant_centipede | Centipede Cavern | T3 | fast venom weapons + coating |
| `potent_centipede_venom` | bug-drop (venom, apex) | drop@centipede_matron | Centipede Cavern | T3→T4 | marquee apex venom weapon; T4 hook |
| `widow_venom` | bug-drop (venom, strongest) | drop@black_widow | Spider Vale East | T5 | strongest venom weapons/coatings/bomb |
| `queen_venom` | bug-drop (venom, hottest) | drop@war_queen | Deadly Ants | T5 | hottest venom coating/weapon (above potent_venom) |
| `waterbug_venom_gland` | bug-drop (venom, potent) | drop@giant_water_bug | Deep Swamp | T4 | strongest poison coats; disease-cure base |
| `hornet_venom` | bug-drop (venom, T3) | drop@hornet | Hilltop Meadow | T3 | venom weapons; antivenom; venom bomb |
| `bullet_ant_stinger` | bug-drop (venom-crit) | drop@bullet_ant | Deadly Ants | T5 | venom-crit sidearm; acid_lance |
| `tick_sac` | bug-drop (leech venom) | drop@desert_tick | Scorpion Rocks | T3 | HP-leech/lifesteal coating; bait; repellent |
| `leech_extract` ✅ | bug-drop (anticoagulant) | drop@leech/swamp_leech | Shallow/Deep Swamp | T2–T3 | water-breath potion; anticoagulant salve; cure base |
| `defensive_toxin` | bug-drop (noxious) | drop@giant_millipede | Millipede Forest | T4 | antitoxin/venom-coat input (the cyanide cloud) |

### Formic / acid drops
| id | type | source | zone(s) | tier | used for |
|---|---|---|---|---|---|
| `formic_dab` ✅ | bug-drop (formic, common) | drop@garden/black ant | Village, Ant Colony | T1–T2 | cleaning/etch agent; sour cooking note; salve |
| `formic_acid` ✅ | bug-drop (formic, concentrated) | drop@soldier_ant | Ant Colony, Deadly Ants | T2 | formic alchemy (etch, cleaner, acid flask, salve) |
| `vinegaroon_acid` | bug-drop (acetic acid) | drop@vinegaroon | Scorpion Rocks | T3 | gem-cut etch; armor-shred throwable |
| `fire_ant_gland` | bug-drop (fire/ignite) | drop@fire_ant | Deadly Ants | T5 | fire weapons/coatings AND fire-resist temper |

### Chitin / carapace / plate drops
| id | type | source | zone(s) | tier | used for |
|---|---|---|---|---|---|
| `chitin` ✅ | bug-drop (chitin) | drop@many | Wasp Thicket → endgame (universal) | T2+ | the universal armor-chitin base; underweave, plates |
| `soldier_chitin` ✅ | bug-drop (chitin plate) | drop@soldier_ant | Ant Colony | T2→T3 | ant-chitin light-armor plating |
| `queen_chitin` | bug-drop (chitin, rare) | drop@colony_queen | Ant Colony | T3 | keystone armor piece; royal trophy/décor |
| `harvester_mandible` ✅ | bug-drop (mandible) | drop@harvester_ant | Ant Colony | T2→T3 | pincer-grip tools; armor gauntlet |
| `seed_husk` | bug-drop (granary chaff) | drop@harvester_ant | Ant Colony | T2 | compost/fertilizer; feed input |
| `cave_beetle_carapace` ✅ | bug-drop (wing-case) | drop@cave_beetle | Centipede Cavern | T3 | Deep Delver armor plating; buckler |
| `camel_cricket_leg` ✅ | bug-drop (spring leg) | drop@camel_cricket | Centipede Cavern | T3 | spring cordage; greaves/boots (fall_resist/move_speed) |
| `centipede_parts` ✅ | bug-drop (segments) | drop@centipede | Shallow Swamp, Centipede Cavern | T3 | venom dagger; segmented flex-plate; set underweave |
| `millipede_segment` ✅ | bug-drop (segment plate) | drop@giant_millipede | Millipede Forest | T4 | segmented flex-plating (light armor/greaves); thorns trinket |
| `forest_centipede_fang` ✅ | bug-drop (fang) | drop@forest_centipede | Millipede Forest | T4 | venom-coating; barbed dagger/thorns reagent |
| `bark_beetle_jaw` ✅ | bug-drop (jaw) | drop@bark_beetle | Millipede Forest | T4 | bark/fungus alchemy line |
| `stag_horn` ✅ | bug-drop (horn) | drop@stag_beetle | Millipede Forest | T4 | the marquee horn melee; warden pauldron spikes |
| `beetle_carapace` | bug-drop (wing-case) | drop@stag/rhino beetle | Millipede Forest | T4 | Carapace Warden plating |
| `prime_carapace` | bug-drop (apex plate) | drop@rhino_beetle | Millipede Forest | T4 | keystone warden plate; T5 hook |
| `rhino_horn` | bug-drop (apex horn) | drop@rhino_beetle | Millipede Forest | T4→T5 | upgraded horn weapon (`rhino_breaker`) |
| `timber_shell` | bug-drop (snail shell) | drop@forest_snail | Millipede Forest | T4 | décor; lime/grit |
| `army_ant_mandible` | bug-drop (mandible) | drop@army_ant | Deadly Ants | T5 | swarm-breaker AoE weapon; swarm-defense item |
| `soldier_ant_plate` | bug-drop (back-plate) | drop@soldier_ant | Deadly Ants | T5 | endgame heavy armor; → `elite_chitin` |
| `war_queen_chitin` | bug-drop (best chitin) | drop@war_queen | Deadly Ants | T5 | set keystone (Fire-Warden crown); trophy |
| `elite_chitin` | bug-drop (refined plate) | craft@forge (`chitin`×3+`soldier_ant_plate`) | Deadly Ants | T5 | endgame armor backbone (chitin = platinum_bar tier) |
| `hornet_carapace` | bug-drop (chitin plate) | drop@hornet | Hilltop Meadow | T3 | T3 carapace armor; trophy; jeweler inlay |
| `scorpion_claw` | bug-drop (pincer) | drop@bark_scorpion | Scorpion Rocks | T3 | pincer tools/weapons; miner grip |
| `harvestman_leg` | bug-drop (springy leg) | drop@harvestman | Scorpion Rocks | T3 | springy cordage; harness/climbing (fall_resist, reach) |
| `matron_carapace` | bug-drop (trophy) | drop@den_matron | Scorpion Rocks | T3 | rare décor/trophy |
| `scorpion_brood` | bug-drop (larvae) | drop@den_matron | Scorpion Rocks | T3 | venom/armor input |
| `crop_beetle_shell` | bug-drop (carapace) | drop@crop_beetle | Locust Farmland | T4 | heavy crop-defense plating; warden body armor |
| `beetle_mandible` | bug-drop (jaw) | drop@crop_beetle | Locust Farmland | T4 | harvest sickle edge; grinder station part |
| `locust_wing` | bug-drop (flight wing) | drop@desert_locust | Locust Farmland | T4 | swarm-warden armor; lure/bait; glider décor |
| `grasshopper_leg` | bug-drop (spring leg) | drop@giant_grasshopper | Locust Farmland | T4 | mobility/knockback gear; food; launcher part |
| `cricket_song_organ` | bug-drop (stridulation) | drop@field_cricket | Locust Farmland | T4 | swarm-LURE tech; sonic/calm-counter; music décor |
| `mantis_scythe` | bug-drop (raptorial blade) | drop@mantis_reaper | Locust Farmland | T5 | high-end swarm-clearing weapon edge; trophy |
| `reaper_chitin` | bug-drop (apex carapace) | drop@mantis_reaper | Locust Farmland | T5 | warden set capstone plating |
| `earwig_pincer` | bug-drop (pincer) | drop@earwig | Wasp Thicket | T2 | (combat drop) |
| `silverfish_scale` | bug-drop (scale) | drop@silverfish | Wasp Thicket | T2 | (combat drop) |
| `whirligig_shell` | bug-drop (carapace) | drop@whirligig_beetle | Shallow Swamp | T2 | light carapace plating (wader armor); clarity lens |
| `blind_beetle_shell` ✅ | bug-drop (pale plate) | drop@blind_beetle | Underground Passages | T3 | spelunker armor; shell_buckler |
| `mole_cricket_claw` ✅ | bug-drop (digging claw) | drop@mole_cricket | Underground Passages | T3 | deepcut pick; mine-cart dig-bit |
| `crayfish_claw` | bug-drop (pincer) | drop@cave_crayfish | Underground River | T3 | edged-tool component; angler-tackle barb |
| `crayfish_shell` | bug-drop (tail plate) | drop@cave_crayfish | Underground River | T3 | light aquatic carapace plating (diver gear) |
| `water_beetle_shell` | bug-drop (domed carapace) | drop@water_beetle | Underground River | T3 | air-trapping diver helm liner; diver gear |
| `albino_chitin` | bug-drop (pale plate) | drop@albino_isopod | Underground River | T3 | light/clarity plating; charm core; rarity sell |
| `giant_waterbug_carapace` | bug-drop (apex plate) | drop@giant_water_bug | Deep Swamp | T4 | apex armor plate; deep-diver set plating |
| `nymph_jaw` | bug-drop (mask-jaw) | drop@dragonfly_nymph | Deep Swamp | T4 | edged weapon component (reach + bite) |
| `cave_crab_carapace` | bug-drop (apex shield) | drop@cave_crab | Underground River | T4 | apex armor plate; diver set high-defense build |
| `crab_claw` | bug-drop (crushing pincer) | drop@cave_crab | Underground River | T4 | anti-apex weapon component |
| `tarantula_hair` | bug-drop (urticating) | drop@tarantula | Spider Vale East | T5 | irritant throwable; barbed `thorns` armor lining |
| `huntsman_fang` ✅ | bug-drop (fang) | drop@giant_huntsman | Spider Vale East | T5 | marquee venom weapon fang-blade; apex accessory |
| `huntsman_eye` | bug-drop (eye, rare) | drop@giant_huntsman | Spider Vale East | T5 | apex accessory input (`huntsman_charm`) |
| `huntsman_carapace` | bug-drop (trophy) | drop@giant_huntsman | Spider Vale East | T5 | rare décor/trophy |
| `wolf_fang` ✅ | bug-drop (fang) | drop@wolf_spider | Spider Vale West | T4 | fanged daggers/spears; grip pieces |
| `jumping_spider_eye` ✅ | bug-drop (eye) | drop@jumping_spider | Spider Vale West | T4 | crit/precision charm; décor/scope lens |
| `centipede_plate` ✅ | bug-drop (plate) | drop@armored_centipede | Spider Vale West | T4 | light flexible armor plating |
| `matron_fang` | bug-drop (trophy) | drop@vale_matron | Spider Vale West | T4 | rare wall trophy |
| `matron_forcipule` | bug-drop (fang trophy) | drop@centipede_matron | Centipede Cavern | T3 | heavier venom-weapon variant; décor |
| `springtail_dust` ✅ | bug-drop (luminescent spore) | drop@springtail | Underground Passages | T3 | light reagent; cheap dye; fungus-bait |
| `pill_chitin` | bug-drop (tiny plate) | drop@pill_bug | Village | T1 | first light-armor plating (Forager's Kit) |
| `ladybug_shell` | bug-drop (elytra) | drop@ladybug | Village | T1 | luck trinket/charm; red dye; décor inlay |
| `snail_shell` | bug-drop (spiral shell) | drop@garden_snail | Village | T1 | décor; lime/grit for stonecutter |
| `aphid_cluster` | bug-drop (colony) | drop@aphid | Village | T1 | compost; ladybug bait |
| `mud_dauber_clay` | bug-drop (clay) | drop@mud_dauber | Wasp Thicket | T2 | (clay variant; mud-dauber gear) |
| `wasp_stinger` ✅ | bug-drop (stinger) | drop@paper_wasp | Wasp Thicket, Hilltop Meadow | T2 | stinger spear; pendant |
| `paper_nest` ✅ | bug-drop (nest) | drop@thicket_matriarch | Wasp Thicket | T2 | (looted nest chunk) |
| `wasp_larvae` ✅ | bug-drop (larvae) | drop@thicket_matriarch | Wasp Thicket | T2 | (brood input) |
| `matriarch_trophy` | bug-drop (trophy) | drop@thicket_matriarch | Wasp Thicket | T2 | rare décor/idle-aura |
| `ant_egg` ✅ | bug-drop (brood pearl) | drop@garden/colony ant | Village, Ant Colony, Deadly Ants | T1–T5 | bait; fertilizer; ant-farm brood trade |
| `royal_jelly_ant` ✅ | bug-drop (royal jelly) | drop@colony_queen | Ant Colony | T3 | marquee buff food; queen-tier alchemy reagent |
| `royal_pheromone` | bug-drop (pheromone) | drop@colony_queen | Ant Colony | T3 | colony-command reagent (`pheromone_whistle`) |
| `dead_*` (carcasses) ✅ | bug-drop (carcass) | drop@any species | every zone | T1+ | bug-meat — jerky/cooking; compost; bait. (`dead_fly/ant/beetle/wasp/spider/centipede/scorpion/...` — one per species) |

### Silk / web drops
| id | type | source | zone(s) | tier | used for |
|---|---|---|---|---|---|
| `spider_silk` ✅ | bug-drop (silk, common) | forage/drop@web_tender | Butterfly Fields, Spider Vales | T3 | net mesh upgrade; tough silk blend; base of the silk ladder |
| `orb_silk` ✅ | bug-drop (silk, premium) | drop/harvest@orb_weaver | Spider Vale West | T4 | → `refined_silk` → `spider_silk_cloth` (premium thread) |
| `broodmother_silk` ✅ | bug-drop (silk, top) | drop@vale_matron | Spider Vale West | T4 | T5 marquee cloth/cape thread (Silk-Stalker keystone) |
| `silk_gland` | bug-drop (refining catalyst) | drop@vale_matron | Spider Vale West | T4 | loom catalyst → top-grade `refined_silk`; gates T5 |
| `royal_silk` | bug-drop (silk, endgame) | drop@giant_huntsman | Spider Vale East | T5 | → `royal_silk_cloth`; the Widow's-set keystone |
| `trapdoor_silk` ✅ | bug-drop (dense silk) | drop@trapdoor_spider | Spider Vale East | T5 | densest silk → endgame armor body; heavy net/trap |
| `web_silk` | bug-drop (silk) | drop@black_widow (reuse from West) | Spider Vale West/East | T4–T5 | tough cordage/web-weave |
| `cave_spider_silk` ✅ | bug-drop (fine cave silk) | drop@cave_spider | Underground Passages | T3 | spelunker weave; hauling rope/harness; net upgrade |
| `glow_silk` | bug-drop (luminous thread) | drop@glowworm | Centipede Cavern | T3 | → `glow_thread` glow-textile; light décor |
| `moth_silk` | bug-drop (cocoon thread) | drop@luna_moth | Butterfly Fields | T2 | → `spun_silk`/`silk`; moth-silk cloth |
| `emperor_silk` | bug-drop (premium thread) | drop@emperor_moth | Butterfly Fields | T3 | premium silk cloth (`emperor_silk_cloth`, T3 gear) |
| `hawkmoth_silk` | bug-drop (fine fast-spun) | drop@hawk_moth | Butterfly Fields | T2 | lightest silk for the speed trinket |
| `spiderling_cluster` | bug-drop (venom filler) | drop@spiderling_swarm | Spider Vale East | T5 | venom-input filler; vendor sell |
| `egg_sac` | bug-drop/nest (burst nest) | drop@spiderling/widow brood | Spider Vale East | T5 | venom/silk input; rare `royal_silk` |
| `spider_egg_sac` | bug-drop (brood) | drop@vale_matron | Spider Vale West | T4 | venom/silk input |
| `trapdoor_lid` | bug-drop (rare) | drop@trapdoor_spider | Spider Vale East | T5 | décor/structure |

### Glow / light / luminous drops
| id | type | source | zone(s) | tier | used for |
|---|---|---|---|---|---|
| `glowworm_lumen` ✅ | bug-drop (BEST light) | drop@glowworm | Centipede Cavern | T3 | the best natural light material — lantern/lamp/amulet/set inlay |
| `firefly_lumen` | bug-drop (glow-gland) | drop@firefly | Butterfly Fields | T2 | the whole light-gear line (lanterns, glow-armor, night_vision) |
| `firefly_dust` | bug-drop (glow powder) | drop@firefly | Butterfly Fields | T2 | glow paint/dye; soft décor light |
| `luna_dust` | bug-drop (wing powder) | drop@luna_moth | Butterfly Fields | T2 | glow-dye; night-vision tonic |
| `glow_gland` | bug-drop (light organ) | drop@glow_mayfly | Underground River | T3 | `light_radius` reagent; lanterns; glow-charm/alchemy |
| `glow_sac` | bug-drop (cold-light gel) | drop@glow_grub | Underground Passages | T3 | the `glow_lantern` fuel; décor |
| `mayfly_wing` | bug-drop (glowing membrane) | drop@glow_mayfly | Underground River | T3 | luminous trinket; fast-attack reagent; glow-dye |
| `serpentfly_scale` | bug-drop (luminous scale) | drop@bog_serpent_fly | Deep Swamp | T4 | elite alchemy/charm; best dye/décor |
| `serpentfly_ichor` | bug-drop (glowing ichor) | drop@bog_serpent_fly | Deep Swamp | T4 | deep-cure; rare elixir; trophy reagent |

### Scale / wing / specimen drops (butterfly/moth/dragonfly/cicada/fish)
| id | type | source | zone(s) | tier | used for |
|---|---|---|---|---|---|
| `butterfly_scale` | bug-drop (iridescent dust) | drop@butterfly | Butterfly Fields | T2 | shimmer dye; scale-glaze; rare-luck charm |
| `monarch_scale` | bug-drop (amber scale) | drop@monarch | Butterfly Fields | T2 | best shimmer dye; jeweled charm; specimen value |
| `glass_scale` | bug-drop (prism scale) | drop@glasswing | Butterfly Fields | T2 | clarity/`gem_luck` charm; prism lens; glasswork |
| `eyespot_scale` | bug-drop (false-eye) | drop@emperor_moth | Butterfly Fields | T3 | intimidation/`dodge` trinket; décor |
| `cicada_shell` | bug-drop (exoskeleton) | drop@cicada | Butterfly Fields | T2 | springy armor plating (dodge/fall_resist); chime |
| `cicada_wing` | bug-drop (lacy wing) | drop@cicada | Butterfly Fields | T2 | translucent décor inlay; glide trinket |
| `dragonfly_wing` | bug-drop (quad-wing) | drop@dragonfly | Deep Swamp | T3 | glider/wing-cloak; attack_speed reagent; gossamer cloth |
| `dragonfly_eye` | bug-drop (compound eye) | drop@dragonfly | Deep Swamp | T3 | night_vision + catch_radius trinkets |
| `nymph_gill` | bug-drop (gill) | drop@dragonfly_nymph | Deep Swamp | T3 | (nymph carapace secondary) |
| `strider_leg` | bug-drop (hydrofuge leg) | drop@water_strider | Deep Swamp | T3 | deep `water_walk` reagent; strider boots/glides |
| `strider_oil` | bug-drop (hydrophobic wax) | drop@water_strider | Deep Swamp | T3 | deep waterproofing; diver seal |
| `skater_oil` | bug-drop (hydrophobic wax) | drop@pond_skater | Shallow Swamp | T2 | water-walk boots reagent; waterproofing |
| `damselfly_wing` | bug-drop (membrane) | drop@damselfly | Shallow Swamp | T2 | gossamer cloth; lily-glide trinket; dye |
| `beetle_air_sac` | bug-drop (bubble-gill) | drop@water_beetle | Underground River | T3 | `water_breath` reagent (natural bubble-gill) |
| `blind_fish_scale` | bug-drop (iridescent scale) | drop@blind_cave_fish | Underground River | T3 | luck/clarity reagent; pearlescent dye/inlay |
| `fish_fillet` | bug-drop (fish meat) | drop@blind_cave_fish | Underground River | T3 | cooking protein (cave-fish dishes) |
| `aquatic_grub` | bug-drop (larva body) | drop@aquatic_larva | Underground River | T3 | prime fishing bait |
| `larva_case` | bug-drop (pebble casing) | drop@aquatic_larva | Underground River | T3 | natural grit/abrasive (pearl-polishing) |
| `cave_detritus` | bug-drop (pale rot) | drop@albino_isopod | Underground River | T3 | compost/bait substrate; cave-fungus mulch |

### Bee/pollinator drops
| id | type | source | zone(s) | tier | used for |
|---|---|---|---|---|---|
| `honeycomb` ✅ | bug-drop (comb) | harvest@bee_skep | Bee Meadow, Hilltop | T1 | → honey + beeswax via honey_extractor |
| `pollen` | bug-drop (pollen) | drop@bees / forage | Bee Meadow, Hilltop | T1 | bee bread; fertilizer; pollination; yellow dye |
| `propolis` | bug-drop (bee glue) | scrape@bee_skep | Bee Meadow | T1 | salve; wood polish; hazard-resist balm |
| `royal_jelly` ✅ | bug-drop (jelly, premium) | drop@sweat_bee / war_queen | Bee Meadow, Deadly Ants | T2 / T5 | premium max_hp/hp_regen tonic; endgame luck/regen |
| `bumble_nectar` | bug-drop (thick nectar) | drop@bumblebee | Hilltop Meadow | T2 | premium mead/honey/cooking; royal_jelly-adjacent tonic |
| `carpenter_resin` | bug-drop (wood-oil) | drop@carpenter_bee | Hilltop Meadow | T2 | waterproofing; wax-wood polish; frame binder |
| `nectar` ✅ | bug-drop (nectar) | gather@butterfly | Butterfly Fields | T2 | cooking sweetener; silk-soak |
| `cabbage_caterpillar` | bug-drop (pest larva) | drop@cabbage_white | Hilltop Meadow | T2 | pest-lure bait (the wasp-patrol target) |
| `silk_thread` | bug-drop (wild silk) | drop@cabbage_white chrysalis | Hilltop Meadow | T2 | light wild silk; pollinator-outfit weave; nets; bandages |

---

## processed (crafted intermediates & alchemy bases)

Refined / processed materials that aren't a bar/plank/cloth/gem/silk but are crafting inputs (etch agents,
alchemy essences, dyes, building bricks, fuels, fertilizers, glass, binders). Finished consumables live in the
consumables catalog; these are the **intermediate** rung.

### Stone / building bricks & blocks
| id | type | source | zone(s) | tier | used for |
|---|---|---|---|---|---|
| `clay` ✅ | processed (raw) | mine/forage | Wasp Thicket, Village + everywhere | T1 | bricks/pottery; bombs; mortar |
| `pond_clay` | processed (fine clay) | mine/forage | Village | T1 | finer bricks/pottery (`pond_brick`) |
| `marsh_clay` | processed (wet clay) | dig | Shallow Swamp | T2 | waterproof pottery/jars; `marsh_brick` |
| `sand` ✅ | processed (raw) | forage/mine | (glass base) | T1 | → `glass`; furnace |
| `desert_sand` | processed (rich sand) | forage/mine | Scorpion Rocks | T1 | → `glass`; polishing grit; sandstone mortar |
| `brick` ✅ | processed (fired) | craft@furnace | (structures) | T2 | the canonical wall/path brick |
| `glass` ✅ | processed (fired) | craft@furnace (`sand`) | (lanterns, jars) everywhere | T2 | lanterns, jars, lenses, windows |
| `sandstone` | processed (building stone) | mine | Scorpion Rocks | T3 | desert blocks/paths/walls; heat-shelter; flux |
| `chalk_stone` | processed (limestone) | mine | Ant Colony | T1 | underground building stone; lime cure; grit |
| `dripstone` | processed (cave limestone) | mine | Centipede Cavern | T3 | cavern blocks/columns; lime/flux |
| `flowstone` | processed (calcite/travertine) | mine | Underground River | T3 | premium banded building stone (`flowstone_block`) |
| `soft_stone` | processed (crumbly wall) | mine | Underground Passages | T3 | cave brick/path; cart rubble; cheap filler |
| `magma_rock` | processed (heat-fused stone) | mine | Deadly Ants | T5 | fire-forge building stone; forge flux; heat décor |
| `scorched_clay` | processed (fire-hardened) | mine | Locust Farmland | T4 | stronger brick/kiln; crop-defense rampart |
| `black_silt` | processed (mineral mud) | dredge | Deep Swamp | T3 | → `silt_brick`; deep-water mortar; glaze |
| `river_silt` | processed (pale silt) | dredge | Underground River | T3 | → `silt_block`; pottery body; crop amendment |
| `silt_brick` | processed (brick) | craft@furnace (`black_silt`+`peat`) | Deep Swamp | T3 | dense waterproof brick |
| `silt_block` | processed (brick) | craft@furnace (`river_silt`+`coal`) | Underground River | T3 | pale waterproof brick; fisher-platform construction |
| `peat` | processed (fuel/amendment) | cut@bog | Shallow/Deep Swamp | T1 | fuel (coal-lite); soil amendment; `peat_block` |
| `peat_block` | processed (earthen block) | craft@stonecutter (`peat`×3) | Shallow Swamp | T2 | cheap structure + fuel store |
| `river_pebble` | processed (pebble) | forage | Village | T1 | stonecutter paths; polished décor; soap grit |
| `river_reed` | processed (reed) | forage | Village | T1 | baskets/mats; forager kit; thatch décor |

### Alchemy essences, etch agents, oils, binders, fertilizers, fuels
| id | type | source | zone(s) | tier | used for |
|---|---|---|---|---|---|
| `resin_glob` ✅ | processed (sticky binder) | tap@brush-trees | Wasp Thicket + venom zones | T2 | venom-coating adhesive; glue; waterproofing |
| `tree_resin` | processed (amber sap) | forage | Millipede Forest | T2 | binder/sealant (resin_glob family); glue/varnish |
| `lure_resin` | processed (mineral seep) | tap/refine | Underground River | T3 | fishing-lure binder; waterproof coat for diver gear |
| `tannin` | processed (tanning agent) | leach@cauldron (peat+bark) | Shallow Swamp | T2 | tans hide/reed → leather; brown dye |
| `formic_etch` | processed (etch/cleaner) | craft@cauldron (`formic_acid`+`chalk_stone`) | Ant Colony | T2 | gem-cut/fine-brick etch; strong cleaner |
| `ember_resin` | processed (fire-binder) | forage/mine | Deadly Ants | T5 | burn-coating base; fire-temper flux; fire décor |
| `lotus_essence` | processed (anti-disease core) | craft@cauldron (`swamp_lotus`+`lily_extract`) | Deep Swamp | T3–T4 | anti-disease/poison alchemy core; strong calm base |
| `lily_extract` | processed (calm/clarity base) | craft@cauldron (`lily_pad`+bloom) | Shallow Swamp | T2 | calm/anti-leech salve base; soothing dye |
| `lily_pad` | processed (buoyant pad) | harvest@water_lily | Shallow Swamp | T2 | water-walk stepping reagent; → `lily_extract` |
| `duckweed_paste` | processed (green) | craft@cauldron (`duckweed`) | Shallow Swamp | T2 | green dye; crop fertilizer additive |
| `miasma_essence` | processed (disease vapor) | condense@fever-fog | Deep Swamp | T3 | fever-bombs; antitoxin base; miasma-lamp |
| `swamp_gas` | processed (volatile) | capture@gas-pockets | Shallow Swamp | T1 | lantern fuel; light_radius consumable; gas bomb |
| `cave_water` | processed (mineral-pure) | draw@river | Underground River | T3 | cold/clarity brew base; solvent; cold hazard_resist |
| `freshwater_nacre` | processed (mother-of-pearl) | grind@cauldron/jeweler | Underground River | T3 | iridescent inlay; pearlescent glaze/dye; polish |
| `locust_oil` | processed (high-energy oil) | press/render@cauldron | Locust Farmland | T4 | weapon-coat (vs swarms); food fat; lamp/forge fuel |
| `swarm_essence` | processed (pheromone residue) | drop/render@cauldron | Locust Farmland | T4 | AoE-weapon charge; swarm-LURE core; fertilizer/poison |
| `silk_resin` | processed (burrow secretion) | drop/forage | Locust Farmland | T4 | composite binder; structure swarm-proofing sealant |
| `saltpeter` | processed (niter) | mine | Underground Passages | T1 | black-powder/`blast_charge`; preservative; flux |
| `rock_salt` | processed (evaporite) | mine | Scorpion Rocks | T1 | preservation/jerky cure; etch/desiccant; anti-tick base |
| `cave_nitre` | processed (saltpetre crust) | mine | Centipede Cavern | T1 | preservation/jerky; gem-cut etch; hazard_resist base |
| `cave_salt` | processed (evaporite) | scrape@ledges | Underground River | T3 | preservative (fish cure); tanning/alchemy; hazard_resist |
| `bat_guano` | processed (fertilizer) | forage | Centipede Cavern | T1 | premium compost; mushroom substrate; nitre note |
| `compost_rich` | processed (fertilizer base) | forage@compost | Village | T1 | premium fertilizer; fly-bait substrate |
| `honeydew` ✅ | processed (sweet secretion) | drop@aphid | Village, Ant Colony, Hilltop | T1 | cooking sweetener; ant/pest bait; tonic input |
| `beeswax` ✅ | processed (wax) | craft@honey_extractor | Bee Meadow, Hilltop | T1 | candles, wax polish, wraps, frames |
| `beeswax_dab` | processed (wild wax) | drop/forage@wild combs | Village | T1 | candle-making; furniture polish; sealing preserves |
| `royal_wax` | processed (premium wax) | craft@honey_extractor (premium split) | Hilltop Meadow | T3 | honeycomb-plate armor; sealed frames; premium candles |
| `honey` ✅ | processed (sweetener) | craft@honey_extractor | Bee Meadow, Hilltop | T1 | sweetener; mead base; healing salve |
| `clover_honey` | processed (single-flower honey) | craft@honey_extractor | Hilltop Meadow | T2 | artisan-sell honey; quality cooking input |
| `bee_bread` | processed (food/feed) | craft@cooking_pot (`pollen`+`honey`) | Bee Meadow | T1 | fed to hive (+honey yield); stamina food |
| `pollen_loaf` | processed (Apiary feed) | craft@cooking_pot (`pollen`+`bumble_nectar`) | Hilltop Meadow | T2 | Apiary yield boost; food buff |
| `comb_foundation` | processed (wax sheet) | craft@workbench (`beeswax`+`plank`) | Hilltop Meadow | T2 | seeds a `bee_frame` (the beekeeping "ammo") |
| `mud_daub` | processed (nest binder) | drop@mason_bee | Bee Meadow | T1 | builds/repairs `bee_hotel`; minor `clay`-like binder |
| `deepwater_kelp` | processed (loom fiber/iodine) | dive/harvest | Deep Swamp | T3 | wet-suit weave (`kelp_weave`); water_retention lining; anti-fever |
| `gossamer_dew` | processed (silk-soak) | forage@webs | Spider Vale West | T2 | lightens/strengthens cloth; dodge-tonic clarity; shimmer dye |
| `glow_spore` | processed (fungal light) | harvest | Underground River | T3 | `light_radius` reagent; luminous dye/additive |
| `bone` ✅ | processed (skeletal) | drop/forage | (canonical) | T2 | tools, décor, alchemy/fertilizer (bone-meal) |

### Crafted dyes (palettes)
| id | type | source | zone(s) | tier | used for |
|---|---|---|---|---|---|
| `red_dye` | processed (dye) | craft@dye_vat (`ladybug_shell`+`poppy`) | Village | T1 | recolor gear/décor |
| `yellow_dye` | processed (dye) | craft@dye_vat (`dandelion`) | Village | T1 | recolor |
| `blue_dye` | processed (dye) | craft@dye_vat (`flower_blue`) | Village | T1 | recolor |
| `green_dye` | processed (dye) | craft@dye_vat (`clover`+`fennel`) | Village | T1 | recolor |
| `pollen_dye` | processed (dye) | craft@dye_vat (`pollen`) | Bee Meadow | T1 | yellow/gold dye bath |
| `gold_dye` | processed (dye) | craft@dye_vat (`pollen`+`bumble_nectar`) | Hilltop Meadow | T2 | rich gold/amber "honey gold" |
| `shimmer_dye` | processed (dye) | craft@dye_vat (`butterfly_scale`) | Butterfly Fields | T2 | iridescent shift-color (signature finish) |
| `amber_dye` | processed (dye) | craft@dye_vat (`monarch_scale`+`dandelion`) | Butterfly Fields | T2 | deep amber-orange |
| `glow_dye` | processed (dye) | craft@dye_vat (`firefly_dust`+`glow_bloom`) | Butterfly Fields | T2 | softly luminous paint |
| `swamp_dye` | processed (dye set) | craft@dye_vat | Shallow Swamp | T2 | brown/green/azure wetland palette |
| `deep_swamp_dye` | processed (dye set) | craft@dye_vat | Deep Swamp | T3 | ink-black/lotus-violet/serpent-glow palette |
| `cavern_dye` | processed (dye set) | craft@dye_vat | Centipede Cavern | T3 | glow-cyan/moss-green/nitre-pale palette |
| `forest_dye` | processed (dye set) | craft@dye_vat | Millipede Forest | T4 | bark-brown/moss-green/amber palette |
| `cave_river_dye` | processed (dye set) | craft@dye_vat | Underground River | T3 | pearl-white/glow-blue/flowstone-amber palette |

### Specialty foraged building/light materials
| id | type | source | zone(s) | tier | used for |
|---|---|---|---|---|---|
| `glow_bloom` | flora-processed (night flower) | forage | Butterfly Fields | T2 | glow-dye base; night-vision tonic; moth lure |
| `luminous_resin` | processed (light-holding sap) | forage | Butterfly Fields | T2 | glow-armor sealant; self-lighting varnish |
| `butterfly_press` | processed (mounted specimen) | craft@workbench | Butterfly Fields | T2 | mounted-specimen tile for cabinet/cabin décor |
| `luminescent_thread` | processed (glowing thread) | craft@loom (`silk`+`firefly_lumen`) | Butterfly Fields | T2 | glow-cloth; light-trim; firefly-lantern wick |

---

## Material ladders

The chains where a raw material is processed up through intermediates to a finished tier. (Read left→right =
cheaper→stronger. ✅ = existing canonical.)

### Ore → bar (the metal spine)
- `copper_ore` ✅ → `copper_bar` ✅ → (+tin, implied) `bronze_bar` ✅ → **T2**
- `iron_ore` ✅ / `bog_iron` ✅ / `cold_iron_ore` → `iron_bar` ✅ → **T3**
- `iron_bar` ✅ → `steel_bar` ✅ → **T4**
- `silver_ore` ✅ → `silver_bar` ✅ → **T4→T5**
- `gold_ore` ✅ → `gold_bar` ✅ → **T5**
- `platinum_ore` ✅ → `platinum_bar` ✅ → **T5**
- *Fire side-temper:* `steel_bar` ✅ + `ember_resin` + `fire_ant_gland` → `flame_alloy` → **T5**

### Wood → plank
- `wood` ✅ → `plank` ✅ → **T1**
- `hardwood` → `hardwood_plank` → **T4**
- `sunken_log` → `bogwood_plank` → **T3**
- `reed_stalk` → `thatch` → **T1–T2**

### Fiber → thread → cloth
- `fiber` ✅ → `thread` ✅ → `cloth` ✅ → **T1–T2**
- `reed_stalk` → `reed_fiber` / `pale_root` → `pale_line` (coarse-weave branch) → **T2–T3**
- `deepwater_kelp` → `kelp_weave` (sealing-cloth branch) → **T3**
- `crop_beetle_shell` + `locust_wing` + `thread` → `chitin_weave` (armor-textile branch) → **T4**

### Sand → glass
- `sand` ✅ / `desert_sand` → `glass` ✅ → **T2** (lanterns, jars, lenses, windows)

### Silk ladder (raw thread → premium cloth)
- **Common:** `spider_silk` ✅ / `moth_silk` / `hawkmoth_silk` / `cave_spider_silk` ✅ → `spun_silk` ✅ → `silk` ✅ / `silk_cloth` ✅ → **T2–T3**
- **Premium (West):** `orb_silk` ✅ + `silk_gland` (catalyst) → `refined_silk` → `spider_silk_cloth` → `gossamer_cloth` (+`gossamer_dew`) → **T4→T5**
- **Endgame (East):** `royal_silk` + `spun_silk` ✅ → `royal_silk_cloth` → **T5** (Widow's-set keystone)
- **Glow branch:** `glow_silk` → `glow_thread` → **T3**
- *Three-tier West rung:* `spider_silk` ✅ → `orb_silk` ✅ → `broodmother_silk` ✅ (boss-gated top thread)

### Venom ladder (cheap → apex), by line
- **Wasp:** `venom_sac` ✅ → `royal_venom` (boss) → **T2**
- **Hornet:** `hornet_venom` → **T3** (above `venom_sac`)
- **Scorpion:** `scorpion_venom` → `potent_venom` ✅ (boss) → **T3→T4**
- **Spider (West):** `spider_venom` → (paralytic branch: `centipede_venom`) → **T4**
- **Spider (East):** `widow_venom` → `potent_venom` ✅ (reused, boss seed) → **T5**
- **Centipede (cavern):** `centipede_venom_gland` → `potent_centipede_venom` (boss) → **T3→T4**
- **Ant (endgame):** `venom` ✅ / `potent_venom` ✅ → `queen_venom` (war_queen) → **T5** (hottest)
- **Swamp:** `mosquito_proboscis` ✅ / `mosquito_venom` → `waterbug_venom_gland` (apex) → **T3→T4**
- **Cave (light):** `spider_venom` (light variant, Underground Passages) → **T3**

### Chitin ladder (plate → refined → endgame)
- **Light intro:** `pill_chitin` (Village) → `chitin` ✅ → **T1→T2+**
- **Ant:** `chitin` ✅ → `soldier_chitin` ✅ → `queen_chitin` → **T2→T3**
- **Forest carapace:** `beetle_carapace` → `prime_carapace` (apex) → **T4**
- **Cavern/cave plates:** `cave_beetle_carapace` ✅ / `blind_beetle_shell` ✅ / `crayfish_shell` / `water_beetle_shell` → **T3**
- **Aquatic apex:** `giant_waterbug_carapace` / `cave_crab_carapace` → **T4**
- **Endgame ant:** `chitin` ✅ ×3 + `soldier_ant_plate` → `elite_chitin` → (with `war_queen_chitin` keystone) → **T5**
- **Locust:** `crop_beetle_shell` → `reaper_chitin` (apex capstone) → **T4→T5**

### Formic / acid ladder
- `formic_dab` ✅ (common worker) → `formic_acid` ✅ (concentrated, soldier) → `formic_etch` (industrial intermediate) → **T1→T2**
- *Acetic side:* `vinegaroon_acid` (gem-cut etch) → **T3**
- *Corrosive endgame:* `acid_crystal` (etch/temper/shred) → **T5**
- *Fire side:* `fire_ant_gland` → `flame_alloy` / `ember_resin` (fire-temper/coating) → **T5**

---

## Total distinct-material count

Counting distinct material/intermediate ids in this catalog (excludes finished gear/weapons/consumables/food/
décor/structures; the `dead_*` carcass family is counted as **one** row):

| type | distinct ids |
|---|---|
| ore | 19 |
| metal-bar | 8 |
| wood | 9 |
| fiber | 13 |
| cloth | 13 |
| flora | 27 |
| mushroom | 9 |
| fruit | 5 |
| crop | 8 |
| gem (cut/processed) | 11 |
| bug-drop (incl. silk/glow/scale/bee + `dead_*` as 1) | 122 |
| processed (bricks/blocks, alchemy/oils/binders/fertilizer/fuel, dyes, specialty) | 71 |
| **Total distinct materials** | **≈ 315** |

> *(Approximate: a handful of ids are deliberately dual-listed across a raw/cut split — e.g. `glow_quartz`
> ore vs `cut_glowquartz` gem, `cave_nitre` mineral vs gem-class — and a few aliases are folded per the
> "Aliases to fold" notes. The implied-but-unnamed `gold_ore`/`platinum_ore` are included for ladder
> completeness. Treat ~315 as the design-stage upper bound before the user's prune pass.)*

### Consolidated aliases to fold (prune candidates)
- `moth_silk_cloth` → **`silk_cloth`** ✅ (same canonical bolt).
- `pale_line` → **`reed_fiber`** (cave-native coarse cordage variant).
- `tanned_leather` → **`tanned_hide`** ✅ (forest bark-tannin vs swamp reed-tannin; one leather id).
- `glowshroom` → **`mushroom_glow`** ✅ (brighter cultivated cave-cap variant).
- `glow_grub`/`glow_sac`/`glow_gland`/`glow_spore`/`springtail_dust`/`firefly_dust`/`luna_dust` — overlapping
  **luminescent-reagent** family; keep the species-signature ones, fold the redundant cheap glow-dusts on prune.
- `cave_quartz`/`quartz` ✅ and `glow_quartz`/`glow_crystal` — keep as deliberate tier ladders or collapse.
- `cut_glowquartz` (T2) ↔ `cut_glow_crystal` (T3) — same luminous-cut concept, two tiers.
- `bog_pearl` (dark) vs `cave_pearl` (pale) — distinct by water (swamp vs cave); keep both or fold to `pearl`.

## Glass building block (D26 — Modern Wares)
- `glass_block` ✅ — a translucent cool-blue **glass building block** (modern windows/walls); mineable like
  `stone_block`. The modern shop's signature material. (Polished `modern_floor` TILE is still 🔵 backlogged.)
