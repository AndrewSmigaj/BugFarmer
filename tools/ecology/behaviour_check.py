#!/usr/bin/env python3
"""The behaviour check: does a changed build still make the bugs do what they did before? (docs/plans/village-slice.md,
Stage 1.0.) Unit-tested by tools/ecology/test_behaviour_check.py.

It compares runs of the NEW build against runs of the BASE build, metric by metric and species by species. With only
--base runs it prints the base runs' spread (the noise floor).

Each run is a folder holding what one behaviour run wrote:
  client_behaviour*.csv   the client's behaviour tally (HeadlessSyncTest -behaviour): per species per window, bug-ticks
                          in total and while hunting, landed, eating, fleeing, attacking, curious, winding up and
                          lunging, plus reports made (strikes, prey claimed, corpses eaten), plus how many times a bug
                          started each of those states (the *_starts columns; older files lack them).
  nakama.log              the server log of the run: ECOSTATS (births by source, deaths by cause), PREDLOG (kills),
                          BEHAVSTATS (feeding and breeding bug-ticks, eggs, trips home, nest defences, merges, splits,
                          hits on players), one line per species per game-day.

Metrics (per species):
  client  share of bug-ticks in each state, per 1,000 bug-ticks; starts of each state and reports, per 10,000 bug-ticks
  server  feeding/breeding share of bug-ticks per 1,000; everything else per bug-day (bug-days = the daily populations
          summed); kills per predator bug-day per prey species
Day 1 (the starting spawn) and the first 30 s of client windows are skipped by default.

PAIRED BY SEED (the normal way): when the base and new runs share at least 3 seeds (a run's seed is the "_seed<N>" at
the end of its folder name, as scaling_study.py names them), each seed's new value is compared with the SAME seed's
base value, and only those per-seed differences are judged. A metric is FLAGGED only when the change
  goes the same way on every seed, AND
  its mean is over K standard errors of the per-seed differences (K = 4; or the differences have no spread), AND
  its mean is over MIN_CHANGE of the base mean (15%).
UNPAIRED (fallback, when the seeds don't match): flagged when |new mean - base mean| is over K standard errors of the
difference of the two groups AND over MIN_CHANGE.
TWO STEPS (the owner's choice, 2026-10-07; five seeds alone missed a certain +65% change at 3.7 standard errors):
  step 1, five seeds: besides the FLAG above, a change that goes the same way on every seed, is over 15% and over the
          5% two-sided critical t for the seeds (2.78 for five) is a SUSPECT -> exit 3: run five FRESH seeds of both
          builds, interleaved, and judge all ten with --confirm;
  step 2, --confirm: flagged when the change goes the same way on at least 9 in 10 of the seeds, is over K standard
          errors of the per-seed differences and over 15%. A suspect that fails this is cleared.
Either way, a metric whose events are rare (fewer than MIN_EVENTS counted across the base runs, and across the new
runs) is reported "too rare to judge", never flagged; one that is absent in the base runs but frequent in the new ones
(or the reverse) is flagged as appearing (vanishing). For a client state the events counted are its STARTS when the
file has them (a few bugs holding a state for a long time give many bug-ticks but few separate occurrences).

Why these rules (2026-10-06): the first noise-floor runs (natural ecology, 3 game-days, 5 + 3 seeds of the SAME
build) raised 14 false alarms under a plain "±3 sd or zero on one side" rule: the village's first days go different
ways from seed to seed (in some seeds the flies die out, in others they breed), and rare events (a beetle laying eggs
once) flip between zero and non-zero. So the check runs with the bug count held steady (the hold_population test
zone, docs/plans/village-slice.md Stage 1.0), and judges only clear, sizeable changes in well-counted behaviour.
Tiny exact differences are the equivalence check's job (tools/netcode/equiv_check.py).
Why paired (2026-10-06, the first held-count calibration): a seed sets where everything starts, and that alone moves
some numbers enormously (wasp attacks: none on three seeds, up to 59,000 bug-ticks on others), so comparing group
averages over different seeds raised a false alarm on the same build and missed a real planted change (the food radius
2.5 -> 4.0), which seed by seed was plain: flies landing up and wasp attacks down on every seed.

THE PACE GATE: a run's client pace (ticks per real second, from client_perf.csv after the warm-up) must match between
the two groups within MAX_PACE_DIFF (1%); otherwise the check refuses to judge (exit 2). Why (2026-10-06): runs made
hours apart kept different paces (the machine ran ~1.7% slower in the evening), and a client that falls behind the
zone changes what the bugs do; comparing such runs flagged a 46% drop in fly breeding that the pace alone may explain.
So run the two builds INTERLEAVED, in one session (base seed 1, new seed 1, base seed 2, ...).

A run whose client pace is under 90% of the median of all the runs is named as BROKEN (2026-10-06: one client stuck
in a resync loop from tick 0 kept 2.9 ticks/s and showed up only as a 19% gap between the group means).

Exit codes: 0 = no flags, 1 = flags, 2 = not enough data, or not comparable (the pace gate, or a broken run),
3 = suspects only (step 1): run step 2.

Usage:
  behaviour_check.py --base RUN_DIR [RUN_DIR ...] [--new RUN_DIR ...] [--k 4] [--min-change 0.15]
                     [--min-events 20] [--skip-days 1] [--skip-seconds 30] [--min-bug-ticks 10000] [--unpaired]
                     [--max-pace-diff 0.01] [--confirm] [--out report.md]
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
MIN_PAIRED_SEEDS = 3
CONFIRM_AGREE = 0.9  # step 2: the share of seeds a change must go the same way on
# Two-sided 5% critical values of Student's t by degrees of freedom (seeds - 1): the step-1 SUSPECT bar.
T_CRIT_5PCT = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
               11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 19: 2.093, 24: 2.064, 29: 2.045}


def t_crit(df):
    """The two-sided 5% critical t for df degrees of freedom (the nearest tabulated df at or below; 1.96 past 29)."""
    if df > 29:
        return 1.96
    return T_CRIT_5PCT[max(d for d in T_CRIT_5PCT if d <= df)]
LINE = re.compile(r"(ECOSTATS|BEHAVSTATS|PREDLOG) (day=\d+[^\"\\]*)")


def kv(s):
    return dict(p.split("=", 1) for p in s.split() if "=" in p)


def client_metrics(run_dir, skip_seconds, min_bug_ticks):
    """species -> {metric: value} from the client tally (summed over windows after the warm-up)."""
    sums = defaultdict(lambda: defaultdict(float))
    has_starts = False
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
                    has_starts = has_starts or "landed_starts" in header
                    continue
                if header is None or len(p) != len(header):
                    continue
                row = dict(zip(header, p))
                if float(row["real_s"]) < skip_seconds:
                    continue
                for k in ["bug_ticks"] + CLIENT_STATES + CLIENT_REPORTS + [s + "_starts" for s in CLIENT_STATES]:
                    sums[row["species"]][k] += float(row.get(k, 0) or 0)
    out = {}
    for sp, s in sums.items():
        bt = s["bug_ticks"]
        if bt < min_bug_ticks:
            continue
        # (value, events): a state's events are its starts when the file counts them, else its bug-ticks
        m = {f"client.{k}_per_1k": (1000.0 * s[k] / bt, s[k + "_starts"] if has_starts else s[k]) for k in CLIENT_STATES}
        if has_starts:
            m.update({f"client.{k}_starts_per_10k": (10000.0 * s[k + "_starts"] / bt, s[k + "_starts"])
                      for k in CLIENT_STATES})
        m.update({f"client.{k}_per_10k": (10000.0 * s[k] / bt, s[k]) for k in CLIENT_REPORTS})
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
        m = {f"server.{k}_per_1k": (1000.0 * beh[sp][k] / (bd * DAY_TICKS), beh[sp][k]) for k in BEHAV_SHARES}
        m.update({f"server.{k}_per_bugday": (beh[sp][k] / bd, beh[sp][k]) for k in BEHAV_EVENTS})
        m.update({f"server.{k}_per_bugday": (v / bd, v) for k, v in eco[sp].items()})
        for prey, n in kills.get(sp, {}).items():
            m[f"server.kills_{prey}_per_bugday"] = (n / bd, n)
        out[sp] = m
    return out


def client_pace(run_dir, skip_seconds):
    """Ticks the client simulated per real second after the warm-up (client_perf.csv), or None without the file."""
    path = os.path.join(run_dir, "client_perf.csv")
    if not os.path.exists(path):
        return None
    ticks = secs = 0.0
    prev = None
    with open(path, encoding="utf-8") as f:
        header = f.readline().strip().split(",")
        for line in f:
            row = dict(zip(header, line.strip().split(",")))
            try:
                real, n = float(row["real_s"]), float(row["ticks"])
            except (KeyError, ValueError):
                continue
            if prev is not None and real >= skip_seconds:
                ticks += n
                secs += real - prev
            prev = real
    return ticks / secs if secs > 0 else None


def run_metrics(run_dir, args):
    m = defaultdict(dict)
    for sp, d in client_metrics(run_dir, args.skip_seconds, args.min_bug_ticks).items():
        m[sp].update(d)
    for sp, d in server_metrics(run_dir, args.skip_days).items():
        m[sp].update(d)
    return m


SEED = re.compile(r"_seed(\d+)$")


def seed_of(run_dir):
    m = SEED.search(os.path.basename(os.path.normpath(run_dir)))
    return int(m.group(1)) if m else None


def pairing(base_dirs, new_dirs):
    """The seeds to pair on (sorted), or None when the runs can't be paired (a run without a seed, a new seed missing
    from the base runs, or fewer than MIN_PAIRED_SEEDS shared seeds)."""
    bs, ns = [seed_of(d) for d in base_dirs], [seed_of(d) for d in new_dirs]
    if not ns or None in bs or None in ns or not set(ns) <= set(bs):
        return None
    common = sorted(set(ns))
    return common if len(common) >= MIN_PAIRED_SEEDS else None


def mean_sd(xs):
    n = len(xs)
    mu = sum(xs) / n
    sd = math.sqrt(sum((x - mu) ** 2 for x in xs) / (n - 1)) if n > 1 else 0.0
    return mu, sd


def rarity(b_events, n_events, mu, nmu, min_events):
    """-> (note, flagged) when the events are too few to judge the usual way, else None."""
    if b_events < min_events and n_events < min_events:
        return "too rare to judge", False
    if b_events < min_events <= n_events and mu == 0:
        return "appears", True
    if n_events < min_events <= b_events and nmu == 0:
        return "vanishes", True
    return None


def pct(new, base):
    return f"{100 * (new - base) / base:+.0f}%" if base else "from 0"


def compare_paired(base_runs, base_seeds, new_runs, new_seeds, seeds, k, min_change, min_events, confirm=False):
    """Per-seed differences. -> rows (species, metric, base_mean, sd of the per-seed differences, new_mean, flagged,
    note). Step 1 (confirm=False): flagged = all seeds one way + over k se + over min_change; a SUSPECT (note starts
    "SUSPECT") = all seeds one way + over the 5% critical t + over min_change. Step 2 (confirm=True): flagged = at
    least CONFIRM_AGREE of the seeds one way + over k se + over min_change."""
    rows = []
    species = sorted({sp for r in base_runs + new_runs for sp in r})
    for sp in species:
        metrics = sorted({mt for r in base_runs + new_runs for mt in r.get(sp, {})})
        for mt in metrics:
            b_vals, n_vals, b_events, n_events = [], [], 0.0, 0.0
            for s in seeds:
                b = [r.get(sp, {}).get(mt, (0.0, 0.0)) for r, rs in zip(base_runs, base_seeds) if rs == s]
                n = [r.get(sp, {}).get(mt, (0.0, 0.0)) for r, rs in zip(new_runs, new_seeds) if rs == s]
                b_vals.append(sum(x[0] for x in b) / len(b))
                n_vals.append(sum(x[0] for x in n) / len(n))
                b_events += sum(x[1] for x in b)
                n_events += sum(x[1] for x in n)
            mu, nmu = sum(b_vals) / len(b_vals), sum(n_vals) / len(n_vals)
            d = [nv - bv for nv, bv in zip(n_vals, b_vals)]
            dmu, dsd = mean_sd(d)
            se = dsd / math.sqrt(len(d))
            rare = rarity(b_events, n_events, mu, nmu, min_events)
            if rare:
                why, flag = rare
            else:
                up, down = sum(1 for x in d if x > 0), sum(1 for x in d if x < 0)
                need = math.ceil(CONFIRM_AGREE * len(d)) if confirm else len(d)
                one_way = max(up, down) >= need
                clear = se == 0 and dmu != 0 or se > 0 and abs(dmu) > k * se
                big = abs(dmu) > min_change * abs(mu)
                flag = one_way and clear and big
                suspect = (not confirm and not flag and one_way and big
                           and (se == 0 and dmu != 0 or se > 0 and abs(dmu) > t_crit(len(d) - 1) * se))
                spread = f"{abs(dmu) / se:.1f} se" if se > 0 else "no spread"
                label = "changed" if flag else ("SUSPECT" if suspect else "")
                why = f"{label} {pct(nmu, mu)}, {up} up / {down} down of {len(d)} seeds, {spread}".strip()
            rows.append((sp, mt, mu, dsd, nmu, flag, why))
    return rows


def compare(base_runs, new_runs, k, min_change, min_events):
    """Unpaired (group means). -> rows (species, metric, base_mean, base_sd, new_mean, flagged, note)."""
    rows = []
    species = sorted({sp for r in base_runs + new_runs for sp in r})
    for sp in species:
        metrics = sorted({mt for r in base_runs + new_runs for mt in r.get(sp, {})})
        for mt in metrics:
            b = [r.get(sp, {}).get(mt, (0.0, 0.0)) for r in base_runs]
            mu, sd = mean_sd([x[0] for x in b])
            b_events = sum(x[1] for x in b)
            if not new_runs:
                rows.append((sp, mt, mu, sd, None, False, "rare" if b_events < min_events else ""))
                continue
            nv = [r.get(sp, {}).get(mt, (0.0, 0.0)) for r in new_runs]
            nmu, nsd = mean_sd([x[0] for x in nv])
            n_events = sum(x[1] for x in nv)
            why, flag = "", False
            rare = rarity(b_events, n_events, mu, nmu, min_events)
            if rare:
                why, flag = rare
            else:
                se = math.sqrt(sd * sd / len(b) + nsd * nsd / len(nv))
                diff = abs(nmu - mu)
                if diff > k * se + 1e-12 and diff > min_change * abs(mu):
                    why, flag = (f"changed {pct(nmu, mu)} ({diff / se:.1f} se)" if se > 0
                                 else f"changed {pct(nmu, mu)} (no spread)"), True
            rows.append((sp, mt, mu, sd, nmu, flag, why))
    return rows


def fmt(x):
    return "" if x is None else (f"{x:.4g}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base", nargs="+", required=True)
    ap.add_argument("--new", nargs="*", default=[])
    ap.add_argument("--k", type=float, default=4.0, help="standard errors of the difference a change must exceed")
    ap.add_argument("--min-change", type=float, default=0.15, help="smallest relative change that counts (0.15 = 15%%)")
    ap.add_argument("--min-events", type=float, default=20, help="fewer counted events than this = too rare to judge")
    ap.add_argument("--skip-days", type=int, default=1)
    ap.add_argument("--skip-seconds", type=float, default=30.0)
    ap.add_argument("--min-bug-ticks", type=float, default=10000.0)
    ap.add_argument("--unpaired", action="store_true", help="compare group means even when the seeds match")
    ap.add_argument("--confirm", action="store_true", help="step 2: judge the step-1 and fresh seeds together")
    ap.add_argument("--max-pace-diff", type=float, default=0.01,
                    help="the largest relative difference in client pace between the groups (0.01 = 1%%)")
    ap.add_argument("--out")
    args = ap.parse_args(argv)

    base = [run_metrics(d, args) for d in args.base]
    new = [run_metrics(d, args) for d in args.new]
    if len(base) < 2 or any(not r for r in base + new):
        print("not enough data: need at least two base runs, and every run must have metrics "
              f"(base runs with data: {sum(1 for r in base if r)}, new: {sum(1 for r in new if r)})")
        return 2
    if new:
        paces = {d: client_pace(d, args.skip_seconds) for d in args.base + args.new}
        known = sorted(v for v in paces.values() if v)
        if known:
            median = known[len(known) // 2]
            slow = [(d, v) for d, v in paces.items() if v and v < 0.9 * median]
            for d, v in slow:  # 2026-10-06: one client stuck in a resync loop kept 2.9 ticks/s and hid in a group mean
                print(f"BROKEN RUN: {d} kept {v:.1f} ticks/s against the runs' median {median:.1f} — check its "
                      f"player.log (a resync loop?) and run that seed again")
            if slow:
                return 2
        bp = [x for x in (paces[d] for d in args.base) if x]
        np_ = [x for x in (paces[d] for d in args.new) if x]
        if bp and np_:
            bmu, nmu = sum(bp) / len(bp), sum(np_) / len(np_)
            diff = abs(nmu - bmu) / bmu
            print(f"client pace: base {bmu:.2f}, new {nmu:.2f} ticks/s ({100 * diff:.2f}% apart)")
            if diff > args.max_pace_diff:
                print(f"NOT COMPARABLE: the client kept a different pace in the two groups (over "
                      f"{100 * args.max_pace_diff:g}%), which changes what the bugs do by itself. Run the two builds "
                      f"interleaved, in one session.")
                return 2
        else:
            print("client pace: not recorded (no client_perf.csv), so the pace gate could not run")
    seeds = None if args.unpaired else pairing(args.base, args.new)
    if seeds:
        rows = compare_paired(base, [seed_of(d) for d in args.base], new, [seed_of(d) for d in args.new], seeds,
                              args.k, args.min_change, args.min_events, confirm=args.confirm)
        mode, spread_col = f"paired by seed ({', '.join(map(str, seeds))})", "sd of per-seed differences"
    else:
        rows = compare(base, new, args.k, args.min_change, args.min_events)
        mode = "unpaired: group means; seed differences count as noise" if new else "noise floor"
        spread_col = "base sd"
    flagged = [r for r in rows if r[5]]
    suspects = [r for r in rows if not r[5] and r[6].startswith("SUSPECT")]
    lines = [f"| species | metric | base mean | {spread_col} | new mean | flag |", "|---|---|---|---|---|---|"]
    for sp, mt, mu, sd, nmu, fl, why in rows:
        lines.append(f"| {sp} | {mt} | {fmt(mu)} | {fmt(sd)} | {fmt(nmu)} | {'**FLAG** ' if fl else ''}{why} |")
    summary = (f"{len(rows)} metrics over {len(base)} base run(s)"
               + (f" and {len(new)} new run(s), {mode}: {len(flagged)} flagged" if new else " (noise floor only)"))
    text = "\n".join(lines) + "\n\n" + summary + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
    print(text if not args.out else summary + f"(table: {args.out})")
    for sp, mt, mu, sd, nmu, fl, why in flagged:
        print(f"FLAG {sp} {mt}: base {fmt(mu)} ± {fmt(sd)}, new {fmt(nmu)} ({why})")
    for sp, mt, mu, sd, nmu, fl, why in suspects:
        print(f"SUSPECT {sp} {mt}: base {fmt(mu)}, new {fmt(nmu)} ({why})")
    if suspects and not flagged:
        print(f"{len(suspects)} suspect(s): step 2 — run five FRESH seeds of both builds, interleaved, then judge all the "
              f"seeds together with --confirm")
    if new:
        rare = sum(1 for r in rows if r[6] == "too rare to judge")
        rule = ("is over" if not seeds else
                f"goes the same way on at least {100 * CONFIRM_AGREE:.0f}% of the seeds, is over" if args.confirm else
                "goes the same way on every seed, is over")
        print(f"({rare} metrics too rare to judge; a change counts when it {rule} {args.k:g} standard errors AND over "
              f"{100 * args.min_change:.0f}%)")
    return 1 if flagged else (3 if suspects else 0)


if __name__ == "__main__":
    sys.exit(main())
