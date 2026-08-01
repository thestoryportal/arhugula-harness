---
artifact: design-substrate/Spec_Control_Plane_v1_114.md
version: v1.114
cleared_at: 2026-08-01T00:00:00-06:00
clearance_type: spec-writer-apply-pass
back_reference:
  - .harness/forward-register.yaml row `B-101` (the filed finding; `close_out` pre-selects disposition (b), and its NEAREST-APPROACH VECTOR note is what makes this leg (b)-PLUS)
  - PR #1166 (the `B-69` impl leg, where `B-101` was surfaced at out-of-family review round 3 [P1] and REPORTED not absorbed)
  - PR '#pending' (this arc)
merge_commit: pending
reviewer_chain:
  - >-
      spec-writer apply pass — applies the PRE-SELECTED disposition (b) in its (b)-PLUS form and EXTENDS NOTHING
      beyond what the authorizing row's own NEAREST-APPROACH VECTOR note demands. Disposition (a), a closed variant
      discriminator on ResumeContext, is deliberately NOT applied — it breaks the field-set-preserved-verbatim
      guarantee Spec_Control_Plane_v1_112.md §0.4 makes, and the row conditions it on a serialization boundary
      appearing on a real resume path, which does not exist at HEAD (verified, not assumed). ONE scope question is
      DECIDED and stated rather than buried — whether §1.3(c)'s 'no construction path produces a legacy variant from
      an accessor-derived one' reaches generic base-schema serialization, or only the CP-owned affordances its own
      detect-then-refuse witness exercises. The narrower reading is applied, which IS the row's pre-selected
      disposition (b) verbatim; the broad reading (under which this is a NARROWING, not a clarification) is recorded
      in full at §0.5 finding (vi) with its one-step escalation route named, so a reviewer can overturn it rather
      than discover it. No fresh operator gate was owed — the row's own council field routes this to a spec-writer
      apply pass, and the underlying residual was already on the record at v1.112 §1.2. Rationale at
      Spec_Control_Plane_v1_114.md §0.3 + §0.5 finding (vi).
  - empirical grounding pass at this leg — every HEAD claim the appended paragraph makes was re-verified by direct
    read rather than carried from the row's 2026-07-31 note (`ResumeContext`-typed annotation census, the
    `model_dump`/`TypeAdapter` sweep across src AND tests, `model_copy` shallowness, `revalidate_instances` absence,
    the pin test's location). Recorded as a table at §0.4.
  - out-of-family Codex review (`just codex-review-uncommitted`) to convergence
supersedes: spec-control-plane-v1-113-cleared-2026-07-31.md
---

# Clearance — `Spec Control Plane v1.114`

v1.114 is a delta-only file carrying **ONE amendment site**: `Spec_Control_Plane_v1_112.md` §1.2 constraint 3's stated residual (the paragraph headed *"The residual, stated precisely rather than left for a reader to discover"*) is **APPENDED TO** with one paragraph. The paragraph declares the **ORDINARY-SERIALIZATION boundary formally OUT of the staleness fence's scope**, NAMES `StepExecutionContext.resume_context` (`harness-cp/src/harness_cp/workflow_driver_types.py:460`) as the ONE live base-typed carrier, RECORDS the three grounded facts that keep it unreachable at HEAD, and states a normative **PROMOTION TRIGGER**.

**No text is retracted or reworded — and the one scope question this leg DID decide is stated, not buried.** §1.3(c)'s reach (*"no construction path produces a legacy variant from an accessor-derived one"*) is made **EXPLICIT where v1.112 left it implicit**: it binds the CP-owned affordances its own detect-then-refuse witness exercises (`harness-cp/tests/test_pause_state_projection_b69.py:149`, AC #A2 — no downgrade helper, frozen-carrier mutation refused, and the accessor-derived variant's OWN dump refused into the legacy type by `extra="forbid"`), and **not** generic base-schema serialization, which slips past that third guard because the base schema never emits the provenance field for `extra="forbid"` to see. **Under the broadest reading of §1.3(c) that IS a narrowing rather than a clarification** — the counter-reading is recorded in full at `Spec_Control_Plane_v1_114.md` §0.5 finding (vi), with the narrower reading's three grounds and the **one-step escalation route (disposition (a))** named, so a reviewer can overturn it. The residual's existing sentences, §1.1, §1.2 constraints 1–3, §1.3, and the whole of §2 / §3 / v1.113 are **PRESERVED VERBATIM**. `ResumeContext`'s field set is untouched; the §2.1 union stays **FOUR** variants over **TEN** source shapes across **SEVEN** carriers. **ZERO contract numbers, ZERO carriers retyped, ZERO fields added, ZERO hash impact, ZERO impl units owed, ZERO plan deltas owed, ZERO test changes owed.**

Reviewed at clearance: that the amendment is an APPEND rather than a rewrite (the preserved-verbatim claim was checked against the v1.112 text, not asserted); that disposition **(a)** is correctly declined and its condition correctly stated; that CXA v2.23 is **UNCHANGED**, aggregate frozen at 111, determined rather than assumed (this delta adds no surface, no payload and no consumer); and that **no implementation plan cites `B-101` as owing units** — `B-101` appears at exactly ONE place in `design-substrate/**`, `Spec_Control_Plane_v1_113.md` §0.4 finding (vi), where it is named as the obstacle `B-107`'s disposition (d) would run into.

## Caveats for Phase 7 consumers

- **The declared-out-of-scope boundary is a REAL residual, not a closed gap.** An accessor-derived `ResumeContext` round-tripped through a base-typed field or a base `TypeAdapter` loses its provenance carrier and the §30 staleness fence does not fire. v1.114 states that this is outside the fence's scope; it does not make it stop happening. **Do not read this version as evidence that the serialization path is safe.**
- **The PROMOTION TRIGGER is binding on future arcs, and it keys on MECHANISM rather than on the named carrier.** Any arc introducing **ANY base-schema serialization boundary over a `ResumeContext` value on a resume path** — a `ResumeContext`-typed model field (today only `StepExecutionContext.resume_context`), a base `TypeAdapter`/`RootModel` over `ResumeContext`, a base-annotated parameter or return crossing a schema-generating boundary, or any equivalent — MUST promote `B-101` to disposition (a) and land that amendment **before or simultaneously with** the serialization — never after.
- **Its enforcement is a pre-merge review obligation, not a validator rule** (§0.5 finding (iv)). The pin test `test_provenance_is_lost_through_base_typed_serialization_registered_b101` (`harness-runtime/tests/test_paused_workflow_state_accessor_b69.py:924`) breaks on a **behavior** change but does **NOT** fire on the bare addition of a `model_dump` call. That gap is stated in the spec rather than papered over.
- **The pin test STAYS and must NOT be deleted at the row's close** (§0.5 finding (i)). Under (b)-PLUS it is the executable half of the trigger: it asserts the current lossy behavior deliberately, so any future change to that behavior is reviewed rather than silent.

## Notes

- **Register disposition at this leg:** `B-101` is **CLOSED** (`pr: '#pending'`, reconciled post-merge). This differs from the `B-100` / `B-97`(a) / `B-102` precedent of NARROWING at a spec leg, and the discriminator is the disposition's own shape: those rows' close-outs left **unbuilt impl remainders**, so closing them would have presented unshipped work as done. Disposition (b) is **documentary by construction** — it declares a boundary rather than moving one — so its close-out is fully discharged by this delta, with **no impl, plan or test remainder** (verified at §0.5 finding (ii)). The row's `summary` and its prose home at `.harness/post-phase-8-forward-register.md` are BOTH refreshed in the same commit, recording the applied disposition, the promotion trigger, and the pin test's retained boundary-marker role.
- **The `B-107` adjacency is recorded, and the rows are NOT merged.** `Spec_Control_Plane_v1_113.md` §0.4 finding (vi) already names `B-101`'s obstacle as the one `B-107`'s disposition (d) (a min-length-1 key type on `effect_fence_resolutions`) would hit — both are field-set changes to a carrier §0.4 guarantees preserved verbatim. The two rows track different harms (dropped provenance vs. accepted empty keys) and remain separate; the adjacency is stated at §0.5 finding (v) so a future arc willing to pay that cost does not re-cost it twice in isolation.
- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
