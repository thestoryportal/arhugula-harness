# Evidence → DESIGN.md Map  *(connective tissue — navigation only)*

**What this is:** a router from the council's open questions, workstreams, and tensions to the evidence in `03-evidence/` that bears on each. It describes *what evidence exists and where*, and **makes no recommendations** — every decision remains the council's / DESIGN.md's. Where a row notes an industry-convergence finding, that is reported as corpus evidence to weigh, not a call.

**Evidence docs (legend):**
- **[EVID]** `memory-corpus-evidence-for-council.md` — empirical analysis of *this* harness's 169-note memory graph.
- **[BROAD]** `notebooklm-research-findings-for-council.md` — open-question answers + per-voice canon + decision-moving inputs.
- **[DEEP]** `notebooklm-deep-dive-findings.md` — 6 mechanism deep-dives (1 ICM · 2 Claude Code cache · 3 Letta-on-files · 4 Zep staleness · 5 eval gates · 6 artifact taxonomy).

---

## Open questions → evidence

| Q | The council's open call | Evidence to weigh (where) | What's there (neutral) |
|---|---|---|---|
| **Q#1** | Home-of-record for `tools/hooks/` exec (HARDENING_PLAN vs council PLAN) | [BROAD Part A Q#1] | Notes this is an org/ownership call with no corpus/empirical evidence; nothing external adjudicates it. |
| **Q#2** | FM-H: detection-first vs prophylactic serialization | [BROAD A Q#2]; [DEEP Dive 4]; [EVID Finding 4 + C9 note] | Industry pattern (OCC detection-first; Cursor's lock→OCC pivot); recovery options (git-as-state, shadow-git); never-overwrite supersede model; the cost of the un-git-versioned store (silent drift). |
| **Q#3** | Proportionality: which WS / gates are MVP | [EVID Findings 2+3]; [BROAD A Q#3]; [DEEP Dive 5; Dive 6.3] | Counted dead-weight (23% zero-inbound) + degree-tiering; evidence that advisory caps drift (OpenAI 1-min-gate precedent); eval-gate thresholds that define "safe to ship"; component size budgets. |
| **Q#4** | `AGENTS.md` auto-load assumption | [BROAD A Q#4]; [DEEP Dive 6.1 (AGENTS.md row); Dive 1] | Claude Code auto-loads `CLAUDE.md`, not `AGENTS.md`; `AGENTS.md` auto-loads under Codex/Agents-SDK (AAIF) — a cross-runtime portability fact for the anchor-naming choice. |
| **Q#5** | Cut-list ownership / retention tiering | [EVID Findings 1+2+3]; [BROAD A Q#5]; [DEEP Dive 3; Dive 6.1 (Cline memory-bank)] | The hub set + the 39-note zero-inbound cut-list + degree-vs-prefix tiering; CoALA / Letta tier taxonomy + reference-count archival signal; Letta-on-files mechanics; Cline `memory-bank/` bounded-file split. |

## Workstreams → evidence

| WS (owner) | Evidence to weigh (where) | What's there (neutral) |
|---|---|---|
| **WS-1** CLAUDE.md slim (C2 ×C5/C7/C9) | [DEEP Dive 2]; [EVID Finding 1]; [DEEP 6.2/6.3]; [BROAD Part C #5/#6] | Claude Code cache mechanics (static-prefix → breakpoint → dynamic-suffix; `cache_read`>0.60; silent-zero-cache); the load-always hub core; instruction-file format (MD+XML) + size norms; the §2-churn-as-cache-detonation framing. |
| **WS-2** Navigation infra (C2 ×C1) | [DEEP Dive 1]; [DEEP 6.1 + 6.5#2]; [BROAD A Q#4] | ICM (numbered stages, `CONTEXT.md` Inputs/Process/Outputs, selective section routing, docs-over-outputs); the established navigation-file set (ARCHITECTURE/WORKFLOWS/MEMORY-ToC) + Cline `memory-bank/`; the `AGENTS.md` loading fact. |
| **WS-3** Retention contracts (C3 ×C5/C7/C9) | [DEEP Dive 3; Dive 4]; [EVID Findings 2+3]; [BROAD A Q#5]; [DEEP 6.1 + 6.5#4] | Letta-on-files tiers + consolidation/reflection; bi-temporal `valid_until`/`superseded_by` + Mark-and-New + staleness loop; the cut-list + degree signal; CoALA/Letta taxonomy; MD-vs-JSON format split for durable-vs-machine-state. |
| **WS-4** Conformance gates (C5) | [BROAD A Q#3]; [DEEP Dive 5]; [EVID Finding 4]; [DEEP Dive 1; 6.4] | Advisory-caps-drift evidence; the tiered eval-validator cascade + thresholds (TPR/TNR/κ); link-integrity + index-coverage gate candidates; ICM binary-pass stage-audits; the structural-vs-heuristic hard/advisory boundary. |
| **WS-5** Health observability (C7 ×C11) | [DEEP Dive 2]; [BROAD Part B (C7)]; [DEEP Dive 5; 6.3] | Cache signals (`cache_read`/`cache_creation`, silent-zero-cache); context-rot detection (positional bias, embedding drift, Dumb-Zone 40–60%); eval health metrics; size thresholds (35-min wall, lost-in-middle, 95–98% compaction). |
| **WS-6** Recovery completeness (C9 ×C3) | [DEEP Dive 2; Dive 4]; [BROAD Part B (C9)]; [DEEP Dive 5] | Tiered compaction + recovery primitives (feature_list re-read, git-as-state boot, Ralph loop); supersede/rollback model; the continuation probe for resume-after-reset. |
| **X** FM-H write serialization (C3 ×C9) | [BROAD A Q#2]; [DEEP Dive 4]; [EVID C9 note] | parallelize-reads-serialize-writes (orchestrator-worker); OCC + git-as-state; never-overwrite supersede; the un-versioned-store finding. |

## Tensions → evidence

| Tension | Evidence to weigh (where) | What's there (neutral) |
|---|---|---|
| **T1** provenance placement (C2↔C3, permanent) | [DEEP Dive 2]; [DEEP Dive 3 / 6.5]; [EVID Finding 1] | Cache rule (volatile content below a breakpoint); the semantic-store home for at-rest provenance; the hub-vs-tail split. |
| **T2** byte-budget gate (C5↔C2, closed) | [BROAD A Q#3] | Corroborating evidence that advisory caps drift (the closed tension's basis). |
| **T3** legibility-vs-eviction (C7↔C2) | [DEEP Dive 1]; [EVID Finding 1] | ICM navigable INDEX + section routing as the legibility-preservation mechanism; the hub map. |
| **T4** sequence slim-down vs recovery (C9↔C2) | [DEEP Dive 5]; [DEEP Dive 6] | Eval gates that make "did the slim-down regress?" testable rather than sequenced-by-assumption. |
| **T5** memory-store recovery (C9↔C3) | [BROAD A Q#2]; [DEEP Dive 4] | git-as-state / shadow-git recovery; the supersede/validity model. |
| **T6** loop fault-handling-as-topology (C1↔C9) | [BROAD Part B (C1)] | Orchestrator-worker write-serialization + concurrency-cap patterns (lighter corpus coverage; flagged as such). |

## Per-voice quick index
- **C2** → ICM [DEEP Dive 1] · cache [DEEP Dive 2] · taxonomy [DEEP Dive 6] · load-always core [EVID Finding 1].
- **C3** → Letta-on-files [DEEP Dive 3] · staleness [DEEP Dive 4] · CoALA/reference-count [BROAD A Q#5] · cut-list/degree/dead-links [EVID Findings 2/3/4] · `memory-bank/` [DEEP 6.1].
- **C5** → eval cascade + thresholds [DEEP Dive 5] · advisory-fails [BROAD A Q#3] · ICM audits [DEEP Dive 1] · gate candidates [EVID Finding 4].
- **C7** → cache signals [DEEP Dive 2] · context-rot/Dumb-Zone [BROAD Part B] · size thresholds [DEEP 6.3].
- **C9** → recovery primitives [DEEP Dive 2] · supersede/rollback [DEEP Dive 4] · continuation probe [DEEP Dive 5].
- **C1** → orchestrator-worker / concurrency caps [BROAD Part B] · ICM × hooks composition [DEEP Dive 1].

---

*Routing index only. The cited evidence is input to the council's deliberation; this map asserts no conclusion. For the composed-design picture (how ICM + cache-aware prefix + Letta-on-files + temporal frontmatter + eval gates relate), see [DEEP] "Composed picture" + Dive 6.5 — also presented as evidence, not a decision.*
