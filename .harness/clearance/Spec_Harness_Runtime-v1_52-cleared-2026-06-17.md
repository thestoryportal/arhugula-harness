---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.52
cleared_at: 2026-06-17T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc (OPERATOR-RATIFIED 2026-06-17 — committed-invariant relaxation; AskUserQuestion "Ratify full")
back_reference:
  - .harness/class_1_fork_b4_per_step_role_override_stepoverride_extension.md
  - .harness/beyond-mvp-capability-boundary-ledger.md (B4 Slice 4 spine registration)
  - .harness/clearance/Spec_Control_Plane-v1_38-cleared-2026-06-17.md (the paired additive CP carrier)
merge_commit: <pending — co-published bundled-absorption PR; merge blocked on operator ratification of the §14.5.3 relaxation>
reviewer_chain:
  - advisor (pre-substantive, full-transcript) — confirmed Option B; caught + reversed the probe-resolves attempt to dissolve the gate (the decisive asymmetry: default_gate_level had no invariant forbidding it; role has the explicit §14.5.3 invariant 2)
  - out-of-family Codex review at PR (decorrelated diff review)
  - operator ratification via AskUserQuestion (the §14.5.3 invariant-2/3 relaxation gate) — THIS is the gated clearance event
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.52` (OPERATOR-GATED)

v1.52 **relaxes two committed §14.5.3 invariants** to admit the **R-FS-1 arc B4 Slice 4** per-step role override + linear-path role indexing:

- **Invariant 2 "Single role source"** → relaxed to "single *dispatch-read* role source": a `StepOverride.agent_role` carrier (CP v1.38) is admitted as a **composition-time input** to the one `step_context.agent_role` source; the runtime **dispatch read is byte-unchanged** (Option B — no two-authority-at-dispatch).
- **Invariant 3 "Linear path untouched"** → conditional: the linear (+ evaluator-optimizer) path carries a role **only** when a per-step override is present.
- **Invariant 1 "Non-breaking default"** → PRESERVED VERBATIM (absent override ⟹ byte-identical to v1.51).

**This is a committed-invariant relaxation → it carried a genuine operator ratification gate** (`CLAUDE.md` `[[feedback-gate-only-on-meaningful-architecture-change]]`). FULL-SPEC pre-authorizes the build + back-flow, NOT silently relaxing a committed invariant — the roadmap reconciled this (build it, ratify the relaxation). **OPERATOR RATIFIED 2026-06-17** (AskUserQuestion "Ratify full" — relax invariant-2 + invariant-3, per-step role on all topologies incl. linear-path indexing). The v1.52 amendment, CP v1.38, and the impl land together; `merge_commit` pinned at the post-merge refresh.

The **runtime dispatch path is UNCHANGED** (Option B) — the entire per-step-role mechanism is the CP driver fold (CP v1.38 §6.2). No new C-RT-NN, no new fail class, no IS-spec change, no ADR change. Reviewed during clearance: Option B over Option A (composition-time fold preserves the single dispatch-read source); the probe-resolves framing error (advisor-reversed: the relaxation is genuine, not a clarification); the verification (CP by-execution tests + the existing Slice-2 dispatch e2e proving `step_context.agent_role → distinct model+prompt`, the unchanged seam the fold feeds).

## Notes

- Phase 7 consumers may rely on this version as canonical **only after** operator ratification + merge.
- See `.harness/clearance/README.md` for marker discipline.
