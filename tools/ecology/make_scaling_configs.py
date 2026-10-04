#!/usr/bin/env python3
"""make_scaling_configs.py — write the run_config configs for the scaling study (S1) and the bench baseline (S2).

Every config carries the SHIPPED tuning (nakama/data/ecology_tuning.json) explicitly: run_config treats an empty
"tuning" as "use the compiled defaults" (it removes the file for the run), so the older v21b_baseline actually
measured the defaults, not the game as shipped.

  bench_scale_1x / _2x / _4x — today's village bug numbers (initial, caps, director bands) times 1, 2 and 4, for
                                the profiler (PERFSTATS/PERFSYS) and client throughput. Nest species (wasps,
                                max_nests > 0) are left as they are: their numbers come from the nests.
  bench_baseline             — the 1x village, for the long (about 48 game-days) population run.

  python3 tools/ecology/make_scaling_configs.py [--source village_21_B]
Run on the bench zone only: python3 tools/ecology/run_config.py bench_scale_2x --zone bench_village --duration 300
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG = ROOT / "tools/bug_lab_configs"
SCALED = ("initial", "max", "max_population", "min_population", "event_low", "event_high", "cull_at")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="village_21_B")
    a = ap.parse_args()
    tuning = json.loads((ROOT / "nakama/data/ecology_tuning.json").read_text())
    caps = json.loads((ROOT / f"nakama/data/zones/{a.source}/zone.json").read_text())["bug_spawning"]["species_caps"]

    def write(name, desc, k):
        sc = {}
        if k != 1:
            for sid, c in caps.items():
                if c.get("max_nests", 0) > 0:
                    continue
                sc[sid] = {f: int(round(c[f] * k)) for f in SCALED if f in c}
        cfg = {"name": name, "description": desc, "species": {}, "tuning": tuning,
               "bug_spawning": {"species_caps": sc} if sc else {}}
        (CFG / f"{name}.json").write_text(json.dumps(cfg, indent=2) + "\n")
        print("wrote", name, f"(x{k}, {len(sc)} species scaled)")

    for k in (1, 2, 4):
        write(f"bench_scale_{k}x", f"S1 scaling: {a.source}'s bug numbers x{k}, shipped tuning (bench zone only)", k)
    write("bench_baseline", f"S2 baseline: {a.source} as shipped (numbers and tuning), long population run", 1)


if __name__ == "__main__":
    main()
