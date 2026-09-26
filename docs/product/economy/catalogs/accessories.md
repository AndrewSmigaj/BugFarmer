# Accessories Catalog

> **Finalize review (2026-06-25, `DECISIONS.md` D10/D16).** Accessories are the **richest bonus layer** (most
> bonuses live here — keep it deep). **Keep Part B as-is** — the systematic one-per-stat base floor is exactly
> right, including knockback/attack-speed/the trade-off "glass" pieces. **Trim Part A (zone) redundancy:**
> (1) **fold** the set "band" pieces (`colonist_band`, `prospector_band`, `spelunker_band`, `delver_band`,
> `warden_band`, `widow_locket`) into their marquee charm — sets are now consolidated (D10); (2) **cut**
> `firewarden_crown` (no firewarden) and the locust `chorusbreaker_charm` (no special locust gear);
> (3) **consolidate** the near-duplicate dive trinkets (`pressure_charm` ≈ `pearl_diver_charm` ≈
> `frog_leg_charm` ≈ `lily_glider`) into ~1–2 water-traversal accessories on the **Diver** line; (4) venom-on-hit
> pieces (`toebiter_fang`) **stay** — venom/poison are real mechanics (D16); (5) **keep the loupe**
> (`prospectors_loupe`). Net Part A ≈ 43 → ~28; the `<gem>+<metal>` naming + cost-pts stay. Below is the
> pre-trim draft.

**Slots:** 2 accessory slots — the *richest* bonus layer in the game. Accessories are small,
mix-and-match bonuses (no single piece dominates); the build comes from the *combination*. This
is where players express their playstyle (offense / defense / mining / farming / catching /
traversal / economy / luck).

**Two families:**
- **Zone accessories** (Part A below) — themed trinkets sourced from a specific zone (jeweler
  recipe + zone material, a boss/rare drop, a quest, or a found recipe scroll). They carry the
  zone's fantasy and usually 2–4 small bonuses.
- **Base accessories** (Part B below) — cross-cutting jeweler staples (a gem + a metal) that
  cover every stat in the vocab, available from the village/town jeweler regardless of zone. They
  are the floor: a single-focus accessory for any stat, plus a handful of trade-off pieces.

**Cost tier-points (per the brief):** gem-minor = 10 · gem-major = 16 · gold = 16 · silver = 10.
Tier-points are summed across an accessory's gem/metal cores to give a rough crafting cost weight
(used for balancing, not a literal coin price).

**Bonus convention:** values shown are the per-piece bonus. With 2 slots, the strongest single-stat
stack is two of the same base accessory (or a base + a zone piece that shares the stat). Trade-off
("glass") accessories carry a penalty (−Y) and are deliberately stronger on the +X.

---

## Part A — Zone Accessories (indexed from `../zones/*.md`)

Every accessory found in the zone docs, with id · zone (tier band) · source · bonus(es). "Optional
matching accessory" = the set's optional 4th/5th jewelry piece flagged in that zone's outfit section.

| id | zone · tier | source | bonus(es) |
|----|-------------|--------|-----------|
| `bee_charm` ✅ | bee_meadow · T1–T2 | buy@beekeeper / rare skep drop | `honey_yield_pct` |
| `lucky_clover` ✅ | village · T1 | forage/find (rare `clover`) | `gem_luck` / drop-luck — **as-built** accessory item (`armor_slot: accessory`) |
| `pollinator_ring` | bee_meadow · T1–T2 | jeweler (`copper_bar` ×2 + `pollen` ×4 + `quartz` ×1) | `pollination` (boosts crop/flower pollination; honey-adjacent) |
| `reed_snorkel` | shallow_swamp · T2 (head) | workbench (`reed_stalk` ×4 + `reed_fiber` ×3 + `swamp_gas` ×1) | `water_breath` (short timer) |
| `lily_glider` | shallow_swamp · T3 | find (recipe scroll in swamp) — jeweler/workbench | brief `water_walk` + `fall_resist` (pad-hop gaps) |
| `leech_charm` | shallow_swamp · T2–T3 | jeweler (`leech_extract` + gem-minor) | `hp_regen` (slow leech-anticoagulant heal) |
| `whirligig_lens` | shallow_swamp · T2–T3 | jeweler (`whirligig_shell` split-eye + `glass`) | `night_vision` + small `catch_arc` |
| `damsel_pin` | shallow_swamp · T2–T3 | find / jeweler (`damselfly_wing` ×4) | `rare_bug_luck` + tiny `move_speed_pct` |
| `frog_leg_charm` | shallow_swamp · T2–T3 | drop/quest (`frog_spawn`-line) | brief `water_walk` + `fall_resist` (cheap traversal) |
| `stinger_pendant` | wasp_thicket · T2→T4 (bridge) | jeweler (`wasp_stinger` ×6 + `silver_bar` ×1 + `quartz` ×1) | `crit_chance +5`, `rare_bug_luck +1` |
| `clay_buckler` | wasp_thicket · T2 (shield/accessory) | buy@thicket_vendor (`clay` ×4 + `bronze_bar` ×1 + `bramble_vine` ×2) | `defense +3`, `knockback` resist, `thorns +1` |
| `hornet_pendant` | meadow · T3 | jeweler (`hornet_carapace` ×1 + `silver_bar` ×1 + `quartz` ×1) | `sting_immunity +1`, `rare_bug_luck +1` |
| `luck_charm` | butterfly_fields · T3 (trinket) | jeweler (`butterfly_scale` ×4 + `silver_ore` ×1 + `thread` ×1) | `luck +1`, `rare_bug_luck +1` |
| `monarch_brooch` | butterfly_fields · T3 (rare-luck) | jeweler (`monarch_scale` ×2 + `gold_ore` ×1 + `prism_dust` ×1) | `rare_bug_luck +2`, `bug_value_pct +5` |
| `glasswing_lens` | butterfly_fields · T3 (held sighting aid) | jeweler (`glass_scale` ×2 + `prism_dust` ×1 + `glass` ×2) | `rare_bug_luck +1`, `catch_radius +1` |
| `glasswing_pendant` | butterfly_fields · T3 (optional 5th) | jeweler (`glass_scale` ×2 + `prism_dust` ×1 + …) | `gem_luck` / clarity (Collector's set stretch piece) |
| `prism_goggles` | butterfly_fields · T3 (head, night-sight) | jeweler (`bronze_bar` ×1 + `prism_dust` ×1 + `glass_scale` ×1) | `night_vision +2`, `gem_luck +1` |
| `miners_charm` | scorpion_rocks · T3 | buy@miners_camp (recipe) — jeweler (`quartz` ×2 + `crystal` ×1 + `gem_geode` ×1 + `copper_bar` ×1) | `ore_fortune +1`, `gem_luck +2`, `luck +1` |
| `quartz_pendant` | scorpion_rocks · T3→T5 (bridge) | craft / find — jeweler (`cut_quartz` ×1 + `silver_bar` ×1 + `scorpion_claw` ×1) | `crit_chance +6`, `gem_luck +1`, `rare_bug_luck +1` |
| `prospector_band` | scorpion_rocks · T3 (optional 4th) | jeweler (`cut_quartz` ×1 + `iron_bar` ×1 + `scorpion_claw` ×2) | `mining_speed_pct`, `gem_luck` |
| `stalkers_charm` | spider_vale_west · T4→T5 | buy@hunters_lodge (recipe) — jeweler (`jumping_spider_eye` ×2 + `silver_bar` ×1 + `gossamer_dew` ×1) | `dodge_chance +5`, `crit_chance +5`, `move_speed_pct +3` |
| `thorn_band` | spider_vale_west · T4→T5 | craft / find — jeweler (`gorse_thorn` ×3 + `centipede_plate` ×1 + `silver_bar` ×1) | `thorns +3`, `defense +2`, `knockback +1` |
| `huntsman_charm` | spider_vale_east · T5 (powerful) | **find@spider_vale_east** (rare boss-lair recipe — not sold) — jeweler (`huntsman_fang` ×1 + `huntsman_eye` ×1 + `diamond` ×1 + `gold_bar` ×1) | `crit_chance +8`, `crit_mult +0.5`, `damage_pct +8`, `rare_bug_luck +1` |
| `web_walker_band` | spider_vale_east · T5 | craft / find — jeweler (`royal_silk` ×1 + `silver_bar` ×1 + `trapdoor_silk` ×1) | `dodge_chance +6`, `move_speed_pct +4`, `fall_resist +1` |
| `widow_locket` | spider_vale_east · T5 (optional 4th) | jeweler (`royal_silk` ×1 + `huntsman_fang` ×1 + …) | `life_on_hit`, `crit_chance` |
| `colonist_charm` | ant_colony · T2→T3 | craft / buy@myrmecologist — jeweler (`cut_glowquartz` ×1 + `harvester_mandible` ×1 + `copper_bar` ×1) | `light_radius +1`, `harvest_yield +1`, `luck +1` |
| `colonist_band` | ant_colony · T2→T3 (optional 4th) | jeweler (`cut_glowquartz` ×1 + `harvester_mandible` ×1 + …) | `light_radius`, `harvest_yield` |
| `prospectors_loupe` | underground_passages · T3→T5 | craft / buy@miners_outpost — jeweler (`cave_nitre` ×1 + `cut_emerald` ×1 + `silver_bar` ×1) | `gem_luck +2`, `vein_sense +1`, `light_radius +1` |
| `spelunker_band` | underground_passages · T3→T5 (optional 4th) | jeweler (`cut_sapphire` ×1 + `silver_bar` ×1 + …) | `mining_speed_pct`, `carry_weight`, `light_radius` |
| `glowstone_amulet` | centipede_cavern · T3→T5 (bridge) | buy@hermit (recipe) / craft — jeweler (`cut_glow_crystal` ×1 + `silver_bar` ×1 + `glowworm_lumen` ×1) | `light_radius +2`, `night_vision +1`, `crit_chance +6`, `gem_luck +1` |
| `delver_band` | centipede_cavern · T3 (optional 4th) | jeweler (`cut_glow_crystal` ×1 + `iron_bar` ×1 + `glowworm_lumen` ×1) | `light_radius`, `crit_chance`, `gem_luck`; set: deep_delver |
| `warden_band` | millipede_forest · T4 (optional 5th) | jeweler (`beetle_carapace` ×1 + `steel_bar` ×1 + `forest_centipede_fang` …) | `thorns`, `defense`, `hp_regen`; set: carapace_warden |
| `pressure_charm` | deep_swamp · T4 | find / buy@hermit — jeweler (`bog_pearl` ×1 + `lotus_essence` ×1 + `silver_bar` ×1) | extend `water_breath` reserve + `hazard_resist +1` (cold/pressure) |
| `dragonfly_glider` | deep_swamp · T4 (back/accessory) | find (recipe scroll) — jeweler/workbench (`dragonfly_wing` ×6 + `sunken_log` ×2 + `reed_fiber` ×4 + `silk` ×2) | `fall_resist`, glide gaps, brief `water_walk` on landing, `move_speed_pct +4` |
| `pearl_charm` | deep_swamp · T4 | jeweler (`bog_pearl` + `silver_bar`) | `gem_luck` + `hazard_resist +1` |
| `dragoneye_lens` | deep_swamp · T4 | jeweler (`dragonfly_eye` + `cave_quartz`/`glass`) | `night_vision` + `catch_radius +1` |
| `serpent_glow_charm` | deep_swamp · T4 (elite trophy) | find / jeweler (`serpentfly_scale` ×2 + `serpentfly_ichor` ×1) | `light_radius +2` + `rare_bug_luck` + tiny `move_speed_pct` |
| `toebiter_fang` | deep_swamp · T4 (combat charm) | drop/quest (`waterbug_venom_gland`-line) | `damage_pct` vs bugs + light `venom`-on-hit |
| `pearl_pendant` | underground_river · T4 (signature pearl) | buy@fisher — jeweler (`cave_pearl` ×2 + `silver_bar` ×1 + `nacre_inlay` ×1) | `luck +1`, `gem_luck +1`, small `water_breath` reserve |
| `pearl_diver_charm` | underground_river · T4 | find / buy@fisher — jeweler (`cave_pearl` ×1 + `lotus_essence` ×1 + `silver_bar` ×1) | extend `water_breath` reserve + `hazard_resist +1` (cold) |
| `glowscale_lens` | underground_river · T3 | find / jeweler (`blind_fish_scale` ×2 + `cave_quartz` ×1 + `glow_gland` ×1) | `night_vision` + `catch_radius +1` + small `light_radius` |
| `glow_charm` | underground_river · T3–T4 | find / jeweler (`glow_gland` ×2 + `freshwater_nacre`) | `light_radius +2` + tiny `move_speed_pct` |
| `crayfish_charm` | underground_river · T3–T4 | jeweler / drop (`crayfish_claw` ×2 + gem-minor) | `defense +1` + `thorns` vs water bugs |
| `crabshell_pauldron` | underground_river · T4 (apex trophy) | drop/quest (`cave_crab_carapace`-line) | `defense +2` + `knockback +1` |
| `chorusbreaker_charm` | locust_farmland · T5 reach (trinket) | craft (buy recipe) — jeweler (`silver_bar` ×2 + `cricket_song_organ` ×2 + `quartz` ×1) | `night_vision +2`, nearby-swarm `attack_speed_pct -10%` aura (anti-cricket-song) |
| `firewarden_crown` | deadly_ants · T5 (head — listed here as the jeweler-inlay crown) | find@deadly_ants (rare War-Queen cache) — jeweler (`war_queen_chitin` ×1 + `flame_alloy` ×1 + `gold_bar` ×1 + `royal_jelly` ×1) | `defense +4`, `hazard_resist +3` (fire), `damage_pct +6`, `light_radius +1` |

**Part A count: 43 zone accessories.**

> Notes:
> - `firewarden_crown` is authored as a head slot in deadly_ants but is jeweler-inlaid and accessory-shaped;
>   listed for completeness. If head pieces are armor-only, drop it and Part A = 42.
> - `colonist_charm`/`colonist_band` are flagged in ant_colony as the same role (keep one as set piece, one as
>   open-market trinket, or fold on prune). Same for the several "optional 4th/5th" set bands — they may
>   collapse into their marquee charm on a balance pass.
> - `pressure_charm` (deep_swamp) and `pearl_diver_charm` (underground_river) are near-duplicate dive trinkets
>   in different zones — intentional parallel, prune-candidate if cross-zone dupes are unwanted.
> - `reed_snorkel`, `prism_goggles`, `firewarden_crown` occupy the head slot in their zones; the rest are
>   true 2-slot accessories.

---

## Part B — Base Accessories (cross-cutting jeweler staples)

The village/town jeweler sells these regardless of zone progress. Each is a **gem + metal** core so it
slots into the gem-minor (10) / gem-major (16) / gold (16) / silver (10) cost economy. They guarantee that
**every stat in the vocab has at least one single-focus accessory**, so any build is expressible from day
one and the zone pieces become *upgrades / multi-stat bundles* rather than the only source.

**Naming:** `<gem/metal>_<focus>_<form>`. Forms rotate (ring / charm / band / pendant / amulet / brooch /
loop / locket / loupe) purely for flavor.

### B1 — Combat & survival

| id | slot/source | tier (cost-pts) | bonus(es) |
|----|-------------|-----------------|-----------|
| `iron_ward_band` | accessory · jeweler (iron + gem-minor) | T2 (10) | `defense +2` |
| `oak_heart_charm` | accessory · jeweler (silver + gem-minor) | T2–T3 (20) | `max_hp +15` |
| `garnet_fury_ring` | accessory · jeweler (gem-major + silver) | T3 (26) | `damage_pct +6` |
| `keen_edge_loop` | accessory · jeweler (gem-minor + silver) | T2–T3 (20) | `crit_chance +5` |
| `deepcut_pendant` | accessory · jeweler (gem-major + gold) | T4 (32) | `crit_mult +0.4` |
| `quickdraw_band` | accessory · jeweler (silver + gem-minor) | T3 (20) | `attack_speed_pct +10` |
| `mendstone_charm` | accessory · jeweler (silver + gem-minor) | T2–T3 (20) | `hp_regen +1` |
| `bloodleech_locket` | accessory · jeweler (gem-major + silver) | T4 (26) | `life_on_hit +1` |
| `bramble_brooch` | accessory · jeweler (iron + gem-minor) | T2–T3 (10) | `thorns +2` |
| `feather_step_ring` | accessory · jeweler (silver + gem-minor) | T3 (20) | `dodge_chance +5` |
| `wardstone_amulet` | accessory · jeweler (gold + gem-minor) | T4 (26) | `hazard_resist +2` |

### B2 — Mining & gems

| id | slot/source | tier (cost-pts) | bonus(es) |
|----|-------------|-----------------|-----------|
| `pickfast_band` | accessory · jeweler (iron + gem-minor) | T2–T3 (10) | `mining_speed_pct +12` |
| `fortune_loupe` | accessory · jeweler (gold + gem-minor) | T4 (26) | `ore_fortune +2` |
| `gemseeker_loupe` | accessory · jeweler (gem-major + silver) | T3–T4 (26) | `gem_luck +2` |
| `lodestone_charm` | accessory · jeweler (silver + gem-minor) | T3 (20) | `vein_sense +1` |
| `lantern_loop` | accessory · jeweler (gem-minor + iron) | T2 (10) | `light_radius +2` |

### B3 — Farming & crops

| id | slot/source | tier (cost-pts) | bonus(es) |
|----|-------------|-----------------|-----------|
| `verdant_ring` | accessory · jeweler (silver + gem-minor) | T2–T3 (20) | `crop_growth_pct +8` |
| `harvest_charm` | accessory · jeweler (silver + gem-minor) | T2–T3 (20) | `harvest_yield +1` |
| `sunsheaf_pendant` | accessory · jeweler (gold + gem-minor) | T3–T4 (26) | `crop_quality +1` |
| `pollen_loop` | accessory · jeweler (gem-minor + copper) | T2 (10) | `pollination +1` |
| `apiary_amulet` | accessory · jeweler (gold + gem-minor) | T3–T4 (26) | `honey_yield_pct +10` |

### B4 — Bug catching & taming

| id | slot/source | tier (cost-pts) | bonus(es) |
|----|-------------|-----------------|-----------|
| `widenet_charm` | accessory · jeweler (silver + gem-minor) | T2–T3 (20) | `catch_radius +1` |
| `sweeparc_loop` | accessory · jeweler (silver + gem-minor) | T3 (20) | `catch_arc +1` |
| `keepers_locket` | accessory · jeweler (gold + gem-minor) | T3–T4 (26) | `catch_cap +1` |
| `cloverluck_charm` | accessory · jeweler (gem-major + silver) | T3 (26) | `rare_bug_luck +1` |
| `soothe_band` | accessory · jeweler (silver + gem-minor) | T2–T3 (20) | `calm_radius +1` |
| `wardbug_amulet` | accessory · jeweler (gold + gem-minor) | T3–T4 (26) | `sting_immunity +1` |
| `appraiser_loupe` | accessory · jeweler (gem-major + gold) | T4 (32) | `bug_value_pct +8` |

### B5 — Traversal & utility

| id | slot/source | tier (cost-pts) | bonus(es) |
|----|-------------|-----------------|-----------|
| `swift_ring` | accessory · jeweler (silver + gem-minor) | T2–T3 (20) | `move_speed_pct +4` |
| `tideglass_charm` | accessory · jeweler (gem-major + silver) | T3–T4 (26) | brief `water_walk` |
| `gillstone_pendant` | accessory · jeweler (gem-major + silver) | T3 (26) | `water_breath` (short) |
| `owl_eye_loop` | accessory · jeweler (gem-minor + silver) | T2–T3 (20) | `night_vision +2` |
| `cat_grace_band` | accessory · jeweler (silver + gem-minor) | T2–T3 (20) | `fall_resist +1` |
| `magnet_charm` | accessory · jeweler (silver + gem-minor) | T2 (20) | `pickup_radius +1` |

### B6 — Economy & luck

| id | slot/source | tier (cost-pts) | bonus(es) |
|----|-------------|-----------------|-----------|
| `merchants_locket` | accessory · jeweler (gold + gem-minor) | T3–T4 (26) | `sell_pct +6` |
| `haggler_loop` | accessory · jeweler (gold + gem-minor) | T3–T4 (26) | `buy_discount_pct +6` |
| `wishbone_charm` | accessory · jeweler (gem-major + gold) | T4 (32) | `luck +2` |

### B7 — Trade-off accessories (glass / focus)

Each carries a penalty; deliberately stronger on the +X. Two slots means a player can run one glass piece
plus a stabilizing base/zone piece.

| id | slot/source | tier (cost-pts) | bonus(es) |
|----|-------------|-----------------|-----------|
| `glasscannon_ring` | accessory · jeweler (gem-major + gold) | T4 (32) | `damage_pct +12` / `defense −3` |
| `berserkers_band` | accessory · jeweler (gem-major + silver) | T4 (26) | `attack_speed_pct +18` / `max_hp −10` |
| `recklessblade_charm` | accessory · jeweler (gem-major + gold) | T4 (32) | `crit_chance +10` / `dodge_chance −4` |
| `ironclad_locket` | accessory · jeweler (gold + gem-minor) | T3–T4 (26) | `defense +5` / `move_speed_pct −4` |
| `prospectors_gambit` | accessory · jeweler (gem-major + silver) | T3–T4 (26) | `ore_fortune +3` / `mining_speed_pct −8` |
| `gluttons_pendant` | accessory · jeweler (gold + gem-minor) | T3–T4 (26) | `harvest_yield +2` / `crop_quality −1` |
| `nightstalker_charm` | accessory · jeweler (gem-major + silver) | T3–T4 (26) | `night_vision +3`, `move_speed_pct +3` / `light_radius −2` (dark-adapted) |
| `vampiric_locket` | accessory · jeweler (gem-major + gold) | T4 (32) | `life_on_hit +2` / `hp_regen −1` |

**Part B count: 11 + 5 + 5 + 7 + 6 + 3 + 8 = 45 base accessories.**

---

## Stat-vocab coverage check

Every stat the brief listed, mapped to at least one accessory (base unless a zone piece is the canonical home):

| stat | covered by |
|------|-----------|
| defense | `iron_ward_band`, `clay_buckler`, `thorn_band`, `crayfish_charm`, `crabshell_pauldron`, `ironclad_locket`, `glasscannon_ring`(−) |
| max_hp | `oak_heart_charm`, `berserkers_band`(−) |
| damage_pct | `garnet_fury_ring`, `huntsman_charm`, `toebiter_fang`, `firewarden_crown`, `glasscannon_ring` |
| crit_chance | `keen_edge_loop`, `stinger_pendant`, `quartz_pendant`, `glowstone_amulet`, `stalkers_charm`, `huntsman_charm`, `recklessblade_charm` |
| crit_mult | `deepcut_pendant`, `huntsman_charm` |
| attack_speed_pct | `quickdraw_band`, `berserkers_band`, `chorusbreaker_charm` (debuff aura) |
| hp_regen | `mendstone_charm`, `leech_charm`, `warden_band`, `vampiric_locket`(−) |
| life_on_hit | `bloodleech_locket`, `widow_locket`, `vampiric_locket` |
| thorns | `bramble_brooch`, `clay_buckler`, `thorn_band`, `warden_band`, `crayfish_charm` |
| dodge_chance | `feather_step_ring`, `stalkers_charm`, `web_walker_band`, `recklessblade_charm`(−) |
| mining_speed_pct | `pickfast_band`, `prospector_band`, `spelunker_band`, `prospectors_gambit`(−) |
| ore_fortune | `fortune_loupe`, `miners_charm`, `prospectors_gambit` |
| gem_luck | `gemseeker_loupe`, `miners_charm`, `quartz_pendant`, `prospectors_loupe`, `pearl_charm`, `pearl_pendant`, `glowstone_amulet`, `prism_goggles` |
| light_radius | `lantern_loop`, `colonist_charm`, `glowstone_amulet`, `glow_charm`, `serpent_glow_charm`, `prospectors_loupe`, `nightstalker_charm`(−) |
| hazard_resist | `wardstone_amulet`, `pressure_charm`, `pearl_charm`, `pearl_diver_charm`, `firewarden_crown` |
| vein_sense | `lodestone_charm`, `prospectors_loupe` |
| crop_growth_pct | `verdant_ring` |
| harvest_yield | `harvest_charm`, `colonist_charm`, `colonist_band`, `gluttons_pendant`(−) |
| crop_quality | `sunsheaf_pendant`, `gluttons_pendant`(−) |
| pollination | `pollen_loop`, `pollinator_ring` |
| catch_radius | `widenet_charm`, `glasswing_lens`, `dragoneye_lens`, `glowscale_lens` |
| catch_arc | `sweeparc_loop`, `whirligig_lens` |
| catch_cap | `keepers_locket` |
| rare_bug_luck | `cloverluck_charm`, `luck_charm`, `monarch_brooch`, `stinger_pendant`, `hornet_pendant`, `damsel_pin`, `serpent_glow_charm` |
| calm_radius | `soothe_band` |
| honey_yield_pct | `apiary_amulet`, `bee_charm` |
| sting_immunity | `wardbug_amulet`, `hornet_pendant` |
| bug_value_pct | `appraiser_loupe`, `monarch_brooch` |
| move_speed_pct | `swift_ring`, `stalkers_charm`, `web_walker_band`, `dragonfly_glider`, `damsel_pin`, `glow_charm`, `serpent_glow_charm`, `nightstalker_charm`, `ironclad_locket`(−) |
| water_walk | `tideglass_charm`, `lily_glider`, `frog_leg_charm`, `dragonfly_glider` |
| water_breath | `gillstone_pendant`, `reed_snorkel`, `pressure_charm`, `pearl_diver_charm`, `pearl_pendant` |
| night_vision | `owl_eye_loop`, `whirligig_lens`, `prism_goggles`, `glowstone_amulet`, `dragoneye_lens`, `glowscale_lens`, `chorusbreaker_charm`, `prospectors_loupe`(light), `nightstalker_charm` |
| fall_resist | `cat_grace_band`, `lily_glider`, `frog_leg_charm`, `dragonfly_glider`, `web_walker_band` |
| pickup_radius | `magnet_charm` |
| sell_pct | `merchants_locket` |
| buy_discount_pct | `haggler_loop` |
| luck | `wishbone_charm`, `colonist_charm`, `miners_charm`, `luck_charm`, `pearl_pendant` |

All 36 listed stats covered. (Trade-off pieces marked (−) appear under the stat they penalize too.)

---

## TOTAL

- **Part A (zone accessories indexed): 43**
- **Part B (base accessories added): 45**
- **Grand total: 88 accessories** (target ≥35 — exceeded; generous as instructed, prune later).
