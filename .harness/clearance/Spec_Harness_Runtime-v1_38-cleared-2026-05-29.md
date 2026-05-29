---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.38
cleared_at: 2026-05-29T15:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_topology_admissibility_check_load_time_vs_runtime_asymmetry.md
  - PR #80 (filing)
  - PR #80-apply (apply arc)
merge_commit: TBD-at-PR-merge
reviewer_chain:
  - use-the-product probe (post-PR-#78 session, 2026-05-29)
  - advisor 56th application (pre-substantive scope-discipline + apply-order check)
  - operator AskUserQuestion ratification 2026-05-29 Q-set (Q1=A + Q2=α + Q3=i + Q4=c + Q5=β)
  - spec-writer apply pass (this arc — Reading A absorption into spec body + plan body)
  - impl-time grounding pass (1301/1301 harness-runtime + 794/794 harness-cp tests pass post-amendment)
---

# Clearance — `Spec_Harness_Runtime_v1.md v1.38`

v1.38 absorbs the Class 1 fork resolution Reading (A) deferring topology admissibility from load-time at `WorkflowManifestLoader.load()` to runtime at the sub-agent-dispatch site (`sub_agent_dispatch.py:585`). Pattern-consistent extension of v1.36 Reading (β) which deferred engine_class admissibility loader → U-RT-106. Spec §14.19.4 invariant 2 + §14.19.2 row 7 canonical-reading amendment; spec body PRESERVED VERBATIM (the deferral is documented at the change-note layer; the body narrative remains).

What was reviewed: use-the-product probe finding #14 catalogued the structural inconsistency empirically (loader rejects what integration test bypass accepts at runtime); advisor 56th application caught apply-order + Q-set ratification record discipline; operator ratified Reading A en-bloc Q1-Q5; impl-time grounding pass verified ZERO regression at runtime + cp test suites (2095 tests pass total).

Caveats for Phase 7 consumers: AC #12 at U-RT-104 is RETIRED at plan v2.40 (AC count 14 → 13). `ManifestAdmissibilityError` class is PRESERVED in the §14.19.2 taxonomy — still used by CLI app for engine_class admissibility per v1.36 Reading β. Future arcs introducing topology-dependent dispatch surfaces beyond sub-agent dispatch SHOULD add admissibility check at each new fan-out site OR add a central enforcement site (Q3=ii deferred to operator-discretion). Sibling fork at PR #79 (YAML scalar coercion) is separate and orthogonal; both must be resolved for operator-facing YAML CLI to ship runnable.

## Notes

- Phase 7 consumers may rely on v1.38 as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
- Sibling clearance (PR #79 apply) follows at separate PR with `Spec_Harness_Runtime-v1_39-cleared-2026-05-29.md`.
