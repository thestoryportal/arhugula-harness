# Implementation Plan — Harness Core v1.0

**Status:** Proposed

**Date:** 2026-05-15

**Revision:** v1.0 — genesis. Phase 7 sub-phase 7b in-CLI plan, created by revision pass **R1** of the materializability-conformance R-series (R1–R5). Introduces the shared-type carrier unit **U-CORE-01**.

**Authority chain:** `Project_Workflow_v1_8.md` §7.4 fidelity-grammar; `implementation-planner` SKILL.md §8 revision-pass sub-mode; `CLAUDE.md` §1.3 authority chain + §3.3 (`harness-core` hosts shared types).

**Entry authorization:** Operator ratification 2026-05-15 of `.harness/revision_R1_harness_core.md` — Q-R1-1 Option A (dedicated `harness-core` plan), Q-R1-2 (include `WorkflowEvent`), Q-R1-3 (`WorkloadClass` edge → `[U-CP-00]`), Q-R1-4 (single identity-alias module), Q-R1-5 (keep `UnitId`/`ReferenceToUnit` as plan-internal non-traced).

---

## §0 Change-note (genesis)

### §0.1 Trigger

The four materializability audits (Q1 AS / Q2 CP / Q3 OD / Q4 IS) and the T1 carrier triage found ~62 auxiliary types consumed at signature positions with no declaration site. The T1 carrier map assigned a cross-cutting subset to `harness-core`; the T2 X-AL-3 resolution confirmed all are spec-committed factor-outs (no design extension). This plan files **U-CORE-01**, the `harness-core` carrier unit for that subset. It is the prerequisite for the per-axis revision passes R2 (IS) / R3 (AS) / R4 (CP) / R5 (OD).

### §0.2 Relationship to `harness-core` and U-CP-00

`harness-core` already hosts one unit's product — `WorkloadClass`, declared by the landed **U-CP-00** (filed in the CP plan because C-CP-07 §7.3 is its single committing contract). U-CORE-01 declares types committed by contracts spread across AS/IS/CP specs — no single axis plan owns them — so they are filed here, in the shared-substrate plan. **U-CORE-01 does NOT redeclare `WorkloadClass`**; it sits beside it in the `harness-core` package.

### §0.3 Scope

One unit (U-CORE-01). No axis-plan edits — the downstream dependency edges (§3) are applied by R2–R5, each in its own axis plan.

---

## §1 Spec inventory

| Contract | Role at this plan |
|---|---|
| `Spec_Action_Surface_v1.md` C-AS-09 §9.1 | Commits the deployment-surface enumeration (12-cell matrix axis) → `DeploymentSurface` |
| `Spec_Action_Surface_v1.md` C-AS-09 §9.4 + `ADR-D5` v1.3 §1.5 | Commits the persona-tier ladder → `PersonaTier` |
| `Spec_Information_Substrate_v1.md` C-IS-05 §5 | Commits the F2 six-field entry-shape identifier fields → `ActionID`, `EntryID` |
| `Spec_Control_Plane` C-CP-05 §5.1, §5.2 | Commits the 8-class lifecycle event taxonomy + per-class attribute set → `WorkflowEvent`; identifier fields → `WorkflowID`, `StepID`, `ThreadID` |
| `Spec_Control_Plane` C-CP-13 §13.4 | Commits the handoff/stage identifier → `StageID` |
| `Spec_Action_Surface_v1.md` C-AS-03 §3 / `Spec_Control_Plane` C-CP-01 §1 | Commit tool/routing contract identifiers → `ContractID` |

---

## §2 U-CORE-01 — unit body

#### U-CORE-01 — Declare the cross-cutting `harness-core` shared-type set (cross-axis enums + identity-alias module + `WorkflowEvent`)

**Implements:** [C-AS-09 §9.1] (DeploymentSurface); [C-AS-09 §9.4] + [ADR-D5 v1.3 §1.5] (PersonaTier); [C-IS-05 §5] (EntryID, ActionID — the F2 six-field entry-shape identifier fields); [C-CP-05 §5.1, §5.2] (WorkflowID, StepID, ThreadID identifier fields + WorkflowEvent 8-class lifecycle taxonomy); [C-CP-13 §13.4] (StageID — handoff/stage identifier); [C-AS-03 §3] / [C-CP-01 §1] (ContractID — tool/routing contract identifier).

> **Spec-traceability note.** Each declared type is traced to a committing contract per the carrier map T1 disposition-1 rows + the T2 FACTOR-OUT verdicts. Every trace is to the **concept**; the alias/enum *shape* is a faithful operationalization of spec prose, not a spec extension.
>
> **`UnitId` / `ReferenceToUnit` — plan-internal (operator-ratified Q-R1-5).** These two aliases are NOT traced to a spec/ADR section. `UnitId` is the atomic-unit identifier domain (`"U-CP-22"` etc.) the plans use; `ReferenceToUnit` is consumed only at CP U-CP-41. They are carried in U-CORE-01 as **explicitly plan-internal** identifiers (carrier-convenience `str`-newtypes, no spec contract) — operator-ratified 2026-05-15.

**Depends on:** (none) — foundational; the topological root of the `harness-core` → IS → AS → CP → OD revision order. U-CORE-01 imports nothing; all four axes import it.

**Inputs:** None (foundational; substrate-supplying type unit).

**Files affected (logical):**
- `harness-core` deployment-surface enum (logical: `deployment-surface-enum`)
- `harness-core` persona-tier enum (logical: `persona-tier-enum`)
- `harness-core` identity-alias module (logical: `identity-aliases`)
- `harness-core` workflow-event type (logical: `workflow-event-type`)
- `harness-core` package export surface (logical: `harness-core-init-exports`)

`WorkloadClass` is **not** in this list — it is the landed U-CP-00 product, untouched by U-CORE-01.

**Residence rationale.** Every type in this unit is consumed by ≥2 axes (most by 3–4); per `CLAUDE.md` §3.3 (`harness-core` hosts shared types) and the carrier map disposition-1 criterion, they reside in `harness-core`. A single carrier prevents `pyright` treating N independent declarations as N distinct types.

**Signatures:**

```
# --- cross-cutting enums ---

enum DeploymentSurface {
  LOCAL_DEVELOPMENT,                                  // AS §9.1 matrix row "local-development"
  SELF_HOSTED_SERVER,                                 // AS §9.1 matrix row "self-hosted-server"
  MANAGED_CLOUD                                       // AS §9.1 matrix row "managed-cloud"
}
// Closed at cardinality 3 — the AS spec §9.1 C-AS-09 12-cell matrix's
// deployment-surface axis. String values are the §9.1 row labels verbatim
// (lowercase-hyphen).

enum PersonaTier {
  SOLO_DEVELOPER,                                     // AS §9.4 / §11 "solo-developer"
  TEAM_BINDING,                                       // AS §9.4 / §11 "team-binding"
  MULTI_TENANT_COMPLIANCE                             // AS §9.4 / §11 "multi-tenant-compliance"
}
// Closed at cardinality 3 — the F4 persona-tier ladder (AS §9.4 / §11;
// ADR-D5 v1.3 §1.5). String values verbatim.

# --- identity-alias module: thin str-newtypes, no shape ambiguity ---

newtype ActionID        = str   // C-IS-05 §5 F2 entry shape `action_id`
newtype EntryID         = str   // C-IS-05 §5 state-ledger entry identifier
newtype WorkflowID      = str   // C-CP-05 §5 `workflow.id` / `workflow_id`
newtype StepID          = str   // C-CP-05 §5 `step_id` / step-boundary identifier
newtype ThreadID        = str   // C-CP-05 §5 `thread_id` (idempotent-write keying tuple)
newtype StageID         = str   // C-CP-13 §13.4 handoff/stage identifier
newtype UnitId          = str   // atomic-unit identifier (plan-internal, non-traced)
newtype ReferenceToUnit = str   // reference to an atomic unit (plan-internal, non-traced; CP U-CP-41)
newtype ContractID      = str   // tool/routing contract identifier (C-AS-03 / C-CP-01)

# --- workflow-event lifecycle type (operator-ratified Q-R1-2: included) ---

enum WorkflowEventClass {
  WORKFLOW_START,                                     // C-CP-05 §5.1 `workflow-start`
  STEP_BOUNDARY,                                      // C-CP-05 §5.1 `step-boundary`
  FALLBACK_TRIGGER,                                   // C-CP-05 §5.1 `fallback-trigger`
  RETRY_ATTEMPT,                                      // C-CP-05 §5.1 `retry-attempt`
  BREAKER_TRIP,                                       // C-CP-05 §5.1 `breaker-trip`
  LEASE_ACQUIRED,                                     // C-CP-05 §5.1 `lease-acquired`
  LEASE_RELEASED,                                     // C-CP-05 §5.1 `lease-released`
  RESUMPTION                                          // C-CP-05 §5.1 `resumption`
}
model WorkflowEvent { event_class: WorkflowEventClass; ... per C-CP-05 §5.2 ... }
```

> **`WorkflowEvent` ↔ U-CP-10 reconciliation (hand-off to R4).** U-CP-10 already landed `LifecycleEventClass` for the same C-CP-05 §5.1 8-class taxonomy. U-CORE-01's `WorkflowEventClass` and U-CP-10's `LifecycleEventClass` are the same spec taxonomy declared twice — exactly the multi-declaration defect the carrier map targets. **R4 (CP revision) must reconcile:** either U-CP-10 is converted to consume `harness-core`'s `WorkflowEventClass`, or the operator rules on which name survives. Flagged here so R4 does not miss it.

**Acceptance criteria:**

1. `DeploymentSurface` declares exactly three values per AS spec §9.1 (C-AS-09) — SCREAMING_SNAKE_CASE rendering of the §9.1 deployment-surface axis rows `local-development | self-hosted-server | managed-cloud`. Closed at cardinality 3. Member string values byte-exact with the §9.1 row labels.
2. `PersonaTier` declares exactly three values — SCREAMING_SNAKE_CASE rendering of the F4 persona-tier ladder `solo-developer | team-binding | multi-tenant-compliance` (AS §9.4 / §11; ADR-D5 v1.3 §1.5). Closed at cardinality 3. String values verbatim.
3. The identity-alias module declares exactly nine `str`-newtype aliases — `ActionID`, `EntryID`, `WorkflowID`, `StepID`, `ThreadID`, `StageID`, `UnitId`, `ReferenceToUnit`, `ContractID` — each a distinct nominal type (a bare `str` is NOT assignable where an alias is required, and vice versa, under `pyright` strict). Seven are traced per the `Implements` line; `UnitId`/`ReferenceToUnit` are plan-internal, non-traced (Q-R1-5).
4. `WorkflowEvent` declares the C-CP-05 §5.1 8-class lifecycle event taxonomy (`WorkflowEventClass`, closed at cardinality 8, values verbatim) and a payload model carrying the §5.2 per-class minimum attribute set.
5. Every type resides in `harness-core` and is exposed at the `harness-core` package public API surface so all consuming axes import from one path. `WorkloadClass` (U-CP-00, landed) is unaffected and remains beside the U-CORE-01 set.
6. No spec extension: no field, value, or alias is introduced that is not committed by the cited contract (except the two ratified plan-internal aliases). Where a spec defers shape (e.g. C-IS-05 §5 identifier format), the alias is `str`-typed and the concrete format is not pinned.

**Tests:**
- `test_deployment_surface_cardinality_three`; `test_deployment_surface_values_match_as_spec_9_1_verbatim`; `test_deployment_surface_closed`
- `test_persona_tier_cardinality_three`; `test_persona_tier_values_match_as_spec_9_4_verbatim`; `test_persona_tier_closed`
- `test_identity_aliases_all_nine_declared`; `test_identity_alias_nominal_distinct_under_pyright`
- `test_workflow_event_class_cardinality_eight`; `test_workflow_event_class_values_match_cp_spec_5_1_verbatim`; `test_workflow_event_payload_matches_spec_5_2`
- `test_all_u_core_01_types_reside_in_harness_core`; `test_harness_core_init_reexports_u_core_01_set`
- `test_workload_class_unaffected_by_u_core_01`

**Rollback boundary:** Revert the U-CORE-01 type declarations (deployment-surface enum, persona-tier enum, identity-alias module, workflow-event type, `__init__` re-export additions). `WorkloadClass` / U-CP-00 is unaffected. Downstream: every IS/AS/CP/OD unit that took a `[U-CORE-01]` edge loses its carrier. A single coherent revert.

---

## §3 Dependency graph

- **U-CORE-01** — Level 0, `Depends on: (none)`. A pure source node, beside U-CP-00 (also Level 0). Acyclic — a source node with inbound-only edges cannot create a cycle.
- Downstream `[U-CORE-01]` edges (~17 units) + `[U-CP-00]` `WorkloadClass` edges (~15 units) are added by the per-axis revision passes R2–R5, not by this plan. Hand-off list at `.harness/revision_R1_harness_core.md` §3.

---

## §4 Coverage matrix

| Contract row | Covered by | Note |
|---|---|---|
| C-AS-09 §9.1 (deployment-surface enum axis) | U-CORE-01 | Multi-unit coverage — the 12-cell matrix proper is AS-plan-covered; U-CORE-01 covers the enum axis only |
| C-AS-09 §9.4 + ADR-D5 v1.3 §1.5 (persona-tier ladder) | U-CORE-01 | |
| C-IS-05 §5 (entry-shape identifier fields, as nominal types) | U-CORE-01 | Multi-unit — the entry shape proper is IS-plan-covered |
| C-CP-05 §5.1, §5.2 (lifecycle event taxonomy → `WorkflowEvent`) | U-CORE-01 | Multi-unit — R4 reconciles with U-CP-10 |
| C-CP-13 §13.4 (`StageID`) | U-CORE-01 | |

U-CORE-01 *adds* a coverage mark to multi-unit-covered contracts; R3/R4/R5 must not drop their existing C-AS-09 / C-CP-05 marks.

---

## §5 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Harness_Core_v1_0.md` |
| Authored at | Phase 7 sub-phase 7b, 2026-05-15 — revision pass R1 |
| Authoring authority | Operator ratification of `.harness/revision_R1_harness_core.md` (2026-05-15) |
| Predecessor | Genesis (no predecessor); `.harness/revision_R1_harness_core.md` is the revision proposal |
| Successor consumption | R2–R5 per-axis revision passes consume the U-CORE-01 carrier + the §3 hand-off edges |
| Revision policy | Canonical for the `harness-core` shared-substrate plan; revisions in-CLI per workspace discipline |

*End of Implementation Plan — Harness Core v1.0. One unit (U-CORE-01). The R2–R5 per-axis passes wire the downstream dependency edges.*
