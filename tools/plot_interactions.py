#!/usr/bin/env python3
"""Parse the ECOSTATS / PREDLOG interaction log out of the nakama container logs and chart it.

The "why" telemetry for ecology tuning (Phase 4c). The server emits, once per game-day at the day
rollover, one `ECOSTATS day=N sp=… pop=… b_*=… d_*=… avg_sat=…` line per species and one
`PREDLOG day=N pred=… prey=… kills=…` line per predator-prey pair (see nakama/.../ecology_stats.go).
This reads them, writes tidy CSVs, and draws per-species births-by-source / deaths-by-cause stacked
bars with the population overlaid — so you can SEE why a species is below target: food-limited births
vs. predation/starvation deaths, and (the self-maintenance metric) how much of its births come from
the Director's `reseed` safety net (should trend to ~0).

  python3 tools/plot_interactions.py --tag eco              # last run from `docker compose logs`
  python3 tools/plot_interactions.py --log run.log --tag eco  # parse a captured log file instead
  python3 tools/plot_interactions.py --since 10m --tag eco   # bound the docker log window

Outputs (under tools/_generated/ecology_charts/):
  interaction_log_<tag>.csv   day,species,pop,b_*,d_*,avg_sat
  predation_log_<tag>.csv     day,pred,prey,kills
  interactions_<tag>.png      the per-species chart grid
"""
import argparse, csv, os, re, subprocess, sys

BIRTH_SRCS = ["brood", "nest", "reproduce", "reseed", "spawn"]
DEATH_CAUSES = ["oldage", "starve", "predation", "cull"]
# Distinct, legible colors (births = greens/blues, reseed = red = "the safety net is propping it up").
SRC_COLOR = {"brood": "#4caf50", "nest": "#26a69a", "reproduce": "#42a5f5",
             "reseed": "#e53935", "spawn": "#9e9e9e"}
CAUSE_COLOR = {"oldage": "#8d6e63", "starve": "#ffb300", "predation": "#ab47bc", "cull": "#ef5350"}

ECO_RE = re.compile(r"ECOSTATS day=(\d+) sp=(\S+) pop=(\d+) (.*?) avg_sat=([\d.]+)")
KV_RE = re.compile(r"(b_\w+|d_\w+)=(\d+)")
PRED_RE = re.compile(r"PREDLOG day=(\d+) pred=(\S+) prey=(\S+) kills=(\d+)")


def get_log_text(args):
    if args.log:
        return open(args.log, encoding="utf-8", errors="replace").read()
    cmd = ["docker", "compose", "logs", "--no-color"]
    if args.since:
        cmd += ["--since", args.since]
    cmd += ["nakama"]
    return subprocess.run(cmd, cwd=_repo_root(), capture_output=True, text=True).stdout


def _repo_root():
    # tools/ is one level under the repo root.
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse(text):
    """Return (eco_rows, pred_rows) for the LAST run only. A run boundary is a day=1 line that
    appears after we've already seen a day>1 (the lab restarts day-counter on each fresh server)."""
    eco, pred, max_day = [], [], 0
    for line in text.splitlines():
        m = ECO_RE.search(line)
        if m:
            day = int(m.group(1))
            if day == 1 and max_day > 1:  # new run started → drop everything prior
                eco, pred, max_day = [], [], 0
            max_day = max(max_day, day)
            kv = {f"{k}": int(v) for k, v in KV_RE.findall(m.group(4))}
            row = {"day": day, "species": m.group(2), "pop": int(m.group(3)),
                   "avg_sat": float(m.group(5))}
            for s in BIRTH_SRCS:
                row[f"b_{s}"] = kv.get(f"b_{s}", 0)
            for c in DEATH_CAUSES:
                row[f"d_{c}"] = kv.get(f"d_{c}", 0)
            eco.append(row)
            continue
        p = PRED_RE.search(line)
        if p:
            pred.append({"day": int(p.group(1)), "pred": p.group(2),
                         "prey": p.group(3), "kills": int(p.group(4))})
    return eco, pred


def write_csvs(eco, pred, outdir, tag):
    cols = ["day", "species", "pop"] + [f"b_{s}" for s in BIRTH_SRCS] + \
           [f"d_{c}" for c in DEATH_CAUSES] + ["avg_sat"]
    ipath = os.path.join(outdir, f"interaction_log_{tag}.csv")
    with open(ipath, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(sorted(eco, key=lambda r: (r["species"], r["day"])))
    ppath = os.path.join(outdir, f"predation_log_{tag}.csv")
    with open(ppath, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["day", "pred", "prey", "kills"])
        w.writeheader()
        w.writerows(sorted(pred, key=lambda r: (r["day"], r["pred"], r["prey"])))
    return ipath, ppath


def chart(eco, outdir, tag):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed — CSVs written, skipping chart", file=sys.stderr)
        return None

    species = sorted({r["species"] for r in eco})
    if not species:
        print("no ECOSTATS rows found", file=sys.stderr)
        return None
    n = len(species)
    fig, axes = plt.subplots(n, 1, figsize=(11, 2.6 * n), squeeze=False)
    for i, sp in enumerate(species):
        ax = axes[i][0]
        rows = sorted([r for r in eco if r["species"] == sp], key=lambda r: r["day"])
        days = [r["day"] for r in rows]
        # Births stack UP (positive), deaths stack DOWN (negative) — a back-to-back bar per day.
        bot = [0] * len(days)
        for s in BIRTH_SRCS:
            vals = [r[f"b_{s}"] for r in rows]
            if any(vals):
                ax.bar(days, vals, bottom=bot, color=SRC_COLOR[s], width=0.8, label=f"+{s}")
                bot = [b + v for b, v in zip(bot, vals)]
        bot = [0] * len(days)
        for c in DEATH_CAUSES:
            vals = [-r[f"d_{c}"] for r in rows]
            if any(vals):
                ax.bar(days, vals, bottom=bot, color=CAUSE_COLOR[c], width=0.8, label=f"-{c}")
                bot = [b + v for b, v in zip(bot, vals)]
        ax.axhline(0, color="black", lw=0.6)
        # Population + avg-satiation on a twin axis.
        ax2 = ax.twinx()
        ax2.plot(days, [r["pop"] for r in rows], "k-o", ms=3, lw=1.4, label="pop")
        ax2.plot(days, [r["avg_sat"] for r in rows], color="#ff7043", ls=":", lw=1.2, label="avg_sat")
        ax2.set_ylabel("pop / sat")
        ax.set_ylabel("births / deaths")
        ax.set_title(f"{sp}", loc="left", fontsize=10, fontweight="bold")
        ax.legend(loc="upper left", fontsize=6, ncol=5, framealpha=0.6)
        ax2.legend(loc="upper right", fontsize=6, framealpha=0.6)
    axes[-1][0].set_xlabel("game-day")
    fig.suptitle(f"Ecology interactions — {tag}", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.99])
    cpath = os.path.join(outdir, f"interactions_{tag}.png")
    fig.savefig(cpath, dpi=110)
    return cpath


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="eco", help="output filename tag")
    ap.add_argument("--log", help="parse this captured log file instead of docker compose logs")
    ap.add_argument("--since", help="docker logs --since window (e.g. 10m); ignored with --log")
    args = ap.parse_args()

    outdir = os.path.join(_repo_root(), "tools", "_generated", "ecology_charts")
    os.makedirs(outdir, exist_ok=True)

    eco, pred = parse(get_log_text(args))
    if not eco:
        print("No ECOSTATS lines found. Is the server up and was a bug_lab run executed?", file=sys.stderr)
        sys.exit(1)
    ipath, ppath = write_csvs(eco, pred, outdir, args.tag)
    days = sorted({r["day"] for r in eco})
    print(f"parsed {len(eco)} ECOSTATS rows ({len(days)} game-days) + {len(pred)} PREDLOG rows")
    print(f"  {ipath}")
    print(f"  {ppath}")
    cpath = chart(eco, outdir, args.tag)
    if cpath:
        print(f"  {cpath}")


if __name__ == "__main__":
    main()
