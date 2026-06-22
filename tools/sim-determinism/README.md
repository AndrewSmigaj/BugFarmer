# sim-determinism — headless bug-sim determinism gate

**What it proves:** the per-bug client simulation (the code every player runs to place individual bugs
around a server-synced swarm *center*) is **deterministic** — same seed + same center path ⇒ byte-identical
bug positions every run. That is the success criterion for "all players stay in sync": the server only syncs
swarm *centers*; each client computes the individual bugs locally, so they must compute them **identically**
or players desync.

**Why this exists / DO NOT delete it:** the determinism core is fragile and easy to break by accident
(a stray `DateTime.Now`, a `Dictionary`/`HashSet` iteration, shared static state, a float instead of
fixed-point). This is the fast tripwire that catches it. (It replaces a throwaway version that was run
once and never committed — hence the rule: this lives in the repo.)

## Run

```bash
~/.dotnet/dotnet run --project tools/sim-determinism            # exit 0 = deterministic, 1 = DIVERGED
~/.dotnet/dotnet run --project tools/sim-determinism -- --selftest   # proves the harness can SEE divergence
```

`--selftest` injects a wall-clock perturbation into one run and asserts the harness reports the divergence —
so a normal PASS is meaningful, not vacuous. Run it once after touching this tool.

## How it works (and why it's trustworthy)

- The `.csproj` **links the real client sim source** (`FixedPoint`, `DeterministicRandom`, the movement
  behaviors, `MovementFactory`, `BugAgent`, `BugCollision`) — it does **not** copy or re-implement it, so it
  can never silently drift from what players run. Those files are deliberately Unity-independent (fixed-point
  math + counter-based RNG); `Shims.cs` stubs the few Unity touch-points (a `Vector2` render helper, and the
  `InfluenceManager`/`TilemapManager` singletons the sim already null-checks → headless = no food, no walls,
  fully deterministic). `EntityDatabase` reads the real `nakama/data/species.json` so each species uses its
  true movement style.
- `Program.cs` drives all 6 species for 600 ticks along a fixed center path, hashing every bug's fixed-point
  position+velocity each tick (the same FNV-1a as the client's `ComputeStateHash`), runs the whole thing
  **twice**, and asserts the per-tick hash streams are identical (plus a "bugs actually moved" sanity check).

## Scope — what this DOES and DOESN'T cover (honest)

**Covers:** the per-bug **movement** sim determinism — the fragile deterministic core. Catches the real
desync causes (wall-clock, unordered collections, shared statics, float math).

**Does NOT cover:**
- Server **merge/split/spawn** orchestration (that lives in the `SwarmManager`/`SwarmVisual` MonoBehaviours;
  replaying a recorded server ledger through them is the next extension).
- That two **different machines** agree — for that, use the server **drift detector** with ≥2 real clients
  (`docker compose logs nakama | grep -i "Drift detected"`) or **headless Unity** (`-batchmode -nographics`)
  instances. Server-side sim determinism is separately covered by the reproducibility gate
  (`run_config.py`, same seed → same `ECOSTATS`).

This is the **first, fastest** gate on the ladder; see `.claude/skills/test-changes/SKILL.md` §3 for the rest.

## Maintenance

If a sim file is added under `BugFarmerClient/Assets/Scripts/Bugs/`, add it to the `<Compile Include>` list
in `SimDeterminism.csproj`. The printed final hash is a stable fingerprint — if it changes across commits,
the sim or species data changed (expected after a tuning/behavior change; a surprise change is worth a look).
