# Zone Content Sheet — Hilltop Meadow

**Grid:** (1,0) · **Biome:** hilltop wildflower meadow · **Difficulty:** MEDIUM · **Tier band:** T2–T3 (copper/bronze → iron)

The **advanced beekeeping + pest-control** zone — the deliberate step up from the gentle **Bee Meadow** (2,0).
Where Bee Meadow taught *calm → gather → process honey*, the Hilltop Meadow is where bees **fight back and
fight for you**: big aggressive **pollinators** (bumblebees, carpenter bees) that defend their patch, **wasps
you recruit as pest control**, and **hornets** as the zone's apex threat. The headline systems are the **Apiary
tower** (a multi-frame managed hive — the upgraded `bee_skep`), the **wax/venom processing** chain, and
**wasps-as-pest-control gameplay**: you keep a paper-wasp patrol that culls crop pests for you, at the price of
managing their aggro. Everything is gated **T2–T3** so it lands right after the player has copper/bronze
(Bee Meadow, Wasp Thicket) and is reaching for **iron** — the "I run an operation now" beat.

> Design contracts this obeys: cost model + stations from [`../crafting.md`](../crafting.md); stat vocab +
> `bonuses{}` schema (and the **one-outfit-at-a-time** rule, `stats_and_bonuses.md §3/§4`) from
> [`../stats_and_bonuses.md`](../stats_and_bonuses.md); pacing/gating from [`../progression.md`](../progression.md);
> shop/NPC seam (`interaction_type:"npc"` + `npc{role, intro, shop, tips[]}`, `buy@<role>` unlock) from
> [`../merchants.md`](../merchants.md).
>
> **Continuity with Bee Meadow:** reuses its canonical ids (`honey`, `honeycomb`, `beeswax`, `pollen`,
> `propolis`, `royal_jelly`, `nectar_bloom`, `bee_bread`, `bee_skep`, `flower_patch`, `bee_smoker`,
> `calm_spray`, the **Beekeeper outfit** + `bee_charm`/`pollinator_ring`) and **builds the next rung on top**
> — never re-introduces them. New ids are `snake_case` and listed in the trailing ledger. Generous by design:
> **we prune later, never thin.**

---

## Species & drops

Five species span the MEDIUM curve: two big managed **pollinators**, a **woodborer** that doubles as a wax/oil
source, a **recruitable pest-control wasp**, and a **hornet apex** at the top. All slot into the existing
ecology vocabulary (they lean on the **wasp** and a "big-bee" pollinator archetype) and reuse the **calm /
sting_immunity** loop from Bee Meadow — the difference is *scale and aggression*. Each gets a behavior gloss
and at least one **new drop id**.

| Species (id) | Tier feel | Behavior gloss | Where | Primary drop — new id | Secondary drop(s) |
|---|---|---|---|---|---|
| **bumblebee** (`bumblebee`) | core pollinator | Big, fuzzy, **loud** — the meadow's heavyweight pollinator. Forages flower_patches in lazy loops; **defends its tussock nest** with a buzzing bull-rush + a hard sting if you stomp the patch (chunkier than a honeybee, but no venom DoT). The best `pollination` source in the game so far. | tussock nests, flower fields | **`bumble_fuzz`** (the dense thoracic pile / "bee fur") | `pollen` ✅ (heavy), `bumble_nectar` (a thick wild nectar from its honey-pot cells) |
| **carpenter_bee** (`carpenter_bee`) | pollinator / borer | Glossy black; **bores perfect round tunnels** into the meadow's old fence posts, dead snags, and the Apiary's beams (light structural nuisance). Territorial males **dive-bomb** to scare you off (a bluff — males can't sting); females sting only if grabbed. Pollinates + yields a unique **wood-oil**. | dead snags, fence posts, beams | **`carpenter_resin`** (chewed wood + saliva sealant from the tunnels) | `wood` ✅ (borings/frass), `pollen` ✅ |
| **hornet** (`hornet`) | **apex threat** | The zone's danger spike. Large, fast, **hyper-aggressive paper-nest hornet**; a sentry patrols the nest and **recruits the whole nest** if alarmed (true swarm). **Venom sting applies `poisoned` + `knockback`**, and hornets actively **hunt the meadow's bees** (an ecology pressure — too many hornets crash your hives). Killing the nest is the zone's combat objective. | great paper hornet nest | **`hornet_venom`** (potent venom — a clean T3 venom tier above `venom_sac`) | `wasp_stinger` ✅, `dead_wasp` ✅, `hornet_carapace` (the big chitin plate) |
| **paper_wasp** (`paper_wasp`) ✅ | **pest-control ally** | *Reused from Wasp Thicket, recast here as a tool.* In the Meadow you **recruit** a paper-wasp patrol (place/seed a `wasp_lodge`): it **hunts crop pests** (aphids, beetles, caterpillars) in a radius for you — the **wasps-as-pest-control** mechanic. Still stings if you crowd the lodge un-calmed; managing that aggro IS the gameplay. | seeded `wasp_lodge` | `wasp_stinger` ✅ | `venom_sac` ✅ (uncommon), `chitin` ✅ |
| **cabbage_white** (`cabbage_white`) | pest / forage | *(the prey of the system above.)* Pretty white butterfly whose **caterpillars eat your crops** — the **pest** the wasp patrol is *for*. Adults flit the flowers (an easy calm-catch / pollinator); the larvae are the crop threat the player learns to manage. Harmless to the player. | crop rows, flower edges | **`cabbage_caterpillar`** (the larva — the pest target) | `pollen` ✅ (adult), `silk_thread` (from the chrysalis — a light wild silk) |

**Renewable nodes / placeables (not species):**
- **`apiary_tower`** — the upgraded, multi-frame managed hive (the **Bee Meadow** `bee_skep`'s T2–T3 successor):
  more honey/wax throughput, holds **`bee_frame`** inserts, and **upgradeable** (see recipes). The zone's
  signature build and the reason to come here.
- **`wasp_lodge`** — a placeable paper-wasp shelter you seed to start a **pest-control patrol**; refills its
  wasp population over in-game days, project a `calm_radius`-managed aggro field.
- **`flower_patch`** ✅ — reused; the bumblebee/carpenter-bee forage + the `bumble_nectar`/`pollen` source.

> **Sting / calm continuity:** every stinger here respects the **Bee Meadow** calm loop — `calm_spray`,
> `bee_smoker`, and `sting_immunity` gear all work, but the Meadow's stings *hurt more* (chunk damage; hornet
> venom is a real DoT), so the player is pushed to *upgrade* their anti-sting answers, not just reuse them.

---

## New ingredients & materials

Wax-, venom-, and pollinator-themed. `source`: `drop` (bug) / `forage` (pick) / `craft` (station output).
Tier-point value (`pts`, per `crafting.md §1`) given for recipe costing. New ids in **bold**.

| id | pts | Source | Where found | Use |
|---|---|---|---|---|
| **`bumble_fuzz`** | 4 | drop — bumblebee | tussock nests | Soft insulating pile: the **lining of the warm "pollinator" outfit**, a felt-like cloth substitute, a brush for hand-pollination tools. (chitin-tier ≈ 4) |
| **`bumble_nectar`** | 6 | drop/forage — bumblebee honey-pots, rich flower_patch | tussock nests, prime blooms | A **thick wild nectar**, richer than `nectar_bloom`: premium mead/honey input, a high-tier cooking sweetener, the `royal_jelly`-adjacent tonic base. (honey-tier ≈ 6) |
| **`carpenter_resin`** | 4 | drop — carpenter_bee | bored snags/beams | A natural **wood-oil/sealant**: waterproofs armor, the **wax-wood polish**, a binder that makes wax frames durable, candle hardener. |
| **`hornet_venom`** | 10 | drop — hornet (apex) | great hornet nest | **T3 venom tier** (above `venom_sac`, below boss `royal_venom`): the venom-tipped iron weapons, the strong antidote, the `sting_immunity` "antivenom" gear, a thrown hornet-venom bomb. |
| **`hornet_carapace`** | 10 | drop — hornet | great hornet nest | Big **chitin plate** for T3 carapace armor & the apex trophy; jeweler inlay (a fierce-looking accessory). |
| **`royal_wax`** | 10 | craft — `honey_extractor` on an Apiary frame (premium split) | Apiary tower | **Upgraded beeswax** (denser, gold-flecked): the **honeycomb-plate armor**, sealed-frame upgrades, premium candles, the wax-comb shield. A clean T3 wax tier above `beeswax`. |
| **`comb_foundation`** | 2 | craft — workbench (`beeswax` + thin `plank`) | — | A pre-stamped wax sheet that **seeds a `bee_frame`** — the consumable that lets the Apiary run; the beekeeping "ammo." |
| **`silk_thread`** | 3 | drop/forage — cabbage_white chrysalis | crop rows | A **light wild silk** (cheaper than canonical `silk`, richer than `thread`): the pollinator-outfit weave, fine nets, bandages. (thread-tier ≈ 3) |
| **`pollen_loaf`** | 2 | craft — cooking_pot (`pollen` + `bumble_nectar`) | — | An upgraded `bee_bread`: **fed to the Apiary to raise honey/wax yield** over coming days; also a stamina food. |
| **`thistle_down`** | 1 | forage — thistle/dandelion heads on the hilltop | open meadow slopes | Fluffy fiber: stuffing for soft gear, a fire-starter tinder, a parachute-seed décor; a cheap `fiber` cousin. |
| **`clover_honey`** | 6 | craft — `honey_extractor` (clover-forage frame) | Apiary tower | A **named single-flower honey** (artisan-flavor variant of `honey`): higher sell at the artisan multiplier, a gift/quality cooking input. |

> Reuse note: `pollen`, `honey`, `honeycomb`, `beeswax`, `propolis`, `royal_jelly`, `nectar_bloom`, `bee_bread`,
> `venom_sac`, `wasp_stinger`, `chitin`, `wood`, `plank`, `thread`, plus all flora/crops reuse existing ids —
> the Meadow plugs straight into the established material ladder and only adds the **upper rungs** (`royal_wax`,
> `hornet_venom`, `bumble_nectar`) that justify the T2→T3 jump.

---

## Recipes debuting here

Wax/venom/pollination crafts at the **T2–T3** band. Each row: output · station · inputs(+counts) · unlock ·
stat/effect · tier. `unlock`: `craft` (have station+recipe) / `buy@apiarist` (the zone NPC, below) /
`find@meadow` (recipe drop). Costs use the tier-point model; the iron-gated rows are the T3 reach.

### Beekeeping operation — the Apiary tower & its loop

| Output | Station | Inputs (×count) | Unlock | Stat / effect | Tier |
|---|---|---|---|---|---|
| `apiary_tower` | sawmill | `plank` ×8 + `bee_frame` ×2 + `carpenter_resin` ×2 + `copper_bar` ×1 | buy@apiarist (recipe) | **Placeable managed hive** — multi-frame honey/wax node; the zone's headline build (upgradeable below) | T2 |
| `bee_frame` | workbench | `plank` ×1 + `comb_foundation` ×1 + `beeswax` ×1 | craft | Insert that an Apiary runs; produces `honeycomb`/`royal_wax` per cycle. The renewable "ammo." | T2 |
| `comb_foundation` ×2 | workbench | `beeswax` ×2 + `plank` ×1 | craft | Stamped wax sheet that seeds a `bee_frame` | T2 |
| `apiary_super` (tier upgrade) | anvil | `iron_bar` ×2 + `royal_wax` ×2 + `carpenter_resin` ×2 | find@meadow / buy@apiarist | **Upgrades an `apiary_tower`** → adds frame slots + `honey_yield_pct`; the T3 capstone of the operation | T3 |
| `royal_wax` + `honey` (split) | honey_extractor | `honeycomb` ×3 + `bumble_nectar` ×1 | craft | Premium artisan split — the **T3 wax engine** (above the basic honey/beeswax split) | T3 |
| `clover_honey` | honey_extractor | `honeycomb` ×2 + `clover` ×2 | craft | Named single-flower honey (artisan sell premium / quality cooking) | T2 |
| `pollen_loaf` | cooking_pot | `pollen` ×4 + `bumble_nectar` ×1 | buy@apiarist | Fed to Apiary → raised honey/wax yield over days; as food: `move_speed_pct +3` + `max_hp +3` | T2 |

### Pest-control — wasps-as-tool

| Output | Station | Inputs (×count) | Unlock | Stat / effect | Tier |
|---|---|---|---|---|---|
| `wasp_lodge` | workbench | `wood` ×6 + `wasp_paper` ×4 + `carpenter_resin` ×1 | buy@apiarist (recipe) | **Placeable** — seeds a paper-wasp **pest-control patrol**: wasps hunt `cabbage_caterpillar`/aphids/beetles in a radius (a crop `harvest_yield` protector) | T2 |
| `pest_lure` (caterpillar bait) | cauldron | `cabbage_caterpillar` ×2 + `honeydew` ×1 + `fiber` ×1 | craft | Thrown — concentrates crop pests at one tile so the wasp patrol (or you) culls them fast | T2 |
| `hornet_trap` | workbench | `glass` ×2 + `bumble_nectar` ×1 + `wasp_paper` ×2 | buy@apiarist | **Placeable trap** — passively thins a hornet nest's patrol (keeps hornets from crashing your hives) | T2 |

### Venom & combat (the hornet answer — T3)

| Output | Station | Inputs (×count) | Unlock | Stat / effect | Tier |
|---|---|---|---|---|---|
| `hornet_lance` (spear) | forge | `iron_bar` ×2 + `hornet_venom` ×2 + `bramble_vine` ×2 | find@meadow (recipe scroll, hornet nest) | `damage_pct +20`, `knockback +1`, long reach — the anti-hornet-swarm weapon; on-hit `poisoned` | T3 |
| `antivenom` | cauldron | `hornet_venom` ×1 + `nettle_leaf` ×2 + `propolis` ×1 | buy@apiarist (recipe) | **Cures `poisoned`** + strong timed `hazard_resist`/`sting_immunity` — the upgraded `antidote` for hornet venom | T3 |
| `venom_bomb` (thrown) | cauldron | `hornet_venom` ×1 + `resin_glob` ×1 + `glass` ×1 | find@meadow | Throwable AoE `poisoned` cloud — great vs a recruited hornet swarm or the nest | T3 |

### Wax goods, food & décor (the gentle side)

| Output | Station | Inputs (×count) | Unlock | Stat / effect | Tier |
|---|---|---|---|---|---|
| `wax_wood_polish` | cauldron | `royal_wax` ×1 + `carpenter_resin` ×1 | craft | Furniture polish (comfort/value tag); waterproofs wood décor | T2 |
| `royal_candle` ×3 | cooking_pot | `royal_wax` ×2 + `silk_thread` ×1 | craft | Premium light décor — bigger `light_radius` aura than the basic beeswax candle | T2 |
| `meadow_mead` | keg | `bumble_nectar` ×2 + `honey` ×2 + `clover` ×1 | buy@apiarist | Aged artisan good (high artisan-multiplier sell); when drunk: `luck +1` + minor `hp_regen` | T2 |
| `pollinators_loaf` (food) | cooking_pot | `clover_honey` ×1 + `wheat` ×2 + `pollen` ×1 | craft | Timed food: `pollination +5` + `harvest_yield +1` (a farming-session buff) | T2 |
| `bumble_butter` (food) | cooking_pot | `bumble_nectar` ×1 + `apple` ×2 | craft | Timed food: `max_hp +5` + `hp_regen` (hearty) | T2 |
| `hand_pollinator` (tool) | workbench | `wood` ×2 + `bumble_fuzz` ×2 + `thread` ×2 | craft | Held tool: manual `pollination` on a crop (works when no bees are near) | T2 |
| `gold_dye` | dye_vat | `pollen` ×3 + `bumble_nectar` ×1 | craft | Rich gold/amber dye bath (recolor gear/décor) — the "honey gold" the zone is known for | T2 |
| `hornet_trophy` | workbench | `hornet_carapace` ×2 + `royal_wax` ×1 + `wood` ×2 | find@meadow (after nest cleared) | Mounted hornet-nest trophy — décor / idle-aura flex ("I cleared the hilltop") | T3 |

---

## Signature gear — the **Apiarist's Mantle** (T3 bonus outfit)

The zone's headline reward and the **direct upgrade to Bee Meadow's Beekeeper suit**: a 3-piece **utility
outfit** (mutually exclusive with other outfits per the *one-outfit-at-a-time* rule, `stats_and_bonuses.md §3`).
Where the Beekeeper suit gave *partial* sting immunity and modest honey yield, the Apiarist's Mantle is the
**T3 master-beekeeper kit** — full venom-proof sting immunity (it survives *hornets*), big honey/pollination
output, and a managed-aggro field that makes the whole aggressive meadow farmable. Built from the zone's
signature mats: **`royal_wax`, `bumble_fuzz`, `silk_thread`, `hornet_carapace`** + iron studs.

`bonuses{}` schema per `../stats_and_bonuses.md §1` (additive; `_pct` are percent; `set` ties the set bonus).
Signature stats: **`pollination` + `honey_yield_pct` + `sting_immunity`**.

| Piece (id) | Slot | Station | Inputs (×count) | `bonuses{}` | `set` |
|---|---|---|---|---|---|
| **`apiarist_veil`** | head | loom | `silk_thread` ×4 + `royal_wax` ×1 + `bumble_fuzz` ×2 | `defense:2, sting_immunity:1, honey_yield_pct:10, night_vision:1` | `apiarist` |
| **`apiarist_robe`** | body | loom | `silk_thread` ×5 + `royal_wax` ×2 + `bumble_fuzz` ×3 + `iron_bar` ×1 | `defense:4, honey_yield_pct:20, pollination:10` | `apiarist` |
| **`apiarist_gauntlets`** | hands | anvil | `royal_wax` ×2 + `hornet_carapace` ×1 + `iron_bar` ×1 | `defense:3, pollination:10, harvest_yield:1, sting_immunity:1` | `apiarist` |

**Set bonus (3/3 `apiarist`): "Master of the Hive"**
> *"The whole meadow works for you."* — **full `sting_immunity`** (bumblebees, wasps, **and hornets** can no
> longer damage you), a passive **`calm_radius`** field (bees/wasps never aggro near you — harvest Apiaries and
> manage wasp lodges freely), **`honey_yield_pct +15`** on top of the robe, and **`pollination +10`**.
> Signature: with the Mantle on, the *aggressive* meadow becomes **the most productive farm in the game** —
> you walk through a hornet swarm to your Apiary tower, harvest `royal_wax`, and your wasp patrol culls the
> crop pests while you work.

**Why this set, this stat:** the Meadow's fantasy is *running an aggressive-bee operation and winning*. A
`pollination` + `honey_yield_pct` + `sting_immunity` outfit is the literal mechanical expression of "master
beekeeper," and it cleanly **supersedes the T1–T2 Beekeeper suit** (the obvious upgrade path) while staying an
*outfit* (low combat, high activity mastery) — so it contrasts with the **Thornweave** combat set from the
Wasp Thicket. The `hornet_carapace`/`royal_wax`/`iron_bar` gating pins it firmly to T3, the reward for
clearing the zone's danger spike.

*Optional matching accessory:* **`hornet_pendant`** (jeweler · `hornet_carapace` ×1 + `silver_bar` ×1 +
`quartz` ×1) → `sting_immunity:1, rare_bug_luck:1` — a T3 accessory that stacks venom-proofing without taking
the outfit slot; the bridge to the T5 silver tier. Prune to the 3-piece if it reads cleaner.

---

## Shop / NPC stock — the **Apiarist** (`apiarist_vendor`)

The zone's **advanced-beekeeper vendor** — an occupant with `interaction_type:"npc"` +
`npc{role:"apiarist", ...}` (per `merchants.md §5`). She runs the hilltop apiary at the zone's heart: the
master beekeeper the Bee Meadow's Beekeeper "graduates you to." Sells the Apiary operation parts, the
pest-control kit, the venom answers, and the recipes that unlock the chain. Stock **grows with progress**
(early: Apiary parts; after first `royal_wax` harvest: the Mantle recipes + venom gear). Buys honey/wax/venom
as a strong coin source (a **`bug_value_pct` premium** on `royal_wax`/`hornet_venom`).

### Sells — goods
| Item | Why it's bought, not crafted |
|---|---|
| `apiary_tower` (starter, markup) | Convenience buy of the headline hive so you can start the operation day one |
| `bee_frame` / `comb_foundation` | The Apiary "ammo" — restock so the hive never sits idle |
| `wasp_lodge` (pre-made) | Start a pest-control patrol without first farming `wasp_paper` |
| `calm_spray` ✅ / `bee_smoker` ✅ | The harvest-safe staples (reused from Bee Meadow; needed *more* here) |
| `antivenom` | The hornet-venom cure — stock-limited daily (forces gathering too) |
| `hornet_trap` (pre-made) | Keep hornets from crashing your hives while you build up |
| `flower_seeds` bundle (clover/thistle) | Plant the hilltop blooms that feed bumblebees + `clover_honey` |

### Sells — recipes (buy → then craft)
| Recipe | Unlocks crafting |
|---|---|
| `apiary_tower` | The managed-hive build |
| `apiary_super` | The T3 hive upgrade (alt path to the find@meadow scroll) |
| `wasp_lodge` | The pest-control mechanic |
| `pollen_loaf` / `meadow_mead` | The yield-boost food + the artisan mead |
| `antivenom` | The hornet-venom cure |
| `apiarist_veil` / `apiarist_robe` / `apiarist_gauntlets` | The **Apiarist's Mantle** outfit (gated: appears after first `royal_wax` harvest) |

### Buys — raw goods (coin source)
`honey` · `honeycomb` · `beeswax` · `royal_wax` (premium) · `clover_honey` · `bumble_nectar` · `pollen` ·
`carpenter_resin` · `hornet_venom` (premium) · `hornet_carapace` · `meadow_mead` (artisan multiplier). Raw
sells cheap; **processed/aged sells far more** — the artisan-multiplier lesson, now at the honey-empire scale.

> Gating (Lens of Pacing): the **Mantle** recipes and the venom gear appear only **after the player's first
> `royal_wax` harvest** (i.e., they've actually run an Apiary). The NPC intro hands a free `antivenom` and
> points at the nearest hornet nest as the "graduation exam."

---

## "New toys" hook

The Hilltop Meadow is where beekeeping stops being a side-gig and becomes an **operation you run**. You build
an **Apiary tower** — a real multi-frame managed hive — feed it `bee_frame`s and `pollen_loaf`, and **upgrade
it (`apiary_super`) into a `royal_wax` engine**, your first genuine artisan empire and a steady T3 coin source.
You learn **wasps-as-pest-control**: seed a `wasp_lodge` and a paper-wasp patrol *works for you*, hunting the
`cabbage_caterpillar`s that eat your crops — turning the scary swarm bug into a farmhand whose aggro you manage.
And the meadow finally **bites**: **hornets** are an apex threat with real venom, so the new toys are also
*answers* — a venom-tipped **`hornet_lance`**, an **`antivenom`**, a thrown **`venom_bomb`**, and the headline
**Apiarist's Mantle**, the master-beekeeper outfit whose **full sting-immunity + pollination + honey_yield**
set bonus lets you stand in a hornet swarm and calmly harvest gold-flecked `royal_wax` while your wasps do the
weeding. Clear the hornet nest and you walk out with `hornet_venom` (the seed of the next zone's nastier iron
weapons) and a `hornet_trophy` for the wall.

---

## New id ledger (for cross-doc reconciliation)

**materials / ingredients:**
- `bumble_fuzz` — drop, bumblebee (insulating pile; pollinator-outfit lining, felt/cloth substitute)
- `bumble_nectar` — drop/forage, bumblebee honey-pots / rich flower_patch (thick wild nectar; premium honey/mead/cooking)
- `carpenter_resin` — drop, carpenter_bee (wood-oil/sealant; waterproofing, polish, frame binder)
- `hornet_venom` — drop, hornet apex (T3 venom tier; weapons, antivenom, venom bomb)
- `hornet_carapace` — drop, hornet (big chitin plate; T3 armor, trophy, jeweler inlay)
- `royal_wax` — craft @ honey_extractor premium split (upgraded beeswax; carapace armor, frames, candles)
- `comb_foundation` — craft @ workbench (stamped wax sheet; seeds a bee_frame — beekeeping "ammo")
- `silk_thread` — drop/forage, cabbage_white chrysalis (light wild silk; pollinator-outfit weave, nets)
- `pollen_loaf` — craft @ cooking_pot (upgraded bee_bread; Apiary yield boost + food buff)
- `thistle_down` — forage, hilltop thistle/dandelion (fluffy fiber; stuffing, tinder, décor)
- `clover_honey` — craft @ honey_extractor (named single-flower honey; artisan sell, quality cooking)
  (reuse: `pollen`, `honey`, `honeycomb`, `beeswax`, `propolis`, `royal_jelly`, `nectar_bloom`, `bee_bread`,
  `venom_sac`, `wasp_stinger`, `chitin`, `wood`, `plank`, `thread`, `wasp_paper`, `nettle_leaf`, `resin_glob`,
  `bramble_vine`, `honeydew`, plus flora/crops)

**species:** (id → primary drop)
- `bumblebee` → `bumble_fuzz` (also `pollen`/`bumble_nectar`)
- `carpenter_bee` → `carpenter_resin` (also `wood`/`pollen`)
- `hornet` → `hornet_venom` (apex; also `wasp_stinger`/`hornet_carapace`)
- `paper_wasp` ✅ → `wasp_stinger` (reused as the **pest-control ally**; also `venom_sac`/`chitin`)
- `cabbage_white` → `cabbage_caterpillar` (the crop pest; adult also `pollen`/`silk_thread`)

**nodes / placeables:**
- `apiary_tower` — managed multi-frame hive (the bee_skep's T2–T3 successor)
- `wasp_lodge` — placeable paper-wasp pest-control patrol shelter
- `hornet_trap` — placeable hornet-thinning trap
- (reuse: `flower_patch`, `bee_skep`)

**items / recipes:**
- `apiary_tower` — placeable hive, sawmill, T2
- `bee_frame` — Apiary insert, workbench, T2
- `comb_foundation` — wax sheet, workbench, T2
- `apiary_super` — hive upgrade, anvil, T3
- `clover_honey` — artisan honey, honey_extractor, T2
- `pollen_loaf` — Apiary feed / food, cooking_pot, T2
- `wasp_lodge` — pest-control placeable, workbench, T2
- `pest_lure` — thrown pest bait, cauldron, T2
- `hornet_trap` — placeable trap, workbench, T2
- `hornet_lance` — weapon (spear), forge, T3 — damage_pct/knockback/long-reach + on-hit poisoned
- `antivenom` — consumable, cauldron, T3 — cures poisoned + hazard_resist/sting_immunity
- `venom_bomb` — thrown consumable, cauldron, T3 — AoE poisoned cloud
- `wax_wood_polish` — furniture polish, cauldron, T2
- `royal_candle` — light décor, cooking_pot, T2
- `meadow_mead` — aged artisan good, keg, T2 — luck/hp_regen
- `pollinators_loaf` — food, cooking_pot, T2 — pollination/harvest_yield buff
- `bumble_butter` — food, cooking_pot, T2 — max_hp/hp_regen
- `hand_pollinator` — tool, workbench, T2 — manual pollination
- `gold_dye` — dye, dye_vat, T2 — gold/amber color
- `hornet_trophy` — décor, workbench, T3 — idle-aura flex (post-nest)
- `apiarist_veil` — outfit (head), loom, T3 — defense/sting_immunity/honey_yield_pct/night_vision; set: apiarist
- `apiarist_robe` — outfit (body), loom, T3 — defense/honey_yield_pct/pollination; set: apiarist (keystone)
- `apiarist_gauntlets` — outfit (hands), anvil, T3 — defense/pollination/harvest_yield/sting_immunity; set: apiarist
- `hornet_pendant` — accessory, jeweler, T3 — sting_immunity/rare_bug_luck (bridge to T5 silver)
- `apiarist_vendor` — NPC ("the Apiarist") — advanced-beekeeper shop at the hilltop apiary
