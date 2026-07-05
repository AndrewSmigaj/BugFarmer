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
echo "[3/6] farm-build (headless client places a farm)"
run_harness --scenario farm-build --zone "$ZONE" --tag build 2>&1 | sed 's/^/    /' | grep -iE "scenario|local view|WorldError|exit=" || true
echo "[4/6] restart nakama (force MatchTerminate save + drop in-memory match)";  restart
echo "[5/6] farm-verify (rejoin from storage + assert)"
VERIFY_OUT="$(run_harness --scenario farm-verify --zone "$ZONE" --tag verify 2>&1)"
echo "$VERIFY_OUT" | sed 's/^/    /' | grep -iE "assert|exit=" || true
CODE=$(echo "$VERIFY_OUT" | grep -oE "exit=[0-9]+" | tail -1 | cut -d= -f2)

# [6/6] Inspect the STORED document directly (the §P format gate): the save must be the ONE
# WorldSave document (":world"), version 1, with a RESUMED clock (tick > 0), the cell diff, the
# swarm population, and the weather/day fields present in the JSON — and NO legacy multi-record
# save (":meta") left behind. This catches "verify passed off the legacy path" false-greens.
echo "[6/6] inspect the stored WorldSave document"
psql_q() { docker compose exec -T postgres psql -U postgres -d nakama -Atc "$1" 2>/dev/null; }
DOC_CHECK="$(psql_q "select (value->>'version')='1'
    and coalesce((value->>'tick')::bigint,0) > 0
    and jsonb_array_length(coalesce(value->'cell_edits','[]'::jsonb)) > 0
    and jsonb_array_length(coalesce(value->'swarms','[]'::jsonb)) > 0
    and value ? 'last_rollover_day'
  from storage where collection='zone_state' and key='${ZONE}:world';")"
LEGACY_LEFT="$(psql_q "select count(*) from storage where collection='zone_state' and key='${ZONE}:meta';")"
DOC_TICK="$(psql_q "select value->>'tick' from storage where collection='zone_state' and key='${ZONE}:world';")"
echo "    world doc ok=${DOC_CHECK:-<missing>} tick=${DOC_TICK:-?} legacy_meta_records=${LEGACY_LEFT:-?}"

echo
if [ "${CODE:-1}" = "0" ] && [ "$DOC_CHECK" = "t" ] && [ "${LEGACY_LEFT:-1}" = "0" ]; then
  echo "RESULT: PASS — farm + bugs survived the restart, AND the stored save is the one WorldSave document (resumed clock, cell diff, swarms; no legacy records)."
  exit 0
else
  echo "RESULT: FAIL — verify exit=${CODE:-?}, doc_check=${DOC_CHECK:-<missing>}, legacy_meta=${LEGACY_LEFT:-?}."
  exit 1
fi
