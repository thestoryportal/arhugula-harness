# Materializability Audit — Operational Discipline Implementation Plan (U-OD-01 – U-OD-34)

## Summary

- Mode: Phase-7 pre-implementation review (per `harness-adversarial-reviewer` SKILL.md §"Phase-7 pre-implementation review mode"), review-ahead pipeline pass Q3 (re-launch). Plan-wide **systemic materializability audit** of all 34 OD-axis units — the SECOND, distinct axis the §4A `verbatim_audit_od_plan.md` audit never checked: **can a coding agent build the unit, pyright-strict-clean, at its topological position?**
- Distinct from §4A: §4A checked *verbatim conformance* (does a plan signature transcribe its cited spec section). This pass checks *materializability* — undeclared types / no-carrier shared types / signature-vs-spec completeness / hidden dependency coupling. Verbatim divergences are NOT re-litigated; the §4A audit (`.harness/verbatim_audit_od_plan.md`) is referenced where relevant.
- Corpus reviewed:
  - `design-substrate/Implementation_Plan_Operational_Discipline_v2_5.md` — delta file; §0 change-note + nine full-revised unit bodies (U-OD-02/04/09/11/12/14/30/32/33)
  - `design-substrate/Implementation_Plan_Operational_Discipline_v2_1.md` §3 — full unit bodies for the 25 preserved-verbatim units; §4 dependency graph; §6.5 anti-pattern audit
  - `design-substrate/Implementation_Plan_Operational_Discipline_v2_4.md` §0 (C3-15 IS-edge delete/remap → 4 edges; F3-02 Form A) ; v2.2 §3.5.3 (U-OD-20 cascade)
  - `design-substrate/Spec_Operational_Discipline_v1_2.md` / `v1_3.md` (consulted per-unit for signature-vs-spec completeness)
  - `.harness/verbatim_audit_od_plan.md` — §4A verbatim audit (precedent + cross-reference); `.harness/verbatim_audit_as_plan.md` — Pattern A / Pattern B framing precedent
  - `harness-od/CLAUDE.md` — OD axis scope; CXA-OD-IS-EDGE-DRIFT carry-forward
- Date: 2026-05-15
- Finding count by §4.1 review-severity class: **Class 3: 2 · Class 2: 5 · Class 1: 2**. The two Class-3 findings are the two systemic patterns (M-1 undeclared shared auxiliary types; M-2 hidden dependency coupling).
- Highest-severity finding: **Pattern M-1** — ≥11 auxiliary types consumed at typed signature positions across ≥10 units with no declaring carrier and no dependency-graph edge. The Tension-003 / U-CP-10 `ParentRelation` / AS Pattern B shape, systemic in the OD plan.
- **Bottom-line:** of 34 OD units, **19 CLEARED** (materializable as written), **1 CONFORM** (U-OD-34 — determinate plan-internal fix), **14 FORK** (operator decision or back-flow needed). The OD plan carries the undeclared-auxiliary-type disease the AS plan exhibited (AS Pattern B) — the §4A OD verbatim audit, scoped only to verbatim claims, never checked it; the plan's own §6.5 anti-pattern audit reports "A6 Missing dependencies ✅ PASS" and "A3 Spec extension ✅ No" — **both miss this cluster.**

### Class-taxonomy disambiguation (per SKILL.md title-section)

Per-unit severity is the **§4.1 review-severity** scale (Class 1 minor / Class 2 moderate / Class 3 severe — phase re-opening). Each materializability-blocking finding's *disposition* is a **§2.7.6 Phase-7 execution fork**; the §2.7.6 fork class is stated explicitly per row. A §4.1 Class 3 review finding ≠ a §2.7.6 Class 3 (informational) fork.

---

## Method

For every unit U-OD-01 – U-OD-34, three checks (per the pass mandate):

1. **Undeclared-type / carrier check.** Every type/enum/record at a typed signature position was checked for a declaring carrier (`enum`/`record`/`opaque` declaration in some unit's Signatures block) AND for that carrier being reachable in the consuming unit's `Depends on` cone (within-axis, or cross-axis via a declared `(cross-axis: …)` edge). A type with no reachable carrier is a fork.
2. **Shared-type no-carrier check.** Where multiple units consume the same auxiliary type, is there ONE carrier unit and do all consumers declare a dep edge to it?
3. **Signature-vs-spec completeness.** Does a signature carry fields/params with no basis in the cited spec section? Does an acceptance criterion claim "per §X verbatim" for a property §X does not define?

Plus dependency-graph completeness — hidden coupling where a unit consumes a sibling's output type without declaring the `Depends on` edge.

**Casing discipline (FM-D self-check).** SCREAMING_SNAKE renderings of spec lowercase identifiers (`PER_MODEL`↔`per_model`) are a Python-stack naming convention, not a materializability defect.

**Stack-primitive exclusion (FM-D self-check; AS-precedent Findings-rejected item 4).** `string`/`int`/`float`/`bool`/`Option`/`List`/`Set`/`Map`/`Duration`/`Result` are stack primitives. OTel-SDK / span-data-model primitives (`SpanId`, `TraceId`, the OTel span/attribute data model) are a `Target_Stack_Commitment` adoption, not harness auxiliary types — they need no plan carrier. The OD plan, however, uses several `*Ref` / emission / harness-domain record types that are NEITHER OTel-SDK primitives NOR stack primitives — they are H_T structured types and DO require a plan carrier. See Pattern M-1.

**`CellID` resolved — not a finding.** The pass mandate flagged `CellID` for attention. `CellID` IS declared — `record CellID` in U-OD-01's Signatures block (v2.1 §3.1.1 line 290), with `PersonaTier` / `DeploymentSurface` also declared there. Every `CellID`-consuming unit (U-OD-02/03/12/13/16/17/22/24/27/28/30/32) declares `Depends on: [U-OD-01]` (direct or transitively in-cone). `CellID` has a carrier and is in-cone everywhere it is used. The U-OD-01 9-cell matrix is a clean L0 anchor. Recorded in the rejected-findings section so the operator sees this was checked, not assumed.

---

## Pattern M-1 — undeclared auxiliary types consumed at signature positions, no carrier (systemic)

The single highest-severity finding. ≥11 H_T structured types appear at typed signature positions (function params, function return types, record field types) with **no `enum`/`record`/`opaque` declaration anywhere in the OD plan** and **no carrier in the consuming unit's `Depends on` cone**. This is the AS-plan Pattern B / Tension-003 shape. Each is verified by reading every unit's Signatures block: the identifier appears only at consumption positions, never at a declaration position.

| Undeclared type | Consuming unit(s) | Position | §4.1 / §2.7.6 |
|---|---|---|---|
| **`SpanRef`** (+ `ChildSpanRef`, same family) | U-OD-09 (`emit_breaker_trip_span_event` param `parent_span_ref`), U-OD-19 (`rollup_fanout_at_close` param), U-OD-20 (`attach_idempotency_key_to_cost_record` param `span`), U-OD-25 (`emit_drift_event` param), U-OD-30 (`assert_tenant_id_on_every_span_at_multi_tenant_cells` param `span`); **`ChildSpanRef`** at U-OD-23 (`emit_eval_as_child_span` return) | `fn …(parent_span_ref : SpanRef, …)` / `-> Result<ChildSpanRef, …>` | Class 3 / Class 1 (halt) — most-consumed undeclared type-family |
| **`EventEmission`** | U-OD-09 (`emit_breaker_trip_span_event` return), U-OD-25 (`emit_drift_event` return) | `-> Result<EventEmission, …>` | Class 3 / Class 1 (halt) |
| **`SpanAttributes`** | U-OD-10 (`enforce_otel_canonical_value` param), U-OD-26 (`classify_eval_span` param), U-OD-31 (`assert_pre_collector_redaction_applied` param `span_attrs`) | `fn …(span_attrs : SpanAttributes)` | Class 3 / Class 1 (halt) — borderline vs OTel SDK; see note below |
| **`DashboardRef`** | U-OD-22 (`DashboardBackendConsolidation` fields `cost_attribution_dashboard`, `operator_burden_eval_dashboard`, `consolidated_view`) | `cost_attribution_dashboard : DashboardRef` | Class 2 / Class 2 (operator-decision) |
| **`DashboardQuery`** | U-OD-31 (`reject_cross_tenant_query` param `query`) | `fn reject_cross_tenant_query(query : DashboardQuery)` | Class 2 / Class 2 |
| **`SpanRow`** | U-OD-27 (`query_ring_buffer_via_tui` return type `List<SpanRow>`) | `-> List<SpanRow>` | Class 2 / Class 2 |
| **`HusainLoopState`** | U-OD-24 (`run_husain_loop_at_cell` return) | `-> HusainLoopState` | Class 2 / Class 2 |
| **`EvictionAction`** | U-OD-27 (`evict_oldest_per_ring_buffer_policy` return) | `-> Result<EvictionAction, RingBufferError>` | Class 2 / Class 2 |
| **`AuditPayload`, `AuditLedger`** | U-OD-30 (`sign_audit_entry` param `payload`; `verify_hash_chain_integrity` param `ledger`) | `fn sign_audit_entry(payload : AuditPayload, …)` / `fn verify_hash_chain_integrity(ledger : AuditLedger)` | Class 2 / Class 2 (operator-decision) — see classification note |
| **`CardinalityCounters`** | U-OD-31 (`assert_per_tenant_cardinality_isolation` param `observed`) | `fn …(observed : CardinalityCounters)` | Class 2 / Class 2 |
| **Error types** — `BreakerEmissionError`, `DriftEmissionError`, `EmissionContractViolation`, `EvalShapeViolation`, `CardinalityViolation`, `CanonicalValueViolation`, `MonotonicityViolation`, `AuthorityViolation`, `CellBindingViolation`, `CellBindingError`, `NamespaceSetMismatch`, `AttributeCountMismatch`, `RingBufferError`, `ReachabilityViolation`, `EmissionModeViolation`, `PreCollectorRedactionViolation`, `CrossTenantAggregationViolation`, `PerTenantCardinalityViolation`, `PerTenantAlertingViolation`, `HashChainBreach`, `TenantIdMissingViolation`, `PreservationViolation`, `CrossAxisCompositionPending`, `AttributeCountMismatch` | Every unit with a `Result<…, E>` signature (≈25 units) | `-> Result<(), CardinalityViolation>` etc. | Class 1 / Class 3 (informational) — see note |

**Classification notes (per-type, FM-D / decision-vocabulary discipline):**

- **`SpanRef` / `SpanAttributes` / `EventEmission`** are the load-bearing trio — *decided* Class 3. They are consumed at 5 / 3 / 2 units respectively. They may *look* like OTel-SDK primitives (the OTel span model has a `Span` and an attributes bag), but the OD plan treats them as harness-internal abstractions: `EventEmission` is a harness return-record (it is not an OTel SDK type), and `SpanRef` is used as an opaque parent-span handle the harness threads through emission functions. **The operator must confirm per type whether it is (a) a thin OTel-SDK alias — in which case U-OD-04 (the OTel base-layer anchor) should declare the alias and every consumer must add a `Depends on: [U-OD-04]` edge — or (b) a harness-introduced abstraction — in which case it needs a carrier unit, and may be an X-AL-3 design extension if it has no spec basis.** *Decision-vocabulary: proposing* on the (a)/(b) split; *decided* that the gap blocks materialization either way.
- **`AuditPayload` / `AuditLedger`** (U-OD-30) — these likely belong to the IS axis (IS owns the state-ledger / hash-chain primitive per `harness-od/CLAUDE.md` §1.4). U-OD-30 *does* declare cross-axis IS edges (`C-IS-14 §14.2`, `C-IS-13 §13.5`), so the carrier may resolve cross-axis at the IS plan — but the plan never names the IS-side carrier type, and the cross-axis edge is annotated by contract section, not by exported type. *Proposing* Class 2: the operator confirms whether `AuditPayload`/`AuditLedger` are IS-exported (then the U-OD-30 cross-axis edge annotation must name the exported type, AS-precedent style) or OD-local (then OD needs a carrier).
- **Error types** — the ≈24 distinct `Result` error types have no declaration site. In a pyright-strict Python build each must be a real class. This is a Class 1 / §2.7.6 Class 3 informational drift, NOT a halt: error types are conventionally thin (`class CardinalityViolation(HarnessError): ...`) and a coding agent can materialize them inline at first-consuming unit without ambiguity — there is no shape to get wrong. Recorded so the count is visible; the resolution is a one-line plan note sanctioning inline error-type materialization (the AS Pattern-B "inline-auxiliary-type discipline" option). It does not, on its own, fork any unit.

**Why the plan's own audit missed this.** `Implementation_Plan_Operational_Discipline_v2_1.md` §6.5 reports "A3 Spec extension ✅ No" and "A6 Missing dependencies ✅ PASS"; §6.4 (implementation-grade detail) reports signatures "present". The §6.5 audit checked `Depends on:`-clause *completeness against declared edges* — it did not check whether every *type at a signature position* has a carrier. The blind spot is exactly where the systemic defect lives — itself evidence the pattern is structural, not a per-unit slip (same marker as the AS plan's §5.4.1 blind spot).

---

## Pattern M-2 — hidden dependency coupling: type/output consumed without a declared `Depends on` edge (systemic)

A unit consumes a sibling unit's declared type, constant, or output but the carrier is **not reachable in the consuming unit's transitive `Depends on` cone**. Distinct from M-1 (M-1 = no carrier anywhere; M-2 = carrier exists but is unreachable — the graph is incomplete). The transitive-cone rule is applied uniformly (per Method §1): a finding requires the carrier be unreachable by *any* dependency path, not merely absent from the direct `Depends on:` list. ≥3 occurrences → systemic per SKILL.md §6 — the threshold is crossed by the U-OD-21→U-OD-20, U-OD-33→U-OD-14, and U-OD-22→`WorkloadClass` rows (three unambiguous no-path cases); the U-OD-32 case is a transitive-resolved direct-edge-clarity drift, NOT a fourth occurrence.

| Consuming unit | Consumed surface | Carrier (declared elsewhere) | Edge declared? | §4.1 / §2.7.6 |
|---|---|---|---|---|
| **U-OD-32** | `VerificationDimension.CARDINALITY_BUDGET_TIGHTENING` is specified (v2.1 §3.8.1 line 2242) as `target.tenant_rate_limit ≤ source.tenant_rate_limit` — `tenant_rate_limit` is the per-cell cardinality-budget field declared by **U-OD-13** (`PerCellCardinalityBudget`). U-OD-32 `Depends on:` includes **U-OD-17**, and U-OD-17 `Depends on: [U-OD-01, U-OD-13, …]` — so U-OD-13 **IS in U-OD-32's transitive cone.** Per the Method §1 transitive-cone rule, the carrier resolves. NOT an M-2 finding. Recorded only as a *direct-edge-clarity* note: U-OD-32 consumes U-OD-13's field directly enough that an explicit `Depends on: [U-OD-13]` edge would be best-practice; absence is documentation drift, not a materializability defect. | U-OD-13 (transitively in-cone via U-OD-17) | Resolves transitively — clean | Class 1 / — (drift only, not a fork) |
| **U-OD-33** | `PreservationDimension` rows are annotated in U-OD-33's own signature block as `CARDINALITY_BUDGET // U-OD-13 + U-OD-14` and `REDACTION_CLASS // U-OD-15 + U-OD-16 + U-OD-17`. The `CARDINALITY_BUDGET` preservation invariant (`SCALAR_MONOTONIC_TIGHTENING_LE`) is computed over U-OD-13's `tenant_rate_limit` and **U-OD-14's cardinality-safe/-prohibited sets**. U-OD-33 `Depends on:` includes U-OD-17 (transitively reaches U-OD-13/15/16) — so U-OD-13 and U-OD-16 are in-cone — but **U-OD-14 is reachable from NO U-OD-33 ancestor path** (U-OD-14 deps are U-OD-05/U-OD-13; U-OD-33's cone reaches U-OD-05 and U-OD-13 but not U-OD-14 itself — U-OD-14 is a *consumer* of U-OD-05/U-OD-13, not on a path *to* U-OD-33). `CARDINALITY_BUDGET` preservation over U-OD-14's sets has no carrier edge. | U-OD-14 | **No** — U-OD-33 `Depends on: [U-OD-05, U-OD-07, U-OD-11, U-OD-12, U-OD-17, U-OD-32, +cross-axis]`; **U-OD-14 absent and not transitively reachable** | Class 2 / Class 2 (operator-decision) |
| **U-OD-22** | `compute_alerting_signal` consumes `WorkloadClass` (`per_class_cost_ceiling : Map<WorkloadClass, float>`; param `workload_class : WorkloadClass`). `WorkloadClass` is a CP-axis type (ADR-D4 workload classes; CP owns routing/workload). No OD unit declares it. | (none in OD) — CP-axis type | **No** — U-OD-22 `Depends on: [U-OD-01, U-OD-12, U-OD-18, U-OD-19, U-OD-21]`, **no cross-axis CP edge for `WorkloadClass`** | Class 3 / Class 1 (halt) — folds into M-1 as well (no carrier *and* no edge) |
| **U-OD-28** | `PerCellPlacement.emission_window`/`emission_batch` are specified `= BATCH_SPAN_PROCESSOR_WINDOW`/`…_BATCH_SIZE` "from U-OD-27" — U-OD-28 consumes two named constants U-OD-27 declares. U-OD-28 `Depends on: [U-OD-01, U-OD-02, U-OD-27]` — **edge present**; clean. Recorded here as the contrast case (the plan *can* declare these edges; M-2 is omission, not impossibility). | U-OD-27 | Yes | — (clean) |
| **U-OD-31** | `assert_per_tenant_cardinality_isolation` enforces "per-tenant cardinality exceeds `tenant_rate_limit` from U-OD-13" (acc #5). U-OD-31 `Depends on:` includes U-OD-13 — **edge present**; clean. Contrast case. | U-OD-13 | Yes | — (clean) |

The U-OD-22 `WorkloadClass` row is the most severe — it is simultaneously an M-1 (no carrier anywhere in OD) and an M-2 (no cross-axis edge) finding, and `WorkloadClass` is owned by another axis. Either OD must declare a cross-axis CP edge that names the exported `WorkloadClass` type, or — if no CP unit exports it — this is an X-AL-3 surface (OD consuming a CP type with no composition seam). Folded into both Pattern tables; counted once in the disposition (U-OD-22 = FORK).

---

## Pattern M-3 — stale cross-axis edge cardinality in U-OD-34 (single-unit, NOT systemic — surfaced for completeness)

U-OD-34's manifest signature hardcodes `cross_axis_edge_count : int // = 28` and `cross_axis_edge_breakdown // {IS: 6, AS: 10, CP: 12}`, and acc #3/#4 + tests `test_cross_axis_edge_count_twenty_eight` / `test_cross_axis_edge_breakdown_6_10_12` assert these values "per Stage 4 §4.6". But OD plan **v2.4 §4.5.1** deleted/remapped the IS-consuming edges from 6 to **4** (C3-15 Path (i-refined)), and v2.5 §0.3 preserves the v2.4 §4.5.1 4-edge enumeration. U-OD-34 is on the v2.5 "preserved verbatim from v2.4" list (§0.3) — so its body still carries the **pre-C3-15 count of 28 / IS:6**, contradicting the v2.4-canonical 26 / IS:4. This is the `CXA-OD-IS-EDGE-DRIFT` carry-forward already logged at `harness-od/CLAUDE.md` §5.2 / §2.2 as a Class 3 *informational* item — but note it surfaces *inside a unit signature and three acceptance-criterion tests*, not only in §4.5. As written, U-OD-34's `test_cross_axis_edge_count_twenty_eight` would **fail** against the v2.4-canonical edge graph: the unit is not materializable to pass its own tests. *Decision-vocabulary: decided.* §4.1 Class 2 (current-phase plan revision — conform U-OD-34's count + breakdown + the two tests to v2.4 §4.5.1); §2.7.6 Class 2 (the v2.4 edge delta is operator-ratified already, so this is a determinate propagation the v2.5 pass missed). NOT escalated to Class 3 — the resolution is plan-internal, no upstream artifact changes.

---

## Per-unit materializability finding table

| Unit | Materializability finding | Verdict |
|---|---|---|
| U-OD-01 | `PersonaTier`/`DeploymentSurface`/`CellID`/`CellStatus` all declared in-unit; L0 anchor, `Depends on: []`. `CellBindingViolation` error type undeclared (M-1 error-type tail — Class 1, inline). | **CLEARED** |
| U-OD-02 | v2.5-revised. `BackendClass`/`CandidateWitness`/`PerCellBackendBinding` declared in-unit; `CellID` in-cone via U-OD-01. No undeclared structured type. Verbatim 3→7 conformance is the §4A axis (out of scope here). | **CLEARED** |
| U-OD-03 | `SurfaceCommitmentClass`/`CommittedSurface`/`DeferredSurface` declared in-unit; deps U-OD-01/02 in-cone. Materializable. | **CLEARED** |
| U-OD-04 | v2.5-revised. `GenAiOperation`/`AttributeTier`/`GenAiAttribute`/`SPAN_NAME_FORMAT`/`BASE_METRIC_NAME` declared in-unit; L0 anchor. `GenAiAttribute` is the carrier other units consume (U-OD-09) — see U-OD-09. Materializable. | **CLEARED** |
| U-OD-05 | `NamespaceSourceAxis`/`NamespaceMapRow` declared in-unit; dep U-OD-04 in-cone. `AuthorityViolation` error type — M-1 tail (inline). Materializable. | **CLEARED** |
| U-OD-06 | `AS_SOURCE_NAMESPACE_PREFIXES` is a `Set<string>` const; cross-axis edge to U-AS-33 declared. `NamespaceSetMismatch`/`AttributeCountMismatch` error types — M-1 tail (inline). Materializable. | **CLEARED** |
| U-OD-07 | `CP_SOURCE_NAMESPACE_PREFIXES` `Set<string>`; cross-axis edge to U-CP-54 declared. Materializable. | **CLEARED** |
| U-OD-08 | `F3LifecycleEventClass`/`LifecycleEventMapping` declared in-unit; cross-axis U-CP-54 edge declared; deps U-OD-04/05/06/07 in-cone. Materializable. | **CLEARED** |
| U-OD-09 | v2.5-revised. `HARNESS_BREAKER_ATTRIBUTES` is typed `List<GenAiAttribute>` — `GenAiAttribute` carrier is U-OD-04, **but U-OD-09 `Depends on: [U-OD-07]` only — U-OD-04 NOT in U-OD-09's cone** (U-OD-07's cone reaches U-OD-04/05; so `GenAiAttribute` IS transitively in-cone via U-OD-07→U-OD-04). Edge resolves transitively — clean. **`SpanRef` (M-1) + `EventEmission` (M-1) undeclared at `emit_breaker_trip_span_event`.** Plus the §4A FF-1 (acc #2 tier split, no spec basis) carried unresolved. | **FORK** |
| U-OD-10 | `NamespacePrecedenceRule`/`NamespaceCollisionResolution`/`CacheTierSubsetInvariant` declared in-unit. **`SpanAttributes` (M-1) undeclared at `enforce_otel_canonical_value`.** | **FORK** |
| U-OD-11 | v2.5-revised. `SamplingMode`/`PerDeploymentSurfaceSamplingMode`/`ALWAYS_SAMPLED_EVENT_CLASSES` declared in-unit; `SamplingDecision` return type undeclared — but it is a thin enum-like result, M-1 tail (inline). Deps in-cone. Materializable. | **CLEARED** |
| U-OD-12 | v2.5-revised. `PerCellBaseRateEnvelope`/`TailKeepRule`/`BASE_RATE_SAMPLED_EVENT_CLASSES` declared in-unit; `CellID` in-cone via U-OD-01. Materializable. | **CLEARED** |
| U-OD-13 | `PerCellCardinalityBudget` declared in-unit; deps U-OD-01/05 in-cone. Materializable. (U-OD-13 is the *carrier* the M-2 finding shows U-OD-32/33 fail to depend on.) | **CLEARED** |
| U-OD-14 | v2.5-revised. `CARDINALITY_SAFE_ATTRIBUTES`/`CARDINALITY_PROHIBITED_ATTRIBUTES` are `Set<string>` consts; `assert_*` fns return `Result<(), CardinalityViolation>`. No undeclared structured type beyond the error-type tail. Materializable. | **CLEARED** |
| U-OD-15 | `AttributeClassification` declared in-unit; `DEFAULT_OFF/ON` `Set/List<string>`. Materializable. | **CLEARED** |
| U-OD-16 | `ContentCapturePosture`/`PerPersonaTierRedactionPosture` declared in-unit; deps U-OD-01/15 in-cone. Materializable. (Carrier of `ContentCapturePosture` for U-OD-17/32.) | **CLEARED** |
| U-OD-17 | `REDACTION_CLASS_ORDER`/`class_index`/`assert_*` consume `ContentCapturePosture` (carrier U-OD-16, in-cone). Cross-axis deps are placeholders `U-AS-NN`/`U-CP-NN` — see Pattern M-1 rejected-note on placeholders. `MonotonicityViolation` M-1 tail. Materializable. | **CLEARED** |
| U-OD-18 | `PriceRateKey`/`PriceRateEntry`/`SpanCostInputs` declared in-unit; `opaque PRICE_TABLE_REF : Reference` — `Reference` is an opaque-marker; `compute_span_cost` self-contained. Materializable. | **CLEARED** |
| U-OD-19 | `SandboxOverhead`/`SpanTotalCost`/`FanOutPattern`/`FanOutRollupResult` declared in-unit. **`SpanRef` (M-1) undeclared at `rollup_fanout_at_close`.** | **FORK** |
| U-OD-20 | `SpanCostRecord`/`F2_12_DeferredSurface`/`F2_12_AffectedContractNotation`/`RevisionStep` declared in-unit (v2.2 cascade). **`SpanRef` (M-1) undeclared at `attach_idempotency_key_to_cost_record` param `span`.** | **FORK** |
| U-OD-21 | `CrossFamilyTag`/`RollupAxis`/`CrossFamilyCostRollup`/`TokenizerVersionAnchor`/`FallbackChainCostComposition` declared in-unit; consumes `SpanCostRecord` (carrier U-OD-20) — but U-OD-21 `Depends on: [U-OD-04, U-OD-18, U-CP-NN]` — **U-OD-20 NOT in cone.** `rollup_costs_by_axis(span_records : List<SpanCostRecord>)` consumes a U-OD-20 type with no edge → M-2. *Proposing* — `SpanCostRecord` could be re-keyed off U-OD-18's `SpanCostInputs`, but as written the param type is U-OD-20's. | **FORK** |
| U-OD-22 | `DashboardBindingForm`/`AlertingHook`/`CellDashboardBinding`/`AlertingThresholdComposition`/`AlertingSignal`/`DashboardBackendConsolidation` declared in-unit. **`WorkloadClass` (M-1 + M-2 — CP-axis type, no carrier, no cross-axis edge); `DashboardRef` (M-1) undeclared.** | **FORK** |
| U-OD-23 | `OperatorBurdenEvalPrimitive`/`ComputationKind`/`EvalPrimitiveDeclaration`/`EvalEmissionContract` declared in-unit. **`ChildSpanRef` (M-1) undeclared at `emit_eval_as_child_span` return** — `ChildSpanRef` is in the `SpanRef`-family; its classification is the same unresolved operator decision as `SpanRef`. Same family, same pending decision as U-OD-09/19/20/25/30 → same verdict for consistency. | **FORK** |
| U-OD-24 | `EvalDashboardForm`/`AlignmentFloorAlertingPosture`/`HusainLoopBinding`/`CellEvalDashboardBinding` declared in-unit. **`HusainLoopState` (M-1) undeclared at `run_husain_loop_at_cell` return.** | **FORK** |
| U-OD-25 | `AlignmentFloorPrimitive`/`AlignmentFloorThreshold`/`ObservationWindow`/`DriftDetectedEventAttributes` declared in-unit. **`SpanRef` + `EventEmission` (M-1) undeclared at `emit_drift_event`.** | **FORK** |
| U-OD-26 | `EvalKindDiscriminator`/`EvalSpanShape`/`SamplingPostureF18` declared in-unit. **`SpanAttributes` (M-1) undeclared at `classify_eval_span`.** Cross-axis CP edge declared (placeholder). | **FORK** |
| U-OD-27 | `CollectorTopology`/`InProcessCollectorBinding`/`RingBufferTraceStoragePolicy`/`TuiTraceBrowserSurface`/`TuiQuery` declared in-unit. **`SpanRow` + `EvictionAction` (M-1) undeclared** at `query_ring_buffer_via_tui` / `evict_oldest_per_ring_buffer_policy` returns. | **FORK** |
| U-OD-28 | `CollectorPlacement`/`PerCellPlacement` declared in-unit; consumes U-OD-27 constants with the **U-OD-27 edge present** (clean M-2 contrast). No undeclared structured type. (§4A FF-2 verbatim divergence is out of scope here.) | **CLEARED** |
| U-OD-29 | `SandboxTier`/`OtlpReachabilityClass`/`SandboxTierReachability` declared in-unit; consumes `CollectorPlacement` (carrier U-OD-28, dep declared, in-cone). Materializable. (§4A FF-3 `Tier-0..3` ADR-verify is out of scope here.) | **CLEARED** |
| U-OD-30 | v2.5-revised. `TenantSeparationStrategy`/`PerTenantSeparation`/`SignatureAlgorithm`/`AuditSignatureAttributes` declared in-unit. **`SpanRef` (M-1) at `assert_tenant_id_on_every_span…`; `AuditPayload`/`AuditLedger` (M-1, proposing — possibly IS-exported) undeclared.** | **FORK** |
| U-OD-31 | `CrossTenantAggregationProhibition` declared in-unit. **`SpanAttributes` + `DashboardQuery` + `CardinalityCounters` (M-1) undeclared**; consumes `ContentCapturePosture` (U-OD-16, in-cone) and `AlertingSignal` (U-OD-22, dep U-OD-22 declared — in-cone). | **FORK** |
| U-OD-32 | v2.5-revised. `BridgingArcTransition`/`TransitionAxis`/`VerificationDimension`/`TransitionVerificationResult`/`VerificationOutcome` declared in-unit. `CARDINALITY_BUDGET_TIGHTENING` consumes U-OD-13's `tenant_rate_limit` — **U-OD-13 IS transitively in-cone via U-OD-17** (U-OD-32→U-OD-17→U-OD-13). NOT an M-2 finding; only a Class-1 direct-edge-clarity drift. Materializable. | **CLEARED** |
| U-OD-33 | v2.5-revised. `PreservationDimension`/`PreservationInvariant`/`InvariantForm`/`EnforcementLayer` declared in-unit; consumes `BridgingArcTransition` (U-OD-32, in-cone). U-OD-13/U-OD-16 are transitively in-cone via U-OD-17. **M-2: the `CARDINALITY_BUDGET` invariant is computed over U-OD-14's cardinality sets; U-OD-14 is absent from `Depends on` AND unreachable by any dependency path** (U-OD-14 is a consumer of U-OD-05/13, not on a path to U-OD-33). | **FORK** |
| U-OD-34 | `SubstrateSeamExport`/`SubstrateSeamExportsManifest`/`F2_12_CarryForwardInheritance`/`ManifestScope`/`ConsumerAxis` declared in-unit. **M-3: hardcoded `cross_axis_edge_count = 28` / `{IS:6,…}` + two tests contradict v2.4 §4.5.1 (26 / IS:4).** No undeclared structured type. | **CONFORM** |

---

## §4.1 severity classification

- **Pattern M-1 (Class 3, discriminator (a)+(b)).** Most of M-1 resolves plan-internal (declare a carrier unit + add `Depends on` edges) → discriminator (a), Class 2 in isolation. But the `SpanRef`/`SpanAttributes`/`EventEmission` trio and the `AuditPayload`/`AuditLedger`/`WorkloadClass` types raise an *unresolved* question — are they OTel-SDK aliases, harness abstractions, or other-axis exports? If any is a harness-introduced abstraction with no spec basis, resolving it requires an OD-spec extension (X-AL-3 / I-2) → discriminator (b), Class 3. Because the pattern *contains* at least one such type and the classification cannot be settled from `design-substrate/` alone, the pattern as a whole is **Class 3, *proposing*** on the per-type (a)/(b) split.
- **Pattern M-2 (Class 2, discriminator (a)).** Missing `Depends on` edges where the carrier exists in-plan but is unreachable by any dependency path (U-OD-14 → U-OD-33; U-OD-20 → U-OD-21). Resolution is a plan-internal dependency-graph completion — add the edges, re-verify acyclicity. No upstream artifact changes. Exception: the U-OD-22 `WorkloadClass` row escalates to Class 3 because the carrier is *not* in-plan and may need a cross-axis composition seam (it folds into M-1). The U-OD-32→U-OD-13 case is NOT an M-2 finding — U-OD-13 is transitively in-cone via U-OD-17 — only a Class-1 direct-edge-clarity drift.
- **Pattern M-3 (Class 2, discriminator (a)).** U-OD-34's stale 28/IS:6 count — plan-internal conformance to the already-ratified v2.4 §4.5.1 edge delta.
- **Class 1:** the ≈24 `Result` error types (M-1 tail) — inline-materializable, no shape ambiguity; one-line plan note. And U-OD-34's two stale tests are the concrete Class-1 surface of M-3.

Severity distribution: **2 / 5 / 2** (the two Class-3 are the two systemic patterns; the five Class-2 are M-3 + the four plan-internal M-2/M-1-carrier dispositions; two Class-1 are the error-type tail + M-3 tests). Not skewed (FM-A / FM-B check). The §2.7.6 fork dispositions: the M-1 type-classification decision is **Class 1 (halt)** for the 9 units that consume `SpanRef`/`SpanAttributes`/`EventEmission`/`WorkloadClass` before the carrier question is settled; M-2/M-3 are **Class 2 (operator-decision / determinate propagation)**.

---

## Systemic-pattern section (SKILL.md §6 — ≥3 occurrences)

The §6 threshold (≥3 → systemic pattern) is crossed **twice**, by two distinct materializability diseases — neither of which the §4A verbatim audit could have caught (it was scoped to verbatim-claim divergence only):

- **Pattern M-1 — undeclared auxiliary types, no carrier.** ≥11 H_T structured types across ≥10 units (U-OD-09/10/19/20/22/24/25/26/27/30/31). The AS Pattern B shape. The OD plan has **no §5.4.1-style auxiliary-type audit at all** (the AS plan at least had one, blind-spotted; OD has none) — so the gap was never even nominally checked. The plan's §6.5 "A3 Spec extension ✅ No / A6 Missing dependencies ✅ PASS" is the false-clean marker.
- **Pattern M-2 — hidden dependency coupling.** 3 units (U-OD-21, U-OD-22, U-OD-33) consume a sibling's type/output whose carrier is unreachable by any dependency path — U-OD-21→U-OD-20 (`SpanCostRecord`), U-OD-33→U-OD-14 (cardinality sets), U-OD-22→`WorkloadClass` (cross-axis CP, also M-1). The U-OD-32→U-OD-13 case is *transitive-resolved* (U-OD-32→U-OD-17→U-OD-13) and is NOT a fourth occurrence — it is a Class-1 direct-edge-clarity drift. The plan's §4.4 Kahn acyclicity proof is sound *for the edges as declared* — but the graph is **incomplete**: the M-2 edges are missing edges. Adding U-OD-21→U-OD-20 and U-OD-33→U-OD-14 introduces no cycle (both carriers sit at lower topological levels), but §4.2 levels must be re-verified after the edges are added.

Both patterns have the same single-revision-pass resolution shape as the AS Pattern B §4A recommendation: one `implementation-planner` pass declaring carriers + completing dependency edges, with a per-type factor-out-vs-extension operator classification for the M-1 types.

---

# §4A Resolution Recommendation — OD-plan materializability cluster (M-1 / M-2 / M-3)

*Appended 2026-05-15 per `systems-architect` SKILL.md §4A (Phase-7 tension-resolution mode). This audit report is the canonical systemic-tension record for the OD-plan **materializability** cluster — distinct from, and additional to, the OD-plan **verbatim-divergence** cluster recorded at `.harness/verbatim_audit_od_plan.md` §4A. The §4A recommendation is **a recommendation** — the operator holds decision authority (§4A.7).*

## §4A.1 — Precise tension statement

The OD plan (v2.5, with v2.1 unit bodies for the 25 unrevised units) carries two systemic materializability defects, both crossing the SKILL.md §6 ≥3-occurrence threshold, plus one single-unit cross-axis-count drift:

- **Pattern M-1:** ≥11 auxiliary H_T types consumed at typed signature positions across ≥10 units with no declaring carrier and no dependency-graph edge.
- **Pattern M-2:** ≥3 units consume an in-plan sibling's type/output without declaring the `Depends on` edge.
- **Pattern M-3:** U-OD-34's signature + 2 tests hardcode the pre-C3-15 cross-axis edge count (28 / IS:6), contradicting the v2.4-canonical 26 / IS:4.

Precise per-unit / per-type detail is in the Pattern tables above; not re-summarized here per §4A.2.

## §4A.2 — Authority-chain placement

`CLAUDE.md` §1.3 chain: ADR → ADD v1.3 → PRD v1.1 → per-axis spec v1.x → per-axis plan v2.x.

- **M-1, most types** — the type is a faithful factor-out of spec content (an emission handle, a dashboard reference) the OD spec implies but does not enumerate field-by-field. Resolution is plan-internal: the plan declares a carrier unit and adds edges. Phase-6 artifact, discriminator (a).
- **M-1, the open types** (`SpanRef`, `SpanAttributes`, `EventEmission`, `AuditPayload`, `AuditLedger`, `WorkloadClass`) — the operator must confirm per type whether it is (i) a thin OTel-SDK / stack alias (no carrier needed beyond a type-alias line at U-OD-04), (ii) a faithful factor-out (plan-internal carrier), (iii) an other-axis export (`AuditPayload`/`AuditLedger` → IS; `WorkloadClass` → CP — needs a *named* cross-axis edge), or (iv) a plan-introduced H_T design extension with no spec basis (X-AL-3 / I-2 — route to OD-spec back-flow). Only (iv) escalates to Phase-5.
- **M-2** — pure Phase-6 plan dependency-graph completion. Discriminator (a).
- **M-3** — Phase-6 plan conformance to the *already-ratified* v2.4 §4.5.1 edge delta. Discriminator (a); determinate.

## §4A.3 — §2-discipline analysis

- **Five-axis:** every M-1/M-2 type is an OD-axis observability/cost/audit primitive — except `WorkloadClass` (CP), `AuditPayload`/`AuditLedger` (likely IS). Those three are cross-axis composition surfaces; the rest is within-axis plan completion.
- **Probabilistic–deterministic boundary:** every undeclared type is a deterministic-side structured type. An undeclared `SpanRef` makes every emission function un-typeable; pyright-strict will not compile the unit. The cost of leaving M-1 unresolved is total — the unit literally cannot be built.
- **Decision ordering:** M-2 and M-3 are D-level (derivative materialization slips, determinate fix). M-1 is D-level for the factor-out types and potentially F-/D-level for any (iv) design-extension type — *that* the OD axis emits via a span handle is held by the spec; *whether* the plan introduced a structured type the spec never sanctioned is the open question.

## §4A.4 — Recommended reading

**A single `implementation-planner` revision-pass on `Implementation_Plan_Operational_Discipline` (next version bump), carrying three internal sub-passes:**

1. **M-1 sub-pass — carrier declaration.** For each undeclared type: either declare a carrier (`record`/`enum`/type-alias) in a unit with an explicit `Depends on` edge to it, or document an inline-auxiliary-type materialization discipline (type materialized inline at first-consuming unit, with a §3.x audit table — the AS Pattern-B option). The `SpanRef`-family belongs at U-OD-04 (the OTel base-layer anchor) if the operator rules them OTel aliases; the error-type tail (≈24 types) is sanctioned for inline materialization by a single plan note. Author an OD §5.4.1-equivalent auxiliary-type audit so the gap is closed structurally, not unit-by-unit.
2. **M-2 sub-pass — dependency-graph completion.** Add `Depends on` edges: U-OD-33 → U-OD-14; U-OD-21 → U-OD-20; and (best-practice direct-edge clarity, not strictly required) U-OD-32 → U-OD-13, U-OD-33 → U-OD-13. Re-run §4.4 Kahn acyclicity + §4.2 level decomposition after the edges are added (the levels likely hold, but must be re-verified).
3. **M-3 sub-pass — U-OD-34 count conformance.** Conform `cross_axis_edge_count`, `cross_axis_edge_breakdown`, acc #3/#4, and tests `test_cross_axis_edge_count_twenty_eight` / `test_cross_axis_edge_breakdown_6_10_12` to the v2.4 §4.5.1 4-IS-edge enumeration (26 total / IS:4). This is a determinate propagation of the already-ratified C3-15 delta the v2.5 pass missed by preserving U-OD-34 verbatim.

### Items requiring an explicit operator decision (NOT plan-internal conform)

1. **M-1 per-type factor-out-vs-extension-vs-cross-axis classification.** For `SpanRef` / `SpanAttributes` / `EventEmission` / `ChildSpanRef` (OTel-alias-vs-harness-abstraction), `AuditPayload` / `AuditLedger` (IS-export-vs-OD-local), `WorkloadClass` (CP-export — needs a named cross-axis edge, and OD must confirm a CP unit exports it). §2.7.6 **Class 1 (halt)** for the 9 units consuming them until classified.
2. **U-OD-22 `WorkloadClass` cross-axis seam.** If no CP unit exports `WorkloadClass`, this is an X-AL-3 surface (OD consuming a CP type with no composition seam) — route to CXA / CP back-flow. §2.7.6 **Class 1 (halt)**.

## §4A.5 — Tiebreaker check

No ADR / ADD / PRD revision postdates the OD spec and re-commits a carrier for the M-1 types. The OD spec v1.2→v1.3 change-note records only the §14.5 cost-attribution amendment — it does not enumerate `SpanRef`, `SpanAttributes`, `EventEmission`, dashboard types, or audit-payload types as named schemas. **Determinate for M-2 and M-3: plan-internal completion. Non-determinate for M-1: the per-type classification in §4A.4's decision list is genuinely owed.**

**Load-bearing-artifact flag:** the resolution touches no `CLAUDE.md` anti-leakage rule and no F-ADR — unless the operator rules an M-1 type a design extension (X-AL-3), in which case OD-spec back-flow is engaged. The cluster needs operator **ratification** of the M-2/M-3 plan-internal direction + the M-1 per-type classification.

## §4A.6 — Fork classification

Per `Project_Workflow_v1_8.md` §2.7.6: **Class 1 (halt-execution)** for the units carrying an unclassified M-1 type (U-OD-09/10/19/20/22/23/25/26/30/31 — `SpanRef`-family / `SpanAttributes` / `WorkloadClass`; the type-classification decision is a precondition for materialization). **Class 2 (operator-decision)** for the remaining M-1 plan-internal-carrier units (U-OD-24/27 — `HusainLoopState`/`SpanRow`/`EvictionAction`, determinate carrier-declaration once authorized) and the M-2 / M-3 dispositions (U-OD-21/33 graph-completion; U-OD-34 count conformance) — determinate, operator ratifies. **U-OD-01 and U-OD-04 are the landed L0 anchors** — see retrospective note below.

## §4A.7 — Operator decision required

The operator decides. Operator actions:

1. **Ratify** the M-2 dependency-graph completion (U-OD-32→13; U-OD-33→13/14/16; U-OD-21→20) and the M-3 U-OD-34 count conformance — both authority-chain-determinate.
2. **Classify** each M-1 open type (`SpanRef`/`SpanAttributes`/`EventEmission`/`ChildSpanRef`/`AuditPayload`/`AuditLedger`/`WorkloadClass`) as OTel-alias / factor-out / cross-axis-export / design-extension.
3. **Disposition** the U-OD-22 `WorkloadClass` cross-axis seam — confirm a CP exporter exists, or route to CXA back-flow.
4. **Authorize** the U-OD-01 / U-OD-04 retrospective check (below) before the revision-pass lands.

On ratification: one `implementation-planner` revision-pass (M-1 carriers + M-2 edges + M-3 count + new auxiliary-type audit) → OD plan version bump → re-clear → land. If any M-1 type is ruled a design extension, a `spec-writer` OD-spec extension precedes the plan pass.

---

## Retrospective concern — landed units U-OD-01 and U-OD-04

`harness-od/CLAUDE.md` §3 names U-OD-01 and U-OD-04 as the two L0 anchors; the MEMORY index notes "7b: 12/12 operational-minimum units landed 2026-05-15". Both are on the v2.5 "preserved verbatim" / v2.5-revised list.

- **U-OD-01 — clean on materializability.** `PersonaTier`/`DeploymentSurface`/`CellID`/`CellStatus` are all declared in-unit; `Depends on: []`; the only undeclared type is `CellBindingViolation` (M-1 error-type tail, inline-materializable). No retrospective concern beyond the generic error-type note. The pass mandate's `CellID` flag resolves clean — U-OD-01 *is* the `CellID` carrier.
- **U-OD-04 — materializability-clean, but it is the proposed M-1 carrier site.** U-OD-04 declares `GenAiAttribute`, which U-OD-09's `HARNESS_BREAKER_ATTRIBUTES : List<GenAiAttribute>` consumes. If the operator rules the `SpanRef`-family to be OTel-SDK aliases, the §4A.4 recommendation places those alias declarations *at U-OD-04*. **U-OD-04 is landed.** If the revision-pass adds `SpanRef`/`SpanAttributes`/`EventEmission` type-aliases to U-OD-04, the landed U-OD-04 source must be revised to match — i.e. **U-OD-04 may need re-visiting**, and the operator should not treat its landed status as closing the M-1 carrier question. Note also: U-OD-04 was the subject of the already-filed **Tension 004** (verbatim — span name / `GenAiOperation` / `AttributeTier` / `BASE_METRIC_NAME`), absorbed at v2.5 §3.2.1; if U-OD-04 landed against the *v2.1* body it landed against the verbatim-divergent state, and that retrospective is owned by the §4A verbatim audit. This pass adds: even setting verbatim aside, U-OD-04 is the candidate M-1 alias-carrier and a landed unit — both retrospectives converge on "U-OD-04's landed materialization must be re-checked before/at the revision-pass."

Logged as a §2.7.6 **Class 3 (informational)** retrospective against the Phase 7 execution log; the U-OD-04 re-check is the operator action it triggers.

---

## Findings considered and rejected (transparency)

1. **`CellID` — checked hardest, holds.** The pass mandate explicitly flagged `CellID` and "whether U-OD-01 actually declares them". Verified: `record CellID { persona_tier : PersonaTier; deployment_surface : DeploymentSurface }` is in U-OD-01's Signatures block (v2.1 §3.1.1). Every consumer declares `Depends on: [U-OD-01]` or reaches it transitively. NOT a finding — recorded so the operator sees the negative result is a *result*.
2. **`GenAiAttribute` — carrier exists, in-cone.** U-OD-09's `HARNESS_BREAKER_ATTRIBUTES : List<GenAiAttribute>` consumes a U-OD-04 type. U-OD-09 `Depends on: [U-OD-07]`; U-OD-07 `Depends on: [U-OD-04, U-OD-05, …]` — so `GenAiAttribute` is transitively in U-OD-09's cone. Edge resolves. NOT an M-2 finding (contrast U-OD-32→U-OD-13, where no path exists). Checked, not assumed.
3. **OTel-SDK / stack primitives excluded (FM-D self-check).** `Duration`, `Result`, `Option`, `Map`, `Set`, `List`, `string`/`int`/`float`/`bool` are stack primitives — no carrier needed. `Reference` (U-OD-18 `opaque PRICE_TABLE_REF : Reference`) is explicitly an opaque marker the plan declares `opaque`; not an undeclared type. The `SpanRef`-family was NOT auto-excluded as OTel primitives — they are flagged precisely because the plan uses them as harness abstractions, and the OTel-vs-harness question is the operator's to settle (M-1 *proposing*).
4. **Cross-axis placeholder edges `U-AS-NN` / `U-CP-NN` / `U-IS-NN` — NOT a materializability finding here.** Units U-OD-06/07/08/17/19/20/21/23/26/27/29/30/33/34 carry `(cross-axis: …)` edges with `U-xx-NN` placeholder unit IDs. The edges are *declared* (target axis + contract section named) and resolve at U-OD-34's aggregate manifest; OD-axis-stream code can be built against the contract section. Placeholder *unit-ID* resolution is a CXA / 7c-composition concern, not a 7b OD-unit materializability blocker — excluded from M-1/M-2. (The one exception folded in: `WorkloadClass` at U-OD-22 has *no* cross-axis edge at all — that is the finding.)
5. **§4A verbatim divergences NOT re-litigated.** U-OD-02/04/09/11/12/14/30/32/33 carry verbatim-divergence findings resolved by the v2.5 conformance pass, and FF-1/FF-2/FF-3 (U-OD-09 acc #2, U-OD-28, U-OD-29) are carried by the §4A verbatim audit. This pass references them where a unit is FORK for *both* reasons (U-OD-09) but does not re-derive them — verbatim is the §4A audit's axis, materializability is this audit's.
6. **A8 (framing contamination) sweep.** No OD unit commits a persona/stack/deployment value the workspace `CLAUDE.md` framing leaves uncommitted. `DeploymentSurface`/`PersonaTier` are committed OD spec enums. No framing finding.
7. **Dependency-graph acyclicity — checked, no cycle finding.** §4.4's Kahn proof is sound for the declared edges. The M-2 finding is *missing edges* (incomplete graph), a distinct defect from a cycle — adding U-OD-32→13 / U-OD-33→13/14/16 / U-OD-21→20 introduces no cycle (all carriers sit at lower topological levels than their consumers). The graph is acyclic but incomplete.
8. **A7 (weak-source) / A5 (uncertainty signals).** Implementation-plan units are not confidence-tagged artifacts; their `[MODERATE]` tags (U-OD-18 extended-thinking note) are preserved verbatim from spec. Not a finding.
9. **U-OD-34 manifest structure — holds as a manifest.** The 8-export sub-section structure, `SubstrateSeamExport`/`SubstrateSeamExportsManifest` records are all in-unit-declared and materializable; the *only* U-OD-34 defect is the stale 28/IS:6 count (M-3). The manifest is otherwise clean.
10. **§6.5 anti-pattern self-audit checked against findings.** The plan's §6.5 "A6 Missing dependencies ✅ PASS" and "A3 Spec extension ✅ No" were tested against M-1/M-2 and found false-clean — the self-audit checked `Depends on:`-clause completeness against *declared* edges, not type-carrier reachability. Recorded as corroborating evidence the patterns are structural.

---

## Pipeline disposition

Per-unit verdict for `pipeline-cleared-queue.md` / `pipeline-fork-queue.md`. **CLEARED** = materializable as written, enters cleared queue. **CONFORM** = authority-chain-determinate plan-internal fix (no operator decision; `implementation-planner` applies, then clears). **FORK** = operator decision / classification / back-flow needed before clearing.

| Unit | Verdict | Basis |
|---|---|---|
| U-OD-01 | **CLEARED** | All types in-unit-declared; L0 anchor; `CellID` carrier. Error-type tail inline. |
| U-OD-02 | **CLEARED** | `BackendClass`/`CandidateWitness`/`PerCellBackendBinding` in-unit; `CellID` in-cone. |
| U-OD-03 | **CLEARED** | `SurfaceCommitmentClass`/`CommittedSurface`/`DeferredSurface` in-unit. |
| U-OD-04 | **CLEARED** | OTel base-layer types in-unit; L0 anchor. (Retrospective: candidate M-1 alias-carrier — see retrospective section.) |
| U-OD-05 | **CLEARED** | `NamespaceSourceAxis`/`NamespaceMapRow` in-unit. |
| U-OD-06 | **CLEARED** | `Set<string>` const; cross-axis U-AS-33 edge declared. |
| U-OD-07 | **CLEARED** | `Set<string>` const; cross-axis U-CP-54 edge declared. |
| U-OD-08 | **CLEARED** | `F3LifecycleEventClass`/`LifecycleEventMapping` in-unit; cross-axis edge declared. |
| U-OD-09 | **FORK** | M-1 `SpanRef` + `EventEmission` undeclared at `emit_breaker_trip_span_event` — §2.7.6 Class 1. (Also §4A FF-1 verbatim, carried by the verbatim audit.) |
| U-OD-10 | **FORK** | M-1 `SpanAttributes` undeclared at `enforce_otel_canonical_value` — §2.7.6 Class 1. |
| U-OD-11 | **CLEARED** | `SamplingMode`/envelope types in-unit; `SamplingDecision` is M-1 inline tail. |
| U-OD-12 | **CLEARED** | `PerCellBaseRateEnvelope`/`TailKeepRule` in-unit; `CellID` in-cone. |
| U-OD-13 | **CLEARED** | `PerCellCardinalityBudget` in-unit; deps in-cone. (Is the M-2 carrier U-OD-32/33 fail to depend on.) |
| U-OD-14 | **CLEARED** | `Set<string>` consts; only error-type tail undeclared. |
| U-OD-15 | **CLEARED** | `AttributeClassification` in-unit. |
| U-OD-16 | **CLEARED** | `ContentCapturePosture`/`PerPersonaTierRedactionPosture` in-unit. |
| U-OD-17 | **CLEARED** | Consumes `ContentCapturePosture` (U-OD-16, in-cone); cross-axis placeholder edges declared. |
| U-OD-18 | **CLEARED** | `PriceRateKey`/`SpanCostInputs` in-unit; `opaque Reference` declared. |
| U-OD-19 | **FORK** | M-1 `SpanRef` undeclared at `rollup_fanout_at_close` — §2.7.6 Class 1. |
| U-OD-20 | **FORK** | M-1 `SpanRef` undeclared at `attach_idempotency_key_to_cost_record` — §2.7.6 Class 1. |
| U-OD-21 | **FORK** | M-2 — consumes `SpanCostRecord` (U-OD-20) with no `Depends on` edge to U-OD-20 — §2.7.6 Class 2. |
| U-OD-22 | **FORK** | M-1 `WorkloadClass` (CP-axis type, no carrier, no cross-axis edge) + `DashboardRef` undeclared — §2.7.6 Class 1. |
| U-OD-23 | **FORK** | M-1 `ChildSpanRef` undeclared at `emit_eval_as_child_span` — same `SpanRef`-family pending operator classification as U-OD-09/19/20/25/30; FORK for consistency — §2.7.6 Class 1. |
| U-OD-24 | **FORK** | M-1 `HusainLoopState` undeclared at `run_husain_loop_at_cell` — §2.7.6 Class 2. |
| U-OD-25 | **FORK** | M-1 `SpanRef` + `EventEmission` undeclared at `emit_drift_event` — §2.7.6 Class 1. |
| U-OD-26 | **FORK** | M-1 `SpanAttributes` undeclared at `classify_eval_span` — §2.7.6 Class 1. |
| U-OD-27 | **FORK** | M-1 `SpanRow` + `EvictionAction` undeclared at ring-buffer fns — §2.7.6 Class 2. |
| U-OD-28 | **CLEARED** | `CollectorPlacement`/`PerCellPlacement` in-unit; U-OD-27 constant consumption has the edge (clean M-2 contrast). |
| U-OD-29 | **CLEARED** | `SandboxTier`/`OtlpReachabilityClass` in-unit; consumes `CollectorPlacement` (U-OD-28, in-cone). |
| U-OD-30 | **FORK** | M-1 `SpanRef` + `AuditPayload` + `AuditLedger` undeclared (latter two *proposing* — possibly IS-exported) — §2.7.6 Class 1. |
| U-OD-31 | **FORK** | M-1 `SpanAttributes` + `DashboardQuery` + `CardinalityCounters` undeclared — §2.7.6 Class 1. |
| U-OD-32 | **CLEARED** | `CARDINALITY_BUDGET_TIGHTENING` consumes U-OD-13's `tenant_rate_limit`; U-OD-13 transitively in-cone via U-OD-17 — no M-2 finding, only Class-1 direct-edge-clarity drift. Materializable. |
| U-OD-33 | **FORK** | M-2 — `CARDINALITY_BUDGET` invariant computed over U-OD-14's cardinality sets; U-OD-14 absent from `Depends on` and unreachable by any path — §2.7.6 Class 2. |
| U-OD-34 | **CONFORM** | M-3 — stale `cross_axis_edge_count = 28` / `{IS:6}` + 2 tests contradict v2.4 §4.5.1 (26 / IS:4); determinate plan-internal conformance to the already-ratified C3-15 delta. |

**Tally: CLEARED 19 · CONFORM 1 (U-OD-34 — M-3 count conformance) · FORK 14.**

Recount for accuracy: FORK units are U-OD-09, 10, 19, 20, 21, 22, 23, 24, 25, 26, 27, 30, 31, 33 = **14**. CLEARED = U-OD-01, 02, 03, 04, 05, 06, 07, 08, 11, 12, 13, 14, 15, 16, 17, 18, 28, 29, 32 = **19**. CONFORM = U-OD-34 = **1**. 19 + 1 + 14 = 34. ✓

The 14 FORK units do not enter `pipeline-cleared-queue.md`; they route to `pipeline-fork-queue.md` with the §4A materializability resolution as the systemic record. The 19 CLEARED units flow to the cleared queue (subject to the §4A *verbatim* audit's separate disposition — a unit CLEARED on materializability may still be FORK on verbatim; U-OD-11/12/32 are examples, CLEARED here, conformed at v2.5 there). The 1 CONFORM unit (U-OD-34) clears automatically once the single OD-plan materializability revision-pass conforms its cross-axis edge count.

**Cross-reference to the §4A verbatim audit.** A unit's final pipeline status is the *intersection* of this audit and `verbatim_audit_od_plan.md`. Units FORK in *either* audit do not clear. Notably U-OD-09 is FORK in both (verbatim FF-1 + materializability M-1); U-OD-30 is FORK in both. The two revision-passes (verbatim conformance — landed as v2.5; materializability — recommended here) should be sequenced or merged by the operator; the v2.5 pass already conformed the verbatim cluster, so the materializability pass is the outstanding one.

---

*Phase-7 pre-implementation review, review-ahead pipeline pass Q3 (re-launch) — plan-wide systemic materializability audit of the OD-axis plan (all 34 units, v2.5 delta resolved through v2.4 → v2.1 bodies). Distinct axis from the §4A verbatim audit: undeclared-type / no-carrier / hidden-coupling / signature-vs-spec completeness. Read-only with respect to all `design-substrate/` artifacts, `CLAUDE.md` files, plans, specs, and source — no repository file modified (HARD WALL / X-AL-3). Findings classified, not absorbed. Authored 2026-05-15 per `harness-adversarial-reviewer` SKILL.md Phase-7 pre-implementation review mode; §4A appendix per `systems-architect` SKILL.md §4A tension-resolution mode.*
