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

# FRESH MATCH (required for a DEFINITIVE run): a build DEPLOY is not a restart, and a restart is not a fresh
# match. FRESH=1 REBUILDS the plugin image from the CURRENT Go source and force-recreates the server (so the
# match starts at tick 0 on the CURRENT backend.so) and waits for "Startup done".
# The image REBUILD is load-bearing: the compose builder BAKES a source copy at image-build time, so a plain
# force-recreate recompiles the OLD source — Go changes silently don't deploy (this invalidated a whole fix
# verification on 2026-07-19; see run-backend skill "you must build builder first").
# See memory: sync-test-fresh-match, server-chunks-lazy-loaded.
if [ "${FRESH:-0}" = "1" ]; then
  echo "FRESH=1: rebuilding plugin image from current source…"
  docker compose -f "$ROOT/docker-compose.yml" build builder >/dev/null 2>&1 \
    || { echo "  ERROR: docker compose build builder FAILED (Go compile error?) — run it manually to see why"; exit 1; }
  echo "FRESH=1: redeploying plugin + server (force-recreate) and waiting for Startup done…"
  docker compose -f "$ROOT/docker-compose.yml" up -d --force-recreate builder nakama >/dev/null 2>&1
  ok=0
  for i in $(seq 1 60); do
    docker compose -f "$ROOT/docker-compose.yml" ps --format '{{.Name}} {{.Status}}' 2>/dev/null \
      | grep -q "nakama.*healthy" && { echo "  nakama healthy (after ~${i}s)"; ok=1; break; }
    sleep 2
  done
  [ "$ok" = 1 ] || { echo "  ERROR: nakama not healthy after FRESH redeploy"; exit 1; }
fi

rm -f "$PDATA"/trace_A_*.csv "$PDATA"/trace_B_*.csv 2>/dev/null
rm -f "$PDATA"/player_A.log "$PDATA"/player_B.log 2>/dev/null

# Optional spawn-apart (Phase 1b proof): SPAWN_A / SPAWN_B = "gx,gy" place each client at a chosen edge so
# they load DISJOINT chunk sets (collision is zone-wide, so fence-adjacent bugs must stay bit-identical even
# on the client that never loaded the fence). Use cells WITHIN 4 of an edge or the server rejects the entry
# (anti-forge) and the client silently falls back to centre. For village_21_B (256x256): SPAWN_A=126,2
# (top edge → chunk rows 0-2) and SPAWN_B=126,253 (bottom edge → rows 5-7) are genuinely disjoint. The
# disjointness is ASSERTED below. Unset = default spawn (co-located regression).
A_SPAWN_ARG=(); B_SPAWN_ARG=()
[ -n "${SPAWN_A:-}" ] && A_SPAWN_ARG=(-spawn "$SPAWN_A")
[ -n "${SPAWN_B:-}" ] && B_SPAWN_ARG=(-spawn "$SPAWN_B")
# DRIFT-NET SELF-TEST: DESYNC_B=<n> makes client B deliberately perturb one bug n recorded ticks in — the
# zone drift round + authority tie-referee must then DETECT + RESYNC it (server log: "tie broken by
# AUTHORITY"). Such a run is EXPECTED to show a divergent span in the diff — it proves the net, not sync.
[ -n "${DESYNC_B:-}" ] && B_SPAWN_ARG+=(-desyncafter "$DESYNC_B")

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

# NON-VACUITY GUARD for spawn-apart: when BOTH SPAWN_A and SPAWN_B are set, the whole point is that the two
# clients loaded DIFFERENT chunks (so zone-wide collision is actually exercised). Parse each client's
# "Subscribe chunk x,y" log lines and FAIL LOUD if the subscribed sets are not disjoint — otherwise a
# silently-rejected entry (clients both at centre) would masquerade as a passing spawn-apart proof.
if [ -n "${SPAWN_A:-}" ] && [ -n "${SPAWN_B:-}" ]; then
  python3 - "$PDATA/player_A.log" "$PDATA/player_B.log" <<'PY' || exit 2
import re, sys
def chunks(p):
    s=set()
    for line in open(p, encoding="utf-8", errors="replace"):
        m=re.search(r"Subscribe chunk (\-?\d+),(\-?\d+)", line)
        if m: s.add((int(m.group(1)), int(m.group(2))))
    return s
A=chunks(sys.argv[1]); B=chunks(sys.argv[2])
inter=A&B
ra=sorted({c[1] for c in A}); rb=sorted({c[1] for c in B})
print(f"spawn-apart chunk check: A loaded {len(A)} chunks (rows {ra}); B loaded {len(B)} chunks (rows {rb})")
if not A or not B:
    print("INCONCLUSIVE: a client subscribed to NO chunks (no PlayerController / entry failed)."); sys.exit(2)
if inter:
    print(f"INCONCLUSIVE: clients are NOT disjoint — {len(inter)} shared chunks {sorted(inter)[:6]}. "
          f"Entry likely rejected (anti-forge) → fell back to centre. Use edge cells (e.g. 126,2 / 126,253)."); sys.exit(2)
print("OK: clients loaded DISJOINT chunk sets — zone-wide collision is genuinely exercised.")
PY
fi

# Cross-client determinism diff — canonical shared impl (tools/netcode/sync_diff.py), unit-tested by
# tools/netcode/test_sync_diff.py. PRIMARY = per-tick whole-state HASH stream; LOCALIZER = per-bug intersection.
# (Stops at the "# SWARMLEGS" marker so 14-col leg rows can't collide with bug-id 0/1 keys.)
python3 "$ROOT/tools/netcode/sync_diff.py" "$TA" "$TB"
RC=$?

# RECONSTRUCTION TRIPWIRES (2026-07-19 late-join bug class): a merge/split that DEFICIT-FILLS bugs a live
# client should have MOVED, or snapshot bugs ORPHANED without metadata, is the same-id-different-bug
# divergence machine even when positions happen not to diverge this run. FAIL LOUD on any occurrence in
# either client log. (moved 0/0 is excluded — a genuinely empty absorbed swarm is legal.)
TRIP=0
for LOGF in "$PDATA/player_A.log" "$PDATA/player_B.log"; do
  [ -f "$LOGF" ] || continue
  HITS=$(grep -E "SWARM_MERGE .* moved 0/[1-9]|SWARM_SPLIT .* moved 0, spawned [1-9]|SWARM_SPLIT .* parent now -1|caching .* bugs for later" "$LOGF" | head -5)
  if [ -n "$HITS" ]; then
    echo "TRIPWIRE: swarm-reconstruction fault in $(basename "$LOGF"):"
    echo "$HITS" | sed 's/^/    /'
    TRIP=1
  fi
done
if [ "$TRIP" = 1 ]; then
  echo "TRIPWIRE: ❌ FAIL — a client fabricated/orphaned bugs during merge/split or late-join (the"
  echo "same-id-different-bug class). This fails the run even if the position diff above passed."
  RC=6
fi

echo "--- backstop: server drift detector (NOTE: structurally blind at 2 players pre-Phase-2 — silence is NOT proof) ---"
docker compose -f "$ROOT/docker-compose.yml" logs --since "$((DUR+30))s" nakama 2>/dev/null \
  | grep -iE "Drift detected|ambiguous hash split" \
  && echo "(server drift machinery fired — see lines above)" \
  || echo "(server drift machinery silent)"
exit $RC
