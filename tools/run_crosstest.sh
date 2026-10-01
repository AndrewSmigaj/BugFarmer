#!/usr/bin/env bash
# The zone-crossing test in the REAL game client (D73) — the headless Unity player (HeadlessSyncTest -crosstest).
#
# A new account's character enters the test zone persist_a, places 2 fences, then crosses zones three times through
# the game's own crossing code (CrossZoneController), and after each one checks the bag the server sends on arrival
# is the bag that left (48 fences — a stale saved copy would show 50):
#   1. into a zone that can't be entered — the player must come back to persist_a (and see a short message);
#   2. into persist_b — persist_a holds back the departure save 3 s, so the server must wait for it;
#   3. back into persist_a — persist_b holds it back 10 s, past the server's 8 s wait, so the game is told "busy"
#      and must retry behind the fade.
# The .NET saves crash test (tools/harness_crash_test.sh) covers the server side with no Unity; this covers the
# game's side of the same crossings: the entry pass, the retry, the way back.
#
# PREREQS:
#   1. Server up with the CURRENT plugin:  docker compose build builder && docker compose up -d --force-recreate builder nakama
#   2. A CURRENT player build (Unity Editor CLOSED):
#        Unity.exe -batchmode -quit -projectPath <BugFarmerClient> -executeMethod SyncTestBuild.Build -logFile <C:/ path>
#
# USAGE:  bash tools/run_crosstest.sh        Exit 0 = every check passed.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PLAYER="$ROOT/BugFarmerClient/Build/SyncTest/BugFarmerClient.exe"
PDATA="/mnt/c/Users/$USER/AppData/LocalLow/DefaultCompany/BugFarmerClient"
[ -d "$PDATA" ] || PDATA="/mnt/c/Users/emily/AppData/LocalLow/DefaultCompany/BugFarmerClient"
# The Windows .exe ignores a -logFile under /mnt/... — it must be a native C:/ path.
WPDATA="$(echo "$PDATA" | sed -E 's#^/mnt/([a-z])/#\U\1:/#')"
LOG="$PDATA/player_cross.log"
RUN="$(date -u +%m%d%H%M%S)"

[ -f "$PLAYER" ] || { echo "ERROR: no player build at $PLAYER"; exit 1; }
echo "=== zone-crossing test in the game client, run $RUN ==="

# A stray player from an earlier run would still hold a zone.
taskkill.exe /F /IM BugFarmerClient.exe >/dev/null 2>&1 || true

# Fresh test zones, wiped while the server is STOPPED (a clean stop saves every zone) — exactly their own keys.
healthy() { for i in $(seq 1 60); do
              docker compose ps --format '{{.Name}} {{.Status}}' 2>/dev/null | grep -q "nakama.*(healthy)" && return 0
              sleep 2
            done; echo "ERROR: nakama is not healthy"; return 1; }
echo "wiping persist_a / persist_b (stop → wipe → start)…"
docker compose stop nakama >/dev/null 2>&1
docker compose exec -T postgres psql -U postgres -d nakama -c "delete from storage where
  collection='zone_state' and (left(key, length('persist_a:')) = 'persist_a:'
                             or left(key, length('persist_b:')) = 'persist_b:');" >/dev/null 2>&1
docker compose start nakama >/dev/null 2>&1
healthy || exit 1

rm -f "$LOG"
# A new account each run (-clientid), so a new character with the starting kit (50 fences).
"$PLAYER" -batchmode -nographics -crosstest -character Crosser -clientid "cross$RUN" -logFile "$WPDATA/player_cross.log" \
  >"$PDATA/player_cross.out" 2>&1 &
PID=$!

# Watchdog: the test takes ~40 s; a hung player is killed (a Windows process outlives a killed WSL wrapper).
for i in $(seq 1 180); do
  kill -0 "$PID" 2>/dev/null || break
  sleep 1
done
if kill -0 "$PID" 2>/dev/null; then
  echo "ERROR: the player was still running after 180 s — killed"
  taskkill.exe /F /IM BugFarmerClient.exe >/dev/null 2>&1 || true
fi
wait "$PID"
CODE=$?

grep -o "\[HeadlessSyncTest\] .*" "$LOG" 2>/dev/null | grep -E "character '|CROSSTEST|EXCEPTION|ERROR" | sed 's/^\[HeadlessSyncTest\] /  /'
grep -E "\[CrossZone\]|\[WorldManager\] entering" "$LOG" 2>/dev/null | sed 's/^/    /' | head -20
if [ "$CODE" = 0 ] && grep -q "CROSSTEST PASS" "$LOG" 2>/dev/null; then
  echo "PASS (exit $CODE) — log: $LOG"
  exit 0
fi
echo "FAIL (exit $CODE) — log: $LOG"
exit 1
