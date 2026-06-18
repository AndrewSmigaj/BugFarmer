#!/usr/bin/env python3
"""Plot per-species bug populations over time from the sync-harness CSV (written to the temp dir as
fly_counts.csv at the end of a run). One line per species + a dashed total. Output:
tools/_generated/scratch/fly_counts.png.

The CSV is per-species: `tick,<species…>,total_bugs`. The x-axis is GAME-TIME (sim seconds), which is
tick/SimRate (SimRate=10) regardless of the zone's wall-clock call rate — so a 6x test run and a normal
run plot identically. Use this to read the ecology: boom-bust per species, oscillation, bounded-at-cap.

  python3 tools/plot_fly_counts.py [path/to/fly_counts.csv] [chart_name] ["Title"]

With a chart_name it saves a NAMED, persistent copy to tools/_generated/ecology_charts/<chart_name>.png
(so tuning runs accumulate for review) in addition to the scratch png.
"""
import csv
import os
import shutil
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

# Weather overlay (rain/drought windows) from the harness's fly_weather.csv (same dir as the pop CSV).
# Shaded UNDER the population lines so the rain->fruit->population relationship reads at a glance.
wpath = os.path.join(os.path.dirname(os.path.abspath(path)), "fly_weather.csv")
_wcolors = {"rain": "#3b6fd4", "drought": "#d4a24a"}
_wlabelled = set()
if os.path.exists(wpath):
    with open(wpath) as wf:
        for w in csv.DictReader(wf):
            kind = w["kind"]
            x0, x1 = int(w["tick_start"]) / SIM_RATE, int(w["tick_end"]) / SIM_RATE
            ax.axvspan(x0, x1, color=_wcolors.get(kind, "#999999"), alpha=0.13, lw=0, zorder=0,
                       label=(kind if kind not in _wlabelled else None))
            _wlabelled.add(kind)

for c in cols:
    if any(series[c]):  # skip species that never appeared
        ax.plot(ticks, series[c], linewidth=1.8, label=c, zorder=3)
ax.plot(ticks, totals, color="black", linewidth=1.0, linestyle="--", alpha=0.5, label="total", zorder=3)

# Carrion (dead_<bug> on the ground) from fly_corpses.csv — the decomposer's food supply vs uptake.
cpath = os.path.join(os.path.dirname(os.path.abspath(path)), "fly_corpses.csv")
if os.path.exists(cpath):
    with open(cpath) as cf:
        cr = list(csv.DictReader(cf))
    if cr:
        ax.plot([int(r["tick"]) / SIM_RATE for r in cr], [int(r["corpses"]) for r in cr],
                color="dimgray", linewidth=1.2, linestyle=":", alpha=0.8, label="corpses", zorder=2)
# game-day gridlines so cycles are readable
if ticks:
    d = day_s
    while d < ticks[-1]:
        ax.axvline(d, color="gray", alpha=0.15, linewidth=0.8)
        d += day_s
ax.set_xlabel(f"game-time (s)   [1 game-day = {day_s:.0f}s, faint gridlines]")
ax.set_ylabel("bugs")
title = sys.argv[3] if len(sys.argv) > 3 else "Bug populations over time (per species)"
ax.set_title(title)
ax.grid(True, alpha=0.25)
ax.legend(loc="upper left", fontsize=8, ncol=2)
fig.tight_layout()
here = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(here, "_generated", "scratch", "fly_counts.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
fig.savefig(out, dpi=120)
peaks = {c: max(series[c]) for c in cols if any(series[c])}
# Named, persistent copy for review (tools/_generated/ecology_charts/<name>.png).
if len(sys.argv) > 2 and sys.argv[2]:
    chart_dir = os.path.join(here, "_generated", "ecology_charts")
    os.makedirs(chart_dir, exist_ok=True)
    named = os.path.join(chart_dir, sys.argv[2] + ".png")
    shutil.copyfile(out, named)
    print(f"saved {named}")
print(f"saved {out}  ({len(ticks)} samples)  peaks: {peaks}  total peak {max(totals) if totals else 0}")
