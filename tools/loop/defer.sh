#!/usr/bin/env bash
# Loop deferral wrapper (U-HK-14/15). The allowlisted, single-invocation entry point the
# autonomous loop uses to record a per-item gate as DEFERRED-HIL and work AROUND it.
#
# Why a wrapper: the permission guard (U-HK-12) rejects chained/redirected commands and
# `source a b` is malformed (sources only `a`). A bare `source lib.sh loop_lib.sh &&
# loop_defer …` therefore (a) leaves loop_defer undefined and (b) gets denied in headless.
# This script sources BOTH libs correctly and is allowlisted by the guard as safe
# regardless of args (it only appends a ledger row — it never resolves an arg as a path),
# so a deferral REASON mentioning "credentials"/"secret" is recorded, not blocked.
#
# Usage: tools/loop/defer.sh <item-id> <what operator input is needed [+ what was built]>
set -uo pipefail
_H="$(cd "$(dirname "${BASH_SOURCE[0]}")/../hooks" && pwd)"
# shellcheck source=../hooks/lib.sh
. "$_H/lib.sh"
# shellcheck source=../hooks/loop_lib.sh
. "$_H/loop_lib.sh"
# Require an item-id AND a non-empty reason: a reason-less deferral would skip the item
# from the skip-set while giving the operator nothing actionable at SessionStart.
[ "$#" -ge 2 ] || { echo "usage: defer.sh <item-id> <what operator input is needed>" >&2; exit 2; }
_item="$1"; shift
_reason="$*"
[ -n "${_reason//[[:space:]]/}" ] || { echo "defer.sh: a non-empty reason is required (what input the operator must provide)" >&2; exit 2; }
loop_defer "$_item" "$_reason"
echo "[loop] deferred ${_item} (logged to loop_status.md; advancing to the next forward item)"
