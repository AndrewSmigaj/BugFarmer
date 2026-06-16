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
Suite: `centipede combat predation nest fruit_tree release swarm_population player_hp equip world_env` (`*_test.go`).
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
