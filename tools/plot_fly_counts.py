#!/usr/bin/env python3
"""Plot per-species bug populations over time from the sync-harness CSV (written to the temp dir as
fly_counts.csv at the end of a run). Output: tools/_generated/scratch/fly_counts.png (+ a named copy).

Layout (readable by design):
  - TOP: a combined overlay of every species on ONE shared y-axis auto-scaled to the per-species data
    (the `total_bugs` sum is NOT on this axis — it dwarfs everything; it rides a faint right-hand axis).
  - BELOW: small-multiples — one mini-panel per species, EACH scaled to its own range, so a species at
    ~20 is just as readable as one at ~2000. Weather spans + game-day gridlines on every panel.

The CSV is per-species: `tick,<species…>,total_bugs`. X-axis is GAME-TIME (sim seconds) = tick/SimRate
(SimRate=10), so a 6× test run and a normal run plot identically.

  python3 tools/plot_fly_counts.py [path/to/fly_counts.csv] [chart_name] ["Title"]
With a chart_name it also saves tools/_generated/ecology_charts/<chart_name>.png.
"""
import csv
import math
import os
import shutil
import sys
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SIM_RATE = 10          # canonical sim ticks/sec — game-time = tick/SIM_RATE
DAY_S = 8400 / SIM_RATE  # one game-day in sim-seconds (DayLengthTicks/SimRate)
WCOLORS = {"rain": "#3b6fd4", "drought": "#d4a24a"}


def _read_csv(path):
    with open(path) as f:
        reader = csv.DictReader(f)
        cols = [c for c in reader.fieldnames if c not in ("tick", "total_bugs")]
        ticks, series, totals = [], {c: [] for c in cols}, []
        for row in reader:
            ticks.append(int(row["tick"]) / SIM_RATE)
            for c in cols:
                series[c].append(int(row.get(c, 0) or 0))
            totals.append(int(row.get("total_bugs", 0) or 0))
    return ticks, series, totals, cols


def _sibling(path, name):
    return os.path.join(os.path.dirname(os.path.abspath(path)), name)


def _weather_spans(path):
    wpath = _sibling(path, "fly_weather.csv")
    spans = []
    if os.path.exists(wpath):
        for w in csv.DictReader(open(wpath)):
            spans.append((int(w["tick_start"]) / SIM_RATE, int(w["tick_end"]) / SIM_RATE, w["kind"]))
    return spans


def _corpses(path):
    cpath = _sibling(path, "fly_corpses.csv")
    if os.path.exists(cpath):
        cr = list(csv.DictReader(open(cpath)))
        if cr:
            return [int(r["tick"]) / SIM_RATE for r in cr], [int(r["corpses"]) for r in cr]
    return None, None


def _decorate(ax, spans, xmax, label_weather=False):
    """Weather shading + faint game-day gridlines on an axis."""
    seen = set()
    for x0, x1, kind in spans:
        ax.axvspan(x0, x1, color=WCOLORS.get(kind, "#999999"), alpha=0.12, lw=0, zorder=0,
                   label=(kind if (label_weather and kind not in seen) else None))
        seen.add(kind)
    d = DAY_S
    while xmax and d < xmax:
        ax.axvline(d, color="gray", alpha=0.13, linewidth=0.8, zorder=0)
        d += DAY_S
    ax.grid(True, axis="y", alpha=0.2)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(tempfile.gettempdir(), "fly_counts.csv")
    ticks, series, totals, cols = _read_csv(path)
    species = [c for c in cols if any(series[c])]
    if not ticks or not species:
        print("no population data to plot", file=sys.stderr)
        return
    xmax = ticks[-1]
    spans = _weather_spans(path)
    cx, cy = _corpses(path)
    cmap = {sp: plt.cm.tab10(i % 10) for i, sp in enumerate(species)}

    n = len(species)
    ncols = 2 if n <= 4 else 3
    nrows_sm = math.ceil(n / ncols)
    fig = plt.figure(figsize=(15, 4.5 + 2.4 * nrows_sm))
    gs = fig.add_gridspec(1 + nrows_sm, ncols, height_ratios=[3.2] + [1] * nrows_sm, hspace=0.45, wspace=0.18)

    # ---- combined overlay (top, full width) ----
    axc = fig.add_subplot(gs[0, :])
    _decorate(axc, spans, xmax, label_weather=True)
    for sp in species:
        axc.plot(ticks, series[sp], color=cmap[sp], linewidth=1.9, label=sp, zorder=3)
    if cx:
        axc.plot(cx, cy, color="dimgray", linewidth=1.1, linestyle=":", alpha=0.6, label="corpses", zorder=2)
    # total on a faint SECONDARY axis so it never squashes the per-species scale
    axt = axc.twinx()
    axt.plot(ticks, totals, color="black", linewidth=1.0, linestyle="--", alpha=0.22, zorder=1)
    axt.set_ylabel("total (faint, right)", color="gray", fontsize=8)
    axt.tick_params(axis="y", labelsize=7, colors="gray")
    axc.set_ylim(bottom=0)
    axc.set_ylabel("bugs (per species)")
    axc.set_title(sys.argv[3] if len(sys.argv) > 3 else "Bug populations over time (per species)")
    axc.legend(loc="upper left", fontsize=8, ncol=max(2, (n + 1) // 2), framealpha=0.6)

    # ---- small-multiples (one panel per species, own scale) ----
    for i, sp in enumerate(species):
        ax = fig.add_subplot(gs[1 + i // ncols, i % ncols])
        _decorate(ax, spans, xmax)
        ax.plot(ticks, series[sp], color=cmap[sp], linewidth=1.6, zorder=3)
        lo, hi = min(series[sp]), max(series[sp])
        mean = sum(series[sp]) / len(series[sp])
        ax.axhline(mean, color=cmap[sp], alpha=0.35, linewidth=0.9, linestyle="--", zorder=1)
        ax.set_ylim(0, max(hi * 1.15, 1))
        ax.set_title(f"{sp}   (min {lo} · mean {mean:.0f} · max {hi})", fontsize=9, loc="left")
        ax.tick_params(labelsize=8)
        if i // ncols == nrows_sm - 1:
            ax.set_xlabel(f"game-time s  [1 day = {DAY_S:.0f}s]", fontsize=8)

    fig.suptitle("", y=0.995)
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "_generated", "scratch", "fly_counts.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, dpi=120, bbox_inches="tight")

    if len(sys.argv) > 2 and sys.argv[2]:
        chart_dir = os.path.join(here, "_generated", "ecology_charts")
        os.makedirs(chart_dir, exist_ok=True)
        named = os.path.join(chart_dir, sys.argv[2] + ".png")
        shutil.copyfile(out, named)
        print(f"saved {named}")
    peaks = {sp: max(series[sp]) for sp in species}
    print(f"saved {out}  ({len(ticks)} samples)  peaks: {peaks}  total peak {max(totals) if totals else 0}")


if __name__ == "__main__":
    main()
