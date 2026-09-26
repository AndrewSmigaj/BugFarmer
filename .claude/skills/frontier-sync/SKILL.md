---
name: frontier-sync
description: Use when adding or changing anything the deterministic BUG SIMULATION reads or that must stay in sync across players (a new ledger/influence event, a new bug behavior input, swarm spawn/merge/split/reproduce, food/collision/predation, late-join snapshot fields). The recipe for wiring a new deterministic mechanic so it is bit-identical across clients AND resync-recoverable, plus the invariants that break sync if violated. Does NOT cover display-only/cosmetic changes (those don't touch the sim) — for those, no ledger event is needed.
---

# Wire a new deterministic mechanic (frontier-sync)

How to add something the bug sim reads so it stays bit-identical across all players. The system of record is
[`docs/product/architecture/architecture_swarm_sync.md`](../../../docs/product/architecture/architecture_swarm_sync.md) — read its
**§0 as-built quick reference** first. Verify with the **`test-changes`** skill (the execution gates). Review
the design with [`.claude/lenses.md`](../../lenses.md) and [`.claude/complex-change-review.md`](../../complex-change-review.md)
(the Determinism / Timing / Data-Contract lenses + STAGE-2 DESIGN cells).

## The one rule that, broken, desyncs players
Everything the deterministic bug sim **reads** must arrive via a **frontier-gated influence event**
(zone-wide, epoch+seq, replayed identically at the same tick on every client) **OR a join/resync snapshot** —
**NEVER** a chunk-scoped on-receipt message (`WorldUpdate` 46 / `SwarmUpdate` metadata = cosmetic only). The
sole sanctioned exception is join-time bootstrap hydration the snapshot+events immediately supersede
(`HydrateFood`). If two clients can read different values for the same sim input, their bugs diverge.

## Classify first — does this even need a ledger event?
- **Ledgered sim-input** (bugs read it → affects positions/targets/alive): YES, follow the recipe.
- **Display-only** (HP bar, sound, cosmetic): NO ledger event — it must NOT enter `ComputeStateHash`.
- **Server-only** (satiation, cooldowns, brood counts the server owns): stays server-side; only its
  *observable outputs* (a kill, a spawn) ride the ledger.
- **Authority-only** (a decision only the authority can make, e.g. which individual bug a predator strikes):
  the authority detects and REPORTS; the effect is applied to everyone via a relayed ledger event
  (detect-don't-remove — see the predation strike, architecture_swarm_sync §14).

## Recipe (for a ledgered sim-input)
1. **Define the event** in `nakama/modules/world/messages.go` (the influence-event const + any new
   `InfluenceEvent` fields, `omitempty`). Mirror it in the client `BugFarmerClient/.../Networking/BugMessages.cs`
   (`InfluenceEvent` fields) + `BugFarmerClient/.../Bugs/InfluenceManager.cs` (`ProcessInfluenceEvent` case).
2. **Emit it server-side in ONE place** (centralize — don't scatter N copies; e.g. placement funnels through
   `broadcastWorldUpdate`). Stamp `seq` via the zone's `NextSeq++` (use the `AddInfluenceEvent` family in
   `state.go`); it lands in `PendingInfluence` → OpCode 71, frontier-gated.
3. **Cover late-join** — the failure that has bitten most often. The event must ride the replay window (auto if
   seq > the snapshot's last seq, within the prune window). BUT if you add **persistent CLIENT sim-state** a
   joiner must have BEFORE replay (a per-bug field, or a new `InfluenceManager` dict), the in-window log is NOT
   enough — it must ride the SNAPSHOT:
   - **Per-bug state** (a new `BugAgent`/`MovementState` field): capture it in `CreateBugSampleData` + apply in
     `ApplySnapshot`, and you're DONE — the server relays the per-bug snapshot VERBATIM (`SwarmSnapshotData.Bugs`
     is `json.RawMessage`; **never re-declare bug fields in a Go struct** — that silently drops them, the S1/S2
     predation desync, 2026-07-14).
   - **Per-swarm/zone state** (a new dict): mirror the food registry EXACTLY — `Export…`/`Clear…`/`Hydrate…` on
     the client + a relayed snapshot section + **clear-then-hydrate before replay** in `HandleLateJoinSnapshot`
     (see `_food` and `_swarmStrikes`).
   The determinism contract is `ComputeStateHash` (`{x,y,vx,vy,hunt_target,feed_until}`); every input to it must
   reconstruct on a late-joiner. VERIFY with a **NON-VACUOUS** `run_sync_latejoin` that actually exercises the
   new behavior (a run where it never fires proves nothing).
4. **Apply on every client in seq order, idempotent, AT the event tick** (`ProcessEventsForTick` runs at
   `evt.tick` in both live and replay). Idempotency matters: a re-join/replay may re-apply it.
5. **Determinism hygiene** (the invariants that bite):
   - fixed-point, not float; `FixedPoint operator* = a*b/1000` (radius² landmine).
   - any loop that draws `state.Rng` / mints ids / grabs a depletable resource → `sortedStringKeys` (Go) or
     ordered keys (C#), never raw map order.
   - zone-wide sim reads zone-COMPLETE data (server chunks load lazily — a zone-complete scan reads the full
     grid from disk, not `state.Chunks`).
   - entities created in the snapshot-lag window are minted by REPLAY at evt.tick, not prespawned from live
     metadata count (the #127 class).
6. **Hash it**: include the new sim output in `ComputeStateHash` on BOTH server and client, or the harness
   can't see its divergence.
7. **Verify** (test-changes skill): `go test ./world/`; `tools/sim-determinism`; fresh-match
   `FRESH=1 tools/run_sync_latejoin.sh` co-located AND `SPAWN_A=126,2 SPAWN_B=126,253` disjoint spawn-apart
   → must be `SYNC: IDENTICAL` (0 bug + 0 hash divergence). The diff is `tools/netcode/sync_diff.py` (unit-tested by
   `tools/netcode/test_sync_diff.py`).

## Worked reference patterns (copy these shapes)
- **New zone-wide input + readiness gate** — `OCCUPANT_BLOCKS_BUGS` + `OpCodeZoneCollisionMap` (Phase 1b):
  static complete set on join (built from ALL chunks, disk-loaded) + dynamic frontier-gated toggles; the
  sim gates on the map being ready. (architecture_swarm_sync §12.3)
- **Authority-detect → relay** — the predation strike: the authority picks the individual victim from its
  bit-identical positions and reports it; the kill applies to everyone via `BUG_REMOVED`. (§14)
- **Event-sourced + snapshot-hydrated registry** — the food registry (`ITEM_ROTTED`/`FOOD_CONSUMED` +
  `HydrateFoodExact`). The zone collision map and swarm legs follow the same "live registry is the reliable
  late-join source" shape.

## Common ways it goes wrong (from real misses)
- Reading view-scoped/on-receipt data into the sim (Phase 1b fence bug).
- Prespawning window-created entities from metadata instead of letting replay mint them (#127).
- A test that doesn't actually exercise it, or whose tool is itself wrong (the harness leg/bug-id collision)
  — re-fire the STAGE-4 VERIFY cells in complex-change-review.md before trusting green.
