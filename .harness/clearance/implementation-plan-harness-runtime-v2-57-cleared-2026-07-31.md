---
artifact: design-substrate/Implementation_Plan_Harness_Runtime_v2_57.md
version: v2.57
cleared_at: 2026-07-31T00:00:00-06:00
clearance_type: spec-writer-apply-pass
back_reference:
  - .harness/forward-register.yaml row `B-100`
  - design-substrate/Spec_Harness_Runtime_v1.md v1.109 §14.14.9.2 (the absorbed spec delta)
  - PR '#pending' (this arc)
merge_commit: pending
reviewer_chain:
  - implementation-planner revision-pass (absorbing Runtime spec v1.109 into ONE existing unit amendment)
  - empirical grounding pass at this leg (U-RT-148's AC #15(b) / #16(a) read against the widened rule to establish that the criteria would ACTIVELY REFUSE the two new shapes if left unamended)
  - out-of-family Codex review (`just codex-review-uncommitted`) to convergence
supersedes: implementation-plan-harness-runtime-v2-56-cleared-2026-07-31.md
---

# Clearance — `Implementation Plan: Harness Runtime v2.57`

v2.57 absorbs `Spec_Harness_Runtime_v1.md` v1.109 §14.14.9.2 into **ONE amended unit — U-RT-148**, the DTO-owning unit. Three sites are amended: the §1 scope statement's source-shape enumeration and counts (now TEN shapes across SEVEN carriers, `EffectFenceAddressable` spanning SIX, `step_kind` on five and absent from five), **AC #15(b)** and **AC #16(a)**. **SIXTEEN acceptance criteria remain SIXTEEN** — two are widened in scope, none added, removed, or renumbered; #1 – #14, #15(a) and #16(b) are PRESERVED VERBATIM. **ZERO new units, ZERO new cluster, ZERO DAG topology change.**

The amendment is load-bearing rather than bookkeeping: **AC #15(b)'s current symmetric clause would ACTIVELY REFUSE the two new shapes** (it requires that a normal branch/orchestrator source shape cannot be constructed without a key), so an impl leg building to the unamended unit would satisfy every criterion and still violate v1.109 §14.14.9.2. The widened #15(b) also adds the empty-string direction — a key-bearing shape must not accept `""` — which an absence-only assertion would pass while leaving the illegal state representable.

Caveats for Phase 7 consumers. AC #16(a)'s three cases carry **explicit witness-shape constraints**: the ORCHESTRATOR case MUST be a constructed-snapshot test (no production path exists — the authorizing register row's premise was checked and found false), the LINEAR case IS reachable and must not be downgraded to that posture, and the crash-reconstruction case re-runs the existing v2.55 witness unmodified. **OD / IS / AS and CXA are UNCHANGED, determined rather than assumed** — §14.14.9.5's trace-emission row still requires FOUR per-variant counts, so the OD-owned `§C-OD-30.5` schema is untouched.

## Notes

- **Register disposition at this leg:** `B-100` is **NARROWED to its IMPL remainder, NOT closed** — the forward-register status enum defines `closed` as *built + merged, or foreclosed/superseded*, and the two projection types plus their emptiness routing are unbuilt. Precedents: `B-97`(a) (open through the v1.108 spec leg at PR #1168, closed only at PR #1171 once U-RT-149 impl landed) and `B-102` (*narrowed to that remainder rather than closed*). The row's `summary` and its prose home at `.harness/post-phase-8-forward-register.md` are BOTH refreshed with the corrected grounds in the same commit, so following the row's heading back-pointer no longer yields contradictory guidance.
- **No fresh operator gate was owed, and the absence is a determination, not an omission** — the authorizing row's own `council` field routes this to a *spec-writer apply pass*; the underlying rule was ratified at the `B-69` arc (2026-07-30, OPTION A′) and is PRESERVED VERBATIM; and the `close_out` names disposition (b) *"NOT the default recommendation"*, leaving (a) as the row's own default. The two sub-decisions this leg did make are flagged at contract altitude so they can be overturned rather than discovered.

- **TWO channels this leg CANNOT close, REGISTERED as `B-106`** (a NEW id; `B-105` was minted and withdrawn at PR #1172). **Neither is closed by this arc, and the map one is NOT closed either.** *(1) The MAP channel* — removing the key field removes only the **advertisement**; `ResumeContext.effect_fence_resolutions` is a `dict[str, …]` with **unconstrained keys**, so a caller composing independently of the projection can still hand-build `{"": …}`, which `_resolve_effect_fence_gated` treats as a mapped resolution. *(2) The SCALAR channel* — `compute_effect_fence_uniform_fallback_eligible_key` (`workflow_driver.py:2935`–`:2970`) does not filter empty keys, so a key-absent location that is the sole unaddressed one becomes eligible for the caller's scalar `effect_fence_resolution`. The terminal loss reaches **all three carriers** (LINEAR threads a doomed directive; branch and orchestrator skip the consult behind their truthiness guard) and ends the same way in every case — a **silent INERT re-pause**. **Do NOT read this arc's criteria green as evidence that EITHER channel is closed**, and note that `B-106` closure requires a witness **per channel AND per carrier**.

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
