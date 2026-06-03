#!/usr/bin/env bash
# Loop stand-down wrapper (U-HK-14/15). The allowlisted, single-invocation entry point the
# loop uses to raise the whole-run halt marker — ONLY at a TRUE stand-down (the forward
# menu is exhausted: every forward item already deferred) or an operator-equivalent stop.
# A single gated item must NOT call this — use defer.sh and advance instead.
#
# Safe regardless of args (logs a STOP row + touches .harness/.loop-halt; stopping the loop
# is never dangerous), so the guard allowlists it. Sources both libs correctly.
#
# Usage: tools/loop/halt.sh [reason]
set -uo pipefail
_H="$(cd "$(dirname "${BASH_SOURCE[0]}")/../hooks" && pwd)"
# shellcheck source=../hooks/lib.sh
. "$_H/lib.sh"
# shellcheck source=../hooks/loop_lib.sh
. "$_H/loop_lib.sh"
loop_log STOP "${*:-forward menu exhausted — awaiting operator input}"
P=$(loop_halt_path)
[ -n "$P" ] && : > "$P" 2>/dev/null
echo "[loop] stand-down: ${*:-forward menu exhausted}. .loop-halt raised; the run will end for operator review."
