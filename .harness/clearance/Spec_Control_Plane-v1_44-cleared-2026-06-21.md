---
artifact: design-substrate/Spec_Control_Plane_v1_44.md
version: v1.44
cleared_at: 2026-06-21T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-spine-ledger (NO operator gate — one additive C-CP-26 §26.2 carrier `PeerFanOutResumeState` + one additive `PauseSnapshot.peer_fan_out_resume` field materializing the cleared §25.15.1 `pause → PAUSED` row for PARALLELIZATION; additive + opt-in, existing snapshots byte-identical)
back_reference:
  - .harness/beyond-mvp-capability-boundary-ledger.md (B-FANOUT-PAUSE-PARALLELIZATION spine BUILT note)
  - design-substrate/Spec_Control_Plane_v1_42.md (§25.15.1 `pause → PAUSED` row + the `FanOutResumeState` / `FanOutBranchResumeState` / `PauseSnapshot.fan_out_resume` ORCHESTRATOR_WORKERS precedent this peer-fan-out arc mirrors; PRESERVED VERBATIM)
  - design-substrate/Spec_Control_Plane_v1_43.md (the immediately-prior head — B-LAYER-BUDGET-OVERRIDE §2.5.3 amendment; PRESERVED VERBATIM)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - advisor (full-transcript) — confirmed the pick + classification (impl-to-cleared-spec, no operator gate), steered the carrier fork to Option B (a NEW `PeerFanOutResumeState`, NOT a loosened `FanOutResumeState` — illegal-states-unrepresentable: loosening the orchestrator fields to optional would make `orchestrator_output=None` representable for an ORCHESTRATOR_WORKERS snapshot), prescribed the second-additive-field route over a union, and named the 5 carried correctness items (resumed-terminal PARTIAL; recovered-output→aggregate fold; re-keyed material-diff guard; drop `pause_resumable`; full-chain witness)
  - standing FULL-SPEC operator directive 2026-06-12 (design back-flow pre-authorized; no operator gate owed)
  - out-of-family Codex review at the impl-diff PR (decorrelated; pending)
supersedes:
superseded_by:
---

# Clearance — `Spec_Control_Plane v1.44`

v1.44 is an additive delta over v1.43 absorbing the **R-FS-1 standalone arc `B-FANOUT-PAUSE-PARALLELIZATION`**. It adds one C-CP-26 §26.2 carrier (`PeerFanOutResumeState` — the `PARALLELIZATION` peer-fan-out analogue of the v1.42 `FanOutResumeState`, with `branches` + `branch_count` and NO orchestrator fields) + one additive `PauseSnapshot.peer_fan_out_resume` field, materializing the cleared **§25.15.1 `pause → PAUSED`** row for the PARALLELIZATION topology (the v1.42 `B-FANOUT-PAUSE` arc materialized it for ORCHESTRATOR_WORKERS). The interim `parallelization-pause-resume-not-yet-materialized` FAILED flips to a genuine resumable PAUSED.

**Prerequisite satisfied:** the `B-PARALLELIZATION-CASCADE` arc (PR #678) built the cascade_policy harvest this resume builds on — PARALLELIZATION had NO cascade machinery before that arc.

**NO operator gate.** The §25.15.1 row already commits, byte-exact, `pause → PAUSED` "composing with C-CP-26 PauseResumeProtocol + C-RT-35 `api.resume`", and §25.15.2 obligation 7 already commits ledger-based resume reconstruction; the only thing missing was the carrier shape. This materializes the R-CC-1 design §1.1 re-open trigger (a self-documented MVP scoping note that explicitly anticipates the fan-out working-state extension) — NOT a forbidding-invariant sacrifice (contrast B4-Slice-4's runtime §14.5.3 inv-2 *role* relaxation, which gated). Additive + opt-in (PAUSED only when a `pause_resume_protocol` is bound; else honest FAILED + `...-protocol-not-bound`); `snapshot_hash` extended (strengthens §26.6 invariant 2); existing snapshots byte-identical; no new ADR / enum / CXA edge / manifest field.

**Carrier fork resolved in-impl (advisor, NOT operator).** Option A (loosen `FanOutResumeState`'s orchestrator fields to optional + reuse) was rejected: it makes `orchestrator_output=None` representable for an ORCHESTRATOR_WORKERS snapshot — an illegal state for that strategy — and forces the existing resume-body-mismatch guard to defend a `None`. Option B (a NEW 2-field peer carrier) keeps each strategy's resume state exactly as constrained as its domain. A reversible in-impl design choice, not an operator scoping call.

Reviewed during clearance: the new field is additive + defaulted (every existing `PauseSnapshot` — linear, single-step, ORCHESTRATOR_WORKERS fan-out — composes + validates byte-identically; the hash key is added only when the field is non-`None`); the honest no-false-PAUSED bar is preserved (PAUSED only with a bound protocol; else FAILED); the resumed-terminal PARTIAL semantic forecloses a silent SUCCESS dropping a recovered branch's failure; the material-diff guard is re-keyed (branch_count + per-branch `step_id` over `steps`, NO orchestrator-identity check); the full-chain witness drives real `execute_workflow → pause → PAUSED → api.resume → re-dispatch survivors → aggregate` through the real RuntimeLLMDispatcher (CP `test_workflow_driver_parallelization_pause.py` + runtime `test_b_fanout_pause_parallelization_resume_e2e.py`), with a tampered-recovered-output integrity negative control + an empty-branches recovery-loss negative control + an opt-out (no protocol) honest-FAILED control.

## Notes

- Phase 7 consumers may rely on this version as canonical after the bundled harness-cp + harness-runtime impl + tests land together (`merge_commit` pinned at the post-merge refresh).
