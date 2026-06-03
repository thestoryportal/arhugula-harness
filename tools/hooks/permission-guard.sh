#!/usr/bin/env bash
# Guardrailed auto-approve (U-HK-12). PreToolUse + PermissionRequest.
#
# THE autonomy gate's blast-radius limiter. Tri-state, fail-safe:
#   1. INERT unless loop mode is on  → exit 0, no output (normal manual approval).
#   2. DENY-LIST first (even in loop mode) → paid calls / secret relocation /
#      destructive-irreversible git / recursive delete → hard "deny" + log to ledger.
#   3. ALLOWLIST → known non-destructive tools + safe Bash prefixes → "allow".
#   4. EVERYTHING ELSE → exit 0, no output → falls through to the normal permission
#      prompt ("ask"). Unknown == ask, never auto-allow.
#
# The deny-list is checked BEFORE the allowlist so a dangerous flag on an otherwise
# allowlisted verb (e.g. `git push --force`) is still blocked. Matching is done here
# in-script (case-sensitive grep -E), so the claudefa.st settings.json matcher gotcha
# (no spaces around `|`) does not apply.
#
# Output schema differs by event (confirmed against code.claude.com/docs/en/hooks):
#   PreToolUse       → {"hookSpecificOutput":{...,"permissionDecision":"allow|deny"}}
#   PermissionRequest→ {"hookSpecificOutput":{...,"decision":{"behavior":"allow|deny"}}}
#
# Trigger: PreToolUse "*" + PermissionRequest "*". Test: tools/hooks/test_permission_guard.sh.

set -uo pipefail

_LIB="$(dirname "${BASH_SOURCE[0]}")/lib.sh"
[ -f "$_LIB" ] || exit 0
# shellcheck source=lib.sh
. "$_LIB"
# shellcheck source=loop_lib.sh
. "$(dirname "${BASH_SOURCE[0]}")/loop_lib.sh"

# 1) INERT unless loop mode on. This is the whole safety story: a normal interactive
#    session never sees an auto-decision.
loop_mode_active || exit 0

PROJECT_DIR=$(hook_project_dir)
[ -n "$PROJECT_DIR" ] && cd "$PROJECT_DIR" 2>/dev/null

PAYLOAD=$(hook_read_stdin)
EVENT=$(hook_json "$PAYLOAD" '.hook_event_name'); EVENT=${EVENT:-PreToolUse}
TOOL=$(hook_json "$PAYLOAD" '.tool_name')
CMD=$(hook_json "$PAYLOAD" '.tool_input.command')
FPATH=$(hook_json "$PAYLOAD" '.tool_input.file_path')
GPATH=$(hook_json "$PAYLOAD" '.tool_input.path')   # Grep/Glob search root
NPATH=$(hook_json "$PAYLOAD" '.tool_input.notebook_path')  # Notebook tools
[ -z "$FPATH" ] && FPATH="$NPATH"   # notebook tools carry the path here, not file_path

# A path is safe to auto-allow iff it is NOT a secret/credential file, is INSIDE the
# worktree (not .git/, no `..` traversal). Empty = no explicit path (defaults to cwd =
# worktree) = safe. Used for both read tools (Read/Grep/Glob) and edit tools, so reads of
# .env / SSH keys / out-of-worktree paths get the same boundary as writes. Returns 0 safe.
_safe_path() {
  local p="$1"
  [ -z "$p" ] && return 0
  case "$p" in
    *.env|*.env.*|*/.env|*credentials*|*.pem|*id_rsa*|*id_ed25519*|*keyring*|*secret*|*.key) return 1 ;;
  esac
  local abs; case "$p" in /*) abs="$p" ;; *) abs="$PROJECT_DIR/$p" ;; esac
  case "$abs" in
    *..*) return 1 ;;                 # traversal
    */.git/*|*/.git) return 1 ;;      # git internals
    "$PROJECT_DIR"|"$PROJECT_DIR"/*) return 0 ;;
    *) return 1 ;;                    # outside worktree
  esac
}

# A Bash command is arg-safe to auto-allow iff it does not reference a secret/credential,
# home/SSH, traversal, or an absolute path OUTSIDE the worktree. The allowlist verbs
# (cat/grep/touch/...) take free-form path args that _safe_path never sees, so without this
# `cat .env` / `grep TOKEN ~/.ssh/id_rsa` / `touch ~/.ssh/authorized_keys` would auto-allow.
# Returns 0 safe.
_bash_args_safe() {
  local cmd="$1" stripped tok
  printf '%s' "$cmd" | grep -Eq '(\.env|credentials|\.pem|id_rsa|id_ed25519|keyring|secret|\.key|\.ssh|authorized_keys)' && return 1
  printf '%s' "$cmd" | grep -Eq '(~|\$HOME|\.\.)' && return 1
  # Secret env-var expansions (e.g. `echo $ANTHROPIC_API_KEY` would print creds).
  printf '%s' "$cmd" | grep -Eq '\$\{?[A-Za-z_]*(KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|APIKEY|_API_)' && return 1
  # Absolute paths outside the worktree. Strip quotes first so `cat '/etc/passwd'`
  # (token starts with a quote, not /) is still caught.
  stripped=$(printf '%s' "$cmd" | tr -d "\"'")
  set -f
  for tok in $stripped; do
    case "$tok" in
      /*) case "$tok" in "$PROJECT_DIR"|"$PROJECT_DIR"/*) ;; *) set +f; return 1 ;; esac ;;
    esac
  done
  set +f
  return 0
}

# Emit an allow/deny decision in the schema for the firing event, then exit.
emit_allow() {
  if [ "$EVENT" = "PermissionRequest" ]; then
    jq -nc '{"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"allow"}}}'
  else
    jq -nc '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","permissionDecisionReason":"[permission-guard] safe in loop mode"}}'
  fi
  exit 0
}
emit_deny() { # $1 = reason
  loop_log DENY "${TOOL:-?}: $1 :: ${CMD:-$FPATH}"
  if [ "$EVENT" = "PermissionRequest" ]; then
    jq -nc --arg r "$1" '{"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"deny"}}}'
  else
    jq -nc --arg r "$1" '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":("[permission-guard] HARD-STOP: "+$r)}}'
  fi
  exit 0
}

# ─── 2) DENY-LIST (hard-stop, enforced even in loop mode) ──────────────────────

# Paid / inference MCP tools: never auto-fire a metered call.
case "$TOOL" in
  *route_llm_call*|*llm_dispatch*) emit_deny "paid LLM inference call — surface, do not auto-fire" ;;
esac

# Bash command deny patterns (case-sensitive). Conservative: a match hard-stops.
if [ "$TOOL" = "Bash" ] && [ -n "$CMD" ]; then
  # Recursive/forced delete.
  printf '%s' "$CMD" | grep -Eq '(^|[^[:alnum:]_])rm[[:space:]]+(-[[:alnum:]]*[rf][[:alnum:]]*[rf]|-[rf][[:space:]]+-[rf]|-[[:alnum:]]*r)' \
    && emit_deny "recursive/forced rm"
  # Force-push / history rewrite / remote branch delete.
  printf '%s' "$CMD" | grep -Eq 'git[[:space:]]+push.*(--force|--force-with-lease|[[:space:]]-f([[:space:]]|$))' \
    && emit_deny "force-push"
  printf '%s' "$CMD" | grep -Eq 'git[[:space:]]+(reset[[:space:]]+--hard|rebase|filter-branch|filter-repo)' \
    && emit_deny "git history rewrite"
  printf '%s' "$CMD" | grep -Eq 'git[[:space:]]+branch[[:space:]]+(-d|-D|--delete)|git[[:space:]]+push[[:space:]]+[^[:space:]]+[[:space:]]+:' \
    && emit_deny "branch deletion / remote ref delete"
  # Secret / credential relocation.
  printf '%s' "$CMD" | grep -Eq '(mv|cp|scp|rsync|install)[[:space:]].*(\.env|credentials|\.pem|id_rsa|id_ed25519|keyring|secret)' \
    && emit_deny "secret/credential relocation"
  printf '%s' "$CMD" | grep -Eq 'gh[[:space:]]+secret|security[[:space:]]+(add|delete)-generic-password' \
    && emit_deny "credential store mutation"
  # Paid external network calls to LLM providers.
  printf '%s' "$CMD" | grep -Eq '(curl|wget|http).*(api\.anthropic\.com|api\.openai\.com|generativelanguage\.googleapis)' \
    && emit_deny "paid provider network call"
  # Harness recipes that require live creds (paid).
  printf '%s' "$CMD" | grep -Eq 'just[[:space:]]+(mech-beta|mech-gamma|daemon)' \
    && emit_deny "recipe requires live creds / long-running"
fi

# ─── 3) ALLOWLIST (auto-approve known-safe) ───────────────────────────────────

# Non-destructive built-in tools.
case "$TOOL" in
  TodoWrite|Task) emit_allow ;;  # no filesystem reach (Task subagent re-enters the hook)
  Read|NotebookRead)
    # Reads are auto-allowed only for non-secret, in-worktree paths — otherwise a read of
    # .env / SSH keys / out-of-worktree files would leak past the approval boundary.
    _safe_path "$FPATH" && emit_allow ;;
  Grep|Glob)
    # Same boundary on the search root (content-mode grep can surface secret contents).
    _safe_path "$GPATH" && emit_allow ;;
  Edit|Write|MultiEdit|NotebookEdit)
    # Edits are git-reversible ONLY inside the worktree. Auto-allow EXCEPT design-substrate
    # (X-AL-3 back-flow) — those, plus secret/outside/.git/traversal paths (via _safe_path),
    # fall through to ask.
    case "$FPATH" in
      */design-substrate/*) : ;;  # ask
      *) _safe_path "$FPATH" && emit_allow ;;
    esac
    ;;
esac

# Safe Bash prefixes (read-only + the normal git/dev arc; force/destructive already
# denied above). Anchored at the START of the (trimmed) command.
#
# CRITICAL: auto-allow ONLY a single clean invocation. A prefix match alone is unsafe —
# a safe prefix can front a dangerous follow-on via shell chaining/nesting/redirection
# (`git status && python scripts/migrate.py --wipe`, `uv run python wipe.py`,
# `cat x | sh`). So if the command contains any control operator (; & | < > ` $( ) or a
# newline), it is NOT eligible for auto-allow — it falls through to ask. Conservative on
# purpose: a safe-but-chained command costs one approval prompt; the alternative is a
# silent bypass of the whole deny path.
if [ "$TOOL" = "Bash" ] && [ -n "$CMD" ]; then
  # Reject (→ ask) if the command (a) chains/nests/redirects, OR (b) uses a destructive
  # SUBMODE of an otherwise-allowlisted verb that the deny-list doesn't cover —
  # `find ... -delete/-exec`, `gh api -X DELETE/POST/...` (mutating). Allowlisted verbs
  # are auto-allowed only in their read-only forms.
  if printf '%s' "$CMD" | grep -q '[;&|<>`]' || [[ "$CMD" == *'$('* ]] || [[ "$CMD" == *$'\n'* ]] \
     || printf '%s' "$CMD" | grep -Eq 'find[[:space:]].*-(delete|exec|execdir|ok|okdir|fprint|fprintf|fls)\b' \
     || printf '%s' "$CMD" | grep -Eq 'gh[[:space:]]+api[[:space:]].*(-X|--method|--field|--raw-field|--input|-f[[:space:]]|-F[[:space:]])' \
     || printf '%s' "$CMD" | grep -Eq 'git[[:space:]]+commit.*--amend'; then
    :  # chained / nested / redirected / destructive submode (incl. git commit --amend) → ask
  else
    TRIM=$(printf '%s' "$CMD" | sed 's/^[[:space:]]*//')
    if printf '%s' "$TRIM" | grep -Eq '^(ls|cat|head|tail|wc|echo|printf|pwd|cd|which|command[[:space:]]+-v|grep|rg|find|sort|uniq|diff|jq|mkdir|chmod[[:space:]]+\+x|touch|bash[[:space:]]+-n|bash[[:space:]]+tools/[^[:space:]]*test_[^[:space:]]*\.sh|ruff|pytest|uv[[:space:]]+run[[:space:]]+(ruff|pytest)|uv[[:space:]]+sync|just[[:space:]]+(check|test|lint|typecheck|fmt|markers|skips|codex-review)|git[[:space:]]+(status|diff|log|show|branch|add|commit|fetch|stash[[:space:]]+(list|show)|rev-parse|symbolic-ref|ls-files|worktree[[:space:]]+list)|git[[:space:]]+checkout[[:space:]]+-b[[:space:]]+[^[:space:]]+|gh[[:space:]]+(pr[[:space:]]+(view|list|checks|diff|status|create|ready|comment|merge)|run[[:space:]]+(view|list|watch)|api|repo[[:space:]]+view))([[:space:]]|$)' \
       && _bash_args_safe "$CMD"; then
      emit_allow
    fi
  fi
fi

# ─── 4) DEFAULT: ask (no output → normal permission prompt) ────────────────────
exit 0
