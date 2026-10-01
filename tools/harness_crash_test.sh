#!/usr/bin/env bash
# The saves crash test — no Unity. A scripted player with a REAL character (tools/sync-harness --char) plays in the
# two linked test zones persist_a and persist_b, and every case checks the number that must never change: the fences
# in the world plus the fences in the bag = 50 (a new character carries 50).
#
#   graceful   place 5 fences, then stop the server CLEANLY while the player is still in the zone; start; count.
#   crash      place 5 and leave (both saved); rejoin, place 5 more, sleep in the bed, and kill -9 the server; count.
#   cross      place 5 in persist_a and walk into persist_b: the bag must arrive with 45. persist_a holds back its
#              departure save (debug_leave_delay_ms), so the next zone always loads first — the crossing race,
#              every time.
#   reconnect  place 2; while still connected, the same account joins again (a second copy of the game): it must
#              see the live bag (48), not an older saved copy.
#
# Each case starts from wiped zones and a new account (so a new character with 50 fences). Exit 0 = every case
# passed. Usage: bash tools/harness_crash_test.sh [graceful|crash|cross|reconnect …]   (default: all four)
set -uo pipefail
cd "$(dirname "$0")/.."                      # repo root
DOTNET="$(command -v dotnet || echo "$HOME/.dotnet/dotnet")"
HARNESS="tools/sync-harness"
RUN="$(date -u +%m%d%H%M%S)"
LOGS="$(mktemp -d)"
CASES=("$@"); [ ${#CASES[@]} -eq 0 ] && CASES=(graceful crash cross reconnect)

# One scripted player: its own log, its exit code. --chunks 2 = the test zones are 2x2 chunks.
player() { local log="$1"; shift
           ( cd "$HARNESS" && timeout 120 "$DOTNET" run --no-build -- --chunks 2 "$@" ) > "$LOGS/$log.log" 2>&1; }
wait_for_line() { local log="$1" pattern="$2"
                  for i in $(seq 1 60); do grep -q "$pattern" "$LOGS/$log.log" 2>/dev/null && return 0; sleep 1; done
                  return 1; }
healthy()       { for i in $(seq 1 60); do
                    docker compose ps --format '{{.Name}} {{.Status}}' 2>/dev/null | grep -q "nakama.*(healthy)" && return 0
                    sleep 2
                  done; echo "    nakama is not healthy"; return 1; }
# A clean stop saves every zone, so the zones are wiped while the server is STOPPED — exactly their own keys.
fresh_zones()   { docker compose stop nakama >/dev/null 2>&1
                  docker compose exec -T postgres psql -U postgres -d nakama -c "delete from storage where
                    collection='zone_state' and (left(key, length('persist_a:')) = 'persist_a:'
                                               or left(key, length('persist_b:')) = 'persist_b:');" >/dev/null 2>&1
                  docker compose start nakama >/dev/null 2>&1; healthy; }
count_line()    { grep -o "COUNT world=[0-9]* bag=[0-9]* total=[0-9]*" "$LOGS/$1.log" | tail -1; }

declare -A RESULT
case_graceful() {
  local dev="crash-$RUN-graceful"
  player g_place --zone persist_a --device "$dev" --char Crasher --scenario fences-place --count 5 --hold 25 &
  local pid=$!
  wait_for_line g_place "HOLDING" || { RESULT[graceful]="FAIL (the player never finished placing)"; return; }
  docker compose stop nakama >/dev/null 2>&1     # a clean stop, with the player still in the zone
  docker compose start nakama >/dev/null 2>&1; healthy; wait $pid
  player g_count --zone persist_a --device "$dev" --char Crasher --scenario fences-count --expect 50
  local code=$?
  RESULT[graceful]="$([ $code -eq 0 ] && echo PASS || echo FAIL) — $(count_line g_count)"
}

case_crash() {
  local dev="crash-$RUN-crash"
  player c_first --zone persist_a --device "$dev" --char Crasher --scenario fences-place --count 5
  sleep 5                                         # its leave saves land (persist_a holds the character's back 3 s)
  player c_second --zone persist_a --device "$dev" --char Crasher --scenario fences-place --count 5 --sleep --hold 40 &
  local pid=$!
  wait_for_line c_second "HOLDING" || { RESULT[crash]="FAIL (the player never finished placing)"; return; }
  sleep 4                                         # whatever the server saves on its own has time to land
  docker kill -s KILL bugfarmer-nakama >/dev/null 2>&1    # a crash: the process dies at once — no clean stop, no save
  # Docker counts a `docker kill` as a deliberate stop, so its restart policy doesn't bring the server back: start it
  # again the way someone would after a crash.
  docker compose start nakama >/dev/null 2>&1; healthy; wait $pid
  player c_count --zone persist_a --device "$dev" --char Crasher --scenario fences-count --expect 50
  local code=$?
  RESULT[crash]="$([ $code -eq 0 ] && echo PASS || echo FAIL) — $(count_line c_count)"
}

case_cross() {
  local dev="crash-$RUN-cross"
  player x_cross --zone persist_a --device "$dev" --char Crasher --scenario cross-fences --count 5
  local code=$?
  RESULT[cross]="$([ $code -eq 0 ] && echo PASS || echo FAIL) — $(grep -o "arrived in persist_b with BAG fence_wood=[0-9]*" "$LOGS/x_cross.log" | tail -1) (left with 45)"
  sleep 5                                         # let the held-back departure save land before the next case
}

case_reconnect() {
  local dev="crash-$RUN-reconnect"
  player r_first --zone persist_a --device "$dev" --char Crasher --scenario fences-place --count 2 --hold 25 &
  local pid=$!
  wait_for_line r_first "HOLDING" || { RESULT[reconnect]="FAIL (the player never finished placing)"; return; }
  player r_second --zone persist_a --device "$dev" --char Crasher --scenario bag-count --expect 48
  local code=$?
  RESULT[reconnect]="$([ $code -eq 0 ] && echo PASS || echo FAIL) — $(grep -o "BAG fence_wood=[0-9]*" "$LOGS/r_second.log" | tail -1) (live bag 48)"
  wait $pid
}

echo "=== saves crash test (persist_a / persist_b), run $RUN — logs in $LOGS ==="
( cd "$HARNESS" && "$DOTNET" build -nologo -v q >/dev/null 2>&1 ) || { echo "harness build FAILED"; exit 2; }
for c in "${CASES[@]}"; do
  echo "[$c] fresh zones, new character…"; fresh_zones
  "case_$c"
  echo "[$c] ${RESULT[$c]}"
done

echo
FAILED=0
for c in "${CASES[@]}"; do
  echo "  $c: ${RESULT[$c]}"
  case "${RESULT[$c]}" in PASS*) ;; *) FAILED=1 ;; esac
done
if [ $FAILED -eq 0 ]; then echo "RESULT: PASS — every case kept the 50 fences."; exit 0; fi
echo "RESULT: FAIL — see the cases above (logs in $LOGS)."; exit 1
