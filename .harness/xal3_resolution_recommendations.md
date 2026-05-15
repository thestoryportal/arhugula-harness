# X-AL-3 Design-Extension Resolution Recommendations — Pipeline Pass T2

*Authored 2026-05-15 by the `systems-architect` role in Phase-7 architectural tension-resolution
mode (`systems-architect` SKILL.md §4A). This file is a **RECOMMENDATION**. It does not decide
and does not edit any canonical artifact. The operator ratifies. HARD WALL: the only file
written by this pass is this file.*

## Inputs reconciled

- `.harness/shared_type_carrier_map.md` — T1 carrier triage; its Disposition-4 X-AL-3 section is the worklist.
- `.harness/verbatim_audit_as_plan.md` — AS Pattern B undeclared-type cluster.
- `.harness/materializability_audit_{cp,od,is}_plan.md` — CP/OD/IS undeclared-type clusters.
- `design-substrate/` — `Spec_Control_Plane_v1_3.md` (+ `v1_2.md` for verbatim-preserved §5/§7/§10/§13/§16/§17/§18/§22), `Spec_Action_Surface_v1.md`, `Spec_Operational_Discipline_v1_3.md`, `Spec_Information_Substrate_v1.md`, `ADR-D4/D5`, `Cross_Axis_Composition_Document_v2_1.md`.

## Authority chain (CLAUDE.md §1.3)

ADR (F1–F5 + D1–D6) → ADD v1.3 → PRD v1.1 → per-axis spec v1.x → per-axis plan v2.x + CXA v2.1.
Earlier is canonical for later.

## Verdict vocabulary

- **FACTOR-OUT** — the type's *semantics* (the concept) ARE committed by an existing spec/ADR;
  it simply lacked a declaration site. Re-route to T1 carrier-map disposition 1 (`harness-core`)
  or 2 (per-axis-owned). **No design-substrate revision needed.** The plan's field set is a
  faithful operationalization of spec prose; the `implementation-planner` revision pass declares
  the carrier.
- **GENUINE EXTENSION** — no spec/ADR commits the type or its semantics. Declaring it is a real
  H_T design extension (X-AL-3 / I-2). Needs a named design-substrate revision before the plan
  pass proceeds.
- Decision status: **decided** (authority-chain-determinate) / **proposing** (recommendation,
  operator confirms; two readings spelled out where present) / **open** (needs operator input
  even to classify).

## Discriminator applied

The discriminator is **does any spec/ADR commit the CONCEPT** — *not* whether the field set is
enumerated. Specs routinely commit a concept in prose and defer the record shape to
implementation discretion (every audited spec has a "Deferred to implementation discretion"
clause). A type whose concept the spec names, but whose field set the spec leaves to the plan,
is a FACTOR-OUT, not an extension. A GENUINE EXTENSION is one where the spec/ADR is silent on
the *concept entirely*.

---

## Resolution table — every X-AL-3 candidate in the T1 worklist

| Type | Class-1 halt? | Verdict | Factor-out carrier | Extension target + change shape | Authority-chain rationale | Status |
|---|---|---|---|---|---|---|
| **`WorkflowEvent`** | **YES** | FACTOR-OUT | `harness-core` (U-CORE-01) — workflow-lifecycle event type | — | CP spec §5.1 (C-CP-05, v1.2-verbatim) commits the **8-class lifecycle event taxonomy** (`workflow-start`/`step-boundary`/`fallback-trigger`/`retry-attempt`/`breaker-trip`/`lease-acquired`/`lease-released`/`resumption`); §5.2 commits the per-class minimum attribute set = the event payload shape. The concept is spec-committed. IS U-IS-14 `on_workflow_event` consumes it by *importing from `harness-core`* — not a cross-axis edge — so the CXA §2.4 "IS = 0 outbound" invariant holds intact. No CXA/ADD revision. | decided |
| **`WorkflowClass` / `WorkloadClass` @ IS** | **YES** | FACTOR-OUT | `harness-core` — **existing** U-CP-00 `WorkloadClass` carrier (spelling unified per T1) | — | CP spec §5.2 commits `workflow.class ∈ Persona §3.1 four-class set`; C-CP-07 §7.3 is the routing enum. Already a `harness-core` resident (U-CP-00). IS U-IS-02/05/12 consume via `harness-core` import, not an outbound edge. Invariant holds. | decided |
| **`DeploymentSurface` @ IS** | **YES** | FACTOR-OUT | `harness-core` (U-CORE-01) — cross-cutting enum | — | CP §7 commits "engine class committed per deployment surface"; AS spec §9.1 / U-AS-04 declares the 3-value enum; OD U-OD-01 declares it independently. Cross-cutting → `harness-core` per CLAUDE.md §3.3. IS U-IS-02/05 consume via `harness-core` import. Invariant holds. | decided |
| **`AuditLedgerEntry` @ CP** | **YES** | FACTOR-OUT | CP-owned (disposition 2) — carrier at/near U-CP-14 (or a CP foundational unit) | — | **CP spec §16.2 (C-CP-16, v1.2-verbatim) commits the per-response audit-ledger entry shape DIRECTLY** — `(action_id, gate_level, response, [hash fields], timestamp, prior_event_hash)` — and §20 (C-CP-20) commits the per-persona-tier audit-ledger cryptographic shape. CP's `AuditLedgerEntry` is **CP-spec-owned**, composing against IS-exported `StateLedgerEntry` shape + C-IS-06 hash-chain discipline via the *existing* CP→IS edges. It is NOT OD's audit-ledger schema; CP→OD stays foreclosed (CXA matrix CP→OD = 0 unchanged). No CXA revision. Confirms IS-audit Q4: `AuditPayload`/`AuditLedger` are OD-local — a parallel family, not the same type. | decided |
| `ToolMetadata` | no | FACTOR-OUT | AS-owned — carrier in U-AS-06 (or AS foundational unit) | — | AS spec §2.2 (C-AS-02) commits `sandbox_tier(tool, call_site_context)` — the `tool` argument's metadata is the contract input; §3 commits tool-contract authoring with `minimum_tier`. Concept committed; field set is implementation-discretion (§2 deferral clause). | proposing |
| `TaintState` | no | FACTOR-OUT | AS-owned — carrier with `CallSiteContext` at U-AS-08 | — | AS spec §2.2 commits `blast_radius_floor(call_site_context.taint_state)` and §2 "Deferred to implementation discretion" names "taint-state propagation mechanism" — the `taint_state` concept is spec-named. FACTOR-OUT, field set deferred to plan. | proposing |
| `MCPServer` | no | FACTOR-OUT | AS-owned — carrier with `CallSiteContext` at U-AS-08; consumed at U-AS-14 | — | AS spec §2.2 commits `mcp_server_trust_tier_floor(call_site_context.mcp_server)`; §10 (C-AS-10) commits the MCP transport / trust-level surface. Concept committed. | proposing |
| `WorkloadManifestOverrides` | no | FACTOR-OUT | AS-owned — carrier in U-AS-30 | — | AS spec §13.6 steps 6–7 commit "Operator selects extended-thinking effort per cell" + "binds Batch API cells"; the "Workload-binding-time" surface commits "Workload manifest declares per-workload sandbox-tier overrides … provider-instance preferences". The override concept IS committed. | proposing |
| `RawContractInput` | no | FACTOR-OUT | AS-owned — carrier in U-AS-07 | — | AS spec §3 commits `validate_tool_contract_at_registration` semantics — the registration-input concept is the §3 contract subject. Plan-internal carrier. | proposing |
| `ModelBinding` | no | FACTOR-OUT | CP-owned — U-CP-00b (CP foundational shared-types) | — | ADR-F1 v1.2 multi-LLM abstraction + CP §13.4 (C-CP-13) "Per-sub-agent-role × model-binding contract" commit per-role model binding. Concept committed. | proposing |
| `TraceContext` | no | FACTOR-OUT | CP-owned — U-CP-00b; or `harness-core` if OTel-aligned | — | OTel W3C Trace Context is a `Target_Stack_Commitment` substrate (OTel libraries adopted); CP §8 references `original_trace_id`/`original_span_id`. Concept committed by the OTel adoption + CP spec. | proposing |
| `ProviderAgnosticPayload` | no | FACTOR-OUT | CP-owned — U-CP-00b | — | ADR-F1 v1.2 capability-aware provider abstraction commits a provider-agnostic request/response surface; CP §1/§2 (C-CP-01/02) provider-abstraction contracts commit the concept. | proposing |
| `ProposedAction` | no | FACTOR-OUT | CP-owned — carrier in HITL unit (U-CP-16/17 family) | — | CP §16 (four-response palette: `approve`/`edit`/`reject` of a *proposed action*) + §17 three-placement HITL primitive commit the proposed-action concept at every HITL gate. ADR-D5 §1.1. | proposing |
| `MaterialDiff` | no | FACTOR-OUT | CP-owned — carrier in U-CP-22 (context-revalidation unit) | — | CP §22 (C-CP-22) commits "material-diff detection contract" explicitly + §22.2 the material-vs-immaterial table. ADR-D5 §1.11. Concept directly named in spec. | decided |
| `ParentRelation` | no | FACTOR-OUT | CP-owned — carrier in U-CP-10 (topology unit) | — | CP §10 (C-CP-10) six-pattern topology commits `decentralized-handoff` / `hierarchical-delegation` parent-ownership semantics; ADR-D4 v1.1 commits "HandoffContext + brief object structure" + sub-agent privilege-inheritance parent contract. Parent-relation concept committed. | proposing |
| `HandoffContext`-family (incl. CP audit usage) | no | FACTOR-OUT | CP-owned — U-CP-30 family | — | ADR-D4 v1.1 (CP spec §D4 row, line 140) commits "HandoffContext + brief object structure" by name; CP §13.4 "Deferred to implementation discretion: Specific HandoffContext serialization format". Concept committed; shape deferred. | decided |
| `VerifierResult` | no | FACTOR-OUT | CP-owned — carrier in U-CP-41 (or verifier unit) | — | CP §18.3/§18.4 commit the `two-agent-observer` verifier meta-class: "verifier agreement and disagreement both surface as inputs to the operator response palette"; §18 audit-composition row. The verifier-output concept is spec-committed. | proposing |
| `OverlayResolution` | no | FACTOR-OUT | CP-owned — carrier in U-CP-41 | — | CP §18.3 commits the `both-by-tier` per-tool overlay + §11.2 per-engine-class implementation-mechanism overlay; persona-tier-binding overlay resolution is spec territory. Concept committed. | proposing |
| `WebhookConfig` | no | FACTOR-OUT | CP-owned — carrier in U-CP-52 | — | CP §18 commits webhook callback / "webhook ingress for durable-async cells"; §18.4 "Deferred to implementation discretion: Specific webhook ingress library binding". The webhook-delivery concept IS committed. | proposing |
| `WebhookPayload` | no | FACTOR-OUT | CP-owned — carrier in U-CP-52 | — | CP §18 (C-CP-18) "webhook idempotency-keyed signal delivery … `(approval_id, idempotency_key)` checked against the ledger" commits the webhook-payload concept. | proposing |
| `HITLInvocation` | no | FACTOR-OUT | CP-owned — carrier in U-CP-17 (HITL primitive unit) | — | CP §17 (C-CP-17) "Three-placement HITL topology primitive + interface signature" commits the HITL-invocation record; §16.4 `hitl.invocation.responded` event. Concept committed. | proposing |
| `LeadAgentPlan` | no | FACTOR-OUT | CP-owned — carrier in U-CP-33 | — | ADR-D4 v1.1 commits "concurrent-prompt-cache warm-up protocol" + multi-agent topology (lead-agent role); CP §13.3 lead-agent binding. The lead-agent-plan concept is multi-agent-topology territory. | proposing |
| `FailedAttempt` / `Alternative` / `RetryHistory` | no | FACTOR-OUT | CP-owned — carrier in U-CP-30 (handoff unit) | — | CP §3.5 (C-CP-03) commits the `retry.*` namespace + retry-attempt taxonomy; §13.4 "Deferred to implementation discretion: Specific `RetryHistory` cardinality cap at HandoffContext payload boundary" — `RetryHistory` is *named in the spec*. `FailedAttempt`/`Alternative` are its constituents. Concept committed. | decided |
| `CurrentState` | no | FACTOR-OUT | CP-owned — carrier in U-CP-30/22 (= the spec `StateSummary`) | — | CP §13.4 (C-CP-13) commits `StateSummary` ("F2 state-ledger entries relevant") by name; §22 context revalidation composes against `handoff_context.state_summary`. The CP audit's `CurrentState` is the spec-committed `StateSummary` concept under a plan spelling. Spelling unification recommended. | proposing |
| `RetryPolicy` | no | FACTOR-OUT | CP-owned — carrier in U-CP-04 (routing-manifest unit) | — | CP §3 (C-CP-03) chain-advancement contracts + §3.5 `retry.*` namespace + C9 full-jitter backoff commit retry-policy semantics. Hand-rolled retry per CLAUDE.md §3.2 — the policy record is a faithful factor-out of §3.5. | proposing |
| `SpanRef` / `ChildSpanRef` | no | FACTOR-OUT | OD-owned — type-alias at U-OD-04 (OTel base-layer anchor) | — | OD spec C-OD-09 + ADR-F5 (observability substrate) + ADR-D6 (12-namespace OTel schema) commit the OTel span substrate. `SpanRef`/`ChildSpanRef` are harness aliases for the OTel-SDK span handle — OTel libraries are a `Target_Stack_Commitment` adoption (cf. AS-audit Findings-rejected #4 `SpanId` exclusion). Reading (a) of OD-audit §4A.4. | proposing |
| `SpanAttributes` | no | FACTOR-OUT | OD-owned — type-alias at U-OD-04 | — | Same basis: the OTel attribute bag is OTel-SDK substrate; ADR-D6 12-namespace schema commits the attribute model. Harness alias at the OD OTel anchor. | proposing |
| `EventEmission` | no | FACTOR-OUT | OD-owned — carrier at U-OD-04/09 | — | OD spec emission contracts (C-OD-09 breaker-event emission, C-OD-25 drift-event emission) + ADR-D6 commit the event-emission concept. `EventEmission` is the harness emission return-record — a faithful factor-out of the OD emission contracts. | proposing |

---

## Summary

### Counts

- **X-AL-3 candidates resolved:** 27 distinct types (the T1 worklist's ~24 plus the
  `WorkflowClass`/`WorkloadClass` spelling-pair and the `SpanRef`/`ChildSpanRef` family counted
  per-type).
- **FACTOR-OUT: 27 of 27 (100%).** Every X-AL-3 candidate's *concept* is committed by an
  existing spec or ADR. The cluster is a **carrier-map gap, not a design-extension cluster** —
  the plans consumed types at signature positions that the specs commit in prose but never gave
  a declaration site. The T1 Disposition-4 "BLOCK until back-flow" framing over-escalated:
  re-route every candidate to disposition 1 (`harness-core`) or 2 (per-axis-owned).
- **GENUINE EXTENSION: 0.**
- **Open (needs operator input to classify): 0.** All classifications resolved against the
  authority chain. 6 rows are *decided* (spec names the concept verbatim:
  `WorkflowEvent`/`WorkflowClass`/`DeploymentSurface`/`AuditLedgerEntry`/`MaterialDiff`/`HandoffContext`/`RetryHistory`-via-`FailedAttempt`-cluster);
  the remaining 21 are *proposing* — authority-chain-supported, operator confirms the carrier
  placement, none requires a design-substrate revision.

### The 2 Class-1 halts — both dissolve into FACTOR-OUTs

1. **`WorkflowEvent` + IS-consumed `WorkflowClass`/`DeploymentSurface`** — RESOLVED, no halt.
   CP spec §5.1 commits the 8-class lifecycle event taxonomy (`WorkflowEvent`); §5.2 commits
   `workflow.class`; CP §7 + AS §9.1 + OD §1 commit `DeploymentSurface`. All three are
   spec-committed concepts → `harness-core` residents (`WorkflowClass` already there via
   U-CP-00; `WorkflowEvent` + `DeploymentSurface` join via U-CORE-01). IS consumes them by
   **importing `harness-core`**, which is shared substrate — *not* a cross-axis `Depends on`
   edge. The CXA §2.4 "IS = 0 outbound edges" invariant is **not violated**. No CXA revision,
   no ADD revision, no IS-spec back-flow. The halt was a false alarm rooted in mistaking a
   `harness-core` import for an outbound edge.

2. **`AuditLedgerEntry` in CP** — RESOLVED, no halt, no CP→OD seam.
   CP spec §16.2 (C-CP-16) commits the per-response audit-ledger entry shape **directly inside
   the CP spec**; §20 (C-CP-20) commits the per-persona-tier audit-ledger cryptographic shape.
   CP's `AuditLedgerEntry` is **CP-spec-owned** (disposition 2, CP carrier near U-CP-14),
   composing against the IS-exported `StateLedgerEntry` shape + C-IS-06 hash-chain discipline
   via the *already-declared* CP→IS edges. It is **not** OD's audit-ledger schema — so no
   CP→OD edge is needed and the CXA matrix CP→OD = 0 stays intact. This confirms the IS-audit
   Q4 finding: OD's `AuditPayload`/`AuditLedger` (OD-local, ADR-D5 audit-ledger) and CP's
   `AuditLedgerEntry` (CP-spec-owned, C-CP-16/20) are **parallel sibling families** — each axis
   declares its own audit-entry type against the shared IS `StateLedgerEntry` export. No CXA
   matrix revision.

### Consolidated design-substrate-revision list (grouped by target artifact)

**NONE.** No design-substrate artifact requires revision to resolve the X-AL-3 cluster. Every
candidate is a faithful factor-out of existing spec/ADR content. The design-phase work scope
the operator faces for this cluster is **zero** — `spec-writer` is not engaged, no `Spec_*`
section, ADR, CXA edge set, or ADD section needs amendment for any of the 27 types.

This is the headline for the operator: **T1's Disposition-4 over-counted.** The ~24 "BLOCKING —
back-flow" candidates are all carrier-placement work, identical in kind to the non-X-AL-3
disposition-1/2 rows of the T1 carrier map. They re-route directly into the existing per-axis
`implementation-planner` revision passes:

| Re-routed to | Types | Carrier |
|---|---|---|
| `harness-core` (disposition 1, U-CORE-01) | `WorkflowEvent`, `DeploymentSurface` (+ `WorkflowClass` already at U-CP-00) | U-CORE-01 / U-CP-00 |
| AS-owned (disposition 2) | `ToolMetadata`, `TaintState`, `MCPServer`, `WorkloadManifestOverrides`, `RawContractInput` | in-place AS carriers (U-AS-06/07/08/30) |
| CP-owned (disposition 2) | `ModelBinding`, `TraceContext`, `ProviderAgnosticPayload`, `ProposedAction`, `MaterialDiff`, `ParentRelation`, `HandoffContext`-family, `VerifierResult`, `OverlayResolution`, `WebhookConfig`, `WebhookPayload`, `HITLInvocation`, `LeadAgentPlan`, `FailedAttempt`/`Alternative`/`RetryHistory`, `CurrentState`(=`StateSummary`), `RetryPolicy` | U-CP-00b + in-place CP carriers (U-CP-10/16/17/22/30/33/41/52) |
| OD-owned (disposition 2) | `SpanRef`, `ChildSpanRef`, `SpanAttributes`, `EventEmission` | type-aliases / carriers at U-OD-04 |

### Caveats the operator should weigh

- The 21 *proposing* rows are authority-chain-supported but invite a confirmation that the
  plan's field set is a *faithful* operationalization of the spec prose (not a quiet over-reach).
  That faithfulness check is the `implementation-planner` revision-pass's job, per type, when it
  declares the carrier — it is not a design-substrate question.
- One spelling-unification item surfaces: the CP audit's `CurrentState` is the CP-spec
  `StateSummary`; recommend the CP plan revision unify the spelling (a verbatim-pass item, not
  an X-AL-3 item).
- The OTel-alias reading for `SpanRef`/`SpanAttributes`/`EventEmission` (OD-audit §4A.4 reading
  (a)) is the recommended one and is consistent with the AS-audit's `SpanId` stack-primitive
  exclusion. If the operator instead rules them harness abstractions *distinct from* the OTel
  SDK types, they remain FACTOR-OUTs (OD spec C-OD-09 + ADR-D6 commit the emission concept
  either way) — only the carrier site shifts. No reading makes them a genuine extension.

---

*End of recommendation. The operator decides. The X-AL-3 cluster requires zero design-substrate
revision; all 27 candidates re-route into the four per-axis `implementation-planner` revision
passes already scoped by the T1 carrier map. The two Class-1 halts are lifted.*
