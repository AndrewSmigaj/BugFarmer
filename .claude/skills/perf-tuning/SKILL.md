---
name: perf-tuning
description: Use when PROFILING or OPTIMIZING the server bug simulation (the sim is slow, a zone can't keep real-time, or before/after a performance change). Covers running a profiled session, reading the cost dashboard (per-species CPU, per-bug, throughput vs the 100ms budget, dark/un-measured time, GC, broadcast bytes), and the safe-optimization discipline — including that any sim-touching optimization is a DETERMINISM change. NOT for ecology BALANCE (that's the ecology-tuning skill, though they share run_config).
---

# Profile & optimize the server bug sim

Measure from data, never guess. The cost profiler is built into the server (`nakama/.../profiler.go`,
gated by the zone `profile` flag, soft/never-hashed → zero cost off, determinism-safe). Charts: `plot_perf.py`.
One-glance view: the dashboard. System of record for the determinism rules: `architecture_swarm_sync.md §0`
+ the `frontier-sync` skill. Execution gates: the `test-changes` skill.

## 1. Run a profiled session
```bash
python3 tools/run_config.py <tag> --zone village_21_B --duration 600
```
~600 s ≈ 8 game-days, `profile:True` injected, restarts nakama, runs the harness, emits PERFSTATS/PERFSYS,
charts everything, files into `tools/_generated/ecology_charts/<zone>/archive/<ts>_<tag>/`, refreshes
`<zone>/current/`, and (re)builds **`<zone>/current/index.html`** — the dashboard. **Open that in a browser**
(it embeds perf + population + interactions + phase + bugmap). For just a re-chart of an existing log:
`python3 tools/plot_perf.py --log <run.log> --tag <tag>` (or `--since 10m` from docker logs).

## 2. Read the perf chart (top-to-bottom)
- **Per-species CPU panels** — stacked `food`/`pred`/`action` µs/day + legs/bugs overlay. Which species + phase dominates?
- **System passes + broadcast bytes** — `merge`/`decay`/`forage`/`nests` + leg/roster KB. Is the cost network, not CPU?
- **THROUGHPUT (the "are we real-time" panel)** — instrumented vs **DARK (un-measured)** ms/tick stacked, total
  ms/tick line vs the **100 ms @ 10 Hz budget**, and **max-tick** (spikes). DARK = whole-tick − Σ(instrumented
  phases). Big dark time means the real hot spot is NOT in a wrapped phase (e.g. `swarm.Move`, lifecycle
  meters, broadcast marshaling) — instrument it before optimizing.
- **PER-BUG over time** — µs/bug per species, **size-normalized**: a big swarm isn't more complex per bug, so
  compare here, not raw CPU, to find genuinely expensive behavior.
- **GC / memory** — per-day GC pause + heap MB + GC count. Go GC pauses can be the real latency spike.
- **cost-per-bug vs swarm size** scatter — fatter swarms cost less per bug (a topology lever).

CSV sidecars (for exact numbers): `tools/_generated/ecology_charts/_data/perf_log_<tag>.csv` (per-species),
`perf_sys_<tag>.csv` (whole-tick + GC + bytes).

## 3. The safe-optimization loop
1. **Measure** — run a profiled baseline; identify the #1 cost from the WHOLE-tick view (incl. dark time),
   not just the biggest wrapped phase.
2. **Understand** — read the actual hot loop + its complexity before changing anything.
3. **Behavior-preserving fix only** — a perf change to the sim must produce BYTE-IDENTICAL results (the sim
   is deterministic + cross-client hashed). E.g. `FindNearbyFood` output is sort-normalized by `(Dist, ID)`,
   so a chunk-bucket spatial index that finds the same in-range SET is identical. Prefer rebuild-from-source
   over incremental — UNLESS a reader observes the source mid-batch (feeding deletes items mid-swarm-loop),
   which forces incremental (Cache-Coherence lens). Worked example (2026-06-22, DONE): `FindNearbyFood` had
   two scans — `ItemsByChunk` (ground-item chunk index, `item_index.go`) and the dominant one,
   `FindNearbyResources` parsing 1024 cells/chunk (a `json.Unmarshal` each) → cached per-chunk anchor index
   (`ChunkData.anchors`, invalidated by `occVersion`). Net cpu_food/call 974→39 us (−96%). The profiler
   named "FindNearbyFood #1" but the per-CALL cost (flat vs item count) revealed the flora cell-sweep, not
   the item scan, was the real cost — measure per-call, not just totals (Accounting-Artifact lens).
4. **Gate it as a determinism change** (it is one): an **equivalence test** (new path == brute-force for
   random states) + `go test ./world/` + `tools/sim-determinism` + a fresh-match `run_sync_latejoin`
   co-located AND disjoint = `SYNC: IDENTICAL`. See `frontier-sync` + `complex-change-review.md`.
5. **Re-profile** — same command, new tag; confirm the measured drop; compare dashboards.
6. **Log it** — before/after numbers in `docs/product/ecology/ecology_tuning_log.md` (or a perf note).

## 4. Gotchas / facts
- Pure instrumentation (timing, `ReadMemStats`) is observation-only + never hashed → it cannot change the
  sim. Adding a timer needs only `sim-determinism` + a quick sync check to confirm.
- `tick_count` (not DayLengthTicks=8400) is the divisor for avg µs/tick — the day-rollover tick lands in the
  next day's bucket by ~1 (negligible).
- GC stats are process-global; the rig runs one match, so they're representative, not per-zone.
- Optional **scaling sweep**: profile the same zone at a few bug populations to expose O(n²) cliffs and prove
  an optimization pays off before building it.

## 5. Maintain this skill
If the run command, a metric, the dashboard layout, or an output path changes, update this file + the
`plot_perf.py`/`profiler.go` docstrings.
