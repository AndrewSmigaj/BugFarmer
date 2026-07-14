# Investigation: 2-client late-join sync reports DIVERGED in village_21_B (~0.3%)

_status: **RESOLVED + FIXED + VERIFIED** (2026-07-14) · see resolution banner below_

## ✅ RESOLUTION (2026-07-14) — read this first
**True root cause:** S1/S2 predation added client sim-state that a late-joiner didn't reconstruct — the server
relayed the per-bug snapshot through a hand-declared Go `BugSampleData` struct that was **missing `hunt_target`/
`feed_until`/`feed_corpse_id`** (silently dropped on relay), and the per-swarm hunt assignment `_swarmStrikes`
was never snapshot-hydrated. So a late-joiner's wasps re-committed to DIFFERENT prey flies → permanent divergence.
(NOT the "center reconstruction" hypothesis explored below — the center is bit-identical; that section is
superseded and kept only for the investigation trail.)
**Fix (structural, keeps behavior identical):** (A) `SwarmSnapshotData.Bugs` → `json.RawMessage` so the server
relays per-bug state VERBATIM (no field can ever be dropped); (B) snapshot `_swarmStrikes` by mirroring the food
registry (`Export/Clear/Hydrate` + a relayed `hunts` section + clear-then-hydrate before replay). Species-agnostic.
**Verified (all green, non-vacuous — wasps actively hunting when B joined):** instrumented confirm (0 ht + 0 pc
A-vs-B mismatch over 11.6k wasp bug-ticks) · `SYNC: IDENTICAL` co-located (128k states) AND spawn-apart (98k
states) on a clean client · `sim-determinism` PASS · Go tests PASS. Contract documented in
`architecture_swarm_sync.md` §0; the skipped check baked into `test-changes`/`frontier-sync`/`certainty-assessment`.

---

_original status: READY — root cause CONFIRMED with trace evidence · investigated 2026-07-13 · (superseded by the resolution above)_

## UPDATE 2026-07-13 (diagnostic run — root cause RE-PINNED; supersedes §3 below)
A FRESH short co-located run (trace buffer bumped so the replay window isn't evicted) captured the divergence
at its ORIGIN. Findings, evidence-backed:
- **The origin tick is INSIDE the late-join REPLAY window.** B's snapshot range was tick 1608→1643; the first
  divergence is tick **1639** — so A processed it **live** while B processed it in **replay**. It is a
  **replay-vs-live** difference, not steady-state.
- **The swarm CENTER is bit-identical** — across all **154 swarms**, hasLeg and `_simCenter` match A-vs-B at
  1638 and 1639 (0 center-differs). The `_fallbackCenter` differs on 36 swarms but is a **red herring**
  (hasLeg=1 everywhere → the fallback is never read). So prey positions are identical too.
- **It is a per-bug HUNT/FEED branch divergence on a predator.** At 1639 the swarm takes a new fast (speed 572)
  **hunt leg** and a corpse appears (`foodNear` flips 0→1; server shows repeated strikes, satiation 100). The
  `ticksUntilChange` tell: **A holds tuc=2** (took the hunt/feed branch, which does NOT decrement tuc) while
  **B decrements to 1** (took the plain `wander`/`UpdateMovement` branch). So **A hunted/fed, B wandered** →
  velocity diverges (A→(319,10) toward target, B→(-10,120)).
- **All TRACED sim inputs are identical** (center, leg, rng, intent, position-history, foodNear-bool). The
  differing input is UNTRACED: the per-tick `preyBugs` (huntTargets) list, the specific food entry, or the
  `WantsConsumeCorpse`/feed state — reconstructed differently in replay than live.
- **Still open (needs one instrumented build):** which of {huntTargets, food-registry, consume-flag} differs.
  Add the move-branch + `HuntTargetBugId` + `FeedUntilTick` to the per-bug trace, one co-located run, done.
- **Note:** the authority-only passes (`RunPredationStrikes`/`RunCorpseConsumes`, SwarmManager.cs:603) are
  skipped during replay (`_syncState==Live` gate) — report-only, but a suspect if one leaves sim state
  (e.g. `WantsConsumeCorpse` un-drained).

## Debrief (read me first)
- **TL;DR:** The `run_sync_latejoin` co-located gate reports `SYNC: DIVERGED — ~0.3%` in `village_21_B`.
  The divergence is **real but cosmetically nil**: a **transient, sub-cell (≤0.2 cell), self-healing**
  per-bug position offset on a *handful* of bugs (3 of 881 at the first compared tick) in **mid-leg,
  fast-moving swarms** (hunting wasps). It is an **inherent, already-documented** property of how late-join
  reconstructs swarm movement legs — `SwarmManager.cs:1764-1768` literally says mid-leg swarms fall back to
  the metadata center "**acceptable, sub-cell, and self-correcting**." The offsets **decay to 0** within
  ~200 ticks (proven from the traces). It flips the **byte-exact** state hash, so the gate goes red even
  though the two clients are visually identical and re-converging.
- **NOT caused by:** the breeding-unify A1 change (baseline with A1 reverted diverges identically), the peace
  toggle / eco kit (client build predates them; village isn't peaceful), or a stray player (owner confirmed
  not logged in). The **core per-bug movement sim is deterministic** (`sim-determinism` PASS, byte-identical).
- **Why it surfaces now (hypothesis, timeline-consistent, not proven):** the recent relentless-wasp tuning
  (`hunt_speed_mult` 1.5→2.6, flee 2.4×) moves swarm centers *faster*, so the reconstruction offset for a
  mid-leg swarm is *larger* and takes *longer* to heal — long enough to survive into the comparison window.
  Earlier-session runs (before the speed bump / shorter) read `SYNC: IDENTICAL`.
- **Severity:** gameplay = negligible (invisible, self-heals, all authoritative outcomes ride server
  events). Gate integrity = a real problem: an "acceptable" red gate **masks REAL desyncs** — you can no
  longer read `SYNC: IDENTICAL` as a clean pass. There is also a small, non-zero risk that a sub-cell offset
  tips a *discrete* decision at a boundary (a strike-range check, a split threshold) and cascades; it stayed
  bounded (0.3%) in this run but that is not guaranteed.
- **Certainty:** mechanism **90%** (trace + the code's own comment predict the exact symptom) · "faster wasps
  amplified it" **60%** (plausible, timeline-consistent, unproven). **Needs your decision:** which remedy
  (see §5). **Status:** `READY` — investigate-only, no fix applied.

## 1. Issue
> Co-located `tools/run_sync_latejoin.sh village_21_B 120 12` → `SYNC: DIVERGED — 629/190576 shared-bug
> states differ (0.3%); hash-mismatch 217/217 ticks. First: tick 697`. Reproduces every run at the same
> tick (pinned seed 1337). Owner: "i am not currently logged in, a thorough investigation is needed."

## 2. Evidence (all from the 19:17 run, trace_A_191754 / trace_B_191725)
1. **Reproducible, not a fluke:** 3/3 runs diverge first at **tick 697** (pinned seed → same first-diverging
   tick each run); different bug id each run.
2. **Not A1 / not the recent changes:** baseline with A1 **reverted** diverges identically
   (`651/191104, first tick 697`). A1 restored → same.
3. **Core sim is deterministic:** `~/.dotnet/dotnet run --project tools/sim-determinism` →
   `DETERMINISM: ✅ PASS — 600 ticks, two runs byte-identical`. So it is **not** float / wall-clock /
   map-order in the movement math.
4. **Divergent bugs are a tiny set, all in mid-leg predator swarms:** at tick 697, **3 of 881** shared bugs
   differ, all `spawnSource=swarmSpawned` (runtime-spawned). The affected swarm `swarm_5b153b3b` is a nest
   wasp (`nests.go:138` "Nest 84,67 spawned resident swarm_5b153b3b (4 wasp_common)"; `predation.go:553`
   it struck prey). Bugs: `swarm_8aec0bd2/{1,2}`, `swarm_5b153b3b/2`.
5. **It is PER-BUG, decaying, and self-healing** — the killer evidence. Offset (A−B) over the overlap:
   | bug | t=697 | t=737 | t=777 | t=857 | t=897 |
   |---|---|---|---|---|---|
   | swarm_5b153b3b/2 | dx=−22 | −5 | +2 | −1 | **0** |
   | swarm_8aec0bd2/2 | dx=−211 | +48 | +42 | +51 | +27 |
   | swarm_8aec0bd2/1 | dx=−2 | −2 | −2 | −1 | −1 |
   Max offset ≈ 211 fixed-point units = **0.21 cell**; all trend toward 0 (damped). Every bug is `wander`
   on **both** clients throughout — no hunting during the compared window.
6. **Everything else matches:** at t=697 the divergent bug's `rngState`, `behavior`, `alertCooldown`,
   `ticksUntilChange`, `intentDir` are **identical** on A and B — only `x/y` (and `v` by ±1) differ. Same
   RNG + decaying position = the position was set *momentarily wrong at reconstruction*, not an ongoing
   non-determinism.
7. **`spawnTick`/`spawnSource` are a RED HERRING:** they differ on the divergent bugs (A=`swarmSpawned`
   tick 1, B=`snapshotApply` tick 103) — but **865 of the 878 MATCHING bugs also have a spawnTick mismatch**.
   They are `// DIAGNOSTIC` fields (`BugAgent.cs:32-33`), not sim inputs.
8. **Snapshot state is complete & exact:** the sampler writes exact fixed-point `agent.Position`
   (`SwarmVisual.cs:761`), and `ApplySnapshot` restores position, velocity, rng, land/hunt/feed timers, and
   the full `MovementState` (all 7 fields) — nothing the sim reads is missing.

## 3. Root cause
The late-joiner reconstructs each swarm's **center from its movement leg**, and for a swarm **mid-leg at
`snapshot_tick`** that reconstructed center is sub-cell different from the authority's. On join the client
clears legs (`SwarmManager.cs:1768`) and re-hydrates from snapshot metadata (`:1829`); per-bug wander is
relative to the center, so every bug in the swarm inherits the offset. Because each bug's wander (identical RNG)
re-seeks the center at its own phase, bugs **heal at different rates** — so at any single tick only a few still
show residual offset (reconciles the per-bug observation §2.5 with a per-swarm cause). The next `Think` emits a
fresh frontier-gated leg that re-syncs everyone → full self-correction.

The snapshot is fairly complete — the server embeds the current center (`match.go:2969` `X: swarm.WorldX`) **and**
the exact leg params incl. `LegStartTick` (`:2998-3005`); leg-embedding was itself a prior fix for mid-leg swarms
"falling back to the metadata center and diverging" (`:2993-2997`). So the **residual** is one (or both) of two
narrow gaps — pinning which is the first step of the fix:
- **(a) pruned-leg fallback:** a swarm whose leg is neither embedded (`HasLeg` false) nor still in the pruned
  `InfluenceLog` (`match.go:3006-3020`) falls back to the metadata center on the joiner while the authority still
  marches its real leg → sub-cell center gap, healed at the next Think.
- **(b) closed-form vs iterative rounding:** the client marches the leg **closed-form** (`SwarmManager.cs:324`
  "mirrors swarm.go Move"); if that accumulates fixed-point rounding differently than the authority's path over a
  long mid-leg span, the centers differ sub-cell until the next (short) leg resets it.

Either way it is the behavior the author anticipated and labeled "acceptable, sub-cell, and self-correcting"
(`SwarmManager.cs:1767`). The gate did not catch it before because the offset used to heal *before* the
comparison window; faster swarm centers (wasp hunt 2.6×) plausibly enlarged/slowed the heal enough to be caught.

## 4. What it is NOT (ruled out with evidence)
- Not the authority-only strike/consume passes (`SwarmManager.cs:603` `RunPredationStrikes` /
  `RunBugPlayerStrikes` / `RunCorpseConsumes`) — all read rendered positions and only *report* to the
  server; sim-inert (read §, they never touch `Agent.Position` or the hash).
- Not the hunt-target assignment — it rides the frontier-gated `EventSwarmSetTarget`
  (`InfluenceManager.cs:189-219`), applied at evt.tick on both clients.
- Not view-scoping — this is **co-located** (same chunks); view-scope only bites spawn-apart.
- Not a missing snapshot field — snapshot is complete (§2.8).

## 5. Recommendation (owner decision — no fix applied)
Three options, not mutually exclusive:
- **A — reconstruct legs exactly (principled, restores a clean byte-exact gate).** Carry each swarm's exact
  current center / leg-integration anchor in the late-join snapshot (not just the leg params), so a mid-leg
  swarm reconstructs bit-identically instead of falling back to the metadata center. Medium effort; touches
  the snapshot payload + `HandleLateJoinSnapshot` leg re-hydration. This is the fix that honors the
  "two players see the same bugs" invariant literally.
- **B — make the gate tolerant of the accepted heal (cheap complement).** Teach `tools/netcode/sync_diff.py`
  to PASS a sub-threshold (< ~0.25 cell) offset that **decays within K ticks**, and only FAIL growing/large
  divergence. Keeps the gate powerful for REAL desyncs without red-flagging the documented sub-cell heal.
  Risk: relaxes strict byte-exactness (must be tuned so a real slow-cascade isn't hidden).
- **C — accept + document only (status quo).** Cheapest, but leaves the gate red/unreliable and the small
  boundary-cascade risk unaddressed.

**Suggested:** **A** (source fix) as the real answer, optionally with **B** so the gate is meaningful in the
meantime. Avoid C alone — a permanently-red determinism gate erodes the one check that catches real desyncs.

## 6. Repro / how to re-measure
```
docker compose exec -T postgres psql -U postgres -d nakama -c "delete from storage where collection='zone_state' and key like 'village_21_B%';"
docker compose up -d --force-recreate nakama
tools/run_sync_latejoin.sh village_21_B 120 12          # co-located → DIVERGED ~0.3% first tick 697
# forensics: compare traces at a tick, track offset decay
#   trace_{A,B}_*.csv under /mnt/c/Users/emily/AppData/LocalLow/DefaultCompany/BugFarmerClient/
```
