# Investigation: a joining player out of step from its first live tick
_status: READY TO IMPLEMENT (pending the owner's approval of the fixes) · investigated 2026-10-06 · investigate-only
(no fix applied)_

## Debrief (read me first)
- **TL;DR:** a player who joins a zone that is already running can see slightly wrong bugs from the moment they
  arrive, until the server's drift check corrects them about 20 seconds later. There are **three separate causes**,
  each a piece of the join that does not describe the same moment as the rest: the bug **collision map** is sent "as
  of now" instead of "as of the snapshot" (a fence a centipede chews through just before you join is already gone in
  your replay); a **departed player's position** is removed outside the ordered event stream (so a player who
  leaves and comes back sees a phantom of themselves); and a joiner in the zone's **first ~10 seconds** can be given a
  stand-in instead of a real snapshot.
- **Root causes:** (B) `match.go:2955-2968` sends the current `BlocksBugsCells()`; (A) `SwarmManager.cs:259-263` removes
  a leaving player's cell on receipt while `InfluenceManager.cs:240-244` ignores `PLAYER_CELL_LEAVE`, and
  `match.go:3057-3069` filters snapshot cells by current members; (C) `SwarmManager.cs:2446-2468` skips the
  authority's first snapshot when its sim is still at tick 0, and the server then builds a seed-baseline stand-in.
- **Recommended fixes:** (B) build the joiner's collision map as of the snapshot's event cut (undo the in-window
  `OCCUPANT_BLOCKS_BUGS` changes, which the replay re-applies at their ticks); (A) apply `PLAYER_CELL_LEAVE` as a
  removal at its tick on every client, drop the on-receipt removal, and send the snapshot's cells unfiltered; (C) send
  the authority's first snapshot as soon as its sim starts (Stage 1.4's snapshot-on-demand then removes the gap
  for good). Each brings that piece of the join under the one rule the sync system already follows everywhere else.
- **Certainty:** causes B 95 · A 90 · C 95 · complete (no fourth cause) 85 · fixes 85 · design 85 · determinism
  (the fixes touch late join, a determinism change) 80 until the gates pass.
- **Risk / determinism:** all three fixes change what a joiner reconstructs; they must pass the Go tests, the
  sim-determinism replay, both late-join gate halves, and the new scenarios below. **Effort:** M (three small fixes,
  a Go test each, two new player scenarios).
- **Needs your decision:** approval to implement (as part of Stage 1, since 1.4 rebuilds the join anyway; or now as
  a separate fix). No design questions.

## 1. Issue, repro & evidence
> Found 2026-10-06 by the Stage 1.0e player tests (`docs/plans/village-slice.md`); the owner asked for a full
> investigation the same evening, with a recommended fix and no change to the game until he approves one.

- **Symptom.** In `REJOIN_AT=100 tools/run_players.sh 3 bench_village 300` (P1 in charge, standing still; P2 and P3
  join 8 and 16 s later and walk a route; P2 quits after 100 s and rejoins at once as the same account), P2 was out of
  step **from its first live tick in both sessions**, with the same bug count as the others, until the drift check
  resynced it ~20 s later. P1 and P3 stayed identical.
- **Expected.** Every computer identical from its first live tick (`architecture_swarm_sync.md` §0); the drift check
  is a safety net, not a routine path.
- **Repro.** The bench village as authored (normal speed), world seed **1704694170488522611** (run 3's; set on the
  throwaway bench copy), the base test build (`Build/SyncTest_base`, 2026-10-06), a fresh server each run. On this
  world a centipede starts beside the fence at (75, 107) and chews through it within the first ~9 s.
- **Evidence** (all git-ignored): run 3 `tools/_generated/players/2026-10-07T010130Z_3p_bench_village/`; the
  reproduction `tools/_generated/players/repro-2026-10-06/` — `full1`, `full2` (run 3 replayed), `join1-3` (short
  plain joins), `rejoin1-3` (short rejoins), `early1-4` (plain joins with both 500-tick traces covering the whole
  join, replay included). Each holds hashlogs, traces, player logs and the server log.
- **Acceptance test.** On this world, the short plain join, the short rejoin and the full run-3 scenario repeated ≥5
  times each: every player identical from its first live tick, no drift resync; plus the regression tests in §5.

## 2. Root cause (the chains)
**Every out-of-step session today has exactly one of three causes; the in-step sessions have none** (or the cause
was present but no bug tested it during the replay — §6).

| Session | Cause present | Outcome |
|---|---|---|
| run 3 P2, full2 P2, join1, join2, early2, early3, rejoin1-3 (first sessions) | **B** fence chewed in the replay window | out of step |
| early1 | **C** no authority snapshot yet | out of step |
| run 3 P2 rejoin, full2 P2 rejoin, rejoin1-3 (rejoins) | **A** stale own position | out of step |
| early4, full1 P2 | none | identical |
| join3 (B present), full1 P2 rejoin (A present) | present, not tested by any bug in the window | identical |

### B. The collision map is "as of now", the replay starts at the snapshot
1. A late joiner's state is the authority's snapshot at tick S plus the replay of every event from S to the join
   (`HandleLateJoinSnapshot`, `SwarmManager.cs:1840` on). The authority snapshots every 10 s
   (`SwarmManager.cs:121`, `:2446-2460`), so the replay can span up to ~10 s.
2. Separately, every joiner is sent the zone collision map (`match.go:647-649` on join, `:2861` on resync):
   `sendZoneCollisionMap` (`match.go:2955-2968`) sends `BlocksBugsCells()` (`state.go:719` on) — the **current**
   blocking cells, with no tick or event position. Its own comment: "dynamic changes after this ride
   OCCUPANT_BLOCKS_BUGS events".
3. A centipede chewing through a fence removes it (`centipede.go:119`) through the shared removal path, which emits
   `OCCUPANT_BLOCKS_BUGS` (blocked=false) at that tick (`handlers_world.go:537-543`).
4. If that happens between S and the join, the joiner's base map already lacks the fence, so throughout its replay
   from S the cell is open — while on the authority it stayed blocked until the chew finished. Any bug that tests
   that cell in the window moves differently.
5. **Evidence:** the joiners that went out of step hydrated **5,115** blocking cells, the authority and the in-step
   joiner **5,116** (`player_P*.log`, "Zone collision map hydrated"); the server log shows "Centipede … gnawed through
   the fence" 1.3–1.5 s **before** each failing join and 0.2 s **after** the in-step one; in early2 and early3 the
   first bug to differ, at ticks 4–5 of the replay, is **the chewing centipede itself**, its x position one step
   ahead (difference = its x speed exactly: 0.349 and 0.136) at x ≈ 75, beside the fence picket the village data puts
   at (75, 107) (`village_21_B/chunk_2_3.json`, local (11, 11)).
6. The same holds on a resync (the map is resent as of now, the resync replays from the snapshot).

### A. A departed player's position is removed outside the ordered stream; a rejoin brings it back
1. The bug sim's player inputs are the cells in `InfluenceManager._playerCells`, read in player-id order
   (`SwarmManager.cs:1002-1023`); bugs react to them (curious, fleeing, attacking).
2. When a player leaves, the server deletes its cell and emits `PLAYER_CELL_LEAVE` (`match.go:762-775`). The client
   **ignores** that event ("keep last known position", `InfluenceManager.cs:240-244`). The only removal is
   `SwarmManager.HandlePlayerLeft` (`SwarmManager.cs:259-263`), on **receipt** of the presence-leave message — at
   whatever tick each client is on. A sim input outside the ordered stream (the invariant in
   `nakama/modules/world/CLAUDE.md`).
3. A joiner's snapshot carries the authority's player cells at the snapshot tick, **filtered to the zone's current
   members** (`match.go:3057-3069`; its comment names "a known ~4s micro-gap"). The filter was there to keep departed
   players from lingering forever, which only happens because the leave event is ignored.
4. A player who leaves and rejoins as the same account is a member again, so its **old** cell passes the filter. If
   the authority's snapshot predates the departure, the rejoiner replays with a phantom of itself at its old spot,
   while the others removed that cell on receipt.
5. **Evidence:** every rejoin hydrated one cell more than the other players present (3 with P1 and P3 present; 2 with
   only P1); in rejoin1-3 the traces show the rejoiner seeing **2 players for 11-12 ticks of its replay while the
   authority saw 1**, and the first bugs to differ are **curious or fleeing on the rejoiner, wandering on the
   authority**, ~100 cells from spawn where P2 had walked to. None of these rejoins had a fence chewed in its window.

### C. A join in the zone's first ~10 s can get a stand-in instead of a snapshot
1. The authority's snapshot loop waits 0.5 s and sends its first snapshot — but `SendAuthoritySnapshot` returns
   without sending if the sim is still at tick 0 (`SwarmManager.cs:2449-2468`); the next try is 10 s later.
2. With no authority snapshot, the server builds a **seed-baseline bootstrap** for the joiner (server log: "No
   authority snapshot yet, creating seed-baseline bootstrap for late joiner"): swarms created from metadata at their
   centres, no events. That is only right at tick 0; by tick 95 the authority's bugs have moved.
3. **Evidence:** early1 — the authority's first snapshot came at tick 96 (early2's at tick 3); P2 joined at tick 95,
   got a 49 KB package with 0 swarms and 0 events (others ~737 KB), and every bug differed at its first live tick.

## 3. How the system actually works (late join)
`HandleLateJoinSnapshot` replaces the whole state: player cells cleared then set from the snapshot; swarm legs
cleared and re-set from metadata; the food registry, hunt assignments and subdued set hydrated from the snapshot
(each "BEFORE replay", one-time-base rule); swarms not in the snapshot pruned; swarms made with exactly the snapshot's
bug ids; then the replay is deferred until the collision map has loaded ("Late-join replay DEFERRED until the zone
collision map loads"), the influence log replays from the snapshot tick to the end tick, and the client goes live.
Live events apply at their own tick in seq order (`ProcessEventsForTick`, `SwarmManager.cs:961-991`). The rule the
design follows everywhere else: **the joiner's starting state describes the snapshot tick, and everything after it
arrives as ordered events.** The three causes are the three places that break it.

## 4. Ruled out (not the cause)
- **A saved spawn position:** every player joined without a character, at the default spawn.
- **The joiner's own exact position fed to the sim:** the per-tick player list comes only from the cells.
- **A join-side on-receipt write:** nothing adds a cell on presence join (every `SetPlayerCell` / `RemovePlayerCell` /
  `OnPlayerJoined` call site listed).
- **The duplicate event at going live** (`DUPLICATE EVENT BEFORE APPLY` for the package's last seq): in-step joiners
  had it too, and it is dropped, not applied twice (`SwarmManager.cs:494-497`). A protocol oddity worth tidying in
  Stage 1.4 (the package's last event is also sent live), not this fault.
- **A late event / protocol violation:** none logged by any player.
- **The world itself / the snapshot's bug data:** P3 joined the same worlds later (snapshot at ~tick 100, after the
  early chew) and was identical every time; the per-bug snapshot record covers position, speed, random state,
  behaviour, intent, landing, eating, hunting and the lunge (`SwarmVisual.cs:769-815`).
- **Other join-time data with the same flaw:** the joiner gets the snapshot (all snapshot-moment), the collision map
  (cause B), the roof map (cosmetic) and a cosmetic SwarmUpdate (`match.go:625-660`); nothing else.

## 5. Proposed solution
**B — the collision map as of the snapshot.** In `sendZoneCollisionMap`, start from `BlocksBugsCells()` and undo, in
reverse seq order, every `OCCUPANT_BLOCKS_BUGS` event in the influence log after the snapshot's last applied seq
(re-block a cell an in-window event opened, open a cell an in-window event blocked); the joiner's replay re-applies
them at their ticks. Same for the resync path (`match.go:2861`). With no snapshot (the bootstrap), send the current
map as today. *Alternatives:* the authority includes its collision set in each snapshot — rejected (~5,000 cells
every 10 s, duplicates the static map); the client undoes the in-window events itself — rejected (the server already
knows the cut, and the map would need its own "as of" position). *Files:* `nakama/modules/world/match.go` (and a
helper beside `BlocksBugsCells` in `state.go`). *Test:* a Go test — snapshot at seq S, a fence removed at S+k: the
joiner's map still has the cell; a removal before S: it doesn't; a place-then-remove inside the window nets out.

**A — a player's departure as an ordered event.** Client: apply `PLAYER_CELL_LEAVE` as a removal at its tick when the
stored cell matches the event's cell (a move's LEAVE + ENTER pair in one tick still nets to the new cell, applied
before that tick's sim step), and stop removing the cell in `HandlePlayerLeft`. Server: send the snapshot's cells
unfiltered (the departure replays at its tick); the filter and its "micro-gap" comment go. *Alternative:* keep the
filter and also filter rejoins by session — rejected (keeps the input outside the stream; the micro-gap stays).
*Files:* `InfluenceManager.cs`, `SwarmManager.cs`, `match.go`. *Test:* a sync-harness or player scenario — a player
leaves and rejoins as the same account; every player identical from the first live tick.

**C — never a stand-in after the first moments.** Client: the authority's first snapshot waits for the sim to start
(retry every frame until tick > 0) instead of skipping to the 10 s mark. Stage 1.4 (snapshot on demand, already
designed in the plan) then asks the authority for a snapshot whenever someone joins, which closes the gap for good.
*Files:* `SwarmManager.cs`. *Test:* a join at ~2 s after the zone starts gets a real snapshot (server log) and is
identical.

**Determinism / risk:** all three change what a joiner reconstructs — determinism changes under
`complex-change-review.md` and the `frontier-sync` recipe; none changes the per-tick simulation itself. Gates: Go
tests (Docker), sim-determinism, `run_sync_latejoin.sh` both halves, `run_players.sh` with the leave and rejoin
options, and the acceptance runs on world 1704694170488522611.

## 6. Critical review + certainty (evidence-gated)
| Claim | % | Evidence | What would raise it |
|---|---|---|---|
| B is a real cause | 95 | code (`match.go:2955-2968`, `state.go:719`); map 5,115 vs 5,116; chew timing in every case; first differing bug = the chewer, one x-step at the fence | the fix removing it in the acceptance runs |
| A is a real cause | 90 | code (`SwarmManager.cs:259-263`, `InfluenceManager.cs:240-244`, `match.go:3057-3069`); +1 player in every rejoin's replay; curious/fleeing bugs first | logging the phantom cell's coordinates (inferred from count + filter) |
| C is a real cause | 95 | server log line; first snapshot at tick 96 vs 3; the skip in `SendAuthoritySnapshot` | — |
| No fourth cause | 85 | every out-of-step session today explained; join-time data audited | the acceptance runs passing after the fixes; more worlds and more players |
| The fixes work | 85 | each restores the snapshot-moment rule the rest of the join follows | built + the gates |
| Good design | 85 | removes the exception rather than patching around it (the filter, the on-receipt removal) | review of the built diff |
| No sync regression | 80 | the per-tick sim is untouched; only reconstruction changes | the gates |

*A presence that is necessary but not sufficient:* join3 had a chew in its window and full1's rejoin carried the
phantom, yet both stayed identical — a cause only shows if some bug tests the opened cell or strays near the phantom
during the replay. Consistent with the mechanism, and why the fault is intermittent.

## 7. Lens analysis
- **Determinism:** each cause is a sim input that reached a client outside the ordered stream or at the wrong moment
  — the invariant in `nakama/modules/world/CLAUDE.md`. The fixes put each back under it.
- **Verification:** today's gates passed because their worlds had no early fence chew and they never rejoin; the
  player tests found it. New scenarios (a chew in the window, a rejoin, a very early join) close that gap.
- **Simpler alternative:** "just resync joiners straight away" — rejected: it hides the faults, doubles join traffic,
  and a resync has fault B too.
- **Hidden cost:** fault B can also make a *resync* fail to converge (a chew in the resync window), so a client could
  loop on resyncs in a busy zone.
- **Test tooling (found on the way):** `run_players.sh` deletes only files P1..N at its start but copies every
  `hashlog_P*` / `trace_P*` it finds, so a 2-player run after a 3-player one compares against a stale P3 file. To
  fix with the rest.

## 8. Gap-closing log
- Reproduced on run 3's world: 6 of 8 plain/first-session joins and every rejoin out of step (`full1-2`, `join1-3`,
  `rejoin1-3`); then `early1-4` with both traces covering the replay: the first difference at replay ticks 4-5.
- Traced the first differing bug to the chewing centipede and the fence cell; matched the collision-map counts.
- Separated the rejoins from the fence cause (no chew in their windows) and measured the extra player in their replays.
- Found cause C in early1 (stand-in snapshot) and its origin in the authority's first-snapshot skip.
- Audited every join-time message for the same flaw (none other).

## 8b. A related fault found later the same night (not investigated)
In the behaviour check's runs, one client of 79 kept its simulation at tick 0 for its first 5 s ("Frontier stalled 5s
(simTick=0, authTick=46)"), resynced, and then kept receiving events for ticks it had already simulated ("PROTOCOL
VIOLATION: Old event not applied", `SwarmManager.cs:970-976`), resyncing again each time for the rest of the run
(`tools/_generated/scaling/2026-10-06-paired/invalid/s10_behave_1000_feed50_seed12/player.log`). It belongs to the
same slow-start family as cause C and should be investigated with it.

## 9. Open decisions for you
- Approve the three fixes (B, A, C as above), and when: as part of Stage 1 (1.4 rebuilds the join anyway; C's
  lasting fix is 1.4's snapshot on demand), or now as their own change. My recommendation: B and A now (small,
  self-contained, and the player tests will keep hitting them), C's small part now and its lasting part in 1.4.
