---
name: test-changes
description: Use when verifying ANY change to the Bug Farmer server, bug simulation, or client — Go unit tests, the headless sync-harness (protocol/ledger, scripted-player scenarios, login/logoff reconnect, cross-zone, persistence/restart), the determinism / "are all players in sync" checks (server drift detector + client tick-hash trace diff), and the Unity Editor pass. Use it to test each implementation task and to confirm all players see the same world. Also documents how to persist new tests durably instead of throwaway scripts.
---

# Test a change

How to verify Bug Farmer changes. Most of this runs **headless (no Unity)**. Pick the section(s) that match
what you changed (see §5), then add a durable test per §0.

## 0. GOLDEN RULE — tests are durable artifacts, not throwaway scripts
The recurring failure: run a one-off `/tmp` script, narrate the result, never write it down → the next
session loses it and re-derives (badly). **Don't.** Every check you write goes in the repo AND gets a line
here:
- Server logic → a Go `*_test.go` in `nakama/modules/world/`.
- A player "does things + assert" flow → a sync-harness `IScenario` in `tools/sync-harness/Scenarios.cs`
  (register it in `Scenarios.Get`; send API = `Actions.cs`; received-state + asserts = `WorldModel.cs`).
- A multi-step procedure → a committed `tools/*.sh` / `tools/*.py`.

If you add a test, **also add its one-liner to §1–§4 below** so it's discoverable.

## 1. Go server unit tests
```bash
bash tools/run_go_tests.sh        # go test ./world/ -count=1 -v inside the builder image (live source)
```
Suite: `centipede combat predation nest fruit_tree release swarm_population player_hp equip world_env
host_plant brood forage_pool ecology_director predator_starvation` (`*_test.go`).
Run after ANY server-logic change. Add a `*_test.go` for new sim/economy logic (mirror `predation_test.go`).

## 2. Headless sync-harness (`tools/sync-harness/`, real Nakama .NET client, no Unity)
Server must be up (`docker compose up -d`). `DOTNET=$(command -v dotnet || echo ~/.dotnet/dotnet)`.
```bash
cd tools/sync-harness
dotnet run -- --zone bug_lab --duration 15            # OBSERVE: ticks advance, no reception gap (exit 0 = ok)
dotnet run -- --zone sim_test --duration 70 --reconnect   # LOGIN/LOGOFF: enter→leave→re-enter, logs post-reconnect seqs
dotnet run -- --scenario farm-build  --zone sim_test  # SCRIPTED PLAYER: does things (till/plant/place/…)
dotnet run -- --scenario farm-verify --zone sim_test  # rejoin + ASSERT it restored (exit 1 on fail)
dotnet run -- --scenario crosszone   --zone village_21    # walk an edge → assert entry on the neighbor
```
Registered scenarios live in `Scenarios.cs`; add new ones there (see §0). The harness is a **protocol
observer + scripted player** — it verifies the deterministic INPUTS (event ledger: in-order seqs, no gaps, no
stale-high) and server behavior; it does NOT itself compute bug-position hashes (see §3).
```bash
bash tools/harness_persist_test.sh   # PERSISTENCE regression: build farm → restart server → rejoin → assert (PASS/FAIL)
```

## 2.5. Ecology population tuning — the 6× `bug_lab` chart loop (THE living-ecology rig)
The one you run for ANY bug-ecology/balance change (predator survival, oscillation, Director bands, food
regen). `bug_lab` runs the sim **6× wall-clock** (`call_rate:60`) so a many-game-day run finishes in
minutes; the chart x-axis is GAME-TIME (`tick/SimRate`) so 6× and normal-speed runs plot identically.
The harness records a per-species population series and writes `fly_counts.csv` to the **temp dir at run
END** (not live). Full loop:
```bash
python3 tools/make_bug_lab.py                                   # (re)author the lab zone (pens + predator-prey arenas)
docker compose build builder && docker compose up -d --force-recreate nakama   # server-CODE change: recompile plugin
#   …OR just `docker compose restart nakama` if you ONLY edited bug_lab DATA (zone.json is read at startup)
rm -f /tmp/fly_counts.csv
~/.dotnet/dotnet run --project tools/sync-harness -- --zone bug_lab --duration 150 --tag eco   # see below: 150s ≈ 8.5 game-days
python3 tools/plot_fly_counts.py /tmp/fly_counts.csv <chart_name> "<Title>"   # → tools/_generated/ecology_charts/<chart_name>.png
python3 tools/plot_interactions.py --tag <chart_name> --since 10m            # the "WHY": births-by-source / deaths-by-cause
```
- **WHY a population is off-target (interaction log):** the server emits one `ECOSTATS day=N sp=… pop=…
  b_*=… d_*=… avg_sat=…` line per species + `PREDLOG …` per predator-prey pair at each game-day rollover
  (soft state, never hashed — `ecology_stats.go`). `plot_interactions.py` greps `docker compose logs
  nakama` (use `--since` to bound the window; it keeps only the last run), writes
  `interaction_log_<tag>.csv` + `predation_log_<tag>.csv`, and charts births-up / deaths-down per species
  with pop+avg_sat overlaid. Read it to diagnose: below target because births are food-limited (low
  brood/reproduce) vs. dying to predation/starvation; **self-maintenance = drive `b_reseed`→0** (a
  population held up by the red `reseed` bars is propped by the Director, not self-sustaining = a FAIL).
- **SPEED:** bug_lab sets `sim_batch: 8` (8 sim-ticks/Nakama call) on top of `call_rate: 60` → **48×
  real-time**. So **`--duration` seconds × ~0.057 = game-days** (a 150s run ≈ 8.5 game-days; a 250s run ≈
  14 days — enough for a full predator lifecycle of 7.5 days + turnover). `sim_batch` is a gated test-zone
  field (production zones omit it → batch=1 → byte-identical). Don't send mutating player messages to a
  batched zone (input is processed only on the first sub-tick of each call).
- **dotnet path:** `~/.dotnet/dotnet` here (not on PATH). If you set a var, use `DOTNET=$(command -v
  dotnet || echo ~/.dotnet/dotnet)` — do NOT wrap it in a `(...)` subshell (the assignment won't persist;
  the run then executes bare `run` → "run: command not found").
- **CSV:** `tick,<species…>,total_bugs`; written once at run end. Plot args: `[csv] [chart_name]
  [title]` — a `chart_name` saves a persistent named copy under `tools/_generated/ecology_charts/`
  (tuning runs accumulate there for review; index in that dir's `README.md`). The harness also writes
  `fly_weather.csv` (rain/drought spans) + `fly_corpses.csv` (live `dead_<bug>` carrion count); the plot
  shades the weather + draws a dotted "corpses" line automatically when those files sit beside the pop CSV.
- **FRESH START (reproducible runs):** bug_lab sets `ephemeral_swarms: true` so MatchInit skips
  `restoreSwarms` and re-spawns the `initial` population every run — otherwise the prior run's saved
  populations reload (e.g. butterflies pinned at their cap), and runs aren't comparable. A normal restart
  is therefore a clean slate; you do NOT need to wipe storage. (Server log confirms: "Seeded world with N
  swarms across M species" = fresh; "restored N swarm(s) from save" = a persisted zone.)
- **TIMESCALE (don't make the 10× mistake):** `DayLengthTicks = 8400` → **1 game-day = 8400 ticks = 840
  sim-seconds = 14 game-minutes.** A `--duration 600` run at 6× = 36000 ticks = **~4.3 game-days** (NOT 42
  — game-days = `tick / 8400`, the plot's x-axis is sim-seconds = `tick/10`). This matters: predator
  `lifespan_secs` ≈ 6300 = **7.5 game-days**, so a 4-day run NEVER shows old-age death — predators only
  starve in a short run. To see a full multi-day lifecycle/turnover, run LONGER (a 15-game-day run ≈ 2100s
  wall ≈ 35 min at 6×; this is why batching sim-steps per call is worth doing).
- **All the tuning dials live in `docs/product/ecology_parameters.md`** (the control panel: every birth /
  death / food / Director-band parameter, what it does, where it is, which way to tweak). Tune populations
  by adjusting those params — NOT by adding new food items/occupants (a hack). The whole web keys off the
  **fly prey base**; fix it first.
- **Read the shape**, not just survival: predators should PERSIST (not crash to 0 in ~60s — the old
  spawn-at-0-satiation bug), populations should OSCILLATE in-band (a flat line pinned at a cap = dead
  dynamics), and `total` should stay under the hard `max_population` caps. The lab layout (per-species
  pens + the wasp/centipede predator-prey-detritivore arenas) is authored in `tools/make_bug_lab.py`.
- **Master dials** (the tuning knobs): food regen (`nectarRegenPerTick`/`hostRegenPerTick` in
  `handlers_farming.go`), flower/tree density + Director bands in `make_bug_lab.py`'s `MAX_POP`/`DIRECTOR`.
- Per-species live overlay in-game is DebugOverlay **F5**; this headless loop is the persistent record.

## 3. Determinism — "do two players see the SAME bugs?" (the whole point of the frontier-gated system)
Bugs are simulated deterministically on each client from the broadcast leg ledger; the success criterion is
that all clients' `ComputeStateHash` (FNV over bug positions/velocities) match at the same tick. **THE test
is ① — two REAL clients, full system. The others are pre-checks/backstops, NOT substitutes.**

- **① CROSS-CLIENT SYNC TEST — two real headless Unity players, full system (THE proof). COMMITTED.**
  Real client + real server, merge/split/spawn all live. Built standalone players don't take the Unity
  project lock, so they run alongside an open Editor (this is how "N players, Editor open" works).
  ```bash
  # one-time per code change: build a CURRENT player (needs the project lock free for a headless build):
  #   Editor menu  BugFarmer ▸ Build Sync-Test Player        (build from the open Editor), OR with Editor closed:
  #   "Unity.exe" -batchmode -quit -projectPath BugFarmerClient -executeMethod SyncTestBuild.Build -logFile -
  docker compose up -d                         # server (rebuild if Go changed)
  tools/run_sync_test.sh village_21_B 60       # launches 2 players, diffs their per-tick hash streams
  ```
  Each player (`HeadlessSyncTest.cs`, flag `-synctest`) auth's as a distinct account (NetworkManager reads
  `-clientid`), enters the zone ephemerally, records its tick hashes (the F1/F2 `TickTraceBuffer`), quits.
  The script diffs the two `trace_<id>_*.csv` streams → **IDENTICAL = players see the same bugs**; first
  mismatch = exact divergence tick. Backstop: it also greps the server drift detector. Run this after ANY
  change to the bug sim, sync, or species data. (Gotcha: a *headless build* needs the Editor closed — a held
  `BugFarmerClient/Temp/UnityLockfile` makes batchmode exit 1; *running* the built players is fine with the
  Editor open.)
- **② sim-determinism pre-check (FAST, no Unity, no server):** `~/.dotnet/dotnet run --project
  tools/sim-determinism` (`--selftest` proves it detects divergence). Links the real per-bug sim source and
  runs it twice — catches wall-clock / unordered-collection / static / float nondeterminism in seconds. But
  it ONLY covers the per-bug movement core (no merge/split/spawn, single process) — a green here does NOT
  replace ①. See `tools/sim-determinism/README.md`.
- **③ server reproducibility gate (headless):** same seed → identical `ECOSTATS` across two `run_config.py`
  runs proves the SERVER sim is deterministic (§1). Known limit: not byte-identical (harness join timing).
- **④ live drift detector (manual, real GUI clients):** connect ≥2 clients, play,
  `docker compose logs nakama | grep -i "Drift detected"` (server samples each client's hash every ~300
  ticks; `match.go` `checkDriftSampling`). ① automates exactly this with headless players + an exact trace diff.

**Why ① is THE test (do not skip to ②):** ② is a single-process run-twice of only the movement core; the
owner's requirement is two REAL clients agreeing on the ENTIRE system. Do not present a movement-only or
seed-run-twice check as "players are in sync." And do not build any of this as throwaway scripts — it lives
in the repo (`HeadlessSyncTest.cs`, `SyncTestBuild.cs`, `tools/run_sync_test.sh`).

## 3.5. Debugging WHY a behavior stalls (temporary server diagnostics)
The harness reports the event ledger and dumps swarm positions only at t=0 — it does NOT show a bug's
internal state over time (phase / satiation / target / why it isn't breeding). When a sim behavior
silently doesn't happen (e.g. "butterflies never breed"), the fastest way to find the break is a
**temporary server `logger.Info`**, then a short harness run + `grep`:
- Gate it tightly so the log isn't a flood: by species (`if swarm.SpeciesID == "butterfly_meadow"`)
  and a slow clock (`worldState.TickCount%50 == 0`) for periodic state, or fire it once per decision
  (e.g. at the forage/target choice) to see inputs→output.
- Log the decision INPUTS and the RESULT (phase, satiation, the FindNearbyFood hits + their flags,
  the chosen target) — that pins which stage of the chain breaks (e.g. "reaches `reproducing` but
  `target=""`" ⇒ the target is found then cleared, not a discovery failure).
- `docker compose up -d --build nakama` to load it; `dotnet run -- --zone bug_lab --duration 90`;
  `docker compose logs nakama --since 3m | grep <TAG>`. Tag logs distinctively (`P7DIAG …`) to grep.
- **STRIP every diagnostic before committing** (`grep -rn '<TAG>\|TEMP-' nakama/modules` must be
  empty) and fold the finding into a permanent `*_test.go` + a code comment so it can't regress.
  (P7 found two bugs this way: `foodSourceAlive` didn't know occupant-backed food; the forage duty
  cycle starved slow feeders — both now have regression tests + comments.)

## 4. Unity Editor pass (client C#)
Client C# is often written headlessly (no local Unity compiler) — it needs an **Editor compile + visual
check**. In-game debug keys (DebugOverlay): **F1** record · **F2** dump trace · **F3** log state · **F4**
swarm centre markers · **F5** multi-species population graph · **F6** tuning · **F8** world debug (incl.
"Stock Bug Lab") · **F9** stats.

## 5. Which to run when
| You changed… | Run |
|---|---|
| Server sim/economy logic | §1 Go tests + §2 observe |
| Influence/event ledger, reproduction/death/predation, anything affecting bug positions | §3 determinism (drift or trace-diff) + §1 |
| Zone join/leave, reconnect, cross-zone | §2 `--reconnect` / `crosszone` + §3 trace-diff before/after |
| Zone/farm persistence | §2 `harness_persist_test.sh` |
| Client UI / rendering | §4 Editor pass |

## 6. Maintain this skill
This skill exists because prior sessions lost this knowledge and re-derived it wrong. When a tool, command,
key, or scenario changes, **update this file** — and when you add a test, add its line here (§0).
