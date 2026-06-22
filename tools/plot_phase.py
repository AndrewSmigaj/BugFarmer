#!/usr/bin/env python3
"""Phase portraits + food-stock timelines for the bug ecology — the "read the emergent dynamics" tool.

Parses a nakama run-log for two soft-state telemetry streams the server emits once per game-day:
  ECOSTATS day=.. sp=.. pop=.. b_*=.. d_*=.. avg_sat=..   (per-species population + births/deaths)
  RESSTATS day=.. rotten=.. rotten_food=.. unripe=.. carrion=.. nectar=.. milkweed=.. msites=..

and renders, for each consumer↔resource pair we care about, BOTH:
  (a) a timeline — population and its food stock vs game-day (are they coupled? lagged?), and
  (b) a phase portrait — population (y) vs food stock (x), trajectory coloured by time:
        closed loop  = a live oscillation (food eaten down → pop falls → food recovers → pop rises)
        inward spiral = damping to a flat fixed point
        outward       = a crash/runaway (food never bounds it)

Usage:  python3 tools/plot_phase.py --log tools/_generated/ecology_charts/nakama_<tag>.log --tag <tag>
Output: tools/_generated/ecology_charts/phase_<tag>.png   (soft observation only; nothing is hashed)
"""
import argparse
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

CHARTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_generated", "ecology_charts")

# Which population is bounded by which food stock — the pairs we tune in isolation (plan §Method).
# (species_id, food_key, human label for the food axis)
PAIRS = [
    ("fly_common", "rotten", "rotten substrate (count)"),
    ("butterfly_meadow", "nectar", "nectar stock"),
    ("butterfly_meadow", "milkweed", "milkweed capacity"),
    ("millipede", "carrion", "carrion (count)"),
    ("beetle_carrion", "carrion", "carrion (count)"),
]

ECO_RE = re.compile(r"ECOSTATS day=(\d+) sp=(\S+) pop=(\d+).*?avg_sat=([\d.]+)")
RES_RE = re.compile(r"RESSTATS day=(\d+) (.+)")


def parse(log_path):
    """Return (pops: {sp: {day: pop}}, res: {key: {day: value}}, days sorted)."""
    pops, res, days = {}, {}, set()
    with open(log_path, errors="ignore") as f:
        for line in f:
            m = ECO_RE.search(line)
            if m:
                day, sp, pop = int(m.group(1)), m.group(2), int(m.group(3))
                pops.setdefault(sp, {})[day] = pop
                days.add(day)
                continue
            m = RES_RE.search(line)
            if m:
                day = int(m.group(1))
                days.add(day)
                for k, v in re.findall(r"(\w+)=([\d.]+)", m.group(2)):
                    res.setdefault(k, {})[day] = float(v)
    return pops, res, sorted(days)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True, help="nakama run-log with ECOSTATS + RESSTATS lines")
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()

    pops, res, days = parse(args.log)
    if not days:
        raise SystemExit(f"no ECOSTATS/RESSTATS lines found in {args.log}")

    # Only the pairs we actually have data for.
    pairs = [(sp, fk, lbl) for (sp, fk, lbl) in PAIRS if sp in pops and fk in res]
    if not pairs:
        raise SystemExit("no consumer/food pair had both population and stock data")

    n = len(pairs)
    fig, axes = plt.subplots(n, 2, figsize=(12, 3.1 * n), squeeze=False)
    fig.suptitle(f"Phase portraits + food-stock timelines — {args.tag}", fontsize=13)

    for row, (sp, fk, flabel) in enumerate(pairs):
        pser = [pops[sp].get(d) for d in days]
        fser = [res[fk].get(d) for d in days]
        xy = [(f, p, d) for d, p, f in zip(days, pser, fser) if p is not None and f is not None]
        if not xy:
            continue
        fvals, pvals, dvals = zip(*xy)

        # (a) timeline — pop (left axis) + food stock (right axis) vs day.
        axt = axes[row][0]
        axt.plot(dvals, pvals, color="tab:blue", lw=1.8, label=f"{sp} pop")
        axt.set_ylabel(f"{sp} pop", color="tab:blue")
        axt.tick_params(axis="y", labelcolor="tab:blue")
        axt.set_xlabel("game-day")
        axf = axt.twinx()
        axf.plot(dvals, fvals, color="tab:green", lw=1.4, alpha=0.8, label=flabel)
        axf.set_ylabel(flabel, color="tab:green")
        axf.tick_params(axis="y", labelcolor="tab:green")
        axt.set_title(f"{sp} vs {fk} — timeline", fontsize=10)

        # (b) phase portrait — pop vs food, coloured by time (early=purple → late=yellow).
        axp = axes[row][1]
        axp.plot(fvals, pvals, color="0.7", lw=0.8, zorder=1)
        axp.scatter(fvals, pvals, c=dvals, cmap="viridis", s=22, zorder=2)
        axp.scatter([fvals[0]], [pvals[0]], facecolors="none", edgecolors="k", s=80, zorder=3, label="start")
        axp.set_xlabel(flabel)
        axp.set_ylabel(f"{sp} pop")
        axp.set_title(f"{sp} vs {fk} — phase portrait", fontsize=10)
        axp.legend(fontsize=7, loc="best")

    fig.tight_layout(rect=(0, 0, 1, 0.97))
    os.makedirs(CHARTS, exist_ok=True)
    out = os.path.join(CHARTS, f"phase_{args.tag}.png")
    fig.savefig(out, dpi=110)
    print(f"wrote {out}  ({len(days)} game-days, pairs: {', '.join(f'{s}/{k}' for s, k, _ in pairs)})")


if __name__ == "__main__":
    main()
