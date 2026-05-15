# ADR-D6: Observability backend — per-deployment-surface × per-persona-tier observability commitment with unified span schema ingestion contract assembly across F3 capability-floor (iv) + D2 + D3 + D4 + D5 + OTel GenAI semconv 1.41.0 substrate and operator-burden eval primitive dashboard binding

## Status

Proposed
Date: 2026-05-10
Phase: 3b Stage 1 (per `Project_Workflow_v1_1.md` §2.3.3) — Phase 3 closed; in F2-12 cascade revision per `Project_Workflow_v1_7.md` §4.1.2
Promotion path: Accepted at ADD v1.3 absorption per Workflow v1.7 §3.1
Phase 3b Stage 1 status on filing: **CLOSE** — all six D-ADRs filed (D1, D2, D3, D4, D5, D6) per Workflow v1.1 §2.3.3 exit criteria
Revision: v1 → v1.1 (P3c-CK iter-2 close revision per `Project_Workflow_v1_2.md` §4.1.2 path — F2-iter2-01 D6 v1.1 cross-D-ADR namespace absorption applying ten iter-1 partial-resolved findings + four iter-1 not-resolved findings; new §1.2.1 sub-section + new `harness.breaker.*` row per F2-16; §1.3 `mcp.tool.call` always-sampled carve-out per F2-09; §1.2 `provider_discriminator` Source column citation refinement per F2-10; §1.2 `hitl.*` row aligned to D5 v1.2 four-distinct-events shape per F2-05 hitl.* sub-finding closure; References Shape 4 updated to v1.1+ source D-ADR references)
Revision date: 2026-05-11
Promotion: P3c-CK final clearance — 2026-05-11
**Revision: v1.1 → v1.2 (F2-12 cascade Step 2b per `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 + `F2-12_Council_Deliberation_Output.md` §8.2; sub-scopes (ii) `retry.attempt` sibling-span discipline + (iii) trace-ingestion dedup composition with F2 `idempotency_key`: §1.2 engine.* row updated to 4-attribute schema citing D1 v1.2 §1.1.1; §1.2 lifecycle event set retry.attempt entry corrected to child-per-attempt terminology; new §1.2.2 retry.* namespace declaration with 6-attribute retry-attempt span schema + 3-field parent event schema; new §1.2.3 sub-agent boundary under retry composition; §1.5 cost-attribution-per-span amended with dedup algorithm specification + new §1.5.1 replay-aware dedup with retry orthogonality + new §1.5.2 cause_attribution invariance check + new §1.5.3 per-attempt cost-attribution discipline)**
**Revision date: 2026-05-14**

## Change-note (v1.1 → v1.2)

**Scope of revision.** F2-12 cascade Step 2b two-sub-scope (ii) + (iii) closure pass per `F2-12_Closure_Path_Execution_Kickoff.md` §3.1 + `F2-12_Council_Deliberation_Output.md` §5 + §6 resolutions. The revision pass formalizes:

| Sub-scope | Resolution source | D6 v1.2 amendment site |
|---|---|---|
| (ii) `retry.attempt` sibling-span discipline | Council §6.2 (C9 primary) + §6.3 (C1 co-primary; T-perm-3 engaged) + §6.8 resolution | §1.2 lifecycle event set retry.attempt entry; new §1.2.2 retry.* namespace; new §1.2.3 sub-agent boundary |
| (iii) trace-ingestion dedup composition with F2 idempotency_key | Council §5.2 (C7 primary algorithm) + §5.3 (C3 co-primary; T-perm-2 engaged) + §5.4 (C9 orthogonality) + §5.5 (C5 invariance) + §5.8 resolution | §1.5 dedup algorithm; new §1.5.1 / §1.5.2 / §1.5.3 sub-sections |

Sub-scope (i) span re-emission semantics is closed at ADR-D1 v1.2 §1.1.1 + §1.1.2 per cascade Step 2a; D6 v1.2 §1.2 engine.* row updates from 3-attribute to 4-attribute citing D1 v1.2 §1.1.1 as canonical source (Pattern P1 cross-artifact name drift prevention discipline).

Workflow v1.7 §7 fidelity-grammar discipline applied across all amendment sites: no Pattern P1 cross-artifact name drift (all attribute names canonical to declaration source); no Pattern P2 verbatim-claim-contradicted (all "per §X verbatim" claims verify against source); citation anchors substrate-verified per Workflow v1.7 §2.3.3.1 clause (iii).

**Status posture.** `Status: Proposed` preserved per `Project_Workflow_v1_7.md` §3.1 — promotion to `Accepted` blocked until ADD v1.3 absorption (F2-12 cascade Step 3). D6 v1.2 enters cascade Step 3 as substrate input for `Architectural_Design_Document_v1_3.md` authoring alongside D1 v1.2.

**Sections preserved verbatim from v1.1.** §1.1 deployment-surface × persona-tier matrix (nine-cell with cells/exclusions/witnesses); §1.2 base-layer OTel GenAI semconv 1.41.0 block (preserved as cross-vendor floor); §1.2 namespace map rows for anthropic.* / mcp.* / skill.* / managed_agents.* / sandbox.* / hitl.* / topology.fanout.* / subagent.* / audit.* / validator.fail.* / files.* / memory.* / harness.breaker.* / provider_discriminator (only engine.* row amended); §1.2 namespace collision discipline paragraph; §1.2.1 harness.breaker.* span attribute names declared sub-section; §1.3 cardinality budget per cell + cardinality-safe attributes + always-sampled list + base-rate-sampled list + tail-keep-on-classification list paragraphs; §1.4 default-on structure attribute list + default-off content attribute list + per-persona-tier override gradient + pre-collector redaction paragraphs; §1.5 cost-attribution-per-span dashboarding contract block (only §1.5 dedup-algorithm + new §1.5.1/§1.5.2/§1.5.3 sub-sections amended; cross-family pricing differential + tokenization-version anchor + per-cell cost-attribution dashboard binding sub-sections preserved verbatim); §1.6 operator-burden eval primitive dashboard binding block; §1.7 local-first OTLP collector commitment block; §1.8 multi-tenant tenant-isolation block; §1.9 cell-selection contract block; §Context; §Rationale (a)–(f); §Consequences (a)–(j); §Alternatives considered; §References Shapes 1–5 + Substrate research citations + Permanent tension ledger updates.

**Changes inline.** Status block (Revision: v1.1 → v1.2 + Revision date lines appended). This Change-note (v1.1 → v1.2) section. §1.2 engine.* namespace row updated from 3-attribute to 4-attribute citation; canonical source citation revised from D1 v1.1 §1.1.1 → D1 v1.2 §1.1.1. §1.2 lifecycle event set retry.attempt entry: "new sibling retry span" terminology corrected to "new child span per attempt" with forward-reference to §1.2.2 retry.* namespace declaration. New §1.2.2 sub-section inserted between §1.2.1 and §1.3 declaring the 6-attribute retry-attempt span schema + 3-field parent-span retry.attempt event schema. New §1.2.3 sub-section declaring sub-agent boundary composition under retry. §1.5 cost-attribution-per-span preamble amended with dedup-algorithm specification. New §1.5.1 sub-section declaring replay-aware dedup with retry orthogonality. New §1.5.2 sub-section declaring cause_attribution invariance check at `deterministic_replay`. New §1.5.3 sub-section declaring per-attempt cost-attribution discipline. References "Workflow and skill discipline references" extended with v1.2 entries (Workflow v1.7 §3.1, §4.1.2, §7; F2-12 cascade kickoff; F2-12 council deliberation output; ADR-D1 v1.2 substrate inheritance). Convening artifact citations extended with F2-12 cascade Step 1 council deliberation reference. Closing footer revised to note v1.2 filing.

**Cross-cascade-step coordination.** ADR-D1 v1.2 (cascade Step 2a) is filed; D6 v1.2 inherits D1 v1.2 §1.1.1 (4-attribute engine.* namespace) + §1.1.2 (per-engine-class replay-emission discipline) + §1.1.2.2 (F2 state-ledger entry shape extension with `original_trace_id` + `original_span_id`) as substrate inputs without re-declaration. Substrate flow: D1 v1.2 declares attribute names + replay-emission semantics + ledger shape; D6 v1.2 declares ingestion contract + dedup algorithm + per-attempt cost-attribution. Pattern P1 prevention discipline enforced at §1.2 engine.* row Source column citation.

## Context

[Preserved verbatim from v1.1; not reproduced here for length. v1.1 §Context begins "This ADR closes the **deployment-surface-AND-persona-dependent** observability-backend deferral declared at `Pattern Reference Catalog v1.0 §11.3.2 D6`..." and runs through "...D6 commits per-span trace-correlation join via `idempotency_key` to F2 state-ledger entries." See `ADR-D6.md` v1.1 lines 45–57.]

## Decision

[Preserved verbatim from v1.1; not reproduced here for length. The nine-component observability backend specification at §Decision lines 59–73 of v1.1 stands. At v1.2, the unified span schema ingestion contract (component 2) is materially extended with F2-12 sub-scope (ii) + (iii) amendments at §1.2 and §1.5; the other eight components are preserved verbatim.]

### 1.1 Deployment-surface × persona-tier matrix

[Preserved verbatim from v1.1; not reproduced here for length. The nine-cell matrix at v1.1 lines 75–87 stands.]

### 1.2 Unified span schema ingestion contract

The unified ingestion contract assembles cleanly across the five upstream span-schema commitments via additive namespace separation, with OTel GenAI semantic conventions 1.41.0 [HIGH] as the cross-vendor floor.

**Base layer — OTel GenAI semconv 1.41.0 [HIGH].** [Preserved verbatim from v1.1 §1.2 base-layer block.]

**Specialization layers (additive, namespace-separated).** The v1.2 amendment updates one existing row (engine.*) and adds no new rows at §1.2 itself; new namespaces are declared at new sub-section §1.2.2 (retry.*). All other rows preserved verbatim from v1.1.

| Namespace | Source | Coverage |
|---|---|---|
| `anthropic.*` | ADR-D3 v1.1 §1.8.1 | [Preserved verbatim from v1.1 §1.2.] |
| `mcp.*` | ADR-D3 v1.1 §1.8.1 | [Preserved verbatim from v1.1 §1.2.] |
| `skill.*` | ADR-D3 v1.1 §1.8.1 | [Preserved verbatim from v1.1 §1.2.] |
| `managed_agents.*` | ADR-D3 v1.1 §1.8.1 | [Preserved verbatim from v1.1 §1.2.] |
| `sandbox.*` | ADR-D2 v1.1 §1.7.1 + ADR-F4 v1.1 §Consequences (a) | [Preserved verbatim from v1.1 §1.2.] |
| `hitl.*` | ADR-D5 v1.2 §1.8 + ADR-D5 v1.3 §1.8 amendment | [Preserved verbatim from v1.1 §1.2.] |
| `topology.fanout.*` | ADR-D4 v1.1 §1.9 | [Preserved verbatim from v1.1 §1.2.] |
| `subagent.*` | ADR-D4 v1.1 §1.9 | [Preserved verbatim from v1.1 §1.2.] |
| **`engine.*` (v1.2 amendment)** | **ADR-D1 v1.2 §1.1.1** | **Four attributes per F2-12 sub-scope (i) closure (was three at v1.1): `engine.class` ∈ `{event-sourced-replay, save-point-checkpoint, pure-pattern-no-engine, reconciler-loop, WAL-segment}`; `engine.event_history.tier` ∈ `{Tier-3, Tier-5}` per F2 state-ledger join via `idempotency_key`; `engine.event.id` joining to F2 state-ledger entry; `engine.replay_disposition` ∈ `{deterministic_replay, checkpoint_resume, no_replay, reconciler_iteration, wal_consume}` closed-mapped to `engine.class` per D1 v1.2 §1.1.1. Per-engine-class replay-emission discipline declared at D1 v1.2 §1.1.2; D6 inherits as ingestion contract without re-declaration. F2 state-ledger entry shape extension at D1 v1.2 §1.1.2.2 (`original_trace_id` + `original_span_id` fields) is the trace-context durability source for `deterministic_replay` dedup at §1.5.** |
| `audit.*` | ADR-D5 v1.2 §1.4.1 | [Preserved verbatim from v1.1 §1.2.] |
| `validator.fail.*` | ADR-D5 v1.2 §1.10.1 + `c5-validation-contract` SKILL.md s14 §7.5(d) | [Preserved verbatim from v1.1 §1.2.] |
| `files.*` | ADR-D3 v1.1 §1.8.1 | [Preserved verbatim from v1.1 §1.2.] |
| `memory.*` | ADR-D3 v1.1 §1.8.1 | [Preserved verbatim from v1.1 §1.2.] |
| `harness.breaker.*` | `c9-reliability-recovery` SKILL.md (per F2-16 closure) | [Preserved verbatim from v1.1 §1.2; schema enumerated at §1.2.1.] |
| **`retry.*` (v1.2 new namespace)** | **`c9-reliability-recovery` SKILL.md (council Primary at sub-scope (ii)); ADR-D1 v1.2 §1.1.2 composition** | **Six attributes on retry-attempt child span (was 0 at v1.1; retry.attempt was lifecycle event only, no span-schema declaration) per F2-12 sub-scope (ii) closure. Schema enumerated at §1.2.2 below. Parent-span retry.attempt event schema (3 event fields) also at §1.2.2.** |
| `provider_discriminator` | `c7-observability` SKILL.md (primary anchor per F2-10 resolution); ADR-F1 §Decision (composition context) | [Preserved verbatim from v1.1 §1.2.] |

**F3 capability-floor (iv) lifecycle event set.** The base ingestion contract committed at F3 v1.1 maps to span-event names within the parent span. The v1.2 amendment corrects the retry.attempt entry terminology and adds the engine.replay_disposition cross-reference:

```
workflow.start                  span attribute on root span
step.boundary                   span event on parent
fallback.triggered              span event on parent + new sibling fallback span
retry.attempt                   span event on parent (3-field event schema per §1.2.2)
                                + new CHILD span per attempt (v1.2 terminology correction;
                                  was "new sibling retry span" at v1.1; corrected per F2-12
                                  sub-scope (ii) closure — retry attempts are children of parent
                                  operation; attempts are siblings to each other under same
                                  parent; 6-attribute span schema per §1.2.2)
breaker.tripped                 span event on parent (always-sampled per §1.3; seven-attribute
                                schema per §1.2.1)
lease.acquired                  span event on parent
lease.released                  span event on parent
workflow.resumed                span attribute on root span (post-resumption; carries
                                engine.replay_disposition per §1.2 engine.* row v1.2 amendment)
```

The lifecycle event set composes additively with the namespace-specialized events from D2/D3/D4/D5 — a single span may carry multiple event types from multiple namespaces (e.g., a `chat` operation span that issues a `tool.call` to an MCP primitive in a sandbox-tier-3 environment carries `gen_ai.*`, `mcp.*`, `sandbox.*`, and F3 lifecycle attributes simultaneously without namespace collision).

**Namespace collision discipline.** [Preserved verbatim from v1.1 §1.2.]

#### 1.2.1 Span attribute names declared for the breaker-trip event

[Preserved verbatim from v1.1 §1.2.1 — seven-attribute `harness.breaker.*` schema declared per `c9-reliability-recovery` SKILL.md substrate.]

#### 1.2.2 Span attribute names declared for the retry-attempt span and parent retry.attempt event (v1.2; new sub-section)

The F3 v1.1 capability-floor (iv) `retry.attempt` lifecycle event is materialized as a dual surface at v1.2: a **parent-span event** carrying retry-trigger semantics (parent-perspective) AND a **child span per attempt** representing the retry-attempt execution (operation-perspective). The dual-surface discipline closes F2-12 sub-scope (ii) per `F2-12_Council_Deliberation_Output.md` §6.2 + §6.8 resolution (C9 primary + C1 co-primary on T-perm-3).

**Terminology correction from v1.1.** The v1.1 §1.2 retry.attempt entry described the second surface as "new sibling retry span"; the v1.2 council resolution corrects this to "child span per attempt." The corrected topology: retry attempts are CHILDREN of the parent operation span; the attempts are SIBLINGS TO EACH OTHER under the same parent. Per `c1-orchestration-control` SKILL.md decision vocabulary at council §6.3, *"C1 selects child-per-attempt topology."*

##### 1.2.2.1 Retry-attempt child span — 6-attribute schema

The retry-attempt child span carries six attributes plus the OTel-standard `parent_span_id` link to the parent operation:

| Attribute | Type | Source | Definition |
|---|---|---|---|
| `retry.attempt_number` | integer (1-indexed) | `c9-reliability-recovery` SKILL.md (council §6.2) | Sequential attempt counter within the parent operation; attempt 1 is the first attempt, attempt N is the N-th retry |
| `retry.original_span_id` | string (16-hex; OTel W3C Trace Context format) | F2 state-ledger entry per attempt 1 | Link to the first attempt's span_id; recovered from F2 state-ledger entry filtered by `idempotency_key` |
| `retry.delay_ms` | integer | `c9-reliability-recovery` SKILL.md (council §6.2) | Jittered delay applied before this attempt (C9 full-jitter backoff computation per `c9-reliability-recovery` SKILL §4.1.1) |
| `retry.cause_attribution` | string (open-set enum) | `c5-validation-contract` SKILL.md s14 §7.5(a) cause_attribution catalog | Reason for retry; values from C5 cause_attribution catalog (`network_timeout`, `provider_outage`, `model_misfire`, `contract_violation`, `capability_shortfall`, etc.); medium cardinality bounded at ~15 values |
| `retry.fail_class` | enum: `{transient-retry, Reflexion-recoverable, HITL-recoverable, permanent-fail-exit, terminal-fail-exit}` | `c5-validation-contract` SKILL.md s14 §7.5(d) | C5 5-class fail-class taxonomy classification of the failure that triggered this retry; carries the validator-fail event's classification if validator-fail triggered the retry, or derives from cause_attribution mapping if mechanical failure triggered the retry |
| `engine.replay_disposition` | enum (5 values per ADR-D1 v1.2 §1.1.1) | ADR-D1 v1.2 §1.1.1 | Composition with sub-scope (i); discriminates orthogonally with `retry.attempt_number` at §1.5.1 dedup; the retry-attempt span inherits the parent operation's `engine.replay_disposition` value |

**Closed-mapping composition with parent.** The retry-attempt span's `parent_span_id` field (OTel-standard) links to the parent operation span. The `retry.original_span_id` is recovered from F2 state-ledger filtered by `idempotency_key`; on attempt 1, `retry.original_span_id == span_id` (self-reference); on attempts 2..N, `retry.original_span_id == attempt 1 span_id`.

##### 1.2.2.2 Parent-span retry.attempt event — 3-field event schema

The parent operation span carries a `retry.attempt` event at the retry-trigger point. The event schema:

| Event field | Type | Source | Definition |
|---|---|---|---|
| `parent.attempt_count` | integer | `c9-reliability-recovery` SKILL.md (council §6.2) | Total attempts so far for this operation (initial attempt + retries; reads from per-operation counter) |
| `parent.attempts_remaining` | integer | `c9-reliability-recovery` SKILL.md (council §6.2) | Remaining retry budget (`max_attempts - parent.attempt_count`); zero means budget exhausted |
| `parent.next_delay_ms` | integer (optional; omitted when `parent.attempts_remaining == 0`) | `c9-reliability-recovery` SKILL.md (council §6.2) | Delay (jittered, computed by C9 full-jitter backoff) before next attempt; omitted at retry-budget-exit boundary |

##### 1.2.2.3 Emission discipline

The retry-attempt mechanism MUST emit BOTH the parent-span event AND the new child span at each retry. Per `F2-12_Council_Deliberation_Output.md` §6.4 (C7 schema authority): emission discipline forbids collapsing to event-only or span-only.

| Collapse mode | Failure mode |
|---|---|
| Event-only (no child span) | Loses per-attempt operation-level instrumentation; cost-attribution at §1.5 cannot accrue per-attempt cost; per-attempt diagnostic spans are missing from the trace tree |
| Span-only (no parent event) | Loses parent-perspective retry-trigger marking; operator scanning the parent span's event timeline cannot see retry occurred at trigger time without traversing children |

##### 1.2.2.4 Sampling discipline

Both the parent retry.attempt event and the retry-attempt child span are subject to the §1.3 sampling discipline. The retry-attempt child span is base-rate-sampled at cell tunable; the parent retry.attempt event carries always-sampled discipline when `parent.attempts_remaining == 0` (retry-budget-exit boundary; tamper-evidence-relevant per `c7-observability` SKILL.md tamper-evidence discipline).

#### 1.2.3 Sub-agent boundary composition under retry (v1.2; new sub-section)

When a retry crosses a sub-agent boundary (the parent operation invokes a sub-agent via ADR-D4 v1.1 §1.9 multi-agent topology), the sub-agent's spans are children of the retry-attempt span, NOT of the original parent operation span. Per `c1-orchestration-control` SKILL.md decision vocabulary at `F2-12_Council_Deliberation_Output.md` §6.3, *"C1 specifies handoff contract: per-retry-attempt invocation carries full handoff payload; not collapsed across attempts."*

**Topology shape under retry-with-sub-agent.**

```
parent operation span
│
├── retry.attempt event (attempt_count=1, attempts_remaining=N-1, next_delay_ms=...)
│
├── retry-attempt child span (attempt_number=1)
│   │
│   └── sub-agent span tree (per ADR-D4 v1.1 §1.9)
│       ├── topology.fanout.opened event (if fan-out)
│       └── subagent.span tree
│
├── retry.attempt event (attempt_count=2, attempts_remaining=N-2, next_delay_ms=...)
│
└── retry-attempt child span (attempt_number=2)
    │
    └── sub-agent span tree (DISTINCT from attempt 1; full handoff payload re-invoked)
        ├── topology.fanout.opened event
        └── subagent.span tree
```

**Per-attempt isolation invariance.** Each retry attempt creates its own sub-agent span sub-tree rooted at the retry-attempt child span. Cross-attempt span linking is via `retry.original_span_id` reference, NOT via shared sub-agent span_ids. The per-attempt isolation invariance supports diagnostic legibility (operator can inspect each attempt's sub-agent execution independently) and per-attempt cost-attribution accuracy (cost rolls up per sub-tree under each retry-attempt child span).

**Handoff payload re-emission.** Per `c1-orchestration-control` SKILL.md `topology_fault_handling` Layer-3 tunable (default `pre-declared-with-allowlist` per council §6.3): the full handoff payload (ADR-D4 v1.1 §1.9 handoff contract) is re-emitted at each retry attempt's sub-agent invocation. Per-attempt handoff payload divergence is NOT permitted under the `pre-declared-with-allowlist` default; operator-set tunable values (`runtime-rewrite`) permit per-attempt handoff payload mutation under T-perm-3 escalation policy.

**T-perm-3 status.** T-perm-3 (C1 ↔ C9 — control-flow vs reliability) ENGAGED at sub-scope (ii) per `F2-12_Council_Deliberation_Output.md` §7.1; honored at default `pre-declared-with-allowlist`; ADR-D1 §1.3 D1-layer T-perm-3 resolution (`topology_fault_handling` parameter) preserved verbatim; ADR-D4 §1.5 D4-layer T-perm-3 resolution (`topology_fault_handling × workload_class × topology_pattern`) preserved verbatim; D6 v1.2 inherits both without revision.

### 1.3 Sampling discipline

[Preserved verbatim from v1.1 §1.3 — head-based-dev / tail-based-prod with always-sampled list + base-rate-sampled list + tail-keep-on-classification list.]

### 1.4 Redaction discipline

[Preserved verbatim from v1.1 §1.4 — default-off content attributes + default-on structure attributes + per-persona-tier override gradient + pre-collector redaction discipline.]

### 1.5 Cost-attribution-per-span dashboarding contract

[The cross-family pricing differential + tokenization-version anchor + per-cell cost-attribution dashboard binding sub-sections are preserved verbatim from v1.1 §1.5. The v1.2 amendment adds the trace-ingestion dedup-algorithm specification at the §1.5 preamble + three new sub-sections §1.5.1 / §1.5.2 / §1.5.3.]

**Trace-ingestion dedup algorithm (v1.2; new content at §1.5 preamble).** The cost-attribution-per-span contract requires per-span cost accrual to be replay-aware. Cost-per-span accrues exactly once per attempt for re-emitting `engine.replay_disposition` values and zero additional accrual for `deterministic_replay`. The dedup algorithm at trace-ingestion time enforces this invariant.

```
function ingest_span(span):
  # span carries: trace_id, span_id, idempotency_key (from F2 state-ledger join),
  #               engine.replay_disposition, optional retry.attempt_number,
  #               optional retry.cause_attribution

  key = span.idempotency_key  # per ADR-IS §10.2 canonical join key
  ledger_entry = F2_state_ledger.lookup_by_key(key)

  if ledger_entry exists:
    match span.engine.replay_disposition:
      case "deterministic_replay":
        # Idempotent replay; verify trace_id + span_id match ledger
        assert span.trace_id == ledger_entry.original_trace_id
        assert span.span_id == ledger_entry.original_span_id
        assert span.retry.cause_attribution == ledger_entry.cause_attribution  # §1.5.2
        DROP  # No new cost attribution; replay is invisible at D6

      case "checkpoint_resume" | "reconciler_iteration" | "wal_consume":
        # Re-emission expected; record as new attempt or new execution
        RECORD span as new ingestion
        mark span.is_replay_derived = true
        # Cost attribution counts ONCE per attempt; not aggregated across replays (§1.5.3)
        # Parent span_id from ledger_entry preserves topology link

      case "no_replay":
        ERROR  # Unexpected re-ingestion for non-replay engine class
        cause_attribution = "replay_semantic_divergence"

  else:
    RECORD span as new (first ingestion)
    F2_state_ledger.append(
      idempotency_key=key,
      original_trace_id=span.trace_id,
      original_span_id=span.span_id,
      engine_attrs={...},
      fail_class=span.retry.fail_class,
      cause_attribution=span.retry.cause_attribution,
      ts_iso8601=now()
    )
```

**Composition with F2 state-ledger.** The `idempotency_key` is the harness-canonical join key per ADR-IS §10.2; D6 ingestion-time lookup precedes the dedup decision. ADR-D1 v1.2 §1.1.2.2 declares the ledger entry shape extension with `original_trace_id` + `original_span_id` fields; D6 §1.5 dedup is the consumer of those fields.

**Hash-chain integrity composition.** The F2 state-ledger entry hash-chain construction (per `c10-action-safety` SKILL.md hash-chain integrity discipline + `c11-operator-local` SKILL.md §4.1.28 sqlite ledger_entries schema) extends to include `original_trace_id` + `original_span_id` fields:

```
ledger_entry_hash = SHA-256(
  prev_entry_hash ||
  idempotency_key ||
  original_trace_id ||
  original_span_id ||
  engine_attrs ||
  fail_class ||
  cause_attribution ||
  ts_iso8601
)
```

The three-way seam (C3 storage primitive / C10 hash-chain integrity discipline / C11 sqlite implementation) is preserved without Layer-3 promotion per `F2-12_Council_Deliberation_Output.md` §5.3.

[The cross-family pricing differential + tokenization-version anchor + per-cell cost-attribution dashboard binding sub-sections preserved verbatim from v1.1 §1.5 follow here.]

#### 1.5.1 Replay-aware dedup with retry orthogonality (v1.2; new sub-section)

Dedup at trace-ingestion does NOT collapse retry attempts. Each retry attempt is a DISTINCT cost-attribution unit; the dedup algorithm at §1.5 collapses only `deterministic_replay` re-reads of the SAME attempt, not different attempts of the same operation.

**Orthogonality discriminators.** Two discriminators compose orthogonally:

| Discriminator | Domain | Discriminates |
|---|---|---|
| `retry.attempt_number` | integer (1..N) | Attempts within a parent operation (attempt 1 vs attempt 2 vs ... vs attempt N) |
| `engine.replay_disposition` | enum (5 values per D1 v1.2 §1.1.1) | Replay-vs-fresh-execution within an attempt (deterministic_replay re-read vs checkpoint_resume re-emission vs ...) |

**Dedup outcome matrix.**

| `retry.attempt_number` | `engine.replay_disposition` | Dedup outcome |
|---|---|---|
| 1 | `deterministic_replay` | DROP if F2 ledger entry matches (idempotency_key + trace_id + span_id + cause_attribution); ERROR if mismatch (per §1.5.2) |
| 1 | `checkpoint_resume` | RECORD as new replay-derived span; cost accrues for attempt 1 |
| 2 | `deterministic_replay` | DROP if F2 ledger entry for attempt 2 matches; ERROR if mismatch |
| 2 | `checkpoint_resume` | RECORD as new retry attempt 2's replay-derived span; cost accrues for attempt 2 |
| 1 | `no_replay` | RECORD if first ingestion; ERROR if re-ingestion (unexpected for no_replay) |
| 2 | `no_replay` | RECORD as new attempt 2; cost accrues for attempt 2 |
| 1 | `reconciler_iteration` | RECORD with iteration_number discriminator from reconciler.iteration_number |
| 1 | `wal_consume` | RECORD with consumer_group discriminator from wal.consumer_group |

**Per-attempt F2 state-ledger entry shape.** Each retry attempt produces a distinct F2 state-ledger entry. The parent operation has ONE `idempotency_key`; each retry attempt joins via that key but is a DISTINCT entry with `retry.attempt_number` as discriminator within the key's join set (per `F2-12_Council_Deliberation_Output.md` §6.6 C3 contribution). The ledger filter at attempt N reads the join set ordered by `retry.attempt_number`; ledger entries are per-attempt, not per-operation.

#### 1.5.2 cause_attribution invariance check at deterministic_replay (v1.2; new sub-section)

Under `engine.replay_disposition=deterministic_replay`, the dedup algorithm at §1.5 includes a cause_attribution invariance check. If the replayed span carries a different `retry.cause_attribution` than the F2 state-ledger entry's stored cause_attribution, this signals replay-introduced semantic divergence — a violation of the deterministic-replay contract.

**Invariance check.**

```
if span.engine.replay_disposition == "deterministic_replay":
  assert span.retry.cause_attribution == ledger_entry.cause_attribution
```

**Escalation on mismatch.** Mismatch ESCALATES to ERROR class:

| Field | Value on mismatch |
|---|---|
| `validator.fail.class` | `terminal-fail-exit` (C5 5-class taxonomy) |
| `validator.fail.cause_attribution` | `replay_semantic_divergence` (new value added to C5 cause_attribution catalog at this revision) |
| `validator.fail.permanence` | `permanent` |
| Always-sampled per §1.3 | Yes (validator.fail.permanence=permanent always-sampled) |

The escalation signals an engine-replay-contract violation: the engine claims `deterministic_replay` disposition but the replay produced a different cause_attribution than the original execution. This is a substrate-level integrity violation requiring operator investigation (HITL escalation per `c11-operator-local` SKILL.md mandatory-HITL triggers + `c10-action-safety` SKILL.md eleven-trigger catalog).

**Cause_attribution catalog extension.** The C5 cause_attribution catalog (per `c5-validation-contract` SKILL.md reconciliation, ~15 values bounded) extends with one new value at v1.2: `replay_semantic_divergence`. Cross-ADR coordination: ADR-D5 v1.2 §1.10.1 `validator.fail.cause_attribution` open-set enum absorbs the new value at the next D5 revision (forward-flagged; not blocking this revision).

#### 1.5.3 Per-attempt cost-attribution discipline (v1.2; new sub-section)

Cost-attribution-per-span at §1.5 accrues per attempt for re-emitting `engine.replay_disposition` values; cost does NOT aggregate across attempts under any disposition.

**Per-attempt cost accrual.**

| Disposition | Cost accrual semantics |
|---|---|
| `deterministic_replay` | ZERO additional cost accrual at replay; cost was accrued at first execution; ledger entry preserves cost figure |
| `checkpoint_resume` | NEW cost accrual at resume; per-attempt cost is independent of pre-checkpoint accrual; resumed attempt's cost adds to the parent operation's total cost |
| `no_replay` | First execution cost only; re-ingestion is ERROR |
| `reconciler_iteration` | NEW cost accrual per iteration; each iteration is an independent operation cost-wise |
| `wal_consume` | NEW cost accrual per consumption; each consumer's processing is independent cost-wise |

**Parent operation total cost.** The parent operation's total cost is the SUM of per-attempt costs across all retry attempts (per `F2-12_Council_Deliberation_Output.md` §6.8 resolution point 6). The roll-up:

```
total_cost(parent_operation) =
  Σ cost(retry-attempt child span_i) for i in 1..N
```

`deterministic_replay` re-reads of any attempt contribute zero to the sum (cost was accrued at first execution; replay re-reads are idempotent at cost level).

**Cross-axis composition with §1.6 operator-burden eval primitive.** The per-attempt cost-attribution composes with §1.6 operator-burden eval primitive dashboard binding: expected-HITL-invocations-per-session × per-HITL-cost rolls up against per-attempt cost-attribution at the per-operation aggregation level. C8's eval primitives (per `c8-eval-engineer` SKILL.md) consume per-attempt cost as substrate without re-aggregation.

### 1.6 Operator-burden eval primitive dashboard binding

[Preserved verbatim from v1.1 §1.6.]

### 1.7 Local-first OTLP collector commitment

[Preserved verbatim from v1.1 §1.7.]

### 1.8 Multi-tenant tenant-isolation

[Preserved verbatim from v1.1 §1.8.]

### 1.9 Cell-selection contract

[Preserved verbatim from v1.1 §1.9.]

## Rationale

[Preserved verbatim from v1.1 §Rationale (a)–(f).]

**v1.2 rationale delta.** F2-12 sub-scopes (ii) + (iii) closure rationale:

- **(g) F2-12 sub-scope (ii) `retry.attempt` sibling-span discipline resolution.** Council §6.2 (C9 primary) + §6.3 (C1 co-primary; T-perm-3 engaged) committed BOTH event AND child span discipline because each surface carries distinct semantic value: the parent-span event marks the retry trigger at the parent-operation timeline (operator can scan event timeline to see retry occurred); the child span represents the retry-attempt execution as a first-class operation (cost-attribution accrues per attempt; per-attempt sub-agent topology preserves diagnostic legibility). Collapse to event-only or span-only loses irrecoverable instrumentation. Terminology correction from v1.1 ("sibling" → "child-per-attempt") reflects C1's topology authority per `c1-orchestration-control` SKILL.md: retry attempts are children of the parent operation; attempts are siblings TO EACH OTHER under that parent. T-perm-3 (C1↔C9) ENGAGED at default `pre-declared-with-allowlist` tunable value; per-retry-attempt handoff payload re-emission discipline (§1.2.3) enforces the default without per-attempt mutation.

- **(h) F2-12 sub-scope (iii) trace-ingestion dedup composition with F2 idempotency_key resolution.** Council §5.2 (C7 primary algorithm) + §5.3 (C3 co-primary; T-perm-2 engaged) committed the `engine.replay_disposition`-discriminated dedup algorithm because uniform dedup policy is incorrect: `deterministic_replay` engines (Temporal, DBOS, Restate) require zero-additional-cost re-read semantics; `checkpoint_resume` engines (LangGraph) require new-attempt cost accrual; `no_replay` engines must ERROR on re-ingestion. The `engine.replay_disposition` attribute (D1 v1.2 §1.1.1) and the F2 state-ledger entry shape extension (D1 v1.2 §1.1.2.2 with `original_trace_id` + `original_span_id` fields) are the load-bearing substrate. cause_attribution invariance check (§1.5.2) closes the deterministic-replay-contract-violation detection surface. Per-attempt cost-attribution discipline (§1.5.3) closes the cost-double-counting surface across retry sequences. T-perm-2 (C2↔C3) ENGAGED at sub-scope (iii); reconciled via idempotency_key composition contract; permanent tension preserved at Layer 3 without re-litigation.

## Consequences

[Preserved verbatim from v1.1 §Consequences (a)–(j).]

**v1.2 consequence delta.** F2-12 sub-scopes (ii) + (iii) closure produces four downstream effects:

- **ADD v1.3 absorption (cascade Step 3).** §1.2 engine.* 4-attribute namespace + §1.2.2 retry.* 6-attribute namespace + §1.2.3 sub-agent boundary under retry + §1.5 dedup algorithm + §1.5.1 / §1.5.2 / §1.5.3 sub-sections absorbed into ADD v1.3 §6.3.1; F2-12 active path declaration updated to "F2-12 CLOSED at cascade close (Step 3 ADD v1.3 + Step 4 PRD v1.1 + Step 5 specs v1.3 + Step 6 plans v2.2)."
- **PRD v1.1 revision (cascade Step 4).** R-CP-04 (workflow lifecycle event surface) absorbs the 4-attribute `engine.*` namespace and the 6-attribute `retry.*` namespace requirement; R-CP-07 (replay-resumption semantics) carries the new `engine.replay_disposition` attribute and the dedup-algorithm requirement; R-OD-* cost-attribution-per-span requirements absorb per-attempt cost discipline.
- **CP spec v1.3 revision (cascade Step 5a).** C-CP-09 §9.1 engine.* attribute declaration extends from 3 → 4 attributes citing D1 v1.2 §1.1.1; C-CP-08 §8.4 F2-12 affected-contract notation closes (all three sub-scopes resolved); §5.4 retry.attempt sampling discipline amended per §1.2.2.4.
- **OD spec v1.3 revision (cascade Step 5b).** C-OD-14 cost-attribution-per-span contract amended with dedup-algorithm specification per §1.5 + per-attempt cost discipline per §1.5.3; trace-ingestion dedup composition added per §1.5.1 orthogonality + §1.5.2 invariance check.

## Alternatives considered

[Preserved verbatim from v1.1 §Alternatives.]

**v1.2 alternative consideration delta.** F2-12 sub-scopes (ii) + (iii) resolution at v1.2 considered three alternatives rejected at council:

- **Alternative 11: Event-only retry.attempt (no child span).** Rejected because (i) per-attempt cost-attribution at §1.5.3 requires a span-shaped cost-accrual unit — event-only loses the cost roll-up surface; (ii) per-attempt sub-agent topology (§1.2.3) requires a span anchor for sub-agent span tree parentage — event-only forces sub-agent spans to parent the original operation, collapsing per-attempt isolation; (iii) operator TUI trace browser UX (per `c11-operator-local` SKILL.md §4.1.24) cannot expand a retry attempt's child span tree without a span anchor.
- **Alternative 12: Span-only retry-attempt (no parent event).** Rejected because (i) operator scanning the parent operation's event timeline cannot see retry occurred without traversing children — the parent-perspective surface is lost; (ii) `parent.attempts_remaining == 0` retry-budget-exit boundary requires an always-sampled event marker at the parent (per §1.2.2.4); span-only cannot provide it without conflating with the child span's sampling discipline.
- **Alternative 13: Uniform dedup policy at trace-ingestion (no engine.replay_disposition discrimination).** Rejected because (i) `deterministic_replay` engines require zero-additional-cost re-read at replay — uniform dedup either DROPs every re-emission (breaking `checkpoint_resume`) or RECORDs every re-emission (breaking `deterministic_replay` cost-attribution); (ii) per-engine-class semantics are engine-architecturally bound (Cluster 2 V2 §2.3.2 [HIGH]) — uniform dedup imposes an incorrect policy on at least one class; (iii) cause_attribution invariance check (§1.5.2) requires per-disposition behavior to detect replay-contract violations meaningfully.

## References

### Shape 1 — Substrate dependency declaration

[Preserved verbatim from v1.1.]

### Shape 2 — Pattern Reference Catalog source citations

[Preserved verbatim from v1.1.]

### Shape 3 — Per-axis recommendation citation

[Preserved verbatim from v1.1.]

### Shape 4 — Parent F-ADR / D-ADR citation (v1.2 amendment)

[v1.1 entries preserved verbatim; v1.2 entry amended:]

- ADR-D1 v1.2 §1.1.1 (canonical 4-attribute engine.* namespace declaration) + §1.1.2 (per-engine-class replay-emission discipline) + §1.1.2.2 (F2 state-ledger entry shape extension) — D6 v1.2 §1.2 engine.* row and §1.5 dedup algorithm inheritance sources.

### Shape 5 — Persona document trace

[Preserved verbatim from v1.1.]

### Substrate research citations (corpus-derived)

[Preserved verbatim from v1.1.]

### Permanent tension ledger updates

[v1.1 entries preserved verbatim; v1.2 entries appended:]

- T-perm-3 (C1 ↔ C9): D6-layer adjacency at retry.attempt parent-child topology seam. F1-layer (per-layer time-budget) + D1-layer (`topology_fault_handling`) + D4-layer (`topology_fault_handling × workload_class × topology_pattern`) resolutions stand. D6 v1.2 §1.2.3 sub-agent boundary under retry honors `pre-declared-with-allowlist` default. **Status: ENGAGED at sub-scope (ii); honored at default; ledger-reference-only carry-forward; no D6-layer revision to T-perm-3.**
- T-perm-2 (C2 ↔ C3): D6-layer engagement at trace-ingestion dedup composition seam. F2-layer resolution stands per F3 v1.1 §References explicit framing. D6 v1.2 §1.5 dedup algorithm + §1.5.3 per-attempt cost-attribution reconcile via idempotency_key composition contract (idempotency_key is canonical join key; within-turn span emission populates ledger; replay recovers from ledger). **Status: ENGAGED at sub-scope (iii); reconciled via idempotency_key composition; ledger-reference-only carry-forward; no D6-layer revision to T-perm-2.**

### Workflow and skill discipline references

[v1.1 entries preserved verbatim; v1.2 entries appended:]

- `Project_Workflow_v1_7.md` §3.1 — `Status: Proposed` preservation discipline; D6 v1.2 carries Proposed posture into cascade Step 3 entry.
- `Project_Workflow_v1_7.md` §4.1.2 — Class-2 finding resolution path; D6 v1.2 instantiates for F2-12 sub-scopes (ii) + (iii).
- `Project_Workflow_v1_7.md` §7 — fidelity-grammar discipline (Path δ revision); applied across all v1.2 amendment sites.
- `F2-12_Closure_Path_Execution_Kickoff.md` §3.1 (F2-12 three-sub-scope enumeration) + §3.2 (canonical 6-step closure cascade) + §7.2 Step 2 ADR-revisions discipline — v1.2 cascade scope authority.
- `F2-12_Council_Deliberation_Output.md` §5 (sub-scope (iii) deliberation) + §6 (sub-scope (ii) deliberation) + §8.2 (ADR-D6 v1.1 → v1.2 amendment specification) — v1.2 amendment-scope substrate.
- ADR-D1 v1.2 (cascade Step 2a output) §1.1.1 + §1.1.2 + §1.1.2.2 — substrate inheritance for §1.2 engine.* row + §1.5 dedup algorithm.
- `spec-writer` SKILL.md council-formalization sub-mode — v1.2 authoring discipline per cascade Step 2b routing.
- `c7-observability` SKILL.md (council Primary at sub-scopes (i) + (iii)) — dedup algorithm schema authority.
- `c9-reliability-recovery` SKILL.md (council Primary at sub-scope (ii)) — retry-attempt span schema + parent-span event schema authority.
- `c3-state-persistence` SKILL.md — F2 state-ledger entry shape composition; per-attempt entry discipline at §1.5.1.
- `c5-validation-contract` SKILL.md — cause_attribution catalog extension at §1.5.2; fail-class composition with retry sequence at §1.2.2.1.
- `c1-orchestration-control` SKILL.md — child-per-attempt topology selection at §1.2.2 + §1.2.3.
- `c11-operator-local` SKILL.md — TUI trace browser UX for retry sequences at §1.2.2.

### Convening artifact citations

[v1.1 entries preserved verbatim; v1.2 entries appended:]

- F2-12 cascade Step 1 council deliberation per `F2-12_Council_Deliberation_Output.md`:
  - Convening Block (6 voices: C7 + C9 primaries; C3, C5, C1, C11 consultants; OD-F212-2.A full 6-voice convening) — §2 of council output.
  - CCR (7 cross-cutting concerns; Security + Observability + Cost + Reliability + Eval-ability + HITL/local-first Touched; Blast radius Not touched) — §3 of council output.
  - Voice contributions at sub-scope (iii) — §5 of council output (C7 primary algorithm; C3 co-primary T-perm-2 surface; C9 + C5 propose-refinement on orthogonality + invariance; C11 + C1 concur-with-rationale).
  - Voice contributions at sub-scope (ii) — §6 of council output (C9 primary BOTH-event-AND-span discipline; C1 co-primary T-perm-3 surface child-per-attempt topology; C7 + C5 + C3 propose-refinement on schema + fail-class composition + ledger discipline; C11 concur-with-rationale).
  - TENSION block — T-perm-3 (C1↔C9) ENGAGED at sub-scope (ii) honored at default; T-perm-2 (C2↔C3 via C7) ENGAGED at sub-scope (iii) reconciled via idempotency_key composition; T-perm-1 NOT engaged at sub-scopes (ii) + (iii) — §7 of council output.

---

*Filed 2026-05-14 at F2-12 cascade Step 2b per `Project_Workflow_v1_7.md` §4.1.2 (F2-12 sub-scopes (ii) + (iii) closure: §1.2 engine.* row updated to 4-attribute schema citing D1 v1.2 §1.1.1; §1.2 lifecycle event set retry.attempt terminology corrected to child-per-attempt; new §1.2.2 retry.* namespace with 6-attribute span schema + 3-field parent event schema; new §1.2.3 sub-agent boundary under retry composition; §1.5 dedup algorithm specification + new §1.5.1 replay-aware dedup orthogonality + §1.5.2 cause_attribution invariance check + §1.5.3 per-attempt cost-attribution discipline). Step 2 closure: D1 v1.2 + D6 v1.2 both filed; cascade segment boundary per OD-F212-4.A. Recommended next step: cascade Step 3 (ADD v1.3 consolidation) per `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 — D1 v1.2 + D6 v1.2 substantive amendments absorbed into `Architectural_Design_Document_v1_3.md`; §6.3.1 active path declaration updated to "F2-12 CLOSED at cascade close."*