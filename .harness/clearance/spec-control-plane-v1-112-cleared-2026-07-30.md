---
artifact: design-substrate/Spec_Control_Plane_v1_112.md
version: v1.112
cleared_at: 2026-07-30T00:00:00-04:00
clearance_type: spec-writer-apply-pass
back_reference:
  - .harness/council-b69-pause-state-accessor-2026-07-30.md
  - .harness/council-b69-pause-state-accessor-2026-07-30.md §14 (ratification addendum — operator AskUserQuestion 2026-07-30, OPTION A′)
  - .harness/forward-register.yaml row B-69
merge_commit: <pending — this PR>
reviewer_chain:
  - council voices C10 + C11 + C9 — genuine dedicated agent invocations, reconciled to zero twice (20 positions withdrawn, replaced or corrected)
  - harness-adversarial-reviewer in-family pass on the council record
  - out-of-family `just codex-review-uncommitted` (GPT-5.6) on the council record and on the applied delta
  - operator AskUserQuestion ratification 2026-07-30 — OPTION A′ (CO-REQUISITE, SEQUENCED), which explicitly covered the §8.2 sizing correction making this a THIRD spec surface
  - spec-writer apply pass (this arc)
---

# Clearance — `Spec_Control_Plane_v1_112.md`

v1.112 is the CP-owned leg of the RATIFIED **B-69 durable-pause-state read accessor arc**, carrying three sections. **§1 — the REQUIRED `ResumeContext` response-provenance carrier**: a closed two-variant discrimination (accessor-derived, carrying the staleness token **non-optionally**; legacy, carrying none and semantically byte-identical to today), with the legacy variant **not constructible from** an accessor-derived one. **§2 — the NEW public projection-returning surface** over the two private resume-tree walks, publishing the authoritative **four**-variant location classification plus tree position, spanning seven-plus source shapes (a draft added a fifth variant for the empty-`idempotency_key` crash-reconstruction carrier; round 11 [P1] showed it would break one-authority, so it is a SOURCE SHAPE with the key field ABSENT instead), with bare identifier sets forbidden as the return shape and the never-keyable pre-dispatch internal identity **absent, not opaque**. **§3 — two registered scope-limit lifts**: `Spec_Control_Plane_v1_106.md` §3's follow-on (a), and `Spec_Control_Plane_v1_107.md` §1.1's round-4 `resume_handle` note — each lifted conditionally and precisely, with the delta stating **where the lifted notes live** so the lifts resolve byte-exact against the delta chain.

**The CP-homed-vs-Runtime-only carrier decision, recorded.** The council carried this as a `[MODERATE]` residual (its §8.2 sizing correction). It is resolved **CP-homed** here, on the grounding that the responses the token binds — `hitl_responses`, `effect_fence_resolutions` — are CP-owned `ResumeContext` fields, so a Runtime-side parallel carrier would leave *"these responses came from **this** read"* untyped and would create a second authority over that fact. The operator's A′ ratification explicitly covered the resulting three-spec-surface sizing.

**What is PRESERVED VERBATIM.** The v1.111 body and the entire C-CP-01 … C-CP-29 contract body; every existing `ResumeContext` field and both resolver methods; §1.2 properties 1–5 and §1.1 properties 6–8 (§2 publishes their classification and defines none of it); `attempt_resume`'s signature, unchanged since v1.16 §26.8.5. The delta is ADDITIVE only — zero field removed, retyped, reordered or narrowed; zero enum member added.

**Caveats for Phase 7 consumers.** Spec + impl do NOT land together — the impl arc follows (CP plan v2.47's U-CP-64 amendment). §3's lifts are **conditional**: the `resume_handle` addressing limitation lifts only for a caller who **takes the read**, only **in conjunction with** the Runtime-side staleness precondition, and only for **ADDRESSING** — §1.1(a)'s 2+-member INERT re-pause safety rule is preserved verbatim and is not relaxed. Three findings are surfaced but **NOT patched**: the journal-vs-HITL-queue posture divergence (with the binding constraint that §2's projection must not be shaped to imply they are the same object); gate-description absence from every durable pause carrier; the pause journal's absent tenant binding (pre-existing, not CP-owned).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
