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

CKDIR=".harness/.checkpoints"
mkdir -p "$CKDIR" 2>/dev/null || exit 0

PAYLOAD=$(hook_read_stdin)
TRIGGER=$(hook_json "$PAYLOAD" '.trigger')
TS=$(date -u +%Y%m%d-%H%M%S 2>/dev/null || echo now)
HEAD=$(git rev-parse --short HEAD 2>/dev/null || echo "?")
BRANCH=$(git symbolic-ref --quiet --short HEAD 2>/dev/null || echo "?")
NEXT=$(grep -oE '\*\*`R-[A-Za-z0-9-]+`\*\*' .harness/roadmap_status.md 2>/dev/null | head -1 | tr -d '`*')
PRS=$(hook_bounded 5 gh pr list --state open --json number,title --jq '.[]|"#\(.number) \(.title)"' 2>/dev/null | head -10)
DIRTY=$(git status --short 2>/dev/null | head -30)

OUT="$CKDIR/precompact-${TS}.md"
{
  echo "# Pre-compaction snapshot ${TS} (trigger=${TRIGGER:-?})"
  echo
  echo "- HEAD: \`${HEAD}\` on \`${BRANCH}\`"
  echo "- roadmap next-action: ${NEXT:-?}"
  echo "- open PRs:"
  printf '%s\n' "${PRS:-  (none)}" | sed 's/^/  - /'
  echo "- uncommitted:"
  printf '%s\n' "${DIRTY:-  (clean)}" | sed 's/^/  /'
} > "$OUT" 2>/dev/null || exit 0
cp "$OUT" "$CKDIR/precompact-latest.md" 2>/dev/null || true
exit 0
