# Triaged Source Inventory — Pattern Reference Catalog Pre-Construction

**Project:** Multi-LLM agent harness (substrate-research phase, post-Session 3)
**Purpose:** Triage 40+ collected sources to scope the Pattern Reference Catalog construction session
**Verification date:** 8 May 2026
**Verification method:** Live web fetch / web search this session; star counts and last-commit/release dates observed directly unless explicitly flagged otherwise
**Confidence schema:** [HIGH] verified live this session · [MODERATE] reputable secondary or strong inference · [SPECULATIVE] reasoned hypothesis without verified source

---

## How to read this document

- **Section 1** is the per-source triage table. Rows grouped by stratum for scannability. Columns: Source · Activity signal · Session 3 cross-reference · Decision · Rationale.
- **Section 2** summarises decision counts, surfaces coverage observations, and flags source-quality limits.
- **Section 3** is the recommended catalog scope (final list of sources for catalog construction next session) plus pre-construction recommendations and open questions.
- **Appendix A** lists every URL referenced, grouped by source, so the document is self-contained.
- **Appendix B** logs URL anomalies, redirects, and naming inconsistencies that the catalog construction session must handle.

Decision codes used in tables:

- **INCLUDE** — active, distinct pattern contribution; deserves a fresh catalog entry
- **INCLUDE-CROSSREF** — already profiled in Session 3 (or Session 2); catalog entry references the prior profile and adds a pattern-extraction layer
- **DEFER** — pattern is interesting but commitment is thin or source is proprietary; revisit if catalog scope grows
- **EXCLUDE** — too thin, too duplicative, or incompatible with V3 framing (no entries this triage)

---

## Section 1 — Triage Table

### A. Research artifacts (papers, reference implementations)

| Source | Activity signal | S3 X-ref | Decision | Rationale |
|---|---|---|---|---|
| arXiv 2603.28052 — *Meta-Harness: End-to-End Optimization of Model Harnesses* (Lee, Nair, Zhang, K. Lee, Khattab, Finn — Stanford / MIT / KRAFTON, 30 Mar 2026) [HIGH] | Paper live; 28 pp; cs.AI | No | **INCLUDE** | Most directly on-topic academic work for this project. Names the discipline ("harness engineering"). TerminalBench-2: 76.4 % on Opus 4.6 (#2 leaderboard at submission). Definitional source. |
| `stanford-iris-lab/meta-harness` (reference implementation) [HIGH] | 34★ / 3 forks / 9 commits / MIT / Python; CITATION.cff present | No | **INCLUDE** | Cleaned reference impl. Small but canonical. ONBOARDING.md → `domain_spec.md` flow is itself a pattern. |
| `stanford-iris-lab/meta-harness-tbench2-artifact` [HIGH — exists per arXiv reference + sibling repo cross-link] | Artifact repo per paper | No | **INCLUDE** | Holds the optimised TerminalBench-2 harness from the paper. Pattern-extractable. |
| `yoonholee.com/meta-harness/` (project page) [HIGH — referenced from arXiv listing and reference repo] | Live | No | **INCLUDE** | First-author project page; primary source for figures and short summary. |
| YouTube `13HP_bSeNjU` (Meta-Harness) [SPECULATIVE — not directly verified] | Not verified live this session | No | **DEFER** | Verify before catalog if used; not load-bearing if paper + repo are catalogued. |
| YouTube `yOeVi3aQ9Kg` (Meta-Harness) [SPECULATIVE — not directly verified] | Not verified live this session | No | **DEFER** | Same as above. |
| arXiv 2603.16021 — *Interpretable Context Methodology: Folder Structure as Agentic Architecture* (Van Clief, McDermott — v2, 18 Mar 2026, 28 pp) [HIGH] | Paper live; cs.AI / cs.HC | No | **INCLUDE** | Defines the Model Workspace Protocol (MWP). Direct counter-position to framework-level orchestration. Decision-relevant for harness/state design. |
| `RinDig/Interpreted-Context-Methdology` (companion repo) [HIGH for existence; MODERATE for activity — direct repo activity not measured] | Repo present; "ICM replaces framework-level orchestration with filesystem structure." | No | **INCLUDE** | Companion to paper. **URL anomaly:** repo name uses *Interpreted* (and "Methdology" missing an 'o'); paper title uses *Interpretable*. Both URLs resolve. Flag during catalog construction. |

### B. Production harnesses (mature, widely used)

| Source | Activity signal | S3 X-ref | Decision | Rationale |
|---|---|---|---|---|
| `OpenHands/OpenHands` (canonical post-Oct-2025 rename; was `All-Hands-AI/OpenHands`) [HIGH] | ~65k★ per Session 3 | **Yes — S3 §B3** | **INCLUDE-CROSSREF** | URL note: user-supplied `OpenHands/OpenHands` is the new canonical org; old org redirects. Pattern-rich (ACI paper, software-agent-sdk paper). |
| `cline/cline` [HIGH] | ~61.3k★ / `v3.82.0` (1 May 2026) per Session 3 | **Yes — S3 §B2** | **INCLUDE-CROSSREF** | S3 covers the cline-core architectural pivot. Pattern-extraction angle: per-step approval gate, snapshot/restore timeline, `cline/prompts` rule library. |
| `aaif-goose/goose` (AAIF Linux Foundation mirror; canonical was `block/goose`) [HIGH] | ~31.2k★ per Session 3 | **Yes — S3 §B4–8** | **INCLUDE-CROSSREF** | Catalog should cite both URLs (block/ → aaif-goose/ post-donation). |
| `RooCodeInc/Roo-Code` [HIGH] | ~23.8k★ per Session 3 | **Yes — S3 §B4–8** | **INCLUDE-CROSSREF** | Cline fork; multi-mode pattern (Architect / Code / Debug / Ask). |
| `bytedance/deer-flow` [HIGH] | ~64.8 – 66.1k★ / 8.5–8.7k forks / Python / MIT / DeerFlow 2.0 self-described as "super agent harness — batteries included" / activity within days; 263 PRs / 459 issues open | **No — major Session 3 omission** | **INCLUDE (priority)** | Largest individual gap relative to Session 3. Explicit LangGraph + LangChain substrate; ships filesystem / memory / skills / sandbox / sub-agents OOTB. Closes Chinese-ecosystem coverage gap. Pattern-rich (`skills/public/` catalog mirrors Anthropic's pattern). |
| `earendil-works/pi` (pi-mono; Mario Zechner / "badlogic") [HIGH] | 45.9k★ / 5.4k forks / 3,967 commits / TypeScript / MIT / `v0.73.1` (7 May 2026) / 213 releases | **Partial — S2 listed as `[Discovery] Pi-mono`; not S3-profiled** | **INCLUDE (priority)** | Multi-package monorepo: `pi-ai` (unified LLM API), `pi-agent-core`, `pi-coding-agent`, `pi-tui`, `pi-web-ui`. Decision-relevant for unified LLM API and TUI patterns. Maintainer publishes OSS session datasets to HuggingFace. |
| `pi.dev` (project home) [HIGH — referenced from repo] | Live; sponsored by exe.dev | n/a | **INCLUDE** | Primary entry alongside the repo. |
| `Kilo-Org/kilocode` [HIGH] | ~19.0k★ / 2.5k forks / TypeScript / MIT / `v7.2.40+` (5 May 2026); self-claims "#1 OpenRouter, 1.5M users, 25T tokens" | No | **INCLUDE (priority)** | Major Session 3 omission. Cline-lineage IDE coding agent. Repo migrated from `Kilo-Org/kilo`. Notable Claude Code provider integration architecture (referenced by `charmbracelet/crush` discussion #421). |
| `langchain-ai/deepagents` (+ sister `deepagentsjs`) [HIGH] | Active; LangChain self-describes as "agent harness"; Python + JS parity; built on LangGraph runtime | No (S3 mentions in passing) | **INCLUDE** | LangChain's own first-party harness on top of LangGraph. README explicitly inspired by Claude Code. Strong as a canonical "framework → harness" exemplar. |
| `langgenius/dify` [HIGH] | "Production-ready platform for agentic workflow development" / 35,000+ issues / `v1.14.0` (29 Apr 2026) / very active | No | **INCLUDE** | Significant Session 3 gap. Founded by ex-Tencent Cloud DevOps. Visual workflow + agent platform. License terms (Apache-derivative) verify during construction. |
| `HKUDS/OpenHarness` [HIGH] | ~12k★ / 2k forks / Python / MIT / `v0.1.7` (18 Apr 2026); slogan: "The model is the agent. The code is the harness." | No | **INCLUDE (priority)** | Closes Chinese-ecosystem gap from Session 3. HK U Data Science Lab. Built-in personal agent (`ohmo`). Pluggable provider compatibility (Anthropic / OpenAI / Moonshot / MiniMax / Gemini / Ollama / OpenAI-compat gateways). Integrates with OpenClaw, nanobot, Cursor. |
| `VoltAgent/voltagent` [HIGH] | ~8.7k★ / MIT / TypeScript / very active | No | **INCLUDE** | Distinct TS-native production-grade play (alongside Mastra). VoltOps observability split. Distinct supervisor / sub-agent + workflow engine pattern. |

### C. Emerging harnesses (newer, less stable)

| Source | Activity signal | S3 X-ref | Decision | Rationale |
|---|---|---|---|---|
| `can1357/oh-my-pi` [HIGH] | 2.7k★ / 248 forks / 3,934 commits / TypeScript + Rust / MIT / `v13.19.0` (5 Apr 2026) / 315 releases | No | **INCLUDE** | Fork of pi-mono with substantial extensions: hashline edits, Time-Traveling Streamed Rules (TTSR), 11 LSP operations, 14 stealth-mode browser plugins, native Rust N-API addons, multi-credential round-robin, isolation backends (worktree / fuse-overlay / fuse-projfs). Genuinely distinct patterns versus upstream. |
| `jonwiggins/optio` [HIGH] | ~922★ / TypeScript / very active (CI #845+, daily PRs) / Kubernetes-native | No | **INCLUDE** | Workflow orchestration for AI coding agents; task → merged PR pipeline. K8s-native, BYO Postgres / Redis. Distinct deployment-surface pattern (self-hosted on existing K8s). Persistent Agents vs Tasks tier model. |
| `mindfold-ai/Trellis` [HIGH] | npm `@mindfoldhq/trellis` / active (3 days) / TypeScript | No | **INCLUDE** | Meta-harness pattern: initialises across 14+ platforms (Cursor / OpenCode / Codex / iFlow / Kilo / Kiro / Gemini / Antigravity / Windsurf / Qoder / CodeBuddy / Copilot / Droid / Pi). Markdown-spec-driven. Bilingual (EN / 中文). |
| `code-yeongyu/oh-my-openagent` ("omo"; formerly oh-my-opencode) [HIGH] | Very active (latest activity 9 hr) / 11 specialised agents / TypeScript / Korean origin | No | **INCLUDE** | Distinct multi-model orchestration: Sisyphus orchestrator + Hephaestus / Oracle / Librarian / Explore / Atlas / Prometheus / Metis subagents. Per-agent fallback chains by model. Deterministic agent-tab cycling. |
| `charmbracelet/crush` [HIGH] | `v0.66.0` (Apr 2026) / Go / **FSL-1.1-MIT** (non-OSI delayed-open) / very active | **Partial — S2 `[Discovery] Crush`** | **INCLUDE** | Charmbracelet's Go-native terminal coding agent. Cosign-signed releases. **License flag:** FSL is non-OSI; converts to MIT after delay. Catalog must call this out. |
| `shareAI-lab/Kode-Agent` (and sister repos: `kode-agent-sdk`, `Kode-cli`, `claw0`, `BashClaw`, `mini-claude-code`) [HIGH] | Active / TypeScript / Docker-first / Chinese ecosystem | No | **INCLUDE** | Closes Chinese-ecosystem gap. shareAI-lab maintains a multi-repo body of work; Kode-Agent is the flagship. SDK is independently pattern-rich (event-driven inbox, approval workflow, multi-agent room, OpenSandbox integration). |
| `mvschwarz/openrig` [HIGH] | Active / TypeScript / MIT / npm `@openrig/cli` | No | **INCLUDE** | Distinct architectural pattern: tmux-based topology orchestration of multiple coding agents (Claude Code + Codex pods). YAML RigSpec, snapshot/restore by name, `rig send`/`broadcast`/`chatroom`. Genuinely different from per-process patterns. |
| `paperclipai/paperclip` [HIGH] | Active (3 hr) / Node.js / embedded Postgres | No | **INCLUDE** | "Open-source orchestration for zero-human companies" — agent-companies-as-deployment pattern. Multi-tenant; Tailscale-friendly local deployment story. Distinct from per-task orchestrators. |

### D. Methodology frameworks

| Source | Activity signal | S3 X-ref | Decision | Rationale |
|---|---|---|---|---|
| `revfactory/harness` (+ sister `revfactory/harness-100`) [HIGH] | Active; 1,808 markdown files / 100 production harnesses across 10 domains / EN + KR (200 packages total) | No | **INCLUDE** | Meta-skill that *generates* domain-specific agent teams. Quantified A/B claim: +60 % avg quality (49.5 → 79.3), 15/15 win rate, n=15. Author-measured (not third-party-replicated yet — flag). Distinct domain-coverage pattern. |
| `sharpdeveye/maestro` [HIGH] | Active; works across Cursor / Claude Code / Gemini CLI / Copilot + 6 more | No | **INCLUDE** | Meta-skill: 1 core skill / 25 commands / 7 domain references / memory layer / audit trail. Cross-harness portable workflow pattern. |
| `msitarzewski/agency-agents` [HIGH] | Active (March 2026); 112 specialised agent personas | No | **INCLUDE** | Markdown-persona-injection pattern across Claude Code / Cursor / Aider. Distinct domain-agent-as-persona pattern; distinct from skills. |
| `humanlayer/12-factor-agents` [HIGH — referenced repeatedly across project substrate] | 19.7k★ per Session 2 / 3 | **Yes — S3 deferred list** | **INCLUDE-CROSSREF** | Methodology, not framework. The reference manifesto for the project's overall framing. Already cited in Cluster 1, 5, and 6 deep-dives. |
| Skool — `cliefnotes` (Jake Van Clief, ICM paper coauthor) [SPECULATIVE — not deeply probed] | Skool platform gates content | No | **DEFER** | Author already covered via the ICM paper. Verify substantive content beyond paper before commit. |

### E. Thought-leader bodies of work

| Source | Activity signal | S3 X-ref | Decision | Rationale |
|---|---|---|---|---|
| `disler/single-file-agents` [HIGH for repo existence; MODERATE for star count, ~412★ per S2] | Repo active | **Yes — S3 deferred / S2 thought leader** | **INCLUDE-CROSSREF** | SFA pattern is canonical (`sfa_<capability>_<provider>_v<version>.py`). Already cited in Cluster 1 Orchestration deep-dive. |
| `disler/the-library` [HIGH] | Active (Mar 2026) | **Yes — S2** | **INCLUDE-CROSSREF** | Meta-Skill for skill distribution. Companion to single-file-agents. |
| `disler` — full repo set (`just-prompt`, `infinite-agentic-loop`, Claude Code monitoring, agentic browser, fork-agent, etc.) [HIGH for set existence — visible on author's repo listing] | All active per repo listing | Partial — S2 thought-leader entry | **INCLUDE (as a body)** | Disler's body of work *is* a pattern source set. Catalog entry should be the *body*; pull individual repos as patterns warrant. |
| YouTube `@indydevdan` [HIGH] | 127k subscribers / 191 videos / active daily | **Yes — S2** | **INCLUDE-CROSSREF** | Companion to repos; named in Session 2 §4 as one of three "harness-as-product" voices. |
| `coleam00` — full repo set, anchored on `coleam00/Archon` [HIGH for Archon] | Active; Archon = "first open-source harness builder for AI coding"; multi-version evolution (V4 → V5 multi-agent refiners) | **Yes — S2 thought leader** | **INCLUDE (as a body)** | Cole Medin profiled in S2; Archon is his flagship harness builder. Catalog should treat as a body of work. |
| YouTube `@ColeMedin` [HIGH — per Session 2] | Active per Session 2 | **Yes — S2** | **INCLUDE-CROSSREF** | Companion to repos. |

### F. Knowledge aggregators

| Source | Activity signal | S3 X-ref | Decision | Rationale |
|---|---|---|---|---|
| `ai-boost/awesome-harness-engineering` [HIGH] | Very active (3 days); multi-language (DE / EN / ES / FR / JA / KO / PT / RU / 中文) | No | **INCLUDE** | The most directly on-topic curated list for the project. Already cites canonical OpenAI / Anthropic / Google / Martin Fowler harness essays. Doubles as a discovery surface. |
| `meleantonio/ChernyCode` [HIGH] | Active (Mar 2026); template repo | No | **INCLUDE (downgrade-eligible)** | Packages Boris Cherny's Claude Code workflow (CLAUDE.md memory + reusable patterns). Worked example of the methodology, not a framework in itself. Could be DEFER if catalog scope is tight. |

### G. Approach experiments

| Source | Activity signal | S3 X-ref | Decision | Rationale |
|---|---|---|---|---|
| `ruvnet/ruflo` [HIGH for activity; some claims unverified] | Very active (2 days); npm distribution; v4 in progress | No | **INCLUDE** | Distinct experimental architectural patterns: GOAP-style A* planning over preconditions/effects, "self-learning swarm intelligence", Claude-Code-plugin install path, federation. Some ML claims aspirational — flag during construction. Pattern source even if claims are aspirational. |
| `humanlayer/agentcontrolplane` (ACP) [HIGH] | 391★ / 57 forks / Go / Apache-2.0 / Active | **Partial — S2 `[Discovery] AgentControlPlane`** | **INCLUDE** | K8s-operator-as-harness pattern. Distinct: agent execution as CRDs, durable async / await at infrastructure layer, mesh ContactChannel for HITL. Smaller scale but architecturally distinct from app-level harnesses. |
| `Factory-AI/factory` (capital-canonical; user URL `factory-ai/factory` redirects) [HIGH for repo existence; LOW for open-source content] | Marketing-only repo on GitHub; product is proprietary; SDK packages (`droid-sdk-typescript`, `factory-plugins`, `droid-action`, etc.) are partially public | **Partial — S2 `[Discovery] Droid (Factory)`** | **DEFER** | Closed-source product; main repo is a stub. Catalog entry would be from public design surface (Code / Knowledge / Reliability / Product Droid taxonomy + Terminal-Bench writeup) — interesting but harder to source-ground. Reconsider if scope expands. |

---

## Section 2 — Triage Summary

### Decision counts

| Decision | Count | Notes |
|---|---|---|
| **INCLUDE** | 27 | New catalog entries needing fresh research |
| **INCLUDE-CROSSREF** | 8 | Already in Session 3 (or Session 2); catalog entry references the prior profile and adds a pattern layer |
| **DEFER** | 4 | Pattern interesting but commitment thin or proprietary; revisit if catalog scope grows |
| **EXCLUDE** | 0 | None of the user's sources are excludable on quality alone |
| **Total user-listed sources triaged** | 39 unique projects (~50 URLs counting paper / site / YouTube duplicates) | |

### Coverage observations

1. **Three projects are major Session 3 omissions, not reasonable budget casualties.** [HIGH]
   - `bytedance/deer-flow` (~65k★, explicit "super agent harness" branding, MIT, near-daily activity)
   - `earendil-works/pi` / pi-mono (~46k★, monorepo with unified LLM API + agent core + TUI + web UI)
   - `Kilo-Org/kilocode` (~19k★, claimed #1 on OpenRouter, Cline-lineage)

   All three meet the Session 3 ≥ 1k-star threshold trivially and were missed because Session 2's discovery surface didn't reach them. Catalog construction should treat these as priority-tier alongside Session 3's profiled Top-15.

2. **The Chinese-ecosystem gap flagged in Session 3 is closed by the user's source list.** [HIGH] DeerFlow (ByteDance), OpenHarness (HKUDS), Dify (langgenius / ex-Tencent), and Kode-Agent (shareAI-lab) collectively cover the ByteDance / HK-academic / Tencent / independent quadrants of the Chinese ecosystem. Session 4 wouldn't need separate Chinese-ecosystem discovery — it lives in this triage list.

3. **Two arXiv papers from March 2026 are directly on-topic.** [HIGH] Meta-Harness (2603.28052) and ICM (2603.16021) both define "harness" in technical terms aligned with this project's framing. Meta-Harness's TerminalBench-2 results give the project quantified evidence for the *automated harness search* discipline. ICM provides the strongest counter-position to framework-orchestration (filesystem-as-orchestrator). Read these first before catalog construction.

4. **Meta-harness / cross-platform meta-skill is a distinct stratum the user's list captures well.** [MODERATE] Trellis, Maestro, Agency-Agents, RevFactory's harness-100, Disler's the-library, and arguably ChernyCode all share a pattern: instead of building a new harness, define a portable Markdown-spec layer that runs across Claude Code / Cursor / Codex / etc. Worth its own catalog section. Session 3 didn't have a category for this.

5. **The user's stratum scheme is sound but a few sources straddle.** [MODERATE]
   - Cole Medin's `Archon` is both an "approach experiment" and a "thought-leader body of work."
   - `humanlayer/12-factor-agents` is both "methodology framework" and "thought leader" (Dex Horthy).
   - `RinDig/Interpreted-Context-Methdology` is both research artifact (paper) and methodology (MWP).
   - Recommend the catalog allow multi-tag stratum membership rather than forcing single-stratum.

6. **Discovery findings adjacent to user's list (worth surfacing pre-catalog):** [MODERATE]
   - `Picrew/awesome-agent-harness` — another curated list, distinct from `ai-boost/awesome-harness-engineering`. Decide whether to include both.
   - `HKUDS/nanobot` (~42k★) — sister to OpenHarness from same lab (personal-agent angle).
   - `humanlayer/advanced-context-engineering-for-coding-agents` (visible in HumanLayer org) — methodology angle worth verifying.

### Source-quality limits

- YouTube videos `13HP_bSeNjU`, `yOeVi3aQ9Kg` (Meta-Harness) — not directly verified this session. Marked [SPECULATIVE] / DEFER. Verify before catalog if used.
- Skool — `cliefnotes` not deeply probed (Skool gate-keeps content). Author covered via paper. Marked DEFER.
- `Factory-AI/factory` is marketing-only on GitHub; deeper pattern-extraction would need product blog + Terminal-Bench writeup mining. Marked DEFER unless catalog scope makes the proprietary-design-surface case worthwhile.
- `revfactory/harness-100` quality claim ("+60 % avg quality, n=15, third-party replications pending") is author-measured; flag during construction.

---

## Section 3 — Recommended Catalog Scope

**Total catalog entries: 35** (27 fresh + 8 cross-ref). Organised by stratum below.

### Priority tier (fresh research, anchor entries)

These three are the highest-leverage Session 3 gaps and should anchor catalog construction:

1. `bytedance/deer-flow` — fresh research; full pattern profile.
2. `earendil-works/pi` (pi-mono) — fresh research; multi-package profile.
3. `Kilo-Org/kilocode` — fresh research; pattern profile.

### A. Research artifacts (fresh research)

4. arXiv 2603.28052 Meta-Harness paper + project page (`yoonholee.com/meta-harness/`)
5. `stanford-iris-lab/meta-harness` (reference impl)
6. `stanford-iris-lab/meta-harness-tbench2-artifact` (artifact)
7. arXiv 2603.16021 ICM paper
8. `RinDig/Interpreted-Context-Methdology` repo

### B. Production harnesses (cross-ref to Session 3, add pattern layer)

9. `OpenHands/OpenHands` — *cross-ref S3 §B3*
10. `cline/cline` — *cross-ref S3 §B2*
11. `aaif-goose/goose` — *cross-ref S3 §B4–8*
12. `RooCodeInc/Roo-Code` — *cross-ref S3 §B4–8*
13. `HKUDS/OpenHarness` — fresh research (priority)
14. `langchain-ai/deepagents` (+ `deepagentsjs`) — fresh research
15. `langgenius/dify` — fresh research
16. `VoltAgent/voltagent` — fresh research

### C. Emerging harnesses (fresh research)

17. `can1357/oh-my-pi`
18. `jonwiggins/optio`
19. `mindfold-ai/Trellis`
20. `code-yeongyu/oh-my-openagent`
21. `charmbracelet/crush`
22. `shareAI-lab/Kode-Agent` (+ `kode-agent-sdk` as appendix)
23. `mvschwarz/openrig`
24. `paperclipai/paperclip`

### D. Methodology frameworks (fresh research + cross-ref)

25. `revfactory/harness` + `harness-100`
26. `sharpdeveye/maestro`
27. `msitarzewski/agency-agents`
28. `humanlayer/12-factor-agents` — *cross-ref S3 deferred + S2*

### E. Thought-leader bodies (cross-ref + body-level catalog entries)

29. `disler` — body-level entry covering single-file-agents, the-library, just-prompt, etc. — *cross-ref S2*
30. `coleam00` — body-level entry anchored on Archon — *cross-ref S2*
31. YouTube `@indydevdan` — *cross-ref S2*
32. YouTube `@ColeMedin` — *cross-ref S2*

### F. Knowledge aggregators (fresh research)

33. `ai-boost/awesome-harness-engineering`
34. `meleantonio/ChernyCode` (downgrade-eligible during construction if scope tight)

### G. Approach experiments (fresh research)

35. `ruvnet/ruflo`
36. `humanlayer/agentcontrolplane`

### Deferred (do not catalogue this session)

- YouTube videos `13HP_bSeNjU`, `yOeVi3aQ9Kg` (Meta-Harness — not directly verified)
- Skool `cliefnotes` (gate-keeping)
- `Factory-AI/factory` (proprietary; design-surface only)

---

### Pre-construction recommendations

1. **Add a "meta-harness / cross-platform meta-skill" sub-stratum under D-Methodology.** Trellis, Maestro, Agency-Agents, RevFactory harness-100, and Disler's the-library form a coherent design pattern not covered by Session 3's categories.
2. **Allow multi-tag stratum membership.** Several entries straddle (Archon: approach-experiment + thought-leader; ICM: research-artifact + methodology). Single-stratum forcing will lose pattern fidelity.
3. **Treat the three priority-tier omissions as anchors.** DeerFlow / pi / kilocode each have ≥ 10k stars and are pattern-rich enough to deserve full Session-3-style profiles before any of the smaller emerging harnesses.
4. **Star-count threshold is no longer load-bearing for catalog scope.** Several sources in this list (Trellis, Maestro, Optio at ~922★, ACP at ~391★, oh-my-pi at 2.7k★) carry distinct patterns that justify catalog inclusion despite sub-1k-star counts. Recommend the catalog use *pattern distinctiveness* rather than stars as the primary inclusion criterion, with stars as a tie-breaker.

### Open questions for the catalog session

- Should `humanlayer/humanlayer` (10.7k★, Session 3-mentioned) be its own catalog entry separate from agentcontrolplane, given they are architecturally distinct (in-process SDK vs K8s operator)?
- For thought-leader bodies (`disler`, `coleam00`), is the catalog entry the *person* with sub-entries per repo, or one entry per repo? Recommend the former for compression but flagging the call.
- For `ai-boost/awesome-harness-engineering` vs `Picrew/awesome-agent-harness` — include both, pick one, or treat as a single "external aggregator landscape" entry?

### Recommended next probes (for catalog session, not this triage)

- Verify the two YouTube Meta-Harness video URLs and decide whether they add over the paper.
- Direct-verify `Picrew/awesome-agent-harness` as a candidate F-stratum entry alongside `ai-boost`.
- Direct-verify `HKUDS/nanobot` and `humanlayer/advanced-context-engineering-for-coding-agents` as adjacent-discovery additions.

---

## Appendix A — URL Reference

Grouped by source for self-containment. URLs verified live this session unless flagged [SPECULATIVE].

### A1. Research artifacts

- Meta-Harness paper: https://arxiv.org/abs/2603.28052 · https://arxiv.org/html/2603.28052v1
- Meta-Harness reference repo: https://github.com/stanford-iris-lab/meta-harness
- Meta-Harness TerminalBench-2 artifact: https://github.com/stanford-iris-lab/meta-harness-tbench2-artifact
- Meta-Harness project page: https://yoonholee.com/meta-harness/
- Meta-Harness YouTube candidates: https://www.youtube.com/watch?v=13HP_bSeNjU · https://www.youtube.com/watch?v=yOeVi3aQ9Kg [SPECULATIVE — not verified live]
- ICM paper: https://arxiv.org/abs/2603.16021 · https://arxiv.org/html/2603.16021v2
- ICM repo: https://github.com/RinDig/Interpreted-Context-Methdology
- Skool — cliefnotes: https://www.skool.com/cliefnotes/about [SPECULATIVE — not verified live]
- Van Clief YouTube: https://www.youtube.com/@JEVanClief [SPECULATIVE — not verified live]

### A2. Production harnesses

- OpenHands: https://github.com/OpenHands/OpenHands · https://www.openhands.dev/
- OpenHands YouTube: https://www.youtube.com/@OpenHands-AI
- Cline: https://github.com/cline/cline
- Goose (AAIF): https://github.com/aaif-goose/goose
- Roo-Code: https://github.com/RooCodeInc/Roo-Code
- DeerFlow: https://github.com/bytedance/deer-flow · https://deerflow.tech/
- pi (canonical): https://github.com/earendil-works/pi · https://pi.dev/
- Kilocode: https://github.com/Kilo-Org/kilocode
- DeepAgents: https://github.com/langchain-ai/deepagents · https://github.com/langchain-ai/deepagentsjs
- Dify: https://github.com/langgenius/dify
- OpenHarness: https://github.com/HKUDS/OpenHarness
- VoltAgent: https://github.com/VoltAgent/voltagent · https://voltagent.dev/

### A3. Emerging harnesses

- oh-my-pi: https://github.com/can1357/oh-my-pi
- Optio: https://github.com/jonwiggins/optio · https://optio.host/
- Optio author repos: https://github.com/jonwiggins?tab=repositories
- Trellis: https://github.com/mindfold-ai/trellis
- oh-my-openagent: https://github.com/code-yeongyu/oh-my-openagent
- Crush: https://github.com/charmbracelet/crush
- Kode-Agent: https://github.com/shareAI-lab/Kode-Agent
- Openrig: https://github.com/mvschwarz/openrig
- Paperclip: https://github.com/paperclipai/paperclip · https://paperclip.ing/

### A4. Methodology frameworks

- RevFactory Harness: https://github.com/revfactory/harness
- Maestro: https://github.com/sharpdeveye/maestro
- Agency Agents: https://github.com/msitarzewski/agency-agents
- 12-Factor Agents: https://github.com/humanlayer/12-factor-agents

### A5. Thought-leader bodies

- Disler repos: https://github.com/disler?tab=repositories
- Disler — single-file-agents: https://github.com/disler/single-file-agents
- IndyDevDan YouTube: https://www.youtube.com/@indydevdan
- Cole Medin repos: https://github.com/coleam00?tab=repositories
- Cole Medin — Archon: https://github.com/coleam00/Archon
- Cole Medin YouTube: https://www.youtube.com/@ColeMedin/videos

### A6. Knowledge aggregators

- Awesome Harness Engineering: https://github.com/ai-boost/awesome-harness-engineering
- ChernyCode: https://github.com/meleantonio/ChernyCode

### A7. Approach experiments

- Ruflo: https://github.com/ruvnet/ruflo
- HumanLayer ACP: https://github.com/humanlayer/agentcontrolplane
- Factory AI: https://github.com/factory-ai/factory

---

## Appendix B — URL anomalies, redirects, and naming flags

To be handled during catalog construction:

1. **arXiv `2603.xxxxx` IDs are March 2026, not the year 2603.** arXiv format is `YYMM.NNNNN`; both Meta-Harness and ICM papers were submitted in March 2026. Worth annotating in the catalog because future-date appearance is misleading.
2. **`RinDig/Interpreted-Context-Methdology`** — repo name uses *Interpreted* (not *Interpretable* per paper title) and has a missing "o" in "Methdology". Both URLs resolve. Catalog entry should normalise spelling and link to the canonical paper title.
3. **`OpenHands/OpenHands`** is the post-October-2025 canonical; the Session 3-cited `All-Hands-AI/OpenHands` redirects. Keep both URLs in the catalog entry for backward reference.
4. **`Factory-AI/factory`** is the case-canonical org; `factory-ai/factory` redirects.
5. **`aaif-goose/goose`** is the AAIF Linux Foundation post-donation mirror; `block/goose` is the historical canonical. Both alive — catalog should cite both.
6. **`Kilo-Org/kilocode`** migrated from `Kilo-Org/kilo`. Old repo redirects.
7. **`earendil-works/pi`** is the new canonical; the maintainer historically used `badlogic/pi-mono` (still referenced in third-party documentation including Session 2). Catalog should call this out.
8. **`charmbracelet/crush` license** is FSL-1.1-MIT (Functional Source License → MIT after a delay). Non-OSI at time of release. License-diligence flag for any catalog use.
9. **`shareAI-lab/Kode-Agent`** repo points to `shareAI-lab/Kode.git` for clone instructions — repo name in the org listing differs slightly from the clone URL. Catalog entry should reconcile.
10. **DeerFlow 2.0 is a from-scratch rebuild** versus DeerFlow 1.0; pattern-extraction must distinguish 2.0 patterns from 1.0 patterns where possible.

---

*End of triaged inventory.*
