# Cluster Deep-Dive 4: Reliability, Observability, Security, and HITL

**Active session:** Cluster Deep-Dive 4 of multi-session agent-harness research project. Topics: (1) observability, (2) reliability primitives, (3) security and governance, (4) human-in-the-loop. Building on Sessions 1–3 / Clusters 1–3 substrate. Advanced Research mode. Target stack: solo founder, local-first, self-hosted n8n, RAG, Claude.ai, Claude Code CLI, Codex, multi-LLM, OpenClaw harness.

---

## §1 Executive Synthesis

The following findings are NEW relative to the Session 1 substrate. Confidence labels: [HIGH] = verified against primary source this session; [MODERATE] = strong inference from multiple primary or one primary + reputable secondary; [SPECULATIVE] = reasoned hypothesis without verified source.

1. **OTel GenAI semconv as a whole is still `Development` status, not Stable, as of semconv 1.41.0 / GenAI doc v1.36.0+** [HIGH]. Every `gen_ai.*` attribute on inference, agent, tool, retrieval, embedding spans is tagged `Development`; only `error.type`, `server.address`, `server.port` are `Stable`. The transition is gated by an `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental` env var. Practical implication: any vendor claiming "OTel-native" today is shipping against a moving target — pin instrumentation library versions, not the spec.

2. **Prompt-cache token attribution has dedicated OTel attributes — `gen_ai.usage.cache_creation.input_tokens` and `gen_ai.usage.cache_read.input_tokens` — both of which SHOULD be subsumed inside `gen_ai.usage.input_tokens` (i.e., not double-counted)** [HIGH]. Anthropic's break-even is 2 cache reads (5-min TTL @ 1.25× write / 0.1× read) or ~2 reads at 1-hour TTL (2× write / 0.1× read). For Claude Code style harnesses with stable system prompts, this changes the cost equation by ~10×.

3. **Claude Code's permission model is a three-tier `deny → ask → allow` evaluation order with first-match-wins, configurable per-tool with glob specifiers, plus five permission modes** (`default`, `acceptEdits`, `plan`, `dontAsk`, `bypassPermissions`) [HIGH]. This is the most concrete production tiered-autonomy implementation available; a documented bug (#6631) confirms `Read`/`Write` deny rules historically failed to enforce against the `Bash(cat ...)` escape hatch — defense-in-depth (permission rules + OS sandbox) is required, not optional.

4. **Anthropic published quantitative prompt-injection robustness numbers — a first** [HIGH]: Claude Sonnet 4.5 prevented 94% of attacks via MCP, 82.6% in computer-use, 99.4% on bash. Even the strongest number (99.4%) implies 1-in-167 attacks succeed. Simon Willison's frame ("99% is a failing grade in appsec") makes this disqualifying for any unsupervised lethal-trifecta-positive deployment.

5. **The lethal trifecta is structurally three properties — (a) access to private data, (b) exposure to untrusted content, (c) ability to externally communicate/exfiltrate** [HIGH]. Willison's argument: any agent with all three is structurally vulnerable regardless of model alignment; the only reliable mitigation is architectural — cut one leg. Filter-based mitigations top out at ~97% (LLM-as-judge), which is insufficient for production.

6. **Rehberger's "Month of AI Bugs" (Aug 2025) is no longer theoretical — it surfaced specific CVEs across most major coding agents** [HIGH], including: CVE-2025-53773 (GitHub Copilot RCE via prompt-injected `~/.vscode/settings.json` flipping `chat.tools.autoApprove: true`), CVE-2025-54132 (Cursor IDE arbitrary exfil via Mermaid image URLs), Amp Code RCE via `settings.json` rewrite, ChatGPT memory exfil via `*.blob.core.windows.net` URL allow-list, Devin (no protection at all), Google Jules (Markdown image exfil + invisible Unicode). Pattern: configuration files that the agent itself can write are the universal soft target.

7. **MCP authorization in spec 2025-06-18 is mandatory OAuth 2.1 + PKCE + RFC 8707 Resource Indicators; MCP servers MUST NOT pass through tokens received from clients to upstream APIs** [HIGH]. STDIO transports are explicitly excluded ("retrieve credentials from environment"). For the local-first stack, this means STDIO MCP servers carry zero protocol-level auth — sandbox is the only boundary.

8. **LangGraph's `interrupt()` API has a non-obvious semantic: resume re-executes the entire node from the beginning, not the line after the interrupt** [HIGH]. Side effects before `interrupt()` MUST be idempotent. `try/except` around `interrupt()` will swallow the special `GraphInterrupt` exception and break the pause. Multiple `interrupt()` calls in one node are matched to resume values by ordinal position. Resume is via `Command(resume=value)`. A checkpointer is mandatory at compile time.

9. **HumanLayer's 12 Factors are not "12 Factor Apps for AI" — they are a deliberate counter-framework argument that "agents are mostly software"** [HIGH]. Factors 5 (unify execution + business state), 6 (launch/pause/resume), 7 (contact humans with tool calls), 8 (own your control flow), 12 (stateless reducer) collectively argue for treating HITL as just another tool call against a durable event log, not a special framework feature. This is convergent with Temporal's signals model.

10. **Brooker's empirical comparison concludes "Full Jitter" wins on call count and "Decorrelated Jitter" wins on completion time, with "Equal Jitter" strictly dominated by "Full Jitter"** [HIGH]. The no-jitter case is so much worse on completion time it has to be omitted from comparison graphs. The N² nature of contention work is unchanged by jitter — jitter only smooths the spike pattern. For LLM rate limits with `Retry-After` headers, the right composition is: honor `Retry-After` if present, otherwise full-jitter exponential backoff capped at ~30s.

11. **Anthropic 429 vs 529 are categorically different and require different handling** [HIGH]. 429 = `rate_limit_error` (your quota), retry per `retry-after` header. 529 = `overloaded_error` (Anthropic-side capacity), retry with backoff but do NOT count against your quota theory. Claude Max plans return HTTP **402** (not 429) on rate-limit exhaustion — OpenClaw issue #30484 documents this misclassification, treating 402 as billing-out and surfacing a misleading error to users.

12. **Tool poisoning is not just description-level — Invariant Labs and CyberArk have demonstrated that tool *responses* and *rug-pulled descriptions* (clean at install, malicious after first use) are equally exploitable** [HIGH]. Invariant's `mcp-scan` tool exists specifically to detect poisoned descriptions. The MCP spec has no mechanism to verify runtime tool descriptions match the audited install-time descriptions — a chain-of-trust gap.

13. **OpenTelemetry GenAI conventions now define `invoke_agent {name}` and `execute_tool {name}` as the canonical span names with INTERNAL/CLIENT span kinds and a documented hierarchy: `invoke_agent` (parent) → `chat` + `execute_tool` (children) → child `invoke_agent` for sub-agent handoff** [HIGH]. GitHub Copilot Chat, Microsoft Agent Framework, and the OTel Python instrumentations now emit this hierarchy natively. Sub-agent handoff is properly nested via trace-context propagation.

14. **OpenClaw's harness architecture exposes a pluggable "Agent Harness" interface where `supports(ctx)` and `runAttempt(params)` are the two contract methods, and the runtime falls back to "PI" (their default harness) when no plugin claims a model** [MODERATE — based on the openclaw/docs DeepWiki and openclaw.ai docs surfaced this session]. Codex and Claude Code are wired in as native ACP-protocol harnesses. This makes OpenClaw an unusual fit for the multi-LLM stack since it can host multiple harnesses but session pinning persists across runs.

---

## §2 Per-Topic Deep Dives

### §2.1 Observability

**2.1.1 Topic restatement.** Observability for an agent harness means: capturing a per-step record of every LLM call, tool execution, retrieval, and sub-agent handoff with sufficient attribution to (a) compute cost per session and per tenant, (b) reproduce a failure deterministically, (c) drive online evaluation, and (d) feed reliability decisions (retry/breaker/escalate). The cluster's central question is whether to standardize on the OTel GenAI semantic conventions (cross-vendor portability at the cost of being on `Development`-status spec) or adopt a vendor LLM-obs platform's native model.

**2.1.2 Canonical sources, deeply engaged.**

- **OpenTelemetry GenAI Spans spec** (`opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/`, semconv 1.41.0). Status: **Development**. Key claims: span name format `{gen_ai.operation.name} {gen_ai.request.model}`; span kind `CLIENT` for inference (or `INTERNAL` if same process); operations enum: `chat`, `create_agent`, `embeddings`, `execute_tool`, `generate_content`, `invoke_agent`, `invoke_workflow`, `retrieval`, `text_completion`. Required attributes: `gen_ai.operation.name`, `gen_ai.provider.name`. Strengths: cross-vendor (Anthropic, AWS Bedrock, Azure, OpenAI, Cohere, DeepSeek, Gemini, Groq, IBM, Mistral, Perplexity, xAI all enumerated as known `gen_ai.provider.name` values). Weaknesses: every GenAI-specific attribute is `Development`; only `error.type`/`server.address`/`server.port` are `Stable`; content capture (`gen_ai.input.messages`, `gen_ai.output.messages`, `gen_ai.system_instructions`, `gen_ai.tool.definitions`) is `Opt-In` due to PII. Connections: directly determines what the reliability layer can observe (couples to §2.2 retry decision input).

- **OpenTelemetry GenAI Agent Spans** (`gen-ai-agent-spans/`). Status: Development. Key claims: span name `invoke_agent {gen_ai.agent.name}` (or `create_agent {name}`); attributes `gen_ai.agent.id`, `gen_ai.agent.name`, `gen_ai.agent.description`, `gen_ai.agent.version`; conversation correlation via `gen_ai.conversation.id`. Strengths: explicitly defines hierarchy (`invoke_agent → chat → execute_tool`), supports sub-agent handoff via standard trace context propagation. Weaknesses: agent-specific failure modes (handoff failure, sub-agent timeout, planner-loop divergence) have no dedicated attributes — instrumentations will reach for custom attributes and break portability.

- **OpenTelemetry GenAI Metrics** (`gen-ai-metrics/`). Required metric: `gen_ai.client.operation.duration` (histogram, seconds). Recommended: `gen_ai.client.token.usage` (histogram of token counts). Cardinality control: per spec, `gen_ai.request.model` and `gen_ai.provider.name` are the recommended dimensions; `gen_ai.conversation.id` is explicitly NOT recommended as a metric dimension (high-cardinality blowup).

- **GenAI Tool / Execute span** (per spec). Required: `gen_ai.operation.name=execute_tool`, `gen_ai.tool.name`. Recommended: `gen_ai.tool.call.id`, `gen_ai.tool.description`, `gen_ai.tool.type` (enum: `function` | `extension` | `datastore`). Opt-In: `gen_ai.tool.call.arguments`, `gen_ai.tool.call.result` (PII warning).

- **GenAI Retrieval span**. `gen_ai.operation.name=retrieval`, span name `retrieval {gen_ai.data_source.id}`. Opt-In `gen_ai.retrieval.documents` (array of `{id, score}`) and `gen_ai.retrieval.query.text`.

- **Datadog "LLM Observability natively supports OTel GenAI Semantic Conventions"** (Datadog blog). Key quoted phrase: "instrument your LLM applications once with OTel" and the version pin "v1.37 and up". Strengths: removes the parallel-instrumentation tax for Datadog users. Weaknesses: prior to this, vendor SDKs and OTel instrumentations were a parallel pipeline.

- **Microsoft Agent Framework observability docs** and **GitHub Copilot Chat OTel docs**. Both confirm the canonical hierarchy: `invoke_agent {name} → chat {model} → execute_tool {tool}` with trace-context propagation across sub-agent invocations. Copilot Chat documents the `github.copilot.chat.otel.captureContent` setting that toggles the `Opt-In` content capture.

- **Indragie Karunaratne / Sentry "Seer" writings** (`blog.sentry.io/seer-debug-with-ai-at-every-stage-of-development/`, Jan 2026; `blog.sentry.io/introducing-seer-agent/`). Key claim with quoted phrase: "deterministically traverse all the data relevant to a problem" because telemetry is "trace-connected". Argument: agent debugging requires a graph (errors → traces → spans → logs → source) walked deterministically, not LLM-on-text-search. Sentry's case study reports their internal AI failure was diagnosed in "seconds" because Seer Agent walked from a Sentry issue to the trace, to per-region routing, to provider-side rate-limits — an investigation that "would have taken at least half an hour" manually.

- **Langfuse / Arize Phoenix / LangSmith / Helicone** product docs and comparison surveys. Architectural distinctions:
  - **Langfuse**: ClickHouse-backed, SDK-based instrumentation, OTel-compatible ingestion, fully self-hostable with feature parity vs cloud, transparent volume pricing.
  - **Arize Phoenix (OSS) / Arize AX (SaaS)**: PostgreSQL for Phoenix OSS (single-node, dev-oriented), proprietary store for AX, OpenInference + OTel native, deeper agent-trace evaluation.
  - **LangSmith**: closed-source, deepest LangChain/LangGraph integration, per-trace pricing, Enterprise-tier self-hosting only.
  - **Helicone**: HTTP proxy (one-line gateway swap) rather than SDK instrumentation, ClickHouse + Kafka, built-in caching, $25/mo flat. Limitation: proxy-only means no agent-internal span detail — you see HTTP, not the agent decision tree.

**2.1.3 Patterns and primitives at depth.**

```
Trace hierarchy (canonical OTel GenAI form):

invoke_agent harness                         [INTERNAL, gen_ai.agent.name=harness]
├── chat claude-sonnet-4-5                  [CLIENT, op=chat]
│   ├── gen_ai.usage.input_tokens=4200
│   ├── gen_ai.usage.cache_read.input_tokens=4000  (subset of input_tokens)
│   ├── gen_ai.usage.cache_creation.input_tokens=200
│   ├── gen_ai.usage.output_tokens=180
│   ├── gen_ai.usage.reasoning.output_tokens=80
│   └── gen_ai.response.finish_reasons=["tool_use"]
├── execute_tool fetch_url                   [INTERNAL, op=execute_tool]
│   ├── gen_ai.tool.call.id="call_abc"
│   └── gen_ai.tool.type="function"
├── retrieval rag_corpus                     [CLIENT, op=retrieval]
│   ├── gen_ai.data_source.id="corpus_v3"
│   └── gen_ai.retrieval.documents (Opt-In)
├── invoke_agent code_subagent               [child agent invocation]
│   └── ... (full sub-tree)
└── chat claude-sonnet-4-5                   [final synthesis]
```

Span-attribute requirement matrix (chat span, abridged):

| Attribute | Stability | Requirement |
|---|---|---|
| `gen_ai.operation.name` | Development | Required |
| `gen_ai.provider.name` | Development | Required |
| `error.type` | **Stable** | Conditionally Required (on error) |
| `gen_ai.request.model` | Development | Conditionally Required (if available) |
| `gen_ai.conversation.id` | Development | Conditionally Required |
| `gen_ai.usage.input_tokens` | Development | Recommended |
| `gen_ai.usage.output_tokens` | Development | Recommended |
| `gen_ai.usage.reasoning.output_tokens` | Development | Recommended (when applicable) |
| `gen_ai.usage.cache_creation.input_tokens` | Development | Recommended |
| `gen_ai.usage.cache_read.input_tokens` | Development | Recommended |
| `gen_ai.response.time_to_first_chunk` | Development | Recommended (streaming) |
| `gen_ai.input.messages` | Development | **Opt-In** (PII) |
| `gen_ai.output.messages` | Development | Opt-In (PII) |
| `gen_ai.system_instructions` | Development | Opt-In (PII) |
| `gen_ai.tool.definitions` | Development | Opt-In |

Sampling-time attributes (per spec, "SHOULD be provided at span creation time"): `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model`, `server.address`, `server.port`. These five are the cardinality-safe dimensions for time-series metrics.

Cost computation: input_tokens already includes cache_read/cache_creation (per spec note [13]: "This value SHOULD include all types of input tokens, including cached tokens"). Don't sum the three or you double-count. Per Anthropic pricing, the right per-span cost formula is:

```
cost = (input_tokens - cache_read - cache_creation) * BASE_INPUT
     + cache_creation * BASE_INPUT * 1.25       # 5-min TTL
     + cache_read * BASE_INPUT * 0.10
     + output_tokens * BASE_OUTPUT
```

Online vs offline eval pattern: write eval scores as a separate child span with a custom attribute `eval.score` and `eval.judge_model`, OR as a span event on the inference span. Either approach lets you correlate score with the span's full attribute set. Don't put eval scores on time-series metrics unless bucketed by `gen_ai.request.model` and stratified — eval drift between offline and online manifests as a metric-level distribution shift only when the metric dimensions match.

**2.1.4 Tradeoffs at depth.**

| Axis | OTel-only | Vendor LLM-obs (Langfuse/Phoenix/LangSmith) | Helicone proxy |
|---|---|---|---|
| Cost | OSS collector + storage cost | $25–$2k+/mo | $25/mo flat, +caching savings |
| Latency overhead | <1ms/span | <1ms (SDK) | +1 hop (HTTP proxy) |
| Reliability impact | None | None (async export) | Proxy outage = LLM outage |
| Debuggability | Best with correlation (trace+log+metric) | Best for LLM-specific UI (token breakdowns, prompt diffs) | Worst — HTTP-only view |
| Security | You control the pipeline; redact at collector | Trust the vendor; check on-prem support | Trust the proxy with full prompts |
| Operator burden | Highest — you run it | Lowest if cloud, mid if self-hosted | Lowest |
| Vendor lock-in | None | Mid (data model coupling) — Phoenix/Langfuse are OSS escape hatches | Low |

**2.1.5 Failure modes in the field.**

- **Cardinality blowup from session/user IDs as metric dimensions**: documented across multiple Datadog/Honeycomb post-mortems, not LLM-specific but exacerbated by LLM apps that naturally want per-user cost attribution. Spec mitigation: sampling-time attributes are limited to the five low-cardinality ones above.
- **PII leakage via captured `gen_ai.input.messages`**: spec explicitly warns. Default behavior is Don't Record; production deployments that flipped this without redaction processors have leaked customer PII into Datadog/Sentry tenant data.
- **Tokenization changes silently break cost dashboards**: Anthropic's Claude Opus 4.7 ships a new tokenizer that produces "up to 35% more tokens for the same fixed text" [HIGH, per Anthropic pricing docs]. Cost-per-task metrics jumped on the upgrade; per-token unit cost is unchanged.
- **Caching breakage from non-deterministic JSON serialization**: Anthropic's prompt-caching docs flag that "Swift, Go" can randomize key order, breaking the cache prefix hash. Spans show `cache_creation_input_tokens > 0` and `cache_read_input_tokens = 0` repeatedly — observable but only if you're looking.
- **Sentry's own Seer-failure incident** (per `introducing-seer-agent/`): generic LLM call failures with no root cause in stack trace; manual diagnosis would have taken >30 min.

**2.1.6 Open questions and unresolved debates.**

- The OTel spec is silent on **agent-specific failure modes**: planner-loop divergence (agent that won't terminate), tool-call-validation failure (agent emitting structurally-wrong calls), sub-agent context-window-exhaustion. No standard `gen_ai.failure_mode` enum exists.
- **No standard span for human-in-the-loop pauses**. There is no `interrupt` operation in the OTel GenAI operation enum. Vendors will fork.
- **No standard for evaluation scores on spans**. Phoenix/Langfuse each define their own `score` model; OTel does not.
- **How to capture multi-modal token attribution** (vision tokens, audio tokens) — spec hints at `gen_ai.output.{type}.*` future attributes but they are unspecified.

**2.1.7 For-the-builder implications.** Adopt the OTel GenAI conventions now, but pin to a specific version (`gen_ai_latest_experimental` opt-in via env var) and accept that breaking changes will land. Default to **Don't Record content**, redact at the collector, and store full prompts in object storage with span attributes carrying only references. Run a self-hosted Langfuse alongside OTel-to-Tempo/Jaeger as the LLM-specific UI — Langfuse's ClickHouse model handles the volume that PostgreSQL-backed Phoenix OSS does not. Compute cost at trace-export time in the collector (deterministic, central), not per-span at SDK time (model-version drift). Never use `gen_ai.conversation.id` as a metric dimension.

---

### §2.2 Reliability Primitives

**2.2.1 Topic restatement.** Reliability primitives for an agent harness are the deterministic mechanisms wrapped around stochastic LLM and tool calls to produce predictable behavior under failure: timeouts, retries with backoff and jitter, circuit breakers, idempotency, bulkheads, rate-limit awareness, graceful degradation, and durable execution. The cluster's central question is whether composition lives in-process (resilience4j/Polly per call), at a gateway (LiteLLM, Bifrost, Helicone), or in a durable executor (Temporal, Inngest).

**2.2.2 Canonical sources, deeply engaged.**

- **Marc Brooker, "Exponential Backoff and Jitter"** (AWS Architecture Blog, Mar 2015; updated May 2023). Three jitter formulas + the "no jitter" baseline, all expressed as the new `sleep` value:

  ```
  No jitter:           sleep = min(cap, base * 2^attempt)
  Full jitter:         sleep = random_between(0, min(cap, base * 2^attempt))
  Equal jitter:        sleep = (min(cap, base * 2^attempt))/2
                              + random_between(0, min(cap, base * 2^attempt)/2)
  Decorrelated jitter: sleep = min(cap, random_between(base, prev_sleep * 3))
  ```

  Empirical comparison on the OCC simulator [HIGH, primary]: "the number of calls is approximately the same for 'Full' and 'Equal' jitter, and higher for 'Decorrelated'. Both cut down work substantially relative to both the no-jitter approaches." On time, decorrelated wins ("less time"); full jitter wins on call count. Equal jitter is strictly dominated by full jitter. No-jitter "is the clear loser. It not only takes more work, but also takes more time" — so much more time it's omitted from the comparison graph. Strengths: simulator code published (`aws-arch-backoff-simulator`); reproducible. Weaknesses: simulator models OCC contention, not LLM token-bucket rate limits, which have a different recovery dynamic (token replenishment vs lock release).

- **Stripe API idempotency docs** (`docs.stripe.com/api/idempotent_requests`, `docs.stripe.com/error-low-level`, `stripe.com/blog/idempotency`). Protocol shape:
  - Header: `Idempotency-Key: <up to 255 chars>`
  - TTL: "We can remove keys from the system automatically after they're at least 24 hours old" [HIGH, quoted].
  - Replay header on response: `Idempotent-Replayed: true`.
  - Conflict semantics: same key + different parameters → error. Same key + same parameters + completed → cached response replay. Same key + same parameters + in-flight → 409 Conflict.
  - Failure recording: only saved after execution begins. 4xx with key reuse → same 4xx replays (so generate fresh key when correcting input). 429 rate-limit happens BEFORE idempotency layer — same key may produce different result.
  - Generation strategies: V4 UUID OR derive from a user-attached object ID. Stripe Ruby SDK auto-generates and retries on its own.

- **resilience4j docs** (`resilience4j.readme.io/docs/circuitbreaker`). State machine: CLOSED, OPEN, HALF_OPEN, plus three special: METRICS_ONLY, DISABLED, FORCED_OPEN. Trip from CLOSED → OPEN at configurable failure-rate threshold OR slow-call-rate threshold (e.g., "more than 50% of recorded calls have failed" or "more than 50% took longer than 5 seconds"). Wait in OPEN per `waitDurationInOpenState`, then transition to HALF_OPEN, permit `permittedNumberOfCallsInHalfOpenState` trial calls; if failure rate ≥ threshold → back to OPEN; else → CLOSED. Sliding window: count-based or time-based, configured via `slidingWindowType`. Documented bugs (issues #903, #935, #2135): "stuck in HALF_OPEN" when buffered calls don't refresh — this is a real production failure mode, not theoretical.

- **Anthropic API rate-limit docs** (`platform.claude.com/docs/en/api/rate-limits`, `code.claude.com/docs/en/errors`). Three independent limits per model: RPM, ITPM, OTPM. 429 response includes `retry-after` header (seconds) and `anthropic-ratelimit-{requests,tokens}-{remaining,reset}` headers. **Claude Code retries 5xx, 429, 408, 409, 529 up to 10 times with exponential backoff** [HIGH, quoted from docs]. Knobs: `CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY` and others. 529 is `overloaded_error`, distinct from 429 — does NOT count against quota. Cached input tokens generally don't count against ITPM ("only uncached input tokens count towards your ITPM rate limits").

- **AWS Bedrock prompt caching** (`docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html`). Response fields: `CacheReadInputTokens`, `CacheWriteInputTokens`, `CacheDetails` (with TTL). Cache checkpoints are markers in the prompt body; minimum tokens vary by model (Claude 3.7 Sonnet: 1024 tokens minimum).

- **Google SRE Book, "Addressing Cascading Failures"** (`sre.google/sre-book/addressing-cascading-failures/`). Quoted: "A cascading failure is a failure that grows over time as a result of positive feedback." Most common cause: overload. Key mitigations: queue management, load shedding, graceful degradation, RPC deadlines, request cancellation propagation, retry budgets (server-side cap on total client retry rate).

- **Anthropic prompt caching pricing**: 5-min cache write = 1.25× base input; 1-hour cache write = 2× base input; cache read = 0.10× base input. Break-even = 2 cache reads (5-min) or 2 cache reads (1-hour @ 2× write).

**2.2.3 Patterns and primitives at depth.**

```
LLM-aware retry policy (composition):

on_response(resp):
  if resp.status == 200: return resp
  if resp.status in (429, 529, 503):
     if resp.headers.get("retry-after"):
         sleep(resp.headers["retry-after"])
     else:
         sleep(full_jitter(base=1s, cap=30s, attempt=n))
     return retry()
  if resp.status == 402:                     # Anthropic Max-plan rate-limit oddity
     treat_as_429()                            # NOT as billing-out
  if resp.status in (500, 502, 504):
     sleep(decorrelated_jitter(base=1s, cap=30s, prev=last_sleep))
     return retry()
  if resp.status in (400, 401, 403, 404, 422):
     return non_retryable(resp)
```

Idempotency key generation for LLM-driven tool calls (Stripe-derivative):

```
key = sha256(
    conversation_id || step_index || tool_name || canonical_json(args)
)[:32]
```

This gives: (a) collision-safe per Stripe's "sufficient entropy" requirement; (b) deterministic across retries by the same agent in the same step; (c) different across legitimate re-issues (different step_index). Failure mode if key collides on different args: server returns Stripe-style 4xx — agent must regenerate key, harness must surface this to the validator loop.

Circuit breaker per LLM endpoint (per-`{provider, model}` instance):

```
config:
  slidingWindowType: TIME_BASED
  slidingWindowSize: 60s
  minimumNumberOfCalls: 20
  failureRateThreshold: 50%
  slowCallRateThreshold: 50%
  slowCallDurationThreshold: 30s   # LLMs are slow; tune up vs HTTP defaults
  waitDurationInOpenState: 30s
  permittedNumberOfCallsInHalfOpenState: 3
  recordExceptions: [RateLimitError, OverloadedError, NetworkError]
  ignoreExceptions: [ValidationError]   # don't trip on bad-prompt; that's our bug
```

Fallback chain composition (provider-tier failover):

```
primary:   anthropic.claude-sonnet-4-5
secondary: anthropic.claude-haiku-4-5     (same vendor, cheaper)
tertiary:  openai.gpt-4o                   (different vendor)
last:      openrouter.mistral-large        (different infra path entirely)
```

Cascade-prevention rule: each tier has its own breaker; opening one cascades to next; tertiary failure should trigger graceful-degradation (return partial result with `degraded=true` metadata), NOT another retry storm.

Validator-failure retry protocol (Reflexion-style):

```
retry budget per step: {validator_failures: 2, escalations: 1}
1st validator fail → re-prompt with the validator error appended
2nd validator fail → re-prompt with a different system prompt OR escalate model tier
3rd validator fail → human-handoff (HITL) — never silent loop
```

**2.2.4 Tradeoffs at depth.**

| Composition site | Cost | Latency | Reliability | Debuggability | Security | Operator burden | Lock-in |
|---|---|---|---|---|---|---|---|
| **In-process (resilience4j/Polly)** | None | None | Per-process only — no cross-instance breaker state | Local logs only | Best — credentials never leave process | Per-language libraries | None |
| **Gateway (LiteLLM, Bifrost, Helicone)** | $0–$$ | +1 hop (~5–20ms) | Cross-instance breaker via shared state | Centralized log | Gateway sees plaintext prompts | Run+scale gateway | Mid |
| **Durable executor (Temporal/Inngest)** | $$$ | +event-log overhead | Highest — survives crashes | Best — full event history | Need to trust executor with payloads | Heavyweight | High |

**2.2.5 Failure modes in the field.**

- **Resilience4j HALF_OPEN stuck** (issues #903, #935, #2135): time-based sliding window with `slidingWindowSize: 1, minimumNumberOfCalls: 10` causes buffered-calls counter to freeze; circuit becomes a permanent black hole.
- **Anthropic 429 without `retry-after`**: docs imply it's always present, but the long-context error body shown in OpenClaw issue (`claude-sonnet-4-6[1m]`) returns a different shape. Don't assume header presence.
- **Anthropic 402 on Max plan rate-limit** (OpenClaw issue #30484): plan-bounded users get 402, not 429. Naive harnesses surface a "no credits" error to the user when the right action is backoff.
- **Cache breakage on JSON key reorder** (Anthropic prompt-caching docs): Swift/Go SDKs can produce non-stable orderings.
- **Cascading failure trigger**: queue saturation under retry storm — Google SRE explicitly calls out "retry amplification" as a death-spiral mechanism. Mitigation: server-side retry budget (cap aggregate retry rate as a fraction of forward traffic, e.g., 10%).

**2.2.6 Open questions and unresolved debates.**

- **Should LLM circuit breakers trip on validator failures?** No published guidance. Argument for: high validator-failure rate signals model regression. Against: validator failures are our schema, not the provider's fault; tripping makes the harness less reliable, not more.
- **Is the right idempotency key per-tool-call or per-conversation-turn?** Stripe model is per-API-call; LLM tool-calls might be retried as a unit (full turn) or individually.
- **No published Brooker-style empirical study for LLM rate limits**. The OCC simulator doesn't model token-bucket dynamics. Decorrelated jitter may not be optimal under TPM exhaustion.
- **Retry budget vs circuit breaker overlap**: SRE Book recommends both; operationally they can fight (budget says no, breaker says yes-trial). No clean resolution.

**2.2.7 For-the-builder implications.** Standardize on **full jitter** as the default (lowest implementation cost, lowest call count, only 5–10% slower than decorrelated on completion time per Brooker). Honor `Retry-After` always when present. Build **per-`{provider, model}` circuit breakers** (not per-process or per-host). Compose retry → breaker → fallback at a thin gateway (LiteLLM or hand-rolled Python) inside the harness; defer durable execution (Temporal/Inngest) until you have multi-day-running agents AND multi-machine scale — neither applies to a solo founder yet. Implement Stripe-style idempotency keys keyed on `sha256(conversation_id || step_index || tool || canonical_args)`. Map 402 from Anthropic Max plans to 429-equivalent backoff. Cap retry budget at ~10% of forward traffic. Hard-cap any in-flight LLM call at 5 minutes, validator-retry at 2 attempts, then human-handoff.

---

### §2.3 Security and Governance

**2.3.1 Topic restatement.** Security and governance for an agent harness covers: prompt injection (direct + indirect), tool poisoning, data exfiltration channels, sandbox model for code/computer-use, MCP authorization, audit-trail integrity, and the structural lethal-trifecta property of agentic systems. The cluster's central question: which architectural constraint do you accept (no MCP, no exfil paths, no private data, sandbox-everything) since detection-based mitigations top out at ~97%.

**2.3.2 Canonical sources, deeply engaged.**

- **Simon Willison, "The lethal trifecta for AI agents"** (`simonwillison.net/2025/Jun/16/the-lethal-trifecta/`, 16 Jun 2025). Three properties, quoted phrasing:
  1. **Access to your private data** — "one of the most common purposes of tools in the first place"
  2. **Exposure to untrusted content** — "any mechanism by which text (or images) controlled by a malicious attacker could become available to your LLM"
  3. **The ability to externally communicate** — "in a way that could be used to steal your data" (a.k.a. exfiltration)

  Argument: "If your agent combines these three features, an attacker can easily trick it into accessing your private data and sending it to that attacker." Filter-based mitigations are insufficient ("99% is a failing grade in application security"). The only reliable mitigation is to remove one leg architecturally. MCP magnifies the problem because it encourages arbitrary tool composition; an HTTP-fetching tool alone is sufficient exfil.

- **Simon Willison, "MCP has prompt injection security problems"** (Apr 2025) — argues MCP outsources the trifecta-avoidance decision to end users.

- **Simon Willison, "The Summer of Johann"** (15 Aug 2025). Surveys Rehberger's August 2025 series. Key claim: "almost three years after we first started talking about [prompt injection]" the same patterns are still exploitable across all major coding agents.

- **Johann Rehberger, "Month of AI Bugs"** (`embracethered.com`, August 2025). Specific incidents (one per day):
  - **Aug 1: ChatGPT memory exfil** — `url_safe` allow-list permitted `*.window.net`; any user can create `*.blob.core.windows.net` Azure storage with logs and harvest exfil.
  - **Aug 4: Cursor IDE — CVE-2025-54132** — Mermaid diagram embedded image URLs become invisible exfil channel.
  - **Aug 5: Amp Code RCE** — agent tricked into editing VS Code `settings.json`, enabling new Bash commands and MCP servers. RCE.
  - **Aug 6: Devin** — "$500 to test Devin AI for prompt injection" — found "no protection at all" against prompt injection executing arbitrary commands.
  - **Aug 7: Devin** — multiple exfil channels: Browser, Shell, Markdown images.
  - **Aug 12: GitHub Copilot — CVE-2025-53773** — prompt-inject `~/.vscode/settings.json` to flip `chat.tools.autoApprove: true`, enabling RCE via subsequent commands.
  - **Aug 13: Google Jules** — Markdown image exfil + `view_text_website` tool hijack.
  - **Aug 14: Google Jules — "Zombie Agent"** — full AI Kill Chain via "unrestricted outbound Internet connectivity."
  - **Aug 15: Google Jules** — invisible Unicode prompt injection through Gemini base.
  - Series also covered Claude Code, Anthropic MCPs, Amazon Q Developer, OpenHands, Windsurf, Manus.

  Rehberger's wrap-up (Aug 30): "Many vendors have chosen not to fix reported vulnerabilities" — a substantial number are "insecure by design".

- **OWASP LLM Top 10 v2.0 (2025)**:
  1. Prompt Injection
  2. Sensitive Information Disclosure
  3. Supply Chain
  4. Data and Model Poisoning
  5. Improper Output Handling
  6. Excessive Agency
  7. System Prompt Leakage (NEW)
  8. Vector and Embedding Weaknesses (NEW)
  9. Misinformation
  10. Unbounded Consumption

  v2.0 reflects shift to agentic deployments. Excessive Agency expanded to address multi-tool autonomous systems. Misinformation now subsumes Overreliance.

- **Model Context Protocol Authorization spec** (2025-06-18, `modelcontextprotocol.io/specification/draft/basic/authorization`). Mandatory:
  - HTTP transports SHOULD conform; STDIO SHOULD NOT (use environment).
  - MCP servers MUST act as OAuth 2.1 Resource Servers.
  - MCP clients MUST implement RFC 8707 Resource Indicators (preventing token-confusion across servers).
  - MCP servers MUST implement RFC 9728 Protected Resource Metadata.
  - **MCP server MUST NOT pass through the token it received from the MCP client** to upstream APIs (token-passthrough attack).
  - SHOULD support OAuth Client ID Metadata Documents (CIMD); MAY support Dynamic Client Registration (RFC 7591) for backwards compat.
  - PKCE required (RFC 7636).
  - Optional Step-up authorization for elevated scopes.

- **Invariant Labs, "MCP Security Notification: Tool Poisoning Attacks"** (Apr 2025). Coined "Tool Poisoning Attack (TPA)". Demonstrated Cursor IDE PoC: malicious tool description embeds hidden instructions to read `~/.cursor/mcp.json` and exfil. Subsequently Apr 7 follow-up with WhatsApp chat exfil; Apr 11 released `mcp-scan` detection tool. **Rug-pull variant**: clean description at install, malicious description after first load — defeats human review.

- **CyberArk, "Poison everywhere"** — extends TPA to tool *responses*, not just descriptions. Any output from a poisoned tool can carry injection.

- **Anthropic prompt-injection metrics** (`anthropic.com/news/prompt-injection-defenses`, `anthropic.com/transparency`). Sonnet 4.5 with detection systems on:
  - MCP scenarios: 94% prevention
  - Computer-use: 82.6% prevention
  - General bash tool use: 99.4% prevention

- **Anthropic Claude Code sandboxing** (`anthropic.com/engineering/claude-code-sandboxing`). Two boundaries: filesystem isolation + network isolation. Quoted: "effective sandboxing requires both filesystem and network isolation. Without network isolation, a compromised agent could exfiltrate sensitive files like SSH keys; without filesystem isolation, a compromised agent could easily escape the sandbox." On macOS uses Seatbelt; Linux/WSL uses bubblewrap + socat. Reduces permission prompts by 84% in internal usage.

- **Oasis Security, Claude.ai prompt-injection vulnerability** (disclosed and fixed). Vector: `claude.ai/new?q=...` URL parameter accepted invisible HTML tags. Exfil via attacker-controlled API key embedded in the hidden prompt + Claude code-execution sandbox's whitelist of `api.anthropic.com` (Files API). Sandbox's whitelist of own-domain became the exfil channel.

- **Anthropic Cowork / PromptArmor demonstration**: prompt-injected file in connected folder still bypasses sandbox via the same Anthropic Files API path on Claude Opus 4.5.

**2.3.3 Patterns and primitives at depth.**

```
Lethal-trifecta-aware tool-call gate (taint-tracking):

state.taint = false
on tool_result(r):
  if r.source == "untrusted":      # web fetch, email, doc, MCP-tool-output
      state.taint = true
on tool_call(c):
  if state.taint and c.has_capability("exfiltrate"):
      require_human_approval(reason="tainted-execution + exfil tool")
  elif state.taint and c.reads_private_data:
      require_human_approval(reason="tainted-execution + private-data read")
  else: proceed()
```

Exfiltration capabilities to flag: outbound HTTP, email/chat send, PR/issue create, image rendering with attacker-controllable URL, link rendering, DNS lookup, file write to shared/synced location.

```
MCP server trust posture (4 levels):

Level 0 (refuse remote): only stdio, only audited servers, no remote MCPs allowed
Level 1 (signed-pinned): remote allowed iff cryptographic signature pinned
                           AND tool description hash pinned (defeats rug-pull)
Level 2 (sandbox all): remote allowed but inside a network-isolated sandbox
                        with allow-list of upstream domains
Level 3 (allow with audit): permissive, but full ledger of every tool call
```

Audit-trail hash-chain ledger schema:

```
LedgerEntry {
  ts: int64,
  actor: string,                    # agent_id or human_id
  action: string,                   # "tool_call", "approval", "interrupt"
  inputs_hash: bytes32,             # sha256 of canonical args
  outputs_hash: bytes32,            # sha256 of result
  parent_hash: bytes32,             # sha256 of previous entry
  signature: bytes,                 # optional Ed25519 over (above fields)
}
verify(chain): for each i, sha256(chain[i-1]) == chain[i].parent_hash
```

Simple-chain is sufficient for solo-founder scale; Merkle tree only matters for selective disclosure.

**2.3.4 Tradeoffs at depth.**

| Defense | Cost | Reliability | Debuggability | Security gain | Operator burden |
|---|---|---|---|---|---|
| **Capability removal (cut a trifecta leg)** | High UX cost | None | None | Highest — structural | Low after design |
| **Sandbox (filesystem + network)** | Mid (OS-level) | None | Worse — sandbox failures look like bugs | High | Mid |
| **Output filtering / LLM-as-judge** | Token cost | Adds latency | Worse | Medium (~97%) | Low |
| **Signed-pinned MCP** | Onboarding cost | None | Better — diff-based rug-pull detection | High | Mid |
| **Audit ledger** | Storage cost | None | Best | Detection only, not prevention | Mid |
| **Human-in-the-loop on tainted ops** | UX cost | Adds latency | Best | High but limited by fatigue | Low |

**2.3.5 Failure modes in the field.**

- **CVE-2025-53773** (GitHub Copilot RCE) — flag-flip attack via config-file edit.
- **CVE-2025-54132** (Cursor Mermaid exfil).
- **Claude.ai URL-param injection** (Oasis Security disclosure, fixed).
- **Anthropic Files API as exfil channel** (PromptArmor on Cowork).
- **Microsoft 365 Copilot audit log gap** (Rehberger): Copilot would access files without audit log entry, on prompt-instruction; reported to MSRC.
- **GitHub MCP server private-repo exfil via public-issue prompt injection** (cited in Oso writeup).
- **Writer.com URL-controlled prompt injection exfil via invisible image URLs**.
- **GitLab Duo Chatbot**: public project with rogue instructions causes private-repo info disclosure.
- **ChatGPT Operator**: untrusted "string-combination" tool covertly exfils.

**2.3.6 Open questions and unresolved debates.**

- **Is multi-agent isolation a real defense?** Oso/Willison argue no — agents share memory/context, "digital gossiping" reproduces the trifecta.
- **CaMeL (Google DeepMind) capability-based mitigation**: promising but no production deployment.
- **MCP's missing pieces**: no signed tool descriptions, no chain-of-trust between install-time and runtime, no standard sandbox.
- **Can prompt-injection robustness scale linearly with model size?** Anthropic's Sonnet 4.5 numbers improved over Sonnet 4 only marginally; suggests no.
- **"Insecure by design"**: Rehberger's wrap-up: many vendors won't fix because the fix breaks core functionality. Open question whether market pressure forces a regression.

**2.3.7 For-the-builder implications.** Adopt the lethal-trifecta as a hard architectural constraint for the OpenClaw/n8n stack: classify every tool by `(reads_private, sees_untrusted, can_exfiltrate)`. Refuse any single execution path that reaches all three. **Default MCP posture: Level 0 (refuse remote) for production; Level 1 (signed-pinned) for staging; never Level 3.** Sandbox all code execution (Claude Code's native sandbox on macOS/Linux; Docker for n8n custom nodes). Require human approval on any tainted execution attempting exfil capabilities. Implement a hash-chain audit ledger with `parent_hash` per ledger entry — this is ~50 lines of Python and is cheap insurance for incident-response provability. Treat 99.4% prompt-injection robustness as insufficient for any tool that touches private data without human gate. Run `mcp-scan` on every MCP server before installation. Never enable `bypassPermissions` mode in Claude Code outside ephemeral container CI.

---

### §2.4 Human-in-the-Loop Design

**2.4.1 Topic restatement.** HITL design for an agent harness covers: when to interrupt, what context to package for the human, how to resume durably, how to compose with sub-agents and parallel execution, how to avoid approval fatigue, and how to model tiered autonomy. The cluster's central question: synchronous-blocking (LangGraph `interrupt()`) vs durable-async (Temporal signals, HumanLayer webhooks) vs both-by-tier.

**2.4.2 Canonical sources, deeply engaged.**

- **HumanLayer 12-Factor Agents** (`github.com/humanlayer/12-factor-agents`, Dex Horthy). Full surfaced list:
  1. **Natural Language to Tool Calls**
  2. **Own your prompts**
  3. **Own your context window**
  4. **Tools are just structured outputs**
  5. **Unify execution state and business state**
  6. **Launch/Pause/Resume with simple APIs**
  7. **Contact humans with tool calls**
  8. **Own your control flow**
  9. **Compact Errors into Context Window**
  10. **Small, Focused Agents**
  11. **Trigger from anywhere, meet users where they are**
  12. **Make your agent a stateless reducer**

  Plus appendix Factor 13 (Pre-fetch context).

  Where HITL appears: Factor 7 ("Contact humans with tool calls") makes HITL a tool call against a human — same shape as any other tool. Factor 6 (Launch/Pause/Resume) makes the runtime contract for HITL identical to durable-execution checkpointing. Factor 8 ("Own your control flow") rejects framework-managed HITL state in favor of explicit application code. Factor 12 (stateless reducer) means the agent function is `(state, event) → (new_state, action)` — HITL is just a particular event type.

- **HumanLayer SDK** (`humanlayer.dev/docs`). Primary primitives: `@hl.require_approval()` decorator; `hl.human_as_tool()`; `ContactChannel` with Slack/Email/React-embed; composite channels via `all_of` and `any_of`; webhook-based async. API shape: POST `/humanlayer/v1/function_calls` with `{run_id, call_id, spec: {fn, kwargs, channel}}`. Webhooks fire on approval.

- **LangGraph `interrupt()` API** (`docs.langchain.com/oss/python/langgraph/interrupts`, `reference.langchain.com/python/langgraph/types/interrupt`). API surface:

  ```python
  from langgraph.types import interrupt, Command
  
  def approval_node(state):
      response = interrupt({"question": "Approve?", "tool_calls": ...})
      # response is the Command(resume=...) value when graph is re-invoked
      return {"approved": response}
  
  # Resume:
  graph.stream(Command(resume="yes"), config={"configurable": {"thread_id": "..."}})
  ```

  Critical semantic [HIGH, quoted]: "When execution resumes (after you provide the requested input), the runtime restarts the entire node from the beginning—it does not resume from the exact line where interrupt was called." Therefore: side effects before `interrupt()` MUST be idempotent. Rules:
  - Do not wrap `interrupt()` in try/except (catches the `GraphInterrupt`).
  - Do not reorder interrupt calls within a node (resume values matched by ordinal position).
  - Do not return complex non-JSON-serializable values.
  - Checkpointer required at compile time (e.g., `MemorySaver`, `SqliteSaver`, `PostgresSaver`).
  - Thread ID required in config to identify which conversation's state to restore.

  Composition with sub-agents: each subagent is its own graph; an interrupt in a subagent must be resumed via the subagent's thread. Parallel execution: each parallel branch can independently interrupt; multiple `__interrupt__` events can surface at once.

- **Anthropic, "Building Effective Agents"** (Schluntz & Zhang, Dec 2024, `anthropic.com/engineering/building-effective-agents`). Distinction: workflows (predetermined orchestration) vs agents (LLM-directed). Five workflow patterns: prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer. HITL appears as a checkpoint pattern: agents "pause for human feedback at checkpoints or when encountering blockers." Argues against framework-heavy approaches; recommends starting with direct API calls.

- **Anthropic, "Effective harnesses for long-running agents"** (`anthropic.com/engineering/effective-harnesses-for-long-running-agents`). Two-agent pattern: initializer agent (sets up `feature_list.json`, git, `init.sh`) + coding agent (one feature per session, commits progress, tests E2E). Session ritual: `pwd`, read progress doc, read feature list, run tests, then implement. Key insight: long-running agent reliability comes from harness design, not bigger models. JSON feature list "harder for model to corrupt than Markdown."

- **Temporal HITL docs** (`docs.temporal.io/ai-cookbook/human-in-the-loop-python`, `learn.temporal.io/tutorials/ai/`). Pattern: workflow uses `@workflow.signal` handler to receive approval decisions; `workflow.wait_condition(...)` with timeout; `@workflow.query` for read-only state inspection. Quoted: "If your application is waiting for 5 days and crashes on day 3, you lose all progress... Temporal's durable timers survive crashes and restarts." Replay determinism requires signal handler to be idempotent.

- **Inngest durable HITL** (`inngest.com`, mentioned in 12-Factor Agents as a reference DAG orchestrator). Similar model to Temporal: durable steps + waitForEvent.

- **Claude Code permission model** (`code.claude.com/docs/en/permissions`). Three rule types in `.claude/settings.json`:
  ```json
  {"permissions": {
    "allow": ["Bash(npm run *)"],
    "deny":  ["Bash(rm *)", "Read(./.env)"],
    "ask":   ["Bash(git push *)"]
  }}
  ```
  Evaluation order: **deny → ask → allow**, first match wins. Five permission modes: `default`, `acceptEdits`, `plan`, `dontAsk` (lockdown), `bypassPermissions` (YOLO). Cycle through three main modes via Shift+Tab. PreToolUse hooks can override at runtime. Documented limitation: deny rules historically failed for `Read`/`Write` against `Bash(cat ...)` workaround (issue #6631).

**2.4.3 Patterns and primitives at depth.**

```
Tiered autonomy via tool annotation + policy table:

ToolDef = {
  name: str,
  tier: "auto" | "ask" | "deny",
  capabilities: {reads_private: bool, sees_untrusted: bool, can_exfiltrate: bool}
}

policy(tool, state, history):
  if tool.tier == "deny": return REJECT
  if tool.tier == "auto" and not (state.tainted and tool.can_exfiltrate):
    return APPROVE
  if state.consecutive_approvals_today > 50 and tool.tier == "ask":
    return BATCH_APPROVE_QUEUE        # approval-fatigue mitigation
  return ASK_HUMAN(context=package_handoff(tool, state, history))
```

Handoff context package (what the human sees):

```
HandoffContext {
  proposed_action: {tool, args, expected_effect},
  agent_confidence: float,
  failed_attempts: [{tool, args, error}],
  alternatives_considered: [...],
  state_summary: {goal, progress, blockers},
  audit_trail_link: url,
  retry_history: [{ts, attempt, outcome}],
}
```

LangGraph durable HITL with sub-agent composition:

```
Parent graph (thread_id=parent-123):
  plan_node ─→ subagent_invocation ─→ synthesis
                       │
                       ├─→ Subagent graph (thread_id=child-456):
                              tool_call_node
                              approval_node     ← interrupt()
                              execution_node
```

Resume requires invoking the *correct* graph with the right thread_id. Parent graph remains paused waiting on subagent invocation result; subagent invocation node SHOULD itself be idempotent so subagent restart-from-node-start doesn't replay external side effects.

Temporal durable HITL:

```python
@workflow.defn
class ApprovalFlow:
    def __init__(self):
        self.decision = None
    
    @workflow.signal
    async def set_decision(self, decision):
        self.decision = decision
    
    @workflow.run
    async def run(self, request):
        proposed = await workflow.execute_activity(propose_action, request)
        try:
            await workflow.wait_condition(
                lambda: self.decision is not None,
                timeout=timedelta(days=5)
            )
        except TimeoutError:
            return await workflow.execute_activity(timeout_handler, proposed)
        return await workflow.execute_activity(execute_decision, self.decision)
```

Approval-fatigue mitigation patterns (with documented effectiveness):

| Pattern | Mechanism | Effectiveness | Failure mode |
|---|---|---|---|
| **Batched approvals** | Queue N similar requests, single approve-all | High when actions are homogeneous | Over-approves heterogeneous batch |
| **Confidence-weighted** | Auto-approve when agent confidence > threshold | Mid — confidence is poorly calibrated | Approves confident-but-wrong actions |
| **Trust ratchet** | Tool starts in `ask`, promotes to `auto` after N successful approvals | Mid — drift over time | One bad action persists across all future calls |
| **Dry-run-then-approve** | Show predicted result before execution | High | Doubles latency; relies on accurate prediction |

**2.4.4 Tradeoffs at depth.**

| Model | Cost | Latency | Reliability | Debuggability | Security | Operator burden | Vendor lock |
|---|---|---|---|---|---|---|---|
| **Sync-blocking (LangGraph)** | Lowest | Best for fast humans | Process-bounded — restart loses state without checkpointer | Best (single trace) | Tied to harness security | Lowest | Mid (LangGraph) |
| **Durable-async (Temporal)** | Highest infra | High latency baseline | Survives crashes, multi-day waits | Best — full event log | Trust executor with payloads | Highest | High |
| **HumanLayer webhook** | Mid | Mid (async webhook) | Survives if webhook handler does | Mid (HumanLayer console) | Trust HumanLayer with prompts | Low | Mid |
| **Both by tier** | Mid | Tier-dependent | Best — durable for high-stakes, sync for fast | Best | Tier-dependent | Mid | Mid |

**2.4.5 Failure modes in the field.**

- **LangGraph `interrupt()` re-entry bug pattern**: developer writes side-effecting code before `interrupt()`, side effect fires twice on resume. Documented in LangGraph rules section.
- **Approval fatigue**: Claude Code without configured permissions becomes a prompt-storm. Empirically users hit `bypassPermissions` mode and lose all gates.
- **Stale interrupt threads**: thread_id checkpointed indefinitely; if no resume comes, state grows unbounded. Need TTL-based abandonment job.
- **Webhook lost-update**: HumanLayer webhook fires, handler crashes, resume signal lost. Mitigation: webhook handler must be idempotent; always re-fetch state from HumanLayer API on suspected loss.
- **Sub-agent interrupt stranding**: parent graph times out waiting on subagent that's itself stuck in interrupt; cascade requires careful timeout composition.
- **Temporal signal-replay determinism**: if signal handler is non-deterministic (e.g., reads wall-clock), workflow replay diverges and corrupts state.

**2.4.6 Open questions and unresolved debates.**

- **No empirical study comparing sync vs durable HITL on completion rate**. Anecdotal: Temporal advocates claim higher completion; LangGraph advocates claim faster iteration.
- **What context length is right for handoff?** Too little = human can't decide; too much = decision fatigue. No published guidance.
- **Trust-ratchet revocation**: how to demote a tool from `auto` back to `ask` after one bad action? No standard pattern.
- **Multi-approver semantics under parallel execution**: HumanLayer has `all_of`/`any_of` but composition with parallel sub-agents is undocumented.

**2.4.7 For-the-builder implications.** Adopt **HumanLayer's Factor-7 framing** (HITL is a tool call) — it eliminates a class of framework-binding decisions. Use **LangGraph `interrupt()` for sync-blocking pauses inside a single agent run** (sub-1-minute wait), backed by SQLite checkpointer for the local-first stack. Use **HumanLayer + webhook for any HITL spanning >1 minute** (Slack/Email is the right channel; n8n is the right webhook router). Defer Temporal until you have multi-day workflows or multi-machine agents; not yet justified for solo founder. Implement **tiered autonomy** with explicit `tier` annotation on every tool, plus a runtime policy table that consults tainted-state — this is the same model as Claude Code's `deny → ask → allow`. Adopt **dry-run-then-approve** for high-blast-radius tools (file delete, git push, API write). Hard-cap human-handoff budget at 1 per agent step; on second handoff, fail the step rather than spam the operator. Make every interrupt-resume path idempotent: any operation before `interrupt()` MUST be re-executable safely. Package handoff context with proposed action, confidence, failed attempts, alternatives — this is the most-undervalued lever in the cluster.

---

## §3 Cross-Topic Synthesis

**3.1 Architectural couplings.**

- **(a) Observability span schema → Reliability decision input.** A retry policy needs per-step latency, error type, and token attribution. The OTel GenAI `error.type` (Stable) is the single attribute the retry layer should branch on. Cache token attributes (`gen_ai.usage.cache_read.input_tokens`) drive cost-budget breach decisions. Without per-span error.type, retry escalation has no signal. **Decision: retry/breaker logic must read OTel span attributes synchronously (via in-process tracer state) rather than awaiting export.**

- **(b) Idempotency keys are simultaneously a reliability and security primitive.** Stripe-style keys prevent retry-induced duplicate writes (reliability) AND replay-attack duplicate writes (security). The same `sha256(conversation_id || step || tool || args)` key handles both. The collision-resistance property (V4 UUID or 32-byte hash) is what makes the security claim tenable.

- **(c) Ask-First boundary tier (HITL) shares enforcement model with write-path trust boundaries (security).** Both are gates: HITL gate fires on tool tier; security gate fires on lethal-trifecta-positive execution path. Implementation convergence: a single `policy()` function evaluating both `tier` and `taint` state, returning `ALLOW | ASK | DENY`. Claude Code's `deny → ask → allow` order is the right composition.

- **(d) Approval queues require durable state that observability traces and reliability guarantees survive restart.** A pending approval spans process restarts — checkpoint storage (SQLite for solo, Postgres for team) is the substrate. The trace context must propagate across the durable boundary so the resumed execution lands in the same logical trace. OTel trace-context-in-state pattern: serialize `traceparent` header into the checkpoint state; reconstitute on resume.

**3.2 Shared primitives across the cluster.**

| Primitive | Observability | Reliability | Security | HITL |
|---|---|---|---|---|
| **Span / Step record** | OTel span | Retry attempt | Audit ledger entry | Approval request |
| **Idempotency key** | Span attr | Retry-safe key | Replay-prevention | Approval-call dedupe |
| **Hash chain** | (n/a) | (n/a) | Audit integrity | Approval provenance |
| **Trust tier** | (n/a) | Breaker per-tier | Capability gate | Approval gate |
| **Durable checkpoint** | Trace state | Workflow resume | Audit persistence | Interrupt resume |

**3.3 Source-level convergence and divergence.**

- **Convergence**: HumanLayer 12-Factor Factor 5 ("Unify execution state and business state") and Temporal "durable execution" agree that the agent's logical state and the runtime's checkpoint state should be the same object. LangGraph's checkpointer model implements exactly this. Anthropic's "Effective Harnesses for Long-running Agents" reinforces with the `feature_list.json` + `claude-progress.txt` artifact pattern — same idea at a different layer (file-based vs in-memory).

- **Convergence**: Brooker (jitter), Stripe (idempotency), Claude Code (rate-limit-aware retry budget), and Google SRE (cascading-failure prevention) all converge on the same composition: timeout → idempotency → retry-with-jitter → circuit-breaker → fallback → degradation. The vocabulary differs; the structure is identical.

- **Divergence**: Anthropic Building-Effective-Agents argues against frameworks ("start with direct API calls"). HumanLayer 12-Factor agrees explicitly ("frameworks are evil" link). LangGraph and Temporal are framework solutions. The cluster's resolution: lightweight primitives (OTel, jitter math, idempotency keys, `interrupt()`) can be adopted without framework lock-in; heavy frameworks (LangChain orchestration, full Temporal cluster) should be deferred until justified.

- **Divergence**: Willison's lethal trifecta says "filtering is insufficient — cut a leg." Anthropic's quantified prompt-injection numbers (94% / 82.6% / 99.4%) implicitly argue filtering is approaching sufficient. The honest position: filtering is necessary but not sufficient; structural cuts are necessary but UX-costly. Both must be deployed in serious systems.

**3.4 Decision points the cluster collectively defines.**

| Decision point | Solo-founder default (recommended) | Trigger to revisit |
|---|---|---|
| **Observability backend** | Self-hosted Langfuse + OTel-to-local-Tempo | Multi-tenant or compliance pressure → add Datadog |
| **Trace-content policy** | Hashed/redacted by default; full content opt-in per dev session | Privacy regulation → never full content |
| **Reliability composition** | In-process (Python `httpx` + `tenacity` + custom breaker) | Multi-machine or >24hr workflows → Temporal |
| **Sandbox model** | Mixed: Claude Code native sandbox for code; Docker for n8n custom nodes; vendor-managed for Bedrock | Multi-tenant code execution → micro-VM (Firecracker, e2b) |
| **MCP trust posture** | Refuse remote MCPs in production; allow stdio audited servers; mcp-scan all installs | Customer pressure for remote MCP → Level 1 (signed-pinned) |
| **HITL model** | LangGraph `interrupt()` for sync (<1min); HumanLayer webhook for async (>1min) | Multi-day workflows → Temporal signals |
| **Approval-fatigue strategy** | Dry-run-then-approve for write-tier; trust-ratchet for read-tier; never confidence-weighted alone | Operator complaints → batched-approvals layer |

---

## §4 Open Questions and Recommended Next Probes

1. **OTel GenAI stability roadmap**: when does `gen_ai.*` move from Development to Stable? Probe the OTel SIG GitHub for the next milestone — version selection page is the canonical source.

2. **LLM-specific Brooker analog**: no published empirical comparison of jitter strategies under token-bucket rate-limit dynamics. Probe: simulate full/decorrelated jitter against Anthropic's actual rate-limit reset semantics (`anthropic-ratelimit-tokens-reset` timestamp).

3. **MCP signed tool descriptions**: open SEPs (Spec Enhancement Proposals) for tool-description signing. Probe: `modelcontextprotocol/modelcontextprotocol` GitHub for SEP-991 (CIMD) and successors targeting tool-poisoning rug-pull.

4. **Anthropic prompt-cache breakage telemetry**: no public numbers on cache-miss rate in production agents. Probe via Langfuse aggregations on own deployment once instrumented.

5. **Empirical HITL completion-rate data**: no published study. Probe blog content from Inngest, Temporal, HumanLayer for case studies with completion-rate baselines.

6. **OpenClaw harness security model**: documentation describes `supports`/`runAttempt` but no published threat model. Probe: openclaw.ai docs section on plugin security; check for sandbox boundaries between harnesses.

7. **CaMeL and capability-based mitigation production deployments**: Google DeepMind's paper is promising but no real-world references found. Probe arXiv for follow-on implementations.

8. **Claude Code permission-system audit log format**: documented hook system can log every tool invocation; no canonical audit-ledger schema. Probe `code.claude.com` for hook examples and consider standardizing on the hash-chain ledger schema in §2.3.3.

9. **Resilience4j HALF_OPEN-stuck root cause**: GitHub issues #903/#935/#2135 are open or marked "implemented" but the production failure persists in some configurations. Probe latest resilience4j releases for fixes.

10. **n8n + OTel GenAI integration**: n8n does not natively emit OTel GenAI spans. Probe n8n community for OTel custom-instrumentation patterns or adopt OpenInference's n8n bridge if it exists.

---

## §5 Source Bibliography

Marker key: [substrate] = present in Session 1 substrate; [deepened] = in substrate but engaged at depth this session; [new] = first surfaced this session.

**Observability**
1. OpenTelemetry, "Semantic conventions for generative client AI spans" (semconv 1.41.0, status: Development). `opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/` — [deepened]
2. OpenTelemetry, "Semantic Conventions for GenAI agent and framework spans". `opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/` — [deepened]
3. OpenTelemetry, "Semantic conventions for generative AI metrics". `opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-metrics/` — [deepened]
4. OpenTelemetry, GenAI attributes registry. `opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/` — [new]
5. OpenTelemetry semconv repo, gen-ai-spans.md. `github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-spans.md` — [deepened]
6. Datadog, "LLM Observability natively supports OpenTelemetry GenAI Semantic Conventions". `datadoghq.com/blog/llm-otel-semantic-convention/` — [deepened]
7. Langfuse, "Arize AX Alternative? Langfuse vs. Arize AI and Arize Phoenix". `langfuse.com/faq/all/best-phoenix-arize-alternatives` — [new]
8. Helicone, "The Complete Guide to LLM Observability Platforms". `helicone.ai/blog/the-complete-guide-to-LLM-observability-platforms` — [new]
9. Microsoft Learn, "Enabling observability for Agents". `learn.microsoft.com/en-us/agent-framework/tutorials/agents/enable-observability` — [new]
10. Visual Studio Code docs, "Monitor agent usage with OpenTelemetry" (GitHub Copilot Chat). `code.visualstudio.com/docs/copilot/guides/monitoring-agents` — [new]
11. Indragie Karunaratne / Sentry, "Seer by Sentry: debug with AI at every stage of development" (Jan 2026). `blog.sentry.io/seer-debug-with-ai-at-every-stage-of-development/` — [deepened]
12. Indragie Karunaratne / Sentry, "Introducing Seer Agent". `blog.sentry.io/introducing-seer-agent/` — [new]

**Reliability**
13. Marc Brooker, "Exponential Backoff and Jitter," AWS Architecture Blog, Mar 2015 (updated May 2023). `aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/` — [deepened]
14. AWS Builders' Library, "Timeouts, retries and backoff with jitter". `aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/` — [deepened]
15. Stripe, "Idempotent requests" (API reference). `docs.stripe.com/api/idempotent_requests` — [deepened]
16. Stripe, "Advanced error handling". `docs.stripe.com/error-low-level` — [new]
17. Stripe blog, "Designing robust and predictable APIs with idempotency". `stripe.com/blog/idempotency` — [deepened]
18. resilience4j, "CircuitBreaker" docs. `resilience4j.readme.io/docs/circuitbreaker` — [deepened]
19. Anthropic, "Rate limits" (Claude API docs). `platform.claude.com/docs/en/api/rate-limits` — [deepened]
20. Anthropic, "Error reference" (Claude Code docs). `code.claude.com/docs/en/errors` — [new]
21. Anthropic, "Prompt caching" (Claude API docs). `platform.claude.com/docs/en/build-with-claude/prompt-caching` — [deepened]
22. Anthropic, "Pricing" (Claude API docs). `platform.claude.com/docs/en/about-claude/pricing` — [new]
23. AWS, "Prompt caching for faster model inference - Amazon Bedrock". `docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html` — [deepened]
24. Google SRE Book, "Addressing Cascading Failures". `sre.google/sre-book/addressing-cascading-failures/` — [deepened]
25. Google SRE Book, "Handling Overload". `sre.google/sre-book/handling-overload/` — [new]

**Security**
26. Simon Willison, "The lethal trifecta for AI agents: private data, untrusted content, and external communication" (16 Jun 2025). `simonwillison.net/2025/Jun/16/the-lethal-trifecta/` — [deepened]
27. Simon Willison, "The Summer of Johann: prompt injections as far as the eye can see" (15 Aug 2025). `simonwillison.net/2025/Aug/15/the-summer-of-johann/` — [deepened]
28. Johann Rehberger, "The Month of AI Bugs 2025" (announcement). `embracethered.com/blog/posts/2025/announcement-the-month-of-ai-bugs/` — [deepened]
29. Johann Rehberger, "GitHub Copilot: Remote Code Execution via Prompt Injection (CVE-2025-53773)". `embracethered.com/blog/posts/2025/github-copilot-remote-code-execution-via-prompt-injection/` — [new, via secondary citation]
30. Johann Rehberger, "Wrap Up: The Month of AI Bugs" (Aug 30, 2025). `embracethered.com/blog/posts/2025/wrapping-up-month-of-ai-bugs/` — [new, via secondary]
31. OWASP GenAI Security Project, "OWASP Top 10 for Large Language Model Applications 2025" (v2.0). `owasp.org/www-project-top-10-for-large-language-model-applications/` — [deepened]
32. Model Context Protocol, "Authorization" specification. `modelcontextprotocol.io/specification/draft/basic/authorization` — [deepened]
33. Auth0 blog, "Model Context Protocol (MCP) Spec Updates from June 2025". `auth0.com/blog/mcp-specs-update-all-about-auth/` — [new]
34. Invariant Labs, "MCP Security Notification: Tool Poisoning Attacks". `invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks` — [deepened]
35. Invariant Labs, `mcp-injection-experiments` repository. `github.com/invariantlabs-ai/mcp-injection-experiments` — [new]
36. CyberArk, "Poison everywhere: No output from your MCP server is safe". `cyberark.com/resources/threat-research-blog/poison-everywhere-no-output-from-your-mcp-server-is-safe` — [new]
37. Elastic Security Labs, "MCP Tools: Attack Vectors and Defense Recommendations for Autonomous Agents". `elastic.co/security-labs/mcp-tools-attack-defense-recommendations` — [new]
38. MCP Manager, "MCP Tool Poisoning - How It Works & How To Fight It". `mcpmanager.ai/blog/tool-poisoning/` — [new]
39. Anthropic, "Mitigating the risk of prompt injections in browser use". `anthropic.com/news/prompt-injection-defenses` — [new]
40. Anthropic, "Transparency Hub" (Sonnet 4.5 prompt-injection metrics). `anthropic.com/transparency` — [new]
41. Anthropic, "Claude Code Sandboxing". `anthropic.com/engineering/claude-code-sandboxing` — [new]
42. Oasis Security, "Claude.ai Prompt Injection Vulnerability". `oasis.security/blog/claude-ai-prompt-injection-data-exfiltration-vulnerability` — [new]

**HITL**
43. HumanLayer, "12-Factor Agents" repository. `github.com/humanlayer/12-factor-agents` — [deepened]
44. HumanLayer, "12 Factor Agents" blog post. `humanlayer.dev/blog/12-factor-agents` — [deepened]
45. HumanLayer docs, "Introduction" (Contact Channels). `humanlayer.dev/docs/channels/introduction` — [new]
46. HumanLayer docs, "Composite Channels". `humanlayer.dev/docs/channels/composite-channels` — [new]
47. HumanLayer docs, "Email" channel. `humanlayer.dev/docs/channels/email` — [new]
48. HumanLayer API, "Function Calls". `humanlayer.dev/docs/api-reference/function-calls` — [new]
49. HumanLayer docs, "Response Webhooks". `humanlayer.dev/docs/core/response-webhooks` — [new]
50. HumanLayer Agent Control Plane (ACP). `github.com/humanlayer/agentcontrolplane` — [new]
51. LangChain docs, "Interrupts" (LangGraph). `docs.langchain.com/oss/python/langgraph/interrupts` — [deepened]
52. LangGraph reference, `interrupt` function (Python). `reference.langchain.com/python/langgraph/types/interrupt` — [deepened]
53. LangGraph.js API reference, `interrupt`. `langchain-ai.github.io/langgraphjs/reference/functions/langgraph.interrupt.html` — [new]
54. Anthropic, "Building Effective Agents" (Schluntz & Zhang, Dec 2024). `anthropic.com/engineering/building-effective-agents` — [deepened]
55. Anthropic, "Effective harnesses for long-running agents". `anthropic.com/engineering/effective-harnesses-for-long-running-agents` — [deepened]
56. Anthropic Cookbook, agent patterns. `github.com/anthropics/anthropic-cookbook/tree/main/patterns/agents` — [new]
57. Temporal docs, "Human-in-the-Loop AI Agent". `docs.temporal.io/ai-cookbook/human-in-the-loop-python` — [deepened]
58. Temporal Learn, "Adding Durable Human-in-the-Loop to Our Research Application". `learn.temporal.io/tutorials/ai/building-durable-ai-applications/human-in-the-loop/` — [new]
59. Temporal blog, "From AI hype to durable reality". `temporal.io/blog/from-ai-hype-to-durable-reality-why-agentic-flows-need-distributed-systems` — [new]
60. Anthropic, "Configure permissions" (Claude Code). `code.claude.com/docs/en/permissions` — [deepened]
61. Anthropic, "Configure permissions" (Claude Agent SDK). `platform.claude.com/docs/en/agent-sdk/permissions` — [new]
62. GitHub issue, "Permission Deny Configuration Not Enforced for Read/Write Tools" (#6631). `github.com/anthropics/claude-code/issues/6631` — [new]

**OpenClaw / harness specifics (for stack alignment)**
63. OpenClaw docs, "Agent harness plugins". `docs.openclaw.ai/plugins/sdk-agent-harness` — [new]
64. OpenClaw DeepWiki, "Agent Harness Plugins". `deepwiki.com/openclaw/docs/5.4-agent-harness-plugins` — [new]
65. NVIDIA Blog, "Nemotron Labs: What OpenClaw Agents Mean for Every Organization" — [new, contextual only]

**Caveats on bibliography**: Sources tagged [new] in this session were retrieved live and are accurate as of May 2026 retrieval. Several sources reference dates (e.g., "AI Security in 2026") that postdate the canonical user-facing date — these reflect crawl-time content of the sites and were used only when the underlying primary technical claim could be cross-referenced with a primary source (Anthropic, OWASP, OTel, LangChain). CVEs cited (CVE-2025-53773, CVE-2025-54132) are surfaced via Rehberger's blog and Simon Willison's link-blog summary; the primary disclosure URLs at embracethered.com were referenced via secondary sources rather than fetched directly this session, so the CVE-to-vendor-fix-status linkage is [MODERATE] not [HIGH] confidence.

**Known gaps / not engaged this session**:
- LangSmith docs deeply (only via comparison surveys)
- Polly docs (substrate-only)
- Hystrix wiki (substrate-only)
- arXiv MCP threat-modeling papers — surfaced one (`MCPTox`) but did not deep-dive
- Anthropic Trust page (surfaced via secondary)
- Specific OpenAI rate-limits doc (surfaced via secondary; primary `platform.openai.com/docs/guides/rate-limits` not retrieved this session)

These gaps are flagged for the next session if the cluster requires deeper coverage of any.