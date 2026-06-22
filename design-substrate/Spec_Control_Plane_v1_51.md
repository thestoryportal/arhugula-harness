# Spec: Control Plane — v1.51 (delta over v1.50)

---

## Change-note (v1.50 → v1.51)

**Scope of revision.** A single additive enum member at **C-CP-26 §26.2**: `WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS = "effect_fence_ambiguous"`. This is the **CP half** of the R-FS-1 standalone arc **`B-EFFECT-FENCE-HITL-ROUTE`** (registered at `.harness/beyond-mvp-capability-boundary-ledger.md`; operator-AUTHORIZED via AskUserQuestion 2026-06-22 over the other gated arcs + the quality track). The paired **runtime half** (the §14.22 C-RT-31 effect fence's two-case split — post-fire output capture + suppress-and-continue / ambiguous-PAUSE — and the `workflow_driver` name-match routing branch) lands in the co-published runtime spec **v1.71 → v1.72** delta (§14.22.8).

**The problem this value names.** The runtime effect fence (§14.22) at-most-once-execution guarantee fail-closes a lost-reserve re-dispatch. v1.72 relaxes that into a two-case split: an effected-but-uncommitted step whose validated output WAS captured suppress-and-continues; one whose output is ABSENT or CORRUPT (a crash in the fire→capture window) is genuinely ambiguous and must be handed to the operator as a resumable PAUSE rather than auto-re-fired. The driver routes that ambiguous case through the existing `PauseResumeProtocol.capture_pause_snapshot(...)` path, which is typed to `WorkflowPauseReason` — so the ambiguous-fence pause needs its own member in that enum.

**The pause-reason home — §26.2 (C-CP-26 `WorkflowPauseReason`), NOT §22.1 (C-CP-22 `PauseReason`).** The two pause-reason enums occupy distinct architectural layers per the v1.11 §26 NEW NOTE coexistence (and the operator-ratified path γ disambiguation, `.harness/class_1_fork_u_cp_63_pause_reason_collision.md`): C-CP-22 §22.1 `PauseReason` is the ENGINE-native replay-pause taxonomy (U-CP-49 surface); C-CP-26 §26.2 `WorkflowPauseReason` is the WORKFLOW-DRIVER explicit/material-diff pause taxonomy that `capture_pause_snapshot` + `PauseSnapshot.pause_reason` are typed to. The effect-fence ambiguous pause is **driver-detected and driver-routed** (the driver catches the runtime signal at the step-dispatch boundary and calls `capture_pause_snapshot`), exactly as a driver-detected HITL pause uses `WorkflowPauseReason.HITL_PENDING` (not the engine-layer `PauseReason.HITL_INVOCATION_PENDING`). So the new value homes in `WorkflowPauseReason` ONLY; adding it to the engine-layer `PauseReason` would be dead. *(This corrects the fork doc `.harness/class_1_fork_effect_fence_hitl_route.md` verification 1, which framed the home as §22.1 — primary-source grounding of the `capture_pause_snapshot` signature settled it the other way; advisor + the type signature concur.)*

**Additive, no committed invariant sacrificed.** The new member is purely additive to a `StrEnum` — every existing `WorkflowPauseReason` value + its semantics are byte-unchanged; the two enums remain value-disjoint (`effect_fence_ambiguous` collides with no engine-layer `PauseReason` value). It mints no new contract, ADR, fail-class, manifest field, or CXA edge. OD ingests `pause_reason` as a serialized string (`str | None`, no closed-enum enforcement), so the new value flows through the audit/observability path without an OD-spec change. The driver's `PAUSE_CAPTURED` CP→IS emission reuses the existing seam with `event_sequence_id = (step_index << 2) | 3` (the effect-fence disambiguator, distinct from the drain-flag [=1] + HITL-signal [=2] paths). What the operator GATED-and-RATIFIED is the runtime-side relaxation of the fence's fail-closed (the committed-behavior change); this CP delta carries only the value that relaxation routes to.

**v1.50 + prior body PRESERVED VERBATIM.** All v1.50 content — the §6.2 `model_binding_override` signal + the entire C-CP-01 … C-CP-29 body incl. §26.1/§26.3–§26.8 — is PRESERVED VERBATIM per the delta-only-spec-file convention. The only change is the additive `WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS` member at §26.2; the other five members (`EXPLICIT_OPERATOR` / `HITL_PENDING` / `VALIDATOR_ESCALATION` / `TIMEOUT_BOUNDARY` / `EXTERNAL_DEPENDENCY`) are PRESERVED VERBATIM.

---

## §1 — Amended C-CP-26 §26.2 `WorkflowPauseReason` — new effect-fence-ambiguous member

`WorkflowPauseReason` gains one additive member (the 6th; the 5 v1.11 members are unchanged):

> **`WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS = "effect_fence_ambiguous"` (NEW at v1.51).** The runtime effect fence (§14.22 C-RT-31) lost a reserve to a prior uncommitted attempt of a non-idempotent effect AND found no captured output proving completion (the crash fell in the fire→capture window). Whether the effect fired is ambiguous, so the runtime fails to the operator rather than auto-re-fire (the at-most-once guarantee). System-triggered, driver-routed: the runtime raises `EffectFenceAmbiguousUncommittedError`, the workflow driver name-matches it at the linear/TOOL_STEP step-dispatch boundary (harness-cp cannot import harness-runtime — the `HITLPauseRequestedSignal` precedent) and, when a `PauseResumeProtocol` is bound, calls `capture_pause_snapshot(pause_reason=WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS)` → `RunStatus.PAUSED`. When unbound, the ambiguous error falls through to the generic FAILED mapping (behaviorally equivalent to the pre-v1.72 fail-closed: FAILED, no auto-re-fire; only the `fail_class` string differs). The PAUSE is a labeled, non-terminal, operator-SURFACED capture (a strict improvement over the terminal FAILED); the resume-side RESOLUTION (operator `skip-as-fired` / `re-fire` / `abort`) is the registered runtime follow-on `B-EFFECT-FENCE-PAUSE-RESOLUTION` — until it lands a naive resume re-pauses identically (INERT — resume is caller-initiated).

`WorkflowPauseReason` remains distinct from the engine-layer C-CP-22 §22.1 `PauseReason` (path γ disambiguation); the two member-value sets remain fully disjoint.

---

## §2 — Status

Additive `WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS` member (the CP half of the FULL-SPEC-pre-authorized, operator-AUTHORIZED R-FS-1 standalone arc `B-EFFECT-FENCE-HITL-ROUTE`). The value is what the runtime §14.22.8 two-case split's ambiguous case routes to via the driver's `capture_pause_snapshot` path.

**Operator-AUTHORIZED arc; additive CP value.** The committed-behavior change (relaxing the §14.22 fence's load-bearing fail-closed into the two-case split + minting a new pause-reason) was operator-AUTHORIZED at AskUserQuestion 2026-06-22 over the other gated arcs + the quality track. The CP enum member itself is additive and sacrifices no committed invariant: every existing `WorkflowPauseReason` value is byte-unchanged; the two pause-reason enums stay value-disjoint; no new contract / ADR / fail-class / manifest field / CXA edge; OD ingests the serialized string with no closed-enum change.

Apply pass: this delta co-published with harness-cp impl (`WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS` + the `workflow_driver` name-match PAUSE branch) + the paired runtime spec v1.72 delta + harness-runtime impl (the §14.22 fence `capture_output`/`read_output` + the rename + the dispatcher two-case split) + by-execution tests (CP: 6-class cardinality + driver-level ambiguous → PAUSED [bound] / FAILED [unbound]; runtime: dispatcher-level suppress-and-continue + ambiguous-absent/corrupt + durable suppress across restart + retry-breaker verbatim re-raise) + clearance markers + spine-ledger registration, per workspace `CLAUDE.md` §11.4 bundled-absorption.

v1.50 + earlier PRESERVED VERBATIM per delta-only-spec-file convention. The entire C-CP-01 … C-CP-29 body + §5.x + §6.x + §16.5.x + §25.x + §26.1/§26.3–§26.8 PRESERVED VERBATIM (the only change: the additive §26.2 `EFFECT_FENCE_AMBIGUOUS` member). IS spec UNCHANGED (no §5.2 hash-recipe change). OD spec UNCHANGED (`pause_reason` ingested as `str | None`). CXA v2.20 UNCHANGED (no new typed edge). ADR-F1/F2/F3/D1–D6 UNCHANGED. ADD v1.3 + PRD v1.1 UNCHANGED. Paired runtime spec v1.71 → v1.72.

Clearance marker filed at `.harness/clearance/Spec_Control_Plane-v1_51-cleared-2026-06-22.md`.

2026-06-22.
