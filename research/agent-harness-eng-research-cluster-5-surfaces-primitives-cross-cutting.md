# Cluster Deep-Dive 5 V2 — Deployment, Anthropic Surface Area, and Cross-Cutting Tradeoffs

## 1. Active Session Restatement

This deliverable is the V2 re-run of Cluster 5 of an agent-harness research project, executed under **corrected agnostic framing**: no user persona is assumed (solo, small team, enterprise team are all in scope); no specific stack is committed (n8n, OpenClaw, Claude Code CLI, Codex, LangGraph, Temporal, etc. are landscape options, not project commitments); "local-first" denotes a *design-time deployment surface* (developer-owned hardware) rather than an Ink & Switch-style architectural commitment to offline-first/CRDT/local-primary storage; cloud-managed and hybrid surfaces are first-class; **multi-LLM is the only architectural commitment that survives**; heterogeneous workflows (software engineering, web dev, content creation, pipeline automation) are a quality bar; production-grade engineering is the quality bar regardless of who uses it. The cluster is named "Deployment, Anthropic Surface Area, and Cross-Cutting Tradeoffs." Topics are ordered (1) deployment architecture across the surface spectrum, (2) Anthropic-specific surface area as of Q2 2026, and (3) cross-cutting tradeoffs synthesized into project-wide architectural meta-structure. The cluster builds on Sessions 1–3 substrate and Cluster 1–4 deep-dives plus the Context Correction and Project Framing documents, and closes the substrate phase of the project.

---

## 2. Executive Synthesis

1. **Anthropic's Q2 2026 model lineup has settled into a three-tier rate card with one pricing anomaly.** Haiku 4.5 ($1/$5 per MTok), Sonnet 4.6 ($3/$15), Opus 4.6 and Opus 4.7 ($5/$25). Opus 4.7 (released April 16, 2026) keeps Opus 4.6's sticker price but ships a new tokenizer that can yield up to ~35% more tokens for the same input text — effective cost-per-task can rise without the rate card changing. Opus/Sonnet 4.6 expose a 1M context window at standard pricing (no beta header); Haiku 4.5 caps at 200K. [HIGH]

2. **Managed Agents is now a real Anthropic primitive (public beta), not a research preview.** Launched April 8–9, 2026 with the `managed-agents-2026-04-01` beta header, $0.08/agent-runtime-hour on top of token pricing, with credential vault, sandboxed runtime, session/harness/sandbox interfaces, native OAuth (Slack/Notion/ClickUp), and Memory-for-Managed-Agents in public beta. Notion/Asana/Sentry/Rakuten cited as early adopters. This materially shifts the build-vs-buy frontier for harness scaffolding. [HIGH]

3. **Adaptive thinking has displaced manual `budget_tokens` as the recommended Anthropic extended-thinking mode.** On Opus 4.7 it is the *only* supported mode; manual `thinking:{type:"enabled", budget_tokens:N}` is rejected. On Opus/Sonnet 4.6 manual mode still works but is deprecated. Interleaved thinking is auto-enabled with adaptive thinking on Sonnet 4.6/Opus 4.6+; the `interleaved-thinking-2025-05-14` header is a no-op on Opus 4.7. Switching between adaptive and enabled/disabled invalidates message cache breakpoints. [HIGH]

4. **Cache-invalidation rules around thinking and Skills have important model-version splits.** On Opus 4.5+ and Sonnet 4.6+, thinking blocks are *preserved by default* even when non-tool-result user content arrives; on earlier Opus/Sonnet and *all* Haiku, thinking blocks are stripped, which silently breaks cache. Tool changes invalidate at the tool level; system changes invalidate system+messages; messages invalidate from the change point onward. Skills loaded dynamically from the filesystem do *not* automatically break the static prefix because Skills load via tool calls (bash reads of `SKILL.md`), not by mutating the prefix — but the *tool definitions* and any `cache_control` applied to system text must stay stable. [HIGH]

5. **Skills are now an open standard at agentskills.io, adopted by VS Code/Copilot, OpenCode, and the broader ecosystem.** Schema is a folder with `SKILL.md` containing YAML frontmatter (`name`, `description` required; optional `allowed-tools`, `disable-model-invocation`, `license`, `dependencies`) plus optional `scripts/`, `references/`, `assets/` subdirectories. Three-level progressive disclosure: (a) frontmatter metadata, (b) `SKILL.md` body, (c) bundled files loaded on demand via filesystem reads. Same format works across Claude.ai, Claude Code, Claude API (`/v1/skills` + `code-execution-2025-08-25` beta), and third-party clients. [HIGH]

6. **The deployment-architecture spectrum has three genuinely different operating regimes, and the right substrate differs by surface.** Local-development: Postgres-backed library (DBOS) or single-binary embedded server (Restate, Hatchet Lite, n8n with SQLite) minimize infra surface; cloud-managed: Temporal Cloud, Restate Cloud, Inngest Cloud, Hatchet Cloud, AWS Step Functions, Bedrock AgentCore (GA Oct 2025), Vertex AI Agent Engine, Azure Durable Functions / Microsoft Agent Framework, Cloudflare Workflows + Durable Objects + Agents SDK; hybrid: Temporal/Restate/Hatchet workers running locally against cloud control planes, or LangGraph with `DynamoDBSaver`/`PostgresSaver` to externalize checkpoints. n8n production realistically wants 4 vCPU / 8 GB RAM + Postgres + queue mode (Redis) before it stops being a single-machine prototype. [HIGH]

7. **Sandboxing has bifurcated by trust level.** Standard Docker shares the host kernel and is no longer considered adequate for *untrusted LLM-generated code*; the consensus 2026 stack is Firecracker microVMs (E2B, Sprites, AWS Lambda, ~125ms boot, dedicated kernel) or gVisor user-space-kernel (Modal, Google Agent Sandbox on GKE, ~10–30% I/O overhead). OpenAI's Agents SDK (April 2026) ships native Manifest abstraction with eight built-in providers (E2B, Modal, Docker, Vercel, Cloudflare, Daytona, Runloop, Blaxel). Anthropic's Code Execution tool runs inside a sandboxed container with bubblewrap/seatbelt isolation. Computer Use remains a *client-side* tool — you own the loop and the VM. [HIGH]

8. **Single-agent vs multi-agent has resolved into a workload-shaped pattern, not a global default.** Walden Yan's April 22, 2026 follow-up ("Multi-Agents: What's Actually Working") explicitly walks back blanket opposition: parallel-writer swarms still fail, but *read-heavy parallel sub-agents with single-threaded writes* (the pattern Anthropic's research system uses, that Claude Code uses for sub-agent search, and that Anthropic's three-agent generator/evaluator harness uses for full-stack dev) reliably outperforms single-agent for breadth-first tasks. Synthesis: keep writes single-threaded; use sub-agents for parallel exploration, evaluation, and context compression. [HIGH]

9. **Context engineering has matured into a named discipline with concrete API primitives.** Anthropic ships `clear_tool_uses_20250919` and `clear_thinking_20251015` (beta header `context-management-2025-06-27`) for selective server-side clearing, plus `compact_20260112` for summarize-and-replace. Tool Search Tool (`defer_loading: true`), Programmatic Tool Calling, and Tool Use Examples reduce tool-definition token overhead by ~85% in internal benchmarks. The deeper insight from Claude Code's leaked source map (March 2026): production harnesses run *four-tier* compaction (MicroCompact, AutoCompact at ~95-98% context, Full Compact, manual `/compact`), reserve a 13K buffer, cap summaries at ~20K tokens, and rehydrate the most recent files (≤5K tokens each) post-compaction. [HIGH for primitives, MODERATE for leaked-source numbers]

10. **The framework-vs-primitives debate has resolved into a workload/team-shape function, not an ideology.** Anthropic's "Building Effective Agents" (Dec 2024) primitives-first stance and HumanLayer's 12-Factor Agents own-your-prompt/own-your-context/own-your-control-flow stance both win at small team / bespoke topology / tight cost control. LangGraph + checkpointer (DynamoDB/Postgres), OpenAI Agents SDK, Microsoft Agent Framework, Mastra, CrewAI win at non-trivial graph topologies, multi-team ownership, audit-heavy compliance contexts, and when managed checkpointing/observability/HITL infrastructure would otherwise be rebuilt internally. [HIGH]

11. **The project-wide architectural backbone is filesystem-as-shared-substrate plus durable-execution-as-coordination-spine plus multi-LLM-router-as-only-fixed-commitment.** Filesystem appears as the convergent primitive across Skills (folder + `SKILL.md`), MCP-as-code (tool definitions as files), Anthropic's progress-file harness pattern (`claude-progress.txt`), Claude Code's tool-output spillover to disk, and Cloudflare Artifacts (Git-native versioned filesystem per agent). Durable execution survives as the coordination layer regardless of deployment surface; the substrate (DBOS/Temporal/Restate/Inngest/Hatchet/LangGraph+checkpointer/Cloudflare Workflows/Bedrock AgentCore/Vertex Agent Engine) is a deployment-surface-dependent decision, not a foundational one. [MODERATE — synthesis claim]

12. **The substrate phase of the project closes here.** Foundational decisions can be made now (multi-LLM commitment, durable-execution-as-spine, filesystem-as-shared-substrate, sandbox-isolation-strength-by-trust-level, OS-keychain-at-dev-vault-at-prod for secrets). Persona-dependent, workload-dependent, and deployment-surface-dependent decisions are explicitly deferred to the design phase that follows. [HIGH]

---

## 3. Per-Topic Deep Dives

### TOPIC 1 — Deployment Architecture Across the Surface Spectrum

**Topic restatement.** The harness must operate across three deployment surfaces — local-development (developer-owned hardware as design-time target), cloud-managed (vendor-hosted control planes), and hybrid (components distributed across the two) — without being architecturally locked to any one. This topic surveys self-hosted agent orchestrators, local-model runtimes, secrets managers, sandboxes, and control-plane services across all three surfaces, with slightly more depth on local-development per scope.

#### Canonical sources, deeply engaged

- **n8n self-hosting docs** (`docs.n8n.io/hosting/`, `docs.n8n.io/hosting/scaling/`, observed May 2026). Key claims: n8n runs as Community edition without a license; queue mode (Redis-backed worker pool) is "the best scalability"; benchmarks report up to ~220 workflow executions/sec/instance; SQLite is acceptable only for proof-of-concept, Postgres is required for production. n8n explicitly recommends Cloud over self-hosting for non-experts. **Strong on:** operational guidance, queue-mode primitives, performance benchmarks. **Weak on:** detailed cost-per-task analysis. **Connects to:** the hybrid pattern (n8n self-hosted with external Postgres + Redis is the canonical scale-out shape).
- **Temporal docs and engineering posts** (`temporal.io`, `temporal.io/blog`, observed May 2026). Key framings: "Durable Execution" as the category-defining term; Workflows are deterministic, Activities are non-deterministic and retried; "OpenAI uses Temporal for Codex" cited as production evidence; Vercel AI SDK + Temporal integration via `temporalProvider.languageModel()` and `proxyActivities` makes tool calls durable. **Strong on:** language SDKs (Go/Java/Python/TypeScript/.NET/Ruby), proven scale, observability via Temporal UI. **Weak on:** operational simplicity at small scale (production Temporal needs a service cluster: history, matching, frontend, worker, plus persistence and visibility stores). **Connects to:** Restate (lighter footprint, similar journal/replay model), DBOS (radically simpler, single-Postgres alternative).
- **Restate docs** (`restate.dev`, observed May 2026). Key framings: "single binary, no dependencies" for local; sub-100ms p99 workflow completion latency claimed; Restate Cloud GA with usage-based pricing; positioned against Temporal as lighter-weight, especially for edge/serverless. **Strong on:** developer ergonomics, Rust runtime performance. **Weak on:** ecosystem maturity vs Temporal.
- **DBOS docs and "DBOS vs Temporal" comparison** (`dbos.dev`, `tiarebalbi.com/en/blog/dbos-vs-temporal-postgres-durable-execution`, observed May 2026). Key claims: DBOS is an *embedded library* not an external orchestrator — workflow state and business data share the same Postgres transaction; integrating DBOS into a 110-LoC app requires "7 lines of code" vs Temporal's ">100 lines" plus splitting the app into worker+API services; DBOS breaks first on Postgres lock contention (workflow status table) and WAL pressure; Temporal breaks first on operational surface. **Strong on:** the architectural tradeoff between embedded-library and external-orchestrator approaches. **Weak on:** truly enormous-scale guidance (DBOS team explicitly aims at the "Postgres is enough" workload band).
- **Inngest docs** (`inngest.com`, `inngest.com/ai`, `inngest.com/docs`, observed May 2026). Key primitives: `step.run` (durable retriable step), `step.ai.infer` (offload LLM call to Inngest infra so serverless functions don't pay compute while waiting), `step.ai.wrap` (wrap any AI SDK call for tracing), AgentKit, Checkpointing (developer preview, ~50% workflow speedup with near-zero inter-step latency). **Strong on:** serverless-native ergonomics, AI-specific primitives. **Weak on:** self-hosting story (open-source Inngest server exists but Cloud is the default).
- **Hatchet docs** (`docs.hatchet.run`, observed May 2026). Key claims: Postgres-backed durability for both runtime and observability; ~25ms P95 dispatch latency in optimized setups; load-tested to 10K tasks/sec; `hatchet-lite` Docker image bundles RabbitMQ + admin CLI + REST + gRPC engine. **Strong on:** self-hosting simplicity (Postgres + optional RabbitMQ at scale), MIT license. **Weak on:** ecosystem reach vs Temporal.
- **Cloudflare Durable Objects + Workflows + Agents SDK** (`developers.cloudflare.com/durable-objects/`, `developers.cloudflare.com/agents/`, `blog.cloudflare.com/dynamic-workflows/`, observed May 2026). Key primitives: each agent is a Durable Object (single global instance, embedded SQLite up to 10 GB, hibernation, alarms, WebSockets); Workflows provide step-based durable execution on top; Dynamic Workflows + Durable Object Facets allow per-tenant code dispatch; Code Mode for MCP-as-code. **Strong on:** edge/serverless, zero-idle-cost multi-tenancy. **Weak on:** non-Workers runtimes (this is the most platform-locked of the cloud options).
- **AWS Bedrock AgentCore** (`aws.amazon.com/bedrock/agentcore`, observed May 2026). Key claims: GA October 2025; provides runtime, memory, gateway, identity (OIDC federation with Entra/Okta), and observability; framework-flexible (LangGraph, CrewAI, OpenAI Agents SDK supported); SharePoint ACL not natively supported. **Strong on:** AWS integration. **Weak on:** non-AWS portability.
- **Vertex AI Agent Engine + ADK** (`cloud.google.com/vertex-ai/generative-ai/docs/agents/adk`, observed May 2026). ADK is open source (Python and Java); Agent Engine is the managed runtime; pricing combines vCPU-hours + model + code execution + session storage + connector fees, harder to predict than Bedrock's per-token model.
- **Microsoft Agent Framework** (`learn.microsoft.com/en-us/agent-framework`, observed May 2026). Open source SDK launched December 2025; supports MCP and A2A; targets multi-agent enterprise systems with Azure-native auth.
- **LangGraph + DynamoDBSaver** (`docs.langchain.com/oss/python/langgraph/persistence`, `aws.amazon.com/blogs/database/build-durable-ai-agents-with-langgraph-and-amazon-dynamodb`, observed May 2026). Key claims: super-step boundaries are checkpoint boundaries; per-task pending writes survive node failures; DynamoDB items < 350 KB stored inline, larger checkpoints offload to S3; PostgresSaver and ValkeySaver available; AgentCoreMemorySaver integrates with Bedrock.
- **Local model runtimes**. Ollama (one-command install, OpenAI-compatible API on `:11434`, GGUF models, MLX backend on Apple Silicon since v0.19), LM Studio (GUI, Anthropic-compatible *and* OpenAI-compatible endpoints), llama.cpp (15–25% faster than Ollama on single GPU, CLI), vLLM (PagedAttention, continuous batching, ~16× Ollama throughput under concurrent load, NVIDIA-only practically). Red Hat benchmarks: vLLM throughput scales linearly with concurrency, Ollama plateaus at default 4-parallel cap. Hardware floor: 16 GB system RAM + 4–8 GB VRAM for 7–13B models in Ollama/LM Studio; 24 GB+ VRAM for 70B-class quantized models or production vLLM.
- **Cloud-hosted local-equivalent models**: Bedrock (Llama, Mistral, Claude via marketplace), Vertex AI Model Garden, Azure AI Foundry. Same OpenAI-compatible surface, same `model` parameter swap.
- **Sandboxes**. Firecracker (microVM, dedicated kernel, ~125ms boot, <5 MiB overhead — used by E2B and AWS Lambda); gVisor (user-space syscall interceptor, ~10–30% I/O overhead — used by Modal and Google Agent Sandbox on GKE); Kata Containers (Firecracker-as-VMM with Kubernetes-native APIs); Docker (shared kernel, *not* recommended for untrusted LLM code). Cold start benchmarks: Blaxel ~25ms, Daytona/E2B ~90–150ms, Modal sub-second. OpenAI Agents SDK (April 2026) Manifest abstraction supports E2B, Modal, Docker, Vercel, Cloudflare, Daytona, Runloop, Blaxel.
- **Secrets**. Cross-platform OS keyring access via `@napi-rs/keyring`, `keytar`, `zalando/go-keyring`, `python-keyring` — wraps macOS Security.framework, Windows Credential Manager (wincred.h), Linux Secret Service / libsecret with `secret-tool` fallback. HashiCorp Vault (centralized, AppRole/AWS-IAM/Kubernetes/JWT auth, dynamic secrets, leases), AWS Secrets Manager (auto-rotation lambdas, KMS encryption), GCP Secret Manager, Azure Key Vault, 1Password Connect (self-hosted REST bridge, plug-in for HashiCorp Vault). `age` (X25519 file encryption) + `sops` (KMS/age-encrypted YAML/JSON in git) is the standard "secrets-in-git" pattern. n8n external-secrets supports 1Password Connect, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager, HashiCorp Vault out of the box.

#### Patterns and primitives at depth

- **Local-development substrate selection logic.** Embedded library (DBOS) wins when Postgres is already in the stack, codebase is single-process, and "no new infrastructure" is a hard requirement. Single-binary server (Restate, Hatchet Lite) wins when language polyglot is needed and the team accepts one extra process. Full external orchestrator (Temporal, full Hatchet, Inngest open-source) wins when graph topology is non-trivial and observability/replay UI is worth the operational tax. n8n wins when *visual workflow authoring by non-engineers* is in scope; production-grade n8n is 4 vCPU / 8 GB RAM + Postgres + Redis-queue-mode.
- **Local model deployment as fallback, not primary.** The right architectural posture is: Ollama (or LM Studio) on developer hardware as a *degraded mode* when the cloud LLM is unreachable or for local privacy-sensitive tasks; vLLM on dedicated GPU for team/production self-hosting; OpenAI-compatible API surface as the abstraction so the harness routes by capability rather than by provider. Tasks that should *never* fall back to local: high-stakes reasoning (Opus-tier required), structured output with strict schemas (local quantized models drift), tool use requiring high JSON fidelity (parallel tool calls, Skills resolution). Degraded-mode signaling is a harness concern: emit a `model_tier=degraded` event into the durable workflow log so downstream HITL gates can require explicit human approval.
- **Secrets failure modes.** Keychain prompts blocking automated runs is the canonical local-dev failure (macOS Keychain ACL prompts when an unsigned process tries to read; Linux Secret Service requires unlocked session). Mitigation: a long-lived agent process started inside the user session that holds keyring handles, or `pass`/`gpg` for headless. In production: vault token expiration mid-agent (mitigation: `vault agent` template renewal, or short-lived AWS STS tokens via IAM auth); secret rotation breaking running agents (mitigation: rotation-aware retry with re-fetch on 401/403); secrets-in-shell-history (mitigation: `set +o history` in scripts, or pass via env from a vault sidecar).
- **Sandbox boundary placement in hybrid.** The right hybrid pattern is local sandbox for development (devcontainer or Firecracker via Docker Sandboxes / Sprites) and managed sandbox for production (E2B, Daytona, Modal, Anthropic Code Execution, OpenAI Code Interpreter). Anthropic Computer Use is *always* client-owned: Anthropic returns a tool call; the harness executes it inside a VM the harness owns; the harness sends the screenshot back. Beta header `computer-use-2025-11-24` for Opus 4.7/4.6/Sonnet 4.6/Opus 4.5 with enhanced actions including `zoom`. The system prompt overhead is 466–499 tokens plus 735 tool-definition tokens.
- **Control-plane comparison.** Cloud control planes provide: managed identity (IAM/Entra/Workload Identity Federation), durable queue with at-least-once or exactly-once semantics, observability collector + storage (CloudWatch, Cloud Logging, App Insights), assumed network reliability, autoscaling, multi-tenancy isolation. Closest local-development equivalents: Postgres + a durable-execution library (DBOS) provide queue durability and execution state; OpenTelemetry Collector + Tempo/Loki/Prometheus or Honeycomb-via-OTel provide observability; Docker Compose or k3d provide multi-tenancy at the namespace level; OS keychain provides identity-at-rest. The *operational* gap is autoscaling and assumed network reliability — these don't have honest local equivalents and define the migration trigger.
- **Migration-trigger threshold.** Empirically, the local-development substrate stops working when (a) concurrent workflow executions exceed ~1× single-machine RAM/2GB-per-active-flow, (b) a single workflow needs to survive developer-laptop sleep/restart, (c) more than one developer needs to share state, or (d) external webhooks must be receivable from the public internet. At that point: cloud-managed control plane + workers running anywhere (locally during dev, in cloud during prod) is the canonical hybrid.

#### Tradeoffs at depth

- **Cost.** Local-development: hardware is sunk, marginal cost of an extra workflow approaches zero, but engineering time to maintain Postgres + Redis + observability + backups is real. Cloud-managed: per-task pricing (Step Functions $25/M state transitions, Temporal Cloud per-action, Inngest per-step) compounds; managed sandboxes ($0.10–$0.30/hour typical) and Managed Agents ($0.08/agent-hour) add fixed overhead per active session. Hybrid often produces the lowest blended cost: cheap local dev + cloud only for production traffic.
- **Latency.** Local-development: <1ms for in-process steps (DBOS), 25–50ms for over-the-network local Temporal/Restate. Cloud-managed: 50–200ms control-plane round-trip typical; 25ms p95 for hot Hatchet, 25ms cold-start for Blaxel sandboxes, 90–150ms for E2B/Daytona, sub-second for Modal.
- **Reliability.** Cloud-managed wins on assumed network reliability and durable-storage replication. Local-development: a developer-machine crash mid-workflow is a real failure mode that must be designed around — DBOS recovers because state is in Postgres, but only if Postgres lives on a server, not the laptop.
- **Debuggability.** Local wins decisively for tight inner-loop. Cloud wins for production incidents (centralized logs, distributed traces, replay UI). The honest answer is both — Inngest Dev Server, Temporal local server, Restate single-binary all support local-then-prod parity.
- **Vendor lock-in.** Cloudflare Workers + Durable Objects has the highest lock-in (the whole programming model is platform-specific). Bedrock AgentCore is moderately locked (framework-flexible but identity/observability/storage are AWS). Temporal Cloud is the loosest (Temporal OSS is a clean migration path away). Self-hosted DBOS/Restate/Hatchet/Inngest OSS have effectively zero lock-in.
- **Operational complexity.** DBOS (1) << Hatchet/Restate (2) < Inngest OSS (3) < Temporal (4) < n8n production (4) < Bedrock AgentCore / Vertex Agent Engine (managed: 1; self-architected on top: 5).
- **Security posture.** Cloud-managed control planes inherit the cloud provider's compliance certifications (SOC2, ISO 27001, HIPAA-eligible, FedRAMP) — material for enterprise workloads. Self-hosted requires explicit posture work.
- **Portability.** Filesystem + git as the durable artifact substrate is portable across all three surfaces; database-backed durable state requires a migration path; cloud-managed-only state is least portable.

#### Failure modes in the field

- **Durable-state-loss-on-crash (local).** SQLite WAL on a laptop with FileVault/BitLocker can corrupt on hard power-off; mitigation is Postgres-on-separate-host even in dev.
- **Control-plane-rate-limit-cascade (cloud).** Bedrock has documented capacity constraints at peak demand; agents that retry aggressively against a rate-limited Bedrock endpoint can self-DDoS. Mitigation: token-bucket per provider, exponential backoff with jitter.
- **State-divergence-local-cloud (hybrid).** A developer running a worker against a cloud control plane while a production worker is also processing the same task queue can cause split-brain — workflow tasks dispatched to dev environment, then "completed" in dev, while prod thinks they're still pending. Mitigation: task-queue isolation by environment, never share queues between dev and prod.
- **Secrets-in-shell-history.** Documented across multiple post-mortems; mitigation: vault sidecar, `op run` (1Password CLI), or `aws-vault exec`.
- **Vault-token-expiration-mid-agent.** Documented in HashiCorp's own guidance; mitigation: `vault agent auto-auth` with sink files and templated secrets.
- **Sandbox-escape-developer-machine.** Standard Docker shared-kernel escapes (CVE-2024-21626 runc, CVE-2019-5736) are real. For untrusted LLM code on a developer machine, microVM (Firecracker via Sprites or local Sandboxes) is the right minimum.
- **Vendor-managed-sandbox-outage.** E2B, Modal, Anthropic Code Execution have all had public outages; harness must degrade gracefully (queue tasks, retry, or fall back to a secondary sandbox provider).
- **Network-flake-induced-degradation.** Streaming responses interrupted mid-message; mitigation: structured-output with `stop_reason` checks and resumable streaming where supported.
- **Resource-contention-single-machine.** vLLM + Ollama + Docker daemon + browser dev tools on one laptop will OOM. Mitigation: hard memory limits in Docker/devcontainer, swap-off for vLLM workloads, disable models when not in active use.

#### Open questions and unresolved debates

- Whether DBOS's Postgres-only model scales past ~10K active workflows without hot-shard pain (DBOS team is shipping Spark partitioning; not yet validated in public benchmarks).
- Whether Cloudflare Workers' programming model (single-region Durable Object instance) is acceptable for low-latency global agent fleets, or whether the multi-region replication patterns are ergonomic enough for production.
- Whether Bedrock AgentCore's framework-flexibility holds up when LangGraph or CrewAI ships a breaking change.

#### Architectural decision considerations

The design phase should weigh: (a) does the harness need to run locally without internet at all (rare; only relevant if local-first-in-the-Ink-&-Switch sense were a commitment, which it is *not* here); (b) does the team currently operate Postgres at sufficient skill to make DBOS or Hatchet viable, or is the operational tax of Temporal/Restate justified by graph topology; (c) what's the secrets failure-mode budget — keychain prompts that block automation are real and may push the design toward env-var-from-vault-sidecar even at dev time; (d) is sandbox isolation strength a function of whether code-from-LLM is actually executed (if yes, microVM minimum; if only deterministic tools, gVisor or Docker is acceptable). Do not propose a specific decision; surface the question shape.

---

### TOPIC 2 — Anthropic-Specific Surface Area as of Q2 2026

**Topic restatement.** Anthropic's API surface and product features that materially change harness design. Re-verified for Q2 2026 because pricing, model availability, beta headers, and Managed Agents status are moving targets and the project's substrate dates from earlier in 2026.

#### Canonical sources, deeply engaged (observation date: May 2026)

- **`platform.claude.com/docs/en/about-claude/pricing`.** Current pricing table:
  - **Haiku 4.5** — $1.00/MTok input, $5.00/MTok output, 200K context, 64K max output, model ID `claude-haiku-4-5-20251001`.
  - **Sonnet 4.6** — $3.00/MTok input, $15.00/MTok output, 1M context at standard pricing, 64K max output (some sources say 128K — verify per request), model ID `claude-sonnet-4-6`.
  - **Opus 4.6** — $5.00/MTok input, $25.00/MTok output, 1M context at standard pricing, 128K max output, model ID `claude-opus-4-6`.
  - **Opus 4.7** — $5.00/MTok input, $25.00/MTok output, 1M context at standard pricing, 128K max output, **new tokenizer** (~5–35% more tokens for the same input text), model ID `claude-opus-4-7`. Released April 16, 2026.
  - **Cache writes**: 1.25× input rate (5-minute TTL) or 2× input rate (1-hour TTL beta). **Cache hits**: 0.10× input rate (90% discount). **Batch API**: 50% discount on both input and output.
  - **`inference_geo: "us"`** parameter for Opus 4.6+ adds a 1.1× multiplier across all token categories (data residency).
  - **Fast mode** (Opus 4.6 only, beta research preview): 6× standard rates; stacks with caching multipliers.
- **`platform.claude.com/docs/en/build-with-claude/prompt-caching`.** Up to 4 `cache_control` breakpoints per request. Cache hierarchy: tools → system → messages. Changes at any level invalidate that level *and all subsequent levels*. Tool changes invalidate tool cache. Image presence/absence and `tool_choice` changes invalidate the cache. Thinking-parameter changes (enable/disable, budget allocation, mode switches) invalidate message-level cache breakpoints; system and tool cache survive thinking changes. **On Opus 4.5+ and Sonnet 4.6+, thinking blocks are preserved by default even when non-tool-result user content is added; on earlier models and all Haikus, they are stripped, which silently invalidates message cache.** Cache entries are organization-isolated.
- **`platform.claude.com/docs/en/build-with-claude/extended-thinking`** and **`/adaptive-thinking`**. Adaptive thinking (`thinking: {type: "adaptive"}`) is the recommended mode on Opus 4.7/4.6 and Sonnet 4.6; on Opus 4.7 it is the *only* supported mode (manual `budget_tokens` rejected). Effort levels: `low | medium | high (default) | xhigh | max`; `max` is Opus-only. Manual mode (`thinking: {type: "enabled", budget_tokens: N}`): N must be ≥ 1024 and < `max_tokens`. Interleaved thinking is auto-enabled with adaptive thinking on Sonnet 4.6/Opus 4.6+; the `interleaved-thinking-2025-05-14` header is a no-op on Opus 4.7. With interleaved thinking + tools, `budget_tokens` can exceed `max_tokens` because the limit becomes the full context window. Thinking content returned as `display: "summarized"` (default) — full thinking tokens are billed but only summaries returned. `display: "raw"` available on request via Anthropic sales contact for Claude 4 models.
- **`platform.claude.com/docs/en/build-with-claude/structured-outputs`.** GA `output_config.format` field with `type: "json_schema"` and a JSON schema; supported on Opus 4.7, Opus 4.6, Sonnet 4.6, and Haiku 4.5 (Haiku 4.5 added post-launch). Beta path `output_format` with `structured-outputs-2025-11-13` header still works on Sonnet 4.5/Opus 4.1. Strict tool use via `strict: true` on tool definitions guarantees parameter schema match. Incompatibilities: structured outputs do not work with citations (returns 400) or with message prefilling. Cost: 50–200 system-prompt tokens overhead + 2–3% effective cost increase at scale; almost always net cost savings vs retry loops.
- **`platform.claude.com/docs/en/build-with-claude/batch-processing`.** Async batches up to 24h, 50% discount, output-size cap raised to 300K tokens via `output-300k-2026-03-24` beta header for Opus 4.7/4.6 and Sonnet 4.6.
- **`platform.claude.com/docs/en/agents-and-tools/agent-skills/overview`** + **`code.claude.com/docs/en/skills`** + **`agentskills.io`** + **`github.com/anthropics/skills`**. SKILL.md schema:
  ```
  ---
  name: skill-name           # required, ≤64 chars, no slashes
  description: when to use   # required, ≤200 chars, write "pushy"
  allowed-tools: Read Grep   # optional whitespace-separated
  disable-model-invocation: false  # optional
  license: MIT               # optional
  dependencies: [...]        # optional
  ---
  # Markdown body
  ```
  Three-level progressive disclosure: (1) frontmatter loaded into tool description; (2) `SKILL.md` body loaded when Claude invokes; (3) bundled files in `scripts/`, `references/`, `assets/` loaded on demand by the model via filesystem reads. Resolution: Claude Code scans `~/.claude/skills/`, `.claude/skills/` (project), plugin-provided skills, built-ins; Claude.ai supports custom Skills as zip uploads (Pro/Max/Team/Enterprise plans, code execution required); Claude API requires beta headers `code-execution-2025-08-25`, `skills-2025-10-02`, `files-api-2025-04-14` and uses `/v1/skills` endpoints. **Cross-tool standard:** VS Code Copilot, OpenCode, GitHub Copilot CLI all parse the same SKILL.md format.
- **`code.claude.com/docs/en/overview`** + Claude Code leaked-source analyses (WaveSpeedAI, Decode Claude, bits-bytes-nn, March/April 2026). Claude Code architecture as publicly characterized: 4,600 source files, 512K LoC TypeScript; 4-tier compaction (MicroCompact in-place tool-output trim → AutoCompact at ~95-98% context with 13K-token reserve and ≤20K summary → Full Compact resetting working budget to 50K with file rehydration ≤5K/file → manual `/compact`); per-tool permission checks (~40 tools, names include Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch, Task for sub-agents, plus internal experimental ones); cost-aware error recovery that prefers free options first; 8-layer security model; streaming parallel tool execution. **Caveat:** these numbers come from community analysis of an accidentally-published source map (npm `@anthropic-ai/claude-code` v2.1.88, 59.8 MB `.map` file, March 31 2026); Anthropic confirmed the packaging error and issued DMCA takedowns. Treat specific counts as MODERATE confidence.
- **`platform.claude.com/docs/en/managed-agents/overview`.** Public beta as of April 8–9 2026. Beta header `managed-agents-2026-04-01` (SDK sets automatically). Pricing: standard token rates plus **$0.08 per agent-runtime-hour**. Endpoints: `POST /v1/agents` (create persistent agent with system prompt, tools, permissions), `POST /v1/sessions` (start execution session). Features in research preview: outcomes, multi-agent. **Memory for Managed Agents** in public beta: filesystem-based memories, API control, audit logs, portable stores. Credential vault stores secrets encrypted, available at runtime without exposing in code/logs; native OAuth for Slack, Notion, ClickUp; custom OAuth via MCP. Early adopters: Notion, Asana, Sentry, Rakuten.
- **`platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool`.** Beta header `computer-use-2025-11-24` for Opus 4.7/4.6, Sonnet 4.6, Opus 4.5; older `computer-use-2025-01-24` for Sonnet 4.5/Haiku 4.5/Opus 4.1/Sonnet 4/Opus 4/Sonnet 3.7 (deprecated). Enhanced actions (`computer_20251124`) include `zoom` with `region` parameter and `enable_zoom: true`. Client-side tool — the harness owns the loop. Token overhead: 466-499 system prompt tokens + 735 tool-definition tokens. ZDR-eligible because Anthropic doesn't store screenshots after the API response.
- **`platform.claude.com/docs/en/build-with-claude/context-editing`.** Beta header `context-management-2025-06-27`. Two strategies: `clear_tool_uses_20250919` (drops oldest tool results when token threshold or tool-use count threshold trips, with `keep`/`clear_at_least`/`exclude_tools` controls; `clear_tool_inputs: true` optionally drops the tool inputs too; placeholder text replaces cleared content) and `clear_thinking_20251015` (for thinking blocks; must come first in `edits` array if combined). Plus SDK-side `compact_20260112` strategy that summarizes and replaces history. Response includes `context_management.applied_edits` with `cleared_tool_uses` and `cleared_input_tokens` counts. Available on Sonnet 4.6/Opus 4.6/4.7 and earlier 4.x; Bedrock support exists but not for `count_tokens`.
- **`platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool`.** Memory tool (`memory_20250818`) with `view`, `create`, `insert`, `delete`, `rename`, `str_replace` commands provides Claude a local-directory-backed memory across conversations, retrievable outside the context window. Pairs with context editing — exclude memory tool from clearing so the model can save important context before tool results are dropped.
- **`anthropic.com/engineering/code-execution-with-mcp`** (Nov 2025). MCP-as-code pattern: present MCP servers as TypeScript files in a filesystem (e.g., `./servers/google-drive/getDocument.ts`), let the model write code that imports only the tools it needs. Reported 150K → 2K token reduction (98.7%) for example workflow; Cloudflare's parallel "Code Mode" reaches the same conclusion. **Tradeoff:** introduces sandbox-execution complexity but reclaims dramatic context budget.
- **`anthropic.com/engineering/advanced-tool-use`** (recent). Three new beta features: Tool Search Tool (`defer_loading: true` on tools makes them discoverable rather than upfront-loaded; ~85% token reduction; Opus 4.5 MCP eval improvement 79.5% → 88.1%), Programmatic Tool Calling, Tool Use Examples (universal standard for demonstrating tool usage).
- **`anthropic.com/engineering/effective-harnesses-for-long-running-agents`** + **`/building-effective-agents`** (Dec 2024) + **`/multi-agent-research-system`**. Two-fold harness: initializer agent sets up env (feature-list JSON, git repo, `claude-progress.txt`); coding agent makes incremental progress per session leaving "clean state" between sessions. Three-agent harness for full-stack (planner/generator/evaluator). Multi-agent research system: lead Opus 4 + parallel Sonnet 4 sub-agents → +90.2% on internal breadth-first eval vs single-agent Opus.

#### Patterns and primitives at depth

- **Cache architecture for an agent loop using prompt caching + extended thinking + Skills.** Optimal pattern: place the cache breakpoint at the *end of the system prompt* (above messages) and a second breakpoint at the *end of the tool block* (above messages). Skills loaded dynamically via `bash` reads of `SKILL.md` arrive in the *messages* block as tool results — they invalidate the message cache from that point forward but *not* system or tool cache. Extended thinking (adaptive) is preserved by default on Opus 4.5+/Sonnet 4.6+, so it does not silently break message cache when non-tool-result user turns arrive. On Haiku 4.5 (no preservation) and earlier models, switching from thinking-on to thinking-off breaks message cache; never mix thinking modes within a cached prefix.
- **Adaptive-thinking interaction with prompt cache.** Switching between adaptive and enabled/disabled invalidates message cache breakpoints; system prompts and tool definitions remain cached. Consecutive requests using adaptive thinking *preserve* prompt cache breakpoints. Recommendation: pick adaptive and stay there.
- **Skills resolution conflicts.** When the same skill name exists at user (`~/.claude/skills/`) + project (`.claude/skills/`) + plugin levels, Claude Code prioritizes project > user > plugin > built-in. agentskills.io spec doesn't mandate a global precedence, so cross-tool resolution may differ between Claude Code, OpenCode, and Copilot.
- **Managed Agents deployment model.** API endpoints `POST /v1/agents` and `POST /v1/sessions` return persistent agent objects with system prompt, tools (including custom MCP), and permissions. Anthropic's runtime owns sandbox + state + recovery + credential vault. The harness layer above shrinks: it routes user input, maintains durable workflow state for *coordination* across multiple Managed Agents, and integrates with HITL approval queues. Pricing $0.08/hour means a 24/7 long-running agent costs ~$58/month for the runtime plus token usage.
- **Computer Use harness pattern.** Always inside a dedicated VM/container with minimal privileges, no production credentials, limited internet. Anthropic's recommendation is human confirmation for "meaningful actions" — codify this as a HITL gate at the harness layer. Coordinate transformation between the harness's display and the model's analysis image dimensions is a known failure mode if resolution differs.

#### Tradeoffs at depth

- **Cost.** Sonnet 4.6 is the right default at $3/$15. Opus 4.7's tokenizer change can silently increase per-request costs by 5–35%; budget +20% if migrating a heavy workload. Caching at 90% discount + batch at 50% are stackable. Effort levels (`low/medium/high/xhigh/max`) on adaptive thinking trade tokens for quality.
- **Latency.** Adaptive thinking adds latency proportional to effort. Streaming starts faster on Sonnet 4.6 than Opus 4.6/4.7. `display: "summarized"` adds latency only for thinking summary generation (a separate model). On Opus 4.7, thinking content is *omitted* by default, causing a long pause before output — set `display: "summarized"` if streaming to humans.
- **Reliability.** Structured outputs eliminate JSON-parsing retries. Tool Search + Tool Use Examples improve tool-call accuracy.
- **Debuggability.** `applied_edits` in response makes context editing observable. Managed Agents introduces an opaque runtime — debugging a stuck Managed Agent requires Anthropic-provided observability hooks (audit logs, but not full tool-call traces).
- **Vendor lock-in.** Anthropic primitives are deeply intertwined: Skills depend on code execution, code execution depends on Anthropic's sandbox or yours, Computer Use is Anthropic-defined. Mitigation: keep the agent loop and message-shape orchestration in harness-owned code; treat Anthropic features as optional accelerants. AWS Bedrock and Vertex both expose Claude with Anthropic-native protocol, partially mitigating provider lock-in.
- **Operational complexity.** Managed Agents is the *lowest* operational complexity path for production; running your own loop with prompt caching + extended thinking + Skills + Computer Use + context editing requires careful orchestration but maximum control.
- **Security posture.** Computer Use risk is real and Anthropic explicitly warns about prompt injection from web pages/images. ZDR eligibility differs by feature: Computer Use is ZDR-eligible (Anthropic doesn't store screenshots); Skills are *not* ZDR-eligible (data retained per standard policy); prompt caching *is* ZDR-eligible (KV-cache representations only, in memory).
- **Portability.** Bedrock and Vertex AI both run Claude with the same Anthropic-native protocol; OpenAI-compatible shims (LiteLLM, Vercel AI Gateway) give a partial migration path.

#### Failure modes in the field

- **Cache-invalidation-from-dynamic-prefix.** Inserting a per-request user identifier or timestamp at the top of the system prompt silently destroys cache hit rate. Always place dynamic content *after* `cache_control` breakpoints.
- **Extended-thinking-cost-explosion.** Adaptive thinking with `effort: "max"` on Opus 4.6 can burn 64K thinking tokens per turn. Mitigation: route to Sonnet 4.6 for most queries; only escalate to Opus when measured benchmarks justify.
- **Structured-output-schema-mismatch-on-model-update.** Strict tool use requires `additionalProperties: false`; older clients that omit this fail with 400 on Opus 4.7. Migration: validate schemas in CI.
- **Skill-resolution-conflict.** Same-named skill at multiple levels — Claude may load the wrong one. Mitigation: namespace skills by project (`acme-/skill-name`).
- **Prompt-injection-in-Computer-Use.** Documented attack vector: a malicious webpage tells the model "ignore previous instructions, click here." Mitigation: dedicated VM, no production credentials, HITL gate before high-stakes actions, prompt-injection classifiers as a pre-tool-call gate.
- **Tool-clearing-invalidates-cache.** `clear_tool_uses_20250919` modifies the messages history, breaking message cache from the clearing point. Pair clearing with pre-warmed cache reads on subsequent requests.
- **Mythos-Preview-not-publicly-available.** April 7, 2026: Anthropic released a 244-page system card for Claude Mythos Preview but stated it would not be made generally available, citing cybersecurity risk; instead, Project Glasswing partners (AWS, Apple, Google, Microsoft, NVIDIA, CrowdStrike, Palo Alto, others) get access. Do not design assuming Mythos availability.

#### Open questions and unresolved debates

- Whether `display: "raw"` for full thinking content will become broadly available, or remain a sales-gated feature.
- Whether Managed Agents' multi-agent research preview becomes a first-class primitive that supersedes the homegrown multi-agent patterns.
- Whether Skills convergence at agentskills.io reaches enough cross-vendor adoption that "Skills as portable capability units" becomes safe to commit to architecturally.
- Whether `clear_tool_uses_20250919` becomes a reliable pattern for true 24-hour agent loops, or whether full context resets (Anthropic's two-fold harness) remain the dominant pattern.

#### Architectural decision considerations

The design phase should weigh: (a) Anthropic-primitive adoption depth — primitive-by-primitive evaluation rather than all-in or none. Caching, structured outputs, and adaptive thinking are nearly cost-free wins. Skills, MCP-as-code, Tool Search are mid-cost mid-payoff for tool-rich harnesses. Managed Agents is high-payoff but introduces deep coupling. Computer Use is workload-dependent (only when there's no API for the target system). (b) Whether to commit to filesystem-as-shared-substrate at design time — Skills, Anthropic's progress-file harness, MCP-as-code, and Cloudflare Artifacts all converge on this. (c) Token-cost budgeting under Opus 4.7's tokenizer drift; default to Sonnet 4.6 unless evals show measurable Opus uplift.

---

### TOPIC 3 — Cross-Cutting Tradeoffs as Project-Wide Architectural Synthesis

**Topic restatement.** This is the integrating topic. Under corrected agnostic framing, it produces an architectural decision framework — what is foundational, what is derivative, what is persona-dependent, what is workload-dependent, what is deployment-surface-dependent, what is deferrable. It does *not* specify a stack or commit to a persona. It closes the substrate phase of the project.

#### Decision-ordering DAG

**Foundational decisions (must be made first; all other decisions follow):**

1. **F1. Multi-LLM commitment** — *foundational, given as project commitment.* Drives provider-abstraction layer, model-router design, OpenAI-compatible-or-Anthropic-native protocol choice, and degraded-mode signaling.
2. **F2. Filesystem-as-shared-substrate** — *foundational, strongly indicated by source convergence.* Skills, Anthropic's progress-file harness, MCP-as-code, Claude Code's tool-output spillover, and Cloudflare Artifacts all converge here. Means: agent state, intermediate artifacts, and reusable capabilities are filesystem-resident; durable execution coordinates *over* the filesystem rather than replacing it.
3. **F3. Durable-execution-as-coordination-spine** — *foundational.* Whatever specific substrate is chosen, the harness assumes a durable workflow engine exists and structures the agent loop as `step.run`-equivalent retriable units. Without this commitment, the harness cannot cleanly support HITL, long-running tasks, recovery, or audit.
4. **F4. Sandbox-isolation-strength-by-trust-level** — *foundational.* For untrusted LLM-generated code: microVM (Firecracker/Kata) or vendor-managed (E2B/Modal). For deterministic tools and trusted code: gVisor or Docker. Decision shape: isolation level is a property of the *tool*, not the *harness*.
5. **F5. OS-keychain-at-dev / vault-at-prod for secrets** — *foundational.* Driven by failure-mode analysis: keychain-prompt-blocking is the dev failure mode, vault-token-expiration is the prod failure mode; the harness must abstract secret-fetch to handle both.

**Derivative decisions (constrained by foundational):**

- D1. Specific durable-execution substrate (DBOS / Temporal / Restate / Inngest / Hatchet / LangGraph+checkpointer / Cloudflare Workflows / Bedrock AgentCore / Vertex Agent Engine) — **deployment-surface-dependent**, derived from F3.
- D2. Specific sandbox provider (E2B / Modal / Daytona / Runloop / Sprites / Anthropic Code Execution / OpenAI Code Interpreter / self-hosted Firecracker) — **deployment-surface-dependent**, derived from F4.
- D3. Anthropic-primitive adoption depth — **workload-dependent**, derived from F2 (Skills only make sense if filesystem-as-substrate is committed).
- D4. Multi-agent topology — **workload-dependent**, single-threaded-writes is a strong default; parallel sub-agents only for read-heavy/exploration workloads (Yan 2026 follow-up).
- D5. HITL synchrony — **persona-dependent**: solo developer → synchronous interactive; team or production → async approval queues; enterprise compliance → both, with audit-ledger.
- D6. Observability backend (OTel-to-vendor vs dedicated LLM-observability platform like LangSmith/Helicone/Langfuse) — **deployment-surface-dependent and persona-dependent**.

**Independent / deferrable decisions:**

- I1. Specific LLM-provider routing logic (capability-based, cost-based, or quality-based routing) — deferred to design phase; can be added without architectural rework.
- I2. Tool granularity (coarse vs fine-grained) — deferred; influenced by Anthropic's Tool Search and Programmatic Tool Calling primitives.
- I3. Database-backed vs filesystem+git for durable state — *partially* foundational (filesystem committed) but db-augmented filesystem is a deferrable addition.

**Marking summary:**
- **Foundational:** F1–F5.
- **Persona-dependent:** D5, D6 (partly), interactive UX vs API-first surface.
- **Workload-dependent:** D3, D4, I2.
- **Deployment-surface-dependent:** D1, D2, D6 (partly).
- **Deferrable:** I1, I2, I3.

#### The major debates, integrated

- **Single-agent vs multi-agent.** Resolved as conditional: single-threaded writes always; parallel read-only sub-agents for breadth-first exploration, evaluation, and context compression. Surface conditions: parallel sub-agents win when (a) tasks are decomposable into independent read-only subqueries, (b) context compression is the bottleneck, (c) breadth-first search dominates the workload. Single-agent wins when (a) tasks have inherent sequential dependencies on writes, (b) consistency of style/edge-case handling matters, (c) context fits in one window. Do not pre-commit; surface the workload-shape signal.
- **Framework vs primitives.** Resolved as workload-and-team-shape function. Primitives win at small-team / bespoke-topology / tight-cost-control / Anthropic-primitive-heavy designs. Frameworks (LangGraph + checkpointer, OpenAI Agents SDK with sandbox+harness, Microsoft Agent Framework, Mastra, CrewAI) win at non-trivial graphs / multi-team ownership / managed-checkpointing-justified scale / audit-heavy compliance. Surface conditions: count concrete workflow nodes (>15 nodes typically justifies a graph framework); count team developers (>3 typically justifies framework opinionation); evaluate audit requirements (regulated industries justify framework HITL/observability infra).
- **LLM-as-judge vs deterministic-only gates.** Surface conditions: deterministic gates (schema validation, regex, type-check, test-pass) always at the trust boundary. LLM-as-judge is acceptable as a *signal* in retry budgets and as a soft scoring layer, never as the final gate for irreversible actions. The Anthropic three-agent harness (generator + evaluator) uses LLM-as-judge with structured criteria *plus* a separate deterministic test-pass gate — that combination wins.
- **Database-backed vs filesystem+git durable state.** Resolved partly: filesystem+git as the artifact substrate (commitments, code, progress files, Skills) and database as the *coordination* layer (workflow execution state, queue, observability). Both are present in production patterns.
- **Coarse vs fine-grained tool design.** Resolved by Tool Search Tool's evidence: many fine-grained tools work at scale *if* `defer_loading` and Tool Use Examples are used; coarse "do-everything" tools waste reasoning capacity. Default: fine-grained with deferred loading.
- **OTel vendor backend vs dedicated LLM-observability.** Surface conditions: existing OTel infra → extend with LLM-specific spans. Greenfield → dedicated LLM-observability (Langfuse OSS, Helicone, LangSmith). Hybrid is common (OTel for infrastructure, LLM-obs for token/latency/quality).
- **Synchronous vs async HITL.** Surface conditions: solo dev → sync via TUI/IDE. Team → async via Slack/email/HumanLayer. Enterprise → both, with SLA-bound async queues plus sync escalation paths.
- **Deployment-architecture surface (Topic 1).** Local-development for design-time; cloud-managed or hybrid for production; do not over-commit at substrate phase.
- **Anthropic-primitive adoption depth (Topic 2).** Primitive-by-primitive: caching/structured-outputs/adaptive-thinking are foundational-cheap; Skills/MCP-as-code/Tool-Search are tool-rich-workload-dependent; Managed Agents is high-leverage-but-coupled; Computer Use is workload-specific.

#### Cost envelope at integrated depth

Cost-per-task is a function of *deployment surface × workload class × reliability target*, not a single number.

- **Local-development surface, software-engineering workload, 99% reliability target:** dominant cost is developer time and electricity; per-task LLM cost is the only direct variable. Sonnet 4.6 with 60% prompt-cache hit rate yields ~$0.005-0.02/task for typical 5K-token interactions. Marginal cost of reliability (retries, validators) is negligible because retries cost LLM tokens, not infra.
- **Cloud-managed surface, customer-service workload, 99.9% reliability target:** LLM cost + control plane (Step Functions/Temporal Cloud/Inngest) + sandbox + observability. Each 9 of reliability beyond 99% adds 2–5× cost at the validator/retry/HITL layer because validator passes are themselves LLM calls. Managed Agents at $0.08/hour adds a fixed cost floor.
- **Hybrid surface, content-creation workload, 99% reliability target:** lowest blended cost — local dev avoids cloud control-plane fees, prod uses managed runtime only for production traffic.
- **Computer-use / pipeline-automation workloads:** sandbox cost dominates ($0.10-0.30/hour for managed sandbox + LLM cost). Reliability above 99.9% requires recovery-from-VM-crash logic.
- **Inflection points.** 99% → 99.9% adds retry budget (~1.3× LLM cost) + structured-output strictness (~1.05×). 99.9% → 99.99% requires HITL on irreversible actions and dual-validator gates (LLM-as-judge + deterministic) — typically 2–4× cost. 99.99% requires audit-ledger, multi-region durable execution, and human-on-call rotations — at this point cost is dominated by people, not LLMs.

#### Autonomy-vs-auditability operating points (per workload class)

| Workload class | Default autonomy | Audit-ledger requirement | HITL design |
|---|---|---|---|
| Code agents (refactor, bug-fix, feature) | High autonomy *within* a sandbox; PRs as the human-review gate | Git history is the audit ledger; commit messages tie to agent decisions | Async — review at PR time |
| Research agents (read-only) | Very high autonomy | Light — citation log + tool-call log | None for read-only; sync for citations-as-decisions |
| Customer-service agents | Medium autonomy; hard limits on refunds, account changes | Heavy — every action logged, decision rationale captured | Async approval queue for high-value actions; sync escalation for sentiment |
| Computer-use agents | Low autonomy by default | Heavy — screenshot trail + action log | Sync confirmation for any irreversible action |
| Content-creation agents | High autonomy in draft; low autonomy at publish | Medium — version history + diff | Async at publish gate |
| Pipeline-automation agents | Medium-high autonomy | Heavy — full input/output + step-result log; durable execution provides this naturally | Async with deterministic gates; sync if cost or external API thresholds tripped |

The HITL × audit-ledger interaction defines an *auditability floor*: even if HITL is async and rare, the audit ledger must be complete enough to reconstruct what the agent did and why. Durable-execution substrates (Temporal/Restate/DBOS/Hatchet/Inngest/LangGraph-checkpointer) provide this naturally; ad-hoc loops do not.

#### Project-wide architectural meta-structure

**Architectural backbone (foundational, decided now):**
- Multi-LLM provider abstraction (F1).
- Filesystem-as-shared-substrate for state, artifacts, and Skills (F2).
- Durable-execution-as-coordination-spine, substrate TBD (F3).
- Sandbox-isolation-strength-by-trust-level (F4).
- OS-keychain-at-dev / vault-at-prod secrets abstraction (F5).
- Anthropic foundational primitives: prompt caching, structured outputs, adaptive thinking — adopt as cheap wins.
- Single-threaded-writes default for any multi-agent topology.

**Derivative (made in design phase, constrained by foundational):**
- Specific durable-execution substrate (depends on deployment surface chosen).
- Specific sandbox provider (depends on deployment surface and isolation requirements per tool).
- Skills/MCP-as-code/Managed Agents adoption (depends on workload class).
- HITL synchrony and audit-ledger design (depends on persona and workload).

**Persona-dependent (deferred to persona definition):**
- Interactive UX surface (TUI vs IDE-extension vs web vs API-only).
- HITL synchrony.
- Multi-tenant vs single-tenant identity.

**Workload-dependent (deferred to workload prioritization):**
- Multi-agent topology.
- Tool granularity and grouping.
- Computer Use adoption.
- LLM-as-judge gating.

**Deployment-surface-dependent (deferred to deployment-surface choice):**
- Specific durable-execution substrate.
- Sandbox provider.
- Observability backend.
- Local model deployment as fallback.

**Deferrable (low cost to defer, can be added without rework):**
- Provider-routing logic (capability vs cost vs quality).
- Filesystem+git vs database augmentation.
- Specific tool authoring patterns.

**Closing statement.** This synthesis closes out the substrate phase of the agent-harness research project. The foundational decisions above are decided. Sessions that follow move into the design phase — persona definition, workload prioritization, deployment-surface choice, and the derivative-decision cascade those choices unlock.

---

## 4. Cross-Topic Synthesis

**Architectural couplings between Topics 1, 2, 3.** Deployment surface (T1) constrains which Anthropic primitives (T2) are usable in what configuration: local-development surface uses Anthropic's API directly; cloud-managed surface adds the choice of Bedrock AgentCore or Vertex Agent Engine as the proxy layer (different beta-header and feature-availability profiles); Managed Agents requires the Anthropic Platform path. Anthropic surface adoption depth (T2) shapes the cost-reliability tradeoff (T3): primitives like prompt caching reduce cost at every reliability tier, while Managed Agents reduces operational cost but increases vendor coupling. Topic 3 integrates these by treating deployment surface and Anthropic primitives both as derivative-not-foundational.

**Shared primitives and patterns.** Filesystem appears as the convergent foundational primitive across all three topics. T1: durable execution writes to filesystem (Cloudflare Artifacts, Anthropic progress files, devcontainer mounts). T2: Skills are folders with `SKILL.md`; MCP-as-code is tool-as-file; Anthropic's harness pattern is `claude-progress.txt`. T3: filesystem-as-shared-substrate is a foundational decision. Durable execution is the second shared primitive — it appears in T1 as substrate choice, in T2 as the Managed Agents runtime, and in T3 as foundational coordination spine.

**Source-level convergence and divergence.** Anthropic's primitives-first posture (Building Effective Agents, Effective Harnesses, Code Execution with MCP, Advanced Tool Use) consistently advocates: simple loops, filesystem state, single-threaded writes, primitives over frameworks. Framework vendors (LangGraph + LangChain, OpenAI Agents SDK, Microsoft Agent Framework, Mastra, CrewAI) consistently advocate: managed graph + state + checkpointing + observability + HITL infra at non-trivial scale. HumanLayer's 12-Factor Agents bridges both — own-your-prompt/context/control-flow at the application level, while explicitly endorsing durable workflow engines underneath. Cognition's 2026 follow-up resolves the multi-agent debate. Convergence on filesystem-as-substrate is broad; divergence on framework-vs-primitives is workload-shape-dependent.

**Closing decision-points.** (a) Deployment-surface choice — defer to persona/workload definition. (b) Anthropic-primitive adoption depth — adopt foundational-cheap primitives now (caching, structured outputs, adaptive thinking); defer high-coupling primitives (Managed Agents, Skills depth) to workload definition. (c) Integration with prior cluster decisions — multi-LLM commitment from substrate, filesystem-as-substrate convergent across clusters, durable-execution-spine from cluster 2/3 work, sandbox-isolation-strength from cluster 4 — all consistent with this cluster's foundational decisions.

---

## 5. Open Questions and Recommended Next Probes

1. **Workload prioritization probe.** Which 2–3 workload classes (code agents, research agents, customer-service, computer-use, content-creation, pipeline-automation) are first-class for the harness? Until this is decided, D3/D4 (Anthropic-primitive depth, multi-agent topology) cannot be settled.
2. **Persona scope probe.** Solo dev, small team, enterprise — or all? Persona scope drives HITL synchrony, identity model, and observability backend. The harness can support multiple personas, but the *first-class* persona drives default UX.
3. **Deployment-surface commitment probe.** Local-development is the design-time target; production-time can be local-only, cloud-managed, or hybrid. The choice between them drives D1/D2 (substrate, sandbox).
4. **Mythos / next-frontier-model probe.** Should the harness be designed assuming frontier-model availability? Anthropic's Project Glasswing model is gated. OpenAI's GPT-5.4 is widely cited. Multi-LLM abstraction protects against this, but workload-specific quality bars may demand specific frontier capabilities.
5. **Skills standard adoption probe.** Re-verify in 6 months whether agentskills.io reaches enough cross-vendor adoption to commit to Skills as the portable capability unit.
6. **Managed Agents GA probe.** Currently public beta. Re-verify GA status, pricing changes, and multi-agent feature availability before committing to it as a substrate.
7. **DBOS scale probe.** Whether Postgres-only durable execution scales past ~10K concurrent workflows in real benchmarks.
8. **Context-editing safety probe.** Whether `clear_tool_uses_20250919` introduces silent agent-state-loss bugs (the "garbage-collector-without-write-barriers" critique deserves empirical investigation before adoption).

---

## 6. Source Bibliography

Marked: [substrate] = present in prior project substrate; [deepened] = engaged at greater depth in this session; [new] = introduced in this session. Observation date noted for moving-target sources.

**Anthropic primary sources (all observed May 2026):**
- Anthropic. *Pricing.* `platform.claude.com/docs/en/about-claude/pricing` [deepened]
- Anthropic. *Prompt caching.* `platform.claude.com/docs/en/build-with-claude/prompt-caching` [deepened]
- Anthropic. *Building with extended thinking* and *Adaptive thinking.* `platform.claude.com/docs/en/build-with-claude/extended-thinking`, `/adaptive-thinking` [deepened]
- Anthropic. *Structured outputs.* `platform.claude.com/docs/en/build-with-claude/structured-outputs` [new]
- Anthropic. *Context editing.* `platform.claude.com/docs/en/build-with-claude/context-editing` [new]
- Anthropic. *Agent Skills overview.* `platform.claude.com/docs/en/agents-and-tools/agent-skills/overview` [deepened]
- Anthropic. *Claude Managed Agents overview.* `platform.claude.com/docs/en/managed-agents/overview` [new]
- Anthropic. *Computer use tool.* `platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool` [deepened]
- Anthropic. *Code Claude — Skills.* `code.claude.com/docs/en/skills` [deepened]
- Anthropic Engineering. *Building Effective Agents,* Dec 2024. `anthropic.com/engineering/building-effective-agents` [substrate, deepened]
- Anthropic Engineering. *Effective harnesses for long-running agents.* `anthropic.com/engineering/effective-harnesses-for-long-running-agents` [deepened]
- Anthropic Engineering. *Code execution with MCP,* Nov 2025. `anthropic.com/engineering/code-execution-with-mcp` [new]
- Anthropic Engineering. *Advanced tool use.* `anthropic.com/engineering/advanced-tool-use` [new]
- Anthropic. *How we built our multi-agent research system* (engineering blog, June 2025) [substrate]
- GitHub: `anthropics/skills` [deepened]
- agentskills.io. *Agent Skills format specification.* [new]

**Substrate platforms (all observed May 2026):**
- Temporal. `temporal.io`, `temporal.io/blog/durable-execution-meets-ai-why-temporal-is-the-perfect-foundation-for-ai`, `temporal.io/blog/of-course-you-can-build-dynamic-ai-agents-with-temporal` [deepened]
- Restate. `restate.dev` [deepened]
- DBOS. `dbos.dev/blog/durable-execution-coding-comparison`, Tiarê Balbi Bonamini, *DBOS vs Temporal,* `tiarebalbi.com/en/blog/dbos-vs-temporal-postgres-durable-execution` [deepened]
- Inngest. `inngest.com`, `inngest.com/ai`, `inngest.com/blog/ai-orchestration-with-agentkit-step-ai`, `inngest.com/blog/building-durable-agents` [deepened]
- Hatchet. `hatchet.run`, `docs.hatchet.run`, GitHub `hatchet-dev/hatchet` [new]
- n8n. `docs.n8n.io/hosting/`, `docs.n8n.io/hosting/scaling/`, `docs.n8n.io/external-secrets/` [deepened]
- Cloudflare. `developers.cloudflare.com/durable-objects/`, `developers.cloudflare.com/agents/`, `blog.cloudflare.com/dynamic-workflows/` [new]
- AWS. *Build durable AI agents with LangGraph and Amazon DynamoDB,* AWS Database Blog [deepened]
- AWS. *Bedrock AgentCore* (overview, identity, observability) [substrate, deepened]
- Google Cloud. *Vertex AI Agent Builder + ADK* documentation [substrate, deepened]
- Microsoft. *Agent Framework* documentation [substrate, deepened]
- LangChain. `docs.langchain.com/oss/python/langgraph/persistence`, GitHub `langchain-ai/langgraph` [deepened]
- Zylos Research. *Durable Execution Patterns for AI Agents,* Feb 17 2026 [new]

**Local model and sandbox:**
- Red Hat. *Ollama vs vLLM benchmark.* `developers.redhat.com/articles/2025/08/08/ollama-vs-vllm-deep-dive-performance-benchmarking` [new]
- Sitepoint, glukhov.org, knovo.dev. *Ollama / LM Studio / vLLM 2026 comparisons* [new]
- Northflank, Superagent, Modal blog. *Sandbox provider comparisons 2026* [new]
- E2B, Daytona, Modal, Sprites.dev product docs [new]
- OpenAI. *The next evolution of the Agents SDK,* April 16 2026 [new]

**Secrets management:**
- HashiCorp. *Vault Agent + AWS auth tutorial.* `developer.hashicorp.com/vault/tutorials/vault-agent/agent-aws` [new]
- 1Password. *Vault plugin for HashiCorp Vault.* GitHub `1Password/vault-plugin-secrets-onepassword`, `1password.com/resources/guides/managing-developer-secrets-with-1password` [new]
- Git. *credential-helpers.* `git-scm.com/doc/credential-helpers` [new]
- npm `cross-keychain`, GitHub `hrantzsch/keychain` [new]
- FiloSottile/age, getsops/sops [substrate]

**Practitioner canon (Topic 3):**
- Anthropic. *Building Effective Agents,* Dec 2024 [substrate, deepened]
- HumanLayer. *12-Factor Agents,* GitHub `humanlayer/12-factor-agents`, `humanlayer.dev/12-factor-agents`, Dex Horthy [substrate, deepened]
- Cognition. *Don't Build Multi-Agents,* Walden Yan, June 2025 [substrate]
- Cognition. *Multi-Agents: What's Actually Working,* Walden Yan, April 22 2026, `cognition.ai/blog/multi-agents-working` [new]
- Eugene Yan. *Patterns for Building LLM-based Systems & Products.* `eugeneyan.com/writing/llm-patterns/` [substrate, deepened]
- Simon Willison. *The lethal trifecta for AI agents,* `simonw.substack.com/p/the-lethal-trifecta-for-ai-agents` [new]
- Phil Schmid. *Single vs Multi-Agent System.* `philschmid.de/single-vs-multi-agents` [new]

**Claude Code architecture (community analysis of leaked source map, March/April 2026):**
- WaveSpeedAI Blog. *Claude Code architecture deep dive,* `wavespeed.ai/blog/posts/claude-code-architecture-leaked-source-deep-dive/` and *Claude Code agent harness architecture,* `wavespeed.ai/blog/posts/claude-code-agent-harness-architecture/` [substrate, deepened — confidence MODERATE because community-derived from accidentally-published source map]
- Decode Claude. *Inside Claude Code's Compaction System.* `decodeclaude.com/compaction-deep-dive/` [new]
- bits-bytes-nn.github.io. *Claude Code Architecture Analysis,* March 31 2026 [new]

**Anthropic Q2 2026 product news (re-verified):**
- SiliconANGLE. *Anthropic launches Claude Managed Agents,* April 8 2026 [new]
- InfoQ. *Anthropic Introduces Managed Agents,* April 2026 [new]
- Pasquale Pillitteri. *Anthropic Managed Agents and Cowork GA,* April 9 2026 [new]
- Releasebot. *Anthropic Release Notes — May 2026* [new]
- BenchLM, Finout, CloudZero, AI Pricing Guru. *Claude pricing analyses Q2 2026* [new — pricing cross-verification]

**Local-first reference (for clear distinction):**
- Ink & Switch. *Local-first software,* 2019 [substrate — cited only to clarify that "local-first" in the project sense is *not* the Ink & Switch sense]

[Confidence note: citations to leaked-source-map analyses of Claude Code (WaveSpeedAI, Decode Claude, bits-bytes-nn) are tagged MODERATE confidence — the analyses are corroborated across multiple independent posts but derive from a packaging error rather than official Anthropic documentation. Specific tool counts, compaction trigger percentages, and architectural detail numbers should be re-verified against official Anthropic engineering posts before being committed to the design phase.]