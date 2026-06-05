# Architectural Topologies for Multi-Agent Systems

The corpus reveals that multi-agent topologies are not interchangeable solutions to be chosen by preference; rather, they are structural commitments that must be strictly mapped to the workload's constraints.

## Topology to Workload Mapping

### 1. Orchestrator-Worker

- **Concrete Examples:**
  - Anthropic's Multi-Agent Research System (a Lead Researcher agent spawns specialized subagents and synthesizes their findings).
  - Microsoft Agent Framework's "Magentic" pattern (a dedicated manager agent dynamically maintains a task ledger and coordinates specialized worker agents).
  - Dify's Supervisor Mode (a supervisor agent coordinates multiple sub-agents for complex multi-step tasks).
- **Predictive Workload Characteristics:**
  - **Parallelism Shape:** Highly parallel but strictly *read-oriented* (breadth-first exploration, data gathering). The corpus explicitly warns against using this for parallel writes due to "digital gossiping" and conflicting code modifications.
  - **Decision-Graph Branching Factor:** Unpredictable and highly branched. It fits "complex tasks where you can't predict subtasks needed" upfront.
  - **Error-Recovery Depth:** Centralized. The orchestrator isolates failures within specific workers, preventing them from corrupting the master plan.
  - **Latency Tolerance:** Moderate to high. Synchronous execution means the entire system can bottleneck waiting for the slowest subagent to return.

### 2. Decentralized Handoff

- **Concrete Examples:**
  - OpenAI Agents SDK "Handoffs" pattern (an agent fully transfers control to another, represented to the LLM as a tool call).
  - Microsoft Agent Framework's "Handoff" orchestration (agents connected directly in a mesh topology without a central orchestrator).
  - Ruflo's "Mesh" hive-mind topology (peer-to-peer pattern sharing context without hierarchical management).
- **Predictive Workload Characteristics:**
  - **Decision-Graph Branching Factor:** Linear or highly gated. Best for systems where progression relies on context or expertise thresholds, such as customer support triage where full ownership must transfer.
  - **Parallelism Shape:** Sequential by handoff edges (low parallelism).
  - **Error-Recovery Depth:** Shallow and fragile. The corpus notes this pattern has the "lowest" reliability and the "hardest" debuggability because state is distributed across a mesh rather than maintained by a central manager.
  - **Latency Tolerance:** Low to moderate, as tasks are sequentially passed to specialists to rapidly resolve user-facing requests.

### 3. Hierarchical Sub-agent

- **Concrete Examples:**
  - Cursor's Planners/Workers/Judges (planners recursively spawn sub-planners to explore codebases before dispatching isolated workers).
  - Cognition's "Manager Devin" (spawns child Devins via internal MCP to handle multi-PR scopes).
  - Google ADK (framework explicitly designed for hierarchical composition and complex multi-layer coordination).
- **Predictive Workload Characteristics:**
  - **Decision-Graph Branching Factor:** Deeply nested. Designed for massive scale tasks (e.g., modernizing legacy code, multi-PR projects) where tasks can be infinitely decomposed into smaller self-contained scopes.
  - **Parallelism Shape:** Tree-structured. Parent agents maintain the high-level plan while children explore extensively with their own isolated context windows.
  - **Error-Recovery Depth:** Deep and isolated. Sub-agent branches can be abandoned or retried without polluting the parent's context window with "exploration dead-ends".
  - **Latency Tolerance:** Very high. These are "long-horizon" tasks operating over hours or days.

### 4. Evaluator-Optimizer Loop

- **Concrete Examples:**
  - Anthropic's baseline Evaluator-Optimizer pattern (one LLM generates a solution, another critiques and provides feedback in a loop).
  - Reflexion (an Actor/Evaluator/Self-Reflection trinity that converts binary environment feedback into a textual summary added to the next trial's memory).
  - disler's "the-verifier-agent" (a two-agent observer system running a read-only, input-disabled verifier in parallel with a generator).
- **Predictive Workload Characteristics:**
  - **Error-Recovery Depth:** Extremely deep. This topology is entirely predicated on iterative self-correction and relies heavily on catching and recovering from errors.
  - **Decision-Graph Branching Factor:** Low (typically a cyclical, single-path loop).
  - **Parallelism Shape:** Sequential generation and critique, though the evaluation itself can occasionally be fanned out.
  - **Latency Tolerance:** High. The back-and-forth critique cycle drastically increases task completion time. It requires workloads with clear, objective success criteria (like test suites or strict rubrics) to prevent endless loops.

### 5. Single-agent ReAct

- **Concrete Examples:**
  - Claude Code CLI (a single agent utilizing a loop of file reads, bash executions, and edits).
  - Hugging Face smolagents' CodeAgent (a barebones loop that writes Python code snippets to execute external actions).
  - 12-Factor Agents' Micro-Agents (small, focused 3-20 step agents embedded within deterministic DAGs).
- **Predictive Workload Characteristics:**
  - **Parallelism Shape:** Strictly serial. It is the optimal choice for "tight coordination," context-sensitive operations, and sequential write tasks.
  - **Decision-Graph Branching Factor:** Low. Ideal for predictable, isolated modules or tightly coupled tasks where splitting context would break coherence.
  - **Error-Recovery Depth:** Shallow. Driven by immediate environment observation (e.g., executing code and reading the stderr).
  - **Latency Tolerance:** Low to moderate. Designed for fast execution without the communication overhead or token amplification of multi-agent orchestration.

## Where the Corpus is Thin or Speculative

- **Thin on Decentralized Handoff Reliability:** While the corpus defines the "Decentralized / Handoff" pattern (OpenAI/Microsoft), it provides almost no empirical performance metrics, success rates, or production case studies for it, explicitly noting it carries the "hardest" debuggability.
- **Speculative on Multi-Agent Code Generation:** Early claims by frameworks promoting swarms of agents collaboratively writing code were highly speculative. The corpus highlights a harsh reality check led by Cognition: parallel writing results in "digital gossiping" and catastrophic conflicting assumptions. The field has only recently converged on the idea that multi-agent systems are strictly for *reads/evaluations*, while writes must remain single-threaded.
- **Thin on Exact Thresholds for Topology Shifts:** The corpus notes that multi-agent systems use "~15x more tokens" than standard chat, but provides no formalized heuristics for exactly *when* an orchestrator should abandon a single agent and fan out, relying instead on manual prompt-engineered scaling rules (e.g., "if complex research, use 10+ subagents").

## Phase 2 Questions for the Systems Architect

To make the topology choice non-arbitrary in Phase 2, the systems architect must answer:

1. **What is the write-contention of the target workload?** (Are we primarily gathering and synthesizing information, or are we actively mutating a single, interdependent state like a codebase? *If mutating, default to Single-Agent ReAct or restrict sub-agents to read-only roles.*)
2. **Can the workload's evaluation criteria be programmatically codified?** (Is success objective enough to build a reliable test suite or rubric? *If yes, Evaluator-Optimizer loops are unlocked; if no, iterative loops risk endless hallucination drift.*)
3. **What is our hard latency and token budget?** (Can the system sustain a 15x token amplification and the synchronous waiting periods required for orchestrator-worker fan-outs, or is sub-second user responsiveness required?)
4. **Are the task boundaries predictable upfront?** (Can we define the entire process as a deterministic DAG, or do we need an Orchestrator to dynamically invent the decision tree on the fly based on intermediate observations?)
5. **How will we isolate context degradation?** (If the task exceeds ~35 minutes or requires reading dozens of irrelevant files, how will we sandbox that exploration so the main reasoning agent doesn't succumb to context rot?)
