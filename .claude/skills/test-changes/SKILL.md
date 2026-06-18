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
```
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

## 3. Determinism — "is everyone in sync?" (same bug positions across players)
Bugs are simulated deterministically on each client from the event ledger; the success criterion is that all
clients' `ComputeStateHash` (FNV over bug positions/velocities) match at the same tick.
- **Live drift detector (real clients, the standing backstop):** connect ≥2 clients to one zone, play, then
  ```bash
  docker compose logs nakama | grep -i "Drift detected"     # nothing logged = all clients' hashes agree
  ```
  The server samples each client's `ComputeStateHash` at the SAME settled tick (~20 behind frontier, ~every
  300 ticks) and logs divergence (`match.go` `checkDriftSampling`/`handleSampleResponse`, OpCodes 61/62).
- **Client tick-hash trace + diff (precise — finds the exact first-divergence tick):** in each client,
  DebugOverlay **F1** (start recording) → run the scenario → **F2** (dump) → writes
  `trace_<clientId>_<HHmmss>.csv` to `Application.persistentDataPath`, with a `# TICK n HASH xxxx PLAYERS k`
  line per tick (`TickTraceBuffer.cs`). Run on two clients (authority↔follower, or the same client before/
  after a reconnect) and **diff the `# TICK … HASH …` lines** — the first mismatch is where determinism broke.
  This is the tool that produced "hashes match tick-for-tick."
- **Headless proxy:** the §2 harness confirms every client receives the SAME in-order event ledger (no gaps /
  no stale-high) — identical inputs ⇒ identical positions, so it catches *server-side* divergence headlessly.
- **HONEST GAP:** there is NO single headless tool that simulates N players AND compares bug-position hashes
  (the harness is an observer; a `--clients N` hash mode was once proposed but never built — it would mean
  porting the client sim). Cross-player POSITION hashes therefore use real clients (live or trace-diff),
  optionally two **headless Unity** (`-batchmode -nographics`) instances.

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
