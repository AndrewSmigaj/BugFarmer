# Zone Content Sheet — Deep Swamp

> **Status:** design only (content brainstorm). Generous-by-design — we prune later, never thin.
> Reuses existing ids where they exist; new ids are `snake_case`. Builds directly on
> [`shallow_swamp.md`](shallow_swamp.md) — reuses its swamp vocabulary (`peat`, `bog_iron`,
> `reed_fiber`, lily/duckweed/cattail flora, `tannin`, `leech_extract`) rather than re-coining it.

| | |
|---|---|
| **Zone** | Deep Swamp |
| **Grid** | 1,3 — stilted-platform deep wetland, west of the Shallow Swamp |
| **Tier band** | **T3–T4** (a real step up — this is the EXTRA-HARD water zone) |
| **Theme** | Deep, dark, drowned bog — stilt-walkways over open black water, sunken hollows, aquatic predators |
| **Identity** | The DANGEROUS deep-water zone: aquatic predators, the **Hermit's hut** (swamp survival gear),
**bog alchemy** (disease & poison), deeper `water_breath` / `water_walk` gear, disease/poison hazard |
| **Existing swamp vocab (reuse)** | `peat`, `bog_iron`, `reed_fiber`, `reed_stalk`, `cattail_fluff`, `lily_pad`,
`lily_extract`, `duckweed_paste`, `marsh_clay`, `tannin`, `tanned_hide`, `swamp_gas`, `leech_extract`,
flora reeds/cattail/duckweed/pondweed/water_lily/marsh_plant; herbs yarrow/sage/mint; `mushroom_glow` |
| **Hazards** | **deep open water** (instant drown without sustained `water_breath`, not a short timer);
**swamp fever / miasma** (a stacking disease DoT in the miasma fog — `hazard_resist` slows it, only an
**antidote/cure** clears it); **predator ambush** (giant water bugs lunge from below); **venom** (mosquito
swarms + predator bites apply poison); **cold black water** (`water_retention_pct` / warmth matters at depth) |

The Deep Swamp is where the Shallow Swamp's *traversal* gear stops being enough. A `reed_snorkel`'s short
timer drowns you here; you need **sustained** breathing and a real **disease defense** to survive the miasma.
It's the zone of **aquatic predators** — the giant water bug ambushes from below, dragonfly nymphs hunt the
shallows — and of **bog alchemy gone dark**: disease cures, venom reagents, and the Hermit who has learned to
live in the drowned bog and will sell you how. You come here for the deep-diver gear, the apex-predator drops,
and the next rung of the water-survival ladder.

---

## 1. Species & drops

World-guide species for this zone: **mosquitoes (aggressive swarms), dragonflies, water striders, giant
water bugs**. Plus extra deep-water species to fill the predator food web and give more T3–T4 drops to craft.
This is an EXTRA-HARD zone, so most species are **hostile** — the apex giant water bug is a genuine fight.

`mosquito_proboscis` already exists (from `shallow_swamp.md`); the deep-swamp swarm **extends** it with a
fever-venom secondary, `mosquito_venom`. New drops introduced here: `dragonfly_wing`, `strider_leg`,
`giant_waterbug_carapace`, plus the predator/extra drops below.

| Species (id) | Tier | Behavior | Catch / combat notes | Primary drop (id) | Secondary drop |
|---|---|---|---|---|---|
| `swamp_mosquito` | T3 | **Aggressive swarms** — dense clouds that actively chase the player at dusk & in miasma fog, biting for a stacking **swamp-fever** DoT (disease, not just sting). Far worse than the shallow `marsh_mosquito`. | Hostile swarm; bites apply `swamp_fever` stacks. Wide `catch_arc` clears a cloud; `sting_immunity`/`hazard_resist` blunt the fever. | `mosquito_proboscis` *(reuse, extend)* | `mosquito_venom` (fever-laced saliva) · `dead_mosquito` *(reuse)* |
| `dragonfly` | T3 | Fast aerial **hunter** — patrols open water in long straight darts, snatches smaller bugs (and mosquito swarms) mid-air. Beautiful, territorial, hard to net. Predator that *thins the mosquitoes* — calming/baiting it backfires. | Aerial catch, high skill; top `rare_bug_luck` (a ruby/emerald morph is the rare). Non-hostile to player but flees hard & fast. | `dragonfly_wing` (large iridescent quad-wing) | `dragonfly_eye` (huge compound eye) · `dead_dragonfly` |
| `dragonfly_nymph` | T3 | The **underwater larval predator** — lurks on the bed in the shallows, ambushes with an extendable jaw. Only reachable/catchable while diving (`water_breath`). The "there's a monster *under* the lily pads" beat. | Underwater hostile-ambush; rewards `defense` + reach. Drops the gilled nymph carapace. | `nymph_jaw` (hinged predatory mask-jaw) | `nymph_gill` · `dead_nymph` |
| `water_strider` | T3 | Skates the **surface tension** of the deep open water in long, fast strides — the deep cousin of the shallow `pond_skater`, bigger and warier. Only catchable from a stilt-platform, a lily-glide, or with `water_walk`. | Surface catch; teaches deep `water_walk`. Non-hostile but very evasive. | `strider_leg` (long hydrofuge rowing leg) | `strider_oil` (richer hydrophobic wax) · `dead_strider` |
| `giant_water_bug` | **T4 (apex)** | The zone's **apex aquatic predator** — a "toe-biter." Submerged, ambushes from below with a stabbing rostrum, injects a **dissolving venom** (heavy DoT). Slow but armored and hits like a truck. The real fight of the zone. | Hostile ambush-predator; a true T4 boss-bug. Rewards `defense`, `knockback`, `hazard_resist` (venom). Drops the signature carapace. | `giant_waterbug_carapace` (thick armored shield) | `waterbug_venom_gland` (raw venom sac) · `dead_giant_waterbug` |
| `swamp_leech` | T3 | The deep cousin of the shallow `leech` — fatter, latches in clusters in the black water for a faster HP drain **plus** a disease-tick. The murky-water hazard, scaled up. | Hostile-passive latch (DoT + minor fever); `hazard_resist` + waders reduce it. Pry/kill. Drops a potent extract. | `leech_extract` *(reuse)* | `dead_leech` *(reuse)* |
| `bog_serpent_fly` *(extra — rare/elite)* | T4 | A long, serpentine **damsel-dragon** that haunts the deepest sunken hollows at night, glowing faintly (`mushroom_glow`-lit). Rare elite spawn; a trophy catch/fight that bridges into bog alchemy. | Rare elite; hostile-evasive. Big `rare_bug_luck` + a unique alchemy reagent. Night/`night_vision` reward. | `serpentfly_scale` (luminous chitin scale) | `serpentfly_ichor` (glowing alchemical ichor) · `dead_serpentfly` |

**Drop → use at a glance**

- `mosquito_venom` → the cheap T3 **venom reagent** for poison coatings, fever-bombs, and the bait line;
  the disease-themed counterpart to shallow `mosquito_proboscis`.
- `dragonfly_wing` → large, strong, iridescent membrane → the **glider/wing-cloak** traversal pieces, a
  fast-attack `attack_speed_pct` reagent, premium gossamer cloth & a brilliant dye.
- `dragonfly_eye` → clarity/sight lens → `night_vision` + `catch_radius` trinkets (see in the murk).
- `nymph_jaw` → a vicious **edged weapon** component (the predatory mask-jaw); reach + bite.
- `strider_leg` → the deep `water_walk` reagent (long hydrofuge legs) → the strider-stride boots & glides.
- `strider_oil` → richer hydrophobic wax than shallow `skater_oil` → deep waterproofing & the diver seal.
- `giant_waterbug_carapace` → the **apex armor plate** — the signature heavy plating for the deep-diver set.
- `waterbug_venom_gland` → potent T4 **venom** (cost-model "venom"=10) → the strongest poison weapon coats,
  and — refined — a key **disease-cure** base (the venom-as-medicine, bog-alchemy beat).
- `serpentfly_scale` / `serpentfly_ichor` → the rare/elite alchemy line: the glowing charm, the deep-cure,
  and the best dye/décor; a trophy reagent.
- `leech_extract` *(reuse)* → still the anticoagulant/regen + cure base, scaled into the deeper salves.

---

## 2. New ingredients / materials (deep-bog gatherables)

Deeper, darker, water-themed gatherables — **not** dupes of the shallow swamp's reeds/peat/lily set. Source
= `forage`/`mine`/`drop`; fed into §3. Generous list — prune later.

| Id | Source (find@deep_swamp) | Use |
|---|---|---|
| `black_silt` | Dredged from the deep bed (a heavy, mineral-black mud, richer & darker than shallow `marsh_clay`). | Smelts to a dense, dark brick (`silt_brick`); a deep-water mortar; a `defense`-grade pottery glaze. The deep-bog building mat. |
| `miasma_essence` | Condensed from the **fever-fog** (miasma) with a sealed jar — the disease vapor itself, weaponizable & curable. | The disease/poison reagent line: fever-bombs, the **antitoxin base** (you fight venom with the venom), miasma-lamp. Volatile — hazard to gather without `hazard_resist`. |
| `swamp_lotus` | A rare deep bloom on the open black water (the deep cousin of `water_lily`; only reachable by diving/gliding). | The signature **cure/clarity** alchemy flower → `lotus_essence`; a potent calming + anti-disease base; a luminous dye/décor. |
| `lotus_essence` | Cauldron-process `swamp_lotus` + (existing) `lily_extract`. | The **anti-disease / anti-poison** alchemy core (the deep-cure); a strong `calm_radius` base; the deep-diver salve treatment. |
| `bog_pearl` | Prised from giant-bivalve clumps on the deep bed (a dark freshwater pearl; rare dive drop). | **Gem-minor** tier reagent for the jeweler — the deep-water charm cores (`gem_luck`, `water_breath` trinkets); a luxury sell. |
| `sunken_log` | Salvaged **bog-oak** dredged from under the water (waterlogged, iron-hard ancient timber). | A premium, water-resistant `plank`-grade structure mat (`bogwood_plank`); the stilt-platform & boat building line; a dark hardwood weapon haft. |
| `deepwater_kelp` | Harvested while diving — long dark fronds in the deep channels. | Loom fiber for the **wet-suit / diver-skin** weave (stretchy, sealing); a `water_retention_pct` lining; a cooking/alchemy iodine note (anti-fever). |
| `cave_quartz` | Mined from sunken rock outcrops in the deepest hollows (a swamp-native `quartz`/`crystal` source). | Ties the deep swamp into the **gem/jeweler** ladder without a dry mine: smelt/cut → `quartz`/`crystal` (existing) for the diver-helm lens & charm cores. |
| `serpent_glow_cap` | A `mushroom_glow`-class fungus that only fruits in the sunken hollows, brighter than the common glow shroom. | A sustained **`light_radius`** reagent for the deep dark (the murk is near-black); a luminous alchemy/dye additive. |
| `frog_toxin` | Milked from the bright bog frogs on the deep banks (the deep cousin of the shallow `frog_spawn` line). | A **poison** weapon-coat reagent and, refined with `lotus_essence`, an antidote component (toxin → tolerance). A `dodge_chance`/agility brew note. |

New raw building mats this introduces: `silt_brick` (from `black_silt`), `bogwood_plank` (from `sunken_log`)
— T3 deep-bog structure pieces that read as "stilt-platform over black water."

---

## 3. Recipes debuting here

Each: output · station · inputs (+counts) · unlock · stat/bonus · tier. Costs sanity-checked against the
tier-point model (wood/fiber/stone/sand/clay=1; plank/coal/brick/glass=2; copper_bar/thread=3; bronze/cloth=4;
iron_bar/silk=6; steel/silver/gem-minor/**venom**=10; gold/gem-major=16; platinum/diamond=24–40). Everything
here is **gated T3 or T4** — a real step above the shallow swamp's T2–T3.

### Deep traversal (the headline — *sustained* water_breath & deep water_walk)

| Output (id) | Station | Inputs | Unlock | Bonus | Tier |
|---|---|---|---|---|---|
| `diving_suit` (body) | workbench | `tanned_hide` ×4 *(reuse)*, `deepwater_kelp` ×6, `strider_oil` ×4, `iron_bar` ×2 | buy@hermit | **sustained `water_breath`** (no timer — survive deep water) + `water_retention_pct +15` + `defense +2` | T3 |
| `deep_diver_helm` (head) | anvil | `steel_bar` ×2, `glass` ×2, `cave_quartz` ×2 *(→ `crystal` lens)*, `strider_oil` ×3 | buy@hermit (gated: own `diving_suit`) | **sustained `water_breath`** + `light_radius +3` + `defense +3` + `hazard_resist +1` | T4 |
| `strider_striders` (boots) | workbench | `strider_leg` ×4, `strider_oil` ×4, `tanned_hide` ×2, `cattail_fluff` ×3 *(reuse)* | buy@hermit | **`water_walk` (deep, sustained)** + `move_speed_pct +8` on water + `defense +1` | T3 |
| `dragonfly_glider` (back/accessory) | jeweler/workbench | `dragonfly_wing` ×6, `sunken_log` ×2 *(haft frame)*, `reed_fiber` ×4 *(reuse)*, `silk` ×2 | find (recipe scroll, deep hollow) | `fall_resist`, glide across open-water gaps, brief `water_walk` on landing, `move_speed_pct +4` | T4 |
| `pressure_charm` (accessory) | jeweler | `bog_pearl` ×1 *(gem-minor)*, `lotus_essence` ×1, `silver_bar` ×1 | find / buy@hermit | extends/`water_breath` reserve + `hazard_resist +1` (cold/pressure) — the dive-deeper trinket | T4 |

### Bog alchemy — disease, venom & cure (cauldron; the dark branch)

| Output (id) | Station | Inputs | Unlock | Effect (timed unless noted) | Tier |
|---|---|---|---|---|---|
| `fever_cure` *(anti-disease — required survival item)* | cauldron | `lotus_essence` ×1, `waterbug_venom_gland` ×1 *(venom-as-medicine)*, `sage` ×2 *(reuse)*, `deepwater_kelp` ×2 | buy@hermit | **clears all `swamp_fever`/disease stacks** + temporary disease immunity window + small `hp_regen` | T3 |
| `deep_antitoxin` | cauldron | `miasma_essence` ×2, `lotus_essence` ×1, `frog_toxin` ×1, `mint` ×1 *(reuse)* | buy@hermit | cures venom/poison + strong `hazard_resist` burst (the deep `marsh_antidote`) | T3 |
| `deep_breathing_potion` | cauldron | `leech_extract` ×2 *(reuse)*, `lotus_essence` ×1, `deepwater_kelp` ×3 | buy@hermit | timed **sustained** `water_breath` (the consumable route before the suit/helm) | T3 |
| `venom_coating` *(weapon buff)* | cauldron | `waterbug_venom_gland` ×1 *(venom)*, `frog_toxin` ×2, `mosquito_venom` ×3 | find | coats a weapon: applies `venom` DoT on hit (strong poison damage) for a timed window | T4 |
| `fever_bomb` *(thrown)* | cauldron | `miasma_essence` ×2, `mosquito_venom` ×3, `clay` ×1 | find/buy@hermit | thrown AoE: a `swamp_fever`/poison cloud vs bugs (disease as a weapon) | T4 |
| `glowcap_oil` | cauldron | `serpent_glow_cap` ×3, `peat` ×2 *(reuse)* | auto | refills a deep-lantern — sustained `light_radius` for the near-black murk | T3 |
| `serpent_elixir` *(rare)* | cauldron | `serpentfly_ichor` ×1, `lotus_essence` ×1, `bog_pearl` ×1 | find (rare, elite drop) | timed: `night_vision` + `dodge_chance +8` + `move_speed_pct` — the elite trophy brew | T4 |

### Weapons / tools (T3–T4 — ties combat to the apex predator)

| Output (id) | Station | Inputs | Unlock | Bonus | Tier |
|---|---|---|---|---|---|
| `nymph_glaive` *(swamp weapon)* | forge | `steel_bar` ×1, `nymph_jaw` ×2, `sunken_log` ×1 *(bog-oak haft)*, `leech_extract` ×1 *(reuse)* | find (apex-area drop recipe) | long-reach polearm tuned vs water bugs: high `damage_pct` vs aquatic/arthropod, `knockback +2`, light `venom` | T4 |
| `toebiter_maul` *(heavy swamp weapon)* | forge | `steel_bar` ×2, `giant_waterbug_carapace` ×2, `sunken_log` ×1 | buy@hermit (gated: apex slain) | slow, heavy `knockback +3`, big `damage_pct`, stuns the predators — the anti-apex weapon | T4 |
| `harpoon_gun` *(aquatic-catch tool)* | anvil | `steel_bar` ×1, `bogwood_plank` ×2, `strider_leg` ×2, `dragonfly_wing` ×2 | buy@hermit | **deep-water catch tool**: long-range tethered catch of surface/diving bugs & fish from a platform; `catch_radius +3`, `catch_cap +6` over deep water | T3 |
| `dredge_net` *(aquatic-catch tool, dive)* | loom | `deepwater_kelp` ×4, `reed_fiber` ×6 *(reuse)*, `strider_oil` ×2 | auto | a weighted underwater catch-net: passively catches diving bugs/nymphs & deep fish when placed (deep `fish_trap`); `catch_cap +8` underwater | T3 |
| `silt_dredge` *(tool)* | anvil | `steel_bar` ×1, `bogwood_plank` ×1 | auto | digs `black_silt`/`bog_pearl`/`sunken_log`/`cave_quartz` faster (deep-dredge speed); upgrade of the shallow `dredge_shovel` | T3 |

### Deep-bog cloth & building crafts

| Output (id) | Station | Inputs | Unlock | Bonus / use | Tier |
|---|---|---|---|---|---|
| `kelp_weave` (cloth substitute) | loom | `deepwater_kelp` ×4 | auto | stretchy sealing fabric — the wet-suit/diver-skin weave (substitutes `cloth` for water gear) | T3 |
| `bogwood_plank` (building mat) | sawmill | `sunken_log` ×1 | auto | water-resistant bog-oak plank — stilt platforms, boats, weapon hafts | T3 |
| `silt_brick` (building mat) | furnace | `black_silt` ×2, `peat` ×1 *(fuel, reuse)* | auto | dense dark waterproof brick (deep-water construction & glaze) | T3 |
| `stilt_platform` (placeable floor) | sawmill | `bogwood_plank` ×3, `iron_bar` ×1 | buy@hermit | a walkable platform **over deep water** — build out across the open bog (the deep-build toy) | T3 |
| `deep_lantern` (placeable/held light) | workbench | `glass` ×2, `bogwood_plank` ×1, `serpent_glow_cap` ×1 | craft | sustained `light_radius` décor/held light for the murk | T3 |
| `deep_swamp_dye` (set: ink-black / lotus-violet / serpent-glow) | dye_vat | `black_silt` / `swamp_lotus` / `serpentfly_scale` | auto | the deep palette for the diver outfit & trophy décor | T3 |

---

## 4. Signature BONUS gear — the **Bog-Hunter / Deep-Diver set** (T3→T4)

The zone's identity outfit: a **deep-diver / bog-hunter** rig that lets you live *under* the black water and
fight the predators in it. Higher `defense` than the shallow Marshwalker set (this is T3–T4 armor, not just
traversal), with the deep-water verbs and the disease/venom resistances as the headline. Built from the deep
drops & gatherables — `giant_waterbug_carapace`, `tanned_hide`, `deepwater_kelp`, `strider_leg`/`strider_oil`,
`steel_bar`, `lotus_essence`. Three core pieces (+ optional gauntlets), paper-doll overlay reads as
"armored bog-hunter in a diving rig."

`bonuses{}` schema per `../stats_and_bonuses.md §1` (additive; `_pct` are percent; `set` ties the set bonus).

| Piece (id) | Slot | Made @ | Inputs | Per-piece bonuses | Tier |
|---|---|---|---|---|---|
| `boghunter_helm` | head | anvil | `steel_bar` ×1, `giant_waterbug_carapace` ×1, `cave_quartz` ×1 *(lens)*, `tanned_hide` ×1 | `defense +3`, **`water_breath` (sustained)**, `light_radius +2`, `night_vision +1` | T4 |
| `boghunter_cuirass` | body | anvil | `steel_bar` ×2, `giant_waterbug_carapace` ×2, `deepwater_kelp` ×4, `kelp_weave` ×2 | `defense +4`, `hazard_resist +2` (disease/venom), `water_retention_pct +15` | T4 |
| `boghunter_waders` | legs/feet | workbench | `tanned_hide` ×4, `strider_leg` ×3, `strider_oil` ×4, `giant_waterbug_carapace` ×1 | `defense +2`, **`water_walk` (deep, sustained)** + `terrain_immunity` (no mud-slow) + `move_speed_pct +5` on water | T3–T4 |
| `boghunter_gauntlets` *(optional 4th)* | hands | anvil | `steel_bar` ×1, `giant_waterbug_carapace` ×1, `lotus_essence` ×1 | `defense +2`, `thorns` vs water bugs, leech/latch-pry speed, minor `crit_chance` | T4 |

**Unlock:** `boghunter_waders` & `boghunter_cuirass` recipes `buy@hermit` (cuirass gated on owning the
`diving_suit`/apex slain); `boghunter_helm` `buy@hermit`; gauntlets `find` (rare deep-hollow scroll).

### Set bonus — "Bog-Hunter" (escalating)

- **2-piece:** `water_breath` & `water_walk` both **sustained** (no flicker) everywhere + `hazard_resist +1`
  — you can live in the deep water indefinitely.
- **3-piece (full):** add **disease immunity** (`swamp_fever`/miasma can't stack on you) + `defense +3`
  + `hazard_resist +2` (venom barely lands) + `dodge_chance +6` — the full deep-predator-hunting rig.
- **4-piece (with gauntlets):** predators **can't ambush-stun** you (the giant water bug's lunge is
  telegraphed/negated) + `thorns` + `crit_chance +5` vs aquatic bugs — built to *hunt the apex*, not flee it.

Design intent: where the Shallow Swamp's Marshwalker set *unwalls* the water, the Bog-Hunter set lets you
**own** it — survive the disease and venom, breathe and walk the deep indefinitely, and turn around to *hunt*
the giant water bug instead of dying to it. Defense is genuinely T4-grade (this is best-in-slot for the
deep swamp), but it's specialized: pure aquatic. Swap to a land plate set for a dry fight (GDD: one outfit at
a time = the build choice). The cuirass/helm lean on the apex `giant_waterbug_carapace`, so the set is the
**reward loop for beating the zone's boss-bug**, not just for crafting.

### Signature accessories (jeweler / drops)

| Accessory (id) | Source | Bonus |
|---|---|---|
| `pearl_charm` | jeweler (`bog_pearl` + `silver_bar`) | `gem_luck` + `hazard_resist +1` — the deep-water luck/protection core |
| `dragoneye_lens` | jeweler (`dragonfly_eye` + `cave_quartz`/`glass`) | `night_vision` + `catch_radius +1` — see & catch in the murk |
| `serpent_glow_charm` | find / jeweler (`serpentfly_scale` ×2 + `serpentfly_ichor` ×1) | `light_radius +2` + `rare_bug_luck` + tiny `move_speed_pct` — the elite trophy trinket |
| `toebiter_fang` | drop/quest (`waterbug_venom_gland`-line) | `damage_pct` vs bugs + light `venom`-on-hit — the apex-bug combat charm |

---

## 5. Shop / NPC — **The Hermit (deep-swamp survivalist)**

A reclusive **Hermit** living in a stilt-built hut over the black water (occupant w/
`interaction_type:"npc"`, `npc{role:"swamp_vendor"}`). He has survived the deep bog for years and sells the
hard-won **survival gear, deep-dive equipment, and bog-alchemy recipes** — plus the cures you need to not die
to the fever. Stock **grows with progress** (Lens of Pacing): the deepest gear (`deep_diver_helm`,
`boghunter_cuirass`, `toebiter_maul`) only stocks once you own the `diving_suit` / have slain the apex.

### Sells — goods (survival gear first)

| Item | Rough cost | Notes |
|---|---|---|
| `fever_cure` | mid | **the survival staple** — you'll die in the miasma without it; on hand from day one |
| `deep_antitoxin` | mid | venom/poison cure — predator & swarm protection |
| `deep_breathing_potion` | mid–high | the consumable deep-`water_breath` route (before the suit) |
| `glowcap_oil` / `deep_lantern` | low–mid | light in the near-black murk (deep-swamp survival basic) |
| `lotus_essence`, `miasma_essence` | mid–high | alchemy reagents (skip the dangerous gather) |
| `bait` *(from `mosquito_venom`/`frog_toxin`)* | low | for the `harpoon_gun` / `dredge_net` catch loop |
| `stilt_platform` / deep-swamp décor | mid | build out over the water; a buy-only lotus-pond / serpent-glow décor |

### Sells — recipes (the coin sink)

`diving_suit` · `deep_diver_helm` · `strider_striders` · `pressure_charm` · `fever_cure` · `deep_antitoxin`
· `deep_breathing_potion` · `harpoon_gun` · `dredge_net` · `boghunter_helm` · `boghunter_waders` ·
`boghunter_cuirass` · `toebiter_maul` · `stilt_platform` · `fever_bomb`. (Gated: the deepest recipes —
`deep_diver_helm`, `boghunter_cuirass`, `toebiter_maul` — only stock once you own the `diving_suit` and/or
have slain the apex `giant_water_bug`.)

### Buys — coin sources

Pays **high** for the dangerous deep drops & gatherables (a reason to risk the deep water): `dragonfly_wing`,
`dragonfly_eye`, `strider_leg`, `nymph_jaw`, `giant_waterbug_carapace`, `waterbug_venom_gland`,
`serpentfly_scale`/`serpentfly_ichor`, `bog_pearl`, `swamp_lotus`, `cave_quartz`, `sunken_log`, and caught
deep fish. Apex & elite drops pay the most — the bounty for clearing the zone's hardest fights.

### Flavor / tips

Intro hook: warns you the deep water drowns the *unprepared even with a snorkel* (the shallow gear isn't
enough), that the **fever-fog** is what really kills here, and that something big — the toe-biter — waits
under the lily pads. Points you at the `fever_cure` and the `diving_suit` first. Random tips seed the
miasma/disease & venom hazards, the dive-only drops, and the apex-hunt reward.

---

## 6. "New toys" hook

The Deep Swamp is the **EXTRA-HARD water zone** that turns the Shallow Swamp's *traversal* into *survival and
predation*. Your shallow snorkel drowns here — you need a real **diving suit** and **sustained** breathing,
and the air itself (the **fever-fog** miasma) is a disease that only a **cure** clears, so the toy is a whole
new **survival layer**: cure your fever, antidote the venom, light the near-black murk, and *then* go under.
It opens a **dive-only world** — underwater predators (the dragonfly nymph), bed-floor gatherables
(`bog_pearl`, `sunken_log`, `cave_quartz`), and aquatic-catch tools (`harpoon_gun`, `dredge_net`) that reward
hunting *below* the surface you used to just cross. It debuts the game's **dark bog-alchemy** branch —
disease-as-weapon (`fever_bomb`), venom coatings, and the venom-as-medicine cure loop — and the **predator
hunt**: the apex `giant_water_bug` is a genuine T4 boss-bug whose carapace builds the **Bog-Hunter set**, the
deep-diver outfit that lets you *own* the black water instead of fearing it. And it carries the swamp into the
gem/steel ladder via `cave_quartz` and `bog_pearl`, so even the deep jewelry has a drowned-bog flavor.

---

## New-id summary

```
materials:
  black_silt, miasma_essence, swamp_lotus, lotus_essence, bog_pearl, sunken_log,
  deepwater_kelp, cave_quartz, serpent_glow_cap, frog_toxin,
  silt_brick, bogwood_plank, kelp_weave, deep_swamp_dye
  # reuse from shallow_swamp: peat, bog_iron, reed_fiber, reed_stalk, cattail_fluff,
  #   lily_pad, lily_extract, duckweed_paste, marsh_clay, tannin, tanned_hide,
  #   swamp_gas, leech_extract

species: (id -> primary drop)
  swamp_mosquito       -> mosquito_proboscis     # reuse + extend (new secondary: mosquito_venom)
  dragonfly            -> dragonfly_wing          # secondary: dragonfly_eye
  dragonfly_nymph      -> nymph_jaw               # secondary: nymph_gill
  water_strider        -> strider_leg             # secondary: strider_oil
  giant_water_bug      -> giant_waterbug_carapace # APEX T4; secondary: waterbug_venom_gland
  swamp_leech          -> leech_extract           # reuse drop id (deep cousin of leech)
  bog_serpent_fly      -> serpentfly_scale        # rare/elite; secondary: serpentfly_ichor
  # new secondary/reagent drops: mosquito_venom, dragonfly_eye, nymph_jaw, nymph_gill,
  #   strider_leg, strider_oil, giant_waterbug_carapace, waterbug_venom_gland,
  #   serpentfly_scale, serpentfly_ichor
  # carcass drops: dead_dragonfly, dead_nymph, dead_strider, dead_giant_waterbug, dead_serpentfly
  #   (dead_mosquito, dead_leech reuse existing ids)

items:
  diving_suit            # body — sustained water_breath + water_retention + defense (T3)
  deep_diver_helm        # head — sustained water_breath + light_radius + defense (T4)
  strider_striders       # boots — deep water_walk + move_speed (T3)
  dragonfly_glider       # back/accessory — fall_resist + glide + brief water_walk (T4)
  pressure_charm         # accessory — extend water_breath + hazard_resist (T4)
  fever_cure             # cauldron — clears swamp_fever/disease (ANTI-DISEASE) (T3)
  deep_antitoxin         # cauldron — cure venom/poison + hazard_resist (T3)
  deep_breathing_potion  # cauldron — timed sustained water_breath (T3)
  venom_coating          # cauldron — weapon venom DoT buff (T4)
  fever_bomb             # cauldron — thrown disease/poison AoE (T4)
  glowcap_oil            # cauldron — sustained light_radius refill (T3)
  serpent_elixir         # cauldron — night_vision + dodge + move_speed (rare T4)
  nymph_glaive           # forge — reach polearm vs water bugs, knockback, venom (T4)
  toebiter_maul          # forge — heavy anti-apex maul, knockback, stun (T4)
  harpoon_gun            # anvil — aquatic-catch tool, deep catch_radius/cap (T3)
  dredge_net             # loom — underwater catch-net / deep fish_trap (T3)
  silt_dredge            # anvil — deep-dredge dig tool (T3)
  kelp_weave             # loom — cloth substitute, wet-suit weave (T3)
  bogwood_plank          # sawmill — water-resistant bog-oak plank (T3)
  silt_brick             # furnace — dense deep-water brick (T3)
  stilt_platform         # sawmill — walkable platform over deep water (T3)
  deep_lantern           # workbench — sustained light décor/held (T3)
  deep_swamp_dye         # dye_vat — ink-black / lotus-violet / serpent-glow palette (T3)
  boghunter_helm         # head armor — set "boghunter", water_breath (T4)
  boghunter_cuirass      # body armor — set "boghunter", hazard_resist (T4)
  boghunter_waders       # legs/feet armor — set "boghunter", deep water_walk (T3-4)
  boghunter_gauntlets    # hands armor — set "boghunter", thorns/crit (T4)
  pearl_charm            # accessory — gem_luck + hazard_resist
  dragoneye_lens         # accessory — night_vision + catch_radius
  serpent_glow_charm     # accessory — light_radius + rare_bug_luck
  toebiter_fang          # accessory — damage_pct vs bugs + venom-on-hit
  # set id: boghunter (2/3/4-piece bonuses)
```
```
