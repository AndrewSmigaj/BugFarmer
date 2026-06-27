# Consumables Catalog — Potions & Meals

> **Scope:** every craftable **consumable** in the BugFarmer economy, split into the game's two consumable
> stations: **Potions** (the `cauldron` — alchemy: cures, buffs, coatings, bombs, salves, tonics) and
> **Meals** (the `cooking_pot` — cooked food that grants **timed buffs**). Generous by design — **we prune
> later, never thin.**
>
> **Sources:** indexed from every zone content sheet under [`../zones/`](../zones/) (section A below), then
> filled to quota with cross-cutting staples that cover the stat vocabulary (section B). Station roster + cost
> model: [`../crafting.md`](../crafting.md). Stat vocab + `bonuses{}`/effect schema:
> [`../stats_and_bonuses.md`](../stats_and_bonuses.md). Pacing/gating: [`../progression.md`](../progression.md).
>
> **GDD note — NO hunger/stamina system.** Meals are **short timed BUFFS**, not nourishment. You never *need*
> to eat; you eat to gain a temporary edge (a farming session, a fight, a dive). Cures and bombs sit in
> Potions even when "food-flavored"; anything cooked at the `cooking_pot` for a timed stat buff is a Meal.
>
> **Two-tier reagents recur:** most zones pair a **cheap, always-craftable survival answer** (an antidote /
> salve / light brew off common gatherables) with a **spicy gated item** (a bomb / coating / apex tonic off a
> boss or rare drop). Cures (`cures` column) clear a debuff; buffs grant a timed stat; coatings buff your
> equipped weapon for a window; bombs/thrown are AoE; salves are heal-over-time + a short resist.

---

## A. Potions (station = `cauldron`)

Alchemy consumables — **cures, timed buffs, weapon coatings, thrown bombs, salves, oils, tonics**. `id` ·
`station` · `ingredients` · `effect` (timed unless a cure) · `tier` · `source-zone`.

### A.1 — Indexed from the zones

| id | station | ingredients | effect (timed unless cure) | tier | source-zone |
|---|---|---|---|---|---|
| `petal_tincture` | cooking_pot→cauldron* | flower 3 + chamomile 1 | short `calm_radius` self-buff (cheap intro potion) | T1 | village |
| `calm_spray` | cauldron / buy@general | nectar_bloom 2 + lavender 1 *(or chamomile 2 + lavender 1 + honeydew 1)* | `calm_radius` pulse — bees/wasps stop attacking (the catch-teaching staple) | T1 | bee_meadow / village |
| `pollination_dust` | cauldron | pollen 4 + chamomile 1 | throwable — temporary `+pollination` over a crop area (faster bloom/yield) | T2 | bee_meadow |
| `propolis_salve` | cauldron | propolis 2 + honey 1 + yarrow 1 | heal-over-time (`hp_regen`); the zone's first regen item | T2 | bee_meadow |
| `royal_tonic` | cauldron / find | royal_jelly 1 + honey 2 | large `max_hp` + `hp_regen` buff (premium) | T2 | bee_meadow |
| `nightsight_tonic` | cauldron | luna_dust 1 + glow_bloom 2 + mint 1 | timed `night_vision +2` | T2 | butterfly_fields |
| `luck_draught` | cauldron | butterfly_scale 2 + nectar 1 + chamomile 1 | short `rare_bug_luck +1`, `luck +1` ("lucky sighting") | T2 | butterfly_fields |
| `calm_incense` | cauldron (placed) | lavender 2 + luna_dust 1 + sage 1 | area `calm_radius` (bugs hold still — clean catches) | T2 | butterfly_fields |
| `antidote` | cauldron / buy@thicket_vendor | nettle_leaf 2 + wasp_paper 1 + mushroom_brown 1 | **cures `poisoned`** + short `hazard_resist` | T2 | wasp_thicket |
| `venom_coat` | cauldron | venom_sac 1 + resin_glob 1 + nettle_leaf 2 *(forest: forest_centipede_fang 1 + tree_resin 1 + defensive_toxin 1)* | weapon coating — adds `poisoned` on-hit for a duration | T2 / T4 | wasp_thicket / millipede_forest |
| `poison_vial` | cauldron / find | nettle_leaf 3 + venom_sac 1 + resin_glob 1 | thrown — AoE `poisoned` cloud (vs swarms / matriarch adds) | T2 | wasp_thicket |
| `nettle_salve` | cauldron | nettle_leaf 2 + yarrow 1 + wasp_paper 1 | short `hp_regen +1` + `thorns +1` (pre-fight prep) | T2 | wasp_thicket |
| `antivenom` | cauldron / buy@apiarist · buy@miners_camp | hornet_venom 1 + nettle_leaf 2 + propolis 1 *(rocks: aloe_leaf 2 + rock_salt 1 + scorpion_venom 1)* | **cures `poisoned`/`envenomed`** + strong `hazard_resist`/`sting_immunity` | T3 | meadow / scorpion_rocks |
| `venom_bomb` | cauldron / find | hornet_venom 1 + resin_glob 1 + glass 1 | thrown — AoE `poisoned` cloud (vs hornet swarm / nest) | T3 | meadow |
| `water_breathing_potion` | cauldron / buy@swamp vendor | leech_extract 2 + lily_extract 1 + pondweed 3 | timed `water_breath` (consumable route before the helm) | T2 | shallow_swamp |
| `anticoagulant_salve` | cauldron | leech_extract 3 + yarrow 2 + lily_extract 1 | `hp_regen` + leech-latch immunity window | T2–T3 | shallow_swamp |
| `marsh_antidote` | cauldron / buy@swamp vendor | lily_extract 2 + sage 2 + mint 1 | **cures swamp poison** / `hazard_resist` burst | T2 | shallow_swamp |
| `gas_bomb` | cauldron / find/buy | swamp_gas 2 + clay 1 + mosquito_proboscis 2 | thrown AoE — bug `calm`/repel cloud (utility) | T3 | shallow_swamp |
| `nimble_brew` | cauldron / find (rare) | frog_spawn 1 + skater_oil 2 + mint 1 | timed `dodge_chance` + `move_speed_pct` | T3 | shallow_swamp |
| `bog_lantern_oil` | cauldron | swamp_gas 3 + peat 2 | refills a lantern — `light_radius` source | T2 | shallow_swamp |
| `fever_cure` | cauldron / buy@hermit | lotus_essence 1 + waterbug_venom_gland 1 + sage 2 + deepwater_kelp 2 | **clears all `swamp_fever`/disease stacks** + disease-immunity window + small `hp_regen` | T3 | deep_swamp |
| `deep_antitoxin` | cauldron / buy@hermit | miasma_essence 2 + lotus_essence 1 + frog_toxin 1 + mint 1 | **cures venom/poison** + strong `hazard_resist` burst | T3 | deep_swamp |
| `deep_breathing_potion` | cauldron / buy@hermit | leech_extract 2 + lotus_essence 1 + deepwater_kelp 3 | timed **sustained** `water_breath` | T3 | deep_swamp |
| `venom_coating` | cauldron / find | waterbug_venom_gland 1 + frog_toxin 2 + mosquito_venom 3 | weapon coating — `venom` DoT on-hit (strong) for a window | T4 | deep_swamp |
| `fever_bomb` | cauldron / find/buy@hermit | miasma_essence 2 + mosquito_venom 3 + clay 1 | thrown AoE — `swamp_fever`/poison cloud (disease as a weapon) | T4 | deep_swamp |
| `glowcap_oil` | cauldron | serpent_glow_cap 3 + peat 2 | refills a deep-lantern — sustained `light_radius` | T3 | deep_swamp |
| `serpent_elixir` | cauldron / find (rare) | serpentfly_ichor 1 + lotus_essence 1 + bog_pearl 1 | timed `night_vision` + `dodge_chance +8` + `move_speed_pct` (elite trophy brew) | T4 | deep_swamp |
| `venom_oil` | cauldron | scorpion_venom 1 + resin_glob 1 + aloe_leaf 1 *(cavern: centipede_venom_gland 1 + resin_glob 1 + cave_moss 1)* | weapon coating — strong `envenomed` on-hit for a duration | T3 | scorpion_rocks / centipede_cavern |
| `heat_salve` | cauldron | aloe_leaf 2 + dust_lichen 1 + yarrow 1 | short `hazard_resist +2` (heat) + `hp_regen +1` | T3 | scorpion_rocks |
| `tick_repellent` | cauldron | rock_salt 2 + dust_lichen 1 + tick_sac 1 | short aura — `desert_tick` won't latch | T3 | scorpion_rocks |
| `woodland_tonic` | cauldron / buy@ranger_station | mushroom_bracket 2 + mushroom_morel 1 + bark_strip 1 | sustained `hp_regen +2` + `max_hp +6` + `night_vision +1` (signature forest brew) | T4 | millipede_forest |
| `bark_salve` | cauldron | bark_strip 2 + forest_moss 1 + mushroom_bracket 1 | short `defense +2` + heals chip damage | T4 | millipede_forest |
| `antitoxin` | cauldron / buy@ranger_station | forest_moss 2 + defensive_toxin 1 + mushroom_bracket 1 | **cures `poisoned`/`noxious`** + short `hazard_resist` | T4 | millipede_forest |
| `thorns_draught` | cauldron / find | forest_centipede_fang 1 + defensive_toxin 1 + mushroom_morel 1 | timed `thorns +3` + `defense +1` | T4 | millipede_forest |
| `swarm_lure` | cauldron / buy@farmhouse | swarm_essence 2 + blighted_grain 2 | draws a swarm to a marked spot (kill/harvest box) | T4 | locust_farmland |
| `swarm_repellent` | cauldron / buy@farmhouse | locust_oil 1 + silk_resin 1 + lavender 2 | timed aura — swarm bugs avoid you / lower density near you | T4 | locust_farmland |
| `blight_antidote` | cauldron | yarrow 2 + locust_oil 1 + blighted_grain 1 | **cures the field-blight/poison DoT** swarms inflict | T4 | locust_farmland |
| `paralytic_coating` | cauldron | centipede_venom 1 + cobweb 1 + gorse_thorn 1 | weapon coating — on-hit slow/`webbed`-lite (paralytic) for a window | T4 | spider_vale_west |
| `spider_antivenom` | cauldron / buy@hunters_lodge | gorse_thorn 2 + cave_moss 1 + spider_venom 1 | **cures `envenomed`** + short `hazard_resist` | T4 | spider_vale_west |
| `gossamer_tonic` | cauldron | gossamer_dew 2 + cave_moss 1 + mint 1 | timed `dodge_chance +3` + `move_speed_pct +4` (agility brew) | T4 | spider_vale_west |
| `venom_draught` | cauldron | widow_venom 1 + resin_glob 1 + cave_nettle 1 | weapon coating — heavy `envenomed` on-hit for a window (widow-tier) | T5 | spider_vale_east |
| `widow_antivenom` | cauldron / buy@scavenger_camp | cave_nettle 2 + widow_venom 1 + gloom_moss 1 | **clears all heavy `envenomed` stacks** + venom-immunity window + small `hp_regen` | T5 | spider_vale_east |
| `gloom_tonic` | cauldron | gloom_moss 2 + cave_nettle 1 + sage 1 | sustained `night_vision +1` + `light_radius +2` | T5 | spider_vale_east |
| `widow_bomb` | cauldron / find (rare) | widow_venom 2 + tarantula_hair 1 + clay 1 | thrown AoE — heavy `envenomed` + `defense`-shred cloud | T5 | spider_vale_east |
| `formic_etch` | cauldron / buy@myrmecologist | formic_acid 1 + chalk_stone 1 | utility reagent — etch/cutting agent (gem-cut/fine brick) + strong cleaner | T2 | ant_colony |
| `acid_flask` | cauldron / find / craft | formic_acid 2 + glass 1 + fungal_spore 1 | thrown — AoE `acid_burn` (armor-chip DoT) on the soldier swarms | T2–T3 | ant_colony |
| `formic_salve` | cauldron | formic_dab 2 + cave_moss 1 + yarrow 1 | short `hazard_resist +2` (acid) + `hp_regen +1` (cures/resists `acid_burn`) | T2 | ant_colony |
| `pheromone_whistle` | cauldron / buy@myrmecologist | royal_pheromone 1 + formic_dab 2 + honeydew 1 | short aura — ants calm & follow (`calm_radius` + friendly `lure_radius`) | T3 | ant_colony |
| `inferno_coating` | cauldron | fire_ant_gland 1 + ember_resin 1 + resin_glob 1 | weapon coating — strong `scorched` on-hit for a window (fire-tier) | T4 | deadly_ants |
| `swarm_repeller` | cauldron / buy@exterminators_base | formic_acid 2 + acid_crystal 1 + army_ant_mandible 1 + ember_resin 1 | thrown smoke-and-acid — `army_ant` columns scatter/bivouac for a window | T4 | deadly_ants |
| `acid_balm` | cauldron / buy@exterminators_base | aloe_leaf 2 + acid_crystal 1 + royal_jelly 1 | **cures `corroded` + `envenomed`** + short `hazard_resist` (acid/venom) | T4–T5 | deadly_ants |
| `deep_delver_brew` | cauldron / buy@hermit | mushroom_glow 2 + glowworm_lumen 1 + cave_moss 1 + cave_nitre 1 | sustained `night_vision +2` + `hazard_resist +2` (cave-damp) + `hp_regen +1` + faint `light_radius +1` | T3 | centipede_cavern |
| `cave_antivenom` | cauldron / buy@hermit | cave_moss 2 + cave_nitre 1 + centipede_venom_gland 1 | **cures `envenomed`** + short `hazard_resist` | T3 | centipede_cavern |
| `damp_salve` | cauldron | cave_moss 2 + mushroom_glow 1 + bat_guano 1 | short `defense +2` + heals chip + `hazard_resist` (cave-rot/spore) tick | T3 | centipede_cavern |
| `spider_antidote` | cauldron / buy@miners_outpost | glowshroom 1 + spider_venom 1 + cave_moss 1 | **cures `venomed`** (cave spider) + short `hazard_resist` | T3 | underground_passages |
| `cave_breathing_potion` | cauldron / buy@fisher | beetle_air_sac 2 + cave_water 2 + deepwater_kelp 3 | timed **sustained** `water_breath` (before rebreather/helm) | T3 | underground_river |
| `cold_current_tonic` | cauldron / buy@fisher | cave_water 3 + cave_salt 1 + pale_root 2 | timed `water_retention_pct +15` + `hazard_resist` (cold) + `move_speed_pct` on water | T3 | underground_river |
| `nightglow_draught` | cauldron | glow_gland 2 + cave_water 1 + mushroom_glow 2 | timed `night_vision` + small `light_radius` | T3 | underground_river |
| `anglers_brew` | cauldron / find | aquatic_grub 3 + glow_spore 1 + cave_salt 1 | timed `catch_cap` + `rare_bug_luck` on the fishing loop | T3 | underground_river |
| `pearl_clarity_elixir` | cauldron / find (rare) | cave_pearl 1 + blind_fish_scale 2 + lotus_essence 1 | timed `gem_luck` + `dodge_chance +6` + `night_vision` (treasure-hunter brew) | T4 | underground_river |
| `glow_oil` | cauldron | glow_spore 3 + cave_water 1 | refills a lantern + thrown `light_radius` flare | T3 | underground_river |

\* `petal_tincture` is authored at the village's `cooking_pot` as a "calm-lite drink" — but it is an alchemy
*potion* (a `calm_radius` self-buff, not a stat-buff meal), so it lives here. The two early calm items
(`petal_tincture`, `calm_spray`) are the T1 entry to the potion line before the cauldron is built.

### A.2 — Cross-cutting staple potions (fill to quota; cover the stat vocab)

Generic, always-craftable potions that round out the stat coverage the zone list is thin on — `health/hp`,
`max_hp`, `move_speed`, `defense`, `crit`, `mining_speed`, `light/night_vision`, `hazard_resist`, `luck`,
`water_breath`, `calm`, `ore_fortune`. Cheap, common reagents; sit at the tier where their ingredients land.

| id | station | ingredients | effect (timed unless cure) | tier | source-zone |
|---|---|---|---|---|---|
| `healing_draught` | cauldron | yarrow 2 + honey 1 | restores HP + short `hp_regen` (the basic heal potion) | T1 | staple |
| `regen_tonic` | cauldron | yarrow 2 + propolis 1 + mint 1 | sustained `hp_regen` over a longer window | T2 | staple |
| `vigor_elixir` | cauldron | royal_jelly 1 + carrot 2 + honey 1 | timed `max_hp` boost (bigger health pool for a fight) | T2 | staple |
| `swift_tonic` | cauldron | mint 2 + clover 1 | timed `move_speed_pct` (the basic mobility brew) | T1 | staple |
| `ironhide_brew` | cauldron | chitin 2 + clay 1 + sage 1 | timed `defense` buff (the basic armor brew) | T2 | staple |
| `keen_eye_draught` | cauldron | quartz 1 + nettle_leaf 1 + mint 1 | timed `crit_chance` buff (pre-fight precision) | T3 | staple |
| `miners_brew` | cauldron | coal 1 + aloe_leaf 1 + rock_salt 1 | timed `mining_speed_pct` (work a vein faster) | T3 | staple |
| `fortune_tonic` | cauldron | gem_geode 1 + quartz 1 + honey 1 | timed `ore_fortune` + `gem_luck` (mine-a-vein luck brew) | T3 | staple |
| `torchlight_brew` | cauldron | mushroom_glow 2 + cave_moss 1 | timed `light_radius` + `night_vision` (cheap cave-light drink) | T2 | staple |
| `lucky_draught` | cauldron | ladybug_shell 1 + clover 2 + honey 1 | timed `luck` + `rare_bug_luck` (the "lucky day" brew) | T1 | staple |
| `warding_tonic` | cauldron | sage 2 + aloe_leaf 1 + cave_moss 1 | timed broad `hazard_resist` (heat/cold/spore generic) | T2 | staple |
| `still_mind_incense` | cauldron (placed) | lavender 2 + chamomile 1 | area `calm_radius` — bugs hold still (cheap clean-catch aid) | T1 | staple |
| `breath_tonic` | cauldron | reed_fiber 2 + lily_extract 1 + mint 1 | timed `water_breath` (cheap swamp/cave breathing route) | T2 | staple |
| `firewalk_salve` | cauldron | aloe_leaf 2 + ember_resin 1 + cave_water 1 | short `hazard_resist +2` (fire) + heals burn chip | T4 | staple |
| `cleansing_tonic` | cauldron | sage 2 + yarrow 1 + mint 1 | **cures generic poison/debuff** + small `hp_regen` (the cheap all-purpose cure) | T2 | staple |
| `oil_of_edges` | cauldron | resin_glob 1 + venom_sac 1 + sage 1 | weapon coating — generic `poisoned` on-hit (any-zone fallback coating) | T2 | staple |
| `smoke_bomb` | cauldron | swamp_gas 1 + clay 1 + lavender 1 | thrown — AoE `calm`/repel + brief vision break (escape/pacify) | T2 | staple |

> **Smoke note:** `smoke_pouch` (wasp_thicket, buy-only thrown `calm_radius` AoE) is sold pre-made by the
> Thicket Trapper rather than cauldron-crafted; folded into the staple `smoke_bomb` line above on prune.

---

## B. Meals (station = `cooking_pot` — timed buffs, NO hunger system)

Cooked food. **Every row is a short timed BUFF** (the GDD has no hunger/stamina to refill). `id` · `station`
(always `cooking_pot`) · `ingredients` · `effect` (the timed buff) · `tier` · `source-zone`. "long" = a
preservation/cured dish with an extended buff window.

### B.1 — Indexed from the zones

| id | station | ingredients | effect (timed buff) | tier | source-zone |
|---|---|---|---|---|---|
| `bee_bread` | cooking_pot / buy@beekeeper | pollen 3 + honey 1 | short `move_speed_pct` (also fed to a hive for yield) | T1 | bee_meadow |
| `honey_cake` | cooking_pot | honey 2 + wheat 2 + nectar_bloom 1 | small `max_hp` + `hp_regen` | T1 | bee_meadow |
| `pollen_loaf` | cooking_pot / buy@apiarist | pollen 4 + bumble_nectar 1 | `move_speed_pct +3` + `max_hp +3` (also feeds the Apiary) | T2 | meadow |
| `pollinators_loaf` | cooking_pot | clover_honey 1 + wheat 2 + pollen 1 | `pollination +5` + `harvest_yield +1` (farming-session buff) | T2 | meadow |
| `bumble_butter` | cooking_pot | bumble_nectar 1 + apple 2 | `max_hp +5` + `hp_regen` (hearty) | T2 | meadow |
| `garden_salad` | cooking_pot | cabbage 1 + carrot 1 + flower 1 | `move_speed_pct +3` (short) | T1 | village |
| `apple_tart` | cooking_pot | apple 2 + pressed_apple 1 + wheat 1 | `hp_regen` (short, hearty) | T1 | village |
| `honeydew_bun` | cooking_pot | wheat 2 + honeydew 1 | `luck +1` (short, "lucky day") | T1 | village |
| `snail_skewer` | cooking_pot | snail 2 + thyme 1 | `defense +1` (short) | T1 | village |
| `forager_stew` | cooking_pot | mushroom_brown 1 + carrot 1 + sage 1 | `pickup_radius +1` (short) | T1 | village |
| `mint_cooler` | cooking_pot | mint 2 + honeydew 1 | `hazard_resist +1` (short, "stay cool") | T1 | village |
| `nectar_cake` | cooking_pot | wheat 2 + nectar 1 + honey 1 | `luck +1` (short, "sweet luck") | T2 | butterfly_fields |
| `wildflower_honey_toast` | cooking_pot / buy@cabin | wheat 1 + honey 1 + nectar 1 | `hp_regen` (short) | T2 | butterfly_fields |
| `glowberry_tart` | cooking_pot | berries 2 + glow_bloom 1 + wheat 1 | `night_vision +1` (short) | T2 | butterfly_fields |
| `monarch_feast` | cooking_pot | corn 1 + pumpkin 1 + nectar 2 + sage 1 | `rare_bug_luck +1` + `bug_value_pct +3` (short, trophy meal) | T3 | butterfly_fields |
| `silk_tea_biscuit` | cooking_pot | wheat 2 + nectar 1 + lavender 1 | `calm_radius +1` (short) | T2 | butterfly_fields |
| `steady_hand_tea` | cooking_pot | thyme 1 + nectar 1 + mint 1 | short `catch_arc` + `catch_radius` buff (skill-catch aid) | T2 | butterfly_fields |
| `desert_jerky` | cooking_pot | dead_scorpion 1 *(or any `dead_*` bug-meat)* + rock_salt 1 + sage 1 | long `max_hp +5` / `hp_regen +1` (salt-cured) | T3 | scorpion_rocks |
| `forest_jerky` | cooking_pot | dead_beetle 1 *(or any `dead_*` bug-meat)* + mushroom_morel 1 + sage 1 | long `max_hp +6` / `hp_regen +1` (smoked) | T4 | millipede_forest |
| `harvester_feast` | cooking_pot / buy@farmhouse | grasshopper_leg 1 + corn 2 + pumpkin 1 + locust_oil 1 | `max_hp +` + `harvest_yield +1` + `defense +1` (long, "feast before the wave") | T4 | locust_farmland |
| `fried_locust` | cooking_pot | locust_wing 2 + locust_oil 1 + wheat 1 | `damage_pct +5%` vs swarms (short) | T4 | locust_farmland |
| `grain_porridge` | cooking_pot | blighted_grain 2 + corn 1 *(purified)* | `hp_regen` (long, cheap survival ration) | T4 | locust_farmland |
| `cricket_skewer` | cooking_pot | dead_cricket 2 + eggplant 1 + thyme 1 | `night_vision +1` + `move_speed_pct +3` (short) | T4 | locust_farmland |
| `warden_stew` | cooking_pot | beetle_mandible 1 *(broth)* + cabbage 1 + carrot 1 | `defense +2` + `thorns +1` (short, pre-wave) | T4 | locust_farmland |
| `spider_jerky` | cooking_pot | dead_spider 1 *(or any `dead_*` bug-meat)* + gorse_thorn 1 + sage 1 | long `max_hp +6` / `hp_regen +1` (preservation) | T4 | spider_vale_west |
| `fungus_bread` | cooking_pot | ant_fungus 2 + wheat 1 | `hp_regen +1` (short, hearty staple loaf) | T2 | ant_colony |
| `fungus_stew` | cooking_pot | ant_fungus 2 + mushroom_glow 1 + carrot 1 | `light_radius +1` + `night_vision +1` (short, "eat the glow") | T2 | ant_colony |
| `royal_jelly_tonic` | cooking_pot / find | royal_jelly_ant 1 + honeydew 1 | `max_hp +5` + `hp_regen +1` (long, rich, Queen-drop meal) | T3 | ant_colony |
| `fungus_jerky` | cooking_pot | ant_fungus 2 + dead_ant 1 *(or any `dead_*` bug-meat)* + chalk_stone 1 *(lime cure)* | long `defense +1` / `hp_regen +1` (preservation) | T2–T3 | ant_colony |
| `cave_jerky` | cooking_pot | dead_beetle 1 *(or any `dead_*` bug-meat)* + cave_nitre 1 + mushroom_glow 1 | long `max_hp +5` / `hp_regen +1` (nitre-cured) | T3 | centipede_cavern |
| `glow_jerky` | cooking_pot | dead_beetle 1 *(or any `dead_*` bug-meat)* + glowshroom 1 + saltpeter 1 *(cure)* | long `night_vision +1` / `hp_regen +1` (salt-cured) | T3 | underground_passages |
| `grilled_cavefish` | cooking_pot | fish_fillet 2 + cave_salt 1 + cave_moss 1 | `max_hp` + `hp_regen` (hearty) | T3 | underground_river |
| `crayfish_boil` | cooking_pot | crayfish_claw 2 + cave_salt 1 | `defense +1` (short, shell-armor) | T3 | underground_river |
| `cured_fillet` | cooking_pot | fish_fillet 2 + cave_salt 2 | `hp_regen` (long, travel food) | T3 | underground_river |
| `glowcap_chowder` | cooking_pot | fish_fillet 1 + mushroom_glow 2 + cave_water 1 | `night_vision` (short — eat to see) | T3 | underground_river |

### B.2 — Cross-cutting staple meals (fill to quota; cover the buff vocab)

Generic cooked buffs covering the meal stat vocab the zone list is thin on — `harvest_yield`, catch buffs,
`sell_pct`, comfort, combat prep, `crit`, `light/night`, `move_speed`. Cheap crop/forage reagents; tier
tracks ingredients.

| id | station | ingredients | effect (timed buff) | tier | source-zone |
|---|---|---|---|---|---|
| `harvest_pie` | cooking_pot | pumpkin 1 + wheat 2 + carrot 1 | `harvest_yield +1` (a farming-session buff) | T1 | staple |
| `bountiful_roast` | cooking_pot | corn 2 + pumpkin 1 + sage 1 | `harvest_yield +1` + `crop_quality +1` (bigger farm haul) | T2 | staple |
| `anglers_supper` | cooking_pot | fish_fillet 1 + thyme 1 + carrot 1 | `catch_cap` + `catch_radius` (a fishing/catch-session buff) | T3 | staple |
| `collectors_lunch` | cooking_pot | berries 2 + nectar 1 + mint 1 | `catch_arc` + `rare_bug_luck` (a specimen-hunt buff) | T2 | staple |
| `merchants_platter` | cooking_pot | apple 2 + honey 1 + cabbage 1 | `sell_pct` + `bug_value_pct` (sell-run "good haggling" buff) | T2 | staple |
| `cozy_hearth_stew` | cooking_pot | carrot 1 + cabbage 1 + mushroom_brown 1 + thyme 1 | `comfort` + small `hp_regen` (the cozy home-cooked buff) | T1 | staple |
| `warriors_breakfast` | cooking_pot | corn 1 + dead_beetle 1 *(bug-meat)* + sage 1 | `defense +1` + `damage_pct` (combat-prep, "eat before the fight") | T2 | staple |
| `crit_skewer` | cooking_pot | dead_wasp 1 *(bug-meat)* + thyme 1 + mint 1 | `crit_chance` (short, precision-prep) | T2 | staple |
| `speed_noodles` | cooking_pot | wheat 2 + mint 1 + carrot 1 | `move_speed_pct +4` (short, the cheap mobility meal) | T1 | staple |
| `night_owl_pie` | cooking_pot | berries 2 + glowshroom 1 + wheat 1 | `night_vision +1` + `light_radius` (the night-shift meal) | T2 | staple |
| `hearty_stew` | cooking_pot | pumpkin 1 + carrot 1 + dead_beetle 1 *(bug-meat)* | `max_hp` + `hp_regen` (long, the big hearty meal) | T2 | staple |
| `iron_ration` | cooking_pot | wheat 2 + rock_salt 1 + dead_ant 1 *(bug-meat)* | `defense +1` (long, cured travel ration) | T2 | staple |

---

## Counts

- **Potions (cauldron):** 61 + 17 = **78** — 61 indexed from zones (A.1) + 17 cross-cutting staples (A.2).
- **Meals (cooking_pot):** 35 + 12 = **47** — 35 indexed from zones (B.1) + 12 cross-cutting staples (B.2).

Both sections clear the ≥25 floor with room to prune. Generous by design — **we prune later, never thin.**

> **Prune notes for later:** several ids legitimately recur across zones at different tiers (the
> `antivenom` / `antidote` / `venom_coat` / `venom_oil` / `venom_coating` venom-cure-and-coat family; the
> `*_breathing_potion` water-breath family; the `*_jerky` cured-meat family; the `light`-oil family). On
> prune, collapse each family to a **per-tier ladder** (one cheap + one strong per tier band) rather than
> deleting the zone flavor. The staple sections (A.2 / B.2) are the deduped generic fallback — if a zone's
> bespoke version covers a stat, the generic staple for that stat can be dropped.
