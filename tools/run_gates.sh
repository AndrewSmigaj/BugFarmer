#!/usr/bin/env bash
# ONE gate-runner for the Stage 1 work (docs/plans/village-slice.md, Stage 1.0c): runs every gate, prints a
# pass/fail table, and exits 1 if any gate failed (2 if any was inconclusive and none failed). Each gate's exit code
# is read directly — no `| tail` that would hide it (the 2026-07-19 lesson, test-changes skill §3).
#
# USAGE:
#   tools/run_gates.sh                                  # go + sim-determinism + both late-join halves on bench_village
#   tools/run_gates.sh --old <exe> --new <exe>          # ... plus the equivalence check, both ways round
#   tools/run_gates.sh --only go,simdet                 # a subset (go, simdet, latejoin, apart, equiv)
#   ZONE=bench_village EQUIV_DUR=180 tools/run_gates.sh ...
#
# The late-join halves and the equivalence runs use a bench zone, whose save is wiped before each run
# (tools/saves/wipe_zone.py via run_sync_latejoin.sh), so each starts from the same authored state. The first
# late-join half runs FRESH=1 (rebuild + redeploy the server plugin from the current Go source).
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
ZONE="${ZONE:-bench_village}"
EQUIV_DUR="${EQUIV_DUR:-180}"
OLD=""; NEW=""; ONLY="go,simdet,latejoin,apart,equiv"
while [ $# -gt 0 ]; do
  case "$1" in
    --old) OLD="$2"; shift 2 ;;
    --new) NEW="$2"; shift 2 ;;
    --only) ONLY="$2"; shift 2 ;;
    *) echo "unknown argument: $1"; exit 64 ;;
  esac
done
want() { [[ ",$ONLY," == *",$1,"* ]]; }
DOTNET="$(command -v dotnet || echo "$HOME/.dotnet/dotnet")"
LOGDIR="$(mktemp -d /tmp/gates.XXXX)"
declare -a NAMES=() CODES=()
record() { NAMES+=("$1"); CODES+=("$2"); echo "  -> $1: exit $2 (log: $LOGDIR/$1.log)"; }

if want go; then
  echo "== Go tests (Docker) =="
  bash tools/run_go_tests.sh >"$LOGDIR/go.log" 2>&1; record go $?
fi

if want simdet; then
  for mode in "" --selftest --los-test --predation-test --surge-test --subdue-test --attack-test; do
    name="simdet${mode:- default}"; name="${name// /_}"
    echo "== sim-determinism ${mode:-default} =="
    "$DOTNET" run --project tools/sim-determinism -- $mode >"$LOGDIR/$name.log" 2>&1; record "$name" $?
  done
fi

if want latejoin; then
  echo "== late-join, players together ($ZONE, FRESH) =="
  FRESH=1 tools/run_sync_latejoin.sh "$ZONE" 70 12 >"$LOGDIR/latejoin.log" 2>&1; record latejoin $?
fi

if want apart; then
  # One player on the south edge, one on the north edge (3 cells in, inside the server's near-edge window): 126,253 in
  # a 256 zone, 126,509 in a 512 one.
  ZH="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('height') or 256)" "nakama/data/zones/$ZONE/zone.json")"
  echo "== late-join, players apart ($ZONE, spawns 126,2 and 126,$((ZH-3))) =="
  SPAWN_A=126,2 SPAWN_B=126,$((ZH-3)) tools/run_sync_latejoin.sh "$ZONE" 70 12 >"$LOGDIR/apart.log" 2>&1; record apart $?
fi

if want equiv && [ -n "$OLD" ] && [ -n "$NEW" ]; then
  echo "== equivalence: old build in charge, new build joins =="
  PLAYER_A="$OLD" PLAYER_B="$NEW" A_FLAGS="-hashlog -reportlog" B_FLAGS="-hashlog -shadowreports" EQUIV=1 \
    tools/run_sync_latejoin.sh "$ZONE" "$EQUIV_DUR" 12 >"$LOGDIR/equiv_old_in_charge.log" 2>&1; record equiv_old_in_charge $?
  echo "== equivalence: new build in charge, old build joins =="
  PLAYER_A="$NEW" PLAYER_B="$OLD" A_FLAGS="-hashlog -reportlog" B_FLAGS="-hashlog -shadowreports" EQUIV=1 \
    tools/run_sync_latejoin.sh "$ZONE" "$EQUIV_DUR" 12 >"$LOGDIR/equiv_new_in_charge.log" 2>&1; record equiv_new_in_charge $?
elif want equiv && { [ -n "$OLD" ] || [ -n "$NEW" ]; }; then
  echo "equivalence needs both --old and --new"; exit 64
fi

echo
echo "| gate | result |"
echo "|---|---|"
worst=0
for i in "${!NAMES[@]}"; do
  c="${CODES[$i]}"
  case "$c" in 0) r="PASS" ;; 2) r="INCONCLUSIVE" ;; *) r="FAIL (exit $c)" ;; esac
  echo "| ${NAMES[$i]} | $r |"
  if [ "$c" != 0 ]; then
    if [ "$c" = 2 ]; then [ "$worst" = 0 ] && worst=2; else worst=1; fi
  fi
done
echo "logs: $LOGDIR"
exit "$worst"
