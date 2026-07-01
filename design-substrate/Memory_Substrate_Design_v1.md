# Memory Substrate Design v1

## Status

Proposed design back-flow packet.

Date: 2026-07-01

Scope: full provider-neutral memory layer for the harness, including CLI-neutral and CLI-specific operation. No implementation is included in this artifact.

## 1. Executive decision

Build the full memory layer as a substrate-first provider-neutral memory plane. Anthropic `memory_20250818` support remains one adapter over that plane, not the architecture.

The memory plane has four responsibilities:

1. Capture state from runs, turns, tools, compaction events, failures, decisions, and operator-approved promotions.
2. Store that state in filesystem/git artifacts and durable ledgers with provider, model, CLI, workflow, and engine provenance.
3. Retrieve and rank bounded memory packets for a run using explicit policy, source references, redaction, and token budgets.
4. Expose memory to any provider and any CLI through the best available access mode: native provider memory, standard tools, or read-only system-prompt extension.

There is no limited MVP. Implementation will be sequenced through atomic units, but the product acceptance target is the complete layer.

## 2. Existing commitments

This design is a back-flow from existing substrate commitments, not a new product direction.

| Commitment | Design implication |
|---|---|
| ADR-F2 commits filesystem + git as canonical state substrate and names artifact-tier layering. | Memory source of truth lives in repo-readable artifacts and ledgers, not provider-owned opaque memory. |
| C-IS-02 defines working, episodic, semantic, procedural, and durable tiers. | Memory must implement tier behavior, not just a `/memories/<path>` byte backend. |
| ADR-D3 Memory primitive 11 maps to CoALA episodic and semantic memory. | Memory must support cross-session project learning, decisions, conventions, failures, and research state. |
| ADR-D3 says memory is cross-family-compatible in principle because the harness implements the backend. | Memory access must work for Anthropic, OpenAI, Ollama, and future providers. |
| ADR-D3 defines engine-class-specific durability behavior. | Memory operations must compose with Temporal-style replay, LangGraph checkpoints, 12-factor ledgers, K8s reconcilers, and WAL engines. |
| C-RT-22 implements the Anthropic callback backend. | The existing callback backend becomes one adapter fed by the provider-neutral store and policy plane. |

## 3. Current-state assessment

What exists:

- A five-tier artifact metadata registry in the information-substrate axis.
- State-ledger schemas and append-only write helpers in the information-substrate axis.
- Runtime memory callback wiring for Anthropic Memory tool calls.
- Backend selection for filesystem, encrypted filesystem, S3, database, and operator-defined memory callbacks.
- Provider dispatch and prompt injection seams for Anthropic, OpenAI, and Ollama.
- Provider capability reflection for tools, caching, thinking, and batch.
- In the deployed `thestoryportal/arhugula` line, multi-OAuth local CLI routing across runtime config defaults, external CLI subprocess adapters, provider construction/degradation, LLM dispatch, temp config helper, `just external-cli-config`, provider examples, docs, and tests.

Repository status at this filing: the local `main` branch at `cc612ec8` does not yet contain that deployed external CLI routing surface. Foundational memory units can proceed without it, but CLI-profile memory units must land on top of, or after, the external CLI routing port so memory provenance and access-mode selection compose with the real provider route.

What does not exist:

- Provider-neutral memory domain objects.
- Durable memory-operation ledger schema.
- Automatic episodic capture.
- Semantic facts/preferences/decisions schema.
- Promotion pipeline from episodic to semantic/procedural artifacts.
- Retrieval, ranking, token budgeting, and context-packet assembly.
- Provider-neutral memory tools.
- Read-only prompt-extension memory packet fallback.
- CLI profile model for generic CLI, Claude Code, Codex, and future CLIs.
- Memory integration with the existing external CLI provider stack. Provider routing is already a runtime concern; memory must add provenance, policy, access-mode selection, capture, and injection around it rather than defining a parallel provider router.
- Engine-class memory durability strategies.
- Compaction-time promotion gates.

## 4. Target architecture

### 4.1 Memory plane

The memory plane is a cross-axis subsystem with authoritative pieces in existing axes:

| Axis | Responsibility |
|---|---|
| Information substrate | Canonical memory schemas, path registry, artifact IO, derived index metadata, memory-operation ledger entry schema, deterministic serializers. |
| Action surface | Memory access contracts, provider-access mode vocabulary, memory telemetry attributes, memory tool contract declarations. |
| Control plane | Memory routing policy, provider capability reflection, memory packet budget selection, provider/CLI access-mode selection. |
| Operational discipline | Audit, redaction, ledger verification, review gates, retention and promotion policy checks. |
| Runtime | Capture hooks, provider dispatch adapters, CLI profile loading, memory packet injection, standard tool exposure, Anthropic native adapter integration. |

No new top-level workspace package is required for v1. The memory layer is cross-axis by nature, but the repo already has axis packages for the relevant responsibilities.

### 4.2 Canonical store

The canonical source of truth is filesystem/git plus append-only ledgers. Memory operation ledgers reuse the existing C-IS state-ledger hash-chain discipline rather than forking a second causality mechanism. A vector or semantic index may exist, but it is derived and rebuildable.

Proposed canonical directory shape:

```text
.harness/memory/
  manifest.json
  policy.json
  episodic/
    runs/<run_id>/
      run.json
      turns.jsonl
      tool_events.jsonl
      compactions.jsonl
      summaries/
  semantic/
    facts/
    preferences/
    decisions/
    conventions/
    failures/
    research/
    index.jsonl
  procedural/
    snapshots/
    promoted/
  durable/
    memory_ops.jsonl
    promotion_decisions.jsonl
    injection_decisions.jsonl
    retrieval_events.jsonl
```

The exact paths are spec-bound in `Spec_Memory_Substrate_v1.md`. `durable/memory_ops.jsonl` is the authoritative global operation ledger using the existing C-IS hash-chain discipline; promotion, injection, and retrieval files are rebuildable review projections keyed by canonical operation ids. Implementations may add derived caches, but they cannot treat those caches as source of truth.

### 4.3 Memory artifact types

The layer should model memory artifacts as typed records, not loose Markdown blobs.

| Type | Tier | Purpose |
|---|---|---|
| `EpisodicRunRecord` | episodic | Per-run metadata: run id, workflow id, provider route, CLI profile, engine class, timestamps. |
| `EpisodicTurnRecord` | episodic | Prompt/response summaries, tool call summaries, failures, compaction candidates, token accounting. |
| `SemanticFactRecord` | semantic | Cross-run factual knowledge with scope, evidence, confidence, and expiry. |
| `PreferenceRecord` | semantic | Operator or project preference with source, scope, confidence, TTL, and injection policy. |
| `DecisionRecord` | semantic | Prior architecture/refactor/product decision with status, rationale, supersession, and evidence. |
| `ConventionRecord` | semantic | Project convention or coding norm with scope and source references. |
| `FailureLearningRecord` | semantic | Reusable failure pattern and avoidance rule mined from failed sessions. |
| `ProceduralSnapshotRecord` | procedural | Content-addressed snapshot of skills, prompts, routing manifest, AGENTS/CLAUDE/Codex guidance, and active memory policy. |
| `MemoryOperationEntry` | durable | Append-only ledger entry for capture, retrieval, promotion, injection, delete, redact, and compaction operations. |

Markdown may be generated as a human-readable projection, but JSON records are authoritative where structured fields matter.

### 4.4 Policy gates

Memory changes and memory injection are separate policy decisions.

Automatic by default:

- Capture episodic turn summaries, tool outcomes, compaction summaries, and failure observations.
- Append durable memory-operation ledger entries.
- Record procedural snapshot references for memory-affecting runs.

Policy-gated:

- Promote episodic observations into semantic memory.
- Promote repeated instructions into procedural artifacts.
- Inject semantic preferences or decisions into future model context.
- Share memory across provider families, CLIs, projects, or tenants.
- Delete, redact, or supersede durable memory artifacts.

The layer must fail closed. If policy cannot be resolved, the harness may capture durable evidence but must not silently promote or inject semantic memory.

### 4.4.1 Threat model

Persisted memory is a cross-run influence channel. Model-authored notes, external CLI memory imports, and summarized failures are untrusted until policy promotes them. The design must prevent prompt-injection persistence, cross-scope leakage, and model-proposed preferences masquerading as operator instruction.

Required controls:

- Model-authored writes land as episodic evidence by default.
- Semantic/procedural promotion requires policy, evidence, scope, and source authority.
- Retrieval and injection enforce project, workflow, tenant, provider-family, CLI-profile, and visibility scope before ranking.
- Redaction prevents future harness retrieval/injection, but cannot revoke content already sent to external providers or provider prompt caches; those limitations are ledgered.
- Redaction also cannot silently erase committed git history. If redacted content reached git history, that residual persistence is ledgered and any operator-managed history rewrite remains outside the memory layer.

### 4.5 Provider access modes

Providers differ in native capability. The memory plane chooses an access mode per provider/model/CLI/workflow step:

| Access mode | Use when | Behavior |
|---|---|---|
| `NATIVE_PROVIDER_MEMORY` | Provider has a native memory primitive and the harness has an adapter. | The provider-native tool operates against the canonical harness store through an adapter. |
| `STANDARD_MEMORY_TOOLS` | Provider supports tools/function calling. | Expose provider-neutral memory tools such as `memory.search`, `memory.read`, `memory.propose_promotion`, and `memory.write_note` under policy. |
| `PROMPT_EXTENSION_PACKET` | Provider has no usable tool path or tools are disabled. | Inject a read-only bounded memory packet into the system prompt using existing provider prompt injection seams. |
| `NO_MEMORY_ACCESS` | Policy denies memory, provider is unsafe for memory, or budget is zero. | Capture durable evidence of denial; do not inject or expose memory. |

Native provider memory never owns the canonical store. It is only an access surface.

For external CLI providers, access-mode selection composes with the existing provider route. The route already carries provider name, provider kind, command, auth-check posture, optional/degradation behavior, model, family, and fallback-chain precedence. Memory adds a second decision on top of that route: whether this provider receives native memory, standard memory tools, a prompt-extension packet, or no memory access. The memory layer must not read or store OAuth/session tokens from local CLIs; it observes only provider identity, command boundary, auth-check result, dispatch result, and policy-approved memory sources.

### 4.6 CLI profiles

The harness must support memory in any CLI and also honor CLI-specific conventions.

| CLI profile | Required behavior |
|---|---|
| `generic` | Use only harness memory policy, memory packet injection, and standard tools. No CLI-specific file conventions. |
| `claude_code` | Load project `CLAUDE.md` and Claude-owned progress conventions as procedural/episodic sources when policy allows. Do not treat Claude-owned memory as canonical harness memory unless imported through a ledgered capture. |
| `codex` | Load `AGENTS.md`, Codex instructions, and Codex-local memories only through explicit profile rules. Do not silently modify external Codex memory stores. |
| `antigravity` | Use the Google-family local CLI route while treating Antigravity-owned auth/session state as outside the memory store. Instruction and memory sources require explicit profile policy. |
| `gemini_legacy` | Use the legacy Gemini CLI route where still installed. Trust prompts, local CLI state, and external memory conventions require explicit policy and ledgered import. |
| `custom` | Adapter-declared instruction files, memory directories, and CLI capability map. Must satisfy the same policy and ledger contracts. |

The CLI profile is provenance, not a separate source of truth.

CLI profile resolution binds to existing external CLI routing where present:

- `claude_code` maps to provider `claude_code`, kind `claude-code`, command `claude`, and Anthropic-family routing.
- `codex` maps to provider `codex`, command `codex`, and OpenAI-family routing.
- `antigravity` and `gemini_legacy` map to Google-family CLI routes.
- `custom` maps to `generic-command` provider entries and their declared command/template behavior.

The profile imports CLI-specific instruction or memory conventions only through policy. It never treats a CLI-owned memory store as canonical unless a ledgered import operation creates canonical harness records.

### 4.7 Engine-class durability

The memory plane must bind memory operation durability to engine class:

| Engine class | Required memory behavior |
|---|---|
| `event-sourced-replay` | Memory reads/writes occur inside activities. Replay observes deterministic snapshots or append-only monotonic versions. |
| `save-point-checkpoint` | Checkpoints include memory store version and retrieval packet hash. Pending writes are staged and committed at checkpoint-safe boundaries. |
| `pure-pattern-no-engine` | Memory operations append state-ledger entries with idempotency keys and response hashes. Restart rebuilds active memory context from ledgers and artifacts. |
| `reconciler-loop` | Memory state is represented through CR status, a Memory CRD, or a mounted canonical store with observed generation/version. |
| `WAL-segment` | Restart prewarms or rebuilds memory state from WAL plus canonical memory ledgers before resuming a segment. |

### 4.8 Compaction rule

Compaction is not allowed to discard load-bearing context without a promotion decision.

Before a compaction event:

1. The runtime identifies candidate facts, decisions, preferences, failures, and procedural updates.
2. The memory policy decides whether each candidate is discarded, kept episodic only, proposed for semantic promotion, or proposed for procedural promotion.
3. The decision is written to `promotion_decisions.jsonl` and linked to the compaction event.
4. Only then may working context be compacted.

This does not require silent semantic promotion. It requires an explicit decision before loss.

## 5. Key flows

### 5.1 Run start

1. Resolve workflow, provider route, CLI profile, memory policy, engine class, and token budgets.
2. Write or resolve the active `ProceduralSnapshotRecord`.
3. Retrieve candidate semantic/procedural memory by scope and query context.
4. Rank, filter, redact, and budget the memory packet.
5. Select access mode per provider capability and policy.
6. Inject packet or expose tools as appropriate.
7. Ledger retrieval and injection decisions.

### 5.2 During run

1. Capture turn summaries, tool outcomes, model routing decisions, provider response metadata, and failure observations.
2. Append episodic records and durable operation entries.
3. For memory writes requested by native or standard tools, enforce path/scope/policy and ledger the operation.
4. Update derived indexes after canonical writes.

### 5.3 Compaction

1. Summarize working state into episodic records.
2. Generate promotion candidates.
3. Apply promotion policy or create operator-review candidates.
4. Ledger the promotion decision.
5. Compact only after the promotion decision is durable.

### 5.4 End of run

1. Finalize episodic run record.
2. Verify memory ledgers and derived indexes.
3. Stage semantic/procedural promotion proposals for review if policy requires.
4. Emit closeout telemetry.

## 6. Why the gap occurred

The implemented path solved the concrete Anthropic Memory tool callback backend first. That was the correct narrow closure for C-RT-22 and the `memory.*` runtime primitive, but it left F2 and D3's broader memory substrate undecomposed.

This is a planning decomposition gap:

- F2 committed repo-as-memory and five-tier artifact layering.
- D3 identified Memory tool use cases and cross-family compatibility.
- Runtime C-RT-22 specified the concrete callback surface.
- The missing artifact was the provider-neutral memory substrate specification that connects those commitments.

The remedy is not to extend the Anthropic callback piecemeal. The remedy is to implement the memory plane and make Anthropic one adapter.

## 7. Design constraints

- Full layer, no limited MVP.
- Provider-neutral first; provider-native adapters second.
- CLI-neutral and CLI-specific behavior both required.
- Filesystem/git and append-only ledgers are canonical.
- Vector indexes are derived caches only.
- Automatic episodic/durable capture is allowed; semantic/procedural promotion is policy-gated.
- Prompt injection must be bounded, cited, redacted, and ledgered.
- Provider-neutral memory tools must be policy-enforced and auditable.
- Memory packets must have token budgets and source references.
- Cross-provider memory sharing requires explicit scope and policy.
- Deletes and redactions are represented as ledgered tombstones/redactions. Content-bearing files may be physically redacted or compacted only through a ledgered operation that preserves old/new hashes and audit reason; append-only ledgers are not silently rewritten.

## 8. Non-goals

- Do not make provider-owned memory authoritative.
- Do not silently write user preferences into semantic memory without policy approval.
- Do not dump unbounded RAG context into every request.
- Do not bypass existing provider routing, prompt injection, or state-ledger primitives.
- Do not edit external CLI memory stores directly without an explicit import/export adapter and ledger entry.
- Do not silently rewrite git history as part of memory redaction.

## 9. Acceptance target

The full memory layer is accepted only when:

- Provider-neutral memory schemas, path registry, ledgers, capture hooks, retrieval/ranking, and context-packet assembly exist.
- Anthropic native memory, standard function tools, and prompt-extension fallback all operate over the same canonical store.
- Generic, Claude Code, Codex, Antigravity, legacy Gemini, and custom CLI profiles are represented.
- Engine-class durability behavior is implemented and tested.
- Compaction cannot discard load-bearing candidates without durable promotion decisions.
- Tests prove behavior across at least Anthropic native memory, a non-Anthropic tool-capable provider path, and a prompt-extension fallback path.
- Review artifacts show no design/implementation divergence on F2/D3/C-IS-02/C-RT-22.
