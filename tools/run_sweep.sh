#!/usr/bin/env bash
# Run a list of bug-ecology tuning configs SEQUENTIALLY (they share one nakama server + the canonical
# data files, so they can't overlap). Each config runs end-to-end via run_config.py (apply → restart →
# harness → chart → RESTORE) under a hard timeout; a failure is logged and the sweep continues. At the
# end it prints the compare_configs scoreboard. Usage:
#
#   tools/run_sweep.sh 250 A1_reach_vision_lo A2_reach_vision_hi ...     # explicit list, 250s each
#   tools/run_sweep.sh                                                   # default: all A*/B*/C*/D* @ 250s
#
# Built for overnight autonomy: ~5 min/config, restores canonical data after every run.
set -u
cd "$(dirname "$0")/.."

DUR="${1:-250}"
case "$DUR" in (*[!0-9]*) DUR=250 ;; (*) shift || true ;; esac   # if $1 isn't a number, keep it as a config

CONFIGS=("$@")
if [ "${#CONFIGS[@]}" -eq 0 ]; then
  mapfile -t CONFIGS < <(ls tools/bug_lab_configs/ | grep -E '^[ABCD][0-9]+_.*\.json$' | sed 's/\.json$//' | sort)
fi

STAMP="$(date +%Y%m%d_%H%M%S)"
LOG="tools/_generated/sweep_${STAMP}.log"
mkdir -p tools/_generated
echo "=== sweep ${STAMP}: ${#CONFIGS[@]} configs @ ${DUR}s each (~$(( ${#CONFIGS[@]} * 5 )) min) ===" | tee "$LOG"

i=0
for cfg in "${CONFIGS[@]}"; do
  i=$((i+1))
  echo "" | tee -a "$LOG"
  echo "### [$i/${#CONFIGS[@]}] $cfg  ($(date +%H:%M:%S))" | tee -a "$LOG"
  if timeout 760 python3 tools/run_config.py "$cfg" --duration "$DUR" >>"$LOG" 2>&1; then
    echo "    ok" | tee -a "$LOG"
  else
    echo "    !! FAILED (exit $?) — continuing" | tee -a "$LOG"
  fi
done

echo "" | tee -a "$LOG"
echo "=== sweep done — scoreboard ===" | tee -a "$LOG"
python3 tools/compare_configs.py "${CONFIGS[@]}" 2>&1 | tee -a "$LOG"
echo "" | tee -a "$LOG"
echo "log: $LOG"
