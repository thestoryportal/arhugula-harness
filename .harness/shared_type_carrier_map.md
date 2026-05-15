# Shared-Type Carrier Map — Pipeline Pass T1 (carrier-triage RECOMMENDATION)

*Authored 2026-05-15 by the `systems-architect` role in Phase-7 architectural-recommendation
mode (`systems-architect` SKILL.md §4A). This file is a **RECOMMENDATION**. It does not
decide and does not edit any canonical artifact. The operator ratifies the carrier map.
HARD WALL: the only file written by this pass is this file.*

## Inputs reconciled

- `.harness/verbatim_audit_as_plan.md` — AS Pattern B undeclared-type cluster
- `.harness/materializability_audit_cp_plan.md` — CP Patterns C / D / E
- `.harness/materializability_audit_od_plan.md` — OD Patterns M-1 / M-2 / M-3
- `.harness/materializability_audit_is_plan.md` — IS Pattern M-1-IS
- `design-substrate/Cross_Axis_Composition_Document_v2_1.md` §2 — 4×4 edge model;
  per-axis outbound posture (§2.4): **IS = 0 outbound** (pure foundational substrate),
  AS = 13, CP = 60, OD = 28 (consumer-most). Topological axis order IS < AS < CP < OD.

## Authority chain (CLAUDE.md §1.3)

ADR (F1–F5 + D1–D6) → ADD v1.3 → PRD v1.1 → per-axis spec v1.x → per-axis plan v2.x + CXA v2.1.
Earlier is canonical for later. A type "committed by the spec" = spec-canonical; a type the
plan introduced with no spec basis = candidate X-AL-3 design extension (route to back-flow).

## Disposition vocabulary

1. **`harness-core` resident** — genuinely cross-axis shared primitive; declared once in
   `harness-core`, all axes import. (`WorkloadClass` precedent: U-CP-00.)
2. **Per-axis-owned** — belongs to one axis; that axis declares it via a named carrier unit;
   other-axis consumers get a cross-axis edge.
3. **Cross-axis seam (CXA edge)** — already an inter-axis dependency the CXA v2.1 edge model
   covers/should cover; map to an edge.
4. **X-AL-3 design extension** — not committed by any spec/ADR; inventing it is a design
   extension. Routes to design-phase back-flow. NOT a placement decision — flagged separately.

Decision status per row: **Decided** (authority-chain-determinate) / **Proposing**
(recommendation, operator confirms) / **Open** (genuinely owed to the operator).

---

## Cross-audit reconciliation (recorded corrections)

- **`AuditPayload` / `AuditLedger` are NOT IS-exported.** The OD audit hypothesised they are
  IS-exported. The IS audit (Q4, `AuditPayload`/`AuditLedger` section) verified against IS spec
  C-IS-10 §10.1 + U-IS-17 manifest: IS exports **`StateLedgerEntry`** (the 6-field primitive)
  and the hash-chain *discipline* — there is no `AuditLedger`/`AuditPayload` record in any IS
  unit. The D5 audit-ledger *inherits* the IS entry shape and *adds* an `audit.*` namespace
  (ADR-D5 v1.3 §1.4) — it is an **OD-axis-owned** type that *composes against* the IS export.
  → `AuditPayload`/`AuditLedger` = OD-owned (disposition 2). The U-OD-30 IS cross-axis edge
  resolves to `STATE_LEDGER_ENTRY_SHAPE_EXPORT` + the hash-chain discipline, NOT to an
  `AuditLedger` type. The CP `AuditLedgerEntry` is the same family — CP-consumed, OD-owned.
- **`WorkloadClass` vs `WorkflowClass`.** `WorkloadClass` is the spec-committed CP routing
  enum (C-CP-07 §7.3), already in `harness-core` via U-CP-00. The IS audit names a
  `WorkflowClass` at U-IS-02/05 — by content this is the *same concept* (path stability
  "across runs of the same workflow class"). The plans use two spellings of one type; the
  triage treats them as **one type** and recommends the `harness-core` `WorkloadClass`
  spelling canonical (the spelling divergence is itself a verbatim item for the IS plan pass).
- **`DeploymentSurface` is already declared (AS, U-AS-04, landed)** and *also* declared
  independently at OD U-OD-01 and consumed undeclared at IS U-IS-02/05 and CP U-CP-16/17.
  Multiple independent declarations of one nominal cross-cutting enum = the exact
  no-single-carrier defect. Recommended: promote to `harness-core` (see row).

---

## Already-declared types — accounted for (no new carrier; dep-edge fixes only)

| Type | Current carrier | Status | Note |
|---|---|---|---|
| `WorkloadClass` | `harness-core`, U-CP-00 (landed) | Decided | CP Pattern E: ~10 CP units + IS U-IS-12 + OD U-OD-22 consume it with no `[U-CP-00]`/core edge. **Dep-edge fix, not a new carrier.** |
| `EngineClass` | CP, U-CP-15 (landed) | Decided | Consumed in-axis only; carrier reachable. No action. |
| `SandboxTier` / `BlastRadiusTier` | AS, U-AS-01 | Decided | CP U-CP-26 etc. consume via declared cross-axis AS edges. No action. |
| `TopologyPattern` | CP, U-CP-22 (landed) | Decided | In-axis; carrier reachable. No action. |
| `DeploymentSurface` | AS, U-AS-04 (landed) — see core-promotion row | Proposing | Re-declared at OD U-OD-01; consumed undeclared at IS U-IS-02/05, CP U-CP-16. Cross-cutting → recommend `harness-core`. |
| `PersonaTier` / `MCPTransport` | AS, U-AS-04 (landed) | Proposing | `PersonaTier` re-declared at OD U-OD-01 and CP U-CP-40; consumed sideways in CP with hidden coupling. Cross-cutting → recommend `harness-core` (see rows). |

---

## Carrier map — full triage

### Disposition 1 — `harness-core` resident (genuine cross-axis primitives)

| Type | Consumed by (units/axes) | Carrier unit / package | Consuming units needing a dep edge | Authority-chain rationale | Status |
|---|---|---|---|---|---|
| `WorkloadClass` (= IS `WorkflowClass`) | CP U-CP-05/06/09/13/17/21/23/29/+ ; IS U-IS-02/05/12; OD U-OD-22; AS U-AS-30 | `harness-core` — **existing** U-CP-00 carrier | CP Pattern-E units; IS U-IS-02/05/12; OD U-OD-22; AS U-AS-30 — all import `harness-core` | Spec-committed (C-CP-07 §7.3). Consumed by 4 axes → genuine cross-axis primitive; U-CP-00 precedent governs. | Decided |
| `DeploymentSurface` | AS U-AS-04 (decl, landed); OD U-OD-01 (re-decl); IS U-IS-02/05; CP U-CP-16/17 | `harness-core` — **new carrier unit U-CORE-01** | OD/IS/CP consumers import `harness-core` | Cross-cutting enum declared *independently twice* (AS+OD). ADD/spec commit the concept across axes; one nominal carrier required or pyright sees N distinct types. CLAUDE.md §3.3: `harness-core` hosts shared types. | Proposing |
| `PersonaTier` | AS U-AS-04 (decl, landed); OD U-OD-01 (re-decl); CP U-CP-40 (re-decl) | `harness-core` — U-CORE-01 | CP U-CP-17/25/36/50 (hidden coupling today); OD; IS if any | Same shape as `DeploymentSurface` — three independent declarations of one cross-cutting enum. | Proposing |
| `Actor` / `ActorIdentity` / `ActionID` / `IdempotencyKey` family | IS-exported (`Actor`, `IdempotencyKey` via U-IS-07/08); CP U-CP-14/27/30/34/49 consume `ActorIdentity`/`ActionID` | `harness-core` for the identity-newtype aliases (`ActionID`, `EntryID`, `WorkflowID`, `StepID`, `ThreadID`, `UnitId`); `Actor`/`IdempotencyKey` stay IS-exported | CP units add `harness-core` import OR cross-axis IS edge for the F2 shape | Identity aliases are thin string-newtypes used cross-axis; consolidating them in `harness-core` avoids per-plan re-declaration. The structured `Actor` stays IS (F2 primitive). | Proposing |

**Note on identity aliases.** `ActionID`/`EntryID`/`WorkflowID`/`StepID`/`ThreadID`/`UnitId`/
`ContractID` (CP Pattern D tail; IS `UnitId`/`ContractID` tail; OD has its own tail) are
thin `str`-newtypes with no shape ambiguity. The recommendation is a **single `harness-core`
identity-alias module** (one carrier unit U-CORE-01) so all four axes import one set —
this is cleaner than the per-plan "inline-materialization discipline" the audits floated,
because these aliases are demonstrably consumed by ≥3 axes. Operator may instead ratify
per-axis inline materialization; flagged **Proposing**.

### Disposition 2 — per-axis-owned (one owning axis; carrier unit + cross-axis edges)

| Type | Consumed by (units/axes) | Owning axis / carrier unit | Consuming units needing a dep edge | Authority-chain rationale | Status |
|---|---|---|---|---|---|
| `AttributeValueType` / `Cardinality` | CP U-CP-01 (decl); CP U-CP-07/11/21/31/37/46/47 (consume) | **CP** — declared at U-CP-01; recommend re-home to a new CP foundational unit **U-CP-00b** (or keep at U-CP-01) | CP U-CP-07/11/21/31/37/46/47 add `Depends on: [carrier]` | Plan-introduced CP auxiliary enums (CP audit Findings-rejected #4: explicitly NOT OTel-SDK types — U-CP-01 declares plan-invented value sets). All consumers in-axis → per-axis, not core. | Decided |
| `AuditPayload` / `AuditLedger` | OD U-OD-30 | **OD** — new OD carrier unit (audit-ledger schema) | — (OD-internal) | Reconciliation above: D5 audit-ledger inherits IS `StateLedgerEntry` + adds `audit.*`; the *record* is OD-owned. IS edge is to the entry shape only. | Decided |
| `AuditLedgerEntry` | CP U-CP-14/27/44 | **OD** (same family as `AuditLedger`) — OD carrier; CP gets a cross-axis OD→CP edge **inverted reading** — see CXA-seam section | CP U-CP-14/27/44 need a cross-axis edge to the OD audit-ledger carrier | The audit ledger is OD-axis (ADR-D1/D4/D5). CP emitting audit entries composes against the OD schema. | Open — see CXA seam note |
| `SpanRef` / `ChildSpanRef` / `SpanAttributes` / `EventEmission` | OD U-OD-09/10/19/20/23/25/26/30/31 | **OD** if harness abstractions — new OD carrier (likely at U-OD-04, the OTel base-layer anchor) | OD consumers add `Depends on: [U-OD-04]` | OD audit §4A.4: if these are harness abstractions they belong at U-OD-04. If thin OTel-SDK aliases, also U-OD-04 as a type-alias line. Either way **OD-owned, not core** — no other axis consumes them. | Proposing |
| `DashboardRef` / `DashboardQuery` / `SpanRow` / `EvictionAction` / `HusainLoopState` / `CardinalityCounters` | OD U-OD-22/24/27/31 | **OD** — declare at first-consuming OD unit | OD-internal | OD-axis observability primitives; single-axis consumption. Faithful factor-outs of OD spec content. | Proposing |
| `ToolMetadata` | AS U-AS-06 | **AS** — carrier in U-AS-06 or an AS foundational unit | AS-internal | AS audit §4A.4 flags as *likely design extension* candidate — see X-AL-3 section. If factor-out: AS-owned. | Open |
| `RawContractInput` | AS U-AS-07 | **AS** — carrier in U-AS-07 | AS-internal | AS tool-contract registration input. Likely AS factor-out. | Proposing |
| `SecretScope` (ellipsis body) / `SecretAllowlistEntry` | AS U-AS-20 decl (ellipsis); U-AS-22/24/26/27/30 consume; `SecretAllowlistEntry` decl U-AS-22 consumed by U-AS-07 (carrier-ordering) | **AS** — U-AS-20 / U-AS-22 | AS U-AS-07 carrier-ordering fix (declare interim shape, or move U-AS-22 ahead) | AS-axis secret types; in-axis. Defect is field-set-deferral + graph ordering, not placement. | Decided (AS-owned) |
| `AnchorCitation` | AS U-AS-28 | **AS** — carrier in U-AS-28 | AS-internal | AS Anthropic-primitive anchor citation. AS factor-out. | Proposing |
| `ExtendedThinkingEffort` / `BatchApiCell` / `WorkloadManifestOverrides` | AS U-AS-30 | **AS** — carrier in U-AS-30 | AS-internal | AS workload-binding types. `WorkloadManifestOverrides` flagged design-extension candidate — see X-AL-3. | Open (`WorkloadManifestOverrides`) / Proposing (others) |
| `Provider` / `ModelClass` | AS U-AS-30 (`C6_CROSS_FAMILY_FALLBACK_CHAIN`); CP `ProviderFamily` adjacent | **AS** for AS-30 use; CP declares `ProviderFamily`/`ProviderCandidate` itself (U-CP-09, in-cone) | AS-internal | Provider/model identity. AS-owned for the AS-30 fallback chain; CP's own provider types are self-declared and clean. | Proposing |
| `AgentRole` / `ModelBinding` / `StepID` / `TraceContext` / `ProviderAgnosticPayload` | CP U-CP-03/04/09/13/14/27/29/50 | **CP** — new CP foundational shared-types unit **U-CP-00b** | CP consumers add `Depends on: [U-CP-00b]` | CP-axis routing/workflow primitives; all in-axis consumption. `ModelBinding`/`TraceContext`/`ProviderAgnosticPayload` are structured — design-extension candidates (X-AL-3 section). | Open (structured) / Proposing (`AgentRole`, `StepID`) |
| `MCPTrustTier` / `Axis` / `TailKeepPredicate` | CP U-CP-43/45/32/51 | **CP** — U-CP-00b or declaring unit | CP-internal | CP gate-level composition primitives. `Axis` is the 5-axis gate enum — plan-introduced; CP-owned. | Proposing |
| Inline-comment enums: `OverrideKind` / `OverrideScope` / `OutputSchemaKind` / `ParentRelationship` / `ReferenceClass` / `KeyRotationState` / `ActionKind` / `LayerOwner` / `RuntimeFault` | CP U-CP-28/30/32/45/53 | **CP** — promote the `// {…}` comment to a real `enum` in the declaring unit | CP-internal | Value sets already stated in plan comments → faithful factor-outs; promotion is mechanical, plan-internal. | Decided |
| Error types (~24 OD + CP `*Violation`/`*Error`) | every OD/CP unit with `Result<_, E>` | **per-axis** — inline at first-consuming unit, sanctioned by a one-line plan note | none (inline) | Conventionally thin (`class XViolation(HarnessError)`); no shape ambiguity. Per AS/OD audits — inline-materialization discipline. | Decided |
| `ResidenceContract` / git-domain `GitRepository`/`CommitRange`/`CommitId` | IS U-IS-01/06 | **IS** — inline at declaring unit; git types pending stack-primitive-vs-abstraction call | IS-internal | IS-axis tails. Git types: operator classifies (stack-primitive of a git library → exclude; harness abstraction → IS carrier). | Open (git trio) / Decided (`ResidenceContract` inline) |

### Disposition 3 — cross-axis seam (CXA edge)

| Type | Edge | CXA v2.1 coverage | Status |
|---|---|---|---|
| `WorkloadClass` at OD U-OD-22 | OD → CP (or OD → core) | §2.3.6 OD→CP bucket (12 edges) covers OD→CP; if `WorkloadClass` lands in `harness-core` no CXA edge is needed (core import, not a cross-axis `Depends on`). **Recommended: core import.** | Proposing |
| `AuditLedgerEntry` consumed by CP, owned by OD | CP → OD | **NOT covered.** CXA §2.1 matrix has CP→OD = **0** (CP is upstream of OD; OD consumes CP, not vice versa). A CP→OD edge would invert the IS<AS<CP<OD topological order. → This is a genuine architectural fork — see X-AL-3 / open-items. | Open |
| `WorkflowEvent` at IS U-IS-14 | IS would need IS → CP | **FORECLOSED.** CXA §2.4: IS = 0 outbound edges by architecture. IS cannot take a cross-axis edge. → resolve via `harness-core` or back-flow, not a CXA edge. | Open — see X-AL-3 section |
| `SecretRef` consumed by CP U-CP-44, produced by AS `fetch_secret` (U-AS-20) | CP → AS | §2.3.3 CP→AS bucket (24 edges) covers CP→AS. But AS plan does not export a *named* `SecretRef` carrier — the AS U-AS-20 `SecretScope` ellipsis-body defect blocks the seam. Edge exists in the bucket; the *exported type* must be named once AS-20 declares it. | Proposing |

### Disposition 4 — X-AL-3 design-extension candidates (BLOCK until back-flow) — flagged separately below

See dedicated section. These are NOT placement decisions.

### CP Pattern D — per-type triage (full enumeration)

The CP audit's Pattern D table names ≥25 distinct types. The headline structured types are
triaged in the rows above and the X-AL-3 section. This table places **every remaining**
Pattern D type so the operator ratifies per-type, not per-cluster. Disposition column:
1 = `harness-core`, 2 = per-axis carrier, 4 = X-AL-3 candidate (blocks).

| Type | Consuming CP unit(s) | Disposition | Carrier / target | Rationale | Status |
|---|---|---|---|---|---|
| `MCPServerID` | U-CP-39 | 2 — AS-owned | AS (MCP integration §); CP gets a cross-axis AS edge, or `harness-core` identity alias | AS-domain MCP identity; thin alias. AS spec C-AS-02 MCP § + U-AS-33 export. | Proposing |
| `ToolName` | U-CP-04/39 | 2 — AS-owned | AS; cross-axis AS edge or `harness-core` alias | AS tool-contract identity; thin alias. | Proposing |
| `ToolTier` | U-CP-41 | 2 — AS-owned | AS (`SandboxTier`/blast-radius family, U-AS-01) | AS sandbox-tier-adjacent; likely the AS `BlastRadiusTier`/tier vocabulary. | Proposing |
| `StageID` | U-CP-29 | 1 — identity alias | `harness-core` U-CORE-01 | `str`-newtype, same family as `StepID`/`ThreadID`. | Proposing |
| `Cell` | U-CP-41 | 2 — CP-owned | CP U-CP-00b or U-CP-40 (HITL matrix cell) | CP HITL-matrix cell; CP-axis concept. May be the `HITLMatrixCell` already self-declared at U-CP-40. | Proposing |
| `ReferenceToUnit` | U-CP-41 | 1 — identity alias | `harness-core` U-CORE-01 (`UnitId` family) | Thin unit-ID reference alias. | Proposing |
| `VerifierResult` | U-CP-41 | 4 — X-AL-3 candidate | CP spec § (verifier) | Structured result type, field set nowhere specified. | Open |
| `OverlayResolution` | U-CP-41 | 4 — X-AL-3 candidate | CP spec § (persona-tier binding) | Structured type, no spec field set. | Open |
| `WebhookConfig` / `WebhookPayload` | U-CP-52 | 4 — X-AL-3 candidate | CP spec § (webhook delivery) | Structured types, field set nowhere specified. | Open |
| `HITLInvocation` | U-CP-52 | 4 — X-AL-3 candidate | CP spec § HITL | Structured HITL-invocation record, no spec field set. | Open |
| `LeadAgentPlan` | U-CP-33 | 4 — X-AL-3 candidate | CP spec § (cache warmup / topology) | Structured plan record, no spec field set. | Open |
| `SubAgent` | U-CP-33 | 2 — CP-owned (likely factor-out) | CP carrier (sub-agent topology unit) | CP sub-agent topology concept; CP spec § topology. Confirm factor-out. | Proposing |
| `CacheWarmupResult` | U-CP-33 | 2 — CP-owned | CP U-CP-33 (declare in-unit) | Function return type; CP-axis. Likely thin result record — factor-out. | Proposing |
| `Span` | U-CP-51 | 2 — OD-owned (OTel/observability) | OD `SpanRef`-family carrier; CP cross-axis OD-direction — see note | Observability span handle; same family as OD `SpanRef`. CP→OD is foreclosed (CXA matrix) — if CP needs a real OD `Span`, it folds into the `AuditLedgerEntry` CP→OD fork. If it is an OTel-SDK primitive, exclude. | Open |
| `FailedAttempt` / `Alternative` / `RetryHistory` | U-CP-30 | 4 — X-AL-3 candidate | CP spec § (handoff / retry) | Structured handoff-context records, field set nowhere specified. | Open |
| `EngineClassPreferences` | U-CP-27 | 2 — CP-owned | CP carrier (engine-class unit, U-CP-15 family) | CP engine-class preference record; CP-axis. Likely factor-out of §7.4 engine content. | Proposing |
| `GateOverride` | U-CP-27 | 2 — CP-owned | CP carrier (gate-level unit, U-CP-43 family) | CP gate-level override; CP-axis. Factor-out of gate-level spec. | Proposing |
| `CurrentState` | U-CP-30/50 | 4 — X-AL-3 candidate | CP spec § (workflow state / summarization) | Structured state-summary record, no spec field set. | Open |
| `ExternalReference` | U-CP-30/50 | 2 — CP-owned | CP U-CP-30 (declared in-unit per CP audit) | CP audit notes `ExternalReference` self-declared at U-CP-30 — carrier exists; consumers (U-CP-50) need the dep edge. | Decided |
| `KeyRotationState` | U-CP-44 | 2 — CP-owned (inline enum) | CP U-CP-44 — promote `// {…}` comment to `enum` | Inline-comment-only enum; value set already stated. Mechanical promotion. | Decided |
| `RewrittenToolCall` | U-CP-39 | 2 — CP-owned | CP U-CP-39 (declare in-unit) | Function return type; CP-axis. Likely thin factor-out. | Proposing |
| `RoleRoutingBinding` / `WorkloadRoutingOverride` / `RetryPolicy` | U-CP-04 | 2 — CP-owned (likely) / 4 (`RetryPolicy` if structured) | CP carrier (routing-manifest unit) | CP routing-manifest sub-records. `RoleRoutingBinding`/`WorkloadRoutingOverride` are routing factor-outs; `RetryPolicy` field set should be confirmed against CP spec §retry. | Open (`RetryPolicy`) / Proposing (others) |
| `RoutingDecisionTrace` | U-CP-03 (consumed), U-CP-05 (declared) | 2 — CP-owned | CP U-CP-05 (carrier exists) | Hidden-coupling: U-CP-03 consumes a type U-CP-05 declares downstream. Carrier exists — dep-graph completion, not a new carrier. | Decided |

**Note on `ActorIdentity` vs IS `Actor`.** CP's `ActorIdentity` (U-CP-14/27/30/49) is **not**
the IS-exported `Actor` (U-IS-07, the F2 state-ledger primitive). Per CP audit
Findings-rejected #9: at the F2-shaped consumers (U-CP-34/35) the `actor` field resolves to
the IS `Actor` type via the declared cross-axis IS edge — no CP carrier needed there. At the
non-F2 consumers (U-CP-14/27/30/49) `ActorIdentity` is a genuinely separate CP-axis identity
alias with no carrier — it needs a `harness-core` identity-alias placement (disposition 1,
U-CORE-01) OR a CP carrier. Recommended: `harness-core` alias, consistent with the other
identity newtypes. **Status: Proposing.**

---

## X-AL-3 design-extension section — the serious findings

These types are consumed at signature positions but may not be committed by any spec/ADR.
Inventing them is a silent H_T design extension (CLAUDE.md I-2 / X-AL-3). Each **blocks the
affected units until the operator either (a) confirms a spec basis exists → it is a
factor-out, re-route to disposition 1/2, or (b) routes to design-phase back-flow** to amend
the named spec before the plan revision proceeds.

| Type | Axis / units | Why a candidate extension | Back-flow target if confirmed | Status |
|---|---|---|---|---|
| `WorkflowEvent` | IS U-IS-14 | A CP/engine lifecycle event type consumed at an IS signature. IS is consumer-most-upstream (0 outbound edges) — it *cannot* legitimately consume a CP type via an edge. Either (a) IS spec §ledger commits a workflow-event input → factor-out to `harness-core`; (b) plan invented it → IS-spec back-flow; (c) IS genuinely must consume a CP type → contradicts the CXA "IS=0 outbound" invariant → **CXA / ADD revision**. | IS spec (`Spec_Information_Substrate_v1`) OR CXA v2.1 / ADD v1.3 if reading (c) | **Open — Class 1 halt** |
| `WorkflowClass` / `DeploymentSurface` at IS | IS U-IS-02/05/12 | Same architectural shape as `WorkflowEvent`: IS consuming CP/cross-cutting types with no addable edge. Strongly indicated to be `harness-core` primitives (IS spec §1 *presumes* "workflow class"/"deployment surface" semantically) → factor-out, disposition 1. But if the IS spec is ruled genuinely silent on them *as IS types*, it is an extension. | IS spec §1 (confirm semantic commitment) — most likely a factor-out, **not** a true extension | Proposing (likely factor-out) |
| `AuditLedgerEntry` consumed by CP | CP U-CP-14/27/44 | CP emitting audit entries needs the OD-owned audit-ledger schema, but CP→OD is a foreclosed direction (CXA matrix CP→OD = 0). Either CP composes against an IS-exported entry shape (the F2 `StateLedgerEntry` — already an IS export CP consumes) and `AuditLedgerEntry` is just CP's local F2-shaped record (→ disposition 2, CP-owned, clean — cf. CP audit Findings-rejected #9 for U-CP-34/35), OR the audit-ledger is genuinely a distinct OD schema CP must reference → architectural fork. | If CP's `AuditLedgerEntry` ≠ F2 shape: CXA v2.1 (new CP→OD edge or re-home audit schema) | **Open — Class 1 halt** |
| `ToolMetadata` | AS U-AS-06 | Structured type whose field set is nowhere in `Spec_Action_Surface` §2/§3. AS audit §4A.4 names it a design-extension candidate. | AS spec C-AS-02 / §3 | **Open** |
| `TaintState` / `MCPServer` | AS U-AS-08/14 | `TaintState` (a `CallSiteContext` field) and `MCPServer` have no spec-enumerated field set. AS audit §4A.4 design-extension candidates. | AS spec C-AS-02 (MCP integration §) | **Open** |
| `WorkloadManifestOverrides` | AS U-AS-30 | Structured override record with no spec field set; AS audit §4A.4 candidate. | AS spec §13 | **Open** |
| `ModelBinding` / `TraceContext` / `ProviderAgnosticPayload` / `ProposedAction` / `MaterialDiff` / `ParentRelation` | CP U-CP-03/10/13/30/49/50 | Structured CP types whose field set is nowhere specified (CP audit §4A.2: "structured types whose field set is nowhere specified — route to spec back-flow"). `ParentRelation` (U-CP-10) has no §5.1 basis (fork-queue item 16). | CP spec `Spec_Control_Plane_v1_3` (§3 routing, §5 lifecycle) | **Open — Class 1 halt** |
| `VerifierResult` / `OverlayResolution` / `WebhookConfig` / `WebhookPayload` / `HITLInvocation` / `LeadAgentPlan` / `FailedAttempt` / `Alternative` / `RetryHistory` / `CurrentState` / `RetryPolicy` | CP U-CP-04/30/33/41/52 | CP Pattern D tail structured types (see CP Pattern D per-type table) — field set nowhere in `Spec_Control_Plane`. Same cluster, same back-flow shape as the headline CP structured types. | CP spec `Spec_Control_Plane_v1_3` (§ handoff / retry / HITL / webhook) | **Open — Class 1 halt** |
| `SpanRef` / `SpanAttributes` / `EventEmission` (if ruled harness abstractions with no spec basis) | OD U-OD-09/+ | If the operator rules these harness-introduced abstractions (not OTel-SDK aliases) AND the OD spec does not sanction them, they are extensions. If OTel-SDK aliases, NOT extensions (disposition 2, alias at U-OD-04). | OD spec `Spec_Operational_Discipline_v1_3` §15 | **Open** (pending OTel-alias-vs-abstraction call) |

**Operator action for the X-AL-3 set:** for each, decide factor-out (re-route to disposition
1/2) vs genuine extension (back-flow to the named spec/CXA/ADD). The two **Class-1-halt**
rows are `WorkflowEvent`+IS-`WorkflowClass`/`DeploymentSurface` (foreclosed-edge) and the CP
structured-type cluster + `AuditLedgerEntry` (foreclosed CP→OD direction). These genuinely
cannot be resolved by reading the authority chain alone — they are design gaps, not tensions.

---

## Carrier-unit gap section — new foundational units the per-axis revisions must add

| New unit | Axis | Hosts | Precedent | Status |
|---|---|---|---|---|
| **U-CORE-01** | `harness-core` | Cross-cutting enums + identity aliases: `DeploymentSurface`, `PersonaTier`, and the `str`-newtype identity module (`ActionID`, `EntryID`, `WorkflowID`, `StepID`, `ThreadID`, `UnitId`, `ContractID`) | Mirrors U-CP-00 (`WorkloadClass` → `harness-core`) | Proposing |
| **U-CP-00b** | CP | CP foundational shared-types: `AttributeValueType`, `Cardinality`, `AgentRole`, `StepID`-ref, `MCPTrustTier`, `Axis`, `TailKeepPredicate` (the CP Pattern-C/D in-axis auxiliary types). May be merged into U-CP-00. | U-CP-00 | Proposing |
| **New OD carrier unit(s)** | OD | OD audit-ledger schema (`AuditPayload`/`AuditLedger`); the `SpanRef`-family + dashboard/eval primitives at/near U-OD-04 | — | Proposing |
| AS: no new unit — carriers added in-place | AS | `ToolMetadata`/`RawContractInput`/`AnchorCitation`/`SecretScope` field-set/`Provider`/`ModelClass`/AS-30 types declared in their first-consuming AS units; carrier-ordering fix for `SecretAllowlistEntry` | — | Proposing |
| IS: no new unit — carriers added in-place / via `harness-core` import | IS | `ResidenceContract`/`ContractID`/`UnitId` inline or via U-CORE-01; M-1-IS types via `harness-core` import | — | Proposing |

`harness-core` package exists on disk (`harness-core/` with `src`, `tests`, `pyproject.toml`)
but has **no `CLAUDE.md`** and currently only the landed U-CP-00 `WorkloadClass`. U-CORE-01 is
the second `harness-core` unit.

---

## Recommended ordering for the four per-axis `implementation-planner` revision passes

The carrier dependencies impose an order. `harness-core` is foundational for all four axes
(CXA §2.4: IS anchors, OD terminates; topological IS < AS < CP < OD).

1. **`harness-core` first — ratify + add U-CORE-01.** `DeploymentSurface`, `PersonaTier`,
   identity aliases must exist in `harness-core` before any axis pass can cite them. This is
   a prerequisite, not a per-axis pass. Operator ratifies the disposition-1 rows first.
2. **IS plan revision pass (second).** IS is consumer-most-upstream and its M-1-IS cluster is
   *entirely* `harness-core`-import work once U-CORE-01 exists (`WorkloadClass`,
   `DeploymentSurface`). IS is small (17 units), cleanest axis, and unblocks nothing
   downstream by waiting — but doing it second confirms the `harness-core` shapes against the
   most-upstream consumer before AS/CP/OD pile on. The `WorkflowEvent` X-AL-3 fork must be
   resolved before this pass lands.
3. **AS plan revision pass (third).** AS consumes only IS + `harness-core`. Its Pattern-B
   carriers are mostly AS-internal; resolve the AS X-AL-3 set (`ToolMetadata`/`TaintState`/
   `MCPServer`/`WorkloadManifestOverrides`) before landing. AS exports `SecretScope` — must
   land before CP's `SecretRef` seam (CP U-CP-44) can resolve.
4. **CP plan revision pass (fourth).** CP consumes IS + AS + `harness-core`. Largest cluster
   (Patterns C/D/E, 56 units). Needs U-CP-00b. The CP structured-type X-AL-3 set
   (`ModelBinding`/`TraceContext`/`ProposedAction`/`ParentRelation`/`MaterialDiff`) and the
   `AuditLedgerEntry` CP→OD foreclosed-direction fork must be resolved first.
5. **OD plan revision pass (last).** OD is consumer-most (consumes IS+AS+CP). Its
   `AuditPayload`/`AuditLedger` carrier and `SpanRef`-family must be settled; the CP
   `AuditLedgerEntry` fork (step 4) and OD's own audit-ledger carrier must be reconciled
   together — recommend the CP and OD passes be **coordinated** on the audit-ledger seam.

**Rationale:** `harness-core` → IS → AS → CP → OD follows the CXA §2.2 axis topological order
(IS < AS < CP < OD), so each pass cites only already-revised upstream carriers. The two
foreclosed-edge X-AL-3 forks (`WorkflowEvent`/IS; `AuditLedgerEntry`/CP→OD) are the gating
items — they must be operator-resolved before steps 2 and 4 respectively.

---

## Summary counts (recommendation)

- **Distinct undeclared types triaged:** ~62 (full CP Pattern D enumeration included;
  excluding the ~24 thin `*Violation`/`*Error` types handled as one inline-materialization
  class, and excluding stack/OTel primitives).
- **Disposition 1 (`harness-core`):** `WorkloadClass`/`WorkflowClass` (existing),
  `DeploymentSurface`, `PersonaTier`, the identity-alias module (`ActionID`/`EntryID`/
  `WorkflowID`/`StepID`/`ThreadID`/`UnitId`/`ContractID`) — ~9 types.
- **Disposition 2 (per-axis-owned):** ~22 types — AS (`ToolMetadata`*, `RawContractInput`,
  `AnchorCitation`, `SecretScope`, `SecretAllowlistEntry`, `Provider`, `ModelClass`, AS-30
  set), CP (`AttributeValueType`/`Cardinality`, `AgentRole`, `MCPTrustTier`, `Axis`,
  `TailKeepPredicate`, inline-comment enums), OD (`AuditPayload`/`AuditLedger`,
  `SpanRef`-family, dashboard/eval primitives). (* also X-AL-3 candidate.)
- **Disposition 3 (CXA seam):** `SecretRef` (CP→AS, edge exists); `WorkloadClass`@OD-22
  (resolves via core import). 2 rows.
- **Disposition 4 (X-AL-3 design extensions — BLOCKING):** ~24 candidate types — AS
  (`ToolMetadata`, `TaintState`, `MCPServer`, `WorkloadManifestOverrides`); IS
  (`WorkflowEvent`; `WorkflowClass`/`DeploymentSurface` likely factor-out); CP headline
  cluster (`ModelBinding`/`TraceContext`/`ProviderAgnosticPayload`/`ProposedAction`/
  `MaterialDiff`/`ParentRelation`) + CP Pattern-D tail (`VerifierResult`/`OverlayResolution`/
  `WebhookConfig`/`WebhookPayload`/`HITLInvocation`/`LeadAgentPlan`/`FailedAttempt`/
  `Alternative`/`RetryHistory`/`CurrentState`/`RetryPolicy`); `AuditLedgerEntry`. **Two are
  Class-1 halts:** `WorkflowEvent`+IS-cross-axis-types (foreclosed IS-outbound-edge) and the
  CP structured-type cluster + `AuditLedgerEntry` (foreclosed CP→OD direction).
- **New carrier units recommended:** U-CORE-01 (`harness-core`), U-CP-00b (CP), 1–2 new OD
  carrier units (audit-ledger + span-family). AS and IS add carriers in-place.

*End of recommendation. The operator decides. Ratification of the disposition-1 rows +
U-CORE-01 is the prerequisite for all four per-axis revision passes.*
