# NotebookLM Deep-Dive Findings — implementable mechanisms for DESIGN.md

*Companion to `notebooklm-research-findings-for-council.md` (broad open-question answers) and `memory-corpus-evidence-for-council.md` (empirical graph evidence). This doc goes DEEP on the three mechanisms that most directly shape the grounding design, each with a follow-up. Generated 2026-06-04 against the Agent Harness Engineering corpus (`57b8d946-…`). 169 source citations across the 5 deep queries. Additive evidence input — does not author DESIGN.md.*

---

## Deep-dive 1 — ICM (the CHARTER's named methodology), now fully specced  *(C2 / WS-1 / WS-2)*

**Hard citable anchor:** **Van Clief & McDermott (2026), *Interpretable Context Methodology: Folder Structure as Agent Architecture*, arXiv:2603.16021v2** (+ `RinDig/Interpreted-Context-Methodology` companion repo). The CHARTER's "interpretable-context methodology (folder architecture)" is *this*. The council can cite it directly.

**Full spec (load-bearing details):**
- **Numbered stage folders** (`01_…`, `02_…`) where *folder-numbering encodes stage sequencing*; one stage's `output/` is the next stage's input. Context-scoping = folder hierarchy; state = files on disk; observability = every step is inspectable plain text (no dashboard).
- **`CONTEXT.md` stage contract** — three mandatory sections: **Inputs** (exact files *and specific sections* the agent may load), **Process** (role + step-by-step logic), **Outputs** (format + destination). The Inputs table is the anti-bloat mechanism — the agent sees only minimum high-signal tokens.
- **Docs-over-outputs rule** — agents are *forbidden from reading their own prior outputs* to learn patterns; they read canonical reference docs (Layer 3) instead. Rationale: "early outputs are the worst outputs"; learning from them compounds errors. **(Directly mirrors the harness's design-substrate-is-canonical + the workspace memory "no code-derivable saves" discipline.)**
- **Stage audits** = checklists run *after a stage completes but before output is written*, each with an **unambiguous binary pass/fail condition** (deterministic validation). **(This is C5's gate model, at the folder layer.)**
- **Five-layer context hierarchy:** L0 Identity · L1 Workspace · L2 Stage · L3 Reference Material (the "Factory") · L4 Working Artifacts (the "Product", offloaded to `output/`). **Strict Factory↔Product split: the "how" (instructions) never grows with the "what" (logs/data).**
- **Selective Section Routing:** Inputs reference exact markdown headers (`output/01_plan.md#architecture_decisions`) — not whole files — to keep context lean.
- **Composes with** Claude Code lifecycle hooks (deterministic enforcement without the LLM remembering) and MCP (complementary: ICM = context delivery, MCP = tool access).

**Retrofit sequence onto the bloated CLAUDE.md** (the council's exact WS-1 situation — 340KB, 81% provenance):
1. Initialize ICM skeleton (`_core/` + numbered stage folders).
2. Decompose by layer: L0 identity → global; L1 standards/invariants → workspace `CLAUDE.md`; L2 procedures → per-stage `CONTEXT.md`.
3. **Externalize the 81% provenance to L3 Reference (`CHANGELOG.md` / Memory-Bank), checked into repo, read on demand — out of the active prefix.**
4. Implement per-stage Inputs/Process/Outputs contracts (selective loading replaces the flat store).
- Cross-stage state without re-bloat: selective section routing + L4 disk offload (`read_file`/`grep` to retrieve, not pre-load).

**ICM failure modes the council MUST design mitigations for (risk register):**
- **Model misrouting** — LLM misreads L2→L3 mapping or can't find an Inputs-table file. *(Mitigation: index integrity gate — exactly the evidence doc's link-integrity `--check`.)*
- **Lost global constraints** — a Stage-1 constraint forgotten by Stage-5 if not passed through the contract. *(Mitigation: a "Reality-Checker"/Architect meta-pass auditing full filesystem state — maps to C1 orchestration + the council's own adversarial pass.)*
- **Manual-review overhead** at solo scale; **audits-by-convention, no deterministic validation runtime** (unlike DeerFlow). *(Mitigation: this is precisely why C5's automated `--check` gates matter — they convert ICM's human checklists into deterministic gates.)*
- **Fails at concurrent multi-user / real-time multi-agent** (no distributed coordination layer). *(Bounds scope: ICM is local-first / solo — which matches the harness persona; but FM-H cross-worktree concurrency is exactly the edge ICM does NOT cover → reinforces the detection-first OCC remedy.)*

---

## Deep-dive 2 — Claude Code's compaction + prompt-cache internals (the §2 problem, mechanically)  *(C2 / C7 / WS-1 / WS-5)*

**Tiered compaction (exact thresholds — citable for WS-5/WS-6):**
- **MicroCompact** — zero-API-call; sheds bulky tool outputs to disk, leaves a reference; keeps a "hot tail" of recent results.
- **AutoCompact** — triggers at **95–98% capacity**; reserves a **13K-token buffer**; emits a structured summary up to **20K tokens**; circuit-breaker after **3 consecutive compaction failures**.
- **FullCompact** — tears down + reboots a fresh session; **re-injects** user intent + key decisions + **5 most-recent files (≤5K tokens each)** + active plans/TODOs + relevant skill schemas; resets working budget to **50K tokens**.
- **Manual `/compact`** — at task boundaries; accepts a **focus hint** (`/compact Focus on API changes`).

**The §2 cache-detonation, diagnosed:**
- `CLAUDE.md` is auto-loaded into the **static system-prompt prefix**. Caching hierarchy is **tools → system → messages**, hash-of-prefix. **Any edit to `CLAUDE.md` invalidates the system block AND all subsequent message history** — a full cache miss. The harness's "60/60 recent commits touch §2" = a guaranteed cache detonation every turn.
- **Token signals:** `cache_creation_input_tokens` (**1.25×** price, 5-min TTL) · `cache_read_input_tokens` (**0.1× — 90% cheaper**; and **does NOT count toward ITPM rate limits**) · `input_tokens` (fresh, post-breakpoint).

**The fix (reframes WS-1 from byte-budget → cache architecture):**
1. **Static immutable prefix at top** (universal unchanging rules).
2. **Cache breakpoint** immediately after the immutable section.
3. **Dynamic volatile content at the bottom** (active goals, current specs, anything frequently edited — i.e. the provenance/change-log).
4. Static prefix must clear the model's min cacheable length (**1,024 tokens Sonnet / 4,096 Opus·Haiku**).
5. Up to **4 breakpoints** (after tools / after immutable CLAUDE.md / after volatile section / near end of history).
- **Metric (gives C7 a real instrument):** Cache-Hit-Rate = `cache_read / (cache_read + cache_creation + input)`; **target > 0.60** on stable workloads; payoff after **2 reads**. **Diagnostic: if `cache_read` is consistently 0 despite breakpoints, a dynamic block sits before your breakpoint** — which is exactly the §2-provenance-in-the-prefix failure.

**⇒ WS-1 reframe:** the win is not merely "≤40KB"; it is **moving §2 provenance below a cache breakpoint (or out of the prefix entirely)** so the static prefix stops detonating the cache. Measure success by `cache_read` ratio, not byte count.

---

## Deep-dive 3 — Letta/MemGPT tiering + a no-vector-DB file-store implementation  *(C3 / WS-3)*

**The OS/virtual-context model:** Main Context (RAM: read-only system + FIFO history + **Core Memory** = pinned editable fact blocks) ↔ External Context (disk: **Recall** = episodic event log; **Archival** = semantic facts). Transitions are **function calls** the model issues itself:
- **Page-out** to Recall as the FIFO fills (+ recursive summarization at the queue head); **page-in** via date/text search.
- **Page-out** to Archival via `archival_memory_insert` for facts that should persist but needn't be pinned; **page-in** via search.
- **Core Memory** self-edited via `core_memory_append` / `core_memory_replace`.
- **Consolidation ("sleep-time compute")** — every **50–200 episodes**, distill recent interactions (by recency/relevance/salience) into stable insights written to Archival/Core; raw transcripts stay in Recall for audit.

**Implementable on the harness's exact store (markdown + `MEMORY.md` + wiki-links, NO vector DB):**
- **Three-tier file mapping:** Working = live context + `SCRATCHPAD.md`; **Episodic = `episodic/` dir (or append-only `JOURNAL.md`/`SESSION_LOG.jsonl`) of raw timestamped traces** (incl. failed approaches); **Semantic = `semantic/` dir of distilled notes indexed by `MEMORY.md`.**
- **Consolidation trigger/cadence:** session-end hook **OR** episodic log > **20–50K tokens**; every **N episodes (50–200)** or task boundary; run as background daemon or manual `/compact` (don't block the interactive loop).
- **Consolidation inputs:** raw episodic logs (incl. failures) + current `MEMORY.md` (avoid duplication) + active `TODO`/`feature_list`.
- **Consolidated note schema (reconstruction-grade):** filename `semantic/slug.md`; YAML frontmatter (`tags`, `last_updated`, `related_notes`); distilled facts; decisions & rationale; **"failure warnings — what went wrong last time"** (single-shot error avoidance).
- **`MEMORY.md` index:** category headers + one-sentence per-note descriptions + wiki-links; **always loaded into the static *cached* prefix** (ties to Deep-dive 2); JIT-retrieve linked files; **selective section routing `[[note#section]]`** for large notes.

**⇒ The harness already runs a PARTIAL version of this** (`MEMORY.md` + per-note `.md` + `[[wiki-links]]`). The missing pieces the council's WS-3 should author:
1. **Episodic/semantic tier separation** — today `pr-*`/`fork-*` event-logs and pattern hubs sit in one flat tier; split episodic (`episodic/`) from semantic (`semantic/`). The evidence doc's **39 zero-inbound notes are episodic records that never consolidated.**
2. **A consolidation/reflection pass** — the harness writes memories ad hoc but has **no reflection step**; the `[[plan-revision-against-not-yet-built-substrate]]` referenced 5× but unwritten is a *consolidation that should have fired*.
3. **Cache-aware `MEMORY.md` placement** (static cached prefix) + **section routing** (`[[note#section]]`) for JIT leanness.
4. **The "failure warnings" field** in the note schema — the harness's `[[advisor-…]]`/`[[halt-route-…]]` hubs already encode this; formalize it.

---

## Composed picture — how the three deep-dives form ONE design
The grounding the council is designing is the composition of three production-validated layers:
- **C2 / folder architecture = ICM** (numbered stages, CONTEXT.md contracts, Factory↔Product split, selective section routing) — arXiv:2603.16021v2.
- **C2·C7 / prefix discipline = cache-aware CLAUDE.md** (static-immutable-prefix → breakpoint → dynamic-suffix; measure `cache_read` > 0.60) — the real WS-1 win.
- **C3 / retention = Letta-on-files** (episodic/semantic split + consolidation/reflection + cached navigable index) — Letta/MemGPT + ICM file-store mapping.

These are mutually reinforcing: ICM's L3 Reference = the semantic store; ICM's selective section routing = Letta's lean page-in = the cache-aware JIT load; ICM's stage audits = C5's deterministic gates that compensate for ICM's "no automated verification" failure mode. **The DESIGN.md MVP slice (WS-1 + WS-3 + a `--check` gate + recovery) is exactly the minimal cut of this composed model**, and every piece now has a named external-canon citation.

*Provenance: deep-dive queries (ICM structure + retrofit; Claude Code compaction + cache; Letta tiering + file-store impl) against notebook `57b8d946-…`; 9/22/32/29/35/42 citations respectively. Re-runnable via `notebooklm ask … --notebook 57b8d946-… [-c <conversation_id>]`.*

---

## Deep-dive 4 — Temporal validity & staleness (Zep / Graphiti)  *(C3 / WS-3 + WS-6)*
**Source:** Zep + Graphiti temporal knowledge graph (NotebookLM, 20 cites).
- **Bi-temporal model:** facts carry a **validity window** (`valid-at … invalid-at`). A contradiction is **never an overwrite** — the old fact's window is *closed* (`invalid-at` set) and a *new* fact node created; the agent knows what is true *now* and what was true *then*. Retrieval = semantic + BM25 + **temporal filter** (prefer currently-valid) → blocks stale-fact recall (e.g. old vs new address, high semantic similarity).
- **Directly implementable on the harness markdown store:**
  - Bi-temporal frontmatter: `valid_from`, `valid_until` (null = current), `superseded_by: [[new-note]]`.
  - **"Mark-and-New" supersede protocol:** on update, set old note's `valid_until` + `superseded_by`, create a fresh note — never edit-in-place.
  - **Staleness-maintenance loop:** scan for notes untouched > N days; inject *"Note X is 30 days old and claims Y — still accurate?"*; agent confirms or supersedes.
  - **Retrieval filter:** a memory-search tool that excludes `valid_until != null`.
- **⇒ Council:** this is the formal model behind the harness's existing "this memory is N days old — verify" reminder. WS-3's retention contract should adopt `valid_until`/`superseded_by` + Mark-and-New, turning the flat store into a *declarative temporal substrate*; pairs with the consolidation pass (Deep-dive 3).

## Deep-dive 5 — Eval-health gates: prove the slim-down didn't regress  *(C5 / C9 — recovery-completeness as co-requisite)*
**Source:** error-analysis-first eval methodology (NotebookLM, 28 cites).
- **Tiered validator cascade:** L1 code assertions (regex / JSON-schema / exec — e.g. verify the `[i]` citation format still emits *after* provenance eviction) → L2 LLM-as-judge (scoped binary Pass/Fail) → L3 human error-analysis (≥100 traces/cycle to calibrate the judge).
- **Regression sets from real production traces** (not synthetic), split Train 10–20% / Dev 40–45% / Test 40–45%. **Three probe types purpose-built for memory restructuring:** **recall** (facts survive compaction), **artifact** (agent knows which files it changed), **continuation** (resume a multi-step task).
- **Hard pre-deploy thresholds:** **TPR ≥ 0.90 · TNR ≥ 0.85 · judge-alignment Cohen's κ ≥ 0.70 · rolling cache-hit-rate > 0.60.**
- **Pairwise before/after judging** (Control = old context, Treatment = new) with bias mitigations: position (swap + re-judge), verbosity (length-normalize / rubric), self-enhancement (judge with a *different* model family).
- **CI wiring:** code assertions on a 20–50-trace dev fixture **block the PR**; a failed eval blocks merge.
- **⇒ Council:** before WS-1 evicts §2, stand up a small recall/artifact/continuation probe set + a `--check` that fails the PR on κ<0.70 or a recall-probe regression. This is how the slim-down is *proven* safe rather than assumed — and is exactly C9's "recovery-completeness is co-requisite, not follow-on."

## Deep-dive 6 — Agent context/memory artifact-file taxonomy
*NotebookLM 6a–6d (4 queries; 33/36/54/83 cites) + a web/Context7 gap-fill agent for undocumented files & adjacent standards.*

### 6.1 Per-file taxonomy
✅ established · ◑ single-tool / partial · ❌ not a convention

| File | Std? | Role (context/memory) | Fed to agent | Format | Size |
|---|---|---|---|---|---|
| **CLAUDE.md** | ✅ Anthropic | persistent project memory / procedural anchor | auto-load **system prefix**; re-read each turn | MD (+XML tags) | essential-only |
| **AGENTS.md** | ✅ open std (AAIF/Linux Fdn, 60k+ repos) | behavioral rulebook / identity; cross-harness | auto-load prefix (Codex/Agents-SDK; **NOT** Claude Code) | MD | **<60 lines; "pilot's checklist, every line earned by a failure"** |
| **GEMINI.md** | ✅ Gemini CLI | per-project + global (`~/.gemini/`) instructions | auto-load prefix | MD | global = prefs only |
| **.cursorrules / .cursor/rules/*.mdc** | ✅ Cursor | project rules / custom modes | auto-load by IDE modes | MD / MDC | per-repo rulebook |
| **.clinerules / .windsurfrules** | ✅ Cline / Windsurf | per-tool project rules | auto-load | MD / text | brief |
| **SOUL.md** | ◑ DeerFlow only | agent persona + skill self-evolution | auto-load, wrapped in `<soul>` tags | MD | (unspecified) |
| **SKILL.md** (`skills/<n>/`) | ✅ Anthropic Skills | portable capability; **progressive disclosure** | metadata (~100 tok) in prefix; body on trigger | MD + YAML frontmatter | desc short; body <500 ln / 5K tok |
| **WORKFLOWS.md** | ◑ commands/Skills pattern | reusable multi-step procedures | `.claude/commands/`; YAML-frontmatter skill, JIT | MD + YAML | <500 ln / 5K tok |
| **MEMORY.md** | ✅ common | semantic index / Memory-Bank root; ToC + wiki-links | **static cached prefix**; JIT-navigate linked notes | MD | index lines short |
| **memory-bank/** (Cline: projectbrief / productContext / activeContext / systemPatterns / techContext / progress) | ✅ Cline (+Kilo/Roo) | hierarchical persistent project memory | primed at session start; `activeContext`/`progress` are hot | MD dir | **split across ~6 files to bound each** |
| **PROGRESS.md / claude-progress.txt** | ✅ Anthropic long-running | session-continuity "lab notes"; log + failed approaches | read at session start (+ git log); updated at session end | MD / TXT | concise |
| **TODO.md** | ✅ common | task state outside the window; long-horizon coherence | agent self-writes; re-injected after reset | MD (headers) | minimal |
| **feature_list.json** | ✅ Anthropic | scope boundaries + testable completion (anti-"victory") | initializer writes once; coding agent reads each session | **JSON** (models hallucinate-overwrite JSON *less* than MD) | 200+ entries OK |
| **ARCHITECTURE.md** | ✅ common / Memory-Bank | system map / structural conventions | primed at session start | MD | concise, high-level |
| **DESIGN.md** | ✅ spec/PRD pattern | persistent blueprint/spec; anti-forgetfulness | primed; hierarchical-summarize via ToC, sections JIT | MD (+XML tags) | scales w/ complexity |
| **repomap.txt** | ✅ Aider | compressed repo map (class/fn defs); global awareness | auto-generated, fed by Aider | **plain text** | **1024-token budget** |
| **CONVENTIONS.md** | ✅ Aider | coding conventions, loaded **read-only / cached** | `aider --read` | MD | concise |
| **llms.txt** (+`llms-full.txt`) | ✅ open std (Answer.AI '24) | root-of-corpus curated map of what's inside | inference-time nav | MD (web root) | summary vs full |
| **GC.md** | ❌ **not a convention** | "context GC" is a runtime compaction *concept*, never a file | — | — | — |
| **ROUTING.md** | ❌ **not a convention** | routing = code/config (`modelPointers`/`fallbackChains`; RCR-Router) | — | — | — |
| **CATALOG.md** | ◑ tool-local only (Azure skills docs; MODERATE) | generated skill-index | — | MD | — |

### 6.2 Format decision rules
- **JSON** — state the agent must not corrupt (`feature_list.json`); programmatic; restricts edits. *Fails:* context-rot → invalid JSON; over-complex schemas.
- **Markdown** — instructions / skills / shared human+agent docs (the default). *Fails:* over-summarizes / drops subtle constraints as context fills.
- **XML tags inside MD** — delineate prompt sections (`<background>`/`<instructions>`/`<soul>`); separate rules from prior output. *Fails:* unbalanced / deeply nested → attention drift.
- **YAML** — frontmatter, declarative config, orchestrator DAGs. *Fails:* indentation sensitivity when the agent writes it.
- **Plain text** — append-only logs, repo maps, `llms.txt`; least token overhead for sequential records.
- **HTML** — sandboxed UI artifacts / visual verification only.

### 6.3 Size / token budgets (general)
skill metadata ~100 tok · AGENTS.md <60 lines · SKILL/WORKFLOWS body <500 lines / 5K tok · repomap 1024 tok · tool defs the hidden cost (~55K tok for 50 tools) · sub-agent distillation returns 1–2K · **"35-minute wall" at 80–150K accumulated tokens** (reasoning noise floor) · lost-in-middle 40–60% · compaction at 95–98%.

### 6.4 How the set is wired into a harness
- **Load order `tools → system → messages`** (hash-of-prefix cache hierarchy).
- **Cache breakpoint at the end of the static prefix (tools + system)** → ~90% read-cost cut; any mutation to tools/system invalidates everything after.
- **Auto-loaded prefix:** stable rules (CLAUDE.md/AGENTS.md), core tool defs, summarized history. **JIT-navigated:** everything else, pulled into the *messages tail* via `glob`/`grep`/`read` only when needed.
- **Cross-linking:** progressive disclosure (SKILL.md → deeper resources on read); a navigable index (MEMORY.md / ARCHITECTURE.md ToC) with `[[wiki-links]]` + **selective section routing** (`[[note#section]]`); memory tiers bridged by filesystem writes (working ↔ episodic JOURNAL/NOTES ↔ semantic MEMORY/CLAUDE).

### 6.5 What this means for the council's design
1. **Do not invent `GC.md` / `ROUTING.md` / `CATALOG.md`** — none is a real convention. Context-GC is a runtime compaction mechanism (Deep-dive 2); routing is CP code-config the harness already has (`modelPointers`/`fallbackChains` per CP spec); a tool/skill catalog, if ever needed, is a *generated index*, not a hand-authored doc.
2. **WS-2 navigation set** = established files: `ARCHITECTURE.md` (system map), `WORKFLOWS.md`/`HOOKS.md` (procedures / lifecycle-topology), a `MEMORY.md`/INDEX ToC with wiki-links + section routing. **Cline `memory-bank/`** (projectbrief/activeContext/progress) is a proven model for splitting persistent project memory across bounded files → directly informs WS-3 tiering.
3. **WS-1 (CLAUDE.md):** cache-aware split (Deep-dive 2) + format rule (instructions = MD + XML tags; volatile provenance *below* a breakpoint or out of the prefix). The `AGENTS.md` decision: under Claude Code it's safe-as-not-loaded, but it auto-loads under Codex/Agents-SDK — name the anchor deliberately if portability matters.
4. **WS-3 (memory) format split:** durable patterns = MD (semantic notes + MEMORY.md index); machine-state the agent must not corrupt (a retention ledger, the substitution tally) = **JSON** per the `feature_list.json` rule; episodic logs = append-only MD/JSONL.
5. **The composed model** (ICM folders + cache-aware prefix + Letta-on-files + temporal frontmatter + eval-gated changes) is the full grounding design; this taxonomy is its file-level instantiation.

*Provenance: NotebookLM dives 4–6 against `57b8d946-…` (20/28/33/36/54/83 cites) + web/Context7 gap-fill (aider.chat, docs.cline.bot, llmstxt.org, agents.md, github/google-gemini, agentskills.io, arxiv 2508.04903 + 2603.20380, learn.microsoft.com; accessed 2026-06-04). GC.md/ROUTING.md = no-convention (evidence-of-absence, strong); CATALOG.md = tool-local (MODERATE).*
