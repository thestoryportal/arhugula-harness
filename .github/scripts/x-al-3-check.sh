#!/usr/bin/env bash
# X-AL-3 silent-absorption guard
#
# Per workspace CLAUDE.md §4.4 + Workflow §2.7.6: no silent H_T design extension
# at Phase 7 execution. New H_T primitives or design changes surfaced at
# execution-time must route through documented back-flow (Class 1/2/3 fork doc,
# architect recommendation, retirement event, or P5-CK / P6-CK clearance marker).
#
# This script runs in CI (and locally as advisory). It fails when a PR diff
# touches design-substrate/* without any accompanying documentation in .harness/.
#
# Inputs:
#   BASE_SHA — git SHA of the PR base commit
#   HEAD_SHA — git SHA of the PR head commit
#   PR_LABELS — JSON array of PR label names (e.g. '["bug","design-phase-direct"]')
#
# Exit codes:
#   0 — guard passed
#   1 — guard failed (design-substrate touched without back-flow doc)
#   2 — script error (missing env vars, etc.)

set -euo pipefail

if [ -z "${BASE_SHA:-}" ] || [ -z "${HEAD_SHA:-}" ]; then
  echo "ERROR: BASE_SHA and HEAD_SHA env vars are required." >&2
  exit 2
fi

PR_LABELS="${PR_LABELS:-[]}"

DIFF_FILES=$(git diff --name-only "$BASE_SHA" "$HEAD_SHA" || true)

# Count design-substrate edits
DESIGN_SUBSTRATE_FILES=$(echo "$DIFF_FILES" | grep '^design-substrate/' || true)
DESIGN_SUBSTRATE_COUNT=$(echo -n "$DESIGN_SUBSTRATE_FILES" | grep -c . || true)

# Count back-flow documentation (any .md or clearance marker under .harness/)
BACK_FLOW_FILES=$(echo "$DIFF_FILES" | grep -E '^\.harness/.+(\.md|/CLEARED)$' || true)
BACK_FLOW_COUNT=$(echo -n "$BACK_FLOW_FILES" | grep -c . || true)

# Check for escape-hatch label
HAS_ESCAPE_LABEL=0
if echo "$PR_LABELS" | grep -q '"design-phase-direct"'; then
  HAS_ESCAPE_LABEL=1
fi

echo "X-AL-3 guard inputs:"
echo "  design-substrate touched: $DESIGN_SUBSTRATE_COUNT file(s)"
echo "  back-flow doc touched:    $BACK_FLOW_COUNT file(s)"
echo "  design-phase-direct label: $HAS_ESCAPE_LABEL"
echo ""

if [ "$DESIGN_SUBSTRATE_COUNT" -eq 0 ]; then
  echo "✓ Guard PASSED — no design-substrate edits."
  exit 0
fi

if [ "$HAS_ESCAPE_LABEL" -eq 1 ]; then
  echo "✓ Guard PASSED — 'design-phase-direct' label present."
  echo ""
  echo "Files modified in design-substrate/:"
  echo "$DESIGN_SUBSTRATE_FILES" | sed 's/^/  - /'
  exit 0
fi

if [ "$BACK_FLOW_COUNT" -gt 0 ]; then
  echo "✓ Guard PASSED — back-flow documentation included."
  echo ""
  echo "Files modified in design-substrate/:"
  echo "$DESIGN_SUBSTRATE_FILES" | sed 's/^/  - /'
  echo ""
  echo "Back-flow documentation in this PR:"
  echo "$BACK_FLOW_FILES" | sed 's/^/  - /'
  exit 0
fi

# Failure path
cat <<EOF
::error::X-AL-3 silent-absorption guard FAILED

This PR modifies design-substrate/* without any accompanying back-flow
documentation in .harness/. Per workspace CLAUDE.md §4.4 + Workflow §2.7.6,
design changes at Phase 7 execution time must route through documented
back-flow channels.

Files modified in design-substrate/:
EOF
echo "$DESIGN_SUBSTRATE_FILES" | sed 's/^/  - /'
cat <<EOF

To resolve, choose one:

  (a) File a fork doc at .harness/class_N_fork_<slug>.md or
      .harness/class_N_tension_<slug>.md documenting the design defect
      that triggered this design-substrate edit.

  (b) File an architect recommendation at
      .harness/architect_recommendation_<slug>.md if this is a Phase 7
      tension-resolution arc.

  (c) Include the corresponding retirement event filing at
      .harness/phase-7d-retirement-events-batch-N.md if this is a
      doc-hygiene refresh paired with a retirement transit.

  (d) Include a P5-CK / P6-CK clearance marker at .harness/clearance/...
      (per PR #49 convention, once landed).

  (e) Add label "design-phase-direct" to this PR for routine doc-only
      design-substrate edits (e.g., typo fix, formatting, citation
      version-bump only) that do not extend H_T design surface.

Escape-hatch label discipline: use sparingly. The presence of the label
is recorded; reviewers should verify it's appropriate for the change.

See workspace CLAUDE.md §4.4 (X-AL-3 anti-leakage rule) and §10.5 (failure
mode: silent H_T design extension) for full back-flow discipline.
EOF

exit 1
