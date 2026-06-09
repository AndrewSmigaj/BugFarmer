#!/usr/bin/env python3
"""Plot the fly population over time from the sync-harness CSV (written to the temp dir as
fly_counts.csv at the end of a run). Output: tools/output/fly_counts.png.

  python3 tools/plot_fly_counts.py [path/to/fly_counts.csv]
"""
import csv
import os
import sys
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(tempfile.gettempdir(), "fly_counts.csv")
ticks, totals = [], []
with open(path) as f:
    for row in csv.DictReader(f):
        ticks.append(int(row["tick"]) / 10.0)  # seconds at 10Hz
        totals.append(int(row["total_bugs"]))

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(ticks, totals, color="tab:green", linewidth=2)
ax.set_xlabel("time (s)")
ax.set_ylabel("total bugs")
ax.set_title("Fly population over time (feed -> reproduce -> split -> plateau when food runs out)")
ax.grid(True, alpha=0.3)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "fly_counts.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
fig.tight_layout()
fig.savefig(out, dpi=120)
print(f"saved {out}  ({len(ticks)} samples, peak {max(totals) if totals else 0} bugs)")
