#!/bin/sh
# Run ALL the Go unit tests (world, entities, rpc) inside the builder toolchain image.
# Bind-mounts the LIVE source over /backend so tests run against the working tree
# (the builder image bakes a COPY of the source at build time). nakama/data is mounted read-only at /data
# so tests that check the real game data (zone_links_test.go) see it at ../../data, as in the repo.
#
# The exit code is go test's own: output goes to a temp file and only its tail is printed, because
# piping into `tail` would hide a failure behind tail's success (it once did — see the memory
# "FRESH != deploy + pipe masking").
cd "$(dirname "$0")/.."
LOG=$(mktemp)
docker compose run --rm \
  --volume "$(pwd)/nakama/modules:/backend" \
  --volume "$(pwd)/nakama/data:/data:ro" \
  --entrypoint sh builder \
  -c "cd /backend && go test ./... -count=1" >"$LOG" 2>&1
STATUS=$?
tail -40 "$LOG"
rm -f "$LOG"
exit $STATUS
