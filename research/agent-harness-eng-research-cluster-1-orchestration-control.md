# Cluster Deep-Dive 1 — Orchestration and Control Flow

**Active session.** Session 4, first cluster deep-dive in Advanced Research mode. Cluster name: *Orchestration and Control Flow*. Topics, in order: (1) orchestration patterns, (2) multi-LLM routing, (3) sub-agents and single-file agents, (4) parallelism. Builds on Session 1 (substrate), Session 2 (harnesses/thought leaders), Session 3 (1k+ star repos). This session re-engages canonical sources at prompt and protocol depth and adjudicates contested points the substrate flagged but did not resolve.

---

## 1. Executive Synthesis

1. **The Cognition–Anthropic debate is not symmetric and should not be flattened.** Yan's *Don't Build Multi-Agents* (Jun 12, 2025) attacks **parallel writers** sharing implicit decisions ("Flappy Bird" example: bird and background built by isolated subagents conflict in style and motion). Anthropic's *How we built our multi-agent research system* (Jun 13, 2025) defends **parallel readers** condensing into a single synthesizer. Cognition's follow-up *Multi-Agents: What's Actually Working* (Apr 22, 2026) explicitly converges: "writes stay single-threaded… additional agents contribute intelligence rather than actions." [HIGH] **Decision rule for the builder:** parallelize read/research; serialize writes.
2. **Anthropic's research system spawns 3–5 subagents per fan-out, scales rules embedded in prompt** — "Simple fact-finding requires just 1 agent with 3-10 tool calls, direct comparisons might need 2-4 subagents with 10-15 calls each, complex research more than 10 subagents with clearly divided responsibilities." Multi-agent uses ~15× chat-token budget; token usage alone explains 80% of BrowseComp variance. [HIGH]
3. **Sub-agent brief is a four-field contract.** Anthropic states each subagent needs "an objective, an output format, guidance on the tools and sources to use, and clear task boundaries." Vague briefs ("research the semiconductor shortage") cause duplicated work; the documented failure was three subagents converging on the same chip-shortage decade. [HIGH]
4. **Concurrent prompt-cache hits are not free.** Anthropic's docs are explicit: "a cache entry only becomes available after the first response begins. If you need cache hits for parallel requests, wait for the first response before sending subsequent requests." This invalidates the naive "fan out N parallel sub-agents off the same prefix" assumption. [HIGH] **Builder implication:** issue one warm-up call, then fan out.
5. **Self-consistency saturates well before N=40 on production tasks.** Independent replications (Loo 2026, arXiv:2511.00751; Wang et al. 2024 on long-context) confirm Wang's original diminishing-returns curve flattens by N≈5–10 on most production-grade benchmarks; Claude Opus 4.5 *loses* accuracy at N=5 in one 2026 study while gaining faithfulness. [MODERATE] Default N=5 with adaptive early-stop (SPRT/Adaptive-Consistency) over fixed N=40.
6. **OpenAI manager pattern ≡ Anthropic orchestrator-workers; OpenAI decentralized ≡ Microsoft handoff.** OpenAI: "In the manager pattern, edges represent tool calls whereas in the decentralized pattern, edges represent handoffs." Microsoft Agent Framework adds two patterns the others omit: **Group Chat** (manager-coordinated turn-taking) and **Magentic** (manager builds a *task ledger* dynamically, AutoGen-derived). Anthropic adds **evaluator-optimizer** which has no first-class equivalent in either OpenAI or Microsoft taxonomy — it's a configuration of group-chat or sequential. [HIGH]
7. **Routing literature has converged on two thresholds and a budget.** RouteLLM exposes a calibrated **threshold α** mapped to "% calls to strong model" (e.g., α calibrated to send 50% of queries to strong, retain ~95% of GPT-4 quality at ~50% cost on MT-Bench). FrugalGPT cascades on **scoring-model confidence** (per-stage threshold tuned on holdout). xRouter (arXiv:2510.08439, Oct 2025) replaces hand-thresholds with RL: **reward = quality − λ·normalized_cost**, with three released λ variants (xRouter-7B-1/2/3). [HIGH]
8. **Category-aware semantic caching is now the state of the art.** Wang et al. (arXiv:2510.26835, Oct 2025) document that uniform similarity thresholds break across workloads: code clusters densely (40–60% hit rate), conversation sparsely (5–15%). The hybrid in-memory HNSW + external doc store reduces miss cost from 30 ms to 2 ms, lowering break-even hit rate from 15–20% down to 3–5%. [HIGH] Substrate covered semantic caching at survey depth; this is the per-category policy not in substrate.
9. **Anthropic's *long-running agents* harness (Nov 26, 2025) introduces a documented two-prompt pattern.** Initializer agent writes a JSON `feature_list` (200+ features), `init.sh`, and `claude-progress.txt` on first run; subsequent **coding agents** read these artifacts, work on one feature, commit. The artifact-passing-via-filesystem pattern formalizes the "subagent output to a filesystem to minimize the 'game of telephone'" tip from the multi-agent research system appendix. [HIGH]
10. **Single-file agent (SFA) ceiling is approximately one tool family + ≤10 compute loops.** Disler's reference set (`sfa_duckdb_anthropic_v2.py` etc.) caps at `-c 10` default compute loops and one capability per file. Beyond that, the natural escalation is sub-agent-as-tool (smolagents `managed_agents`, OpenAI Agents SDK `agent.as_tool()`), not a multi-file SFA. [HIGH]
11. **Fan-in merger bottleneck has a documented fix: bypass the merger.** Anthropic's appendix recommends "subagents call tools to store their work in external systems, then pass lightweight references back to the coordinator." This is the only well-documented production pattern for the case where N subagent outputs no longer fit in the lead's context. [HIGH]
12. **Evaluator-optimizer is not Reflexion.** Reflexion (Shinn 2023) is *single-agent* verbal RL persisting reflective text in episodic memory across trials; Anthropic's evaluator-optimizer is *two roles* in one trial. Substrate conflated these; in cluster terms evaluator-optimizer is closer to Cognition's "Devin Review" generator-verifier loop where Cognition explicitly recommends *no shared context* between coder and reviewer. [HIGH]

---

## 2. Per-Topic Deep Dives

### 2.1 Topic 1 — Orchestration Patterns

#### 2.1.1 Topic restatement
Substrate (Session 1 §2.1) catalogued the six Anthropic patterns plus framework-level patterns at survey depth. The deep-dive engages the canonical sources at the prompt and protocol level: it characterizes the orchestrator-worker brief, maps the three taxonomies (Anthropic / Microsoft / OpenAI) onto each other, surfaces the operational signals that tip a workload to multi-agent, and adjudicates the Cognition–Anthropic debate at the mechanism level rather than at the slogan level.

#### 2.1.2 Canonical sources, deeply engaged

**Anthropic, "Building Effective Agents," Schluntz & Zhang (Dec 19, 2024)** [HIGH]
- Defines the workflow/agent split: workflows are "systems where LLMs and tools are orchestrated through predefined code paths"; agents are "systems where LLMs dynamically direct their own processes and tool usage."
- Six patterns: chaining, routing, parallelization (sectioning + voting variants), orchestrator-workers, evaluator-optimizer, and the bare augmented-LLM building block.
- Distinguishes orchestrator-workers from parallelization explicitly: "the key difference from parallelization is its flexibility — subtasks aren't pre-defined, but determined by the orchestrator based on the specific input."
- Three core principles: "Maintain simplicity… Prioritize transparency by explicitly showing the agent's planning steps… Carefully craft your agent-computer interface (ACI)."
- Strength: definitional clarity, paradigm-setting taxonomy. Weakness: silent on inter-pattern composition rules and on prompt-level structure of orchestrator brief.

**Anthropic, "How we built our multi-agent research system," Hadfield et al. (Jun 13, 2025)** [HIGH]
- Architecture: LeadResearcher → spawns 3–5 subagents in parallel → CitationAgent runs at end. Plan persisted to **Memory** because "if the context window exceeds 200,000 tokens it will be truncated."
- Quantitative claims:
  - Multi-agent (Opus 4 lead + Sonnet 4 subagents) outperformed single-agent Opus 4 by **90.2%** on internal research eval.
  - Token usage explains **80%** of BrowseComp variance; tool calls + model choice add to 95%.
  - Multi-agent uses ~15× tokens of chat; agents ~4× tokens of chat.
- Synchronous execution acknowledged as a bottleneck: "the lead agent can't steer subagents, subagents can't coordinate, and the entire system can be blocked while waiting for a single subagent."
- Failure modes documented from production: spawning 50 subagents for trivial queries; endless searches for nonexistent sources; SEO content farms preferred over academic PDFs.
- Strength: only canonical source with documented prompt-engineering rules and token economics for an orchestrator-worker production system. Weakness: appendix tips ("subagent output to filesystem") under-developed.

**Anthropic, "Effective harnesses for long-running agents," Young (Nov 26, 2025)** [HIGH]
- Two-agent harness: **initializer** (writes `feature_list.json` with ~200 features all marked `passes:false`, `init.sh`, initial git commit, `claude-progress.txt`) and **coding agent** (one feature per session, commits, updates progress file).
- Documents a footnote disclaiming the "two agents" framing: "We refer to these as separate agents in this context only because they have different initial user prompts. The system prompt, set of tools, and overall agent harness was otherwise identical." This collapses the distinction between "different agent" and "different prompt for a fresh context window."
- Direct architectural anti-pattern named: agents "one-shotting" the app (running out of context mid-implementation) and agents "declaring victory" prematurely.
- Strength: rare published source on cross-context-window orchestration; concrete artifacts and JSON schemas. Weakness: optimized for full-stack web app, generalization unstated.

**Anthropic, "Effective context engineering for AI agents" (Sep 29, 2025)** [HIGH]
- Subagent architecture as one of three context-pressure relief valves alongside compaction and structured note-taking. Quoted: "Each subagent might explore extensively, using tens of thousands of tokens or more, but returns only a condensed, distilled summary of its work (often 1,000-2,000 tokens)."
- Decision rule for which technique: "Compaction maintains conversational flow… Note-taking excels for iterative development with clear milestones… Multi-agent architectures handle complex research and analysis where parallel exploration pays dividends."
- Goldilocks principle for system prompts: avoid "brittle if-else hardcoded" and "overly general or falsely assume shared context."

**Cognition, "Don't Build Multi-Agents," Yan (Jun 12, 2025)** [HIGH]
- Two principles, framed in source vocabulary:
  - Principle 1: "Share context, and share full agent traces, not just individual messages."
  - Principle 2: "Actions carry implicit decisions, and conflicting decisions carry bad results."
- The **Flappy Bird example** is the load-bearing illustration: parallel subagents build a Mario-styled background and a non-game-asset bird because "any number of details could have consequences on the interpretation of the task."
- Recommendation: "the simplest way to follow the principles is to just use a single-threaded linear agent."

**Cognition, "Multi-Agents: What's Actually Working," Yan (Apr 22, 2026)** [HIGH] [new]
- Explicit walkback: "we've begun to deploy multi-agent systems that actually work in practice… setups where multiple agents contribute intelligence to a task while writes stay single-threaded."
- Three working patterns:
  1. **Code-Review-Loop** with deliberate clean context: "this technique to work best when the coding and review agents do not share any context beforehand," justified by Context Rot research.
  2. **Smart-Friend** tool: weak primary calls strong model. Cross-frontier (Claude+GPT) works; weak-primary-strong-secondary "is still an open problem, and we think it's a training one."
  3. **Manager Devin** spawning child Devins via internal MCP for multi-PR scope.
- Anti-pattern named: "the unstructured-swarm approach, arbitrary networks of agents negotiating with each other, is mostly a distraction. The practical shape is map-reduce-and-manage."

**Microsoft Agent Framework orchestrations** [HIGH]
- Five patterns: sequential, concurrent, handoff (mesh topology, agents exchange via tool calls), group chat (manager selects speaker), Magentic (manager builds **task ledger** dynamically, AutoGen-derived).
- Cost rule: "Magentic orchestrations are the most variable because the manager agent iterates until it builds a viable plan."
- Handoff is structurally distinct from manager: "Internally, the handoff orchestration is implemented using a mesh topology where agents are connected directly without an orchestrator." Context broadcast across all participants by default.

**OpenAI, "A practical guide to building agents"** [HIGH]
- Two patterns: **Manager (agents-as-tools)** and **Decentralized (handoffs)**. Direct quote: "In the manager pattern, edges represent tool calls whereas in the decentralized pattern, edges represent handoffs that transfer execution between agents."
- Strong recommendation to start single-agent: "A single agent can handle many tasks by incrementally adding tools."
- Code-first emphasis vs declarative graphs: "this approach can quickly become cumbersome and challenging as workflows grow more dynamic."

**Yao et al., ReAct (arXiv:2210.03629)** [HIGH] — Thought→Action→Observation triples; the canonical loop primitive that all subsequent harnesses (smolagents, Anthropic research subagent OODA loop, 12-Factor agentic loop) inherit.

**Shinn et al., Reflexion (arXiv:2303.11366)** [HIGH] — Verbal RL: "Reflexion converts binary or scalar feedback from the environment into verbal feedback in the form of a textual summary, which is then added as additional context for the LLM agent in the next episode." Distinct from evaluator-optimizer: Reflexion is **across trials**, evaluator-optimizer is **within a trial**.

**Wang et al., Plan-and-Solve (arXiv:2305.04091)** [HIGH] — Two components: "first, devising a plan to divide the entire task into smaller subtasks, and then carrying out the subtasks according to the plan." The plan is the persistent artifact the verify step references; substrate underweighted that plan persistence is the architectural commitment, not the wording of the prompt.

**HumanLayer, 12-Factor Agents** [HIGH] — Factors 8 ("Own your control flow"), 10 ("Small, focused agents"), and 12 ("Make your agent a stateless reducer") most directly govern orchestration. Position: "Most of the products out there billing themselves as 'AI Agents' are not all that agentic. A lot of them are mostly deterministic code, with LLM steps sprinkled in at just the right points."

#### 2.1.3 Patterns and primitives at depth

**Orchestrator-workers prompt structure (Anthropic research system).** The lead agent's brief to each subagent must contain four fields, in source vocabulary: **objective**, **output format**, **guidance on tools and sources**, **clear task boundaries**. The lead agent's own system prompt embeds **scaling rules** (1 agent / 3–10 tool calls for fact-finding; 2–4 / 10–15 for comparisons; >10 for complex research) and **search heuristics** (start broad, narrow down). The lead persists its plan to a `Memory` tool/file before fan-out because the 200k context can be truncated. Subagents run an OODA loop with **interleaved thinking** (extended thinking after each tool result). Return values are condensed summaries (1–2k tokens per subagent in Anthropic's context engineering essay), with large artifacts written directly to filesystem and only references returned to lead.

```
LEAD AGENT (Opus)                         SUBAGENT (Sonnet, ×3-5 parallel)
───────────────────────────               ───────────────────────────────
[plan written to Memory]                  [system prompt: OODA + tool docs]
   │                                          │
   ├─ spawn(brief_1) ──────────────────────►  observe → orient → decide → act (×N)
   │     {objective, format,                  │
   │      tools, boundaries}                  │
   ├─ spawn(brief_2) ──────────────────────►  …
   │                                          │
   │   ◄── condensed summary (1-2k tokens) ───┤
   │   ◄── condensed summary ─────────────────┤
   │   ◄── filesystem artifact reference ─────┤
   │
   ├─ synthesize / decide more research?
   │
   └─ CitationAgent (sequential, post-loop)
```

**Mapping the three taxonomies.**

| Anthropic (BEA) | Microsoft Agent Framework | OpenAI Practical Guide | Notes |
|---|---|---|---|
| Prompt chaining | Sequential | (single-agent w/ tools, looped) | Direct match Anthropic↔MS |
| Routing | (no first-class) | (single-agent triage) | Routing absent in MS taxonomy; OpenAI subsumes into single-agent |
| Parallelization (sectioning) | Concurrent | (no first-class) | OpenAI does not name; emerges via `asyncio.gather` of agent.as_tool() |
| Parallelization (voting) | (no first-class) | (no first-class) | Self-consistency primitive only in Anthropic taxonomy |
| Orchestrator-workers | Group Chat / Magentic | Manager (agents-as-tools) | Magentic adds dynamic task ledger; OpenAI manager is closest equivalent |
| Evaluator-optimizer | (no first-class) | (no first-class) | Distinct from Reflexion; closest analogue is maker-checker |
| (no first-class) | Handoff | Decentralized | Mesh topology, no central manager |
| (no first-class) | Magentic | (no first-class) | Dynamic plan ledger; AutoGen lineage |

What's missing in each:
- **Anthropic** lacks an explicit *handoff/decentralized* pattern.
- **Microsoft** lacks routing-as-classifier and voting; both expressible but unnamed.
- **OpenAI** lacks parallelization (no sectioning/voting), evaluator-optimizer, and Magentic-style dynamic task ledgers.

#### 2.1.4 Tradeoffs at depth

| Axis | Single-agent | Orchestrator-workers | Decentralized handoff |
|---|---|---|---|
| Cost | 1× baseline | ~15× chat tokens (Anthropic data) | ~4–8× chat tokens (estimate) |
| Latency | Sequential, slow on breadth | Parallel fan-out cuts time up to 90% on complex queries (Anthropic) | Sequential by handoff edges |
| Reliability | Highest context coherence (Cognition) | Lower; coordination errors | Lowest; mesh broadcasting fragile |
| Debuggability | Single trace | Per-subagent traces, harder root-cause | Hardest: distributed state across mesh |
| Autonomy | Bounded by context window | High on parallelizable tasks | High on triage |
| Lock-in | Low | Medium (orchestrator prompts are project-specific) | High if framework manages mesh |
| Cognitive overhead | Lowest | Highest at first; standardizes once brief shape is fixed | High; agent boundaries must be well-defined |

Contested tradeoff: **single vs multi for coding.** Anthropic explicitly excludes coding from multi-agent recommendations: "most coding tasks involve fewer truly parallelizable tasks than research." Cognition agrees on the writer side ("writes stay single-threaded") but adds a multi-agent code-review pattern with **deliberately disjoint context**. Both positions cited; resolution is task-decomposition-dependent, not ideology-dependent.

#### 2.1.5 Failure modes in the field

| Mode | Source | Status |
|---|---|---|
| Subagent spawning explosion (50 subagents for trivial query) | Anthropic Multi-Agent Research System | Mitigated via scaling rules in lead prompt |
| Subagent task duplication ("3 agents on 2025 chip supply") | Anthropic | Mitigated via "objective + boundaries" brief |
| SEO content-farm preference over authoritative sources | Anthropic | Mitigated via source quality heuristics in prompt |
| Parallel-writer style/edge-case conflicts (Flappy Bird) | Cognition | Open; Cognition recommends single-threaded writes |
| Premature victory declaration in long-running coding | Anthropic Long-Running Harness | Mitigated via JSON feature list with `passes:false` initial state |
| Mid-implementation context overflow | Anthropic Long-Running Harness | Mitigated via incremental progress + commit-and-document |
| Synchronous fan-out blocking on slow subagent | Anthropic Multi-Agent Research System | **Open** — async noted as future work |
| Compaction loses subtle context | Anthropic Context Engineering | Open — recommend tuning recall first, then precision |

#### 2.1.6 Open questions and unresolved debates

- Asynchronous subagent execution with steering: how does the lead intervene without breaking subagent context? Anthropic flags this as future work.
- The bridging case in the Cognition–Anthropic debate: when does a writer-subagent become acceptable? Cognition's manager-Devin spawning child-Devins suggests the answer is "when scope is large enough that single-threaded becomes infeasible AND each child's scope is bounded enough that decisions don't interlock," but no operational threshold is published.
- Whether evaluator-optimizer should share context with optimizer. Cognition's review-loop says no; Anthropic's BEA is silent.

#### 2.1.7 For-the-builder implications
Build the lead-and-workers pattern with the **four-field brief** as a contract object (`objective`, `output_format`, `tool_guidance`, `boundaries`) and persist it alongside per-subagent results for replay. Encode scaling rules as data, not prompt strings, so they evolve under eval. Defer evaluator-optimizer until a working chain exists; defer handoff/decentralized indefinitely (highest debug cost, lowest payoff for solo founder). Treat any pattern that has writers in parallel as guilty until proven innocent.

---

### 2.2 Topic 2 — Multi-LLM Routing

#### 2.2.1 Topic restatement
Substrate covered routing as a survey topic — classifier-vs-LLM router, cascade architectures, semantic caching as an adjacent capability. The deep-dive surfaces operational thresholds (RouteLLM α-calibration, FrugalGPT confidence cutoffs, xRouter RL reward shape), the cache-invalidation interaction with provider switching, the validated bias-mitigation work building on Zheng et al. for LLM-as-judge, and the per-category cache policy from Wang et al. (2025).

#### 2.2.2 Canonical sources, deeply engaged

**Anthropic BEA — routing pattern** [HIGH] — Routing "directs different types of customer service queries (general questions, refund requests, technical support) into different downstream processes" or "easy/common questions to smaller models like Claude 3.5 Haiku and hard/unusual questions to more capable models like Claude 3.5 Sonnet to optimize cost and speed." Treats routing as a separable workflow primitive with classification done by either an LLM or a traditional classifier.

**Ong et al., RouteLLM (arXiv:2406.18665, ICLR 2025)** [HIGH] — Trained on Chatbot Arena preference data with augmentation. Two key metrics: **CPT** (call-performance threshold, the % calls to strong model needed to recover X% of strong-model performance) and **APGR** (average performance gain recovered). Trained routers achieve "up to 85% [cost reduction] while maintaining 95% GPT-4 performance on widely-used benchmarks like MT Bench"; ">40% cheaper" than commercial offerings at parity. The router exposes a continuous threshold α the operator calibrates against a target cost or quality envelope. Substrate flagged routing thresholds; this provides the calibration mechanism.

**Chen et al., FrugalGPT (arXiv:2305.05176)** [HIGH] — Three strategies: prompt adaptation, LLM approximation, **LLM cascade**. Cascade trains a **scoring function** per stage; if the score on stage-i output exceeds the per-stage threshold, return; else escalate. Reported "match GPT-4 with up to 98% cost reduction or improve accuracy over GPT-4 by 4% with same cost." Per-stage threshold is the operational knob; tuned on holdout per dataset.

**Zheng et al., LLM-as-a-Judge (arXiv:2306.05685)** [HIGH] — Documents three biases: **position** (preferring first-presented answer), **verbosity** (preferring longer answers), **self-enhancement** (model preferring its own outputs). Mitigations validated in source: random swapping for position; explicit length-normalization in prompts; using a different family/scale of model for judging. Subsequent literature (Wang 2023 *Large language models are not fair evaluators*; LLMBar) validates these and adds **formality bias**.

**Anthropic Prompt Caching docs** [HIGH] — Operational details that materially constrain routing+caching composition:
- Hierarchy: **tools → system → messages**, "each level builds upon the previous ones."
- Up to **4 cache breakpoints**; lookback ≈ **20 content blocks** before the breakpoint.
- Minimum cache tokens: **1024** (Claude Opus 4, Sonnet 4, Sonnet 3.7/3.5, Opus 3); **2048** for Haiku; **4096 for Haiku 4.5**.
- Default **5-minute TTL**, refreshed on hit; optional **1-hour TTL** at additional cost.
- Cache write cost is **1.25× base input**, cache read is **0.1× base input** (90% reduction).
- **Critical for parallelism**: "a cache entry only becomes available after the first response begins. If you need cache hits for parallel requests, wait for the first response before sending subsequent requests."
- Provider-side caching is provider-keyed: switching from Anthropic → OpenAI invalidates entirely. OpenRouter implements **provider sticky routing** to keep cache warm across the same provider, but cross-provider switches still cost.

**Wang et al., Cortex (arXiv:2509.17360, Sep 2025)** [HIGH] [new] — Cross-region semantic caching for LLM agents. Introduces **Semantic Element (SE)** with performance-aware metadata (latency, cost, **staticity**) and **Semantic Retrieval Index (Seri)**: ANN candidate selection followed by lightweight LLM-judger validation. Staticity metadata is the load-bearing innovation — it lets the cache distinguish "stock price" (seconds-stale) from "code-pattern question" (months-stale).

**Wang et al., Category-Aware Semantic Caching (arXiv:2510.26835, Oct 2025)** [HIGH] [new] — Per-category similarity thresholds, TTLs, and quotas. Reported category hit-rate ranges:
- Code: 40–60% (dense embedding clusters, power-law repetition)
- Conversation: 5–15% (sparse, near-uniform repetition)
- Stale-content categories (stock data): minutes; code patterns: months
Hybrid HNSW-in-memory + external doc store reduces miss cost from 30 ms to 2 ms, dropping break-even from 15–20% to 3–5%; this lets the long tail be cached instead of excluded. Adaptive load-based thresholds reduce traffic to overloaded models 9–17% (theoretical projection).

**Qian et al., xRouter (arXiv:2510.08439, Oct 2025)** [HIGH] [new] — RL-trained tool-calling router. **Reward = quality − λ·normalized_cost**, "success-gated, cost-shaped." Wrong answer earns 0 reward regardless of cost. Three released variants xRouter-7B-1/2/3 corresponding to three λ settings. Training catalog perturbs prices to prevent overfit. Operates over 20+ LLMs via LiteLLM. The RL setup bypasses the need for hand-tuned thresholds — the router learns when to answer directly vs delegate.

**LiteLLM Anthropic provider docs** [MODERATE] — Unified provider interface; relevant here as the substrate-level fallback chain mechanism. Composition implication: LiteLLM-mediated fallback typically *bypasses* provider-specific prompt caching (cache headers may not be propagated identically across providers).

#### 2.2.3 Patterns and primitives at depth

**Operational defaults observed.**

| Router | Decision signal | Default threshold | Tuning lever |
|---|---|---|---|
| RouteLLM (matrix factorization) | Predicted strong-model win-prob | α calibrated to target % strong-model calls | α ↑ → more strong calls, higher quality, higher cost |
| FrugalGPT cascade | Per-stage scoring-model confidence | Stage-specific, learned on holdout | Per-stage threshold + stage ordering |
| CARGO | Embedding regressor predicted gap | Confidence-aware; binary classifier fallback when uncertain | Per-category regressor (math/code/reasoning/summary/creative) |
| xRouter | RL policy | Implicit (learned) | λ (cost penalty coefficient): 1/2/3 variants |
| Anthropic BEA routing | Classifier output | Operator-defined per category | Classifier model + category labels |

**Routing + prompt caching + fallback composition order.** The dependency order is forced by cache locality:

```
Request
  │
  ▼
[1] Semantic cache lookup (category-aware threshold)   ← short-circuits on hit
  │ miss
  ▼
[2] Router classifies → primary model selection
  │
  ▼
[3] Primary model call WITH provider-native prompt cache
  │ failure (5xx, rate-limit, content-policy)
  ▼
[4] Fallback chain: same-provider model → cross-provider model
        ⚠ cross-provider invalidates prompt cache → cost ↑
  │
  ▼
[5] On success, write to semantic cache with TTL by category
```

Naive composition footguns:
- Re-routing on every request *without* sticky session breaks prompt cache even within a provider.
- Semantic cache layered *after* router means each route gets its own cache namespace; cache hit-rate drops to per-route hit-rate. Place semantic cache *before* router for global hits.
- Fallback to a different family resets prompt-cache write cost; for a 100k-token system prompt at $3/MT, fallback adds ~$0.30 per first-call recovery on Sonnet-tier vs ~$0.03 on cache-hit.

**LLM-as-judge bias mitigations validated in subsequent work.**

| Bias (Zheng) | Mitigation | Validation |
|---|---|---|
| Position | Random swap; report agreement only when both orders agree | Wang 2023 (arXiv:2305.17926); now standard |
| Verbosity | Length normalization in prompt; rubric scoring | Saito 2023; LLMBar |
| Self-enhancement | Cross-family judge (e.g., GPT-4 judge of Claude output) | Standard in Anthropic research-system eval and elsewhere |
| Formality | (Added by post-Zheng work) | LLMBar; PandaLM |

#### 2.2.4 Tradeoffs at depth

| Axis | Classifier router | LLM router (RouteLLM/CARGO) | RL router (xRouter) |
|---|---|---|---|
| Latency overhead | µs–ms (embedding + lookup) | 50–200 ms (regressor or small model) | Variable; 7B model in front |
| Cost overhead | Negligible | Minor | 7B inference cost per request |
| Accuracy ceiling | Limited by label space | Arena-quality calibration | Highest reported on diverse benchmarks |
| Adapt to new model | Retrain | Re-train regressor | Refresh catalog, re-RL |
| Operational simplicity | Highest | Medium | Lowest (RL infra) |

Contested: **rule-based vs learned routing.** xRouter argues "static escalation rules and keyword heuristics under-utilize this spectrum." FrugalGPT shows learned cascade thresholds outperform any single model. Counter (BEA): for many production cases, "classification can be handled accurately, either by an LLM or a more traditional classification model/algorithm." Resolution depends on label-space stability: if categories are stable and small, classifier wins on operational simplicity; if open-ended, learned routing wins.

#### 2.2.5 Failure modes in the field

| Mode | Source | Status |
|---|---|---|
| Cross-provider fallback invalidates prompt cache | Anthropic docs + OpenRouter sticky-routing rationale | Mitigated via provider-sticky; cross-provider unavoidable |
| Concurrent parallel requests miss cache before warm-up | Anthropic prompt caching docs | Mitigated via warm-up call before fan-out |
| Position-bias judge bias inflates first-presented model scores | Zheng et al. | Mitigated via random swap |
| Semantic cache false positives on dense code-query space | Wang 2510.26835 | Mitigated via category-specific threshold |
| Static cascade threshold drifts with model upgrades | FrugalGPT lineage | Open; periodic re-calibration on rolling holdout |
| Cache stampede on TTL expiry under high concurrency | General; not LLM-specific | Mitigated via probabilistic early refresh, single-flight |

#### 2.2.6 Open questions and unresolved debates
- Whether semantic cache and prompt cache should share an embedding key. No published architecture combines both layers cleanly; an embedding-keyed prefix-aware cache is, as of May 2026, an open design.
- xRouter-style RL routing under **distribution shift** (new models added monthly): how often must the policy be retrained? The paper perturbs costs but not capabilities; this remains thin.
- Calibration of category-aware thresholds across heterogeneous workloads with overlapping classes (e.g., a code-explanation question that is conversational in form).

#### 2.2.7 For-the-builder implications
For a solo founder: implement a **two-tier router** — small classifier for stable categories, fallback to LLM-router on `unknown`. Wire **provider-sticky session keys** into the harness (request → session → provider). Implement **semantic cache before router** with category-aware thresholds (default: code 0.92, conversation 0.85, factual 0.88; tune on production traffic). Use Anthropic prompt caching with one cache breakpoint at end-of-system-prompt for short-term wins; revisit category-aware semantic caching once you have ≥10k requests of category-labeled traffic. Defer xRouter-style RL routing until you have a stable model catalog and labeled win-loss data.

---

### 2.3 Topic 3 — Sub-agents and Single-File Agents

#### 2.3.1 Topic restatement
Substrate (§2.6) covered sub-agents (Anthropic, smolagents) and SFAs (Disler) at survey depth. The deep-dive specifies the sub-agent contract from the Anthropic research system, characterizes the SFA scaling ceiling from Disler's reference set, and reconciles the two via an SFA-as-tool composition pattern.

#### 2.3.2 Canonical sources, deeply engaged

**Anthropic Multi-Agent Research System (Jun 13, 2025)** [HIGH] — Sub-agent contract has four input fields (objective, output format, tool/source guidance, boundaries) and a return-shape that is a **condensed summary** with optional filesystem artifact references. Lead-spawning rules embedded in lead's system prompt. Subagent's own system prompt embeds OODA loop. The "subagent output to filesystem" appendix tip: "implement artifact systems where specialized agents can create outputs that persist independently. Subagents call tools to store their work in external systems, then pass lightweight references back to the coordinator."

**Anthropic, Effective Context Engineering for AI Agents** [HIGH] — Quantifies the asymmetry: "Each subagent might explore extensively, using tens of thousands of tokens or more, but returns only a condensed, distilled summary of its work (often 1,000-2,000 tokens)." Names the architectural benefit: "clear separation of concerns — the detailed search context remains isolated within sub-agents."

**disler/single-file-agents** [HIGH] — File naming convention `sfa_<capability>_<provider>_v<version>.py`. Each file is one Python module with `uv` script-level dependency declarations; runs as `uv run sfa_duckdb_anthropic_v2.py -d ./data/analytics.db -p "..." -c 10`. Default compute loops `-c 10`. Disler's own README disclaimer: "We're using the term 'agent' loosely for some of these SFA's. We have prompts, prompt chains, and a couple are official Agents."

**Hugging Face smolagents** [HIGH] — Key API: `managed_agents=[web_agent]` parameter on a `CodeAgent`. Each managed agent exposes `name` and `description` baked into the manager's system prompt. The library codebase is "<1,000 lines" (claim repeated in README). Two agent classes: `CodeAgent` (writes Python tool calls) and `ToolCallingAgent` (writes JSON). Maps cleanly to OpenAI's `agent.as_tool()` and Microsoft's group-chat with manager.

**Simon Willison weblog on agent patterns** [MODERATE] — Repeatedly distinguishes agent variants; coined the practical definition Anthropic now references: "LLMs autonomously using tools in a loop." Sub-agent pattern characterization in his Jun 14, 2025 post: "certain coding research tasks were passed off to a 'sub-agent' using a tool call."

**HumanLayer 12-Factor Agents (Factor 10)** [HIGH] — "Small, focused agents — 3-10 steps max for reliability." Names the SFA-equivalent principle without using the term: "Instead of building one massive agent, successful teams build small, focused agents."

#### 2.3.3 Patterns and primitives at depth

**Sub-agent brief schema (extracted from Anthropic research-system prose).**

```
brief := {
  objective:        string,            // single goal; not "research X"
  output_format:    schema,             // structured return contract
  tools_allowed:    [tool_id, ...],     // narrow set
  source_guidance:  string,             // e.g., "prefer academic PDFs"
  boundaries:       {
    token_budget:   int,
    tool_calls_max: int,                // 3-10 / 10-15 per Anthropic scaling rules
    time_budget_s:  int (optional),
    out_of_scope:   string (optional),  // explicit non-goals
  }
}
```

**SFA-as-tool composition.**

```
PARENT (orchestrator)
  │
  ├── tool: invoke_sfa
  │     args: {sfa_path, prompt, compute_loops, args}
  │     impl: subprocess.run(["uv", "run", sfa_path, "-p", prompt, "-c", str(loops)])
  │     contract:
  │       stdout    → structured result (or final answer text)
  │       stderr    → diagnostic stream
  │       exit_code → 0 success / nonzero error
  │       timeout   → SIGTERM, parent classifies as transient/terminal
  │     observability: parent captures (stdout, stderr, duration, tokens-if-emitted)
```

This composition makes an SFA into a **tool** the parent agent can call — preserving SFA's filesystem-isolation and per-process ephemerality while letting a smolagents-style or Anthropic-style orchestrator route to it. The contract is intentionally OS-level (subprocess) rather than in-process to preserve SFA's "single file, single capability, embedded deps" property.

**SFA ceiling.** Empirically inferred from Disler's repo: SFA stops scaling when (a) it needs more than **one tool family** (e.g., DuckDB + email + Slack); (b) it needs **persistent state across invocations** (an SFA is born and dies per call); (c) compute loops would exceed ~10–20 (debug burden becomes unmanageable in single file); (d) tool-result schemas need cross-validation (multi-tool composition logic). Natural escalation path: **SFA → SFA-as-tool → smolagents managed_agents → Anthropic-style sub-agent with brief + filesystem artifacts**.

#### 2.3.4 Tradeoffs at depth

| Axis | SFA | Sub-agent (in-harness) | Specialist multi-file agent |
|---|---|---|---|
| Cold-start latency | ~100ms (uv) | ~ms (in-process) | ~ms |
| Isolation | Process-level (best) | Context-window only | Context-window only |
| Composability | Tool-call shape only | First-class | First-class |
| Debuggability | Best (single file, plain stdin/stdout) | Medium (parent must log subagent traces) | Medium |
| State | Stateless | Stateful within parent run | Stateful |
| Reusability | Highest (drop into any harness) | Bound to harness | Bound to package |
| Observability cost | Parent must capture stdout/stderr | Parent emits structured spans | Built-in tracing |

What context isolation buys beyond "don't blow parent's context" (per Anthropic + Cognition convergent reasoning):
- **Reliability**: clean context reviewer catches bugs the coding agent cannot (Cognition Devin Review case: 2 bugs/PR average, 58% severe).
- **Parallelism**: independent contexts ⇒ trivial fan-out without state coordination.
- **Debuggability**: bounded blast radius; per-subagent trace replay possible.
- **Faithfulness over accuracy** (specifically): a 2026 multi-model self-consistency analysis (arXiv:2601.06423) found Claude Opus 4.5 *gained faithfulness* (0.270 → 0.891) while *losing* accuracy at N=5 — clean context shifts the operating point.

#### 2.3.5 Failure modes in the field

| Mode | Source | Status |
|---|---|---|
| Subagent runaway tool use | Anthropic | Mitigated via tool-call cap in brief |
| Subagent task drift (chases tangent) | Anthropic | Mitigated via explicit boundaries field |
| SFA orphan process (parent dies) | General | Mitigated via subprocess timeout + group-kill |
| Stdout pollution corrupting structured return | Inferred from Disler patterns | Mitigated via separate stderr channel for diagnostic |
| Sub-agent context bleed via shared filesystem artifacts | Inferred | **Open**; namespaced artifact paths recommended |
| Compaction loses subagent's intermediate findings on parent compaction | Anthropic Context Engineering | Open; tune compaction prompt for subagent-output preservation |

#### 2.3.6 Open questions and unresolved debates
- Where does the SFA end and a "real agent" begin? Disler explicitly equivocates ("loosely"). The substrate noted this; deep-dive resolves: a file is an SFA iff (1) one capability, (2) embedded deps, (3) ephemeral, (4) callable as tool by stdin/stdout/exitcode contract. Multi-capability or stateful escalates out.
- Whether sub-agent failure should propagate as exception or be swallowed and reported as text. Anthropic harness lets the model "know when a tool is failing and adapt" (suggests text). HumanLayer Factor 9 "Compact Errors into Context Window" agrees.

#### 2.3.7 For-the-builder implications
Standardize on a **brief object** as a Python dataclass; pass to either in-process subagents or to SFA subprocesses via JSON-on-stdin. Implement subagents' return as JSON with `summary`, `artifacts: [path...]`, `metrics: {tokens, tool_calls, duration_s}`. Keep SFAs for hermetic single-capability work (DuckDB query, semantic search over a corpus, code-formatting). Promote to sub-agent only when parent needs to fan out 3+ in parallel or share short-lived in-memory state.

---

### 2.4 Topic 4 — Parallelism

#### 2.4.1 Topic restatement
Substrate (§2.7) covered parallelism patterns at survey depth. The deep-dive nails down concurrency caps (Anthropic 3–5 documented), prompt-caching interaction with parallel fan-out (warm-up requirement), self-consistency saturation curves on production tasks, and the merger-bottleneck pattern.

#### 2.4.2 Canonical sources, deeply engaged

**Anthropic BEA — parallelization** [HIGH] — Names two sub-patterns: **sectioning** (independent subtasks split) and **voting** (same task multiple times, aggregate). Voting examples include "reviewing a piece of code for vulnerabilities, where several different prompts review and flag the code." This frames voting as both ensemble accuracy and false-positive/negative balancing.

**Anthropic Multi-Agent Research System** [HIGH] — Documented concurrency: "lead agent spins up 3-5 subagents in parallel rather than serially; (2) the subagents use 3+ tools in parallel. These changes cut research time by up to 90% for complex queries." Synchronous bottleneck explicitly named (see §2.1.5). Cap is **prompt-engineered into the lead**, not framework-enforced.

**Wang et al., Self-Consistency (arXiv:2203.11171)** [HIGH] — Ensemble strategy: sample diverse reasoning paths, return most consistent answer. Original benchmarks: GSM8K +17.9%, SVAMP +11.0%, AQuA +12.2%. Originally tested up to N=40.

**Loo, Reevaluating Self-Consistency Scaling (arXiv:2511.00751, Nov 2025)** [HIGH] [new] — On Math-500 with Gemini-2.5-Pro and Gemini-2.5-Flash-Lite, "additional agents contribute little to overall performance while significantly increasing token cost." Plateau is reached at low N; high-sample configs not justified.

**Wang et al., How Effective Is Self-Consistency for Long-Context (arXiv:2411.01101)** [HIGH] [new] — "Clear diminishing return with an increased number of self-consistency samples." Q-Doc-Q format gives +10–15% only when relevant info is at the start of context.

**Sample Complexity / Best-of-n vs Self-Consistency (arXiv:2506.05295, Jun 2025)** [HIGH] [new] — Theoretical separation: self-consistency requires **Θ(1/Δ²)** samples vs best-of-n's **Θ(1/Δ)** for the same correctness probability, where Δ is the gap between most likely and second-most likely answer. Practical implication: with a verifier, best-of-n is quadratically more sample-efficient than self-consistency.

**Anthropic Prompt Caching docs** [HIGH] — Re-engaged here for the parallel-specific implication: "If you need cache hits for parallel requests, wait for the first response before sending subsequent requests."

**AWS Builders' Library — Timeouts, Retries and Backoff with Jitter** [HIGH] — Three primitives: timeouts on every remote call (connection + request); retries with **token-bucket budget** to prevent retry storms (built into AWS SDK 2016); **exponential backoff with full jitter** to avoid synchronized retry waves. Direct quote: "If errors are caused by load, retries can be ineffective if all clients retry at the same time. To avoid this problem, we employ jitter."

#### 2.4.3 Patterns and primitives at depth

**Documented concurrency caps.**

| Source | Cap | Mechanism |
|---|---|---|
| Anthropic Research System | 3–5 subagents per fan-out | Prompt-engineered scaling rule in lead |
| Anthropic Research System | 3+ tool calls in parallel within subagent | Native parallel tool calling |
| smolagents `CodeAgent` | `max_tool_threads` (ThreadPoolExecutor default) | Constructor parameter |
| OpenAI Agents SDK | `Runner.run` with `asyncio.gather` over `agent.as_tool` | Application-level |

**How production teams set the cap (synthesizing Anthropic prose + general practice).**
- **Rate-limit derived**: `N_max = floor(provider_rpm / per_subagent_rpm * safety_margin)`. For Anthropic on Tier 4 with parallel tool calls, ~5 subagents × ~6 calls/min ≈ 30 RPM headroom inside a typical 2000 RPM ceiling.
- **Cost-budget derived**: `N_max = floor(per_request_budget / per_subagent_expected_cost)`. With ~15× chat tokens for multi-agent, the budget bound usually binds before rate-limit.
- **Downstream-derived**: if subagents call rate-limited tools (web search APIs, internal services), cap by downstream RPS, not LLM RPS.

**Prompt caching + parallelism: optimized fan-out.**

```
T=0:   Lead emits warm-up call           ──► writes cache (cache_creation_input_tokens)
T=200ms: Lead receives partial response  ◄── cache entry available
T=200ms: Fan out N parallel subagents    ──► all read cache (cache_read_input_tokens)
                                              cost per subagent = 0.1× normal input + new tokens
```

If fan-out launches at T=0 with no warm-up, all N pay full input cost; cache writes race condition produces N independent cache entries (cache fragmentation) that may not even reuse each other.

**Self-consistency / voting saturation on production tasks.** Synthesizing Wang 2022, Loo 2026, Wang 2024:

| N (samples) | Typical accuracy gain (vs N=1) | Notes |
|---|---|---|
| 1 | baseline | |
| 3 | +60–80% of total achievable gain | Fast win |
| 5 | +85–95% of total gain | Practical sweet spot |
| 10 | +95–99% | Diminishing returns clearly visible |
| 20 | +99% | Rarely justified |
| 40 | ceiling | Original paper N; 8× cost vs N=5 |

Production rule: **N=5 with adaptive early-stop** (Adaptive-Consistency, ConSol/SPRT) — if first 3 samples agree, stop; else continue to 5; if 5 still split, fall back to a stronger model. Substrate left optimal-N as an open question; this is the resolution.

**Deadlock-on-shared-rate-limit mitigations.**
1. **Per-sub-agent token bucket**: each subagent gets `(N_total_bucket / N_subagents)` tokens; refill at proportional rate.
2. **Multiple API keys with weighted distribution**: keys assigned per subagent; orchestrator weights by historical success rate.
3. **Local-model fallback**: contention triggers reroute to local Ollama / vLLM-served open-weights model. Cognition's "smart-friend" pattern shows **cross-frontier delegation works**; local fallback is the same shape with weaker downstream.

**Merger bottleneck in fan-in.** When N condensed summaries (1–2k tokens each) total > merger context: hierarchical merge.

```
Subagent results: 12 × 2k tokens = 24k
                              │
                              ▼
First-stage merger × 3 (each merges 4 inputs → 4k summary)
                              │
                              ▼
Second-stage merger × 1 (merges 3 × 4k → 6k final synthesis)
```

Anthropic's filesystem-artifact pattern is the alternative: subagent writes raw output to disk, returns path; merger reads only on demand.

#### 2.4.4 Tradeoffs at depth

| Axis | Sectioning | Voting / Self-consistency | Best-of-N w/ verifier |
|---|---|---|---|
| Cost | N × subtask cost | N × full-task cost | N × full-task cost + verifier cost |
| Accuracy gain | Coverage of breadth | Variance reduction; saturates ~N=5 | Best-known: Θ(1/Δ) samples |
| Latency | max(subagent latency) | max(subagent latency) | max(subagent latency) + verifier |
| Cache friendliness | High (each section different prefix) | Highest (identical prefix → cache hits after warm-up) | Highest |
| Failure tolerance | Lose section ⇒ partial result | Lose votes ⇒ smaller ensemble | Lose samples ⇒ fewer candidates |

#### 2.4.5 Failure modes in the field

| Mode | Source | Status |
|---|---|---|
| Synchronized retry storm on shared rate limit | AWS Builders' Library | Mitigated via exponential backoff with full jitter |
| Cache miss on parallel fan-out without warm-up | Anthropic docs | Mitigated via warm-up call |
| Slow-subagent blocks entire fan-out | Anthropic Research System | Open; async noted as future work |
| Voting agreement on wrong answer (correlated errors) | General | Mitigated via diverse prompts/models in voting set |
| Merger context overflow at high N | Anthropic appendix | Mitigated via hierarchical merge or filesystem artifacts |
| Token bucket starvation when one subagent dominates | Inferred | Mitigated via per-subagent bucket allocation |

#### 2.4.6 Open questions and unresolved debates
- The **async-with-steering** problem: how does the lead intervene mid-subagent without breaking subagent context? Anthropic explicitly flags this.
- Whether voting and best-of-N should be unified under a single primitive in the harness (they share fan-out shape, differ only in aggregation).
- Optimal N as a function of problem difficulty (Δ): theory says best-of-N is quadratically better; production tooling rarely exposes the choice.

#### 2.4.7 For-the-builder implications
Default fan-out cap = **5** (matching Anthropic). Always issue **one warm-up call** before parallel fan-out off a shared prefix. Implement **per-subagent token bucket** with central RPM ceiling derived from provider rate limit; back off with **full jitter** on 429s. Use **N=5 voting with early-stop** for tasks where you have a verifier; use **best-of-N** with verifier where one exists (it is provably more sample-efficient). Expose merger as a separate role with explicit hierarchical-merge fallback when input tokens exceed threshold; default to filesystem-artifact pattern for outputs > 4k tokens per subagent.

---

## 3. Cross-Topic Synthesis

### 3.1 Architectural couplings

The four topics are not independent. The choice in any one constrains the others:

```
                    ┌───────────────────────────────┐
                    │  Orchestration pattern        │
                    │  (single / orchestrator-      │
                    │   workers / handoff / etc.)   │
                    └──────┬───────────────┬────────┘
                           │               │
                determines fan-out   determines who
                shape & cap          decides routing
                           │               │
                           ▼               ▼
                    ┌────────────┐   ┌────────────┐
                    │ Parallelism│   │  Routing   │
                    │  (N, type) │   │ (M models) │
                    └─────┬──────┘   └──────┬─────┘
                          │                 │
                  shapes context    determines cache
                  isolation needs   keying & TTL
                          │                 │
                          └─────┬───────────┘
                                ▼
                      ┌──────────────────┐
                      │ Sub-agents / SFA │
                      │  (isolation,     │
                      │   compose unit)  │
                      └──────────────────┘
```

Concrete couplings:
- Orchestrator-workers + parallelism = ~15× tokens but ~90% time savings (Anthropic).
- Routing + parallelism + prompt cache: requires warm-up call before fan-out *and* provider-sticky session for cache preservation. Composing all three naively leaves cache hit rate near zero.
- Sub-agent context isolation + parallelism: enables Cognition's clean-context-reviewer pattern (no shared context = better bug detection).
- Single-threaded writes + multi-source intelligence = Cognition's converged 2026 position; this maps to **Anthropic's BEA orchestrator-workers used for read-only work**.

### 3.2 Source-level convergence and divergence

**Anthropic BEA (Dec 2024) vs Multi-Agent Research System (Jun 2025).** No contradiction; the latter is a worked instance of orchestrator-workers from BEA. MARS adds: (a) explicit token economics; (b) prompt-engineered scaling rules; (c) filesystem-artifact escape valve for fan-in; (d) async-execution as future work; (e) `CitationAgent` as a sequential post-processing role demonstrating evaluator-optimizer-adjacent role separation.

**OpenAI manager pattern vs Anthropic orchestrator-workers.** Functionally identical: a central LLM invokes specialized sub-LLMs as tools, retains the conversation thread, synthesizes results. Differences are nominal rather than architectural — OpenAI's `agent.as_tool()` is a code-level mechanism; Anthropic's `Task` tool with subagent spawning is the same shape with different surface.

**Cognition position over time.** The 10-month arc from "Don't Build Multi-Agents" (Jun 2025) to "Multi-Agents: What's Actually Working" (Apr 2026) is not a reversal; it is a refinement. The original target was *parallel writers*, never readers; the 2026 update makes this explicit by deploying "setups where multiple agents contribute intelligence to a task while writes stay single-threaded." Anthropic's research system was always parallel readers. **The two companies were never disagreeing** on the same architectural unit; the perceived disagreement was a category error amplified by the 24-hour publication gap. This deep-dive resolves that error definitively.

**Microsoft vs Anthropic vs OpenAI taxonomies.** Anthropic's six-pattern taxonomy is the most comprehensive at the *primitive* level. Microsoft's five-pattern taxonomy adds Magentic (which is a runtime-dynamic orchestrator-workers) but lacks evaluator-optimizer and voting. OpenAI's two-pattern taxonomy is the simplest and is correct as a *user-facing* abstraction but elides voting, sectioning, and evaluator-optimizer.

### 3.3 Decision points the cluster collectively defines

| Decision | Default for solo founder | Threshold to revisit |
|---|---|---|
| Single-agent vs orchestrator-workers | Single-agent | Task is breadth-first research over many sources |
| Orchestrator-workers vs handoff | Orchestrator-workers | User-facing triage with clear specialist domains |
| Sub-agent vs SFA | SFA for one-capability tools | Need parallel fan-out OR need shared in-memory state |
| Voting N | 5 with early-stop | Verifier exists → switch to best-of-N |
| Prompt-cache breakpoint | One at end of system prompt | Tool definitions stable AND >2 distinct stable sections |
| Routing classifier vs LLM router | Classifier on 5–10 stable categories | Open-ended categories OR cost gap > 10× across models |
| Semantic cache threshold | 0.88 uniform | ≥10k labeled requests → switch to category-aware |
| Fan-out concurrency | 3 | Per-subagent token budget + rate-limit headroom both safe at higher N |
| Fallback chain | Same-provider model variants | Cross-provider fallback is necessary even with cache cost |

---

## 4. Open Questions and Recommended Next Probes

1. **Asynchronous subagent steering.** Anthropic flagged this as future work. Probe: Cognition's manager-Devin internal MCP protocol — published only in summary form. Recommend re-checking Cognition blog and Devin docs in 3–6 months for protocol-level disclosure.
2. **Cross-provider prompt-cache portability.** Whether OpenRouter's sticky-routing extends to a proper prefix-aware cache that survives provider switching is unclear. Probe: OpenRouter docs + LiteLLM caching docs deeper read.
3. **Optimal N as a function of Δ.** Theory (arXiv:2506.05295) gives the bound; tooling does not yet expose adaptive N. Probe: ConSol (arXiv:2503.17587) and Adaptive-Consistency reference implementations for production deployment patterns.
4. **Sub-agent + SFA composition observability.** No canonical source documents the trace-stitching pattern when a sub-agent shells out to an SFA. Probe: smolagents tracing internals, OpenAI Agents SDK tracing semantics for `agent.as_tool` invoked subprocesses.
5. **Cross-frontier "smart friend" routing protocol.** Cognition reports it works but doesn't publish the prompts. Probe: Anthropic "advisor strategy" beta announcement for the inverse direction.
6. **IndyDevDan video sources.** Could not locate dated YouTube videos via search; the GitHub repo and personal channel exist but specific SFA-pattern videos with dates were not surfaced. Mark as gap; substrate-only at video level.

---

## 5. Source Bibliography

1. Anthropic. "Building effective agents." Schluntz, E. & Zhang, B. Dec 19, 2024. anthropic.com/research/building-effective-agents — [deepened]
2. Anthropic. "How we built our multi-agent research system." Hadfield, J., Zhang, B., Lien, K., Scholz, F., Fox, J., Ford, D. Jun 13, 2025. anthropic.com/engineering/multi-agent-research-system — [deepened]
3. Anthropic. "Effective harnesses for long-running agents." Young, J. Nov 26, 2025. anthropic.com/engineering/effective-harnesses-for-long-running-agents — [new]
4. Anthropic. "Effective context engineering for AI agents." Rajasekaran, P., Dixon, E., Ryan, C., Hadfield, J. Sep 29, 2025. anthropic.com/engineering/effective-context-engineering-for-ai-agents — [deepened]
5. Anthropic. "Prompt caching." platform.claude.com/docs/en/build-with-claude/prompt-caching — [deepened]
6. Cognition. "Don't Build Multi-Agents." Yan, W. Jun 12, 2025. cognition.ai/blog/dont-build-multi-agents — [deepened]
7. Cognition. "Multi-Agents: What's Actually Working." Yan, W. Apr 22, 2026. cognition.ai/blog/multi-agents-working — [new]
8. Microsoft. "Workflow orchestrations in Agent Framework." learn.microsoft.com/en-us/agent-framework/workflows/orchestrations — [deepened]
9. Microsoft. "AI Agent Orchestration Patterns." learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns — [new]
10. OpenAI. "A practical guide to building agents." openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents (PDF: cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) — [deepened]
11. Yao, S. et al. "ReAct: Synergizing Reasoning and Acting in Language Models." arXiv:2210.03629. — [substrate]
12. Shinn, N. et al. "Reflexion: Language Agents with Verbal Reinforcement Learning." arXiv:2303.11366. NeurIPS 2023. — [substrate]
13. Wang, L. et al. "Plan-and-Solve Prompting." arXiv:2305.04091. ACL 2023. — [substrate]
14. Wang, X. et al. "Self-Consistency Improves Chain of Thought Reasoning in Language Models." arXiv:2203.11171. — [substrate]
15. Loo, C. "Reevaluating Self-Consistency Scaling in Multi-Agent Systems." arXiv:2511.00751. Nov 2025. — [new]
16. Wang, et al. "How Effective Is Self-Consistency for Long-Context Problems?" arXiv:2411.01101. — [new]
17. "Sample Complexity and Representation Ability of Test-time Scaling Paradigms." arXiv:2506.05295. Jun 2025. — [new]
18. Ong, I. et al. "RouteLLM: Learning to Route LLMs with Preference Data." arXiv:2406.18665. ICLR 2025. — [substrate]
19. Chen, L., Zaharia, M., Zou, J. "FrugalGPT." arXiv:2305.05176. — [substrate]
20. Zheng, L. et al. "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena." arXiv:2306.05685. — [substrate]
21. Ruan, C. et al. "Cortex: Achieving Low-Latency, Cost-Efficient Remote Data Access For LLM via Semantic-Aware Knowledge Caching." arXiv:2509.17360. Sep 2025. — [deepened]
22. Wang, C. et al. "Category-Aware Semantic Caching for Heterogeneous LLM Workloads." arXiv:2510.26835. Oct 2025. — [deepened]
23. Barrak, A. et al. "CARGO: A Framework for Confidence-Aware Routing of Large Language Models." arXiv:2509.14899. Sep 2025. — [deepened]
24. Qian, C. et al. "xRouter: Training Cost-Aware LLMs Orchestration System via Reinforcement Learning." arXiv:2510.08439. Oct 2025. — [deepened]
25. Disler. single-file-agents. github.com/disler/single-file-agents — [deepened]
26. Hugging Face. smolagents. huggingface.co/docs/smolagents (and github.com/huggingface/smolagents) — [deepened]
27. HumanLayer. 12-Factor Agents. github.com/humanlayer/12-factor-agents — [deepened]
28. AWS. "Timeouts, Retries and Backoff with Jitter." Brooker, M. Amazon Builders' Library. aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter — [substrate]
29. Willison, S. "Building effective agents" / "Anthropic: How we built our multi-agent research system." simonwillison.net Dec 20, 2024 / Jun 14, 2025. — [substrate]
30. OpenRouter. "Prompt Caching." openrouter.ai/docs/guides/best-practices/prompt-caching — [new]

---

*End of cluster deep-dive 1 deliverable.*