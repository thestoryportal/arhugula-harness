---
artifact: design-substrate/Spec_Operational_Discipline_v1_40.md
version: v1.40
cleared_at: 2026-08-11T23:59:00-07:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_b144_cp_24_1b_stale_retable.md
  - .harness/clearance/spec-control-plane-v1-117-cleared-2026-08-11.md
  - "PR #1311 out-of-family review rounds 4-5 (the OD ingestion carry: map row at r4, the C-OD-05 §5.1 row-9 spec pin at r5)"
merge_commit: pending (this leg's PR merge; recorded at the PR)
reviewer_chain:
  - "codex r4 P1 (OD map engine=3 vs CP manifest 4) + r5 P1 (C-OD-05 §5.1 row 9 pins 3 — the sweep claim 'no OD spec pin' falsified); both grounded valid and absorbed as this delta + the code cascade"
  - out-of-family `just codex-review` continuation rounds at this PR (to convergence)
  - "merge-gate: lens 2 x2 (APPROVE both, 67-state and 68-state); lenses 1+3 run at the final diff (recorded at the PR)"
supersedes: spec-operational-discipline-v1-39-cleared-2026-08-09.md
---

# Clearance — Spec_Operational_Discipline v1.40 (B-144 OD leg: §5.1 row-9 engine count carry)

**What v1.40 changes.** One cell: C-OD-05 §5.1 row 9 (`engine.*`) `Attribute count`
3 → 4, carrying the C-CP-09 §9.1 v1.3 supersession (+`engine.replay_disposition`,
ADR-D1 v1.2 §1.1.1) the row's own `Ingest verbatim` posture + citation already point
at. All other §5.1 rows — including row 6's hitl.* "11 attributes across 4 span
names" cell (register row B-153's scope) — and every other C-OD contract PRESERVED
VERBATIM.

**Same-PR cascade.** `harness-od/src/harness_od/namespace_map.py` engine row 3 → 4 +
`test_cp_source_namespace_verification.py` dict/docstring; no OD-side aggregate sums
the map; the OD plan does not restate the §5.1 per-row counts (swept at HEAD).
