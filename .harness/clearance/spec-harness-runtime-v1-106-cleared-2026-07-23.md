---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.106
cleared_at: 2026-07-23T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_b39_nested_hitl_response_threading.md (RATIFIED 2026-07-23)
  - design-substrate/Spec_Control_Plane_v1_106.md (same-arc CP-owned rider; Q1/Q2 full reconcile record)
merge_commit: pending (pre-merge at filing time; B-39 spec-leg PR)
reviewer_chain:
  - operator ratification (2026-07-23) — Q1=(A) retire ResumeContextHolder
  - advisor() + AskUserQuestion reconcile (this session) — Q2 carrier-shape (CP-owned; cross-referenced here)
  - just codex-review-uncommitted (2026-07-23, round 1) — out-of-family, found 4 P1 wiring defects (2 land on this file's §14.8.8.10)
  - Explore grounding pass (2026-07-23, round 1) — confirmed the entry-point + nested-child + retry-replay findings against the real call graph
  - advisor() (2026-07-23, round 1) — recommended the CONTRACT-altitude correction
  - just codex-review-uncommitted (2026-07-23, round 2) — out-of-family, found the CP-owned hitl_responses key shape (branch_path) collides on repeated same-child_workflow_id dispatch (this file's own §14.8.8.10 was not itself wrong, but its cross-references needed updating)
  - just codex-review (2026-07-23, round 3, branch-vs-main against open PR #1092) — out-of-family, found the resume_handle path cannot supply child run_ids for hitl_responses addressing (this file's own §14 resume() invariants needed a scope-limit note); the other 2 round-3 findings are entirely CP-owned
---

# Clearance — Spec_Harness_Runtime_v1 (B-39 arc, spec leg; THREE same-day correction passes)

**Round-2 note.** A second out-of-family review round found the CP-owned
`ResumeContext.hitl_responses` key shape (`branch_path`) collides when two
peer branches dispatch the SAME `child_workflow_id` — see the sibling
`Spec_Control_Plane_v1_106.md`'s own round-2 correction block for the full
fix (re-keyed to the paused child's own `run_id`). This file's §14.8.8.10
CONTRACT was already agnostic to the exact key shape (it references CP's
`hitl_response_for` by name, not by its argument), so NO content change was
needed here beyond this note — the round-1 correction below stands
unmodified.

**Round-1 correction pass (same-day, after this marker's original filing).** The
§14.8.8.10 body originally cleared here asserted a specific two-channel
`execute_workflow` parameter design and claimed one-shot delivery is
"now structural... by construction." Out-of-family review
(`just codex-review-uncommitted`) plus an `Explore` grounding pass found
this false against the EXISTING retry composition
(`RetryBreakerFallbackDispatcher` wraps the HITL gate composer as `inner`
and re-invokes `dispatch()` on every retry attempt within one
`execute_workflow` invocation — a bare parameter re-supplied identically on
every retry would incorrectly replay the resolved response). §14.8.8.10 is
rewritten to state the CONTRACT (per-branch-distinct delivery; one-shot
preserved under retry; no new global sharing) without prescribing the
parameter shape. This mirrors the same-day correction at the sibling
`Spec_Control_Plane_v1_106.md` §1.

v1.105→v1.106: the `ResumeContextHolder` sidecar carrier (§14.8.8.9,
authored at v1.25) is RETIRED as a ctx-level, run-tree-wide-shared binding,
per the CP-owned Q1=(A) decision at the sibling `Spec_Control_Plane_v1_106.
md`. `HarnessContext` no longer carries a `resume_context_holder` field
(C-RT-04 row marked RETIRED). NEW §14.8.8.10 declares the CONTRACT the
replacement mechanism must satisfy — it does NOT prescribe which CP-owned
`execute_workflow` parameters (if any) deliver the value, nor which entry
point supplies it. §14.8.8.5/§14.8.8.7 invariant 3/§14.8.8.8 are marked
SUPERSEDED in-place; their historical content is preserved verbatim
(nothing deleted, per this file's accumulating-change-note convention).
**Round-4 clarification (out-of-family review):** a prior draft here noted
retaining-and-rescoping the `ResumeContextHolder` class as a "candidate
lead" for the one-shot-under-retry property; review found this risked
reading as reopening Q1=(A)'s ratified full retirement of the holder.
REMOVED — Q1's retirement of the ctx-level, run-tree-wide-shared BINDING is
fixed, not impl discretion; the impl leg may use any TYPE (new or
repurposed) so long as it is never bound at that scope again. Exact
wiring — including which entry point supplies the depth-0 value (grounding
located the REAL one at `harness_runtime/api.py`'s `resume()` +
`lifecycle/mcp_server.py`, not the previously-asserted `attempt_resume`) and
how a nested child's re-dispatch (which crosses the EXISTING
`StepExecutionContext.child_resume_snapshot` → `RuntimeSubAgentDispatcher` →
`ChildWorkflowRunner` → `child_workflow_runner.py` seam) receives its own
value — is implementation discretion, verified by execution (not by grep)
at the impl leg, mirroring the ORIGINAL v1.24 §14.8.8.8 framing for this
identical question.

**Round-3 note (branch-vs-main `just codex-review` against open PR #1092).** Found the `resume_handle` crash-recovery resume mode (§14's `resume()` invariants) cannot supply a paused child's `run_id` before `resume_context` construction, since the caller never possesses the prior `PauseSnapshot` on that path — the CP-owned `hitl_responses`/`child_run_id` addressing scheme (§0 of the sibling CP spec) is therefore unreachable there. Fixed: the `resume()` invariants' "Resume-context one-shot delivery" bullet gains a scope-limit note stating `hitl_responses` addressing works only on the `pause_snapshot`-supplied resume path; `resume_handle` callers are limited to the single-paused-child uniform-fallback case. A follow-on durable-pause-state read accessor is registered, not designed here. The other 2 round-3 findings (multi-child fallback-safety gate; unsafely-sequenced field-removal AC) are entirely CP-owned — see the sibling `Spec_Control_Plane_v1_106.md` clearance marker's own round-3 section; this file required no further change for those two.

This is the spec leg only — the impl arc (composer body amend,
`HarnessContext` field removal, plus tests, plus a scope-discovery pass to
determine which units carry the propagation-mechanism wiring) follows as a
separate PR per the B-33/B-59 precedent. Plan delta `Implementation_Plan_
Harness_Runtime_v2_54.md` (U-RT-94 amended + U-RT-95 confirmation note,
both post-correction) carries the acceptance criteria.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
