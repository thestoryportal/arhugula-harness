# Spec Layer: Tools Integration

The specifications for the custom multi-LLM agent harness implement **tools integration** as a highly governed, secure, and context-optimized architecture. Rather than treating tools as simple, ad-hoc API functions, the harness manages them through a strictly typed and sandboxed contract layer.

The integration is implemented through **six core architectural pillars**:

### 1. The Model Context Protocol (MCP) Substrate
The harness standardizes on the **Model Context Protocol (MCP)** as its universal, cross-vendor wire protocol [226, 364]. Tools, resources, and prompts are loaded as out-of-process MCP servers rather than inside the main harness process [226, 364].
*   **Transport-Level Security Floors**: Because the local `STDIO` transport lacks protocol-level authentication (relying on environment variables) [392, 564], the specifications mandate that any STDIO-based tool invocation must be isolated to a **`tier-3-microvm` minimum** [392, 564].
*   **Remote MCP & OAuth 2.1**: Remote `Streamable HTTP+SSE` transports are integrated under a structured trust-level taxonomy [564]. For Level 2 and Level 3 trust, servers must act as **OAuth 2.1 Resource Servers** (implementing PKCE and RFC 8707 Resource Indicators [392, 406]). This structurally prohibits token-passthrough exploits [406].
*   **Poisoning & Rug-Pull Protection**: To defend against malicious tool descriptions or output-injected attacks, every registered MCP primitive carries a content-addressable hash (`mcp.primitive.signature.sha256` [575]). This signature acts as an audit gate to verify that the tool's behavior has not mutated since its initial design-time audit [362].

### 2. The Progressive-Disclosure Skills System
For packaging higher-level procedural workflows, the harness implements the **`agentskills.io` open standard** [366, 421].
*   **Directory-Based Skills**: A Skill is defined as a directory containing a `SKILL.md` file (which declares required YAML frontmatter: `name` and `description` [366, 369]) along with optional `scripts/`, `references/`, and `assets/` subdirectories [366, 369].
*   **Three-Level Progressive Disclosure**: To prevent loading massive system instructions upfront, Skills are loaded dynamically on an as-needed basis [366, 567]:
    1.  **Metadata Layer (~100 tokens)**: The frontmatter metadata [369] is always loaded in the tool description to allow the model to discover the capability.
    2.  **Body Layer (<5,000 tokens)**: The full `SKILL.md` instruction set [366, 369] is loaded only when the model triggers the Skill.
    3.  **File Layer (Unbounded)**: Associated scripts or reference files are read on-demand by the model via local filesystem tools [366, 369].

### 3. Context-Optimized Scaling (Avoiding "Context Bloat")
To scale past the 30–50 tool limit where LLM tool-selection accuracy traditionally degrades [370], the harness leverages two advanced context-relief mechanisms:
*   **The Tool Search Tool**: Under the `defer_loading: true` flag [370], tools are advertised to the model by name only. When the model needs a capability, it invokes a search tool that dynamically retrieves the full parameter definitions on-demand, **slashing tool-definition context overhead by ~85%** [370].
*   **Code-Execution-with-MCP (MCP-as-Code)**: Instead of exposing dozens of independent tool schemas directly to the LLM API, the harness exposes MCP servers as standard files inside a virtual directory (e.g., `./servers/google-drive/getDocument.ts`) [367, 428]. The model navigates this tree, writes a TypeScript/Python script to compose and execute the exact operations it needs, and runs it locally [367, 428]. All intermediate data is contained inside the execution environment, reducing a typical 150,000-token multi-stage transfer down to a **~2,000-token code payload** [367, 428].

### 4. Graduated Sandbox Isolation Tiers
To execute untrusted model-generated code safely, the Action Surface defines a **four-tier sandbox-isolation set** (`C-AS-01` [545, 546]):
1.  **`tier-1-process`**: Language-level + filesystem ACLs for read-only or local deterministic tools [546].
2.  **`tier-2-container`**: OS-level seccomp/bubblewrap or macOS Seatbelt isolation for local file mutations [546].
3.  **`tier-3-microvm`**: gVisor or shared-kernel containerization for external-reversible tools (and the baseline for STDIO MCP servers) [546, 559].
4.  **`tier-4-full-vm`**: Hardware-virtualized microVMs (e.g., Firecracker) or isolated, egress-restricted full VMs [546, 559].

*   **The `max()` Composition Formula**: When a tool is invoked, its runtime isolation is resolved dynamically [420, 547]:
    $$	ext{assigned\_tier} = \max(	ext{tool.minimum\_tier}, 	ext{blast\_radius\_floor}, 	ext{mcp\_server\_trust\_floor}, 	ext{operator\_policy\_floor}, 	ext{sandbox\_tier\_floor})$$
    For example, a tool might declare a `minimum_tier` of Tier 2, but if it executes **LLM-generated code** or binds to an **untrusted remote MCP server**, the formula unconditionally escalates the runtime execution to a **`tier-4-full-vm`** [546, 559].

### 5. Tool-Call Rewriting and Human-in-the-Loop Gating
When a tool invocation represents a high-risk operation, the harness interceptor evaluates the **5-axis multiplicative gate-level rule** (`C-CP-19` / `C-AS-12` [590]).
*   **The Autonomy Gate**: If the resolved gate-level is `ask`, the harness halts direct execution and **rewrites** the tool call into an interactive human-mediated counterpart [567, 570]:
    *   `request_human_input(prompt, options)`: Synchronous blocking for local interactive workflows [686].
    *   `await_human_approval(action, context, channel)`: Durable asynchronous queues (e.g., Slack/Email via webhooks) for long-lived team operations [686].
    *   `escalate_to_human(severity, summary, retry_history)`: Triggered automatically upon retry-budget exhaustion [686].

### 6. Observability and Telemetry
To monitor non-deterministic tool use, the Operational Discipline axis ingests specialized OTel-compliant telemetry across three dedicated namespaces (`C-AS-14` [572]):
*   **`mcp.*`** [575]: Captures `mcp.server.name`, `mcp.server.trust_tier`, the `mcp.primitive.signature.sha256` for supply-chain verification, and transport metadata.
*   **`skill.*`** [576]: Tracks the active `skill.id`, `skill.version_sha` (the git content hash for replay determinism), and `skill.body_tokens` for granular cost attribution.
*   **`sandbox.*`** [584]: Emits `sandbox.tier`, `sandbox.tech` (e.g., Firecracker vs. gVisor), and `sandbox.fail.class` in the event of an isolation breach.
