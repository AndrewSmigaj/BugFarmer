# Stage 1.1: the numbers after (2026-10-07)

Part of `docs/plans/village-slice.md`, Stage 1.1 (the client's bug simulation without waste). The same measurements as
the "before" numbers (`stage1-before-2026-10-06/README.md`), on the same PC, bench village and settings, made after the
five same-results changes: the food lookup through a cell index, the state check reading each bug directly, groups and
bugs kept sorted, reused per-tick lists, and the strike check's reused lists. Each change was proven to give exactly
the same results as before by the equivalence check, both ways round. Raw files:
`tools/_generated/scaling/2026-10-07-after-s11/` (git-ignored). "Typical" = the median; "slow" = the worst 1 in 100.

## 1. The bug simulation on a player's computer, per tick (release build, fixed count)
| Bugs | Before: typical / slow / worst | After: typical / slow / worst | Target (Stage 1 done when) |
|---|---|---|---|
| 1,000 | 2.7 / 4.5 / 16.5 ms | **0.56 / 1.06** / 12.6 ms | — |
| 2,000 | 6.0 / 10.0 / 20.7 ms | **1.06 / 2.0** / 12.5 ms | typical ≤ 2 ms, slow ≤ 4 ms ✓ |
| 4,000 | 13.3 / 29.9 / 40.4 ms | **2.1 / 3.5** / 13.8 ms | slow ≤ 6 ms ✓ |

Ticks over 4 ms at 4,000 bugs: 2,919 of 2,919 before, 13 of 2,998 after. The worst tick is now about 12.5–14 ms
whatever the bug count, which points at a one-off cost (start-up or a memory clean-up) rather than the bugs; not yet
looked into.

## 2. Where the time goes (development build, per tick)
| Part | 1,000 bugs | 2,000 bugs | 4,000 bugs |
|---|---|---|---|
| The whole bug simulation | 3.58 → 0.69 ms | 6.93 → 1.32 ms | 15.72 → 2.63 ms |
| Bug movement (all groups) | 1.61 → 0.58 ms | 3.51 → 1.11 ms | 9.28 → 2.21 ms |
| … of which looking for food | 0.43 → 0.06 ms | 1.38 → 0.12 ms | 5.18 → 0.24 ms |
| Predator strikes | 1.03 → 0.07 ms | 1.72 → 0.14 ms | 3.23 → 0.27 ms |
| The per-tick state check | 0.88 → 0.02 ms | 1.62 → 0.04 ms | 3.07 → 0.09 ms |
| Memory thrown away per tick (should be ≈ 0) | 464 → ~11 KB | 884 → ~19 KB | 1,705 → ~40–54 KB |
| … after step 7 (the counter RNG fix) | ≈ 0 | ≈ 0 | ≈ 0 |

(From the part-by-part timing totals divided by the ticks run; the memory is the estimate the rig makes from frames with
and without a tick.) Moving the bugs themselves, at about half a millisecond per 1,000 bugs, is now most of the cost.
The memory thrown away per tick was about 3% of before after step 5, not yet zero. **Step 7 found it:** the counter
random-number helper made a copy of the group's id on every roll, about 11 bytes per bug per tick (the headless test
program measured the same 11 bytes exactly, and zero after the fix). After step 7, in the 5-second windows without the
authority's 10-second snapshot, a frame with a tick allocates no more than a frame without one (+0.4 / +3.0 / −0.2 KB
at 1,000 / 2,000 / 4,000 bugs: noise). The snapshot itself still allocates (the send-on-join change removes it), and
drawing allocates 1–7 KB a frame (Stage 1.2). Raw files: `tools/_generated/scaling/2026-10-07-after-s17/`.

## 3. Today's village at four times its bugs, living normally (6× speed, 600 s)
| | Before | After |
|---|---|---|
| Client keeps up with the zone (60 ticks a second) | 32.8 ✗ (falls behind) | **60.4 ✓** |
| Client tick at 2,000–3,000 bugs, typical / slow | 64.8 / 83.8 ms | **2.6 / 5.0 ms** |
| Client tick at 1,000–2,000 bugs, typical / slow | 35.8 / 57.7 ms | **1.9 / 3.4 ms** |

Both runs start from the same ~3,530 bugs (seed 1337) and lose bugs along the same path, tick for tick (at tick
~11,500: 474 before, 532 after). The old client ran at half speed, so in the same 10 minutes it covered half as many
game-days and stopped with more bugs alive; its whole-run median (~1,500 bugs) and the new one's (~690) are therefore
not comparable, and the table compares the two at the same bug counts instead (5-second windows grouped by bug count).
Day 1 differs between the runs (flies killed by predators: 229 before, 624 after), as expected: a client at half speed
reports its predators' strikes late, so the zone lives differently — another reason the fixed-count runs are the
measure.

## 4. Drawing the bugs, per frame (headless; drawing is Stage 1.2)
| | 1,000 bugs | 2,000 bugs | 4,000 bugs | Target at 2,000 |
|---|---|---|---|---|
| Before, typical / slow | 1.6 / 2.5 ms | 2.8 / 4.5 ms | 5.6 / 9.4 ms | slow ≤ 2 ms |
| After, typical / slow | 1.2 / 1.5 ms | 2.0 / 2.7 ms | 4.0 / 5.3 ms | |

Drawing improved a little because it reads the kept-sorted bugs instead of sorting them each frame; the rest of it
(on-screen-only smoothing and trails) is Stage 1.2.

## 5. Stage 1.2: drawing only what is in view (2026-10-07)
A group of bugs outside the camera's view (plus a 3-cell margin) isn't drawn: its object is switched off, and switched
back on when it returns. The sting check works out drawn positions on demand for groups out of view. The simulation is
untouched: the equivalence check gave identical results both ways round (2,518 / 2,512 live ticks).

**On screen (windowed, the camera walking the village, release build, typical / slow):**
| | Before Stage 1.1 | After 1.1 | After 1.2 | Target at 2,000 |
|---|---|---|---|---|
| Whole frame, 2,000 bugs | 3.98 / 14.1 ms | 2.99 / 4.47 ms | **0.63 / 1.68 ms** | |
| Drawing the bugs, 2,000 bugs | 3.16 / 5.31 ms | 2.11 / 2.66 ms | **0.07 / 0.11 ms** | slow ≤ 2 ms ✓ |
| Whole frame, 4,000 bugs | 6.68 / 29.9 ms | 5.31 / 8.91 ms | **0.71 / 1.88 ms** | |
| Drawing the bugs, 4,000 bugs | 5.31 / 8.91 ms | 4.22 / 5.62 ms | **0.13 / 0.22 ms** | |

About 130 frames per 300 s run still take more than 16.7 ms, in every build (173 before Stage 1.1): about half in the
5-second windows holding the full bug snapshot the computer in charge builds every 10 s (23 ms at 2,000 bugs, 42 ms at
4,000; the send-on-join change removes it), the rest elsewhere (up to 67–84 ms; not the bugs, cause not yet known).

**The simulation tick at 60 frames a second** (development build, old against new, interleaved): the tick reads 9–13%
slower (2,000 bugs 1.35 → 1.48 ms), the slow tick 19–58% slower, while the processor time per second of play (ticks
plus drawing) falls 87% (2,000 bugs 156 → 21 ms; 4,000 bugs 300 → 40 ms). The cache test explains it: with every group
still drawn, the parts that didn't change come back to the old build's values (strikes 0.115 against 0.111 ms, state
check 0.042 against 0.040) — the old build's drawing touched every bug every frame and so kept their data in the
processor's cache for the next tick — and the group tick shows the real added work, +7.6% (0.08 ms at 2,000 bugs).
The plan's rule for this check (no part more than 10% slower) **failed as written**; the next step merges the tick's two
passes over each group's bugs into one, which removes a pass of both.

**Side-by-side check** (every group still drawn, each bug's on-demand position against its sprite, every tick): at
2,000 bugs, 0 of 3.37 million positions more than 0.05 cells apart once the game was running; 182 in the first 600
ticks, up to 0.13 cells. Cause: the sprites hang on their group's object, which glides toward the group's centre in its
own per-frame update and drags them until the next frame places them — large only while start-up frames are slow. The
on-demand position is the intended one; the drag is old and cosmetic (BACKLOG). The rule (none over 0.05) **failed as
written** on those start-up positions. (The 6× run hit the startup resync fault and is set aside.)

**The two-player sting test** (the computer in charge at the south edge, the stung player F out of its view; 1,000
held bugs at 6×; stings on F from the in-charge computer's report log): F standing at the spawn — old 0 / 138 / 16
(154), new 38 / 4 / 107 (149); F walking the busiest feeding spots — old 26 / 12 / 30 (68), new 8 / 10 / 24 (42).
**Passed** both (stung on every seed the old build stung, totals within half to twice). The counts swing widely from run
to run; the side-by-side check is the precise test of the positions the stings read.

**Behaviour check:** the first five seeds (uncapped frame rate) flagged flies — landed −49%, landings started −50%,
breeding share −54% (5/5 seeds, ~5 standard errors), with the pace equal but the frame rates not (~740 old, ~3,600
new). Then: old against new at 60 frames a second, ten seeds — nothing flagged; the old build uncapped against itself at
60 — nothing; the new build uncapped against itself at 60, ten seeds — nothing; and the uncapped comparison itself on
five fresh seeds, ten in all — nothing flagged (fly breeding −22% and feeding −20%, under 1 standard error). The first
flag was chance. Fly landing still leans down over the ten (−48%, 8 of 10 seeds, 3.1 standard errors, under the bar):
watched in the next behaviour checks.
