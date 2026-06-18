#!/usr/bin/env python3
"""Run ONE bug-ecology tuning config end-to-end: apply its deltas to the canonical data, restart the
server, run the fast bug_lab harness, chart it (population + interaction log), then RESTORE the canonical
data. The runner MUTATES canonical files (species.json / occupants.json / ecology_tuning.json / the
bug_lab zone) — the snapshot/restore around the run is the critical footgun guard so a tuning sweep never
leaves the repo dirty. See docs/product/ecology_parameters.md and the test-changes skill §2.5.

  python3 tools/run_config.py 00_baseline                 # baseline (no deltas → compiled defaults)
  python3 tools/run_config.py 01_no_cull --duration 250   # ~14 game-days
  python3 tools/run_config.py 02_fly_food_up --keep       # leave the applied data in place (debug)

A config (tools/bug_lab_configs/<name>.json) is a DELTA, deep-merged over the baseline:
  "lab":     quantities → make_bug_lab.DEFAULT_LAB (caps / Director bands / sim_batch)
  "tuning":  dials       → nakama/data/ecology_tuning.json   (empty/absent → compiled defaults)
  "species": fields      → nakama/data/species.json          (per-species overrides)
  "fruit":   tree rates  → nakama/data/entities/occupants.json (merged under each tree's "world")
Outputs land in tools/_generated/ecology_charts/ tagged with the config name (then compare_configs.py).
"""
import argparse, copy, json, os, shutil, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import make_bug_lab  # noqa: E402

CFG_DIR = os.path.join(ROOT, "tools", "bug_lab_configs")
DATA = os.path.join(ROOT, "nakama", "data")
TUNING_JSON = os.path.join(DATA, "ecology_tuning.json")
SPECIES_JSON = os.path.join(DATA, "species.json")
OCCUPANTS_JSON = os.path.join(DATA, "entities", "occupants.json")
ZONE_DIR = os.path.join(DATA, "zones", "bug_lab")
CHARTS = os.path.join(ROOT, "tools", "_generated", "ecology_charts")
DOTNET = os.path.expanduser("~/.dotnet/dotnet")
if not os.path.exists(DOTNET):
    DOTNET = shutil.which("dotnet") or DOTNET


def deep_merge(base, delta):
    """Recursively merge delta into a COPY of base (delta wins; dicts merge, scalars/lists replace)."""
    out = copy.deepcopy(base)
    for k, v in delta.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def load_config(name, _seen=None):
    """Load a config, resolving an optional "extends": "<parent>" chain (child deep-merged OVER parent),
    so sweep configs inherit a base (e.g. 01_no_cull's cull-off director) and specify only their delta."""
    _seen = _seen or set()
    path = os.path.join(CFG_DIR, name if name.endswith(".json") else name + ".json")
    with open(path) as f:
        cfg = json.load(f)
    parent = cfg.get("extends")
    if parent:
        if parent in _seen:
            raise SystemExit(f"config extends cycle at '{parent}'")
        _seen.add(parent)
        base = load_config(parent, _seen)
        merged = deep_merge(base, cfg)
        merged.pop("extends", None)
        merged["name"] = cfg.get("name", name)
        merged["description"] = cfg.get("description", base.get("description", ""))
        return merged
    return cfg


def snapshot(paths):
    """Return a restore-token: {path: bytes-or-None}. None = file/dir didn't exist (delete on restore)."""
    snap = {}
    for p in paths:
        if os.path.isdir(p):
            snap[p] = ("dir", {f: open(os.path.join(p, f), "rb").read() for f in os.listdir(p)})
        elif os.path.exists(p):
            snap[p] = ("file", open(p, "rb").read())
        else:
            snap[p] = ("absent", None)
    return snap


def restore(snap):
    for p, (kind, data) in snap.items():
        if kind == "absent":
            if os.path.isdir(p):
                shutil.rmtree(p)
            elif os.path.exists(p):
                os.remove(p)
        elif kind == "file":
            with open(p, "wb") as f:
                f.write(data)
        elif kind == "dir":
            os.makedirs(p, exist_ok=True)
            for f, b in data.items():
                with open(os.path.join(p, f), "wb") as fh:
                    fh.write(b)


def apply_config(cfg, zone="bug_lab"):
    # tuning → ecology_tuning.json (empty/absent → remove so the server uses compiled defaults)
    tuning = cfg.get("tuning") or {}
    if tuning:
        with open(TUNING_JSON, "w") as f:
            json.dump(tuning, f, indent=2)
        print(f"  tuning: wrote {len(tuning)} dial(s) → ecology_tuning.json")
    elif os.path.exists(TUNING_JSON):
        os.remove(TUNING_JSON)

    # species → species.json (per-species field overrides)
    sp_delta = cfg.get("species") or {}
    if sp_delta:
        species = json.load(open(SPECIES_JSON))
        for sid, fields in sp_delta.items():
            if sid not in species:
                raise SystemExit(f"config species '{sid}' not in species.json")
            species[sid] = deep_merge(species[sid], fields)
        json.dump(species, open(SPECIES_JSON, "w"), indent=2)
        print(f"  species: patched {', '.join(sp_delta)}")

    # fruit → occupants.json tree rates (merged under each tree's "world")
    fr_delta = cfg.get("fruit") or {}
    if fr_delta:
        occ = json.load(open(OCCUPANTS_JSON))
        for tid, fields in fr_delta.items():
            if tid not in occ:
                raise SystemExit(f"config fruit tree '{tid}' not in occupants.json")
            occ[tid].setdefault("world", {})
            occ[tid]["world"] = deep_merge(occ[tid]["world"], fields)
        json.dump(occ, open(OCCUPANTS_JSON, "w"), indent=2)
        print(f"  fruit: patched {', '.join(fr_delta)}")

    if zone == "bug_lab":
        # lab → bug_lab zone (deep-merge the lab delta over DEFAULT_LAB, then build)
        lab = deep_merge(make_bug_lab.DEFAULT_LAB, cfg.get("lab") or {})
        make_bug_lab.build_lab(lab)
        return

    # Authored zone (e.g. village_21_B): DON'T regenerate. Patch its zone.json — deep-merge the config's
    # `bug_spawning` delta (caps / spawn weights / Director bands) + inject the temp tuning-speed flags
    # (restored from the snapshot after the run, so the shipped zone.json stays production-clean).
    zone_json = os.path.join(DATA, "zones", zone, "zone.json")
    z = json.load(open(zone_json))
    # seed: a FIXED non-zero seed makes the whole run reproducible (the server seeds its per-match RNG from
    # zone.seed, and the sim iterates entities in sorted order) — so a config's effect is measurable, not
    # drowned in run-to-run noise. Production zones keep seed 0 (random per match). A config may override.
    flags = {"ephemeral_swarms": True, "call_rate": 60, "sim_batch": 2, "seed": 1337,
             **(cfg.get("flags") or {})}
    z.update(flags)
    bs_delta = cfg.get("bug_spawning") or {}
    if bs_delta:
        z["bug_spawning"] = deep_merge(z.get("bug_spawning", {}), bs_delta)
        print(f"  bug_spawning: patched {zone} ({', '.join(bs_delta)})")
    json.dump(z, open(zone_json, "w"), indent=2)
    print(f"  zone {zone}: temp flags {flags}")


def restart_nakama():
    print("  restarting nakama (data reload)…")
    subprocess.run(["docker", "compose", "restart", "nakama"], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL)
    for _ in range(40):
        h = subprocess.run(["docker", "inspect", "bugfarmer-nakama", "--format",
                            "{{.State.Health.Status}}"], capture_output=True, text=True).stdout.strip()
        if h == "healthy":
            time.sleep(6)  # SETTLE: health passes before the socket API truly accepts joins — the
            return         # post-restart race that made 15/20 sweep-1 harness runs write no CSV.
        time.sleep(1)
    raise SystemExit("nakama did not become healthy after restart")


def _csv_ok(path):
    return os.path.exists(path) and sum(1 for _ in open(path)) >= 2  # header + ≥1 data row


def run_harness(duration, tag, zone="bug_lab", retries=3):
    """Run the harness; on an empty/missing CSV (the post-restart connection race) restart + retry.
    Returns (csv_path_or_None, run_log_text) where run_log_text is the nakama log for EXACTLY this run's
    window (so plot_interactions can't pick up a prior run's ECOSTATS — the sweep-1 contamination bug)."""
    csv = "/tmp/fly_counts.csv"
    for attempt in range(1, retries + 1):
        if os.path.exists(csv):
            os.remove(csv)
        t0 = time.time()
        print(f"  running harness ({duration}s ≈ {duration*0.057:.1f} game-days), attempt {attempt}…")
        subprocess.run([DOTNET, "run", "--project", os.path.join(ROOT, "tools", "sync-harness"),
                        "--", "--zone", zone, "--duration", str(duration), "--tag", tag],
                       cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        window = int(time.time() - t0) + 8
        run_log = subprocess.run(["docker", "compose", "logs", "--no-color", "--since", f"{window}s",
                                  "nakama"], cwd=ROOT, capture_output=True, text=True).stdout
        if _csv_ok(csv):
            return csv, run_log
        print(f"  attempt {attempt}: harness produced no CSV — restarting + retrying", file=sys.stderr)
        restart_nakama()
    return None, ""


def chart(csv, tag, run_log):
    os.makedirs(CHARTS, exist_ok=True)
    if csv and _csv_ok(csv):
        subprocess.run(["python3", os.path.join(ROOT, "tools", "plot_fly_counts.py"), csv, tag,
                        f"Config {tag}"], cwd=ROOT)
    # Per-run log file → plot_interactions parses ONLY this run's ECOSTATS (no docker-logs --since
    # cross-run contamination). Written under the charts dir so it's auditable.
    log_path = os.path.join(CHARTS, f"nakama_{tag}.log")
    with open(log_path, "w") as f:
        f.write(run_log)
    subprocess.run(["python3", os.path.join(ROOT, "tools", "plot_interactions.py"), "--tag", tag,
                    "--log", log_path], cwd=ROOT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config", help="config name under tools/bug_lab_configs/ (with or without .json)")
    ap.add_argument("--zone", default="bug_lab", help="zone to run (bug_lab regenerates; others are authored)")
    ap.add_argument("--duration", type=int, default=250, help="harness seconds (×0.057 = game-days)")
    ap.add_argument("--keep", action="store_true", help="don't restore canonical data after the run (debug)")
    args = ap.parse_args()

    cfg = load_config(args.config)
    name = cfg.get("name", args.config)
    print(f"=== config {name} [{args.zone}]: {cfg.get('description', '')}")

    snap = snapshot([TUNING_JSON, SPECIES_JSON, OCCUPANTS_JSON, os.path.join(DATA, "zones", args.zone)])
    try:
        apply_config(cfg, args.zone)
        restart_nakama()
        csv, run_log = run_harness(args.duration, name, args.zone)
        if csv is None:
            print("  ERROR: harness produced no CSV after retries — skipping charts for this config", file=sys.stderr)
        chart(csv, name, run_log)
    finally:
        if args.keep:
            print("  --keep: canonical data LEFT MUTATED (restore with `git checkout nakama/data`)")
        else:
            restore(snap)
            print("  restored canonical data")
    print(f"=== done: tools/_generated/ecology_charts/{name}.png + interactions_{name}.png")


if __name__ == "__main__":
    main()
