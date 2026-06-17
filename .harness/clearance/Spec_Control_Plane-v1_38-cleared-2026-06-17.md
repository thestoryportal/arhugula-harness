---
artifact: design-substrate/Spec_Control_Plane_v1_38.md
version: v1.38
cleared_at: 2026-06-17T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc (OPERATOR-GATED — paired with runtime v1.52 §14.5.3 relaxation)
back_reference:
  - .harness/class_1_fork_b4_per_step_role_override_stepoverride_extension.md
  - .harness/beyond-mvp-capability-boundary-ledger.md (B4 Slice 4 spine registration)
  - .harness/clearance/Spec_Harness_Runtime-v1_52-cleared-2026-06-17.md (the paired runtime relaxation — the gated half)
merge_commit: <pending — co-published bundled-absorption PR; merge blocked on operator ratification of the §14.5.3 relaxation>
reviewer_chain:
  - advisor (pre-substantive, full-transcript) — confirmed Option B (composition-time fold); caught the probe-resolves framing error (do not dissolve the gate); confirmed provenance scope + fan-out granularity + council-not-warranted
  - out-of-family Codex review at PR (decorrelated diff review)
  - operator ratification via AskUserQuestion (the §14.5.3 invariant-2/3 relaxation gate) — the gated half (runtime v1.52)
  - standing FULL-SPEC operator directive 2026-06-12 (design back-flow pre-authorized; the invariant relaxation is separately gated)
supersedes:
superseded_by:
---

# Clearance — `Spec_Control_Plane v1.38`

v1.38 is an additive delta over v1.37 absorbing the **R-FS-1 arc B4 Slice 4** per-step role override. It adds one optional field — `StepOverride.agent_role: AgentRole | None = None` (C-CP-06 §6.1, reusing the committed `AgentRole` shared type) — propagates it through `StepEffectiveBinding` + `resolve_step_binding` (§6.2), and extends §6.6 to cover the role dimension of the per-step override's **provenance scope** (the wired per-step override state-ledger entry, NOT the run-level C-IS-05 §5.2 hash). Governed by the v1.27 §2(d) X-AL-3 explicit-extension discipline (mirror precedents v1.20/v1.22/v1.34/v1.37).

**The CP-side field add is additive (no operator gate); the committed-invariant relaxation lives in the paired runtime v1.52 §14.5.3 amendment and IS operator-gated.** The CP driver folds `binding.agent_role` onto the single `StepExecutionContext.agent_role` source at composition (Option B; precedence per-step > fan-out-derived > default), so the runtime dispatch read is unchanged. This marker becomes effective ON operator ratification of the §14.5.3 relaxation (the AUQ gate) + merge; the PR does not merge without ratification — this marker, the CP v1.38 delta, the runtime v1.52 amendment, and the impl land together or not at all.

Reviewed during clearance: Option B over Option A (composition-time fold preserves the single dispatch-read role source — no two-authority-at-dispatch); the scope (per-step role + linear-path role indexing, both facets of the one §14.5.3 relaxation, bundled into one gate, not split); the provenance scope (per-step override ledger entry, following the per-step MODEL/PROMPT override precedent).

## Notes

- Phase 7 consumers may rely on this version as canonical **only after** the paired runtime v1.52 clearance is operator-ratified + merged.
- See `.harness/clearance/README.md` for marker discipline.
