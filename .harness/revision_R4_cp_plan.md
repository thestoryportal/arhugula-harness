# Revision R4 — Control Plane Plan: Materializability Conformance (v2.5 → v2.6)

**Status:** Proposed
**Revision pass:** R4 — CP plan materializability conformance (the fourth of the 5-pass carrier-map absorption sequence R1–R5; the largest — 56 units, 24 forks).
**Authored:** 2026-05-15 by the `implementation-planner` role in revision-pass sub-mode (`implementation-planner` SKILL.md §8).
**Mode:** Revision-pass. This is a **revision PROPOSAL artifact**, not an applied plan edit. The operator ratifies before any `design-substrate/` plan is amended.

**HARD WALL.** This pass writes only `.harness/revision_R4_cp_plan.md`. No `design-substrate/` file, no `CLAUDE.md`, no plan/spec/audit/carrier-map, no source code is edited. No git commit.

---

## §0 Change-note (v2.5 → v2.6)

### §0.1 Trigger

Two ratified upstream recommendations, and the R1-applied carrier:

- `.harness/materializability_audit_cp_plan.md` (Pipeline Pass Q2) — the canonical CP-plan systemic-tension record. Plan-wide materializability audit: of 56 CP units, **20 CLEARED / 12 CONFORM / 24 FORK**. Three CP-specific systemic patterns crossing the SKILL.md §6 ≥3-occurrence threshold: **Pattern C** (`AttributeValueType`/`Cardinality` declared once at U-CP-01, consumed sideways with no carrier edge at 7 units), **Pattern D** (≥25 undeclared auxiliary types at signature positions with no declaring carrier; ≥20 consuming units; ≥5 hidden-coupling edges), **Pattern E** (the v2.5 §0.5 deferred `[U-CP-00]` `WorkloadClass` edges, recorded-not-materialized at ~10 consumer bodies).
- `.harness/shared_type_carrier_map.md` (Pipeline Pass T1) — ratified carrier map; CP Pattern-D per-type triage; names candidate carrier unit **U-CP-00b** for the CP-owned auxiliary types.
- `.harness/xal3_resolution_recommendations.md` (Pipeline Pass T2) — 27 of 27 X-AL-3 candidates resolved **FACTOR-OUT** (concept spec-committed; declaration site missing). **Zero design-substrate revision required.** The audit's "Class-1 halt" framing for the CP structured-type cluster and `AuditLedgerEntry` is lifted.
- `Implementation_Plan_Harness_Core_v1_0.md` (R1, applied) — declares **U-CORE-01** in the new `harness-core` plan: `DeploymentSurface`, `PersonaTier`, the 9-alias identity module (`ActionID`/`EntryID`/`WorkflowID`/`StepID`/`ThreadID`/`StageID`/`UnitId`/`ReferenceToUnit`/`ContractID`), and `WorkflowEventClass`/`WorkflowEvent`. R1 §3.3 hands R4 the CP downstream edge list.

R4 is the **fourth of the five-pass carrier-map absorption sequence** (R1 `harness-core` → R2 IS → R3 AS → R4 CP → R5 OD). R4 absorbs the CP materializability audit + the carrier map + the T2 verdicts into a CP plan v2.5 → v2.6 amendment.

### §0.2 Scope of R4

| In scope | Out of scope |
|---|---|
| New CP foundational carrier unit **U-CP-00b** (Pattern C) — full body (§1, §7) | Editing any `design-substrate/` plan (operator applies post-ratification) |
| Pattern C consumer dep-edges — 7 `…AttributeSchema` units + U-CP-01 strip (§1) | U-CORE-01 itself — R1's product, applied; R4 only cites it |
| Pattern D carrier re-pointing — every undeclared type to its ratified carrier (§2) | The IS / AS / OD per-axis edge lists — R2 / R3 / R5 scope |
| Pattern D hidden-coupling edges — the ≥5 missing `Depends on` edges (§2) | Source-code edits to landed units — flagged for retrospective, not done here (HARD WALL) |
| Pattern E — materialize the ~10 `[U-CP-00]` `WorkloadClass` edges in-body (§3) | Re-litigation of the §4A verbatim cluster (off the table at the v2.5/v2.4 body) |
| U-CP-40 declaration-site conversion (`PersonaTier`) (§4) | New H_T design (zero per T2 — every type is a factor-out) |
| U-CP-10 ↔ U-CORE-01 reconciliation (`WorkflowEventClass`) (§5) | |
| Inline-comment-enum promotions (`OverrideKind`/`OverrideScope`/`OutputSchemaKind`/`ParentRelationship`/`ActionKind`/`ReferenceClass`/`KeyRotationState`/`LayerOwner`/`RuntimeFault`) (§2.4) | |
| Retrospective re-check flags for landed U-CP-00/15/19/22 (§6) | |
| Permanent auxiliary-type-audit section added to the CP plan (§11) | |

### §0.3 The CONFORM / FORK distinction (audit-derived)

The Q2 audit verdicts split the affected units into two buckets, and R4 absorbs both — but they differ in whether an operator decision is owed:

- **12 CONFORM** (U-CP-05, 06, 07, 09, 11, 17, 21, 29, 31, 37, 46, 47) — authority-chain-**determinate**. Pure Pattern-C carrier-edge work + Pattern-E deferred-`[U-CP-00]`-edge work. R4's mechanical carrier+edge pass clears these; **no operator decision** on *what*, only ratification of the pass.
- **24 FORK** (U-CP-01, 03, 04, 10, 12, 13, 14, 20, 23, 27, 28, 30, 32, 33, 38, 39, 41, 43, 44, 45, 49, 50, 51, 52) — needs an operator decision **at the audit's snapshot**. But the T2 resolution dissolved the substance of the decision: all 27 X-AL-3 candidates are FACTOR-OUTs, so the Pattern-D carrier placements are now authority-chain-determinate too. What remains genuinely owed to the operator is narrowed to: the U-CP-00b residence call (Q-R4-1), the inline-enum value sets the plan states only in comments (mechanical — promoted here), `ParentRelation`'s value set (Q-R4-3), U-CP-23's `default_pattern` structural mismatch (carried — Q-R4-5), and the two **propagation-gated** units (U-CP-12, U-CP-20 — they FORK only because they transitively depend on U-CP-10; they clear automatically once U-CP-10's reconciliation lands).
- **20 CLEARED** — materializable as written; no R4 action except where a Pattern-E `[U-CP-00]` edge or a hidden-coupling edge touches them.

R4's net effect: after the carrier+edge pass, the 12 CONFORM units clear, the 2 propagation-gated FORKs (U-CP-12, U-CP-20) clear, and the remaining ~22 FORK units clear once their per-type carrier edges (all FACTOR-OUT per T2) are written. The genuine operator surface is the 7 numbered questions at §12.

### §0.4 Sections preserved verbatim (from v2.5)

| Section | Preservation rationale |
|---|---|
| §1 Spec inventory | Substrate versions unchanged at v2.6 (CP spec v1.3/v1.2; ADR-D1 v1.2; ADR-D6 v1.2; ADD v1.3; PRD v1.1) — v2.6 adds the U-CP-00b coverage cell per §10 |
| All 20 CLEARED unit bodies (per §8 list) | No materializability finding; bodies intact except where a Pattern-E / hidden-coupling edge is added (those edge-adds are §3 / §2.5 table rows, not body rewrites) |
| U-CP-00 (landed) | Untouched; U-CP-00b sits beside it at L0 |
| §0 change-notes (v2.1 → v2.5) | Historical; carried |

### §0.5 Sections revised / added (v2.5 → v2.6)

| Section | Shape | Resolves |
|---|---|---|
| **U-CP-00b (NEW)** | New CP foundational unit — declares `AttributeValueType` + `Cardinality` enums; `Implements: (carrier; no spec contract — plan-internal auxiliary types — see §1.3)`; `Depends on: (none)`; L0 | Pattern C |
| **U-CP-01** | Signature delta — strip the inline `enum AttributeValueType` / `enum Cardinality` declarations; add `Depends on: [U-CP-00b]`; `RoutingAttributeSchema` `value_type`/`cardinality` fields now resolve to the U-CP-00b carrier | Pattern C; the `cardinality` field's §1.4-basis question carried as Q-R4-2 |
| **U-CP-07/11/21/31/37/46/47** | `Depends on:` adds `[U-CP-00b]`; signatures otherwise preserved | Pattern C — the 7 sideways `…AttributeSchema` consumers |
| **Pattern E ~10 units** (U-CP-05/06/09/13/17/21/23/29 + tail) | `Depends on:` adds `[U-CP-00]`; `Inputs:` notes `WorkloadClass` enum (U-CP-00); body otherwise preserved | Pattern E — materializes the v2.5 §0.5 recorded-not-materialized edges |
| **Pattern D FORK units** (U-CP-03/04/10/13/14/27/30/33/38/39/41/43/44/49/50/51/52) | `Depends on:` / `Inputs:` deltas re-pointing each undeclared type to its ratified carrier (U-CP-00b / U-CORE-01 / `harness-core` / in-axis CP unit); inline-comment enums promoted to real `enum` declarations | Pattern D |
| **U-CP-40** | Declaration-site conversion — strip the local `PersonaTier` re-declaration; import from `harness-core`; add `Depends on: [U-CORE-01 (cross-axis: core)]` | R1 §3.3 hand-off; carrier-map disposition-1 |
| **U-CP-10** | Declaration-site conversion — strip the local `LifecycleEventClass` enum; re-type `LifecycleEventClassMetadata.class` to `WorkflowEventClass`; add `Depends on: [U-CORE-01 (cross-axis: core)]`; promote `ParentRelation` to a real `enum` | §5 reconciliation; Pattern D (`ParentRelation`) |
| **U-CP-12, U-CP-20** | No body change — propagation-gated FORKs; clear automatically once U-CP-10 conforms (the `LifecycleEventClass` → `WorkflowEventClass` re-type propagates through their cited tokens) | Propagation |
| **§11 (NEW)** | Permanent auxiliary-type-audit section — every CP auxiliary type, its carrier, its consuming units | Audit §4A.4 sub-pass 3(c): "add a §5-style auxiliary-type audit section so the blind spot does not recur" |
| §3 dependency graph | Delta per §9 (U-CP-00b node + Pattern C/D/E edges) | |
| §4 coverage matrix | Delta per §10 (U-CP-00b cell; no contract row dropped) | |

CP-plan unit inventory: 56 → **57** units (U-CP-00b added; U-CP-00 + U-CP-01–U-CP-55 unchanged in count).

### §0.6 v2.5 §0.8 disposition correction (audit §4A.4 item 4)

CP plan v2.5 §0.8 stated the Pattern-E deferred `[U-CP-00]` edges were "a v2.5 plan-internal completeness item, **not a fork**." The Q2 audit's Pattern E finding is that, **at the canonical-current body in force** (resolved through the v2.4/v2.3/v2.2/v2.1 pointer chain), none of the ~10 `WorkloadClass`-consuming units carries `[U-CP-00]` in its `Depends on` line — so for each unit the dependency cone is broken exactly as Tension 003 described, and each is materializability-FORK-blocked until its edge is written. **R4 corrects the v2.5 §0.8 disposition: the Pattern-E edges are materialized in-body at §3 of this revision, not carried as a deferred pointer.** This supersedes v2.5 §0.8's "deferred, not a fork" reading.

### §0.7 Status

`Status: Proposed` per `implementation-planner` SKILL.md §8 — promotion to `Accepted` requires Phase-7 pre-implementation re-clearance. This artifact is a **revision proposal**; the operator ratifies before the v2.6 plan file is written.

### §0.8 Forward-flagged concerns (v2.6)

All v2.5 §0.8 forward-flagged concerns carry unchanged **except** Tension 003's deferred-materialization note (resolved at §3 of this pass). v2.6 adds:
- The U-CP-23 `default_pattern` single-vs-dual structural mismatch (§4A verbatim borderline, fork-queue item 4) — **carried, not resolved by R4** (it is a verbatim-axis item, not a materializability item; surfaced as Q-R4-5).
- The U-CP-01 `cardinality` field §1.4-basis question (fork-queue item 17) — **carried** (Q-R4-2).
- The U-CP-43 `MCP_TRUST` / `DEPLOYMENT_SURFACE` floor spec-silence (fork-queue item 1) — carried from v2.4 §0.8 unchanged.
- The U-CP-15 `CapabilityFloor` Class-3 informational (§6 retrospective; Q-R4-6).

## §1 Pattern C — `AttributeValueType` / `Cardinality` carrier (U-CP-00b)

### §1.1 The defect

`AttributeValueType` and `Cardinality` are declared **only** inside U-CP-01's Signatures fenced block (v2.4-conformed body, lines 175–176):

```
enum AttributeValueType { STRING, INT, FLOAT, BOOL, ENUM_REF }
enum Cardinality { LOW, MEDIUM, HIGH, PER_REQUEST }
```

They are consumed at typed `record` field positions (`.value_type`, `.cardinality`) across **seven other units** that declare a `…AttributeSchema` record — none with a `Depends on` edge to U-CP-01: **U-CP-07** (`Fallback/HarnessBreaker/RetryAttributeSchema`), **U-CP-11** (`LeaseAttributeSchema`), **U-CP-21** (`EngineAttributeSchema`), **U-CP-31** (`Topology/SubAgentAttributeSchema`), **U-CP-37** (`HITLResponseClassAttribute.value_type`), **U-CP-46** (`Audit/Validator/HITLSpanSchema`), **U-CP-47** (`ValidatorFailAttributeSchema`). U-CP-07 is an L0 unit (in-degree 0) — it cannot import the carrier from U-CP-01. `pyright` strict either fails the unresolved name, or — if each unit re-declares the enum locally — treats the seven copies as seven distinct nominal types, breaking the cross-unit `…AttributeSchema` composition U-CP-54's export manifest aggregates. This is the `WorkloadClass`→U-CP-00 / Tension-003 shape.

### §1.2 Resolution — new CP foundational carrier unit U-CP-00b

Per carrier-map disposition 2 (`AttributeValueType`/`Cardinality` are CP-owned — plan-introduced auxiliary enums with plan-invented value sets, **NOT** OTel-SDK types; T2 reaffirmed: "the AS-audit precedent was explicitly OVERRIDDEN for CP, with cause"). The carrier map named the candidate carrier **U-CP-00b**; the Q2 audit §4A.4 sub-pass 1 left the residence as an explicit operator decision (`harness-core` unit vs U-CP-01-as-carrier). R4 **proposes U-CP-00b** — a CP foundational unit beside U-CP-00 at L0 — and surfaces the `harness-core`-vs-U-CP-00b residence as **Q-R4-1**. Rationale for U-CP-00b over `harness-core`: all seven consumers are CP-axis units; no other axis consumes `AttributeValueType`/`Cardinality` (verified against the carrier map — they appear in no IS/AS/OD audit). The carrier-map disposition-1 criterion ("genuinely cross-axis shared primitive") is **not met**; disposition 2 (per-axis-owned, named carrier unit) is the correct placement. `harness-core` residence would mis-state cross-axis sharing that does not exist.

### §1.3 U-CP-00b — full unit body

> On ratification this body is transcribed into `Implementation_Plan_Control_Plane_v2_6.md` §2.0b, beside U-CP-00.

---

#### U-CP-00b — Declare `AttributeValueType` + `Cardinality` schema-attribute utility enums (v2.6 — new CP foundational unit per the Pattern C carrier resolution; relocates the two enums from U-CP-01's inline Signatures block to a reachable carrier)

**Implements:** (carrier unit — no single spec contract). `AttributeValueType` and `Cardinality` are **plan-introduced auxiliary enums**: they are the value-type and cardinality discriminators the CP plan uses to type its `…AttributeSchema` records (the per-namespace attribute-schema records at U-CP-01/07/11/21/31/37/46/47). No CP spec contract enumerates them as named enums — the spec commits the *namespace attribute schemas* (C-CP-01 §1.4, C-CP-03 §3.5, C-CP-07 §7-engine, C-CP-10/11 topology, C-CP-18 §16-HITL, C-CP-20 §20-audit, C-CP-21 §21-validator each commit an attribute table with a "Type" / value-type column and a cardinality characterization), and the plan factors the shared value-type/cardinality vocabulary out of those tables into two enums. Per `implementation-planner` SKILL.md §4.2 a unit must cite a contract by ID and section; a pure carrier unit for a plan-internal factor-out has no single such section. **This unit is traced to the *aggregate* of the seven attribute-schema contracts it serves** — `[C-CP-01 §1.4]`, `[C-CP-03 §3.5]`, `[C-CP-07]`, `[C-CP-10 §10]`, `[C-CP-18 §16]`, `[C-CP-20 §20.4]`, `[C-CP-21 §21.5]` — each of which characterizes attribute value-types and cardinality in prose; the enum value sets (`{STRING,INT,FLOAT,BOOL,ENUM_REF}` / `{LOW,MEDIUM,HIGH,PER_REQUEST}`) are a faithful factor-out of that prose, not a spec extension. (This is the U-CP-00 precedent: U-CP-00 carries `WorkloadClass` against a single contract; U-CP-00b carries a cross-cluster vocabulary against the aggregate. The aggregate-citation form is flagged for operator review at Q-R4-1.)

**Depends on:** (none) — foundational; L0, beside U-CP-00. Imports nothing; the seven `…AttributeSchema` units import it.

**Inputs:** None (foundational; substrate-supplying enum unit — mirrors U-CP-00).

**Files affected:** CP-axis schema-attribute utility enums (logical: `attribute-value-type-enum`, `cardinality-enum`). Residence: `harness-cp` (CP-axis-owned — contrast U-CP-00's `harness-core` residence; see §1.2 rationale).

**Signatures:**

```
enum AttributeValueType {
  STRING,                                             // attribute carries a string value
  INT,                                                // attribute carries an integer value
  FLOAT,                                              // attribute carries a float value
  BOOL,                                               // attribute carries a boolean value
  ENUM_REF                                            // attribute carries a reference into a named enum domain
}
// Closed at cardinality 5. Verbatim relocation of the enum declared at
// U-CP-01 v2.4-conformed body line 175 — no value added, no value dropped.

enum Cardinality {
  LOW,                                                // bounded small domain
  MEDIUM,                                             // bounded moderate domain
  HIGH,                                               // bounded large domain
  PER_REQUEST                                         // unbounded / per-request-distinct
}
// Closed at cardinality 4. Verbatim relocation of the enum declared at
// U-CP-01 v2.4-conformed body line 176 — no value added, no value dropped.
```

**Acceptance criteria:**

1. `AttributeValueType` declares exactly five values `STRING | INT | FLOAT | BOOL | ENUM_REF` — byte-exact with the enum previously declared inline at U-CP-01 (v2.4-conformed body line 175). Closed at cardinality 5. No value added or removed by the relocation.
2. `Cardinality` declares exactly four values `LOW | MEDIUM | HIGH | PER_REQUEST` — byte-exact with the enum previously declared inline at U-CP-01 (v2.4-conformed body line 176). Closed at cardinality 4. No value added or removed.
3. Both enums reside in `harness-cp` and are exposed at the CP-axis package surface so the seven `…AttributeSchema` consuming units (U-CP-01/07/11/21/31/37/46/47) import from one path; `pyright` strict resolves a single nominal type for each across all eight units.
4. No spec extension: the relocation introduces no new value; the value sets are the faithful factor-out the seven attribute-schema contracts characterize in prose.

**Tests:** `test_attribute_value_type_cardinality_five`; `test_attribute_value_type_values_byte_exact_with_relocated_enum`; `test_cardinality_cardinality_four`; `test_cardinality_values_byte_exact_with_relocated_enum`; `test_both_enums_reside_in_harness_cp`; `test_attribute_schema_units_resolve_single_nominal_type` (a `pyright`-strict cross-unit composition check — `U-CP-07.FallbackAttributeSchema.value_type` and `U-CP-46.AuditAttributeSchema.value_type` are the *same* `AttributeValueType`).

**Rollback boundary:** Revert the two enum declarations from `harness-cp`. Downstream impact: the seven `…AttributeSchema` units lose their `value_type`/`cardinality` carrier; Pattern C reopens. If the relocation is reverted *without* restoring the inline U-CP-01 declarations, all eight units fail `pyright`. A single coherent revert.

---

### §1.4 Pattern C consumer dep-edge table

Each unit below adds `Depends on: [U-CP-00b]`; **all other signature content preserved verbatim** from the canonical-current body. These are pure edge-adds — not body rewrites (SKILL.md §8: preserve verbatim what is unaffected). U-CP-01 is the exception — it has a *signature delta* (strip the inline enums).

| Unit | Canonical-current `Depends on` | v2.6 `Depends on` | Change | Audit verdict |
|---|---|---|---|---|
| **U-CP-01** | `(none)` | `[U-CP-00b]` | **Signature delta** — strip inline `enum AttributeValueType` + `enum Cardinality` (lines 175–176); `RoutingAttributeSchema.value_type`/`.cardinality` now resolve to U-CP-00b. Body otherwise preserved (the §1.4 4-attribute `ROUTING_NAMESPACE_SCHEMA` is intact). | FORK → clears |
| **U-CP-07** | `(none)` | `[U-CP-00b]` | Edge-add only. `Fallback/HarnessBreaker/RetryAttributeSchema` `.value_type`/`.cardinality` resolve to U-CP-00b. | CONFORM → clears |
| **U-CP-11** | `(none)` | `[U-CP-00b]` | Edge-add only. `LeaseAttributeSchema` fields resolve. | FORK → clears |
| **U-CP-21** | `[U-CP-15]` | `[U-CP-15, U-CP-00b]` | Edge-add only. `EngineAttributeSchema` fields resolve. | FORK → clears |
| **U-CP-31** | `[U-CP-22, U-CP-15]` | `[U-CP-22, U-CP-15, U-CP-00b]` | Edge-add only. `Topology/SubAgentAttributeSchema` fields resolve. | FORK → clears |
| **U-CP-37** | `(none)` | `[U-CP-00b]` | Edge-add only. `HITLResponseClassAttribute.value_type` resolves. | CONFORM → clears |
| **U-CP-46** | `[U-CP-37,38,42,43,44,45,47]` | `[U-CP-37,38,42,43,44,45,47, U-CP-00b]` | Edge-add only. `Audit/Validator/HITLSpanSchema` fields resolve. | FORK → clears |
| **U-CP-47** | `[U-AS-03]` | `[U-AS-03, U-CP-00b]` | Edge-add only. `ValidatorFailAttributeSchema` fields resolve. | FORK → clears |

> **U-CP-01 strip — signature delta block.** The v2.6 U-CP-01 Signatures block is the v2.4-conformed body **minus** the final two lines:
> ```
> record RoutingAttributeSchema {
>   attribute_name : string
>   value_type     : AttributeValueType      // resolves to U-CP-00b
>   cardinality    : Cardinality             // resolves to U-CP-00b
>   inherited_from : string
> }
> const ROUTING_NAMESPACE_SCHEMA: List<RoutingAttributeSchema>  // exactly 4 entries
> // enum AttributeValueType { ... }   ← REMOVED — relocated to U-CP-00b
> // enum Cardinality { ... }          ← REMOVED — relocated to U-CP-00b
> ```
> U-CP-01's acceptance criteria #1–#4 (the §1.4 4-attribute conformance) and tests are **preserved verbatim**; the v2.6 amendment note records only the enum relocation + the `Depends on: [U-CP-00b]` edge. The `cardinality` field's §1.4-basis question (fork-queue item 17 — CP spec §1.4 routing table columns are `{Attribute, Type, Semantic, Source}`, no Cardinality column) is **carried as Q-R4-2**: R4 does not remove the field (it is plan-added, used uniformly across all seven `…AttributeSchema` records, and the spec defers schema shape to plan discretion) — but the operator should confirm the field is a sanctioned plan-internal characterization.

## §2 Pattern D — undeclared auxiliary-type carriers + hidden-coupling edges

### §2.1 Disposition principle

The Q2 audit Pattern D names ≥25 distinct types at signature positions with no declaring carrier anywhere in the CP plan. The T2 X-AL-3 resolution classified **every** structured type among them as **FACTOR-OUT** (concept spec/ADR-committed; declaration site missing) — so there is **zero design-substrate revision** and zero genuine design extension. R4's Pattern-D work is therefore entirely carrier-placement + dependency-graph completion: re-point each undeclared type to its ratified carrier and write the `Depends on` edge.

Carriers, by category:
- **`harness-core` / U-CORE-01** — the identity aliases + cross-cutting enums R1 placed (`ActionID`, `EntryID`, `WorkflowID`, `StepID`, `ThreadID`, `StageID`, `UnitId`, `ReferenceToUnit`, `ContractID`; `WorkflowEventClass`/`WorkflowEvent`).
- **`harness-core` / U-CP-00** — `WorkloadClass` (landed; Pattern E §3).
- **CP-owned, U-CP-00b** — the structured CP routing/workflow shared types with no natural single-unit home (`AgentRole`, `ModelBinding`, `TraceContext`, `ProviderAgnosticPayload`, `MCPTrustTier`, `Axis`, `TailKeepPredicate`, `ActorIdentity`).
- **CP-owned, in-place at the declaring/first-consuming unit** — the structured types with a natural cluster home (`ProposedAction`, `MaterialDiff`, `HandoffContext`-family, `VerifierResult`, `OverlayResolution`, `WebhookConfig`/`WebhookPayload`, `HITLInvocation`, `LeadAgentPlan`, `FailedAttempt`/`Alternative`/`RetryHistory`, `CurrentState`=`StateSummary`, `RetryPolicy`, `ParentRelation`, `EngineClassPreferences`, `GateOverride`, `CacheWarmupResult`, `RewrittenToolCall`, `SubAgent`, `RoleRoutingBinding`/`WorkloadRoutingOverride`).
- **AS-owned, cross-axis edge** — `MCPServerID`, `ToolName`, `ToolTier` (AS-domain identity / tier vocabulary; CP gets a `(cross-axis: AS)` edge or a `harness-core` alias — see §2.3).
- **inline-comment-enum promotion** — `OverrideKind`, `OverrideScope`, `OutputSchemaKind`, `ParentRelationship`, `ActionKind`, `ReferenceClass`, `KeyRotationState`, `LayerOwner`, `RuntimeFault` (value sets already stated in `// {…}` comments — promote to real `enum` in the declaring unit; §2.4).
- **already in-cone — not a finding** — `RoutingDecisionTrace` (U-CP-05 declares; U-CP-03 consumes — hidden-coupling edge §2.5), `ExternalReference` (U-CP-30 declares; U-CP-50 consumes — hidden-coupling), `MerkleRoot` (U-CP-35 self-declared), `F1/D1/D4LayerState` (U-CP-53 self-declared).

### §2.2 Pattern D carrier re-pointing table — `harness-core` / U-CP-00b carrier

Per the carrier-map CP Pattern-D per-type table + the T2 resolution table. Each row: the consuming CP unit adds the named `Depends on` edge; the type resolves at the carrier. Bodies otherwise preserved.

| Type | Consuming CP unit(s) | Carrier (ratified) | Edge added to consumer | T2 verdict |
|---|---|---|---|---|
| `ActionID` | U-CP-27, U-CP-30, U-CP-34*, U-CP-35* | `harness-core` U-CORE-01 | `[U-CORE-01 (cross-axis: core)]` | FACTOR-OUT (decided) — C-IS-05 §5 |
| `EntryID` | U-CP-38, U-CP-49, U-CP-52 | `harness-core` U-CORE-01 | `[U-CORE-01 (cross-axis: core)]` | FACTOR-OUT (decided) |
| `WorkflowID` | U-CP-49, U-CP-50, U-CP-51, U-CP-52 | `harness-core` U-CORE-01 | `[U-CORE-01 (cross-axis: core)]` | FACTOR-OUT (decided) — C-CP-05 §5 |
| `StepID` | U-CP-13, U-CP-14 | `harness-core` U-CORE-01 | `[U-CORE-01 (cross-axis: core)]` | FACTOR-OUT (decided) — C-CP-05 §5 |
| `ThreadID` | (CP F2-keying tuple consumers) | `harness-core` U-CORE-01 | `[U-CORE-01 (cross-axis: core)]` | FACTOR-OUT (decided) |
| `StageID` | U-CP-29 | `harness-core` U-CORE-01 | `[U-CORE-01 (cross-axis: core)]` | FACTOR-OUT (proposing) — C-CP-13 §13.4 |
| `ReferenceToUnit` | U-CP-41 | `harness-core` U-CORE-01 | `[U-CORE-01 (cross-axis: core)]` | plan-internal (Q-R1-5 ratified) |
| `ActorIdentity` | U-CP-14, U-CP-27, U-CP-30, U-CP-49 | **U-CP-00b** (CP-owned identity alias) | `[U-CP-00b]` | FACTOR-OUT (proposing) — carrier-map "`ActorIdentity` vs IS `Actor`" note; see §2.2.1 |
| `AgentRole` | U-CP-03, U-CP-04, U-CP-09, U-CP-27, U-CP-29 | **U-CP-00b** | `[U-CP-00b]` | FACTOR-OUT (proposing) — C-CP-13 §13.4 per-role contract |
| `ModelBinding` | U-CP-13, U-CP-14, U-CP-29, U-CP-50 | **U-CP-00b** | `[U-CP-00b]` | FACTOR-OUT (proposing) — ADR-F1 v1.2 + C-CP-13 §13.4 |
| `TraceContext` | U-CP-03 | **U-CP-00b** | `[U-CP-00b]` | FACTOR-OUT (proposing) — OTel W3C Trace Context (stack adoption) + CP §8 |
| `ProviderAgnosticPayload` | U-CP-03 | **U-CP-00b** | `[U-CP-00b]` | FACTOR-OUT (proposing) — ADR-F1 v1.2 + C-CP-01/02 |
| `MCPTrustTier` | U-CP-43, U-CP-45 | **U-CP-00b** | `[U-CP-00b]` | FACTOR-OUT (proposing) — C-CP-43 gate-level; carrier-map disposition 2 |
| `Axis` | U-CP-43 | **U-CP-00b** | `[U-CP-00b]` | FACTOR-OUT (proposing) — the 5-axis gate enum; plan-introduced CP-owned |
| `TailKeepPredicate` | U-CP-32, U-CP-51 | **U-CP-00b** | `[U-CP-00b]` | FACTOR-OUT (proposing) — CP §51 tail-keep; carrier-map disposition 2 |

\* U-CP-34 / U-CP-35: per audit Findings-rejected #9, at these two units `actor`/`action_id` resolve to the **IS-exported** `Actor`/F2 entry shape via the *already-declared* `(cross-axis: IS)` edge — they are the F2 six-field shape, NOT the U-CORE-01 alias. **No edge change at U-CP-34/35.** They appear in the `ActionID` row only for completeness; their resolution is the cross-axis F2 shape, already in-cone.

> **§2.2.1 — `ActorIdentity` placement note.** The carrier-map "Note on `ActorIdentity` vs IS `Actor`" recommends a `harness-core` identity-alias placement OR a CP carrier. R1's U-CORE-01 identity-alias module does **not** include `ActorIdentity` (R1 §2 lists exactly nine aliases; `ActorIdentity` is not among them). R4 therefore places `ActorIdentity` on **U-CP-00b** as a CP-owned identity alias (consistent with U-CP-00b carrying the CP-owned structured shared types). This is **proposing** — if the operator prefers `ActorIdentity` join U-CORE-01 as a 10th `harness-core` alias, that is an R1-reopen (U-CORE-01 amendment), surfaced as **Q-R4-7**.

### §2.3 Pattern D — AS-owned types consumed by CP (cross-axis edges)

Per carrier-map CP Pattern-D table, three types are AS-domain identity/tier vocabulary, not CP-owned:

| Type | Consuming CP unit(s) | Carrier | Edge | Note |
|---|---|---|---|---|
| `MCPServerID` | U-CP-39 | AS (MCP integration §; U-AS-33 export) — OR `harness-core` identity alias | `[U-AS-33 (cross-axis: AS)]` (proposing) | AS-domain MCP identity. R3 (AS pass) confirms the AS export carrier. |
| `ToolName` | U-CP-04, U-CP-39 | AS (tool-contract identity) — OR `harness-core` alias | `[U-AS-03 (cross-axis: AS)]` (proposing) | AS tool-contract identity. R3 confirms. |
| `ToolTier` | U-CP-41 | AS (`SandboxTier`/`BlastRadiusTier` family, U-AS-01 — already a declared CP cross-axis dep at U-CP-26) | `[U-AS-01 (cross-axis: AS)]` (proposing) | Likely the AS blast-radius tier vocabulary. R3 confirms. |

> **§2.3.1 — cross-axis ordering caveat (Q-R4-4).** CP consumes from AS (CXA §2.4 topological order IS < AS < CP < OD — CP→AS edges are sanctioned, 24 of them per CXA §2.3.4). But `MCPServerID`/`ToolName` are **thin identity aliases**, not structured AS exports — the carrier-map flags them as candidates for the `harness-core` identity-alias module instead (where `ContractID` already lives, serving "tool/routing contract identifier — C-AS-03 / C-CP-01"). R4 surfaces **Q-R4-4**: place `MCPServerID`/`ToolName` as (a) AS-owned types with CP cross-axis edges, or (b) `harness-core` identity aliases (R1-reopen — U-CORE-01 amendment). R4 default: **proposing (a)** — keep AS-domain identity in AS; but `ToolName` overlaps `ContractID`'s domain, so the operator should rule. This is coordinated with the R3 (AS) pass.

### §2.4 Pattern D — inline-comment-enum promotions

Nine enums are declared in CP unit Signatures blocks only as `// {…}` comments, not as real `enum` declarations. The value sets are **already stated** in the plan comments — promotion is mechanical (audit §4A.4 sub-pass 3(b); carrier-map disposition "Decided"). Each promotion is a **signature delta** at the declaring unit: replace the `// {…}` comment with a real `enum`. No value invented.

| Enum | Declaring unit | Value set (from the existing `// {…}` comment) | Consumed by |
|---|---|---|---|
| `OutputSchemaKind` | U-CP-28 | `{ JSON_SCHEMA, … }` (per the U-CP-28 `OutputSchema.schema_kind` comment) | U-CP-28 |
| `ParentRelationship` | U-CP-32 | `{ ROOT, CHILD_OF, SIBLING_OF }` | U-CP-32 (`SpanHierarchyNode.parent_relationship`) |
| `OverrideKind` | U-CP-45 | `{ … }` (per the U-CP-45 `OperatorPolicyOverride.override_kind` comment) | U-CP-45, U-CP-46 (acc text) |
| `OverrideScope` | U-CP-45 | `{ … }` (per the U-CP-45 `OperatorPolicyOverride.scope` comment) | U-CP-45, U-CP-46 (acc text) |
| `ActionKind` | U-CP-30 | `{ … }` (per the U-CP-30 `ProposedAction` comment) | U-CP-30 |
| `ReferenceClass` | U-CP-30 | `{ … }` (per the U-CP-30 `ExternalReference` comment) | U-CP-30 |
| `KeyRotationState` | U-CP-44 | `{ … }` (per the U-CP-44 `SigningKey…` comment) | U-CP-44 |
| `LayerOwner` | U-CP-53 | `{ … }` (per the U-CP-53 comment) | U-CP-53 |
| `RuntimeFault` | U-CP-53 | `{ … }` (per the U-CP-53 comment) | U-CP-53 |

> **Materialization discipline.** R4's promotion transcribes the value set **exactly as the existing comment states it**. Where the comment uses an ellipsis (`{ JSON_SCHEMA, … }`), the operator/executor must complete the value set against the declaring unit's cited spec section at landing — R4 cannot invent the elided values. This is flagged: the four ellipsis-bearing comments (`OutputSchemaKind`, `OverrideKind`, `OverrideScope`, `ActionKind`, `ReferenceClass`, `KeyRotationState`, `LayerOwner`, `RuntimeFault` — those whose `// {…}` the plan body does not fully spell) need a value-set completion check at the v2.6 transcription. `ParentRelationship` is the one fully-enumerated comment (`{ROOT, CHILD_OF, SIBLING_OF}`) — promoted directly. Surfaced as a sub-item of **Q-R4-3** (the operator confirms the value-set completion for the ellipsis enums alongside `ParentRelation`).

### §2.5 Pattern D — structured-type in-place carriers + hidden-coupling edges

Per T2: every structured type below is a **FACTOR-OUT** with a CP-owned carrier at a natural cluster unit. R4 declares the carrier as a `record` in the named unit's Signatures block and adds the `Depends on` edge from each consumer. Most of these types are **already self-declared at the named unit** (the audit confirmed `ProposedAction` self-declared at U-CP-30, `RoutingDecisionTrace` at U-CP-05, `ExternalReference` at U-CP-30, `MerkleRoot` at U-CP-35) — for those the defect is purely the missing consumer edge (hidden coupling). For the genuinely undeclared structured types, the carrier `record` is declared at the cluster unit per the T2 carrier column.

| Type | Carrier unit (T2) | Status | Consumer units needing the edge |
|---|---|---|---|
| `HandoffContext`-family (`HandoffContext`, `StateSummary`, `LedgerEntryRef`) | U-CP-30 (self-declares per audit) | Decided (ADR-D4 v1.1 names `HandoffContext`) | U-CP-13, U-CP-14, U-CP-27, U-CP-38 — see hidden-coupling table |
| `ProposedAction` | U-CP-30 (self-declares per audit) | proposing — CP §16/§17 | U-CP-30 internal |
| `FailedAttempt` / `Alternative` / `RetryHistory` | U-CP-30 | Decided — CP §13.4 names `RetryHistory` | U-CP-30 internal |
| `CurrentState` (= spec `StateSummary`) | U-CP-30 / U-CP-22-context-revalidation | proposing — spelling unification to `StateSummary` (verbatim-pass item) | U-CP-30, U-CP-50 |
| `MaterialDiff` / `DiffEntry` | U-CP-50 (self-declares) | Decided — CP §22 names "material-diff detection" | U-CP-50 internal |
| `RetryPolicy` | U-CP-04 | proposing — CP §3.5 `retry.*` | U-CP-04 internal |
| `RoleRoutingBinding` / `WorkloadRoutingOverride` | U-CP-04 | proposing — CP §3 routing-manifest | U-CP-04 internal |
| `VerifierResult` / `OverlayResolution` | U-CP-41 | proposing — CP §18.3/§18.4 | U-CP-41 internal |
| `WebhookConfig` / `WebhookPayload` | U-CP-52 | proposing — CP §18 webhook ingress | U-CP-52 internal |
| `HITLInvocation` | U-CP-17 (HITL primitive unit) | proposing — CP §17 | U-CP-52 — cross-cluster edge `[U-CP-17]` |
| `LeadAgentPlan` / `SubAgent` / `CacheWarmupResult` | U-CP-33 | proposing — ADR-D4 v1.1 cache-warmup | U-CP-33 internal |
| `EngineClassPreferences` | U-CP-27 (or U-CP-15 family) | proposing — CP §7.4 engine content | U-CP-27 internal |
| `GateOverride` | U-CP-27 (or U-CP-43 family) | proposing — CP gate-level | U-CP-27 internal |
| `RewrittenToolCall` | U-CP-39 | proposing — function return type | U-CP-39 internal |
| `ParentRelation` | U-CP-10 | proposing — see §5; value set Q-R4-3 | U-CP-10 internal |
| `AuditLedgerEntry` | U-CP-14 (CP-spec-owned per T2; composes against IS `StateLedgerEntry`) | Decided — CP §16.2 (C-CP-16) commits the per-response audit-ledger entry shape directly; **CP→OD foreclosed-direction halt is LIFTED** | U-CP-14 (self-declares), U-CP-27, U-CP-44 — see hidden-coupling |

> **`AuditLedgerEntry` — Class-1 halt lifted.** The Q2 audit flagged `AuditLedgerEntry` as a Class-1 halt (foreclosed CP→OD direction). T2 resolved: CP spec §16.2 (C-CP-16) commits the per-response audit-ledger entry shape **directly inside the CP spec**, and §20 (C-CP-20) the per-persona-tier cryptographic shape. `AuditLedgerEntry` is **CP-spec-owned** (carrier at U-CP-14), composing against the IS-exported `StateLedgerEntry` shape via the *already-declared* CP→IS edges. It is **not** OD's `AuditLedger`/`AuditPayload` (a parallel OD-local sibling family). **No CP→OD edge; the CXA matrix CP→OD = 0 is intact; no CXA revision.** R4 declares the `AuditLedgerEntry` `record` carrier at U-CP-14 and adds the consumer edges.

### §2.6 Hidden-coupling edges (audit Findings-considered #8 — ≥5 confirmed)

The audit confirmed ≥5 units consume a sibling unit's type without declaring the `Depends on` edge. R4 adds each:

| Consumer | Consumed type | Declaring (carrier) unit | Edge added |
|---|---|---|---|
| U-CP-13 | `SubAgentBrief` | U-CP-28 | `[U-CP-28]` |
| U-CP-14 | `LedgerEntryRef` | U-CP-30 | `[U-CP-30]` |
| U-CP-17 | `PersonaTier` | U-CP-40 (→ post-§4, `harness-core` U-CORE-01) | `[U-CORE-01 (cross-axis: core)]` (see §4) |
| U-CP-27 | `SubAgentBrief` | U-CP-28 | `[U-CP-28]` |
| U-CP-39 | `SynchronyClass` | U-CP-40 | `[U-CP-40]` |
| U-CP-03 | `RoutingDecisionTrace` | U-CP-05 | `[U-CP-05]` — *forward edge; see acyclicity note §9* |
| U-CP-50 | `ExternalReference` | U-CP-30 | `[U-CP-30]` |
| U-CP-27 | `AuditLedgerEntry` | U-CP-14 | `[U-CP-14]` |
| U-CP-44 | `AuditLedgerEntry` | U-CP-14 | `[U-CP-14]` |

> **U-CP-03 → U-CP-05 forward-edge note.** U-CP-03 consumes `RoutingDecisionTrace`, declared at U-CP-05. Per the v2.1 §3.2 topology U-CP-03 is L0 and U-CP-05 is L2 — adding `U-CP-03 → U-CP-05` would invert the level order. The audit (Findings #8) names this hidden coupling but the carrier-map row marks `RoutingDecisionTrace` as **"hidden-coupling — dep-graph completion, not a new carrier"**. R4 surfaces this as part of **Q-R4-5** (the U-CP-03/U-CP-05 ordering): either (a) `RoutingDecisionTrace` is re-homed to a unit upstream of U-CP-03 (a foundational routing-types unit, or U-CP-00b), or (b) U-CP-03 and U-CP-05 are re-atomized so the trace type is declared before it is consumed. R4 default: **proposing (a)** — re-home `RoutingDecisionTrace` to U-CP-00b alongside the other structured routing shared types (`TraceContext`, `ProviderAgnosticPayload` already there). This keeps the DAG acyclic and level-ordered; the operator confirms at Q-R4-5.

## §3 Pattern E — materialize the `[U-CP-00]` `WorkloadClass` edges

### §3.1 The defect

CP plan v2.5 §0.5 records that ~10 `WorkloadClass`-consuming units gain a `[U-CP-00]` dependency edge — but their bodies are `[preserved verbatim]` pointers, and v2.5 §0.5 deferred the edge: "the edge is recorded here and is materialized at each unit's next full-revision." v2.5 §0.8 called this "a v2.5 plan-internal completeness item, not a fork." The Q2 audit Pattern E finding (and §4A.4 item 4) corrects this: **at the canonical-current body in force, none of the ~10 units carries `[U-CP-00]` in its `Depends on` line** (only U-CP-22 had its body re-revised at v2.5 to carry the edge). The dependency cone is broken exactly as Tension 003 described. **R4 materializes the recorded edges in-body** — this is the §0.6 v2.5 §0.8 disposition correction.

### §3.2 Pattern E edge-materialization table

Each unit below adds `[U-CP-00]` to its `Depends on` line and an `Inputs:` note that `WorkloadClass` (U-CP-00) is consumed. **All other body content preserved verbatim** — this is the v2.5 §0.5 / U-CP-22 amendment shape, scaled to the full set. No body rewrite.

| Unit | `WorkloadClass` consumption site | Canonical-current `Depends on` | v2.6 `Depends on` (Pattern E delta) | Audit verdict |
|---|---|---|---|---|
| **U-CP-05** | `InferenceRequest` (symbolic, via routing layer) | `[U-CP-03]` (per v2.1 body) | `[U-CP-03, U-CP-00]` | CONFORM → clears |
| **U-CP-06** | `LayerBudget` keyed by workload class | `[U-CP-05]` | `[U-CP-05, U-CP-00]` | CONFORM → clears |
| **U-CP-09** | `compose_fallback_chain` (workload param) | `[U-CP-07, U-CP-08]` (per v2.1) | `[U-CP-07, U-CP-08, U-CP-00]` | CONFORM → clears |
| **U-CP-13** | `WorkflowManifestEntry.workload_class` | `[U-CP-04, U-CP-06, U-CP-09, U-CP-15, U-CP-22, U-CP-38]` | `+ U-CP-00` (and `+ U-CP-28` hidden-coupling §2.6; `+ U-CORE-01` for `StepID`/`ModelBinding` §2.2) | FORK → clears |
| **U-CP-17** | `WorkloadBindingSelectionInput.workload_class` | `[U-CP-16]` (per v2.1) | `+ U-CP-00` (and `+ U-CORE-01` for `DeploymentSurface`/`PersonaTier` §2.6/§4) | CONFORM → clears |
| **U-CP-21** | `EngineAttributeSchema` (workload-keyed) | `[U-CP-15]` → `[U-CP-15, U-CP-00b]` (§1.4) | `+ U-CP-00` | FORK → clears |
| **U-CP-23** | `PerWorkloadClassTopologyCommitment.workload_class` | `[U-CP-22]` (per v2.4) | `[U-CP-22, U-CP-00]` | FORK → clears (the `default_pattern` mismatch is a *separate* carry — Q-R4-5) |
| **U-CP-25** | `WorkloadEngineMatrixCell` (workload-keyed) | `[U-CP-22, U-CP-24]` (per v2.1) | `[U-CP-22, U-CP-24, U-CP-00]` | CLEARED → edge-add only |
| **U-CP-29** | `BriefAuthoringInheritance` (workload-keyed) | `[U-CP-28]` (per v2.1) | `+ U-CP-00` (and `+ U-CORE-01` for `StageID` §2.2; `+ U-CP-00b` for `AgentRole`/`ModelBinding`) | CONFORM → clears |
| **U-CP-53** | `T-perm-3` composition (workload-keyed) | (per v2.1 multi-dep) | `+ U-CP-00` | CLEARED → edge-add only |

> **Unit-set caveat.** v2.5 §0.5 names "U-CP-05, U-CP-06, U-CP-09, U-CP-13, U-CP-17, U-CP-21, U-CP-23, and others"; the exact tail is *proposing* — R4 derives the full set above from the audit's per-unit findings table (`WorkloadClass` consumption noted at U-CP-05/06/09/13/17/21/23/25/29/53). The R4 transcription into v2.6 must verify each unit's body against the landed source for any `WorkloadClass` consumption the audit's table did not surface. **U-CP-22 is NOT in this table** — its `[U-CP-00]` edge was already materialized at v2.5. Surfaced as part of the standard transcription-verification step, not a separate operator question.

---

## §4 U-CP-40 declaration-site conversion (`PersonaTier`)

### §4.1 The defect

U-CP-40 (`Declare persona-tier × engine-class 2D matrix + cell exclusion inheritance`) **currently re-declares `PersonaTier` itself** in its Signatures block (carrier-map "already-declared" table: "`PersonaTier` re-declared at OD U-OD-01 **and CP U-CP-40**"; audit U-CP-40 verdict: "`PersonaTier`/`SynchronyClass`/`HITLPrimitiveShape`/`HITLMatrixCell` all self-declared"). After R1, `PersonaTier` resides in `harness-core` (U-CORE-01). U-CP-40's local declaration is now a duplicate — `pyright` strict treats the U-CP-40 `PersonaTier` and the `harness-core` `PersonaTier` as two distinct nominal types, breaking every cross-unit composition that mixes them (U-CP-17/25/36/50 consume `PersonaTier`; if some resolve to U-CP-40's copy and some to `harness-core`'s, the matrix composition fails).

### §4.2 The conversion

R4 converts U-CP-40 from a **declaring** site to a **consuming** site for `PersonaTier`. **Signature delta** at U-CP-40:

```
// REMOVED — PersonaTier now resides in harness-core (U-CORE-01); U-CP-40 imports it.
// enum PersonaTier { SOLO_DEVELOPER, TEAM_BINDING, MULTI_TENANT_COMPLIANCE }   ← strip

// PRESERVED — SynchronyClass, HITLPrimitiveShape, HITLMatrixCell stay U-CP-40-owned
// (no other axis declares them; carrier-map disposition: in-axis self-declared, clean).
enum SynchronyClass { ... }                  // preserved verbatim
enum HITLPrimitiveShape { ... }              // preserved verbatim
record HITLMatrixCell { ... }                // preserved verbatim — persona_tier field re-types to harness-core PersonaTier
```

- `Depends on:` adds `[U-CORE-01 (cross-axis: core)]`.
- `Inputs:` adds `PersonaTier` enum (U-CORE-01).
- The `HITLMatrixCell.persona_tier` field (and any other `PersonaTier`-typed field) re-resolves to the `harness-core` enum — no field added/removed.
- Acceptance criteria: the U-CP-40 acceptance criterion that asserted `PersonaTier` 3-value cardinality is **struck** (that assertion now lives at U-CORE-01 acc #2); a new acceptance criterion is added: "U-CP-40 imports `PersonaTier` from `harness-core`; the persona-tier × engine-class matrix composes against the single `harness-core` nominal type." The `SynchronyClass`/`HITLPrimitiveShape`/`HITLMatrixCell`/matrix-exclusion-inheritance acceptance criteria are **preserved verbatim**.

This mirrors the R1 §3.3 hand-off ("R4 also converts U-CP-40 from a `PersonaTier` re-declaring site to a consuming site") and the R3-precedent U-AS-04 / R5-precedent U-OD-01 conversions. `MCPTransport` is **not** a U-CP-40 concern (it is the U-AS-04 / R3 surface).

> **Retrospective note — U-CP-40 landed?** U-CP-40 is **not** in the landed set (landed: U-CP-00/15/19/22 per audit §4A.6 + `.harness` memory). The conversion is a forward plan edit; no source re-point owed. The hidden-coupling consumers U-CP-17 (§2.6) and U-CP-39 (§2.6) take their `PersonaTier` / `SynchronyClass` edges per the §2.6 table.

---

## §5 U-CP-10 ↔ U-CORE-01 reconciliation (R1-flagged)

### §5.1 The defect — duplicate declaration of the C-CP-05 §5.1 taxonomy

R1 (`revision_R1_harness_core.md` §2) and `Implementation_Plan_Harness_Core_v1_0.md` §2 (the "`WorkflowEvent` ↔ U-CP-10 reconciliation" note) explicitly hand R4 this item:

- **U-CP-10** (LANDED — `.harness` memory operational-minimum set) declares `enum LifecycleEventClass { WORKFLOW_START, STEP_BOUNDARY, FALLBACK_TRIGGER, RETRY_ATTEMPT, BREAKER_TRIP, LEASE_ACQUIRED, LEASE_RELEASED, RESUMPTION }` — the C-CP-05 §5.1 8-class taxonomy (v2.4-conformed body lines 213–222).
- **U-CORE-01** (R1, applied) declares `enum WorkflowEventClass { WORKFLOW_START, STEP_BOUNDARY, FALLBACK_TRIGGER, RETRY_ATTEMPT, BREAKER_TRIP, LEASE_ACQUIRED, LEASE_RELEASED, RESUMPTION }` — the **same** C-CP-05 §5.1 8-class taxonomy (`Implementation_Plan_Harness_Core_v1_0.md` §2 lines 105–114), plus a `WorkflowEvent` payload model carrying the §5.2 attribute set.

These are the **same spec taxonomy declared twice under two names** — the exact multi-declaration defect the carrier map exists to eliminate. `pyright` strict sees `LifecycleEventClass` and `WorkflowEventClass` as two distinct nominal types; any composition site that mixes a U-CP-10-typed value with a U-CORE-01-typed value fails.

### §5.2 R4 recommendation — *proposing*

**Decided / proposing / open vocabulary:**

- **proposing — name survival.** `WorkflowEventClass` (the U-CORE-01 spelling) survives; `LifecycleEventClass` is retired. Rationale: U-CORE-01 is the ratified `harness-core` carrier (R1 applied, operator-ratified Q-R1-2 including `WorkflowEvent`); `harness-core` is the cross-cutting carrier home per `CLAUDE.md` §3.3; the type is consumed cross-axis (IS U-IS-14 `on_workflow_event` per R1 §3.1) so it *must* be the `harness-core` type. Keeping `LifecycleEventClass` as the survivor would force `harness-core` to import from CP — inverting the `harness-core` → CP topological order. **R1 explicitly preserved the operator's right to rule on the name** (`Implementation_Plan_Harness_Core_v1_0.md` §2: "or the operator rules on which name survives"); R4 surfaces this as **Q-R4-2's companion, recorded at Q-R4-7's sibling — see §12 Q-R4-… No: surfaced as Q-R4-2-adjacent → carried explicitly as Q-R4-7**. *(See §12: the name-survival ruling is Q-R4-7.)*
- **proposing — U-CP-10 conversion to consuming site.** U-CP-10 is converted from a **declaring** site to a **consuming** site for the lifecycle-event taxonomy. **Signature delta** at U-CP-10:

  ```
  // REMOVED — the 8-class taxonomy now resides in harness-core (U-CORE-01) as WorkflowEventClass.
  // enum LifecycleEventClass { WORKFLOW_START, ... RESUMPTION }   ← strip

  // PRESERVED + RE-TYPED — the span-name map record is U-CP-10-owned (the C-CP-05 §5.1
  // "Span name" column is CP-spec content; harness-core carries only the event-class enum,
  // not the OTel span-name map). The `class` field re-types to the harness-core enum.
  record LifecycleEventClassMetadata {
    class            : WorkflowEventClass        // re-typed from LifecycleEventClass; resolves to U-CORE-01
    span_name        : string                   // canonical OTel span name — preserved
    parent_relation  : ParentRelation            // PROMOTED to a real enum — see §5.3
  }
  const LIFECYCLE_EVENT_CLASS_METADATA: List<LifecycleEventClassMetadata>  // exactly 8 entries — preserved
  ```

  - `Depends on:` `(none)` → `[U-CORE-01 (cross-axis: core)]`.
  - `Inputs:` `None` → `WorkflowEventClass` enum (U-CORE-01).
  - U-CP-10 acceptance criterion #1 (the 8-class verbatim enumeration) is **struck** — that assertion now lives at U-CORE-01 acc #4. Criteria #2 (the span-name map — `WORKFLOW_START → workflow.start` etc.), #3 (closed at cardinality 8), #4 (D6 ingestion delegation) are **preserved verbatim**; #2/#3 re-anchored to `WorkflowEventClass`.
  - `Implements:` `[C-CP-05 §5.1]` preserved — U-CP-10 still covers the §5.1 *span-name map*; U-CORE-01 covers the §5.1 *event-class enum*. Multi-unit coverage of one contract (SKILL.md §4.2 permits) — and the `Implementation_Plan_Harness_Core_v1_0.md` §4 coverage matrix already notes "C-CP-05 §5.1, §5.2 … Multi-unit — R4 reconciles with U-CP-10."

- **decided — `WorkflowEvent` payload model home.** The `WorkflowEvent` *payload model* (§5.2 per-class attribute set) resides at U-CORE-01 (R1, applied — operator-ratified Q-R1-2). U-CP-10 does **not** re-declare it. No R4 action; recorded for completeness.

### §5.3 `ParentRelation` — U-CP-10's separate Pattern D fork (carried)

U-CP-10's `LifecycleEventClassMetadata.parent_relation : ParentRelation` consumes `ParentRelation`, declared by no unit and with no §5.1 basis (Q2 audit U-CP-10 verdict; fork-queue item 16). T2 resolved `ParentRelation` as **FACTOR-OUT, CP-owned, carrier at U-CP-10** (the topology unit) — CP §10 (C-CP-10) six-pattern topology commits `decentralized-handoff` / `hierarchical-delegation` parent-ownership semantics; ADR-D4 v1.1 commits the sub-agent privilege-inheritance parent contract. R4 **promotes `ParentRelation` to a real `enum` in U-CP-10's Signatures block**:

```
enum ParentRelation {
  ROOT,                                               // event has no parent span (workflow-root event)
  CHILD_OF,                                           // event is a child span of its workflow parent
  DELEGATED_TO                                        // event is a delegated sub-agent span (hierarchical-delegation / decentralized-handoff)
}
```

> **proposing — value set.** The 3-value set above is R4's *proposed* operationalization of the ADR-D4 v1.1 parent-ownership semantics. **Neither CP spec §5.1 nor ADR-D4 enumerates a named `ParentRelation` value set** — the value set is a faithful factor-out of the parent-relation *concept* T2 confirmed is spec-committed, but the *exact members* are R4's proposal. Surfaced as **Q-R4-3** (the operator confirms the `ParentRelation` value set, alongside the §2.4 ellipsis-enum value-set completions). Alternative the operator may select: drop the `parent_relation` field from `LifecycleEventClassMetadata` entirely if the operator rules it has no §5.1 basis (audit §4A.7 item 4 explicitly offers "carrier + value set, **or drop the field**").

### §5.4 Retrospective implication for the landed U-CP-10

**U-CP-10 is LANDED.** The §5.2 conversion is a **source-vs-plan reconciliation** item, not a fresh implementation (R1 §4 "Discipline flag"). The landed U-CP-10 source currently:
- declares a local `LifecycleEventClass` enum — must be **re-pointed** to import `WorkflowEventClass` from `harness-core`;
- consumes `ParentRelation` — the landed source either inlined a placeholder or used `Any`/`str` (it could not have a real carrier — none existed); must be re-pointed to the promoted U-CP-10 `enum ParentRelation`.

R4 **does not touch source** (HARD WALL). R4 flags: when v2.6 is ratified and applied, the landed U-CP-10 source MUST be re-inspected and re-pointed, and the re-point recorded in the v2.6 application change-note. The two propagation-gated FORK units **U-CP-12** and **U-CP-20** (which transitively depend on U-CP-10's enum) clear automatically once U-CP-10's `class`-field re-type lands — their bodies cite `LifecycleEventClass` value tokens; the v2.6 transcription re-anchors those token citations to `WorkflowEventClass` (a cross-unit propagation, the U-CP-12 v2.4-amendment shape). This is surfaced as **Q-R4-7** (name-survival ruling) — once the operator rules the name, the U-CP-12/U-CP-20 token re-anchor is mechanical.

---

## §6 Retrospective — landed units

Four CP units are **landed** (Phase 7 7b operational-minimum set, per audit §4A.6 + `.harness` memory): **U-CP-00, U-CP-15, U-CP-19, U-CP-22**. R4 carries the following retrospective items — R4 does **not** revise landed units' bodies for materializability (they cleared the audit); it records the re-check obligations and the one flagged informational.

| Landed unit | Audit verdict | Retrospective item | Disposition |
|---|---|---|---|
| **U-CP-00** | CLEARED | `WorkloadClass` carrier — clean. U-CP-00b sits beside it at L0 (no interaction). | No action — decided clean. |
| **U-CP-22** | CLEARED (retrospective: clean) | The one CP unit whose v2.5 body materialized the `[U-CP-00]` `WorkloadClass` edge in-body. Not in the Pattern E table (§3.2). | No action — decided clean. |
| **U-CP-19** | CLEARED | `ResumptionKind`/`ResumptionKindBinding` self-declared; consumes `EngineClass` (U-CP-15 in-cone). | No action — decided clean. |
| **U-CP-15** | CLEARED (retrospective concern) | `CapabilityFloor` self-declared with field set (`capability_name`, `required_at_class`, `rationale`); acceptance #4 claims "per §7.4" — but the §7.4 basis for the *field set* is thin. Audit logged this as a **§2.7.6 Class 3 informational, non-blocking** (a `CapabilityFloor` "per §7.4" claim). | **open — Q-R4-6.** Carried as a flagged retrospective item: is U-CP-15's `CapabilityFloor` field set accepted as a faithful factor-out of §7.4 prose (no action — landed unit stands), or does the operator want the §7.4 basis amplified (a verbatim-axis / spec re-check, NOT an R4 materializability item)? R4 default: accept as faithful factor-out; the field set is a reasonable operationalization of §7.4 capability-floor prose. Non-blocking; does not gate any landing. |

> **U-CP-10 is also landed** but its retrospective item is the §5.4 source-vs-plan reconciliation (the `LifecycleEventClass` → `WorkflowEventClass` re-point + the `ParentRelation` carrier re-point) — recorded at §5.4, not duplicated here. U-CP-10's audit verdict was **FORK** (not CLEARED) — it is a substantively-revised unit (§5), distinct from the four CLEARED-landed units above.

## §7 Revised unit bodies

### §7.1 Body-revision classification (SKILL.md §8 discipline)

Per `implementation-planner` SKILL.md §8, R4 produces **full revised bodies only where signatures actually change** and **preserved-verbatim pointers + amendment notes** where a unit's only change is a `Depends on:` / `Inputs:` line. A unit whose sole delta is an edge-add is **not** a revised body — it is a v2.6 amendment-note line (the v2.5 / U-CP-22 precedent). The 57 units split:

| Class | Treatment | Units |
|---|---|---|
| **A — new unit, full body** | Full body filed in this proposal | **U-CP-00b** (§1.3) |
| **B — signature delta** (declaration stripped, field re-typed, or inline-enum promoted) | Signature delta block filed in this proposal; rest preserved | **U-CP-01** (§1.4 strip), **U-CP-10** (§5.2 + §5.3), **U-CP-40** (§4.2), **U-CP-28 / U-CP-30 / U-CP-32 / U-CP-44 / U-CP-45 / U-CP-53** (§2.4 inline-enum promotions), **U-CP-14** (`AuditLedgerEntry` record carrier declared — §2.5) |
| **C — edge-add only** (amendment note, body preserved verbatim) | v2.6 amendment-note table row (§1.4, §2.2, §2.5, §2.6, §3.2) — no body in this proposal | U-CP-03, 04, 05, 06, 07, 09, 11, 13, 17, 21, 23, 25, 27, 29, 31, 33, 37, 38, 39, 41, 43, 46, 47, 49, 50, 51, 52, 53 |
| **D — preserved verbatim** (no R4 change) | §8 list | U-CP-00, 02, 08, 12, 15, 16, 18, 19, 20, 22, 24, 26, 34, 35, 36, 42, 48, 54, 55 |

> The §2.4 inline-enum promotions are **Class B** (signature delta — the `// {…}` comment becomes a real `enum`), but their delta blocks are already filed at §2.4 — not re-filed here. §7 names them in Class B for the change-note ledger; §2.4 is the body-of-record. Likewise U-CP-01 (§1.4), U-CP-10 (§5.2/§5.3), U-CP-40 (§4.2), U-CP-14 (`AuditLedgerEntry` carrier, §2.5) — each Class-B delta block is filed in the section that resolves its pattern. **§7 is the index; §§1–5 are the bodies.** This avoids duplicating delta blocks.

### §7.2 The Class-B delta-block index

| Unit | Delta filed at | Delta summary |
|---|---|---|
| U-CP-00b | §1.3 | NEW — full body; `AttributeValueType` + `Cardinality` carrier |
| U-CP-01 | §1.4 | Strip inline `AttributeValueType`/`Cardinality`; `Depends on: + [U-CP-00b]` |
| U-CP-10 | §5.2 + §5.3 | Strip local `LifecycleEventClass`; re-type `class` field to `WorkflowEventClass`; `Depends on: + [U-CORE-01]`; promote `ParentRelation` to real `enum` |
| U-CP-14 | §2.5 | Declare `AuditLedgerEntry` `record` carrier; `Depends on:` gains the `harness-core` / U-CP-00b / U-CP-30 edges per §2.2/§2.6 |
| U-CP-28 | §2.4 | Promote `OutputSchemaKind` `// {…}` → real `enum` |
| U-CP-30 | §2.4 | Promote `ActionKind` + `ReferenceClass` `// {…}` → real `enum`s |
| U-CP-32 | §2.4 | Promote `ParentRelationship` `// {ROOT, CHILD_OF, SIBLING_OF}` → real `enum` |
| U-CP-40 | §4.2 | Strip local `PersonaTier`; `Depends on: + [U-CORE-01]`; re-type `HITLMatrixCell.persona_tier` |
| U-CP-44 | §2.4 | Promote `KeyRotationState` `// {…}` → real `enum` |
| U-CP-45 | §2.4 | Promote `OverrideKind` + `OverrideScope` `// {…}` → real `enum`s |
| U-CP-53 | §2.4 | Promote `LayerOwner` + `RuntimeFault` `// {…}` → real `enum`s |

All Class-C units carry an amendment note (`Depends on:` delta only) in the relevant pattern table at §1.4 / §2.2 / §2.3 / §2.5 / §2.6 / §3.2. No Class-C body is rewritten — the v2.5 / U-CP-22 amendment precedent.

---

## §8 Preserved-verbatim units

The following **19 units** receive **no R4 change** — body, signatures, acceptance criteria, tests, `Depends on`, `Inputs` all preserved verbatim from the canonical-current body (resolved through the v2.5 → v2.4 → v2.3 → v2.2 → v2.1 pointer chain). The change-note's preserved-verbatim list and the v2.6 file must agree (SKILL.md §8 step 4).

`U-CP-00` (landed; L0), `U-CP-02`, `U-CP-08`, `U-CP-12`*, `U-CP-15` (landed), `U-CP-16`, `U-CP-18`, `U-CP-19` (landed), `U-CP-20`*, `U-CP-22` (landed; v2.5 body), `U-CP-24`, `U-CP-26`, `U-CP-34`, `U-CP-35`, `U-CP-36`, `U-CP-42`, `U-CP-48`, `U-CP-54`, `U-CP-55`.

> \* **U-CP-12 and U-CP-20 — preserved-verbatim with a propagation caveat.** Both are audit-verdict **FORK**, but FORK *only* because they transitively depend on U-CP-10 (`ParentRelation`-blocked at the audit snapshot). They consume `LifecycleEventClass` value *tokens* in their acceptance-criteria text (U-CP-12 acc #4; U-CP-20 per-resumption catalog). Once U-CP-10's §5.2 conversion lands (`LifecycleEventClass` → `WorkflowEventClass`), the token citations in U-CP-12/U-CP-20 must be re-anchored to the surviving name — a **cross-unit propagation** identical to the v2.4 U-CP-12 amendment ("acc #4 `LifecycleEventClass` value-token enumeration conformed to U-CP-10 conformed enum per cross-unit propagation"). R4's position: U-CP-12 and U-CP-20 bodies are **preserved verbatim** *except* for the mechanical token re-anchor, which is applied at v2.6 transcription once Q-R4-7 (name survival) is ruled. They are listed here as preserved-verbatim because no *substantive* change is made; the token re-anchor is a notation-propagation, not a re-decomposition. If the operator rules `LifecycleEventClass` survives (Q-R4-7), even the token re-anchor is null and the preservation is total.

Every other unit (the 37 in §7.1 Classes A/B/C) carries a v2.6 delta — full body (A), signature delta (B), or amendment note (C).

## §9 Dependency-graph delta

### §9.1 New nodes

- **U-CP-00b** — Level 0, `Depends on: (none)`. A pure source node, beside U-CP-00 and U-CORE-01 (the latter in the `harness-core` plan). In-degree 0; out-degree 8 (the seven Pattern-C `…AttributeSchema` consumers + U-CP-01).

No other new CP node — U-CORE-01 is the R1 product (in the `harness-core` plan, not the CP plan); CP units cite it via cross-axis import edges.

### §9.2 New edges

| Edge class | Edges | Source |
|---|---|---|
| Pattern C — `[U-CP-00b]` | U-CP-01, 07, 11, 21, 31, 37, 46, 47 → U-CP-00b (8 edges) | §1.4 |
| Pattern E — `[U-CP-00]` | U-CP-05, 06, 09, 13, 17, 21, 23, 25, 29, 53 → U-CP-00 (10 edges) | §3.2 |
| Pattern D — `[U-CORE-01 (cross-axis: core)]` | U-CP-13, 14, 17, 27, 29, 30, 38, 49, 50, 51, 52, 41, 40, 10 → U-CORE-01 (~14 units; identity aliases + `PersonaTier` + `WorkflowEventClass`) | §2.2, §4.2, §5.2 |
| Pattern D — `[U-CP-00b]` (CP-owned structured shared types) | U-CP-03, 04, 09, 13, 14, 27, 29, 30, 32, 43, 45, 49, 50, 51 → U-CP-00b | §2.2 |
| Pattern D — AS cross-axis | U-CP-04, 39 → `[U-AS-03 (cross-axis: AS)]`; U-CP-39 → `[U-AS-33 (cross-axis: AS)]`; U-CP-41 → `[U-AS-01 (cross-axis: AS)]` (proposing — Q-R4-4) | §2.3 |
| Hidden-coupling (within-axis) | U-CP-13→28, U-CP-14→30, U-CP-27→28, U-CP-39→40, U-CP-50→30, U-CP-27→14, U-CP-44→14 (7 edges); U-CP-03→05 *(proposing — Q-R4-5; default re-home `RoutingDecisionTrace` to U-CP-00b instead, no edge)* | §2.6 |
| Cross-cluster (within-axis) | U-CP-52 → U-CP-17 (`HITLInvocation` carrier) | §2.5 |

### §9.3 Acyclic invariant

- **U-CP-00b** is a pure source node (in-degree 0) — adding inbound-only edges to it cannot create a cycle.
- **U-CORE-01** (`harness-core`) is a pure source node — cross-axis import edges to it are inbound-only; no cycle.
- **`[U-CP-00]` Pattern-E edges** — U-CP-00 is a pure source node (v2.5 §0.5 establishes this); inbound-only; no cycle.
- **Hidden-coupling edges** — all point from a consumer to a *declaring* unit. The audit (Findings-considered #7) confirmed the §3.2 9-level Kahn DAG is acyclic; the hidden-coupling edges are *missing edges that already correspond to a real consumption ordering* — adding them makes the graph match reality. The one exception is **U-CP-03 → U-CP-05** (a consumer at L0 to a declarer at L2 — a level inversion). R4's default resolution (re-home `RoutingDecisionTrace` to U-CP-00b, §2.6 note) **avoids the edge entirely** — U-CP-03 then takes `[U-CP-00b]` (L0→L0, no inversion) and the U-CP-03→U-CP-05 edge is never added. If the operator instead rules U-CP-05 keeps `RoutingDecisionTrace` (Q-R4-5 reading b), U-CP-03 and U-CP-05 must be re-atomized so the declaration precedes consumption — R4 flags this as the only place the DAG is at risk, and the default resolution removes the risk.
- **Topological levels** — U-CP-00b joins U-CP-00 at L0. U-CP-22 already moved L0→L1 at v2.5. The Pattern-E `[U-CP-00]` consumers and the Pattern-C `[U-CP-00b]` consumers are all already at L1+ (they had non-trivial deps); adding a source-node edge does not change their level. **No unit changes level by R4** except via the U-CP-03 `RoutingDecisionTrace` re-home (U-CP-03 stays L0 — it now depends only on L0 source nodes). The 9-level structure (L0–L8) is preserved; L0 gains U-CP-00b.
- **Re-verification:** the v2.6 graph is a DAG. Kahn execution: U-CP-00, U-CP-00b, U-CP-01, U-CP-07, U-CP-10 (now L0-input-only via `harness-core`)… consume to ∅. Acyclic invariant holds.

---

## §10 Coverage-matrix delta

CP plan §4 coverage matrix: rows = the 24 C-CP contracts; columns = plan units. R4 deltas:

| Coverage cell | At v2.5 | At v2.6 | Note |
|---|---|---|---|
| (no contract row) — **U-CP-00b column** | n/a | U-CP-00b is a **carrier unit with no single committing contract** (§1.3) | U-CP-00b is traced to the *aggregate* of C-CP-01 §1.4 / C-CP-03 §3.5 / C-CP-07 / C-CP-10 §10 / C-CP-18 §16 / C-CP-20 §20.4 / C-CP-21 §21.5 — it adds a column mark to each of those seven contract rows (it serves their attribute schemas). It does **not** add a new contract row. Q-R4-1 covers the carrier-citation form. |
| C-CP-05 §5.1 (lifecycle event taxonomy) | Covered at U-CP-10 (8-class enum + span-name map) | Covered at **U-CORE-01** (`harness-core` plan — the event-class enum) **+ U-CP-10** (the span-name map) | Multi-unit coverage of one contract — SKILL.md §4.2 permits; `Implementation_Plan_Harness_Core_v1_0.md` §4 already records this. U-CP-10's §5.1 mark is **NOT dropped** — it is *narrowed* to the span-name map; U-CORE-01 *adds* the enum-axis mark. |
| C-CP-07 §7.3 (workload-class taxonomy) | Covered at U-CP-00 (v2.5) | Unchanged — Pattern E adds `[U-CP-00]` *edges*, not coverage marks | The Pattern-E units *consume* `WorkloadClass`; they do not *cover* C-CP-07 §7.3. No coverage delta. |

**No contract row loses a mark.** Every C-CP-01…C-CP-24 row remains covered by ≥1 unit. Every plan unit column (including U-CP-00b) has ≥1 row mark (U-CP-00b via the aggregate-attribute-schema rows). Coverage matrix completeness preserved (SKILL.md §5 step 8 / §8 step 5).

> **Coverage caveat — U-CP-00b's no-single-contract status.** U-CP-00b is the one v2.6 unit whose `Implements` line is an *aggregate* citation, not a single `C-CP-NN §N` (§1.3). This is permitted under SKILL.md §4.2's multi-contract-composition clause, but it is unusual for a *carrier* unit. The alternative — keeping `AttributeValueType`/`Cardinality` inline at U-CP-01 (which *does* have a single contract, C-CP-01 §1.4) — fails Pattern C (the seven sideways consumers cannot reach it). R4's resolution accepts the aggregate-citation carrier; Q-R4-1 surfaces this for operator review (the `harness-core`-residence alternative would have the *same* aggregate-citation property — there is no placement that gives U-CP-00b a single committing contract, because the two enums genuinely serve seven contracts).

---

## §11 Permanent auxiliary-type-audit section

Per audit §4A.4 sub-pass 3(c): "Add a §5-style auxiliary-type audit section to the CP plan so the blind spot does not recur." This section is **proposed as a new permanent §5.x section of the CP plan v2.6** (the AS plan has a §5.4.1 analog; the CP plan had none — that absence is exactly why Pattern C/D went uncaught). It enumerates **every CP-axis auxiliary type**, its carrier, and its consuming units. Future CP plan revisions extend this table; a type at a signature position absent from this table is a materializability defect by construction.

### §11.1 CP auxiliary-type registry

| Type | Kind | Carrier | Consuming units | Trace |
|---|---|---|---|---|
| `WorkloadClass` | enum | `harness-core` / U-CP-00 (landed) | U-CP-05/06/09/13/17/21/22/23/25/29/53 | C-CP-07 §7.3 |
| `AttributeValueType` | enum | **U-CP-00b** (new) | U-CP-01/07/11/21/31/37/46/47 | aggregate (7 attribute-schema contracts) |
| `Cardinality` | enum | **U-CP-00b** (new) | U-CP-01/07/11/21/31/37/46/47 | aggregate |
| `EngineClass` | enum | U-CP-15 (landed) | in-axis (U-CP-16/17/19/24/25/40/53) | C-CP-07 §7.1/§7.4 |
| `TopologyPattern` / `CascadePolicy` | enum | U-CP-22 (landed) | in-axis | C-CP-10 §10.1/§10.2 |
| `ResumptionKind` | enum | U-CP-19 (landed) | in-axis | C-CP-08 §8.1 |
| `WorkflowEventClass` | enum | `harness-core` / U-CORE-01 | U-CP-10, U-CP-12, U-CP-20 (+ IS U-IS-14) | C-CP-05 §5.1 |
| `WorkflowEvent` | model | `harness-core` / U-CORE-01 | cross-axis | C-CP-05 §5.1/§5.2 |
| `DeploymentSurface` | enum | `harness-core` / U-CORE-01 | U-CP-16, U-CP-17 | C-AS-09 §9.1 |
| `PersonaTier` | enum | `harness-core` / U-CORE-01 | U-CP-17/25/36/40/50 | C-AS-09 §9.4 / ADR-D5 §1.5 |
| `ActionID`/`EntryID`/`WorkflowID`/`StepID`/`ThreadID`/`StageID`/`ContractID`/`UnitId`/`ReferenceToUnit` | newtype | `harness-core` / U-CORE-01 | U-CP-13/14/27/29/30/38/41/49/50/51/52 | C-IS-05 §5 / C-CP-05 §5 / C-CP-13 §13.4 / plan-internal |
| `ActorIdentity` | newtype | **U-CP-00b** (proposing — Q-R4-7) | U-CP-14/27/30/49 | carrier-map "`ActorIdentity` vs IS `Actor`" |
| `AgentRole` | enum/newtype | **U-CP-00b** | U-CP-03/04/09/27/29 | C-CP-13 §13.4 |
| `ModelBinding` | record | **U-CP-00b** | U-CP-13/14/29/50 | ADR-F1 v1.2 / C-CP-13 §13.4 |
| `TraceContext` | record | **U-CP-00b** | U-CP-03 | OTel adoption / CP §8 |
| `ProviderAgnosticPayload` | record | **U-CP-00b** | U-CP-03 | ADR-F1 v1.2 / C-CP-01/02 |
| `RoutingDecisionTrace` | record | **U-CP-00b** (re-homed — proposing Q-R4-5) / else U-CP-05 | U-CP-03, U-CP-05 | CP §2 layered routing |
| `MCPTrustTier` | enum | **U-CP-00b** | U-CP-43/45 | C-CP-43 gate-level |
| `Axis` | enum | **U-CP-00b** | U-CP-43 | 5-axis gate enum (plan-introduced) |
| `TailKeepPredicate` | type | **U-CP-00b** | U-CP-32/51 | CP §51 tail-keep |
| `MCPServerID` / `ToolName` / `ToolTier` | newtype | AS-owned cross-axis (proposing — Q-R4-4) | U-CP-04/39/41 | C-AS-02/03 |
| `HandoffContext`/`StateSummary`/`LedgerEntryRef` | record | U-CP-30 (self-declares) | U-CP-13/14/27/38/50 | ADR-D4 v1.1 / C-CP-13 §13.4 |
| `ProposedAction`/`ActionPayload` | record | U-CP-30 (self-declares) | U-CP-30 | CP §16/§17 |
| `FailedAttempt`/`Alternative`/`RetryHistory` | record | U-CP-30 | U-CP-30 | CP §13.4 (`RetryHistory` named) |
| `CurrentState` (= `StateSummary`) | record | U-CP-30 (spelling-unify to `StateSummary`) | U-CP-30/50 | CP §13.4 |
| `RetryPolicy` | record | U-CP-04 | U-CP-04 | CP §3.5 `retry.*` |
| `RoleRoutingBinding`/`WorkloadRoutingOverride` | record | U-CP-04 | U-CP-04 | CP §3 routing-manifest |
| `MaterialDiff`/`DiffEntry` | record | U-CP-50 (self-declares) | U-CP-50 | CP §22 (C-CP-22) |
| `VerifierResult`/`OverlayResolution` | record | U-CP-41 | U-CP-41 | CP §18.3/§18.4 |
| `WebhookConfig`/`WebhookPayload` | record | U-CP-52 | U-CP-52 | CP §18 |
| `HITLInvocation` | record | U-CP-17 | U-CP-52 (`[U-CP-17]`) | CP §17 |
| `LeadAgentPlan`/`SubAgent`/`CacheWarmupResult` | record | U-CP-33 | U-CP-33 | ADR-D4 v1.1 |
| `EngineClassPreferences` | record | U-CP-27 | U-CP-27 | CP §7.4 |
| `GateOverride` | record | U-CP-27 | U-CP-27 | CP gate-level |
| `RewrittenToolCall` | record | U-CP-39 | U-CP-39 | function return |
| `ParentRelation` | enum | U-CP-10 (promoted — Q-R4-3) | U-CP-10 | CP §10 / ADR-D4 v1.1 |
| `AuditLedgerEntry` | record | U-CP-14 (CP-spec-owned) | U-CP-14/27/44 | C-CP-16 §16.2 / C-CP-20 |
| `OutputSchemaKind` | enum | U-CP-28 (promoted from `// {…}`) | U-CP-28 | CP §13 output-schema |
| `ParentRelationship` | enum | U-CP-32 (promoted `{ROOT,CHILD_OF,SIBLING_OF}`) | U-CP-32 | CP §15 span hierarchy |
| `OverrideKind`/`OverrideScope` | enum | U-CP-45 (promoted from `// {…}`) | U-CP-45/46 | CP §19 operator-policy |
| `ActionKind`/`ReferenceClass` | enum | U-CP-30 (promoted from `// {…}`) | U-CP-30 | CP §13.4 |
| `KeyRotationState` | enum | U-CP-44 (promoted from `// {…}`) | U-CP-44 | CP §20 key-rotation |
| `LayerOwner`/`RuntimeFault` | enum | U-CP-53 (promoted from `// {…}`) | U-CP-53 | CP §24 T-perm-3 |
| `MerkleRoot` / `F1LayerState`/`D1LayerState`/`D4LayerState` | record | self-declared (U-CP-35 / U-CP-53) | in-cone — not a finding | — |
| `*Violation` / `*Error` (~conventional) | exception | per-unit inline at first-consuming unit (sanctioned by this section) | every `Result<_, E>` unit | `HarnessError` base; thin, no shape ambiguity |

### §11.2 Registry discipline

- A type appearing at a CP signature position **must** appear in §11.1 with a carrier and a trace before the consuming unit lands. A type at a signature position absent from §11.1 is a Pattern-C/D-class defect by construction — the registry makes the blind spot self-detecting.
- Stack/cryptographic/OTel primitives (`string`, `int`, `bytes`, `SHA256`, `ISO8601`, `JSONSchema`, `Duration`, OTel-SDK span handles) are **excluded** — no carrier needed (audit Findings-considered #1).
- Cross-axis IS/AS types (`Actor`, `IdempotencyKey`, `FilesystemPath`, `BlastRadiusTier`, `SandboxTier`) resolve via declared `(cross-axis: …)` edges — they appear in §11.1 only where a CP unit's edge was missing; otherwise they are the IS/AS plans' registry rows.
- Future CP plan revisions **extend §11.1**; a new auxiliary type is added with its carrier in the same revision that introduces it.

---

## §12 Operator questions (Q-R4-N)

| ID | Question | Class | R4 default / recommendation |
|---|---|---|---|
| **Q-R4-1** | `AttributeValueType` / `Cardinality` residence — a new CP foundational unit **U-CP-00b** (R4 recommendation; CP-owned per carrier-map disposition 2 + T2), or a `harness-core` unit (carrier-map §4A.4 item-1 alternative), or keep them inline at U-CP-01 with 7 dep-edges to U-CP-01? Sub-question: ratify the **aggregate-citation `Implements` form** for U-CP-00b (§1.3, §10 caveat) — a carrier unit traced to 7 contracts rather than 1. | §2.7.6 Class 1 | **U-CP-00b** — all 7 consumers are CP-axis; no cross-axis sharing; disposition-2 placement. Aggregate-citation form accepted (no placement gives a single contract). |
| **Q-R4-2** | U-CP-01's `RoutingAttributeSchema.cardinality` field has no C-CP-01 §1.4 basis (the §1.4 routing table columns are `{Attribute, Type, Semantic, Source}` — no Cardinality column; fork-queue item 17). Keep the field as a sanctioned plan-internal characterization (uniform across all 7 `…AttributeSchema` records), or strike it from `RoutingAttributeSchema`? | §2.7.6 Class 2 | **Keep** — it is plan-added, uniform across the seven attribute-schema records, and the spec defers schema shape to plan discretion. Plan-internal, sanctioned. |
| **Q-R4-3** | `ParentRelation` value set (U-CP-10) — R4 proposes `{ROOT, CHILD_OF, DELEGATED_TO}` (§5.3); neither CP §5.1 nor ADR-D4 enumerates a named set. Confirm the value set, or drop the `LifecycleEventClassMetadata.parent_relation` field (audit §4A.7 item-4 offers both). **Sub-question:** confirm the §2.4 ellipsis-enum value-set completions (`OutputSchemaKind`, `OverrideKind`, `OverrideScope`, `ActionKind`, `ReferenceClass`, `KeyRotationState`, `LayerOwner`, `RuntimeFault`) — R4 promotes the `// {…}` comments but cannot invent elided values; the executor completes each against the declaring unit's cited spec section at v2.6 transcription. | §2.7.6 Class 1 (`ParentRelation`); Class 2 (ellipsis enums) | **Confirm `{ROOT, CHILD_OF, DELEGATED_TO}`** as the faithful ADR-D4-v1.1 factor-out. Ellipsis enums: value-set completion is a transcription-time check against each unit's spec section. |
| **Q-R4-4** | `MCPServerID` / `ToolName` placement — (a) AS-owned types with CP `(cross-axis: AS)` edges (R4 default), or (b) `harness-core` identity aliases joining U-CORE-01 (R1-reopen). `ToolName` overlaps `ContractID`'s already-declared U-CORE-01 domain ("tool/routing contract identifier — C-AS-03"). Coordinated with the R3 (AS) pass. | §2.7.6 Class 1 | **(a)** — keep AS-domain identity in AS; but if the operator rules `ToolName` ⊆ `ContractID`, fold it into U-CORE-01 (R1-reopen). R3 confirms the AS export carrier either way. |
| **Q-R4-5** | U-CP-03 ↔ U-CP-05 — U-CP-03 (L0) consumes `RoutingDecisionTrace`, declared at U-CP-05 (L2): a level inversion. Resolve by (a) re-homing `RoutingDecisionTrace` to U-CP-00b (R4 default — keeps the DAG level-ordered, U-CP-03 takes `[U-CP-00b]`), or (b) keeping it at U-CP-05 and re-atomizing U-CP-03/U-CP-05. **Also:** U-CP-23's `default_pattern` single-vs-dual structural mismatch (fork-queue item 4) is a *verbatim-axis* carry — R4 does not resolve it; it stays a v2.6 §0.8 forward-flagged concern. | §2.7.6 Class 1 (U-CP-03/05); Class 2 (U-CP-23 carry) | **(a)** — re-home `RoutingDecisionTrace` to U-CP-00b alongside `TraceContext`/`ProviderAgnosticPayload`. Keeps acyclic + level-ordered. U-CP-23 `default_pattern`: carried, not R4-resolved. |
| **Q-R4-6** | U-CP-15 (landed) `CapabilityFloor` — the field set (`capability_name`, `required_at_class`, `rationale`) has a thin C-CP-07 §7.4 basis; audit logged a §2.7.6 Class 3 informational. Accept as faithful §7.4 factor-out (landed unit stands; R4 default), or flag for a §7.4 spec re-check? | §2.7.6 Class 3 (informational) | **Accept** — the field set is a reasonable operationalization of §7.4 capability-floor prose. Non-blocking; does not gate any landing. Carried as a retrospective flag only. |
| **Q-R4-7** | U-CP-10 ↔ U-CORE-01 name survival — `WorkflowEventClass` (U-CORE-01 spelling — R4 recommendation; the `harness-core` carrier must own the cross-axis-consumed type) or `LifecycleEventClass` (U-CP-10's landed spelling)? R1 explicitly preserved the operator's right to rule. The ruling settles the U-CP-12 / U-CP-20 token re-anchor (§8) and the landed-U-CP-10 source re-point (§5.4). **Sub-question:** `ActorIdentity` — keep on U-CP-00b (R4 default, §2.2.1) or fold into U-CORE-01 as a 10th `harness-core` alias (R1-reopen)? | §2.7.6 Class 1 | **`WorkflowEventClass` survives**; U-CP-10 converts to a consuming site (§5.2). `ActorIdentity` on U-CP-00b. |

> **Decided / proposing / open summary.** **Decided** (authority-chain-determinate, no operator input needed beyond ratification): the Pattern C carrier-edge mechanics; the Pattern E edge materialization; the Pattern D FACTOR-OUT carrier placements for the 6 T2-*decided* types (`WorkflowEvent`, `DeploymentSurface`, `WorkflowClass`@IS, `AuditLedgerEntry`, `MaterialDiff`, `HandoffContext`/`RetryHistory`-cluster); the inline-enum promotions where the comment fully enumerates the set (`ParentRelationship`); the v2.5 §0.8 disposition correction; the U-CP-40 conversion. **Proposing** (R4 recommendation, operator confirms — the 21 T2-*proposing* types' carrier placements + the U-CP-10 conversion + U-CP-00b residence + `RoutingDecisionTrace` re-home): captured at Q-R4-1/3/4/5/7. **Open** (genuinely owed): the `ParentRelation` value set (Q-R4-3) and the U-CP-15 `CapabilityFloor` acceptance (Q-R4-6) — neither resolvable by reading the authority chain alone; and the name-survival ruling (Q-R4-7), which R1 explicitly reserved to the operator.

---

## §13 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/revision_R4_cp_plan.md` |
| Role | `implementation-planner`, revision-pass sub-mode (`implementation-planner` SKILL.md §8) |
| Revision pass | R4 — CP plan materializability conformance (4th of the R1–R5 carrier-map absorption sequence) |
| Authored | 2026-05-15, Phase 7 sub-phase 7b |
| Inputs | `materializability_audit_cp_plan.md` (Q2 — canonical CP systemic-tension record: 20 CLEARED / 12 CONFORM / 24 FORK; Patterns C/D/E); `shared_type_carrier_map.md` (T1 — ratified carrier map); `xal3_resolution_recommendations.md` (T2 — 27/27 FACTOR-OUT); `revision_R1_harness_core.md` §3.3 (CP hand-off list); `Implementation_Plan_Harness_Core_v1_0.md` (applied U-CORE-01 carrier); CP plan delta chain v2.5 → v2.4 → v2.3 → v2.2 → v2.1; `Spec_Control_Plane_v1_3.md` / `v1_2.md`; `harness-cp/CLAUDE.md`; workspace root `CLAUDE.md` §1.3/§3 |
| Output proposal | CP plan v2.5 → **v2.6** amendment: U-CP-00b new foundational unit (Pattern C); 8 Pattern-C dep-edges; 10 Pattern-E `[U-CP-00]` edge materializations; ~14 `[U-CORE-01]` + ~14 `[U-CP-00b]` Pattern-D edges; 9 inline-enum promotions; 7 hidden-coupling edges; U-CP-40 + U-CP-10 declaration-site conversions; new permanent §11 auxiliary-type-audit section. Unit inventory 56 → 57. |
| Status | `Proposed` — pending operator ratification of the §12 questions (Q-R4-1 … Q-R4-7) |
| Successor | On ratification: `Implementation_Plan_Control_Plane_v2_6.md` carries the U-CP-00b body + the Class-B signature deltas + the Class-C amendment notes + §11; the landed U-CP-10 / U-CP-15 source re-checks per §5.4 / §6 are recorded in the v2.6 application change-note; R5 (OD plan revision) is the final R-series pass |
| HARD WALL attested | This pass wrote **only** `.harness/revision_R4_cp_plan.md`. No `design-substrate/` file, no `CLAUDE.md`, no plan/spec/audit/carrier-map, no source code edited. No git commit. |

*End of Revision R4 — Control Plane Plan: Materializability Conformance. The operator ratifies the §12 questions before `Implementation_Plan_Control_Plane_v2_6.md` is written. R4 is the fourth of the five-pass R1–R5 carrier-map absorption sequence; R5 (OD) is the last.*
