# Changelog — finished work

Sections moved verbatim from `BACKLOG.md` on 2026-09-26 (nothing edited), newest first as they appeared
there. The open queue is [`BACKLOG.md`](BACKLOG.md); the plan is [`ROADMAP.md`](ROADMAP.md).

## Done 2026-09-30 — saves, steps 5–8: one save queue, one copy per zone, one zone at a time per character (D73)
- **One save queue for the whole server** (`persistence.go`, `save_writer.go`, `save_batch.go`). Each zone save is a
  batch — the zone plus the character of everyone in it, and of everyone leaving — captured at one tick and written
  in one transaction, in order. So after a crash or a restart, each zone and the characters in it come back from the
  same moment: an item put in a chest can no longer end up in the chest and the bag, or in neither. Zones save every
  minute while someone is in them, whenever someone leaves, after a sleep in a bed, and at a clean stop. A database
  error retries the same batch until it lands; if something else changed a zone's save, saving stops (and says so in
  the log every 30 s) rather than overwrite it.
- **One live copy per zone** (`zone_lease.go`; the ROADMAP's latent bug 2): every request that starts a zone goes
  through that zone's lock; a copy whose match died is retired before a new one loads its last save, and anything
  it tries to save afterwards is refused; the debug panel can no longer start a second copy of a running zone.
- **One zone at a time per character** (`char_registry.go`): a character enters the next zone only once the zone it
  left has saved it, so crossing zones no longer duplicates items. A second copy of the game in the same zone takes
  over (the older session is sent out and saved first, so the live bag is kept); one in another zone waits. Joins
  carry an entry pass that expires after 8 s, so a join Nakama has already reported as timed out can't leave a ghost
  holding the character. A character in play can't be deleted.
- **The game's side** (`WorldManager.cs`, `CrossZoneController.cs`): entering sends the character and its pass; a
  "busy" answer is retried behind the fade for up to 15 s; a crossing that still fails takes the player back to the
  zone they left with a short message (the ROADMAP's latent bug 6, except when that zone can't be entered either);
  the character screen shows why a delete was refused.
- **Verified:** the saves crash test, all four cases PASS — before: a crash lost 5 fences (45), a crossing arrived
  with 50 after leaving with 45, a reconnect saw the stored 50 instead of the live 48; after: 50, 45, 48. The new
  crossing test in the real game client (`tools/run_crosstest.sh`) PASS: 48 fences arrived after a failed crossing,
  a normal one and one refused as busy. Go tests with the race detector (a unit test for each row of both state
  tables); sim-determinism; `harness_persist_test.sh`; the crosszone and reconnect harness runs; the two-player sync
  gate with the late joiner entering as a character, together (89,420 states, 242 hashes) and apart (93,595 states,
  249 hashes): identical.
- **Docs:** `architecture_persistence.md` (the save queue, one live copy, the character registry, the game's side,
  the gates), `architecture_world.md`, `architecture_bugs.md`, `architecture_swarm_sync.md` §11.1, GDD §19, the
  test-changes skill, `tools/README.md`.

## Done 2026-09-30 — saves, steps 2–4: trustworthy tests, the crash test, and a save that costs ~1 ms (D73)
- **A faithful stand-in for Nakama storage** in the save tests (`storage_fake_test.go`), copied from Nakama 3.35's own
  storage code: versions are md5 of the value, `*` only creates, a stale version is rejected, every write is
  all-or-nothing, listing with no user id covers every user, deleted accounts are refused, failures can be injected.
  `RACE=1 bash tools/run_go_tests.sh` runs the race detector.
- **The saves crash test** (`tools/harness_crash_test.sh`): a scripted player with a real character (`--char`) in the
  test zones `persist_a` ↔ `persist_b`; fences in the world + in the bag must stay 50. On today's server it reproduces
  the faults the rest of D73 fixes — a crash lost 5 fences (45), a zone crossing duplicated 5 (arrived with 50 after
  leaving with 45), a reconnecting second copy saw the stored 50 instead of the live 48; a clean stop already passes.
- **A zone's save costs ~1 ms instead of ~110 ms** (fully loaded village_21_B): cells are compared by their bytes first,
  and the authored chunk files are read once per match (`BaseChunks`). So zones can save every minute, as decided.
- **Verified:** Go tests with the race detector; sim-determinism; `harness_persist_test.sh`; the crash test; the
  two-player sync gate together (85,961 states) and apart (89,384 states): identical.

## Done 2026-09-30 — saves, step 1: a clean stop saves every zone with its players (D73)
- **A clean server stop now saves each zone together with the characters still in it**, in one write
  (`MatchTerminate` → `writeFinalSave`), then stops the zone at once (`MatchTerminate` returns nil). Until now Nakama
  was given no shutdown time (`shutdown_grace_sec` defaulted to 0), so a stop halted every zone with no save at all.
- **Config:** `nakama/data/local.yml` `shutdown_grace_sec: 15`; `docker-compose.yml` `stop_grace_period: 30s` (the
  container is recreated; `docker inspect` shows `StopTimeout` 30).
- **Rebuilding while someone plays no longer crashes the server:** the builder renames the new plugin into place
  instead of copying over the file the server has open. Reproduced first — overwriting it under a connected player
  killed the server (exit 139, SIGSEGV; the player got 116 ticks in 40 s); with the fix, the same test ran with no
  restart (450 ticks).
- **Wipe scripts** (`tools/harness_persist_test.sh`, `tools/ecology/run_config.py` incl. its retry): stop → wipe →
  start — a running server's final save would otherwise write a wiped zone straight back — and only keys starting
  with exactly `<zone>:` (a wipe of `village_21` used to take 41 records across village_21, village_21_B and
  village_21_lab; now 15, all village_21's).
- **Verified:** Go tests incl. `final_save_test.go`; `harness_persist_test.sh` PASS, with a new check that the stop
  itself wrote the save — and FAIL with the shutdown time switched off (the control run); the rebuild test
  before/after; sim-determinism; the two-player sync gate, players together (all 80,775 shared-bug states and 245
  tick hashes identical) and apart (all 85,836 states and 248 hashes identical, the two players on disjoint chunks).
- **Docs:** `architecture_persistence.md` ("The clean stop"), `architecture_world.md` (saves are per zone, not per
  world), `architecture_bugs.md`, `architecture_swarm_sync.md` §11.1, GDD §19, D73, and the run-backend,
  bug-spawning and test-changes skills.

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

## Done 2026-07-06 (later) — THE OWNER'S SEVEN CORRECTIONS, BUILT (bee_meadow rework II)
One session, all seven owner corrections landed as guides + ledger entries + code + a
connectivity GATE, all zone gates green (lint 0/0, save, smoke, crosszone both ways):
- **C14 households**: place_cottage rebuilt — shared shells, per-HOUSEHOLD furnishing specs
  (fisher net-room / farmsteader pantry+vanity / Maren's bee home); house.md gains the
  "Making DIVERSE houses" ontology section (trade room, wealth, signature, tidiness, room jobs).
- **C19 brewing backroom**: extractor/wine-rack/honey-shelf/keg moved INSIDE Maren's cottage;
  the pen keeps yard work only. **Bee stations**: the 4 hive tiers collapsed to TWO placeables
  (bee_station_small 1x1 / bee_station_large 2x1), Maren's shop + species nest list updated
  (old beehive_* kept as legacy for the village's placed boxes); + 4 bee-decor entities
  (skep, beeswax candle, honey-jar shelf, honeycomb rug) — all placeholders, in art_needed.md.
- **C15 connectivity**: a BFS ROAD GATE in the zone build (fails the build on any gap) — it
  immediately found the farm-trace stub AND a north footpath that had NEVER touched the road;
  joint WELDS at every waypoint + bridge exit; worn lanes are surface=path so scatter can't
  plant into them; flora-trample clearing for footpath cells.
- **C16 wooded zone**: ~12 new stands — east band, SE shoulder, south corners, NE corner,
  west strip — the meadow is now a CLEARING around the farm (forest.md zone-balance rule).
- **C17 river to sea**: the spring pondlet is GONE; the river mouths into the sea through a
  flared reeded delta (w4), runs w3 under the road bridge and through the gorge to the
  village contract; the hamlet inlet's head pinches closed on a curve (no straight cut).
  **Gorge** now FLANKS the river: 4 masses + full-length bank lips + scree throat.
- **C18 backyards**: fisher's three-sided backyard fence (log pile + stump inside); yard.md rule.
- **Fruit patches**: the 3 pairs became 4 PATCHES of 4-5 (corridor, road fork, south meadow,
  west meadow).
- Open: sprites for the 6 new entities (placeholder squares in-game); village's legacy
  beehive_basic boxes migrate to stations on the village's next pass.

## Done 2026-07-06 — THE ZONE-CRAFT SCAFFOLDING (the skill that teaches zone quality)
Owner directive: build a zone-improvement guide — a new skill that scaffolds zone authoring — built
and VALIDATED by a live run, all phases committed green:
- **The `zone-craft` skill** (craft loop: brief w/ quotas → 2-3 rendered OPTIONS the owner picks →
  build via author-zone → lens pass against pixels → corrections-ledger walk → polish) + routing
  (author-zone starts there; a COLD-agent probe reached zone-craft → CORRECTIONS.md → caves.md
  unprompted and flagged the gorge's own violation).
- **CORRECTIONS.md** (11 owner corrections, one-liners + inline-guide homes) · **Zone & scene
  lenses** in lenses.md (8; five now ★-earned) · **footprints.py** (generated table + --check; the
  2×4 bed is the fixture) · **4 research packs** (composition / mining feel / settlements /
  coasts — procgen-digest format, checkable rules + counterexamples) · **gallery.md** +
  references/ (6 annotated before/after pairs from the real passes).
- **The live run** (the validation): `rock_mass` extended (shell/core/vein_spec; default output
  proven byte-identical ×5 seeds) → ant country rebuilt as THE OLD DIG (7 mineable dirt-block
  masses w/ stone cores + doctrine veins, the ring dig, mounds, the prospector's scratch) and the
  gorge's hand-set ores/stepped stones replaced by doctrine veins + Halloway's claim. The lens
  pass produced 3 build-changing findings (claim scatter, sign-on-lake, no route in). Ore
  MEASURED: 10-21% per mass region, runs not specks, ring-visible; grep gate zero hand-set calls.
  Zone gates all green (lint 0/0, smoke 90 swarms, crosszone both ways).
- **OWNER VERDICT on the live run (2026-07-06): the scaffolding did NOT move the pixels** —
  the result still looked poor: abrupt changes with no gradients, unnatural straight-line
  geometry, and barely any visible difference from before. AND the ant framing was builder
  invention: this zone has no ant colony (the colony IS zone (3,0), mostly underground; the
  south band should shift gradually toward dirt and rock rather than stop at an abrupt dirt
  wall — C12). Postmortem: adopted research rules had no code mechanism behind them
  (the same blob-stamp rock_mass reused ×7); the lens pass was self-graded; brief promises
  were met in comments, not pixels ("aprons = the lanes"). → C12/C13 + agent memory.
- **→ DONE (2026-07-06, the deep-rework session):** south band rebuilt as the gradient
  (gradient_field primitive: warp-meandered frontier, embedded size-varied masses, rubble,
  patchy east woods) · all three scenes OVERHAULED 2-3 real iterations each (beach: backshore/
  dune belt/headlands/wreck debris field/tide pool; hamlet: organic asymmetric inlet + the
  domestic layer — well, berry garden, log pile, shore lanes, commons seats; apiary: premium
  bed row, interrupted-inspection vignette, staged stock, compost line) · 3 zone iterations
  (wild fruit clumps, the Waystone, the Humming Oak, drifts) · then a COLD grading agent
  (village_21_B as the bar) found 4 BROKENs the builder's own pass had passed — road runway →
  waypointed+worn, meadow void → 33 flower/clover/grass drifts, "gorge" pads → bank lips +
  rim boulders + scree, checker stream → widened+reeded — all fixed + re-verified in crops.
  Gates: lint 0/0, save, smoke, crosszone both ways PASS. Primitives grown: gradient_field,
  rock_mass gap/core-noise, coherent forest floors, backshore. roads.md gains the WAYPOINT
  rule; gallery pairs 6-7 rewritten (the OLD DIG kept as a caution). (Ore-tier
  shape-readability sprite pass still queued from the research.)

## Done 2026-07-05 — THE BEEKEEPING MILESTONE (persistence + calming foundations, bees, Bee Meadow)
Six gated phases, each committed green (full record: `docs/product/economy/DECISIONS.md` D31; systems:
`architecture_persistence.md` + `architecture_beekeeping.md`; zone: `docs/product/zones/bee_meadow_20.md`):
- **A0 Persistence (§P):** ONE WorldSave document per zone, THE CLOCK RESUMES, full-fidelity swarms
  (json-tagged, identities kept), reflection-enforced field classification, generation-stamped writes,
  one-time legacy import-then-delete. Replaced the 2026-06-16 multi-record system below (kept for history).
  Fixed latent: GroundItemSeq id re-mint collisions, GnawDamage lost on restart, weather/day reset.
- **A1 Condition/subdual (§C):** the GENERAL calming mechanic on the dead schema stub — one threshold for
  behavior + catching, all three aggression funnels + the damage-funnel belt, the catch gate, the
  generalized smoker + consumables on the ToolUse verb (calm_spray live), explicit fills for all species.
- **A2 Bees:** the prey-less nest-forager branch (decline → shared nectar forage → homing deposits =
  brood + HONEY), dormant claimable hive boxes, nectar-gated recovery/founding, sting-immunity armor
  hook, hand-harvest with the smoke/anger loop; dragonfly + firefly species.
- **B client** (hive harvest + toasts, smoker/consumable routing, firefly glow, bee-suit layer-set) ·
  **C sprites** (13 new: hive/Maren/beach set/bee items) · **D lab gate** (bee arena: self-maintained
  colony, b_reseed 0, honey at cap — run 1 exposed + fixed a REAL phase-handoff sim bug) ·
  **E the zone** (bee_meadow_20: sea/coves/island, stream + 3 bridges at the village contract rows,
  Maren's farm, fishing hamlet, lakes, meadows/forests; crosszone BOTH directions PASS; builder
  neighbors/grid hardening retired all post-save zone.json patching; NEW terrain.bridge primitive).
- **Still backlogged from the milestone:** smoker tiers · smoke_bomb/chill_canister/stun_rod · the
  "weakened" catch condition + centipede capture loop · SwarmMeterUpdate client UI · mead/keg (D26) ·
  4-piece suit set · fishing mechanic (docks are dressing) · day/night spawn gate · the WASP nest-economy
  starve square-wave (predates this work — ecology_tuning_log) · worn-overlay re-anchor (suit look) ·
  LateJoinSnapshot size growth (bee_meadow adds a zone).

## Done 2026-06-16 — zone / farm persistence (farm + bug population survive a server restart)
**SUPERSEDED 2026-07-05 by the WorldSave document (architecture_persistence.md; A0 above) — this
section is history; zone_persist.go survives only as the one-time legacy importer.**
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

## Superseded 2026-06 (this slice shipped it) — was: armor server sync
Art + local rendering shipped; making OTHER players see your outfit needs:
- `PlayerState.Appearance { SkinTone, Hair }` + equipment slots `{ Head, Chest }` in Go
- items.json wearables get `equip_slot` (+ the armor pieces as obtainable items)
- EntityData join/update payload carries appearance + visible equipment
- RemoteEntity feeds CharacterComposer instead of LoadBaked("farmer")
- An equip UI (replace the F6 debug cycle)
