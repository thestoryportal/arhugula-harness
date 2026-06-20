---
artifact: design-substrate/Spec_Control_Plane_v1_43.md
version: v1.43
cleared_at: 2026-06-19T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc (NO operator gate — a single in-place §2.5.3 amendment materializing the C-CP-03 §3.1 per-workload-class × per-persona-tier tuning surface, which §3.1 commits explicitly on `llm_as_router`; behavior-preserving by default — no override ⇒ byte-identical 200 ms)
back_reference:
  - .harness/class_2_fork_b_layer_budget_override_l3_effective_budget.md
  - .harness/beyond-mvp-capability-boundary-ledger.md (B-LAYER-BUDGET-OVERRIDE spine BUILT note)
  - design-substrate/Spec_Control_Plane_v1_2.md (C-CP-03 §3.1 — the cleared override-tuning surface, naming `llm_as_router` explicitly; PRESERVED VERBATIM, materialized here)
  - design-substrate/Spec_Control_Plane_v1_36.md (C-CP-02 §2.5.3 — the v1.36 flat-field gloss this delta amends to the §3.1 effective budget)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - advisor (full-transcript) — confirmed the X-AL-3 reversal is sound; steered to lead with §3.1's affirmative on-`llm_as_router` commitment (and drop the shaky "effective"-reading of §2.5.3), to frame the §2.5.3 edit as a real small amendment + version bump (not "doc-hygiene"), to verify the no-gate discriminator via a ledger grep for a ratified "flat-only at L3" (none found), and flagged the non-vacuity overclaim trap (witness at infer(); dispatcher seam dormant/activation-gated; never "fires in production")
  - standing FULL-SPEC operator directive 2026-06-12 (design back-flow pre-authorized; no operator gate owed)
  - out-of-family Codex review at the impl-diff PR (decorrelated; pending)
supersedes:
superseded_by:
---

# Clearance — `Spec_Control_Plane v1.43`

v1.43 is a single in-place amendment over v1.42 absorbing the **R-FS-1 standalone arc `B-LAYER-BUDGET-OVERRIDE`**. It amends **C-CP-02 §2.5.3** so the Layer-3 router timeout is bounded by the **§3.1 OVERRIDE-RESOLVED** effective `LayerBudget` (keyed on the request's `workload_class` + `persona_tier`) rather than the flat `time_budget_ms`; the flat 200 ms is the default when no override applies. C-CP-03 §3.1 itself is unchanged — it already commits the override surface this arc materializes.

**NO operator gate.** The load-bearing evidence is C-CP-03 §3.1 (cleared at v1.2, PRESERVED VERBATIM through the head): it affirmatively commits the per-layer time-budget as per-workload-class operator-tunable with the tuning surface "per layer × per workload class × per persona tier" and names the router layer explicitly — *"the higher-tier persona caps budget tighter on `llm_as_router`."* The override carrier (`LayerBudget.per_workload_override` / `per_persona_override` + `effective_budget`, U-CP-06) was already built but **vacuous** (zero production callers); honoring it at the L3 timeout MATERIALIZES that cleared surface — impl-to-cleared-spec, not a design extension. No committed invariant is sacrificed: §3.1 affirmatively commits the override, so this fulfils a cleared contract (contrast B4-Slice-4's runtime §14.5.3 inv-2 *role* relaxation, which gated because the invariant explicitly forbade per-step role). No ratified "flat-only at L3" decision exists in the fork/clearance ledger (the v1.36 clearance shows §2.5.3 was about making the timeout *enforceable* — the Codex round-1 [P2]; override-honoring was registered "build later," not "decided never"). Adopt-and-note + clearance under the FULL-SPEC directive.

Reviewed during clearance: the §2.5.3 amendment preserves the v1.36 "Timeout = exhaustion" requirement (the router await stays timeout-bounded; only the budget VALUE narrows from flat to §3.1-effective); the threading prerequisite is present (`InferenceRequest` carries `workload_class` + `persona_tier`, C-CP-01 §1.1); behavior-preserving by default (no override ⇒ byte-identical 200 ms); the non-vacuity scoping is honest — capability-built, **production-dormant** (production binds `router=None` + the DEFAULT budgets, so L3 is inert and no override surface is wired), the live path additionally gated by the UNOWNED routing-activation gate; the dormant `RuntimeLLMDispatcher.budgets` construction seam defaults to `DEFAULT_LAYER_BUDGETS`; scope is the L3 timeout site only (deterministic-layer wall-clock enforcement + the 200 ms recalibration are separate concerns, not in scope).

## Notes

- Phase 7 consumers may rely on this version as canonical after the bundled harness-cp + harness-runtime impl + tests land together (`merge_commit` pinned at the post-merge refresh).
