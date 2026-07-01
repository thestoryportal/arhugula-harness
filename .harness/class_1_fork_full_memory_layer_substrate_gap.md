---
fork_class: Class 1 (design back-flow - substrate gap)
fork_id: class_1_fork_full_memory_layer_substrate_gap
filed_at: 2026-07-01
filed_against_head: cc612ec8
status: PROPOSED - operator approved full-memory-layer planning direction; implementation not started
routing_target: design-substrate memory packet, then implementation across the existing harness axes
related_artifacts:
  - design-substrate/ADR-F2.md
  - design-substrate/ADR-D3.md
  - design-substrate/Spec_Information_Substrate_v1.md
  - design-substrate/Spec_Harness_Runtime_v1.md
  - design-substrate/Memory_Substrate_Design_v1.md
  - design-substrate/ADR-D7_memory_substrate.md
  - design-substrate/PRD_v1_2.md
  - design-substrate/Spec_Memory_Substrate_v1.md
  - design-substrate/Implementation_Plan_Memory_Substrate_v1.md
---

# Class 1 fork: full memory layer substrate gap

## 1. Detection

The deployed `/arhugula/` harness implements a narrow provider-specific memory surface: the Anthropic `memory_20250818` callback backend, path validation under `/memories`, backend selection, and callback spans. That surface is real and useful, but it does not implement the broader memory/state substrate already committed by the design substrate.

The gap was surfaced by reviewing the local design and research corpus. The key finding is that the current harness mostly implements one provider primitive, while the design substrate commits a provider-neutral, five-tier memory substrate whose state lives in filesystem/git artifacts plus durable ledgers and is accessible across LLM families and CLI surfaces.

Scoping correction: the deployed multi-OAuth external CLI routing feature in `thestoryportal/arhugula` is not the missing layer. That feature already crosses runtime config types/defaults, external CLI subprocess adapters, provider construction/degradation, LLM dispatch, `harness.toml.example`, `just external-cli-config`, examples, docs, and tests. The memory gap is that this routing surface does not yet carry provider-neutral memory capture, retrieval, injection, or ledger semantics.

Repository sequencing correction: at `filed_against_head: cc612ec8`, this repository's local `main` branch does not yet contain the deployed external CLI routing feature. The memory plan treats that route as a prerequisite for CLI-profile memory units, not as already-present local substrate. Foundational canonical-store and policy units remain independent of that prerequisite.

## 2. Evidence

| Evidence | Finding |
|---|---|
| `ADR-F2.md` | F2 accepts filesystem + git as canonical state substrate and explicitly names artifact-tier layering over working, episodic, semantic, procedural, and durable state. |
| `Spec_Information_Substrate_v1.md` | C-IS-02 defines the five-tier model and places semantic, procedural, and durable tiers on filesystem + git. |
| `ADR-D3.md` | Anthropic Memory tool primitive 11 maps to CoALA episodic and semantic memory use cases such as coding sessions, project conventions, prior refactor decisions, failure learning, and research state. |
| `ADR-D3.md` | D3 requires engine-class-dependent memory durability: Temporal-style append/snapshot determinism, LangGraph memory-store versions, 12-factor ledger entries, K8s CR status or Memory CRD, and WAL rebuild/prewarm. |
| `ADR-D3.md` | D3 says the memory store is cross-family-compatible in principle because it is harness-implemented, with future non-Anthropic exposure via system-prompt extension content or standard function tools. |
| `Spec_Harness_Runtime_v1.md` | C-RT-22 specifies the narrower runtime callback backend for the Anthropic Memory tool. |
| Runtime implementation review | Current runtime memory dispatch is Anthropic-gated and delegates to the Memory tool callback loop; it does not manage provider-neutral capture, promotion, retrieval, or injection. |
| Information substrate implementation review | The five-tier registry exists, but it is metadata only; it does not implement capture, retrieval, ranking, promotion, or injection. |
| Control-plane implementation review | Provider capabilities cover tools/caching/thinking/batch, not memory-access classes or memory routing modes. |
| Deployed `thestoryportal/arhugula` external CLI routing implementation | Multi-CLI provider routing exists across config, adapters, provider materialization, dispatch, helper config, examples, docs, and tests; the memory layer must integrate with that surface rather than re-implement provider routing. |
| Local `cc612ec8` absence probe | `rg "ExternalCLIProvider|external_cli_provider|external_cli_providers|enabled_provider_names|external-cli-config" harness-runtime tools harness.toml.example examples docs README.md justfile` returned no hits, so CLI-profile memory implementation is port-gated in this repo. |

## 3. Gap statement

The current harness has a provider-specific memory callback backend, not the full memory layer. Missing surfaces:

- Automatic episodic capture of runs, turns, compaction summaries, tool outcomes, and failure learnings.
- Durable memory-operation ledger entries with idempotency, hashes, timestamps, provider/model/CLI provenance, and source artifact references.
- Semantic artifact schema for facts, preferences, decisions, conventions, and learned failure avoidance.
- Explicit promotion rules from working/episodic state into semantic or procedural memory.
- Provider-neutral retrieval, ranking, redaction, and context-packet assembly.
- Cross-provider memory access through standard tools when supported and read-only system-prompt extension packets when tools are unavailable.
- CLI-neutral and CLI-specific memory profiles for generic CLI use, Claude Code conventions, Codex conventions, and future CLI adapters.
- Memory provenance and access-mode decisions threaded through the existing external CLI provider route: `claude_code`, `codex`, `antigravity`, `gemini_legacy` over legacy `gemini`, and `generic-command`.
- Engine-class durability behavior required by ADR-D3.
- Review and test gates that prove memory behavior is not only mocked at the callback boundary.

## 4. Why this gap occurred

This gap is understandable. The earlier memory tool work closed the executable surface for the concrete Anthropic Memory tool callback primitive because that was the immediate runtime defect and the narrowest RETIRE-READY path for `memory.*` telemetry and `/memories` backend wiring. That work correctly implemented the client-side callback contract declared by C-RT-22.

The broader design commitments sat one layer above that runtime callback: F2's repo-as-memory state substrate, C-IS-02's artifact-tier layering, D3's CoALA episodic/semantic target, and D3's cross-family fallback note. Those commitments were not decomposed into a memory substrate PRD, ADR, spec, or atomic implementation plan. In practice, the harness implemented the provider primitive before the provider-neutral memory plane was specified.

The root cause is therefore a decomposition gap, not a local code bug. The design substrate had the memory direction, but the executable roadmap selected a narrower Anthropic primitive closure. The missing bridge is a formal memory substrate packet that makes the broader commitments implementable without silently inventing scope inside runtime code.

## 5. Operator decisions already applied

- There is no limited MVP. The full memory layer is the implementation target.
- The design direction is substrate-first and provider-neutral.
- Anthropic native Memory remains an adapter, not the architecture.
- The system must manage memory for multi-LLM routing inside any CLI and also support CLI-specific memory conventions.
- Automatic episodic and durable capture are required.
- Semantic/preference promotion and future injection are policy-gated and auditable, not silent.

## 6. Disposition

Route to a full design back-flow packet:

1. Design: `Memory_Substrate_Design_v1.md`
2. PRD: `PRD_v1_2.md`
3. ADR: `ADR-D7_memory_substrate.md`
4. Spec: `Spec_Memory_Substrate_v1.md`
5. Atomic plan: `Implementation_Plan_Memory_Substrate_v1.md`

Implementation must not start until the packet is reviewed and accepted. The implementation sequence may be atomic and incremental, but acceptance is for the full memory layer, not a reduced MVP.
