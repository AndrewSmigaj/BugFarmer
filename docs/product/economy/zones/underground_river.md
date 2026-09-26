# Zone Content Sheet — Underground River

> **Status:** design only (content brainstorm). Generous-by-design — we prune later, never thin.
> Reuses existing ids where they exist; new ids are `snake_case`. Reuses the swamp **water-survival
> lineage** from [`shallow_swamp.md`](shallow_swamp.md) / [`deep_swamp.md`](deep_swamp.md) — the
> `water_walk` / `water_breath` verbs, `tanned_hide`, `reed_fiber`, `deepwater_kelp`, `lotus_essence`,
> `bog_pearl`, `cave_quartz` — rather than re-coining the water-gear ladder. This is the **subterranean
> aquatic** rung above the swamp: same wet survival problem, in the pitch dark.

| | |
|---|---|
| **Zone** | Underground River |
| **Grid** | underground col 2 — waterfall pool feeding a subterranean river/lake; **3,2 medium → 4,2 hard** |
| **Tier band** | **T3–T4** (the deep-underground water zone — a step into the dark above the open-air swamp) |
| **Theme** | Cave water — a roaring waterfall pool, a black subterranean river winding into a still cave lake; glowing aquatic life, freshwater pearls & gems, blind albino fauna |
| **Identity** | The UNDERGROUND AQUATIC zone: **cave fishing**, pearls / freshwater gems, glowing aquatic creatures, **deep water-survival in the dark** (water gear + light + the cold-current hazard), and the Sunken-ruins / Fisher's-platform vendor & treasure |
| **Existing flora (reuse)** | `mushroom_glow`, `cave_moss` |
| **Existing water vocab (reuse)** | `tanned_hide`, `reed_fiber`, `deepwater_kelp`, `kelp_weave`, `lotus_essence`, `bog_pearl`, `cave_quartz`, `leech_extract`; verbs `water_walk` / `water_breath` |
| **Hazards** | **near-total darkness** (no `light_radius` = blind + ambush-prone — the zone's baseline hazard); **deep cold current** (the fast river sweeps you off-line / off a ledge without `water_walk`; `move_speed_pct`/`fall_resist` matter at the falls); **drowning** in the deep lake (sustained `water_breath` needed, not a short timer); **cold black water** (`water_retention_pct`/warmth at depth); **slick cave stone & the waterfall drop** (`fall_resist` near the falls); **silt-clouds** (stirred sediment kills `light_radius` reach — a vision hazard, not damage) |

The Underground River is where the swamp's **water-survival** problem goes **into the dark**. You already
own (or can buy) the snorkel-and-waders idea from the swamp; here the new wall is **light + the current**.
The river runs fast and cold off a waterfall, the lake beyond is deep and pitch-black, and everything that
lives in it has either learned to **glow** or gone **blind and white**. You come here to **fish the cave
water** (a real rod/trap/spear loop in the dark), to prise **freshwater pearls and cave gems** from the bed,
and for the next rung of the water-survival ladder — the **cave-diver / angler** gear that lets you light,
breathe, and walk the underground river instead of being swept away or eaten in the black.

---

## 1. Species & drops

World-guide species for this zone: **cave crayfish, water beetles, aquatic larvae, albino insects**, plus
the **blind cave fish** (the fishing target). Generous food-web fill below; most are aquatic and several are
**glowing** (the zone's only light if you bring none) or **blind/albino** (the dark-adapted beat). New drops:
`crayfish_claw`, `water_beetle_shell`, `cave_pearl`, `albino_chitin`, `blind_fish_scale`, plus the larva /
glow / apex drops.

| Species (id) | Tier | Behavior | Catch / combat notes | Primary drop (id) | Secondary drop |
|---|---|---|---|---|---|
| `cave_crayfish` | T3 | Scuttles backward along the river bed & under ledges; **pincered** and territorial — raises claws and snaps when cornered, but doesn't chase. The zone's bread-and-butter aquatic catch; comes in good numbers in the shallows below the falls. | Bed catch (net/trap or grab); hostile-passive (snaps on contact for a pinch). Rewards `defense` + reach. A "wait for the claws down" catch. | `crayfish_claw` (big serrated pincer) | `crayfish_shell` (segmented tail plate) · `dead_crayfish` |
| `water_beetle` | T3 | **Diving** beetle — rows the open river in bursts, surfaces for an air bubble, dives when threatened (vanishes a beat, like the swamp whirligig but bigger & subterranean). Swarms in the slack water of the lake; high `catch_cap` is rewarded. | Surface/dive catch; cluster = many per swing. Non-hostile but evasive — `water_walk` or a platform helps reach them. | `water_beetle_shell` (domed air-trapping carapace) | `beetle_air_sac` (the hydrophobe bubble-gill) · `dead_beetle` *(reuse)* |
| `aquatic_larva` | T3 | **Caddis/aquatic larvae** — soft grubs that build little pebble/grit cases and cling to the bed & submerged stone. Slow, near-defenseless; a *cluster* dive-catch and the food-web base (crayfish & fish eat them). The classic **live fishing bait** source. | Bed cluster catch (dive/reach); harmless. Squishy — many per grab. The bait pipeline. | `larva_case` (the pebble-grit casing — a natural grit/abrasive) | `aquatic_grub` (the soft body — prime fishing bait) · `dead_larva` |
| `albino_isopod` | T3 | **Blind albino cave isopod** — a ghost-white, eyeless roly-poly detritivore that trundles the wet cave floor & ledges; curls when disturbed (like the village pill-bug, dark-adapted). The "everything down here went white & blind" beat; a calm patience-catch. | Floor catch; harmless, curls & waits. Teaches "approach in the dark gently." High value to the vendor (rarity). | `albino_chitin` (translucent pale plate) | `cave_detritus` (the pale rot it grazes) · `dead_isopod` |
| `glow_mayfly` | T3 | **Bioluminescent mayfly** — drifts in soft glowing clouds over the still lake at the dark hours, the only light in some hollows; short-lived, skittish, re-forms fast. The zone's *living lantern* and a `light_radius` reagent source. Drawn faintly to still water. | Aerial cloud catch (wide `catch_arc` shines); non-hostile, flees fast. High `rare_bug_luck` (a brighter "blue-glow" morph is the rare). | `glow_gland` (the luminescent organ — a light reagent) | `mayfly_wing` (gossamer glowing membrane) · `dead_mayfly` |
| `blind_cave_fish` | T3 | **Blind cave fish** — the fishing target proper. Eyeless, pale, senses vibration; idles in the deep lake & undercut banks, **bolts** at a clumsy approach. Not a bug — the zone's *fish* (caught by rod/spear/trap, not netted). The signature catch of the cave-fishing loop. | **Fishing** catch (rod / `cave_harpoon` / fish-trap), not a net. Flees vibration — rewards a quiet approach / the angler set. | `blind_fish_scale` (pale iridescent scale) | `fish_fillet` (cave-fish meat — cooking) · `dead_fish` |
| `cave_crab` *(extra — elite/apex)* | **T4 (apex)** | A big, pale, **armored cave crab** that haunts the deepest sunken-ruins pool — slow, heavily plated, lashes with a crushing claw and **guards the treasure**. The zone's genuine T4 fight; ambushes from a flooded ruin alcove. | Hostile apex; a true T4 boss. Rewards `defense`, `knockback`, reach. Drops the heavy apex plate. The treasure-guard. | `cave_crab_carapace` (massive pale shield plate) | `crab_claw` (crushing pincer — weapon part) · `dead_crab` |

**Drop → use at a glance**

- `crayfish_claw` → a light edged-tool/weapon component (serrated pincer) + the angler-tackle barb; the
  vendor's bread-and-butter buy.
- `crayfish_shell` / `water_beetle_shell` → light aquatic carapace plating for the **cave-diver / angler**
  gear; the beetle's domed shell → the air-trapping diver helm liner.
- `beetle_air_sac` → a **`water_breath`** reagent (a natural bubble-gill) — the cave route to the breathing kit.
- `aquatic_grub` / `larva_case` → `aquatic_grub` is **prime fishing bait** (the rod/trap loop runs on it);
  `larva_case` is a natural **grit/abrasive** for the stonecutter/jeweler (pearl-polishing).
- `albino_chitin` → a pale, translucent **light/clarity** plating & charm core (dark-adapted) — the angler
  set's signature plate; rarity sell.
- `cave_detritus` → compost/bait substrate in the dark; a `crop_growth_pct` cave-fungus mulch.
- `glow_gland` → the zone's **`light_radius`** reagent (living bioluminescence) → lanterns, the glow-charm,
  glow alchemy; the murk-killer.
- `mayfly_wing` → gossamer glowing membrane → a luminous trinket, fast-attack reagent, brilliant glow-dye.
- `blind_fish_scale` → a pale iridescent **luck/clarity** reagent (the fish "sees" by vibration) →
  `rare_bug_luck`/`catch` trinkets; a pearlescent dye/inlay.
- `fish_fillet` → cooking protein (cave-fish dishes — the food line).
- `cave_pearl` *(see materials — formed in the species' shells too)* → the freshwater **gem-minor** core for
  the jeweler & the pearl accessory.
- `cave_crab_carapace` → the **apex armor plate** — heavy plating for the diver set's high-defense build;
  `crab_claw` → the anti-apex weapon component. The treasure-guard bounty.

---

## 2. New ingredients / materials (cave-water gatherables)

Pearl / aquatic / cave-water themed gatherables — **not** dupes of the swamp's reed/peat/lily set; where a
swamp mat fits (kelp, hide, `cave_quartz`), we **reuse** it. Source = `forage`/`mine`/`drop`/`dive`; fed into
§3. Generous — prune later.

| Id | Source (find@underground_river) | Use |
|---|---|---|
| `cave_pearl` | Prised from freshwater mussel clumps & crayfish/beetle shells on the river bed (a pale cave pearl; rare **dive** drop). Distinct from the swamp's dark `bog_pearl` — luminous, freshwater. | **Gem-minor** jeweler core: the pearl accessory, the angler charm cores (`luck`, `catch_cap`, `water_breath` trinkets); a luxury sell + treasure. |
| `freshwater_nacre` | Ground/leached from spare pearl-shell & mussel with `larva_case` grit (cauldron/jeweler). | Iridescent **mother-of-pearl** inlay & a pearlescent **glaze/dye**; a polish for the gem line; décor sheen. |
| `cave_water` | Drawn from the cold clear river in a sealed jar (mineral-pure, cold subterranean water). | The cave-water alchemy base (cold/clarity brews, the `water_retention_pct` cold-tonic); a pure solvent for the dyes; a `hazard_resist` (cold) reagent. |
| `glow_spore` | Harvested from `mushroom_glow` & `glow_mayfly`-line near the water (the fungal light). | A **`light_radius`** reagent (the gather route to glow-oil/lamps) + a luminous dye/alchemy additive — the dark-killer that isn't a bug drop. |
| `river_silt` | Dredged from the river/lake bed (fine, mineral-rich pale silt, distinct from the swamp's `black_silt`). | Smelts to a pale waterproof brick (`silt_block`); a fine pottery/glaze body; a `crop_growth_pct` amendment for cave-fungus farming. |
| `flowstone` | Mined from the cave's mineral deposits — banded calcite/travertine sheets (a swamp-free, cave-native **stone/granite** flavor source). | A premium banded **building stone** (`flowstone_block`) & décor; cut at the stonecutter; a `defense`-grade tile/glaze. |
| `cave_salt` | Scraped from evaporite crusts on dry ledges above the water line. | A **preservative** (cooking — cures `fish_fillet`), a tanning/alchemy reagent, and a minor `hazard_resist` cooking note; a coin-cheap bait additive. |
| `cold_iron_ore` | Mined from wet ore veins by the water (a cold, water-quenched **iron source** — the cave route to `iron_bar`, like the swamp's `bog_iron`). | Smelt → `iron_bar` (existing) at the furnace; ties the cave water into the T3 metal ladder for the tackle/spear. |
| `lure_resin` | Tapped from sticky mineral seeps / refined from `glow_spore` + `cave_water`. | The **fishing-lure** binder (the tackle line — makes glowing lures the blind fish strike); a sealing/waterproof coat for the diver gear. |
| `pale_root` | Foraged — ghostly pale cave-plant roots threading the wet walls (with `cave_moss`). | A loom fiber substitute for the **angler-line / net** weave; an anti-cold/clarity alchemy note; a pale dye. |

New raw building mats this introduces: `silt_block` (from `river_silt`), `flowstone_block` (from `flowstone`)
— T3 cave-water structure pieces that read as "fisher's platform & sunken-ruin over the underground river."

---

## 3. Recipes debuting here

Each: output · station · inputs (+counts) · unlock · stat/bonus · tier. Costs sanity-checked against the
tier-point model (wood/fiber/stone/sand/clay=1; plank/coal/glass=2; copper_bar/thread=3; bronze/cloth=4;
iron_bar/silk=6; steel/silver/**gem-minor**=10; gold/gem-major=16; platinum/diamond=24–40). Everything here
is **gated T3 or T4** — the deep-underground water rung above the swamp.

### Cave fishing & tackle (the headline catch loop — fishing in the dark)

| Output (id) | Station | Inputs | Unlock | Bonus / use | Tier |
|---|---|---|---|---|---|
| `cave_rod` *(fishing tool)* | workbench | `iron_bar` ×1 *(cold_iron route)*, `pale_root` ×4, `lure_resin` ×2, `crayfish_claw` ×1 *(barb)* | buy@fisher | the **cave-fishing rod** — catches `blind_cave_fish` & cave fish from a bank/platform; `catch_radius +1` over water | T3 |
| `glow_lure` *(tackle/bait)* | workbench | `glow_gland` ×2, `lure_resin` ×1, `aquatic_grub` ×2 | buy@fisher | a glowing lure the **blind fish strike in the dark** — boosts fish-catch rate & `rare_bug_luck` on the rod | T3 |
| `cave_harpoon` *(fishing/spear tool)* | anvil | `iron_bar` ×2 *(cold_iron route)*, `flowstone` ×1 *(haft weight)*, `crayfish_claw` ×2 | buy@fisher | long-reach **spear-fishing** tool: stab fish/crayfish from a ledge; `catch_radius +3` over water, doubles as a light melee weapon | T3 |
| `cave_fish_trap` *(placeable)* | workbench | `pale_root` ×5, `reed_fiber` ×3 *(reuse)*, `lure_resin` ×1 | auto | a **passive cave fish-trap** — placed in the river, catches fish/crayfish/larvae over time (baited with `aquatic_grub`); `catch_cap +6` passive | T3 |
| `dive_net` *(aquatic-catch tool, dive)* | loom | `deepwater_kelp` ×4 *(reuse)*, `pale_root` ×6, `lure_resin` ×2 | auto | a weighted **underwater catch-net** for diving bugs/larvae/beetles & deep fish (needs `water_breath`); `catch_cap +8` underwater | T3 |
| `bed_dredge` *(tool)* | anvil | `iron_bar` ×1, `flowstone` ×1 | auto | dredges `cave_pearl`/`river_silt`/`flowstone`/`cold_iron_ore` from the bed faster (cave-dredge speed) | T3 |

### Deep cave-water survival (water_breath / water_walk / light, in the dark)

| Output (id) | Station | Inputs | Unlock | Bonus | Tier |
|---|---|---|---|---|---|
| `bubble_rebreather` (head accessory) | workbench | `beetle_air_sac` ×2, `glass` ×2, `reed_fiber` ×3 *(reuse)*, `lure_resin` ×1 *(seal)* | buy@fisher | **`water_breath` (sustained)** — the beetle-gill route to breathing the deep cave lake | T3 |
| `glowshell_helm` (head) | anvil | `iron_bar` ×2, `glass` ×2, `water_beetle_shell` ×2, `glow_gland` ×2 | buy@fisher (gated: own `bubble_rebreather`) | **`water_breath` (sustained)** + **built-in `light_radius +3`** (glow-lit, hands-free) + `defense +2` — breathe *and* see in the deep dark | T4 |
| `current_waders` (legs/feet) | workbench | `tanned_hide` ×4 *(reuse)*, `crayfish_shell` ×3, `pale_root` ×3 | buy@fisher | **`water_walk` (deep, sustained)** + `terrain_immunity` (not swept by the **cold current**) + `fall_resist +1` (the slick falls) + `defense +1` | T3 |
| `cave_lantern` *(placeable/held light)* | workbench | `glass` ×2, `glow_spore` ×2, `flowstone` ×1 | craft | sustained **`light_radius`** held/placed light for the near-black cave (the baseline murk-killer) | T3 |
| `glow_oil` *(lantern fuel/consumable)* | cauldron | `glow_spore` ×3, `cave_water` ×1 | auto | refills a lantern + a thrown **`light_radius`** flare for the dark; the cave-survival staple | T3 |
| `pearl_diver_charm` (accessory) | jeweler | `cave_pearl` ×1 *(gem-minor)*, `lotus_essence` ×1 *(reuse)*, `silver_bar` ×1 | find / buy@fisher | extends `water_breath` reserve + `hazard_resist +1` (cold) — the **pearl accessory** & dive-deeper trinket | T4 |

### Cave-water alchemy (cauldron — cold/clarity/light brews)

| Output (id) | Station | Inputs | Unlock | Effect (timed unless noted) | Tier |
|---|---|---|---|---|---|
| `cave_breathing_potion` | cauldron | `beetle_air_sac` ×2, `cave_water` ×2, `deepwater_kelp` ×3 *(reuse)* | buy@fisher | timed **sustained `water_breath`** — the consumable route before the rebreather/helm | T3 |
| `cold_current_tonic` *(aquatic potion)* | cauldron | `cave_water` ×3, `cave_salt` ×1, `pale_root` ×2 | buy@fisher | timed `water_retention_pct +15` + `hazard_resist` (cold) + steadies you in the current (`move_speed_pct` on water) — the **deep-water-survival potion** | T3 |
| `nightglow_draught` | cauldron | `glow_gland` ×2, `cave_water` ×1, `mushroom_glow` ×2 | auto | timed **`night_vision`** + small `light_radius` — see in the murk before you've built a lantern | T3 |
| `anglers_brew` | cauldron | `aquatic_grub` ×3, `glow_spore` ×1, `cave_salt` ×1 | find | timed `catch_cap` + `rare_bug_luck` on the fishing loop — the lucky-catch potion | T3 |
| `pearl_clarity_elixir` *(rare)* | cauldron | `cave_pearl` ×1, `blind_fish_scale` ×2, `lotus_essence` ×1 *(reuse)* | find (rare) | timed `gem_luck` + `dodge_chance +6` + `night_vision` — the cave-treasure-hunter brew | T4 |

### Cave-water cloth, jewelry & building crafts

| Output (id) | Station | Inputs | Unlock | Bonus / use | Tier |
|---|---|---|---|---|---|
| `pale_line` (cordage/cloth substitute) | loom | `pale_root` ×4 | auto | the cave fiber → angler-line, nets & light weaves (substitutes `fiber`/`thread` for water gear) | T3 |
| `nacre_inlay` *(jewelry/décor mat)* | jeweler | `freshwater_nacre` ×2, `larva_case` ×2 *(grit polish)* | auto | mother-of-pearl inlay for charms & luxury décor; a pearlescent finish | T3 |
| `pearl_pendant` *(accessory)* | jeweler | `cave_pearl` ×2 *(gem-minor)*, `silver_bar` ×1, `nacre_inlay` ×1 | buy@fisher | `luck +1` + `gem_luck +1` + small `water_breath` reserve — the signature **pearl accessory** | T4 |
| `glowscale_lens` *(accessory)* | jeweler | `blind_fish_scale` ×2, `cave_quartz` ×1 *(reuse → crystal lens)*, `glow_gland` ×1 | find / jeweler | `night_vision` + `catch_radius +1` + small `light_radius` — see & catch in the black | T3 |
| `silt_block` (building mat) | furnace | `river_silt` ×2, `coal` ×1 *(fuel)* | auto | pale waterproof brick — fisher's-platform & sunken-ruin construction | T3 |
| `flowstone_block` (building mat) | stonecutter | `flowstone` ×2 | auto | banded calcite building stone & décor (premium cave wall/path) | T3 |
| `fishers_platform` (placeable floor) | sawmill | `plank` ×3, `flowstone_block` ×1, `iron_bar` ×1 | buy@fisher | a walkable **platform over the underground river** — build out the fishing decks (the deep-build toy) | T3 |
| `cave_river_dye` (set: pearl-white / glow-blue / flowstone-amber) | dye_vat | `freshwater_nacre` / `glow_spore` / `cave_water` | auto | the underground-river palette for the angler outfit & trophy décor | T3 |

### Cooking — cave-fish & forage (cooking_pot; timed buffs)

| Output (id) | Station | Inputs | Unlock | Buff | Tier |
|---|---|---|---|---|---|
| `grilled_cavefish` | cooking_pot | `fish_fillet` 2 + `cave_salt` 1 + `cave_moss` 1 *(reuse)* | craft | `max_hp` + `hp_regen` (hearty) | T3 |
| `crayfish_boil` | cooking_pot | `crayfish_claw` 2 + `cave_salt` 1 | craft | `defense +1` (short, shell-armor) | T3 |
| `cured_fillet` *(preserve)* | cooking_pot | `fish_fillet` 2 + `cave_salt` 2 | craft | long-shelf travel food — `hp_regen` (long) | T3 |
| `glowcap_chowder` | cooking_pot | `fish_fillet` 1 + `mushroom_glow` 2 + `cave_water` 1 | craft | `night_vision` (short — eat to see) | T3 |

---

## 4. Signature BONUS gear — the **Cave-Diver / Angler set** (T3→T4)

The zone's identity outfit: a **cave-diver / angler** rig that lets you light, breathe, and *fish* the
underground river — and turn around to fight the cave crab that guards its treasure. Moderate-to-high
`defense`, with the cave-water verbs (**`water_breath` / `water_walk`**), **`light_radius`** (the dark is the
real wall here), and the **fishing/catch** stats (`catch_cap`, `rare_bug_luck`) as the headline — plus
`dodge_chance` to slip the crab's ambush in the current. Built from the cave-water drops & gatherables —
`water_beetle_shell`, `crayfish_shell`/`crayfish_claw`, `albino_chitin`, `cave_pearl`, `glow_gland`,
`tanned_hide`, `iron_bar`/`steel_bar`. Three core pieces (+ optional gloves), paper-doll overlay reads as
"glow-lit diver-angler in a shell-plated rig."

`bonuses{}` schema per `../stats_and_bonuses.md §1` (additive; `_pct` are percent; `set` ties the set bonus).

| Piece (id) | Slot | Made @ | Inputs | Per-piece bonuses | Tier |
|---|---|---|---|---|---|
| `angler_hood` | head | anvil | `iron_bar` ×1, `water_beetle_shell` ×1, `albino_chitin` ×1 *(pale lens)*, `glow_gland` ×1 | `defense +2`, `light_radius +2`, `night_vision +1`, `rare_bug_luck +1` | T3 |
| `divers_carapace` | body | anvil | `steel_bar` ×2, `cave_crab_carapace` ×1, `water_beetle_shell` ×2, `kelp_weave` ×2 *(reuse)* | `defense +4`, **`water_breath` (sustained)**, `water_retention_pct +15`, `hazard_resist +1` (cold) | T4 |
| `current_leggings` | legs/feet | workbench | `tanned_hide` ×4 *(reuse)*, `crayfish_shell` ×3, `albino_chitin` ×1, `pale_root` ×3 | `defense +2`, **`water_walk` (deep, sustained)** + `terrain_immunity` (current), `fall_resist +1`, `move_speed_pct +5` on water | T3–T4 |
| `angler_gloves` *(optional 4th)* | hands | anvil | `iron_bar` ×1, `crayfish_claw` ×2, `albino_chitin` ×1 | `defense +1`, `catch_cap +6`, `catch_radius +1`, crab/latch-pry speed | T3 |

**Unlock:** `current_leggings` & `divers_carapace` recipes `buy@fisher` (carapace gated on owning the
`bubble_rebreather`/`glowshell_helm` **and/or** the apex `cave_crab` slain — it leans on
`cave_crab_carapace`); `angler_hood` `buy@fisher`; the gloves `find` (rare sunken-ruin scroll).

### Set bonus — "Cave-Diver" (escalating)

- **2-piece:** `water_breath` & `water_walk` both **sustained** (no flicker) + `light_radius +2` — you can
  live in the lit deep water indefinitely, no swept-by-current.
- **3-piece (full):** add **`night_vision`** + `light_radius +2` (you carry your own daylight), `defense +3`,
  `hazard_resist +2` (cold/current), and **`catch_cap +8` / `rare_bug_luck +2`** — the full cave-angler rig:
  the river's fish & rare aquatic bugs come up generously, and the dark stops being a wall.
- **4-piece (with gloves):** the cave crab **can't ambush-stun** you (its lunge from the flooded alcove is
  telegraphed/negated) + `dodge_chance +6` + `catch_cap +6` — built to *fish the treasure pool and beat its
  guard*, not flee it.

Design intent: where the swamp sets *unwall the open water*, the Cave-Diver / Angler set lets you **own the
underground river in the dark** — light it, breathe it, walk its current, and reap it (fish, pearls, rare
aquatic bugs) — then turn and fight the cave crab guarding the sunken-ruins treasure. Defense is genuinely
T4-grade (best-in-slot for this zone), but it's **specialized**: aquatic + light + catch. Swap to a land
plate set for a dry fight (GDD: one outfit at a time = the build choice). The carapace leans on the apex
`cave_crab_carapace`, so the set is the **reward loop for beating the treasure-guard**, not just for crafting.

### Signature accessories (jeweler / drops)

| Accessory (id) | Source | Bonus |
|---|---|---|
| `pearl_pendant` *(see §3)* | jeweler (`cave_pearl` ×2 + `silver_bar` + `nacre_inlay`) | `luck +1` + `gem_luck +1` + small `water_breath` reserve — the signature pearl accessory |
| `glowscale_lens` *(see §3)* | jeweler (`blind_fish_scale` + `cave_quartz` + `glow_gland`) | `night_vision` + `catch_radius +1` + small `light_radius` |
| `crayfish_charm` | jeweler / drop (`crayfish_claw` ×2 + gem-minor) | `defense +1` + `thorns` vs water bugs — the pincer-guard trinket |
| `glow_charm` | find / jeweler (`glow_gland` ×2 + `freshwater_nacre`) | `light_radius +2` + tiny `move_speed_pct` — the living-lantern trinket |
| `crabshell_pauldron` | drop/quest (`cave_crab_carapace`-line) | `defense +2` + `knockback +1` — the apex-bug combat charm/trophy |

---

## 5. Shop / NPC — **"Marlow," the Sunken-Ruins Fisher** (+ treasure)

A weathered **cave fisher** stationed on a `fishers_platform` at the edge of the underground lake, beside a
half-drowned **sunken ruin** (occupant w/ `interaction_type:"npc"`, `npc{role:"cave_fisher"}`). Half angler
(tackle, fishing & dive gear), half **treasure-hunter** (pearls, cave gems, the ruin's recovered relics &
rare recipes). Stock **grows with progress** (Lens of Pacing): the deepest gear (`glowshell_helm`,
`divers_carapace`, the apex weapon) only stocks once you own the `bubble_rebreather` / have slain the
treasure-guard `cave_crab`.

### Sells — goods (light & tackle first)

| Item | Rough cost | Notes |
|---|---|---|
| `cave_lantern` / `glow_oil` | low–mid | **the survival staple** — you're blind & ambush-bait in the dark without light; on hand from day one |
| `cave_rod` / `glow_lure` | low–mid | gates the cave-fishing loop; the glowing lure the blind fish strike |
| `cave_breathing_potion` | mid | the consumable deep-`water_breath` route (before the rebreather) |
| `cold_current_tonic` / `nightglow_draught` | mid | survive the cold current & see in the murk (cave-survival basics) |
| `cave_water`, `glow_spore`, `lure_resin` | low–mid | alchemy/tackle reagents (skip the gather) |
| `bait` *(from `aquatic_grub`)* | low | for the rod / `cave_fish_trap` |
| `fishers_platform` / cave-river décor | mid | build out the fishing decks; a buy-only glow-pool / flowstone décor |

### Sells — treasure & recipes (the coin sink + the reward)

Recipes: `cave_rod` · `glow_lure` · `cave_harpoon` · `cave_fish_trap` · `bubble_rebreather` ·
`glowshell_helm` · `current_waders` · `pearl_diver_charm` · `cave_breathing_potion` · `cold_current_tonic` ·
`anglers_brew` · `pearl_pendant` · `fishers_platform` · `angler_hood` · `current_leggings` ·
`divers_carapace`. (Gated: the deepest recipes — `glowshell_helm`, `divers_carapace`, the apex
`crab_claw` weapon — only stock once you own the `bubble_rebreather` and/or have slain the `cave_crab`.)

**Treasure (the ruin's recovered relics):** a rotating small stock of **`cave_pearl`** & a buy-only luxury
**`pearl_pendant`** / pearl décor; the rare-recipe scrolls (`pearl_clarity_elixir`, the `angler_gloves`) turn
up here as recovered ruin finds — a reason to keep coming back to the platform.

### Buys — coin sources

Pays **high** for the cave-water drops & dive-gatherables (a reason to fish & dive the dark river):
`cave_pearl`, `crayfish_claw`, `water_beetle_shell`, `albino_chitin`, `blind_fish_scale`, `glow_gland`,
`cave_crab_carapace`/`crab_claw`, `freshwater_nacre`, `cold_iron_ore`, and caught **cave fish**. The apex
crab & the pale albino rarities pay the most — the bounty for clearing the treasure pool.

### Flavor / tips

Intro hook: warns you the dark itself is the killer here (no light = blind & ambushed), that the **cold
current** will sweep you off the falls and the **deep lake drowns** the unprepared, and that something big —
the pale **cave crab** — guards the sunken-ruins treasure pool. Points you at a `cave_lantern` and the
`cave_rod` first. Random tips seed the glow-lure trick (the blind fish strike light), the dive-only pearls,
and the treasure-guard hunt.

---

## 6. "New toys" hook

The Underground River takes the swamp's **water survival** and drops it **into the pitch dark**: your snorkel
isn't enough when you also can't *see*, and the river itself **moves** — a cold current that sweeps you off
the waterfall ledge. So the toy is a new **light-and-current survival layer** (a `cave_lantern`, `glow_oil`,
the `nightglow_draught`, the `cold_current_tonic`) stacked on top of breathing and walking the deep water. It
debuts a full **cave-fishing loop** in the dark — a real `cave_rod`, a **glowing lure the blind fish strike**,
the `cave_harpoon`, the passive `cave_fish_trap`, and the diving `dive_net` — that finally rewards *fishing*
the water you learned to cross, with **cave fish** as a brand-new catch class (rod, not net). It opens a
**dive-and-prise** treasure layer: freshwater **`cave_pearl`s**, mother-of-pearl `nacre_inlay`, cave gems
(`cave_quartz` reuse), and the **glowing aquatic life** (`glow_mayfly`, `glow_spore`) that lights the murk
and feeds a luminous jewelry/dye line. And it crowns the zone with the **Sunken-Ruins Fisher** and a guarded
**treasure pool** — the pale apex **cave crab** whose carapace builds the **Cave-Diver / Angler set**, the
glow-lit diving-angler outfit that lets you *own* the underground river: light it, breathe it, walk its
current, fish its pearls, and beat the guard instead of fearing the dark.

---

## New-id summary

```
materials:
  cave_pearl, freshwater_nacre, cave_water, glow_spore, river_silt, flowstone,
  cave_salt, cold_iron_ore, lure_resin, pale_root,
  silt_block, flowstone_block, pale_line, nacre_inlay, cave_river_dye
  # reuse from swamp/water lineage: tanned_hide, reed_fiber, deepwater_kelp, kelp_weave,
  #   lotus_essence, bog_pearl, cave_quartz, leech_extract
  # reuse cave flora: mushroom_glow, cave_moss ; reuse metals: iron_bar, steel_bar, silver_bar,
  #   coal, glass, plank, silk

species: (id -> primary drop)
  cave_crayfish    -> crayfish_claw          # secondary: crayfish_shell
  water_beetle     -> water_beetle_shell     # secondary: beetle_air_sac
  aquatic_larva    -> larva_case             # secondary: aquatic_grub  (prime fishing bait)
  albino_isopod    -> albino_chitin          # secondary: cave_detritus
  glow_mayfly      -> glow_gland             # secondary: mayfly_wing
  blind_cave_fish  -> blind_fish_scale       # FISH (rod/spear/trap, not net); secondary: fish_fillet
  cave_crab        -> cave_crab_carapace     # APEX T4 treasure-guard; secondary: crab_claw
  # new reagent/drop ids: crayfish_claw, crayfish_shell, water_beetle_shell, beetle_air_sac,
  #   larva_case, aquatic_grub, albino_chitin, cave_detritus, glow_gland, mayfly_wing,
  #   blind_fish_scale, fish_fillet, cave_crab_carapace, crab_claw
  # carcass drops: dead_crayfish, dead_isopod, dead_larva, dead_mayfly, dead_fish, dead_crab
  #   (dead_beetle reuses existing id)

items:
  # cave fishing & tackle
  cave_rod              # workbench — cave-fishing rod (T3)
  glow_lure             # workbench — glowing lure, blind fish strike (T3)
  cave_harpoon          # anvil — spear-fishing tool / light weapon (T3)
  cave_fish_trap        # workbench — passive cave fish-trap (T3)
  dive_net              # loom — underwater catch-net, needs water_breath (T3)
  bed_dredge            # anvil — dredge pearls/silt/ore from the bed (T3)
  # deep cave-water survival (water_breath / water_walk / light)
  bubble_rebreather     # workbench — sustained water_breath (beetle-gill) (T3)
  glowshell_helm        # anvil — sustained water_breath + built-in light_radius + defense (T4)
  current_waders        # legs/feet — deep water_walk + current immunity + fall_resist (T3)
  cave_lantern          # workbench — held/placed light_radius (T3)
  glow_oil              # cauldron — lantern refill + thrown light flare (T3)
  pearl_diver_charm     # accessory — extend water_breath + hazard_resist cold (T4)
  # cave-water alchemy
  cave_breathing_potion # cauldron — timed sustained water_breath (T3)
  cold_current_tonic    # cauldron — water_retention + cold hazard_resist + current steady (T3)
  nightglow_draught     # cauldron — night_vision + light_radius (T3)
  anglers_brew          # cauldron — catch_cap + rare_bug_luck (T3)
  pearl_clarity_elixir  # cauldron — gem_luck + dodge + night_vision (rare T4)
  # cloth, jewelry & building
  pale_line             # loom — cave cordage/cloth substitute (T3)
  nacre_inlay           # jeweler — mother-of-pearl inlay mat (T3)
  pearl_pendant         # jeweler — luck + gem_luck + water_breath (PEARL ACCESSORY) (T4)
  glowscale_lens        # jeweler — night_vision + catch_radius + light_radius (T3)
  silt_block            # furnace — pale waterproof brick (T3)
  flowstone_block       # stonecutter — banded calcite building stone (T3)
  fishers_platform      # sawmill — walkable platform over the river (T3)
  cave_river_dye        # dye_vat — pearl-white / glow-blue / flowstone-amber palette (T3)
  # cooking
  grilled_cavefish      # cooking_pot — max_hp + hp_regen (T3)
  crayfish_boil         # cooking_pot — defense (T3)
  cured_fillet          # cooking_pot — long hp_regen preserve (T3)
  glowcap_chowder       # cooking_pot — night_vision (T3)
  # Cave-Diver / Angler set
  angler_hood           # head armor — set "cavediver", light + rare_bug_luck (T3)
  divers_carapace       # body armor — set "cavediver", water_breath + cold resist (T4)
  current_leggings      # legs/feet armor — set "cavediver", deep water_walk + current (T3-4)
  angler_gloves         # hands armor — set "cavediver", catch_cap + catch_radius (T3)
  # signature accessories
  crayfish_charm        # accessory — defense + thorns vs water bugs
  glow_charm            # accessory — light_radius + move_speed
  crabshell_pauldron    # accessory — defense + knockback (apex trophy)
  # set id: cavediver (2/3/4-piece bonuses)
```
```
