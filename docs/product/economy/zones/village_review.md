# Zone 1 — Starting Village (`village_21`) · REVIEW CHECKLIST (updated, zone-accurate)

Everything planned for Zone 1, reconciled to the **real `village_21_B` data** (the tuned 6-species ecology)
+ your review decisions (`../DECISIONS.md` D18–D20). Companion to [`village.md`](village.md).

Legend: ✅ exists in code · 🆕 new this pass · ❌ cut/removed · ⚠️ changed.

---

## Core model — Bug Extractor (🆕 D18)
Bugs drop **only `dead_<bug>`**. A clean in-town **Bug Extractor** building processes dead bugs → materials
(chitin/silk/leather…) and feeds **cooking**. ❌ Removed all per-bug ground drops + the bug-leather station.

## Species → drop (actual spawns — 6 species)
| Species | Drop |
|---|---|
| `fly` ✅ | `dead_fly` |
| `butterfly` ✅ (on `milkweed`) | `dead_butterfly` |
| `wasp` ✅ (+ `wasp_nest`) | `dead_wasp` |
| `centipede` ✅ | `dead_centipede` |
| **`millipede`** ✅ | `dead_millipede` |
| **`carrion beetle`** ✅ | `dead_beetle` |

❌ Removed: pill bugs, ants, snails, aphids (→ later/forested zones). So ❌ `honeydew`, `formic_*`, `ant_egg`-as-drop.

## Materials (from the real `village_21_B`)
- **Flora:** wood + **fruit** (oak/pine + apple/plum/cherry/orange), fiber (bush/tall_grass/reeds/fern/**clover**), **`milkweed`**, **berries** (`wild_berry_bush`), flowers (`flower_red`/`blue`/`yellow`/`wild`/**`aster`**), `poppy`, `lavender`, mushrooms (`mushroom_cluster`/`puffball`)
- **Mineable (basic surface):** copper/tin/coal + a little iron (per progression), `crystal`/`geode`, stone, clay, sand
- **Crops:** garden vegetables — tomato, corn, carrot, cabbage, eggplant, pumpkin. ❌ **wheat PULLED** (buy up north — fast-grow, good money, travel gate; *TODO: remove `plant_wheat` from `village_21_B`*). ❌ no cotton yet
- ❌ Removed: `wildflower_petals`, `river_pebble`, `pond_clay` (→ clay), `compost_rich` (→ one compost), `beeswax_dab` (→ west bee zone)
- ✅ reeds stay

## Stations
**Already in zone:** workbench · furnace · anvil · **sawmill** (woodcutting/saw) · cauldron · forge · keg
🆕 **Add:** Bug Extractor · compost bin (basic → bigger holds more)
⚠️ cauldron/forge/keg placed but advanced content (potions/steel/artisan) unlocks later

## Tools & gear
- 🆕 **start with a net** (also sold) · base tools wood→stone→copper · `watering_can` (small) · **`magnifying_glass`** (starter)
- `gardener_gloves`, `straw_hat` — craft + sold · fishing poles (Fisherman)

## Storage
🆕 small sack → large basket → backpack (storage slot)

## Armour
- Base only: **leather** (Bug Extractor) · padded/cloth (loom) · copper (anvil)
- ❌ Forager's Kit (→ later zone)

## Weapons
basic (auto recipes) `sword_wood→copper`, `spear_wood→copper` — also **sold + a few rare/expensive teases**

## Consumables
- ✅ `calm_spray` · ❌ rot_bait, sweet_bait, petal_tincture, bug_balm, village_soap
- ⚠️ health potions → wait for the alchemy pass (backlog)

## Food
- 🆕 offer **`forager_stew`** only · ⚠️ cooking recipes = separate system → backlog

## Décor & furniture
Everything in the zone (beds, sofas, dressers, tables, fountain, statue, lamps, aquarium, specimen_shelf,
bug_terrarium, rugs, clock, signs…). **Most buildable**; ⚠️ fancy/dyed pieces (`bed_fancy`, `sofa_fancy`,
`dresser_fancy`…) NOT buildable yet. **No roofs** (overhead) — walls/fences/gates/doors only.

## Dyes
`red`/`yellow`/`blue`/`green` from local flowers — sold by the right vendor.

## Farming
garden crops · fertilizer (compost) · 🆕 sprinklers **basic + advanced (cost-gated)**

## Fishing
🆕 basic fishing here (pond/docks/boats/poles) — the Fisherman sells poles + a boat

## NPCs (5)
1. **Merchant** — general goods/seeds/supplies/decor/recipes/net; **rotating stock + rare teases**
2. **Fisherman / boatperson** — poles + a **boat** (expensive)
3. **Blacksmith** — some metal (mining gear is at the Mining Camp)
4. **Carpenter** — furniture/wood/building recipes
5. **Mayor** — **land deeds** only (separate system → backlog)

---

## Still open for your call
1. ✅ **Centipedes + millipedes** — keep both (decided, as is).
1b. ✅ **Wheat** — pulled; buy it up north. *TODO: remove `plant_wheat` from `village_21_B` in zone authoring.*
2. **Cauldron/forge/keg** are physically placed in `village_21` — leave them (content gated later), or are they too advanced for the start town?
3. **`straw_hat`** — keep the sun hat (D11 only cut straw *armour*).
4. Anything in the décor/furniture set to mark **not-yet-buildable** beyond the obvious fancy ones?
