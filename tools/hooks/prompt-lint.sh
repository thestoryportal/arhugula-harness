#!/usr/bin/env bash
# UserPromptSubmit prompt-lint (U-HK-22). Flags an under-specified / contentless prompt
# and suggests tightening it (name a target + a desired outcome). Advisory only — emits
# additionalContext, never blocks. Composes with prompt-context (U-HK-08) +
# skill-activation-check (U-HK-21) on the same event.
#
# DELIBERATELY CONSERVATIVE. The whole prompt (trimmed, lowercased, trailing-punct
# stripped) must EXACTLY equal one of a small set of bare deictic imperatives that
# genuinely lack a referent ("fix it", "do this", a lone "it"). Anything with more
# context, any slash-command, and every workspace idiom ("continue", "ship it", "go
# ahead", "yes") is SILENT — silent-when-well-formed is the AC, and false positives on
# the per-prompt path would train the operator to ignore the hint.
#
# Fast + non-network + always-exit-0. Trigger: UserPromptSubmit (no matcher).

set -uo pipefail

_LIB="$(dirname "${BASH_SOURCE[0]}")/lib.sh"
[ -f "$_LIB" ] || exit 0
# shellcheck source=lib.sh
. "$_LIB"

PAYLOAD=$(hook_read_stdin)
PROMPT=$(hook_json "$PAYLOAD" '.prompt')
[ -z "$PROMPT" ] && exit 0

# A slash-command prompt is structured input, not prose — never lint it.
case "$PROMPT" in /*) exit 0;; esac

# Normalize: lowercase, collapse all whitespace to single spaces, trim ends, strip
# trailing sentence punctuation. tr handles the case-fold portably.
NORM=$(printf '%s' "$PROMPT" \
  | tr '[:upper:]' '[:lower:]' \
  | tr '\n\t' '  ' \
  | sed -E 's/[[:space:]]+/ /g; s/^ //; s/ $//; s/[[:space:][:punct:]]+$//')
[ -z "$NORM" ] && exit 0

# The flag set: whole-prompt bare deictic imperatives / lone pronouns with no object.
# Membership-tested exactly (space-padded) so "fix it now" (has context) does NOT match.
_VAGUE=" it this that fix-it fix-this fix-that do-it do-this do-that change-it change-this \
change-that update-it update-this update-that make-it-better make-it-work improve-it \
improve-this redo-it redo-this handle-it sort-it "

# Build the space-joined key form of NORM (words joined by '-') so multi-word phrases
# can be matched against the hyphen-joined flag set without word-splitting surprises.
KEY=$(printf '%s' "$NORM" | tr ' ' '-')

case "$_VAGUE" in
  *" $KEY "*)
    hook_emit "UserPromptSubmit" \
      "[prompt-lint] under-specified ('${NORM}') — name the target (file/symbol) and the desired outcome so the request is unambiguous."
    ;;
esac
exit 0
