# current/ — the current setup (latest baseline run)

These three charts are the live snapshot of village_21_B's ecology under the canonical (no-delta) config.
They are OVERWRITTEN every time a baseline run finishes, so this folder is always "where we are now".
The exact run that produced them is also kept in `../archive/<timestamp>_baseline_*/` for history.

- **population.png** — per-species population vs game-day. The main read: who's oscillating in band, who's
  flat / runaway / pinned at the cap.
- **interactions.png** — per game-day, why each species moved: births by source (`b_brood/b_nest/b_reproduce/
  b_reseed/b_spawn`) and deaths by cause (`d_oldage/d_starve/d_predation/d_cull`), plus the predator→prey
  kill matrix. High `b_reseed` = propped up by the Director (not self-sustaining); high `d_starve` = food/
  access-limited.
- **phase_portraits.png** — each consumer plotted against its food stock, coloured by time: closed loop =
  live boom-bust oscillation, inward spiral = damping to flat, outward = crash/runaway.

To refresh: `python3 tools/ecology/run_config.py v21b_baseline --zone village_21_B --duration 600`.
