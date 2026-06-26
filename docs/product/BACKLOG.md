# Backlog

Running queue of upcoming work. Short notes only — each item gets its own plan when we start it.
**Now** = active, **Next** = teed up, **Later** = captured so we don't forget.

This is the durable queue. The throwaway plan doc covers only the single item we're actively
working; this file is what survives between sessions.

## Testing backlog (deferred test coverage — not blocking)
- **Cross-zone determinism check**: a player leaves a zone and re-enters; assert the bug-sim STATE HASH
  is identical across the leave/join (same bug positions/phase) — i.e. the swap didn't perturb the
  deterministic tick. Extend the sync-harness `crosszone` scenario to capture + compare zone hashes
  before/after. (The crossing is *designed* to be determinism-inert; this proves it.)

## Now — Bug ecology / farming (livestock loop on a living-ecosystem engine)
Design of record: [bug_ecology_plan.md](../brainstorms/ecology/bug_ecology_plan.md). Phased build P0–P11
(P1 Bug Lab DONE). **Verify every sim-touching phase with the `test-changes` skill** (Go tests +
sync-harness + the determinism / "all players in sync" checks — the testing methodology is now captured as a
skill so it stops getting lost between sessions).
The **SERVER ecology is built + verified** (Go tests + 6× headless lab + per-species charts in
`tools/_generated/ecology_charts/`). The living system = **depletable food → boom-bust → the Director →
(future) the Ecologist restores → progression**. Done:
- **Visible breeding broods** — flies/butterflies lay eggs into a brood (compost / rotten-fruit maggot pile /
  milkweed) that matures + hatches (`entities/brood.go`, `world/brood.go`).
- **Natural death + carcass recycle** (per-bug `DeathTick`, `dead_<species>`, millipede→compost).
- **Hard `max_population` crash-guard** (per species per zone; the only guaranteed bound — food is
  player-controlled, so it can't be the guard).
- **Depletable food** — flower `ForagePoolState` nectar + milkweed `HostPlantState` (deplete + regrow).
- **Starvation death** (`StarveTimer`/`processStarvation`) — the bust.
- **The Ecology Director** (`world/ecology_director.go`) — per-species bands: re-seed below `min_population`,
  cull above `cull_at` (release `cull_with` predator else overcrowding cull). The oscillation engine + the
  universal "add a layer when out of range" lever.
- **Test sim-speed control** (`SimRate`/`call_rate`, 6×, balance-neutral) + **per-species population graphs**.
- Design of record: see architecture_farming.md "Living ecology — population dynamics" + the roadmap plan.

### Phase W2 — Cost profiler + perf-first rebalance (DONE 2026-06-19)
Built the full-stack bug **cost profiler** (measure before optimizing) + rebalanced village_21_B to fix the
~1000-bug lag. All committed-ready (see ecology_tuning_log.md 2026-06-19 + the plan doc).
- **Profiler:** server `PERFSTATS`/`PERFSYS` (per-species CPU by sub-phase + leg counts + global passes +
  broadcast bytes; gated by zone `profile` flag; soft/never-hashed — `world/profiler.go`), `tools/ecology/plot_perf.py`,
  `run_config.py` wiring, and a client **F7 overlay + Unity-Profiler markers** (`Util/PerfProfiler.cs`,
  `DebugOverlay`). **Finding:** `FindNearbyFood` dominates server CPU (butterfly 11.7s/day); the predicted
  O(S²) merge is negligible (5ms/day).
- **Rebalance (baked):** fly/butterfly 3× swarm size; millipede+beetle category→swarm + brood-gate on
  `EggSpriteID` (detritivores instant-grow+merge); tuned to ballpark bands. **Win: legs 5.9→1.1 MB/day,
  butterfly cpu_food 11.7s→~0.5s, swarms 68→20 — lag gone.**
- **Follow-ups surfaced (NOT done — structural, not tunable):**
  - **[PERF, high] FindNearbyFood spatial index** — bucket `GroundItems`/`Stations` by chunk; route the
    food query + `nearestPredator/PreySwarm` + merge through it (O(S·I)→O(S·k)). The profiler-proven #1.
  - **[PERF] Chunk-scoped broadcasts = per-chunk-frontier redesign** — NOT safe routing (the client gate
    `HasAllEventsUpTo` needs a contiguous global seq stream; dropping a chunk's legs stalls it). Per-chunk
    seq+watermark+gating+handoff. Gate behind the profiler showing the global stream is still the bottleneck.
  - **[ECO] beetle carrion supply** — beetle stuck ~3 (carrion-starved); needs distributed carrion sources
    (zone change), not a breeding param.
  - **[ECO] wasp prey base** — stable ~16; reaches 30-50 only if fly settles higher.
  - **[ECO/Go] centipede kills→breeding conversion** — pinned ~4 across two breeding-lever runs; needs a Go
    fix (it can't convert kills to offspring), not tuning.

### Phase 4c — TUNING RIG (built + committed) + the sweep (in progress)
The ecology is structurally complete but UNTUNED; targets are the CENTERS of an oscillation (boom-bust
for ecologist gameplay), NOT flat lines: **fly 100, butterfly 100, wasp/centipede/beetle/millipede 30**.
Two acceptance criteria/species — **oscillates** (visible amplitude/period) + **self-maintained** (troughs
above the re-seed floor → `b_reseed` births ≈ 0). The RIG (all committed, see `ecology_parameters.md`):
- **Tick batching** (`sim_batch`) → 48× runs; **tunable consts** → `data/ecology_tuning.json` (`Tuning`,
  byte-identical defaults); **interaction-log telemetry** (`ECOSTATS`/`PREDLOG` → `plot_interactions.py`,
  births-by-source / deaths-by-cause / predation matrix); **config system** (`tools/bug_lab_configs/` +
  `run_config.py` snapshot→apply→run→chart→restore + `compare_configs.py` scoring).
- **40-run sweep (3 batches, configs in `tools/bug_lab_configs/`, charts in `_generated/ecology_charts/`):**
  - **Harness reliability fix (infra):** the sweeps exposed a real bug — Nakama's `socket.outgoing_queue_size`
    (1024) overflowed on the whole-zone chunk-subscribe burst → server closed the socket → runs froze (no
    CSV). Raised to **8192** (`nakama/data/local.yml`). Also hardened `run_config.py` (retry + per-run log
    isolation so `plot_interactions` can't read a prior run's ECOSTATS).
  - **SOLVED ✅ fly → 100:** `C3` lever = faster fly breeding (`reproduce_cooldown` 30→18, `breed_amount`
    10→16). Oscillating, 0% re-seed.
  - **SOLVED ✅ butterfly → ~90:** robust across nearly every config (host/nectar-limited, self-maintained).
  - **SOLVED ✅ centipede → 30** (the breakthrough): the predator FLOOR was **structural, not behavioral** —
    proven because NO predator/prey/food parameter (vision, speed, strike, feed, breed-bar, lifespan, decay)
    moved it across 30 runs (at fly=100 GLOBAL the predation log showed `centipede→fly = 0 kills` — its pen
    had no prey; a predator eats its small fly seed to extinction in ~3 days then starves = small-system
    predator-prey collapse). **Fix = prey immigration** (`fly_common` `spawn_interval` 999999→20s; since
    `spawnSwarmForSpecies` picks a random spawn area, fresh flies trickle into every predator pen). With
    sustained prey the centipede hunts→breeds→reaches 30, **0% re-seed, oscillating** (configs `G4`-`G7`).
  - **PARTIAL ◐ beetle ~12, millipede ~18:** both now self-maintained (0% re-seed) but below the 30 target —
    need higher caps + more food (beetle: corpse supply / cap 20→40; millipede: more `leaf_litter`).
  - **SOLVED ✅ wasp (2026-06-18, the living-zone redesign):** the frozen-wasp holdout was STRUCTURAL —
    nestless free-spawned/reseeded wasps (sterile, can't deposit brood) + dead colonies going permanently
    dormant. Fix = **wasps nest-only** (skip nest species in every free-spawn path → zero nestless wasps)
    + **prey-gated nest recovery** (a brood-exhausted colony re-founds a fresh patrol when live prey is
    within home range, else WAITS) + **6 nests spread to woods/corners each near a fly source**. Verified:
    wasp pop sustained ENTIRELY by `b_nest` (hatches + recoveries), `b_reseed=0 b_spawn=0`, colonies
    re-found as flies boom (run v21b_nocaps, seed 1337). Remaining = oscillation-band tuning, not structure.
  - **Open balance items:** immigration overshoots fly to ~390 — dial `spawn_interval`/cap so fly sits at
    100 while still feeding predators; then re-add the Director culls as far guardrails (`G10` showed culls
    reshape via re-seed, not self-maintenance — keep them last-resort).
  - **Best config so far: `G6_immig_breedbar` / `G4_immig_reach`** (centipede PASS + decomposers
    self-maintained); fly/wasp still need the two balance items above.
  - **→ Next (post living-zone redesign, 2026-06-18):** (1) longer runs (sim_batch>2) to watch a full fly
    boom→bust→wasp-dip→recovery oscillation and judge the bands; (2) dial fly initial/food (boomed to ~198);
    (3) beetle/centipede establishment (still reseed-reliant); (4) re-confirm same-seed reproducibility gate.

**Up next (the roadmap remainder, mostly client → needs the Unity Editor):**
### Ecology mechanic fixes (from the village_21_lab control campaign, 2026-06-18)
The 15-run controllability campaign (`docs/product/ecology/ecology_control_campaign.md`) proved two species are
STUCK for MECHANIC reasons, not tunable by any param:
- **Make `leaf_litter` DEPLETABLE** (a ForagePool like milkweed/nectar, deplete + regrow) — millipede's only
  food is non-depletable flora, so it's "food-limited" by infinite food → pins flat-high (~130) and never
  oscillates. Depletable litter makes it genuinely food-bounded → it'll sit in a real oscillating band.
- **Buff centipede kills→breeding CONVERSION** — centipede hunts fine (144 kills/run) but can't convert
  kills to population (stuck at the founding floor ~4 under every param). Likely `predator_breed_satiation`
  too high / `max_swarm_size` 3 too small to accumulate / well-fed-split too slow. A ground-predator
  breeding pass would let it climb. (Tuning vision/position/seed-count all FAILED — it's a breeding bottleneck.)
- **Brood CLIENT layer** — right-click a source → eggs/maggots panel + on-world maggot-pile/egg visuals + sprites.
- **Plant repopulation** — player planting (seeds from destroying milkweed/flowers) + rare bounded natural spread.
- **Ecologist meta** — the Ecology TAB dashboard (per-species graph + band status + tasks, reusing the same
  per-species data), restorative TASKS (the Director's player-facing tier: a task + grace window before the
  auto-event fires), and progression (CharacterSave XP/unlocks).
- (Optional) natural predator-prey oscillator — the Director's predator pulse already covers the culling.

### Bugs at zone boundaries (owner has ideas incl. heuristics)
- **Problem:** bug swarms wander to / spawn near the zone edge (x|y → 0 or 256) — half a swarm's
  habitat falls off the map, predators chase prey that "leaks" past the boundary, and edge clusters
  read badly on the bug-map. The sim treats the 256×256 box as a hard wall with no edge behavior.
- **Direction (owner):** handle this with **heuristics** rather than a hard clamp — e.g. soft
  repulsion / reflect wander targets away from the border, weight spawn-area picks toward the interior,
  keep nest home-ranges off the edge, possibly hand swarms that cross to the neighbor zone (cross-zone
  movement already exists for players). Owner to detail the specific heuristics.
- **Why now:** the spatial multi-region seeding (below) puts clusters near the NE/NW corners, so edge
  behavior starts to matter; capture it before it bites the ecology tuning.

## Done 2026-06-16 — cross-zone movement (walk off a zone edge → hidden swap into the neighbor)
Walk to a zone edge that has an authored neighbor → quick fade → tear down zone A → join the neighbor at
its matching edge → fade back. Each zone is an independent Nakama match/sync domain, so a crossing is a
normal leave-A/join-B (zero cross-zone determinism surface; player position is not in the sim hash).
- **Adjacency as data**: `ZoneConfig.Neighbors {north/south/east/west}` (zone.go); `world_enter` returns
  the entered zone's neighbors (rpc/world.go). Authored pair: `village_21_B` (south) ↔ `underground_passages_31` (north).
- **Server entry-override**: join metadata `entry_x/entry_y` → `MatchJoinAttempt` validates (clamp +
  anti-forge: within 4 cells of an edge) → `PendingEntryPositions` → `MatchJoin` places the player at the
  neighbor's matching edge (overrides the char-save spawn). `PlayerSpawn` (102) broadcasts it.
- **Client**: `CrossZoneController` edge-detect + `ScreenFade` cover; `WorldManager.ResetForZoneSwap`
  tears down entities/swarms/influence/tiles (zones share coords 0..255 — avoids ghosting); match-id guard
  on `HandleMatchState`. **Authoritative entry placement**: the swap sets the player position itself
  (`SetLocalPlayerSpawn(ex,ey)`) — position is client-authoritative and the join-time `PlayerSpawn` races
  with the `JoinMatchAsync` `CurrentMatch` assignment (gets dropped), so the swap can't depend on it;
  movement-send suppressed while `InputLocked`; entry insets off the seam (Lo=4/Hi=251).
- **Content**: a walkable grass strip across the mine's north edge (entry apron) so a crossing lands on
  walkable ground, not the rock wall.
- **Verified**: sync-harness `crosszone` scenario (server entry-override, headless) + in-Editor rapid
  up→down crossing — root-caused a stale-snap race from the Editor.log and fixed it client-side.

## Done 2026-06-16 — zone / farm persistence (farm + bug population survive a server restart)
A zone's player-built farm AND its cultivated bug population now persist to Nakama storage and restore on
match (re)create — previously everything evaporated on restart / `MatchTerminate`. NEW
`world/zone_persist.go` (mirrors `character_persist.go`): `zone_state` collection, `ZoneStateKey(zone,
instance)` (forward-compatible with future private plots), per-chunk delta records + a `:meta` index +
a `:swarms` population record.
- **Farm** = a DELTA on the authored base: per-chunk `CellEdit`s (ground/occupant, semantic diff so authored
  formatting never false-positives; `OccSet` encodes a broken authored occupant) + the crops/trees/
  containers/stations/craft-stations/ground-items anchored in the chunk. Applied in `handleChunkSubscribe`
  BEFORE the init scans (which randomize untracked trees). Prefetched once at `MatchInit` (no per-subscribe I/O).
- **Bugs** = minimal per-swarm descriptors (species/pos/count/phase/satiation/breeding); restored as CLEAN
  swarms via `spawnSwarmAt`+`InitializeBugIDs` (skips `spawnInitialSwarms`). Determinism-safe: the server is
  the swarm authority, restored swarms enter at the cold-start boundary identical to fresh spawns, food
  re-discovers via `FindNearbyFood`. Only `FruitTreeState.LastFallTick` needed a tick-reset clamp (crops are
  water-driven).
- **Triggers:** prefetch on `MatchInit`; save on transition-to-empty (async) + `MatchTerminate` (sync,
  replaced the old TODO) + a 10-min autosave while occupied. Determinism surface = zero (farm not hashed;
  swarms enter cold; tick loop/ledger/food-registry untouched).
- **Verified autonomously** via the sync-harness: join `village_21` → leave wrote 59 swarms + chunk records
  (`cells:0` = no false positives, authored base safe); restart → `restored 59 swarm(s)` + frontier-gated
  sync ran clean (no RECEPTION GAP, ticks advanced) → the determinism check passes; merge-preserve keeps
  unvisited chunks; zero panics. (Farm-modification visual confirmation — placed objects/crops/chests across a
  restart — is the one remaining check, needs the Unity client.)
- **Deferred (separate feature):** the two-tier-LOD "empty-zone ecology" — bugs *evolving while you're away*
  in zones with no players. This milestone preserves state as-of-last-player, not active offline simulation.

## Done 2026-06-16 (pending Editor compile) — Terraria-style characters + per-character persistence
An account (one device-auth `userID`) owns multiple **characters**, each persisting independently
(inventory, equipment, coins, unlocked slots, appearance, position). Pick a character → join a world
with it → it persists for that character. Determinism-safe: character data is NOT in the bug-sim
state hash; save/load happen only at the MatchJoin/MatchLeave boundaries.

**Done + server-rebuild-verified (Go compiles in the Docker builder):**
- **Storage model** `world/character_persist.go`: `CharacterSave`/`Appearance`/`CharacterSummary`,
  `applyStartingKit` (extracted from `AddPlayer` — single source of truth for the starting kit),
  `DefaultCharacterSave`/`applyCharacterSave`/`buildCharacterSave` + load/write/list/delete helpers.
  Collection `character/<charID>`, user-owned, `PermissionWrite:0` (server-only — clients can't forge).
- **RPCs** `rpc/character.go`: `character_list` / `character_create` (name 1-20, max 8/account, unique
  name, appearance defaults) / `character_delete`; registered in `main.go`.
- **charID bridge**: client `JoinMatchAsync(matchId, {char_id})` → `MatchJoinAttempt` validates
  ownership + stashes `WorldState.PendingCharacters[userID]` → `MatchJoin` consumes it, overlays the
  save, picks the spawn (first login = zone spawn_point + `IntroSeen`; else last-logout pos if same
  zone). `MatchLeave` builds the save + writes it async. No-char joins (sync-harness) still work.

**Done, NEEDS an in-Editor C# compile pass (written without a local Unity compiler):**
- **Char select UI** `UI/CharacterSelectPanel.cs` (own top canvas, code-built like UIBootstrap): lists
  characters, Create (name + class/hair/skin picker w/ live paper-doll preview), Delete; on pick stores
  `CharacterSession` + hides → reveals WorldMenu. DTOs in `NetworkMessages.cs`; `WorldMenu.Play` gated.
- **`EnterWorld(zone, charID)`** passes the join metadata. **Local appearance** renders the chosen
  class/hair/skin (`PlayerController.RebuildOutfit` reads `CharacterSession`).
- **Bed = set-home + respawn + first-login intro** (Part E): the existing beds already carry
  `interaction_type:"sleep"` (added it to canopy+bunk too; republished) — NO new art. `OpCodeSetHome`
  (100) + `handleSetHome` (validates a sleepable occupant in range, sets `PlayerState.Home*`, saves
  async) + `SetHomeAck` (101) toast. `handlers_player.go` respawn now wakes at the bed's home when set
  in-zone. First-login intro rides a new `intro` flag on `FullInventorySync` (no join race) →
  `IntroOverlay`. Client `SleepController` routes the bed right-click (PlayerInputRouter chain 1c).

- **Remote appearance + nameplates** (Part F remote): a dedicated `PlayerInfo` snapshot message
  (`OpCode 103`, sent once on join — NOT the per-tick `EntityData`, per that struct's own comment) carries
  each player's class/hair/skin + name. Server emits a roster→joiner + the joiner→everyone in `MatchJoin`;
  client `EntityManager._playerInfo` dict applies it to a live `RemoteEntity` or on spawn (handles
  ordering). `RemoteEntity` gained a shared `RecomposeOutfit()` (kills the hardcoded merchant/blonde;
  armor + appearance converge) + a world-space `TextMeshPro` nameplate (LiberationSans SDF, Occupants
  layer order 960, above the head). Display-only — zero determinism surface.

**Whole character system is now feature-complete** — pending the in-Editor C# compile pass (the client
batch was written without a local Unity compiler) + a nameplate fontSize/scale visual tweak.

## Done 2026-06-14 — crafting system (Stage 1) + item containers
Recipes-as-data + a unified craft model (no quick/slow split — one `process_ticks` speed knob), item
containers, and the determinism boundary. See [architecture_crafting.md](architecture/architecture_crafting.md)
(system) + [crafting_design.md](design/crafting_design.md) (content).
- **Recipes** (`data/entities/recipes.json`, published by glob) → `LoadRecipes` + `RecipesByStation`;
  client `RecipeDatabase`. ~10 Stage-1 recipes on EXISTING art (workbench/stonecutter/anvil fast,
  furnace slow, multi-input).
- **One craft model**: right-click → recipe grid → have/need + qty → Craft (inputs leave the bag) →
  process at `process_ticks` (a bar fills) → **output grid** → "Get all" / double-click (overflow stays).
- **Container primitive** (`ContainerState`) + **`CraftStationState`** — lazily created on first open;
  one `OpCodeContainer` (98) action opcode (`quick`/`move`/`craft`/`collect`/`get_all`/`set_recipe`) +
  `OpCodeContainerUpdate` (99) echo. Double-/shift-click quick-moves stacks.
- **Item tags** (`clothing`/`food`/`metal`/…) + a **storage audit**: 20 furniture pieces got
  `world.container {slots, filter}` (chests generic; wardrobe→clothing, bookshelf→book, fridge→food, …).
- **Determinism**: crafting/containers are display/inventory state, NEVER in the sim hash; compost +
  the food ledger untouched.
- **Test**: `crafting_test` zone (in the WorldMenu) + an F8 "Give crafting kit" debug button.
- ⚠ **Needs a server rebuild** (Go) + an **in-Editor C# compile pass** (the new client UI was written
  without a local Unity compiler — expect to iron out small panel issues on first run).

### Crafting — deferred (Stage 2 / later)
- **Player persistence → learned/bought recipes** + the NPC recipe economy (the `unlock` field is in
  the data, unused by the gate). Ties to the locked HUD NPC buttons.
- **Themed station UI** (the Apico touch): per-station panel art — the smelter's fuel + ore input
  slots + fire/heat meter + fuel tank; `panel_craft` frame (see art_needed.md). Stage 1 = generic panel.
- **Precise drag-drop** between container/bag (server `move` op exists; client drag wiring deferred —
  Stage 1 is double-/shift-click quick-move only).
- **Sawmill/loom recipes** (placed in the test zone but no Stage-1 recipes yet) + the new-output art
  batch (bars, plank, glass, cloth, …).
- **Fridge food rot-prevention**, a persistent **fuel tank + heat meter**, **inventory expansion**
  (bigger backpack → tag-based sort/filter), **craft-from-nearby-chests** QoL, **station-chaining**.
- **Bee/honey**, **leather source** (no bug-leather), **electronics bench** (when electricity lands).

## Done 2026-06-14 — heavy/light rain + lightning/thunder, torch placement tool, dry-soil + hands
- **Weather v2 visuals**: rain Light/Heavy presets (parallax streaks + splash layer + gusting wind +
  overcast tint), Heavy = lightning flash (global-light) + synth thunder; F8 intensity toggle + Strike.
- **Torch = the first "placer" tool**: `tool_type:"placer"` → left-click places the occupant centered
  on the target cell (no ghost; blocks keep right-click+ghost), shown in-hand + glows. Tall sprite fix
  (was square 16×16 → mushroom; now 10×20). See `architecture_items.md`.
- **Dry tilled soil** lightened (distinct from wet). **`hands`** removed from the starting hotbar
  (grab verb → the grabbing/pushing/shoving backlog item).
- Scaffolding: CLAUDE.md quality directive; `regenerate-sprite` skill hardened (aspect-ratio check,
  missing-catalog-row, pixelclean churn).

## Next — HUD: bigger hearts + access-button bar (planned, not built)
Plan exists (`~/.claude/plans` / the torch+HUD plan). Bigger/nudged hearts; bottom rounded-square
access buttons (Inventory works; Ecologist/Mayor/Herbalist locked w/ toasts); Apico-style layout
(hotbar→top) OR keep bottom — DECISION pending. Needs `UIFactory.MakeButton` + `btn_square` art + a
reusable `ToastUI`. Also backlog: how players learn WHERE those NPCs are.

## Next — perf: bound the ground-item pile (decay pass grows O(items))
**Diagnosis (2026-06-22, investigate-only):** the `decay` system pass climbs monotonically over a run
(33k→435k µs/game-day on `village_21_B`, 8 days) because **ground-item count keeps growing** —
`processGroundItemDecay` ages EVERY item each tick (inherently O(total items); a spatial index does NOT
help it). The accumulator is **rotten fruit from fruit trees**: lifetime `rottenFruitDecaySeconds = 5040s
= 6 game-days` (`handlers_farming.go:29`), produced continuously by trees + windfall, faster than flies
eat or it expires, so it builds toward a high 6-day steady-state. Carcasses (`killDropLifetime = 60s`) are
negligible. Matches the documented old "immortal-rot → 40k+ items" history (`zone_persist.go:500`).
**Fix options (separate effort):** (a) **expiry-bucket the decay pass** — schedule each item's despawn
tick in a per-tick bucket so decay processes only items expiring this tick (O(expiring) not O(all)); and/or
(b) **bound the standing rotten-fruit count** — shorter rotten lifetime, a per-cell cap, or a lower tree
drop rate (a gameplay/ecology lever — run it through the 6× bug_lab chart loop). Verify: equivalence /
sim-determinism + re-profile that `decay` flattens. Note: the FindNearbyFood chunk index already removes
the *food-search* sensitivity to this pile (committed); this item is specifically the decay-pass cost +
the underlying unbounded accumulation.

## Later — creatures: ants & spiders (DESIGNED, not built)
Full approved design: **[design_ants_spiders.md](ecology/design_ants_spiders.md)**. Ants = a foraging colony
(hill/queen/eggs reuse Nest+Brood; workers forage carrion → carry home via the wasp provisioning loop;
scouts + server-only "colony memory" make trails emerge — no per-cell ACO grid). Spiders = a web-builder
ambusher (web tiles slow prey via a server speed-debuff; reuse occupant placement + `OCCUPANT_BLOCKS_BUGS`)
+ a jumping/stalk-pounce hunter (reuse the centipede `ActionState` lunge). Determinism-light (ant trails add
zero sync surface). Build spiders first (lower risk); ants are Med–High complexity. Includes Step 0 = the
rotten-fruit decay fix (bound the pile).

## Later — content layer (agriculture + crafting depth) + station minigames
- **Flesh out agriculture & crafting (finish the content layer):** the systems exist (crops, crafting
  stations, recipes, containers); this is the CONTENT pass — more crops/recipes/stations/products, the
  progression that ties them together, and the missing art. Needed eventually, not now.
- **Station minigames:** interactive minigames at craft stations (e.g. a timing/skill step when smelting,
  brewing, etc.) instead of a pure timer. Polish/engagement layer on top of the crafting system.

## Later — sprite review (manual, by hand)
Go through EVERY sprite by hand and fix/redo the ones that read wrong (Andrew edits on his end). Many
were auto-generated; quality varies. NB: a bare `pixelclean.py` re-cleans ALL sprites — regenerate +
clean ONE key at a time and revert incidental churn.

## Done 2026-06-13 — day/night lighting actually works (root-caused after 2 failed passes)
Night was never dark — only point-lights were added, so deep night was the *brightest* time.
ROOT CAUSE: TWO global Light2D at runtime — a static `Global Light 2D` baked in `SampleScene`
(intensity 1, never touched by code) plus the controller's ramped one; URP 2D accumulates globals,
so the static one pinned the world bright and defeated the night ramp (prior fixes wrongly
brightened point-lights). Fix (client-only, no new art/data — see `architecture_weather.md`):
(1) `DayNightController.Start` adopt-one-global pattern — drive the first global, disable extras,
never leave zero; (2) removed the always-on `PlayerNightLight` base glow → no light unless a torch/
lamp is the selected hotbar item (already in the starting kit) or a torch is placed (Terraria-style);
(3) `DebugNightIntensityOverride` + an F8 "Night darkness" slider to tune the floor live. **Verify
pending: in-Editor F8 (Night → dark; hold/place torch → pool of light; never pure black).**

## Done 2026-06-13 — client freeze fix: the logging storm (investigation + cause fix)
Overnight investigation (`crash_investigation.md`) found the in-Editor client freeze was a
**client-side synchronous-logging storm**, not a server bug. With `useMainThread:true` (NetworkManager.cs:67)
every match-state callback runs on the Unity main thread; per-tick/per-message logging there did
~125 lines/tick, each a `Debug.Log` → synchronous `ExtractStackTrace` **and** a `DebugFileLogger`
file open/append/close. The session Editor.log was 2.4 GB / 31.7 M lines. The stalled main thread
couldn't drain the socket → Nakama closed the session `session outgoing queue full` (×10) → no client
reconnect → frozen client, live server. Fix (client-only, no `.so`): `SetStackTraceLogType(Log/Warning,None)`
in UIBootstrap; a default-off `DebugConfig.Verbose` gating the hot Debug.Log sites + DebugFileLogger
internally; removed the defeated tick-gate throttle (canAdvance toggles every tick); plus an
unrelated `HotbarUI.Start` NRE guard (leftover-scene null `slots`). **Verify pending: in-Editor soak.**

## Done (recent) — DETERMINISTIC SPAWNS + INDIVIDUAL-FLY PREDATION (deterministic lockstep)
- **Phase 1 — deterministic swarm creation:** swarms are now CREATED at a deterministic, cross-client-agreed
  tick (new `SWARM_SPAWNED` ledger event + first-joiner/reconnect `ZoneAuthority` seed-baseline + the
  late-join snapshot); `SwarmUpdate` no longer creates swarms (creating on-receipt at an arbitrary local
  tick was the pinned spawn-tick desync). Proven: the staggered late-join harness (`tools/run_sync_latejoin.sh`)
  shows 19,074/19,074 shared-bug states bit-identical across a late join with runtime spawns.
- **Phase 2 — individual-fly predation:** hornets/wasps/centipedes now strike the actual NEAREST INDIVIDUAL
  fly by its position (not the swarm centre). The hunt economy stays server-side; the AUTHORITY client (which
  has bit-identical per-bug positions) computes the strike and reports victims via `OpCodePredationStrike` →
  `handlePredationStrike` → `applyPredationStrike`; the kill rides `BUG_REMOVED` (frontier-gated) so all
  clients stay bit-identical. Per-victim snatch telegraph. Proven: harness IDENTICAL (21,734/21,734) through
  9 real strikes; `go test ./world/` green; `tools/sim-determinism` PASS.
- **Phase 1b — zone-complete `blocks_bugs` collision (DONE):** the bug sim now collides against a ZONE-WIDE
  collision set on every client, decoupled from the camera — closing the last cross-player desync (bugs near
  a fence that only some players had loaded used to diverge). The server sends each joiner the complete
  blocks_bugs cell set on join + resync (`OpCodeZoneCollisionMap` 106, built from ALL zone chunks incl. those
  not yet in memory — loaded transiently from disk, no RNG init); dynamic place/break rides a frontier-gated
  `OCCUPANT_BLOCKS_BUGS` ledger event so every client toggles the same cell at the same tick. Client reads
  `TilemapManager._blocksBugsZoneWide` (was view-scoped `_loadedChunks`); the bug sim gates on the map being
  ready (timeout fallback). **Proven:** spawn-apart harness — two clients loading DISJOINT chunk halves both
  hydrate the identical 4322-cell map → collision is camera-independent; co-located regression unchanged;
  residual divergence is the pre-existing late-join snapshot leg residual (confirmed identical pre-1b at 1.2%
  via a baseline build, so NOT introduced here — see [[#127]]); `go test ./world/` green; `sim-determinism` PASS.
- **Determinism hardening + teachability (DONE 2026-06):**
  - **Test framework (sacred):** found+fixed a real harness defect — both `run_sync_*.sh` inlined a diff that
    let 14-col leg rows collide with bug-id 0/1 keys (could MASK a divergence). Extracted one canonical
    `tools/netcode/sync_diff.py` (stops at `# SWARMLEGS`, requires the 15-col bug shape, adds the per-tick whole-state
    HASH stream as the PRIMARY gate), unit-tested by `tools/netcode/test_sync_diff.py`. Harness now asserts spawn-apart
    clients are DISJOINT (non-vacuity) + has a `FRESH=1` redeploy helper.
  - **#127 (DONE):** late-join now mints window-created bugs by REPLAY at evt.tick (not metadata prespawn),
    so a bug reproduced in the snapshot-lag window no longer drifts. Proven: co-located AND genuinely-disjoint
    spawn-apart late-joins are bit-identical — 0 bug + 0 hash divergence; `sim-determinism` PASS.
  - **Docs/skill:** `architecture_swarm_sync.md` §0 as-built quick reference (guarantee + the one invariant +
    ledger glossary + add-a-mechanic recipe); new `frontier-sync` skill; `determinism_audit_2026-06-20.md`
    marked SUPERSEDED + indexed in ARCHITECTURE.md; `lenses.md`/`complex-change-review.md` cross-linked.
- **Accepted (self-healing, not fixed):** the empty-bootstrap window (#137 — a late-joiner in the ~1-frame
  gap before the authority's first snapshot; converges via drift-resync; the on-demand-snapshot round-trip
  costs more than it's worth for a self-healing transient) and the continuous-spawn on-receipt-vs-hash sub-1%
  caveat. Both documented in `architecture_swarm_sync.md` §0.

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

## Done 2026-06: village_21_B (the natural rebuild) + zone-authoring scaffolding v2
- The candidate-replacement zone (joinable as "Village B"): one bending main road with
  bevelled curves (the road-angle system: composited diagonal tiles + smooth_paths),
  multi-blob lakes + shore_dress arcs, compose-in-place core (upgraded plaza at the
  bend, general store composed, varied composer houses), solid rock_mass mining
  sneak-peeks abutting the lake, forest-ring masses with dirt floors, orchard/wheat/
  fly-farm belt, NE centipede gloom, no-dead-grass fill. Scaffolding: ZoneBuilder.blit,
  lint v2 (road-tile net, spawn-circle-water, potholes), 3 test-scene cards.
- Centipede knots (multi-centipede swarms) + overshoot lunge + turnaround re-attack;
  water stops people only (bugs fly over).
- THE ROAD-THROUGH-BUILDING root fix (the 4x "buildings overlap roads" class): house/shop
  interiors RESERVE at place-time, path() refuses building cells + warns loudly on
  reserved crossings, lint flags road cells walled on both sides; residential lane
  re-laid STRAIGHT in a scan-verified corridor (W-lane connector at x44), farm lane
  y186, U-house +2 (zero warnings). Player-farm pond pulled off the fence row.

## Done 2026-06 (overnight): procgen research + routed roads + natural houses
- research_procgen.md (3-track web sweep, adopted/passed-on scoreboard).
- terrain.route_road (least-cost-path: network discount, turn penalties,
  multiplicative noise hills, route-to-network spurs); main road + farm lane
  routed in village_21_B; town segments pinned (settlements straighten roads).
- terrain.noise_field/ring_mask: the forest rim is a noise mask (calibrated).
- house.sculpt_plan + l/u/z_house + porch + the LANDMARK BUDGET; scene_houses
  v2 card; village_21_B street = U showpiece + L+porch + cottage.

## Later additions from this slice
- route_road taper option (band narrows at zone edges, like path(taper_ends)).
- Chaikin smoothing pass on route_road centerlines (research; only if 45°
  quantization ever shows through smooth_paths' bevels).
- **The river-zone slice**: the stream + `terrain.bridge(b, start, end)` (engine-free —
  walkability is the tile-id switch; bridge tiles replacing water are walkable both
  sides). Recorded geometry from review: a gx≈40-50 stream needs TWO bridges
  (≈(44,130) + ≈(47,182)) or it walls off the west third.
- **Player-placed road AUTOTILE**: when tile placement lands, run the smooth_paths
  neighbor rule server-side on placement — no manual sprite flipping.
- Occupant-on-water support so lily pads can live in SAVED zones (today decor =
  render-only; the boat-store furniture un-reserves water as a special case).
- Side-door TEXT-GRID pieces (composer + place_room already do all sides).
- A leaf-litter/forest_floor ground tile (deep forest uses dirt=True meanwhile).
- A frog ambient critter for the lake (intent doc wish).
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
  events + writes the population CSV (`tools/ecology/plot_fly_counts.py`).
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
  test-zone generator (`tools/world/make_test_zone.py`), `sim_test` zone; single-source zone config
  (removed `debug_mode` + `species_debug.json`).
- New world-select login (`WorldMenu`).

## Done (recent) — overnight: new scenes + bug pipeline + encyclopedia
- **Blocks/walls — MISTAKE, being corrected:** an opaque-generation change I made (`is_block_like` →
  `background="opaque"`) was WRONG — it baked black/white backgrounds and the blocks didn't tile; a
  related `ab_generate` bug turned `cave_floor` into a chest. Reverted to the standard transparent+crop
  flow; regenerating each block/wall as 2 variants matched to `wall_stone`, verified with
  `scene_block_tiling.py`. `wall_stone` (untouched) is the standard. Guide rewritten with HARD RULES.
- **A/B sprite workflow:** `tools/sprites/ab_generate.py` (A live + B in `tools/_generated/ab/`) + `contact_sheet.py`
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
- **Encyclopedia (`docs/product/design/encyclopedia.md`) + `brainstorm_items.md`:** ~50 bugs (incl. water bugs)
  across ~16 families ×3 difficulty tiers + 21 new plants — data + catalog + A/B sprites being generated.
- `docs/product/investigations/underground_review.md` — proposals for camp + ant-colony additions.

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

## Done 2026-06: multi-frame sprites SOLVED via pixkit (hand-authored, not gpt sheets)
The text-grid toolkit (tools/player_sprites/pixkit.py) made animation a derivation, not an
art problem: player walk cycle (4 frames x 4 dirs, mechanical leg-shift+bob from one master
grid per direction), paper-doll layers (body/hair/shirt/pants/chest/helmet, region-filtered,
registration by construction), wearables, and 4 hand-authored vegetable crops with stage art
(carrot/pumpkin/cabbage/eggplant). CharacterComposer.cs composites layers at runtime;
F6 cycles debug outfits. Remaining from the old item:
- **Segmented bugs (centipede/millipede) head/body/tail sheets** — could now be pixkit grids too.

## Done 2026-06: programmatic UI + ARMOR SYSTEM + bug info card
- ALL inventory UI now code-built (UIFactory/UIBootstrap own canvas; zero scene
  wiring): hotbar strip + EDGE-DOCK inventory screen — the center stays open
  world so you SEE your real player while equipping (the game never pauses).
  Hand-authored UI art kit (tools/sprites/ui_sprites.py: wood/parchment 9-slice, slot
  frames, ghost silhouettes, keycap-E).
- ARMOR (cosmetic + synced): leather + iron sets (region-derived legs/feet fit
  the walking legs by construction) + 2 accessories; items.json armor entries;
  PlayerState.Equipment[7], OpCode 96 {equip_slot, inv_slot} (swap-safe),
  OpCode 97 echo, EntityData.eqa; spawn wearing leather; click/drag +
  right-click quick-equip; local AND remote players re-compose live. 5 Go tests.
- Bug info card (right-click a bug slot): freely-known tier + locked rows
  shaped for the research mechanic. Pickup polish: drops 0.9-cell fit +
  0.6 floor, honest keycap-E badge. Starting inventory freed (E-pickup fix).

## Next — client reconnect / self-heal (deferred from the 2026-06-13 freeze fix)
The logging fix removes the *cause* of the `session outgoing queue full` close, but the client still
has NO reconnect — `NetworkManager.Socket.Closed` only logs + invokes `OnDisconnected` (sole
subscriber: DebugPanel). Make a server-side close self-heal instead of freezing. Done correctly it
must: clear `WorldManager.CurrentMatch`, reset SwarmManager via the existing `RequestResync()`
(SwarmManager.cs ~580), re-check session expiry before reconnecting, and wait for
`ZoneAuthority`/`LateJoinSnapshot` before resuming ticks. Repro: kill/restart the server mid-session.

## Next — Tool ANIMATION improvement (Andrew, 2026-06-12)
The in-hand tool animations (PlayerToolAnimator swing/sweep/stab/pour) need a
quality pass — the profiles are functional but stiff. Candidates: anticipation
frames (wind-up before the arc), easing curves instead of linear sweeps, a
small body lean on swing (the walk-frame rig makes 1px shifts cheap via
pixkit), impact pause/flash on hit, tool-specific follow-through. Pairs well
with the existing walk-cycle rig since both are code-driven.

## Next — Bug RESEARCH mechanic (the magnifying glass) + food boosts
The bug info card ships with locked rows ("Breeding: ???", "Favorite foods:
???") — this fills them:
- magnifying_glass item; per-species research level on PlayerState (use it X
  times on a species to unlock tiers: breeding plants -> favorite foods)
- food-source boosts: flowers/foods grant swarm bonuses (data per species)
- BEES (later): produce honey; gain more from some flowers — the info card's
  foods tier is where players learn this in-game
- armor DEFENSE (cosmetic now): armor_class per piece, server damage reduction

## Superseded 2026-06 (this slice shipped it) — was: armor server sync
Art + local rendering shipped; making OTHER players see your outfit needs:
- `PlayerState.Appearance { SkinTone, Hair }` + equipment slots `{ Head, Chest }` in Go
- items.json wearables get `equip_slot` (+ the armor pieces as obtainable items)
- EntityData join/update payload carries appearance + visible equipment
- RemoteEntity feeds CharacterComposer instead of LoadBaked("farmer")
- An equip UI (replace the F6 debug cycle)

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

## Decided against
- **Sideways / rotated furniture (side + back facing variants + place-rotate)** — explored 2026-06-24
  (gpt-image-1.5 re-edited 8 pieces to `_side`/`_back`, separate placeable keys, server `resolveFacing`,
  a place-time R-rotate + a furnished showcase house). **Scrapped**: most JRPGs don't rotate furniture, and
  in this strictly-flat 3/4 projection the side/back views add art + placement complexity for little payoff.
  All variant sprites, the rotate code, and the showcase zone were removed. The reference-image re-angle
  TECHNIQUE survives for animation (see the fly/butterfly flap work) — only the furniture product use is dead.

## Now/Next — economy, gear & town NPCs (DESIGNED — see `economy/`)
Full design folder: [`docs/product/economy/`](economy/README.md) — **start at the README map.** Reorganized
2026-06-25, one-concern-per-file: `progression.md` (pacing/gating + village scope, lens-justified),
`crafting.md` (the master recipe/cost table — all categories incl. sprinklers, bug-derived + artisan goods,
target floors), `merchants.md` (the 3 shops + craft-vs-buy matrix), `production.md` (**build waves — start
W1**), `DECISIONS.md` (every decision, resolved + open). Geography for it is in
[`architecture_world.md`](architecture/architecture_world.md) (restructured 2026-06-25: **rows 0–4** with row 5 deferred,
underground col-0 centipede→ants + Queen, Centipede Cavern→(4,1), + a resource/material dispersion map §1b).
**Zone authoring of the new 0–4 layout is its own backlog effort.** The **content** is now designed in full:
`economy/zones/` (17 per-zone content sheets) + `economy/catalogs/` (28 armor sets, 82 weapons, 88
accessories, ~102 tools, 78 potions + 47 meals, ~315 materials) + `species_and_drops.md` (84 species) —
intentionally over-produced to **prune down**, then wire via `production.md`'s waves. The big build items:
- **Player bonus/stat layer** (the foundation) — add a `bonuses{}` block to the item schema + a derived
  `PlayerStats` recompute on equip; wire `defense` + `damage_pct` into combat first so armor/accessories
  finally DO something. Today the only working bonus is the backpack `slot_bonus`.
- **Currency + merchant economy** — `coins` on `CharacterSave`, buy/sell RPCs + merchant panel (reuse the
  crafting/container plumbing). `sell_price`/`buy_price` are already priced in data; no RPC/coins yet.
- **Town NPCs (merchant, blacksmith, carpenter)** — new `interaction_type:"npc"` occupant + a dialogue
  panel: intro line on first meet (track "met" in `CharacterSave`), random tip thereafter. Sprites exist
  (`merchant_down`/`miner_down`/`farmer_down`); persist them via `place_occupant` instead of preview-only
  `place_player`. Ecologist/Beekeeper reuse it later (GDD §13).
- **Material stations + ladders** — sawmill (planks), loom (cloth), forge (steel/alloys), cauldron
  (potions), stove (meals), jeweler (accessory gems), honey_extractor — data + recipes once art lands.
- **Recipe acquisition** — per-character known-recipes set + the auto/buy@npc/find content split.
- **Gear content** — armor tiers, utility outfits (bee suit, fisherman's vest, miner kit…), accessories,
  trade-off ("bonus-while-detrimenting") items, consumables.

## Later — mining depth (the loop is thin; flagged 2026-06-24)
Mining is currently "tool_tier gates ore → break block → get ore" with no risk, variety, or reason to go
deep — and several designed gear bonuses (`ore_fortune`, `gem_luck`, `light_radius`, `hazard_resist`,
`fall_resist`, miner's kit) have nothing to hook onto. To make it a real loop (details: `economy/suggestions.md §4`):
- **Depth + risk**: deeper layers = better ore + hazards (darkness, gas pockets, fall drops, cave-ins).
- **Yield variety**: `ore_fortune` (double drops), `gem_luck` (gems/geodes in plain stone), rare nodes.
- **Tools beyond the pick**: drill (fast/AoE, later electric §11.6), dynamite (already a concept), ore
  cart/rail haul, prospector/vein-sense tools.
- **Deep-only materials** (mithril/adamant) that gate the endgame gear in `economy/item_catalog.md`.
- **Light as a real stat** — `light_radius` (lanterns/headlamp/placed torches); the flashlight is cosmetic today.

## Later — mechanics flagged by the economy content pass (2026-06-25)
These came out of designing `economy/zones/` + `catalogs/`; each needs its own design before wiring. See
`economy/DECISIONS.md` D10–D16.
- **Electricity (a whole EXPANSION)** — drills/powered mining run on **batteries** (buy, or find in chests) for
  temporary power, until a **battery recharger** unlocks. Recharger is gated by **WEALTH, not zone**. Treat as
  a large standalone expansion.
- **Signposts** — fast-travel/landmark posts (per-zone hub, unlock-on-visit; `architecture_world.md` already
  sketches the road+signpost system).
- **Cart system** — rail carts go left/right/up/down (diagonal TBD); lots of payoffs to weigh. *Research how
  Minecraft minecarts work* (powered/detector/booster rails, momentum) before designing.
- **Dredge mechanic** — place-on-water → station "dredge" button → player drags a hose and clicks water to
  dredge like a tool; weaker/stronger + condition variants (swamp dredge). Get the feel right (D14).
- **Potions & alchemy system** — the cauldron potion-crafting + buff/cure layer. (Venom/poison combat
  *effects* are assumed real mechanics, D16; this backlog item is just the potion-making system.)
- **Fishing** — a fishing **mini-game** + rod tiers + passive capacity-capped fish traps (no harpoons). Bows
  + **cast/thrown nets** + **bug-size matching** (a small net can't hold a big bug) ride along here.
- **Beekeeping system** — multi-level beekeeping: faster/stronger bees, some **hostile**, smoker tiers (≥3),
  hive management. The bee zones' content hangs on this.
- **Armour balance** — tune per-set DEFENSE against each zone's enemy damage once combat numbers exist (D11).
- **Home-plot décor bonuses** — the capped idle/comfort aura system (GDD §11.5) that décor + light décor feed.
- **Mining processing** — rock crusher → `paydirt` (final name TBD) → sluice refine loop (D13).
- **Bug Extractor** (D18) — a clean in-town station that processes `dead_<bug>` → materials (chitin, silk,
  venom, leather…) AND feeds bug-based cooking. Replaces per-bug ground drops + the old bug-leather station.
  Needs: the station + the extraction recipe table (which dead bug → which material).
- **Food / cooking system** (D19) — cooking recipes are a separate system from crafting; the village ships one
  starter meal (`forager_stew`) and the player cooks freely. Design the cooking system + recipe set later.
- **Land deeds** (D20) — the Mayor's plot/land-ownership system (separate from the merchant economy).
- **Boats / vehicles** — the Fisherman sells a boat (water traversal); design the boat mechanic + cost.
- **Store inventory rotation** — randomized/rotating merchant stock with a few rare/expensive "teases" (a peek
  at high-end gear from the start).
- **Chests** (user request) — storage chest behaviour/UI pass.
- **Size-by-growth** — centipedes/millipedes grow ~0.5→×2 as they eat (new deterministic sim mechanic; static
  small/large variants ship in the meantime).
- **Projectile-spit** — a deep tough-area **cave beetle** that spits projectiles (new ranged-combat sim
  mechanic; frontier-sync + test-changes gates).
- **Station "crank-to-charge" mini-game** — most stations take an active crank input that charges them to run a
  while (the sluice hand-crank is the first); client mini-game + server charge state.
- **Cave species + sprites** — `cave_beetle`, `glowworm` (green, catchable light), small `cave_spider`, the
  **green garden centipede** (village) + **cave millipede** (millipede ×0.5); cave centipede reuses the current
  centipede sprite. Plus a **`rock_crusher`** + tube/pipe sprite for the mining camp (stand-in `coal_bin` bins
  used for now). Then wire the cave critters' real diets/breeding + the underground ecology tuning pass.

## Later — captured, not scoped yet
- **Tune bug animations, including speed and size** — the cosmetic flap/buzz frames + the per-species
  anim profile (FlapFps / GlideSecs / Bob, in BugVisual + SwarmVisual) and each animated species' frame
  pixel size (the downscale target) want a pass for feel: wing-beat speed, hover jitter, and on-screen
  scale per species (fly buzz + butterfly glide are the first two; more species as they get frames).
- **Grabbing / pushing / shoving** (Andrew has the design; to detail later). Replaces the old
  "hands" slot-0 grab verb, which was pulled from the starting kit 2026-06-14 pending this rework
  (empty slots still bare-hand grab in the meantime).
- **Weather system expansion** (rain light/heavy + lightning/thunder shipped 2026-06-13; the
  client preset is a seam for the below):
  - **Intentional droughts** — gameplay weather; Andrew has design ideas (his to scope).
  - **Fog** — layered scrolling noise + depth/parallax + 2D-light interaction (NOT a flat tint);
    own research pass. A SEPARATE self-activating component reading the weather state, not a
    branch in RainController.
  - **Dust storms** — horizontal driven sheet; same component pattern.
  - **Per-zone / server-driven weather + intensity** — when the multi-zone system lands, the
    server picks weather kind + intensity per zone (today `RainController.Intensity` is a client
    F8 toggle and "rain" is one state).
  - **Rain polish** — URP post-process color-grade while raining (desaturate/vignette), puddle
    accumulation; extract a shared `WeatherVisual` base once fog/dust make it rule-of-three.
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
