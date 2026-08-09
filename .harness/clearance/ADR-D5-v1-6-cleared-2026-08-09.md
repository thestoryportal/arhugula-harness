---
artifact: design-substrate/ADR-D5.md
version: v1.6
cleared_at: 2026-08-09T00:00:00-06:00
clearance_type: spec-writer-apply-pass
back_reference:
  - design-substrate/Spec_Control_Plane_v1_116.md (the bundled CP spec leg)
  - .harness/clearance/spec-control-plane-v1-116-cleared-2026-08-09.md
  - .harness/forward-register.yaml (B-138 CLOSED; B-139 minted)
merge_commit: pending
reviewer_chain:
  - operator ratification of B-138 disposition (a), 2026-08-09 (AskUserQuestion)
  - out-of-family codex review round 1 (P1 — the authority-chain conflict this amendment resolves)
supersedes: ADR-D5-v1-5-cleared-2026-07-16.md
---

# Clearance — `ADR-D5 v1.6`

v1.6 reconciles ADR-D5 §1.10.1 — the canonical declaration site for the `validator.fail.*`
attribute names — with the operator-ratified B-138 disposition (a). The amendment exists
because the authority chain (ADR over spec, root `CLAUDE.md` §1.3) forbids a spec-only delta
from overriding an accepted ADR: the codex round on the CP v1.116 leg caught exactly that (P1),
so the correction is applied at the source and bundled in the same PR.

Five amendment sites, all in the header revision chain + §1.10.1: (1) revision-chain and
revision-date entries; (2) bullet 1 — `validator.fail.class` re-declared with the
C-CP-25→C-CP-28 `ValidatorFailClass` domain, emission conditional on a populated `fail_class`,
the composer's `unspecified` sentinel named, and the five retry-exit values retained as the
§1.10 escalation-order discriminator (demoted from the wire name, never deleted); (3) bullet 3 —
the permanence derivation clause demoted with the taxonomy, the outcome projection recorded as
lossy, the derivation decision routed to register row `B-124`; (4) bullet 2 — cause_attribution's
zero-producer state cross-referenced to new row `B-139`; (5) no other §1.10/§1.10.1 text moved.
§1.10's escalation order, staircase, palettes, and audit discipline are preserved verbatim.
