# Implementation Plan — Harness Core v1.1

**Status:** Proposed

**Date:** 2026-05-15

**Revision:** v1.1 — Phase 7 sub-phase 7b in-CLI revision. Resolves a **Class 1 fork** surfaced at U-CORE-01 execution-time: the `WorkflowEvent` payload model was specified at the v1.0 unit body as an unmaterialized placeholder (`model WorkflowEvent { ...; ... per §5.2 ... }`). Operator ruling 2026-05-15 (carrier-thin) — strike the `WorkflowEvent` payload model from U-CORE-01; `WorkflowEventClass` (the cross-cutting enum) is retained. See §0.4. Predecessor: v1.0 (R1 genesis).

**Authority chain:** `Project_Workflow_v1_8.md` §7.4 fidelity-grammar; `CLAUDE.md` §4.3 back-flow routing (Class 1 fork resolution); `implementation-planner` SKILL.md §8 revision-pass sub-mode; `CLAUDE.md` §1.3 authority chain + §3.3 (`harness-core` hosts shared types).

**Entry authorization:** Operator ratification 2026-05-15 of the carrier-thin reading of the U-CORE-01 `WorkflowEvent`-payload Class 1 fork (`.harness/class_1_tension_u_core_01_workflow_event.md`).

---

## §0 Change-note

### §0.1 Trigger (v1.0 genesis)

The four materializability audits (Q1 AS / Q2 CP / Q3 OD / Q4 IS) and the T1 carrier triage found ~62 auxiliary types consumed at signature positions with no declaration site. The T1 carrier map assigned a cross-cutting subset to `harness-core`; the T2 X-AL-3 resolution confirmed all are spec-committed factor-outs (no design extension). This plan files **U-CORE-01**, the `harness-core` carrier unit for that subset. It is the prerequisite for the per-axis revision passes R2 (IS) / R3 (AS) / R4 (CP) / R5 (OD).

### §0.2 Relationship to `harness-core` and U-CP-00

`harness-core` already hosts one unit's product — `WorkloadClass`, declared by the landed **U-CP-00** (filed in the CP plan because C-CP-07 §7.3 is its single committing contract). U-CORE-01 declares types committed by contracts spread across AS/IS/CP specs — no single axis plan owns them — so they are filed here, in the shared-substrate plan. **U-CORE-01 does NOT redeclare `WorkloadClass`**; it sits beside it in the `harness-core` package.

### §0.3 Scope

One unit (U-CORE-01). No axis-plan edits — the downstream dependency edges (§3) are applied by R2–R5, each in its own axis plan.

### §0.4 v1.1 revision — Class 1 fork resolution (`WorkflowEvent` payload model struck)

**Trigger.** At U-CORE-01 execution-time (Phase 7 7b), the v1.0 unit body's `WorkflowEvent` signature was found unmaterializable as written. The v1.0 signature was a placeholder — `model WorkflowEvent { event_class: WorkflowEventClass; ... per C-CP-05 §5.2 ... }`. Faithful materialization of "a payload model carrying the §5.2 per-class minimum attribute set" (v1.0 acc #4) transitively requires four CP-axis types U-CORE-01 does not own and the carrier map did not assign to it — `engine.class` (C-CP-09), `step.kind`, `resumption.kind` (C-CP-08), and the `lease.*` namespace (C-CP-05 §5.3) — and C-CP-05 §5.2 declares per-class attribute rows for only 5 of the 8 event classes. Materializing the payload in `harness-core` would also collapse the v1.0 §2 R4-reconciliation hand-off (U-CP-10, the CP-axis lifecycle-event unit, would have nothing left to own).

**Class.** Class 1 (architectural defect; plan signature cannot be materialized at target stack) per `CLAUDE.md` §4.3 + `phase-7-implementation` SKILL.md §6. Halted at U-CORE-01; surfaced to operator.

**Operator ruling 2026-05-15 — carrier-thin.** U-CORE-01 declares `WorkflowEventClass` (the 8-class enum — a genuine cross-cutting shared type, consumed by CP U-CP-10 and IS U-IS-14) and **does not declare a `WorkflowEvent` payload model**. The C-CP-05 §5.2 per-class minimum attribute set is a span-emission-site contract owned by the CP axis (lifecycle-event-emission units), not a `harness-core` carrier type.

**Changes at v1.1.**

| Site | v1.0 | v1.1 |
|---|---|---|
| §1 spec inventory — C-CP-05 row | `§5.1, §5.2 → WorkflowEvent; identifier fields` | `§5.1 → WorkflowEventClass; §5.2 identifier fields → WorkflowID, StepID, ThreadID`. §5.2 per-class attribute *schema* no longer claimed by U-CORE-01. |
| §2 `Implements` line | `[C-CP-05 §5.1, §5.2] (... + WorkflowEvent 8-class lifecycle taxonomy)` | `[C-CP-05 §5.1] (WorkflowEventClass 8-class lifecycle taxonomy); [C-CP-05 §5.2] (WorkflowID, StepID, ThreadID identifier fields)` |
| §2 signature block | `model WorkflowEvent { ...; ... per §5.2 ... }` declared | struck — `WorkflowEventClass` enum retained, no payload model |
| §2 Files affected | `workflow-event-type` | `workflow-event-class-enum` |
| §2 acc #4 | enum + "a payload model carrying the §5.2 per-class minimum attribute set" | enum only; payload-model clause struck |
| §2 Tests | `test_workflow_event_payload_matches_spec_5_2` listed | struck |
| §4 coverage matrix — C-CP-05 row | `§5.1, §5.2 (... → WorkflowEvent)` | `§5.1 (taxonomy → WorkflowEventClass enum); §5.2 (identifier fields only)`; per-class payload schema is CP-plan-covered |

No other v1.0 content modified. The 9 identity aliases, `DeploymentSurface`, `PersonaTier`, and `WorkflowEventClass` are unchanged from v1.0.

**Flagged follow-ups (recorded at `.harness/class_1_tension_u_core_01_workflow_event.md`).**

- **F-1.** C-CP-05 §5.2 per-class minimum attribute set — coverage reverts entirely to the CP plan. The §5.2 contract is satisfied at CP lifecycle-event span-emission sites; verify §5.2 coverage holds in CP plan v2.6 (or successor) when CP emission units land. Not owed by `harness-core`.
- **F-2.** CP plan v2.6 §0 spec-inventory line ("declares **U-CORE-01** in the `harness-core` plan: ... and `WorkflowEventClass`/`WorkflowEvent`") carries a now-stale `WorkflowEvent` reference. Mechanical back-reference fix owed at the next CP plan touch.

---

## §1 Spec inventory

| Contract | Role at this plan |
|---|---|
| `Spec_Action_Surface_v1.md` C-AS-09 §9.1 | Commits the deployment-surface enumeration (12-cell matrix axis) → `DeploymentSurface` |
| `Spec_Action_Surface_v1.md` C-AS-09 §9.4 + `ADR-D5` v1.3 §1.5 | Commits the persona-tier ladder → `PersonaTier` |
| `Spec_Information_Substrate_v1.md` C-IS-05 §5 | Commits the F2 six-field entry-shape identifier fields → `ActionID`, `EntryID` |
| `Spec_Control_Plane` C-CP-05 §5.1 | Commits the 8-class lifecycle event taxonomy → `WorkflowEventClass` |
| `Spec_Control_Plane` C-CP-05 §5.2 | Commits the per-class minimum attribute set; U-CORE-01 carries only the identifier fields → `WorkflowID`, `StepID`, `ThreadID` (the per-class attribute *schema* is CP-plan-covered — see §0.4 F-1) |
| `Spec_Control_Plane` C-CP-13 §13.4 | Commits the handoff/stage identifier → `StageID` |
| `Spec_Action_Surface_v1.md` C-AS-03 §3 / `Spec_Control_Plane` C-CP-01 §1 | Commit tool/routing contract identifiers → `ContractID` |

---

## §2 U-CORE-01 — unit body

#### U-CORE-01 — Declare the cross-cutting `harness-core` shared-type set (cross-axis enums + identity-alias module + `WorkflowEventClass`)

**Implements:** [C-AS-09 §9.1] (DeploymentSurface); [C-AS-09 §9.4] + [ADR-D5 v1.3 §1.5] (PersonaTier); [C-IS-05 §5] (EntryID, ActionID — the F2 six-field entry-shape identifier fields); [C-CP-05 §5.1] (WorkflowEventClass — the 8-class lifecycle event taxonomy); [C-CP-05 §5.2] (WorkflowID, StepID, ThreadID — the per-class-attribute identifier fields); [C-CP-13 §13.4] (StageID — handoff/stage identifier); [C-AS-03 §3] / [C-CP-01 §1] (ContractID — tool/routing contract identifier).

> **Spec-traceability note.** Each declared type is traced to a committing contract per the carrier map T1 disposition-1 rows + the T2 FACTOR-OUT verdicts. Every trace is to the **concept**; the alias/enum *shape* is a faithful operationalization of spec prose, not a spec extension.
>
> **`WorkflowEvent` payload model — struck at v1.1 (operator ruling, carrier-thin).** v1.0 declared a `WorkflowEvent` payload model carrying the C-CP-05 §5.2 per-class minimum attribute set. That model is **not** declared at U-CORE-01 — it was unmaterializable as a `harness-core` carrier type (it transitively requires four CP-axis types U-CORE-01 does not own) and the §5.2 per-class attribute set is a CP-axis span-emission contract. U-CORE-01 retains only `WorkflowEventClass`, the cross-cutting enum. See §0.4.
>
> **`UnitId` / `ReferenceToUnit` — plan-internal (operator-ratified Q-R1-5).** These two aliases are NOT traced to a spec/ADR section. `UnitId` is the atomic-unit identifier domain (`"U-CP-22"` etc.) the plans use; `ReferenceToUnit` is consumed only at CP U-CP-41. They are carried in U-CORE-01 as **explicitly plan-internal** identifiers (carrier-convenience `str`-newtypes, no spec contract) — operator-ratified 2026-05-15.

**Depends on:** (none) — foundational; the topological root of the `harness-core` → IS → AS → CP → OD revision order. U-CORE-01 imports nothing; all four axes import it.

**Inputs:** None (foundational; substrate-supplying type unit).

**Files affected (logical):**
- `harness-core` deployment-surface enum (logical: `deployment-surface-enum`)
- `harness-core` persona-tier enum (logical: `persona-tier-enum`)
- `harness-core` identity-alias module (logical: `identity-aliases`)
- `harness-core` workflow-event-class enum (logical: `workflow-event-class-enum`)
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

# --- workflow-event-class lifecycle taxonomy (operator-ratified Q-R1-2: included) ---

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
// Closed at cardinality 8 — the C-CP-05 §5.1 lifecycle event class table's
// `Event class` column. String values verbatim (lowercase-hyphen).
// No `WorkflowEvent` payload model is declared (v1.1 — see §0.4).
```

> **`WorkflowEventClass` ↔ U-CP-10 reconciliation (R4, applied at CP plan v2.6).** U-CP-10 originally landed a local `LifecycleEventClass` for the same C-CP-05 §5.1 8-class taxonomy. CP plan v2.6 (R4, operator decision D9 / Q-R4-7) ruled `WorkflowEventClass` — the U-CORE-01 name — survives; `LifecycleEventClass` is retired and U-CP-10 converts to a consuming site. The landed U-CP-10 source re-point is the CP plan v2.6 §0.13 D-2 deferred action item.

**Acceptance criteria:**

1. `DeploymentSurface` declares exactly three values per AS spec §9.1 (C-AS-09) — SCREAMING_SNAKE_CASE rendering of the §9.1 deployment-surface axis rows `local-development | self-hosted-server | managed-cloud`. Closed at cardinality 3. Member string values byte-exact with the §9.1 row labels.
2. `PersonaTier` declares exactly three values — SCREAMING_SNAKE_CASE rendering of the F4 persona-tier ladder `solo-developer | team-binding | multi-tenant-compliance` (AS §9.4 / §11; ADR-D5 v1.3 §1.5). Closed at cardinality 3. String values verbatim.
3. The identity-alias module declares exactly nine `str`-newtype aliases — `ActionID`, `EntryID`, `WorkflowID`, `StepID`, `ThreadID`, `StageID`, `UnitId`, `ReferenceToUnit`, `ContractID` — each a distinct nominal type (a bare `str` is NOT assignable where an alias is required, and vice versa, under `pyright` strict). Seven are traced per the `Implements` line; `UnitId`/`ReferenceToUnit` are plan-internal, non-traced (Q-R1-5).
4. `WorkflowEventClass` declares the C-CP-05 §5.1 8-class lifecycle event taxonomy — closed at cardinality 8, member string values byte-exact with the §5.1 `Event class` column (`workflow-start | step-boundary | fallback-trigger | retry-attempt | breaker-trip | lease-acquired | lease-released | resumption`). **(v1.1 — the v1.0 payload-model clause is struck; no `WorkflowEvent` payload model is declared at U-CORE-01. See §0.4.)**
5. Every type resides in `harness-core` and is exposed at the `harness-core` package public API surface so all consuming axes import from one path. `WorkloadClass` (U-CP-00, landed) is unaffected and remains beside the U-CORE-01 set.
6. No spec extension: no field, value, or alias is introduced that is not committed by the cited contract (except the two ratified plan-internal aliases). Where a spec defers shape (e.g. C-IS-05 §5 identifier format), the alias is `str`-typed and the concrete format is not pinned.

**Tests:**
- `test_deployment_surface_cardinality_three`; `test_deployment_surface_values_match_as_spec_9_1_verbatim`; `test_deployment_surface_closed`
- `test_persona_tier_cardinality_three`; `test_persona_tier_values_match_as_spec_9_4_verbatim`; `test_persona_tier_closed`
- `test_identity_aliases_all_nine_declared`; `test_identity_alias_nominal_distinct_under_pyright`
- `test_workflow_event_class_cardinality_eight`; `test_workflow_event_class_values_match_cp_spec_5_1_verbatim`; `test_workflow_event_class_closed`
- `test_all_u_core_01_types_reside_in_harness_core`; `test_harness_core_init_reexports_u_core_01_set`
- `test_workload_class_unaffected_by_u_core_01`

**Rollback boundary:** Revert the U-CORE-01 type declarations (deployment-surface enum, persona-tier enum, identity-alias module, workflow-event-class enum, `__init__` re-export additions). `WorkloadClass` / U-CP-00 is unaffected. Downstream: every IS/AS/CP/OD unit that took a `[U-CORE-01]` edge loses its carrier. A single coherent revert.

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
| C-CP-05 §5.1 (lifecycle event taxonomy → `WorkflowEventClass` enum) | U-CORE-01 | Multi-unit — CP plan v2.6 U-CP-10 covers the span-name-metadata map |
| C-CP-05 §5.2 (per-class identifier fields, as nominal types) | U-CORE-01 | Identifier-field aliases only; the per-class minimum *attribute schema* is CP-plan-covered at lifecycle-event emission sites (v1.1 — see §0.4 F-1) |
| C-CP-13 §13.4 (`StageID`) | U-CORE-01 | |

U-CORE-01 *adds* a coverage mark to multi-unit-covered contracts; R3/R4/R5 must not drop their existing C-AS-09 / C-CP-05 marks.

---

## §5 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Harness_Core_v1_1.md` |
| Authored at | Phase 7 sub-phase 7b, 2026-05-15 — v1.1 Class 1 fork resolution |
| Authoring authority | Operator ratification of the carrier-thin reading (`.harness/class_1_tension_u_core_01_workflow_event.md`, 2026-05-15) |
| Predecessor | `Implementation_Plan_Harness_Core_v1_0.md` (R1 genesis) |
| Successor consumption | R2–R5 per-axis revision passes consume the U-CORE-01 carrier + the §3 hand-off edges |
| Revision policy | Canonical for the `harness-core` shared-substrate plan; revisions in-CLI per workspace discipline |

*End of Implementation Plan — Harness Core v1.1. One unit (U-CORE-01). The R2–R5 per-axis passes wire the downstream dependency edges.*
