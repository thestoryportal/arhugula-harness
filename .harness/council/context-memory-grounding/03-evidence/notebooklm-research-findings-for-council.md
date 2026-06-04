# NotebookLM Research Findings — external canon for the Context/Memory Grounding Council

*Companion to `memory-corpus-evidence-for-council.md`. Input for **DESIGN.md** (Stage 3 / external-canon mode). Generated 2026-06-04 via 5 focused queries against the **Agent Harness Engineering** NotebookLM corpus (`57b8d946-…`; 28 URL-scrape compilations of production-harness primary sources). 224 source references across the 5 queries. Additive — does not modify any worktree deliberation artifact. Each finding tags the council voice + open question it moves, and the system(s) that establish the pattern.*

---

## Part A — The five OPEN questions, now answered against external canon

### Q#4 (AGENTS.md auto-load) — **ANSWERED; council assumption holds for Claude Code, with a portability caveat**
- **Claude Code auto-loads `CLAUDE.md` (and `.claude/CLAUDE.md`) at session start — NOT `AGENTS.md`.** `AGENTS.md` is the **OpenAI Codex / Agents-SDK** auto-load standard (the AAIF convention); Cursor uses `.cursorrules` / `.cursor/rules/*.mdc`.
- **⇒ WS-2:** the council's "`AGENTS.md` is a JIT-navigable anchor, NOT pre-loaded" is **correct under Claude Code**. **Caveat:** if the harness is ever driven by Codex/Agents-SDK, `AGENTS.md` *would* auto-load — so either (a) name the not-auto-loaded navigation anchors something other than `AGENTS.md` to avoid the cross-runtime collision, or (b) consciously adopt `AGENTS.md` as a *loaded* anchor and budget for it. **Decide explicitly in DESIGN.md.**
- **The JIT model to copy:** Claude Code's **SKILL.md progressive disclosure** — only name+description (~100 tokens) pre-loaded; full body loaded on trigger. This is the canonical pattern for WS-2's "navigate-to, don't pre-load." Devin spends **60% of its first turn retrieving context via `SWE-grep`** rather than pre-filling — JIT-over-eager is the production default.

### Q#5 (cut-list / retention tiering) — **ANSWERED; my degree-based tiering is canonical, not invented**
- **Canonical taxonomy = CoALA** (Cognitive Architectures for Language Agents): **working / episodic / semantic / procedural**. The harness memory store conflates **episodic** (`pr-*`/`fork-*`/`h-*` event-logs) and **semantic** (pattern/feedback hubs) in one flat tier — exactly the anti-pattern CoALA separates.
- **Letta/MemGPT** is the canonical implementation: **Main Context (working) → Recall Storage (episodic) → Archival Storage (distilled semantic)**, with the agent moving items between tiers via explicit tool calls. **⇒ maps 1:1 onto the evidence doc's tiers:** KEEP-HOT = Main; KEEP-LINKED = Recall; **ARCHIVE = Archival (my 39 zero-inbound notes)**.
- **Reference-count / centrality is an ESTABLISHED archival signal** — "three pipeline incidents on the same table ⇒ abstract into a semantic rule." This externally validates **(i)** the evidence doc's degree-keyed cut-list AND **(ii)** the workspace's own cardinality-≥2 pattern-save rule. *Tier by body-to-body in-degree is canon.*
- **Consolidation / Reflection** = the episodic→semantic promotion process. **⇒ Finding 4 of the evidence doc reframed:** `[[plan-revision-against-not-yet-built-substrate]]` referenced 5× but never written = a **consolidation trigger that hasn't fired** (5 refs ≫ threshold) → promote it to a semantic note.
- **Zep/Graphiti validity-windows** (facts carry validity windows; invalidate stale facts while retaining the episodic record) → a concrete model for C3's retention contract and the harness's existing "this memory is N days old — verify" staleness reminder.

### Q#2 (FM-H — detection-first vs prophylactic; un-versioned store) — **ANSWERED; field converges on detection-first + git-as-state**
- **Detection-first wins.** **Cursor explicitly pivoted from file-locks → Optimistic Concurrency Control (OCC)** (AWS/DynamoDB lineage) to remove lock bottlenecks: verify the store hasn't changed since last read (version/timestamp), resolve at commit. **⇒ validates AR-4** ("gate serialization behind a cheap detection step") — do **not** build prophylactic locks first; build a cheap OCC/version check.
- **The un-git-versioned-store fix (C9's finding) has canonical remedies:** **git-as-state** (Claude Code, Aider, kilocode — commits are the transactional/rollback unit) and **shadow-git per-step snapshots** (Cline, Roo Code — navigable snapshot timeline, granular rollback). **⇒ DESIGN.md C3 remedy:** git-version (or shadow-git snapshot) the memory store; rollback = snapshot timeline.
- **The harness already owns the deeper pattern.** **State-ledger + replay** (12-Factor Agents, LangGraph checkpoint-per-super-step, Temporal signal-gated writes) is the convergent durable-state model — and the harness *authored its own state-ledger/hash-chain for product state (IS spec)*. The council's central irony ("product has the contract, process doesn't") is externally underscored: **apply the existing state-ledger discipline to the process memory store.**
- **`parallelize-reads-serialize-writes` is the convergent default** (Anthropic MARS / Dify orchestrator-worker: lead agent alone writes; read-only sub-agents return distilled artifacts + lightweight refs). **⇒ validates CP-AL-1 and the FM-H remedy:** worktrees should not all write `MEMORY.md` directly; serialize through one writer.

### Q#3 (proportionality; advisory vs hard gates) — **ANSWERED; advisory-only caps demonstrably fail**
- **Strong evidence advisory caps fail:** OpenAI "Extreme Harness Engineering" instituted a **hard 1-minute max build-time gate** *because* advisory drifts — "humans and agents prioritize short-term completion over long-term health." The current **MEMORY.md advisory cap (27KB > 24.4KB, currently breached and ignored) IS the predicted failure mode.** **⇒ validates C5** (G1 byte-budget must be a `--check` hard gate, exits 1) and the evidence doc's link-integrity/index-coverage gates.
- **Principled advisory-vs-hard rule** (from the layered-validator-cascade canon — which mirrors the harness's own C5 ValidatorFramework): **structural failure ⇒ HARD** (schema, security boundaries, context-threshold); **heuristic optimization ⇒ ADVISORY** (style/conventions). Gives C5 a clean MVP-ranking criterion for WS-4 G1–G4.
- **Context-budget target is principled, not arbitrary:** canon says target **60–80% utilization** (not the hard window limit), and the **"Dumb Zone" at 40–60%** is where recall degrades. **⇒ WS-1's "≤40KB" should be re-derived as a % of the actual context window** (and paired with the degradation-onset rationale), not stated as a bare KB number.
- **ICM "docs-over-outputs" rule:** agents are forbidden from learning patterns from their own prior (possibly flawed) outputs — must use canonical reference material. Directly mirrors the harness's design-substrate-is-canonical discipline; a citable external anchor for it.

### Q#1 (home-of-record for `tools/hooks/`) — *not a corpus question*
Organizational/ownership decision internal to this repo (HARDENING_PLAN vs council PLAN); no external canon adjudicates it. DESIGN.md decides directly (AR-2 recommendation stands).

---

## Part B — Per-voice external canon (citable anchors for DESIGN.md)

- **C2 (context engineering):** progressive disclosure (SKILL.md ~100-token metadata); JIT retrieval via lightweight identifiers + `grep`/`read` (Devin SWE-grep 60% first-turn); **ICM — Interpretable Context Methodology** (numbered stage folders + `CONTEXT.md` "stage contracts": Inputs/Process/Outputs) — *this is the exact methodology the CHARTER names*; Kilocode **Memory Bank** (`brief`/`architecture`/`dependencies`), Trellis (`spec`/`tasks`/`workspace`).
- **C3 (state/memory persistence):** CoALA tiers; Letta Recall→Archival; Mem0 adaptive dedup; Zep/Graphiti validity-windows; consolidation/reflection as the promotion process; reference-count as archival signal.
- **C1 (orchestration):** orchestrator-worker write-serialization (MARS/Dify); concurrency caps (3–5 sub-agents, DeerFlow/Anthropic); Temporal signal-gated state mutation — the hook-lifecycle-as-topology framing has direct analogues.
- **C5 (validation):** layered validator cascade (deterministic→inferential); schema-as-hard-gate (OpenAI Agents SDK / VoltAgent typed contracts); test-ratchet (Claude Code/DeerFlow — non-zero exit, no test-deletion); GitHub Spec Kit gated-phase lock; ruflo anti-drift enforcer; ICM stage audits with unambiguous pass conditions.
- **C7 (observability):** context-rot detection (positional bias / lost-in-the-middle 15–20% drop; embedding drift via MMD/cosine); **cache-hit monitoring via `cache_read_input_tokens`/`cache_creation_input_tokens`** + the **"silent zero-cache" failure** (breakpoints on dynamic content like timestamps) — *this precisely names the CLAUDE.md §2 cache-detonation problem (60/60 recent commits touch §2 ⇒ cache_creation increments, cache_read stays low)*; "Dumb Zone" 40–60% threshold.
- **C9 (recovery):** tiered compaction (Micro/Auto/Full/Manual; Claude Code reserves a 13K-token buffer, re-injects 5 most-recent files); tool-result clearing (`clear_tool_uses_*`); `feature_list.json` re-read to prevent "victory declaration"; git-as-state boot (read last 20 commits); Ralph Loop ("are you really done?"); sub-agent isolation (return 1–2K-token summaries).

---

## Part C — Net-new, decision-moving inputs DESIGN.md should absorb
1. **Adopt CoALA/Letta vocabulary + tiers** for WS-3 (working/episodic/semantic/procedural; Main/Recall/Archival) instead of inventing terms — gives the retention contract a standard, citable shape.
2. **Q#2 resolves toward detection-first (OCC), not locks** — build a cheap version/timestamp check; defer prophylactic serialization (AR-4 externally confirmed).
3. **git-version (or shadow-git snapshot) the memory store** — the canonical fix for C9's "unrecoverable store"; rollback = snapshot timeline.
4. **Q#3 resolves toward hard gates** — advisory caps demonstrably drift (OpenAI 1-min-build precedent); promote G1 byte-budget to `--check`; structural⇒hard / heuristic⇒advisory is the MVP-ranking rule.
5. **Re-derive WS-1's budget as % utilization (target 60–80%; degradation onset 40–60%)**, not a bare ≤40KB.
6. **Name the §2 cache problem as "silent zero-cache" from dynamic-content cache-breakpoints** — gives C7 a concrete instrument (`cache_read` ratio) and reframes WS-1 eviction as a *cache-hit* win, not just a byte-budget win.
7. **Q#4 portability decision:** under Claude Code `AGENTS.md` is safe-as-not-loaded, but pick the anchor filename deliberately given the Codex/Agents-SDK auto-load convention.
8. **Reference-count consolidation trigger:** promote the ≥4-reference unwritten patterns (e.g. `[[plan-revision-against-not-yet-built-substrate]]`) to semantic notes — an episodic→semantic consolidation the store is overdue on.

*Provenance: queries P1–P6 against notebook `57b8d946-830c-42dd-b201-ac117a8af951`; answers carry 31/48/51/49/45 source citations respectively into the corpus's 28 URL-scrape compilations (Anthropic, OpenAI, Cursor, Devin/Cognition, LangGraph, Temporal, Letta/MemGPT, Mem0, Zep, CoALA, ICM, et al.). Re-runnable via `notebooklm ask … --notebook 57b8d946-…`.*
