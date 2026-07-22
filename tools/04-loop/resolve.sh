#!/usr/bin/env bash
# Loop resolution wrapper (U-HK-14/15 sibling). The allowlisted, single-invocation entry
# point the loop uses to record that a previously-DEFERRED item's gate has since been
# answered (ratified, selected, decided) — clearing it from the skip-set and the
# SessionStart pending-summary per loop_lib.sh's RESOLVED-HIL last-write-wins rule.
#
# Why a wrapper: same reasoning as defer.sh — the permission guard (U-HK-12) rejects
# chained/redirected commands, and a bare `source lib.sh loop_lib.sh && loop_resolve …`
# leaves loop_resolve undefined and gets denied in headless. This script sources BOTH
# libs correctly and is allowlisted by the guard as safe regardless of args (it only
# appends a ledger row — it never resolves an arg as a path), so a resolution note
# mentioning "credentials"/"secret" (e.g. "operator ran gh secret set") is recorded,
# not blocked.
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
loop_resolve "$_item" "$_note"
echo "[loop] resolved ${_item} (logged to loop_status.md; cleared from the skip-set and pending summary)"
