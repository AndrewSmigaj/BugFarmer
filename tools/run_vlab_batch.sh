#!/usr/bin/env bash
# Run a list of village_21_lab campaign configs sequentially (each: snapshot→apply→run→chart→restore).
# Per-config nakama log is preserved at _data/nakama_<cfg>.log; charts in archive/<ts>_<cfg>/.
# Usage: bash tools/run_vlab_batch.sh <duration> <cfg1> <cfg2> ...
set -u
cd "$(dirname "$0")/.."
DUR="$1"; shift
for cfg in "$@"; do
  echo "=== BATCH: $cfg (duration $DUR) @ $(date +%H:%M) ==="
  python3 tools/run_config.py "$cfg" --zone village_21_lab --duration "$DUR" 2>&1 | tail -3
done
echo "=== BATCH COMPLETE ($# configs) @ $(date +%H:%M) ==="
