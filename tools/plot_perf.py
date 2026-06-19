#!/usr/bin/env python3
"""Parse the PERFSTATS / PERFSYS cost-profiler log out of the nakama container logs and chart it.

The "what costs what" telemetry for performance work (BACKLOG #88). With the zone's `profile` flag on,
the server emits once per game-day at the day rollover (see nakama/.../profiler.go):
  PERFSTATS day=N sp=… swarms=… bugs=… cpu_food_us=… cpu_pred_us=… cpu_action_us=…
            food_calls=… pred_thinks=… legs=…              (one line per species)
  PERFSYS   day=N sys_merge_us=… sys_decay_us=… sys_forage_us=… sys_nests_us=…
            influence_bytes=… influence_msgs=… roster_bytes=… roster_msgs=…   (one global line)

This reads them, writes tidy CSVs, and draws: per-species server-CPU by sub-phase + legs (the network
driver); the global per-tick passes + broadcast bytes; and — the key chart — CPU-per-bug vs. average
swarm size, which shows fewer/fatter swarms cost proportionally less per visible bug.

  python3 tools/plot_perf.py --tag perf               # last run from `docker compose logs`
  python3 tools/plot_perf.py --log run.log --tag perf  # parse a captured log file instead

Outputs (under tools/_generated/ecology_charts/):
  perf_log_<tag>.csv   day,species,swarms,bugs,cpu_food_us,cpu_pred_us,cpu_action_us,food_calls,pred_thinks,legs
  perf_sys_<tag>.csv   day,sys_merge_us,…,influence_bytes,influence_msgs,roster_bytes,roster_msgs
  perf_<tag>.png       the per-species + system + cost-vs-size chart grid
"""
import argparse, csv, os, re, subprocess, sys

CPU_PHASES = ["food", "pred", "action"]          # per-species server-CPU sub-phases (µs)
COUNTERS = ["food_calls", "pred_thinks", "legs"]  # per-species call/leg counts
SYS_PHASES = ["merge", "decay", "forage", "nests"]  # global per-tick passes (µs)
SYS_BYTES = ["influence_bytes", "influence_msgs", "roster_bytes", "roster_msgs"]

PHASE_COLOR = {"food": "#42a5f5", "pred": "#ab47bc", "action": "#ffb300"}
SYS_COLOR = {"merge": "#ef5350", "decay": "#8d6e63", "forage": "#4caf50", "nests": "#26a69a"}
# A stable per-species color so the cost-vs-size scatter is readable across species.
SP_COLOR = ["#e53935", "#42a5f5", "#4caf50", "#ffb300", "#ab47bc", "#26a69a", "#8d6e63", "#ec407a"]

PERF_RE = re.compile(r"PERFSTATS day=(\d+) sp=(\S+) (.*)")
SYS_RE = re.compile(r"PERFSYS day=(\d+) (.*)")
KV_RE = re.compile(r"(\w+)=(\d+)")


def _repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_log_text(args):
    if args.log:
        return open(args.log, encoding="utf-8", errors="replace").read()
    cmd = ["docker", "compose", "logs", "--no-color"]
    if args.since:
        cmd += ["--since", args.since]
    cmd += ["nakama"]
    return subprocess.run(cmd, cwd=_repo_root(), capture_output=True, text=True).stdout


def parse(text):
    """Return (perf_rows, sys_rows) for the LAST run only — a day=1 line after a day>1 is a fresh
    server (the lab restarts the day counter), so everything prior is dropped (cross-run guard)."""
    perf, sysr, max_day = [], [], 0
    for line in text.splitlines():
        m = PERF_RE.search(line)
        if m:
            day = int(m.group(1))
            if day == 1 and max_day > 1:
                perf, sysr, max_day = [], [], 0
            max_day = max(max_day, day)
            kv = {k: int(v) for k, v in KV_RE.findall(m.group(3))}
            row = {"day": day, "species": m.group(2),
                   "swarms": kv.get("swarms", 0), "bugs": kv.get("bugs", 0)}
            for ph in CPU_PHASES:
                row[f"cpu_{ph}_us"] = kv.get(f"cpu_{ph}_us", 0)
            for c in COUNTERS:
                row[c] = kv.get(c, 0)
            perf.append(row)
            continue
        s = SYS_RE.search(line)
        if s:
            kv = {k: int(v) for k, v in KV_RE.findall(s.group(2))}
            row = {"day": int(s.group(1))}
            for ph in SYS_PHASES:
                row[f"sys_{ph}_us"] = kv.get(f"sys_{ph}_us", 0)
            for b in SYS_BYTES:
                row[b] = kv.get(b, 0)
            sysr.append(row)
    return perf, sysr


def write_csvs(perf, sysr, outdir, tag):
    pcols = ["day", "species", "swarms", "bugs"] + [f"cpu_{p}_us" for p in CPU_PHASES] + COUNTERS
    ppath = os.path.join(outdir, f"perf_log_{tag}.csv")
    with open(ppath, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=pcols)
        w.writeheader()
        w.writerows(sorted(perf, key=lambda r: (r["species"], r["day"])))
    scols = ["day"] + [f"sys_{p}_us" for p in SYS_PHASES] + SYS_BYTES
    spath = os.path.join(outdir, f"perf_sys_{tag}.csv")
    with open(spath, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=scols)
        w.writeheader()
        w.writerows(sorted(sysr, key=lambda r: r["day"]))
    return ppath, spath


def chart(perf, sysr, outdir, tag):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed — CSVs written, skipping chart", file=sys.stderr)
        return None

    species = sorted({r["species"] for r in perf})
    if not species:
        print("no PERFSTATS rows found", file=sys.stderr)
        return None
    spcol = {sp: SP_COLOR[i % len(SP_COLOR)] for i, sp in enumerate(species)}

    n = len(species)
    # n per-species CPU panels + 1 system panel + 1 cost-vs-size scatter.
    fig, axes = plt.subplots(n + 2, 1, figsize=(11, 2.6 * (n + 2)), squeeze=False)

    for i, sp in enumerate(species):
        ax = axes[i][0]
        rows = sorted([r for r in perf if r["species"] == sp], key=lambda r: r["day"])
        days = [r["day"] for r in rows]
        bot = [0] * len(days)
        for ph in CPU_PHASES:
            vals = [r[f"cpu_{ph}_us"] for r in rows]
            if any(vals):
                ax.bar(days, vals, bottom=bot, color=PHASE_COLOR[ph], width=0.8, label=f"cpu_{ph}")
                bot = [b + v for b, v in zip(bot, vals)]
        ax.set_ylabel("server µs/day")
        ax2 = ax.twinx()
        ax2.plot(days, [r["legs"] for r in rows], "k-o", ms=3, lw=1.3, label="legs")
        ax2.plot(days, [r["bugs"] for r in rows], color="#90a4ae", ls=":", lw=1.2, label="bugs")
        ax2.set_ylabel("legs / bugs")
        ax.set_title(f"{sp}", loc="left", fontsize=10, fontweight="bold", color=spcol[sp])
        ax.legend(loc="upper left", fontsize=6, ncol=3, framealpha=0.6)
        ax2.legend(loc="upper right", fontsize=6, framealpha=0.6)

    # System passes + broadcast bytes (global, not per-species).
    axs = axes[n][0]
    if sysr:
        srows = sorted(sysr, key=lambda r: r["day"])
        days = [r["day"] for r in srows]
        bot = [0] * len(days)
        for ph in SYS_PHASES:
            vals = [r[f"sys_{ph}_us"] for r in srows]
            if any(vals):
                axs.bar(days, vals, bottom=bot, color=SYS_COLOR[ph], width=0.8, label=f"sys_{ph}")
                bot = [b + v for b, v in zip(bot, vals)]
        axs.set_ylabel("server µs/day")
        axs2 = axs.twinx()
        axs2.plot(days, [r["influence_bytes"] / 1024 for r in srows], color="#5c6bc0", lw=1.4, label="leg KB")
        axs2.plot(days, [r["roster_bytes"] / 1024 for r in srows], color="#ff7043", lw=1.4, label="roster KB")
        axs2.set_ylabel("broadcast KB/day")
        axs2.legend(loc="upper right", fontsize=6, framealpha=0.6)
    axs.set_title("system passes + broadcast bytes (global)", loc="left", fontsize=10, fontweight="bold")
    axs.legend(loc="upper left", fontsize=6, ncol=4, framealpha=0.6)

    # Cost-vs-size: CPU-per-bug vs avg swarm size (the "fatter swarms cost less per bug" proof).
    axc = axes[n + 1][0]
    for sp in species:
        xs, ys = [], []
        for r in perf:
            if r["species"] != sp or r["bugs"] <= 0 or r["swarms"] <= 0:
                continue
            cpu = sum(r[f"cpu_{ph}_us"] for ph in CPU_PHASES)
            xs.append(r["bugs"] / r["swarms"])      # avg swarm size
            ys.append(cpu / r["bugs"])              # µs per bug per day
        if xs:
            axc.scatter(xs, ys, s=20, color=spcol[sp], label=sp, alpha=0.7)
    axc.set_xlabel("avg swarm size (bugs / swarm)")
    axc.set_ylabel("server µs per bug / day")
    axc.set_title("cost per bug vs swarm size — fatter swarms ⇒ less per-bug cost",
                  loc="left", fontsize=10, fontweight="bold")
    axc.legend(loc="upper right", fontsize=6, framealpha=0.6)

    fig.suptitle(f"Bug cost profiler — {tag}", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.99])
    cpath = os.path.join(outdir, f"perf_{tag}.png")
    fig.savefig(cpath, dpi=110)
    return cpath


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="perf", help="output filename tag")
    ap.add_argument("--log", help="parse this captured log file instead of docker compose logs")
    ap.add_argument("--since", help="docker logs --since window (e.g. 10m); ignored with --log")
    args = ap.parse_args()

    outdir = os.path.join(_repo_root(), "tools", "_generated", "ecology_charts")
    os.makedirs(outdir, exist_ok=True)

    perf, sysr = parse(get_log_text(args))
    if not perf:
        print("No PERFSTATS lines found. Is the zone's `profile` flag on and a run executed?", file=sys.stderr)
        sys.exit(1)
    ppath, spath = write_csvs(perf, sysr, outdir, args.tag)
    days = sorted({r["day"] for r in perf})
    print(f"parsed {len(perf)} PERFSTATS rows ({len(days)} game-days) + {len(sysr)} PERFSYS rows")
    print(f"  {ppath}")
    print(f"  {spath}")
    cpath = chart(perf, sysr, outdir, args.tag)
    if cpath:
        print(f"  {cpath}")


if __name__ == "__main__":
    main()
