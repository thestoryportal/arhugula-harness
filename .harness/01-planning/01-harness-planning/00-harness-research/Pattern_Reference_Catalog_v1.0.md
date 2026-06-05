# Pattern Reference Catalog v1.0

*Multi-LLM Agent Harness Design Project · Research-Substrate Phase · Catalog Construction Sessions A–G*

---

## §1. Catalog metadata

**Compilation date:** 2026-05-08 (observation date for all live-source verification carried forward from per-session research).

**Source-list version:** Triaged Source Inventory — Pattern Reference Catalog Pre-Construction (verification date 2026-05-08; Section 3 "Recommended Catalog Scope" is the canonical entry list this catalog instantiates). See cross-reference at the end of this section.

**Scope boundary.** This catalog is a **curated short-list of pattern-bearing sources**, not a comprehensive landscape of the agent-harness ecosystem. Inclusion criterion is *pattern distinctiveness* (per the Triaged Source Inventory pre-construction recommendations §3), with star count and maintenance signal as tie-breakers rather than primary gates. The catalog is the substrate-research input to the project's design phase; it does not itself recommend a stack, a persona, or a deployment surface.

**Total catalog entries: 36** spanning 9 strata (priority-tier B, A, B-standard, C, D, D-meta, E, F, G). The Triaged Source Inventory §3 enumerated 35 entries (3 priority + 5 research + 4 production cross-ref + 4 production standard + 8 emerging + 4 methodology + 4 thought-leader + 2 aggregators + 2 approach experiments). The catalog as constructed contains 36 source rows because the Meta-Harness research artifact is split across three sub-entries (§2.1 paper, §2.2 reference implementation, §2.3 TerminalBench-2 optimized artifact) reflecting the three distinct repositories the paper publishes. The "35 vs 36" delta is a counting convention only; no source was added or omitted relative to the Triaged Source Inventory scope.

**Per-stratum entry counts:**

| Stratum | Tag | Entries | Sub-section |
|---|---|---|---|
| Priority production harnesses | B-priority | 3 | §3.priority |
| Research artifacts | A | 5 | §2 (with Meta-Harness as 3 sub-entries; ICM as 2) |
| Standard production harnesses | B-standard | 8 | §3.standard |
| Emerging harnesses | C | 8 | §4 |
| Methodology framework | D | 1 | §5 |
| Cross-platform meta-skill | D-meta | 3 | §6 |
| Thought-leader bodies of work | E | 4 (2 anchor + 2 channel companions) | §7 |
| Knowledge aggregators | F | 2 | §8 |
| Approach experiments | G | 2 | §9 |
| **Total** | | **36** | |

**Multi-tag stratum membership.** Per the Triaged Source Inventory §2 coverage observation 5, four entries straddle stratum boundaries and are recorded with multi-tag membership in the catalog:

| Entry | Primary stratum | Secondary stratum | Catalog location |
|---|---|---|---|
| ICM paper (arXiv 2603.16021) | A (research artifact) | D (methodology) | §2.4 (full Stratum A treatment); §5 cross-references |
| RinDig/Interpreted-Context-Methdology | A (research artifact) | D (methodology) | §2.5 (full Stratum A treatment); §5 cross-references |
| mindfold-ai/Trellis | C (emerging harness) | D-meta (cross-platform meta-skill) | §4.C3 (full Stratum C treatment); §6 cross-references |
| humanlayer/12-factor-agents | D (methodology) | E (thought-leader body — Dex Horthy) | §5.D1 (full Stratum D treatment); §7 cross-references |

**URL anomaly reconciliation.** Ten URL anomalies cataloged in Triaged Source Inventory Appendix B are reconciled in the catalog entries. The reconciliations are recorded inline in the affected entry's Identification block (§2.1 arXiv ID convention; §2.5 RinDig repo-name typo + paper footnote stale URL; §3.B1 OpenHands org rename; §3.B3 goose AAIF mirror; §3.priority-3 kilocode migration history; §3.priority-2 pi-mono → earendil-works/pi org migration; §4.C5 crush FSL-1.1-MIT non-OSI status; §4.C6 Kode-Agent vs Kode.git clone target; §3.B7 Dify modified Apache 2.0 license; §3.priority-1 DeerFlow 2.0 from-scratch rebuild vs 1.0).

**Priority-tier supplement.** The three priority-tier production harnesses (DeerFlow, pi-mono, kilocode — §3.priority-1, §3.priority-2, §3.priority-3) are profiled with a Session-3-style supplement (repository structure + architectural overview + distinguishing features + community signals + documentation quality) in addition to the standard catalog schema. All other entries use the standard schema (Identification / Pattern source context / Patterns extracted / V3 framing compatibility / Integration considerations / Critical assessment / Decision relevance / Citation strength). Stratum F entries (§8) use an abbreviated schema per Triaged Source Inventory pre-construction recommendation 4 (aggregators are pointers, not pattern sources).

**Cross-reference to Triaged Source Inventory.** This catalog instantiates the scope defined in *Triaged Source Inventory — Pattern Reference Catalog Pre-Construction* (project knowledge base file: `Triaged_Source_Inventory__Pattern_Reference_Catalog_Pre-Construction.md`). Decision codes (INCLUDE / INCLUDE-CROSSREF / DEFER / EXCLUDE) and per-source rationale are sourced from that document's Section 1 triage tables. Adjacent-discovery candidates flagged in Triaged Source Inventory §2 coverage observation 6 (`Picrew/awesome-agent-harness`, `HKUDS/nanobot`, `humanlayer/advanced-context-engineering-for-coding-agents`) are not catalogued in this v1.0; see §12 for follow-up disposition.

**Synthesis matrices (§10–§11).** Cross-source pattern matrix (§10) and decision-relevance matrix (§11) are computed against all 36 source rows. The §11.1 primary matrix uses Decision Relevance fields recorded in each entry; §11.2 per-axis recommendations and §11.3 decision-DAG mapping derive from §11.1. The "32 unique sources / 160 cells" referenced in the brief is a historical arithmetic and is reconciled in §11.1 to the actual 36 rows × 5 columns = 180 cells.

---

# §2. Stratum A — Research artifacts

Stratum A contains primary research artifacts: peer-style preprints and the canonical reference repositories that ship alongside them. These sources establish first-principles claims about how to build, optimize, and observe the *harness* layer that surrounds an LLM. Two research programs are catalogued in this session: (i) Stanford IRIS Lab / KRAFTON / MIT's **Meta-Harness** (Lee et al., arXiv 2603.28052) — a method for *automating* harness optimization through filesystem-mediated agentic search; and (ii) Eduba / Edinburgh's **Interpretable Context Methodology / Model Workspace Protocol** (Van Clief & McDermott, arXiv 2603.16021) — a *manual, human-reviewed* methodology that replaces framework orchestration with folder hierarchy. Both research programs converge on a common architectural primitive — **the filesystem as the durable substrate for agent state, history, and coordination** — but they apply that primitive at opposite ends of the operator-cost spectrum. Two of the five entries (§2.4, §2.5) are multi-tagged Stratum A + Stratum D because the ICM artifacts simultaneously function as a research contribution and as a deployable methodology framework; their full Stratum D treatment is deferred to Session D.

> **Note on arXiv ID convention.** The identifiers `2603.28052` and `2603.16021` follow arXiv's `YYMM.NNNNN` scheme: the leading `2603` denotes **March 2026**, not the year 2603. Both papers were posted in March 2026 and are addressed at their published submission dates below.

---

## §2.1 Meta-Harness paper (arXiv 2603.28052)

### Identification

- **Source name:** *Meta-Harness: End-to-End Optimization of Model Harnesses*
- **Stratum tags:** A (research artifact)
- **Maintainer / authors:** Yoonho Lee (Stanford), Roshen Nair (Stanford), Qizheng Zhang (Stanford), Kangwook Lee (KRAFTON), Omar Khattab (MIT), Chelsea Finn (Stanford)
- **Primary URL (canonical):** https://arxiv.org/abs/2603.28052
- **Secondary URLs:**
  - HTML rendering: https://arxiv.org/html/2603.28052v1
  - PDF: https://arxiv.org/pdf/2603.28052v1
  - Project page (interactive demo, leaderboard tables): https://yoonholee.com/meta-harness/
  - Reference code: https://github.com/stanford-iris-lab/meta-harness
  - Optimized TerminalBench-2 artifact: https://github.com/stanford-iris-lab/meta-harness-tbench2-artifact
- **Redirect / historical URLs:** None. v1 is the only posted version as of observation date 2026-05-08.
- **License:** arXiv preprint posted under **CC BY 4.0** (per arXiv HTML metadata). OSI-aligned.
- **Last meaningful activity:** v1 submitted **30 March 2026**; project page reflects v1 results. Observation date: 2026-05-08.
- **Star count:** N/A for paper itself (see §2.2 / §2.3 for repo signals).
- **Cross-reference to Session 3 profile:** None. Per the triage table, Stratum A entries carry no S3 cross-ref.
- **arXiv ID convention note:** `2603.28052` = March 2026, not year 2603.

### Pattern source context

- **Discovery context:** Surfaced through harness-engineering literature scan; widely cited in March–May 2026 practitioner writeups (LangChain harness-engineering report, Medium analyses, Hugging Face blog) as the first end-to-end automated harness optimizer with a published TerminalBench-2 result. Directly relevant to the project's *control plane* and *information substrate* axes because it formalizes "the harness" as the unit of optimization.
- **Stated thesis:** "The performance of LLM systems depends not only on model weights, but also on their harness" — and that harness can be optimized automatically by a coding-agent proposer with **unrestricted filesystem access** to the full source code, scores, and execution traces of every prior candidate. The diagnostic budget is on the order of **10 MTok/iteration**, ~3 orders of magnitude above prior text-optimizer feedback budgets (Table 1 of paper).
- **Architectural altitude:** Meta-harness / theoretical position. Meta-Harness is *itself* a harness for searching over task-specific harnesses; it occupies a strictly higher level of abstraction than the harnesses it produces. Mark altitude as **meta-skill / theoretical position**, with the artifact repos (§2.2, §2.3) as its **reference implementation**.

### Patterns extracted

1. **Filesystem-as-feedback-channel for the proposer** — Every prior candidate harness contributes a directory containing source code, scores, and execution traces (prompts, tool calls, outputs, state updates). The proposer (a coding agent — Claude Code with Opus-4.6 in the paper) navigates this growing filesystem 𝒟 via `grep`, `cat`, and similar terminal tools rather than ingesting it as one prompt; the filesystem is "typically far larger than the proposer's context window" (§3). In the most demanding setting the proposer reads a median of **82 files per iteration**, referencing 20+ prior candidates per step (Appendix A.1). *Axis: Information substrate (PRIMARY); Operational discipline (SECONDARY — observability is a byproduct).* Documented in §3 "Meta-Harness search loop" and Figure 2.

2. **Algorithm 1 — Meta-Harness outer loop** — Formal procedure: initialize population ℋ of valid harnesses and empty filesystem 𝒟; evaluate seeds and append to 𝒟; for N iterations the proposer queries 𝒟, proposes k candidates, each is interface-validated then evaluated and appended; return Pareto frontier. The objective is H* = argmax_H E_{x∼𝒳, τ∼p_M(H,x)} r(τ,x), with multi-objective evaluation (accuracy × context cost) reported as a Pareto frontier rather than a scalar. *Axis: Control plane (PRIMARY).* Documented in §3, Algorithm 1.

3. **Coding-agent proposer over raw-LLM proposer** — The proposer is deliberately not "a raw next-token model operating on a fixed prompt assembled by the outer loop"; it is an agent that retrieves, navigates, and edits code as part of search. The authors explicitly note this "only became practical recently, following major improvements in coding-agent capabilities around early 2026" (§3, footnote). *Axis: Control plane (PRIMARY); Action surface (SECONDARY).* Documented in §3 "Meta-Harness search loop" and "Practical implementation."

4. **Single-file Python harness as the unit of optimization** — In all three experimental domains, "each harness is a single-file Python program that modifies task-specific prompting, retrieval, memory, and orchestration logic" (§3, "Practical implementation"). Search is bounded by an interface validator, not by a fixed scaffold or DSL. *Axis: Action surface (PRIMARY); Information substrate (SECONDARY).* Documented in §3 and Appendix B.

5. **Pareto-frontier multi-objective search over (accuracy, context cost)** — Rather than committing to a scalar objective, Meta-Harness reports a frontier; the proposer can be steered to discover harnesses across a smooth accuracy–context curve (Figure 3 of paper). On online text classification, the discovered harness reaches **48.6% accuracy at 11.4K context tokens**, vs. ACE at 40.9% / 50.8K and MCE at 40.0% / 28.5K (Table 2). *Axis: Information substrate (PRIMARY); Operational discipline (SECONDARY — cost discipline).* Documented in §4.1 and Figure 3.

6. **Test-set isolation discipline** — "The proposer never sees test-set results; its only feedback comes from the search set … and from execution traces logged during those search runs" (§3). The authors additionally inspect for benchmark-specific string leakage on TerminalBench-2 and decontaminate the math retrieval corpus against eval benchmarks (§4.3, Appendix C.2). *Axis: Operational discipline (PRIMARY — anti-overfitting / evaluation hygiene).* Documented in §3, §4.3.

7. **Trace-access ablation result** — Table 3 ablation: scores-only proposer reaches 34.6 median / 41.3 best accuracy; scores-plus-LLM-summary reaches 34.9 / 38.7; full Meta-Harness with raw execution traces reaches **50.0 / 56.7**. The summary condition can underperform the scores-only condition, "suggesting LLM-generated summaries compress away diagnostically useful details." *Axis: Information substrate (PRIMARY).* Documented in §4.1, Table 3. This is the entry's strongest empirical claim about *why* compressed feedback is the wrong primitive for harness optimization.

8. **Environment-bootstrapping pattern (TerminalBench-2 discovered harness)** — The harness Meta-Harness discovered for TerminalBench-2 extends Terminus-KIRA by gathering a snapshot of the sandbox (working directory, file listing, available languages/tools, package managers, memory) and injecting it into the initial prompt, "saving 2–5 early exploration turns" the agent normally spends on `ls`, `which python3`, etc. *Axis: Information substrate (PRIMARY); Action surface (SECONDARY).* Documented in §4.3, Appendix B.3, and the artifact-repo README.

### Quantified results table (paper-reported)

| Domain | Base model | Comparator | Meta-Harness result | Source |
|---|---|---|---|---|
| Online text classification (avg of USPTO/S2D/Law) | GPT-OSS-120B | ACE 40.9% / 50.8K ctx; MCE 40.0% / 28.5K | **48.6%** / 11.4K ctx (+7.7 pts vs ACE, 4× fewer tokens) | Table 2 |
| Text classification, OOD (9 unseen datasets) | GPT-OSS-120B | ACE 70.2% | **73.1%** avg (+2.9 pts) | Table 5 |
| Retrieval-augmented IMO-level math (200 problems, 5 held-out models) | GPT-5.4-nano/mini, Gemini-3.1-FL/Gemini-3-F, GPT-OSS-20B | No retriever 34.1%; BM25 37.5% | **38.8%** avg pass@1 (+4.7 over no-retriever, +1.3 over BM25) | Table 6 |
| TerminalBench-2 (89 tasks × 5 trials) | Claude Opus 4.6 | Terminus-KIRA 74.7% | **76.4%** (#2 among Opus 4.6 agents at submission; behind ForgeCode 81.8%) | Project page, artifact README |
| TerminalBench-2 | Claude Haiku 4.5 | Goose 35.5% | **37.6%** (#1 among Haiku 4.5 agents at submission) | Project page |

> **Important leaderboard caveat.** The paper / project page report Meta-Harness as **"#2 among all Opus 4.6 agents"** — *not* #1 on the overall leaderboard. Subsequent leaderboard updates (April–May 2026) show GPT-5.5-class entries (Codex CLI / Claude "Mythos" preview) overtaking the field at ≥82%. The user's task-context phrasing "76.4% on Opus 4.6, #2 leaderboard at submission" matches the project page exactly.

### V3 framing compatibility

| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | **PASS** | The method is defined over arbitrary task distributions 𝒳 and a frozen base model M; ONBOARDING.md (in §2.2) gives a persona-agnostic onboarding flow with examples spanning solo and team workflows. |
| Stack-neutral | **PARTIAL** | The protocol is stack-neutral in principle (single-file Python harness + filesystem + any coding-agent proposer), but the shipped reference assumes Claude Code as proposer and `uv` as Python toolchain. Adapting to a different proposer requires writing a `claude_wrapper.py`-equivalent (acknowledged in repo README). |
| Deployment-surface-flexible | **PARTIAL** | Search loop is local-filesystem-first; nothing forbids running it against cloud sandboxes (and the TerminalBench-2 evaluation does run in Dockerized cloud-suitable sandboxes via Harbor/Runloop), but the "filesystem 𝒟" abstraction presupposes a single coherent FS namespace. Cross-host orchestration would require shared storage. |
| Multi-LLM | **PASS** | The base model M is explicitly frozen *per run* but not constrained to one vendor; the math experiments demonstrate transfer across five held-out models from three vendors (OpenAI, Google, OpenAI-OSS). The proposer model and the optimized harness model are decoupled. |
| Production-grade discipline | **PARTIAL** | Strong on evaluation hygiene (test-set isolation, contamination audits, Pareto reporting). Weaker on observability/security/HITL surfaces — those are acknowledged as future work; the harness produced by search has no built-in citation/anti-fabrication discipline beyond what the seed harness provides. |

### Integration considerations

- **License (CC BY 4.0 paper, MIT code):** No licensing impedance for project adoption.
- **Dependency on coding-agent capability ceiling:** The authors explicitly state Meta-Harness "only became practical … following major improvements in coding-agent capabilities around early 2026." Adopting Meta-Harness binds the project's *meta-optimization* layer to the proposer agent's tier; a regression or quota change at the proposer tier directly degrades search quality.
- **Compute envelope:** A typical run = ~60 harness evaluations over 20 iterations, with up to 10 MTok of diagnostic context per evaluation. This is a non-trivial offline cost; it is paid *once* per domain and amortized across deployment, but it is not a development-time cost the project should plan to incur every sprint.
- **Framing tension with §2.4 (ICM):** Meta-Harness *automates* the harness; ICM (§2.4) argues for keeping the harness *human-readable and human-edited*. These are not contradictory — Meta-Harness optimizes a single-file Python harness that *could* be the entry point of an ICM-style workflow — but adopting both requires a clear policy on which layers are search-optimized vs. human-edited.
- **Open question for project:** Does the project want a Meta-Harness-style outer loop in scope at all (i.e., is harness *search* in scope), or only the discovered patterns (filesystem feedback, environment bootstrapping, Pareto reporting) as design primitives? Until persona is committed, default to "patterns only."

### Critical assessment

- **Documented limitations (cited):**
  - Cost: "evaluation is the main computational bottleneck" (§4.1). Each candidate evaluation is non-trivial (e.g., a full TerminalBench-2 sweep is 89 tasks × 5 trials).
  - TerminalBench-2 search uses the same 89 tasks for search and final eval (§4.3); the authors mitigate via manual inspection and regex audits but acknowledge the lack of a held-out split is a concession to benchmark size.
  - Repo release note explicitly states the code "has not been tested beyond verifying that it runs" (§2.2 README).
  - Result is **#2** on the Opus 4.6 split, not overall #1; ForgeCode at 81.8% on Opus 4.6 outranks it at submission.
- **Inferred concerns [SPECULATIVE]:**
  - **[SPECULATIVE]** Reproducibility risk: with Claude Code / Opus-4.6 as proposer, the discovered harnesses are partially a function of that specific proposer's reasoning trace; a different proposer family may converge on different harnesses. The math experiment shows *harness* transfer across base models, but the authors do not show *search* transfer across proposers.
  - **[SPECULATIVE]** Diagnostic-context cost (10 MTok/iter) is the very thing prior optimizers compressed for a reason; pricing and latency at that scale may bite outside large-lab compute envelopes.
  - **[SPECULATIVE]** Filesystem 𝒟 is unbounded; the paper does not document a retention policy. Long-running search would need pruning to remain navigable.

### Decision relevance

| Axis | Relevance |
|---|---|
| Control plane (orchestration) | **PRIMARY** — defines an outer-loop control pattern (Algorithm 1) the project can adopt, partially adopt, or explicitly decline. |
| Information substrate (context/prompts/memory/state) | **PRIMARY** — strongest contribution; the trace-access ablation (Table 3) is the paper's most policy-relevant finding for *any* harness, search-optimized or not. |
| Action surface (tools/validation) | **SECONDARY** — interface validation step (Algorithm 1, line 11) is a useful pattern; environment-bootstrapping is a directly portable action-surface pattern. |
| Operational discipline | **SECONDARY** — strong evaluation hygiene; weak HITL/security. |
| Deployment surface | **TANGENTIAL** — agnostic to deployment surface; the filesystem assumption is satisfied by every plausible target. |

### Citation strength

**HIGH.** Primary source fetched end-to-end; algorithm box, formal objective, all four experiment tables, ablation table, and project-page leaderboard claims are recorded against §/Table references.

---

## §2.2 stanford-iris-lab/meta-harness (reference implementation)

### Identification

- **Source name:** `stanford-iris-lab/meta-harness` — *Reference code for the Meta-Harness paper.*
- **Stratum tags:** A (research artifact)
- **Maintainer:** Stanford IRIS Lab (organization owns 12 public repos as of 2026-05-08)
- **Primary URL (canonical):** https://github.com/stanford-iris-lab/meta-harness
- **Secondary URLs:**
  - Paper: https://arxiv.org/abs/2603.28052
  - Project page: https://yoonholee.com/meta-harness/
  - Sister repo (optimized TerminalBench-2 harness): https://github.com/stanford-iris-lab/meta-harness-tbench2-artifact (see §2.3)
  - Onboarding flow: https://github.com/stanford-iris-lab/meta-harness/blob/main/ONBOARDING.md
- **Redirect / historical URLs:** None.
- **License:** **MIT** (OSI-approved). `LICENSE` file at root.
- **Last meaningful activity:** 9 commits total on `main` as of observation date 2026-05-08; observation indicates repo is in initial-publication state ("This is a cleaned up version of the code we used for the paper. It has not been tested beyond verifying that it runs.").
- **Star count:** **34 stars / 3 forks / 1 watcher** (observed 2026-05-08; one search result snapshot showed 51 — star count is rising; treat 34 as the catalog-time anchor).
- **Cross-reference to Session 3 profile:** None (Stratum A).
- **arXiv ID convention note:** Paper cited in repo's `CITATION.cff` is `2603.28052` = March 2026.

### Repository structure (as fetched)

```
meta-harness/
├── assets/                       # paper figures used in README
├── reference_examples/
│   ├── text_classification/      # memory-system search; uv sync; meta_harness.py
│   └── terminal_bench_2/         # scaffold evolution; scripts/run_eval.sh; baseline_kira agent
├── .env.example
├── .gitignore
├── CITATION.cff                  # canonical BibTeX (lee2026metaharness…)
├── LICENSE                       # MIT
├── ONBOARDING.md                 # 203-line onboarding-prompt-as-pattern (see below)
└── README.md
```

Languages: **98.9% Python, 1.1% Shell**. Topics: `llm-agents`, `harness-engineering`.

### Pattern source context

- **Discovery context:** Linked from the paper's title page and the project page as the "Code" reference. Co-located with the optimized artifact repo (§2.3). Found via the paper's GitHub-pages link and corroborated through the IRIS Lab org index.
- **Stated thesis:** *"Meta-Harness is a framework for automated search over task-specific model harnesses … This repo contains the framework and two reference experiments from the paper."* The repo positions itself as a domain-portable scaffold, not just a paper appendix.
- **Architectural altitude:** Reference implementation + onboarding methodology. The repo embeds a methodology pattern (the ONBOARDING.md → domain_spec.md flow) that is itself catalogable independently of the paper's algorithm.

### Patterns extracted

1. **Onboarding-as-prompt-flow (ONBOARDING.md → domain_spec.md)** — The repo ships a 203-line onboarding prompt that the user is instructed to point a coding assistant at. The assistant then runs an interview ("Ask 1–2 focused questions at a time… If something is unknown, mark it explicitly as `unknown` and propose a default when possible") whose terminal artifact is a `domain_spec.md` containing six required sections: problem framing, harness definition, evaluation, baselines, offline experience, online experience. The onboarding prompt also encodes *anti-patterns*: examples of vague user answers and the screening questions that recover from them, plus an explicit "screening for poor fit" example that flags Meta-Harness as a wrong fit when no stable evaluation loop exists. *Axis: Information substrate (PRIMARY); Operational discipline (SECONDARY — evaluation-loop discipline, leakage screening).* Documented in `ONBOARDING.md`.

2. **`reference_examples/` two-experiment scaffolding** — The repo separates two paradigms of harness search:
   - `text_classification/`: memory-system search (small, fast iteration; `meta_harness.py` is the entrypoint).
   - `terminal_bench_2/`: scaffold-evolution search (long-horizon agentic coding; `scripts/run_eval.sh` driven; uses a `baseline_kira` agent module).
   Each subdir is uv-managed, locally runnable, and designed to be cloned-and-modified rather than imported as a library. *Axis: Control plane (PRIMARY).* Documented in `README.md` "Contents" section.

3. **Proposer-wrapper interface (`claude_wrapper.py` adapter pattern)** — The README explicitly documents how to swap proposers: *"To use a different proposer agent, adapt the example `claude_wrapper.py` scripts … The main requirement is a wrapper that cleanly logs proposer interactions."* This makes the proposer-agnosticism claim concrete: there is one named adapter file per reference example and a stated interface contract (clean logging of proposer interactions). *Axis: Control plane (PRIMARY); Action surface (SECONDARY).* Documented in `README.md` "Applying Meta-Harness To A New Domain."

4. **CITATION.cff first-class citizenship** — The repo ships a machine-readable `CITATION.cff` and a BibTeX block in the README. This is a small but signal-bearing pattern for any research-grade harness the project might ship: the citation surface is curated alongside the code. *Axis: Operational discipline (SECONDARY — provenance / reproducibility).* Documented in repo root.

### V3 framing compatibility

| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | **PASS** | ONBOARDING.md examples span single-developer ("customer-support agent on refund tickets") and team contexts; nothing in the repo presumes a persona. |
| Stack-neutral | **PARTIAL** | Python + `uv` toolchain hard-required; reference proposer is Claude Code; environment-bootstrapping reference example is bound to Harbor + Runloop sandbox runtime. Adapter path is documented. |
| Deployment-surface-flexible | **PARTIAL** | Local-first; the TerminalBench-2 example assumes a Harbor-managed sandbox surface that is cloud-or-local. Nothing forbids hybrid use. |
| Multi-LLM | **PASS** | Proposer model and optimized base model are independently configurable; reference examples already use different vendors (Claude Code as proposer, GPT-OSS-120B and Anthropic Claude as base models depending on experiment). |
| Production-grade discipline | **PARTIAL** | Repo explicitly disclaims production-readiness ("has not been tested beyond verifying that it runs"). ONBOARDING.md enforces evaluation hygiene strongly. |

### Integration considerations

- **License (MIT):** No licensing concern; redistribution and modification permitted.
- **Maturity disclaimer:** The README "Release Note" is unambiguous — this is a *reference* implementation. Treat as a pattern source, not a production dependency.
- **Adapter cost:** Replacing Claude Code as proposer is documented but non-zero; budget at least one engineer-week to validate a new wrapper.
- **ONBOARDING.md as standalone artifact:** The onboarding prompt is the single highest-leverage extract from this repo for the project: it is a reusable, persona-neutral, stack-neutral methodology pattern that can be adopted independently of whether the project adopts the Meta-Harness search loop itself. Recommend extracting this pattern verbatim into the project's own scaffold.
- **Open question for project:** Does the project want the ONBOARDING.md → domain_spec.md flow as a *project-wide* onboarding pattern (e.g., for any new agent/harness the project ships), or only for harnesses subject to outer-loop search?

### Critical assessment

- **Documented limitations (cited):** Repo is fresh (9 commits), single-contributor visible in the contributor list at observation, and explicitly untested beyond smoke-running. Star count (34) is signal-light and likely transient.
- **Inferred concerns [SPECULATIVE]:**
  - **[SPECULATIVE]** Maintenance trajectory uncertain — Stanford research-lab repos historically attract initial activity around publication and then plateau; abandonment risk is real and should not be discounted.
  - **[SPECULATIVE]** The `reference_examples/terminal_bench_2/` example is tightly coupled to the Harbor framework and Terminus-KIRA agent; if either upstream churns, the example breaks.

### Decision relevance

| Axis | Relevance |
|---|---|
| Control plane | **PRIMARY** — `meta_harness.py` is the canonical control-plane reference. |
| Information substrate | **SECONDARY** — patterns are paper-side; repo demonstrates them. |
| Action surface | **SECONDARY** — `claude_wrapper.py` adapter pattern. |
| Operational discipline | **PRIMARY** — ONBOARDING.md encodes an evaluation-hygiene methodology that is independently valuable. |
| Deployment surface | **TANGENTIAL**. |

### Citation strength

**HIGH.** Repo, README, ONBOARDING.md, license, commit count, star count all directly fetched.

---

## §2.3 stanford-iris-lab/meta-harness-tbench2-artifact

### Identification

- **Source name:** `stanford-iris-lab/meta-harness-tbench2-artifact` — *Meta-Harness: 76.4% on Terminal-Bench 2.0 (Claude Opus 4.6).*
- **Stratum tags:** A (research artifact)
- **Maintainer:** Stanford IRIS Lab
- **Primary URL (canonical):** https://github.com/stanford-iris-lab/meta-harness-tbench2-artifact
- **Secondary URLs:**
  - Paper: https://arxiv.org/abs/2603.28052
  - Sibling repo (framework + onboarding): https://github.com/stanford-iris-lab/meta-harness (§2.2)
  - Project page: https://yoonholee.com/meta-harness/
  - Built-on dependencies: KRAFTON's Terminus-KIRA (https://github.com/krafton-ai/KIRA); Harbor's Terminus-2 (https://github.com/laude-institute/harbor); Terminal-Bench 2.0 (https://tbench.ai)
- **Redirect / historical URLs:** None.
- **License:** **No LICENSE file present in repo root listing as of observation date 2026-05-08.** GitHub's repository UI does not display a license badge for this repo. *Treat as unlicensed (all rights reserved by default) until clarified.* This is a non-OSI flag relative to the sister framework repo's MIT license.
- **Last meaningful activity:** **1 commit on `main`** as of observation date 2026-05-08 (single drop alongside paper). README states "More details coming soon."
- **Star count:** **11 stars / 0 forks / 0 watchers** (observed 2026-05-08).
- **Cross-reference to Session 3 profile:** None (Stratum A).

### Repository structure (as fetched)

```
meta-harness-tbench2-artifact/
├── prompt-templates/             # the actual evolved prompt artifacts
├── README.md
├── agent.py                      # AgentHarness class — the discovered harness
├── anthropic_caching.py          # prompt-caching helpers for Anthropic API
└── pyproject.toml
```

Language: **100% Python**.

### Pattern source context

- **Discovery context:** This is the **frozen, post-search artifact** corresponding to the TerminalBench-2 row of the paper's results table. The repo exists specifically so that the leaderboard claim (76.4% on Opus 4.6) is independently runnable.
- **Stated thesis:** *"Agent scaffold for Terminal-Bench 2.0, built on top of Terminus-KIRA by KRAFTON AI and Harbor's Terminus-2 framework. … Meta-Harness extends the Terminus-KIRA agent with environment bootstrapping … The agent was discovered through automated harness evolution."*
- **Architectural altitude:** **Reference implementation of a single discovered harness** — the lowest abstraction level in this catalog session. Read this repo to see what a Meta-Harness *output* concretely looks like.

### Patterns extracted

1. **Environment-bootstrap prepass before agent loop** — Before the agent loop starts, the harness gathers a snapshot of the sandbox environment (working directory, file listing, available languages/tools, package managers, memory) and injects it into the initial prompt, "saving 2–5 early exploration turns that the agent normally spends on `ls`, `which python3`, etc." (README, "Method"). *Axis: Information substrate (PRIMARY); Action surface (SECONDARY).* Documented in `agent.py` and README.

2. **Structured-output via `tools` parameter rather than parsed JSON/XML** — Per the agent.py source surfaced in search results: *"Instead of prompting the model to output JSON/XML and parsing it, TerminusKira uses the `tools` parameter in LLM API calls for structured outputs."* This is a portable, Anthropic-native pattern for action-surface validation. *Axis: Action surface (PRIMARY); Operational discipline (SECONDARY — schema enforcement).* Documented in `agent.py`.

3. **Prompt-caching pattern (`anthropic_caching.py`)** — A dedicated module for Anthropic prompt caching, indicating that long-horizon TerminalBench-2 runs were materially cost/latency sensitive at the proposer-emitted-system-prompt level. *Axis: Operational discipline (PRIMARY — cost/latency); Information substrate (SECONDARY).* Documented in `anthropic_caching.py`.

4. **Model-coupling and harness-coupling cautions encoded in prompt** — The README and surfaced prompt fragments contain extremely specific instructions ("Do not include extra whitespace before or after the keystrokes…", "Never wait longer than 60 seconds; prefer to poll…", "On slow commands … set an appropriate duration as you determine necessary. It is better to set a smaller duration than a longer duration. It is always possible to wait again …"). These are concrete behavioral rules that emerged from search and that *do not generalize* outside the Terminal-Bench/Harbor sandbox. *Axis: Action surface (PRIMARY).* Documented in `agent.py` and `prompt-templates/`.

5. **Result split table** — The README documents the per-difficulty breakdown of the 76.4% headline:

   | Split | N | Score |
   |---|---|---|
   | Easy | 4 | 100.0 |
   | Medium | 55 | 81.1 |
   | Hard | 30 | 64.7 |
   | **All** | **89** | **76.4** |

   The harness's hard-split score (64.7%) is the load-bearing number for any decision about whether environment-bootstrapping generalizes to genuinely difficult work. *Axis: Operational discipline (PRIMARY).* Documented in README "Results."

### V3 framing compatibility

| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | **PASS** | Harness is task-shaped, not persona-shaped. |
| Stack-neutral | **FAIL** | Hard-coupled to Anthropic API (Opus 4.6), Harbor sandbox, Terminus-KIRA base, Terminal-Bench 2.0 task surface. Not portable as-is. |
| Deployment-surface-flexible | **PARTIAL** | Runs against Harbor-managed sandboxes (cloud or local Docker). |
| Multi-LLM | **FAIL** | Hard-coded to `anthropic/claude-opus-4-6`; structured-output pattern uses Anthropic `tools` parameter. |
| Production-grade discipline | **PARTIAL** | Caching, structured outputs, environment snapshots are production-shaped; absence of a license is a production blocker. |

### Integration considerations

- **License gap:** Most acute integration concern. With no LICENSE file, the repo is "all rights reserved" by default under U.S. copyright. The project should not vendor or fork code from this repo without first asking IRIS Lab to add a license, or it should treat the repo as a *read-only specification* and reimplement patterns. **Flag as non-OSI / license-missing.**
- **Coupling depth:** The agent is built on three external upstreams (Terminus-KIRA, Harbor Terminus-2, Anthropic). A change in any of the three breaks the artifact.
- **Patterns vs. code:** Recommend extracting the four patterns above (environment-bootstrap, tools-param structured outputs, prompt caching, hard-split reporting) as design primitives for the project's own action surface, *without* taking a code dependency on this repo.

### Critical assessment

- **Documented limitations (cited):**
  - 1 commit, "More details coming soon" — the artifact is a snapshot, not a maintained codebase.
  - Single-domain validity: the harness was searched against the 89-task TerminalBench-2 surface; transfer outside that surface is not claimed.
  - License absence (above).
  - 76.4% is **#2** on the Opus 4.6 split, behind ForgeCode at 81.8% (paper §4.3, project page).
- **Inferred concerns [SPECULATIVE]:**
  - **[SPECULATIVE]** Some of the per-task hard-coded behavioral rules in the prompt may be *near-overfits* to specific Terminal-Bench task families even after the authors' regex audits; the paper acknowledges this risk explicitly and mitigates by manual inspection only.
  - **[SPECULATIVE]** Without a license, downstream uptake will be limited; star count (11) is consistent with that.

### Decision relevance

| Axis | Relevance |
|---|---|
| Control plane | **TANGENTIAL** — this is a leaf harness, not a control structure. |
| Information substrate | **SECONDARY** — environment-bootstrap pattern is portable. |
| Action surface | **PRIMARY** — tools-parameter pattern, prompt caching, behavioral-rule encoding are directly applicable. |
| Operational discipline | **SECONDARY** — split-reporting and caching disciplines portable. |
| Deployment surface | **TANGENTIAL**. |

### Citation strength

**HIGH** for repo structure, license-absence flag, results table, and pattern surfacing. **MODERATE** for inferred behavior of `agent.py` since only excerpts (not full file) were directly fetched.

---

## §2.4 ICM paper (arXiv 2603.16021) — multi-tagged A + D

### Identification

- **Source name:** *Interpretable Context Methodology: Folder Structure as Agent Architecture* (paper title, v2). v1 used "Folder Structure as Agentic Architecture" and named the protocol **Model Workspace Protocol (MWP)**; v2 renamed both to **Interpretable Context Methodology (ICM)** with Folder Structure as Agent Architecture. Both v1 and v2 are catalog-relevant; v2 is the canonical text.
- **Stratum tags:** **A (research artifact) + D (methodology framework).** Multi-tag justified because the paper *defines* a methodology that is independently deployable; full Stratum D treatment is deferred to Session D.
- **Maintainer / authors:** Jake Van Clief, David McDermott — Eduba (Palm Coast, FL, USA) / University of Edinburgh. Contact: theceo@eduba.io.
- **Primary URL (canonical):** https://arxiv.org/abs/2603.16021
- **Secondary URLs:**
  - HTML v2: https://arxiv.org/html/2603.16021v2
  - HTML v1 (uses "MWP" terminology throughout): https://arxiv.org/html/2603.16021v1
  - PDF: https://arxiv.org/pdf/2603.16021
  - Companion repository (this catalog § 2.5): https://github.com/RinDig/Interpreted-Context-Methdology
  - Origin repo cited in §6: https://github.com/RinDig/Content-Agent-Routing-Promptbase
- **Redirect / historical URLs:** Paper footnote-1 in both v1 and v2 cites a repository URL `https://github.com/RinDig/Interpretable-Context-Methodology-ICM-` (with trailing hyphen) which **does not currently resolve** to an active GitHub repo; the de facto live companion is `https://github.com/RinDig/Interpreted-Context-Methdology` (see §2.5 for full anomaly reconciliation).
- **License:** **CC BY 4.0** (arXiv-side); the protocol itself is stated open-source under MIT (paper §1, footnote 1). OSI-aligned.
- **Last meaningful activity:** v1 submitted 17 Mar 2026; **v2 (canonical) submitted 18 Mar 2026**. 28 pages, 5 figures, 2 tables, 54 references. Categories cs.AI, cs.HC. Observation date: 2026-05-08.
- **Star count:** N/A for paper.
- **Cross-reference to Session 3 profile:** None for the Stratum A face. The Stratum D face will receive an S3 cross-ref in Session D.
- **arXiv ID convention note:** `2603.16021` = March 2026, not year 2603.

### Pattern source context

- **Discovery context:** Surfaced via direct counter-position to framework-level orchestration (CrewAI / LangChain / AutoGen). Architecturally adjacent to Meta-Harness (§2.1) on the *filesystem-as-substrate* axis but at the opposite extreme of operator cost: ICM is a **manual, human-reviewed** methodology, while Meta-Harness is **automated outer-loop search**.
- **Stated thesis:** *"This paper presents Interpretable Context Methodology (ICM), a method that replaces framework-level orchestration with filesystem structure. Numbered folders represent stages. Plain markdown files carry the prompts and context that tell a single AI agent what role to play at each step."* The strongest claim is that **for sequential, human-reviewed workflows, the filesystem is sufficient and a coordination framework is overhead.**
- **Architectural altitude:** **Methodology framework + theoretical position.** Section 6 explicitly proposes ICM as a multi-pass-compilation analogue for AI workflows ("ICM as Multi-Pass Incremental Compilation").

### Patterns extracted

1. **Five design principles (paper §3.1)** — Numbered, named, each tied to a pre-existing software-engineering source:
   - *One stage, one job* — McIlroy's Unix principle + Parnas's information-hiding criterion.
   - *Plain text as the interface* — Kernighan & Pike.
   - *Layered context loading* — citing Liu et al. "lost in the middle."
   - *Every output is an edit surface* — Horvitz mixed-initiative + Shneiderman direct manipulation.
   - *Configure the factory, not the product* — continuous-delivery-style separation of pipeline configuration from per-run product.
   *Axis: Information substrate (PRIMARY); Operational discipline (SECONDARY).* Documented in §3.1.

2. **Five-layer context hierarchy (paper §3.2, Figure 1)** — Formal context-loading specification with token budgets:

   | Layer | File | Question answered | Token budget |
   |---|---|---|---|
   | L0 | `CLAUDE.md` (or equivalent root identity file) | "Where am I?" | ~800 tok |
   | L1 | workspace `CONTEXT.md` | "Where do I go?" | ~300 tok |
   | L2 | `stages/NN-name/CONTEXT.md` | "What do I do?" | 200–500 tok |
   | L3 | reference material (factory) | "What rules apply?" | 500–2,000 tok, varies |
   | L4 | working artifacts (product) | "What am I working with?" | varies |

   Layers 0–2 are structural; Layers 3–4 are content. Layer 3 = reference material, persistent across runs ("the factory"); Layer 4 = per-run working artifacts ("the product"). Total typical context window per stage = **2,000–8,000 tokens**, contrasted with a monolithic baseline of **30,000–50,000 tokens**. *Axis: Information substrate (PRIMARY).* Documented in §3.2 and Figure 3.

3. **Stage contract specification (paper §3.3)** — Each stage's `CONTEXT.md` has three mandatory sections — **Inputs, Process, Outputs** — with an Inputs *table* that names exactly which Layer-3 and Layer-4 files (and which sections within them) the agent should load. The repository (§2.5) also surfaces *checkpoints* and *audits* as optional fourth/fifth sections for creative stages. *Axis: Action surface (PRIMARY); Operational discipline (SECONDARY — quality gates).* Documented in §3.3 and the §2.5 repo's `_core/CONVENTIONS.md`.

4. **Filesystem-as-orchestrator framing (paper §3.2 closing)** — *"Stage sequencing is the folder numbering. Context scoping is the folder hierarchy. State management is the files on disk. Coordination between stages is one folder's output being another folder's input."* This is the load-bearing thesis claim: every framework-resident state primitive maps to a filesystem primitive. *Axis: Control plane (PRIMARY); Information substrate (SECONDARY).* Documented in §3.2.

5. **Distinction between ICM and MCP (paper §2.2)** — *"MCP standardizes how models access external tools and data sources … ICM addresses a different layer: how to structure and deliver context to an agent across a multi-stage workflow. The two are complementary."* This is a deliberate axis-of-concern declaration that lets the project adopt ICM and Anthropic's Model Context Protocol simultaneously without conflict. *Axis: Action surface (PRIMARY).* Documented in §2.2.

6. **Observability-as-byproduct (paper §5.3)** — *"Because every intermediate output is a plain file, the system is observable by default. There is no logging layer to build, no dashboard to configure, no special tooling to inspect pipeline state."* The paper argues this aligns with EU AI Act human-oversight requirements (citing Enqvist 2023, Novelli et al. 2024) without claiming compliance. *Axis: Operational discipline (PRIMARY).* Documented in §5.3.

7. **U-shaped human-intervention pattern (paper §4.5, Figure 5)** — Self-reported observation from 33 of 52 practitioners across multi-stage ICM workspaces: heavy editing at stage 1 (direction-setting, ~92% report frequent edits), light editing in middle stages (~30%), heavy editing again at the final stage (~78%, alignment/debugging). The paper explicitly flags this as **practitioner self-report through conversation, not instrumented measurement**. *Axis: Operational discipline (SECONDARY — HITL pattern).* Documented in §4.5.

8. **Future-direction pattern: ICM as multi-pass incremental compilation (paper §6.1)** — A forward-looking architectural framing positioning each stage as a compiler pass, intermediate representations as the artifacts in `output/` folders, and proposing "semantic debugging" tooling that traces a defect at stage N back to its origin stage. **This is forward-looking, not currently implemented; mark as proposal, not pattern.** *Axis: Operational discipline (TANGENTIAL until implemented).* Documented in §6.

### V3 framing compatibility

| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | **PARTIAL** | The paper is candid that ICM is most useful for "sequential workflows where a human reviews output at each step" (§5.1). This implicitly assumes a single-operator or small-team persona; Section 5.2 ("Where this does not work") explicitly excludes high-concurrency multi-user surfaces. |
| Stack-neutral | **PASS** | "ICM is designed to be model-agnostic. The protocol specifies folder structure, file formats, and naming conventions. It does not depend on any model-specific capability" (§4.1). Tested with Claude only, but the protocol claims no vendor lock-in. |
| Deployment-surface-flexible | **FAIL** | "ICM is local-first by design. Scaling it to concurrent users would require building the infrastructure ICM was designed to avoid" (§5.2). For the project's design-time local target this is a PASS; for cloud-managed and hybrid surfaces this is a FAIL absent additional infrastructure. Net: **FAIL** at the cross-surface flexibility level the project requires; **PASS** at the local-development-target level. |
| Multi-LLM | **PARTIAL** | The protocol is model-agnostic, and §4.1 documents an Opus-4.6-orchestrating-Sonnet-4.6 sub-agent pattern; multi-vendor routing is not exercised but is not forbidden. |
| Production-grade discipline | **PARTIAL** | Strong on observability and HITL; weak on automated validation, anti-fabrication enforcement, and concurrent-user reliability. The paper's §4.6 "Threats to Validity" is unusually candid: no controlled comparison against monolithic prompting, single-model-family testing, informal data collection. |

### Integration considerations

- **Adoption cost: very low.** A workspace is a folder; no infrastructure, no server, no deployment artifact.
- **Framing tension with Meta-Harness (§2.1):** ICM's "every output is an edit surface" principle is incompatible with Meta-Harness's "the proposer never sees test-set results" discipline if applied at the *same* layer. They are compatible if applied at *different* layers: Meta-Harness searches the harness code (machine-edit), ICM structures the workflow the harness participates in (human-edit). The project should pin this layer separation explicitly.
- **License (CC BY 4.0 paper, MIT protocol):** No constraints.
- **Empirical fragility:** The paper's quantified claims (U-shape intervention, 30/33 practitioner reports, 2K–8K tokens per stage vs. 30K–50K monolithic baseline) are author-measured-not-replicated. The "lost in the middle" support (Liu et al. 2024) is theoretical, not measured on ICM workspaces directly. The paper's own §4.6 acknowledges this.
- **Open question for project:** Does the project want ICM as the **outer methodology** within which a multi-LLM harness sits (likely YES given the local-development-target framing), or only as a source of context-layering patterns? Default interpretation: ICM provides the workspace skeleton; multi-LLM routing decisions live inside individual stage `CONTEXT.md` files.

### Critical assessment

- **Documented limitations (paper §4.6, §5.2):**
  - "No controlled comparison has been conducted between ICM's staged context loading and a monolithic prompting approach on the same tasks."
  - All testing on a single model family (Claude Opus 4.6 + Sonnet 4.6); cross-model evaluation is future work.
  - U-shape intervention pattern is self-reported through conversation, not instrumented; community is invite-only and self-selected (selection + enthusiasm bias).
  - Explicitly does not work for: real-time multi-agent collaboration, high-concurrency multi-user systems, automated mid-pipeline branching.
- **Contested claims:**
  - The thesis that frameworks "introduce engineering overhead the problem does not require" is a position, not a measurement; CrewAI/LangChain/AutoGen advocates would dispute it.
  - The claim that ICM provides "full orchestration capability" for the addressed workflow class (§5.1) is asserted, not benchmarked.
- **Inferred concerns [SPECULATIVE]:**
  - **[SPECULATIVE]** ICM's reliance on the orchestrating model reading folder structure correctly is an unmeasured failure mode; if the model misroutes between Layer 2 and Layer 3, no compile-time check catches it.
  - **[SPECULATIVE]** Token-budget figures (2K–8K per stage) are workspace-dependent; the script-to-animation reference workspace is unusually tight.

### Decision relevance

| Axis | Relevance |
|---|---|
| Control plane | **PRIMARY** — proposes filesystem-as-orchestrator as a primary control structure. |
| Information substrate | **PRIMARY** — five-layer hierarchy is a directly adoptable specification. |
| Action surface | **SECONDARY** — stage contracts and the "every output is an edit surface" principle constrain action-surface design. |
| Operational discipline | **PRIMARY** — observability-as-byproduct, HITL gates, audits at stage boundaries. |
| Deployment surface | **PRIMARY for local-dev target; TANGENTIAL/FAIL for cross-surface.** Explicitly local-first by design. |

### Citation strength

**HIGH.** Paper fetched end-to-end (v2). Algorithm-equivalent (the five-layer hierarchy, stage-contract spec, intervention-pattern table) and quantified claims (token budgets, practitioner counts) are recorded against §/Figure references.

---

## §2.5 RinDig/Interpreted-Context-Methdology repository — multi-tagged A + D

### Identification

- **Source name:** Canonical (per paper title): *Interpretable Context Methodology (ICM)*. Actual repository name (per GitHub URL): `Interpreted-Context-Methdology` — note **two spelling anomalies in the repo name**: (i) "Interpreted" instead of "Interpretable"; (ii) "Methdology" instead of "Methodology" (missing 'o' between 'h' and 'd'). The repository's own README banner reads "Interpretable Context Methdology (ICM)" — i.e., the README corrects the first typo but preserves the second. The paper consistently uses *Interpretable Context Methodology*. **The catalog records the canonical spelling per the paper title in this Identification block, and lists the actual (typo-preserving) GitHub URL as the primary URL.**
- **Stratum tags:** **A (research artifact) + D (methodology framework).** Same multi-tag justification as §2.4. Full Stratum D treatment deferred to Session D.
- **Maintainer:** Jake Van Clief (GitHub user `RinDig`); credited contributors are RinDig and a `@claude` automation account.
- **Primary URL (actual, typo-preserving):** https://github.com/RinDig/Interpreted-Context-Methdology
- **Secondary URLs:**
  - Paper: https://arxiv.org/abs/2603.16021
  - Conventions spec: https://github.com/RinDig/Interpreted-Context-Methdology/blob/main/_core/CONVENTIONS.md (referenced from README)
  - PRD documents in repo root: `MWP-PRD.md`, `MWP-V2-PRD.md` (preserve the v1 protocol name)
  - Origin / sister repo: https://github.com/RinDig/Content-Agent-Routing-Promptbase
  - Third-party guide: https://gist.github.com/LvlyBot/91c386584c99e4f3c300013d5cebaf78 (independent ICM-as-implemented-in-Lovely-monorepo guide)
- **Redirect / historical URLs (anomaly reconciliation):**
  - Paper footnote 1 (both v1 and v2) cites `https://github.com/RinDig/Interpretable-Context-Methodology-ICM-` (with trailing hyphen). **At observation date 2026-05-08, this URL does not appear in search-index hits as a live repo and was not retrievable; treat as a stale or never-finalized redirect.**
  - The paper's v1 (17 Mar 2026) refers to the protocol as **MWP (Model Workspace Protocol)**; v2 (18 Mar 2026) renames to **ICM (Interpretable Context Methodology)**. The repository's README and About text inconsistently mix both names ("ICM" in README body, "MWP" in repo description text "MWP replaces framework-level orchestration with filesystem structure"). PRD files in the repo retain the MWP name. Treat ICM as canonical (paper-current) and MWP as the historical name; both URLs and references should resolve to this same artifact.
  - **Anomaly summary:**
    1. Paper-cited URL (`Interpretable-Context-Methodology-ICM-`) does not resolve.
    2. Live URL (`Interpreted-Context-Methdology`) carries two typos in the slug.
    3. The repo's GitHub "About" sentence still uses MWP terminology; the README body uses ICM.
    Both the live URL and the canonical (paper) name are recorded explicitly above.
- **License:** **MIT** (per `LICENSE` file at repo root; OSI-approved). README confirms MIT.
- **Last meaningful activity:** **14 commits on `main`** as of observation date 2026-05-08. No releases published. 0 packages.
- **Star count:** **45 stars / 3 forks / 1 watcher / 2 contributors** (observed 2026-05-08).
- **Cross-reference to Session 3 profile:** None for Stratum A face. Stratum D face will receive S3 cross-ref in Session D.

### Repository structure (as fetched)

```
Interpreted-Context-Methdology/
├── _core/                        # CONVENTIONS.md (15 patterns) — load-bearing
├── workspaces/
│   ├── script-to-animation/      # 3-stage ref workspace
│   ├── course-deck-production/   # 5-stage ref workspace
│   └── workspace-builder/        # 5-stage workspace whose output is a workspace
├── .gitignore
├── CLAUDE.md                     # Layer 0 root identity file
├── LICENSE                       # MIT
├── MWP-PRD.md                    # historical PRD (v1 protocol naming)
├── MWP-V2-PRD.md                 # historical PRD (v1→v2 transition)
└── README.md
```

Languages reported by GitHub: **Python 77.6% / JavaScript 18.5% / TypeScript 3.9%**. (The Python-heavy distribution reflects local scripts and the Remotion build path inside `workspaces/script-to-animation/`, not the protocol itself, which is markdown-and-folders.)

### Pattern source context

- **Discovery context:** Direct companion to §2.4 paper. Adopted as a primary Stratum A artifact because it is the *only* runnable instantiation of the protocol the paper describes. Three workspaces ship: a content/animation pipeline, a slide-deck pipeline, and a workspace-builder.
- **Stated thesis:** README is a near-verbatim distillation of the paper. *"Folder structure as agent architecture. ICM replaces framework-level orchestration with filesystem structure."* The repo additionally formalizes a 15-convention specification (`_core/CONVENTIONS.md`) referenced by the README.
- **Architectural altitude:** **Reference implementation of methodology** + minimum-viable bootstrap (workspace-builder workspace).

### Patterns extracted

1. **Workspace-builder bootstrap pattern** — A workspace whose output is a new workspace, walking the user through five stages: discovery, stage-mapping, scaffolding, questionnaire design, validation. The builder enforces ICM conventions on its own output, so any workspace produced through it inherits the convention set. *Axis: Control plane (PRIMARY); Operational discipline (SECONDARY).* Documented in `workspaces/workspace-builder/` and README.

2. **15-convention specification (`_core/CONVENTIONS.md`)** — Architecture/Quality/Onboarding categories. Architecture conventions named in the README: stage contracts; stage handoffs; one-way references; selective section routing; canonical sources. Quality conventions: specs-are-contracts; checkpoints; stage audits; value validation; docs-over-outputs ("Agents do not read previous outputs to learn patterns. Early outputs are the worst outputs."). Onboarding conventions: questionnaire design; shared constants. *Axis: Operational discipline (PRIMARY); Information substrate (SECONDARY).*

3. **Selective section routing in stage contracts** — Each stage `CONTEXT.md` Inputs table specifies *which sections* of which files to load, not whole files. *"Without this scoping, an agent would either load everything or guess."* This is a finer-grained version of the paper's Layer-2 specification. *Axis: Information substrate (PRIMARY).* Documented in README and `_core/CONVENTIONS.md`.

4. **Canonical sources / no-duplication discipline** — *"Every piece of information has one home. Other files point there. The moment the same rule exists in two files, they drift."* Functions as an anti-fabrication / anti-drift convention at the workspace level. *Axis: Operational discipline (PRIMARY); Information substrate (SECONDARY).* Documented in README "The Conventions" → Architecture.

5. **Checkpoints and audits at stage level** — Creative stages pause for human steering between sub-units (checkpoints); quality checklists run after stage completion but before output write (audits). Each audit check has "an unambiguous pass condition." *Axis: Operational discipline (PRIMARY — HITL + automated quality gates).* Documented in README "Stage Contracts" and conventions.

6. **`docs-over-outputs` convention** — Agents are required to read reference docs (Layer 3) for build patterns rather than learning from prior stage outputs (Layer 4). Stated rationale: *"Early outputs are the worst outputs. If future agents learn from them, quality never improves."* This is a load-bearing convention against drift in self-improving loops. *Axis: Information substrate (PRIMARY).* Documented in README "Quality" conventions.

7. **PR-ready contribution checklist** — Repo's README ships a structured checklist for submitting new workspaces (built via workspace-builder; setup runs cleanly; ≥1 end-to-end run; no committed stage outputs; CONTEXT.md ≤80 lines; reference files ≤200 lines; creative stages have ≥1 checkpoint and an audit; no circular dependencies). This is itself a methodology-governance pattern. *Axis: Operational discipline (SECONDARY).*

### V3 framing compatibility

| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | **PARTIAL** | Same as §2.4: methodology presupposes single-operator or small-team workflows. The 52-member practitioner community spans solo creators through small organizations. |
| Stack-neutral | **PASS** | Repo is markdown + folders + small Python scripts; no framework dependency. Reference workspaces use Remotion / PowerPoint generation, but those are workspace-specific, not protocol-specific. |
| Deployment-surface-flexible | **FAIL** | Same as §2.4: explicitly local-first; high-concurrency excluded. **PASS** at the project's local-development-target level. |
| Multi-LLM | **PARTIAL** | The orchestrator-delegates-to-sub-agent pattern (Opus 4.6 → Sonnet 4.6 via Agent Teams) is documented but is single-vendor. Multi-vendor routing is not exercised. |
| Production-grade discipline | **PARTIAL** | Strong on convention enforcement, weak on automated validation infrastructure. The paper's §4.6 caveats apply here too. |

### Integration considerations

- **License (MIT):** No constraints. Patterns and code may be vendored.
- **URL anomaly mitigation:** Project should pin the *actual* live URL `https://github.com/RinDig/Interpreted-Context-Methdology` in any internal reference. Do not link to the paper-footnote URL (`Interpretable-Context-Methodology-ICM-`) until/unless the maintainer publishes a redirect.
- **Naming hygiene risk:** The repo's mixed ICM/MWP naming inside its own description, README, and PRD files is a maintenance smell. The project should adopt **ICM** (per paper v2) as the canonical name and document the alias once.
- **Workspace-builder as primary integration entry point:** Recommend the project adopt the workspace-builder as the *only* sanctioned way to scaffold new ICM workspaces, exactly as the repo's PR checklist requires for external contributions.
- **Convention-set adoption:** The 15-convention spec (`_core/CONVENTIONS.md`) is self-contained and adoptable independently of the rest of the repo. Recommend extracting and pinning at a known commit hash in the project's documentation.
- **Open question for project:** Does the project intend to ship its multi-LLM agent harness *as* an ICM workspace, or to ship ICM-style conventions *inside* a different orchestration substrate? The two answers imply very different §2.5 dependency depths.

### Critical assessment

- **Documented limitations:**
  - Paper §4.6 caveats (informal data collection, single-model-family testing, no controlled comparison) apply to the artifacts in this repo.
  - 14 commits, single primary contributor (`@RinDig`) with assist from `@claude` automation. Bus factor is 1.
  - Repository name typos and ICM/MWP terminology drift suggest the project is at "rough first cut" maturity even if the protocol itself is well-specified.
  - Practitioner-community claims (52 members, deployments at Edinburgh Neuropolitics Lab, ICR Research, Academy of International Affairs Bonn) are author-reported and not independently verified at the catalog observation date; the paper acknowledges some are NDA-blocked.
- **Inferred concerns [SPECULATIVE]:**
  - **[SPECULATIVE]** With one human maintainer plus a Claude automation account, abandonment risk is non-trivial; the project should treat the conventions as a specification to vendor rather than a dependency to track upstream.
  - **[SPECULATIVE]** The repo's all-rights-defaults around stage outputs (output folders should contain only `.gitkeep`) suggests prior accidental output commits — a reproducibility hygiene risk the project should plan around.

### Decision relevance

| Axis | Relevance |
|---|---|
| Control plane | **PRIMARY** — workspace-builder is the canonical bootstrap path. |
| Information substrate | **PRIMARY** — five-layer hierarchy + selective section routing. |
| Action surface | **SECONDARY** — stage contracts (Inputs/Process/Outputs/Checkpoints/Audits) define the permitted action surface per stage. |
| Operational discipline | **PRIMARY** — 15-convention spec is the strongest operational-discipline pattern in this catalog session. |
| Deployment surface | **PRIMARY for local-dev target; FAIL for high-concurrency cloud surface.** Explicitly local-first. |

### Citation strength

**HIGH.** Repo, README, license, commit count, contributor list, language breakdown, and folder structure all directly fetched. URL anomaly explicitly reconciled with three sub-cases.

# §3. Stratum B — Production agent harnesses

Stratum B holds production-grade agent harnesses with significant adoption signal (≥8K stars or institutional backing) and operational discipline (sandboxing, observability, permissioning, or governance present rather than aspirational). The stratum is split into two subsections that differ on origin in this catalog rather than on architectural altitude. **§3.priority** profiles three Session-3-omitted production harnesses (DeerFlow, pi-mono, kilocode) with a Session-3-style supplement (repository structure, architectural overview, distinguishing features, community signals, documentation quality) atop the standard catalog schema; these are the highest-leverage gaps the Triaged Source Inventory surfaced. **§3.standard** contains the eight production harnesses cataloged at standard depth — four cross-referenced from Session 3 profiles (OpenHands, Cline, goose, Roo Code) plus four fresh-research entries (OpenHarness, deepagents, Dify, VoltAgent). The eleven entries together cover the production-archetype space the harness design must reason about: opinionated framework-host (DeerFlow, Dify), composable substrate library (pi-mono, deepagents), client-server agent core (kilocode, OpenHands, goose), Cline-lineage IDE coding agents (Cline, Roo Code), academic flagship harness-as-substrate (OpenHarness), and TypeScript-first observability-split framework (VoltAgent).

# §3.priority — Priority-tier production harness anchors

This subsection profiles three Session-3-omitted production harnesses that exceed the 1k-star threshold by an order of magnitude, carry permissive MIT licensing, and exhibit very active maintenance as of May 2026. Each is pattern-rich enough to warrant the full Session-3-style profile supplement (repository structure, architectural overview, distinguishing features, community signals, documentation quality) alongside the standard schema. They are anchored here because each addresses a load-bearing harness concern the catalog cannot leave unprofiled: DeerFlow contributes a complete batteries-included long-horizon orchestration surface; pi-mono contributes a layered, package-decomposed unified multi-LLM substrate plus minimal agent runtime; kilocode contributes a Cline/OpenCode-lineage IDE-coding-agent harness with explicit multi-mode control plane, persistent project memory, and a CLI-server architecture. Together they cover the three production archetypes the harness design must reason about: the **opinionated framework-host** (DeerFlow), the **composable substrate library** (pi-mono), and the **client-server agent core** (kilocode).

---

## §3.priority-1: bytedance/deer-flow (DeerFlow 2.0)

### Identification

| Field | Value |
|---|---|
| Source name | DeerFlow (Deep Exploration and Efficient Research Flow), v2.0 |
| Stratum tags | B (production harness), priority-tier |
| Maintainer / author | ByteDance (org repo); core maintainers include WillemJiang and others listed in the project's acknowledgements section [HIGH] |
| Primary URL (canonical) | https://github.com/bytedance/deer-flow |
| Secondary URLs | https://deerflow.tech/ (project site); https://deepwiki.com/bytedance/deer-flow (third-party generated wiki, used here as cross-reference, not primary) |
| Redirect / historical URLs | None — repo URL stable; the legacy 1.x codebase is preserved on the `1.x` branch of the same repository, not at a separate URL [HIGH] |
| License | MIT [HIGH] (README license section) |
| Last meaningful activity | Commit activity through May 5, 2026; weekly progress reports filed (e.g., issue #2051 covering 2026-04-03 → 2026-04-09); active issue triage on Apr 22, 2026 [HIGH], observed May 8, 2026 |
| Star count | ~64.7k–65k stars [HIGH] (org repo listing showing 65k; activity page showing 64.7k), observed May 8, 2026 |
| Cross-reference to Session 3 profile | NONE (Session 3 omission) |

### Pattern source context

- **Discovery context.** Surfaced as a Session-3 omission because DeerFlow 2.0 is the highest-star end-to-end "super agent harness" on GitHub at the time of catalog construction and explicitly self-describes as a *harness* in the same sense the project uses (README §"From Framework to Harness"). Its February 2026 ground-up rebuild and #1 GitHub Trending placement on Feb 28, 2026 [HIGH] make it the dominant exemplar of the opinionated-framework-host archetype.
- **Stated thesis.** The README frames DeerFlow as a *runtime providing the infrastructure agents need to actually complete work* — not a framework one wires together but a batteries-included execution environment with sandbox, memory, skills, sub-agents, and a message gateway shipped in the box.
- **Architectural altitude.** Harness (production) + reference implementation. Not a framework in the LangGraph sense — DeerFlow consumes LangGraph as a library rather than exposing one. Closer to a turnkey super-agent appliance whose patterns can be lifted out.

### Profile (priority-tier supplement)

**Repository structure** (top-level, from README and CONTRIBUTING.md). Layout:

```
deer-flow/
├── config.example.yaml             # Configuration template
├── extensions_config.example.json  # MCP & skills configuration
├── Makefile                        # check/install/dev/stop
├── docker/                         # Compose + nginx configs
├── backend/                        # Python backend
│   └── src/{gateway, agents, mcp, skills, sandbox, subagents,
│              models, tools, memory, community, reflection, config}
├── frontend/                       # Web frontend
└── skills/{public, custom}         # Agent skills (markdown)
```
The deeper backend layout (per `backend/README.md`) places the lead agent factory at `backend/src/agents/lead_agent/`, the middleware chain at `backend/src/agents/middlewares/` (9 middlewares), thread-state schema at `backend/src/agents/thread_state.py`, sandbox abstraction at `backend/src/sandbox/`, sub-agent orchestration at `backend/src/subagents/`, and the FastAPI gateway with six router modules at `backend/src/gateway/` [HIGH].

**Architectural overview.** DeerFlow 2.0 runs four primary processes plus one optional process behind a single Nginx reverse proxy on port 2026 [HIGH]:

| Process | Port | Role |
|---|---|---|
| Nginx | 2026 | Single ingress; routes `/api/langgraph/*` to LangGraph server, `/api/*` to Gateway API |
| LangGraph Server | 2024 | Hosts the single `lead_agent` graph; runs middleware chain, tools, sub-agents |
| Gateway API (FastAPI) | 8001 | Models, MCP, skills, memory, uploads, artifacts, thread-local cleanup |
| Frontend (web) | 3000 | Hot-reload web UI |
| Provisioner | 8002 | Optional; only started in provisioner/Kubernetes sandbox mode |

The agent loop is a *single* LangGraph agent — `lead_agent`, assembled by `make_lead_agent(config)` in `backend/src/agents/lead_agent/agent.py` — combining (1) dynamic model selection via `create_chat_model()` with thinking/vision support, (2) a fixed-order middleware chain of 9 middlewares (`before_agent`/`before_model`/`after_model`/`wrap_model_call` hooks), and (3) tools assembled by `get_available_tools()` which combines sandbox tools, MCP tools, built-in tools, and the `task()` sub-agent delegation tool [HIGH]. State lives in `ThreadState` (extending LangGraph `AgentState`) with custom reducers `merge_artifacts` and `merge_viewed_images`, and persists per-thread `sandbox`, `thread_data`, `title`, `artifacts`, `todos`, `uploaded_files`, and `viewed_images` fields [HIGH]. Long-term memory is a JSON-file-backed system with confidence-scored facts, debounced LLM-driven extraction, and prompt injection of top facts [HIGH].

**Distinguishing features.**

1. **"Decompose, Delegate, Synthesize" sub-agent model with hard concurrency caps.** The `task()` tool spawns sub-agents in the background; built-in agents are `general-purpose` (full toolset) and `bash` (only when shell access is available). Hard limit is 3 concurrent sub-agents per turn, 15-minute timeout per sub-agent [HIGH] (`backend/README.md`).
2. **Skills as progressive-load Markdown capability modules.** `SKILL.md` files under `skills/{public,custom}` are recursively discovered; nested container paths preserved; loaded via background worker thread `_refresh_enabled_skills_cache_worker` to avoid blocking prompt assembly [HIGH] (`backend/packages/harness/deerflow/agents/lead_agent/prompt.py:34-52`).
3. **Pluggable sandbox backends.** `LocalSandboxProvider` (host filesystem), `AioSandboxProvider` (Docker / Apple Containers, all-in-one image with browser+shell+File+MCP+VSCode Server), `RemoteSandboxBackend` (K8s provisioner). `bash` is disabled by default for `LocalSandboxProvider` [HIGH].
4. **First-class messaging-channel gateway.** Native channels for Feishu, Slack, Telegram, DingTalk, WeCom, WeChat, configured in `config.yaml` under `channels:`; channels speak to the Gateway via the same `langgraph-sdk` HTTP client the frontend uses, with internal-auth + matching CSRF cookie/header injection [HIGH].
5. **Three execution context modes.** Flash (`thinking_enabled:false, is_plan_mode:false, subagent_enabled:false`), Pro, and Ultra — selected per-run via the `context` block on the `runs/stream` SSE endpoint [HIGH] (`skills/public/claude-to-deerflow/SKILL.md`).
6. **"Agent Soul" prompt layer.** `SOUL.md` files inside an agent directory are loaded by `load_agent_soul(name)` and wrapped in `<soul>` tags inside the system prompt; supports an optional "Skill Self-Evolution" instruction block [HIGH] (`backend/packages/harness/deerflow/agents/lead_agent/prompt.py:7,151-164`).
7. **Embedded mode.** `DeerFlowClient` provides direct in-process access to all DeerFlow capabilities without HTTP services, sharing config files and data dirs with Gateway [HIGH].

**Community signals.** ByteDance is a single-vendor commercial backer (corporate-OSS pattern). PR/issue throughput is high: ~214 open PRs / 1,060 closed; fork count 8.5k–8.6k [HIGH], observed May 8, 2026. Weekly progress reports are filed as issues by `WillemJiang` (e.g., #2051 covering 2026-04-03 → 2026-04-09). Q2 2026 roadmap tracked in issue #1669. Hit #1 on GitHub Trending Feb 28, 2026 following 2.0 launch [HIGH]. Recommended models in the README skew toward Doubao-Seed-2.0-Code, DeepSeek v3.2, and Kimi 2.5 — a non-trivial vendor signal (Doubao is ByteDance's own).

**Documentation quality.** README is organized but long and operational rather than architectural; deeper architecture lives in `backend/README.md`, `backend/CLAUDE.md`, and `backend/docs/CONFIGURATION.md`. The `skills/public/claude-to-deerflow/SKILL.md` doubles as a complete API reference for the SSE `runs/stream` protocol [HIGH]. *Under-documented:* memory subsystem internals beyond the high-level "confidence scores + debounced updates" description; failure modes of the middleware chain; detailed MCP OAuth flow edge cases. The canonical reference is the in-tree `backend/README.md` plus `backend/CLAUDE.md`; third-party DeepWiki coverage exists but is generated, not curated.

### Patterns extracted

1. **Lead-agent + middleware-chain orchestrator.** A single LangGraph agent serves as runtime entry point; cross-cutting concerns (sandbox lifecycle, memory injection, sub-agent limits, thinking-mode gating, etc.) are factored into a fixed-order middleware chain rather than branching graph nodes. Middlewares implement `before_agent` / `before_model` / `after_model` / `wrap_model_call` hooks. *Axes:* PRIMARY control plane, SECONDARY information substrate. *Documented in:* `backend/src/agents/lead_agent/agent.py` (`make_lead_agent`, `_build_middlewares`); `backend/README.md` "Lead Agent" section.
2. **Recursive sub-agent delegation via the `task()` tool with hard concurrency caps.** Lead agent emits structured sub-task requests through a tool; an executor runs each in the background with its own scoped context, tools, and termination conditions; results stream back through `messages-tuple` SSE events. Hardcoded 3-concurrent / 15-min cap surfaces operational discipline directly in the prompt. *Axes:* PRIMARY control plane, SECONDARY operational discipline. *Documented in:* `backend/src/tools/builtins/task_tool.py`, `backend/src/subagents/executor.py`, `backend/src/agents/middlewares/subagent_limit_middleware.py`.
3. **Progressive-load Markdown skills with self-evolution affordance.** Capabilities packaged as `SKILL.md` workflow definitions discovered recursively, loaded on demand into the prompt rather than all at once, and (optionally) updated by the agent itself after complex tasks. *Axes:* PRIMARY information substrate, SECONDARY action surface. *Documented in:* `backend/packages/harness/deerflow/agents/lead_agent/prompt.py:22-52,151-164`; README "Skills" section.
4. **Pluggable sandbox provider abstraction with virtual path translation.** A `Sandbox` interface with `acquire()`/`release()` and three concrete providers (local / Aio Docker / remote K8s) decouples the agent's view of the filesystem from the host's. Path translation isolates the agent's `<working_directory>` from host paths. *Axes:* PRIMARY action surface, SECONDARY deployment surface. *Documented in:* `backend/src/sandbox/sandbox.py`, `backend/CLAUDE.md` "Sandbox Architecture"; `config.example.yaml` lines 160-212.
5. **Per-thread state engine with custom reducers.** `ThreadState` extends `AgentState` with sandbox handle, thread data, artifacts, todos, uploads, and viewed images; custom reducers (`merge_artifacts`, `merge_viewed_images`) make state evolution deterministic across replay. *Axes:* PRIMARY information substrate, SECONDARY operational discipline. *Documented in:* `backend/src/agents/thread_state.py`.
6. **Messaging-channel gateway as a first-class harness surface.** Channels are server-side workers that speak to the LangGraph runtime through the same SDK as the web frontend, injecting internal auth + CSRF, allowing inbound and streamed outbound across Feishu/Slack/Telegram/DingTalk/WeCom without a public callback URL. *Axes:* PRIMARY action surface, SECONDARY deployment surface. *Documented in:* README "Multi-Channel Deployment"; `backend/CLAUDE.md` channels section.
7. **Embedded vs HTTP dual-mode runtime.** `DeerFlowClient` exposes the same response schemas in-process (no FastAPI dependency) as the HTTP Gateway. Same config files, same data dirs. Lets the same harness code be called from a long-running service or imported as a library. *Axes:* PRIMARY deployment surface, SECONDARY control plane. *Documented in:* `backend/CLAUDE.md` `DeerFlowClient` section.
8. **Soul + skills + memory composite system prompt.** XML-tagged sections (`<soul>`, `<subagent_system>`, `<working_directory>`, skill index, memory facts) assembled per-run; concurrency limits are inlined as prompt-level instructions, not just runtime guards. *Axes:* PRIMARY information substrate. *Documented in:* `backend/packages/harness/deerflow/agents/lead_agent/prompt.py`.

### V3 framing compatibility

| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | PARTIAL | Skills + Soul layer accommodates persona injection, but built-in skills (research/report/slides/podcasts) bias the default toward a research-author persona. |
| Stack-neutral | FAIL | Hard-bound to Python + LangGraph + LangChain + FastAPI + Nginx + Node frontend. Lifting individual patterns is feasible; lifting the harness whole imports the stack. |
| Deployment-surface-flexible | PASS | Local-trusted-host default, Docker Compose, Kubernetes provisioner, and embedded `DeerFlowClient` mode are all first-class. |
| Multi-LLM | PASS | OpenAI-compatible model abstraction; `litellm` integration; `models.yaml` model registry; first-class support for Doubao, DeepSeek, Kimi, OpenAI, Anthropic, vLLM. Best-effort vendor neutrality despite ByteDance favoring Doubao defaults. |
| Production-grade discipline | PASS | Middleware chain, sandbox isolation, recursion/concurrency caps, debounced memory writes, regression coverage in `backend/tests/`, explicit security-perimeter doc in README. |

### Integration considerations

- **Stack import is the dominant cost.** Adopting the lead-agent + middleware-chain pattern wholesale requires LangGraph as a runtime dependency. Lifting the *pattern* without the dependency is feasible but loses the `before_model`/`wrap_model_call` machinery LangGraph supplies — the abstraction would have to be re-implemented.
- **License is permissive (MIT).** No copyleft constraint on adopting code or patterns.
- **Framing tension:** DeerFlow's README explicitly warns it is "designed by default to be deployed in a local trusted environment (accessible only via the 127.0.0.1 loopback interface)." This aligns with the harness project's local-development-as-design-time-target framing but means DeerFlow's *own* security posture assumes loopback-only; production hardening for non-loopback exposure is the adopter's problem.
- **Skills-as-Markdown is portable.** The `SKILL.md` convention can be lifted independently of the LangGraph runtime; the progressive-load pattern is the higher-value extract.
- **Implementation effort.** Adopting the channel-gateway pattern is high-effort (per-platform SDKs, OAuth flows). Adopting the sub-agent task-delegation pattern is moderate-effort given any reasonable agent loop. Adopting the middleware chain is low-effort once the agent loop exists.

### Critical assessment

- **Documented limitations.** README's security section explicitly enumerates risks of non-loopback deployment: unauthorized invocation, compliance/legal exposure, internet-scanner discoverability [HIGH]. Bash is disabled by default under `LocalSandboxProvider`; `AioSandboxProvider` is the official path to shell access [HIGH].
- **Documented version-1 → version-2 discontinuity.** README is explicit: "DeerFlow 2.0 is a ground-up rewrite. It shares no code with v1" [HIGH]. The 1.x branch remains maintained but is stated to be in wind-down. *Migration risk* for any team adopting 1.x patterns: those patterns do not transfer; 1.x architecture (Coordinator + tiered LLM workflow described in some third-party docs) is *not* the current architecture and should not be cited as such.
- **Stability risk.** Third-party guide notes Python requirement moved 3.11 → 3.12 since 2.0 launch and that "commands and configuration options will likely keep changing" [MODERATE — third-party blog, but consistent with weekly-progress-report cadence and high open-PR volume]. Pinning to a release tag rather than `main` is the rational adopter posture.
- **Inferred (SPECULATIVE) failure modes.** Sub-agent fan-out under tight concurrency caps (3) plausibly bottlenecks long-tail tasks; memory-fact extraction is LLM-driven and inherits LLM unreliability for retrieval correctness; nested middleware order is fixed and not declaratively configurable from `config.yaml`, which limits tunability without code changes.
- **Vendor-bias risk.** README explicitly recommends Doubao-Seed-2.0-Code (ByteDance) first; default LLM tuning may regress on non-Doubao providers. SPECULATIVE in scale, documented in fact.
- **Contested external claims.** Third-party blogs assert version-specific star/fork numbers (e.g., "39,000 stars and 4,600 forks" by VentureBeat, March 2026) that conflict with current ~65k figures; treat point-in-time third-party star counts as snapshots, not authoritative.

### Decision relevance

| Axis | Tag | Rationale |
|---|---|---|
| Control plane | PRIMARY | Lead-agent + middleware chain + sub-agent delegation define a complete control-plane reference. |
| Information substrate | PRIMARY | ThreadState + skills + soul + memory together form a fully worked information-substrate stack. |
| Action surface | PRIMARY | Pluggable sandbox + MCP + tool registry + messaging channels define an action surface across host, container, K8s, and external chat platforms. |
| Operational discipline | SECONDARY | Recursion/concurrency caps, debounced memory, regression tests, explicit security perimeter — present and disciplined, but not the source's headline contribution. |
| Deployment surface | SECONDARY | Local/Docker/K8s/embedded-library matrix is exemplary, but DeerFlow does *not* attempt to be deployment-surface-neutral the way pi-mono is — it ships an opinionated four-process topology. |

### Citation strength

HIGH — primary source (README, `backend/README.md`, `backend/CLAUDE.md`, `backend/packages/.../prompt.py`, `config.example.yaml`, GitHub org repo listing) verified within Session B. Cross-referenced third-party coverage (VentureBeat, DeepWiki) used only for corroboration on community signals and 2.0-launch chronology.

---

## §3.priority-2: earendil-works/pi (pi-mono)

### Identification

| Field | Value |
|---|---|
| Source name | pi (project name); pi-mono (monorepo handle still used in third-party docs) |
| Stratum tags | B (production harness), priority-tier |
| Maintainer / author | Mario Zechner (@badlogic, libGDX author) — currently published under the Earendil Works org [HIGH] |
| Primary URL (canonical) | https://github.com/earendil-works/pi |
| Secondary URLs | https://pi.dev/ (project site); https://pi.dev/news/2026/5/7/pi-has-a-new-home (org-migration announcement) |
| Redirect / historical URLs | `https://github.com/badlogic/pi-mono` → redirects to `earendil-works/pi`; npm scope `@mariozechner/*` → deprecated, points to `@earendil-works/*`; final release on old scope was 0.73.1, first release on new scope was 0.74.0 [HIGH] |
| License | MIT [HIGH] (org repo listing, package READMEs) |
| Last meaningful activity | Repo updated May 8, 2026; issues filed May 7–8, 2026; rapid CHANGELOG cadence [HIGH], observed May 8, 2026 |
| Star count | ~46.3k–46.4k stars [HIGH] (org repo listing 46,437; issues page 46k; discussions page 46.4k), observed May 8, 2026. Note: prompt-supplied figure of 45.9k is a slightly older snapshot from issue #2815 (Apr 4, 2026) and #2112 (Mar 13, 2026); current figure is higher. |
| Cross-reference to Session 3 profile | NONE (Session 3 omission) |

### Pattern source context

- **Discovery context.** Surfaced as a Session-3 omission because pi-mono's *unified LLM API* (`pi-ai`) is the most directly relevant open-source pattern to the harness's multi-LLM commitment, and because the layered package decomposition (foundation → core → applications) is a textbook example of the *composable substrate library* archetype — the inverse of DeerFlow's batteries-included framework-host.
- **Stated thesis.** Author's design essay (`mariozechner.at/posts/2025-11-30-pi-coding-agent`): "if I don't need it, it won't be built." Project README frames the offering as four composable pieces — call any LLM, wrap as agent loop, full coding-agent runtime, terminal UI library — usable independently or together.
- **Architectural altitude.** Substrate library + reference implementation. `pi-ai` and `pi-agent-core` are libraries (substrate); `pi-coding-agent`, `pi-tui`, `pi-web-ui` are reference implementations and reusable application-tier libraries.

### Profile (priority-tier supplement)

**Repository structure.** TypeScript monorepo using npm workspaces with lockstep versioning [HIGH]. Strict layered dependency graph: foundation packages have zero internal deps; core packages depend only on foundation; applications sit on top.

| Package | Role | Key responsibilities |
|---|---|---|
| `@earendil-works/pi-ai` | Foundation: unified LLM API | Multi-provider stream/complete; ten provider adapters (anthropic-messages, openai-completions, openai-responses, openai-codex-responses, azure-openai-responses, google-generative-ai, google-vertex, mistral-conversations, bedrock-converse-stream, plus `registerFauxProvider` for tests); cross-provider context handoff (Claude `<thinking>` ↔ OpenAI/Google equivalents); TypeBox-schema tool definitions; cost/token tracking; OAuth helpers under `@mariozechner/pi-ai/oauth` (now `@earendil-works/pi-ai/oauth`) [HIGH] |
| `@earendil-works/pi-agent-core` | Core: agent runtime | Agent loop (`while not done: stream → execute tools → feed results → loop`); state management; abort control; queued steering / follow-up messages with two delivery modes (one-at-a-time / all-at-once); attachment handling; transport abstraction (direct vs proxy); lifecycle events for monitoring; `StreamFn` middleware seam [HIGH] |
| `@earendil-works/pi-coding-agent` | Application: coding agent CLI | `pi` binary; four built-in tools (read, write, edit, bash); JSONL session persistence; context compaction; skills system; extensions (jiti-loaded TypeScript); prompt templates; themes; pi packages; four operational modes (interactive TUI / `--print` single-shot / RPC over stdin/stdout JSONL / programmatic SDK); `AgentSession`, `SessionManager`, `AuthStorage`, `ModelRegistry`, `createAgentSessionRuntime` SDK exports [HIGH] |
| `@earendil-works/pi-tui` | Application library: terminal UI | Differential rendering, three-strategy update; CSI 2026 synchronized output for atomic / flicker-free updates; bracketed paste mode; component library (Text, TruncatedText, Input, Editor, Markdown, Loader, SelectList, SettingsList, Image, Box, Container); inline image rendering for Kitty / iTerm2; autocomplete for paths and slash commands [HIGH] |
| `@earendil-works/pi-web-ui` | Application library: web UI | mini-lit web components + Tailwind v4; ChatPanel; sandboxed artifact execution (HTML/SVG/Markdown); JS REPL tool; document extraction (PDF/DOCX/XLSX/PPTX); IndexedDB-backed session/key/settings storage; CORS proxy handling; custom-provider support (Ollama / LM Studio / vLLM) [HIGH] |
| `@earendil-works/pi-pods` | CLI for vLLM GPU-pod management | Local + cloud inference deployment management (referenced in third-party catalog; not deeply profiled here per scope) [MODERATE] |
| Sister repos | Off-monorepo extensions | `earendil-works/pi-chat` (Slack/chat automation), `earendil-works/pi-review` (review extension, 205 stars, MIT), `earendil-works/pi-tutorial`, `earendil-works/gondolin` (experimental Linux microvm sandbox, Apache-2.0, 1.1k stars), `earendil-works/absurd` (durability experiment, Apache-2.0, 1.7k stars) [HIGH] |

**Architectural overview.** The agent loop in `pi-agent-core` is intentionally minimal (`packages/agent/src/agent-loop.ts`): no `max_steps` knob, no termination heuristics — the loop runs until the model produces a turn with no tool calls. The `Agent` class adds state management (mutable `model`, `thinkingLevel`, `tools`, `messages` fields), event subscription (`agent_start`, `turn_start`/`turn_end`, `message_start`/`update`/`end`, `agent_end`), abort, follow-up injection. The streaming layer is normalized: every provider's stream becomes a uniform event sequence (`start`, `text_start`/`delta`/`end`, `thinking_start`/`delta`/`end`, `toolcall_start`/`delta`/`end`, `done`, `error`) regardless of underlying API [HIGH].

State lives in three layers: (1) the `Context` object holds messages and serializes to plain JSON for portability; (2) `pi-coding-agent`'s `SessionManager` persists JSONL session files supporting branching (revisit any turn and fork) and compaction; (3) `AuthStorage` and `ModelRegistry` are per-process singletons with on-disk credential storage at `~/.pi/agent/auth.json` [HIGH]. RPC mode uses strict LF-delimited JSONL framing (the docs explicitly warn against generic line readers like Node `readline` because they split on Unicode separators inside JSON payloads) [HIGH].

The unified-LLM-API package is the most architecturally distinctive piece. Cross-provider context handoff is a stated first-class design goal: switching from Claude to GPT mid-session converts Anthropic `thinking` blocks to `<thinking>...</thinking>` content blocks and preserves signed reasoning blobs where required [HIGH]. The author acknowledges this is best-effort because thinking traces don't represent identical underlying behaviors across vendors.

**Distinguishing features.**

1. **Unified LLM API with cross-provider context handoff** (`pi-ai`). Switch model mid-conversation; `Context` serializes to JSON; replay across providers.
2. **Strict layered package graph.** Foundation (zero internal deps) → Core (depends on foundation only) → Applications. Documented in `AGENTS.md` and `docs/packages.md`. Peer-deps for bundled core packages (`@earendil-works/pi-ai`, `pi-agent-core`, `pi-coding-agent`, `pi-tui`, `typebox`) must use `*` range and *not* be bundled; non-core packages bundle [HIGH].
3. **`StreamFn` middleware seam.** `session.agent.streamFn` is a swappable function; the documented use case is wrapping `streamSimple` to inject OpenRouter attribution headers, enable Anthropic prompt caching, or add per-provider logging. Provides a first-class extension point for cross-cutting LLM-call concerns without touching the loop [HIGH].
4. **Four agent operational modes from one codebase.** Interactive TUI, `pi -p` print/single-shot, RPC over stdin/stdout JSONL (for non-Node integrations), and programmatic SDK — same `AgentSession` core, four delivery surfaces [HIGH] (`packages/coding-agent/README.md`).
5. **Public OSS session-data sharing as a project norm.** README directs users to publish coding-agent sessions to Hugging Face via `pi-share-hf`; author explicitly frames this as training-data source for coding agents over toy benchmarks. Operational signal for harness designers about evaluation datasets.
6. **Terminal UI primitive separately reusable.** `pi-tui` is positioned as a stand-alone library (CSI 2026 atomic updates, differential rendering) — independently consumable for any TUI agent.
7. **Skills + Extensions + Prompt Templates + Pi Packages convention.** Auto-discovery from conventional directories (`extensions/`, `skills/`, `prompts/`, `themes/`); `PI_CODING_AGENT_DIR` overrides root [HIGH].

**Community signals.** Single-author project with growing external contributor base — recent CHANGELOG entries credit external PRs (`@mitsuhiko`, `@pi0`, `@julien-c`, `@jsynowiec`, `@smithbm2316`) [HIGH]. Cloudflare engineer filed a feature request on Apr 27, 2026 asking for Workers AI / AI Gateway providers (issue #3850), an indicator of vendor-side attention. ~46.3k stars, ~5.5k forks, ~24 open issues, 3 open PRs as of May 8, 2026 [HIGH]. CHANGELOG cadence is multi-PR-per-week. The May 7, 2026 organizational migration from `badlogic/pi-mono` to `earendil-works/pi` was handled with a deprecated-but-published npm scope and a jiti-loader compat shim, an unusually disciplined OSS naming-rename. No commercial sponsorship disclosed in primary sources; the Earendil Works org was incorporated for the project per the project-site announcement.

**Documentation quality.** Per-package `README.md` is the canonical reference (`packages/ai/README.md`, `packages/agent/README.md`, `packages/coding-agent/README.md`, `packages/tui/README.md`, `packages/web-ui/README.md`). `AGENTS.md` at repo root encodes contribution rules including provider-addition checklist and per-file `git add` discipline ("never `git add -A`") [HIGH]. `docs/sdk.md`, `docs/packages.md`, `docs/providers.md`, `docs/keybindings.md` cover specific subsystems. *Well-documented:* provider extension surface (precise file-by-file walkthrough), session/branching/compaction model, RPC framing rules. *Under-documented:* internal `agent-loop.ts` state-machine semantics beyond the source code itself; long-running operational metrics; observability hooks beyond lifecycle events. The author's design-essay blog post is invaluable but external to the repo.

### Patterns extracted

1. **Unified multi-provider LLM API with normalized streaming events** (`pi-ai`). Per-provider streams flattened to a uniform `start / text_* / thinking_* / toolcall_* / done / error` event sequence; provider quirks (Cerebras lacks `store`, Mistral uses `max_tokens`, Google lacks tool-call streaming, Anthropic returns reasoning in `thinking` blocks) handled internally; one streaming handler works across all. *Axes:* PRIMARY information substrate, SECONDARY action surface. *Documented in:* `packages/ai/README.md`; design essay at `mariozechner.at/posts/2025-11-30-pi-coding-agent`.
2. **Cross-provider context handoff with serializable `Context`.** Sessions are JSON-serializable; switching models mid-conversation rewrites thinking traces into provider-agnostic tagged content blocks. Anthropic signed-reasoning blobs preserved for replay. *Axes:* PRIMARY information substrate. *Documented in:* `packages/ai/README.md`; primary use sample in design essay.
3. **Minimal agent loop with no max-steps knob** (`pi-agent-core`). Loop runs until model emits a turn with no tool calls; deliberately omits termination heuristics. Author's stated rationale: never found a use case for `max_steps`. *Axes:* PRIMARY control plane. *Documented in:* `packages/agent/src/agent-loop.ts`; design essay.
4. **`StreamFn` middleware seam for LLM calls.** Single function-level extension point for headers, caching, parameter mutation, logging. `session.agent.streamFn` is replaceable per-provider. *Axes:* PRIMARY operational discipline, SECONDARY information substrate. *Documented in:* nader.substack.com PI tutorial referenced from project README; SDK docs in `packages/coding-agent/docs/sdk.md`.
5. **Layered substrate package graph with peer-dep contract.** Foundation / Core / Applications strict layering enforced at install time via `peerDependencies` rules; bundled vs non-bundled packages explicitly distinguished. *Axes:* PRIMARY deployment surface, SECONDARY operational discipline. *Documented in:* `packages/coding-agent/docs/packages.md`; `AGENTS.md`.
6. **Four-mode delivery from one runtime: interactive TUI / single-shot CLI / RPC-over-stdio / programmatic SDK.** Same `AgentSession` core; mode is selected at process boundary. RPC framing is strict LF-delimited JSONL with explicit warnings against `readline`. *Axes:* PRIMARY action surface, SECONDARY deployment surface. *Documented in:* `packages/coding-agent/README.md` "Programmatic Usage" + RPC section.
7. **TypeBox tool schemas with serializable validation.** Tools defined as `{ name, description, parameters: TBoxSchema, execute(...) }`; TypeBox is re-exported from `pi-ai` so tool definitions travel with sessions across processes. *Axes:* PRIMARY action surface. *Documented in:* `packages/ai/README.md` Tools section.
8. **Session branching and JSONL session persistence with on-demand compaction.** Sessions stored as JSONL; any prior turn forkable to a new branch; compaction reduces context without losing history. *Axes:* PRIMARY information substrate, SECONDARY operational discipline. *Documented in:* `packages/coding-agent/README.md` Sessions/Branching/Compaction sections.
9. **Differential-rendering TUI primitive with CSI 2026 atomic frames** (`pi-tui`). Three-strategy diff renderer; bracketed paste mode for >10 line pastes; per-component theme contracts. *Axes:* SECONDARY action surface (HITL surface). *Documented in:* `packages/tui/README.md`.
10. **Zero-deps web-UI tier with sandboxed artifact execution and IndexedDB storage** (`pi-web-ui`). Mirrors the TUI's component model in mini-lit web components; sandbox executes HTML/SVG/Markdown artifacts; same `Agent` runtime. *Axes:* SECONDARY action surface. *Documented in:* `packages/web-ui/README.md`.
11. **Conventional-directory auto-discovery for extensions/skills/prompts/themes.** No manifest required for default layout; manifest is opt-in. `PI_CODING_AGENT_DIR` overrides root. *Axes:* SECONDARY operational discipline. *Documented in:* `packages/coding-agent/docs/packages.md`.

### V3 framing compatibility

| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | PASS | Default persona is "coding agent" but `pi-agent-core` and `pi-ai` ship with no persona at all; `pi-coding-agent` builds the persona via system prompt + skills, fully replaceable. |
| Stack-neutral | PARTIAL | TypeScript / Node lockstep across the monorepo. Cannot adopt as a Python harness without re-implementing. The *patterns* are stack-neutral; the *code* is not. |
| Deployment-surface-flexible | PASS | npm-installable library (any Node target), interactive TUI, CLI, RPC, web UI, programmatic embed. Has community Python port (williepaul/pi-mono-py) demonstrating port feasibility. |
| Multi-LLM | PASS | Strongest exemplar in the catalog. Ten API protocol adapters; cross-provider handoff a designed feature; custom-provider config via `~/.pi/agent/models.json` JSONC. |
| Production-grade discipline | PARTIAL | Strong: lockstep versioning, peer-dep contract, structured CHANGELOG, named-PR attribution, strict RPC framing, `AGENTS.md` git-add discipline. Weaker: limited built-in observability beyond lifecycle events; no first-class metrics/tracing surface; no native sandbox primitive (sister repo `gondolin` is the experimental answer). |

### Integration considerations

- **Substrate-vs-stack adoption decision.** Adopting `pi-ai` + `pi-agent-core` as the harness's multi-LLM and agent-loop substrate locks the harness into the Node/TypeScript runtime. Adopting only the *design patterns* (normalized stream events; serializable `Context`; `StreamFn` middleware seam; minimal loop; four-mode delivery) is stack-portable.
- **License is permissive (MIT).** No copyleft constraint.
- **Ownership / vendor risk.** Single-maintainer project that just migrated orgs (badlogic/pi-mono → earendil-works/pi). The migration was handled cleanly but is a recency signal for governance change. SPECULATIVE: if the project funding model changes, license could in principle be re-set on future versions; existing MIT code is irrevocable.
- **Subscription auth tension.** Issue #3372 (Apr 18, 2026) documents that Anthropic and Claude Pro/Max subscriptions billing changed under pi: third-party tool usage now draws from "extra usage" billed per-token, not from the plan limit [HIGH]. This is an Anthropic policy change, not a pi defect, but is a documented integration constraint.
- **Sandbox not built in.** Unlike DeerFlow, pi-mono does not ship a sandbox primitive. `bash` runs against the host. Sister repo `gondolin` is the experimental answer (Linux microvm with TypeScript control plane); Apache-2.0, 1.1k stars, separate maturity track.
- **Implementation effort.** Lifting the unified LLM API as a runtime dep is low-effort (`npm install`). Lifting as patterns into a Python harness is moderate-to-high effort: ten provider adapters, normalized streaming events, cross-provider handoff. The community port `williepaul/pi-mono-py` exists but is third-party with unknown maintenance level — treat as reference, not dependency.

### Critical assessment

- **Documented limitations.** Author's design essay states the loop has no `max_steps` knob and no plans to add one. For long-horizon tasks where runaway loops are a real concern, the harness must add this guard externally [HIGH]. RPC framing requires `\n`-only splitting; using `readline` corrupts JSON containing Unicode line/paragraph separators [HIGH] (`packages/coding-agent/README.md` RPC section).
- **Author-acknowledged best-effort behaviors.** Cross-provider context handoff is "best-effort"; thinking traces from different vendors do not represent equivalent computations [HIGH] (design essay). Token / cost tracking is "best-effort across all providers" [HIGH].
- **Documented vendor breakage.** Issue #3372 documents Claude Pro subscription auth no longer flowing through pi as it once did [HIGH]. Issue #2815 documents Antigravity provider deprecation [HIGH]. These reflect the inherent fragility of any third-party LLM aggregator.
- **Single-maintainer sustainability.** SPECULATIVE: bus factor is one (Mario Zechner). External contributor PRs are present but recurring core-architecture changes remain authored by the maintainer. The org-level migration to Earendil Works *may* indicate planned scaling (incorporation, hiring) but this is unconfirmed in primary sources.
- **No native observability.** SPECULATIVE: lifecycle events are sufficient for in-process logging but a production deployment will need to layer OpenTelemetry / Prometheus on top via the `StreamFn` seam and event subscriptions.
- **Third-party criticism.** A critical blog (`docs.bswen.com/blog/2026-03-15-opencode-vs-kilocode-vs-cline-comparison`) does not mention pi-mono directly; available primary criticism is limited to GitHub issues (largely vendor-side breakage) — *low signal*.

### Decision relevance

| Axis | Tag | Rationale |
|---|---|---|
| Control plane | SECONDARY | Minimal-loop pattern is a useful reference but pi-mono doesn't take strong positions on multi-agent orchestration, sub-agents, or planning — the loop is intentionally bare. |
| Information substrate | PRIMARY | Unified LLM API + serializable `Context` + cross-provider handoff + JSONL session + branching is the most relevant info-substrate exemplar in the catalog. |
| Action surface | SECONDARY | TypeBox tools, four built-in tools, MCP-extensible — present and disciplined but smaller than DeerFlow's surface (no native sandbox, no channel gateway). |
| Operational discipline | SECONDARY | Layered package graph, peer-dep contract, strict RPC framing, `AGENTS.md` rules, CHANGELOG attribution — strong governance, weaker observability. |
| Deployment surface | PRIMARY | Four delivery modes (TUI / `--print` / RPC / SDK) from one runtime + library-tier vs application-tier separation is the cleanest deployment-surface model among the three priority sources. |

### Citation strength

HIGH — primary sources verified across `README.md`, `AGENTS.md`, `packages/ai/README.md`, `packages/agent/README.md`, `packages/coding-agent/README.md`, `packages/tui/README.md`, `packages/web-ui/README.md`, `packages/coding-agent/docs/packages.md`, the org-migration announcement at `pi.dev/news/2026/5/7/pi-has-a-new-home`, and current GitHub repo metadata. Author's design essay used as primary for stated thesis. Third-party Substack/Medium content used only for corroboration on architectural details independently visible in primaries.

---

## §3.priority-3: Kilo-Org/kilocode

### Identification

| Field | Value |
|---|---|
| Source name | Kilo Code (VS Code extension + JetBrains + CLI); umbrella product line "Kilo" |
| Stratum tags | B (production harness), priority-tier |
| Maintainer / author | Kilo Code Inc. (Kilo-Org GitHub organization). Reportedly $8M seed-funded; commercial-OSS pattern [MODERATE — third-party comparative reviews] |
| Primary URL (canonical) | https://github.com/Kilo-Org/kilocode |
| Secondary URLs | https://kilo.ai/ (product site); https://kilo.ai/code (VS Code extension); https://kilo.ai/cli (CLI page); https://blog.kilo.ai/ (engineering blog); https://kilo.ai/docs/code-with-ai/platforms/cli (CLI docs); https://github.com/Kilo-Org/docs (docs repo); https://github.com/Kilo-Org/kilocode-legacy (preserved Apache-2.0 legacy codebase) |
| Redirect / historical URLs | `https://github.com/Kilo-Org/kilo` → redirects to `Kilo-Org/kilocode` (per the `Kilo-Org/kilo` repo description) [HIGH] |
| License | MIT (current `Kilo-Org/kilocode/LICENSE`) [HIGH]. *Important:* the *legacy* Kilo Code extension lived at `Kilo-Org/kilocode-legacy` under Apache 2.0 [HIGH] and pre-rebuild blog/PR records show MIT was preceded by Apache 2.0 with NOTICE attribution to Roo Code and Cline (PR #50, Mar 2025). The current `kilocode` repo is the *new* OpenCode-server-based codebase under MIT. |
| Last meaningful activity | Commit activity through Apr 30, 2026 (org listing). Multiple PRs landed in late April 2026 (e.g., #9961, #9989, #10004) [HIGH], observed May 8, 2026 |
| Star count | 19,000–19,033 [HIGH] (Kilo-Org org repo listing: 19k stars / 2.5k forks / 854 open issues / 250 open PRs / TypeScript), observed May 8, 2026 |
| Cross-reference to Session 3 profile | NONE (Session 3 omission) |

### Pattern source context

- **Discovery context.** Surfaced as a Session-3 omission because the Cline-lineage IDE-coding-agent harness is the dominant production form of "agent-as-IDE-extension," because kilocode self-claims #1 on OpenRouter (volume signal), and because kilocode underwent a documented ground-up rebuild that *changed lineage* mid-2026 — the current repo no longer derives from Cline/Roo but from OpenCode. This makes the kilocode-vs-Cline differentiation question simultaneously easier (the new code is structurally OpenCode) and harder (the *product* still inherits Cline/Roo-era affordances surfaced through the OpenCode core).
- **Stated thesis.** README + product site: "all-in-one agentic engineering platform" — VS Code, JetBrains, CLI, Cloud Agents, Slack, Code Reviewer, all clients of one CLI core. Engineering blog (`blog.kilo.ai/p/new-kilo-for-vs-code-is-live`): "the previous extension served over 2.2 million developers ... we built a portable core that runs natively on every surface."
- **Architectural altitude.** Harness (production, IDE-coding-agent specialization) + product platform. Distinct from DeerFlow (long-horizon research) and pi-mono (substrate library): kilocode is an opinionated multi-surface client-server harness optimized for in-IDE coding workflows.

### Profile (priority-tier supplement)

**Repository structure.** Bun-managed monorepo [HIGH] (`AGENTS.md`, `bun.lock`):

```
kilocode/
├── packages/
│   ├── opencode/              # @kilocode/cli — core engine: TUI, kilo run, kilo serve.
│   │                          #   Fork of upstream OpenCode (sst-dev). AI agent runtime,
│   │                          #   HTTP server, session management.
│   ├── kilo-vscode/           # kilo-code — VS Code extension. Bundles CLI binary,
│   │                          #   spawns `kilo serve` as child process. SolidJS webview.
│   │                          #   Includes Agent Manager (multi-session orchestration
│   │                          #   panel with git worktree isolation).
│   ├── desktop/               # @opencode-ai/desktop — Tauri v2 desktop app
│   ├── desktop-electron/      # @opencode-ai/desktop-electron — Electron alternative
│   ├── app/                   # @opencode-ai/app — shared SolidJS web UI
│   ├── ui/                    # @opencode-ai/ui — shared component library
│   ├── sdk/js/                # @kilocode/sdk — TS client SDK (OpenAPI-generated, v1+v2)
│   ├── plugin/                # @kilocode/plugin — plugin framework
│   ├── kilo-gateway/          # Kilo AI Gateway plugin (OpenAI-compatible 500+ model
│   │                          #   router with org-level rate limits and usage tracking)
│   ├── kilo-telemetry/        # Telemetry / observability
│   ├── kilo-i18n/             # Localization strings (zh, fr, ja, etc.)
│   └── kilo-utils/            # Shared utilities
├── sdks/vscode/               # VS Code-specific SDK glue
└── AGENTS.md                  # Upstream-merge discipline rules
```
[HIGH] (DeepWiki monorepo doc and `AGENTS.md`).

A shared `catalog:` mechanism in `bun.lock` pins common dependencies (solid-js, zod, hono, vite) to single versions across all packages [HIGH].

**Architectural overview.** Strict client-server architecture [HIGH]:

- **Backend (the brain).** `packages/opencode/` is a fork of upstream OpenCode and contains the full AI agent runtime, HTTP server, and session DB. Run as `kilo serve` — a child process spawned by every client.
- **Clients.** VS Code extension (`packages/kilo-vscode`), Tauri desktop, Electron desktop, JetBrains, web app, TUI (built into the CLI binary). Every client is a thin wrapper that manages CLI lifecycle and communicates via HTTP + Server-Sent Events through `@kilocode/sdk`.
- **Session model.** A `Session` (`packages/opencode/src/session/index.ts`) is the unit of work, persisted in a `SessionTable`. `SessionPrompt.prompt` (`packages/opencode/src/session/prompt.ts`) drives the agent loop: context assembly (system prompts + project rules + history) → LLM streaming via `Provider` abstraction → tool dispatch via `ToolRegistry`.
- **Provider layer.** Unified `Provider` interface (`packages/opencode/src/provider/provider.ts`) over Anthropic, OpenAI, Bedrock, etc., wrapping Vercel AI SDK with `ProviderTransform` (`packages/opencode/src/provider/transform.ts`) for Kilo-specific overrides. The `kilo-gateway` package routes through Kilo's hosted OpenAI-compatible gateway (500+ models, zero markup, organization rate limits) [HIGH].
- **Agent Manager.** Multi-session orchestration panel inside the VS Code extension. Spawns parallel agent sessions in *git worktrees* for isolation; uses `RuntimeProcessHandler` to fork agent-runtime processes [HIGH] (`packages/kilo-vscode/`; agent-safehouse third-party doc corroborated by current PR titles like #9970 "Agent Manager session tabs", #9989 "branch/mode/model selectors in worktree dialog", #9614 "start tasks in selected worktree").
- **Persistence & state.** Backend SQLite-style session DB; Memory Bank — `.kilocode/rules/memory-bank/` directory of Markdown files (`brief.md`, `architecture.md`, `dependencies.md`, etc.) checked into the repo, providing project-scoped persistent context across sessions [HIGH] (`kilo.ai/docs/advanced-usage/memory-bank`, GitHub discussion #2022).

**Distinguishing features (kilocode innovations vs. inherited Cline lineage).**

The crucial distinction: the *current* `Kilo-Org/kilocode` repo (post-rebuild, MIT) is *not* a Cline fork at the code level. It is an OpenCode fork. The legacy code that *was* a Cline/Roo fork is preserved at `Kilo-Org/kilocode-legacy` under Apache 2.0. Per `AGENTS.md`: "Kilo CLI is a fork of OpenCode" and "Everything is shared code from OpenCode, except folders that contain `kilo` in the name."

| Feature | Lineage | Notes |
|---|---|---|
| `kilo serve` HTTP+SSE backend | Inherited from OpenCode | Core architecture is upstream OpenCode |
| `Provider` abstraction over Vercel AI SDK | Inherited from OpenCode | Kilo extends with `ProviderTransform` |
| Custom Modes (Architect / Coder / Debugger / Ask / Orchestrator) | Inherited from Roo Code via legacy code, *re-implemented* in OpenCode-core | Modes themselves originated in Roo Code as a Cline fork; current kilocode re-implements over OpenCode |
| Plan / Act methodology | Inherited from Cline | Pre-rebuild |
| Kilo AI Gateway (`kilo-gateway`) | **Distinct kilocode innovation** | Unified OpenAI-compatible router for 500+ models, org-level rate limits, usage tracking, transparent provider rates |
| Memory Bank | **Distinct kilocode innovation** | `.kilocode/rules/memory-bank/*.md` repo-checked-in persistent project context. Initialized by Architect mode running "initialize memory bank" |
| Orchestrator Mode | **Distinct kilocode innovation** atop Roo Code's mode system | Routes complex tasks across Architect → Coder → Debugger sub-agents |
| Agent Manager with git worktree isolation | **Distinct kilocode innovation** | Parallel multi-session UI in VS Code extension; each session in its own git worktree |
| KiloClaw | **Distinct kilocode innovation** (separate product) | Hosted multi-tenant OpenClaw runner on Fly.io; chat backend migrated to `kilo-chat` per release #9764 |
| `check-kilocode-change` and `check-opencode-annotations.ts` upstream-merge guards | **Distinct kilocode innovation** | Per `AGENTS.md`, every Kilo-specific shared-file change is marked with `// kilocode_change` comments to keep upstream merges tractable. `packages/opencode/src/kilocode/` is the canonical Kilo-only directory; markers are not needed there. |
| Cross-platform (VS Code + JetBrains + CLI + Web + Desktop) sharing one engine | **Distinct kilocode innovation** | Cline is VS Code-only |
| Inline autocomplete | **Distinct kilocode innovation** atop Continue.dev-derived engine [MODERATE — agent-safehouse 2025 doc on legacy version; not yet re-verified for new architecture] | Cline does not ship inline autocomplete |
| MCP Server Marketplace | Inherited from Cline (and surfaced in current product) | |
| 500+ model coverage | **Distinct kilocode innovation** via `kilo-gateway` | |
| KiloClaw multi-conversation chat backend (release #9764) | **Distinct kilocode innovation** | Migrated April 2026 |
| OAuth for MCP servers | Inherited (legacy doc); current repo PR #8910 restored Sign-in for OAuth MCP servers in VS Code settings | |
| `.kilocode/skills/` and `~/.kilocode/skills/` | **Distinct kilocode innovation** atop generic skills concept | Project-level + global skill scoping |

**Community signals.** Commercial backing: Kilo Code Inc. with reported $8M seed funding [MODERATE — third-party reviews]. Self-reported metrics on the org page: "#1 on OpenRouter. 1.5M+ Kilo Coders. 25T+ tokens processed" [HIGH — primary self-claim, treat volume claims as marketing]. ~19k stars; 854 open issues; 250 open PRs; 2.5k forks [HIGH], observed May 8, 2026 — high activity with high backlog. PR cadence is multi-PR-per-day in late April 2026. Active upstream-merge process from OpenCode (`mergiraf` and `script/upstream/` referenced in `AGENTS.md`). External-facing engineering blog at `blog.kilo.ai`.

**Documentation quality.** *Well-documented:* monorepo structure (DeepWiki + `AGENTS.md`), upstream-merge discipline (`AGENTS.md` is exceptional), changelog detail (per-PR descriptions in `packages/kilo-vscode/CHANGELOG.md`), product-side docs at `kilo.ai/docs`, opencode-migration plan at `packages/kilo-vscode/docs/opencode-migration-plan.md`. *Under-documented in-tree:* the Memory Bank concept (canonical reference is `kilo.ai/docs/advanced-usage/memory-bank`, *not* the repo); detailed Mode-system semantics; how `kilo-gateway` performs routing; security model for Agent Manager worktrees beyond "git isolation". The canonical reference is split: `AGENTS.md` for monorepo internals, `kilo.ai/docs` for product behavior — adopters must consult both.

### Patterns extracted

1. **CLI-as-server with thin clients across IDE/desktop/terminal/web.** One `kilo serve` process per workspace; every UI surface (VS Code extension, JetBrains, Tauri/Electron desktop, CLI TUI, web app) is a client communicating over HTTP + SSE through `@kilocode/sdk`. Inverts the "agent inside IDE" model. *Axes:* PRIMARY deployment surface, SECONDARY action surface. *Documented in:* `AGENTS.md`; `blog.kilo.ai/p/new-kilo-for-vs-code-is-live`; DeepWiki "Multi-Interface Design".
2. **Kilo-specific code segregation + `// kilocode_change` markers + upstream-merge guards.** All Kilo-specific code in `packages/opencode/src/kilocode/` directory; shared-file modifications inline-marked with `// kilocode_change`; `script/check-kilocode-change` and `script/check-opencode-annotations.ts` are CI guards; `mergiraf` used for structural merge resolution. Pattern for sustaining a long-lived fork. *Axes:* PRIMARY operational discipline. *Documented in:* `AGENTS.md`.
3. **Agent Manager: parallel multi-session orchestration with git worktree isolation.** UI panel in VS Code extension; each session gets a dedicated git worktree as filesystem isolation; `RuntimeProcessHandler` forks agent-runtime processes per session; recovery metadata kept out of worktree git changes (PR #10004); branch/mode/model independent per session and persisted across restart (PR #9922). *Axes:* PRIMARY control plane, SECONDARY action surface. *Documented in:* `AGENTS.md`; `packages/kilo-vscode/CHANGELOG.md`; release notes.
4. **Mode system: per-task constrained agent personas with scoped tools and prompts.** Architect (read-only planning), Coder (implementation), Debugger (fixes), Ask (Q&A), Orchestrator (routing). Each mode has its own prompt, tool allowlist, and context policy. Custom modes definable per project; cloud-synced organization-managed modes also supported. *Axes:* PRIMARY control plane, SECONDARY information substrate. *Documented in:* product docs at `kilo.ai/`; mode definitions in `packages/opencode/src/`.
5. **Orchestrator Mode: hierarchical mode-routing for complex tasks.** Top-level instruction decomposed into subtasks; each subtask routed to the specialist mode (Architect → Coder → Debugger). *Axes:* PRIMARY control plane. *Documented in:* product site at `kilo.ai/code`; comparative third-party docs.
6. **Memory Bank: repo-checked-in Markdown project memory.** `.kilocode/rules/memory-bank/{brief,architecture,dependencies,...}.md` files initialized by Architect mode running "initialize memory bank"; loaded at session start with `[Memory Bank: Active]` indicator; updated via "update memory bank" command. Persistence is *the repository itself*. *Axes:* PRIMARY information substrate. *Documented in:* `kilo.ai/docs/advanced-usage/memory-bank`; GitHub discussion #2022.
7. **Unified OpenAI-compatible model gateway (`kilo-gateway`).** Routes 500+ models with transparent provider pricing, org-level rate limits, usage tracking. Backend hits gateway through standard `Provider` interface. *Axes:* PRIMARY information substrate, SECONDARY operational discipline. *Documented in:* `packages/kilo-gateway/`; product page `kilo.ai/`.
8. **Permission model with allow/deny command lists, `--auto` opt-out, parallel tool calls.** `allowedCommands` / `deniedCommands` config; Enter/Escape accept/deny prompts (PR #9991); command permission UX unified; `--auto` flag for headless CI/CD bypassing prompts. Recent shift to *parallel* tool calls (engineering blog: "files are read, terminal commands run, and searches execute concurrently"). *Axes:* PRIMARY operational discipline, SECONDARY action surface. *Documented in:* `kilo.ai/docs/code-with-ai/platforms/cli`; `blog.kilo.ai/p/new-kilo-for-vs-code-is-live`.
9. **OpenTelemetry-based observability with OTLP HTTP export.** Setting `OTEL_EXPORTER_OTLP_ENDPOINT` enables trace and log export; spans include `http.method`, `http.path`, `session.id`, `message.id`, and `opencode.*` internal attributes. *Axes:* PRIMARY operational discipline. *Documented in:* `kilo.ai/docs/code-with-ai/platforms/cli` "Telemetry" section.
10. **Bundled snapshots / Changes panel as session-level diff state.** Workspace and per-session diffs unified in a single panel with source dropdown (PR #9897). Sidebar changes badge shows session-level additions/deletions. Repository-level snapshot disable warning surfaced in panel. *Axes:* SECONDARY operational discipline. *Documented in:* `packages/kilo-vscode/CHANGELOG.md`.
11. **CA-trust + corporate-proxy compatibility.** `NODE_USE_SYSTEM_CA=1` defaulted on the spawned CLI; `kilo-code.new.extraCaCerts` setting accepts PEM file path; `http.proxyStrictSSL=false` honored as opt-out (PR #9881). Production-readiness pattern for enterprise environments. *Axes:* PRIMARY operational discipline. *Documented in:* release notes.

### V3 framing compatibility

| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | FAIL | Strongly biased toward IDE-coding-agent persona (Architect/Coder/Debugger). Modes are user-extensible but the default ontology is coding-task-shaped. |
| Stack-neutral | FAIL | TypeScript / Node / Bun monorepo; SolidJS webviews; OpenCode fork relationship. Cannot lift the harness whole into a non-Node stack. |
| Deployment-surface-flexible | PASS | Strongest among the three. CLI-server core supports VS Code, JetBrains, Tauri, Electron, terminal TUI, web — all on one engine. |
| Multi-LLM | PASS | `kilo-gateway` routes 500+ models; `Provider` abstraction over Vercel AI SDK supports BYOK across major vendors; OAuth for MCP. |
| Production-grade discipline | PASS | OpenTelemetry, CA-trust handling, permission allow/deny lists, kilocode_change marker discipline, parallel tool calls, `--auto` for CI/CD, structured per-PR changelog. |

### Integration considerations

- **Lineage interpretation matters.** Citing kilocode patterns as "Cline-derived" is wrong for the *current* MIT codebase; cite OpenCode-derived for the engine layer and Cline/Roo-lineage only for the *legacy* `kilocode-legacy` repo or for *concept* lineage of features like Plan/Act and modes.
- **License is permissive (MIT).** No copyleft constraint on the current repo. The legacy repo is Apache 2.0 — adopters must distinguish if porting old code.
- **OpenCode upstream coupling.** Per `AGENTS.md`: "We regularly merge upstream changes from opencode." Adopting kilocode-specific patterns risks tracking *two* upstreams (OpenCode + kilocode). Patterns extractable cleanly: Memory Bank, Agent Manager + git-worktree isolation, kilocode_change marker discipline, kilo-gateway routing model.
- **Framing tension.** kilocode is a *product* with cloud services (Kilo Auto, KiloClaw, Cloud Agents, Slack, Code Reviewer); the open-source MIT repo is the engine + extension code, but the *paid services* (`kilo-gateway` routing through `app.kilo.ai`, KiloClaw on Fly.io) are not in-scope for self-hosting from this repo. Self-hosting requires bringing your own gateway or BYO API keys.
- **Implementation effort.** Lifting CLI-as-server pattern is high effort but well-documented. Lifting Memory Bank is low effort (it is a directory convention + initialization prompt). Lifting kilocode_change marker discipline is essentially zero effort (a documentation choice). Lifting Mode system is moderate (prompt/tool/policy authoring per mode).

### Critical assessment

- **Documented quality concerns about *legacy* kilocode.** Third-party (`docs.bswen.com/blog/2026-03-15-opencode-vs-kilocode-vs-cline-comparison`, March 2026) reports KiloCode (legacy) suffered "context bloat" and "tool call failures that cascaded into hallucinated solutions" relative to OpenCode and Cline [MODERATE — single third-party blog, not corroborated; written *before* or during the OpenCode-rebuild migration, so its characterization may be obsolete]. The blog explicitly recommends OpenCode over KiloCode. Since the *current* kilocode is now built on OpenCode-server core, this critique partly addresses itself; the new architecture inherits OpenCode's reliability characteristics.
- **Documented user dissatisfaction with the rebuild rollout.** Comments on the engineering blog note v7 prompt-comprehension regressions vs v5 [HIGH — primary blog comment thread]. SPECULATIVE: a major rewrite at this scale typically has a regression tail that resolves over a few releases.
- **Sandboxing posture.** Per agent-safehouse third-party report (analyzing the *legacy* extension at commit `7dace4a` from 2025-07-01): "No built-in sandboxing. The extension runs with the full privileges of the VS Code extension host process. Command approval — `allowedCommands` and `deniedCommands` lists" [MODERATE — third-party but specific to the now-deprecated codebase]. The current OpenCode-based code adds Agent Manager git-worktree isolation but the underlying VS Code extension host privilege model is structurally unchanged.
- **High open-issue volume.** 854 open issues / 250 open PRs is a triage backlog signal. Combined with multi-PR-per-day cadence, indicates high velocity with non-trivial unresolved-defect inventory. SPECULATIVE on stability impact.
- **Self-claimed superlatives.** "#1 on OpenRouter", "1.5M+ Kilo Coders", "25T+ tokens processed" are self-reported and prominently used in marketing copy. Volume signal real but specific numerical claims should be treated as marketing, not audited metrics.
- **Vendor-lock concern on paid path.** `kilo-gateway` routing via `app.kilo.ai` is the convenient path; full self-hosting requires direct provider keys.
- **Repository naming history is messy.** `Kilo-Org/kilo` (redirects), `Kilo-Org/kilocode` (current), `Kilo-Org/kilocode-legacy` (preserved Apache 2.0 pre-rebuild), and the npm package name shifts (`@kilocode/cli`, `@kilocode/kilo`). Adopters must trace which artifact corresponds to which architecture generation.

### Decision relevance

| Axis | Tag | Rationale |
|---|---|---|
| Control plane | PRIMARY | Mode system + Orchestrator + Agent Manager with worktree isolation are the most relevant control-plane patterns for an IDE-style harness in the catalog. |
| Information substrate | SECONDARY | Memory Bank is a strong info-substrate exemplar (repo-as-memory) but kilocode is less ambitious than DeerFlow on long-term memory; provider abstraction is competent but pi-mono's is more architecturally distinctive. |
| Action surface | SECONDARY | MCP, terminal, file edit/diff, browser, agent-manager parallel sessions — comprehensive but partially inherited from OpenCode upstream. Native sandbox is git-worktree level, not container/microvm. |
| Operational discipline | PRIMARY | OpenTelemetry export, CA-trust handling, allow/deny permission lists, `--auto` for CI/CD, kilocode_change marker discipline, snapshot/diff state model, parallel-tool-calls execution model — most production-disciplined among the three. |
| Deployment surface | PRIMARY | CLI-as-server with VS Code / JetBrains / desktop (Tauri+Electron) / terminal TUI / web clients on one engine — strongest deployment-surface model in the catalog at the IDE-tier. |

### Citation strength

HIGH for primary repo content (`AGENTS.md`, `LICENSE`, `packages/kilo-vscode/CHANGELOG.md`, `packages/kilo-vscode/docs/opencode-migration-plan.md`, org repo metadata, blog.kilo.ai engineering posts). MODERATE for product-side feature descriptions sourced from `kilo.ai/`. MODERATE for legacy-architecture sandbox/security analysis (agent-safehouse, July 2025 commit) — primary-source-derived but for a now-superseded codebase. MODERATE for third-party comparative reviews; vendor-marketing claims (1.5M users, 25T tokens, #1 on OpenRouter) flagged as self-reported.

---
# §3.standard — Stratum B standard production harnesses

The eight entries that follow constitute the Stratum B "standard" production-harness layer of the Pattern Reference Catalog. All eight share three properties: (1) significant adoption signal (≥8K stars or institutional backing), (2) production-grade discipline (sandboxing, observability, permissioning, or governance present rather than aspirational), and (3) directly competing or composable architectural positions on at least one of the five harness axes. Entries §3.B1–§3.B4 are cross-referenced from Session 3 profiles; the schema here captures the pattern-extraction layer only and does not duplicate Session 3 prose. Entries §3.B5–§3.B8 are fresh research and document primary-source engagement (README, LICENSE, CHANGELOG, release tags). License terms for Dify (§3.B7) were verified by direct read of the LICENSE file and are NOT vanilla Apache 2.0. URL redirects are flagged in Identification blocks where applicable.

---

## §3.B1: OpenHands/OpenHands

### Identification
- **Source name:** OpenHands (formerly OpenDevin)
- **Stratum tag:** B (production harness)
- **Maintainer:** OpenHands GitHub org (formerly All-Hands-AI); core team Xingyao Wang, Robert Brennan, Graham Neubig
- **Primary URL:** https://github.com/OpenHands/OpenHands
- **Secondary URLs:** https://www.openhands.dev/; https://docs.openhands.dev/; https://github.com/OpenHands/software-agent-sdk
- **Redirect/historical URLs:** github.com/All-Hands-AI/OpenHands → github.com/OpenHands/OpenHands (org rename 20 Oct 2025, GitHub auto-redirects); ghcr.io/all-hands-ai/* still live but ghcr.io/openhands/* is canonical [HIGH, OpenHands/docs issue #36, All-Hands-AI/OpenHands issue #11376]
- **License:** MIT for core `openhands` and `agent-server` Docker images; `enterprise/` directory under separate source-available enterprise license [HIGH, README §License]
- **Last meaningful activity:** Active; Software Agent SDK paper arXiv:2511.03690 published late 2025; ongoing commits as of May 2026 [MODERATE]
- **Star count:** Not re-fetched this session; Session 3 has count
- **Cross-reference to Session 3:** §B3

### Pattern source context
- **Discovery context:** Highest-profile open-source SWE-bench-competitive harness; canonical reference for sandboxed CodeAct loop.
- **Stated thesis:** Open replica of autonomous SWE agents; SDK-first composability separating agent logic from execution environment from interface layer [HIGH, README §SDK].
- **Architectural altitude:** Reference implementation + composable harness SDK. Not a methodology — a runnable production system.

### Patterns extracted
1. **Three-layer composable SDK** (Agent / Agent Server / Interface). Agent logic, sandboxed execution environment, and interface (CLI / GUI / REST) are independently replaceable modules. Agents can target the local machine OR ephemeral Docker/Kubernetes workspaces via the Agent Server. Axes: **Action surface (PRIMARY)**, **Deployment surface (PRIMARY)**, Control plane (SECONDARY). Documented: README §Architecture; Session 3 §B3.
2. **CodeAct execution loop with auditable sandbox.** Single-agent ReAct-derived loop where actions are code/shell/file-edit operations executed inside a Docker runtime image (`docker.all-hands.dev/all-hands-ai/runtime`); host filesystem mounted explicitly. Axes: **Action surface (PRIMARY)**, **Operational discipline (PRIMARY — sandbox isolation)**. Documented: Session 3 §B3.
3. **Single-tenant local-first deployment posture.** README explicitly states OpenHands is meant to be run by a single user on a local workstation; multi-tenant requires separate enterprise licensing. Axes: **Deployment surface (PRIMARY)**. Documented: README §Running; Session 3 §B3.
4. **LiteLLM-backed multi-LLM provider matrix.** Provider matrix verified against SWE-bench (Anthropic, OpenAI, Moonshot/Kimi, Devstral, OpenHands LM, OpenRouter). Axes: **Information substrate (SECONDARY)**, Action surface (TANGENTIAL). Documented: docs.openhands.dev/openhands/usage/llms/llms; Session 3 §B3.

### V3 framing compatibility
| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | PASS | No fixed persona; agents defined per-deployment. |
| Stack-neutral | PARTIAL | Python-only SDK; Docker hard dependency for sandbox. |
| Deployment-surface-flexible | PASS | Local Docker, remote Agent Server, K8s all supported. |
| Multi-LLM | PASS | LiteLLM substrate. |
| Production-grade discipline | PASS | Sandbox, audit, hardened Docker guide. |

### Integration considerations
- SDK is Python; TypeScript clients must use REST API. Docker requirement raises friction for pure local-Node deployments. MIT license on core is permissive; enterprise/ directory must be excluded if forking.
- The Agent Server pattern (separate process for sandboxed execution) is directly portable as a reference for our action-surface design.

### Critical assessment
- **Documented:** Single-tenant assumption; not appropriate for multi-tenant deployments [HIGH, README]. Dependency on heavy Docker images (>1GB) [MODERATE, hardened install guide].
- **SPECULATIVE:** Cost discipline at scale — README warns LLMs cost money but no built-in spend cap is documented at SDK level (CLI may differ).

### Decision relevance
- Control plane: SECONDARY (single-agent loop is reference, not novel)
- Information substrate: SECONDARY (LiteLLM + workspace state)
- Action surface: **PRIMARY** (sandbox separation is canonical pattern)
- Operational discipline: **PRIMARY** (Docker isolation, hardened deployment guide)
- Deployment surface: **PRIMARY** (local-first explicitly, with cloud/VPC paths)

### Citation strength
HIGH — primary-source verification this session (README §License, §SDK, §Running), Session 3 profile, OpenHands docs.

---

## §3.B2: cline/cline

### Identification
- **Source name:** Cline (formerly "Claude Dev"; VS Code extension ID `saoudrizwan.claude-dev` retained)
- **Stratum tag:** B
- **Maintainer:** Cline Bot Inc. (founder Saoud Rizwan)
- **Primary URL:** https://github.com/cline/cline
- **Secondary URLs:** https://cline.bot/; https://docs.cline.bot/; https://github.com/cline/sdk
- **Redirect/historical URLs:** None at repo level; product rebrand "Claude Dev" → "Cline" preserved extension ID for backwards compatibility [MODERATE, deployhq.com guide].
- **License:** Apache 2.0 [HIGH, README footer]
- **Last meaningful activity:** Highly active; default branch updated 8 May 2026 [HIGH, github.com/cline org listing]
- **Star count:** 61,523 (observed 8 May 2026) [HIGH, github.com/cline org listing]
- **Cross-reference to Session 3:** §B2

### Pattern source context
- **Discovery context:** Largest-install agentic-coding harness in the IDE-extension form factor (5M+ installs claimed; 61.5K stars).
- **Stated thesis:** Autonomous coding agent inside the editor with permission-gated every-step approval [HIGH, README §Header].
- **Architectural altitude:** Reference implementation (VS Code extension primary target; expanding to JetBrains, CLI, SDK).

### Patterns extracted
1. **Plan / Act mode duality with separable model configurations.** Mode is persisted in `StateManager` ("plan" | "act"); Plan mode is read-only (no file writes, no commands); Act mode executes. `planActSeparateModelsSetting` allows binding a stronger reasoning model to Plan and a faster/cheaper model to Act. Axes: **Control plane (PRIMARY)**, **Information substrate (SECONDARY)**. Documented: src/shared/storage/types.ts (Mode type), src/core/task/index.ts (mode → ApiHandler binding); Session 3 §B2.
2. **YOLO mode = self-managed autonomy escalation.** Setting that auto-approves all actions and auto-transitions Plan→Act when the agent decides it has sufficient context. Inverse of the default permission-gated workflow. Axes: **Operational discipline (PRIMARY)**, Control plane (SECONDARY). Documented: CHANGELOG (yolo mode introduction); Session 3 §B2.
3. **Checkpoints via shadow Git repository.** Auditable snapshot mechanism; rollback per step. Axes: **Operational discipline (PRIMARY)**. Documented: Session 3 §B2.
4. **Spend-cap UI as first-class operational discipline.** v3.78 (April 2026) shipped explicit "Spend Limit Reached" UI with per-day / per-month caps. Axes: **Operational discipline (PRIMARY)**. Documented: Session 3 §B2; cline CHANGELOG.
5. **30+ provider matrix; never bound to vendor.** OpenRouter, Anthropic, OpenAI, Gemini, Bedrock, Azure, Vertex, Cerebras, DeepSeek, Moonshot, Qwen, xAI, Mistral, Groq, Fireworks, Together, Baseten, SambaNova, Nebius, HF, Ollama, LM Studio. Axes: **Information substrate (PRIMARY)**. Documented: Session 3 §B2.

### V3 framing compatibility
| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | PASS | No fixed persona; rules-driven. |
| Stack-neutral | PARTIAL | TypeScript / VS Code Extension API binding. CLI preview decouples this. |
| Deployment-surface-flexible | PARTIAL | Primarily local IDE; CLI broadens; Cline Cloud is separate product. |
| Multi-LLM | PASS | 30+ providers. |
| Production-grade discipline | PASS | Checkpoints, spend caps, audit logs. |

### Integration considerations
- VS Code Extension API is the primary substrate; portability requires using the SDK or CLI surfaces.
- Apache 2.0 is permissive; clean precedent for forks (Roo Code).
- Plan/Act mode pattern is portable — it is a state-machine over the agent loop, not a VS Code-specific feature.

### Critical assessment
- **Documented:** Plan-mode bug where model accidentally writes files reported (cline issue #4848) [MODERATE]; mode-sync conflict across multiple windows reported. CLI is in beta as of May 2026 [HIGH, cline issue tracker labels].
- **SPECULATIVE:** Per anecdotal install/star ratio, satisfaction signal is mixed vs Roo Code fork.

### Decision relevance
- Control plane: **PRIMARY** (Plan/Act duality is a directly portable pattern)
- Information substrate: **PRIMARY** (per-mode model binding)
- Action surface: SECONDARY
- Operational discipline: **PRIMARY** (Checkpoints, spend caps)
- Deployment surface: SECONDARY (IDE-bound today)

### Citation strength
HIGH — primary-source verification (DeepWiki structural references, github.com/cline org, CHANGELOG); Session 3 profile.

---

## §3.B3: aaif-goose/goose

### Identification
- **Source name:** goose
- **Stratum tag:** B
- **Maintainer:** Agentic AI Foundation (AAIF) under the Linux Foundation; originally Block, Inc.
- **Primary URL (canonical):** https://github.com/aaif-goose/goose
- **Secondary URLs:** https://goose-docs.ai/; https://aaif.io/
- **Redirect/historical URLs:** github.com/block/goose → github.com/aaif-goose/goose (donation announced 9 Dec 2025; repo migration completed early April 2026); docs moved from previous Block-hosted site to goose-docs.ai [HIGH, goose-docs.ai blog 7 April 2026; Linux Foundation press release 9 Dec 2025]
- **License:** Open-source, commercial-friendly per AAIF terms; OSI-approved per AAIF criteria [MODERATE, block.xyz announcement]
- **Last meaningful activity:** Active; under AAIF governance with continuing Block contribution [HIGH, opensourcesecurity.io interview Feb 2026]
- **Star count:** Not re-fetched; Session 3 has count
- **Cross-reference to Session 3:** §B4–8

### Pattern source context
- **Discovery context:** Reference implementation of MCP at agent-harness scale; first major agent harness donated to a neutral foundation.
- **Stated thesis:** Local-first, extensible, MCP-native agent for any task (not just code) [HIGH, goose-docs.ai].
- **Architectural altitude:** Reference implementation + framework (Rust core; native desktop / CLI / API surfaces).

### Patterns extracted
1. **MCP-native extension model.** Tools and integrations are loaded as MCP servers, not as in-process plugins. Axes: **Action surface (PRIMARY)**. Documented: Session 3 §B4–8; reinforced by AAIF governance pairing goose with MCP.
2. **Rust-core, multi-surface delivery.** Single Rust core powers desktop app (macOS / Linux / Windows), CLI, and embeddable API. Axes: **Deployment surface (PRIMARY)**. Documented: aaif-goose/goose README §Surfaces.
3. **Provider-agnostic with subscription pass-through.** 15+ providers (Anthropic / OpenAI / Google / Ollama / OpenRouter / Azure / Bedrock); supports using existing Claude/ChatGPT/Gemini subscriptions via ACP. Axes: **Information substrate (PRIMARY)**. Documented: aaif-goose/goose README.
4. **Neutral-governance handoff pattern.** Project structure under AAIF prevents vendor capture; precedent for project-level governance in agentic-AI infra. Axes: **Operational discipline (SECONDARY — governance)**. Documented: aaif.io launch press; Session 3 §B4–8.

### V3 framing compatibility
| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | PASS | General-purpose, not coding-only. |
| Stack-neutral | PARTIAL | Rust core forces FFI for non-Rust embedding. |
| Deployment-surface-flexible | PASS | Desktop / CLI / API. |
| Multi-LLM | PASS | 15+ providers. |
| Production-grade discipline | PASS | LF governance, MCP standardization. |

### Integration considerations
- Rust binary distribution is operationally clean but harder to extend than Python/TS.
- AAIF governance is a positive signal for long-term neutrality but does not eliminate Block's de facto upstream control.
- MCP-native posture aligns with our action-surface direction; goose is a reference for MCP-host implementation patterns.

### Critical assessment
- **Documented:** Donation is recent; governance maturity unproven [HIGH, infoq.com Dec 2025 — community comments on premature foundation establishment].
- **SPECULATIVE:** Repo URL migration creates short-term link rot in third-party documentation.

### Decision relevance
- Control plane: SECONDARY
- Information substrate: SECONDARY
- Action surface: **PRIMARY** (MCP-native reference)
- Operational discipline: SECONDARY (governance pattern)
- Deployment surface: **PRIMARY** (multi-surface from one core)

### Citation strength
HIGH — primary-source confirmation of donation and URL migration (linuxfoundation.org press, goose-docs.ai blog, anthropic.com news, block.xyz/inside, techcrunch.com); Session 3 profile.

---

## §3.B4: RooCodeInc/Roo-Code

### Identification
- **Source name:** Roo Code (previously Roo Cline)
- **Stratum tag:** B
- **Maintainer:** Roo Code, Inc. (community team taking over from original Roo team's pivot to Roomote per repo announcement)
- **Primary URL:** https://github.com/RooCodeInc/Roo-Code
- **Secondary URLs:** https://roocode.com/; https://docs.roocode.com/; https://github.com/RooCodeInc/Roo-Code-Docs
- **Redirect/historical URLs:** Roo Cline → Roo Code rebrand; lineage from cline/cline (fork). No URL redirect at repo level.
- **License:** Apache 2.0 © Roo Code, Inc. [HIGH, README footer]
- **Last meaningful activity:** Active; recent additions noted (GPT-5.5 via OpenAI Codex provider, Claude Opus 4.7 on Vertex AI, checkpoint navigation controls) [HIGH, README §Recent]
- **Star count:** ~23.7K (observed in secondary source, not re-verified this session) [MODERATE, decisioncrafters.com]
- **Cross-reference to Session 3:** §B4–8

### Pattern source context
- **Discovery context:** Cline-lineage fork that diverged on multi-mode architecture and orchestration; community-validated alternate of the same control-plane substrate.
- **Stated thesis:** "A whole dev team of AI agents in your code editor" — multi-mode persona-as-agent within one extension [HIGH, README header].
- **Architectural altitude:** Reference implementation; pattern-extension over Cline's loop.

### Patterns extracted
1. **Multi-mode pattern (Architect / Code / Debug / Ask / Test / Orchestrator + Custom Modes).** Each mode has its own prompt, tool restrictions, and bound model configuration. Modes can hand off to each other. Axes: **Control plane (PRIMARY)**, **Information substrate (SECONDARY)**. Documented: README §Modes; docs.roocode.com; Session 3 §B4–8.
2. **Orchestrator mode = supervisor agent within a single-process harness.** Orchestrator coordinates delegated mode-tasks "for hours and delivering complex results." Pattern is currently sequential per discussion #2861. Axes: **Control plane (PRIMARY)**. Documented: README §Orchestrator; Session 3 §B4–8.
3. **Configurable autonomy slider (Manual approval ↔ Auto-Approve / "BRRR").** Same gating model as Cline but with explicit normalization to "trust roles" tied to modes. Axes: **Operational discipline (PRIMARY)**. Documented: docs.roocode.com.
4. **Per-mode model binding with cost-tier optimization.** Architect → reasoning model; Code → coding model; cost-tier matrix per mode. Axes: **Information substrate (PRIMARY)**. Documented: roocode.com homepage.
5. **Codebase indexing for semantic search.** Configurable integrated semantic search for large codebases. Axes: **Information substrate (SECONDARY)**, Action surface (SECONDARY). Documented: roocode.com.

### V3 framing compatibility
| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | FAIL | Modes ARE personas; pattern is persona-as-control-mechanism. Inverse of V3 framing. |
| Stack-neutral | PARTIAL | TypeScript / VS Code Extension; same constraints as Cline. |
| Deployment-surface-flexible | PARTIAL | IDE-bound. |
| Multi-LLM | PASS | OpenRouter, Anthropic, Glama, OpenAI, Gemini, Bedrock, Azure, Vertex, LM Studio, Ollama. |
| Production-grade discipline | PASS | Permission-gated, SOC 2 Type II per marketing. |

### Integration considerations
- The mode pattern is portable as a control-plane primitive (state-machine of role-bound configurations) **even if** we strip persona framing — modes can be relabeled as "task-class profiles" without semantic loss.
- Apache 2.0 lineage from Cline is clean; no copyleft issues.
- Sequential orchestrator is a documented limitation (Discussion #2861); our design should consider parallelism from the outset.

### Critical assessment
- **Documented:** Maintainership transition risk — original team going "all-in on Roomote"; community handoff in progress [HIGH, README announcement]. Multi-window mode-sync interference (issue #5605) [HIGH]. Sequential-only orchestration today (Discussion #2861) [HIGH].
- **SPECULATIVE:** SOC 2 Type II claim from marketing is unverified against an audit document.

### Decision relevance
- Control plane: **PRIMARY** (multi-mode pattern)
- Information substrate: **PRIMARY** (per-mode model binding)
- Action surface: SECONDARY
- Operational discipline: SECONDARY
- Deployment surface: TANGENTIAL (IDE-bound)

### Citation strength
HIGH — primary-source verification (RooCodeInc/Roo-Code README, roocode.com, docs.roocode.com, issue #5605, discussion #2861); Session 3 profile.

---

## §3.B5: HKUDS/OpenHarness

### Identification
- **Source name:** OpenHarness
- **Stratum tag:** B
- **Maintainer:** HKUDS (Data Intelligence Lab @ The University of Hong Kong)
- **Primary URL:** https://github.com/HKUDS/OpenHarness
- **Secondary URLs:** README.zh-CN.md (Chinese-localized README); https://pypi.org/project/openharness-ai/
- **Redirect/historical URLs:** None.
- **License:** MIT — see LICENSE [HIGH, README §License]
- **Last meaningful activity:** v0.1.7 released 18 Apr 2026 ("TUI Polish & Safer Install"); v0.1.6 10 Apr 2026 (Auto-Compaction); v0.1.5 8 Apr 2026 (MCP HTTP transport) [HIGH, github.com/HKUDS/OpenHarness/releases]
- **Star count:** 11.2K stars / 1.9K forks (observed via Releases page header this session); 12,179 stars per HKUDS org page (later snapshot) [HIGH/MODERATE — two snapshots within session, 11.2K → 12.2K consistent with rapid growth]
- **Cross-reference to Session 3:** NONE (fresh research)

### Pattern source context
- **Discovery context:** Chinese-ecosystem flagship harness with explicit "harness layer separate from model" thesis; rapid trajectory in early-to-mid-2026.
- **Stated thesis:** "The model is the agent. The code is the harness." OpenHarness delivers core lightweight agent infrastructure — tool-use, skills, memory, multi-agent coordination — separable from any specific model [HIGH, README header].
- **Architectural altitude:** Framework + reference implementation. `oh` is the core harness CLI; `ohmo` is a packaged personal agent built on it.

### Patterns extracted
1. **Harness-as-substrate thesis (model-agnostic infrastructure layer).** Explicit separation of "the model" (intelligence) from "the harness" (hands, eyes, memory, safety boundaries). Pattern operationalized by treating providers as `workflow + profile` pairs rather than raw protocol names. Axes: **Information substrate (PRIMARY)**, **Control plane (SECONDARY)**. Documented: README §What is a Harness; CHANGELOG (provider profile binding).
2. **Provider profile system with credential isolation per backend.** Built-in profiles for Anthropic / OpenAI / Copilot / Codex / Moonshot (Kimi) / GLM / MiniMax / Gemini / NVIDIA NIM / Ollama / OpenAI-compat gateways. Anthropic-compatible backends (Kimi, GLM, MiniMax) bind credentials per-profile rather than sharing a global key. Axes: **Information substrate (PRIMARY)**, Operational discipline (SECONDARY). Documented: README §Providers; CHANGELOG (Built-in minimax provider profile, Built-in gemini provider profile).
3. **Auto-Compaction for context preservation across sessions.** v0.1.6 introduced auto-compaction that "preserves task state and channel logs across context compression — agents can run multi-day sessions without manual compact/clear." Axes: **Information substrate (PRIMARY)**. Documented: CHANGELOG v0.1.6 (10 Apr 2026).
4. **Pluggable sandbox backend with Docker isolation.** `sandbox.backend = "docker"` for stronger execution isolation, configurable resource limits, network isolation, automatic image management. Axes: **Action surface (PRIMARY)**, **Operational discipline (PRIMARY)**. Documented: CHANGELOG (Docker sandbox backend).
5. **CLI-agent integration substrate (OpenClaw / nanobot / Cursor).** OpenHarness loads Markdown skills and Claude-style plugin layouts; positions itself as an integration hub for other CLI agents. Axes: **Action surface (SECONDARY)**, **Deployment surface (SECONDARY)**. Documented: README §Supports CLI agent integration.
6. **Dry-run pre-flight verdict (ready / warning / blocked).** `oh --dry-run` previews resolved runtime settings, auth state, skills, commands, tools, MCP servers; produces verdict with concrete next-step suggestions. Axes: **Operational discipline (PRIMARY)**. Documented: README §Dry-run; SHOWCASE.md.
7. **MCP HTTP transport with auto-reconnect.** v0.1.5 added MCP HTTP transport, auto-reconnect on disconnect, tool-only server compatibility. Axes: **Action surface (PRIMARY)**. Documented: CHANGELOG v0.1.5.
8. **Subprocess "teammate" workers for headless multi-agent.** v0.1.6 stabilized subprocess teammates running in headless worker mode; agent team creation. Axes: **Control plane (PRIMARY)**. Documented: CHANGELOG v0.1.6.

### V3 framing compatibility
| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | PASS | `ohmo` is persona-bearing; `oh` core is not. |
| Stack-neutral | PARTIAL | Python; React TUI; MCP integration broadens. |
| Deployment-surface-flexible | PASS | Local CLI, Docker sandbox, headless, chat-app gateway (Feishu/Slack/Telegram/Discord). |
| Multi-LLM | PASS | Provider profile system explicitly built for this. |
| Production-grade discipline | PASS | Sandbox, dry-run pre-flight, auto-compaction, MCP reconnection. |

### Integration considerations
- MIT license clean.
- v0.1.x velocity is high; API stability not yet guaranteed (no 1.0).
- Chinese-ecosystem positioning (Feishu integration, MiniMax/GLM/Kimi first-class profiles) is a positive signal for provider diversity but introduces dependencies on China-region API availability.
- The `provider = workflow + profile` abstraction is directly portable as a design pattern for our information substrate.

### Critical assessment
- **Documented:** Pre-1.0 versioning (v0.1.7 as of 18 Apr 2026); breaking changes likely [HIGH, semver convention + CHANGELOG cadence].
- **Documented:** Windows terminal compatibility issues and PowerShell `oh` alias collision (must use `openh`) [HIGH, README §Note].
- **SPECULATIVE:** "ohmo runs on your existing Claude Code or Codex subscription — no extra API key needed" implies subscription-tunneling that may violate provider TOS depending on provider.

### Decision relevance
- Control plane: **PRIMARY** (subprocess teammate workers, swarm polling)
- Information substrate: **PRIMARY** (provider profiles, auto-compaction)
- Action surface: **PRIMARY** (sandbox backends, MCP HTTP transport, skills)
- Operational discipline: **PRIMARY** (dry-run pre-flight, Docker isolation)
- Deployment surface: SECONDARY (local-first; chat-gateway extension)

### Citation strength
HIGH — primary-source verification (README, CHANGELOG, releases page, SHOWCASE.md, CONTRIBUTING.md all read this session).

---

## §3.B6: langchain-ai/deepagents

### Identification
- **Source name:** Deep Agents (deepagents)
- **Stratum tag:** B
- **Maintainer:** langchain-ai (LangChain, Inc.); internal maintainers Sydney Runkle, Vishnu Suresh, Hunter Lovell, John Kennedy, ccurme, Eugene Yurtsev, Mason Daugherty
- **Primary URL:** https://github.com/langchain-ai/deepagents
- **Secondary URLs (sister repos):** https://github.com/langchain-ai/deepagentsjs (TypeScript parity); https://github.com/langchain-ai/deep-agents-ui (UI); https://github.com/langchain-ai/openshell-deepagent (NVIDIA OpenShell sandbox example); docs at https://docs.langchain.com/oss/python/deepagents/overview; reference at https://reference.langchain.com/python/deepagents
- **Redirect/historical URLs:** github.com/langchain-ai/deepagents-quickstarts → moved into main repo `examples/`
- **License:** MIT [HIGH, langchain-ai org repo listing]
- **Last meaningful activity:** Default branch updated 6 May 2026 [HIGH, langchain-ai org listing]. Recent release introduced "harness profiles" — declarative override layer per model family.
- **Star count:** 31K stars / 5.3K forks (observed 6 May 2026) [HIGH, langchain-ai/repositories listing]
- **Cross-reference to Session 3:** NONE (fresh research)

### Pattern source context
- **Discovery context:** LangChain's first-party agent harness; canonical "deep agent" pattern explicitly inspired by Claude Code, Deep Research, and Manus.
- **Stated thesis:** A "batteries-included, general purpose agent harness" — same core tool-calling loop as other frameworks but with built-in tools (planning, filesystem, sub-agents) and middleware [HIGH, README §What is deepagents].
- **Architectural altitude:** Framework / harness layered on the LangGraph runtime. Not a runtime itself — `create_deep_agent` returns a compiled LangGraph graph.

### Patterns extracted
1. **Harness-on-runtime layering (deepagents → LangGraph).** Distinct architectural pattern: deepagents is a harness layer above LangGraph's durable-execution runtime. Streaming, persistence, checkpointing, human-in-the-loop come from LangGraph; planning/filesystem/subagents from deepagents middleware. Axes: **Control plane (PRIMARY)**, Information substrate (SECONDARY). Documented: docs.langchain.com/oss/python/deepagents/overview §"deepagents is a standalone library built on top of LangChain's core building blocks for agents. It uses the LangGraph runtime for durable execution".
2. **Modular middleware architecture (PlanningMiddleware / FilesystemMiddleware / SubAgentMiddleware / MemoryMiddleware).** Each capability is a separate middleware. `createDeepAgent` auto-attaches the default trio; users can compose middleware independently or build a bare `createAgent` and add only what they need. Axes: **Control plane (PRIMARY)**, **Information substrate (PRIMARY)**. Documented: src/deepagents/graph.py, npmjs.com/package/deepagents §Middleware.
3. **Pluggable filesystem backends (StateBackend / StoreBackend / Local / Sandboxes).** `CompositeBackend` lets routes dispatch to different storage (e.g., `/memories/` → durable Store; default → ephemeral State). Sandbox backends support Modal / Daytona / Deno; sandbox backends gate the `execute` shell tool. Axes: **Action surface (PRIMARY)**, **Information substrate (PRIMARY)**. Documented: src/deepagents/backends; docs.langchain.com filesystem guide.
4. **Subagent delegation for context isolation.** Subagents run as separate LangGraph subgraphs; supervisor delegates via the `task` tool; subagents have their own context windows. Async subagents can run on remote Agent Protocol servers. Axes: **Control plane (PRIMARY)**, **Information substrate (PRIMARY)**. Documented: SubAgentMiddleware reference; deepwiki docs.
5. **AGENTS.md memory loading middleware.** MemoryMiddleware loads agent memory/context from `AGENTS.md` files; aligns with the OpenAI-donated AGENTS.md AAIF standard. Axes: **Information substrate (PRIMARY)**. Documented: reference.langchain.com/python/deepagents §MemoryMiddleware.
6. **Harness profiles — declarative per-model override layer.** Most recent release added harness profiles: provider-specific system-prompt prefixes/suffixes, tool inclusion, naming, middleware selection, subagent config, skills. Anthropic and OpenAI built-ins ship by default. Released claim: 10–20 point lift on tau2-bench subset (GPT-5.3 Codex 33→53; Claude Opus 4.7 43→53). Third-party plugins register via `deepagents.provider_profiles` / `deepagents.harness_profiles` entry points. Axes: **Information substrate (PRIMARY)**, Control plane (SECONDARY). Documented: github.com/langchain-ai/deepagents/releases (latest); profiles documentation.
7. **Declarative permission rules for filesystem access + HITL approval gates.** Filesystem operations gated by access rules; sensitive operations gated by human-in-the-loop. Axes: **Operational discipline (PRIMARY)**. Documented: docs.langchain.com overview.
8. **Python + TypeScript parity (deepagents + deepagentsjs).** First-party JS port maintains API parity (`createDeepAgent` matches `create_deep_agent`). Axes: **Deployment surface (SECONDARY)**. Documented: github.com/langchain-ai/deepagentsjs README §"Looking for the Python package?".

### V3 framing compatibility
| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | PASS | Persona via `system_prompt` parameter; no persona forced. |
| Stack-neutral | PARTIAL | Bound to LangGraph runtime semantics; Python + TS but framework-coupled. |
| Deployment-surface-flexible | PASS | Local, sandbox (Modal/Daytona/Deno), LangGraph deployments. |
| Multi-LLM | PASS | Any tool-calling-capable LLM; harness profiles per family. |
| Production-grade discipline | PASS | LangGraph runtime, HITL, permissioning, LangSmith tracing. |

### Integration considerations
- **Hard runtime dependency on LangGraph.** Not a runtime-neutral library; if our project does NOT adopt LangGraph, we cannot use deepagents directly — but the pattern catalog (middleware, pluggable backends, harness profiles) is portable as design inspiration.
- MIT license; permissive.
- LangSmith tracing is opt-in; deepagents itself doesn't require it.
- Performance claims on tau2-bench (10–20 point lift) are vendor-published — INTEGRATION NOTE: treat as marketing-adjacent until independently reproduced.

### Critical assessment
- **Documented:** Default model is `claude-sonnet-4-5-20250929` — switching to non-Anthropic providers requires explicit `model=` configuration [HIGH, examples/deep_research README].
- **Documented:** LangGraph coupling means the harness inherits LangGraph's failure modes (graph compilation errors, state-schema merge conflicts) [HIGH, src/deepagents/graph.py]. 
- **SPECULATIVE:** harness-profiles benchmark lift is from a "curated tau2-bench subset" — selection bias possible.

### Decision relevance
- Control plane: **PRIMARY** (subagent delegation, middleware composition)
- Information substrate: **PRIMARY** (filesystem backends, memory middleware, harness profiles)
- Action surface: **PRIMARY** (filesystem tools, execute tool, MCP via langchain-mcp-adapters)
- Operational discipline: SECONDARY (HITL via LangGraph)
- Deployment surface: SECONDARY (sandbox backends; LangGraph deployments)

### Citation strength
HIGH — primary-source verification across README, releases page, docs.langchain.com, npmjs.com TS package, deepwiki API reference, deepagentsjs sister-repo README.

---

## §3.B7: langgenius/dify

### Identification
- **Source name:** Dify
- **Stratum tag:** B
- **Maintainer:** LangGenius, Inc. (founded by ex-Tencent Cloud DevOps team)
- **Primary URL:** https://github.com/langgenius/dify
- **Secondary URLs:** https://dify.ai/; https://docs.dify.ai/; https://github.com/langgenius/dify-plugin-daemon (Apache-2.0); https://github.com/langgenius/dify-official-plugins; https://github.com/langgenius/dify-sandbox; https://github.com/langgenius/dify-docs (CC BY 4.0)
- **Redirect/historical URLs:** None.
- **License:** **Dify Open Source License — a MODIFIED Apache License 2.0 with additional conditions.** NOT vanilla Apache 2.0. Verified by direct read of LICENSE file [HIGH, github.com/langgenius/dify/blob/main/LICENSE]. The two material restrictions:
  - **(a) Multi-tenant clause:** "you may not use the Dify source code to operate a multi-tenant environment" without explicit written authorization. A tenant = one workspace.
  - **(b) Frontend logo/copyright clause:** "you may not remove or modify the LOGO or copyright information in the Dify console or applications." Inapplicable to uses that do not involve the frontend (defined as `web/` directory or `web` Docker image).
  - Apart from these two conditions, all other rights/restrictions follow Apache 2.0.
  - Sister repos differ: `dify-plugin-daemon` is plain Apache 2.0; `dify-docs` is CC BY 4.0.
- **Last meaningful activity:** v1.14.0 released 29 Apr 2026 ("Collaboration" feature, Graphon 0.2.2 standalone packaging, large SQLAlchemy 2.0 migration) [HIGH, github.com/langgenius/dify/releases/tag/1.14.0; releasealert.dev]
- **Star count:** Star count badge on dify.ai homepage exceeds 100K; discussions page header showed "Star 140k" this session [MODERATE — dify.ai discussions header reading "Star 140k"]
- **Cross-reference to Session 3:** NONE (fresh research)

### Pattern source context
- **Discovery context:** Highest-star agentic-workflow platform; visual workflow + agent platform with substantial enterprise adoption signal.
- **Stated thesis:** "Production-ready platform for agentic workflow development" — combines AI workflow, RAG pipeline, agent capabilities, model management, observability features [HIGH, README header].
- **Architectural altitude:** Platform / framework. Visual canvas + plugin runtime + multi-tenant workspace abstraction. Not a library; a deployable application.

### Patterns extracted
1. **Visual workflow canvas with directly-runnable nodes.** Workflows on a visual canvas with Variable Inspect panel showing all variables across nodes; "step-by-step execution" runs individual nodes directly (Jupyter-cell analogy). Axes: **Control plane (PRIMARY)**, **Operational discipline (SECONDARY — debugging)**. Documented: dify.ai/blog/dify-1-5-0-real-time-workflow-debugging.
2. **Plugin daemon with three runtime modes.** `langgenius/dify-plugin-daemon` (Apache 2.0) manages plugin lifecycle in Local runtime (subprocess via STDIN/STDOUT), Debug runtime (TCP-based for plugin developers), Serverless runtime (AWS Lambda). All requests are HTTP-based from Dify API. Axes: **Action surface (PRIMARY)**, **Deployment surface (PRIMARY)**. Documented: dify-plugin-daemon README.
3. **Plugin-everything migration since v1.0.0 (Feb 2025).** Models and tools are plugins, not core; published to Dify Marketplace. Distinct from in-process tool registries. Axes: **Action surface (PRIMARY)**. Documented: dify-official-plugins README.
4. **Agent Strategies as plug-in reasoning logic.** "Customizable Agent Strategies are plug-in logic modules that dictate how the LLM thinks and uses tools" — Chain-of-Thought, Tree-of-Thought, Function-call, ReAct as composable strategies. Axes: **Control plane (PRIMARY)**. Documented: dify.ai/blog (Agent Node).
5. **Human Input node as first-class workflow primitive.** v1.13.0 added a Human Input node so workflows pause for human review and resume with approved/edited/rerouted decisions. Axes: **Operational discipline (PRIMARY — HITL)**. Documented: dify.ai/blog (v1.13.0 announcement).
6. **MCP-as-client integration.** Dify connects to any MCP server (filesystems, GitHub, Slack, databases, browsers) via Settings → Tool Providers → MCP. Axes: **Action surface (PRIMARY)**. Documented: dify-hosting.com 2026 update guide [MODERATE — secondary source; cross-confirmed by primary plugin docs].
7. **Sandbox code execution via dify-sandbox.** Lightweight code execution environment for multi-language code blocks. Axes: **Action surface (PRIMARY)**, **Operational discipline (PRIMARY)**. Documented: github.com/langgenius/dify-sandbox.
8. **Multi-provider observability integration (Opik / Langfuse / Arize Phoenix).** Three observability backends supported out of the box; not a single-vendor lock-in. Axes: **Operational discipline (PRIMARY)**. Documented: README §observability features.
9. **Tenant = workspace abstraction.** Native multi-workspace concept in the data model — but commercial multi-tenant deployment is license-restricted. Axes: **Deployment surface (PRIMARY)**. Documented: LICENSE §1(a) tenant definition.
10. **Supervisor-mode agent loop.** New Supervisor agent mode in 2026 coordinates multiple sub-agents for complex multi-step tasks. Axes: **Control plane (PRIMARY)**. Documented: dify-hosting.com 2026 updates [MODERATE — secondary; would need primary verification before architectural commitment].

### V3 framing compatibility
| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | PASS | Workflow nodes are configurable; no fixed persona. |
| Stack-neutral | PARTIAL | Python (api) + TypeScript (web); deployment requires PostgreSQL + Redis + vector DB + Docker Compose. |
| Deployment-surface-flexible | PARTIAL | Self-host OR Dify Cloud; multi-tenant restricted by license. |
| Multi-LLM | PASS | "Hundreds of proprietary / open-source LLMs from dozens of inference providers." |
| Production-grade discipline | PASS | Plugin sandbox, observability backends, HITL node, Grafana dashboard. |

### Integration considerations
- **License risk: PARTIAL FAIL for multi-tenant SaaS use cases.** If our harness goal includes any form of hosted multi-tenant deployment, a commercial Dify license is required. For single-tenant local-first use, the LICENSE is effectively Apache 2.0 minus logo-modification rights.
- **Frontend logo/copyright clause** affects re-skinned forks; fully avoidable by not using `web/` directory.
- Heavy operational footprint (Docker Compose, Postgres, Redis, vector DB) — not appropriate for the local-development design-time deployment target as a wholesale adoption; pattern extraction only.
- The plugin-daemon pattern (HTTP-uniform across Local / Debug / Serverless runtimes) is directly portable.

### Critical assessment
- **Documented:** Repository has accumulated **35,000+ issues** per task brief — confirmed velocity but signals issue-management strain [MODERATE — task-brief assertion not re-verified by exact issue count this session]. Recent v1.13.x patches show regression patterns: prompt message transformation regression, Knowledge Retrieval node failures, Weaviate v4 client breakage [HIGH, github.com/langgenius/dify/releases].
- **Documented:** Default similarity-threshold pitfall — without explicit threshold, Dify returns top-K regardless of relevance [HIGH, tech-insider.org tutorial].
- **SPECULATIVE:** "Founded by ex-Tencent Cloud DevOps" task-brief claim not re-verified by primary source this session.

### Decision relevance
- Control plane: **PRIMARY** (visual workflow, Agent Strategies, Supervisor mode, Human Input node)
- Information substrate: SECONDARY (RAG pipeline, knowledge filtering)
- Action surface: **PRIMARY** (plugin daemon three-runtime model, MCP-as-client, sandbox)
- Operational discipline: **PRIMARY** (multi-vendor observability, HITL node, sandbox)
- Deployment surface: **PRIMARY** (license-bounded; plugin daemon supports Local/Debug/Serverless explicitly)

### Citation strength
HIGH for license terms (LICENSE file read directly this session), v1.14.0 release facts, plugin-daemon architecture; MODERATE for star count snapshot and supervisor-mode primary docs.

---

## §3.B8: VoltAgent/voltagent

### Identification
- **Source name:** VoltAgent
- **Stratum tag:** B
- **Maintainer:** VoltAgent (founder Omer Aplak)
- **Primary URL:** https://github.com/VoltAgent/voltagent
- **Secondary URLs:** https://voltagent.dev/; https://console.voltagent.dev/ (VoltOps console); https://github.com/VoltAgent/ai-agent-examples; https://github.com/VoltAgent/ai-agent-platform
- **Redirect/historical URLs:** None.
- **License:** MIT — Copyright (c) 2026 VoltAgent [HIGH, sibling LICENSE files in VoltAgent org repos read this session]
- **Last meaningful activity:** Highly active; CHANGELOG shows steady cadence including MCP Docs Server integration, Node 18 drop, ES2022 target [HIGH, voltagent/CHANGELOG.md].
- **Star count:** 8,697 stars (observed in voltagent org repo list this session) [HIGH, github.com/voltagent org listing]
- **Cross-reference to Session 3:** NONE (fresh research)

### Pattern source context
- **Discovery context:** TypeScript-first agent framework with a deliberate split between OSS framework and commercial observability product.
- **Stated thesis:** "Open-Source TypeScript Framework — Memory, RAG, Guardrails, Tools, MCP, Voice, Workflow" + "VoltOps Console (Cloud / Self-Hosted) — Observability, Automation, Deployment, Evals, Guardrails, Prompts" [HIGH, voltagent.dev homepage; README header].
- **Architectural altitude:** Framework + companion commercial platform. Two-product architecture is itself the distinguishing pattern.

### Patterns extracted
1. **Supervisor / Sub-Agent + Workflow Engine dual-control-plane pattern.** Two distinct orchestration primitives co-exist:
   - **Supervisor / Sub-Agent runtime** for dynamic task routing among specialized agents.
   - **Workflow Engine** for declarative multi-step automations — "describe multi-step automations declaratively rather than stitching together custom control flow."
   The two are composable. Axes: **Control plane (PRIMARY — distinct dual primitives)**. Documented: README §Core Runtime / Workflow Engine / Supervisors & Sub-Agents.
2. **VoltOps observability split (OSS framework + paid console).** Framework (`@voltagent/core`) is MIT and free; **VoltOps Console** is the paid product (Core $50/mo, Pro $250/mo, Enterprise) for observability, automation, deployment, evals, guardrails, prompts. Self-hosted option available for Enterprise. Console exposes: detailed traces, agent dashboards, execution logs, memory inspection, prompt playground, one-click GitHub deployment, webhook/schedule/trigger automations. Axes: **Operational discipline (PRIMARY)**. Documented: voltagent.dev/pricing; README §VoltOps Console.
3. **OTLP-exporter observability pattern.** Traces forward to VoltOps OR DataDog OR Grafana OR any OpenTelemetry-compatible backend. Custom business-level metrics co-emit alongside LLM telemetry. Axes: **Operational discipline (PRIMARY)**. Documented: ai-agent-platform README §Observability.
4. **Zod-typed tools with lifecycle hooks and cancellation.** "Tool Registry & MCP: Ship Zod-typed tools with lifecycle hooks and cancellation, and connect to Model Context Protocol servers without extra glue." Type-safe tool contracts at runtime via Zod; lifecycle hooks for pre/post/cancel. Axes: **Action surface (PRIMARY)**. Documented: README §Tool Registry & MCP.
5. **Deployment-surface matrix with explicit per-environment guidance.** Documented support for: standalone Hono server (long-running, full persistence), Cloudflare Workers (edge, stateless), Netlify Functions, AWS Bedrock, Vercel AI SDK, Next.js, Nuxt. Per-target guidance on memory backend, observability mode, scaling characteristics, limitations. Axes: **Deployment surface (PRIMARY)**. Documented: ai-agent-platform README §Deployment patterns.
6. **Memory layering: Working memory + Persistent memory + Semantic recall.** Working-memory adapter (in-process, session), persistent-storage adapter (Postgres/Supabase/Turso for durable history), semantic-recall layer for retrieval. Axes: **Information substrate (PRIMARY)**. Documented: README §Memory Systems; ai-agent-examples §with-postgres, with-supabase, with-turso.
7. **Vercel AI SDK provider-agnostic substrate.** 30+ providers via Vercel AI SDK (OpenAI, Anthropic, Google, Mistral, Groq, xAI, Bedrock, Vertex). Axes: **Information substrate (PRIMARY)**. Documented: ai-agent-examples §with-vercel-ai.
8. **MCP Docs Server for IDE integration.** Comprehensive MCP Docs Server gives IDE-resident AI assistants real-time access to VoltAgent documentation/examples/best-practices. Axes: **Action surface (SECONDARY)**, **Information substrate (SECONDARY)**. Documented: voltagent/CHANGELOG.md (MCP Docs Server entry).

### V3 framing compatibility
| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | PASS | Agents declared with typed roles; no forced persona. |
| Stack-neutral | FAIL | TypeScript-only; no Python parity. |
| Deployment-surface-flexible | PASS | Standalone, serverless, edge — per-target docs. |
| Multi-LLM | PASS | Vercel AI SDK substrate. |
| Production-grade discipline | PASS | OTLP, VoltOps, Zod-typed tools, lifecycle hooks. |

### Integration considerations
- **TypeScript-only** is a hard constraint vs our multi-LLM, multi-stack neutrality goal — the framework is not a candidate for direct adoption if Python coverage is required.
- VoltOps split: framework is MIT, but observability tooling cost is non-trivial at scale (Pro $250/mo). Self-hosting requires Enterprise license. Pattern is portable: **observability as a separable commercial layer above an OSS framework**.
- The dual-orchestration pattern (supervisor + workflow engine) is directly portable as a control-plane design.
- Vercel AI SDK dependency carries Vercel ecosystem alignment — a feature for Next.js stacks, friction otherwise.

### Critical assessment
- **Documented:** Zod version pinning required (3.24.2) due to TypeScript "Type instantiation is excessively deep" errors when packages use different patch versions [HIGH, voltagent/CHANGELOG.md issue #162]. Indicates framework brittleness around peer-dep version drift.
- **Documented:** Cloudflare Workers target has hard limits — no Node fs/child_process, ~1MB script size, strict CPU/memory caps [HIGH, ai-agent-platform README].
- **SPECULATIVE:** Star count of 8.7K is real but modest; production adoption signal lower than Cline/OpenHands/Dify; recent traction (3/2/2026 founding, per star-history.com on adjacent repo).

### Decision relevance
- Control plane: **PRIMARY** (Supervisor + Workflow dual primitives)
- Information substrate: **PRIMARY** (memory layering, Vercel AI SDK)
- Action surface: **PRIMARY** (Zod-typed tools, MCP integration)
- Operational discipline: **PRIMARY** (VoltOps split, OTLP exporters)
- Deployment surface: **PRIMARY** (per-target deployment matrix)

### Citation strength
HIGH — primary-source verification (README, voltagent.dev, voltagent.dev/pricing, CHANGELOG.md, ai-agent-platform README, ai-agent-examples README all read this session).

---

## Pattern density summary (Stratum B standard)

| Entry | Control plane | Information substrate | Action surface | Operational discipline | Deployment surface |
|---|---|---|---|---|---|
| §3.B1 OpenHands | SECONDARY | SECONDARY | **PRIMARY** | **PRIMARY** | **PRIMARY** |
| §3.B2 Cline | **PRIMARY** | **PRIMARY** | SECONDARY | **PRIMARY** | SECONDARY |
| §3.B3 goose | SECONDARY | SECONDARY | **PRIMARY** | SECONDARY | **PRIMARY** |
| §3.B4 Roo Code | **PRIMARY** | **PRIMARY** | SECONDARY | SECONDARY | TANGENTIAL |
| §3.B5 OpenHarness | **PRIMARY** | **PRIMARY** | **PRIMARY** | **PRIMARY** | SECONDARY |
| §3.B6 deepagents | **PRIMARY** | **PRIMARY** | **PRIMARY** | SECONDARY | SECONDARY |
| §3.B7 Dify | **PRIMARY** | SECONDARY | **PRIMARY** | **PRIMARY** | **PRIMARY** |
| §3.B8 VoltAgent | **PRIMARY** | **PRIMARY** | **PRIMARY** | **PRIMARY** | **PRIMARY** |

§3.B5 (OpenHarness) and §3.B8 (VoltAgent) carry PRIMARY weight on four or five axes and warrant the highest-priority deeper review in subsequent design sessions. §3.B1 (OpenHands) anchors action-surface and deployment-surface canonical patterns. §3.B7 (Dify) is the only entry with a non-vanilla license — it must be treated as **pattern source only**, not a direct dependency, for any deployment posture that includes multi-tenancy.

---
# §4 — Stratum C emerging harnesses

The eight entries in this section share three properties: (1) each is below the Session 3 ≥1 k-star priority threshold (sole exception: `can1357/oh-my-pi` at ≈3 k★ — included here because it is a fork of an already-cataloged Session B entry and is scoped to fork-distinct extensions only); (2) each is currently very active (commits or releases within days of the 8 May 2026 observation date); and (3) each contributes at least one architecturally distinctive pattern that does not appear, or appears only in weaker form, elsewhere in the catalog. Stratum C is the "emerging but pattern-rich" tier: weight is given to pattern distinctiveness rather than to popularity. Confidence tags ([HIGH] / [MODERATE] / [SPECULATIVE]) are applied at claim level. All star counts and activity signals are observed 8 May 2026 unless stated otherwise.

---

## §4.C1 — can1357/oh-my-pi

### Identification
- **Source name:** oh-my-pi (CLI binary `omp`)
- **Stratum tags:** C (emerging harness — included despite ≈3 k★ because pattern extraction is restricted to fork-distinct extensions)
- **Maintainer:** Can Bölük (`can1357`); fork of `badlogic/pi-mono` by Mario Zechner [HIGH — `README.md`: "omp is a fork of pi-mono by Mario Zechner, extended with a batteries-included coding workflow"]
- **Primary URL:** https://github.com/can1357/oh-my-pi
- **Secondary URLs:** npm scope `@oh-my-pi/*` (e.g. `@oh-my-pi/pi-coding-agent`, `@oh-my-pi/pi-natives`, `@oh-my-pi/pi-utils`, `@oh-my-pi/pi-ai`, `@oh-my-pi/pi-tui`); SourceForge mirror `oh-my-pi.mirror`
- **Redirect/historical URLs:** none observed in fork repository; upstream is `badlogic/pi-mono` (Session B)
- **License:** MIT [HIGH — `README.md` "MIT. See LICENSE."]
- **Last meaningful activity:** v13.15.x release series visible on the releases page; v13.14.0 changelog references active feature work; observed 8 May 2026 [HIGH — newreleases.io v13.14.0/v13.15.3 entries; SourceForge mirror v13.8.0 / v13.9.3 / v13.9.15 confirm a v13.x cadence] (Note: task brief specifies "v13.19.0 (5 Apr 2026)"; v13.19.0 not directly verified during this session; v13.14.0 / v13.15.3 confirmed [MODERATE] — exact tag claimed in brief is treated as MODERATE pending direct release-page confirmation.)
- **Star count:** ≈3 k★ (issue page header "Star 3k", March 2026) [HIGH — issue #413 page header]; brief cites 2.7 k.
- **Cross-reference to Session 3 profile:** NONE (Stratum C is below the Session 3 threshold; pi-mono base is a separate Session B entry — do not duplicate base patterns here).

### Pattern source context
- **Discovery context:** Listed as a Session B priority-tier ancestor (`pi-mono`) plus an actively divergent fork. Catalog inclusion reason: the fork has accumulated architecturally meaningful extensions (TTSR, hashline, isolation backends, native Rust addons) that are not present in pi-mono and have already been ported into other harnesses (e.g. oh-my-openagent ported TTSR — confirmed by the upstream commit `feat(ttsr): Port Time Traveling Streamed Rules from oh-my-pi`) [HIGH — github.com/code-yeongyu/oh-my-openagent/actions/runs/22888688607].
- **Stated thesis:** "AI Coding agent for the terminal — hash-anchored edits, optimized tool harness, LSP, Python, browser, subagents, and more" [HIGH — repo description].
- **Architectural altitude:** harness (full TUI/CLI agent runtime), with a documented SDK surface (`createAgentSession`, `SessionManager`, `ModelRegistry`, `discoverAuthStorage`) and an RPC mode for embedding from other languages [HIGH — `README.md` SDK section].

### Patterns extracted
*(scope-limited to extensions that distinguish oh-my-pi from pi-mono; pi-mono base patterns belong in the Session B entry, not here)*

1. **Hashline edit protocol**
   *Description:* Each line is tagged with a short content-hash anchor (format `LINE:HASH`, e.g. `5:ab|export function foo() {`). The model references anchors instead of reproducing line text; on file mutation, hash mismatch rejects the edit before corruption. The README reports a benchmark across "16 models, 180 tasks, 3 runs each" with Grok Code Fast 1 climbing from 6.7 % to 68.3 % task success and Grok 4 Fast emitting 61 % fewer output tokens [HIGH — `README.md` "Hashline" section]. Benchmark methodology details beyond those three figures are not surfaced in the README and should be treated as [MODERATE] until the harness benchmark file is read directly.
   *Axes:* action surface (PRIMARY); information substrate (SECONDARY — anchors are a context format).
   *Documented in:* `README.md` "Hashline" section; `packages/coding-agent/src/patch/hashline.ts`; DeepWiki "Hashline Edit Mode" page.

2. **Time-Traveling Streamed Rules (TTSR)**
   *Description:* Rules carry a `ttsrTrigger` regex; the harness watches the model's output stream, and when a trigger pattern matches it aborts the in-flight stream, injects the rule as a system reminder, and retries the request. Rules consume zero tokens until matched and fire once per session, preventing loops [HIGH — `README.md` "Time Traveling Streamed Rules" section; persistence to `session.jsonl` confirmed at `packages/coding-agent/CHANGELOG.md` lines 26–28 per DeepWiki].
   *Axes:* information substrate (PRIMARY); operational discipline (SECONDARY — behavioural guardrails).
   *Documented in:* `README.md`; `packages/coding-agent/src/...` rule discovery code; DeepWiki "TTSR" pages.

3. **Native Rust N-API performance layer**
   *Description:* "~7,500 lines of Rust compiled to a platform-tagged N-API addon" supplying regex search, glob/type filtering, fuzzy find, and other hot operations without shelling out. Supported targets: linux-x64, linux-arm64, darwin-x64, darwin-arm64, win32-x64 [HIGH — `README.md` "Native Performance Layer"].
   *Axes:* action surface (SECONDARY — tool execution acceleration); deployment surface (SECONDARY — platform-tagged binaries).
   *Documented in:* `README.md`; package `@oh-my-pi/pi-natives`; `DEVELOPMENT.md` references `Shell` from `@oh-my-pi/pi-natives`.

4. **Isolation backends with three-mode dispatch**
   *Description:* Tasks run with `isolated: true` resolve to one of `worktree`, `fuse-overlay` (Unix), or `fuse-projfs` (Windows ProjFS). When prerequisites are missing, fuse-overlay/projfs fall back to worktree with a system notification; non-prerequisite startup errors fail the task. Merge strategy is `task.isolation.merge` ∈ {`patch` (default), `branch`}; patch mode captures a delta via `captureDeltaPatch(...)` and applies with `git apply` [HIGH — `packages/coding-agent/DEVELOPMENT.md` task-isolation section].
   *Axes:* operational discipline (PRIMARY — runtime isolation across parallel agents); deployment surface (SECONDARY — Windows/Unix dispatch).
   *Documented in:* `packages/coding-agent/DEVELOPMENT.md`; `packages/coding-agent/src/task/worktree.ts`.

5. **Multi-credential round-robin / fallback chain**
   *Description:* Per-role fallback chains under `retry.fallbackChains.<role>` (e.g. `default`, `plan`); cooldown-expiry revert policy at `fallbackRevertPolicy: cooldown-expiry`; provider order via `modelProviderOrder`. Multiple API keys per provider with usage-aware selection are described in `docs/models.md` [HIGH — `README.md` settings excerpt; `docs/models.md`].
   *Axes:* control plane (PRIMARY — model routing); operational discipline (SECONDARY — degradation behaviour).
   *Documented in:* `README.md` settings example; `docs/models.md`; `src/config/model-registry.ts`, `src/config/model-resolver.ts`.

6. **11 LSP operations with workspace-wide diagnostics**
   *Description:* LSP tool surface includes format-on-write, immediate post-edit diagnostics, workspace-wide diagnostics, occurrence-based symbol disambiguation, and local LSP binary auto-resolution from `node_modules/.bin` and `.venv/bin`. The brief specifies "11 LSP operations" — the README enumerates a category list rather than naming a count of 11; treat the integer "11" as [MODERATE] pending a direct read of `src/lsp/`.
   *Axes:* action surface (PRIMARY).
   *Documented in:* `README.md` "LSP" section; `src/lsp/` (referenced in `DEVELOPMENT.md`).

7. **14 stealth-mode browser plugins**
   *Description:* The README enumerates Puppeteer-based browser tooling with 14 stealth scripts (toString tampering, WebGL fingerprinting, audio context, screen dimensions, font enumeration, plugin/mime-type mocking, hardware concurrency, codec availability, iframe detection, locale spoofing, worker detection, and others). User-agent spoofing strips `HeadlessChrome`; Client Hints brand lists are forged via CDP `Network` and `Emulation` domains. NixOS detection resolves system Chromium because Puppeteer's bundled binary cannot run on a non-FHS system [HIGH — `README.md` browser section].
   *Axes:* action surface (PRIMARY).
   *Documented in:* `README.md`; `src/tools/puppeteer/*.txt` (per `DEVELOPMENT.md`).

### V3 framing compatibility

| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | PASS | Framing is "AI coding agent for the terminal"; persona is not baked into core patterns. |
| Stack-neutral | PARTIAL | TS+Bun+Rust toolchain is non-trivially specific; native addons require platform tags. Patterns themselves (hashline, TTSR, isolation modes) are language-agnostic in concept but the reference implementation is not. |
| Deployment-surface-flexible | PASS | Local CLI, RPC mode, SDK embedding, and process-isolation paths are all documented [HIGH — `README.md` SDK + RPC sections]. |
| Multi-LLM | PASS | Provider registry + per-role fallback chains explicitly multi-vendor; Ollama / llama.cpp / LM Studio / vLLM local discovery in `docs/models.md`. |
| Production-grade discipline | PASS | Telemetry/log rotation under `~/.omp/logs/`, MCP auto-reconnect, isolated tasks, per-turn metrics callback, abort-controller plumbing [HIGH — `AGENTS.md`, `CHANGELOG.md`]. |

### Integration considerations
- **Dependencies:** Bun runtime (preferred) or prebuilt binary; Puppeteer (with stealth scripts) for browser tool; `fuse-overlayfs` (Linux) or ProjFS (Windows) for non-`worktree` isolation.
- **License constraints:** MIT — clean for derivative work and pattern adoption.
- **Framing tensions:** `omp` CLI surface assumes a TUI-first deployment; the SDK surface (`createAgentSession`, RPC mode) is the path that aligns with the V3 deployment-surface-flexible requirement.
- **Implementation effort:** Patterns 1–2 (hashline, TTSR) are mechanically reproducible from the documented file paths; pattern 4 (isolation backends) requires platform-specific code paths and is a multi-week effort to replicate faithfully; pattern 7 (stealth browser) is a maintained adversarial surface and incurs ongoing upkeep.

### Critical assessment
- **Documented:** Issue #413 (March 2026) reports that disabled imported skills remained discovered after v13.11.1 across both Codex and Claude-Code import paths despite a stated fix in v13.11.1; partial-fix status acknowledged by reporter [HIGH — github.com/can1357/oh-my-pi/issues/413].
- **Documented:** Hashline benchmark figures (6.7 → 68.3 % for Grok Code Fast 1) are self-published in the README; the benchmark harness, prompt set, and run-to-run variance are not exposed in the README excerpt [MODERATE — README claims; methodology unverified in this session].
- **Inferred:** Maintenance is single-author dominant (Can Bölük); fork drift relative to upstream `pi-mono` will widen as TTSR / hashline / isolation diverge [SPECULATIVE].
- **Scope discipline:** Patterns owned by upstream `pi-mono` (e.g. base session manager, prompt template, base tool registry, IPython kernel reuse) are NOT cataloged here — they belong in the Session B `pi-mono` entry.

### Decision relevance
- Control plane: SECONDARY (per-role fallback chains, subagent task graph)
- Information substrate: PRIMARY (TTSR, hashline anchors)
- Action surface: PRIMARY (hashline edits, native Rust ops, browser stealth)
- Operational discipline: PRIMARY (isolation backends, MCP reconnect, retry chains)
- Deployment surface: SECONDARY (RPC mode, process isolation, platform-tagged native addons)

### Citation strength
HIGH for patterns 1–5, 7 (verified against `README.md`, `DEVELOPMENT.md`, `docs/models.md`, and the issues page); MODERATE for pattern 6 (the integer "11" not directly confirmed in this session) and for the v13.19.0 release tag (newreleases.io confirmed v13.14.0 / v13.15.3 only).

---

## §4.C2 — jonwiggins/optio

### Identification
- **Source name:** Optio
- **Stratum tags:** C
- **Maintainer:** Jon Wiggins (`jonwiggins`)
- **Primary URL:** https://github.com/jonwiggins/optio
- **Secondary URLs:** https://optio.host/ (project site); HN announcement at news.ycombinator.com/item?id=47520220
- **Redirect/historical URLs:** none observed
- **License:** open-source MIT (per HN post and README differentiation block) [HIGH — README "Open source (MIT) — read the code, fork it, audit it"]
- **Last meaningful activity:** CI run sequence visible at `#849`–`#850` with PRs synchronized on observation date; CI #845+ with daily PRs from maintainer [HIGH — Workflow runs page]
- **Star count:** 922 ★ [HIGH — user-profile listing on `JonWiggins`'s GitHub]
- **Cross-reference to Session 3 profile:** NONE.

### Pattern source context
- **Discovery context:** Active K8s-native ticket→PR orchestrator; demonstrates a tiered-tasks topology not seen in other Stratum C entries.
- **Stated thesis:** "Self-hosted AI engineering platform — your cluster, your agents, your code" — a wedge defined as self-hosted, BYO-K8s, multi-vendor, MIT [HIGH — README differentiation block].
- **Architectural altitude:** harness/platform — Helm-deployable Kubernetes orchestrator with an HTTP control surface (`/api/tasks`, `/api/internal/persistent-agents/*`) and a UI dashboard.

### Patterns extracted

1. **Three-tier task model (Tasks / Jobs / Persistent Agents)**
   *Description:* All three tiers share triggers (manual / schedule / webhook / ticket), prompt templates, the reconciler, and the unified `/api/tasks` HTTP layer. Tasks land code via PRs; Jobs are reusable parameterized agent runs in empty pods (reports, triage, ops, DB queries) without repo checkout; Persistent Agents are long-lived named processes with a stable slug, an inbox, and a cyclic state machine [HIGH — README Tasks/Jobs/Agents section].
   *Axes:* control plane (PRIMARY — tiering is an orchestration topology); operational discipline (SECONDARY — shared reconciler, shared HTTP surface).
   *Documented in:* README "Three Task tiers" section; CI #841 PR title "docs: update for v0.4 — Tasks/Jobs/Reviews/Issues split + Persistent Agents tier".

2. **Inter-agent messaging via Persistent-Agents endpoints**
   *Description:* Persistent Agents address each other via `/api/internal/persistent-agents/*` for direct messages and broadcasts, enabling multi-agent teams (the "Forge demo" is the documented reference) [HIGH — README "Inter-agent messaging"].
   *Axes:* control plane (PRIMARY — explicit multi-agent topology); information substrate (SECONDARY — durable inbox/state).
   *Documented in:* README; `/api/internal/persistent-agents/*` endpoint family.

3. **Autonomous feedback loop with auto-resume on CI / merge conflict / review**
   *Description:* Optio "auto-resumes the agent on CI failures, merge conflicts, and review feedback; auto-merges when everything passes." Pipeline stages: Intake → Queued → Provisioning → Running → PR Opened → CI & Review → Merged. A reconciler drives the task forward across stages [HIGH — README + optio.host pipeline diagram].
   *Axes:* operational discipline (PRIMARY — CI feedback closure is the core reliability mechanism); control plane (SECONDARY — pipeline state machine).

4. **MCP-as-Connections, injected per repo / per agent**
   *Description:* "Configure a provider once, assign it to repos or agents, and Optio injects MCP servers into agent pods automatically." Built-in providers: Notion, GitHub, Slack, Linear, PostgreSQL, Sentry, Filesystem, plus custom MCP servers and HTTP APIs [HIGH — README Connections].
   *Axes:* action surface (PRIMARY); deployment surface (SECONDARY — pod-level injection).

5. **Per-repo isolation via long-lived pod with concurrent git worktrees**
   *Description:* "One long-lived Kubernetes pod per repo with git worktree isolation. Multiple tasks run concurrently in separate worktrees. Multi-pod scaling and idle cleanup built in" [HIGH — optio.host site].
   *Axes:* deployment surface (PRIMARY — K8s pod is the deployment primitive); operational discipline (SECONDARY — idle cleanup, scaling).

6. **Multi-vendor agent abstraction**
   *Description:* "Run Claude Code, OpenAI Codex, GitHub Copilot, Google Gemini, or OpenCode. Configure model, prompt template, and settings per repository. Launch review agents as subtasks with separate prompts" [HIGH — optio.host].
   *Axes:* control plane (PRIMARY — vendor swap is per-repo); information substrate (SECONDARY — per-repo prompt templates).

### V3 framing compatibility

| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | PASS | Engineering-platform framing without persona overlay. |
| Stack-neutral | PARTIAL | Hard dependency on Kubernetes; BYO Postgres/Redis is an external requirement. |
| Deployment-surface-flexible | FAIL | Deployment surface is fixed at Kubernetes (GKE/EKS/AKS or any conformant K8s); the local "Docker Desktop with Kubernetes enabled" path still requires K8s. The harness *we* are designing runs on developer-owned hardware; Optio's K8s assumption is a strong divergence. |
| Multi-LLM | PASS | Five named runtimes (Claude Code, Codex, Copilot, Gemini, OpenCode), per-repo selection. |
| Production-grade discipline | PASS | AES-256-GCM secret encryption at rest, OIDC/OAuth, K8s RBAC, audit-friendly task history, reconciliation controller [HIGH — README differentiation block]. |

### Integration considerations
- **Dependencies:** Kubernetes cluster, Postgres, Redis. The `setup-local.sh` path requires Docker Desktop with Kubernetes enabled.
- **License constraints:** MIT — clean.
- **Framing tensions:** Deployment-surface FAIL is the dominant tension. The *patterns* (three-tier task model, persistent-agents inbox, auto-resume reconciler) are extractable and re-implementable on a non-K8s deployment surface; the reference implementation is not portable.
- **Implementation effort:** Pattern adoption (tiered tasks + reconciler + persistent-agent inbox) is a meaningful effort but is not gated by Kubernetes.

### Critical assessment
- **Documented:** Project is self-described as competing in a "crowded" space (Devin, Charlie Labs, Cursor background agents, Sweep) [HIGH — README]; differentiation hinges on self-hosted + multi-vendor.
- **Inferred:** Single-author velocity (CI runs are predominantly `jonwiggins`) — bus-factor risk [SPECULATIVE].
- **Scaling concerns:** "One long-lived pod per repo" + "multi-pod scaling" is described but no published throughput, queue depth, or concurrency benchmarks were observed in this session [SPECULATIVE].

### Decision relevance
- Control plane: PRIMARY (three-tier task model, persistent-agent messaging)
- Information substrate: SECONDARY (per-repo prompt templates, inbox state)
- Action surface: SECONDARY (MCP Connections injection)
- Operational discipline: PRIMARY (auto-resume reconciler, encrypted secrets, audit log)
- Deployment surface: TANGENTIAL (Kubernetes-bound — useful as a counter-pattern reference, not as a deployment-surface match)

### Citation strength
HIGH (README + optio.host + CI workflow runs all observed this session).

---

## §4.C3 — mindfold-ai/Trellis (multi-tag: C + D-meta)

### Identification
- **Source name:** Trellis
- **Stratum tags:** C (emerging harness) **+ D-meta** (cross-platform meta-skill / harness-of-harnesses)
- **Maintainer:** mindfold-ai org (org has 6 public repos including Trellis, marketplace, nanoclaw, open-typeless) [HIGH — github.com/mindfold-ai]
- **Primary URL:** https://github.com/mindfold-ai/Trellis
- **Secondary URLs:** https://docs.trytrellis.app/ (docs site, multilingual EN/中文); npm package `@mindfoldhq/trellis`; `mindfold-ai/open-typeless` (showcase repo)
- **Redirect/historical URLs:** none observed
- **License:** AGPL-3.0 [HIGH — npm registry page "Official Repository • AGPL-3.0 License"]. Note: this is a copyleft license and is materially distinct from the more permissive licenses of the other Stratum C entries; surface in Integration considerations.
- **Last meaningful activity:** v0.4.0 published ≈14 days before observation (npm) [HIGH — npmjs.com/@mindfoldhq/trellis]; brief states "very active (3 days)".
- **Star count:** Not directly observed in this session; brief does not specify [SPECULATIVE on count].
- **Cross-reference to Session 3 profile:** NONE.

### Pattern source context
- **Discovery context:** Multi-tag candidate — operates as a harness-layer integration that initialises *across* other harnesses, making it a meta-skill in the D taxonomy as well as an emerging harness in C.
- **Stated thesis:** "A team AI coding harness for progressive specs, custom workflows, task context, and memory across Claude Code, Cursor, Codex, OpenCode, Pi Agent, and more" [HIGH — README opening].
- **Architectural altitude:** meta-skill / methodology + reference implementation. The CLI (`trellis init`) generates platform-specific entry files (`.claude/`, `.cursor/`, `AGENTS.md`, `.agents/`, `.codex/`, `.kilocode/`, `.kiro/`, `.github/copilot/`, `.github/hooks/`, `.pi/`) around a platform-neutral `.trellis/` layout.

### Patterns extracted

1. **Markdown-spec-driven progressive context layout (`.trellis/` skeleton)**
   *Description:* Workflow lives in `.trellis/` with subdirectories `spec/` (project standards), `tasks/` (PRDs, context, status), `workspace/` (per-developer journals + continuity, scoped under `workspace/<user>/`), `workflow.md` (shared workflow rules), and `scripts/`. Specs ship empty by default and are filled per project; `--registry` supports remote spec template repos [HIGH — README + README_CN].
   *Axes:* information substrate (PRIMARY — durable spec/task/workspace memory).
   *Documented in:* `README.md`; `README_CN.md`; `.trellis/` directory in repo.

2. **Multi-platform initialization (cross-harness fan-out)**
   *Description:* `trellis init` accepts platform flags `--cursor`, `--opencode`, `--iflow`, `--codex`, `--kilo`, `--kiro`, `--gemini`, `--antigravity`, `--windsurf`, `--qoder`, `--codebuddy`, `--copilot`, `--droid`, `--pi`. It generates the platform-specific entry files appropriate to each enabled platform, while keeping the canonical workflow in `.trellis/`. For Codex it installs both `.agents/skills/` (project skills) and `.codex/` (project-level config + custom agents). For Pi Agent it installs prompt templates, skills, sub-agent definitions, and project-local TypeScript extensions under `.pi/` [HIGH — README_CN].
   *Axes:* deployment surface (PRIMARY — the harness *is* a deployment-surface fan-out across heterogeneous harnesses); information substrate (SECONDARY — same context, multiple wire formats).
   *Documented in:* `README.md`; `README_CN.md`; CHANGELOG entries v0.3.0 ("platform support expanded from 2 to 10") and v0.3.4 (Qoder) and v0.4.0.

3. **Trellis-meta SKILL pattern (vanilla vs project-local)**
   *Description:* `.claude/skills/trellis-meta/SKILL.md` documents the unmodified system; project-specific customizations are recorded in a separate `trellis-local` skill that "inherits from trellis-meta for base documentation". Hooks are explicitly Claude-Code-only; portable parts (workspace, tasks, specs, file-based configs, JSONL context files) work across all platforms; non-portable parts (`.claude/hooks/`, `.claude/settings.json` hooks, SubagentStop control, Ralph Loop, multi-session worktrees) are bracketed [HIGH — `.claude/skills/trellis-meta/SKILL.md`].
   *Axes:* operational discipline (PRIMARY — explicit portability boundaries); information substrate (SECONDARY).

4. **Task-lifecycle hooks + parent-child subtasks**
   *Description:* v0.3.6 introduced task lifecycle hooks, custom template registries (`--registry`), and parent-child subtasks. v0.3.5 was a hotfix for a delete-migration manifest field name affecting Kilo workflows [HIGH — README CHANGELOG block].
   *Axes:* control plane (PRIMARY — task graph with hooks); operational discipline (SECONDARY).

### V3 framing compatibility

| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | PASS | "Solo developer / team / lab / public-company engineering" all explicitly supported [HIGH — README]. |
| Stack-neutral | PASS | The `.trellis/` layout is filesystem + Markdown only; platform fan-out is the integration layer, not the substrate. |
| Deployment-surface-flexible | PASS | Operates inside whichever host harness the user picks; no deployment commitment. |
| Multi-LLM | PASS | 14 host platforms span essentially all current LLM coding-agent surfaces. |
| Production-grade discipline | PARTIAL | Workspace + spec + task layout is disciplined; hook portability is bracketed (Claude-only) and node version + Python ≥3.9 prerequisites are hard requirements [HIGH — README_CN]. |

### Integration considerations
- **Dependencies:** Node ≥18 (CLI), Python ≥3.9 (init scripts on macOS/Linux uses `python3`, Windows uses `python`).
- **License constraints:** **AGPL-3.0**. This is the strongest licensing constraint of any Stratum C entry. AGPL-3.0 obligations attach to network-service distribution; pattern adoption (re-implementing the `.trellis/` layout idea) is unaffected, but copying source from the repo into a closed-source product triggers AGPL terms. Treat as integration-blocking unless the harness is itself open-sourceable.
- **Framing tensions:** The "best agent harness" tagline overlaps semantically with the V3 harness — Trellis's value is as a context/layout meta-skill, not as a control-plane substitute. Adopt the layout pattern; do not adopt as the harness.
- **Implementation effort:** Layout pattern (1) reproduces in days. Multi-platform fan-out (2) is a maintenance commitment scaling with the number of host platforms supported.

### Critical assessment
- **Documented:** v0.3.6 changelog explicitly fixes a CC v2.1.63+ PreToolUse hook regression, evidencing that hook compatibility is a moving target Trellis chases [HIGH — README CHANGELOG].
- **Documented:** Specs ship empty; "many teams start by letting AI draft specs from existing code and then tighten the important parts by hand" [HIGH — README]. Risk: under-maintained specs amplify outdated rules into every session [SPECULATIVE on severity].
- **Inferred:** A 14-platform fan-out commits the maintainer to N parallel integration treadmills [SPECULATIVE].

### Decision relevance
- Control plane: SECONDARY (task lifecycle hooks, subtasks)
- Information substrate: PRIMARY (spec/task/workspace progressive layout)
- Action surface: TANGENTIAL (delegated to host platform)
- Operational discipline: SECONDARY (portability boundaries, journals)
- Deployment surface: PRIMARY (fan-out across 14 host harnesses is the distinctive deployment pattern)

### Citation strength
HIGH for patterns 1–3 (README, README_CN, SKILL.md, npm registry); HIGH for license (npm registry); MODERATE for star count (not verified in this session).

---

## §4.C4 — code-yeongyu/oh-my-openagent

### Identification
- **Source name:** oh-my-openagent (CLI: `omo`; legacy: `oh-my-opencode`)
- **Stratum tags:** C
- **Maintainer:** Yeongyu Kwon (`code-yeongyu`)
- **Primary URL:** https://github.com/code-yeongyu/oh-my-openagent
- **Secondary URLs:** https://ohmyopenagent.com/ (docs site); npm `oh-my-opencode` (dual-published as `oh-my-openagent` during the rename transition)
- **Redirect/historical URLs:** Repository was previously `oh-my-opencode`; package + binary still ship under the legacy name; plugin registration prefers `oh-my-openagent` with legacy entries loading with a warning [HIGH — README rename-compat block].
- **License:** Not directly read in this session [SPECULATIVE]; the brief does not specify; package.json license field would resolve.
- **Last meaningful activity:** v4.0.0 release "07 May 10:13" with "Team Mode lands today" — observed within hours of 8 May 2026 observation date [HIGH — Releases page]
- **Star count:** Releases page header reads "Star 56.4k" / "Fork 4.6k" — these are anomalously high for a Stratum C entry; the brief lists this entry as Stratum C without a star figure. Treat the 56.4 k figure as [MODERATE] until reconciled with a direct fetch of the repo header — the releases page may be aggregating across forks, and the figure is inconsistent with the brief's framing.
- **Cross-reference to Session 3 profile:** NONE per brief instructions (Stratum C is below threshold). If 56.4 k is the true count, this entry would normally be promoted; the brief explicitly tags it C, so we honour the brief and flag the anomaly here.

### Pattern source context
- **Discovery context:** Direct downstream of oh-my-pi: ports TTSR upstream (commit `feat(ttsr): Port Time Traveling Streamed Rules from oh-my-pi`) and adopts hashline; positioning is a multi-LLM orchestration plugin for OpenCode.
- **Stated thesis:** "the best agent harness — previously oh-my-opencode" with the explicit framing "Models have different temperaments... Single-model tools force you to pick one personality for all tasks. Oh My OpenAgent leverages them all, routing by task type" [HIGH — `docs/guide/overview.md`].
- **Architectural altitude:** harness layered as an OpenCode plugin (~278 k LOC TypeScript across 1967 files; 1304 source + 663 test per `AGENTS.md`).

### Patterns extracted

1. **Sisyphus-led specialised-agent topology**
   *Description:* 11 specialised agents are documented [HIGH — `docs/reference/features.md`], with Sisyphus as orchestrator. Subagents named in the brief and verified in docs include Hephaestus (legitimate-craftsman deep worker, "inspired by AmpCode's deep mode"), Oracle (architecture consultation), Librarian (research/docs), Explore (codebase exploration), Atlas, Prometheus (planning interview mode), Metis. Each subagent is a *role*, not just a model: Sisyphus is "the developer who knows everyone, goes everywhere, gets things done through communication and coordination"; Hephaestus is the autonomous deep worker; Oracle is for nuanced architecture review [HIGH — `docs/guide/agent-model-matching.md`].
   *Axes:* control plane (PRIMARY — orchestrator + named subagents).

2. **Per-agent fallback chains by model**
   *Description:* Each agent has a hard-coded fallback chain in `src/shared/model-requirements.ts`. Sisyphus runtime chain: `anthropic|github-copilot|opencode/claude-opus-4-7 (max) → opencode-go/kimi-k2.6 → kimi-for-coding/k2p5 → opencode|moonshotai|moonshotai-cn|firmware|ollama-cloud|aihubmix/kimi-k2.5 → openai|github-copilot|opencode/gpt-5.5 (medium) → zai-coding-plan|opencode/glm-5 → opencode/big-pickle`. User config can override with arrays mixing plain strings and per-model objects (variant, thinking, budgetTokens) [HIGH — `docs/guide/installation.md`, `docs/reference/features.md`]. Note: model identifiers shown (e.g. "claude-opus-4-7", "gpt-5.5") are reproduced from the docs as written; this catalog does not assert their existence as released models.
   *Axes:* control plane (PRIMARY); operational discipline (SECONDARY — graceful degradation).

3. **Deterministic agent-tab cycling via runtime `order` field**
   *Description:* Tab-cycle order is fixed: Sisyphus (1), Hephaestus (2), Prometheus (3), Atlas (4), with remaining agents following stably [HIGH — `docs/reference/features.md`]. The pattern surfaces a deterministic UX contract over a non-deterministic agent-set.
   *Axes:* operational discipline (PRIMARY — UX determinism); control plane (SECONDARY).

4. **Intent Gate (pre-action intent classification)**
   *Description:* Sisyphus classifies user intent (research / implementation / investigation / fix) before acting, routing accordingly [HIGH — `docs/guide/overview.md`].
   *Axes:* control plane (PRIMARY — routing); information substrate (SECONDARY — intent as a discriminator over context).

5. **Team Mode (parallel multi-agent coordination, OFF by default)**
   *Description:* v4.0.0 (07 May 2026) introduces a lead agent orchestrating category-specialized members in parallel, communicating via `team_create`, `team_send_message`, `team_task_create`, `team_status` tools, with a tmux focus+grid visualization. Storage layout: `~/.omo/teams/{name}/` containing `config.json` (spec), `state.json` (runtime), `mailbox/` (messages), `tasklist.jsonl` (tasks), `worktrees/` (per-member git worktrees). Skills riding on Team Mode: `hyperplan` (5 hostile agents critiquing a plan from orthogonal angles) and `security-research` (3 vulnerability hunters + 2 PoC engineers in parallel) [HIGH — README v4.0.0 release notes; `AGENTS.md` storage layout].
   *Axes:* control plane (PRIMARY); operational discipline (SECONDARY); deployment surface (SECONDARY — tmux-based visualization layer).

6. **Hierarchical config discovery (walked configs)**
   *Description:* Closer wins: `<pwd up to $HOME>/.opencode/oh-my-openagent.json[c]` (legacy: `oh-my-opencode.json[c]`) merges onto user config `~/.config/opencode/oh-my-openagent.json[c]` (Windows `%APPDATA%\opencode\`), falling back to defaults via Zod `safeParse`. `agents`, `categories`, `claude_code` deep-merge recursively (prototype-pollution safe); `disabled_*` arrays are Set unions [HIGH — `AGENTS.md`].
   *Axes:* information substrate (PRIMARY — config layering); operational discipline (SECONDARY — prototype-pollution safety).

### V3 framing compatibility

| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | PASS | Coding-agent framing without persona overlay. |
| Stack-neutral | PARTIAL | Bound to OpenCode as host plugin; tmux as visualization. |
| Deployment-surface-flexible | PARTIAL | Local dev via OpenCode plugin only; no documented embedding/RPC mode. |
| Multi-LLM | PASS | Multi-model orchestration is the explicit thesis. |
| Production-grade discipline | PASS | Default-off Team Mode, write-existing-file-guard, never-as-`any` rule, never-bypass-lint, anonymous telemetry default-on with daily-cap and opt-out env vars [HIGH — `AGENTS.md`]. |

### Integration considerations
- **Dependencies:** OpenCode (host), Bun (install only), tmux (Team Mode visualization).
- **License constraints:** [SPECULATIVE — license not verified this session]. Resolve before adopting.
- **Framing tensions:** Adoption requires accepting OpenCode as the host control plane. Patterns 1–4 are conceptually portable; pattern 5 (Team Mode) is more tightly coupled to host integration.
- **Implementation effort:** The orchestrator/role taxonomy (Sisyphus + Hephaestus + Oracle + …) is reproducible; the value is in the role specialisation by *model temperament*, which transfers as a methodology even without porting code.

### Critical assessment
- **Documented:** README acknowledges that Anthropic blocked OpenCode "because of us" (per maintainer claim, unverified third-party reporting [SPECULATIVE on factual basis]); maintainer's X account "was mistakenly suspended" — both signal an adversarial relationship with upstream vendors that introduces availability risk.
- **Documented:** Hashline benchmark figure for Grok Code Fast 1 (6.7 % → 68.3 %) inherited from oh-my-pi, reproduced in `docs/guide/overview.md` [HIGH — same source as §4.C1 with same caveats].
- **Inferred:** TTSR was *ported in* via commit `206dc8c`; this is the cleanest available evidence that oh-my-pi's patterns are in fact transferable across harnesses [HIGH — github.com/code-yeongyu/oh-my-openagent/actions/runs/22888688607].
- **Anomaly:** Star count discrepancy (56.4 k on releases page vs. brief's Stratum C placement) flagged in Identification.

### Decision relevance
- Control plane: PRIMARY (orchestrator + roles + intent gate + per-agent fallback chains)
- Information substrate: SECONDARY (hierarchical walked config; team mode mailbox)
- Action surface: SECONDARY (TTSR-port, hashline-port; team_* tools)
- Operational discipline: SECONDARY (deterministic tab order, default-off Team Mode)
- Deployment surface: TANGENTIAL (OpenCode-plugin-coupled)

### Citation strength
HIGH for patterns 1–6 (README, AGENTS.md, docs/guide/* and docs/reference/* directly read this session); MODERATE for license and exact star count.

---

## §4.C5 — charmbracelet/crush

### Identification
- **Source name:** Crush
- **Stratum tags:** C
- **Maintainer:** Charmbracelet, Inc.
- **Primary URL:** https://github.com/charmbracelet/crush
- **Secondary URLs:** https://charm.land/; npm `@charmland/crush`; Homebrew tap `charmbracelet/tap/crush`; `github.com/charmbracelet/catwalk` (community model registry)
- **Redirect/historical URLs:** none observed
- **License (MANDATORY FLAG):** **FSL-1.1-MIT (Functional Source License v1.1, MIT Future License) — non-OSI-approved, source-available not open-source.** [HIGH — `LICENSE.md` "Functional Source License, Version 1.1, MIT Future License"; SPDX issue #2458 confirms FSL-1.1-MIT is "not an OSI-approved license"]. Conversion delay: **two years** (fixed in FSL-1.1 spec) — after the change date, the software becomes available under MIT [HIGH — SPDX submission "fixed time period (two years), and only two possible future licenses (Apache 2.0 or MIT)"; LICENSE.md "On or after that date, you may use the Software under the MIT license"]. Competing-Use restriction prohibits substituting for, or offering substantially similar functionality to, the Software in a commercial product or service [HIGH — LICENSE.md Permitted Purpose / Competing Use]. Maintainer clarification (discussion #1482): bundling Crush server-side inside a hosted IDE/platform is permitted; repackaging Crush itself into a competing agent product is not [HIGH — discussions/1482].
- **Last meaningful activity:** v0.62.x and v0.66.0 release artifacts and signed checksums observed [HIGH — Releases page]. Brief specifies "v0.66.0 (Apr 2026)"; release-page entries align.
- **Star count:** 22.4 k★ per discussions header; 15.4 k+ per a third-party review (older snapshot) [HIGH — discussion #1482 page header at observation time].
- **Cross-reference to Session 3 profile:** NONE.

### Pattern source context
- **Discovery context:** Charmbracelet's flagship Go-native terminal coding agent; non-OSI license is the catalog-relevant flag.
- **Stated thesis:** "Glamourous agentic coding for all" — terminal-first, multi-provider, LSP+MCP-extensible [HIGH — repo description].
- **Architectural altitude:** harness — single Go binary with embedded SQLite, Cobra CLI, sqlc-generated DB layer, internal pubsub, and a hooks engine.

### Patterns extracted

1. **Hooks-as-shell-decorators around tools**
   *Description:* Hooks are user-defined shell commands in `crush.json` that fire before tool execution. The engine in `internal/hooks/` is independent of the agent; it takes inputs, runs commands in parallel with timeout + dedup, and returns decisions. The `hookedTool` decorator in `internal/agent/hooked_tool.go` wraps tools at the coordinator level. Hooks run *before* permission checks. Stdin payload, env vars, and stdout-parsed decisions are documented as a stable user-facing protocol in `HOOKS.md` [HIGH — `crush/AGENTS.md`].
   *Axes:* operational discipline (PRIMARY — pre-tool gating); action surface (SECONDARY — tool wrapping).

2. **Coordinator + per-session SessionAgent pattern**
   *Description:* `internal/agent/coordinator.go` manages named agents ("coder", "task"); `internal/agent/agent.go` defines `SessionAgent` running one LLM conversation per session. Pub/sub in `internal/pubsub` decouples agent ↔ UI ↔ services [HIGH — `AGENTS.md`].
   *Axes:* control plane (PRIMARY — explicit Coordinator/Agent split).

3. **Auto-updating provider catalog (Catwalk)**
   *Description:* Default model listing is sourced from `charmbracelet/catwalk`, a "community-supported, open source repository of Crush-compatible models". Crush auto-updates local config from Catwalk when new providers/models appear. Disabled via `disable_provider_auto_update: true` or env `CRUSH_DISABLE_PROVIDER_AUTO_UPDATE=1` for air-gapped use [HIGH — README "Catwalk" section].
   *Axes:* information substrate (PRIMARY — model registry as out-of-band data); operational discipline (SECONDARY — air-gap toggle).

4. **Multi-source context-file discovery**
   *Description:* Crush reads `AGENTS.md`, `CRUSH.md`, `CLAUDE.md`, `GEMINI.md` (and `.local` variants) from cwd for project-specific instructions; `initialize_as` controls the auto-generated context filename [HIGH — `AGENTS.md` + README].
   *Axes:* information substrate (PRIMARY).

5. **Cosign-signed releases**
   *Description:* Each release ships `checksums.txt` + `checksums.txt.sigstore.json`, verifiable via `cosign verify-blob` against `--certificate-identity 'https://github.com/charmbracelet/meta/.github/workflows/goreleaser.yml@refs/heads/main'` and `--certificate-oidc-issuer 'https://token.actions.githubusercontent.com'` [HIGH — Releases v0.66.0 + v0.62.0 + v0.61.1 entries].
   *Axes:* operational discipline (PRIMARY — supply-chain integrity); deployment surface (SECONDARY — verifiable artifacts).

6. **Cross-platform single-binary terminal-native deployment**
   *Description:* "First-class support in every terminal on macOS, Linux, Windows (PowerShell and WSL), Android, FreeBSD, OpenBSD, and NetBSD" via Homebrew, npm `@charmland/crush`, AUR `crush-bin`, Nix (NUR), FreeBSD pkg, Winget, Scoop. CGO disabled (`CGO_ENABLED=0`, `GOEXPERIMENT=greenteagc`) [HIGH — README + `AGENTS.md`].
   *Axes:* deployment surface (PRIMARY).

### V3 framing compatibility

| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | PASS | "Glamourous AI coding agent" is aesthetic, not persona-binding. |
| Stack-neutral | PARTIAL | Go runtime is portable; SQLite + sqlc bind the storage choice. |
| Deployment-surface-flexible | PASS | Single binary, multi-OS, configurable global vs. project paths (`CRUSH_GLOBAL_CONFIG`, `CRUSH_GLOBAL_DATA`). |
| Multi-LLM | PASS | Anthropic, OpenAI, Groq, OpenRouter, Gemini, Cerebras, HuggingFace, Vertex AI, Bedrock, Hyper, MiniMax, Vercel, Copilot — provider-agnostic. |
| Production-grade discipline | PASS | Cosign-signed releases, hook permission ordering, opt-out telemetry (`DO_NOT_TRACK=1`), `.crushignore` access control [HIGH]. |

### Integration considerations
- **Dependencies:** Go toolchain (for source build); `wl-copy`/`wl-paste` (Wayland), `xclip`/`xsel` (X11) for clipboard.
- **License constraints (CRITICAL):** **FSL-1.1-MIT is not OSI-approved**. The Competing-Use clause prohibits making Crush available in a commercial product or service that "substitutes for the Software" or "offers the same or substantially similar functionality." For this catalog's harness — a multi-LLM agent harness — there is a non-trivial risk of being deemed a "substantially similar" product. Maintainer clarification (discussion #1482) explicitly excludes server-side bundling inside a broader platform from Competing Use, but explicitly *includes* repackaging into a competing agent product. The two-year delay before MIT conversion means code committed today reverts to MIT in 2028. Practical posture for this catalog: pattern adoption (hooks engine design, Coordinator/Agent split, Catwalk auto-update model) is unconstrained by the license; *vendoring or forking Crush itself* into the harness as the harness is materially constrained.
- **Framing tensions:** The license is the dominant tension; functional alignment is otherwise high.
- **Implementation effort:** Hooks pattern is ≈1 week to replicate; Catwalk-style auto-updating provider catalog is ≈2–3 weeks including signing infrastructure.

### Critical assessment
- **Documented:** License ambiguity is widely noted by third parties (vibecodinghub.org calls it "source-available rather than plain open source today"; brightcoding.dev incorrectly summarises as "MIT-licensed (with FSL-1.1 for the trademark)" — the latter is wrong; the licensing is FSL-1.1 over the entire software, with MIT as the future-conversion target [HIGH — LICENSE.md primary]).
- **Documented:** v0.66.0 changelog includes `fix: reduce token usage, use short tool descriptions by default` and `fix: silence unless warning about non-existent skill paths` — evidence of ongoing token-efficiency tuning [HIGH — Releases page].
- **Inferred:** Cosign-signed releases plus FSL Competing-Use clause together signal Charmbracelet is treating Crush as a commercially-defended product, not a community-stewarded library [SPECULATIVE on intent].

### Decision relevance
- Control plane: SECONDARY (Coordinator/Agent split as a reference architecture)
- Information substrate: PRIMARY (Catwalk pattern; multi-source context files)
- Action surface: SECONDARY (hooks-as-shell-decorators; MCP http/stdio/sse)
- Operational discipline: PRIMARY (cosign-signed releases; permission ordering)
- Deployment surface: PRIMARY (single Go binary, multi-OS, configurable global vs. project paths)

### Citation strength
HIGH for license, patterns, and release artifacts (LICENSE.md, AGENTS.md, README, Releases page, discussion #1482, SPDX submission #2458 all directly accessed this session).

---

## §4.C6 — shareAI-lab/Kode-Agent

### Identification
- **Source name:** Kode Agent
- **Stratum tags:** C
- **Maintainer:** shareAI-Lab (org: 38 public repos, "Hacking & Accelerating & Saving the World") [HIGH — github.com/shareai-lab]
- **Primary URL:** https://github.com/shareAI-lab/Kode-Agent
- **Secondary URLs:** npm `@shareai-lab/kode` (CLI install path documented at `npm i -g @shareai-lab/kode`); npm `@shareai-lab/kode-sdk`; sister repos listed in appendix below
- **Redirect/historical URLs (URL ANOMALY):** The README's documented git clone target is `git clone https://github.com/shareAI-lab/Kode.git` despite the canonical repo being `Kode-Agent`. This is the URL anomaly flagged in the brief. The `Kode.git` URL appears to redirect to or alias the `Kode-Agent` repo (or to a sibling); the inconsistency is a maintenance/documentation hazard for adopters [HIGH — README clone instruction].
- **License:** Not directly verified this session [SPECULATIVE].
- **Last meaningful activity:** "very active" per brief; sister `learn-claude-code` repo describes a "12-session" harness-engineering tutorial with explicit references to `kode-agent-sdk` as the production successor pattern [HIGH — github.com/shareAI-lab/learn-claude-code].
- **Star count:** Not directly observed for `Kode-Agent` in this session [SPECULATIVE]; brief does not specify.
- **Cross-reference to Session 3 profile:** NONE.

### Pattern source context
- **Discovery context:** shareAI-Lab maintains a multi-repo ecosystem treating "harness engineering" as a discipline; Kode-Agent is the flagship production artifact. SDK (separate repo) is pattern-rich and is referenced from the main repo as the embeddable runtime.
- **Stated thesis:** "Design for post-human workflows. One unit agent for every human & computer task" [HIGH — repo description].
- **Architectural altitude:** harness (TypeScript, Bun, Docker-first deployment) with a separately-released SDK exposing an agent runtime.

### Patterns extracted

1. **Multi-model pointer table (`modelPointers`)**
   *Description:* Configuration declares an array of `modelProfiles` (per-model API key, context length, etc.) and a `modelPointers` map binding *roles* to model-profile names: `main` (primary conversation), `task` (sub-agent), `compact` (context compression), `quick` (quick operations). The `/cost` slash command surfaces token usage and per-model cost tracking [HIGH — README config example].
   *Axes:* control plane (PRIMARY — role→model indirection); information substrate (SECONDARY — context-compression role).

2. **Event-First architecture with Progress / Control / Monitor channel split (SDK-pattern, ported from sister repo)**
   *Description:* The kode-agent-sdk specifies: the UI subscribes only to *Progress* events (text/tool streams); approval and governance flow through *Control & Monitor* callbacks; default does not push noise events. Token usage, errors, and file changes are covered by Monitor events [HIGH — github.com/shareAI-lab/Kode-agent-sdk README]. Note: this pattern lives canonically in the SDK, but the architectural shape governs how Kode-Agent surfaces events.
   *Axes:* information substrate (PRIMARY — channel discipline); operational discipline (SECONDARY — auditable governance channel).

3. **Seven-segment break-point resume (READY → POST_TOOL) with Safe-Fork-Points**
   *Description:* SDK supports seven-stage resumable execution from READY through POST_TOOL; safe-fork-points exist naturally at tool results and pure-text positions, enabling one-click `fork` to continue [HIGH — Kode-agent-sdk README "长时运行 + 可分叉" / long-running + forkable].
   *Axes:* operational discipline (PRIMARY — resumability); control plane (SECONDARY — branching topology).

4. **Multi-agent room (Room API) for collaborative agents**
   *Description:* `npm run example:room # Multi-agent collaboration` — collaborative multi-agent execution surfaced as a first-class SDK example, alongside `agent-inbox` (event-driven inbox), `approval` (tool approval workflow), and `opensandbox` (OpenSandbox basic usage) [HIGH — Kode-agent-sdk README examples list].
   *Axes:* control plane (PRIMARY).

5. **OpenSandbox integration via env config**
   *Description:* Kode-Agent integrates Alibaba's OpenSandbox (Apache-2.0 sandbox runtime, Docker + Kubernetes; CNCF Landscape) via `OPEN_SANDBOX_API_KEY` / `OPEN_SANDBOX_ENDPOINT` / `OPEN_SANDBOX_IMAGE` env vars [HIGH — Kode-agent-sdk README].
   *Axes:* action surface (PRIMARY — sandboxed tool execution); deployment surface (SECONDARY — containerized execution plane).

6. **Tool approval workflow (gated tool execution)**
   *Description:* `npm run example:approval # Tool approval workflow` — approval is a first-class SDK example, with the README emphasising that "tool rejections must be audited" and that Monitor events cover errors and file changes. The `#` prefix turns a chat message into an `AGENTS.md` documentation generator [HIGH — README + Kode-agent-sdk README].
   *Axes:* operational discipline (PRIMARY — HITL); action surface (SECONDARY).

7. **Docker-first deployment with bind mounts**
   *Description:* Standard run: `docker run -it --rm -v $(pwd):/workspace -v ~/.kode:/root/.kode -v ~/.kode.json:/root/.kode.json -w /workspace kode`. Memory directory `~/.kode` and config `~/.kode.json` are bind-mounted into the container [HIGH — README Docker section]. On Linux, sandboxing uses `bwrap` (bubblewrap) and can be disabled via `KODE_SYSTEM_SANDBOX=0`.
   *Axes:* deployment surface (PRIMARY).

### V3 framing compatibility

| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | PASS | "post-human workflows / one unit agent" is an architectural framing, not a persona. |
| Stack-neutral | PARTIAL | TypeScript + Bun + Docker; OpenSandbox optional but recommended. |
| Deployment-surface-flexible | PASS | Local CLI, Docker, embeddable SDK ("standalone library with no per-user process overhead, embeddable in backends, browser extensions, embedded devices"). |
| Multi-LLM | PASS | `modelProfiles` with multiple providers (OpenAI, Alibaba/Qwen) and pointer-based routing. |
| Production-grade discipline | PASS | Approval workflow, WAL, zero-copy text stream, audited tool rejections, MCP-native, Sandbox driver, Scheduler DSL [HIGH — Kode-agent-sdk README]. |

### Integration considerations
- **Dependencies:** Bun (build); Docker (recommended deployment); bwrap on Linux (sandbox); optional OpenSandbox endpoint.
- **License constraints:** Not verified this session — resolve before vendoring [SPECULATIVE].
- **Framing tensions:** The "Kode" vs "Kode-Agent" naming inconsistency (URL anomaly above) requires explicit handling in any clone/vendor pipeline.
- **Implementation effort:** Pattern 1 (`modelPointers`) ≈ days. Pattern 3 (seven-segment resume) is a deep architectural commitment; budget weeks if reproducing faithfully. OpenSandbox integration is API-shaped and ports cleanly.

### Critical assessment
- **Documented:** Sister repo `learn-claude-code` explicitly states the teaching implementation "intentionally simplifies or omits several production mechanisms" including full hook buses, rule-based permission governance, session lifecycle (resume/fork) controls, and full MCP runtime details [HIGH — learn-claude-code README] — i.e. the production patterns documented here are not all present in the teaching repo.
- **Documented:** OpenClaw integration is positioned in `learn-claude-code` as the inspiration for the heartbeat + cron pattern; treat OpenClaw-specific patterns as out-of-scope for this entry (they belong to the OpenClaw entry where OpenClaw appears in the catalog).
- **Inferred:** The shareAI-lab body of work (38 repos) suggests strong development velocity and breadth, but also a higher likelihood of focus drift across repos [SPECULATIVE].

#### Appendix: shareAI-lab body of work (sister repos for reference; NOT cataloged as separate Stratum C entries)

| Repo | One-line description |
|---|---|
| `shareAI-lab/Kode-cli` | Kode CLI (npm `@shareai-lab/kode`); install-and-go terminal CLI, Skill + LSP, Windows-ready, pluggable with GLM / MiniMax / DeepSeek and other open models [HIGH — Kode-cli README + sister-repo summary]. |
| `shareAI-lab/Kode-agent-sdk` | Standalone embeddable agent SDK with no per-user process overhead, MCP-native, OpenSandbox driver, seven-segment resume, multi-agent room [HIGH — Kode-agent-sdk README]. |
| `shareAI-lab/learn-claude-code` | "Bash is all you need" — 0→1 nano-claude-code teaching project with a minimal append-only lifecycle event stream and a JSONL mailbox protocol [HIGH — learn-claude-code README]. |
| `shareAI-lab/claw0` | Per organization listing on shareai-lab profile [HIGH — org listing]. Specific role not surfaced this session [SPECULATIVE]. |
| `shareAI-lab/BashClaw` | Per organization listing [HIGH — org listing]. Specific role not surfaced this session [SPECULATIVE]. |
| `shareAI-lab/mini-claude-code` | Per organization listing [HIGH — org listing]. Specific role not surfaced this session [SPECULATIVE]. |

### Decision relevance
- Control plane: PRIMARY (modelPointers role-routing; multi-agent room; safe-fork resume topology)
- Information substrate: PRIMARY (Progress / Control / Monitor channel split)
- Action surface: PRIMARY (approval workflow; OpenSandbox-mediated tool execution)
- Operational discipline: PRIMARY (WAL, audited tool rejections, seven-segment resume)
- Deployment surface: SECONDARY (Docker-first; SDK-embeddable)

### Citation strength
HIGH for patterns 1, 5, 7 (Kode-Agent README directly read); HIGH for SDK patterns 2, 3, 4, 6 (Kode-agent-sdk README directly read); MODERATE for license, exact star count, and roles of `claw0` / `BashClaw` / `mini-claude-code` not detailed this session.

---

## §4.C7 — mvschwarz/openrig

### Identification
- **Source name:** OpenRig
- **Stratum tags:** C
- **Maintainer:** `mvschwarz`
- **Primary URL:** https://github.com/mvschwarz/openrig
- **Secondary URLs:** npm `@openrig/cli` (install: `npm install -g @openrig/cli`); HN announcement news.ycombinator.com/item?id=47772935
- **Redirect/historical URLs:** Name collisions with unrelated projects exist in the search index (Squarebit Studios's `openrig` Maya rigging library; `0xPlaygrounds/rig`; `rigdev/rig` Kubernetes platform). For this entry, the canonical reference is `mvschwarz/openrig` and the `@openrig/cli` npm package — flag explicitly to avoid pattern-attribution errors.
- **License:** MIT per brief; not directly read this session [MODERATE].
- **Last meaningful activity:** "very active" per brief; tmux-based topology described as actively in development with adapters for Pi and OpenHands "in development" [HIGH — README].
- **Star count:** Not directly observed in this session [SPECULATIVE].
- **Cross-reference to Session 3 profile:** NONE.

### Pattern source context
- **Discovery context:** Counter-positioned to Anthropic's "Claude Managed Agents" cloud-hosted runtime ($0.08/session-hour, Claude-only): OpenRig is "the local side: open source, cross-harness, runs on your machine" [HIGH — README closing block].
- **Stated thesis:** "A harness wraps a model. A rig wraps your harnesses. Define your agent team in YAML, boot it with one command. Claude Code and Codex in the same rig, managed as one system" [HIGH — README].
- **Architectural altitude:** harness-of-harnesses — local daemon + CLI + MCP server + React UI built on tmux. Architecture row: `CLI / UI / MCP | Hono HTTP daemon | Domain services (52) | SQLite + tmux + runtime adapters` [HIGH — README].

### Patterns extracted

*(Tmux-based topology and YAML RigSpec are surfaced separately, per brief instruction.)*

1. **Tmux-based topology orchestration**
   *Description:* "tmux is still doing the talking underneath. I didn't try to add a fancier messaging layer on top" [HIGH — HN comment from author]. Live agent sessions are tmux sessions; CMUX (or `tmux attach`) is the entry point into a node from the React UI. Continuity policies + snapshot/restore by name are layered on top to make tmux topologies recoverable infrastructure rather than ephemeral terminal state [HIGH — README; kirupaForum summary].
   *Axes:* deployment surface (PRIMARY — tmux *is* the runtime substrate); control plane (SECONDARY — topology is expressed in tmux).

2. **YAML RigSpec (declarative multi-agent harness definition)**
   *Description:* RigSpec is "Declarative multi-agent harness definition in YAML. Pods, members, edges, continuity policies, culture file." Auxiliary AgentSpec is a "Reusable agent blueprint with skills, guidance, hooks, profiles, and startup contracts." Pod = "Bounded context group. Agents in a pod share memory and can maintain each other's context" [HIGH — README].
   *Axes:* control plane (PRIMARY — declarative topology); information substrate (SECONDARY — culture file is a context artifact).

3. **MCP-as-self-management (17 tools for agents to manage their own topology)**
   *Description:* The MCP surface exposes 17 tools (`rig_up`, `rig_ps`, `rig_send`, `rig_chatroom_send`, etc.) so agents can manage their own topology. The CLI exposes 40+ commands; each mutating command "ends with what happened, current state, and next action" — a self-describing CLI contract designed for agent consumption rather than human shell use [HIGH — README].
   *Axes:* action surface (PRIMARY — agents act on topology); control plane (SECONDARY — self-orchestration).

4. **Snapshot / restore by name; recoverable infrastructure model**
   *Description:* "Define your team in a YAML file, boot it with one command, and get a live topology you can see, click into, save, and bring back by name" [HIGH — HN post]. Continuity policies are first-class in RigSpec; the value framing is "recoverable infrastructure" rather than disposable terminal state [HIGH — kirupaForum summary].
   *Axes:* operational discipline (PRIMARY — recoverability); control plane (SECONDARY).

5. **Cross-harness `rig send / broadcast / chatroom`**
   *Description:* CLI commands `rig send`, `rig broadcast`, `rig chatroom` (and MCP equivalents `rig_send`, `rig_chatroom_send`) provide a unified messaging vocabulary across heterogeneous runtimes (Claude Code, Codex, terminal nodes; adapters for Pi and OpenHands in development) [HIGH — README].
   *Axes:* control plane (PRIMARY — cross-harness fan-out); action surface (SECONDARY).

6. **Adopted-session managed-config writeback**
   *Description:* OpenRig writes managed config into both global and project scopes: `~/.claude/settings.json` (command allowlist), `~/.claude.json` (workspace trust + onboarding), `.claude/settings.local.json` (managed-session permissions), `.mcp.json` (MCP servers), `~/.codex/config.toml` (workspace trust + MCP servers). "Already-running adopted sessions may need restart before they pick up newly written runtime config" [HIGH — README "For agents" block].
   *Axes:* operational discipline (PRIMARY — config governance across host harnesses); information substrate (SECONDARY).

### V3 framing compatibility

| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | PASS | "Multi-agent harness" framing without persona overlay. |
| Stack-neutral | PARTIAL | TypeScript + Hono + SQLite + tmux is a specific stack; the *patterns* (declarative topology, MCP-as-self-management) are stack-neutral. |
| Deployment-surface-flexible | PARTIAL | Local-only by design; cross-platform tmux is required. The brief's deployment-surface = developer-owned hardware aligns directly. |
| Multi-LLM | PASS | Cross-harness by definition (Claude Code + Codex in one rig; Pi + OpenHands adapters planned). |
| Production-grade discipline | PASS | Snapshot/restore, continuity policies, self-describing mutating commands, `rig doctor` diagnostics [HIGH — README]. |

### Integration considerations
- **Dependencies:** tmux; cmux (optional, for UI-driven attachment); Claude Code and/or Codex installed and authenticated; OAuth logins are out-of-scope for the agent (human-in-the-loop required) per author note "the only thing your agent can't do would be the oauth logins for claude and openai and dealing with permission prompts."
- **License constraints:** MIT (per brief, not directly verified this session) [MODERATE].
- **Framing tensions:** OpenRig is itself a *harness-of-harnesses*. If the V3 harness adopts OpenRig wholesale, the V3 harness becomes a layer atop OpenRig rather than a peer; if the V3 harness adopts the *RigSpec pattern*, it can absorb the topology-declaration discipline without inheriting the tmux runtime constraint.
- **Implementation effort:** RigSpec + AgentSpec + recoverable-topology pattern is a multi-week reproduction; tmux-as-runtime is days but inherits the runtime-isolation gap (parallel rigs trample each other on shared ports / databases — a known general issue with worktree-only isolation).

### Critical assessment
- **Documented:** Author's HN post acknowledges "The project is still early. My own setup uses the config layer extensively (YAML, Markdown, JSON) for prototyping functionality that outpaces what's shipped in the repo and npm package. But the core primitives are there and the happy path in readme works" [HIGH — HN]. This is an explicit early-stage maturity flag.
- **Documented:** "Built to be driven by your agent, not by you typing commands by hand" — the CLI is intentionally agent-first, which is aligned with V3 but is unusual relative to comparable harnesses.
- **Inferred:** Tmux as the runtime substrate inherits tmux's well-known limits: tmux is not designed as a process supervisor; long-lived rigs may degrade (zombies, leaked panes) without explicit cleanup [SPECULATIVE].

### Decision relevance
- Control plane: PRIMARY (RigSpec/AgentSpec; rig send/broadcast/chatroom)
- Information substrate: SECONDARY (culture file; AgentSpec hooks)
- Action surface: PRIMARY (17-tool MCP self-management)
- Operational discipline: PRIMARY (snapshot/restore by name; continuity policies)
- Deployment surface: PRIMARY (tmux-based topology)

### Citation strength
HIGH for patterns 1–6 (README directly read; HN post directly read; kirupaForum summary corroborated).

---

## §4.C8 — paperclipai/paperclip

### Identification
- **Source name:** Paperclip
- **Stratum tags:** C
- **Maintainer:** Paperclip AI org (the paperclipai GitHub org); copyright header in `LICENSE` reads "Copyright (c) 2025 Paperclip AI" [HIGH — `paperclip/LICENSE`]
- **Primary URL:** https://github.com/paperclipai/paperclip
- **Secondary URLs:** https://paperclip.ing/ (project site); npm `paperclipai` (CLI: `npx paperclipai onboard --yes`); `paperclipai/paperclip-docs`, `paperclipai/paperclip-website`, `paperclipai/companies`, `paperclipai/clipmart`, `paperclipai/companies-tool`, `paperclipai/hermes-paperclip-adapter`, `paperclipai/pr-reviewer` (org repos); `agencyenterprise/paperclip-ai` mirror.
- **Redirect/historical URLs:** none observed; org `agencyenterprise/paperclip-ai` mirrors README content.
- **License:** MIT [HIGH — `paperclip/LICENSE`].
- **Last meaningful activity:** Releases page shows ongoing `@paperclipai/mcp-server`, "BETA Standalone MCP server", "Multi-user access and invite flows", "Auto-checkout for scoped wakes" features; very active per brief; observed 8 May 2026 [HIGH — Releases page].
- **Star count:** Org page shows the paperclip repo at 63.4 k★ / 11.4 k forks [HIGH — github.com/paperclipai org listing]. As with C4, this is anomalously high for a Stratum C entry; the brief explicitly tags it C without a star figure. Honour the brief; flag the anomaly here.
- **Cross-reference to Session 3 profile:** NONE.

### Pattern source context
- **Discovery context:** Distinctive deployment-surface pattern — "agent companies as deployment". Paperclip is unique in this catalog in that it models the *organizational structure* (orgs, roles, budgets, goals, governance) as the deployment unit, not the agent process or the K8s pod.
- **Stated thesis:** "Open-source orchestration for zero-human companies. Manage business goals, not pull requests" [HIGH — repo description + paperclip.ing].
- **Architectural altitude:** harness — Node.js server + React UI with embedded PostgreSQL; explicitly self-described as "a full control plane, not a wrapper."

### Patterns extracted

1. **Agent-companies-as-deployment-unit (PRIMARY for deployment-surface axis)**
   *Description:* The deployment unit is the *company*, not the agent or the pod. A single Paperclip deployment runs an unlimited number of companies with complete data isolation between them; "every entity is company-scoped" [HIGH — paperclip.ing FAQ + README]. The companies-spec at `docs/companies/companies-spec.md` documents a portable file layout: `COMPANY.md`, `TEAM.md`, `AGENTS.md`, `PROJECT.md`, `TASK.md`, `SKILL.md` plus the corresponding directory structure (`agents/<slug>/AGENTS.md`, `teams/<slug>/TEAM.md`, etc.). Companies can be exported and imported with secret scrubbing and collision handling [HIGH — docs/companies/companies-spec.md].
   *Axes:* deployment surface (PRIMARY); information substrate (SECONDARY — companies-spec is a Markdown context layout).

2. **Heartbeat + event triggers (BYO-agent abstraction)**
   *Description:* "If it can receive a heartbeat, it's hired." Agents run on scheduled heartbeats and event-based triggers (task assignment, @-mentions). Agents bring their own prompts, models, and runtimes; Paperclip "manages the organization they work in" [HIGH — README + paperclip.ing FAQ].
   *Axes:* control plane (PRIMARY — heartbeat orchestration); action surface (SECONDARY — vendor-neutral agent contract).

3. **Goal-aware execution (full goal ancestry on tasks)**
   *Description:* "Tasks carry full goal ancestry so agents consistently see the 'why,' not just a title." Combined with "governance with rollback" — "approval gates are enforced, config changes are revisioned, and bad changes can be rolled back safely" [HIGH — README "Governance with rollback" / "Goal-aware execution"].
   *Axes:* information substrate (PRIMARY — goal ancestry as durable context); operational discipline (SECONDARY — rollback governance).

4. **Per-agent monthly budget with hard stop**
   *Description:* "Every agent gets a monthly budget. When they hit it, they stop. Automatically. No runaway costs. No surprise bills. Hard limits, enforced by the system." Cost tracking is per-agent / per-task / per-project / per-goal [HIGH — paperclip.ing].
   *Axes:* operational discipline (PRIMARY — cost containment); control plane (SECONDARY — budget gate).

5. **Tailscale-friendly local deployment with bind presets**
   *Description:* `npx paperclipai onboard --yes` defaults to "trusted local loopback mode for the fastest first run". Bind presets surface as `--bind lan` and `--bind tailnet` for authenticated/private mode. The README explicitly recommends "If you're a solo-entrepreneur you can use Tailscale to access Paperclip on the go. Then later you can deploy to e.g. Vercel when you need it" [HIGH — README + paperclip-cli docs].
   *Axes:* deployment surface (PRIMARY — local-loopback / LAN / tailnet preset hierarchy); operational discipline (SECONDARY — auth boundary by preset).

6. **Plugin system with capability-gated host services**
   *Description:* "Instance-wide plugin system with out-of-process workers, capability-gated host services, job scheduling, tool exposure, and UI contributions" [HIGH — README "Plugins"].
   *Axes:* action surface (PRIMARY — plugin tools); operational discipline (SECONDARY — capability gating).

7. **Embedded Postgres for zero-setup local; production swap-in**
   *Description:* Locally a single Node.js process manages an embedded Postgres and local file storage; for production, point at user's own Postgres [HIGH — README "What does a typical setup look like?"]. Decouples dev simplicity from production durability.
   *Axes:* deployment surface (PRIMARY — local/prod gradient); information substrate (SECONDARY — durable state).

### V3 framing compatibility

| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | PARTIAL | "Zero-human companies" framing is persona-laden (you-as-board-of-directors); the *patterns* (heartbeat, goal-ancestry, budgets, multi-tenancy) are persona-neutral. |
| Stack-neutral | PARTIAL | Node.js 20+ / pnpm 9.15+ / React UI / embedded Postgres are concrete stack commitments; the spec format (COMPANY.md / TEAM.md / etc.) is portable. |
| Deployment-surface-flexible | PASS | Loopback / LAN / tailnet bind presets + embedded-vs-external Postgres = flexible. |
| Multi-LLM | PASS | "Bring your own agent" — OpenClaw, Claude Code, Codex, Cursor, OpenCode, any HTTP/CLI bot. |
| Production-grade discipline | PASS | Per-agent budgets with hard stop, audit log, governance with rollback, multi-tenant isolation, secret scrubbing on company export, telemetry opt-out [HIGH — README]. |

### Integration considerations
- **Dependencies:** Node.js ≥20, pnpm ≥9.15; embedded Postgres for local; external Postgres for prod; optional Tailscale for remote-access pattern.
- **License constraints:** MIT — clean.
- **Framing tensions:** "Zero-human companies" is a strong persona framing that the V3 harness should *not* inherit. Adopt the *patterns* (heartbeat-as-agent-contract, goal-ancestry, per-agent budgets, multi-tenancy, bind-preset deployment) without adopting the framing.
- **Implementation effort:** Pattern 1 (companies-spec) is a Markdown spec — adoptable in days. Pattern 2 (heartbeat) requires a scheduler and a stateful agent registry — weeks. Pattern 4 (per-agent budgets with hard stop) requires per-call accounting plumbing — weeks. Pattern 5 (bind presets) is a CLI ergonomics pattern — days.

### Critical assessment
- **Documented:** Releases page shows recent feature flux: "BETA Standalone MCP server", "Multi-user access and invite flows", "Structured issue-thread interactions" with #IDs in the high 3000s and 700s — i.e. the surface is broad and moving [HIGH — Releases page].
- **Inferred (third-party):** Third-party reviewers note "Maximizer Mode removes human approval gates" and "Importable company templates are unproven... no evals, no benchmarks, and no quality guarantees" — the maintainer reportedly described importable templates as "completely unproven" per a third-party review [SPECULATIVE on accuracy of third-party paraphrase; primary source not directly accessed this session].
- **Inferred:** Project is very young (created March 2026 per third-party reporting); 53 k+ stars in 6 weeks per third-party tracking. Stability and maintenance trajectory are not established [SPECULATIVE on dating; primary creation date not directly verified this session].
- **Anomaly:** As with C4, the star figure is anomalously high for Stratum C; brief tagging is honoured.

### Decision relevance
- Control plane: PRIMARY (heartbeat orchestration; goal ancestry; multi-company control plane)
- Information substrate: PRIMARY (companies-spec Markdown layout; goal-ancestry; activity/events durable record)
- Action surface: SECONDARY (plugin system with capability-gated host services; standalone MCP server)
- Operational discipline: PRIMARY (per-agent budgets with hard stop; governance with rollback; audit log)
- Deployment surface: PRIMARY (companies-as-deployment-unit; loopback/LAN/tailnet bind presets; embedded↔external Postgres gradient)

### Citation strength
HIGH for patterns 1–7 (README, paperclip.ing FAQ, `paperclip/LICENSE`, `docs/companies/companies-spec.md`, `paperclip/cli` directory, Releases page all directly accessed this session); MODERATE for star count and creation date (anomaly flagged); SPECULATIVE for the third-party-paraphrased "Maximizer Mode" claim and the "53 k stars in 6 weeks" growth claim.

---
# §5. Stratum D — Methodology Framework

Stratum D is reserved for sources that codify a methodology rather than ship a runtime. The defining characteristic is that the artefact is a set of named principles and patterns intended to guide the engineer building a harness, not a framework that imposes a runtime topology. The single Stratum D entry below — Dex Horthy's *12-Factor Agents* — is the canonical example: it exists as numbered factors, each backed by prose and a small reference snippet, and it is explicitly positioned in the source as anti-framework. The author also appears in Stratum E as a thought leader (multi-tag E), but the pattern-extraction altitude here is the methodology document itself, not the body of work.

## §5.D1 — humanlayer/12-factor-agents

### Identification
- **Source name:** 12-Factor Agents
- **Stratum tags:** D (primary, methodology); E (secondary, thought-leader body — Dex Horthy / HumanLayer)
- **Maintainer / author:** Dex Horthy (HumanLayer); ~75+ acknowledged contributors per repo
- **Primary URL:** `https://github.com/humanlayer/12-factor-agents`
- **Secondary URLs:** `https://www.humanlayer.dev/12-factor-agents` (rendered companion site); `https://github.com/humanlayer/12-factor-agents/tree/main/content` (per-factor markdown)
- **Redirect/historical URLs:** v1.1 tag preserved at `/tree/v1.1`; the methodology itself was first announced ~April 2025 on Hacker News (item 43699271)
- **License:** Apache-2.0 (consistent with humanlayer org default observed for sibling repos) [MODERATE — license file not directly opened this session]
- **Last meaningful activity:** Active discussions in Sep 2025 (Discussion #61, "Collaborators Wanted — npx/uvx create-12-factor-agent"); content directory carries factor files with commit hash `d20c728…` referenced as recent edits to `factor-03-own-your-context-window.md` [HIGH]
- **Star count:** 19.7k stars / 1.5k forks (verified via humanlayer org page) [HIGH]
- **Cross-reference to prior project substrate:** Cited in Cluster 1 (Orchestration) deep-dive, Cluster 5 (Context Engineering) deep-dive, Cluster 6 (HITL & Reliability) deep-dive

### Pattern source context
- **Discovery context:** Surfaced repeatedly during research-substrate phase as the most-cited methodology document for production LLM-powered software. Dex Horthy framed the work in response to the observation that most "AI Agent" products in production are largely deterministic code with LLM steps placed strategically, not the "prompt + tools + loop" archetype that frameworks optimise for. [HIGH]
- **Stated thesis:** Production-grade LLM software is mostly software; the value-add of the agent is small, modular concepts (the twelve factors) that an experienced engineer applies inside an existing application — the explicit analogy is Heroku's 12-Factor Apps. [HIGH]
- **Architectural altitude:** **Methodology** — explicitly *not* a framework. This is the central distinction the source surfaces and the project must preserve when adopting patterns: the artefacts (`create-12-factor-agent` scaffolder, content files) are pattern templates, not runtime libraries. Horthy positions the model as "shadcn for AI agents" — copy, own, modify — in Discussion #61. [HIGH]

### Patterns extracted
The twelve factors are surfaced below with confirmed names from the repo's `content/factor-NN-*.md` filenames where verified, and inferred from the published companion site otherwise. Cluster 1, 5, and 6 deep-dives have already enumerated factor-by-factor reasoning; this catalog entry is a pattern-extraction layer atop that substrate and avoids duplication.

1. **Natural Language → Tool Calls** (`factor-01-natural-language-to-tool-calls.md`). The LLM's primary output contract is a structured tool-call payload that deterministic code dispatches; the LLM does not "execute" anything. [HIGH] *Axes:* Action surface (PRIMARY); Information substrate (SECONDARY).
2. **Own Your Prompts.** Prompts are first-class versioned artefacts owned by the application, not framework-managed templates. [HIGH per companion site index] *Axes:* Information substrate (PRIMARY).
3. **Own Your Context Window** (`factor-03-own-your-context-window.md`). Information density is engineerable; the context window is the primary interface to the model and must be deliberately structured (the source notes the term "context engineering" emerged ~2 months after the document was published). [HIGH] *Axes:* Information substrate (PRIMARY).
4. **Tools Are Just Structured Outputs.** Tools are specifications for what JSON the LLM produces; the harness is what binds those structures to side effects. [HIGH per companion index] *Axes:* Action surface (PRIMARY).
5. **Unify Execution State and Business State** (`factor-05-unify-execution-state.md`). All execution metadata (current step, waiting status) should be inferable from the conversational/tool-call thread; minimise out-of-band session/state stores. Enables thread forking and trivial markdown/HTML rendering. [HIGH] *Axes:* Information substrate (PRIMARY); Operational discipline (SECONDARY).
6. **Launch / Pause / Resume with Simple APIs.** Agent runs are interruptible operations exposed over standard APIs, not in-process loops. [MODERATE — companion-site enumeration] *Axes:* Control plane (PRIMARY); Deployment surface (SECONDARY).
7. **Contact Humans with Tool Calls.** Human input is itself a tool the agent invokes; HITL is not a separate pipeline. Maps directly to humanlayer's A2H (agent-to-human) protocol referenced in the create-12fa-agent template. [HIGH] *Axes:* Action surface (PRIMARY); Operational discipline (SECONDARY).
8. **Own Your Control Flow.** The driving loop is application code, not framework-internal. [HIGH] *Axes:* Control plane (PRIMARY).
9. **Compact Errors into the Context Window.** Errors are summarised and re-injected as context rather than thrown; the agent learns to recover via prompt context. [MODERATE] *Axes:* Information substrate (PRIMARY); Operational discipline (SECONDARY).
10. **Small, Focused Agents.** Prefer many narrow agents over one omni-agent; matches single-file-agents and Claude Code's subagent model. [HIGH] *Axes:* Control plane (PRIMARY).
11. **Trigger from Anywhere; Meet Users Where They Are.** Webhooks, crons, Slack, email, and CLI all become symmetric entrypoints to the same agent core. [MODERATE] *Axes:* Deployment surface (PRIMARY); Action surface (SECONDARY).
12. **Make Your Agent a Stateless Reducer.** The agent is a pure function `(context, event) → next_step`; durability lives below it. [MODERATE] *Axes:* Control plane (PRIMARY); Information substrate (SECONDARY).

### V3 framing compatibility
| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | **PASS** | Methodology is described in terms of engineers building software, not a target persona. |
| Stack-neutral | **PASS** | The `create-12fa-agent` scaffolder explicitly supports Python, TypeScript, and (planned) Ruby; principles claim language-agnosticism. |
| Deployment-surface-flexible | **PASS** | Factors 6 and 11 explicitly require launch-anywhere/trigger-anywhere semantics; stateless-reducer factor pushes durability out of process. |
| Multi-LLM | **PASS** | Sample `.env` in template references `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_AI_API_KEY` simultaneously. [HIGH] |
| Production-grade discipline | **PASS** | Document's stated raison d'être is "actually good enough to put in the hands of production customers." |

### Integration considerations
- **Dependencies:** None; methodology is documentation. Adoption costs are entirely in engineering practice, not lock-in.
- **License constraints:** Apache-2.0 permits derivative methodology documents and copying of factor-content prose with attribution. [MODERATE]
- **Framing tensions:** Factor 5 ("unify execution state and business state") is in productive tension with Stratum G's ACP (which puts execution state in CRDs at the infra layer). The project must decide whether to follow the in-context-window discipline or the externalised-CRD discipline; the two are not directly compatible at the same layer.
- **Implementation effort:** LOW for principle adoption (review existing design against factors); MODERATE if the `create-12fa-agent` scaffolder is used as a starting template.

### Critical assessment
- **Documented limitation:** The author explicitly notes that 12-factor's tradeoff is "more code to write and more setup and glue code" relative to a framework like CrewAI/LangChain (Discussion #61). [HIGH]
- **Replication status:** Methodology has 19.7k stars and broad citation but no quantitative third-party benchmark validates that 12-factor adherence improves outcomes. The thesis rests on Horthy's qualitative survey of "at least 100 SaaS builders." [HIGH]
- **Aspirational vs replicated:** The principles are descriptive of practice Horthy observed, not derived from controlled experiments. Treat as engineering convention, not measured science. [SPECULATIVE on causal benefit]

### Decision relevance
- Control plane: **PRIMARY** (factors 6, 8, 10, 12)
- Information substrate: **PRIMARY** (factors 2, 3, 5, 9)
- Action surface: **PRIMARY** (factors 1, 4, 7)
- Operational discipline: **SECONDARY** (factors 5, 7, 9 carry operational implications)
- Deployment surface: **SECONDARY** (factors 6, 11 — implications, not mandates)

### Citation strength
**HIGH** — primary-source READMEs and content/factor-NN markdown verified this session; star count, license, contributor list, and recent activity all corroborated against the org page.

---

# §6. Stratum D-meta — Cross-Platform Meta-Skill

D-meta surfaces a unifying pattern: **a portable Markdown-spec layer that runs on top of one or more host harnesses (Claude Code, Cursor, Codex, Aider, Copilot, Gemini CLI) and produces or instantiates agents/skills/personas at the project level.** The three entries below differ on what the markdown layer encodes — RevFactory generates *agent teams* from a domain prompt; Maestro encodes *workflow commands* with memory and audit; agency-agents distributes *persona definitions*. All three depend on a host harness's skill/agent file convention as the substrate. This stratum cross-references the Trellis methodology entry (§4 — multi-tagged into D-meta) and disler/the-library (§7.E1 body, which is the "catalog of skills" companion to the meta-skill pattern).

## §6.Dmeta1 — revfactory/harness (+ harness-100)

### Identification
- **Source name:** Harness — Agent Team & Skill Architect for Claude Code
- **Stratum tags:** D-meta (primary)
- **Maintainer / author:** Minho Hwang (revfactory), Kakao AI Native Strategy team lead [HIGH per `revfactory/README.md`]
- **Primary URL:** `https://github.com/revfactory/harness`
- **Secondary URLs:**
  - `https://github.com/revfactory/harness-100` (sister: 100 production-ready harnesses, 200 packages EN+KR, 1,808 markdown files) [HIGH]
  - `https://github.com/revfactory/claude-code-harness` (companion controlled experiment / A/B study) [HIGH]
  - `https://revfactory.github.io/harness/` (project site)
- **License:** Not directly verified this session [MODERATE — assumed permissive given Claude Code plugin marketplace distribution]
- **Last meaningful activity:** Active; star/fork dynamics show 1.5k stars / 189 forks on `harness` and 295 stars / 100 forks on `harness-100` per recent observation [HIGH]
- **Cross-reference to prior project substrate:** NONE (new entry for this catalog)

### Pattern source context
- **Discovery context:** Surfaced as a worked example of "harness-as-code" — the harness itself is generated by an agent from a one-line domain prompt. ai-boost/awesome-harness-engineering cites it explicitly under that label.
- **Stated thesis:** Harness occupies an "L3 Meta-Factory layer" of the Claude Code ecosystem — it produces other harnesses rather than being one. The author distinguishes Harness (team architecture + skills) from Archon (deterministic runtime configuration) and notes both can be combined. [HIGH]
- **Architectural altitude:** **Meta-skill** — a Claude Code plugin/skill whose only job is to design domain-specific agent teams and emit `.claude/agents/` and `.claude/skills/` files for the target project.

### Patterns extracted
1. **Domain-prompt-to-team generation.** A natural-language sentence ("build a harness for webtoon episode production") triggers selection from six pre-defined team-architecture patterns and emits agent+skill markdown into the target project. *Documented in:* root `README.md`, "Two commands. That's it." section. [HIGH] *Axes:* Control plane (PRIMARY); Information substrate (SECONDARY).
2. **Six battle-tested team patterns.** Pipeline; Fan-out/Fan-in; Expert Pool; Producer-Reviewer (Generate-Verify); Supervisor; Hierarchical Delegation. These are the explicit topology vocabulary the meta-skill chooses from. *Documented in:* project site features section. [HIGH] *Axes:* Control plane (PRIMARY).
3. **Progressive Disclosure skills.** Generated skills load detail only on demand to keep the active context window lean. *Documented in:* features section, "Skill Generation." [HIGH] *Axes:* Information substrate (PRIMARY).
4. **Trigger-verify + dry-run + with/without A/B harness.** Validation is a first-class output of the meta-skill: every generated team ships with trigger verification, dry-run tests, and a built-in skill-vs-no-skill comparison harness. *Documented in:* "Validation" feature card. [HIGH] *Axes:* Operational discipline (PRIMARY).
5. **Meta-factory layering vocabulary.** The README explicitly proposes an L1/L2/L3/L4 vocabulary for Claude Code ecosystem layers (skills → harnesses → meta-factories → user prompts), giving a stack-shape language the project can reuse. *Documented in:* `README_KO.md` and English README. [HIGH] *Axes:* Control plane (SECONDARY); Information substrate (SECONDARY).

### V3 framing compatibility
| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | **PARTIAL** | The 100-harness library spans 10 domains (content, software, data/AI, business, education, legal, health, ops); domain personas are first-class but the *meta-skill* itself is persona-neutral. |
| Stack-neutral | **FAIL** | Hard-bound to Claude Code's `.claude/agents/` and `.claude/skills/` filesystem conventions and the `/plugin` marketplace. |
| Deployment-surface-flexible | **PARTIAL** | Markdown artefacts are portable in principle; the loader is not. |
| Multi-LLM | **FAIL** at runtime | Generated artefacts target Claude Code; team-architecture patterns themselves are model-neutral. |
| Production-grade discipline | **PASS** | Quantified A/B claim; validation gates are an explicit output. |

### Integration considerations
- **Adoption mode:** Use as a *pattern reference* (six team architectures, progressive-disclosure idiom, validation triad) rather than a runtime dependency. The project would re-encode the team patterns into its own host-agnostic skill/agent file format.
- **Lock-in:** HIGH if used directly; LOW if used as architectural inspiration.
- **Effort:** LOW to study; MODERATE-HIGH to port the team-pattern catalog to a stack-neutral substrate.

### Critical assessment
- **+60% A/B claim — author-measured, not third-party-replicated.** The exact phrasing on the `claude-code-harness` README is "+60% avg quality (49.5 → 79.3), 15/15 win-rate, −32% variance, n=15, author-measured A/B, third-party replications pending." Sample size is small, the rubric is the author's 10-dimension/100-point evaluation, and complexity-stratified deltas (+23.8 Basic / +29.6 Advanced / +36.2 Expert) are derived from the same n=15. **FLAG: do not cite as established fact.** [HIGH on quote; SPECULATIVE on generalisability]
- **L3 Meta-Factory taxonomy is RevFactory-internal.** The L1–L4 layering is not standard vocabulary; useful for internal reasoning, premature for external comms.

### Decision relevance
- Control plane: **PRIMARY** (six topology patterns directly inform the orchestration loop's supported shapes)
- Information substrate: **SECONDARY** (progressive disclosure pattern)
- Action surface: **TANGENTIAL**
- Operational discipline: **PRIMARY** (validation triad)
- Deployment surface: **TANGENTIAL** (Claude-Code-bound runtime)

### Citation strength
**HIGH** for repo content, README, and A/B claim wording verified this session; **MODERATE** on license (not opened directly).

---

## §6.Dmeta2 — sharpdeveye/maestro

### Identification
- **Source name:** Maestro — Workflow fluency for AI coding agents
- **Stratum tags:** D-meta (primary)
- **Maintainer / author:** sharpdeveye
- **Primary URL:** `https://github.com/sharpdeveye/maestro`
- **License:** Not directly verified this session [MODERATE]
- **Last meaningful activity:** Active per audit-log example dated 2026-04-26 in README sample [HIGH]
- **Cross-reference to prior project substrate:** NONE

> **Disambiguation:** "Maestro" is also used by `mobile-dev-inc/maestro` (mobile UI testing), `ReinaMacCredy/maestro` (Linear-style harness), `neilzhangpro/Maestro` (Symphony-derived Linear/GitHub orchestrator), and `sionic-ai/sionic-maestro-skills` (multi-LLM consult). Only `sharpdeveye/maestro` is the catalog entry; the others are noted to prevent confusion in citations.

### Pattern source context
- **Discovery context:** Cited as the canonical example of a *cross-host* portable workflow skill — explicitly claims compatibility with Cursor, Claude Code, Gemini CLI, Copilot, plus six others.
- **Stated thesis:** A single, opinionated workflow skill plus 25 commands plus 7 domain reference files, layered with a memory directory and an audit-log JSONL, gives any AI coding agent "workflow fluency" without committing to a specific host. [HIGH]
- **Architectural altitude:** **Meta-skill** — a portable Markdown-spec layer.

### Patterns extracted
1. **One-skill / 25-command / 7-reference layout.** The repo packages a single SKILL.md plus 25 slash commands (`/diagnose`, `/streamline`, `/fortify`, `/refine`, `/calibrate`, `/evaluate`, `/accelerate`, `/specialize`, etc.) and 7 domain reference docs (prompt-engineering, context-management, tool-orchestration, agent-architecture, plus three more). *Documented in:* README "Skill" section. [HIGH] *Axes:* Information substrate (PRIMARY); Control plane (SECONDARY).
2. **Project-context handshake.** A `.maestro.md` (or `.maestro/context.md`) is the required pre-flight artefact ensuring every command operates with project-specific awareness. *Documented in:* "context gathering protocol" callout. [HIGH] *Axes:* Information substrate (PRIMARY).
3. **Append-only decision + audit log.** `.maestro/decisions.jsonl` and `.maestro/audit.jsonl` capture every command invocation with cost and duration; sessions are summarised to dated markdown. *Documented in:* directory tree in README. [HIGH] *Axes:* Operational discipline (PRIMARY).
4. **Effectiveness panel.** Standardised TUI-style output reports commands run, completion rate, most-used command, and total cost — making the meta-skill itself observable from inside the host harness. [HIGH] *Axes:* Operational discipline (PRIMARY).
5. **Embedded anti-patterns.** SKILL.md explicitly prohibits four behaviours: dumping codebases into context; using multi-agent for single-agent problems; skipping error handling; retrying identical prompts. This is anti-pattern-as-spec. *Documented in:* "what to avoid" section. [HIGH] *Axes:* Operational discipline (SECONDARY).
6. **MCP-server execution mode.** README notes Maestro can run as a live MCP server rather than static skill files — same artefacts, two execution surfaces. [HIGH] *Axes:* Action surface (SECONDARY); Deployment surface (SECONDARY).

### V3 framing compatibility
| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | **PASS** | Coding-agent oriented but workflow vocabulary is generic. |
| Stack-neutral | **PASS** | Explicit cross-host claim across 10 hosts; commands defined as plain Markdown. |
| Deployment-surface-flexible | **PASS** | Static skill OR live MCP server. |
| Multi-LLM | **PASS** | Host-agnostic implies model-agnostic. |
| Production-grade discipline | **PASS** | Audit log + decision log + effectiveness panel are operational-discipline primitives. |

### Integration considerations
- **Adoption mode:** High-fidelity pattern source for the project's command surface and audit substrate.
- **Dependencies:** `npx skills add sharpdeveye/maestro` install path implies a shared "skills" CLI convention; portability claim depends on each host's interpretation of skill files.
- **Effort:** LOW to study; LOW-MODERATE to lift the audit/decision-log JSONL pattern.

### Critical assessment
- **"10 hosts" claim is unverified.** README claims compatibility with Cursor, Claude Code, Gemini CLI, Copilot, "and 6 more"; the six are not enumerated this session. [MODERATE on stated claim; SPECULATIVE on operational equivalence across all hosts]
- **Cost/duration metrics depend on host telemetry.** The effectiveness panel shows `~$0.47` totals; this requires the host to expose token/cost data, which not all hosts do. [SPECULATIVE — implementation detail not verified]

### Decision relevance
- Control plane: **SECONDARY** (commands frame the loop's verbs)
- Information substrate: **PRIMARY** (context-handshake + reference docs)
- Action surface: **SECONDARY** (MCP-server mode)
- Operational discipline: **PRIMARY** (audit/decision/effectiveness triad)
- Deployment surface: **SECONDARY** (static-or-server)

### Citation strength
**HIGH** on README content; **MODERATE** on cross-host claim and license.

---

## §6.Dmeta3 — msitarzewski/agency-agents

### Identification
- **Source name:** Agency Agents — A complete AI agency at your fingertips
- **Stratum tags:** D-meta (primary)
- **Maintainer / author:** Michael Sitarzewski (msitarzewski)
- **Primary URL:** `https://github.com/msitarzewski/agency-agents`
- **License:** MIT (verified in README acknowledgements section) [HIGH]
- **Last meaningful activity:** Discussions through May 2026; ideas thread in March 2026 [HIGH]
- **Star count / scale:** **README states 147 agents across 12 divisions** and ~91.5k–94.8k stars / ~15k–15.7k forks observed across mirror pages this session. The task brief specifies **"112 specialised agent personas (March 2026)"** — this likely captured a March 2026 snapshot before later additions; both numbers are reflected here with the caveat. [HIGH on current README; HIGH on brief-stated March 2026 count]
- **Cross-reference to prior project substrate:** NONE

### Pattern source context
- **Discovery context:** Surfaced as the canonical example of *persona-as-markdown injection* — a fundamentally different pattern from skills (capabilities/workflows) or agents (instances). Personas are *identity definitions* for an existing host agent.
- **Stated thesis:** Each agent is "specialized, personality-driven, deliverable-focused, production-ready" — depth of role definition is what produces architecture-level output rather than surface-level autocomplete. [HIGH]
- **Architectural altitude:** **Meta-skill** (persona-injection variant) — distributable across host harnesses via per-host install scripts that translate the same Markdown into host-native locations.

### Patterns extracted
1. **Persona-as-Markdown distribution.** The unit of distribution is a persona file (mission, rules, voice, success metrics). Personas are not skills (capabilities) and not agent instances (runtime); they are configuration of an underlying coding agent. *Documented in:* repo top-level READMEs. [HIGH] *Axes:* Information substrate (PRIMARY).
2. **Per-host install translation.** A single source persona is installed via `./scripts/install.sh --tool <claude-code|copilot|gemini-cli|opencode|cursor|antigravity|aider>`, with each host's native location and format derived from the source: Claude Code → `~/.claude/agents/`; Copilot → `~/.github/agents/` + `~/.copilot/agents/`; Antigravity → `~/.gemini/antigravity/skills/agency-<slug>/SKILL.md`; Gemini CLI → extension + skill files; OpenCode → `.opencode/agents/`; Cursor → `.cursor/rules/*.mdc`. *Documented in:* "Multi-tool support" README section. [HIGH] *Axes:* Deployment surface (PRIMARY); Action surface (SECONDARY).
3. **12-division agent taxonomy.** Engineering, Design, Marketing, Product, Support, Spatial Computing, Project Management, Reddit/community, plus others — a real ontology rather than ad-hoc personas. *Documented in:* README "12 divisions." [HIGH] *Axes:* Control plane (SECONDARY).
4. **Multi-agent exercise pattern.** The `examples/` directory documents a "Nexus Spatial Discovery Exercise" where 8 agents ran in parallel and produced cross-referencing plans without coordination overhead — the persona files are sufficient context for emergent coordination. *Documented in:* `examples/README.md`. [HIGH] *Axes:* Control plane (PRIMARY).
5. **Reality-Checker meta-persona.** Distinct persona class whose mission is to verify whether a stated requirement is feasible — a structural counterweight to other personas, not a workflow stage. [HIGH] *Axes:* Operational discipline (SECONDARY).

### V3 framing compatibility
| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | **PASS** at meta-level | Project must remain persona-neutral; agency-agents demonstrates the *pattern* (per-host translation) without requiring adoption of any specific persona. |
| Stack-neutral | **PASS** | Same Markdown → 7+ host targets via translation scripts. |
| Deployment-surface-flexible | **PASS** | Each install path is a different surface. |
| Multi-LLM | **PASS** | Per-host install generalises across providers. |
| Production-grade discipline | **PARTIAL** | Persona files include "success metrics" by convention but no validation runtime ships. |

### Integration considerations
- **Adoption mode:** **Pattern only**, never persona content. The project is deliberately persona-agnostic; the value here is the *translation idiom* and the *persona-as-markdown* abstraction.
- **License (MIT):** Compatible with copying and modifying.
- **Effort:** LOW to study the install translation scripts.

### Critical assessment
- **Star count includes growth from a Reddit-thread origin** (147 agents are evolved from an initial 51). Stars do not validate persona quality; they validate appeal. [HIGH on origin; SPECULATIVE on quality]
- **No quantitative quality benchmark.** "Production-ready" and "battle-tested" are author claims without measured backing. [HIGH on claim; SPECULATIVE on validation]
- **Persona pattern is distinct from skill pattern and must not be conflated.** The project should treat persona injection (identity), skill injection (capability), and agent definition (runtime instance) as three orthogonal axes — agency-agents is the cleanest reference for the persona axis.

### Decision relevance
- Control plane: **SECONDARY** (multi-persona exercise demonstrates parallel-by-design coordination)
- Information substrate: **PRIMARY** (persona-as-markdown is the pattern)
- Action surface: **SECONDARY**
- Operational discipline: **TANGENTIAL** (Reality-Checker pattern)
- Deployment surface: **PRIMARY** (cross-host translation idiom)

### Citation strength
**HIGH** on README, install scripts, license, and persona-pattern thesis verified this session.

---

# §7. Stratum E — Thought-Leader Bodies of Work

Stratum E catalogs the *body of work* of an individual thought leader — not a single repo. The catalog entry distills 3–5 recurring patterns that appear across multiple repos in the body, with the anchor repo carrying primary citation and companion repos cited as evidence of pattern recurrence. Entries E3 and E4 are channel companions to the body-of-work entries; they receive abbreviated treatment.

## §7.E1 — disler (anchor: single-file-agents)

### Identification
- **Source name:** disler / IndyDevDan (Dan Isler)
- **Stratum tags:** E (primary, body of work)
- **Maintainer / author:** disler
- **Primary URL (anchor repo):** `https://github.com/disler/single-file-agents`
- **Author profile:** `https://github.com/disler?tab=repositories`
- **Companion repos cited as evidence of pattern recurrence:**
  - `https://github.com/disler/the-library` — meta-skill catalog of agentics [HIGH]
  - `https://github.com/disler/just-prompt` — MCP server unifying OpenAI/Anthropic/Gemini/Groq/DeepSeek/Ollama [HIGH]
  - `https://github.com/disler/infinite-agentic-loop` — wave-based parallel sub-agent generation [HIGH]
  - `https://github.com/disler/claude-code-hooks-mastery` — 13-hook lifecycle interception [HIGH]
  - `https://github.com/disler/claude-code-hooks-multi-agent-observability` — real-time hook-event monitoring [HIGH]
  - `https://github.com/disler/fork-repository-skill` — terminal-fork-N-times skill [HIGH]
  - `https://github.com/disler/agent-sandboxes` — E2B-isolated parallel agent forks [HIGH]
  - `https://github.com/disler/bowser` — composable skill/subagent/command/justfile browser automation [HIGH]
  - `https://github.com/disler/the-verifier-agent` — two-agent observer system with input-disabled verifier [HIGH]
  - `https://github.com/disler/agent-sandbox-skill` — isolated execution skill [HIGH]
- **License (anchor):** MIT (consistent with infinite-agentic-loop MIT verified) [MODERATE — anchor not opened directly]
- **Last meaningful activity:** Body is actively maintained; multiple repos updated 2026 (the-library, the-verifier-agent, bowser among recent). disler GitHub bio: "Betting the next 10 years of my career on AGENTIC software." [HIGH]
- **Cross-reference to prior project substrate:** Cited in Cluster 1 (Orchestration) deep-dive — Single-File Agent (SFA) pattern.

### Pattern source context
- **Discovery context:** disler's body of work is the highest-density public output on Claude-Code-style agentic coding patterns and is the companion to the @IndyDevDan YouTube channel; many patterns appear first as a video demo and then crystallise into a repo.
- **Stated thesis:** "What if we could pack single purpose, powerful AI Agents into a single python file?" (single-file-agents). The broader thesis across the body is **maximum control via minimum primitives**: prefer one file over a framework; prefer composable skills/subagents/commands/justfiles over monolithic harnesses; prefer running N parallel agents to scale rather than one cleverer agent. [HIGH]
- **Architectural altitude:** **Thought-leader body of work** spanning reference implementations, methodology demos, and pattern crystallisations. Anchor repo (single-file-agents) is reference-implementation altitude.

### Recurring patterns across the body (5 distilled)
1. **Single-File Agent (SFA).** A self-contained Python file using `uv` script-header dependency declarations, packaging one narrow agent end-to-end. The author explicitly notes "we're using the term 'agent' loosely — we have prompts, prompt chains, and a couple are official Agents." Pattern is about *atomic packaging*, not strict ReAct loops. *Anchor:* `single-file-agents/README.md`. *Recurrence:* `quick-data-mcp` follows the same atomic-packaging discipline; `mac-mini-agent` apps are similarly atomic. [HIGH] *Axes:* Control plane (PRIMARY); Deployment surface (SECONDARY).
2. **Composable layered architecture (skill / subagent / command / justfile).** The same workflow is exposed at four entry points — a raw skill, a subagent that wraps the skill for parallel execution, a slash command that orchestrates, and a `just` recipe for one-line shell access. The user can enter at any layer. *Documented in:* `bowser/README.md` and `agent-sandboxes/README.md`. *Recurrence across:* bowser, agent-sandboxes, agentic-finance-review, fork-repository-skill. [HIGH] *Axes:* Control plane (PRIMARY); Action surface (PRIMARY).
3. **Hooks as deterministic guardrails.** Lifecycle hooks (PreToolUse / PostToolUse / Stop / SessionStart, etc.) are the primary mechanism for adding deterministic validation, security filtering, and observability to a non-deterministic agent. The `claude-code-hooks-mastery` repo enumerates 13 hook events; `agentic-finance-review` shows PostToolUse CSV validators on every Read/Edit/Write; `claude-code-hooks-multi-agent-observability` ships hooks as the event-emission layer. [HIGH] *Axes:* Operational discipline (PRIMARY); Action surface (SECONDARY).
4. **Parallel forking for scale.** The thesis "spend tokens to generate value and time" appears repeatedly: `infinite-agentic-loop` deploys parallel sub-agents in waves with progressive sophistication; `fork-repository-skill` forks the running terminal agent N times into new windows; `agent-sandboxes/obox` runs N agent forks across isolated E2B sandboxes; `the-verifier-agent` runs a second agent in parallel as a read-only observer. The body's stance is that single-agent serial work is the ceiling and parallel forking is the way past it. [HIGH] *Axes:* Control plane (PRIMARY); Operational discipline (SECONDARY).
5. **Multi-LLM uniform interface (just-prompt).** A unified MCP server fronts OpenAI, Anthropic, Google Gemini, Groq, DeepSeek, and Ollama with a single tool surface. Default models are configured as a list (e.g., `openai:o3:high,openai:o4-mini:high,anthropic:claude-opus-4-…,gemini:gemini-2.5-pro-preview-…`) and the server boot-checks key availability. The `ceo_and_board` tool pattern uses multi-model consultation to surface dissent on hard decisions. *Anchor for this pattern:* `just-prompt/README.md`. [HIGH] *Axes:* Action surface (PRIMARY); Deployment surface (SECONDARY).

### V3 framing compatibility (body-level)
| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | **PASS** | Patterns are about engineering primitives, not personas. |
| Stack-neutral | **PARTIAL** | Strong Claude Code centring; just-prompt and SFA are model-neutral; hooks are Claude-Code-specific. |
| Deployment-surface-flexible | **PASS** | Local-dev demos but patterns generalise to MCP, CLI, justfile, sandboxed remote, and parallel terminal. |
| Multi-LLM | **PASS** | just-prompt is the explicit multi-LLM artefact in the body. |
| Production-grade discipline | **PASS** | Hook discipline + verifier-agent pattern address review and validation as first-class. |

### Integration considerations
- **Adoption mode:** Treat the body as a pattern-mining quarry. Best candidates for direct lift are (a) the layered skill/subagent/command/justfile shape, (b) the hook-as-guardrail discipline, (c) the just-prompt-style multi-provider abstraction, and (d) the verifier-agent observer pattern.
- **License:** Mostly MIT across the body (verified for infinite-agentic-loop; presumed for siblings). [MODERATE]
- **Effort:** LOW to study; MODERATE to port the layered architecture cleanly into a stack-neutral host.

### Critical assessment
- **Claude-Code-centring is real.** Many repos depend on Claude Code's `.claude/` filesystem convention, hooks API, and Task tool. Pattern abstraction is possible but requires deliberate translation effort.
- **Aspirational author claims to flag.** Some videos and READMEs use marketing-style superlatives ("the best agentic coding tool," "scale your impact"). The patterns are sound; the rhetoric is YouTube-flavoured. Quote sparingly.
- **No third-party measurement.** The body is widely watched and forked but not benchmarked; treat as engineering convention, not validated science. [SPECULATIVE on causal benefit claims]

### Decision relevance
- Control plane: **PRIMARY** (SFA, layered architecture, parallel forking)
- Information substrate: **SECONDARY** (CLAUDE.md / context-prime patterns)
- Action surface: **PRIMARY** (hooks, just-prompt, MCP servers)
- Operational discipline: **PRIMARY** (hook guardrails, verifier-agent)
- Deployment surface: **SECONDARY** (sandboxed, parallel-fork, MCP-or-skill modalities)

### Citation strength
**HIGH** on every cited repo's README content verified this session.

---

## §7.E2 — coleam00 (anchor: Archon)

### Identification
- **Source name:** coleam00 / Cole Medin (Founder, Dynamous AI)
- **Stratum tags:** E (primary, body of work)
- **Author profile:** `https://github.com/coleam00?tab=repositories`
- **Anchor repo:** `https://github.com/coleam00/Archon`
- **Companion repos / branches cited as evidence of pattern recurrence:**
  - `archive/v1-task-management-rag` branch — original Python-based Archon (task management + RAG) preserved [HIGH]
  - `https://github.com/coleam00/context-engineering-intro` — PRP framework, CLAUDE.md template, examples-driven approach [HIGH]
  - `principles-of-agentic-engineering` workshop repo — "AI layer concept, the PIV loop, 15 reusable Claude Code commands" [HIGH per coleam00 repos page]
  - `local-ai-packaged` — Ollama + Supabase + n8n + Open WebUI single-package local stack [HIGH]
  - `ottomator-agents` — open-source agents on Live Agent Studio [HIGH]
  - GAN-inspired three-agent harness (generator vs adversarial evaluator) — referenced on profile as a discrete repo [HIGH]
  - "second-brain" / Claude-Code-memory companion repos referenced on profile [HIGH]
- **License (anchor):** MIT (per coleam00 repos page summary line for Archon) [HIGH]
- **Last meaningful activity:** Archon at ~21k stars / 3.2k forks; releases dated through May 2026 with active CI build features (build-time constants, env-leak gate, retroactive consent) [HIGH]
- **Cross-reference to prior project substrate:** NONE explicit; thematically adjacent to Cluster 1 (Orchestration) and Cluster 5 (Context Engineering)

### Pattern source context
- **Discovery context:** Archon is positioned as **"the first open-source harness builder for AI coding"** — a workflow engine for AI coding agents that turns development processes into YAML workflows. The framing line is "Like what Dockerfiles did for infrastructure and GitHub Actions did for CI/CD — Archon does for AI coding workflows. Think n8n, but for software development." [HIGH]
- **Stated thesis:** AI coding agents are non-deterministic by default. Determinism is recovered by encoding the development process as a workflow — phases, validation gates, artifacts — owned by the team. The AI fills in intelligence at each step; the structure stays fixed. [HIGH]
- **Architectural altitude:** **Body of work** — Archon is reference-implementation altitude for harness-builder pattern; companion repos provide context-engineering, agent-architecture experiments, and local-stack patterns.

### Recurring patterns across the body (5 distilled)
1. **Workflow-as-DAG-YAML with loop nodes.** Archon defines workflows in `.archon/workflows/*.yaml` and slash-commands in `.archon/commands/*.md`. The Workflow Builder is a visual drag-and-drop DAG editor with loop-node support. Same-named files in the user repo override bundled defaults — workflows are version-controlled team artefacts. *Documented in:* Archon README "Authoring Workflows." [HIGH] *Axes:* Control plane (PRIMARY); Information substrate (SECONDARY).
2. **Multi-agent refiner evolution (V4 → V5).** Earlier Archon (v5 Python era) introduced specialized refiner agents for prompts, tools, and agent definitions; the primary coding agent creates the initial agent and follow-up "refine" prompts kick off specialized agents in parallel. The current TypeScript Archon retains the architectural intent (workflows + multi-agent execution) at a different scope. *Documented in:* `CCwithAi/Archon-v5` mirror citing Cole Medin's original; current Archon README "idea-to-PR" workflow trace. [HIGH on V5 statement; HIGH on current architecture] *Axes:* Control plane (PRIMARY).
3. **PRP framework + CLAUDE.md + examples directory.** Context-engineering-intro repo defines a 3-step Product Requirements Prompt (PRP) flow: (1) write `INITIAL.md` with examples and context; (2) `/generate-prp INITIAL.md` produces a comprehensive PRP under `PRPs/`; (3) `/execute-prp PRPs/<feature>.md` implements. CLAUDE.md holds project-wide rules. `examples/` directory is described as "critical." *Documented in:* `context-engineering-intro/README.md`. [HIGH] *Axes:* Information substrate (PRIMARY); Operational discipline (SECONDARY).
4. **Platform-adapter pattern.** Archon's orchestrator sits behind a uniform adapter layer (Web UI, CLI, Telegram, Slack, Discord, GitHub Webhooks) — same routing/context manager, multiple ingress surfaces, each a 5–15-minute setup. *Documented in:* Archon README architecture diagram. [HIGH] *Axes:* Deployment surface (PRIMARY); Action surface (SECONDARY).
5. **Local-first + cloud-flexible packaging.** `local-ai-packaged` bundles Ollama + Supabase + n8n + Open WebUI for fully-local deployment; Archon's CLI ships as binary installs (curl-fetched) plus a `bun run dev` source path. The body consistently treats local-dev as a first-class deployment surface without excluding hosted/cloud. [HIGH] *Axes:* Deployment surface (PRIMARY); Operational discipline (SECONDARY).

### V3 framing compatibility (body-level)
| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | **PASS** | Workflow vocabulary is persona-agnostic. |
| Stack-neutral | **PARTIAL** | Archon installs the Archon skill into Claude Code projects via the setup wizard; YAML workflows are stack-neutral but the runtime currently orchestrates Claude Code as the executor. |
| Deployment-surface-flexible | **PASS** | Web UI, CLI binary, source build, and platform adapters cover most surfaces. |
| Multi-LLM | **PARTIAL** | Current Archon orchestrates Claude Code (which itself supports multiple Anthropic models); v5-era Archon was provider-broader. |
| Production-grade discipline | **PASS** | Validation gates and PR creation are first-class workflow phases. |

### Integration considerations
- **Adoption mode:** Strong reference for **the harness-builder pattern itself** — workflows + commands as versioned, overridable team artefacts. The platform-adapter shape is directly liftable.
- **License (MIT):** Permissive; safe to study and re-encode.
- **Effort:** LOW to study; MODERATE to lift workflow-DAG semantics into the project's chosen substrate.

### Critical assessment
- **"First open-source harness builder for AI coding" is a marketing claim.** Several open-source harness-builders (RevFactory Harness, ruflo, Maestro v2, OpenHarness) make adjacent claims. Treat the framing as positioning, not historical record. [HIGH on quote; SPECULATIVE on primacy]
- **Archive branch confusion risk.** The original Python-RAG Archon is preserved on `archive/v1-task-management-rag`; community references and the `CCwithAi/Archon-v5` mirror reflect that earlier architecture. The catalog entry treats current Archon as the anchor and v5 as evolutionary context — the project should not conflate them.
- **Workflow YAML schema is Archon-specific.** Liftable as pattern, not as artefact.

### Decision relevance
- Control plane: **PRIMARY** (workflow DAG + loop nodes is the core orchestration grammar)
- Information substrate: **PRIMARY** (PRP + CLAUDE.md + examples discipline)
- Action surface: **SECONDARY** (platform adapters)
- Operational discipline: **SECONDARY** (validation gates as workflow phases)
- Deployment surface: **PRIMARY** (multi-platform adapter + local-first packaging)

### Citation strength
**HIGH** on Archon README, releases page, profile repo list, and context-engineering-intro README verified this session.

---

## §7.E3 — YouTube @indydevdan (companion to E1)

### Identification
- **Source name:** IndyDevDan (Dan Isler) — YouTube channel
- **Stratum tags:** E (companion entry)
- **Maintainer:** disler (same author as E1)
- **Primary URL:** `https://www.youtube.com/@indydevdan`
- **Channel pages:** `/videos`, `/channel/UC_x36zCEGilGpB1m-V4gmjg`
- **Subscriber / video count:** 127k subscribers / 191 videos per Developer Educators channel listing; "AI Coding YouTube channel … updated daily"; brief alignment confirmed [HIGH]
- **Companion to:** disler GitHub repos (E1)
- **Cross-reference to prior project substrate:** NONE direct; many disler repos link "watch the breakdown video" to specific @IndyDevDan videos.

### Recurring themes (3 distilled)
1. **Top-2% agentic engineering thesis** — multi-agent orchestration over single-agent prompting, custom agents, agent sandboxes, and "agentic coding 2.0" where the engineer talks to a lead agent that orchestrates worker agents. Crystallised in the agenticengineer.com 2026 roadmap and reflected across ~Q1–Q2 2026 videos. [HIGH]
2. **Skills + subagents + slash commands as the composable triad** — a recurring pedagogical structure that maps directly to the layered-architecture pattern in E1. VSCode-snippets gist (last active 2026-03-24) is the meta-example. [HIGH]
3. **Tactical, repo-anchored video format** — most videos pair with a public disler repo that the viewer can clone and run; the channel is, in practice, the documentation surface for the body of work. [HIGH]

### Representative video citations
- "Elite Context Engineering with Claude Code" — `https://www.youtube.com/watch?v=Kf5-HWJPTIE` (sneak-peek of Tactical Agentic Coding course; context-engineering theme).
- "One Agent Is NOT ENOUGH: Agentic Coding BEYOND Claude Code" — `https://www.youtube.com/watch?v=M30gp1315Y4` (multi-agent thesis).

### V3 framing compatibility
| Dimension | Verdict |
|---|---|
| Persona-neutral | PASS |
| Stack-neutral | PARTIAL (heavy Claude Code) |
| Deployment-surface-flexible | PASS |
| Multi-LLM | PASS |
| Production-grade discipline | PASS |

### Integration considerations
- **Adoption mode:** Reference media; do not embed video transcripts. Cite specific videos when an E1 repo's README points to them.
- **No license issues at the citation altitude.**

### Critical assessment
- Channel is a self-promotion surface for the agenticengineer.com paid course (Tactical Agentic Coding); some claims are sales-shaped. Use as evidence of pattern *circulation*, not measured outcomes. [HIGH on framing]

### Decision relevance
- Control plane: **SECONDARY** (orchestration thesis)
- Information substrate: **SECONDARY** (context-engineering thesis)
- Action surface: **TANGENTIAL**
- Operational discipline: **TANGENTIAL**
- Deployment surface: **TANGENTIAL**

### Citation strength
**MODERATE** — channel-level metadata and theme attribution verified; specific subscriber count comes from a third-party listing (Developer Educators) consistent with the brief.

---

## §7.E4 — YouTube @ColeMedin (companion to E2)

### Identification
- **Source name:** Cole Medin — YouTube channel
- **Stratum tags:** E (companion entry)
- **Maintainer:** Cole Medin (Founder, Dynamous AI)
- **Primary URL:** `https://www.youtube.com/@ColeMedin/videos`
- **Channel page (shorts variant):** `/shorts` listing reflects "@ColeMedin • 202K subscribers • 259 videos" [HIGH]
- **Companion to:** coleam00 GitHub repos (E2)
- **Cross-reference to prior project substrate:** NONE direct.

### Recurring themes (3 distilled)
1. **Build-along masterclass format.** "AI Agents Masterclass" series with companion code in dedicated GitHub repo; videos walk through end-to-end agent builds. [HIGH]
2. **Workflow-engine / harness-builder advocacy.** Channel is the primary marketing surface for Archon and the framing "the AI layer concept, the PIV loop, and 15 reusable Claude Code commands" from the Principles of Agentic Engineering workshop. [HIGH]
3. **Local-first + practical RAG / second-brain bootcamp.** Recurrent emphasis on local AI deployment, persistent memory, and second-brain patterns; Channel header lists `dynamous.ai/second-brain-bootcamp`. [HIGH]

### Representative video citations
- "Introducing Archon - The Revolutionary Operating System for AI Coding" — `https://www.youtube.com/watch?v=8pRc_s2VQIo` (anchor video for Archon).
- "Build Your Own AI Agents With Archon - Complete Setup Guide 2025" (community video referencing Cole's introductory video at `https://www.youtube.com/watch?v=GjR5UsVGE60` — note that the GjR5UsVGE60 link is the canonical Cole-authored Archon introduction).

### V3 framing compatibility
| Dimension | Verdict |
|---|---|
| Persona-neutral | PASS |
| Stack-neutral | PARTIAL (Claude Code-heavy in current Archon era) |
| Deployment-surface-flexible | PASS (local-first emphasis) |
| Multi-LLM | PARTIAL |
| Production-grade discipline | PASS |

### Integration considerations
- **Adoption mode:** Reference media; pair with E2 repos.
- **Marketing layer:** Dynamous course/community sits behind several videos — strip sales framing when extracting patterns.

### Critical assessment
- 202k subscribers per channel header observation is materially larger than channel-meta from earlier capture (likely growth between research snapshots). Treat the metric as the most-recent observation, not a fixed fact. [HIGH on observed value; MODERATE on its stability]
- Same self-promotion caveat as E3. [HIGH on framing]

### Decision relevance
- Control plane: **SECONDARY** (workflow-engine thesis)
- Information substrate: **SECONDARY** (PRP / context-engineering thesis)
- Action surface: **TANGENTIAL**
- Operational discipline: **TANGENTIAL**
- Deployment surface: **SECONDARY** (local-first thesis)

### Citation strength
**MODERATE** — channel metadata, theme attribution, and representative video URLs verified this session.

---

# §8. Stratum F — Knowledge Aggregators (abbreviated schema)

Stratum F catalogs aggregator artefacts: pointers to other patterns rather than pattern sources themselves. Treatment is reference-only — single paragraph for what's pointed at, single sentence for design-phase utility.

## §8.F1 — ai-boost/awesome-harness-engineering

**Identification.** Source: *Awesome Harness Engineering*. Stratum: F (knowledge aggregator). Maintainer: ai-boost. Primary URL: `https://github.com/ai-boost/awesome-harness-engineering`. Last meaningful activity: very active — within ~3 days of observation date, multilingual READMEs (DE/EN/ES/FR/JA/KO/PT/RU/中文) [HIGH].

**Pattern source context.** Curated index of AI-agent harness-engineering tools, patterns, evals, memory, MCP, permissions, observability, and orchestration resources. Catalogued because it consolidates citations the project would otherwise gather one-by-one — including canonical OpenAI, Anthropic, Google, and Martin-Fowler-blog harness essays (e.g., the Microsoft Azure SRE Agent case study; Birgitta Böckeler's harness-engineering write-up; Anthropic's Claude Agent SDK docs; LiteLLM, LangGraph, OpenAI Agents SDK).

**Patterns extracted (abbreviated).** This aggregator points at categories rather than individual patterns: (a) production-harness reference architectures and case studies (Azure SRE Agent reducing time-to-mitigation from 40.5h → 3min over 35,000+ incidents; Symphony/Maestro v2-style); (b) harness-as-code generators (revfactory/harness, raphaelchristi/harness-evolver); (c) academic-leaning harness theory pieces (Knowledge Objects; ERR — Expected Recovery Regret); (d) infrastructure layer pieces (LiteLLM, LangGraph, OpenAI Agents SDK); (e) Anthropic Agent SDK + MCP tooling. The aggregator's frame is consistent with this project's: **harness as the engineered substrate around an LLM**, distinct from the model and from individual agent applications.

**Decision relevance.** Use this aggregator at the start of synthesis matrix construction (§10/§11) to confirm that no production-grade harness pattern in current circulation has been missed; do not lift content from it as primary citation.

**Citation strength.** **HIGH** — README content directly verified this session.

---

## §8.F2 — meleantonio/ChernyCode

**Identification.** Source: *ChernyCode*. Stratum: F (knowledge aggregator). Maintainer: Antonio Mele (meleantonio). Primary URL: `https://github.com/meleantonio/ChernyCode`. Last meaningful activity: Active, March 2026 (per task brief and repo presence on 2026-04 GitHub-trending list) [HIGH].

**Pattern source context.** Template repo packaging Boris Cherny's (creator of Claude Code) Claude Code workflow recommendations into a forkable starting point: `CLAUDE.md` and `AGENTS.md` memory/instruction files; project-scoped `.cursor/skills/` and `.cursor/agents/`; personal-scope `claude_personal_skills/`, `claude_subagents/`, `cursor_personal_skills/`, `cursor_subagents/` with copy-script install. Source material is `threads.md` containing two Boris Cherny X threads. Catalogued as a worked example of methodology — it's not a pattern source, it's a reference implementation of patterns published informally by the Claude Code team.

**Patterns extracted (abbreviated).** This aggregator points at: (a) `CLAUDE.md`-as-team-shared-living-rules-file pattern; (b) parallel session pattern (3–5 Claude sessions, one per task, via `git worktree`); (c) plan-then-implement separation with a "staff engineer reviewer" Claude reviewing the plan; (d) skills-as-`/skill-name`-invocations and subagents-as-specialists across both Claude Code and Cursor with parallel directory layouts. The repo is itself markdown — its value is as a copy-able starting layout, not a runtime.

**Decision relevance.** Use as a concrete reference layout when designing the project's memory/skill/subagent file conventions; useful particularly as evidence that the same pattern shape ports cleanly between Claude Code and Cursor with directory-name translation.

**Citation strength.** **HIGH** — README and threads.md content verified this session.

---

# §9. Stratum G — Approach Experiments

Stratum G catalogs small-scope architectural experiments — projects that take a single architectural bet (planning algorithm; deployment substrate) further than mainstream harnesses, and whose value is the bet itself even if the project around it is research-stage or aspirational. Both entries below are deliberately distinct from app-level harnesses.

## §9.G1 — ruvnet/ruflo

### Identification
- **Source name:** RuFlo (formerly / aliased as Claude-Flow)
- **Stratum tags:** G (primary)
- **Maintainer / author:** ruvnet (rUv) / Agentics Foundation
- **Primary URL:** `https://github.com/ruvnet/ruflo`
- **Distribution:** npm `ruflo` package; installer at `https://cdn.jsdelivr.net/gh/ruvnet/ruflo@main/scripts/install.sh`; `claude-flow` and `@claude-flow/cli` aliased packages [HIGH]
- **License:** Not directly verified this session [MODERATE]
- **Last meaningful activity:** Releases dated through observation window — v3.6.10 with 32-plugin release notes; v3.6.4 added `ruflo-goals` plugin (GOAP); active within ~2 days of observation date [HIGH]
- **Star count:** Wiki shows 46.1k stars / 5.1k forks (one snapshot) and 20.5k stars / 2.3k forks on a Goal Module wiki page snapshot — wide variation across mirror snapshots; the trajectory is into the tens of thousands. [MODERATE — exact number snapshot-dependent]
- **Cross-reference to prior project substrate:** NONE

### Pattern source context
- **Discovery context:** Surfaced as the canonical example of GOAP-style (Goal-Oriented Action Planning) **A\* planning over preconditions/effects** applied to LLM agent orchestration — a concrete bet on classical-AI planning techniques rather than pure LLM-loop orchestration.
- **Stated thesis:** "Enterprise-grade AI orchestration platform … combining hive-mind swarm intelligence, neural pattern recognition, and 87 advanced MCP tools" — operationally, RuFlo is a Claude-Code plugin + CLI + MCP server with 100+ specialised agents, hierarchical/mesh swarm topologies, persistent memory (AgentDB + ReasoningBank), and a GOAP planner module reachable at `goal.ruv.io`. [HIGH]
- **Architectural altitude:** **Approach experiment** — the architectural bets (GOAP, federation, anti-drift defaults, swarm-bench evaluation harness) are research-substrate altitude inside a production-shipping plugin.

### Patterns extracted
1. **GOAP A\* planning module.** Plain-English goals are converted into executable agent plans with adaptive replanning and multi-step reasoning; the agent definition is a single `goal-planner.md` file with all GOAP capability folded into the agent definition (no separate config). *Documented in:* `Goal Module` wiki page. [HIGH] *Axes:* Control plane (PRIMARY); Information substrate (SECONDARY).
2. **Hive-mind topologies (queen-led + mesh).** "Coordinated Agent Teams" run unlimited agents simultaneously in either hierarchical (queen/workers) or peer-to-peer (mesh) patterns, sharing context and dividing work automatically. *Documented in:* USERGUIDE.md. [HIGH] *Axes:* Control plane (PRIMARY).
3. **Anti-drift defaults + spec-first compliance.** Ruflo V3 ships defaults that prevent agents from going off-task, plus an ADR + DDD-bounded-context compliance enforcer that runs as agents work. *Documented in:* USERGUIDE.md. [HIGH] *Axes:* Operational discipline (PRIMARY).
4. **Federation across machines/orgs.** "Zero-trust federation — agents across machines/orgs discover, authenticate, and exchange work securely." Pluggable as `/plugin install ruflo-federation@ruflo`. [HIGH on stated capability] *Axes:* Deployment surface (PRIMARY); Action surface (SECONDARY).
5. **swarm-bench / SWE-bench integration.** Built-in evaluation harness running both internal swarm-bench and the public SWE-bench (300-instance lite full evaluation). The README claims "84.8% SWE-Bench solve rate, 2.8–4.4× speed improvement." *Documented in:* root README. [HIGH on quote; **see critical assessment below**] *Axes:* Operational discipline (PRIMARY).
6. **Cryptographic install verification.** `ruflo verify` is described as a step that "cryptographically prove[s] your installed bytes match the signed witness." [HIGH on stated capability] *Axes:* Deployment surface (SECONDARY); Operational discipline (SECONDARY).

### V3 framing compatibility
| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | **PASS** | Patterns are general; specific agents (coder/tester/reviewer) are configuration, not requirement. |
| Stack-neutral | **FAIL** | Claude-Code-plugin-bound. |
| Deployment-surface-flexible | **PARTIAL** | Local CLI + MCP + Claude-Code-plugin + federation; not cleanly hostable inside arbitrary harnesses. |
| Multi-LLM | **PARTIAL** | "LLM Providers (Claude, GPT, Gemini, Cohere, Ollama)" mentioned in the architecture diagram — provider abstraction at the bottom of the stack. |
| Production-grade discipline | **PARTIAL** | Anti-drift, swarm-bench, cryptographic verify are real; some claims (below) are aspirational. |

### Integration considerations
- **Adoption mode:** Pattern study only — extract GOAP-as-planner, hive-mind topology shapes, anti-drift discipline, federation framing.
- **License:** Unverified this session; assume permissive given npm distribution but **confirm before any code lift**. [SPECULATIVE]
- **Effort:** LOW to study; HIGH to disentangle a single pattern from the integrated plugin runtime.

### Critical assessment
- **"Self-learning swarm intelligence" and similar superlatives are aspirational.** README marketing copy ("revolutionizes," "enterprise-grade," "Truth Verification System with 0.95 accuracy threshold," "Training Pipeline that improves agent performance over time") is in advance of independently verified evidence. **FLAG: cite ruflo as architectural pattern source, not as performance benchmark.**
- **"84.8% SWE-Bench solve rate" claim — author-asserted, not third-party-replicated this session.** The README provides commands to reproduce (`swarm-bench swe-bench official --lite`); third-party replication is not located in this session's evidence. **FLAG.**
- **"v4 in progress" and rapid version churn (v3.5.x, v3.6.x with frequent fix releases) imply substantial in-flight architectural change.** Pattern stability is not guaranteed. [HIGH on observation]
- **Aliasing (ruflo / claude-flow / @claude-flow/cli) creates citation hazards.** Use the canonical `ruvnet/ruflo` repo URL.

### Decision relevance
- Control plane: **PRIMARY** (GOAP planner; hive-mind topologies)
- Information substrate: **SECONDARY** (AgentDB + ReasoningBank persistent memory)
- Action surface: **SECONDARY** (MCP server; federation)
- Operational discipline: **PRIMARY** (anti-drift; swarm-bench; verify)
- Deployment surface: **SECONDARY** (federation; multiple install paths)

### Citation strength
**HIGH** on README, USERGUIDE, releases, and Goal Module wiki content verified this session; **MODERATE** on quantitative claims; **SPECULATIVE** on license and on benchmark replicability.

---

## §9.G2 — humanlayer/agentcontrolplane (ACP)

### Identification
- **Source name:** Agent Control Plane (ACP)
- **Stratum tags:** G (primary)
- **Maintainer / author:** HumanLayer (same org as §5.D1)
- **Primary URL:** `https://github.com/humanlayer/agentcontrolplane`
- **License:** **Apache-2.0** (verified directly in repo footer and pkg.go.dev license metadata) [HIGH]
- **Last meaningful activity:** Repo is **archived** per humanlayer org repos page (`Public archive`) with last-update July 2025; the README remains the canonical reference for the K8s-operator-as-harness pattern. **FLAG: project status is archive — the pattern is reference, not active dependency.** [HIGH]
- **Star count / language:** ~389–399 stars, 57 forks, **Go**, per cross-snapshot consistency [HIGH]
- **Cross-reference to prior project substrate:** NONE — but adjacent to §5.D1 (same organisation; orthogonal architectural altitude)

> **Distinction from `humanlayer/humanlayer`.** The `humanlayer/humanlayer` repo (10.7k stars, TypeScript) is an **in-process SDK** for HITL approval workflows over Slack/email — it is *not* catalogued in this session. ACP is a **Kubernetes operator** with CRDs for LLMs, Agents, Tools, and Tasks; the two artefacts share a thesis but operate at different architectural layers. Catalog citations must distinguish them.

### Pattern source context
- **Discovery context:** Surfaced as the cleanest reference for the **K8s-operator-as-harness** pattern: agent execution modelled as Custom Resources, durable async/await built into the infrastructure layer, and HITL surface implemented as a mesh-pattern `ContactChannel` CRD.
- **Stated thesis:** ACP is "a distributed agent scheduler optimized for simplicity, clarity, and control. It is designed for outer-loop agents that run without supervision, and make asynchronous tool calls like requesting human feedback on key operations. Full MCP support." [HIGH]
- **Architectural altitude:** **Approach experiment** — at infrastructure-platform altitude, distinct from app-level harnesses.

### Patterns extracted
1. **Agent execution as CRDs.** Four primary kinds: `LLM`, `Agent`, `Tool`, `Task`, all under `acp.humanlayer.dev/v1alpha1`. A Task references an Agent which references an LLM and Tools; each is a first-class Kubernetes object with `spec`/`status` and reconciliation. Validation is delegated to controller reconciliation — `Status: Ready` with detail "All dependencies validated successfully." *Documented in:* README "Getting Started" walkthrough. [HIGH] *Axes:* Control plane (PRIMARY); Deployment surface (PRIMARY).
2. **Durable async/await at the infrastructure layer.** ACP "implements something like async/await at the infrastructure layer, checkpointing a conversation chain whenever a tool call or agent delegation occurs, with the ability to resume from that checkpoint when the operation completes." This is the architectural counter-position to in-process loops. *Documented in:* README "Key Features." [HIGH] *Axes:* Control plane (PRIMARY); Operational discipline (PRIMARY).
3. **Observable control loop.** "Simple, observable control loop architecture" with `kubectl get events --watch` as the canonical operator-debugging surface; reconciliation events (Initializing, ValidationSucceeded) become the primary observability stream. *Documented in:* README tutorial. [HIGH] *Axes:* Operational discipline (PRIMARY).
4. **Dynamic workflow planning at runtime.** Agents can "reprioritize and replan their workflows mid-execution" — the planning surface is part of the agent CRD lifecycle, not buried in prompt context. [HIGH on stated capability] *Axes:* Control plane (PRIMARY).
5. **Outer-loop agent framing.** Explicit positioning for unsupervised long-running agents that asynchronously request human input — the inverse of an interactive REPL/CLI agent. The pattern is distinct from in-process harnesses and informs the project's stance on whether the harness is process-bound or platform-bound. [HIGH] *Axes:* Action surface (PRIMARY); Deployment surface (SECONDARY).

### V3 framing compatibility
| Dimension | Verdict | Rationale |
|---|---|---|
| Persona-neutral | **PASS** | Operator-level pattern; persona is configuration of an Agent CR. |
| Stack-neutral | **PASS at pattern level**, **FAIL at runtime** | The pattern (control-loop CRDs) is stack-neutral; the runtime requires Kubernetes. |
| Deployment-surface-flexible | **PARTIAL** | Designed for K8s; local kind clusters work but the pattern presumes cluster-shaped deployment. |
| Multi-LLM | **PASS** | LLM CR is parameterised by provider (`openai`, "Anthropic and other providers — see Using other language models"); secrets-from-secretRef pattern. |
| Production-grade discipline | **PASS** | Durable checkpointing and observable reconciliation are core, not bolted on. |

### Integration considerations
- **Adoption mode:** **Architectural reference, not dependency** — the project's working scope keeps deployment-surface options open (local-dev as design-time target without committing to local-first), and ACP is at a fundamentally different layer. The patterns (CRDs as agent state, async/await at infrastructure, observable reconciliation) are extractable to a non-K8s host with effort.
- **Repo status:** Archive (last update Jul 2025). Treat as preserved reference, not actively maintained code.
- **License (Apache-2.0):** Permits derivative pattern documentation and code lift.
- **Effort:** LOW to study; HIGH to port to a non-K8s harness.

### Critical assessment
- **Archive status is real and matters.** The pattern is published; the project is not actively shipping. If the harness project's deployment-surface decision later includes K8s, ACP is the reference; if the project commits to non-K8s deployment, ACP remains useful as architectural mirror but should not be cited as a live dependency.
- **The "outer-loop agent" framing is HumanLayer-specific vocabulary** (paired with their in-process `humanlayer/humanlayer` SDK for inner-loop HITL). Do not over-load the term outside that context.
- **No third-party benchmarks in this session.** [SPECULATIVE on production performance]

### Decision relevance
- Control plane: **PRIMARY** (CRDs as state, durable checkpointing, observable control loop)
- Information substrate: **SECONDARY** (CR `spec`/`status` separation as substrate pattern)
- Action surface: **PRIMARY** (outer-loop async tool calls; HITL as ContactChannel CR)
- Operational discipline: **PRIMARY** (reconciliation events as observability stream)
- Deployment surface: **PRIMARY** (K8s-operator-as-harness *is* the deployment-surface choice)

### Citation strength
**HIGH** — README walkthrough, license, Apache-2.0 footer, contributors page, and archive-status badge all directly verified this session.

---
# §10. Cross-source pattern matrix

This matrix clusters recurring patterns across the 36 catalog entries documented in Sessions A–E (the task brief's "32 unique entries" is an arithmetic miscount of the explicit per-stratum breakdown — see §11.1 for the row reconciliation). Patterns are organized by the five harness axes. Source clustering uses the source's own terminology where convergent; descriptive names where sources differ in vocabulary for what is structurally the same pattern. Convergence notation: **C** = sources agree on shape and implementation contract; **D** = sources implement the pattern with materially different mechanics (the divergence is the design-decision space). Multi-axis patterns are listed under their dominant axis with cross-axis pointers.

## §10.1 Patterns by axis: Control plane

**P-CP-1. Plan/Act mode duality with separable model bindings.** A read-only planning mode that produces a structured plan, followed by an executing mode that actuates the plan; planner and executor may bind to different model tiers. Sources: Cline (`StateManager` Mode = "plan"|"act"; `planActSeparateModelsSetting`); Roo Code (Architect/Code/Debug/Ask multi-mode with per-mode model binding); kilocode (Mode system + Orchestrator + Agent Manager); Anthropic two-prompt harness pattern (initializer + executor) is the upstream methodology referenced by 12-Factor F8. **C** on the plan-then-execute split; **D** on whether plan is read-only (Cline yes; kilocode partial; Roo Code per-mode tool restriction).

**P-CP-2. Supervisor + sub-agent delegation as `task` tool.** A lead/supervisor agent delegates bounded work to ephemeral sub-agents through a structured tool call carrying an objective, output-format contract, tool whitelist, and resource budget. Sources: deepagents (`SubAgentMiddleware` + `task` tool returning to LangGraph subgraph); DeerFlow (lead-agent + middleware + sub-agent delegation, concurrency cap = 3); VoltAgent (Supervisor / Sub-Agent runtime); 12-Factor (Factor 10 — small, focused agents); revfactory (six topology patterns: Pipeline / Fan-out-Fan-in / Expert Pool / Producer-Reviewer / Supervisor / Hierarchical Delegation); disler (SFA-as-tool composition); oh-my-openagent (Sisyphus orchestrator + Hephaestus / Oracle / Librarian / Explore / Atlas / Prometheus / Metis); ruflo (hive-mind topologies: queen-led + mesh); Kode-Agent (multi-agent room); openrig (rig send / broadcast / chatroom). **C** on the brief-as-contract shape (objective + tools + budget); **D** on isolation mechanism (in-process middleware in deepagents; subprocess in disler SFA; tmux pane in openrig; subgraph in deepagents; LangGraph subgraph isolation in deepagents).

**P-CP-3. Filesystem-as-orchestrator.** Numbered folders encode stage sequencing; per-folder context files encode stage contracts; folder hierarchy encodes context scope; on-disk artifacts encode state and inter-stage handoff. Sources: ICM paper (numbered stages + plain-text context files); ICM repo / RinDig (workspace-builder + 15-convention spec); Meta-Harness paper (filesystem 𝒟 as the search space). **C** across all three on filesystem as the coordination primitive; **D** on operator-cost — ICM is manual + human-reviewed, Meta-Harness is automated outer-loop search.

**P-CP-4. Outer-loop optimization of inner harness.** A meta-loop searches over harness configurations (prompts, tool sets, behavioral rules) using inner-loop benchmark performance as the optimization signal; the inner harness is the artifact being optimized. Sources: Meta-Harness paper (Algorithm 1; TerminalBench-2 = 76.4% on Opus 4.6); Meta-Harness reference impl; Meta-Harness TBench2 artifact (the optimized leaf harness). **C** within the Stanford IRIS lineage; no external sources implement this pattern in the catalog.

**P-CP-5. Dual control primitives — declarative workflow + supervisor agent.** Two orthogonal control-plane primitives co-exist: a declarative workflow / DAG for predictable multi-step automations, and a supervisor agent for dynamic task routing. Sources: VoltAgent (Workflow Engine + Supervisor / Sub-Agent runtime, both composable); Dify (visual workflow + Agent Strategies + Supervisor mode + Human Input node); coleam00 / Archon (workflow YAML DAG with loop nodes); Trellis (task graph with parent-child subtasks + lifecycle hooks). **C** on the dual-primitive shape; **D** on which primitive owns multi-agent coordination — VoltAgent assigns multi-agent to the Supervisor; Dify assigns it to the workflow.

**P-CP-6. Multi-process / topology-managed orchestration (tmux or pod-tier).** The harness manages a topology of multiple OS processes or pods rather than a single in-process loop, with explicit messaging between participants. Sources: openrig (tmux-based; YAML RigSpec; rig send / broadcast / chatroom); ruflo (federation + hive-mind across machines/orgs); paperclip (multi-tenant agent companies). **D** on the substrate — openrig binds to tmux, ruflo to MCP federation, paperclip to embedded Postgres. The pattern is the bet on multi-process; the mechanics diverge.

**P-CP-7. K8s operator as control plane.** Agent execution is modelled as Custom Resources reconciled by a controller; durable async/await is implemented at the infrastructure layer. Sources: ACP (Agent / LLM / Tool / Task / ContactChannel CRDs); optio (Kubernetes-native; one long-lived pod per repo + reconciliation controller). **C** within the K8s-native subset; **D** on whether HITL is a CRD (ACP `ContactChannel`) or a UI primitive (optio inbox).

**P-CP-8. Stateless reducer / launch-pause-resume control flow.** The agent is `(context, event) → next_step`; durability lives below the agent; runs are interruptible operations exposed over standard APIs. Sources: 12-Factor (Factors 6, 8, 12); ACP (CRDs persist agent state across restarts); Cluster 5 V2 F3. **C** on the principle; **D** on substrate — 12-Factor is methodology-only; ACP is K8s-bound.

**P-CP-9. Mode/role specialization with model temperament binding.** Distinct agent roles are bound to distinct models chosen for temperament fit, not just capability tier. Sources: Cline (separate plan/act models); Roo Code (per-mode model binding with cost-tier optimization); oh-my-openagent (role specialization by model temperament: Sisyphus on Claude, Oracle on Gemini); deepagents (harness profiles per provider with system-prompt prefixes/suffixes); pi-mono (`~/.pi/agent/models.json` JSONC custom-provider config). **C** on the binding mechanism; **D** on configuration grain — Cline binds at mode level, oh-my-openagent at role level, deepagents at provider level.

**P-CP-10. Classical-AI planning over LLM action selection.** A non-LLM planner (A*, GOAP, ADR/DDD compliance enforcer) generates the plan; the LLM fills in execution intelligence per step. Sources: ruflo (GOAP A* over preconditions/effects in `goal-planner.md`); coleam00 / Archon (workflow-as-Dockerfile-equivalent — predetermined phases). **D** on planner type — ruflo is search-based, Archon is author-defined.

**P-CP-11. Agent-companies-as-deployment-unit.** The deployment unit is the *organization* (orgs, roles, budgets, goals, governance), not the agent process or pod. Sources: paperclip (every entity is company-scoped; multi-tenant on local/Tailscale). Singleton in catalog; no convergence/divergence to note.

## §10.2 Patterns by axis: Information substrate

**P-IS-1. Filesystem-as-shared-substrate.** Agent state, intermediate artifacts, and reusable capabilities live on the filesystem; the harness coordinates over the filesystem rather than replacing it. Sources: ICM paper (five-layer hierarchy L0–L4); ICM repo (selective section routing); Meta-Harness paper (filesystem 𝒟); DeerFlow (skills/ + soul + memory directory layout); pi-mono (serializable Context + JSONL session); 12-Factor (Factor 5 unify execution+business state); Trellis (`.trellis/` skeleton: spec/ tasks/ workspace/); coleam00 / Archon (PRP + CLAUDE.md + examples); ChernyCode (CLAUDE.md / AGENTS.md memory layout); kilocode (Memory Bank); disler (single-file-agents); Cluster 5 V2 F2 foundational. **C** on the substrate commitment; **D** on schema — ICM mandates a five-layer hierarchy with token budgets; 12-Factor mandates only that the thread+context contains all state; Trellis and ICM are most prescriptive, 12-Factor and Anthropic's progress-file pattern are loosest.

**P-IS-2. Markdown-spec-driven configuration.** Agent definitions, skills, prompts, and stage contracts are authored as Markdown with YAML frontmatter or convention-defined headings, not as code. Sources: ICM (CONTEXT.md per stage; `_core/CONVENTIONS.md`); 12-Factor (`content/factor-NN-*.md`); Maestro (commands as Markdown with audit/decision/effectiveness panels); Agency-Agents (147 personas across 12 divisions, all Markdown); RevFactory (`.claude/agents/` + `.claude/skills/` Markdown emission); Trellis (`.trellis/` is filesystem + Markdown); ChernyCode (CLAUDE.md / AGENTS.md / threads.md); disler / the-library (skills as Markdown); deepagents (`AGENTS.md` MemoryMiddleware loads). **C** on the format; **D** on what the Markdown encodes — workflow commands (Maestro), personas (Agency-Agents), team architectures (RevFactory), stage contracts (ICM).

**P-IS-3. Five-layer context hierarchy with token budgets.** Layered context loading from identity (L0) through workspace (L1), stage (L2), reference material (L3), to working artifacts (L4), with explicit per-layer token budgets summing to 2,000–8,000 tokens vs the 30,000–50,000-token monolithic baseline. Sources: ICM paper (formal specification, Figure 1); ICM repo (selective section routing operationalizes L2/L3); Cluster 2 substrate (context-rot research). **C** within ICM; the layered idea recurs in 12-Factor (Factor 3) and Trellis (workspace + tasks + specs separation), but without the formal token-budget table.

**P-IS-4. Hash-anchored edit protocol.** Each line is tagged with a content-hash anchor; the model references anchors instead of reproducing text; hash mismatch rejects the edit before file corruption. Sources: oh-my-pi (Hashline `LINE:HASH`; benchmark: Grok Code Fast 1 from 6.7% → 68.3%); ported into oh-my-openagent (commit `206dc8c`). **C** within the lineage; the cross-harness port is direct evidence of pattern transferability.

**P-IS-5. Time-Traveling Streamed Rules (TTSR).** Rules carry a regex trigger; the harness watches the model's output stream and aborts/injects/retries when a trigger matches; rules consume zero tokens until matched. Sources: oh-my-pi (origin); oh-my-openagent (ported via the same `206dc8c` commit). **C** across the two, no divergence.

**P-IS-6. Repo-as-memory / persistent project memory.** A long-lived in-repo memory store — distinct from session state — that survives sessions and accretes project-specific facts. Sources: kilocode (Memory Bank); coleam00 (PRP + second-brain + context-engineering-intro); ruflo (AgentDB + ReasoningBank persistent memory); Trellis (`workspace/<user>/` per-developer journals). **D** on storage mechanism — kilocode and coleam00 use Markdown files; ruflo uses an embedded DB; Trellis uses a hybrid.

**P-IS-7. Provider profiles / harness profiles as declarative override layer.** Per-model-family overrides for system-prompt prefixes/suffixes, tool inclusion, naming, middleware selection, subagent config, skills — declarative, not coded. Sources: deepagents (Anthropic / OpenAI built-ins; tau2-bench: GPT-5.3 Codex 33→53, Opus 4.7 43→53; third-party plugin via entry points); OpenHarness (provider profiles with auto-compaction). **C** on the override-layer pattern; **D** on registration — deepagents uses Python entry points, OpenHarness uses config files.

**P-IS-8. AGENTS.md / CLAUDE.md memory loading.** A standardized root-level Markdown file that the harness auto-loads as identity/instruction memory. Sources: deepagents (`MemoryMiddleware` loads AGENTS.md per AAIF standard); ChernyCode (parallel CLAUDE.md and AGENTS.md); disler (CLAUDE.md present in single-file-agents and infinite-agentic-loop); coleam00 (CLAUDE.md + claude-code-full-guide). **C** on the convention name post-AAIF donation (December 2025).

**P-IS-9. Selective section routing in stage contracts.** Stage `CONTEXT.md` Inputs table specifies *which sections* of which files to load, not whole files. Sources: ICM repo (formal specification); Trellis (workspace tasks reference specific spec sections); revfactory (Progressive Disclosure skills load detail on demand). **C** on the principle (load less, load specifically); **D** on routing grain.

**P-IS-10. Multi-LLM provider abstraction.** A unified API normalizes streaming events, tool-call schemas, and cross-provider context handoff across heterogeneous model APIs. Sources: pi-mono (10 protocol adapters, normalized streaming events, cross-provider handoff "best-effort"); Cline (30+ providers); 12-Factor (multi-provider env in `create-12fa-agent`); Trellis (14 host platforms); kilocode (provider abstraction); openrig (Claude Code + Codex pods); OpenHarness (Anthropic / OpenAI / Moonshot / MiniMax / Gemini / Ollama / OpenAI-compat); DeerFlow (Doubao-default with multi-provider support); Cluster 5 V2 F1 foundational. **C** on the abstraction's necessity; **D** on protocol choice — pi-mono is normalized-event; Cline is per-provider adapter; Trellis is fan-out-to-hosts.

**P-IS-11. Catwalk pattern / multi-source context files.** Multiple distinct context files (project rules, user rules, team rules) merged at load time with explicit precedence ordering. Sources: crush (Catwalk); oh-my-openagent (hierarchical config: pwd → user config → defaults via Zod `safeParse` with deep-merge for objects, Set union for `disabled_*` arrays, prototype-pollution safe). **C** on the layered-config principle; **D** on merge semantics — oh-my-openagent specifies prototype-pollution-safe deep-merge, crush is less explicit.

## §10.3 Patterns by axis: Action surface

**P-AS-1. Sandbox isolation with per-tool trust tiers.** Untrusted LLM-generated code runs in microVM / vendor-managed sandbox; deterministic tools run in lighter isolation; isolation strength is a property of the *tool*, not the *harness*. Sources: OpenHands (Docker-based agent-server, separate process); DeerFlow (`LocalSandboxProvider` default + `AioSandboxProvider` for shell access); deepagents (`CompositeBackend` with Modal / Daytona / Deno backends; sandbox gates `execute` shell tool); Dify (dify-sandbox under separate license); kilocode (git-worktree isolation via Agent Manager); oh-my-pi (worktree / fuse-overlay / fuse-projfs platform-tagged); disler (E2B agent-sandboxes); Kode-Agent (OpenSandbox); Cluster 5 V2 F4 foundational. **C** on per-tool trust tiering; **D** on isolation mechanism — Docker (OpenHands), microVM (E2B), worktree (kilocode/oh-my-pi), agent-server-process (OpenHands).

**P-AS-2. MCP-native tool model.** Tools and integrations are loaded as MCP servers, not in-process plugins; tool definitions, descriptions, and authentication live in MCP server contracts. Sources: goose (MCP-native, AAIF reference impl); DeerFlow (MCP integration); OpenHarness (MCP-as-client); Dify (MCP-as-client); pi-mono (MCP-extensible); kilocode (MCP); openrig (17-tool MCP self-management); ruflo (87 advanced MCP tools); paperclip (`@paperclipai/mcp-server` BETA standalone); disler / just-prompt (MCP server unifying OpenAI/Anthropic/Gemini/Groq/DeepSeek/Ollama); Maestro (MCP-server mode). **C** on protocol adoption; **D** on transport — http (most), stdio, sse (crush MCP supports all three). Near-universal adoption since AAIF donation in December 2025.

**P-AS-3. Tools-as-structured-outputs with typed schemas.** Tool definitions are schemas the LLM produces JSON against; the harness binds those structures to side effects. Sources: 12-Factor (Factors 1, 4 — natural-language→tool-calls; tools as structured outputs); pi-mono (TypeBox schemas for built-in tools); VoltAgent (Zod-typed tools); deepagents (LangGraph tool decorator); Anthropic-style strict mode (Cluster 4 substrate). **C** on the schema-first principle; **D** on schema language — TypeBox (pi-mono), Zod (VoltAgent), Pydantic (deepagents Python), JSON Schema (most).

**P-AS-4. HITL approval gates as first-class action-surface primitives.** Sensitive operations gate on explicit human approval; the approval is itself a tool call (not a separate pipeline). Sources: Cline (per-step approval gate); deepagents (HITL approval gates + filesystem access rules); ACP (`ContactChannel` CR mesh-pattern); kilocode (`allowedCommands` / `deniedCommands` lists + `--auto` for CI); Roo Code (autonomy slider Manual ↔ Auto-Approve / "BRRR"); 12-Factor (Factor 7 — contact humans with tool calls); OpenHands (per-action approval); Dify (Human Input node); disler (the-verifier-agent two-agent observer); Kode-Agent SDK (approval workflow). **C** on HITL-as-tool-call (12-Factor F7 explicit); **D** on synchrony — Cline is synchronous interactive, ACP is async via mesh CRD, kilocode supports both. Cluster 5 V2 marks D5 (HITL synchrony) as **persona-dependent**.

**P-AS-5. Hooks-as-shell-decorators / lifecycle hooks.** Pre/post hooks at tool-call boundaries (or stage boundaries) are shell scripts the harness invokes; the hook can rewrite the call, abort it, or emit observability data. Sources: crush (hooks-as-shell-decorators); disler (claude-code-hooks-mastery 13-hook lifecycle interception); Trellis (task-lifecycle hooks v0.3.6 + parent-child subtasks; hooks bracketed as Claude-Code-only for portability). **C** on shape; **D** on portability — Trellis explicitly brackets hooks as non-portable; crush hooks ship in the agent contract.

**P-AS-6. Outer-loop async tool calls.** Long-running or human-mediated tool calls return a token immediately; the loop suspends and resumes when the result lands. Sources: ACP (outer-loop design via CRDs); 12-Factor (Factor 6 launch/pause/resume); deepagents (async subagents on remote Agent Protocol servers); HumanLayer SDK (outer-loop framing). **C** on the async contract; **D** on substrate — ACP via K8s reconciliation, deepagents via Agent Protocol, 12-Factor methodology-only.

**P-AS-7. Browser/computer-use stealth tooling.** Browser automation with stealth-mode plugins (anti-detection, fingerprint evasion) as a maintained adversarial surface. Sources: oh-my-pi (14 stealth-mode browser plugins via Puppeteer); disler / bowser (composable browser automation skill). **C** on Puppeteer-based stack; oh-my-pi is the more developed implementation. Adversarial-surface upkeep is a stated cost.

**P-AS-8. Behavioral-rule encoding in system prompt.** Hard-coded per-task or per-tool behavioral rules embedded in the prompt rather than in tool descriptions or external policy. Sources: Meta-Harness TBench2 artifact (per-task behavioral rules; flagged as near-overfit risk); oh-my-pi (TTSR triggers as rules); disler / `claude-code-hooks-mastery` (rule library). **D** on overfit risk — Meta-Harness paper explicitly acknowledges per-task rules may overfit; disler's rule library is general-purpose.

## §10.4 Patterns by axis: Operational discipline

**P-OD-1. Validation gates / dry-run pre-flight.** A deterministic gate runs before the agent acts; dry-run mode validates the plan against schemas, tests, or rubrics; A/B harness compares with-and-without-skill outcomes. Sources: revfactory (trigger-verify + dry-run + A/B harness as first-class output); OpenHarness (dry-run pre-flight); Maestro (audit / decision / effectiveness triad); Cluster 5 V2 (single-threaded-writes default). **C** on validation-as-gate; **D** on what's validated — revfactory validates skill behavior, OpenHarness validates execution plans.

**P-OD-2. Spend caps and cost discipline.** Per-day / per-month / per-task spend ceilings enforced at the harness level, with explicit UI when caps trip. Sources: Cline (v3.78 April 2026: explicit "Spend Limit Reached" UI); VoltAgent ($/mo tiers in VoltOps); ruflo (cost gates in goal module). **C** on the discipline; **D** on enforcement layer — Cline at the agent-loop, VoltAgent at the platform.

**P-OD-3. Audit ledger / decision log / hash-chained provenance.** Every action and decision is logged with structured rationale; the ledger is queryable and tamper-evident. Sources: Maestro (audit log + decision log + effectiveness panel JSONL); 12-Factor (Factor 5 implies audit-as-thread); ACP (reconciliation events as observability stream); paperclip (multi-tenant audit; auto-checkout for scoped wakes); ChernyCode (markdown-as-rationale). **C** on the log-everything principle; **D** on durability — Maestro is JSONL files, ACP is K8s events, paperclip is embedded Postgres.

**P-OD-4. Checkpoint + rollback via shadow Git.** Every step writes a snapshot to a shadow Git repository; rollback navigates the snapshot timeline. Sources: Cline (shadow Git checkpoints, per-step rollback); kilocode (snapshot/diff state model + checkpoint navigation); Roo Code (checkpoint navigation controls). **C** within the Cline lineage. The pattern is essentially Git-as-undo-log.

**P-OD-5. Conventions / discipline specifications.** A named set of conventions (15-convention spec, 12 factors, AGENTS.md rules, kilocode_change marker discipline) the harness enforces or scaffolders generate compliant artifacts against. Sources: ICM repo (15 conventions: Architecture / Quality / Onboarding); 12-Factor (12 numbered factors); kilocode (`AGENTS.md` rules + kilocode_change markers); oh-my-openagent (`AGENTS.md`: write-existing-file-guard, never-as-`any`, never-bypass-lint); ChernyCode (Cherny workflow patterns); coleam00 (PIV loop + 15 reusable Claude Code commands). **C** on the discipline-as-named-set principle; **D** on enforcement — ICM and oh-my-openagent enforce in the harness; 12-Factor is documentation-only.

**P-OD-6. OpenTelemetry / OTLP export observability.** Traces forward to any OTLP-compatible backend; LLM telemetry co-emits with custom business metrics. Sources: VoltAgent (OTLP → VoltOps / DataDog / Grafana); kilocode (OpenTelemetry export); Dify (multi-vendor observability); Cluster 5 V2 D6 (deployment-surface and persona-dependent). **C** on OTLP as the protocol of choice; **D** on observability backend choice.

**P-OD-7. Cosign-signed releases / cryptographic install verification.** Release artifacts are signed and the install path verifies bytes against a signed witness. Sources: crush (Cosign-signed releases); ruflo (`ruflo verify` cryptographically proves installed bytes match signed witness). **C** within these two.

**P-OD-8. Eval harness / SWE-bench / swarm-bench integration.** A built-in evaluation harness with reproducible benchmark runs (SWE-bench, TerminalBench-2, internal swarm-bench). Sources: Meta-Harness paper (TerminalBench-2 76.4% on Opus 4.6, ranked #2 behind ForgeCode at 81.8%); ruflo (swarm-bench + SWE-bench integration; 84.8% solve-rate claim — author-asserted, not third-party-replicated). **D** on rigor — Meta-Harness publishes the optimization artifact; ruflo's claims are author-measured.

**P-OD-9. Verifier agent / two-agent review.** A second agent reviews the first's output as a clean-context reviewer (or generator-evaluator pair); the reviewer's input is disabled to prevent contamination. Sources: disler (the-verifier-agent two-agent observer with input-disabled verifier); revfactory (Producer-Reviewer / Generate-Verify topology pattern); coleam00 (GAN-inspired three-agent harness: generator vs adversarial evaluator); Anthropic clean-context-reviewer pattern (Cluster 1 substrate). **C** on the two-agent shape; **D** on whether the reviewer is structurally identical to the generator (Anthropic) or asymmetric (disler input-disabled).

**P-OD-10. Concurrency caps and recursion limits.** Hard ceilings on sub-agent fan-out, recursion depth, and total tool-call count per session. Sources: DeerFlow (sub-agent concurrency cap = 3; documented bottleneck); Anthropic research-system (3–5 subagents per fan-out, 10–15 tool calls each); 12-Factor (3–10 step ceiling implied by Factor 10); ruflo (verify gate); Cluster 1 substrate. **C** on the principle; **D** on cap value — DeerFlow at 3, Anthropic at 5, 12-Factor at 10.

**P-OD-11. Encrypted-secrets-at-rest with OS-keychain abstraction.** Secrets stored encrypted in dev (OS keychain), in vault in production; the harness abstracts secret-fetch across both. Sources: optio (AES-256-GCM secret encryption at rest; OIDC/OAuth); kilocode (CA-trust handling); Cluster 5 V2 F5 foundational. **C** on the dev-vs-prod abstraction; primary divergence is on transit mechanism.

**P-OD-12. Anti-drift defaults / spec-first compliance enforcer.** Enforcer agents run alongside the working agents to keep them on-task and compliant with ADR / DDD bounded contexts. Sources: ruflo (anti-drift defaults + ADR + DDD-bounded-context compliance enforcer); Trellis (workspace continuity; specs as contracts). **D** on enforcement layer — ruflo runs an enforcer agent; Trellis enforces via filesystem layout.

**P-OD-13. Append-only event stream / WAL.** Every agent action and tool-call result is appended to a WAL/event log; resume reconstructs state from the log. Sources: Kode-Agent SDK (WAL + audited tool rejections + seven-segment resume); learn-claude-code ("Bash is all you need"; minimal append-only lifecycle event stream + JSONL mailbox protocol); pi-mono (JSONL session). **C** on the WAL principle.

## §10.5 Patterns by axis: Deployment surface

**P-DS-1. Local-first design-time target.** The harness is deployed on developer-owned hardware at design time; loopback-only network exposure by default; cloud and hybrid deployment surfaces remain in scope as architectural options. Sources: ICM (explicitly local-first); ICM repo; DeerFlow (README warns "designed by default to be deployed in a local trusted environment, accessible only via 127.0.0.1"); goose (local-first, Rust core); coleam00 / local-ai-packaged (Ollama + Supabase + n8n + Open WebUI); Cluster 5 V2 framing. **C** on local-as-design-time-target; **D** on cloud-deployment posture — ICM treats cross-surface as FAIL, DeerFlow makes the production-hardening the adopter's problem.

**P-DS-2. Multi-surface delivery from a single core.** One CLI/SDK/RPC core powers many client surfaces (TUI, IDE extension, desktop, web, programmatic embed). Sources: kilocode (CLI-as-server with VS Code / JetBrains / Tauri+Electron desktop / TUI / web); goose (Rust core powers desktop / CLI / API); pi-mono (TUI / `--print` / RPC / SDK from one runtime; library-tier vs application-tier separation); VoltAgent (per-target deployment matrix); OpenHands (Agent / Agent-Server / Interface three-layer SDK). **C** on the multi-surface objective; **D** on architectural altitude — kilocode and goose are server-binary-as-engine; pi-mono is library-first.

**P-DS-3. K8s-native deployment.** Deployment substrate is Kubernetes; agent state lives in CRDs or per-repo pods; reconciliation controllers replace in-process orchestration. Sources: optio (one long-lived pod per repo + Postgres + Redis); ACP (Agent / LLM / Tool / Task / ContactChannel CRDs). **C** within the K8s subset; both treat the cluster as the durable substrate.

**P-DS-4. Local / Docker / K8s / embedded matrix.** A single harness explicitly targets multiple deployment surfaces with parity across them. Sources: DeerFlow (local + Docker + K8s + embedded library); OpenHarness (similar matrix); VoltAgent (per-target deployment matrix). **C** on the matrix-explicitness; **D** on parity — DeerFlow ships an opinionated four-process topology that is *not* surface-neutral; pi-mono is more genuinely surface-neutral.

**P-DS-5. Cross-platform meta-skill (fan-out across host harnesses).** The harness *is* the deployment-surface fan-out: it initializes its same content into platform-specific entry files for many host harnesses. Sources: Trellis (14 host platforms: Cursor / OpenCode / Codex / iFlow / Kilo / Kiro / Gemini / Antigravity / Windsurf / Qoder / CodeBuddy / Copilot / Droid / Pi); Maestro (10 hosts claimed); revfactory (Claude Code emission target); Agency-Agents (Claude Code / Cursor / Aider parallel layouts); ChernyCode (Claude Code + Cursor parallel directory layouts); disler / the-library (cross-platform skill catalog). **C** on the fan-out objective; **D** on coverage — Trellis is broadest; ChernyCode is narrowest. Multi-LLM compatibility is implied (host-agnostic = model-agnostic).

**P-DS-6. Single Go binary / multi-OS distribution.** Compiled single-binary with multi-OS coverage and configurable global vs project paths. Sources: crush (Go single binary; configurable global vs project paths); goose (Rust). **C** on the compile-once-distribute-everywhere stance.

**P-DS-7. Agent-companies multi-tenant with embedded DB.** The deployment unit is a multi-tenant company-scoped namespace running on a single embedded-DB-backed server. Sources: paperclip (Tailscale-friendly local + embedded Postgres + multi-user invite flows). Singleton in catalog.

**P-DS-8. Cross-machine / cross-org federation.** Agents discover, authenticate, and exchange work across machines/organizations via a federation protocol. Sources: ruflo ("Zero-trust federation — agents across machines/orgs discover, authenticate, and exchange work securely"; pluggable as `/plugin install ruflo-federation@ruflo`). Singleton in catalog as a stated capability.

**P-DS-9. Multi-process / tmux-as-deployment-fabric.** The deployment substrate is tmux panes orchestrating heterogeneous coding agents (Claude Code + Codex pods) as one system. Sources: openrig (RigSpec orchestration via tmux). Singleton.

**P-DS-10. K8s-managed-async-runtime as alternative to in-process loop.** Agent execution is fundamentally async (durable async/await at the infrastructure layer); the in-process agent loop is replaced by reconciliation. Sources: ACP; optio. **C** within the K8s subset.

## §10.6 Cross-axis tensions

**T1. Filesystem-as-orchestrator vs framework-orchestration.** ICM (paper + repo) and Meta-Harness commit to the filesystem as the *coordination primitive itself* — folder numbering encodes sequence, folder hierarchy encodes scope, files-on-disk encode state. deepagents, Dify, and VoltAgent commit to a framework-managed graph (LangGraph subgraphs, Dify visual workflow, VoltAgent Workflow Engine) where the filesystem is *content*, not coordinator. The tension is not framework-vs-no-framework; it is whether the *coordination logic* lives in code or in folder structure. The 12-Factor methodology splits the difference: filesystem holds business state (Factor 5), but control flow is application code (Factor 8). Cluster 5 V2 marks F2 (filesystem-as-shared-substrate) as foundational — both sides of T1 agree the filesystem is the *substrate*; they disagree on whether the filesystem is also the *control plane*.

**T2. Single-process harness vs multi-process / topology orchestration.** Cline, OpenHands, deepagents, VoltAgent run the harness as a single process; the agent loop, tools, and sub-agents are in-process modules. openrig runs the harness as a topology of OS processes orchestrated via tmux; sub-agents are full coding-agent processes (Claude Code + Codex), not in-process Python/TypeScript modules. ACP and optio extrapolate further to K8s pods. The tension surfaces under fault isolation (multi-process recovers from sub-agent crashes; single-process loses session) versus context coherence (single-process trivially shares prompt cache, working state, and observability stream; multi-process requires coordination machinery). Anthropic's clean-context-reviewer pattern (Cluster 1 substrate) and Cognition's "single-threaded writes" position (Cluster 1 substrate) sit closer to single-process; openrig and ACP sit closer to multi-process.

**T3. Per-task vs per-company deployment unit.** Most catalog entries (DeerFlow, kilocode, deepagents, OpenHands, Cline, OpenHarness) treat the deployment unit as the *task* (or session). optio extends to per-repo (one long-lived pod per repo). paperclip extends further to per-company (the *organizational structure* — orgs, roles, budgets, governance — is the deployment unit). The tension surfaces under multi-tenancy: per-task deployments can be horizontally replicated trivially; per-company deployments require company-scoping at every entity, embedded multi-tenant DB, and inter-company isolation guarantees. Cluster 5 V2 leaves multi-tenant identity as **persona-dependent** (D5).

**T4. Markdown-spec-driven vs code-driven configuration.** RevFactory, Maestro, Agency-Agents, Trellis, ICM, ChernyCode, 12-Factor, and disler / the-library encode agent definitions, skills, prompts, and workflows as Markdown. deepagents, VoltAgent, OpenHands, OpenHarness, kilocode, Dify, and pi-mono encode them as code (Python decorators, TypeScript classes, YAML schemas with code interpretation). The tension surfaces under reviewability (Markdown is human-reviewable as authored; code requires execution to inspect runtime shape) versus expressivity (code can express conditional logic, dynamic dispatch, and computed configurations that Markdown cannot). The cross-platform meta-skill cluster (P-DS-5) is exclusively Markdown-driven by necessity — Markdown is the only format every host harness reads. Multi-tag entries like Trellis (C + D-meta) sit at the intersection: filesystem + Markdown substrate, with code-driven hooks layered above where the host harness allows.

---

# §11. Decision-relevance matrix

This matrix enables selective per-decision loading during the design phase. The primary matrix (§11.1) records each catalog entry's relevance to each of the five harness axes as **PRIMARY** (directly informs decision shape), **SECONDARY** (informs but does not anchor), **TANGENTIAL** (relevant context only), or **NONE**. Per-axis recommendations (§11.2) order entries by relevance density for fastest design-phase load. Secondary mapping (§11.3) projects the matrix against the Cluster 5 V2 §3 decision-ordering DAG, with conditional dependencies (persona / workload / deployment-surface) noted where the DAG specifies them.

## §11.1 Primary matrix: sources × axes

The matrix below has 36 source rows × 5 axis columns = 180 cells. (The task brief's "32 unique entries / 160 cells" is an arithmetic miscount of the explicit per-stratum breakdown: 5 + 3 + 8 + 8 + 1 + 3 + 4 + 2 + 2 = 36; the matrix below documents what the catalog actually contains.) Cells reflect the Decision Relevance fields recorded in Sessions A–E catalog entries. Cell labels: **PRI** = PRIMARY, **SEC** = SECONDARY, **TAN** = TANGENTIAL, **—** = NONE.

| # | Source | Stratum | Control plane | Information substrate | Action surface | Operational discipline | Deployment surface |
|---|---|---|---|---|---|---|---|
| 1 | Meta-Harness paper (arXiv 2603.28052) | A | **PRI** | **PRI** | SEC | SEC | TAN |
| 2 | stanford-iris-lab/meta-harness (ref impl) | A | SEC | SEC | SEC | SEC | TAN |
| 3 | meta-harness-tbench2-artifact | A | TAN | SEC | **PRI** | SEC | TAN |
| 4 | ICM paper (arXiv 2603.16021) | A + D | **PRI** | **PRI** | SEC | SEC | TAN |
| 5 | RinDig/Interpreted-Context-Methdology | A + D | **PRI** | **PRI** | SEC | **PRI** | SEC |
| 6 | bytedance/deer-flow (DeerFlow 2.0) | B-priority | **PRI** | **PRI** | **PRI** | SEC | SEC |
| 7 | earendil-works/pi (pi-mono) | B-priority | SEC | **PRI** | SEC | SEC | **PRI** |
| 8 | Kilo-Org/kilocode | B-priority | **PRI** | SEC | SEC | **PRI** | **PRI** |
| 9 | OpenHands/OpenHands | B-standard | SEC | SEC | **PRI** | **PRI** | **PRI** |
| 10 | cline/cline | B-standard | **PRI** | **PRI** | SEC | **PRI** | SEC |
| 11 | aaif-goose/goose | B-standard | SEC | SEC | **PRI** | SEC | **PRI** |
| 12 | RooCodeInc/Roo-Code | B-standard | **PRI** | **PRI** | SEC | SEC | TAN |
| 13 | HKUDS/OpenHarness | B-standard | **PRI** | **PRI** | **PRI** | **PRI** | SEC |
| 14 | langchain-ai/deepagents | B-standard | **PRI** | **PRI** | **PRI** | SEC | SEC |
| 15 | langgenius/dify | B-standard | **PRI** | SEC | **PRI** | **PRI** | **PRI** |
| 16 | VoltAgent/voltagent | B-standard | **PRI** | **PRI** | **PRI** | **PRI** | **PRI** |
| 17 | can1357/oh-my-pi | C | SEC | **PRI** | **PRI** | **PRI** | SEC |
| 18 | jonwiggins/optio | C | **PRI** | SEC | SEC | **PRI** | TAN |
| 19 | mindfold-ai/Trellis | C + D-meta | **PRI** | **PRI** | SEC | **PRI** | **PRI** |
| 20 | code-yeongyu/oh-my-openagent | C | **PRI** | **PRI** | SEC | **PRI** | SEC |
| 21 | charmbracelet/crush | C | SEC | **PRI** | SEC | **PRI** | **PRI** |
| 22 | shareAI-lab/Kode-Agent | C | **PRI** | **PRI** | **PRI** | **PRI** | SEC |
| 23 | mvschwarz/openrig | C | **PRI** | SEC | **PRI** | **PRI** | **PRI** |
| 24 | paperclipai/paperclip | C | **PRI** | SEC | SEC | SEC | **PRI** |
| 25 | humanlayer/12-factor-agents | D | **PRI** | **PRI** | **PRI** | SEC | SEC |
| 26 | revfactory/harness (+ harness-100) | D-meta | **PRI** | SEC | TAN | **PRI** | TAN |
| 27 | sharpdeveye/maestro | D-meta | SEC | **PRI** | SEC | **PRI** | SEC |
| 28 | msitarzewski/agency-agents | D-meta | SEC | **PRI** | TAN | SEC | SEC |
| 29 | disler (body of work) | E | **PRI** | SEC | **PRI** | **PRI** | SEC |
| 30 | coleam00 (body of work) | E | **PRI** | **PRI** | SEC | SEC | **PRI** |
| 31 | YouTube @indydevdan | E | SEC | SEC | TAN | TAN | TAN |
| 32 | YouTube @ColeMedin | E | SEC | SEC | TAN | TAN | SEC |
| 33 | ai-boost/awesome-harness-engineering | F | TAN | TAN | TAN | TAN | TAN |
| 34 | meleantonio/ChernyCode | F | TAN | SEC | TAN | TAN | SEC |
| 35 | ruvnet/ruflo | G | **PRI** | SEC | SEC | **PRI** | SEC |
| 36 | humanlayer/agentcontrolplane (ACP) | G | **PRI** | SEC | **PRI** | **PRI** | **PRI** |

**Total PRIMARY weight per axis** (count of PRIMARY cells in column): Control plane = 18; Information substrate = 18; Action surface = 11; Operational discipline = 16; Deployment surface = 11.

Operational-discipline pattern density is concentrated in production harnesses (B standard + B priority); action-surface and deployment-surface densities are concentrated in entries that span multi-surface delivery (VoltAgent, kilocode, Dify, ACP, OpenHarness).

## §11.2 Per-axis recommendations

For each axis, load these catalog entries (PRIMARY relevance only), ordered by relevance density (count of PRIMARY axis tags across the entry's row, descending; ties broken by stratum maturity B > C > D > G > A > D-meta > E > F).

### §11.2.1 Control plane

For design-phase decisions on orchestration topology, control-flow patterns, sub-agent boundaries, parallelism mode, hand-off mechanics, and HITL placement, load these 18 catalog entries:

1. **VoltAgent/voltagent** (5 PRI) — Supervisor + Workflow dual primitives.
2. **HKUDS/OpenHarness** (4 PRI) — Subprocess teammate workers + provider profiles.
3. **langgenius/dify** (4 PRI) — Visual workflow + Agent Strategies + Supervisor mode.
4. **shareAI-lab/Kode-Agent** (4 PRI) — modelPointers role-routing + multi-agent room + safe-fork resume.
5. **mvschwarz/openrig** (4 PRI) — RigSpec / AgentSpec + tmux topology orchestration.
6. **mindfold-ai/Trellis** (4 PRI; multi-tag C + D-meta) — Task graph with parent-child subtasks + lifecycle hooks.
7. **humanlayer/agentcontrolplane** (4 PRI) — CRDs as state + durable checkpointing + observable control loop.
8. **bytedance/deer-flow** (3 PRI) — Lead-agent + middleware chain + sub-agent delegation.
9. **Kilo-Org/kilocode** (3 PRI) — Mode system + Orchestrator + Agent Manager with worktree isolation.
10. **cline/cline** (3 PRI) — Plan / Act mode duality with separable model bindings.
11. **langchain-ai/deepagents** (3 PRI) — Harness-on-runtime layering + middleware architecture + subagent delegation.
12. **code-yeongyu/oh-my-openagent** (3 PRI) — Sisyphus orchestrator + 11-role taxonomy + per-role fallback chains.
13. **humanlayer/12-factor-agents** (3 PRI) — Factors 6, 8, 10, 12 (own control flow + small focused agents + stateless reducer).
14. **disler (body of work)** (3 PRI) — SFA + layered architecture + parallel forking.
15. **coleam00 (body of work)** (3 PRI) — Workflow DAG + loop nodes + PIV loop.
16. **RooCodeInc/Roo-Code** (2 PRI) — Multi-mode + Orchestrator mode + per-mode autonomy slider.
17. **revfactory/harness** (2 PRI) — Six topology patterns + meta-factory layering.
18. **Meta-Harness paper / arXiv 2603.28052** (2 PRI) — Outer-loop search algorithm; ruflo (1 PRI) GOAP planner is the divergent classical-AI bet.
19. *Plus:* **ICM paper, RinDig/ICM repo** — filesystem-as-orchestrator counter-position (2 entries, 2 PRI each).
20. *Plus:* **paperclipai/paperclip** — agent-companies-as-deployment-unit (1 PRI).
21. *Plus:* **jonwiggins/optio** — three-tier task model (1 PRI).
22. *Plus:* **ruvnet/ruflo** — GOAP planner + hive-mind topologies (1 PRI).

### §11.2.2 Information substrate

For design-phase decisions on context engineering, prompt management, memory tiers, state durability, and within-turn context curation, load these 18 catalog entries:

1. **VoltAgent/voltagent** (5 PRI) — Memory layering + Vercel AI SDK.
2. **HKUDS/OpenHarness** (4 PRI) — Provider profiles + auto-compaction.
3. **shareAI-lab/Kode-Agent** (4 PRI) — Progress / Control / Monitor channel split.
4. **mindfold-ai/Trellis** (4 PRI) — Markdown-spec-driven progressive context layout.
5. **bytedance/deer-flow** (3 PRI) — ThreadState + skills + soul + memory composite.
6. **earendil-works/pi (pi-mono)** (3 PRI) — Unified LLM API + serializable Context + JSONL session + branching.
7. **cline/cline** (3 PRI) — Per-mode model binding + 30+ provider matrix.
8. **langchain-ai/deepagents** (3 PRI) — AGENTS.md memory loading + harness profiles + filesystem backends.
9. **code-yeongyu/oh-my-openagent** (3 PRI) — Hierarchical config layering with prototype-pollution-safe deep-merge.
10. **charmbracelet/crush** (3 PRI) — Catwalk pattern + multi-source context files.
11. **humanlayer/12-factor-agents** (3 PRI) — Factors 2, 3, 5, 9 (own prompts / context / unified state / compacted errors).
12. **coleam00 (body of work)** (3 PRI) — PRP + CLAUDE.md + examples discipline.
13. **RooCodeInc/Roo-Code** (2 PRI) — Multi-mode prompts with tool restrictions.
14. **can1357/oh-my-pi** (2 PRI) — Hashline + TTSR + anchor-as-context-format.
15. **ICM paper / arXiv 2603.16021** (2 PRI) — Five-layer hierarchy (L0–L4) with token budgets.
16. **RinDig/Interpreted-Context-Methdology** (2 PRI) — Selective section routing in stage contracts.
17. **sharpdeveye/maestro** (2 PRI) — Context-handshake + reference docs.
18. **msitarzewski/agency-agents** (2 PRI) — Markdown-persona-injection across hosts.

### §11.2.3 Action surface

For design-phase decisions on tool contracts, MCP boundaries, sandbox isolation, validation gates, and HITL approval surfaces, load these 11 catalog entries:

1. **VoltAgent/voltagent** (5 PRI) — Zod-typed tools + MCP integration + guardrails.
2. **HKUDS/OpenHarness** (4 PRI) — Sandbox backends + MCP HTTP transport + skills.
3. **shareAI-lab/Kode-Agent** (4 PRI) — Approval workflow + OpenSandbox-mediated execution.
4. **mvschwarz/openrig** (4 PRI) — 17-tool MCP self-management.
5. **humanlayer/agentcontrolplane** (4 PRI) — Outer-loop async tool calls + HITL as ContactChannel CR.
6. **bytedance/deer-flow** (3 PRI) — Pluggable sandbox + MCP + tool registry + messaging channels.
7. **langgenius/dify** (3 PRI) — Plugin daemon three-runtime model + MCP-as-client + sandbox.
8. **OpenHands/OpenHands** (3 PRI) — Three-layer composable SDK + sandboxed agent-server.
9. **langchain-ai/deepagents** (3 PRI) — Pluggable filesystem backends + permission rules + HITL gates.
10. **aaif-goose/goose** (2 PRI) — MCP-native extension model.
11. **humanlayer/12-factor-agents** (3 PRI) — Factors 1, 4, 7 (NL→tool-calls + tools-as-structured-outputs + contact-humans-with-tool-calls).
12. **disler (body of work)** (3 PRI) — Hooks + just-prompt + MCP servers + verifier-agent.
13. **meta-harness-tbench2-artifact** (1 PRI) — Tools-parameter pattern + behavioral-rule encoding.

### §11.2.4 Operational discipline

For design-phase decisions on validation gates, observability, audit ledger, reliability primitives, secrets handling, and discipline conventions, load these 16 catalog entries:

1. **VoltAgent/voltagent** (5 PRI) — VoltOps split + OTLP exporters.
2. **HKUDS/OpenHarness** (4 PRI) — Dry-run pre-flight + Docker isolation.
3. **shareAI-lab/Kode-Agent** (4 PRI) — WAL + audited tool rejections + seven-segment resume.
4. **Kilo-Org/kilocode** (3 PRI) — OpenTelemetry export + CA-trust + allow/deny lists + parallel-tool-calls.
5. **langgenius/dify** (3 PRI) — Multi-vendor observability + HITL node + sandbox.
6. **OpenHands/OpenHands** (3 PRI) — Docker isolation + hardened deployment guide.
7. **mindfold-ai/Trellis** (3 PRI) — Explicit portability boundaries (Claude-Code-only hooks bracketed).
8. **mvschwarz/openrig** (3 PRI) — Snapshot/restore by name + continuity policies.
9. **humanlayer/agentcontrolplane** (3 PRI) — Reconciliation events as observability stream.
10. **cline/cline** (3 PRI) — Checkpoints via shadow Git + spend caps.
11. **can1357/oh-my-pi** (3 PRI) — Isolation backends + MCP reconnect + retry chains.
12. **code-yeongyu/oh-my-openagent** (3 PRI) — Default-off Team Mode + write-existing-file-guard + telemetry.
13. **charmbracelet/crush** (3 PRI) — Cosign-signed releases + permission ordering.
14. **revfactory/harness** (2 PRI) — Trigger-verify + dry-run + A/B harness.
15. **sharpdeveye/maestro** (2 PRI) — Audit / decision / effectiveness triad.
16. **disler (body of work)** (3 PRI) — Hook guardrails + the-verifier-agent.
17. **jonwiggins/optio** (2 PRI) — Auto-resume reconciler + AES-256-GCM secret encryption + audit log.
18. **RinDig/Interpreted-Context-Methdology** (2 PRI) — 15-convention specification.
19. **ruvnet/ruflo** (2 PRI) — Anti-drift defaults + swarm-bench + verify gate.

### §11.2.5 Deployment surface

For design-phase decisions on runtime targets, deployment topology, multi-surface delivery, and cross-platform portability, load these 11 catalog entries:

1. **VoltAgent/voltagent** (5 PRI) — Per-target deployment matrix.
2. **Kilo-Org/kilocode** (3 PRI) — CLI-as-server with VS Code / JetBrains / desktop / TUI / web on one engine.
3. **langgenius/dify** (3 PRI) — License-bounded; plugin daemon supports Local/Debug/Serverless explicitly.
4. **mindfold-ai/Trellis** (3 PRI) — Cross-harness fan-out across 14 host platforms.
5. **mvschwarz/openrig** (3 PRI) — tmux-based topology.
6. **paperclipai/paperclip** (2 PRI) — Agent-companies-as-deployment-unit + Tailscale-friendly local + embedded Postgres.
7. **humanlayer/agentcontrolplane** (3 PRI) — K8s-operator-as-harness *is* the deployment-surface choice.
8. **OpenHands/OpenHands** (3 PRI) — Local-first explicitly, with cloud/VPC paths.
9. **earendil-works/pi (pi-mono)** (3 PRI) — TUI / CLI / RPC / SDK from one runtime.
10. **aaif-goose/goose** (2 PRI) — Rust-core, multi-surface delivery (desktop / CLI / embeddable API).
11. **charmbracelet/crush** (3 PRI) — Single Go binary, multi-OS, configurable global vs. project paths.
12. **coleam00 (body of work)** (3 PRI) — Multi-platform adapter + local-first packaging (`local-ai-packaged`).

## §11.3 Secondary mapping: Cluster 5 V2 §3 DAG → catalog entries

Cluster 5 V2 §3 partitions architectural decisions into foundational (F1–F5; decided now), derivative (D1–D6; deferred to design phase under foundational constraints), and independent / deferrable (I1–I3; can be added without rework). Below, each decision node is mapped to the catalog entries with PRIMARY (or, where noted, SECONDARY) relevance to that specific decision. Conditional dependencies marked in Cluster 5 V2 §3 are propagated.

### §11.3.1 Foundational decisions (F1–F5)

**F1. Multi-LLM commitment** *(foundational; given as project commitment)*. For provider-abstraction layer design, model-router design, OpenAI-compatible-or-Anthropic-native protocol choice, degraded-mode signaling, load:
- **earendil-works/pi (pi-mono)** — 10 protocol adapters with normalized streaming events; cross-provider context handoff.
- **cline/cline** — 30+ provider matrix.
- **HKUDS/OpenHarness** — Anthropic / OpenAI / Moonshot / MiniMax / Gemini / Ollama / OpenAI-compat gateways.
- **bytedance/deer-flow** — Doubao-default with multi-provider support.
- **humanlayer/12-factor-agents** — Multi-provider env in `create-12fa-agent` template.
- **mindfold-ai/Trellis** — 14 host platforms (host-agnostic implies model-agnostic).
- **mvschwarz/openrig** — Claude Code + Codex pods in same rig.
- **VoltAgent/voltagent** — Vercel AI SDK abstraction.
- **disler/just-prompt** (within disler body) — MCP server unifying OpenAI/Anthropic/Gemini/Groq/DeepSeek/Ollama.

**F2. Filesystem-as-shared-substrate** *(foundational; strongly indicated by source convergence)*. For decisions on agent-state location, intermediate-artifact persistence, and reusable-capability format, load:
- **ICM paper (arXiv 2603.16021)** — Five-layer hierarchy as directly adoptable specification.
- **RinDig/Interpreted-Context-Methdology** — Workspace-builder + 15-convention spec.
- **Meta-Harness paper (arXiv 2603.28052)** — Filesystem 𝒟 as the search space.
- **bytedance/deer-flow** — `skills/public/` + `soul.md` + memory composite.
- **humanlayer/12-factor-agents** — Factor 5 (unify execution+business state).
- **mindfold-ai/Trellis** — `.trellis/` skeleton (spec / tasks / workspace / scripts).
- **earendil-works/pi (pi-mono)** — JSONL session + serializable Context.
- **Kilo-Org/kilocode** — Memory Bank pattern.
- **coleam00 (body of work)** — PRP + CLAUDE.md + examples.
- **meleantonio/ChernyCode** — CLAUDE.md + AGENTS.md as memory layout.
- **disler (body of work)** — Single-file-agents (filesystem-resident agent).
- **sharpdeveye/maestro** — Context-handshake + reference docs.

**F3. Durable-execution-as-coordination-spine** *(foundational; substrate-TBD)*. For `step.run`-equivalent retriable-unit design, suspend/resume semantics, and the harness's posture toward managed checkpointing, load:
- **langchain-ai/deepagents** — LangGraph runtime as durable-execution layer.
- **humanlayer/agentcontrolplane** — K8s CRD-based durable async/await at infrastructure layer.
- **VoltAgent/voltagent** — Workflow Engine for declarative multi-step automations.
- **langgenius/dify** — Visual workflow engine.
- **humanlayer/12-factor-agents** — Factors 6, 12 (launch/pause/resume + stateless reducer).
- **jonwiggins/optio** — Auto-resume reconciler.
- **shareAI-lab/Kode-Agent** — Seven-segment resume; WAL.

**F4. Sandbox-isolation-strength-by-trust-level** *(foundational; isolation level is a property of the tool)*. For the per-tool isolation tier decision, load:
- **OpenHands/OpenHands** — Three-layer composable SDK; sandboxed agent-server.
- **bytedance/deer-flow** — `LocalSandboxProvider` default + `AioSandboxProvider` for shell.
- **langchain-ai/deepagents** — `CompositeBackend` with Modal / Daytona / Deno backends.
- **langgenius/dify** — dify-sandbox under separate license.
- **Kilo-Org/kilocode** — git-worktree isolation via Agent Manager.
- **can1357/oh-my-pi** — worktree / fuse-overlay / fuse-projfs platform-tagged.
- **disler / agent-sandboxes** (within disler body) — E2B-isolated parallel agent forks.
- **shareAI-lab/Kode-Agent** — OpenSandbox-mediated tool execution.

**F5. OS-keychain-at-dev / vault-at-prod for secrets** *(foundational; failure-mode-driven)*. For secret-fetch abstraction, load:
- **jonwiggins/optio** — AES-256-GCM secret encryption at rest; OIDC/OAuth.
- **Kilo-Org/kilocode** — CA-trust handling.
- **humanlayer/12-factor-agents** — Factor 3 (own your context window) implies secret-handling discipline.

### §11.3.2 Derivative decisions (D1–D6)

**D1. Specific durable-execution substrate** — *deployment-surface-dependent*; derived from F3. The choice between DBOS / Temporal / Restate / Inngest / Hatchet / LangGraph+checkpointer / Cloudflare Workflows / Bedrock AgentCore / Vertex Agent Engine cannot be committed until deployment surface is chosen. Load:
- **langchain-ai/deepagents** — LangGraph + checkpointer (DynamoDB / Postgres) reference.
- **humanlayer/agentcontrolplane** — K8s-native reconciler reference.
- **langgenius/dify** — Self-hosted workflow engine reference.
- **VoltAgent/voltagent** — Workflow Engine reference.
- **jonwiggins/optio** — K8s + Postgres + Redis self-hosted reference.

**D2. Specific sandbox provider** — *deployment-surface-dependent*; derived from F4. Load:
- **OpenHands/OpenHands** — Docker reference.
- **langchain-ai/deepagents** — Modal / Daytona / Deno backends.
- **bytedance/deer-flow** — Aio provider.
- **langgenius/dify** — dify-sandbox.
- **can1357/oh-my-pi** — fuse-overlay / fuse-projfs.
- **Kilo-Org/kilocode** — git-worktree.
- **shareAI-lab/Kode-Agent** — OpenSandbox.
- **disler / agent-sandboxes** — E2B.

**D3. Anthropic-primitive adoption depth** — *workload-dependent*; derived from F2. Skills / MCP-as-code / Managed Agents adoption depth. Load:
- **RinDig/Interpreted-Context-Methdology** — Filesystem-as-substrate dependence.
- **revfactory/harness** — Claude Code skills/agents emission target.
- **meleantonio/ChernyCode** — CLAUDE.md / AGENTS.md as Cherny-pattern reference.
- **disler (body of work)** — Claude Code-heavy; hooks-mastery, skills.
- **Kilo-Org/kilocode** — Anthropic Provider Integration.
- **mindfold-ai/Trellis** — Claude-only hooks bracketed (explicit portability boundary).
- **sharpdeveye/maestro** — Skills CLI integration.
- **bytedance/deer-flow** — `skills/public/SKILL.md` mirrors Anthropic pattern.

**D4. Multi-agent topology** — *workload-dependent*; single-threaded-writes is a strong default. Parallel sub-agents only for read-heavy/exploration workloads (Yan 2026 follow-up). Load:
- **revfactory/harness** — Six topology patterns (Pipeline / Fan-out-Fan-in / Expert Pool / Producer-Reviewer / Supervisor / Hierarchical Delegation).
- **humanlayer/12-factor-agents** — Factor 10 (small, focused agents; 3–10 step reliability ceiling).
- **bytedance/deer-flow** — Sub-agent + concurrency caps (cap = 3).
- **langchain-ai/deepagents** — SubAgentMiddleware for context isolation.
- **mvschwarz/openrig** — RigSpec multi-process topology.
- **code-yeongyu/oh-my-openagent** — 11-role taxonomy with model temperament binding.
- **shareAI-lab/Kode-Agent** — Multi-agent room.
- **ruvnet/ruflo** — Hive-mind topologies (queen-led + mesh).
- **disler / infinite-agentic-loop** — Wave-based parallel sub-agent generation.

**D5. HITL synchrony** — *persona-dependent*: solo developer → synchronous interactive; team or production → async approval queues; enterprise compliance → both, with audit-ledger. Load:
- **humanlayer/12-factor-agents** — Factor 7 (contact humans with tool calls).
- **cline/cline** — Per-step approval gate (synchronous interactive).
- **Kilo-Org/kilocode** — Approval gates + `--auto` for CI/CD (both modes).
- **RooCodeInc/Roo-Code** — Configurable autonomy slider.
- **langgenius/dify** — Human Input node (v1.13.0).
- **humanlayer/agentcontrolplane** — `ContactChannel` CR (mesh-pattern async).
- **langchain-ai/deepagents** — HITL approval gates.
- **disler / the-verifier-agent** — Two-agent observer pattern.
- **OpenHands/OpenHands** — Per-action approval.

**D6. Observability backend** — *deployment-surface-dependent and persona-dependent*. OTel-to-vendor vs dedicated LLM-observability platform. Load:
- **VoltAgent/voltagent** — VoltOps split (OSS framework + paid console) with OTLP export.
- **Kilo-Org/kilocode** — OpenTelemetry export.
- **langgenius/dify** — Multi-vendor observability + Grafana dashboard.
- **sharpdeveye/maestro** — Audit / decision / effectiveness triad as JSONL.
- **humanlayer/agentcontrolplane** — Reconciliation events as observability stream.
- **paperclipai/paperclip** — Multi-tenant audit + auto-checkout logging.
- **ruvnet/ruflo** — swarm-bench + verify.

### §11.3.3 Independent / deferrable decisions (I1–I3)

**I1. Specific LLM-provider routing logic** — *deferrable*; can be added without architectural rework. Capability-based, cost-based, or quality-based. Load:
- **code-yeongyu/oh-my-openagent** — Per-agent fallback chains by model.
- **earendil-works/pi (pi-mono)** — `~/.pi/agent/models.json` JSONC custom-provider config.
- **cline/cline** — `planActSeparateModelsSetting`.
- **RooCodeInc/Roo-Code** — Per-mode model binding with cost-tier optimization.
- **langchain-ai/deepagents** — Harness profiles per provider.
- **HKUDS/OpenHarness** — Provider profiles + auto-compaction.

**I2. Tool granularity** — *workload-dependent*; influenced by Anthropic's Tool Search and Programmatic Tool Calling primitives. Load:
- **humanlayer/12-factor-agents** — Factor 4 (tools as structured outputs).
- **bytedance/deer-flow** — Tool registry + messaging channels.
- **HKUDS/OpenHarness** — Sandbox backends + MCP HTTP transport + skills.
- **langgenius/dify** — Plugin daemon three-runtime model.
- **langchain-ai/deepagents** — Pluggable filesystem backends.
- **Kilo-Org/kilocode** — MCP + terminal + file edit/diff + browser + agent-manager.

**I3. Database-backed vs filesystem+git for durable state** — *partially foundational* (filesystem committed); db-augmented filesystem is a deferrable addition. Load:
- **paperclipai/paperclip** — Embedded Postgres.
- **langgenius/dify** — Postgres + Redis + vector DB.
- **jonwiggins/optio** — Postgres.
- **mindfold-ai/Trellis** — Filesystem-only (counter-example).
- **RinDig/Interpreted-Context-Methdology** — Filesystem-only (counter-example).
- **humanlayer/12-factor-agents** — Filesystem+thread (counter-example).
- **ruvnet/ruflo** — AgentDB + ReasoningBank (db-augmented).

---
---

# §12. Open questions, pattern-extraction gaps, and candidate additions

This section closes the catalog with the explicit unresolved-ness the Triaged Source Inventory pre-construction phase flagged, plus gaps surfaced by Sessions A–F that no individual entry was the right place to record. None of the items below alter v1.0 entry coverage; all are forward-looking inputs to a v1.1 follow-up session or to design-phase deliberation.

## §12.1 Three open triage questions (per Triaged Source Inventory §3 "Open questions")

**Q1. Should `humanlayer/humanlayer` (10.7k★, Session 3-mentioned) be its own catalog entry separate from `agentcontrolplane`?**

The two HumanLayer artifacts are architecturally distinct: `humanlayer/humanlayer` is an **in-process SDK** for HITL approval workflows over Slack/email (TypeScript primary; ~10.7k★ per the Session 3 deferred list referenced in the Triaged Source Inventory); `agentcontrolplane` (ACP, this catalog §9.G2) is a **Kubernetes operator** with CRDs for LLMs, Agents, Tools, and Tasks. They share Dex Horthy as author and the "outer-loop agent" framing, but they sit at different architectural altitudes — SDK vs platform. **Catalog v1.0 disposition:** `humanlayer/humanlayer` is NOT cataloged as its own entry. The Triaged Source Inventory marked it Session 3-deferred and the Stratum G inclusion of ACP captures the architecturally distinctive K8s-operator pattern; the SDK adds HITL-specific implementation detail without a distinct architectural bet relative to ACP. **Open for v1.1:** if HITL synchrony (D5 in Cluster 5 V2 §3) becomes load-bearing in design, the `humanlayer/humanlayer` SDK should be cataloged as an Action-surface-PRIMARY entry on its own, distinct from ACP, because the SDK's in-process mesh-pattern HITL tools are not co-extensive with ACP's `ContactChannel` CR. **Disposition rationale source:** §9.G2 (ACP) Identification block "Distinction from `humanlayer/humanlayer`" callout; not independently re-argued in this catalog.

**Q2. For thought-leader bodies (`disler`, `coleam00`), is the catalog entry the *person* with sub-entries per repo, or one entry per repo?**

The Triaged Source Inventory recommended the former *for compression* but flagged the call. **Catalog v1.0 disposition:** the *person* is the entry (§7.E1 disler — body of work; §7.E2 coleam00 — body of work), with anchor repos cited and companion repos listed as "evidence of pattern recurrence." Channel companions (§7.E3 @indydevdan, §7.E4 @ColeMedin) are separate abbreviated entries because the channel surfaces different pattern-evidence (recurring themes documented in video corpora) than the repos. **Rationale (recorded here, not re-argued in entry prose):** treating each disler/coleam00 repo as its own catalog entry would multiply Stratum E to ~15+ rows of largely-repeating pattern attributions (single-file-agents and infinite-agentic-loop both demonstrate parallel forking; just-prompt and bowser both demonstrate composable layered architecture); the body-level entry compresses these without losing pattern-citation granularity (each body-entry's "Recurring patterns across the body" subsection cites the specific anchor and companion repos per pattern). The §11.1 matrix accordingly carries one row per body, weighted by primary patterns recurring across the body. **Dissent path:** if a v1.1 design-phase decision requires citing exact star counts, license, or maintenance trajectory of a *single* disler/coleam00 repo (e.g. the project decides to adopt `just-prompt` as its multi-LLM gateway), that single repo should be promoted to its own Stratum-B-or-C catalog entry alongside the body-level Stratum E entry; multi-tag membership is the right resolution, not body-decomposition.

**Q3. For `ai-boost/awesome-harness-engineering` vs `Picrew/awesome-agent-harness` — include both, pick one, or treat as a single "external aggregator landscape" entry?**

**Catalog v1.0 disposition:** `ai-boost/awesome-harness-engineering` is included (§8.F1). `Picrew/awesome-agent-harness` is **NOT** cataloged in v1.0. **Disposition rationale gap (flagged honestly):** Session E's Stratum F treatment of `ai-boost/awesome-harness-engineering` does not document a comparison with `Picrew/awesome-agent-harness`. The Triaged Source Inventory §2 coverage observation 6 surfaced `Picrew` as an adjacent-discovery candidate but did not direct-verify it. **Net status:** the v1.0 choice is a default-from-omission (the entry that was triaged in is the one cataloged), not a measured comparison. **Recommended v1.1 probe:** direct-verify `Picrew/awesome-agent-harness` for (a) curation focus relative to ai-boost; (b) overlap of cited primary sources; (c) maintenance signal. Likely outcomes: include both as separate Stratum F entries with a "comparison of curation focus" sub-block; OR consolidate into a single "External aggregator landscape" entry with both repos as sub-citations. The v1.0 catalog leaves this open rather than fabricate a rationale.

## §12.2 Candidate additions for v1.1 follow-up (NOT cataloged in v1.0)

Three adjacent-discovery candidates flagged in the Triaged Source Inventory §2 coverage observation 6 as discovery findings adjacent to the user's source list, deferred from v1.0 catalog construction:

**Picrew/awesome-agent-harness** — aggregator addition. Distinct from ai-boost/awesome-harness-engineering (§8.F1); both cataloging surfaces would benefit from comparison (see Q3 above). Candidate stratum: **F** (knowledge aggregator), abbreviated schema. v1.1 priority: **MODERATE** — closes a Q3 disposition gap without changing decision-relevance density.

**HKUDS/nanobot** — sister project to OpenHarness (§3.B5). Per the Triaged Source Inventory, ~42k★ from the same HK U Data Science Lab; positioned as the personal-agent angle complementary to OpenHarness's harness-as-substrate framing. Candidate stratum: **B-standard** (production harness) or **C** (emerging) depending on architectural distinctiveness relative to OpenHarness — direct verification needed before placement. v1.1 priority: **HIGH** — same lab as a Stratum B-standard PRIMARY-on-four-axes entry (OpenHarness); covers an adjacent architectural altitude (personal agent) that no current Stratum B entry occupies cleanly.

**humanlayer/advanced-context-engineering-for-coding-agents** — methodology angle. Visible in HumanLayer org listing per Triaged Source Inventory §2 coverage observation 6; not direct-verified in any session. Candidate stratum: **D** (methodology) or **D-meta** depending on whether the artifact ships as a portable spec layer or as an opinionated methodology document. v1.1 priority: **MODERATE-HIGH** — HumanLayer's methodology output (12-Factor Agents, ACP) is already disproportionately represented in the catalog (§5.D1, §9.G2); a third HumanLayer methodology entry would either reinforce a recurring author-voice signal or add a distinct context-engineering pattern not covered by 12-Factor F3. Direct verification first.

## §12.3 Pattern-extraction gaps within v1.0 entries

Catalog entries where the patterns extracted are thin, the citation strength is partial, or specific quantitative claims could not be verified within session scope. These are flagged for v1.1 deepening, not dropped from v1.0:

- **§4.C6 shareAI-lab/Kode-Agent — license unverified.** Integration considerations note "Not verified this session — resolve before vendoring [SPECULATIVE]." v1.1 probe: open `LICENSE` file directly; resolve `Kode-Agent` vs `Kode.git` clone-target naming inconsistency from the URL anomaly list.
- **§4.C7 mvschwarz/openrig — license MODERATE.** Integration considerations note "MIT per brief, not directly verified this session." v1.1 probe: open `LICENSE` file directly.
- **§4.C4 code-yeongyu/oh-my-openagent — license SPECULATIVE; star count anomalous.** v1.1 probes: (a) open `LICENSE` file or `package.json` license field; (b) reconcile the 56.4k releases-page-header figure against the repo header to confirm Stratum C placement vs promotion to Stratum B-priority.
- **§4.C1 can1357/oh-my-pi — Hashline benchmark methodology partially documented.** README claims "16 models, 180 tasks, 3 runs each" with Grok Code Fast 1 6.7%→68.3% lift and Grok 4 Fast 61% fewer output tokens; the benchmark harness file, prompt set, and run-to-run variance are not surfaced in the README excerpt. Confidence on the figures is HIGH; on the methodology is MODERATE. v1.1 probe: read the benchmark file directly if cited as decision-relevant evidence.
- **§4.C1 can1357/oh-my-pi — "11 LSP operations" integer not directly verified.** README enumerates a category list rather than naming a count of 11. v1.1 probe: read `src/lsp/` directly.
- **§4.C1 can1357/oh-my-pi — release tag v13.19.0 (5 Apr 2026) per task brief not directly verified.** v13.14.0 / v13.15.3 confirmed; the exact brief-cited tag is MODERATE. v1.1 probe: visit the releases page directly.
- **§3.B7 langgenius/dify — Supervisor-mode agent loop sourced from secondary documentation.** "New Supervisor agent mode in 2026 coordinates multiple sub-agents for complex multi-step tasks" is sourced from `dify-hosting.com` 2026 update guide [MODERATE — secondary]. v1.1 probe: locate the primary release-note or docs source for Supervisor mode if architectural commitment is being made.
- **§3.B7 langgenius/dify — "Founded by ex-Tencent Cloud DevOps" task-brief claim not re-verified.** v1.1 probe: locate primary About-page source.
- **§9.G1 ruvnet/ruflo — license unverified, "84.8% SWE-Bench solve rate" claim not third-party-replicated.** Both flags surfaced in §9.G1 critical assessment. v1.1 probe: open `LICENSE` and the swarm-bench artifact directly if ruflo is a load-bearing decision input.
- **§5.D1 humanlayer/12-factor-agents — license MODERATE.** Identification block notes "consistent with humanlayer org default observed for sibling repos" — license file not directly opened this session. v1.1 probe: open `LICENSE` file directly.
- **§7.E1 disler — anchor-repo license MODERATE.** Body-of-work integration considerations note "Mostly MIT across the body (verified for infinite-agentic-loop; presumed for siblings)." v1.1 probe: open `LICENSE` for `single-file-agents` directly to lift the anchor confidence to HIGH.
- **§6.Dmeta1 revfactory/harness — license MODERATE.** Identification block notes "Not directly verified this session [MODERATE — assumed permissive given Claude Code plugin marketplace distribution]." v1.1 probe: open `LICENSE` directly.
- **§6.Dmeta2 sharpdeveye/maestro — license MODERATE; "10 hosts" claim unverified.** README claims compatibility with Cursor, Claude Code, Gemini CLI, Copilot, "and 6 more" without enumerating the six. v1.1 probes: open `LICENSE`; enumerate the ten claimed hosts.
- **§4.C3 mindfold-ai/Trellis — star count not directly observed.** v0.4.0 license confirmed AGPL-3.0 from npm registry; star count was not in the Identification block. v1.1 probe: visit repo header directly.
- **Meta-Harness YouTube videos `13HP_bSeNjU`, `yOeVi3aQ9Kg`** — Triaged Source Inventory §1A flagged these as DEFER (not directly verified). Catalog §2.1 omitted them, consistent with the DEFER decision; the question of whether they add over the paper remains open per Triaged Source Inventory "Recommended next probes." v1.1 probe: direct-verify and decide whether to add to §2.1 secondary URLs or drop the candidacy.

## §12.4 Cross-source tensions the catalog cannot resolve

These are tensions surfaced in §10.6 that the catalog flags but does not adjudicate. The design phase, not catalog construction, is the appropriate locus for resolution. Each tension is restated here as an open question with the §10.6 citation:

- **T1 (§10.6) — Filesystem-as-orchestrator vs framework-orchestration.** ICM and Meta-Harness commit the filesystem as the *coordination primitive*; deepagents, Dify, and VoltAgent commit framework-managed graphs. 12-Factor splits the difference (filesystem = state per Factor 5; control flow = code per Factor 8). Cluster 5 V2 §3 marks F2 as foundational only at the *substrate* level; the *control plane* face of T1 is unresolved. **Design-phase decision input, not catalog adjudication.**
- **T2 (§10.6) — Single-process harness vs multi-process / topology orchestration.** Cline / OpenHands / deepagents / VoltAgent (single-process) vs openrig (tmux-process-graph) vs ACP / optio (K8s pods). Cluster 1 substrate sits closer to single-process via Anthropic's clean-context-reviewer pattern and Cognition's single-threaded-writes position; openrig / ACP sit closer to multi-process. **Resolution depends on D4 (multi-agent topology) and deployment-surface choice.**
- **T3 (§10.6) — Per-task vs per-company deployment unit.** Most catalog entries treat the task/session as the deployment unit; optio extends to per-repo; paperclip extends to per-company. Cluster 5 V2 marks D5 (multi-tenant identity) as **persona-dependent**. **Resolution awaits persona commitment in design phase.**
- **T4 (§10.6) — Markdown-spec-driven vs code-driven configuration.** Markdown sources (RevFactory, Maestro, Agency-Agents, Trellis, ICM, ChernyCode, 12-Factor, disler/the-library) vs code sources (deepagents, VoltAgent, OpenHands, OpenHarness, kilocode, Dify, pi-mono). The cross-platform meta-skill cluster (P-DS-5) is exclusively Markdown by necessity — Markdown is the only format every host harness reads. **Resolution depends on whether the harness is itself a meta-skill / cross-platform layer (Markdown-mandated) or an opinionated runtime (code-driven open).**

Additional unresolved-in-catalog tensions worth noting that are not in §10.6 but surface across entries:

- **T5 (cross-cutting) — Hooks portability boundary.** Trellis explicitly brackets hooks as Claude-Code-only (§4.C3 Pattern 3); crush ships hooks in the agent contract (§4.C5 Pattern 1); disler's `claude-code-hooks-mastery` enumerates 13 hook events; deepagents has no hooks primitive (uses middleware composition instead). The catalog cannot adjudicate whether the harness should adopt the hook abstraction at all, or whether middleware-as-hook-equivalent is the better substrate.
- **T6 (cross-cutting) — License heterogeneity.** Catalog spans MIT (most), Apache-2.0 (Cline, Roo Code, ACP), AGPL-3.0 (Trellis), FSL-1.1-MIT non-OSI (crush), Dify Open Source License (modified Apache 2.0 with multi-tenant clause), CC BY 4.0 (papers), and several unverified. License-discipline-by-stratum is not a foregone conclusion; the design phase should commit a license-acceptance posture per pattern-source category (vendor as runtime dep vs. lift as patterns vs. study only).

---

# §13. Consolidated source bibliography

This bibliography consolidates the per-session bibliographies of Sessions A–F (the bodies of which are §2–§11 of this catalog). Sources are organized by catalog section to keep citation traceability direct from any entry. Within each section, sources are deduplicated across sessions; observation dates are preserved as recorded in each session (uniformly **2026-05-08** unless otherwise noted). Cross-references to *Triaged Source Inventory Appendix A* (the URL reference appendix in the project knowledge base file `Triaged_Source_Inventory__Pattern_Reference_Catalog_Pre-Construction.md`) are explicit where the source URL appears in that appendix; absence of cross-reference indicates a source surfaced in catalog construction beyond the original triage scope.

**Format:** *Author / Org. (Year). Title. URL. — observation note where relevant.* Markdown anchor links are preserved as in the catalog entries; observation dates default to 2026-05-08 (catalog construction) and are noted explicitly only when the original session captured a different access date or surfaced a snapshot caveat.

## §13.1 Sources cited in §2 — Stratum A research artifacts

*Source-list version: Triaged Source Inventory Appendix A1 (Research artifacts).*

1. Lee, Y., Nair, R., Zhang, Q., Lee, K., Khattab, O., & Finn, C. (2026). *Meta-Harness: End-to-End Optimization of Model Harnesses.* arXiv:2603.28052v1 [cs.AI], 30 Mar 2026. https://arxiv.org/abs/2603.28052
2. Lee, Y. et al. (2026). *Meta-Harness — project page with interactive demo and TerminalBench-2 leaderboard tables.* https://yoonholee.com/meta-harness/
3. Stanford IRIS Lab. (2026). *meta-harness — Reference code for the Meta-Harness paper.* GitHub repository (MIT, 9 commits, 34 stars at observation 2026-05-08). https://github.com/stanford-iris-lab/meta-harness
4. Stanford IRIS Lab. (2026). *meta-harness/ONBOARDING.md.* https://github.com/stanford-iris-lab/meta-harness/blob/main/ONBOARDING.md
5. Stanford IRIS Lab. (2026). *meta-harness-tbench2-artifact — Meta-Harness: 76.4% on Terminal-Bench 2.0 (Claude Opus 4.6).* GitHub repository (no LICENSE file, 1 commit, 11 stars at observation 2026-05-08). https://github.com/stanford-iris-lab/meta-harness-tbench2-artifact
6. Van Clief, J., & McDermott, D. (2026). *Interpretable Context Methodology: Folder Structure as Agent Architecture.* arXiv:2603.16021v2 [cs.AI, cs.HC], 18 Mar 2026 (28 pp, 5 figures, 2 tables, 54 references). https://arxiv.org/abs/2603.16021
7. Van Clief, J., & McDermott, D. (2026). *Interpretable Context Methodology — paper v1, "Model Workspace Protocol" naming.* arXiv:2603.16021v1, 17 Mar 2026. https://arxiv.org/html/2603.16021v1
8. Van Clief, J. (2026). *RinDig/Interpreted-Context-Methdology — companion repository to the ICM paper* (MIT, 14 commits, 45 stars at observation 2026-05-08; URL slug carries two typos relative to the paper title). https://github.com/RinDig/Interpreted-Context-Methdology
9. *tbench.ai — Terminal-Bench 2.0 leaderboard.* https://www.tbench.ai/leaderboard/terminal-bench/2.0 — referenced for the leaderboard-context disambiguation in §2.1 ("#2 on Opus 4.6 split, not overall #1" caveat).

## §13.2 Sources cited in §3.priority — Priority-tier production harnesses

*Source-list version: Triaged Source Inventory Appendix A2 (Production harnesses) for DeerFlow, pi, and kilocode.*

### bytedance/deer-flow (DeerFlow 2.0) — §3.priority-1

1. ByteDance. (2026). *deer-flow — README.* https://github.com/bytedance/deer-flow
2. ByteDance. (2026). *deer-flow/README.md (full text).* https://github.com/bytedance/deer-flow/blob/main/README.md
3. ByteDance. (2026). *deer-flow/CONTRIBUTING.md — top-level repo layout.* https://github.com/bytedance/deer-flow/blob/main/CONTRIBUTING.md
4. ByteDance. (2026). *deer-flow/backend/README.md — backend architecture and component layout.* https://github.com/bytedance/deer-flow/blob/main/backend/README.md
5. ByteDance. (2026). *deer-flow/backend/CLAUDE.md — lead agent + middleware + sandbox mode reference.* https://github.com/bytedance/deer-flow/blob/main/backend/CLAUDE.md
6. ByteDance. (2026). *deer-flow/skills/public/claude-to-deerflow/SKILL.md — SSE streaming protocol and context modes.* https://github.com/bytedance/deer-flow/blob/main/skills/public/claude-to-deerflow/SKILL.md
7. ByteDance. (2026). *deer-flow/activity — fork/star/issue counts.* https://github.com/bytedance/deer-flow/activity
8. *bytedance — org repository listing* (repo metadata, last push date, language distribution). https://github.com/orgs/bytedance/repositories
9. ByteDance. (2026). *deer-flow/issues — open-issue counts; weekly progress reports.* https://github.com/bytedance/deer-flow/issues
10. ByteDance. (2026). *deer-flow/issues/824 — DeerFlow 2.0 release plan.* https://github.com/bytedance/deer-flow/issues/824
11. *deerflow.tech — project site, demo gallery.* https://deerflow.tech/
12. *deepwiki.com/bytedance/deer-flow — third-party generated wiki* (used for cross-reference of architecture diagrams).
13. *deepwiki.com/bytedance/deer-flow/3-architecture — architectural reference cross-check.*
14. *deepwiki.com/bytedance/deer-flow/5.3-llm-configuration — soul/skills/memory composite prompt.*
15. *VentureBeat. What is DeerFlow and what should enterprises know about this new local AI* — corroboration of v1→v2 ground-up rewrite chronology. https://venturebeat.com/orchestration/what-is-deerflow-and-what-should-enterprises-know-about-this-new-local-ai
16. *dev.to/arshtechpro/deerflow-20-what-it-is-how-it-works-and-why-developers-should-pay-attention-3ip3* — community signals corroboration.

### earendil-works/pi (pi-mono) — §3.priority-2

17. Zechner, M. / earendil-works. (2026). *pi/README.md — package list and project overview.* https://github.com/earendil-works/pi/blob/main/README.md
18. Zechner, M. / earendil-works. (2026). *pi/AGENTS.md — provider-addition checklist and contribution discipline.* https://github.com/earendil-works/pi/blob/main/AGENTS.md
19. Zechner, M. / earendil-works. (2026). *pi/packages/coding-agent — coding-agent operational modes.* https://github.com/earendil-works/pi/tree/main/packages/coding-agent
20. Zechner, M. / earendil-works. (2026). *pi/packages/coding-agent/README.md — interactive mode, sessions, RPC framing.* https://github.com/earendil-works/pi/blob/main/packages/coding-agent/README.md
21. Zechner, M. / earendil-works. (2026). *pi/packages/coding-agent/CHANGELOG.md — release cadence and external contributor signals.* https://github.com/earendil-works/pi/blob/main/packages/coding-agent/CHANGELOG.md
22. Zechner, M. / earendil-works. (2026). *pi/issues — issue-level evidence for activity, vendor breakage, environment configuration* (issues #3850, #3372, #2815, #1900). https://github.com/earendil-works/pi/issues
23. Zechner, M. / earendil-works. (2026). *pi/discussions/2112 — community signal, star count snapshot Mar 13, 2026.* https://github.com/earendil-works/pi/discussions/2112
24. *earendil-works — org listing* (current star/fork/last-push metadata for pi and sister repos: gondolin, absurd, pi-chat, pi-website, pi-review, pi-tutorial). https://github.com/earendil-works
25. *orgs/earendil-works/repositories — sister-repo star counts.* https://github.com/orgs/earendil-works/repositories
26. *github.com/badlogic/pi-mono — historical URL verification* (redirects to earendil-works/pi). https://github.com/badlogic/pi-mono
27. *github.com/badlogic/pi-mono/tree/main/packages/web-ui — pi-web-ui detail.*
28. *github.com/badlogic/pi-mono/tree/main/packages/tui — pi-tui detail.*
29. *github.com/badlogic/pi-mono/tree/main/packages/ai — pi-ai protocol adapters.*
30. *github.com/badlogic/pi-mono/blob/main/packages/ai/README.md — provider list and OAuth surface.*
31. *github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/packages.md — peer-dep contract, package layering rules.*
32. *npmjs.com/package/@mariozechner/pi-ai — npm metadata, OAuth entry point.* https://www.npmjs.com/package/@mariozechner/pi-ai
33. *pi.dev — project site.* https://pi.dev/
34. *pi.dev/news/2026/5/7/pi-has-a-new-home — org-migration announcement.* https://pi.dev/news/2026/5/7/pi-has-a-new-home
35. Zechner, M. (2025). *Anatomy of a coding agent — author's design essay (primary for stated thesis).* https://mariozechner.at/posts/2025-11-30-pi-coding-agent
36. *nader.substack.com — How to build a custom agent framework* — third-party tutorial corroboration of `StreamFn` middleware seam. https://nader.substack.com/p/how-to-build-a-custom-agent-framework
37. *Agarwal, S. — Agentic AI Pi: anatomy of a minimal coding agent powering OpenClaw* — third-party analysis of agent-loop and provider quirks. https://shivamagarwal7.medium.com/agentic-ai-pi-anatomy-of-a-minimal-coding-agent-powering-openclaw-5ecd4dd6b440
38. *deepwiki.com/badlogic/pi-mono/3-pi-agent-core:-agent-framework — third-party generated wiki, cross-reference for `agent-loop.ts` line citations.*
39. *deepwiki.com/badlogic/pi-mono/4-pi-coding-agent:-coding-agent-cli — coding-agent operational-mode cross-reference.*

### Kilo-Org/kilocode — §3.priority-3

40. Kilo Code Inc. (2026). *kilocode — README, license.* https://github.com/Kilo-Org/kilocode
41. Kilo Code Inc. (2026). *kilocode/LICENSE — MIT confirmation.* https://github.com/Kilo-Org/kilocode/blob/main/LICENSE
42. Kilo Code Inc. (2026). *kilocode/AGENTS.md — monorepo discipline, OpenCode upstream relationship, kilocode_change markers, Agent Manager description.* https://github.com/Kilo-Org/kilocode/blob/main/AGENTS.md
43. Kilo Code Inc. (2026). *kilocode/packages/kilo-vscode/docs/opencode-migration-plan.md — rebuild rationale, parity tracking.* https://github.com/Kilo-Org/kilocode/blob/main/packages/kilo-vscode/docs/opencode-migration-plan.md
44. Kilo Code Inc. (2026). *kilocode/packages/kilo-vscode/CHANGELOG.md — recent PR-level features.* https://github.com/Kilo-Org/kilocode/blob/main/packages/kilo-vscode/CHANGELOG.md
45. Kilo Code Inc. (2026). *kilocode/package.json — root package metadata.* https://github.com/Kilo-Org/kilocode/blob/main/package.json
46. Kilo Code Inc. (2026). *kilocode/releases — release-level changelog.* https://github.com/Kilo-Org/kilocode/releases
47. Kilo Code Inc. (2026). *kilocode/discussions/2022 — Memory Bank setup steps.* https://github.com/Kilo-Org/kilocode/discussions/2022
48. Kilo Code Inc. (2025). *kilocode/pull/50 — historical license attribution PR (Apache 2.0 + Roo Code/Cline NOTICE), Mar 2025.* https://github.com/Kilo-Org/kilocode/pull/50
49. *github.com/Kilo-Org/kilo — redirect target verification.* https://github.com/Kilo-Org/kilo
50. Kilo Code Inc. *kilocode-legacy — preserved Apache-2.0 legacy codebase.* https://github.com/Kilo-Org/kilocode-legacy
51. *Kilo-Org — org listing* (current star/fork/issue/PR counts). https://github.com/Kilo-Org
52. *kilo.ai — product site.* https://kilo.ai/
53. *kilo.ai/code — product features (Memory Bank, Orchestrator, autocomplete).* https://kilo.ai/code
54. *kilo.ai/cli — CLI page; OpenCode fork statement.* https://kilo.ai/cli
55. *kilo.ai/docs/code-with-ai/platforms/cli — CLI configuration, telemetry/OTLP, environment-variable references.* https://kilo.ai/docs/code-with-ai/platforms/cli
56. *kilo.ai/features/memory-bank — Memory Bank product description.* https://kilo.ai/features/memory-bank
57. *kilo.ai/kilo-code/vs/cline — Kilo's first-party comparative content* (treated as marketing-tinted).
58. *blog.kilo.ai/p/new-kilo-for-vs-code-is-live — engineering blog announcing the OpenCode-server-based VS Code extension as default.* https://blog.kilo.ai/p/new-kilo-for-vs-code-is-live
59. *deepwiki.com/Kilo-Org/kilocode* and `.../3.1-monorepo-structure`, `.../9.1-autocomplete-architecture`, `.../3-core-features` — third-party generated wiki used to cross-reference monorepo structure and provider-layer details.
60. *VentureBeat. Kilo launches KiloClaw, allowing anyone to deploy hosted OpenClaw agents into…* https://venturebeat.com/orchestration/kilo-launches-kiloclaw-allowing-anyone-to-deploy-hosted-openclaw-agents-into
61. *agent-safehouse.dev/docs/agent-investigations/kilo-code — third-party security analysis of *legacy* extension (commit 7dace4a, 2025-07-01)*; flagged as legacy-architecture data.
62. *docs.bswen.com/blog/2026-03-15-opencode-vs-kilocode-vs-cline-comparison — third-party critical review (legacy-era)*; flagged as moderate-confidence single-source criticism.
63. *morphllm.com/comparisons/kilo-code-vs-cline — third-party comparative review.*
64. *marketplace.visualstudio.com/items?itemName=kilocode.Kilo-Code — VS Code Marketplace listing.*
65. *pkg.go.dev/github.com/Kilo-Org/kilocode — license and recent-publish-date corroboration.*

## §13.3 Sources cited in §3.standard — Stratum B standard production harnesses

*Source-list version: Triaged Source Inventory Appendix A2 (Production harnesses) for OpenHands, Cline, goose, Roo-Code, OpenHarness, deepagents, Dify, VoltAgent.*

### Primary repository / first-party (alphabetical by entry)

66. *cline/cline — README, CHANGELOG.md, issues page (May 2026), issue #4848 (Plan-mode bug), issue #9174 (competitive landscape).* https://github.com/cline/cline
67. *cline — org repository listing (8 May 2026).* https://github.com/cline
68. *cline.bot — /core-workflows/plan-and-act, /blog/cline-the-fastest-growing-ai-open-source-project, /blog/plan-smarter-code-faster.* https://cline.bot
69. *cline.ghost.io/5m-installs-1m-open-source-grant-program/.*
70. *DeepWiki: cline/cline §3.4 Plan and Act Modes; langchain-ai/deepagents §5.1 create_deep_agent.*
71. *aaif-goose/goose — README.* https://github.com/aaif-goose/goose
72. *goose-docs.ai/blog/2026/04/07/goose-moves-to-aaif/.*
73. *aaif.io/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation-aaif/.* https://aaif.io
74. *linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation.*
75. *prnewswire.com — Linux Foundation AAIF release.*
76. *anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation.* https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation
77. *block.xyz/inside/block-anthropic-and-openai-launch-the-agentic-ai-foundation.*
78. *RooCodeInc/Roo-Code — README, discussion #2861, issue #5605.* https://github.com/RooCodeInc/Roo-Code
79. *RooCodeInc — org repository listing.*
80. *RooCodeInc/Roo-Code-Docs — README.*
81. *roocode.com — homepage; docs.roocode.com — homepage.*
82. *HKUDS/OpenHarness — README.md, README.zh-CN.md, CHANGELOG.md, CONTRIBUTING.md, releases page, docs/SHOWCASE.md, pull requests page (8 May 2026).* https://github.com/HKUDS/OpenHarness
83. *HKUDS — org repository listing (8 May 2026).* https://github.com/HKUDS
84. *langchain-ai/deepagents — README, releases page (latest harness profiles release).* https://github.com/langchain-ai/deepagents
85. *langchain-ai/deepagentsjs — README.* https://github.com/langchain-ai/deepagentsjs
86. *langchain-ai/deep-agents-ui — README.*
87. *langchain-ai/openshell-deepagent — README.*
88. *langchain-ai — org repository listing (6 May 2026 snapshot).*
89. *docs.langchain.com/oss/python/deepagents/overview.*
90. *reference.langchain.com/python/deepagents.*
91. *langgenius/dify — README, releases page, v1.14.0 release tag (29 Apr 2026).* https://github.com/langgenius/dify
92. *langgenius/dify/blob/main/LICENSE — Dify Open Source License (modified Apache 2.0).* https://github.com/langgenius/dify/blob/main/LICENSE
93. *langgenius/dify-plugin-daemon — README (Apache-2.0).* https://github.com/langgenius/dify-plugin-daemon
94. *langgenius/dify-official-plugins — README.* https://github.com/langgenius/dify-official-plugins
95. *langgenius/dify-sandbox — LICENSE.* https://github.com/langgenius/dify-sandbox
96. *langgenius/dify-docs — README, LICENSE (CC BY 4.0).* https://github.com/langgenius/dify-docs
97. *dify.ai — homepage, blog (v1.13.0 Human Input, v1.5.0 real-time debugging, v1.0.0 plugin ecosystem, March 2026 release index).* https://dify.ai
98. *VoltAgent/voltagent — README, voltagent/CHANGELOG.md.* https://github.com/VoltAgent/voltagent
99. *VoltAgent/ai-agent-platform — README.* https://github.com/VoltAgent/ai-agent-platform
100. *VoltAgent/ai-agent-examples — README.* https://github.com/VoltAgent/ai-agent-examples
101. *VoltAgent/awesome-design-md/blob/main/LICENSE — MIT (used to confirm VoltAgent org license posture).*
102. *voltagent — org repository listing (8 May 2026).*
103. *voltagent.dev — homepage, /pricing.* https://voltagent.dev
104. *OpenHands/OpenHands — README.* https://github.com/OpenHands/OpenHands
105. *OpenHands/software-agent-sdk — README.* https://github.com/OpenHands/software-agent-sdk
106. *OpenHands/docs — issue #36 (org rename to OpenHands).*
107. *All-Hands-AI/OpenHands — issue #11376 (org rename notice).*
108. *docs.openhands.dev/openhands/usage/llms/llms — provider matrix.*
109. *openhands.dev — homepage, /blog/one-year-of-openhands, /blog/announcing-all-hands-online-beta.* https://www.openhands.dev

### Secondary / corroborating

110. *techcrunch.com — OpenAI/Anthropic/Block AAIF coverage (9 Dec 2025).*
111. *infoq.com — AAIF launch coverage.*
112. *opensourcesecurity.io — Brad Axen / goose / AAIF interview (Feb 2026).*
113. *talkpython.fm Episode #543 — Sydney Runkle on Deep Agents (19 Feb 2026).*
114. *npmjs.com/package/deepagents.*
115. *producthunt.com/products/voltagent-opensource-ai-agent-framework.*
116. *producthunt.com/products/voltops-llm-observability-platform.*
117. *huggingface.co/voltagent.*
118. *blog.brightcoding.dev/2026/04/18/voltagent-the-revolutionary-typescript-framework-for-ai-agents.*
119. *towardsai.net/p/machine-learning/agents-2-0-from-shallow-loops-to-deep-agents.*
120. *medium.com — deepagents Chapter 2.*
121. *knightli.com/en/2026/04/12/openharness-basic-functions/ — OpenHarness positioning analysis.*
122. *deployhq.com/guides/cline — Cline 2026 setup reference.*
123. *decisioncrafters.com — Roo Code overview (star count snapshot).*
124. *dify-hosting.com/en/guides/dify-updates/ — Dify 2026 updates summary.*
125. *tech-insider.org — Dify tutorial (pitfalls).*
126. *releasealert.dev — Dify v1.14.0 release date confirmation.*

## §13.4 Sources cited in §4 — Stratum C emerging harnesses

*Source-list version: Triaged Source Inventory Appendix A3 (Emerging harnesses).*

### oh-my-pi — §4.C1

127. Bölük, C. (2026). *oh-my-pi/README.md.* https://github.com/can1357/oh-my-pi/blob/main/README.md
128. Bölük, C. (2026). *oh-my-pi/AGENTS.md.* https://github.com/can1357/oh-my-pi/blob/main/AGENTS.md
129. Bölük, C. (2026). *oh-my-pi/packages/coding-agent/DEVELOPMENT.md.*
130. Bölük, C. (2026). *oh-my-pi/packages/coding-agent/CHANGELOG.md.*
131. Bölük, C. (2026). *oh-my-pi/docs/models.md, docs/skills.md.*
132. Bölük, C. (2026). *oh-my-pi/issues/413 (March 2026); Releases page; SourceForge mirror tags v13.8.0 / v13.9.3 / v13.9.15; newreleases.io v13.14.0 / v13.15.3.*
133. *DeepWiki secondary index pages (key-features; @oh-my-pi/pi-coding-agent).*

### Optio — §4.C2

134. Wiggins, J. (2026). *optio/README.md.* https://github.com/jonwiggins/optio
135. *optio.host — project site.* https://optio.host
136. *optio Workflow runs page (CI #845–#850).*
137. *Hacker News — news.ycombinator.com/item?id=47520220.*
138. *optio/LICENSE.*

### Trellis — §4.C3

139. mindfold-ai. (2026). *Trellis/README.md, README_CN.md.* https://github.com/mindfold-ai/Trellis
140. mindfold-ai. (2026). *Trellis/.claude/skills/trellis-meta/SKILL.md.*
141. *npmjs.com/package/@mindfoldhq/trellis (v0.4.0; AGPL-3.0).*
142. *docs.trytrellis.app/release.*
143. *github.com/mindfold-ai — org page.*

### oh-my-openagent — §4.C4

144. Kwon, Y. (2026). *oh-my-openagent/README.md.* https://github.com/code-yeongyu/oh-my-openagent/blob/dev/README.md
145. Kwon, Y. (2026). *oh-my-openagent/AGENTS.md.*
146. Kwon, Y. (2026). *oh-my-openagent/docs/guide/installation.md, docs/guide/overview.md, docs/guide/agent-model-matching.md.*
147. Kwon, Y. (2026). *oh-my-openagent/docs/reference/configuration.md, docs/reference/features.md.*
148. *ohmyopenagent.com — docs site; Releases v4.0.0 (07 May 2026).* https://ohmyopenagent.com
149. *Action run `feat(ttsr): Port Time Traveling Streamed Rules from oh-my-pi` (commit 206dc8c).* https://github.com/code-yeongyu/oh-my-openagent/actions/runs/22888688607

### Crush — §4.C5

150. Charmbracelet, Inc. (2026). *crush/README.md, AGENTS.md.* https://github.com/charmbracelet/crush
151. Charmbracelet, Inc. (2026). *crush/LICENSE.md.* https://github.com/charmbracelet/crush/blob/main/LICENSE.md (raw at https://raw.githubusercontent.com/charmbracelet/crush/main/LICENSE.md)
152. Charmbracelet, Inc. (2026). *crush/discussions/1482 — FSL-1.1 maintainer clarification.*
153. Charmbracelet, Inc. (2026). *crush/Releases v0.61.1 / v0.62.0 / v0.62.1 / v0.66.0.*
154. *SPDX submission #2458 — FSL-1.1-MIT non-OSI status, two-year fixed delay.*

### Kode-Agent — §4.C6

155. shareAI-lab. (2026). *Kode-Agent/README.md.* https://github.com/shareAI-lab/Kode-Agent/blob/main/README.md
156. shareAI-lab. (2026). *Kode-Agent/docs/skills.md.*
157. shareAI-lab. (2026). *Sister repos: Kode-cli/README.md, Kode-agent-sdk/README.md, learn-claude-code/README.md.*
158. *github.com/shareai-lab — org page.*

### OpenRig — §4.C7

159. Schwarz, M. (2026). *openrig/README.md.* https://github.com/mvschwarz/openrig
160. *Hacker News — news.ycombinator.com/item?id=47772935.*
161. *kirupaForum thread — openrig-turns-agent-topologies-into-recoverable-infrastructure.* https://forum.kirupa.com/t/openrig-turns-agent-topologies-into-recoverable-infrastructure/680272

### Paperclip — §4.C8

162. Paperclip AI. (2026). *paperclip/README.md, LICENSE.* https://github.com/paperclipai/paperclip
163. Paperclip AI. (2026). *paperclip/docs/companies/companies-spec.md.*
164. Paperclip AI. (2026). *paperclip/cli — CLI directory.*
165. Paperclip AI. (2026). *paperclip Releases page.*
166. *github.com/paperclipai — org page.*
167. *paperclip.ing — project site.* https://paperclip.ing

## §13.5 Sources cited in §5 — Stratum D methodology framework

168. HumanLayer / Horthy, D. (2025). *humanlayer/12-factor-agents — root README, content/factor-NN-*.md, Discussion #61.* https://github.com/humanlayer/12-factor-agents
169. HumanLayer / Horthy, D. (2025). *content/factor-01-natural-language-to-tool-calls.md.*
170. HumanLayer / Horthy, D. (2025). *content/factor-03-own-your-context-window.md.*
171. HumanLayer / Horthy, D. (2025). *content/factor-05-unify-execution-state.md.*
172. *humanlayer.dev/12-factor-agents — rendered companion site.* https://www.humanlayer.dev/12-factor-agents
173. *github.com/humanlayer — org page.*
174. *Hacker News submission item 43699271 (April 2025 announcement).*

## §13.6 Sources cited in §6 — Stratum D-meta cross-platform meta-skill

### revfactory/harness — §6.Dmeta1

175. Hwang, M. / revfactory. (2026). *harness/README (English) and README_KO.md.* https://github.com/revfactory/harness
176. *revfactory.github.io/harness — project site.*
177. *revfactory/harness-100 — sister repo (100 production harnesses).* https://github.com/revfactory/harness-100
178. *revfactory/claude-code-harness — companion controlled experiment / A/B study.*
179. *revfactory profile README and activity page.*

### sharpdeveye/maestro — §6.Dmeta2

180. sharpdeveye. (2026). *maestro/README — command reference, directory layout, anti-pattern callouts, MCP-server note.* https://github.com/sharpdeveye/maestro

### msitarzewski/agency-agents — §6.Dmeta3

181. Sitarzewski, M. (2026). *agency-agents/README, examples/README.md.* https://github.com/msitarzewski/agency-agents
182. *github.com/msitarzewski — profile page.*
183. *yuv.ai/blog/agency-agents — secondary commentary.*

## §13.7 Sources cited in §7 — Stratum E thought-leader bodies of work

### disler — §7.E1 + §7.E3 (@indydevdan)

184. disler. (2026). *disler — full repository listing.* https://github.com/disler?tab=repositories
185. disler. (2026). *single-file-agents/README + CLAUDE.md (anchor).* https://github.com/disler/single-file-agents
186. disler. (2026). *the-library — meta-skill catalog of agentics.* https://github.com/disler/the-library
187. disler. (2026). *just-prompt — README + .mcp.json.* https://github.com/disler/just-prompt
188. disler. (2026). *infinite-agentic-loop — README + .claude/commands/infinite.md + CLAUDE.md.* https://github.com/disler/infinite-agentic-loop
189. disler. (2026). *claude-code-hooks-mastery.* https://github.com/disler/claude-code-hooks-mastery
190. disler. (2026). *claude-code-hooks-multi-agent-observability — README + .claude/skills/.* https://github.com/disler/claude-code-hooks-multi-agent-observability
191. disler. (2026). *agent-sandboxes.* https://github.com/disler/agent-sandboxes
192. disler. (2026). *agent-sandbox-skill.*
193. disler. (2026). *bowser — composable browser-automation.* https://github.com/disler/bowser
194. disler. (2026). *fork-repository-skill.* https://github.com/disler/fork-repository-skill
195. disler. (2026). *the-verifier-agent.* https://github.com/disler/the-verifier-agent
196. disler. (2026). *mac-mini-agent.*
197. disler. (2026). *agentic-finance-review.*
198. *gist.github.com/disler — supplementary gists.*
199. IndyDevDan / disler. (2026). *YouTube channel.* https://www.youtube.com/@indydevdan
200. *youtube.com/@indydevdan/videos and channel/UC_x36zCEGilGpB1m-V4gmjg.*
201. *YouTube — Elite Context Engineering with Claude Code (Kf5-HWJPTIE).* https://www.youtube.com/watch?v=Kf5-HWJPTIE
202. *YouTube — One Agent Is NOT ENOUGH: Agentic Coding BEYOND Claude Code (M30gp1315Y4).* https://www.youtube.com/watch?v=M30gp1315Y4
203. *developereducators.com/channel/indydevdan/ — channel metadata listing.*
204. *agenticengineer.com — companion course site (principled-ai-coding, tactical-agentic-coding, top-2-percent-agentic-engineering).* https://agenticengineer.com

### coleam00 — §7.E2 + §7.E4 (@ColeMedin)

205. Medin, C. (2026). *coleam00 — full repository listing.* https://github.com/coleam00?tab=repositories
206. Medin, C. (2026). *Archon — README at dev and main; releases page; CONTRIBUTING.md; .claude/skills/archon.* https://github.com/coleam00/Archon
207. Medin, C. (2026). *context-engineering-intro — README; claude-code-full-guide directory.* https://github.com/coleam00/context-engineering-intro
208. Medin, C. (2026). *principles-of-agentic-engineering — workshop repo (AI layer concept, PIV loop, 15 reusable Claude Code commands).*
209. Medin, C. (2026). *local-ai-packaged — Ollama + Supabase + n8n + Open WebUI single-package local stack.*
210. Medin, C. (2026). *ottomator-agents — open-source agents on Live Agent Studio.*
211. Medin, C. — *GAN-inspired three-agent harness (generator vs adversarial evaluator) — referenced on profile.*
212. Medin, C. — *"second-brain" / Claude-Code-memory companion repos.*
213. Medin, C. (2026). *YouTube channel — @ColeMedin/shorts header observation.* https://www.youtube.com/@ColeMedin/shorts
214. *YouTube — Introducing Archon - The Revolutionary Operating System for AI Coding (8pRc_s2VQIo).* https://www.youtube.com/watch?v=8pRc_s2VQIo
215. *YouTube — Cole Medin Archon introduction (GjR5UsVGE60).* https://www.youtube.com/watch?v=GjR5UsVGE60
216. *linkedin.com/in/cole-medin-727752184/ — bio.*

## §13.8 Sources cited in §8 — Stratum F knowledge aggregators

217. ai-boost. (2026). *awesome-harness-engineering — root README, multilingual variants.* https://github.com/ai-boost/awesome-harness-engineering
218. *github.com/mseeks/awesome-harness-engineering-1 — mirror.*
219. Mele, A. / meleantonio. (2026). *ChernyCode — root README; threads.md; CLAUDE.md; claude_subagents/code-reviewer.md.* https://github.com/meleantonio/ChernyCode
220. *blog.andreszenteno.com/notes/github-trending-today-22-… — secondary trending listing.*
221. *github.com/bcherny — Boris Cherny profile.*
222. *x.com/antoniomele101/status/2017930909983309841 — X thread reference.*

## §13.9 Sources cited in §9 — Stratum G approach experiments

223. ruvnet / Agentics Foundation. (2026). *ruflo — root README; docs/USERGUIDE.md; releases page including Ruflo v3.6.10 notes; wiki Home and Goal Module pages.* https://github.com/ruvnet/ruflo
224. *sitepoint.com — Deploying Multiagent Swarms with Ruflo*. https://www.sitepoint.com/deploying-multiagent-swarms-with-ruflo-…
225. *cdn.jsdelivr.net/gh/ruvnet/ruflo@main/scripts/install.sh — installer.*
226. HumanLayer. (2025). *agentcontrolplane — root README; contributors page; .cursorrules; .github/CODEOWNERS.* https://github.com/humanlayer/agentcontrolplane
227. *pkg.go.dev/github.com/humanlayer/agentcontrolplane/acp/test/e2e/getting_started — license attestation.*

## §13.10 Sources cited in §10 / §11 — Synthesis matrices (internal references only)

Session F (§10–§11) is synthesis-only against the catalog substrate produced in Sessions A–E plus Cluster 5 V2 §3. No external sources are consulted in Session F. Internal references:

228. *Catalog body §2 — Stratum A research artifacts* (this document).
229. *Catalog body §3.priority + §3.standard — Stratum B production harnesses* (this document).
230. *Catalog body §4 — Stratum C emerging harnesses* (this document).
231. *Catalog body §5–§9 — Stratum D / D-meta / E / F / G* (this document).
232. *Cluster 5 V2 §3 Topic 3 — "Cross-Cutting Tradeoffs as Project-Wide Architectural Synthesis", Decision-ordering DAG.* Project knowledge base file: `Agent_Harness_Architecture__Deployment_Surfaces__Anthropic_Primitives__and_Foundational_Tradeoffs.md`.
233. *Triaged Source Inventory — Pattern Reference Catalog Pre-Construction.* Project knowledge base file: `Triaged_Source_Inventory__Pattern_Reference_Catalog_Pre-Construction.md`. Cited throughout for entry inventory, URL-anomaly reconciliation, multi-tag membership rationale, and v1.1 candidate-addition deferrals.

---

*End of Pattern Reference Catalog v1.0.*
