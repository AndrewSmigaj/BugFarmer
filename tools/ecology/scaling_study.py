#!/usr/bin/env python3
"""Scaling study — how bug counts cost the players' computers and the server (S1 in
docs/plans/finish-bugs-zones-items.md; results in docs/product/investigations/scaling-*/).

    python3 tools/ecology/scaling_study.py                      # run 1x, 2x, 4x on bench_village, then summarise
    python3 tools/ecology/scaling_study.py --summarize <outdir>  # summarise saved runs again

Each run is one tools/ecology/run_config.py config (tools/bug_lab_configs/bench_scale_*.json, made by
make_scaling_configs.py) on a BENCH zone — run_config wipes the tested zone's save, so real zones are refused. One run
at a time; nothing else should be running (the CPU numbers are only fair on a quiet machine). After each run the
canonical data must be back as committed (`git status nakama/data` clean) or the study stops.

What it reads:
  client  client_perf.csv from the headless ecology client: every ~5 s, ticks simulated, process CPU ms, bug-sim ms
          (PerfProfiler Sim.SwarmTick), frames, GC, heap, bug count.
  server  the nakama log for the run's window: PERFSYS per game-day (tick time and its worst tick, broadcast bytes,
          the authority's snapshot upload) and PERFSTATS (bugs per species).
Writes <outdir>/<config>/{client_perf.csv, fly_counts.csv, player.log, nakama.log, run.log} and
<outdir>/summary.{json,md}.
"""
import argparse
import glob
import csv
import datetime as dt
import json
import os
import re
import shutil
import statistics
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PDATA = "/mnt/c/Users/emily/AppData/LocalLow/DefaultCompany/BugFarmerClient"
SYS_RE = re.compile(r"PERFSYS day=(\d+) (.*?)(?:\"|$)")
PERF_RE = re.compile(r"PERFSTATS day=(\d+) sp=(\S+) (.*?)(?:\"|$)")
KV_RE = re.compile(r"(\w+)=(\d+)")
LJ_RE = re.compile(r"Sent LateJoinSnapshot to \S+: (\d+) bytes")
WARMUP_S = 30          # client windows before this many real seconds are start-up, not steady cost


def sh(cmd, **kw):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, **kw)


def data_clean():
    return sh(["git", "status", "--porcelain", "nakama/data"]).stdout.strip() == ""


RIG_FILES = ("client_cost_E.csv", "client_cost_summary_E.json", "client_behaviour_E.csv", "hashlog_E.csv", "reports_E.csv")


def run_one(cfg, zone, duration, out, env=None, label=None, seed=None):
    d = os.path.join(out, label or cfg)
    os.makedirs(d, exist_ok=True)
    for f in ("/tmp/client_perf.csv", "/tmp/client_perf_totals.csv", "/tmp/fly_counts.csv") + tuple("/tmp/" + r for r in RIG_FILES):
        if os.path.exists(f):
            os.remove(f)
    for f in glob.glob(os.path.join(PDATA, "screenshot_E_*.png")):  # a windowed run's pictures (-screenshot)
        os.remove(f)
    t0 = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"=== {cfg}: start {t0}", flush=True)
    with open(os.path.join(d, "run.log"), "w") as log:
        if env:
            log.write(f"rig environment: {json.dumps(env)}\n")
            log.flush()
        cmd = ["python3", "tools/ecology/run_config.py", cfg, "--zone", zone, "--duration", str(duration)]
        if seed is not None:
            cmd += ["--seed", str(seed), "--tag", os.path.basename(d)]
        rc = subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, env={**os.environ, **(env or {})}).returncode
    for src, dst in (("/tmp/client_perf.csv", "client_perf.csv"), ("/tmp/client_perf_totals.csv", "client_perf_totals.csv"),
                     ("/tmp/fly_counts.csv", "fly_counts.csv"),
                     (os.path.join(PDATA, "player_ecology.log"), "player.log")) + tuple(("/tmp/" + r, r) for r in RIG_FILES):
        if os.path.exists(src):
            shutil.copy(src, os.path.join(d, dst))
    for f in glob.glob(os.path.join(PDATA, "screenshot_E_*.png")):
        shutil.move(f, os.path.join(d, os.path.basename(f)))
    with open(os.path.join(d, "nakama.log"), "w") as f:
        f.write(sh(["docker", "compose", "logs", "--no-color", "--since", t0, "nakama"]).stdout)
    print(f"=== {cfg}: run_config exit {rc}", flush=True)
    return rc


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(q * (len(xs) - 1))))] if xs else None


def summarize_one(d):
    s = {"config": os.path.basename(d)}
    runlog = open(os.path.join(d, "run.log")).read() if os.path.exists(os.path.join(d, "run.log")) else ""
    s["retries"] = len(re.findall(r"attempt \d+: harness produced no CSV", runlog))
    # client
    p = os.path.join(d, "client_perf.csv")
    if os.path.exists(p):
        rows = [r for r in csv.DictReader(open(p)) if float(r["real_s"]) >= WARMUP_S and int(r["ticks"]) > 0]
        if rows:
            ticks = sum(int(r["ticks"]) for r in rows)
            real = sum(5.0 for _ in rows)   # windows are ~5 s each
            sim_per_tick = [float(r["sim_ms"]) / int(r["ticks"]) for r in rows]
            cpu_per_tick = [float(r["cpu_ms"]) / int(r["ticks"]) for r in rows]
            s["client"] = {
                "windows": len(rows), "bugs_mean": round(statistics.mean(int(r["bugs"]) for r in rows)),
                "swarms_mean": round(statistics.mean(int(r["swarms"]) for r in rows)),
                "ticks_per_s": round(ticks / real, 1),
                "sim_ms_per_tick_median": round(statistics.median(sim_per_tick), 2),
                "sim_ms_per_tick_p90": round(pct(sim_per_tick, 0.9), 2),
                "cpu_ms_per_tick_median": round(statistics.median(cpu_per_tick), 1),
                "frames_per_s": round(sum(int(r["frames"]) for r in rows) / real),
                "heap_mb_max": max(float(r["managed_mb"]) for r in rows),
            }
            if "food_ms" in rows[0]:            # the food-lookup timer (added for the scaling study's suspect)
                sim_total = sum(float(r["sim_ms"]) for r in rows)
                food_total = sum(float(r["food_ms"]) for r in rows)
                calls = sum(int(r["food_calls"]) for r in rows)
                s["client"].update({
                    "food_ms_per_tick_median": round(statistics.median(float(r["food_ms"]) / int(r["ticks"]) for r in rows), 2),
                    "food_share_of_sim": round(food_total / sim_total, 2) if sim_total else None,
                    "food_us_per_call": round(1000 * food_total / calls, 2) if calls else None,
                })
    # the Stage 1.0 cost probe: whole-run percentiles (the targets are judged on these) and the worst window
    cs = os.path.join(d, "client_cost_summary_E.json")
    if os.path.exists(cs):
        s["cost"] = json.load(open(cs))
        cw = os.path.join(d, "client_cost_E.csv")
        if os.path.exists(cw):
            rows = [r for r in csv.DictReader(open(cw)) if float(r["real_s"]) >= WARMUP_S and int(r["ticks"]) > 0]
            if rows:
                s["cost"]["window_tick_p99_worst_ms"] = max(float(r["tick_p99_ms"]) for r in rows)
                s["cost"]["window_draw_p99_worst_ms"] = max(float(r["draw_p99_ms"]) for r in rows)
                s["cost"]["bugs_mean_after_warmup"] = round(statistics.mean(int(r["bugs"]) for r in rows))
                allocs = [float(r["alloc_frame_tick_b"]) for r in rows if r.get("alloc_frame_tick_b")]
                idle = [float(r["alloc_frame_idle_b"]) for r in rows if r.get("alloc_frame_idle_b")]
                if allocs and idle:
                    s["cost"]["alloc_per_tick_estimate_b"] = round(statistics.mean(allocs) - statistics.mean(idle))
                snaps = [float(r["snapshot_max_ms"]) for r in rows if int(r["snapshots"]) > 0]
                if snaps:
                    s["cost"]["snapshot_build_max_ms"] = max(snaps)
    # every timed part of the client, per simulated tick (whole run; includes start-up)
    t = os.path.join(d, "client_perf_totals.csv")
    if os.path.exists(t):
        tot = {r["scope"]: (float(r["ms"]), int(r["calls"])) for r in csv.DictReader(open(t))}
        ticks = tot.get("Sim.Tick", (0, 0))[1]
        if ticks:
            s["client_breakdown_ms_per_tick"] = {k: round(ms / ticks, 3) for k, (ms, _) in sorted(tot.items())}
    # server
    n = os.path.join(d, "nakama.log")
    if os.path.exists(n):
        text = open(n).read()
        days = {}
        for m in SYS_RE.finditer(text):
            days[int(m.group(1))] = {k: int(v) for k, v in KV_RE.findall(m.group(2))}
        bugs = {}
        for m in PERF_RE.finditer(text):
            kv = {k: int(v) for k, v in KV_RE.findall(m.group(3))}
            bugs.setdefault(int(m.group(1)), 0)
            bugs[int(m.group(1))] += kv.get("bugs", 0)
        if days:
            ds = [v for v in days.values() if v.get("tick_count")]
            tc = sum(v["tick_count"] for v in ds)
            s["server"] = {
                "game_days": len(ds), "ticks": tc,
                "tick_us_mean": round(sum(v["tick_total_us"] for v in ds) / tc) if tc else None,
                "tick_us_worst": max(v["tick_max_us"] for v in ds),
                "ticks_over_100ms": sum(v.get("ticks_over", 0) for v in ds),
                # broadcast bytes per game-second (10 ticks) = per real second at normal speed, per player
                "broadcast_bytes_per_s": round(sum(v["influence_bytes"] + v["roster_bytes"] for v in ds) / (tc / 10)) if tc else None,
                "snapshot_bytes_max": max((v.get("snapshot_in_max", 0) for v in ds), default=0),
                "snapshot_bytes_mean": round(sum(v.get("snapshot_in_bytes", 0) for v in ds) /
                                             max(1, sum(v.get("snapshot_in_msgs", 0) for v in ds))),
                "heap_mb_max": max(v.get("heap_alloc_mb", 0) for v in ds),
                "bugs_by_day": {str(k): v for k, v in sorted(bugs.items())},
            }
        lj = [int(x) for x in LJ_RE.findall(text)]
        if lj:
            s["latejoin_bytes"] = lj
    return s


def summarize(out):
    runs = [summarize_one(os.path.join(out, c)) for c in sorted(os.listdir(out)) if os.path.isdir(os.path.join(out, c))]
    json.dump(runs, open(os.path.join(out, "summary.json"), "w"), indent=2)
    L = ["| run | bugs (client) | client bug-sim ms per tick (median / 90th) | client whole tick ms (p50 / p99 / max, probe) | "
         "frames over 16.7 ms | KB allocated per tick (est.) | client ticks/s reached | "
         "server ms per tick (mean / worst) | broadcast KB/s per player | authority snapshot KB (mean / max) |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in runs:
        c, v, k = r.get("client", {}), r.get("server", {}), r.get("cost", {})
        probe = (f"{k['tick_p50_ms']} / {k['tick_p99_ms']} / {k['tick_max_ms']}" if k else "—")
        alloc = (round(k["alloc_per_tick_estimate_b"] / 1024) if k.get("alloc_per_tick_estimate_b") is not None else "—")
        L.append(f"| {r['config']} | {k.get('bugs_mean_after_warmup', c.get('bugs_mean', '—'))} | "
                 f"{c.get('sim_ms_per_tick_median', '—')} / {c.get('sim_ms_per_tick_p90', '—')} | {probe} | "
                 f"{k.get('frames_over_16_7ms', '—')} | {alloc} | {c.get('ticks_per_s', '—')} | "
                 f"{(v['tick_us_mean'] / 1000) if v.get('tick_us_mean') is not None else '—'} / "
                 f"{(v['tick_us_worst'] / 1000) if v.get('tick_us_worst') is not None else '—'} | "
                 f"{round(v['broadcast_bytes_per_s'] / 1024, 1) if v.get('broadcast_bytes_per_s') else '—'} | "
                 f"{round(v.get('snapshot_bytes_mean', 0) / 1024)} / {round(v.get('snapshot_bytes_max', 0) / 1024)} |")
    open(os.path.join(out, "summary.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    return runs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--configs", default="bench_scale_1x,bench_scale_2x,bench_scale_4x")
    ap.add_argument("--zone", default="bench_village")
    ap.add_argument("--duration", type=int, default=300, help="real seconds per run")
    ap.add_argument("--out", default=os.path.join(ROOT, "tools/_generated/scaling", dt.date.today().isoformat()))
    ap.add_argument("--summarize", metavar="OUTDIR", help="only summarise saved runs")
    # the Stage 1.0 rig (docs/plans/village-slice.md): passed to the client through tools/run_ecology_client.sh
    ap.add_argument("--perfmode", choices=("clean", "breakdown"), help="turn the cost probe on (clean: per-part timers off)")
    ap.add_argument("--behaviour", action="store_true", help="the behaviour tally")
    ap.add_argument("--player", help="another build's BugFarmerClient.exe (e.g. BugFarmerClient/Build/Release/...)")
    ap.add_argument("--route", help="a route file (tools/ecology/make_route.py) for the player to walk")
    ap.add_argument("--windowed", action="store_true", help="draw for real in a window (not headless), vSync off")
    ap.add_argument("--affinity", help="hold the client to these logical CPUs, a hex mask (the slower-computer emulation)")
    ap.add_argument("--screenshot", help="a windowed run saves the game's own picture at these seconds, e.g. 60,240")
    ap.add_argument("--label", help="folder name suffix for these runs (default: the config name)")
    ap.add_argument("--seeds", help="comma-separated zone seeds: each config runs once per seed (the noise floor)")
    a = ap.parse_args()
    if a.summarize:
        summarize(a.summarize)
        return 0
    if not a.zone.startswith("bench_"):
        sys.exit(f"refusing: {a.zone} is not a bench zone (bench copies keep runs comparable: no save, no neighbours)")
    if sh(["pgrep", "-f", r"^python3 .*run_config"]).stdout.strip():
        sys.exit("refusing: another run_config is running")
    os.makedirs(a.out, exist_ok=True)
    seeds = [int(s) for s in a.seeds.split(",")] if a.seeds else [None]
    jobs = [(cfg, seed) for cfg in a.configs.split(",") for seed in seeds]
    for cfg, seed in jobs:
        if not data_clean():
            sys.exit(f"stopping before {cfg}: nakama/data is not as committed")
        env = {}
        flags = []
        if a.perfmode:
            flags += ["-perfmode", a.perfmode]
        if a.behaviour:
            flags += ["-behaviour"]
        if a.screenshot:
            flags += ["-screenshot", a.screenshot]
        if flags:
            env["CLIENT_FLAGS"] = " ".join(flags)
        if a.player:
            env["PLAYER"] = os.path.abspath(a.player)
        if a.route:
            env["ROUTE"] = os.path.abspath(a.route)
        if a.windowed:
            env["WINDOWED"] = "1"
        if a.affinity:
            env["AFFINITY"] = a.affinity
        label = cfg + ("_" + a.label if a.label else "") + (f"_seed{seed}" if seed is not None else "")
        run_one(cfg, a.zone, a.duration, a.out, env=env, label=label, seed=seed)
        if not data_clean():
            sys.exit(f"stopping after {cfg}: nakama/data was NOT restored — look before touching it")
    summarize(a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
