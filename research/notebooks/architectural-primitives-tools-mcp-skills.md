# Architectural Primitives: Tools, MCP Servers, and Agent Skills

The corpus reveals that the choice between an MCP server, an in-process tool, and a Skill is not a matter of developer preference, but a strict architectural calculation based on process boundaries, trust gradients, context window economics, and authorship.

Here is how the corpus defines the boundaries between these three primitives, how studied harnesses implement them, and the ambiguities that remain.

## 1. In-Process Tools

**Decision Criteria:** High trust, zero network latency, foundational harness capabilities, harness-author ownership.

- **Process Boundary:** None. These tools execute within the same memory space or runtime loop as the agent harness itself.
- **Trust Gradient:** Absolute trust required. Because they lack sandboxing, any vulnerability or prompt-injected payload executed here compromises the host.
- **Corpus Examples:**
  - **Claude Code:** Ships with ~20 base tools (like bash, FileRead, FileEdit) that are built-in and always active. These form the foundational action surface that allows the agent to interact with its immediate environment.
  - **pi-mono:** Defines built-in tools using TypeBox schemas (read, write, edit, bash) that run directly in the Node.js runtime.

## 2. Model Context Protocol (MCP) Servers

**Decision Criteria:** External state mutation, credential isolation, third-party authorship, cross-platform reuse.

- **Process Boundary:** Strict out-of-process isolation. MCP communicates over STDIO or HTTP/SSE, allowing the server to run in a separate container, microVM (like Firecracker), or remote cloud environment.
- **Trust Gradient:** Zero-trust architecture. MCP servers act as OAuth 2.1 Resource Servers, allowing the harness to execute actions without the LLM ever seeing or possessing the underlying API keys or credentials.
- **Reuse Across Agents:** Solves the "N×M integration problem." A tool written as an MCP server can be used instantly by Claude Desktop, VS Code, Dify, and Goose without custom adapter code.
- **Corpus Examples:**
  - **Goose (AAIF):** Uses an "MCP-native extension model." It explicitly abandons in-process plugins entirely, loading all external capabilities as MCP servers.
  - **Dify:** Connects to any MCP server as a client, standardizing how its visual workflows access third-party SaaS platforms like GitHub or Slack.
  - **openrig:** Exposes 17 tools via MCP so that heterogeneous agents (Claude Code + Codex) can self-manage their shared tmux topology.

## 3. Agent Skills

**Decision Criteria:** Domain-expert authorship, procedural workflows, progressive context disclosure.

- **Process Boundary:** Executed via the harness's existing code-execution or bash tools. A Skill is just a folder containing a `SKILL.md` file and optional scripts.
- **Context Economics:** Skills use "progressive disclosure" (discovery → activation → execution). The agent loads a 100-token metadata description upfront, expanding the full Markdown workflow or executing Python scripts only when triggered.
- **Third-Party Authorship:** Designed for non-technical domain experts (e.g., product managers or legal reviewers) to author plain-English workflows without needing to write APIs or run servers.
- **Corpus Examples:**
  - **DeerFlow:** Uses progressive-load Markdown skills (`SKILL.md`) discovered recursively, allowing the agent to self-evolve its capabilities after complex tasks.
  - **Trellis:** Operates as a "meta-skill," distributing persona and workflow logic across 14 different host harnesses via `.trellis/` Markdown skeletons.

## Contradictions and Thin Evidence in the Corpus

**The Blurry Boundary Between Skills and MCP:** The corpus states that "Skills can complement MCP servers," but provides contradictory evidence on where the dividing line actually sits. Anthropic's "Code Execution with MCP" proposes exposing MCP servers as TypeScript files in a directory that the agent explores and executes dynamically. Mechanically, this makes an MCP server look and act exactly like a Skill (a script in a folder executed via bash). The corpus notes that the community is divided on this overlap: some developers argue that Skills can entirely subsume MCP via single-tool wrappers, while others argue MCP should strictly be for API capabilities and Skills for procedural knowledge.

## Undeferred Action-Surface Decisions for Phase 2

While the user persona and exact deployment surface are deferred, **the "wrap/equip/MCP line" dictates the harness's core infrastructure and must be decided now based on workload shape:**

1. **Will the workload require integrating with 30+ external SaaS tools?** If yes, the harness *must* implement an MCP client and an OAuth 2.1 authorization flow to prevent API keys from bloating the prompt and leaking to the LLM.
2. **Will the workload require dynamic tool discovery to survive context rot?** If the workload needs hundreds of tools, the harness must support "Tool Search" or "Code execution with MCP" to defer loading schemas, which prevents a 150,000-token upfront context tax.
3. **Does the workload require executing untrusted, LLM-generated code?** If the harness allows Skills with bundled scripts or CodeAct loops, you cannot rely on in-process tools. You *must* commit to a rigid sandbox boundary (e.g., Firecracker microVMs or gVisor) as a foundational harness primitive.
4. **Will non-engineers define the agent's workflows?** If domain experts are dictating business logic, the harness must support a Markdown-driven Skill parser (like DeerFlow or Trellis) rather than relying exclusively on code-driven tool registries.
