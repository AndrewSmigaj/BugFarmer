# Cross-client determinism regression — root-cause audit (2026-06-20)

## Symptom (measured, not assumed)
Two real headless Unity clients in ONE live `village_21_B` match, compared **per-bug** (matched by
`(swarmId,bugId)`, comparing fixed-point `x,y,vx,vy` at the same sim tick, intersection only):
**57,117 / 59,462 shared-bug states differ (96%).** A few shared bugs are ~0.02 cells apart (near-match);
most are ~7 cells apart (≈ a full wander radius). Both clients are in the match together (`PLAYERS 2`),
each sees ~68k bug-rows. It **worked** (hashes matched tick-for-tick) before the recent ecology mechanics.

Method: `tools/run_sync_test.sh` (build current player → 2 headless clients → per-bug trace diff). The
prior whole-client `ComputeStateHash` comparison is WRONG for interest-managed clients (they hash different
subscribed *sets*) — fixed to per-bug-on-the-intersection.

## ROOT CAUSE (high confidence): mid-session swarm acquisition re-roots the bug chain
The server broadcasts only the swarm **center** (`SwarmUpdate` OpCode 20: `X,Y,Count,NextBugID,RemovedIDs`,
**no per-bug positions** — `match.go:1445-1465`). Each client reconstructs individual bug positions locally:
a bug starts at a position and then `Position += Velocity` every tick (`BugAgent.cs:253-259`) — a
**deterministic chain from spawn**, where velocity per tick is history-independent (CounterRng on
`seed,swarmId,bugId,tick`) but POSITION depends on the start point and the number of integrated ticks.

When a client first sees a swarm, `SpawnBug` roots every bug at **the swarm's CURRENT center, zero velocity,
at the client's CURRENT tick** (`SwarmVisual.cs:158-167`, `SpawnInitialBugs` 124-150). There is **no
re-simulation from the swarm's birth tick**. The ONLY path that transplants real per-bug state
(`x,y,vx,vy,rng,behavior`) is the **LateJoinSnapshot (OpCode 72)** — and it fires **once, at MatchJoin**
(`match.go:570, 2817-2829`). Chunk-subscribe deliberately sends **no** bug state
(`handlers_world.go:47-48`).

Therefore:
- A client present when a swarm SPAWNS gets the full chain (born at the birth center, integrated every tick).
- A client that acquires the same swarm **later** (interest management: the swarm wandered into its chunks,
  or it merged/split/respawned after this client's join snapshot) re-roots the bugs at "now" → a chain
  offset by the swarm's whole age → **permanent divergence**, never reconverged.

**This exactly matches the data:** the ~0.02-cell near-matches are swarms both clients have held since their
snapshot (chain intact); the ~7-cell (full-wander-radius) differences are swarms acquired mid-session and
re-rooted at the center. Broad 96% = most swarms were acquired mid-session by at least one client.

## Why it WORKED before and BROKE after the ecology work
The flaw is **structural and pre-existing**, but exposure flipped from rare to constant:
- Before: few, stable, long-lived swarms → essentially every client got every swarm at MatchJoin via the
  single snapshot → the no-snapshot acquisition path almost never ran.
- After (the recent mechanics): **3× swarm sizes + breeding-driven seeding (many more swarms) + mobile,
  churning swarms (merge/split/reproduce/relocate) + detritivores flipped to swarm**. Swarms are now
  numerous, mobile, and constantly created/destroyed, so **mid-session acquisition is the common case**.
  Every such acquisition hits the divergent re-root path.

So "I had high certainty the ecology was safe" was wrong because the ecology didn't add a determinism *bug*
per line — it changed the *population dynamics* such that the long-standing "per-bug state is only synced at
join" assumption no longer holds. Interest management + churn = constant late acquisition.

## CONTRIBUTING / INDEPENDENT divergence sources (each real, each needs fixing)
2. **Food registry: chunk-scoped input to a zone-wide sim (high).** Bugs feed via
   `BugAgent.TryFeedAtFood → InfluenceManager.TryGetNearestFood`, which changes a bug's motion (it hovers/
   lands). But `_food` is hydrated **chunk-scoped** (`GroundItemManager.cs:84/89`, server `broadcastToChunk`)
   while the bug sim runs **zone-wide** → two clients with different food knowledge feed the same swarm
   differently → divergence. Worse: the SAME food id is stored at the **cell-center** via the event path
   (`InfluenceManager.cs:167-180`, `cell+0.5`) but at the **raw sub-cell float** via hydrate
   (`GroundItemManager.cs:84`) → even when both "have" it, bugs pull to different points. Pre-snapshot food
   (windfall/seeded carrion, below `snapshotLastSeq`) isn't in the late-join log → joiners only learn it via
   chunk hydrate. The recent food (windfall, carrion, leaf-litter) is what made feeding common enough to matter.
3. **Merge/split apply trusts LOCAL state — the amplifier (high).** Client split moves its **own highest
   local alive ids**, count = `parent.Count - evt.parent_count` (`SwarmManager.cs:943-951`); merge maps the
   local absorbed set ascending to `new_bug_id_base+i`. Correct ONLY if every client's alive-id set already
   matches the server's exactly. So any pre-existing one-bug drift (from #1 root cause) is converted by the
   next merge/split into a **scrambled id→bug map = total divergence**. The detritivore flip
   (millipede/beetle `individual→swarm`) put two species onto this merge/split path for the first time
   **untested**, and 3× sizes + `SplitThreshold` multiply the event rate. Lifecycle events aren't the root
   randomizer; they're what turns small drift into 96%.
4. **Player-cell removal is async, not ledger-driven (real, but likely NOT this test's cause).**
   `PLAYER_CELL_LEAVE` is a client no-op; removal happens via the async presence callback
   (`SwarmManager.HandlePlayerLeft → RemovePlayerCell`), so clients drop a player at different ticks →
   flies(flee)/butterflies(curious) react differently. In THIS test no one disconnected and player ENTER is
   broadcast zone-wide, so player positions were consistent — so this didn't cause the 96% here, but it WILL
   desync on any mid-session disconnect. Fix anyway (drive removal from the ledger event).

## Ruled OUT (verified)
- Per-bug movement sim is deterministic (the `tools/sim-determinism` run-twice gate is green; CounterRng is
  counter-based/history-independent; all fixed-point).
- WorldSeed is one zone-wide value, broadcast identically (`WorldSeedProvider`, OpCode 68) — not per-client.
- RELOCATE / HUNT / FLEE / ActionState (centipede) all emit ordinary server-authored `SWARM_SET_TARGET`
  legs (`predation.go`, `centipede.go`) replayed identically; no client-side predation sim.
- Published vs canonical `species.json` movement data is identical (publish was run).
- Server run-to-run reproducibility (the `67c8ccf` determinism pass) is a *different* axis and is fine.

## Fix direction (NOT yet done — this is an audit)
1. **(Root) Per-swarm state on acquisition.** Send authoritative per-bug state (`x,y,vx,vy,rng,behavior`)
   whenever a client first becomes interested in an already-running swarm — i.e. extend the existing
   snapshot machinery to fire on **chunk-subscribe / swarm-enters-interest**, not only at MatchJoin. (The
   `ApplySnapshot` path already exists and is correct; it just isn't invoked mid-session.) Alternative
   (heavier): make spawn chain-deterministic and replay from the swarm's birth tick.
2. **(Food) One zone-wide, position-consistent food stream.** Make ITEM_ROTTED/FOOD events the single writer,
   broadcast zone-wide (already `nil`-recipient at `match.go:1487`), include pre-snapshot food in the
   late-join payload, and use ONE position convention (cell-center) in both the event and hydrate paths.
3. **(Amplifier) Validate merge/split against the event payload** instead of trusting local `parent.Count`;
   add a 2-client hash-parity harness scenario that forces a crawling-swarm (millipede/beetle) merge+split.
4. **(Player) Drive player-cell removal from the `PLAYER_CELL_LEAVE` ledger event**, not the async callback.

## How this was found
Five parallel determinism audits (late-join init; lifecycle events; predation/relocate/player-reaction;
food/RNG/seed; git forensics) + the committed `tools/run_sync_test.sh` per-bug 2-client test. The git
forensics fingered commit `14d38a6` (the "Phase 2" rebalance: 3× swarms + detritivore flip + SplitThreshold)
as the trigger that made mid-session acquisition common — consistent with the structural root cause above.
