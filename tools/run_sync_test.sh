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

echo "launching 2 headless clients CONCURRENTLY (must share the same live match/ticks)…"
# Redirect the player's stdout/stderr to a file — otherwise command substitution / the pipe blocks until
# the player exits, which serializes the two clients (they then sync to different match ticks → no overlap).
"$PLAYER" -batchmode -nographics -synctest -zone "$ZONE" -clientid A -duration "$DUR" \
  -logFile "$PDATA/player_A.log" >"$PDATA/player_A.out" 2>&1 &
PA=$!
"$PLAYER" -batchmode -nographics -synctest -zone "$ZONE" -clientid B -duration "$DUR" \
  -logFile "$PDATA/player_B.log" >"$PDATA/player_B.out" 2>&1 &
PB=$!
echo "  client A pid=$PA  client B pid=$PB ; waiting for both…"
wait "$PA" "$PB"
echo "both clients exited; comparing hash streams…"

TA=$(ls -t "$PDATA"/trace_A_*.csv 2>/dev/null | head -1)
TB=$(ls -t "$PDATA"/trace_B_*.csv 2>/dev/null | head -1)
if [ -z "$TA" ] || [ -z "$TB" ]; then
  echo "ERROR: missing trace file(s) — A=$TA B=$TB. Check $PDATA/player_*.log (did they connect + enter the zone?)."
  exit 1
fi

# PER-BUG comparison on the INTERSECTION of bugs both clients have. NOTE: a whole-client ComputeStateHash
# is the WRONG comparison here — clients are interest-managed (each subscribes to chunks around its own
# player), so two clients hash DIFFERENT bug SETS and "diverge" even when every shared bug is identical.
# The honest check: for each shared (swarmId,bugId) at each common tick, do (x,y,vx,vy) match?
python3 - "$TA" "$TB" <<'PY'
import sys
def load(p):
    d={}  # tick -> {(swarm,bug): (x,y,vx,vy)}
    for line in open(p, encoding="utf-8", errors="replace"):
        if not line[:1].isdigit(): continue
        f=line.rstrip("\n").split(",")
        if len(f)<7: continue
        try: t=int(f[0])
        except ValueError: continue
        d.setdefault(t,{})[(f[1],f[2])]=(f[3],f[4],f[5],f[6])
    return d
A=load(sys.argv[1]); B=load(sys.argv[2])
common=sorted(set(A)&set(B))
if not common:
    print("INCONCLUSIVE: no overlapping ticks (clients never co-simulated)."); sys.exit(2)
shared=mismatch=0; first=None
for t in common:
    a=A[t]; b=B[t]
    for k in (a.keys()&b.keys()):
        shared+=1
        if a[k]!=b[k]:
            mismatch+=1
            if first is None: first=(t,k,a[k],b[k])
print(f"common ticks={len(common)} ({common[0]}..{common[-1]});  shared-bug comparisons={shared}")
if shared==0:
    print("INCONCLUSIVE: clients shared NO bugs (disjoint chunk subscriptions — co-locate the players)."); sys.exit(2)
if mismatch==0:
    print(f"SYNC: ✅ IDENTICAL — all {shared} shared-bug states match. Two players see the same bugs.")
    sys.exit(0)
pct=100*mismatch/shared
t,k,va,vb=first
print(f"SYNC: ❌ DIVERGED — {mismatch}/{shared} shared-bug states differ ({pct:.1f}%). First: tick {t} bug {k} A={va} B={vb}")
print("The two players do NOT agree on shared bugs => cross-client determinism is NOT holding.")
sys.exit(1)
PY
RC=$?

echo "--- backstop: server drift detector ---"
docker compose -f "$ROOT/docker-compose.yml" logs --since "$((DUR+30))s" nakama 2>/dev/null | grep -i "Drift detected" \
  && echo "(server ALSO logged drift — corroborates divergence)" \
  || echo "(no 'Drift detected' in server log — corroborates sync)"
exit $RC
