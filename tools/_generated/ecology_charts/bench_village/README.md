# bench_village — a measurement copy of the village

A copy of `village_21_B`'s authored files (`tools/ecology/make_bench_zone.py`), so measurement runs never touch the
real village's save (`run_config.py` wipes the tested zone's save). Same bugs, food and tuning as the shipped village.

- **`current/`** — the 48-game-day baseline of 2026-10-04 (`tools/bug_lab_configs/bench_baseline.json`): the first run
  with the client keeping pace with a fast-forwarded zone, so the bugs' own hunting and eating run faithfully. It is
  the "before" picture for the village slice. Read it with
  `docs/product/investigations/village-baseline-2026-10-04/README.md`.
- **`archive/`** (not in git) — every run, including the scaling runs of the same night (S1).
