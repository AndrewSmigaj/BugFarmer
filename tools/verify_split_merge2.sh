#!/bin/sh
# Round 2: capture the DECODED SWARM_SPLIT event with the fixed harness, and give the
# merge better odds (4 swarms spawned together, ~3 population passes).
set -e
cd "$(dirname "$0")/.."

echo "=== harness rebuild (CS0136 fixed) ==="
DOTNET=$(command -v dotnet || echo "$HOME/.dotnet/dotnet")
(cd tools/sync-harness && "$DOTNET" build -v quiet 2>&1 | grep -E "error|Build succeeded" | head -3)

echo "=== fresh zones ==="
python3 tools/make_test_zone.py --zone-id split_test2 --species fly_common \
  --initial 1 --max 4 --swarm-size 30 --spawn-radius 3 --dynamic | tail -1
python3 tools/make_test_zone.py --zone-id merge_test2 --species fly_common \
  --initial 4 --max 4 --swarm-size 5 --spawn-radius 1 --dynamic | tail -1
docker compose restart nakama > /dev/null 2>&1
sleep 6

echo "=== SPLIT run (80s) - expect a decoded SWARM_SPLIT event ==="
(cd tools/sync-harness && timeout 100 "$DOTNET" run --no-build -- --zone split_test2 --duration 80 --tag s2 2>&1 \
  | grep -E "SWARM_SPLIT|SWARM_MERGE|SWARM swarm|POPULATION|  SWARM" )

echo "=== MERGE run (200s = 3 population passes; 4 swarms of 5, cap 20) ==="
(cd tools/sync-harness && timeout 220 "$DOTNET" run --no-build -- --zone merge_test2 --duration 200 --tag m2 2>&1 \
  | grep -E "SWARM_SPLIT|SWARM_MERGE|SWARM swarm|POPULATION|  SWARM" )

echo "=== server population log ==="
docker compose logs nakama --since 320s 2>&1 | grep -E "Split .*over-limit|Merged .*SWARM_MERGE" | tail -5
echo "=== done ==="
