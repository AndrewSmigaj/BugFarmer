#!/bin/sh
# One-off e2e MERGE capture: temporarily widen fly_common merge_radius (2.5 -> 12.0) so
# wandering swarms WILL overlap at the population pass, capture the SWARM_MERGE event,
# then RESTORE 2.5. The strict 2.5 stays the real game value.
set -e
cd "$(dirname "$0")/.."

python3 - <<'PY'
import json
p='nakama/data/species.json'; d=json.load(open(p))
d['fly_common']['merge_radius']=12.0
json.dump(d,open(p,'w'),indent=2)
print('merge_radius -> 12.0 (temporary)')
PY
python3 tools/make_test_zone.py --zone-id merge_test3 --species fly_common \
  --initial 2 --max 2 --swarm-size 8 --spawn-radius 2 --dynamic | tail -1
docker compose restart nakama > /dev/null 2>&1
sleep 6

DOTNET=$(command -v dotnet || echo "$HOME/.dotnet/dotnet")
echo "=== MERGE run (80s, radius 12 so the pass catches them) ==="
(cd tools/sync-harness && timeout 100 "$DOTNET" run --no-build -- --zone merge_test3 --duration 80 --tag m3 2>&1 \
  | grep -E "SWARM_MERGE|SWARM_SPLIT|SWARM swarm|POPULATION|  SWARM" )

echo "=== restore merge_radius 2.5 ==="
python3 - <<'PY'
import json
p='nakama/data/species.json'; d=json.load(open(p))
d['fly_common']['merge_radius']=2.5
json.dump(d,open(p,'w'),indent=2)
print('merge_radius restored -> 2.5')
PY
docker compose restart nakama > /dev/null 2>&1
echo "=== server log ==="
docker compose logs nakama --since 130s 2>&1 | grep -E "Merged .*SWARM_MERGE" | tail -3
echo "=== done ==="
