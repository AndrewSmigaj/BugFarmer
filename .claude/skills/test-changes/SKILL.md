---
name: test-changes
description: Use when verifying ANY change to the Bug Farmer server, bug simulation, or client — Go unit tests, the headless sync-harness (protocol/ledger, scripted-player scenarios, login/logoff reconnect, cross-zone, persistence/restart), the determinism / "are all players in sync" checks (server drift detector + client tick-hash trace diff), and the Unity Editor pass. Use it to test each implementation task and to confirm all players see the same world. Also documents how to persist new tests durably instead of throwaway scripts.
---

# Test a change

How to verify Bug Farmer changes. Most of this runs **headless (no Unity)**. Pick the section(s) that match
what you changed (see §5), then add a durable test per §0.

**Related (use together):** for a deterministic/sync change, design + review it with
`.claude/complex-change-review.md` (the stages × failure-modes loop + the BugFarmer invariant checklist) and
`.claude/lenses.md` (review lenses), and follow the `frontier-sync` skill to wire it. This skill is the
EXECUTION GATES those reference — the model-independent arbiter that decides PASS/FAIL.

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
host_plant brood forage_pool ecology_director predator_starvation shop recipe_unlock` (`*_test.go`).
Run after ANY server-logic change. Add a `*_test.go` for new sim/economy logic (mirror `predation_test.go`).
- `shop_test.go` covers buy/sell/recipe/book + the **`sell_batch`** barter basket (mixed batch, duplicate-slot
  no-double-pay, the negative-qty duplication exploit, bug-dealer batch) + the arbitrage invariant.
- NOTE: this script pipes through `tail -30` — for the FULL verbose list run the inner `docker compose run …
  go test` yourself or grep the un-tailed output; don't conclude "test missing" from the tail.

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
python3 tools/ecology/make_bug_lab.py                                   # (re)author the lab zone (pens + predator-prey arenas)
docker compose build builder && docker compose up -d --force-recreate nakama   # server-CODE change: recompile plugin
#   …OR just `docker compose restart nakama` if you ONLY edited bug_lab DATA (zone.json is read at startup)
rm -f /tmp/fly_counts.csv
~/.dotnet/dotnet run --project tools/sync-harness -- --zone bug_lab --duration 150 --tag eco   # see below: 150s ≈ 8.5 game-days
python3 tools/ecology/plot_fly_counts.py /tmp/fly_counts.csv <chart_name> "<Title>"   # → tools/_generated/ecology_charts/<chart_name>.png
python3 tools/ecology/plot_interactions.py --tag <chart_name> --since 10m            # the "WHY": births-by-source / deaths-by-cause
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
- **All the tuning dials live in `docs/product/ecology/ecology_parameters.md`** (the control panel: every birth /
  death / food / Director-band parameter, what it does, where it is, which way to tweak). Tune populations
  by adjusting those params — NOT by adding new food items/occupants (a hack). The whole web keys off the
  **fly prey base**; fix it first.
- **Read the shape**, not just survival: predators should PERSIST (not crash to 0 in ~60s — the old
  spawn-at-0-satiation bug), populations should OSCILLATE in-band (a flat line pinned at a cap = dead
  dynamics), and `total` should stay under the hard `max_population` caps. The lab layout (per-species
  pens + the wasp/centipede predator-prey-detritivore arenas) is authored in `tools/ecology/make_bug_lab.py`.
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
  # one-time per code change: build a CURRENT player (needs the project lock free → Editor CLOSED for a headless build):
  #   Editor menu  BugFarmer ▸ Build Sync-Test Player    OR headless (Editor closed; -logFile MUST be a C:/ path, not /mnt/):
  #   "Unity.exe" -batchmode -quit -nographics -projectPath BugFarmerClient -executeMethod SyncTestBuild.Build -logFile C:/…/build.log
  #   VERIFY THE BUILD via the managed DLL, NOT the .exe: Build/SyncTest/BugFarmerClient_Data/Managed/Assembly-CSharp.dll
  #   gets the fresh mtime + your new symbols (`strings … | grep <YourSymbol>`); the .exe is just the launcher and
  #   never changes — a months-old .exe mtime alongside a fresh DLL is normal, NOT a failed build.
  docker compose build builder && docker compose up -d   # rebuild the plugin (if Go changed) + start the server
  # CANONICAL GATE — staggered LATE-JOIN (run_sync_latejoin.sh): A authority creates the match, B LATE-JOINS it.
  # (run_sync_test.sh launches 2 CONCURRENT players → they can race into TWO separate matches → inconclusive; prefer latejoin.)
  # FRESH=1 force-recreates builder+nakama so the match starts at tick 0 on the CURRENT plugin. BOTH halves → SYNC: IDENTICAL:
  FRESH=1 tools/run_sync_latejoin.sh village_21_B 70 12                                  # co-located spawn
  FRESH=1 SPAWN_A=126,2 SPAWN_B=126,253 tools/run_sync_latejoin.sh village_21_B 70 12     # spawn-APART: disjoint chunks (the harder half)
  #   diff = tools/netcode/sync_diff.py (hash-stream primary + per-bug localizer; unit-tested by test_sync_diff.py).
  #   NON-VACUITY: the run must actually exercise the change (e.g. wasps killing flies); harness fails fast on 0-seed/0-bugs (exit 4/5).
  ```
  Each player (`HeadlessSyncTest.cs`, flag `-synctest`) auth's as a distinct account (NetworkManager reads
  `-clientid`), enters the zone ephemerally, records its tick hashes (the F1/F2 `TickTraceBuffer`), quits.
  The script diffs the two `trace_<id>_*.csv` streams → **IDENTICAL = players see the same bugs**; first
  mismatch = exact divergence tick. Backstop: it also greps the server drift detector. Run this after ANY
  change to the bug sim, sync, or species data. (Gotcha: a *headless build* needs the Editor closed — a held
  `BugFarmerClient/Temp/UnityLockfile` makes batchmode exit 1; *running* the built players is fine with the
  Editor open.)
  **VALIDITY GATE (learned the hard way, 2026-06-20):** a client only has bugs once it receives the world
  seed (`WorldInit`, OpCode 68 → `WorldSeedProvider.IsInitialized`). If a client shows **0 swarms** the whole
  run, the result is NOT determinism data — it's a dead client; do not compare it. `HeadlessSyncTest` now
  fails fast (exit 4 = seed never initialized, exit 5 = 0 bugs seen) so this can't masquerade as a run. Sanity
  every run: each client's log should have `[WorldSeedProvider] Initialized with seed: …` and
  `Tick N: >0 swarms`. (The bug that taught us this: the one-shot `WorldInit` was dropped during the join
  handshake by `WorldManager`'s `CurrentMatch==null` guard — fixed in commit `1c1b251` by buffering
  pre-join match-state. A 0-swarm authority gave a bogus "96% divergence" that wasn't real.)
  **DENSE-ZONE late-join gotchas (2026-06-29 — the gate had silently passed only because zones were small):**
  (1) **read cap** — the Nakama client's default `MaxMessageReadSize` is 256KB; a big `LateJoinSnapshot`
  (village_21_B's grew to ~305KB base64) silently TRUNCATES → the late-joiner gets **0 swarms**. Fixed:
  `NetworkManager` builds the socket with `WebSocketStdlibAdapter(maxMessageReadSize: 8MB)`. (2) **view-scoped reads
  diverge ONLY on disjoint chunks** — that is the whole point of the spawn-APART half: it caught the per-chunk
  `_food` hydration (food now rides the zone-wide ledger + snapshot, not `GroundItemSpawn`). Any sim-input read that
  isn't zone-wide/frontier-gated passes co-located but FAILS spawn-apart. See `architecture_swarm_sync.md` §0.
  (3) **NEW CLIENT SIM-STATE → LATE-JOIN COMPLETENESS (2026-07-14 — the S1/S2 predation desync).** If you add or
  rename ANY client-side per-bug or per-swarm state that feeds `ComputeStateHash` (bug x/y/vx/vy/hunt_target/
  feed_until) OR that moves a bug, it MUST be reconstructed on a late-joiner. Two carriers: **per-bug** state
  rides the VERBATIM per-bug relay automatically (`SwarmSnapshotData.Bugs` is `json.RawMessage` — never re-declare
  bug fields in a Go struct, or the server silently drops them: that was the bug); **per-swarm/zone** state (a
  new `InfluenceManager` dict like `_swarmStrikes`) needs its OWN snapshot section — mirror `_food`
  (`Export…`/`Clear…`/`Hydrate…` on the client + a relayed section on ZoneSnapshot/LateJoinSnapshot + clear-then-
  hydrate before replay in `HandleLateJoinSnapshot`). **VERIFY it with a NON-VACUOUS `run_sync_latejoin` that
  actually exercises the new state** (e.g. wasps must be HUNTING when B joins — a run where the behavior never
  fires is VACUOUS and proves nothing; that is how S1/S2 passed while broken). A quick way to prove non-vacuity +
  reconstruction at once: temporarily log the new field per bug on A and B and assert 0 A-vs-B mismatches over
  the overlap, in a window where the behavior is active.
- **② sim-determinism pre-check (FAST, no Unity, no server):** `~/.dotnet/dotnet run --project
  tools/sim-determinism` (`--selftest` proves it detects divergence; `--los-test` checks the
  `BugCollision.LineBlocked` predator line-of-sight geometry, #20). Links the real per-bug sim source and
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
