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
hook_review_isolated && exit 0

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

# ─── 0) ALWAYS-ON: direct removal cannot close the check/remove race ───────────
# Hoisted ABOVE the loop-mode inert gate — the ONLY auto-decision this guard makes in an
# interactive session, and it is a DENY (never an approve), so the "no interactive auto-
# APPROVAL" contract holds. Removing a worktree out from under a live session orphans it:
# the session's Edit/Write tools stay pinned to the deleted worktree root and reject every
# shared-checkout path (operator hit this 2026-06-04). Every parsed direct removal is
# denied because even a negative liveness check can race a new SessionStart; the shared
# liveness helper only makes the denial reason more specific.
# Escape hatch: HARNESS_ALLOW_LIVE_WORKTREE_REMOVE=1.
if [ "$TOOL" = "Bash" ] && [ -n "$CMD" ] && [ "${HARNESS_ALLOW_LIVE_WORKTREE_REMOVE:-}" != "1" ] \
   && printf '%s' "$CMD" | grep -Eq 'git[^;&|]*[[:space:]]worktree[[:space:]]+remove'; then
  # Last non-flag token after `worktree remove` = the target path.
  _WT=$(printf '%s' "$CMD" | sed -E 's/.*worktree[[:space:]]+remove//' | tr ' \t' '\n' | grep -vE '^(-.*)?$' | tail -n1)
  if [ -n "$_WT" ]; then
    _REMOVE_REASON="direct git worktree removal is race-prone; use tools/hooks/safe-worktree-remove.sh so SessionStart lease registration and removal share one mutex"
    worktree_has_live_session "$_WT" \
      && _REMOVE_REASON="target worktree has a live Claude/Codex session"
    loop_log DENY "Bash: worktree removal blocked :: $CMD"
    if [ "$EVENT" = "PermissionRequest" ]; then
      jq -nc '{"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"deny"}}}'
    else
      jq -nc --arg r "$_REMOVE_REASON" '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":("[permission-guard] HARD-STOP: "+$r+". Override only with HARNESS_ALLOW_LIVE_WORKTREE_REMOVE=1.")}}'
    fi
    exit 0
  fi
fi

# 1) INERT unless loop mode on. This is the whole safety story: a normal interactive
#    session never sees an auto-decision (other than the §0 hard-DENY above).
loop_mode_active || exit 0

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
  # Resolve symlinks PHYSICALLY before the containment check: an in-worktree symlink to an
  # outside/secret file would otherwise pass the string-prefix test while the OS follows it
  # out. Resolve the dir via `pwd -P`, and one level of a symlinked final component.
  local dir base rp tgt hops=0
  dir=$(dirname "$abs"); base=$(basename "$abs")
  if rp=$(cd "$dir" 2>/dev/null && pwd -P); then abs="$rp/$base"; fi
  # Follow the symlink CHAIN physically (bounded) — a link to a link to outside the repo
  # would otherwise keep `abs` under $root after only one hop.
  while [ -L "$abs" ] && [ "$hops" -lt 16 ]; do
    tgt=$(readlink "$abs" 2>/dev/null) || break
    case "$tgt" in /*) abs="$tgt" ;; *) abs="$(dirname "$abs")/$tgt" ;; esac
    if rp=$(cd "$(dirname "$abs")" 2>/dev/null && pwd -P); then abs="$rp/$(basename "$abs")"; fi
    hops=$((hops + 1))
  done
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

# Worktree paths intentionally sit outside the CURRENT linked worktree, so they cannot use
# _bash_args_safe's normal containment rule. Permit only the explicit, non-expanded path
# shapes used by this repo's isolated-arc workflow. `list` is read-only; `add` accepts an
# absolute path under the repo-local worktree roots or a throwaway /tmp root. Removal uses
# the separately allowlisted mutex-backed wrapper.
# Returns 0 safe.
_safe_worktree_command() {
  local cmd="$1" sub rest target common repo_root skip_next=0 tok
  printf '%s' "$cmd" | grep -q '[;&|<>`\\()]' && return 1
  [[ "$cmd" == *$'\n'* ]] && return 1
  printf '%s' "$cmd" | grep -Eq '(~|\.\.|\$\{?[A-Za-z_])' && return 1
  sub=$(printf '%s' "$cmd" | sed -E 's/^[[:space:]]*git[[:space:]]+worktree[[:space:]]+([^[:space:]]+).*/\1/')
  [ "$sub" = "list" ] && return 0
  case "$sub" in add) ;; *) return 1 ;; esac

  rest=$(printf '%s' "$cmd" | sed -E "s/^[[:space:]]*git[[:space:]]+worktree[[:space:]]+$sub[[:space:]]*//")
  set -f
  for tok in $rest; do
    if [ "$skip_next" -eq 1 ]; then skip_next=0; continue; fi
    case "$tok" in
      -b|-B|--reason) skip_next=1 ;;
      --detach|--checkout|--no-checkout|--lock) ;;
      -*) set +f; return 1 ;;
      *) target="$tok"; break ;;
    esac
  done
  set +f
  case "$target" in /tmp/*|/private/tmp/*) return 0 ;; /*) ;; *) return 1 ;; esac

  common=$(git -C "$PROJECT_DIR" rev-parse --git-common-dir 2>/dev/null) || return 1
  case "$common" in /*) ;; *) common="$PROJECT_DIR/$common" ;; esac
  repo_root=$(cd "$(dirname "$common")" 2>/dev/null && pwd -P) || return 1
  case "$target" in
    "$repo_root"/.codex-worktrees/*|"$repo_root"/.claude/worktrees/*) return 0 ;;
    *) return 1 ;;
  esac
}

_safe_worktree_remove_wrapper() {
  local cmd="$1" target common repo_root
  printf '%s' "$cmd" | grep -q '[;&|<>`\\()]' && return 1
  [[ "$cmd" == *$'\n'* ]] && return 1
  printf '%s' "$cmd" | grep -Eq '(~|\.\.|\$\{?[A-Za-z_])' && return 1
  set -f; set -- $cmd; set +f
  if [ "${1:-}" = "bash" ]; then shift; fi
  [ "$#" -eq 2 ] && [ "$1" = "tools/hooks/safe-worktree-remove.sh" ] || return 1
  target="$2"
  case "$target" in
    \"*\") target=${target#\"}; target=${target%\"} ;;
    \'*\') target=${target#\'}; target=${target%\'} ;;
  esac
  printf '%s' "$target" | grep -qE "['\"]" && return 1
  case "$target" in /tmp/*|/private/tmp/*) return 0 ;; /*) ;; *) return 1 ;; esac
  common=$(git -C "$PROJECT_DIR" rev-parse --git-common-dir 2>/dev/null) || return 1
  case "$common" in /*) ;; *) common="$PROJECT_DIR/$common" ;; esac
  repo_root=$(cd "$(dirname "$common")" 2>/dev/null && pwd -P) || return 1
  case "$target" in
    "$repo_root"/.codex-worktrees/*|"$repo_root"/.claude/worktrees/*) return 0 ;;
    *) return 1 ;;
  esac
}

# C-HE-07 §1: the ONLY merge verb auto-allowed in loop mode is the safe-merge wrapper,
# exact arity `bash tools/hooks/safe-merge.sh <pr-number>` (all-digits PR, no other token) —
# mirroring _safe_worktree_remove_wrapper's hardening. Reference matcher folded verbatim
# from Spec_HE_Loop_Lanes_v1.md C-HE-07 §1.
_safe_merge_wrapper() {
  local cmd="$1"
  printf '%s' "$cmd" | grep -q '[;&|<>`\\()]' && return 1
  [[ "$cmd" == *$'\n'* ]] && return 1
  printf '%s' "$cmd" | grep -Eq '(~|\.\.|\$\{?[A-Za-z_])' && return 1
  set -f; set -- $cmd; set +f
  if [ "${1:-}" = "bash" ]; then shift; fi
  [ "$#" -eq 2 ] && [ "$1" = "tools/hooks/safe-merge.sh" ] || return 1
  case "$2" in ''|*[!0-9]*) return 1 ;; esac
  return 0
}

# 0 iff the push command targets main: any refspec destination == main, or no refspec while
# main is checked out (a bare push sends the current branch). U-HE-26 (C-HE-08 §1).
_push_targets_main() {
  local cmd="$1" tok positional=() dest branch remote="" repo_opt="" want_value="" pd scan_from=0 opts_done=0
  # codex r2 P1: the parser sees the UNEXPANDED command. Brace expansion
  # (`HEAD:ma{in,ster}` executes as HEAD:main) and variable expansion (`HEAD:$b` --
  # _bash_args_safe rejects only $UPPERCASE) can synthesize a main refspec after approval,
  # and neither is rejected by the generic control-operator gate. Any expansion-capable
  # character in a push command denies outright.
  # (`#` joins the gate at codex r6 P1: word-splitting treats a shell comment's tokens as
  # arguments -- `git push # comment` IS a bare push to the checked-out branch, while the
  # parser would count two phantom positionals and skip the bare-push branch. `#` is
  # illegal in refnames, so nothing legitimate is lost.)
  # (`*`/`?`/`[` join at codex r9 P1: pathname expansion applies to EVERY word -- a glob
  # remote token like `[am]*` can expand to `a main …`, synthesizing a main refspec the
  # per-destination checks below never see. No legitimate loop push carries glob chars.)
  case "$cmd" in *'{'*|*'}'*|*'$'*|*'#'*|*'*'*|*'?'*|*'['*) return 0 ;; esac
  # codex r4 P1: word-splitting cannot preserve quoted argument boundaries -- a quoted
  # value containing whitespace (--repo 'remote bare repo') smears into phantom
  # positionals and skips the bare-push branch. Any quoted span with internal whitespace
  # denies outright (single-token quoting like 'HEAD:main' is unaffected).
  printf '%s' "$cmd" | grep -Eq "['\"][^'\"]*[[:space:]][^'\"]*['\"]" && return 0
  # codex r7 P1 (same class): a backslash-escaped whitespace (`origin\ repo` is ONE
  # argument to git) also breaks word-split boundaries -- deny outright.
  printf '%s' "$cmd" | grep -Eq '\\[[:space:]]' && return 0
  set -f; set -- $cmd; set +f
  shift 2                                   # git push
  for tok in "$@"; do
    if [ -n "$want_value" ]; then
      # codex r3 P1: --repo's value IS the selected remote -- discarding it made the
      # config checks below inspect the wrong remote's push refspecs. Dequoted before
      # storing (codex r5 P1: the shell passes 'origin' to git AS origin; querying config
      # for the literal quoted string missed the remote's main-targeting refspec).
      if [ "$want_value" = "repo" ]; then
        tok=${tok//\"/}; tok=${tok//\'/}; tok=${tok//\\/}
        repo_opt="$tok"
      elif [ "$want_value" = "rsub" ]; then
        # codex r8 P1: recursive submodule modes trigger NESTED pushes that never pass
        # through this hook (a submodule checked out on main could be pushed). Only the
        # non-recursive modes are inert.
        case "$tok" in no|check) ;; *) return 0 ;; esac
      fi
      want_value=""; continue
    fi
    # Shell dequoting: quotes AND backslashes -- 'HEAD:main' IS HEAD:main (Codex round-4 P1)
    # and HEAD:ma\in IS HEAD:main (codex r1 P1). Removing every backslash can only widen
    # the deny (a literal backslash-bearing ref can never be main).
    tok=${tok//\"/}; tok=${tok//\'/}; tok=${tok//\\/}
    if [ "$opts_done" = 1 ]; then positional+=("$tok"); continue; fi
    case "$tok" in
      --) opts_done=1; continue ;;          # codex r8 P2: end-of-options -- everything after
                                            # is positional; hard-denying `--` broke legit
                                            # topic pushes
      --all|--branches) return 0 ;;         # pushes every branch, main included (codex r1 P1;
                                            # --mirror is denied by the sibling predicate above)
      --repo) want_value=repo; continue ;;
      --repo=*) repo_opt="${tok#--repo=}"; continue ;;
      --recurse-submodules) want_value=rsub; continue ;;
      --recurse-submodules=no|--recurse-submodules=check) continue ;;
      --recurse-submodules=*) return 0 ;;   # codex r8 P1: on-demand/only spawn nested
                                            # submodule pushes outside this hook's sight
      -o|--push-option|--receive-pack|--exec)
                                            # codex r2/r3 P1: the separate-value options of
                                            # `git push` -- their value is NOT a positional;
                                            # miscounting one skipped the bare-push branch
                                            # entirely (`--recurse-submodules no origin` was
                                            # empirically confirmed to consume `no` as value).
        want_value=other; continue ;;
      -u|--set-upstream|-q|--quiet|-v|--verbose|-n|--dry-run|--porcelain|--progress|--no-progress|--thin|--no-thin|--atomic|--no-atomic|--follow-tags|--no-follow-tags|--tags|--verify|--no-verify|-4|--ipv4|-6|--ipv6|--signed|--no-signed|--signed=*|--force-with-lease|--force-with-lease=*|--no-force-with-lease|--push-option=*|--receive-pack=*|--exec=*|--no-recurse-submodules)
        continue ;;                         # recognized flag-only / =-form options: none can
                                            # redirect an otherwise-safe push onto main
      -*) return 0 ;;                       # codex r4 P1: git accepts unambiguous
                                            # long-option ABBREVIATIONS (--al == --all), so
                                            # any option not an EXACT member of the
                                            # recognized set fails closed.
    esac
    positional+=("$tok")
  done
  branch=$(git -C "$PROJECT_DIR" symbolic-ref --short -q HEAD 2>/dev/null)
  # Refspec scan always skips the remote slot: positional[0] is git's REPOSITORY argument
  # at every arity (measured r7: a positional repository beats --repo; codex r6/r9 P2: a
  # remote named `main` must not hard-deny a topic push). Since r4 every unrecognized
  # option fails closed, positional[0] is reliably the repository -- a single-positional
  # push is a BARE push to that repository and is handled by the bare-push branch below
  # (branch check + config checks against exactly that remote).
  scan_from=1
  if [ "${#positional[@]}" -gt "$scan_from" ]; then
    for tok in "${positional[@]:$scan_from}"; do
      # codex r2 P1: `+:` (and bare `:`) is the matching-refspec push -- it updates every
      # matching branch, main included, and parses to an EMPTY destination.
      case "$tok" in *:) return 0 ;; esac
      # Two-step strip: refs/heads/main -> main AND the DWIM partial form heads/main ->
      # main (codex r5 P1: git resolves `topic:heads/main` to refs/heads/main).
      dest="${tok##*:}"; dest="${dest#+}"; dest="${dest#refs/}"; dest="${dest#heads/}"
      # codex r3 P1: a colonless HEAD/@ refspec resolves to the CURRENT branch (deny on a
      # main checkout); an explicit `:HEAD`/`:@` destination resolves to the REMOTE's
      # default branch, which is plausibly main -- deny outright (over-deny is safe).
      case "$tok" in
        HEAD|@|+HEAD|+@) [ "$branch" = "main" ] && return 0 ;;
        *:*) case "$dest" in HEAD|@) return 0 ;; esac ;;
      esac
      # Exact main, a wildcard refspec that can reach it (codex r1 P1), or a glob-capable
      # token (`?`/`[` -- a matching file in the cwd would expand it; same class as the
      # brace/variable gate above).
      case "$dest" in main|*'*'*|*'?'*|*'['*) return 0 ;; esac
    done
  fi
  # The remote git will actually push to: positional[0] when refspecs are present, else the
  # bare-push precedence chain --repo > branch.<b>.pushRemote > remote.pushDefault >
  # branch.<b>.remote > origin (codex r2/r3 P1: resolving only branch.<b>.remote read the
  # wrong remote's config).
  if [ "${#positional[@]}" -ge 2 ]; then
    remote="${positional[0]}"
  else
    remote="${positional[0]:-$repo_opt}"
    [ -z "$remote" ] && remote=$(git -C "$PROJECT_DIR" config --get "branch.${branch:-HEAD}.pushRemote" 2>/dev/null)
    [ -z "$remote" ] && remote=$(git -C "$PROJECT_DIR" config --get remote.pushDefault 2>/dev/null)
    [ -z "$remote" ] && remote=$(git -C "$PROJECT_DIR" config --get "branch.${branch:-HEAD}.remote" 2>/dev/null)
  fi
  remote="${remote:-origin}"
  # codex r3 P1: remote.<r>.mirror=true behaves as if --mirror were supplied -- every ref,
  # main included, regardless of the command's own refspecs.
  # --bool normalizes yes/on/1 (codex r4 P1: git booleans are not the literal string true).
  [ "$(git -C "$PROJECT_DIR" config --bool --get "remote.${remote}.mirror" 2>/dev/null)" = "true" ] && return 0
  if [ "${#positional[@]}" -le 1 ]; then    # bare push (optional remote only)
    [ "$branch" = "main" ] && return 0
    # codex r1 P2 + r3 P2: a bare push can update main regardless of the checked-out
    # branch -- deterministic config reads (no remote-tracking refs required, unlike
    # @{push}). push.default=matching pushes every matching branch. branch.<b>.merge=main
    # pushes main ONLY under push.default=upstream (or its deprecated alias tracking):
    # under simple the push merely refuses, and under current it goes topic->topic --
    # both stay allowed (r3 P2 corrected the unconditional over-deny here).
    pd=$(git -C "$PROJECT_DIR" config --get push.default 2>/dev/null)
    [ "$pd" = "matching" ] && return 0
    if [ "$pd" = "upstream" ] || [ "$pd" = "tracking" ]; then
      case "$(git -C "$PROJECT_DIR" config --get "branch.${branch:-HEAD}.merge" 2>/dev/null)" in
        refs/heads/main|main) return 0 ;;
      esac
    fi
    while IFS= read -r tok; do
      # codex r3 P1: a configured matching refspec (`:` / `+:`, empty parsed destination)
      # updates every matching branch, main included -- same class as the command-line
      # token check above; a HEAD/@ destination resolves to the remote default branch.
      case "$tok" in *:) return 0 ;; esac
      dest="${tok##*:}"; dest="${dest#+}"; dest="${dest#refs/}"; dest="${dest#heads/}"
      case "$dest" in main|*'*'*|HEAD|@) return 0 ;; esac
    done < <(git -C "$PROJECT_DIR" config --get-all "remote.${remote}.push" 2>/dev/null)
  fi
  return 1
}

# A merge-gate lens may spawn a fresh Codex process only in lifecycle-isolated,
# ephemeral read-only mode.
# Require `--` before the prompt so option validation never scans prompt or reviewed text.
# The only out-of-worktree path is the exact /tmp report shape required by merge-gate.
_safe_codex_exec_command() {
  local cmd="$1" options prompt tok value
  local sandbox_count=0 ephemeral_count=0 cd_count=0 output_count=0
  case "$cmd" in *" -- "*) options=${cmd%% -- *}; prompt=${cmd#* -- } ;; *) return 1 ;; esac
  # The prompt may contain newlines and shell metacharacters only inside one literal
  # single-quoted argument. Reject embedded/extra quotes, which could terminate it and
  # turn prompt text into a second shell command.
  case "$prompt" in \'*\') ;; *) return 1 ;; esac
  prompt=${prompt#\'}; prompt=${prompt%\'}
  [ -n "$prompt" ] && [ "$prompt" = "${prompt//\'/}" ] || return 1

  set -f
  set -- $options
  set +f
  [ "${1:-}" = "env" ] \
    && [ "${2:-}" = "HARNESS_CODEX_REVIEW_ISOLATED=1" ] \
    && [ "${3:-}" = "codex" ] \
    && [ "${4:-}" = "exec" ] || return 1
  shift 4
  while [ "$#" -gt 0 ]; do
    tok="$1"; shift
    case "$tok" in
      --ephemeral)
        ephemeral_count=$((ephemeral_count + 1))
        ;;
      --sandbox)
        [ "$#" -gt 0 ] || return 1
        value="$1"; shift
        [ "$value" = "read-only" ] || return 1
        sandbox_count=$((sandbox_count + 1))
        ;;
      -C|--cd)
        [ "$#" -gt 0 ] || return 1
        value="$1"; shift
        [ "$value" = "$PROJECT_DIR" ] || return 1
        cd_count=$((cd_count + 1))
        ;;
      -o|--output-last-message)
        [ "$#" -gt 0 ] || return 1
        value="$1"; shift
        printf '%s' "$value" | grep -Eq '^/tmp/arhugula-pr-[0-9]+-lens[123]-[0-9a-f]{40}\.md$' || return 1
        output_count=$((output_count + 1))
        ;;
      *) return 1 ;;
    esac
  done
  [ "$sandbox_count" = "1" ] && [ "$ephemeral_count" = "1" ] \
    && [ "$cd_count" = "1" ] && [ "$output_count" = "1" ]
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

# This parser proves that the entire invocation is one read-only Codex command and that
# any shell-looking review text is contained in one literal prompt argument. Run it before
# the generic raw control-operator scan, which intentionally cannot distinguish quoted
# prompt text from active shell syntax.
if [ "$TOOL" = "Bash" ] && [ -n "$CMD" ] && _safe_codex_exec_command "$CMD"; then
  emit_allow
fi
if [ "$TOOL" = "Bash" ] && [ -n "$CMD" ] && _safe_worktree_remove_wrapper "$CMD"; then
  emit_allow
fi
# U-HE-25 (codex r2 P1): token-parse the transition target instead of pattern-matching it.
# argparse accepts --to=<v> and prefix abbreviations (--t <v>), and last-occurrence wins —
# a regex pair ("has --to open" + "lacks --to merged") is bypassable via `--to open
# --to=merged`. 0 iff the command carries EXACTLY ONE --to option, in the two-token
# literal form, with target exactly `open`; any =-form or --t… abbreviation rejects.
_transition_to_open_only() {
  local cmd="$1" tok prev="" target="" count=0
  set -f; set -- $cmd; set +f
  for tok in "$@"; do
    case "$tok" in
      --to) prev="TO"; count=$((count + 1)); continue ;;
      --to=*|--t|--t=*|--to?*) return 1 ;;   # =-form / abbreviation / mangled option
      *) if [ "$prev" = "TO" ]; then target="$tok"; fi; prev="" ;;
    esac
  done
  [ "$count" -eq 1 ] && [ "$target" = "open" ]
}

# C-HE-07 §2: wrapper allow exits BEFORE the deny block below (which denies the raw verb).
# The exact-shape HARNESS_ARC_ID=/HARNESS_LANE_ID= bareword prefix (U-HE-25 (b)) is stripped
# first: safe-merge.sh requires both ids and shell exports do not survive across Bash tool
# calls, so a Claude-session invocation must carry them inline (codex r1 P1). A non-bareword
# value (any $ / quote / space) never strips, and the verbatim matcher then rejects it.
if [ "$TOOL" = "Bash" ] && [ -n "$CMD" ]; then
  _MERGE_CMD=$(printf '%s' "$CMD" | sed -E 's/^[[:space:]]*((HARNESS_ARC_ID|HARNESS_LANE_ID)=[A-Za-z0-9._-]+[[:space:]]+)+//')
  if _safe_merge_wrapper "$_MERGE_CMD"; then
    emit_allow
  fi
fi

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
  printf '%s' "$CMD" | grep -Eq 'git[[:space:]]+push.*(--mirror|--prune([[:space:]]|$))|git[[:space:]]+worktree[[:space:]]+add.*([[:space:]]-B([[:space:]]|$))' \
    && emit_deny "ref-pruning or branch-reset mutation"
  printf '%s' "$CMD" | grep -Eq 'git[[:space:]]+(reset[[:space:]]+--hard|rebase|filter-branch|filter-repo)' \
    && emit_deny "git history rewrite"
  printf '%s' "$CMD" | grep -Eq 'git[[:space:]]+branch[[:space:]]+(-D|--delete[[:space:]]+--force)|git[[:space:]]+push.*(--delete|[[:space:]]+:)|git[[:space:]]+worktree[[:space:]]+(add|remove).*--force' \
    && emit_deny "branch deletion / remote ref delete"
  # C-HE-08 §1 (D5): no auto-approved push lands content on main. Explicit denies (audited
  # via loop_log DENY), NOT a removal from the allow regex (that would be the silent,
  # unaudited "ask" path). The spec's reference regexes (C10) consumed at most one token
  # between `push` and the refspec and therefore ALLOWED `git push -u origin feature:main`
  # (Codex round-2 P1); this parses the argument list instead: option tokens (`-*`) anywhere
  # are skipped, positionals are [remote] [refspec...], and any refspec whose destination is
  # main -- `main`, `HEAD:main`, `X:main`, `refs/heads/main` -- or a push with NO refspec
  # while main is checked out, is denied. The predicate reads the same HARNESS_ARC_ID=/
  # HARNESS_LANE_ID= prefix-stripped form the allowlist matches (U-HE-25 (b) TRIM strip
  # below): an anchored scan of the RAW command would let `HARNESS_ARC_ID=x git push origin
  # main` past this deny and into the alternation's auto-allow (U-HE-25 rev (v)
  # discriminating witness).
  _PUSH_CMD=$(printf '%s' "$CMD" | sed -E 's/^[[:space:]]*((HARNESS_ARC_ID|HARNESS_LANE_ID)=[A-Za-z0-9._-]+[[:space:]]+)+//')
  if printf '%s' "$_PUSH_CMD" | grep -Eq '^[[:space:]]*git[[:space:]]+push([[:space:]]|$)' && _push_targets_main "$_PUSH_CMD"; then
    emit_deny "push targeting main — land through a PR + tools/hooks/safe-merge.sh"
  fi
  # C-HE-07: the merge verb goes through the lease-holding wrapper ONLY (structural fence, P1).
  printf '%s' "$CMD" | grep -Eq '(^|[[:space:]])gh[[:space:]]+pr[[:space:]]+merge([[:space:]]|$)' \
    && emit_deny "raw gh pr merge — must go through tools/hooks/safe-merge.sh"
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
    case "$FPATH" in
      */design-substrate/*|design-substrate/*) : ;;  # ask (absolute OR relative path)
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
     || printf '%s' "$CMD" | grep -Eq 'gh[[:space:]]+pr[[:space:]]+merge.*--admin' \
     || printf '%s' "$CMD" | grep -Eq 'git[[:space:]]+commit.*--amend' \
     || printf '%s' "$CMD" | grep -Eq 'git[[:space:]]+fetch([[:space:]]+[^[:space:]]+)*[[:space:]]+(-u([[:space:]]|$)|--upload-pack(=|[[:space:]]|$))' \
     || printf '%s' "$CMD" | grep -Eq 'git[[:space:]]+branch[[:space:]]+(-f|--force|-m|-M|--move|-c|-C|--copy)'; then
    :  # chained / nested / redirected / destructive submode (incl. git commit --amend) → ask
  else
    TRIM=$(printf '%s' "$CMD" | sed 's/^[[:space:]]*//')
    # U-HE-25 (registered from U-HE-21 codex r6, EXACT-SHAPE): strip a leading
    # HARNESS_ARC_ID= / HARNESS_LANE_ID= bareword assignment (no $ / quotes / spaces in the
    # value) so the prefixed review-wrapper invocation matches the alternation below.
    # NEVER the generic HARNESS_[A-Z0-9_]+ class — HARNESS_FAILOVER_CHILD=1 must NOT strip
    # (it would let `just gemini-review` silently skip reservation-outcome persistence).
    # The deny scan above and _bash_args_safe below still see the FULL command.
    TRIM=$(printf '%s' "$TRIM" | sed -E 's/^((HARNESS_ARC_ID|HARNESS_LANE_ID)=[A-Za-z0-9._-]+[[:space:]]+)+//')
    # (Loop-control wrappers defer.sh/halt.sh are auto-allowed earlier — at the top of the
    # deny block — so a deferral reason naming an operator action isn't tripped by the
    # free-text deny scan. See the short-circuit in §2.)
    # Allowlist = commands that are safe REGARDLESS of their arguments (the dev/git arc
    # + pure builtins with no filesystem reach). Deliberately NOT here:
    #  - content readers / programmable filters (cat/head/tail/grep/rg/find/jq/sed/awk/
    #    sort/uniq/diff/wc) — safety depends on unvalidatable path/glob/env args;
    #  - path mutators / listers (mkdir/chmod/touch/ls) — a relative arg can run through an
    #    in-worktree symlink (`mkdir out/dir` where `out -> /tmp`) and escape the worktree.
    # For file create/read the loop uses the structured Write/Edit/Read/Grep/Glob tools,
    # which resolve symlinks via _safe_path. This removes the recurring "verb X has an
    # unsafe arg" class structurally rather than patching each verb.
    if printf '%s' "$TRIM" | grep -Eq '^git[[:space:]]+merge[[:space:]]+--no-edit[[:space:]]+(origin/)?main$'; then
      # A topic branch may absorb the verified local/fetched default branch without a
      # prompt. Keep this exact: no arbitrary ref, strategy, abort, squash, or extra flag.
      emit_allow
    elif printf '%s' "$TRIM" | grep -Eq '^git[[:space:]]+worktree[[:space:]]+(add|list)([[:space:]]|$)' \
       && _safe_worktree_command "$CMD"; then
      # Worktrees are normally siblings of the current linked worktree, so their absolute
      # paths intentionally fail _bash_args_safe's current-worktree containment test.
      # Git scopes these operations to this repository; this path helper limits destinations.
      # Removal uses the separately allowlisted mutex-backed wrapper.
      emit_allow
    elif printf '%s' "$TRIM" | grep -Eq '^(source|\.)[[:space:]]+tools/hooks/lane-init\.sh$'; then
      # U-HE-31: two-lane / roadmap-continue open a lane by SOURCING lane-init, and in loop
      # mode an unmatched command becomes ask -> headless denial, so the lane could never
      # get its id or index. Anchored EXACT shape with no argument surface at all (`$`-end):
      # the script takes no arguments, and anything chained, redirected or substituted was
      # already rejected above. A different path after `source` does not match.
      emit_allow
    elif printf '%s' "$TRIM" | grep -Eq '^uv[[:space:]]+run[[:space:]]+python[[:space:]]+tools/reservations\.py[[:space:]]+transition([[:space:]]|$)' \
       && _transition_to_open_only "$TRIM" \
       && _bash_args_safe "$CMD"; then
      # U-HE-25 (codex r1 P1): ship-pr's production pending→open flip at the final gate
      # (ship-pr/SKILL.md — `transition --arc-id <arc> --to open --lane-id <lane>`) must not
      # strand headless at ask→deny. ONLY the exact two-token `--to open` is allowed —
      # _transition_to_open_only token-parses the target (codex r2 P1: =-forms, argparse
      # prefix abbreviations, and last-occurrence-wins smuggling all reject), keeping the
      # U-HE-21 r6 rationale: terminal state changes + gc stay operator-visible.
      emit_allow
    elif printf '%s' "$TRIM" | grep -Eq '^(echo|printf|pwd|cd|which|command[[:space:]]+-v|bash[[:space:]]+-n|bash[[:space:]]+tools/[^[:space:]]*test_[^[:space:]]*\.sh|ruff|pytest|uv[[:space:]]+run[[:space:]]+(ruff|pytest)|uv[[:space:]]+sync|uv[[:space:]]+run[[:space:]]+python[[:space:]]+tools/reservations\.py[[:space:]]+(selectable|show|reserve|update|mint-lane-id)|just[[:space:]]+(check|test|lint|typecheck|fmt|markers|skips|overlay-check|codex-(preflight|checkpoint|closeout|autonomous-arc|loop-record|loop-status|loop-check|worktree-gc|check|context-check|credential-gate|review|review-uncommitted)|gemini-review|review-with-failover|merge-gate-(binding|emit|log-check|landing-delta)|lanes-(verify|phase0-check)|mutation-probe-coverage-check)|git[[:space:]]+(status|diff|log|show|branch|add|commit|fetch|push|pull[[:space:]]+--ff-only|stash[[:space:]]+(list|show)|rev-parse|symbolic-ref|ls-files|ls-remote|merge-tree)|git[[:space:]]+checkout[[:space:]]+-b[[:space:]]+[^[:space:]]+|gh[[:space:]]+(pr[[:space:]]+(view|list|checks|diff|status|create|ready|comment)|run[[:space:]]+(view|list|watch)|api|repo[[:space:]]+view))([[:space:]]|$)' \
       && _bash_args_safe "$CMD"; then
      emit_allow
    fi
  fi
fi

# ─── 4) DEFAULT: ask (no output → normal permission prompt) ────────────────────
exit 0
