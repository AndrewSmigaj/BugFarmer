#!/usr/bin/env python3
"""Plot per-species bug populations over time from the sync-harness CSV (written to the temp dir as
fly_counts.csv at the end of a run). One line per species + a dashed total. Output:
tools/_generated/scratch/fly_counts.png.

The CSV is per-species: `tick,<species…>,total_bugs`. The x-axis is GAME-TIME (sim seconds), which is
tick/SimRate (SimRate=10) regardless of the zone's wall-clock call rate — so a 6x test run and a normal
run plot identically. Use this to read the ecology: boom-bust per species, oscillation, bounded-at-cap.

  python3 tools/plot_fly_counts.py [path/to/fly_counts.csv]
"""
import csv
import os
import sys
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SIM_RATE = 10  # canonical sim ticks/sec — sim-time = tick/SIM_RATE (see SimRate in match.go)

path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(tempfile.gettempdir(), "fly_counts.csv")
with open(path) as f:
    reader = csv.DictReader(f)
    cols = [c for c in reader.fieldnames if c not in ("tick", "total_bugs")]
    ticks, series = [], {c: [] for c in cols}
    totals = []
    for row in reader:
        ticks.append(int(row["tick"]) / SIM_RATE)  # sim-seconds (game-time)
        for c in cols:
            series[c].append(int(row.get(c, 0) or 0))
        totals.append(int(row.get("total_bugs", 0) or 0))

day_s = 8400 / SIM_RATE  # one game-day in sim-seconds (DayLengthTicks/SimRate)
fig, ax = plt.subplots(figsize=(12, 5))
for c in cols:
    if any(series[c]):  # skip species that never appeared
        ax.plot(ticks, series[c], linewidth=1.8, label=c)
ax.plot(ticks, totals, color="black", linewidth=1.0, linestyle="--", alpha=0.5, label="total")
# game-day gridlines so cycles are readable
if ticks:
    d = day_s
    while d < ticks[-1]:
        ax.axvline(d, color="gray", alpha=0.15, linewidth=0.8)
        d += day_s
ax.set_xlabel(f"game-time (s)   [1 game-day = {day_s:.0f}s, faint gridlines]")
ax.set_ylabel("bugs")
ax.set_title("Bug populations over time (per species)")
ax.grid(True, alpha=0.25)
ax.legend(loc="upper left", fontsize=8, ncol=2)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_generated", "scratch", "fly_counts.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
fig.tight_layout()
fig.savefig(out, dpi=120)
peaks = {c: max(series[c]) for c in cols if any(series[c])}
print(f"saved {out}  ({len(ticks)} samples)  peaks: {peaks}  total peak {max(totals) if totals else 0}")
