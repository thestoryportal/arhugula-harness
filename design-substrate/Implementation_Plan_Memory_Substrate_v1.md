# Implementation Plan - Memory Substrate v1

## Status

Proposed.

Date: 2026-07-01

Scope: atomic implementation plan for the full memory substrate. This plan is not an MVP. Units are sequenced only to control risk and review size.

## 1. Goal

Implement the complete provider-neutral memory layer specified by `Spec_Memory_Substrate_v1.md` and required by PRD v1.2 R-MEM.

The implementation is complete only when the harness can:

- Capture episodic and durable memory automatically.
- Promote semantic and procedural memory under explicit policy.
- Retrieve, rank, and assemble bounded memory packets.
- Expose memory through native Anthropic memory, provider-neutral memory tools, and prompt-extension fallback.
- Resolve memory behavior for generic, Claude Code, Codex, Antigravity, legacy Gemini, and custom CLI profiles.
- Preserve engine-class durability behavior.
- Audit capture, retrieval, promotion, injection, denial, redaction, and compaction decisions.

## 2. Non-negotiable constraints

- No limited MVP.
- No provider-owned canonical memory.
- No silent semantic or procedural promotion.
- No injection without policy and ledger decision.
- No unbounded prompt memory dump.
- No derived index as source of truth.
- No external CLI memory mutation without an explicit ledgered import/export policy.
- No runtime behavior change for no-memory deployments; default policy is memory-disabled until explicitly enabled.
- No completion claim until every `C-MEM-*` contract is implemented and verified; blockers are allowed only for registered external dependencies with deterministic absence probes.

Existing deployed external CLI routing in `thestoryportal/arhugula` is an integration boundary, not new scope. The memory layer must reuse and extend:

- `harness_runtime.types`: external CLI provider kind/config/default provider ordering.
- `harness_runtime.lifecycle.external_cli_provider`: Claude Code, Codex, Antigravity, legacy Gemini, and generic-command subprocess adapters.
- `harness_runtime.lifecycle.providers`: enabled-provider ordering, provider construction, optional degradation, and API/SDK fallback.
- `harness_runtime.lifecycle.llm_dispatch`: external CLI dispatch and `external_cli.*` telemetry.
- `harness.toml.example`, `tools/external_cli_provider_config.py`, `just external-cli-config`, examples, docs, and tests that prove provider precedence.

Repository sequencing note: at filing head `cc612ec8`, this repository's `main` branch does not yet contain the deployed external CLI routing surface. G1 foundational memory schemas, store, policy, and ledger work can proceed without it, but CLI-route-specific acceptance in U-MEM-05, U-MEM-12, U-MEM-14, U-MEM-18, and U-MEM-24 is port-gated. Those slices must run after the external CLI routing port is landed, or on an implementation branch that carries that port and proves provider ordering, optional degradation, and dispatch telemetry are preserved. No affected unit may claim full CLI-profile completion against a branch that lacks the routing port.

## 3. Axis placement

| Axis | Units |
|---|---|
| Information substrate | U-MEM-01, U-MEM-02, U-MEM-03, U-MEM-04, U-MEM-05, U-MEM-06, U-MEM-10, U-MEM-11, U-MEM-21, U-MEM-24 |
| Action surface | U-MEM-12, U-MEM-13, U-MEM-22, U-MEM-24 |
| Control plane | U-MEM-11, U-MEM-12, U-MEM-18, U-MEM-19, U-MEM-24 |
| Operational discipline | U-MEM-04, U-MEM-08, U-MEM-09, U-MEM-20, U-MEM-21, U-MEM-22, U-MEM-24 |
| Runtime | U-MEM-07, U-MEM-08, U-MEM-09, U-MEM-14, U-MEM-15, U-MEM-16, U-MEM-17, U-MEM-18, U-MEM-19, U-MEM-20, U-MEM-22, U-MEM-23, U-MEM-24 |
| Cross-axis closeout | U-MEM-24, U-MEM-25 |

## 4. Dependency map

```text
U-MEM-01 -> U-MEM-02
U-MEM-01 -> U-MEM-03
U-MEM-02 -> U-MEM-03
U-MEM-01 -> U-MEM-04
U-MEM-01 -> U-MEM-05
U-MEM-01 -> U-MEM-06
U-MEM-02 -> U-MEM-06
U-MEM-03 -> U-MEM-06
U-MEM-04 -> U-MEM-06
U-MEM-05 -> U-MEM-06
U-MEM-03 -> U-MEM-07
U-MEM-06 -> U-MEM-07
U-MEM-04 -> U-MEM-08
U-MEM-07 -> U-MEM-08
U-MEM-06 -> U-MEM-09
U-MEM-08 -> U-MEM-09
U-MEM-06 -> U-MEM-10
U-MEM-04 -> U-MEM-11
U-MEM-10 -> U-MEM-11
U-MEM-04 -> U-MEM-12
U-MEM-11 -> U-MEM-12
U-MEM-04 -> U-MEM-13
U-MEM-11 -> U-MEM-13
U-MEM-12 -> U-MEM-13
U-MEM-11 -> U-MEM-14
U-MEM-12 -> U-MEM-14
U-MEM-14 -> U-MEM-15
U-MEM-13 -> U-MEM-16
U-MEM-14 -> U-MEM-16
U-MEM-14 -> U-MEM-17
U-MEM-05 -> U-MEM-18
U-MEM-14 -> U-MEM-18
U-MEM-03 -> U-MEM-19
U-MEM-07 -> U-MEM-19
U-MEM-11 -> U-MEM-19
U-MEM-14 -> U-MEM-19
U-MEM-07 -> U-MEM-20
U-MEM-08 -> U-MEM-20
U-MEM-09 -> U-MEM-20
U-MEM-04 -> U-MEM-21
U-MEM-06 -> U-MEM-21
U-MEM-09 -> U-MEM-21
U-MEM-03 -> U-MEM-22
U-MEM-12 -> U-MEM-22
U-MEM-16 -> U-MEM-22
U-MEM-17 -> U-MEM-22
U-MEM-21 -> U-MEM-22
U-MEM-17 -> U-MEM-23
U-MEM-23 -> U-MEM-24
U-MEM-15 -> U-MEM-24
U-MEM-16 -> U-MEM-24
U-MEM-17 -> U-MEM-24
U-MEM-18 -> U-MEM-24
U-MEM-19 -> U-MEM-24
U-MEM-20 -> U-MEM-24
U-MEM-21 -> U-MEM-24
U-MEM-22 -> U-MEM-24
U-MEM-24 -> U-MEM-25

External CLI routing port gates CLI-route-specific acceptance in U-MEM-05, U-MEM-12, U-MEM-14, U-MEM-18, and U-MEM-24. It is not represented as a `U-MEM` node because it is an upstream/deployed feature port, not memory-layer scope.
```

## 4.1 Requirement coverage map

| Requirement | Primary units |
|---|---|
| R-MEM-01 full layer/no MVP | U-MEM-01 through U-MEM-25 |
| R-MEM-02 canonical filesystem/git store | U-MEM-02, U-MEM-03, U-MEM-06 |
| R-MEM-03 typed records | U-MEM-01, U-MEM-06, U-MEM-07 |
| R-MEM-04 automatic episodic and durable capture | U-MEM-03, U-MEM-07 |
| R-MEM-05 semantic/preference promotion | U-MEM-06, U-MEM-08, U-MEM-09 |
| R-MEM-06 compaction safety | U-MEM-20 |
| R-MEM-07 retrieval and ranking | U-MEM-10, U-MEM-11 |
| R-MEM-08 packet assembly and injection | U-MEM-11, U-MEM-14, U-MEM-15, U-MEM-16, U-MEM-17 |
| R-MEM-09 multi-provider memory routing | U-MEM-12, U-MEM-13, U-MEM-14, U-MEM-15, U-MEM-16, U-MEM-17 |
| R-MEM-10 CLI-neutral and CLI-specific memory | U-MEM-05, U-MEM-18, U-MEM-24 |
| R-MEM-11 engine-class durability | U-MEM-19 |
| R-MEM-12 redaction, privacy, and scope | U-MEM-04, U-MEM-21, U-MEM-24 |
| R-MEM-13 observability | U-MEM-22 |
| R-MEM-14 review and administration | U-MEM-09, U-MEM-21, U-MEM-25 |
| R-MEM-15 migration and compatibility | U-MEM-17, U-MEM-23, U-MEM-24 |

## 5. Atomic units

### U-MEM-01 - Declare memory vocabulary and record envelopes

Contracts: C-MEM-01, C-MEM-03.

Axis: Information substrate.

Implement:

- `MemoryTier`, `MemoryRecordKind`, `MemoryScope`, `SourceRef`, `MemoryRecordEnvelope`.
- Stable record identity and content hash helpers.
- Supersession and redaction-state fields.

Acceptance:

- Illegal tier/kind values are rejected.
- Content hash is deterministic for equivalent records.
- Supersession and redaction fields are present on every record envelope.

Verification:

- Schema tests for valid and invalid envelopes.
- Deterministic hash tests.

### U-MEM-02 - Implement memory path registry

Contracts: C-MEM-02.

Axis: Information substrate.

Depends on: U-MEM-01.

Implement:

- Logical path classes for manifest, policy, episodic, semantic, procedural, and durable ledgers.
- Root binding with deployment-surface remapping.
- Traversal rejection.
- Directory creation strategy for canonical roots.

Acceptance:

- Every C-MEM-02 path resolves through the registry.
- Traversal outside root fails loudly.
- Deployment remapping preserves logical path identity.

Verification:

- Path resolution tests for every logical path.
- Traversal rejection tests.

### U-MEM-03 - Implement durable memory operation ledger

Contracts: C-MEM-08.

Axis: Information substrate.

Depends on: U-MEM-01, U-MEM-02.

Implement:

- `MemoryOperationEntry` as an additive C-IS-05/C-IS-06 state-ledger derivative.
- Canonical append-only writer for `durable/memory_ops.jsonl` over the existing C-IS ledger append/verify discipline.
- Rebuildable projection writers for promotion decisions, injection decisions, and retrieval events.
- Idempotency handling.
- Prior-event-hash chaining.
- Global append serialization for concurrent writers.
- Ledger verifier.

Acceptance:

- Duplicate idempotency key for equivalent operation is safe.
- Non-equivalent duplicate idempotency key fails loudly.
- Hash-chain verification detects tampering.
- Parallel appends cannot fork the canonical memory operation ledger.
- Projection entries are keyed by canonical ledger `action_id` and do not define independent causality.

Verification:

- Append, retry, conflict, and tamper tests.
- Concurrent append serialization tests.
- Projection rebuild tests.

### U-MEM-04 - Implement memory policy model

Contracts: C-MEM-09.

Axis: Information substrate plus operational discipline.

Depends on: U-MEM-01.

Implement:

- Capture, promotion, access, review, retention, and redaction decision enums.
- Policy document schema.
- Default disabled/no-memory policy that preserves current runtime behavior until memory is explicitly enabled.
- Policy resolver with fail-closed injection and promotion behavior.

Acceptance:

- Default policy denies retrieval, injection, native memory, and standard memory tools unless memory is enabled.
- Policy resolution can deny capture, summarize capture, allow capture, and redact capture.
- Policy resolution can deny, queue, or allow promotion.
- Policy failure denies promotion and injection.

Verification:

- Policy matrix tests.
- Fail-closed tests.

### U-MEM-05 - Implement CLI profile schema

Contracts: C-MEM-16.

Axis: Information substrate.

Depends on: U-MEM-01.

Implement:

- `CliProfileKind`.
- `CliProfile`, instruction source, external memory source, and import policy schemas.
- Optional binding fields for existing external CLI provider identity: provider name, provider kind, command name, and auth boundary.
- Built-in generic, Claude Code, Codex, Antigravity, legacy Gemini, and custom profile validation.

Acceptance:

- Generic profile has no CLI-specific assumptions.
- Claude Code and Codex profiles require explicit source declarations.
- Built-in profiles declare provider identity bindings without creating a second provider-ordering system.
- Concrete mapping to deployed external CLI provider identities is verified only after the external CLI routing port is present.
- External memory source mutation is impossible unless import policy allows it.

Verification:

- Profile validation tests.
- Port-present provider identity mapping tests for the external CLI profiles.
- Import-policy guard tests.

### U-MEM-06 - Implement canonical memory store

Contracts: C-MEM-02, C-MEM-03, C-MEM-04, C-MEM-05, C-MEM-06, C-MEM-07.

Axis: Information substrate.

Depends on: U-MEM-01, U-MEM-02, U-MEM-03, U-MEM-04, U-MEM-05.

Implement:

- Store read/write interfaces for episodic, semantic, preference, procedural, and durable records.
- Canonical serialization.
- Atomic write discipline appropriate to local filesystem roots.
- Derived index invalidation hook.

Acceptance:

- Each canonical record kind can be written and read back byte-stably.
- Derived indexes are invalidated or marked stale after writes.
- Redacted/tombstoned records remain inspectable through the store API under audit mode.

Verification:

- Round-trip record tests.
- Derived-index invalidation tests.

### U-MEM-07 - Add automatic episodic capture API

Contracts: C-MEM-04, C-MEM-08.

Axis: Runtime.

Depends on: U-MEM-03, U-MEM-06.

Implement:

- Capture API for run start, turn completion, tool event, provider route, failure observation, compaction event, and run close.
- Durable ledger write for capture decisions.
- Minimal capture mode for redacted or summarized policy.
- Summary provenance fields for rule-generated, model-generated, operator, and imported summaries.

Acceptance:

- Every supported event can produce an episodic record and a memory operation entry.
- Stored summaries carry source, model when applicable, and summary hash.
- Capture failure is observable.
- Capture does not promote semantic memory.

Verification:

- Event capture tests.
- Capture failure tests.

### U-MEM-08 - Implement promotion candidate extraction

Contracts: C-MEM-10.

Axis: Runtime plus operational discipline.

Depends on: U-MEM-04, U-MEM-07.

Implement:

- Candidate extractor for facts, decisions, conventions, preferences, failure learnings, research findings, and procedural updates.
- Candidate source refs.
- Risk flags for sensitive, low-confidence, cross-scope, and behavior-changing candidates.

Acceptance:

- Extracted candidates are source-linked.
- Preference candidates distinguish operator-direct from inferred.
- Low-confidence candidates cannot auto-promote when policy requires review.

Verification:

- Candidate extraction tests from representative episodic records.

### U-MEM-09 - Implement promotion and review queue

Contracts: C-MEM-05, C-MEM-06, C-MEM-10.

Axis: Runtime plus operational discipline.

Depends on: U-MEM-06, U-MEM-08.

Implement:

- Promotion decision application.
- Review queue persistence for proposed semantic and procedural records.
- Operator approve, deny, supersede, and edit flow at the API level.
- Promotion decision ledger writes.

Acceptance:

- Approved semantic records become active only after policy/review allows it.
- Denied records are ledgered.
- Preference promotion requires scope, evidence, confidence, and injection policy.

Verification:

- Promotion lifecycle tests.
- Preference review tests.

### U-MEM-10 - Implement derived retrieval indexes

Contracts: C-MEM-02, C-MEM-11.

Axis: Information substrate.

Depends on: U-MEM-06.

Implement:

- Rebuildable metadata index over semantic/procedural records.
- Index version/hash.
- Rebuild command/API.
- Empty-store behavior.
- Optional non-authoritative search accelerator hook; absent accelerators degrade to deterministic metadata-index retrieval.

Acceptance:

- Index can be rebuilt from canonical records.
- Stale index is detected.
- Large-store retrieval uses the rebuildable index path rather than unbounded prompt dumping.
- Empty store returns a valid empty retrieval base.

Verification:

- Index rebuild and stale-detection tests.
- Large-store fixture test proving bounded indexed retrieval.

### U-MEM-11 - Implement retrieval, ranking, and packet assembly

Contracts: C-MEM-11, C-MEM-12.

Axis: Control plane plus information substrate.

Depends on: U-MEM-04, U-MEM-10.

Implement:

- Retrieval request/result models.
- Ranking over scope, recency, confidence, authority, pinning, failure-risk relevance, workflow, and CLI profile.
- Stable memory packet assembly with section ordering and token budget.
- Retrieval event ledger write.

Acceptance:

- Fixed store/policy/request produces stable selected refs and packet hash.
- Excluded considered refs carry reasons.
- Packet sections cite memory refs and obey budget.

Verification:

- Deterministic retrieval tests.
- Token budget tests.
- Exclusion reason tests.

### U-MEM-12 - Extend provider capability and access-mode selection

Contracts: C-MEM-13.

Axis: Action surface plus control plane.

Depends on: U-MEM-04, U-MEM-11.

Implement:

- `MemoryAccessMode` vocabulary.
- Capability reflection for native memory, standard memory tools, and prompt packet fallback.
- Selection function using provider, model, provider route, CLI profile, workflow policy, and token budget.

Acceptance:

- Anthropic can select native memory when policy allows.
- Tool-capable non-native providers can select standard memory tools.
- Providers without usable tools can select prompt-extension packet.
- External CLI route fields participate in access-mode selection when the external CLI routing port is present.
- Denial is explicit and ledgerable.

Verification:

- Access-mode matrix tests.
- Port-present external CLI route selection tests.

### U-MEM-13 - Define provider-neutral memory tools

Contracts: C-MEM-14.

Axis: Action surface.

Depends on: U-MEM-04, U-MEM-11, U-MEM-12.

Implement:

- Tool contracts for `memory.search`, `memory.read`, `memory.write_note`, `memory.propose_promotion`, and `memory.request_redaction`.
- Argument schemas.
- Output schemas carrying stable refs.
- Policy requirements per tool.

Acceptance:

- Tool schemas are provider-neutral.
- Write-like tools require durable ledger entries.
- Tool outputs never return untracked memory prose.

Verification:

- Contract schema tests.
- Policy requirement tests.

### U-MEM-14 - Implement runtime memory context composer

Contracts: C-MEM-11, C-MEM-12, C-MEM-13.

Axis: Runtime.

Depends on: U-MEM-11, U-MEM-12.

Implement:

- Run-start composition of policy, CLI profile, provider route, retrieval request, packet, and access mode.
- Injection decision ledger entry.
- No-memory-access denial entry.

Acceptance:

- Run start can produce a memory context with packet or denial.
- Packet hash and policy ref are stored before dispatch.
- External CLI provider routes compose with memory context when the external CLI routing port is present.
- No-memory-access is explicit.

Verification:

- Runtime composer tests for all access modes.
- Port-present composer tests for external CLI routes.

### U-MEM-15 - Implement prompt-extension packet fallback

Contracts: C-MEM-12, C-MEM-13.

Axis: Runtime.

Depends on: U-MEM-14.

Implement:

- Read-only system-prompt memory packet rendering.
- Provider prompt seam integration for providers that use top-level system content or leading system messages.
- Conflict detection with existing system prompt overrides.

Acceptance:

- Prompt packet is bounded, cited, and stable.
- Prompt injection conflict fails loudly.
- Denied or redacted records do not appear.

Verification:

- Prompt packet rendering tests.
- Provider prompt integration tests.

### U-MEM-16 - Implement standard memory tool executor

Contracts: C-MEM-14.

Axis: Runtime.

Depends on: U-MEM-13, U-MEM-14.

Implement:

- Tool executor for provider-neutral memory tools.
- Policy enforcement for every call.
- Durable ledger entries for reads and writes where required.
- Tool-call span emission.

Acceptance:

- `memory.search` and `memory.read` return only allowed refs.
- `memory.write_note` stays episodic unless policy promotes.
- `memory.propose_promotion` queues or applies policy decision.
- `memory.request_redaction` creates a reviewable durable request.

Verification:

- Tool executor tests.
- Non-native provider dispatch integration check.

### U-MEM-17 - Refactor Anthropic native memory adapter onto canonical store

Contracts: C-MEM-15.

Axis: Runtime.

Depends on: U-MEM-14.

Implement:

- Adapter bridge from Anthropic Memory callbacks to canonical store and policy.
- Compatibility with existing `/memories` path validation.
- Durable ledger entries for native adapter operations.
- Existing backend selection preserved where applicable.

Acceptance:

- Existing Anthropic callback behavior remains compatible.
- Native writes cannot silently promote semantic memory.
- Adapter reads and writes are policy-checked and ledgered.

Verification:

- Compatibility tests for existing memory callbacks.
- Native adapter policy tests.

### U-MEM-18 - Implement CLI profile loading

Contracts: C-MEM-16.

Axis: Runtime plus control plane.

Depends on: U-MEM-05, U-MEM-14.

Implement:

- Profile resolver for generic, Claude Code, Codex, Antigravity, legacy Gemini, and custom profiles.
- Integration with existing external CLI provider config and dispatch metadata for `claude_code`, `codex`, `antigravity`, `gemini_legacy` over legacy `gemini`, and `generic-command`.
- Instruction source loading under policy.
- External memory source read/import guards.
- CLI profile provenance threading into capture, retrieval, and injection.

Acceptance:

- Generic profile works without CLI-specific files.
- Claude Code and Codex profiles require explicit source policy.
- Custom profile can declare instruction and memory sources.
- Profile resolution follows active runtime provider route and does not override enabled provider order or fallback-chain selection.
- CLI profile appears in episodic and durable records.

Verification:

- Profile resolver tests for all built-in profiles and a custom profile.

### U-MEM-19 - Implement engine-class durability bindings

Contracts: C-MEM-17.

Axis: Runtime plus control plane.

Depends on: U-MEM-03, U-MEM-07, U-MEM-11, U-MEM-14.

Implement:

- Binding to the existing five-value `EngineClass` taxonomy.
- Memory store version and packet hash carrier for checkpoint engines.
- Activity/snapshot boundary contract for replay engines.
- State-ledger write contract for pure-pattern engines.
- Reconciler observed-version carrier.
- WAL rebuild/prewarm contract.

Acceptance:

- Each engine class has a represented memory durability strategy.
- The represented classes match the current closed `EngineClass` enum before implementation proceeds.
- Replay cannot perform unstabilized retrieval without recorded version or packet hash.
- Pending writes do not become active semantic memory before commit boundary.

Verification:

- Contract-level tests for all five engine classes.

### U-MEM-20 - Implement compaction safety hook

Contracts: C-MEM-06, C-MEM-10.

Axis: Runtime plus operational discipline.

Depends on: U-MEM-07, U-MEM-08, U-MEM-09.

Implement:

- Compaction candidate extraction before context loss.
- Required disposition for each candidate.
- Durable compaction decision entry.
- Fail-closed behavior when disposition cannot be written.

Acceptance:

- Compaction cannot complete without candidate disposition.
- Candidates can be discarded, kept episodic, promoted, or queued.
- Disposition is auditable.

Verification:

- Compaction safety tests.

### U-MEM-21 - Implement redaction, tombstone, and retention

Contracts: C-MEM-18.

Axis: Operational discipline plus information substrate.

Depends on: U-MEM-04, U-MEM-06, U-MEM-09.

Implement:

- Redaction event schema and writer.
- Tombstone state transition.
- Retention expiry operation.
- Ledgered physical redaction/compaction operation for content-bearing files where policy requires content removal.
- Retrieval/tool exclusion for redacted or tombstoned records.

Acceptance:

- Redacted records are excluded from packets and tools.
- Tombstoned records remain ledger-visible.
- Physical content removal preserves old and new content hashes in the redaction event.
- Retention expiry is ledgered before derived index removal.

Verification:

- Redaction/tombstone/retention tests.
- Physical redaction hash-preservation tests.

### U-MEM-22 - Implement memory observability

Contracts: C-MEM-19.

Axis: Action surface plus operational discipline plus runtime.

Depends on: U-MEM-03, U-MEM-12, U-MEM-16, U-MEM-17, U-MEM-21.

Implement:

- Memory telemetry attributes for capture, retrieval, ranking, packet assembly, injection, promotion, native adapter calls, standard tool calls, redaction, and denial.
- Failure class vocabulary.
- Additive compatibility with existing `memory.*` attributes: `memory.operation.kind`, `memory.path`, `memory.backend`, `memory.bytes_read`, `memory.bytes_written`, and `memory.context_editing_active`.

Acceptance:

- All major memory operations emit telemetry.
- Failure classes distinguish policy denial, path violation, IO failure, serialization failure, provider adapter failure, and retrieval empty result.
- Existing memory telemetry consumers remain compatible and existing attribute names are not renamed.

Verification:

- Span/attribute tests.

### U-MEM-23 - Implement migration and compatibility defaults

Contracts: C-MEM-15.

Requirements: R-MEM-15.

Axis: Runtime.

Depends on: U-MEM-17.

Implement:

- Adapter compatibility for existing storage backend selections.
- Migration path from callback-only memory store to canonical memory root.

Acceptance:

- Existing callback-backed memory can operate through the new adapter.
- Migration is explicit and ledgered.

Verification:

- Adapter backward compatibility tests.
- Migration dry-run tests.

### U-MEM-24 - Cross-provider and CLI verification suite

Contracts: C-MEM-20 and all preceding contracts.

Axis: Runtime plus information substrate plus action surface plus control plane plus operational discipline plus cross-axis evidence.

Depends on: U-MEM-15, U-MEM-16, U-MEM-17, U-MEM-18, U-MEM-19, U-MEM-20, U-MEM-21, U-MEM-22, U-MEM-23.

Implement:

- End-to-end scenario for Anthropic native memory.
- End-to-end scenario for standard memory tools on a non-native provider path.
- End-to-end scenario for prompt-extension fallback.
- CLI profile scenarios for generic, Claude Code, Codex, Antigravity, legacy Gemini, and custom.
- External CLI routing scenarios for Claude Code, Codex, Antigravity, legacy Gemini, and generic-command, with credential-gated live tests separated from deterministic subprocess-fake tests.
- Compaction safety scenario.
- Redaction and denial scenarios.
- Memory poisoning and cross-scope isolation scenarios.

Acceptance:

- All access modes are exercised.
- All CLI profiles are exercised.
- Existing external CLI provider ordering and optional degradation semantics are preserved.
- Compaction safety is exercised.
- Redaction and policy denial are exercised.
- Model-authored memory cannot become injectable without policy approval.
- Cross-project, cross-workflow, cross-tenant, cross-provider-family, and cross-CLI leakage is denied.
- Credential-gated live checks are separated from non-credential checks with explicit gates.

Verification:

- Local deterministic suite.
- Optional live-provider suite behind explicit credential gates.
- Cross-axis review of evidence.

### U-MEM-25 - Closeout, documentation, and review evidence

Contracts: C-MEM-20.

Axis: Cross-axis.

Depends on: U-MEM-24.

Implement:

- Operator-facing memory policy documentation.
- Maintainer-facing architecture notes.
- Migration notes.
- Review evidence packet.
- Closeout checklist mapping every R-MEM and C-MEM item to implementation and verification evidence.

Acceptance:

- Every R-MEM requirement is mapped to code and verification evidence.
- Every C-MEM contract is mapped to implementation and verification evidence.
- Any remaining blocker names an external dependency, includes a deterministic absence probe, and is registered in a fork, roadmap, or credential-gate surface.
- Out-of-family review has been run against the complete diff or explicitly blocked with reason.

Verification:

- Documentation link check.
- Closeout checklist review.

## 6. Required review gates

Before implementation starts:

- Review this design packet for consistency with ADR-F2, ADR-D3, C-IS-02, C-AS-13, C-AS-14 §14.7, C-RT-22, and the resolved H_T-CP-16 memory lineage.
- Confirm no existing roadmap artifact already supersedes the memory substrate packet.
- Confirm operator acceptance of the provider-neutral architecture and policy-gated promotion/injection behavior.

During implementation:

- Run narrow checks after each unit.
- Run cross-axis compatibility checks after every unit that changes a public contract.
- Run out-of-family review at each major group boundary: foundational store, retrieval/policy, provider access, CLI/engine durability, final full layer.

Before completion:

- Run the full local verification suite.
- Run credential-gated live checks only with explicit operator authorization.
- Run closeout and report all warnings.
- Produce a final R-MEM and C-MEM coverage matrix.

## 7. Grouping for PR execution

The units may land as multiple PRs if each PR is internally complete and does not claim full-layer completion early.

Recommended PR groups:

| Group | Units | Purpose |
|---|---|---|
| G1 | U-MEM-01 through U-MEM-06 | Canonical schemas, path registry, policy, store, ledger. U-MEM-05 schema can land port-free; external CLI identity mapping evidence is port-gated. |
| G2 | U-MEM-07 through U-MEM-11 | Capture, promotion, retrieval, packet assembly. |
| G3 | U-MEM-12 through U-MEM-17 | Provider access modes, standard tools, prompt fallback, Anthropic adapter. External CLI route branches of U-MEM-12 and U-MEM-14 are port-gated. |
| G4 | U-MEM-18 through U-MEM-22 | CLI profiles, engine durability, compaction safety, redaction, observability. Requires landed external CLI routing before CLI-profile completion claims. |
| G5 | U-MEM-23 through U-MEM-25 | Migration, end-to-end verification, documentation, final evidence. |

No group may be described as an MVP. Groups are review boundaries only.

## 8. Risk controls

| Risk | Control |
|---|---|
| Silent behavior change in no-memory runs | U-MEM-04 default-disabled policy preserves current behavior unless memory is enabled. |
| Provider-native memory bypasses policy | U-MEM-17 maps native operations through canonical policy and ledger. |
| Semantic preference pollution | U-MEM-06 and U-MEM-09 require evidence, confidence, scope, and injection policy. |
| Compaction loses facts | U-MEM-20 blocks compaction until candidate disposition is durable. |
| Retrieval becomes nondeterministic | U-MEM-10 and U-MEM-11 pin index version, request hash, selected refs, and packet hash. |
| CLI silos fragment memory | U-MEM-18 treats CLI profiles as provenance and import policy, not separate canonical stores. |
| Redaction rewrites history | U-MEM-21 uses tombstone and redaction events. |
| Engine replay sees different memory | U-MEM-19 records store version or packet hash at replay/checkpoint boundaries. |

## 9. Completion definition

The memory substrate is complete when:

- U-MEM-01 through U-MEM-25 are implemented.
- Every R-MEM requirement maps to implementation and verification evidence.
- Every C-MEM contract maps to implementation and verification evidence.
- Anthropic native memory, standard memory tools, and prompt packet fallback all operate over the same canonical store.
- Generic, Claude Code, Codex, Antigravity, legacy Gemini, and custom CLI profiles all resolve and are recorded.
- Compaction safety is enforced.
- Redaction and retention are durable.
- Engine-class memory durability is represented.
- Closeout and out-of-family review are complete or explicitly blocked by a registered external dependency with a deterministic absence probe.
