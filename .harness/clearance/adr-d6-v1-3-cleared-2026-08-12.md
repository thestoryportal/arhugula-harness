---
artifact: design-substrate/ADR-D6_v1_2.md
version: v1.3
version_note: in-place revision — file name retained per the ADR-D5 v1.6 in-place mechanics; the internal Revision line carries the v1.3 identity
cleared_at: 2026-08-12T12:00:00-07:00
clearance_type: Phase-7-absorbed-via-back-flow-record
back_reference:
  - .harness/b-141-validator-fail-class-cascade-2026-08-12.md
  - .harness/clearance/spec-control-plane-v1-116-cleared-2026-08-09.md
  - "register row B-141; B-138 operator-ratified disposition (a), 2026-08-09"
merge_commit: pending (this leg's PR merge; recorded at the PR)
reviewer_chain:
  - "advisor() arc-open pass (2026-08-12)"
  - out-of-family `just codex-review` rounds at this PR (to convergence)
  - "merge-gate lenses per the LEAN protocol (recorded at the PR)"
supersedes: (none — first clearance marker for an ADR-D6 revision; the v1.2 revision predates the marker convention)
---

# Clearance — ADR-D6 v1.3 (B-141 cascade: §1.5.2 escalation-table domain carry + §1.2.2.1 cross-ref rewording)

**What v1.3 changes.** Two sites: (1) the §1.5.2 escalation-table
`validator.fail.class` row `terminal-fail-exit` → `semantic_inconsistency`
(`ValidatorFailClass` domain per CP spec v1.116 / B-138 disposition (a)); (2) the
§1.2.2.1 `retry.fail_class` Definition clause reworded — `retry.fail_class` KEEPS the
five-value retry-exit domain, and the clause now names its validator-fail source as
the C5 retry-exit ROUTING classification per ADR-D5 v1.6 §1.10, explicitly distinct
from the wire attribute's domain. Everything else — including §1.5.2's
`cause_attribution` / `permanence` / always-sampled rows and the v1.2-era "Cross-ADR
coordination" forward flag (recorded as register row B-139's family at the back-flow
record §4, not chased here) — PRESERVED VERBATIM.
