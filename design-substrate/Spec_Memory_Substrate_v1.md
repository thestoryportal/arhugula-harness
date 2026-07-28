# Specification - Memory Substrate v1

## Status

Proposed.

Date: 2026-07-01

Authority chain: ADR-F2, ADR-D3, PRD v1.2 R-MEM family, and Memory Substrate Design v1.

This specification introduces the `C-MEM-*` contract family for the full provider-neutral memory layer. It is additive to the existing Information Substrate, Action Surface, Control Plane, Operational Discipline, and Runtime specifications.

Revision: v1 -> v1.1 (`B-86` spec-leg apply pass - C-MEM-03 `provider_family` value domain, `null` semantics, and derivation rule; C-MEM-13 cross-family withholding invariant; C-MEM-14 exposure qualification. The Memory threat model is unchanged. Detail at the change-note below.)

Revision date: 2026-07-28

## Change-note (v1 -> v1.1)

**Trigger and back-flow authority.** RATIFIED Class 1 fork `.harness/class_1_fork_b86_memory_scope_provider_family_keying.md` (filed 2026-07-28; register row `B-86` at `.harness/forward-register.yaml`, status `design_substrate_gated` **at the fork filing** - that value is historical-at-filing, not live: the row transited to `open` within this same PR, since the spec leg below is what clears the design gate. Consult the register for live status). The fork's §5 recommendations were produced by a three-leg decorrelated pass: an Opus grounding agent (direct code and spec read, file:line evidence), a transcript-aware `advisor()` pass, and a genuinely-convened council deliberation - C10 (action-safety / blast-radius) and C3 (state / memory / persistence) co-primary, C6 (model routing) consultant. The Q1 C10↔C3 tension was surfaced and probe-resolved in favour of chain-primary keying, with C10's requirement satisfied at a different mechanism (the dispatch-side predicate of Amendment 2). This delta is the mechanical spec-leg apply of the fork's §6 drafting targets; nothing was decided here.

**Why this is conformance repair, not design extension (X-AL-3).** The Memory threat model's invariant "Retrieval and injection enforce project, workflow, tenant, provider-family, CLI-profile, and visibility scope before ranking." (line `:481` at fork-filing HEAD `f79dbe85`) **stands unchanged at v1.1 and is the authority for all three amendments below**. v1 already mandated that the provider-family boundary be enforced; it never stated what that boundary is keyed to, which left the mandate unfalsifiable at the contract level. v1.1 supplies the missing value domain, derivation rule, and dispatch-boundary condition that make the already-cleared invariant checkable. No new commitment is created.

**Amendment 1 - C-MEM-03: NEW subsection "`MemoryScope.provider_family` value domain and derivation" plus two appended invariants.** (a) Value domain: the field carries a `ProviderFamily` value - `anthropic`, `openai`, `google`, or `local_open_weight` - never a provider key, a model identifier, or a CLI-profile identifier; a record written with a non-value identifier is not retrievable under a family-scoped request, including a request scoped to that identifier's own family; normalization to the value domain is forward-only, leaving pre-normalization records as a permanent residual. (b) `null` semantics, load-bearing in the enforcement predicates but undocumented at v1: a `null` **stored** value denotes an unpartitioned record that matches any requested family - a wildcard, not an unknown-deny sentinel - while a `null` **requested** family does not widen access past a family-scoped record. The asymmetry is stated deliberately: it is what the enforcement predicates in aggregate actually do (the two scope-filter predicates skip a `null` on either side, but the policy leg they compose with denies a `null`-request-vs-non-`null`-record pair), and it is the field-level instance of C-MEM-09's "Injection cannot be broader than the record's scope." invariant. A first draft of this delta claimed symmetric either-side wildcarding; out-of-family Codex round 1 [P1-a] caught the over-claim against the policy predicate, and it was corrected before merge. (c) Derivation rule (fork §6 item 2, placed at C-MEM-03 rather than C-MEM-11 because it constrains a field C-MEM-03 declares): a run-level partition attribute, derived once at run-scope composition from the fallback chain's primary family binding, not re-derived per dispatch, so a fallback advancement to a different-family candidate does not alter the run's memory scope. (d) The paired writer-side obligation: memory capture writes under the run's composed record scope and does not construct an independent scope.

**Amendment 2 - C-MEM-13: NEW subsection "Cross-family withholding of standard memory tools" plus one appended invariant.** When `standard_memory_tools` has been selected and the dispatched candidate's provider family differs from `MemoryScope.provider_family`, the harness MUST NOT expose the memory tool schemas or the scope reference for that dispatch; the dispatch proceeds without model-facing memory access, and the withholding is recorded with a named denial reason on the C-MEM-19 memory telemetry surface (see the recording-surface paragraph below). Harness-authored memory capture is unaffected - C3's condition of concurrence, on the ground that capture is a different authorship class and crosses no boundary the harness does not already hold. C6's limit is recorded as a stated non-claim: family equality is a necessary but not a sufficient trust condition, and within-family routing to a local terminal surface carries a distinct posture addressed outside this contract.

**Recording surface, stated precisely (Codex round 1 [P1-b]).** The fork's §6 wording called a withheld exposure a "ledgered outcome"; v1.1 does **not** adopt that phrasing, because it over-claims. The withholding is a **recorded** outcome on the C-MEM-19 memory telemetry surface, with the denial reason carried as an attribute value - the shape already shipped for the B-83 packet disposition. On the durable-ledger half the position is split, and both halves are stated at the new C-MEM-13 recording-surface paragraph: (i) where the withholding is realized as a transition of that dispatch to `no_memory_access`, C-MEM-13's pre-existing must-ledger invariant applies unchanged and is **dischargeable through the existing `inject` operation kind** and its injection-decision projection - no new operation kind, no C-MEM-08 amendment; (ii) where it is not such a transition, no durable row is owed, because C-MEM-08's operation-kind vocabulary is closed and expresses no requested-but-withheld operation. Half (ii) is a **pre-existing recording-surface limitation of C-MEM-08, not created by v1.1** - the same constraint the `B-85` close-out recorded independently, and the same one the `B-83`-era span-only disposition already lives under. Widening that vocabulary would be a C-MEM-08 amendment on its own authority, and v1.1 neither performs nor implies one.

**Amendment 3 - C-MEM-14: the exposure obligation qualified.** The present-tense "the harness exposes provider-neutral tools" obligation is now explicitly subject to the C-MEM-13 family-scope condition, and a withheld exposure is a recorded outcome (per the paragraph above) rather than a violation of this contract. Recorded as a clarification of C-MEM-14's existing invariant "Tools cannot bypass scope, redaction, retention, or injection policy." - withholding is that invariant enforced at the exposure boundary instead of at the call - not an extension of it.

**No amendment - Memory threat model.** Zero change, deliberately. Per the X-AL-3 paragraph above, the `:481` invariant is the authority the three amendments conform to, not a surface they revise.

**Downstream consequences recorded here, applied elsewhere.** (i) `B-89` (producer key-vs-value asymmetry: written records carry raw provider keys while retrieval requests carry family values, so an `ollama`-written note is invisible even to a `local_open_weight`-scoped request of its own family) now has its direction determined - the writer adopts the run's composed record scope per Amendment 1(d). (ii) `B-90` (the capture path's independently-constructed scope omits `tenant` and `workload_class`, so under the wildcard-on-`null` semantics every tool-captured record is tenant-unpartitioned, against the `:481` tenant mandate) is closed incidentally by that same writer-side repair. (iii) The impl leg - the C-MEM-13 withholding guard (fork §5 Q2), the `B-89` writer repair, and the `B-90` fold-in - follows as a separate arc per the `B-33` / `B-59` / `B-70` / `B-72` spec-leg-then-impl-leg precedent. This delta changes no code.

**Plan absorption (same arc).** `Implementation_Plan_Memory_Substrate_v1.md` v1 -> v1.1 adds NEW U-MEM-26 decomposing that impl leg, filed in this same PR.

**Named open question carried forward, not discharged.** Fork §7: whether records captured during a cross-family fallback leg are promotion-eligible under C-MEM-10. That is C-MEM-10 policy territory, outside B-86's scope; v1.1 neither resolves nor forecloses it, and it is restated here so it does not disappear with the fork doc.

**Surfaced finding, not patched.** Three of the fork's `:NNN` cites are off-by-N against this file at HEAD `f79dbe85`: the C-MEM-14 "Tools cannot bypass scope…" invariant is at `:502` (fork §6 item 4 cites `:500`), the cross-run prompt-injection-persistence threat is at `:471` (fork §4 cites `:472`), and C-MEM-11's stable-result invariant is at `:392` (fork §4 cites `:384`). Every load-bearing cite the amendments rest on - C-MEM-03 `:100-108` and `:104`, C-MEM-11 `:346-395`, C-MEM-13 `:431-463` with `:449` and `:454`, the threat model `:465-483` and `:481`, C-MEM-14 `:485-504` - resolves byte-exact. No spec text is changed on account of the drifted cites. Separately, every pre-v1.1 `:NNN` cite into this file across `.harness/**` (for example the `B-84` row's `:463` and the `B-83` row's `:481`) is pinned to the HEAD at which it was written and shifts by construction with this delta; those are historical records of a filing state, not live contract references, and they are deliberately not rewritten here. Cite this spec by contract ID and section name, not by line, in any text authored after v1.1.

**Sections preserved verbatim at v1.1.** The Status section (revision lines appended only); C-MEM-01; C-MEM-02; the C-MEM-03 `MemoryRecordEnvelope`, `SourceRef`, and `MemoryScope` field shapes plus its three existing invariants (byte-unchanged - the amendment constrains a declared field's value domain and derivation; it adds, removes, and retypes nothing); C-MEM-04 through C-MEM-12; the C-MEM-13 `MemoryAccessMode` vocabulary, selection-input list, and all six existing invariants (byte-unchanged; one subsection and one invariant appended); the Memory threat model in full; the C-MEM-14 tool table and all four existing invariants (byte-unchanged; one qualifying paragraph appended to its Contract); C-MEM-15 through C-MEM-20. Zero new record type, zero new field, zero new enum member, zero change to any ledger, packet, or telemetry shape.

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

### `MemoryScope.provider_family` value domain and derivation

`provider_family` carries a `ProviderFamily` value - one of `anthropic`, `openai`, `google`, or `local_open_weight` - and never a provider key, a model identifier, or a CLI-profile identifier. The `string | null` declaration above is a serialization shape, not a licence to store an arbitrary identifier.

A record written with a non-value identifier in this field is not retrievable under a family-scoped request. The retrieval, index, and policy scope predicates compare the stored identifier against the requested family directly, so such a record is invisible even to a request scoped to that identifier's own family. Normalization to the value domain is forward-only: records already written with a non-value identifier are not rewritten and remain unretrievable under family-scoped requests as a permanent residual.

`null` on a stored record denotes an unpartitioned record: it matches any requested provider family. `null` is not an unknown-deny sentinel; a record that must be confined to one provider family carries that family's value, never `null`.

The wildcard is scoped to the stored-record side only, and the two sides are deliberately not symmetric. A `null` requested family does not widen access past a family-scoped record: a record carrying a family value is not reachable by a request that carries none. That asymmetry is this field's instance of C-MEM-09's "Injection cannot be broader than the record's scope." invariant - a request that declines to name a partition is narrower than, never broader than, a partitioned record.

`provider_family` is a run-level partition attribute. It is derived once, at run-scope composition, from the fallback chain's primary family binding, and it is not re-derived per dispatch: a fallback advancement to a candidate of a different provider family does not alter the run's memory scope. A fallback chain is a continuity mechanism, and the run's memory partition is one of the run-level identities it preserves across that boundary.

The paired writer-side obligation is that memory capture writes under the run's composed record scope. The capture path does not construct an independent `MemoryScope`; the run's composed scope is the single authority for every record the run writes, so what a run writes and what a run can retrieve share one partition by construction.

### Invariants

- `content_hash` is computed over canonical serialized content excluding derived indexes.
- Supersession does not delete the prior record.
- Redaction and tombstone states are durable memory operations.
- `provider_family` carries a `ProviderFamily` value or `null`, where a `null` stored value is the unpartitioned wildcard and not an unknown-deny sentinel, and a `null` requested value does not widen access past a family-scoped record.
- The run's composed record scope is the single authority for both retrieval and capture within a run; the capture path does not construct an independent scope.

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

### Cross-family withholding of standard memory tools

When `standard_memory_tools` has been selected and the dispatched candidate's provider family differs from `MemoryScope.provider_family`, the harness MUST NOT expose the memory tool schemas or the scope reference for that dispatch. The dispatch proceeds without model-facing memory access, and the withholding is recorded with a named denial reason. Harness-authored memory capture is unaffected: capture is a different authorship class and crosses no boundary the harness does not already hold.

Recording surface. The withholding is recorded on the C-MEM-19 memory telemetry surface, whose declared coverage already includes standard memory tool calls and policy denial, with the denial reason carried as an attribute value. Where the withholding is realized as a transition of that dispatch to `no_memory_access`, this contract's `no_memory_access` must-ledger invariant applies unchanged and is satisfied by the existing `inject` memory operation entry and its injection-decision projection; no new operation kind is required. Where the withholding is not such a transition, no durable ledger row is owed: C-MEM-08's operation-kind vocabulary is closed and expresses no requested-but-withheld operation, and adding one would be a C-MEM-08 amendment that this contract does not imply.

Stated limit. Family equality is a necessary but not a sufficient trust condition for exposing model-facing memory. Within-family routing to a local terminal surface carries a distinct trust posture that this contract does not address and does not claim to cover.

### Invariants

- Anthropic native Memory is an adapter, not canonical storage.
- Tool-capable non-Anthropic providers may use standard memory tools.
- Providers without usable tool support may receive prompt-extension packets.
- External CLI provider routing remains the provider-construction authority; memory access mode is selected after the route is known.
- Local CLI OAuth/session tokens are never memory records and are never read by the memory layer.
- `no_memory_access` is a valid policy outcome and must be ledgered when memory was requested.
- Standard memory tools and the scope reference are withheld on a cross-family dispatch per the cross-family withholding rule above; the withholding is a recorded outcome, carried on the C-MEM-19 memory telemetry surface with a named denial reason.

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

Exposure is subject to the C-MEM-13 cross-family condition: when the dispatched candidate's provider family differs from `MemoryScope.provider_family`, the tool schemas and the scope reference are withheld for that dispatch. A withheld exposure is a recorded outcome - carried on the C-MEM-19 memory telemetry surface with a named denial reason, per the recording-surface paragraph of C-MEM-13 - and not a violation of this contract. This qualification is a clarification of the "Tools cannot bypass scope, redaction, retention, or injection policy." invariant below - withholding enforces that invariant at the exposure boundary rather than at the call - and not an extension of it.

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
