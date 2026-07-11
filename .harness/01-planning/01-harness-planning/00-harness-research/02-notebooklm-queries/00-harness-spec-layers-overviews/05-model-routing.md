# Spec Layer: Model Routing

The specifications for the custom multi-LLM agent harness implement **model routing** through a highly disciplined, multi-layered architecture designed to maximize reasoning performance, maintain cache friendliness, and enforce strict budget limits.

The specifications outline several interconnected layers and contracts to manage how and where LLM queries are dispatched:

### 1. The Cheapest-Deterministic-First (CDF) Layered Strategy
To manage model invocation without vendor lock-in or cost runaways, the Control Plane specification establishes a **three-tier resolution sequence** (`C-CP-02` [637, 638]). The core philosophy is to resolve the routing decision at the cheapest, most deterministic layer possible before escalating to probabilistic methods:
*   **Layer 1: The Declarative Manifest** [638] — The default static tier. It checks a version-controlled configuration file residing on the filesystem [770] that explicitly binds specific `(agent_role, workflow_class, step)` tuples to designated models [638]. This lookup is **fully deterministic** and incurs **zero inference cost** [638].
*   **Layer 2: The Embedding Classifier** [638] — If the manifest does not explicitly bind the active step, the harness invokes a local embedding classifier. It performs a $k$-nearest neighbor lookup against a task-context corpus to classify the required model tier, resolving only if the classifier’s confidence exceeds a defined threshold [638]. This is highly deterministic and incurs only the cost of a local embedding call [638].
*   **Layer 3: LLM-as-Router** [638] — Utilized as an opt-in, last-resort dynamic dispatcher when prior layers fall through. The harness passes the task context to a fast, lightweight reasoning model (such as a Haiku-class model) that acts as an intelligent router [638]. This layer is probabilistic and carries the highest latency and token overhead [638].

### 2. Per-Sub-Agent-Role & Model-Temperament Binding
Rather than using a single omni-model, the specifications mandate a **per-sub-agent-role × model-binding contract** [669]. This allows the harness to assign specific models to specific roles based on "temperament," task complexity, and cost [669]:
*   **Lead/Orchestrator & Generator** roles are bound to high-tier reasoning models like **Sonnet 4.6** (or **Opus 4.6** for multi-tenant compliance) [669].
*   **Evaluator** roles are also bound to **Sonnet 4.6** (capped at 1–3 parallel instances) [669].
*   **Reviewer** and **Sub-agent parallel workers** are downgraded to cheaper, faster models like **Haiku 4.5** (capped at 3 parallel instances) [669] to conduct broad exploration reads without draining the token budget [669].

### 3. Time-Budgeted Fallbacks & Cross-Family Chains
To ensure high system reliability, the routing architecture implements strict time budgets and fallback paths:
*   **Per-Layer Time Budgets** [640] — Every routing layer is bound to an operator-configurable time budget. If a layer exceeds its allotted time or experiences a capability shortfall [644], the system triggers a **deterministic, unconditional fall-through** to the next routing layer or model [640].
*   **Circuit Breakers** — Circuit breakers are mapped per `{provider, model}` instance. When a breaker trips (monitored via the canonical `harness.breaker.*` schema), the system bypasses that endpoint and advances down the fallback chain [401, 404].
*   **Provider-Sticky Session Keys & Cache Protection** [642] — Fallback chains prioritize same-provider model variants first (e.g., falling back from Claude Opus to Claude Sonnet) [404]. If a fallback must cross provider families (e.g., Anthropic to OpenAI), it triggers a `fallback.cross_family_triggered` event, invalidates the previous provider-specific prompt cache, and binds a **provider-sticky session key** [404, 642]. This prevents "cache-miss-storms" and protects the prompt cache locality for the remainder of the session [404].

### 4. Telemetry and Run-Event Attribution
To ensure compliance-readiness and full auditability, every routing decision is captured at the LLM call surface via OTel-compliant `llm.inference` span attributes [634]. The system captures:
*   `routing.provider` [634]: The provider identity bound at the call (e.g., Anthropic, OpenAI).
*   `routing.model` [634]: The specific model version utilized.
*   `routing.layer` [634]: The exact routing layer that produced the binding (`manifest`, `embedding`, `llm_as_router`, or `fallback`).
*   `routing.binding_rationale` [634]: A short token explaining why the specific path was selected.
