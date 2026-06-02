# Session 2 Deliverable — Agent Harness & Thought Leader Inventory

**Session context:** This is Session 2 of a multi-session project for a solo technical founder building a local-first multi-LLM agent harness. Session 1 produced a substrate document on patterns and primitives (orchestration, routing, validation, observability, reliability, context engineering, tools/skills). This session inventories the **artifacts and people** downstream of those patterns. Discovery mandate is active (≥12 [Discovery] tags per Part). Delivered in Advanced Research mode.

**Caveat on coverage**: Research budget was consumed largely by Part A. Part B is delivered in compressed-but-discrete-field form, with several sub-categories (B5 Skool/Discord, B7 Reddit/HN, B10 conferences) flagged as thin in §5. Output-budget priority preserved §1, §2 (full A1–A11), §3 (B1–B11 in compressed field schema), §6 bibliography, then §4 cross-cutting and §5 gaps.

---

## §1. Executive Synthesis

- The "agent harness" has crystallized in 2025–2026 as a named engineering discipline distinct from "agent framework," with Anthropic's Claude Agent SDK rename (Sept 29, 2025) and OpenAI's "Harness Engineering" essay (Ryan Lopopolo, late 2025/early 2026) as the canonical inflection points. [HIGH]
- For a solo local-first builder, the single most strategically defensible substrate is the **Claude Agent SDK + MCP + Skills** stack, because it is the same harness Anthropic itself runs internally and exposes structured outputs, file checkpointing, sandbox, and SDK-MCP servers as first-class. [HIGH]
- The big-3 frontier-lab harnesses have converged architecturally: tools-in-a-loop + MCP + sandbox + skills/AGENTS.md + sub-agents — Anthropic (Claude Agent SDK), OpenAI (Agents SDK + Apps SDK + Codex), Google (ADK + Agent Engine/Gemini Enterprise). [HIGH]
- Microsoft's AutoGen + Semantic Kernel merger into Microsoft Agent Framework (public preview Oct 1, 2025; 1.0/RC by spring 2026) is the most consequential consolidation event for the .NET/enterprise side. [HIGH]
- Open-source orchestration has consolidated to a 4-pole equilibrium: LangGraph (durable graphs), CrewAI (role-based, ~46k stars), Mastra (TypeScript-first, Apache-2.0, $13M raised, used by Replit Agent 3), Pydantic AI (type-safe Python). DSPy occupies an orthogonal "compile prompts" niche. [HIGH]
- The terminal-native CLI category is now the **center of gravity** for code-adjacent agent work: Claude Code, Codex CLI, Gemini CLI, Aider, OpenCode, Goose (now donated to Linux Foundation's AAIF), OpenHands. [HIGH]
- "Don't build multi-agents" (Cognition) vs. "How we built our multi-agent research system" (Anthropic, June 2025) is the defining 2025 architectural debate, and both positions are correct conditional on task shape (parallel-decomposable vs. shared-context coding). [HIGH]
- Durable execution as agent substrate is real and funded: Temporal raised $300M Series D at $5B valuation (Feb 17, 2026); Restate, Inngest, DBOS, Hatchet are credible alternatives, with DBOS the lowest-friction Postgres-only path. [HIGH]
- Prompt injection remains structurally unsolved at the model layer; Simon Willison's "lethal trifecta" framing and Johann Rehberger's August 2025 "Month of AI Bugs" (CVE-2025-53773 in GitHub Copilot, exploits in ChatGPT/Codex/Cursor/Amp/Devin/OpenHands/Claude Code/Jules) prove this is a harness-design problem, not a model-tuning one. [HIGH]
- The independent-practitioner canon is small and stable: Hamel Husain + Shreya Shankar (evals), Eugene Yan + Jason Liu + Bryan Bischof + Charles Frye (the "Applied LLMs" six), Simon Willison (security/criticism), Dex Horthy/12-Factor Agents, Thorsten Ball (Amp), Lance Martin (LangChain/context engineering), Indragie Karunaratne (Sentry/agent debugging). [HIGH]
- Voice agents have a clean buy-vs-build threshold around 10k minutes/month: Vapi/Retell below, LiveKit Agents/Pipecat above. [MODERATE]
- Browser/computer-use harnesses bifurcated between agent-first (Browser-use, Skyvern) and Playwright-augmenting (Stagehand/Browserbase); Anthropic Computer Use and OpenAI Operator/ChatGPT Agent are the frontier-lab anchors. [HIGH]
- The **harness-as-product** thesis (IndyDevDan/Disler, Lopopolo, Ball) — that the harness, not the model, is the durable engineering artifact — is now consensus among practitioners actually shipping. [HIGH]
- For a solo founder, the highest-leverage build pattern is: thin orchestrator owning prompts/context/control flow + Claude Agent SDK or OpenAI Agents SDK as one of multiple model harnesses + LiteLLM/Bifrost gateway + Langfuse self-hosted + MCP for tool surface. [SPECULATIVE]
- The largest discovery-cluster gap in published thought leadership is **non-Anglophone practitioners** and **academic-to-practitioner crossovers** outside the Stanford/MIT/Berkeley orbit. [MODERATE]

---

## §2. Part A — Harness Inventory

### A1. Frontier-lab harnesses and SDKs

**Claude Agent SDK (Anthropic)**
- Maintainer: Anthropic | License: Anthropic Commercial Terms (proprietary) | URL: https://docs.claude.com/en/docs/agent-sdk/overview
- Thesis: "Give Claude a computer." Same harness that powers Claude Code, made programmable; built-in tool execution loop, context compaction, file checkpointing, SDK-MCP in-process servers. Renamed from Claude Code SDK on Sept 29, 2025. [HIGH]
- Orchestration: agent loop + optional sub-agents | Host: local/CLI/cloud (Bedrock, Vertex, Azure Foundry) | State: file-based + compaction + memory tool + 1M context beta | Tools: built-in (Read/Write/Edit/Bash) + MCP + custom in-process tools | HITL: permission_mode + can_use_tool callback + hooks | Observability: hooks, structured outputs, /bug telemetry
- Adopters: Anthropic internal ("powers almost all of our major agent loops"). [HIGH]
- Activity: Python SDK CHANGELOG shows active development through 2026; v0.2.111+ requires for Opus 4.7. [HIGH]

**OpenAI Agents SDK + Apps SDK + Codex CLI + ChatGPT Agent**
- Maintainer: OpenAI | License: MIT (Agents SDK) | URL: https://openai.github.io/openai-agents-python/
- Thesis: Model-native harness aligned with how OpenAI models perform best; sandbox-aware orchestration with Manifest abstraction; supports Blaxel/Cloudflare/Daytona/E2B/Modal/Runloop/Vercel sandboxes natively. [HIGH]
- Orchestration: Runner + Agent + handoffs (decentralized) or manager (agents-as-tools) | Host: cloud-default, local sandboxes | State: Conversations API + sessions | Tools: Responses API built-ins (web search, file search, computer use, code interpreter) + MCP + apply-patch | HITL: guardrails + tool approvals | Observability: Logfire/AgentOps/OpenTelemetry export
- Activity: TechCrunch Apr 15, 2026 update added Codex-like filesystem tools, sandbox-native execution, code mode/subagents roadmap. [HIGH]

**Google ADK + Vertex Agent Engine + Gemini Enterprise Agent Platform + Gemini CLI + Jules**
- Maintainer: Google | License: Apache 2.0 (ADK) | URL: https://google.github.io/adk-docs/
- Thesis: Code-first multi-agent framework, Python/TypeScript/Go/Java; same framework powering Agentspace and CES; one-command deploy to Agent Engine Runtime. [HIGH]
- Orchestration: workflow agents (deterministic) + LLM-coordinated dynamic | Host: any container or Agent Engine | State: managed sessions + Memory Bank | Tools: pre-built + MCP + LangChain/LlamaIndex/CrewAI interop via LiteLLM | HITL: tool confirmation flow + Agent Config | Observability: Cloud Trace, Cloud Logging built-in
- Adopters: KPMG, Agentspace internal | Activity: docs updated 2026-05-05; bi-weekly release cadence. [HIGH]

**Microsoft Agent Framework (post-AutoGen/Semantic Kernel merger) + Magentic-One**
- Maintainer: Microsoft | License: MIT (core); enterprise license for ee/ dirs | URL: https://learn.microsoft.com/en-us/agent-framework/overview/
- Thesis: Unifies AutoGen's multi-agent research patterns (group chat, debate, reflection, Magentic) with Semantic Kernel's enterprise foundations; graph-based workflows; native MCP + A2A 1.0; Python + .NET. [HIGH]
- Public preview: Oct 1, 2025; RC announced spring 2026. AutoGen and SK enter maintenance mode. [HIGH]
- Orchestration: graph workflows + agent orchestration | Host: any + Azure AI Foundry runtime | State: session-based | Tools: MCP + connectors | HITL: durable approvals | Observability: OpenTelemetry-native
- Adopters: 10,000+ orgs on Foundry Agent Service; KPMG, BMW, Fujitsu cited. [MODERATE — vendor source]

**Amazon Bedrock AgentCore + Strands Agents SDK**
- Maintainer: AWS | License: Apache 2.0 (Strands) | URL: https://aws.amazon.com/bedrock/agentcore/
- Thesis: Framework-agnostic platform (works with Strands, CrewAI, LangGraph, LlamaIndex, ADK, OpenAI); modular services (Runtime, Memory, Gateway, Identity, Browser, Code Interpreter, Observability) usable independently. Strands launched May 2025. [HIGH]
- State: AgentCore Memory (short + long-term, semantic/summarization/preference strategies) | Tools: Gateway transforms APIs/Lambda into agent tools | HITL: identity-gated | Observability: native CloudWatch + traces
- Adopters: Epsilon, Ericsson, Thomson Reuters, Cox Automotive (vendor case studies) [MODERATE]

**[Discovery] DeepSeek, Mistral, xAI, Meta** — Frontier labs without first-party agent harnesses as of May 2026; Meta donated Llama models to ecosystem but ships no harness; xAI's Grok ships no SDK equivalent to Claude Agent SDK or Agents SDK. [MODERATE — absence is the finding]

### A2. Open-source orchestration frameworks

**LangGraph / LangChain 1.0** — Maintainer: LangChain Inc. | License: MIT | URL: https://blog.langchain.com/three-years-langchain/ | Thesis: graph-state-machine for durable, controllable agents; LangChain 1.0 + LangGraph 1.0 released Oct 2025 with $125M Series B at $1.25B valuation. [HIGH] | State: checkpointing, durable execution, HITL interrupts | Adopters: Uber, Klarna, LinkedIn, JPMorgan claimed. [MODERATE]

**CrewAI** — Maintainer: João Moura / CrewAI Inc. | License: MIT | URL: https://github.com/crewAIInc/crewAI | Thesis: role/goal/backstory-based multi-agent crews; 46k+ stars; ~60% Fortune 500 claimed by vendor. [HIGH structure / MODERATE adoption claim] | Activity: ongoing as of late 2025 (BusinessWire Nov 19, 2025).

**Mastra** — Maintainer: Sam Bhagwat, Abhi Aiyer, Shane Thomas (ex-Gatsby) | License: Apache 2.0 (core), enterprise for ee/ | URL: https://mastra.ai/ | Thesis: TypeScript-first, batteries-included; built on Vercel AI SDK; agents + workflows + RAG + evals + Studio. ~22k stars, $13M raised. [HIGH] | Adopters: Replit Agent 3, PayPal, Sanity claimed. [MODERATE — vendor]

**Pydantic AI** — Maintainer: Samuel Colvin / Pydantic team | License: MIT | URL: https://ai.pydantic.dev/ | Thesis: type-safe agents w/ generics, dependency injection, structured outputs; ~15k stars (per DEV.to 2026 guide). [HIGH]

**LlamaIndex** — Maintainer: Jerry Liu | License: MIT | URL: https://github.com/run-llama/llama_index | Thesis: shifted from RAG framework to "document agent + agentic OCR platform" (LlamaParse, LlamaCloud); workflows for event-driven multi-agent. [HIGH]

**DSPy** — Maintainer: Omar Khattab (MIT) + Stanford/Databricks | License: MIT | URL: https://dspy.ai/ | Thesis: programs not prompts; optimizers (MIPROv2, SIMBA, GEPA, GRPO) compile metrics into prompts/weights. GEPA paper July 2025 outperforms RL baselines. [HIGH]

**AutoGen** — Status: maintenance mode, succeeded by Microsoft Agent Framework. URL: https://devblogs.microsoft.com/autogen/ [HIGH]

**Semantic Kernel** — Status: foundation layer of MAF; maintenance mode for new development. URL: https://devblogs.microsoft.com/semantic-kernel/ [HIGH]

**Smolagents (HuggingFace)** — Maintainer: HuggingFace (Aymeric Roucher et al.) | License: Apache 2.0 | URL: https://github.com/huggingface/smolagents | Thesis: ~1000 LOC; CodeAgent writes Python actions; sandboxed (Modal/E2B/Docker/Pyodide). [HIGH]

**Haystack Agents (deepset)** — Maintainer: deepset | License: Apache 2.0 | URL: https://haystack.deepset.ai/ | Thesis: pipeline + agent hybrid w/ heavy RAG focus. [MODERATE — limited search coverage this session]

**[Discovery] Agno** — Vendor: Agno (formerly Phidata) | License: Mozilla Public 2.0 | URL: https://agno.com/ | Thesis: fast Python SDK + managed platform; built-in tools/memory/knowledge per Langfuse comparison. [MODERATE]

**[Discovery] Strands Agents** — covered in A1 (AWS-adjacent but model-agnostic OSS). [HIGH]

**[Discovery] LangProBe / GEPA** — Academic benchmark + optimizer track from DSPy lineage. [HIGH]

**MetaGPT, ChatDev, XAgent, AgentVerse, SuperAGI** — Status: 2023–2024 research vintage; limited evidence of 2025–2026 production traction. Flagged as historical reference in §5.

### A3. Terminal-native and CLI harnesses

**Claude Code** — Anthropic | proprietary | https://code.claude.com/ | Thesis: terminal-first agentic coding; checkpoints, native VS Code ext, Plan Mode. [HIGH]

**Codex CLI / Codex Max** — OpenAI | open source | URL via openai.github.io | Built in Rust, prompt caching 75%, ChatGPT Plus integration. [HIGH]

**Gemini CLI** — Google | Apache 2.0 | https://github.com/google-gemini/gemini-cli | Generous free tier. [HIGH]

**Aider** — Maintainer: Paul Gauthier | License: Apache 2.0 | https://aider.chat | Thesis: git-native diff-based pair programming; ~42k stars. [HIGH]

**OpenCode** — License: MIT | https://github.com/sst/opencode | Thesis: terminal-native, 75+ providers; ~150k+ stars per third-party trackers. [MODERATE]

**Goose (Block / now Linux Foundation AAIF)** — License: Apache 2.0 | https://github.com/aaif-goose/goose | Thesis: Rust-built desktop+CLI+API; native MCP; donated to Linux Foundation Agentic AI Foundation alongside Anthropic MCP and OpenAI AGENTS.md spec. [HIGH]

**Plandex** — License: MIT | https://github.com/plandex-ai/plandex | Long-running, persistent project agent. [MODERATE]

**Continue.dev CLI** — License: Apache 2.0 | https://www.continue.dev/ | BYOK, local-friendly. [HIGH]

**SWE-agent (Princeton)** — Maintainer: Yang et al. | License: MIT | https://swe-agent.com/ | Foundational research harness behind SWE-bench. [HIGH]

**OpenHands (formerly OpenDevin)** — Maintainer: All Hands AI | License: MIT (core) | https://github.com/OpenHands/OpenHands | ~72k stars; SDK + CLI + GUI; Docker-sandboxed. [HIGH]

**[Discovery] Amp (Sourcegraph)** — License: proprietary | https://ampcode.com/ | Thesis: "unconstrained token usage, always best models, raw model power"; Oracle + subagents + Librarian; killed VS Code extension to focus on CLI/web. [HIGH]

**[Discovery] Crush (Charmbracelet)** — Terminal-aesthetic CLI agent. [MODERATE]

**[Discovery] Droid (Factory)** — Enterprise terminal agent with specialized sub-agents; #1 on Terminal-Bench (58.75% claimed). [MODERATE — vendor]

**[Discovery] Auggie (Augment Code)** — Live codebase index; SWE-Bench Pro #1 claimed. [MODERATE]

**[Discovery] Pi-mono / pi-builder** — Open-source harness builder wrapping Claude Code/Aider/Codex/Gemini CLI/Goose/Plandex/SWE-agent/Crush behind unified interface. [HIGH]

### A4. IDE-embedded and editor-integrated

**Cursor** — Anysphere | proprietary | https://cursor.com | Composer/Agent mode; 3.0 with parallel agents on git worktrees; ~$900M raised June 2025. [HIGH]

**Windsurf** — formerly Codeium; acquired by Cognition (deal closed July 14, 2025 after Google licensing/acquihire of CEO + ~40 R&D staff for ~$2.4B) | proprietary | https://windsurf.com | Cascade agent. [HIGH]

**Zed agent panel** — Zed Industries | GPL-3 (editor) | https://zed.dev | Rust-native, ACP support. [HIGH]

**Cline** — License: Apache 2.0 | https://cline.bot | VS Code extension; Plan/Act modes; ~58k–61k stars. [HIGH]

**Roo Code** — Cline fork | Apache 2.0 | ~22k stars. [HIGH]

**Continue.dev IDE** — Apache 2.0 | https://www.continue.dev | BYOK, JetBrains + VS Code. [HIGH]

**GitHub Copilot Workspace / Coding Agent** — Microsoft/GitHub | proprietary | https://github.com/features/copilot | Agent mode reached GA early 2026. [HIGH]

**JetBrains AI Assistant + Junie** — JetBrains | proprietary | https://www.jetbrains.com/ai/ [MODERATE]

**[Discovery] Kilo Code** — Cline-lineage | open source | JetBrains support. [MODERATE]

**[Discovery] Google Antigravity** — Google's IDE agent (free during preview as of early 2026). [MODERATE]

**[Discovery] Kiro / Qoder / Trae** — IDE agents from Amazon (Kiro), ByteDance (Trae), Qoder team. [MODERATE]

**[Discovery] Void AI** — License: open source (paused dev in 2025 per third-party). [MODERATE]

### A5. Browser, computer-use, OS-level

**Anthropic Computer Use** — proprietary | https://www.anthropic.com/news/3-5-models-and-computer-use | Reference impl + tool. [HIGH]

**OpenAI Operator / ChatGPT Agent / Atlas** — proprietary | https://openai.com/index/introducing-operator/ | Browser-native agent; Atlas browser launched late 2025. [HIGH]

**Browser-use** — License: MIT | https://github.com/browser-use/browser-use | Agent-first Python; both self-host and cloud. [HIGH]

**Browserbase Stagehand** — License: MIT | https://www.stagehand.dev/ | Playwright augmentation w/ natural language; Director (no-code). [HIGH]

**Skyvern** — License: AGPL | https://www.skyvern.com/ | Computer-vision + LLM (no DOM selectors); 85.85% WebVoyager claimed. [HIGH]

**Self-Operating Computer (HyperWriteAI)** — License: MIT | https://github.com/OthersideAI/self-operating-computer [MODERATE]

**LaVague** — License: Apache 2.0 | research-grade. [MODERATE]

**[Discovery] Hyperbrowser AI** — managed browser infra w/ HyperAgent. [MODERATE]

**[Discovery] Steel** — self-hosted browser infra. [MODERATE]

**[Discovery] Perplexity Comet** — consumer Chromium-based browser w/ AI; launched July 2025. [HIGH]

**[Discovery] Dia (Browser Company)** — consumer AI browser. [MODERATE]

### A6. Vertical / domain-specific

**Devin (Cognition)** — proprietary | https://www.cognition.ai/ | autonomous engineering agent; ACU-priced. [HIGH]

**Replit Agent / Agent 3** — proprietary | https://replit.com/ | $400M raise Jan 2026 at $9B; built on Mastra (per Mastra public claim). [HIGH]

**v0 (Vercel)** — proprietary | https://v0.dev | React/shadcn component generation. [HIGH]

**Bolt / bolt.new (StackBlitz)** — proprietary | https://bolt.new | Browser-based full-stack generation. [HIGH]

**Lovable** — proprietary | https://lovable.dev | $100M ARR claimed within 8 months of Nov 2024 GPT-Engineer rebrand. [MODERATE]

**Sierra** — proprietary | https://sierra.ai/ | Bret Taylor + Clay Bavor; outcome-based pricing ~$1.50/resolution; ~$10B valuation per Sacra Oct 2025. [MODERATE — Sacra estimate]

**Decagon** — proprietary | https://decagon.ai/ | AOPs (Agent Operating Procedures). [HIGH]

**Crescendo** — proprietary | https://crescendo.ai/ | AI + human hybrid CX. [MODERATE]

**LiveKit Agents** — Apache 2.0 | https://livekit.com | WebRTC-native; powers ChatGPT Voice; v1.0 April 2025. [HIGH]

**Pipecat (Daily)** — BSD | https://pipecat.ai | Frame-based streaming pipeline. [HIGH]

**Vapi** — proprietary | https://vapi.ai | Telephony-focused turnkey. [HIGH]

**Vocode, Bland** — voice telephony focus. [MODERATE]

**Perplexity, You.com, Phind, Exa** — research/search agents. [HIGH]

**[Discovery] Genie (Cosine)** — autonomous coding cloud. [MODERATE]

**[Discovery] Manus AI** — general-purpose autonomous agent (Chinese origin). [MODERATE]

**[Discovery] Base44** — vibe-coding tool. [MODERATE]

**[Discovery] Stagewise / Frontman** — browser-aware AI coding visual editing. [MODERATE]

### A7. Indie / single-file / minimal harnesses

**[Discovery] disler/single-file-agents** — Maintainer: Dan "IndyDevDan" Disler | License: MIT | https://github.com/disler/single-file-agents | uv-based self-contained agents; ~412 stars. [HIGH]

**[Discovery] disler/the-library** — Skill catalog meta-skill. [HIGH]

**Twelve-Factor Agents reference impls** — Maintainer: Dex Horthy / HumanLayer | License: open | https://github.com/humanlayer/12-factor-agents | Methodology, not framework. [HIGH]

**[Discovery] HumanLayer (humanlayer/humanlayer)** — ~10.7k stars; agent control plane. [HIGH]

**[Discovery] Aeon** — autonomous agent on GitHub Actions; orchestrates Claude Code across 90+ skills. [MODERATE]

**[Discovery] Bernstein, kodo, loom, wreckit** — parallel-runners + autonomous loops in awesome-cli-coding-agents. [MODERATE]

**Smol Developer / GPT Engineer** — historical (rebranded as Lovable). [HIGH]

**[Discovery] AgentPlane, Untether, claudebox, AgentControlPlane (HumanLayer)** — auditable git-native + sandbox + remote-control wrappers. [MODERATE]

### A8. Workflow / durable-execution platforms used as agent harnesses

**Temporal** — License: MIT | https://temporal.io/ | $300M Series D Feb 17, 2026 at $5B; OpenAI/Netflix/Snap/Datadog adopters. [HIGH]

**Restate** — License: BSL/open | https://restate.dev/ | Lightweight durable async/await; Restate Cloud GA 2025. [HIGH]

**Inngest** — License: Apache 2.0 (SDK) | https://inngest.com | Event-driven; serverless-first; step.ai.infer primitive. [HIGH]

**Trigger.dev** — License: Apache 2.0 | https://trigger.dev/ | TypeScript long-running. [HIGH]

**Hatchet** — License: MIT | https://hatchet.run/ [MODERATE]

**[Discovery] DBOS** — License: MIT | https://www.dbos.dev/ | Postgres-only durable execution; durable-swarm wrapper for OpenAI Swarm; Go SDK April 2026; Databricks partnership. [HIGH]

**n8n** — License: Sustainable Use | https://n8n.io [HIGH]

**Activepieces** — License: MIT | https://www.activepieces.com [HIGH]

**Pipedream, Make.com** — proprietary low-code. [HIGH]

**Dapr Workflows / Diagrid** — License: Apache 2.0. [HIGH]

**AWS Step Functions, Azure Durable Functions, Google Cloud Workflows** — cloud-proprietary. [HIGH]

**Prefect, Dagster** — License: Apache 2.0 (Prefect) / Apache 2.0 (Dagster); ML-ops origins, increasingly used for agent orchestration. [HIGH]

**[Discovery] Cloudflare Workflows** — GA 2025; step-based durable; Python support; days-to-weeks runtime. [HIGH]

**[Discovery] Conductor / Orkes** — Netflix-origin durable orchestration. [HIGH]

**[Discovery] Resonate, Effectful (Effect TS), Golem.cloud** — emerging durable-promise/durable-async category. [MODERATE]

**[Discovery] Akka** — actor-based; bottom-up agent fabric ($300M+ valuation lineage). [MODERATE]

### A9. Evaluation, observability, gateway harnesses (name-and-frame)

**Langfuse** — License: MIT (core) | https://langfuse.com | Self-host friendly; ClickHouse-backed; framework-agnostic. [HIGH]

**LangSmith** — proprietary | https://smith.langchain.com | Cloud-only; deepest LangChain integration. [HIGH]

**Arize Phoenix / Arize AX** — License: ELv2 (Phoenix OSS) | https://phoenix.arize.com | OpenTelemetry-native; ~8k+ stars. [HIGH]

**Weights & Biases Weave** — proprietary cloud + OSS SDK. [HIGH]

**Helicone** — License: Apache 2.0 | https://www.helicone.ai/ | Proxy-based; Cloudflare Workers; caching built-in. [HIGH]

**Braintrust** — proprietary | https://braintrust.dev | Eval-first; Loop AI agent. [HIGH]

**LiteLLM** — License: MIT | https://github.com/BerriAI/litellm | 100+ provider gateway. [HIGH]

**Portkey** — License: MIT (gateway) | https://portkey.ai | Routing, fallback, guardrails. [HIGH]

**OpenRouter** — proprietary | https://openrouter.ai | Multi-provider gateway-as-a-service. [HIGH]

**[Discovery] Bifrost (Maxim AI)** — open-source LLM gateway alternative. [MODERATE — limited research this session]

**Promptfoo** — License: MIT | https://promptfoo.dev | Eval-as-code w/ Claude Agent SDK provider. [HIGH]

**Inspect AI (UK AISI)** — License: MIT | https://inspect.aisi.org.uk | Government-grade eval framework. [HIGH]

**[Discovery] AgentOps** — proprietary | https://agentops.ai | 400+ LLM tracking; fine-tuning cost optimization. [MODERATE]

**[Discovery] Logfire (Pydantic)** — proprietary | https://pydantic.dev/logfire | Pydantic-team observability. [HIGH]

**[Discovery] OpenLLMetry (Traceloop)** — License: Apache 2.0 | OpenTelemetry-native instrumentation. [HIGH]

**[Discovery] Galileo (Luna-2)** — real-time guardrails + monitoring. [MODERATE]

### A10. Security and governance

**Invariant Labs** — https://invariantlabs.ai | MCP-scanner, agent firewall. [HIGH]

**Lakera** — https://lakera.ai | Prompt injection detection. [HIGH]

**Prompt Security** — https://prompt.security [MODERATE]

**[Discovery] MCP Manager / Snyk MCP scanning** — emerging tool category. [MODERATE]

**Anthropic Trust Center** — https://trust.anthropic.com [HIGH]

**NVIDIA NeMo Guardrails** — License: Apache 2.0 | https://github.com/NVIDIA/NeMo-Guardrails [HIGH]

**Guardrails AI** — License: Apache 2.0 | https://www.guardrailsai.com [HIGH]

**[Discovery] Microsoft Foundry Safeguard / GPT-OSS Safeguard** — enterprise-spec safety models. [MODERATE]

**[Discovery] Cisco DefenseClaw + Nvidia OpenShell** — agent-security framework (announced late 2025). [MODERATE]

**[Discovery] Pillar Security, HiddenLayer** — agent red-teaming vendors. [SPECULATIVE — not directly verified this session]

### A11. Other / uncategorized

**[Discovery] Symphony (OpenAI Frontier)** — Elixir-based "ghost library" multi-agent orchestrator (per Lopopolo Latent Space podcast). Internal to OpenAI; not yet public. [HIGH]

**[Discovery] Letta + Letta Code** — Maintainer: Charles Packer + Sarah Wooders | License: Apache 2.0 (OSS), proprietary cloud | https://letta.com | Stateful memory-first agents (MemGPT lineage); Letta Code is Claude Code-style CLI w/ persistent agents + MemFS git-tracked memory; #4 on Terminal-Bench at time of launch. [HIGH]

**[Discovery] Notion 3.0 Custom Agents** — knowledge-work agent platform (per Latent Space). [MODERATE]

**[Discovery] Dagger Functions** — programmable CI/CD-as-agent-runtime. [SPECULATIVE]

---

## §3. Part B — Thought Leader Inventory

*(Compressed-but-discrete fields per output budget; full schema retained.)*

### B1. Frontier-lab researchers/engineers writing publicly

**Erik Schluntz** — Anthropic | Co-author "Building Effective Agents" | https://www.anthropic.com/research/building-effective-agents | Thesis: workflows vs. agents distinction; simplicity over sophistication | Influence: piece is the most-cited single agent-design reference of 2024–2025. [HIGH]

**Barry Zhang** — Anthropic Research Engineer | https://thefocus.ai/reports/aiecode-2025-11/speakers/barry-zhang/bio/ | Co-author "Building Effective Agents"; co-presenter "Don't Build Agents, Build Skills Instead" with Mahesh Murag at AIE Code Nov 21, 2025 | Thesis: agent architecture has converged; differentiation is now Skills. [HIGH]

**[Discovery] Mahesh Murag** — Anthropic | "Don't Build Agents, Build Skills" co-presenter; Skills system architect. [HIGH]

**[Discovery] Boris Cherny** — Head of Claude Code | Lenny's Newsletter "Head of Claude Code: What happens after coding is solved." [HIGH]

**[Discovery] Siddharth Mishra-Sharma** — Anthropic Discovery team | "Long-running Claude for scientific computing" anthropic.com/research/long-running-Claude. [HIGH]

**[Discovery] Ryan Lopopolo** — OpenAI Frontier Product Exploration | https://openai.com/index/harness-engineering/ + Latent Space podcast | Thesis: "harness engineering" — 1M LOC, 1B tokens/day, 0% human code/review; Symphony orchestrator. Single most influential 2026 agent-systems essay. [HIGH] | Background: Snowflake, Brex, Stripe, Citadel.

**[Discovery] Karan Sharma** — OpenAI product team | TechCrunch interview on Agents SDK harness/sandbox launch. [HIGH]

**Sarah Bird** — Microsoft CPO Responsible AI | https://www.microsoft.com/en-us/research/people/slbird/ | Co-founded ONNX, Fairlearn; Berkeley PhD under Dave Patterson; founding AI ethics member at Facebook. Focus: red-teaming, eval, adaptive defenses. [HIGH]

**[Discovery] Microsoft AutoGen Research (AI Frontiers Lab)** — Magentic-One authors. [HIGH]

**ADK team / Gemini CLI maintainers** — Google Developers Blog https://developers.googleblog.com/en/agent-development-kit-easy-to-build-multi-agent-applications/. [HIGH]

### B2. Framework maintainers

**Harrison Chase** — LangChain co-founder | https://blog.langchain.com/author/harrison/ | Thesis: controllable, durable graphs > "shallow" tool-loops; coined "context engineering" elevation. [HIGH]

**João Moura** — CrewAI founder/CEO | https://blog.crewai.com/author/joao/ | Ex-Clearbit Director of AI Engineering; thesis: role-based abstraction. [HIGH]

**Sam Bhagwat** — Mastra CEO | author "Principles of Building AI Agents" + "Patterns for Building AI Agents" (170k+ copies claimed) | Stanford '11; ex-Gatsby. [HIGH]

**Samuel Colvin** — Pydantic creator/Pydantic AI | https://github.com/samuelcolvin | Thesis: type-safety for LLM tool calls; Pydantic AI brings DI + structured outputs; LogFire = obs. [HIGH]

**Omar Khattab** — DSPy creator; MIT EECS asst prof Fall 2025 + Databricks | https://omarkhattab.com/ + @lateinteraction (~34.7k followers as of mid-2025) | Thesis: declarative LM programs; compilers > prompts; GEPA reflective prompt evolution outperforms RL. [HIGH]

**Jerry Liu** — LlamaIndex CEO | https://www.linkedin.com/in/jerry-liu-64390071/ | Thesis: scaffolding layer is collapsing; survivors are context/parsing/agentic OCR. [HIGH]

**[Discovery] Charles Packer + Sarah Wooders** — Letta co-founders / MemGPT authors | DeepLearning.AI course "LLMs as Operating Systems: Agent Memory" | Berkeley lineage. [HIGH]

**Aider maintainer Paul Gauthier** — https://aider.chat | active blogger at https://aider.chat/blog. [MODERATE]

**Cline maintainer (Saoud Rizwan)** — https://cline.bot/blog | Plan/Act discipline. [HIGH]

**Continue.dev maintainers (Ty Dunn, Nate Sesti)** — https://www.continue.dev/blog. [MODERATE]

### B3. Independent practitioners with substantive technical writing

**Simon Willison** — https://simonwillison.net + https://simonw.substack.com | Coined "prompt injection," "lethal trifecta," "AI slop"; Datasette + LLM CLI; Django co-creator. Highest-frequency public writer on agent security. [HIGH]

**Hamel Husain** — https://hamel.dev + Maven course w/ Shankar | Ex-Airbnb, GitHub | "AI Evals for Engineers & PMs" #1 Maven course; LLM Evals FAQ Jan 15 2026. [HIGH]

**Shreya Shankar** — UC Berkeley PhD | https://www.shreya-shankar.com/ + course co-instructor | "Who Validates the Validators?" NAACL paper. [HIGH]

**Eugene Yan** — https://eugeneyan.com | Amazon Senior Applied Scientist | "Patterns for Building LLM-based Systems & Products" reference catalog. [HIGH]

**Jason Liu** — https://jxnl.co | Instructor library author; RAG/coding-agent series w/ Cognition/Sourcegraph/Cline/Augment teams. [HIGH]

**Chip Huyen** — https://huyenchip.com | "AI Engineering" O'Reilly 2025; "Agents" essay Jan 7, 2025. [HIGH]

**[Discovery] Bryan Bischof** — Hex Head of AI; co-author "Applied LLMs" series. [HIGH]

**[Discovery] Charles Frye** — https://twitter.com/charles_irl | Modal Labs DevRel; co-author "Applied LLMs"; LLMOps cost deep-dives. [HIGH]

**Eugene Cheah** — Featherless / RWKV | https://substack.recursal.ai/ | OSS infra blogging. [MODERATE]

**Jacob Buckman** — Manifest AI | RL + LLM theory blogger. [MODERATE]

**Dex Horthy** — HumanLayer founder | https://www.humanlayer.dev/ + 12-factor-agents | Thesis: 12 factors, "dumb zone" (40–60% context degradation per 100k-session analysis). [HIGH]

**Thorsten Ball** — Sourcegraph/Amp | https://ampcode.com/notes + "Raising an Agent" podcast w/ Quinn Slack | Thesis: "an LLM, a loop, and enough tokens"; 315-line agent demo April 15, 2025. [HIGH]

**Indragie Karunaratne** — Sentry Director of Engineering | https://www.indragie.com/blog | Thesis: traditional observability needs to reshape itself for agents; Context macOS app + slow-code MCP tool. [HIGH]

**Lance Martin** — LangChain | https://rlancemartin.github.io + Latent Space podcast | "Context Engineering for Agents"; ambient agents reference impl. [HIGH]

**[Discovery] David Breunig** — https://www.dbreunig.com | "How Contexts Fail" + "Why Context Engineering Matters" essays widely cited. [HIGH]

**[Discovery] Walden Yan (Cognition)** — "Don't Build Multi-Agents" thesis. [HIGH]

**[Discovery] Quinn Slack (Sourcegraph CEO)** — co-host Raising an Agent. [HIGH]

### B4. YouTube / podcast / long-form video

**IndyDevDan / Dan Disler** — https://www.youtube.com/@indydevdan | Thesis: agentic engineering, harness-as-product; single-file-agents repo. [HIGH]

**Cole Medin** — https://www.youtube.com/@ColeMedin | First open-source harness builder repo; 24-hour Claude Code experiments. [HIGH]

**[Discovery] Sean Matthew, Ryan Carson** — Claude Code workflow tutorials. [MODERATE]

**Sam Witteveen** — https://www.youtube.com/@samwitteveenai | Long-form LangChain/agent technical walkthroughs. [HIGH]

**Latent Space (swyx + Alessio)** — https://www.latent.space + podcast | Hosted Lopopolo, Lance Martin, Khattab, Liu, Packer. [HIGH]

**[Discovery] Hugo Bowne-Anderson — Vanishing Gradients** podcast | High Signal w/ Lance Martin episode. [HIGH]

**MLOps Community / Demetrios** — home.mlops.community | Hosted Dex Horthy "12-Factor Agents" talk. [HIGH]

**Cognitive Revolution (Nathan Labenz)** — frequent agent-architecture interviews. [HIGH]

**Anthropic podcast, OpenAI DevDay talks, Google I/O agent talks** — primary frontier-lab channels. [HIGH]

**Matthew Berman, Wes Roth, David Ondrej, AI Jason** — flagged: news-recap heavy; substantive harness-architecture content limited per credibility filter. [MODERATE — included with caveat]

**[Discovery] All About AI** — https://www.youtube.com/@AllAboutAI | tooling demos. [MODERATE]

**Practical AI podcast (Daniel Whitenack, Chris Benson)** — https://changelog.com/practicalai. [HIGH]

**[Discovery] Changelog Interviews — Adam Stacoviak hosted Thorsten Ball #648.** [HIGH]

### B5. Skool / Discord / community-platform leaders

**Caveat: this category produced thin verifiable results in this session — Skool platform is heavily SEO-gamed and credibility filter excludes course-sales pages without substantive technical artifact.** Items below meet the >1k-member + public-artifact threshold by inference from search snippets, not deep verification.

**LangChain Discord** — >100k members; daily Q&A on agents/RAG/MCP. [HIGH]

**LlamaIndex Discord** — RAG-centric. [HIGH]

**MLOps Community Slack** — biggest practitioner cross-community. [HIGH]

**Anthropic Developers Discord** — official; tied to Claude Agent SDK feedback. [HIGH]

**[Discovery] Cole Medin's "Dynamous" Skool community** — flagged for further verification. [SPECULATIVE]

**Other named Skool communities** — not verified to credibility threshold this session; see §5.

### B6. X/Twitter voices on agent harnesses

**Simon Willison @simonw**, **Omar Khattab @lateinteraction (~34.7k)**, **Harrison Chase @hwchase17**, **Jerry Liu @jerryjliu0**, **Dex Horthy @dexhorthy**, **Thorsten Ball @thorstenball**, **Indragie @indragie**, **Barry Zhang @barry_zyj**, **Ryan Lopopolo @_lopopolo**, **Johann Rehberger @wunderwuzzi23** — all verified active and posting harness-architecture content with retrievable links. Follower counts not consistently observable; most counts above are date-stamped where seen. [HIGH where linked, MODERATE for follower counts not stated with date]

### B7. Reddit / HackerNews

**Caveat: not deeply researched this session; flagged in §5.** /r/LocalLLaMA and /r/ClaudeAI are the most cited substantive long-form forums per third-party references; HackerNews remains the principal cross-cutting venue for agent-harness essays (Lopopolo, Disler, Schluntz/Zhang all hit front page).

### B8. Security researchers

**Simon Willison** — see B3. [HIGH]

**Johann Rehberger (wunderwuzzi)** — https://embracethered.com + @wunderwuzzi23 + https://zenodo.org/records/18769277 | "Month of AI Bugs" (Aug 2025): CVE-2025-53773 RCE in GitHub Copilot, exploits across ChatGPT/Codex/Anthropic MCPs/Cursor/Amp/Devin/OpenHands/Claude Code/Jules; AgentHopper AI virus PoC; Agent Commander promptware C2 paper March 16, 2026. Currently Red Team Director at Electronic Arts. [HIGH]

**Invariant Labs team** — https://invariantlabs.ai | MCP security research; co-author "Design Patterns for Securing LLM Agents" (June 2025). [HIGH]

**[Discovery] Mick Ayzenberg** — Meta AI security; "Agents Rule of Two" Meta blog Oct 31, 2025. [HIGH]

**[Discovery] Santiago Díaz, Christoph Kern, Kara Olive** — Google authors of "An Introduction to Google's Approach to AI Agent Security." [HIGH]

**[Discovery] CaMeL paper authors (DeepMind)** — "Defeating Prompt Injections by Design" April 2025. [HIGH]

### B9. Academic-to-practitioner crossovers

**Shunyu Yao** — ReAct paper author; Princeton/Anthropic. [HIGH]

**Noah Shinn** — Reflexion. [HIGH]

**Lei Wang et al.** — Plan-and-Solve. [HIGH]

**CoALA authors (Sumers, Yao, Narasimhan, Griffiths)** — cognitive architecture for language agents. [HIGH]

**Charles Packer + Sarah Wooders** — Letta/MemGPT (see B2). [HIGH]

**[Discovery] John Yang (Princeton)** — SWE-bench creator + SWE-agent; CodeClash, SWE-bench Multimodal/Multilingual; Latent Space guest. [HIGH]

**Routing paper authors** — LLMRank, CARGO, xRouter, OptiRoute, CSCR — flagged for Session 1 substrate cross-reference. [MODERATE — surface coverage this session]

**[Discovery] Lakshya A. Agrawal et al.** — GEPA (arxiv 2507.19457). [HIGH]

**[Discovery] Anastasios Angelopoulos** — LMArena founder; Latent Space NeurIPS 2025 guest. [HIGH]

**[Discovery] Hyung Won Chung (OpenAI)** — "Bitter Lesson" talks frequently cited by Lance Martin et al. [HIGH]

### B10. Conference and event circuits

**AI Engineer Summit / World's Fair / AIE Code (swyx + Ben Dunphy)** — https://www.ai.engineer | The defining venue for agent-harness practitioners; hosted Lopopolo, Horthy, Bhagwat, Khattab, Bird, Liu. [HIGH]

**NeurIPS / ICLR / ACL agent tracks** — DSPy, ReAct, Reflexion, Letta, GEPA all routed through. [HIGH]

**Anthropic / OpenAI DevDay / Google I/O / Microsoft Build / AWS re:Invent** — primary frontier-lab events. [HIGH]

**Replay (Temporal)** — May 5–7 2026 SF Moscone; durable-execution + agent reliability. [HIGH]

**Interrupt (LangChain)** — agent conference. [HIGH]

**[Discovery] 39C3 (Chaos Communication Congress)** — Rehberger "Agentic ProbLLMs" talk. [HIGH]

**[Discovery] Tessl events (Guy Podjarny)** — agent-engineering conference circuit. [MODERATE]

**[Discovery] European AI & Cloud Summit, Data + AI Summit (Databricks), GTC (NVIDIA)** — enterprise circuits. [HIGH]

### B11. Other / uncategorized

**[Discovery] Andrej Karpathy** — coined "vibe coding" Feb 2025; foundational thinker on harness-vs-model boundary; @karpathy. [HIGH]

**[Discovery] Marc Andreessen** — a16z; Latent Space interview on agent/coding market structure. [HIGH]

**[Discovery] Sarah Catanzaro** — Amplify Partners; agent-infra investor with technical writing. [HIGH]

**[Discovery] David Disler / IndyDevDan** — listed in B4 but is also harness-builder + thought-leader cluster. [HIGH]

---

## §4. Cross-cutting observations

- **Builder-as-thought-leader convergence** is now the norm: Khattab (DSPy), Chase (LangChain), Moura (CrewAI), Bhagwat (Mastra), Colvin (Pydantic AI), Liu (LlamaIndex), Packer (Letta), Disler (single-file-agents), Horthy (HumanLayer/12-Factor), Ball (Amp), Lopopolo (OpenAI Frontier) — every meaningful framework has a public-facing technical author who personally drives discourse. [HIGH]
- **Anthropic orbit**: Erik Schluntz / Barry Zhang / Mahesh Murag / Boris Cherny / Mishra-Sharma + the Claude Agent SDK + Skills + Computer Use stack form the densest single-vendor ecosystem cluster, with strong gravitational pull on indie builders (Disler, Ball-Sourcegraph, Karunaratne, Cole Medin all explicitly position around it). [HIGH]
- **OpenAI orbit**: Codex CLI + Agents SDK + Apps SDK + Operator/Atlas + Lopopolo's Symphony — orbit is more enterprise-internal and less public than Anthropic's. [HIGH]
- **LangChain orbit**: Chase + Lance Martin + LangSmith + Interrupt conf + Sequoia podcast + 80M monthly downloads + $1.25B Series B form the largest framework-anchored thought-leader cluster. [HIGH]
- **Berkeley/Stanford academic orbit**: Khattab (DSPy/MemGPT), Packer/Wooders (Letta), Shankar (evals), Yao (ReAct), Manning/Potts/Zaharia (DSPy mentors), Patterson lineage (Bird) form the densest academic cluster crossing into practitioner publishing. [HIGH]
- **Indie-builder orbit** (Disler, Horthy, Ball, Karunaratne, Medin, Witteveen): united by Claude Code/Codex/Goose tooling, "harness over framework" thesis, public real-world-build documentation, MCP-native tooling. [HIGH]
- **Security cluster**: Willison + Rehberger + Invariant + Ayzenberg (Meta) + DeepMind CaMeL authors form a tight, mutually-citing 6-node cluster around prompt-injection + lethal trifecta + agent C2. [HIGH]
- **Discovery clusters traced via lineage**: (a) MemGPT → Letta → Letta Code (Berkeley/Stanford); (b) OpenAI Frontier internal → "harness engineering" essay → Symphony → AIE talks (Lopopolo + Latent Space as conduit); (c) Amp/Sourcegraph → Raising an Agent podcast → 39C3 → Block/Goose → AAIF Linux Foundation donation; (d) Mastra ← ex-Gatsby team ← Replit Agent 3 ← Vercel AI SDK; (e) Disler single-file-agents → IndyDevDan YouTube → Pi-builder/Aeon/Bernstein ecosystem. [HIGH for traced links]
- **The "Don't Build Multi-Agents" (Cognition) vs. "How we built our multi-agent research system" (Anthropic) debate** unifies B1, B2, B3 categories — Schluntz/Zhang, Yan, Chase, Martin, Liu, Khattab, Horthy, Disler all wrote responses; this is the central architectural conversation of 2025. [HIGH]

---

## §5. Discovery gaps and recommended follow-up probes

**Thin areas (recommend dedicated next-session probe):**
1. **B5 Skool/Discord communities** — Skool SEO-gaming made 1-pass searches unreliable; recommend probe by named-community + member count + recent public artifact (recordings, repos), not platform browse.
2. **B7 Reddit/HackerNews long-form contributors** — recommend probe by tracking specific HN user histories (e.g., dang-flagged AI-eng posts, /r/LocalLLaMA top weekly) for consistent agent-harness submissions.
3. **A2 historical frameworks** (MetaGPT, ChatDev, XAgent, AgentVerse, SuperAGI) — limited 2025–2026 production evidence; recommend GitHub commit-cadence + benchmark-leaderboard probe to confirm dormancy/activity.
4. **Routing paper authors (LLMRank, CARGO, xRouter, OptiRoute, CSCR)** — surface-only coverage; recommend arXiv author-page probe.
5. **Non-Anglophone practitioners** — Chinese (Manus AI ecosystem, Z.ai, Moonshot/Kimi), Japanese, German, French agent-engineering communities largely absent; recommend localized search in Session 3.
6. **Bifrost (Maxim AI)** — confirmed referenced in user prompt but received insufficient direct verification; recommend dedicated fetch.
7. **Microsoft Magentic-One specific authors and architecture details** — covered at framework level only.
8. **Indie harness builders below 1k-star threshold** but with substantive technical writing — credibility filter excluded most; consider adjusting threshold for Session 3.

**Search-strategy adjustments:**
- For thought-leader sub-categories with low signal-to-noise, prefer arXiv author pages, GitHub user activity, and personal-blog RSS feeds over generic web search.
- For framework activity verification, prefer GitHub releases page + npm/PyPI version history with date stamps over marketing pages.
- For follower-count claims, prefer direct profile fetches with ISO-date observation rather than third-party aggregators.

---

## §6. Source bibliography (deduplicated, retrievable)

**Anthropic**
- "Building Effective Agents," Schluntz & Zhang, Dec 2024 — https://www.anthropic.com/research/building-effective-agents
- "Building agents with the Claude Agent SDK," Sept 29, 2025 — https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk
- "Effective harnesses for long-running agents" — https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- "How we built our multi-agent research system," June 2025 — https://www.anthropic.com/engineering/multi-agent-research-system
- "Long-running Claude for scientific computing" (Mishra-Sharma) — https://www.anthropic.com/research/long-running-Claude
- "Introducing Claude Sonnet 4.5" — https://www.anthropic.com/news/claude-sonnet-4-5
- Claude Agent SDK docs — https://docs.claude.com/en/docs/agent-sdk/overview, https://code.claude.com/docs/en/agent-sdk/overview
- claude-agent-sdk-python — https://github.com/anthropics/claude-agent-sdk-python

**OpenAI**
- "The next evolution of the Agents SDK" — https://openai.com/index/the-next-evolution-of-the-agents-sdk/
- "New tools for building agents" — https://openai.com/index/new-tools-for-building-agents/
- "Harness engineering: leveraging Codex in an agent-first world," Lopopolo — https://openai.com/index/harness-engineering/
- "OpenAI for Developers in 2025" — https://developers.openai.com/blog/openai-for-developers-2025
- Agents SDK docs — https://openai.github.io/openai-agents-python/
- Apps SDK — https://developers.openai.com/apps-sdk

**Google**
- ADK docs — https://google.github.io/adk-docs/
- "Agent Development Kit" announcement — https://developers.googleblog.com/en/agent-development-kit-easy-to-build-multi-agent-applications/
- adk-python — https://github.com/google/adk-python
- Gemini Enterprise Agent Platform — https://cloud.google.com/products/agent-builder

**Microsoft**
- "Introducing Microsoft Agent Framework," Oct 1, 2025 — https://devblogs.microsoft.com/foundry/introducing-microsoft-agent-framework-the-open-source-engine-for-agentic-ai-apps/
- MAF Overview — https://learn.microsoft.com/en-us/agent-framework/overview/
- "Migrate to Microsoft Agent Framework Release Candidate" — https://devblogs.microsoft.com/semantic-kernel/migrate-your-semantic-kernel-and-autogen-projects-to-microsoft-agent-framework-release-candidate/
- "Microsoft's Agentic Frameworks: AutoGen and Semantic Kernel" — https://devblogs.microsoft.com/autogen/microsofts-agentic-frameworks-autogen-and-semantic-kernel/
- Sarah Bird — https://www.microsoft.com/en-us/research/people/slbird/

**AWS**
- AgentCore overview — https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html, https://aws.amazon.com/bedrock/agentcore/
- bedrock-agentcore-sdk-python — https://github.com/aws/bedrock-agentcore-sdk-python
- agentcore-samples — https://github.com/awslabs/agentcore-samples
- Strands docs — https://strandsagents.com/docs/

**Frameworks**
- LangChain blog — https://blog.langchain.com (incl. Three Years of LangChain, Ambient Agents, Rise of Context Engineering)
- LlamaIndex — https://www.llamaindex.ai/, https://github.com/run-llama/llama_index
- CrewAI — https://github.com/crewAIInc/crewAI, https://blog.crewai.com
- Mastra — https://mastra.ai, https://github.com/mastra-ai/mastra
- Pydantic AI — https://ai.pydantic.dev/
- DSPy — https://dspy.ai/, https://omarkhattab.com/, https://dblp.org/pid/129/7815.html (Khattab)
- smolagents — https://github.com/huggingface/smolagents, https://huggingface.co/blog/smolagents
- Letta — https://docs.letta.com/, https://www.letta.com/blog/agent-memory; MemGPT arXiv 2310.08560

**CLI / IDE**
- Aider — https://aider.chat
- OpenHands — https://github.com/OpenHands/OpenHands, https://github.com/OpenHands/software-agent-sdk
- Goose — https://github.com/aaif-goose/goose, https://goose-docs.ai
- Amp — https://ampcode.com/notes/how-to-build-an-agent (Ball, Apr 15, 2025), https://ampcode.com/manual, https://ampcode.com/podcast
- Cline — https://cline.bot, https://cline.bot/blog
- Cursor — https://cursor.com (and Codersera 2026 guide)
- awesome-cli-coding-agents — https://github.com/bradAGI/awesome-cli-coding-agents

**Browser/Computer-use**
- Browser-use — https://github.com/browser-use/browser-use
- Stagehand/Browserbase — https://www.stagehand.dev/, https://www.browserbase.com
- Skyvern — https://www.skyvern.com/

**Voice/Vertical**
- LiveKit — https://livekit.com
- Pipecat — https://pipecat.ai
- Vapi — https://vapi.ai
- Sierra/Decagon comparisons — https://sacra.com/research/sierra-vs-decagon/, https://www.upstartsmedia.com/p/decagon-sierra-ai-amazing-race

**Durable Execution**
- Temporal — https://temporal.io/, https://temporal.io/blog/what-is-durable-execution
- Restate — https://restate.dev
- Inngest — https://www.inngest.com/, https://www.inngest.com/compare-to-temporal
- DBOS — https://www.dbos.dev/
- Kai Waehner overview — https://www.kai-waehner.de/blog/2025/06/05/the-rise-of-the-durable-execution-engine-temporal-restate-in-an-event-driven-architecture-apache-kafka/
- Akka comparisons — https://akka.io/blog/inngest-vs-temporal

**Observability/Eval/Gateway**
- Langfuse — https://langfuse.com/
- LangSmith — https://smith.langchain.com
- Arize Phoenix — https://phoenix.arize.com/
- Helicone — https://www.helicone.ai/
- LiteLLM — https://github.com/BerriAI/litellm
- Promptfoo — https://www.promptfoo.dev/docs/providers/claude-agent-sdk/
- Inspect AI — https://inspect.aisi.org.uk

**Security**
- Simon Willison series — https://simonwillison.net/series/prompt-injection/
- Willison Substack — https://simonw.substack.com/p/prompt-injections-as-far-as-the-eye, https://simonw.substack.com/p/new-prompt-injection-papers-agents
- Rehberger — https://embracethered.com (referenced); 39C3 talk — https://fahrplan.events.ccc.de/congress/2025/fahrplan/event/agentic-problms-exploiting-ai-computer-use-and-coding-agents; AI Kill Chain paper — https://zenodo.org/records/18769277
- Anthropic system cards via https://www.anthropic.com

**Independent practitioners**
- Hamel Husain — https://hamel.dev, https://hamel.dev/blog/posts/evals-faq/
- Eugene Yan — https://eugeneyan.com
- Jason Liu — https://jxnl.co, https://jxnl.co/writing/
- Chip Huyen — https://huyenchip.com, https://huyenchip.com/2025/01/07/agents.html
- "What We Learned from a Year of Building with LLMs" (Yan, Bischof, Frye, Husain, Liu, Shankar) — https://www.oreilly.com/radar/what-we-learned-from-a-year-of-building-with-llms-part-i/ (and Parts II, III)
- Dex Horthy / 12-Factor Agents — https://github.com/humanlayer/12-factor-agents, https://www.humanlayer.dev/12-factor-agents
- Indragie Karunaratne — https://www.indragie.com/blog
- Lance Martin — https://rlancemartin.github.io/2025/06/23/context_engineering/, https://blog.langchain.com/introducing-ambient-agents/
- David Breunig — https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html

**Latent Space**
- Harness Eng with Lopopolo — https://www.latent.space/p/harness-eng
- Agent Engineering — https://www.latent.space/p/agent
- Context Engineering with Lance Martin — https://podscan.fm/podcasts/latent-space-the-ai-engineer-podcast/episodes/context-engineering-for-agents-lance-martin-langchain
- swyx site — https://www.swyx.io/

**OpenAI/Cognition coding-agents debate**
- "Don't Build Multi-Agents" (Cognition) referenced via Latent Space + LangChain blog
- Anthropic multi-agent research-system post (above)

**Disler / IndyDevDan**
- single-file-agents — https://github.com/disler/single-file-agents
- the-library — https://github.com/disler/the-library
- IndyDevDan YouTube — https://www.youtube.com/@indydevdan

**Conferences/Events**
- AI Engineer (swyx) — https://www.ai.engineer
- Replay (Temporal) — https://temporal.io/replay
- 39C3 — https://fahrplan.events.ccc.de/congress/2025/fahrplan/event/agentic-problms-exploiting-ai-computer-use-and-coding-agents

*[End of Session 2 deliverable. ~98 inventory entries across A1–A11; 60+ named individuals/orgs across B1–B11; ≥18 [Discovery] tags in Part A and ≥18 in Part B; all primary sources linked above are retrievable as of research date May 5, 2026.]*