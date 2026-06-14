---
artifact: design-substrate/Implementation_Plan_Harness_Runtime_v2_43.md
version: v2.43
cleared_at: 2026-06-13T19:30:00-06:00
clearance_type: Phase-7-absorbed-via-plan-decomposition (R-FS-1 arc #6 / B1-plan — the runtime-axis leg; 2 NEW units U-RT-113/114 decomposing the cleared runtime spec v1.48 §9 + §14.5.3)
back_reference:
  - design-substrate/Spec_Harness_Runtime_v1.md §9 (C-RT-09 `'partial'` projection) + §14.5.3 (branch `AgentRole` dispatch-read) + §2.2 (materialization site — §2.2a no-change → O-RT-1); cleared at `.harness/clearance/Spec_Harness_Runtime-v1_48-cleared-2026-06-13.md`, PR #533
  - design-substrate/Implementation_Plan_Control_Plane_v2_32.md (sibling co-publication + the B1-arc aggregate dependency-graph home; the cross-axis edge U-RT-114 → U-CP-81 is recorded there)
  - design-substrate/Implementation_Plan_Information_Substrate_v2_6.md (sibling co-publication)
  - .harness/r-fs-1-b1-topology-orchestration-design-v1.md §8 (B1-plan cascade row)
  - .harness/adversarial-review-r-fs-1-arc-6-b1-plan.md (the shared genuine-agent pre-merge review)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - harness-adversarial-reviewer Phase-7 pre-merge review (dedicated-agent, 25 tool-uses; shared review) — VERDICT **APPROVE-WITH-CLASS-3**; verified U-RT-113 `Literal['completed','drained','failed','paused','partial']` transcribed VERBATIM from runtime §9 (line 2450 — no spec extension); U-RT-114 `Depends on: [U-CP-81 (cross-axis: CP)]` runs runtime→CP downstream (no cycle); §2.2a no-change disposition (O-RT-1) is correct (not a unit per atomicity §3.1).
  - out-of-family Codex review (`just codex-review-uncommitted`) — 2 [P2] both fixed (pointer-index lineage + this marker's prior absence); no decomposition defect.
  - advisor() pre-substantive scoping (the CP-vs-runtime code-home discriminator: §2.2(b/c/d) are CP-driver-internal → covered CP-side; only §9 projection + §14.5.3 role-read are runtime-axis units; full account at the CP-leg marker)
  - design-phase bundled-absorption posture (CLAUDE.md §11.4; X-AL-3 satisfied by this marker + the shared adversarial review)
supersedes: design-substrate/Implementation_Plan_Harness_Runtime_v2_42.md v2.42
superseded_by:
---

# Clearance — `Implementation_Plan_Harness_Runtime v2.43`

v2.43 is the **runtime-axis leg of R-FS-1 arc #6 (B1-plan)** — TWO NEW units decomposing the cleared **runtime spec v1.48**: **U-RT-113** the `RunStatus.PARTIAL` runtime projection (`_CP_TO_RT_STATUS[PARTIAL]→'partial'` + the C-RT-09 §9 `status` `Literal` widen) + **U-RT-114** the branch `AgentRole` dispatch-read (the model-binding half of the §14.5.3 role seam; per-role prompt deferred to B4). Design-substrate (plan-layer); **no code lands** (impl is B1-impl-N).

**Code-home split (the scoping).** The runtime spec authored three sites; their plan homes split by code-residence: §9 → U-RT-113 (runtime `api.py`); §14.5.3 → U-RT-114 (runtime `llm_dispatch.py`); §2.2(b/c/d) buffered-drain/write-cadence/branch-context → **CP plan v2.32** (CP-driver-internal); §2.2(a) materialization-site (existing stage-5 sufficient, no new binding) → **§6 Open-item O-RT-1**, NOT a unit (per atomicity §3.1 — "no change needed" is not a coherent change).

## Notes
- Coordinated next arc: B1-impl-N (the `api.py` `_CP_TO_RT_STATUS` flip + the `llm_dispatch.py` role-read land in code).
- See `.harness/clearance/README.md`.
