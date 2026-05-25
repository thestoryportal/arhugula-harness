# Specification — Control Plane v1.18

## Change-note (v1.17 → v1.18)

**Scope of revision.** Narrow-scope `HITLEscalationBrief.fail_class` field-type widening at C-CP-28 §25.2 (the v1.10-lineage canonical field-set declaration; the contract ID `C-CP-25` was renamed to `C-CP-28` at v1.13 §1 Reading A ratification; the section-number `§25.2` is preserved verbatim from the v1.10 file body per delta-only spec-chain preservation discipline). v1.18 amends the field type from `fail_class: ValidatorFailClass` (non-Optional, no default) to `fail_class: ValidatorFailClass | None = None` (Optional, defaults to None). The amendment resolves the third spec/code divergence surfaced at impl(U-RT-93) HALT-on-discovery 2026-05-24 + carried at CP spec v1.17 change-note adjacent defect (i) + runtime spec v1.26 change-note adjacent defect (iii): runtime spec v1.24 §14.8.8.1 step 1 composer-body construction calls for `HITLEscalationBrief(..., fail_class=None, ...)` at durable-async cell HITL pause-trigger context (NOT a validator-failure context — the cell is firing on synchrony class alone, no validator outcome exists at the construction site), but the canonical `HITLEscalationBrief` declared the field as non-Optional. The amendment makes the field nullable so durable-async pause-trigger callsites can construct the brief without synthesizing a placeholder `ValidatorFailClass` value. Per checkpoint Phase 1 step 3 (operator AskUserQuestion 2026-05-24 close — "optional Phase 1 step 3"; user-ratified at session resume). Operator-ratified 2026-05-24. ZERO change to other `HITLEscalationBrief` fields (`parent_step_id`, `parent_action_id`, `fail_detail_hash`, `escalation_reason`, `proposed_response_palette` all preserved verbatim). ZERO change to `ValidatorFailClass` enum body. ZERO change to `ValidatorResult.fail_class: ValidatorFailClass | None` (the field at v1.10 §25.2 ValidatorResult was already Optional per §25.2 line 170 — `fail_class: ValidatorFailClass | None # None if outcome=PASS`; v1.18 makes `HITLEscalationBrief.fail_class` parallel to that pattern). ZERO change to ValidatorFramework Protocol signature. ZERO new fail class. ZERO new contract. ZERO cross-axis cascade — `HITLEscalationBrief` is intra-CP-axis; consumed at runtime composer body per §14.8.8.1 step 1 (already in v1.24 spec text); OD spec / CXA v2.10 / ADR / ADD / PRD unaffected.

**v1.17 substantive content preserved verbatim.** All v1.17 NEW §6.5 sub-section (§6.5.1 canonical-name reconciliation + §6.5.2 carrier field-set extension + §6.5.3 `resolve_step_binding` signature widening + §6.5.4 composition with §18.1 matrix + §6.5.5 verbatim-layer integrity + §6.5.6 field-set ordering stability) preserved unchanged. All v1.16 NEW §26.8 (`ResumeContext` carrier + `attempt_resume` signature widening) preserved verbatim. All v1.15 §19.1.1 (NEW) canonical 4-axis statement preserved verbatim. All v1.14 4-cite-cell amendments preserved. All v1.13 §28 ValidatorFramework rename preserved. All v1.12 §25.2.1 9th-field `workflow_id` amendment preserved. All v1.11 §26.2 `PauseReason` → `WorkflowPauseReason` rename + §26 NEW NOTE preserved. All v1.10 §25 / §26 / §27 substantive content preserved verbatim except the single-field-type widening recorded at §25.2.X canonical-reading amendment at v1.18 §25.2.X below. All v1.6 / v1.2 substantive content preserved verbatim.

**Source of fix.** CP spec v1.17 change-note adjacent defect (i) ("`HITLEscalationBrief.fail_class` non-Optional vs runtime spec v1.24 §14.8.8.1 step 1 `fail_class=None` divergence") + runtime spec v1.26 change-note adjacent defect (iii) (same defect, carried forward at runtime-side change-note) + operator AskUserQuestion 2026-05-24 close ("optional Phase 1 step 3") + session-resume user ratification 2026-05-24 ("Proceed to phase 1 step 3"). Empirical-verification at HEAD `cc16fc8`: runtime spec v1.26 §14.8.8.1 step 1 preserves v1.24 composer-body construction calling for `fail_class=None`; the v1.26 amendment did NOT absorb via sentinel-value pattern (e.g., `fail_class=ValidatorFailClass.SCHEMA_VIOLATION` with `fail_detail_hash="0"*64` per U-RT-93 fixture posture at commit `2cfc5dc`) — instead deferred the choice to v1.18 spec-side absorption OR runtime-side workaround. v1.18 executes the spec-side absorption per operator-ratified Phase 1 step 3.

**Authority basis for fix direction.** The runtime spec v1.24 §14.8.8.1 step 1 construction site is the canonical consumer of `HITLEscalationBrief` at the durable-async cell HITL pause-trigger composition arc; the construction context has no validator outcome (the cell is firing on synchrony class alone — `binding.persona_tier × binding.engine_class → SynchronyClass.DURABLE_ASYNC` per C-CP-18 §18.1 matrix + CP spec v1.17 §6.5.2 carrier field-set extension authoring the canonical `persona_tier` field). The validator-failure construction context (the v1.10 original intent at C-CP-28 §25.2 — `ValidatorFramework.evaluate(...)` returning `ValidatorOutcome.ESCALATE` with a typed `HITLEscalationBrief` carrying the fail context) remains valid; v1.18 broadens the carrier shape to accommodate the durable-async pause-trigger construction context as well. The parallel precedent is `ValidatorResult.fail_class: ValidatorFailClass | None` at v1.10 §25.2 line 170 (already Optional with `# None if outcome=PASS` semantic); v1.18 aligns `HITLEscalationBrief.fail_class` with the same Optional posture. The two contexts produce semantically distinct construction shapes (validator-failure: fail_class populated + fail_detail_hash populated; pause-trigger: fail_class=None + fail_detail_hash=...); consumers MUST disambiguate via the construction-context discipline at §14.8.8.1 step 1 vs §14.15 C-RT-25 (validator-escalation gate composer).

**Single amendment site (1 field-type widening canonical-reading amendment).**

| Site | Amendment shape |
|---|---|
| **§25.2.X (NEW at v1.18) — `HITLEscalationBrief.fail_class` field-type widening (canonical-reading amendment)** | Authors a canonical-reading amendment over the v1.10 §25.2 `HITLEscalationBrief` dataclass body (preserved verbatim in v1.10 file): `fail_class: ValidatorFailClass` → `fail_class: ValidatorFailClass | None = None`. The v1.10 file body is NOT edited — delta-only spec-chain preservation discipline preserved per v1.13 §1.3 + v1.14 §1.3 + v1.15 §19.1.1.4 + v1.16 §26.8.4 + v1.17 §6.5.5 verbatim-layer-integrity precedent. Consumers reading the delta chain interpret the v1.10 §25.2 `HITLEscalationBrief` carrier field-set AS canonically supplemented at v1.18 §25.2.X per this change-note. |

**Adjacent harmonization sites.** None — the amendment is surgical at one field. §25.2 `ValidatorResult.fail_class` field-type (already `ValidatorFailClass | None`) preserved verbatim. `ValidatorFailClass` enum body preserved verbatim. `ValidatorOutcome` enum body preserved verbatim. `ValidatorNextAction` enum body preserved verbatim. §25.3-§25.8 (lifecycle / invocation / span / failure-mode / invariants / deferred-discretion) preserved verbatim. The other 5 fields on `HITLEscalationBrief` (`parent_step_id`, `parent_action_id`, `fail_detail_hash`, `escalation_reason`, `proposed_response_palette`) preserved verbatim with non-Optional types — see adjacent defect (i) below for `fail_detail_hash` follow-on consideration.

**Sections preserved verbatim from v1.17.** All v1.17 NEW §6.5 + all v1.16 NEW §26.8 + all v1.15 §19.1.1 + all v1.14 / v1.13 / v1.12 / v1.11 / v1.10 / v1.6 / v1.2 substantive content preserved verbatim.

**Status posture.** Proposed (v1.17) → **Proposed (v1.18)**. v1.18 is a fidelity-pure field-type widening amendment — single existing carrier field changes from non-Optional to Optional with backward-compatible default. NO v1.17 contract removed; NO v1.17 contract re-decomposition; NO v1.17 field-set added or removed. Contract count unchanged at 28. Fail-class count unchanged. Signature change at any Protocol: ZERO (the `HITLEscalationBrief` is a typed payload, not a Protocol). Field-set change at any field set: ONE — `HITLEscalationBrief.fail_class` widened from `ValidatorFailClass` to `ValidatorFailClass | None = None` (backward-compatible at validator-failure callsites — existing callers passing `ValidatorFailClass.X` continue to work unchanged; new callers at durable-async pause-trigger callsites can pass `None` or omit the parameter entirely per the default). Acceptance criterion change at any contract: NONE at spec-side (CP plan U-CP-NN absorption AC re-decomposition is downstream absorption per (b) below; runtime plan U-RT-94 AC #2 re-evaluation is Phase 3 step 9). Behavior change: NONE at canonical validator-failure callsites — `fail_class` is a typed-payload field; widening to Optional preserves all existing semantics. Behavior change at durable-async pause-trigger callsites: composer body at §14.8.8.1 step 1 can construct `HITLEscalationBrief(..., fail_class=None, ...)` without sentinel-value synthesis (was: impossible at v1.17 without breaking the non-Optional contract).

**Downstream absorption owed (post-v1.18).**

(a) Workspace `CLAUDE.md` §2.3 CP spec row version bump (v1.17 → v1.18); co-published this arc OR next bookkeeping commit.

(b) **CP plan v2.20 → v2.21 → v2.22 (or naming-equivalent per current head)** — single-unit-body amendment at U-CP-58/59/60/61 (the cluster 10-CP-A units landing `HITLEscalationBrief` dataclass body + `ValidatorFramework` Protocol surface per `harness-cp/src/harness_cp/validator_framework_types.py:130` per C-CP-28 §28.3 implementation). Add new AC covering the field-type widening. Files-column unchanged (the dataclass body file already exists; only the field type annotation changes). NO new unit; NO new cluster; NO DAG topology change. Co-published next arc OR at Phase 2 step 4 per checkpoint plan.

(c) **harness-cp impl** updates: `harness-cp/src/harness_cp/validator_framework_types.py:NNN` (or wherever `HITLEscalationBrief` body lives — implementer-discretion location per dataclass-vs-Pydantic-v2-implementation discretion at U-CP-58 landing) — AMEND `fail_class: ValidatorFailClass` annotation to `fail_class: ValidatorFailClass | None = None`. Backward-compatible: existing validator-escalation construction callsites passing `ValidatorFailClass.X` continue to work unchanged. New durable-async pause-trigger construction callsites at runtime composer body per §14.8.8.1 step 1 can pass `fail_class=None` or omit. Co-published next arc OR at Phase 3 step 6 per checkpoint plan.

(d) **harness-runtime impl** updates: at U-RT-93 helper fixture revision (Phase 3 step 8) — current U-RT-93 fixture at commit `2cfc5dc` uses `ValidatorFailClass.SCHEMA_VIOLATION + fail_detail_hash="0"*64` sentinel pattern per fork doc §2.2 finding 3 + runtime spec v1.26 adjacent defect (iii). Post-v1.18, the U-RT-93 fixture can be amended to use `fail_class=None` directly (the sentinel pattern is no longer required). U-RT-94 composer body landing at Phase 3 step 9 consumes the widened type at §14.8.8.1 step 1 construction site.

(e) **OD spec / OD plan / OD impl**: ZERO — `HITLEscalationBrief` is intra-CP-axis (consumed by runtime composer + validator escalation gate composer; not by OD-side audit payload composers). `PauseResumeAuditPayload` at §C-OD-30.4 + `CostRecordAuditPayload` at §C-OD-26.6 do not consume `HITLEscalationBrief`. ZERO OD cascade.

(f) **CXA v2.10**: ZERO — no new cross-axis edge; the field-type widening is internal to C-CP-28; no consumer crosses the axis boundary at v1.18.

(g) **ADR-D1 / ADR-D5 / ADD / PRD**: ZERO retag owed — `HITLEscalationBrief.fail_class` Optional posture is a derivative narrowing within C-CP-28's contract surface (already ADR-D3 v1.2 §1.1 #1 validation-contract territory; the Optional posture aligns with the parallel `ValidatorResult.fail_class: ValidatorFailClass | None` already canonical at v1.10 §25.2 line 170). ZERO upstream-artifact revision triggered.

**Adjacent defects surfaced (NOT patched per FM-2 no-extension discipline).**

(i) **`HITLEscalationBrief.fail_detail_hash` field-type at durable-async pause-trigger callsite.** v1.10 §25.2 declares `fail_detail_hash: str` as non-Optional. At durable-async cell HITL pause-trigger context (per runtime spec v1.24 §14.8.8.1 step 1 construction), there is no fail reason — there is no fail at all — so `fail_detail_hash` has no canonical value. Three resolution options: (α) widen `fail_detail_hash: str | None = None` parallel to v1.18 `fail_class` amendment (full carrier-shape harmonization for the dual-context construction discipline); (β) synthesize a sentinel value at runtime-side per U-RT-93 fixture posture `"0"*64` (purely runtime-side workaround; no spec amendment); (γ) split the `HITLEscalationBrief` into two carriers — `ValidatorEscalationBrief` + `PauseTriggerBrief` (full structural-symmetry resolution at higher spec-cost). v1.18 does NOT patch this — operator instruction at Phase 1 step 3 was scoped narrowly to `fail_class` only ("amend `HITLEscalationBrief.fail_class` to `ValidatorFailClass | None = None`"). Surfaced; routed to follow-on operator-discretion arc per `[[halt-route-split-AC-pattern]]` precedent. Note: if (α) is chosen at a follow-on arc, the amendment is structurally identical to v1.18 (single field-type widening with backward-compatible default).

(ii) **Construction-context discipline at consumers.** Post-v1.18, `HITLEscalationBrief.fail_class` is Optional but the field carries different semantics depending on construction context: validator-failure callsites at C-CP-28 §25.2 / §14.15 C-RT-25 (ValidatorEscalationGateComposer) populate `fail_class` per the validator outcome; durable-async pause-trigger callsites at §14.8.8.1 step 1 pass `fail_class=None`. Consumers MUST disambiguate via construction-context discipline (the consumer at `hitl.gate.evaluated` span emission can read `fail_class is None` as the durable-async-pause-trigger discriminator). v1.18 does NOT add an explicit `construction_context: Literal["validator_failure", "pause_trigger"]` discriminator field — the Optional `fail_class` is the implicit discriminator. Surfaced; alternative (explicit discriminator field) routed to follow-on operator-discretion arc per FM-2.

(iii) **`ValidatorFailClass` enum extension foreclosed at v1.18.** v1.10 §25.2 declares `ValidatorFailClass` as a closed enum (5-class taxonomy per C-CP-21 §21.3). v1.18 does NOT extend the enum (e.g., adding a `PAUSE_TRIGGERED` member to indicate the durable-async pause-trigger discriminator). The Optional posture at `fail_class` is the canonical pattern for the dual-context construction; enum extension is foreclosed at v1.18 per FM-2 no-extension discipline. Surfaced; future arcs requiring an explicit pause-trigger discriminator should consider Option (i)(γ) carrier split rather than enum extension to preserve the 5-class fail taxonomy invariant.

(iv) **U-CP-58/59/60/61 cluster-boundary edge to runtime composer body.** The Phase 3 step 8 + step 9 absorption (U-RT-93 helper revision + U-RT-94 composer body) consumes `HITLEscalationBrief` per the v1.18 widened type. The cluster-boundary edge from runtime plan v2.24 → v2.25 L9-terdecies cluster to CP plan v2.20-cluster-10-CP-A is implicit via the typed carrier import at `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py` (the composer body imports `HITLEscalationBrief` from harness-cp). v1.18 does NOT amend the cluster-boundary edge declaration at the plan-level; implementation-planner absorption per Phase 2 steps 4 + 5 handles the cluster-boundary edge per (b). Surfaced; routed to implementation-planner revision-pass per checkpoint Phase 2.

---

## §25.2.X (NEW at v1.18) — `HITLEscalationBrief.fail_class` field-type widening (canonical reading)

### §25.2.X.1 Canonical-reading amendment

The v1.10 §25.2 `HITLEscalationBrief` dataclass body at v1.10 file lines 201-210 is canonically read at v1.18 as:

```python
@dataclass(frozen=True)
class HITLEscalationBrief:
    parent_step_id: str
    parent_action_id: str
    fail_class: ValidatorFailClass | None = None         # WIDENED at v1.18 (was: ValidatorFailClass, non-Optional, no default)
    fail_detail_hash: str                                # preserved verbatim (non-Optional at v1.18; see adjacent defect (i) for pause-trigger callsite consideration)
    escalation_reason: str                               # preserved verbatim — operator-readable summary
    proposed_response_palette: frozenset[HITLResponse]   # preserved verbatim — default = full palette per C-CP-16 §16.1
```

The v1.10 file body at lines 201-210 is NOT edited — delta-only spec-chain preservation discipline preserved per v1.13 §1.3 + v1.17 §6.5.5 verbatim-layer-integrity precedent. Consumers reading the delta chain interpret the v1.10 §25.2 `HITLEscalationBrief` carrier field-set AS canonically supplemented at v1.18 §25.2.X.1 per this change-note.

### §25.2.X.2 Field-type widening rationale

The widening from non-Optional to Optional-with-default-None resolves the dual-context construction discipline at:

| Construction context | Callsite | `fail_class` value |
|---|---|---|
| Validator-failure escalation | `ValidatorFramework.evaluate(...)` returning `ValidatorOutcome.ESCALATE`; §14.15 C-RT-25 ValidatorEscalationGateComposer composition | Populated per the validator outcome — `ValidatorFailClass.SCHEMA_VIOLATION` / `.SEMANTIC_VIOLATION` / `.SAFETY_VIOLATION` / `.POLICY_VIOLATION` / `.OPERATOR_BURDEN_EXCEEDED` per the 5-class taxonomy at C-CP-21 §21.3 |
| Durable-async cell HITL pause-trigger | Runtime spec v1.24 §14.8.8.1 step 1 composer-body construction | `None` (no validator outcome at construction site; cell is firing on synchrony class alone per C-CP-18 §18.1 + CP spec v1.17 §6.5.2) |

The Optional posture aligns with the parallel `ValidatorResult.fail_class: ValidatorFailClass | None` at v1.10 §25.2 line 170 (with `# None if outcome=PASS` semantic). Pre-v1.18, the `HITLEscalationBrief.fail_class` field was inconsistent with the parallel `ValidatorResult.fail_class` Optional posture — v1.18 harmonizes the two.

### §25.2.X.3 Consumer-side semantics

Post-v1.18, consumers of `HITLEscalationBrief` (the HITL gate composer at runtime spec v1.24 §14.8.2 step 4 cluster + the validator escalation gate composer at runtime spec v1.22 §14.15 C-RT-25 + the audit-payload composers at OD spec §C-OD-30) MUST treat `fail_class is None` as the durable-async-pause-trigger construction discriminator. Future spec amendments adding explicit construction-context discriminator (e.g., `construction_context: Literal["validator_failure", "pause_trigger"]`) are foreclosed at v1.18 per FM-2 no-extension discipline (see adjacent defect (ii)).

The `hitl.gate.evaluated` span emission per C-CP-17 §17.4 + OD spec §C-OD-29.X (or wherever the span attributes for HITL gate evaluation live in the canonical OD-side namespace declaration) MAY benefit from a derived `pause_trigger_origin: bool` span attribute (computed as `fail_class is None` at the span construction site) to surface the construction-context discriminator at observability layer. NOT amended at v1.18 per FM-2 — OD spec / OD plan absorption owed at follow-on operator-discretion arc.

### §25.2.X.4 Verbatim-layer integrity

The v1.10 file (`Spec_Control_Plane_v1_10.md`) §25.2 `HITLEscalationBrief` dataclass body at lines 201-210 is NOT edited at v1.18 — delta-only spec-chain preservation discipline preserved per v1.13 §1.3 + v1.14 §1.3 + v1.15 §19.1.1.4 + v1.16 §26.8.4 + v1.17 §6.5.5 verbatim-layer-integrity precedent. The §25.2.X.1 canonical-reading amendment at v1.18 is the canonical interpretation of the `HITLEscalationBrief.fail_class` field-type going forward; consumers reading the delta chain interpret the v1.10 §25.2 body AS canonically supplemented at v1.18 §25.2.X.1.

### §25.2.X.5 ValidatorResult.fail_class parallel posture preservation

The v1.10 §25.2 `ValidatorResult.fail_class: ValidatorFailClass | None` field (with `# None if outcome=PASS` semantic at v1.10 line 170) is preserved verbatim at v1.18. The amendment at `HITLEscalationBrief.fail_class` brings the parallel carrier to the same Optional posture; the two carriers now have structurally-identical `fail_class` field shapes, with the construction-context discriminator carried by:

- `ValidatorResult`: `outcome: ValidatorOutcome` enum value (PASS implies `fail_class is None`)
- `HITLEscalationBrief`: implicit via `fail_class is None` (pause-trigger context discriminator per §25.2.X.3)

The structural symmetry is intentional and load-bearing — future amendments to either carrier's `fail_class` field-type SHOULD preserve the symmetry per FM-2 no-extension discipline.

---

## §2 — Preservation guarantees

| Element | Disposition |
|---|---|
| v1.17 NEW §6.5 (`StepEffectiveBinding.persona_tier` extension + `resolve_step_binding` signature widening) | Preserved verbatim |
| v1.16 NEW §26.8 (`ResumeContext` carrier + `attempt_resume` signature widening) | Preserved verbatim |
| v1.15 §19.1.1 (NEW) canonical 4-axis statement (§19.1.1.1-§19.1.1.4) | Preserved verbatim |
| v1.14 4-cite-cell canonical-reading amendment | Preserved verbatim |
| v1.13 §28 ValidatorFramework rename (C-CP-25 → C-CP-28) | Preserved verbatim — v1.18 cite shape `C-CP-28 §25.2` honors the rename convention (contract ID renamed; section-number preserved from v1.10 file body) |
| v1.12 §25.2.1 9th-field `workflow_id` amendment | Preserved verbatim |
| v1.11 §26.2 `PauseReason` → `WorkflowPauseReason` rename + §26 NEW NOTE | Preserved verbatim |
| v1.10 §25 / §26 / §27 substantive content | Preserved verbatim — v1.18 §25.2.X (NEW) appended; `HITLEscalationBrief.fail_class` field-type widening recorded as canonical-reading amendment at §25.2.X.1; v1.10 file body lines 201-210 NOT edited |
| v1.10 §25.2 `ValidatorResult.fail_class: ValidatorFailClass | None` (with `# None if outcome=PASS` semantic) | Preserved verbatim — v1.18 brings `HITLEscalationBrief.fail_class` to parallel Optional posture (see §25.2.X.5) |
| v1.10 §25.3 lifecycle stage placement | Preserved verbatim |
| v1.10 §25.4 invocation discipline (5 invariants: run-every-step, validation-after-dispatch, REVALIDATE-bounded, ESCALATE-always-emits-HITL, burden-count-monotonic) | Preserved verbatim |
| v1.10 §25.5 span emission | Preserved verbatim |
| v1.10 §25.6 failure-mode taxonomy | Preserved verbatim |
| v1.10 §25.7 invariants | Preserved verbatim |
| v1.10 §25.8 deferred to implementation discretion | Preserved verbatim |
| v1.10 `ValidatorFailClass` 5-class enum (SCHEMA_VIOLATION / SEMANTIC_VIOLATION / SAFETY_VIOLATION / POLICY_VIOLATION / OPERATOR_BURDEN_EXCEEDED per C-CP-21 §21.3) | Preserved verbatim — closed enum at v1.18 per adjacent defect (iii) |
| v1.10 `ValidatorOutcome` enum body | Preserved verbatim |
| v1.10 `ValidatorNextAction` enum body | Preserved verbatim |
| `HITLEscalationBrief` other 5 fields (`parent_step_id`, `parent_action_id`, `fail_detail_hash`, `escalation_reason`, `proposed_response_palette`) | Preserved verbatim with non-Optional types at v1.18 — `fail_detail_hash` follow-on consideration at adjacent defect (i) |
| C-CP-17 §17.1 HITLResult type + HITLPlacement enum + C-CP-16 §16.1 default-full-palette | Preserved verbatim |
| C-CP-18 §18.1 / §18.3 (synchrony matrix + both-by-tier overlay) | Preserved verbatim |
| C-CP-06 §6.1-§6.4 (v1.2 baseline) + §6.5 (v1.17 NEW) | Preserved verbatim |
| §26.8 (v1.16 NEW) `ResumeContext` carrier + `attempt_resume` signature widening | Preserved verbatim |
| §28 ValidatorFramework rename + post-v1.13 cite-cascade context | Preserved verbatim |
| All other v1.x contracts | Preserved verbatim |

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_18.md` |
| Version | v1.18 |
| Filing event | HITL-gate-as-pause-trigger impl arc — Phase 1 step 3 (OPTIONAL) absorption per checkpoint `20260524-211500-u-rt-94-fork-filed-reading-a-path-1-ratified.md` Phase 1 step 3 + CP spec v1.17 adjacent defect (i) + runtime spec v1.26 adjacent defect (iii); operator AskUserQuestion 2026-05-24 close ("optional Phase 1 step 3") + session-resume ratification 2026-05-24 ("Proceed to phase 1 step 3") |
| Predecessor | `Spec_Control_Plane_v1_17.md` (v1.17 substantive content preserved verbatim outside the NEW §25.2.X sub-section) |
| Successor | (none — current canonical) |
| Co-published artifacts (this arc) | Workspace `CLAUDE.md` §2.3 CP row bump v1.17 → v1.18 (this commit OR next bookkeeping commit); CP plan v2.20 → v2.21 → v2.22 (Phase 2 step 4 — U-CP-58/59/60/61 absorption); harness-cp impl `HITLEscalationBrief.fail_class` annotation widening; harness-runtime impl U-RT-93 fixture revision (drop sentinel pattern; use `fail_class=None` directly) + U-RT-94 composer body Phase 3 step 9 |
| Downstream absorption owed (next arcs) | `HITLEscalationBrief.fail_detail_hash` parallel Optional widening per adjacent defect (i) (operator-discretion at follow-on arc; structurally-identical amendment shape); explicit construction-context discriminator per adjacent defect (ii) (foreclosed at v1.18 per FM-2; future arcs); `pause_trigger_origin: bool` derived span attribute at OD-side `hitl.gate.evaluated` namespace per §25.2.X.3 (OD spec / OD plan absorption); cluster-boundary edge declaration at plan-level per adjacent defect (iv) (implementation-planner revision-pass) |
| Operator authority | AskUserQuestion 2026-05-24 close ("optional Phase 1 step 3") at session post-fork-filing commit `347de9c` + session-resume user ratification 2026-05-24 ("Proceed to phase 1 step 3") at session post-runtime-spec-v1.26 commit `cc16fc8` |
| Contract-count change | None — `HITLEscalationBrief.fail_class` field-type widening is within C-CP-28, not a new contract surface |
| Fail-class-count change | None |
| Signature change at any Protocol | ZERO — `HITLEscalationBrief` is a typed payload (frozen dataclass), not a Protocol |
| Field-set change at any field set | ONE — `HITLEscalationBrief.fail_class` widened from `ValidatorFailClass` to `ValidatorFailClass | None = None` (backward-compatible default) |
| Acceptance criterion change at any contract | None at spec-side (CP plan U-CP-58/59/60/61 absorption AC re-decomposition is downstream absorption per (b); runtime plan U-RT-93 + U-RT-94 fixture/body absorption is Phase 3 steps 8 + 9) |
| Behavior change | None at canonical validator-failure callsites — field-type widening is backward-compatible (existing callers passing `ValidatorFailClass.X` continue to work unchanged). Behavior change at durable-async pause-trigger callsites: composer body at §14.8.8.1 step 1 can construct `HITLEscalationBrief(..., fail_class=None, ...)` without sentinel-value synthesis (was: impossible at v1.17 without breaking the non-Optional contract; runtime-side U-RT-93 fixture at commit `2cfc5dc` used sentinel pattern as workaround which v1.18 makes redundant) |
| Cross-axis cascade | ZERO at semantics layer — `HITLEscalationBrief` is intra-CP-axis (consumed by runtime composer + validator escalation gate composer; not by OD-side audit payload composers); CXA v2.10 unaffected; ADR-D1 / ADR-D3 / ADR-D5 / ADD / PRD unaffected; `ValidatorResult.fail_class: ValidatorFailClass | None` parallel Optional posture at v1.10 §25.2 line 170 preserved verbatim |
| Skill discipline | `spec-writer` Phase-7 narrow-scope spec-amendment application of operator-ratified Phase 1 step 3 disposition; fidelity-pure single-field-type widening with backward-compatible default; NO contract change; NO extension beyond authorized scope (4 adjacent defects surfaced at change-note for follow-on arcs per FM-2: `fail_detail_hash` parallel Optional consideration, explicit construction-context discriminator, ValidatorFailClass enum extension foreclosure, cluster-boundary edge declaration at plan-level); preservation audit PASSED |
| Date | 2026-05-24 |
