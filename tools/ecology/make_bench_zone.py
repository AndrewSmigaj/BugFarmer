#!/usr/bin/env python3
"""make_bench_zone.py — copy a real zone into a throwaway BENCH zone for measurement and tuning runs.

Why: `run_config.py` deletes the tested zone's saved state before every run (run_config.py wipe_zone_state). Run on
the real village, that would erase the village's live save. A bench copy has its own zone id, keeps no save
(`ephemeral_swarms: true`), has no neighbours, and is git-ignored (`nakama/data/zones/bench_*/`), so tests can't
touch real zones or bloat the repo. Regenerate it any time from the authored source zone.

  python3 tools/ecology/make_bench_zone.py                      # village_21_B -> bench_village
  python3 tools/ecology/make_bench_zone.py --source bee_meadow_20 --name bench_meadow

Only ids starting with "bench_" can be written, and an existing bench folder is replaced only if its zone.json
says it is a bench zone.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ZONES = ROOT / "nakama/data/zones"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="village_21_B")
    ap.add_argument("--name", default="bench_village")
    a = ap.parse_args()
    if not a.name.startswith("bench_"):
        sys.exit("refusing: bench zone ids must start with 'bench_' (real zones are never written by this tool)")
    src, dst = ZONES / a.source, ZONES / a.name
    if not (src / "zone.json").exists():
        sys.exit(f"no source zone {src}")
    if dst.exists():
        old = json.loads((dst / "zone.json").read_text()) if (dst / "zone.json").exists() else {}
        if not old.get("bench_of"):
            sys.exit(f"refusing: {dst} exists and is not a bench zone")
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    z = json.loads((dst / "zone.json").read_text())
    z.update({"zone_id": a.name, "name": f"Bench copy of {z.get('name', a.source)}", "bench_of": a.source,
              "row": 0, "col": 0, "ephemeral_swarms": True})
    z.pop("neighbors", None)
    (dst / "zone.json").write_text(json.dumps(z, indent=2))
    chunks = len(list(dst.glob("chunk_*.json")))
    print(f"{a.name}: copied {chunks} chunks from {a.source} (ephemeral, no neighbours, row/col 0,0)")


if __name__ == "__main__":
    main()
