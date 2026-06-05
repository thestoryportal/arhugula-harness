# Cluster Deep-Dive 2: Context, Prompts, and Memory

**Active session restatement.** Session 4, Cluster Deep-Dive 2 of the multi-session agent harness specification project. Cluster: "Context, Prompts, and Memory" — three topics: (1) prompt management infrastructure, (2) context engineering, (3) state and memory consistency. Builds on Session 1 (canonical-source substrate), Session 2 (harness/people inventory), Session 3 (repo profiles), Cluster Deep-Dive 1 (orchestration). Mode: Advanced Research, implementation-level depth. Stack target: self-hosted n8n, RAG pipeline, Claude.ai, Claude Code CLI, Codex, multi-LLM complexity-routed, OpenClaw.

---

## §1 Executive Synthesis

1. **Anthropic's `cache_control` is a *hash-of-prefix at the breakpoint*, not a content-cache.** Cache writes happen exclusively at marked blocks; reads walk backward up to **20 blocks** looking for prior writes. Placing the breakpoint on a block that varies per request (timestamp, incoming message) silently produces zero cache hits forever — `cache_creation_input_tokens` keeps incrementing, no error is raised. The discipline this imposes is non-negotiable: breakpoint = **last block identical across calls**, with all variable suffix after it. [HIGH] (platform.claude.com/docs/en/build-with-claude/prompt-caching, fetched 2026-05-06)

2. **Prompt-cache hierarchy `tools → system → messages` is a strict invalidation cascade.** Any change to tool definitions blows the entire cache; any system change blows system+messages. With dynamically-loaded skills/MCP tools, naive auto-loading is a cache-cost detonator. The architectural implication: **freeze a static tool/skill superset for the cacheable epoch and load specifics via filesystem/code-execution rather than re-mutating the `tools` array** — exactly the pattern Anthropic's "Code execution with MCP" (Nov 2025) ratifies. [HIGH]

3. **Context rot is real, model-non-uniform, and not summarizable as a single token threshold.** Chroma's July 2025 study (18 models, ~194,480 LLM calls) shows degradation begins well before stated context limits and depends on (a) needle-question cosine similarity (low-similarity pairs degrade fastest), (b) distractor count and identity (a single distractor reduces accuracy; non-uniform per distractor), (c) haystack structural coherence (counterintuitively, *shuffled* haystacks outperform coherent ones), and (d) needle-haystack similarity. **No per-model "Sonnet rots at Xk" number exists in the report; the curve is per-task, per-distractor, per-similarity.** Plan for graceful degradation, not a cliff. [HIGH] (research.trychroma.com/context-rot)

4. **Anthropic's "Effective harnesses for long-running agents" (Nov 26, 2025) prescribes a two-prompt, single-harness pattern.** Initializer agent writes `init.sh`, `feature_list.json` (JSON deliberately chosen over Markdown — "the model is less likely to inappropriately change or overwrite JSON"), an initial git commit, and `claude-progress.txt`. Coding agent runs every session: `pwd` → read `claude-progress.txt` → read `feature_list.json` → `git log --oneline -20` → run `init.sh` → smoke-test → pick one feature → implement → commit → update progress. **The post explicitly does NOT publish a `claude-progress.txt` schema** (sections, length caps, preserved-vs-discarded fields). Surface this honestly to the builder. [HIGH]

5. **Compaction ≠ summarization in production.** Claude Code's compaction "preserves architectural decisions, unresolved bugs, and implementation details while discarding redundant tool outputs"; the *safest* form is **tool-result clearing** (recently shipped as a platform feature). Anthropic recommends tuning compaction prompts by maximizing recall first, then iterating for precision. Failure mode: load-bearing detail (a constraint mentioned once, 30 turns ago) gets compressed away, and the agent silently regresses on it. [HIGH]

6. **Just-in-time (JIT) retrieval beats RAG-dump for agentic-code workloads but loses for stable knowledge corpora.** Anthropic's argument (effective-context-engineering, Sept 29 2025): JIT keeps file paths/queries/links as identifiers and loads on demand; mirrors human cognition; pays off when (a) corpus is dynamic, (b) navigation primitives (glob/grep/head/tail) exist, (c) full-corpus embed would dwarf context. RAG-dump wins for stable legal/finance corpora where navigation cost > retrieval cost. **Hybrid is dominant in practice** (e.g., `CLAUDE.md` pre-loaded + glob/grep on demand). [HIGH]

7. **Diagrid's "checkpoints are not durable execution" (Feb 25, 2026) names a real architectural gap, not a marketing wedge.** LangGraph's checkpointer saves state per super-step but the *application* is responsible for failure detection, lease coordination, dedup, and resumption. Temporal/Restate/Dapr Workflows provide event-sourced replay where every `await` is implicitly durable, completed activities return cached results on replay, and the runtime owns the lifecycle. **Do not flatten this to "both work."** For a solo founder running n8n + a single agent process: LangGraph-style checkpointing is sufficient until you have concurrent agents racing on shared state or SLA-bound workflows. Beyond that threshold, you need event-sourced durable execution. [HIGH]

8. **Claude Code's git-as-state is a working two-phase-commit-by-convention.** Commits = transactional unit; `claude-progress.txt` updates = the "ledger" that survives compaction; `init.sh` = idempotent rehydration. There is *no* real cross-medium 2PC shipping in Claude Code, Aider, or LangGraph: the practical pattern is **idempotency keys + git as the audit log + human reconciliation on divergence**. Aider's behavior makes this explicit: it commits dirty preexisting changes first (separating user edits from agent edits), then commits each agent change atomically. [HIGH]

9. **Hamel Husain's eval methodology is "error-analysis-first," not "eval-driven-development."** Concrete operational rules: 60–80% of dev time on error analysis; binary pass/fail (not Likert); annotate the *first upstream failure* in a multi-turn trace, not all failures; review ≥100 traces per cycle; use Cohen's κ (chance-corrected) for inter-annotator agreement when multiple labelers exist; LLM-as-judge requires ≥100 labeled examples and ongoing weekly maintenance and is reserved for *persistent generalization failures*; cheap code-based assertions (regex, schema, execution test) are the default gate. **Prompts in git, not in registries**, unless registries earn their keep through non-engineer iteration or A/B routing. [HIGH] (hamel.dev/blog/posts/evals-faq, Jan 15 2026)

10. **Shankar's "Who Validates the Validators?" (UIST '24, arXiv 2404.12272) operationalizes judge alignment as a mixed-initiative loop**, not a one-shot calibration. The concrete protocol: (a) human grades a subset, (b) candidate judges (code or LLM-prompt) generated, (c) judges that better align with grades are selected, (d) iterate as criteria drift (a documented phenomenon). Reported alignment metric is graded percent-agreement plus TPR/TNR; Husain's FAQ explicitly flags Cohen's κ for multi-annotator disagreement detection (because "judges with high percent agreement can still assign vastly different scores"). [HIGH]

11. **CoALA (Sumers et al., arXiv 2309.02427) memory taxonomy — working / episodic / semantic / procedural — is implemented in production only partially.** Most production harnesses (Claude Code, Aider, Manus) implement working memory (context window) + procedural (skills/tools) + a single shared episodic-and-semantic store (filesystem files, NOTES.md, todo.md). True four-tier separation appears in research systems (Letta/MemGPT, Mem0) but adds residence-decision overhead that is rarely paid back at solo-founder scale. [MODERATE]

12. **The substrate's `arXiv:2603.29194` "Multi-Layered Memory Architectures" is a *real* paper but its mid-2026 timestamp and low citation footprint suggest you should treat its specific F1/retention numbers (46.85 SR, 0.618 F1, 56.90% six-period retention) as not-yet-corroborated.** Use it as a vocabulary source (working/episodic/semantic decomposition with retrieval gating and retention regularization) rather than as a benchmark. [SPECULATIVE — corroboration low; treat as a single-paper claim until replicated]

---

## §2 Per-Topic Deep Dives

### 2.1 Topic 1 — Prompt Management Infrastructure

#### 2.1.1 Topic restatement
Prompt management infrastructure is the deterministic substrate that (a) constructs prompts at request time from versioned components (system prompt, tool defs, examples, retrieved context, conversation history); (b) governs what is cacheable vs. dynamic at the byte level so that prompt-prefix caches actually hit; (c) versions, evaluates, and routes prompts as code; and (d) connects prompt changes to evals, traces, and rollback. It is the bottom of the stack on which context engineering (§2.2) and state/memory (§2.3) sit.

#### 2.1.2 Canonical sources, deeply engaged

**Anthropic, "Prompt caching"** — `https://platform.claude.com/docs/en/build-with-claude/prompt-caching` (fetched 2026-05-06).
- Cache prefix order is **`tools → system → messages`**, "in that order up to and including the block designated with `cache_control`."
- "Cache writes happen only at your breakpoint." Marking a block writes exactly one entry: a hash of the prefix ending at that block.
- Lookback window is **20 blocks**: "checks at most 20 positions per breakpoint."
- TTL: 5 min default (cache-write 1.25× base; read 0.1×); 1 hr extended (write 2× base) — supported on Opus 4.5+, Haiku 4.5, Sonnet 4.5+. 1-hr cache entries must appear *before* shorter-TTL entries.
- Min cacheable prefix: 1024 tok (Sonnet 4.5 / Opus 4 / Sonnet 4 / Sonnet 3.7), 2048 (Sonnet 4.6, Haiku 3.5), **4096** (Opus 4.5/4.6/4.7, Haiku 4.5).
- Up to **4 explicit breakpoints per request**; auto-cache uses one slot.
- Length-based caching failures are silent: response succeeds, but `cache_creation_input_tokens` and `cache_read_input_tokens` both equal 0.
- Pre-warming: `max_tokens: 0` returns empty content with `stop_reason: "max_tokens"`, runs full prefill, populates cache; place breakpoint on shared static prefix, not the placeholder user message.
- Strong on mechanism, billing, invalidation table, edge cases. Weak on multi-tenant patterns, on dynamic-tool-set strategies (these are addressed only obliquely in Anthropic's separate code-execution-with-MCP post).
- Connects to: §2.1.2 Spring AI analysis (concrete code-level reification of the same rules); §2.2 long-running-harnesses post (compaction interacts with caching because compaction rewrites the message tail).

**Anthropic Cookbook, "Prompt caching" notebook** — `github.com/anthropics/anthropic-cookbook/blob/main/misc/prompt_caching.ipynb` (fetched via search 2026-05-06).
- "Start with automatic caching." Switch to explicit breakpoints "only when you need fine-grained control."
- Worked example: cache `cache_control` on book content block; "manually move the breakpoint forward on each turn."
- Reinforces: 4 breakpoints, 5-min default, 1-hr=2× base.
- Strong on minimal-viable code; weak on multi-segment caches (RAG context + tools + system as four independent segments), which the Anthropic docs cover better.

**Spring AI prompt-caching analysis** — `spring.io/blog/2025/10/27/spring-ai-anthropic-prompt-caching-blog`.
- Frames caching as a `CacheEligibilityResolver` strategy + `CacheBreakpointTracker` enforcing the 4-breakpoint limit.
- Names four strategies: `SYSTEM_ONLY`, `TOOLS_ONLY`, `CONVERSATION_HISTORY`, and combinations. Aggregate-eligibility for `CONVERSATION_HISTORY` "considers the combined content of all message types... within the last ~20 content blocks."
- Operational warning: "Don't use `SYSTEM_ONLY` if your system prompt changes frequently — you'll pay cache write costs without getting cache hits." (a forcing function: declare which prompt parts are "static" up front.)
- Worked latency/cost: 5,000 tokens at Sonnet 3.5 = $0.01875 first call (write), $0.00150 subsequent (read) — ~12× reduction.
- Strong on framework-level enforcement and the *failure mode* the substrate flagged ("single character change creates new cache entry"). Weak on: not Anthropic-authoritative.
- Connects to: 12-Factor Agents Factor 2 (own your prompts) — Spring AI's strategies are essentially codified Factor-2 discipline at framework level.

**Hamel Husain, "LLM Evals: Everything You Need to Know"** — `hamel.dev/blog/posts/evals-faq` (Jan 15 2026, with Shreya Shankar).
- Cost hierarchy: code assertions/regex/schema (cheap, default); reference-based checks; LLM-as-judge ("100+ labeled examples, ongoing weekly maintenance, coordination between developers, PMs, and domain experts"). Build expensive evaluators only for *persistent generalization failures*.
- Binary pass/fail required; Likert "introduces significant challenges: the difference between adjacent points... is subjective and inconsistent across annotators."
- Error-analysis-first; *not* eval-driven development. "60-80% of development time on error analysis."
- For multi-annotator setups: draft rubric → independent labels → measure inter-annotator agreement using Cohen's κ → alignment sessions → iterate.
- Prompt versioning: **prompts in git** ("treats them as software artifacts that are versioned, reviewed, and deployed atomically"). Prompt-management UIs "risk creating additional layers of indirection" and "can't easily execute your application's code."
- Connects to: Shankar et al. 2404.12272 (judge alignment loop); PROMPTEVALS dataset (operationalizes assertion generation).

**Hamel Husain, "Your AI Product Needs Evals"** — `hamel.dev/blog/posts/evals`.
- Three levels: L1 unit tests (every code change), L2 human/model eval (set cadence), L3 A/B (after significant product changes). Cost: L3 > L2 > L1 → dictates cadence.
- "Critique shadowing" protocol for building LLM-as-judge: principal domain expert produces pass/fail with critique; critique becomes alignment fuel for the judge prompt.

**Shankar et al., "Who Validates the Validators?"** — `arxiv.org/abs/2404.12272` (UIST '24).
- Mixed-initiative loop: human grades subset → candidate judges generated → judges selected by alignment with human grades → iterate.
- Documents **criteria drift**: "evaluation criteria tends to shift after reviewing a model's outputs" — meaning judge alignment is not a one-shot calibration but a continuous process.
- Reported metric: alignment-with-human-grades; Husain's FAQ extends this with TPR/TNR on held-out set and Cohen's κ for chance-corrected agreement.
- The paper does *not* publish a single threshold for "aligned"; treat ≥0.99 GPT-4.1-judge alignment with humans (as Chroma reports for their context-rot judge) as the ceiling, ≥80–90% as a working gate, with Cohen's κ ≥ 0.7 as substantive agreement.
- Connects to: PROMPTEVALS (2504.14738) — empirically grounded assertion-generation dataset (2087 prompts, 12,623 assertion criteria, 5× larger than prior).

**Shankar et al., "PROMPTEVALS"** — `arxiv.org/abs/2504.14738` (Apr 20 2025).
- 2087 LLM pipeline prompts (median 191 tokens) with 12,623 human-authored assertion criteria from LangChain Prompt Hub.
- Three-step ground-truth criteria generation: initial generation → omission pass → removal pass for incorrect/redundant/vague.
- Fine-tuned Mistral-7b and Llama-3-8b outperform GPT-4o by 20.93% on average for assertion generation.
- Strong as a corpus for what real production assertions look like; weak as direct benchmark for *your* assertions (your domain ≠ their domain).

**Eugene Yan, "Patterns for Building LLM-based Systems"** — `eugeneyan.com/writing/llm-patterns/`.
- Seven patterns: Evals, RAG, Fine-tuning, Caching, Guardrails, Defensive UX, User feedback.
- Caching framed as both a latency/cost lever *and* a determinism lever (cache embeddings, cache lookups by hashed input, cache LLM outputs for high-frequency prompts).
- Cited as substrate; nothing new at depth beyond Session 1 coverage.

**HumanLayer "12-Factor Agents," Factor 2** — `github.com/humanlayer/12-factor-agents/blob/.../content/factor-2-own-your-prompts.md`.
- Treat prompts as first-class code: "directly control your prompts as first-class code."
- Frameworks that hide prompts limit tuning and debuggability.
- Factor 3 ("Own your context window") complements: encode arbitrary event sequences into a single user message with XML-style event tags rather than relying on chat-message roles. This is the most prompt-engineering-significant Factor 3 claim: **structured-event encoding inside a single message gives you full control over token layout and cache stability.**
- Empirically grounded by Horthy's "100,000 developer sessions" claim cited in derived posts (analyst, not a peer-reviewed claim — treat as practitioner heuristic). [MODERATE]

**OpenTelemetry GenAI semantic conventions for spans** — `opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/` and `.../gen-ai-agent-spans/`.
- Span name: `{gen_ai.operation.name} {gen_ai.request.model}`; CLIENT kind for remote-model calls.
- Required attributes: `gen_ai.provider.name`, `gen_ai.request.model`, `error.type`. Optional captured-content: `gen_ai.system_instructions`, `gen_ai.input.messages`, `gen_ai.output.messages` — **default OFF**, opt-in.
- Agent spans extend with `gen_ai.operation.name` of `create_agent` / `invoke_agent` and `gen_ai.agent.name` / `gen_ai.agent.id`.
- Stability gate: `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental` to receive new conventions; otherwise instrumentations preserve v1.36.0 semantics.
- Connects to: Husain (eval tooling needs trace bulk-export); LangGraph (Tracing integrations for LangSmith/Phoenix/Braintrust use these conventions).

#### 2.1.3 Patterns and primitives at depth

**Pattern P1.1 — Static-prefix / dynamic-suffix discipline.**

```
┌─────────────────── CACHEABLE PREFIX (hash key) ──────────────────┐ ┌─ DYNAMIC ─┐
│ tools[] (frozen for epoch)                                        │ │ user msg  │
│ system[]: identity, policies, output schema, examples (frozen)    │ │ timestamp │
│ messages[]: conversation history up to last user turn (growing)   │ │ retrieved │
│ ◆ cache_control HERE (5m or 1h ephemeral)                         │ │ context   │
└───────────────────────────────────────────────────────────────────┘ └───────────┘
                                  ▲                                          ▲
                          Breakpoint on LAST                  Suffix is uncached;
                          IDENTICAL block across              cost = base × suffix tokens
                          requests in epoch
```

Cost model when discipline holds (Sonnet 4.5, 5-min cache, 100k-token prefix, 500-token suffix): write once $0.375, then per request $0.030 + $0.0015 = $0.0315. Cost when discipline breaks because the breakpoint lands on a block that mutates per request: **every request costs a full write** ≈ $0.375 (12× more). At 10 requests/min for an hour, the difference is ≈$5 vs ≈$220.

**Pattern P1.2 — Multi-segment cache for differential-frequency content.** Up to 4 breakpoints lets you cache `[tools] [stable-instructions] [skill-pack] [conversation]` independently. When the skill-pack rotates, only segments 3+4 invalidate; segments 1+2 still hit.

**Pattern P1.3 — Pre-warm at process boot.** Use `max_tokens: 0` after process start (and on a 4-min recurring keep-alive for 5-min TTL caches), placing the breakpoint on the **shared static prefix**, not the warmup placeholder. Eliminates first-request TTFT penalty.

**Pattern P1.4 — Tool-set freezing for an epoch.** Because any change to the `tools` array invalidates the entire cache (tools→system→messages cascade), the dynamically-loaded-tool problem (Skills, MCP) is solved either (a) by freezing a *superset* of tool defs for the epoch and letting the agent ignore unused ones, or (b) by Anthropic's code-execution-with-MCP pattern: present tools as files on disk that the agent reads on demand via bash; the `tools` array stays static (a single `bash`/`read` tool), only the file content varies. The latter is the more cache-efficient pattern and is the *only* one that scales past ~20 dynamically-rotating tools.

**Pattern P1.5 — Eval gate cadence (Husain).**
- Pre-commit: code-based assertions (regex, JSON-schema, execution sanity) on a 20-50 trace dev fixture. Latency budget: ≤30s in CI.
- Pre-deploy: LLM-judge on 100-trace held-out fixture; gate on TPR ≥0.9, TNR ≥0.85, Cohen's κ vs. principal domain expert ≥0.7.
- Post-deploy: weekly error-analysis cycle on ≥100 fresh production traces; whenever a new failure mode crosses the cost-benefit threshold, mint an automated assertion or judge.

**Approximate ratio (operationalized from Husain's posts; not a published Husain number):** code-based gates : LLM-judge gates ≈ **3–5 : 1** in mature pipelines. [MODERATE — inferred]

**Pattern P1.6 — Prompt registry vs. git decision matrix.**

| Criterion | Git wins | Registry wins |
|---|---|---|
| Atomic deploy with code | ✓ | ✗ (indirection) |
| Non-engineer iteration | ✗ | ✓ |
| Runtime version selection (A/B) | possible (config-driven) | ✓ (native) |
| Eval linkage in CI | ✓ (PR triggers evals) | ✓ (vendor MCP) |
| Diff/review/blame | ✓ (native) | varies |
| Solo founder, ≤3 contributors | **Git** | overkill |
| Multi-team, 2 LLM products, PM-driven copy | possible but painful | **Registry** |

Threshold (operational heuristic): **registry only when (a) ≥3 non-engineer authors regularly edit prompts, OR (b) you need runtime A/B routing on prompt id without redeploy, OR (c) a regulated domain requires explicit prompt-version audit trails**. For the solo-founder profile in this project: git + Jupyter prompt-experimentation, no registry. [HIGH on Husain's recommendation; SPECULATIVE on the precise threshold]

#### 2.1.4 Tradeoffs at depth

| Axis | Auto-caching | Explicit breakpoints | No caching | Prompt registry | Git-only |
|---|---|---|---|---|---|
| Cost (steady state) | **0.1×** input | **0.1×** input | 1× input | 0.1× (same) | 0.1× (same) |
| Cost (worst case: bad breakpoint) | 1.25× | **1.25× every call** | 1× | n/a | n/a |
| Latency (cache hit) | **−40–80% TTFT** | **−40–80% TTFT** | baseline | n/a | n/a |
| Reliability | high (auto walks back ≤20 blocks) | highest (developer controls) | n/a | network dep | filesystem |
| Debuggability | medium (silent length failures) | medium (silent length failures) | high | medium | **highest** |
| Cache hit rate | high if conv. tail simple | **highest** (multi-segment) | 0 | n/a | n/a |
| Operational complexity | low | medium | none | medium | low |
| RPO/RTO of prompt changes | n/a | n/a | n/a | seconds (runtime) | minutes (deploy) |

#### 2.1.5 Failure modes in the field

- **Silent zero-cache.** Reported across Spring AI blog, Anthropic docs, and OpenRouter docs: marking the breakpoint on a per-request varying block produces success responses with `cache_creation_input_tokens=cache_read_input_tokens=0`. Detection: emit a Prometheus counter from your client wrapper; alert when 5-min rolling cache-hit rate drops below 0.6 on a known-stable workload.
- **Tool-array reorder breaks cache silently.** Some languages (Swift, Go) randomize JSON key order in tool_use blocks, "breaking caches" (Anthropic docs explicitly call this out). Mitigation: serialize tool definitions with sorted keys.
- **Thinking-block stripping (pre-Sonnet 4.6/Opus 4.5).** Adding non-tool-result user content invalidates cached thinking blocks, evicting them from context. On 4.5+/4.6+, thinking blocks are preserved by default — model upgrades cause behavioral drift.
- **Image presence flip invalidates messages cache.** "Adding/removing images anywhere in the prompt affects message blocks."
- **Eval-driven development trap (Husain).** Teams write evaluators for hypothetical failures; production reveals different failures; eval suite measures the wrong thing. Mitigation: write evaluators only after error analysis names a recurring concrete failure mode.
- **Generic-metric trap (Husain).** Vendor-provided "helpfulness" / "coherence" judges produce false confidence: "All you get from using these prefab evals is you don't know what they actually do."

#### 2.1.6 Open questions and unresolved debates

- Multi-tenant cache-key isolation: from Feb 5 2026 prompt caching uses **workspace-level isolation** (Claude API + Azure AI Foundry preview); Bedrock/Vertex retain organization-level. Not yet documented: whether cross-workspace prompt-prefix collisions can leak cache hits in adversarial scenarios.
- Whether "criteria drift" (Shankar) can be partially automated by agent-led error analysis (Husain's `evals-skills`/MCP-server direction) without losing the human-in-the-loop guarantee.
- The dispute between automated prompt optimization (DSPy, EvoPrompt) and Husain's "write prompts manually so you understand your problem" — unresolved, with Husain conceding "for that last mile of performance" automation is fine.

#### 2.1.7 For-the-builder implications

For your local-first multi-LLM harness: enforce static-prefix discipline at the n8n-orchestration layer by serializing every Anthropic-route request through a single client that (a) sorts tool-def JSON keys, (b) places one explicit `cache_control` after the system+tool block and another at the end of the conversation tail, (c) emits cache-hit telemetry into your OpenTelemetry GenAI spans. Keep prompts in git; build a 100-trace held-out fixture per agent role; gate deploys on a Cohen's κ ≥ 0.7 LLM-judge plus a regex/schema assertion battery; do not adopt a prompt registry until you have a non-engineer collaborator. Accept that your dynamically-loaded skills will be cache-hostile unless you migrate to a code-execution-with-MCP filesystem pattern.

---

### 2.2 Topic 2 — Context Engineering

#### 2.2.1 Topic restatement
Context engineering is the (probabilistic, iterative) discipline of curating the token-by-token holistic state available to a language model at each inference: system prompt altitude, tool surface, examples, retrieved/JIT context, message history, scratchpads, and compaction artifacts. It is the layer above prompt management (the deterministic substrate) and below state/memory (the durable substrate); its target is "the smallest set of high-signal tokens that maximize the likelihood of a desired outcome" (Anthropic, Sept 29 2025).

#### 2.2.2 Canonical sources, deeply engaged

**Anthropic, "Effective context engineering for AI agents"** — `anthropic.com/engineering/effective-context-engineering-for-ai-agents` (Sept 29 2025, fetched 2026-05-06). Authors: Prithvi Rajasekaran, Ethan Dixon, Carly Ryan, Jeremy Hadfield (Applied AI team).
- Frames context as a "finite resource with diminishing marginal returns"; treats LLMs as having an "attention budget" depleted by every additional token.
- "Right altitude" for system prompts: between hardcoded if-else brittleness and overly general guidance; recommends `<background_information>`, `<instructions>`, `## Tool guidance`, `## Output description` sectioning (XML or Markdown).
- Tool guidance: minimal viable tool set, no overlapping functionality. "If a human engineer can't definitively say which tool should be used... an AI agent can't be expected to do better."
- Few-shot: curate a "set of diverse, canonical examples"; explicitly does NOT recommend "stuff[ing] a laundry list of edge cases."
- JIT-vs-RAG hybrid: maintain "lightweight identifiers (file paths, stored queries, web links)" and load on demand; Claude Code as canonical example using glob/grep/bash head/tail.
- Three long-horizon techniques: **compaction** (Claude Code preserves "architectural decisions, unresolved bugs, and implementation details while discarding redundant tool outputs"), **structured note-taking** (NOTES.md, todo.md; Claude playing Pokémon "for the last 1,234 steps I've been training my Pokémon in Route 1, Pikachu has gained 8 levels toward the target of 10"), **sub-agent architectures** (sub-agent uses tens of thousands of tokens, returns "1,000-2,000 tokens" distilled).
- Strong on principles, mental model. **Weak on**: no specific token thresholds for compaction triggers; no claude-progress.txt schema; no explicit mention of distractor-density numbers.
- Connects to: §2.2.2 Chroma context-rot (provides the empirical degradation curves Anthropic gestures at); §2.2.2 long-running-harnesses post (concretizes compaction-vs-handoff); §2.3 LangGraph (compaction is *application-level*, it is not durable execution).

**Anthropic, "Effective harnesses for long-running agents"** — `anthropic.com/engineering/effective-harnesses-for-long-running-agents` (Nov 26 2025, fetched 2026-05-06). Author: Justin Young.
- Core failures observed: (a) agent tries to one-shot, exhausts context mid-implementation; (b) later-session agent declares victory after seeing prior progress.
- Two-prompt solution: **initializer agent** writes `init.sh`, `feature_list.json`, an initial git commit, and `claude-progress.txt`. **Coding agent** runs every session; same system prompt + tools + harness as initializer, only the user prompt differs ("We refer to these as separate agents in this context only because they have different initial user prompts").
- `feature_list.json` example given — a single JSON entry has fields `category` ("functional"), `description`, `steps[]`, `passes` (bool). For the claude.ai clone, "over 200 features."
- "JSON for this, as the model is less likely to inappropriately change or overwrite JSON files compared to Markdown."
- Strongly-worded gate: "It is unacceptable to remove or edit tests because this could lead to missing or buggy functionality."
- Coding agent startup ritual (verbatim): `pwd` → read `claude-progress.txt` → read `feature_list.json` → `git log --oneline -20` → run `init.sh` (start dev server) → smoke-test via Puppeteer MCP → pick highest-priority not-done feature.
- Testing: Puppeteer MCP for end-to-end browser automation. Acknowledged limit: "Claude can't see browser-native alert modals through the Puppeteer MCP, and features relying on these modals tended to be buggier."
- **The post does NOT publish a `claude-progress.txt` schema.** It is described as "a log of what agents have done" and "summaries of its progress in a progress file"; it is read at session start and updated at session end. Section names, length caps, what is preserved-vs-discarded, structured-vs-prose: **not specified in the public post**.
- Failure-modes table is published verbatim and is the most concrete contract: see §2.2.3.
- Open questions explicitly acknowledged: whether multi-agent (testing/QA/cleanup specialists) outperforms a single coding agent; whether the pattern generalizes beyond full-stack web dev.
- Strong on the operational ritual; **weak on** the schema details a builder needs.

**Anthropic, "Code execution with MCP"** — `anthropic.com/engineering/code-execution-with-mcp` (Nov 4 2025).
- Problem framing: 5-MCP-server setup with 58 tools = ~55K tokens before conversation starts.
- Solution: present MCP servers as a `./servers/<server-name>/<tool-name>.ts` filesystem tree the agent reads on demand; agent writes TypeScript that imports and composes wrappers.
- Reported reduction: "150,000 tokens to 2,000 tokens — a time and cost saving of 98.7%." (This is Anthropic's own example, not an independent benchmark; treat as illustrative not load-bearing.) [MODERATE]
- Internal-testing accuracy on MCP evals (cited in the related "Advanced tool use" post, not this one): Opus 4 49% → 74%, Opus 4.5 79.5% → 88.1% with Tool Search Tool enabled.
- Cloudflare's "Code Mode" reaches the same conclusion via different framing.
- Implementation gap: Anthropic publishes the pattern but "no code to execute on it"; treated as a community-implementation prompt (Simon Willison commentary, Nov 4 2025).

**Chroma Research, "Context Rot: How Increasing Input Tokens Impacts LLM Performance"** — `research.trychroma.com/context-rot` (July 14 2025; authors Kelly Hong, Anton Troynikov, Jeff Huber). 18 models, ~194,480 calls, GPT-4.1-judge with >99% human alignment.

Specific reported findings (paraphrased, with numbers):
- **No single per-model "rot threshold."** Performance is non-monotonic and per-task; Sonnet 3.5 outperforms newer Claudes on Repeated Words "up to its maximum output token count of 8192," then degrades.
- **Needle-question similarity matters.** PG-essay haystack: needle-question similarity range 0.445–0.775 (across 5 embedding models). Lower-similarity needles (lower 50%) degrade *faster* with input length than higher-similarity (upper 50%); the gap widens at longer inputs.
- **Distractor effects are non-uniform.** Single distractor measurably reduces accuracy vs. needle-only; 4 distractors compound. Per-distractor identity matters: in arXiv-haystack/PG-essay-needle, distractor 3 caused greater decline than 1, 2, 4. Hallucinated responses preferentially picked distractors 2 and 3.
- **Model-family ambiguity behavior.** Claude Sonnet 4 and Opus 4 abstain conservatively under ambiguity (lowest hallucination rate). GPT models hallucinate confidently most often under distractors.
- **Haystack structural coherence hurts.** Across all 18 models, *shuffled* haystacks outperform coherent essays — shuffling removes structural attention competition for the needle.
- **LongMemEval results.** ~113K-token full input vs. ~300-token focused input on the same question. *All models* perform significantly better on focused; Claude Opus 4 / Sonnet 4 show the largest gap (driven by abstentions on the long input). Refusal example: Sonnet 4 says "I cannot determine the number of days... the specific dates for these events are not provided" when the dates are present in the long context.
- **Repeated Words.** As input/output length scales, accuracy degrades; GPT-4.1 refuses 2.55%, Opus 4 refuses 2.89% (with explicit copyright/inconsistency reasoning); GPT-3.5 refuses 60.29% (excluded entirely).
- **Position accuracy.** Across families, accuracy is highest when the unique token sits near the *beginning* of the sequence at long inputs.

The Chroma report's calibrated takeaway is that **no specific per-model token-cliff exists**; degradation is gradual, multi-factor, and the best summary statistic is "needle-question similarity × distractor density × input length × haystack structure."

**Liu et al., "Lost in the Middle"** — `arxiv.org/abs/2307.03172` (TACL 2024).
- U-shaped curve: best performance when relevant info is at beginning (primacy) or end (recency); worst in the middle.
- Holds across models including those marketed as long-context.
- 2025/2026 follow-up work (2511.05850 Gemini 2.5 Flash; 2508.07479 input-length-relative-to-window) shows the LiM effect is **not universal**: it has been substantially mitigated on some frontier models for simple factoid Q&A but reappears under (a) longer relative input, (b) primacy-bias drop near context-window limits, (c) semantic-matching tasks. Substrate's cite remains correct; flag the partial mitigation. [HIGH for original; MODERATE for "still applies in 2026"]

**"Multi-Layered Memory Architectures for LLM Agents"** — `arxiv.org/abs/2603.29194`. Verified the substrate's exact ID is real; paper is by Sunil Tiwari and 1 other; presents working / episodic / semantic decomposition with "adaptive retrieval gating and retention regularization." Reports 46.85 SR / 0.618 F1 / 56.90% six-period retention / 5.1% false-memory / 58.40% context usage on LOCOMO/LOCCO/LoCoMo. **Mid-2026 timestamp + thin citation footprint** — treat numbers as not-yet-corroborated. [SPECULATIVE corroboration; HIGH on existence] Useful as vocabulary; not as a benchmark.

**"Context Engineering: From Prompts to Corporate Multi-Agent Architecture"** — searches did not surface a paper of this exact title at a verifiable arXiv ID this session. **If the substrate carries this title, leave the citation as-is but flag it as not-re-verified-this-session.** [SPECULATIVE — could not corroborate]

**Drew Breunig context-rot essays** — `dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html` (referenced via Lance Martin's posts; not directly fetched this session). Names four failure modes that Lance Martin operationalizes: context **poisoning** (a hallucination becomes self-citation), **distraction** (too much irrelevant content), **confusion** (conflicting instructions), **clash** (incompatible objectives). The "context poisoning" pattern is widely echoed (contextpatterns.com, multiple practitioner sites). [MODERATE corroboration via secondary practitioner sources]

**Lance Martin (LangChain), "Context Engineering for Agents"** — `blog.langchain.com/context-engineering-for-agents/` and `rlancemartin.github.io/2025/06/23/context_engineering/`.
- Four-bucket taxonomy: **write** (scratchpad/memory outside context), **select** (RAG/retrieval), **compress** (summarize/prune), **isolate** (sub-agents, sandboxed code).
- Explicit naming of Anthropic multi-agent's "up to 15× more tokens than chat" cost.
- Substantively congruent with Anthropic's Sept 29 2025 post; published 3 months earlier as standalone framing.

**CoALA framework (Sumers et al.)** — `arxiv.org/abs/2309.02427` (TMLR 2024).
- Memory: working (short-term) + long-term split into **episodic** (experiences/traces), **semantic** (knowledge/world model), **procedural** (code/skills/the LLM weights themselves).
- Decision-making: planning → execution loop with internal actions (reasoning, retrieval, learning) + external actions.
- Connects: most cited memory taxonomy across IBM/MongoDB/Letta/Mem0 docs; the de-facto vocabulary.

#### 2.2.3 Patterns and primitives at depth

**Anthropic two-agent harness (verbatim contract).**

```
SESSION 0 (initializer agent — different USER prompt, same SYSTEM/tools/harness):
  Input:  high-level spec ("build a clone of claude.ai")
  Output: ./init.sh                  (idempotent dev-server startup)
          ./feature_list.json        (>=100 entries with category/description/steps[]/passes:false)
          ./claude-progress.txt      (initialized)
          git init && git commit -m "initial scaffold"

SESSION N>=1 (coding agent — fresh context window, different USER prompt):
  Startup ritual:
    1. pwd
    2. read claude-progress.txt
    3. read feature_list.json
    4. git log --oneline -20
    5. bash init.sh                  (start dev server)
    6. smoke test via Puppeteer MCP
    7. select highest-priority feature where passes==false
  Work loop:
    8. implement single feature
    9. self-test end-to-end via Puppeteer
   10. mark passes:true ONLY if test verifies (gate: "It is unacceptable to remove or edit tests")
   11. git commit -m "<descriptive>"
   12. append to claude-progress.txt
```

**`claude-progress.txt` schema: NOT SPECIFIED IN THE PUBLIC ANTHROPIC POST.** The post describes its purpose ("a log of what agents have done"; "summaries of its progress") and read/write cadence (start-of-session read, end-of-session write) but does not publish field names, length caps, or section structure. Builders must design their own schema. A reasonable starting design (this is the builder's choice, not Anthropic's): `## YYYY-MM-DD HH:MM session N` heading, `### completed: [feature ids]`, `### in-flight: [feature id + state]`, `### blocked: [reason]`, `### key decisions: [≤5 bullets]`, `### next: [feature id]`. [SPECULATIVE — schema is the builder's invention, not from Anthropic]

**Feature-list JSON schema (Anthropic-published, verbatim form).**
```json
{
  "category": "functional",
  "description": "New chat button creates a fresh conversation",
  "steps": ["Navigate to main interface", "Click the 'New Chat' button", ...],
  "passes": false
}
```
The harness mutates only `passes`. Other fields are write-once by the initializer.

**Compaction implementation (Claude Code, paraphrased from Anthropic).**
- Trigger: token budget approaching context-window limit (specific threshold not published; empirically observed to trigger near 80–90% of window per practitioner reports — [SPECULATIVE]).
- Method: pass message history to the model with a compaction prompt; model produces a summary preserving "architectural decisions, unresolved bugs, and implementation details" and discarding "redundant tool outputs."
- Continuation: compressed summary + the **5 most recently accessed files** form the new context.
- Lightest-touch variant: tool-result clearing only (now a platform feature on Claude Developer Platform). Preserves all reasoning, drops only stale tool outputs.
- Failure mode: load-bearing detail mentioned once early in a long trace (a constraint, an edge case the user flagged) is summarized away; agent regresses on it silently. Mitigation: compaction prompt should be tuned by maximizing recall first then iterating for precision (Anthropic's stated method), and important constraints should be promoted to a persistent NOTES.md scratchpad outside context.

**JIT vs. RAG decision (Anthropic, paraphrased into a decision rule).**

```
   Corpus dynamic?              ── yes ──> JIT (file paths, glob/grep, head/tail)
        │
        no
        ▼
   Navigation primitives        ── no ──> RAG-dump (pre-inference embed retrieval)
   exist (filesystem,
   index, schema)?
        │
        yes
        ▼
   Full corpus token            ── yes ──> JIT
   count >> context window?
        │
        no
        ▼
   Hybrid (small static
   pre-load + JIT navigation)
```

Operational difference from a trace standpoint: JIT produces a *reasoning trace* visible in tool-call spans (agent decides "I need file X" → `read_file` → reasons over result → next decision). RAG-dump puts retrieval before inference; the model never explicitly reasons about retrieval choice. JIT cache-hit rate is typically *worse* than RAG-dump (each `read_file` adds dynamic content to the message tail) but **per-call tokens are lower** because the agent loads selectively. Net cost depends on whether navigation reduces total bytes-in-context more than cache-miss costs. Anthropic's stated case for JIT: stale-indexing avoidance + progressive disclosure + emergent behavior on metadata signals (folder hierarchies, naming conventions).

#### 2.2.4 Tradeoffs at depth

| Axis | Compaction | Structured notes (NOTES.md) | Sub-agents | JIT retrieval | RAG-dump |
|---|---|---|---|---|---|
| Cost (per call) | low | low | **high** (15× chat per Anthropic) | medium | low |
| Latency | low compaction event | low | high (sub-agent spawn + parallel) | medium (extra tool calls) | low |
| Reliability | medium (info-loss risk) | high (durable) | medium (handoff loss) | high (fresh state) | medium (stale) |
| Debuggability | low (post-summary trace gone) | **high** (file diff is durable) | medium | high (visible tool calls) | medium |
| Cache hit rate | bad post-compaction (prefix changes) | unaffected (file outside ctx) | bad (each subagent fresh) | medium-bad (dynamic tail) | **good** (static prefix) |
| RPO (data loss) | minutes (last compaction) | seconds (last write) | minutes (between handoffs) | n/a | n/a |
| RTO (resume) | needs new context window | seconds (re-read file) | spawn new sub-agent | seconds | seconds |
| Operational complexity | medium | low | high | medium | low |

#### 2.2.5 Failure modes in the field

- **Compaction-after-cache invalidates everything.** Compaction rewrites the message tail, so the prompt-cache prefix hash changes; next request is a full cache write. Plan for one expensive request after every compaction.
- **JSON-vs-Markdown for feature-list.** Anthropic explicitly chose JSON because Markdown was being silently overwritten by the model. Field-tested practitioner finding, not a published benchmark; treat as strong signal. [HIGH per Anthropic post]
- **Premature victory declaration.** Documented in the harness post as a real failure: later session sees prior progress, declares done. Mitigation = `feature_list.json` with explicit `passes:false` defaults plus `pwd→read→smoke-test` ritual.
- **Puppeteer MCP blind to native browser modals.** Documented limit — features that depend on `alert()`/`confirm()` are buggier.
- **Context poisoning (Breunig).** A single hallucinated fact in turn 3 is treated as ground truth in turn 7 and architectural assumption in turn 12. Mitigation: prefix model-generated content with `[Model's previous analysis]`-style labels; periodically re-verify key assumptions against source files.
- **Manus (cited via Lance Martin):** typical agent task ≈ 50 tool calls; without offloading via `todo.md` the context fills with tool observations. Production teams "offload tok-heavy tool observations" to disk and pass references back into the model.
- **NoisyBench / haystack-engineering follow-on findings:** agentic workflows amplify noise — distractors trigger ≤80% accuracy drops and "emergent misalignment even without adversarial intent." (arXiv 2601.07226 Lee et al.; published 2026-01-13.) [MODERATE corroboration]

#### 2.2.6 Open questions and unresolved debates

- **Anthropic context-engineering post vs. long-running-harnesses post: convergent or in tension?** The Sept post emphasizes compaction/notes/sub-agents as three alternatives. The Nov post downplays compaction as insufficient ("compaction isn't sufficient... even a frontier coding model... will fall short of building a production-quality web app... if it's only given a high-level prompt"). The **resolved reading**: compaction is necessary but not sufficient for projects spanning >> one context window; bridging requires durable artifacts (git, JSON state file, progress log). The two posts do not contradict; they layer.
- **Single general-purpose coding agent vs. specialized sub-agents** (testing, QA, cleanup): the long-running-harnesses post explicitly leaves this open.
- **Whether the two-agent pattern generalizes beyond full-stack web** (scientific research, financial modeling): Anthropic explicitly flags as open.
- **Per-model context-rot characterization:** Chroma's data is task-specific and cannot be reduced to per-model thresholds. The community's desire for a "Sonnet rots at Xk" number is unfulfilled; the right answer is per-task profiling.

#### 2.2.7 For-the-builder implications

For the local-first multi-LLM harness: implement Anthropic's two-prompt pattern as an n8n workflow with two distinct user-prompt templates against the same Claude Code CLI / Codex harness. Treat `feature_list.json` and `claude-progress.txt` as the cluster's most important durable artifacts (they bridge to §2.3). Define your own `claude-progress.txt` schema (Anthropic does not publish one); start with section headings the LLM can write to without corrupting (no nested JSON, no tables, no unicode tricks). Use Puppeteer MCP for E2E if you build web UIs; accept the alert-modal blindness. Adopt JIT retrieval over RAG-dump for code tasks (Claude Code already does this); keep RAG-dump for stable knowledge corpora the agent must reason over. Profile context-rot per-route in your eval fixtures; do not assume context-window-stated capacity is your operating capacity. Pre-load `CLAUDE.md` style files in the static prefix so they cache; let everything else navigate via filesystem.

---

### 2.3 Topic 3 — State and Memory Consistency

#### 2.3.1 Topic restatement
State and memory consistency is the durable substrate beneath context: the deterministic guarantees about what happens to in-progress work when an agent crashes, restarts, gets superseded by a new model version, or receives concurrent updates from a human and itself. It governs checkpoint cadence, replay determinism, two-phase-commit-ish patterns across mediums (filesystem, git, external APIs, DB), and pruning/garbage-collection of long-lived state.

#### 2.3.2 Canonical sources, deeply engaged

**LangGraph durable execution & checkpointing** — `docs.langchain.com/oss/python/langgraph/durable-execution`, DeepWiki `deepwiki.com/langchain-ai/langgraph/4.1-checkpointing` (fetched via search 2026-05-06).
- Persistence backbone: **thread** (`thread_id`), **checkpoint** (snapshot at every super-step), **StateSnapshot** (values + next + metadata), **pending writes** (intermediate node outputs not yet committed to a checkpoint).
- Cadence: "saves snapshots of graph state after each super-step." A super-step is one tick where one or more nodes execute; parallel-node super-steps emit a single composite checkpoint with successful-node outputs preserved as pending writes if a sibling fails.
- What's stored: full state snapshot + metadata (source, writes, step number) + parent_config. Implementations: PostgresSaver, SqliteSaver, MemorySaver (dev only), DynamoDBSaver (AWS-maintained, payloads >350KB offload to S3).
- Resumption: invoke with same `thread_id` and `None` input.
- RetryPolicy attaches per node; on exhaustion, exception is raised and persisted in checkpoint.
- **What it explicitly does not do** (per the docs and Diagrid): no automatic failure detection (no watchdog, no heartbeat); no automatic resumption; no built-in distributed locking against concurrent resumes of the same `thread_id`; single-process by default in OSS.
- Strong on per-step persistence and time-travel debugging. Weak on guaranteed completion.

**LangGraph human-in-the-loop** — `docs.langchain.com/oss/python/langchain/human-in-the-loop`.
- Interrupts pause execution to wait for external input; checkpoint preserves the pending state.
- Resume by re-invoking the graph with the human-provided value; the interrupted node re-runs with the new input.
- Mechanism is a special case of the same checkpoint substrate.

**Diagrid, "Checkpoints Are Not Durable Execution"** — `diagrid.io/blog/checkpoints-are-not-durable-execution-why-langgraph-crewai-google-adk-and-others-fall-short-for-production-agent-workflows` (Yaron Schneider, Feb 25 2026, fetched 2026-05-06).
- Specific technical claim: LangGraph/CrewAI/Google ADK provide *save points* but require the developer to be the orchestrator — to detect failure, lease, dedup, and resume. Quote: "What they actually give you is a save point... That's a far cry from production-grade durability."
- Failure modes in LangGraph specifically: (a) **no automatic failure detection** ("If your process crashes, no one knows. There is no supervisor, no watchdog, no heartbeat mechanism"); (b) **no automatic resumption**; (c) **no duplicate-execution prevention** ("If two processes try to resume the same `thread_id` simultaneously... LangGraph has no built-in coordination"); (d) **single-process execution** in OSS.
- Concrete example of CrewAI's `@persist`: saves state but does not auto-resume; "you have to add conditional logic to every method... `if self.state.step_completed >= 2: return`."
- Google ADK is "the most architecturally sophisticated" with event-sourcing and `ResumabilityConfig` (v1.14.0+) and `ReflectAndRetryToolPlugin` (v1.16.0+), but still requires the caller to detect failure and re-invoke.
- The contrast with **durable execution** (Dapr Workflows, Temporal-class systems): "Every await point in your workflow is automatically a checkpoint... Before executing any workflow step, the runtime creates a durable reminder... If the process, Dapr, or even the entire cluster crashes, the reminder automatically reactivates the workflow and retries indefinitely, without any human or external system intervention." Workflow function "replays from the beginning, but completed activities return their stored results from the event log instead of re-executing."
- The position: "The gap is between saving state and guaranteeing completion and it requires a runtime that takes ownership of the workflow lifecycle, not one that hands you a snapshot and wishes you well."
- Strong on naming the architectural gap and its specific manifestations. Weak on: it is a vendor (Dapr) post and ends with a Dapr Agents pitch; the **architectural argument is sound but the framing is partial** — it doesn't fully credit LangGraph Platform (managed) which adds some of the missing pieces (auto-checkpointer provisioning, but still single-thread OSS semantics for the runtime guarantees).

**Temporal documentation** — `docs.temporal.io/evaluate/understanding-temporal`, `temporal.io/blog/temporal-replaces-state-machines-for-distributed-applications`.
- Mechanism: every workflow API call sends a Command to the Temporal Service; Commands map to Events in the durable Event History; on crash, Worker replays Event History to reconstitute state to immediately-before-crash, then resumes.
- Determinism constraint: workflow code must be deterministic (no random, no wall clock, no direct I/O — all I/O happens in Activities, which are non-deterministic but checkpointed).
- Quote: "It's as if your function is atomically persisted at each await point."
- Activities replay from cache, not from re-execution; workflow code re-runs but is short-circuited at each previously-completed activity by the Event History.
- Cost: forces the workflow author into a very specific programming model (deterministic functions, separated activities); learning curve and migration are non-trivial.

**Restate, Inngest, DBOS, Hatchet** (substrate-level survey, not re-deepened this session beyond Kai Waehner's 2025 blog and Diagrid's comparison page). Restate and DBOS are emerging durable-execution engines with similar event-sourced replay semantics; Inngest is event-driven serverless workflow; Hatchet is queue-and-workflow. The substrate's coverage holds at depth; nothing new to add.

**AWS, "Build durable AI agents with LangGraph and Amazon DynamoDB"** — `aws.amazon.com/blogs/database/build-durable-ai-agents-with-langgraph-and-amazon-dynamodb/`.
- DynamoDBSaver schema: PK (String) partition, SK (String) sort, optional `ttl` attribute for automatic expiration, S3 offload for payloads >350KB.
- Compression on by default; TTL controls retention.
- OSS package `langgraph-checkpoint-aws`.
- Confirms LangGraph's "checkpoint = state at super-step" with concrete persistence schema. Does not address Diagrid's automatic-failure-detection gap; AWS's recommendation for that layer is Bedrock AgentCore Runtime.

**Aider git workflow** — `aider.chat/docs/git.html`, `aider.chat/docs/usage.html`, `aider.chat/docs/config/options.html`.
- `--auto-commits` (default true): every change committed atomically with descriptive message generated by `--weak-model`.
- `--dirty-commits` (default true): preexisting uncommitted user changes get committed *first* with a separate message before aider's edits.
- `--attribute-author` and `--attribute-committer` mark aider authorship; `--attribute-co-authored-by` adds Co-authored-by trailer.
- `/undo`, `git revert HEAD`, branch-based rollback are the documented rollback primitives.
- Combined cost savings on long sessions with prompt caching: "30–70%" per DeployHQ analyst guide. [MODERATE]

**Claude Code documentation** — `code.claude.com/docs/en/overview` (substrate cite). Behavioral observations from Anthropic's harness post: starts each session with `pwd`, reads progress files, runs git log, smoke-tests; ends with descriptive commits. Git is the primary state ledger; `claude-progress.txt` is the human-readable scratchpad.

#### 2.3.3 Patterns and primitives at depth

**LangGraph checkpoint schema (DeepWiki, paraphrased).**
```
checkpoint:
  config:        { thread_id, checkpoint_id, checkpoint_ns }
  metadata:      { source, writes, step }
  values:        <full graph state at super-step>
  next:          <node names to run>
  tasks:         [ { node, interrupt? } ]
  created_at:    <timestamp>
  parent_config: <reference to previous checkpoint>
pending_writes:  [ { task_id, node, channel, value } ]   ← intermediate, pre-commit
```

**Cadence:** every super-step. Not every tool call (a parallel-node super-step bundles multiple tool outputs). Not every token. **What's stored:** full state snapshot per checkpoint, *not* deltas. (Implementations may compress; AWS DynamoDBSaver compresses by default.)

**Resumption when tools change:** if you compile the graph with a new tool definition and resume an old `thread_id`, behavior is undefined-ish — the persisted state references the old tool's structure; the graph definition expects the new. Practical pattern: version your graph definitions and pin `thread_id`s to a graph version; on tool-set migration, terminate threads gracefully or migrate state explicitly. Not a documented LangGraph feature; **operational responsibility falls on the application.** [MODERATE — inferred from LangGraph design + practitioner reports]

**RPO/RTO in practice (LangGraph):**
- RPO: super-step granularity. If you crash mid-super-step (e.g., node 2 of 5 has finished, node 3 is in-flight), pending_writes preserve node 1+2's results; node 3 re-runs from scratch on resume.
- RTO: cold-start the process + load the latest checkpoint by `thread_id` (single Postgres/Dynamo query) + re-execute from `next` → seconds for small state, minutes if state is large.
- **Both depend on the application detecting the crash and triggering the resume.** (Diagrid's central point.)

**Diagrid's mechanism-level argument (steelmanned).** The architectural mechanism missing in LangGraph that durable-execution engines provide:
1. **Reminder-based reactivation.** Before executing any step, the runtime registers a durable reminder. If the process dies, the reminder fires from the durable scheduler and reactivates the workflow on any available worker. LangGraph has no scheduler.
2. **Distributed lease coordination.** Two workers attempting the same workflow are arbitrated by the runtime via consistent-hash placement. LangGraph has nothing.
3. **Deterministic replay with activity caching.** Workflow code re-runs from the beginning; each previously-completed activity returns its cached result without re-execution. LangGraph re-runs only from the last super-step but does not guarantee non-determinism boundaries — application code must avoid non-determinism manually.
4. **Exactly-once semantics for activities (with idempotency keys at the application layer).** LangGraph offers no exactly-once guarantee.

**The honest disagreement, not flattened:** LangGraph's design choice is that *most agent workflows do not need this*. A solo-founder running n8n with a single agent process and no SLA is correctly served by checkpointing alone. A team running 1000 concurrent customer-facing agents with revenue tied to completion needs durable execution. The two camps are not arguing about the same workload class. **The decision-point**: when concurrent retries can corrupt shared external state (DB, payment processor, ticketing system), checkpointing is insufficient.

**Git-as-state in Claude Code / Aider.**
- *When does the agent commit?* Aider: after every successful edit (auto-commit). Claude Code (per Anthropic harness post): at the end of each session, after a feature is verified.
- *What's in commits?* Code changes. Aider: code only by default. Claude Code: code + changes to `feature_list.json` (`passes:false→true`) + appended-to `claude-progress.txt`. Tool outputs and planning are *not* in commits — they live in `claude-progress.txt` and the message history.
- *Rollback mechanics.* `git revert HEAD`, `git reset --hard <prior>`, branch rewind. Aider's `/undo` reverts the last aider commit specifically.
- *Rebase/squash/amend impact.* All three rewrite history → break replay if any external system held SHAs as references. Practitioner discipline: never amend or rebase commits the agent has logged in `claude-progress.txt`. [MODERATE — convention not enforced by tooling]

**Two-phase commit across mediums (filesystem AND external API AND DB).** *Real 2PC is not shipping in any of the surveyed agent harnesses.* The practical pattern is **best-effort with idempotency keys + human reconciliation**:

```
Step 1: Generate idempotency_key = hash(thread_id + step_id + input)
Step 2: Persist checkpoint (LangGraph: super-step write to DynamoDB)
Step 3: Call external API with idempotency_key in header
        - Retry on transport errors (server can dedup)
        - On timeout: re-call same idempotency_key; server returns cached response
Step 4: Write side-effect record into State Ledger
Step 5: On step replay: check State Ledger; skip if idempotency_key already-recorded
```

A "State Ledger" in this pattern is a small append-only table (DynamoDB / Postgres) with `(thread_id, step_id, idempotency_key, response_hash, timestamp)`. None of LangGraph's official docs publish this exact schema as a primitive; it's the practitioner pattern that fills the gap Diagrid names. [MODERATE — synthesized from AWS DynamoDBSaver patterns + Temporal's idempotency guidance + Stripe-style API conventions]

**Pruning / GC in long-running agents.**
- DynamoDBSaver: `ttl_seconds` on checkpoint records; expired rows auto-deleted by DynamoDB TTL.
- Aider: `.aider*` files in `.gitignore`; chat history file (`.aider.chat.history.md`) can be summarized/truncated via `--max-chat-history-tokens`.
- Claude Code: compaction is the GC mechanism for context; git is the durable retention; no automated git-history GC documented.
- **Failure mode:** pruning removes a checkpoint that a still-running thread needs to resume, or a session file the next agent expects. Mitigation: never prune *active* `thread_id`s (lock or mark active); retain the latest N checkpoints per thread regardless of TTL; tombstones on pruned threads so resumes fail loudly rather than silently restarting.

#### 2.3.4 Tradeoffs at depth

| Axis | LangGraph checkpointing | Temporal (event-sourced replay) | Git-as-state (Aider/Claude Code) |
|---|---|---|---|
| Cost (infra) | low (Postgres/Dynamo) | medium (Temporal Cluster or Cloud) | none beyond local disk |
| Latency (per step) | low (single write) | low (Command batched) | low |
| Reliability (single process) | medium | high | medium |
| Reliability (distributed) | low (no coord) | **high** (placement, lease) | n/a |
| Debuggability | high (state snapshots) | very high (full Event History) | **highest** (git diff) |
| Cache hit rate | n/a (state, not prompt) | n/a | n/a |
| RPO | super-step (~seconds) | per-await (~ms) | per-commit (~seconds-minutes) |
| RTO | seconds-minutes (manual restart) | **automatic** (reminder fires) | seconds (re-read) |
| Operational complexity | low-medium | medium-high (deterministic constraint) | low |
| Deterministic vs. probabilistic | deterministic (state) wrapped around probabilistic (LLM) | **strict deterministic boundary** required | deterministic (filesystem) |

#### 2.3.5 Failure modes in the field

- **LangGraph concurrent-resume corruption.** Two workers picking up the same `thread_id` after a partial failure each re-execute from the same checkpoint, causing duplicate external-API calls and divergent state writes. Diagrid documents this; the LangGraph docs do not promise prevention. Mitigation = application-level locking (Redis lease, DB unique constraint).
- **CrewAI conditional-skip-logic-everywhere.** `@persist` saves state but resume requires you to add `if self.state.step_completed >= N: return` to every method. Easy to forget; produces silent re-execution.
- **Google ADK tool exception kills entire workflow.** Documented: "an unhandled exception in a tool can propagate up and terminate the entire multi-agent workflow." Recommended mitigation is convention (return error dicts), not guarantee.
- **Aider rebase/squash breaks replay.** If an agent logs SHAs and you rebase/squash, the agent's references dangle. No tooling enforcement.
- **Claude Code premature `passes:true`.** Documented in the Anthropic harness post. Mitigation = strongly-worded prompt + Puppeteer E2E gate.
- **Memory pruning racing active sessions.** Common across DynamoDB/Redis-backed checkpointers when TTL is misconfigured.
- **AWS Bedrock AgentCore vs. self-hosted LangGraph DynamoDBSaver** — AgentCore wraps the missing pieces (scaling, monitoring) but the core checkpointing primitive is the same; do not assume AgentCore solves Diagrid's gaps without verifying.

#### 2.3.6 Open questions and unresolved debates

- **Is durable execution worth the determinism constraint for solo-founder workloads?** Diagrid says yes-eventually; LangGraph implicitly says no-for-most. **Genuinely unresolved.** The pragmatic threshold (this builder's read of the literature): durable execution earns its keep when (a) >1 concurrent agent acts on shared external state, (b) workflows span >hours and crash recovery is business-critical, (c) regulatory audit trails are required. Below that threshold, LangGraph checkpointing + idempotency keys + git is sufficient.
- **Can you bolt durable-execution semantics onto LangGraph?** Diagrid claims structurally no without runtime rearchitecture. Some practitioners attempt it via wrapping nodes in Temporal Activities; Diagrid calls this a "DIY marketing honeytrap."
- **What `claude-progress.txt` schema converges?** Open; Anthropic has not published one and no community standard has emerged.
- **Cross-medium 2PC in agent harnesses:** practical convergence around idempotency-key + State-Ledger pattern, but no library has standardized it. Open opportunity.

#### 2.3.7 For-the-builder implications

For your local-first multi-LLM harness with self-hosted n8n: adopt LangGraph-style checkpointing for orchestration state (Postgres or SQLite locally), backed by an explicit State Ledger table for external-API side-effects keyed by idempotency hash. Use git as the durable artifact ledger for code/prompts/feature-state, exactly as Anthropic's two-prompt harness prescribes; do not amend or rebase commits the agent has logged. Defer Temporal-class durable execution until you have concrete concurrency or SLA pain — the determinism constraint will fight your existing n8n-centric design. Build a small reconciliation tool that, on resume of a `thread_id`, queries the State Ledger and surfaces any in-flight external operations to you for human reconciliation rather than auto-retrying. Set DynamoDB/SQLite TTLs generously (≥30 days) and never prune an active thread.

---

## §3 Cross-Topic Synthesis

### 3.1 Architectural couplings

**Coupling C1 — Prompt cache constrains compaction.** Because compaction rewrites the message tail, it invalidates the message-level cache and forces a full cache write on the next request. **Implication:** schedule compaction events at natural cache-TTL boundaries (every ~4 minutes for 5-min cache, or per session for 1-hr cache); do not compact mid-burst. Practitioner pattern: emit a compaction-cost telemetry counter and amortize compaction cost by deferring until ≥70% of context window is consumed.

```
   ┌───────────── stable prefix (cached) ─────────────┐ ┌─ tail (varies) ─┐
   │ tools | system | early conversation              │ │ recent turns    │
   └──────────────────────────────────────────────────┘ └─────────────────┘
                                            ▲ compaction rewrites here
                                            ▼ → invalidates messages cache
                                            └─ tools/system cache survives
```

**Coupling C2 — Memory tier constrains compaction preservation.** The CoALA-tier in which a fact lives determines whether compaction can drop it:
- **Working memory (in context):** at risk of being summarized away.
- **Episodic (NOTES.md, claude-progress.txt):** durable to compaction by design (it's outside the context window; agent re-reads it).
- **Semantic (CLAUDE.md, knowledge base):** durable; reloaded fresh per session.
- **Procedural (skills, tools):** durable (frozen for the cache epoch).

**Implication:** any fact whose loss would regress the agent must be promoted to episodic+ before compaction can fire. The compaction prompt should explicitly include "before summarizing, ensure all open constraints, decisions, and TODOs have been written to NOTES.md."

**Coupling C3 — Durable-state substrate constrains prompt registry choice.** If your durable substrate is git (Aider/Claude Code style), prompts in git are natural and atomic — one PR moves prompts, evals, and code together. If your durable substrate is a service-managed checkpointer (DynamoDB/Postgres/Temporal), prompts in a registry that can be versioned at runtime *might* let you A/B-route without redeploying — but you lose atomic deploy. **Decision rule:** match prompt-storage durability to workflow-state durability. Mismatched substrates create skew (workflows resume on old prompts; new prompts apply only to new threads).

**Coupling C4 — JIT retrieval is a cache-prefix discipline.** JIT requires the agent to make tool calls into the message tail; each call invalidates its own segment of the cache. To make JIT pay off, the *static* JIT-enabling prefix (filesystem layout description, tool definitions, navigation primitives) must be cached aggressively. JIT works only because the static "you have glob/grep available" prelude is cached forever and the dynamic "here's the file content" suffix is the only uncached cost.

### 3.2 Shared primitives across topics

| Primitive | Topic 1 (prompts) | Topic 2 (context) | Topic 3 (state) |
|---|---|---|---|
| **Idempotency key** | not applicable | n/a | core: dedups external side-effects on replay |
| **Hash-of-prefix** | cache key | n/a | analog: git commit SHA |
| **Append-only log** | n/a | claude-progress.txt | git history; Temporal Event History; LangGraph checkpoint chain |
| **Schema-versioned artifact** | prompt files (git) | feature_list.json | LangGraph state schema; DynamoDB checkpoint row |
| **Domain expert as gate** | LLM-judge alignment (Husain/Shankar) | error analysis on traces | human reconciliation on replay divergence |
| **Pre-warm / smoke-test** | `max_tokens:0` cache pre-warm | session-start `pwd → init.sh → Puppeteer test` | `git log --oneline -20` startup ritual |
| **Tombstones** | cache silent-zero detection | n/a | pruned-thread tombstones |

### 3.3 Source-level convergence and divergence

**Convergence: Anthropic context-engineering (Sept 29 2025) ↔ Anthropic long-running-harnesses (Nov 26 2025).** The Sept post lays out compaction / notes / sub-agents as alternatives. The Nov post says, on real long-horizon work, **compaction alone is insufficient** and you need durable artifacts (git, JSON state, progress log) that survive across context windows. The two posts layer rather than contradict: the Sept post is about *what* context to keep within a session; the Nov post is about *how to bridge* across sessions. The durable artifacts of the Nov post are the structured-note-taking primitive of the Sept post, taken seriously.

**Divergence: Husain evals ↔ LangGraph checkpointing.** Husain treats evals as the primary correctness mechanism; checkpointing is barely mentioned. LangGraph treats checkpointing as the primary durability mechanism; evals are downstream tooling (LangSmith). The two communities have **non-overlapping epistemics**: Husain is data-quality-driven (look at traces, label, iterate); LangGraph is workflow-state-driven (persist, resume, time-travel). A complete agent harness needs both: evals to know whether the LLM is doing the right thing, checkpointing to know where it was when it crashed. Neither alone is sufficient.

**Convergence: Diagrid ↔ Husain on operational realism.** Different topics, same posture: don't believe the marketing ("checkpointing = production-grade durability"; "off-the-shelf evals = production-grade quality"). Both demand a higher engineering bar.

### 3.4 Decision points the cluster collectively defines

1. **Prompt versioning substrate:** git vs. registry → use git unless ≥3 non-engineer authors or runtime-A/B routing required.
2. **Cache-TTL choice:** 5m (default, refreshed on hit) vs. 1h (2× write cost) → 1h only when prompts run less frequently than every 5min but more than every hour.
3. **JIT vs. RAG-dump:** JIT for dynamic corpora with navigation primitives; RAG-dump for stable knowledge corpora.
4. **Compaction vs. handoff (within vs. across context windows):** compaction within a session for conversational continuity; two-prompt handoff across sessions for project continuity.
5. **Checkpointing vs. durable execution:** LangGraph-style checkpointing until concurrent retries on shared external state become a real risk.
6. **Single agent vs. sub-agents:** single agent until token cost (sub-agents = ~15× chat) is justified by parallel exploration value.
7. **Eval gate composition:** ~3–5 code-based assertions per LLM-judge gate.
8. **Memory tier residence:** working (context) → episodic (NOTES.md) → semantic (CLAUDE.md) → procedural (tools/skills) → durable (git).

---

## §4 Open Questions and Recommended Next Probes

1. **`claude-progress.txt` schema convergence.** Probe: search GitHub for `claude-progress.txt` files in public repos using the Anthropic `claude-quickstarts/autonomous-coding` template; extract field structures. Cite the actual emerging convention rather than inventing one.
2. **Per-model context-rot operating curves for Sonnet 4.5 / Opus 4.5 specifically.** Chroma's data covered Sonnet 4 / Opus 4. Probe: re-run their public methodology (`github.com/chroma-core/context-rot`) on the 4.5 series; expect partial improvement but the multi-factor degradation pattern to persist.
3. **State Ledger pattern standardization.** No library publishes a canonical State-Ledger schema for cross-medium idempotency in agent harnesses. Probe: survey Inngest / Restate / DBOS docs for an emerging convention.
4. **OpenTelemetry GenAI conventions stability date.** Currently in development; capture-content attributes (`gen_ai.input.messages`) opt-in only. Probe: monitor `opentelemetry.io/docs/specs/semconv/gen-ai/` for stability promotion to track when instrumentation libraries can safely emit input/output content by default.
5. **Whether code-execution-with-MCP becomes the default tool surface.** Anthropic's Nov 4 2025 post is influential but no community library has shipped a canonical implementation. Probe: monitor `anthropics/anthropic-cookbook` for a code-execution-MCP recipe in the next 2–3 months.
6. **Diagrid's "groundbreaking technical advancements" for transparent durable-execution-on-LangGraph.** Diagrid signaled (Feb 2026) work to provide automatic recovery to LangGraph "with little to no code changes." Probe: revisit `diagrid.io/blog` Q3 2026.
7. **`arxiv:2603.29194` corroboration.** Track citation count and replication of the multi-layer memory framework numbers; downgrade or upgrade confidence accordingly.

---

## §5 Source Bibliography (deduplicated)

**Substrate-cited and re-engaged at depth this session [deepened]:**
- Anthropic, "Prompt caching," `platform.claude.com/docs/en/build-with-claude/prompt-caching`, fetched 2026-05-06. [deepened]
- Anthropic Cookbook, "Prompt caching" notebook, `github.com/anthropics/anthropic-cookbook/blob/main/misc/prompt_caching.ipynb`. [deepened]
- Anthropic, "Effective context engineering for AI agents," Sept 29 2025, `anthropic.com/engineering/effective-context-engineering-for-ai-agents`. [deepened]
- Anthropic, "Effective harnesses for long-running agents," Justin Young, Nov 26 2025, `anthropic.com/engineering/effective-harnesses-for-long-running-agents`. [deepened]
- Anthropic, "Code execution with MCP," Nov 4 2025, `anthropic.com/engineering/code-execution-with-mcp`. [deepened]
- Chroma Research (Hong, Troynikov, Huber), "Context Rot: How Increasing Input Tokens Impacts LLM Performance," July 14 2025, `research.trychroma.com/context-rot`. [deepened]
- Hamel Husain & Shreya Shankar, "LLM Evals: Everything You Need to Know," Jan 15 2026, `hamel.dev/blog/posts/evals-faq`. [deepened]
- Hamel Husain, "Your AI Product Needs Evals," `hamel.dev/blog/posts/evals`. [deepened]
- Shankar et al., "Who Validates the Validators?", UIST '24, `arxiv.org/abs/2404.12272`. [deepened]
- Vir, Shankar, Chase, Fu-Hinthorn, Parameswaran, "PROMPTEVALS," Apr 20 2025, `arxiv.org/abs/2504.14738`. [deepened]
- Eugene Yan, "Patterns for Building LLM-based Systems," `eugeneyan.com/writing/llm-patterns/`. [substrate]
- HumanLayer, "12-Factor Agents," Factor 2 + Factor 3, `github.com/humanlayer/12-factor-agents`. [deepened]
- Spring AI, "Prompt Caching Support in Spring AI with Anthropic Claude," Oct 27 2025, `spring.io/blog/2025/10/27/spring-ai-anthropic-prompt-caching-blog`. [deepened]
- OpenTelemetry GenAI semantic conventions for spans, `opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/` and `.../gen-ai-agent-spans/`. [deepened]
- LangGraph Checkpointing Architecture, DeepWiki, `deepwiki.com/langchain-ai/langgraph/4.1-checkpointing`. [deepened]
- LangGraph durable execution and human-in-the-loop, `docs.langchain.com/oss/python/langgraph/durable-execution`, `docs.langchain.com/oss/python/langchain/human-in-the-loop`. [deepened]
- Aider git workflow, `aider.chat/docs/git.html`, `aider.chat/docs/usage.html`, `aider.chat/docs/config/options.html`. [deepened]
- Claude Code documentation, `code.claude.com/docs/en/overview`. [substrate]
- Diagrid, "Checkpoints Are Not Durable Execution," Yaron Schneider, Feb 25 2026, `diagrid.io/blog/checkpoints-are-not-durable-execution-why-langgraph-crewai-google-adk-and-others-fall-short-for-production-agent-workflows`. [deepened]
- Temporal documentation, `docs.temporal.io/evaluate/understanding-temporal`, `temporal.io/blog/temporal-replaces-state-machines-for-distributed-applications`. [deepened]
- Liu et al., "Lost in the Middle," `arxiv.org/abs/2307.03172`, TACL 2024. [substrate]
- Sumers, Yao, Narasimhan, Griffiths, "Cognitive Architectures for Language Agents (CoALA)," TMLR 2024, `arxiv.org/abs/2309.02427`. [substrate]
- AWS, "Build durable AI agents with LangGraph and Amazon DynamoDB," `aws.amazon.com/blogs/database/build-durable-ai-agents-with-langgraph-and-amazon-dynamodb/`. [deepened]
- Lance Martin, "Context Engineering for Agents," `rlancemartin.github.io/2025/06/23/context_engineering/` and `blog.langchain.com/context-engineering-for-agents/`. [deepened]
- Drew Breunig, "How Contexts Fail," `dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html` (referenced via secondary corroboration). [substrate]
- Tiwari et al., "Multi-Layered Memory Architectures for LLM Agents: An Experimental Evaluation of Long-Term Context Retention," `arxiv.org/abs/2603.29194`. [deepened — existence confirmed; numbers not corroborated]

**New beyond substrate this session [new]:**
- Lee et al., "Lost in the Noise: How Reasoning Models Fail with Contextual Distractors," `arxiv.org/pdf/2601.07226`, Jan 13 2026 — corroborates Chroma findings under agentic workflows. [new]
- McKinnon, "Retrieval Quality at Context Limit," `arxiv.org/pdf/2511.05850` — Gemini 2.5 Flash partially mitigates Lost-in-the-Middle on factoid Q&A. [new]
- Modarressi et al., "Positional Biases Shift as Inputs Approach Context Window Limits," `arxiv.org/pdf/2508.07479` — primacy-bias drops near window limits, complicates LiM picture. [new]
- Anthropic, "Advanced tool use" / Tool Search Tool, `anthropic.com/engineering/advanced-tool-use` — companion to code-execution-with-MCP, reports Opus 4 49%→74%, Opus 4.5 79.5%→88.1% on MCP evals. [new]
- AWS DynamoDB LangGraph checkpoint developer guide, `docs.aws.amazon.com/amazondynamodb/latest/developerguide/ddb-langgraph-checkpoint.html`. [new]
- "Memory for Autonomous LLM Agents: Mechanisms, Evaluation, and Emerging Frontiers," `arxiv.org/pdf/2603.07670` — taxonomy of five memory mechanism families (context-resident compression, retrieval-augmented stores, reflective self-improvement, hierarchical virtual context, policy-learned management). [new]
- "Rethinking Memory in LLM-based Agents: Representations, Operations, and Emerging Topics," `arxiv.org/pdf/2505.00675` — six fundamental memory operations (Consolidation, Updating, Indexing, Forgetting, Retrieval, Compression). [new]

Total new beyond substrate: 7 (within the 6–12 calibration target).