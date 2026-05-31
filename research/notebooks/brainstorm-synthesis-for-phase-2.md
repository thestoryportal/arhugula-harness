# Brainstorm Synthesis for Phase 2 Persona Surfacing

**Purpose:** Consolidated priming context for the systems architect skill entering Phase 2. Synthesizes 10 NotebookLM brainstorm chat outputs (5 broad-sweep round 1 + 5 granular round 2) into per-axis convergence / divergence maps, harness instance citations, permanent-tension flags, and a consolidated architect's question scaffold. **Loads into the harness project KB; does not replace the underlying corpus.**

**Citation discipline (read first):** Specific harness names (Microsoft Agent Framework, openrig, LangGraph, Trellis, ACP, Optio, Cline, kilocode, pi-mono, etc.) are retained as named in the chat outputs. Label-shaped claims (F1–F5 foundational decisions, T1–T4 permanent tensions, P-XX-N pattern IDs) are retained as quoted from NotebookLM but should be **reconciled against the harness project KB's canonical form** (Pattern Reference Catalog v1.0, Cluster 5 V2 §3, Project Workflow v1.0) before any ADR cites them. Internal numeric citations from NotebookLM ("1, 2, 5–7") have been stripped; topic-file provenance is given in the footer.

**Path B brainstorm round integrated:** T3 (per-task vs per-company deployment unit) and eval-methodology / Husain-loop content are folded into §4, §5, §7, and §9. No PENDING items remain.

**V3 framing constraint preserved:** No persona, stack, or deployment-surface commitment. The synthesis illuminates the design space; it does not pre-empt Phase 2.

---

## §1. Control Plane (orchestration, routing, multi-agent topology)

**Convergence:** Weak. Topology is workload-shaped, not architecture-shaped. The corpus has converged only on what topology is *not* — namely, parallel multi-agent writes are unsafe ("digital gossiping," Cognition's harsh reality check), so multi-agent systems are strictly for reads/evaluations while writes remain single-threaded.

**Divergence:** Wide. Five topology classes appear in the corpus, each fitting different workload characteristics:

| Topology | Concrete examples | Workload predictor |
|---|---|---|
| Orchestrator-worker | Anthropic Multi-Agent Research System; MS Agent Framework "Magentic"; Dify Supervisor Mode | Read-oriented, breadth-first exploration; unpredictable subtask shape; centralized error recovery |
| Decentralized handoff | OpenAI Agents SDK Handoffs; MS Agent Framework Handoff orchestration; Ruflo "Mesh" | Linear or gated decision graph; full ownership transfer (e.g., support triage); shallow recovery |
| Hierarchical sub-agent | Cursor Planners/Workers/Judges; Cognition "Manager Devin"; Google ADK | Deeply nested decomposition; long-horizon tasks (hours/days); tree-structured parallelism |
| Evaluator-optimizer loop | Anthropic Evaluator-Optimizer; Reflexion (Actor/Evaluator/Self-Reflection); disler the-verifier-agent | Iterative self-correction; objective success criteria available; high latency tolerance |
| Single-agent ReAct | Claude Code CLI; smolagents CodeAgent; 12-Factor Micro-Agents | Tight coordination; sequential write tasks; predictable boundaries; low latency |

**Permanent tensions located here:** T1 (filesystem-as-orchestrator vs framework-orchestration; ICM and Meta-Harness vs deepagents/Dify/VoltAgent; 12-Factor Agents splits the difference). T2 (single-process vs multi-process topology; Cline/OpenHands/VoltAgent vs openrig vs Optio/ACP).

**Cost-knob model routing layered on top:** Declarative/static (Roo Code per-mode model binding; oh-my-openagent per-role fallback chains; kilocode unified gateway allowlists) vs embedding-similarity/classifier (OptiRoute kNN, CARGO embedding regressor; semantic caches as pre-routers) vs LLM-as-router (xRouter RL-trained, success-gated, cost-shaped reward; OpenAI Agents SDK manager). Routing accuracy varies (CARGO 76.4% top-1; xRouter matches GPT-5 accuracy at up to 80% cost reduction), and each adds its own latency tax (µs–ms for embeddings; 50–200+ ms for LLM routers).

**Thin/speculative areas:** Decentralized handoff has the lowest reliability and hardest debuggability per the corpus — but lacks empirical performance metrics. Multi-agent code generation claims were highly speculative until Cognition's reality check; field has converged that writes must remain single-threaded. No formalized heuristics for *exactly when* to fan out vs stay single-agent; the corpus notes ~15× token cost amplification for multi-agent but defers the fan-out trigger to manual prompt-engineered scaling rules.

---

## §2. Information Substrate (context, prompts, memory, durable state)

**Convergence:** Strong on filesystem-as-shared-substrate (F2). Cluster 5 V2 explicitly notes this as a foundational architectural decision where the field has strongly converged. Harnesses including ICM, Meta-Harness, DeerFlow, pi-mono, Trellis, kilocode, Anthropic's canonical long-running agent harness (claude-progress.txt, feature_list.json + git commits as state ledger) all coordinate *over* the filesystem rather than replacing it with in-memory graph abstractions. Driven heavily by Anthropic's "Code execution with MCP" pattern and progressive-load skills, which shrink massive tool schemas into simple filesystem reads (grep/glob).

**Divergence:** Wide on durability tier choice. The five-tier model (filesystem / git / checkpoints / vector store / ledger) splits hard by deployment surface and persona:

| Tier | Stores | Adopts | Rejects |
|---|---|---|---|
| Filesystem | Working memory; capability ledger; SKILL.md; project context (CLAUDE.md, .kilocode/rules/memory-bank/); progress trackers; intermediate tool outputs | Claude Code, Aider, ICM, Meta-Harness, DeerFlow, kilocode, pi-mono, Trellis | ACP, Cloudflare Agents (Durable Objects), Optio |
| Git | Atomic commits of code changes; feature_list.json updates; shadow-repository checkpoints; user-vs-agent edit separation (Aider "dirty commits"); concurrent sub-agent isolation (kilocode worktrees) | Claude Code, Aider, kilocode | Dify, VoltAgent, deepagents, 12-Factor Agents |
| Checkpoints | Serialized graph state at super-steps; channel values, next nodes, thread IDs, pending writes; relational/NoSQL backed | LangGraph (and deepagents), MS Agent Framework, DBOS, Hatchet, Inngest | ICM, Meta-Harness, Claude Code, openrig |
| Vector store | Document embeddings; semantic facts; user preferences; cached responses; ANN-retrieved long-term semantic memory | Mem0, Dify, VoltAgent, LlamaIndex, AWS Bedrock AgentCore, Redis LangCache | Claude Code, ICM, Meta-Harness, single-file agents |
| Ledger (event-sourced) | Immutable append-only event history; LLM thoughts, tool executions, human approvals, system commands; deterministic replay | Temporal, 12-Factor Agents, Anthropic Managed Agents, Kode-Agent SDK, Maestro (audit.jsonl, decisions.jsonl), Paperclip | Basic LangGraph, ICM, simple SFAs |

**Memory tier architectures:** CoALA episodic / semantic / procedural decomposition is the corpus reference. Studied harnesses implement these tiers unevenly — some implicit, some absent, some conflated. Within-turn context residence (prompt cache breakpoints, dynamic suffix) is distinct from across-turn persistence; the central design tension is which knowledge belongs in static prefix vs dynamic suffix vs durable state.

**Costs of filesystem-as-substrate:** Concurrency limits (no built-in distributed locking; ICM explicitly rejects high-concurrency multi-user; openrig parallel rigs trample shared ports/local DBs); latency overhead on JIT navigation (grep/ls/cat slower than indexed RAG); host-bound orchestration (single namespace presupposed; cross-cloud requires shared network storage); semantic routing failures (no compile-time safety on folder hierarchies; file-based compaction risks premature deletion of historical context).

---

## §3. Action Surface (tools, skills, MCP, validation)

**Convergence:** Strong on the strict-mode tool contract (universal across the harnesses surviving in production). Strong on the descriptions-as-prompts discipline. Strong that capabilities decompose into three primitives:

| Primitive | Decision criteria | Process boundary | Trust gradient | Examples |
|---|---|---|---|---|
| In-process tools | High trust; zero latency; foundational harness capabilities; harness-author ownership | None (same memory space) | Absolute trust required | Claude Code ~20 base tools (bash, FileRead, FileEdit); pi-mono TypeBox tools |
| MCP servers | External state mutation; credential isolation; third-party authorship; cross-platform reuse (solves N×M integration) | Strict out-of-process (STDIO/HTTP/SSE; container/microVM/remote) | Zero-trust; OAuth 2.1 Resource Servers; LLM never sees keys | Goose AAIF (MCP-native, abandons in-process plugins); Dify (MCP client); openrig (17 tools via MCP for tmux topology self-management) |
| Skills | Domain-expert authorship; procedural workflows; progressive context disclosure (~100-token metadata, full markdown on activation) | Executes via existing code-execution/bash tools | Inherits trust of execution sandbox | DeerFlow (recursive SKILL.md discovery); Trellis (meta-skill across 14 host harnesses) |

**Divergence:** Wide on the wrap-vs-equip-vs-MCP boundary. The corpus is explicitly contradictory on Skills-vs-MCP overlap — Anthropic's "Code Execution with MCP" exposes MCP servers as TypeScript files in a directory the agent explores via bash, which mechanically looks identical to a Skill (script in folder executed via bash). Community is divided: some argue Skills can subsume MCP via single-tool wrappers; others argue MCP is for API capabilities and Skills are for procedural knowledge.

**Permanent tension located here:** T4 (markdown-spec-driven vs code-driven configuration; Maestro/Trellis/Agency-Agents vs deepagents/VoltAgent/OpenHands).

**Validation pipeline shapes** (cross-references operational discipline §4):

| Pattern | Loop shape | Fail-class fit |
|---|---|---|
| Deterministic-gate-only | Schema/typecheck/lint/test gates; retry-on-fail; exit-on-permanent-fail | Programmatically verifiable outputs (code, structured data) |
| LLM-as-judge-only | Model-based judge; retry-on-fail; exit-on-budget-exceeded | Outputs without deterministic check; risk of judge-base-model collision |
| Hybrid evaluator-optimizer | Deterministic outer ring + judge inner ring; Reflexion-style verbal feedback | Mixed fail-class; iterative refinement valuable |

**Tool-sprawl tension:** When does tool_search become preferable to bulk-loading? Corpus shows Anthropic's "Code execution with MCP" achieves 98.7% token reduction by dynamic loading — but at the explicit cost of requiring secure execution (sandbox is mandatory). The cost is also paid in routing accuracy and latency.

---

## §4. Operational Discipline (reliability, observability, security, HITL, cost)

**Convergence:** Strong on what production-grade-from-day-one looks like. Industry pattern: teams adopt magic frameworks for scaffolding speed, hit a 70–80% reliability wall, reverse-engineer the framework, and start over. Harnesses surviving in production view agents primarily as software components requiring classical engineering, treating the LLM as a probabilistic engine wrapped in deterministic guardrails.

**The seven architectural commitments of production-grade-from-day-one:**

1. **Sandbox isolation calibrated by trust level.** Treat isolation as adversarial, not just resource partitioning. Data-only tools tolerate language-level sandboxing; agent-generated code execution requires microVMs (Firecracker, gVisor, Kata).
2. **Durable execution + state ledgers.** Abandon in-process while loops for event-sourced durability (Temporal, DBOS, LangGraph checkpointing). Append-only event log distinct from materialized state. Resume, replay, audit without losing work.
3. **Idempotency keys for mutating actions.** At-least-once execution is reality; every state-mutating tool call requires an idempotency-key. Replay cached results instead of duplicating side effects.
4. **Strict contracts and validation cascades.** Constrained decoding (OpenAI structured outputs, XGrammar) for mathematical JSON guarantees. Deterministic code validators (regex, type checks) layered before LLM-as-a-judge.
5. **Circuit breakers and jittered retries.** Full-jitter exponential backoff. Per-provider circuit breakers. Fail fast during systemic outages; prevent token burn.
6. **OpenTelemetry observability.** GenAI semantic conventions; canonical span hierarchies (invoke_agent → execute_tool); token costs and latencies mappable directly to agent behaviors.
7. **HITL as an asynchronous tool.** Treat human escalation as a standard tool call, not an exception. Workflow hibernates via durable waits without consuming compute until human responds. Survives network interruptions and multi-day delays.

**HITL primitive design spectrum:**

| Granularity | Mechanism | Operator-experience cost | Workload tolerance |
|---|---|---|---|
| Coarse (approve/deny on tool call) | Decorator (HumanLayer @hl.require_approval()); CLI permission modes (Claude Code deny→ask→allow) | Low integration cost; high approval-fatigue risk at frequency; synchronous latency | Infrequent irreversible actions (DB writes, financial transactions); fails on iterative exploratory tasks |
| Medium (rubric-prompt review / dry-run) | Predicted-action handoff packet with confidence + alternatives; evaluator-optimizer loop with human grading | Moderate integration cost (mock execution + UI); higher decision quality at moderate latency | Async SWE (PR review); content drafts; data pipeline changes; fails on real-time UX |
| Fine (interrupt/resume at any agent step) | LangGraph interrupt(); Temporal durable signals | High integration cost (persistent checkpointer + idempotent side effects); excellent operator UX (async response, exact state inspection) | Multi-day enterprise workflows; async Slack/email; fails on ephemeral scripts and DB-less deployments |

**Cost knob mechanics (three primary knobs):**

| Knob | Mechanism | Tradeoff | Examples |
|---|---|---|---|
| Model routing | Declarative / embedding-similarity / LLM-as-router | Static = zero overhead but over-provisioning; embedding = µs–ms latency, ongoing index maintenance, ~76% top-1 accuracy; LLM = highest accuracy but 50–200+ ms tax | (cross-ref §1: Roo Code, oh-my-openagent, kilocode; OptiRoute, CARGO; xRouter, OpenAI Agents SDK manager) |
| Prompt caching | Static-prefix-only vs dynamic/conversational | Static = reliable 90% read discount; dynamic = max savings if hit, **catastrophic silent zero-cache failure if breakpoint mutates by one character** (paying 1.25× write penalty per call with no warning) | Spring AI SYSTEM_ONLY/TOOLS_ONLY; Meta-Harness anthropic_caching.py; pi-mono StreamFn middleware; LangChain JS dynamic; Spring AI CONVERSATION_HISTORY |
| Batch API / async pricing | JSONL submission + custom_id mapping; 50% flat discount stackable with cache for 95% total | Trades synchronous latency for cost; **fundamentally breaks sequential agentic workflows** (24h window per step makes multi-step chains impossible) | Temporal Anthropic Message Batches API pattern (durable workflow state); 12-Factor Factor 11 "Trigger from anywhere" |

**Out-of-loop eval discipline (Husain loop):** Distinct from in-loop gating (which catches schema violations and immediate execution errors at runtime), out-of-loop eval is the offline alignment + observability mechanism for criteria drift and generalization failures. The corpus surfaces an explicit error-analysis-first workflow: a principal domain expert ("benevolent dictator") reviews traces, writes open-coded critiques, axial-codes them into a failure-mode taxonomy, then builds automated evaluators against that specific taxonomy. Demonstrated explicitly by Arize Phoenix, VoltAgent VoltOps, and Husain's evals-skills plugin (which ships error-analysis and judge-prompting workflows as Skills). In-loop gating examples — distinct discipline, runtime mechanism — include 12-Factor Agents (stateless reducer + tools-as-structured-outputs feeding schema errors back into context for retry; gate decoupled from validator), Claude Code (Go-based deny-first guardrail engine, every tool call evaluated before execution), OpenAI Agents SDK (input/output/tool guardrails with `tripwire_triggered` halt; gate co-located on agent and tool definitions via decorators), LangGraph (configurable RetryPolicy on specific nodes for the retry-vs-exit boundary).

**Judge-human alignment measurement:** Raw accuracy fails on imbalanced data; the corpus uses TPR / TNR / Cohen's κ instead (chance-corrected inter-annotator agreement). **Quantitative alignment floor for trusting an LLM-as-judge: TPR ≥ 0.9, TNR ≥ 0.85, κ ≥ 0.7** against expert ground-truth labels on a held-out test set.

**Judge-base-model collision (self-enhancement bias):** Zheng et al. find significant bias when judge and target share base model — GPT-4 favored own answers by 10%; Claude-v1 by 25%. Academic recommendation: cross-family judge mitigation. Pragmatic engineering view per Husain: same-family judge is acceptable if the strict TPR/TNR/κ calibration floor passes against human ground-truth. Flagged in research; resolved/bypassed in production by alignment-floor discipline.

**Meta-eval (evaluating the evaluator):** Criteria drift — humans change their definitions of success after observing real model outputs — means validators are not static rules. EvalGen generates candidate grader prompts and selects ones aligning with a human-graded subset; Arize Phoenix and LangSmith treat evaluators as artifacts requiring continuous tuning on a ~100-trace held-out test set. **Treating the validator as ground truth is the failure mode:** Reflexion underperformed baselines on the MBPP benchmark because its unit-test evaluator had a 16.3% false-positive rate, inducing endless token-burning self-correction loops on outputs that were actually valid.

**Permanent tension here:** Production-discipline-from-day-one vs scaffolding-speed. Honest absorption (12-Factor Agents accepts more boilerplate; Anthropic accepts file rituals over infinite context; ICM accepts scaling limits; Anthropic Code Execution with MCP accepts mandatory sandbox tax) vs displacement (frameworks marketing checkpointing as durable execution while shifting deduplication and race-condition burdens to application layer; multi-agent frameworks claiming parallel writes work until Cognition's reality check).

---

## §5. Deployment Surface (local-development, cloud-managed, hybrid)

**Convergence:** Weak. Deployment-surface flexibility is costly to retain. Most harnesses bind tightly to one surface; the few that bridge pay an explicit abstraction tax.

**Cost of flexibility:** The "Brain/Hands/Session" abstraction tax (manually building Anthropic's decoupled architecture: stateless harness + swappable execution sandboxes + externalized append-only event log). Re-implementing distributed coordination across disconnected environments. Operational gap (autoscaling, queue durability, network reliability assumptions have no true local equivalents); flexible harness must maintain a complex deployment matrix with graceful degradation.

**Patterns that enable flexibility (with corpus instances):**

| Pattern | Examples |
|---|---|
| Multi-surface delivery from a single core (P-DS-2) | kilocode, pi-mono (CLI/TUI/VS Code/web/SDK across local + cloud) |
| Three-layer composable SDK | OpenHands (agent logic / interface / sandboxed agent-server; local Docker dev → remote K8s prod) |
| Embedded vs external database gradient | Paperclip (embedded Postgres + Tailscale local; external Postgres prod) |
| Cross-platform meta-skills (P-DS-5) | Trellis (.trellis/ Markdown skeleton fanning to 14 host harnesses) |
| Plugin daemons with runtime modes | Dify (Local subprocess / Debug TCP / Serverless AWS Lambda uniform over HTTP) |

**Patterns that preclude flexibility (with corpus instances):**

| Pattern | Examples |
|---|---|
| Kubernetes-operator-as-harness (P-DS-3 / P-CP-7) | Optio (one long-lived pod per repo); ACP (agents/tools as K8s CRDs) |
| Tmux-as-deployment-fabric (P-DS-9) | openrig (tmux panes orchestrating heterogeneous coding agents; single OS instance only) |
| Proprietary cloud primitives | Cloudflare Durable Objects (locked to Cloudflare isolate model); Bedrock AgentCore (AWS IAM + CloudWatch tightly coupled) |

**Permanent tension located here:** T3 (per-task vs per-company deployment unit; corpus splits hard between transient session pole and enduring organizational primitive pole — see §7).

**F1–F5 trace through the deployment-surface axis:** F1 (multi-LLM commitment) gains flexibility via provider-abstraction layer at the cost of cross-provider context-handoff engineering. F2 (filesystem-as-shared-substrate) gains maximal flexibility (every surface has a filesystem). F3 (durable-execution-as-coordination-spine) loses flexibility if engine-committed too early (DBOS binds Postgres; Temporal requires a cluster); flexibility requires committing to the *pattern* via stateless-reducer principles while deferring the engine choice. F4 (sandbox-isolation-strength-by-trust-level) gains flexibility by making isolation a property of the tool, not the harness. F5 (OS-keychain-at-dev / vault-at-prod) bridges local-to-cloud explicitly, preventing macOS keychain prompts blocking cloud automation and short-lived cloud tokens breaking local dev loops.

**Persona binding strength varies:**

| Binding | Examples |
|---|---|
| Tight (committed) | MS Agent Framework → enterprise (FIPS 140-2, Azure VNet, Entra ID); ICM → solo/small-team (rejects high-concurrency); openrig → solo hacker (tmux deployment fabric) |
| Bridging (cross-persona) | LangGraph/deepagents (single-process SQLite locally → Postgres + LangSmith + async interrupts at enterprise); 12-Factor Agents (stateless reducers + webhooks scaling local → distributed); OpenHands (OSS single-tenant → enterprise multi-tenant + remote Agent Server licensing) |
| Substrate (deferred) | Meta-Harness ONBOARDING.md spans solo→team; pi-mono pi-agent-core "no persona at all"; Kode-Agent "post-human workflows" event-driven design |

---

## §6. F1–F5 Foundational Decisions (cross-axis consolidation)

Per the round 1 chat 4 output, the corpus enumerates F1–F5 as the foundational decisions that gate downstream derivative decisions. The label assignment is from NotebookLM's reading of the harness project's primary research material; reconcile against Cluster 5 V2 / Pattern Reference Catalog v1.0 before treating as canonical.

| ID | Foundational decision | Primary axis | Secondary effects |
|---|---|---|---|
| F1 | Multi-LLM commitment | Action surface (provider abstraction layer) | Operational discipline (cost knob via routing); Information substrate (cross-provider context handoff) |
| F2 | Filesystem-as-shared-substrate | Information substrate | Action surface (Skills); Deployment surface (any-surface portability); Control plane (T1 selection) |
| F3 | Durable-execution-as-coordination-spine | Operational discipline | Control plane (orchestration topology constraints); Information substrate (state ledger tier) |
| F4 | Sandbox-isolation-strength-by-trust-level | Action surface | Operational discipline (security); Deployment surface (microVM availability) |
| F5 | OS-keychain-at-dev / vault-at-prod | Operational discipline (secrets) | Deployment surface (local-cloud bridge) |

**Phase 2 framing implication:** F1, F2, F4, F5 are flexibility-gaining when committed early (corpus-supported). F3 is flexibility-losing if the *engine* (D1) is committed early; flexibility requires committing to the pattern via stateless-reducer discipline while deferring engine choice. The pattern-vs-engine distinction is the load-bearing nuance for Phase 3a.

---

## §7. T1–T4 Permanent Tensions (cross-axis consolidation)

Per Cluster 5 V2 §3, the catalog identifies T1–T4 as permanent tensions — fundamental software engineering tradeoffs applied to LLMs that cannot be eliminated by better models, only deliberately absorbed. Round 1 chat 5 surfaced T1, T2, T4 only.

| ID | Tension | Pole A examples | Pole B examples | Primary axis |
|---|---|---|---|---|
| T1 | Filesystem-as-orchestrator vs framework-orchestration | ICM, Meta-Harness (filesystem coordinator) | deepagents, Dify, VoltAgent (framework graphs) | Control plane + Information substrate |
| T2 | Single-process harness vs multi-process topology | Cline, OpenHands, VoltAgent (single-process) | openrig (tmux multi-process); Optio, ACP (K8s pods/CRDs) | Control plane + Operational discipline |
| T3 | Per-task vs per-company deployment unit | DeerFlow, kilocode, deepagents, OpenHands, Cline, OpenHarness (per-task/session); Optio (per-repo, mid-spectrum) | Paperclip (per-company; embedded Postgres per deployment, per-agent financial hard-stops, governance with rollback) | Deployment surface + Operational discipline |
| T4 | Markdown-spec-driven vs code-driven configuration | Maestro, Trellis, Agency-Agents (markdown definitions) | deepagents, VoltAgent, OpenHands (Python/TypeScript workflows) | Action surface + Information substrate |

**Honest absorption vs displacement (corpus examples):** 12-Factor Agents (accepts more boilerplate for reliability; "more code to write and more setup and glue code" admitted directly). Anthropic (accepts file rituals over infinite context; explicit "compaction isn't sufficient" admission, forcing agents to re-read ground-truth files on every session boot). ICM (accepts scaling limits; "does not work for high-concurrency multi-user systems" stated). Anthropic Code Execution with MCP (98.7% token reduction with explicit "requires a secure execution environment with appropriate sandboxing" admission). Vs displacement: framework checkpointing marketed as durable execution while shifting deduplication burden to application layer; early multi-agent parallel-write claims that Cognition's reality check disproved.

**T3-specific absorption vs displacement:** Paperclip absorbs the per-company pole honestly — accepts the architectural overhead of true multi-tenancy (embedded Postgres per deployment, strict per-agent financial hard-stops, governance with rollback as core mechanism) to guarantee complete data isolation between companies. kilocode absorbs the per-task pole honestly — relies on concurrent git worktrees for session isolation, accepts that this provides fast local orchestration but cannot satisfy enterprise multi-tenancy. **Displacement pattern:** adopting a per-task framework (LangGraph or standard single-process harness) and bolting on multi-tenancy later by tagging database rows with user IDs — this displaces inter-tenant data-leak risk, cross-session financial budget enforcement, and runaway-compute isolation back to the application developer.

---

## §8. Convergence vs Divergence Map

**Strong convergence (Phase 2 and 3a should treat as largely settled):**

- Filesystem-as-shared-substrate (F2)
- Strict-mode tool contracts (action surface)
- HITL as first-class architectural primitive (not an exception)
- Production-grade-from-day-one architectural commitments (the seven items in §4) for harnesses surviving in production
- Failure of "magic" frameworks at 70–80% reliability — the industry pattern is well-documented
- Multi-agent systems for reads/evaluation only; writes single-threaded
- Strict-mode JSON contracts (constrained decoding) as the input gate to deterministic validators

**Weak / no convergence (Phase 2 must illuminate; Phase 3a council deliberation will be deepest here):**

- Topology choice (workload-shaped; five classes in active use)
- Durability tier (split hard by deployment surface and persona)
- Wrap-vs-equip-vs-MCP line (workload-shaped; Skills-vs-MCP boundary actively contradictory in corpus)
- HITL primitive granularity (three tiers; choice is operator-availability-shaped)
- Routing strategy (declarative vs embedding vs LLM-as-router)
- Persona binding strength (tight / bridging / substrate)
- F3 engine choice (Temporal vs DBOS vs LangGraph checkpointing — pattern is settled, engine isn't)

---

## §9. Consolidated Architect's Question Scaffold

Phase 2 persona surfacing must answer the following before Phase 3a council deliberation can produce non-arbitrary foundational ADRs. Questions consolidated from the "Phase 2 questions for the systems architect" closing sections of all 10 chat outputs.

### Persona and operator-availability

1. **What operational persona binds?** Solo developer (zero-infra-overhead, local-first, synchronous HITL, filesystem/SQLite state) / small team (shared workflows, version-controlled prompts, unified gateways, modest infra tax) / enterprise (durable execution, async HITL via webhook/Slack, multi-tenant isolation, RBAC/SSO, OTel, microVM sandbox) — or bridging pattern explicitly?
2. **What is the expected human response SLA on HITL?** Synchronous (<1 minute, blocks process; in-process backed by local SQLite) / asynchronous (>1 minute to multi-day, durable execution + Postgres checkpointing or Temporal mandatory).
3. **What is the operator's approval budget?** Hard caps on human handoffs to prevent agent spam and approval fatigue.
4. **What is the timeout and abandonment policy** for unresponsive humans?

### Workload shape

5. **What is the write-contention of the target workload?** Primarily gathering and synthesizing information (multi-agent topology unlocked) vs actively mutating shared interdependent state like a codebase (single-agent ReAct or read-only sub-agents only).
6. **Can the workload's evaluation criteria be programmatically codified?** If yes, evaluator-optimizer loops are unlocked. If no, iterative loops risk endless hallucination drift.
7. **What is the hard latency budget?** Sustains 15× token amplification and orchestrator-worker fan-out latency, or sub-second user responsiveness required?
8. **Are task boundaries predictable upfront?** Deterministic DAG fits, or does the orchestrator need to invent the decision tree dynamically based on intermediate observations?
9. **How will context degradation be isolated?** If the task exceeds ~35 minutes or requires reading dozens of irrelevant files, sandboxing strategy required.
10. **What is the sub-task predictability and routing distribution?** 80% predictable → static routing to cheap models; highly unpredictable → LLM-as-router latency tax.

### Action surface

11. **30+ external SaaS tools required?** If yes → MCP client + OAuth 2.1 mandatory.
12. **Hundreds of tools requiring dynamic discovery?** If yes → tool_search / Code-execution-with-MCP to defer schema loading (otherwise 150K-token upfront tax); MUST also commit to sandbox.
13. **Untrusted LLM-generated code execution?** If yes → microVM (Firecracker, gVisor) sandbox commitment is foundational, not derivative.
14. **Non-engineers defining workflows?** If yes → Markdown-driven Skill parser (DeerFlow / Trellis pattern) over code-driven tool registries.

### State and durability

15. **Database-backed vs filesystem + git for durable state?** Concurrent agents mutating shared external state → database-backed execution ledger with idempotency keys mandatory.
16. **If database-backed: snapshot checkpointing (LangGraph) or event-sourced replay (Temporal/DBOS)?** Tradeoff is who owns failure detection, lease coordination, determinism constraints.
17. **JIT filesystem retrieval vs RAG vector store?** JIT lowers per-call tokens but hurts cache hit rates due to dynamic message tail; RAG requires indexing infrastructure but benefits stable knowledge corpora.

### Cost ceiling

18. **How static is the tool catalog and system prompt?** Mutating per-session = silent zero-cache penalties at 1.25× write tax. Perfectly static = 90% read discount available.
19. **Can any workload portion tolerate >1 hour latency?** Async background research / ETL → Batch API cuts costs ~50% (stackable to 95% with caching). Synchronous user-facing → Batch API completely off the table.
20. **Does the workload's parallelism actually justify the 15× token cost** of orchestrator-worker, or can it constrain to single serial agent?

### Eval methodology and gating discipline

21. **What is the objective-to-subjective ratio of our success criteria?** Mathematically/syntactically provable success (linters, schemas, type checks) → in-loop deterministic gates. Subjective criteria (tone, architectural soundness, "appropriate" output) → out-of-loop LLM-as-judge pipelines on traces (avoids slowing the runtime).
22. **Who is the "benevolent dictator" for this workload?** Out-of-loop eval requires a single principal domain expert to manually review traces, axially-code failure-mode taxonomies, and resolve annotation conflicts on the holdout set. **If no such role exists in the persona, an out-of-loop LLM judge cannot be reliably built.**
23. **What is the false-positive tolerance for in-loop validators?** A gate failing on valid output triggers costly retry loops (Reflexion-on-MBPP failure mode). Required telemetry: TPR / TNR monitoring on deterministic gates against the alignment floor (TPR ≥ 0.9, TNR ≥ 0.85, κ ≥ 0.7) before token-budget burn becomes structural.

---

## §10. How This Synthesis Loads into Phase 2

The systems architect skill (per its frontmatter description: "surfacing persona, workloads, scale, integration surface, hard constraints, soft preferences") loads this synthesis at Phase 2 entry. Suggested loading discipline:

1. The skill loads §6 (F1–F5), §7 (T1–T4), and §8 (convergence/divergence map) as orientation context.
2. The skill uses §9 (consolidated architect's question scaffold) as the persona-surfacing interview script, sequenced as the operator's persona constraints become clear.
3. The skill loads per-axis sections (§1–§5) on demand when Phase 2 conversation surfaces a specific axis decision needing illumination.

Selective per-decision loading per Project Workflow v1.0 §0 — never bulk-load §1–§9 at once. The synthesis is structured to support partial loads.

---

## Provenance

**Source:** NotebookLM brainstorm rounds 1 (broad sweeps, 5 chat outputs) and 2 (granular drilldowns, 5 chat outputs). Round 1 prompts: persona constraints, filesystem-as-substrate convergence, operational discipline underweighting, decision-surface flexibility cost, three permanent tensions. Round 2 prompts: multi-agent topology vs workload fit (C2.1), HITL primitive design (C2.2), wrap-vs-equip-vs-MCP decomposition (C2.3), state durability tier mapping (C2.4), cost knob mechanics (C2.5).

**Underlying corpus:** NotebookLM project containing the harness engineering project's primary research material (Sessions 1–3, Clusters 1–5 V2, Triaged Source Inventory, Pattern Reference Catalog v1.0) plus 28 supplemental URL-scrape topical compilations (1140 successful scrapes across topics: 01_Anthropic_Claude_Core through 28_Misc_Tools_Resources; manifest in NotebookLM corpus folder).

**Citation discipline applied:** Harness names retained verbatim. NotebookLM internal numeric citations stripped. Label-shaped claims (F1–F5, T1–T4, P-XX-N) retained as quoted; canonical authority is the harness project KB; reconcile before any ADR cites them.

**Confidence cap:** MODERATE. This synthesis is NotebookLM's reading of the corpus, not direct corpus extraction. Specific harness claims should be verified against the actual primary research artifacts before becoming load-bearing in any foundational ADR.

**Path B integration (this revision):** T3 (per-task vs per-company deployment unit) added to §7 table and absorption-vs-displacement paragraph; T3 axis-flag added to §5; eval-methodology content (Husain loop, judge-base-model collision via Zheng et al. self-enhancement bias, alignment floor TPR/TNR/κ thresholds, meta-eval, Reflexion-MBPP false-positive failure mode) added to §4; architect question scaffold extended with three eval-methodology questions in §9 (Q21–Q23). Synthesis is feature-complete for Phase 2 priming.

---

*End of synthesis. File: `Brainstorm_Synthesis_For_Phase_2.md`. Intended destination: harness engineering project KB, loaded by systems architect skill at Phase 2 entry.*
