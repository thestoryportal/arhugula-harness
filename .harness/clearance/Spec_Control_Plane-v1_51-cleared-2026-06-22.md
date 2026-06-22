---
artifact: design-substrate/Spec_Control_Plane_v1_51.md
version: v1.51
cleared_at: 2026-06-22T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-spine-ledger (additive enum member — the CP half of B-EFFECT-FENCE-HITL-ROUTE. Adds `WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS = "effect_fence_ambiguous"` at C-CP-26 §26.2 — the value the runtime §14.22.8 two-case split's ambiguous case routes to via the driver's `capture_pause_snapshot` path. Homes in WorkflowPauseReason [C-CP-26 §26.2, the workflow-driver pause taxonomy capture_pause_snapshot + PauseSnapshot.pause_reason are typed to], NOT the engine-layer §22.1 PauseReason [path γ disambiguation; the driver-detected/driver-routed pause uses WorkflowPauseReason exactly as a HITL pause uses HITL_PENDING, not the engine HITL_INVOCATION_PENDING]. The committed-behavior GATE — the runtime relaxation of the fence's fail-closed — was operator-AUTHORIZED by AskUserQuestion 2026-06-22; this CP value is additive. The two pause-reason enums stay value-disjoint. OD ingests pause_reason as str|None → no OD-spec change. No new contract / ADR / fail-class / manifest field / CXA edge / §5.2 hash change.)
back_reference:
  - .harness/class_1_fork_effect_fence_hitl_route.md (the advisor-vetted design proposal the operator authorized; verification 1's §22.1→§26.2 pause-reason-home corrected by primary-source grounding of the capture_pause_snapshot signature)
  - .harness/beyond-mvp-capability-boundary-ledger.md (B-EFFECT-FENCE-HITL-ROUTE spine BUILT note)
  - design-substrate/Spec_Harness_Runtime_v1.md (the paired runtime v1.72 delta — §14.22.8 the two-case split + output-capture substrate; the PRODUCER of the EffectFenceAmbiguousUncommittedError this value routes)
  - design-substrate/Spec_Control_Plane_v1_50.md (the immediately-prior head — B-MODEL-RESOLUTION-CONSOLIDATION CP half; PRESERVED VERBATIM)
  - .harness/class_1_fork_u_cp_63_pause_reason_collision.md (the path γ WorkflowPauseReason ↔ engine-layer PauseReason disambiguation this new member respects)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - advisor (full-transcript) — settled the enum-layer home (WorkflowPauseReason §26.2, NOT §22.1) against the fork doc's framing, via the capture_pause_snapshot type signature; confirmed the additive member breaks nothing (the two enums stay value-disjoint; OD ingests str|None)
  - out-of-family Codex (decorrelated, 2 rounds) — pre-merge on the diff; both [P2] reconciled (the suppress-path sandbox.exit telemetry gap + the capture-not-resolution partial-land → registered follow-on B-EFFECT-FENCE-PAUSE-RESOLUTION)
  - operator AskUserQuestion 2026-06-22 — AUTHORIZED B-EFFECT-FENCE-HITL-ROUTE (the committed-behavior gate the runtime relaxation carries; this CP value is additive)
  - standing FULL-SPEC operator directive 2026-06-12 (design back-flow pre-authorized)
supersedes:
superseded_by:
---

# Clearance — `Spec_Control_Plane v1.51`

v1.51 is an additive delta over v1.50 absorbing the **CP half** of the R-FS-1 standalone arc **`B-EFFECT-FENCE-HITL-ROUTE`** (operator-AUTHORIZED via AskUserQuestion 2026-06-22). It adds a single enum member — `WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS = "effect_fence_ambiguous"` — at **C-CP-26 §26.2**.

**Why the value is needed.** The runtime §14.22.8 two-case split (v1.72) routes an ambiguous lost-reserve re-dispatch (effect fired-or-not, no captured output) to a resumable PAUSE through the driver's `PauseResumeProtocol.capture_pause_snapshot(...)` path. That method + `PauseSnapshot.pause_reason` are typed to `WorkflowPauseReason`, so the ambiguous-fence pause needs its own member there.

**The pause-reason home — §26.2, NOT §22.1 (the fork-doc verification 1 correction).** The two pause-reason enums occupy distinct layers (path γ disambiguation, `.harness/class_1_fork_u_cp_63_pause_reason_collision.md`): C-CP-22 §22.1 `PauseReason` is the ENGINE-native replay-pause taxonomy; C-CP-26 §26.2 `WorkflowPauseReason` is the WORKFLOW-DRIVER pause taxonomy the driver's `capture_pause_snapshot` is typed to. The effect-fence ambiguous pause is driver-detected + driver-routed, exactly like a driver-detected HITL pause (which uses `WorkflowPauseReason.HITL_PENDING`, not the engine `HITL_INVOCATION_PENDING`). So the new value homes in `WorkflowPauseReason` only; the fork doc's §22.1 framing was corrected by primary-source grounding of the `capture_pause_snapshot` signature (advisor + the type signature concur).

**Gate posture.** The committed-behavior change (the runtime relaxation of the fence's fail-closed) was operator-AUTHORIZED at AskUserQuestion 2026-06-22; this CP delta carries only the additive value that relaxation routes to. The member is purely additive to a `StrEnum`: every existing value + semantics byte-unchanged; the two enums stay value-disjoint (`effect_fence_ambiguous` collides with no engine-layer value); OD ingests `pause_reason` as `str | None` (no closed-enum change). No new contract / ADR / fail-class / manifest field / CXA edge / §5.2 hash change.

Reviewed during clearance (verified by execution): the `WorkflowPauseReason` 6-class cardinality + member-value/name + the two-enum-disjoint regression gates (`test_pause_resume_protocol_types.py`, updated 5→6); the driver-level routing (`test_workflow_driver_effect_fence_pause.py` — ambiguous → PAUSED with `pause_reason is EFFECT_FENCE_AMBIGUOUS` [bound] / FAILED with the error-named fail_class [unbound], on the linear/TOOL_STEP path). harness-cp 1167 passed / 1 xfailed; pyright 0/0/0. Cross-axis suites (harness-runtime non-e2e 2030, harness-od 950, harness-cxa 28) confirm the 6th member did not ripple to any cardinality or golden-hash assertion (OD's `pause_reason: str | None` ingestion is value-agnostic).

## Notes

- Phase 7 consumers may rely on this version as canonical after the bundled harness-cp + harness-runtime impl + tests land together (`merge_commit` pinned at the post-merge refresh).
- Paired runtime clearance: `.harness/clearance/Spec_Harness_Runtime-v1_72-cleared-2026-06-22.md`.
