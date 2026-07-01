# PRD v1.2 - Memory Substrate Requirements

## Status

Proposed PRD back-flow revision.

Date: 2026-07-01

Relationship to prior PRD: additive memory-substrate requirements extending PRD v1.1. This file does not replace unrelated v1.1 requirements; it adds the R-MEM requirement family.

## 1. Product problem

The harness currently has an executable Anthropic Memory tool callback backend, but not the full memory layer described by the substrate design. The result is a product gap: memory behavior is provider-specific, callback-scoped, and not yet integrated with cross-run learning, CLI continuity, compaction safety, provider routing, or engine-class durability.

The product needs a full memory layer now. There is no limited MVP target. Implementation may be atomized for execution control, but all acceptance gates in this PRD must be satisfied before the memory layer is considered complete.

## 2. Product goal

Provide a provider-neutral, CLI-aware, durable memory layer that lets the harness:

- Capture useful episodic and durable memory automatically.
- Promote selected knowledge into semantic and procedural memory through explicit policy.
- Retrieve bounded memory packets just in time.
- Route memory access across Anthropic, OpenAI, Ollama, and future provider families.
- Work inside any CLI while preserving CLI-specific conventions where explicitly profiled.
- Preserve auditability, redaction, source references, and engine-class determinism.

## 3. Users and stakeholders

| Stakeholder | Need |
|---|---|
| Operator | Cross-session continuity without silent or unbounded memory mutation. |
| Harness maintainer | Typed schemas, deterministic stores, and tests that isolate behavior by axis. |
| Workflow author | Memory policies that can be declared per workflow, provider, CLI, and workload class. |
| Compliance reviewer | Durable operation ledgers, source references, redaction records, and replayable decisions. |
| Future provider adapter author | A provider-neutral memory API that does not require rethinking the store. |

## 4. Requirements

### R-MEM-01 - Full memory layer, no limited MVP

The implementation must target the complete layer described by this PRD. Atomic sequencing is allowed; scope reduction is not.

Acceptance criteria:

- The implementation plan covers capture, store, retrieve, rank, promote, inject, tool access, CLI profiles, engine durability, and audit.
- A completion claim must implement and verify every requirement; a blocker can substitute only when it names a registered external dependency with a deterministic absence probe.
- Anthropic native memory alone is insufficient for completion.

### R-MEM-02 - Canonical filesystem/git store

The memory source of truth must be filesystem/git artifacts plus append-only ledgers.

Acceptance criteria:

- Memory records are readable from canonical artifact paths.
- Durable memory ledgers are append-only and idempotency-keyed.
- Derived vector, keyword, or semantic indexes are rebuildable from canonical artifacts.
- Provider-owned native memory is never the authoritative store.

### R-MEM-03 - Typed memory records

The layer must define typed records for episodic, semantic, procedural, and durable memory.

Acceptance criteria:

- Episodic run and turn records include run, workflow, provider, model, CLI profile, engine class, timestamps, and source references.
- Semantic records include scope, evidence, confidence, TTL or expiry posture, supersession, and injection policy.
- Preference records are first-class semantic records, not unstructured notes.
- Procedural snapshot records include content hashes for prompts, skills, routing manifest, active instruction files, and memory policy.
- Durable operation entries include operation kind, actor, provider route, idempotency key, response hash, timestamp, prior hash, and affected memory refs.

### R-MEM-04 - Automatic episodic and durable capture

The harness must automatically capture episodic and durable memory evidence during execution.

Acceptance criteria:

- Run start, turn completion, tool result, provider route, failure observation, compaction event, retrieval event, injection decision, promotion decision, and run close are capturable events.
- Capture failure must be observable; it must not silently disappear.
- Captured episodic data may be summarized or redacted by policy, but the durable operation decision must remain ledgered.

### R-MEM-05 - Semantic and preference promotion

Semantic facts, preferences, decisions, conventions, research findings, and failure learnings must be promoted through explicit policy.

Acceptance criteria:

- Promotion candidates can be generated from episodic records and compaction events.
- Policy can select discard, keep-episodic, propose-semantic, promote-semantic, propose-procedural, or promote-procedural.
- Preference promotion requires scope, source, confidence, and injection policy.
- Promotion writes are ledgered and source-linked.
- The system must support operator-review queues for policy modes that require human approval.

### R-MEM-06 - Compaction safety

Compaction must not discard load-bearing context before promotion policy runs.

Acceptance criteria:

- A compaction event records candidate facts, decisions, preferences, failures, and procedural changes.
- Every candidate has a durable disposition before compaction completes.
- The runtime can prove, through ledgers, whether a candidate was discarded, retained episodically, promoted, or queued for review.

### R-MEM-07 - Retrieval and ranking

The layer must retrieve bounded, source-linked memory packets just in time.

Acceptance criteria:

- Retrieval accepts workflow, CLI profile, provider route, workload class, query context, scope, and token budget.
- Ranking can combine recency, scope match, confidence, source authority, explicit pinning, and failure-risk relevance.
- Retrieval packets include source references and stable content hashes.
- Retrieval can exclude low-confidence, expired, denied, superseded, or redacted records.
- Large memory stores must use rebuildable derived indexes, with vector or semantic search acceleration allowed only as a non-authoritative cache.

### R-MEM-08 - Memory packet assembly and injection

The layer must assemble bounded memory packets and expose them through provider-appropriate access modes.

Acceptance criteria:

- The packet builder has a deterministic token budget and stable section ordering.
- Packet content is read-only unless exposed through policy-checked tools.
- Prompt-extension packets are injected through existing provider system prompt seams.
- Standard memory tools expose provider-neutral operations where tools are supported.
- Native provider memory adapters operate against the canonical harness store.
- All injection decisions are ledgered with packet hash, provider, model, CLI profile, and policy reference.

### R-MEM-09 - Multi-provider memory routing

The control plane must select a memory access mode per provider/model/step.

Acceptance criteria:

- Provider capability reflection includes memory access classes beyond generic tool support.
- Routing can select native provider memory, standard memory tools, prompt-extension packet, or no memory access.
- Non-Anthropic providers can receive memory through tools or prompt packet fallback.
- Memory routing composes with the existing external CLI provider route, including enabled provider order, external CLI provider kind, fallback-chain model/family, auth-check result, and optional provider degradation.
- Local CLI OAuth/session material remains owned by the official CLI; the harness records auth-check and dispatch outcomes but does not read or store CLI tokens.
- Memory access denial is explicit and ledgered.

### R-MEM-10 - CLI-neutral and CLI-specific profiles

The layer must work inside any CLI and support explicit CLI-specific conventions.

Acceptance criteria:

- A generic CLI profile works without Claude or Codex assumptions.
- A Claude Code profile can load Claude-specific instruction/progress conventions as procedural or episodic sources under policy.
- A Codex profile can load AGENTS-style instruction conventions and Codex-local memory only through explicit import/read policy.
- Built-in CLI profiles bind to deployed provider identities and kinds: `claude_code`/`claude-code`, `codex`, `antigravity`, `gemini_legacy` over legacy `gemini`, and `generic-command`.
- A custom profile can declare instruction paths, memory path mappings, and capability flags.
- CLI profile identity is recorded in episodic and durable memory records.

### R-MEM-11 - Engine-class durability

Memory operations must compose with engine-class durability semantics.

Acceptance criteria:

- Temporal-style replay uses deterministic memory snapshots or monotonic append versions.
- LangGraph-style checkpointing stores memory version and packet hash in checkpoint state.
- 12-factor execution writes memory operations into state ledgers with idempotency keys.
- K8s reconciler execution has a CR-status, Memory CRD, or mounted-store binding.
- WAL execution can rebuild or prewarm memory from WAL plus canonical ledgers.

### R-MEM-12 - Redaction, privacy, and scope controls

Memory must be scoped and redacted by policy.

Acceptance criteria:

- Records carry project, workflow, provider-family, CLI-profile, tenant, and visibility scopes where applicable.
- Redaction produces a durable redaction/tombstone event rather than silent mutation.
- Retrieval excludes records denied by scope, redaction, expiry, or policy.
- Sensitive content capture can be disabled or summarized without disabling durable operation ledgering.
- Model-authored and external-CLI-authored memory is treated as untrusted until policy promotes it.
- Scope isolation prevents cross-project, cross-workflow, cross-tenant, cross-provider-family, and cross-CLI leakage.

### R-MEM-13 - Observability

Memory operations must be observable.

Acceptance criteria:

- Capture, retrieval, promotion, injection, native adapter operation, standard tool operation, and prompt-packet fallback emit telemetry.
- Telemetry includes memory tier, operation kind, access mode, provider, CLI profile, policy decision, packet hash where applicable, and failure class.
- Existing `memory.*` telemetry remains compatible with the new provider-neutral layer.

### R-MEM-14 - Review and administration

The layer must support review of pending promotions, denied injections, redactions, and drift.

Acceptance criteria:

- Promotion proposals can be listed, approved, denied, or superseded.
- Memory policy can be inspected at runtime.
- The operator can audit why a memory packet was included or excluded.
- Review decisions are durable and source-linked.

### R-MEM-15 - Migration and compatibility

The existing Anthropic callback backend must migrate into the memory plane without regression.

Acceptance criteria:

- Current `/memories` path discipline remains enforced.
- Existing filesystem, encrypted filesystem, S3, database, and operator-defined backend selection remains available as adapter storage where applicable.
- Anthropic native memory uses the same canonical policy and ledger path as provider-neutral memory tools.
- Existing no-memory requests keep the same behavior unless memory policy explicitly enables capture or injection.

## 5. Success metrics

- Cross-provider parity: one scenario proves Anthropic native memory, one proves standard tool memory, and one proves prompt-extension packet memory.
- Compaction safety: a testable compaction path proves candidate disposition before context loss.
- Retrieval quality: memory packets are bounded, source-linked, and deterministic for a fixed store and policy.
- Auditability: every promotion and injection can be traced to source records and policy.
- CLI portability: generic, Claude Code, Codex, Antigravity, legacy Gemini, and custom profiles all resolve through the same profile contract.

## 6. Out of scope

- Making provider-owned native memory canonical.
- Silent unreviewed semantic promotion where policy requires review.
- Unbounded RAG dumps into every request.
- Editing external CLI-owned memory stores without a ledgered import/export operation.
- Replacing the existing axis architecture with a new top-level package.

## 7. Open issues for specification

- Exact record field names and enum values.
- Exact path registry contract and path migration behavior.
- Exact memory tool operation names and argument schemas.
- Exact retention policy syntax.
- Exact review queue persistence format.
- Exact live-provider e2e credential gates.
