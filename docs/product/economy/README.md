# Economy / Crafting / Content — design folder

The design for BugFarmer's **crafting, stations, merchants, items, gear bonuses, per-zone content, and the
world-gated progression** that paces them — a content-DENSE, "much better than bare minimum" layer that stays
inside the GDD guardrails (item-driven power, no stat grind, capped accessory bonuses, capped décor boosts).

**Balance here means PACING — *where and when* things become available — not stripping content down.**
Content is intentionally **over-produced so you PRUNE down**, never beg for more.

> Status: **design only** — nothing here is wired into the game yet.

## The map

**Start here / cross-cutting**
| File | What it is |
|---|---|
| **[`DECISIONS.md`](DECISIONS.md)** | Every design decision — resolved (D1–D9) + the synthesis/prune notes. Check before assuming anything. |
| [`progression.md`](progression.md) | The **pacing & gating curve** + lens rationale + the starting-village scope. |
| [`crafting.md`](crafting.md) | The crafting **system**: cost model, station roster, recipe schema, bug-derived/artisan/sprinkler mechanics. (Item *enumeration* lives in `catalogs/`.) |
| [`merchants.md`](merchants.md) | The 3 shops (General Store / Blacksmith / Carpenter) + currency + the craft-vs-buy matrix. |
| [`stats_and_bonuses.md`](stats_and_bonuses.md) | The bonus/purpose system: `bonuses{}` schema, the stat vocabulary, sources, caps. |
| [`production.md`](production.md) | How we build it all: art queue, authoring templates, build waves W1–W5. |
| [`findings.md`](findings.md) | As-built audit (what's actually in code today). Reference. |

**Content (the dense part)**
| Folder/file | What it is |
|---|---|
| [`zones/`](zones/) | **One content sheet per zone (×17)** — species, drops, ingredients, recipes, signature gear, shop, hook. *Every zone adds new toys.* |
| [`species_and_drops.md`](species_and_drops.md) | The full bug roster (84 species) by zone + the drop→ingredient map. |
| [`catalogs/materials.md`](catalogs/materials.md) | Every material/ingredient (~315) by type/source/zone/tier. |
| [`catalogs/armor.md`](catalogs/armor.md) | 11 base metal sets + 17 zone bonus sets (28 sets). |
| [`catalogs/weapons.md`](catalogs/weapons.md) | 48 base tiered + 34 special = 82 weapons. |
| [`catalogs/accessories.md`](catalogs/accessories.md) | 88 accessories covering the full stat vocab (+ trade-offs). |
| [`catalogs/tools.md`](catalogs/tools.md) | 54 base tier tools + 48 special = ~102. |
| [`catalogs/consumables.md`](catalogs/consumables.md) | 78 potions + 47 meals. |

**Reading order:** `DECISIONS` → `progression` → a few `zones/` sheets → `catalogs/*` → `crafting`/`merchants`
→ `production`.

## Content coverage (quotas — all met or exceeded; these are pre-prune maxima)
| Category | Target | Delivered |
|---|---|---|
| Zones with full content sheets | 13+ | **17** |
| Species (w/ drops) | ≥45 | **84** (6 exist in code) |
| New materials/ingredients | ≥50 | **~315 total** (incl. existing) |
| Armor base sets | 11 | **11** (+ **17** zone bonus sets) |
| Bonus armor sets, spread early→late | ≥18 | **17** (one per zone) |
| Weapons | ≥28 | **82** |
| Accessories | ≥35 | **88** |
| Potions / Meals | ≥25 / ≥25 | **78 / 47** |
| Tools | families + ≥8 | **~102** |
| Per zone: ingredients/recipes/signature gear/shop | ≥3 / ≥4 / ≥1 / ≥1 | met in all 17 |

## Where geography lives (do NOT duplicate here)
The world map, zones, mining depth, and the **resource/material dispersion** are canonical in
**[`../architecture_world.md`](../architecture_world.md)** (§1, §1b). The economy docs link to it.

## Synthesis / prune notes (carried from the generation pass — see `DECISIONS.md`)
- **Spider Vale East** generated before West finished, so it used a parallel silk/venom lineage — reconcile
  the two silk ladders when pruning.
- **`paper_wasp`** is double-listed (Wasp Thicket threat + Meadow pest-control ally) but is the single
  existing `wasp` species.
- **Material aliases to fold** (materials.md flags them): `moth_silk_cloth`→`silk_cloth`, `glowshroom`→
  `mushroom_glow`, `tanned_leather`→`tanned_hide`, overlapping glow/venom reagents, the optional 4th/5th set
  "band" accessories.
- Counts above are the **design-stage upper bound** — the explicit intent is to prune toward a shippable set.

> `item_catalog.md` is **superseded** by `catalogs/` + `species_and_drops.md`. `suggestions.md` is the origin
> brainstorm (economy loop + NPC sketch), now reflected in `progression.md`/`merchants.md`.
