# Spec Layer: Observability

The specifications implement **observability** not as an afterthought, but as a rigid, multi-layered architectural contract designed to guarantee deterministic tracking, cost auditing, and safety compliance across all execution paths.

This observability framework is structured around several core components:

### 1. The OpenTelemetry (OTel) GenAI Base Layer
The harness standardizes on the **OTel GenAI semantic conventions (semconv 1.41.0 / GenAI doc v1.36.0+)** [395] as its foundational trace schema. Although these specs are technically flagged as "Development" status, the harness pins specific instrumentation versions to manage breaking changes stably [393].

The core span name format enforces `{gen_ai.operation.name} {gen_ai.request.model}` with `CLIENT` span kinds for model calls [395]. The harness establishes a strict **span hierarchy** for correlation [393]:
$$	ext{invoke\_agent (parent)} ightarrow 	ext{chat} + 	ext{execute\_tool (children)} ightarrow 	ext{child invoke\_agent (sub-agent handoff)}$$
Trace context is propagated across sub-agent boundaries using standard W3C headers to preserve the parent `gen_ai.conversation.id` [393].

### 2. The Eleven-Namespace Export Map (6 + 4 + 1)
The Control Plane and Action Surface axes export exactly **eleven namespaces** to the Operational Discipline axis, structured across three distinct ingestion paths to avoid conflation [710]:
*   **Six Specialization-Layer Namespaces (Ingested at D6 §1.2)** [710, 712]:
    *   `engine.*` [712]: Exposes `engine.class`, `engine.event_history.tier`, and `engine.event.id` to identify the underlying durable execution engine.
    *   `topology.*` [712]: Logs the active multi-agent configuration, cost budget, and cascade policies.
    *   `subagent.*` [712]: Tracks per-sibling token usage and results during parallel fan-out.
    *   `hitl.*` [712]: Exposes human-in-the-loop metrics (`hitl.gate.evaluated`, `hitl.invocation.opened`, `hitl.invocation.responded`, `hitl.invocation.timed_out`).
    *   `audit.*` [712]: Emits cryptographic signature and actor provenance fields per persona tier.
    *   `validator.fail.*` [712]: Dissects inline validation failures into a discriminated five-class fail taxonomy (e.g., transient vs. permanent).
*   **Four F3-Capability-Floor Lifecycle Event Namespaces** [710, 713]:
    *   `fallback.*` [713]: Attribute set for `fallback.triggered` and `fallback.exhausted` events.
    *   `retry.*` [713]: Attaches to `retry.attempt` loop iterations.
    *   `lease.*` [713]: Manages concurrency locks to prevent split-brain state re-execution.
    *   `harness.breaker.*` [713]: Captures per-model or per-provider circuit-breaker trip events (`breaker.tripped`) using a canonical seven-attribute schema [401].
*   **One Inheritance-Composition Namespace** [710, 714]:
    *   `routing.*` [714]: Captures provider-level and model-level routing layers (`manifest`, `embedding`, `llm_as_router`, or `fallback`) on the parent `llm.inference` span.

### 3. Sampling Discipline and Always-Sampled Exception Set
To control telemetry volume without losing critical data, the specifications define two operational sampling regimes:
*   **Mode-by-Surface** [827]: Local-development environments default to **head-based sampling** for immediate feedback, while self-hosted and managed-cloud servers enforce **tail-based sampling** [827]. Tail-sampling uses *tail-keep-on-classification* to preserve full span trees if a permanent failure, sandbox violation, or circuit breaker trips [830].
*   **The Always-Sampled Set (Head=1.0)** [828]: Critical security, cost-attribution, and governance events bypass any sampling rate-limits and are always recorded. This includes `sandbox.violation`, `sandbox.tier_escalation`, all `hitl.*` events, `fallback.triggered`, `breaker.tripped`, `topology.fanout.opened/closed`, `subagent.span.closed`, and `mcp.tool.call` [828].
*   **Cardinality-Safe-Attribute Discipline** [832]: High-cardinality attributes (like `gen_ai.conversation.id`, `idempotency_key`, and cryptographic hashes) are strictly restricted to span attributes and are **never** permitted as metric dimensions to prevent backend-side cardinality blowup [832].

### 4. Redaction and the "Structure-Not-Content" Invariant
To meet strict security requirements, the specifications apply a **structure-not-content principle** [834] to default logging:
*   **Omitted Raw Payloads** [833]: Content-bearing attributes (such as messages, system instructions, tool arguments, and results) are **default-off** across all cells [833]. Only structural metadata—such as SHA-256 hashes of inputs and outputs—is logged to preserve auditability without PII or credential disclosure [834].
*   **Pre-Collector Redaction** [837]: At the `multi-tenant-compliance` tier, the harness eliminates the security vulnerability of unredacted content sitting in the memory-buffered `BatchSpanProcessor` [837]. Spans are parsed through an eval-grade redaction pipeline **at the SDK/wrapper boundary** before being pushed to the collector, sanitizing sensitive strings into opaque tokens pre-buffer [837].

### 5. Cost-Attribution-per-Span Engine
The Operational Discipline axis implements a dedicated cost calculation engine computed per-span [839]:
*   **Pricing Formula** [840]:
    $$	ext{cost} = (	ext{input\_tokens} 	imes 	ext{BASE\_INPUT}) + (	ext{output\_tokens} 	imes 	ext{BASE\_OUTPUT})$$
    Input tokens include both `cache_creation` and `cache_read` tokens, which are attributed on the `llm.inference` span [841]. The formula reads these natively while adjusting for Anthropic’s prompt-caching discounts to prevent double-counting [841].
*   **Sandbox-Tier Overhead** [840]: Emits a `sandbox.cost.tier_overhead_*` metric to charge the workflow for physical sandbox resource consumption (such as microVM cold starts or dedicated VM provisioning premiums) [840].
*   **Tokenization-Version Anchor** [845]: To prevent silent dashboard breakage on model updates (e.g., Opus 4.7’s tokenizer drift that can silently spike token usage by up to 35% for identical text [399]), dashboard queries are forced to join on a versioned price table keyed on `(provider, model, tokenizer_version)` [846].
*   **Replay Deduplication** [841]: Spans are tagged with the parent's canonical `idempotency_key` to allow the cost-attribution engine to deduplicate and prevent double-counting during durable replay loops [841].

### 6. Operator-Burden Evals and Drift Detection
To verify alignment and track performance decay, the specifications implement out-of-loop evaluations [851]:
*   **Five Core Primitives** [852]: Tracks expected HITL invocations, expected sandbox violations, sandbox-tier-routing accuracy, cache-hit-rate alignment-floor, and routing-accuracy holdout.
*   **`gen_ai.eval.kind` Separation** [852]: The harness uses this attribute to cleanly isolate inline execution validations (`inline_gate`, which block the runtime and trigger escalations) from asynchronous evaluations (`offline_judge`, which score traces out-of-loop) [852].
*   **Separate Child Span Emission** [853]: Out-of-loop judges are structurally prohibited from emitting evaluations as mere span events [853]. Instead, they must emit as **separate child spans** to preserve trace identity, which is required for meta-evaluations (evaluating the evaluators) [853].
*   **Drift-Detection Events** [853]: Breaching an operator-defined alignment floor (e.g., if the judge-human Cohen's $\kappa$ drops) triggers a `gen_ai.eval.alignment_floor` event on the trace to signal that the model’s real-world behavior has drifted and needs re-baselining [853].

### 7. Deployment-Surface Matrix (Local-First vs. Multi-Tenant)
Observability implementations scale cleanly across the harness's **9-cell deployment-surface × persona-tier matrix** [801, 803]:
*   **Solo-Developer × Local-Development (Cell-1)** [803, 854]: Runs an **in-process OTel collector** (`otelcol-contrib`) directly within the harness [854]. Spans are buffered via a 5-second `BatchSpanProcessor` window and flushed to a local **SQLite-backed ring-buffer** (Tier-3 storage) [854]. The operator inspects, navigates, and debugging-walks these traces locally via a terminal-native **TUI trace browser** [855].
*   **Team-Binding × Self-Hosted (Cell-5)** [803, 857]: Leverages a sidecar or DaemonSet collector to route telemetry asynchronously to a dedicated multi-node observability backend (such as a self-hosted ClickHouse-backed Langfuse instance or Grafana stack) [857].
*   **Multi-Tenant-Compliance × Managed-Cloud (Cell-8)** [803, 857]: Combines pre-collector SDK-level redaction, per-tenant OTLP resource partitioning, and HSM/KMS-secured cryptographic signatures on every event to guarantee secure, multi-tenant trace isolation [857].
