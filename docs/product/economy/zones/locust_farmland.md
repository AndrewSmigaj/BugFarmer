# Zone Content Sheet — Locust Farmland (0,0 · `locust_farmland_00`)

**Tier:** T4 (steel era, reaching T5) · **Biome:** ruined / devastated farmland · **Difficulty:** HARD (swarm warfare).

The generous content sheet for the **swarm-warfare farm zone**. Everything here is gated to **T4 (steel) and up**,
with a few **T5 reach** items (silver→platinum) for the signature gear and the high-end swarm tech. This zone has
**NO river barrier** — that is deliberate: the locust swarms here *pressure the neighboring medium zones*, so the
fiction and the gear are about **holding a line, clearing a swarm, and defending crops** against waves. The job of
this zone is to feel **dangerous and embattled** while rewarding mastery: AoE swarm-clearing, crop-defense
structures, swarm-harvest tooling, and a marquee harvester/swarm-warden set. We over-produce here; the user prunes later.

> Design contracts this obeys: cost model + stations from [`../crafting.md`](../crafting.md); stat vocab +
> `bonuses{}` schema from [`../stats_and_bonuses.md`](../stats_and_bonuses.md); pacing/gating from
> [`../progression.md`](../progression.md) (T4→T5 hard-zone scope); shop seam from [`../merchants.md`](../merchants.md)
> (ruined-farmhouse vendor). Zone fiction + species roster from the world guide (locusts, grasshoppers, crickets,
> crop beetles).

---

## Species & drops

Locust Farmland is the **swarm-ecology showcase** (crops → grasshopper/cricket grazers → locust mass-outbreak →
crop beetles strip the ruins). Unlike the village, **most species here are dangerous in numbers** — a single
locust is trivial, a *swarm* is a moving wall of damage that strips crops and overruns you. Each species gets a
behavior gloss and at least one **new drop id** that feeds crafting.

| Species (id) | Behavior gloss | Where | Drop(s) — new ids | Drop use |
|---|---|---|---|---|
| **desert_locust** (`locust`) | The headline threat. Spawns as **massive coordinated swarms** that roll across the map in a wall, devour standing crops, and pile damage by *density* (a few are harmless, a swarm shreds you). Scatters under AoE, re-forms relentlessly. The "clear the swarm / harvest the swarm" core loop. | Open ruined fields, crop rows, swarm-fronts | **`locust_wing`** (translucent flight wing), **`swarm_essence`** (concentrated swarm-pheromone residue, see materials) | `locust_wing` → light swarm-warden armor + lure/bait + a glider décor; `swarm_essence` → the swarm-lure & the AoE weapon charge |
| **giant_grasshopper** (`grasshopper`) | Big solo/loose-pack ambusher; **long leap-charges** that close distance fast and knock you back, then a heavy bite. Not a swarm but a bruiser — punishes melee, rewards spacing/knockback. Strips crop leaves between charges. | Field edges, fence lines, tall ruin grass | **`grasshopper_leg`** (powerful spring leg), `chitin` (exists) | `grasshopper_leg` → mobility/knockback gear (spring-step boots) + a hearty food + a launcher part |
| **field_cricket** (`cricket`) | Nocturnal; mostly passive by day, **swarms and grows aggressive at night** (the night-vision gate). Its *song* maddens/draws other bugs — a cricket chorus reinforces a nearby locust swarm. Burrows; pops up to chirp-buff allies. | Burrows, ruins, active at night | **`cricket_song_organ`** (the resonant stridulation organ), `dead_cricket` (exists pattern) | `cricket_song_organ` → the swarm-LURE tech + a sonic/`calm`-counter device + a music décor |
| **crop_beetle** (`crop_beetle`) | Armored slow grinder that **eats placed crops and wooden structures** (chews your defenses, not just you). Tanky, low damage, high nuisance — ignores you to wreck your farm. Curls plate-side-up under threat. | Crop plots, around structures, compost | **`crop_beetle_shell`** (thick ridged carapace), **`beetle_mandible`** (grinding jaw) | `crop_beetle_shell` → heavy crop-defense plating + the warden body armor; `beetle_mandible` → a harvest sickle edge + a grinder station part |
| **mantis_reaper** (`mantis`) | *(bonus apex — elite/miniboss)* The swarm's predator and yours: a large ambush mantis that **picks off stragglers and players alike** with a fast reaping strike + high crit. Rare spawn at swarm peaks; the zone's "oh no" elite. High-value harvest. | Swarm-peak events, ruin thickets | **`mantis_scythe`** (the raptorial blade), **`reaper_chitin`** (dense apex carapace) | `mantis_scythe` → high-end swarm-clearing weapon edge (T5 reach) + trophy; `reaper_chitin` → set capstone plating |
| **swarmling_nymph** (`nymph`) | *(bonus — swarm fodder)* Juvenile locusts: fast, weak, spawned in clouds *behind* a swarm front; trivial alone but inflate swarm density and **mature into adults if left alive** (clear them or the swarm grows). Teaches "thin the swarm now." | Behind swarm fronts, hopper bands | **`nymph_husk`** (shed molt skin) | `nymph_husk` → cheap bulk crafting filler (mulch, paper-chitin, bait extender) + compost |

**Threat/clear teaching:** locusts teach *density-AoE* (you can't single-catch a wall), grasshoppers teach
*spacing & knockback* (don't stand still), crickets teach *night risk + lure/counter* (silence the chorus),
crop beetles teach *defend the structure, not yourself*, the mantis teaches *the elite spike*, and nymphs teach
*thin it before it grows*. Together they make the zone a **swarm-warfare gauntlet** instead of a catch garden.

---

## New ingredients & materials

Zone-signature materials, swarm/farmland-devastation themed. Source = `forage` (pick), `mine` (break),
`drop` (from a bug), `craft` (process). T4-tier value unless noted.

| Id | Source | Where found | Use |
|---|---|---|---|
| **`swarm_essence`** | drop (locust) / craft | rendered down from `locust_wing` + locust bodies at the cauldron | the **charge/ammo** for the AoE swarm weapon; core of the swarm-LURE; a potent fertilizer-or-poison reagent |
| **`blighted_grain`** | forage | devastated crop rows, half-eaten silos, ruined field tiles | the swarm's food + a dark bait; cooked-down into a hearty (if grim) farm ration; compost feedstock |
| **`hardened_husk`** | forage / mine | sun-baked locust-stripped stalks & dried mud-ridges across the ruins | a tough **fibrous plate** material (between `plank` and `chitin`) for crop-defense walls & light armor backing |
| **`chitin_weave`** | craft | loom: `crop_beetle_shell` + `locust_wing` + `thread` processed into a flexible scale-mesh | the signature **armor textile** of the warden set — chitin scales bound into cloth; T4 |
| **`scorched_clay`** | mine | the cracked, fire-hardened earth of the burned farmhouse & field | a stronger `brick`/`kiln` material; the crop-defense rampart block; T4 |
| **`locust_oil`** | craft | press/render `grasshopper_leg` + locust bodies at the cauldron | a high-energy oil: weapon-coat (damage vs swarms), food fat, lamp/forge fuel |
| **`silk_resin`** | drop/forage | hardened cricket-burrow secretions & nymph molt-glue in the ruins | a binder/adhesive for composites + a sealant for swarm-proofing structures *(complements existing `silk`)* |

*(`locust_wing`, `grasshopper_leg`, `cricket_song_organ`, `crop_beetle_shell`, `beetle_mandible`, `nymph_husk`,
`mantis_scythe`, `reaper_chitin` from the species table are the bug-derived ingredients; listed there to avoid
duplication.)*

---

## Recipes debuting here

All T4 (steel) baseline, with **T5 reach** rows flagged. Station per row (one output → one station, per the
roster in `crafting.md §3`). `unlock`: **craft** (have station + recipe) / **buy@farmhouse** / **find**.
Costs use the tier-point model (Σ inputs); these are expensive by design — this is a hard endgame-adjacent zone.

### Gear & tools

| Output | Station | Inputs (counts) | Unlock | Stat / bonus | Tier |
|---|---|---|---|---|---|
| **swarm_culler** (AoE swarm weapon — see signature recipe below) | forge | steel_bar 4 + mantis_scythe 1 + swarm_essence 3 + locust_oil 2 | craft (buy recipe) | wide-arc AoE that scales `damage_pct` **vs swarm density**; `knockback +3` | **T5 reach** |
| **harvest_sickle** (swarm-harvest tool) | anvil | steel_bar 3 + beetle_mandible 2 + grasshopper_leg 1 | craft | `bug_value_pct +15` & `catch_cap +20` **vs swarm bugs**; harvests scattered swarm fast | T4 |
| **springstep_boots** (feet) | anvil | steel_bar 2 + grasshopper_leg 2 + hardened_husk 2 | craft | `move_speed_pct +8`, `knockback +1`, `fall_resist +2` (leap-dodge swarms) | T4 |
| **cropwarden_buckler** (off-hand) | forge | steel_bar 3 + crop_beetle_shell 3 + scorched_clay 2 | craft | `defense +4`, `thorns +2`, `knockback +2` | T4 |
| **chorusbreaker_charm** (trinket) | jeweler | silver_bar 2 + cricket_song_organ 2 + quartz 1 | craft (buy recipe) | counters cricket-song aggro: `night_vision +2`, nearby swarm `attack_speed_pct -10%` aura | **T5 reach** |
| **swarm_visor** (head) | anvil | steel_bar 2 + locust_wing 4 + glass 2 | craft | `defense +2`, `hazard_resist +3` (swarm/dust), `catch_radius +2` | T4 |

### Structures — crop defense (the zone's signature build loop)

| Output | Station | Inputs (counts) | Unlock | Tag / effect | Tier |
|---|---|---|---|---|---|
| **swarm_barricade** ×2 | stonecutter | scorched_clay 4 + hardened_husk 3 + steel_bar 1 | craft (buy recipe) | crop-defense wall; blocks/slows swarm fronts, beetle-chew resistant | T4 |
| **scarecrow_ward** | sawmill | plank 4 + locust_wing 3 + swarm_essence 1 | craft | area ward: reduces swarm spawn pressure on protected crop plots | T4 |
| **pheromone_pylon** | forge | steel_bar 2 + swarm_essence 4 + silk_resin 2 | craft (buy recipe) | swarm-LURE: pulls swarms toward IT (away from crops/you) — a kite/funnel tool | **T5 reach** |
| **reinforced_crop_plot** | stonecutter | scorched_clay 3 + brick 2 + silk_resin 1 | craft | a crop tile swarms can't strip in one pass (`crop` survives waves) | T4 |
| **iron_silo** | forge | steel_bar 4 + glass 2 + scorched_clay 2 | craft | storage + a `harvest_yield` aura over adjacent plots | T4 |

### Consumables & bait

| Output | Station | Inputs (counts) | Unlock | Effect | Tier |
|---|---|---|---|---|---|
| **swarm_lure** (bait) | cauldron | swarm_essence 2 + blighted_grain 2 | craft / buy@farmhouse | draws a swarm to a marked spot (set up a kill/harvest box) | T4 |
| **swarm_repellent** (consumable) | cauldron | locust_oil 1 + silk_resin 1 + lavender 2 | craft / buy@farmhouse | timed aura: swarm bugs avoid you / lower their density near you | T4 |
| **culler_charge** (weapon ammo) | forge | swarm_essence 1 + locust_oil 1 + coal 1 | craft | recharges the `swarm_culler` AoE blast | T4 |
| **blight_antidote** | cauldron | yarrow 2 + locust_oil 1 + blighted_grain 1 | craft | cures the field-blight/poison DoT swarms inflict | T4 |
| **nymph_mulch** (fertilizer) | compost_bin | nymph_husk 3 + blighted_grain 2 + swarm_essence 1 | craft | strong `crop_growth_pct` boost (turn the swarm's own brood into farm fuel) | T4 |

### Food (cooking_pot — timed buffs, no hunger system)

| Output | Station | Inputs (counts) | Unlock | Buff | Tier |
|---|---|---|---|---|---|
| **harvester_feast** (hearty farm food) | cooking_pot | grasshopper_leg 1 + corn 2 + pumpkin 1 + locust_oil 1 | craft (buy recipe) | big multi-stat: `max_hp +`, `harvest_yield +1`, `defense +1` (long, "feast before the wave") | T4 |
| **fried_locust** | cooking_pot | locust_wing 2 + locust_oil 1 + wheat 1 | craft | `damage_pct +5%` vs swarms (short) | T4 |
| **grain_porridge** | cooking_pot | blighted_grain 2 + corn 1 *(purified)* | craft | `hp_regen` (long, cheap survival ration) | T4 |
| **cricket_skewer** | cooking_pot | dead_cricket 2 + eggplant 1 + thyme 1 | craft | `night_vision +1`, `move_speed_pct +3` (short) | T4 |
| **warden_stew** | cooking_pot | crop_beetle_shell 0 *(broth from beetle_mandible 1)* + cabbage 1 + carrot 1 | craft | `defense +2`, `thorns +1` (short, pre-wave) | T4 |

---

## Signature gear — the **Swarm-Warden's Harvest** (bonus set)

The marquee **T4 set** for this zone: a **harvester / swarm-warden** outfit that fuses *crop-defense* and
*swarm-clearing*. Its signature stats are **`defense` + `harvest_yield`** with **`damage_pct` vs swarms** and
**`knockback`** — you stand in the wave, take the hits, knock the front back, and harvest what you cull. Built
from this zone's drops/materials: **`crop_beetle_shell`, `chitin_weave`, `locust_wing`, `hardened_husk`,
`steel_bar`**, with a **T5 reach** capstone using **`reaper_chitin`/`silver_bar`**. Four pieces; wearing the
core set grants the bonus.

`bonuses{}` schema per `../stats_and_bonuses.md §1` (additive; `_pct` are percent; `set` ties the set bonus).

| Piece (id) | Slot | Station | Inputs (counts) | `bonuses{}` | `set` |
|---|---|---|---|---|---|
| **wardens_helm** | head | anvil | steel_bar 2 + crop_beetle_shell 2 + locust_wing 2 | `defense:3, harvest_yield:1, knockback:1` | `swarm_warden` |
| **wardens_plate** | body | forge | steel_bar 3 + crop_beetle_shell 4 + chitin_weave 2 | `defense:5, damage_pct:5, harvest_yield:1` | `swarm_warden` |
| **wardens_greaves** | feet | anvil | steel_bar 2 + hardened_husk 3 + grasshopper_leg 1 | `defense:3, knockback:2, move_speed_pct:3` | `swarm_warden` |
| **wardens_gauntlets** | hands | forge | steel_bar 2 + chitin_weave 1 + beetle_mandible 1 | `defense:2, harvest_yield:1, damage_pct:5` | `swarm_warden` |

**Set bonus (4/4 `swarm_warden`):**
> *"Hold the line. Harvest the wave."* — additional `defense:+3`, `harvest_yield:+2`, `knockback:+2`, and
> `damage_pct:+10` **vs swarm-tagged bugs**. Signature: while the full set is worn, **culled swarm bugs auto-drop
> a harvest pickup** (you reap what you clear), and **swarm density does reduced damage to you** (you become the
> anchor the wave breaks on). Turns a swarm front from "run away" into "stand and farm it."

**Why this set, this stat:** Locust Farmland is about *defending crops while standing in a wall of bugs* — pure
survival armor would be boring here, and pure DPS would ignore the farm. A `defense` + `harvest_yield` core, with
`damage_pct`-vs-swarm and `knockback`, makes the player the **warden who profits from the wave**: tanky enough to
hold, lethal enough to thin the front, and rewarded for clearing (harvest pickups). It's the clean T4 contrast to
the village's mobility set — heavy, embattled, and built from the carapaces of the very swarm it fights.

*T5 reach capstone:* **wardens_aegis** (off-hand · forge · silver_bar 2 + reaper_chitin 2 + chitin_weave 1) →
`defense:4, thorns:3, knockback:3`, and **upgrades the set bonus to 5/5** (adds a swarm-shockwave on a timed
knockback pulse). Prune to the 4-piece if it reads cleaner; keep as the silver→platinum chase.

---

## Shop stock — **Ruined-Farmhouse Vendor**

The lone holdout farmer in the burned farmhouse — sells **crop seeds** (rebuild the fields), **swarm-defense**
gear/structures, and the zone's **buy-only recipes**. **Buys** raw swarm drops at good prices (the swarm is a
renewable harvest). Stock is T4-priced and grim. Below is the standing shelf.

### Sells — goods
| Item | Why it's bought, not crafted |
|---|---|
| **seeds**: corn, wheat, pumpkin, eggplant, cabbage, carrot (+ `blight-resistant` seed variants) | rebuild the devastated fields; the farm-defense premise |
| **swarm_lure / swarm_repellent** | the core swarm-control consumables, on hand for a wave |
| **blight_antidote** | survival staple vs the swarm DoT |
| **culler_charge ×3** | ammo for the AoE weapon, kept stocked |
| **scarecrow_ward** (assembled) | guaranteed first crop-defense ward if you can't craft yet |
| **harvest_sickle** | the swarm-harvest tool, on the shelf |
| **iron_silo** (flavor/storage) | a reason to invest in the farm + storage |

### Sells — recipes (buy → then craft)
| Recipe | Unlocks crafting |
|---|---|
| **swarm_culler** | the marquee AoE swarm weapon (T5 reach) |
| **pheromone_pylon** | the swarm-LURE funnel structure |
| **swarm_barricade** | the crop-defense wall |
| **chorusbreaker_charm** | the cricket-song counter trinket |
| **harvester_feast** | the hearty pre-wave farm food |

### Buys — raw goods (renewable swarm harvest)
swarm drops (`locust_wing`, `grasshopper_leg`, `cricket_song_organ`, `crop_beetle_shell`, `beetle_mandible`,
`nymph_husk`, `mantis_scythe`, `reaper_chitin`) · processed materials (`swarm_essence`, `locust_oil`,
`chitin_weave`) · foraged (`blighted_grain`, `hardened_husk`, `scorched_clay`) · rebuilt crops. Raw swarm drops
sell well (the swarm is the gold mine); **rendered/crafted sells more** — the artisan multiplier, swarm-scale.

---

## "New toys" hook

Locust Farmland flips the catch garden into a **siege**: the field is a *living wave* — massive locust swarms roll
in as a wall of damage, leaping grasshoppers punish you for standing still, a night-time cricket chorus *reinforces*
the swarm, crop beetles grind down your defenses, and a mantis-reaper elite spikes at the peak. The toy is that the
swarm is both the **threat and the harvest**: you build a **kill-box** (lure → barricade → funnel with a pheromone
pylon), unleash a **wide-arc AoE swarm-culler** that hits harder the denser the wave, and then *reap* what you cull —
the Swarm-Warden's Harvest set literally turns culled swarm bugs into auto-pickups so standing in the wave becomes
*farming the wave*. Every drop loops back: locust wings and beetle shells become your warden armor, the swarm's own
brood (`nymph_husk`) becomes the fertilizer that regrows the crops it ate, and the whole zone is a tense, generous
**defend-the-farm-while-harvesting-the-apocalypse** loop — with the silver→platinum reach gear (and the next zone's
pressure-relief) visibly waiting past the broken fences.
