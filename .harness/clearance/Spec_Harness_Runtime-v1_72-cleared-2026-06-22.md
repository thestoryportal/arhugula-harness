---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.72
cleared_at: 2026-06-22T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-spine-ledger (operator-AUTHORIZED committed-behavior change — the runtime half of B-EFFECT-FENCE-HITL-ROUTE. The §14.22 C-RT-31 effect fence's lost-reserve re-dispatch no longer uniformly fail-closes; it SPLITS two ways [new §14.22.8] on a newly-captured output — present → suppress-and-continue [return the captured output, NEVER re-fire], absent/corrupt → an operator-SURFACED §26.2 PAUSE [bound PauseResumeProtocol; a labeled non-terminal capture, strictly better than the v1.60 terminal FAILED — the resume-side RESOLUTION is the registered follow-on B-EFFECT-FENCE-PAUSE-RESOLUTION] else FAILED. NEVER an auto-re-fire [the #701 decline-mirror invariant transferred: auto-proceed ONLY on proof-of-completion]. Adds `capture_output`/`read_output` to the fence [atomic O_EXCL/link, present ⟹ complete-and-valid]; renames `EffectFenceReservedUncommittedError` → `EffectFenceAmbiguousUncommittedError`. The OPERATOR GATE — relaxing the fence's load-bearing fail-closed + a new pause-reason value — was AUTHORIZED by AskUserQuestion 2026-06-22 over the other gated arcs + the quality track. No new fail-class taxonomy code, no §5.2-hash change, no StepDispatcher Protocol widening, no new CXA edge.)
back_reference:
  - .harness/class_1_fork_effect_fence_hitl_route.md (the advisor-vetted design proposal the operator authorized; this runtime v1.72 + CP v1.51 deltas execute it — with verification 1's §22.1→§26.2 pause-reason-home corrected by primary-source grounding)
  - .harness/beyond-mvp-capability-boundary-ledger.md (B-EFFECT-FENCE-HITL-ROUTE spine BUILT note)
  - design-substrate/Spec_Control_Plane_v1_51.md (the paired CP delta — the new WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS value the §14.22.8 ambiguous case routes to)
  - design-substrate/Spec_Harness_Runtime_v1.md (§14.22 v1.60 the fence carrier + §14.22.7 the registered follow-on this BUILDS; §14.23 B-ENGINE-OUTPUT-REPLAY the probe debunked as the output source)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - advisor (full-transcript) — vetted the build BEFORE code; surfaced + settled the enum-layer correction (the pause-reason homes in WorkflowPauseReason C-CP-26 §26.2, NOT the engine-layer §22.1 PauseReason the fork doc framed — the capture_pause_snapshot signature settled it); confirmed the crux ('the prior output' was never persisted → the arc MUST add its own capture); caught the byte-identical-string caveat (unbound → FAILED, but the fail_class string differs → claim "behaviorally equivalent" not "byte-identical"); confirmed capture-after-validation + retry-breaker no-change + the driver name-match pattern
  - out-of-family Codex (decorrelated, 2 rounds) — pre-merge on the diff; both [P2] reconciled: (a) the suppress path skipped `sandbox.exit` (enter-without-exit telemetry gap; advisor concurred Codex was right over advisor's earlier "correct") → FIXED + span-test; (b) the ambiguous PAUSE was capture-not-resolution (a naive resume re-pauses) → (B) partial-land + registered follow-on `B-EFFECT-FENCE-PAUSE-RESOLUTION` + interim re-pause test + over-claim language corrected
  - operator AskUserQuestion 2026-06-22 — AUTHORIZED B-EFFECT-FENCE-HITL-ROUTE over the other 2 gated arcs + the quality track (the committed-behavior gate)
  - standing FULL-SPEC operator directive 2026-06-12 (design back-flow pre-authorized)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.72`

v1.72 is the runtime half of the R-FS-1 standalone arc **`B-EFFECT-FENCE-HITL-ROUTE`** (operator-AUTHORIZED via AskUserQuestion 2026-06-22). It refines the v1.60 §14.22 C-RT-31 effect fence's interim fail-closed posture into the genuine HITL-routed two-case split the §14.22.7 follow-on named, via the NEW **§14.22.8**.

**What changed (the committed-behavior relaxation).** The fence gains post-fire / pre-commit durable output capture (`capture_output`/`read_output`, the same crash-atomic `O_EXCL`/`os.link` primitive + per-(run, step, tool) digest keying as `try_reserve`). A lost-reserve re-dispatch SPLITS: output **present** → suppress-and-continue (return the captured output, never re-fire); output **absent/corrupt** → raise `EffectFenceAmbiguousUncommittedError` (renamed from `EffectFenceReservedUncommittedError`, whose sole raise site the split replaces). The driver name-matches the ambiguous error and routes it to a §26.2 `WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS` PAUSE (bound `PauseResumeProtocol`) else FAILED.

**The crux (advisor-sharpened).** The v1.60 §14.22.7 entry deferred suppress-and-continue to `B-ENGINE-OUTPUT-REPLAY`, but the 2026-06-22 probe found replay cannot supply it (only a `response_hash` digest + a `resume_at`-driven rehydrate that ignores the suppressed step's own output). So this arc adds its OWN output substrate at the fence — atomic, so present ⟹ complete-and-valid; a present-but-corrupt output fail-closes to PAUSE, never a valid suppress source.

**The enum-layer correction (advisor + primary source).** The fork doc verification 1 framed the new pause-reason as the engine-layer §22.1 `PauseReason`; primary-source grounding of the `capture_pause_snapshot` signature corrected it — the driver-routed pause is `WorkflowPauseReason`-typed (C-CP-26 §26.2). The §22.1 enum is the engine-native replay-pause substrate the driver never calls here. The new value homes in `WorkflowPauseReason` only.

**Gate posture.** The operator AUTHORIZED the committed-behavior change (relaxing the fence's load-bearing fail-closed + minting a new pause-reason) at AskUserQuestion 2026-06-22, over the other 2 gated arcs + the quality track. Otherwise additive/impl: **no** new fail-class taxonomy code, **no** §5.2-hash change, **no** `StepDispatcher` Protocol widening, **no** new CXA edge (the driver's `PAUSE_CAPTURED` CP→IS emission reuses the existing seam with `event_kind_index=3`).

Reviewed during clearance (verified by execution): dispatcher-level suppress-and-continue (re-dispatch returns the captured output, the counting tool fires EXACTLY ONCE), ambiguous-absent + ambiguous-corrupt raises (no re-fire), durable suppress across a process restart, the 6 fence-gate tests re-asserted via the at-most-once fire-count signal; driver-level ambiguous → PAUSED (bound) / FAILED (unbound) on the linear/TOOL_STEP path; retry-breaker verbatim re-raise of the renamed error. harness-runtime non-e2e 2030 passed; pyright 0/0/0. Cross-axis suites (harness-cp 1167+1xfail, harness-od 950, harness-cxa 28) confirm the rename + the WorkflowPauseReason 6th member did not ripple to any cardinality or golden-hash assertion outside the updated `test_pause_resume_protocol_types.py`.

## Notes

- Phase 7 consumers may rely on this version as canonical after the bundled harness-runtime + harness-cp impl + tests land together (`merge_commit` pinned at the post-merge refresh).
- Paired CP clearance: `.harness/clearance/Spec_Control_Plane-v1_51-cleared-2026-06-22.md`.
