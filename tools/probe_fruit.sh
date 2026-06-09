#!/bin/sh
# Quick probe: join repro_test for 60s and report fruit/food/swarm activity.
cd "$(dirname "$0")/../tools/sync-harness"
DOTNET=$(command -v dotnet || echo "$HOME/.dotnet/dotnet")
timeout 80 "$DOTNET" run --no-build -- --zone repro_test --duration 60 --tag probe 2>&1 \
  | grep -E "ITEM_ROTTED|FOOD_CONSUMED|SWARM_REPRODUCED|SWARM swarm|POPULATION"
