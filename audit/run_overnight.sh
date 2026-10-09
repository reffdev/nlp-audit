#!/usr/bin/env bash
# Overnight queue (local model only; no Phase 3). Each step logs to data/overnight.log and the next step
# runs even if one fails. Watch with:  tail -f data/overnight.log
cd "$(dirname "$0")/.." || exit 1
export PYTHONIOENCODING=utf-8
PY="${PYTHON:-python}"
"$PY" -c "import openai, pdfplumber, sklearn" || { echo "python env check failed" >> data/overnight.log; exit 1; }
LOG=data/overnight.log
step() { echo; echo "===== $(date '+%F %T') $1 ====="; }
{
  step "1/3 decoy test (does a confident 'found' mean anything?)"
  "$PY" -u audit/decoy_test.py; echo "exit $?"
  step "2/3 continue the 21 sampled items (weak 2-of-3 matches go to rounds 2-3)"
  "$PY" -u audit/xref_search.py --group sample --resume; echo "exit $?"
  step "3/3 search the remaining 59 items"
  "$PY" -u audit/xref_search.py --group rest; echo "exit $?"
  step "summary"
  "$PY" -u audit/search_summary.py
  step "done"
} >> "$LOG" 2>&1
