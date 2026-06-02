# The Agentic Engineering SDLC

## Application of the Canonical SDLC to Agent-Augmented and Agent-Native Software Development

> **Baseline.** This document is a delta against the 8-phase canonical SDLC defined in `sdlc-research.md`: Phase 1 Initiation/Conception → Phase 2 Requirements → Phase 3 Architecture & Design → Phase 4 Implementation/Construction → Phase 5 Verification & Validation → Phase 6 Release & Deployment → Phase 7 Operations & Maintenance → Phase 8 Retirement/Decommissioning, with cross-cutting concerns (PM, Risk, CM, QA, Security, Compliance, Documentation, Measurement, Supplier/SOUP) running across all phases under Waterfall, V-Model, Iterative, Spiral, Scrum, Kanban, SAFe, DevOps, and regulated lifecycles (FDA GPSV, IEC 62304, DO-178C, ISO 26262). Phase numbering, artifact names, and cross-cutting taxonomy from that document are retained verbatim.
> **Confidence taxonomy.** `[HIGH]`, `[MODERATE]`, `[VARIES: …]`, `[EMERGING]`, `[CONTESTED: A vs B]`, `[CONDITIONAL: …]`, `[uncertain]` — applied per claim.

---

## 0. Agentic SDLC Overview

### 0.0 Definitions (used throughout)

- **Agent** — an LLM operating tools in a loop with environmental feedback, dynamically directing its own process (Schluntz & Zhang, "Building Effective Agents," Anthropic, Dec 19 2024). [HIGH]
- **Workflow / agentic system** — LLM(s) and tools orchestrated through predefined code paths; the parent term that subsumes "agents" (Anthropic, Dec 2024). [HIGH]
- **Augmented LLM** — an LLM enhanced with retrieval, tools, and memory; the foundational building block of agentic systems (Anthropic, Dec 2024; Willison summary, Dec 20 2024). [HIGH]
- **Agent-assisted** — human leads, agent is a tool (Tier 0–1).
- **Agent-augmented** — human supervises, agent owns subtasks (Tier 2–3).
- **Agent-orchestrated** — multi-agent systems with human approval gates (Tier 4).
- **Agent-native** — agents own the lifecycle, human reviews (Tier 5–6).
- **Multi-agent system** — multiple LLMs with their own tools/contexts coordinating, typically orchestrator-worker (Anthropic, "How we built our multi-agent research system," June 13 2025). [HIGH]

### 0.1 Phase-flow with agent participation, HITL checkpoints, and net-new feedback loops

```
                                CANONICAL SDLC PHASES (sdlc-research.md)
   ┌─────────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐
   │ Ph.1    │ Ph.2    │ Ph.3    │ Ph.4    │ Ph.5    │ Ph.6    │ Ph.7    │ Ph.8    │
   │ Init    │ Req'ts  │ Arch    │ Impl    │ V&V     │ Release │ Ops/Mnt │ Retire  │
   └────┬────┴────┬────┴────┬────┴────┬────┴────┬────┴────┬────┴────┬────┴────┬────┘
        │         │         │         │         │         │         │         │
   ┌────▼─────────▼─────────▼─────────▼─────────▼─────────▼─────────▼─────────▼────┐
   │                       AGENT PARTICIPATION SURFACE                              │
   │  ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    │
   │  │spec │    │spec │    │ADR  │    │plan │    │eval │    │canar│    │trace│    │
   │  │assst│    │gen  │    │draft│    │mode │    │run  │    │y rev│    │triag│    │
   │  └──┬──┘    └──┬──┘    └──┬──┘    └──┬──┘    └──┬──┘    └──┬──┘    └──┬──┘    │
   │     │HITL      │HITL      │HITL      │HITL gate │HITL eval │HITL go/  │HITL    │
   │     │approve   │approve   │approve   │+autonomy │triage    │no-go     │rollback│
   │     ▼          ▼          ▼          ▼ bound    ▼          ▼          ▼        │
   └──────────────────────────────────────────────────────────────────────────────┘
        ▲          ▲          ▲          ▲          ▲          ▲          ▲
        │          │          │          │          │          │          │
   ┌────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴────┐
   │              NET-NEW AGENTIC FEEDBACK LOOPS (continuous)                  │
   │  ◀── Eval-failure loop (LLM-judge / golden-trace regressions)             │
   │  ◀── Prompt-regression loop (prompt-diff CI on eval suite)                │
   │  ◀── Trajectory-anomaly loop (OTel GenAI span anomalies → SRE)            │
   │  ◀── Context-drift loop (CLAUDE.md / AGENTS.md staleness alarms)          │
   │  ◀── Tool-misuse loop (OWASP Agentic ASI signals → guardrail update)      │
   └───────────────────────────────────────────────────────────────────────────┘
```

The diagram preserves the canonical 8-phase ordering. Each phase gains an *agent-participation point* and an explicit *human-in-the-loop (HITL) checkpoint*. Four feedback loops are net-new and run continuously across all phases: eval failures, prompt regressions, trajectory anomalies, and tool-misuse signals (per Husain "Your AI Product Needs Evals," 2024; Anthropic engineering, June 2025; OpenTelemetry GenAI semconv 1.37+, 2025; OWASP ASI 2025).

### 0.2 Agentic Engineering Tier Definitions

| Tier | Name | Autonomy | Primary Tools/Frameworks (representative) | Owner of canonical phases | Governance posture | Project class |
|------|------|----------|------------------------------------------|---------------------------|-------------------|---------------|
| 0 | Code-completion | Suggests tokens; human accepts each | GitHub Copilot autocomplete, Tabnine, Amazon Q inline | Human owns all 8 phases | Standard SDLC governance; AI use disclosed | Solo dev, scripts, internal tools |
| 1 | Conversational agent | Chat-driven edits; human reviews diffs | Cursor (chat), Claude Code interactive, Continue, Copilot Chat | Human owns Ph.1–8; agent assists Ph.2–5 | Add prompt logging; treat agent as a SOUP-like supplier | Feature work, refactors, tests |
| 2 | Autonomous coding agent | Plan → execute → verify within a session | Claude Code plan/agent mode, Aider, Cline, Codex CLI | Human owns Ph.1, 6, 8; agent leads Ph.4–5 under HITL | Add eval gate, prompt CM, autonomy bounds | Bug fixes, well-scoped issues |
| 3 | Team with shared agent infra | Shared CLAUDE.md/AGENTS.md, prompt registry, eval CI | Cursor + GitHub Actions evals, Claude Code skills, LangSmith/Langfuse, MCP servers | Team owns Ph.1–3, 6–8; agents own Ph.4–5 with team review | Prompt versioning + AI BOM + agent observability | Mid-size product teams |
| 4 | Multi-agent build subsystem | Orchestrator-worker agents in pipeline | LangGraph, AutoGen (v0.4), CrewAI, OpenAI Agents SDK, Semantic Kernel | Humans own Ph.1–3, 8; agent system owns Ph.4–5; co-owned Ph.6–7 | NIST AI RMF Govern/Map/Measure/Manage; eval-as-CI; OWASP Agentic ASI mapping | Research, ETL, content, large refactors |
| 5 | Agent-native engineering | Agent owns ticket → PR; human reviews | Devin (Cognition), Codex cloud agents, GitHub Copilot Workspace, Claude Code headless | Agent owns Ph.2 detailed reqs, Ph.3 design, Ph.4–5; human owns Ph.1, Ph.6 release decision, Ph.8 | ISO/IEC 42001 AIMS; signed AI BOM; trajectory archival | Backlog burn-down, modernization |
| 6 | Agent-orchestrated workflow product | Agents do the work the product sells | Production multi-agent systems (Anthropic Research, Claude Code subagents, customer-deployed CrewAI/LangGraph) | Agents own runtime Ph.4–5–7; humans own Ph.1–3, 6, 8 governance | EU AI Act high-risk obligations where applicable; full RMF + 42001 + OWASP; on-call agent-SRE | Customer-facing autonomous products |

Tier delineation derives from Anthropic ("Building Effective Agents" Dec 2024, "Multi-agent research" June 2025), OpenAI ("A Practical Guide to Building Agents" Apr 2025), Cognition ("Don't Build Multi-Agents" June 12 2025), and OWASP GenAI ASI documents 2025. [HIGH]

### 0.3 Frameworks and Tools Comparison Matrix

| Framework / Tool | Tiers supported | Primary agent pattern(s) | Primary artifacts | Governance features | Observability | MCP support |
|------------------|-----------------|--------------------------|-------------------|--------------------|---------------|-------------|
| GitHub Copilot (inline + Chat) | 0–1 | Augmented LLM; chat | Inline suggestions, chat transcripts | Org policy, content exclusions | GitHub audit log | Indirect via VS Code |
| Cursor | 1–3 | Conversational, agent mode, "Spec" | `.cursorrules` / `.cursor/rules`, Cursor Spec, chat traces | Team rules, privacy modes | Built-in usage panel; OTel via integrations | Yes (MCP client) |
| Claude Code | 1–5 | Interactive, plan mode, agent mode, sub-agents, headless `-p` | `CLAUDE.md`, sub-agent files, skills, plan docs, session transcripts | Allowed-tools allowlist, hooks, permissions | OTel hooks, Claude Code logs | Yes (first-class) |
| Aider | 2 | Plan-execute, repo-map | Chat history, `.aider*` files, edit-apply diffs | Git-native (every edit a commit) | Local logs | Limited |
| Cline | 2 | Plan/Act mode, browser/computer use | Project rules, task history | Approval modes | Local | Yes |
| Continue | 1–3 | Chat + autocomplete + agent | `config.json`, `.continue/` rules | Self-hosted option | OTel | Yes |
| GitHub Copilot Workspace | 2–3 | Spec → Plan → Implement | Spec doc, plan doc, PR | GitHub policy + Actions | GitHub | Limited |
| Codex CLI / OpenAI Agents SDK | 2–5 | ReAct, manager pattern, handoffs | Agent definitions, tool schemas, traces | Guardrails primitive, structured outputs | OpenAI tracing, OTel GenAI | Yes (March 2025+) |
| Microsoft AutoGen | 4 | Group-chat, conversational MA | Agent configs, group-chat transcripts | Azure governance | OTel GenAI | Via extensions |
| Microsoft Semantic Kernel | 1–4 | Planner, function calling, agent groups | Plugins, planners | Azure AI Content Safety | OTel GenAI | Yes |
| LangChain / LangGraph | 3–6 | Graphs, stateful supervisors, ReAct | Graph definitions, checkpointer state, prompt templates | LangSmith policies | LangSmith + OTel GenAI | Yes |
| CrewAI | 4 | Role-based crews, hierarchical | Agent yaml, task yaml, crew yaml | Validators | OTel via Traceloop | Yes |
| LlamaIndex Agents | 3–4 | Workflow events, ReAct, function | Workflow defs, indexes | — | OTel | Yes |
| Haystack Agents | 3–4 | Pipelines + tool agents | Pipeline yaml | — | OTel | Yes |
| Devin (Cognition) | 5–6 | Single long-running agent + planning sub-component | Plan, terminal/browser session, PRs, Slack thread | Org policies, sandboxed VM | Devin session timeline | Limited |

Sources: vendor documentation pages cited in §16. [HIGH] for tier coverage of Cursor, Claude Code, Aider, AutoGen, LangGraph, CrewAI, OpenAI Agents SDK; [MODERATE] for Devin (closed-source); [VARIES] for "tier supported" because tier capability depends on configuration.

---

## 1. Phase 1 — Initiation / Conception (Delta)

### 1.0 Phase Summary
The canonical purpose — feasibility, business case, scope, stakeholder identification, go/no-go — is unchanged. The agentic delta is twofold: (a) a new **agent-suitability decision** must be made up-front, and (b) **agentic-system-as-product** projects must declare governance posture (NIST AI RMF, ISO/IEC 42001, EU AI Act risk class) before requirements work begins. Anthropic's first directive — "find the simplest solution possible … this might mean not building agentic systems at all" — is a Phase-1 gate. [HIGH]

### 1.1 Step-by-step deltas

| Canonical step | Activity delta | Ownership delta (by tier) | Artifact deltas | New exit criteria |
|----------------|---------------|---------------------------|-----------------|-------------------|
| 1.1 Opportunity / problem framing | Add explicit "do we need an agent at all?" decision; map to Anthropic workflow-vs-agent test | Tiers 0–2: human only. Tiers 3–6: human + agent literature scan | NEW: *Agent-Suitability Decision Record* | Documented justification per Anthropic 2024 criteria |
| 1.2 Business case | Add token/compute cost model (agents ≈ 4× chat tokens; multi-agent ≈ 15×, per Anthropic June 2025) | Same | TRANSFORMED: *Business Case* now includes inference-cost section | Cost model approved |
| 1.3 Stakeholder analysis | Add "agent" as non-human stakeholder with capability card | Tiers 3–6 only | NEW: *Agent Capability Card* (initial draft) | Card lists model, autonomy bounds, owned tools |
| 1.4 Scope / charter | Add autonomy-bounds statement and HITL checkpoint plan | Tiers 2–6 | TRANSFORMED: *Project Charter* gains autonomy section | Autonomy boundaries signed by accountable owner |
| 1.5 Initial risk register | Pull from OWASP LLM Top 10 (2025) and OWASP Agentic ASI (Dec 2025); map to NIST AI RMF 600-1 risks | All tiers building agentic features | NEW: *Agent Threat Model — Initial* | Top-10 mapped; high-risk EU AI Act check done |
| 1.6 Compliance class | Determine if EU AI Act high-risk, ISO/IEC 42001 AIMS scope, sectoral overlay | Tiers 3–6 | NEW: *AI Compliance Class Decision* | Decision logged |

### 1.Z Phase 1 Artifact Catalog

| Artifact | Canonical equivalent | Purpose | Format | Owner | Audience | Lifecycle | Tiers | Conf. | Citation |
|----------|----------------------|---------|--------|-------|----------|-----------|-------|-------|----------|
| Agent-Suitability Decision Record | net-new | Justify (or decline) building an agentic system | Markdown / ADR-style | Tech lead | Steering, eng, security | Versioned in repo | 1–6 | [HIGH] | Anthropic, Dec 2024 |
| Agent Capability Card (v0) | net-new (cf. Mitchell et al. Model Cards) | Describe the proposed agent's role, model, tools, autonomy | Markdown | Product + Eng | Org-wide | Living | 3–6 | [MODERATE] | Mitchell et al., 2019 (model cards); generalized in NIST AI RMF Map |
| Initial AI BOM placeholder | SBOM | Inventory of model/data/prompt/tool components anticipated | SPDX 3.0 AI profile / CycloneDX 1.6 ML-BOM | SecOps + Eng | Security, supply-chain | Living | 3–6 | [HIGH] | SPDX 3.0.1 AI profile; Linux Foundation AI-BOM report |
| AI Compliance Class Decision | TRANSFORMED Compliance plan | Bind project to NIST RMF / ISO 42001 / EU AI Act class | Memo | GRC | Steering | One-time | 3–6 | [HIGH] | NIST AI 600-1; ISO/IEC 42001:2023; EU AI Act |

---

## 2. Phase 2 — Requirements (Delta)

### 2.0 Phase Summary
SRS, user stories, BDD scenarios, acceptance criteria, and the Requirements Traceability Matrix (RTM) all survive — but in agentic projects each requirement becomes either an **input to the agent** (specification-driven development) or an **eval input**. Hamel Husain's position is foundational: requirements are not initially "evals" but are surfaced through **error analysis** of real outputs; eval-driven development as a strict TDD analog "creates more problems than it solves" except for narrow guardrail constraints (Husain, "Should I practice eval-driven development?", hamel.dev, 2024–2025). [CONTESTED: classical eval-driven development advocacy vs. Husain/Shankar's error-analysis-first approach]

### 2.1 Step-by-step deltas

| Canonical step | Activity delta | Ownership delta | Artifact deltas | Exit criteria |
|----------------|---------------|------------------|-----------------|---------------|
| 2.1 Elicitation | Agents generate clarifying questions, draft user stories from raw notes | Tier 0–1: human elicits; Tier 2+: agent drafts under HITL | TRANSFORMED: *User stories* may be agent-drafted; require human sign-off | Stories signed by PO |
| 2.2 SRS authoring | SRS becomes an *executable specification* readable by agents | Tier 2+: agent authors first draft | TRANSFORMED: SRS in Markdown structured for `CLAUDE.md`/`AGENTS.md` consumption (one-sentence project description, build/test commands, conventions, security gotchas — per HumanLayer "Writing a good CLAUDE.md", 2025) | SRS lints in agent-context manifest format |
| 2.3 BDD/acceptance criteria | Acceptance criteria double as agent prompts and as evals | Tier 2+ co-authored | TRANSFORMED: *BDD scenarios* serve as both Cursor/Claude spec inputs and eval rubric seeds | Each story has at least one runnable scenario or eval |
| 2.4 NFRs | Add agent-specific NFRs: max latency per turn, max tokens per task, autonomy bounds, refusal coverage, prompt-injection resistance | All agentic tiers | NEW: *Agent NFR section* | NFRs measurable via OTel GenAI metrics |
| 2.5 Requirements traceability | Trace expands from req → code → test to req → spec → prompt → eval → trajectory | Tier 3+ | TRANSFORMED: RTM → *spec-to-eval-to-trajectory traceability matrix* | Every req linked to at least one eval datum |
| 2.6 Spec-driven dev inputs | New step: write the Cursor Spec / Claude Code plan doc that the agent will consume | Tier 2+ | NEW: *Plan-Mode Planning Document*; *Cursor Spec file* | Spec is precise enough to plausibly solve task (Lütke/Karpathy criterion) |

### 2.Z Phase 2 Artifact Catalog

| Artifact | Canonical equivalent | Purpose | Format | Owner | Audience | Lifecycle | Tiers | Conf. | Citation |
|----------|----------------------|---------|--------|-------|----------|-----------|-------|-------|----------|
| Executable SRS / agent-readable spec | SRS | Single source of truth for human + agent | Markdown w/ headings, code fences | PO + Lead | Devs + agents | Living | 1–6 | [HIGH] | HumanLayer 2025; Anthropic Claude Code docs |
| Plan-Mode Planning Document | (no canonical equivalent) | Pre-execution plan agent commits to before coding | Markdown checklist | Agent (drafted) + human (approved) | Agent + reviewer | Per-task | 2–6 | [HIGH] | Cognition June 2025; Claude Code docs |
| Eval Plan | Test Plan | Define eval strategy: error-analysis, sample size, judges | Markdown | Eng + ML lead | QA, devs | Versioned | 2–6 | [HIGH] | Husain hamel.dev 2024–25 |
| Eval Dataset (seed) | Test cases | Inputs + expected behavior / golden traces | JSONL / parquet | Eng | Eng, judges | Versioned, hashed | 2–6 | [HIGH] | Husain; Datadog 2025 |
| Spec-to-Eval-to-Trajectory RTM | RTM | End-to-end traceability | Spreadsheet / DB | Eng lead | Audit, regulatory | Living | 3–6 | [MODERATE] | Generalization of canonical RTM under NIST RMF Manage 2.x |
| Agent NFR sheet | NFR section of SRS | Latency, token, refusal, autonomy NFRs | Markdown | Architect | Eng, SRE | Living | 2–6 | [HIGH] | OpenTelemetry GenAI 1.37 metrics |

---

## 3. Phase 3 — Architecture & Design (Delta)

### 3.0 Phase Summary
Canonical architecture artifacts (architecture description, ADRs, interface specs, threat models) survive but are joined by agent-specific design artifacts. The central design choice — **single agent vs. workflow vs. multi-agent** — is now a first-order architecture decision (ADR), with the published industry tension between Anthropic ("multi-agent works for breadth-first parallel research with careful prompt engineering") and Cognition ("don't build multi-agents; sub-agents lose context, decisions conflict") forming the canonical reference debate (Anthropic, June 13 2025; Cognition, June 12 2025). [CONTESTED]

### 3.1 Step-by-step deltas

| Canonical step | Activity delta | Ownership | Artifact deltas | Exit criteria |
|----------------|---------------|-----------|-----------------|---------------|
| 3.1 Architecture description | Add an "agent architecture" view: agents, tools, MCP servers, memory, retrieval, guardrails | Architect + ML lead | TRANSFORMED: *4+1 / C4 diagrams* gain an Agent view | Diagram includes every agent, tool, MCP server |
| 3.2 ADRs | New ADR types: pattern selection, model selection, framework selection, single-vs-multi-agent | Architect | NEW: *Agent Decision Records (AgDR)* using ADR template + agent fields | AgDR for each major agentic choice |
| 3.3 Interface specs | Tool schemas (JSON Schema function/tool defs), MCP server manifests | Eng | NEW: *Tool/Function Schemas*; *MCP Server Manifests (`server.json`)* | Schemas validated; MCP manifest passes registry schema |
| 3.4 Threat modeling | Map STRIDE + LINDDUN + OWASP LLM Top 10 (2025) + OWASP Agentic ASI (Dec 2025) | SecOps | TRANSFORMED: *Threat Model* gains LLM/agent sections | Each ASI threat addressed or accepted |
| 3.5 Data architecture | Add retrieval corpus, chunking spec, embedding model+version, vector store config | Data eng | NEW: *Retrieval Corpus Spec*; *Chunking Spec*; *Embedding Versioning Record* | Spec covers source, refresh cadence, PII handling |
| 3.6 Context architecture | Define what goes in `CLAUDE.md` / `AGENTS.md` vs. system prompt vs. session vs. tool docs | Architect + DevEx | NEW: *Context Manifest* | Manifest scoped under ~150–200 instructions (HumanLayer) |
| 3.7 HITL checkpoint design | Identify each point at which a human must approve / can override | Architect + product | NEW: *HITL Checkpoint Specification* | Each agent action class mapped to {auto, approve, deny} |

### 3.Z Phase 3 Artifact Catalog

| Artifact | Canonical equivalent | Purpose | Format | Owner | Audience | Lifecycle | Tiers | Conf. | Citation |
|----------|----------------------|---------|--------|-------|----------|-----------|-------|-------|----------|
| Agent Decision Record (AgDR) | ADR | Record agent-architecture choices | Markdown ADR + fields {pattern, model, framework, autonomy} | Architect | Eng, audit | Versioned | 2–6 | [MODERATE] | Generalization of Nygard ADR; Anthropic Dec 2024 patterns |
| Tool/Function Schema | Interface spec | Define each tool callable by the agent | JSON Schema | Eng | Agents, reviewers | Versioned | 1–6 | [HIGH] | OpenAI tool calling, Anthropic tool use, MCP spec |
| MCP Server Manifest (`server.json`) | Interface descriptor (e.g., OpenAPI) | Declare an MCP server's tools, resources, prompts, transport, auth | JSON conforming to MCP Schema | Eng | MCP clients, registry | Versioned | 2–6 | [HIGH] | modelcontextprotocol.io spec 2025-11-25; GoReleaser MCP guide |
| Agent Context Manifest (`CLAUDE.md`/`AGENTS.md`) | Coding standards + onboarding doc | Provide durable, repo-level instructions to all agents | Markdown at repo root and/or `~/.claude/` | Eng team | All agents + new humans | Living | 1–6 | [HIGH] | HumanLayer 2025; AGENTS.md convention (Sourcegraph/OpenAI/Google/Cursor/Factory 2025); copymarkdown.com |
| Retrieval Corpus Spec | Data dictionary | Define corpus, sources, freshness, PII rules | Markdown / YAML | Data eng | Eng, GRC | Living | 3–6 | [MODERATE] | OWASP LLM03/LLM04, LLM08 |
| Chunking Spec | (none — net-new) | Define chunk size, overlap, metadata | YAML | Data eng | Eng | Living | 3–6 | [MODERATE] | OWASP LLM08; LangChain context engineering blog |
| Embedding Versioning Record | CM record | Tie embeddings to model+version+date+corpus | YAML | Data eng | Eng | Versioned | 3–6 | [MODERATE] | NIST 600-1 Manage 1.3 |
| Guardrail Specification | Safety req | Define input/output filters, refusal rules, allow-lists | YAML/Markdown | Sec + ML | Eng | Versioned | 1–6 | [HIGH] | OpenAI guide, OWASP ASI |
| HITL Checkpoint Spec | Workflow def | Map each agent action class to autonomy level | Table | PO + Sec | All | Living | 2–6 | [HIGH] | Anthropic Dec 2024; OpenAI 2025 |
| Agent Threat Model | Threat model | Add LLM/agent threats | Markdown w/ STRIDE+ASI | SecOps | Eng, audit | Living | 1–6 | [HIGH] | OWASP LLM Top 10 2025; OWASP ASI Dec 2025; arXiv 2504.19956 |

---

## 4. Phase 4 — Implementation / Construction (Delta)

### 4.0 Phase Summary
Coding, code review, unit testing, and version control survive intact. The agent-driven delta replaces "the developer types code" with "the developer (or another agent) drives an agent that types code, and the result is reviewed". Three new construction artifacts are first-class: the **system prompt**, the **prompt library/registry**, and the **agent run log/trajectory**. Karpathy's late-2025 working style — directing agents from `program.md`-style files rather than touching Python directly (karpathy/autoresearch repo, 2025) — illustrates Tier 5 working mode. [HIGH]

### 4.1 Step-by-step deltas

| Canonical step | Activity delta | Ownership by tier | Artifact deltas | Exit criteria |
|----------------|---------------|------------------|-----------------|---------------|
| 4.1 Coding standards | Standards become *agent context*: belong in `CLAUDE.md`/`AGENTS.md`, not in chat | Tier 1+: shared manifest | TRANSFORMED: *Coding standards* split into linter-enforced (deterministic) and context-injected (agent-followed) | HumanLayer rule: never send LLM to do a linter's job |
| 4.2 Coding | Tier 0: autocomplete; Tier 1: chat-edit; Tier 2: plan→agent loop; Tier 3+: shared agent infra; Tier 5–6: agent owns ticket | Per tier above | TRANSFORMED: *Source code* now often agent-authored; NEW: *Agent run log* | Code passes linter, type-check, eval gate |
| 4.3 Code review | Reviews extend to prompt diffs, trajectory diffs, eval diffs | Tier 3+ | NEW: *Prompt-diff review*; *Trajectory review record*; TRANSFORMED: PR template gains agent fields ("driven by", "model", "tokens", "evals delta") | Reviewer initials each new artifact class |
| 4.4 Unit testing | Tests still authored; agents draft them; eval suite runs alongside | All tiers | TRANSFORMED: *Tests* may be agent-drafted; NEW: *Eval Suite* runs on every change | Both green |
| 4.5 Build & dependency management | Models, prompts, MCP servers, embeddings join classic deps | Tier 3+ | TRANSFORMED: *SBOM* becomes *AI BOM* covering models, prompts, datasets, MCP servers, embeddings | AI BOM generated and signed |
| 4.6 Configuration as code | Prompts, agent definitions, MCP configs, eval rubrics versioned in git | Tier 3+ | NEW: *Agent Configuration as Code* (yaml/markdown for prompts, agents, crews) | All agent config in version control |

### 4.Z Phase 4 Artifact Catalog

| Artifact | Canonical equivalent | Purpose | Format | Owner | Audience | Lifecycle | Tiers | Conf. | Citation |
|----------|----------------------|---------|--------|-------|----------|-----------|-------|-------|----------|
| System Prompt | (none — net-new) | Standing instructions defining agent role, constraints, tools | Markdown / template | ML eng | Agent runtime | Versioned, signed | 1–6 | [HIGH] | OpenAI/Anthropic docs; OWASP LLM07 |
| Agent Role/Persona Definition | Job description analog | Per-subagent prompt + tool allowlist + model | Markdown front-matter | Eng | Orchestrator + reviewers | Versioned | 4–6 | [HIGH] | Claude Code sub-agents docs; CrewAI yaml |
| Prompt Library / Registry | Reusable code library | Centralized canonical prompts | Repo + template engine (e.g., Jinja, MDX) | DevEx | Eng | Versioned | 3–6 | [MODERATE] | Anthropic resources whitepaper 2025 |
| Prompt Change Log | Changelog | Track every prompt edit + reason + eval delta | Markdown / commit message convention | Eng | Audit | Versioned | 3–6 | [MODERATE] | Husain prompt-versioning blog conventions [EMERGING] |
| Agent Run Log | Build log | Per-task record: messages, tool calls, files changed | JSONL + OTel spans | Agent runtime | Reviewers, SRE | Time-bounded retention | 1–6 | [HIGH] | OTel GenAI semconv |
| Trajectory Record | Test execution log | The full agent decision sequence for a task | OTel trace tree (`invoke_agent`, `execute_tool`, `chat`) | Runtime | Reviewers, eval, SRE | Retained | 2–6 | [HIGH] | OTel GenAI agent spans 2025 |
| Golden Trace | Reference test fixture | Known-good trajectory used for regression detection | JSON | Eng | Eval CI | Versioned | 3–6 | [HIGH] | Husain; Datadog 2025 |
| Eval Suite | Test suite | Runnable evals over datasets w/ judges | Code repo | ML eng | CI | Versioned | 2–6 | [HIGH] | Husain hamel.dev |
| LLM-Judge Rubric | Test oracle | Rubric used by an LLM judge to grade outputs | Markdown | ML eng | Judges | Versioned | 3–6 | [HIGH] | Maven course; Husain |
| AI BOM (full) | SBOM | Inventory of all AI components | SPDX 3.0.1 AI profile / CycloneDX 1.6 ML-BOM | SecOps | Supply-chain, audit | Per release | 3–6 | [HIGH] | SPDX 3.0.1; LF AI-BOM report; Wiz/Mend AI-BOM articles |
| Agent Configuration as Code | Build config | Agents, crews, graphs, tool maps as version-controlled config | YAML / Python module | Eng | Eng | Versioned | 3–6 | [HIGH] | LangGraph, CrewAI, AutoGen docs |

---

## 5. Phase 5 — Verification & Validation (Delta)

### 5.0 Phase Summary
This is the most heavily transformed phase. Classical V&V (unit/integration/system/UAT/static-analysis/security testing) is **augmented**, not replaced, by **eval-driven QA**. Husain's "vibes → evals" maturity progression — start by manually reviewing 20–50 outputs (error analysis), then build evaluators for the discovered failure modes — is the dominant practitioner model (Husain, "LLM Evals: Everything You Need to Know," 2025). [HIGH]

LLM-as-judge is widely used but its reliability is **[CONTESTED]**: Husain notes the "criteria drift" risk (Shankar et al.) and recommends maintaining a human "benevolent dictator" reviewer; Anthropic's June 2025 multi-agent post reports successful production use of LLM-judges paired with human rubric calibration.

### 5.1 Step-by-step deltas

| Canonical step | Activity delta | Ownership | Artifact deltas | Exit criteria |
|----------------|---------------|-----------|-----------------|---------------|
| 5.1 Test plan | Eval plan in addition to test plan | ML lead | TRANSFORMED: Test Plan → Test+Eval Plan | Plan covers deterministic tests *and* probabilistic evals |
| 5.2 Test cases | Eval datasets (input + expected behavior or rubric) and golden traces | ML eng | TRANSFORMED: test cases → *Eval Datasets* + *Golden Traces* | Dataset stratified across discovered error modes |
| 5.3 Static analysis | Add prompt-linting (length, instruction count, jailbreak patterns) | Sec eng | NEW: *Prompt linter results* | Prompts pass lints |
| 5.4 Security testing | Add LLM red-teaming (prompt injection, tool misuse, data exfiltration, agent session smuggling) | SecOps | NEW: *Agent Red-team Report* | OWASP LLM Top 10 + ASI checklist completed |
| 5.5 Integration testing | Add multi-agent integration evals; tool-chain end-state evals | ML eng | NEW: *Multi-agent eval scenarios*; end-state evals (Anthropic) | All scenarios meet target pass-rate |
| 5.6 UAT | UAT users observe trajectories, not just final outputs | Product + users | TRANSFORMED: *UAT report* now includes trajectory acceptance | Users approve both outputs and process |
| 5.7 Regression | Prompt-regression analyses run on every prompt/model/context change | Eng | NEW: *Prompt Regression Report* | No regressions vs. golden set |

### 5.Z Phase 5 Artifact Catalog

| Artifact | Canonical equivalent | Purpose | Format | Owner | Audience | Lifecycle | Tiers | Conf. | Citation |
|----------|----------------------|---------|--------|-------|----------|-----------|-------|-------|----------|
| Eval Plan | Test plan | Strategy for non-deterministic system V&V | Markdown | ML lead | Eng, audit | Living | 2–6 | [HIGH] | Husain hamel.dev |
| Eval Dataset | Test data | Curated inputs + expectations or rubric anchors | JSONL/parquet, hashed | ML eng | CI | Versioned | 2–6 | [HIGH] | Husain; Datadog "golden" datasets 2025 |
| Golden Trace | Reference exec | Reference trajectory for regression | JSON / OTel trace | ML eng | CI | Versioned | 3–6 | [HIGH] | OTel GenAI; Datadog 2025 |
| LLM-Judge Rubric | Acceptance criteria | Rubric prompt + score schema | Markdown / JSON Schema | ML eng | Judge model | Versioned | 3–6 | [HIGH] | Husain; Maven course |
| Agent Red-team Report | Pen-test report | Findings from prompt-injection / tool-misuse / exfil tests | Markdown | SecOps | GRC, eng | Per release | 1–6 | [HIGH] | OWASP LLM Top 10 2025; OWASP ASI Dec 2025 |
| Prompt Regression Report | Regression report | Pass-rate deltas vs. baseline on every prompt/model change | Dashboard + Markdown | ML eng | Eng | Per change | 3–6 | [HIGH] | Husain; LangSmith / Langfuse / Phoenix |
| Multi-Agent Eval Scenario | System test | End-state-graded multi-agent task | YAML + dataset | ML eng | CI | Versioned | 4–6 | [HIGH] | Anthropic June 2025 (end-state evaluation) |

---

## 6. Phase 6 — Release & Deployment (Delta)

### 6.0 Phase Summary
Release engineering, change management, deployment, and rollback survive. Net-new: **prompt deployment** and **model deployment** become first-class release artifacts; release decisions consider eval-suite pass rates and trajectory anomaly rates alongside test results. Anthropic's reported practice — *do not update agents simultaneously to avoid disrupting in-flight operations* — is an emerging release norm (Constellation, June 2025 summarizing Anthropic). [MODERATE]

### 6.1 Step-by-step deltas

| Canonical step | Activity delta | Ownership | Artifact deltas | Exit criteria |
|----------------|---------------|-----------|-----------------|---------------|
| 6.1 Release plan | Add prompt-version, model-version, MCP-server-version, embedding-version pinning | Release mgr | TRANSFORMED: *Release plan* gains AI-version section | All AI components pinned |
| 6.2 Deployment | Use staged rollouts; do not roll all agents simultaneously | DevOps + ML | TRANSFORMED: *Deployment runbook* gains agent rollout policy | Canary + percentage rollout signed off |
| 6.3 Release notes | Include AI BOM diff, prompt diff, eval-suite delta | Eng | TRANSFORMED: *Release notes* gain AI section + AI BOM diff | Notes published |
| 6.4 Rollback | Rollback now covers prompt, model, embedding, MCP server versions | DevOps | TRANSFORMED: *Rollback plan* covers AI components | Rehearsed in non-prod |
| 6.5 Sign-off | Go/no-go uses eval-suite pass rate + red-team report + AI BOM signature | GRC | TRANSFORMED: *Release approval* includes AI gates | All gates green |

### 6.Z Phase 6 Artifact Catalog

| Artifact | Canonical equivalent | Purpose | Format | Owner | Audience | Lifecycle | Tiers | Conf. | Citation |
|----------|----------------------|---------|--------|-------|----------|-----------|-------|-------|----------|
| AI BOM (signed, per-release) | SBOM | Frozen inventory of AI components for that release | SPDX 3.0.1 / CycloneDX 1.6 | SecOps | Customers, regulators | Per release | 3–6 | [HIGH] | LF AI-BOM; SPDX 3.0.1 |
| Release Eval Report | Test summary | Final eval results vs. acceptance thresholds | Dashboard + PDF | ML lead | GRC, audit | Per release | 2–6 | [HIGH] | Husain; OpenAI guide |
| Agent Rollout Policy | Deployment policy | Canary %, blast radius, simultaneity caps | YAML | SRE | DevOps | Living | 4–6 | [MODERATE] | Anthropic via Constellation 2025 |
| Prompt/Model Pinning Manifest | Version manifest | Cryptographic pin of all AI artifacts | YAML w/ hashes | Release mgr | Audit | Per release | 3–6 | [MODERATE] | TAIBOM 2025 (arXiv 2510.02169) |

---

## 7. Phase 7 — Operations & Maintenance (Delta)

### 7.0 Phase Summary
SRE, monitoring, incident response, runbooks, and postmortems survive but acquire AI-specific instrumentation. The reference observability schema is the **OpenTelemetry GenAI Semantic Conventions** (development → v1.37+ stable adoption by Datadog, Portkey, etc., 2025), defining `gen_ai.*` spans for `chat`, `invoke_agent`, `create_agent`, `execute_tool`, `embeddings`, evaluation events, and per-token metrics. [HIGH]

### 7.1 Step-by-step deltas

| Canonical step | Activity delta | Ownership | Artifact deltas | Exit criteria |
|----------------|---------------|-----------|-----------------|---------------|
| 7.1 Monitoring | Add agent observability: spans, token usage, judge scores, refusal rate, tool error rate | SRE + ML | TRANSFORMED: *Dashboards* gain GenAI panels | OTel GenAI metrics flowing |
| 7.2 Incident response | New incident classes: prompt-injection, runaway agent, tool misuse, hallucinated commit, context-rot regression | SRE | NEW: *Agent Incident Playbook* | Playbook covers ASI top-10 |
| 7.3 Runbooks | Runbooks declare agent autonomy bounds, HITL fallbacks | SRE | TRANSFORMED: *Runbooks* → *Agent Runbooks* | Each runbook lists allowed-tools and escalation |
| 7.4 Postmortems | Postmortems analyze trajectories and prompt history; produce *agent failure analyses* | SRE + ML | NEW: *Agent Failure Analysis*; *Prompt Regression Analysis* | Root cause classified (model/context/tool/prompt) |
| 7.5 Continuous improvement | Re-evaluate evals; refresh corpus; retrain or migrate models | ML | TRANSFORMED: *CIP* gains AI loop | Regular eval refresh cadence |
| 7.6 Cost / SLO management | Token-cost SLOs alongside latency/error SLOs | SRE | NEW: *Token-cost SLO* | Dashboards track $/task |

### 7.Z Phase 7 Artifact Catalog

| Artifact | Canonical equivalent | Purpose | Format | Owner | Audience | Lifecycle | Tiers | Conf. | Citation |
|----------|----------------------|---------|--------|-------|----------|-----------|-------|-------|----------|
| Agent Runbook | Runbook | Operational procedure incl. autonomy, HITL, escalation | Markdown | SRE | On-call | Living | 1–6 | [HIGH] | OpenAI guide; Anthropic Dec 2024 |
| Agent Incident Playbook | Incident playbook | Per-class IR guidance | Markdown | SecOps + SRE | On-call, GRC | Living | 1–6 | [HIGH] | OWASP ASI Dec 2025 |
| Agent Failure Analysis | Postmortem | RCA for agent-driven incident | Markdown | SRE + ML | Org-wide | Per incident | 1–6 | [HIGH] | OTel GenAI; Anthropic June 2025 |
| Prompt Regression Analysis | Defect analysis | Diagnose drop in eval pass rate after prompt/model change | Markdown + Dashboard | ML eng | Eng | Per regression | 3–6 | [HIGH] | Husain; LangSmith/Langfuse |
| Trajectory Archive | Audit log | Long-term trajectory store for compliance and learning | OTel-compatible store | SRE | GRC, ML | Retention-policy | 4–6 | [MODERATE] | OTel GenAI; ISO 42001 Annex A |

---

## 8. Phase 8 — Retirement / Decommissioning (Delta)

### 8.0 Phase Summary
Sunset, data archival, knowledge transfer, contract closure survive. Net-new: **model and prompt sunset**, **embedding/corpus disposal**, and **trajectory retention/erasure** under privacy law. ISO/IEC 42001 Annex A requires lifecycle decommissioning controls for AIMS. [HIGH]

### 8.1 Step-by-step deltas

| Canonical step | Activity delta | Ownership | Artifact deltas | Exit criteria |
|----------------|---------------|-----------|-----------------|---------------|
| 8.1 Sunset plan | Add model/prompt/MCP-server retirement schedule | Architect | TRANSFORMED: *Sunset plan* covers AI components | All components scheduled |
| 8.2 Data archival | Embedding corpora archived or destroyed; PII purged | Data eng + GRC | NEW: *Embedding Disposition Record* | Archival/destruction certified |
| 8.3 Trajectory retention | Decide retention vs. erasure of agent run logs | GRC | NEW: *Trajectory Retention Policy execution record* | Policy executed |
| 8.4 Knowledge transfer | Migrate `CLAUDE.md`/`AGENTS.md` to successor system or archive | DevEx | TRANSFORMED: *KT pack* includes context manifests | Pack delivered |

### 8.Z Phase 8 Artifact Catalog

| Artifact | Canonical eq. | Purpose | Format | Owner | Tiers | Conf. | Citation |
|----------|--------------|---------|--------|-------|-------|-------|----------|
| Model/Prompt Sunset Record | Sunset record | Final disposition of AI artifacts | Markdown | Architect | 3–6 | [MODERATE] | ISO 42001 Annex A |
| Embedding Disposition Record | Data disposition | Archival or destruction proof for vector stores | Form | Data eng | 3–6 | [MODERATE] | OWASP LLM08 |
| Trajectory Retention Policy execution | Audit log | Proof retention/erasure was executed | Form + signature | GRC | 4–6 | [MODERATE] | ISO 42001; GDPR analog |

---

## 9. Net-New Agentic Artifact Catalog (Comprehensive)

| # | Artifact | Purpose | Format | Author | Lifecycle | Phases | Tiers | Conf. | Citation |
|---|---------|---------|--------|--------|-----------|--------|-------|-------|----------|
| 1 | System Prompt | Standing instructions for agent identity, constraints, tools | Markdown / template | ML eng | Versioned | 3–7 | 1–6 | [HIGH] | OpenAI/Anthropic; OWASP LLM07 |
| 2 | Agent Role / Persona Definition | Per-subagent prompt + tools + model | Markdown front-matter | ML eng | Versioned | 3–7 | 4–6 | [HIGH] | Claude Code subagents; CrewAI |
| 3 | Tool / Function Schema | Machine-readable tool contract | JSON Schema | Eng | Versioned | 3–7 | 1–6 | [HIGH] | OpenAI tool calling; MCP spec |
| 4 | MCP Server Manifest (`server.json`) | Declares tools/resources/prompts/transport for an MCP server | JSON | Eng | Versioned | 3–7 | 2–6 | [HIGH] | modelcontextprotocol.io 2025-11-25 |
| 5 | Context Manifest (`CLAUDE.md`/`AGENTS.md`/`.cursorrules`/`.windsurfrules`) | Repo-level standing context for agents | Markdown / TOML-like | Team | Living | 2–7 | 1–6 | [HIGH] | HumanLayer 2025; AGENTS.md convention 2025 |
| 6 | Prompt Library / Registry | Centralized canonical prompts | Repo + template engine | DevEx | Versioned | 4–7 | 3–6 | [MODERATE] | Anthropic 2025 architecture whitepaper |
| 7 | Prompt Change Log | Per-prompt diff + rationale + eval delta | Markdown / commit conv. | Eng | Versioned | 4–7 | 3–6 | [EMERGING] | Husain 2025; community convention |
| 8 | Eval Plan | Strategy for evaluating non-deterministic outputs | Markdown | ML lead | Living | 2–7 | 2–6 | [HIGH] | Husain 2024–25 |
| 9 | Eval Dataset | Inputs + expectations / rubric anchors | JSONL/parquet | ML eng | Versioned | 2–7 | 2–6 | [HIGH] | Husain |
| 10 | Golden Trace | Known-good trajectory | JSON / OTel | ML eng | Versioned | 4–7 | 3–6 | [HIGH] | OTel GenAI; Datadog 2025 |
| 11 | LLM-Judge Rubric | Prompt+schema for an LLM judge | Markdown / JSON | ML eng | Versioned | 5–7 | 3–6 | [HIGH] | Husain; Maven course |
| 12 | Agent Run Log | Per-task message/tool history | JSONL + OTel | Runtime | Retention | 4–7 | 1–6 | [HIGH] | OTel GenAI |
| 13 | Trajectory Record | Full agent decision tree | OTel trace | Runtime | Retention | 4–7 | 2–6 | [HIGH] | OTel GenAI agent spans |
| 14 | Agent Decision Record (AgDR) | Architectural decision specific to agent design | Markdown | Architect | Versioned | 1–3 | 2–6 | [MODERATE] | ADR (Nygard) generalization |
| 15 | Guardrail Specification | Input/output filter rules, refusal rules | YAML/MD | SecOps | Versioned | 3–7 | 1–6 | [HIGH] | OpenAI guide; OWASP ASI |
| 16 | Agent Capability Card | Describes agent role, autonomy, tools | Markdown | Product+Eng | Living | 1–8 | 3–6 | [MODERATE] | Generalization of model cards |
| 17 | AI BOM / Model BOM / Prompt BOM | Inventory of models/prompts/datasets/MCP servers/embeddings | SPDX 3.0.1 AI / CycloneDX 1.6 ML-BOM | SecOps | Per release | 1–8 | 3–6 | [HIGH] | LF AI-BOM 2024; SPDX 3.0.1; arXiv 2511.12668 (AIRS) |
| 18 | Agent Runbook | Ops procedure incl. autonomy bounds, HITL | Markdown | SRE | Living | 6–7 | 1–6 | [HIGH] | Anthropic Dec 2024 |
| 19 | Agent Failure Analysis | RCA for agent incident | Markdown | SRE+ML | Per incident | 7 | 1–6 | [HIGH] | Anthropic June 2025; Husain |
| 20 | Prompt Regression Analysis | Diagnose eval drop after change | Markdown+dashboard | ML | Per regression | 5–7 | 3–6 | [HIGH] | Husain; Phoenix/Langfuse |
| 21 | Agent Threat Model | LLM/agent threats per OWASP & STRIDE | Markdown | SecOps | Living | 1–7 | 1–6 | [HIGH] | OWASP LLM Top 10 2025; ASI Dec 2025; arXiv 2504.19956 |
| 22 | Retrieval Corpus Spec | Source/freshness/PII rules | Markdown/YAML | Data eng | Living | 3–7 | 3–6 | [MODERATE] | OWASP LLM03/08; LangChain context blog |
| 23 | Chunking Spec | Chunk size/overlap/metadata | YAML | Data eng | Living | 3–7 | 3–6 | [MODERATE] | OWASP LLM08; LangChain |
| 24 | Embedding Versioning Record | Tie embeddings to model/version/date/corpus | YAML | Data eng | Versioned | 3–8 | 3–6 | [MODERATE] | NIST 600-1 Manage 1.3 |
| 25 | Plan-Mode Planning Document | Pre-execution plan committed by agent | Markdown | Agent + human | Per task | 2–4 | 2–6 | [HIGH] | Cognition June 2025; Claude Code |
| 26 | HITL Checkpoint Spec | Maps action classes to autonomy levels | Table | PO+Sec | Living | 3–7 | 2–6 | [HIGH] | Anthropic Dec 2024; OpenAI 2025 |

---

## 10. Transformed Canonical Artifact Crosswalk

| Canonical artifact | Agentic transformation | New format | Governance change | Source(s) | Conf. |
|--------------------|----------------------|-----------|-------------------|-----------|-------|
| SRS / user stories | Executable specs / agent-readable spec / Cursor Spec / plan doc | Markdown structured for LLM context | PO sign-off remains; agent-draft permitted but reviewed | HumanLayer 2025; Cursor docs | [HIGH] |
| BDD scenarios | Dual-purpose: agent prompt + eval seed | Gherkin or rubric | Acceptance evals binding | Husain hamel.dev | [HIGH] |
| Test plan | Test+Eval Plan | Markdown | Eval gates added to CI | Husain | [HIGH] |
| Test cases | Eval Datasets + Golden Traces + LLM-Judge Rubrics | JSONL + JSON | Datasets versioned, hashed, contamination-controlled | Husain; Datadog 2025 | [HIGH] |
| Code review records | Add prompt-diff and trajectory reviews | Git PR + linked artifacts | New reviewer competency | HumanLayer 2025 | [MODERATE] |
| Runbooks | Agent Runbooks with autonomy bounds + HITL | Markdown | SRE-AI on-call | Anthropic Dec 2024 | [HIGH] |
| Postmortems | Agent Failure Analyses + Prompt Regression Analyses | Markdown + dashboards | New RCA categories: model, context, tool, prompt | Anthropic June 2025; Husain | [HIGH] |
| Threat models | Agent Threat Models incl. prompt injection, tool misuse, context exfiltration, agent session smuggling | Markdown w/ STRIDE+ASI | OWASP ASI as required input; STRIDE-AI per AWS 2025 | OWASP LLM Top 10 2025; ASI Dec 2025 | [HIGH] |
| Configuration management | Prompt + model + context + embedding versioning | Git + hash pinning + AI BOM | CM scope expanded | TAIBOM 2025; SPDX 3.0.1 | [HIGH] |
| SBOM | AI BOM / Model BOM / Prompt BOM | SPDX 3.0.1 AI profile / CycloneDX 1.6 ML-BOM | Required for EU AI Act / 42001 | LF AI-BOM 2024; AIRS arXiv 2025 | [HIGH] |
| Requirements Traceability Matrix (RTM) | Spec→Eval→Trajectory traceability matrix | DB / spreadsheet | Trace to runtime decisions | Generalization under NIST RMF Manage 2.x | [MODERATE] |
| Coding standards | Split: linter-enforced (deterministic) vs. agent-context-injected | `.eslintrc` + `CLAUDE.md`/`AGENTS.md` | Never delegate linter work to agent | HumanLayer 2025 | [HIGH] |
| Architecture description | Adds Agent View (agents/tools/MCP/memory/retrieval) | C4 + Agent view | New AgDRs | Anthropic Dec 2024 + June 2025 | [HIGH] |

---

## 11. Process Pattern Catalog

### 11.1 Specification-driven development
**Originator:** Tobi Lütke / Lovable / Cursor Spec / Claude Code plan-mode (2024–2025). **Problem:** under-specified prompts cause unreliable agent behavior. **Structure:** spec → plan → implement → verify loop, with the spec the durable artifact. **When to use:** Tier 2+, well-defined tasks. **When not to use:** open-ended research; over-engineered specs increase rigidity. **Anti-pattern:** writing specs *for the agent* that no human will maintain. **Citation:** Anthropic Dec 2024; HumanLayer 2025. [HIGH]

### 11.2 Plan-mode / agent-mode separation
**Originator:** Claude Code plan-mode + agent-mode; Cline Plan/Act; Cursor Agent. **Problem:** mixing planning and execution leads to context bloat and unverified actions. **Structure:** read-only plan → user approval → execution. **When to use:** any change >1 file. **Not when:** trivial autocompletes. **Anti-pattern:** executing without an approved plan. **Citation:** Claude Code docs; Cline docs. [HIGH]

### 11.3 Context engineering as a discipline
**Originator:** Karpathy ("delicate art and science of filling the context window with just the right information for the next step"); Tobi Lütke; Drew Breunig; Chip Huyen *AI Engineering* (O'Reilly, 2024). **Problem:** prompts under-perform without intentional context curation. **Structure:** instructions + memory + retrieval + tool descriptions + state, layered (global → project → session). **When to use:** every agentic project. **Anti-pattern:** stuffing every command and convention into `CLAUDE.md` (HumanLayer recommends ≤150–200 instructions). **Citation:** Karpathy 2025 quote; LangChain blog 2025; Breunig 2025. [HIGH]

### 11.4 Eval-driven development (and the "vibes → evals" progression)
**Originator:** Hamel Husain ("Your AI Product Needs Evals," 2024); Shreya Shankar et al. on criteria drift; Eugene Yan on LLM patterns. **Problem:** non-deterministic outputs cannot be regression-tested by classical means. **Structure:** error analysis on real outputs → discover failure modes → write evaluators for those modes (not imagined ones) → iterate. **When to use:** any LLM/agent product. **Not when:** trivial deterministic tasks. **Anti-pattern:** "eval-driven development" as TDD for LLMs (Husain warns this generally creates more problems than it solves; exception only for narrow guardrail constraints). **Citation:** Husain hamel.dev "evals-faq" 2024–2025; Maven course 2025. [HIGH] [CONTESTED with classical EvalOps advocacy]

### 11.5 Multi-agent patterns
Anthropic's Dec 2024 taxonomy is the de facto reference. [HIGH]

| Pattern | One-liner | Use when | Avoid when |
|---------|-----------|---------|------------|
| Augmented LLM | Single LLM + tools/memory/retrieval | Most cases | Never — it's the foundation |
| Prompt chaining | Sequential LLM calls, fixed steps | Decomposable, predictable | Need branching |
| Routing | Classifier picks downstream call | Diverse query classes | Pure retrieval works |
| Parallelization (sectioning, voting) | Run subtasks or replicas in parallel | Independent subtasks; safety voting | Tightly coupled state |
| Orchestrator-worker | Lead LLM dispatches dynamic subtasks to workers | Open-ended research; breadth-first parallel exploration (Anthropic Research) | Tasks need shared moving state (Cognition warning) |
| Evaluator-optimizer | Generator + critic loop | Improvable outputs with clear rubric | No clear rubric |
| Autonomous agent | Tools-in-a-loop until done | Open-ended, trusted environment | Hard latency/cost budgets |

**The 2025 multi-agent debate.** Cognition Labs ("Don't Build Multi-Agents," June 12 2025) argues that naive sub-agent setups break because sub-agents lack context of each other's work and their parallel actions encode conflicting implicit decisions; Cognition prescribes single-threaded agents with context compression for long-running tasks. Anthropic ("How we built our multi-agent research system," June 13 2025) reports a multi-agent system with Claude Opus 4 lead + Sonnet 4 subagents outperformed a single-agent Opus 4 by 90.2% on its internal research eval, but consumed ≈15× more tokens than chat and ≈4× more than a single agent, and was unsuitable for "tightly interdependent tasks such as coding". Both positions converge on: write-paths should remain single-threaded; multi-agent shines for read-heavy parallel breadth; coordination overhead and prompt engineering dominate the engineering cost. [CONTESTED: Cognition 2025-06-12 vs Anthropic 2025-06-13]

### 11.6 Reflection / Reflexion / ReAct / CodeAct / Toolformer / Voyager / Generative Agents
- **ReAct** (Yao et al., ICLR 2023): interleave Thought→Action→Observation. Foundation for nearly all modern agent loops. [HIGH]
- **Reflexion** (Shinn et al., 2023): verbal reinforcement via self-critique. [HIGH]
- **Toolformer** (Schick et al., 2023): self-supervised tool use. [HIGH]
- **Voyager** (Wang et al., 2023): lifelong-learning agent in Minecraft, skill library. [HIGH]
- **Generative Agents** (Park et al., 2023): memory-stream + reflection + planning architecture. [HIGH]
- **CodeAct** (2024): the agent writes and executes code instead of calling fixed tools. [MODERATE]
- **SWE-agent / SWE-bench** (Yang et al., NeurIPS 2024; Jimenez et al., ICLR 2024): agent-computer interface (ACI) is the primary determinant of coding-agent performance. [HIGH]

### 11.7 Human-in-the-loop checkpoint design
**Source:** Anthropic Dec 2024; OpenAI Apr 2025 ("A Practical Guide to Building Agents"). **Pattern:** classify each action into {auto, approve-then-act, deny}; require approval for destructive ops; set max-retry / max-step ceilings ("exceeding failure thresholds"); always allow human escalation. **Anti-pattern:** infinite approval prompts (causes user fatigue → rubber-stamping). [HIGH]

### 11.8 Agent harness patterns and tool selection
**Source:** Yang et al. SWE-agent NeurIPS 2024; Anthropic 2025 architecture whitepaper. **Pattern:** the agent-computer interface — file editor, shell, search, browser — is co-designed with the model; tool count <15 distinct, well-named; tools should fail loudly with structured errors so the agent can self-correct. **Anti-pattern:** 50 overlapping tools or string-only error messages. [HIGH]

---

## 12. Complexity Tier Walkthrough (All 8 Phases × Tiers 0–6)

(Compressed; "—" = unchanged from canonical; "+X" = artifact added; "→Y" = artifact transformed.)

### 12.1 Tier 0 — Solo dev with code completion (Copilot autocomplete, Tabnine)
1. Initiation: — 2. Reqs: — 3. Arch: — 4. Impl: completions logged for audit (+org policy). 5. V&V: — 6. Release: — 7. Ops: — 8. Retire: —. Net effect: agent treated as IDE feature; SDLC unchanged; AI use disclosed in PR template. [HIGH]

### 12.2 Tier 1 — Solo dev with conversational agent (Cursor chat / Claude Code interactive / Continue)
+ `.cursorrules` or `CLAUDE.md` (Phase 3); + chat transcripts retained per org policy (Phase 4); → Code review checks AI-authored sections (Phase 4). Other phases unchanged. [HIGH]

### 12.3 Tier 2 — Solo dev with autonomous coding agent (Claude Code plan/agent, Aider, Cline, Codex CLI)
Phase 2 → executable spec; Phase 3 + plan-mode planning doc, + tool/function schemas; Phase 4 + agent run log, + prompt change log; Phase 5 + eval plan + small eval dataset; Phase 6 + simple AI BOM; Phase 7 + agent runbook (autonomy bounds). HITL gate at end of plan-mode. [HIGH]

### 12.4 Tier 3 — Team with shared agent infrastructure
Phases 1–3: + AgDRs, shared `AGENTS.md`, MCP server manifests, prompt registry. Phase 4: agent CI runs evals; prompt-diff review enforced. Phase 5: full eval suite + golden traces + LLM-judge rubrics + red-team report. Phase 6: signed AI BOM; staged rollouts. Phase 7: OTel GenAI dashboards + agent failure analyses. Phase 8: embedding disposition record. NIST AI RMF Govern/Map/Measure/Manage operationalized. [HIGH]

### 12.5 Tier 4 — Multi-agent build subsystem (LangGraph / AutoGen / CrewAI / OpenAI Agents SDK / Semantic Kernel)
Adds: orchestrator-worker / planner-executor design (Phase 3); per-subagent role/persona definitions; multi-agent eval scenarios with end-state grading (Phase 5; Anthropic 2025); inter-agent trace correlation in OTel. ISO/IEC 42001 AIMS scope likely; OWASP ASI mapping mandatory. [HIGH]

### 12.6 Tier 5 — Agent-native engineering (Devin, Codex cloud agents, Copilot Workspace)
Agent owns Phase 2 detailed reqs, Phase 3 design, Phase 4 implementation, Phase 5 self-eval. Human owns Phase 1, Phase 6 release decision, Phase 8 retirement. Required: trajectory archival; signed AI BOM per release; per-task plan doc; PR-level human review. Cognition's reported Devin practice — long planning step plus visual-diff screenshots delivered via Slack — is the canonical Tier-5 review pattern (Jason Liu summary, Sept 2025). [MODERATE]

### 12.7 Tier 6 — Agent-orchestrated workflow products (production multi-agent systems)
Adds runtime governance: EU AI Act high-risk obligations where applicable (logging, transparency, human oversight, robustness), 24/7 agent-SRE, real-time guardrail telemetry, A2A / inter-agent identity (per OWASP ASI Dec 2025 case studies on Agent Session Smuggling — Palo Alto Unit 42, Nov 2025). Trajectory retention bounded by GDPR/sectoral law. [HIGH]

---

## 13. Cross-Cutting Concern Reframing

| Concern | Canonical | Agentic delta | New artifacts | Frameworks / standards |
|---------|-----------|---------------|---------------|------------------------|
| Project Mgmt | Plans, schedules, RACI | Add token-cost forecasts; agent vs. human task split; Tier-aware estimation | Token budget; per-task autonomy spec | Anthropic Dec 2024; OpenAI Apr 2025 |
| Risk | Risk register | Add LLM/agent-specific risks (prompt injection, excessive agency, system-prompt leakage, vector/embedding weaknesses, supply chain, unbounded consumption, misinformation, data poisoning, sensitive disclosure, improper output handling) | Agent threat model | OWASP LLM Top 10 2025; OWASP ASI Dec 2025; NIST AI 600-1; arXiv 2504.19956 |
| Configuration Mgmt | Versioned source/binaries | + prompt versioning, model versioning, embedding versioning, MCP-server versioning, context-manifest versioning | AI BOM, prompt change log, embedding versioning record | SPDX 3.0.1 AI profile; CycloneDX 1.6 ML-BOM; TAIBOM 2025 |
| QA | Tests + reviews | + evals, golden traces, LLM-judge rubrics, prompt-regression CI | Eval suite; trajectory archive | Husain 2024–25; Maven course |
| Security | AppSec + threat modeling | + LLM/agent threat modeling, agent red-teaming, MCP server trust, A2A identity, prompt-injection defenses | Agent red-team report | OWASP LLM Top 10 2025; OWASP ASI Dec 2025; AWS ISO 42001 STRIDE blog 2025 |
| Compliance | Regulatory mapping | + NIST AI RMF GOVERN/MAP/MEASURE/MANAGE; + ISO/IEC 42001 AIMS; + EU AI Act high-risk obligations (where applicable); + sectoral overlays | AI compliance class decision; AIMS scope statement | NIST AI 100-1 / 600-1; ISO/IEC 42001:2023; EU AI Act |
| Documentation | SRS, design, ops | + context manifests, agent capability cards, AgDRs | `CLAUDE.md`/`AGENTS.md`; capability card | HumanLayer 2025; AGENTS.md convention |
| Measurement | KPIs, defect density | + token usage, judge scores, refusal rate, tool error rate, trajectory anomaly rate, prompt-regression rate | OTel GenAI metrics dashboards | OpenTelemetry GenAI semconv 1.37+ |
| Supplier / SOUP | Third-party SW | + model providers, MCP servers, embedding providers, vector DBs, agent frameworks treated as SOUP-equivalent suppliers | Supplier-AI assessment | OWASP LLM03; ISO 42001 supplier oversight |
| Observability | APM | + agent observability platforms (LangSmith, Langfuse, Arize Phoenix, Datadog LLM Obs); OTel GenAI traces/events/metrics | Trajectory archive; eval-event stream | OTel GenAI; Datadog 2025 |
| Incident response | SRE IR | + agent IR playbook, prompt-injection IR, tool-misuse IR | Agent incident playbook | OWASP ASI Dec 2025 |

---

## 14. Agentic Engineering Maturity Model (5 Levels)

Modeled on OWASP SAMM levels and adapted from Husain's "vibes → evals" progression and NIST AI RMF GOVERN/MAP/MEASURE/MANAGE. [MODERATE]

| Level | Name | Markers — Practices | Markers — Artifacts | Markers — Governance |
|-------|------|---------------------|---------------------|---------------------|
| 1 | Ad-hoc ("vibes") | Free-form chat with agents; no eval; no shared context | Possibly a `CLAUDE.md`; chat transcripts | Org AI usage policy at most |
| 2 | Repeatable | Plan-mode used; per-repo `AGENTS.md`; manual error analysis on a few outputs | Spec docs; small eval dataset; tool/function schemas | NIST RMF GOVERN started; AI BOM placeholder |
| 3 | Defined | Eval-driven dev; prompt registry; CI runs evals on every PR; agent threat model exists | Full eval suite, golden traces, LLM-judge rubrics, AgDRs, MCP manifests, signed AI BOM per release | NIST RMF MAP+MEASURE; OWASP LLM Top 10 mapping; ISO 42001 gap-assessed |
| 4 | Managed | OTel GenAI in prod; trajectory anomaly alerts; prompt regression CI; agent runbooks; staged rollouts; agent SRE on-call | Trajectory archive; prompt regression dashboards; agent capability cards; HITL checkpoint spec | NIST RMF MANAGE; ISO/IEC 42001 certified or equivalent; OWASP ASI assessed |
| 5 | Optimizing | Continuous error analysis loops feeding eval set growth; automatic prompt-eval co-evolution; multi-agent A/B testing; learnings flow back to context manifests | Living prompt-eval-context graph; closed-loop trajectory→eval feedback | EU AI Act conformity (if high-risk); auditable A2A identity; supply-chain attestations (TAIBOM-style) |

---

## 15. Open Questions and Active Debates

1. **Single-agent vs multi-agent.** Cognition (Walden Yan, Jun 12 2025) vs. Anthropic (Hadfield et al., Jun 13 2025). Convergence point: writes single-threaded; reads/research can be parallel. [CONTESTED]
2. **Spec-driven vs error-analysis-driven for agents.** Cursor Spec / Lovable / Karpathy `program.md` advocate writing specs first; Husain advocates error analysis first and writing evals only for *observed* failures. [CONTESTED]
3. **Cursor vs Claude Code spec workflow.** Cursor's "Spec" treats the spec doc as the primary artifact the agent reconciles to; Claude Code plan-mode produces an ephemeral plan committed only after approval. The first preserves the spec as durable artifact; the second elevates the trajectory as the durable artifact. [VARIES: Cursor-style vs Claude-Code-style]
4. **Optimal HITL frequency.** Anthropic recommends checkpoints "at blockers"; OpenAI recommends per-action thresholds. No consensus on rate. [EMERGING]
5. **LLM-as-judge reliability.** Anthropic's June 2025 multi-agent post reports successful production use; Husain/Shankar warn of "criteria drift" and unaligned judges; recommend keeping human "benevolent dictator". [CONTESTED]
6. **Prompt versioning conventions.** Semantic versioning of prompts, content-hash pinning, or commit-tracked Markdown all in use; no standard. [EMERGING]
7. **Where to draw the AGENTS.md / CLAUDE.md line.** Sourcegraph/OpenAI/Google/Cursor/Factory backed AGENTS.md (2025); Anthropic's Claude Code retains CLAUDE.md (open issue #34235 / #6235 to support AGENTS.md natively). Common workaround: symlink. [EMERGING]
8. **Agent identity / A2A trust.** OWASP ASI documents (2025) flag inter-agent trust (Agent Session Smuggling, Palo Alto Unit 42 Nov 2025) but standards are nascent. [EMERGING]

---

## 16. Sources Consulted

- Schluntz, E., & Zhang, B. (Anthropic). "Building Effective Agents." Dec 19 2024. https://www.anthropic.com/research/building-effective-agents (accessed May 2026).
- Anthropic. "Building Effective AI Agents — Architecture Patterns and Implementation Frameworks" (whitepaper PDF). https://resources.anthropic.com/building-effective-ai-agents (2025).
- Hadfield, J., Zhang, B., Lien, K., Scholz, F., Fox, J., Ford, D. (Anthropic). "How we built our multi-agent research system." Jun 13 2025. https://www.anthropic.com/engineering/multi-agent-research-system.
- Cognition Labs. "Don't Build Multi-Agents." Jun 12 2025. https://cognition.ai/blog/dont-build-multi-agents.
- Liu, J. (summary). "Why Cognition does not use multi-agent systems." Sep 11 2025. https://jxnl.co/writing/2025/09/11/why-cognition-does-not-use-multi-agent-systems/.
- Anthropic. Claude Code documentation: sub-agents, plan mode, headless mode. https://code.claude.com/docs/ (accessed 2026).
- Anthropic. Model Context Protocol. https://modelcontextprotocol.io/specification/2025-11-25 (spec rev 2025-11-25).
- modelcontextprotocol/modelcontextprotocol GitHub (Linux Foundation). https://github.com/modelcontextprotocol/modelcontextprotocol.
- OpenAI. "A Practical Guide to Building Agents." Apr 2025. https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf.
- OpenAI Developers. Agents SDK and Building Agents tracks. https://developers.openai.com/tracks/building-agents and https://developers.openai.com/api/docs/guides/agents.
- OpenAI Apps SDK / MCP server documentation. https://developers.openai.com/apps-sdk/concepts/mcp-server.
- Microsoft. AutoGen documentation. https://microsoft.github.io/autogen/.
- Microsoft. Semantic Kernel docs. https://learn.microsoft.com/en-us/semantic-kernel/.
- LangChain. "Context Engineering." https://www.langchain.com/blog/context-engineering-for-agents.
- LangChain / LangGraph official documentation. https://python.langchain.com/ ; https://langchain-ai.github.io/langgraph/.
- CrewAI documentation. https://docs.crewai.com/.
- LlamaIndex agents documentation. https://docs.llamaindex.ai/.
- Karpathy, A. autoresearch repository (`program.md` agent driving). https://github.com/karpathy/autoresearch.
- Karpathy, A. context-engineering quote (compiled in davidkimai/Context-Engineering). https://github.com/davidkimai/Context-Engineering.
- HumanLayer. "Writing a good CLAUDE.md." 2025. https://www.humanlayer.dev/blog/writing-a-good-claude-md.
- HiveTrail. "AGENTS.md vs CLAUDE.md: The AI Developer's Guide to Context Standards." 2026. https://hivetrail.com/blog/agents-md-vs-claude-md-cross-tool-standard.
- Copymarkdown. "CLAUDE.md, AGENTS.md, GEMINI.md Explained." https://copymarkdown.com/agents-md-explained/.
- Anthropic Claude Code GitHub Issues #6235 / #34235 (AGENTS.md support). https://github.com/anthropics/claude-code/issues/34235.
- Husain, H. "Your AI Product Needs Evals." 2024. https://hamel.dev/blog/posts/evals/.
- Husain, H. "LLM Evals: Everything You Need to Know" (FAQ + PDF, 2025). https://hamel.dev/blog/posts/evals-faq/.
- Husain, H. "Should I practice eval-driven development?" 2025. https://hamel.dev/blog/posts/evals-faq/should-i-practice-eval-driven-development.html.
- Maven. "AI Evals For Engineers & PMs" (Husain & Shankar). https://maven.com/parlance-labs/evals.
- Pragmatic Engineer. "A pragmatic guide to LLM evals for devs" (Husain interview). https://newsletter.pragmaticengineer.com/p/evals.
- Yao, S. et al. "ReAct: Synergizing Reasoning and Acting in Language Models." ICLR 2023. https://arxiv.org/abs/2210.03629.
- Shinn, N. et al. "Reflexion: Language Agents with Verbal Reinforcement Learning." 2023.
- Schick, T. et al. "Toolformer." 2023.
- Wang, G. et al. "Voyager: An Open-Ended Embodied Agent with LLMs." 2023.
- Park, J.S. et al. "Generative Agents: Interactive Simulacra of Human Behavior." 2023.
- Yang, J., Jimenez, C.E., Wettig, A., Lieret, K., Yao, S., Narasimhan, K., Press, O. "SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering." NeurIPS 2024. https://arxiv.org/abs/2405.15793.
- Jimenez, C.E. et al. "SWE-bench: Can Language Models Resolve Real-world GitHub Issues?" ICLR 2024. https://www.swebench.com.
- NIST. AI Risk Management Framework 1.0 (NIST AI 100-1, Jan 2023) and Generative AI Profile (NIST AI 600-1, Jul 26 2024). https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf.
- ISO/IEC 42001:2023, "Information technology — Artificial intelligence — Management system." https://www.iso.org/standard/42001.
- AWS. "AI lifecycle risk management: ISO/IEC 42001:2023 for AI governance." 2025. https://aws.amazon.com/blogs/security/ai-lifecycle-risk-management-iso-iec-420012023-for-ai-governance/.
- OWASP. "OWASP Top 10 for LLM Applications & Generative AI 2025." https://owasp.org/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-v2025.pdf.
- OWASP. "LLM01:2025 Prompt Injection." https://genai.owasp.org/llmrisk/llm01-prompt-injection/.
- OWASP. "Agentic AI — Threats and Mitigations" (Apr 2025). https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/.
- OWASP. "Top 10 for Agentic Applications." Released Dec 9 2025. https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/.
- arXiv 2504.19956. "Securing Agentic AI: A Comprehensive Threat Model and Mitigation Framework for Generative AI Agents." 2025. https://arxiv.org/pdf/2504.19956.
- arXiv 2510.02169. "TAIBOM: Bringing Trustworthiness to AI-Enabled Systems." 2025.
- arXiv 2511.12668. "AI Bill of Materials and Beyond: AI Risk Scanning (AIRS) Framework." 2025.
- Linux Foundation. "Implementing AI Bill of Materials (AI BOM) with SPDX 3.0." 2024. https://www.linuxfoundation.org/research/ai-bom.
- Mend.io. "What is an AI Bill of Materials (AI BOM)?" 2025. https://www.mend.io/blog/what-is-an-ai-bill-of-materials-ai-bom/.
- Wiz. "AI-BOMs: A Practical Guide." 2025. https://www.wiz.io/academy/ai-security/ai-bom-ai-bill-of-materials.
- Palo Alto Networks. "What Is an AI-BOM?" 2025. https://www.paloaltonetworks.com/cyberpedia/what-is-an-ai-bom.
- OpenTelemetry. "Semantic conventions for generative AI systems." https://opentelemetry.io/docs/specs/semconv/gen-ai/.
- OpenTelemetry. "Semantic Conventions for GenAI agent and framework spans." https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/.
- OpenTelemetry. "Semantic conventions for generative AI events." https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-events/.
- OpenTelemetry blog. "AI Agent Observability — Evolving Standards and Best Practices." 2025. https://opentelemetry.io/blog/2025/ai-agent-observability/.
- Datadog. "Datadog LLM Observability natively supports OpenTelemetry GenAI Semantic Conventions." 2025. https://www.datadoghq.com/blog/llm-otel-semantic-convention/.
- LangSmith / Langfuse / Arize Phoenix product documentation (general references for agent observability). Vendor sites.
- Willison, S. Commentary on "Building effective agents" (Dec 20 2024) and "How we built our multi-agent research system" (Jun 14 2025). https://simonwillison.net/.
- Huyen, C. *AI Engineering* (O'Reilly, 2024).
- Constellation Research (Larry Dignan). "Anthropic's multi-agent system overview a must read for CIOs." Jun 2025. https://www.constellationr.com/blog-news/insights/anthropics-multi-agent-system-overview-must-read-cios.
- Lares Labs. "OWASP Agentic AI Top 10: Threats in the Wild." Dec 2025. https://labs.lares.com/owasp-agentic-top-10/.
- Google Cloud. "MLOps: Continuous delivery and automation pipelines in machine learning" (Google Cloud Architecture Center, used as MLOps lineage reference for cross-cutting Measurement and CM concerns).

(All URLs accessed during research window April–May 2026 unless otherwise noted; where pages cited speculative/marketing content, claims drawn from them have been tagged [EMERGING] or omitted in favor of primary sources.)

---

### Closing note on epistemic posture
This document treats the canonical 8-phase SDLC as fixed and adds, transforms, or replaces artifacts and steps under that frame only when a primary source supports the change. Where authoritative sources disagree (notably on multi-agent systems and on eval-driven vs. error-analysis-driven development) both positions are presented and attributed. Several conventions central to current practice — `AGENTS.md`/`CLAUDE.md` interoperability, prompt-versioning schemes, A2A identity, and HITL frequency — are explicitly tagged `[EMERGING]` because no standard yet exists. Practitioners adopting this guide should expect the [EMERGING] sections to consolidate over the next 12–24 months.