---
artifact: design-substrate/Spec_Operational_Discipline_v1_41.md
version: v1.41
cleared_at: 2026-08-12T12:00:00-07:00
clearance_type: Phase-7-absorbed-via-back-flow-record
back_reference:
  - .harness/b-141-validator-fail-class-cascade-2026-08-12.md
  - .harness/clearance/spec-control-plane-v1-116-cleared-2026-08-09.md
  - "register row B-141 (surfaced at the B-138 spec-leg out-of-family review round 3, 2026-08-09; B-138 operator-ratified disposition (a))"
merge_commit: pending (this leg's PR merge; recorded at the PR)
reviewer_chain:
  - "advisor() arc-open pass (2026-08-12) — B-141 selected over the fork-shaped B-71; venue order + carried-value default confirmed"
  - out-of-family `just codex-review` rounds at this PR (to convergence)
  - "merge-gate lenses per the LEAN protocol (recorded at the PR)"
supersedes: spec-operational-discipline-v1-40-cleared-2026-08-11.md
---

# Clearance — Spec_Operational_Discipline v1.41 (B-141 cascade: §14.5.3 validator.fail.class domain carry)

**What v1.41 changes.** One row: C-OD-14 §14.5.3's escalation-on-mismatch table's
`validator.fail.class` value `terminal-fail-exit` → `semantic_inconsistency`
(`ValidatorFailClass` domain member per CP spec v1.116 / B-138 disposition (a)).
The invariance check, escalation prose, catalog-extension paragraph, and the table's
other three rows — including `validator.fail.permanence = permanent` and its C-OD-09
§9.2 always-sampled arm — PRESERVED VERBATIM. The retry-exit ROUTING classification
(`terminal-fail-exit` per ADR-D5 v1.6 §1.10) is demoted from the wire name, not
deleted.

**Same-PR cascade.** `ReplaySemanticDivergenceError.validator_fail_class` default +
docstrings (`harness-od/src/harness_od/idempotency_join_dedup.py`) + witness
(`harness-od/tests/test_idempotency_join_dedup.py`); sibling venue legs ADR-D6 v1.3
(in place at `ADR-D6_v1_2.md`) + CP plan v2.52. Zero production emission sites
construct the carrier at HEAD — declared-shape-only change.
