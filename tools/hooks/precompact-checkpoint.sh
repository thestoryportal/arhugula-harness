#!/usr/bin/env bash
# PreCompact checkpoint — fires before context compaction. Writes a lightweight
# state snapshot to .harness/.checkpoints/ so the essentials survive compaction
# (U-HK-06 re-injects it after). A safety-net complement to the richer /context-save
# skill, not a replacement. Gitignored — never dirties the tree. Wired SYNCHRONOUSLY
# (not async): PostCompact reinject reads precompact-latest.md, so the write must
# finish before compaction completes or the snapshot races its own reader and the
# in-flight context is lost. The one slow call (gh pr list) is hook_bounded 5, so
# the synchronous cost is capped at a few seconds.
#
# Trigger: PreCompact, matcher "manual"|"auto" (distinguishes /compact from auto).

set -uo pipefail

_LIB="$(dirname "${BASH_SOURCE[0]}")/lib.sh"
[ -f "$_LIB" ] || exit 0
# shellcheck source=lib.sh
. "$_LIB"

PROJECT_DIR=$(hook_project_dir)
[ -z "$PROJECT_DIR" ] && exit 0
cd "$PROJECT_DIR" || exit 0

PAYLOAD=$(hook_read_stdin)
TRIGGER=$(hook_json "$PAYLOAD" '.trigger')
# Snapshot via the shared writer (U-HK-27 extracted this). At compaction we are NOT on a
# hot path, so include the open-PRs gh lookup (no skip_gh).
hook_write_checkpoint "Pre-compaction snapshot (trigger=${TRIGGER:-?})"
exit 0
