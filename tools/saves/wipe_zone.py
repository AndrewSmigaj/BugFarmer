#!/usr/bin/env python3
"""Wipe ONE zone's save so its next start is the authored zone, then bring the server back up.

Why (docs/plans/village-slice.md, Stage 1.0): a test zone with ephemeral_swarms keeps no bugs or ground items between
runs, but its save still holds and restores nests (pointing at bug groups that no longer exist), trees, food plants,
broods and the clock, and a restored nest is never restaffed. So every measuring run wipes its bench zone first.

    python3 tools/saves/wipe_zone.py bench_village            # bench zones: no extra flag
    python3 tools/saves/wipe_zone.py village_21_B --any-zone  # any other zone needs --any-zone (deliberate)

The server is stopped FIRST (a clean stop writes every zone's final save, so a zone wiped on a running server comes
straight back), the zone's rows are deleted by their exact "<zone>:" key prefix (a LIKE pattern would also match
village_21_B when wiping village_21), then the server is started and the script waits until it is healthy.
The same recipe as the run-backend skill's "Reset one zone's save" and tools/ecology/run_config.py's wipe.
"""
import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sh(*args, check=True):
    return subprocess.run(list(args), cwd=ROOT, check=check, capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("zone")
    ap.add_argument("--any-zone", action="store_true", help="allow a zone whose id doesn't start with bench_")
    a = ap.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_]{1,64}", a.zone):
        sys.exit(f"refusing: '{a.zone}' is not a zone id")
    if not a.zone.startswith("bench_") and not a.any_zone:
        sys.exit(f"refusing: '{a.zone}' is not a bench zone (pass --any-zone to wipe it deliberately)")

    sh("docker", "compose", "stop", "nakama")
    sql = (f"delete from storage where collection='zone_state' and left(key, length('{a.zone}:')) = '{a.zone}:';")
    out = sh("docker", "compose", "exec", "-T", "postgres", "psql", "-U", "postgres", "-d", "nakama", "-c", sql)
    print(f"wiped {a.zone}: {out.stdout.strip()}")
    sh("docker", "compose", "start", "nakama")
    for _ in range(60):
        st = sh("docker", "inspect", "-f", "{{.State.Health.Status}}", "bugfarmer-nakama", check=False).stdout.strip()
        if st == "healthy":
            print("nakama healthy")
            return 0
        time.sleep(2)
    print("ERROR: nakama not healthy after the wipe", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
