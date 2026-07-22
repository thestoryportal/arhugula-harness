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

# Read the payload UP FRONT (before the loop-mode inert gate) so the §0 worktree-live-
# session guard below can fire in BOTH interactive and loop mode. stdin is consumed once.
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

# ─── 0) ALWAYS-ON: never remove a worktree that has a LIVE Claude session ───────
# Hoisted ABOVE the loop-mode inert gate — the ONLY auto-decision this guard makes in an
# interactive session, and it is a DENY (never an approve), so the "no interactive auto-
# APPROVAL" contract holds. Removing a worktree out from under a live session orphans it:
# the session's Edit/Write tools stay pinned to the deleted worktree root and reject every
# shared-checkout path (operator hit this 2026-06-04). Liveness = a Claude transcript for
# that worktree touched within the window (lib.sh worktree_has_live_session). Fail-open:
# unknown target / no recent transcript → no-op → falls through to the normal flow below.
# Escape hatch: HARNESS_ALLOW_LIVE_WORKTREE_REMOVE=1.
if [ "$TOOL" = "Bash" ] && [ -n "$CMD" ] && [ "${HARNESS_ALLOW_LIVE_WORKTREE_REMOVE:-}" != "1" ] \
   && printf '%s' "$CMD" | grep -Eq 'git[[:space:]]+worktree[[:space:]]+remove'; then
  # Last non-flag token after `worktree remove` = the target path.
  _WT=$(printf '%s' "$CMD" | sed -E 's/.*worktree[[:space:]]+remove//' | tr ' \t' '\n' | grep -vE '^(-.*)?$' | tail -n1)
  if [ -n "$_WT" ] && worktree_has_live_session "$_WT"; then
    loop_log DENY "Bash: live-session worktree removal blocked :: $CMD"
    if [ "$EVENT" = "PermissionRequest" ]; then
      jq -nc '{"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"deny"}}}'
    else
      jq -nc '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"[permission-guard] HARD-STOP: target worktree has a live Claude session — removing it would orphan that session. Close the session first, or override with HARNESS_ALLOW_LIVE_WORKTREE_REMOVE=1."}}'
    fi
    exit 0
  fi
fi

# 1) INERT unless loop mode on. This is the whole safety story: a normal interactive
#    session never sees an auto-decision (other than the §0 hard-DENY above).
loop_mode_active || exit 0

# Canonicalize a path (relative or absolute) to its physical, symlink-resolved absolute
# form. Factored out of _safe_path so any OTHER path-IDENTITY check (e.g. the
# loop_status.md ledger exclusion below) uses the SAME resolution and can't be bypassed by
# an alias (`.harness//loop_status.md`, `.harness/./loop_status.md`, a symlink) that would
# fool a naive literal string/case match (codex [P1] round 5 on the resolve.sh arc — a
# `_safe_path`-style raw-string comparison for the ledger exclusion had exactly this gap).
# Degrades gracefully to the un-resolved concatenation if a component doesn't exist yet
# (e.g. `.harness/` not yet created) — still consistent as long as both sides of a
# comparison call this same function.
_resolve_abs() {
  local p="$1"
  local abs; case "$p" in /*) abs="$p" ;; *) abs="$PROJECT_DIR/$p" ;; esac
  local dir base rp tgt hops=0
  dir=$(dirname "$abs"); base=$(basename "$abs")
  if rp=$(cd "$dir" 2>/dev/null && pwd -P); then abs="$rp/$base"; fi
  # Follow the symlink CHAIN physically (bounded).
  while [ -L "$abs" ] && [ "$hops" -lt 16 ]; do
    tgt=$(readlink "$abs" 2>/dev/null) || break
    case "$tgt" in /*) abs="$tgt" ;; *) abs="$(dirname "$abs")/$tgt" ;; esac
    if rp=$(cd "$(dirname "$abs")" 2>/dev/null && pwd -P); then abs="$rp/$(basename "$abs")"; fi
    hops=$((hops + 1))
  done
  printf '%s' "$abs"
}

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
  # Resolve symlinks PHYSICALLY before the containment check: an in-worktree symlink to an
  # outside/secret file would otherwise pass the string-prefix test while the OS follows it
  # out.
  local abs; abs=$(_resolve_abs "$p")
  # Re-check secret patterns on the resolved target too.
  case "$abs" in
    *.env|*.env.*|*/.env|*credentials*|*.pem|*id_rsa*|*id_ed25519*|*keyring*|*secret*|*.key) return 1 ;;
  esac
  local root; root=$(cd "$PROJECT_DIR" 2>/dev/null && pwd -P) || root="$PROJECT_DIR"
  case "$abs" in
    *..*) return 1 ;;                 # traversal
    */.git/*|*/.git) return 1 ;;      # git internals
    "$root"|"$root"/*) return 0 ;;
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
  printf '%s' "$cmd" | grep -Eq '(~|\.\.)' && return 1
  # .git internals (config holds token-bearing remote URLs; hooks/ run on every commit).
  # `\.git/` won't match `.github/` (that's .git + 'hub').
  printf '%s' "$cmd" | grep -Eq '\.git/|(^|[[:space:]])\.git([[:space:]]|$)' && return 1
  # ANY uppercase env-var expansion ($HOME, ${HOME}, $ANTHROPIC_API_KEY, $TMPDIR, ...),
  # braced or not — it can resolve to an out-of-worktree path or print a credential, and
  # the hook cannot evaluate it. Conservative: such commands fall through to ask.
  printf '%s' "$cmd" | grep -Eq '\$\{?[A-Z]' && return 1
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

# Loop-control wrappers short-circuit to ALLOW *before* the free-text deny scan. defer.sh
# / halt.sh only append a ledger row / touch the halt marker — they perform no dangerous
# action regardless of args, and their REASON text naturally names operator actions ("gh
# secret set …", ".env", "credentials") that the deny-list scans for as substrings. Without
# this exemption a safe deferral whose reason names the gate would be DENIED, no DEFERRED-HIL
# row would be written, and the headless loop would retry the same gated item to the cap.
#
# Deliberately NOT here: any mechanism that CLEARS a gate (asserts a human already
# answered it) rather than just logging one for future attention. defer.sh/halt.sh are
# safe to blanket-allow because logging can never cause harm regardless of who calls it;
# a gate-clearing action is fundamentally different — it must go through the normal
# deny-list-then-ask flow, reachable only from an attended session. This is why there is
# no `resolve.sh` wrapper: an unattended headless child could never legitimately answer a
# HIL gate on its own, so a mechanism that let it try (even indirectly, by clearing a
# ledger row) would be a bypass, not a convenience. Resolution is recorded directly via
# loop_lib.sh's loop_resolve from an attended session — no wrapper needed or wanted.
# Strictly bounded to a SINGLE CLEAN invocation: wrapper prefix + NO control operators (so it
# can't chain a real dangerous command) + NO $VAR expansion (so it can't expand a secret VALUE
# into the ledger). $(...) and newlines are control-operator-rejected here too.
if [ "$TOOL" = "Bash" ] && [ -n "$CMD" ] \
   && printf '%s' "$CMD" | grep -Eq '^[[:space:]]*(bash[[:space:]]+)?tools/04-loop/(defer|halt)\.sh([[:space:]]|$)' \
   && ! printf '%s' "$CMD" | grep -q '[;&|<>`]' && [ "$CMD" = "${CMD%%\$(*}" ] && [ "$CMD" = "${CMD//$'\n'/}" ] \
   && ! printf '%s' "$CMD" | grep -Eq '\$\{?[A-Za-z_]'; then
  emit_allow
fi

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
  Grep)
    # Auto-allow only a NARROW, checked search root (a specific in-worktree file/subdir).
    # An empty path or the repo root = a broad recursive read that could surface a
    # descendant secret file (content-mode grep returns matching lines) → ask.
    case "$GPATH" in
      ""|"."|"./"|"$PROJECT_DIR"|"$PROJECT_DIR"/) exit 0 ;;
    esac
    _safe_path "$GPATH" && emit_allow ;;
  Glob)
    # Glob's `pattern` IS a path-glob — reject an absolute or traversing pattern even when
    # `path` is empty (`/etc/*`, `../*.pem` would escape the worktree).
    _safe_path "$GPATH" || exit 0
    case "$(hook_json "$PAYLOAD" '.tool_input.pattern')" in
      /*|*..*) : ;;            # absolute / traversal glob → ask
      *) emit_allow ;;
    esac
    ;;
  Edit|Write|MultiEdit|NotebookEdit)
    # Edits are git-reversible ONLY inside the worktree. Auto-allow EXCEPT design-substrate
    # (X-AL-3 back-flow) — those, plus secret/outside/.git/traversal paths (via _safe_path),
    # fall through to ask.
    #
    # loop_status.md is ALSO excluded (codex [P1] round 4, U-HK-11/14/15): it is a
    # human-reviewed audit trail, not a file any agent — attended or not — should be able
    # to self-edit via a plain Edit/Write tool call to assert its own gates are cleared
    # (e.g. hand-appending a RESOLVED-HIL row). Raw Bash-level redirection into it
    # (`echo … >> .harness/loop_status.md`) is separately already blocked: any `>` trips
    # the control-operator check in §3's Bash-prefix block below, falling through to ask.
    # The ONLY writers are loop_log's own appends: from defer.sh/halt.sh (always allowed,
    # §2 above) or from loop_resolve called directly in an attended session (no wrapper —
    # see the §2 comment on why resolution has none).
    #
    # Compared by CANONICAL absolute path (_resolve_abs), not a literal string/case match
    # (codex [P1] round 5) — a raw-string check would let `.harness//loop_status.md`,
    # `.harness/./loop_status.md`, or a symlink alias slip through to the `*)` branch and
    # auto-allow, defeating this exclusion entirely.
    case "$FPATH" in
      */design-substrate/*|design-substrate/*) : ;;  # ask (absolute OR relative path)
      *)
        if [ -n "$FPATH" ] && [ "$(_resolve_abs "$FPATH")" = "$(_resolve_abs "$PROJECT_DIR/.harness/loop_status.md")" ]; then
          :  # ask — ledger is audit-only
        else
          _safe_path "$FPATH" && emit_allow
        fi
        ;;
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
     || printf '%s' "$CMD" | grep -Eq 'gh[[:space:]]+pr[[:space:]]+merge.*--admin' \
     || printf '%s' "$CMD" | grep -Eq 'git[[:space:]]+commit.*--amend' \
     || printf '%s' "$CMD" | grep -Eq 'git[[:space:]]+branch[[:space:]]+(-f|--force|-m|-M|--move|-c|-C|--copy)'; then
    :  # chained / nested / redirected / destructive submode (incl. git commit --amend) → ask
  else
    TRIM=$(printf '%s' "$CMD" | sed 's/^[[:space:]]*//')
    # (Loop-control wrappers defer.sh/halt.sh are auto-allowed earlier — at the top of the
    # deny block — so a deferral reason naming an operator action isn't tripped by the
    # free-text deny scan. See §2.)
    # Allowlist = commands that are safe REGARDLESS of their arguments (the dev/git arc
    # + pure builtins with no filesystem reach). Deliberately NOT here:
    #  - content readers / programmable filters (cat/head/tail/grep/rg/find/jq/sed/awk/
    #    sort/uniq/diff/wc) — safety depends on unvalidatable path/glob/env args;
    #  - path mutators / listers (mkdir/chmod/touch/ls) — a relative arg can run through an
    #    in-worktree symlink (`mkdir out/dir` where `out -> /tmp`) and escape the worktree.
    # For file create/read the loop uses the structured Write/Edit/Read/Grep/Glob tools,
    # which resolve symlinks via _safe_path. This removes the recurring "verb X has an
    # unsafe arg" class structurally rather than patching each verb.
    if printf '%s' "$TRIM" | grep -Eq '^(echo|printf|pwd|cd|which|command[[:space:]]+-v|bash[[:space:]]+-n|bash[[:space:]]+tools/[^[:space:]]*test_[^[:space:]]*\.sh|ruff|pytest|uv[[:space:]]+run[[:space:]]+(ruff|pytest)|uv[[:space:]]+sync|just[[:space:]]+(check|test|lint|typecheck|fmt|markers|skips|codex-review)|git[[:space:]]+(status|diff|log|show|branch|add|commit|fetch|stash[[:space:]]+(list|show)|rev-parse|symbolic-ref|ls-files|worktree[[:space:]]+list)|git[[:space:]]+checkout[[:space:]]+-b[[:space:]]+[^[:space:]]+|gh[[:space:]]+(pr[[:space:]]+(view|list|checks|diff|status|create|ready|comment|merge)|run[[:space:]]+(view|list|watch)|api|repo[[:space:]]+view))([[:space:]]|$)' \
       && _bash_args_safe "$CMD"; then
      emit_allow
    fi
  fi
fi

# ─── 4) DEFAULT: ask (no output → normal permission prompt) ────────────────────
exit 0
