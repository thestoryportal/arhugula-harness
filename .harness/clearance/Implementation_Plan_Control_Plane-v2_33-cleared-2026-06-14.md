---
artifact: design-substrate/Implementation_Plan_Control_Plane_v2_33.md
version: v2.33
cleared_at: 2026-06-14T00:00:00-06:00
clearance_type: Phase-6-plan-amendment (atomic-unit decomposition of the cleared B3 spec legs + design impl-against-cleared-spec gaps; R-FS-1 arc #20 / B3-plan; CP-axis leg)
back_reference:
  - .harness/r-fs-1-b3-plan-decomposition.md (the B3-plan decomposition summary + coverage matrix + DAG + the G2c fork-class finding)
  - design-substrate/Spec_Harness_Runtime_v1.md §3.8 (B3-spec-1, cleared v1.49) + §14.8.9 (B3-spec-2, cleared v1.50) — the cleared specs this plan decomposes
  - .harness/class_1_fork_b3_1_hitl_auto_approve_policy_field.md (F-B3-1) + .harness/class_1_fork_b3_2_timeout_degradation_vocabulary_drift.md (F-B3-2) — the ratified decisions + carried ACs
  - .harness/r-fs-1-b3-smart-hitl-design-v1.md §2/§3.2/§4.1/§5/§6.1/§8.2/§8.3 (the gap-set + sequence authority); cleared #549
  - design-substrate/Spec_Control_Plane_v1_2.md §21.8 + §19.1 + §20.6; design-substrate/ADR-D5.md §1.6; design-substrate/Spec_Action_Surface_v1.md C-AS-03 §3.1 + C-AS-12 §12.1 (the G2c authority — confirms `ToolContract` has no typed `per_tool_gate_level` field)
  - .harness/adversarial-review-r-fs-1-b3-plan.md (the filed pre-merge adversarial review report)
  - design-substrate/Implementation_Plan_Control_Plane_v2_32.md (the delta base — preserved verbatim per delta-only-plan-chain)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - implementation-planner (genuine dedicated-agent invocation per [[feedback-genuine-skill-invocation-dedicated-agent]], 67 tool-uses) — produced the decomposition: 8 NEW units (U-CP-91/92 CP + U-RT-115..120 runtime), coverage-matrix-complete, acyclic aggregate DAG, delta-only-verified; surfaced the G2c fork-class finding (the design §4.1 mis-framed G2c as pure-impl; AS C-AS-03 §3.1 declares no typed `per_tool_gate_level` field → REGISTERED as O-CP-3, not pre-stamped fork, not silently impl'd).
  - main-agent integrity verification (direct read, NOT summary-trust per CLAUDE.md §7): confirmed delta-only preservation (U-CP-01..90 + §1 B1-coverage rows present; v2.33 446 lines vs v2.32 345); the G2c claim by direct read of AS C-AS-03 §3.1 + `tool_contract.py` (typed field genuinely absent); the new units + O-CP-3 present.
  - harness-adversarial-reviewer Phase-6 pre-merge review (dedicated-agent, 34 tool-uses; full report `.harness/adversarial-review-r-fs-1-b3-plan.md`) — VERDICT **APPROVE-WITH-CLASS-3** (0 blocking / 0 substantive / 1 doc-hygiene). All 9 load-bearing claims verified by direct read (coverage-complete; ZERO spec extension; G2c→O-CP-3 correct — byte-compared AS C-AS-03 §3.1 + tool_contract.py; DAG acyclic; delta-only byte-compared prior unit bodies; carried ACs → units; homing correct; U-CP-91 plan-layer not CP-spec fork). F3-01 (doc-hygiene): U-CP-92 cross-ref under-scoped a `harness-runtime` vocab-B docstring (`hitl_placement.py:167-171`) → **APPLIED** (U-CP-92 cross-ref widened to sweep `harness-*/src`).
  - out-of-family Codex review (`just codex-review-uncommitted`) — 3 [P2], **ALL APPLIED:** (1) clearance markers claimed-but-absent → **filed (this marker + the runtime v2.44 marker)**; (2) plan-head pointer bumps owed-in-same-change → **applied (CLAUDE.md §2.4 + claude-artifact-pointers §2.4 → CP v2.33 / runtime v2.44)**; (3) **the substantive catch** — U-CP-91's "no-new-field, pass-the-already-adjusted-value" GateLevelInput-lowering option is IMPOSSIBLE (`persona_tier`/`blast_radius_tier` are enum-mapped through fixed floor tables; no enum value maps to AUTO for the targeted cells) → **APPLIED** (U-CP-91 forecloses the impossible path; the carrier is now concretely an explicit override field OR override argument). **Decorrelation payoff (CLAUDE.md §13.1):** Codex caught the impossible-lowering-path (substantive) that the adversarial agent missed; the adversarial agent caught the cross-spec-drift docstring (F3-01) Codex did not.
  - advisor() — the planner's pre-done check (DAG/ACs/coverage/homing confirmed sound; the planner's own hygiene items fixed).
supersedes: design-substrate/Implementation_Plan_Control_Plane_v2_32.md
superseded_by:
---

# Clearance — `Implementation Plan: Control Plane v2.33`

v2.33 is the **CP-axis leg of R-FS-1 arc #20 (B3-plan)** — the atomic-unit decomposition of the cleared B3 (smart-HITL) spec legs (runtime spec §3.8 F-B3-1 + §14.8.9 F-B3-2) + the design §8.2 impl-against-cleared-spec gaps. **2 NEW CP units + 1 open-item:**

- **U-CP-91** — `GateLevelInput` floor-override carrier-shape (F-B3-1 plan-carrier / U-CP-43). The carrier is an EXPLICIT override field on `GateLevelInput` OR an override argument to `gate_level()` (the "pass-the-adjusted-enum-value" no-field path is foreclosed — Codex catch — because the persona/blast floors are enum-table-mapped). Plan-layer, NOT a CP-spec fork (F-B3-1 §3.2).
- **U-CP-92** — `TimeoutDegradationKind` vocab-B→vocab-A reconciliation (per CP §21.8 + ADR-D5 §1.6; multi→`fail-closed`, NOT abort-workflow) + the §21.6→§21.8 cite fix + the `fail-open`-refused-at-all-tiers config-guard + a `harness-*/src` residual-vocab-B sweep (F3-01 widened).
- **O-CP-3** (open-item, NOT a unit) — G2c `ToolContract.per_tool_gate_level` producer. The design §4.1 mis-framed it as pure-impl; AS C-AS-03 §3.1 declares no typed field → REGISTERED as owing a skipped AS-leg gate (impl-vs-fork classified there), per FULL-SPEC register-don't-drop + X-AL-3 don't-silently-impl-an-un-cleared-contract.

§3 is the aggregate cross-axis dependency-graph home; the B3 nodes are acyclic + topologically ordered (cross-axis edges U-RT-116→U-CP-91 + U-RT-119→U-CP-92, RT→CP downstream). **ZERO spec amendment; ZERO new contract ID;** delta-only (U-CP-01..90 preserved verbatim). Co-published with runtime plan v2.44.

## Notes
- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- Next: B3-impl-1 (U-CP-91 + U-RT-115/116/117 coupled cluster) → B3-impl-2 (U-CP-92 + U-RT-118/119) → B3-impl-3 (U-RT-120) per design §8.3.
- See `.harness/clearance/README.md` for marker discipline.
