# ADR-D7: Adopt a provider-neutral harness memory substrate with CLI profiles and provider adapters

## Status

Proposed.

Date: 2026-07-01

## Context

ADR-F2 already commits filesystem + git as the canonical state substrate, with artifact-tier layering across working, episodic, semantic, procedural, and durable tiers. The Information Substrate spec already defines those five tiers. ADR-D3 already recognizes the Anthropic Memory tool as a client-side primitive mapping to CoALA episodic and semantic memory, and says the memory store is cross-family-compatible in principle because the harness implements the backend.

The current implementation closes only the concrete Anthropic Memory callback surface. It validates `/memories` paths, resolves a storage backend, and invokes the callback loop when an Anthropic request includes the Memory tool. That is narrower than F2 and D3 require.

The deployed multi-OAuth external CLI routing implementation in `thestoryportal/arhugula` is a separate existing substrate, not the gap. It already spans runtime config schema/defaults, external CLI subprocess adapters, provider construction/degradation, CP_CLIENTS bootstrap binding, LLM dispatch, `harness.toml.example`, `just external-cli-config`, examples, docs, and tests. The memory decision must compose with that route rather than replace it.

At this ADR filing head (`cc612ec8`), the local `main` branch does not yet include that deployed external CLI routing surface. The memory implementation must therefore sequence CLI-profile units after the routing port lands, while allowing canonical memory store and policy units to proceed independently.

The operator decision is explicit: there is no limited MVP. The system must build the full memory layer now, and it must manage memory for multi-LLM routing inside any CLI as well as CLI-specific surfaces.

## Decision

Adopt a provider-neutral harness memory substrate as the canonical memory architecture.

The memory substrate consists of:

1. Canonical filesystem/git records for episodic, semantic, procedural, and durable memory.
2. A canonical append-only memory operation ledger for capture, retrieval, promotion, injection, deletion, redaction, and compaction decisions, reusing the existing C-IS state-ledger hash-chain discipline, with non-authoritative review projections for promotion, injection, and retrieval.
3. Policy-gated promotion from working/episodic state into semantic or procedural memory.
4. Bounded retrieval and ranking that assembles source-linked memory packets.
5. Provider access modes: native provider memory, standard memory tools, prompt-extension packet, and no-memory access.
6. CLI profiles: generic, Claude Code, Codex, Antigravity, legacy Gemini, and custom.
7. Engine-class durability bindings for the closed five-value taxonomy: `event-sourced-replay`, `save-point-checkpoint`, `pure-pattern-no-engine`, `reconciler-loop`, and `WAL-segment`.

Anthropic Memory remains supported, but only as one adapter over the canonical memory substrate. Provider-native memory never becomes the source of truth.

## Rationale

### 1. F2 and D3 already commit the substrate shape

The design substrate is broader than a provider callback backend. F2's repo-as-memory posture and C-IS-02's five-tier model require real artifacts and ledgers. D3's Memory tool row names cross-session coding, project conventions, prior refactor decisions, per-execution failure learning, and research state. Those use cases require semantic and episodic capture, not only byte reads and writes under `/memories`.

### 2. Provider neutrality prevents architecture lock-in

If Anthropic native memory becomes the architecture, non-Anthropic providers can only receive lossy prompt summaries or no memory at all. A harness-owned store lets Anthropic use its native tool while OpenAI, Ollama, and future providers use standard tools or prompt-extension packets against the same records.

### 3. CLI profiles solve portability without erasing useful conventions

The harness must operate inside arbitrary CLIs. A generic profile keeps the memory layer portable. Claude Code and Codex profiles allow known instruction and progress conventions to be read under explicit policy. The profile is provenance and policy input, not a separate memory silo.

### 4. Promotion and injection are different safety decisions

Automatic episodic capture and durable operation ledgering are necessary for continuity and audit. Semantic preference promotion and injection into future context can change model behavior across runs. Those actions require explicit policy, source references, and durable decisions.

### 5. Derived indexes are useful but cannot be authoritative

Vector or semantic search can accelerate retrieval, but it cannot become the only source of memory truth. Filesystem/git artifacts and durable ledgers remain canonical because they are inspectable, reviewable, replayable, and compatible with the existing substrate.

## Consequences

### What becomes possible

- Cross-provider memory continuity.
- CLI-neutral operation with CLI-specific adapters where useful.
- Compaction safety through promotion decisions before context loss.
- Auditable preference and project-knowledge memory.
- Native Anthropic Memory support without vendor lock-in.
- Provider fallback that preserves memory access through standard tools or prompt packets.
- Engine-class-aware memory replay and recovery.

### What becomes harder

- The implementation spans multiple axes instead of staying in runtime only.
- Memory policy must be explicit and testable.
- Promotion and injection require review surfaces, not just storage APIs.
- Retrieval quality and token budget behavior must be deterministic enough to test.
- Redaction and deletion require tombstone-style ledger semantics rather than simple file mutation.

### Downstream constraints

- The Information Substrate axis owns canonical memory record schemas and path registry.
- The Action Surface axis owns provider-neutral memory tool contracts and memory access mode vocabulary.
- The Control Plane axis owns memory routing policy and provider/CLI access-mode selection.
- The Operational Discipline axis owns audit, redaction, retention, and ledger verification posture.
- The Runtime axis owns capture hooks, provider adapters, CLI profile loading, packet injection, and standard memory tool execution.
- Existing external CLI routing remains the provider-construction authority. Memory work adds profile provenance, memory access-mode selection, packet/tool/native adapter behavior, capture, and ledgering around that route.
- CLI-profile implementation units cannot claim completion against a branch that lacks the external CLI routing port; they must either depend on the landed port or carry it in the same implementation branch with explicit preservation tests for provider ordering, degradation, and dispatch telemetry.
- Default policy preserves current no-memory behavior until memory is explicitly enabled.
- Model-authored and external-CLI-authored memory is untrusted until policy promotes it; scope isolation and poisoning tests are required.
- Redaction prevents future harness retrieval/injection but cannot silently erase provider caches or committed git history; residual persistence must be ledgered.
- Provider OAuth/session state remains provider-owned. The harness may observe auth-check and dispatch outcomes, but memory policy cannot require reading or storing local CLI tokens.
- Implementation plans must decompose the full layer, not a reduced MVP.
- ADD v1.3 absorption is a clearance question for this new D7 packet; no ADD file is edited in this design PR.

## Alternatives considered

### Alternative 1: Extend the Anthropic callback backend only

Rejected. This would improve the existing primitive but would not satisfy F2's five-tier substrate or D3's cross-family compatibility note. It would also leave OpenAI, Ollama, and generic CLI execution without first-class memory access.

### Alternative 2: Prompt-extension memory only

Rejected. Prompt packets are necessary as a fallback, but prompt-only memory cannot support durable writes, provider-native tools, standard memory tools, compaction promotion decisions, or robust retrieval. It also risks unbounded context stuffing.

### Alternative 3: External vector database as canonical memory

Rejected. Vector storage may be a derived accelerator, but making it canonical would weaken filesystem/git reviewability and replay. The canonical memory store must remain inspectable artifacts plus append-only ledgers.

### Alternative 4: CLI-specific memory silos

Rejected. Claude Code and Codex conventions matter, but separate CLI memory silos would fragment cross-provider continuity. CLI profiles must adapt external conventions into the same harness substrate.

### Alternative 5: New top-level memory package

Rejected for v1. The existing axis packages already express the ownership boundaries this layer needs. A new package would add dependency and governance overhead before the package boundary has proven necessary. If implementation pressure later shows the axis split creates real duplication, a future ADR may factor shared memory code into a new package.

## Policy commitments

- Automatic episodic and durable capture is allowed by default when memory is enabled.
- Semantic and procedural promotion is policy-gated.
- Injection is separately policy-gated from promotion.
- Cross-project, cross-tenant, or cross-CLI sharing requires explicit scope.
- Redaction and deletion are durable operations with source references.
- Provider-native memory adapters cannot bypass the canonical policy plane.

## Acceptance

This ADR is satisfied when the memory substrate spec and implementation plan exist and are reviewed, and when implementation later proves:

- Anthropic native memory, standard memory tools, and prompt-extension packet fallback all use the same canonical store.
- Generic, Claude Code, Codex, Antigravity, legacy Gemini, and custom CLI profiles are supported.
- Compaction cannot lose load-bearing context without a durable promotion decision.
- Engine-class memory durability behavior is represented and tested.
- Memory operation ledgers can explain every capture, retrieval, promotion, injection, redaction, and denial.

## References

- ADR-F2: filesystem + git canonical state substrate.
- Spec_Information_Substrate_v1: C-IS-02 five-tier artifact layering.
- ADR-D3: Anthropic primitive adoption depth, Memory tool primitive 11, cross-family compatibility note, engine-class memory behavior.
- Spec_Harness_Runtime_v1: C-RT-22 MemoryToolRegistry and MemoryToolStorageBackendProtocol.
- Memory_Substrate_Design_v1.
- PRD_v1.2 R-MEM requirement family.
