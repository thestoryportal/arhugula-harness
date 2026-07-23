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
  - just codex-review (2026-07-23, round 3, branch-vs-main against open PR #1092) — out-of-family, found §2's "AC #3 confirmed" claim empirically false against the actual U-RT-95 test file (resume-consume-cycle deferred per FM-2, not exercised)
  - Direct file read (2026-07-23, round 3) — read test_u_rt_95_hitl_pause_trigger_durable_async_full_execution_path.py lines 1-56 to verify the finding before editing (per subagent-landscape-reports-need-regrounding discipline, applied to a self-authored claim this time)
  - just codex-review (2026-07-23, round 4, branch-vs-main against the round-3 fix commit) — out-of-family, found this file's own filing footer still said "one confirmation note (U-RT-95)" after round 3 made it a genuine amendment; the other 2 round-4 findings are entirely CP-owned
  - just codex-review (2026-07-23, round 5, branch-vs-main against the round-4 fix commit) — out-of-family, found AC #9 implicitly overclaimed coverage of the production-shape repeated-child_workflow_id routing proof, which no unit actually owns
  - just codex-review (2026-07-23, round 6, branch-vs-main against the round-5 fix commit) — out-of-family, found this file's own U-RT-94 Files row still asserted HarnessContext.resume_context_holder removal as unconditional/standalone; the other round-6 finding (HITLEscalationBrief correlation gap) is entirely CP-owned
---

# Clearance — Implementation_Plan_Harness_Runtime_v2_54 (B-39 arc, plan leg; SIX same-day correction passes)

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
originally got a confirmation note here (fixture-setup change only; public
call shape unchanged) plus a NEW owed same-cycle-retry e2e scenario —
**SUPERSEDED at round 3** (see below): direct reading of the actual test
file found the resume-consume-cycle path is deferred per FM-2, not
exercised at all; U-RT-95 is a genuine AC #9 amendment, not a fixture-only
confirmation.

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

**Round-3 correction (same-day, branch-vs-main `just codex-review` against open PR #1092).** §2's prior text claimed AC #3 "is CONFIRMED to still exercise the IDENTICAL operator-facing call shape" through the public `attempt_resume`/`api.resume()` surface, framed as a fixture-only note. Direct read of the ACTUAL U-RT-95 test file found this FALSE: its own doc-comment (lines 29-31) states path (ii) resume-consume-cycle is "deferred to a follow-on arc per FM-2." The materialized path (i) exercises the *engine-layer* WAL_SEGMENT recovery loop (a distinct C-CP-22 surface) — not the workflow-layer HITL composer's public delivery. No test anywhere currently exercises a full public-surface HITL resume-consume cycle. Fix: the "confirmation note" framing is withdrawn; a genuinely NEW AC #9 requires a net-new e2e test (not a fixture edit) materializing the FM-2-deferred path, plus the previously-noted same-cycle-retry e2e scenario.

**Second branch-vs-main correction (same-day, against the round-3-above fix commit — distinct from the EARLIER "Round-4 note" above, which predates this session's branch-vs-main review sequence and covers a different topic, candidate-lead removal).** Found this file's own §0.3/filing-footer text still described U-RT-95 as carrying "one confirmation note" after the round-3 fix directly above already made it a genuine AC #9 amendment — fixed (§0.3 + filing footer now say "TWO amended-unit-body amendments"). The round's other 2 findings (a resolver-mechanism defect + a CP-plan unit-assignment defect) are entirely CP-owned — see the sibling `Implementation_Plan_Control_Plane_v2_42.md` clearance marker's own round-4 section; this file required no further content change for those.

**Third branch-vs-main correction (same-day, against the round-4-above fix commit).** Found AC #9 implicitly overclaimed coverage: it materializes a single-workflow public-surface resume-consume-cycle + retry scenario, but the sibling Runtime spec's PD-8 witness paragraph promised a repeated-`child_workflow_id` PRODUCTION-shape routing proof that neither AC #9 nor CP plan U-CP-64's own pure-lookup AC #7 can actually exercise (the production derivation/delivery join needs the not-yet-designed resolver). Fixed: AC #9 gains an explicit "OUT of scope" carve-out naming this scenario and registering it in the SAME deferred-resolver bucket as §3's existing deferred row (a NEW §3 row added); the sibling Runtime spec's PD-8 paragraph is corrected to match (CARRIER-level confirmed vs. PRODUCTION-shape deferred, no longer conflated as one witness).

**Fourth branch-vs-main correction (same-day, against the round-5-above fix commit).** Found this file's OWN §1's Files row still described `HarnessContext.resume_context_holder` removal as "the one unconditional removal this unit owns" — a drift, since the sibling CP spec's §1.4 atomicity requirement (physical removal MUST co-land with re-pointing 3 CP-owned effect-fence readers) was never propagated to THIS file's own parallel assertion, even though it names the identical field. Fixed: the Files row now states the atomicity constraint explicitly; §3's coverage matrix row updated to match (field removal folded into the deferred bucket, not owned standalone by U-RT-94). The round's other finding (operator-facing HITL escalation requests lack a run_id) is entirely CP-owned — see the sibling `Spec_Control_Plane_v1_106.md` clearance marker's own round-6 section (`B-71`); this file required no further change for that.

This is the spec leg's plan absorption only — impl (code + tests) is a
separate follow-on arc per the B-33/B-59 precedent; the impl leg additionally
owes the scope-discovery pass this correction defers.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
