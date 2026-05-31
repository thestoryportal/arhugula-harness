# Architectural Personas in AI Agent Harness Design

The corpus reveals that agent harness architectures are rarely persona-neutral in practice; instead, technical choices around state management, execution durability, and human-in-the-loop (HITL) synchrony naturally constrain harnesses to specific operational personas.

## Implicit Personas and Revealed Constraints

### 1. The Solo Developer

- **Constraints:** Demands zero-infrastructure overhead, local-first execution, synchronous/interactive HITL (prompts via CLI or IDE), and state managed via the filesystem or local SQLite rather than external databases.
- **Harness Fits:**
  - **Cline / Roo Code:** Tightly integrated into the IDE as an extension, utilizing a synchronous plan/act duality and local Git checkpoints for state.
  - **crush:** Delivered as a single compiled Go binary for terminal-native interaction with configurable local project paths.
  - **disler (Single-File Agents):** Optimizes for extreme simplicity, packing single-purpose agents into isolated Python files with inline dependencies.
  - **openrig:** Uses tmux panes as the underlying orchestration deployment fabric, which strictly bounds it to developer-owned hardware and single-operator environments.

### 2. The Small Team

- **Constraints:** Requires shared workflows, version-controlled prompts, collaborative debugging, and unified gateways for API routing, but cannot sustain the operational tax of managing Kubernetes clusters or complex durable execution engines.
- **Harness Fits:**
  - **Archon:** Treats workflows as YAML Directed Acyclic Graphs (DAGs) checked into the repository, establishing shared team artifacts ("like what Dockerfiles did for infrastructure").
  - **Trellis:** Enforces a `.trellis/` Markdown-spec-driven directory layout across the team, providing shared progressive context and developer journals without forcing a specific host platform.
  - **DeerFlow:** Provides a batteries-included setup (Docker Compose, SQLite/local sandbox) with a unified gateway and Markdown-based skills, balancing collaborative features with low infrastructure demands.
  - **Dify / VoltAgent:** Provide visual workflow canvases, plugin daemons, and separate observability consoles (VoltOps) that teams can share for debugging and strategy refinement.

### 3. The Enterprise

- **Constraints:** Mandates durable execution (to survive process crashes in multi-day workflows), asynchronous HITL (escalation queues via webhook/Slack), multi-tenant data isolation, strict RBAC/SSO (Entra ID), OpenTelemetry (OTel) observability, and microVM sandboxing (Firecracker/Kata).
- **Harness Fits:**
  - **Microsoft Agent Framework:** Imposes heavy enterprise constraints, including FIPS 140-2 compliance, Azure VNet support, Entra ID authentication, and explicit durable state.
  - **Agent Control Plane (ACP):** Implements agents as Kubernetes Custom Resources (CRDs) with reconciliation controllers and durable async/await at the infrastructure layer.
  - **Paperclip:** Models the deployment unit as a "company" with multi-tenant data isolation, strict per-agent financial budgets (hard stops), and governance with rollback.
  - **Optio:** Deploys one long-lived Kubernetes pod per repository, utilizing AES-256-GCM secret encryption and an auto-resume reconciler.

## Persona Bindings and Boundary Mapping

### Tight Bindings (Committed to a Single Persona)

- **Microsoft Agent Framework** binds almost exclusively to the enterprise. The corpus explicitly categorizes it as a "poor fit" for solo developers building simple agents due to its setup overhead and Azure-centric defaults.
- **ICM (Interpretable Context Methodology)** explicitly rejects enterprise concurrency. The paper states it "does not work for... high-concurrency multi-user systems" and requires a single operator or small team manually reviewing outputs.
- **openrig** binds to the solo hacker. Using tmux as a deployment fabric creates an unscalable local-only environment that degrades if applied to multi-user or cloud constraints.

### Overlapping / Bridging Personas

- **LangGraph / deepagents:** Can scale across all three. A solo developer can run it in a single process with an in-memory or SQLite checkpointer; an enterprise can deploy it over Postgres with LangSmith tracing and asynchronous interrupts.
- **12-Factor Agents:** The methodology bridges team and enterprise personas by arguing that agents are "mostly software" and should utilize standard stateless reducers, webhooks for human contact, and unified event states that scale from local scripts to distributed cloud deployments.
- **OpenHands:** Straddles the solo/enterprise boundary via licensing and architecture. The OSS version assumes a single-tenant local-first deployment, while multi-tenant isolation requires a separate enterprise license and remote Agent Server configurations.

### Ambiguity and Deferred Commitment

Where harnesses exhibit persona ambiguity, it often reveals a deliberate architectural choice to act as a **substrate** rather than an opinionated product:

- **Meta-Harness:** Automates the search loop for finding optimal harnesses. Its `ONBOARDING.md` spans solo to team contexts, revealing that the optimization algorithm fundamentally avoids committing to who is operating it.
- **pi-mono (earendil-works/pi):** Functions as a unified API and substrate library. While its TUI and pi-coding-agent hint at a solo developer, its core (`pi-agent-core`) ships with "no persona at all" and leaves persona injection entirely to the implementer.
- **Kode-Agent:** Frames its architecture around "post-human workflows" and a "Progress / Control / Monitor channel split." By explicitly designing for events rather than user interfaces, it avoids assigning a persona to the human operator, treating them merely as another control channel.
