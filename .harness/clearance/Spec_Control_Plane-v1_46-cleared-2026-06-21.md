---
artifact: design-substrate/Spec_Control_Plane_v1_46.md
version: v1.46
cleared_at: 2026-06-21T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-spine-ledger (NO operator gate — two additive C-CP-26 §26.2 carriers `HandoffResumeState` + `HandoffStageResumeState` + one additive `PauseSnapshot.handoff_resume` field, materializing the §25.15.1 `pause → PAUSED` disposition EXTENDED to single-owner sequential per §25.18's named DECENTRALIZED_HANDOFF impl-order; additive + opt-in, existing snapshots byte-identical via drop-when-None hashing)
back_reference:
  - .harness/beyond-mvp-capability-boundary-ledger.md (B-HANDOFF-PAUSE spine BUILT note)
  - design-substrate/Spec_Control_Plane_v1_45.md (the immediately-prior head — B-HIERARCHICAL-PAUSE; PRESERVED VERBATIM; its §2 DECENTRALIZED_HANDOFF forward-arc line corrected here)
  - design-substrate/Spec_Control_Plane_v1_44.md (§25.15.1 `pause → PAUSED` + the `PeerFanOutResumeState` per-strategy-carrier precedent this arc follows; PRESERVED VERBATIM)
  - design-substrate/Spec_Control_Plane_v1_32.md (§25.15.1 fan-out-barrier-scoped pause row + §25.18 "deferred to implementation discretion" — names DECENTRALIZED_HANDOFF as the LAST strategy in the simplest→hardest impl order this arc materializes; PRESERVED VERBATIM)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - advisor (full-transcript) — confirmed B-HANDOFF-PAUSE (impl-to-cleared-spec) over the EO fork-first arc (EO is sequential with NO cascade_policy / NO pause trigger; pairing them would be parking-dressed-as-decomposition); SHARPENED the cite-precision gap that §25.15.1's pause row is fan-out-barrier-scoped so HANDOFF is an EXTENSION not verbatim coverage (the §2 framing owns this); named the load-bearing witness (completed prefix recovered-not-re-executed AND the resumed stage's parent_action_id chains off the last completed stage's action_id, NOT the workflow origin); flagged the invariant check (none forbids a single-owner resumable pause)
  - standing FULL-SPEC operator directive 2026-06-12 (design back-flow pre-authorized; no operator gate owed)
  - out-of-family Codex review at the impl-diff PR (decorrelated; <pending>)
supersedes:
superseded_by:
---

# Clearance — `Spec_Control_Plane v1.46`

v1.46 is an additive delta over v1.45 absorbing the **R-FS-1 standalone arc `B-HANDOFF-PAUSE`**. It adds two C-CP-26 §26.2 carriers (`HandoffResumeState` — a single-owner sequential STAGE CURSOR; `HandoffStageResumeState` — one completed stage of the contiguous prefix, carrying its recovered output) and one additive `PauseSnapshot.handoff_resume` field, materializing the **§25.15.1 `pause → PAUSED`** disposition **EXTENDED to the single-owner sequential case** for the `DECENTRALIZED_HANDOFF` topology. This completes the resumable-pause family across all five non-linear strategies (ORCHESTRATOR_WORKERS v1.42, PARALLELIZATION v1.44, HIERARCHICAL_DELEGATION v1.45, DECENTRALIZED_HANDOFF v1.46); only the sequential `EVALUATOR_OPTIMIZER` iteration-cursor (a fork-first arc) remains.

**The §25.15.1 EXTENSION (not verbatim coverage) — the framing the advisor sharpened.** Unlike the v1.42/v1.44 fan-out materializations, §25.15.1's pause row is fan-out-barrier-scoped ("Halt the **fan-out**…"), and `DECENTRALIZED_HANDOFF` is explicitly NOT a fan-out barrier (single-owner sequential; `cascade_policy` "degenerate for single-owner"). So this arc EXTENDS the row's `pause → PAUSED` disposition to the single-owner sequential case. The authority is **§25.18** (PRESERVED VERBATIM), which defers the per-strategy materialization to implementation discretion ("Deferred to implementation discretion … NOT design holes") and names `DECENTRALIZED_HANDOFF` as the **LAST strategy in the simplest→hardest impl order**. No committed invariant forbids a single-owner resumable pause (C-CP-26 + C-RT-30 are topology-agnostic); the existing handoff executor already resolved `cascade_policy` (TEAM→pause) — only the carrier + resume re-entry were missing. The §2 change-note owns the extension explicitly (the first-draft "verbatim coverage" claim was corrected).

**The handoff causality chain is the load-bearing correctness.** On resume the executor RE-WALKS the body: the completed prefix's outputs are RECOVERED (replayed, NOT re-dispatched — effect may have landed), and because each stage's context + `action_id` is recomputed DETERMINISTICALLY through the prefix, the resumed stage's `parent_action_id` chains off the LAST COMPLETED stage's `action_id` — NOT re-anchored to the workflow origin. The chain is INHERENT in the recompute, not a carried string that could drift. The discriminating witness (`test_workflow_driver_handoff_pause.py`) asserts (a) the completed prefix's dispatcher is NEVER re-invoked across pause+resume, AND (b) the resumed stage's `parent_action_id` equals the clean-run chain anchor and is NOT the origin.

**NO operator gate.** Additive carriers + field + opt-in (PAUSED only with a bound `pause_resume_protocol`; else honest FAILED + `decentralized-handoff-pause-resume-protocol-not-bound`, salvaging the prefix — the detect-then-refuse mirror of `_execute_parallelization`); `snapshot_hash` extended (covers `handoff_resume` when present, DROPPED when None so every pre-arc snapshot is byte-identical); no new ADR / enum / CXA edge / manifest field.

**Carrier shape resolved in-impl (NOT operator) — `[[fanout-pause-per-strategy-carrier]]`.** A dedicated stage-cursor carrier (a CONTIGUOUS completed prefix), NOT a loosened fan-out carrier (a branch set with re-dispatchable gaps): a handoff resume has no orchestrator output, no peer-branch set, and no absent-ordinal gap, so reusing the fan-out carriers would make illegal states representable for those strategies. A reversible in-impl design choice.

Reviewed during clearance (verified by execution): the hash covers the recovered prefix outputs (a tampered output fails the parent resume recompute → `CP-FAIL-PAUSE-SNAPSHOT-CORRUPTION`) AND preserves byte-compat for pre-arc snapshots (drop-when-None); the resume material-diff guard fails closed on stage-count mismatch, stage-identity mismatch, non-contiguous prefix, and non-strict prefix; the handoff path dispatches through the ordinary `StepDispatcher` (never `SUB_AGENT_DISPATCH`), so NO runtime dispatcher change is needed (unlike the v1.45 HIERARCHICAL child-pause); the discriminating full-chain witness drives the real `execute_workflow(pause_snapshot_input=...)` resume path (CP) AND the full-runtime `api.resume` with a JSON round-trip (runtime `test_b_handoff_pause_resume_e2e.py`), both asserting the completed prefix is recovered exactly once.

## Notes

- Phase 7 consumers may rely on this version as canonical after the bundled harness-cp impl + tests land together (`merge_commit` pinned at the post-merge refresh).
- The root / harness-cp `CLAUDE.md` §2.3 / §1.2 spec-head pointers remain at v1.38 (a pre-existing drift untouched by the v1.39–v1.46 delta arcs; left as-is per surgical-changes — the spec-file head is the canonical authority).
