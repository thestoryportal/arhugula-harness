---
artifact: design-substrate/Spec_Control_Plane_v1_113.md
version: v1.113
cleared_at: 2026-07-31T00:00:00-06:00
clearance_type: spec-writer-apply-pass
back_reference:
  - .harness/forward-register.yaml row `B-100` (the filed finding; `close_out` pre-selects disposition (a))
  - PR #1166 (the `B-69` impl leg, where `B-100` was surfaced and REPORTED not absorbed)
  - PR '#pending' (this arc)
merge_commit: pending
reviewer_chain:
  - spec-writer apply pass — applies the PRE-SELECTED disposition (a) and EXTENDS NOTHING beyond it. It is
    NOT decision-free, and the two determinations it did make are recorded at contract altitude rather than
    buried, so a reviewer can overturn them: (1) the orchestrator KEY-ABSENT shape is retained on a NEW
    TYPE-TOTALITY ground after the authorizing row's premise was empirically falsified; (2) a pre-existing
    §2.1 table/count gap is refreshed here rather than filed separately. Neither reverses a committed surface,
    neither is irreversible, and no fresh operator gate was owed — the authorizing row's own `council` field
    routes this to a spec-writer apply pass, and the underlying rule was ratified at the `B-69` arc
    (2026-07-30, OPTION A′) and is PRESERVED VERBATIM. Rationale at `Spec_Control_Plane_v1_113.md` §0.4a.
  - empirical grounding pass at this leg (all three effect-fence carriers, their capture sites, both resume consult sites, the runtime dispatcher key-match, and the shipped projection read directly at HEAD)
  - out-of-family Codex review (`just codex-review-uncommitted`) to convergence
supersedes: spec-control-plane-v1-112-cleared-2026-07-30.md
---

# Clearance — `Spec Control Plane v1.113`

v1.113 is a delta-only file carrying **ONE amendment site**: `Spec_Control_Plane_v1_112.md` §2.1's empty-`idempotency_key` key-ABSENT treatment is generalized from a **PROVENANCE** scope (*"the crash-reconstruction carrier"*) to a **STATE** scope (**any effect-fence source shape whose captured key is EMPTY**), adding a KEY-ABSENT sibling SOURCE SHAPE for the LINEAR `EffectFenceResumeState` and for `OrchestratorEffectFencePausedResumeState`. **The VARIANT set is UNCHANGED at FOUR; only the SOURCE column widens** — `effect-fence-addressable` 4 → 6 shapes, the union 8 → 10, across an UNCHANGED SEVEN distinct source carriers. No contract number is minted, no carrier is retyped, no field is added, no classification rule is added, and `snapshot_hash` is untouched: the delta is entirely READ-SIDE.

Reviewed at clearance: that the sub-discriminator rule accommodates the two new shapes with no new machinery (it keys on the source SHAPE, a projection-stamped tag, not on any carrier field — checked before applying); that disposition **(b)** (capture-side refusal) is NOT applied, per the register row's own declination; and that CXA v2.23 is UNCHANGED, aggregate frozen at 111, determined rather than assumed.

Caveats for Phase 7 consumers. **Six findings are surfaced rather than absorbed**, recorded at §0.4: **(i)** the authorizing row's ground for the ORCHESTRATOR half is **FALSIFIED at HEAD** — that carrier's sole capture site *does* carry a truthiness guard — so the disposition is applied on a corrected ground (TYPE TOTALITY over journaled records), and its shape is **unreachable in production**, making a constructed-snapshot test the only buildable witness; **(ii)** the row's mechanism claim is accurate for the fan-out per-branch sites **and for the ORCHESTRATOR consult** (`workflow_driver.py:12118`, truthiness-gated the same way) and inaccurate for the **LINEAR consult ALONE** (`:4925`–`:4936`), which is unconditional — the spec text states that accurate mechanism, and this leg's own round-1 over-generalization of it was narrowed at round 2 and recorded; **(iii)** the branch key-absent shape was already under-scoped by its provenance naming (the ordinary fan-out path defensively coerces a missing key to `""`); **(iv)** a pre-existing §2.1 table/count gap, caused by a shape-vs-carrier conflation, is refreshed here; **(v)** the IMPL delta owed; **(vi)** the SCALAR uniform-fallback channel this delta cannot close, registered as `B-106`. **The IMPL delta IS owed and is NOT this leg** — owning units U-CP-64 (`Implementation_Plan_Control_Plane_v2_48.md`) and U-RT-148 (`Implementation_Plan_Harness_Runtime_v2_57.md`).

## Notes

- **Register disposition at this leg:** `B-100` is **NARROWED to its IMPL remainder, NOT closed** — the forward-register status enum defines `closed` as *built + merged, or foreclosed/superseded*, and the two projection types plus their emptiness routing are unbuilt. Precedents: `B-97`(a) (open through the v1.108 spec leg at PR #1168, closed only at PR #1171 once U-RT-149 impl landed) and `B-102` (*narrowed to that remainder rather than closed*). The row's `summary` and its prose home at `.harness/post-phase-8-forward-register.md` are BOTH refreshed with the corrected grounds in the same commit, so following the row's heading back-pointer no longer yields contradictory guidance.
- **No fresh operator gate was owed, and the absence is a determination, not an omission** — the authorizing row's own `council` field routes this to a *spec-writer apply pass*; the underlying rule was ratified at the `B-69` arc (2026-07-30, OPTION A′) and is PRESERVED VERBATIM; and the `close_out` names disposition (b) *"NOT the default recommendation"*, leaving (a) as the row's own default. The two sub-decisions this leg did make are flagged at contract altitude so they can be overturned rather than discovered.

- **TWO channels this leg CANNOT close, REGISTERED as `B-106`** (a NEW id; `B-105` was minted and withdrawn at PR #1172). **Neither is closed by this arc, and the map one is NOT closed either.** *(1) The MAP channel* — removing the key field removes only the **advertisement**; `ResumeContext.effect_fence_resolutions` is a `dict[str, …]` with **unconstrained keys**, so a caller composing independently of the projection can still hand-build `{"": …}`, which `_resolve_effect_fence_gated` treats as a mapped resolution. *(2) The SCALAR channel* — `compute_effect_fence_uniform_fallback_eligible_key` (`workflow_driver.py:2935`–`:2970`) does not filter empty keys, so a key-absent location that is the sole unaddressed one becomes eligible for the caller's scalar `effect_fence_resolution`. The terminal loss reaches **all three carriers** (LINEAR threads a doomed directive; branch and orchestrator skip the consult behind their truthiness guard) and ends the same way in every case — a **silent INERT re-pause**. **Do NOT read this arc's criteria green as evidence that EITHER channel is closed**, and note that `B-106` closure requires a witness **per channel AND per carrier**.

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
