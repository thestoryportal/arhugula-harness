# F2-12 Council Deliberation Output

## §1 Status block

| Field | Value |
|---|---|
| Artifact | `F2-12_Council_Deliberation_Output.md` |
| Status | **Filed** — F2-12 cascade Step 1 output per `F2-12_Closure_Path_Execution_Kickoff.md` §9.1 |
| Phase | F2-12 cascade execution — Step 1 of 6 |
| Date | 2026-05-14 |
| Predecessor artifacts | `F2-12_Closure_Path_Execution_Kickoff.md`; `F2-12_Cascade_Entry_Deferral_Note.md`; `Project_Workflow_v1_7.md`; ADR-D1 v1.1; ADR-D6 v1.1; CP spec v1.2; OD spec v1.2 |
| Successor artifacts | `ADR-D1_v1_2.md` (Step 2a, sub-scope (i)); `ADR-D6_v1_2.md` (Step 2b, sub-scopes (ii) + (iii)) |
| OD selections honored | OD-F212-1.A (Path δ before F2-12 — Workflow v1.7 in force); OD-F212-2.A (full 6-voice convening); OD-F212-3.C (sequential (i) → (iii) → (ii) dependency-aware); OD-F212-4.A (single combined session, segment boundaries between cascade steps) |
| Authoring discipline | `council-orchestrator` SKILL.md + 6 voice SKILL.md files (C7, C9, C3, C5, C1, C11); Workflow v1.7 §7 fidelity-grammar discipline |
| Filing destination | `/mnt/user-data/outputs/F2-12_Council_Deliberation_Output.md` |

---

## §2 Convening Block

### §2.1 Voices convened (per OD-F212-2.A)

| Voice | Role | Domain rationale (per kickoff §4.1) |
|---|---|---|
| **C7 Observability Architect** | Primary | Owns OTel GenAI semconv + span schema + per-attribute discipline + sampling. F2-12 sub-scopes (i) + (iii) are span-emission-discipline territory. |
| **C9 Reliability & Recovery Engineer** | Primary | Owns retry mechanics + retry.attempt event semantics + per-attempt timeout + breaker-trip event composition. F2-12 sub-scope (ii) is retry.attempt sibling-span discipline territory. |
| **C3 State, Memory & Persistence Architect** | Consultant (co-primary at sub-scope (iii) per T-perm-2 surface) | Owns durable state + F2 state-ledger entry shape + idempotency_key as canonical join key. F2-12 sub-scope (iii) trace-ingestion dedup composes against F2 state-ledger join surface. |
| **C5 Validation Contract Architect** | Consultant | Owns fail-classification at runtime gates. F2-12 sub-scope (i) span re-emission disposition under engine-replay boundary affects fail-class attribution at replay-time. |
| **C1 Orchestration & Control Architect** | Consultant (co-primary at sub-scope (ii) per T-perm-3 surface) | Owns control-flow + topology. F2-12 sub-scope (ii) retry.attempt sibling-span discipline affects parent-child topology under retry composition. |
| **C11 Operator Loop & Local Deployment Specialist** | Consultant | Owns TUI trace browser + operator-experience at replay-time event visibility. F2-12 sub-scope (i) span re-emission at replay-time affects TUI trace inspection surface. |

### §2.2 Question type classification

| Sub-scope | Question type | Anchor |
|---|---|---|
| (i) Span re-emission semantics under engine replay | Contract (per-engine-class disposition contract) | C7 |
| (iii) Trace-ingestion dedup composition with F2 idempotency_key | Cross-cutting (within-turn ↔ durable composition; T-perm-2 surface) | C7 + C3 co-primary |
| (ii) `retry.attempt` sibling-span discipline | Architectural (topology-vs-retry composition; T-perm-3 surface) | C9 + C1 co-primary |

### §2.3 Voices considered, not convened

None. Full 6-voice convening per OD-F212-2.A engaged the maximum voice set for F2-12 territory. C2 (Context Engineering & Attention Budget) and C4 (Tools & Integration), C6 (Model Strategy & Routing), C8 (Eval Engineer), C10 (Action Safety & Blast Radius) are not engaged at F2-12 substantive territory; their domains are referenced consulted-by-reference where surfaces touch.

### §2.4 Routing rationale per voice

| Voice | Rationale |
|---|---|
| C7 | F2-12 is fundamentally an observability-substrate question: what spans emit at replay, what attributes carry replay semantics, how cost-attribution composes with dedup. C7 anchors. |
| C9 | F2-12 sub-scope (ii) is retry-mechanics territory; retry.attempt is C9's canonical event. C9 anchors at (ii). |
| C3 | F2 state-ledger is C3's canonical durable substrate; idempotency_key is C3's authoritative join key. Sub-scope (iii) co-primary by structural necessity. |
| C5 | Fail-class taxonomy + cause_attribution annotation carried on retry/replay events; C5 owns the contract that those signals follow. |
| C1 | retry.attempt's parent-child topology is C1's territory; T-perm-3 engaged at sub-scope (ii). |
| C11 | TUI trace-browser UX at replay time + sqlite ledger schema extensions for trace_id/span_id durability. |

### §2.5 Pointer to CCR

See §3.

---

## §3 Cross-Cutting Receipt (CCR)

| Concern | Touched | Owner status | Pre-check note |
|---|---|---|---|
| **Security** | Touched | Consulted-by-reference (C10) | Hash-chain integrity discipline (C10 territory) operates over F2 state-ledger entries that carry trace_id + span_id under this resolution; C10's hash-chain construction rule (per `c10-action-safety` SKILL) extends to these fields without re-litigation. No new trust-boundary opened. |
| **Blast radius** | Not touched | — | F2-12 scope is observability + state-ledger composition; no new action class surfaced; no new blast-radius classification required. |
| **Observability** | Touched | Convened (C7 anchors) | F2-12 is observability-substrate territory by construction. C7's resolution at §4 + §5 + §6 is the canonical commitment. |
| **Cost** | Touched | Convened (C7 + C9) | Cost-attribution-per-span at D6 §1.5 is the load-bearing primitive at sub-scope (iii). Per-engine-class replay disposition discriminates whether cost re-accrues or amortizes. Per-attempt cost-attribution at sub-scope (ii) preserves accurate cost-per-attempt. |
| **Reliability** | Touched | Convened (C9 anchors at (ii)) | retry.attempt mechanics + breaker-trip composition are C9 territory. Retry-attempt-span carries `retry.cause_attribution` (from C5's annotation) + `retry.fail_class` (from C5's 5-class taxonomy). |
| **Eval-ability** | Touched | Consulted-by-reference (C8) | Surface exposed for C8 holdout: `replay_idempotence_rate` (per-attempt cost-attribution accuracy under replay); `retry_attempt_topology_compliance` (per-attempt parent-child invariance); `dedup_correctness_rate` (per-replay-disposition dedup outcome). C8 designs methodology; C7's schema makes these queryable. |
| **HITL / local-first** | Touched | Convened (C11) | Sqlite ledger schema extension at §4.1.28 absorbs trace_id + span_id fields; TUI trace-browser UX at §4.1.24 visually distinguishes replay-derived spans; no new HITL trigger introduced. |

---

## §4 Sub-scope (i) Deliberation — Span re-emission semantics under engine replay

### §4.1 Anchor question (per kickoff §3.1)

Event-sourced-replay engines (Temporal/Restate, Kafka WAL): when the workflow re-executes from event history at replay time, do spans re-emit (producing new span IDs, new trace context) or is replay a deterministic re-read without new span emission?

### §4.2 C7 primary contribution

**C7 commits to per-engine-class replay-emission discipline.** The five engine classes in ADR-D1 v1.1 §1.2 (`EVENT_SOURCED_REPLAY`, `SAVE_POINT_CHECKPOINT`, `PURE_PATTERN_NO_ENGINE`, `RECONCILER_LOOP`, `WAL_SEGMENT`) have structurally distinct replay semantics. A uniform replay-emission policy across all engine classes is incorrect; the disposition is engine-class-bound.

**C7 commits the engine.* namespace extension from 3 → 4 attributes.** Current canonical 3-attribute schema at CP spec §9.1 (`engine.class`, `engine.resumption_kind`, `engine.tech`) extends with one new attribute:

| Attribute | Type | Cardinality | Per-engine-class binding |
|---|---|---|---|
| `engine.replay_disposition` | enum | bounded at 5 | one value per `engine.class` value (closed mapping) |

**C7 specifies the 5-value `engine.replay_disposition` enum:**

| `engine.class` | `engine.replay_disposition` | Replay semantics |
|---|---|---|
| `EVENT_SOURCED_REPLAY` | `deterministic_replay` | Replay is deterministic re-read; spans NOT re-emitted; original trace_id + span_id recovered from F2 state-ledger entry |
| `SAVE_POINT_CHECKPOINT` | `checkpoint_resume` | Activity-level spans re-emit on resume; NEW span_id; parent span_id preserved from checkpoint |
| `PURE_PATTERN_NO_ENGINE` | `no_replay` | No replay concept; spans always fresh; every invocation is new operation |
| `RECONCILER_LOOP` | `reconciler_iteration` | Each reconciliation is new execution; spans fresh per iteration; `reconciler.iteration_number` discriminator |
| `WAL_SEGMENT` | `wal_consume` | Consumer replay is new processing; spans fresh per consumption; `wal.consumer_group` discriminator |

**C7 commits emission discipline.** For `deterministic_replay`: NO new span emission at replay time; the original span is the canonical instrumentation record. For all other dispositions: NEW span emission at replay/resume/iteration; the new span carries `engine.replay_disposition` as attribute marking it as replay-derived.

**Schema authority (per `c7-observability` SKILL §"Decision-claim vocabulary"):** *"C7 specifies the engine.replay_disposition attribute namespace extension to engine.* at CP spec §9.1, expanding the 3-attribute schema to 4 attributes, with the 5-value enum closed-mapped to engine.class."*

### §4.3 C9 co-primary contribution (adjacent territory)

**C9 proposes refinement.** Replay disposition composes with retry classification. The retry attempt under replay must distinguish "fresh retry" (new attempt against fresh execution) from "replay-of-prior-attempt" (deterministic re-read of a prior retry attempt's span). Without this discrimination, retry-budget exhaustion under replay would double-count and inflate failure rates.

**C9 commits trigger-and-timing composition.** For `deterministic_replay`: retry-budget is recovered from F2 state-ledger entry (not re-counted at replay). For `checkpoint_resume` and other re-emitting dispositions: retry-budget continues from the checkpoint-resume point; the resumed attempt is attempt N+1 not attempt 1.

**Defer-to-sub-scope-(ii).** Full retry composition specification at §6.

### §4.4 C3 consultant contribution — propose refinement

**C3 proposes the F2 state-ledger entry shape extension.** C7's `deterministic_replay` resolution requires `trace_id` + `span_id` to be DURABLE in the F2 state-ledger entry, otherwise the no-re-emission discipline cannot recover the original trace context at replay.

**C3 commits the ledger entry schema extension** (per `c3-state-persistence` SKILL decision-claim vocabulary):

| Field | Type | Purpose |
|---|---|---|
| `original_trace_id` | string (32-hex) | OTel trace_id of the original operation invocation; durable across replay |
| `original_span_id` | string (16-hex) | OTel span_id of the original operation span; durable across replay |
| (existing fields) | — | `idempotency_key` (canonical join key per IS spec §10.2), `engine.class`, `engine.resumption_kind`, fail-class, cause_attribution, hash-chain pointer |

**C3 surfaces tension with C7 (resolved within this deliberation).** C7's no-re-emission resolution depends on C3 absorbing the schema extension. C3 absorbs it under Tier 5 ledger discipline (`c3-state-persistence` SKILL — F2 state-ledger is Tier 5 with append-only + hash-chain integrity). The composition is clean; the dependency is mutual.

### §4.5 C5 consultant contribution — propose refinement

**C5 commits the fail-class durability discipline.** On replay, the original validator-fail-class MUST be preserved; replay does NOT re-classify. The C5 fail-class signal carried in F2 state-ledger entry must include both fail-class (5-class taxonomy per `c5-validation-contract` SKILL reconciliation: `transient-retry` / `Reflexion-recoverable` / `HITL-recoverable` / `permanent-fail-exit` / `terminal-fail-exit`) AND cause_attribution annotation.

**C5 commits the no-replay-re-classification invariant.** On `deterministic_replay`: the fail-class span event is NOT re-emitted; the durable record in F2 state-ledger entry is the canonical fail-class signal at replay.

### §4.6 C11 consultant contribution — concur-with-rationale + UX implication

**C11 concurs with C7's per-engine-class disposition.** TUI trace browser UX at replay time aligns with C7's resolution:

| `engine.replay_disposition` | TUI display |
|---|---|
| `deterministic_replay` | Original span displayed; no duplicate trace nodes; replay invisible at UX (correct — deterministic re-read is not a new operation) |
| `checkpoint_resume` | Resumed span displayed with "resume" badge + link to checkpoint span; operator sees "this activity ran again because we resumed from checkpoint" |
| `reconciler_iteration` | Per-iteration span tree; iteration_number badge; ordered list under reconciler operation |
| `wal_consume` | Per-consumption span tree; consumer_group + offset discriminators |

**C11 commits sqlite ledger_entries schema absorption.** Per §4.1.28 of `c11-operator-local` SKILL, the `original_trace_id` + `original_span_id` fields are added to the sqlite `ledger_entries` table; hash-chain integrity verification extends to cover these fields.

### §4.7 C1 consultant contribution — concur-with-rationale

**C1 selects topology-preservation-under-replay invariant.** Per-engine-class replay disposition aligns with C1's per-engine-class topology semantics (per `c1-orchestration-control` SKILL): the engine class determines the topology shape, and the replay disposition is a property of that topology. For `deterministic_replay`: topology graph is invariant under replay (same parent-child structure). For `checkpoint_resume`: topology extends with a child span under the original parent (resumed activity as child).

### §4.8 Sub-scope (i) resolution

**Resolution (load-bearing):**

1. `engine.*` namespace extends from 3 → 4 attributes at CP spec §9.1; new attribute `engine.replay_disposition` with 5-value enum closed-mapped to `engine.class`.
2. For `deterministic_replay`: NO new span emission at replay; original trace_id + span_id recovered from F2 state-ledger entry.
3. For all other dispositions: NEW span emission at replay/resume/iteration; new span carries `engine.replay_disposition` attribute.
4. F2 state-ledger entry shape extends with `original_trace_id` + `original_span_id` fields (C3 Tier 5 absorption).
5. Fail-class + cause_attribution carried durably in F2 state-ledger entry; not re-emitted at replay for `deterministic_replay`.
6. Sqlite `ledger_entries` schema extends per §4.6; hash-chain integrity verification covers new fields.

**ADR-D1 v1.1 → v1.2 amendment scope (sub-scope (i) substrate for Step 2a):**

| ADR-D1 section | Amendment |
|---|---|
| §1.1.1 (engine.* attribute declaration) | Add `engine.replay_disposition` to 3-attribute declaration → 4-attribute declaration |
| §1.1 (engine lifecycle envelope) | Add per-engine-class replay-emission discipline subsection |
| §1.2 (engine-class taxonomy) | Add `engine.replay_disposition` per-class default value column |

---

## §5 Sub-scope (iii) Deliberation — Trace-ingestion dedup composition with F2 idempotency_key

### §5.1 Anchor question (per kickoff §3.1)

Cost-attribution-per-span at D6 §1.5 must avoid double-counting on replay. F2 `idempotency_key` join key (per IS spec §10.2) must compose with D6 ingestion dedup at replay boundary.

### §5.2 C7 primary contribution

**C7 commits the trace-ingestion dedup algorithm at D6 §1.5.** Building on §4 resolution, the dedup algorithm discriminates by `engine.replay_disposition`:

```
function ingest_span(span):
  key = span.idempotency_key  # from F2 state-ledger join per IS spec §10.2
  ledger_entry = F2_state_ledger.lookup_by_key(key)
  
  if ledger_entry exists:
    match span.engine.replay_disposition:
      case "deterministic_replay":
        # Idempotent replay; verify trace_id + span_id match ledger
        assert span.trace_id == ledger_entry.original_trace_id
        assert span.span_id == ledger_entry.original_span_id
        DROP  # No new cost attribution; replay is invisible at D6
      
      case "checkpoint_resume" | "reconciler_iteration" | "wal_consume":
        # Re-emission expected; record as new attempt
        RECORD span as new ingestion
        mark span.is_replay_derived = true
        # Cost attribution counts ONCE per attempt; not aggregated across replays
        # Parent span_id from ledger_entry preserves topology link
      
      case "no_replay":
        ERROR  # Unexpected re-ingestion for non-replay engine class
  else:
    RECORD span as new (first ingestion)
    F2_state_ledger.append(idempotency_key=key, original_trace_id=span.trace_id,
                            original_span_id=span.span_id, ...)
```

**C7 commits cost-attribution invariance.** Per OD spec C-OD-14 cost-attribution-per-span contract: cost-per-replay-cycle accrues ONCE per attempt, NOT aggregated across `deterministic_replay` re-reads. For re-emitting dispositions, cost-per-attempt is the unit.

### §5.3 C3 co-primary contribution — T-perm-2 surface

**C3 commits the idempotency_key composition contract.** F2 `idempotency_key` is the canonical join key (per IS spec C-IS-10 §10.2). The contract surface at trace-ingestion dedup:

| Phase | Action | Owner |
|---|---|---|
| First emission | Span emitted within-turn; OTel SDK records | C7 (within-turn span emission discipline) |
| State-ledger entry creation | F2 ledger appends entry with idempotency_key + trace_id + span_id + engine attrs | C3 (Tier 5 durable storage) |
| Replay invocation | Engine looks up state-ledger entry by idempotency_key | C3 (read seam) |
| Replay span ingestion at D6 | D6 looks up ledger entry; applies dedup per §5.2 | C7 (ingestion-time algorithm) + C3 (ledger lookup) |

**T-perm-2 (C2↔C3 within-turn-vs-durable composition) engaged.** The within-turn span emission (C7's surface, structurally adjacent to C2's prompt structure territory) composes with the across-turn durable F2 state-ledger storage (C3's surface). The composition contract is the `idempotency_key` join. **Status: ENGAGED; reconciled via idempotency_key composition; permanent tension preserved at Layer 3 — see ledger as T-perm-2.**

**C3 commits hash-chain integrity discipline extension.** Per `c3-state-persistence` SKILL reconciliation absorption: hash-chain entry shape extends to include `original_trace_id` + `original_span_id`. Hash-chain construction:

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

C10 owns the hash-chain integrity discipline (per `c10-action-safety` SKILL); C3 owns the storage primitive; C11 owns the sqlite implementation per `c11-operator-local` SKILL §4.1.28. Three-way seam preserved; no Layer-3 promotion required.

### §5.4 C9 consultant contribution — propose refinement

**C9 proposes the retry-attempt dedup-exemption rule.** Dedup at D6 ingestion does NOT collapse retry attempts. Each retry attempt is a DISTINCT cost-attribution unit; the dedup algorithm only collapses `deterministic_replay` re-reads of the SAME attempt, not different attempts of the same operation.

**C9 commits the discriminator.** `retry.attempt_number` discriminates attempts within a parent operation; `engine.replay_disposition` discriminates replay-vs-fresh-execution within an attempt. The two discriminators compose orthogonally:

| `retry.attempt_number` | `engine.replay_disposition` | Dedup outcome |
|---|---|---|
| 1 | `deterministic_replay` | DROP if ledger entry matches; ERROR if mismatch |
| 1 | `checkpoint_resume` | RECORD as new replay-derived span |
| 2 | `deterministic_replay` | DROP if ledger entry matches attempt 2; ERROR otherwise |
| 2 | `checkpoint_resume` | RECORD as new retry attempt 2's replay-derived span |

### §5.5 C5 consultant contribution — propose refinement

**C5 commits the cause_attribution invariance check.** If the same idempotency_key has different `cause_attribution` values across replays under `deterministic_replay`, this signals replay-introduced semantic divergence — which violates the deterministic-replay contract.

**C5 commits dedup-algorithm extension.** Under `deterministic_replay`, the dedup algorithm includes:

```
assert span.cause_attribution == ledger_entry.cause_attribution  # invariance
```

Mismatch ESCALATES to ERROR class (terminal-fail-exit per 5-class taxonomy); signals engine-replay contract violation; cause_attribution = `replay_semantic_divergence`.

### §5.6 C11 consultant contribution — concur-with-rationale

**C11 concurs with the resolution.** Sqlite ledger_entries schema absorption (per §4.6): trace_id + span_id fields added; no further schema modification required for sub-scope (iii). TUI trace browser dedup behavior: replay-derived spans visually distinct from fresh-emission spans (per §4.6 table).

### §5.7 C1 consultant contribution — concur-with-rationale

**C1 commits topology-preservation invariance.** Per `c1-orchestration-control` SKILL decision vocabulary: *"C1 selects topology preservation under replay-dedup composition."* Parent-child span topology is preserved across replay; idempotency_key join does NOT alter topology shape. No re-design required.

### §5.8 Sub-scope (iii) resolution

**Resolution (load-bearing):**

1. D6 §1.5 trace-ingestion dedup algorithm specified per §5.2 pseudocode; discriminates by `engine.replay_disposition`.
2. F2 idempotency_key (per IS spec §10.2) is canonical join key; ledger lookup precedes dedup decision.
3. Cost-attribution-per-span accrues ONCE per attempt for re-emitting dispositions; ZERO additional accrual for `deterministic_replay`.
4. retry.attempt_number + engine.replay_disposition compose orthogonally as dedup discriminators (per §5.4).
5. cause_attribution invariance check at `deterministic_replay` dedup (per §5.5); mismatch → ERROR class.
6. Hash-chain integrity extends to cover trace_id + span_id fields (per §5.3); three-way seam (C3 / C10 / C11) preserved.

**T-perm-2 status: ENGAGED at sub-scope (iii); reconciled via idempotency_key composition contract.** Permanent tension preserved at Layer 3; tunable parameter not re-litigated.

**ADR-D6 v1.1 → v1.2 amendment scope (sub-scope (iii) substrate for Step 2b):**

| ADR-D6 section | Amendment |
|---|---|
| §1.5 (cost-attribution-per-span) | Add dedup-algorithm specification per §5.2 |
| §1.2 (D6 ingestion namespace) | Add `engine.replay_disposition` ingestion path (delegate to C-CP-09 §9.1 per spec §24.1.A) |
| §1.5.x (new subsection) | Specify replay-aware dedup composition with retry.attempt_number orthogonality |
| §1.5.y (new subsection) | Specify cause_attribution invariance check for `deterministic_replay` |

---

## §6 Sub-scope (ii) Deliberation — `retry.attempt` sibling-span discipline

### §6.1 Anchor question (per kickoff §3.1)

Does the retry emit `retry.attempt` event AND a new sibling span per D6 §1.2? Affects retry observability composition with engine-replay boundary.

### §6.2 C9 primary contribution

**C9 commits BOTH-event-AND-span discipline.** The retry emits:

1. `retry.attempt` EVENT on parent span (marks the retry trigger; parent-perspective semantic)
2. NEW SPAN representing the retry-attempt execution (operation-perspective semantic; child of parent operation span)

**C9 commits terminology correction.** The phrase "sibling-span" in ADR-D6 v1.1 §1.2 is a misnomer for "siblings to each other under the same parent operation." Retry attempts are CHILDREN of the parent operation span; the attempts are SIBLINGS TO EACH OTHER at the topology level. The correct terminology is "child span per retry attempt"; the "sibling" framing applies between attempts (e.g., attempt 1 and attempt 2 are siblings to each other under the same parent).

**C9 commits the retry-attempt span schema.** Per `c9-reliability-recovery` SKILL §"What this skill produces" (events catalog):

| Attribute | Source | Purpose |
|---|---|---|
| `parent_span_id` | OTel context | Link to parent operation span |
| `retry.attempt_number` | C9 attempt counter | Integer; 1-indexed |
| `retry.original_span_id` | F2 state-ledger | Link to first attempt span |
| `retry.delay_ms` | C9 backoff calculation | Jittered delay applied before this attempt |
| `retry.cause_attribution` | C5 annotation | Reason for retry (e.g., `network_timeout`, `provider_outage`) |
| `retry.fail_class` | C5 5-class taxonomy | Classification of triggering failure |
| `engine.replay_disposition` | C7 §4 resolution | Composition with replay (per §5.4) |

**C9 commits the parent-span `retry.attempt` event schema:**

| Event field | Purpose |
|---|---|
| `parent.attempt_count` | Total attempts so far for this operation |
| `parent.attempts_remaining` | Remaining budget |
| `parent.next_delay_ms` | Delay before next attempt (if attempt-count < budget) |

### §6.3 C1 co-primary contribution — T-perm-3 surface

**C1 selects topology pattern: child-per-attempt.** Retry attempts are children of the parent operation span; the attempts are siblings to each other in the topology.

**C1 commits sub-agent-boundary composition.** If a retry crosses a sub-agent boundary, the sub-agent's spans are CHILDREN of the retry-attempt-span (NOT of the original parent). Each retry attempt creates its own sub-tree rooted at the retry-attempt span. This preserves per-attempt isolation in trace topology while maintaining per-operation aggregation under the parent.

**C1 selects handoff contract under retry.** Per `c1-orchestration-control` SKILL decision vocabulary: *"C1 specifies handoff contract: per-retry-attempt invocation carries full handoff payload; not collapsed across attempts."* Each retry attempt's child span tree preserves the full handoff topology, supporting per-attempt diagnostic legibility.

**T-perm-3 (C1↔C9 control-flow-vs-reliability) ENGAGED.** Per `c1-orchestration-control` SKILL + `c9-reliability-recovery` SKILL §"Co-primary scan": the C1↔C9 Layer-3 promotion at session 12 produced the tunable parameter `topology_fault_handling` ∈ {`pre-declared`, `pre-declared-with-allowlist`, `runtime-rewrite`} with default `pre-declared-with-allowlist`. F2-12 sub-scope (ii) resolution honors this default — retry topology is pre-declared in the workflow shape with allowlist for engine-class-specific extensions.

**Status: ENGAGED; honored at default; permanent tension preserved at Layer 3 — see ledger as T-perm-3.**

### §6.4 C7 consultant contribution — propose refinement

**C7 commits the canonical span schema authority.** Per `c7-observability` SKILL: *"C9 emits events; C7 owns schema."* The retry-attempt span schema and parent-span retry.attempt event schema specified at §6.2 are absorbed into C7's per-voice runtime signal catalog under the accretion-pattern rule (C7 SKILL §"Accretion discipline"). No re-opening of s10-c7-observability-spec.md required.

**C7 commits emission discipline.** Emit BOTH the event AND the child span. Do NOT collapse to event-only (loses per-attempt operation-level instrumentation; cost-attribution at D6 §1.5 cannot accrue per-attempt cost) or span-only (loses parent-perspective retry-trigger marking; operator cannot scan parent span event timeline to see retry occurred).

### §6.5 C5 consultant contribution — propose refinement

**C5 commits fail-class composition with retry sequence.** Each retry attempt carries:

1. `retry.fail_class` from the validator-fail event (if validator-fail triggered the retry) OR from the cause_attribution annotation (if mechanical failure triggered the retry)
2. `retry.cause_attribution` annotation (per C5 reconciliation: 5-class taxonomy with attribution annotation is the contract surface)

**C5 commits per-attempt classification invariance.** The 5-class taxonomy applies per-attempt; classifications are NOT aggregated across the retry sequence. The retry-exit determination uses the LATEST attempt's classification:

| Latest classification | Retry-exit outcome |
|---|---|
| `transient-retry` AND budget remaining | Continue (next attempt) |
| `transient-retry` AND budget exhausted | C9 retry-budget-exit |
| `Reflexion-recoverable` | Route to Reflexion loop (C5 territory) |
| `HITL-recoverable` | Route to HITL primitive (C11 territory) |
| `permanent-fail-exit` | C5 permanent-fail-exit |
| `terminal-fail-exit` | C5 terminal-fail-exit |

### §6.6 C3 consultant contribution — propose refinement

**C3 commits per-attempt F2 state-ledger entry discipline.** Each retry attempt produces a NEW state-ledger entry. The parent operation has ONE idempotency_key; each retry attempt joins via that key but is a DISTINCT entry with `retry.attempt_number` as discriminator within the key's join set.

**C3 commits hash-chain construction.** Per-attempt entry appended to hash-chain; hash-chain integrity verification covers the attempt sequence.

```
key_join_set = F2_state_ledger.filter_by_key(idempotency_key)
# Returns ordered list of entries: [attempt_1, attempt_2, ..., attempt_N]
# Each entry carries retry.attempt_number, original_trace_id, original_span_id, engine attrs
```

### §6.7 C11 consultant contribution — concur-with-rationale

**C11 concurs with the resolution.** Sqlite ledger schema: per-attempt entry storage absorbs without further schema modification beyond §4.6 + §5.3 additions (retry.attempt_number is already in the per-attempt entry).

**C11 commits TUI trace browser UX for retry sequences:**

| UX element | Behavior |
|---|---|
| Parent operation span | Displayed with `retry.attempt_count` badge if attempts > 1 |
| Retry attempt spans | Visually grouped under parent; ordered by `retry.attempt_number`; collapsible |
| Per-attempt span tree | Expandable; preserves full handoff topology per C1's commitment |
| retry.attempt event timeline | Displayed in parent span's event stream; per-attempt timestamps |

### §6.8 Sub-scope (ii) resolution

**Resolution (load-bearing):**

1. Retry emits BOTH `retry.attempt` event on parent span AND new child span representing the retry-attempt execution.
2. Terminology: "sibling-span" in D6 v1.1 §1.2 is corrected to "child-per-attempt"; attempts are siblings to each other under the same parent operation.
3. Retry-attempt span schema per §6.2 (7 attributes); parent-span `retry.attempt` event schema per §6.2 (3 event fields).
4. Sub-agent boundary composition: sub-agent spans are children of the retry-attempt span, not of the original parent (per §6.3).
5. `topology_fault_handling` honored at default `pre-declared-with-allowlist` (T-perm-3 Layer-3 default).
6. Fail-class + cause_attribution per-attempt (per §6.5); retry-exit determined by latest attempt's classification.
7. F2 state-ledger: one entry per attempt; idempotency_key + retry.attempt_number as join discriminator; hash-chain construction per §6.6.

**T-perm-3 status: ENGAGED; honored at default `pre-declared-with-allowlist`; permanent tension preserved at Layer 3.**

**ADR-D6 v1.1 → v1.2 amendment scope (sub-scope (ii) substrate for Step 2b):**

| ADR-D6 section | Amendment |
|---|---|
| §1.2 (D6 ingestion namespace) | Replace "sibling-span" terminology with "child-per-attempt"; add full retry-attempt span schema (7 attributes per §6.2) |
| §1.2 (parent.retry.attempt event) | Add parent-span event schema (3 event fields per §6.2) |
| §1.2.x (new subsection) | Specify sub-agent boundary composition per §6.3 |
| §1.5.z (new subsection) | Per-attempt cost-attribution discipline; cost accrues per attempt; not aggregated |

---

## §7 TENSION block

Per `council-orchestrator` SKILL §"Surface tensions" + kickoff §4.3 permanent-tension-engagement table.

### §7.1 TENSION-1 — T-perm-3 (C1 ↔ C9) engaged at sub-scope (ii)

| Field | Value |
|---|---|
| Parties | C1 (Orchestration & Control) ↔ C9 (Reliability & Recovery) |
| Issue | retry.attempt parent-child topology vs sibling-at-topology framing; sub-agent boundary composition under retry |
| C1 position | retry attempts are children of parent operation; sub-agent spans are children of the retry-attempt-span; topology is pre-declared with allowlist |
| C9 position | retry mechanics emit per-attempt span; "sibling-span" v1.1 terminology corrected to "child-per-attempt"; topology composition deferred to C1 |
| Stakes | Span hierarchy under retry composition; legibility of retry sequences in trace UX; per-attempt isolation for diagnostic purposes; topology composition with sub-agent boundaries |
| Resolution | Both voices CONCUR on child-per-attempt topology; "sibling-span" terminology corrected; `topology_fault_handling` honored at default `pre-declared-with-allowlist` |
| Status | **PROMOTED to Layer 3 (permanent tension — see ledger as T-perm-3); honored at default tunable value; not re-litigated** |

### §7.2 TENSION-2 — T-perm-2 (C2 ↔ C3) engaged at sub-scope (iii)

| Field | Value |
|---|---|
| Parties | C2 (Context Engineering & Attention Budget) ↔ C3 (State, Memory & Persistence) — C2 not convened; C7 stands in at the within-turn-emission party position |
| Issue | Within-turn span emission (C7 surface, structurally adjacent to C2's within-turn territory) ↔ across-turn durable F2 state-ledger storage (C3 territory) |
| Within-turn position (C7) | Spans emit at within-turn instrumentation point; OTel SDK is the canonical emission substrate; deterministic_replay does NOT re-emit |
| Durable position (C3) | F2 state-ledger entry is authoritative durable record; idempotency_key + trace_id + span_id durably stored; replay recovers from ledger |
| Stakes | Consistency of trace data across within-turn instrumentation and across-turn replay-recovery; whether the trace-store mirrors the ledger or vice versa |
| Resolution | idempotency_key composition is the contract surface; within-turn emission populates ledger; replay recovers from ledger; no contention on authority |
| Status | **ENGAGED at sub-scope (iii); reconciled via idempotency_key composition; permanent tension preserved at Layer 3 (T-perm-2) — see ledger; not re-litigated** |

### §7.3 T-perm-1 status

| Field | Value |
|---|---|
| Engagement | NOT ACTIVELY ENGAGED at F2-12 scope |
| Rationale | Per kickoff §4.3, T-perm-1 (C4↔C10) is conditionally engaged per OD-F212-3 sub-scope (i) scoping. Sub-scope (i) resolution at §4 does not touch tool-call replay disposition substantively; tool calls within a replayed workflow inherit the parent operation's `engine.replay_disposition` without C4↔C10 territory re-litigation. |
| Status | Not engaged at this convening |

---

## §8 Cascade Step 2 substrate output

### §8.1 ADR-D1 v1.1 → v1.2 amendment specification (Step 2a)

**Amendment scope:** Sub-scope (i) span re-emission semantics.

| ADR-D1 section | Amendment shape | Substrate source |
|---|---|---|
| §0 amendment trace | Add F2-12 sub-scope (i) closure record; cite this council deliberation output | New section per ADR-revision protocol |
| §1.1.1 (engine.* attribute declaration) | 3-attribute → 4-attribute declaration; add `engine.replay_disposition` with 5-value enum | §4.2 + §4.8 |
| §1.1 (engine lifecycle envelope) | Add per-engine-class replay-emission discipline subsection | §4.2 |
| §1.2 (engine-class taxonomy) | Add `engine.replay_disposition` per-class default value column to 5-class table | §4.2 table |
| Status field | `Status: Proposed` until ADD v1.3 consolidation absorbs | Per kickoff §7.2 |

**Preserve verbatim:** All ADR-D1 v1.1 substantive content not affected by F2-12 sub-scope (i) — engine-class taxonomy values, capability-floor preservation invariant, per-deployment-surface candidate mapping, F3 capability-floor composition.

### §8.2 ADR-D6 v1.1 → v1.2 amendment specification (Step 2b)

**Amendment scope:** Sub-scopes (ii) `retry.attempt` sibling-span discipline + (iii) trace-ingestion dedup composition.

| ADR-D6 section | Amendment shape | Substrate source |
|---|---|---|
| §0 amendment trace | Add F2-12 sub-scope (ii) + (iii) closure record; cite this council deliberation output | New section per ADR-revision protocol |
| §1.2 (D6 ingestion namespace — retry.attempt) | Replace "sibling-span" terminology with "child-per-attempt"; specify 7-attribute retry-attempt span schema; specify 3-event-field parent retry.attempt event schema | §6.2 + §6.8 |
| §1.2 (D6 ingestion namespace — engine.replay_disposition) | Add ingestion path for `engine.replay_disposition`; delegate to C-CP-09 §9.1 per spec §24.1.A | §4.8 |
| §1.2.x (new subsection — sub-agent boundary under retry) | Specify sub-agent boundary composition: sub-agent spans are children of retry-attempt-span | §6.3 + §6.8 |
| §1.5 (cost-attribution-per-span) | Add dedup-algorithm specification per §5.2 pseudocode; specify per-replay-disposition behavior | §5.2 + §5.8 |
| §1.5.x (new subsection — replay-aware dedup with retry orthogonality) | Specify retry.attempt_number + engine.replay_disposition orthogonal composition | §5.4 + §5.8 |
| §1.5.y (new subsection — cause_attribution invariance check) | Specify invariance check at `deterministic_replay` dedup; specify ERROR escalation on mismatch | §5.5 + §5.8 |
| §1.5.z (new subsection — per-attempt cost-attribution) | Specify cost accrues per attempt; not aggregated across attempts | §6.8 |
| Status field | `Status: Proposed` until ADD v1.3 consolidation absorbs | Per kickoff §7.2 |

**Preserve verbatim:** All ADR-D6 v1.1 substantive content not affected by F2-12 sub-scopes (ii) + (iii) — unified span schema baseline, 12 additive namespace declarations, OTel GenAI semconv 1.41.0 inheritance, observability cross-section composition.

### §8.3 Downstream cascade substrate (forward routing)

| Step | Artifact | Substrate consumed |
|---|---|---|
| Step 3 — ADD v1.3 consolidation | `Architectural_Design_Document_v1_3.md` | ADR-D1 v1.2 + ADR-D6 v1.2 + this council output; §6.3.1 active path updated to "F2-12 CLOSED at v1.3" |
| Step 4 — PRD v1.1 revision pass | `PRD_v1_1.md` | ADD v1.3 + ADR-D1 v1.2 + ADR-D6 v1.2; [CF-1] carry-forward removed; R-CP-04 + R-CP-07 + R-OD-* requirements amended |
| Step 5a — CP spec v1.3 revision pass | `Spec_Control_Plane_v1_3.md` | C-CP-08 §8.4 closure declaration; C-CP-09 §9.1 4-attribute engine.* schema; §5.4 retry.attempt sampling discipline amended |
| Step 5b — OD spec v1.3 revision pass | `Spec_Operational_Discipline_v1_3.md` | C-OD-14 cost-attribution-per-span contract amended; trace-ingestion dedup composition added; cause_attribution invariance specified |
| Step 6a — CP plan v2.2 revision pass | `Implementation_Plan_Control_Plane_v2_2.md` | U-CP-20 acceptance #5 closure declaration; U-CP-21 engine.* namespace updated to 4-attribute schema; U-CP-55 §24.4 export manifest updated |
| Step 6b — OD plan v2.2 revision pass | `Implementation_Plan_Operational_Discipline_v2_2.md` | U-OD-20 closure_path closure status updated; U-OD-14 cost-attribution-per-span unit updated |

---

## §9 Audit pass (council-orchestrator SKILL §"Audit your own response")

### §9.1 Convening Block field completeness

| Field | Status |
|---|---|
| Voices convened | ✅ §2.1 (6 voices listed with roles + rationale) |
| Question type classification | ✅ §2.2 (per-sub-scope question type) |
| Routing rationale per voice | ✅ §2.4 |
| Voices considered, not convened | ✅ §2.3 (stated "None" with consulted-by-reference notation for C2/C4/C6/C8/C10) |
| Pointer to CCR | ✅ §2.5 |

### §9.2 CCR completeness

| Concern | Touched | Pre-check note present |
|---|---|---|
| Security | ✅ | ✅ (C10 hash-chain integrity engagement) |
| Blast radius | — | ✅ (Not touched stated) |
| Observability | ✅ | ✅ (C7 anchors) |
| Cost | ✅ | ✅ (per-attempt cost-attribution; per-replay-disposition cost behavior) |
| Reliability | ✅ | ✅ (retry.attempt mechanics + composition) |
| Eval-ability | ✅ | ✅ (C8 holdout primitives surfaced) |
| HITL / local-first | ✅ | ✅ (sqlite ledger schema + TUI trace browser) |

### §9.3 Consultant substance

| Voice | Contribution type | Substance present |
|---|---|---|
| C9 at (i) | propose-refinement | ✅ (composition with retry classification) |
| C3 at (i) | propose-refinement | ✅ (F2 state-ledger schema extension) |
| C5 at (i) | propose-refinement | ✅ (fail-class durability discipline) |
| C11 at (i) | concur-with-rationale + UX implication | ✅ (TUI display per-disposition; sqlite absorption) |
| C1 at (i) | concur-with-rationale | ✅ (topology-preservation-under-replay invariant) |
| C9 at (iii) | propose-refinement | ✅ (retry-attempt dedup-exemption rule) |
| C5 at (iii) | propose-refinement | ✅ (cause_attribution invariance check) |
| C11 at (iii) | concur-with-rationale | ✅ (sqlite schema absorption confirmation) |
| C1 at (iii) | concur-with-rationale | ✅ (topology-preservation invariance) |
| C7 at (ii) | propose-refinement | ✅ (schema authority + emission discipline) |
| C5 at (ii) | propose-refinement | ✅ (fail-class composition with retry sequence) |
| C3 at (ii) | propose-refinement | ✅ (per-attempt F2 state-ledger entry discipline) |
| C11 at (ii) | concur-with-rationale | ✅ (TUI retry sequence UX) |

No "no comment" or formulaic concur-without-rationale present.

### §9.4 TENSION block hygiene

| Tension | Engaged | Surfaced | Layer-3 status |
|---|---|---|---|
| T-perm-3 (C1↔C9) | ✅ | ✅ §7.1 | Honored at default; not re-litigated |
| T-perm-2 (C2↔C3) | ✅ (C7 stands in for C2) | ✅ §7.2 | Reconciled via idempotency_key; not re-litigated |
| T-perm-1 (C4↔C10) | — (not actively engaged) | ✅ §7.3 (status declared) | Not engaged |

### §9.5 Single-voice anti-pattern check

Primary collapse: NOT present. C7 anchors at (i) + (iii); C9 anchors at (ii); consultants produce substantive contributions on each sub-scope (4–5 contributions per sub-scope). The deliberation reads as multi-voice; no degenerate single-voice pattern.

### §9.6 Workflow v1.7 §7 fidelity-grammar discipline

| Discipline | Application |
|---|---|
| Use-latest-version body-citation | All ADR/spec citations resolve to v1.x post-Path-δ canonical state; no v1.6-anchored references |
| Pattern P2 (verbatim-claim-contradicted) prevention | All "per spec §X verbatim" claims verify against accessible substrate; no fabricated verbatim claims |
| Pattern P1 (cross-artifact-name-drift) prevention | engine.* attribute names canonical: `engine.class`, `engine.resumption_kind`, `engine.tech`, `engine.replay_disposition` (the new 4th attribute); used consistently across §4/§5/§6/§8 |
| Sub-scope scope-creep prevention | Only F2-12 sub-scopes (i)/(ii)/(iii) addressed; no out-of-scope items folded in |
| Cascade-step dependency-ordering preservation | Step 1 output produces Step 2 substrate only; no Step 3+ authoring at this filing |

---

## §10 Filing footer

| Field | Value |
|---|---|
| Artifact | `F2-12_Council_Deliberation_Output.md` |
| Status | Filed — F2-12 cascade Step 1 complete |
| Filing destination | `/mnt/user-data/outputs/F2-12_Council_Deliberation_Output.md` |
| Successor (Step 2a) | `ADR-D1_v1_2.md` per §8.1 amendment specification |
| Successor (Step 2b) | `ADR-D6_v1_2.md` per §8.2 amendment specification |
| Operator confirmation gate | Step 1 closure; OD-F212-4.A segment boundary; operator confirms before Step 2 authoring entry |
| Workflow discipline | Workflow v1.7 §7 fidelity-grammar in force; per-cascade-step authoring agent activated per kickoff §3.3 |
| Date | 2026-05-14 |

*Filed at F2-12 cascade Step 1 close. Council deliberation complete; per-sub-scope resolutions recorded; per-tension status declared; Step 2 ADR-D1 v1.2 + ADR-D6 v1.2 substrate provided per §8. Single combined session continues at Step 2 on operator confirmation.*
