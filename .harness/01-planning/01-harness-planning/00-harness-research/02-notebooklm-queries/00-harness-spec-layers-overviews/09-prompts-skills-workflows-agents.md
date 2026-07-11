# Spec Layer: Prompts, Skills, Workflows, and Agents

The finalized system specifications for the custom multi-LLM agent harness implement a rigorous, contract-governed lifecycle to manage **prompts, skills, workflows, and agents**. This architecture replaces ad-hoc runtime loops with deterministic, audit-compliant, and cost-controlled execution.

### 1. Prompts

#### Creation & Management
*   **Plain-Text File Ingestion**: Prompts are treated as first-class, versioned software artifacts authored manually as plain-text files in Git [326].
*   **Atomic Deployment**: Prompts reside in the *procedural* layer of the harness’s five-tier context hierarchy [321, 322]. They are checked into version control to guarantee **atomic deployments** of prompts alongside code, evaluation configurations, and the model routing manifest [326, 752].
*   **Static/Dynamic Partitioning**: To maximize caching efficiency, prompt creation enforces a strict separation between stable static instructions (the prefix) and request-specific variables (the suffix) [321, 324].

#### Invocation
*   **Multi-Segment Caching**: The harness configures up to four explicit `cache_control` breakpoints [324, 627] to cache cumulative prompt prefix blocks (e.g., tools, system instructions, and stable history) independently.
*   **Pre-Warming Prefills**: During process boot, the harness triggers a warm-up call using `max_tokens: 0` [324, 627] to pre-warm the static prefix cache, eliminating the Time-To-First-Token (TTFT) penalty for incoming runs [324, 627].
*   **Selective Section Routing**: To keep context windows lean, stage contracts (`CONTEXT.md`) extract only targeted file headers and sub-sections rather than loading monolithic repositories [770].

#### Evaluation (Evals)
*   **Assertion-First CI Gates**: Every prompt modification is validated via a fast, deterministic pre-commit CI gate executing cheap, code-based assertions (schema validation, regex checks, and execution tests) over a 20–50 trace dev fixture (budgeted under 30 seconds) [326].
*   **Aligned LLM-as-a-Judge**: Qualitative prompts undergo offline pre-deployment evaluation against a 100-trace held-out gold set using an LLM-as-a-judge [326]. Release is gated on the judge satisfying strict **Cohen’s Kappa ($\kappa \geq 0.7$)** [326] and **True Positive/Negative Rate ($TPR \geq 0.9, TNR \geq 0.85$)** thresholds against a principal human expert [326].
*   **Zheng et al. Bias Mitigations**: To prevent evaluation corruption, LLM-judges implement pairwise position-swapping, length-normalization rubrics, and mandatory cross-family grading (e.g., a GPT-class judge evaluating Claude-class outputs) [362].

#### Observability & Improvement
*   **OTel Span Ingestion**: Prompt performance is captured on the `llm.inference` span via OTel semantic conventions [395].
*   **Cache Attribution**: The `anthropic.*` telemetry namespace logs granular metrics including `cache_creation_input_tokens`, `cache_read_input_tokens`, `thinking_budget_tokens`, and the active `cache_breakpoint_id` [574].
*   **Weekly Error-Analysis Cycles**: In line with Hamel Husain's methodology, developers conduct manual error analysis on over 100 fresh production traces weekly, translating persistent generalization failures into new code-based assertions [326].

---

### 2. Skills

#### Creation & Management
*   **`agentskills.io` Open Standard**: Skills are packaged as directory-bounded folders containing a canonical `SKILL.md` file [366]. Frontmatter YAML strictly requires a unique lowercase, alphanumeric name ($\leq 64$ characters, no vendor reserved words) and a description ($\leq 1024$ characters) [369].
*   **Stateless Executables**: Skills compose declarative instructions with executable assets (e.g., custom Python validators, RAG tools) stored inside nested `scripts/` and `references/` directories [366].

#### Invocation
*   **Progressive Disclosure**: To prevent context bloat, Skills scale up through a three-level progressive-disclosure protocol (`C-AS-13` [366, 567]):
    1.  *Metadata Layer*: Frontmatter (~100 tokens [369]) is always loaded into the system prompt for tool discovery.
    2.  *Body Layer*: The complete `SKILL.md` instructions ($<5,000$ tokens [366, 369]) are loaded only when the model invokes the Skill.
    3.  *File Layer*: Associated scripts are executed on-demand in isolated runtimes [366, 369].
*   **Tool Search and Lazy Loading**: When the registered Skill count exceeds the $30	ext{--}50$ limit where model selection accuracy degrades, the harness triggers the **Tool Search Tool**, lazy-loading full Skill schemas on-demand via search reference blocks [370].

#### Evaluation, Observability & Improvement
*   **Authoring-Time Verification**: Skill registration requires declaring a `minimum_tier` for sandbox execution, preventing un-audited or under-isolated tools from entering the registry [540].
*   **`skill.activation` Spans**: Skill execution emits a parent `skill.activation` span containing `skill.id`, `skill.name`, `skill.body_tokens`, and `skill.version_sha` (the git content hash acting as a replay-determinism anchor) [576].
*   **Self-Evolution**: Skills support a **"Skill Self-Evolution"** instruction block, allowing the agent to dynamically update its own `SKILL.md` workflows after completing complex tasks [46, 48].

---

### 3. Workflows

#### Creation & Management
*   **Stateless Reducers**: Workflows are modeled as deterministic, interruptible pipelines where the agent acts as a stateless reducer (`(state, event) ightarrow next\_step` [296, 381]) with durability handled by the outer harness.
*   **Declarative Manifests**: High-level execution flow is registered in a static, git-versioned routing manifest mapping workflow steps to model bindings and defaults [638, 752].
*   **Durable State Checkpoint-Syncing**: Durability is managed by a **durable-execution coordination spine** [608]. Based on the deployment target, it executes under one of five committed engine classes (e.g., *event-sourced-replay* via Temporal, *save-point-checkpoint* via LangGraph) [654].

#### Invocation
*   **Idempotency-Keyed Exactly-Once Semantics**: Every workflow step and tool invocation requires an idempotency key generated as:
    $$	ext{idempotency\_key} = 	ext{sha256}(	ext{conversation\_id} \mathbin{\Vert} 	ext{step\_index} \mathbin{\Vert} 	ext{tool} \mathbin{\Vert} 	ext{canonical\_args})$$ [404]
    Duplicate writes are resolved as idempotent no-ops against the F2 state-ledger [758].
*   **Per-Step Annotation Overrides**: Manifest defaults can be overridden at individual steps using fine-grained `@f3_invocation` decorators to tune durability and checkpoint cadences [650].

#### Evaluation & Observability
*   **OTel Agent Trace Hierarchy**: Telemetry is propagated through standard W3C context headers to produce a fully nested tree: `invoke_agent` (Parent) $ightarrow$ `chat` + `execute_tool` (Children) $ightarrow$ child `invoke_agent` (Sub-agent) [393].
*   **Durable Replay Resumption**: Upon resuming from a crash, the engine emits a `workflow.resumption` event carrying a `resumption.kind` attribute [657] to guarantee that already-completed steps are read from the state-ledger and never re-executed [657].

#### Improvement
*   **Outer-Loop Optimization**: Discovered through research-grade patterns (e.g., Stanford's *Meta-Harness*), the harness can be optimized by an outer search loop where a coding agent proposer reviews prior execution traces, scores, and codebases on the filesystem, mutating the harness configuration toward a Pareto-frontier of accuracy and context token costs [11, 451].

---

### 4. Agents

#### Creation & Management
*   **Markdown Personas**: Agents are created as task-focused specialist roles (e.g., Sisyphus, Hephaestus, Oracle, or Architect) defined in Markdown specification files [118].
*   **Git Worktree Isolation**: To run parallel, concurrent agent executions without file contention, the harness spawns sub-agents into isolated **Git Worktree** directories pointing back to the same underlying repository storage [764, 765].

#### Invocation
*   **The Orchestrator-Workers Brief**: Parent orchestrators dispatch sub-agents through a structured `task()` tool call wrapping a **four-field Brief object** contract [290, 670]:
    1.  `objective`: Bounded task goal [670].
    2.  `output_format`: Expected JSON output schema [670].
    3.  `tool_guidance`: Whitelisted tools and filesystem paths [670].
    4.  `task_boundaries`: Explicit constraints to prevent task-drift [670].
*   **Monotonic Sandbox-Tier Ascension**: Sub-agents inherit privileges under a strict rule of monotonic sandbox-tier ascension:
    $$	ext{sub-agent sandbox tier} \ge 	ext{parent sandbox tier}$$ [565, 669]
    Any attempt to downgrade containment boundaries is structurally rejected and logged as a policy violation [692].

#### Evaluation (Validators)
*   **Asymmetric Clean-Context Verification**: High-risk write operations undergo review via independent **Verifier Agents** running with inputs disabled or limited to prevent semantic bias and context rot [389].
*   **Pre-HITL Escalation Staircase**: If a sub-agent's action fails validation, the Control Plane executes a strict, automated recovery sequence [702]:
    1.  *First Failure*: Triggers exponential backoff with full jitter, or Reflexion-style verbal self-correction in-context [702].
    2.  *Second Failure*: Triggers a **Model-Tier Escalation** [659, 669], programmatically hot-swapping the active model for a more capable reasoning class (e.g., Haiku &rarr; Sonnet &rarr; Opus).
    3.  *Third Failure / Budget Exhaustion*: Bypasses the loop and halts, routing the complete execution history to a Human-in-the-Loop (HITL) gate [702].

#### Observability & Improvement
*   **`subagent.*` Telemetry**: Sibling agents emit a dedicated `subagent.span` tracking `subagent.result_status` (`completed`, `failed`, or `cascade-cancelled`) along with raw and cached input/output token counts [674].
*   **Cross-Sibling Audit Rollup**: Once parallel workers complete, a cryptographic Merkle root of the sibling ledgers is generated and appended as a standalone `parent_fanout_close_entry` primitive on the parent's ledger [677, 679].
