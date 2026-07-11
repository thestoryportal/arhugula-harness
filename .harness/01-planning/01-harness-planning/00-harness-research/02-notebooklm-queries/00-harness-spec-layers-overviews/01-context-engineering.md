# Spec Layer: Context Engineering

The specifications for the custom multi-LLM agent harness implement **context engineering** as a rigorous, multi-layered discipline rather than an ad-hoc prompt-crafting exercise. The primary objective is to maintain a highly dense, high-signal context window that maximizes reasoning performance while controlling token costs and prompt-caching behaviors [321, 335, 420].

Here is exactly how context engineering is codified across the Information Substrate, Action Surface, Control Plane, and Operational Discipline axes:

### 1. The Five-Tier Artifact Layering Schema (`C-IS-02`)
The Information Substrate establishes a **strict five-tier context partition** [747, 748] to structure context loading and optimize the token budget:
*   **`working`**: Per-run scratch state. Resides on the filesystem and survives only a single inference call within a run [748].
*   **`episodic`**: Per-run history and in-flight conversational state [321, 322]. Resides on the filesystem and survives multiple inference calls within a run [748].
*   **`semantic`**: Cross-run knowledge artifacts and learned content [748].
*   **`procedural`**: Workflow-class procedural rules (such as YAML-frontmatter Skills, prompts, and the routing manifest) [748].
*   **`durable`**: The append-only state-ledger, JSONL event ledger, and audit ledger [748].

By structuring context into these explicit boundaries, the harness keeps the average context window per stage tightly scoped to **2,000–8,000 tokens** [748], compared to typical monolithic baselines of **30,000–50,000 tokens** [748].

### 2. Selective Section Routing (`C-IS-10`)
To prevent "context bloat" from loading massive monolithic files, the harness implements **selective section routing** [770]. The workflow's stage `CONTEXT.md` Inputs table dictates *which specific sections* of which files the agent is authorized to load [770]. Rather than forcing the model to read entire repositories, the harness injects only the relevant headers and sub-sections, keeping the active context window clean and focused [476].

### 3. XML Structured-Event Message Encoding
To maintain absolute control over token layout, the prompt management infrastructure utilizes **structured-event encoding** [330]. Instead of relying on raw, unstructured conversational history, the harness encodes arbitrary event sequences (tool calls, environmental changes, status updates) into a single, cohesive user message wrapped in **XML-style event tags** [330]. This prevents the model from suffering from "lost in the middle" degradation and ensures complete predictability of the token sequence [330].

### 4. Static-Prefix / Dynamic-Suffix Caching Discipline
The harness is architected around the strict invalidation hierarchy of Anthropic’s prompt caching: **tools &rarr; system &rarr; messages** [321, 324]. The specifications implement four key caching rules:
*   **Static/Dynamic Separation**: System prompts, static instructions, and tool definitions are placed at the top as a stable prefix, terminated by an explicit `cache_control` breakpoint [324, 627]. All highly variable content (such as user queries and timestamps) is forced into the dynamic suffix *after* the breakpoint to prevent cache invalidation [321, 324].
*   **Multi-Segment Breakpoints**: The harness supports up to **4 explicit breakpoints** [324, 627] to cache different, progressively changing blocks (e.g., tools, stable system rules, skill packs, and historical turns).
*   **Pre-Warming**: At process boot (and on a 4-minute keep-alive loop), the harness issues a `max_tokens: 0` pre-flight call [324, 627] with the breakpoint placed on the static prefix, populating the cache and **eliminating the first-request Time-To-First-Token (TTFT) latency** [324, 627].
*   **Tool-Set Freezing**: Rather than dynamically appending tool schemas to the API call (which instantly detonates the cache), the harness uses **code-execution-with-MCP** [421, 428]. It exposes the tool catalog as standard filesystem-resident files that the model discovers and reads via local bash commands [428]. The core `tools` array is frozen to a single `bash`/`read` tool, preserving prefix cache integrity [421, 428].

### 5. Multi-Tier Context Compaction & Selective Clearing
As long-running sessions approach the model’s context limit, the harness employs a **multi-tier context compaction and clearing system** [321, 422, 428]:
*   **Four-Tier Compaction**: It sequences through *MicroCompact* (in-place tool-output trimming), *AutoCompact* (triggered at 95–98% of the context window with a 13K-token reserve, limiting the summary to 20K tokens [422, 428]), *Full Compact* (resetting the working budget to 50K [422, 428]), and manual `/compact` commands.
*   **Selective Server-Side Clearing**: Using the `clear_tool_uses_20250919` and `clear_thinking_20251015` headers [428], the harness surgically drops token-heavy raw tool outputs from the message history while retaining the core reasoning chains [428].
*   **Constraint Preservation**: To prevent compaction from wiping out critical project instructions, the compaction prompt enforces a rule where the agent must write all unresolved bugs, key decisions, and open constraints to a durable, out-of-context `NOTES.md` file before the history is summarized [344].

### 6. Context Revalidation on Human-in-the-Loop Resume (`C-CP-22`)
During long asynchronous pauses (e.g., when the agent is waiting days for a human approval signal [422]), the active workspace is highly vulnerable to "context rot" and drift [422]. Upon resumption, the Control Plane executes a `material_diff` predicate [422]. It compares the active state of the filesystem, state-ledgers, and external MCP resources against a **pause-time snapshot** [422, 704]. Only the "material" delta is re-emitted into the context window, surgically rehydrating stale references without wasting context tokens on redundant data [422, 704].

### 7. Just-In-Time (JIT) Retrieval
To keep file-reading operations lightweight, the harness prefers **JIT retrieval over massive RAG-dumps** for engineering tasks [321, 336, 421]. The system prompt contains only lightweight identifiers (such as filesystem paths or directories) [336]. The agent is expected to navigate the workspace on-demand using native command-line primitives (`glob`, `grep`, `head`, `tail`) [321, 336, 428]. This isolates the detailed search context within transient, ephemeral sub-agent context windows rather than bloating the main coordinator's history [336, 428].

### 8. Context Isolation via Sub-Agent Briefs (`C-CP-13` / `C-CP-14`)
When launching concurrent sub-agents to parallelize work, the coordinator authors a highly typed **four-field Brief object** containing [290, 670]:
1.  **`objective`**: The scoped, bounded task goal [670].
2.  **`output_format`**: The structured output JSON schema [670].
3.  **`tool_guidance`**: Whitelisted tools and local filesystem paths [670].
4.  **`task_boundaries`**: Explicit boundaries to prevent sub-agent task-drift [670].

The sub-agent is fanned out into an isolated context [290]. It can explore, search, and parse files extensively—consuming tens of thousands of tokens within its own ephemeral window [295]—but it returns only a **condensed, 1,000–2,000 token summary** back to the coordinator [295], shielding the lead agent's context from clutter.

### 9. The "Docs-Over-Outputs" Invariant
To defeat the hazard of "context poisoning" (where a model-generated error in turn 3 is treated as authoritative, self-citing ground truth in turn 10 [346]), the specifications programmatically enforce a **docs-over-outputs convention** [476]. The harness requires that the model always retrieve reference documentation and specifications (Layer 3 "factory" content) to learn code patterns, rather than reading prior stage or sub-agent outputs (Layer 4 "product" content) [476].
