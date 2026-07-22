#!/usr/bin/env bash
# Loop resolution wrapper (U-HK-14/15 sibling). NOT permission-guard-allowlisted (unlike
# defer.sh/halt.sh) — see the permission-guard.sh §2 short-circuit comment for why: this
# script ASSERTS a human already answered a gate, so it must go through the normal
# deny-list-then-ask flow rather than bypass it, reachable only from an attended session.
#
# Records that a previously-DEFERRED item's gate has since been answered (ratified,
# selected, decided) — clearing it from the skip-set and the SessionStart pending-summary
# per loop_lib.sh's RESOLVED-HIL last-write-wins rule. Sources both libs correctly (the
# same malformed-chained-source problem defer.sh/halt.sh solve), and validates its
# arguments rather than blindly trusting them (codex [P2] round 3 on this arc): a
# malformed or not-currently-pending item-id must error, not silently report success while
# writing a row that misrepresents the ledger.
#
# Usage: tools/04-loop/resolve.sh <item-id> <how it was resolved + evidence pointer>
set -uo pipefail
_H="$(cd "$(dirname "${BASH_SOURCE[0]}")/../hooks" && pwd)"
# shellcheck source=../hooks/lib.sh
. "$_H/lib.sh"
# shellcheck source=../hooks/loop_lib.sh
. "$_H/loop_lib.sh"
# Require an item-id AND a non-empty note: a note-less resolution would clear the item
# from the skip-set while giving a future reader no evidence of how/where it was answered.
[ "$#" -ge 2 ] || { echo "usage: resolve.sh <item-id> <how it was resolved + evidence pointer>" >&2; exit 2; }
_item="$1"; shift
_note="$*"
[ -n "${_note//[[:space:]]/}" ] || { echo "resolve.sh: a non-empty note is required (how the gate was answered)" >&2; exit 2; }
# Item-id shape must match loop_skip_set's own filter (tools/hooks/loop_lib.sh) — kept as a
# literal duplicate rather than a shared helper to avoid adding a new cross-file dependency
# for a one-line regex; if loop_skip_set's filter ever changes, update this to match. This
# check is technically subsumed by the pending-check below (loop_skip_set's own filter would
# never surface a malformed id as pending either), but it gives a clearer, more specific
# error message for the common typo case rather than the generic "not pending" message.
case "$_item" in
  *[[:space:]]*) _item_ok="" ;;
  *) printf '%s' "$_item" | grep -Eq '^(R|B)-[A-Za-z0-9._-]+$' && _item_ok=1 || _item_ok="" ;;
esac
[ -n "$_item_ok" ] || { echo "resolve.sh: '${_item}' is not a valid item-id (expected R-* or B-*)" >&2; exit 2; }
# Must be currently PENDING (a live DEFERRED-HIL not already RESOLVED-HIL since the last
# ACTIVATE) — else this call would write a RESOLVED-HIL row and report success for an item
# that was never deferred, already resolved, or a typo of the real id.
case " $(loop_skip_set) " in
  *" ${_item} "*) ;;
  *) echo "resolve.sh: '${_item}' is not currently a pending DEFERRED-HIL item — nothing to resolve" >&2; exit 3 ;;
esac
loop_resolve "$_item" "$_note"
echo "[loop] resolved ${_item} (logged to loop_status.md; cleared from the skip-set and pending summary)"
