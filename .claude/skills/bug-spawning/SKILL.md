---
name: bug-spawning
description: Use when a zone has the WRONG number of bugs — none spawning, too many, stuck in formation, not refilling, or a config change "not taking effect". Explains the four ways a zone gets a bug population (restore / initial spawn / director reseed / continuous immigration), which fires when, the walkability + persistence gotchas that make it look broken, how to populate/reset/persist a zone's bugs, and how to verify headlessly. Server-side only (the Go ecology sim); not the client render.
---

# Bug spawning — how a zone gets its bugs

The single source of truth is the Go code under `nakama/modules/world/`. This skill is the map so you don't
re-derive it (badly) every time. **Verify with a headless Go test, never by eyeballing the client.**

## The ONE creation primitive

Every bug population, no matter the trigger, is built by **`spawnSwarmAt(state, species, count, x, y, chunkSize)`**
(`handlers_bugs.go:91`): it makes the `SwarmState`, registers it in `state.Swarms`, and emits the deterministic
`SWARM_SPAWNED` ledger event (so every client + late-joiner creates it at the same tick). It does **NOT**
walkability-check — it places at the point you give it.

## The four triggers (and when each fires)

At `MatchInit` (`match.go:317`): `if !restoreSwarms(...) { spawnInitialSwarms(...) }` — **restore if there's a
save, otherwise initial spawn.** Then, in the tick loop, the director + continuous spawner run periodically.

| Trigger | Where | Fires when | Fills how much |
|---|---|---|---|
| **Restore** | `zone_persist.go:119` | a save exists for the zone AND `ephemeral_swarms` is off | the whole saved population, instantly (direct `spawnSwarmAt`) |
| **Initial spawn** | `spawnInitialSwarms` `match.go:1642` | no save was restored | `cap.Initial` swarms per species, instantly |
| **Director reseed** | `processEcologyDirector` `ecology_director.go:52` | every `DirectorIntervalTicks`, when `pop < min_population` | **1 swarm per pass** — an anti-extinction *floor*, NOT a populate mechanism. Slow. |
| **Continuous immigration** | `checkContinuousSpawning` `match.go:~1919` | every 100 ticks, when `now ≥ SpeciesNextSpawn` | 1 swarm per `spawn_interval`. `spawn_interval: 999999` = effectively off. |

**To populate a zone, you use `initial` (or restore).** The director/continuous are slow trickles — do NOT
rely on them to fill a fresh zone; a short visit won't see them.

## Gotcha #1 — the walkability/chunk-load trap (fixed 2026-06-25, keep it this way)

Spawn picks a point in a `spawn_area` and rejects "blocked" cells. The check must use **`IsBlockedForSpawn`**
(`state.go`), which reads the **authored map** — loading the chunk from disk via `chunkForCollision` when it
isn't in memory.

WHY this matters: `state.Chunks` is the **lazily-loaded** cache (chunks load only when a player subscribes).
At `MatchInit` it is **EMPTY**. The per-tick `IsBlocked` treats a missing chunk as *blocked*, so if spawn used
it, **every cell reads blocked and `spawnInitialSwarms` places ZERO bugs** ("Seeded world with 0 swarms").
That was the long-standing bug; the symptom was "fresh zones are empty, only saved ones have bugs." If you add
a new spawn path, use `IsBlockedForSpawn`, not `IsBlocked`.

## Gotcha #2 — a stale save masks everything (this WILL confuse you)

A persistent zone restores its **saved** population and **skips initial spawn** (you'll see
`restored N swarm(s) from save (skipping initial spawn)` in the log). So:
- If you change `swarm_size`/`initial`/counts in `zone.json` and "nothing changes," it's because the zone is
  **restoring an old save** made under the *previous* config. Your new config is never reached.
- **Fix:** make it ephemeral (below) or wipe the save (below) so a fresh population is built from the new config.

Read the server log to know which path ran — don't guess:
```bash
docker logs bugfarmer-nakama 2>&1 | grep -iE "restored .* swarm|Seeded world with"
```
`Seeded world with N swarms` = initial spawn ran (N should be > 0). `restored N swarm(s)` = it loaded a save.

## Persistence: save / don't-save / reset

Populations save to Nakama storage (Postgres — **survives server reloads**) on player-leave, and restore on
entry. The toggle is one top-level `zone.json` field:

- **`"ephemeral_swarms": true`** → never restore (+ don't save/restore transient ground items). The zone
  **always starts fresh from `bug_spawning.initial`**. This is what test/combat *labs* want. (`zone.go:106`,
  gated in `zone_persist.go:123/350/504`.)
- **omit it / `false`** (default) → persistent world: saves on leave, restores on entry, survives reloads.
- **Reset a persistent zone** = delete its saved record so the next entry rebuilds from config
  (`deleteZoneRecord`, key `zoneSwarmKey(ZoneStateKey(zoneID,""))`). After the 2026-06-25 fix, that yields a
  fresh *populated* zone (before it, a wipe came back empty — which is why reset felt broken).

`ephemeral_swarms` only gates the bug population + transient ground items. Authored content + farm deltas
persist regardless.

## Recipe: make a zone spawn the bugs you want

In `zone.json` `bug_spawning` (or the zonegen scene's `Z.bug_spawning`):
1. A `spawn_area` over **walkable ground** (open floor; type `circle` {cx,cy,radius} or `zone`).
2. `species_caps[species].initial` = **the number you want at match start** (this is the real populate knob).
3. `swarm_size`: bugs per swarm. **`1` = each bug is its own swarm** = its own AI/center (centipedes hunt
   independently); higher = a "knot" sharing one center that moves/attacks as a unit.
4. `min_population` = the director's refill floor (tops up *slowly* after kills). For an instant-full,
   self-refilling lab: `initial == min_population`.
5. `max` = swarm-count cap (must be ≥ the swarm count you're targeting). `max_population` = hard bug ceiling.
6. `static: false` to let the director/continuous run; `true` freezes them (only `initial`, no refill).
7. For a lab, add `"ephemeral_swarms": true` so it's fresh every entry.

Then **restart nakama** (or just re-enter a fresh match — zone.json is read at match creation from the
bind-mounted `nakama/data`).

## Verify HEADLESSLY (don't trust the client, don't guess)

The real proof that spawning works is a Go test that runs the actual server spawn against real zone files —
see `nakama/modules/world/initial_spawn_test.go` (`TestInitialSpawnPlacesBugsWithEmptyChunkCache`). It builds a
`WorldState` with an **empty** `state.Chunks` (the MatchInit condition), runs `spawnInitialSwarms`, and asserts
bugs land. Run it (the builder image has the toolchain + cached deps; mount the repo so it sees the zone files):

```bash
docker run --rm -v "$(pwd)/nakama:/src" -w /src/modules bugfarmer-builder \
  go test ./world/ -run TestInitialSpawnPlacesBugsWithEmptyChunkCache -v
# and the whole package for regressions:
docker run --rm -v "$(pwd)/nakama:/src" -w /src/modules bugfarmer-builder go test ./world/
```
(The test `os.Chdir("../..")` to the `nakama/` dir so `LoadChunk`'s `data/zones/...` resolves. `newTestState`
in `swarm_population_test.go` is the state builder; it omits `SpeciesNextSpawn`, so set it.)

After any server code change: rebuild + redeploy the plugin per the **`run-backend`** skill, then read the log
to confirm `Seeded world with N swarms` has N>0 on entry. For determinism-touching spawn changes, also run the
**`test-changes`** gates.

## Debugging checklist (in order)

1. `grep -iE "restored .* swarm|Seeded world with"` the nakama log → which path ran, and N.
2. If `Seeded world with 0` → spawn area is over blocked/missing terrain, or `initial` is 0, or (pre-fix) the
   walkability bug. Check the spawn_area cells are walkable in the authored chunk.
3. If `restored N` but the count/behavior is from an OLD config → stale save (Gotcha #2): set `ephemeral` or
   wipe the save.
4. If bugs appear but "all move/attack as one" → `swarm_size > 1` (a knot shares one AI). Set `swarm_size: 1`.
5. Don't declare a root cause off one log line. Trace to the actual function and, if you can, prove it with the
   Go test above before changing code.
