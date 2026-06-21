---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.67
cleared_at: 2026-06-21T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-spine-ledger (NO operator gate — change-note-level amendment marking §14.22.7's registered follow-on B-EFFECT-FENCE-DURABLE-AUTO BUILT + one hash-inert StepExecutionContext.run_engine_class field: the §14.22 C-RT-31 effect fence now auto-activates per-run for durable-execution engine classes via a per-dispatch gate on the RUN engine class (step_context.run_engine_class), no operator effect_fencing opt-in needed; additive, non-durable runs stay fence-free)
back_reference:
  - .harness/beyond-mvp-capability-boundary-ledger.md (B-EFFECT-FENCE-DURABLE-AUTO spine BUILT note)
  - design-substrate/Spec_Harness_Runtime_v1.md (v1.60 — the §14.22 C-RT-31 RuntimeEffectFence contract this arc auto-activates; v1.60 §14.22.7 explicitly registered this follow-on + named the mechanism; PRESERVED VERBATIM)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - advisor (full-transcript) — confirmed B-EFFECT-FENCE-DURABLE-AUTO (the only impl-to-cleared-spec candidate of the three; clean-first selects it); steered the ONE genuine fork — use the PER-RUN RESERVE GATE (engine class from the per-dispatch step_context), NOT factory threading (the dispatcher is a daemon-reused singleton across runs with different engine_classes; caching the engine class would leak cross-run); flagged the durable-set as impl-discretion + the hash-inert StepExecutionContext-field requirement (verified hash-inert; the new run_engine_class field rides it)
  - out-of-family Codex [P2] (decorrelated) — caught that the first impl's gate on the per-step `binding.engine_class` would let a per-step `StepOverride.engine_class` disable the run-level fence; re-keyed onto `step_context.run_engine_class` (the run engine class governing resume) + added a regression witness
  - standing FULL-SPEC operator directive 2026-06-12 (design back-flow pre-authorized; no operator gate owed)
  - out-of-family Codex review at the impl-diff PR (decorrelated; <pending>)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.67`

v1.67 is a change-note-level additive amendment absorbing the **R-FS-1 standalone arc `B-EFFECT-FENCE-DURABLE-AUTO`**. It marks the §14.22.7 registered follow-on BUILT: the §14.22 C-RT-31 `RuntimeEffectFence` now auto-activates per-run for durable-execution engine classes, removing the operator `RuntimeConfig.effect_fencing=True` opt-in for the common durable case.

**The build (per-run reserve gate — the spec's named mechanism).** The stage-5 factory constructs the fence UNCONDITIONALLY (lazy claim dir → no footprint until a reserve fires). The dispatcher carries a NEW `effect_fencing_explicit` flag (the operator opt-in) and gates the per-dispatch reserve on `effect_fencing_explicit OR step_context.run_engine_class ∈ durable-set`. The per-run engine class arrives on a NEW hash-inert `StepExecutionContext.run_engine_class` field, set by the CP driver from `manifest_entry.engine_class` at every step-context composition site (the `hitl_placements` producer precedent) — NOT cached on the daemon-reused dispatcher singleton (it travels with the per-dispatch `step_context`). The advisor steered AWAY from the spec's other named option ("thread the engine class to the factory") for exactly that daemon-reuse reason.

**Out-of-family Codex [P2] — the channel correction (decorrelated catch).** The first impl gated on `binding.engine_class` (the per-step effective binding). Codex caught that `resolve_step_binding` resolves `override.engine_class or manifest_entry.engine_class`, so a per-step `StepOverride.engine_class=PURE_PATTERN_NO_ENGINE` on a DURABLE workflow would make `binding.engine_class` non-durable → the gate would wrongly SKIP the fence for a step the RUN still resumes + re-dispatches (a crash-after-effect / before-ledger-commit double-fire window). The fix re-keys the gate onto the RUN engine class (`step_context.run_engine_class` = `manifest_entry.engine_class`), which is what governs resume. A dedicated regression witness (`test_effect_fence_gates_on_run_not_per_step_override`) proves a durable run with a per-step non-durable override STILL fences.

**Durable-set reading (impl-discretion).** §14.22.7 defines "durable" as "a resume re-dispatches uncommitted steps" without enumerating. The impl reads the durable-auto-fence set as `{SAVE_POINT_CHECKPOINT, EVENT_SOURCED_REPLAY, WAL_SEGMENT, RECONCILER_LOOP}`, EXCLUDING `PURE_PATTERN_NO_ENGINE` (the "no-engine" baseline = the spec's "non-durable run" carve-out). A strict improvement over the pre-v1.60 all-opt-in default (no regression: the 4 real durable engines move opt-in → auto-on; pure-pattern is unchanged + can still opt in via the explicit flag).

**NO operator gate.** Additive; sacrifices no committed invariant; non-durable runs stay fence-free unless `effect_fencing=True`. No new contract, no new fail-class, no §5.2-hash change (`effect_fencing_explicit` + the new `StepExecutionContext.run_engine_class` are runtime-/driver-internal + hash-inert). CP spec UNCHANGED (`run_engine_class` rides the existing CP `StepExecutionContext` carrier, set from the existing `manifest_entry.engine_class`). The §14.22 C-RT-31 contract carrier is PRESERVED VERBATIM.

Reviewed during clearance (verified by execution): a durable engine class auto-fences without the opt-in (a re-dispatch of the same effect fail-closes `EffectFenceReservedUncommittedError`); a non-durable run stays fence-free (both dispatches succeed, no claim); the explicit opt-in still fences every tool step. The fence claim dir is created lazily, so the always-construct change leaves no footprint for never-reserving runs (the factory default test asserts the fence is present + `effect_fencing_explicit is False`).

## Notes

- Phase 7 consumers may rely on this version as canonical after the bundled harness-runtime impl + tests land together (`merge_commit` pinned at the post-merge refresh).
