# nakama/modules/world — DETERMINISM RULES (read before editing any `*.go` here)

This package is the **frontier-gated deterministic bug sim**. Editing any `*.go` here is a **determinism
change**. The `frontier-sync` skill is the recipe; **`docs/product/architecture/architecture_swarm_sync.md §0`
is the source of truth** (the guarantee, the invariant, the ledger glossary, the verbatim-relay contract).
Read those — this file is only the always-present checklist.

## The ONE load-bearing invariant
Everything the deterministic sim **READS** must arrive via a **frontier-gated influence event** (zone-wide,
epoch+seq, replayed identically on every client) **OR a join/resync snapshot** — **NEVER** via a chunk-scoped
on-receipt message (`WorldUpdate` 46 / `SwarmUpdate` metadata are **COSMETIC only**). Reading view-scoped /
on-receipt data into the sim is the classic desync (the Phase-1b fence bug; the food-hydration late-join bug).

## The guarantee a change MUST preserve (BOTH)
- **Deterministic steady state** — the frontier-gated ledger makes every client replay the same events at the
  same tick → bit-identical.
- **Resync-recoverable** — a per-tick whole-state hash drift triggers `RequestResync` → `RequestSnapshot`.

## Concrete violations — the checklist (any ONE desyncs)
- [ ] **Float in sim math** — fixed-point (×1000) only; never `float` in anything feeding `ComputeStateHash`.
- [ ] **Nondeterministic iteration** — ranging a Go `map` in the sim or in serialization; **sort keys first**.
- [ ] **Wall-clock / unseeded RNG** — no `time.Now()`, no `rand` outside the seeded `(worldSeed, ids)` stream.
- [ ] **Non-authority or non-idempotent write** — sim mutations are **authority-only + ledgered**
  (**detect-don't-remove**), applied in `seq` order, **idempotent** under replay/re-join, **AT the event tick**.
- [ ] **A hash input with no snapshot carrier** — any NEW client sim-state feeding `ComputeStateHash` (or that
  moves a bug) MUST be reconstructed on a late-joiner (per-bug → the verbatim relay; per-swarm/zone dict → its
  own snapshot section). **"Rides the ledger" is NOT enough** — the 2026-07-14 predation desync passed the
  ledger but not the snapshot.
- [ ] **Wall-clock in the hash** — `ComputeStateHash` is `{x, y, vx, vy, hunt_target, feed_until}` per bug. Keep it pure.

## Hard contract (do NOT re-open)
The per-bug snapshot (`SwarmSnapshotData.Bugs`) is relayed as **opaque bytes** (`json.RawMessage`) — **never
re-declare bug fields in a Go struct** (that silently drops fields → the 2026-07-14 predation desync). Add new
per-bug state to the `BugAgent` snapshot; it round-trips verbatim.

## Recipe (adding a deterministic mechanic) — full version in swarm_sync §0
Classify the state → define the influence event + fields in `messages.go`, mirror in client
`InfluenceManager.ProcessInfluenceEvent` → emit server-side in **ONE** place, stamping `seq` via `NextSeq++`
→ broadcast zone-wide **AND** ride the late-join replay window **AND** (if persistent per-bug) the snapshot →
apply on every client in `seq` order, idempotent, at the event tick → include in `ComputeStateHash` both sides.

## Before you finish — the gates (`test-changes` skill)
`bash tools/run_go_tests.sh` · the headless `sim-determinism` replay · `run_sync_latejoin.sh`
**co-located AND disjoint spawn-apart** (non-vacuous). A determinism change is not done until these pass.
