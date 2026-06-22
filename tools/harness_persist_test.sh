#!/usr/bin/env bash
# Autonomous zone/farm-persistence regression test — no Unity required.
#
# A headless scripted client (tools/sync-harness, --scenario) builds a farm in sim_test, the server is
# restarted (clearing the in-memory match → forces a real load from storage), and a second client rejoins
# and ASSERTS the farm + bug population came back. Exit 0 = PASS.
#
# Usage:  bash tools/harness_persist_test.sh
set -uo pipefail
cd "$(dirname "$0")/.."                     # repo root
DOTNET="$(command -v dotnet || echo "$HOME/.dotnet/dotnet")"
HARNESS="tools/sync-harness"
ZONE="sim_test"

run_harness() { ( cd "$HARNESS" && timeout 90 "$DOTNET" run -- "$@" ); }
wipe_zone()   { docker compose exec -T postgres psql -U postgres -d nakama \
                  -c "delete from storage where collection='zone_state' and key like '${ZONE}%';" >/dev/null 2>&1; }
restart()     { docker compose up -d --force-recreate nakama >/dev/null 2>&1
                for i in $(seq 1 30); do
                  docker compose logs nakama 2>&1 | grep -q "module loaded successfully" && sleep 2 && return 0
                  sleep 1
                done; }

echo "=== zone/farm persistence test (${ZONE}) ==="

echo "[1/5] wipe ${ZONE} persistence";                                    wipe_zone
echo "[2/5] restart nakama (drop the in-memory match → truly pristine)";  restart
echo "[3/5] farm-build (headless client places a farm)"
run_harness --scenario farm-build --zone "$ZONE" --tag build 2>&1 | sed 's/^/    /' | grep -iE "scenario|local view|WorldError|exit=" || true
echo "[4/5] restart nakama (force MatchTerminate save + drop in-memory match)";  restart
echo "[5/5] farm-verify (rejoin from storage + assert)"
VERIFY_OUT="$(run_harness --scenario farm-verify --zone "$ZONE" --tag verify 2>&1)"
echo "$VERIFY_OUT" | sed 's/^/    /' | grep -iE "assert|exit=" || true
CODE=$(echo "$VERIFY_OUT" | grep -oE "exit=[0-9]+" | tail -1 | cut -d= -f2)

echo
if [ "${CODE:-1}" = "0" ]; then
  echo "RESULT: PASS — the headless-built farm + bug population survived a server restart."
  exit 0
else
  echo "RESULT: FAIL — verify exit=${CODE:-?} (a restored-state assertion did not hold)."
  exit 1
fi
