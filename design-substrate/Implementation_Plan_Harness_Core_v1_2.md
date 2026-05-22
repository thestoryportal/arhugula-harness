# Implementation Plan — Harness Core v1.2

**Status:** Proposed

**Date:** 2026-05-22 (v1.2 revision; v1.1 + v1.0 history preserved at §0)

**Revision:** v1.2 — Phase 7 sub-phase 7b in-CLI revision. Absorbs the `SandboxDecisionPolicy` Class 1 fork resolution per `.harness/class_1_fork_sandbox_decision_policy_phantom_cite.md` (operator-ratified Q1=C-i 2026-05-22) — adds NEW unit **U-CORE-02** for the `SandboxDecisionPolicy` empty-marker carrier at `harness-core` package, consumed by `Implementation_Plan_Harness_Runtime_v2_13.md` U-RT-71 (co-published this arc). v1.1 + v1.0 content preserved verbatim per §0.5 below. Predecessor: v1.1 (Class 1 fork resolution — `WorkflowEvent` payload model struck).

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

### §0.5 v1.2 revision — `SandboxDecisionPolicy` carrier addition (Class 1 fork absorption)

**Trigger.** During `phase-7-implementation` skill §3.4 dependency-verification step for L9-septies cluster opening (runtime plan v2.12 U-RT-71 consumption attempt 2026-05-22), an empirical phantom-cite was surfaced: runtime spec v1.15 §3 C-RT-02 `sandbox_decision_policy` field-table row cited `SandboxDecisionPolicy` as imported from "AS spec v1.3 §15 carrier", but ZERO hits across `harness-{as,cp,runtime,core}` source trees + ZERO declarations at AS spec v1.3 / §C-AS-15 (which is `secret.fetch` span schema, not a sandbox policy class). Class 1 fork filed at `.harness/class_1_fork_sandbox_decision_policy_phantom_cite.md` (commit `1060a15`).

**Class.** Class 1 (architectural defect; cited spec contract section unreachable) per `CLAUDE.md` §4.3 + `phase-7-implementation` SKILL.md §6. Halted L9-septies cluster opening; surfaced to operator.

**Operator ruling 2026-05-22 — Q1=C-i.** Re-home `SandboxDecisionPolicy` to `harness-core` package (smallest spec edit; preserves the field; no AS-axis-spec reopen; no semantic commitment to AS-internal sandbox policy at the runtime layer). Q2=Open-now: resolution arc opens this session — spec-writer v1.15 → v1.16 + implementation-planner v2.12 → v2.13 + harness-core plan v1.1 → v1.2 (this revision) all co-published 2026-05-22.

**Authoring-locus decision — option (α) ratified by implementation-planner per `implementation-planner` SKILL.md §3.1 single-coherent-change criterion.** Bundling the new class authoring at `harness-core` package WITH the `RuntimeConfig` schema-field extension at `harness-runtime` package within U-RT-71 (option β) would constitute two coherent changes across two packages, NOT a single coherent change. Option (α) — a NEW atomic unit **U-CORE-02** at this plan — preserves atomic-decomposition discipline; U-RT-71 gains a within-axis-cross-package dependency edge to U-CORE-02 (analogous to existing U-CORE-01 consumers across all axes).

**Carrier-shape decision — empty-marker.** Per `implementation-planner` SKILL.md §4 sub-discipline 4.4 (no spec extension) + X-AL-3 (no silent H_T design extension at Phase 7): runtime spec v1.16 commits `SandboxDecisionPolicy | None` + `SandboxDecisionPolicy.default()` factory only; no §14 contract specifies any internal field set (§14.9.1 step 5 reads only `sandbox.tier ≥ ToolContract.minimum_tier`; the field is a dangling marker per spec v1.16 §"Adjacent defects surfaced" finding (i)). Pre-committing internal fields (e.g. `tier_floor_overrides: Mapping[str, SandboxTier]`) would be a plan-side spec extension. **U-CORE-02 carrier shape is therefore empty-marker:** frozen Pydantic v2 BaseModel with NO fields + `@classmethod def default() -> SandboxDecisionPolicy` returning the empty instance. Future operator-driven extension surfaces via spec extension + planner revision pass adding fields.

**Changes at v1.2.**

| Site | v1.1 | v1.2 |
|---|---|---|
| §1 spec inventory | (preserved verbatim) | NEW row appended: `Spec_Harness_Runtime_v1.md` v1.16 §3 C-RT-02 `sandbox_decision_policy` field carrier home → `SandboxDecisionPolicy` (empty-marker class at `harness-core`) |
| §2 unit bodies | U-CORE-01 only | U-CORE-01 (preserved verbatim) + NEW U-CORE-02 unit body appended |
| §3 dependency graph | U-CORE-01 Level 0 only | U-CORE-01 + U-CORE-02 both Level 0; both source nodes; acyclic preserved |
| §4 coverage matrix | C-AS-09 / C-IS-05 / C-CP-05 / C-CP-13 rows | preserved + NEW row C-RT-02 §3 (runtime spec v1.16 `sandbox_decision_policy` carrier) → U-CORE-02 |
| §5 filing footer | v1.1 fields | v1.2 fields with predecessor `Implementation_Plan_Harness_Core_v1_1.md` |

**Cross-axis cascade.** ZERO per fork doc §5. CXA v2.8 unchanged. AS plan v1.2 / CP plan v2.17 / OD plan v2.15 unchanged.

**v1.1 content preserved verbatim outside the §0.5 / §1 row addition / §2 U-CORE-02 unit body / §3 dep-graph addition / §4 matrix row / §5 footer update.** U-CORE-01 body, the 9 identity aliases, `DeploymentSurface`, `PersonaTier`, `WorkflowEventClass`, the §0.1-§0.4 change-note sections all unchanged.

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
| `Spec_Harness_Runtime_v1.md` v1.16 C-RT-02 §3 (`sandbox_decision_policy` field carrier home) | Commits `SandboxDecisionPolicy` as a `harness-core` carrier per Q1=C-i Class 1 fork resolution 2026-05-22 → U-CORE-02 empty-marker class (v1.2 addition) |

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

### U-CORE-02 — `SandboxDecisionPolicy` empty-marker carrier (NEW at v1.2)

**Implements:** [`Spec_Harness_Runtime_v1.md` v1.16 §3 C-RT-02 — `sandbox_decision_policy: SandboxDecisionPolicy | None` field carrier-home commitment at `harness-core` (per Q1=C-i Class 1 fork resolution 2026-05-22, `.harness/class_1_fork_sandbox_decision_policy_phantom_cite.md`)].

> **Spec-traceability note.** Runtime spec v1.16 §3 C-RT-02 commits ONLY `SandboxDecisionPolicy | None` field type + `SandboxDecisionPolicy.default()` factory; NO §14 contract specifies any internal field set. §14.9.1 step 5 reads only `sandbox.tier ≥ ToolContract.minimum_tier` and does NOT consume the policy (spec v1.16 §"Adjacent defects surfaced" finding (i) — dangling marker). Per X-AL-3 (no silent H_T design extension at Phase 7) + `implementation-planner` SKILL.md §4 sub-discipline 4.4 (no spec extension): U-CORE-02 authors the **empty-marker** carrier — frozen Pydantic v2 BaseModel with NO fields + `.default()` factory. Future operator-driven extension (adding `tier_floor_overrides` or other fields) surfaces via spec extension + planner revision pass; not pre-committed here.

**Depends on:** (none) — foundational; sits beside U-CORE-01 and U-CP-00 at Level 0. U-CORE-02 imports nothing; `harness-runtime` U-RT-71 imports it.

**Inputs:** None (foundational; substrate-supplying type unit).

**Files affected (logical):**
- `harness-core` sandbox-decision-policy carrier module (logical: `sandbox-decision-policy-carrier`)
- `harness-core` package export surface (logical: `harness-core-init-exports` — EXTEND; U-CORE-01's exports preserved verbatim)

**Residence rationale.** Per workspace `CLAUDE.md` §3.3 (`harness-core` hosts shared types) + Q1=C-i operator ratification: the `SandboxDecisionPolicy` carrier is operator-supplied configuration semantics consumed at the `harness-runtime` package (`RuntimeConfig` field type + `materialize_runtime_tool_dispatcher_stage` factory body). Per the carrier-home decision matrix at Q1=C-i fork doc §3: `harness-core` is the home of choice because (a) the surface crosses runtime + (potential future) AS + (potential future) CP consumers; (b) `harness-runtime` home would couple a config-policy carrier to the runtime package boundary; (c) AS package home (option β/A in fork doc) was rejected by operator to avoid AS-spec reopen at C-i.

**Signatures:**

```
# --- sandbox-decision-policy empty-marker carrier ---

@frozen-pydantic-base-model
class SandboxDecisionPolicy:
  # NO fields declared at v1.2 — empty-marker carrier per Q1=C-i ratification
  # + carrier-shape decision (§0.5). Future operator-driven extension adds
  # fields via spec extension + planner revision pass.

  @classmethod
  def default() -> SandboxDecisionPolicy:
    # Returns the empty-marker instance (no operator-supplied policy fields).
    # The instance is value-identical for all callers (frozen + no fields →
    # all instances structurally equivalent).
    return SandboxDecisionPolicy()
```

> **Pydantic v2 shape.** Per workspace `CLAUDE.md` §3.1 stack discipline: `pydantic.BaseModel` with `ConfigDict(frozen=True, extra='forbid')`. Empty-field BaseModel is valid Pydantic v2 (the model has no fields to validate; `extra='forbid'` ensures construction with no kwargs succeeds and construction with any kwarg fails).

**Acceptance criteria:**

1. `SandboxDecisionPolicy` declared at `harness-core` package, a frozen Pydantic v2 BaseModel with `ConfigDict(frozen=True, extra='forbid')`. NO fields declared at v1.2 per Q1=C-i + carrier-shape empty-marker decision.
2. `SandboxDecisionPolicy.default()` classmethod returns a `SandboxDecisionPolicy` instance (the empty-marker singleton-equivalent instance — every instance is structurally identical because no fields exist).
3. `SandboxDecisionPolicy()` (bare construction with no kwargs) succeeds without ValidationError.
4. `SandboxDecisionPolicy(extra_field="anything")` raises `pydantic.ValidationError` per `extra='forbid'` invariant.
5. Frozen invariant: attempting to set any attribute on a constructed instance raises `pydantic.ValidationError` (or equivalent immutability error per Pydantic v2 frozen-model discipline).
6. Importable from the `harness-core` package public API surface — `from harness_core import SandboxDecisionPolicy` succeeds; consumed by `harness-runtime` U-RT-71 (`RuntimeConfig.sandbox_decision_policy` field type) + (future) U-RT-75 factory body step 3.
7. pyright strict mode passes.
8. No spec extension: NO field, NO method beyond `.default()`, NO behavior is introduced that is not committed by the runtime spec v1.16 §3 C-RT-02 row. The `.default()` factory satisfies the spec's commitment to "uses `SandboxDecisionPolicy.default()` if `None`"; nothing more.

**Tests:**
- `test_sandbox_decision_policy_is_pydantic_base_model`
- `test_sandbox_decision_policy_has_no_fields_at_v1_2`
- `test_sandbox_decision_policy_default_returns_instance`
- `test_sandbox_decision_policy_bare_construction_succeeds`
- `test_sandbox_decision_policy_extra_field_rejected`
- `test_sandbox_decision_policy_frozen_attribute_assignment_raises`
- `test_sandbox_decision_policy_importable_from_harness_core`
- `test_sandbox_decision_policy_no_spec_extension_audit` (assertion: dir(SandboxDecisionPolicy) public surface limited to Pydantic-baseline methods + `.default()`)

**Rollback boundary:** Revert the `SandboxDecisionPolicy` class declaration (carrier module) + `__init__` re-export addition. Downstream: `harness-runtime` U-RT-71 import fails; cluster L9-septies cluster opening blocked again pending re-resolution. A single coherent revert.

---

## §3 Dependency graph

- **U-CORE-01** — Level 0, `Depends on: (none)`. A pure source node, beside U-CP-00 (also Level 0). Acyclic — a source node with inbound-only edges cannot create a cycle.
- **U-CORE-02** (NEW at v1.2) — Level 0, `Depends on: (none)`. A pure source node, beside U-CORE-01 + U-CP-00. Acyclic — same source-node argument. Consumed by `harness-runtime` U-RT-71 (within-axis-cross-package edge added at `Implementation_Plan_Harness_Runtime_v2_13.md` §2 — co-published this arc).
- Downstream `[U-CORE-01]` edges (~17 units) + `[U-CP-00]` `WorkloadClass` edges (~15 units) + the NEW `[U-CORE-02]` edge to U-RT-71 are added by the per-axis revision passes (the U-RT-71 edge added by `Implementation_Plan_Harness_Runtime_v2_13.md` co-published this arc; further consumer edges, if any, surface at future axis-plan revision passes). Hand-off list at `.harness/revision_R1_harness_core.md` §3 (now extended).

DAG verified acyclic at v1.2: both U-CORE-01 and U-CORE-02 are L0 source nodes with no within-plan dependencies; no cycle creatable from source-only additions.

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
| `Spec_Harness_Runtime_v1.md` v1.16 §3 C-RT-02 (`sandbox_decision_policy` field carrier home → `SandboxDecisionPolicy` empty-marker class) | U-CORE-02 (NEW at v1.2) | Single-unit coverage at `harness-core` per Q1=C-i fork resolution; downstream consumer at `harness-runtime` U-RT-71 + (transitively) U-RT-75 factory body step 3 |

U-CORE-01 *adds* a coverage mark to multi-unit-covered contracts; R3/R4/R5 must not drop their existing C-AS-09 / C-CP-05 marks. U-CORE-02 single-unit-covers its row.

---

## §5 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Harness_Core_v1_2.md` |
| Version | v1.2 |
| Authored at | Phase 7 sub-phase 7b, 2026-05-22 — v1.2 `SandboxDecisionPolicy` Class 1 fork resolution absorption |
| Authoring authority | Operator ratification of Q1=C-i (`.harness/class_1_fork_sandbox_decision_policy_phantom_cite.md`, 2026-05-22) |
| Predecessor | `Implementation_Plan_Harness_Core_v1_1.md` (v1.1 Class 1 fork resolution — `WorkflowEvent` payload model struck; preserved verbatim outside the §0.5 / §1 row / §2 U-CORE-02 / §3 dep-graph node / §4 row / §5 footer additions) |
| New units at v1.2 | 1 (U-CORE-02) |
| Successor consumption | `harness-runtime` U-RT-71 at `Implementation_Plan_Harness_Runtime_v2_13.md` (co-published this arc) consumes U-CORE-02 via within-axis-cross-package edge; R2–R5 per-axis revision passes continue to consume the U-CORE-01 carrier + the §3 hand-off edges |
| Revision policy | Canonical for the `harness-core` shared-substrate plan; revisions in-CLI per workspace discipline |
| Fork ratification | `.harness/class_1_fork_sandbox_decision_policy_phantom_cite.md` RATIFIED 2026-05-22 |

*End of Implementation Plan — Harness Core v1.2. Two units (U-CORE-01 + U-CORE-02). U-CORE-01 + the R2–R5 per-axis passes preserved verbatim from v1.1; U-CORE-02 added at v1.2 per Q1=C-i fork resolution absorption.*
