#!/usr/bin/env python3
"""The equivalence check: do two test players — one on the OLD build, one on the NEW — compute the same bugs and make
the same decisions, tick for tick? (docs/plans/village-slice.md, Stage 1.0.) Unit-tested by test_equiv_check.py.

Why it exists: the headless determinism replay (tools/sim-determinism) has no food, no walls and no SwarmManager, so
it can't prove that an optimisation of the client's bug simulation left the results unchanged. Two builds in ONE
live run can: both replay the same server ledger, so any difference in what they compute is a difference between the
builds. Run it both ways round (old build in charge, then new). It only holds for builds with the same snapshot and
message formats (the late-joiner reads the other build's snapshot).

Inputs (written by the headless player, HeadlessSyncTest):
  hashlog_<id>.csv  (-hashlog)   header `tick,hash,full,bugs,live`; one row per simulated tick; marker lines
                                 `#live,<tick>`, `#replay,<tick>`, `#resync,<tick>`, `#timeout,<tick>`.
                                 `hash` = the game's own state check; `full` = a test-only check over each bug's whole
                                 record (landing, random state, movement intent, alert, behaviour, corpse id too).
  reports_<id>.csv  (-reportlog on the one in charge, -shadowreports on the other)
                                 header `tick,kind,a,b,ids,sent`; kinds: `detect` (what each predator could strike this
                                 tick, before the local report throttle), `strike` (what was sent, or would have been),
                                 `corpse` (corpses eaten); the same marker lines.

Rules (each from the cold review of 2026-10-06):
  - A tick seen twice (a replay re-runs ticks) keeps its FIRST value, so a later replay can't overwrite a divergence.
  - A resync or timeout anywhere, or a replay after the first live tick, makes the run INCONCLUSIVE, never a pass:
    a resync copies the other computer's state and would hide a difference.
  - Hashes are compared over every tick both computers simulated live; reports from the later of the two first live
    ticks plus a warm-up (a joiner's first live tick drains stale corpse flags).
  - By default reports are compared on `detect` and `corpse`, not `strike`: each computer paces its strike reports with
    a local, report-only throttle (one per predator per cooldown) that starts empty on a late joiner, so the same
    strikes come out at shifted ticks for as long as the predator keeps striking (seen 2026-10-06). Detections depend
    only on the simulated state, so they must match exactly.
  - A window too short, or with no reports at all when reports are given, is INCONCLUSIVE (a quiet run proves nothing).

Usage:
  equiv_check.py HASH_A HASH_B [--reports REP_A REP_B] [--warmup TICKS] [--min-ticks N] [--min-reports N]
Exit codes: 0 = identical, 1 = diverged, 2 = inconclusive.
"""
import argparse
import collections
import sys

INCONCLUSIVE_MARKERS = ("resync", "timeout")


class Log:
    """One computer's log: first value per tick, the live flags, and the markers in order."""

    def __init__(self):
        self.rows = {}          # tick -> tuple of compared fields (first seen wins)
        self.live = {}          # tick -> bool (first seen wins)
        self.markers = []       # (kind, tick) in file order
        self.reports = collections.defaultdict(list)  # tick -> [report keys] (reports file)

    def first_live(self):
        for kind, tick in self.markers:
            if kind == "live":
                return tick
        live_ticks = [t for t, v in self.live.items() if v]
        return min(live_ticks) if live_ticks else None

    def problems(self):
        """Markers that make the run inconclusive, as readable strings."""
        out, seen_live = [], False
        for kind, tick in self.markers:
            if kind in INCONCLUSIVE_MARKERS:
                out.append(f"{kind} at tick {tick}")
            if kind == "live":
                seen_live = True
            elif kind == "replay" and seen_live:
                out.append(f"replay after going live, at tick {tick} (a resync)")
        return out


def _marker(line, log):
    kind, _, tick = line[1:].strip().partition(",")
    try:
        log.markers.append((kind, int(tick)))
    except ValueError:
        pass


def load_hashlog(path):
    log = Log()
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("tick,"):
                continue
            if line.startswith("#"):
                _marker(line, log)
                continue
            p = line.split(",")
            if len(p) < 5 or not p[0].lstrip("-").isdigit():
                continue
            tick = int(p[0])
            if tick not in log.rows:  # first value wins
                log.rows[tick] = (p[1], p[2], p[3])
                log.live[tick] = p[4] == "1"
    return log


def load_reports(path, kinds=("detect", "corpse")):
    log = Log()
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("tick,"):
                continue
            if line.startswith("#"):
                _marker(line, log)
                continue
            p = line.split(",")
            if len(p) < 6 or not p[0].isdigit():
                continue
            if p[1] not in kinds:
                continue
            # the key ignores `sent` (one computer sends, the other only logs)
            log.reports[int(p[0])].append((p[1], p[2], p[3], p[4]))
    return log


def compare_hashes(a, b, min_ticks):
    """-> (status, message). Compares ticks both simulated live, from the later first-live tick on."""
    fa, fb = a.first_live(), b.first_live()
    if fa is None or fb is None:
        return 2, "a computer never went live"
    start = max(fa, fb)
    common = sorted(t for t in a.rows.keys() & b.rows.keys() if t >= start and a.live.get(t) and b.live.get(t))
    if len(common) < min_ticks:
        return 2, f"only {len(common)} live ticks in common (need {min_ticks})"
    names = ("state check", "full-record check", "bug count")
    for t in common:
        ra, rb = a.rows[t], b.rows[t]
        for i, name in enumerate(names):
            if ra[i] != rb[i]:
                return 1, f"first difference at tick {t}: {name} {ra[i]} vs {rb[i]}"
    return 0, f"{len(common)} live ticks identical (ticks {common[0]}..{common[-1]})"


def compare_reports(a, b, warmup, min_reports, last_common_tick):
    first = [x for x in (a.first_live(), b.first_live()) if x is not None]
    if len(first) < 2:
        return 2, "a reports log has no live tick"
    start = max(first) + warmup
    ticks = sorted(t for t in set(a.reports) | set(b.reports) if start <= t <= last_common_tick)
    n = 0
    for t in ticks:
        ra, rb = sorted(a.reports.get(t, [])), sorted(b.reports.get(t, []))
        if ra != rb:
            return 1, f"first report difference at tick {t}: {ra} vs {rb}"
        n += len(ra)
    if n < min_reports:
        return 2, f"only {n} reports in the compared window (need {min_reports}) — too quiet to prove anything"
    return 0, f"{n} reports identical (ticks {start}..{last_common_tick})"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("hash_a")
    ap.add_argument("hash_b")
    ap.add_argument("--reports", nargs=2, metavar=("REP_A", "REP_B"))
    ap.add_argument("--warmup", type=int, default=100, help="ticks after the later first-live tick before reports count")
    ap.add_argument("--min-ticks", type=int, default=300)
    ap.add_argument("--min-reports", type=int, default=1)
    ap.add_argument("--kinds", default="detect,corpse", help="report kinds to compare (strike is paced by a local throttle)")
    args = ap.parse_args(argv)

    a, b = load_hashlog(args.hash_a), load_hashlog(args.hash_b)
    status = 0
    problems = [f"A: {p}" for p in a.problems()] + [f"B: {p}" for p in b.problems()]
    hs, hmsg = compare_hashes(a, b, args.min_ticks)
    print(f"hashes:  {hmsg}")
    status = max(status, hs) if hs != 1 else 1

    if args.reports:
        kinds = tuple(k for k in args.kinds.split(",") if k)
        ra, rb = load_reports(args.reports[0], kinds), load_reports(args.reports[1], kinds)
        problems += [f"A reports: {p}" for p in ra.problems()] + [f"B reports: {p}" for p in rb.problems()]
        last = min(max(a.rows, default=0), max(b.rows, default=0))
        rs, rmsg = compare_reports(ra, rb, args.warmup, args.min_reports, last)
        print(f"reports: {rmsg}")
        if rs == 1:
            status = 1
        elif status != 1:
            status = max(status, rs)

    if problems:
        print("inconclusive events: " + "; ".join(problems))
        if status != 1:
            status = 2
    print({0: "EQUIVALENT: IDENTICAL", 1: "EQUIVALENT: DIVERGED", 2: "EQUIVALENT: INCONCLUSIVE"}[status])
    return status


if __name__ == "__main__":
    sys.exit(main())
