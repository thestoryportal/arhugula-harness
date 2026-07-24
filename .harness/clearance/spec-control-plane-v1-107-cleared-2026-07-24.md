---
artifact: design-substrate/Spec_Control_Plane_v1_107.md
version: v1.107
cleared_at: 2026-07-24T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_2_fork_b70_effect_fence_resolution_uniform_fallback.md (filed 2026-07-24; operator ratified "open the spec-leg now" via AskUserQuestion the same day)
  - .harness/forward-register.yaml B-70 row
merge_commit: pending (direct-to-main commit at authoring time)
reviewer_chain:
  - operator AskUserQuestion ratification (2026-07-24) — "open the spec-leg now" vs. "hold registered with dormant siblings"
  - out-of-family codex review, 5 rounds to convergence (round 1 — carrier enumeration omitted the ORCHESTRATOR consume site; round 2 — the safety rule was a no-op for the LINEAR consume site, which never calls `effect_fence_resolution_for`; round 3 — round 2's own fix would permanently livelock any 2+-simultaneous-LINEAR-pause resume, corrected to genuine map-addressability via the already-existing `idempotency_key` field; round 4 — added the `resume_handle` scope-limit note mirroring `B-69`; round 5 — round 4's `B-69` citation was aspirational, fixed by widening `B-69`'s own row)
supersedes: null
---

# Clearance — `Spec_Control_Plane_v1_107` (B-70 spec leg)

Closes the registered finding `B-70`: v1.106 §1.2 property 4 fixed a uniform-fallback safety gap for the NEW `ResumeContext.hitl_responses`/`hitl_response_for` mechanism (the B-39 arc) but explicitly declined to extend the fix to the sibling, already-shipped `effect_fence_resolution_for`/`effect_fence_resolutions` mechanism (C-CP-26 §26.8.1, built at `Spec_Control_Plane_v1_66.md`), registering the identical gap as `B-70`. This delta adds ONE new CONTRACT property (§1) mirroring property 4's safety+liveness shape — but simpler, since grounding (§2 of this spec delta, and the fork doc) confirms `effect_fence_resolution_for` needs no property-5-equivalent gate-owning/container split: every carrier entry is inherently gate-owning by construction (`EffectFencePausedBranchResumeState`'s own "always tool-step in production" docstring + v1.106 §2 REMOVED's own text that the effect-fence mechanism "does not cross a recursion boundary the way HITL child-pause delivery does").

NO field, method signature, or enum is added or changed. The property constrains a resolver that does not yet exist — deferred to the impl leg (CP plan v2.43 §5's coverage-matrix row), mirroring exactly how v1.106 §1.2 property 4 was deferred rather than assigned to a then-existing unit. Impl leg (code + tests) is a separate follow-on arc per the B-33/B-39/B-59 spec-leg-first precedent — not built by this clearance.

Reviewed at authoring time: the grounding claims in the fork doc (`.harness/class_2_fork_b70_effect_fence_resolution_uniform_fallback.md`) were independently re-verified against `EffectFencePausedBranchResumeState`'s docstring and `Spec_Control_Plane_v1_106.md` §2 (REMOVED) by direct read before this delta was authored, not merely carried forward from the fork's own claims.

## Notes

- Phase 7 consumers may rely on `Spec_Control_Plane_v1_107.md` as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
