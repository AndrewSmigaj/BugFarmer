# village_21_B — the real shipped zone (active tuning target)

256×256 open natural zone with the full 6-species food web. **This is where balance is tuned** (bug_lab is
fenced/fake — observation only). Goal: all 6 species in good, *alive* (oscillating) bands, bounded by
emergent food competition + predation + aging, with the hard `max_population` cap as a rare backstop.

- **`current/`** — charts for the latest baseline run = where the ecology sits right now.
- **`archive/<timestamp>_<tag>/`** — every run, for comparing which settings worked. `note.md` in each says
  what it changed + the result.
- **`comparisons/`** — overlay charts (one line per run) for fast before/after reads.
- Full move-by-move history + reasoning: `docs/product/ecology_tuning_log.md`.

## Current state (as of the latest baseline — seed 1337, ~8 game-days)
- **fly** — works (breeds on rotten fruit), but booms to ~1300–1500, sitting near its 1500 cap (cap-limited,
  not yet food/predation-bounded). Standing rotten fruit plateaus ~6k.
- **millipede** — stable ~130. **centipede** — the working fly predator (climbs late). **beetle** — low (~3–8).
- **butterfly** — oscillates low; noisy across runs (see determinism note below).
- **wasp** — STUCK at ~4. The nest economy is broken (resident starves at the nest, replaced by nestless
  Director reseeds; deposit/provision rhythm fragile). Forager-loop behavior was redesigned (cleaner) but the
  nest spatial/reseed problem is still open. See the tuning log.

## Caveats when reading these
- **Runs are reproducible-ish, not byte-identical** (seed 1337 fixed, but a residual shared-RNG-stream
  desync from the harness player gives ~1.5× day-to-day noise). Trust a lever only if it moves a population
  WELL beyond ~1.5×. Butterfly is the most noise-sensitive — don't over-read single-run butterfly numbers.
- Wall-clock pacing means runs reach slightly different day counts; compare at the same game-day.
