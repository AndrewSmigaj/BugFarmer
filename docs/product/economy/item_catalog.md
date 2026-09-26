# Item Catalog — the craftable/findable database (brainstorm)

> **⚠ SUPERSEDED (2026-06-25).** This early ladder-level brainstorm has been replaced by the full content
> design: per-category enumerations in [`catalogs/`](catalogs/) (armor, weapons, accessories, tools,
> consumables, materials), the bug roster in [`species_and_drops.md`](species_and_drops.md), and the per-zone
> sheets in [`zones/`](zones/). Kept for history; use those instead.

The menu of **what exists to make or find**, organized as progression ladders, with each item's **source**
(craft @ station / buy @ NPC / find @ location), rough **cost**, and **how it unlocks** (auto at the station
vs a recipe you buy or find). A working menu to prune + cost-tune, not a contract.

Conventions:
- **Source:** `craft@station` · `buy@npc` · `find@zone` · `drop@bug`.
- **Unlock:** `auto` (recipe always available at the station) · `buy@npc` (learn the recipe from a vendor)
  · `find` (recipe scroll dropped/looted) · `n/a` (not crafted — gathered/bought).
- Costs are **placeholder** integers (coins) / input lists — tune later. Stations from `../crafting_design.md`.
- ✅ = item already in `items.json` (see [`findings.md`](findings.md)); the rest are proposals.

The acquisition philosophy (GDD): **most early recipes auto-unlock at the station you built; mid/late
recipes and the fun outfits are bought from the right NPC or found while exploring** — so building, shopping,
and exploring all feed crafting.

---

## 1. Material ladders (the backbone)

### Metals — smelt ore → bar @ **furnace** (auto), then bar → gear @ **anvil/forge**
| Ore (find/mine) | → Bar (furnace, auto) | Tier it gates |
|---|---|---|
| copper_ore ✅ | copper_bar | T1–2 tools/armor |
| tin_ore | tin_bar | (alloys → bronze) |
| iron_ore ✅ | iron_bar ✅ | T3 workhorse |
| silver_ore ✅ | silver_bar | T4 / jewelry |
| gold_ore ✅ | gold_bar | jewelry / décor / high sell |
| platinum_ore ✅ | platinum_bar | T5 endgame |
| *alloy:* copper+tin | **bronze_bar** (forge) | between copper & iron |
| *alloy:* iron+charcoal | **steel_bar** (forge) | best non-exotic |
| *exotic (deep):* mithril/adamant ore | mithril/adamant_bar (forge) | endgame sets |

Smelt sub-inputs: most bars cost `2 ore + 1 coal` (~200 ticks). Charcoal (`wood`→furnace) substitutes for
coal. Glass = `sand`→furnace.

### Wood — **sawmill** (auto): `wood ✅ → wood_plank (+ sawdust)`. Planks gate better furniture/structures.
### Fiber/cloth — **loom** (auto): `fiber ✅ → thread → cloth`. Cloth gates soft armor + the utility outfits.
### Stone — **stonecutter** (auto, ✅): `stone_block → brick ✅ / wall ✅ / slab / path / statue`.
### Gems — mined from stone (`gem_luck`) or geodes ✅: quartz ✅, diamond ✅, emerald, ruby, sapphire,
amethyst, topaz → cut @ **jeweler** into **accessories** (buy the recipes).

## 2. Tools (the tier ladder — anvil, recipes auto)

The recolor pipeline already mints tier icons, so tools scale cleanly by metal. Each tier ≈
`2–3 bars + 1–2 wood @ anvil`, recipe `auto`.

| Family | Wood ✅ | Stone ✅ | Copper ✅ | Iron ✅ | Silver/Steel + | What the tier buys |
|---|---|---|---|---|---|---|
| Pickaxe | ✅ | ✅ | ✅ | ✅ | proposed | tool_tier (ore access) + mining_speed |
| Axe | ✅ | ✅ | ✅ | ✅ | proposed | chop speed + a melee secondary |
| Shovel | ✅ | ✅ | — | proposed | — | dirt/sand speed |
| Hoe | ✅ | ✅ | — | proposed | — | till speed/cooldown |
| Scythe | ✅ | proposed | — | proposed | — | harvest AoE |
| Watering can | basic ✅ | — | large ✅ | — | — | capacity + `water_aoe` |
| Net | small ✅ (T1) | — | — | large ✅ (T3) | proposed "gossamer net" T5 | catch_cap/arc + `rare_bug_luck` |
| **New:** Drill | — | — | — | iron | power-tier (§11.6) | fast mining, later electric |
| **New:** Fishing rod | wood | — | — | — | — | **gates fishing** (new system) — buy@fishing hut |
| **New:** Bug vacuum | — | — | — | mid | — | slow auto-catch handheld (capacity-capped) |

## 3. Weapons (combat) — anvil/forge; some bought, some found

Combat is item-driven (GDD §14). Keep a **small, characterful** set, not a Terraria-sized arsenal.

| Type | Examples (tiered) | Source / unlock | Notes |
|---|---|---|---|
| Sword | sword_wood ✅ → copper/iron/steel | craft@anvil, auto | wide arc, the all-rounder |
| Spear | spear_wood ✅ → iron | craft@anvil, auto | long reach, single-target |
| Hammer/Mace | stone/iron maul | craft@anvil, auto | high `knockback`, slow |
| Dagger | bronze/silver dirk | craft, auto | fast `attack_speed`, low dmg, `crit` |
| Bug-bane blade | chitin/venom-edged | **find/drop** from a boss bug | thematic, `damage` vs arthropods |
| Bug spray (ranged-ish) | calm_spray ✅, pesticide | craft@cauldron | utility/AoE calm, not pure dmg |
| Slingshot/bow (?) | wood + fiber | craft, buy@blacksmith | optional ranged — design risk, defer |

## 4. Armor sets (true armor — defense + a set bonus)

Each set = head/body/legs (+ optional arms/feet). Per-piece `defense`; full set = a `set` bonus (see
[`stats_and_bonuses.md`](stats_and_bonuses.md) §4). Craft @ anvil/forge from bars + cloth; recipes mostly
`auto`, the top tiers `buy@blacksmith` or `find`.

| Set | Material | Source / unlock | Set bonus theme |
|---|---|---|---|
| Leather ✅ | hide/cloth (loom) | craft@workbench/loom, auto | cheap starter; tiny `move_speed` |
| Copper | copper_bar | craft@anvil, auto | light defense |
| Bug-chitin | boss-bug drops + cloth | **find recipe** + drop | `thorns`, looks cool |
| Iron ✅ | iron_bar | craft@anvil, auto | the workhorse defense set |
| Silver/Steel | silver/steel_bar | craft@forge, **buy@blacksmith** | `damage_pct` + defense |
| Crystal/Gold (endgame) | gems + platinum | **buy@blacksmith** (pricey) | top defense + `hp_regen`/`dodge` |

## 5. Utility outfits (themed working sets) — the headline content

Cloth-based (loom), low defense, big activity bonus. **These are the items the request is most excited
about.** Recipes are **bought from the matching NPC** (or found), so each outfit ties to a vendor + an
activity. (Full bonus lists in [`stats_and_bonuses.md`](stats_and_bonuses.md) §4.)

| Outfit | Buy from | Rough cost | Made from |
|---|---|---|---|
| **Beekeeper suit** | Beekeeper NPC | mid | cloth + honeycomb |
| **Fisherman's vest** | Fishing-hut NPC | mid | cloth + cork/cord |
| **Miner's kit** (lamp helmet) | Blacksmith | mid | iron + glass + cloth (the lamp) |
| **Gardener's apron** | Carpenter/Builder or seed-merchant | low–mid | cloth + leather |
| **Entomologist's coat** | Ecologist | mid–high | cloth + rare-bug trophy |
| **Explorer's cloak** | Trader/merchant | mid | cloth + dye |
| **Forager's poncho** | Trader | low | cloth |
| **Combat plate** (true armor, listed in §4) | Blacksmith | high | steel + |

## 6. Accessories — jeweler + drops + quest rewards

2 slots, small bonuses ([`stats_and_bonuses.md`](stats_and_bonuses.md) §5). Cut gems @ **jeweler**
(buy recipes), or earn from rare drops / Ecologist quests.

| Accessory | Source / unlock | Bonus |
|---|---|---|
| Lucky Clover ✅ | find@meadow / quest | `luck` |
| Bee Charm ✅ | Beekeeper / hive drop | `honey_yield` |
| Swift Boots | craft@jeweler (leather+gem) | `move_speed` |
| Warding Band | jeweler (silver+gem) | `defense` |
| Magnet Stone | jeweler (iron+lodestone) | `pickup_radius` |
| Prospector's Loupe | Blacksmith / mine drop | `gem_luck` |
| Green Thumb Ring | seed-merchant | `crop_growth` |
| Glowstone Amulet | Miner / cave drop | `light_radius` |
| Merchant's Seal | Trader (expensive) | `sell_pct` |
| *(trade-off charms — §6 of stats doc)* | various | + / − |

## 7. Consumables — cauldron (potions) + kitchen (meals)

Timed buffs; strong but expire. Ingredients = the gatherable flora/produce ladder (the reason to explore).

| Item | Station | Effect (timed) |
|---|---|---|
| calm_spray ✅ | cauldron | bug `calm` (utility) |
| Health Tonic | cauldron | heal / `hp_regen` |
| Swiftness Brew | cauldron | `move_speed` |
| Night-Eye Drops | cauldron | `night_vision` (caves) |
| Miner's Draught | cauldron | `hazard_resist` + `light_radius` |
| Luck Potion | cauldron | `luck` (rare bug/ore window) |
| Cooked meals (bread, stew, pie…) | stove/cooking_pot | small **timed** stat buffs (NO hunger/stamina system — meals are buffs, per GDD §14) |
| Honey / honey wine | honey_extractor | `honey`→sell or buff base |

## 8. Recipe-acquisition map (auto vs buy vs find)

How the `unlock` seam ([`findings.md`](findings.md) §2) gets used — a concrete content rule:

- **`auto`** (always available once the station is built): the *backbone* — bars, planks, cloth, bricks,
  basic tool tiers (wood→iron), leather/copper/iron armor, torches, basic furniture. Building the furnace
  is the gate, not a recipe scroll. This keeps the early game frictionless.
- **`buy@npc`**: the **flavorful + power picks** — the utility outfits (from their themed NPC), top-tier
  armor/weapons (blacksmith), accessory cuts (jeweler), advanced food/potions, and convenience stations.
  This is the **coin sink** that makes selling matter.
- **`find`**: a few **rare recipe scrolls** as exploration payoffs — a unique weapon, a special outfit, an
  endgame accessory. Sparse, never required (no recipe is mandatory for progression).

This three-way split (build→auto, shop→buy, explore→find) is what turns crafting from a menu into a loop:
mine/farm/catch → sell → buy recipes + materials → craft better gear → reach deeper content → repeat.

---

## 9. Open questions for the catalog (decide before building)

1. **Currency**: one coin type, or barter? (Recommend one coin — simplest, matches `sell_price`.)
2. **Fishing**: in or out for v1? It unlocks the fisherman's vest + a whole gathering loop, but it's a new
   system. (Recommend: backlog as its own feature; design the vest/rod now so it's ready.)
3. **How many tiers** of armor/weapons is "much better than bare minimum" without becoming a treadmill?
   (Recommend 4–5 metal tiers + ~6 utility outfits + ~15 accessories — broad but curated.)
4. **Boss-bug drops** as a gear source (chitin set, bug-bane blade) — ties combat to the ecology bosses
   the GDD already wants (§14.2). (Recommend yes — it makes the fighting matter.)
