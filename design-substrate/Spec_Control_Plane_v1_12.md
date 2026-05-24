# Specification — Control Plane v1.12

## Change-note (v1.11 → v1.12)

**Scope of revision.** Class 1 fork resolution absorption per `.harness/class_1_fork_step_execution_context_workflow_id_field_absence.md` (filed + ratified 2026-05-24 at HEAD `c413d40`; operator chose Path A — CP-spec amendment over Path B/C/D). The v1.6 §25.2.1 `StepExecutionContext` record (preserved verbatim through v1.7/v1.8/v1.9/v1.10/v1.11) is amended at v1.12 to add a **9th field `workflow_id: str`** sourced from `manifest_entry.workflow_id` at the driver composition site. The field resolves the OD spec v1.10 §C-OD-26.6.1 step 2 cite (`<workflow_id>` is the parent workflow's identifier from `step_context.workflow_id`) which was authored at OD-spec Sub-arc B publication arc (commit `0919a9b` 2026-05-24) ahead of the corresponding CP-spec surface availability — silent absorption of a CP-spec extension per X-AL-3.

**v1.11 substantive content preserved verbatim.** All v1.11 content outside the §25.2.1 9th-field addition + §25.3.3.4 composition prose extension preserved unchanged. The v1.11 §26.2 `WorkflowPauseReason` rename + §26 coexistence NOTE preserved. The v1.10 NEW §17.4 + §25 (C-CP-25 ValidatorFramework) + §26 + §27 chains preserved. The v1.6 NEW §25.2.1 8-field record extends to 9 fields; existing 8 fields preserved byte-exact (no type / cardinality / semantics change at any existing field).

**Source of fix.** Cost-axis production callsite migration arc opening per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` + OD plan v2.17 §0(b)(i)(vi) "Sub-arc B sequel adjacent-finding" + advisor pre-implementation gate per `[[advisor-before-substantive-work-for-cross-axis-blockers]]`:
- OD spec v1.10 §C-OD-26.6.1 step 2 cites `step_context.workflow_id` as the source for the canonical `cost:<workflow_id>:<step_action_id>` audit action_id pattern at the `CostRecordAuditPayload` typed carrier (NEW at v1.10).
- Empirical inventory at HEAD `c413d40`: `StepExecutionContext` (CP spec v1.6 §25.2.1, preserved verbatim through v1.11) has 8 fields; `workflow_id` is NOT among them. The workflow identifier is embedded as a substring of `parent_action_id` (composed as `f"workflow:{workflow_id}:step:{step_index}"` at `workflow_driver.py:598-600`) but is NOT a discrete field.
- Substring-parse alternative (advisor-flagged structurally brittle): `Identifier(workflow_id)` upstream does not document a colon-exclusion constraint; splitting `parent_action_id` on `:step:` silently mis-extracts if `workflow_id` contains the substring `:step:`.
- Path A (this amendment) chosen by operator over Path B (parse) / Path C (indefinite deferral) / Path D (file-only).
- Co-published artifacts: CP plan v2.17 → v2.18 (revision-pass at the §25.2.1 cluster anchor); harness-cp impl (StepExecutionContext field add + driver fill); harness-runtime impl (cost-attribution callsite migration consuming the new field); workspace CLAUDE.md + per-axis CLAUDE.md pointer bumps.

**One amendment site + one prose extension.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **§25.2.1 9th-field addition** | `StepExecutionContext` Pydantic v2 BaseModel gains 9th field `workflow_id: str` (NOT Optional — required at composition). Field semantics: the parent workflow identifier sourced from `manifest_entry.workflow_id` at the driver §25.3.3.4 dispatch site composition. The driver already has `manifest_entry.workflow_id` in scope at the composition site (per existing `workflow_driver.py:597-608` composition pattern); the new field is composed deterministically alongside the existing `parent_action_id` field which itself embeds the value (`f"workflow:{workflow_id}:step:{step_index}"`). Anti-extension invariant preserved: this is an ADDITIVE field surfacing an already-driver-tracked value as a discrete typed surface for consumer dispatchers + downstream OD-axis cost-attribution wiring — NOT a new design extension. ZERO behavior change for existing consumers (all 8 existing fields preserved verbatim; the new field is keyword-only at the `StepExecutionContext(...)` construction call). | Path A operator ratification 2026-05-24 + OD spec v1.10 §C-OD-26.6.1 step 2 cite reconciliation |
| **§25.3.3.4 composition prose extension** | The §25.3.3.4 step 4 driver composition prose ("v1.6 Path A amendment: the driver composes a StepExecutionContext per §25.2.1 from driver-tracked run-level state (`run_id`, `workflow_id`, `step_index`, `ctx.ledger_writer.actor`, run-scope idempotency key, plus the 4 MVP-default-bounded fields)") explicitly mentions `workflow_id` as already-driver-tracked at the composition site — v1.12 makes this surfacing operative-rather-than-incidental by extending the §25.2.1 record. Composition discipline prose at §25.2.1 amended to include `workflow_id` in the "4 fields composed deterministically" enumeration → "5 fields composed deterministically: `workflow_id`, `parent_action_id`, `parent_actor`, `parent_idempotency_key`, `step_index`". | Same as above |

**Status posture.** Proposed (v1.11) → **Proposed (v1.12)**. v1.12 is an additive field-extension patch — single field addition at §25.2.1 + one prose-extension at §25.3.3.4. No v1.11 contract re-decomposition; no signature change at any Protocol; no acceptance criterion change at any existing contract; no new contract; no fail-class change. ZERO removal of any v1.11 surface.

**Downstream absorption owed (post-v1.12).**
(a) Workspace `CLAUDE.md` §2.3 CP spec row version bump (v1.11 → v1.12).
(b) `Implementation_Plan_Control_Plane_v2_18.md` (co-published this arc) — U-CP-NN revision-pass at the §25.2.1 cluster anchor; AC + Files + Signatures lines absorb the 9th field.
(c) `harness-cp/src/harness_cp/workflow_driver_types.py` — Pydantic BaseModel field addition; `harness-cp/src/harness_cp/workflow_driver.py:597-608` driver composition site fill from `manifest_entry.workflow_id`.
(d) `harness-runtime/src/harness_runtime/lifecycle/cost_attribution_llm_dispatch.py` — `attribute_llm_dispatch_cost` signature widening (kwargs `workflow_id: str` + `parent_action_id: str`); `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:701` caller update (passes `step_context.workflow_id` + `step_context.parent_action_id`); replace local `_project_and_convert_audit_entry` helper with import of canonical `harness_od.cost_record_audit_writer._project_cost_record_to_audit_payload` (already landed at Sub-arc B `0919a9b`).
(e) `.harness/class_1_fork_step_execution_context_workflow_id_field_absence.md` §8 ratification footer documenting Path A applied at this v1.12 publication arc.
(f) Memory: `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` advance — cost-axis production-wiring CLOSED at this arc; pause/resume-axis status preserved STRUCK.

**Adjacent defects surfaced (not patched per FM-2 no-extension discipline).**

(i) **`parent_action_id` substring redundancy.** With `workflow_id` now a discrete field, `parent_action_id` (composed as `f"workflow:{workflow_id}:step:{step_index}"`) contains the redundant `workflow_id` substring. Consumers that need both `workflow_id` + `step_index` can read them discretely from `StepExecutionContext` fields without parsing `parent_action_id`. The string-composition format of `parent_action_id` is preserved verbatim per FM-2 — existing audit-ledger consumers (per C-IS-05 §5 hash-chain hash-input composition) depend on the string format byte-exact. Surfaced; the redundancy is bounded (string-format preserved for audit-trail hash-chain consumers; discrete fields available for typed consumers). Future v1.x revision MAY tighten if a structural-format change is independently motivated.

(ii) **OD spec v1.10 §C-OD-26.6.1 step 2 cite reconciliation.** OD spec v1.10 §C-OD-26.6.1 step 2 cite "from `step_context.workflow_id`" was authored at Sub-arc B publication arc (commit `0919a9b`) before this v1.12 amendment — the cite was implicitly forward-cite (no `StepExecutionContext.workflow_id` field existed at HEAD at the cite-authoring moment). This v1.12 amendment RESOLVES the implicit forward-cite. OD spec v1.10 §C-OD-26.6.1 step 2 prose preserved verbatim — the cite is now byte-exact resolvable to CP spec v1.12 §25.2.1 field `workflow_id`.

(iii) **OD plan v2.17 §0(b)(i)(vi) "from runtime context" phrasing.** OD plan v2.17 §0(b)(i)(vi) Sub-arc B sequel adjacent-finding documents the deferred production migration as requiring `workflow_id` + `parent_action_id` "from runtime context" — implicit acknowledgement that the source surface was unclear at OD-plan-authoring time. This v1.12 amendment RESOLVES the implicit ambiguity: "runtime context" = `StepExecutionContext` (the C-CP-25 §25.2.1 canonical step-level runtime context surface). OD plan v2.17 §0(b)(i)(vi) prose preserved verbatim at this v1.12 publication.

---

## §1 — §25.2.1 9th-field amendment (v1.12)

The v1.6 NEW §25.2.1 `StepExecutionContext` record (preserved verbatim through v1.7/v1.8/v1.9/v1.10/v1.11) is amended at v1.12 to add a 9th field `workflow_id: str`. The existing 8 fields preserved verbatim (type / cardinality / semantics / MVP-default convention all unchanged).

### §25.2.1 amended StepExecutionContext record (v1.12)

```text
record StepExecutionContext {
  workflow_id              : string         // v1.12 NEW — parent workflow identifier
                                            //   sourced from manifest_entry.workflow_id at
                                            //   driver §25.3.3.4 composition site (already in
                                            //   driver scope at workflow_driver.py:597-608);
                                            //   discrete surface for typed-consumer dispatchers
                                            //   + OD-axis cost-attribution audit-write wiring
                                            //   per OD spec v1.10 §C-OD-26.6.1 step 2 cite
  parent_action_id         : string         // composed: f"workflow:{workflow_id}:step:{step_index}"
                                            //   per existing pattern at workflow_driver.py
                                            //   (_append_step_ledger_entry); v1.12 NOTE — embeds
                                            //   workflow_id substring; preserved byte-exact for
                                            //   audit-trail hash-chain consumers
  parent_gate_level        : GateLevel      // seed input for C-CP-12 §12.2 sub-agent gate-level
                                            //   max() composition; v1.6 MVP default GateLevel.AUTO
                                            //   per C-CP-12 §12.4 deferred-to-implementation-discretion
  parent_sandbox_tier      : SandboxTier    // seed input for C-AS-11 monotonic-ascension at sub-agent
                                            //   dispatch; v1.6 MVP default SandboxTier.TIER_1_PROCESS
  parent_actor             : Actor          // from ctx.ledger_writer.actor per
                                            //   LedgerWriter construction-time identity
  parent_entry_hash        : string         // hash of prior-step audit-ledger entry per C-CP-13 §13.5
                                            //   v1.6 MVP empty-string sentinel
  parent_idempotency_key   : string         // derived from existing _compute_step_idempotency_key
                                            //   (run_idempotency_key, step_index) per §25.3.3.7
  tenant_id                : Optional<string>  // None at v1.6 MVP — multi-tenancy not committed
                                               //   at v1.6 stack per Target_Stack_Commitment_v1.md
  step_index               : int            // per-iteration loop variable from §25.3.3 step
                                            //   enumeration
}
```

**Field semantics — `workflow_id` (v1.12 NEW).** The parent workflow's identifier. Sourced from `manifest_entry.workflow_id` (per C-CP-05 §5 `WorkflowManifestEntry.workflow_id`) at the driver §25.3.3.4 composition site. Required (NOT Optional) at composition. Composition rule: `workflow_id=manifest_entry.workflow_id` — the value is already in scope at the existing composition site (`workflow_driver.py:597-608`) where `parent_action_id` is composed via the same value via string interpolation.

**Composition discipline at the driver (v1.12 amendment).** The driver composes one `StepExecutionContext` per step at the §25.3.3.4 dispatch site, before invoking `step_dispatcher.dispatch(binding, step, step_context=step_context)`. Composition is from driver-tracked state (**5 fields** composed deterministically at v1.12 — was 4 at v1.6: `workflow_id`, `parent_action_id`, `parent_actor`, `parent_idempotency_key`, `step_index`) + 4 MVP-default-bounded fields (`parent_gate_level`, `parent_sandbox_tier`, `parent_entry_hash`, `tenant_id`) — preserved verbatim from v1.6 framing.

**Anti-extension invariant.** The 4 MVP-default-bounded fields remain documented as deferred-to-implementation-discretion at v1.12 per the C-CP-12 §12.4 pattern (preserved verbatim from v1.6). v1.7+ extension to surface them via operator-authored `WorkflowManifestEntry` extension fields remains a Workflow §4.1.2 Class-2 amendment to this contract, NOT a Phase-7 implementation-time amendment (per X-AL-3). The v1.12 `workflow_id` addition is NOT a deferred-field-surfacing — it surfaces an already-driver-tracked value that was already implicitly available via the `parent_action_id` substring; the v1.12 amendment makes the typed surface discrete without altering the underlying provenance.

**Step body opaque-to-driver invariant preserved.** `step_context` carries metadata about the step's execution environment (driver-composed); the existing C-CP-25 §25.3.3.4 invariant that "Step body is opaque to the driver" remains — `step_context` is NOT step body content, and the driver does not introspect `step.step_payload` to compose `step_context`. The new `workflow_id` field is composed from `manifest_entry.workflow_id` (driver-scope) at composition time, NOT from step body content.

### §25.3.3.4 step 4 driver composition prose (v1.12 cross-reference)

The v1.6 §25.3.3.4 step 4 prose ("v1.6 Path A amendment: the driver composes a `StepExecutionContext` per §25.2.1 from driver-tracked run-level state (`run_id`, `workflow_id`, `step_index`, `ctx.ledger_writer.actor`, run-scope idempotency key, plus the 4 MVP-default-bounded fields)") already enumerated `workflow_id` as a driver-tracked source value at composition time. The v1.12 amendment makes the `workflow_id` surface discrete at the `StepExecutionContext` record — the prose at §25.3.3.4 step 4 is preserved verbatim (the `workflow_id` enumeration was operatively-correct at v1.6 but the field was not pinned at §25.2.1 until v1.12).

---

## §2 — Preservation guarantees

| Element | Disposition |
|---|---|
| All v1.11 contracts (C-CP-01 through C-CP-27) | Preserved verbatim outside the §25.2.1 9th-field addition + §25.3.3.4 implicit-cross-reference resolution |
| v1.11 §26.2 `WorkflowPauseReason` rename | Preserved verbatim |
| v1.11 §26 §22 ↔ §26 coexistence NOTE | Preserved verbatim |
| v1.10 NEW §17.4 + §25 (C-CP-25 ValidatorFramework) + §27 (C-CP-27 PerServerTrustEvaluator + MCPClientNamespaceEmitter) | Preserved verbatim |
| v1.6 NEW §25.2.1 8 existing fields (`parent_action_id`, `parent_gate_level`, `parent_sandbox_tier`, `parent_actor`, `parent_entry_hash`, `parent_idempotency_key`, `tenant_id`, `step_index`) | Preserved verbatim — type / cardinality / semantics / MVP-default convention all unchanged |
| v1.6 §25.2 `StepDispatcher` Protocol signature | Preserved verbatim — Protocol consumers receive `step_context: StepExecutionContext` at v1.12 same as v1.6/v1.11 (the Pydantic BaseModel adds a field; Protocol conformance preserves) |
| v1.6 §25.3.3.4 step 4 driver composition prose | Preserved verbatim |
| All ADR commitments (F1–F5 + D1–D6) | Unchanged |

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_12.md` |
| Version | v1.12 |
| Filing event | Class 1 fork resolution Path A absorption — StepExecutionContext.workflow_id field addition per `.harness/class_1_fork_step_execution_context_workflow_id_field_absence.md` ratification 2026-05-24 |
| Predecessor | `Spec_Control_Plane_v1_11.md` (v1.11 substantive content preserved verbatim outside §25.2.1 9th-field addition) |
| Co-published artifacts | CP plan v2.18 (U-CP-NN revision-pass); harness-cp impl (StepExecutionContext field add + driver fill); harness-runtime impl (cost-attribution callsite migration); workspace `CLAUDE.md` row bumps; fork doc §8 ratification footer |
| Operator authority | `.harness/class_1_fork_step_execution_context_workflow_id_field_absence.md` Path A ratification (AskUserQuestion 2026-05-24) |
| Contract-count change | None (27 → 27) |
| Fail-class-count change | None |
| Skill discipline | `phase-7-back-flow-routing` Class 1 fork detection at cost-axis production migration arc opening; `spec-writer` Phase-7 spec-fix application of operator-ratified Path A; `[[advisor-before-substantive-work-for-cross-axis-blockers]]` advisor pre-implementation gate |
| Date | 2026-05-24 |
