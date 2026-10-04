# What more bugs cost

*Measured 2026-10-04, first pass (S1 in the plan). Full numbers, method and caveats:
`docs/product/investigations/scaling-2026-10-04/README.md`.*

### The question
You asked for real numbers before deciding whether zones should hold more bugs or be four times bigger, and for as much
as possible to run on the players' computers. So I ran the village (a copy, never the real one) with its starting bugs
at 1×, 2× and 4×. One player, one fast desktop. The test client was the real game, in charge of the zone.

### What it found
**The server barely notices the bugs.** It spends well under 1 ms of its 100 ms per tick on them, at every size. Bugs
were moved to the players' computers by design, and the numbers show why that works.

**The players' computers are where bugs cost, and the cost grows much faster than the number of bugs.** Each tick (ten
a second) the player's computer moves every bug. The chart shows how long that takes, against the length of one frame
at 60 frames a second:

```svg Time the player's computer spends moving the bugs, per tick. The dashed line is one frame at 60 frames a second.
<svg width="720" height="330" viewBox="0 0 720 330" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Bug simulation time per tick: about 0.4 ms at 280 bugs, 1.2 ms at 550 bugs, 27 ms at 2,540 bugs; one frame is 16.7 ms">
  <g style="font-size:17px">
    <line x1="90" y1="250" x2="690" y2="250" style="stroke:var(--line-strong);stroke-width:2"/>
    <line x1="90" y1="30" x2="90" y2="250" style="stroke:var(--line-strong);stroke-width:2"/>
    <text x="80" y="255" text-anchor="end" style="fill:var(--ink-2)">0</text>
    <text x="80" y="200" text-anchor="end" style="fill:var(--ink-2)">10</text>
    <text x="80" y="145" text-anchor="end" style="fill:var(--ink-2)">20</text>
    <text x="80" y="90" text-anchor="end" style="fill:var(--ink-2)">30</text>
    <text x="80" y="35" text-anchor="end" style="fill:var(--ink-2)">40 ms</text>
    <line x1="90" y1="158" x2="690" y2="158" style="stroke:var(--cut);stroke-width:2;stroke-dasharray:8 6"/>
    <text x="100" y="150" style="fill:var(--cut)">one frame, 16.7 ms</text>
    <rect x="150" y="247" width="100" height="3" style="fill:var(--keep)"/>
    <line x1="200" y1="237" x2="200" y2="250" style="stroke:var(--ink-3);stroke-width:2"/>
    <text x="200" y="228" text-anchor="middle" style="fill:var(--ink);font-weight:700">0.4</text>
    <rect x="330" y="243" width="100" height="7" style="fill:var(--keep)"/>
    <line x1="380" y1="205" x2="380" y2="250" style="stroke:var(--ink-3);stroke-width:2"/>
    <text x="380" y="196" text-anchor="middle" style="fill:var(--ink);font-weight:700">1.2</text>
    <rect x="510" y="100" width="100" height="150" style="fill:var(--cut-soft);stroke:var(--cut)"/>
    <line x1="560" y1="39" x2="560" y2="100" style="stroke:var(--ink-3);stroke-width:2"/>
    <text x="560" y="92" text-anchor="middle" style="fill:var(--ink);font-weight:700">27</text>
    <text x="200" y="276" text-anchor="middle" style="fill:var(--ink)">~280 bugs</text>
    <text x="380" y="276" text-anchor="middle" style="fill:var(--ink)">~550 bugs</text>
    <text x="560" y="276" text-anchor="middle" style="fill:var(--ink)">~2,540 bugs</text>
    <text x="390" y="312" text-anchor="middle" style="fill:var(--ink-2)">bar: a typical tick · thin line: the slowest tenth of ticks</text>
  </g>
</svg>
```

- **~280 bugs** (the village after its first day): well under a millisecond. Nothing to see.
- **~550 bugs:** about 1 ms, and up to 8 ms on the slowest ticks. Still smooth.
- **~2,540 bugs:** 27 ms on a typical tick, 38 ms on the slowest. That's about two whole frames, ten times a second: the
  game would stutter, and this was a fast desktop.

Twice the bugs cost three times as much; about five times the bugs cost twenty-three times as much. The cost per bug
rises with the number of bug groups, so something in a tick seems to compare each group with every other one. I
haven't found which part yet.

The data the server sends each player roughly doubles with each step, to about 35 KB a second at the largest. That's
fine for one player on broadband, and worth watching with many players.

### What I recommend
- **Don't decide on more bugs or bigger zones yet.** First find what makes the cost grow faster than the bugs, and fix
  it, or spread a tick's work over several frames so it never lands in one. Then measure again.
- **Next measurements:** finer timers inside the bug simulation (which part of a tick takes the time); several players
  on one machine; a zone four times bigger (three client limits fixed at 256 cells have to be raised first); real
  frame times with drawing.

### Two faults found in the test tools (fixed)
- Since July 18 the ecology test client never recorded the population, so its runs drew no population charts.
- In a fast-forwarded test zone the client ran at normal speed while the server ran six times faster, so the bugs'
  own decisions (hunting, eating) fell further and further behind. Tuning results from those runs should be
  re-checked; the July village tuning used an older driver and isn't affected.
