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
  - just codex-review (2026-07-23, round 4, branch-vs-main against the round-3 fix commit) — out-of-family, found round 3's CP-owned property 4 defective; this file required no further content change (entirely CP-owned)
  - just codex-review (2026-07-23, round 5, branch-vs-main against the round-4 fix commit) — out-of-family, found THIS file's own property-1 restatement had not carried the round-4 gate-owning correction, plus an overstated PD-8 witness promise and a stale U-RT-95 cross-reference
  - just codex-review (2026-07-23, round 6, branch-vs-main against the round-5 fix commit) — out-of-family, found a Runtime-plan-side atomicity drift + a genuinely new CP-owned registration (B-71); this file itself required no round-6 change
---

# Clearance — Spec_Harness_Runtime_v1 (B-39 arc, spec leg; SIX same-day correction passes)

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

**Round-4 note (branch-vs-main `just codex-review` against the round-3 fix commit).** Found round 3's CP-owned §1.2 property 4 (this file's own §14.8.8.10 CONTRACT never itself asserted the fallback semantics) prescribed a resolver mechanism that strands transitively-paused container branches and is unassignable to any declared unit — converted to a black-box invariant at the sibling CP spec, entirely CP-owned; see that marker's own round-4 section. **This "no further change" call was ITSELF corrected at round 5 below — this file DID need a change, just not one round 4's own review pass surfaced.**

**Round-5 note (branch-vs-main `just codex-review` against the round-4 fix commit).** Found this file's own §14.8.8.10.1 property 1 restatement had NOT carried the CP spec's round-4 gate-owning-vs-container-branch correction — it still read as requiring EVERY concurrently-paused branch (including a transitively-paused container/ancestor) to receive its own `hitl_response_for` resolution, reintroducing the exact strand-the-container-branch defect round 4 fixed on the CP side. Fixed: property 1 corrected in-place to scope to GATE-OWNING branches only; a NEW property 4 (the multi-branch safety+liveness invariant) added for completeness, mirroring the CP-owned one. Also found this file's own PD-8 witness-obligations paragraph overstated coverage — the repeated-`child_workflow_id` PRODUCTION-shape routing proof (as opposed to the CARRIER-level witness, which IS confirmed at CP plan v2.42 AC #7) is not actually assigned to any unit; corrected to explicitly defer it to the impl-leg resolver bucket (Runtime plan v2.54 §3's new row) rather than implying it was already covered by U-RT-95's AC #9. Also found the stale "U-RT-95 confirmation note" cross-reference below (unchanged since this marker's original filing, predating even round 3's own U-RT-95 fix) — corrected.

**Round-6 note.** Findings landed at the sibling Runtime PLAN's own §1 Files row (an atomicity drift, this SPEC file's own §14.8.8.10.1 property 3/§1.4-mirroring text was not itself wrong) and at the CP spec (`B-71`, a genuinely new registration). This file required no further content change.

This is the spec leg only — the impl arc (composer body amend,
`HarnessContext` field removal, plus tests, plus a scope-discovery pass to
determine which units carry the propagation-mechanism wiring) follows as a
separate PR per the B-33/B-59 precedent. Plan delta `Implementation_Plan_
Harness_Runtime_v2_54.md` (U-RT-94 amended + U-RT-95 amended — round-3-
corrected from a confirmation note to a genuine NEW AC #9, round-4-scoped
to exclude the production-shape multi-child witness) carries the
acceptance criteria.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
