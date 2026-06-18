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


def apply_config(cfg):
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

    # lab → bug_lab zone (deep-merge the lab delta over DEFAULT_LAB, then build)
    lab = deep_merge(make_bug_lab.DEFAULT_LAB, cfg.get("lab") or {})
    make_bug_lab.build_lab(lab)


def restart_nakama():
    print("  restarting nakama (data reload)…")
    subprocess.run(["docker", "compose", "restart", "nakama"], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL)
    for _ in range(40):
        h = subprocess.run(["docker", "inspect", "bugfarmer-nakama", "--format",
                            "{{.State.Health.Status}}"], capture_output=True, text=True).stdout.strip()
        if h == "healthy":
            return
        time.sleep(1)
    raise SystemExit("nakama did not become healthy after restart")


def run_harness(duration, tag):
    csv = "/tmp/fly_counts.csv"
    if os.path.exists(csv):
        os.remove(csv)
    print(f"  running harness ({duration}s ≈ {duration*0.057:.1f} game-days)…")
    subprocess.run([DOTNET, "run", "--project", os.path.join(ROOT, "tools", "sync-harness"),
                    "--", "--zone", "bug_lab", "--duration", str(duration), "--tag", tag],
                   cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return csv


def chart(csv, tag, duration):
    os.makedirs(CHARTS, exist_ok=True)
    subprocess.run(["python3", os.path.join(ROOT, "tools", "plot_fly_counts.py"), csv, tag,
                    f"Config {tag}"], cwd=ROOT)
    subprocess.run(["python3", os.path.join(ROOT, "tools", "plot_interactions.py"), "--tag", tag,
                    "--since", f"{duration + 60}s"], cwd=ROOT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config", help="config name under tools/bug_lab_configs/ (with or without .json)")
    ap.add_argument("--duration", type=int, default=250, help="harness seconds (×0.057 = game-days)")
    ap.add_argument("--keep", action="store_true", help="don't restore canonical data after the run (debug)")
    args = ap.parse_args()

    cfg = load_config(args.config)
    name = cfg.get("name", args.config)
    print(f"=== config {name}: {cfg.get('description', '')}")

    snap = snapshot([TUNING_JSON, SPECIES_JSON, OCCUPANTS_JSON, ZONE_DIR])
    try:
        apply_config(cfg)
        restart_nakama()
        csv = run_harness(args.duration, name)
        if not os.path.exists(csv):
            print("  WARNING: harness wrote no CSV (connection issue?) — charts may be empty", file=sys.stderr)
        chart(csv, name, args.duration)
    finally:
        if args.keep:
            print("  --keep: canonical data LEFT MUTATED (restore with `git checkout nakama/data`)")
        else:
            restore(snap)
            print("  restored canonical data")
    print(f"=== done: tools/_generated/ecology_charts/{name}.png + interactions_{name}.png")


if __name__ == "__main__":
    main()
