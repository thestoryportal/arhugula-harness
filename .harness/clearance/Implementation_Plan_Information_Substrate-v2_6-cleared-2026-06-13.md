---
artifact: design-substrate/Implementation_Plan_Information_Substrate_v2_6.md
version: v2.6
cleared_at: 2026-06-13T19:30:00-06:00
clearance_type: Phase-7-absorbed-via-plan-decomposition (R-FS-1 arc #6 / B1-plan — the IS-axis leg; NEW foundational unit U-IS-19 decomposing the cleared IS spec v1.8 §5.4 `branch_metadata` sidecar carrier)
back_reference:
  - design-substrate/Spec_Information_Substrate_v1.md §5.4 (the cleared `branch_metadata` carrier this plan decomposes; cleared at `.harness/clearance/Spec_Information_Substrate-v1_8-cleared-2026-06-13.md`, PR #531)
  - design-substrate/Implementation_Plan_Control_Plane_v2_32.md (sibling co-publication + the B1-arc aggregate dependency-graph home; the cross-axis edge U-CP-84 → U-IS-19 is declared CP-side there)
  - design-substrate/Implementation_Plan_Harness_Runtime_v2_43.md (sibling co-publication)
  - .harness/r-fs-1-b1-topology-orchestration-design-v1.md §8 (B1-plan cascade row)
  - .harness/adversarial-review-r-fs-1-arc-6-b1-plan.md (the shared genuine-agent pre-merge review covering all 3 plan legs)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - harness-adversarial-reviewer Phase-7 pre-merge review (dedicated-agent, 25 tool-uses; shared review at `.harness/adversarial-review-r-fs-1-arc-6-b1-plan.md`) — VERDICT **APPROVE-WITH-CLASS-3**; verified U-IS-19 `BranchMetadata {parent_action_id, branch_index, terminal_status: Literal['cancelled','completed','timed_out']|None}` is transcribed VERBATIM from IS §5.4 (lines 481–487 — no spec extension), `Depends on: (none)` foundational, IS-0-outbound cycle guard intact.
  - out-of-family Codex review (`just codex-review-uncommitted`) — 2 [P2] both fixed (pointer-index lineage + this marker's prior absence); no decomposition defect.
  - advisor() pre-substantive scoping (the coverage-matrix-first + carrier-home-impl-discretion + IS-0-outbound disciplines; full account at the CP-leg marker `Implementation_Plan_Control_Plane-v2_32-cleared-2026-06-13.md`)
  - design-phase bundled-absorption posture (CLAUDE.md §11.4; X-AL-3 satisfied by this marker + the shared adversarial review as `.harness/` back-flow companions)
supersedes: design-substrate/Implementation_Plan_Information_Substrate_v2_5.md v2.5
superseded_by:
---

# Clearance — `Implementation_Plan_Information_Substrate v2.6`

v2.6 is the **IS-axis leg of R-FS-1 arc #6 (B1-plan)** — ONE NEW foundational unit **U-IS-19** decomposing the cleared **IS spec v1.8 §5.4** `branch_metadata` D-derivative sidecar carrier (`BranchMetadata` = `{parent_action_id, branch_index, terminal_status}` + the optional 8th `branch_metadata` field on `StateLedgerEntry`/`EntryPayload` + omit-when-`None` canonicalization). The **producer** (the CP `WorkflowDriver` write-cadence) lives at CP plan v2.32 U-CP-84; this IS unit authors only the carrier shape + canonicalization contribution. Design-substrate (plan-layer); **no code lands** (impl is B1-impl-N).

**Carve-outs.** Carrier-home (`harness-core` vs `harness-is`) stays implementer-discretion (hard constraint: NOT `harness-cp`, IS 0-outbound); no §5.2-analogue resolver (producer-supplied, not resolver-derived); `branch_path` is NOT in this carrier (CP-side §25.16 idempotency-key). U-IS-19 `Depends on: (none)`, ZERO IS-outbound edge — the cross-axis edge U-CP-84 → U-IS-19 is declared inbound from the CP side.

## Notes
- Coordinated next arc: B1-impl-N (the `BranchMetadata` carrier + the canonicalization contribution land in code).
- See `.harness/clearance/README.md`.
