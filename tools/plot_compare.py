#!/usr/bin/env python3
"""Overlay per-species population trajectories from several run logs on one figure — so a tuning change's
effect is visible at a glance (one small-multiple panel per species, one line per run).

Usage: python3 tools/plot_compare.py out.png  "label1=/path/log1"  "label2=/path/log2"  ...
Each log is a nakama run-log containing the per-game-day `ECOSTATS day=.. sp=.. pop=..` lines.
"""
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ECO = re.compile(r"ECOSTATS day=(\d+) sp=(\S+) pop=(\d+)")
SPECIES = ["fly_common", "butterfly_meadow", "wasp_common", "centipede_garden", "millipede", "beetle_carrion"]


def parse(path):
    series = {}  # sp -> {day: pop}
    for line in open(path, errors="ignore"):
        m = ECO.search(line)
        if m:
            day, sp, pop = int(m.group(1)), m.group(2), int(m.group(3))
            series.setdefault(sp, {})[day] = pop
    return series


def main():
    out = sys.argv[1]
    runs = [(a.split("=", 1)[0], parse(a.split("=", 1)[1])) for a in sys.argv[2:]]

    fig, axes = plt.subplots(2, 3, figsize=(16, 8))
    fig.suptitle("Per-species population by game-day — run comparison", fontsize=14)
    for ax, sp in zip(axes.flat, SPECIES):
        for label, series in runs:
            s = series.get(sp, {})
            if not s:
                continue
            days = sorted(s)
            ax.plot(days, [s[d] for d in days], marker="o", ms=3, label=label)
        ax.set_title(sp, fontsize=11)
        ax.set_xlabel("game-day")
        ax.set_ylabel("pop")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(out, dpi=110)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
