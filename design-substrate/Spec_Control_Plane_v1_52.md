# Spec: Control Plane — v1.52 (delta over v1.51)

---

## Change-note (v1.51 → v1.52)

**Scope of revision.** Additive type carriers + two additive model fields at **C-CP-26** for the resume-side resolution of the §26.2 `WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS` pause: a new `EffectFenceResolution` 3-value enum (§26.8.2), a new `EffectFenceResumeState` carrier (§26.2), a new `EffectFenceResolutionDirective` (§26.8.2), the additive `ResumeContext.effect_fence_resolution` field (§26.8), and the additive `PauseSnapshot.effect_fence_resume` field (§26.2). This is the **CP half** of the R-FS-1 standalone arc **`B-EFFECT-FENCE-PAUSE-RESOLUTION`** (registered at `.harness/beyond-mvp-capability-boundary-ledger.md`; **BUILD-not-gate** — the #702 registration's "operator-gated" label flipped at design-vet, advisor-concurred; design vetted at `.harness/class_1_fork_effect_fence_pause_resolution.md`). The paired **runtime half** (the §14.22 C-RT-31 fence's `clear_claim` + the dispatcher three-branch resolution split + the hash-inert `StepExecutionContext.effect_fence_resolution` channel) lands in the co-published runtime spec **v1.72 → v1.73** delta (§14.22.9).

**The problem this resolves.** v1.51 (§26.2) + runtime v1.72 (§14.22.8) ship the ambiguous-pause CAPTURE: a lost-reserve re-dispatch with no captured output raises, and the driver routes it to a resumable `WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS` PAUSE. But the pause was INERT — a naive `api.resume` re-enters the same step (claim still held, still no output) → re-raises → an identical re-pause. v1.52 + runtime v1.73 wire the resume to RESOLVE it: the operator answers the question the fence surfaced ("did the effect fire?") via `ResumeContext.effect_fence_resolution`, and the driver key-binds + threads that answer to the resumed dispatch.

**The reframe (BUILD-not-gate).** The fence pauses *to ASK the operator "did the effect fire?"* — the harness genuinely cannot tell (the crash fell in the fire→capture window). The three resolutions are the operator ANSWERING with ground-truth the harness lacks: `SKIP_AS_FIRED` = "it fired" (→ proceed with empty output, the lost output is unrecoverable, never re-fire); `RE_FIRE` = "it did NOT fire" (→ clear the held claim + re-dispatch fresh, a first-and-only execution); `ABORT` = "can't determine" (→ FAILED). `RE_FIRE` does NOT breach at-most-once — it COMPLETES the at-most-once decision the harness couldn't compute (a mis-assertion is operator-error responsibility, the §3.1 `idempotent` / `blast_radius_tier` mis-declaration posture). The palette composes only committed primitives → no new primitive, no committed-invariant sacrifice → no operator gate (the §13.4 discriminator (a)). The candidate C10⊥C11 tension is probe-resolved to the minimal spec'd semantic (skip-as-fired = empty output, NO operator-supplied-output over-build) → no council.

**Additive, no committed invariant sacrificed.** `EffectFenceResolution` is a NEW `StrEnum`; `EffectFenceResumeState` / `EffectFenceResolutionDirective` are NEW frozen models; `ResumeContext.effect_fence_resolution` + `PauseSnapshot.effect_fence_resume` are additive `… | None = None` fields, so every existing `ResumeContext` / `PauseSnapshot` is byte-unchanged and still validates. `effect_fence_resume` is COVERED by `PauseSnapshot`'s canonical-serialization `snapshot_hash` (a tampered key fails the U-CP-64 resume recompute → `CP-FAIL-PAUSE-SNAPSHOT-CORRUPTION`), added to the canonical dict ONLY when present (at most one of the five resume carriers is ever set — a fence pause is linear/TOOL_STEP, never co-set with the four fan-out carriers), so every pre-existing snapshot hashes byte-identically. It mints no new contract, ADR, fail-class, manifest field, or CXA edge. OD ingests `pause_reason` as a serialized string (no closed-enum enforcement), unaffected. The runtime-side delivery rides the hash-inert `StepExecutionContext.effect_fence_resolution` field (NOT persisted, NOT in any §5.2 / per-step-override outcome-hash) — the `run_engine_class` channel precedent.

**v1.51 + prior body PRESERVED VERBATIM.** All v1.51 content — the §26.2 `WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS` member + the entire C-CP-01 … C-CP-29 body incl. §26.1/§26.3–§26.8 — is PRESERVED VERBATIM per the delta-only-spec-file convention. The only changes are the additive carriers/fields below. The §26.8 `ResumeContext` single-field-shape note (v1.16) is superseded: the shape is now the deliberately-amended `{hitl_response, effect_fence_resolution}` (a deliberate spec amendment, not a silent absorption — the §26.8.1 change-note anticipated extension).

---

## §1 — NEW `EffectFenceResolution` enum (C-CP-26 §26.8.2)

> **`EffectFenceResolution` (NEW at v1.52).** The operator's resume-side resolution of a §26.2 `EFFECT_FENCE_AMBIGUOUS` pause. A 3-value `StrEnum`:
> - `SKIP_AS_FIRED = "skip_as_fired"` — operator asserts the effect FIRED; its output is unrecoverable → the resumed step proceeds with EMPTY output, NEVER re-firing.
> - `RE_FIRE = "re_fire"` — operator asserts the effect did NOT fire → the runtime clears the held reserve and re-dispatches the step FRESH (a first-and-only execution).
> - `ABORT = "abort"` — operator cannot determine (or declines) → the run fails terminally (never re-fire, never proceed-with-empty).
>
> Delivered one-shot via `ResumeContext.effect_fence_resolution` on `api.resume`; key-bound to the paused effect via `PauseSnapshot.effect_fence_resume.idempotency_key`. Answering the fence's question is IN-DOMAIN — it completes the at-most-once decision, it does not override the guarantee.

## §2 — NEW `EffectFenceResumeState` carrier (C-CP-26 §26.2)

> **`EffectFenceResumeState` (NEW at v1.52).** The linear/TOOL_STEP analogue of the four fan-out resume carriers, present on `PauseSnapshot.effect_fence_resume` ONLY when the snapshot captures an `EFFECT_FENCE_AMBIGUOUS` pause. One frozen field — `idempotency_key: str` — the per-(run, step, tool) key of the held reserve the paused dispatch lost. (Unlike the fan-out carriers there is NO recovered output — the ambiguity is precisely that no output was captured; the key alone lets the resumed dispatch key-bind the operator's resolution.) NEVER co-set with `fan_out_resume` / `peer_fan_out_resume` / `handoff_resume` / `evaluator_optimizer_resume`. COVERED by `snapshot_hash`.

## §3 — NEW `EffectFenceResolutionDirective` (C-CP-26 §26.8.2)

> **`EffectFenceResolutionDirective` (NEW at v1.52).** Pairs the operator's `EffectFenceResolution` (from `ResumeContext`) with the `idempotency_key` it is bound to (from `PauseSnapshot.effect_fence_resume`) — illegal-state-unrepresentable (a resolution without its key cannot exist). Two frozen fields: `resolution: EffectFenceResolution`, `idempotency_key: str`. Set by the CP driver on the resumed linear step's `StepExecutionContext.effect_fence_resolution` (hash-inert); read by the runtime tool dispatcher at the §14.22 fence gate, which applies it ONLY when the recomputed dispatch key equals `idempotency_key` (key-bind, correctness-by-construction).

## §4 — Amended `ResumeContext` (C-CP-26 §26.8) — additive `effect_fence_resolution`

> `ResumeContext` gains an additive field `effect_fence_resolution: EffectFenceResolution | None = None` alongside the v1.16 `hitl_response`. `None` when the pause was not an effect-fence pause (a HITL / EXPLICIT_OPERATOR pause carries `hitl_response` instead — the two are mutually exclusive in practice, a pause has one reason). When set on a resume of an effect-fence pause, the driver key-binds it (via `PauseSnapshot.effect_fence_resume.idempotency_key`) and threads it to the resumed linear step. The driver PEEKS the runtime `ResumeContextHolder` non-consuming for this field, so the HITL composer's one-shot `consume_and_clear` is unaffected.

## §5 — Amended `PauseSnapshot` (C-CP-26 §26.2) — additive `effect_fence_resume`

> `PauseSnapshot` gains an additive carrier `effect_fence_resume: EffectFenceResumeState | None = None` (the FIFTH additive resume carrier, after `fan_out_resume` / `peer_fan_out_resume` / `handoff_resume` / `evaluator_optimizer_resume`). Present ONLY for an `EFFECT_FENCE_AMBIGUOUS` pause; NEVER co-set with the four fan-out carriers. COVERED by `_compute_snapshot_hash` when present (added to the canonical dict only when set, so every pre-existing snapshot hashes byte-identically). Populated by the driver from the runtime `EffectFenceAmbiguousUncommittedError`'s `idempotency_key` at the §26.2 pause-capture branch.

---

## §6 — Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_52.md` (delta over v1.51) |
| Authority | R-FS-1 `B-EFFECT-FENCE-PAUSE-RESOLUTION` (BUILD-not-gate; design `.harness/class_1_fork_effect_fence_pause_resolution.md`); FULL-SPEC directive (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`) |
| Paired runtime delta | `Spec_Harness_Runtime_v1.md` v1.72 → v1.73 (§14.22.9) |
| Preserved | v1.51 + entire C-CP-01 … C-CP-29 body PRESERVED VERBATIM; IS / OD / AS / ADR specs UNCHANGED; CXA v2.20 UNCHANGED |
| Apply pass | Co-published with harness-cp impl (the type carriers + `workflow_driver` carrier-population + directive-threading) + the paired runtime v1.73 delta + harness-runtime impl + by-execution witnesses + clearance markers + spine-ledger registration, per workspace `CLAUDE.md` §11.4 bundled-absorption |
