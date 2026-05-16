# Implementation Plan — Control Plane v2.6

**Status:** Proposed

**Date:** 2026-05-15

**Revision:** v2.6 — Phase 7 sub-phase 7b in-CLI plan revision absorbing the operator-ratified **Revision R4** (CP plan materializability conformance — the 4th of the 5-pass R1–R5 carrier-map absorption sequence). Adds foundational carrier unit **U-CP-00b**; materializes Pattern C / D / E carrier-and-edge work; converts U-CP-40 and U-CP-10 from declaring to consuming sites; adds permanent §11 auxiliary-type-audit section.

**Revision date:** 2026-05-15

**Source set:** CP spec v1.3 + CP spec v1.2 (§10–§24 preserved-verbatim) + ADR-D1 v1.2 + ADR-D6 v1.2 + ADD v1.3 + PRD v1.1 (substrate versions unchanged from v2.5; **zero design-substrate revision** — per the T2 X-AL-3 resolution all 27 candidates are FACTOR-OUT)

**Authority chain:** `Project_Workflow_v1_8.md` §7.4 fidelity-grammar; `implementation-planner` SKILL.md §8 revision-pass sub-mode; `CLAUDE.md` §1.3 authority chain.

**Entry authorization:** Operator ratification 2026-05-15 — all 9 R4-relevant decisions (D3–D9 + the two propagation-gated clears) approved in full; `.harness/revision_R4_cp_plan.md` §12 questions Q-R4-1 … Q-R4-7 ruled per R4's defaults.

---

## §0 Change-note (v2.5 → v2.6)

### §0.1 Trigger

v2.6 absorbs the operator-ratified **Revision R4** (`.harness/revision_R4_cp_plan.md`) — the CP plan materializability conformance pass. R4 itself absorbed four upstream inputs:

- `.harness/materializability_audit_cp_plan.md` (Q2) — the canonical CP-plan systemic-tension record: of 56 CP units, **20 CLEARED / 12 CONFORM / 24 FORK**. Three CP-specific systemic patterns: **Pattern C** (`AttributeValueType`/`Cardinality` declared once at U-CP-01, consumed sideways with no carrier edge at 7 units), **Pattern D** (≥25 undeclared auxiliary types at signature positions with no declaring carrier), **Pattern E** (the v2.5 §0.5 deferred `[U-CP-00]` `WorkloadClass` edges, recorded-not-materialized at ~10 consumer bodies).
- `.harness/shared_type_carrier_map.md` (T1) — ratified carrier map; CP Pattern-D per-type triage; names candidate carrier unit **U-CP-00b**.
- `.harness/xal3_resolution_recommendations.md` (T2) — 27 of 27 X-AL-3 candidates resolved **FACTOR-OUT** (concept spec-committed; declaration site missing). **Zero design-substrate revision required.** The audit's "Class-1 halt" framing for the CP structured-type cluster and `AuditLedgerEntry` is lifted.
- `Implementation_Plan_Harness_Core_v1_0.md` (R1, applied) — declares **U-CORE-01** in the `harness-core` plan: `DeploymentSurface`, `PersonaTier`, the 9-alias identity module (`ActionID`/`EntryID`/`WorkflowID`/`StepID`/`ThreadID`/`StageID`/`UnitId`/`ReferenceToUnit`/`ContractID`), and `WorkflowEventClass`/`WorkflowEvent`.

### §0.2 Scope of v2.6

| In scope | Out of scope |
|---|---|
| New CP foundational carrier unit **U-CP-00b** (Pattern C) — full body (§2.0b) | The IS / AS / OD per-axis edge lists — R2 / R3 / R5 scope |
| Pattern C consumer dep-edges — 7 `…AttributeSchema` units + the U-CP-01 inline-enum strip (§0.10) | U-CORE-01 itself — R1's product, applied; v2.6 only cites it |
| Pattern D carrier re-pointing — every undeclared type to its ratified carrier (§0.11) | Source-code edits to landed units — flagged at §0.13, not performed |
| Pattern D hidden-coupling edges — the missing `Depends on` edges (§0.11) | The §4A verbatim cluster (off the table; U-CP-23 `default_pattern` carried at §0.8) |
| Pattern E — materialize the ~10 `[U-CP-00]` `WorkloadClass` edges in-body (§0.12) | New H_T design (zero per T2 — every type is a factor-out) |
| U-CP-40 declaration-site conversion (`PersonaTier`) (§2.0c-ref / §0.11) | |
| U-CP-10 ↔ U-CORE-01 reconciliation (`WorkflowEventClass`) (§2.2-revised) | |
| Inline-comment-enum promotions (9 enums) (§0.11) | |
| Retrospective re-check flags for landed U-CP-10/15 (§0.13) | |
| Permanent auxiliary-type-audit section (§11) | |

### §0.3 The CONFORM / FORK distinction (audit-derived)

The Q2 audit verdicts split the affected units into two buckets:

- **12 CONFORM** (U-CP-05, 06, 07, 09, 11, 17, 21, 29, 31, 37, 46, 47) — authority-chain-determinate. Pure Pattern-C carrier-edge + Pattern-E deferred-edge work; cleared by the mechanical carrier+edge pass.
- **24 FORK** (U-CP-01, 03, 04, 10, 12, 13, 14, 20, 23, 27, 28, 30, 32, 33, 38, 39, 41, 43, 44, 45, 49, 50, 51, 52) — needed an operator decision at the audit snapshot. The T2 resolution dissolved the substance: all 27 X-AL-3 candidates are FACTOR-OUTs, so the Pattern-D carrier placements are authority-chain-determinate. U-CP-12 and U-CP-20 are **propagation-gated** FORKs — they clear automatically once U-CP-10's reconciliation lands.
- **20 CLEARED** — materializable as written; no v2.6 action except where a Pattern-E `[U-CP-00]` edge or a hidden-coupling edge touches them.

### §0.4 Operator-ratified decisions (2026-05-15)

All R4 §12 questions ruled per R4's defaults; recorded here as decisions, not open questions.

| R4 question | Operator decision |
|---|---|
| **Q-R4-1** (D3) | `AttributeValueType` / `Cardinality` residence — **U-CP-00b is filed in the CP plan** (NOT `harness-core`), beside U-CP-00 at L0. The aggregate-citation `Implements` form (citing the 7 attribute-schema contracts collectively) is **approved**. |
| **Q-R4-2** (D4) | U-CP-01's `RoutingAttributeSchema.cardinality` field — **implementer's discretion; keep the field, no spec edit.** Sanctioned plan-internal characterization. |
| **Q-R4-3** (D5) | `ParentRelation` value set — **`{ROOT, CHILD_OF, DELEGATED_TO}` approved as R4 proposed.** Ellipsis-enum value-set completions are a transcription-time check against each declaring unit's cited spec section. |
| **Q-R4-4** (D6) | `MCPServerID` / `ToolName` — **AS-owned; CP consumes via a cross-axis CP→AS edge.** |
| **Q-R4-5** (D7) | U-CP-03 ↔ U-CP-05 dependency-level ordering — **fixed (mechanical): re-home `RoutingDecisionTrace` to U-CP-00b; U-CP-03 takes `[U-CP-00b]`, no level inversion.** U-CP-23's `default_pattern` single-vs-dual mismatch is **NOT resolved here** — carried as a separately-tracked verbatim-axis item (fork-queue item 4); see §0.8. |
| **Q-R4-6** (D8) | U-CP-15 `CapabilityFloor` — **recorded as a scheduled landed-unit re-check** (deferred coding-lane action item, bundled with the resume re-checks); not performed here. See §0.13. |
| **Q-R4-7** (D9) | U-CP-10 ↔ U-CORE-01 name survival — **`WorkflowEventClass` (the U-CORE-01 name) survives; `LifecycleEventClass` retired.** U-CP-10 converts to consume `harness-core`'s type. The landed U-CP-10 source re-point is recorded as a deferred action item (§0.13). `ActorIdentity` placement — **on U-CP-00b per R4's recommendation.** |

### §0.5 Sections preserved verbatim (from v2.5)

| Section | Preservation rationale |
|---|---|
| §1 Spec inventory | Substrate versions unchanged at v2.6 (CP spec v1.3/v1.2; ADR-D1 v1.2; ADR-D6 v1.2; ADD v1.3; PRD v1.1) — v2.6 adds the U-CP-00b coverage cells per §10 |
| The 20 CLEARED unit bodies + all other unaffected bodies | No materializability finding; bodies intact except where a Pattern-E / hidden-coupling edge is added (those edge-adds are §0.11/§0.12 amendment-note rows, not body rewrites) |
| U-CP-00 (landed) | Untouched; U-CP-00b sits beside it at L0 |
| U-CP-22 (v2.5 body) | Already materialized its `[U-CP-00]` edge at v2.5; not in the Pattern E set |
| §0 change-notes (v2.1 → v2.5) | Historical; carried |

### §0.6 Sections revised / added (v2.5 → v2.6)

| Section | Shape | Resolves |
|---|---|---|
| **U-CP-00b (NEW)** | New CP foundational unit (§2.0b) — declares `AttributeValueType` + `Cardinality` enums + the CP-owned structured shared types; `Depends on: (none)`; L0 | Pattern C; Pattern D (CP-owned carrier) |
| **U-CP-01** | Signature delta (§0.10) — strip the inline `enum AttributeValueType` / `enum Cardinality`; add `Depends on: [U-CP-00b]` | Pattern C; the `cardinality` field carried as a sanctioned plan-internal field (D4) |
| **7 Pattern-C consumers** (U-CP-07/11/21/31/37/46/47) | `Depends on:` adds `[U-CP-00b]`; signatures preserved | Pattern C |
| **~10 Pattern-E units** (U-CP-05/06/09/13/17/21/23/25/29/53) | `Depends on:` adds `[U-CP-00]`; `Inputs:` notes `WorkloadClass`; body preserved | Pattern E — materializes the v2.5 §0.5 recorded-not-materialized edges |
| **Pattern D FORK units** | `Depends on:` / `Inputs:` deltas re-pointing each undeclared type to its ratified carrier; inline-comment enums promoted to real `enum` declarations | Pattern D |
| **U-CP-40** | Declaration-site conversion — strip the local `PersonaTier` re-declaration; import from `harness-core`; add `Depends on: [U-CORE-01 (cross-axis: core)]` | R1 §3.3 hand-off |
| **U-CP-10** | Declaration-site conversion (§2.2-revised) — strip the local `LifecycleEventClass` enum; re-type `LifecycleEventClassMetadata.class` to `WorkflowEventClass`; add `Depends on: [U-CORE-01 (cross-axis: core)]`; promote `ParentRelation` to a real `enum` | §2.2 reconciliation; Pattern D (`ParentRelation`) |
| **U-CP-12, U-CP-20** | No body change — propagation-gated FORKs; the `LifecycleEventClass` → `WorkflowEventClass` token re-anchor is a mechanical transcription-time propagation | Propagation |
| **§11 (NEW)** | Permanent auxiliary-type-audit section — every CP auxiliary type, its carrier, its consuming units | Audit §4A.4 sub-pass 3(c) |
| §3 dependency graph | Delta per §9 (U-CP-00b node + Pattern C/D/E edges; the U-CP-03/05 order fix) | |
| §4 coverage matrix | Delta per §10 (U-CP-00b cells; no contract row dropped) | |

CP-plan unit inventory: 56 → **57** units (U-CP-00b added; U-CP-00 + U-CP-01–U-CP-55 unchanged in count).

### §0.7 v2.5 §0.8 disposition correction (Pattern E)

CP plan v2.5 §0.8 stated the Pattern-E deferred `[U-CP-00]` edges were "a v2.5 plan-internal completeness item, **not a fork**." The Q2 audit's Pattern E finding is that, **at the canonical-current body in force**, none of the ~10 `WorkloadClass`-consuming units carries `[U-CP-00]` in its `Depends on` line — so for each unit the dependency cone is broken exactly as Tension 003 described, and each is materializability-FORK-blocked until its edge is written. **v2.6 corrects the v2.5 §0.8 disposition: the Pattern-E edges are materialized in-body at §0.12, not carried as a deferred pointer.** This supersedes v2.5 §0.8's "deferred, not a fork" reading.

### §0.8 Forward-flagged concerns (v2.6)

All v2.5 §0.8 forward-flagged concerns carry unchanged **except** Tension 003's deferred-materialization note (resolved at §0.12 of this revision). v2.6 adds / carries:

- The **U-CP-23 `default_pattern` single-vs-dual structural mismatch** (§4A verbatim borderline, fork-queue item 4) — **carried, not resolved by v2.6** (it is a verbatim-axis item, not a materializability item; tracked separately per operator decision D7).
- The U-CP-01 `cardinality` field §1.4-basis note (fork-queue item 17) — operator-ruled **keep** (D4); the field stands as a sanctioned plan-internal characterization.
- The U-CP-43 `MCP_TRUST` / `DEPLOYMENT_SURFACE` floor spec-silence (fork-queue item 1) — carried from v2.4 §0.8 unchanged.
- The U-CP-15 `CapabilityFloor` Class-3 informational — carried as a scheduled landed-unit re-check (§0.13).

### §0.9 v2.6 coherence-pass summary

| Pass | Status |
|---|---|
| §1 Spec inventory | ✅ PASS — no substrate-version delta; zero design-substrate revision (T2: 27/27 FACTOR-OUT) |
| §2 Atomic-unit decomposition | ✅ PASS — U-CP-00b is a single coherent change (carrier-enum + CP-owned shared-type declarations; SKILL.md §3.1); U-CP-10/U-CP-40 are declaration-site conversions; Class-C units carry edge-adds only |
| §3 Dependency graph | ✅ PASS — U-CP-00b added as L0 source node; acyclic invariant preserved (§9.3); the U-CP-03/05 inversion removed via the `RoutingDecisionTrace` re-home |
| §4 Spec-traceability | ✅ PASS — U-CP-00b traced to the aggregate of 7 attribute-schema contracts (aggregate-citation form ratified at D3); all other revised units' citations verified |
| §4.4 No spec extension | ✅ PASS — every Pattern-D type is a T2 FACTOR-OUT; the inline-enum promotions transcribe value sets already stated in plan comments; no value invented |
| Verbatim-claim check | ✅ PASS — U-CP-00b acc #1/#2 enum value sets verified byte-exact against the relocated U-CP-01 inline enums |

### §0.10 Pattern C consumer dep-edge ledger (amendment notes)

Each unit below adds `Depends on: [U-CP-00b]`; **all other signature content preserved verbatim** from the canonical-current body — pure edge-adds, not body rewrites. U-CP-01 is the exception — signature delta (strip the inline enums).

| Unit | Canonical-current `Depends on` | v2.6 `Depends on` | Change | Audit verdict |
|---|---|---|---|---|
| **U-CP-01** | `(none)` | `[U-CP-00b]` | **Signature delta** — strip inline `enum AttributeValueType` + `enum Cardinality`; `RoutingAttributeSchema.value_type`/`.cardinality` now resolve to U-CP-00b. §1.4 4-attribute `ROUTING_NAMESPACE_SCHEMA` body, acceptance criteria #1–#4, tests all preserved verbatim. | FORK → clears |
| **U-CP-07** | `(none)` | `[U-CP-00b]` | Edge-add only. `Fallback/HarnessBreaker/RetryAttributeSchema` fields resolve. | CONFORM → clears |
| **U-CP-11** | `(none)` | `[U-CP-00b]` | Edge-add only. `LeaseAttributeSchema` fields resolve. | FORK → clears |
| **U-CP-21** | `[U-CP-15]` | `[U-CP-15, U-CP-00b, U-CP-00]` | Edge-add (`[U-CP-00b]` Pattern C + `[U-CP-00]` Pattern E §0.12). `EngineAttributeSchema` fields resolve. | FORK → clears |
| **U-CP-31** | `[U-CP-22, U-CP-15]` | `[U-CP-22, U-CP-15, U-CP-00b]` | Edge-add only. `Topology/SubAgentAttributeSchema` fields resolve. | FORK → clears |
| **U-CP-37** | `(none)` | `[U-CP-00b]` | Edge-add only. `HITLResponseClassAttribute.value_type` resolves. | CONFORM → clears |
| **U-CP-46** | `[U-CP-37,38,42,43,44,45,47]` | `[U-CP-37,38,42,43,44,45,47, U-CP-00b]` | Edge-add only. `Audit/Validator/HITLSpanSchema` fields resolve. | FORK → clears |
| **U-CP-47** | `[U-AS-03]` | `[U-AS-03, U-CP-00b]` | Edge-add only. `ValidatorFailAttributeSchema` fields resolve. | FORK → clears |

U-CP-01 signature-delta block — the v2.6 U-CP-01 Signatures block is the v2.4-conformed body **minus** the final two enum lines:

```
record RoutingAttributeSchema {
  attribute_name : string
  value_type     : AttributeValueType      // resolves to U-CP-00b
  cardinality    : Cardinality             // resolves to U-CP-00b
  inherited_from : string
}
const ROUTING_NAMESPACE_SCHEMA: List<RoutingAttributeSchema>  // exactly 4 entries
// enum AttributeValueType { ... }   ← REMOVED — relocated to U-CP-00b
// enum Cardinality { ... }          ← REMOVED — relocated to U-CP-00b
```

The `cardinality` field is **kept** per operator decision D4 — plan-added, uniform across all seven `…AttributeSchema` records, the spec defers schema shape to plan discretion. Sanctioned plan-internal characterization; no spec edit.

### §0.11 Pattern D carrier re-pointing + hidden-coupling ledger (amendment notes)

Per the T2 X-AL-3 resolution, **every** Pattern-D structured type is a **FACTOR-OUT** (concept spec/ADR-committed; declaration site missing) — zero design-substrate revision. v2.6's Pattern-D work is entirely carrier-placement + dependency-graph completion.

**§0.11.1 — `harness-core` / U-CORE-01 carrier (identity aliases + cross-cutting enums).** Each consuming CP unit adds `[U-CORE-01 (cross-axis: core)]`; the type resolves at U-CORE-01.

| Type | Consuming CP unit(s) | Edge added |
|---|---|---|
| `ActionID` | U-CP-27, U-CP-30 | `[U-CORE-01 (cross-axis: core)]` |
| `EntryID` | U-CP-38, U-CP-49, U-CP-52 | `[U-CORE-01 (cross-axis: core)]` |
| `WorkflowID` | U-CP-49, U-CP-50, U-CP-51, U-CP-52 | `[U-CORE-01 (cross-axis: core)]` |
| `StepID` | U-CP-13, U-CP-14 | `[U-CORE-01 (cross-axis: core)]` |
| `ThreadID` | CP F2-keying tuple consumers | `[U-CORE-01 (cross-axis: core)]` |
| `StageID` | U-CP-29 | `[U-CORE-01 (cross-axis: core)]` |
| `ReferenceToUnit` | U-CP-41 | `[U-CORE-01 (cross-axis: core)]` |
| `PersonaTier` | U-CP-17, U-CP-40 (§4.2 conversion) | `[U-CORE-01 (cross-axis: core)]` |
| `WorkflowEventClass` | U-CP-10 (§2.2-revised conversion) | `[U-CORE-01 (cross-axis: core)]` |

> **U-CP-34 / U-CP-35 — no edge change.** Per audit Findings-rejected #9, at these two units `actor`/`action_id` resolve to the **IS-exported** `Actor`/F2 entry shape via the *already-declared* `(cross-axis: IS)` edge — they are the F2 six-field shape, NOT the U-CORE-01 alias. No edge change at U-CP-34/35; they are preserved verbatim.

**§0.11.2 — U-CP-00b carrier (CP-owned structured shared types).** Each consuming CP unit adds `[U-CP-00b]`; the type resolves at U-CP-00b's Signatures block.

| Type | Consuming CP unit(s) | Edge added |
|---|---|---|
| `ActorIdentity` | U-CP-14, U-CP-27, U-CP-30, U-CP-49 | `[U-CP-00b]` (CP-owned identity alias — operator decision D9: on U-CP-00b, not U-CORE-01) |
| `AgentRole` | U-CP-03, U-CP-04, U-CP-09, U-CP-27, U-CP-29 | `[U-CP-00b]` |
| `ModelBinding` | U-CP-13, U-CP-14, U-CP-29, U-CP-50 | `[U-CP-00b]` |
| `TraceContext` | U-CP-03 | `[U-CP-00b]` |
| `ProviderAgnosticPayload` | U-CP-03 | `[U-CP-00b]` |
| `RoutingDecisionTrace` | U-CP-03, U-CP-05 | `[U-CP-00b]` (re-homed per D7 — replaces the U-CP-03→U-CP-05 forward edge; keeps the DAG level-ordered) |
| `MCPTrustTier` | U-CP-43, U-CP-45 | `[U-CP-00b]` |
| `Axis` | U-CP-43 | `[U-CP-00b]` |
| `TailKeepPredicate` | U-CP-32, U-CP-51 | `[U-CP-00b]` |

**§0.11.3 — AS-owned types consumed by CP (cross-axis CP→AS edges).** Per operator decision D6, `MCPServerID`/`ToolName` are AS-owned; CP consumes via cross-axis edges (sanctioned CP→AS direction per CXA §2.4 IS < AS < CP < OD).

| Type | Consuming CP unit(s) | Edge added |
|---|---|---|
| `MCPServerID` | U-CP-39 | `[U-AS-33 (cross-axis: AS)]` |
| `ToolName` | U-CP-04, U-CP-39 | `[U-AS-03 (cross-axis: AS)]` |
| `ToolTier` | U-CP-41 | `[U-AS-01 (cross-axis: AS)]` |

**§0.11.4 — inline-comment-enum promotions (signature deltas).** Nine enums are declared in CP unit Signatures blocks only as `// {…}` comments. Promotion is mechanical: replace the `// {…}` comment with a real `enum` in the declaring unit. No value invented; where a comment uses an ellipsis the value-set completion is a transcription-time check against the declaring unit's cited spec section (operator decision D5 sub-item).

| Enum | Declaring unit | Value set | Status |
|---|---|---|---|
| `OutputSchemaKind` | U-CP-28 | `{ JSON_SCHEMA, … }` | ellipsis — completion checked at landing |
| `ParentRelationship` | U-CP-32 | `{ ROOT, CHILD_OF, SIBLING_OF }` | fully enumerated — promoted directly |
| `OverrideKind` | U-CP-45 | `{ … }` | ellipsis — completion checked at landing |
| `OverrideScope` | U-CP-45 | `{ … }` | ellipsis — completion checked at landing |
| `ActionKind` | U-CP-30 | `{ … }` | ellipsis — completion checked at landing |
| `ReferenceClass` | U-CP-30 | `{ … }` | ellipsis — completion checked at landing |
| `KeyRotationState` | U-CP-44 | `{ … }` | ellipsis — completion checked at landing |
| `LayerOwner` | U-CP-53 | `{ … }` | ellipsis — completion checked at landing |
| `RuntimeFault` | U-CP-53 | `{ … }` | ellipsis — completion checked at landing |

**§0.11.5 — structured-type in-place carriers.** Per T2, every structured type below is a FACTOR-OUT with a CP-owned carrier at a natural cluster unit. Most are already self-declared at the named unit — the defect is the missing consumer edge.

| Type | Carrier unit | Consumer units needing the edge |
|---|---|---|
| `HandoffContext` / `StateSummary` / `LedgerEntryRef` | U-CP-30 (self-declares) | U-CP-13, U-CP-14, U-CP-27, U-CP-38, U-CP-50 |
| `ProposedAction` / `ActionPayload` | U-CP-30 (self-declares) | U-CP-30 internal |
| `FailedAttempt` / `Alternative` / `RetryHistory` | U-CP-30 | U-CP-30 internal |
| `CurrentState` (= `StateSummary`) | U-CP-30 | U-CP-30, U-CP-50 |
| `MaterialDiff` / `DiffEntry` | U-CP-50 (self-declares) | U-CP-50 internal |
| `RetryPolicy` | U-CP-04 | U-CP-04 internal |
| `RoleRoutingBinding` / `WorkloadRoutingOverride` | U-CP-04 | U-CP-04 internal |
| `VerifierResult` / `OverlayResolution` | U-CP-41 | U-CP-41 internal |
| `WebhookConfig` / `WebhookPayload` | U-CP-52 | U-CP-52 internal |
| `HITLInvocation` | U-CP-17 | U-CP-52 — cross-cluster edge `[U-CP-17]` |
| `LeadAgentPlan` / `SubAgent` / `CacheWarmupResult` | U-CP-33 | U-CP-33 internal |
| `EngineClassPreferences` | U-CP-27 | U-CP-27 internal |
| `GateOverride` | U-CP-27 | U-CP-27 internal |
| `RewrittenToolCall` | U-CP-39 | U-CP-39 internal |
| `ParentRelation` | U-CP-10 (promoted to real `enum` — §2.2-revised §5.3) | U-CP-10 internal |
| `AuditLedgerEntry` | U-CP-14 (CP-spec-owned per T2; composes against IS `StateLedgerEntry`) | U-CP-14 (self-declares), U-CP-27, U-CP-44 |

> **`AuditLedgerEntry` — Class-1 halt LIFTED.** The Q2 audit flagged `AuditLedgerEntry` as a Class-1 halt (foreclosed CP→OD direction). T2 resolved: CP spec §16.2 (C-CP-16) commits the per-response audit-ledger entry shape **directly inside the CP spec**, and §20 (C-CP-20) the per-persona-tier cryptographic shape. `AuditLedgerEntry` is **CP-spec-owned** (carrier at U-CP-14), composing against the IS-exported `StateLedgerEntry` via *already-declared* CP→IS edges. It is **not** OD's `AuditLedger`/`AuditPayload`. **No CP→OD edge; the CXA matrix CP→OD = 0 is intact; no CXA revision.**

**§0.11.6 — hidden-coupling edges (≥5 confirmed).** Each consumer below consumes a sibling unit's type without declaring the `Depends on` edge; v2.6 adds each.

| Consumer | Consumed type | Declaring (carrier) unit | Edge added |
|---|---|---|---|
| U-CP-13 | `SubAgentBrief` | U-CP-28 | `[U-CP-28]` |
| U-CP-14 | `LedgerEntryRef` | U-CP-30 | `[U-CP-30]` |
| U-CP-17 | `PersonaTier` | U-CORE-01 (post-§4.2 conversion) | `[U-CORE-01 (cross-axis: core)]` |
| U-CP-27 | `SubAgentBrief` | U-CP-28 | `[U-CP-28]` |
| U-CP-39 | `SynchronyClass` | U-CP-40 | `[U-CP-40]` |
| U-CP-50 | `ExternalReference` | U-CP-30 | `[U-CP-30]` |
| U-CP-27 | `AuditLedgerEntry` | U-CP-14 | `[U-CP-14]` |
| U-CP-44 | `AuditLedgerEntry` | U-CP-14 | `[U-CP-14]` |

> **U-CP-03 → U-CP-05 — no forward edge.** U-CP-03 (L0) consumes `RoutingDecisionTrace`, declared at U-CP-05 (L2) — a level inversion. Per operator decision D7 this is fixed mechanically: `RoutingDecisionTrace` is **re-homed to U-CP-00b** (alongside `TraceContext`/`ProviderAgnosticPayload`). U-CP-03 then takes `[U-CP-00b]` (L0→L0, no inversion); the U-CP-03→U-CP-05 edge is never added. U-CP-05 also imports `RoutingDecisionTrace` from U-CP-00b.

### §0.12 Pattern E edge-materialization ledger (amendment notes)

CP plan v2.5 §0.5 recorded that ~10 `WorkloadClass`-consuming units gain a `[U-CP-00]` dependency edge but deferred the materialization to "each unit's next full-revision." Per the §0.7 disposition correction, v2.6 **materializes the recorded edges in-body**. Each unit below adds `[U-CP-00]` to its `Depends on` line and an `Inputs:` note that `WorkloadClass` (U-CP-00) is consumed. **All other body content preserved verbatim.**

| Unit | `WorkloadClass` consumption site | Canonical-current `Depends on` | v2.6 `Depends on` | Audit verdict |
|---|---|---|---|---|
| **U-CP-05** | `InferenceRequest` (symbolic, via routing layer) | `[U-CP-03]` | `[U-CP-03, U-CP-00, U-CP-00b]` (`+ U-CP-00b` for `RoutingDecisionTrace` §0.11.2) | CONFORM → clears |
| **U-CP-06** | `LayerBudget` keyed by workload class | `[U-CP-05]` | `[U-CP-05, U-CP-00]` | CONFORM → clears |
| **U-CP-09** | `compose_fallback_chain` (workload param) | `[U-CP-07, U-CP-08]` | `[U-CP-07, U-CP-08, U-CP-00, U-CP-00b]` (`+ U-CP-00b` for `AgentRole` §0.11.2) | CONFORM → clears |
| **U-CP-13** | `WorkflowManifestEntry.workload_class` | `[U-CP-04, U-CP-06, U-CP-09, U-CP-15, U-CP-22, U-CP-38]` | `+ U-CP-00, + U-CP-28 (hidden-coupling), + U-CORE-01 (StepID/ModelBinding), + U-CP-00b (ModelBinding), + U-CP-30 (HandoffContext)` | FORK → clears |
| **U-CP-17** | `WorkloadBindingSelectionInput.workload_class` | `[U-CP-16]` | `+ U-CP-00, + U-CORE-01 (DeploymentSurface/PersonaTier)` | CONFORM → clears |
| **U-CP-21** | `EngineAttributeSchema` (workload-keyed) | `[U-CP-15]` | `[U-CP-15, U-CP-00b, U-CP-00]` (`U-CP-00b` Pattern C §0.10) | FORK → clears |
| **U-CP-23** | `PerWorkloadClassTopologyCommitment.workload_class` | `[U-CP-22]` | `[U-CP-22, U-CP-00]` | FORK → clears (the `default_pattern` mismatch is a separate carry — §0.8) |
| **U-CP-25** | `WorkloadEngineMatrixCell` (workload-keyed) | `[U-CP-22, U-CP-24]` | `[U-CP-22, U-CP-24, U-CP-00]` | CLEARED → edge-add only |
| **U-CP-29** | `BriefAuthoringInheritance` (workload-keyed) | `[U-CP-28]` | `+ U-CP-00, + U-CORE-01 (StageID), + U-CP-00b (AgentRole/ModelBinding)` | CONFORM → clears |
| **U-CP-53** | `T-perm-3` composition (workload-keyed) | (v2.1 multi-dep) | `+ U-CP-00` | CLEARED → edge-add only |

> **Transcription-verification step.** v2.5 §0.5 named "U-CP-05, U-CP-06, U-CP-09, U-CP-13, U-CP-17, U-CP-21, U-CP-23, and others"; the exact tail above is derived from the audit's per-unit findings table. The v2.6 application against the landed source must verify each unit's body for any `WorkloadClass` consumption the audit's table did not surface. **U-CP-22 is NOT in this table** — its `[U-CP-00]` edge was already materialized at v2.5.

### §0.13 Deferred coding-lane action items (FLAGGED — not performed in v2.6)

v2.6 is a plan-document revision. The following are deferred coding-lane / landed-source obligations recorded here and bundled with the resume re-checks; **none is performed by v2.6** (the HARD WALL forbids source edits):

| # | Item | Trigger | Disposition |
|---|---|---|---|
| **D-1** | **U-CP-15 `CapabilityFloor` re-check** (Q-R4-6 / D8). The landed U-CP-15 `CapabilityFloor` field set (`capability_name`, `required_at_class`, `rationale`) has a thin C-CP-07 §7.4 basis (audit §2.7.6 Class-3 informational). Operator decision: scheduled landed-unit re-check; not performed here. R4 default: accept as a faithful §7.4 factor-out — non-blocking, does not gate any landing. | v2.6 ratification | Scheduled re-check, bundled with the resume re-checks. FLAGGED. |
| **D-2** | **U-CP-10 landed-source re-point** (Q-R4-7 / D9). U-CP-10 is LANDED. When v2.6 is applied, the landed U-CP-10 source MUST be re-inspected: (a) strip the local `LifecycleEventClass` enum, re-point to import `WorkflowEventClass` from `harness-core`; (b) the `ParentRelation` consumption (landed source inlined a placeholder or used `Any`/`str` — no real carrier existed) re-points to the promoted U-CP-10 `enum ParentRelation`. The re-point is recorded in the v2.6 application change-note. | v2.6 application | Source-vs-plan reconciliation. FLAGGED. |
| **D-3** | **U-CP-12 / U-CP-20 token re-anchor propagation.** Both units consume `LifecycleEventClass` value *tokens* in their acceptance-criteria text (U-CP-12 acc #4; U-CP-20 per-resumption catalog). Once U-CP-10's §2.2-revised conversion lands (`LifecycleEventClass` → `WorkflowEventClass`), those token citations are re-anchored to the surviving name — a mechanical cross-unit notation-propagation (the v2.4 U-CP-12 amendment shape). No re-decomposition; bodies otherwise preserved verbatim. | v2.6 transcription | Mechanical token re-anchor. FLAGGED. |

---

## §1 Spec inventory

[Preserved verbatim from v2.5 → v2.4 → v2.3 → v2.2. v2.6 adds U-CP-00b coverage cells per §10; no contract row dropped. Substrate versions unchanged — CP spec v1.3/v1.2; ADR-D1 v1.2; ADR-D6 v1.2; ADD v1.3; PRD v1.1. Per the T2 X-AL-3 resolution there is **zero design-substrate revision** at v2.6.]

---

## §2 Atomic-unit decomposition

### §2.0 Foundational pre-anchor (v2.5 — Tension 003 resolution)

[U-CP-00 preserved verbatim from v2.5 — declares `WorkloadClass` closed 4-value enum; `Implements: [C-CP-07 §7.3]`; `Depends on: (none)`; `harness-core` residence; L0. Untouched at v2.6; U-CP-00b sits beside it at L0.]

### §2.0b Foundational carrier (v2.6 — Pattern C / Pattern D CP-owned carrier resolution)

#### U-CP-00b — Declare `AttributeValueType` + `Cardinality` schema-attribute utility enums + the CP-owned structured shared types (v2.6 — new CP foundational carrier unit per the Pattern C carrier resolution; relocates the two attribute enums from U-CP-01's inline Signatures block to a reachable carrier, and homes the CP-owned structured routing/workflow shared types with no natural single-unit cluster)

**Implements:** (carrier unit — no single spec contract). `AttributeValueType` and `Cardinality` are **plan-introduced auxiliary enums**: they are the value-type and cardinality discriminators the CP plan uses to type its `…AttributeSchema` records (the per-namespace attribute-schema records at U-CP-01/07/11/21/31/37/46/47). No CP spec contract enumerates them as named enums — the spec commits the *namespace attribute schemas* (C-CP-01 §1.4, C-CP-03 §3.5, C-CP-07, C-CP-10 §10, C-CP-18 §16, C-CP-20 §20.4, C-CP-21 §21.5 each commit an attribute table with a "Type" / value-type column and a cardinality characterization), and the plan factors the shared value-type/cardinality vocabulary out of those tables into two enums. Per `implementation-planner` SKILL.md §4.2 a unit must cite a contract by ID and section; a pure carrier unit for a plan-internal factor-out has no single such section. **This unit is traced to the *aggregate* of the seven attribute-schema contracts it serves** — `[C-CP-01 §1.4]`, `[C-CP-03 §3.5]`, `[C-CP-07]`, `[C-CP-10 §10]`, `[C-CP-18 §16]`, `[C-CP-20 §20.4]`, `[C-CP-21 §21.5]` — each of which characterizes attribute value-types and cardinality in prose; the enum value sets are a faithful factor-out of that prose, not a spec extension. The aggregate-citation form is **operator-ratified at D3 (Q-R4-1)**. (This is the U-CP-00 precedent: U-CP-00 carries `WorkloadClass` against a single contract; U-CP-00b carries a cross-cluster vocabulary against the aggregate.)

**Depends on:** (none) — foundational; L0, beside U-CP-00. Imports nothing; the seven `…AttributeSchema` units and the Pattern-D consumers import it.

**Inputs:** None (foundational; substrate-supplying carrier unit — mirrors U-CP-00).

**Files affected:** CP-axis schema-attribute utility enums (logical: `attribute-value-type-enum`, `cardinality-enum`) + the CP-owned structured shared types (logical: `cp-shared-types`). **Residence: `harness-cp`** (CP-axis-owned per operator decision D3 — contrast U-CP-00's `harness-core` residence; all consumers are CP-axis units, no cross-axis sharing).

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

// CP-owned structured shared types (Pattern D — FACTOR-OUT carriers per T2; no
// natural single-unit cluster home). Declared here as the CP-axis shared-type
// carrier; consuming units import via [U-CP-00b].
type    ActorIdentity            // CP-owned identity alias (operator decision D9 — Q-R4-7)
enum    AgentRole                // per-role contract vocabulary — C-CP-13 §13.4
record  ModelBinding             // ADR-F1 v1.2 + C-CP-13 §13.4 — provider/model binding
record  TraceContext             // OTel W3C Trace Context (stack adoption) + CP §8
record  ProviderAgnosticPayload  // ADR-F1 v1.2 + C-CP-01/02 — provider-agnostic request payload
record  RoutingDecisionTrace     // re-homed from U-CP-05 per operator decision D7 (Q-R4-5)
enum    MCPTrustTier             // C-CP-43 gate-level trust tier
enum    Axis                     // the 5-axis gate enum (plan-introduced, CP-owned)
type    TailKeepPredicate        // CP §51 tail-keep predicate
```

**Acceptance criteria:**

1. `AttributeValueType` declares exactly five values `STRING | INT | FLOAT | BOOL | ENUM_REF` — byte-exact with the enum previously declared inline at U-CP-01 (v2.4-conformed body line 175). Closed at cardinality 5. No value added or removed by the relocation.
2. `Cardinality` declares exactly four values `LOW | MEDIUM | HIGH | PER_REQUEST` — byte-exact with the enum previously declared inline at U-CP-01 (v2.4-conformed body line 176). Closed at cardinality 4. No value added or removed.
3. Both enums reside in `harness-cp` and are exposed at the CP-axis package surface so the seven `…AttributeSchema` consuming units (U-CP-01/07/11/21/31/37/46/47) import from one path; `pyright` strict resolves a single nominal type for each across all eight units.
4. The CP-owned structured shared types (`ActorIdentity`, `AgentRole`, `ModelBinding`, `TraceContext`, `ProviderAgnosticPayload`, `RoutingDecisionTrace`, `MCPTrustTier`, `Axis`, `TailKeepPredicate`) are declared at U-CP-00b and exposed at the CP-axis package surface; each Pattern-D consumer (§0.11.2) resolves a single nominal type via `[U-CP-00b]`.
5. No spec extension: the relocation introduces no new value; each shared type is a T2-confirmed FACTOR-OUT of a spec/ADR-committed concept.

**Tests:** `test_attribute_value_type_cardinality_five`; `test_attribute_value_type_values_byte_exact_with_relocated_enum`; `test_cardinality_cardinality_four`; `test_cardinality_values_byte_exact_with_relocated_enum`; `test_both_enums_reside_in_harness_cp`; `test_attribute_schema_units_resolve_single_nominal_type` (a `pyright`-strict cross-unit composition check); `test_cp_shared_types_resolve_single_nominal_type` (Pattern-D consumers resolve the same `U-CP-00b` nominal type).

**Rollback boundary:** Revert the U-CP-00b declarations from `harness-cp`. Downstream impact: the seven `…AttributeSchema` units lose their `value_type`/`cardinality` carrier (Pattern C reopens); the Pattern-D consumers lose their structured-type carrier. If the relocation is reverted *without* restoring the inline U-CP-01 declarations, all eight attribute-schema units fail `pyright`. A single coherent revert.

### §2.1 Cluster 1 — Routing, fallback, breaker, retry (C-CP-01 through C-CP-04)

[Preserved verbatim from v2.5 → v2.4 — U-CP-01 through U-CP-09. v2.6 amendment notes only: U-CP-01 signature delta + `[U-CP-00b]` (§0.10); U-CP-03/04/05/06/07/09 edge-adds per §0.10/§0.11/§0.12 — no body rewrites.]

### §2.2 Cluster 2 — F3 lifecycle + manifest (C-CP-05, C-CP-06)

[Preserved verbatim from v2.5 → v2.4 — U-CP-11/U-CP-13. **U-CP-10 declaration-site converted at v2.6 — full revised body below.** U-CP-12 preserved verbatim with the §0.13 D-3 propagation caveat.]

#### U-CP-10 — Declare lifecycle-event-class span-name-metadata map + `ParentRelation` enum (v2.6 — declaration-site conversion: the 8-class event taxonomy is reconciled to `harness-core`'s `WorkflowEventClass` per operator decision D9; `LifecycleEventClass` retired; `ParentRelation` promoted to a real `enum` per the Pattern-D carrier resolution; C-CP-05 §5.1 span-name-map body otherwise preserved verbatim)

**Implements:** [C-CP-05 §5.1]

**Depends on:** [U-CORE-01 (cross-axis: core)]

**Inputs:** `WorkflowEventClass` enum (U-CORE-01) — consumed by `LifecycleEventClassMetadata.class`.

**Files affected:** CP-axis lifecycle-event span-name-metadata map (logical: `lifecycle-event-span-name-map`); CP-axis parent-relation enum (logical: `parent-relation-enum`).

**Signatures:**

```
// REMOVED — the C-CP-05 §5.1 8-class event taxonomy now resides in harness-core
// (U-CORE-01) as WorkflowEventClass. LifecycleEventClass is retired (operator
// decision D9 / Q-R4-7 — WorkflowEventClass survives).
// enum LifecycleEventClass { WORKFLOW_START, ... RESUMPTION }   ← strip

enum ParentRelation {
  ROOT,                                               // event has no parent span (workflow-root event)
  CHILD_OF,                                           // event is a child span of its workflow parent
  DELEGATED_TO                                        // event is a delegated sub-agent span (hierarchical-delegation / decentralized-handoff)
}
// PROMOTED to a real enum (operator decision D5 / Q-R4-3 — value set
// {ROOT, CHILD_OF, DELEGATED_TO} approved as a faithful ADR-D4 v1.1 factor-out
// of the parent-ownership semantics; carrier at U-CP-10 per the Pattern-D resolution).

// PRESERVED + RE-TYPED — the span-name map record is U-CP-10-owned (the C-CP-05
// §5.1 "Span name" column is CP-spec content; harness-core carries only the
// event-class enum, not the OTel span-name map).
record LifecycleEventClassMetadata {
  class            : WorkflowEventClass        // re-typed from LifecycleEventClass; resolves to U-CORE-01
  span_name        : string                   // canonical OTel span name — preserved verbatim
  parent_relation  : ParentRelation            // resolves to the U-CP-10-local enum above
}
const LIFECYCLE_EVENT_CLASS_METADATA: List<LifecycleEventClassMetadata>  // exactly 8 entries — preserved
```

**Acceptance criteria:**

1. **(v2.6 — struck.)** The former U-CP-10 acceptance criterion #1 (the 8-class verbatim enumeration) is **struck** — that assertion now lives at U-CORE-01 acc #4 (`harness-core` plan). U-CP-10 no longer declares the event-class enum.
2. **(preserved verbatim — re-anchored to `WorkflowEventClass`.)** `LIFECYCLE_EVENT_CLASS_METADATA` maps each `WorkflowEventClass` value to its canonical OTel span name (`WORKFLOW_START → workflow.start`, etc.) per C-CP-05 §5.1's "Span name" column.
3. **(preserved verbatim — re-anchored to `WorkflowEventClass`.)** The span-name map is closed at cardinality 8 — exactly one entry per `WorkflowEventClass` value.
4. **(preserved verbatim.)** The map delegates to the ADR-D6 OTel ingestion contract per C-CP-05 §5.1.
5. **(v2.6 — new.)** `ParentRelation` declares exactly three values `{ROOT, CHILD_OF, DELEGATED_TO}` (operator decision D5); `LifecycleEventClassMetadata.parent_relation` resolves to it. Closed at cardinality 3.
6. **(v2.6 — new.)** U-CP-10 imports `WorkflowEventClass` from `harness-core`; `LifecycleEventClassMetadata.class` composes against the single `harness-core` nominal type — `pyright` strict resolves one nominal type, not two.

**Tests:** `test_lifecycle_event_class_metadata_cardinality_eight`; `test_span_name_map_match_spec_5_1_verbatim`; `test_lifecycle_event_class_metadata_consumes_harness_core_workflow_event_class`; `test_parent_relation_cardinality_three`; `test_parent_relation_values_root_child_of_delegated_to`; `test_no_local_lifecycle_event_class_enum` (verifies the local enum is stripped).

**Rollback boundary:** Revert the `LifecycleEventClassMetadata` re-type + the `ParentRelation` enum + the `[U-CORE-01]` edge. Downstream impact: U-CP-12 / U-CP-20 token re-anchor reverts; the `LifecycleEventClass`/`WorkflowEventClass` duplicate-declaration defect reopens. A single coherent revert.

> **Multi-unit coverage of C-CP-05 §5.1.** `Implements: [C-CP-05 §5.1]` is preserved — U-CP-10 still covers the §5.1 *span-name map*; U-CORE-01 (`harness-core` plan) covers the §5.1 *event-class enum*. Multi-unit coverage of one contract is permitted (SKILL.md §4.2); `Implementation_Plan_Harness_Core_v1_0.md` §4 already records this. The `WorkflowEvent` *payload model* (§5.2 per-class attribute set) resides at U-CORE-01 — U-CP-10 does not re-declare it.

[U-CP-12 — preserved verbatim from v2.4. **Propagation caveat (§0.13 D-3):** U-CP-12 acc #4 consumes `LifecycleEventClass` value tokens; at v2.6 transcription those tokens are re-anchored to `WorkflowEventClass` (mechanical notation-propagation, the v2.4 U-CP-12 amendment shape). No substantive change; body otherwise preserved verbatim.]

### §2.3 Cluster 3 — D1 engine + replay (C-CP-07, C-CP-08, C-CP-09)

[Preserved verbatim from v2.5 → v2.4 — U-CP-14 through U-CP-21. v2.6 amendment notes only: U-CP-14 declares the `AuditLedgerEntry` `record` carrier + gains the `harness-core`/U-CP-00b/U-CP-30 edges (§0.11.5/§0.11.6); U-CP-17/21 edge-adds per §0.10/§0.11/§0.12. Note: C-CP-07 §7.1/§7.4 covered at U-CP-15 (landed — §0.13 D-1 re-check); §7.3 covered at U-CP-00 (§2.0).]

### §2.4 Cluster 4 — Topology (C-CP-10, C-CP-11)

[Preserved verbatim from v2.5 — U-CP-22 (v2.5 body), U-CP-23 (v2.4 conformance), U-CP-24/U-CP-25. v2.6 amendment notes only: U-CP-23/U-CP-25 Pattern-E edge-adds per §0.12; U-CP-22 untouched (its `[U-CP-00]` edge materialized at v2.5). U-CP-23's `default_pattern` single-vs-dual structural mismatch is **carried, not resolved** — §0.8 forward-flagged concern.]

### §2.5–§2.9 Clusters 5–9

[Preserved verbatim from v2.5 → v2.4 — U-CP-26 through U-CP-55. **U-CP-40 declaration-site converted at v2.6 — signature delta below.** v2.6 amendment notes for the rest (no body rewrites except the Class-B signature deltas listed at §0.11.4):
- **U-CP-28** — promote `OutputSchemaKind` `// {…}` → real `enum` (§0.11.4).
- **U-CP-30** — promote `ActionKind` + `ReferenceClass` `// {…}` → real `enum`s (§0.11.4); self-declares `ProposedAction`/`ExternalReference`/`HandoffContext`-family carriers (§0.11.5).
- **U-CP-32** — promote `ParentRelationship` `// {ROOT, CHILD_OF, SIBLING_OF}` → real `enum` (§0.11.4).
- **U-CP-44** — promote `KeyRotationState` `// {…}` → real `enum` (§0.11.4).
- **U-CP-45** — promote `OverrideKind` + `OverrideScope` `// {…}` → real `enum`s (§0.11.4).
- **U-CP-53** — promote `LayerOwner` + `RuntimeFault` `// {…}` → real `enum`s (§0.11.4).
- All other Cluster 5–9 edge-adds per §0.11 / §0.12.
- **U-CP-20** — preserved verbatim with the §0.13 D-3 propagation caveat (`LifecycleEventClass` token re-anchor).]

#### U-CP-40 — Declare persona-tier × engine-class 2D matrix + cell exclusion inheritance (v2.6 — declaration-site conversion: the local `PersonaTier` re-declaration is stripped and imported from `harness-core` per R1 §3.3 hand-off; `SynchronyClass`/`HITLPrimitiveShape`/`HITLMatrixCell` stay U-CP-40-owned; matrix body otherwise preserved verbatim)

**Implements:** [C-AS-09 §9.4, ADR-D5 §1.5] (preserved from the v2.4 body — persona-tier × engine-class matrix + cell exclusion inheritance)

**Depends on:** [U-CP-15, U-CORE-01 (cross-axis: core)] (v2.6 — `[U-CORE-01]` added; the v2.4 `[U-CP-15]` engine-class dependency preserved)

**Inputs:** `PersonaTier` enum (U-CORE-01); `EngineClass` enum (U-CP-15).

**Files affected:** CP-axis persona-tier × engine-class matrix (logical: `persona-engine-matrix`); CP-axis synchrony-class + HITL-primitive-shape enums (logical: `synchrony-class-enum`, `hitl-primitive-shape-enum`).

**Signatures:**

```
// REMOVED — PersonaTier now resides in harness-core (U-CORE-01); U-CP-40 imports it.
// enum PersonaTier { SOLO_DEVELOPER, TEAM_BINDING, MULTI_TENANT_COMPLIANCE }   ← strip

// PRESERVED VERBATIM — SynchronyClass, HITLPrimitiveShape, HITLMatrixCell stay
// U-CP-40-owned (no other axis declares them; carrier-map disposition: in-axis
// self-declared, clean). MCPTransport is NOT a U-CP-40 concern (U-AS-04 surface).
enum SynchronyClass { ... }                  // preserved verbatim from v2.4 body
enum HITLPrimitiveShape { ... }              // preserved verbatim from v2.4 body
record HITLMatrixCell {
  persona_tier : PersonaTier                 // re-typed — resolves to harness-core U-CORE-01
  ...                                        // all other fields preserved verbatim
}
```

**Acceptance criteria:**

1. **(v2.6 — struck.)** The former U-CP-40 acceptance criterion asserting `PersonaTier` 3-value cardinality is **struck** — that assertion now lives at U-CORE-01 acc #2 (`harness-core` plan).
2. **(v2.6 — new.)** U-CP-40 imports `PersonaTier` from `harness-core`; the persona-tier × engine-class matrix composes against the single `harness-core` nominal type — `pyright` strict resolves one nominal type across U-CP-17/25/36/40/50.
3. **(preserved verbatim.)** `SynchronyClass` / `HITLPrimitiveShape` / `HITLMatrixCell` declarations and the matrix cell-exclusion-inheritance criteria are preserved verbatim from the v2.4 body.

**Tests:** `test_persona_tier_imported_from_harness_core`; `test_persona_engine_matrix_composes_single_nominal_type`; `test_no_local_persona_tier_enum` (verifies the local enum is stripped) — plus the v2.4 `SynchronyClass`/`HITLPrimitiveShape`/`HITLMatrixCell`/matrix-exclusion tests preserved verbatim.

**Rollback boundary:** Revert the local-`PersonaTier` strip + the `[U-CORE-01]` edge. Downstream impact: the U-CP-40 / `harness-core` `PersonaTier` duplicate-declaration defect reopens. A single coherent revert.

> **Retrospective note.** U-CP-40 is **not** in the landed set (landed: U-CP-00/15/19/22) — the conversion is a forward plan edit; no source re-point owed. The hidden-coupling consumers U-CP-17 and U-CP-39 take their `PersonaTier` / `SynchronyClass` edges per §0.11.6.

---

## §3 Dependency graph

[Preserved verbatim from v2.5 in structure. v2.6 delta per §9.]

### §9 Dependency-graph delta (v2.5 → v2.6)

**§9.1 — New nodes.** **U-CP-00b** — Level 0, `Depends on: (none)`. Pure source node, beside U-CP-00 (and U-CORE-01, the latter in the `harness-core` plan). In-degree 0. No other new CP node — U-CORE-01 is the R1 product in the `harness-core` plan; CP units cite it via cross-axis import edges.

**§9.2 — New edges.**

| Edge class | Edges | Source |
|---|---|---|
| Pattern C — `[U-CP-00b]` | U-CP-01, 07, 11, 21, 31, 37, 46, 47 → U-CP-00b | §0.10 |
| Pattern E — `[U-CP-00]` | U-CP-05, 06, 09, 13, 17, 21, 23, 25, 29, 53 → U-CP-00 | §0.12 |
| Pattern D — `[U-CORE-01 (cross-axis: core)]` | U-CP-10, 13, 14, 17, 27, 29, 30, 38, 40, 41, 49, 50, 51, 52 → U-CORE-01 | §0.11.1, §2.2-revised, §2.5 (U-CP-40) |
| Pattern D — `[U-CP-00b]` (CP-owned structured shared types) | U-CP-03, 04, 05, 09, 13, 14, 27, 29, 30, 32, 43, 45, 49, 50, 51 → U-CP-00b | §0.11.2 |
| Pattern D — AS cross-axis | U-CP-04, 39 → `[U-AS-03 (cross-axis: AS)]`; U-CP-39 → `[U-AS-33 (cross-axis: AS)]`; U-CP-41 → `[U-AS-01 (cross-axis: AS)]` | §0.11.3 |
| Hidden-coupling (within-axis) | U-CP-13→28, U-CP-14→30, U-CP-27→28, U-CP-39→40, U-CP-50→30, U-CP-27→14, U-CP-44→14 | §0.11.6 |
| Cross-cluster (within-axis) | U-CP-52 → U-CP-17 (`HITLInvocation` carrier) | §0.11.5 |

> **U-CP-03 ↔ U-CP-05 order fix (operator decision D7).** No `U-CP-03 → U-CP-05` forward edge is added. `RoutingDecisionTrace` is re-homed to U-CP-00b (§0.11.2); U-CP-03 and U-CP-05 each take `[U-CP-00b]` (L0→L0, no level inversion). The v2.1 §3.2 level inversion the audit named is dissolved at its root.

**§9.3 — Acyclic invariant.**
- **U-CP-00b** is a pure source node (in-degree 0) — inbound-only edges cannot create a cycle.
- **U-CORE-01** (`harness-core`) is a pure source node — cross-axis import edges are inbound-only; no cycle.
- **`[U-CP-00]` Pattern-E edges** — U-CP-00 is a pure source node; inbound-only; no cycle.
- **Hidden-coupling edges** — all point from a consumer to a *declaring* unit; they correspond to a real consumption ordering — adding them makes the graph match reality. The one potential inversion (U-CP-03 → U-CP-05) is dissolved by the `RoutingDecisionTrace` re-home — the edge is never added.
- **Topological levels** — U-CP-00b joins U-CP-00 at L0. The Pattern-E `[U-CP-00]` consumers and the Pattern-C `[U-CP-00b]` consumers are all already at L1+ (they had non-trivial deps). **No unit changes level by v2.6** (U-CP-03 stays L0 — it now depends only on L0 source nodes). The 9-level structure (L0–L8) is preserved; L0 gains U-CP-00b.
- **Re-verification:** the v2.6 graph is a DAG; Kahn execution terminates. Acyclic invariant holds.

---

## §4 Coverage matrix

[Preserved verbatim from v2.5 in structure. v2.6 delta per §10.]

### §10 Coverage-matrix delta (v2.5 → v2.6)

| Coverage cell | At v2.5 | At v2.6 | Note |
|---|---|---|---|
| **U-CP-00b column** | n/a | U-CP-00b is a **carrier unit with no single committing contract** (§2.0b) | U-CP-00b is traced to the *aggregate* of C-CP-01 §1.4 / C-CP-03 §3.5 / C-CP-07 / C-CP-10 §10 / C-CP-18 §16 / C-CP-20 §20.4 / C-CP-21 §21.5 — it adds a column mark to each of those seven contract rows. It does **not** add a new contract row. Aggregate-citation form ratified at D3. |
| C-CP-05 §5.1 (lifecycle event taxonomy) | Covered at U-CP-10 (8-class enum + span-name map) | Covered at **U-CORE-01** (`harness-core` plan — the event-class enum) **+ U-CP-10** (the span-name map) | Multi-unit coverage of one contract — SKILL.md §4.2 permits; `Implementation_Plan_Harness_Core_v1_0.md` §4 already records this. U-CP-10's §5.1 mark is **NOT dropped** — it is *narrowed* to the span-name map; U-CORE-01 *adds* the enum-axis mark. |
| C-CP-07 §7.3 (workload-class taxonomy) | Covered at U-CP-00 (v2.5) | Unchanged — Pattern E adds `[U-CP-00]` *edges*, not coverage marks | The Pattern-E units *consume* `WorkloadClass`; they do not *cover* C-CP-07 §7.3. No coverage delta. |

**No contract row loses a mark.** Every C-CP-01…C-CP-24 row remains covered by ≥1 unit. Every plan unit column (including U-CP-00b) has ≥1 row mark. Coverage matrix completeness preserved (SKILL.md §5 step 8 / §8 step 5).

---

## §7 Revised-unit body-revision classification (SKILL.md §8 discipline)

Per `implementation-planner` SKILL.md §8, v2.6 carries **full revised bodies only where signatures actually change** and **preserved-verbatim pointers + amendment notes** where a unit's only change is a `Depends on:` / `Inputs:` line.

| Class | Treatment | Units |
|---|---|---|
| **A — new unit, full body** | Full body filed at §2.0b | **U-CP-00b** |
| **B — signature delta** (declaration stripped, field re-typed, inline-enum promoted, record carrier declared) | Signature delta resolved in-section | **U-CP-01** (§0.10 strip), **U-CP-10** (§2.2-revised — full body), **U-CP-40** (§2.5 conversion), **U-CP-14** (`AuditLedgerEntry` carrier §0.11.5), **U-CP-28/30/32/44/45/53** (§0.11.4 inline-enum promotions) |
| **C — edge-add only** (amendment note, body preserved verbatim) | §0.10 / §0.11 / §0.12 amendment-note table rows | U-CP-03, 04, 05, 06, 07, 09, 11, 13, 17, 21, 23, 25, 27, 29, 31, 33, 37, 38, 39, 41, 43, 46, 47, 49, 50, 51, 52, 53 |
| **D — preserved verbatim** (no v2.6 change) | §8 list | U-CP-00, 02, 08, 12, 15, 16, 18, 19, 20, 22, 24, 26, 34, 35, 36, 42, 48, 54, 55 |

---

## §8 Preserved-verbatim units

The following **19 units** receive **no v2.6 change** — body, signatures, acceptance criteria, tests, `Depends on`, `Inputs` all preserved verbatim from the canonical-current body (resolved through the v2.5 → v2.4 → v2.3 → v2.2 → v2.1 pointer chain):

`U-CP-00` (landed; L0), `U-CP-02`, `U-CP-08`, `U-CP-12`*, `U-CP-15` (landed), `U-CP-16`, `U-CP-18`, `U-CP-19` (landed), `U-CP-20`*, `U-CP-22` (landed; v2.5 body), `U-CP-24`, `U-CP-26`, `U-CP-34`, `U-CP-35`, `U-CP-36`, `U-CP-42`, `U-CP-48`, `U-CP-54`, `U-CP-55`.

> \* **U-CP-12 and U-CP-20 — preserved-verbatim with a propagation caveat.** Both are audit-verdict **FORK**, but FORK *only* because they transitively depend on U-CP-10 (the `LifecycleEventClass` → `WorkflowEventClass` re-type). They consume `LifecycleEventClass` value *tokens* in their acceptance-criteria text (U-CP-12 acc #4; U-CP-20 per-resumption catalog). At v2.6 transcription those token citations are re-anchored to `WorkflowEventClass` — a mechanical cross-unit notation-propagation (§0.13 D-3), not a re-decomposition. They are listed here because no *substantive* change is made.

Every other unit (the 37 in §7 Classes A/B/C) carries a v2.6 delta — full body (A), signature delta (B), or amendment note (C).

---

## §11 Permanent CP auxiliary-type-audit section

Per audit §4A.4 sub-pass 3(c): "Add a §5-style auxiliary-type audit section to the CP plan so the blind spot does not recur." This is a **permanent section** of the CP plan from v2.6 onward. It enumerates every CP-axis auxiliary type, its carrier, and its consuming units. A type at a signature position absent from this table is a materializability defect by construction.

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
| `ActorIdentity` | newtype | **U-CP-00b** (operator decision D9) | U-CP-14/27/30/49 | carrier-map "`ActorIdentity` vs IS `Actor`" |
| `AgentRole` | enum/newtype | **U-CP-00b** | U-CP-03/04/09/27/29 | C-CP-13 §13.4 |
| `ModelBinding` | record | **U-CP-00b** | U-CP-13/14/29/50 | ADR-F1 v1.2 / C-CP-13 §13.4 |
| `TraceContext` | record | **U-CP-00b** | U-CP-03 | OTel adoption / CP §8 |
| `ProviderAgnosticPayload` | record | **U-CP-00b** | U-CP-03 | ADR-F1 v1.2 / C-CP-01/02 |
| `RoutingDecisionTrace` | record | **U-CP-00b** (re-homed — operator decision D7) | U-CP-03, U-CP-05 | CP §2 layered routing |
| `MCPTrustTier` | enum | **U-CP-00b** | U-CP-43/45 | C-CP-43 gate-level |
| `Axis` | enum | **U-CP-00b** | U-CP-43 | 5-axis gate enum (plan-introduced) |
| `TailKeepPredicate` | type | **U-CP-00b** | U-CP-32/51 | CP §51 tail-keep |
| `MCPServerID` / `ToolName` / `ToolTier` | newtype | AS-owned cross-axis (operator decision D6) | U-CP-04/39/41 | C-AS-02/03 |
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
| `ParentRelation` | enum | U-CP-10 (promoted — operator decision D5) | U-CP-10 | CP §10 / ADR-D4 v1.1 |
| `AuditLedgerEntry` | record | U-CP-14 (CP-spec-owned) | U-CP-14/27/44 | C-CP-16 §16.2 / C-CP-20 |
| `OutputSchemaKind` | enum | U-CP-28 (promoted from `// {…}`) | U-CP-28 | CP §13 output-schema |
| `ParentRelationship` | enum | U-CP-32 (promoted `{ROOT,CHILD_OF,SIBLING_OF}`) | U-CP-32 | CP §15 span hierarchy |
| `OverrideKind`/`OverrideScope` | enum | U-CP-45 (promoted from `// {…}`) | U-CP-45/46 | CP §19 operator-policy |
| `ActionKind`/`ReferenceClass` | enum | U-CP-30 (promoted from `// {…}`) | U-CP-30 | CP §13.4 |
| `KeyRotationState` | enum | U-CP-44 (promoted from `// {…}`) | U-CP-44 | CP §20 key-rotation |
| `LayerOwner`/`RuntimeFault` | enum | U-CP-53 (promoted from `// {…}`) | U-CP-53 | CP §24 T-perm-3 |
| `MerkleRoot` / `F1LayerState`/`D1LayerState`/`D4LayerState` | record | self-declared (U-CP-35 / U-CP-53) | in-cone — not a finding | — |
| `*Violation` / `*Error` (conventional) | exception | per-unit inline at first-consuming unit | every `Result<_, E>` unit | `HarnessError` base; thin, no shape ambiguity |

### §11.2 Registry discipline

- A type appearing at a CP signature position **must** appear in §11.1 with a carrier and a trace before the consuming unit lands. A type at a signature position absent from §11.1 is a Pattern-C/D-class defect by construction.
- Stack/cryptographic/OTel primitives (`string`, `int`, `bytes`, `SHA256`, `ISO8601`, `JSONSchema`, `Duration`, OTel-SDK span handles) are **excluded** — no carrier needed.
- Cross-axis IS/AS types (`Actor`, `IdempotencyKey`, `FilesystemPath`, `BlastRadiusTier`, `SandboxTier`) resolve via declared `(cross-axis: …)` edges — they appear in §11.1 only where a CP unit's edge was missing.
- Future CP plan revisions **extend §11.1** — a new auxiliary type is added with its carrier in the same revision that introduces it.

---

## §[carry-forwards]

[Preserved verbatim from v2.5 → v2.4. Tension 003 RESOLVED at v2.5. v2.6 carries: the U-CP-23 `default_pattern` single-vs-dual structural mismatch (§0.8 — verbatim-axis item, separately tracked); the U-CP-43 `MCP_TRUST`/`DEPLOYMENT_SURFACE` floor spec-silence (§0.8). The §0.13 deferred coding-lane action items (D-1 U-CP-15 re-check; D-2 U-CP-10 landed-source re-point; D-3 U-CP-12/U-CP-20 token re-anchor) are bundled with the resume re-checks.]

---

## §12 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_6.md` |
| Role | `implementation-planner`, revision-pass sub-mode (`implementation-planner` SKILL.md §8) |
| Revision | v2.5 → v2.6 — CP plan materializability conformance; absorbs operator-ratified Revision R4 (`.harness/revision_R4_cp_plan.md`), the 4th of the R1–R5 carrier-map absorption sequence |
| Authored | 2026-05-15, Phase 7 sub-phase 7b |
| Entry authorization | Operator ratification 2026-05-15 — all 9 R4-relevant decisions (D3–D9 + the two propagation-gated clears) approved; Q-R4-1 … Q-R4-7 ruled per R4's defaults |
| Inputs | `.harness/revision_R4_cp_plan.md` (ratified R4 proposal); `Implementation_Plan_Control_Plane_v2_5.md` + the v2.4/v2.3/v2.2/v2.1 delta chain; `materializability_audit_cp_plan.md` (Q2); `shared_type_carrier_map.md` (T1); `xal3_resolution_recommendations.md` (T2); `Implementation_Plan_Harness_Core_v1_0.md` (applied U-CORE-01 carrier); `Spec_Control_Plane_v1_3.md` / `v1_2.md`; `implementation-planner` SKILL.md §8; `CLAUDE.md` §1.3/§3 |
| Output | CP plan v2.6: U-CP-00b new foundational carrier unit (Pattern C + CP-owned structured shared types); 8 Pattern-C dep-edges; 10 Pattern-E `[U-CP-00]` edge materializations; ~14 `[U-CORE-01]` + ~15 `[U-CP-00b]` Pattern-D edges; 3 AS cross-axis edges; 9 inline-enum promotions; 7 hidden-coupling edges; U-CP-40 + U-CP-10 declaration-site conversions; permanent §11 auxiliary-type-audit section. Unit inventory **56 → 57**. |
| Deferred action items | §0.13 D-1 (U-CP-15 `CapabilityFloor` re-check); D-2 (U-CP-10 landed-source re-point); D-3 (U-CP-12/U-CP-20 token re-anchor propagation) — all FLAGGED, not performed |
| Status | `Proposed` — promotion to `Accepted` requires Phase-7 pre-implementation re-clearance |
| Successor | R5 (OD plan revision) is the final R-series carrier-map absorption pass |

---

*End of Implementation Plan — Control Plane v2.6. Filed at Phase 7 sub-phase 7b. Absorbs the operator-ratified Revision R4 — adds foundational carrier unit U-CP-00b, materializes the Pattern C / D / E carrier-and-edge work, converts U-CP-40 and U-CP-10 from declaring to consuming sites, adds the permanent §11 auxiliary-type-audit section. Unit inventory 56 → 57. `Status: Proposed` pending pre-implementation re-clearance.*
