#!/usr/bin/env python3
"""Score the bug-ecology tuning configs on the OSCILLATION + SELF-MAINTENANCE objective.

Reads the per-config interaction logs (tools/_generated/ecology_charts/interaction_log_<name>.csv,
written by run_config.py → plot_interactions.py) and prints a table per config × species:

  mean  — average population vs the target CENTER (fly/butterfly 100, others 30)
  min/max/σ — is it actually SWINGING? (a flat line fails even at the right mean)
  amp%  — (max-min)/mean: oscillation amplitude as a fraction of the center
  %rsd  — fraction of births from the Director re-seed safety net (→0 = self-maintained)
  trough>floor — did the low point stay ABOVE the re-seed floor? (self-maintained)
  born/died — the dominant birth source / death cause (the "why", at a glance)
  verdict — PASS (near target, oscillating, self-maintained) / OSC? / LOW / FLOOR / FLAT

  python3 tools/ecology/compare_configs.py                 # every config with a log
  python3 tools/ecology/compare_configs.py 00_baseline 01_no_cull
"""
import csv, glob, os, statistics, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import make_bug_lab  # noqa: E402  (DEFAULT_LAB → re-seed floors + Director bands)

CHARTS = os.path.join(ROOT, "tools", "_generated", "ecology_charts")
TARGET = {"fly_common": 100, "butterfly_meadow": 100, "wasp_common": 30,
          "centipede_garden": 30, "millipede": 30, "beetle_carrion": 30}
BIRTH_SRCS = ["brood", "nest", "reproduce", "reseed", "spawn"]
DEATH_CAUSES = ["oldage", "starve", "predation", "cull"]
SPECIES_ORDER = ["fly_common", "butterfly_meadow", "wasp_common", "centipede_garden",
                 "millipede", "beetle_carrion"]


def floor_for(sp):
    return make_bug_lab.DEFAULT_LAB["director"].get(sp, {}).get("min_population", 0)


def load(name):
    path = os.path.join(CHARTS, f"interaction_log_{name}.csv")
    if not os.path.exists(path):
        return None
    by_sp = {}
    for r in csv.DictReader(open(path)):
        sp = r["species"]
        by_sp.setdefault(sp, []).append({k: (float(v) if k == "avg_sat" else int(v))
                                         for k, v in r.items() if k not in ("species",)})
    return by_sp


def score_species(rows):
    """rows = list of per-day dicts for one species (sorted by day). Returns a metrics dict."""
    rows = sorted(rows, key=lambda r: r["day"])
    pops = [r["pop"] for r in rows]
    if not pops:
        return None
    mean = statistics.mean(pops)
    lo, hi = min(pops), max(pops)
    sigma = statistics.pstdev(pops) if len(pops) > 1 else 0.0
    amp = (hi - lo) / mean if mean else 0.0
    births = {s: sum(r[f"b_{s}"] for r in rows) for s in BIRTH_SRCS}
    deaths = {c: sum(r[f"d_{c}"] for r in rows) for c in DEATH_CAUSES}
    tot_b = sum(births.values()) or 1
    tot_d = sum(deaths.values())
    pct_reseed = 100.0 * births["reseed"] / tot_b
    dom_b = max(births, key=births.get) if tot_b > 1 else "-"
    dom_d = max(deaths, key=deaths.get) if tot_d else "-"
    return {"mean": mean, "min": lo, "max": hi, "sigma": sigma, "amp": amp,
            "pct_reseed": pct_reseed, "trough": lo, "dom_b": dom_b, "dom_d": dom_d}


def verdict(sp, m):
    """Compress the metrics into a one-word read against the objective."""
    target = TARGET.get(sp, 30)
    floor = floor_for(sp)
    near = 0.6 * target <= m["mean"] <= 1.6 * target
    oscillating = m["amp"] >= 0.30 and m["sigma"] >= 0.10 * max(m["mean"], 1)
    self_maint = m["trough"] > floor and m["pct_reseed"] < 10.0
    if m["trough"] <= floor or m["pct_reseed"] >= 25.0:
        return "FLOOR"          # propped up by re-seed = not self-maintained
    if not near and m["mean"] < 0.6 * target:
        return "LOW"
    if not oscillating:
        return "FLAT"
    if near and self_maint:
        return "PASS"
    return "OSC?"               # swinging but mean off-target


def main():
    names = sys.argv[1:]
    if not names:
        names = sorted(os.path.basename(p)[len("interaction_log_"):-4]
                       for p in glob.glob(os.path.join(CHARTS, "interaction_log_*.csv")))
    if not names:
        print("no interaction_log_*.csv found — run tools/ecology/run_config.py first", file=sys.stderr)
        sys.exit(1)

    hdr = f"{'species':<17} {'mean':>6} {'min':>4} {'max':>4} {'σ':>5} {'amp%':>5} {'%rsd':>5} {'born':>9} {'died':>9}  verdict"
    for name in names:
        by_sp = load(name)
        print(f"\n=== {name}   (targets: fly/butterfly 100, others 30; PASS = near + oscillating + self-maintained)")
        if not by_sp:
            print("  (no log)")
            continue
        print(hdr)
        for sp in SPECIES_ORDER:
            if sp not in by_sp:
                continue
            m = score_species(by_sp[sp])
            if not m:
                continue
            print(f"{sp:<17} {m['mean']:>6.1f} {m['min']:>4d} {m['max']:>4d} {m['sigma']:>5.1f} "
                  f"{100*m['amp']:>5.0f} {m['pct_reseed']:>5.0f} {m['dom_b']:>9} {m['dom_d']:>9}  "
                  f"{verdict(sp, m)}")


if __name__ == "__main__":
    main()
