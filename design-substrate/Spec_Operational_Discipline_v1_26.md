# Spec: Operational Discipline — v1.26 (delta over v1.25)

---

## Change-note (v1.25 → v1.26)

**Status posture (PROPOSED 2026-05-28).** v1.26 is a canonical-reading amendment clarifying §C-OD-10 §10.3 + §C-OD-13 §13.1 per-deployment persona_tier classification reading per `.harness/class_1_fork_od_3_od_4_retire_ready_persona_tier_plumbing.md` operator-ratified 2026-05-28 (Q1=A + Q2=A + Q3=a + Q4=i + Q5=α). v1.25 body PRESERVED VERBATIM per delta-only-spec-file convention. Co-published with runtime spec v1.37 NEW `RuntimeConfig.persona_tier: PersonaTier = PersonaTier.SOLO_DEVELOPER` field at §3 C-RT-03.

**Source of fix.** Fork doc §3 shared substrate + §6 architect-leaning recommendation Q5=(α) canonical-reading amendment clarifying persona_tier semantic-axis disambiguation. Empirical orientation surfaced a latent workspace defect: persona_tier is consumed at TWO semantic axes with distinct scope but no canonical disambiguation at the spec layer.

- **CP-axis per-step / per-workflow persona_tier** at CP spec v1.17 §6.5 `StepEffectiveBinding.persona_tier` — sourced from `WorkflowManifestEntry.persona_tier` (CP spec §6.1) per workflow_driver.py emission at `workflow.persona_tier` span attribute (root span only); drives gate-level / engine-class / HITL-matrix decisions per CP spec §6.5.x evaluators.

- **OD-axis per-deployment persona_tier** at OD spec §C-OD-10 §10.3 + §C-OD-13 §13.1 — the deployment-classification reading: solo-developer / team-binding / multi-tenant-compliance ARE deployment classes (a deployment binds to exactly one tier). Drives sampler base_rate + redaction discipline at the SDK / wrapper boundary; sourced from `RuntimeConfig.persona_tier` (runtime spec v1.37 NEW field).

The two surfaces co-exist by design. Pre-v1.26, the spec was silent on the disambiguation. v1.26 surfaces the canonical reading.

---

## §1. Canonical-reading amendments

### §1.1 §C-OD-13 §13.1 — per-deployment persona_tier reading

**Canonical reading at v1.26.** The persona-tier column at the §13.1 per-persona-tier override gradient table (rows solo-developer / team-binding / multi-tenant-compliance) refers to the **deployment binding's persona_tier classification** — i.e., a deployment is bound to exactly one persona tier at startup via `RuntimeConfig.persona_tier` (runtime spec v1.37 NEW field at §3 C-RT-03). This is DISTINCT from CP-axis per-step / per-workflow `StepEffectiveBinding.persona_tier` (CP spec v1.17 §6.5) which drives per-step gate-level / engine-class / HITL-matrix decisions.

**Composition site.** `materialize_span_processor_stage` (`harness-runtime/.../lifecycle/span_processor.py`) reads `config.persona_tier` and threads through to `RedactionSpanProcessor(persona_tier=config.persona_tier, ...)`. The processor consumes the deployment-binding persona_tier for §13.1 row-3 (multi-tenant-compliance) non-toggleability enforcement via NEW typed `MultiTenantOverrideRefusedError` raised at ctor when `redacted_attributes=frozenset()` (empty-disable) is supplied at multi-tenant-compliance.

**Backward-compatibility posture.** §13.1 body text PRESERVED VERBATIM. The 3-row table + mechanism column + override-mechanism column + audit-trail discipline column are unchanged. v1.26 is the canonical-reading amendment naming the read site (`RuntimeConfig.persona_tier`); §13.1 row semantics are unchanged.

**Scope discipline.** v1.26 does NOT change §13.1 mechanism column behavior at solo-developer. Solo-developer's "OPERATOR_SELF_REDACT" + "Per-session toggle at the in-process collector configuration" mechanism is BEYOND deployment-binding-time scope — it operates at runtime via operator-session control. v1.26 covers deployment-binding-time persona_tier resolution; per-session toggle mechanism is deferred to a follow-on arc.

### §1.2 §C-OD-10 §10.3 — per-deployment base_rate envelope materialization

**Canonical reading at v1.26.** The §10.3 8-row table is materialized at the sampler binding via the canonical `PER_CELL_BASE_RATE_ENVELOPE` substrate (U-OD-12 at `harness-od/.../base_rate_set_and_envelope.py`) keyed by `CellID(persona_tier=config.persona_tier, deployment_surface=config.deployment_surface)`. The 8-row table BYTE-EXACT:

| Persona tier × deployment surface | Base-rate default |
|---|---|
| solo-developer × local-development | 1.0 |
| solo-developer × self-hosted-server | 1.0 |
| solo-developer × managed-cloud | 1.0 |
| team-binding × local-development | 0.5 |
| team-binding × self-hosted-server | 0.1 |
| team-binding × managed-cloud | 0.1 |
| multi-tenant-compliance × self-hosted-server | 0.2 |
| multi-tenant-compliance × managed-cloud | 0.2 |

**Excluded cell.** `multi-tenant-compliance × local-development` has NO §10.3 row (structurally incoherent: multi-tenant requires shared backend; local-development is single-operator). Raises `CellBindingViolation` at `reject_excluded_cell(cell)` invocation pre-lookup at materializer; wraps as `TracerProviderBindError` per `materialize_tracer_provider_stage` exception contract.

**Composition site.** `materialize_tracer_provider_stage` (`harness-runtime/.../lifecycle/tracer_provider.py`) reads `config.persona_tier` + `config.deployment_surface`; constructs `CellID`; invokes `reject_excluded_cell`; resolves `base_rate = PER_CELL_BASE_RATE_ENVELOPE[cell].default_rate`; constructs `build_default_sampler(base_rate=base_rate)`. The pre-v1.26 module-level `_DEFAULT_SAMPLER: Final[Sampler] = build_default_sampler()` (forcing `base_rate=1.0` at every cell) RETIRED at runtime spec v1.37 co-publication.

**Backward-compatibility posture.** §10.3 body text PRESERVED VERBATIM. The 8-row table + envelope column ("Operator-tunable" / "0.1–1.0" / etc.) + footer ("Deferred to implementation discretion: ... specific base-rate numeric calibration at deployment-binding time") are unchanged. v1.26 names the materialization site; the table values themselves are spec-canonical at v1.2 verbatim.

**Scope discipline at envelope column.** v1.26 materializes the "Base-rate default" column. The "Base-rate envelope" column (operator-tunable ranges for team-binding + multi-tenant-compliance cells) requires a sub-config extension at `RuntimeConfig.otel` or sibling. Deferred to a follow-on operator-discretion arc.

---

## §2. Cross-artifact cite-cascade

| Artifact | §-cite | Disposition at v1.26 |
|---|---|---|
| Runtime spec v1.37 | §3 C-RT-03 NEW `persona_tier` field | Co-published this arc — canonical declaration site for the deployment-binding-time persona_tier field. The OD spec consumes this field at the materializer composition sites enumerated at §1.1 + §1.2. |
| CP spec v1.17 | §6.5 `StepEffectiveBinding.persona_tier` | PRESERVED VERBATIM. The per-step / per-workflow persona_tier reading at CP-axis is distinct from the per-deployment persona_tier reading at OD-axis; v1.26 §1.1 surfaces the disambiguation. ZERO cross-axis cascade at CP layer. |
| ADR-D6 v1.2 | §1.4 per-persona-tier override gradient | PRESERVED VERBATIM. v1.26 does NOT amend the ADR-D6 §1.4 gradient table; it surfaces the deployment-binding reading at the spec composition layer. |
| harness-od/CLAUDE.md | §4.1 OD-3 + OD-4 rows | Updated this arc — OD-3 transit PARTIAL → RETIRE-READY (substrate-criterion-B MET: base_rate envelope materialized at sampler); OD-4 transit PARTIAL → RETIRE-READY (substrate-criterion-B MET: per-persona toggle wired at redactor); both terminal in-CLI; full RETIRED gates on deployment-time-opt-in exercise per X-AL-2 + sub-species 7 deployment-time-opt-in-gate precedent. |
| Workspace `CLAUDE.md` §2.3 OD spec row | v1.25 → v1.26 version bump | Co-published this arc. |
| OD plan v2.24 | §3 U-OD-04 sampler binding + redactor unit | OD plan v2.25 single-arc absorption co-published this arc. |

ZERO cross-axis cascade at CXA / IS / AS / ADR / ADD / PRD per Q5=(α) operator-ratified scope discipline. Intra-OD + intra-Runtime + intra-harness-od substrate only.

---

## §3. Sections preserved verbatim from v1.25

ALL v1.25 + v1.24 + ... + v1.2 lineage preserved verbatim per delta-only-spec-file convention. ZERO body text change at any §C-OD-NN contract surface. ZERO contract removal. ZERO new contract. ZERO acceptance-criterion change. ZERO §10.3 table value change. ZERO §13.1 row text change.

---

## §4. Adjacent observations

(a) **Per-deployment vs per-step persona_tier semantic-axis disambiguation.** Pre-v1.26, the workspace carried a latent semantic-axis defect: persona_tier is consumed at TWO semantic axes (CP per-step, OD per-deployment) without canonical disambiguation at the spec layer. v1.26 §1.1 surfaces the disambiguation; future spec arcs MAY canonicalize the disambiguation at ADR-D5 v1.3 §1.5 (persona-tier ladder declaration site) for cross-axis discoverability.

(b) **Reading (a) field-plumbing-no-behavior-change scope.** Per advisor pre-substantive consultation Q5=(α) operator-ratified scope, v1.26 does NOT change §13.1 row text or §10.3 table values. The amendment is purely canonical-reading + material-binding-site declaration. RedactionSpanProcessor MVP strip-at-all-3-tiers behavior PRESERVED VERBATIM; multi-tenant-compliance non-toggleability NEW at runtime-impl layer via `MultiTenantOverrideRefusedError` enforces §13.1 row 3 ("Operator cannot enable raw content capture") at construction-time.

(c) **§10.3 envelope column deferred.** The "Base-rate envelope" column (operator-tunable ranges per cell) requires a sub-config extension at `RuntimeConfig.otel` or sibling. v1.26 materializes the default column only. Operator-discretion timing.

(d) **Substrate pre-landed; consumer lifted.** Mirror-shape to OD-3 batch-34 + OD-4 batch-35 substrate-retirement precedents. `PER_CELL_BASE_RATE_ENVELOPE` (U-OD-12) + `PER_PERSONA_TIER_REDACTION` (U-OD-16) + `CellID` (U-OD-01) + `reject_excluded_cell` already canonical at HEAD pre-arc. v1.26 lifts the consumer site at the runtime materializer; ZERO new OD substrate authored.

(e) **NEW species candidate at workflow v1.12 §7.4.7.2 — `cross-axis-semantic-axis-disambiguation-deferred-then-surfaced`.** A workspace-internal semantic-axis defect persists across multiple spec arcs (persona_tier consumed at CP per-step + OD per-deployment without disambiguation), then surfaces at a fork-doc arc that lifts the consumer site. Distinct closure-event-class candidate at species-3 or species-5 sub-species column.

(f) **Runtime spec v1.37 (vi) duplicate-substrate-authoring catalogue propagation.** v1.37 (vi) catalogues `redundant-substrate-authoring-at-pre-substantive-grep-gap` as candidate at species-3 sub-species column. v1.26 honors the catalogue by citing the canonical OD substrate (`PER_CELL_BASE_RATE_ENVELOPE` + `cost_attribution_dashboard_binding.base_rate_for`) at §1.2 to prevent future duplicate-substrate-authoring at cite-cascade.

---

## §5. Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Operational_Discipline_v1_26.md` |
| Status | **Proposed (v1.26)** — canonical-reading amendment clarifying §C-OD-10 §10.3 + §C-OD-13 §13.1 per-deployment persona_tier classification reading |
| Predecessor | v1.25 (2026-05-28 §C-OD-27 phantom-`U-RT-30`-cite resolution) |
| Substrate consumed | `.harness/class_1_fork_od_3_od_4_retire_ready_persona_tier_plumbing.md`; runtime spec v1.37 NEW `RuntimeConfig.persona_tier` field; `PER_CELL_BASE_RATE_ENVELOPE` (U-OD-12 at `base_rate_set_and_envelope.py`); `PER_PERSONA_TIER_REDACTION` (U-OD-16 at `redaction_gradient.py`); `CellID` + `reject_excluded_cell` (U-OD-01 at `observability_matrix.py`); 16 NEW tests at `tests/test_persona_tier_plumbing.py` |
| Successor | OD plan v2.24 → v2.25 absorption (co-published this arc); H_T-OD-3 + H_T-OD-4 PARTIAL → RETIRE-READY transit at batch-N retirement event filing (co-published this arc OR follow-on arc per operator-discretion timing) |
| Revision policy | In-CLI per workspace `CLAUDE.md` §4.3 (design-substrate/ canonical; back-flow deprecated 2026-05-15) |
| Date | 2026-05-28 |

---

*End of `Spec_Operational_Discipline_v1_26.md` delta. Per delta-only convention, v1.25 + v1.24 + ... + v1.2 file bodies PRESERVED VERBATIM and remain canonical-at-authoring for their respective scopes. v1.26 is the operative canonical reading for §C-OD-10 §10.3 + §C-OD-13 §13.1 per-deployment persona_tier classification going forward.*
