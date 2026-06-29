# Investigation: #10 moving the compost container broke it (can't load compost)
_status: READY TO IMPLEMENT (sim-touching — needs the determinism gate) · investigated 2026-06-28 · investigate-only_

## Debrief (read me first)
- **TL;DR:** A compost bin's `StationState` is created **only** by the chunk-load eager scan
  `initStationsInChunk` (`handlers_farming.go:901`). When you **move** a compost (break + re-place into an
  already-loaded chunk), the runtime place handler creates the occupant but **no StationState**, and
  `handleStationDeposit` requires a **pre-existing** one (`:956-961` → "No station there") with **no
  find-or-create**. So the moved bin silently can't accept deposits = "could no longer load compost."
- **Why only compost:** craft stations + containers lazily find-or-create on first use
  (`resolveCraftStation` `craft_stations.go:64`, `resolveContainer`). The deterministic **station** path
  (compost/breeding) is the one place that was never given that fallback.
- **Fix:** give the station path the same lazy find-or-create (build the `StationState` from the occupant's
  `world.station` block at (gx,gy) when `state.Stations[key]` is nil), in `handleStationDeposit` and the
  station-open path. ~15 lines mirroring `resolveCraftStation`.
- **Determinism:** compost is **sim-feeding** (`providers:[food,breeding]`). The fix is server-side state
  creation; its food contribution still rides the existing `processStations → AddFoodEvent` (frontier-gated),
  so risk is low — but it IS a sim-touching station → run the `sim-determinism` + sync-harness gate on the fix.
- **Certainty:** root cause **95%** · fix-shape **90%**. **Needs your decision:** none. **Status:** `READY`.

## 1. Issue
> "moving the compost container broke it, could no longer load compost"

## 2. Root cause (verified, the chain)
1. compost_bin: `interaction_type:"station"`, `world.station{accepts[], capacity, process_ticks,
   providers:[food,breeding]}` — the deterministic breeding/food station (routes to the `_station` handler,
   NOT the container/craft panel).
2. Its `StationState` is created only by `initStationsInChunk` (`handlers_farming.go:901`), which runs as the
   **chunk-load** init scan. (`state.Stations[key]`, `key = StationKey(gx,gy)`.)
3. The runtime **place** handler (`handlers_world.go` ~225) does `chunk.SetOccupant(...)` and footprint cells
   but **never creates a StationState** and never re-runs the init scan (verified: no `Stations[` / `initStation`
   in the place handler). The chunk is already loaded, so the eager scan won't fire again.
4. `handleStationDeposit` (`handlers_farming.go:956-961`): `st := state.Stations[key]; if st == nil { error
   "No station there"; return }` — **requires** an existing StationState; no find-or-create.
   ⇒ moved/runtime-placed compost has no StationState → every deposit returns "No station there."

## 3. Ruled out
- Click resolution (the shared OverlapPoint issue) — not it: the deposit reaches the server (you'd otherwise
  get nothing); the server explicitly rejects with "No station there".
- State keyed wrong / orphaned-on-move — the key is fine; the problem is the new cell's state was never created.

## 4. Recommendation
Add lazy find-or-create to the **station** path, mirroring `resolveCraftStation` (`craft_stations.go:64`):
when `state.Stations[StationKey(gx,gy)]` is nil, look up the anchored occupant; if it has `world.station`,
create `&entities.StationState{Key, EntityID, GridX, GridY}` and store it. Call this from `handleStationDeposit`
(and the station right-click/open). Then gate the change with Go tests + `tools/sim-determinism` + the
sync-harness (sim-feeding station). Optional belt-and-suspenders: also init a station's state in the place
handler when the placed occupant has `world.station`.
