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

# Cross-client determinism diff — canonical shared impl (tools/netcode/sync_diff.py), unit-tested by
# tools/netcode/test_sync_diff.py. PRIMARY = per-tick whole-state HASH stream; LOCALIZER = per-bug intersection.
# (Stops at the "# SWARMLEGS" marker so 14-col leg rows can't collide with bug-id 0/1 keys.)
python3 "$ROOT/tools/netcode/sync_diff.py" "$TA" "$TB"
RC=$?

echo "--- backstop: server drift detector ---"
docker compose -f "$ROOT/docker-compose.yml" logs --since "$((DUR+30))s" nakama 2>/dev/null | grep -i "Drift detected" \
  && echo "(server ALSO logged drift — corroborates divergence)" \
  || echo "(no 'Drift detected' in server log — corroborates sync)"
exit $RC
