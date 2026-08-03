#!/usr/bin/env bash
# PostToolUse(Edit|Write) lint-on-edit. After Claude edits a .py file, run ruff on
# JUST that file and inject any findings as additionalContext; after a .yaml/.yml
# edit, parse-check that file with pyyaml instead. NON-BLOCKING by design
# (PostToolUse cannot undo — it only informs; the Stop gate / CI ruff + ledger jobs
# are the hard enforcement). Silent when the file is clean. Bounded so it can't hang.
#
# Trigger: PostToolUse, matcher "Edit|Write|MultiEdit". Early-exits for every other
# extension. The .py branch prefers a `ruff` on PATH; falls back to `uv run ruff`.
# The .yaml branch prefers the repo `.venv/bin/python` (pyyaml is already a dev dep
# at pyproject.toml) and falls back to `uv run --quiet python` — NEVER
# `uv run --with`, which would build an ephemeral env on every single edit.
#
# The YAML check's limit, stated honestly: a parse check catches unquoted `: `
# scalars (`title: fix: thing`) and indentation/tab errors. It does NOT catch
# ` #NNN` comment-truncation — `notes: shipped in #1189` is VALID YAML whose value
# silently truncates at the `#`. No `#`-regex advisory is added here on purpose: it
# is false-positive-heavy, the same rejection class as HARDENING_PLAN D3/D13.

set -uo pipefail

_LIB="$(dirname "${BASH_SOURCE[0]}")/lib.sh"
[ -f "$_LIB" ] || exit 0
# shellcheck source=lib.sh
. "$_LIB"

PROJECT_DIR=$(hook_project_dir)
[ -z "$PROJECT_DIR" ] && exit 0
cd "$PROJECT_DIR" || exit 0

PAYLOAD=$(hook_read_stdin)
FILE=$(hook_json "$PAYLOAD" '.tool_input.file_path')
[ -z "$FILE" ] && exit 0
case "$FILE" in *.py) KIND=py ;; *.yaml|*.yml) KIND=yaml ;; *) exit 0 ;; esac
[ -f "$FILE" ] || exit 0

export UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/arhugula-uv-cache}"

# Parse-check a single YAML file. Bounded; prefer the repo venv's python (pyyaml is
# already installed there), else `uv run --quiet python`. The checker itself always
# exits 0 — a YAMLError is reported on stdout (str(e) carries "line N, column M"),
# so no rc ever leaks through hook_bounded and nothing else is treated as a finding.
if [ "$KIND" = yaml ]; then
  if [ -x "$PROJECT_DIR/.venv/bin/python" ]; then
    YAML_PY=("$PROJECT_DIR/.venv/bin/python")
  else
    YAML_PY=(uv run --quiet python)
  fi
  YAML_OUT=$(hook_bounded 10 "${YAML_PY[@]}" -c '
import sys, yaml
try:
    list(yaml.safe_load_all(open(sys.argv[1])))
except yaml.YAMLError as e:
    print(str(e))
' "$FILE" 2>/dev/null)

  [ -z "$YAML_OUT" ] && exit 0   # parses → stay silent (no noise on good edits)

  hook_emit "PostToolUse" "[yaml] parse error in ${FILE}:
${YAML_OUT}
(advisory — CI ledger checks are the hard gate)"
fi

# Lint the single file (concise). Bounded; prefer a direct ruff, else uv run ruff.
# `ruff format --check` reports files that would be reformatted; combine with check
# findings (the CI ruff job runs both). grep/sed keep format's exit off RUFF_OUT.
RUFF_OUT=$(hook_bounded 20 bash -c '
  if command -v ruff >/dev/null 2>&1; then RUFF=(ruff); else RUFF=(uv run --quiet ruff); fi
  "${RUFF[@]}" check --quiet --output-format=concise "$1"
  "${RUFF[@]}" format --check "$1" 2>/dev/null | grep -qi "would be reformatted" \
    && printf "format: %s needs ruff format\n" "$1"
' _ "$FILE" 2>/dev/null)

[ -z "$RUFF_OUT" ] && exit 0   # clean → stay silent (no noise on good edits)

hook_emit "PostToolUse" "[lint] ruff findings on ${FILE}:
${RUFF_OUT}
(advisory — fix before the Stop gate / CI ruff job)"
