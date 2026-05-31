# Research-Citation Pointers — Voice → Cluster Mapping

Standing reference (authored 2026-05-31 per workspace council/adversarial/research bake-in arc) — maps each council voice to the research-corpus cluster deep-dive(s) carrying its domain's external-authority anchors.

The research corpus at `research/` is the Phase 1 substrate that the design phase consumed to produce ADRs + ADD + PRD + per-axis specs. By the time the design phase closed (Phase 6.5 ε, 2026-05-15), the research had been crystallized into canonical artifacts. The research is therefore **derivative-redundant for re-litigating settled design decisions**, but **high-value for external-authority grounding** when a voice's position needs anchoring beyond intra-workspace authority.

Use this file to look up the right cluster section when a voice wants to cite external authority — Anthropic engineering posts, LangGraph / Temporal / OpenAI Agents SDK production patterns, Pattern Reference Catalog v1.0 entries — during deliberation.

---

## Corpus inventory

| File | Lines | Scope |
|---|---|---|
| `research/Pattern_Reference_Catalog_v1.0.md` | 3603 | Master catalog of patterns/primitives synthesized from Sessions A–G |
| `research/Triaged_Source_Inventory__Pattern_Reference_Catalog_Pre-Construction.md` | 342 | Triaged source list (40+ sources) used to scope the PRC |
| `research/agent-harness-eng-deep-research-baseline.md` | 573 | Session-1 landscape map; canonical Anthropic "Building Effective Agents" framing |
| `research/agent-harness-eng-existing-thought-leaders-research.md` | 692 | Session-2 thought-leader + artifact inventory (LangGraph, OpenAI, Microsoft Agent Framework, CrewAI, Mastra, etc.) |
| `research/agent-harness-eng-research-cluster-1-orchestration-control.md` | 610 | Orchestration patterns + multi-LLM routing + sub-agents + parallelism |
| `research/agent-harness-eng-research-cluster-2-context-prompts-memory.md` | 635 | Prompt management + context engineering + state/memory consistency |
| `research/agent-harness-eng-research-cluster-3-tools-skills-validation.md` | 624 | Tool integration + Skills + validator/judge gates |
| `research/agent-harness-eng-research-cluster-4-observability-reliability-security.md` | 778 | Observability + reliability + security + HITL |
| `research/agent-harness-eng-research-cluster-5-surfaces-primitives-cross-cutting.md` | 400 | Deployment surfaces + Anthropic-specific area + cross-cutting tradeoffs |
| `research/agent-harness-eng-research-github-repos.md` | 343 | 1k+ star repo deep profiles (LangChain, AutoGen, CrewAI, LlamaIndex, etc.) |
| `research/agentic-engineeriing-sdlc.md` | 567 | **NEW (not in Phase 1 council context)** — 8-phase canonical SDLC applied to agent-native development; valuable for Workflow v1.14+ revision and Phase 7→8 transition framing |

---

## Voice → cluster mapping

| Voice | Domain | Primary cluster | Secondary | When to cite |
|---|---|---|---|---|
| **C1 — Orchestration & Control** | Topology, control-flow, sub-agent boundaries, HITL placement | Cluster 1 (orchestration-control) | PRC v1.0 §orchestration; deep-research-baseline §workflows-vs-agents | When voice disputes topology pattern, sub-agent boundary, or control-flow shape against canonical Anthropic taxonomy |
| **C2 — Context Engineering** | Within-turn context staging, prompt composition | Cluster 2 (context-prompts-memory) | PRC v1.0 §context-engineering | When voice disputes context window management, retrieval strategy, or prompt assembly discipline |
| **C3 — State, Memory & Persistence** | Durable state across inferences, ledger, checkpoint cadence | Cluster 2 (context-prompts-memory) §state-memory; Cluster 4 (observability) §audit-ledger | PRC v1.0 §persistence | When voice disputes durability model, checkpoint discipline, or hash-chain semantics |
| **C4 — Tools & Integration** | Tool contracts, MCP, sandbox, idempotency posture | Cluster 3 (tools-skills-validation) | github-repos §MCP-impls; thought-leaders §tool-frameworks | When voice disputes tool schema, MCP integration shape, or sandbox tier |
| **C5 — Validation Contract** | In-loop deterministic gates, evaluator-optimizer, Reflexion | Cluster 3 (tools-skills-validation) §validation | PRC v1.0 §validation-gates | When voice disputes gate shape, fail-class taxonomy, or evaluator contract |
| **C6 — Model Routing** | Capability-aware multi-LLM routing, provider portability | Cluster 1 (orchestration-control) §multi-llm-routing | PRC v1.0 §routing; deep-research-baseline §multi-llm | When voice disputes routing strategy, fallback chain composition, or provider abstraction |
| **C7 — Observability** | OTel spans, audit attributes, cardinality, sampling | Cluster 4 (observability-reliability-security) §observability | PRC v1.0 §observability | When voice disputes span schema, attribute namespace, or sampling policy |
| **C8 — Eval Engineer** | Eval methodology, judge holdout, gate-quality audits | Cluster 3 (tools-skills-validation) §validation; Cluster 4 §eval-methodology | PRC v1.0 §eval | When voice disputes eval design, judge alignment, or holdout discipline |
| **C9 — Reliability & Recovery** | Retry/backoff, breaker, idempotency, fallback timing | Cluster 4 (observability-reliability-security) §reliability | PRC v1.0 §reliability-primitives | When voice disputes retry policy, breaker shape, or fallback trigger |
| **C10 — Action Safety & Blast Radius** | Sandbox tiers, trust boundaries, secrets, blast-radius gating | Cluster 4 (observability-reliability-security) §security; Cluster 5 §cross-cutting-tradeoffs | PRC v1.0 §safety | When voice disputes blast-radius classification, trust tier, or sandbox dispatch |
| **C11 — Operator Loop & Local Deployment** | HITL primitives, local-first surface, operator experience | Cluster 4 (observability-reliability-security) §HITL; Cluster 5 §deployment-surfaces | thought-leaders §local-first | When voice disputes HITL palette, operator gate shape, or local-deployment-surface posture |

---

## Citation discipline

When a voice cites the research corpus during deliberation:

1. **Cite the cluster file + section** — e.g., `research/agent-harness-eng-research-cluster-1-orchestration-control.md §sub-agents`. Section anchors are stable across the corpus.
2. **Cite the underlying primary source if named** — the research deep-dives carry HIGH/MODERATE/SPECULATIVE-tagged citations to original sources (Anthropic engineering, arXiv IDs, GitHub repos, vendor docs). Prefer the primary source cite for load-bearing claims.
3. **Cite from Pattern Reference Catalog v1.0 for canonical patterns** — PRC is the synthesis; voices arguing "the canonical pattern is X" should ground that in PRC §X.Y.
4. **Distinguish external authority from internal authority** — design-substrate cites are internal (workspace's own ADRs / specs / plans); research cites are external (industry/academia). Both are admissible; voices should be explicit about which they're invoking.
5. **Probe-first discipline applies to research cites too** — if a voice asserts "the canonical reference says X" and the assertion is contested, the orchestrator MUST grep the cited file before resolving the tension. The pilot's lesson: deliberation surfaces, primary sources decide.

---

## When NOT to cite the research corpus

- **Settled design decisions.** ADRs F1–F5 + D1–D6 + ADD v1.3 + PRD v1.1 are canonical at workspace. Re-citing the research corpus to relitigate these is the failure mode the council was built to avoid.
- **Workspace-specific patterns.** The workspace has accumulated 50+ named patterns at `MEMORY.md` (`[[advisor-before-substantive-work-for-cross-axis-blockers]]`, `[[strike-revision-on-refined-second-tier-reason]]`, etc.). These are workspace-internal authority; the research corpus does not carry them. Cite workspace memory directly.
- **Phase 7 implementation tactics.** Specific impl arc choices (which composer file, which factory shape) are not settled by research — they're settled by spec + plan + workspace impl precedent. Don't pull research into impl-level tactical decisions.

---

## Maintenance

- This mapping evolves as research is updated. When a new research file lands at `research/`, add a row to the corpus inventory + extend voice mappings.
- `agentic-engineeriing-sdlc.md` is currently mapped at the workflow-doc revision arc (not a council voice's primary domain). Future workflow v1.14+ revision arcs SHOULD cite this file.
- This file is referenced from `council-orchestrator/SKILL.md` §"Workflow at runtime" step 4. Updates here propagate automatically through skill activation.
