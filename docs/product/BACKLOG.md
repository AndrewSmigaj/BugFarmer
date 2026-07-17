# Backlog

Running queue of upcoming work. Short notes only — each item gets its own plan when we start it.
**Now** = active, **Next** = teed up, **Later** = captured so we don't forget.

This is the durable queue. The throwaway plan doc covers only the single item we're actively
working; this file is what survives between sessions.

## CLAUDE.md & scaffolding improvements (owner wants a pass here; captured 2026-07-09)
Umbrella for tightening how the assistant is steered. Add items here as they come up.
- **DONE 2026-07-15 — enforcement scaffolding landed (P0-P5; plan: `docs/plans/repo-health-enforcement.md`).**
  Built the manifest-driven hook system this section called for: `.claude/manifest.json` (one source) +
  `.claude/hooks/` (skill-read gates, doc-drift Stop hook + git pre-commit backstop, determinism Stop gate,
  plan-exit gate, prompt routing) + `nakama/modules/world/CLAUDE.md` + committed `docs/plans/`. System map:
  `.claude/hooks/README.md`. **Hooks go live at the NEXT session start** (Claude Code snapshots hooks at startup).
  STILL OPEN in this umbrella (deferred to owner review): the **server-data-reload reminder hook** (below) is now
  a ~1-row add to the framework (a PostToolUse Edit nudge on `nakama/data/**` + `tools/zonegen/**`); the
  **teach-as-we-go** and **token-optimization** items; and the owner's **scaffolding audit** (effort-pinning,
  trim CLAUDE.md to a router, skill scar-vs-guess review) + doc-hygiene (bugs_new.md dup, entity_sync stale).
- **Reminder HOOK: don't say "go test" after a server-DATA edit without reloading.** Recurring failure
  (many times): the assistant edits zone/server DATA, re-saves the file, then tells the owner to Play-test —
  but the running Nakama still serves the old in-memory match, so the owner hunts for things that aren't there.
  The knowledge IS documented (run-backend "restart on data changes"; bug-spawning "Gotcha #2 stale save"), but
  the assistant reliably **won't** read a skill/memory just because CLAUDE.md points to it — memory/CLAUDE.md
  reminders get buried in a large context and don't fire. So: a **reminder-style hook** (e.g. PostToolUse on
  Write/Edit under `nakama/data/**` or `tools/zonegen/**`) that injects a fresh nudge AT THE EDIT: *"server-data
  change — restart Nakama (and reset the persisted save for bug/edit cases) and verify BEFORE telling anyone to
  test."* **Reminder that nudges the assistant, NOT an auto-run script or hard block** — the owner needs the
  assistant's judgment in the loop (sometimes it needs to look at a specific thing), not a rigid runner. Will
  test whether it's a strong enough reminder in a fresh session.
- **The actual reload is simpler than the assistant made it (verified 2026-07-09):** authored occupants/ground
  come from the FILE (`LoadChunk` reads `nakama/data/zones/<zone>/chunk_*.json`; the save only layers player
  `CellEdits` on top — `world_save.go`). So for authored zone changes, **`docker compose restart nakama`** alone
  is enough (drops the cached match → re-reads the file). The DB wipe is only needed when the persisted SAVE
  masks the change: **bug population** (persists swarms → bug-spawning Gotcha #2) or a **player cell-edit** on a
  re-authored cell. The reminder hook should point at the simple restart first.
- **Make all sessions learning experiences (owner 2026-07-10).** A skill/scaffold — ideally triggered by a
  push (or other) hook — where the assistant ELI5s / teaches what it's doing as we go (concepts, why this
  approach, the trade-offs), so the owner actively learns software dev instead of being hand-waved through.
  The owner is building toward an AI-engineer role and wants to not let that part of the brain atrophy.
- **Audit our scaffolding — is it helping or caging? (owner 2026-07-10).** Review the skills / memories /
  CLAUDE.md / plan discipline and ask, per piece: what specific failure does it prevent (can we name it)?
  does it TRANSFER INFO the model can't have, or merely DICTATE METHOD / restate general competence? is it
  still true? Lens: **scar-born** scaffolding (from a real "burned us 3×" failure) = usually keep; **guess-born**
  (proactive theories of how an agent "should" work) = scrutinize hardest. Explicitly include the ASSISTANT's
  own habit of inventing rigid rules and over-constraining itself — that's a big source of caging, not just the
  docs. Prune noise/stale/method-dictation; keep info/corrections/taste.
- **Token-optimization review (owner 2026-07-10).** Owner has a guide (drafted in chat) on cutting token cost —
  both to run more projects and as a core modern-AI-engineer skill. Turn it into real practice/scaffolding:
  **compact early** (after a task completes, at direction pivots — don't just let context fill), prompt-**cache**
  awareness, and **richer up-front instructions to agents** so they don't waste turns re-discovering context
  (clear, streamlined briefs). Capture the guide into a doc/skill + habits.

## Shaped-ground builder — BUILT M0–M4 + S1 legibility rework (2026-07-09/10)
The shovel is a terraform builder: it places `matA~matB~shape` **composite ground ids** (two materials
blended through a runtime GPU mask-composite into one tile — see `architecture_shaped_ground.md`). A composite
is governed by its **primary material** (`PrimaryMaterial`) for gameplay. **S1 (2026-07-10)** made dig/place
legible after playtest: **LMB places** as a **recipe-craft** (`ground_recipes.json`; a composite costs BOTH
materials), **Shift+LMB digs** as a **progressive break** (2–3 hits, crack overlay, ~3s idle-reset) → the
recessed **`dug_soil`** tile + **drops the material(s) to the ground** like felling a tree; the mouse wheel
cycles **shape only**; and a game-wide **world-error toast** (`WorldToast`, OpCode 40) surfaces every refusal
("Need 2 stone"). Server-tested (`shaped_ground_test.go`). **Remaining (S2–S4 + owner passes):**
- **S2 — "Set Materials" panel — BUILT, verify + pick layout:** `UI/ShovelBuilderPanel.cs` (open with `B`) —
  composited-tile swatches + material-B row + live have/need (`Data/GroundRecipeDatabase.cs`), unaffordable
  dimmed; additive over the dev HUD + temp M/N keys. Two layouts rendered (`tools/sprites/shovel_panel_mockup.py`,
  option A built). Owner: pick A vs B; confirm it compiles + reads in-engine (blind-built, no Unity here).
- **S3 — preview/GIF tooling — BUILT:** `tools/sprites/composite_tiles.py` + `tool_swing_gif.py` (verified by render).
- **S4 — animation fixes — BUILT, eyeball in-engine:** watering-can Pour (was sideways+static) + hoe till.
  Broader technique pass (reach-extension etc.) is taste — do with owner watching.
- **`dug_soil` art polish** — the current tile is a cropped placeholder; re-prompt (gpt-image-1.5/medium) or
  hand-draw a cleanly-blended recessed edge so it doesn't read as a bordered box.
- **Material item icons** — `grass_turf, dirt, mud, stone, sand, plank, wood` used by recipes have placeholder
  icons; generate real icons via the pipeline (API spend → owner approval) in one batch.
- **Verification owed:** the in-engine S1 playtest is the legibility gate; also confirm 2-client parity of the
  new player-break drop RNG once (autonomous determinism harness is unaffected — it issues no player breaks).
- **Build note:** add `Hidden/BugFarmer/TileComposite` to Always-Included Shaders before a player BUILD
  (Shader.Find works in-Editor; a stripped build would miss it).

## Ground material MECHANICS (deferred from the shaped-ground builder; owner 2026-07-09)
The builder ships **COSMETIC** (above). Later: some ground materials carry mechanics — e.g. **swamp** =
slowed movement, **ice** (mountains, if we do them) = slippery. **Rule for a split (diagonal) cell: AVERAGE
the two materials' mechanical values.** Mechanism: replace `PrimaryMaterial(id)` (the cosmetic resolver used
at every gameplay derivation site — hoe/water/collision/bug-block) with a `Properties(id)` that blends
`matA`+`matB` — SAME call sites, no rework. Movement speed isn't ground-derived today (`TileDefinition.
MovementMult` has zero consumers), so swamp-slow also needs wiring movement to the tile def first.

## Rug system redo — grid-square pattern builder (owner 2026-07-09)
Replacing the current single-sprite rugs (`rug_small`/`rug_large`). Owner wants a **grid-square-based rug
system**: build rugs out of square/tile patterns the player composes, cell by cell (like laying carpet).
A cousin of the shaped-ground builder — likely reuses the same mask/composite + square-pattern tech. Because
of this redo, **rugs are EXCLUDED from the shovel palette** (they are not shovel-placed ground). Design when
we reach it.

## Sandbag water-fill system (owner 2026-07-09)
A separate mechanic (NOT the shovel builder): fill in **shallow water** (and later **swamp**) with sandbags,
which converts those cells into **normal walkable ground**. This is why water/bridges are out of the shovel
scope — crossing/filling water is its own system. Design + build later.

## Sound / audio pass (deferred 2026-07-09 — owner on a bad speaker, can't tune audio now)
The `AudioFx` synth system exists (bug hit/kill, sting, faint, thunder, hiss, crunch, and the new axe-chop).
Deferred until the owner has proper audio: broaden SFX coverage (footsteps, UI clicks, water, crafting,
pickups, ambience), tune the volume mix + distance falloff, positional-audio polish, and music. Revisit then.

## Tutorials & instructions review (owner, 2026-07-09)
Polish pass on player onboarding — show users the different systems instead of leaving them to guess.
Includes tool-role instruction via tooltips/first-use hints, e.g. **shovel** = "change the ground below your
feet", **pick** = "break blocks & items at your level" (better wording TBD), and surfacing the other mechanics
(farming, catching, crafting, ground-editing) as they're encountered. Ties into the shovel ground-editing UX
being designed now.

## Late-join / determinism (found 2026-06-29 via the 2-client sync gate)
- **DONE 2026-06-29 — late-joiner gets 0 bugs in dense zones (real multiplayer bug + why the determinism gate "couldn't run").** Root cause: the Nakama client's default `MaxMessageReadSize` is **256KB**; village_21_B's `LateJoinSnapshot` is ~230KB raw → **~305KB base64 on the wire** (Nakama frames match-state data as base64) → the client silently truncates the frame, the websocket framing **desyncs**, and the late joiner receives **nothing** after it (snapshot + handoff + tick broadcasts) → **0 swarms**. Any 2nd player into a populated zone saw no bugs; regressed when #113 tripled swarm counts ("worked the other day"). Fix (shipped, `NetworkManager.Awake`): build the socket with `WebSocketStdlibAdapter(maxMessageReadSize: 8MB)` to match the server's `max_message_size_bytes`. **Verified:** co-located late-join `SYNC: IDENTICAL` (128332 bug-states + 236 tick-hashes, no drift). Proven by A/B zone size: bug_lab (20KB snapshot) ingested fine; village_21_B (230KB) dropped everything.
- **DONE 2026-06-29 — spawn-apart (disjoint-chunk) late-join divergence (the determinism gate's 2nd half).** Root cause (proven by a per-tick `_food` digest probe): the client deterministic food registry (`InfluenceManager._food`, which bug LANDING visuals read — `BugAgent.TryFeedAtFood` sets bug position) was hydrated **per-chunk** — `GroundItemManager.HandleItemSpawn` called `HydrateFood` for each `GroundItemSpawn`, and those are sent **per-chunk-subscribe** — so a client only knew food in its loaded chunks (authority held ~85 entries, a disjoint late-joiner ~265) → bugs forage/land differently → ~11-15% per-bug divergence. Fix (shipped, `GroundItemManager.cs`, 1 file): `GroundItemSpawn` is **COSMETIC-ONLY**; food enters `_food` only via the zone-wide `ITEM_ROTTED`/`FOOD_CONSUMED` ledger + the authority's `ZoneSnapshot.Food`. **Verified:** BOTH gate halves `SYNC: IDENTICAL` (co-located 166k + spawn-apart 161k shared-bug states, no drift). NOT an ecology change — `_food` is landing-visuals only; the server ecology uses its own `ForagePools`/`HostPlantStates`/`FindNearbyFood(worldState)`. With the collision map (#133) already zone-wide, food was the last view-scoped sim input → the deterministic bug sim is now fully zone-wide. (Optional polish, backlogged: a `ZoneFoodMap` would let bugs land on the FULL zone food set for richer feeding visuals, vs only the ledgered/un-consumed food they land on now.)
- **Snapshot size scalability (follow-up).** The `LateJoinSnapshot` grows unbounded with zone density (8MB client cap = ~30× today's headroom, not infinite). Consider gzip-compressing or chunking the snapshot, or bounding it.
- **DONE 2026-07-14 — S1/S2 predation client-state not surviving late-join (each client's wasps re-picked different prey → permanent desync).** Root: the server relayed the per-bug snapshot through a hand-declared Go `BugSampleData` struct missing `hunt_target`/`feed_until`/`feed_corpse_id` (silently dropped), and `_swarmStrikes` was never snapshot-hydrated. Fix: (A) `SwarmSnapshotData.Bugs` → `json.RawMessage` (server relays per-bug state VERBATIM — no field can drop); (B) snapshot `_swarmStrikes` by mirroring the food registry. Verified `SYNC: IDENTICAL` co-located + spawn-apart, non-vacuous (wasps hunting), 0 ht+pc mismatch. Contract in `architecture_swarm_sync.md §0`; check baked into test-changes/frontier-sync/certainty-assessment.
- **STRESS / SCALE TEST the bug sim (owner ask 2026-07-14).** Spawn LARGE bug populations (many swarms, dense predation/breeding) and confirm it all still holds: (1) DETERMINISM — the 2-client late-join gate stays `SYNC: IDENTICAL` under high swarm/bug counts (the snapshot + per-tick hash cost scale; watch the 8MB snapshot cap above); (2) PERF — client FPS + server tick time under load (tie in the `perf-tuning` skill + the ground-item pile bound below); (3) STABILITY — no crashes/OOM, no unbounded growth (ground items, brood, food registry). Add a stress test-zone (mass `initial` spawns) or a debug "spawn N swarms" and run the determinism + perf gates against it. Likely surfaces snapshot-size + O(n) hot spots first.

## Playtest 2026-06-28 — backlog items + fix queue
Full investigation campaign: **`docs/product/investigations/playtest_2026-06-28_index.md`** (root-caused 17 of
the 22 issues; one findings doc each). Backlogged-by-the-user items (not investigated):
- **Net dynamics (catch by net size).** You shouldn't be able to catch a centipede with a small net but
  currently can — flesh out the net-size / `catch_condition` / catch-difficulty matching (which net catches
  which species). Pairs with the catching-gear backlog (auto-catcher + fly nets) below.
- **Sleep.** A sleep/skip-to-morning mechanic (right-click bed → sleep), beyond the bed-as-respawn-home that
  exists. Design the day-skip + any restore/cost.
- **MOSTLY DONE 2026-07-05 — night critters + fireflies.** Fireflies SHIPPED (species + existing sprite +
  the per-bug amber LampLight glow that self-ramps at night; spawns all day, glow reads at dusk) with the
  bee milestone, plus dragonflies (the wasp-hunting chassis proof). STILL BACKLOGGED: the day/night SPAWN
  gate (fireflies visible-glow-only at night is display; a real nocturnal spawn window is sim).
- **DONE 2026-07-02 — the last two playtest fixes: #2 ghost offset + #7 rain.** **#2**: `TilemapManager.OccupantWorldPos` = the ONE shared position helper (footprint-X + bottom-pivot Y baseline); `RenderOccupant` + the placement ghost both use it → preview == placement by construction (ghost positions with the seed→plant id it renders). **#7**: rain streak lifetime was a fixed spec (~9-10 units of fall) shorter than a screen crossing; now computed per-layer from the live camera so the SLOWEST drop crosses the bottom edge (+ band/splash boxes sized from the view, rebuilt on zoom). Both display-only, no sim surface; editor-compile + eyeball gates.
- **DONE 2026-07-01 — three quick playtest fixes: #14 containers · #15 water empty bed · #10 moved compost.**
  **#14** (data): `basket`/`chest`/`trunk`/`yarn_basket` had a `world.container` block but no
  `interaction_type` → the client open gate (`CraftingPanel` needs `storage`) never fired. Added
  `interaction_type:"storage"` (exhaustive audit: exactly these 4 of 30) + published. **#15** (server): bare
  tilled `garden_plot` now waters → `garden_plot_wet` + consumes a use (was "No crop here"); ground-tile
  CellEdit only, no sim surface. **#10** (server, sim-feeding station): moved/runtime-placed compost had no
  `StationState` (chunk-load scan only) → deposits rejected; new `resolveStation` lazily find-or-creates
  (mirrors `resolveCraftStation`). Determinism-safe (empty station inert; food rides the frontier-gated
  `processStations`→ledger). Gated: `go test ./world/` green incl. 2 new falsifiable tests + FRESH 2-client
  sync IDENTICAL. In-game visuals = the Editor pass.
- **DONE 2026-07-01 — shared front-most-interactable click resolver (#18 + the overlap-steal defect class).**
  Occupant `BoxCollider2D`s are sized to the full sprite, so tall/large sprites overlap neighbouring cells; every
  click used a single `Physics2D.OverlapPoint` (one ARBITRARY overlapping collider) → an occupant that merely
  overlaps could steal the click. New `InteractionResolver.TopmostInteractable` (`OverlapPointAll` → front-most
  INTERACTABLE occupant, front-most = lowest `AnchorCell.y` = highest render sortingOrder) routes all 8 click
  handlers (`Breaking/Sleep/TreeHarvest/Station/Shop/Crafting/Mannequin/Sign`). Client-only target selection, no
  sim/determinism surface; Unity batchmode build compile-clean. **Fixes #18** (break behind a tree) + the
  flakiness class; **de-risks but does NOT fix** #5 (live-confirmed *sell-flow*, not the open), #14 (data tag),
  #10 (station-state keying), #4 (render never built), bed-2 (respawn/optimistic-message) — each keeps its own
  fix. In-Editor click-feel pass pending.
- **DONE 2026-06-29 — village doors (#1/#9) + modern-store windows (#2) + village neighbor (#3-edge).**
  `door_square` (the only placed door — all village doors) is now 1×2 tall + `blocks_bugs:true`, so flies stop
  at doors; players still pass (`blocks_players` left unset, by design — doors don't open, they just block
  bugs). Pure entity-def change: `blocks_bugs` is derived at zone-load and synced via the existing
  `OCCUPANT_BLOCKS_BUGS` path, so **no zone re-save and no determinism gate** (data on a proven mechanism — the
  earlier "needs re-save/sim-determinism" note was wrong). Modern store's frosted `glass_block` "windows" →
  real `window_4pane` (also bumped to 2-tall to match the walls + door); village_21_B rebuilt and its dropped
  `south→underground_passages_31` neighbor restored. Art regenerated for door_square + window_4pane (gpt-image-1).
- **Doors/windows — general polish (deferred):** a slow per-item pass — review EVERY door/window placement in
  every zone for look, and conform the unused `door_wood`/`door_iron` defs to 1×2.
- **Object/bug blocking-consistency audit (deferred):** bugs pass through some fences/objects but not others
  (confusing in playtest) — one systematic pass over every occupant's `blocks_bugs`/`blocks_players` for
  correctness + consistency.
- **Zone-neighbors builder hardening (deferred — the general #3 fix):** `ZoneBuilder.save()` writes no
  `neighbors`, so every rebuild drops zone links (we patched village_21_B locally in its scene's post-save
  block). Add a first-class `ZoneBuilder.neighbors` field written by `save()`, retire the underground
  post-save hack, and audit all built zones for dropped links.
- **DONE 2026-06-29 — dead bugs + fruit are placed GRID objects; sword-kills drop the bug (#22).** Carcasses
  (player kill → the strike cell; old-age/starvation → scattered across the swarm by a DETERMINISTIC per-bug
  hash, never `state.Rng`) and fallen fruit snap to a cell centre and render STATIC + per-item-nudged (multiple
  per cell, no bob); excluded from the walk-over magnet (bug food + `no_auto_pickup`), grabbed with E on
  mouse-hover. Server: `spawnCarcass` snap + blocked-fallback, melee carcass, `killBugsNaturally` scatter, fruit
  snap. Client: `IsAutoPickupExcluded += FoodValue>0`, `GroundItemVisual` static+nudge, `PickupController`
  E-on-hover. Go tests + sim-determinism green; ecology band check + Unity render/pickup are the in-game gates.
- **★ ARCHITECTURE INITIATIVE — move the bug ECOLOGY onto the authority client (server → thin relay + snapshot
  cache; lockstep).** Movement is already client-authoritative, but the ecology (breeding/death/hunger/food/the
  Director) runs server-side — which is why a corpse has no individual position (the server thinks in swarm
  *centres*). Viable because zones **freeze when empty** (no always-on requirement; the frozen-zone catch-up is
  its own backlogged heuristic). Big project (the full ecology must become deterministic-on-clients, with
  authority handoff) — it dissolves the corpse-position problem and scales. The natural-death scatter above is
  the throwaway interim until this lands.
  - **PILOT SHIPPED — individual predation S1+S2 (2026-07):** the first slice of this initiative — per-bug
    DECISIONS on the authority client, deterministic, ~no new traffic. **S1** = one wasp PURSUES a specific fly
    (`BugAgent` HUNT branch, staggered commit; per-bug strike broad-phase). **S2** = the kill drops a REAL edible
    corpse and the wasp PAUSES to eat it, with a ~1/4 chance it leaves it (`BugAgent` FEED branch; the corpse rides
    the ITEM_ROTTED food ledger; consume via the new authority-only `CorpseConsume` opcode 112 → FOOD_CONSUMED).
    Gated: `sim-determinism --predation-test` (non-vacuous, byte-identical) + Go tests green; committed `c39289b`
    (S1 `0b7dd3c`). See `architecture_swarm_sync.md` §14.6. **Next — S3:** dial back the swarm-centre steamroll
    (`predationThink`, scoped to swarm predators) + an `ecology-tuning` re-balance; then arena feel-watch (owner).
    Breeding/death/hunger/food/Director still server-side — the FULL ecology port is the remaining big project.
- **Dead-bugs/fruit follow-ups:** ~~predator kills leave a corpse + the hornet feeding-pause (#20)~~ **DONE
  2026-06-30** — feed-pause (`feed_pause_ticks`, server) + client-side LOS (`BugCollision.LineBlocked`, fixes the
  through-bin phantom) + consumed-corpse/lunge VFX (`StrikeVfx`); see `investigations/wasp-attack-indicators-phantom.md`.
  Still deferred: drop/place ANY non-occupant item from inventory, one at a time (reuse the torch "placer"); smarter
  placement (true across-a-fence reachability, nicer spread); the frozen-zone catch-up heuristic; tree refinement + testing.

## Opening intro + title screen — built 2026-06-28 (follow-ups)
The game now opens with a text intro ("It is 2136…", line-by-line) → crossfade → a **BugFarmer** title
screen (composed farm scene + logo + Start) → reveals char-select. `UI/OpeningSequence.cs` (self-bootstrapping
canvas, order 30, skippable, fail-safe). Art: `tools/sprites/title_art.py` → `Resources/UI/title_{bg,logo}.png`.
- **Replace the placeholder intro script** — `IntroLines[]` at the top of `OpeningSequence.cs` is a stand-in
  (only line 1, "It is 2136.", is Andrew's; the paste didn't come through). Swap in the real 8-ish lines.
- **Animate the title scene** — currently a static PNG; layer it for parallax/drift (floating bugs, swaying
  crops, clouds) — re-author `title_art.py` to emit layers + a small animator, OR a particle/Tween pass.
- **Custom display font for the logo** (optional polish) — the wordmark uses DejaVuSerif-Bold + styling (only
  standard fonts were available); a bespoke pixel/display .ttf would lift it. Re-render via `title_art.py --font`.
- **Remember-intro-seen** (optional) — auto-skip the cinematic on later launches (PlayerPrefs), still show title.

## Testing backlog (deferred test coverage — not blocking)
- **Crafting chain — verify in-game (the buildout from 2026-06-28).** The data/sprites/test-zone are built +
  the validators (`recipe_graph.py`, `catalog_coverage.py`) + Go tests are green, but the chain was NOT
  exercised in a running client. Steps: rebuild/run the backend (`run-backend`, force-recreate so the Go
  plugin picks up the new F8 "crafting" give-loadout); enter the **`crafting_test`** zone; **F8 → give
  "crafting"**; then right-click through `rock_crusher` (ore→paydirt) → `ore_sluice` (paydirt→refined) →
  `furnace` (refined+coal→bar) → `anvil`/`forge` (bar→tool/weapon) → `gem_cutter` (raw→cut gem) →
  `bug_extractor` (dead bug→chitin/leather). Confirm each opens, crafts, and produces; check tool-tier icons.
- **Cross-zone determinism check**: a player leaves a zone and re-enters; assert the bug-sim STATE HASH
  is identical across the leave/join (same bug positions/phase) — i.e. the swap didn't perturb the
  deterministic tick. Extend the sync-harness `crosszone` scenario to capture + compare zone hashes
  before/after. (The crossing is *designed* to be determinism-inert; this proves it.)

## Crafting buildout — remaining pieces (data/sprites/test-zone DONE 2026-06-28; these were specified, not built)
Plan + designs: `docs/product/economy/crafting_buildout.md` + the saved plan. All three are fully designed.
- **DONE 2026-07-03 — Per-station craft-slot mechanic.** `Procs []CraftProcessor` lanes (world.`craft_slots`,
  default 1; furnace/forge/sawmill/ore_sluice/dye_vat/bug_extractor = 2) sharing ONE output grid; legacy
  saves migrate via `UnmarshalJSON`→`Procs[0]`; `proc` on ContainerActionMessage + `procs[]` on the echo;
  CraftingPanel renders one row per lane with lane-targeting DoCraft. 5 falsifiable Go tests (migration
  round-trip, parallel lanes, stall isolation, proc targeting, seeding/top-up) + suite green. NOTE from the
  build: campfire/stove/cooking_pot/cauldron/keg have ZERO recipes — not functional stations; their
  craft_slots are moot until cooking recipes ship (cooking = D16/D19 backlog). In-Editor parallel-smelt
  check pending. Sprite pass shipped alongside: 15 missing sprites + ~82 placeholder regens (metal/gem/
  weapon/tool tiers now real per-metal art; catalog rows authored). Editor eyeball flags: `specimen_case`
  reads empty; bronze-vs-gold sword tone is close.
- **Station panel LAYOUT session (user-requested backlog)** — a joint pass positioning panel elements
  ("right now they are ok but could be positioned a little better") + the themed per-station dressing
  (Apico fuel/heat treatment) that was deferred with it.
- **DONE 2026-07-02 — Barter sell UI** (Apico/BG3; also the playtest **#5** fix). Your REAL inventory opens
  with the shop; stage stacks into a basket (right-/double-click = whole stack; drag via the cursor;
  right-click a basket cell = one-at-a-time partial) → one atomic **`sell_batch`** server op (each line
  validated by the shared `sellLine` core vs the vendor `Buys` filter, sum, pay ONCE, one FullInventorySync
  echo) — NOT a client loop of single sells. Staging = a render OVERLAY (`ShopPanel.StagedQty`/`ForRender`,
  consulted by InventoryPanel + HotbarUI) so the mid-shop FullInventorySync repaint can't resurrect staged
  slots. Also shipped: "Buys: …" header + client stage filter mirroring `shopBuysItem`, OpCode-40 server
  errors surfaced in a shop status line (were silently dropped — the #5 feedback gap), per-line `qty<=0`
  rejection (closed a real negative-qty duplication exploit), bug-release guarded while a shop is open.
  Gated: 4 new falsifiable Go tests + suite green + Unity batchmode compile clean + in-Editor CONFIRMED (Andrew, 2026-07-02; incl. the layout fix — wide short trade dock clearing the inventory).
- **Station mockups** (PIL) — extend `tools/ui_mock.py` to render every craft station + the breeding/food
  stations (compost/beehive/milkweed/wasp-nest) with the Apico I/O-square treatment, for visual review.
- Also: armor + weapon-tier *sprite polish* (placeholders shipped); the InitialContainers authored-stock seed
  (the good-design alternative to the F8-give); fruit/crop + breeding-station info panels (separate backlog).

## Now — Bug ecology / farming (livestock loop on a living-ecosystem engine)
Design of record: [bug_ecology_plan.md](../brainstorms/ecology/bug_ecology_plan.md). Phased build P0–P11
(P1 Bug Lab DONE). **Verify every sim-touching phase with the `test-changes` skill** (Go tests +
sync-harness + the determinism / "all players in sync" checks — the testing methodology is now captured as a
skill so it stops getting lost between sessions).
The **SERVER ecology is built + verified** (Go tests + 6× headless lab + per-species charts in
`tools/_generated/ecology_charts/`). The living system = **depletable food → boom-bust → the Director →
(future) the Ecologist restores → progression**. Done:
- **Breeding-unify — ONE visible brood model (2026-07-14, SERVER DONE + deployed):** ALL non-instant
  breeding lays eggs into a visible `BroodState` that develops over GAME-HOURS (`BroodEggMatureTicks=350`
  ≈ 1 game-hour/egg, was ~10s = the "always-empty nests" problem) and hatches — flies/butterflies (compost /
  rotten-fruit pile / milkweed), detritivores, AND **wasp NESTS** (nest brood routed off the old invisible
  instant-pop counter onto the `BroodState`; recovery/founding read it via `nestBroodCount`; the homing
  resident ENTERS the nest a beat to tend). Go-tested; A1 ecology-validated (ground species self-sustain via
  `+brood`). `entities/brood.go`, `world/{brood,nests,predation}.go`.
  **→ NURSERY-STATION model built (2026-07-16) — see `architecture/architecture_nursery_stations.md`:** a brood
  IS a modified STATION. Right-click a **wasp nest** or **milkweed** → the `NurseryPanel` (egg/larva/pupa slots +
  stage sprites + resident adults + a maturing bar), fed by OpCode 104 (now carrying conversion progress +
  resident count). **Take** a stage's units into the bag like any station transfer — no random yield, nothing
  perishes on take (larva → the designed `wasp_larvae` material, else the stackable stage sprite;
  `OpCodeNurseryTake` 113). **Teardown** now **perishes the brood** and spills the resident adults (aggressive) —
  the `wasp_nest` `paper_nest`+`wasp_larvae` break-drop removed per D23 (now Wasp-Thicket boss loot only). The
  **pupa stage is universal** — nests pupate too (wasp `wasp_pupa`); millipede/centipede stay egg→larva→adult;
  `BroodEggMatureTicks` split across stages so total dev time is unchanged. Stage art: 11 existing +
  `fly_pupa`/`beetle_pupa`/`butterfly_caterpillar`/`butterfly_chrysalis`/`wasp_pupa`. The earlier wrong-model
  (on-world `BroodManager` sprite renderer + the "emergence beat") was a MIS-BUILD → **removed**. Go-tested green;
  determinism-safe by construction (broods are server-soft/unhashed); D23 + docs reconciled. **STILL OPEN:**
  place brood back onto a compatible nursery; the **compost bin** deposit+brood unified into the panel; the wild
  fly-brood object; compost residents; the owner's in-Unity compile + panel eyeball + a non-vacuous 2-client
  sync re-run. **Bug Zoo built** (`zone_bug_zoo.py` — a peaceful 3×3-pen observation zone, replaces the scattered
  labs) to watch the loop; `zone_arena`/`zone_crawler_lab` flagged superseded. Then Phase-3 re-tune to the new
  bands (fly 200 · butterfly 100 · rest 30) on the predation-inclusive Unity rig. Dead `egg_count_min/max`
  species fields to delete (unused).
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
- **Butterfly life stages ON the milkweed (owner decision 2026-07-16 — keep it simple):** caterpillar +
  chrysalis are STAGES that happen ON the milkweed host plant — eggs → caterpillar → chrysalis → adult — **NOT**
  a caterpillar that crawls off or a chrysalis that wanders to a tree/fence (that mobile-creature version is
  explicitly OUT of scope). Extends the existing `host_plant` `BroodState` (butterfly already breeds on milkweed,
  `brood.go`) with a chrysalis stage on top of egg→larva, plus caterpillar + chrysalis stage sprites (butterfly
  caterpillar sprite already backlogged above). Adult butterfly birth rides the deterministic ledger as today.
  Deferred: caterpillar/chrysalis are synchronized client-side bugs — needs the sync-gate work, not done today.
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
Owner directive ("lets create a zone improvement guide, scaffolding for you… this new skill related
to zone authoring") — built and VALIDATED by a live run, all phases committed green:
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
  "everything looks aweful, just sudden changes no gradients, unatural geometry (lines)…
  why is everything barely different at all?" AND the ant framing was builder invention:
  "there is no ant colony in the zone" (the colony IS zone (3,0), mostly underground; the
  south band should "start getting dirty and rocky on a gradient not suddenly having the
  dirt wall" — C12). Postmortem: adopted research rules had no code mechanism behind them
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

## Now — COMBAT FOUNDATION (M1 BUILT 2026-07-11 → `architecture_combat.md § Milestone 1 — as-built`)
Owner adopted the skeleton (**attack-token + FSM + steering**) + core bundle. **Decided dials:** bite-token
pool = **2**, **dodge-only**, danger **at night**, bug→player damage **per-individual** (authority-decided,
mirrors predation; swarm-of-1 dropped — player HP is SIM-INERT so it needs no hash/snapshot wiring), new sprites
**gpt-image-1.5/medium**.
- **✅ M1 DONE + gated** (commits `combat M1.1`…`M1.4`): arena + debug species-picker spawner · per-individual
  sting (fixes the wasp **phantom hit** — retired the `checkBugAttacks` swarm-centre sting; opcode 110) · player
  dodge + i-frames (Space; opcode 111 + `DodgeInvulnUntilTick`) · attack telegraph (two-beat wind-up = **12
  ticks**, `processPendingStings`). Gated: `bug_player_strike_test.go` + full world suite + `sim-determinism`
  PASS. **Left to run** (needs the rebuilt plugin deployed — do with the playtest): 2-client `run_sync_latejoin`
  regression + the **owner arena playtest**.
- **✅ M2 DONE + nocturnal + aggro:** **nocturnal** night-hunter mechanic + **player-aggro radius**
  (`aggroPlayerThink` — non-centipede attackers chase a nearby player) + 2 wasp tiers with fresh gpt-image-1.5
  sprites — `wasp_soldier` (med) / `hornet_giant` (hard, **diurnal** — real hornets are day-active).
  Gated: Go suite + sim-determinism PASS. Difficulty via existing knobs (dmg/cd/speed/vision/hp/swarm) + nocturnal.
- **🩹 M3 caterpillars STRIPPED (2026-07-12):** built as caterpillars off a literal misread; caterpillars are
  butterfly/moth larvae, not combat enemies. Removed all of it. Replaced by → **M3 centipede tiers** (below).
- **✅ M3 centipede tiers DONE:** 2 REAL centipede species, medium + hard, own segmented sprites, reusing the
  base centipede surge model — `centipede_tiger` (Scolopendra polymorpha) + `centipede_giant` (S. gigantea). One
  clean code change: de-hardcode `CentipedeTrail` segment family (add `sprite_family`).
- **✅ Enemy AI — individual attack movement + phantom/bumble fix (2026-07-12) → `architecture_combat.md §
  Individual attack AI`.** Owner report (*"wasps bumble … centipedes phantom-hit … they should swoop in and
  attack, solo divers one or two at a time"*) fixed. ROOT CAUSE of the bumbling: wasps shipped
  `player_reaction:"ignore"` so each individual bug's AI wandered and never engaged (the swarm-centre chase +
  cosmetic-dart first pass didn't fix it). REAL fix: (A) **individual attack MOVEMENT** — `player_reaction:"attack"`
  + `BugAgent.AttackMove`: each bug HOVERS at `standoff` then SWOOPS in during its phase-offset slice
  (`dive_period_secs`/`dive_secs`) → ~1–2 divers at once, staggered, DETERMINISTIC (pure `tick`+`bugId` + player
  CELL); (B) `aggro_speed_mult` brings the cloud onto you; (C) sting detection vs the **RENDERED** sprite killed the
  phantom + the **server centipede bite was DELETED**; (D) `wasp_soldier render_scale 0.5` (was too big); (E) all
  feel in `attack{}` + a "Combat knobs" table. **Gated:** Go world+entities PASS; `sim-determinism` PASS (wander
  hash unchanged `BDE84AEF38467D57`) **+ a new `--attack-test`** that drives a moving player and proves the attack
  movement reproducible (A==B, `FB80CE8997CF9EC3`). **Left to run:** owner arena playtest + knob tuning; 2-client
  `run_sync_latejoin` confirmation (Unity build).
- **⏳ REMAINING:** the super-hard "boss" centipede (owner floated it). **Consolidation refactor** (future,
  tracked): bug→player DAMAGE now has ONE model (client-detect-vs-rendered → server-apply, both styles); the
  remaining overlap is the **3 aggro triggers** (surge-trigger / nest-defence / `aggroPlayerThink`) — collapse into
  one threat-table in a deliberate pass.

## Content — TRUE BUG MAPPINGS (make every bug a real bug) — owner direction 2026-07-11
Every creature in the game should be an **actual real bug species** — real name, real look, and behavior that
matches the real animal (so a player's real-world knowledge never jars, e.g. "hornets are diurnal, why is this one
nocturnal?"). The hint was already there: `nakama/data/bugs.json` is a roster of REAL species (honeybee, bumblebee,
luna/atlas moth, stag/rhino beetle, wolf/jumping spider, scorpions, cicadas…). Combat generated GENERIC invented
names (`wasp_soldier`, `hornet_giant`, `caterpillar_spiny/thornback`) that break this.
- **Task:** sweep ALL species (`species.json` combat + `bugs.json` art) and MAP each to a real species — rename ids,
  names, descriptions, sprites, AND align behavior to the real animal (diurnal/nocturnal, diet, aggression). e.g.
  the combat tiers → real day-active wasps/hornets (Vespa spp.) + real nocturnal caterpillars/moths; verify each
  flag against the real animal.
- **Discipline:** nocturnal ONLY where the real species is night-active (caterpillars/moths yes; wasps/hornets no).
  This is a rename+realism pass, not new mechanics — the combat/ecology machinery is unchanged.
**Backlog `zone barriers`:** gate danger by zone so starter zones stay cozy while wilds/caves/night are dangerous.
Earlier notes (still valid): Deferred — utility-AI attack selection, enemy-role/species expansion. Rejected: GOAP, flow fields.
All integer/fixed-point on the server → cheap on the wire (legs + events, not per-bug positions; see the doc's
network section). **Build order:** dodge+i-frames → one telegraphed enemy + token pool in `feel_test` (playtest)
→ aggro/leash → generalise FSM+steering → threat director. Open taste/scope Qs in the doc (how cozy vs hard;
dodge-only vs block/parry; is threat zoned; how many new enemy roles). Full evidence:
`investigations/deep_research_2026-07/combat/`.

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

## Later — UNDERGROUND LIGHTING + LOOK OVERHAUL (Plan 1 BUILT M0–M3 · Plan 2 look-&-feel BUILT 7/7 · 2026-07-09)
Design (scored candidates, spike-gated): `docs/product/architecture/architecture_lighting.md`. Evidence (each
through 2 adversarial critic rounds): `docs/product/investigations/research_lighting_dark_underground.md`,
`..._look.md`, `..._look_and_feel.md`.

**BUILT + in-engine (pending owner Play-test validation — client-only, no sim/determinism surface):**
- **Plan 1 lighting M0–M3** (owner-confirmed working): world-space darkness multiply overlay (`DarknessOverlay`
  + `DarknessMultiply.shader`) = max(buried-from-solids, roofed), opened by carried-light reach; roof data path
  zonegen→Go→client (`OpCodeZoneRoofMap` 109); torches fade in like dusk via one smooth "how-dark-here"
  (`LampLight` reads `UndergroundDarknessAt`). Test vehicle: `lighting_test` zone.
- **Plan 2 look-&-feel P2-1..P2-7 (ALL built)** on `feature/profiling-upgrade`, awaiting Play-test: wind sway +
  hit-flash lit shader (`SpriteLitWorld.shader`, world-space motion; grain crops sway, vegetables don't) +
  `LitMaterials` routing · ambient dust (`DustController`) · blob shadows (`BlobShadow`) · hit-flash + camera kick
  + leaf/chip burst on chops (`HitFlash`/`HitBurst`/`CameraFollow.AddShake`) · lily-pad bob + reed sway · emote
  bubble system (`Emote`, F6 test trigger) · **P2-6 animated water** (`WaterAnimated.shader` = copy of
  `SpriteLitWorld` + world-space seamless distortion/shimmer; a runtime second Tilemap under the Grid, sorted
  "Ground" order 10; centralized `IsWaterTile`; additive + graceful-degrade to static water; calm/flowing/sparkle
  are material dials). Test vehicle: `feel_test`. Tuning dials are owner Play-test work.

**STILL DEFERRED:**
- **Lighting M4:** roll the roof mask out to the REAL underground zones (`ant_tunnels_30`/mining), cross-zone
  seams, save migration, digging-updates the mask; run the M2 **2-client determinism gate** (roof is cosmetic →
  expected IDENTICAL, run when the owner's not connected).
- **Tree improvements** (owner 2026-07-09):
  - **Recreate the tree art**: regenerate `tree_oak` (+ other trees) via the sprite pipeline
    (`add-object`/`regenerate-sprite`). Art task. Blob-shadow read on trees improves once the trunk is redrawn.
  - **Cutting-down animation**: a proper felling animation when a tree is chopped (lean/fall + a stump left),
    beyond the current hit-flash + leaf burst. Owner wants it eventually; out of scope for now.
- **Water follow-ups (experimental):** shoreline **foam** = BUILT (world-space shore-mask swash) · specular
  **sparkle** default-on · reflections · **lava** animation (same overlay, different material).
- **Part II look phases** (flicker, post-processing bloom/grade, god-rays) + broader look-&-feel backlog below.
- **Owner-taste Qs** (mostly settled during the build; revisit if needed): scalar/binary roof (light shafts),
  palette mood, emission tooling, normal maps, player-light-underground.

**Original owner spec (still the requirement — the reference the build targets):**
Owner: "the outside area at the top should be lit like any other day/night, on the top ant
zone and the mining zone with the mining camp, we can make it dark past that point. as it
is all masses of ore block should have the inner ones dark, wherever they are surrounded,
this is like terraria. but we can backlog lighting for now as we are just focused on the
zones, so backlog all lighting."
- Surface strips of (3,0) + (3,1) get normal day/night; DARK below/past them.
- Terraria block rule: any block cell fully surrounded by blocks renders dark (applies to
  ore masses on the surface too — inner blocks of a mass are dark).
- Full-dark underground + flashlight (already designed, game_design.md ~720); glowworms +
  mushroom_glow are the natural sources (D21); zone docs place them to double as future
  light anchors so the lighting pass never rearranges rooms (R5).
- **CROSS-ZONE LIGHTING (owner 2026-07-07):** lighting must be continuous ACROSS zone
  seams, not per-zone-isolated. A lit surface zone bordering a dark underground zone (e.g.
  bee_meadow/ant_tunnels surface ↔ the underground below) must transition believably at the
  boundary — no hard light/dark wall at the seam, and a player straddling the edge sees one
  coherent light field. Design the lighting model to read the neighbor's light state (or a
  shared day/night + depth model) so crossing a zone line is seamless.

## Later — ANT mechanics riders (owner review 2026-07-07)
- Ants CARRY real items to chambers (fruit/rotten fruit/dead bugs -> granary caches) —
  the transport mechanic; v1 granaries are authored caches of real items.
- The ant BROOD system deep pass ("backlog the entire brood testing") — lifecycle,
  harvest response, defense tuning.
- Scouts are BASED in the lower colony and head UP AND OUT across zones — rides the
  real cross-zone transfer below.

## Later — UNDERGROUND BUG ROSTER (owner ruling 2026-07-07: "backlog all bugs, we're just building the zones")
Built AFTER the row-4 zone terrain. The zones PLAN the spawn locations; these are the sims.
- **Warrior ants** (soldier caste — BLACK ants): guard the Queen; turn aggressive near her; the
  general **defender response to STEALING/DAMAGING** (also the fix for players stealing boats/
  containers). This is the mechanic behind the (4,0) Queen "just chills, guarded by warriors."
- **Cave fly** — a NEW, REAL underground fly, faster + stronger than surface flies (a real
  cave-dwelling fly; owner: all bugs must be actual bugs, never invented).
- **Aggressive raid centipede** — GREEN variant, REUSE the existing garden-centipede sprite, tuned
  MORE aggressive than garden centipedes; dens at the (4,0)↔(4,1) raid seam and raids the colony.
- **Scout tuning** — scouts share the workers' home but wander much farther; must reliably FIND +
  return food, and IGNORE near-nest food (don't over-provision — ants forage). Tuning, not a spawn.
- **Glowworm** species (light keystone + catchable, firefly-style lantern) — the (4,1) grotto light.
- **Cave spider** species (webs slow prey via a speed-debuff; pounce hunter) + webs decor.
- **Aphids** (livestock/honeydew mutualism, disruptable).
- **Live cross-zone bug traffic** (real transfer; already sketched below).
- **Black mold hazard** — needs a POISON/hazard-cell mechanic (verified 2026-07-07: none exists);
  build the mechanic, THEN mold that poisons on contact can be placed. (Not decorative-only.)

## Later — POLISH ALL ZONES to the craft bar (owner 2026-07-07)
Bring the existing zones (village_21_B, bee_meadow_20, underground_passages_31, …) up to the
standard set building ant_tunnels_30: natural dirt/stone INTEGRATION (substrate model, not flat
fills), NOISE-FADED boundaries (never straight material lines), clean prominent entrances, wooded-
by-default with real carved clearings, neighbor edges that actually connect. Folds in the already-
listed bee-gradient removal + mushroom-realism sweep (ANT-ARC BUILD PREP below).
CRAFT RULES set this session (also in CORRECTIONS.md): **NO CEILINGS** (overhead view can't show
them — no ceiling glowworms/stalactites/star-fields; features are floor/wall based); **micro-stories
must be compatible with real game mechanics** (don't assume unbuilt mechanics).

## Now — ANT-ARC BUILD PREP (owner decisions 2026-07-06, do alongside the (3,0) build)
- **bee_meadow_20 — REMOVE the south dirtying/rocky GRADIENT** (zone_bee_meadow_20.py §1b:
  the `gradient_field` + rock_masses + torn-ground rubble + dead-tree/dry-flora band along
  the south edge). Owner: "removing the strip at the bottom of the bee zone just to give
  more space to encounter ants, and more spread out forest." Its original job (blend into
  the ant zone below with no sudden dirt wall) is gone now that ant_tunnels_30 is
  half-outside and carries its own cliff transition. AFTER: restore meadow to the south
  edge with more spread-out forest. **Keep the Rocky Gorge (§1c, the stream's east exit) —
  a separate feature, untouched.** Re-save the zone + view_world.
- **Mushroom realism sweep — REPLACE the two generic ids** (`mushroom_cluster`,
  `mushroom_brown`) at all 17 placements with existing real species (morel, inkcap,
  chanterelle, puffball, bracket, red, glow…), then DEPRECATE the two generic entities.
  Owner: "actual mushrooms, not just 'cluster' or 'brown mushroom'." Touches many
  zone_*.py + regen; no new art (real species already have sprites). Ant zone already uses
  inkcap/morel natively.

## Later — REAL cross-zone bug transfer (owner 2026-07-06: "it will be real bug transfer")
Zones are isolated per-match sims today (Neighbors is player-only). The real feature:
a bug/swarm that walks off a connected edge LEAVES zone A's sim (a ledgered removal) and
ARRIVES in zone B's sim (a ledgered spawn at the matching edge) — two zone-local ledger
events, no shared sim state, each zone stays independently deterministic; transfer routing
via the existing Neighbors map. Until built: NO fake edge-spawn pretense; ant populations
stay zone-local (D21's "ants cross into the Mining Camp" waits for this).

## Later — MARBLE (owner 2026-07-06, "backlog this just talking")
The material exists (style.json marble palette; column_marble; wall_marble client-side).
Future: a quarry source in the deep zones (row 4), statues + fountains crafted at the
Stonemason (D27 sculpture yard), and the marble premium furniture tier (P2 of the
underground-arc plan adds table/bench/bust_marble as stone-set premium overrides).

## Now — ANT TRAIL FEEL-BAR (open; mechanism proven, rate-tuning remains)
The underground-arc P3 shipped the ant colony sim (species, nest gates, colony memory,
commitment, recruitment, reinforcement, coalescence — all gated: go suite, determinism,
latejoin x2 SYNC IDENTICAL, zero new ledger events). The visible nest→carrion FILE has
not yet formed in the open-field lab: 11 evidence-logged runs (ecology_tuning_log.md),
two named bottlenecks left — (1) recruit-eligibility filter (needs one instrumented
run), (2) scout coverage (patrol-bias lever). Owner decides at the review package
(docs/product/investigations/underground_arc_review_package.md): finish in the lab now,
or bar it on ant_tunnels_30's real tunnel geometry when built.

## Later — creatures: ants & spiders (DESIGNED, not built)
Full approved design: **[design_ants_spiders.md](ecology/design_ants_spiders.md)**. Ants = a foraging colony
(hill/queen/eggs reuse Nest+Brood; workers forage carrion → carry home via the wasp provisioning loop;
scouts + server-only "colony memory" make trails emerge — no per-cell ACO grid). Spiders = a web-builder
ambusher (web tiles slow prey via a server speed-debuff; reuse occupant placement + `OCCUPANT_BLOCKS_BUGS`)
+ a jumping/stalk-pounce hunter (reuse the centipede `ActionState` lunge). Determinism-light (ant trails add
zero sync surface). Build spiders first (lower risk); ants are Med–High complexity. Includes Step 0 = the
rotten-fruit decay fix (bound the pile).
- **Spiders & webs in the underground (don't forget!)** — finish adding the cave spider + its webs to the
  FIRST underground zone (Underground Passages / Mining Camp). Per the zone sheet it's the dark-warren ambush
  species (`cave_spider` drops from the ceiling on silk; web-choked side-passages; `cave_spider_silk` is the
  zone's soft-material spine) — designed, not yet placed/wired into the zone.

## Later — content layer (agriculture + crafting depth) + station minigames
- **Flesh out agriculture & crafting (finish the content layer):** the systems exist (crops, crafting
  stations, recipes, containers); this is the CONTENT pass — more crops/recipes/stations/products, the
  progression that ties them together, and the missing art. Needed eventually, not now.
- **Station minigames:** interactive minigames at craft stations (e.g. a timing/skill step when smelting,
  brewing, etc.) instead of a pure timer. Polish/engagement layer on top of the crafting system.

## Later — catching gear: auto-catcher + fly nets
The catch system already exists (net sweep + `net_size` small/large gate, `CatchingController`/
`BugReleaseController`); this is the gear layer on top of it.
- **Auto-catcher (placeable):** a passive bug-collection station — set near a swarm, it slowly catches
  bugs in range into a capped internal buffer the player empties; the bug-farm chore-relief device
  (cf. the `egg_collector` sketch in `docs/brainstorms/objects/storage_automation.md`). Must be
  **capacity-bounded** so it can't strip a farm, and respect the existing "what the bugs eat belongs to
  the bugs" rule. Likely a placeable with its own panel + a designed catch rate and species whitelist.
- **Fly nets (tool tiers):** dedicated nets for flies/butterflies — extend the small/large net ladder
  (e.g. small → large → specialized) with their craft recipes + diagonal tool icons (the same
  `net_size` enforcement already decides which species each net can take).

## Later — sprite review (manual, by hand)
Go through EVERY sprite by hand and fix/redo the ones that read wrong (Andrew edits on his end). Many
were auto-generated; quality varies. NB: a bare `pixelclean.py` re-cleans ALL sprites — regenerate +
clean ONE key at a time and revert incidental churn.

## Later — economy reconciliation follow-ups + item-model tech debt (from the 2026-06-26 catalog pass)
The catalog consolidation is **done**: 5 as-built pages (furniture/containers/decoration/structures/plants) +
materials blocks&deposits, `architecture_items.md §1–15` retired, `tools/data/catalog_coverage.py` no-orphan gate
green, the recurring rules logged as DECISIONS D22. Open follow-ups the user adjudicates:
- **The economy FEATURE itself** — buy/sell/NPC/dialogue/trading + recipe-acquisition (default/bought/found
  unlocks). The *data + catalogs* are ready; the *gameplay loop* (shops, dialogue, coin sink) is not built.
- **Per-item recipes & costs** — `recipes.json` only has ~10; the catalogs propose `source` (🔵) but not the
  ingredient lists. Author recipes per the crafting.md ~70/20/10 split.
- **Rock-decor / cave-scene rework** — "leave decor as-is for now"; `boulder` + `sandstone_formation`/`cave_moss`
  art/placement deferred. Decide keep/cut `boulder` + the `*_test`/look-alike entities the catalogs flag.
- **Tech debt — capability-based gating (8a):** stop overloading `category` as a behavior gate. Resolve
  tool/weapon/armor behavior from capability fields (`tool_type` present, `armor_slot` present) so recategorizing
  an item can't silently break `getToolStats` (handlers_world.go:693) or the armor-equip gate (:859). (This pass
  used the minimal `||"weapon"` fix deliberately; the clean refactor is here.)
- **Tech debt — data-schema lint (8b):** a committed validator for the entity JSON (category ∈ known enum, every
  drop/recipe id resolves in the unified registry, every drop has an item entry or is flagged). Extends
  `catalog_coverage.py`'s reports into a CI gate so the class of bug behind the 2026-06 doc-drift can't recur.
- **Icon polish (optional):** the 6 new herb items + the occupant-only drops (cacti, several mushrooms, `geode`,
  `reeds`) render via world-sprite fallback; dedicated `_icon.png`s via Pipeline A when art has time.

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
  - **Village windmill (Andrew, 2026-06-27):** put a **windmill in the starting town that powers the
    houses** — but the player **cannot buy or build it until the wheat/locust area** (the
    `locust_farmland` zone — *"a little western-style town"*). Gates the village's electrification behind
    reaching that zone. ("I will know what it means when we get there.")
  - **`clothing_rack` unlock (D26):** the 2-wide garment rail is a **display fixture only** in the Weaver
    for now — **not craftable/buyable until "the other town"** (same later-zone gate as the windmill).
    Wire its recipe/shop-entry when that zone lands. (`coat_rack` stays the house clothing piece.)
  - **`electric_heater`** is a Modern-Wares showroom display; functional only with the electricity expansion.
- **Single-slot "bulk bin" containers (D26):** `produce_crate` is now `slots:1` (a covered crate = one bulk
  stack of fruit/veg) — the same model the **ore bins** want. For a slot holding MORE than the normal stack
  cap (a true silo), add a per-container `stack_cap` override; until then 1 slot = 1 normal stack.
- **Procedural container fill-display (deferred):** the "show real contents" idea (a `fill_rect` + the client
  drawing the top item icons into it) stays backlogged — covered containers (lid/tarp) sidestep it for now;
  it's the eventual upgrade for OPEN containers.
- **`modern_floor` TILE:** polished floor for the Modern Wares showroom (terrain pipeline); proxied by
  `stone_floor` for now.
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
  icons; the design-target table lives in [`economy/catalogs/weapons.md`](economy/catalogs/weapons.md)). Durability still unenforced.
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

## Later — commerce spine follow-ons (after the 2026-06-27 v1: currency + general store + bug dealer)
v1 (DECISIONS D25) shipped currency + two working village vendors. Open follow-ons:
- **Distinct NPC art** — v1 reuses player-model sprites (`merchant`/`scholar`) as placeholders; the user wants
  NPCs to look different from the player. Make proper NPC sprites (Pipeline B/A).
- **The other 3 village NPCs** (Fisherman, Blacksmith, Carpenter) + the **Mining-Outpost** vendor — pure data
  (new `shop` occupants) now that the spine works.
- **Bug-market building + scene** — a dedicated building w/ unique decor + sign for the bug dealer, plus 1–2
  pricier **exotic bugs from other zones** in its sell list to show the value ceiling (game-feel curation).
- **Recipe-selling (Phase 2)** — `KnownRecipes` on the character + craft-station unlock enforcement, so shops
  can sell recipes (today all recipes are `unlock:"default"`).
- **NPC dialogue / wandering**, rotating/rare stock (adds shared state → revisit concurrency), bug-slot UI polish.

## Later — furniture / container / skill mechanics (from the Weaver scene pass, 2026-06-27)
- **Placeable containers (world + char-slot):** a container item can be worn in the character's container
  slot AND **placed in the world and used like a chest** — for the ones that make sense (a `dresser` holds
  clothes; you shouldn't drop it as a generic world chest). Define which containers are placeable-as-storage.
- **Furniture container filters:** make sure **all** furniture/decoration containers are actually set up as
  containers and **filter correctly** (dresser → clothes/armor only, wardrobe → clothes, terrarium → bugs,
  ore bin → blocks, etc.). Audit the `world.container.filter` on every container.
- **Player skill system (passive, station-driven):** each station USE grants a little EXP toward a skill
  (weaving, smithing, masonry, cooking…) — a nice passive, player-driven progression. Skills unlock perks /
  speed / quality. Design + build later.
- **Furniture-on-rug:** placing furniture **on top of a rug** must work (rug is a flat floor decoration that
  doesn't block the cell; the furniture sits over it). Verify the flat-placeable + occupant stacking.
- **Multi-square rug art:** rugs should visibly span **multiple cells** (`rug` 2×2 / `rug_large` 2×3) — the
  current art reads as one tiny square; the sprite must fill its footprint. (Art fix, batched.)

## Later — functional clutter (Weaver pass follow-ups, 2026-06-27)
- **`fabric_bolt` → optional `fabric_pile` container:** dropping cloth on the ground could aggregate into a
  **fabric-pile container** (the drop-aggregation idea — same family as ore bins / placeable fill containers).
  For now `fabric_bolt` is shop décor; revisit when the placeable-container-with-fill mechanic lands.
- `yarn_basket` is now a real **container** (filter `textile`); its **fill-state visual** (showing yarn level)
  rides the same fill-display backlog.

## UI/shop follow-ups (2026-06-28 — the polish run)
- **Village shop placement cleanup** — the 3 new shops (Weaver/Stonemason/Modern Wares) are placed in a
  loose south commerce strip on open grass; give them proper access lanes/spurs + tidy the layout in a
  paired pass (positions are easy to nudge in `zone_village_21_B.py`).
- **Full verification pass** — Unity compile + in-game test of the new panels (dialogue/shop, station I/O
  squares, mannequin dress-up, sign read); go tests via the docker/run-backend path (local go toolchain
  can't parse `go 1.25`); re-run `sim-determinism` after the mannequin `blocks_bugs` change.
- **Mannequin render Increment-B** — sync each chunk's container states on subscribe (mirror tree-water in
  `handleChunkSubscribe`) so ALL viewers + rejoins see a dressed mannequin (Increment-A renders it for the
  dresser only). Keep ONE source of truth (the synced `ContainerState`); never store the outfit on the occupant.
- **Sign 2-wide retroactivity** — store signs widened to `[2,1]` render 2-wide in OTHER zones that already
  placed them (cosmetic, non-blocking); re-place signs there when those zones are next touched.
- **Richer NPC dialogue** — quests/lore/topics beyond Trade/Goodbye (the shell is extensible).

## UI polish run — remaining follow-ups (2026-06-28)
- **Mannequin LIVE outfit render** — the equip panel + storage + blocks_bugs ship now; the mannequin still
  shows its flat sprite. To render the WORN outfit as a paper-doll (Increment-A: compose locally from the
  ContainerUpdate when you open/dress it; Increment-B: sync each chunk's container states on subscribe so
  all viewers + rejoins see it), author `Player/layers/body/mannequin_{dir}{frame}.png` (Pipeline B) + a
  custom `Outfit{Body="mannequin", Shirt/Pants/Hair=null, +overlays}` → `CharacterComposer.Compose`, and
  inject at `TilemapManager.RenderOccupant`. Single source of truth = the synced ContainerState.
- **Store-sign 2-wide art** — the 11 store signs are now `[2,1]` in data; only the crossroads `signpost`
  was re-rendered. Regen the rest at the 32×24 aspect (gpt-image-1) so they don't stretch.
- **Re-run `sim-determinism`** — mannequins now `blocks_bugs:true` (in village_21_B's weaver), so the zone
  collision map changed (deterministically). Re-run the cross-client gate via the run-backend/docker path
  (local go toolchain can't build the plugin) — it should still PASS (every client gets the same new map).
