# Revision R1 — `harness-core` Foundation: Introducing U-CORE-01

**Status:** ✅ ABSORBED-INTO-CANONICAL-PLAN (status-line refreshed 2026-05-28 Phase 1 status-cascade sweep per workflow v1.12 §7.4.7.3.B) — R1 ratified + applied at `design-substrate/Implementation_Plan_Harness_Core_v1_0.md` (now at canonical v1.2 per workspace `CLAUDE.md` §2.4 core row); revision proposal superseded by canonical plan chain. Species 3 stale-carry per workflow v1.12 §7.4.7.2.

**Status:** Proposed *(historical; predates 2026-05-15 ratification)*
**Revision pass:** R1 — `harness-core` foundation (the first of the 5-pass carrier-map absorption sequence R1–R5).
**Authored:** 2026-05-15 by the `implementation-planner` role in revision-pass sub-mode (`implementation-planner` SKILL.md §8).
**Mode:** Revision-pass. This is a **revision proposal artifact**, not an applied plan edit. The operator ratifies before any `design-substrate/` plan is amended.

**HARD WALL.** This pass writes only `.harness/revision_R1_harness_core.md`. No `design-substrate/` file, no `CLAUDE.md`, no plan/spec/audit/carrier-map, no source code is edited. No git commit.

---

## §0 Change-note

### §0.1 Trigger

Two ratified upstream recommendations:

- `.harness/shared_type_carrier_map.md` (Pipeline Pass T1) — Disposition-1 rows assign a set of cross-cutting types to `harness-core`; the "Carrier-unit gap section" names **U-CORE-01** as the new `harness-core` carrier unit.
- `.harness/xal3_resolution_recommendations.md` (Pipeline Pass T2) — 27 of 27 X-AL-3 candidates resolved as **FACTOR-OUT** (concept spec-committed; declaration site missing). Zero design-substrate revision required. `WorkflowEvent` and `DeploymentSurface` re-route to `harness-core` / U-CORE-01.

R1 is the **prerequisite pass** for the four per-axis revision passes (R2 IS / R3 AS / R4 CP / R5 OD): the disposition-1 carrier types must exist in `harness-core` before any axis plan can cite them. This pass proposes the U-CORE-01 unit body and the plan-home for it.

### §0.2 Scope of R1

| In scope | Out of scope |
|---|---|
| Plan-home recommendation for U-CORE-01 (§1) | Editing any `design-substrate/` plan (operator applies post-ratification) |
| U-CORE-01 full atomic-unit body (§2) | U-CP-00b (CP foundational unit) — that is R4's scope |
| Downstream dep-edge hand-off list per axis (§3) | Per-axis carrier units (AS/CP/OD in-place carriers) — R2–R5 scope |
| Retrospective re-check flags for landed units (§4) | The X-AL-3 disposition-2 (per-axis-owned) types — R2–R5 scope |

`WorkloadClass` already resides in `harness-core` via the **landed U-CP-00** (CP plan v2.5 §2.0). **U-CORE-01 does NOT redeclare `WorkloadClass`** — it is accounted for in §2 as a pre-existing `harness-core` resident; U-CORE-01 sits beside it in the package.

### §0.3 Type inventory delta

`harness-core` package before R1: `WorkloadClass` (U-CP-00, landed) only.
`harness-core` package after U-CORE-01 lands: `WorkloadClass` + the U-CORE-01 set (§2).

---

## §1 Plan-home recommendation for U-CORE-01

**Recommendation:** File U-CORE-01 in a **new dedicated `harness-core` plan** — `Implementation_Plan_Harness_Core_v1.0.md` — NOT appended to an existing axis plan.
**Status: Proposing.** This is a *proposing*-class recommendation; the operator ratifies. Trade-offs spelled out below.

### §1.1 The U-CP-00 precedent and why it differs here

U-CP-00 (`WorkloadClass`) physically resides in `harness-core/` but its **unit body is filed in the CP plan** (`Implementation_Plan_Control_Plane_v2_5.md` §2.0). The CP plan v2.5 §2.0 residence rationale is explicit on *why*: "The CP plan carries the declaring unit because **C-CP-07 §7.3 is the spec contract that commits the taxonomy**; the unit's `Files affected` targets `harness-core`." U-CP-00 is plan-homed in CP because exactly one spec contract — a CP contract — commits `WorkloadClass`. The plan that owns the committing contract owns the unit body; the package is orthogonal to the plan-home.

U-CORE-01 is structurally different. It declares **a set of types committed by contracts spread across three different axis specs**:

| U-CORE-01 type | Committing spec/ADR | Committing axis |
|---|---|---|
| `DeploymentSurface` | AS spec §9.1 (C-AS-09 12-cell matrix, deployment-surface axis) | AS |
| `PersonaTier` | AS spec §9.4 + §11 (per-persona-tier composition); ADR-F4; ADR-D5 v1.3 §1.5 | AS / cross |
| Identity aliases (`ActionID`, `EntryID`, …) | IS spec C-IS-05 §5 (`action_id`/`entry_id`); CP spec §5 (`workflow_id`/`step_id`/`thread_id`); plan-unit-ID domain (`UnitId`/`ReferenceToUnit`); AS/CP contract IDs (`ContractID`/`StageID`) | IS / CP / cross |
| `WorkflowEvent` (see §2 note) | CP spec §5.1 (C-CP-05, 8-class lifecycle event taxonomy) | CP |

There is no single committing axis. Appending U-CORE-01 to any one axis plan (CP, say) would mis-state ownership: the CP plan does not commit `DeploymentSurface` or the `action_id`/`entry_id` aliases. The U-CP-00 "plan that owns the committing contract owns the unit body" rule does not select a single plan-home for U-CORE-01 — because no single plan owns all the committing contracts.

### §1.2 Options and trade-offs

| Option | For | Against |
|---|---|---|
| **A. New dedicated `harness-core` plan** (`Implementation_Plan_Harness_Core_v1.0.md`) — RECOMMENDED | Plan-home matches package identity 1:1; future `harness-core` units (the package will grow) have an obvious home; no axis plan misrepresents ownership of cross-cutting types it does not commit; `CLAUDE.md` §3.3 already treats `harness-core` as a first-class workspace member ("hosts shared types + cross-axis utilities"); the new plan declares the dependency-graph-led shape (`implementation-planner` SKILL.md §6) — `harness-core` is the topological root of the IS<AS<CP<OD order. | Introduces a 6th plan file; `CLAUDE.md` §2.4's per-axis-plan table does not yet enumerate a `harness-core` plan (operator must add the row — a `CLAUDE.md` edit, itself routed through ratification). |
| **B. Append U-CORE-01 to the CP plan** (beside U-CP-00) | Co-locates the two `harness-core`-resident units; reuses the v2.5 §2.0 precedent surface; no new file. | Mis-states ownership — CP plan would carry `DeploymentSurface` (AS-committed) and `EntryID` (IS-committed); violates the U-CP-00 rule's own logic ("the plan that owns the committing contract"); makes the CP plan a dumping ground for cross-cutting types as the package grows; couples `harness-core` evolution to CP plan versioning. |
| **C. Append to the IS plan** (IS is topological root of the axes) | IS is upstream-most; `EntryID` has an IS basis. | IS does not commit `DeploymentSurface`/`PersonaTier`/`WorkflowEvent`; same ownership-misstatement defect as B; IS plan is the smallest/cleanest axis and absorbing cross-cutting types pollutes it. |
| **D. Split U-CORE-01 across axis plans** (each axis plan declares the subset its spec commits) | Every type's plan-home matches its committing contract. | Defeats the carrier-map's core finding — a single carrier prevents N distinct pyright types; splitting re-creates the multi-declaration defect at the *plan* level; no longer one atomic unit; fails §3.1 single-coherent-change. Rejected. |

### §1.3 Recommendation rationale (authority chain)

- `CLAUDE.md` §1.3 authority chain: ADR → ADD → PRD → per-axis spec → per-axis plan + CXA. The plans are **per-axis** by the chain's structure. `harness-core` is **not an axis** — it is the shared substrate the four axes import (`CLAUDE.md` §3.3: "shared `harness-core/`"; "`harness-core/` hosts shared types + cross-axis utilities"). A cross-cutting carrier unit therefore does not belong *inside* an axis plan; it belongs in a plan whose scope is the shared substrate.
- The carrier map's own "Recommended ordering" section treats `harness-core` as **step 1 — "a prerequisite, not a per-axis pass."** A prerequisite that is not a per-axis pass should not be filed inside a per-axis plan artifact.
- U-CP-00 is the precedent for **a foundational unit whose code resides in `harness-core`** — and it is honored: U-CORE-01 is exactly that. U-CP-00 is *not* a precedent for *which plan file* a multi-axis-committed carrier unit is filed in; that question did not arise for U-CP-00 because `WorkloadClass` has a single committing contract.
- Option A keeps each plan's coverage matrix honest: the new `harness-core` plan's coverage matrix rows are the cross-cutting contracts (C-AS-09 §9.1 deployment-surface axis; the identity-field commitments of C-IS-05 §5 / CP §5; C-CP-05 §5.1 for `WorkflowEvent`), cited from their home specs — a faithful multi-spec coverage matrix, which `implementation-planner` SKILL.md §4.2 permits ("multi-contract composition is allowed and common; cite all governing contracts").

### §1.4 Open question for the operator (Q-R1-1)

Option A requires a `CLAUDE.md` §2.4 edit to enumerate the new `Implementation_Plan_Harness_Core_v1.0.md` and a §2.5-adjacent note that `harness-core` now carries a plan (it currently has "no `CLAUDE.md`" per the carrier map). `CLAUDE.md` is canonical-for-this-workspace and its revision routes through ratification (`CLAUDE.md` §9.1 revision policy). **The operator must authorize the `CLAUDE.md` row addition as part of ratifying Option A.** If the operator declines a 6th plan file, Option B is the fallback — accept the ownership-misstatement cost, file U-CORE-01 in the CP plan as `Implementation_Plan_Control_Plane_v2_6.md` §2.0b beside U-CP-00.

---

## §2 U-CORE-01 — unit body

Filed below in the canonical per-unit plan format (`implementation-planner` SKILL.md §4.4 + the U-CP-00 template). On Option A ratification this body is transcribed into `Implementation_Plan_Harness_Core_v1.0.md` §2.0; on Option B fallback into the CP plan.

---

#### U-CORE-01 — Declare the cross-cutting `harness-core` shared-type set (cross-axis enums + identity-alias module + `WorkflowEvent`)

**Implements:** [C-AS-09 §9.1] (DeploymentSurface); [C-AS-09 §9.4] + [ADR-D5 v1.3 §1.5] (PersonaTier); [C-IS-05 §5] (EntryID, ActionID — the F2 six-field entry-shape identifier fields); [C-CP-05 §5.1, §5.2] (WorkflowID, StepID, ThreadID identifier fields + WorkflowEvent 8-class lifecycle taxonomy); [C-CP-13 §13.4] (StageID — handoff/stage identifier); [C-AS-03 §3] / [C-CP-01 §1] (ContractID — tool/routing contract identifier).

> **Spec-traceability note.** Each declared type is traced to a committing contract per the carrier map T1 disposition-1 rows + the T2 FACTOR-OUT verdicts. Every trace above is to the **concept**; the alias/enum *shape* is a faithful operationalization of spec prose, not a spec extension (T2 discriminator: "does any spec/ADR commit the CONCEPT"). The §2 acceptance criteria pin each type to its section.
>
> **`UnitId` / `ReferenceToUnit` — trace caveat (open item Q-R1-5).** These two aliases are NOT traced to a spec/ADR section. They are **plan-internal identifiers** — `UnitId` is the atomic-unit identifier domain (`"U-CP-22"` etc.) the *plans* use; `ReferenceToUnit` is consumed only at CP U-CP-41 (carrier map CP Pattern-D table) with no spec contract behind it. Per `implementation-planner` SKILL.md §4.2, a unit citing a contract must cite "ID and section" — these have no such section. R1 flags this honestly rather than inventing a trace: the operator confirms whether (a) `UnitId`/`ReferenceToUnit` are kept in U-CORE-01 as explicitly **plan-internal** identifiers (carrier-convenience, no spec contract — acceptable for a thin `str`-newtype with no shape ambiguity, but acknowledged as non-spec-traced), or (b) they are dropped from U-CORE-01 and materialized inline at U-CP-41 by R4. R1 default: keep in U-CORE-01 as plan-internal, explicitly non-traced. See Q-R1-5 in §6.

**Depends on:** (none) — foundational; the topological root of the `harness-core` → IS → AS → CP → OD order (carrier map "Recommended ordering" §1). U-CORE-01 imports nothing; all four axes import it.

**Inputs:** None (foundational; substrate-supplying type unit — mirrors U-CP-00's "foundational; substrate-supplying enum unit").

**Files affected (logical):**
- `harness-core` deployment-surface enum (logical: `deployment-surface-enum`)
- `harness-core` persona-tier enum (logical: `persona-tier-enum`)
- `harness-core` identity-alias module (logical: `identity-aliases`) — the `str`-newtype set
- `harness-core` workflow-event type (logical: `workflow-event-type`)
- `harness-core` package export surface (logical: `harness-core-init-exports`) — the package `__init__` re-export so consumers import from one path

`Files affected` targets `harness-core` for every item — the U-CP-00 residence pattern ("the unit's `Files affected` targets `harness-core`"). `WorkloadClass` is **not** in this list — it is the landed U-CP-00 product, untouched by U-CORE-01.

**Residence rationale.** Every type in this unit is consumed by ≥2 axes (most by 3–4); per `CLAUDE.md` §3.3 (`harness-core` hosts shared types) and the carrier map disposition-1 criterion ("genuinely cross-axis shared primitive; declared once in `harness-core`, all axes import"), they reside in `harness-core`. A single carrier prevents pyright treating N independent declarations as N distinct types (the carrier map's core defect: `DeploymentSurface` "declared independently twice (AS+OD)").

**Signatures:**

```
# --- cross-cutting enums ---

enum DeploymentSurface {
  LOCAL_DEVELOPMENT,                                  // AS §9.1 matrix row "local-development"
  SELF_HOSTED_SERVER,                                 // AS §9.1 matrix row "self-hosted-server"
  MANAGED_CLOUD                                       // AS §9.1 matrix row "managed-cloud"
}
// Closed at cardinality 3 — the AS spec §9.1 C-AS-09 12-cell matrix's
// deployment-surface axis enumerates exactly these three rows. String values
// are the §9.1 row labels verbatim (lowercase-hyphen).

enum PersonaTier {
  SOLO_DEVELOPER,                                     // AS §9.4 / §11 "solo-developer"
  TEAM_BINDING,                                       // AS §9.4 / §11 "team-binding"
  MULTI_TENANT_COMPLIANCE                             // AS §9.4 / §11 "multi-tenant-compliance"
}
// Closed at cardinality 3 — the F4 persona-tier ladder (AS §9.4 operator-policy
// override scope per persona tier; AS §11 bridging-arc traversal
// "solo-developer -> team-binding -> multi-tenant-compliance"; ADR-D5 v1.3 §1.5
// per-persona-tier audit-ledger cryptographic shape). String values verbatim.

# --- identity-alias module: thin str-newtypes, no shape ambiguity ---

newtype ActionID        = str   // C-IS-05 §5 F2 entry shape `action_id`
newtype EntryID         = str   // C-IS-05 §5 state-ledger entry identifier
newtype WorkflowID      = str   // C-CP-05 §5 `workflow.id` / `workflow_id`
newtype StepID          = str   // C-CP-05 §5 `step_id` / step-boundary identifier
newtype ThreadID        = str   // C-CP-05 §5 `thread_id` (idempotent-write keying tuple)
newtype StageID         = str   // C-CP-13 §13.4 handoff/stage identifier
newtype UnitId          = str   // atomic-unit identifier (plan-unit domain, e.g. "U-CP-22")
newtype ReferenceToUnit = str   // a reference to an atomic unit (CP U-CP-41 consumption)
newtype ContractID      = str   // tool/routing contract identifier (C-AS-03 / C-CP-01)

# --- workflow-event lifecycle type ---

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
// WorkflowEvent record: the C-CP-05 §5.1 8-class lifecycle event + §5.2
// per-class minimum attribute set. Pydantic v2 model carrying `event_class:
// WorkflowEventClass` + the §5.2 attribute payload. Field set is the §5.2
// per-class minimum attribute set verbatim — a faithful factor-out (T2 verdict:
// FACTOR-OUT, decided).
model WorkflowEvent { event_class: WorkflowEventClass; ... per §5.2 ... }
```

> **Note on `WorkflowEvent` inclusion.** The task framing lists the identity aliases + cross-cutting enums as the U-CORE-01 set. The carrier map's "Carrier-unit gap section" U-CORE-01 row names `DeploymentSurface`, `PersonaTier`, and the identity-alias module — it does **not** list `WorkflowEvent`. However the **T2 resolution table (decided row)** explicitly re-routes `WorkflowEvent` to "`harness-core` (U-CORE-01)". This is a divergence between the T1 carrier-map row text and the T2 verdict. **Open question Q-R1-2 (see §5):** the operator confirms whether `WorkflowEvent` is declared in U-CORE-01 (per T2) or carried separately. This unit body includes it per the later T2 verdict; if the operator rules it out, strike the `WorkflowEvent`/`WorkflowEventClass` signature block and the C-CP-05 §5.1/§5.2 `Implements` citations, with no other change to the unit.

**Acceptance criteria:**

1. `DeploymentSurface` declares exactly three values per AS spec §9.1 (C-AS-09) — the SCREAMING_SNAKE_CASE rendering of the §9.1 12-cell matrix deployment-surface axis rows `local-development | self-hosted-server | managed-cloud`. Closed at cardinality 3. Member string values match the §9.1 row labels byte-exact.
2. `PersonaTier` declares exactly three values — the SCREAMING_SNAKE_CASE rendering of the F4 persona-tier ladder `solo-developer | team-binding | multi-tenant-compliance` (AS §9.4 / §11; ADR-D5 v1.3 §1.5). Closed at cardinality 3. String values verbatim.
3. The identity-alias module declares exactly nine `str`-newtype aliases — `ActionID`, `EntryID`, `WorkflowID`, `StepID`, `ThreadID`, `StageID`, `UnitId`, `ReferenceToUnit`, `ContractID` — each a distinct nominal type (a bare `str` is NOT assignable where an alias is required, and vice versa, under `pyright` strict). Seven aliases are traced to a committing section per the `Implements` line; `UnitId`/`ReferenceToUnit` are plan-internal identifiers carried without a spec trace per the Q-R1-5 caveat above.
4. `WorkflowEvent` declares the C-CP-05 §5.1 8-class lifecycle event taxonomy (`WorkflowEventClass`, closed at cardinality 8, values verbatim) and a payload model carrying the §5.2 per-class minimum attribute set. **(Conditional on Q-R1-2 — see signature note.)**
5. Every type resides in `harness-core` and is exposed at the `harness-core` package public API surface so all consuming axes import from one path. `WorkloadClass` (U-CP-00, landed) is unaffected and remains beside the U-CORE-01 set in the package. *(The `harness-core` `pyproject.toml` uses whole-package wheel inclusion — `packages = ["src/harness_core"]` — so new modules need no per-module packaging change; the public-API exposure mechanism is the package `__init__`, an implementation-discretion detail not pinned by this criterion.)*
6. No spec extension: no field, value, or alias is introduced that is not committed by the cited contract. Where a spec defers shape (e.g. C-IS-05 §5 "Deferred to implementation discretion: Specific identifier format for `action_id` — UUID v4 / ULID / monotonic-counter"), the alias is `str`-typed and the concrete format is **not** pinned by this unit (deferral honored).

**Tests:**
- `test_deployment_surface_cardinality_three`; `test_deployment_surface_values_match_as_spec_9_1_verbatim`; `test_deployment_surface_closed`
- `test_persona_tier_cardinality_three`; `test_persona_tier_values_match_as_spec_9_4_verbatim`; `test_persona_tier_closed`
- `test_identity_aliases_all_nine_declared`; `test_identity_alias_nominal_distinct_under_pyright` (a `pyright`-strict assignability check — `ActionID` not assignable to/from bare `str` or to `EntryID`)
- `test_workflow_event_class_cardinality_eight`; `test_workflow_event_class_values_match_cp_spec_5_1_verbatim`; `test_workflow_event_payload_matches_spec_5_2` *(conditional on Q-R1-2)*
- `test_all_u_core_01_types_reside_in_harness_core`; `test_harness_core_init_reexports_u_core_01_set`
- `test_workload_class_unaffected_by_u_core_01` (regression — U-CP-00 product intact)

**Rollback boundary:** Revert the U-CORE-01 type declarations (the deployment-surface enum, persona-tier enum, identity-alias module, workflow-event type, and the `__init__` re-export additions). `WorkloadClass` / U-CP-00 is unaffected — U-CORE-01 declares no edge to it and shares only the package. Downstream impact on revert: every IS/AS/CP/OD unit that took a `Depends on: [U-CORE-01 (cross-axis: core)]` edge (§3) loses its carrier; the multi-declaration defect the carrier map identified reopens. A single coherent revert (one logical change) — satisfies `implementation-planner` SKILL.md §3.4.

---

## §3 Downstream dependency-edge consequences — hand-off to R2–R5

Every existing axis unit that consumes a U-CORE-01 type needs a `Depends on: [U-CORE-01 (cross-axis: core)]` edge added **by its own axis's revision pass** (R2 IS / R3 AS / R4 CP / R5 OD). R1 does not edit those plans; this is the hand-off list. Edge targets derived from the carrier map disposition-1 rows + CP Pattern-D per-type table + the T2 re-route table.

> **Edge form.** Per `implementation-planner` SKILL.md §7, a non-axis foundational dependency is still flagged cross-axis: `Depends on: [U-CORE-01 (cross-axis: core)]`. `harness-core` is shared substrate, not an axis — the annotation makes the import explicit and reviewable. This is an *import* edge, not an outbound CXA edge: per T2, an IS unit importing `harness-core` does **not** violate the CXA §2.4 "IS = 0 outbound edges" invariant.

### §3.1 IS axis — handed to R2 (IS plan revision pass)

| Unit | U-CORE-01 type(s) consumed | Source |
|---|---|---|
| U-IS-02 | `DeploymentSurface`, `WorkflowClass`* | carrier map disposition-1 (`DeploymentSurface` row); `WorkflowClass`=U-CP-00 |
| U-IS-05 | `DeploymentSurface`, `WorkflowClass`* | carrier map disposition-1 |
| U-IS-12 | `WorkflowClass`* | carrier map disposition-1 (`WorkloadClass` row) |
| U-IS-14 | `WorkflowEvent` | carrier map disposition-3 / T2 `WorkflowEvent` row (conditional on Q-R1-2) |

\* `WorkflowClass`/`WorkloadClass` is the **landed U-CP-00** type — the IS units need a `Depends on: [U-CP-00]` edge for it (or `[U-CORE-01]` if the operator folds it; recommend `[U-CP-00]` — U-CP-00 is the carrier). R2 also absorbs the IS-internal `WorkflowClass`-vs-`WorkloadClass` spelling unification (a verbatim-pass item flagged in the carrier map). **IS units: 4 distinct units (U-IS-02, U-IS-05, U-IS-12, U-IS-14).**

### §3.2 AS axis — handed to R3 (AS plan revision pass)

| Unit | U-CORE-01 type(s) consumed | Source |
|---|---|---|
| U-AS-04 | `DeploymentSurface`, `PersonaTier` — **currently the declaring site** | carrier map "already-declared" table |
| U-AS-30 | `WorkloadClass`* | carrier map disposition-1 |

U-AS-04 is the landed AS unit that **currently declares `DeploymentSurface`/`PersonaTier`/`MCPTransport` itself**. R3 must convert U-AS-04 from a *declaring* site to a *consuming* site for `DeploymentSurface` and `PersonaTier` (delete the in-AS declaration; import from `harness-core`; add the `Depends on: [U-CORE-01 (cross-axis: core)]` edge). `MCPTransport` stays AS-owned (carrier map "already-declared" table — proposing; not a U-CORE-01 type). **AS units: 2 distinct units (U-AS-04, U-AS-30); U-AS-04 is a declaration-site conversion, not just an edge add.**

### §3.3 CP axis — handed to R4 (CP plan revision pass)

`WorkloadClass` consumers (carrier map CP Pattern-E; already noted in CP plan v2.5 §3 as "recorded; materialized at next full-revision"): U-CP-05, U-CP-06, U-CP-09, U-CP-13, U-CP-17, U-CP-21, U-CP-23, U-CP-29, and the others in the Pattern-E set — these need `Depends on: [U-CP-00]` (the landed `WorkloadClass` carrier).

| Unit | U-CORE-01 type(s) consumed | Source |
|---|---|---|
| U-CP-05/06/09/13/17/21/23/29 + Pattern-E tail | `WorkloadClass`* (→ `[U-CP-00]`) | carrier map disposition-1 + CP v2.5 §3 |
| U-CP-16, U-CP-17 | `DeploymentSurface` | carrier map disposition-1 (`DeploymentSurface` row) |
| U-CP-17, U-CP-25, U-CP-36, U-CP-50, U-CP-40 | `PersonaTier` | carrier map disposition-1 (`PersonaTier` row — "hidden coupling today"); U-CP-40 currently re-declares it |
| U-CP-29 | `StageID` | carrier map CP Pattern-D table (`StageID` → U-CORE-01) |
| U-CP-41 | `ReferenceToUnit` | carrier map CP Pattern-D table (`ReferenceToUnit` → U-CORE-01) |
| U-CP-14, U-CP-27, U-CP-30, U-CP-49 | identity aliases (`ActionID`/`ActorIdentity`-family) | carrier map "Note on `ActorIdentity` vs IS `Actor`" — recommended `harness-core` alias placement |

R4 also converts U-CP-40 from a `PersonaTier` re-declaring site to a consuming site.

**CP unit counts.** The `WorkloadClass`/U-CP-00 edge set is **named exactly by the CP plan v2.5 itself** — v2.5 §0.1 lists "U-CP-05, U-CP-06, U-CP-09, U-CP-13, U-CP-17, U-CP-21, U-CP-22, U-CP-23, and others" and §0.5 confirms "~10 other `WorkloadClass`-consuming units" gain a `[U-CP-00]` edge (U-CP-22's edge is already materialized at v2.5). The non-`WorkloadClass` U-CORE-01-consuming CP units are derived from the carrier-map disposition-1 + Pattern-D rows: U-CP-14/16/17/25/27/29/30/36/40/41/49/50 — **12 unit IDs**, several consuming multiple U-CORE-01 types. Both lists remain *proposing* — R4 resolves the exact unit set against the CP plan §3 dependency graph and the landed Pattern-E enumeration before materializing edges.

### §3.4 OD axis — handed to R5 (OD plan revision pass)

| Unit | U-CORE-01 type(s) consumed | Source |
|---|---|---|
| U-OD-01 | `DeploymentSurface`, `PersonaTier` — **currently a re-declaring site** | carrier map "already-declared" + disposition-1 rows |
| U-OD-22 | `WorkloadClass`* (→ `[U-CP-00]`) | carrier map disposition-1 + disposition-3 (`WorkloadClass`@OD-22 resolves via core import, no CXA edge) |

U-OD-01 independently re-declares `DeploymentSurface` and `PersonaTier` (carrier map: "declared independently twice (AS+OD)"; "PersonaTier re-declared at OD U-OD-01"). R5 converts U-OD-01 from a re-declaring site to a consuming site for both enums. **OD units: 2 distinct units (U-OD-01, U-OD-22); U-OD-01 is a declaration-site conversion.**

### §3.5 Hand-off summary (count of downstream units needing a core dep-edge)

| Axis | Pass | Units needing a `[U-CORE-01]` edge | Units needing a `[U-CP-00]` (`WorkloadClass`) edge | Declaration-site conversions |
|---|---|---|---|---|
| IS | R2 | U-IS-02, U-IS-05, U-IS-14 (3) | U-IS-02, U-IS-05, U-IS-12 (3) | none |
| AS | R3 | U-AS-04 (1) | U-AS-30 (1) | U-AS-04 (DeploymentSurface, PersonaTier) |
| CP | R4 | ~12 (U-CP-14/16/17/25/27/29/30/36/40/41/49/50) | ~10 (U-CP-05/06/09/13/17/21/23/29 + Pattern-E tail) | U-CP-40 (PersonaTier) |
| OD | R5 | U-OD-01 (1) | U-OD-22 (1) | U-OD-01 (DeploymentSurface, PersonaTier) |

**Aggregate:** ~17 distinct units take a direct `[U-CORE-01]` edge; a further ~15 take the `[U-CP-00]` `WorkloadClass` edge (some units appear in both columns — e.g. U-IS-02, U-CP-17). 4 units are declaration-site conversions (U-AS-04, U-CP-40, U-OD-01 — U-OD-01 covers two enums). Exact unit lists are *proposing* — R2–R5 each verify their axis's list against the landed source and the per-axis plan coverage matrix.

---

## §4 Retrospective note — landed units consuming now-U-CORE-01 types

Three units are **already landed** (Phase 7 7b operational-minimum set, per `.harness` memory) and consume types that U-CORE-01 will now declare. Their axis revision passes must **re-check the landed source against the U-CORE-01 declarations** — a verbatim-conformance re-check, not a fresh implementation:

| Landed unit | Axis / pass | What R-pass must re-check |
|---|---|---|
| **U-AS-02** | AS / R3 | If U-AS-02 consumes `DeploymentSurface`/`PersonaTier` (it is in the AS sandbox-tier cone — likely), the landed source must be re-pointed from any local AS declaration to the `harness-core` import. R3 verifies the landed enum values match U-CORE-01 byte-exact; if U-AS-04's local declaration was the source U-AS-02 imported, the conversion is transitive. |
| **U-OD-04** | OD / R5 | U-OD-04 is the OD OTel base-layer anchor (carrier map). If it consumes `DeploymentSurface`/`PersonaTier` (audit-ledger cryptographic shape is per-persona-tier — ADR-D5 v1.3 §1.5 — so likely), re-check the landed source uses the `harness-core` enum, not the U-OD-01 re-declaration. |
| **U-IS-02** | IS / R2 | U-IS-02 consumes `DeploymentSurface` and `WorkflowClass` (carrier map disposition-1). Landed source must be re-checked: it currently consumes these **undeclared** (carrier map: "consumed undeclared at IS U-IS-02/05"). R2 must verify the landed U-IS-02 code compiles against the U-CORE-01 `DeploymentSurface` and the U-CP-00 `WorkloadClass` — if the landed code inlined a local definition or a `str` placeholder, R2 re-points it. |

**Discipline flag for R2/R3/R5.** A landed unit that consumed a type *before* its carrier existed may have (a) inlined a local declaration, (b) used a bare `str`/`Any` placeholder, or (c) imported from a sibling unit's declaration. All three are now non-conformant once U-CORE-01 lands. The axis revision pass MUST inspect the landed source (not just the plan unit body) and record the re-point in its change-note. This is a **source-vs-plan reconciliation** item — it is the axis pass's responsibility, but R1 flags it here so it is not missed. R1 itself does not touch source (HARD WALL).

---

## §5 Coverage matrix + dependency graph delta

### §5.1 Coverage matrix delta (for the new `harness-core` plan, Option A)

| Contract row | Covered by |
|---|---|
| C-AS-09 §9.1 (deployment-surface axis of the 12-cell matrix) | U-CORE-01 *(also covered for the matrix proper by the AS plan's U-AS-09 — U-CORE-01 covers only the enum axis)* |
| C-AS-09 §9.4 + ADR-D5 v1.3 §1.5 (persona-tier ladder) | U-CORE-01 |
| C-IS-05 §5 (F2 entry-shape identifier fields — `action_id`, `entry_id` as nominal types) | U-CORE-01 *(the entry shape proper is IS plan U-IS-0x; U-CORE-01 covers the identifier-alias factor-out only)* |
| C-CP-05 §5.1, §5.2 (lifecycle event taxonomy → `WorkflowEvent`) | U-CORE-01 *(conditional Q-R1-2)* |
| C-CP-13 §13.4 (`StageID`) | U-CORE-01 |

> A coverage-matrix subtlety the operator should note: U-CORE-01 covers the **identifier/enum factor-out** of contracts whose **primary** coverage lives in an axis plan (e.g. C-AS-09's 12-cell matrix is AS-plan-covered; U-CORE-01 covers only its deployment-surface enum axis). This is multi-unit coverage of one contract — permitted (`implementation-planner` SKILL.md §4.2). R3/R4/R5 coverage matrices must not *drop* their existing C-AS-09 / C-CP-05 marks; U-CORE-01 *adds* a mark, it does not move one.

### §5.2 Dependency graph delta

- New node: **U-CORE-01** at Level 0 (`Depends on: (none)`) — a pure source node, beside U-CP-00 (also Level 0).
- New edges (added by R2–R5, not R1): ~17 `[U-CORE-01]` edges + ~15 `[U-CP-00]` edges per §3.5.
- Acyclic invariant: holds. U-CORE-01 has no outbound dependency; it can only be a source node. No cycle is creatable by adding inbound-only edges to a source node.

---

## §6 Open questions for the operator

| ID | Question | R1 default taken |
|---|---|---|
| **Q-R1-1** | Option A (new `Implementation_Plan_Harness_Core_v1.0.md`) requires a `CLAUDE.md` §2.4 row addition. Authorize the `CLAUDE.md` edit, or fall back to Option B (U-CORE-01 in CP plan v2.6 §2.0b)? | Recommend Option A; this artifact is written assuming A, with B as documented fallback. |
| **Q-R1-2** | T1 carrier map's U-CORE-01 row does NOT list `WorkflowEvent`; T2 resolution table (decided) re-routes `WorkflowEvent` to "`harness-core` (U-CORE-01)". Include `WorkflowEvent`/`WorkflowEventClass` in U-CORE-01? | Included per the later T2 verdict; strike-instructions provided in §2 if the operator rules it out. |
| **Q-R1-3** | `WorkloadClass` consumers — edge to the landed `[U-CP-00]`, or fold `WorkloadClass`'s carrier into U-CORE-01? | Recommend `[U-CP-00]` — it is the landed carrier; do not disturb it. U-CORE-01 sits beside it. |
| **Q-R1-4** | The identity-alias module: carrier map flags it *Proposing* — operator may instead ratify per-axis inline materialization. Confirm the single `harness-core` identity-alias module (the R1 recommendation)? | Single `harness-core` module — the aliases are demonstrably consumed by ≥3 axes (carrier map note). |
| **Q-R1-5** | `UnitId`/`ReferenceToUnit` have no spec/ADR section trace (plan-internal identifiers). Keep in U-CORE-01 as explicitly non-traced plan-internal aliases, or drop and materialize inline at U-CP-41 (R4)? | Keep in U-CORE-01, explicitly flagged non-traced (see §2 `Implements` caveat). |

---

## §7 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/revision_R1_harness_core.md` |
| Role | `implementation-planner`, revision-pass sub-mode (SKILL.md §8) |
| Authored | 2026-05-15, Phase 7 sub-phase 7b |
| Inputs | `shared_type_carrier_map.md` (T1); `xal3_resolution_recommendations.md` (T2); `Implementation_Plan_Control_Plane_v2_5.md` §0 + U-CP-00; `harness-core/src/harness_core/workload_class.py`; `Spec_Action_Surface_v1.md` §9; `Spec_Information_Substrate_v1.md` C-IS-05 §5; `Spec_Control_Plane_v1_2.md` §5 |
| Status | `Proposed` — pending operator ratification of §1 plan-home (Q-R1-1) and §6 open questions |
| Successor | On ratification: `Implementation_Plan_Harness_Core_v1.0.md` (Option A) or CP plan v2.6 (Option B) carries the U-CORE-01 body; R2–R5 per-axis passes consume the §3 hand-off list |
| HARD WALL attested | This pass wrote only this file. No `design-substrate/`, `CLAUDE.md`, plan, spec, audit, carrier-map, or source edit. No git commit. |

*End of Revision R1 — `harness-core` Foundation. The operator ratifies. R1 is the prerequisite for the four per-axis revision passes R2–R5.*
