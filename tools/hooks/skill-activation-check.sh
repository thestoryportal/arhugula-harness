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

# Collect known skill names from project + user skill directories. Skills can be NESTED
# (e.g. .claude/skills/council/<voice>/SKILL.md), so walk recursively for every SKILL.md
# and take its INVOKABLE name = the frontmatter `name:` (canonical), falling back to the
# parent-dir basename. An immediate-children-only scan would miss the council voices and
# silently fail to hint on a typo of them.
# Skills live at <skills>/<name>/SKILL.md or <skills>/<group>/<name>/SKILL.md, so
# `-maxdepth 3` reaches both WITHOUT descending into each skill's node_modules /
# references / evals (an unbounded recurse over the user skills tree cost ~5s/prompt —
# unacceptable on a per-prompt hook). Name extraction is pure-bash (no awk/sed/basename
# subprocess per file) so the whole scan stays well under the budget even for ~70 skills.
_skill_dirs=("$PROJECT_DIR/.claude/skills" "$HOME/.claude/skills")
_known=""
for sd in "${_skill_dirs[@]}"; do
  [ -d "$sd" ] || continue
  while IFS= read -r f; do
    nm=""
    while IFS= read -r line || [ -n "$line" ]; do
      case "$line" in
        name:*) nm="${line#name:}"; break;;
      esac
    done < "$f"
    nm="${nm#"${nm%%[![:space:]]*}"}"   # strip leading whitespace
    nm="${nm%%[[:space:]]*}"            # keep only the first token (drop trailing ws/desc)
    nm="${nm//\"/}"; nm="${nm//\'/}"; nm="${nm//$'\r'/}"
    if [ -z "$nm" ]; then nm="${f%/SKILL.md}"; nm="${nm##*/}"; fi
    [ -n "$nm" ] && _known="$_known $nm "
  done < <(find "$sd" -maxdepth 3 -type f -name SKILL.md 2>/dev/null)
done

# Extract leading-token slash-commands from the prompt. A skill invocation is a `/name`
# at a word boundary; names are kebab/colon (plugin:skill). Ignore `//`, paths like
# `a/b`, and http(s):// URLs. We only consider tokens that START a word (prev char is
# whitespace or string start) to avoid matching `foo/bar` path fragments.
_cmds=$(printf '%s' "$PROMPT" \
  | grep -oE '(^|[[:space:]])/[a-z][a-z0-9:_-]+' 2>/dev/null \
  | sed -E 's#^[[:space:]]*/##' | sort -u)
[ -z "$_cmds" ] && exit 0

# near-match: is $1 a PREFIX-ANCHORED near-miss of a known skill name? Echoes the first
# match. Prefix-anchored + a >=4-char floor on the query is the silent-when-correct
# guard: an arbitrary-substring match made short commands noisy (`/pr`->`/ship-pr`,
# `/pla`->`/implementation-planner`, `/opt`->`/optimize-claude-md` — all false hints). A
# real mistype shares a leading prefix (`/resolv`->resolve, `/counci`->council), so we
# require either a prefix relationship (q is a prefix of k, or k of q) or a >=4-char
# shared leading prefix, and never guess for a query shorter than 4 chars.
_near() {
  local q="$1" k pfx
  [ "${#q}" -ge 4 ] || return 1
  for k in $_known; do
    case "$k" in "$q"*) printf '%s' "$k"; return 0;; esac   # q is a prefix of k (truncation typo)
    case "$q" in "$k"*) printf '%s' "$k"; return 0;; esac   # k is a prefix of q (extra-suffix typo)
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
