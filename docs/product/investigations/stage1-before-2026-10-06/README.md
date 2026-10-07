# Stage 1 "before" numbers (2026-10-06/07)

Part of `docs/plans/village-slice.md`, Stage 1.0e: how today's game performs before any speed-up, measured with the
Stage 1.0 rig, so every later change can be judged against it. Nothing here changes the game.

**How it was measured.** This PC (Intel i7-14700F). The bench copy of today's village (`bench_village`, a throwaway
copy of `village_21_B`, rebuilt before every run). The game client headless unless stated, release build for times,
development build for the part-by-part breakdown and memory. "Fixed count" runs hold the bug count steady
(`hold_population`) at normal speed (10 ticks a second); "natural" runs let the village live at 6× speed. Each run 300
or 600 seconds. Raw files: `tools/_generated/scaling/2026-10-06-before/` and `…/2026-10-07-tour/` (git-ignored).
"Typical" = the median; "slow" = the worst 1 in 100.

## 1. The bug simulation on a player's computer, per tick (release build, fixed count)
| Bugs | Typical | Slow | Worst | Target (Stage 1 done when) |
|---|---|---|---|---|
| 1,000 | 2.7 ms | 4.5 ms | 16.5 ms | — |
| 2,000 | 6.0 ms | 10.0 ms | 20.7 ms | typical ≤ 2 ms, slow ≤ 4 ms |
| 4,000 | 13.3 ms | 29.9 ms | 40.4 ms | slow ≤ 6 ms |

Today's code is about 2½–5× slower than the targets. At 4,000 bugs a single tick can take longer than a frame.

## 2. Where the time goes (development build, per tick)
| Part | 1,000 bugs | 2,000 bugs | 4,000 bugs |
|---|---|---|---|
| Bug movement (all groups) | 1.6 ms | 3.5 ms | 9.3 ms |
| … of which looking for food | 0.4 ms | 1.4 ms | 5.2 ms |
| Predator strikes | 1.0 ms | 1.7 ms | 3.2 ms |
| The per-tick state check (used to detect players out of step) | 0.9 ms | 1.6 ms | 3.1 ms |
| Memory thrown away per tick (should be ≈ 0) | 464 KB | 884 KB | 1,705 KB |

In today's village at four times its bugs (natural, ~1,500 bugs) a tick costs 29 ms: movement 12.7 (food lookup 8.1),
strikes 7.5, handling the server's events 5.1, the state check 3.7.

## 3. Drawing the bugs, per frame
| | 1,000 bugs | 2,000 bugs | 4,000 bugs | Target at 2,000 |
|---|---|---|---|---|
| Headless (drawing code runs, nothing shown) | 1.6 / 2.5 ms | 2.8 / 4.5 ms | 5.6 / 9.4 ms | slow ≤ 2 ms |
| **Windowed, camera walking the village** | — | **3.2 / 5.3 ms** | **5.3 / 8.9 ms** | slow ≤ 2 ms |
| Frames over 16.7 ms, windowed | — | 173 of 67,852 | 2,539 of 36,848 | none caused by bugs |

(typical / slow). In the windowed tour the whole frame was 4.0 / 14.1 ms at 2,000 bugs and 6.7 / 29.9 ms at 4,000.

## 4. Today's village living normally (6× speed, 600 s ≈ 4 game-days)
| | Today's numbers (~200 bugs) | Four times the bugs (~1,500) |
|---|---|---|
| Client keeps up with the zone (60 ticks a second) | 59.3 ✓ | **32.8 ✗** (falls behind) |
| Client tick, typical / slow | 1.3 / 6.0 ms | 23.7 / 84.1 ms |
| Server tick, average / worst | 0.17 / 59.5 ms | 0.32 / 110 ms |
| Data sent to each player | 6.9 KB/s | 22.2 KB/s |
| The full bug-state snapshot, average / largest | 175 / 589 KB | 1,101 / 2,347 KB |

The server's own count of bugs in the 4× run (about 900 on day 1, 250 by day 4, against ~1,500 on the client) is the
known fault that the server only runs the parts of the zone a player has loaded (Stage 1.3 fixes it).

## 5. A slower computer
The game held to two processor cores (process affinity), release build, fixed count: 1,000 bugs 3.4 / 10.6 ms per tick
(typical / slow); 2,000 bugs 7.5 / 12.6 ms (target on a slower computer at 2,000: slow ≤ 8 ms). Capping the processor
at 50% through the Windows power plan on top made no clear difference (2,000 bugs 7.1 / 13.3 ms), so it probably
did not lower this processor's clock; not counted as a result until the clock is measured during such a run.

## 6. Players staying in step
Two players (one walking a route), three with the computer in charge leaving: every computer identical on every tick.
A player rejoining as the same account, and plain late joins on one world, went out of step from their first tick —
three causes, investigated and fixed on 2026-10-07: `../latejoin-rejoin-divergence.md`. A fourth, rare fault (a client
stuck at tick 0 for its first seconds, then in a resync loop) is noted there, not yet investigated.

## 7. The checks built for Stage 1
- **The equivalence check** (`tools/netcode/equiv_check.py`): proven — two copies of one build are identical tick for
  tick; a one-line change is caught at the first tick.
- **The behaviour check** (`tools/ecology/behaviour_check.py`): no false alarms; became a two-step check on
  2026-10-07; its limits and calibration are in `behaviour-check.md`.

## 8. What it means for Stage 1.1
The biggest costs per tick are the food lookup (every group searching all food), the strikes pass and the per-tick
state check; per frame, drawing grows with every bug whether on screen or not; and every tick throws away memory.
Those are Stage 1.1's first targets, each to be proven with the equivalence check (same results) or, for a different
method, a side-by-side check plus the behaviour check.
