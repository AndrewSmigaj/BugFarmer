#!/bin/sh
# End-to-end headless verification of SWARM_SPLIT / SWARM_MERGE.
#  1. Rebuild the Go module + restart nakama
#  2. Create two dynamic test zones:
#       split_test : one 30-bug fly swarm (over the 20 limit) -> SWARM_SPLIT at the 60s pass
#       merge_test : two 8-bug fly swarms spawned overlapping -> SWARM_MERGE at the 60s pass
#  3. Run the sync-harness ~80s on each and print the population events + counts
set -e
cd "$(dirname "$0")/.."

echo "=== 1. rebuild + restart server ==="
docker compose build builder | tail -1
docker compose up -d --force-recreate nakama | tail -1
sleep 8
docker compose logs nakama --since 15s 2>&1 | grep -E "module loaded successfully|Startup done" | tail -2

echo "=== 2. test zones ==="
python3 tools/world/make_test_zone.py --zone-id split_test --species fly_common \
  --initial 1 --max 4 --swarm-size 30 --spawn-radius 3 --dynamic | tail -2
python3 tools/world/make_test_zone.py --zone-id merge_test --species fly_common \
  --initial 2 --max 2 --swarm-size 8 --spawn-radius 1 --dynamic | tail -2
docker compose restart nakama > /dev/null 2>&1
sleep 6

echo "=== 3. harness build ==="
DOTNET=$(command -v dotnet || echo "$HOME/.dotnet/dotnet")
(cd tools/sync-harness && "$DOTNET" build -v quiet 2>&1 | grep -E "error|Build succeeded" | head -2)

echo "=== 4. SPLIT run (~80s: population pass fires at tick 600 = 60s) ==="
(cd tools/sync-harness && timeout 100 "$DOTNET" run --no-build -- --zone split_test --duration 80 --tag split 2>&1 \
  | grep -E "SWARM_SPLIT|SWARM_MERGE|SWARM swarm|POPULATION|maxAuthTick|Seeded" )

echo "=== 5. MERGE run (~80s) ==="
(cd tools/sync-harness && timeout 100 "$DOTNET" run --no-build -- --zone merge_test --duration 80 --tag merge 2>&1 \
  | grep -E "SWARM_SPLIT|SWARM_MERGE|SWARM swarm|POPULATION|maxAuthTick|Seeded" )

echo "=== server-side population log ==="
docker compose logs nakama --since 200s 2>&1 | grep -E "Split .*over-limit|Merged .*via SWARM_MERGE" | tail -4
echo "=== done ==="
