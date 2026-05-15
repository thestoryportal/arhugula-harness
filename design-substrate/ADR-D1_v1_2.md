# ADR-D1: Specific durable-execution substrate — engine-class commitment with per-deployment-surface candidate mapping

## Status

Proposed
Date: 2026-05-10
Phase: 3b Stage 1 (per `Project_Workflow_v1_1.md` §2.3.3) — Phase 3 closed; in F2-12 cascade revision per `Project_Workflow_v1_7.md` §4.1.2
Promotion path: Accepted at ADD v1.3 absorption per Workflow v1.7 §3.1
Revision: v1 → v1.1 (P3c-CK iter-1 close revision pass per Path A — F2-07 resolution: `engine.*` attribute names back-declared at §1.1 source via new §1.1.1 sub-section)
Revision date: 2026-05-10
Promotion: P3c-CK final clearance — 2026-05-11
**Revision: v1.1 → v1.2 (F2-12 cascade Step 2a per `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 + `F2-12_Council_Deliberation_Output.md` §8.1; sub-scope (i) span re-emission semantics under engine replay: 3-attribute → 4-attribute `engine.*` namespace extension with new `engine.replay_disposition`; new §1.1.2 per-engine-class replay-emission discipline subsection; §1.1 taxonomy table extended with per-class `engine.replay_disposition` default column; F2 state-ledger entry shape extension at §1.1.2 for trace context durability under `deterministic_replay`)**
**Revision date: 2026-05-14**

## Change-note (v1.1 → v1.2)

**Scope of revision.** F2-12 cascade Step 2a single-sub-scope (i) closure pass per `F2-12_Closure_Path_Execution_Kickoff.md` §3.1 + `F2-12_Council_Deliberation_Output.md` §4 resolution. The revision pass formalizes the council's per-engine-class span re-emission discipline under engine replay as an amendment to the `engine.*` namespace and the §1.1 engine-class taxonomy. Three discrete amendment sites: §1.1.1 (3-attribute → 4-attribute namespace extension; new `engine.replay_disposition` with 5-value enum closed-mapped to `engine.class`); new §1.1.2 (per-engine-class replay-emission discipline subsection committing span-re-emission semantics + F2 state-ledger entry shape extension for trace context durability under `deterministic_replay`); §1.1 taxonomy table (new column `Replay-emission disposition` carrying per-class default `engine.replay_disposition` value). F2-12 sub-scopes (ii) `retry.attempt` sibling-span discipline and (iii) trace-ingestion dedup composition route to ADR-D6 v1.2 per `F2-12_Council_Deliberation_Output.md` §8.2; D1 v1.2 carries no (ii) or (iii) content. Workflow v1.7 §7 fidelity-grammar discipline applied: no Pattern P1 cross-artifact name drift; no Pattern P2 verbatim-claim-contradicted; all citation anchors substrate-verified.

**Status posture.** `Status: Proposed` preserved per `Project_Workflow_v1_7.md` §3.1 — promotion to `Accepted` blocked until ADD v1.3 absorption (F2-12 cascade Step 3). D1 v1.2 enters cascade Step 3 as substrate input for `Architectural_Design_Document_v1_3.md` authoring.

**Sections preserved verbatim from v1.1.** §1.1 engine-class taxonomy table rows + the v1.1 columns (Class, Lifecycle ownership, Capability-floor mechanism, C3-tier residence, Concurrent-resume mitigation); §1.2 per-deployment-surface candidate mapping; §1.3 D1-layer T-perm-3 resolution; §1.4 capability-floor preservation; Context; Rationale (a) (b) (c) (d); Consequences (a) (b) (c) (d); Alternatives 1–5; References Shapes 1–5 (Substrate dependency declaration, Pattern Reference Catalog citations, Per-axis recommendation citation, Parent F-ADR citation, Persona document trace); Substrate research citations; Convening artifact citations (v1.1 entries preserved; v1.2 entries appended).

**Changes inline.** Status block (Revision: v1.1 → v1.2 + Revision date lines appended). This Change-note (v1.1 → v1.2) section. §1.1.1 sub-section amended from 3-attribute to 4-attribute declaration with new `engine.replay_disposition` attribute added per `F2-12_Council_Deliberation_Output.md` §4.2 C7 primary contribution. New §1.1.2 sub-section inserted between §1.1.1 and §1.2 declaring per-engine-class replay-emission discipline + F2 state-ledger entry shape extension. §1.1 engine-class taxonomy table extended with one new column `Replay-emission disposition` carrying per-class default value. References "Workflow and skill discipline references" extended with new entries (Workflow v1.7 §3.1, §4.1.2, §7; F2-12 cascade kickoff; F2-12 council deliberation output; `spec-writer` SKILL council-formalization sub-mode). Convening artifact citations extended with F2-12 cascade Step 1 council deliberation reference. Closing footer revised to note v1.2 filing.

**Cross-cascade-step coordination.** ADR-D6 v1.2 (cascade Step 2b) absorbs sub-scopes (ii) + (iii) per `F2-12_Council_Deliberation_Output.md` §8.2. D6 v1.2 §1.2 engine.* namespace row updates from 3-attribute to 4-attribute citing this D1 v1.2 §1.1.1 as canonical declaration source. D1 v1.2 → D6 v1.2 substrate flow is Pattern P1 (cross-artifact-name-drift) prevention discipline: `engine.replay_disposition` attribute name is canonical at D1 §1.1.1 and inherited at D6 §1.2 without re-declaration.

## Context

[Preserved verbatim from v1.1; not reproduced here for length. v1.1 §Context begins "This ADR closes the substrate-TBD deferral declared at `ADR-F3.md` v1.1 §11.3.1..." and runs through "...F2's read/write contract pair rather than relitigating per F3 v1.1 §References explicit framing." See `ADR-D1.md` v1.1 lines 25–35.]

## Decision

Commit at the D1 layer to a **five-element engine-class taxonomy with parametric per-deployment-surface candidate selection**, where the engine-class taxonomy enumerates the failure-containment and lifecycle-ownership shapes any candidate must inhabit, and the per-deployment-surface mapping commits the candidate set per surface tier (local-development / self-hosted-server / managed-cloud) as the contract for deployment-surface-time engine selection downstream. Engine class is committed at D1; specific engine-within-class is deferred to deployment-surface-time per surface row of the mapping table. **At v1.2, the engine-class taxonomy is materialized at the observability substrate as a 4-attribute `engine.*` namespace (was 3 at v1.1), with per-class replay-emission discipline committed at new §1.1.2.**

### 1.1 Engine-class taxonomy

| # | Class | Lifecycle ownership | Capability-floor mechanism | C3-tier residence | Concurrent-resume mitigation | **Replay-emission disposition (v1.2)** |
|---|---|---|---|---|---|---|
| 1 | **Event-sourced-replay** | Engine | Engine-native: replay from Event History; activity outputs cached and replayed deterministically | Engine event history (Tier-3) + F2 state-ledger (Tier-5) joined on `idempotency_key` | Engine-native lease (Temporal placement primitive; DBOS transaction boundary) | **`deterministic_replay`** — replay is deterministic re-read; spans NOT re-emitted; original `trace_id` + `span_id` recovered from F2 state-ledger entry |
| 2 | **Save-point-checkpoint** | Application (composed atop engine save points) | Engine exposes per-super-step checkpoint; harness composes lease + dedup + resumption above | Checkpointer state (Tier-3) + F2 state-ledger (Tier-5) | Application-level lease (Redis lease, DB unique constraint, worktree isolation) | **`checkpoint_resume`** — activity-level spans re-emit on resume; NEW `span_id`; parent `span_id` preserved from checkpoint |
| 3 | **Pure-pattern-no-engine** | Harness | Harness owns full durability contract over F2 substrate (filesystem-journal + state-ledger + idempotency-key) | F2 filesystem (Tier-3) + F2 state-ledger (Tier-5) | Harness-owned lease (worktree isolation per ADR-F2 [HIGH]; DB unique constraint) | **`no_replay`** — no replay concept; every invocation is new operation; spans always fresh |
| 4 | **Reconciler-loop** | K8s controller | Reconciler-native: CRDs persist agent state across restarts (humanlayer/agentcontrolplane reference) | K8s etcd (Tier-3) + CRD events (Tier-5) | etcd compare-and-swap | **`reconciler_iteration`** — each reconciliation is new execution; spans fresh per iteration; `reconciler.iteration_number` discriminator |
| 5 | **WAL-segment** | Harness | WAL-owned: append-only segment log with per-segment resume (shareAI-lab/Kode-Agent reference) | WAL segments (Tier-3) + segment metadata (Tier-5) | Harness-owned per-segment lease | **`wal_consume`** — consumer replay is new processing; spans fresh per consumption; `wal.consumer_group` discriminator |

### 1.1.1 Span attribute names declared by §1.1 (v1.2: 4-attribute namespace)

The §1.1 engine-class taxonomy is materialized as the **`engine.*` span attribute namespace** ingested by ADR-D6 §1.2 row `engine.*` under the OTel/OTLP export contract. D1 §1.1.1 is the canonical declaration site for these attribute names; D6 §1.2 inherits without re-declaration. **At v1.2, four attribute names declared (was three at v1.1; `engine.replay_disposition` added per F2-12 sub-scope (i) closure):**

- **`engine.class`** — discriminator over the §1.1 *Class* column. Values per D6 §1.2 alignment: `event-sourced-replay` / `save-point-checkpoint` / `pure-pattern-no-engine` / `reconciler-loop` / `WAL-segment` (acronym preserved at row 5; first four lower-cased and hyphen-joined per §1.1 row labels). Every span emitted under D1 §1.1's lifecycle envelope (workflow-start, step-boundary, fallback-trigger, retry-attempt, breaker-trip, lease-acquired/released, resumption — per F3 v1.1 capability-floor (iv)) carries `engine.class` as a stable attribute. Cardinality is bounded at five — the closed enumeration of §1.1 rows.

- **`engine.event_history.tier`** — discriminator over the §1.1 *C3-tier residence* column at C3-tier-substrate granularity. Values: `Tier-3` (engine-internal durable substrate per row — engine event history / checkpointer state / F2 filesystem / K8s etcd / WAL segments) or `Tier-5` (F2 state-ledger join surface — `idempotency_key`-keyed entry per row, with row 4's CRD events as the row-specific Tier-5 stand-in). Span events that reference engine-internal durable state (e.g., replay-from-event-history, checkpoint-write, segment-append) carry `Tier-3`; span events that reference state-ledger join surface (e.g., idempotency-key-resolved, ledger-entry-written) carry `Tier-5`. Per-row mapping inherits §1.1 *C3-tier residence* column without re-derivation.

- **`engine.event.id`** — per-engine-event identifier joining the F2 state-ledger entry shape `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` on `idempotency_key`. Type: opaque string under each engine class's native ID convention (Temporal eventId; LangGraph checkpoint_id; ACP CRD event UID; Kode-Agent segment offset; pure-pattern harness-assigned UUID). Cross-engine-class portability is achieved through the `idempotency_key` join on F2 — `engine.event.id` is engine-internal-naming, the join key is harness-canonical.

- **`engine.replay_disposition` (v1.2; new attribute)** — discriminator over the §1.1 *Replay-emission disposition* column. Values per §1.1 table column 6: `deterministic_replay` (row 1 event-sourced-replay) / `checkpoint_resume` (row 2 save-point-checkpoint) / `no_replay` (row 3 pure-pattern-no-engine) / `reconciler_iteration` (row 4 reconciler-loop) / `wal_consume` (row 5 WAL-segment). Cardinality is bounded at five — the closed enumeration of §1.1 rows, with closed mapping to `engine.class` (one `engine.replay_disposition` value per `engine.class` value; no cross-class value sharing). Every span emitted under D1 §1.1's lifecycle envelope carries `engine.replay_disposition` as a stable attribute. The attribute composes with §1.1.2 per-engine-class replay-emission discipline as the runtime discriminator at D6 §1.5 trace-ingestion dedup (per ADR-D6 v1.2 §1.5 amendment).

**Capability-floor (iv) traceability.** F3 v1.1 capability-floor (iv) requires observable lifecycle exposing seven event types (workflow-start, step-boundary, fallback-trigger, retry-attempt, breaker-trip, lease-acquired/released, resumption); §1.1.1 declares the attribute substrate for these events. Per-event-type emission semantics under engine replay are committed at new §1.1.2 below (sub-scope (i) closure); `retry.attempt` sibling-span vs span-event treatment and trace-ingestion dedup via `engine.event.id` × `idempotency_key` × `engine.replay_disposition` composition are committed at ADR-D6 v1.2 §1.2 + §1.5 (sub-scopes (ii) + (iii) closure).

### 1.1.2 Per-engine-class replay-emission discipline (v1.2; new subsection)

Per-engine-class replay-emission discipline commits the span-emission semantics under engine replay for each of the five §1.1 engine classes. The discipline is engine-class-bound: a uniform replay-emission policy across all classes is incorrect because the five classes have structurally distinct replay semantics (per `F2-12_Council_Deliberation_Output.md` §4.2 C7 primary contribution).

#### 1.1.2.1 Per-class emission semantics

| Class | `engine.replay_disposition` | Replay-emission discipline |
|---|---|---|
| Row 1 — Event-sourced-replay | `deterministic_replay` | **NO new span emission at replay time.** Replay is deterministic re-read of the original execution; the original span is the canonical instrumentation record. The replay execution recovers `trace_id` + `span_id` from the F2 state-ledger entry (per §1.1.2.2 ledger entry shape extension). D6 §1.5 trace-ingestion dedup (per ADR-D6 v1.2 §1.5) DROPs replay-derived span ingestions matching ledger trace context. |
| Row 2 — Save-point-checkpoint | `checkpoint_resume` | **NEW span emission at resume time.** Activity-level spans re-emit on resume; the new span carries a NEW `span_id` and references the parent `span_id` preserved from the pre-resume checkpoint state. `engine.replay_disposition=checkpoint_resume` marks the span as replay-derived; D6 §1.5 dedup RECORDs the new span as a distinct ingestion (per-attempt cost-attribution accrues for the resumed execution). |
| Row 3 — Pure-pattern-no-engine | `no_replay` | **No replay concept applies.** Every invocation produces fresh spans with fresh `trace_id` + `span_id`; the harness owns full durability over F2 substrate without engine-mediated replay. D6 §1.5 dedup reaching a `no_replay` span for a key already in the ledger ERRORs (per ADR-D6 v1.2 §1.5; ERROR class signals unexpected re-ingestion for non-replay engine class). |
| Row 4 — Reconciler-loop | `reconciler_iteration` | **NEW span emission per reconciliation iteration.** Each reconciliation is a fresh execution; spans are emitted fresh per iteration; the K8s reconciler emits a span tree rooted at the reconciliation operation. `reconciler.iteration_number` attribute discriminates iterations. D6 §1.5 dedup RECORDs each iteration as distinct. |
| Row 5 — WAL-segment | `wal_consume` | **NEW span emission per consumption.** Each consumer replay is new processing of WAL segments; spans are emitted fresh per consumption. `wal.consumer_group` attribute discriminates consumer groups; cross-consumer-group consumption of the same segment is permitted and produces distinct span trees. D6 §1.5 dedup RECORDs each consumption as distinct. |

#### 1.1.2.2 F2 state-ledger entry shape extension (v1.2)

The `deterministic_replay` discipline at row 1 depends on durable trace-context preservation: replay execution must recover `trace_id` + `span_id` from the F2 state-ledger entry, otherwise the no-re-emission discipline cannot reconstruct the original trace context. The F2 state-ledger entry shape extends with two new fields under D1 v1.2 specialization:

| Field (v1.2 addition) | Type | Purpose |
|---|---|---|
| `original_trace_id` | string (32-hex; OTel W3C Trace Context format) | OTel `trace_id` of the original operation invocation; durable across replay |
| `original_span_id` | string (16-hex; OTel W3C Trace Context format) | OTel `span_id` of the original operation span; durable across replay |

Both fields populate at first emission (when the F2 state-ledger entry is appended). Replay execution reads these fields and reuses them under `engine.replay_disposition=deterministic_replay`; the OTel SDK is configured to NOT generate new IDs for spans that recover from durable trace context. ADR-D6 v1.2 §1.5 specifies the dedup algorithm that consumes these fields at trace-ingestion time. ADR-F2's existing state-ledger entry shape `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` is preserved verbatim; the two new fields are additive at the entry-shape level without breaking F2's hash-chain construction discipline (per ADR-F2 §References; hash-chain construction extends to cover the new fields, with C3 Tier 5 ledger discipline and C10 hash-chain integrity discipline composing at the sqlite `ledger_entries` schema per `c11-operator-local` SKILL §4.1.28).

#### 1.1.2.3 Composition with sub-scopes (ii) + (iii) at ADR-D6 v1.2

The `engine.replay_disposition` attribute and the §1.1.2.2 ledger entry shape extension are inputs to ADR-D6 v1.2's amendments at sub-scope (ii) `retry.attempt` sibling-span discipline (per `F2-12_Council_Deliberation_Output.md` §6 — retry attempts as child spans of parent operation with `engine.replay_disposition` composing in the orthogonal dedup discriminator at §5.4) and sub-scope (iii) trace-ingestion dedup composition (per §5 — dedup algorithm discriminates by `engine.replay_disposition`; cause_attribution invariance check applies at `deterministic_replay`). The cross-ADR substrate flow: D1 v1.2 §1.1.1 declares the attribute name canonically; D1 v1.2 §1.1.2.2 declares the ledger entry shape extension; ADR-D6 v1.2 inherits both as ingestion contracts without re-declaration. Pattern P1 (cross-artifact name drift) prevention is enforced by D6 v1.2 §1.2 engine.* row citing D1 v1.2 §1.1.1 as canonical source.

### 1.2 Per-deployment-surface candidate mapping

[Preserved verbatim from v1.1; not reproduced here for length. v1.1 §1.2 mapping table runs at lines 63–69 covering local-development, self-hosted-server, and managed-cloud surface rows.]

### 1.3 D1-layer T-perm-3 resolution

[Preserved verbatim from v1.1; not reproduced here for length. v1.1 §1.3 runs at lines 71–86 declaring `topology_fault_handling ∈ {ABOVE_ENGINE, BELOW_ENGINE, RECONCILER}` tunable parameter with per-surface defaults.]

### 1.4 Capability-floor preservation across classes

[Preserved verbatim from v1.1; not reproduced here for length. v1.1 §1.4 runs at lines 88–96 with the four-row × five-column capability-floor preservation matrix.]

## Rationale

[Preserved verbatim from v1.1; not reproduced here for length. v1.1 §Rationale runs at lines 99–115 covering (a) pattern this decision follows, (b) persona-constraint application, (c) T-perm-3 stance, (d) cross-axis composition. v1.2 amendment to (d) at the D6 forward-reference clause: the cross-axis composition with D6 now references ADR-D6 v1.2 (was v1.1) for the observability backend composition, with `engine.replay_disposition` as the v1.2-canonical attribute at D6 §1.2 engine.* row.]

## Consequences

[Preserved verbatim from v1.1; not reproduced here for length. v1.1 §Consequences runs at lines 117–154 covering (a) downstream D-ADR dependencies, (b) deployment-surface-time × workload-class-bind-time selection, (c) Phase 3c integration verification, (d) permanent-tension ledger updates.]

**v1.2 consequence delta.** F2-12 sub-scope (i) closure produces three downstream effects:

- **ADD v1.3 absorption (cascade Step 3).** §1.1 taxonomy table (6-column form with `Replay-emission disposition` column) + §1.1.1 (4-attribute namespace) + §1.1.2 (replay-emission discipline + F2 state-ledger entry shape extension) absorbed into ADD v1.3 §6.3.1; F2-12 active path declaration updated to "F2-12 sub-scope (i) CLOSED at D1 v1.2; sub-scopes (ii) + (iii) CLOSED at D6 v1.2; closure cascade complete at ADD v1.3 absorption."
- **PRD v1.1 revision (cascade Step 4).** R-CP-04 (workflow lifecycle event surface) absorbs the `engine.replay_disposition` attribute requirement; R-CP-07 (replay-resumption semantics) carries the new attribute as the engine-class-visible replay-resumption discriminator per `c7-observability` SKILL.md schema authority.
- **CP spec v1.3 revision (cascade Step 5).** C-CP-09 §9.1 engine.* attribute declaration extends from 3 → 4 attributes citing D1 v1.2 §1.1.1; C-CP-08 §8.4 F2-12 affected-contract notation closes (sub-scope (i) resolution recorded).

## Alternatives considered

[Preserved verbatim from v1.1; not reproduced here for length. v1.1 §Alternatives runs at lines 156–164 covering five alternatives.]

**v1.2 alternative consideration delta.** F2-12 sub-scope (i) resolution at v1.2 considered two alternatives that were rejected at council deliberation:

- **Alternative 6: Uniform replay-emission policy (re-emit on all classes; ignore engine-class distinction).** Rejected because (i) `event-sourced-replay` engines (Temporal, DBOS, Restate) are explicitly deterministic re-read substrates per Cluster 2 V2 §2.3.2 [HIGH] — uniform re-emission contradicts the engine-native semantics; (ii) cost-attribution-per-span at D6 §1.5 would double-count on every replay, inflating per-attempt cost by N (replay count) for every event-sourced-replay execution; (iii) operator TUI trace browser UX (per `c11-operator-local` SKILL.md §4.1.24) would show duplicate trace nodes per replay, breaking the "one trace per logical workflow execution" UX commitment.
- **Alternative 7: Replay-emission as deployment-surface-time decision (defer to per-surface configuration).** Rejected because (i) replay-emission is engine-class-bound at the architectural layer — deferring to deployment-surface-time produces deployment-surface × engine-class matrix complexity without architectural benefit; (ii) the C7 schema authority for `engine.replay_disposition` requires canonical declaration at D1 (per `c7-observability` SKILL — schema authority over events from other voices); (iii) cross-deployment trace portability requires consistent replay-emission semantics, which deployment-surface-time deferral cannot guarantee.

## References

### Shape 1 — Substrate dependency declaration

[Preserved verbatim from v1.1.]

### Shape 2 — Pattern Reference Catalog source citations

[Preserved verbatim from v1.1.]

### Shape 3 — Per-axis recommendation citation

[Preserved verbatim from v1.1.]

### Shape 4 — Parent F-ADR citation

[Preserved verbatim from v1.1.]

### Shape 5 — Persona document trace

[Preserved verbatim from v1.1.]

### Substrate research citations (corpus-derived)

[Preserved verbatim from v1.1.]

### Workflow and skill discipline references

[v1.1 entries preserved verbatim; v1.2 entries appended:]

- `Project_Workflow_v1_7.md` §3.1 — `Status: Proposed` preservation discipline on revised D-ADRs until ADD v1.3 absorption; D1 v1.2 carries Proposed posture into cascade Step 3 entry.
- `Project_Workflow_v1_7.md` §4.1.2 — Class-2 finding resolution path: revised ADR with version bump in the artifact + change-note inline. D1 v1.2 instantiates this shape for F2-12 sub-scope (i).
- `Project_Workflow_v1_7.md` §7 — fidelity-grammar discipline (Path δ revision); applies to all v1.7-authored revision-pass artifacts; D1 v1.2 authored under this discipline.
- `F2-12_Closure_Path_Execution_Kickoff.md` §3.1 (F2-12 three-sub-scope enumeration) + §3.2 (canonical 6-step closure cascade) + §7.2 Step 2 ADR-revisions discipline — v1.2 cascade scope authority.
- `F2-12_Council_Deliberation_Output.md` §4 (sub-scope (i) deliberation) + §8.1 (ADR-D1 v1.1 → v1.2 amendment specification) — v1.2 amendment-scope substrate.
- `spec-writer` SKILL.md council-formalization sub-mode — v1.2 authoring discipline per cascade Step 2a routing.
- `c7-observability` SKILL.md — schema authority for `engine.replay_disposition` attribute (council Primary at sub-scope (i)).
- `c3-state-persistence` SKILL.md — F2 state-ledger entry shape extension at §1.1.2.2 (Tier 5 ledger discipline + hash-chain integrity composition).
- `c11-operator-local` SKILL.md §4.1.28 — sqlite `ledger_entries` schema extension absorbing `original_trace_id` + `original_span_id` fields.

### Convening artifact citations

[v1.1 entries preserved verbatim; v1.2 entries appended:]

- F2-12 cascade Step 1 council deliberation per `F2-12_Council_Deliberation_Output.md`:
  - Convening Block (6 voices: C7 + C9 primaries; C3, C5, C1, C11 consultants; OD-F212-2.A full 6-voice convening) — §2 of council output.
  - CCR (7 cross-cutting concerns; Security + Observability + Cost + Reliability + Eval-ability + HITL/local-first Touched; Blast radius Not touched) — §3 of council output.
  - Voice contributions at sub-scope (i) — §4 of council output (C7 primary; C9 co-primary on adjacent retry territory; C3 + C5 propose-refinement; C11 + C1 concur-with-rationale).
  - TENSION block — T-perm-3 (C1↔C9) ENGAGED at sub-scope (ii) honored at default; T-perm-2 (C2↔C3 via C7) ENGAGED at sub-scope (iii) reconciled via idempotency_key composition; T-perm-1 NOT engaged at sub-scope (i) — §7 of council output.

---

*Filed 2026-05-14 at F2-12 cascade Step 2a per `Project_Workflow_v1_7.md` §4.1.2 (F2-12 sub-scope (i) closure: `engine.replay_disposition` attribute added at §1.1.1; per-engine-class replay-emission discipline at new §1.1.2; F2 state-ledger entry shape extension at §1.1.2.2; §1.1 taxonomy table extended with 6th column). Recommended next session for D1: cascade Step 2b (ADR-D6 v1.2) per `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 — F2-12 sub-scopes (ii) + (iii) closure absorbing D1 v1.2 §1.1.1 4-attribute namespace and §1.1.2 replay-emission discipline as substrate inputs.*