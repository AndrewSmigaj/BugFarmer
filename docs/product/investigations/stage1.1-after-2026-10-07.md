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
