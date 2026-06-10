#!/bin/sh
# Run the Go unit tests for the world module inside the builder toolchain image.
# Bind-mounts the LIVE source over /backend so tests run against the working tree
# (the builder image bakes a COPY of the source at build time).
cd "$(dirname "$0")/.."
docker compose run --rm \
  --volume "$(pwd)/nakama/modules:/backend" \
  --entrypoint sh builder \
  -c "cd /backend && go test ./world/ -count=1 -v" 2>&1 | tail -30
