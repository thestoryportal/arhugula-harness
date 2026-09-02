#!/usr/bin/env bash
# PreToolUse(Bash) guard for the two grep shapes the rtk rewrite mangles (U-SR-09 b4,
# plan §8 R2; [B] F5: 29 wasted calls ≈ 1.2M IET on one arc).
#
# The user-level `rtk hook claude` (Rust Token Killer 0.40.0) rewrites `grep …`/`rg …` to
# `rtk grep …`, which runs ripgrep with grep's arguments. Two argument shapes fail
# DETERMINISTICALLY under that translation, witnessed at U-SR-09 on the installed binary:
#   (1) `--glob` / `-g`  -- an rg-only flag; rtk hands the call to BSD grep, which exits 2
#                           with "unrecognized option";
#   (2) an unescaped `(` or `)` in a BRE pattern (no -E/-F/-P) -- a literal paren to grep, a
#                           group to rg: "regex parse error … unclosed group", exit 2.
#   [B]'s third shape, `\|` alternation, round-trips on 0.40.0 (rtk translates it); it fails
#   only when combined with a paren, which shape (2) already covers -- so it is NOT guarded
#   (a deny on a working command would be a false positive that costs the call it saves).
#
# Why a DENY and not a fix or a pass-through, stated once: the rewrite lives in rtk (not
# workspace code); rtk's `[hooks] exclude_commands` is a command-PREFIX match (`"grep -F"`
# excludes, `"--glob"` cannot -- witnessed at U-SR-09), so mid-command shapes have no config
# escape; and Claude Code runs every PreToolUse hook in parallel on the ORIGINAL input with
# no documented precedence between two hooks' `updatedInput` (hooks doc, "Hook handler
# fields"), so a project hook cannot out-rewrite rtk. A deny outranks every allow
# (`deny > defer > ask > allow`) and is the one repo-owned mechanism that fires BEFORE the
# mangled call is spent: one call (the deny + re-issue) instead of two (the failure + the
# re-query), and a loud, exact redirect instead of a silent wrong answer. The corrected
# command is `rtk proxy <original>` -- rtk's own raw-execution verb, which its hook leaves
# alone (witnessed: `rtk hook claude` emits 0 bytes for every `rtk proxy` shape).
#
# Three preconditions, each a fact about the venue and not a guess:
#   - rtk's rewrite hook is REGISTERED in the Claude user settings
#     (`${CLAUDE_CONFIG_DIR:-$HOME/.claude}/settings.json`, a PreToolUse command carrying
#     `rtk hook claude`). That registration is the mechanism this guard compensates for;
#     without it nothing rewrites and the guard is silent -- which is also why it is NOT
#     mirrored into `.codex/hooks.json`: Codex never runs rtk's hook, so a mirrored deny
#     would refuse commands Codex runs unmangled (`CLAUDE_ONLY_HOOKS` in the Codex adapter).
#   - `rtk` is on PATH (CI and other machines: no rtk, no rewrite, silent exit 0).
#   - rtk's own dry-run (`rtk hook check <cmd>`) says THIS command is rewritten. Its print
#     form varies (the rewritten command; "No rewrite for: <cmd>"; or the command echoed
#     back verbatim -- all three seen on 0.40.0); the judgement keys on the one token that
#     appears only in a real rewrite: `rtk grep`. An oracle that fails or exceeds its bound
#     is read as "no rewrite" -- the call proceeds exactly as it did before this guard
#     existed (the guard can only ever REMOVE a wasted call, never add a stall).
# The judgement itself -- separators, quoting, attached flag values, the pattern operand,
# the re-issue -- is `tools/rtk_shape_guard.py`, run with the hook shell's /usr/bin/python3
# (the sibling hooks' interpreter; 3.9-compatible) and unit-tested on its own. A plain
# command emits ZERO bytes (WR-16 emit policy; test_pretooluse_bash_emit_policy.sh pins it).
# The two 5 s bounds are the sibling hooks' bounded-subprocess budget (postedit-lint.sh's
# YAML step); the dry-run and the judgement each return in milliseconds.
#
# EXIT PLAN ([LAW:no-mode-explosion]): this guard exists for a defect in an external tool at
# a known version. test_rtk_shape_guard.sh section 4 (runs only where rtk is installed)
# asserts each shape STILL fails under `rtk grep` and works under `rtk proxy`; when a newer
# rtk translates them correctly that section reds with "rtk fixed this -- delete the guard",
# and the deletion is this file, tools/rtk_shape_guard.py + its tests, the manifest row,
# the adapter's CLAUDE_ONLY_HOOKS entry and the settings.json entry.

set -uo pipefail

_LIB="$(dirname "${BASH_SOURCE[0]}")/lib.sh"
[ -f "$_LIB" ] || exit 0
# shellcheck source=lib.sh
. "$_LIB"
hook_review_isolated && exit 0

PAYLOAD=$(hook_read_stdin)
CMD=$(hook_json "$PAYLOAD" '.tool_input.command')
[ -z "$CMD" ] && exit 0

# Cheap pre-check so an unrelated Bash call never pays for a subprocess.
case "$CMD" in *grep*|*rg*) ;; *) exit 0 ;; esac
command -v rtk >/dev/null 2>&1 || exit 0

# rtk's rewrite hook must be registered for THIS venue (see the header).
SETTINGS="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/settings.json"
[ -f "$SETTINGS" ] || exit 0
jq -e '[.hooks.PreToolUse[]?.hooks[]?.command // empty] | any(contains("rtk hook claude"))' \
  "$SETTINGS" >/dev/null 2>&1 || exit 0

# The oracle: rtk's own dry-run of its rewrite. Bounded; any failure = no rewrite = no guard.
REWRITE=$(hook_bounded 5 rtk hook check "$CMD" 2>/dev/null) || exit 0
case "$REWRITE" in *"rtk grep"*) ;; *) exit 0 ;; esac

JUDGE="$(dirname "${BASH_SOURCE[0]}")/../rtk_shape_guard.py"
[ -f "$JUDGE" ] || exit 0
REASON=$(hook_bounded 5 /usr/bin/python3 "$JUDGE" "$CMD" "$REWRITE" 2>/dev/null) || exit 0
[ -z "$REASON" ] && exit 0

jq -nc --arg r "$REASON" \
  '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":$r}}'
exit 0
