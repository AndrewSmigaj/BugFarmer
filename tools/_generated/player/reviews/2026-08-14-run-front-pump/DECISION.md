# run_front — PICKED: widest lowest

Owner decision (2026-08-14): **the widest, lowest variant**, `W3_widest_lowest`.

Chosen from `bronze_REACH.gif` — current, big reach, and three variants of it.

## What was wrong with run_front

`official.GAITS["FRONT_RUN"]` is byte-identical to `FRONT` apart from `ms`. The camera-facing run IS the
camera-facing walk played faster, and never got its own pose — the same mistake the side run already
fixed. The owner rejected it: hands held down by the sides do not read as running.

## The picked numbers

`W3_widest_lowest` in `tools/player_sprites/run_front_lab.py`:

| | current FRONT_RUN | picked |
|---|---|---|
| `row`   | 0.62 | **0.53** |
| `gap`   | 0.03 | **0.09** |
| `dx`    | 0.06 | **0.08** |
| `dy`    | 0.15 | **0.26** |
| `pulse` | — | **0.22** ← new |
| `ratio`, `ms` | 0.17, 90 | unchanged |

**`pulse` does not exist in the pipeline yet.** It is the thing the owner asked for — fists that grow and
shrink — the fist coming toward the camera grows and the one going back shrinks, which is
what sells a run toward the viewer. In the lab it scales each fist's size ratio by `1 ± pulse * s`.

Two earlier attempts were rejected on the way, both worth not repeating:

- **higher** (row 0.38 and above) — rejected by the owner: the fists cannot go that high, because they clip
  into the shoulders.
- drawing the smaller fist BEHIND the body — at chest height the torso is at its widest and swallows it
  entirely. Both fists go in front, as `gait.walk_front_into` already does; the size change carries the
  depth on its own.

## Not built

Nothing is wired in. Doing so touches three things, and `run_back` rides on the same numbers:

1. `gait.walk_front_into` — needs the `pulse` term (it has no concept of per-hand scale today).
2. `official.GAITS["FRONT_RUN"]` — the numbers above. **This is shared with `run_back`**, so both change.
3. a re-render of `run_front` + `run_back` for every official outfit via `build.py`.
