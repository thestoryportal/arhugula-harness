#!/usr/bin/env bash
# UserPromptSubmit skill-activation validation (U-HK-21). When the operator types a
# slash-command in the prompt, verify it resolves to a KNOWN skill (project, user, or
# a built-in Claude Code command). If it resolves to nothing but is a near-miss of a
# real skill name, surface a "did you mean" hint so a mistyped `/skill` invocation is
# caught before it silently no-ops.
#
# SILENT-WHEN-CORRECT is the load-bearing AC (three hooks now share UserPromptSubmit:
# prompt-context U-HK-08 + this + prompt-lint U-HK-22, all per-prompt). It emits a hint
# ONLY when a typed `/cmd` is (a) NOT a known project skill, (b) NOT a known user skill,
# (c) NOT a built-in command, AND (d) within near-match of a real skill. Anything that
# resolves, or has no plausible correction, stays quiet — so a legit but locally-unknown
# command (a plugin, a new built-in) never produces a false warning.
#
# Fast + non-network + always-exit-0 (UserPromptSubmit 30s budget; this is pure local
# filesystem lookups). Trigger: UserPromptSubmit (no matcher).

set -uo pipefail

_LIB="$(dirname "${BASH_SOURCE[0]}")/lib.sh"
[ -f "$_LIB" ] || exit 0
# shellcheck source=lib.sh
. "$_LIB"

PROJECT_DIR=$(hook_project_dir)
[ -z "$PROJECT_DIR" ] && exit 0

PAYLOAD=$(hook_read_stdin)
PROMPT=$(hook_json "$PAYLOAD" '.prompt')
[ -z "$PROMPT" ] && exit 0

# Built-in Claude Code slash commands that are NOT skills (never warn on these).
# Conservative superset — better to miss a typo than warn on a real built-in.
_BUILTINS=" clear compact help config model fast review continue resume init add-dir \
agents bug cost doctor exit login logout mcp memory permissions pr-comments release-notes \
status terminal-setup vim ide hooks export rewind usage code-review security-review verify \
run loop schedule simplify library graphify resolve loop-start loop-stop fewer-permission-prompts "

# Collect known skill names from project + user skill directories.
_skill_dirs=("$PROJECT_DIR/.claude/skills" "$HOME/.claude/skills")
_known=""
for sd in "${_skill_dirs[@]}"; do
  [ -d "$sd" ] || continue
  while IFS= read -r d; do
    [ -f "$sd/$d/SKILL.md" ] && _known="$_known $d "
  done < <(ls -1 "$sd" 2>/dev/null)
done

# Extract leading-token slash-commands from the prompt. A skill invocation is a `/name`
# at a word boundary; names are kebab/colon (plugin:skill). Ignore `//`, paths like
# `a/b`, and http(s):// URLs. We only consider tokens that START a word (prev char is
# whitespace or string start) to avoid matching `foo/bar` path fragments.
_cmds=$(printf '%s' "$PROMPT" \
  | grep -oE '(^|[[:space:]])/[a-z][a-z0-9:_-]+' 2>/dev/null \
  | sed -E 's#^[[:space:]]*/##' | sort -u)
[ -z "$_cmds" ] && exit 0

# near-match: does $1 share a >=4-char common prefix with, or is a substring of (or
# superstring of), any known skill name? Echoes the first matching known name.
_near() {
  local q="$1" k pfx
  for k in $_known; do
    # substring either direction (typo by truncation / extra suffix)
    case "$k" in *"$q"*) printf '%s' "$k"; return 0;; esac
    case "$q" in *"$k"*) printf '%s' "$k"; return 0;; esac
    # >=4-char shared prefix
    pfx=$(printf '%s\n%s\n' "$q" "$k" | sed -e 'N;s/\(.*\).*\n\1.*/\1/')
    [ "${#pfx}" -ge 4 ] && { printf '%s' "$k"; return 0; }
  done
  return 1
}

_hints=""
for c in $_cmds; do
  # resolves to a real skill? quiet.
  case "$_known" in *" $c "*) continue;; esac
  # known built-in? quiet.
  case "$_BUILTINS" in *" $c "*) continue;; esac
  # plugin-namespaced (foo:bar) — can't validate locally; quiet.
  case "$c" in *:*) continue;; esac
  # unknown — only speak if there's a plausible correction.
  if sugg=$(_near "$c"); then
    _hints="$_hints /${c}->/${sugg}?"
  fi
done

[ -z "$_hints" ] && exit 0
hook_emit "UserPromptSubmit" "[skill-check] unknown slash-command(s); did you mean:${_hints}"
