# Zone Swarm Sync — Authoritative Client + Deterministic Followers

How bug-swarm simulation stays consistent across clients: one authority client per zone
runs the canonical simulation and relays tick frontier updates, an event ledger, and
periodic snapshots through the server; follower clients replay deterministically and
recover from snapshots on late-join or drift.

## 1. Architecture

### 1.1 Roles

Authority Client (per zone):

Runs the canonical swarm simulation for the zone.

Produces authoritative outputs:

tick frontier updates

event ledger (influence events)

periodic snapshots (for late join + drift recovery)

Sends these to the server for relay.

Server (Nakama):

Does not simulate swarms.

Acts as: authority assigner, validator, relay, and snapshot cache.

Builds late-join packages from cached snapshot + log slice.

Follower Clients (non-authority):

Run deterministic simulation only when they have all authoritative inputs required.

Must never “invent” missing inputs.

Use snapshots for:

late join bootstrapping

drift correction (optional)

recovery if protocol violations occur

1.2 One design choice: Ledger-first correctness

Correctness mechanism is:

Authoritative inputs (event ledger) + deterministic simulation on clients

Snapshots are supporting infrastructure (bootstrap / safety net), not the primary feed.

This choice implies:

Followers must apply the same events in the same order and simulate the same ticks.

Any mismatch is a contract violation in tick labeling, seq continuity, epoch handling, or event delivery assumptions.

2) Mandatory Concepts (No Exceptions)
2.1 Epoch (Session / Authority generation) — REQUIRED

Problem it solves: stale events/snapshots/seq baselines from previous sessions causing freezing, “old event not applied”, watermark mismatch, etc.

Rule:

Every zone has an integer epoch.

epoch increments whenever:

authority changes (handoff)

zone empties and later restarts

server decides to reset for any reason (e.g., detected inconsistency)

All messages include epoch.

Clients drop any message whose epoch != current epoch.

When epoch changes, clients purge inbox, reset seq baselines, request late join snapshot for the new epoch.

2.2 Sequence Numbers (seq) — Single monotonic stream per epoch

Rule:

Within a given epoch, authoritative events have strictly increasing seq (0..N).

seq is global within epoch (not per tick).

seq assignment is done by the authority client (or server, but choose one; do not mix).

Server validates monotonicity: reject/ignore messages from non-authority or decreasing seq.

2.3 Tick Contract (the offset-killer) — define it once

You must pick exactly one contract. Use this one:

Contract:

tick T refers to the world state after simulating tick T.

Events labeled tick T are applied after simulating tick T, before simulating tick T+1. (End-of-tick semantics.)

This matches the common pattern you already wrote in comments.

Therefore:

A snapshot labeled snapshot_tick = T must contain the state after simulating tick T (and after applying events for tick T, if your semantics say those apply end-of-tick; see below).

2.4 Event application semantics (must match the contract)

Given end-of-tick semantics, the deterministic loop must be one of these two and must be consistent across authority and followers:

Semantics A (recommended for clarity):

Simulate tick T using inputs already applied from prior step.

Apply events stamped tick T (these become visible starting next simulation).

Increment to T+1.

Semantics B (equivalent but differently framed):

“AdvanceOneTick” does:

apply events for current simulationTick (the tick being left)

increment tick

simulate new tick

You already have something like B.

Important: whichever ordering you use, snapshot labeling must match the state that exists after the step corresponding to “after simulating tick T”.

3) Message Set (Authority per zone)

All messages include: zone_id, epoch.

3.1 ZoneAuthority (server → all clients)

Sent on join and on handoff.
Fields:

zone_id

epoch

authority_id

authoritative_tick (current tick per contract)

last_event_seq (largest committed seq in this epoch up to that tick)

Client rules:

If epoch changes, reset local state and request late join snapshot unless you are authority and already live.

Authority flag is derived from authority_id == localUserId.

3.2 ZoneTickBroadcast (authority → server → clients)

Sent every tick (or at a controlled rate, but conceptually per tick).
Fields:

zone_id

epoch

authoritative_tick

last_event_seq (watermark: “all events with seq ≤ this are committed/finalized”)

Follower tick gate uses:

frontier = authoritative_tick

watermark = last_event_seq

3.3 InfluenceBroadcast (authority → server → clients)

Batch authoritative events.
Fields:

events[] where each event has:

tick (the event’s tick label)

seq (global monotonic per epoch)

type

payload

Client ingestion:

Deduplicate by seq

Reject if seq ≤ lastAppliedSeq (duplicate-after-apply)

Store in inbox by seq, also keep sortable list (tick, seq)

3.4 ZoneSnapshot (authority → server; server caches latest)

Fields:

snapshot_tick

snapshot_last_event_seq

player_cells (state)

swarms (state: positions/velocities/bug ids)

optional state_hash (highly recommended)

Server stores last snapshot per (zone_id, epoch).

3.5 LateJoinSnapshot (server → joiner)

Server sends a packaged bootstrap:
Fields:

snapshot_tick

snapshot_last_event_seq

end_tick (current authoritative_tick)

end_last_event_seq (current watermark)

player_cells (state at snapshot_tick)

swarms (state at snapshot_tick)

influence_log (events needed to catch up)

Critical rule: influence_log must cover exactly the missing seq interval:

include events where seq ∈ (snapshot_last_event_seq, end_last_event_seq]

ticks can be older/newer, but seq interval must be continuous or client will gate.

3.6 ZoneHandoff (server → joiner)

Sent after LateJoinSnapshot to tell the joiner where “live” begins.
Fields:

live_start_tick (typically end_tick + 1 or equal to end_tick depending on your live definition)

last_event_seq (baseline watermark at handoff time)

epoch

Client uses this to enter LIVE and set correct baselines (details below).

4) Client State Machine (Unity)

States:

Joining

Replaying

HandshakeWait

Live

4.1 Joining

Waiting for ZoneAuthority or LateJoinSnapshot depending on whether you’re first joiner or late joiner.

Do not simulate.

4.2 Late join flow (Replaying → HandshakeWait → Live)

On LateJoinSnapshot:

Set currentEpoch = msg.epoch. Purge all prior epoch state.

Clear inbox, clear player cells, clear swarms (or replace per snapshot).

Apply snapshot state:

_simulationTick = snapshot_tick (must match the snapshot tick contract)

_lastAppliedSeq = snapshot_last_event_seq IMPORTANT

Hydrate state (player_cells, swarms) as state, not fabricated events.

Enqueue all influence_log events into inbox (dedup by seq).

Replay deterministically from _simulationTick to end_tick using the same AdvanceOneTick.

During replay, you should not use watermark gating (you already have all needed events; if not, it’s a server packaging bug).

Enter HandshakeWait.

On ZoneHandoff:

Validate epoch matches.

Set:

_authoritativeTick = live_start_tick (or end_tick depending on your definition)

_frontierWatermark = msg.last_event_seq

Ensure _lastAppliedSeq >= snapshot_last_event_seq already true.

Enter LIVE.

4.3 Live tick gate (followers)

Followers advance only when:

_simulationTick < _authoritativeTick

HasAllEventsUpTo(_frontierWatermark) is true

HasAllEventsUpTo(watermark) must check continuity from _lastAppliedSeq+1 to watermark in inbox.

4.4 Live tick gate (authority)

Authority does not gate on receiving events; it is the producer.
Authority simulates continuously and publishes:

tick broadcasts

influence events

snapshots

5) Invariants and “Do Not Break” Rules (Debug Session)
5.1 Hard invariants to assert in logs

For every client (authority + followers), at the moment they simulate tick T:

simulationTick increments by exactly 1 per simulation step.

Events applied satisfy:

applied in increasing seq

never apply seq <= lastAppliedSeq

If follower is in LIVE:

HasAllEventsUpTo(watermark) must be true when it advances.

5.2 Drop rules (prevent stale chaos)

Clients must drop:

any message with wrong epoch

any influence event with seq <= lastAppliedSeq (duplicate)

any influence event from non-authority (server should already prevent this)

Do not drop “old tick” events solely because evt.tick < simulationTick unless you have epoch guarantees and you understand the consequences. Old-tick events can be legitimate under reordering; seq ordering is what matters.

6) Where your current pain usually comes from (review for correctness)

This section is not guesses about “the one bug”; it’s a correctness checklist.

6.1 The 1-tick offset

This happens when any of these are inconsistent between authority and follower:

snapshot tick label does not represent the tick state you think it does

follower sets _simulationTick wrong after snapshot

replay loop applies events for tick T but simulates T+1 (or vice versa) differently than authority’s own progression

The only way to kill this is to lock the tick contract and log “what tick does this state correspond to” on both ends.

6.2 Freezing

Freezing almost always equals:

follower gate never opens

because _lastAppliedSeq baseline is wrong after late join

or watermark refers to seq values the follower will never receive (epoch mismatch / server packaging bug)

Baseline requirement:

After snapshot application: _lastAppliedSeq = snapshot_last_event_seq

After handoff: _frontierWatermark must be >= _lastAppliedSeq, and events up to watermark must be receivable for this epoch.

6.3 “Old event not applied” protocol violations

This indicates:

You processed events in a way that left older tick events still in inbox by the time you advanced beyond them, OR

The event tick labeling contract changed midstream (authority differs), OR

You are mixing epochs without realizing.

If epochs are correct, “old event not applied” is often a tick-label mismatch, not a network issue.

7) Debugging Plan (Fresh session, minimal thrash)
7.1 Debug Principle: One change, one confirmation

During this session:

Do not apply bundles of changes.

Do not refactor.

Add instrumentation first, then one fix.

7.2 Build a “single source of truth” trace line

Add a single log line emitted:

by authority every N ticks

by each follower every N ticks
that includes:

epoch

role (AUTH/FOLLOW)

simulationTick

authoritativeTick

lastAppliedSeq

watermark

inboxCount

stateHash (bugs + any other deterministic state you care about)

Example format (single line):
TRACE epoch=7 role=FOLLOW sim=27884 auth=27890 applied=512 watermark=520 inbox=9 hash=...

7.3 Late join trace (exact checkpoints)

On follower when handling LateJoinSnapshot, log:

APPLY_SNAPSHOT epoch=?, snapshot_tick=?, snapshot_last_seq=?, end_tick=?, end_last_seq=?

after setting baselines:

BASELINES simTick=?, lastAppliedSeq=?

after enqueueing influence_log:

INBOX minSeq=?, maxSeq=?, count=?

after replay:

REPLAY_DONE simTick=?, lastAppliedSeq=? hash=?

on handoff:

HANDOFF live_start_tick=?, last_event_seq=? => LIVE

These 5 logs alone usually expose the offset or freeze instantly.

7.4 Authority snapshot labeling verification

On authority when sending snapshot, log:

SNAP epoch=? snapshot_tick=? snapshot_last_seq=? simTick=? lastAppliedSeq=?

And ensure:

snapshot_tick equals the tick of the state you are actually serializing.

snapshot_last_seq equals the last applied/committed seq included in that serialized state.

7.5 Server late join packaging verification

On server when constructing LateJoinSnapshot, log:

epoch

snapshot_tick

snapshot_last_seq

end_tick

end_last_seq

events_count

first_event_seq, last_event_seq in influence_log

And assert:

influence_log covers seq interval (snapshot_last_seq, end_last_seq] with no gaps.

8) Implementation Guidance: What to watch out for (Nakama + Unity)
8.1 Do not mix “authority tick” sources

Only the authority client defines authoritative_tick and last_event_seq for the epoch.
Server relays. Followers obey.

8.2 Snapshots are state; logs are deltas

Snapshots contain point-in-time state.

influence_log contains changes after snapshot (by seq interval), not “events after snapshotTick by tick filter”.

Do not filter influence_log by tick alone. Use seq intervals.

8.3 Deterministic ordering

All deterministic loops must be stable:

swarm iteration sorted by swarmId

bug iteration sorted by bug_id

player targets sorted by playerId

You already do this; keep it.

8.4 Unity timing drift is not the cause of 1-tick offset

A stable 1-tick offset is almost never float drift. It’s semantic labeling or baseline mismatch.

9) What Opus must NOT do (anti-kneejerk guardrails)

Opus must:

Not “fix” by adding more snapshots/state unless a trace proves missing state.

Not change tick semantics without changing the explicit tick contract text and updating both authority + follower code.

Not implement heuristic drops like “ignore evt.tick < simTick” unless epoch and seq continuity rules are proven correct and there is a precise reason.

Opus should:

First implement the trace lines exactly.

Then identify whether the bug is:

epoch mixing

snapshot tick labeling mismatch

wrong baseline lastAppliedSeq after snapshot/handoff

server packaging gaps in influence_log seq interval

Then make one minimal fix.

10) Success Criteria (end of debug session)

A) No freezing:

In LIVE, followers show canAdvance=true regularly.

HasAllEventsUpTo(watermark) returns true whenever frontier moves.

B) No permanent 1-tick offset:

For the same (epoch, tick) after LIVE transition, authority and follower stateHash match.

C) No protocol violations:

“Old event not applied” never triggers in a healthy run.

## 11. Implemented world lifecycle & recovery (2026-06)

How the above is wired in practice, and the fixes that made it hold up under real play. The
headless `tools/sync-harness` (real Nakama .NET client, no Unity) reproduces/verifies these.

### 11.1 World lifecycle (server, `match.go`)
- **Entry is via `world_enter(zone_id)`** (RPC): find-or-create the canonical *singleton* world per
  zone (deterministic key `default_<zone>`), reuse its live match or recreate on demand, return the
  match id. The frontend never creates worlds; Normal=`village_21`, Test=`sim_test`.
- **Pause when empty:** `MatchLoop` early-returns when no players/presences are connected — no tick
  advance, no swarm sim/merge/split, no broadcasts. A world only "runs" while someone is in it; a
  joining player resumes from the frozen `TickCount`. (Replaces the old never-terminating match that
  ticked forever with zero players and eventually crashed in merge/split.)
- **Empty-reset:** when the last player leaves, the zone's sync state resets
  (`NextSeq=0, InfluenceLog=nil, Snapshot=nil, AuthorityUserID=""`) **and `PendingInfluence` is
  cleared** — see 11.3.

### 11.2 Frontier stall ≠ "caught up" (client, `SwarmManager.Update`)
The frontier-stall watchdog must only fire when the client is genuinely **behind and blocked**
(`simTick < authTick` but missing events). Being **caught up** (`simTick == authTick`, the normal
state between tick broadcasts) must NOT count as a stall — the client catches up within the frame a
broadcast arrives, so the gate ends each frame caught-up. The earlier code counted that as a stall,
so `_frontierStallTimer` never reset and fired a spurious resync every ~5s (and, before the lifecycle
fixes, hung when that resync got stuck in `Joining`). Reset the timer when caught up; only accumulate
when behind-and-blocked.

### 11.3 Reconnect must not leak stale seqs (server)
On re-entry a client bootstraps as first-client with `LastEventSeq=-1` and expects a fresh,
contiguous seq stream from 0. An influence event from the last tick before everyone left could be
stranded in `WorldState.PendingInfluence` (the empty-reset cleared `InfluenceLog`/`NextSeq` but not
the pending queue, and pause-when-empty skips the normal per-tick broadcast+clear). Delivered on
resume, it created a `lastSeq` ≫ `watermark` gap that `HasAllEventsUpTo` can never close → genuine
stall. Fix: clear `PendingInfluence` in the empty-reset (and defensively in the pause guard) so the
next client always gets a clean stream from seq 0.

### 11.4 Test/dev knobs
Test zones are ordinary zones authored by `tools/make_test_zone.py`; the zone config is the single
source of truth (`static` = no spawn/merge/split, `swarm_size` = fixed count, `seed` = fixed world
seed). There is no separate `debug_mode` flag or `species_debug.json` anymore.

If it triggers, logs immediately show whether it’s epoch mismatch, gap in seq, or tick contract mismatch.
## 12. Combat v1: per-bug HP + melee (2026-06)

**Design rule: the ledger carries SIM-STATE only.** Bug *removal* (kill = catch = shed) flows
through `RemoveBugs` + `BUG_REMOVED` influence events exactly like catching — deterministic
application at the event tick, late-joiner replay included. Per-bug *HP* is **display-only**
(nothing in the sim reads it, it is not in the state hash) and deliberately does NOT ride the
ledger: it flows through `MeleeResultMessage` (OpCode 89) + a late-join seed.

**Opcodes:**
- **88 `MeleeAttack` (C→S)** — ONE message per swing: `{click_x, click_y, hits:[{swarm_id,
  bug_ids[]}]}`. A swing that intercepts several swarms is one payload (per-swarm messages would
  trip the per-player rate limit — see the catch-burst fix below).
- **89 `MeleeResult` (S→C)** — `{attacker_id, click, results:[{swarm_id, damaged:[{bug_id,hp}],
  killed:[]}]}`. The SOLE per-bug HP display channel + combat cosmetics. `hp` is ABSOLUTE
  (last-writer-wins converges when two players hit the same bug); clients apply HP from their OWN
  echo too and skip only the cosmetic flash. `killed[]` is the pop cue/attribution — authoritative
  removal is the `BUG_REMOVED` event in the same network flush (89 → events → ZoneTickBroadcast).

**Server state:** `SwarmState.BugHP map[int]int` — sparse, stores only damaged bugs (absent =
species `max_hp`; the `RemovedBugIDs` precedent). Cleanup is centralized **inside `RemoveBugs`**
(catch, melee kill, and split-shed all clean their entries). At split/merge, HP transfers along the
deterministic id mappings (shed ids sorted ASCENDING → child `0..n-1`, harvested BEFORE the
`RemoveBugs(shed)` call; absorbed alive ids ascending → `newBugIDBase+k`).

**Validation (the catch trust model):** the server holds no per-bug positions, so it validates
alive-ids (`IsBugAlive`), player→click reach (+0.5 slack), per-weapon `cooldown_ticks` via the
shared `validateToolCooldown`/`LastToolTick` (also closes weapon-swap bypass), and a per-SWING
`max_targets` cap applied across swarms in sorted order. Hit GEOMETRY (the swept sector,
`arc_degrees × reach`) is client-detected — `SwarmVisual.GetBugsInSector` queries RENDER transform
positions (deliberate divergence from catch's sim-position circle; both safe since only validated
ids matter). One full-sector query at swing START (no per-frame accumulation): zero perceived
latency, and the animator's sweep trail traces the exact queried arc.

**Client display:** `BugVisual.DisplayHP` (-1 = full) — display-only by contract, persists the
damaged tint + hit flash, and **rides split/merge bug-moves for free** (the BugVisual object moves
between swarms). Late joiners seed it from `SwarmData.bug_hp []BugHPEntry` (an ARRAY — JsonUtility
cannot parse dictionaries), populated only by `sendLateJoinSnapshot` from server-owned `BugHP`;
subsequent 89s converge it. No InfluenceLog dependency → pruning is irrelevant to HP.

**Catch-burst fix (pre-existing ghost bug):** `handleCatchBug` stamped its rate limit BEFORE
validation, per message — a single net swing hitting two swarms sent two messages and the second
was silently dropped, leaving optimistically-removed bugs as client-side ghosts until drift resync.
Now: tool stats are data-driven (`state.Entities[EquippedTool]` — this also fixed large_net being
treated as a bare hand), and the rate limit is per-SWING (`LastCatchTick`): same-tick messages
share the swing's slot.

**Future boundary (BACKLOG):** if bugs ever *behave* differently when damaged (flee at low HP),
HP becomes sim-state and must move into the deterministic path + state hash.

### 12.1 Movesets wire amendment (2026-06)
OpCode 88 (`MeleeAttack`) gains `move` (input slot name; empty normalizes to `"primary"`).
OpCode 89 (`MeleeResult`) gains `weapon` + the RESOLVED `move` — replay on remote clients is
self-describing (no lookup race against the per-tick `eq`). Validation is per-MOVE
(reach/damage/max_targets/cooldown duration) on the same shared `LastToolTick`; the gate is
move-EXISTENCE via a nil-receiver-safe `GetMove` (bare hand, unknown ids, move-less tools and
unknown move names all reject through one expression), and reach is validated BEFORE the
cooldown stamps. All ledger semantics are unchanged: kills still ride `BUG_REMOVED`, HP display
still rides 89 only.

Related, pre-existing and unchanged by cursor-place: occupant placement reaches clients via the
chunk-scoped, NON-tick-gated `WorldUpdate` (46) and mutates bug-relevant collision
(`blocks_bugs`) mid-sim; equal-tick drift detection is the standing backstop.

### 12.2 Player bug release (2026-06)
Releasing caught bugs (OpCode 29, drag a bug stack onto the cursor → click the world) reuses
the existing machinery end-to-end:
- **Join** (a same-species swarm within `max(species.MergeRadius, swarm.Radius)` of the click —
  the max() matters: fly merge_radius 2.5 < swarm_radius 4.0, so clicking VISIBLE fringe bugs
  must join, not spawn an overlapping duplicate the merge pass would never fuse): the server
  applies reproduceSwarm's exact id math (meters untouched) and emits the SAME
  `SWARM_REPRODUCED` ledger event — deterministic application at the event tick, late-join
  replay included. Ledger = sim-state rule intact.
- **New swarm** (open ground): the continuous-spawning path — spawn template + `SwarmsDirty`;
  live clients spawn deterministic visuals from the SwarmUpdate metadata; the new swarm Thinks
  the SAME tick so its anchoring leg lands after the SwarmUpdate and before the frontier;
  late joiners reconcile via MatchJoin's `SwarmsDirty = true` bootstrap. Shares continuous
  spawning's accepted on-receipt-vs-hash caveat (~sub-1% chance of one self-healing minority
  resync per creation for a lagging client).
- Slot decrement echoes to the releaser only; the client's cursor count rides the standard
  echo interception.
- **Caps (2026-06, closes the old BACKLOG caveat):** releases are gated by §13's
  population cap BEFORE any mutation (visible error, slot untouched — both branches);
  at the swarm-COUNT cap a release can't mint a new swarm and instead FORCE-JOINS the
  nearest same-species swarm at any distance (the player keeps their bugs; the split
  pass rebalances). `spawnSwarmAt` is the single mint path shared with the F8 debug
  spawn (same on-receipt class).

## 13. Ecology population control (2026-06)

An orchard must not exponentially explode the fly population, and "release a jar of
flies into a nearly-full zone" must never crash the match. Three layers:

1. **SOFT — food economics (the real thermostat).** One rotten apple (100 food) funds
   exactly one breed event: at fly `consume_rate` 0.2, a 10-fly swarm drains 2/s —
   feeding 0→100 satiation (20s) = 40 food, breeding the meter (10s) = 20, plus the
   event cost `reproduceFoodCost` = 40. Cost-per-new-fly RISES with population (bigger
   swarms drain faster per capita): growth is inherently self-braking.
2. **MEDIUM — gentle reproduction.** A breed event adds **1-2 flies (randomized)**,
   not doubling. Replay-safe: the count rides the `SWARM_REPRODUCED` event.
3. **HARD — `species_caps.max_population` (the crash guard).** Village: fly 400,
   butterfly 300; **0 = uncapped** (test zones rely on the zero value). Enforced at
   every entity-minting point:
   - `reproduceSwarm`: partial litter at the boundary; at the cap — meters reset, the
     cooldown ARMED (else the meter refills every ~30s and the skip spams), no event,
     no food charge (continuous drain is the honest cost of camping a source).
   - `handleReleaseBugs`: rejected with a visible error before ANY mutation.
   - `checkContinuousSpawning` + the F8 debug spawn skip saturated zones.

**The two ceilings are different kinds of guarantee.** `max_population` is the hard
invariant. `species_caps.max` (swarm COUNT) is spawn BACK-PRESSURE only: a force-join
can push a swarm over MaxSwarmSize, the 600-tick split pass then makes +1 swarm over
the count cap, and the split pair sums past MaxSwarmSize so the merge pass can never
re-fuse it. That overage is bounded (absolute worst case max_population/MinSwarmSize
swarms), decays via catches, and is never refilled by spawning — accepted and
documented rather than papered over.

**Why a release near the limit is safe:** it either joins an existing swarm (bounded
entity count), or is rejected with no mutation. There is no path that mints unbounded
swarms or bugs; a huge orchard plateaus at the soft/hard ceilings instead of crashing
the match.

## 14. Predation: wasps, nests, the centipede, player HP (2026-06)

The first predators. The design's correctness backbone: **clients never replay AI
decisions — they replay AI OUTPUTS.** The deterministic client sim consumes exactly
SWARM_SET_TARGET legs, bug add/remove events, player cells, and the food registry;
satiation, prey targeting, strike cooldowns, brood, and gnaw counters are SERVER-ONLY
state (the forage-duty-cycle convention — server rand at Think time is replay-safe).
The entire slice shipped with **zero new ledger event types**.

### 14.1 The sync invariants this slice added
- **SpeedMult (per-leg speed multipliers — hunt ×1.5, flee ×1.8, surge ×4.8):**
  `swarm.Move` multiplies by it AND the leg-event emission carries
  `BaseSpeed × SpeedMult × dt` — the server position and the client's closed-form leg
  interpolation always agree. It is written ONLY by code that immediately emits a leg
  (never mid-leg: clients capture speed per-leg), and EVERY leg-emitting path writes it
  (the shared forage path writes 1.0 — otherwise a swarm that fled keeps the flee speed
  forever, consistently on both sides and invisible to every harness). Late-join leg
  hydration copies the event's speed verbatim → correct by construction.
- **flies_over_fences acts at BOTH collision sites:** the server leg clamp
  (IsBlockedForSpecies) AND the client per-bug collision (BugCollision/
  IsCellBlockedForBugs) — per-bug positions are hash state. The flag skips the
  OCCUPANT branch ONLY, and it means ALL occupants (walls, houses — there is no roof
  concept; B-future `blocks_flying` adds one). The nil-chunk zone edge still blocks
  everyone — never hand movement code a nil checker. GROUND never blocks bugs (2026-06
  playtest rule: water stops PEOPLE only — bugs fly over it; the old water blocking
  pinned shoreline flies visibly). The server ground branch stays data-driven via
  tiles.json blocks_bugs (currently none set).
- **Movement-class determinism contract** (DartingMovement/CrawlingMovement and all
  future classes): fixed-point math only; CounterRng via bug.RandomInt (tick+purpose
  keyed) only; every cross-tick field round-trips GetState/SetState through
  MovementState (extend MovementState + BugSampleData in Go AND C# lockstep if more
  state is needed); visual effects (trail, smoothing, shadows) never write Position.
  Client movement tuning lives in the PUBLISHED species.json (movement_style etc.) —
  same-build clients parse the same file; publish_entities.py is the drift tripwire.
- **Carrion is hash-bearing food:** edible kill-drops (item def food_value > 0) emit
  ITEM_ROTTED at spawn; lifetime EXPIRY emits FOOD_CONSUMED(0) in removeGroundItem
  (carrion is the first edible item that expires — without it, phantom registry
  entries + a joiner-vs-veteran resync loop); the client hydration fallback reads the
  published item def's food_value (the rotten_ prefix can't cover carrion).

### 14.2 Wasps + nests
Hunt trips: hunt below satiation 30 (legs ×1.5 re-aimed every 10-15 ticks, strike at
3.0 with a 10s cooldown — THE anti-snowball knob — killing the LOWEST alive ids via
the shared melee kill path, +35 satiation/kill) → sated at 100 → HOMING (one brood
carried; 60s timeout drops it) → deposit (satiation → 80; hunting resumes below 30 ≈
a 125s readable rest loiter) → repeat. Nests: brood clamps at 6; +2 wasps per 3 brood
into the resident (the shared growSwarm id-math + SWARM_REPRODUCED, §13 partial-litter
at the cap); a culled resident RE-HATCHES after 2 min at brood-consumed size — ~3
culls = readable dormancy (bounds the culling treadmill, the catch money pump, and
farm net-growth at once). Destroying the nest (axe, aggro-on-damage recalls the
resident from ANY distance) orphans the patrol: never breeds, still hunts. NO
starvation v1: prey can't go extinct (continuous spawning refills), so wasp decline is
always the player's doing — readable. Containment asymmetry: wasps fly over fences
(defense = kill/denest/roofs-later); centipedes respect fences but GNAW WOOD (defense
= stone). Penned prey corners against its own fence — penned flies are MORE vulnerable
to raids, intentionally.

### 14.3 The centipede
Category "individual" — reuses combat/catch/caps/sync wholesale; never merges/splits
(the category guards). "Individual" means GROUND CRAWLER WITH AN ACTION-STATE MACHINE;
swarm sizes are DATA: max_swarm_size is now 3, so a swarm is a small KNOT of 1-3
centipedes sharing one center (one leg stream per knot — the server-traffic lever; the
2026-06 design decision was to KEEP predator AI server-side: the server must stay
authoritative over kills/HP/caps/brood, wire traffic is identical wherever the AI
runs, and multi-bug knots are the real traffic win). Because splits are disabled, a
FULL knot's litter mints a NEW swarm beside the parent in reproduceSwarm (zone
swarm-count capped, arm-the-cooldown skip at the cap). Phase = what it WANTS (the
standard feeding/reproducing lifecycle — the CheckPhaseTransition skip applies ONLY to
nest predators, so the centipede parks at carrion and breeds there); ActionState =
what it's DOING (windup 0.8s zero-leg freeze → SURGE at the launch position + a 0.8
velocity half-lead, clamped, ×4.8 → bite 1.6 with a line-of-sight gate (no
through-fence bites — "stone is the answer" stays true) → recover + 5s cooldown); the
whole knot lunges together (members are center+offset). Gnaw: its own GnawState
damage pool (NOT BreakingState — the owner-reset would let players "repair" by
hitting), 1 dmg/80 ticks → wood HP 2 = 16 visible+audible seconds (the crunch is the
NIGHT tell: audible past the light radius); breaks via breakOccupantAt with no drops;
the cooldown arms only on ABANDONS (successful breaks chain layered walls). Serpentine
wander = heading-constrained short legs (±60°, widening to ±120° once clamped, free
360° after 3 — the dead-end escape). CLIENT: CrawlingMovement = center + a
slowly-wandering per-bug OFFSET (position-based, so members track surge legs exactly;
CounterRng; offset/target/timer round-trip MovementState — per-bug positions are hash
state). Segments are PURE display (one CentipedeTrail per member; parts scaled 0.35 —
the sprites are 2.0 world units raw — spacing 0.5, art-angle offset −90°, the head
rotates along its motion; segment hits map to THAT trail's bug id in the client
sector query — the server validates click-vs-player reach only and needs no change).
Known v1 behaviors: no pathfinding (chews the wall 3 cells from an open gate — the
dumb-relentless fantasy); trap_only = uncatchable until the subdue system.

### 14.4 Player HP
Sim-inert display state (bug AI reads player CELLS, already ledgered): HP 10, sting 1 /
bite 2, per-swarm attack cooldown + a SHARED 1s invuln, +1 HP/30s regen 10s after
damage, faint = refill + respawn (client snaps itself — it is movement-authoritative).
PlayerDamage (94) is PRESENCE-TARGETED to the victim (broadcast would knock back every
client); BugTelegraph (95) is broadcast cosmetics. Audio dedup: THWACK mirrors the
hit-flash gating (optimistic self / !ownEcho remote); the kill POP plays
unconditionally from MeleeResult killed[] (no optimistic kill exists) and NEVER from
BUG_REMOVED application (catches ride it; replay would storm).

### 14.5 Known v1 properties (documented, not bugs)
- No persistence: a destroyed nest RESURRECTS on server restart (true of all broken
  occupants; this one is the headline counterplay, so it's named here).
- Nests come alive on first chunk-touch (the fruit-tree class); wild prey spawns
  zone-wide from match start — accepted asymmetry.
- Releasing caught wasps into another player's farm mints a permanent orphan patrol
  (no starvation) — known grief vector, revisit with starvation.
- Per-SWARM sting cooldown caps any swarm at 0.5 player-DPS regardless of size — right
  for wasps, wrong for future bees (damage-scaling-by-count is a one-formula change).
- The client's IsCellBlockedForBugs checks OCCUPANTS only (ground never blocks bugs);
  the server's ground branch reads tiles.json blocks_bugs. If a tile ever needs to
  block bugs again, set the flag server-side AND restore a matching client check —
  both sites or neither (per-bug positions are hash state).
- Content-update workflow: zone files are read at chunk-touch and never written back —
  regenerate → restart the server → visible on next approach.
