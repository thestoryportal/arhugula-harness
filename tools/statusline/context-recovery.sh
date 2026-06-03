#!/usr/bin/env bash
# Context-recovery statusLine (U-HK-27 / R-3). Claude Code runs the configured statusLine
# command every turn with session JSON on stdin — the ONLY place context-window usage is
# exposed to a script (`context_window.used_percentage`, per code.claude.com/docs/statusline
# + the claudefa.st context-recovery pattern). We use that signal to PROACTIVELY checkpoint
# as context fills (before compaction loses the in-flight thread), and PRESERVE the
# operator's existing themed statusline by chaining their configured command for display
# (a project statusLine overrides the user one, so we invoke the user's command ourselves).
#
# Discipline: NEVER blocks the prompt; fast; the save touches local git only (no network
# on the hot path); the rare save fires at most once per (session, threshold). Always
# prints SOMETHING (the operator's statusline, or a minimal fallback) and exits 0.

set -uo pipefail
input=$(cat 2>/dev/null || true)
_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
_LIB="$_DIR/../hooks/lib.sh"
[ -f "$_LIB" ] && . "$_LIB"

pct=""
# ── 1. Proactive checkpoint save at context thresholds (deduped, fast) ─────────
if [ -n "$input" ] && command -v jq >/dev/null 2>&1; then
  pct=$(printf '%s' "$input" | jq -r '.context_window.used_percentage // empty' 2>/dev/null | cut -d. -f1)
  sid=$(printf '%s' "$input" | jq -r '.session_id // .session.id // "s"' 2>/dev/null | tr -dc 'A-Za-z0-9_.-' | cut -c1-40)
  if printf '%s' "${pct:-}" | grep -qE '^[0-9]+$' && command -v hook_write_checkpoint >/dev/null 2>&1; then
    T=""
    if   [ "$pct" -ge 85 ]; then T=85
    elif [ "$pct" -ge 75 ]; then T=75
    elif [ "$pct" -ge 60 ]; then T=60
    fi
    if [ -n "$T" ]; then
      proj=$(hook_project_dir 2>/dev/null)
      if [ -n "$proj" ]; then
        # Per-(session,threshold) marker → save once each. Marker presence (atomic touch)
        # is race-tolerant: a duplicate save under a race is harmless (an extra snapshot).
        mark="$proj/.harness/.checkpoints/.ctxmarks/${sid:-s}-${T}"
        if [ ! -e "$mark" ]; then
          mkdir -p "$(dirname "$mark")" 2>/dev/null && : > "$mark" 2>/dev/null
          hook_write_checkpoint "Context-threshold ${T}% proactive save (session ${sid:-?})" skip_gh
        fi
      fi
    fi
  fi
fi

# ── 2. Display: chain the operator's CONFIGURED statusline (preserve their UX) ──
# Read the user-level configured command (a project statusLine overrides it). Guard
# against pointing back at THIS script (would recurse). Fall back to a minimal context
# indicator when no user statusline exists (e.g. a fresh clone / different machine).
user_cmd=""
if command -v jq >/dev/null 2>&1 && [ -f "$HOME/.claude/settings.json" ]; then
  user_cmd=$(jq -r '.statusLine.command // empty' "$HOME/.claude/settings.json" 2>/dev/null)
fi
case "$user_cmd" in
  ""|*context-recovery*)
    printf 'ctx %s%%' "${pct:-?}" ;;
  *)
    out=$(printf '%s' "$input" | bash -c "$user_cmd" 2>/dev/null)
    if [ -n "$out" ]; then printf '%s' "$out"; else printf 'ctx %s%%' "${pct:-?}"; fi ;;
esac
exit 0
