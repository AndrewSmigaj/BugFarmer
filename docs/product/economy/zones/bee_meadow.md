# Zone Content Sheet — Bee Meadow

**Grid:** (2,0) · **Biome:** flowery meadow · **Difficulty:** EASY · **Tier band:** T1–T2 (wood/stone → copper/bronze)

The gentle bee-farming intro. This is the game's **honey / pollination / flowers** zone — the player's first
encounter with hives, beeswax, pollen, and the Beekeeper NPC. Lean hard into *calm*, *gather*, *pollinate*,
*process* rather than combat: nothing here can seriously hurt an unarmored player, and the headline reward is
the **Beekeeper outfit** + the honey/beeswax artisan chain that feeds the rest of the economy.

Conventions: reuses canonical ids where they exist (`honey`, `honeycomb`, `beeswax` are already in
`crafting.md`'s cost model; `honey_extractor` station + `honey_yield_pct` / `sting_immunity` / `pollination`
stats already exist). New ids are introduced in `snake_case` and listed at the end. Cost = Σ input tier-points
(`crafting.md §1`).

---

## Species & drops

Four named bee species (plus a passive flower-pest the player can shoo for an early bug-drop). All bees are
**non-aggressive unless their hive is disturbed**; a calm player gathers freely, a flailing one gets stung for
chip damage. This is the zone that teaches `calm_radius` / `bee_calm` matter.

| Species | id | Behavior | Primary drop | Secondary drop | Notes |
|---|---|---|---|---|---|
| **Honeybee** | `honeybee` | Social; lives in the wild **bee_skep** hives dotted across the meadow. Forages in loops between flowers and hive. Defends hive if smoked-out without a calm tool. | `honeycomb` | `honey` (when hive harvested), `beeswax` | The staple. Hive = the renewable honey node; harvest with smoker or calm. |
| **Mason bee** | `mason_bee` | Solitary; nests in mud tubes (`bee_hotel` / reed banks). Docile, never stings. Best **pollinator** in the zone. | `pollen` | `mud_daub` (mason nest material) | Drawn to fruit blossom; boosts nearby crop `pollination`. The "good neighbor" bee. |
| **Leafcutter bee** | `leafcutter_bee` | Solitary; snips crescents from leaves to line nest cells. Mildly destructive to flora but harmless to player. | `leaf_disc` | `pollen` | Snipped leaves = a renewable `fiber`-ish craft input themed to the meadow. |
| **Sweat bee** | `sweat_bee` | Tiny, metallic-green, attracted to the player (sweat/salt). Skittish, fast, hard to net — the zone's **rare-catch** target. | `royal_jelly` (rare) | `pollen` | Low drop chance; `rare_bug_luck` / `catch_radius` gear pays off here. The "collector" bee. |
| **Pollen beetle** (pest) | `pollen_beetle` | Swarms open flowers, nibbles petals. Harmless; shoo/net for an easy starter drop. | `dead_beetle` (reuse) | `chitin` (reuse, low) | Gives the meadow a non-bee bug so net/bait crafting has a target here too. |

**Renewable nodes (not species):**
- **`bee_skep`** — wild domed straw hive; the harvestable honeybee colony node. Re-fills over in-game days.
  Harvesting it un-calmed aggros the colony briefly.
- **`flower_patch`** — dense bloom tiles (chamomile, lavender, yarrow, poppy, dandelion, clover — all existing
  flora) that the player can forage for **`nectar_bloom`** and that bees pollinate.

---

## New ingredients & materials

All bee/flower-themed gatherables, with id → source → use and a tier-point value (for recipe costing).

| id | pts | Source | Use |
|---|---|---|---|
| `honeycomb` | 4 | Harvest a `bee_skep`; honeybee drop | Feedstock for `honey_extractor` → splits into `honey` + `beeswax`. (Already referenced in `crafting.md`.) |
| `honey` | 6 | `honey_extractor` output | Sweetener for foods, base for **mead** (keg), healing salve. Already canonical. |
| `beeswax` | 4 | `honey_extractor` output | Candles, wax polish, wax-sealed preserves, wax wraps. Already canonical. |
| `pollen` | 1 | Mason/leafcutter/sweat bee drop; forage flower_patch | Bee bread, fertilizer booster, pollination consumable, dye base (yellow). |
| `propolis` | 4 | Scraped from `bee_skep` when harvested (low yield) | "Bee glue" — a natural sealant/resin: salve, wood polish, hazard-resist balm. The healing/utility ingredient. |
| `royal_jelly` | 10 | Rare sweat-bee / disturbed-skep drop | Premium consumable input (max_hp / hp_regen tonic); the zone's "luxury" mat. |
| `nectar_bloom` | 1 | Forage a `flower_patch` (themed flower bundle) | Cooking sweet/aromatic input; cauldron `calm_spray` base; keg floral mead. |
| `bee_bread` | 2 | Craft (pollen + honey, see recipes) | Fed to a hive to **boost honey yield**; also a stamina-style food buff input. |
| `leaf_disc` | 1 | Leafcutter bee drop | Meadow-flavored `fiber` substitute for soft crafts (wraps, woven mats). |
| `mud_daub` | 1 | Mason bee drop; reed banks | Builds/repairs the `bee_hotel`; minor `clay`-like binder. |

> Note: `dead_beetle`, `chitin`, `fiber`, `clay`, and all listed flora/flowers reuse existing ids — the pollen
> beetle and flower foraging slot straight into the existing food web and material ladder.

---

## Recipes debuting here

Honey/beeswax/pollination crafts. `process_ticks` follow `crafting.md §1` station classes. Tier gating per the
T1–T2 band of this zone. "Unlock" uses the `craft` / `buy@beekeeper` / `find` seam.

| Output | Station | Inputs (×count) | Unlock | Stat / effect | Tier |
|---|---|---|---|---|---|
| `honey` + `beeswax` (split) | honey_extractor | `honeycomb` ×2 | craft | Base artisan split — the honey engine | T1 |
| `bee_bread` | cooking_pot | `pollen` ×3 + `honey` ×1 | buy@beekeeper | Fed to hive: +honey yield over next days; as food: short `move_speed_pct` | T1 |
| `honey_cake` | cooking_pot | `honey` ×2 + `wheat` ×2 + `nectar_bloom` ×1 | craft | Timed food buff: small `max_hp` + `hp_regen` | T1 |
| `beeswax_candle` ×3 | cooking_pot | `beeswax` ×2 + `fiber` ×1 | craft | Décor light source; `light_radius` aura when placed | T1 |
| `wax_polish` | cauldron | `beeswax` ×2 + `propolis` ×1 | craft | Applied to wood furniture → comfort/value bonus (furniture tag) | T1 |
| `calm_spray` | cauldron | `nectar_bloom` ×2 + `lavender` ×1 | buy@beekeeper | Consumable: `calm_radius` pulse — bees/wasps stop attacking (✅ id exists) | T1 |
| `pollination_dust` | cauldron | `pollen` ×4 + `chamomile` ×1 | craft | Throwable: temporary `+pollination` over a crop area (faster bloom/yield) | T2 |
| `propolis_salve` | cauldron | `propolis` ×2 + `honey` ×1 + `yarrow` ×1 | craft | Heal-over-time consumable; the zone's first `hp_regen` item | T2 |
| `royal_tonic` | cauldron | `royal_jelly` ×1 + `honey` ×2 | find | Premium consumable: large `max_hp` + `hp_regen` buff | T2 |
| `floral_mead` | keg | `honey` ×3 + `nectar_bloom` ×2 | buy@beekeeper | Aged artisan good (sell at artisan multiplier); slight `luck` when drunk | T2 |
| `pollen_dye` | dye_vat | `pollen` ×4 | craft | Yellow/gold dye bath (recolor gear/décor) | T1 |
| `wax_wrap` ×2 | loom | `beeswax` ×1 + `leaf_disc` ×2 + `cloth` ×1 | craft | Preserves food/seeds (storage buff); soft-craft intro | T2 |
| `bee_smoker` | anvil | `copper_bar` ×2 + `cloth` ×1 + `propolis` ×1 | buy@beekeeper | **Tool**: harvest a `bee_skep` without aggro; passive `calm_radius` while held | T2 |
| `bee_hotel` | workbench | `wood` ×6 + `mud_daub` ×3 + `fiber` ×4 | craft | Placeable: attracts mason/leafcutter bees → local `pollination` aura | T1 |
| `honey_jar` | preserves_jar | `honey` ×2 + `glass` ×1 | craft | Shelf-stable honey, higher sell; gift item | T1 |

---

## Signature gear — the Beekeeper outfit (set)

The zone's headline reward: a 3-piece **utility outfit** (mutually exclusive with other outfits per
`stats_and_bonuses.md §"only one outfit active"`). Early tier (cloth + honeycomb/beeswax), built at the **loom**
with Beekeeper-bought recipes. Defense is intentionally low — outfits trade combat for activity mastery.

| Piece | id | Station | Inputs (×count) | Stats |
|---|---|---|---|---|
| Beekeeper hood (veil) | `beekeeper_hood` | loom | `cloth` ×3 + `beeswax` ×1 | `defense` +1, `sting_immunity` (partial: bees can't sting), `night_vision` minor |
| Beekeeper smock | `beekeeper_smock` | loom | `cloth` ×4 + `honeycomb` ×2 | `defense` +2, `honey_yield_pct` +15 |
| Beekeeper gloves | `beekeeper_gloves` | loom | `cloth` ×2 + `leaf_disc` ×3 + `beeswax` ×1 | `defense` +1, `pollination` +10, `harvest_yield` minor |

**Set bonus (all 3 worn): "Hive Keeper"** — full **`sting_immunity`** (bees *and* wasps can't damage you),
**`calm_radius`** aura (bees never aggro near you, harvest skeps freely), and `honey_yield_pct` +10 on top of
the smock. This is the canonical "bee suit" referenced in `stats_and_bonuses.md §155`.

**Companion accessory (jeweler-adjacent, drops/buys here):**
- **Bee Charm** (`bee_charm`, ✅ concept exists) — accessory, `honey_yield_pct`; buy@beekeeper or rare skep drop.
  Stacks with the outfit without occupying the outfit slot.
- **Pollinator's Ring** (`pollinator_ring`) — jeweler accessory, `copper_bar` ×2 + `pollen` ×4 + `quartz` ×1;
  `pollination` +10, tiny `crop_growth_pct`. T2 stretch craft.

---

## Shop / NPC — the Beekeeper

NPC occupant (`interaction_type:"npc"`, `npc{role:"beekeeper", ...}` per `merchants.md §5`). Lives at a small
apiary in the meadow. Sells bee supplies, hive parts, and the recipes that unlock the chain. Stock **grows with
progress** (early: basics; after first honey harvest: gear recipes). Buys honey/wax/pollen as an early coin
source.

**Sells (goods):**
| Item | Why |
|---|---|
| `bee_skep` (empty hive starter) | Place on the farm to start your own colony — the beekeeping mechanic seed |
| `bee_smoker` (finished, markup) | Convenience buy of the harvest tool |
| `calm_spray` | Consumable staple for safe harvesting |
| `flower_seeds` bundle (chamomile/lavender/clover) | Plant your own flower_patch for nectar + pollination |
| `bee_charm` (accessory) | The honey_yield accessory |

**Sells (recipes — unlock then craft):**
`bee_bread`, `floral_mead`, `bee_smoker`, `calm_spray`, and the three **Beekeeper outfit** pieces
(`beekeeper_hood` / `beekeeper_smock` / `beekeeper_gloves`).

**Buys (coin source):** `honey`, `honeycomb`, `beeswax`, `pollen`, `royal_jelly` (premium), `floral_mead`.

> Gating: outfit recipes appear only **after the player's first honeycomb harvest** (Lens of Pacing) — the NPC
> intro hands you a free `calm_spray` and points you at the nearest wild `bee_skep`.

---

## "New toys" hook

Bee Meadow is where the player first **places and harvests a hive** — buy an empty `bee_skep`, plant a
flower_patch beside it, and watch honeycomb accrue you can extract into honey + beeswax (your first artisan
chain and a steady coin source). It introduces the **calm loop**: a `bee_smoker` or `calm_spray` lets you
harvest without getting stung, teaching the `calm_radius` / `sting_immunity` stats that the **Beekeeper outfit**
later makes permanent. And it debuts **pollination as a farming lever** — mason bees and `pollination_dust`
visibly speed up nearby crops, turning "keep bees happy" into a real yield bonus that pays off across every
later farming zone.

---

## New-id index (for cross-doc reconciliation)

**materials / ingredients:** `pollen`, `propolis`, `royal_jelly`, `nectar_bloom`, `bee_bread`, `leaf_disc`, `mud_daub`
(reuse: `honeycomb`, `honey`, `beeswax`, plus `fiber`/`clay`/`chitin`/`dead_beetle`/flora ids)

**species:** `honeybee` → `honeycomb`; `mason_bee` → `pollen`/`mud_daub`; `leafcutter_bee` → `leaf_disc`/`pollen`;
`sweat_bee` → `royal_jelly`/`pollen`; `pollen_beetle` → `dead_beetle`/`chitin`

**nodes/placeables:** `bee_skep`, `flower_patch`, `bee_hotel`

**items / recipes:** `bee_bread`, `honey_cake`, `beeswax_candle`, `wax_polish`, `calm_spray`*, `pollination_dust`,
`propolis_salve`, `royal_tonic`, `floral_mead`, `pollen_dye`, `wax_wrap`, `bee_smoker`, `honey_jar`

**gear:** `beekeeper_hood`, `beekeeper_smock`, `beekeeper_gloves` (set: "Hive Keeper"), `bee_charm`*, `pollinator_ring`

\* `calm_spray` and `bee_charm` already exist as concepts — reused, not new.
