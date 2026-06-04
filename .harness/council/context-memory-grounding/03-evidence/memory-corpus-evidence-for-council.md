# Memory-Corpus Evidence — input for the Context/Memory Grounding Council

*Standalone, additive evidence for **DESIGN.md** (Stage 3). Generated 2026-06-04 from the live 169-note durable memory store via CodeFlow (graph lens) + ground-truth link parse. **Does not modify any worktree deliberation artifact** — drop into `…/context-memory-grounding/03-evidence/` if DESIGN.md wants it inline. Reproducible via `/tmp/mem_graph2.py`; CodeFlow JSON at `~/Downloads/codeflow-report.json`.*

Primary voices: **C2** (context engineering), **C3** (state/memory persistence). Consultants: C1/C5/C7/C9. This doc targets the council's **two still-open, data-discriminable questions** — proportionality/MVP ranking (Q#3) and cut-list/retention-tiering (Q#5) — and footnotes the qualitative findings the council already closed.

## Method (and a C7 caveat)
- **CodeFlow** (served at `localhost`) rendered the store as a wiki-link graph: 169 notes, 526 links, grade A (cosmetic). Used for visual topology + its computed "5 highly-coupled / 28 circular-dep" issues.
- **Ground-truth parse** of both `[[wiki]]` and `[md](slug.md)` links, **excluding MEMORY.md index spokes**, isolates the *semantic* (body-to-body) graph: **169 notes · 452 edges · density 2.67/note.**
- **C7 note (one line):** CodeFlow's non-graph engines misfire on prose — its 1 "Hardcoded Secret" is a regex literal quoted in a memory body (false positive; no real leak), its "React/VBA patterns" are keyword false-matches, churn=0 (the store isn't git-versioned). **Wire only CodeFlow's graph topology into any memory-health surface; never its security/pattern/grade engines.**

## Finding 1 — The load-always core is tiny and concentrated  *(C2: JIT-loading / what-to-load)*
Top semantic (body-to-body) in-degree:

| note | in-degree |
|---|---|
| `advisor-before-substantive-work-for-cross-axis-blockers` | **65** |
| `halt-route-split-ac-pattern` | 27 |
| `verification-shape-sharpened-grep-vs-e2e` | 26 |
| `fork-h-t-cp-19-default-gate-level-spec-extension` | 10 |
| `phase-7-bootstrap-status`, `use-the-product-probe-pattern` | 9 |
| `design-substrate-divergence`, `feedback-…-no-paid-calls`, `fork-cp-is-wiring-gaps`, `fork-u-rt-44-workflow-loop-drain` | 8 |

- Top 3 hubs absorb **118/452 edges (26%)**; ~20 notes have in-degree ≥5. **This is the load-always pattern spine.** Everything else is load-on-demand.
- **C2 JIT discipline, made concrete:** pin the in-degree-≥5 set into the re-attended layer; reach the rest only via the MEMORY.md index (WS-2 navigation).

## Finding 2 — 23% of notes have ZERO semantic inbound: the counted cut-list  *(C3 WS-3 retention; C2 WS-1 slim; OPEN Q#5)*
- **39/169 notes (23%) are reachable only through the MEMORY.md index** — no note links to them. (A naïve parse that counts the index's own spokes reports "0 orphans" — an artifact; excluding index spokes surfaces the real set.)
- These bloat the over-cap index (27,051B > 24,400B) **without contributing to the semantic web** → the WS-3 Tier-5 archive / JIT-load candidates.

## Finding 3 — Tier by DEGREE, not by prefix  *(resolves episodic-vs-semantic; OPEN Q#3 proportionality)*
"Episodic ⇒ archive" is too coarse. Zero-inbound vs load-bearing, per topic-prefix:

| prefix | total | zero-inbound (archive cand.) | load-bearing |
|---|---|---|---|
| `pr-*` | 29 | **14** | 15 |
| `fork-*` | 28 | 3 | **25** |
| `h-*` (retirement) | 17 | 1 | 16 |
| `u-*` | 9 | 1 | 8 |
| `phase/advisor/finding-*` | 17 | 0 | 17 |
| singleton reference/recipe tail | ~30 | ~13 | ~17 |

- **`fork-*` is 25/28 load-bearing** (e.g. `fork-h-t-cp-19` = 10 inbound) → never archive forks by category.
- **`pr-*` splits ~50/50** → the **14 zero-inbound PR event-logs** are the cleanest archive tier (write-once episodic records).
- **Cut-list selection key = body-to-body in-degree, prefix only as tie-breaker.**

## Finding 4 — Integrity gaps are real but far smaller than the flat count  *(C3 retention contract; C5 gate; C9 recovery)*
The 68 raw "dead links" categorize:

| bucket | n | meaning |
|---|---|---|
| **A** — `.harness/` cross-ref that **exists** | 8 | Valid cross-store refs (`class_1_tension_u_rt_59_*` underscore fork docs). **Not defects** — but expose a **naming-convention drift**: memory = kebab-case, `.harness/` = underscore; cross-store links silently read as "dead." Cross-store refs aren't first-class. |
| **B** — code/config false-positive | 8 | TOML/spec fragments in bodies parsed as links (`[[path_bindings.raw_entries]]`, `[[steps]]`, `[[tool.pyright.executionEnvironments]]`). **A link-integrity gate must skip code-fenced content.** |
| **C** — naming-drift, **true break** | 3 | Dead link is a substring of a real slug: `[[test-bypass-as-runtime-truth]]` (3×) → real `…-pattern`; `[[landed-substrate-pending-upstream-loop-substrate]]` → `…-sub-species`; `[[verify-observation-layer-…]]` → `feedback-verify-…`. **The genuine broken links.** |
| **D** — unwritten pattern / gap | 20 | `[[plan-revision-against-not-yet-built-substrate]]` (5×) + `[[strike-revision-on-refined-second-tier-reason]]` (4×): referenced repeatedly, never written as notes (live only in CLAUDE.md/workflow doc). Mostly sanctioned placeholders (CLAUDE.md blesses `[[name]]`-before-file); ≥4-ref ones worth promoting. `[[checkpoint-2026…]]` = memory→checkpoint ref (C3 tier-boundary leak). |

- **Actionable now: ~3 true breaks (C) + promote the 2 high-ref unwritten patterns (D).** "68 defects" is wrong; the real story = naming-drift + parser-pollution + a sound (sanctioned) placeholder convention.

## Recommendations mapped to the OPEN questions
- **Q#3 (proportionality / MVP):** evidence supports **WS-1 + WS-3 as MVP-load-bearing** (23% counted dead-weight in the over-cap index). Adds a concrete, cheap **WS-4 gate beyond byte-budget**: a **link-integrity + index-coverage `--check`** (catches the 3 bucket-C breaks and the 1 currently-unindexed note; mirrors `substitution_ledger.py --check`, exits 1). WS-5 full dashboard stays defer-able — a single periodic memory-health line (orphan %, density, true-break count) covers the need.
- **Q#5 (cut-list / retention tiering):** degree-keyed, counted —
  - **KEEP-HOT (pin, never evict):** in-degree ≥5 (~20 notes — the spine).
  - **KEEP-LINKED (in graph, index-navigable):** in-degree 1–4 (bulk of `fork-`/`h-`/`finding-`).
  - **ARCHIVE/JIT (out of re-attended index → Tier-5 `.harness/`):** the **39 zero-inbound notes** (14 `pr-` + singleton recipes).
- **C5 gates (WS-4):** (1) link-integrity `--check`; (2) index-coverage `--check`; (3) code-fence-aware link parsing (eliminates bucket B).
- **C3 cross-store convention:** formalize memory↔`.harness/` references (bucket A) — kebab-vs-underscore drift makes valid cross-store links read as dead; a first-class cross-store link form closes it. Also the `[[checkpoint-…]]` ref is a memory→transient-tier leak to seal.
- **C9:** the store isn't git-versioned (already a council finding); Finding 4 shows the *cost* — no integrity check, so drift/breaks (3 already) accumulate silently. Recovery (version/snapshot the store) + the integrity gate compose.
