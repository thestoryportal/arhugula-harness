# Architectural Tensions and Tradeoffs in LLM System Design

While the provided sources do not explicitly use the terminology "T-perm-1, T-perm-2, or T-perm-3," the Pattern Reference Catalog and Cluster 5 V2 §3 detail permanent, cross-cutting architectural tensions (labeled T1 through T4) that **"the design phase, not catalog construction, is the appropriate locus for resolution"**. Because these tensions represent fundamental software engineering tradeoffs applied to LLMs, they cannot be eliminated by better models; they must be deliberately absorbed.

## The Core Architectural Tensions

At the architectural level, the unresolved tensions are:

### 1. Filesystem-as-Orchestrator vs. Framework-Orchestration (Catalog T1)

- **The Tension:** Does coordination logic (sequencing, state management, scope) live in folder structures and files, or within application code graphs?
- **How Sources Address It:** The Interpretable Context Methodology (ICM) and Meta-Harness embrace the filesystem as the coordinator—folder hierarchies determine agent scope. In contrast, deepagents, Dify, and VoltAgent utilize framework-managed graphs. *12-Factor Agents* absorbs this tension by splitting the difference: the filesystem manages business state (Factor 5), but the control flow remains in application code (Factor 8).

### 2. Single-Process Harness vs. Multi-Process Topology (Catalog T2)

- **The Tension:** Context coherence versus fault isolation. A single process effortlessly shares prompt caches, working state, and observability streams, while a multi-process architecture survives sub-agent crashes but demands complex coordination machinery.
- **How Sources Address It:** Cline, OpenHands, and VoltAgent operate as single-process harnesses. Openrig explicitly relies on a multi-process approach, orchestrating a topology of agents via tmux panes. Optio and Agent Control Plane (ACP) push this entirely to the infrastructure layer, using Kubernetes pods and Custom Resource Definitions (CRDs) for state.

### 3. Markdown-Spec-Driven vs. Code-Driven Configuration (Catalog T4)

- **The Tension:** Human reviewability versus programmatic expressivity.
- **How Sources Address It:** Maestro, Trellis, and Agency-Agents author their agent definitions, skills, and workflows strictly in Markdown, meaning any host harness can read them. Conversely, deepagents, VoltAgent, and OpenHands encode workflows in Python or TypeScript, gaining dynamic logic execution (like dynamic dispatch) at the cost of cross-platform portability.

## Displacing Tensions vs. Eliminating Them

Frameworks frequently market solutions that claim to resolve architectural tensions, but a closer look reveals they often merely **shift the hard problems to the application developer**.

- **Durable Execution vs. Checkpointing:** Frameworks like LangGraph, CrewAI, and Google ADK offer "checkpointing" as a solution to the fragility of long-running tasks. However, critics like Diagrid note this displaces the tension: checkpoints act as save points, but they lack automatic failure detection, lease coordination, or guaranteed resumption. The framework hands the developer a snapshot and shifts the distributed-systems problems (deduplication, race conditions on resumption) back to the application layer.
- **Parallel Multi-Agent Writes:** Early multi-agent frameworks attempted to eliminate task-time limitations by allowing swarms of agents to write code collaboratively. Cognition discovered this led to clashing edits and "digital gossiping". They eventually displaced the tension by conceding that while *reads* (exploration and context gathering) can be parallelized through sub-agents, *writes* must remain strictly single-threaded.

## Honest Tension Absorption in Practice

Honest absorption means accepting the inherent costs of a tradeoff rather than hiding behind abstractions. In practice, this looks like:

- **Accepting Boilerplate for Reliability (12-Factor Agents):** HumanLayer honestly absorbs the tradeoff of avoiding "magic" frameworks. The author explicitly acknowledges that prioritizing deterministic reliability and clear control flow inherently requires "more code to write and more setup and glue code".
- **Accepting File Rituals over Infinite Context (Anthropic):** Rather than pretending massive context windows eliminate "context rot," Anthropic absorbs the tension by requiring agents to use explicit, durable file handoffs (like `claude-progress.txt` and `feature_list.json`). They openly admit that simple "compaction isn't sufficient" for long horizons and instead force the agent to re-read ground-truth files on every session boot to stay anchored.
- **Accepting Scaling Limits (ICM):** ICM candidly absorbs the limitations of its local-first, folder-driven architecture by admitting that its methodology "does not work for... high-concurrency multi-user systems" to preserve operational simplicity.
- **Accepting Infrastructure Tax for Token Savings (MCP):** Anthropic's *Code-Execution with MCP* achieves a massive 98.7% reduction in token costs by dynamically loading tools from the filesystem. However, they honestly absorb the security tension by acknowledging this pattern is unsafe by default and strictly "requires a secure execution environment with appropriate sandboxing" to prevent system compromise.
