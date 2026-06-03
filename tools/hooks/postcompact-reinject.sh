#!/usr/bin/env bash
# PostCompact context re-inject — after compaction completes, surface the
# pre-compaction checkpoint pointer (written by U-HK-05) + the roadmap next-action
# + a nudge to re-run the §12.1 audit, so the thread survives the context reset.
#
# Note: SessionStart(source=compact) ALSO fires after compaction and the existing
# session-start.sh re-injects the full roadmap audit there. This hook adds the one
# thing that audit lacks — the checkpoint pointer (in-flight/uncommitted state) —
# kept concise to avoid double-injection noise.
#
# Trigger: PostCompact, matcher "*". Context-only (cannot block).

set -uo pipefail

_LIB="$(dirname "${BASH_SOURCE[0]}")/lib.sh"
[ -f "$_LIB" ] || exit 0
# shellcheck source=lib.sh
. "$_LIB"

PROJECT_DIR=$(hook_project_dir)
[ -z "$PROJECT_DIR" ] && exit 0
cd "$PROJECT_DIR" || exit 0

NEXT=$(grep -oE '\*\*`R-[A-Za-z0-9-]+`\*\*' .harness/roadmap_status.md 2>/dev/null | head -1 | tr -d '`*')
HEAD=$(git rev-parse --short HEAD 2>/dev/null || echo "?")
BRANCH=$(git symbolic-ref --quiet --short HEAD 2>/dev/null || echo "?")

CK=".harness/.checkpoints/precompact-latest.md"
CKNOTE=""
[ -f "$CK" ] && CKNOTE=" Pre-compaction snapshot (in-flight/uncommitted state): ${CK} — read it to recover the thread."

hook_emit "PostCompact" "[CONTEXT] Post-compaction on \`${BRANCH}\` @ \`${HEAD}\`; roadmap next-action=${NEXT:-?}. Re-run the §12.1 session-start audit before acting.${CKNOTE}"
