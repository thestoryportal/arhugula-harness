# Production-Grade Multi-LLM Agent Harnesses (2025–2026): A Source-Grounded Landscape Map

## TL;DR

- **The field has converged on a narrow definition** — "agents are LLMs autonomously using tools in a loop" (Anthropic, "Effective context engineering for AI agents," anthropic.com/engineering/effective-context-engineering-for-aI-agents) [HIGH] — and on a clear architectural split between *workflows* (predefined code paths orchestrating LLM calls) and *agents* (LLMs dynamically directing their own processes). Anthropic's "Building Effective Agents" (Dec 19, 2024, anthropic.com/research/building-effective-agents) is the canonical reference; nearly every other framework (LangGraph, OpenAI Agents SDK, Microsoft Agent Framework, CrewAI, Mastra) reproduces its taxonomy of prompt chaining, routing, parallelization, orchestrator-workers, and evaluator-optimizer [HIGH].
- **The deterministic outer harness is the actual product.** Frontier-model capability is now sufficient that the differentiating engineering work is no longer prompt cleverness but rather context engineering, schema-validated tool contracts, durable execution, observability, and trust boundaries — a position taken explicitly by Anthropic (anthropic.com/engineering/effective-context-engineering-for-ai-agents), HumanLayer's "12-Factor Agents" (github.com/humanlayer/12-factor-agents), and Hamel Husain's eval guidance (hamel.dev/blog/posts/evals-faq) [HIGH]. The "Claude Code harness leak" community analysis and Anthropic's own "Effective harnesses for long-running agents" (anthropic.com/engineering/effective-harnesses-for-long-running-agents) reinforce that the harness — not the model — owns reliability [MODERATE].
- **There is settled practice on the primitives but contested practice on the framing layer.** Settled: prompt caching, structured outputs, MCP for tool plumbing, OpenTelemetry GenAI semantic conventions for traces, Reflexion/evaluator-optimizer for self-correction, sub-agent isolation for context economy, jittered backoff + circuit breakers for reliability. Contested: whether to adopt a framework (LangGraph, CrewAI, Microsoft Agent Framework, Mastra, OpenAI Agents SDK) or build from primitives; whether checkpointing constitutes "durable execution"; whether multi-agent orchestration is worth its 10–15× token amplification for non-research workloads [HIGH on settled items; MODERATE on contested].

---

## 1. Executive Synthesis

The 2025–2026 production-grade multi-LLM agent harness has stabilized around a layered model: a *probabilistic core* (LLM tool-calling loops) wrapped in a *deterministic outer harness* (schemas, sandboxes, gates, ledgers, telemetry). Every credible primary source — Anthropic engineering, the major framework docs, the research literature on Reflexion and ReAct, and the OpenTelemetry GenAI working group — converges on this separation.

Five tectonic shifts define the era:

1. **From prompt engineering to context engineering.** Anthropic now defines context engineering as "the set of strategies for curating and maintaining the optimal set of tokens (information) during LLM inference, including all the other information that may land there outside of the prompts" (anthropic.com/engineering/effective-context-engineering-for-ai-agents) [HIGH]. This reframes the work from "writing the right prompt" to "managing a finite attention budget across a long-running process."

2. **Context rot is empirical, not anecdotal.** Chroma's research on 18 frontier models (trychroma.com/research/context-rot) shows degradation begins well below the advertised context limit, even on simple retrieval tasks, and worsens with distractor density and needle-question dissimilarity [HIGH]. This is the single biggest constraint on long-running agents and motivates compaction, sub-agent fan-out, and just-in-time retrieval.

3. **Tools are a new software paradigm.** Anthropic frames agent tools as "contracts between deterministic systems and non-deterministic agents" (anthropic.com/engineering/writing-tools-for-agents) [HIGH] — different from APIs because the consumer is probabilistic. MCP (modelcontextprotocol.io/specification/2025-06-18) standardizes the wire format, and Anthropic's "Code execution with MCP" post (anthropic.com/engineering/code-execution-with-mcp) demonstrates a 98.7% token reduction (150k→2k) by having agents discover and load tools via filesystem rather than prompt-stuffing [HIGH].

4. **Skills as portable expertise.** Anthropic's Agent Skills (anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — folders containing a `SKILL.md` plus optional scripts and references, loaded via *progressive disclosure* — were published as an open standard on Dec 18, 2025 and adopted across Claude.ai, Claude Code, the Agent SDK, and the API [HIGH].

5. **Multi-agent is a high-cost, high-value pattern, not a default.** Anthropic's "How we built our multi-agent research system" (anthropic.com/engineering/multi-agent-research-system) reports >90% performance gain on breadth-first research vs single-agent, but at ~15× the token cost of a chat interaction and ~4× the cost of a single agent [HIGH]. This pattern excels at parallelizable exploration and is "less effective for tightly interdependent tasks such as coding."

For a solo founder building a local-first heterogeneous-workflow harness, the practical implication is that the moat is the harness design itself — schemas, ledgers, gates, observability — and that the model providers are increasingly providing primitives (prompt caching, structured outputs, batch API, Skills, MCP, code execution) that subsume what frameworks tried to do in 2023–2024.

---

## 2. Sixteen Domain Deep Dives

### 2.1 Orchestration patterns

**Core concepts.** Anthropic's Dec 2024 guide enumerates the canonical workflow patterns: prompt chaining, routing, parallelization (sectioning + voting), orchestrator-workers, and evaluator-optimizer; agents are reserved for "open-ended problems where it's difficult or impossible to predict the required number of steps" (anthropic.com/research/building-effective-agents) [HIGH]. Microsoft Agent Framework formalizes five orchestration patterns explicitly: sequential, concurrent, handoff, group chat, and Magentic (magentic-one-derived, designed for open-ended tasks) (learn.microsoft.com/en-us/agent-framework/workflows/orchestrations) [HIGH]. OpenAI's "A practical guide to building agents" distinguishes the *manager pattern* (central LLM calls specialists as tools) from the *decentralized pattern* (handoffs transfer control) (openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents) [HIGH].

**Plan-Execute-Verify** descends from Plan-and-Solve Prompting (Wang et al., arXiv:2305.04091, 2023) [HIGH]: an explicit plan step ("devise a plan to divide the entire task into smaller subtasks") followed by execution, formalized in LangChain's Plan-and-Execute module. **Single-file agents** (Simon Willison; disler/single-file-agents on GitHub) is a counter-pattern emphasizing that "a single python file" with carefully crafted prompts and uv-managed deps can outperform framework abstractions for scoped tasks [MODERATE].

**Headless/autonomous** corresponds to Anthropic's "agents" definition — once started, "agents plan and operate independently, potentially returning to the human for further information or judgement … gain 'ground truth' from the environment at each step" (anthropic.com/research/building-effective-agents) [HIGH].

**Failure modes.** Anthropic's multi-agent post documents emergent pathologies: "spawning 50 subagents for simple queries, scouring the web endlessly for nonexistent sources, and distracting each other with excessive updates" (anthropic.com/engineering/multi-agent-research-system) [HIGH].

**Measurable metrics.** Token amplification ratio (multi-agent vs single-agent vs chat: Anthropic reports ~4× and ~15× respectively); end-state evaluation success rate (Anthropic explicitly recommends this over turn-by-turn analysis); orchestrator decision accuracy.

**Contested.** Whether multi-agent is generally worth the overhead; Anthropic itself notes it is "less effective for tightly interdependent tasks such as coding" [HIGH]. Simon Willison wrote in Dec 2024 that he was "skeptical … why make your life more complicated by running multiple different prompts in parallel when you can usually get something useful done with a single, carefully-crafted prompt against a frontier model" before being persuaded by Anthropic's results (simonwillison.net/2025/Jun/14/multi-agent-research-system) [MODERATE].

### 2.2 Multi-LLM routing

**Core concepts.** Routing classifies inputs and dispatches to specialized models or workflows; Anthropic describes it as "send[ing] easy tasks to Haiku and harder tasks to Sonnet" (anthropic.com/research/building-effective-agents) [HIGH]. The research literature formalizes this as a constrained optimization: maximize expected quality $Q_R$ subject to expected cost $C_R$, often expressed as $U_R = Q_R - \lambda \cdot C_R$ (LLMRank, arXiv:2510.01234) [HIGH].

**Patterns.** (a) *Task-complexity routing* via lightweight classifier or embedding similarity (OptiRoute, arXiv:2502.16696, uses kNN over a "Model Repository and Evaluation Store") [MODERATE]; (b) *Cost-aware contrastive routing* via logit footprints / perplexity fingerprints (CSCR, arXiv:2508.12491) [MODERATE]; (c) *Confidence-aware routing* (CARGO, arXiv:2509.14899, reports 76.4% top-1 accuracy with binary uncertainty fallback) [MODERATE]; (d) *Reinforcement-learned routing* with success-contingent cost-sensitive reward (xRouter, arXiv:2510.08439) [MODERATE]; (e) *Cascade* (FrugalGPT-style) with escalation; (f) **Semantic caching** as a pre-routing layer (Redis, redis.io/blog/semantic-caching-and-routing-two-powerful-patterns-for-vector-classification; GPTCache; Cortex, arXiv:2509.17360) [HIGH on existence of pattern; MODERATE on relative effectiveness].

**Model-as-judge vs model-as-worker separation.** Anthropic's research system uses Claude Opus 4 as the lead orchestrator and Sonnet 4 as workers, reporting >90% improvement over a single-agent setup (anthropic.com/engineering/multi-agent-research-system) [HIGH]. Hamel Husain documents a separate frontier-vs-cheap allocation: cheap models for synthetic data generation and code-based assertions, frontier models for LLM-as-judge with calibration against human labels (hamel.dev/blog/posts/evals-faq) [MODERATE].

**Failure modes.** "Thundering herd" on retries; cache poisoning if similarity threshold is too loose (Cortex paper notes false positives in dense embedding spaces and missed valid paraphrases in sparse spaces, arXiv:2510.26835) [MODERATE]; routing oscillation when the classifier's confidence is unstable.

**Metrics.** Routing accuracy, cost-per-task, p50/p95 latency per route, cache hit rate (production benchmarks cited: 30–98% for Anthropic prompt cache reads in batch contexts), routing decision overhead in ms.

**Contested.** Whether to route via embeddings/classifiers vs. via a small LLM "router agent." OpenAI's guide and Mastra's "agent networks" treat the LLM itself as router (mastra.ai/docs/agents/networks) [HIGH]; Inworld and academic routers argue this is wasteful for repeated patterns.

### 2.3 Prompt management infrastructure

**Core concepts.** Production teams treat prompts as code: versioned, tested, evaluated, and registry-managed. Hamel Husain's eval methodology starts with manual review of 20–50 outputs per significant change, then categorization into systematic failure modes, then code-based and LLM-judge eval gates (hamel.dev/blog/posts/evals-faq, hamel.dev/blog/posts/evals) [HIGH]. Shreya Shankar's research formalizes assertion derivation from prompts (PROMPTEVALS, arXiv:2504.14738) [HIGH] and judge alignment with human preferences ("Who Validates the Validators?", sh-reya.com/papers).

**System/developer/user layer separation.** OpenTelemetry GenAI semconv codifies `gen_ai.system_instructions`, `gen_ai.input.messages`, and `gen_ai.output.messages` as distinct attributes (opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans) [HIGH]. Anthropic's prompt-caching docs treat "tools, system, and messages (in that order) up to and including the block designated with cache_control" as the cacheable prefix (platform.claude.com/docs/en/build-with-claude/prompt-caching) [HIGH], which forces a discipline of static-prefix / dynamic-suffix prompt construction.

**Prompt caching.** Anthropic's caching: writes cost 1.25× base input price for 5-minute TTL (or 2.0× for 1-hour TTL); reads cost 0.10× base input. Minimum cacheable length is 1,024 tokens for Sonnet, 4,096 for Opus and Haiku 4.5; up to 4 explicit `cache_control` breakpoints per request (claude-cookbooks/misc/prompt_caching.ipynb; platform.claude.com/docs/en/build-with-claude/prompt-caching) [HIGH]. Stacks with Batch API at 50% off and can compound to ~95% savings on input (llmindset.co.uk/posts/2024/10/anthropic-batch-pricing) [MODERATE — independent confirmation].

**Templating discipline.** Eugene Yan's "Patterns for Building LLM-based Systems" (eugeneyan.com/writing/llm-patterns) calls out evals, RAG, fine-tuning, caching, guardrails, defensive UX, and feedback collection as the seven canonical production patterns [HIGH].

**Failure modes.** "Prompt drift" when templates are duplicated across services; cache invalidation from accidental dynamic content in the cacheable prefix (Spring AI's analysis: "even a single character change creates a new cache entry," spring.io/blog/2025/10/27/spring-ai-anthropic-prompt-caching-blog) [MODERATE]; LLM-judge bias when judge and worker share a base model (Hamel/Shreya note this and recommend explicit alignment runs) [HIGH].

**Metrics.** Cache hit rate, cache write/read token ratio, prompt-version regression test pass rate, judge-human agreement (Spearman, percent agreement).

**Contested.** Whether to use a prompt registry product or git-tracked text files. Practitioner consensus (Husain, Willison) leans toward git+code; vendors push registries.

### 2.4 Context engineering

**Core concepts.** Anthropic's framing: "find the smallest set of high-signal tokens that maximize the likelihood of your desired outcome" (anthropic.com/engineering/effective-context-engineering-for-ai-agents) [HIGH]. The post introduces three operational principles:

1. **System prompt altitude.** "The Goldilocks zone between two common failure modes": brittle hardcoded if-else logic vs. vague high-level guidance. "Specific enough to guide behavior effectively, yet flexible enough to provide the model with strong heuristics" [HIGH].
2. **Just-in-time retrieval** over pre-inference RAG dumps: "agents [are] increasingly … augmenting these retrieval systems with 'just in time' context strategies" — load tool definitions and references on demand rather than upfront [HIGH].
3. **Compaction for long-horizon tasks** vs. fresh-context handoffs. Anthropic's "Effective harnesses for long-running agents" (anthropic.com/engineering/effective-harnesses-for-long-running-agents) introduces a *two-agent harness*: an *initializer agent* that writes an `init.sh`, a `claude-progress.txt`, and an initial git commit, plus a *coding agent* that makes incremental progress and leaves "clean state" for the next session [HIGH].

**Memory tiers.** The CoALA-derived taxonomy (working / episodic / semantic / procedural) is consensus across IBM, MongoDB, LangChain, Letta, Mem0 and academic surveys (atlan.com/know/types-of-ai-agent-memory; "Multi-Layered Memory Architectures," arXiv:2603.29194) [MODERATE — taxonomy is widely repeated; specific implementations vary]. Letta (formerly MemGPT) implements an OS-inspired three-tier model with agent-directed consolidation [MODERATE].

**Context-rot mitigation.** Chroma's empirical study (trychroma.com/research/context-rot) tested 18 models and found degradation at every input-length increment, not just near the limit, with U-shaped attention favoring start and end of context (Liu et al. lost-in-the-middle effect) [HIGH]. Mitigations: keep critical info near the start or end; use sub-agents with bounded context; offload to filesystem (Anthropic's "claude-progress.txt" pattern); aggressive compaction.

**Failure modes.** "Context rot" (Hacker News–coined June 2025; trychroma research July 2025); agent "one-shotting" or declaring a project complete prematurely (explicit in Anthropic's harness post); implicit cache invalidation from non-deterministic prompt construction.

**Metrics.** Token utilization curve, retrieval relevance@k, attention-position degradation curve, fraction of context devoted to tool definitions vs. task content.

**Contested.** Whether 1M-token contexts are useful at all; Chroma's data suggests "a 1M-token window still rots at 50K tokens" [HIGH-as-cited]. Anthropic's own doc agrees: "treating context as a precious, finite resource will remain central."

### 2.5 Tool use and skills

**Tool design contracts.** Anthropic's "Writing effective tools for agents — using AI agents" (anthropic.com/engineering/writing-tools-for-agents) is the most thorough primary source [HIGH]. Five principles distilled:
- Strategic selection (don't wrap every API endpoint).
- Clear namespacing (Anthropic notes namespacing has "non-trivial effects on tool-use evaluations").
- Meaningful context in responses.
- Token efficiency with smart defaults.
- Tool descriptions are prompts.

**Parallel tool use.** Anthropic supports parallel tool calls; this can be disabled with `tool_choice: {disable_parallel_tool_use: true}` (platform.claude.com/docs/en/agents-and-tools/tool-use; GitHub Chainlit issue #2662) [HIGH]. Note: extended thinking has limits — "tool_choice: {'type': 'any'}" or specifying a tool is incompatible with extended thinking (platform.claude.com/docs/en/build-with-claude/extended-thinking) [HIGH].

**Strict / structured tool use.** Anthropic released structured outputs in public beta on Nov 14, 2025 with constrained decoding that "compiles your JSON schema into a grammar and actively restricts token generation" (platform.claude.com/docs/en/build-with-claude/structured-outputs) [HIGH]. Strict mode adds `strict: true` to tool defs.

**MCP servers.** MCP (modelcontextprotocol.io/specification/2025-06-18) uses JSON-RPC 2.0 over stdio or HTTP/SSE; defines Tools, Resources, Prompts, Roots, Elicitation, and Sampling primitives [HIGH]. Donated to the Agentic AI Foundation under the Linux Foundation in Dec 2025 (en.wikipedia.org/wiki/Model_Context_Protocol) [MODERATE]. Tool selection at scale is a known problem: Anthropic's "Code execution with MCP" post documents the explosion when "agents are connected to thousands of tools" and presents a solution where the agent discovers tool files on a filesystem and loads only what's needed, reducing token usage from 150,000 to 2,000 (98.7% saving) [HIGH]. Cloudflare independently published similar findings as "Code Mode."

**Anthropic Skills.** A `SKILL.md` file with YAML frontmatter (`name`, `description`) plus optional folders (`scripts/`, `references/`, `assets/`) (anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) [HIGH]. **Progressive disclosure** is the core design principle: only `name` and `description` are pre-loaded into the system prompt; the body is loaded only when the agent decides the skill is relevant. Published as an open standard Dec 18, 2025 (agentskills.io). Skills cookbooks include 17 open-source examples (github.com/anthropics/skills).

**Server tools.** Anthropic provides hosted server-side tools (`web_search`, `web_fetch`, `code_execution`, `tool_search`) where Anthropic executes and returns results; client tools run in your application (platform.claude.com/docs/en/agents-and-tools/tool-use/overview) [HIGH].

**Idempotency.** Standard practice: "Retry idempotent tools only (GET-like reads, deterministic queries)" with idempotency keys for state-mutating calls (medium.com/@2nick2patel2/llm-tooling-in-prod) [MODERATE — community consensus, not single primary source].

**Failure modes.** Tool sprawl (hundreds of MCP tools blowing context); tool poisoning (malicious instructions in metadata); tool shadowing; **rug pull** attacks (servers updated with malicious prompts after install) ("Top 10 MCP Security Risks," prompt.security; arXiv:2603.22489) [MODERATE].

**Metrics.** Tool-call success rate, token cost per tool call, tool-selection accuracy on holdouts, cache hit rate on tool definitions.

### 2.6 Sub-agents and single-file agents

**When sub-agents apply.** Anthropic uses sub-agents for breadth-first exploration and to "spread reasoning across multiple independent context windows." The Lead Researcher saves a plan to memory because "if the context window exceeds 200,000 tokens it will be truncated" (anthropic.com/engineering/multi-agent-research-system) [HIGH]. Sub-agents are *isolated context* boundaries that return distilled findings to the orchestrator; they do not share memory with peers.

**Single-file agents** (disler/single-file-agents; Simon Willison's commentary). "Pack single purpose, powerful AI Agents into a single python file." Use case: scoped, repeatable tasks with carefully crafted prompts and uv-managed deps. The pattern's value: deployability ("you can run these scripts from your server or right from a gist") and testability — but does not scale to long-running heterogeneous workflows [MODERATE — primary source is the GitHub README].

**Context handoff contracts.** Anthropic's harness post (anthropic.com/engineering/effective-harnesses-for-long-running-agents) documents the handoff artifact: a comprehensive feature requirements file, a `claude-progress.txt`, an init script, and git commits — all designed so "future coding agents will need to work effectively" with no shared memory [HIGH]. OpenAI Agents SDK's *handoff* primitive carries optional structured metadata and `input_filter` for the next agent (openai.github.io/openai-agents-python/handoffs) [HIGH].

**Return-value shape.** OpenAI Agents SDK enforces typed `output_type` (Pydantic / Zod / typed JSON Schema) (openai.github.io/openai-agents-python/agents) [HIGH]. Mastra workflows require `inputSchema`/`outputSchema` per step (mastra.ai/docs/workflows/overview) [HIGH]. LangGraph state is a TypedDict reducer-merged across nodes (reference.langchain.com/python/langgraph) [HIGH].

**Failure modes.** Sub-agent context loss when handoff artifacts are incomplete; orchestrator over-decomposing simple queries; handoff loops (A→B→A) without termination criteria.

**Metrics.** Handoff-success rate, sub-agent token efficiency, orchestrator-vs-sub-agent token ratio.

### 2.7 Parallelism

**Patterns.** Anthropic ("Building Effective Agents") splits parallelization into *sectioning* (independent subtasks running concurrently) and *voting* (multiple attempts of the same task aggregated) [HIGH]. Map-reduce over agents is the natural extension. The research-system post documents that "subagents enabling the kind of scaling that a single agent cannot achieve" and that asynchronous orchestration "adds challenges in result coordination, state consistency, and error propagation" — Anthropic describes their own system as currently synchronous with async under development [HIGH].

**Concurrency limits.** Anthropic's research-system post explicitly notes early agents "spawning 50 subagents for simple queries" — concurrency caps are a prompt-engineering lever ("We embed scaling rules in the prompts for tasks") [HIGH].

**Race patterns.** Common in evaluator-optimizer setups; not extensively documented in primary sources reviewed.

**Cost amplification.** Multi-agent ≈ 15× chat tokens, ≈ 4× single-agent; only justified "for tasks where the value of the outcome outweighs the expense" (anthropic.com/engineering/multi-agent-research-system; blog.bytebytego.com/p/how-anthropic-built-a-multi-agent) [HIGH for the multipliers; MODERATE on universality].

**Deadlock and starvation.** Less discussed in primary sources. Diagrid's "Checkpoints Are Not Durable Execution" (diagrid.io/blog) raises that LangGraph's open-source library "runs in a single process" without distributed locking, so two processes resuming the same `thread_id` can race [MODERATE — vendor-aligned source].

**Metrics.** Throughput (tasks/min), p95 wall-clock vs sequential baseline, cost amplification ratio, parallel efficiency (speedup ÷ workers).

### 2.8 Validation and the deterministic outer harness

**Schema validation / structured outputs.** Anthropic's grammar-constrained decoding (platform.claude.com/docs/en/build-with-claude/structured-outputs) mathematically guarantees schema compliance via token-level constraints; supports Pydantic, Zod, plain Java classes, and raw JSON Schema; caches the compiled grammar for 24h [HIGH]. OpenAI Agents SDK uses `output_type` with Pydantic; LangChain has `with_structured_output(method="json_schema")` for Anthropic native (docs.langchain.com/oss/python/integrations/chat/anthropic).

**Linters / type checks / test gates.** Anthropic's harness post puts "verification tools so the agent can check correctness without human feedback" at the center of the design [HIGH]. The pattern: deterministic gates (linters, type-checkers, unit tests) run between LLM steps and feed results back as observations. The Reflexion paper (Shinn et al., arXiv:2303.11366, NeurIPS 2023) [HIGH] formalizes this: "Reflexion converts binary or scalar feedback from the environment into verbal feedback in the form of a textual summary, which is then added as additional context for the LLM agent in the next episode."

**Sandboxed execution.** Anthropic recommends "extensive testing in sandboxed environments, along with the appropriate guardrails" (anthropic.com/research/building-effective-agents) [HIGH]. OpenAI Agents SDK introduced *sandbox agents* (v0.14.0+) — agents bound to a manifest-defined isolated workspace with snapshots and resumable sessions (openai.github.io/openai-agents-python) [HIGH].

**Reflexion / generator-evaluator loops.** Reflexion (arXiv:2303.11366) shows that verbal self-reflection on failure trajectories, stored in an episodic memory buffer, induces better decisions on subsequent trials — without weight updates [HIGH]. Anthropic's "evaluator-optimizer" workflow (anthropic.com/research/building-effective-agents) is the production-engineering analogue: "two signs of good fit are, first, that LLM responses can be demonstrably improved when a human articulates their feedback; and second, that the LLM can provide such feedback" [HIGH].

**Retry exit criteria.** Anthropic's guide explicitly recommends "stopping conditions (such as a maximum number of iterations) to maintain control" [HIGH].

**Failure modes.** Endless self-correction loops; evaluator drift (judge gradually loosens standards); validation gates that catch syntax but not semantics.

**Metrics.** First-try pass rate, retries-to-success distribution, eval gate true-positive rate, time-to-validation.

### 2.9 State and memory consistency

**File-backed state.** Anthropic's harness post: "Claude's latest models are effective at discovering state from the filesystem … put everything critical in CLAUDE.md, which the harness re-reads on every turn" — a deliberate departure from in-memory state (community analysis at wavespeed.ai/blog/posts/claude-code-agent-harness-architecture) [MODERATE — community analysis citing Anthropic docs]. Anthropic's official harness post recommends progress files plus git history.

**Git as state.** Explicit in Anthropic's harness post: "an init.sh script, a claude-progress.txt file that keeps a log of what agents have done, and an initial git commit that shows what files were added" [HIGH]. Git provides versioning, atomicity (commit/rollback), and an auditable trail — a deterministic outer harness for stateful change.

**Two-phase commits, snapshots, rollback.** LangGraph implements *checkpoints* with three durability modes — `exit`, `async`, `sync` — backed by `BaseCheckpointSaver` implementations (InMemory, SQLite, Postgres) (docs.langchain.com/oss/python/langgraph/durable-execution) [HIGH]. Each checkpoint is a complete state snapshot enabling "persistence, resumability, time-travel debugging, and human-in-the-loop workflows" (deepwiki.com/langchain-ai/langgraph). However, Diagrid critiques: "Checkpointing is not production-grade durability. It's a low-level building block that shifts the hard problems onto you" — specifically, no built-in distributed locking when two processes resume the same thread (diagrid.io/blog) [MODERATE — vendor-aligned but technically detailed].

**Pruning.** Anthropic's `clear_tool_uses_20250919` (beta `context-management-2025-06-27`) automatically clears old tool results as context fills (docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages-tool-use) [HIGH].

**State Ledger pattern.** Not a single primary source coined this, but the convergent pattern across Anthropic's harness post, HumanLayer's "12-Factor Agents" Factor 6 ("Separate Business from Execution State"), and LangGraph's checkpoint model is: an append-only log of events distinct from materialized state, allowing replay and audit [MODERATE — synthesis from multiple sources].

**Failure modes.** Cache poisoning across sessions; stale state from incomplete compaction; concurrency races in distributed resume (Diagrid, github.com/langfuse/langfuse/issues/10962 documents Langfuse trace fragmentation across LangGraph interrupt resumes) [MODERATE].

**Metrics.** Checkpoint write latency, recovery time after crash, ledger size growth rate, state-divergence incidents per 10k runs.

### 2.10 Observability

**OpenTelemetry GenAI semantic conventions** (opentelemetry.io/docs/specs/semconv/gen-ai). Defines event, exception, metric, and span signals; agent-specific spans extend model spans. Operations include `chat`, `create_agent`, `invoke_agent`, `invoke_workflow`, `retrieval`, `text_completion`. **Span name conventions:** `create_agent {gen_ai.agent.name}`, `invoke_agent {agent.name}`, etc. **Sensitive data handling:** "Instrumentations SHOULD NOT capture [model instructions, user messages, model outputs] by default, but SHOULD provide an option for users to opt in" [HIGH]. Workflow spans (`invoke_workflow`) should be reported only by frameworks that distinguish workflow-from-agent (e.g., CrewAI's "crew" concept), not by frameworks like Google ADK whose workflow agents are a kind of agent [HIGH].

**Provider discriminator.** `gen_ai.provider.name` (e.g., `aws.bedrock`) acts as a discriminator with provider-specific extensions (e.g., `aws.bedrock.*`, `openai.*`) [HIGH].

**Production maturity.** "As of March 2026, most GenAI semantic conventions are in experimental status" (dev.to/x4nent/opentelemetry-genai-semantic-conventions) [MODERATE — secondary source corroborating the OTel docs marking conventions as experimental]. Datadog announced native support starting v1.37 (datadoghq.com/blog/llm-otel-semantic-convention) [HIGH].

**Distributed tracing across agent steps.** Microsoft Agent Framework includes "Built-in OpenTelemetry integration for distributed tracing" (github.com/microsoft/agent-framework) [HIGH]. CrewAI lists Arize Phoenix, Datadog, Langfuse, MLflow, Opik, Weave, and Galileo integrations (docs.crewai.com) [HIGH]. OpenAI Agents SDK provides built-in tracing.

**Evaluation in production.** Hamel Husain's methodology: "vibe code your own trace viewer," manually review 20–50 outputs per significant change, take notes on traces, then build automated assertions (hamel.dev/blog/posts/evals-faq) [HIGH]. Anthropic's research-system team uses LLM-as-judge supplemented by human evaluation, noting human testers caught subtle issues like "early agents consistently chose SEO-optimized content farms over authoritative but less highly-ranked sources" [HIGH].

**Cost and token attribution.** OTel GenAI metrics include token usage; framework-specific instrumentation captures per-step costs.

**Failure modes.** "Vendor differences in trace definitions" (Hamel cites Alex Strick van Linschoten's analysis); over-instrumentation flooding storage; under-instrumentation hiding root causes.

**Metrics.** Token cost per session, span error rate, p95 step latency, eval-failure→fix MTTR.

### 2.11 Reliability primitives

**Timeouts.** Per-attempt timeouts plus a global budget — "The pattern that consistently works is: exponential backoff with jitter, per-attempt timeouts, capped total attempts, idempotency for mutating actions, and a circuit breaker" (skywork.ai citing AWS Well-Architected) [MODERATE].

**Retries with jittered exponential backoff.** Standard formula: `wait = (base * 2^attempt) + random(0, jitter_max)` — "AWS research on distributed systems [shows] exponential backoff with jitter reduces retry storms by 60-80%" [MODERATE]. Anthropic's API rate-limit handling guidance (no single primary URL — implemented in SDK).

**Idempotency keys.** Required for any state-mutating tool call; assume "at-least-once execution; make it safe" (medium.com/@2nick2patel2/llm-tooling-in-prod) [MODERATE].

**Circuit breakers.** Open the circuit after error threshold; serve cached/approximate responses or fail fast. Portkey, llm-circuit-breaker (npm package by hanzalagithub), and many vendors implement this pattern [MODERATE].

**Fallback chains.** Same-model retry → cheaper-model fallback → cached response → human escalation. Mastra exposes `retryConfig: { maxRetries, delayMs }` per step (console.groq.com/docs/mastra) [HIGH].

**Graceful degradation.** Anthropic's research-system team "doesn't update agents at the same time because it doesn't want to disrupt operations" — staggered rollouts as a degradation strategy (constellationr.com summary of Anthropic post) [MODERATE].

**Failure modes.** Retry storms from synchronized clients; circuit-breaker false trips during slow recovery; fallback amplifying cost without improving reliability.

**Metrics.** Retry-success rate, p99 retry-induced latency, circuit-breaker open duration, fallback-rate trend.

### 2.12 Security and governance

**Agent authorization scopes.** OpenAI Agents SDK distinguishes input guardrails (run only on first agent), output guardrails (run on final-output producer), and tool guardrails (per-tool-call); guardrails return `tripwire_triggered` to halt execution (openai.github.io/openai-agents-python/guardrails) [HIGH]. LangGraph's HITL middleware checks each tool call against an `interrupt_on` policy, with decisions `approve`/`edit`/`reject`/`respond` (docs.langchain.com/oss/python/langchain/human-in-the-loop) [HIGH].

**Write-path trust boundaries.** Claude Code analysis describes "rule-based pipeline evaluat[ing] every tool call: allow, ask, or deny, with deny always winning. In auto mode, a background classifier on a separate model instance evaluates ambiguous cases — and deliberately doesn't see the agent's prose output to prevent prompt injection" (wavespeed.ai analysis) [MODERATE — community analysis but consistent with Anthropic's published patterns].

**Sandbox isolation.** OpenAI sandbox agents and Anthropic Managed Agents both run agent execution in isolated containers (openai.github.io/openai-agents-python; platform.claude.com/docs/en/managed-agents/overview) [HIGH].

**Secrets handling.** Standard 12-factor: env vars, no secrets in prompts. Anthropic Skills security note: "We strongly recommend using Skills only from trusted sources … malicious Skills could lead to data exfiltration, unauthorized system access" (platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) [HIGH].

**Supply-chain integrity.** MCP tool poisoning is the dominant attack class — "tool poisoning attacks, a specialized form of prompt injection where malicious instructions are tucked away in the tool descriptions themselves — visible to the LLM, not normally displayed to users" (Invariant Labs via simonwillison.net/2025/Apr/9/mcp-prompt-injection) [HIGH]. The arXiv SoK (arXiv:2512.08290) catalogs Resources/Prompts/Tools as attack surfaces and surveys defenses including ETDI cryptographic provenance and runtime intent verification [MODERATE]. Empirical study of seven major MCP clients (arXiv:2603.21642) found "significant disparities … some clients, such as Claude Desktop, implement strong guardrails, others, such as Cursor, exhibit high susceptibility to cross-tool poisoning, hidden parameter exploitation, and unauthorized tool invocation" [MODERATE — preprint-stage].

**Audit trails.** OTel GenAI spans (with opt-in input/output capture) plus git as state are the two pillars [HIGH].

**HITL gates.** See domain 2.13.

**Failure modes.** Indirect prompt injection via retrieved documents; lookalike/shadow tools; rug-pull updates of trusted MCP servers.

**Metrics.** Authorization-denial rate, gate bypass attempts, audit completeness (% of write-path calls logged), MCP server signature verification rate.

### 2.13 Human-in-the-loop design

**Checkpoint placement.** Anthropic: "Agents can then pause for human feedback at checkpoints or when encountering blockers" (anthropic.com/research/building-effective-agents) [HIGH]. LangGraph's `interrupt()` is the canonical primitive: pauses inside a node, returns control with a payload, persists state via the checkpointer, resumes via `Command(resume=value)` (docs.langchain.com/oss/python/langchain/human-in-the-loop) [HIGH].

**Approval queues.** LangGraph HITL middleware decisions: `approve`, `edit`, `reject`, `respond`. Microsoft Agent Framework: "Orchestrations support human-in-the-loop interactions through tool approval and request info" (learn.microsoft.com/en-us/agent-framework/workflows/orchestrations) [HIGH]. CrewAI provides "Human-in-the-Loop (HITL) Workflows" and "Human Feedback in Flows" (docs.crewai.com) [HIGH].

**Interruption and resumption.** LangGraph requires a checkpointer (or it errors at compile); the same `thread_id` config must be used for invoke and resume (langchain.com/blog/making-it-easier-to-build-human-in-the-loop-agents-with-interrupt) [HIGH].

**Ask-First boundary tier.** Implicit pattern: gate any irreversible operation behind an explicit user approval. The "12-Factor Agents" Factor 7 ("Contact Humans as First-Class Operations") frames human input as a tool call rather than an exception (github.com/humanlayer/12-factor-agents) [HIGH].

**Escalation triggers.** Confidence thresholds, repeated failure counts, policy violations. OpenAI guardrails offer `run_in_parallel=False` (block until check completes, saving downstream cost) vs. `run_in_parallel=True` (lower latency, but tokens may already be spent before tripwire fires) [HIGH].

**Failure modes.** Approval fatigue (over-asking); silent autonomy expansion (gradually loosening gates); trace fragmentation across resume (Langfuse Issue #10962) [MODERATE].

**Metrics.** Approval response time, % approved/rejected/edited, fraction of runs requiring HITL.

### 2.14 Local-first deployment specifics

**Running orchestrators on developer hardware.** Mastra is explicitly TypeScript-native, runs locally with LibSQL/SQLite storage by default (mastra.ai/docs) [HIGH]. CrewAI "supports various language models, including local ones … Tools like Ollama and LM Studio allow seamless integration" (github.com/crewaiinc/crewai) [HIGH]. LangGraph runs in a single process by default with an in-memory checkpointer, swappable to SQLite/Postgres (docs.langchain.com/oss/python/langgraph/durable-execution) [HIGH].

**Self-hosted patterns.** OpenAI Agents SDK is provider-agnostic: "supporting the OpenAI Responses and Chat Completions APIs, as well as 100+ other LLMs" via LiteLLM (github.com/openai/openai-agents-python) [HIGH]. LiteLLM provides a unified API for Anthropic, OpenAI, and local providers including Ollama (docs.litellm.ai/docs/providers/anthropic) [HIGH].

**Secrets at rest.** Standard practice: OS keychain, env vars, .env files git-ignored. No primary source uniquely defines this for agents.

**Local model fallback.** Pattern: route simple/private tasks to local Ollama; cloud frontier for complex/non-private. No primary source benchmarks the quality cliff explicitly.

**What changes when not in cloud control plane.** (a) Prompt caching's 5-minute TTL is harder to maintain across local CLI invocations; (b) batch API's 24-hour async window doesn't fit interactive workflows; (c) distributed checkpointing/durable-execution layers (Temporal, Dapr Workflows) are heavier to self-host; (d) OTel collector can run locally but requires a backend (Jaeger, local Loki, etc.) (Diagrid's argument for durable execution is most relevant here, though vendor-aligned).

**Failure modes.** Single-process crashes losing in-memory state; secrets leaking into shell history or trace logs; rate-limit storms when retry logic runs in parallel from one developer machine.

**Metrics.** Local-cache hit rate, recovery time on crash, fraction of requests served by local model.

**Contested.** Whether local-first agents need true durable execution or whether checkpointing-to-disk is sufficient for solo/single-user workflows. Diagrid argues no; LangChain's stance is that checkpointing + correctly structured nodes is enough for most cases.

### 2.15 Anthropic-specific surface area

**Claude Skills.** See 2.5. SKILL.md + progressive disclosure + cross-product portability (Claude.ai, Claude Code, Agent SDK, API) [HIGH]. Skills can be uploaded via the API, listed via List Skills endpoint, pinned to a specific `version` or `latest`, and are *not* covered by ZDR arrangements (platform.claude.com/docs/en/build-with-claude/skills-guide).

**Prompt caching.** See 2.3. Automatic (single top-level `cache_control`) vs. explicit (up to 4 breakpoints). Cache hits cost 0.10× input price; writes 1.25× (5min) or 2.0× (1hr); minimum 1,024 tokens (Sonnet) / 4,096 tokens (Opus, Haiku 4.5) [HIGH]. Stacks with Batch API.

**Extended thinking.** Adaptive thinking is the default on Opus 4.7; budget-based modes (low/medium/high/xhigh/max) available; `xhigh` recommended for coding and agentic tasks (promptfoo.dev/docs/providers/anthropic; platform.claude.com/docs/en/build-with-claude/extended-thinking) [HIGH]. Constraint: extended thinking with tool use only supports `tool_choice: auto` or `none`. Thinking blocks must be passed back unchanged for the last assistant message during tool use loops.

**Structured outputs.** Constrained-decoding-based, beta from Nov 14, 2025, supports Pydantic/Zod/JSON Schema; ~2–3% cost overhead but eliminates retry/parsing logic [HIGH on the launch and mechanism].

**Batch API.** 50% off both input and output tokens; up to 100k requests per batch or 256MB; results within 24 hours (most under 1 hour); no webhooks (poll); stacks with prompt caching for compounding discounts; **extended output** (anthropic-beta `output-300k-2026-03-24`) up to 300k tokens per request, batch-only (platform.claude.com/docs/en/build-with-claude/batch-processing) [HIGH].

**Managed Agents.** "Provides the harness and infrastructure for running Claude as an autonomous agent … fully managed environment where Claude can read files, run commands, browse the web, and execute code securely. The harness supports built-in prompt caching, compaction, and other performance optimizations" (platform.claude.com/docs/en/managed-agents/overview) [HIGH]. Four concepts: agent (model + system prompt + tools + MCP servers + skills), environment (cloud container with packages and network rules), session, events (SSE streaming).

**MCP.** See 2.5. Anthropic donated MCP to the Agentic AI Foundation under the Linux Foundation in Dec 2025.

**Claude Code as reference implementation.** "Claude Code is composable and follows the Unix philosophy"; ships ~19 permission-gated tools (community analysis suggests up to ~40 with LSP and subagent tools); auto-compaction at ~98% context fill; full-context-reset handoffs sometimes outperform compaction (wavespeed.ai analysis) [MODERATE — community analysis citing Anthropic docs].

**Server tools.** `web_search`, `web_fetch`, `code_execution`, `tool_search` execute on Anthropic infrastructure with usage-based billing.

### 2.16 Cross-cutting tradeoffs

This is intentionally overlapping with §3 below; here we note the tradeoff classes, while §3 expands the matrix.

- **Cost vs reliability.** Frontier models reduce iteration count but cost more per call; Reflexion-style retries trade tokens for higher first-try reliability; multi-agent fan-out trades cost for breadth coverage.
- **Autonomy vs auditability.** Pure agents (LLM in a loop) are most flexible but hardest to audit; workflow patterns trade flexibility for traceable, replayable steps. OTel + git-as-state lifts auditability for both.
- **Generality vs specialization.** Single generalist agent (Claude Code style) covers many domains but accumulates context rot; specialized sub-agents (Skills + handoffs) are precise but require orchestration complexity.
- **Framework vs primitives.** Anthropic's stance: "the most successful implementations weren't using complex frameworks or specialized libraries. Instead, they were building with simple, composable patterns" (anthropic.com/research/building-effective-agents) [HIGH]. The 12-Factor Agents stance: "I don't see a lot of frameworks in production customer-facing agents" (Dex Horthy, github.com/humanlayer/12-factor-agents) [HIGH]. The counterpoint: frameworks (LangGraph, OpenAI Agents SDK, Microsoft Agent Framework) provide checkpointing, guardrails, and HITL primitives that are non-trivial to roll yourself, especially for the durable-execution corner.

---

## 3. Cross-Cutting Tradeoff Matrix

| Tradeoff axis | Lever | Cheaper / faster pole | More reliable / general pole | Primary signal |
|---|---|---|---|---|
| Cost vs reliability | Model tier | Haiku-class for routing, classification, extraction | Opus-class for orchestrator, judge, complex reasoning | Anthropic multi-agent post (Opus lead + Sonnet workers, +90% gain) [HIGH] |
| Cost vs reliability | Caching | Aggressive prompt cache + 1h TTL | Per-request fresh prompts | 0.10× cache read pricing [HIGH] |
| Cost vs reliability | Batch | 50% off async batch | Real-time sync | platform.claude.com/docs batch [HIGH] |
| Autonomy vs auditability | Workflow vs agent | Pure agent loop | Predefined workflow with gates | Anthropic "workflows vs agents" distinction [HIGH] |
| Autonomy vs auditability | HITL frequency | No interrupts | Interrupt on every write | LangGraph `interrupt_on` policy [HIGH] |
| Generality vs specialization | Single vs multi-agent | One generalist agent | Orchestrator + sub-agents + Skills | Anthropic multi-agent ~15× tokens [HIGH] |
| Generality vs specialization | Tool count | Few cohesive tools | Many specialized tools | Anthropic "tool sprawl" caveats [HIGH] |
| Framework vs primitives | Adoption | Build from primitives | Adopt LangGraph/Mastra/MAF | Anthropic and 12-Factor Agents both lean primitives [HIGH] |
| Speed vs determinism | Structured output | Free-form text + parser | Constrained decoding | Anthropic structured outputs ~2–3% overhead [HIGH] |
| Recall vs context-rot | Long context | 1M-token Sonnet/Opus | Aggressive retrieval + compaction | Chroma context-rot, even at 50k of 1M [HIGH] |
| Local vs cloud | Deployment | Local-first with Ollama+LiteLLM | Anthropic Managed Agents | LiteLLM provider docs; managed-agents overview [HIGH] |
| Cost vs latency | Extended thinking | `thinking: none` | `xhigh` / `max` | Promptfoo Anthropic notes [HIGH] |

---

## 4. Pattern Catalogue

The names below are drawn from primary sources where they exist; entries marked *(common practice)* are convergent patterns without a single canonical owner.

**Agent / harness shape**
- Augmented LLM (Anthropic Dec 2024)
- Workflow vs Agent dichotomy (Anthropic Dec 2024)
- Orchestrator-Worker (Anthropic; reused in OpenAI's "manager pattern," Microsoft Agent Framework "Magentic")
- Prompt Chaining / Sequential
- Routing
- Parallelization: Sectioning + Voting
- Evaluator-Optimizer (= generator-evaluator loop)
- Decentralized Handoff (OpenAI Agents SDK)
- Group Chat / Magnetic (Microsoft Agent Framework)
- Single-File Agent (Willison / disler)
- ReAct (Yao et al., arXiv:2210.03629) — interleaved reasoning + action
- Plan-and-Solve (Wang et al., arXiv:2305.04091) — explicit plan, then execute
- Pre-Act (Rawat et al., arXiv:2505.09970) — multi-step plan up front
- Reflexion (Shinn et al., arXiv:2303.11366) — verbal self-reflection in episodic memory
- OODA loop for sub-agents (Anthropic multi-agent post)
- Agent Harness (Anthropic / Claude Code) — initializer + worker, file-backed state
- Two-agent context-window-spanning harness (Anthropic Effective harnesses post)

**Context engineering**
- System-prompt altitude
- Just-in-time retrieval
- Compaction (auto via `clear_tool_uses_20250919`; manual via summarization)
- Fresh-context handoff via artifact (CLAUDE.md, claude-progress.txt)
- Progressive disclosure (Skills metadata → SKILL.md body → references)
- Code-execution-with-MCP (load tool files on demand)

**Tools and skills**
- Strict tool use (`strict: true`)
- Structured outputs (constrained decoding)
- Server tools vs client tools
- Anthropic "think" tool (anthropic.com/engineering/claude-think-tool) [HIGH]
- MCP server (stdio, HTTP/SSE; tools, resources, prompts, roots, elicitation, sampling)
- Agent Skill (SKILL.md + frontmatter + optional scripts/references/assets)
- Code Mode (Cloudflare; Anthropic code-execution-with-MCP)

**Memory / state**
- Working / Episodic / Semantic / Procedural (CoALA-derived)
- Three-tier OS-inspired memory (Letta/MemGPT)
- Reflection-based consolidation (Park et al. Generative Agents)
- File-backed state (CLAUDE.md, MEMORY.md, AGENTS.md)
- Git-as-state with progress.txt
- Checkpointing with thread_id (LangGraph)
- State Ledger / append-only event log *(common practice)*

**Reliability**
- Jittered exponential backoff
- Per-attempt timeout + global budget
- Idempotency keys for mutating tool calls
- Circuit breaker with cooldown
- Fallback chain (same-model retry → cheaper-model → cached → human)
- Rainbow / staggered deployment (Anthropic research-system post)

**Observability**
- OTel GenAI spans / metrics / events
- Vibe-coded trace viewer (Husain/Shankar)
- LLM-as-judge (with human-alignment validation)
- End-state evaluation (Anthropic for state-mutating agents)
- Drop-off analytics on agent journeys

**Security**
- Permission pipeline: allow / ask / deny (Claude Code analysis)
- Tool-poisoning defenses: static metadata analysis, parameter visibility, behavioral anomaly detection (arXiv:2603.22489)
- Sandbox isolation (OpenAI sandbox agents, Anthropic Managed Agents)
- ZDR boundaries; MCP roots filesystem scoping

**HITL**
- Interrupt + approve/edit/reject/respond (LangGraph)
- Tool approval gates (Microsoft Agent Framework, OpenAI guardrails)
- Ask-First boundary tier (12-Factor Agents Factor 7)

**Routing**
- Cascade / FrugalGPT escalation
- Embedding-classifier routing (OptiRoute, vLLM Semantic Router)
- Confidence-aware routing (CARGO)
- RL-trained cost-sensitive router (xRouter)
- Semantic cache before routing (GPTCache, Cortex)

---

## 5. Open Questions

1. **Durable execution vs checkpointing.** Where exactly is the boundary at which file-or-DB-backed checkpointing becomes insufficient and a workflow engine (Temporal, Dapr Workflows, Inngest) is required? Diagrid argues most agent frameworks fall short; LangChain's docs imply checkpointing suffices for most cases. No public benchmark resolves this for solo/local-first deployments.

2. **Quantitative context-rot curves per model.** Chroma's research provides curves for 18 models in mid-2025; updated curves for Opus 4.7, Sonnet 4.6, Gemini 3, GPT-5.4 are not yet centrally published. The 50% drop point ranges broadly across models.

3. **Skills-vs-MCP boundary.** Anthropic's own docs say "Skills can complement MCP servers by teaching agents more complex workflows that involve external tools and software." Practical decision criteria for what becomes a Skill vs an MCP tool vs both are not yet codified in primary sources.

4. **Reliability of LLM-judge in agent eval at scale.** Husain/Shankar emphasize human alignment for judge calibration (sh-reya.com "Who Validates the Validators?"). The exact judge-human agreement floor below which automated eval is unsafe is task-dependent and not generalized.

5. **Cost-quality frontier of routing.** Academic routers (LLMRank, CARGO, xRouter) report meaningful gains in controlled benchmarks; production case studies of how much these saved at scale, with quality holding, are sparse.

6. **MCP security maturity.** The "Are AI-assisted Development Tools Immune to Prompt Injection?" preprint (arXiv:2603.21642) shows wide variance across clients in mid-2026; the rate of fix uptake and standardized defenses (ETDI, runtime intent verification) is a moving target.

7. **Multi-agent for software engineering specifically.** Anthropic states multi-agent is "less effective for tightly interdependent tasks such as coding" — but Claude Code does spawn sub-agents internally for some research-style tasks. Where the line falls inside a coding workflow is not crisply documented.

8. **Local-model fallback quality cliff.** No widely-cited benchmark compares Anthropic frontier vs Qwen/Llama/DeepSeek locally on the specific orchestration roles (router, judge, sub-agent worker). The cliff is widely assumed but not characterized in primary sources reviewed.

9. **OTel GenAI semconv stabilization.** Conventions are still experimental as of the most recent docs accessed; vendor-specific extensions for Anthropic, OpenAI, Bedrock, Azure are partially defined. Production teams adopting the spec face dual-emission churn (`OTEL_SEMCONV_STABILITY_OPT_IN`).

10. **"Single-file agent" ceiling.** No primary source tests where the simplicity of a uv-managed single-file agent breaks under heterogeneous workflow demands.

---

## Caveats

- **Versioning churn.** Several specific facts (Opus 4.7 tokenizer, structured outputs beta header, 1M context flat-rate pricing, 300k extended output beta header `output-300k-2026-03-24`, Skills standard publication Dec 18 2025) are pulled from documentation accessed in this session and reflect a state that has been moving rapidly. Pricing and beta-header strings should be reverified before code is written against them.

- **Pricing precision.** Some pricing figures (e.g., $5/$25 Opus 4.7, $3/$15 Sonnet 4.6, $1/$5 Haiku 4.5) come from secondary sources (finout.io, pecollective.com) corroborated against Anthropic platform docs accessed in this session. Anthropic's official `claude.com/pricing` page is the authoritative source for current rates.

- **Community vs primary reverse-engineering.** Several Claude Code internals (~19 vs ~40 tools, exact compaction trigger at "98%," classifier-on-separate-model-instance) come from community analyses (wavespeed.ai, leehanchung.github.io, llmmultiagents.com) rather than official Anthropic docs. These are tagged [MODERATE] above; treat as informed inference, not specification.

- **Framework feature parity drift.** LangGraph durability modes, CrewAI Flows, Microsoft Agent Framework v1.0 capabilities, OpenAI Agents SDK sandbox agents (v0.14.0+), Mastra Networks — feature sets are evolving on roughly monthly cadences. The relative-positioning claims here will go stale faster than the conceptual framing.

- **Multi-agent token amplification figures.** The widely-cited "~15× chat" and ">90% improvement" numbers come from Anthropic's own research-system internal evals; they are specific to research workloads and should not be generalized to coding or pipeline-automation tasks. Anthropic itself flags this caveat.

- **"Durable execution" debate has vendor stakes.** The Diagrid critique of LangGraph/CrewAI/Google ADK checkpointing is technically substantive but Diagrid sells a competing product (Dapr Workflows). LangChain's stance that checkpointing is sufficient for most cases is also self-interested. The actual operational floor depends on workload characteristics not exposed by either side.

- **MCP security research is preprint-stage.** Several arXiv references (2603.22489, 2603.21642, 2512.08290) carry future-looking date stamps in their preprint IDs; they reflect the state of the security literature as accessed but have not gone through full peer review.

- **Speculative bridging.** The "State Ledger pattern" name and a few synthesis-level observations (e.g., that the tradeoff matrix's structure mirrors classical control-systems tradeoffs) are my synthesis from multiple primary sources rather than terms-of-art with a single canonical citation. [SPECULATIVE] in the strict sense.

---

## Source Bibliography

The following primary and reputable secondary sources were accessed during this research session and underpin the claims above. Vendor-marketing pages without primary technical content are intentionally omitted.

### Anthropic engineering and documentation
- "Building Effective Agents," Schluntz & Zhang, Dec 19, 2024 — anthropic.com/research/building-effective-agents
- "How we built our multi-agent research system," Hadfield et al., June 13, 2025 — anthropic.com/engineering/multi-agent-research-system
- "Effective context engineering for AI agents," Sept 29, 2025 — anthropic.com/engineering/effective-context-engineering-for-ai-agents
- "Effective harnesses for long-running agents" — anthropic.com/engineering/effective-harnesses-for-long-running-agents
- "Equipping agents for the real world with Agent Skills," Zhang/Lazuka/Murag — anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- "Code execution with MCP: building more efficient AI agents" — anthropic.com/engineering/code-execution-with-mcp
- "Writing effective tools for AI agents — using AI agents," Aizawa et al. — anthropic.com/engineering/writing-tools-for-agents
- "The 'think' tool: Enabling Claude to stop and think" — anthropic.com/engineering/claude-think-tool
- "Claude 3.7 Sonnet and Claude Code" — anthropic.com/news/claude-3-7-sonnet
- Claude API Docs — Pricing — platform.claude.com/docs/en/about-claude/pricing
- Claude API Docs — Prompt caching — platform.claude.com/docs/en/build-with-claude/prompt-caching
- Claude API Docs — Extended thinking — platform.claude.com/docs/en/build-with-claude/extended-thinking
- Claude API Docs — Structured outputs — platform.claude.com/docs/en/build-with-claude/structured-outputs
- Claude API Docs — Batch processing — platform.claude.com/docs/en/build-with-claude/batch-processing
- Claude API Docs — Tool use overview — platform.claude.com/docs/en/agents-and-tools/tool-use/overview
- Claude API Docs — Agent Skills overview — platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Claude API Docs — Skills guide — platform.claude.com/docs/en/build-with-claude/skills-guide
- Claude API Docs — Managed Agents overview — platform.claude.com/docs/en/managed-agents/overview
- Claude API Docs — Glossary — platform.claude.com/docs/en/about-claude/glossary
- Claude Code Docs — Overview — code.claude.com/docs/en/overview
- Claude Code Docs — Skills — code.claude.com/docs/en/skills
- Anthropic Skills repository — github.com/anthropics/skills
- Anthropic Cookbook prompt caching notebook — github.com/anthropics/anthropic-cookbook/blob/main/misc/prompt_caching.ipynb
- Agent Skills open standard — agentskills.io

### Research papers (arXiv / ACL)
- Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models," arXiv:2210.03629, ICLR 2023
- Shinn et al., "Reflexion: Language Agents with Verbal Reinforcement Learning," arXiv:2303.11366, NeurIPS 2023
- Wang et al., "Plan-and-Solve Prompting," arXiv:2305.04091, ACL 2023 (aclanthology.org/2023.acl-long.147)
- Rawat et al., "Pre-Act: Multi-Step Planning and Reasoning Improves Acting in LLM Agents," arXiv:2505.09970
- Vir, Shankar et al., "PROMPTEVALS: A Dataset of Assertions and Guardrails for Custom Production LLM Pipelines," arXiv:2504.14738
- Shankar et al., "Who Validates the Validators? Aligning LLM-Assisted Evaluation of LLM Outputs with Human Preferences" (sh-reya.com/papers)
- "Context Rot: How Increasing Input Tokens Impacts LLM Performance," Chroma research, July 2025 — trychroma.com/research/context-rot
- "Intelligence Degradation in Long-Context LLMs," arXiv:2601.15300 (preprint)
- "Multi-Layered Memory Architectures for LLM Agents," Fofadiya & Tiwari, arXiv:2603.29194 (preprint)
- "Context Engineering: From Prompts to Corporate Multi-Agent Architecture," arXiv:2603.09619 (preprint)
- "From Exact Hits to Close Enough: Semantic Caching for LLM Embeddings," arXiv:2603.03301 (preprint)
- "Cortex: Achieving Low-Latency, Cost-Efficient Remote Data Access For LLM via Semantic-Aware Knowledge Caching," arXiv:2509.17360
- "Category-Aware Semantic Caching for Heterogeneous LLM Workloads," arXiv:2510.26835
- "Dynamic LLM Routing and Selection based on User Preferences (OptiRoute)," arXiv:2502.16696
- "Cost-Aware Contrastive Routing for LLMs (CSCR)," arXiv:2508.12491
- "CARGO: A Framework for Confidence-Aware Routing of Large Language Models," arXiv:2509.14899
- "xRouter: Training Cost-Aware LLMs Orchestration System via Reinforcement Learning," arXiv:2510.08439
- "LLMRank: Understanding LLM Strengths for Model Routing," arXiv:2510.01234
- "Model Context Protocol Threat Modeling and Analyzing Vulnerabilities to Prompt Injection with Tool Poisoning," arXiv:2603.22489 (preprint)
- "Are AI-assisted Development Tools Immune to Prompt Injection?," arXiv:2603.21642 (preprint)
- "Systematization of Knowledge: Security and Safety in the Model Context Protocol Ecosystem," arXiv:2512.08290 (preprint)

### Framework documentation
- LangGraph durable execution — docs.langchain.com/oss/python/langgraph/durable-execution
- LangGraph Human-in-the-loop — docs.langchain.com/oss/python/langchain/human-in-the-loop
- LangGraph checkpointing architecture — deepwiki.com/langchain-ai/langgraph/4.1-checkpointing-architecture
- LangChain blog "Making it easier to build human-in-the-loop agents with interrupt" — langchain.com/blog/making-it-easier-to-build-human-in-the-loop-agents-with-interrupt
- LangChain "ChatAnthropic integration" — docs.langchain.com/oss/python/integrations/chat/anthropic
- CrewAI Flows — docs.crewai.com/en/concepts/flows
- CrewAI core repository — github.com/crewaiinc/crewai
- CrewAI examples — github.com/crewAIInc/crewAI-examples
- CrewAI on AWS Prescriptive Guidance — docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-frameworks/crewai.html
- Microsoft Agent Framework overview — learn.microsoft.com/en-us/agent-framework/overview/
- Microsoft Agent Framework Workflows — learn.microsoft.com/en-us/agent-framework/workflows/
- Microsoft Agent Framework orchestrations — learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/
- Microsoft Agent Framework v1.0 launch — devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/
- Microsoft Agent Framework GitHub — github.com/microsoft/agent-framework
- OpenAI Agents SDK — openai.github.io/openai-agents-python/
- OpenAI Agents SDK guardrails — openai.github.io/openai-agents-python/guardrails/
- OpenAI Agents SDK handoffs — openai.github.io/openai-agents-python/handoffs/
- OpenAI Agents SDK Python repo — github.com/openai/openai-agents-python
- OpenAI "A practical guide to building agents" — openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/
- OpenAI Apps SDK MCP page — developers.openai.com/apps-sdk/concepts/mcp-server
- Mastra docs — mastra.ai/docs
- Mastra workflows — mastra.ai/docs/workflows/overview
- Mastra agents — mastra.ai/docs/agents/overview
- Mastra agent networks — mastra.ai/docs/agents/networks
- Mastra GitHub — github.com/mastra-ai/mastra
- LiteLLM Anthropic provider — docs.litellm.ai/docs/providers/anthropic

### Standards and protocols
- Model Context Protocol specification — modelcontextprotocol.io/specification/2025-06-18
- MCP organization GitHub — github.com/modelcontextprotocol
- MCP Wikipedia (for chronology and adoption notes) — en.wikipedia.org/wiki/Model_Context_Protocol
- OpenTelemetry GenAI semantic conventions — opentelemetry.io/docs/specs/semconv/gen-ai/
- OpenTelemetry GenAI agent and framework spans — opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/
- OpenTelemetry GenAI metrics — opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-metrics/
- OpenTelemetry GenAI events — opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-events/
- OpenTelemetry semantic-conventions repo — github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-spans.md

### Practitioner writing
- Simon Willison, "Building effective agents" — simonwillison.net/2024/Dec/20/building-effective-agents/
- Simon Willison, "Anthropic: How we built our multi-agent research system" — simonwillison.net/2025/Jun/14/multi-agent-research-system/
- Simon Willison, "Model Context Protocol has prompt injection security problems" — simonwillison.net/2025/Apr/9/mcp-prompt-injection/
- Simon Willison, Agentic Engineering Patterns guide — simonwillison.net/guides/agentic-engineering-patterns/
- Simon Willison, agent-definitions tag — simonwillison.net/tags/agent-definitions/
- disler/single-file-agents — github.com/disler/single-file-agents
- Hamel Husain, "LLM Evals: Everything You Need to Know" — hamel.dev/blog/posts/evals-faq/
- Hamel Husain, "Your AI Product Needs Evals" — hamel.dev/blog/posts/evals/
- Hamel Husain, "The Revenge of the Data Scientist" — hamel.dev/blog/posts/revenge/
- Husain & Shankar AI Evals course — maven.com/parlance-labs/evals
- Eugene Yan, "Patterns for Building LLM-based Systems & Products" — eugeneyan.com/writing/llm-patterns/
- Shreya Shankar papers — sh-reya.com/papers/
- HumanLayer 12-Factor Agents — github.com/humanlayer/12-factor-agents and humanlayer.dev/12-factor-agents
- Datadog "LLM Observability natively supports OpenTelemetry GenAI Semantic Conventions" — datadoghq.com/blog/llm-otel-semantic-convention/
- Diagrid "Checkpoints Are Not Durable Execution" — diagrid.io/blog/checkpoints-are-not-durable-execution-why-langgraph-crewai-google-adk-and-others-fall-short-for-production-agent-workflows
- Redis "Semantic caching & routing" — redis.io/blog/semantic-caching-and-routing-two-powerful-patterns-for-vector-classification/
- Redis "Context rot explained" — redis.io/blog/context-rot/
- AWS "Build durable AI agents with LangGraph and Amazon DynamoDB" — aws.amazon.com/blogs/database/build-durable-ai-agents-with-langgraph-and-amazon-dynamodb/
- AWS Bedrock prompt caching — docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html
- AWS Bedrock Anthropic tool use (incl. clear_tool_uses_20250919) — docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages-tool-use.html
- AWS Prescriptive Guidance "Retry with backoff" — docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/retry-backoff.html
- Promptfoo Anthropic provider — promptfoo.dev/docs/providers/anthropic/
- Spring AI prompt caching post — spring.io/blog/2025/10/27/spring-ai-anthropic-prompt-caching-blog/
- Lee Hanchung "Claude Agent Skills: A First Principles Deep Dive" — leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/
- WaveSpeedAI "Claude Code Agent Harness: Architecture Breakdown" — wavespeed.ai/blog/posts/claude-code-agent-harness-architecture/
- ByteByteGo "How Anthropic Built a Multi-Agent Research System" — blog.bytebytego.com/p/how-anthropic-built-a-multi-agent
- Constellation Research "Anthropic's multi-agent system overview a must read for CIOs" — constellationr.com/blog-news/insights/anthropics-multi-agent-system-overview-must-read-cios

### Security-specific secondary sources
- Prompt Security "Top 10 MCP Security Risks" — prompt.security/blog/top-10-mcp-security-risks
- MCP Manager "MCP Prompt Injection" — mcpmanager.ai/blog/mcp-prompt-injection/
- MCP Manager "MCP Tool Poisoning" — mcpmanager.ai/blog/tool-poisoning/
- Security Boulevard / Datadome "MCP security: How to prevent prompt injection and tool poisoning attacks" — securityboulevard.com/2026/01/mcp-security-how-to-prevent-prompt-injection-and-tool-poisoning-attacks/

End of research synthesis.