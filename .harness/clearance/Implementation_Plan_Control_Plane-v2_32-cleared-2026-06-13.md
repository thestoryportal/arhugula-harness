---
artifact: design-substrate/Implementation_Plan_Control_Plane_v2_32.md
version: v2.32
cleared_at: 2026-06-13T19:30:00-06:00
clearance_type: Phase-7-absorbed-via-plan-decomposition (R-FS-1 arc #6 / B1-plan — the CP-axis leg; decomposition of the cleared CP spec v1.32 §25.10–§25.18 into 11 atomic units + the B1-arc aggregate cross-axis dependency-graph home)
back_reference:
  - design-substrate/Spec_Control_Plane_v1_32.md §25.10–§25.18 (the cleared contract this plan decomposes; cleared at `.harness/clearance/Spec_Control_Plane-v1_32-cleared-2026-06-13.md`, PR #529)
  - design-substrate/Implementation_Plan_Harness_Runtime_v2_43.md + design-substrate/Implementation_Plan_Information_Substrate_v2_6.md (sibling co-publications — the runtime + IS legs of the same B1-plan arc)
  - .harness/r-fs-1-b1-topology-orchestration-design-v1.md §8 (the B1-plan cascade row)
  - .harness/adversarial-review-r-fs-1-arc-6-b1-plan.md (the genuine-agent pre-merge review)
  - .claude/skills/implementation-planner/SKILL.md + references/implementation-plan-template.md (the role discipline applied)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - advisor() pre-substantive decision-fork (transcript-aware; produced the load-bearing SCOPING: (1) COVERAGE-MATRIX-FIRST as the done-bar — surfaced the two would-be-silent-gaps §25.17 [cite from U-CP-80 + U-CP-85, no own unit] + runtime §2.2a [no-change → §6 Open-item, NOT a unit]; (2) §2.2c write-cadence = a tri-spec CROSS-CUTTING integration unit [U-CP-84, CP §25.13 + IS §5.4 + runtime §2.2c]; (3) SPLIT branch-context from buffered-drain so idempotency/role units don't false-depend on the drain; (4) HIERARCHICAL_DELEGATION `Depends on ORCHESTRATOR_WORKERS` [recursive, per §25.11]; (5) assert IS-0-outbound as the cycle guard; (6) U-IS-19 carrier-home stays impl-discretion; (7) cascade obl-5 composes already-landed C-AS-02→C-CP-19→C-CP-16, cite-don't-edge; done-bar = coverage-complete + signatures-transcribed-not-redesigned)
  - harness-adversarial-reviewer Phase-7 pre-merge review (dedicated-agent invocation per [[feedback-genuine-skill-invocation-dedicated-agent]], 25 tool-uses; full report at `.harness/adversarial-review-r-fs-1-arc-6-b1-plan.md`) — VERDICT **APPROVE-WITH-CLASS-3** (0 Class-1 blocking / 0 Class-2 / 1 Class-3). Verified by direct read: COVERAGE (every CP §25.10–18 / runtime §2.2(a–d)/§9/§14.5.3 / IS §5.4 row maps to a unit or explicit disposition — no silent gap); NO-SPEC-EXTENSION (U-IS-19 `BranchMetadata {parent_action_id, branch_index, terminal_status: Literal[...]|None}` verbatim vs IS §5.4 lines 481–487; U-RT-113 `Literal['completed','drained','failed','paused','partial']` verbatim vs runtime §9 line 2450; code symbols `_CP_TO_RT_STATUS`/`_MVP_DEFAULT_AGENT_ROLE`/`_IN_SCOPE_TOPOLOGY` real at HEAD); DAG (all 14 edges walked vs §3.2 order — every edge to a strictly-lower unit, cross-axis downstream CP→IS + RT→CP, IS-0-outbound intact, acyclic); ATOMICITY (U-CP-81 defensibly one context-shape change); byte-exact cites; delta integrity (version bumps correct, preserved-verbatim sets declared); zero forbidden risk/estimate/PR-granularity annotations. The 1 Class-3 (F3-01: CLAUDE.md §2.3 CP spec-head stale `v1_30` vs cleared `v1.32`) is **pre-existing #529 spec-PR debt, out-of-scope for this plan PR** — noted for the Q1 doc-hygiene sweep (fixing only CP risks a partial §2.3 audit). NOTE: the agent erroneously reported "all three clearance markers present" — Codex (decorrelated) correctly caught them ABSENT; this marker + siblings discharge that.
  - out-of-family Codex review (`just codex-review-uncommitted`, decorrelated) — 2 [P2], BOTH addressed: (1) the `.harness/claude-artifact-pointers.md` §2.4 lineage index still pointed at v2.5/v2.31/v2.42 while CLAUDE.md §2.4 was bumped → FIXED (all 3 pointer rows updated); (2) the plan files' §0.5 claimed clearance markers "filed" but none existed → FIXED (this marker + the IS/runtime siblings filed, making the claim true at merge). **Decorrelation payoff (CLAUDE.md §13.1):** Codex caught the absent markers the adversarial agent missed (claimed present); the adversarial agent did the deep decomposition verification (coverage/DAG/transcription) Codex did not. Neither flagged a decomposition defect — the decomposition is sound.
  - empirical code-grounding (verify-by-execution: the CP spec v1.32 §25.10–§25.18 contracts + the IS §5.4 carrier + the runtime §9/§14.5.3 surfaces all read at HEAD; the new unit IDs start above the existing maxima U-CP-79/U-RT-112/U-IS-18; no code lands — impl is B1-impl-N)
  - design-phase bundled-absorption posture (workspace CLAUDE.md §11.4; X-AL-3 guard satisfied by this clearance marker + the adversarial review `.md` as the `.harness/` back-flow companions to the `design-substrate/**` + CLAUDE.md edits)
supersedes: design-substrate/Implementation_Plan_Control_Plane_v2_31.md v2.31
superseded_by:
---

# Clearance — `Implementation_Plan_Control_Plane v2.32`

v2.32 is the **CP-axis leg of R-FS-1 arc #6 (B1-plan)** — the atomic-unit decomposition of the cleared **CP spec v1.32 §25.10–§25.18** (the C-CP-25 WorkflowDriver non-linear-topology extension) into **11 NEW units (U-CP-80..U-CP-90)**, and the **aggregate cross-axis dependency-graph home** for the B1 arc (14 nodes across CP + runtime + IS). Design-substrate (plan-layer); **no code lands** (impl is B1-impl-N).

**What changed (the 11 units).** U-CP-80 driver-strategy dispatch table (§25.10); U-CP-81 branch `StepExecutionContext` composition — causality fields + `AgentRole` field (§25.11/§25.12/§25.14); U-CP-82 buffered/deferred-append drain + bounded barriers + determinism (§25.11/§25.12); U-CP-83 branch-scoped idempotency-key (§25.16); U-CP-84 `branch_metadata.terminal_status` write-cadence (tri-spec cross-cutting: CP §25.13 + IS §5.4 + runtime §2.2c); U-CP-85 `cascade_policy` + cascade-cancel, 8 §25.15.2 obligations (§25.15); U-CP-86..90 the 5 strategies (PARALLELIZATION → EVALUATOR_OPTIMIZER → ORCHESTRATOR_WORKERS → HIERARCHICAL_DELEGATION → DECENTRALIZED_HANDOFF, impl-order simplest→hardest per design §8).

**Coverage + dispositions.** Every CP §25.10–§25.17 subsection is covered; §25.18 (deferred-to-impl + already-resolved forks) → §6 Open-items O-CP-1/2 (not units); §25.17 (failure-mode taxonomy) cited by U-CP-80 + U-CP-85 (no own unit); runtime §2.2(b/c/d) covered CP-side at U-CP-82/84/81 (the CP-driver-internal code home). The aggregate B1 DAG (§3) is acyclic with the IS-0-outbound cycle guard.

**Carve-outs.** All implementation lands at B1-impl-N; §25.18 deferred-to-impl items (TaskGroup nesting, cascade_policy recursion propagation, fan-out caps, DriverStrategy shape) stay implementer-discretion (O-CP-1). ZERO spec amendment, ZERO new contract ID.

## Notes
- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- Coordinated next arc: **B1-impl-N** (implement per strategy simplest→hardest, each with a deterministic-append regression + persisted-branch-causality assertion + cascade-cancel idempotency test + live e2e per CP §25.18).
- See `.harness/clearance/README.md` for marker discipline.
