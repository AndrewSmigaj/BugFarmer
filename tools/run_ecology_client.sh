#!/usr/bin/env bash
# Ecology DRIVER — launch ONE headless Unity client in -ecology mode.
#
# It enters the zone as authority (so client-authoritative PREDATION actually runs) and just LIVES there while
# the SERVER logs ECOSTATS, sampling the client's ground-truth per-species population into fly_counts.csv. This
# REPLACES the passive .NET sync-harness for ecology runs: the harness never ran bug behavior, so predation was
# invisible (d_predation:0) and every predator band was an artifact. Called by tools/ecology/run_config.py.
#
# The real client + real server = faithful predator/prey dynamics. Speed is the zone's call_rate (run_config
# patches it); long runs go overnight, exactly like the sync tests we already run.
#
# USAGE: tools/run_ecology_client.sh [zone] [duration_seconds]
set -u

ZONE="${1:-village_21_B}"
DUR="${2:-600}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLAYER="$ROOT/BugFarmerClient/Build/SyncTest/BugFarmerClient.exe"
PDATA="/mnt/c/Users/$USER/AppData/LocalLow/DefaultCompany/BugFarmerClient"
[ -d "$PDATA" ] || PDATA="/mnt/c/Users/emily/AppData/LocalLow/DefaultCompany/BugFarmerClient"
# The Windows .exe silently ignores a -logFile under /mnt/... — it MUST be a native C:/ path (like run_sync_*).
WPDATA="$(echo "$PDATA" | sed -E 's#^/mnt/([a-z])/#\U\1:/#')"

if [ ! -f "$PLAYER" ]; then
  echo "ERROR: no player build at $PLAYER"
  echo "  build it: Unity Editor 'BugFarmer ▸ Build Sync-Test Player', OR headless (Editor closed):"
  echo "    Unity.exe -batchmode -quit -projectPath BugFarmerClient -executeMethod SyncTestBuild.Build -logFile -"
  exit 1
fi

# A stray player from a prior run keeps the server match alive → contaminates the next run. Kill strays.
taskkill.exe /F /IM BugFarmerClient.exe >/dev/null 2>&1 || true
rm -f "$PDATA/fly_counts.csv" "$PDATA/client_perf.csv" "$PDATA/player_ecology.log" /tmp/client_perf.csv 2>/dev/null

# Keep the client's clock at the zone's speed (call_rate/10 x sim_batch): a client stepping at 1x in a 6x zone falls
# ever further behind the server, so the bugs' own decisions (hunting, eating) run at a sixth of the server's pace.
TS="$(python3 -c "import json; z=json.load(open('$ROOT/nakama/data/zones/$ZONE/zone.json')); print((z.get('call_rate') or 10) * max(1, z.get('sim_batch') or 1) / 10)" 2>/dev/null || echo 1)"

echo "=== ecology client: zone=$ZONE duration=${DUR}s timescale=$TS ==="
"$PLAYER" -batchmode -nographics -ecology -zone "$ZONE" -clientid E -duration "$DUR" -timescale "$TS" \
  -logFile "$WPDATA/player_ecology.log"

# Hand the population CSV to run_config where it already looks (/tmp), so the Python side is a one-line swap.
if [ -f "$PDATA/fly_counts.csv" ]; then
  cp "$PDATA/fly_counts.csv" /tmp/fly_counts.csv
  # optional overlays, if the client ever writes them (weather spans / corpse counts)
  [ -f "$PDATA/fly_weather.csv" ] && cp "$PDATA/fly_weather.csv" /tmp/fly_weather.csv
  [ -f "$PDATA/fly_corpses.csv" ] && cp "$PDATA/fly_corpses.csv" /tmp/fly_corpses.csv
  echo "ecology CSV -> /tmp/fly_counts.csv ($(wc -l < /tmp/fly_counts.csv) lines)"
else
  echo "WARNING: ecology client wrote no fly_counts.csv (see $PDATA/player_ecology.log)"
fi
# The client's own cost per game tick, in ~5 s windows (the scaling study reads it from /tmp too).
[ -f "$PDATA/client_perf.csv" ] && cp "$PDATA/client_perf.csv" /tmp/client_perf.csv
