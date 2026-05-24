# Specification — Control Plane v1.17

## Change-note (v1.16 → v1.17)

**Scope of revision.** Narrow-scope C-CP-06 §6 amendment — authors NEW §6.5 sub-section extending the per-step override evaluator output (the carrier the v1.6 narrative names `StepEffectiveBinding` at §6.2 + line 282 + line 345) with one new field `persona_tier: PersonaTier`, and widens the v1.6-narrative `resolve_step_binding(manifest_entry, step_id)` signature with one new keyword-only parameter `persona_tier: PersonaTier` (no default; the caller is responsible for resolving persona tier upstream from `WorkflowManifestEntry` per §6.1 / routing-manifest per C-CP-01 §1.3 prior to invocation). Authored per Reading A path 1 ratification at fork doc `.harness/class_1_fork_u_rt_94_webhook_delivery_composer_binding_chain_absence.md` §3.1 step 2 (operator AskUserQuestion 2026-05-24 close). The fork-doc §2 empirical-verification finding confirmed canonical `StepEffectiveBinding` lacks `persona_tier` at HEAD `ba072f4` — the durable-async cell synchrony branch authored at runtime spec v1.24 §14.8.8 is dead-code-in-production because `_evaluate_cell_synchrony_tolerant` returns `None` for every canonical-shape binding via getattr-tolerant fallback. v1.17 resolves the canonical-shape gap at the spec layer (CP-side carrier amendment) so the runtime-side helper consumes `binding.persona_tier` directly post-impl-arc. Operator-ratified 2026-05-24. ZERO change to existing field-sets at `WorkflowManifestEntry` (§6.1), `HITLPlacement` (C-CP-17), `HITLResult` (C-CP-17), `EngineClass` (C-CP-07), or any v1.x carrier. ZERO change to `resolve_step_binding` return type (still `StepEffectiveBinding`). ZERO new fail class. ZERO new span attribute. ZERO new enum. ZERO behavior change at canonical CP-side composition — the carrier just gains a field; the resolver just gains a parameter sourced from canonical upstream surfaces. ZERO cross-axis cascade — OD spec / CXA v2.10 / ADR / ADD / PRD unaffected.

**v1.16 substantive content preserved verbatim.** All v1.16 NEW §26.8 sub-section (§26.8.1 carrier definition + §26.8.2 field semantics + §26.8.3 composition with §26.6 invariants + §26.8.4 verbatim-layer integrity + §26.8.5 `attempt_resume` async signature widening canonical reading) preserved unchanged. All v1.15 §19.1.1 (NEW) canonical 4-axis statement preserved verbatim. All v1.14 4-cite-cell amendments preserved. All v1.13 §28 ValidatorFramework rename preserved. All v1.12 §25.2.1 9th-field `workflow_id` amendment preserved. All v1.11 §26.2 `PauseReason` → `WorkflowPauseReason` rename + §26 NEW NOTE preserved. All v1.10 §26 / §27 / §28 substantive content preserved verbatim. All v1.6 §6 / §14.7 substantive content preserved verbatim. All v1.2 §6.1-§6.4 substantive content preserved verbatim.

**Source of fix.** Ratified Class 1 fork doc at `.harness/class_1_fork_u_rt_94_webhook_delivery_composer_binding_chain_absence.md` §3.1 (Reading A path 1) + operator AskUserQuestion 2026-05-24 close ("Reading A path 1 — author full webhook binding chain + StepEffectiveBinding.persona_tier extension"). Fork doc §1 empirical-grep at HEAD `ba072f4` confirmed `StepEffectiveBinding` (frozen, `extra="forbid"`) declares 6 fields {`step_id`, `model_binding`, `engine_class`, `hitl_placement`, `override_applied`, `override_audit_ref`} but NOT `persona_tier`. The downstream runtime spec v1.24 §14.8.8.3 helper signature reads `matrix_cell_for(binding.persona_tier, binding.engine_class).synchrony_class` per CP spec v1.2 §18.1 — the field reference is structurally well-formed at the spec layer but the canonical carrier shape is absent. Reading A path 1 closes the gap by amending C-CP-06 §6.2 / line 282 / line 345 narrative to declare the extended field-set as canonical at v1.17.

**Authority basis for fix direction.** C-CP-06 §6.2 is the per-step override evaluator surface; its return-value (the per-step effective binding) is the canonical handoff from manifest-declaration tier to per-step composition tier. The synchrony-class × persona-tier × engine-class composition at C-CP-18 §18.1 is the H_T-CP-2 territory (persona-tier-aware HITL composition); the carrier handoff at §6.2 is the natural site for persona-tier landing because (a) the resolver already consumes manifest-level data and persona tier is manifest-resolvable upstream per Persona §3 + C-CP-01 §1.3 routing-manifest tier resolution (the routing-manifest persona-tier resolution is established at C-CP-01 §1.3 + Persona §3.1 four-class set); (b) the consuming surface (C-CP-18 §18.1 synchrony-class matrix) accepts `persona_tier` as a row dimension; (c) downstream runtime-side composers (runtime spec v1.24 §14.8.8.3 `_evaluate_cell_synchrony_tolerant`) reference `binding.persona_tier` directly. Reading A path 1 is the spec-faithful resolution per fork doc §4 advisor recommendation ("identical-shape to `[[fork-validator-composer-arc-stage-4-absence]]` — mirror precedent").

**Single amendment site (1 NEW sub-section).**

| Site | Amendment shape |
|---|---|
| **§6.5 (NEW) — `StepEffectiveBinding.persona_tier` field-set extension + `resolve_step_binding` signature widening** | NEW sub-section appended at §6 (v1.2 §6.1-§6.4 + v1.6 §6.2 narrative line 282 + line 345 preserved verbatim outside this addition). Authors the canonical field-set extension of the per-step effective binding carrier (the v1.6 narrative `StepEffectiveBinding` — see §6.5.1 canonical-name reconciliation) adding `persona_tier: PersonaTier` field; amends the `resolve_step_binding(manifest_entry, step_id)` signature with one new keyword-only parameter `persona_tier: PersonaTier`. Source-of-truth-upstream: `WorkflowManifestEntry` persona-tier resolution per C-CP-01 §1.3 routing-manifest tier resolution + Persona §3 four-class set; the resolver caller is responsible for resolving persona tier prior to invocation, not the resolver itself. |

**Adjacent harmonization sites.** None — the v1.6 narrative line 282 (`binding : StepEffectiveBinding, // per C-CP-06 §6.2 per-step override evaluator output`) and v1.6 narrative line 345 (`binding = resolve_step_binding(manifest_entry, s.id)`) are preserved verbatim outside this addition. The §6.5 amendment is recorded as a canonical-reading amendment over the v1.6 narrative per delta-only spec-chain preservation discipline (the v1.6 file is NOT edited; consumers reading the delta chain interpret the v1.6 narrative AS canonically supplemented at v1.17 §6.5 per this change-note). The §6.1 `WorkflowManifestEntry` schema is preserved verbatim (persona_tier sourcing is upstream of the resolver per fork doc §3.1 step 2 "sourced from manifest_entry or routing-manifest resolution per scoping doc Q4"; v1.17 does NOT mandate persona_tier as a `WorkflowManifestEntry` field — the resolution mechanism is operator-discretion per existing canonical routing-manifest surfaces).

**Sections preserved verbatim from v1.16.** All v1.16 NEW §26.8 + all v1.15 §19.1.1 + all v1.14 / v1.13 / v1.12 / v1.11 / v1.10 / v1.6 / v1.2 substantive content preserved verbatim.

**Status posture.** Proposed (v1.16) → **Proposed (v1.17)**. v1.17 is a fidelity-pure additive amendment — one NEW field on the per-step effective binding carrier + one signature widening (no default; caller responsibility). NO v1.16 contract removed; NO v1.16 contract re-decomposition; NO v1.16 field-set modified. Contract count unchanged at 28. Fail-class count unchanged. Signature change at any contract: ONE — `resolve_step_binding(manifest_entry, step_id, *, persona_tier: PersonaTier)` gains one keyword-only parameter (no default; required at all callsites; backward-INcompatible at the impl-level callsite enumeration per fork doc §3.1 step 6 "Amend `resolve_step_binding` callers (find via grep; likely ~3-5 callsites)"). Field-set change at any field set: ONE — `StepEffectiveBinding` (the v1.6-narrative per-step override evaluator output) gains one field `persona_tier: PersonaTier`. Acceptance criterion change at any contract: NONE at spec-side (CP plan U-CP-13 absorption AC re-decomposition is downstream absorption per (b) below). Behavior change at canonical CP-side composition: NONE — the carrier just gains a field; the resolver just gains a parameter sourced from canonical upstream surfaces; the existing §18.1 synchrony-class matrix consumption pattern is preserved.

**Downstream absorption owed (post-v1.17).**

(a) Workspace `CLAUDE.md` §2.3 CP spec row version bump (v1.16 → v1.17); co-published this arc.

(b) **CP plan v2.20 → v2.21 → v2.22** — single-unit-body amendment at U-CP-13 (per-step-override-evaluator unit; the unit landing `StepEffectiveBinding` Pydantic class + `resolve_step_binding` callable per `harness-cp/src/harness_cp/per_step_override_evaluator.py`). Add new AC covering the `persona_tier` field addition + `resolve_step_binding` signature widening + callsite enumeration update. NO new unit; NO new cluster; NO DAG topology change. Co-published next arc (Phase 2 step 4 per checkpoint plan).

(c) **harness-cp impl** updates: `harness-cp/src/harness_cp/per_step_override_evaluator.py:117` — APPEND `persona_tier: PersonaTier` field to `StepEffectiveBinding(BaseModel)` (frozen, `extra="forbid"` preserved). `harness-cp/src/harness_cp/per_step_override_evaluator.py:NNN` — AMEND `resolve_step_binding(manifest_entry, step_id)` signature: add `persona_tier: PersonaTier` keyword-only parameter. Update all callsites (~3-5 per fork doc §3.1 step 6) across harness-cp + harness-runtime + tests + fixtures to pass the new parameter. Co-published next arc (Phase 3 step 6 per checkpoint plan).

(d) **harness-runtime impl** updates: ZERO at v1.17 spec-side; downstream consumption authored at:
- U-RT-93 helper revision (Phase 3 step 8 per checkpoint plan) — drop the `getattr(binding, "persona_tier", None)` tolerance now that the canonical field exists; consume `binding.persona_tier` directly.
- U-RT-94 composer body (Phase 3 step 9) — consume the typed `binding.persona_tier` at the cell synchrony resolution path.
- U-RT-95 e2e (Phase 3 step 10) — regression-gate fixtures now construct `StepEffectiveBinding(..., persona_tier=...)` per typed shape; old fixtures lacking the field are no longer valid.

(e) **OD spec / OD plan / OD impl**: ZERO — the `persona_tier` field is intra-CP-axis (carrier on the per-step effective binding); the OD-side audit-payload composers (`PauseResumeAuditPayload` at §C-OD-30.4 + `CostRecordAuditPayload` at §C-OD-26.6) do not consume `StepEffectiveBinding`. ZERO OD cascade.

(f) **CXA v2.10**: ZERO — no new cross-axis edge; the field is internal to the CP-side per-step override evaluator's typed output; no consumer crosses the axis boundary.

(g) **ADR-D5 / ADD / PRD**: ZERO retag owed — `StepEffectiveBinding.persona_tier` is a derivative carrier field within C-CP-06 §6.2 (already ADR-D5 §1.3.2 4-axis floor formula territory — `persona_tier_floor` is one of the 4 axes per §19.1.1 (i) canonical statement; v1.17 makes the carrier-level field landing explicit). ZERO upstream-artifact revision triggered.

**Adjacent defects surfaced (NOT patched per FM-2 no-extension discipline).**

(i) **`HITLEscalationBrief.fail_class` non-Optional vs runtime spec v1.24 §14.8.8.1 step 1 `fail_class=None` divergence.** Per fork doc §2.2 finding 3 + checkpoint §"Notes" finding 3: canonical `HITLEscalationBrief` at C-CP-28 §25.2 declares `fail_class: ValidatorFailClass` as non-Optional, but runtime spec v1.24 §14.8.8.1 step 1 calls for the composer body to construct a brief with `fail_class=None`. This is a third spec/code divergence surfaced at impl(U-RT-93). v1.17 does NOT patch this — the resolution choice (amend `HITLEscalationBrief.fail_class` at C-CP-28 §25.2 to `ValidatorFailClass | None = None` per checkpoint Phase 1 step 3 OR runtime-side workaround via sentinel value pattern) is orthogonal to the `StepEffectiveBinding.persona_tier` extension and was explicitly scoped out at operator AskUserQuestion 2026-05-24 close ("optional Phase 1 step 3"). Surfaced; routed to operator-discretion arc at Phase 1 step 3 OR runtime-side absorption.

(ii) **Persona-tier sourcing mechanism at the resolver caller.** v1.17 declares `resolve_step_binding(..., *, persona_tier: PersonaTier)` accepts persona_tier as a required keyword parameter sourced upstream from canonical surfaces (`WorkflowManifestEntry` per §6.1 OR routing-manifest tier resolution per C-CP-01 §1.3 OR Persona §3 four-class set resolution). The specific upstream surface is NOT mandated at v1.17 — the resolver is a pure function over (manifest_entry, step_id, persona_tier); the caller is responsible for persona tier resolution prior to invocation. Future arcs may explicitly enumerate the resolver-caller persona-tier sourcing at the workflow_driver step-dispatch site OR at the bootstrap composer-step level. Surfaced; NOT patched at v1.17 per FM-2 — the canonical resolver signature is sufficient at spec layer; implementer-discretion at the caller-side per `[[halt-route-split-AC-pattern]]` precedent.

(iii) **`StepEffectiveBinding` future-extensibility.** v1.17 adds one field `persona_tier: PersonaTier` to the canonical carrier. Future arcs may need additional per-step typed fields (e.g., `gate_level_floor: GateLevel` per §19.1.1 (iv) 4-axis composition input; `deployment_surface: DeploymentSurface` per §19.3 D2-layer sandbox composition; `mcp_trust_floor: MCPTrustTier` per C-AS-12). Surfaced; NOT patched at v1.17 per FM-2 — Reading A path 1 authorized ONLY `persona_tier` field. Subsequent fields routed to follow-on operator-discretion arcs as the consuming surfaces require them.

(iv) **Backward-incompatible signature change at `resolve_step_binding`.** Per the operator instruction ("amend `resolve_step_binding()` signature to accept `persona_tier` parameter sourced from manifest_entry/routing-manifest") AND fork doc §3.1 step 2 ("Co-publish at C-CP-06 §6.2 amendment"), v1.17 mandates the new keyword-only parameter as **required** (no default). This is a backward-incompatible signature change: existing callers at `harness-runtime/tests/test_lifecycle_runtime_tool_dispatcher.py:138` + `harness-cp/src/harness_cp/workflow_driver.py:NNN` step-dispatch site + downstream test fixtures construct the binding without persona_tier and MUST be updated at the impl-arc landing (per fork doc §3.1 step 6 "Update test fixtures across harness-cp + harness-runtime that construct StepEffectiveBinding(...) with no persona_tier"). Alternative shape (kw-only with `None` default + post-construction validation) was considered but rejected per the operator instruction explicit phrasing — the caller is responsible. Surfaced; this is the AUTHORIZED breaking change at v1.17 (per Reading A path 1); the impl-arc absorption per checkpoint Phase 3 step 6 enumerates the callsite update obligation.

---

## §6.5 (NEW) — `StepEffectiveBinding.persona_tier` field-set extension + `resolve_step_binding` signature widening

### §6.5.1 Canonical-name reconciliation

The v1.6 narrative at line 282 + line 345 names the per-step override evaluator output `StepEffectiveBinding`:

> v1.6 line 282: `binding      : StepEffectiveBinding,        // per C-CP-06 §6.2 per-step override evaluator output`
>
> v1.6 line 345: `binding = resolve_step_binding(manifest_entry, s.id) per U-CP-14 (§6.2 per-step override surface).`

The canonical Pydantic class body is at `harness-cp/src/harness_cp/per_step_override_evaluator.py:117` (declared frozen + `extra="forbid"`). v1.6 narrative establishes the carrier NAME at the spec layer; v1.7 → v1.16 preserved verbatim; v1.17 §6.5 authors the CANONICAL FIELD-SET EXTENSION at the spec layer (matching the impl-side Pydantic class body authoring pattern established at C-CP-13 §13.5 HandoffContext + C-CP-26 §26.2 PauseSnapshot precedent).

### §6.5.2 Carrier field-set extension

The v1.6-narrative `StepEffectiveBinding` (the per-step override evaluator output per §6.2) is canonically read at v1.17 as carrying the following 7-field set:

| Field | Type | Source | Semantics |
|---|---|---|---|
| `step_id` | `str` | manifest_entry step enumeration | Step identifier within the workflow manifest |
| `model_binding` | `ModelBinding` | manifest_entry default + per-step opt-in override per §6.2 | Model binding selected for this step (canonical at C-CP-13 §13.5) |
| `engine_class` | `EngineClass` | manifest_entry per C-CP-07 §7.1 closed five-element taxonomy | Engine class bound at workflow manifest per C-CP-07 §7.1 |
| `hitl_placement` | `HITLPlacement \| None` | manifest_entry `hitl_placements` per §6.1 + per-step override | HITL placement selected for this step (canonical at C-CP-17 §17.1) |
| `override_applied` | `bool` | derived: any per-step opt-in override evaluated per §6.2 | Whether per-step opt-in override syntax fired for this step |
| `override_audit_ref` | `LedgerEntryRef \| None` | C-IS-05 entry shape per §6.4 audit-surface composition | Reference to the audit-ledger entry emitted at workflow-binding time per §6.4 when an override was applied; None when `override_applied=False` |
| **`persona_tier`** (NEW at v1.17) | **`PersonaTier`** | **routing-manifest tier resolution per C-CP-01 §1.3 OR `WorkflowManifestEntry` per §6.1 (operator-discretion at canonical-upstream surface)** | **Persona tier resolved for this workflow step. Sourced upstream of the resolver per Persona §3.1 four-class set; consumed at C-CP-18 §18.1 synchrony-class × persona-tier × engine-class composition matrix.** |

The 6 v1.6-narrative-preserved fields are unchanged; the NEW 7th field `persona_tier` is the v1.17 amendment.

### §6.5.3 `resolve_step_binding` signature widening (canonical reading)

The v1.6-narrative `resolve_step_binding(manifest_entry, s.id)` signature at line 345 is canonically read at v1.17 as:

```python
def resolve_step_binding(
    manifest_entry: WorkflowManifestEntry,
    step_id: str,
    *,
    persona_tier: PersonaTier,  # NEW at v1.17; required keyword-only (no default)
) -> StepEffectiveBinding: ...
```

**Source-of-truth-upstream for `persona_tier`.** The caller is responsible for resolving persona tier prior to invocation. The canonical upstream surfaces are:

1. **`WorkflowManifestEntry`** per §6.1 — the manifest entry MAY carry persona-tier resolution at the per-workload level (extension to the v1.2 §6.1 schema is operator-discretion at follow-on arcs per adjacent defect (iii)).
2. **Routing-manifest tier resolution** per C-CP-01 §1.3 — the routing manifest already declares the per-workload persona tier surface at the C-CP-01 routing tier; the resolver caller (the workflow-driver step-dispatch site) reads from this surface.
3. **Persona §3.1 four-class set resolution** — for workflows that route through capability-based tier resolution per Persona §3 (the four-class set {solo-developer, team-binding, team-binding+, enterprise} per ADR-D1).

The specific upstream surface is implementer-discretion at the resolver-caller site per adjacent defect (ii). v1.17 mandates ONLY that the parameter is required at the resolver-callee site; the resolver is a pure function over `(manifest_entry, step_id, persona_tier)`.

**Backward-INcompatibility.** No default. Existing callers at `harness-cp` + `harness-runtime` tests + fixtures MUST be updated at the impl-arc landing per checkpoint Phase 3 step 6. Per adjacent defect (iv): this is the AUTHORIZED breaking change at v1.17 per Reading A path 1.

### §6.5.4 Composition with §18.1 synchrony-class matrix

The C-CP-18 §18.1 synchrony-class × persona-tier × engine-class composition matrix (preserved verbatim from v1.2) is the canonical consumer of `binding.persona_tier`:

```python
matrix_cell_for(binding.persona_tier, binding.engine_class).synchrony_class
```

Pre-v1.17, this composition path was structurally well-formed at the spec narrative but unreachable at production code (canonical `StepEffectiveBinding` lacked `persona_tier`; runtime helper `_evaluate_cell_synchrony_tolerant` returned `None` via getattr-tolerant fallback at every production callsite per fork doc §2.2 finding). Post-v1.17 + impl-arc landing per Phase 3 steps 6 + 8 + 9, the composition path is reachable at production callers — the durable-async cell synchrony branch authored at runtime spec v1.24 §14.8.8 is no longer dead-code-in-production.

### §6.5.5 Verbatim-layer integrity

The v1.6 file (`Spec_Control_Plane_v1_6.md`) §6.2 narrative + line 282 + line 345 is NOT edited at v1.17 — delta-only spec-chain preservation discipline preserved per v1.13 §1.3 + v1.14 §1.3 + v1.15 §19.1.1.4 + v1.16 §26.8.4 verbatim-layer-integrity precedent. The §6.5.2 field-set extension + §6.5.3 signature widening at v1.17 are recorded as canonical-reading amendments over the v1.6 narrative; consumers reading the delta chain interpret the v1.6 narrative AS canonically supplemented at v1.17 §6.5 per this change-note.

The v1.2 file (`Spec_Control_Plane_v1_2.md`) §6.1 `WorkflowManifestEntry` schema is NOT edited at v1.17 — persona_tier sourcing is at the resolver-caller site, not at the manifest-entry-field-set site (per adjacent defect (iii)).

### §6.5.6 Field-set ordering stability

The v1.6-narrative carrier-field-set ordering (step_id → model_binding → engine_class → hitl_placement → override_applied → override_audit_ref) is preserved verbatim. The NEW field `persona_tier` is appended at field-set position 7; the canonical ordering at v1.17 is:

```
1. step_id              : str
2. model_binding        : ModelBinding
3. engine_class         : EngineClass
4. hitl_placement       : HITLPlacement | None = None
5. override_applied     : bool
6. override_audit_ref   : LedgerEntryRef | None = None
7. persona_tier         : PersonaTier        # NEW at v1.17 (no default — required)
```

The append-at-end discipline preserves construction-call ordering for existing positional-arg callers (none exist at canonical CP-side composition — all callers are kw-only per `StepEffectiveBinding(BaseModel)` Pydantic v2 convention with `extra="forbid"`).

---

## §2 — Preservation guarantees

| Element | Disposition |
|---|---|
| v1.16 NEW §26.8 (`ResumeContext` carrier + `attempt_resume` signature widening) | Preserved verbatim |
| v1.15 §19.1.1 (NEW) canonical 4-axis statement (§19.1.1.1-§19.1.1.4) | Preserved verbatim |
| v1.14 4-cite-cell canonical-reading amendment | Preserved verbatim |
| v1.13 §28 ValidatorFramework rename | Preserved verbatim |
| v1.12 §25.2.1 9th-field `workflow_id` amendment | Preserved verbatim |
| v1.11 §26.2 `PauseReason` → `WorkflowPauseReason` rename + §26 NEW NOTE | Preserved verbatim |
| v1.10 §26 / §27 / §28 substantive content | Preserved verbatim |
| v1.6 §6 narrative (line 282 + line 345 `StepEffectiveBinding` + `resolve_step_binding(manifest_entry, s.id)`) | Preserved verbatim — v1.17 §6.5 (NEW) appended; the field-set extension + signature widening recorded as canonical-reading amendment at §6.5.2-§6.5.3; v1.6 file NOT edited |
| v1.6 §14.7 substantive content | Preserved verbatim |
| v1.2 §6.1 `WorkflowManifestEntry` schema | Preserved verbatim — `persona_tier` sourcing is at the resolver-caller site per §6.5.3; manifest-entry-field-set is NOT extended at v1.17 |
| v1.2 §6.2 Per-step annotation override syntax | Preserved verbatim |
| v1.2 §6.3 Per-step opt-in scope | Preserved verbatim |
| v1.2 §6.4 Audit-surface composition | Preserved verbatim |
| v1.2 §18.1 synchrony-class × persona-tier × engine-class matrix | Preserved verbatim — §6.5.4 documents the matrix as the canonical consumer of `binding.persona_tier` post-v1.17 |
| v1.2 §19.1 / §19.1.1 4-axis floor formula | Preserved verbatim — `persona_tier_floor` per §19.1.1 (i) was already canonical; v1.17 makes the per-step carrier-level field landing explicit |
| C-CP-17 §17.1 HITLResult type + HITLPlacement enum | Preserved verbatim |
| C-CP-18 §18.1 / §18.3 (synchrony matrix + both-by-tier overlay) | Preserved verbatim |
| C-CP-28 §25.2 `HITLEscalationBrief.fail_class` non-Optional declaration | Preserved verbatim at v1.17 — divergence with runtime spec v1.24 §14.8.8.1 step 1 surfaced as adjacent defect (i); NOT patched per FM-2 (routed to optional Phase 1 step 3 OR runtime-side workaround) |
| All other v1.x contracts | Preserved verbatim |

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_17.md` |
| Version | v1.17 |
| Filing event | HITL-gate-as-pause-trigger impl arc — Class 1 fork resolution Reading A path 1 absorption per `.harness/class_1_fork_u_rt_94_webhook_delivery_composer_binding_chain_absence.md` §3.1 step 2 (operator AskUserQuestion 2026-05-24 close) |
| Predecessor | `Spec_Control_Plane_v1_16.md` (v1.16 substantive content preserved verbatim outside the NEW §6.5 sub-section) |
| Successor | (none — current canonical) |
| Co-published artifacts (this arc) | Workspace `CLAUDE.md` §2.3 CP row bump v1.16 → v1.17 (this commit OR next bookkeeping commit); runtime spec v1.25 → v1.26 (Phase 1 step 2 — NEW webhook binding chain factory contract + amended §14.8.8.1 step 0 precondition); CP spec v1.17 → v1.18 OPTIONAL (Phase 1 step 3 — `HITLEscalationBrief.fail_class` Optional amendment per adjacent defect (i), if runtime-side does not absorb via sentinel); CP plan v2.20 → v2.21 → v2.22 (Phase 2 step 4 — U-CP-13 absorption); runtime plan v2.24 → v2.25 (Phase 2 step 5 — NEW U-RT-96 webhook binding chain + U-RT-94 re-author); impl arcs at Phase 3 steps 6-10 |
| Downstream absorption owed (next arcs) | `WorkflowManifestEntry` persona-tier-as-field-set-extension per adjacent defect (iii) (future arcs as consuming surfaces require); resolver-caller-site persona-tier sourcing mechanism per adjacent defect (ii) (workflow_driver step-dispatch site OR bootstrap composer-step level); `HITLEscalationBrief.fail_class` Optional amendment per adjacent defect (i) (Phase 1 step 3 OR runtime-side workaround); `StepEffectiveBinding` future-extensibility per adjacent defect (iii) (gate_level_floor, deployment_surface, mcp_trust_floor as consuming surfaces require) |
| Operator authority | AskUserQuestion 2026-05-24 close ("Reading A path 1 — author full webhook binding chain + StepEffectiveBinding.persona_tier extension") at session post-fork-filing commit `347de9c` |
| Contract-count change | None — `StepEffectiveBinding` field-set extension + `resolve_step_binding` signature widening are within C-CP-06, not a new contract surface |
| Fail-class-count change | None |
| Signature change at any contract | ONE — `resolve_step_binding(manifest_entry, step_id, *, persona_tier: PersonaTier)` gains one keyword-only parameter (no default; backward-incompatible at impl-level callsite enumeration) |
| Field-set change at any field set | ONE — `StepEffectiveBinding` (per-step override evaluator output per v1.6 §6.2 narrative line 282) gains one field `persona_tier: PersonaTier` (required, no default) |
| Acceptance criterion change at any contract | None at spec-side (CP plan U-CP-13 absorption AC re-decomposition is downstream absorption per (b); runtime plan U-RT-93/94/95 AC re-authoring is Phase 2 step 5 + Phase 3 steps 8-10) |
| Behavior change | None at canonical CP-side composition — the carrier just gains a field; the resolver just gains a parameter sourced from canonical upstream surfaces; the existing §18.1 synchrony-class matrix consumption pattern is preserved AND made reachable at production callers (was dead-code-in-production at v1.16 per fork doc §2.2 finding) |
| Cross-axis cascade | ZERO at semantics layer — OD spec / OD plan / OD impl unaffected (the field is intra-CP-axis); CXA v2.10 unaffected (no new cross-axis edge); ADR-D5 / ADD / PRD unaffected (the `persona_tier_floor` per §19.1.1 (i) was already canonical at ADR-D5 §1.3.2 4-axis floor formula territory; v1.17 makes the per-step carrier-level field landing explicit) |
| Skill discipline | `spec-writer` Phase-7 narrow-scope spec-amendment application of operator-ratified Reading A path 1 disposition; fidelity-pure additive amendment (one NEW field on existing carrier + one signature widening with no default — backward-incompatible at impl-callsite enumeration per AUTHORIZED scope at adjacent defect (iv)); NO contract change; NO extension beyond authorized scope (4 adjacent defects surfaced at change-note for follow-on arcs per FM-2); preservation audit PASSED |
| Date | 2026-05-24 |
