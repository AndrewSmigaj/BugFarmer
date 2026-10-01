#!/usr/bin/env bash
# Autonomous zone/farm-persistence regression test — no Unity required.
#
# A headless scripted client (tools/sync-harness, --scenario) builds a farm in sim_test, the server is
# stopped cleanly (the zone writes its final save) and started again (clearing the in-memory match → forces a real
# load from storage), and a second client rejoins and ASSERTS the farm + bug population came back. Exit 0 = PASS.
#
# Usage:  bash tools/harness_persist_test.sh
set -uo pipefail
cd "$(dirname "$0")/.."                     # repo root
DOTNET="$(command -v dotnet || echo "$HOME/.dotnet/dotnet")"
HARNESS="tools/sync-harness"
ZONE="sim_test"

run_harness() { ( cd "$HARNESS" && timeout 90 "$DOTNET" run -- "$@" ); }
# A clean stop saves every zone (MatchTerminate's final save), so the server must be STOPPED while a zone is
# wiped — wiping a running server's zone just has its final save write it straight back.
stop_nakama()  { docker compose stop nakama >/dev/null 2>&1; }
start_nakama() { local since; since="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
                 docker compose start nakama >/dev/null 2>&1
                 for i in $(seq 1 40); do
                   docker compose logs --since "$since" nakama 2>&1 | grep -q "module loaded successfully" && sleep 2 && return 0
                   sleep 1
                 done
                 echo "    nakama did not come back up"; return 1; }
# Exactly the keys of THIS zone: a plain prefix compare on "<zone>:". In LIKE, '_' is a wildcard, and a bare
# '<zone>%' also catches other zones whose names start the same (wiping village_21 took village_21_B with it).
wipe_zone()    { docker compose exec -T postgres psql -U postgres -d nakama \
                  -c "delete from storage where collection='zone_state' and left(key, length('${ZONE}:')) = '${ZONE}:';" >/dev/null 2>&1; }

echo "=== zone/farm persistence test (${ZONE}) ==="

echo "[1/6] stop nakama, wipe ${ZONE}, start nakama (a truly pristine zone)"
stop_nakama; wipe_zone; start_nakama
echo "[2/6] farm-build (headless client places a farm)"
run_harness --scenario farm-build --zone "$ZONE" --tag build 2>&1 | sed 's/^/    /' | grep -iE "scenario|local view|WorldError|exit=" || true
echo "[3/6] clean stop (the zone's final save) + start"
# Let the build client's own leave-save (the empty-zone save, same tick — an empty zone is paused) land well BEFORE
# the stop, so "stored at or after the stop began" can only be the shutdown save.
sleep 3
STOP_AT="$(date -u +%s)"; STOP_SINCE="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
stop_nakama
FINAL_LINE="$(docker compose logs --since "$STOP_SINCE" nakama 2>&1 | grep -o "Zone ${ZONE}: final save on shutdown — world (tick [0-9]*)" | head -1)"
FINAL_TICK="$(echo "$FINAL_LINE" | grep -oE "tick [0-9]+" | grep -oE "[0-9]+")"
# Read the stored document NOW, while the server is stopped: nothing but the clean stop can have written it since
# STOP_AT. (Later in the test the verify client's own leave saves the zone again, so reading it at the end proves
# nothing about the shutdown save.)
psql_q() { docker compose exec -T postgres psql -U postgres -d nakama -Atc "$1" 2>/dev/null; }
STOPPED_SAVED_AT="$(psql_q "select value->>'saved_at' from storage where collection='zone_state' and key='${ZONE}:world';")"
STOPPED_TICK="$(psql_q "select value->>'tick' from storage where collection='zone_state' and key='${ZONE}:world';")"
echo "    ${FINAL_LINE:-<no final-save line in the log>}; stored while stopped: tick=${STOPPED_TICK:-?} saved_at=${STOPPED_SAVED_AT:-?}"
start_nakama
echo "[4/6] farm-verify (rejoin from storage + assert)"
VERIFY_OUT="$(run_harness --scenario farm-verify --zone "$ZONE" --tag verify 2>&1)"
echo "$VERIFY_OUT" | sed 's/^/    /' | grep -iE "assert|exit=" || true
CODE=$(echo "$VERIFY_OUT" | grep -oE "exit=[0-9]+" | tail -1 | cut -d= -f2)

# [6/6] Inspect the STORED document directly (the §P format gate): the save must be the ONE
# WorldSave document (":world"), version 1, with a RESUMED clock (tick > 0), the cell diff, the
# swarm population, and the weather/day fields present in the JSON — and NO legacy multi-record
# save (":meta") left behind. This catches "verify passed off the legacy path" false-greens.
echo "[5/6] inspect the stored WorldSave document"
DOC_CHECK="$(psql_q "select (value->>'version')='1'
    and coalesce((value->>'tick')::bigint,0) > 0
    and jsonb_array_length(coalesce(value->'cell_edits','[]'::jsonb)) > 0
    and jsonb_array_length(coalesce(value->'swarms','[]'::jsonb)) > 0
    and value ? 'last_rollover_day'
  from storage where collection='zone_state' and key='${ZONE}:world';")"
LEGACY_LEFT="$(psql_q "select count(*) from storage where collection='zone_state' and key='${ZONE}:meta';")"
DOC_TICK="$(psql_q "select value->>'tick' from storage where collection='zone_state' and key='${ZONE}:world';")"
echo "    world doc ok=${DOC_CHECK:-<missing>} tick=${DOC_TICK:-?} legacy_meta_records=${LEGACY_LEFT:-?}"
# [6/6] The clean stop itself saved the zone: while the server was stopped, the stored document had been written
# at or after the stop began, at the tick the final-save line reports. (The empty-zone save when the build client
# left happened BEFORE the stop, so this fails if the shutdown save didn't run.)
echo "[6/6] the clean stop wrote the zone's final save"
FINAL_OK=f
if [ -n "$FINAL_LINE" ] && [ -n "$STOPPED_SAVED_AT" ] && [ "$STOPPED_SAVED_AT" -ge "$STOP_AT" ] \
   && [ -n "$FINAL_TICK" ] && [ "$STOPPED_TICK" = "$FINAL_TICK" ]; then FINAL_OK=t; fi
echo "    while stopped: saved_at=${STOPPED_SAVED_AT:-?} (stop began ${STOP_AT}), tick=${STOPPED_TICK:-?} (final-save line says ${FINAL_TICK:-?}) → ${FINAL_OK}"

echo
if [ "${CODE:-1}" = "0" ] && [ "$DOC_CHECK" = "t" ] && [ "${LEGACY_LEFT:-1}" = "0" ] && [ "$FINAL_OK" = "t" ]; then
  echo "RESULT: PASS — farm + bugs survived the restart, the clean stop wrote the zone's final save, AND the stored save is the one WorldSave document (resumed clock, cell diff, swarms; no legacy records)."
  exit 0
else
  echo "RESULT: FAIL — verify exit=${CODE:-?}, doc_check=${DOC_CHECK:-<missing>}, legacy_meta=${LEGACY_LEFT:-?}, final_save=${FINAL_OK}."
  exit 1
fi
