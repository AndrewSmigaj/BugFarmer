# Backlog

Running queue of upcoming work. Short notes only — each item gets its own plan when we start it.
**Now** = active, **Next** = teed up, **Later** = captured so we don't forget.

This is the durable queue. The throwaway plan doc covers only the single item we're actively
working; this file is what survives between sessions.

## Done (recent) — PREDATORS v1: wasps + nests, the centipede, player HP, first audio
- **Predation core** (architecture_swarm_sync §14 — the system of record): predators hunt
  prey SWARMS via ordinary legs + the existing BUG_REMOVED/SWARM_REPRODUCED/ITEM_ROTTED
  vocabulary — ZERO new ledger event types across the whole slice. SpeedMult per-leg
  multipliers (Move + emission, written by every emitter), flies_over_fences at BOTH
  collision sites, the movement-class determinism contract, carrion as hash-bearing food
  (ITEM_ROTTED at spawn, FOOD_CONSUMED(0) at expiry, def-driven client hydration).
- **Wasps**: chase kinematics that close (the closure test pins it), 3 HP, sting 1,
  large-net-only (the first net_size enforcement; hand-catching flies/butterflies
  preserved), hive trips (hunt → home → deposit → 125s rest), nest brood economy
  (+2/hatch, clamp 6, brood-drain re-hatch = 3 culls to dormancy), aggro-on-damage
  recall, orphan patrols, wasp_stinger drops. Village: ONE nest at (124,232) inside the
  fly-farm buffer.
- **Centipede**: a swarm-of-one with an ActionState machine (windup hiss → leading surge
  ×4.8 clamped + LOS-gated bite 2 → recover), serpentine wander with a graduated
  dead-end escape, carrion-first foraging + rare breeding, GNAW through wood (16s,
  audible past the night light radius — the night tell; stone immune; successful breaks
  chain layers), scattered centipede_parts, segment trail + segment-hit mapping
  client-side. Village test patch: forest at (90,225), cap 2.
- **Player HP v1**: 10 hearts, invuln, knockback, faint-respawn, regen, presence-targeted
  OpCode 94, first-damage toast naming the sword.
- **First audio**: runtime-synthesized AudioFx (thwack/pop/sting/thud/hiss/crunch) with
  the dedup rules; the gnaw crunch is the deep-night × predator cross-system moment.
- ~34 new Go tests (closure, speed parity, catch matrix, nest economy, surge lead,
  gnaw, escape — flake-checked 8x); sync-harness clean after every server phase.

## Later additions from this slice
- Subdue/drag/revive (smoke tool) — the centipede capture path (trap_only reserves it).
- Millipede: the peaceful detritivore on the same individual chassis (eats rot, makes
  compost). Dragonfly: prey:[wasp_common] — pure data + sprite (the chassis proof).
- Second wasp type (yellowjacket ground-nester); craftable hive box; roofed enclosures
  (blocks_flying); predator starvation (needed for finite-prey private plots);
  nocturnal centipede aggression; bee mass-sting damage scaling (per-swarm cooldown is
  the v1 cap); eat-fruit-to-heal (regen is the placeholder).
- Forest zone proper (docs/guides/authoring/forest.md collects the rules); village
  remake folds the test patches into real content.
- P8 curved legs (protocol bezier) — default-skipped; revisit only if the serpentine
  read disappoints; gate = sync-harness hash parity.
- spawnKillDrops directional scatter along the death trail (drops currently burst-jitter).

## Done (recent) — Orchard redesign + weather v1 + deep night/flashlight + F8 + ecology caps
- **F8 world-debug panel**: set time of day (epoch-compare rollover — a set-time can't skip
  the daily reset), force rain/stop, spawn a fly swarm at the player (cap-aware). OpCodes 90/91.
- **Rain v1**: 30%/day one 2.5-5min shower; one-shot watering of crops (daily cap) + fruit
  trees (the wild-orchard restock path); streak particles + overcast dim + ☔ clock glyph.
  NEW architecture_weather.md is the system of record.
- **Fruit tree TANK model**: 3 waterings (1 manual/day, == day gate) buy ONE batch of 4 that
  grows fruit-by-fruit onto the canopy; fruit never rots on the tree; HANDS (new visible
  slot-0 tool) left-click picks one; tool hits knock one down per hit; unpicked fruit sheds
  STAGGERED (≥50s apart) into the evening window; ground rot ~2 days. Canopy overlay =
  separate GOs (occupant GOs are POOLED — children would ride them); droplet now means
  "can drink today" and self-refreshes at rollover.
- **Ecology safety, 3 layers (architecture_swarm_sync §13)**: one-apple-per-breed food budget
  (consume 0.2, event cost 40); reproduction +1-2 randomized (NOT doubling); HARD
  max_population (fly 400 / butterfly 300, 0=uncapped) gating reproduce/release/continuous/
  debug spawns — a release at the swarm-count cap force-joins the nearest swarm (closes the
  §12.2 caveat item from the release slice).
- **Deep night** (floor 0.20, smoothstep golden dusk/dawn) + **flashlight** (cone Light2D
  aimed at the mouse; PlayerNightLight fully data-driven). **Pickup polish**: fresh fruit
  no_auto_pickup (the auto-picking bug), E-pickup magnet tween (TTL marks, pool-safe), [E]
  prompt over the highlighted item. ~30 new Go tests across env/trees/harvest/caps.

## Later additions from this slice
- Falling-fruit tween (canopy → ground arc) — falls currently just spawn the ground item.
- Underground full-dark zone ambient flag (flashlight required) — designed, not built.
- Weather ledger v2 (per-cell deterministic rain — designed in architecture_weather.md).
- Rain audio; sun/moon arc dial to replace the text clock.
- Tree-shake harvest animation + canopy rustle on knockdown.
- Shop entry for the flashlight (starter panel slot 15 has one for now).
- Hands as a permanent un-droppable slot-0 fixture (v1: a normal loseable item).

## Done (recent) — Bug release + axe feel + real crop-stage art + more flies
- **Release caught bugs** (OpCode 29): bug stack on the drag cursor → click the world —
  joins a nearby same-species swarm (within max(merge radius, VISUAL radius) — the max()
  prevents overlapping duplicates) via the same SWARM_REPRODUCED ledger event, or spawns a
  new swarm at the wall-clamped click (continuous-spawning path). Left=all, right=one;
  reach-tinted release circle. 12 Go tests. Design: architecture_swarm_sync §12.2.
- **Axe feel**: swings play at air (the tool no longer reads as broken); axe right-click is
  a jab. **Crop stage art is REAL now** — the watered-bed "blocked out" bug was the 52%-opaque
  placeholder blobs; garden_plot_wet was working underneath all along.
- village_21 flies: initial 25→40. Starter panel: bookshelf + bench (placement testing).

## Later additions from this slice
- ~~Zone swarm-count cap for releases~~ DONE (force-join nearest + max_population hard cap —
  see §13). Optional per-player release cooldown still open (validateCooldownTicks one-liner).
- Release-moment feedback polish (a "−N flies" popup like CatchPopup).

## Done (recent) — Inventory polish + cursor-place + weapon movesets + equip visibility
- **Hotbar drag/drop** (two-mode button: panel open = item ops) + the LIVE swap-source
  corruption fix + server cross-type guard + Metadata travels with moves/swaps and clears on
  empty + echoes carry it.
- **Cursor-place (Terraria)**: drag a placeable from the panel → ghost over the world →
  right-click places from THAT slot (`TilePlace.source_slot` *int; remainder-preserving echo
  interception on BOTH slot types — the full contract is in architecture_inventory.md).
- **Weapon movesets**: per-move stats in items.json `moves {primary, secondary}` — sword
  L=swing/R=jab, spear L=stab/R=sweep, axes R=combat swing (L stays breaking); nil-safe
  move-existence gate; reach-before-stamp; ONE shared cooldown body. Router owns right-click
  (station close-consumes → placement mode-consumes → weapon secondary). 8 new Go tests.
- **Equip visibility**: held-at-rest tool display local + remote (EntityData.eq on op11),
  remote swing replays self-describing from MeleeResult.weapon+move; animator RestoreIdle
  contract (also fixed the interrupted-sweep trail leak). Starter kit: sword (slot 4),
  spear + dirt in the panel.

## Done (recent) — Combat v1 + icon unification + tool animations + mouse facing
- **Icon unification (architecture_items §0 now real):** every icon/drop = the scaled-down
  original sprite via one resolution chain in `GetItemSprite` (Objects→Items fallbacks,
  optional `icon_from`); preserveAspect in UI; ground drops fit-box ≤0.75 cell.
- **Mouse facing** (run backwards), **PlayerToolAnimator** (in-hand swing/sweep/stab/pour
  with arc trail; killed the invisible-net sorting bug class), **PlayerInputRouter**
  (single left-click owner — see `architecture_input.md`).
- **Combat v1:** per-bug HP (sparse server `BugHP`, display-only client copy on
  `BugVisual`), sword/spear swept-sector melee (OpCodes 88/89), net = physical sweep with
  data-driven arc/reach/caps, `bug_parts` kill drops, seed drops from wild flora. Fixed:
  large_net-as-hand, multi-swarm catch ghosting, stale `EquippedTool`, UI click-through.
  13 new Go tests; sync-harness regression clean. Design: `architecture_swarm_sync.md §12`.
- **Remaining for the slice:** Phase 2 art (tool families + recolored tiers + seed packets
  + 6 art-less items) and in-game verification (Phase 5 checklist in the plan).

## Done (recent) — FLY LIFECYCLE: feed → reproduce on rotten fruit/compost until the food runs out
- **The ecology loop is LIVE and verified e2e** (headless, 6-min run): tree drops fruit → rots
  (`ITEM_ROTTED`) → flies feed (`FOOD_CONSUMED` thresholds 75/50/25/0; drain ∝ fly count) → satiation
  fills → phase flips → breeding at a DEPLETABLE source → **`SWARM_REPRODUCED` doubles the swarm**
  (6→12→24→48) → over the 20 limit → minute-pass **SIZE SPLIT** → children feed/breed too →
  **13 swarms / 168 bugs from 6 in ~6 min**; graph at `tools/output/fly_counts.png`.
- **Server-authoritative lifecycle** (replaced the dead OpCode-70 client-report sketch): meters advance in
  the swarm loop from centre-at-cached-food checks (O(1)/tick); `FindNearbyFood` unifies rotten ground
  items (the old occupant-only query NEVER matched dropped fruit) + station fill + flora; satiation decay
  wired; v1 rule: REPRODUCTION requires a depletable source (flora is infinite — no unbounded butterflies).
- **FIXED a pre-existing breaker**: ground-item lifetimes were processed by TWO per-tick functions — double
  decrement + a deleter racing the rot transition (fruit usually VANISHED instead of rotting). One
  processor now; rot time data-driven (`fruit_rot_ticks`, units fixed to real 28min default).
- **STATIONS (general pattern, composter first)**: data-driven `world.station` block (accepts/capacity/
  food_per_unit/providers); player deposits via a right-click menu (`StationController`, OpCodes 85/86);
  fill = food+breeding provider for flies, drained by the same consumption path. Item PICKUP existed
  (research wrong) — added the food-registry removal event on pickup of rotten fruit.
- **Client**: deterministic event-driven FOOD REGISTRY (ITEM_ROTTED/FOOD_CONSUMED upserts; join-time
  hydration from chunk-resent ground items); `SWARM_REPRODUCED` → idempotent `SpawnBugAt`; per-bug
  **land-on-food behavior** (approach, ring offset by bug-id, pause, resume — all deterministic inputs);
  **debug overlay**: F4 swarm centres/counts markers, F5 live population graph.
- **Gates block bugs** (wood/iron/picket — `blocks_bugs: true`): bug-tight pens players can walk into.
- Test zone `repro_test` (gated pen + fast `tree_apple_test` + compost bin + 6 flies); 3 new Go unit tests
  (consumption thresholds/depletion, reproduce bookkeeping, station drain); harness decodes the lifecycle
  events + writes the population CSV (`tools/plot_fly_counts.py`).
- **GATHERING MODEL settled (Terraria-style)**: LEFT-CLICK breaks (hand for soft flora — flowers are 1-HP
  with drops already; axe for trees), drops float as ground items, **WALK-OVER AUTO-PICKUP** collects
  ordinary drops (magnet 1.25, rate-limited + per-item backoff). **EXCEPTION: bug food (rotten_*) is never
  auto-collected** — deliberate E only ("what the bugs eat belongs to the bugs"), so you can't strip your
  fly farm by walking through it. **CLICK PRIORITY: catch beats break** — a bug within net-catch range of
  the cursor claims the click (BreakingController defers), so clicking a fly on a flower catches the fly
  instead of smashing the flower. No gathering tool needed; the net stays equipped.
- **Unity to verify**: add `StationController` to the player/systems object; F4/F5 overlays; deposit menu;
  bugs visibly landing on fruit/bin; auto-pickup feel + the catch-over-break priority. **Next/tuning**:
  real-tree scarcity pacing, station processing-over-time (`process_ticks` reserved), eggs for other
  species, butterfly reproduction via flora-capacity design, tree-shake harvest (`TREE_FRUIT_HARVEST`).

## Done (recent) — Bug collision + deterministic swarm split/merge (Phases 1+2)
- **Per-bug collision wired** (`BugAgent.SimulateTick` → `BugCollision.Resolve`, slide vs `blocks_bugs`);
  **player collision** added client (`IsCellBlockedForPlayers` + PlayerController feet-gate) + server
  (`IsBlockedForPlayers`, authoritative reject in `OpCodeMovement`); **spawn-at-center** (bugs drift out).
- **Population model**: once-a-minute pass (600 ticks) — swarm **splits when `Count > max_swarm_size`**
  (sheds its HIGHEST alive bug-ids into a child) and **merges when centers within `merge_radius`** if
  `combined ≤ max`. Carried as tick+seq **`SWARM_SPLIT`/`SWARM_MERGE` influence events** (no `SwarmsDirty`
  — lifecycle travels only via the deterministic ledger); clients **MOVE the actual bugs** between swarms
  (positions/motion preserved — never re-spawned), idempotent handlers cover the on-receipt window +
  late-join replay. fly_common tuned: `max_swarm_size 20`, `merge_radius 2.5`.
- **Verified**: 4 Go unit tests (bookkeeping: conservation, shed=highest, `SwarmsBySpecies`, event fields,
  no dirty) + headless e2e (`SWARM_SPLIT … count=15 parentCount=15 (tick=600)`, 30→15+15 conserved;
  `SWARM_MERGE … count=8 idBase=8 (tick=600)`); `collision_test` zone (in the client picker as
  "Collision Test") proves walk-over-corn/blocked-by-tree + a closed pen holds a swarm.
- **Still to confirm in a Unity build**: the visual move (bugs staying put on split/merge) — client C#
  can't run headless. Note: size-splits activate for real once reproduction grows swarms (stub today).

## Done (recent) — Building pieces + village recompose (text-grid authoring + lint)
- **Scaffolding for reliable buildings**: `features/tilemap.py` (`stamp`/`dump` — author + verify
  buildings as CHARACTER GRIDS) and `zonebuilder.lint()` (text QA gate: blocked doors, 1-wide doors,
  walls/fences on path/water, wall/door/window height, road dirt%). `registry.render_one` prints lint;
  gates/doors count as passable. Working rule: no "looks good" without lint output + a crop I've seen.
- **`features/yard.property_yard`** — the standard home yard (side yards + backyard + a couple
  back-corner trees + front flower garden, gate auto-aligned to the door). HOMES are fenced; SHOPS are
  open-fronted (no fence).
- **Composable building pieces** (`place_*`, each a full multi-room home/shop, text-grid + lint, 0
  warnings): `scene_smith` (forge+supply), `scene_carpenter` (workshop+timber), `scene_market`
  (shop+storeroom), `scene_mayor` (4-room marble mansion + iron estate), `scene_ecologist` (4-room
  study home — EAST zone), `scene_cottage` (NPC home), `scene_lakeside.place_boat_store` (shop+supply +
  dock). Village reuses `player_house.place_player_house` (⊥ 4-room).
- **`scene_village.py` recomposed** from the REAL pieces on STRAIGHT roads + central square: shops
  cluster at the square (open-fronted), homes line a residential street (fenced, one cottage per NPC),
  boat store on the SW lake, tree clumps + flower patches in the open. Buildings placed clear of roads.
- **New entities/art** (gpt-image-1): `sign_fish_board` (3-wide), `ship_wheel`, `anchor_decor`,
  `fishing_pole`, `marsh_plant`; wired the orphan `notice_board`; added a `marble` palette + re-baked
  `wall_marble`. Conventions written into `house.md`/`yard.md`/`object_pipeline.md`.
- FOLLOW-UP: **side-facing door variants** (grids currently put the door south) so buildings can face
  N-S streets / the square from more sides; tighten village density + make roads less grid-like; the
  wall(32)/door(24) 1.5-cell re-bake.

## Done (recent) — Village rebuild (guide-driven quality pass)
- **Village authoring guide** `docs/guides/authoring/village.md` — 13 town-design principles (focal
  point, road hierarchy, function clusters, density gradients, …) mapped to the primitives + a
  build-order recipe; linked from `authoring/README.md` + the author-zone skill.
- **New helpers** `tools/zonegen/features/village.py`: `shop_building()` (shell + wide sign + shelf
  rows + counter + NPC) and `plaza()` (paved square + fountain + benches/lamps + corner beds).
- **`place_bug` gains `flip=`** (zonebuilder + render + make_scene) so bugs face either way.
- **`scene_village.py` rebuilt**: organic road hierarchy (main 4 → connector 3 → side lanes 2),
  bigger lake, central fountain plaza, CLUSTERED buildings (civic: hall·market·grocer·store;
  production: carpenter+smith adjacent; residential cottages; lakeside boat store), market is now a
  shop building w/ merchant behind a counter, carpenter has the sawmill + goods in rows indoors,
  picket-fenced cottage + garden, clumped meadow with a forest rim. 0 warnings, validate OK.
- **New entities** (data + art): `sign_market_board`, `shop_shelving`, `fence_picket`/`gate_picket`/
  `fence_picket_weathered`, `garden_border_stone`/`_log`.
- FOLLOW-UP: build the real 256×256 `village_21` zone (save()-based) on this scene; iterate art.

## Done (recent) — Butterfly Meadow scenes
- **`tools/zonegen/scenes/scene_butterfly_meadow.py`** (64×52, **0 warnings**, validate OK) — the open
  meadow for `butterfly_meadow_11`: south village-road entrance (flower arch, signpost, spring/puddle),
  the **Flower-Clock Glade** (a colored-flower ring around a birdbath "sundial", composed from existing
  flowers), the **Great Milkweed Stand** (`milkweed_giant` + a milkweed colony swarming with monarchs),
  the **Basking Boulder**, the **Broken Fence Line** (split-rail run + leaning gate + orb-web), the
  **Lepidopterist's Blind** (tent/specimen case/crate/net post/lantern), scattered open-grown oaks +
  failed-farm relics, heavy flower/milkweed/tall-grass scatter, drifting butterflies/bees + a paper
  wasp and a yellowjacket.
- **`tools/zonegen/scenes/scene_meadow_forest_edge.py`** (60×46, **0 warnings**, validate OK) — the
  northern transition (renderer is north-up): warm flowery meadow at the bottom darkening to **dirt**,
  **threshold stumps** (`stump`/`stump_mossy`) with bracket fungus, the **fallen-log bridge**
  (`log_fallen`) across a boggy seam, a thickening **tree band** of pine/oak/dead-tree clusters, log
  piles + brambles + fern/mushroom understory, and the edge threats — a **millipede** and a
  **centipede** assembled from the existing segmented head/body/tail part sprites.
- **7 new lean placeholder entities** (catalog `look` rows in place): `milkweed_giant`, `clover_red`,
  `stump_mossy`, `log_fallen` (occupants); `broken_fence`, `boulder`, `specimen_case` (placeables).
  Queued in `art_needed.md`. PLACEHOLDERS only — no art generated.

## Done (recent) — starting-village town scene
- **`tools/zonegen/scenes/scene_village.py`** (80×80, **0 placement warnings**, validate OK): the
  full lived-in town for `village_21` — a N–S × E–W stone road crossing at a central **civic square**
  (well, fast-travel signpost, notice board, benches, founder statue, flower beds, lamp posts); the
  **six shops** ringing it (Town Hall in marble w/ columns + map table + mirror; open-air Market w/
  stalls + awnings + produce; General Store; Carpenter w/ furniture display + log/sawhorse/chopping
  block; Smith w/ exterior forge + anvil + coal bin + tool rack; Boat & Fishing Store on the SW
  **lake** with docks, a moored boat, anchor sign, nets, fish crates); an **Ecologist's cottage**
  (specimen shelves, terrarium, test garden), **3 themed NPC cottages** (window boxes / cat statue /
  laundry + veg patch) via `features/house` layouts + furniture collections; an **orchard** + **fly farm** on
  the edges; meadow scatter, road lamps, pollinators. PLACEHOLDERS only — no art generated.
- **24 new lean placeholder entities** added (`placeables.json` + catalog `look` rows): `wall_marble`,
  `column_marble`, 7 shop signs, `market_stall`, `awning`, `produce_crate`, `dock_plank`, `boat`,
  `mooring_post`, `fish_crate`, `fishing_net`, `coal_bin`, `lumber_rack`, `bait_station`,
  `veg_patch_sign`, `statue_founder`, `laundry_line`, `cat_statue`, `window_box`, `specimen_shelf`,
  `bug_terrarium_big`, `map_table_big`, `sofa_modern`. Queued for the art pass in `art_needed.md`.

## Done (recent) — sync stability + headless test infra
- Fixed the frontier-gated freeze (spurious resync — "caught up" was wrongly treated as a stall)
  and the reconnect seq-desync (stale `PendingInfluence` leaked to the next client). Details in
  `architecture_swarm_sync.md` §11.
- World lifecycle: pause-when-empty + `world_enter` (singleton Normal/Test worlds; the frontend no
  longer creates worlds).
- Test infra: headless `.NET` sync-harness (`tools/sync-harness/`, incl. a reconnect scenario),
  test-zone generator (`tools/make_test_zone.py`), `sim_test` zone; single-source zone config
  (removed `debug_mode` + `species_debug.json`).
- New world-select login (`WorldMenu`).

## Done (recent) — overnight: new scenes + bug pipeline + encyclopedia
- **Blocks/walls — MISTAKE, being corrected:** an opaque-generation change I made (`is_block_like` →
  `background="opaque"`) was WRONG — it baked black/white backgrounds and the blocks didn't tile; a
  related `ab_generate` bug turned `cave_floor` into a chest. Reverted to the standard transparent+crop
  flow; regenerating each block/wall as 2 variants matched to `wall_stone`, verified with
  `scene_block_tiling.py`. `wall_stone` (untouched) is the standard. Guide rewritten with HARD RULES.
- **A/B sprite workflow:** `tools/ab_generate.py` (A live + B in `tools/_generated/ab/`) + `contact_sheet.py`
  A/B sheets in `previews/ab_review/`. Every new sprite has an A/B pair to pick from.
- **Underground scenes:** caves improved (quartz blocks, wider rail tunnel + wood supports, more dirt,
  shape labels); underground house rebuilt **flush in rock**; NEW **mining camp** (campfire+spit, tents,
  miners via a new player palette, custom sign); **ant colony 2×** (egg room + queen + tunnel to a
  mushroom cavern). Previews in `previews/` (flat, one `scene_<name>.png` each).
- **Bug pipeline:** `bugs` source → `Resources/Bugs/` + a `creature` art family; **segmented centipede &
  millipede** (head/body/tail ×2, mix-and-match) + **scorpion**.
- **New surface scenes:** `scene_beefarm_woods` (apiary + meadow + woods + stream) and `scene_desert`
  (sand + sand_block, road, old inn w/ neon sign, weather outpost + antenna + windmill, oasis, cacti,
  scorpions) + ~20 desert entities.
- **Encyclopedia (`docs/product/encyclopedia.md`) + `brainstorm_items.md`:** ~50 bugs (incl. water bugs)
  across ~16 families ×3 difficulty tiers + 21 new plants — data + catalog + A/B sprites being generated.
- `docs/product/underground_review.md` — proposals for camp + ant-colony additions.

## Done (recent) — underground zone scenes + guides + content
- **Caves guide + primitives:** `docs/guides/authoring/caves.md` + `features/cave.py`
  (`carve_tunnel` natural-meander/straight, `carve_cavern` shapes, `place_pool`, `fill_solid` with a
  rarity-tiered ore table). **Mineral art family** (catalog `"family":"mineral"`) so crystals/rubble/bone
  render as faceted rock, not plants. New entities: `ore_tin_block`+`tin_ore`, `mine_rail`, plus
  `crystal_quartz`/`rubble`/`hard_stone_block` and the mining props.
- **Scenes (all 64×64-ish, full real art, 0 warnings):** `scene_underground_caverns` (man-made rail
  tunnel vs natural meandering tunnels, varied caverns, cave mouth, ore veins, pool, fauna),
  `scene_underground_house` (stone house dug into a cave), `scene_ant_colony` (`ant-colony.md`:
  branching nest + ant-file trails).
- **Content batch (+27, art generated):** mushrooms (blue/cluster/morel/bracket/inkcap), geode, mining
  equipment (tool_rack, wheelbarrow, ore_pile, powder_keg, mining_bucket), furniture (ottoman,
  chaise_lounge, vanity, kitchen_island, bunk_bed, throne, bar_cart, bathtub, stone stool/bench),
  decorations (statue_bug, suit_of_armor, globe, gramophone, easel, telescope).

## Done (recent) — data-driven art layer + content + house collections
- **Art is data-driven:** `tools/art/style.json` (global look + per-family blocks + palettes) +
  `tools/art/catalog/*.json` (per-item `look`/`materials`, one file per category). `gen_sprites.py`
  is now a thin assembler (1350→~740 lines); prompt output is byte-identical to before. Dead
  player-art spikes removed (kept `segment_sheet` + frame helpers for the multi-frame item).
- **Furniture/decor +34** plain valued entries (quality = `sell_price`); **+12 wild flora** occupants
  + **+12 resource items**. Art generated for the new furniture + flora (data-driven catalog).
- **Furniture collections** (`features/furniture.py`, basic/fancy, `pick(role, coll)`, `styled_rooms`)
  — fancy/appropriate-for-wealth knowledge lives in the scaffolding, NOT game data. New scene
  `scenes/scene_houses.py` (room counts × collections, each in a yard). New primitives:
  `features/{yard,terrain,garden}.py`, `features/house.py` layouts (3/4/5-room). Guides: `house.md`
  (updated), `yard.md` (new); `object_pipeline.md` + `add-object` skill rewritten around the catalog.
- **Item/inventory model written down** (`architecture_items.md §0`): placeable vs free/collectible,
  derived vs authored icons, bonus diminishing-returns keyed off `id`. Content-diversity philosophy
  (`game_design.md §19`). Power/cooking design (`§11.6/11.7`).

## Done (recent) — zone-authoring scaffolding + house system
- Builder library `tools/zonegen/` (ZoneBuilder + occupancy masks), `make_scene` renders from data
  with category placeholders, `author-zone` skill, `feature-building`/`feature-vegetation` guides.
- **House composer** (`features/house.py`): multi-room buildings from shared-wall rects (⊥/L),
  interior doors + windows + doorway-avoidance, and a reusable room-template library
  (living/bedroom/kitchen/crafting) following the south-facing **facing rule**. Guide:
  `docs/guides/authoring/house.md`; reusable house `scenes/player_house.py`; scenes live in
  `scenes/` and compose houses (e.g. `scenes/scene1_player_farm.py`).
- New entities (data + `OBJECT_DESC` ready, art pending): fridge, stove, sink, counter, keg, sofa,
  armchair, nightstand, dresser, rug, bug_terrarium, vase, window_4pane, door_square.
- **Engine fix**: `TilemapManager` tall-sprite vertical baseline (center-pivot PNGs + zeroed bc
  offset made beds overshoot); preview renderer flipped to match game orientation (+Y north).

## Now — Scene 1: player house + fly farm
- House DONE (the ⊥ cottage, full real art). Fly farm FIRST PASS done
  (`scenes/scene1_player_farm.py`): netted fly pen (apple trees, fallen/rotting fruit, flies on
  ground + netting, autonet, compost bin, broken net, apple crate, the farmer), orchard, garden
  (fountain, benches, beds, lamps), paths, scattered decor + butterflies/bee. Pending:
  - **Generate the farm art** (placeholders now): fountain, compost_bin, autonet, fly_netting,
    fallen_fruit, rotten_fruit, rock_small, rock_mossy — `OBJECT_DESC` ready in `gen_sprites.py`.
  - Iterate the garden/pen layout; confirm the **decorative-rock** decision (vs the old
    "no standalone rocks, use stone_block" rule).
  - **Unity Play test** of the tall-sprite pivot fix + orientation (verify in-game vs preview).

## Now — Safe cleanup only (no refactoring, no splitting files)
Tidy what's clearly safe; leave anything risky alone.
- ~~Delete dead player-art spikes in `gen_sprites.py`~~ DONE (removed `recolor_skin`/`SKIN_*`/
  `PLAYER_STYLE`/`char_sample_prompt`/`body_prompt`/`walk_sheet_prompt`/`build_walk_set` + their CLI
  flags; kept `segment_sheet` + frame helpers per the multi-frame item).
- Remove scratch/clutter and any empty dirs left over from earlier reorgs.
- No structural refactors, no god-class splits — those are deferred until we have a way to verify
  them (there are currently no automated tests).

## Next — Get multi-frame sprites working (hands-on, together)
Experimental and human-in-the-loop — we try things and look at the output together, not plan it up
front.
- First: see if gpt-image-1 will output a clean sprite sheet we can crop. Start with the garden
  bed (dry vs watered).
- If it won't: fall back to a base bed plus a separate water-drops layer (procedural or old-style).
  The plant is drawn on top as its own layer either way.
- Once a method works, reuse it for crop growth stages, then later bug animation frames.
- **Segmented bugs (centipede/millipede): head/body/tail sprite sheets** — the agreed next hands-on task.
  BLOCKER: `gen_sprites.py` has no `bugs` source/dest yet (bug sprites are hand-made in `Resources/Bugs/`);
  add a bug art path + family + a bug species data file before generating. Then chain head→segments→tail.

## Next — Zone-design guides cleanup
- ~~Consolidate the scattered/contradictory guides into one coherent set~~ **DONE** — `docs/guides/`
  split into `art/` (look & pipeline) + `authoring/` (zone/scene building, indexed by
  `authoring/README.md`); the dead `generate_zone.py` system (+ its `ZONE_GENERATION_GUIDE`/
  `BUILDING_TEMPLATES` guides) archived; zonegen code consolidated (`houses/`+`builds/` folded into
  `features/`+`scenes/`; scene registry → `zonegen/registry.py`; `artlab/` is now purely the viewer).
- REMAINING (design, its own plan): make generation **natural & non-rigid** — no dead-straight roads,
  no uniform scatter; encode that into the authoring primitives + guides.

## Next — Zone graphics: 6 preview scenes
Fill missing entity data, generate/clean remaining sprites, render 3 surface + 3 mining preview
scenes. Depends on the two items above.

## Later — captured, not scoped yet
- **Power & electrification + cooking progression** (design captured in `game_design.md §11.6/11.7`):
  windmill/hydro/generator → power unit with a coverage-radius aura (highlight covered cells at
  placement); a shared "linked placement" line tool (power lines AND rail/track — click start/end,
  reject if it clips); machines split into fuel-fed (wood stove) vs electric; stove cooking-capacity
  tiers. Add the power/fuel-requirement entity flag only when building this. Author a small
  **power/electronics demo scene** to tinker with it visually.
- **Placeable wall/block visual tiling consistency** — make placeable walls/blocks (wood/brick/iron/
  glass/marble + wood/stone) tile together cleanly. Iterate-heavy, token-spend; its own pass.
- **General-store catalog scene** — a shop (next to the produce market) with a buy-catalog of
  furniture/decor/valuables (gold pieces, piano, fancy whatevers).
- **Building-materials + rug/valuables content** — wall_brick/iron/glass/marble, window_wood/metal/
  fancy, rug_bearskin/fancy-patterns/simple, piano & gilded valuables (data + art via the catalog).
- Bug behaviour / AI.
- Authoring brand-new zones.
- More weapons + loot tables: per-species `kill_drops` schema (v1 hardcodes `bug_parts`),
  higher weapon tiers via the recolor pipeline, rarity tiers per the weapons brainstorm.
- **Bug HP affecting BEHAVIOR is a determinism boundary**: today HP is display-only; if
  damaged bugs should flee/slow, HP must enter the deterministic sim + state hash
  (architecture_swarm_sync §12).
- Higher tool tiers (steel→diamond): items.json entries + `recolor_sprites.py --family ...`
  (ramps already inline; the legacy reference art was cleaned out of Items/).
- Tiles still import Bilinear (Objects/Items/Bugs are Point now) — flipping the ground's
  filtering is a deliberate style decision to make with eyes on it.
- Staggered per-bug catch/kill pops along the sweep arc (cosmetic, no protocol change).
- Client EditMode test infra (first candidates: icon resolution chain, sector math as a
  pure function, the cursor echo-interception rule).
- Weapon tiers as moves data (sword_stone+, spear_iron — items.json entries + recolored
  icons; the design-target table lives in architecture_items §3). Durability still unenforced.
- Whip weapon kind: one new AnimKind/profile + one client line/tip hit query — server-free
  (reach-only validation). First whip proves the moveset schema's extensibility claim.
- Idle-held display for torches/lights (v1 gates on ToolType; the held torch already glows).
- Facing-aware idle held pose (remote + local render at a fixed side regardless of facing).
- TilePlace server range check (none exists — you can place from any distance).
- "Cursor hold as server-visible state" if inventory grows sort/quick-stack/shift-click —
  each new server-side slot writer must re-prove the echo-interception invariant
  (architecture_inventory.md).
- An enemy.
- Active/inactive zones: simulate bugs in detail only in zones that have players; cheaply
  aggregate the rest; pause a zone entirely when it has no one. Finer-grained than today's
  per-match pause-when-empty (which only idles when the *whole* world is empty).
- Free long-idle matches + clean up accumulated world metadata (matches currently idle when
  empty but are never freed; harness `world_create` runs leave stale metadata).
