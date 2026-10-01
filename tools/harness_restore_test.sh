#!/usr/bin/env bash
# The restore round trip (D73) — no Unity. A scripted player with a real character in the test zone persist_a:
#
#   1. places 3 fences and leaves; the server restarts, and its start-up backup holds that moment (B1);
#   2. places 3 more (6 in the zone, 44 in the bag) and leaves; a second player makes a NEW character and visits
#      persist_b, which had no save yet — two things made after B1;
#   3. B1 is restored with the real tool (tools/saves/restore_backup.py): the zone must hold 3 fences and the bag 47
#      again, the new character and persist_b's save must be gone, the zone save and the character must be stored
#      with their usual permissions, and the server's safety copy (pre-restore/) must hold the 6-fence state;
#   4. that safety copy is restored — the restore undone: 6 in the zone, 44 in the bag, the new character and
#      persist_b's save back.
#
# It restores the WHOLE database to B1 and back, so run it when no one is playing: anything made by others between
# B1 and step 3 would be removed (and come back with step 4). On a pass it removes the four files it made in the backup
# folder (its two safety copies and the two used restore files), so test runs don't fill the owner's backup list.
# Exit 0 = every check passed.
# Usage: bash tools/harness_restore_test.sh
set -uo pipefail
cd "$(dirname "$0")/.."                      # repo root
DOTNET="$(command -v dotnet || echo "$HOME/.dotnet/dotnet")"
HARNESS="tools/sync-harness"
RUN="$(date -u +%m%d%H%M%S)"
LOGS="$(mktemp -d)"
DEV="restore-$RUN"
CHAR="Rst$RUN"                               # unique, so the character can be found in the backup files by name
NEW="New$RUN"                                # the character made after the backup
FOLDER="${BF_BACKUP_HOST_DIR:-$(cd .. && pwd)/BugFarmer_backups/world}"
FAILS=0
check() { if [ "$1" = 0 ]; then echo "  ok — $2"; else echo "  FAILED — $2"; FAILS=$((FAILS+1)); fi; }

player() { local log="$1"; shift
           ( cd "$HARNESS" && timeout 120 "$DOTNET" run --no-build -- --chunks 2 "$@" ) > "$LOGS/$log.log" 2>&1; }
healthy() { for i in $(seq 1 60); do
              docker compose ps --format '{{.Name}} {{.Status}}' 2>/dev/null | grep -q "nakama.*(healthy)" && return 0
              sleep 2
            done; echo "nakama is not healthy"; return 1; }
server_msgs() { docker compose logs --since "$1" nakama 2>/dev/null | sed -nE 's/.*"msg":"([^"]*)".*/\1/p'; }
count_line()  { grep -o "COUNT world=[0-9]* bag=[0-9]*" "$LOGS/$1.log" | tail -1; }
sql()         { docker compose exec -T postgres psql -U postgres -d nakama -At -c "$1"; }
made_after()  { echo "character $(sql "select count(*) from storage where collection='character' and value->>'name'='$NEW';"),"\
                     "persist_b $(sql "select count(*) from storage where collection='zone_state' and key='persist_b:world';")"; }
# Fences in the character's bag, in a backup file (found by the character's unique name).
bag_in() { python3 - "$1" "$CHAR" <<'PY'
import json, sys
f = json.load(open(sys.argv[1]))
for c in f["characters"]:
    if c["value"].get("name") == sys.argv[2]:
        print(sum(s.get("count", 0) for s in c["value"]["item_slots"] if s.get("item_id") == "fence_wood")); break
else:
    print("missing")
PY
}

echo "=== restore round trip, run $RUN — logs in $LOGS ==="
echo "[setup] fresh persist_a / persist_b (stop → wipe → start)"
docker compose stop nakama >/dev/null 2>&1
docker compose exec -T postgres psql -U postgres -d nakama -c "delete from storage where collection='zone_state' and
  (left(key, length('persist_a:')) = 'persist_a:' or left(key, length('persist_b:')) = 'persist_b:');" >/dev/null 2>&1
docker compose start nakama >/dev/null 2>&1; healthy || exit 1

echo "[1] place 3 fences, leave, restart: the start-up backup is B1"
player p1 --zone persist_a --device "$DEV" --char "$CHAR" --scenario fences-place --count 3
sleep 5                                       # persist_a holds a departing player's save back 3 s
SINCE="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
docker compose restart nakama >/dev/null 2>&1; healthy || exit 1; sleep 3
B1="$(server_msgs "$SINCE" | grep -o 'Backup (start-up) written: world-[0-9TZ-]*\.json' | grep -o 'world-.*\.json' | tail -1)"
[ -n "$B1" ] || { echo "  FAILED — no start-up backup was written"; exit 1; }
echo "  B1 = $B1 (bag $(bag_in "$FOLDER/$B1"))"
check "$([ "$(bag_in "$FOLDER/$B1")" = 47 ] && echo 0 || echo 1)" "B1 holds the bag after 3 fences (47)"

echo "[2] place 3 more and leave; a second player makes a new character and visits persist_b"
player p2 --zone persist_a --device "$DEV" --char "$CHAR" --scenario fences-place --count 3
player p2b --zone persist_b --device "$DEV-b" --char "$NEW" --scenario bag-count
sleep 12                                      # persist_b holds a departing player's save back 10 s
check "$([ "$(made_after)" = "character 1, persist_b 1" ] && echo 0 || echo 1)" "made after B1: [$(made_after)]"

echo "[3] restore B1 with the tool"
SINCE="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
python3 tools/saves/restore_backup.py "$B1" --yes > "$LOGS/restore1.log" 2>&1
check $? "the tool reports the restore applied"
sed 's/^/    /' "$LOGS/restore1.log" | grep "server:"
PRE="$(server_msgs "$SINCE" | grep -o 'pre-restore/pre-restore-[0-9TZ-]*\.json' | tail -1 | sed 's#pre-restore/##')"
player c1 --zone persist_a --device "$DEV" --char "$CHAR" --scenario fences-count
check "$([ "$(count_line c1)" = "COUNT world=3 bag=47" ] && echo 0 || echo 1)" "after the restore: 3 fences in the zone, 47 in the bag [$(count_line c1)]"
check "$([ -n "$PRE" ] && [ "$(bag_in "$FOLDER/pre-restore/$PRE")" = 44 ] && echo 0 || echo 1)" \
  "the safety copy ($PRE) holds the state before the restore (bag 44)"
check "$([ "$(made_after)" = "character 0, persist_b 0" ] && echo 0 || echo 1)" "what was made after B1 is gone [$(made_after)]"
PERMS="$(sql "select collection||':'||read||'/'||write from storage where (collection='zone_state' and key='persist_a:world')
  or (collection='character' and value->>'name'='$CHAR') order by 1;" | tr '\n' ' ')"
check "$([ "$PERMS" = "character:1/0 zone_state:2/0 " ] && echo 0 || echo 1)" "restored records keep their permissions [$PERMS]"
RECS="$(sql "select count(*) from storage where collection='restores';")"
check "$([ "${RECS:-0}" -ge 1 ] && echo 0 || echo 1)" "the restore is recorded ($RECS record(s))"

echo "[4] undo it: restore the safety copy"
SINCE="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
python3 tools/saves/restore_backup.py "$PRE" --yes > "$LOGS/restore2.log" 2>&1
check $? "the tool reports the undo applied"
PRE2="$(server_msgs "$SINCE" | grep -o 'pre-restore/pre-restore-[0-9TZ-]*\.json' | tail -1 | sed 's#pre-restore/##')"
player c2 --zone persist_a --device "$DEV" --char "$CHAR" --scenario fences-count
check "$([ "$(count_line c2)" = "COUNT world=6 bag=44" ] && echo 0 || echo 1)" "after the undo: 6 fences in the zone, 44 in the bag [$(count_line c2)]"
check "$([ "$(made_after)" = "character 1, persist_b 1" ] && echo 0 || echo 1)" "and what was made after B1 is back [$(made_after)]"

if [ "$FAILS" = 0 ]; then
  for f in "pre-restore/$PRE" "pre-restore/$PRE2" "restore/done/$B1" "restore/done/$PRE"; do
    [ -n "$f" ] && [ -f "$FOLDER/$f" ] && rm -f "$FOLDER/$f" && echo "  (removed this run's $f)"
  done
  echo "RESULT: PASS — restored, checked, and undone."; exit 0
fi
echo "RESULT: FAIL — $FAILS check(s) failed (logs in $LOGS)"; exit 1
