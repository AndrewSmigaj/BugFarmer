# Zone persistence — the WorldSave document

> System of record for HOW A ZONE SURVIVES A SERVER RESTART (Terraria-style hosting: a player runs
> the server; everything persists). Shipped 2026-07-05 (§P). Code: `nakama/modules/world/
> world_save.go` (the system) + `persist_classes.go` (the enforcement) + `zone_persist.go` (the
> dying legacy importer). Character/player state is a SEPARATE user-owned system
> (`character_persist.go`) and is untouched by all of this.

## The principle
**The world saves as-is and time continues.** One `WorldSave` JSON document per zone (storage key
`<zone>:world`), marshaled whole, restored whole, and the WORLD CLOCK (`Tick`) persists with it —
so every tick-stamp anywhere in the state (tree gates, rehatch timers, smoke stamps, action
cooldowns) stays valid across the restart with **no clamps, no relinking, no lossy rebuilds**.
Those compensations existed only because the old system reset the clock and re-minted swarm
identities; both roots are gone.

## What's in the document
`Tick` (+ `LastRolloverDay`), the sky (`DayOffsetTicks`, weather kind/until/rain-at/drought),
`GroundItemSeq` (id counter — a reset counter silently overwrote restored items), `CellEdits`
(the global-coordinate SEMANTIC DIFF of every loaded chunk vs the authored zone — authored-zone
updates stay compatible with old saves), the `Gnaw` map (half-chewed fences stay half-chewed),
**full-fidelity `Swarms`** (whole `SwarmState` structs — json tags ARE the save format; identities
kept, so `NestState.ResidentSwarmID` stays valid), and every sidecar registry (crops, trees,
stations, containers, craft stations, nests, forage pools, host plants, broods, ground items).
Two swarm fields are refreshed from the live species def at load (`Radius`, `WanderRad` — a
rebalance must reach saved swarms); the player-ref field `DefendTargetID` holds a stable userID and
self-heals (`WindupTargetID` was removed with the centipede combat-brain move to the client, 2026-07-18).

## Restore (eager, at MatchInit, before any client joins)
One order, one function (`restoreWorldSave`): **(1)** the clock + scalars (`LastZoneSaveTick` :=
the restored Tick, else one spurious autosave fires), **(2)** the registries, **(3)** the swarms
(+ `SwarmsBySpecies` rebuild), **(4)** every chunk referenced by a CellEdit: `LoadChunk` → apply
edits → the five init scans (all skip-if-present; tree randomness is position-hashed, so
load-order-independent). Untouched chunks keep lazy-loading on subscribe, where the same scans
start them from scratch. The zone-wide collision map sees saved fences because edited chunks are
already in memory (`chunkForCollision` is in-memory-first).

## Write (three triggers, one guard)
Empty-transition (async), 10-minute autosave (async), MatchTerminate (synchronous). The snapshot
is marshaled ON the match goroutine (frozen bytes; async-safe). **`WorldSave.Tick` doubles as the
generation stamp**: `writeWorldSave` refuses to replace a stored document with a HIGHER tick —
which kills the real race (a slow async empty-save landing after a newer terminate-save and
rolling the zone back). `EphemeralSwarms` test zones skip ONLY the population (swarms + ground
items) both ways; `tools/ecology/run_config.py` additionally WIPES the zone's storage before every
tuning run so runs stay comparable.

## The enforcement — persist_classes.go
Every `WorldState` field is classified exactly once: **WORLD-STATE** (in the document, note says
which field) | **PER-RUN** (presences, the sync ledger — per-run BY the sync architecture —, RNG,
caches, telemetry) | **CONFIG** (reloaded from data files). A reflection test
(`TestPersistClassificationComplete`) fails BY NAME on any unclassified new field — "forgot to
persist X" cannot happen silently. The table doubles as the field-by-field documentation.

## Determinism boundary
Nothing here enters the bug-sim hash. The ledger/epoch/seq are PER-RUN by design (determinism is
within-run); a restart starts a fresh sync epoch over the restored world, exactly like a fresh
boot over an authored zone. Restore happens entirely before the first join.

## Migration (dying code)
Old multi-record saves (`:meta` + `:<cx>_<cy>` + `:swarms`) are imported ONCE at boot when no
document exists (`importLegacySave` — the OLD clamps live only inside it, because legacy stamps
were written against a clock that reset), and the legacy records are DELETED on the first
successful document write. New-doc-wins forever after. The importer dies a release later.

## Gates that hold it
`world_save_test.go`: classification completeness, full round-trip deep-equality, resume-clock,
GroundItemSeq no-collision, ephemeral skip, generation guard, legacy decode+clamps, SwarmState
json tags. End-to-end: `tools/harness_persist_test.sh` (build a farm headless → restart → assert
restored, incl. a [6/6] direct Postgres inspection of the stored document), plus a seeded
legacy-format migration run (imported → carried → legacy rows deleted).
