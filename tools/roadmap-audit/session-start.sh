#!/usr/bin/env bash
# Roadmap session-start audit — fires at every Claude Code session open.
# Implements CLAUDE.md §12.1 audit + §12.2.1 fixed-point carve-out.
# Emits JSON with additionalContext per Claude Code SessionStart hook protocol.
#
# Token budget: match=~17 tokens, lag=~25 tokens, drift=~35 tokens.
# Total preamble overhead at session start: under 50 tokens worst case.
#
# Always exit 0; encode any failure in additionalContext to avoid silent skip.
# Shared conventions (emit shape, hash recipe, bounded fetch, default branch) live
# in tools/hooks/lib.sh — sourced below. Tested by tools/roadmap-audit/test_session_start.sh.

set -uo pipefail

# Source the shared hook library; if missing, no-op rather than crash a session.
_LIB="$(dirname "${BASH_SOURCE[0]}")/../hooks/lib.sh"
[ -f "$_LIB" ] || exit 0
# shellcheck source=../hooks/lib.sh
. "$_LIB"
hook_review_isolated && exit 0
# Loop ledger lib (optional) — used only to surface pending DEFERRED-HIL at engagement.
_LOOPLIB="$(dirname "${BASH_SOURCE[0]}")/../hooks/loop_lib.sh"
# shellcheck source=../hooks/loop_lib.sh
[ -f "$_LOOPLIB" ] && . "$_LOOPLIB"

PROJECT_DIR=$(hook_project_dir)
[ -z "$PROJECT_DIR" ] && exit 0
cd "$PROJECT_DIR" || exit 0

ROADMAP_STATUS=".harness/roadmap_status.md"
ROADMAP="Project_Roadmap_v1.md"

# Pending operator-input summary from the last loop run (empty when none / no ledger).
# Appended to EVERY emit() so the deferrals are "clearly presented when the operator
# engages next", regardless of which audit branch (match / lag-expected / drift) fires.
_HIL=""
if command -v loop_pending_hil_summary >/dev/null 2>&1; then
  # C-HE-20 (U-HE-09): re-surface deferrals older than the 24 h TTL as NOTIFY rows first --
  # a notification threshold only; it never resolves, reclaims, or transitions anything.
  command -v loop_hil_ttl_resurface >/dev/null 2>&1 && loop_hil_ttl_resurface 2>/dev/null
  # C-HE-10 §2 (U-HE-30): delivery is PULL-BASED and happens HERE, not in the lanes --
  # one batched prompt per cause group whose window has closed, emitted exactly once per
  # generation (the COALESCE-DELIVERED row makes a second SessionStart path a no-op).
  #
  # The batch renders BESIDE the pending summary, never instead of it -- the same
  # segments-are-independent rule C-HE-09 §5 already applies to NOTIFY, and here it is
  # load-bearing rather than cosmetic (codex r2 P1). Exactly-once delivery across a crash
  # is unachievable: the COALESCE-DELIVERED row is necessarily durable before this
  # process publishes its output, so a crash in between would mark a gate delivered that
  # the operator never saw. Keeping the summary always-on removes the consequence -- a
  # swallowed batch still surfaces as a pending item, every session, until it is
  # RESOLVED. The two lines say different things and both are wanted: the summary is the
  # standing register of what is still open, the batch is the once-per-generation notice
  # that these N gates share one cause and their window has closed.
  _d=""
  command -v loop_hil_deliver >/dev/null 2>&1 && _d=$(loop_hil_deliver 2>/dev/null | paste -sd' ' -)
  _h=$(loop_pending_hil_summary 2>/dev/null)
  [ -n "$_d" ] && _HIL="${_HIL} $_d"
  [ -n "$_h" ] && _HIL="${_HIL} $_h"
  # C-HE-09 §5 (U-HE-29): NOTIFY rows render BESIDE the pending-HIL summary, never merged
  # into it. The distinction is load-bearing for the operator: the HIL line says "the loop
  # is gated on you"; the notify line says "here is something you may want to know". Its
  # own segment, appended after -- so an empty HIL summary still surfaces notices, and a
  # populated one is never diluted by them.
  if command -v loop_notify_summary >/dev/null 2>&1; then
    _n=$(loop_notify_summary 2>/dev/null)
    [ -n "$_n" ] && _HIL="${_HIL} $_n"
  fi
fi

# C-HE-03 §5 (U-HE-18): one ground-truth reconcile pass over every non-terminal arc
# reservation at session start (the merge lane is the other caller, U-HE-22). DETACHED --
# codex-session-start wraps this whole script in an 8 s hook_bounded slice and discards
# failures (codex U-HE-18 r1 P1), so an inline gh-backed pass could starve the audit emit
# below; the spawn costs milliseconds and never consumes the parent's budget. Durable
# outcomes surface through the loop ledger (DEFERRED-HIL / NOTIFY rows read by
# loop_pending_hil_summary at the NEXT engagement, C-HE-20 §1). U-HE-29 landed
# loop_log_structured, so the activation gate below is now SATISFIED and the pass runs:
# its escalation rows reach the shared ledger rather than only the store-local
# .reconcile.log (the pre-U-HE-29 registered residual, plan U-HE-18 rev note). The dir
# pre-probe mirrors arc_metrics.py's QUEUE_DIR default so sessions without a reservation
# store skip the interpreter spawn entirely; if the defaults ever drift the only cost is
# a skipped best-effort pass (the merge lane re-runs it).
_QROOT="${ARC_METRICS_QUEUE_DIR:-$HOME/.gstack/projects/arhugula-v2/arc-metrics-queue}"
_RROOT="${_QROOT}/reservations"
_RESV=""
# Activation gate (codex r5 P2): the pass's C-HE-20 escalation rows need loop_lib.sh's
# `loop_log_structured` (U-HE-29), which HAS landed -- the gate is retained as a live
# precondition, not a countdown: a checkout whose loop_lib.sh predates U-HE-29 (bisect,
# an old worktree) would otherwise run an unattended pass that can only fail closed into
# the log. Synchronous callers (CLI, U-HE-22 merge lane) are unaffected: their exit codes
# surface directly.
if [ -e "$_RROOT" ] || [ -L "$_RROOT" ]; then if [ ! -d "$_RROOT" ] || [ -L "$_RROOT" ]; then
  # The store root exists but is not a plain directory: corruption of authoritative
  # state, never an absent-store clean skip (codex r10 P2) -- fail open here would hide
  # exactly what reconcile_all classifies as corrupt.
  _RESV=" resv=ERR(reservations store corrupt: ${_RROOT} is not a directory)"
fi; fi
if [ -d "$_RROOT" ] && [ ! -L "$_RROOT" ]; then
  # Surface the LAST pass's outcome (codex r2 P2) UNGATED by the U-HE-29 activation gate
  # below (codex r7 P2): the store-local log can already exist from the CLI / merge-lane
  # callers pre-U-HE-29, and an rc!=0 pass must surface regardless of which caller wrote
  # it. The log write itself is store-owned + atomically renamed inside reservations.py
  # (codex r2 P1/r3 P2). jq on the authoritative rc field (codex r4 P3: a substring grep
  # would false-positive on an arc id containing "ERROR"); jq is already a hard
  # dependency of hook_emit. A corrupt/unparseable log reads as non-zero -- fail closed.
  if [ -f "${_RROOT}/.reconcile.log" ] && [ ! -L "${_RROOT}/.reconcile.log" ]; then
    if [ "$(jq -r '.rc' "${_RROOT}/.reconcile.log" 2>/dev/null)" != "0" ]; then
      _RESV=" resv=ERR(last reconcile pass; see ${_RROOT}/.reconcile.log)"
    fi
  elif [ -e "${_RROOT}/.reconcile.log" ] || [ -L "${_RROOT}/.reconcile.log" ]; then
    # Log path exists but is not a regular file (directory/symlink/other): a structural
    # store fault the detached pass cannot repair or report -- surface it here (codex
    # r10 P2), never a silent skip.
    _RESV=" resv=ERR(reconcile log path corrupt: not a regular file)"
  fi
  if [ -f tools/reservations.py ] && command -v uv >/dev/null 2>&1 \
    && grep -q 'loop_log_structured()' tools/hooks/loop_lib.sh 2>/dev/null; then
    nohup uv run python tools/reservations.py reconcile-all --log-to-store \
      >/dev/null 2>&1 &
  fi
fi

# Single-line additionalContext for the SessionStart event (wraps the lib helper). The
# pending-HIL summary is appended so an operator opening a fresh session always sees what
# the last unattended loop run deferred for them.
emit() { hook_emit "SessionStart" "$1${_HIL}${_RESV}"; }

[ -f "$ROADMAP_STATUS" ] || emit "[ROADMAP] absent — see Project_Roadmap_v1.md §7"
[ -f "$ROADMAP" ] || emit "[ROADMAP] roadmap_status.md exists but roadmap absent"

# Compute current workspace_state_hash per CLAUDE.md §12.1 step 2 recipe.
HEAD=$(git rev-parse HEAD 2>/dev/null | head -c 8)
PRS=$(gh pr list --state open --json number,headRefName --jq '. | sort_by(.number) | map("\(.number):\(.headRefName)") | join(",")' 2>/dev/null || echo "")
FORKS=$(ls .harness/class_1_fork_*.md .harness/class_2_fork_*.md 2>/dev/null | wc -l | tr -d ' ')
BATCH=$(ls .harness/phase-7d-retirement-events-batch-*.md 2>/dev/null | sort -V | tail -1)
COMPUTED=$(hook_state_hash "$HEAD" "$PRS" "$FORKS" "$BATCH")

# Extract stored hash + next_action from roadmap_status.md.
STORED_HASH=$(grep '`workspace_state_hash`' "$ROADMAP_STATUS" 2>/dev/null | head -1 | grep -oE '[a-f0-9]{12}' | head -1)
NEXT=$(hook_roadmap_next "$ROADMAP_STATUS")

PR_COUNT=$([ -z "$PRS" ] && echo 0 || echo "$PRS" | tr ',' '\n' | grep -c .)

# Recurrence guard (CLAUDE.md §12.3 / roadmap drift-log line-92 precedent): when on the
# default branch, detect a local checkout trailing origin. The base hook reads only the LOCAL
# roadmap_status.md + HEAD, so a checkout behind origin yields a globally-stale next-action
# that still looks locally-consistent (the Cluster A/B drift, 2026-05-31). Only fires on the
# default branch so feature-branch worktrees that intentionally trail main get no noise.
# Best-effort fetch is bounded (and a no-op offline) so the hook can never hang — it falls
# back to the existing origin ref, which sibling worktrees/jobs keep fresh.
DEFAULT_BRANCH=$(hook_default_branch)
CURRENT_BRANCH=$(git symbolic-ref --quiet --short HEAD 2>/dev/null || echo "")
if [ "$CURRENT_BRANCH" = "$DEFAULT_BRANCH" ]; then
  hook_bounded 4 git fetch --quiet --no-tags origin "$DEFAULT_BRANCH" >/dev/null 2>&1 || true
  BEHIND=$(git rev-list --count "HEAD..origin/${DEFAULT_BRANCH}" 2>/dev/null || echo 0)
  if [ "${BEHIND:-0}" -gt 0 ] 2>/dev/null; then
    emit "[ROADMAP] behind-origin=${BEHIND} on ${DEFAULT_BRANCH} — fast-forward (git merge --ff-only origin/${DEFAULT_BRANCH}) before deriving next-action; roadmap next=${NEXT:-?} may be stale (§12.3 / line-92 precedent)."
  fi
fi

if [ "$COMPUTED" = "$STORED_HASH" ]; then
  emit "[ROADMAP] hash=ok next=${NEXT:-?} in_flight=${PR_COUNT} forks=${FORKS}"
fi

# Hash mismatch — check §12.2.1 fixed-point carve-out. A terminating refresh requires
# BOTH (a) the reserved commit-title prefix "ops: roadmap status refresh " AND (b) a
# roadmap-status-only changed-file set (EXACTLY roadmap_status.md — see
# hook_is_roadmap_status_only_set for the §12.2.1 set). The title is format-agnostic on
# the post-NNN suffix — refreshes have been titled `post-PR-NNN` (early) and `post-#NNN`
# / `post-#NNN/#NNN` / `post-#NNN (...)` (later) — so we match the prefix, not a specific
# NNN format, keeping the lag-expected fixed point robust to either convention. The
# roadmap-status-only conjunct is load-bearing: keying on the title alone would let a
# substantive commit mis-titled with the reserved prefix suppress a genuine drift halt
# (the false negative post-merge-refresh.sh + prompt-context.sh also guard).
is_terminating_refresh_ref() {
  local _ref _title _files
  _ref="$1"
  _title=$(git log -1 --format=%s "$_ref" 2>/dev/null || echo "")
  echo "$_title" | grep -qE '^ops: roadmap status refresh ' || return 1
  _files=$(git show --name-only --pretty=format: "$_ref" 2>/dev/null | grep -v '^$' | sort -u)
  hook_is_roadmap_status_only_set "$_files"
}

if is_terminating_refresh_ref HEAD; then
  emit "[ROADMAP] hash=lag-expected next=${NEXT:-?} (post-refresh fixed-point §12.2.1)"
fi

PARENTS=$(git rev-list --parents -n 1 HEAD 2>/dev/null || echo "")
# shellcheck disable=SC2086 # intentional word splitting of rev-list parent SHAs.
set -- $PARENTS
if [ "$#" -ge 3 ]; then
  FIRST_PARENT="$2"
  SECOND_PARENT="$3"
  CHANGED_FILES=$(git diff --name-only "$FIRST_PARENT" HEAD 2>/dev/null | sort -u)
  if hook_is_roadmap_status_only_set "$CHANGED_FILES"; then
    if is_terminating_refresh_ref "$SECOND_PARENT"; then
      emit "[ROADMAP] hash=lag-expected next=${NEXT:-?} (post-refresh fixed-point §12.2.1)"
    fi
  fi
fi

# Genuine drift — surface for §12.3 halt-and-reconcile. Reached when the hash mismatches
# AND the tip is not a roadmap-status-only terminating refresh (incl. a mis-titled
# substantive commit — which now correctly halts here rather than passing as lag-expected).
emit "[ROADMAP DRIFT] stored=${STORED_HASH:-none} computed=${COMPUTED} next=${NEXT:-?} action=§12.3"
