#!/usr/bin/env python3
"""The behaviour check: does a changed build still make the bugs do what they did before? (docs/plans/village-slice.md,
Stage 1.0.) Unit-tested by tools/ecology/test_behaviour_check.py.

It compares runs of the NEW build against several runs (seeds) of the BASE build, metric by metric and species by
species, using the base runs' own spread as the noise floor. With only --base runs it prints that noise floor.

Each run is a folder holding what one behaviour run wrote:
  client_behaviour*.csv   the client's behaviour tally (HeadlessSyncTest -behaviour): per species per window, bug-ticks
                          in total and while hunting, landed, eating, fleeing, attacking, curious, winding up and
                          lunging, plus reports made (strikes, prey claimed, corpses eaten).
  nakama.log              the server log of the run: ECOSTATS (births by source, deaths by cause), PREDLOG (kills),
                          BEHAVSTATS (feeding and breeding bug-ticks, eggs, trips home, nest defences, merges, splits,
                          hits on players), one line per species per game-day.

Metrics (per species):
  client  share of bug-ticks in each state, per 1,000 bug-ticks; reports per 10,000 bug-ticks
  server  feeding/breeding share of bug-ticks per 1,000; everything else per bug-day (bug-days = the daily populations
          summed); kills per predator bug-day per prey species
Day 1 (the starting spawn) and the first 30 s of client windows are skipped by default.

A metric is FLAGGED when the new mean is outside the base mean ± K standard deviations (K = 3), or when it is zero on
one side and not on the other. Exit codes: 0 = no flags, 1 = flags, 2 = not enough data.

Usage:
  behaviour_check.py --base RUN_DIR [RUN_DIR ...] [--new RUN_DIR ...] [--k 3] [--skip-days 1] [--skip-seconds 30]
                     [--min-bug-ticks 10000] [--out report.md]
"""
import argparse
import glob
import math
import os
import re
import sys
from collections import defaultdict

CLIENT_STATES = ["hunting", "landed", "eating", "flee", "attack", "curious", "windup", "lunge"]
CLIENT_REPORTS = ["strikes", "prey_claimed", "corpses"]
BEHAV_SHARES = ["feed", "breed"]
BEHAV_EVENTS = ["eggs", "trip_home", "trip_abandon", "nest_defend", "merge", "split", "player_hit"]
DAY_TICKS = 8400
LINE = re.compile(r"(ECOSTATS|BEHAVSTATS|PREDLOG) (day=\d+[^\"\\]*)")


def kv(s):
    return dict(p.split("=", 1) for p in s.split() if "=" in p)


def client_metrics(run_dir, skip_seconds, min_bug_ticks):
    """species -> {metric: value} from the client tally (summed over windows after the warm-up)."""
    sums = defaultdict(lambda: defaultdict(float))
    files = sorted(glob.glob(os.path.join(run_dir, "client_behaviour*.csv")))
    for path in files:
        with open(path, encoding="utf-8") as f:
            header = None
            for line in f:
                p = line.strip().split(",")
                if not p or not p[0]:
                    continue
                if p[0] == "real_s":
                    header = p
                    continue
                if header is None or len(p) != len(header):
                    continue
                row = dict(zip(header, p))
                if float(row["real_s"]) < skip_seconds:
                    continue
                for k in ["bug_ticks"] + CLIENT_STATES + CLIENT_REPORTS:
                    sums[row["species"]][k] += float(row.get(k, 0) or 0)
    out = {}
    for sp, s in sums.items():
        bt = s["bug_ticks"]
        if bt < min_bug_ticks:
            continue
        m = {f"client.{k}_per_1k": 1000.0 * s[k] / bt for k in CLIENT_STATES}
        m.update({f"client.{k}_per_10k": 10000.0 * s[k] / bt for k in CLIENT_REPORTS})
        out[sp] = m
    return out


def server_metrics(run_dir, skip_days):
    """species -> {metric: value} from ECOSTATS / BEHAVSTATS / PREDLOG in the run's server log."""
    path = os.path.join(run_dir, "nakama.log")
    if not os.path.exists(path):
        return {}
    pop = defaultdict(float)                         # species -> bug-days
    eco = defaultdict(lambda: defaultdict(float))    # species -> b_*/d_* totals
    beh = defaultdict(lambda: defaultdict(float))
    kills = defaultdict(lambda: defaultdict(float))  # pred -> prey -> kills
    seen = set()                                     # (kind, day, sp[, prey]) — a line logged twice counts once
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = LINE.search(line)
            if not m:
                continue
            kind, d = m.group(1), kv(m.group(2))
            day = int(d["day"])
            if day <= skip_days:
                continue
            if kind == "PREDLOG":
                key = (kind, day, d["pred"], d["prey"])
                if key in seen:
                    continue
                seen.add(key)
                kills[d["pred"]][d["prey"]] += float(d["kills"])
                continue
            key = (kind, day, d["sp"])
            if key in seen:
                continue
            seen.add(key)
            sp = d["sp"]
            if kind == "ECOSTATS":
                pop[sp] += float(d["pop"])
                for k, v in d.items():
                    if k.startswith(("b_", "d_")):
                        eco[sp][k] += float(v)
            else:
                for k in BEHAV_SHARES + BEHAV_EVENTS:
                    beh[sp][k] += float(d.get(k, 0))
    out = {}
    for sp, bd in pop.items():
        if bd <= 0:
            continue
        m = {f"server.{k}_per_1k": 1000.0 * beh[sp][k] / (bd * DAY_TICKS) for k in BEHAV_SHARES}
        m.update({f"server.{k}_per_bugday": beh[sp][k] / bd for k in BEHAV_EVENTS})
        m.update({f"server.{k}_per_bugday": v / bd for k, v in eco[sp].items()})
        for prey, n in kills.get(sp, {}).items():
            m[f"server.kills_{prey}_per_bugday"] = n / bd
        out[sp] = m
    return out


def run_metrics(run_dir, args):
    m = defaultdict(dict)
    for sp, d in client_metrics(run_dir, args.skip_seconds, args.min_bug_ticks).items():
        m[sp].update(d)
    for sp, d in server_metrics(run_dir, args.skip_days).items():
        m[sp].update(d)
    return m


def mean_sd(xs):
    n = len(xs)
    mu = sum(xs) / n
    sd = math.sqrt(sum((x - mu) ** 2 for x in xs) / (n - 1)) if n > 1 else 0.0
    return mu, sd


def compare(base_runs, new_runs, k):
    """-> rows (species, metric, base_mean, base_sd, new_mean, flagged, why)."""
    rows = []
    species = sorted({sp for r in base_runs + new_runs for sp in r})
    for sp in species:
        metrics = sorted({mt for r in base_runs + new_runs for mt in r.get(sp, {})})
        for mt in metrics:
            b = [r.get(sp, {}).get(mt, 0.0) for r in base_runs]
            mu, sd = mean_sd(b)
            if not new_runs:
                rows.append((sp, mt, mu, sd, None, False, ""))
                continue
            nv = [r.get(sp, {}).get(mt, 0.0) for r in new_runs]
            nmu, _ = mean_sd(nv)
            why = ""
            if (mu == 0) != (nmu == 0) and (abs(mu) > 0 or abs(nmu) > 0):
                why = "zero on one side only"
            elif abs(nmu - mu) > k * sd + 1e-12:
                why = f"outside base ±{k:g}sd"
            rows.append((sp, mt, mu, sd, nmu, bool(why), why))
    return rows


def fmt(x):
    return "" if x is None else (f"{x:.4g}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base", nargs="+", required=True)
    ap.add_argument("--new", nargs="*", default=[])
    ap.add_argument("--k", type=float, default=3.0)
    ap.add_argument("--skip-days", type=int, default=1)
    ap.add_argument("--skip-seconds", type=float, default=30.0)
    ap.add_argument("--min-bug-ticks", type=float, default=10000.0)
    ap.add_argument("--out")
    args = ap.parse_args(argv)

    base = [run_metrics(d, args) for d in args.base]
    new = [run_metrics(d, args) for d in args.new]
    if len(base) < 2 or any(not r for r in base + new):
        print("not enough data: need at least two base runs, and every run must have metrics "
              f"(base runs with data: {sum(1 for r in base if r)}, new: {sum(1 for r in new if r)})")
        return 2
    rows = compare(base, new, args.k)
    flagged = [r for r in rows if r[5]]
    lines = ["| species | metric | base mean | base sd | new mean | flag |", "|---|---|---|---|---|---|"]
    for sp, mt, mu, sd, nmu, fl, why in rows:
        lines.append(f"| {sp} | {mt} | {fmt(mu)} | {fmt(sd)} | {fmt(nmu)} | {why} |")
    summary = (f"{len(rows)} metrics over {len(base)} base run(s)"
               + (f" and {len(new)} new run(s): {len(flagged)} flagged" if new else " (noise floor only)"))
    text = "\n".join(lines) + "\n\n" + summary + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
    print(text if not args.out else summary + f"(table: {args.out})")
    for sp, mt, mu, sd, nmu, fl, why in flagged:
        print(f"FLAG {sp} {mt}: base {fmt(mu)} ± {fmt(sd)}, new {fmt(nmu)} ({why})")
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
