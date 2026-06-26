# Ecology tuning charts

Output of the bug-ecology tuning harness (`tools/ecology/run_config.py`). **Organized per ZONE**, because tuning is
per-zone (each zone has its own species mix, food, and spawn config). See the **`ecology-tuning` skill**
(`.claude/skills/ecology-tuning/`) for the full workflow; this file just explains the layout.

```
ecology_charts/
  README.md                     ← you are here
  _data/                        ← raw run logs + telemetry CSVs (nakama_*.log, *_log_*.csv). Not charts;
                                   kept so plots can be regenerated. Safe to ignore / delete to reclaim space.
  <zone>/                       ← one folder per zone (village_21_B = the real shipped zone; bug_lab = the
                                   old fenced behavior-observation arena, ARCHIVED — do not tune balance on it)
    README.md                   ← what's being tuned in this zone + where its numbers currently sit
    current/                    ← the CURRENT SETUP: charts for the latest canonical (baseline) run — i.e.
                                   "where this zone's ecology sits right now". Overwritten each baseline run.
        population.png          ← per-species population vs game-day (the main read)
        interactions.png        ← births-by-source / deaths-by-cause / predation matrix per day (the "why")
        phase_portraits.png     ← population-vs-its-food loops (closed loop = alive oscillation; spiral = flat/crash)
    archive/                    ← every run kept for comparing which settings were better, one folder each:
        <YYYY-MM-DD_HHMM>_<tag>/   population.png, interactions.png, note.md (what this run changed + the result)
    comparisons/                ← cross-run overlay charts (one line per run) — the fastest before/after read
```

## How to read the three chart types
- **population.png** — is each species in a good, *oscillating* band, or flat / runaway / crashed / pinned at its cap?
- **interactions.png** — *why* a population moved: `b_*` = births by source (brood/nest/reproduce/reseed/spawn),
  `d_*` = deaths by cause (oldage/starve/predation/cull). High `reseed` = the Director is propping it up (bad —
  it should self-sustain). High `starve` = food/access-limited.
- **phase_portraits.png** — each species plotted against the food it eats, coloured by time. A closed loop =
  a live boom-bust cycle; an inward spiral = damping to flat; outward = crash/runaway.

## The strategy log
Every tuning move + its measured result is recorded in `docs/product/ecology/ecology_tuning_log.md` (append-only).
Read that to see what's been tried and why, before proposing a new lever.
