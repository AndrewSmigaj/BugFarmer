#!/usr/bin/env bash
# Headless cross-client SYNC TEST — the proof that two real players see IDENTICAL bugs.
#
# Launches 2 instances of the built Unity player (real client) into one live zone, each recording its
# per-tick bug-state hash, then DIFFS the two hash streams. Identical => the frontier-gated deterministic
# sim keeps players in sync. First mismatch => the exact tick determinism broke.
#
# PREREQS:
#   1. Server up:   docker compose up -d   (and rebuilt if Go changed)
#   2. A CURRENT player build:  Editor menu "BugFarmer ▸ Build Sync-Test Player", OR headless:
#        "Unity.exe" -batchmode -quit -projectPath <BugFarmerClient> -executeMethod SyncTestBuild.Build -logFile -
#      (headless build needs the project lock free — close the Editor; RUNNING this script is fine with it open)
#
# USAGE:  tools/run_sync_test.sh [zone] [duration_seconds]
#   tools/run_sync_test.sh village_21_B 60
set -u

ZONE="${1:-village_21_B}"
DUR="${2:-60}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLAYER="$ROOT/BugFarmerClient/Build/SyncTest/BugFarmerClient.exe"
PDATA="/mnt/c/Users/$USER/AppData/LocalLow/DefaultCompany/BugFarmerClient"
[ -d "$PDATA" ] || PDATA="/mnt/c/Users/emily/AppData/LocalLow/DefaultCompany/BugFarmerClient"

if [ ! -f "$PLAYER" ]; then
  echo "ERROR: no player build at $PLAYER"
  echo "Build it first (Editor menu 'BugFarmer ▸ Build Sync-Test Player', or the headless -executeMethod above)."
  exit 1
fi
echo "=== sync test: zone=$ZONE duration=${DUR}s ==="
echo "player: $PLAYER"
echo "traces: $PDATA"

# clear old traces so we pick up only this run's
rm -f "$PDATA"/trace_A_*.csv "$PDATA"/trace_B_*.csv 2>/dev/null

run_client () {  # $1 = clientId
  "$PLAYER" -batchmode -nographics -synctest -zone "$ZONE" -clientid "$1" -duration "$DUR" \
    -logFile "$PDATA/player_$1.log" &
  echo $!
}

echo "launching 2 headless clients…"
PA=$(run_client A)
PB=$(run_client B)
# wait out the run + connect/enter + dump margin
wait "$PA"; wait "$PB"
echo "both clients exited; comparing hash streams…"

TA=$(ls -t "$PDATA"/trace_A_*.csv 2>/dev/null | head -1)
TB=$(ls -t "$PDATA"/trace_B_*.csv 2>/dev/null | head -1)
if [ -z "$TA" ] || [ -z "$TB" ]; then
  echo "ERROR: missing trace file(s) — A=$TA B=$TB. Check $PDATA/player_*.log (did they connect + enter the zone?)."
  exit 1
fi

python3 - "$TA" "$TB" <<'PY'
import re, sys
def load(p):
    h={}
    for line in open(p, encoding="utf-8", errors="replace"):
        m=re.match(r"# TICK (\d+) HASH ([0-9A-Fa-f]+)", line)
        if m: h[int(m.group(1))]=m.group(2)
    return h
A=load(sys.argv[1]); B=load(sys.argv[2])
common=sorted(set(A)&set(B))
if not common:
    print("INCONCLUSIVE: no overlapping ticks between the two clients (did both reach the sim?)"); sys.exit(2)
diff=[t for t in common if A[t]!=B[t]]
print(f"compared {len(common)} common ticks (range {common[0]}..{common[-1]})")
if diff:
    t=diff[0]
    print(f"SYNC: ❌ DIVERGED — first mismatch at tick {t}: A={A[t]} B={B[t]}  ({len(diff)} ticks differ)")
    print("The two players do NOT see the same bugs => determinism is broken.")
    sys.exit(1)
print("SYNC: ✅ IDENTICAL — both clients computed the same bug hashes on every common tick.")
print("Two players see the same bugs. The frontier-gated deterministic system holds.")
PY
RC=$?

echo "--- backstop: server drift detector ---"
docker compose -f "$ROOT/docker-compose.yml" logs --since "$((DUR+30))s" nakama 2>/dev/null | grep -i "Drift detected" \
  && echo "(server ALSO logged drift — corroborates divergence)" \
  || echo "(no 'Drift detected' in server log — corroborates sync)"
exit $RC
