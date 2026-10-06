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
# Optional environment (the Stage 1.0 rig, docs/plans/village-slice.md):
#   PLAYER=<path to BugFarmerClient.exe>  another build (default: Build/SyncTest; Build/Release is the release build)
#   CLIENT_FLAGS="..."                    extra client flags, e.g. "-perfmode clean -behaviour"
#   ROUTE=<route file>                    walk the player along it (tools/ecology/make_route.py); a WSL path is fine
#   WINDOWED=1                            draw for real (no -batchmode -nographics), 1600x900 windowed, vSync off
#   AFFINITY=<hex mask>                   hold the client to these logical CPUs (the slower-computer emulation; 5 = two
#                                         different P-cores on this i7-14700F, whose hyperthread pairs are 0-1, 2-3, …)
set -u

ZONE="${1:-village_21_B}"
DUR="${2:-600}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLAYER="${PLAYER:-$ROOT/BugFarmerClient/Build/SyncTest/BugFarmerClient.exe}"
CLIENT_FLAGS="${CLIENT_FLAGS:-}"
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
rm -f "$PDATA/fly_counts.csv" "$PDATA/client_perf.csv" "$PDATA/client_perf_totals.csv" "$PDATA/player_ecology.log" /tmp/client_perf.csv /tmp/client_perf_totals.csv 2>/dev/null
RIG_FILES="client_cost_E.csv client_cost_summary_E.json client_behaviour_E.csv hashlog_E.csv reports_E.csv"
for f in $RIG_FILES; do rm -f "$PDATA/$f" "/tmp/$f"; done

# Keep the client's clock at the zone's speed (call_rate/10 x sim_batch): a client stepping at 1x in a 6x zone falls
# ever further behind the server, so the bugs' own decisions (hunting, eating) run at a sixth of the server's pace.
TS="$(python3 -c "import json; z=json.load(open('$ROOT/nakama/data/zones/$ZONE/zone.json')); print((z.get('call_rate') or 10) * max(1, z.get('sim_batch') or 1) / 10)" 2>/dev/null || echo 1)"

MODE_FLAGS="-batchmode -nographics"
[ "${WINDOWED:-0}" = "1" ] && MODE_FLAGS="-screen-fullscreen 0 -screen-width 1600 -screen-height 900 -vsyncoff"
ROUTE_FLAGS=""
if [ -n "${ROUTE:-}" ]; then
  RWIN="$(realpath "$ROUTE" | sed -E 's#^/mnt/([a-z])/#\U\1:/#')"
  ROUTE_FLAGS="-route $RWIN"
fi

echo "=== ecology client: zone=$ZONE duration=${DUR}s timescale=$TS player=$PLAYER flags=[$MODE_FLAGS $CLIENT_FLAGS $ROUTE_FLAGS] ==="
# shellcheck disable=SC2086  # the flag lists are meant to split into words
"$PLAYER" $MODE_FLAGS -ecology -zone "$ZONE" -clientid E -duration "$DUR" -timescale "$TS" $CLIENT_FLAGS $ROUTE_FLAGS \
  -logFile "$WPDATA/player_ecology.log" &
CPID=$!
if [ -n "${AFFINITY:-}" ]; then
  # A process-level setting only (no machine setting changes): the one running test client is held to these CPUs.
  sleep 2
  powershell.exe -NoProfile -Command "Get-Process BugFarmerClient | ForEach-Object { \$_.ProcessorAffinity = [IntPtr]0x$AFFINITY; \$_.ProcessorAffinity }" \
    | tr -d '\r' | sed 's/^/affinity set: /'
fi
wait "$CPID"
CLIENT_EXIT=$?

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
[ -f "$PDATA/client_perf_totals.csv" ] && cp "$PDATA/client_perf_totals.csv" /tmp/client_perf_totals.csv
# The Stage 1.0 rig's files (cost, behaviour, fingerprints, reports), when the flags asked for them.
for f in $RIG_FILES; do [ -f "$PDATA/$f" ] && cp "$PDATA/$f" "/tmp/$f"; done
exit $CLIENT_EXIT  # the client's own exit code (0 ok, 4 no seed, 5 no bugs; see HeadlessSyncTest)
