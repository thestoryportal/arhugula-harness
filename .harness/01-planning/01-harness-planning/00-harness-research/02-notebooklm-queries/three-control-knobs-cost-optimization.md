# The Three Control Knobs of Agentic Cost Optimization

The corpus reveals that an agent harness's cost profile is dictated by three primary control knobs: how requests are routed, how context is cached, and when execution is deferred.

## 1. Model Routing: Declarative vs. Embedding vs. LLM-as-Router

The routing knob determines whether a query is sent to a premium frontier model (e.g., Opus 4.7 at $5/$25 per million tokens) or an economical model (e.g., Haiku 4.5 at $1/$5 per million tokens).

- **Declarative / Static Rules:** The harness hardcodes model selection to specific agent roles or task types.
  - **Harnesses:** **Roo Code** uses "per-mode model binding with cost-tier optimization," assigning a reasoning model to the "Architect" mode and a cheaper model to the "Coder" mode. **oh-my-openagent** utilizes "per-role fallback chains," and **kilocode** exposes a unified gateway with explicit allowlists.
  - **Tradeoff:** Zero latency and zero cost-overhead to make the routing decision. However, it over-provisions compute because it uses the expensive model for *all* tasks within a role, regardless of the specific prompt's actual difficulty.
- **Embedding-Similarity / Classifier Routing:** The harness evaluates the prompt against a vector database or lightweight regressor before dispatching.
  - **Harnesses:** Discussed extensively in the research substrate, frameworks like **OptiRoute** (kNN search) and **CARGO** (embedding-based regressor) predict model performance thresholds dynamically. **Semantic Caches** (like Redis or Cortex) act as "pre-routers," serving exact/similar hits at sub-millisecond latency.
  - **Tradeoff:** Drastically reduces cost (e.g., CARGO routes to cheaper experts with 76.4% top-1 accuracy) at a very low latency penalty (µs–ms), but requires ongoing maintenance of the embedding indices or labeled training data.
- **LLM-as-Router (RL/Generative):** A model explicitly decides where to route the task based on cost-aware reinforcement learning or prompt instructions.
  - **Harnesses:** **xRouter** uses an RL-trained model with a "success-gated, cost-shaped" reward (reward = quality − λ × normalized_cost). **OpenAI Agents SDK** and **Mastra** rely on the LLM itself as a central manager determining which sub-agent to hand off to.
  - **Tradeoff:** Achieves the highest dynamic accuracy (xRouter matches GPT-5 accuracy while cutting costs by up to 80%), but introduces the non-trivial token cost and latency (50-200+ ms) of the router LLM call itself before the actual work even begins.

## 2. Prompt-Cache Strategy: Static-Prefix vs. Dynamic Content

Prompt caching changes the economics of agent harnesses entirely. Anthropic charges a 1.25x premium for cache writes (5-minute TTL) but offers a 90% discount (0.10x) on cache reads.

- **Static-Prefix-Only Caching:** The harness explicitly places the cache breakpoint at the end of stable elements (tools, system prompts, few-shot examples) and isolates all per-request variables to the uncached suffix.
  - **Harnesses:** **Spring AI** implements this via its `SYSTEM_ONLY` and `TOOLS_ONLY` strategies. **Meta-Harness** uses a dedicated `anthropic_caching.py` module to preserve its heavy environment-bootstrapping prompt. **pi-mono** provides a `StreamFn` middleware seam to inject these explicit breakpoints cleanly across models.
  - **Tradeoff:** Highly reliable 90% savings on the heavy preamble. The tradeoff is that the model must re-process the entire conversation history on every turn.
- **Dynamic / Conversational Caching:** The harness attempts to cache the evolving conversation history by placing breakpoints deep into the message tail.
  - **Harnesses:** **LangChain JS** attempts this by placing breakpoints on the "most recent user message." **Spring AI** offers a `CONVERSATION_HISTORY` mode.
  - **Tradeoff:** If it hits, it yields maximum token savings. However, **the corpus reveals a catastrophic failure mode:** if a cache breakpoint is placed on a block that mutates even by a single character (e.g., a timestamp or a fluctuating thinking-block), the system silently fails to cache. The harness will pay the 1.25x write penalty on *every single call* and receive zero cache reads, actively inflating costs by 25% with no warning.

## 3. Batch API / Async Pricing Tier Usage

The Batch API offers a flat 50% discount on all input and output tokens, and it stacks with prompt caching for up to 95% total cost reduction.

- **Harnesses:** **Temporal** maintains a specific architectural pattern for the Anthropic Message Batches API, using its durable workflow state to submit 10,000+ queries, hibernate, and poll for results within the 24-hour window. Frameworks adhering to the **12-Factor Agents** methodology (Factor 11: "Trigger from anywhere") accommodate this well. Conversely, interactive IDE harnesses like **Cline** and **Roo Code** cannot use it.
- **Mechanisms:** Tasks are bundled into JSONL files and submitted asynchronously, with results mapped back via `custom_id` strings (since results return out-of-order).
- **Tradeoff:** You trade synchronous latency for massive cost savings. It is ideal for bulk evaluations, document classification, or overnight ETL. **However, it fundamentally breaks sequential agentic workflows.** Because step N+1 cannot execute until step N returns (which can take up to 24 hours), it is impossible to use the Batch API for autonomous, multi-step chain-of-thought loops.

## Phase 2 Cost-Budget Questions for the Systems Architect

Because the corpus demonstrates that **the cost ceiling is workload-determined, not architecture-determined**, the architect cannot finalize the harness without surfacing these specific questions to stakeholders in Phase 2:

1. **What is our sub-task predictability and routing distribution?** *(If 80% of tasks are predictable, we can use static routing to cheap models. If tasks are highly unpredictable, we must pay the latency/cost tax of an LLM-as-router to evaluate every prompt.)*
2. **How static is our tool catalog and system prompt?** *(If our tool definitions mutate per session or we inject dynamic user-data into the system prompt, we will suffer "silent zero-cache" penalties. If they are perfectly static, we can reduce input costs by 90%.)*
3. **What is the write-contention and parallelism value of the workload?** *(Anthropic's multi-agent orchestrator-worker pattern costs ~15x more tokens than a single chat. Does the workload's requirement for parallel, breadth-first exploration justify a 15x cost multiplier, or can we constrain it to a single, serial agent?)*
4. **Can any part of the workload tolerate >1 hour latency?** *(If the workload is purely asynchronous background research or data synthesis, we can cut costs in half instantly via the Batch API. If it is a synchronous user-facing chatbot, the Batch API is completely off the table.)*
