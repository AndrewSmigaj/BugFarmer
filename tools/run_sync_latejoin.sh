#!/usr/bin/env bash
# Headless cross-client LATE-JOIN sync test — the Phase-1 determinism gate.
#
# Unlike run_sync_test.sh (two CONCURRENT clients, which race into two separate match instances via the
# WorldEnter check-then-act), this STAGGERS the launch: client A enters first and becomes authority +
# creates the match, then — once A is actually simulating — client B LATE-JOINS the same match. B must
# adopt A's state (snapshot / seed-baseline) and then stay bit-identical, INCLUDING swarms that A spawns
# at runtime (continuous spawn → SWARM_SPAWNED) AFTER B has joined. That is the exact scenario the
# deterministic-spawn work (SWARM_SPAWNED + SwarmUpdate-demote + seed-baseline) has to make hold.
#
# PREREQS (same as run_sync_test.sh):
#   1. Server up with the CURRENT plugin:  docker compose build builder && docker compose up -d
#   2. A CURRENT player build:  Editor "BugFarmer ▸ Build Sync-Test Player", OR headless:
#        Unity.exe -batchmode -quit -projectPath <BugFarmerClient> -executeMethod SyncTestBuild.Build -logFile -
#
# USAGE:  tools/run_sync_latejoin.sh [zone] [duration_seconds] [join_delay_seconds]
#   tools/run_sync_latejoin.sh village_21_B 70 12
set -u

ZONE="${1:-village_21_B}"
DUR="${2:-120}"      # A records this long (from when it starts recording)
DELAY="${3:-10}"     # after A is recording, wait this long (A spawns runtime swarms) before B joins
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLAYER="$ROOT/BugFarmerClient/Build/SyncTest/BugFarmerClient.exe"
PDATA="/mnt/c/Users/$USER/AppData/LocalLow/DefaultCompany/BugFarmerClient"
[ -d "$PDATA" ] || PDATA="/mnt/c/Users/emily/AppData/LocalLow/DefaultCompany/BugFarmerClient"
# The Windows .exe silently ignores a -logFile under /mnt/... — it MUST be a native C:/ path or no log is
# written (and our "wait for A recording" poll would never fire). Convert /mnt/<drive>/ -> <DRIVE>:/.
WPDATA="$(echo "$PDATA" | sed -E 's#^/mnt/([a-z])/#\U\1:/#')"

if [ ! -f "$PLAYER" ]; then
  echo "ERROR: no player build at $PLAYER"; exit 1
fi
echo "=== late-join sync test: zone=$ZONE A-duration=${DUR}s B-joins-after=${DELAY}s ==="

# CONTAMINATION GUARD (cost real debugging time once): a stray player from a prior run keeps the
# server match ALIVE and ticking; the next "A" then joins that persisted, player-empty-but-state-full
# match as a second authority/late-joiner → FALSE divergence. Kill strays here, AND for a definitive
# run restart the server first so the match starts at tick 0:  docker compose restart nakama
taskkill.exe /F /IM BugFarmerClient.exe >/dev/null 2>&1 || true

rm -f "$PDATA"/trace_A_*.csv "$PDATA"/trace_B_*.csv 2>/dev/null
rm -f "$PDATA"/player_A.log "$PDATA"/player_B.log 2>/dev/null

# Optional spawn-apart (Phase 1b proof): SPAWN_A / SPAWN_B = "gx,gy" place each client at a chosen edge so
# they load DIFFERENT chunk sets. Collision is now zone-wide, so fence-adjacent bugs must stay bit-identical
# even on the client that never loaded the fence. Unset = default spawn (co-located regression).
A_SPAWN_ARG=(); B_SPAWN_ARG=()
[ -n "${SPAWN_A:-}" ] && A_SPAWN_ARG=(-spawn "$SPAWN_A")
[ -n "${SPAWN_B:-}" ] && B_SPAWN_ARG=(-spawn "$SPAWN_B")

echo "launching client A (authority, creates the match)… spawn=${SPAWN_A:-default}"
"$PLAYER" -batchmode -nographics -synctest -zone "$ZONE" -clientid A -duration "$DUR" "${A_SPAWN_ARG[@]}" \
  -logFile "$WPDATA/player_A.log" >"$PDATA/player_A.out" 2>&1 &
PA=$!

# Wait until A is actually simulating (recording) so B joins an EXISTING match, not a racing second one.
echo "waiting for A to enter + start recording (so B late-joins the SAME match)…"
recording=0
for i in $(seq 1 120); do
  grep -q "recording" "$PDATA/player_A.log" 2>/dev/null && { echo "  A is recording (after ~${i}s)"; recording=1; break; }
  kill -0 "$PA" 2>/dev/null || { echo "  ERROR: A exited before recording — see player_A.log"; wait "$PA"; exit 1; }
  sleep 1
done
[ "$recording" = 1 ] || { echo "  ERROR: A never started recording within 120s"; kill "$PA" 2>/dev/null; exit 1; }

echo "extra ${DELAY}s so A spawns runtime swarms before B joins…"
sleep "$DELAY"

# Overlap algebra (boot time cancels): A ends at A_recstart+DUR; B records from B_launch+~28s boot, and
# B_launch = A_recstart+DELAY → B records [A_recstart+DELAY+28, ...]. So BDUR = DUR-DELAY-28 ends B with A.
BDUR=$(( DUR - DELAY - 30 ))
[ "$BDUR" -lt 30 ] && BDUR=30
echo "launching client B (LATE JOIN), duration=${BDUR}s… spawn=${SPAWN_B:-default}"
"$PLAYER" -batchmode -nographics -synctest -zone "$ZONE" -clientid B -duration "$BDUR" "${B_SPAWN_ARG[@]}" \
  -logFile "$WPDATA/player_B.log" >"$PDATA/player_B.out" 2>&1 &
PB=$!

echo "waiting for both clients to finish…"
wait "$PA" "$PB"
echo "both exited; comparing per-bug state on the overlapping ticks…"

TA=$(ls -t "$PDATA"/trace_A_*.csv 2>/dev/null | head -1)
TB=$(ls -t "$PDATA"/trace_B_*.csv 2>/dev/null | head -1)
if [ -z "$TA" ] || [ -z "$TB" ]; then
  echo "ERROR: missing trace file(s) — A=$TA B=$TB. Check $PDATA/player_*.log."
  exit 1
fi

# PER-BUG comparison on the INTERSECTION of bugs both clients have, at each common tick (same diff as
# run_sync_test.sh — a whole-client hash is wrong here because clients are interest-managed).
python3 - "$TA" "$TB" <<'PY'
import sys
def load(p):
    d={}
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
    print("INCONCLUSIVE: no overlapping ticks (B never co-simulated with A)."); sys.exit(2)
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
    print("INCONCLUSIVE: clients shared NO bugs (disjoint chunk subscriptions)."); sys.exit(2)
if mismatch==0:
    print(f"SYNC: ✅ IDENTICAL — all {shared} shared-bug states match across the late join.")
    sys.exit(0)
pct=100*mismatch/shared
t,k,va,vb=first
print(f"SYNC: ❌ DIVERGED — {mismatch}/{shared} shared-bug states differ ({pct:.1f}%). First: tick {t} bug {k} A={va} B={vb}")
sys.exit(1)
PY
RC=$?

echo "--- backstop: server drift detector ---"
docker compose -f "$ROOT/docker-compose.yml" logs --since "$((DUR+30))s" nakama 2>/dev/null | grep -i "Drift detected" \
  && echo "(server ALSO logged drift — corroborates divergence)" \
  || echo "(no 'Drift detected' in server log — corroborates sync)"
exit $RC
