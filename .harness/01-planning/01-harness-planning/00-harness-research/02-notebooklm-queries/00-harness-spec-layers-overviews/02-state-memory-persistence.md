# Spec Layer: State Memory Persistence

The specifications implement **state memory persistence** in the custom multi-LLM agent harness through a tightly integrated, cross-cutting durability framework. This architecture ensures that the system is completely resilient to process crashes, capable of time-travel debugging, and audit-compliant while keeping the active context window clean.

### 1. The Filesystem and Git Substrate (The Dual-Mode State Record)
The harness commits to the **filesystem as the primary durable substrate** for all agent state, history, and coordination [448]. The **Combined Git Tier** manages this filesystem through a **dual-mode state-record model** [421, 751] consisting of:
*   **A coarse-grained ledger**: The Git commit stream itself, where commit messages and git history track high-level transitions [751].
*   **A fine-grained ledger**: An append-only JSONL event ledger file stored at a workflow-canonical filesystem path [751].

To manage context and memory overhead, state is structured across **five distinct artifact layers** (`C-IS-02` [747, 748]):
*   **`working`**: Bounded to the local filesystem; survives only a single inference call within a run [748].
*   **`episodic`**: Captures per-run history and in-flight conversation; survives multiple inference calls and is rehydrated via durable engine replay on crash [748].
*   **`semantic`**: Stores cross-run knowledge and learned facts; persists on the filesystem and Git to carry forward across future runs [748].
*   **`procedural`**: Contains workflow-class procedural rules (such as YAML-frontmatter Skills, prompts, and the routing manifest); persists across both runs and workflow versions [748].
*   **`durable`**: Comprises the append-only state-ledger, JSONL event ledger, and audit ledger; persists across terminations, crashes, and recoveries with cryptographic hash-chain verification [748].

### 2. The Canonical State-Ledger and Write-Ahead Log (WAL)
Every meaningful agent step or transaction writes to a **State-Ledger** [751]. This ledger enforces a strict **six-field record signature** (`C-IS-05` [754, 755]) for its entries:
*   `action_id`: Unique, harness-generated identifier [755].
*   `idempotency_key`: The harness-canonical join key used to unify engine history, sandbox violations, audit records, and span metrics across runs [755, 758, 760].
*   `actor`: The specific agent, sub-agent, or operator originating the action [755].
*   `response_hash`: A SHA-256 digest of the canonical-JSON payload [755].
*   `timestamp`: Monotonically non-decreasing wall-clock instant [755].
*   `prior_event_hash`: The cryptographic link pointing to the preceding entry's hash [755].

To handle this ledger, the specifications construct a **Read/Write Seam Contract**:
*   **The C3-Pole (Write) Contract**: Persists entries as indexable, line-by-line JSONL [758]. It is strictly append-only, structured, JSON-encoded (not Markdown) [321, 758], idempotent, and immediately computes the `prior_event_hash` to keep the integrity chain unbroken [758].
*   **The C2-Pole (Read) Contract**: Discourages bulk data dumps [758]. Reads are selective, bounded, and mediated through specialized navigation primitives (as Skills or tools) [758]. These are injected only into the prompt's *dynamic suffix* (after the prompt-caching breakpoints) to prevent cache invalidation [321, 758].

### 3. Hash-Chain Integrity and Cryptographic Auditing
To satisfy compliance-readiness and prevent tampering, the event ledger is secured with **Hash-Chain Integrity** [757]:
*   **Write-Time Chaining**: Prior to writing, each entry is canonicalized to a deterministic byte representation using the RFC 8785 JSON Canonicalization Scheme (JCS) [555, 757], hashed via SHA-256 [757], and chained sequentially to its ancestor's hash.
*   **Verification**: The downstream operator can mathematically verify the ledger's integrity post-termination by traversing the `prior_event_hash` chain [757].
*   **Tier-Aware Cryptographic Audits**: The audit ledger composes with this state-ledger structure but adjusts its cryptographic shape to the deployment's **persona-tier** (`C-CP-20` [697]):
    *   *Solo-developer*: Written to an append-only local SQLite database [697].
    *   *Team-binding*: Hash-chained locally on SQLite [697].
    *   *Multi-tenant-compliance*: Hash-chained on partitioned SQLite and cryptographically signed on every entry using an asymmetric key (using `ed25519`, `ecdsa-p256`, or `rsa-pss-2048`) fetched from a vault-configured secrets abstraction [697].
*   **Structure-Not-Content Principle**: If the tool call accesses sensitive credentials or PII, the ledger writes only a cryptographic fingerprint (`outputs_hash` [550, 555]) to avoid storing raw secret content.

### 4. Workload-Class-Opt-In Durable Primitives
Workflows can declaratively opt into advanced Git-backed persistence mechanisms via the manifest:
*   **Shadow-Git Checkpointing**: Creates isolated snapshots of the filesystem using a shadow-repository pattern [751] (similar to Cline or Roo Code).
    *   *Cadence*: Can be configured to snapshot `per_step`, `per_tool_call`, `per_significant_change`, or via `per_explicit_marker` [762].
    *   *Rollback*: Restores the workflow’s files atomically and coherently, writing a new state-ledger record to document the reversion [751].
*   **Git Worktree Isolation**: Spawns isolated, concurrent file workspaces for parallel sibling sub-agents [751, 765].
    *   Each sibling agent is given a dedicated `git worktree` directory pointing to the same underlying `.git` storage [765].
    *   Provides read-read and read-write non-interference between parallel agents [765].
    *   Worktrees are dynamically deleted (`git worktree remove`) and reclaimed upon sub-agent termination [765].

### 5. The Durable Execution and Coordination Spine
To ensure deterministic execution across restarts, the Control Plane defines a **Five-Element Engine-Class Taxonomy** [654]:
1.  **`event-sourced-replay`**: Engine-native (e.g., Temporal). Replays steps from a durable event history, caching completed activity outputs to skip redundant I/O [654].
2.  **`save-point-checkpoint`**: Application-native (e.g., LangGraph). Saves state snapshots per super-step using SQLite, Postgres, or DynamoDB checkpointers [654].
3.  **`pure-pattern-no-engine`**: Harness-driven. Manages durability directly over the F2 filesystem-journal and state-ledger [654].
4.  **`reconciler-loop`**: Kubernetes-native. Persists agent state as Custom Resources reconciled in `etcd` [654].
5.  **`WAL-segment`**: Segment-log with per-segment resumption [654].

Regardless of the engine, the system preserves a **durable capability floor** [608]. Upon resuming from a crash or pause, the engine emits a `workflow.resumption` event carrying a `resumption.kind` attribute (e.g., `engine_replay`, `save_point_resume`, `journal_resume` [657]) to guarantee that already-completed tool calls are bypassed and resolved from the F2 state-ledger rather than re-executed [657].

### 6. Client-Side Memory Tools and the Files API
For long-horizon agentic interactions, the harness integrates Anthropic-specific storage primitives:
*   **Files API** (`files-api-2025-04-14` beta [669, 674]): Allows uploading workspace-scoped file assets. The agent can reference large datasets via a `file_id` in its message context, bypassing the need to bloat the main conversational prompt [567, 578].
*   **Memory Tool** (`memory_20250818` [567, 579]): Exposes a client-side `/memories` directory to the agent [567, 579]. The model uses view, create, and search tools to read and write cross-session notes [579]. The harness implements the physical backend [571].
*   **Compaction Exclusion**: Memory tools are explicitly excluded from server-side context editing and compaction (such as `clear_tool_uses` [567, 579]). This ensures that when the context window is pruned, the model is instructed to write all unresolved bugs, todo lists, and open constraints to a durable, out-of-context file (like `NOTES.md` or `todo.md`) so that they are never summarized away.
