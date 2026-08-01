---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.109
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
supersedes: spec-harness-runtime-v1-108-cleared-2026-07-31.md
---

# Clearance — `Spec Harness Runtime v1.109`

v1.109 carries **ONE amendment site, entirely inside §14.14.9.2**: the key-ABSENT treatment is generalized from a **PROVENANCE** scope to a **STATE** scope (**any effect-fence source shape whose captured key is EMPTY**), adding a KEY-ABSENT sibling SOURCE SHAPE for the LINEAR and orchestrator carriers, exactly parallel to the CP-owned publication at `Spec_Control_Plane_v1_113.md` §1. **The VARIANT set is UNCHANGED at FOUR**; `EffectFenceAddressable` goes 4 → 6 source shapes and the union 8 → 10, across an UNCHANGED SEVEN distinct source carriers. The `step_kind` per-source-shape paragraph and the sub-discriminator parenthetical are recounted (present on FIVE shapes, absent from FIVE; sub-discriminator required for 6 + 2 shapes). **NO new `C-RT-*` number, NO carrier retyped, NO field added, NO `snapshot_hash` impact** — the delta is entirely READ-SIDE. §14.14.9.1, §14.14.9.3 – §14.14.9.6, §30, §14.14.8 and §13.7 are PRESERVED VERBATIM.

Reviewed at clearance: that the §14.14.9.2 sub-discriminator rule accommodates the two new shapes with no new machinery (it keys on the source SHAPE, not on any carrier field — checked before applying); that §14.14.9.5's trace-emission row still requires FOUR per-variant counts, so the OD-owned `§C-OD-30.5` attribute schema is untouched and no OD delta is owed; and that disposition **(b)** (capture-side refusal) is NOT applied.

Caveats for Phase 7 consumers. **FIVE findings are surfaced rather than absorbed** (change-note (i) – (iv) plus the registered `B-106` scalar-channel finding), the first being a **FALSIFIED PREMISE in the authorizing register row** — the orchestrator capture site *does* guard on a truthy key, so that shape is unreachable in production and its acceptance witness MUST be a constructed-snapshot test, never an end-to-end run. **An IMPL delta IS owed and is NOT this leg** — owning units U-RT-148 (`Implementation_Plan_Harness_Runtime_v2_57.md`) and U-CP-64 (`Implementation_Plan_Control_Plane_v2_48.md`). **Anchor convention:** this delta authors no new in-file `:NNNN` anchors; its insertion shifts lines below it, and `:NNNN` anchors inside prior-version change-notes remain historical records read against the version that authored them.

## Notes

- **Register disposition at this leg:** `B-100` is **NARROWED to its IMPL remainder, NOT closed** — the forward-register status enum defines `closed` as *built + merged, or foreclosed/superseded*, and the two projection types plus their emptiness routing are unbuilt. Precedents: `B-97`(a) (open through the v1.108 spec leg at PR #1168, closed only at PR #1171 once U-RT-149 impl landed) and `B-102` (*narrowed to that remainder rather than closed*). The row's `summary` and its prose home at `.harness/post-phase-8-forward-register.md` are BOTH refreshed with the corrected grounds in the same commit, so following the row's heading back-pointer no longer yields contradictory guidance.
- **No fresh operator gate was owed, and the absence is a determination, not an omission** — the authorizing row's own `council` field routes this to a *spec-writer apply pass*; the underlying rule was ratified at the `B-69` arc (2026-07-30, OPTION A′) and is PRESERVED VERBATIM; and the `close_out` names disposition (b) *"NOT the default recommendation"*, leaving (a) as the row's own default. The two sub-decisions this leg did make are flagged at contract altitude so they can be overturned rather than discovered.

- **TWO channels this leg CANNOT close, REGISTERED as `B-106`** (a NEW id; `B-105` was minted and withdrawn at PR #1172). **Neither is closed by this arc, and the map one is NOT closed either.** *(1) The MAP channel* — removing the key field removes only the **advertisement**; `ResumeContext.effect_fence_resolutions` is a `dict[str, …]` with **unconstrained keys**, so a caller composing independently of the projection can still hand-build `{"": …}`, which `_resolve_effect_fence_gated` treats as a mapped resolution. *(2) The SCALAR channel* — `compute_effect_fence_uniform_fallback_eligible_key` (`workflow_driver.py:2935`–`:2970`) does not filter empty keys, so a key-absent location that is the sole unaddressed one becomes eligible for the caller's scalar `effect_fence_resolution`. The terminal loss reaches **all three carriers** (LINEAR threads a doomed directive; branch and orchestrator skip the consult behind their truthiness guard) and ends the same way in every case — a **silent INERT re-pause**. **Do NOT read this arc's criteria green as evidence that EITHER channel is closed**, and note that `B-106` closure requires a witness **per channel AND per carrier**.

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
