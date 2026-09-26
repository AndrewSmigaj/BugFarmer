# Species & Drops — the canonical BugFarmer bug roster

> **Status:** design aggregation. This sheet rolls up **every species** from the 17 per-zone content
> sheets in [`zones/`](zones/) into one roster, grouped by zone in **progression order** (surface rows
> 2 → 1 → 0, then the underground zones). It is the canonical list the per-zone gear hangs on.
>
> **How to read it:**
> - **category** — `swarm` (cloud/cluster catch, weak singly), `solo` (single non-swarm catch/threat),
>   `predator` (hostile hunter/bruiser), `mini-boss` (the zone's flagged signature fight).
> - **✅ in code** — the 6 species that ALREADY exist in the deterministic ecology sim (see the note at
>   the end). Everything else is **design-only / new**.
> - **drop(s)** — the species' primary + signature new ingredient ids (carcass listed separately).
> - **carcass** — the `dead_*` id (the existing `dead_*` carcass family; new ones noted per-zone sheet).
> - The **MINI-BOSS** of each zone is flagged in its row and called out under the table.
>
> The 6 existing-in-code mappings (design id → code id): `fly_common`→`fly`, `butterfly_meadow`→`butterfly`,
> `wasp_common`→`wasp`, `centipede_garden`→`centipede`/`giant_centipede`, `millipede`→`giant_millipede`,
> `beetle_carrion`→the carrion/`dead_beetle` decomposer. These are the species the live food-web sim runs;
> the zone sheets re-skin / extend them. See the per-zone `dead_*` notes for the carcass family.

---

# SURFACE — Row 2 (the start row, easiest)

## Starting Village (2,1 · T1 · EASY — tutorial hub)

The fly-ecology showcase; all harmless/nuisance. Teaches every catch verb death-free.

| species id | category | behavior (short) | drop(s) — new ids | carcass |
|---|---|---|---|---|
| `fly` ✅ | swarm | Loose clouds over rot/compost; scatter & re-form fast (the "catch a hundred" bug) | `fly_clump` | `dead_fly` |
| `ladybug` | solo | Slow, calm, beneficial; the lucky/charm catch | `ladybug_shell` | — |
| `aphid` | swarm | Tiny clustered crop pest; a cluster catch (ladybugs eat them) | `aphid_cluster`, `honeydew` | — |
| `pill_bug` | solo | Roly-poly; curls when disturbed (patience catch) | `pill_chitin`, `leaf_litter` | — |
| `garden_ant` | swarm | Black ant, tidy trails between mound & food; swarms the crumb, not you | `ant_egg`, `formic_dab` | — |
| `garden_snail` | solo | Slow dew grazer; tucks into shell (bonus/flavor catch) | `snail_shell`, `snail` | — |

**No mini-boss** (tutorial zone). `fly` is the one existing-in-code species here.

## Bee Meadow (2,0 · T1–T2 · EASY)

The honey/pollination intro. Bees non-aggressive unless the hive is disturbed.

| species id | category | behavior (short) | drop(s) — new ids | carcass |
|---|---|---|---|---|
| `honeybee` | swarm | Social; lives in wild `bee_skep` hives, forages flower↔hive; defends hive if smoked un-calmed | `honeycomb` (+`honey`/`beeswax`) | — |
| `mason_bee` | solo | Solitary mud-tube nester; docile, best pollinator | `pollen`, `mud_daub` | — |
| `leafcutter_bee` | solo | Solitary; snips leaf crescents for nest cells | `leaf_disc`, `pollen` | — |
| `sweat_bee` | solo | Tiny, metallic, skittish — the zone's rare-catch | `royal_jelly` (rare), `pollen` | — |
| `pollen_beetle` | swarm | Pest; swarms open flowers, nibbles petals (easy starter drop) | `dead_beetle`, `chitin` | `dead_beetle` |

**No mini-boss.** None existing-in-code (the meadow bees are all new).

## Wasp Thicket (2,2 · T2 · MEDIUM — combat intro)

The first place that fights back: venom, stingers, swarms.

| species id | category | behavior (short) | drop(s) — new ids | carcass |
|---|---|---|---|---|
| `paper_wasp` ✅ | swarm | Nest-anchored; **swarms** (calls 2–4 nestmates), sting applies `poisoned` | `wasp_stinger`, `venom_sac` (uncommon) | `dead_wasp` |
| `mud_dauber` | solo | Burrow-anchored bruiser; does NOT swarm, hits harder, lunging sting | `mud_dauber_clay`, `venom_sac` | `dead_wasp` |
| `earwig` | predator | Ground harasser; flanks from behind, pincer melee + knockback, evasive | `earwig_pincer` | `dead_centipede` |
| `silverfish` | swarm | Fast, fragile forager; flees, eats fallen flora/fiber | `silverfish_scale` | `dead_fly` |
| `thicket_matriarch` ⭐ | **mini-boss** | Bloated paper-wasp queen; spawns `paper_wasp` adds, then heavy venom sting + AoE sting-cloud | `royal_venom` (guaranteed), `matriarch_trophy` | — |

**MINI-BOSS:** `thicket_matriarch` (great nest at the zone's heart). `paper_wasp` maps to the existing `wasp`.

## Shallow Swamp (2,3 · T2–T3 · HARD-for-row — the WATER zone)

Water-walk / water-breath debut; leech/venom reagents.

| species id | category | behavior (short) | drop(s) — new ids | carcass |
|---|---|---|---|---|
| `damselfly` | solo | Skims reeds & water in short hops; skittish (high rare-bug-luck, azure morph) | `damselfly_wing` | `dead_damselfly` |
| `pond_skater` | solo | Glides on surface tension; only reachable with `water_walk`/from a bank | `skater_oil` | `dead_skater` |
| `whirligig_beetle` | swarm | Spins in surface clusters, dives when threatened (cluster catch) | `whirligig_shell` | `dead_beetle` |
| `leech` | predator | Lurks in murky shallows; **latches** for a slow HP-drain DoT | `leech_extract` | `dead_leech` |
| `marsh_mosquito` | swarm | Dusk clouds near still water; weak sting, drawn to player | `mosquito_proboscis` | `dead_mosquito` |
| `bog_centipede` | predator | Wetland centipede apex; hostile chaser, real combat (T3 fight) | `centipede_parts` | `dead_centipede` |

**No mini-boss** (the `bog_centipede` is an apex T3 chaser, not flagged a boss). None existing-in-code as such
(`bog_centipede` is a variant of the in-code centipede; `whirligig`→`dead_beetle` reuses the beetle carcass).

---

# SURFACE — Row 1 (the mid row)

## Hilltop Meadow (1,0 · T2–T3 · MEDIUM — advanced beekeeping + pest-control)

Bees fight back and fight for you; hornets are the apex threat.

| species id | category | behavior (short) | drop(s) — new ids | carcass |
|---|---|---|---|---|
| `bumblebee` | solo | Big, loud heavyweight pollinator; defends its tussock nest (bull-rush + hard sting) | `bumble_fuzz`, `bumble_nectar` (+`pollen`) | — |
| `carpenter_bee` | solo | Glossy borer; bores tunnels in snags/beams; males dive-bomb (bluff) | `carpenter_resin` (+`wood`/`pollen`) | — |
| `hornet` ⭐ | **mini-boss / apex** | Hyper-aggressive paper-nest hornet; sentry recruits the whole nest (true swarm), venom `poisoned`+`knockback`, hunts your bees | `hornet_venom`, `hornet_carapace` (+`wasp_stinger`) | `dead_wasp` |
| `paper_wasp` ✅ | swarm | Reused as a **pest-control ally**: seeded `wasp_lodge` patrol hunts crop pests | `wasp_stinger`, `venom_sac` | `dead_wasp` |
| `cabbage_white` | swarm | Pretty white butterfly; its **caterpillars eat crops** (the pest the wasps cull) | `cabbage_caterpillar`, `silk_thread` (+`pollen`) | — |

**MINI-BOSS / apex threat:** `hornet` (the great paper-hornet nest — clearing it is the zone objective).
`paper_wasp` reuses the existing `wasp`.

## Butterfly Fields (1,1 · T2–T3 · MEDIUM — lepidoptera + glow)

Day = butterflies/cicadas; **night** = moths/fireflies + the glow economy. Catch-focused, no real combat.

| species id | category | behavior (short) | drop(s) — new ids | carcass |
|---|---|---|---|---|
| `butterfly` ✅ | solo | Lazy bloom-to-bloom drift (the bread-and-butter beautiful catch) · day | `butterfly_scale` (+`nectar`) | `dead_butterfly` |
| `monarch` | solo | Bigger, bolder milkweed glider; the trophy day catch | `monarch_scale` | — |
| `glasswing` | solo | Rare transparent-wing drifter; the luck catch · dawn/dusk | `glass_scale` | — |
| `luna_moth` | solo | Big pale-green night flier drawn to lantern; the silk source · night | `moth_silk`, `luna_dust` | — |
| `emperor_moth` | solo | Large eyespotted moth; "plays dead" then bursts (patience) · night | `emperor_silk`, `eyespot_scale` | — |
| `firefly` | swarm | Low blinking swarms after dusk; stores living light · night | `firefly_lumen`, `firefly_dust` | — |
| `cicada` | solo | Loud, clingy day bug; one explosive jump when grabbed (timing) · day | `cicada_shell`, `cicada_wing` | — |
| `hawk_moth` | solo | Fast hovering dusk nectar-feeder (the skill/speed catch) · dusk | `hawkmoth_silk` (+`nectar`) | — |

**No mini-boss** (the "danger" is missing the rare catch). `butterfly` is the existing-in-code species.

## Scorpion Rocks (1,2 · T3 reaching T4 · HARD — mining intro + potent venom)

First real mining; venom that can kill. Heat/hazard survival debuts.

| species id | category | behavior (short) | drop(s) — new ids | carcass |
|---|---|---|---|---|
| `bark_scorpion` | predator | Den-anchored; claws to grapple then stings → strong `envenomed`; low-light hunter | `scorpion_venom`, `scorpion_claw` | `dead_scorpion` |
| `desert_tick` | swarm | Gravel cluster parasite; **latches** for a slow `bleed` leech | `tick_sac` | `dead_tick` |
| `harvestman` | solo | Long-legged daddy-longlegs; stilts, flanks, flees (high dodge, no venom) | `harvestman_leg` | `dead_centipede` |
| `vinegaroon` | solo | Whip-scorpion bruiser; does NOT swarm, **sprays acid** (`acetic`, shreds defense) | `vinegaroon_acid` | `dead_scorpion` |
| `den_matron` ⭐ | **mini-boss** | Bloated brood-mother scorpion; spawns `bark_scorpion` adds, heavy `envenomed` sting + venom-mist AoE | `potent_venom` (guaranteed), `matron_carapace` | — |

**MINI-BOSS:** `den_matron` (the great den). None existing-in-code.

## Deep Swamp (1,3 · T3–T4 · EXTRA-HARD — dangerous deep water)

Aquatic predators + dark bog-alchemy (disease & poison). Most species hostile.

| species id | category | behavior (short) | drop(s) — new ids | carcass |
|---|---|---|---|---|
| `swamp_mosquito` | swarm | Aggressive chasing clouds; bites apply stacking `swamp_fever` | `mosquito_venom` (+`mosquito_proboscis`) | `dead_mosquito` |
| `dragonfly` | predator | Fast aerial hunter; thins mosquitoes, flees hard (rare morph) | `dragonfly_wing`, `dragonfly_eye` | `dead_dragonfly` |
| `dragonfly_nymph` | predator | Underwater larval ambush-predator (dive-only, extendable jaw) | `nymph_jaw`, `nymph_gill` | `dead_nymph` |
| `water_strider` | solo | Deep surface-tension skater; platform/`water_walk` only, very evasive | `strider_leg`, `strider_oil` | `dead_strider` |
| `giant_water_bug` ⭐ | **mini-boss / apex** | Submerged "toe-biter"; ambushes from below, dissolving-venom DoT, armored bruiser (T4) | `giant_waterbug_carapace`, `waterbug_venom_gland` | `dead_giant_waterbug` |
| `swamp_leech` | predator | Fatter deep leech; latches in clusters for fast HP-drain + disease tick | `leech_extract` | `dead_leech` |
| `bog_serpent_fly` | solo | Rare/elite serpentine "damsel-dragon" in sunken hollows; glowing, evasive · night | `serpentfly_scale`, `serpentfly_ichor` | `dead_serpentfly` |

**MINI-BOSS / apex:** `giant_water_bug` (the toe-biter — its carapace builds the Bog-Hunter set).
None existing-in-code.

---

# SURFACE — Row 0 (the hard top row)

## Locust Farmland (0,0 · T4 reaching T5 · HARD — swarm warfare)

Crops → grazers → locust outbreaks → crop beetles. Most species dangerous in numbers.

| species id | category | behavior (short) | drop(s) — new ids | carcass |
|---|---|---|---|---|
| `locust` | swarm | Massive coordinated swarms that roll a wall of damage; scatter under AoE, re-form | `locust_wing`, `swarm_essence` | — |
| `grasshopper` | predator | Big solo/loose-pack ambusher; long leap-charges + knockback, heavy bite | `grasshopper_leg` (+`chitin`) | — |
| `cricket` | swarm | Nocturnal; swarms & aggros at night; its song reinforces a nearby locust swarm | `cricket_song_organ` | `dead_cricket` |
| `crop_beetle` | solo | Armored slow grinder; **eats placed crops & wooden structures** (wrecks your farm) | `crop_beetle_shell`, `beetle_mandible` | — |
| `mantis` ⭐ | **mini-boss / apex** | Ambush mantis elite; picks off stragglers & players, fast reaping strike + crit (rare spawn at swarm peaks) | `mantis_scythe`, `reaper_chitin` | — |
| `nymph` | swarm | Juvenile locusts; fast/weak fodder that inflates density & **matures if left alive** | `nymph_husk` | — |

**MINI-BOSS / apex elite:** `mantis` (the swarm-peak "oh no" elite). None existing-in-code.

## Millipede Forest (0,1 · T4 reaching T5 · HARD — premium lumber + chitin armor)

Deep old-growth; logging + big-beetle carapace armor + the stag-horn weapon.

| species id | category | behavior (short) | drop(s) — new ids | carcass |
|---|---|---|---|---|
| `giant_millipede` ✅ | solo | Long armored detritivore; curls when struck, secretes a `cyanide`-class `noxious` cloud | `millipede_segment`, `defensive_toxin` | `dead_millipede` |
| `forest_centipede` | predator | Bigger/faster ground hunter; flanks from litter, venom bite → `poisoned`, re-flanks | `forest_centipede_fang` (+`chitin`) | `dead_centipede` |
| `bark_beetle` | swarm | Wood-borers; swarm a bored tree, erupt in a chip-damage cloud when disturbed | `bark_beetle_jaw`, `bored_bark` | `dead_beetle` |
| `stag_beetle` | predator | Iconic bruiser; huge mandible "antlers", charges to grapple-and-throw (big knockback) | `stag_horn`, `beetle_carapace` | `dead_beetle` |
| `rhino_beetle` ⭐ | **mini-boss / apex** | Enormous horned bruiser on the great rotten log; summons `bark_beetle` swarms, single-horn charge | `prime_carapace` (guaranteed), `rhino_horn` | `dead_beetle` |
| `forest_snail` | solo | Big timber snail grazing bracket fungus (bonus/flavor calm catch) | `timber_shell` (+`snail`) | — |

**MINI-BOSS / apex:** `rhino_beetle` (the only `prime_carapace` source). `giant_millipede` is the existing-in-code species.

## Spider Vale West (0,2 · T4 reaching T5 · EXTRA HARD — silk + web + agility)

Premium silk economy; dodge-and-mobility under web ambush. Three-tier silk + hotter venom.

| species id | category | behavior (short) | drop(s) — new ids | carcass |
|---|---|---|---|---|
| `orb_weaver` | predator | Web-anchored ambusher; drops on a dragline & strikes when you snag the web (premium-silk source) | `orb_silk`, `spider_venom` | `dead_spider` |
| `wolf_spider` | predator | No web — a ground rusher; stalks then sprints the last gap; loose packs | `wolf_fang`, `spider_venom` (+`chitin`) | `dead_spider` |
| `jumping_spider` | predator | Ledge-perched; pounces across a gap then dodges away (very high dodge) | `jumping_spider_eye` (+`spider_silk`) | `dead_spider` |
| `armored_centipede` | predator | Hardened plated centipede; coils, anchors, lashes a venom bite (tanky bruiser) | `centipede_plate`, `centipede_venom` | `dead_centipede` |
| `web_tender` | swarm | Small cellar spiders that re-spin cut webs; fragile cluster catch (keeps webs coming back) | `cobweb` (+`spider_silk`) | `dead_spider` |
| `vale_broodmother` ⭐ | **mini-boss** | Bloated broodmother orb-weaver on the great cave-mouth web; spawns `wolf_spider`/`web_tender` adds, web-snare AoE + venom-spray | `silk_gland` (guaranteed), `broodmother_silk`, `spider_egg_sac`, `matron_fang` | `dead_spider` |

**MINI-BOSS:** `vale_broodmother` (id `vale_matron`/`vale_broodmother` — beating her opens the premium-silk
motherlode). None existing-in-code (`armored_centipede` is a hardened centipede variant).

## Spider Vale East (0,3 · T5 · EXTRA-EXTRA HARD — endgame surface gauntlet)

The hardest surface zone; deadly stacking venom + web-ambush + darkness. Best surface gear lives here.

| species id | category | behavior (short) | drop(s) — new ids | carcass |
|---|---|---|---|---|
| `black_widow` | predator | Web-anchored in dark corners; drops on a line & bites → heavy stacking `envenomed` (worst DoT) | `widow_venom` (+`spider_silk`, `web_silk`) | `dead_spider` |
| `tarantula` | solo | Big slow tanky ground spider; flicks urticating hairs (irritant cloud) then heavy fanged bite | `tarantula_hair` (+`chitin`, `venom_gland`) | `dead_spider` |
| `trapdoor_spider` | predator | Hidden under a hinged lid; bursts out, grabs & drags toward the pit (knockback-into-fall) | `trapdoor_silk` (+`spider_silk`, `trapdoor_lid`) | `dead_spider` |
| `spiderling_swarm` | swarm | The widows' brood; dense clusters pour from an `egg_sac`, biting for small stacking `envenomed` | `spiderling_cluster`, `egg_sac` | — |
| `giant_huntsman` ⭐ | **mini-boss / apex** | Huge fast **free-roaming** huntsman (comes to you); skitter-charges + heavy `envenomed`, phase-2 wall-runs + venom-mist | `huntsman_fang` (guaranteed), `royal_silk`, `potent_venom`, `huntsman_carapace`, `huntsman_eye` | `dead_spider` |

**MINI-BOSS / apex:** `giant_huntsman` (no anchor — hunts you across the hollow; the hardest surface fight).
None existing-in-code.

---

# UNDERGROUND

## Ant Colony (underground 0,3 · T2–T3 · EASY→MEDIUM — underground intro)

The friendly organized colony; darkness + fungus farming + formic alchemy debut. Row 4 ends at the Queen.

| species id | category | behavior (short) | drop(s) — new ids | carcass |
|---|---|---|---|---|
| `garden_ant` | swarm | Reused worker; tends fungus gardens on pheromone trails; swarms the crumb, not you | `ant_egg`, `formic_dab` | `dead_ant` |
| `black_ant` | swarm | Colony haulers; carry forage in long supply columns; ignore the player | `ant_fungus`, `formic_dab` | `dead_ant` |
| `harvester_ant` | solo | Big red seed-harvester anchored to a `seed_cache`; slow/stubborn, bites if you grab the cache | `harvester_mandible`, `seed_husk` (+`chitin`) | `dead_ant` |
| `soldier_ant` | predator | Armored guard at deep-gallery mouths; flanks, bites hard, sprays formic acid (`acid_burn`) | `soldier_chitin`, `formic_acid` (+`chitin`) | `dead_ant` |
| `colony_queen` ⭐ | **mini-boss** | Bloated egg-layer in the royal chamber; spawns `soldier_ant` adds, mandible slam + formic-spray AoE | `royal_jelly_ant` (guaranteed), `queen_chitin`, `royal_pheromone` (+`ant_egg`) | — |

**MINI-BOSS:** `colony_queen` (the royal chamber, bottom of row 4). None existing-in-code (`garden_ant` here is a
reuse of the village ant concept, not the sim species).

## Centipede Cavern (4,1 · T3 reaching T4 · HARD — deep cavern + glowworm light + fast venom)

True cave: glowworm light (best natural light), fast giant centipedes, crystal accessories.

| species id | category | behavior (short) | drop(s) — new ids | carcass |
|---|---|---|---|---|
| `giant_centipede` ✅ | predator | Long fast aggressive hunter; flanks from the dark, venom forcipule bite → strong `envenomed`, re-flanks | `centipede_venom_gland` (+`centipede_parts`, `chitin`) | `dead_centipede` |
| `glowworm` | solo | Ceiling colonies; the cavern's light — harvest a colony for the best natural light material (reach-up gather) | `glowworm_lumen`, `glow_silk` | `dead_glowworm` |
| `cave_beetle` | solo | Blind floor beetle; trundles slowly, curls under a thick wing-case when struck (patience/armor catch) | `cave_beetle_carapace` (+`chitin`) | `dead_beetle` |
| `camel_cricket` | swarm | Pale spider-crickets clinging to walls; spring in erratic leaps (jittery cluster catch) | `camel_cricket_leg` (+`chitin`) | `dead_cricket` |
| `centipede_matron` ⭐ | **mini-boss / apex** | Bloated segment-armored brood-mother in the great crevice den; spawns `giant_centipede` adds, heavy bite + charge | `potent_centipede_venom` (guaranteed), `matron_forcipule` | `dead_centipede` |

**MINI-BOSS / apex:** `centipede_matron`. `giant_centipede` is the existing-in-code species (the sim centipede).

## Underground Passages (3,1 · T3 · MEDIUM–HARD — the core mining hub / gateway)

The real mining zone: light, dig-deeper pick, ore/gem processing, the mine-cart haul loop. A connecting hub.

| species id | category | behavior (short) | drop(s) — new ids | carcass |
|---|---|---|---|---|
| `springtail` | swarm | Tiny jumpy detritivores; boil up in clouds, **light-shy** (your lamp scatters them), re-form | `springtail_dust` | `dead_springtail` |
| `blind_beetle` | solo | Eyeless pale grinder; trundles by feel, wedges into cracks when struck (high defense, ignores light) | `blind_beetle_shell` (+`chitin`) | `dead_beetle` |
| `mole_cricket` | predator | Burrowing bruiser; erupts from the wall to shove & gnaw (knockback charge) then re-burrows; drawn to your mining | `mole_cricket_claw` (+`soft_stone`) | `dead_cricket` |
| `cave_spider` | predator | Pale ambusher; drops from the ceiling on silk, bites for a `venomed` DoT, then skitters (bright lamp holds them off) | `cave_spider_silk`, `spider_venom` | `dead_spider` |
| `glow_grub` | solo | Fat luminescent larva clinging to gem veins; a living vein-marker, pure forage catch (the `vein_sense` tutorial) | `glow_sac` (+`glow_grub` body, `raw_gem`) | — |

**No mini-boss** (a connecting hub — the keystone set is a deep-gallery FIND, not a boss). None existing-in-code.

## Underground River (3,2 medium → 4,2 hard · T3–T4 — underground aquatic)

Cave fishing in the dark, freshwater pearls/gems, glowing & blind-albino fauna; light + cold-current hazard.

| species id | category | behavior (short) | drop(s) — new ids | carcass |
|---|---|---|---|---|
| `cave_crayfish` | solo | Scuttles the river bed; pincered & territorial, snaps when cornered but doesn't chase | `crayfish_claw`, `crayfish_shell` | `dead_crayfish` |
| `water_beetle` | swarm | Diving beetle; rows the river in bursts, dives when threatened; lake swarms (cluster catch) | `water_beetle_shell`, `beetle_air_sac` | `dead_beetle` |
| `aquatic_larva` | swarm | Caddis grubs in pebble cases on the bed; slow cluster dive-catch (the prime fishing-bait source) | `larva_case`, `aquatic_grub` | `dead_larva` |
| `albino_isopod` | solo | Blind ghost-white cave isopod; curls when disturbed (the "everything went white & blind" patience catch) | `albino_chitin`, `cave_detritus` | `dead_isopod` |
| `glow_mayfly` | swarm | Bioluminescent mayfly; soft glowing lake clouds (the living lantern + `light_radius` reagent; rare blue morph) | `glow_gland`, `mayfly_wing` | `dead_mayfly` |
| `blind_cave_fish` | solo | Eyeless pale fish; senses vibration, bolts at a clumsy approach (the **fishing** target — rod/spear/trap, not net) | `blind_fish_scale`, `fish_fillet` | `dead_fish` |
| `cave_crab` ⭐ | **mini-boss / apex** | Big pale armored crab guarding the sunken-ruins treasure; ambushes from a flooded alcove, crushing claw (T4) | `cave_crab_carapace`, `crab_claw` | `dead_crab` |

**MINI-BOSS / apex:** `cave_crab` (the treasure-guard — its carapace builds the Cave-Diver set). None existing-in-code.

## Deadly Ants (outpost 3,3 HARD → core 4,3 EXTRA HARD · T4–T5 — fire/acid swarm-warfare capstone)

A militarized super-colony at war; fire-resist becomes mandatory, acid eats armor. (Reuses Ant Colony ids.)

| species id | category | behavior (short) | drop(s) — new ids | carcass |
|---|---|---|---|---|
| `army_ant` | swarm | Dense marching **river** that never stops; bivouacs when provoked then resumes; out-attrits you en masse | `army_ant_mandible` (+`chitin`) | `dead_ant` |
| `fire_ant` | swarm | Cluster-attacker; bites then sprays igniting venom → `scorched`; dying ants leave `ignited` floor patches | `fire_ant_gland` (+`formic_acid`) | `dead_ant` |
| `soldier_ant` | predator | Armored bruiser; huge mandibles, heavily plated, telegraphed shear-bite + knockback (guards the choke) | `soldier_ant_plate` (+`chitin`) | `dead_ant` |
| `bullet_ant` | solo | Single-sting killer; does NOT swarm but its sting is the most lethal single hit — heavy `envenomed` + `stagger` | `bullet_ant_stinger` (+`venom`) | `dead_ant` |
| `war_queen` ⭐ | **mini-boss** | Bloated armored matriarch (core 4,3); hatches `army_ant` rivers + `fire_ant` clusters, then acid-spray + fire-breath cone | `war_queen_chitin` (guaranteed), `queen_venom`, `royal_jelly` (+`ant_egg`) | `dead_ant` |
| `ant_worker` / `ant_scout` | — | Ambient column traffic / carrion labor (reused, no new drops) | — | `dead_ant` |

**MINI-BOSS:** `war_queen` (the War-Queen's brood-fortress in the EXTRA-HARD core, 4,3). None of the elite ants
existing-in-code.

---

# Drop → ingredient map

The signature new drop ids, what each crafts, and the station. (Existing/reused drop ids like `pollen`,
`honey`, `chitin`, `venom_sac`, `wasp_stinger`, `centipede_parts`, `leech_extract`, the `dead_*` carcasses,
metal bars, etc. are not re-listed here — they feed the established material ladder; see the per-zone sheets.)

| drop id | what it crafts (use) | station(s) |
|---|---|---|
| `fly_clump` | premium bug-farm bait, fishing bait | workbench |
| `ladybug_shell` | luck charm, décor inlay, red dye | jeweler / dye_vat |
| `aphid_cluster` | compost, ladybug bait, fertilizer | compost_bin / workbench |
| `honeydew` | cooking sweetener, ant/sweet bait | cooking_pot / workbench |
| `pill_chitin` | light-armor plating (Forager's vest, pill_plate_buckler) | workbench / loom |
| `leaf_litter` | compost, growth mulch, gardener_gloves | compost_bin / loom |
| `snail_shell` | décor, lime/grit (stonecutter), shell_lamp | stonecutter / workbench |
| `mud_daub` | bee_hotel build/repair, clay-like binder | workbench |
| `leaf_disc` | meadow `fiber` substitute (wax_wrap, soft crafts) | loom |
| `bumble_fuzz` | pollinator-outfit lining, felt cloth, hand_pollinator brush | loom / workbench |
| `bumble_nectar` | premium honey/mead/cooking sweetener; meadow_mead | honey_extractor / keg / cooking_pot |
| `carpenter_resin` | wood-oil sealant (waterproof armor, wax_wood_polish, frame binder) | cauldron / sawmill |
| `hornet_venom` | T3 venom weapons/coatings, antivenom, venom_bomb | forge / cauldron |
| `hornet_carapace` | T3 carapace armor (apiarist_gauntlets), hornet_trophy, jeweler inlay | anvil / jeweler / workbench |
| `cabbage_caterpillar` | pest_lure (caterpillar bait) | cauldron |
| `silk_thread` | light wild silk (pollinator weave, nets, royal_candle) | loom |
| `butterfly_scale` | shimmer dye, luck_charm, scale décor | dye_vat / jeweler |
| `monarch_scale` | best shimmer dye, monarch_brooch (jeweled rare-luck), specimen value | jeweler / dye_vat |
| `glass_scale` | prism_dust (→ prism gear), glasswing_lens, prism_window | jeweler |
| `moth_silk` / `emperor_silk` | spun → `silk` → moth/emperor cloth → T2–T3 silk gear | loom |
| `luna_dust` | glow-dye, nightsight_tonic | dye_vat / cauldron |
| `eyespot_scale` | intimidation/`dodge` trinket, décor | jeweler |
| `firefly_lumen` | the light-gear line (firefly_lantern, glow-armor, lumen_jar) | workbench / loom |
| `firefly_dust` | glow paint/dye, glow_lure, resin_torch | dye_vat / cauldron |
| `cicada_shell` | springy plate (`dodge`/`fall_resist`), calm_chime, cicada_chime | workbench |
| `cicada_wing` | translucent décor inlay, glide trinket | workbench / jeweler |
| `hawkmoth_silk` | lightest silk for the speed trinket; high `bug_value` sale | loom |
| `mud_dauber_clay` | mud-dauber-themed gear, clay supply | workbench |
| `silverfish_scale` | (vendor sell / light crafting) | — |
| `earwig_pincer` | (vendor sell / light crafting) | — |
| `royal_venom` | rare/upgraded venom — forward hook to T3 venom weapons | forge / cauldron |
| `damselfly_wing` | gossamer cloth, lily-glide trinket (damsel_pin), dye | loom / jeweler |
| `skater_oil` | hydrophobic water-walk coating (marsh_waders, skater_boots) | workbench / loom |
| `whirligig_shell` | wader light carapace plating; whirligig_lens (night/clarity) | workbench / jeweler |
| `mosquito_proboscis` | weak poison coating / bait reagent | cauldron |
| `scorpion_venom` | strong venom weapons/coatings (scorpion_pick, venom_oil), antivenom | forge / cauldron |
| `scorpion_claw` | pincer tools/weapons, miner-grip pieces, quartz_pendant | anvil / forge / jeweler |
| `tick_sac` | HP-leech/lifesteal coating, bait, tick_repellent | cauldron |
| `harvestman_leg` | springy cordage → miner harness/climb gear (`fall_resist`, reach) | anvil / loom |
| `vinegaroon_acid` | gem-cut etch agent (cut_quartz), armor-shred throwable | jeweler / cauldron |
| `potent_venom` | marquee venom weapon (venom_lash) + forward hook to next tier | forge |
| `mosquito_venom` | T3 venom coatings, fever-bombs, bait | cauldron |
| `dragonfly_wing` | glider/wing-cloak (dragonfly_glider), fast-attack reagent, gossamer cloth | jeweler / loom |
| `dragonfly_eye` | clarity/sight lens → night_vision + catch trinkets (dragoneye_lens) | jeweler |
| `nymph_jaw` | edged weapon component (nymph_glaive) | forge |
| `strider_leg` | deep water-walk reagent → strider_striders, harpoon_gun part | workbench / anvil |
| `strider_oil` | richer hydrophobic wax → deep waterproofing, diver seal | cauldron / workbench |
| `giant_waterbug_carapace` | apex armor plate → Bog-Hunter set, toebiter_maul | anvil / forge |
| `waterbug_venom_gland` | potent T4 venom weapon-coat + disease-cure base (fever_cure) | cauldron |
| `serpentfly_scale` / `serpentfly_ichor` | elite alchemy line (serpent_elixir), glow charm, dye | cauldron / jeweler |
| `locust_wing` | swarm-warden armor, lure/bait, swarm_essence render | anvil / cauldron |
| `swarm_essence` | the AoE swarm-weapon charge + swarm-LURE core | cauldron / forge |
| `grasshopper_leg` | mobility/knockback gear (springstep_boots), locust_oil, hearty food | anvil / cauldron |
| `cricket_song_organ` | swarm-LURE tech, sonic/`calm`-counter (chorusbreaker_charm), music décor | jeweler |
| `crop_beetle_shell` | heavy crop-defense plating, warden body armor (cropwarden_buckler) | forge |
| `beetle_mandible` | harvest_sickle edge, grinder station part | anvil |
| `mantis_scythe` | high-end swarm-clearing weapon edge (swarm_culler), trophy | forge |
| `reaper_chitin` | swarm-warden set capstone plating (wardens_aegis) | forge |
| `nymph_husk` | cheap bulk filler (mulch, paper-chitin, bait extender), nymph_mulch | compost_bin / workbench |
| `millipede_segment` | segmented flex-plating (warden_greaves), thorns trinket | anvil |
| `forest_centipede_fang` | venom coating (venom_coat), barbed_dagger/thorns reagent | cauldron / anvil |
| `bark_beetle_jaw` (+`bored_bark`) | bark/fungus alchemy line, rustic décor | cauldron |
| `stag_horn` | the iconic horn melee (stag_horn_maul, horned_glaive), warden pauldron spikes | forge / anvil |
| `beetle_carapace` | Carapace Warden plating, chitin_buckler, carved_throne inlay | anvil |
| `prime_carapace` | keystone warden body plate (apex) + T5 hook | anvil |
| `rhino_horn` | upgraded apex horn weapon (rhino_breaker, T4→T5) | forge |
| `defensive_toxin` | antitoxin, venom_coat, thorns_draught (millipede secretion) | cauldron |
| `timber_shell` | décor, lime/grit | stonecutter / workbench |
| `orb_silk` | premium cloth bolt (→ refined_silk → spider_silk_cloth) — the silk spine | loom |
| `cobweb` | web-trap structures (web_trap), binder, net-mesh, décor stuffing | workbench / loom |
| `spider_venom` | strong venom weapons/coatings (fang_dagger, venom_oil), antivenom | forge / cauldron |
| `centipede_venom` | paralytic slow/stun weapon coating (paralytic_coating), trap charge | cauldron / workbench |
| `silk_gland` | loom catalyst — spins raw thread into top-grade `refined_silk` (gates T5) | loom |
| `broodmother_silk` | T5 marquee cloth/cape (stalker_cape) + artisan flex bolt | loom |
| `wolf_fang` | fanged daggers/spears (fang_dagger) + grip pieces | forge / loom |
| `jumping_spider_eye` | `crit`/precision charm (stalkers_charm), scope lens | jeweler |
| `centipede_plate` | light flexible armor plating (silk-stalker), venom_glaive | forge / loom |
| `widow_venom` | strongest venom weapons/coatings (widowfang_blade, venom_draught), widow_bomb | forge / cauldron |
| `tarantula_hair` | urticating throwable + barbed `thorns` armor lining (widow_shroud) | cauldron / loom |
| `trapdoor_silk` | densest silk → endgame silk armor body + heavy net/trap line (silk_repeater) | loom / forge |
| `royal_silk` | the endgame silk (→ royal_silk_cloth) — Widow's set keystone | loom |
| `huntsman_fang` | marquee weapon fang-blade (widowfang_blade) + apex accessory (huntsman_charm) | forge / jeweler |
| `huntsman_eye` | apex accessory input (huntsman_charm) | jeweler |
| `ant_fungus` | the fungus food chain (fungus_bread/stew/jerky) + fungus-leather binder | cooking_pot / loom |
| `harvester_mandible` | pincer-grip tools (light dig pick) + the colonist gauntlet | anvil / jeweler |
| `soldier_chitin` | ant-chitin light armor plating (Colonist's Carapace) | anvil / loom |
| `seed_husk` | granary-chaff compost / fertilizer (colony_compost), feed | compost_bin |
| `formic_acid` | formic-acid alchemy (acid_flask, formic_etch), strong tier | cauldron |
| `queen_chitin` | keystone colonist armor + royal trophy/décor | loom / jeweler |
| `royal_pheromone` | colony-command consumable (pheromone_whistle — calm/lure ants) | cauldron |
| `royal_jelly_ant` | marquee buff food (royal_jelly_tonic) + Queen-tier alchemy | cooking_pot |
| `centipede_venom_gland` | fast venom weapons (centipede_fang_blade) + coating (venom_oil) | forge / cauldron |
| `glowworm_lumen` | best natural light gear (glowworm_lantern, lumen_torch, set inlay) | workbench / loom |
| `glow_silk` | luminous thread (glow_thread) → glow-textile + light décor | loom |
| `cave_beetle_carapace` | Deep Delver armor plating + chitin_buckler | anvil |
| `camel_cricket_leg` | springy cordage → delver greaves/boots (`fall_resist`/`move_speed`) | anvil |
| `potent_centipede_venom` | marquee apex venom weapon (venom_lash) + T4 hook | forge |
| `matron_forcipule` | heavier venom-weapon variant + wall trophy | forge |
| `springtail_dust` | luminescent light reagent (cave_headlamp), cheap dye, fungus bait | workbench / dye_vat |
| `glow_sac` | cold-light gel — the `glow_lantern` fuel + cold-light décor | workbench |
| `blind_beetle_shell` | spelunker plate (helm/body) + shell_buckler off-hand | anvil / workbench |
| `mole_cricket_claw` | deepcut_pick / fortune_drill / mine_cart dig-bit (`effective_tool_tier`) | anvil / forge |
| `cave_spider_silk` | spelunker weave (body/legs), hauling rope/harness, net & ore_sack | loom |
| `crayfish_claw` | edged-tool/weapon component (cave_harpoon barb), angler tackle, crayfish_charm | anvil / workbench / jeweler |
| `crayfish_shell` / `water_beetle_shell` | light aquatic carapace plating (Cave-Diver/Angler gear) | anvil / workbench |
| `beetle_air_sac` | `water_breath` reagent (bubble_rebreather, cave_breathing_potion) | workbench / cauldron |
| `larva_case` / `aquatic_grub` | `aquatic_grub` = prime fishing bait; `larva_case` = grit/abrasive (pearl-polish) | workbench / jeweler |
| `albino_chitin` | pale light/clarity plating & charm core (angler set) | anvil / jeweler |
| `glow_gland` | the `light_radius` reagent (glow lures/lamps, glow_charm, glow alchemy) | workbench / jeweler / cauldron |
| `mayfly_wing` | luminous trinket, fast-attack reagent, glow-dye | jeweler / dye_vat |
| `blind_fish_scale` | luck/clarity reagent → `rare_bug_luck`/catch trinkets (glowscale_lens), pearl dye | jeweler / dye_vat |
| `cave_crab_carapace` | apex armor plate (divers_carapace) + crab trophy charm | anvil / jeweler |
| `crab_claw` | anti-apex weapon component | forge |
| `army_ant_mandible` | swarm-breaker AoE weapon (mandible_maul) + swarm-defense (swarm_repeller) | forge / cauldron |
| `fire_ant_gland` | fire weapons/coatings (`scorched`) AND fire-resist armor temper (flame_alloy, fireguard_cloak) | forge / cauldron |
| `soldier_ant_plate` | endgame heavy armor (Legionnaire) → `elite_chitin` intermediate | forge |
| `bullet_ant_stinger` | venom-crit sidearm (bullet_sting_dagger) + acid_lance | forge |
| `war_queen_chitin` | Fire-Warden set keystone (firewarden_crown) + trophy | jeweler |
| `queen_venom` | hottest endgame venom coating/weapon | forge / cauldron |
| `royal_jelly` | endgame luck/regen consumable (acid_balm) + set accessory inlay | cauldron / jeweler |

---

# Totals & new-vs-existing

**Total species across the 17 zones:** **84** distinct catchable/fightable species rows
(including the two ambient ant labor castes `ant_worker`/`ant_scout` counted as one row in Deadly Ants).

Per-zone counts: Village 6 · Bee Meadow 5 · Wasp Thicket 5 · Shallow Swamp 6 · Hilltop Meadow 5 ·
Butterfly Fields 8 · Scorpion Rocks 5 · Deep Swamp 7 · Locust Farmland 6 · Millipede Forest 6 ·
Spider Vale West 6 · Spider Vale East 5 · Ant Colony 5 · Centipede Cavern 5 · Underground Passages 5 ·
Underground River 7 · Deadly Ants 6 (5 + the ambient `ant_worker`/`ant_scout` row).

**Already exist in code (6):** `fly` (Village `fly_common`), `butterfly` (Butterfly Fields `butterfly_meadow`),
`wasp` (Wasp Thicket / Hilltop Meadow `paper_wasp` ≈ `wasp_common`), `giant_centipede` (Centipede Cavern;
also the surface `centipede` / `centipede_garden`), `giant_millipede` (Millipede Forest `millipede`), and the
**carrion beetle** decomposer (`beetle_carrion`, the `dead_beetle`/carcass-eater in the sim). Note `paper_wasp`
appears in **two** zones (Wasp Thicket as a threat, Hilltop Meadow re-cast as a pest-control ally) but is the
single existing `wasp` species.

**New / design-only:** the remaining **~78** species rows are unbuilt — they exist only as design in the zone
sheets and are the content backlog the per-zone gear, drops, and mini-boss fights hang on. Of these, **16 are
flagged MINI-BOSSES** (one per combat zone that has a flagged boss): `thicket_matriarch`, `hornet`, `den_matron`,
`giant_water_bug`, `mantis`, `rhino_beetle`, `vale_broodmother`, `giant_huntsman`, `colony_queen`,
`centipede_matron`, `cave_crab`, `war_queen` — plus the apex/elite threats that double as the zone's hardest
fight (`bog_centipede` apex, `bullet_ant` single-sting killer). Zones with **no** mini-boss: Village, Bee Meadow,
Butterfly Fields, and Underground Passages (the last gates its keystone via a deep-gallery FIND instead).
