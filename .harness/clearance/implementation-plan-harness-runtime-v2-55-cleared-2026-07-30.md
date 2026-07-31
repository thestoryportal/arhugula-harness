---
artifact: design-substrate/Implementation_Plan_Harness_Runtime_v2_55.md
version: v2.55
cleared_at: 2026-07-30T00:00:00-04:00
clearance_type: spec-writer-apply-pass
back_reference:
  - .harness/council-b69-pause-state-accessor-2026-07-30.md
  - .harness/council-b69-pause-state-accessor-2026-07-30.md §9 row 6 + §11 (the W1–W4 witness obligations)
  - .harness/forward-register.yaml row B-69
merge_commit: <pending — this PR>
reviewer_chain:
  - council voices C10 + C11 + C9 (§11's witness set, including C9's own falsifier placed on the record)
  - harness-adversarial-reviewer in-family pass — which called the witness shape (by-execution, PD-8 mutation probe, falsifier on record) a strength, and re-scoped W4
  - out-of-family `just codex-review-uncommitted` (GPT-5.6)
  - operator AskUserQuestion ratification 2026-07-30 — OPTION A′ (CO-REQUISITE, SEQUENCED)
  - spec-writer apply pass (this arc)
---

# Clearance — `Implementation_Plan_Harness_Runtime_v2_55.md`

v2.55 absorbs Runtime spec **v1.106 → v1.107** into **ONE NEW unit, U-RT-148**, carrying BOTH ratified surfaces — the C-RT-36 §31 accessor (with its closed **four**-variant projection DTO spanning seven-plus source shapes, five-member cause attribution, and declared postures) and the §30 refusal-only staleness precondition — under the arc's conjunctive closure criterion. ZERO existing unit amended; ZERO new cluster. **TWO new cross-axis DAG edges** — U-RT-148 → U-CP-64 (concrete) and U-RT-148 → a PENDING, not-yet-numbered OD unit.

**Why one unit rather than a paired sibling** (the council authorized either): the closure criterion is conjunctive, so a single unit makes it the unit's own completion test rather than a cross-unit note a session handoff can drop; the primary witness **W2 is inherently joint** (it asserts the misattribution is refused *under* the fence AND reproduces *without* it) and cannot be assigned to either surface alone; and splitting would create precisely the merge interval the operator's A′ ratification forecloses. **The ordering constraint is therefore restated as a unit-internal obligation (AC #10)** — no commit may make the accessor reachable through the public surface before the precondition is enforced on `resume()`.

**SIXTEEN acceptance criteria (recounted programmatically at the final review round), every one by EXECUTION.** The load-bearing ones: **AC #1 (W2, PRIMARY)** — the sole-member misattribution in the **1→1 shape**, asserting the branch does *not* receive the uniform response under the fence **and does without it**, with C9's falsifier carried on the record; **AC #4 (W3)** — the fence by **PD-8 mutation-probe** against a **REAL** second `capture()`, remove-the-check-and-confirm-it-reappears, which is **one half of B-69's conjunctive closure criterion**; **AC #3 (W2′)** — run the 1→1 shape with a `snapshot_hash`-based fence installed and assert it *still* misattributes, converting the council's P4 from a reasoned finding to an executed one and foreclosing a later session re-nominating the conceded carrier; **AC #6** — non-downgradability and the unrepresentability of read-then-omitted, asserted by **detect-then-refuse**, not by absence-of-helper; **AC #9** — the checkable one-authority criterion, carried **verbatim** and duplicated at CP plan v2.47 so neither side drifts unilaterally; **AC #15** — the **source-shape sub-discriminator by detect-then-refuse**, since the DTO variants span **seven-plus source shapes** with different field sets and a per-variant optional `step_kind` would readmit an illegal state one level below the union.

**Two dependencies, and the second has no number yet.** U-RT-148 depends on **U-CP-64** (concrete) **and on a PENDING, not-yet-numbered OD unit** carrying the OD v1.36 §30.5.2 additive audit carrier — AC #13(c) cannot run without it, because the staleness refusal is raised pre-bootstrap and `PauseResumeAuditPayload` is `frozen` / `extra="forbid"` with no token field. Both edges are stated in the plan's header and footer so a scheduler cannot read U-RT-148 as ready once CP alone lands.

**AC #5 (W4) carries a mandatory in-test annotation.** As written it asserts a **placeholder property**; when a real `pause_context_reader` lands it will fail *for a good reason*, and its correct disposition is then **DELETION or INVERSION — never repair**. Without the annotation a future session will "repair" it, which is the wrong disposition. AC #3 is the load-bearing empirical form of the same finding and is unaffected.

**Caveats for Phase 7 consumers.** Spec + impl do NOT land together — this is the plan absorption only. Out of scope for U-RT-148 and stated so they are not silently absorbed: the CP projection surface and CP `ResumeContext` carrier (U-CP-64's); a tenant binding on the pause journal; gate description in the projection; **any capture-side change whatsoever** — this is a read-only arc, and the §14.14.8 substrate invariant is what makes it possible without one.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
