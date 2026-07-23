---
artifact: design-substrate/Implementation_Plan_Harness_Runtime_v2_54.md
version: v2.54
cleared_at: 2026-07-23T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_b39_nested_hitl_response_threading.md (RATIFIED 2026-07-23)
  - design-substrate/Spec_Harness_Runtime_v1.md (§14.8.8.10, v1.106)
merge_commit: pending (pre-merge at filing time; B-39 spec-leg PR)
reviewer_chain:
  - operator ratification (2026-07-23) — Q1=(A)
  - just codex-review-uncommitted (2026-07-23, round 1) — out-of-family, found 4 P1 wiring defects in a first draft (2 land on this file's AC #7/#8)
  - Explore grounding pass (2026-07-23, round 1) — confirmed the retry-replay defect against the real `RetryBreakerFallbackDispatcher`/composer wiring
  - advisor() (2026-07-23, round 1) — recommended the CONTRACT-altitude correction
  - just codex-review-uncommitted (2026-07-23, round 2) — out-of-family, found the CP-owned hitl_responses key shape collides on repeated same-child_workflow_id dispatch (CP-owned; this file's own AC #7/#8 unaffected, Depends-on note updated)
---

# Clearance — Implementation_Plan_Harness_Runtime_v2_54 (B-39 arc, plan leg; TWO same-day correction passes)

**Round-2 note.** A second out-of-family pass found the CP-owned
`hitl_responses` key shape (`branch_path`) collides on repeated same-
`child_workflow_id` dispatch — see the sibling `Implementation_Plan_
Control_Plane_v2_42.md`'s own round-2 correction for the fix (re-keyed to
`child_run_id`). This file's own AC #7/#8 (round-1 content, below) are
UNCHANGED — they never referenced `branch_path` — only the §1 Depends-on
note's parenthetical was updated to match.

v2.53→v2.54: U-RT-94 (the HITL gate composer body unit that has owned
§14.8.8.5 resume-side one-shot delivery since its v2.23 authoring) is
amended — AC #7/#8 rewritten at CONTRACT altitude: per-branch-distinct
delivery, one-shot-per-resume-cycle PRESERVED UNDER RETRY, no new global
sharing. `HarnessContext.resume_context_holder` field removal is asserted;
the exact replacement wiring (including `resume_context_holder.py`'s own
disposition) is impl discretion. U-RT-95's e2e resume-consume-cycle test
gets a confirmation note (fixture-setup change only; public call shape
unchanged) plus a NEW owed same-cycle-retry e2e scenario.

**Round-1 correction pass (same-day).** A first draft's AC #7/#8 asserted the
composer consumes a bare per-call `resolved_hitl_response` parameter and
that one-shot delivery is "now structural... by construction." Out-of-family
review found this false: `RetryBreakerFallbackDispatcher` wraps the HITL
gate composer as `inner` and re-invokes `dispatch()` on every retry attempt
within ONE `execute_workflow` invocation — a bare parameter re-supplied
identically on every retry would incorrectly REPLAY the resolved response
instead of letting the retry re-fire the gate, a regression versus the
retired holder's `consume_and_clear()`. AC #7/#8 were rewritten to state the
guarantee (one-shot-under-retry) without prescribing the mechanism.
**Round-4 note:** a "retain-and-rescope-the-class" candidate lead was
recorded here and at the spec; out-of-family review found it risked
reading as reopening Q1=(A)'s full holder retirement. REMOVED from both —
Q1's retirement of the ctx-level, run-tree-wide-shared BINDING is fixed;
the impl leg may use any type, new or repurposed, so long as it is never
bound at that scope again.

This is the spec leg's plan absorption only — impl (code + tests) is a
separate follow-on arc per the B-33/B-59 precedent; the impl leg additionally
owes the scope-discovery pass this correction defers.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
