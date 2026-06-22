# Bug Lab tuning configs

Each `<NN_name>.json` is a **delta** over the baseline, deep-merged and applied by
`tools/run_config.py <name>` (which snapshots → applies → restarts nakama → runs the fast `bug_lab`
harness → charts → **restores** the canonical data). The sweep is scored by `tools/compare_configs.py`.

## Schema (every section optional; absent = baseline)
| section | merges into | what it tunes |
|---|---|---|
| `lab` | `make_bug_lab.DEFAULT_LAB` | per-species caps (`caps`), Director bands (`director`), `sim_batch`, `call_rate`, `max_pop` |
| `tuning` | `nakama/data/ecology_tuning.json` | the Go balance dials (nectar/host regen, satiation, nest economy, nest-found distance…) — see `docs/product/ecology_parameters.md` |
| `species` | `nakama/data/species.json` | per-species fields (`reproduce_cooldown`, `breed_amount`, `feed_per_kill`, `lifespan_secs`, `satiation_decay_rate`, …) |
| `fruit` | `nakama/data/entities/occupants.json` (under each tree's `world`) | tree fruit rates (`max_fruit`, `fruit_grow_ticks`, `fruit_drop_ticks`) |

Deep-merge: dicts merge key-by-key (so a `director` delta only needs the species+fields it changes);
scalars and lists REPLACE.

## The objective (what compare_configs scores)
Targets are the **centers of an oscillation**, not flat lines: fly 100, butterfly 100, wasp/centipede/
beetle/millipede 30. Two acceptance criteria per species — **oscillates** (visible amplitude/period) and
**self-maintained** (troughs stay above the re-seed floor → `b_reseed` births ≈ 0). A population pinned
at its floor or flatlined scores poorly even at the right mean.

## The planned sweep (one dial/layer per config)
`00_baseline` · `01_no_cull` (natural equilibria) · `02_fly_food_up` · `03_butterfly_food_calibrate` ·
`04_predator_spread` (nest-found distance + home_range) · `05_predator_breed_up` · `06_decomposer_up` ·
`07_lifespans` · `08_combined` · `09_combined_tuned`. Build each from the prior run's interaction log
(diagnose with `plot_interactions.py`, change ONE thing).
