# Materializability Audit — Control Plane Implementation Plan (U-CP-00 – U-CP-55)

## Summary

- Mode: Phase-7 pre-implementation review (per `harness-adversarial-reviewer` SKILL.md §"Phase-7 pre-implementation review mode"), review-ahead pipeline pass **Q2**. Plan-wide **SYSTEMIC MATERIALIZABILITY audit** of the entire CP-axis plan — distinct from the §4A `verbatim_audit_cp_plan.md` pass, which checked only **verbatim conformance** (does a plan signature transcribe its cited spec section). This pass checks the second axis: **materializability** — can a coding agent build the unit, pyright-strict-clean, at its position in the topological order, given the canonical-current v2.5 body actually in force.
- Corpus reviewed:
  - `design-substrate/Implementation_Plan_Control_Plane_v2_5.md` — delta file; U-CP-00 (new), U-CP-22 (re-revised); §0.5 deferred-edge declaration
  - `design-substrate/Implementation_Plan_Control_Plane_v2_4.md` — canonical-current bodies for the §4A verbatim cluster: U-CP-01, U-CP-10, U-CP-12, U-CP-19, U-CP-22, U-CP-23, U-CP-43, U-CP-46, U-CP-47, U-CP-48
  - `design-substrate/Implementation_Plan_Control_Plane_v2_3.md` — canonical-current bodies for U-CP-07, U-CP-12
  - `design-substrate/Implementation_Plan_Control_Plane_v2_2.md` — canonical-current bodies for U-CP-20, U-CP-21, U-CP-55
  - `design-substrate/Implementation_Plan_Control_Plane_v2_1.md` — canonical-current bodies for all other units (U-CP-02–06, 08–09, 11, 13–18, 24–42, 44–45, 49–54)
  - `design-substrate/Spec_Control_Plane_v1_3.md` (§3.5/§9.1 amendments) + `Spec_Control_Plane_v1_2.md` (§1–§24 preserved-verbatim contracts; §1.4 routing table, §7.3 workload-class, §20.4 audit table spot-verified)
  - `.harness/verbatim_audit_cp_plan.md` — §4A precedent (verbatim axis; referenced, not re-derived)
  - `.harness/verbatim_audit_as_plan.md` — Q1 systemic-audit precedent (report-shape contract; Pattern A / Pattern B framing)
  - `.harness/pipeline-fork-queue.md` items 16–18 — CP materializability forks the coding lane already found (folded by reference, not re-derived)
- Date: 2026-05-15
- Finding count by §4.1 review-severity class: **Class 3: 4 · Class 2: 3 · Class 1: 1** — counted **per systemic pattern**, not per unit (the AS Q1 audit counted per-unit; CP's defect is structural — Pattern C touches 7 units as one finding, Pattern D ≥20 units as one finding — so a per-unit count would read ~24 Class-3 and mislead a direct comparison to AS's 11/4/2; the per-pattern count is the honest aggregation here).
- **Bottom-line:** of 56 CP units (U-CP-00 added at v2.5; U-CP-01–U-CP-55), **20 CLEARED** (materializable as written), **12 CONFORM** (authority-chain-determinate dependency-graph fix — Pattern C / Pattern E mechanical edge work; clears once the single `implementation-planner` revision-pass applies), **24 FORK** (operator decision needed).

### Class-taxonomy disambiguation (per SKILL.md title-section)

Per-unit severity below is the **§4.1 review-severity** scale (Class 1 minor / Class 2 moderate / Class 3 severe — phase re-opening). Each materializability-blocking unit's *disposition* is a **§2.7.6 Phase-7 execution fork**; the §2.7.6 fork class is stated per row. A §4.1 Class 3 review finding here ≠ a §2.7.6 Class 3 (informational) fork.

### Relationship to the §4A verbatim audit

The §4A `verbatim_audit_cp_plan.md` audit flagged 7 verbatim-divergence units (U-CP-01, 10, 19, 22, 43, 46, 47); the operator ratified conform-to-spec; v2.4 conformed them and v2.5 resolved U-CP-22's `WorkloadClass` dependency. **Those verbatim divergences are NOT re-litigated here** — they are off the table at the v2.5 canonical body. This pass audits a distinct axis the §4A mandate explicitly did not cover (`pipeline-fork-queue.md` "Pattern — the materializability axis spans all four plans"): does every type at a signature position have a reachable carrier, and does every signature have a complete spec basis. The §4A audit's CLEARED verdicts meant "no verbatim divergence", NOT "ready to land" — this pass supplies the missing materializability verdict.

---

## Method

For every unit U-CP-00 – U-CP-55, three checks were applied against the canonical-current body (resolved through the v2.5 → v2.4 → v2.3 → v2.2 → v2.1 "preserved verbatim" pointer chain):

1. **Undeclared-type / carrier check.** Every type/enum/record at a typed signature position (record fields, function params/returns, `const` element types) was checked for a declaring carrier (`enum`/`record` declaration in some unit's Signatures block) AND for that carrier being inside the consuming unit's `Depends on` cone. Landed foundational types: `WorkloadClass` (U-CP-00), `EngineClass` (U-CP-15), `TopologyPattern`+`CascadePolicy` (U-CP-22), `ResumptionKind` (U-CP-19). Cross-axis types carried by IS/AS plans via declared `(cross-axis: …)` edges resolve in-cone and are NOT undeclared.

2. **Shared-type no-carrier check.** Where multiple units consume the same auxiliary type, the audit checked for ONE carrier unit + a `Depends on` edge from every consumer. Multiple independent re-declarations of the same nominal type, or a single declaration with no dep edge from sideways consumers, is a defect — pyright treats nominally-distinct declarations as distinct types, breaking cross-unit composition. This is the `WorkloadClass`→U-CP-00 shape.

3. **Signature-vs-spec completeness.** Each unit's signature was checked for fields/params with NO basis in the cited spec section, and for acceptance criteria claiming "per §X verbatim" for a field §X does not define.

Dependency-graph completeness (hidden coupling) was checked across the whole graph.

**Stack-primitive exclusion list (FM-D self-check; mirrors `verbatim_audit_as_plan.md` Findings-rejected #4).** The following are treated as stack / language / cryptographic primitives and need NO plan carrier: `string`, `int`, `float`, `bool`, `bytes`, `List<>`, `Set<>`, `Map<>`, `Optional<>`, `Result<>`, `Duration`, `SHA256` (hash digest primitive), `ISO8601` (timestamp primitive), `JSONSchema`. Mechanical "every type is a finding" application was avoided.

---

## Fork inventory table — Pattern C: schema-attribute utility types declared inside U-CP-01, consumed sideways with no carrier edge

This is the **shared-type-no-carrier** shape — the WorkloadClass→U-CP-00 / Tension-003 shape, recurring across the namespace-schema units. `pipeline-fork-queue.md` items 17 + 18 are the seed; this plan-wide sweep confirms and extends them.

`AttributeValueType` and `Cardinality` are declared **only** inside U-CP-01's Signatures fenced block (v2.1 lines 257–258; carried verbatim to the v2.4-conformed body lines 175–176):

```
enum AttributeValueType { STRING, INT, FLOAT, BOOL, ENUM_REF }
enum Cardinality { LOW, MEDIUM, HIGH, PER_REQUEST }
```

They are then consumed at typed `record` field positions across **six other units** that declare a `…AttributeSchema` record — with **no `Depends on` edge to U-CP-01** at any of them:

| Consuming unit | Consumption site | `Depends on` (canonical-current) | Edge to U-CP-01? |
|---|---|---|---|
| **U-CP-07** | `FallbackAttributeSchema`/`HarnessBreakerAttributeSchema`/`RetryAttributeSchema` `.value_type`,`.cardinality` | `(none)` | **NO** |
| **U-CP-11** | `LeaseAttributeSchema.value_type`,`.cardinality` | `(none)` | **NO** |
| **U-CP-21** | `EngineAttributeSchema.value_type`,`.cardinality` | `[U-CP-15]` | **NO** |
| **U-CP-31** | `TopologyAttributeSchema`/`SubAgentAttributeSchema` `.value_type`,`.cardinality` | `[U-CP-22, U-CP-15]` | **NO** |
| **U-CP-46** | `AuditAttributeSchema`/`Validator…`/`HITLSpan…` `.value_type`,`.cardinality` (v2.4 body) | `[U-CP-37,38,42,43,44,45,47]` | **NO** |
| **U-CP-47** | `ValidatorFailAttributeSchema.value_type`,`.cardinality` | `[U-AS-03]` | **NO** |

**This IS the WorkloadClass shape.** `AttributeValueType`/`Cardinality` are plan-introduced auxiliary types (the §4A audit did not flag them because it audited verbatim conformance, not carrier reachability). They have one declaration site (U-CP-01) but no consuming unit declares it as a predecessor. A coding agent landing U-CP-07 (an L0 unit, in-degree 0) cannot import `AttributeValueType` from a reachable carrier — pyright-strict fails at the unresolved name, OR each unit re-declares the enum locally and pyright treats the six copies as six distinct nominal types, breaking the cross-unit `…AttributeSchema` composition that U-CP-54's export manifest depends on.

§4.1 severity: **Class 3** (discriminator (b) — resolution requires a Phase-6 plan revision: a carrier unit + dep edges). §2.7.6 fork class: **Class 1 (halt-execution)** for the cluster.

**Note on the `verbatim_audit_as_plan.md` precedent conflict.** The AS audit (Findings-rejected #4) treated `AttributeValueType`/`Cardinality` as OTel-SDK primitives, excluded from Pattern B. That reading does **not** hold for the CP plan: U-CP-01 explicitly *declares* `enum AttributeValueType { STRING, INT, FLOAT, BOOL, ENUM_REF }` and `enum Cardinality { LOW, MEDIUM, HIGH, PER_REQUEST }` with plan-invented value sets — these are not the OpenTelemetry SDK `AttributeType` enum, they are harness auxiliary types authored in U-CP-01's signature block. The fork-queue item-18 reading (CP-plan-declared, shared, no carrier edges) is the correct one for CP; the AS audit was lenient on a parallel issue. This call is recorded explicitly in Findings-considered-and-rejected item 4.

---

## Fork inventory table — Pattern D: types referenced at signature positions with no declaring carrier anywhere

Every type below appears at a typed signature position in a CP unit with **no `enum`/`record` declaration site anywhere in the CP plan** (verified by grep — each appears only at consumption positions) and **no carrier in any cross-axis IS/AS plan reachable via a declared `(cross-axis: …)` edge**. Stack primitives (per the exclusion list) are not in this table.

| Undeclared type | Consuming unit(s) | Position | §4.1 / §2.7.6 |
|---|---|---|---|
| **`ParentRelation`** | U-CP-10 (`LifecycleEventClassMetadata.parent_relation`) | `parent_relation : ParentRelation` | Class 3 / Class 1 — **fork-queue item 16** |
| **`AgentRole`** | U-CP-03 (`InferenceRequest`), U-CP-04 (`RoutingManifest.per_role_bindings` key), U-CP-09 (`compose_fallback_chain` param), U-CP-29 (`resolve_brief_authoring_model_binding`… via workload), U-CP-27 (sub-agent) | `agent_role : AgentRole` | Class 3 / Class 1 |
| **`ProviderAgnosticPayload`** | U-CP-03 (`InferenceRequest.request_payload`, `InferenceResponse.response_payload`) | record field | Class 3 / Class 1 |
| **`TraceContext`** | U-CP-03 (`InferenceRequest.trace_context`) | record field | Class 3 / Class 1 |
| **`StepID`** | U-CP-13 (`WorkflowManifestEntry.per_step_overrides` key, `StepOverride.step_id`), U-CP-14 (`resolve_step_binding` param, `StepEffectiveBinding`) | record field / param | Class 3 / Class 1 |
| **`ModelBinding`** | U-CP-13 (`StepOverride.model_binding`), U-CP-14 (`StepEffectiveBinding.model_binding`), U-CP-29 (`resolve_brief_authoring_model_binding` return), U-CP-50 (`SummarizationModelBinding`) | record field / return | Class 3 / Class 1 |
| **`ActorIdentity`** | U-CP-14 (`emit_override_audit_entry` param), U-CP-30 (`LedgerEntryRef.actor`), U-CP-34 (`SiblingLedgerEntry.actor`), U-CP-49 (`ResumeAttempt`) | record field / param | Class 3 / Class 1 |
| **`ActionID`** | U-CP-27, U-CP-30 (`LedgerEntryRef.action_id`), U-CP-34, U-CP-35 (`ParentFanoutCloseEntry.action_id`) | record field / param | Class 3 / Class 1 |
| **`EntryID`** | U-CP-38 (`HITLResult.audit_ledger_entry_id`), U-CP-49 (`PauseEvent.pause_audit_entry_id`), U-CP-52 (`WebhookDeliveryEvent.gate_evaluation_ref`) | record field | Class 3 / Class 1 |
| **`WorkflowID`** | U-CP-49, U-CP-50, U-CP-51, U-CP-52 | record field / param | Class 3 / Class 1 |
| **`AuditLedgerEntry`** | U-CP-14 (`emit_override_audit_entry` return), U-CP-27 (`emit_sub_agent_dispatch_audit` return), U-CP-44 (`sign_audit_entry` param) | return / param | Class 3 / Class 1 |
| **`MCPTrustTier`** | U-CP-43 (`GateLevelInput.mcp_trust_tier`, `MCP_TRUST_GATE_LEVEL_FLOOR` key), U-CP-45 (`FiveAxisCompositionInput`) | record field | Class 3 / Class 1 |
| **`Axis`** | U-CP-43 (`GateLevelComputation.per_axis_floors` key, `.composition_winner`) | `Map<Axis, GateLevel>` | Class 3 / Class 1 |
| **`OverrideKind`, `OverrideScope`** | U-CP-45 (`OperatorPolicyOverride`) — declared inline as `// {…}` comments only, not as `enum`; consumed by U-CP-46 acc text | record field | Class 2 / Class 2 |
| **`SecretRef`, `SecretScopeKind`** | U-CP-44 (`SigningKeyHandle.key_secret_ref`, `SigningKeyScope.scope_kind`) | record field | Class 3 / Class 1 |
| **`MerkleRoot`** | U-CP-35 — declared in U-CP-35's own block (`record MerkleRoot {…}`); consumed only there. **In-cone — not a finding** |
| **`TailKeepPredicate`** | U-CP-32 (`SpanSamplingDecision.tail_keep_predicate`), U-CP-51 (`TailKeepRule.keep_predicate`) | record field | Class 3 / Class 1 |
| **`OutputSchemaKind`** | U-CP-28 — declared inline as `// {…}` comment on `OutputSchema.schema_kind`, not as `enum` | record field | Class 2 / Class 2 |
| **`F1LayerState`/`D1LayerState`/`D4LayerState`** | U-CP-53 — all three declared in U-CP-53's own Signatures block. **In-cone — not a finding** |
| **`MCPServerID`, `ToolName`, `ToolTier`, `Cell`, `ReferenceToUnit`, `RuntimeFault`, `CurrentState`, `LeadAgentPlan`, `WebhookConfig`/`WebhookPayload`, `HITLInvocation`, `ProposedAction`/`ActionPayload`/`ActionKind`, `FailedAttempt`/`Alternative`, `Span`, `SubAgent`, `ThreadID`/`StageID`, `EngineClassPreferences`, `GateOverride`** | various (U-CP-13/27/30/33/38/39/41/49/51/52/53) | record field / param | folded into Pattern D systemic scope |

**The Pattern D type cluster is large** (≥25 distinct types across ≥20 consuming units). Many are "obvious" identity/payload aliases (`ActionID`, `EntryID`, `WorkflowID`, `StepID`, `ThreadID`) that a coding agent would plausibly inline-materialize as `str` newtypes; others are genuine structured types (`ProposedAction`, `AuditLedgerEntry`, `ModelBinding`, `TraceContext`) whose field set is nowhere specified. The CP plan has **no `harness-core` shared-types unit** and **no §5.4-style auxiliary-type audit** (the AS plan at least had a §5.4.1 audit, flawed as it was). The CP plan simply never declares a carrier for its cross-cutting auxiliary types — the same structural blind spot the AS Pattern B audit found, here unaccompanied by even a self-audit.

§4.1 severity: **Class 3** for the structured types (discriminator (b) — Phase-6 plan revision: carriers + edges, or a spec-extension confirmation per type); **Class 2** for the inline-comment-only enums (`OverrideKind`/`OverrideScope`/`OutputSchemaKind` — plan-internal: promote the `// {…}` comment to a real `enum` in the declaring unit).

---

## Pattern E — the v2.5 deferred-edge state is itself a materializability blocker

v2.5 §0.5 records that **~10 `WorkloadClass`-consuming units** (U-CP-05, U-CP-06, U-CP-09, U-CP-13, U-CP-17, U-CP-21, U-CP-23, and others) gain a `[U-CP-00]` dependency edge — but their bodies are `[preserved verbatim]` pointers, and "the edge is recorded here and is materialized at each unit's next full-revision." v2.5 §0.8 calls this a "v2.5 plan-internal completeness item, not a fork."

That disposition under-states the materializability cost. At the **canonical-current body in force** (resolved through the v2.4/v2.3/v2.2/v2.1 pointer chain), **none of these ~10 units carries `[U-CP-00]` in its `Depends on` line.** Only U-CP-22 had its body re-revised at v2.5 to carry the edge. So for every other `WorkloadClass` consumer the dependency cone is broken exactly as Tension 003 described — post-resolution-in-principle, pre-edge-materialization-in-body. A coding agent reading U-CP-13's body (v2.1) sees `Depends on: [U-CP-04, U-CP-06, U-CP-09, U-CP-15, U-CP-22, U-CP-38]` with `WorkloadClass` consumed at `WorkflowManifestEntry.workload_class` and **no edge to U-CP-00**.

This is the shared-type-no-carrier shape (Pattern C/D family), introduced by the v2.5 deferral itself. It is authority-chain-determinate to fix (write the recorded edge into each body) but it is a real fork until done — §2.7.6 **Class 2 (operator-decision)** at minimum: the operator should direct the `implementation-planner` to materialize the §0.5 edges in-body rather than carry them as deferred pointers, OR explicitly accept the deferral with the understanding that each of the ~10 units is FORK-blocked until its next revision. The reviewer recommends the former (it is a single mechanical pass).

---

## Per-unit findings table

Verdict basis per unit. **CLEARED** = all signature types resolve to a reachable carrier (or stack primitive); signature has spec basis; materializable at topo position. **CONFORM** = authority-chain-determinate fix (dependency-graph completion; no operator decision). **FORK** = operator decision needed.

| Unit | Verdict | Materializability basis |
|---|---|---|
| U-CP-00 | **CLEARED** | Landed. `WorkloadClass` closed 4-value enum; no consumed types; `harness-core` residence. |
| U-CP-01 | **FORK** | Declares `AttributeValueType`/`Cardinality` (Pattern C carrier); `RoutingAttributeSchema.value_type`/`.cardinality` fields **have no §1.4 basis** — spec §1.4 routing table columns are {Attribute, Type, Semantic, Source}, no Cardinality column (fork-queue item 17). §2.7.6 Class 2. |
| U-CP-02 | **CLEARED** | `ProviderCapabilities`/`ProviderCapability` self-declared; `string`/`int`/`bool`/`float` primitives only. Materializable. |
| U-CP-03 | **FORK** | `InferenceRequest`/`InferenceResponse` consume undeclared `AgentRole`, `ProviderAgnosticPayload`, `TraceContext`, `RoutingDecisionTrace` (last declared at U-CP-05, downstream — see hidden-coupling note). Pattern D. §2.7.6 Class 1. |
| U-CP-04 | **FORK** | `RoutingManifest` consumes undeclared `AgentRole`, `RoleRoutingBinding`, `WorkloadRoutingOverride`, `RetryPolicy`, `ToolName`; `FilesystemPath` is cross-axis IS in-cone. Pattern D. §2.7.6 Class 1. |
| U-CP-05 | **CONFORM** | Declares `RoutingLayer`/`RoutingDecisionTrace`. Consumes `WorkloadClass`/`PersonaTier` symbolically via `InferenceRequest` — Pattern E deferred-edge (no `[U-CP-00]`). Determinate graph fix. |
| U-CP-06 | **CONFORM** | `LayerBudget` self-declared; consumes `RoutingLayer` (U-CP-05 in-cone), `WorkloadClass`/`PersonaTier` — Pattern E deferred-edge. Determinate. |
| U-CP-07 | **FORK** | `Fallback/HarnessBreaker/RetryAttributeSchema` consume `AttributeValueType`/`Cardinality` with no edge to U-CP-01 (Pattern C). L0 unit, in-degree 0 — cannot import the carrier. §2.7.6 Class 1. |
| U-CP-08 | **CLEARED** | `FallThroughCause`/`FallThroughResult` self-declared; consumes `RoutingLayer`/`InferenceRequest` in-cone. (The `FallThroughCause` spec-silence is a §4A verbatim/spec-extension item, fork-queue item 3 — NOT a materializability defect; the type IS declared by the unit.) Materializable. |
| U-CP-09 | **CONFORM** | `FallbackChain`/`ProviderCandidate`/`ProviderFamily` self-declared; consumes undeclared `AgentRole` (Pattern D) + `WorkloadClass` Pattern-E deferred-edge. The `WorkloadClass` edge is determinate; `AgentRole` folds into the Pattern D systemic fork. Verdict CONFORM on the determinate part; the Pattern D `AgentRole` resolution is cluster-wide. |
| U-CP-10 | **FORK** | `LifecycleEventClassMetadata.parent_relation : ParentRelation` — `ParentRelation` declared by no unit, no spec §5.1 basis (fork-queue item 16). Pattern D. §2.7.6 Class 1. |
| U-CP-11 | **FORK** | `LeaseAttributeSchema` consumes `AttributeValueType`/`Cardinality` no edge to U-CP-01 (Pattern C). §2.7.6 Class 1. (Separately: U-CP-11 `LEASE_NAMESPACE_SCHEMA` value-name divergence is the §4A verbatim borderline item, fork-queue item 5 — out of this pass's scope.) |
| U-CP-12 | **FORK** | v2.4 body. `PerClassAttributeSet.class`/`SamplingDisposition.class` typed `LifecycleEventClass` — U-CP-10 in-cone. But U-CP-12 transitively depends on U-CP-10 which is Pattern-D-blocked (`ParentRelation`). Propagation-gated; clears once U-CP-10 conforms. |
| U-CP-13 | **FORK** | `WorkflowManifestEntry`/`StepOverride` consume undeclared `StepID`, `ModelBinding`, `HITLPlacement` (last from U-CP-38, in-cone OK), `SubAgentBrief` (U-CP-28 — **not in `Depends on`**: hidden coupling — see note). `WorkloadClass` Pattern-E deferred-edge. Pattern D + hidden-coupling. §2.7.6 Class 1. |
| U-CP-14 | **FORK** | `StepEffectiveBinding`/`emit_override_audit_entry` consume undeclared `StepID`, `ModelBinding`, `ActorIdentity`, `AuditLedgerEntry`, `LedgerEntryRef` (U-CP-30 — **not in `Depends on`**: hidden coupling). Pattern D. §2.7.6 Class 1. |
| U-CP-15 | **CLEARED** (retrospective concern) | Landed. `EngineClass` self-declared. `CapabilityFloor` self-declared — but see retrospective note: the field set (`capability_name`, `required_at_class`, `rationale`) has thin §7.4 basis; acc #4 claims "per §7.4". Logged as §2.7.6 Class 3 informational, non-blocking. |
| U-CP-16 | **CLEARED** | `DeploymentSurface`/`EngineClassCandidate` self-declared; consumes `EngineClass` (U-CP-15 in-cone). Materializable. |
| U-CP-17 | **CONFORM** | `WorkloadBindingSelectionInput` consumes `WorkloadClass` (Pattern-E deferred-edge), `DeploymentSurface`/`PersonaTier`. `DeploymentSurface` carrier is U-CP-16 (in-cone). `PersonaTier` carrier is U-CP-40 — **not in `Depends on`**: hidden coupling. Determinate graph fix. |
| U-CP-18 | **CLEARED** | `EngineF2JoinContract`/`F2JoinKind` self-declared; cross-axis IS deps declared. Materializable. |
| U-CP-19 | **CLEARED** | Landed. `ResumptionKind`/`ResumptionKindBinding` self-declared; consumes `EngineClass` (U-CP-15 in-cone). Materializable. |
| U-CP-20 | **FORK** | `PerResumptionObservableBehavior` consumes `ResumptionKind` (U-CP-19 in-cone), `F2JoinKind` (U-CP-18 in-cone). Transitively depends on U-CP-12 (Pattern-D-blocked). Propagation-gated. |
| U-CP-21 | **FORK** | `EngineAttributeSchema` consumes `AttributeValueType`/`Cardinality` no edge to U-CP-01 (Pattern C). v2.2 body. §2.7.6 Class 1. |
| U-CP-22 | **CLEARED** (retrospective: clean) | Landed. v2.5 body carries `[U-CP-00]` edge + `WorkloadClass` Input. `TopologyPattern`/`CascadePolicy` self-declared. The one CP unit whose v2.5 re-revision materialized the WorkloadClass edge in-body. Materializable. |
| U-CP-23 | **FORK** | `PerWorkloadClassTopologyCommitment` consumes `WorkloadClass` — Pattern-E deferred-edge (body has no `[U-CP-00]`). Also carries the §4A `default_pattern` single-vs-dual structural mismatch (fork-queue item 4). §2.7.6 Class 2. |
| U-CP-24 | **CLEARED** | `TopologyFaultHandling`/`CascadeEnforcementMechanism`/`WriterSerializationMechanism`/`PerEngineClassTopologyOverlay` all self-declared; `EngineClass` in-cone. Materializable. |
| U-CP-25 | **CLEARED** | `WorkloadEngineMatrixCell`/`D4MultiplicativeTunable` self-declared; consumes `EngineClass`/`TopologyPattern`/`CascadeEnforcementMechanism`(U-CP-24)/`TopologyFaultHandling`(U-CP-24) — all in-cone; `WorkloadClass`/`PersonaTier` Pattern-E. Materializable on the declared types. |
| U-CP-26 | **CLEARED** | `SubAgentDefaultDowngrade` self-declared; `BlastRadiusTier` cross-axis AS (U-AS-01) in-cone. Materializable. |
| U-CP-27 | **FORK** | `SubAgentGateLevelDescent`/`dispatch_sub_agent` consume undeclared `ActionID`, `ActorIdentity`, `GateOverride`, `AuditLedgerEntry`, `LedgerEntryRef`(U-CP-30 in-cone), `SHA256` primitive; `GateLevel`(U-CP-43 in-cone), `SandboxTier`(cross-axis), `SubAgentBrief`(U-CP-28 — **not in `Depends on`**: hidden coupling). Pattern D + hidden-coupling. §2.7.6 Class 1. |
| U-CP-28 | **FORK** | `OutputSchema.schema_kind : OutputSchemaKind` — `OutputSchemaKind` given only as `// {JSON_SCHEMA, …}` comment, no `enum` declaration; `ClearTaskBoundaries` self-declared. Pattern D inline-enum. §2.7.6 Class 2. |
| U-CP-29 | **CONFORM** | `BriefAuthoringInheritance`/`InheritanceRule` self-declared; consumes `WorkloadClass`(Pattern-E), `ModelBinding`(Pattern D — undeclared), `StageID`(Pattern D). Determinate on the `WorkloadClass` edge; `ModelBinding`/`StageID` fold into the Pattern D cluster. |
| U-CP-30 | **FORK** | `HandoffContext`/`StateSummary`/`ProposedAction`/`ExternalReference` consume undeclared `ProposedAction`(self-declared OK), `ActionKind`/`ActionPayload`(inline comment only), `FailedAttempt`, `Alternative`, `RetryHistory`, `ActorIdentity`, `ActionID`, `ReferenceClass`(inline comment only). Pattern D dense. §2.7.6 Class 1. |
| U-CP-31 | **FORK** | `TopologyAttributeSchema`/`SubAgentAttributeSchema` consume `AttributeValueType`/`Cardinality` no edge to U-CP-01 (Pattern C). §2.7.6 Class 1. |
| U-CP-32 | **FORK** | `SpanHierarchyNode.parent_relationship : ParentRelationship` — `ParentRelationship` given only as `// {ROOT, CHILD_OF, SIBLING_OF}` comment, no `enum`; `SpanSamplingDecision.tail_keep_predicate : TailKeepPredicate` undeclared. Pattern D. §2.7.6 Class 1/2. |
| U-CP-33 | **FORK** | `CacheWarmupInput` consumes undeclared `SubAgent`, `LeadAgentPlan`, `CacheWarmupResult`(return, undeclared). Pattern D. §2.7.6 Class 1. |
| U-CP-34 | **CLEARED** | `SiblingLedgerEntry`/`F2_14_Reading_1_Rationale` self-declared; `IdempotencyKey`/`ActorIdentity` — `IdempotencyKey` cross-axis IS (U-IS-08/12) in-cone; `ActorIdentity` undeclared (Pattern D) but `SiblingLedgerEntry` matches the F2 six-field shape per U-IS-07 cross-axis — `actor` resolves to the IS-exported `Actor` type. Materializable via the cross-axis F2 shape. |
| U-CP-35 | **CLEARED** | `ParentFanoutCloseEntry`/`MerkleRoot`/`MerkleConstructionStep`/`F2Effect`/etc. all self-declared; `TopologyPattern`(U-CP-22 in-cone); `ActionID` undeclared but joins F2 via the cross-axis shape. Materializable. |
| U-CP-36 | **CLEARED** | `CrossSiblingCryptographicComposition`/`TraceInspectionSurface` self-declared; `CryptographicShape`(U-CP-42 in-cone), `PersonaTier`(U-CP-40 — in `Depends on` via U-CP-42 chain). Materializable. |
| U-CP-37 | **CONFORM** | `HITLResponse`/`HITLResponseSemantic`/`AuditFieldName`/`PerResponseAuditEntryShape`/`PaletteCompletenessInvariant`/`HITLResponseClassAttribute` all self-declared. `HITLResponseClassAttribute` carries `value_type : AttributeValueType` — and U-CP-37 does NOT depend on U-CP-01: another Pattern C consumer (the 7th). The carrier-edge fix is authority-chain-determinate — CONFORM. §2.7.6 Class 1 on that field, cleared by the Pattern C mechanical pass. |
| U-CP-38 | **FORK** | `HITLResult` consumes undeclared `EntryID`; `hitl_gate` consumes `HandoffContext`(U-CP-30 in-cone), `CascadePolicy`(U-CP-22 in-cone). Pattern D (`EntryID`). §2.7.6 Class 1. |
| U-CP-39 | **FORK** | `rewrite_tool_call_to_hitl` consumes undeclared `ToolName`, `MCPServerID`, `RewrittenToolCall`(return). `SynchronyClass`(U-CP-40 — **not in `Depends on`**: hidden coupling), `CrossTrustBoundaryState`(U-CP-48 in-cone). Pattern D + hidden-coupling. §2.7.6 Class 1. |
| U-CP-40 | **CLEARED** | `PersonaTier`/`SynchronyClass`/`HITLPrimitiveShape`/`HITLMatrixCell` all self-declared; `EngineClass` in-cone. Materializable. |
| U-CP-41 | **FORK** | `TwoAgentObserverMetaClass.applicable_cell_predicate : Cell -> bool` — `Cell` undeclared; `PersonaTierBindingSelectionResult` consumes `ReferenceToUnit`, `ToolTier`, `VerifierResult`, `OverlayResolution` — all undeclared. Pattern D dense. §2.7.6 Class 1. |
| U-CP-42 | **CLEARED** | `CryptographicShape`/`PersonaTierCryptographicShape` self-declared; cross-axis IS deps declared. Materializable. |
| U-CP-43 | **FORK** | v2.4 body. `GateLevelInput` consumes undeclared `MCPTrustTier`; `GateLevelComputation.per_axis_floors : Map<Axis, GateLevel>` consumes undeclared `Axis`. Pattern D. (Separately carries the §4A-carried `DEPLOYMENT_SURFACE`/`MCP_TRUST` floor spec-silence — fork-queue item 1, out of this pass's scope.) §2.7.6 Class 1. |
| U-CP-44 | **FORK** | `SigningKeyScope`/`SigningKeyHandle` consume undeclared `SecretScopeKind`, `SecretRef`(cross-axis AS U-AS-20 — `fetch_secret` returns `SecretRef`; the type SHOULD arrive via the U-AS-20 edge but AS plan does not export a named `SecretRef` carrier — see note), `KeyRotationState`(inline comment only), `AuditLedgerEntry`. Pattern D. §2.7.6 Class 1. |
| U-CP-45 | **FORK** | `OperatorPolicyOverride.override_kind : OverrideKind` / `.scope : OverrideScope` — both given only as `// {…}` comments, no `enum` declaration; consumed downstream by U-CP-46 acc text. Pattern D inline-enum. §2.7.6 Class 2. |
| U-CP-46 | **FORK** | v2.4 body. `AuditAttributeSchema`/`ValidatorFailAttributeSchema`/`HITLSpanSchema` consume `AttributeValueType`/`Cardinality` — U-CP-46 `Depends on` does NOT include U-CP-01 (Pattern C, 8th consumer). §2.7.6 Class 1. |
| U-CP-47 | **FORK** | v2.4 body. `ValidatorFailAttributeSchema` consumes `AttributeValueType`/`Cardinality`; `Depends on: [U-AS-03]` only — no edge to any carrier (Pattern C; fork-queue item 18 names this exact unit). §2.7.6 Class 1. |
| U-CP-48 | **CLEARED** | v2.4 body. `StaircaseStage`/`StaircaseTransition`/`CrossTrustBoundaryState`/`PaletteRestriction` self-declared; `ValidatorFailClass`(U-CP-47 in-cone), `HITLResponse`(U-CP-37 in-cone). Materializable on declared types. (U-CP-47 dep is for `ValidatorFailClass` the enum, not the schema record — that enum is clean; U-CP-48 does not consume `…AttributeSchema`.) |
| U-CP-49 | **FORK** | `PauseEvent`/`ResumeAttempt`/`ResumeOutcome` consume undeclared `WorkflowID`, `ActorIdentity`, `EntryID`, `MaterialDiff`(U-CP-50 in-cone). Pattern D. §2.7.6 Class 1. |
| U-CP-50 | **FORK** | `MaterialDiff`/`DiffEntry`/`SummarizationModelBinding` consume undeclared `WorkflowID`, `ModelBinding`, `CurrentState`, `ExternalReference`(U-CP-30 in-cone), `PersonaTier`(in-cone via chain). Pattern D. §2.7.6 Class 1. |
| U-CP-51 | **FORK** | `OperatorBurdenEval`/`TailKeepRule` consume undeclared `WorkflowID`, `TailKeepPredicate`, `HITLResponse`(U-CP-37 in-cone), `Span`. Pattern D. §2.7.6 Class 1. |
| U-CP-52 | **FORK** | `TimeoutDegradationPolicy`/`WebhookDeliveryEvent` consume undeclared `WorkflowID`, `EntryID`, `WebhookConfig`, `WebhookPayload`, `HITLInvocation`. Pattern D. §2.7.6 Class 1. |
| U-CP-53 | **CLEARED** | `TPerm3LayerComposition`/`F1/D1/D4LayerState`/`PerCellReadingKind`/`PerCellTPerm3Reading`/`DeterministicOuterHarnessBoundary` all self-declared; `RoutingLayer`/`EngineClass`/`F2JoinKind`/`ResumptionKind`/`TopologyPattern`/`CascadeEnforcementMechanism`/`TopologyFaultHandling` all in-cone via declared deps; `LayerOwner`/`RuntimeFault`/`WorkloadClass`/`PersonaTier` — `LayerOwner`/`RuntimeFault` inline comments / Pattern D, but the load-bearing composition types resolve. Marginal — verdict CLEARED with a Class-1 note that `LayerOwner` and `RuntimeFault` are inline-comment-only. |
| U-CP-54 | **CLEARED** | `NamespaceExport`/`SourceAuthorityPosture`/`IngestionTarget` self-declared; `UnitID` is an identifier alias (Pattern D-adjacent, but a descriptive-manifest string). Manifest unit; descriptive only. Materializable. |
| U-CP-55 | **CLEARED** | `CrossAxisCompositionExport`/`CompositionSurface`/`SessionTarget`/`SurfaceKind`/`F2_12_CarryForward`/`RevisionStep` all self-declared; `UnitID`/`AxisName` identifier aliases. Manifest unit; descriptive only. Materializable. |

**Tally: CLEARED 20 · CONFORM 12 · FORK 24** (= 56). The CONFORM bucket (U-CP-05, 06, 07, 09, 11, 17, 21, 29, 31, 37, 46, 47) is the Pattern C carrier-edge work + Pattern E deferred-`[U-CP-00]`-edge work — authority-chain-determinate, no operator decision; the `implementation-planner` revision-pass applies it and these clear. The FORK bucket (U-CP-01, 03, 04, 10, 12, 13, 14, 20, 23, 27, 28, 30, 32, 33, 38, 39, 41, 43, 44, 45, 49, 50, 51, 52) needs an operator decision — the Pattern D structured-type factor-out-vs-extension classification, the `AttributeValueType`/`Cardinality` residence call, `ParentRelation`, U-CP-01's `cardinality` field, U-CP-23's `default_pattern` structural mismatch, and the propagation-gated units (U-CP-12, U-CP-20 — gated on U-CP-10).

This is the **current-state** bucket the pipeline queues act on; it follows the `verbatim_audit_as_plan.md` precedent (current state, not a forward projection). Forward note: once the §4A.4 revision-pass lands, the 12 CONFORM units and the 2 propagation-gated FORK units (U-CP-12, U-CP-20) clear automatically, leaving the genuine Pattern-D / operator-decision forks.

---

## Findings considered and rejected (transparency)

1. **`SHA256` / `ISO8601` / `bytes` are NOT undeclared-type findings.** These are cryptographic-digest and timestamp stack primitives, the analog of `string`/`int`. The CP plan uses them as field types throughout (`LedgerEntryRef.entry_hash : SHA256`, `SiblingLedgerEntry.timestamp : ISO8601`). Excluded per the stack-primitive list — same ground as `verbatim_audit_as_plan.md` Findings-rejected #4 for `JSONSchema`. No carrier needed.
2. **Cross-axis IS/AS types are NOT undeclared.** `IdempotencyKey`, `FilesystemPath`/`PathClass`, `BlastRadiusTier`, `SandboxTier`, `SandboxFailClass`, the F2 state-ledger entry shape (`Actor`, `Bytes32`, etc.) arrive via the IS/AS plan export seams; every consuming CP unit declares the corresponding `(cross-axis: IS)` / `(cross-axis: AS)` edge. Carrier resolves out-of-axis-in-cone. Not Pattern D. (Contrast `ParentRelation`/`AttributeValueType` — no IS/AS carrier, no edge.)
3. **Casing convention is not a divergence (FM-D self-check).** SCREAMING_SNAKE renderings of spec lowercase-hyphen identifiers were treated as a Python-stack naming convention, not a finding — consistent with the §4A audit.
4. **`AttributeValueType`/`Cardinality` — the AS-audit precedent was explicitly OVERRIDDEN for CP, with cause.** `verbatim_audit_as_plan.md` Findings-rejected #4 treated these as OTel-SDK primitives. For the CP plan that reading is wrong: U-CP-01's Signatures block literally *declares* `enum AttributeValueType { STRING, INT, FLOAT, BOOL, ENUM_REF }` and `enum Cardinality { LOW, MEDIUM, HIGH, PER_REQUEST }` — plan-authored enums with plan-invented value sets, not the OpenTelemetry SDK `AttributeType`. Fork-queue item 18's reading (CP-plan-declared, shared, no carrier edges) is the materializability-correct one. This is the load-bearing call that sets Pattern C's scope; recorded here per the SKILL.md *proposing*-to-*decided* discipline. *Decision-vocabulary label: decided* (the declaration text is unambiguous).
5. **The §4A verbatim divergences are NOT re-litigated.** U-CP-01/10/19/22/43/46/47 verbatim cluster — conformed at v2.4, ratified. Where this audit flags those same units it is for a *distinct* materializability defect (e.g., U-CP-10's `ParentRelation`, U-CP-01's `cardinality` field) the §4A pass did not check. Confirmed no overlap with the §4A finding content.
6. **`FallThroughCause` (U-CP-08) is NOT a materializability finding.** Fork-queue item 3 + the §4A audit flag `FallThroughCause` as a spec-extension / spec-silence issue (the spec §3.2 declares no enum; the plan invents one). That is a verbatim/X-AL-3 axis concern. On the *materializability* axis U-CP-08 is clean — `FallThroughCause` IS declared by U-CP-08 itself; a coding agent can build it. The two axes give different verdicts on the same unit; this audit reports only the materializability axis (CLEARED).
7. **Dependency-graph acyclicity — checked, no cycle.** The §3.2 9-level Kahn DAG plus U-CP-00 at L0 (pure source node per v2.5 §0.5) is acyclic. The Pattern C/D/E findings are *missing nodes/edges*, a distinct defect from a cycle — the graph is acyclic but incomplete.
8. **Hidden-coupling sweep — confirmed present at ≥5 units.** U-CP-13 consumes `SubAgentBrief` (U-CP-28) without a `Depends on` edge; U-CP-14 consumes `LedgerEntryRef` (U-CP-30) without an edge; U-CP-17 consumes `PersonaTier` (U-CP-40) without an edge; U-CP-27 consumes `SubAgentBrief` (U-CP-28) without an edge; U-CP-39 consumes `SynchronyClass` (U-CP-40) without an edge. These are real graph-completeness defects folded into the Pattern D / §4A.4 resolution (the revision-pass must add the edges). Not escalated as separate forks — same conformance shape.
9. **U-CP-34/U-CP-35 `ActionID`/`ActorIdentity` — checked, CLEARED via the cross-axis F2 shape.** Both units' acceptance criteria state the records "match the F2 six-field shape per U-IS-07" — the `actor`/`action_id` fields resolve to the IS-plan-exported `StateLedgerEntry` field types via the declared `(cross-axis: IS)` edge. They are NOT free-standing Pattern D types at these units. (Contrast U-CP-30's `LedgerEntryRef` which is a *separate* 3-field record, not the F2 shape — there `ActorIdentity` is genuinely undeclared.)
10. **A8 (framing contamination) sweep — no finding.** No CP unit commits a persona/stack/deployment value the workspace `CLAUDE.md` leaves uncommitted; `DeploymentSurface`/`PersonaTier`/`ProviderFamily` are committed CP/Persona spec enums.
11. **Manifest units U-CP-54/U-CP-55 — checked hardest, CLEARED.** Both are descriptive export manifests; their `UnitID`/`AxisName`/`SessionTarget` types are identifier aliases / self-declared enums. `UnitID` is a string alias (the manifest enumerates unit IDs as data); not a structured Pattern D type. Recorded so the operator sees the clean outcome is a result, not an unchecked unit.

---

## §4.1 severity classification

The 4 Class-3 findings (Pattern C; Pattern D structured-type cluster; the U-CP-03/04 root-unit cluster; the v2.5 deferred-edge Pattern E in its strict reading) share discriminator **(b)** — resolution requires revising a Phase-6 plan artifact (the CP plan): declaring carrier units, adding `Depends on` edges, materializing the §0.5 deferred edges. The CP plan is the artifact in error — the spec does not under-specify here (the spec never claimed to enumerate `ActionID`/`ParentRelation`/`AttributeValueType` field-by-field; the plan introduced these auxiliary types and simply failed to assign them a carrier).

The 3 Class-2 findings name discriminator **(a)** — substantive content of the Phase-6 plan, plan-internal fix: U-CP-01's `cardinality` field with no §1.4 basis (could route to spec, but the spec is canonical and the field is plan-added — plan-internal removal/justification); the inline-comment-only enums (`OverrideKind`/`OverrideScope`/`OutputSchemaKind`/`ParentRelationship`/`ActionKind` etc. — promote `// {…}` to a real `enum` in the declaring unit); the Pattern E deferred-edge under the "accept the deferral" reading.

The 1 Class-1 finding is the U-CP-53 `LayerOwner`/`RuntimeFault` inline-comment drift (non-blocking; the load-bearing composition types resolve).

Severity distribution 4/3/1 **counted per systemic pattern** — not skewed (FM-A / FM-B check). Counting convention note: this differs from `verbatim_audit_as_plan.md`'s per-unit count (11/4/2 across 15 units). CP's materializability defect is *structural* — Pattern C is one finding that touches 7 units, Pattern D one finding touching ≥20. A per-unit count would read ≈24 Class-3 / ≈3 Class-2 and invite a misleading direct comparison to the AS numbers; the per-pattern count is the honest aggregation. Stated explicitly here per the operator-transparency discipline.

---

## Systemic-pattern section (SKILL.md §6 — ≥3 occurrences)

The §6 threshold is crossed **twice** (Pattern C, Pattern D); a third pattern (Pattern E) is v2.5-introduced and named for completeness. The naming continues the `verbatim_audit_as_plan.md` alphabet (A = verbatim divergence, B = AS undeclared types) — **C/D/E are CP-specific**.

### Pattern C — schema-attribute utility types declared inside U-CP-01, consumed sideways with no carrier edge

Occurrences: `AttributeValueType` + `Cardinality` consumed at `…AttributeSchema` records in **U-CP-07, U-CP-11, U-CP-21, U-CP-31, U-CP-37, U-CP-46, U-CP-47** — **7 units**, none with a `Depends on` edge to U-CP-01 (the sole declaration site). This is the `WorkloadClass`→U-CP-00 / Tension-003 shape: one nominal type, many sideways consumers, no carrier reachability. pyright-strict treats independent re-declarations as distinct types, breaking the cross-unit `…AttributeSchema` composition U-CP-54's export manifest aggregates. The §4A verbatim audit could not have caught this — it audited transcription, not carrier reachability.

### Pattern D — auxiliary types referenced at signature positions with no declaring carrier anywhere

Occurrences: ≥25 distinct types (`ParentRelation`, `AgentRole`, `ProviderAgnosticPayload`, `TraceContext`, `StepID`, `ModelBinding`, `ActorIdentity`, `ActionID`, `EntryID`, `WorkflowID`, `AuditLedgerEntry`, `MCPTrustTier`, `Axis`, `SecretRef`/`SecretScopeKind`, `TailKeepPredicate`, `ProposedAction`/`ActionKind`/`ActionPayload`, `FailedAttempt`, `Alternative`, `RetryHistory`, and the inline-comment-only enums `OverrideKind`/`OverrideScope`/`OutputSchemaKind`/`ParentRelationship`/`ReferenceClass`/`KeyRotationState`/`LayerOwner`/`RuntimeFault`/`SubAgentResultStatus`-adjacent) across **≥20 consuming units**. No `enum`/`record` declaration site anywhere in the CP plan; no cross-axis carrier. The CP plan has **no `harness-core` shared-types unit** and **no auxiliary-type audit section at all** (the AS plan at least had a §5.4.1 audit). This is the AS Pattern B disease in the CP plan — and worse, because the CP plan never self-audited for it.

This is **distinct from** the §4A verbatim-divergence Pattern A (which was about *transcription fidelity*); Pattern D is about *dependency-graph completeness*. The fork-queue's own note confirms it: "The §4A audit checked verbatim conformance. It did NOT check materializability… `CLEARED` meant 'no §4A verbatim divergence', NOT 'ready to land'."

### Pattern E — v2.5 deferred dependency edges not materialized in unit bodies

Occurrences: ~10 `WorkloadClass`-consuming units (U-CP-05, 06, 09, 13, 17, 21, 23, +others) whose `[U-CP-00]` edge v2.5 §0.5 *records* but defers to "each unit's next full-revision." At the canonical-current body in force, none carries the edge — the dependency cone is broken exactly as Tension 003 described. v2.5 §0.8 mislabels this "not a fork." It is the shared-type-no-carrier shape, v2.5-introduced.

The three patterns have different conformance shapes: Pattern C = declare a carrier (or move `AttributeValueType`/`Cardinality` to `harness-core`) + 7 dep edges; Pattern D = declare carriers (likely a `harness-core` shared-types unit) + edges, with per-type operator classification of factor-out-vs-extension; Pattern E = write the §0.5-recorded edges into the ~10 bodies (pure mechanical).

---

# §4A Resolution Recommendation — CP-plan materializability cluster

*Appended 2026-05-15 per `systems-architect` SKILL.md §4A (Phase-7 tension-resolution mode). This audit report is the canonical systemic-tension record for the CP-plan materializability cluster (per the Phase-7 checkpoint decision: no per-unit Tension proliferation). The §4A recommendation is a recommendation — the operator holds decision authority (§4A.7).*

## §4A.1 — Precise tension statement

The CP plan v2.5 carries three systemic materializability defects, all crossing the SKILL.md §6 ≥3-occurrence threshold, none touched by the §4A verbatim audit:

- **Pattern C** — `AttributeValueType`/`Cardinality` declared once (U-CP-01), consumed at `…AttributeSchema` records in 7 units with no carrier dep edge.
- **Pattern D** — ≥25 auxiliary types at signature positions with no declaring carrier anywhere; ≥20 consuming units; plus ≥5 hidden-coupling edges (consumer uses a sibling's type without declaring the edge).
- **Pattern E** — v2.5's own deferred `[U-CP-00]` edges for ~10 `WorkloadClass` consumers, recorded but not materialized in the bodies in force.

Per-pattern enumeration in the inventory tables above; not re-summarized here per §4A.2.

## §4A.2 — Authority-chain placement

`CLAUDE.md` §1.3 chain: ADR → ADD v1.3 → PRD v1.1 → per-axis spec v1.x → per-axis plan v2.x.

- **Pattern C + Pattern E:** authority-chain-**determinate**. The defect is purely a Phase-6 plan dependency-graph incompleteness. `AttributeValueType`/`Cardinality` are plan-introduced (the spec never enumerates them); `WorkloadClass` is spec-committed (C-CP-07 §7.3) and already has a carrier (U-CP-00). The fix is plan-internal: declare a carrier / write the recorded edges. No operator decision on *what* — only ratification of the fix.
- **Pattern D:** **partially determinate.** For each undeclared type the operator must confirm, per type, whether it is a *faithful factor-out of spec content* (plan-internal carrier declaration suffices — `ActionID`/`EntryID`/`WorkflowID`/`StepID` identity aliases; `OverrideKind`/`OverrideScope`/`OutputSchemaKind` inline enums whose value sets the plan already states in comments) or a *plan-introduced design extension* the spec does not commit (route to spec back-flow per X-AL-3 — `ProposedAction`/`AuditLedgerEntry`/`ModelBinding`/`TraceContext`/`ParentRelation`/`MaterialDiff` are structured types whose field set is nowhere specified). This is the AS Pattern B §4A.4 item-4 shape exactly.

## §4A.3 — §2-discipline analysis

- **Five-axis:** every undeclared type is a Control-Plane-axis primitive; the resolution is within-axis plan dependency-graph completion (plus, possibly, a `harness-core` shared-types unit — `CLAUDE.md` §2.5 names `harness-core` as the home for shared cross-axis types, and `AttributeValueType`/`Cardinality`/the identity aliases are exactly that). No cross-axis re-decomposition.
- **Probabilistic–deterministic boundary:** every undeclared type is a **deterministic-side** primitive — an enum, an identity alias, a schema record. A missing carrier does not silently mis-route; it hard-fails pyright-strict at build time. The cost of leaving it is a guaranteed build break at landing, not a subtle runtime defect — which makes it cheaper to catch now (this pass) than at the coding lane.
- **Decision ordering:** the defects are **D-level** (derivative materialization). *That* the CP axis needs these schema/identity types is not in question; the plan's failure to assign them a carrier is the defect. Pattern C/E are pure derivative-materialization fixes; Pattern D's factor-out-vs-extension split is the only place a small genuine design decision is owed.

## §4A.4 — Recommended reading

**A single `implementation-planner` revision-pass on `Implementation_Plan_Control_Plane` (next version bump), carrying three internal sub-passes:**

1. **Pattern C sub-pass.** Relocate `AttributeValueType` + `Cardinality` from U-CP-01's inline Signatures block into a foundational carrier — recommended: a `harness-core` unit (the U-CP-00 shape; these are cross-axis-shared schema-attribute types, and the AS plan consumes OTel-analog types too). Add a `Depends on` edge to that carrier at U-CP-01, U-CP-07, U-CP-11, U-CP-21, U-CP-31, U-CP-37, U-CP-46, U-CP-47. The reviewer does not pick `harness-core`-unit-vs-U-CP-01-as-carrier — that is the operator's residence call (§4A.7).
2. **Pattern E sub-pass.** Write the v2.5 §0.5-recorded `[U-CP-00]` edges into the ~10 `WorkloadClass`-consuming unit bodies (U-CP-05, 06, 09, 13, 17, 21, 23, +others per Tension 003 §2). Pure mechanical; no decision. (This supersedes v2.5 §0.8's "deferred, not a fork" disposition.)
3. **Pattern D sub-pass — carrier declaration + dependency-graph completion + hidden-coupling edges.** For each undeclared type: (a) declare a carrier (`record`/`enum`) in a unit with a `Depends on` edge to it — likely a `harness-core` shared-types unit for the identity aliases and a per-cluster declaring unit for the structured types; (b) promote the inline-comment enums (`OverrideKind`/`OverrideScope`/`OutputSchemaKind`/`ParentRelationship`/`ActionKind`/`ReferenceClass`/`KeyRotationState`) to real `enum` declarations in their consuming units; (c) add the ≥5 missing hidden-coupling edges (U-CP-13→U-CP-28, U-CP-14→U-CP-30, U-CP-17→U-CP-40, U-CP-27→U-CP-28, U-CP-39→U-CP-40). Add a §5-style auxiliary-type audit section to the CP plan so the blind spot does not recur.

### Items requiring an explicit operator decision (NOT plan-internal conform)

1. **`AttributeValueType`/`Cardinality` residence — operator decision.** `harness-core` shared-types unit (recommended — cross-axis shared) vs U-CP-01-as-carrier-with-7-edges. §2.7.6 Class 1.
2. **Pattern D factor-out-vs-extension classification — per-type operator confirmation.** Identity aliases (`ActionID`, `EntryID`, `WorkflowID`, `StepID`, `ThreadID`, `StageID`, `AgentRole`, `UnitID`) and the inline-comment enums are likely factor-outs — plan-internal carrier suffices. The structured types (`ProposedAction`, `AuditLedgerEntry`, `ModelBinding`, `TraceContext`, `ParentRelation`, `MaterialDiff`, `ProviderAgnosticPayload`, `RetryHistory`) may be design extensions — the operator must confirm, per type, whether a spec-extension (X-AL-3 back-flow) is owed first. §2.7.6 Class 1.
3. **`ParentRelation` (U-CP-10, landed)** — fork-queue item 16. Operator decides carrier + value set, or drop the plan-invented `parent_relation` field. Routes to CP plan revision; *and* note U-CP-10 is the consumer of a landed-adjacent unit — see retrospective. §2.7.6 Class 1.
4. **v2.5 §0.8 disposition correction — operator note.** v2.5 §0.8 called the Pattern E deferred edges "a v2.5 plan-internal completeness item, not a fork." This audit's finding is that, at the body in force, it IS a materializability fork for each of the ~10 units. The operator should direct the Pattern E sub-pass rather than carry the deferral.

## §4A.5 — Tiebreaker check

No ADR / ADD / PRD revision postdates the cited spec sections and re-commits a carrier for the plan's auxiliary types — the spec change-notes (v1→v1.3) touch only `retry.*`/`engine.*`/§24.1, none of the Pattern C/D types. **Determinate for Pattern C + E + the Pattern D factor-out half: plan-internal carrier declaration.** The non-determinate items are exactly §4A.4's "requiring a decision" list (residence call; structured-type factor-out-vs-extension classification).

**Load-bearing-artifact flag:** the resolution touches no `CLAUDE.md` anti-leakage rule and no F-ADR. It may add a `harness-core` unit (the U-CP-00 precedent — operator-sanctioned at Tension 003). The cluster needs operator ratification of the conformance direction + the residence + classification calls.

## §4A.6 — Fork classification

Per `Project_Workflow_v1_8.md` §2.7.6: **Class 1 (halt-execution)** for the Class-3 findings — the CP plan requires revision before the affected units land. Under the `design-substrate/`-is-canonical posture, Class 1 means: halt landing of the affected units, run the `implementation-planner` revision-pass in-CLI, re-clear, land. **U-CP-00, U-CP-15, U-CP-19, U-CP-22 are already landed** — see the retrospective section; U-CP-15's `CapabilityFloor` and U-CP-22's clean v2.5 body are the retrospective items.

## §4A.7 — Operator decision required

**The operator decides.** Operator actions:

1. **Ratify** the §4A.4 three-sub-pass `implementation-planner` revision-pass (Pattern C carrier + edges; Pattern E edge materialization; Pattern D carriers + inline-enum promotion + hidden-coupling edges + add an auxiliary-type audit section).
2. **Decide** the `AttributeValueType`/`Cardinality` residence (`harness-core` unit vs U-CP-01-carrier).
3. **Classify** each Pattern D structured type as factor-out (plan-internal carrier) vs design extension (spec back-flow per X-AL-3).
4. **Decide** `ParentRelation` (U-CP-10): carrier + value set, or drop the field.
5. **Correct** the v2.5 §0.8 disposition: direct the Pattern E edge-materialization sub-pass.
6. **Authorize** the U-CP-15 `CapabilityFloor` retrospective check (below).

On ratification: `implementation-planner` revision-pass on `Implementation_Plan_Control_Plane` (next version bump) → re-clear → land. The `verbatim_audit_cp_plan.md` §4A conformance pass (v2.4) and this materializability pass should be absorbed in the **same** plan version where practical, since both touch the same units.

---

## Retrospective concern — already-landed CP units (U-CP-00 / 15 / 19 / 22)

Task-mandated. Landed status confirmed against `.harness/phase-7-progress.md` (U-CP-00, U-CP-15, U-CP-19, U-CP-22 all ✅ landed 2026-05-15).

- **U-CP-00** — `WorkloadClass` closed 4-value enum. No consumed types; clean. **No retrospective concern** — it IS the Tension 003 carrier; its existence is what makes Pattern E *resolvable*.
- **U-CP-15** — `EngineClass` enum (clean) + `CapabilityFloor` record. `CapabilityFloor` is self-declared (no carrier defect) but its field set (`capability_name`, `required_at_class`, `rationale`) and the `CAPABILITY_FLOORS` constant rest on acc #4's claim "per §7.4 the minimum capability set". The §4A verbatim audit clean-listed U-CP-15 but did not deep-check whether §7.4 enumerates a per-class capability-floor *table* the `CapabilityFloor` record transcribes, or whether the record is a plan-side operationalization of §7.4 prose. **Logged as a §2.7.6 Class 3 (informational) retrospective** — the operator should authorize a check that the landed `CapabilityFloor`/`CAPABILITY_FLOORS` materialization has a genuine §7.4 basis (factor-out) and is not a silent plan extension. Non-blocking; U-CP-15 is landed and `EngineClass` (the load-bearing export) is clean.
- **U-CP-19** — `ResumptionKind` + `RESUMPTION_KIND_BINDINGS`. Consumes only `EngineClass` (U-CP-15, in-cone). Both types self-declared. **No retrospective concern.**
- **U-CP-22** — landed against the v2.5 body, which is the *only* CP unit whose v2.5 re-revision materialized the `[U-CP-00]` `WorkloadClass` edge in-body. `TopologyPattern`/`CascadePolicy` self-declared; `WorkloadClass` resolves via the declared U-CP-00 edge. **No retrospective concern** — U-CP-22 is, ironically, the one `WorkloadClass`-consumer that is materializability-clean precisely because v2.5 fixed its body and not the other ~10 (which is the Pattern E finding). The operator should note: the landed U-CP-22 is correct; the ~10 *un*-revised consumers are the exposure.

No landed unit needs revisiting on the materializability axis. The one retrospective action is the U-CP-15 `CapabilityFloor` §7.4-basis check (§4A.7 item 6).

---

## Pipeline disposition

Per-unit verdict for `pipeline-cleared-queue.md` / `pipeline-fork-queue.md`, reflecting the **post-systemic-resolution** bucket. **CLEARED** = materializable as written (no carrier defect, spec basis present). **CONFORM** = authority-chain-determinate fix (Pattern C/E mechanical edge work; `implementation-planner` applies, then clears — no operator decision). **FORK** = operator decision needed (Pattern D structured-type classification; residence call; `ParentRelation`; U-CP-01 `cardinality` field).

| Unit | Verdict | Basis |
|---|---|---|
| U-CP-00 | **CLEARED** | Landed; carrier of `WorkloadClass`; clean |
| U-CP-01 | **FORK** | `cardinality` field no §1.4 basis (item 17); Pattern C carrier residence (operator call) |
| U-CP-02 | **CLEARED** | All types self-declared |
| U-CP-03 | **FORK** | Pattern D — `AgentRole`/`ProviderAgnosticPayload`/`TraceContext` undeclared |
| U-CP-04 | **FORK** | Pattern D — `AgentRole`/`RoleRoutingBinding`/`WorkloadRoutingOverride`/`RetryPolicy` undeclared |
| U-CP-05 | **CONFORM** | Pattern E deferred `[U-CP-00]` edge; determinate |
| U-CP-06 | **CONFORM** | Pattern E deferred `[U-CP-00]` edge; determinate |
| U-CP-07 | **CONFORM** | Pattern C — `AttributeValueType`/`Cardinality` carrier edge; determinate once residence decided |
| U-CP-08 | **CLEARED** | `FallThroughCause` self-declared (materializability axis; the spec-silence is a separate §4A item) |
| U-CP-09 | **CONFORM** | Pattern E `[U-CP-00]` edge; `AgentRole` folds into Pattern D cluster |
| U-CP-10 | **FORK** | `ParentRelation` undeclared, no §5.1 basis (item 16) — operator decides carrier or drop field |
| U-CP-11 | **CONFORM** | Pattern C carrier edge; determinate |
| U-CP-12 | **FORK** | Propagation-gated on U-CP-10 (`ParentRelation`); clears when U-CP-10 conforms |
| U-CP-13 | **FORK** | Pattern D (`StepID`/`ModelBinding`) + hidden-coupling edge to U-CP-28 |
| U-CP-14 | **FORK** | Pattern D (`StepID`/`ModelBinding`/`ActorIdentity`/`AuditLedgerEntry`) + hidden-coupling edge to U-CP-30 |
| U-CP-15 | **CLEARED** | Landed; `EngineClass` clean. `CapabilityFloor` §7.4-basis retrospective (Class 3 informational) |
| U-CP-16 | **CLEARED** | All types self-declared / in-cone |
| U-CP-17 | **CONFORM** | Pattern E `[U-CP-00]` edge + hidden-coupling edge to U-CP-40; determinate |
| U-CP-18 | **CLEARED** | All types self-declared / cross-axis in-cone |
| U-CP-19 | **CLEARED** | Landed; clean |
| U-CP-20 | **FORK** | Propagation-gated on U-CP-12 → U-CP-10 |
| U-CP-21 | **CONFORM** | Pattern C carrier edge + Pattern E `[U-CP-00]` edge; determinate |
| U-CP-22 | **CLEARED** | Landed; v2.5 body materialized the `[U-CP-00]` edge; clean |
| U-CP-23 | **FORK** | Pattern E `[U-CP-00]` edge (determinate) **+** the §4A `default_pattern` single-vs-dual structural mismatch (item 4 — operator decision); FORK on the latter |
| U-CP-24 | **CLEARED** | All types self-declared / in-cone |
| U-CP-25 | **CLEARED** | All declared types in-cone |
| U-CP-26 | **CLEARED** | Self-declared + cross-axis AS in-cone |
| U-CP-27 | **FORK** | Pattern D (`ActionID`/`ActorIdentity`/`GateOverride`/`AuditLedgerEntry`) + hidden-coupling edge to U-CP-28 |
| U-CP-28 | **FORK** | Pattern D inline-enum (`OutputSchemaKind` comment-only) — Class 2 |
| U-CP-29 | **CONFORM** | Pattern E `[U-CP-00]` edge; `ModelBinding`/`StageID` fold into Pattern D cluster |
| U-CP-30 | **FORK** | Pattern D dense (`ActionKind`/`ActionPayload`/`FailedAttempt`/`Alternative`/`RetryHistory`/`ActorIdentity`/`ActionID`/`ReferenceClass`) |
| U-CP-31 | **CONFORM** | Pattern C carrier edge; determinate |
| U-CP-32 | **FORK** | Pattern D (`ParentRelationship` comment-only; `TailKeepPredicate` undeclared) |
| U-CP-33 | **FORK** | Pattern D (`SubAgent`/`LeadAgentPlan`/`CacheWarmupResult` undeclared) |
| U-CP-34 | **CLEARED** | F2 six-field shape resolves `actor`/`action_id` via cross-axis IS edge |
| U-CP-35 | **CLEARED** | All types self-declared; `ActionID` joins F2 via cross-axis shape |
| U-CP-36 | **CLEARED** | All types self-declared / in-cone |
| U-CP-37 | **CONFORM** | Pattern C — `HITLResponseClassAttribute.value_type` consumes `AttributeValueType`; carrier edge determinate |
| U-CP-38 | **FORK** | Pattern D (`EntryID` undeclared) |
| U-CP-39 | **FORK** | Pattern D (`ToolName`/`MCPServerID`/`RewrittenToolCall`) + hidden-coupling edge to U-CP-40 |
| U-CP-40 | **CLEARED** | All types self-declared / in-cone |
| U-CP-41 | **FORK** | Pattern D dense (`Cell`/`ReferenceToUnit`/`ToolTier`/`VerifierResult`/`OverlayResolution`) |
| U-CP-42 | **CLEARED** | Self-declared + cross-axis IS in-cone |
| U-CP-43 | **FORK** | Pattern D (`MCPTrustTier`/`Axis` undeclared) — **plus** the §4A-carried `DEPLOYMENT_SURFACE`/`MCP_TRUST` floor spec-silence (item 1) |
| U-CP-44 | **FORK** | Pattern D (`SecretScopeKind`/`SecretRef`/`KeyRotationState`/`AuditLedgerEntry`) |
| U-CP-45 | **FORK** | Pattern D inline-enum (`OverrideKind`/`OverrideScope` comment-only) — Class 2 |
| U-CP-46 | **CONFORM** | Pattern C carrier edge; determinate (the §4A verbatim conformance is done at v2.4) |
| U-CP-47 | **CONFORM** | Pattern C carrier edge — `Depends on: [U-AS-03]` only, needs the carrier edge (item 18) |
| U-CP-48 | **CLEARED** | All declared types in-cone; does not consume `…AttributeSchema` |
| U-CP-49 | **FORK** | Pattern D (`WorkflowID`/`ActorIdentity`/`EntryID`) |
| U-CP-50 | **FORK** | Pattern D (`WorkflowID`/`ModelBinding`/`CurrentState`) |
| U-CP-51 | **FORK** | Pattern D (`WorkflowID`/`TailKeepPredicate`/`Span`) |
| U-CP-52 | **FORK** | Pattern D (`WorkflowID`/`EntryID`/`WebhookConfig`/`WebhookPayload`/`HITLInvocation`) |
| U-CP-53 | **CLEARED** | Load-bearing composition types in-cone; `LayerOwner`/`RuntimeFault` inline-comment drift is Class-1 non-blocking |
| U-CP-54 | **CLEARED** | Descriptive manifest; `UnitID` identifier alias |
| U-CP-55 | **CLEARED** | Descriptive manifest; identifier aliases |

**Tally: CLEARED 20 · CONFORM 12 (U-CP-05, 06, 07, 09, 11, 17, 21, 29, 31, 37, 46, 47 — Pattern C carrier-edge + Pattern E deferred-edge mechanical work) · FORK 24 (U-CP-01, 03, 04, 10, 12, 13, 14, 20, 23, 27, 28, 30, 32, 33, 38, 39, 41, 43, 44, 45, 49, 50, 51, 52).** 20 + 12 + 24 = 56.

For queue routing: the 20 CLEARED units flow to `pipeline-cleared-queue.md`; the 12 CONFORM + 24 FORK units route to `pipeline-fork-queue.md`. The 12 CONFORM units clear automatically once the single `implementation-planner` revision-pass applies the Pattern C / Pattern E edge work (authority-chain-determinate; no operator decision). The 24 FORK units need the operator decisions in §4A.7. Forward note: 2 of the 24 FORK units (U-CP-12, U-CP-20) are propagation-gated on U-CP-10 (`ParentRelation`) and clear once it conforms.

The FORK units do not enter `pipeline-cleared-queue.md`. Fork-queue items 16, 17, 18 are folded by reference (U-CP-10, U-CP-01, U-CP-47 respectively) — this audit supersedes their per-unit provisional framing with the systemic Pattern C / D / E resolution.

---

*Phase-7 pre-implementation review, review-ahead pipeline pass Q2 — plan-wide systemic MATERIALIZABILITY audit of `Implementation_Plan_Control_Plane_v2_5.md` (all 56 units U-CP-00 – U-CP-55, bodies resolved through the v2.5→v2.4→v2.3→v2.2→v2.1 pointer chain). Three systemic patterns: Pattern C (schema-attribute utility types, no carrier edge), Pattern D (undeclared auxiliary types, ≥25 types / ≥20 units), Pattern E (v2.5 deferred dependency edges). Distinct from the §4A verbatim audit — that pass checked transcription fidelity; this pass checks carrier reachability + spec-basis completeness + topo-position materializability. Read-only with respect to all `design-substrate/` artifacts, `CLAUDE.md` files, plans, specs, and source — no canonical file modified. Fork-queue items 16–18 folded by reference. Findings classified, not absorbed (X-AL-3). Authored 2026-05-15 per `harness-adversarial-reviewer` SKILL.md Phase-7 pre-implementation review mode; §4A appendix per `systems-architect` SKILL.md §4A tension-resolution mode.*
