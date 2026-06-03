BugFarmer Zone Swarm Sync — Authoritative Client Architecture + Deterministic Followers

Purpose: fresh debugging session. Not a rebuild. Lock semantics, stop kneejerk changes, find the true fault.

1) Architecture (Locked)
1.1 Roles

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

If it triggers, logs immediately show whether it’s epoch mismatch, gap in seq, or tick contract mismatch.