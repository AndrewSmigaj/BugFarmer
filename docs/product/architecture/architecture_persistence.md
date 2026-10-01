# Zone persistence — the WorldSave document

> System of record for HOW A ZONE SURVIVES A SERVER RESTART (Terraria-style hosting: a player runs
> the server; everything persists). Shipped 2026-07-05 (§P). Code: `nakama/modules/world/
> world_save.go` (the system) + `persist_classes.go` (the enforcement) + `zone_persist.go` (the
> dying legacy importer). Characters are user-owned documents (`character_persist.go`); since 2026-09-30 a
> zone's clean-stop save writes them together with the world (below), and the rest of the
> saves-and-backups work (D73) is bringing every save to that shape.

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
generation stamp**: every world write first passes `worldSaveWriteAllowed`, which refuses to replace a stored
document with a HIGHER tick (a slow async empty-save landing after a newer terminate-save would roll the zone
back) or one this build can't use. `EphemeralSwarms` test zones skip ONLY the population (swarms + ground
items) both ways; `tools/ecology/run_config.py` additionally WIPES the zone's storage before every tuning run so
runs stay comparable — with the server STOPPED (stop → wipe → start), since a clean stop now saves the zone.

**Save cost (2026-09-30).** The document is built on the match goroutine, so it must stay cheap now that zones save
every minute. Building it diffs every loaded chunk against its authored file: `occCellEqual` first compares the
cells' bytes (a chunk loaded from its file keeps each cell's exact bytes, so an untouched cell matches without
decoding — the old path ran ~65,000 JSON decodes per save of a 64-chunk zone), and the authored files are read once
per match and kept (`WorldState.BaseChunks` via `baseChunk`, per-run, read-only). Measured on a fully loaded
village_21_B with 251 edits (`world_save_cost_test.go`): ~110 ms per save before, ~1.1 ms after — except the first
save after a zone starts, which fills the cache (~110 ms once). The byte fast path agreed with the full comparison on
all 140,600 cell pairs tested.

**The clean stop (2026-09-30).** `MatchTerminate` → `writeFinalSave` writes the zone's document AND the character
of every player still in it (`characterSaveWrite`, the same shape the leave and sleep saves use) in **one**
`StorageWrite` — Nakama runs a multi-object write as one transaction, so the world and the characters land
together or not at all. If the guard refuses the world document, nothing is written. `MatchTerminate` then
returns **nil**: Nakama stops the match at once, whereas a live state would keep the match running unsaved through
the grace period (Nakama 3.35 `match_handler.go` `QueueTerminate`). The save runs on a context of its own,
bounded by the grace period less a second (`terminateSaveTimeout`), because Nakama cancels the match's context
when it stops the match. **This needs shutdown time:** `nakama/data/local.yml` `shutdown_grace_sec: 15` (Nakama's
default, 0, halts every match with no MatchTerminate — so before this date no zone was ever saved on shutdown)
and `docker-compose.yml` `stop_grace_period: 30s`, which applies when the container is (re)created; check it with
`docker inspect -f '{{.Config.StopTimeout}}' bugfarmer-nakama` → 30. A crash (or turning off the PC / WSL)
still skips this save.

## Save formats — upgrade old, refuse newer, never overwrite what can't be read (2026-09-26)
Every stored document carries `version` — the format of the build that wrote it (`worldSaveVersion`,
`characterSaveVersion`). `save_versions.go` (`upgradeSaveJSON`) decides on load:
- **same format** → read as-is (byte-identical);
- **older** → upgraded one step at a time on the raw JSON (`worldSaveSteps` / `characterSaveSteps`: step `v`
  turns a version-v document into v+1, so a step can reshape fields today's structs no longer know). The
  untouched original is kept first — a zone at `<zone>:world:v<N>` in `zone_state`, a character at
  `<charID>:v<N>` in `character_backup` (a separate collection so it never appears on the select screen). The
  first backup of a version is never replaced. If the backup can't be written, the zone does not start;
- **newer** (a downgrade), **unreadable**, or **storage unreachable** → the zone does NOT start (`MatchInit`
  returns no state → `world_enter` answers `MATCH_CREATE_FAILED`; the log says why) and the document is left
  untouched; `writeWorldSave` also refuses to write over a newer or unreadable document. A character that
  can't be used refuses the join (`character load failed`) and is left off the select screen.

This replaced "any other version = treat the save as missing", where the zone then started empty and the next
autosave wrote over the player's world; a storage read error at start-up did the same. **Changing a save
shape:** bump the version and add the step for the OLD version; never edit an existing step.

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
json tags. `storage_fake_test.go`: `memStorage`, the faithful in-memory stand-in for Nakama storage the save tests run
on (Nakama 3.35's version rules, all-or-nothing batches, all-users listing in pages, deleted accounts refused,
injected failures), with tests pinning each rule. `save_versions_test.go`: the upgrade chain, refusing newer /
unreadable saves at start-up and on write, upgrading an older save with its original backed up once, and
the same for characters. `world_save_cost_test.go`: the byte fast path agrees with the full cell comparison on every real village_21_B cell,
and the save-build timing (run with -v). `final_save_test.go`: the clean stop writes the world and the present characters in ONE
write and returns nil, and writes nothing over an unusable save. End-to-end: `tools/harness_persist_test.sh`
(stop → wipe → start; build a farm headless → clean stop → start → assert restored; a direct Postgres inspection of
the stored document; and proof the clean stop itself wrote the save — its `saved_at` is at or after the stop),
plus a seeded legacy-format migration run (imported → carried → legacy rows deleted). **The saves crash test,**
`tools/harness_crash_test.sh`: a scripted player with a real character in the test zones `persist_a` ↔ `persist_b`,
checking fences in the world + in the bag = 50 through a clean stop, a `docker kill`, a zone crossing (with
`persist_a`'s `debug_leave_delay_ms` holding back the departure save so the race happens every time) and a reconnect.
Recorded on 2026-09-30, before the save queue and the character registry: graceful PASS (50); crash FAIL — 45, five
fences lost (the world last saved on leaving, the character on sleeping); cross FAIL — the bag arrived with 50 after
leaving with 45 (duplicated); reconnect FAIL — a second copy of the game saw the stored 50, not the live 48.
