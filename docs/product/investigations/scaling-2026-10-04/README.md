# Scaling study, first pass (S1) — what more bugs cost, 2026-10-04

Part of [`docs/plans/finish-bugs-zones-items.md`](../../../plans/finish-bugs-zones-items.md) (S1). The question: how much
do more bugs cost the players' computers and the server, so the zone-size and server-or-client decisions rest on numbers.
This first pass covers **bug counts on one zone, with one player**. Still to do: several players on one machine, a
512-cell zone, frame time with real drawing, and the cost of each server system (see "Not measured yet").

## How it was measured
- **Zone:** `bench_village`, a copy of the village's authored files (`tools/ecology/make_bench_zone.py`), never the real
  save.
- **Bug counts:** `tools/bug_lab_configs/bench_scale_{1x,2x,4x}.json` (made by `make_scaling_configs.py`): the shipped
  tuning, with every species' start, cap and band scaled 1×, 2× and 4×. Nest species keep their nests.
- **Runs:** `python3 tools/ecology/scaling_study.py`, one run at a time on a quiet machine (i7-14700F; WSL2 with 8
  cores; nothing else running). Each run lasts 300 real seconds with the zone fast-forwarded 6× (about 2 game-days).
- **The player's side:** the real game client, headless (`HeadlessSyncTest -ecology`), in charge of the zone, so its
  bug decisions (hunting, eating) run as in play. Every ~5 s it records the time its bug simulation took
  (`Sim.SwarmTick`) and the ticks it simulated. The first 30 s are start-up and left out.
- **The server's side:** the built-in profiler (`PERFSYS` per game-day): tick time and its worst tick, and the bytes it
  broadcasts.
- Raw data (git-ignored): `tools/_generated/scaling/2026-10-04/<run>/`; the summary is `summary.md` there.

## Results
The village's numbers fall sharply on day 1 at these settings (most of the starting flies starve; the July 14 village
baseline shows the same), so the runs are compared by the bugs actually present, averaged over each run:

| Bugs in the zone (groups) | Player's computer: bug simulation per tick, median / slowest tenth | Ticks a second it reached (60 needed here) | Server: time per tick, average / worst | Data the server sends each player |
|---|---|---|---|---|
| ~280 (82) | 0.4 / 2.4 ms | 60 | 0.23 / 63 ms | 9.6 KB/s |
| ~550 (136) | 1.2 / 8.2 ms | 60 | 0.30 / 68 ms | 17 KB/s |
| ~2,540 (539) | 27 / 38 ms | 21 | 0.41 / 70 ms | 34 KB/s |

**What it means**
1. **The server is not where bugs cost.** It spends 0.2–0.4 ms of its 100 ms per tick on everything; its worst ticks
   (60–70 ms) are the start-up seeding on day 1; no tick went over 100 ms.
2. **The players' computers are, and the cost grows much faster than the bug count:** about 1.4, 2.1 and 10.7 µs per
   bug per tick. In play a tick comes ten times a second and its work lands in one frame (16.7 ms at 60 frames a
   second). At ~550 bugs that's about 1 ms, and up to 8 ms on the slowest tenth: fine. At ~2,500 bugs every tick costs
   27–38 ms, about two whole frames: a stutter ten times a second, and about a quarter of one core.
3. **Data per player roughly doubles with each step** (9.6 → 17 → 34 KB/s). About 35 KB/s is fine for one player on
   broadband; it matters with many players in one zone.
4. **The cost per bug rises with the number of groups** (82 → 539). That pattern points at work that compares each
   group or bug with every other one. Which part it is hasn't been measured yet.

**Recommendation (mine):** before deciding on "more bugs" or a zone 4× the size, find what makes the client's cost grow
faster than the bug count, and fix it or spread a tick's work over several frames. Next measurement: finer timers inside
the client's bug simulation (which part of a tick takes the time), then the same three runs again.

**Caveats**
- The ~2,540-bug run's client couldn't keep up, so it ran many ticks per frame to catch up. Its frame rate means
  nothing, but its time per tick is still valid.
- In that run the server ran ahead of the lagging client, so its server columns reflect the server's own counts,
  which fell faster (about 890 bugs at the end of day 1, 330 at day 2), not ~2,540.
- The client's whole-process CPU isn't reported. The headless client runs without a frame cap, so that number mostly
  measures idle spinning.
- One fast desktop (i7-14700F). A weaker player's computer would take longer per tick.

## Faults found in the test tools on the way (fixed)
- The ecology client never recorded a population sample (an overflow in its first comparison), so no real-client
  ecology run since 2026-07-18 produced population charts. Fixed in `4c824a09`.
- In a fast-forwarded zone the client simulated at normal speed while the server ran 6×: after 5 minutes the server was
  near tick 17,990 and the client near 2,980. The bugs' own decisions ran 6× too slowly against the server's births and
  starvation. The client now runs its clock at the zone's speed (`-timescale`). Fixed in `4c824a09`.
- The first pass of this study ran next to browser tests and its CPU numbers were unfair; it was re-run quietly.

## Not measured yet
- **The snapshot a late joiner downloads:** the profiler now counts it (`05e14624`), but the server was still running
  the older build during these runs, so it reads 0 here. It comes from the late-join check and the baseline run.
- **Several players on one machine**, then a 512-cell zone (4× the area). A 512 zone needs three client limits raised
  first: `DarknessOverlay.cs:21` (`N = 256`), `TilemapManager.cs:31` (`ShoreN = 256`) and `WaterAnimated.shader:28`
  (`_ShoreN = 256`).
- **Frame time with real drawing** (the headless client draws nothing).
- **Each server system's cost, and what it would cost on the players' computers**, for the keep-or-move table.
