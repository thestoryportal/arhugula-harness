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
# Oracle, not re-implementation: `rtk hook check <cmd>` (rtk's dry-run) says whether THIS
# command gets rewritten to `rtk grep …`; only then is the shape judged. Its print form
# varies (the rewritten command; "No rewrite for: <cmd>"; or the command echoed back
# verbatim -- all three seen on 0.40.0), so the guard keys on ONE token that appears only
# in a real rewrite: `rtk grep `. rtk absent (CI, another machine) -> nothing rewrites ->
# nothing to guard -> silent exit 0; an oracle that fails or exceeds its bound is treated
# the same way -- the call proceeds exactly as it did before this guard existed (the guard
# can only ever REMOVE a wasted call, never add a stall). A plain command emits ZERO bytes
# (WR-16 emit policy; test_pretooluse_bash_emit_policy.sh pins it). The oracle's 5 s bound
# is the sibling hooks' bounded-subprocess budget (postedit-lint.sh's ruff step); the
# dry-run itself returns in milliseconds.
#
# EXIT PLAN ([LAW:no-mode-explosion]): this guard exists for a defect in an external tool at
# a known version. test_rtk_shape_guard.sh section 4 (runs only where rtk is installed)
# asserts each shape STILL fails under `rtk grep` and works under `rtk proxy`; when a newer
# rtk translates them correctly that section reds with "rtk fixed this -- delete the guard",
# and the deletion is this file, its test, its manifest row and its settings.json entry.

set -uo pipefail

_LIB="$(dirname "${BASH_SOURCE[0]}")/lib.sh"
[ -f "$_LIB" ] || exit 0
# shellcheck source=lib.sh
. "$_LIB"
hook_review_isolated && exit 0

PAYLOAD=$(hook_read_stdin)
CMD=$(hook_json "$PAYLOAD" '.tool_input.command')
[ -z "$CMD" ] && exit 0

# Cheap pre-check so an unrelated Bash call never pays for the oracle subprocess.
case "$CMD" in *grep*|*rg*) ;; *) exit 0 ;; esac
command -v rtk >/dev/null 2>&1 || exit 0

# The oracle: rtk's own dry-run of its rewrite. Bounded; any failure = no rewrite = no guard.
REWRITE=$(hook_bounded 5 rtk hook check "$CMD" 2>/dev/null) || exit 0
case "$REWRITE" in *"rtk grep "*) ;; *) exit 0 ;; esac

# The `rtk grep …` segment the shapes are judged on: from the (last) `rtk grep ` to the next
# space-delimited shell separator. A `\|` inside a quoted pattern has no spaces around it,
# so it never cuts the segment.
SEG=$(printf '%s' "$REWRITE" | sed -E 's/^.*rtk grep /rtk grep /; s/ (\||&&|\|\||;) .*$//')

# -E / -F / -P (or their long forms) make a paren mean the same thing to grep and rg.
if printf '%s' "$SEG" | grep -qE -- '(^|[[:space:]])(-[[:alnum:]]*[EFP][[:alnum:]]*|--extended-regexp|--fixed-strings|--perl-regexp)([[:space:]]|$)'; then
  REGEX_SAFE=1
else
  REGEX_SAFE=0
fi

SHAPES=""
if printf '%s' "$SEG" | grep -qE -- '(^|[[:space:]])(-g|--glob)([[:space:]=]|$)'; then
  SHAPES="${SHAPES}an rg-only --glob/-g flag (rtk lands it on BSD grep: 'unrecognized option', exit 2); "
fi
if [ "$REGEX_SAFE" -eq 0 ] && printf '%s' "$SEG" | grep -qE -- '(^|[^\\])[()]'; then
  SHAPES="${SHAPES}an unescaped paren in a BRE pattern (a literal to grep, a group to rg: 'regex parse error', exit 2); "
fi
[ -z "$SHAPES" ] && exit 0

# The re-issue, built from the ORIGINAL command (the dry-run collapses `rg` into `grep`, and
# `rtk proxy grep -g` would fail exactly like today): every command-position grep/rg gets
# rtk's raw-execution prefix. Command position = start of the string, after `;`/`&`/`|`, or
# inside `$(`. A quoted `; grep` would be prefixed too -- the reason text is a suggestion,
# the deny is the mechanism.
FIX=$(printf '%s' "$CMD" | sed -E 's/(^[[:space:]]*|[;&|][[:space:]]*|\$\([[:space:]]*)(grep|rg)([[:space:]])/\1rtk proxy \2\3/g')

jq -nc --arg r "[rtk-shape-guard] the rtk PreToolUse rewrite turns this into \`${SEG}\`, which carries ${SHAPES%; }. Re-issue verbatim as: ${FIX}" \
  '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":$r}}'
exit 0
