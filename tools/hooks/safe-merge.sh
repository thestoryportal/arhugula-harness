#!/usr/bin/env bash
# C-HE-07 allowlisted merge wrapper. Exact arity: `bash tools/hooks/safe-merge.sh <pr-number>`.
# Performs C-HE-06 steps (i)-(ix) by delegating to tools/merge_door.py; the ONLY merge string it
# ever issues is `gh pr merge <pr> --squash --match-head-commit <head_sha>` (inside merge_door).
# No flags are accepted or forwarded.
set -euo pipefail
[ "$#" -eq 1 ] || { echo "usage: safe-merge.sh <pr-number>" >&2; exit 64; }
case "$1" in ''|*[!0-9]*) echo "safe-merge: pr must be all digits" >&2; exit 64 ;; esac
: "${HARNESS_LANE_ID:?HARNESS_LANE_ID must be set (lane-init)}"
: "${HARNESS_ARC_ID:?HARNESS_ARC_ID must be set (roadmap-continue arc open)}"
cd "$(git rev-parse --show-toplevel)"
# Pre-lease availability guard (merge-gate r1, all three lenses; landed U-HE-25, kept as a
# permanent probe now that U-HE-28 shipped the flag): merge_door.land() runs the refresh
# AFTER the irreversible merge (check=True), so a checkout whose refresh CLI lacks
# `--emit-refresh-pr-json` would mark_blocked() the shared global lease post-merge
# (operator-only unblock). Abort HERE — before any lease is taken or merge attempted.
if ! uv run python tools/roadmap_status_refresh.py --help 2>/dev/null | grep -q -- --emit-refresh-pr-json; then
  echo "safe-merge: refresh producer flag --emit-refresh-pr-json unavailable in this checkout; aborting pre-lease" >&2
  exit 69
fi
exec uv run python tools/merge_door.py land "$1" --lane-id "$HARNESS_LANE_ID" --arc-id "$HARNESS_ARC_ID" \
  --refresh-cmd "uv run python tools/roadmap_status_refresh.py --emit-refresh-pr-json $1"
