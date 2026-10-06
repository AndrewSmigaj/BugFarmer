#!/usr/bin/env bash
# Two to four headless test players in one zone, like real players (docs/plans/village-slice.md, Stage 1.0c):
# player P1 enters first and is in charge; the others join one after another and walk a route (the wanderers).
# Optional: the computer in charge leaves part-way (an authority hand-over under load), and P2 leaves and rejoins.
# At the end, every player's fingerprint log is compared with P2's (the reference) by tools/netcode/equiv_check.py,
# and each player's cost summary is collected. Several players on one machine share its CPU, so these runs are
# valid for sync, the server and bandwidth — not for one client's frame time.
#
# USAGE:  tools/run_players.sh N [zone=bench_village] [duration_seconds=180]
#   ROUTE=<route file>   the wanderers' route (default: tools/_generated/routes/<zone>.route, made if missing)
#   LEAVE_AT=<s>         P1 (in charge) quits after this many seconds of recording; the server hands charge on
#   REJOIN_AT=<s>        P2 quits after this many seconds and rejoins at once as the same account (a reconnect)
#   FLAGS="..."          flags for every player (default: "-hashlog -perfmode clean")
#   PLAYER=<exe>         the build (default: Build/SyncTest)
#   WIPE=0               keep the zone's save (default: wiped first for bench_* zones)
# Exit: equiv_check's worst verdict over the players compared (0 identical, 1 diverged, 2 inconclusive).
set -u
N="${1:?usage: run_players.sh N [zone] [duration]}"
ZONE="${2:-bench_village}"
DUR="${3:-180}"
[ "$N" -ge 2 ] && [ "$N" -le 4 ] || { echo "N must be 2..4"; exit 64; }
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLAYER="${PLAYER:-$ROOT/BugFarmerClient/Build/SyncTest/BugFarmerClient.exe}"
FLAGS="${FLAGS:--hashlog -perfmode clean}"
PDATA="/mnt/c/Users/$USER/AppData/LocalLow/DefaultCompany/BugFarmerClient"
[ -d "$PDATA" ] || PDATA="/mnt/c/Users/emily/AppData/LocalLow/DefaultCompany/BugFarmerClient"
WPDATA="$(echo "$PDATA" | sed -E 's#^/mnt/([a-z])/#\U\1:/#')"
OUT="$ROOT/tools/_generated/players/$(date -u +%Y-%m-%dT%H%M%SZ)_${N}p_$ZONE"
mkdir -p "$OUT"
[ -f "$PLAYER" ] || { echo "ERROR: no player build at $PLAYER"; exit 1; }

ROUTE="${ROUTE:-$ROOT/tools/_generated/routes/$ZONE.route}"
[ -f "$ROUTE" ] || python3 "$ROOT/tools/ecology/make_route.py" "$ZONE" --out "$ROUTE" || { echo "ERROR: no route"; exit 1; }
RWIN="$(realpath "$ROUTE" | sed -E 's#^/mnt/([a-z])/#\U\1:/#')"

taskkill.exe /F /IM BugFarmerClient.exe >/dev/null 2>&1 || true
WIPE="${WIPE:-$([[ "$ZONE" == bench_* ]] && echo 1 || echo 0)}"
if [ "$WIPE" = "1" ]; then
  WIPE_FLAG=""; [[ "$ZONE" == bench_* ]] || WIPE_FLAG="--any-zone"
  python3 "$ROOT/tools/saves/wipe_zone.py" "$ZONE" $WIPE_FLAG || { echo "ERROR: wipe failed"; exit 1; }
fi
for i in $(seq 1 "$N"); do
  rm -f "$PDATA"/hashlog_P"$i"*.csv "$PDATA"/client_cost_P"$i"*.csv "$PDATA"/client_cost_summary_P"$i"*.json \
        "$PDATA"/player_P"$i"*.log "$PDATA"/trace_P"$i"_*.csv 2>/dev/null
done

launch() {  # id duration extra-args...   (sets LAST_PID; called directly, never in $(...), so `wait` can see it)
  local id="$1" dur="$2"; shift 2
  # shellcheck disable=SC2086
  "$PLAYER" -batchmode -nographics -synctest -zone "$ZONE" -clientid "${id%%_*}" -duration "$dur" $FLAGS "$@" \
    -logFile "$WPDATA/player_$id.log" >/dev/null 2>&1 &
  LAST_PID=$!
}
wait_recording() {
  for _ in $(seq 1 120); do grep -q "recording" "$PDATA/player_$1.log" 2>/dev/null && return 0; sleep 1; done
  return 1
}

echo "=== $N players in $ZONE for ${DUR}s (route $ROUTE${LEAVE_AT:+, P1 leaves at ${LEAVE_AT}s}${REJOIN_AT:+, P2 rejoins at ${REJOIN_AT}s}) ==="
PIDS=()
P1DUR="${LEAVE_AT:-$DUR}"
launch P1 "$P1DUR"; PIDS+=("$LAST_PID")
wait_recording P1 || { echo "ERROR: P1 never started recording"; exit 1; }
for i in $(seq 2 "$N"); do
  sleep 8
  d=$(( DUR - 8 * (i - 1) - 20 )); [ "$d" -lt 40 ] && d=40
  if [ "$i" = 2 ] && [ -n "${REJOIN_AT:-}" ]; then d="$REJOIN_AT"; fi
  launch "P$i" "$d" -route "$RWIN"; PIDS+=("$LAST_PID")
done
if [ -n "${REJOIN_AT:-}" ]; then
  # P2's first session ends at REJOIN_AT (its -duration); rejoin as the same account, with its own file names.
  wait "${PIDS[1]}" 2>/dev/null
  d=$(( DUR - REJOIN_AT - 40 )); [ "$d" -lt 40 ] && d=40
  launch P2_r2 "$d" -route "$RWIN" -runtag r2; PIDS+=("$LAST_PID")
fi
echo "waiting for every player to finish…"
for p in "${PIDS[@]}"; do wait "$p" 2>/dev/null; done

cp "$PDATA"/player_P*.log "$OUT"/ 2>/dev/null
cp "$PDATA"/hashlog_P*.csv "$PDATA"/client_cost_P*.csv "$PDATA"/client_cost_summary_P*.json "$OUT"/ 2>/dev/null
docker compose -f "$ROOT/docker-compose.yml" logs --no-color --since "$((DUR + 120))s" nakama > "$OUT/nakama.log" 2>/dev/null
grep -h "authority\|Authority" "$OUT/nakama.log" | tail -5 | sed 's/^/  server: /'

# Compare every player with the reference P2 (the one that stays the whole time unless it rejoins; then P3).
REF="hashlog_P2.csv"; [ -n "${REJOIN_AT:-}" ] && [ "$N" -ge 3 ] && REF="hashlog_P3.csv"
worst=0
for f in "$OUT"/hashlog_P*.csv; do
  [ "$(basename "$f")" = "$REF" ] && continue
  echo "--- $(basename "$f") against $REF ---"
  python3 "$ROOT/tools/netcode/equiv_check.py" "$f" "$OUT/$REF" --min-ticks 100
  rc=$?
  if [ "$rc" = 1 ]; then worst=1; elif [ "$rc" = 2 ] && [ "$worst" = 0 ]; then worst=2; fi
done
for s in "$OUT"/client_cost_summary_P*.json; do
  [ -f "$s" ] && python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(sys.argv[1].split('/')[-1], 'tick p99', d['tick_p99_ms'], 'ms; frames over 16.7 ms', d['frames_over_16_7ms'])" "$s"
done
echo "results: $OUT"
exit "$worst"
