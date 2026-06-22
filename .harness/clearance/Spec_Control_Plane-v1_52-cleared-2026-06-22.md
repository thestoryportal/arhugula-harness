---
artifact: design-substrate/Spec_Control_Plane_v1_52.md
version: v1.52
cleared_at: 2026-06-22T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-spine-ledger (BUILD-not-gate — the CP half of B-EFFECT-FENCE-PAUSE-RESOLUTION. Additive type carriers + two additive model fields at C-CP-26 for the resume-side resolution of the §26.2 EFFECT_FENCE_AMBIGUOUS pause: NEW EffectFenceResolution 3-value enum [skip_as_fired / re_fire / abort], NEW EffectFenceResumeState carrier [the held reserve's idempotency_key], NEW EffectFenceResolutionDirective [resolution + key, illegal-state-unrepresentable], additive ResumeContext.effect_fence_resolution + PauseSnapshot.effect_fence_resume fields. The paired runtime half [the fence clear_claim + the dispatcher three-branch split + the hash-inert StepExecutionContext.effect_fence_resolution channel] lands in runtime v1.72 → v1.73 [§14.22.9]. NO operator gate — the palette composes only committed primitives [answering the fence's "did it fire?" question is in-domain → re-fire COMPLETES at-most-once, not breaches it]. Purely additive: no new contract/ADR/fail-class/manifest-field/CXA edge; effect_fence_resume COVERED by snapshot_hash [added only when present → pre-existing snapshots byte-identical]; the ResumeContext shape is now the deliberately-amended {hitl_response, effect_fence_resolution}.)
back_reference:
  - .harness/class_1_fork_effect_fence_pause_resolution.md (the advisor-vetted design proposal this CP v1.52 + runtime v1.73 deltas execute)
  - .harness/beyond-mvp-capability-boundary-ledger.md (B-EFFECT-FENCE-PAUSE-RESOLUTION spine BUILT note)
  - design-substrate/Spec_Harness_Runtime_v1.md (the paired runtime v1.73 delta — §14.22.9 clear_claim + the dispatcher resolution split)
  - design-substrate/Spec_Control_Plane_v1_51.md (§26.2 the EFFECT_FENCE_AMBIGUOUS pause-reason this RESOLVES; §26.8 the v1.16 ResumeContext this extends)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - advisor (full-transcript, 2 passes) — the BUILD-not-gate reframe (the disposition flip) + the key-bound/consume-once correctness-by-construction guard
  - out-of-family Codex (decorrelated) — pre-merge on the diff (pending at clearance authoring)
  - standing FULL-SPEC operator directive 2026-06-12 (design back-flow pre-authorized; registered → BUILD)
supersedes:
superseded_by:
---

# Clearance — `Spec_Control_Plane v1.52`

v1.52 is the CP half of the R-FS-1 standalone arc **`B-EFFECT-FENCE-PAUSE-RESOLUTION`** — the type carriers + model-field extensions for the resume-side resolution of the §26.2 `EFFECT_FENCE_AMBIGUOUS` pause v1.51 (+ runtime v1.72) opened.

**What changed (additive carriers/fields at C-CP-26).** NEW `EffectFenceResolution` 3-value `StrEnum` (§26.8.2); NEW `EffectFenceResumeState` carrier holding the held reserve's `idempotency_key` (§26.2); NEW `EffectFenceResolutionDirective` pairing resolution + key (§26.8.2); additive `ResumeContext.effect_fence_resolution: EffectFenceResolution | None = None` (§26.8); additive `PauseSnapshot.effect_fence_resume: EffectFenceResumeState | None = None` (§26.2, the FIFTH resume carrier, never co-set with the four fan-out carriers, COVERED by `snapshot_hash`).

**Gate posture — BUILD-not-gate.** The #702 registration labeled this "operator-gated." The reframe flipped it: the fence pauses to ASK "did the effect fire?"; the resolutions are the operator answering, so `RE_FIRE` completes the at-most-once decision rather than overriding it. The palette composes only committed primitives → no net-new primitive → no operator gate. No council (the candidate C10⊥C11 tension probe-resolved to the minimal spec'd semantic).

**Scope.** Purely additive to `C-CP-26`. The v1.51 + entire C-CP-01 … C-CP-29 body PRESERVED VERBATIM. No new contract, ADR, fail-class, manifest field, or CXA edge. OD ingests `pause_reason` as a string (unaffected). The `ResumeContext` single-field-shape note (v1.16) is superseded by the deliberately-amended `{hitl_response, effect_fence_resolution}` set (the §26.8.1 change-note anticipated extension — a deliberate amendment, not a silent absorption; the shape-lock test updated accordingly).

Reviewed during clearance (verified by execution): the `ResumeContext` shape-lock test updated for the deliberate amendment; carrier-population + hash-integrity (the driver populates `effect_fence_resume` from the runtime error's key; the `snapshot_hash` covers it); the full-chain directive-threading producer (the driver peeks non-consuming, key-binds, threads to the resumed step only). harness-cp 1171 passed + 1 xfailed; pyright 0/0/0.

## Notes

- Phase 7 consumers may rely on this version as canonical after the bundled harness-cp + harness-runtime impl + tests land together (`merge_commit` pinned at the post-merge refresh).
- Paired runtime clearance: `.harness/clearance/Spec_Harness_Runtime-v1_73-cleared-2026-06-22.md`.
