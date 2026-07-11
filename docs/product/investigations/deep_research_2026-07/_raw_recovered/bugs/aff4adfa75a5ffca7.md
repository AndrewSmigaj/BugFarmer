I'll mine the design material for the Ant Colony + Queen zone. Let me start by locating all the relevant files in parallel.

---

Now the brainstorm files, the superseded demo, and the ecology proposal.

---

Now the landmark/flora/decoration/trees brainstorms and the ecology proposal, plus checking for the referenced live docs and decisions.

---

Now the ecology proposal, DECISIONS.md (for D21), and checking for the referenced live docs.

---

Let me read the D21 decision context, the authoring guide, and search for the owner's 2026-07-06 quotes (scripted queen, block-built, ant_brood).

---

Let me hunt for the owner's 2026-07-06 quotes (scripted queen, block-built colony, brood anchors) across the docs and any design log.

---

Let me find the specific owner 2026-07-06 notes about the scripted queen, block-built colony, and brood anchors.

---

Let me read the ant-colony authoring guide and the relevant architecture_world.md sections.

---

Let me pull the design_ants_spiders.md (queen/nest mechanics) and confirm the grid-edge/centipede context.

---

Let me locate the owner's "Queen scripted like a game" quote and confirm the Myrmecologist/royal-jelly merchant seams.

---

I have everything needed. Here is the digest.

---

# ANT COLONY + QUEEN — (4,0) MEDIUM — design digest

Scope note: the (4,0) queen zone has **no dedicated live doc yet**. The referenced `ant_colony_40.md`/`ant_tunnels_30.md` do NOT exist — `docs/product/zones/ant_colony.md` is the SUPERSEDED demo, and the row-4 material lives inside the combined economy sheet + the architecture grid + brainstorms. Two conflicting id-sets exist (flag below).

## HARD OWNER DECISIONS (D-entries / owner quotes / architecture with owner attribution)
- **Grid & ownership (D2/D3/D9; `product/zones/ant_colony.md:3-8`):** ants own **col 0** — Ant Tunnels **(3,0)** + **Ant Colony w/ Queen (4,0)**. Colony sits in the **SW zone**; scout tunnels above lead outside, south of the bee zone.
- **D21 (`economy/DECISIONS.md:228-232`):** **scout ants = top of western ant zone (3,0)**, forage far; **warrior ants = lower-left (4,0)**. Ants **spawn in col-0 and CROSS OVER** into the Mining Camp via dirt tunnels (not spawned in the camp). "Ant species still need building."
- **NO mounds/hills — BLOCK-BUILT (owner 2026-07-06; `authoring/ant-colony.md:13-17`, `architecture_world.md:144`):** "there is no such thing as ant mounds or hills — these are made from our dirt blocks, the blocks literally form these and the tunnels." Mound MOUTHS + tunnels are **`dirt_block`**; the `ant_mound` OCCUPANT is **DEPRECATED** — never place it.
- **Nest ANCHOR = `ant_brood` (owner 2026-07-06; `authoring/ant-colony.md:18`, `architecture_world.md:144,275,636`):** nests anchor on **`ant_brood`** (pale egg pile) — the sim hook `NestState` keys off (`speciesForNestOccupant`). **Structure is blocks; life is the brood.** `ant_brood` = 1×1, mined w/ Shovel, drops `ant_egg` ×1-2; it **replaces deprecated `ant_mound`**.
- **Colony Queen tier (`architecture_world.md:143-149`):** **medium tier (row 4) holds the Colony Queen** — a **mid-game mini-boss + ant guards**, DISTINCT from the deferred **grand Ant Queen Chamber boss** (returns with row 5). Row 4 also compresses the rarest ores.
- **Edges (`underground_passages_31.md:97-102`):** (3,1) Passages connect **West → Ant Tunnels (3,0)** and **South → Centipede Cavern (4,1)**. So (4,0)'s **east neighbor is Centipede Cavern (4,1)** — the centipede-raid seam.
- **Sim design APPROVED-but-set-aside (`ecology/design_ants_spiders.md`, "DESIGNED NOT BUILT 2026-06-23"):** colony = reuse of `NestState`+`BroodState`. Sim ids: `ant_hill`(→`ant_brood`), **`ant_queen`** (stationary, provisioned brood→eggs→hatch workers/scouts), **`ant_scout`** (registers carrion sites), **`ant_worker`** (forage→carry→deposit, reuses wasp provisioning), later `ant_leafcutter`, `ant_soldier`. **Colony memory = emergent trail** (server-only soft state, no new ledger). Build phasing: colony core → memory/scouts → leafcutter/soldier → production zone.

> **⚠ Queen "scripted like a game" tension:** the literal phrase isn't in docs — it captures a real conflict. The economy sheet frames `colony_queen` as a **scripted mini-boss encounter** (emits `soldier_ant` adds from brood piles until you break them, then mandible slam + formic-spray AoE ground hazard, gear-gated). The sim design frames `ant_queen` as an **emergent egg-layer**. The boss fight is a scripted layer ON the brood-anchor sim.

## DRAFT / CANDIDATE — species (assistant-authored, `economy/zones/ant_colony.md`, "design only")
Note: sheet is headed **(3,0) row-3 EASY→MEDIUM** but explicitly states **"row 4 is medium and ends at the `colony_queen` mini-boss"** — the row-4 slice is soldier_ant + colony_queen. Ids here (`garden_ant`/`black_ant`/…) diverge from the sim's `ant_worker`/`ant_scout` — needs reconciliation.
- **v1 DECIDED baseline (per D21):** worker (scout `ant_scout`@3,0 + warrior/soldier@4,0). Queen scripted.
- **Caste ladder as LATER-CANDIDATES (sheet):** `garden_ant`✅(reuse, tends fungus), `black_ant` (haulers, spill `ant_fungus`), `harvester_ant` (stubborn, anchors `seed_cache`, bites if you grab cache), `soldier_ant` (**core row-4 threat** — guards deep galleries + royal approach, formic-acid `acid_burn`), **`colony_queen`** (mini-boss).
- **Deeper caste-brainstorm candidates (`brainstorms/bugs/ant_colony.md`):** `ant_leafcutter`, `ant_minor` (tends fungus/grooms), `ant_nurse`, `ant_drone`/`ant_queen_winged` (nuptial-flight flavor), **`ant_repletes`** (honeypot living-larder — harvestable honeydew), `ant_larva`/`ant_pupa` (resource/bait), `ant_soldier_giant` (elite gatekeeper of queen approach).
- **Livestock/parasite candidates (medium-fit, hold most as later):** `aphid`(+winged/giant/red/woolly/herd), `scale_insect`, `mealybug`, `treehopper_tended`; parasites `parasitoid_wasp`, `phorid_fly` (ant-decapitator, harmless flavor), `nest_beetle_raider`, `rove_beetle_mimic`, `cordyceps_ant`, `antlion_larva` (trap-bug). **`centipede_hunter`** listed as a deep-tier wanderer leaking in from the caves — the (4,1) raid vector.

## CHAMBER TYPES & SPATIAL LOGIC (nest = tree of tunnels; `authoring/ant-colony.md:8-26`)
- Soil-dominant (`dirt_block` >> `stone_block`, no ore veins in the pure colony); **entrance = dirt-block mound mouth** over a 1-cell dark shaft; **narrow (1-cell) meandering main shaft** descends to the queen; **branches → rounded chambers (2-4 cells)**. Trails = files of ants (~every 2 cells on main shaft, 3-4 on branches; queen + 2-3 tenders per chamber).
- **Chamber roster:** **Queen's Chamber** (largest, deepest/central — arena for the mini-boss) · **brood chambers** (`ant_brood` anchors) · **food stores** · **fungus gardens** (terraced) · **aphid pastures**.
- Superseded-demo prose worth carrying (`product/zones/ant_colony.md`): **The Queen's Domed Hall**, **Brood/egg chambers**, **The Fungus Garden** (pale glowing terraces), **Aphid pastures** (root-wall + soldier guards), **THE GREAT TRUNK TUNNEL** (the colony highway, two worker columns streaming opposite ways), **The Abandoned Dig** (half-collapsed side tunnel, **crushed mine cart** on bent rails from the caves above).

## LANDMARK CANDIDATES (`brainstorms/landmarks/ant_colony.md` — DRAFT vignettes)
Royal/brood: **Queen's Domed Hall** (scene climax), **Royal Antechamber** (giant-soldier gatekeepers — the arena gate), **Brood Nursery**, **Pupae Vault**, **Nuptial Shaft**. Fungus: **Fungus Garden Terraces**, **Leafcutter Trail** (river of moving leaves), **Compost Pit**, **The Blighted Garden** (out-of-balance mold overrun), **Honeypot Ceiling** (replete larder). Aphid: **Aphid Pasture Wall**, **Weeping Root Pasture**, **Milking Station**. Tunnels: **Great Trunk Tunnel**, **Crossroads Chamber**, **Pebble Arch Gate**, **Ventilation Chimney**, **Deep Sump** (hints deeper zones). Grim relics: **Abandoned Dig** (crushed mine cart), **Lost Miner's Pack** (loot cache + still-lit lantern), **Sealed Breach**, **Ore-Studded Wall** (soldier-guarded gems — the deep-tier reward), **Boneyard** (refuse midden, cordyceps corpses). Eerie: **Cordyceps Cluster**, **Glowworm Curtain**, **Antlion Pit**, **Alarm-Scent Cloud** (event — the colony converges).

## FUNGUS-GARDEN / BROOD / FOOD-STORE VOCABULARY (DRAFT — flora/decor/trees)
- **Crop fungi:** `pale_brood_fungus`, `gromphadina_cap`, `gongylidia_nodes`, `staghorn_fungus`, `terrace_mycelium`, `gray_button_fungus`. **Glow fungi (the nest's light + alchemy):** `glowcap_lantern`, `foxfire_shelf`, `bluecap_glowmoss`, `ember_fungus`, `spore_lantern_pod`. **Rot/out-of-balance:** `creeping_white_mold`, `escovopsis_blight`, `dog_vomit_slime`, `weeping_fungus`. **Substrate:** `leaf_mash_substrate`, `chewed_leaf_pile`, `compost_terrace`.
- **Aphid pasture flora:** `root_tendril`, `sap_root_swollen`, `weeping_root_node`, `honeydew_dew`/`honeydew_pool`, `sooty_mold_film`, `gall_knot`.
- **Structure placeables (decor):** `clay_wall`/`dirt_wall`/`mud_brick_wall`, `pebble_arch`/`pebble_pillar`, `tunnel_buttress`, `dirt_ramp`, `clay_chimney`. Brood: `egg_cluster`, `egg_clutch_large`, `larva_pile`, `pupa_rack`, **`brood_cradle`** (royal brood, rare). Garden: `fungus_terrace`(+tall), `leaf_substrate_bed`, `compost_heap`, `glowcap_cluster`. Pasture: `aphid_root_wall`, `honeydew_drip`, `honeypot_hangers`, `milking_perch`. Trail texture: `ant_trail_groove`, `leaf_litter_scatter`, `food_cache`, `seed_husk_pile`, `prey_carcass`, `refuse_midden`. Relics: `crushed_mine_cart`, `broken_rail`, `snapped_timber`, `miner_pack`, `dropped_lantern`, `bone_scatter`, `sealed_breach_patch`. Many tagged **[tame→decor]** (husbandry payoff).
- **"Trees" (`brainstorms/trees`):** `great_root_pillar`/`taproot_descent` (vertical scale, "you dug beneath a forest"), `weeping_taproot` (doubles as aphid pasture), `root_arch`/`root_curtain`, fungal "trees" `glowcap_tree`/`bracket_tower`/`puffstalk`.

## LOOT / REWARDS LADDER (DRAFT — economy sheet, T2→T3)
- **Worker→guard→queen:** workers → `ant_egg`✅, `formic_dab`✅, `dead_ant`, `ant_fungus`✅; harvester → `harvester_mandible`✅, `seed_husk`, `chitin`✅; soldier → `soldier_chitin`✅, **`formic_acid`✅** (concentrated). Two-tier formic ladder (`formic_dab`→`formic_acid`).
- **Queen mini-boss drops:** **`royal_jelly_ant`✅** (guaranteed 1-2 — marquee tonic + Queen-tier alchemy reagent), **`queen_chitin`** (rare — keystone armor + wall trophy), `ant_egg`✅ ×3-5 (royal brood), **`royal_pheromone`** (colony-command reagent). Confirmed in `species_and_drops.md:230`.
- **Rewards spine:** light (`glow_lantern`→`glowquartz_lamp`), **fungus food chain** (`fungus_bread`→`fungus_stew` "eat the glow"→`royal_jelly_tonic`), **formic alchemy** (`formic_etch`, `acid_flask` anti-soldier throwable, `formic_salve` cure), **`pheromone_whistle`** (needs `royal_pheromone` — colony calm/follow), **`fungus_garden`** placeable (your own farm). **Signature set: "Colonist's Carapace"** (`colonist_helm/vest/boots`, ant-chitin light armor; set bonus = light + full acid-immunity + "colony treats you as kin"; vest is bought OR queen-dropped, with a `queen_chitin` royal variant).

## NPC / LOCATION CANDIDATES (DRAFT)
- **The Myrmecologist's Camp (`myrmecologist`)** — dedicated vendor at the **colony mouth** (safe surface entry). Teaches trails/fungus/formic/"the Queen is the prize"; sells first light gear, fungus-farm seeds, formic + survival recipes, keystone armor recipe; **trades ant-eggs**; buys fungus/chitin/formic high (over-harvest incentive); `royal_jelly_ant`/`queen_chitin`/`royal_pheromone` sell highest. (Realizes `merchants.md` NPC seam.)
- **The Ecologist (`ecology_proposal.md`)** — the balance-reader NPC; would surface colony health / destabilization as optional world-state quests.

## SECRETS / SURPRISE MATERIAL
- **Lost Miner's Pack** (loot cache, still-lit lantern, bones) · **Sealed Breach** (walled-off human breakthrough) · **Ore-Studded Wall** (soldier-guarded deep gems — richest reward) · **Cordyceps Cluster** / **Boneyard** (eerie) · **Antlion Pit** (buried trap-bug) · myrmecophile "huh what's that" finds (`rove_beetle_mimic` ant-scent predator, `pseudoscorpion` rider). Husbandry secret: **learn to ranch aphids/honeydew yourself** (the emergent farmable trick — `ecology_proposal.md §4`, bugs-brainstorm hook).

## THREATS & EDGE CONTRACTS
- **Core threats:** soldier ants (formic `acid_burn` guards — the row-4 fight) + the scripted Queen (soldier adds from brood, mandible slam, formic-spray AoE floor). Superorganism alarm: harming any caste rallies soldiers (`brainstorms/bugs` notes).
- **Centipede raids from (4,1) EAST:** (4,1) = Centipede Cavern (`underground_passages_31.md`, `architecture_world.md:152`). `centipede_hunter` explicitly leaks down the tunnels to prey on workers (`brainstorms/bugs:117`) — the east-edge raid vector; cave centipede reuses the shipped centipede sprite (D21).
- **EDGE CONTRACTS:** **(3,0) ABOVE** = Ant Tunnels (scout ants, forage-out, tunnels rising to surface south of bee zone — the intro/easy approach into the colony). **(4,1) EAST** = Centipede Cavern (mine-through seam; centipede predators raid in). Forward hook: `royal_pheromone`/`queen_chitin` seed the deeper **col-3 Deadly Ants** command/gear toys.

## DEADLY ANTS (col 3) — what belongs THERE not here (`economy/zones/deadly_ants.md`, DRAFT)
Keep the two colonies distinct: col-3 is **T4→T5 endgame WAR-colony** — `army_ant` swarm-rivers, `fire_ant` burning-floor hazard (`scorched`/`ignited`), `bullet_ant` single-sting killer, armored bruiser soldiers, **`war_queen`** (EXTRA-HARD core 4,3) w/ acid-spray + fire-breath. Endgame mats `ember_resin`/`acid_crystal`/`magma_rock`/`elite_chitin`/`flame_alloy`, **Fire-Warden's Legion** set, **Exterminator's Base + Bounty Board**. (4,0) stays **friendly organized colony, no fire, no acid-floors, chitin LIGHT armor, formic ≠ corrosive war-acid.)