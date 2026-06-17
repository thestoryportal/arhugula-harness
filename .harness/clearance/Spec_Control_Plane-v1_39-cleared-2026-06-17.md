---
artifact: design-substrate/Spec_Control_Plane_v1_39.md
version: v1.39
cleared_at: 2026-06-17T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc (OPERATOR-GATED — the closed-at-5 StepKind §5.2 Class-2 revision)
back_reference:
  - .harness/class_1_fork_m_managed_agents_stepkind_c_rt_28.md
  - .harness/clearance/Spec_Harness_Runtime-v1_55-cleared-2026-06-17.md (the paired runtime C-RT-28 §14.20 consumer)
  - .harness/beyond-mvp-capability-boundary-ledger.md (arc M spine registration)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - advisor (pre-substantive, full-transcript) — affirmed Option B (new MANAGED_AGENTS kind); reversed a probe-resolves gate-dissolution (directed verification of §4.1.2 + the RunStatus.PAUSED landing, both of which fail the dissolve bar)
  - operator ratification via AskUserQuestion 2026-06-17 (the closed-at-5 StepKind extension gate → Option B)
  - standing FULL-SPEC operator directive 2026-06-12 (design back-flow pre-authorized; the closed-enum extension separately gated)
  - out-of-family Codex review at the impl-diff PR (decorrelated; deferred to Slice 2+ diff per the no-diff-yet fork-doc stage)
supersedes:
superseded_by:
---

# Clearance — `Spec_Control_Plane v1.39`

v1.39 is an additive delta over v1.38 absorbing the **R-FS-1 arc M** managed-agents production-wiring decision. It adds one member to the **§5.2 `step.kind` enum** (and its **§25.2 `StepKind` materialization**) — `managed-agents` / `MANAGED_AGENTS` — extending the taxonomy 5 → 6. This delta **is** the Workflow §4.1.2 Class-2 revision of §5.2 that the §25.2 closed-enum docstring ("Closed at cardinality 5 — extension is a Class-2 revision of §5.2") names. A `managed-agents` step's body is executed by a vendor-run Managed Agents session (the runtime C-RT-28 consumer, paired runtime v1.55 §14.20), distinct from the harness-orchestrated `sub-agent-dispatch`.

**OPERATOR-GATED + RATIFIED 2026-06-17** (AskUserQuestion → **Option B**: new `MANAGED_AGENTS` kind, not overload `SUB_AGENT_DISPATCH`). The closed-at-5 enum extension is the operator's ratified call (a meaningful change to the core dispatch enum); Option A (riding `SUB_AGENT_DISPATCH`) was probe-foreclosed because that dispatcher hard-requires harness-orchestration semantics (topology-admissibility gate + child-manifest recursion) a vendor session cannot honor — riding would sacrifice that committed C-RT-17/`SUB_AGENT_DISPATCH` semantic. FULL-SPEC pre-authorized the build + back-flow; the closed-enum extension itself is what the operator ratified.

Reviewed during clearance: Option B over Option A (driver is StepKind-agnostic — verified; the `SUB_AGENT_DISPATCH` dispatcher hard-requires topology-admissibility — verified; so ride is the more-invasive committed-semantic sacrifice, new-kind is purely additive); no §5.2 hash-recipe change (step.kind is an existing captured dimension; this adds a value, not a dimension); no new CXA edge (`managed_agents.*` namespace + ingestion already declared at AS §14.5 + OD `sampling_mode`); the gate discriminator (§4.1.2 is silent on operator-gating; the RunStatus.PAUSED "additive minor-version" carve-out covers a FIELD not the enum member — both fail the dissolve-the-gate bar).

## Notes

- Phase 7 consumers may rely on this version as canonical **only after** the paired runtime v1.55 C-RT-28 clearance + the bundled impl land together (`merge_commit` pinned at the post-merge refresh).
- See `.harness/clearance/README.md` for marker discipline.
