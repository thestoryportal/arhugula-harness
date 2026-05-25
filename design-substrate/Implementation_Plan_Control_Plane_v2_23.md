# Implementation Plan — Control Plane v2.23

## Change-note (v2.22 → v2.23)

**Scope of revision.** Single-unit-body amendment at U-CP-59 (cluster 10-CP-A — the unit landing `HITLEscalationBrief` dataclass body per C-CP-28 §28.3 implementation) absorbing CP spec v1.18 → v1.19 NEW §25.2.Y `HITLEscalationBrief.fail_detail_hash` field-type widening (canonical-reading amendment widening the field from `str` non-Optional to `str | None = None` Optional with backward-compatible default). The v1.19 amendment resolves CP spec v1.18 change-note adjacent defect (i) per operator routing decision 2026-05-25 (option (α) parallel widening). v2.23 follows the same delta-only convention applied at v2.22 — single AC added to U-CP-59 covering the v1.19 widening; unit body otherwise preserved verbatim. NO new units; NO new cluster; NO DAG topology change. ZERO contract removal; contract count unchanged at 28. Co-published with CP spec v1.19 + harness-cp impl + harness-runtime impl + runtime plan v2.26 + workspace `CLAUDE.md` row bumps. 2026-05-25.

**v2.22 substantive content preserved verbatim.** All v2.22 NEW §2 U-CP-14 (StepEffectiveBinding.persona_tier extension) + v2.22 NEW §3 U-CP-59 (HITLEscalationBrief.fail_class Optional widening) preserved unchanged. v2.21 + earlier substantive content preserved verbatim.

**Source of fix.** CP spec v1.18 → v1.19 NEW §25.2.Y per operator routing decision 2026-05-25 (option (α) parallel widening). v1.18 change-note adjacent defect (i) RESOLVED at v1.19.

**Authority basis for fix direction.** Per CP spec v1.19 (b) downstream absorption: "single-unit-body amendment at U-CP-59." Empirical-verification: U-CP-59 lands `HITLEscalationBrief` Pydantic v2 BaseModel body at `harness-cp/src/harness_cp/validator_framework_types.py:133-150`. The v1.19 amendment site is line 148.

**Single amendment site (1 NEW AC at U-CP-59).**

| Site | Amendment shape |
|---|---|
| **§3 (NEW at v2.23) — U-CP-59 NEW AC absorbing CP spec v1.19 §25.2.Y** | Adds NEW AC covering: `HITLEscalationBrief.fail_detail_hash` field type AMENDED from `str` (non-Optional, no default) to `str \| None = None` (Optional, defaults to None) per CP spec v1.19 §25.2.Y canonical-reading amendment. Backward-compatible: existing validator-failure construction callsites passing sha256(fail_reason_text) continue to work unchanged; new durable-async pause-trigger construction callsites at runtime composer body (`hitl_gate_composer.py:985`) pass `fail_detail_hash=None`. Tests: 1+ unit test verifying `HITLEscalationBrief(fail_detail_hash=None, ...)` constructs without `ValidationError`. |

**Status posture.** Proposed (v2.22) → **Proposed (v2.23)**. Fidelity-pure single-AC amendment. Net AC count: +1. Unit count: 73 (unchanged). DAG topology: unchanged.

---

## §1 — v2.22 change-note preserved verbatim

---

## Change-note (v2.21 → v2.22)

**Scope of revision.** Two single-unit-body amendments absorbing two operator-ratified spec amendments authored at this session's Phase 1 arc per checkpoint `20260524-211500-u-rt-94-fork-filed-reading-a-path-1-ratified.md` Phase 2 step 4:

**(1) U-CP-14 plan-body amendment** absorbing CP spec v1.17 → v1.17 NEW §6.5 sub-section authoring `StepEffectiveBinding.persona_tier: PersonaTier` field-set extension + `resolve_step_binding(manifest_entry, step_id, *, persona_tier: PersonaTier)` signature widening (NEW keyword-only parameter; no default; required at all callsites per CP spec v1.17 change-note adjacent defect (iv) AUTHORIZED breaking change). Source-of-truth-upstream: `WorkflowManifestEntry.persona_tier: PersonaTier` field already landed at U-CP-13 per CP spec v1.2 §6.1 verbatim manifest schema (existing field; U-CP-13 unchanged at v2.22). Co-published with CP spec v1.17 `9f22924` + runtime spec v1.26 `cc16fc8` this arc.

**(2) U-CP-59 plan-body amendment** absorbing CP spec v1.17 → v1.18 NEW §25.2.X canonical-reading amendment widening `HITLEscalationBrief.fail_class` field-type from `ValidatorFailClass` (non-Optional, no default) to `ValidatorFailClass | None = None` (Optional, default None). Resolves third spec/code divergence at impl(U-RT-93) HALT-on-discovery 2026-05-24 + carried at CP spec v1.17 adjacent defect (i) + runtime spec v1.26 adjacent defect (iii); the durable-async cell HITL pause-trigger composer body at runtime spec v1.24 §14.8.8.1 step 1 calls for `fail_class=None` (no validator outcome at construction site — cell fires on synchrony class alone per C-CP-18 §18.1 + CP spec v1.17 §6.5.2). Co-published with CP spec v1.18 `fe4d622` this arc.

ZERO new units; ZERO new cluster; ZERO DAG topology change; ZERO acceptance-criteria removal; ZERO cross-axis cascade at semantics layer (within-axis-cross-package edges at runtime plan v2.24 U-RT-93/94 consume the widened CP-side surfaces — cross-axis edges declared at consumer-site per established convention, NOT here).

**Source of fix.** Class 1 fork `.harness/class_1_fork_u_rt_94_webhook_delivery_composer_binding_chain_absence.md` §3.1 Reading A path 1 (operator AskUserQuestion 2026-05-24 close) + session-resume ratification 2026-05-24 ("Proceed to phase 1 step 3" + "Proceed to Phase 2 step 4"). Phase 1 spec arc landed 3 amendments across CP spec v1.16→v1.17→v1.18 + runtime spec v1.25→v1.26 at HEAD chain `9f22924`/`cc16fc8`/`fe4d622`. Phase 2 step 4 = CP plan absorption of v1.17 + v1.18 (the v1.26 runtime spec amendment is absorbed at runtime plan v2.24→v2.25 — Phase 2 step 5, separate skill invocation).

**Authority basis for fix direction.** Per CP spec v1.17 (b) downstream absorption: "single-unit-body amendment at U-CP-13 per-step-override-evaluator unit (or sibling unit landing StepEffectiveBinding)." Empirical-verification at the canonical v2 plan body: U-CP-13 lands `WorkflowManifestEntry` (per C-CP-06 §6.1; already declares `persona_tier: PersonaTier` at line 760); U-CP-14 lands `resolve_step_binding` + `StepEffectiveBinding` (per C-CP-06 §6.2; canonical 6-field StepEffectiveBinding declaration at lines 811-818). The v1.17 §6.5 amendment site is U-CP-14, NOT U-CP-13 per the spec text's hedge "(or sibling unit landing StepEffectiveBinding)". Per CP spec v1.18 (b) downstream absorption: "single-unit-body amendment at U-CP-58/59/60/61 (the cluster 10-CP-A units landing `HITLEscalationBrief` dataclass body)". Empirical-verification at v2.15 cluster 10-CP-A authoring: U-CP-58 lands the 3 enums; U-CP-59 lands the dataclasses (including `HITLEscalationBrief`); U-CP-60 lands `ValidatorFramework.evaluate()` body; U-CP-61 lands span emission. The HITLEscalationBrief dataclass body is at U-CP-59 exclusively; v2.22 amends U-CP-59 only per FM-2 no-extension discipline (the over-broad "U-CP-58/59/60/61" enumeration in the spec change-note is honored at the correct sibling-unit per implementation-planner discipline §4.2 spec-traceability).

**Two amendment sites.**

| Site | Amendment shape |
|---|---|
| **U-CP-14 plan body (v1.17 §6.5 absorption)** | (i) AMEND Signatures block: extend `record StepEffectiveBinding` field-set with 7th field `persona_tier: PersonaTier` (no default; required) at canonical field position 7 per CP spec v1.17 §6.5.6 append-at-end discipline; amend `resolve_step_binding(manifest_entry: WorkflowManifestEntry, step_id: StepID)` signature to `resolve_step_binding(manifest_entry: WorkflowManifestEntry, step_id: StepID, *, persona_tier: PersonaTier) -> StepEffectiveBinding` (NEW keyword-only parameter; no default; required at all callsites per CP spec v1.17 adjacent defect (iv) AUTHORIZED breaking change). (ii) AMEND Implements line: `Implements: [C-CP-06 §6.2 + CP spec v1.17 §6.5 StepEffectiveBinding.persona_tier extension + resolve_step_binding signature widening]`. (iii) ADD new AC #5 covering persona_tier field landing on StepEffectiveBinding + AC #6 covering resolve_step_binding signature widening + caller-site update obligation. (iv) Existing ACs #1-#4 preserved verbatim from v2 canonical body. (v) Inputs line EXTEND: `Inputs: ... + PersonaTier enum (existing canonical type at harness-core/src/harness_core/persona_tier.py per Persona §3 four-class set; consumed at U-CP-13 manifest schema already)`. (vi) Files-column unchanged (the file already exists at `harness-cp/src/harness_cp/per_step_override_evaluator.py:117`; the amendment is in-place body refresh at the existing module). (vii) Depends-on EXTEND: append `U-CORE-XX (cross-axis: core) — PersonaTier canonical type at harness-core` if not already present; current v2 canonical Depends-on does not enumerate harness-core but PersonaTier is consumed transitively via U-CP-13's `persona_tier: PersonaTier` field landing — no NEW Depends-on edge required at v2.22 absorption (within-axis-cross-package consumption per existing pattern). (viii) Rollback boundary preserved verbatim. (ix) Tests line EXTEND: append `test_persona_tier_field_on_step_effective_binding`, `test_resolve_step_binding_persona_tier_kw_only_parameter_required`, `test_resolve_step_binding_caller_site_update_at_workflow_driver` to existing test enumeration. |
| **U-CP-59 plan body (v1.18 §25.2.X absorption)** | (i) AMEND Signatures block: `class HITLEscalationBrief` field-type `fail_class: ValidatorFailClass` → `fail_class: ValidatorFailClass | None = None` (widened to Optional with backward-compatible default None per CP spec v1.18 §25.2.X.1 canonical-reading amendment). Other 5 fields (`parent_step_id`, `parent_action_id`, `fail_detail_hash`, `escalation_reason`, `proposed_response_palette`) preserved verbatim with non-Optional types. (ii) AMEND Implements line: `Implements: CP spec v1.10 §25.1 (Validator Protocol + ValidatorFramework Protocol) + §25.2 (ValidatorResult + ValidatorEvaluation + HITLEscalationBrief dataclasses) + CP spec v1.18 §25.2.X HITLEscalationBrief.fail_class field-type widening`. (iii) ADD new AC #6 covering `HITLEscalationBrief.fail_class` field-type widening to Optional with backward-compatible default None + AC #7 covering parallel Optional posture alignment with v1.10 §25.2 line 170 `ValidatorResult.fail_class: ValidatorFailClass | None` (the structural symmetry intentional per CP spec v1.18 §25.2.X.5). (iv) Existing ACs #1-#5 preserved verbatim from v2.15 cluster 10-CP-A authoring. (v) Files-column unchanged (`harness-cp/src/harness_cp/validator_framework_types.py` EXTEND — the file already lands the dataclass body; only the field-type annotation changes). (vi) Depends-on preserved verbatim `[U-CP-58]`. (vii) Tests line EXTEND: append `test_hitl_escalation_brief_fail_class_optional_default_none`, `test_hitl_escalation_brief_fail_class_validator_failure_callsite_unchanged`, `test_hitl_escalation_brief_fail_class_pause_trigger_callsite_none`. |

**Adjacent harmonization sites.** None — both amendments are surgical at single-unit bodies. U-CP-13 manifest schema preserved verbatim (existing `persona_tier: PersonaTier` field already meets CP spec v1.17 §6.5.3 source-of-truth-upstream requirement). U-CP-58 enum carriers preserved verbatim (`ValidatorFailClass` 5-class enum body unchanged; v1.18 does NOT extend the enum per CP spec v1.18 adjacent defect (iii) FM-2 foreclosure). U-CP-60 `ValidatorFramework.evaluate()` body preserved verbatim (the validator-failure construction callsite continues to pass `ValidatorFailClass.X` per the backward-compatible widening). U-CP-61 span emission preserved verbatim. U-CP-62/63/64/65 cluster 10-CP-B preserved verbatim (NO change at v2.22 from v2.21 NEW ResumeContext absorption at U-CP-64 which remains canonical). All other plan units preserved verbatim.

**Sections preserved verbatim from v2.21.** All v2.21 NEW §1 U-CP-64 plan-body amendment (ResumeContext carrier + attempt_resume signature widening) preserved verbatim. All v2.20 substantive content + v2.19 / v2.18 / v2.17 / v2.16 / v2.15 / ... / v2 chain preserved verbatim outside the two amendment sites at v2.22. U-CP-43 GateLevelInput conform at v2.20 (B2 plan-follows-spec) preserved unchanged. U-CP-56 StepExecutionContext 9th-field workflow_id at v2.18 preserved. All cluster 10-CP-A + 10-CP-B unit bodies preserved verbatim outside the U-CP-59 amendment site at v2.22. All foundational substrate units (U-CP-01 through U-CP-12) preserved verbatim.

**Status posture.** Proposed (v2.21) → **Proposed (v2.22)**. v2.22 is a fidelity-pure two-unit-body amendment — both amendments are field-set / signature-shape extensions with backward-compatible posture (U-CP-14 amendment authorizes a breaking change at resolve_step_binding callsites per spec-side AUTHORIZED scope; U-CP-59 amendment is fully backward-compatible at validator-failure callsites). NO v2.21 unit removed; NO v2.21 unit re-decomposed; NO new unit; NO new cluster; NO DAG topology change. Acceptance criterion count change: +2 at U-CP-14 (4 → 6) + +2 at U-CP-59 (5 → 7); total ACs +4 across the two units. Field-set change at any field set: TWO — `StepEffectiveBinding` gains 7th field `persona_tier: PersonaTier` (required, no default) + `HITLEscalationBrief.fail_class` widened from `ValidatorFailClass` to `ValidatorFailClass | None = None` (Optional, default None). Signature change at any function: ONE — `resolve_step_binding(manifest_entry, step_id, *, persona_tier: PersonaTier)` gains required keyword-only parameter. Cross-axis cascade: ZERO at CXA-level (no new cross-axis edge declared at this revision); within-axis-cross-package consumption at runtime plan v2.24 → v2.25 U-RT-93/94 absorbs the widened surfaces per Phase 2 step 5.

**Downstream absorption owed (post-v2.22).**

(a) Workspace `CLAUDE.md` §2.4 CP plan row version bump (v2.21 → v2.22); also §2.3 CP spec row v1.17 → v1.18 bump per Phase 1 step 3 completion. Co-published this arc OR next bookkeeping commit.

(b) **harness-cp impl** — at U-CP-14 + U-CP-59 absorption arcs (Phase 3 step 6 per checkpoint plan): `harness-cp/src/harness_cp/per_step_override_evaluator.py:117` APPEND `persona_tier: PersonaTier` field to `StepEffectiveBinding(BaseModel)` (frozen + `extra="forbid"` preserved); `harness-cp/src/harness_cp/per_step_override_evaluator.py:NNN` AMEND `resolve_step_binding(manifest_entry, step_id)` signature: add `persona_tier: PersonaTier` keyword-only parameter (no default; required); update all callsites (~3-5 per fork doc §3.1 step 6) across harness-cp + harness-runtime + tests + fixtures. `harness-cp/src/harness_cp/validator_framework_types.py` AMEND `HITLEscalationBrief.fail_class` annotation from `ValidatorFailClass` to `ValidatorFailClass | None = None`; existing validator-escalation construction callsites passing `ValidatorFailClass.X` continue to work unchanged.

(c) **harness-runtime impl** — at U-RT-93 helper revision arc (Phase 3 step 8): `_evaluate_cell_synchrony_tolerant(binding)` consumes `binding.persona_tier` directly (no longer getattr-tolerant — the canonical field now exists post-v2.22 absorption + harness-cp impl); REMOVE pyright `reportUnusedFunction` suppression at U-RT-93 helper definition (per checkpoint Phase 3 step 8). U-RT-93 fixture at commit `2cfc5dc` uses sentinel pattern `ValidatorFailClass.SCHEMA_VIOLATION + fail_detail_hash="0"*64`; post-v2.22 + harness-cp impl, the fixture can be amended to use `fail_class=None` directly (the sentinel pattern is no longer required).

(d) **runtime plan v2.24 → v2.25** — Phase 2 step 5 (separate implementation-planner skill invocation per checkpoint): NEW pre-U-RT-94 cluster decomposing webhook binding chain (U-RT-96 per checkpoint enumeration; mirrors L9-decies / L9-undecies precedent at 3-unit cluster decomposition); U-RT-94 re-author with joint precondition + consumer of widened CP-side surfaces; U-RT-95 e2e extension for path (vi) operator-binds-pause-resume-protocol-but-not-webhook arm.

(e) **OD spec / OD plan / OD impl**: ZERO cascade. `HITLEscalationBrief` is intra-CP-axis (consumed by runtime composer + validator escalation gate composer; not by OD-side audit payload composers). `PauseResumeAuditPayload` at OD spec §C-OD-30.4 + `CostRecordAuditPayload` at OD spec §C-OD-26.6 do not consume `HITLEscalationBrief`. `StepEffectiveBinding.persona_tier` is intra-CP-axis (consumed at C-CP-18 §18.1 synchrony matrix lookup + runtime composer; not by OD-side audit payload composers).

(f) **CXA v2.10**: ZERO — no new cross-axis edge; both amendments are intra-CP-axis at the field-set / signature layer.

(g) **ADR-D1 / ADR-D3 / ADR-D5 / ADD / PRD**: ZERO retag owed — both amendments are derivative narrowings within their respective contracts (`persona_tier_floor` per ADR-D5 §1.3.2 4-axis floor formula already canonical; v2.22 makes the per-step carrier-level field landing explicit at U-CP-14 plan body); `HITLEscalationBrief.fail_class` Optional posture aligns with v1.10 parallel `ValidatorResult.fail_class: ValidatorFailClass | None` already canonical).

**Adjacent defects surfaced (NOT patched per FM-2 no-extension discipline).**

(i) **`HITLEscalationBrief.fail_detail_hash` field-type follow-on consideration.** Per CP spec v1.18 adjacent defect (i): `fail_detail_hash: str` at v1.10 §25.2 is non-Optional but at durable-async cell HITL pause-trigger callsite there is no fail reason (no validator outcome at construction site). Three resolution options enumerated at CP spec v1.18 adjacent defect (i) — (α) widen `fail_detail_hash: str | None = None` parallel to v1.18 `fail_class` amendment; (β) synthesize sentinel value at runtime-side per U-RT-93 fixture posture `"0"*64`; (γ) split HITLEscalationBrief into two carriers. v2.22 absorbs (β) at U-RT-93 fixture continuation (per Phase 3 step 8) — the sentinel `"0"*64` pattern continues at v2.22 (the CP spec v1.18 amendment did NOT widen fail_detail_hash). If (α) is chosen at a follow-on spec-extension arc, plan absorption at U-CP-59 is structurally identical to the v2.22 U-CP-59 amendment shape (single field-type widening with backward-compatible default). Surfaced; routed to follow-on operator-discretion arc.

(ii) **Persona-tier sourcing mechanism at the resolver caller site (carried from CP spec v1.17 adjacent (ii)).** Per CP spec v1.17 §6.5.3: the resolver caller is responsible for resolving persona tier prior to invocation. The canonical upstream surfaces are (1) `WorkflowManifestEntry.persona_tier` per §6.1 (already landed at U-CP-13); (2) routing-manifest tier resolution per C-CP-01 §1.3; (3) Persona §3.1 four-class set resolution. The specific upstream surface at the workflow_driver step-dispatch site is implementer-discretion at the impl arc per FM-2; v2.22 plan body at U-CP-14 does NOT pre-commit to a specific upstream surface — the impl absorption (per (b)) chooses the surface at the workflow_driver `step_dispatch` invocation site. Surfaced; routed to implementer-discretion at Phase 3 step 6 per `[[halt-route-split-AC-pattern]]` precedent.

(iii) **Backward-INcompatible signature change at `resolve_step_binding` (AUTHORIZED at v1.17 (iv); plan-level callsite enumeration owed at v2.22).** Per CP spec v1.17 adjacent defect (iv): the `*, persona_tier: PersonaTier` parameter is required (no default) — this is the AUTHORIZED breaking change at v1.17. Plan v2.22 U-CP-14 amendment adds new AC #6 covering the caller-site update obligation but does NOT pre-enumerate the exact callsite count at plan-body (the spec-side AUTHORIZED scope says "find via grep; likely ~3-5 callsites" — the impl arc handles the callsite enumeration). The plan-level AC #6 lists the obligation generically; the impl-arc-specific callsite enumeration is implementer-discretion per the spec-side AUTHORIZED scope. Surfaced; routed to impl absorption at Phase 3 step 6.

(iv) **Cluster 10-CP-A consumer-side construction discipline (NEW post-v1.18 widening).** Post-v2.22 + harness-cp impl, `HITLEscalationBrief.fail_class` is Optional but the field carries different semantics depending on construction context: validator-failure callsites populate per validator outcome; durable-async pause-trigger callsites pass `fail_class=None`. Consumers of `HITLEscalationBrief` at U-CP-60 (`ValidatorFramework.evaluate()` body) + U-CP-61 (`validator.*` span emission) MUST disambiguate via construction-context discipline. v2.22 does NOT pre-commit to consumer-side disambiguation patterns at U-CP-60/61 plan bodies — the construction-context discriminator is implicit via `fail_class is None` per CP spec v1.18 §25.2.X.3. Surfaced; routed to consumer-side absorption at follow-on operator-discretion arc OR runtime-side U-RT-94 composer body landing per Phase 3 step 9.

(v) **Workspace `CLAUDE.md` §2.4 CP plan row stale at v2.20.** Empirical-verification at session resume: workspace `CLAUDE.md` §2.4 CP plan row cites v2.20 but the canonical head is v2.21 (this session's predecessor `Implementation_Plan_Control_Plane_v2_21.md`). v2.22 absorption at this session creates a 2-version-bump stale at the workspace `CLAUDE.md` row. Surfaced; routed to bookkeeping commit per Phase 4 step 11 of checkpoint plan. NOT patched at this implementation-planner revision-pass arc per FM-2 — workspace `CLAUDE.md` row maintenance is bookkeeping discipline, not plan-authoring scope.

---

## §1 — U-CP-14 plan-body amendment (v2.22 — v1.17 §6.5 absorption)

The U-CP-14 declaration last canonically authored at `Implementation_Plan_Control_Plane_v2.md` lines 789-837 (preserved verbatim through v2.21) is amended at v2.22 as follows. Original v2 content preserved verbatim except for the additions enumerated below. v2.1 through v2.21 did not touch U-CP-14.

### U-CP-14 — Implement per-step override evaluator + audit-ledger entry composition (v2.22 amendment — StepEffectiveBinding 7th-field `persona_tier` landing + resolve_step_binding signature widening + 2 NEW ACs)

**Implements:** [C-CP-06 §6.2 (v1.2 baseline) + CP spec v1.17 §6.5 StepEffectiveBinding.persona_tier extension + resolve_step_binding signature widening]

**Depends on:** [U-CP-13, U-CP-15, U-IS-07 (cross-axis: IS), U-IS-08 (cross-axis: IS), U-IS-09 (cross-axis: IS), U-IS-11 (cross-axis: IS)] (preserved verbatim from v2)

**Inputs:** Workflow manifest entry (U-CP-13; existing `WorkflowManifestEntry.persona_tier: PersonaTier` field at v2 line 760 provides the source-of-truth-upstream per CP spec v1.17 §6.5.3); `EngineClass` enum (U-CP-15); F2 substrate (U-IS-07, U-IS-08, U-IS-09, U-IS-11 cross-axis); `PersonaTier` enum (existing canonical type at `harness-core/src/harness_core/persona_tier.py` per Persona §3.1 four-class set; already consumed transitively via U-CP-13's `persona_tier: PersonaTier` field landing).

**Files affected:** CP-axis per-step override evaluator (logical: `per-step-override-evaluator`); CP-axis override audit-ledger entry composition (logical: `override-audit-ledger-composition`) — preserved verbatim from v2; the v2.22 amendment is in-place body refresh at the existing `harness-cp/src/harness_cp/per_step_override_evaluator.py:117` module.

**Cross-axis substrate consumed.** `STATE_LEDGER_ENTRY_SHAPE_EXPORT` + `HASH_CHAIN_CONSTRUCTION_DISCIPLINE_EXPORT` + `JSONL_EVENT_LEDGER_FORMAT_EXPORT` (C-IS-10 §10.1, §10.3, §10.5) for audit-ledger entry composition (preserved verbatim from v2).

**Signatures (v2.22 amendment — Signatures block):**

```
function resolve_step_binding(
    manifest_entry: WorkflowManifestEntry,
    step_id: StepID,
    *,
    persona_tier: PersonaTier        // NEW at v1.17 §6.5.3; required keyword-only; no default
) -> StepEffectiveBinding
    // applies per_step_overrides over manifest_entry defaults
    // emits audit-ledger entry per ADR-F2 audit composition when override applied
    // persona_tier sourced upstream from manifest_entry.persona_tier (U-CP-13 field)
    //   OR routing-manifest tier resolution per C-CP-01 §1.3
    //   OR Persona §3.1 four-class set resolution
    // (specific upstream surface is implementer-discretion at workflow_driver step-dispatch
    //  site per CP spec v1.17 adjacent defect (ii); plan-level AC #6 covers the
    //  caller-site update obligation generically)

record StepEffectiveBinding {                       // 7-field set at v1.17 (was 6-field at v2 baseline)
  step_id            : StepID
  model_binding      : ModelBinding                 // effective (override or default)
  engine_class       : EngineClass
  hitl_placement     : Optional<HITLPlacement>
  override_applied   : bool
  override_audit_ref : Optional<LedgerEntryRef>     // when override_applied = true
  persona_tier       : PersonaTier                  // NEW at v1.17 §6.5.2 field position 7 (required, no default)
}

function emit_override_audit_entry(                 // unchanged at v2.22
    workflow_id: string,
    step_id: StepID,
    override: StepOverride,
    actor: ActorIdentity
) -> AuditLedgerEntry
```

**Acceptance criteria (v2.22 amendment — ACs #1-#4 preserved verbatim from v2; NEW ACs #5 + #6 added):**

1. `resolve_step_binding` returns the effective binding combining manifest defaults + per-step override; override field-by-field; no field-set substitution. *(preserved verbatim from v2)*
2. When override applied, `override_audit_ref` populated by `emit_override_audit_entry` per F2 audit composition; audit entry shape per U-IS-07 six-field shape with `action_id = workflow_id || step_id`. *(preserved verbatim from v2)*
3. `emit_override_audit_entry` delegates canonicalize+hash to U-IS-08; chain construction to U-IS-09; append to U-IS-11. *(preserved verbatim from v2)*
4. Override evaluator is deterministic given inputs. *(preserved verbatim from v2)*
5. **(NEW at v2.22 per CP spec v1.17 §6.5.2)** `StepEffectiveBinding` declares exactly 7 top-level fields with field-set ordering `{step_id, model_binding, engine_class, hitl_placement, override_applied, override_audit_ref, persona_tier}` per v1.17 §6.5.6 append-at-end discipline; the 7th field `persona_tier: PersonaTier` is required (no default); construction without `persona_tier` raises `pydantic.ValidationError`; the 6 prior fields preserved verbatim with identical types from v2.
6. **(NEW at v2.22 per CP spec v1.17 §6.5.3)** `resolve_step_binding` signature is `(manifest_entry: WorkflowManifestEntry, step_id: StepID, *, persona_tier: PersonaTier) -> StepEffectiveBinding`; the `persona_tier` parameter is required keyword-only (no default; backward-INcompatible at impl-level callsite enumeration per CP spec v1.17 adjacent defect (iv) AUTHORIZED breaking change); all callsites across harness-cp + harness-runtime + tests + fixtures (~3-5 per fork doc §3.1 step 6 estimate) MUST be updated to pass the new parameter; the source-of-truth-upstream for the persona_tier value at the workflow_driver step-dispatch site is implementer-discretion per CP spec v1.17 adjacent defect (ii) — canonical upstream surfaces enumerated at §6.5.3 (manifest_entry.persona_tier per U-CP-13 / routing-manifest tier per C-CP-01 §1.3 / Persona §3.1 four-class set).

**Tests (v2.22 amendment — existing tests preserved; 3 NEW tests added):** `test_resolve_step_binding_field_by_field_override`, `test_audit_ref_populated_on_override`, `test_audit_entry_action_id_composition`, `test_delegates_to_u_is_07_08_09_11` *(preserved verbatim from v2)*; **NEW at v2.22:** `test_persona_tier_field_on_step_effective_binding` (verifies 7-field set + persona_tier required + ValidationError on omission), `test_resolve_step_binding_persona_tier_kw_only_parameter_required` (verifies kw-only signature + no-default + TypeError when omitted), `test_resolve_step_binding_caller_site_update_at_workflow_driver` (verifies the workflow_driver step-dispatch invocation passes persona_tier sourced from manifest_entry).

**Rollback boundary:** Revert per-step override evaluator + audit composition. Pipeline-automation per-stage customization loses runtime evaluation; override audit trail dissolves. Cross-axis IS edges to U-IS-07, U-IS-08, U-IS-09, U-IS-11 release. *(preserved verbatim from v2; v2.22 amendment scope is in-place body refresh, no rollback-boundary change.)*

---

## §2 — U-CP-59 plan-body amendment (v2.22 — v1.18 §25.2.X absorption)

The U-CP-59 declaration last canonically authored at `Implementation_Plan_Control_Plane_v2_15.md` §3 cluster 10-CP-A lines 51-62 (preserved verbatim through v2.21) is amended at v2.22 as follows. Original v2.15 content preserved verbatim except for the additions enumerated below. v2.16 through v2.21 did not touch U-CP-59.

### U-CP-59 — Validator Protocol + ValidatorResult + ValidatorEvaluation + HITLEscalationBrief schemas (v2.22 amendment — HITLEscalationBrief.fail_class field-type widening + 2 NEW ACs)

- **Implements:** CP spec v1.10 §25.1 (Validator Protocol + ValidatorFramework Protocol) + §25.2 (ValidatorResult + ValidatorEvaluation + HITLEscalationBrief dataclasses) + **CP spec v1.18 §25.2.X HITLEscalationBrief.fail_class field-type widening (Optional, default None) [NEW at v2.22]**
- **Files:** `harness-cp/src/harness_cp/validator_framework_types.py` (EXTEND — the file already lands the dataclass body per v2.15 cluster 10-CP-A; v2.22 amendment is in-place annotation refresh at the existing `HITLEscalationBrief.fail_class` field declaration)
- **Signatures (v2.22 amendment):**
  - `class Validator(Protocol)` *(preserved verbatim from v2.15)*
  - `@dataclass(frozen=True) class ValidatorResult` *(preserved verbatim from v2.15; `fail_class: ValidatorFailClass | None` already Optional per CP spec v1.10 §25.2 line 170 with `# None if outcome=PASS` semantic — the v2.22 amendment at HITLEscalationBrief brings parallel posture)*
  - `class ValidatorEvaluation` *(preserved verbatim from v2.15)*
  - `class HITLEscalationBrief` field-set at v2.22:
    ```
    @dataclass(frozen=True)
    class HITLEscalationBrief:
        parent_step_id: str                              # preserved verbatim from v2.15
        parent_action_id: str                            # preserved verbatim from v2.15
        fail_class: ValidatorFailClass | None = None    # WIDENED at v2.22 (was: ValidatorFailClass non-Optional no default)
        fail_detail_hash: str                            # preserved verbatim from v2.15 (Optional widening foreclosed at v1.18 per adjacent defect (i) FM-2)
        escalation_reason: str                           # preserved verbatim from v2.15
        proposed_response_palette: frozenset[HITLResponse]   # preserved verbatim from v2.15; default = full palette per C-CP-16 §16.1
    ```
- **Depends on:** [U-CP-58] *(preserved verbatim from v2.15)*
- **ACs (v2.22 amendment — ACs #1-#5 preserved verbatim from v2.15; NEW ACs #6 + #7 added):**
  1. `Validator.validate()` Protocol signature matches §25.1 exactly *(preserved verbatim from v2.15)*
  2. `ValidatorResult` instantiable with all 5 fields (outcome required; others optional per outcome) *(preserved verbatim from v2.15)*
  3. `ValidatorEvaluation` includes `burden_count` cumulative tracking *(preserved verbatim from v2.15)*
  4. `HITLEscalationBrief.proposed_response_palette` defaults to C-CP-16 §16.1 4-response palette *(preserved verbatim from v2.15)*
  5. Pydantic v2 validation on all dataclasses *(preserved verbatim from v2.15)*
  6. **(NEW at v2.22 per CP spec v1.18 §25.2.X.1)** `HITLEscalationBrief.fail_class` field-type is `ValidatorFailClass | None = None` (Optional, default None — widened from v1.10 §25.2 non-Optional no-default declaration); construction WITHOUT `fail_class` parameter succeeds with `fail_class = None`; construction with `fail_class=ValidatorFailClass.X` succeeds backward-compatibly (validator-failure callsites unchanged); construction with `fail_class=None` succeeds (durable-async pause-trigger callsite per runtime spec v1.24 §14.8.8.1 step 1 construction context); other 5 fields preserved verbatim with non-Optional types.
  7. **(NEW at v2.22 per CP spec v1.18 §25.2.X.5 parallel posture preservation)** `HITLEscalationBrief.fail_class: ValidatorFailClass | None = None` field-type matches the parallel `ValidatorResult.fail_class: ValidatorFailClass | None` shape at v1.10 §25.2 line 170; the structural symmetry is intentional and load-bearing — consumers of `HITLEscalationBrief` MUST disambiguate construction context via `fail_class is None` discriminator (validator-failure context: populated; pause-trigger context: None) per CP spec v1.18 §25.2.X.3 consumer-side semantics.

- **Tests (v2.22 amendment — existing tests preserved; 3 NEW tests added):**
  - Existing v2.15 tests preserved (test names per v2.15 cluster 10-CP-A authoring — `test_validator_protocol_signature`, `test_validator_result_instantiation`, etc.)
  - **NEW at v2.22:**
    - `test_hitl_escalation_brief_fail_class_optional_default_none` — verifies construction without `fail_class` parameter produces `fail_class is None` instance
    - `test_hitl_escalation_brief_fail_class_validator_failure_callsite_unchanged` — verifies backward-compat: `HITLEscalationBrief(..., fail_class=ValidatorFailClass.SCHEMA_VIOLATION, ...)` continues to work as in v2.15
    - `test_hitl_escalation_brief_fail_class_pause_trigger_callsite_none` — verifies NEW callsite shape: `HITLEscalationBrief(..., fail_class=None, ...)` is the canonical durable-async pause-trigger construction per runtime spec v1.24 §14.8.8.1 step 1

---

## §3 — Cluster preservation + DAG topology (v2.22)

**Cluster 2 (F3 lifecycle + manifest) at v2.22:** unchanged structurally — U-CP-13 (`WorkflowManifestEntry` schema) + U-CP-14 (per-step override evaluator + `StepEffectiveBinding` carrier — AMENDED at v2.22 NEW §1) preserved at their canonical positions. U-CP-10/11/12 preserved verbatim.

**Cluster 10-CP-A at v2.22:** unchanged structurally — U-CP-58 (3 enums) + U-CP-59 (Validator Protocol + dataclasses including `HITLEscalationBrief` — AMENDED at v2.22 NEW §2) + U-CP-60 (`ValidatorFramework.evaluate()` body) + U-CP-61 (span emission) preserved at their canonical positions. All 4 units' Depends-on declarations preserved verbatim.

**Cluster 10-CP-B at v2.22:** unchanged from v2.21 — U-CP-62/63/64 (NEW ResumeContext absorption at v2.21) / U-CP-65 preserved verbatim.

**DAG topology at v2.22:** ZERO new edges within CP-axis; ZERO new edges to other axes at CXA-level. Within-axis-cross-package consumption edges at runtime plan v2.24 → v2.25 U-RT-93/94 consume the widened CP-side surfaces (`StepEffectiveBinding.persona_tier` + widened `resolve_step_binding` signature + Optional `HITLEscalationBrief.fail_class`) — cross-axis edges declared at consumer-site per established convention, NOT here.

**Coverage matrix at v2.22:** preserved verbatim — C-CP-06 §6.1 + §6.2 → U-CP-13, U-CP-14 (rows unchanged; AC count change at U-CP-14: +2); C-CP-28 §25.1 + §25.2 + §25.2.X → U-CP-58, U-CP-59, U-CP-60, U-CP-61 (rows unchanged; AC count change at U-CP-59: +2; NEW §25.2.X row added pointing to U-CP-59 absorption).

---

## §4 — Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_22.md` |
| Version | v2.22 |
| Filing event | HITL-gate-as-pause-trigger impl arc — Phase 2 step 4 (CP plan absorption of v1.17 + v1.18 spec amendments) per checkpoint `20260524-211500-u-rt-94-fork-filed-reading-a-path-1-ratified.md` |
| Predecessor | `Implementation_Plan_Control_Plane_v2_21.md` (substantive content preserved verbatim outside the U-CP-14 + U-CP-59 amendment sites) |
| Successor | (none — current canonical) |
| Co-published artifacts (prior commits this arc) | CP spec v1.16 → v1.17 `9f22924`; runtime spec v1.25 → v1.26 `cc16fc8`; CP spec v1.17 → v1.18 `fe4d622`; this revision-pass (CP plan v2.21 → v2.22) co-publishes with Phase 1 step 1 + step 2 + step 3 commits |
| Co-published artifacts (next arcs) | runtime plan v2.24 → v2.25 (Phase 2 step 5 — separate implementation-planner skill invocation); harness-cp impl Phase 3 step 6; harness-runtime impl Phase 3 steps 7-10 |
| Downstream absorption owed (next arcs) | Workspace `CLAUDE.md` §2.3 CP spec row v1.17 → v1.18 bump + §2.4 CP plan row v2.20 → v2.22 bump (Phase 4 step 11 bookkeeping); `HITLEscalationBrief.fail_detail_hash` parallel Optional widening per adjacent defect (i) (operator-discretion); explicit construction-context discriminator per CP spec v1.18 adjacent (ii) (foreclosed at v1.18 per FM-2; future arcs) |
| Operator authority | AskUserQuestion 2026-05-24 close ("Reading A path 1 — author full webhook binding chain + StepEffectiveBinding.persona_tier extension") + session-resume ratifications 2026-05-24 ("Proceed to phase 1 step 3" + "Proceed to Phase 2 step 4") |
| Unit-count change | None (73 → 73) |
| Cluster-count change | None (no new cluster; no cluster re-decomposition) |
| DAG topology change | None (ZERO new within-axis edges; ZERO new cross-axis edges at CXA-level) |
| Coverage matrix structural change | None at row count (rows unchanged); ONE NEW row added (CP spec v1.18 §25.2.X HITLEscalationBrief.fail_class field-type widening → U-CP-59) per delta-only convention |
| Acceptance criterion count change | +4 across two units (U-CP-14: 4 → 6; U-CP-59: 5 → 7) |
| Cross-axis cascade | Within-axis-cross-package (runtime plan v2.24 → v2.25 U-RT-93/94 depend on the widened CP-side surfaces); ZERO new CXA-level cross-axis edges |
| Skill discipline | `implementation-planner` Phase-7 revision-pass absorbing upstream CP spec v1.17 §6.5 + CP spec v1.18 §25.2.X publications into U-CP-14 + U-CP-59 plan bodies; fidelity-pure two-unit-body amendment (4 NEW ACs + 1 field-set field addition + 1 signature widening + 1 field-type widening); NO contract addition; NO unit re-decomposition; NO DAG topology change; NO cluster reorganization; 5 adjacent defects surfaced at change-note for follow-on arcs per FM-2; preservation audit PASSED |
| Date | 2026-05-24 |
