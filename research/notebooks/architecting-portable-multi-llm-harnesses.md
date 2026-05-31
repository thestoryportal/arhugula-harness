# Architecting Portable Multi-LLM Agent Harnesses

Designing a multi-LLM agent harness for deployment-surface flexibility (local, cloud, and hybrid) requires decoupling the agent's logic from its execution environment, state persistence, and infrastructure.

## The Architectural Cost of Deployment-Surface Flexibility

Compared to committing to a specific surface early, maintaining flexibility imposes significant architectural and operational costs:

- **The "Brain/Hands/Session" Abstraction Tax:** To run anywhere, you must manually build Anthropic's decoupled architecture: a stateless harness (the brain), swappable execution sandboxes (the hands), and an externalized append-only event log (the session). Early commitment to a platform like Bedrock AgentCore or Claude Managed Agents provides this infrastructure out of the box with SLAs.
- **Re-implementing Distributed Coordination:** Flexible harnesses must handle state across disconnected environments (e.g., a developer's laptop and a cloud queue). This prevents you from relying on native cloud orchestration like Kubernetes Custom Resource Definitions (CRDs) for state reconciliation or Cloudflare's zero-idle-cost Durable Objects.
- **Managing the Operational Gap:** Autoscaling, queue durability, and assumed network reliability have no true local equivalents. A flexible harness must maintain a complex deployment matrix, gracefully degrading when cloud services (like managed sandboxes or external databases) are unavailable in a local environment.

## Catalog Patterns That Enable Surface Flexibility

- **Multi-surface delivery from a single core (P-DS-2):** Harnesses like **kilocode** and **pi-mono** build a core engine that can be consumed via multiple clients (CLI, TUI, VS Code extension, web, programmatic SDK) across local and cloud environments.
- **Three-layer composable SDK:** **OpenHands** explicitly separates agent logic, the interface, and the sandboxed agent-server. This permits agents to target a local Docker instance during development and remote Kubernetes clusters in production.
- **Embedded vs. External Database Gradient:** **Paperclip** uses an embedded Postgres database for zero-setup local deployments (with Tailscale presets for LAN access) and swaps to an external Postgres instance for cloud production.
- **Cross-platform meta-skills (P-DS-5):** **Trellis** operates entirely above the deployment surface. It uses a `.trellis/` Markdown skeleton to fan out configuration files to 14 different host harnesses, running wherever the host runs.
- **Plugin daemons with runtime modes:** **Dify** manages plugins via a daemon that explicitly supports Local (subprocess), Debug (TCP), and Serverless (AWS Lambda) runtimes uniformly over HTTP.

## Catalog Patterns That Preclude Surface Flexibility

- **Kubernetes-Operator-as-Harness (P-DS-3 / P-CP-7):** Harnesses like **Optio** (one long-lived pod per repository) and **Agent Control Plane (ACP)** (modeling agents and tools as K8s CRDs) bind execution to cluster-native reconciliation. They fail on local-first surfaces without running heavy Kubernetes infrastructure locally.
- **Tmux-as-deployment-fabric (P-DS-9):** **openrig** relies on tmux panes to orchestrate heterogeneous coding agents. This ties the deployment strictly to a single OS instance and completely fails cloud-native scaling requirements.
- **Proprietary Cloud Primitives:** Workflows built exclusively around **Cloudflare Durable Objects** are locked to Cloudflare's serverless isolate model. Similarly, **Bedrock AgentCore** tightly couples identity (AWS IAM) and observability (CloudWatch) to AWS.

## Flexibility Gains and Losses in Foundational Decisions (F1-F5)

The project's foundational decisions (F1-F5) dictate how flexibility is preserved or restricted before derivative decisions are made:

- **F1. Multi-LLM commitment:** **Gains flexibility.** By requiring a provider-abstraction layer (e.g., LiteLLM or pi-mono's unified API adapters), the harness avoids vendor lock-in to Anthropic or OpenAI, but costs the engineering effort of managing cross-provider context handoffs.
- **F2. Filesystem-as-shared-substrate:** **Gains maximal flexibility.** Every deployment surface has a filesystem. By keeping agent state, intermediate artifacts, and reusable skills in files, the harness remains portable across laptops, containers, and microVMs without requiring a database at initialization.
- **F3. Durable-execution-as-coordination-spine:** **Loses flexibility if committed to a specific substrate too early.** Committing to the *pattern* of durable execution ensures resilience, but the specific engine (D1) must be deferred. For example, DBOS binds you to Postgres, and Temporal requires a complex cluster. To remain flexible, the harness must adopt stateless-reducer principles (Factor 12) while delaying the choice of the runtime engine.
- **F4. Sandbox-isolation-strength-by-trust-level:** **Gains flexibility.** By making isolation a property of the *tool* rather than the *harness*, you can run deterministic data tools locally via language-level sandboxing, while routing untrusted LLM-generated code to cloud-managed Firecracker microVMs (e.g., E2B).
- **F5. OS-keychain-at-dev / vault-at-prod for secrets:** **Gains flexibility.** This decision explicitly bridges the local-to-cloud gap by abstracting secret fetching. It prevents local macOS keychain prompts from blocking automated cloud runs, and prevents short-lived cloud vault tokens from breaking local development loops.
