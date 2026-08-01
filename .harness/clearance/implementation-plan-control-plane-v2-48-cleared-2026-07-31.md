---
artifact: design-substrate/Implementation_Plan_Control_Plane_v2_48.md
version: v2.48
cleared_at: 2026-07-31T00:00:00-06:00
clearance_type: spec-writer-apply-pass
back_reference:
  - .harness/forward-register.yaml row `B-100`
  - design-substrate/Spec_Control_Plane_v1_113.md §1 (the absorbed spec delta)
  - PR '#pending' (this arc)
merge_commit: pending
reviewer_chain:
  - implementation-planner revision-pass (absorbing CP spec v1.113 into ONE existing unit amendment)
  - empirical grounding pass at this leg (the shipped projection's LINEAR / orchestrator construction sites read directly at HEAD to establish that an impl delta is genuinely owed)
  - out-of-family Codex review (`just codex-review-uncommitted`) to convergence
supersedes: implementation-plan-control-plane-v2-47-cleared-2026-07-30.md
---

# Clearance — `Implementation Plan: Control Plane v2.48`

v2.48 absorbs `Spec_Control_Plane_v1_113.md` §1 into **ONE amended unit — U-CP-64**, the owner of the §2 projection surface per v2.47 §0.3. **ONE acceptance criterion is ADDED (#A11)**; AC #A1 … #A10 are PRESERVED VERBATIM, including #A4, whose crash-reconstruction clause remains true as written and is now a special case of the general rule rather than the whole of it. **ZERO new units, ZERO new cluster, ZERO DAG topology change** — the U-RT-148 → U-CP-64 edge already exists (v2.47 §0.4), and no new crossing point, consumer, or edge is added.

AC #A11 requires the KEY-ABSENT sibling source shapes for **all three** effect-fence carriers, witnessed by **detect-then-refuse in both directions** (a key-absent shape cannot be constructed carrying a key; a key-bearing one cannot be constructed without one) — an absence-only assertion cannot distinguish a type invariant from a happens-to-be-`None`.

Caveats for Phase 7 consumers. The criterion carries **two witness-shape constraints stated deliberately**, so a later closeout does not read a correct test as an inadequate one: **(b)** the orchestrator case MUST be a constructed-snapshot test, because that carrier's sole capture site guards on a truthy key and **no production path can produce the state** (the authorizing register row asserted otherwise; the premise was checked and found false); **(a)** the LINEAR case IS reachable and must not be downgraded to that posture. No deferred coverage-matrix row is added, on v2.47 §2's own reasoning. CXA v2.23 UNCHANGED, aggregate frozen at 111.

## Notes

- **Register disposition at this leg:** `B-100` is **NARROWED to its IMPL remainder, NOT closed** — the forward-register status enum defines `closed` as *built + merged, or foreclosed/superseded*, and the two projection types plus their emptiness routing are unbuilt. Precedents: `B-97`(a) (open through the v1.108 spec leg at PR #1168, closed only at PR #1171 once U-RT-149 impl landed) and `B-102` (*narrowed to that remainder rather than closed*). The row's `summary` and its prose home at `.harness/post-phase-8-forward-register.md` are BOTH refreshed with the corrected grounds in the same commit, so following the row's heading back-pointer no longer yields contradictory guidance.
- **No fresh operator gate was owed, and the absence is a determination, not an omission** — the authorizing row's own `council` field routes this to a *spec-writer apply pass*; the underlying rule was ratified at the `B-69` arc (2026-07-30, OPTION A′) and is PRESERVED VERBATIM; and the `close_out` names disposition (b) *"NOT the default recommendation"*, leaving (a) as the row's own default. The two sub-decisions this leg did make are flagged at contract altitude so they can be overturned rather than discovered.

- **TWO channels this leg CANNOT close, REGISTERED as `B-106`** (a NEW id; `B-105` was minted and withdrawn at PR #1172). **Neither is closed by this arc, and the map one is NOT closed either.** *(1) The MAP channel* — removing the key field removes only the **advertisement**; `ResumeContext.effect_fence_resolutions` is a `dict[str, …]` with **unconstrained keys**, so a caller composing independently of the projection can still hand-build `{"": …}`, which `_resolve_effect_fence_gated` treats as a mapped resolution. *(2) The SCALAR channel* — `compute_effect_fence_uniform_fallback_eligible_key` (`workflow_driver.py:2935`–`:2970`) does not filter empty keys, so a key-absent location that is the sole unaddressed one becomes eligible for the caller's scalar `effect_fence_resolution`. The terminal loss reaches **all three carriers** (LINEAR threads a doomed directive; branch and orchestrator skip the consult behind their truthiness guard) and ends the same way in every case — a **silent INERT re-pause**. **Do NOT read this arc's criteria green as evidence that EITHER channel is closed**, and note that `B-106` closure requires a witness **per channel AND per carrier**.

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
