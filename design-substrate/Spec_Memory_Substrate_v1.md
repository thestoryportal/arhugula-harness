# Specification - Memory Substrate v1

## Status

Proposed.

Date: 2026-07-01

Authority chain: ADR-F2, ADR-D3, PRD v1.2 R-MEM family, and Memory Substrate Design v1.

This specification introduces the `C-MEM-*` contract family for the full provider-neutral memory layer. It is additive to the existing Information Substrate, Action Surface, Control Plane, Operational Discipline, and Runtime specifications.

## C-MEM-01 - Memory plane boundary

### Contract

The memory substrate is a provider-neutral harness plane with five axis responsibilities:

| Axis | Responsibility |
|---|---|
| Information substrate | Typed records, path registry, canonical artifact IO, deterministic serialization, derived index metadata, memory ledger entry shape. |
| Action surface | Memory access mode vocabulary, provider-neutral memory tool contracts, memory telemetry namespace extension. |
| Control plane | Memory policy resolution, provider/CLI access-mode selection, retrieval budget selection. |
| Operational discipline | Audit, redaction, retention, ledger verification, review queue policy. |
| Runtime | Capture, retrieval invocation, provider adapters, CLI profile loading, packet injection, tool execution. |

### Invariants

- Provider-owned memory is never canonical.
- Derived indexes are never canonical.
- Native provider memory, standard tools, and prompt packet fallback operate against the same canonical store.
- Memory promotion and memory injection are distinct policy decisions.
- Atomic implementation sequencing is allowed; product completion requires the full contract family.

## C-MEM-02 - Canonical path registry

### Contract

The canonical memory root is `.harness/memory/` unless a deployment-surface binding explicitly maps it elsewhere. Under that root, the following paths are stable:

| Path | Role |
|---|---|
| `manifest.json` | Memory store manifest, schema version, project/workflow identity, store id. |
| `policy.json` | Default memory policy for capture, promotion, retrieval, injection, redaction, retention. |
| `episodic/runs/<run_id>/run.json` | One run record. |
| `episodic/runs/<run_id>/turns.jsonl` | Append-only turn records. |
| `episodic/runs/<run_id>/tool_events.jsonl` | Append-only tool summaries. |
| `episodic/runs/<run_id>/compactions.jsonl` | Append-only compaction events. |
| `episodic/runs/<run_id>/summaries/` | Human-readable or machine summaries, source-linked. |
| `semantic/facts/` | Semantic fact records. |
| `semantic/preferences/` | Preference records. |
| `semantic/decisions/` | Decision records. |
| `semantic/conventions/` | Project convention records. |
| `semantic/failures/` | Failure learning records. |
| `semantic/research/` | Research state records. |
| `semantic/index.jsonl` | Derived semantic index metadata. Rebuildable. |
| `procedural/snapshots/` | Procedural snapshot records. |
| `procedural/promoted/` | Policy-approved procedural memory projections. |
| `durable/memory_ops.jsonl` | Canonical append-only global memory operation ledger. |
| `durable/promotion_decisions.jsonl` | Rebuildable review projection keyed by canonical memory operation `action_id`. |
| `durable/injection_decisions.jsonl` | Rebuildable review projection keyed by canonical memory operation `action_id`. |
| `durable/retrieval_events.jsonl` | Rebuildable review projection keyed by canonical memory operation `action_id`. |

### Invariants

- Canonical writes go to canonical paths before derived indexes update.
- Deployment-surface remapping must preserve the same logical path classes.
- A path registry implementation must reject traversal outside the memory root.
- Files under `semantic/index.jsonl` or equivalent derived caches must be rebuildable from canonical records.
- `durable/memory_ops.jsonl` is the only authoritative memory operation ledger and provides the global hash-chain order. Projection files are non-authoritative filtered views that may be rebuilt from `memory_ops.jsonl`.

## C-MEM-03 - Common record identity

### Contract

Every memory record has a common identity envelope:

```text
MemoryRecordEnvelope {
  memory_id: string
  schema_version: string
  tier: working | episodic | semantic | procedural | durable
  kind: string
  created_at: timestamp
  updated_at: timestamp | null
  source_refs: list<SourceRef>
  scope: MemoryScope
  content_hash: sha256
  supersedes: list<memory_id>
  superseded_by: list<memory_id>
  redaction_state: active | redacted | tombstoned
}

SourceRef {
  ref_type: run | turn | tool_event | compaction | file | git_commit | operator | provider_response | external
  ref: string
  content_hash: sha256 | null
}

MemoryScope {
  project: string | null
  workflow: string | null
  workload_class: string | null
  provider_family: string | null
  cli_profile: string | null
  tenant: string | null
  visibility: private | project | workflow | tenant | public
}
```

### Invariants

- `content_hash` is computed over canonical serialized content excluding derived indexes.
- Supersession does not delete the prior record.
- Redaction and tombstone states are durable memory operations.

## C-MEM-04 - Episodic records

### Contract

Episodic memory includes `EpisodicRunRecord`, `EpisodicTurnRecord`, `ToolEventRecord`, and `CompactionEventRecord`.

```text
EpisodicRunRecord {
  envelope: MemoryRecordEnvelope
  run_id: string
  workflow_id: string | null
  thread_id: string | null
  engine_class: event-sourced-replay | save-point-checkpoint | pure-pattern-no-engine | reconciler-loop | WAL-segment
  cli_profile: string
  provider_route: list<ProviderBinding>
  started_at: timestamp
  closed_at: timestamp | null
  close_status: completed | failed | cancelled | paused | unknown
}

EpisodicTurnRecord {
  envelope: MemoryRecordEnvelope
  run_id: string
  turn_id: string
  step_id: string | null
  prompt_summary: string
  response_summary: string
  summary_source: harness_rule | model_generated | operator | imported
  summary_model: string | null
  summary_hash: sha256
  tool_event_refs: list<memory_id>
  failure_observations: list<string>
  promotion_candidates: list<PromotionCandidate>
  token_usage: TokenUsage | null
}
```

### Invariants

- Episodic capture is automatic when memory is enabled.
- Episodic records may summarize sensitive content by policy, but the capture decision remains durable.
- Model-generated summaries are captured as stored artifacts with model and hash provenance; retrieval/ranking must not regenerate summaries as part of selection.
- Episodic records are run-scoped unless explicitly promoted.

## C-MEM-05 - Semantic records

### Contract

Semantic memory includes fact, decision, convention, failure learning, research, and preference records.

```text
SemanticRecord {
  envelope: MemoryRecordEnvelope
  semantic_kind: fact | decision | convention | failure_learning | research | preference
  statement: string
  rationale: string | null
  evidence: list<SourceRef>
  confidence: low | medium | high | verified
  status: proposed | active | denied | superseded | expired
  ttl: duration | null
  expires_at: timestamp | null
  injection_policy: never | retrieval_only | prompt_packet_allowed | tool_allowed | native_allowed
  tags: list<string>
}
```

### Invariants

- Semantic records are cross-run only after promotion policy approves or queues them.
- Evidence is mandatory for active semantic records.
- Expired, denied, superseded, redacted, or tombstoned records are excluded from injection.

## C-MEM-06 - Preference records

### Contract

Preferences are first-class semantic records with additional fields:

```text
PreferenceRecord extends SemanticRecord {
  preference_subject: operator | project | workflow | code_style | tool_use | provider | review | other
  preference_strength: weak | normal | strong | mandatory
  source_authority: operator_direct | inferred_from_repetition | imported | policy
  confirmation_required: bool
}
```

### Invariants

- `source_authority=operator_direct` may be promoted without inference if policy allows.
- `source_authority=inferred_from_repetition` must carry at least two source refs or remain proposed.
- Mandatory preferences must be scoped and source-linked.
- A preference can be stored without being injectable; injection is governed by `injection_policy`.

## C-MEM-07 - Procedural snapshots

### Contract

Procedural memory snapshots capture the workflow instructions active for a run or promotion:

```text
ProceduralSnapshotRecord {
  envelope: MemoryRecordEnvelope
  snapshot_id: string
  workflow_id: string | null
  cli_profile: string
  prompt_refs: list<ContentRef>
  skill_refs: list<ContentRef>
  routing_manifest_ref: ContentRef | null
  instruction_file_refs: list<ContentRef>
  memory_policy_ref: ContentRef
}

ContentRef {
  path_or_uri: string
  content_hash: sha256
  kind: prompt | skill | routing_manifest | instruction_file | memory_policy | other
}
```

### Invariants

- Every memory-affecting run references a procedural snapshot.
- Snapshot refs are content-addressed.
- CLI-specific instruction files may participate only through the active CLI profile policy.

## C-MEM-08 - Memory operation ledger

### Contract

Every memory operation writes a durable ledger entry. The memory ledger shape is an additive D-derivative over the existing C-IS-05/C-IS-06 state-ledger discipline: it preserves `action_id`, `idempotency_key`, `actor`, `response_hash`, `timestamp`, and `prior_event_hash`, then adds memory-specific fields as sidecar payload.

```text
MemoryOperationEntry extends StateLedgerEntry {
  operation_kind: capture | retrieve | inject | promote | propose_promotion | deny_promotion | redact | tombstone | delete_request | native_adapter_call | standard_tool_call | compaction_decision
  operation_projection: none | promotion_decisions | injection_decisions | retrieval_events
  run_id: string | null
  step_id: string | null
  provider: string | null
  model: string | null
  cli_profile: string | null
  engine_class: event-sourced-replay | save-point-checkpoint | pure-pattern-no-engine | reconciler-loop | WAL-segment | null
  memory_refs: list<memory_id>
  policy_ref: string | null
  procedural_snapshot_ref: string | null
}
```

Projection mapping:

| Operation kind | Authoritative ledger | Projection |
|---|---|---|
| `capture` | `durable/memory_ops.jsonl` | none |
| `retrieve` | `durable/memory_ops.jsonl` | `durable/retrieval_events.jsonl` |
| `inject` | `durable/memory_ops.jsonl` | `durable/injection_decisions.jsonl` |
| `promote`, `propose_promotion`, `deny_promotion` | `durable/memory_ops.jsonl` | `durable/promotion_decisions.jsonl` |
| `redact`, `tombstone`, `delete_request` | `durable/memory_ops.jsonl` | none |
| `native_adapter_call`, `standard_tool_call`, `compaction_decision` | `durable/memory_ops.jsonl` | none |

### Invariants

- Ledger entries are append-only.
- `idempotency_key` is stable for retry of the same operation.
- `prior_event_hash` chains entries within `durable/memory_ops.jsonl` using the C-IS hash-chain construction.
- `durable/memory_ops.jsonl` has a serialization point for appends; concurrent writers must not observe the same prior hash and fork the global stream.
- Projection files do not define independent causality; audit reconstruction follows the canonical memory operation ledger order.
- Deletion and redaction are represented as ledgered operations; prior records are not silently rewritten.

## C-MEM-09 - Memory policy

### Contract

Memory policy resolves six decisions:

1. Capture: whether to capture an event and at what fidelity.
2. Promotion: whether to discard, keep episodic, propose, or promote.
3. Retrieval: which scopes and record kinds are eligible.
4. Injection: which packet/tool/native surfaces may expose records.
5. Retention: expiry, pruning, and tombstone behavior.
6. Redaction: sensitive content handling and review.

Policy decision values:

```text
CaptureDecision = deny | summarize_only | capture_full | capture_redacted
PromotionDecision = discard | keep_episodic | propose_semantic | promote_semantic | propose_procedural | promote_procedural
AccessDecision = deny | retrieval_only | prompt_packet | standard_tools | native_provider
ReviewMode = automatic | operator_required | forbidden
```

### Invariants

- If policy resolution fails, capture may fall back to durable minimal evidence, but promotion and injection must deny.
- Injection cannot be broader than the record's scope.
- Native provider access cannot bypass policy.

## C-MEM-10 - Promotion pipeline

### Contract

Promotion transforms episodic candidates into semantic or procedural records.

```text
PromotionCandidate {
  candidate_id: string
  source_refs: list<SourceRef>
  proposed_kind: fact | decision | convention | failure_learning | research | preference | procedural_update
  statement: string
  confidence: low | medium | high
  suggested_scope: MemoryScope
  risk_flags: list<string>
}
```

### Pipeline

1. Candidate extraction from turn, tool, failure, compaction, or operator events.
2. Policy resolution.
3. Optional operator review.
4. Canonical semantic/procedural write.
5. Durable promotion decision ledger entry.
6. Derived index update.

### Invariants

- Compaction candidates must receive a durable disposition before compaction completes.
- Promotion cannot create an active semantic record without evidence.
- Promotion denial is also ledgered.

## C-MEM-11 - Retrieval and ranking

### Contract

Retrieval accepts:

```text
MemoryRetrievalRequest {
  run_id: string
  workflow_id: string | null
  workload_class: string | null
  cli_profile: string
  provider: string
  model: string
  query_summary: string
  scope: MemoryScope
  token_budget: int
  allowed_kinds: list<string>
}
```

Retrieval returns:

```text
MemoryRetrievalResult {
  request_hash: sha256
  selected_refs: list<memory_id>
  excluded_refs: list<ExcludedMemoryRef>
  packet_hash: sha256
  ranking_trace: list<RankingTraceEntry>
}
```

Ranking factors:

- Scope match.
- Recency.
- Confidence.
- Source authority.
- Explicit pinning.
- Failure-risk relevance.
- Workflow and CLI profile match.
- Supersession, expiry, redaction, and denial filters.

### Invariants

- Fixed store, fixed policy, fixed request, and fixed index version must produce a stable result.
- Retrieval operates over persisted records, persisted summaries, and derived indexes; any LLM summarization occurs before retrieval as ledgered capture or promotion work.
- Excluded refs must carry a reason when they were considered but denied.
- Retrieval writes a durable retrieval event.

## C-MEM-12 - Memory packet assembly

### Contract

A memory packet is a bounded, source-linked representation of selected records:

```text
MemoryPacket {
  packet_id: string
  packet_hash: sha256
  token_budget: int
  access_mode: native_provider_memory | standard_memory_tools | prompt_extension_packet | no_memory_access
  sections: list<MemoryPacketSection>
  selected_refs: list<memory_id>
  policy_ref: string
}
```

Stable section order:

1. Active operator/project preferences.
2. Current project conventions.
3. Relevant prior decisions.
4. Failure learnings and hazards.
5. Research or domain facts.
6. Procedural notes.

### Invariants

- Packet content must cite memory refs.
- Prompt-extension packets are read-only.
- Packet assembly writes or references an injection decision before provider dispatch when injection is used.
- Packet text must not include redacted or denied records.

## C-MEM-13 - Provider memory access modes

### Contract

Provider memory access mode is selected from:

```text
MemoryAccessMode =
  native_provider_memory |
  standard_memory_tools |
  prompt_extension_packet |
  no_memory_access
```

Selection inputs:

- Provider capability reflection.
- Model binding.
- Runtime provider route: enabled provider order, model family, fallback-chain primary, and, when the selected provider is an external CLI route, external CLI provider kind, command boundary, auth-check result, and optional/degradation state.
- CLI profile.
- Workflow policy.
- Step policy.
- Token budget.
- Record scope.

### Invariants

- Anthropic native Memory is an adapter, not canonical storage.
- Tool-capable non-Anthropic providers may use standard memory tools.
- Providers without usable tool support may receive prompt-extension packets.
- External CLI provider routing remains the provider-construction authority; memory access mode is selected after the route is known.
- Local CLI OAuth/session tokens are never memory records and are never read by the memory layer.
- `no_memory_access` is a valid policy outcome and must be ledgered when memory was requested.

## Memory threat model

### Threats

The memory substrate treats model-authored and external CLI-authored memory as untrusted until policy promotes it. The threat model covers:

- Cross-run prompt-injection persistence through promoted semantic/procedural memory.
- Cross-scope or cross-tenant retrieval leakage.
- Model-proposed preferences masquerading as operator instruction.
- External CLI memory import poisoning.
- Provider-side prompt cache retention after harness-side redaction.

### Invariants

- Model-authored notes are episodic by default and cannot become injectable semantic memory without policy and evidence.
- Operator-direct preferences are distinguishable from inferred or model-proposed preferences.
- Retrieval and injection enforce project, workflow, tenant, provider-family, CLI-profile, and visibility scope before ranking.
- Redaction can prevent future harness retrieval/injection, but cannot revoke content already sent to an external provider or provider prompt cache; that limitation must be ledger-visible when relevant.
- Redaction can prevent future harness retrieval/injection, but cannot erase committed git history. If redacted content entered git history, the redaction event records that residual persistence and any operator-managed history rewrite remains outside the memory layer.

## C-MEM-14 - Provider-neutral memory tools

### Contract

When `standard_memory_tools` is selected, the harness exposes provider-neutral tools:

| Tool | Purpose |
|---|---|
| `memory.search` | Search eligible records and return source-linked summaries. |
| `memory.read` | Read one allowed memory record or packet section by ref. |
| `memory.write_note` | Write an episodic note under policy. |
| `memory.propose_promotion` | Submit a promotion candidate for policy/review. |
| `memory.request_redaction` | Submit a redaction request. |

### Invariants

- Tools are policy-enforced at every call.
- Tools cannot bypass scope, redaction, retention, or injection policy.
- Write-like tools append durable memory operation entries.
- Tool output must include stable refs, not untracked memory prose.

## C-MEM-15 - Native provider memory adapters

### Contract

Native provider memory adapters translate provider-native operations into canonical memory operations.

For Anthropic Memory:

- `/memories` path discipline remains enforced.
- Native reads map to canonical store reads or derived packet views.
- Native writes map to policy-checked episodic or semantic operations.
- Native mutations append durable memory operation entries.

### Invariants

- Native adapter operations cannot write outside the canonical memory root.
- Native adapter path or content errors are observable.
- Native adapter writes cannot silently promote semantic memory unless policy allows.

## C-MEM-16 - CLI profiles

### Contract

CLI profile values:

```text
CliProfileKind = generic | claude_code | codex | antigravity | gemini_legacy | custom
```

```text
CliProfile {
  profile_id: string
  kind: CliProfileKind
  provider_name: string | null
  external_cli_kind: string | null
  command_name: string | null
  instruction_sources: list<CliInstructionSource>
  external_memory_sources: list<CliMemorySource>
  capability_flags: list<string>
  import_policy: deny | read_only | ledgered_import | bidirectional_sync
}
```

### Invariants

- `generic` must work without CLI-specific assumptions.
- `claude_code` may read Claude-specific instruction/progress conventions only by policy.
- `codex` may read AGENTS-style and Codex-local memory only by policy.
- `claude_code`, `codex`, `antigravity`, `gemini_legacy`, and `custom` profiles bind to existing external CLI provider identities where those providers are active.
- CLI profile loading must not define an independent provider order; it consumes the runtime route already selected by provider materialization and fallback-chain policy.
- External CLI memory stores are not silently modified.
- CLI profile identity is recorded in episodic and durable records.

## C-MEM-17 - Engine-class durability

### Contract

Memory operations bind to engine class:

| Engine class | Contract |
|---|---|
| `event-sourced-replay` | Memory operations occur inside activities; replay uses deterministic snapshots or monotonic versions. |
| `save-point-checkpoint` | Checkpoint state includes memory store version and packet hash. |
| `pure-pattern-no-engine` | Memory operations append state-ledger entries with idempotency keys. |
| `reconciler-loop` | Memory state binds to CR status, Memory CRD, or mounted canonical store with observed version. |
| `WAL-segment` | Restart rebuilds or prewarms memory from WAL plus canonical ledgers. |

### Invariants

- Replay must not re-run non-deterministic retrieval without a recorded store version or packet hash.
- Pending writes must not become visible as active semantic memory until their commit boundary.
- Engine binding is recorded in `MemoryOperationEntry`.

## C-MEM-18 - Redaction, tombstone, and retention

### Contract

Redaction and deletion are durable state transitions:

```text
MemoryRedactionEvent {
  event_id: string
  target_memory_id: string
  redaction_kind: content_redaction | scope_restriction | tombstone | retention_expiry
  reason: string
  actor: harness | operator | policy
  timestamp: timestamp
  replacement_summary: string | null
}
```

### Invariants

- Redacted records are excluded from packets and tools unless policy explicitly allows a replacement summary.
- Tombstoned records remain ledger-visible.
- Retention expiry writes an event before derived indexes drop the record.
- Content-bearing files may be physically redacted or compacted only through a ledgered redaction/retention operation that preserves the target memory id, old content hash, new content hash or tombstone hash, actor, reason, and timestamp.
- Append-only ledger history is not rewritten by redaction; retrieval eligibility is determined by the latest redaction/tombstone state.
- Git history persistence is ledgered when applicable; the memory layer does not silently rewrite git history.

## C-MEM-19 - Observability

### Contract

Memory telemetry covers:

- Capture.
- Retrieval.
- Ranking.
- Packet assembly.
- Injection.
- Promotion.
- Native adapter call.
- Standard memory tool call.
- Redaction and tombstone.
- Policy denial.

Required attributes:

```text
memory.tier
memory.operation.name
memory.access_mode
memory.provider
memory.model
memory.cli_profile
memory.policy.decision
memory.packet_hash
memory.record_count
memory.failure_class
```

### Invariants

- Existing `memory.*` telemetry remains compatible with the current six-attribute memory namespace; new attributes are additive and must not rename `memory.operation.kind`, `memory.path`, `memory.backend`, `memory.bytes_read`, `memory.bytes_written`, or `memory.context_editing_active`.
- Failure telemetry must distinguish policy denial, path violation, IO failure, serialization failure, provider adapter failure, and retrieval empty-result.

## C-MEM-20 - Verification contract

### Contract

The full layer must be verified by unit, integration, and cross-provider behavior checks.

Required verification:

- Schema validation for every record type.
- Path registry traversal rejection.
- Append-only ledger and hash-chain validation.
- Concurrent writer tests proving ledger streams do not fork under parallel append.
- Promotion policy tests, including preference promotion.
- Memory poisoning tests proving model-authored proposals cannot become injectable memory without policy approval.
- Compaction safety test proving durable candidate disposition.
- Retrieval determinism for fixed store/policy/request.
- Cross-scope and cross-tenant retrieval denial tests.
- Prompt packet fallback for a provider without native memory.
- Standard memory tools for a tool-capable non-native provider path.
- Native Anthropic adapter compatibility with existing `/memories` behavior.
- CLI profile resolution for generic, Claude Code, Codex, Antigravity, legacy Gemini, and custom.
- Engine-class durability behavior for all five engine classes at the contract level.
- Redaction/tombstone exclusion from packets and tools.

### Completion rule

No implementation arc may claim the memory layer complete unless all `C-MEM-*` contracts are implemented and verified. A blocker may substitute for implementation only when it names an external dependency whose absence is verified by a deterministic probe and is recorded in a fork, roadmap, or credential-gate surface. A partial provider adapter is not sufficient.
