# The Five-Tier Durability Model for AI Agent State Architectures

The five-tier durability model tracks how agent harnesses persist state, context, and capabilities across turns, sessions, and failures. Across the studied harnesses, the architectural commitments to these tiers vary wildly from local-first filesystem reliance to cloud-native database engines.

## 1. Filesystem Tier

- **Harnesses that use it:** Claude Code, Aider, Interpretable Context Methodology (ICM), Meta-Harness, DeerFlow, kilocode, pi-mono, and Trellis.
- **Harnesses that don't:** Agent Control Plane (ACP), Cloudflare Agents (Durable Objects), and Optio.
- **What's stored:** The filesystem acts as the primary working memory and capability ledger. It stores progressive disclosure skills (e.g., `SKILL.md`), project context (e.g., `CLAUDE.md`, `.kilocode/rules/memory-bank/`), human-readable progress trackers (`claude-progress.txt`), intermediate tool outputs, and configuration skeletons. Meta-Harness even uses the filesystem as an unbounded search space containing source code, scores, and execution traces for outer-loop optimization.

## 2. Git Tier

- **Harnesses that use it:** Claude Code, Aider, and kilocode.
- **Harnesses that don't:** Dify, VoltAgent, deepagents, and 12-Factor Agents.
- **What's stored:** Git serves as the transactional state engine and rollback mechanism for long-running workflows. It stores atomic commits of code changes, updates to structured feature lists (`feature_list.json`), and shadow-repository checkpoints. Aider uses it to separate user edits from agent edits via "dirty commits", while kilocode uses parallel Git worktrees to isolate concurrent sub-agent sessions.

## 3. Checkpoints Tier

- **Harnesses that use it:** LangGraph (and derived harnesses like deepagents), Microsoft Agent Framework, DBOS, Hatchet, and Inngest.
- **Harnesses that don't:** ICM, Meta-Harness, Claude Code, and openrig.
- **What's stored:** Checkpoints store a complete, serialized graph state snapshot captured at specific super-steps. This includes channel values, next nodes to execute, thread IDs for resumption, and "pending writes" (intermediate node outputs not yet committed). They are typically stored in relational or NoSQL databases like SQLite, Postgres, or DynamoDB, allowing for time-travel debugging and human-in-the-loop (HITL) resumption.

## 4. Vector Store (Semantic Memory) Tier

- **Harnesses that use it:** Mem0, Dify, VoltAgent, LlamaIndex, AWS Bedrock AgentCore, and Redis (LangCache).
- **Harnesses that don't:** Claude Code, ICM, Meta-Harness, and single-file agents (SFAs).
- **What's stored:** This tier houses long-term semantic knowledge retrieved via approximate nearest neighbor (ANN) search. It stores document embeddings, semantic facts, user preferences, and cached responses to semantically similar historical queries.

## 5. Ledger (Event Sourced) Tier

- **Harnesses that use it:** Temporal, 12-Factor Agents, Anthropic Managed Agents, Kode-Agent SDK, Maestro, and paperclip.
- **Harnesses that don't:** Basic LangGraph implementations, ICM, and simple SFAs.
- **What's stored:** An immutable, append-only event history. It records every LLM thought, tool execution, human approval, and system command. In durable execution engines like Temporal, this ledger is used to deterministically replay execution state after a crash, substituting cached tool results instead of re-executing non-deterministic side effects. In Maestro, it manifests as JSONL files (`audit.jsonl`, `decisions.jsonl`) capturing command invocations, cost, and duration.

## Convergence and Divergence on Filesystem-as-Substrate

**Where the corpus has converged:** Cluster 5 V2 explicitly notes that **filesystem-as-shared-substrate** is a foundational architectural decision where the field has strongly converged. Harnesses like ICM, Meta-Harness, DeerFlow, pi-mono, Trellis, and kilocode all agree that agent state, intermediate artifacts, and reusable capabilities belong on the filesystem. They coordinate *over* the filesystem rather than replacing it with in-memory graph abstractions. This convergence is heavily driven by Anthropic's documentation of "Code execution with MCP" and progressive-load skills, which shrink massive tool schemas into simple filesystem reads (`grep`/`glob`).

**Where the corpus hasn't converged:** Frameworks built for enterprise multi-tenancy and high-concurrency cloud deployments actively reject the filesystem. The **Agent Control Plane (ACP)** stores agent state inside Kubernetes Custom Resource Definitions (CRDs), **Cloudflare Agents** use embedded SQLite within Durable Objects to achieve zero-idle-cost multi-tenancy, and **Optio** and **paperclip** rely entirely on Postgres/Redis or embedded databases to isolate company data and orchestrate workflows. For these harnesses, the filesystem is a liability that breaks horizontal scaling.

## Phase 2 Decisions for the Systems Architect

Because the studied harnesses split wildly across these durability tiers, the systems architect must illuminate the following decisions in Phase 2 to make their topology non-arbitrary:

1. **Database-Backed vs. Filesystem + Git for Durable State (I3):** Will the harness rely on a centralized database (Postgres/Temporal/DynamoDB) to track workflows and concurrent state, or will it rely on `claude-progress.txt` and atomic Git commits? If multiple concurrent agents need to mutate shared external state, a database-backed execution ledger with idempotency keys is mandatory.
2. **Specific Durable-Execution Substrate (D1):** If database-backed state is chosen, the architect must choose between snapshot-based checkpointing (LangGraph) and event-sourced replay (Temporal/DBOS). LangGraph requires the developer to handle failure detection and lease coordination, while Temporal owns the entire lifecycle but enforces a strict determinism constraint on the application code.
3. **Just-In-Time (JIT) vs. RAG-Dump Retrieval:** Will the harness use a Vector Store tier for semantic search, or rely on JIT filesystem navigation? JIT (using CLI tools to dynamically explore files) lowers per-call token counts but hurts cache hit rates due to a dynamic message tail. RAG-dumping from a vector database requires indexing infrastructure but benefits stable knowledge corpora.
