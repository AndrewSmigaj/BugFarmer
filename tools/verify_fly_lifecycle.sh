#!/bin/sh
# End-to-end verification of the FLY LIFECYCLE (feed -> reproduce -> split -> plateau).
#  1. test-tree sprite + publish entities (gates block bugs, compost station, tree_apple_test)
#  2. Go unit tests (consumption thresholds, reproduce bookkeeping, station drain)
#  3. build repro_test zone + rebuild/restart the server
#  4. ~6-minute headless run: watch ITEM_ROTTED -> FOOD_CONSUMED -> SWARM_REPRODUCED -> SWARM_SPLIT
#  5. plot the population curve -> tools/output/fly_counts.png
set -e
cd "$(dirname "$0")/.."

echo "=== 1. sprite + publish ==="
cp -f BugFarmerClient/Assets/Resources/Objects/tree_apple.png BugFarmerClient/Assets/Resources/Objects/tree_apple_test.png
python3 tools/publish_entities.py | tail -1

echo "=== 2. Go unit tests ==="
sh tools/run_go_tests.sh | tail -16

echo "=== 3. zone + server ==="
python3 tools/zonegen/scenes/zone_repro_test.py | tail -2
docker compose build builder | tail -1
docker compose up -d --force-recreate nakama | tail -1
sleep 8
docker compose logs nakama --since 15s 2>&1 | grep -cE "module loaded successfully|Startup done" || true

echo "=== 4. lifecycle run (360s) ==="
DOTNET=$(command -v dotnet || echo "$HOME/.dotnet/dotnet")
(cd tools/sync-harness && "$DOTNET" build -v quiet 2>&1 | grep -E "error|Build succeeded" | head -3)
(cd tools/sync-harness && timeout 390 "$DOTNET" run --no-build -- --zone repro_test --duration 360 --tag fly 2>&1 \
  | grep -E "ITEM_ROTTED|FOOD_CONSUMED|SWARM_REPRODUCED|SWARM_SPLIT|SWARM_MERGE|SWARM swarm|POPULATION|reproduced|series" )

echo "=== 5. plot ==="
python3 tools/plot_fly_counts.py || echo "(matplotlib missing? pip install matplotlib)"

echo "=== server lifecycle log ==="
docker compose logs nakama --since 420s 2>&1 | grep -E "reproduced|Split .*over-limit|rotted" | tail -8
echo "=== done ==="
