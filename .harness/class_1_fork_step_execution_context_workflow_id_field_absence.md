# Class 1 Fork — StepExecutionContext.workflow_id field absence vs OD spec v1.10 §C-OD-26.6.1 step 2 cite

**Filed:** 2026-05-24 at cost-axis production callsite migration arc opening (post-Sub-arc B + bucket-count refresh landing; HEAD `c413d40`).

**Status:** OPEN — operator ratification pending; resolution arc not opened at filing.

**Trigger.** Operator opened the cost-axis production callsite migration arc at session resume per checkpoint Remaining Work item #1. Sub-arc B landed the typed `CostRecordAuditPayload` path (carrier + helper + converter branch) at `0919a9b` 2026-05-24; migration of production code from CPAuditLedgerEntry path → typed CostRecordAuditPayload path was DEFERRED at Sub-arc B per FM-2 + `[[halt-route-split-AC-pattern]]` (U-OD-41 plan v2.17 AC #8). The migration unblock arc surfaced an OD-spec-side silent absorption of a CP-spec extension: the canonical action_id pattern composition cites a `StepExecutionContext` field that does not exist at the CP-spec contract.

## §1 Empirical evidence

### §1.1 OD spec v1.10 §C-OD-26.6.1 step 2 cite

OD spec v1.10 §C-OD-26.6.1 step 2 (line 146, byte-exact):

> **`audit_cp_action_id` pattern.** `cost:<workflow_id>:<step_action_id>` per CXA v2.9 §0.3 row 8 discriminator-table extension. **The `<workflow_id>` is the parent workflow's identifier from `step_context.workflow_id`**; the `<step_action_id>` is the billable span's parent step action_id (the LLM dispatch / tool dispatch / etc. that caused the cost attribution).

The cite `step_context.workflow_id` references a field on the `StepExecutionContext` Pydantic v2 BaseModel.

### §1.2 StepExecutionContext field empirical inventory at HEAD `c413d40`

CP spec v1.11 §25 `StepExecutionContext` field-set per `harness-cp/src/harness_cp/workflow_driver_types.py:119-183`:

| Field | Type | Notes |
|---|---|---|
| `parent_action_id` | str | Composed as `f"workflow:{workflow_id}:step:{step_index}"` per driver `workflow_driver.py:598-600` |
| `parent_gate_level` | GateLevel | MVP default AUTO per C-CP-12 §12.4 |
| `parent_sandbox_tier` | SandboxTier | MVP default TIER_1_PROCESS per C-AS-11 |
| `parent_actor` | Actor | From `ctx.ledger_writer.actor` |
| `parent_entry_hash` | str | MVP `""` per C-RT-17 §14.7.4 |
| `parent_idempotency_key` | str | From `_compute_step_idempotency_key` |
| `tenant_id` | str \| None | MVP None per stack v1.6 |
| `step_index` | int | Per-iteration loop variable |

**`workflow_id` field is ABSENT.** The workflow identifier exists at the driver scope (`manifest_entry.workflow_id` per `workflow_driver.py:397/441/444/.../781`) and is embedded as a substring of `parent_action_id` (composed at `workflow_driver.py:598-600`), but is NOT surfaced as a discrete `StepExecutionContext` field consumable by step dispatchers.

### §1.3 Path B (substring parse) structural-safety analysis

The naive alternative — parsing `workflow_id` out of `parent_action_id` via the `workflow:{workflow_id}:step:{step_index}` pattern — is structurally unsafe:

- `workflow_id` is typed as `Identifier(workflow_id)` upstream (per `workflow_driver.py:866 thread_id=Identifier(workflow_id)`).
- The `Identifier` type at `harness-core/src/harness_core/identity.py` does NOT document a colon-exclusion constraint.
- A `workflow_id` containing the substring `:step:` would silently mis-split (the parse would extract a truncated workflow_id).
- This encodes a structural assumption at a non-creation site (the cost-attribution helper), which violates the workspace pattern `[[advisor-before-substantive-work-for-cross-axis-blockers]]` and the general design-discipline preference for typed surfaces over string-parsing at consumer sites.

## §2 Decision class

**Class 1 — silent absorption of CP-spec extension at OD spec authoring.** Per workspace memory `[[advisor-before-substantive-work-for-cross-axis-blockers]]` + `Phase_7_Meta_Architecture_v1.md` §7.7 X-AL-3: no silent H_T design extension at Phase 7 execution. The OD spec v1.10 §C-OD-26.6.1 step 2 cite `step_context.workflow_id` constitutes a silent CP-spec extension absorption at OD-spec-authoring time (Sub-arc B publication arc 2026-05-24, commit `0919a9b`). The OD-spec absorption arc did not surface the cross-axis cite as a CP-spec gap requiring CP-side coordination; the cite was authored as if `workflow_id` were already a `StepExecutionContext` field, but no such field exists at C-CP-25 contract or `workflow_driver_types.py` implementation.

**Bounded scope.** OD spec v1.10 §C-OD-26.6.5 explicitly classifies the production callsite migration as "OPERATIONAL refinement (not spec-correctness gate) deferred per FM-2 to a follow-on arc per `[[halt-route-split-AC-pattern]]`." Both paths (legacy CPAuditLedgerEntry path with `cost:{span_id}` + typed CostRecordAuditPayload path with `cost:{workflow_id}:{step_action_id}`) are explicitly declared spec-supported at v1.10. The fork is therefore Class 1-bounded: it does NOT halt the production-supported audit path; it gates the proposed migration arc.

## §3 Resolution paths

### §3.A — CP-spec amendment (clean, additive)

**Scope.** Add `workflow_id: str` field to `StepExecutionContext` at CP spec v1.11 §25 (or v1.11 → v1.12 if §25 is not directly amendable). Driver fills the field at composition site `workflow_driver.py:597-608` from `manifest_entry.workflow_id` (already in scope at the composition site). OD-side helper consumer at `cost_attribution_llm_dispatch.py:198-202` migrates to typed CostRecordAuditPayload path using both `step_context.workflow_id` + `step_context.parent_action_id` directly.

**Authority chain.**
- CP spec v1.11 → v1.12 (additive field at C-CP-25 `StepExecutionContext` Pydantic BaseModel).
- CP plan v2.17 → v2.18 (revision-pass at U-CP-NN — the cluster anchor for C-CP-25 surface — absorbing the new field at AC + signature line + Files line).
- Driver impl: 1-line field-fill at `workflow_driver.py:597-608` StepExecutionContext composition; field already in scope (`manifest_entry.workflow_id`).
- OD-side helper consumer migration (the original AC #8 deferred scope): widen `attribute_llm_dispatch_cost` signature to accept `workflow_id` + `parent_action_id`; caller at `llm_dispatch.py:701` passes `step_context.workflow_id` + `step_context.parent_action_id`; replace `_project_and_convert_audit_entry()` helper at `cost_attribution_llm_dispatch.py:209-244` with import of canonical `_project_cost_record_to_audit_payload()` at `harness-od/src/harness_od/cost_record_audit_writer.py`.

**Estimated arc:** ~6-8 commits across 1 session.
1. Fork doc filing (this artifact) + operator ratification AskUserQuestion
2. CP spec v1.11 → v1.12 (spec-writer skill scope)
3. CP plan v2.17 → v2.18 (implementation-planner skill scope)
4. Driver field-fill + StepExecutionContext field-add impl (`harness-cp`)
5. OD-side helper consumer migration + production callsite widening impl (`harness-runtime`)
6. Tests (driver-side field-population + production-callsite typed-path emission)
7. Workspace CLAUDE.md §2.3 CP spec row + §2.4 CP plan row version bumps
8. Memory advance: `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` → cost-axis production-wiring close noted

**ZERO cross-axis cascade beyond CP-spec/plan + harness-cp + harness-runtime.** OD spec v1.10 §C-OD-26.6.1 step 2 cite already references `step_context.workflow_id` — the CP-spec amendment RESOLVES the cite (was implicitly pending; becomes byte-exact). No CXA amendment owed (CXA v2.9 row 8 is already canonical). OD spec preserved verbatim at v1.10.

### §3.B — Parse workflow_id from parent_action_id (structurally brittle; advisor-flagged)

Split `parent_action_id` on `:step:` substring to extract `workflow_id`. NO CP-spec amendment.

**Defect.** Per §1.3 above, `Identifier(workflow_id)` upstream does not document a colon-exclusion constraint. Path B silently mis-splits if `workflow_id` contains `:step:`. Encodes structural assumption at non-creation site.

**Estimated arc:** ~2 commits (helper + test). NO spec amendment.

**NOT RECOMMENDED.** Listed for catalogue.

### §3.C — Close carry-forward as spec-blessed-deferred indefinitely

OD spec v1.10 §C-OD-26.6.5 explicitly says both paths produce valid audit entries. Document at U-OD-41 plan body + memory: production stays at CPAuditLedgerEntry path with `cost:{span_id}` action_id pattern (operational since U-OD-38 landing); typed CostRecordAuditPayload path remains canonical for future surfaces (sub-agent dispatch / tool dispatch / etc. — separate billable-span contexts where the new typed path applies cleanly without a CP-spec gap).

**Estimated arc:** ~1 commit (memory advance + change-note at U-OD-41 plan body documenting permanent-deferral).

**Permits:** §3.A at a future arc when CP-spec amendment is independently motivated (e.g., another consumer that needs `step_context.workflow_id` discretely).

### §3.D — File this fork only; defer resolution arc

Land this fork doc filing; operator routes resolution decision at a future arc. Mirrors `[[fork-u-rt-68-retry-wrap-and-bootstrap-wiring-gap]]` filing-first pattern.

## §4 Adjacent findings

(i) **OD spec v1.10 §C-OD-26.6.5 deferred-item enumeration is internally consistent.** §C-OD-26.6.5 line 177 enumerates the deferral as "Migration of production code to the v1.10 typed CostRecordAuditPayload path + NEW `cost:{workflow_id}:{step_action_id}` pattern requires widening `attribute_llm_dispatch_cost` signature to accept `workflow_id` + `parent_action_id` kwargs". The widening scope is correctly enumerated; the missing piece is the upstream `step_context.workflow_id` source — which §C-OD-26.6.1 step 2 cites as the source but which does not exist at CP-spec contract. The OD-spec sub-arc B authoring absorbed the cite without flagging the CP-side gap.

(ii) **OD plan v2.17 U-OD-41 plan-body deferred-item documentation already enumerates the CP-spec-gap shape implicitly.** OD plan v2.17 §0 line 33 (i)(vi) Sub-arc B sequel adjacent-finding documents: "Migration of the production callsite from CPAuditLedgerEntry path → typed CostRecordAuditPayload path requires widening `attribute_llm_dispatch_cost` signature to accept `workflow_id` + `parent_action_id` from runtime context". The phrasing "from runtime context" is the implicit acknowledgement that the source surface is unclear; the present filing surfaces "runtime context" = `StepExecutionContext` (the canonical step-level runtime context per C-CP-25) AND that the cited field does not exist on that surface.

(iii) **§26.3 prose vs §C-OD-26.6.1 step 2 pattern divergence already self-disclosed at OD spec v1.10.** OD spec v1.10 line 238: "§26.3 prose says `audit.cp.action_id = f\"cost:{span_id}\"` — at v1.10 implementation, the §C-OD-26.6 `audit_cp_action_id` field uses the more-specific pattern `cost:<workflow_id>:<step_action_id>` per CXA v2.9 §0.3 row 8 discriminator-table (workflow-scoped + step-anchored). The `span_id` in the §26.3 prose maps to `<step_action_id>` at impl... The §26.3 prose is preserved verbatim per FM-2; the more-specific pattern is operationalized at §C-OD-26.6 + helper construction. Adjacent finding: §26.3 prose may be tightened at a future v1.x revision to align byte-exact with the CXA v2.9 §0.3 pattern; surfaced at this v1.10 change-note (i) for future routing."

This indicates the OD-spec authors were aware of the pattern-shape change but did NOT independently verify the upstream surface (`step_context.workflow_id`) existence at HEAD.

(iv) **Path A blast-radius bounding.** Per §3.A scope, adding `workflow_id: str` field to `StepExecutionContext` is purely ADDITIVE (no existing field removed; no behavior change for existing consumers). All current consumers of `StepExecutionContext` (per grep `step_context` across `harness-runtime` + `harness-cp` + `harness-od`): `StepDispatcher.dispatch` Protocol consumers + `cost_attribution_llm_dispatch._attribute_cost_best_effort` + `sub_agent_dispatch` chain — all are field-additive-compatible (Pydantic v2 `extra="forbid"` is preserved; only the construction site at `workflow_driver.py:597-608` needs the new arg). ZERO breaking change.

## §5 Cross-axis impact

**ZERO new cross-axis EDGES introduced by §3.A resolution.** The amendment is intra-CP-spec (StepExecutionContext is CP-axis contract surface). The OD-side helper consumer migration already had its cross-axis edge (CP→OD audit-write) at CXA v2.9 §2.3.7 row 8; the CP-spec field-add does not modify the edge.

**CP-spec / CP-plan / harness-cp / harness-runtime cascade only.** Per §3.A authority chain.

## §6 Recommended resolution path

**§3.A (CP-spec amendment) recommended.**

Rationale:
- The OD-spec absorption arc had implicit-cite to `step_context.workflow_id` (§1.1); the silent absorption is the design-fidelity defect, not the missing field.
- Path B (substring parse) has the documented brittleness at §1.3.
- Path C (indefinite deferral) is spec-permitted per §C-OD-26.6.5 but leaves the silent-absorption defect un-flagged at upstream OD-spec — future readers / consumers will hit the same surface gap.
- Path D (file-only) is the operator-bounded variant of §3.A — appropriate if operator prefers multi-arc decomposition over single-session full resolution.

## §7 Filing footer

| Field | Value |
|---|---|
| Filed | 2026-05-24 |
| Filing arc | Cost-axis production callsite migration arc opening (post Sub-arc B + bucket-count refresh landing) |
| Filing skill | `phase-7-back-flow-routing` (Class 1 fork detection at migration-arc opening) |
| HEAD at filing | `c413d40` |
| Resolution arc(s) (if §3.A ratified) | (a) CP spec v1.11 → v1.12 amendment; (b) CP plan v2.17 → v2.18 revision; (c) driver impl + StepExecutionContext field add; (d) OD-side helper consumer migration + production callsite widening |
| Status | OPEN at filing → RATIFIED at AskUserQuestion → APPLIED at multi-commit arc |
| Related memory | `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` (cost-axis production-wiring close gated on this fork resolution); `[[advisor-before-substantive-work-for-cross-axis-blockers]]` (advisor call confirmed pre-implementation gate); `[[halt-route-split-AC-pattern]]` (Sub-arc B AC #8 deferral pattern); `[[fork-u-rt-68-retry-wrap-and-bootstrap-wiring-gap]]` (filing-first multi-arc precedent if §3.D selected) |
