#!/usr/bin/env bash
# Classify whether a CI event's changed-file set is EXACTLY a §12.2.1 terminating
# refresh — i.e. `.harness/roadmap_status.md` and nothing else.
#
# Extracted from an inline `run:` block in `.github/workflows/ci.yml` so it can carry a
# hermetic test suite (`test_classify_refresh_scope.sh`, auto-discovered by
# `tools/codex-parity-check.sh`). The inline version shipped two behaviour-changing
# defects that only ad-hoc review caught — a `HEAD^ HEAD` range that ignored all but the
# last commit of a multi-commit push, and a job-level gate that concluded `skipped`. Logic
# that decides whether the blocking test/typecheck/axis-isolation jobs run at all belongs
# behind a regression witness, not in a YAML string.
#
# CONTRACT
#   Writes `refresh_only=true|false` to $GITHUB_OUTPUT when set, and always echoes the
#   same value to stdout (which is what the tests read).
#
#   Inputs, all optional, read from the environment:
#     BASE_SHA       PR base SHA          -> compare BASE_SHA...HEAD
#     PUSH_BEFORE    ref tip before push  -> compare PUSH_BEFORE..HEAD
#     CHANGED_FILES  explicit newline-separated list; bypasses git entirely (tests)
#
# FAIL CLOSED. Every uncertain path yields `false`, i.e. run the full matrix:
#   * neither BASE_SHA nor a usable PUSH_BEFORE
#   * PUSH_BEFORE all-zeros (branch creation) or unreachable (force-push)
#   * a git failure, or an empty diff
#   * ANY path other than the one blessed file
# Because the predicate is set EQUALITY against a single literal path, any code file in
# the diff makes the set unequal — the fast path can never let a code change through.

set -uo pipefail

REFRESH_ONLY_PATH='.harness/roadmap_status.md'

emit() {
  # $1 = true|false
  if [ -n "${GITHUB_OUTPUT:-}" ]; then
    echo "refresh_only=$1" >>"$GITHUB_OUTPUT"
  fi
  echo "$1"
}

if [ -n "${CHANGED_FILES+x}" ]; then
  changed="$CHANGED_FILES"
elif [ -n "${BASE_SHA:-}" ]; then
  changed="$(git diff --name-only "$BASE_SHA"...HEAD 2>/dev/null)" || changed=""
elif [ -n "${PUSH_BEFORE:-}" ] &&
  [ "$PUSH_BEFORE" != "0000000000000000000000000000000000000000" ] &&
  git cat-file -e "${PUSH_BEFORE}^{commit}" 2>/dev/null; then
  # The WHOLE push range, not HEAD^..HEAD: a push can carry many commits, and one whose
  # final commit touches only the blessed file while an earlier one touches code must NOT
  # take the fast path.
  changed="$(git diff --name-only "$PUSH_BEFORE" HEAD 2>/dev/null)" || changed=""
else
  echo "push/PR range unavailable — running the full matrix (fail-closed)" >&2
  emit false
  exit 0
fi

if [ -z "$changed" ]; then
  echo "empty or unreadable diff — running the full matrix (fail-closed)" >&2
  emit false
  exit 0
fi

# `grep -vFx` is fixed-string AND whole-line: `x.harness/roadmap_status.md` and
# `.harness/roadmap_status.md.bak` are correctly NOT the blessed path.
other="$(printf '%s\n' "$changed" | grep -vFx "$REFRESH_ONLY_PATH" || true)"
if [ -z "$other" ]; then
  echo "terminating-refresh shape — skipping pytest/pyright/axis-isolation/coverage" >&2
  emit true
else
  emit false
fi
