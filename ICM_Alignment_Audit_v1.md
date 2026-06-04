# ICM Alignment Audit — `arhugula-v2`

*Read-only assessment of the repo's alignment with the **Interpreted Context Methodology (ICM)** in structure, flow, and hygiene. Authored to establish the foundation for designing requirements, a spec, and a plan to adopt ICM.*

| Field | Value |
|---|---|
| Audit type | Read-only (no source files modified) |
| Repo HEAD | `557f219c` |
| Date | 2026-06-04 |
| Method | 4 parallel fan-out audit sub-agents against a 23-element rubric |
| ICM sources | `github.com/RinDig/Interpreted-Context-Methdology` (accessed 2026-06-04); `arxiv.org/html/2603.16021v2` — Van Clief, *"Model Workspace Protocol: Folder Structure as Agent Architecture"* (2026) |
| **Overall alignment** | **15.5 / 23 = 67.4%** — but the flat number hides the story (see §4) |

---

## 1. Scope and framing

### 1.1 Which audit this is

"Align *the repo* with ICM" has two readings. This audit takes the **workspace-methodology reading (A)** — *how well this repo's own organization (how it structures its design→build process for Claude Code) matches ICM's folder-structure-as-architecture*. The task phrase "its structure, flow, hygiene" points unambiguously at (A).

The **product reading (B)** — making the harness being built (`H_T`) implement ICM internally — is **out of scope**. When §8 says "implement ICM seamlessly," it means adopting ICM's *workspace* discipline, **not** rewriting `H_T`.

### 1.2 The reconciliation constraint (read this before any "fix")

ICM explicitly scopes itself **out of** "real-time multi-agent collaboration, high-concurrency systems, and complex automated branching." That is *precisely* the class of system this repo (a) **builds** — a multi-LLM harness with 6 topology patterns, orchestrator-workers, durable execution — and (b) **uses to build it** — an 11-voice council, a Workflow multi-agent fan-out tool, 5 sub-agents, autonomous loop mode.

**Therefore "implement ICM" cannot mean wholesale conversion.** It means *reconciliation*: identify which ICM principles are adoptable for the **workspace governance layer** vs which conflict with committed, load-bearing constraints. A naive "shrink CLAUDE.md to 800 tokens" recommendation would destroy a governance system the repo documents as essential. The next-steps in §8 are framed as reconciliation, not teardown.

---

## 2. The standard being audited against (ICM in one page)

ICM = *"folder structure as agent architecture."* Thesis: **"if the prompts and context for each stage already exist as files in a well-organized folder hierarchy, you do not need multiple agents or a coordination framework."**

**5 design principles:** (1) One Stage, One Job · (2) Plain-Text Interface · (3) Layered Context Loading · (4) Every Output is an Edit Surface · (5) Configure the Factory, Not the Product.

**5-layer context hierarchy (with token targets):**

| Layer | File | Purpose | Target |
|---|---|---|---|
| L0 | `CLAUDE.md` | Global identity / orientation | **~800 tok** |
| L1 | `CONTEXT.md` | Task routing | **~300 tok** |
| L2 | Stage `CONTEXT.md` | Stage contract | **200–500 tok** |
| L3 | `references/` | Stable "factory" rules | 500–2k tok |
| L4 | `output/` | Per-run working artifacts | varies |

Goal: **2,000–8,000 focused tokens per stage**. Named anti-pattern: **30,000–50,000 monolithic tokens.**

**Prescribed structure:** numbered `stages/NN-name/` folders, each with `CONTEXT.md` + `references/` + `output/`; `_config/`, `shared/`, `skills/`, `setup/questionnaire.md`.

**Stage contract:** every stage `CONTEXT.md` carries 3 sections — **Inputs table** (Source | File | Section | Why) · **Process** (numbered steps) · **Outputs table** (Artifact | Location | Format).

**Conventions:** one-way references · canonical sources (one home per fact) · selective section routing · specs-as-contracts (WHAT/WHEN not HOW) · docs-over-outputs.

**Hygiene:** `CONTEXT.md` < 80 lines · reference files < 200 lines · outputs uncommitted (only `.gitkeep`) · no circular deps · stage audits (pass/fail checklists).

---

## 3. Audit methodology

Four read-only sub-agents ran in parallel, each carrying the full distilled ICM model and owning a rubric slice; each returned present(1)/partial(0.5)/absent(0) scores with byte/line counts, file lists, and verbatim quotes. The orchestrator verified the one cross-agent discrepancy (CONTEXT.md count) directly against HEAD. Scoring is element-counted, not impressionistic, so every percentage is reproducible from the appendix.

---

## 4. Scorecard

| Category | Elements | Score | % | Read |
|---|---|---|---|---|
| **Principles** | 5 | 4.5 | **90%** | values deeply aligned |
| **Conventions** | 5 | 4.5 | **90%** | values deeply aligned |
| **Layers** | 5 | 2.5 | **50%** | structure inverted |
| **Stage contract** | 3 | 1.5 | **50%** | beachhead only |
| **Hygiene** | 5 | 2.5 | **50%** | caps violated wholesale |
| **TOTAL** | **23** | **15.5** | **67.4%** | — |

**The number that matters is the split, not the 67%:**

| Cluster | Elements | Score | % |
|---|---|---|---|
| **VALUES** (Principles + Conventions) | 10 | 9.0 | **90%** |
| **STRUCTURE + HYGIENE** (Layers + Stage contract + Hygiene) | 13 | 6.5 | **50%** |

> **The repo is ~90% aligned with ICM's *values* and ~50% aligned with ICM's *structure and minimalism*.** It already practices filesystem-as-source-of-truth, one-way references, canonical sources, plain-text interfaces, human edit-surfaces, and stage-audits — the ICM *philosophy*. It diverges sharply on token budgets, the numbered-stage `CONTEXT.md` layering, and the framework-replacement minimalism — the ICM *form*.

Per-element detail in Appendix A.

---

## 5. Headline findings

### 5.1 The token-budget chasm (the single most consequential metric)

| Measure | Bytes | Est. tokens (B/4) | Lines | vs ICM target |
|---|---:|---:|---:|---|
| Root `CLAUDE.md` (L0) | 342,823 | **85,705** | 762 | **~107× over** the ~800-tok L0 budget |
| `MEMORY.md` (auto-loaded) | 11,712 | 2,928 | 60 | — |
| **Session-start load (global)** | 354,535 | **88,633** | — | **2.95× the 30K anti-pattern; 1.77× the 50K** |
| Worst-case load (+4 axis CLAUDE.md) | 485,970 | **121,492** | — | **4.05× / 2.43×** |

The root `CLAUDE.md` **alone** (85.7K tokens) is **2.86× ICM's 30K-token monolithic anti-pattern** and **~11–60× ICM's 2–8K per-stage goal**. ICM was authored to fix exactly the 30–50K monolithic load; this repo's standing load is **2.4–4.0× that figure.** Every session — design-phase, Phase-7 impl, or a one-line roadmap refresh — eats the same ~335 KB preamble carrying the entire CXA version-history saga and every spec's full change-note lineage (CP spec v1.30→v1.6, OD v1.27→v1.9, runtime v1.41→v1).

This is **principle 3 (Layered Context Loading) inverted at scale** — and it is the repo's single largest, most mechanically-fixable ICM debt.

### 5.2 The philosophical inversion (the deepest finding)

ICM's thesis is *"you don't need multiple agents or a coordination framework."* **This repo is the photographic negative:** it is *building* a coordination framework (`H_T`: 6 topology patterns incl. orchestrator-workers, retry/breaker, durable execution) and *using* coordination machinery to build it (council §10.7, Workflow fan-out §13.2, 5 sub-agents per `Sub_Agent_Boundary_Specification_v1.md`, loop mode).

The precise inversion: **ICM treats the file hierarchy as a *replacement* for agents; this repo treats the file hierarchy (`design-substrate/`, `.harness/`, atomic-unit plans) as the *coordination medium for* agents** — the council, sub-agents, and Workflow tool all read/write the same plain-text ledger. The repo adopts ICM's *filesystem-as-coordination-medium value* while rejecting ICM's *conclusion that this obviates multi-agent machinery.*

**Second-order irony (a genuine asset, §7):** the repo's own §13.3 retrospective half-concedes ICM's point — *"the verification disciplines (§13.1, cheap) catch the bugs — not raw reasoning depth or multi-agent fan-out"* and *"Ultracode is NOT a standing default."* The repo **empirically discovered, from the other direction, that its cheap file-based disciplines beat its heavy multi-agent machinery** — which is ICM's core claim.

### 5.3 ICM is already partially adopted in-repo (the foundation fact)

Contrary to a first impression of "ICM is foreign here," the repo contains **two working ICM beachheads** and a third reference:

1. **`.harness/spec-code-overlay/`** — *full canonical ICM.* Its root `CONTEXT.md` states verbatim: *"**Layout:** canonical ICM (`RinDig/Interpreted-Context-Methdology`). Root `CONTEXT.md` routes; numbered `stages/NN-*/` each carry their own `CONTEXT.md` (Inputs/Process/Outputs), `references/`, `output/`. Empty layers (`_config/`, `shared/`, `skills/`, `setup/`) are **not** pre-stubbed — they materialize when a stage needs them (anti-bloat)."* Its `stages/01-exploration/CONTEXT.md` is headed *"# CONTEXT — stage 01: exploration (Layer 2: stage contract)"* with literal `## Inputs` / `## Process` (numbered) / `## Outputs` sections and a real `output/` dir.
2. **`.harness/council/context-memory-grounding/`** — numbered sequential stage dirs `01-council → 02-adversarial → 03-evidence`/`03-codex-advisor → 04-reconciliation` (ICM-flavored sequencing; no `CONTEXT.md` contracts yet).
3. **`_bmad/CONTEXT.md`** — vendored runtime, *"Laid out per ICM directory discipline."*

**Implication:** adopting ICM more broadly is not greenfield. There is a **proven, canonical-citing in-repo template** to scale from. This is the strongest possible starting point for §8.

---

## 6. Detailed findings by category

### 6.1 Principles — 4.5 / 5 (90%)

| Principle | Score | Evidence |
|---|---|---|
| One Stage, One Job | **1.0** | Atomic units `U-{IS,AS,CP,OD,RT}-NN` (IS=17, CP=80, runtime=110), one transformation each. Single-purpose skills with explicit NOT-clauses (`spec-writer` *"applies a fix already decided; does not decide, does not red-team"*). Role separation architect→spec-writer→planner→reviewer. |
| Plain-Text Interface | **1.0** | `design-substrate/*.md`, 45 `class_*_fork_*.md`, 21 clearance markers, 50 retirement-batch `.md`, `roadmap_status.md`, `substitutions.yaml`. Methodology state is fully plain-text. (The product's SQLite/OTel storage is the *deliverable*, not the methodology interface.) |
| Layered Context Loading | **0.5** | Per-axis `CLAUDE.md` + event-driven skills express the value, but the 335 KB always-loaded root `CLAUDE.md` is "everything-at-once," and the per-axis files load *additively*, not *substitutively*. See §5.1. |
| Every Output is an Edit Surface | **1.0** | Class-1 fork halts + `AskUserQuestion` ratification = ICM "checkpoints." `design-substrate/*.md` and fork docs are the editable intermediates. X-AL-3 CI guard + adversarial reviewer = "stage audits before writing output." |
| Configure the Factory, Not the Product | **1.0** | Clean factory (`settings.json`, `pyproject.toml`, `justfile`, `.mcp.json`) vs product (`harness.toml` runtime config) separation. §11 posture model is configure-once. |

### 6.2 Layers — 2.5 / 5 (50%)

| Layer | Score | Evidence |
|---|---|---|
| L0 present + budget | **0.5** | Present but **~107× over** the ~800-tok target (85.7K tok). |
| L1 present + budget | **0** | No workspace task-routing `CONTEXT.md`. The 3 `CONTEXT.md` that exist are scoped to `.harness/` subtrees + `_bmad/`, not the workspace root. |
| L2 present + budget | **0** | One stage `CONTEXT.md` exists (`spec-code-overlay/stages/01-exploration/`), but it is a bounded beachhead, not a per-stage layer across the workspace. (Scored 0 at the workspace-architecture layer; the beachhead is credited under Stage Contract §6.3.) |
| L3 present | **1.0** | Rich stable factory layer: `design-substrate/*`, per-axis `CLAUDE.md`, `.claude/skills/` (38), `research/` (Pattern Reference Catalog + cluster deep-dives). |
| L4 present + uncommitted | **1.0** | `_bmad/CONTEXT.md`: *"Outputs are not committed."* `.harness/.checkpoints/` keep-10 prune. Per-run artifact areas are separated. |

Per-axis CLAUDE.md sizes (the closest L2-analog, all far over the 200–500-tok ceiling):

| File | Bytes | Est. tok | Lines |
|---|---:|---:|---:|
| `harness-is/CLAUDE.md` | 17,444 | 4,361 | 202 |
| `harness-as/CLAUDE.md` | 29,032 | 7,258 | 238 |
| `harness-cp/CLAUDE.md` | 38,031 | 9,507 | 250 |
| `harness-od/CLAUDE.md` | 46,928 | 11,732 | 240 |

### 6.3 Stage contract — 1.5 / 3 (50%)

The Inputs/Process/Outputs convention is **demonstrably present and canonically understood** — but only inside the `.harness/spec-code-overlay/` beachhead and not as the workspace's organizing architecture. Each of the 3 rows scores 0.5: the convention exists in-repo (verbatim, citing the canonical ICM repo) but the primary workspace (axis packages, design-substrate, skills) uses a different idiom — **Authority chain + Posture precondition + Activation surface** rather than Inputs/Process/Outputs. The numbered-stage convention `stages/NN-name/` is present in 2 bounded `.harness/` subtrees, absent at the root.

**Repo construct → ICM analog map:**

| Repo construct | ICM analog | True ICM stage? |
|---|---|---|
| `.harness/spec-code-overlay/stages/NN-*/` | Stage folder + 3-section contract | **Yes** (explicit canonical adoption) |
| `.harness/council/context-memory-grounding/NN-*/` | Numbered sequential stages | Partial (numbered, one-way; no `CONTEXT.md`) |
| Phase-7 sub-phases 7a→7b→7c→7d | Numbered execution-order stages | Partial (sequential, one-job — but governance tables, not folders) |
| `harness-{is,as,cp,od,cxa,core,runtime}/` | Separation-of-concerns boundaries | No (parallel axes, not sequential stages) |
| `design-substrate/*.md` | L3 factory rules | Partial (stable refs; flat version-suffixed; no contract) |
| `.claude/skills/` (38) | L3 factory / domain knowledge | Partial (bundled knowledge; activation-framed, not I/P/O) |

### 6.4 Conventions — 4.5 / 5 (90%)

| Convention | Score | Evidence |
|---|---|---|
| One-way references | **1.0** | §1.3 authority chain *"ADR → ADD → PRD → spec → plan → impl; earlier artifacts canonical for later."* Package import discipline (`harness-cp` must NOT import `harness-od`; str-literal cross-boundary). |
| Canonical sources | **0.5** | Doctrine stated (*"every piece of information has one home"*, delta-only convention) but undercut in practice: 30 coexisting CP spec versions (v1.2…v1.30), 27 OD plan files, and change-notes duplicated across root CLAUDE.md §2 + the spec file + per-axis CLAUDE.md + clearance markers. |
| Selective section routing | **1.0** | **The defining strength.** 1,300 `§N` citations in root CLAUDE.md (~1.7/line); 338 in a single sample spec. Byte-exact mandated (I-1, Workflow §7.4.2). |
| Specs-as-contracts | **1.0** | Clean WHAT/WHEN (specs: `C-IS-NN`, interfaces, acceptance) vs HOW (plans: `U-IS-NN`, signatures, files). §1.2 forbids specs as a design-extension surface. |
| Docs-over-outputs | **1.0** | §10.4 *"reference docs authoritative."* Phase-7 sessions consume cleared specs, not prior outputs, to learn patterns. |

### 6.5 Hygiene — 2.5 / 5 (50%)

| Hygiene rule | Score | Evidence |
|---|---|---|
| `CONTEXT.md` < 80 lines | **0** | Analog governance docs grossly over: root CLAUDE.md = 762 lines (~9.5× cap); 196 of 214 `design-substrate/*.md` over 80. |
| Reference files < 200 lines | **0** | 81 of 214 `design-substrate/*.md` over 200 (largest 4,654); 19 of 38 SKILL.md over 200 (largest 1,206); Pattern catalog 3,603; roadmap 2,189. |
| Outputs uncommitted / `.gitkeep` | **0.5** | Only **3** `.gitkeep` repo-wide. Generated artifacts committed: `tools/dashboard/roadmap.html` (a TRACKED snapshot), a `stages/01-exploration/output/` doc, multiple `*_Report*.md`, plus accidental copy-suffixed `Spec_Operational_Discipline_v1 (1).md`/`(2).md`. Partly mitigated by the deliberate regenerate-and-commit convention. |
| No circular dependencies | **1.0** | One-way authority chain + package import discipline + "DAG Kahn-acyclic" verified at each plan revision + X-AL-3 guard. |
| Stage audits | **1.0** | `harness-adversarial-reviewer`; `x-al-3-guard.yml` (pass/fail CI gate); `substitution_ledger.py --check` tally gate; clearance markers; `overlay-check`; P3/P5/P6-CK reviews; out-of-family Codex + transcript-aware `advisor()`. |

**Top-10 largest reference files (lines):** 4654 `Spec_Harness_Runtime_v1.md` · 3846 / 3813 CP plan v2.1/v2 · 3603 `Pattern_Reference_Catalog_v1.0.md` · 2863 / 2863 OD plan v2.1/v2 · 2339 `Spec_Control_Plane_v1_2.md` · 2338 AS plan v1 · 2189 `Project_Roadmap_v1.md` · 1670 `Spec_Action_Surface_v1.md`.

---

## 7. ICM-aligned assets to build on

These existing disciplines are genuine ICM-shaped strengths a methodology adoption can lift directly — they are why the values score is 90%:

1. **The `.harness/spec-code-overlay/` canonical-ICM beachhead** — a working, RinDig-citing `stages/NN-*/CONTEXT.md` template already in the repo. *Scale from this; don't reinvent.*
2. **Single-purpose role-skills with explicit NOT-clauses** — textbook "one stage, one job," already activatable.
3. **Plain-text fork-doc ledger** (45 `class_*_fork_*.md`) — ICM's "edit surface + checkpoint" at scale.
4. **X-AL-3 CI guard + clearance markers** — a working "stage-audit pass/fail before writing output," file-presence-checked.
5. **Sequential authority chain + byte-exact §-citation + `overlay-query`** — ICM's filesystem handoff, made *verifiable*.
6. **Factory/product config separation** (`settings.json` vs `harness.toml`) — a clean, already-honored "configure the factory" boundary.
7. **The §13.3 retrospective insight** — the repo's *own measured evidence* that cheap file-based verification beats multi-agent fan-out: the strongest internal endorsement of ICM's thesis.

---

## 8. Next steps — foundation for requirements / spec / plan

Framed as **reconciliation** (§1.2), staged from cheapest-highest-leverage to most-invasive. Each is a candidate requirement line for an eventual ICM-adoption spec.

### Tier 1 — High-leverage, low-risk (the token-budget fix)
- **R-ICM-1 · Split the L0 monolith.** Decompose root `CLAUDE.md` (85.7K tok) into a true ~800-tok L0 orientation file + a router that *points to* sections loaded on demand. The historical change-note lineage (CXA saga, per-spec delta history) is the bulk and the least-needed-per-session — relocate it to a referenced `design-substrate/`-adjacent history doc. **This alone converts the one principle "partial" (Layered Context Loading) toward "present" and removes the repo's largest ICM debt.** *Caution:* this governance file is load-bearing; do it as a reviewable, posture-aware refactor with the existing `optimize-claude-md` skill, not a blind truncation.
- **R-ICM-2 · Introduce L1 `CONTEXT.md` at the workspace root** — a ~300-tok task-router that branches to design-phase vs Phase-7 vs mode-agnostic posture and points to the right L3 references. (The §11 posture model already supplies the logic; this externalizes it into the ICM L1 slot.)

### Tier 2 — Structural adoption (scale the beachhead)
- **R-ICM-3 · Promote `spec-code-overlay`'s ICM pattern to a first-class workspace convention.** Define which workspace workflows become numbered `stages/NN-*/` with `CONTEXT.md` contracts (candidates: the council workflow `01→04`, the roadmap loop, retirement-event batches). Reuse the canonical template already in-repo.
- **R-ICM-4 · Add Inputs/Process/Outputs tables to single-job skills.** The role-skills are already one-job; give the highest-traffic ones (`phase-7-implementation`, `roadmap-continue`, `council-orchestrator`) an explicit Inputs/Process/Outputs contract alongside their existing Authority-chain idiom.

### Tier 3 — Hygiene reconciliation (decide, don't blindly enforce)
- **R-ICM-5 · Reconcile the file-size caps.** ICM's <80/<200-line caps clash with the repo's spec/plan reality. *Decision needed:* adopt ICM caps for `CONTEXT.md`/router files only (recommended) while exempting `design-substrate/` specs as a documented divergence — or split large specs into sectioned references.
- **R-ICM-6 · Outputs-uncommitted discipline.** Decide per-artifact: keep deliberately-committed snapshots (`roadmap.html`) as documented exceptions; move genuinely-regenerable outputs behind `.gitkeep`'d `output/` dirs; clean the accidental `(1).md`/`(2).md` duplicates.
- **R-ICM-7 · Canonical-sources tightening.** Reduce change-note duplication across root CLAUDE.md / spec / per-axis CLAUDE.md / clearance markers toward genuine one-home-per-fact (the `overlay` already proves the cross-reference machinery exists).

### Tier 4 — Explicit non-goals (record the divergence; do not "fix")
- **N-ICM-1 · The product stays a coordination framework.** `H_T` (6 topologies, durable execution) is the deliverable and is correctly outside ICM's scope. Do not ICM-ify the product.
- **N-ICM-2 · Concurrency + multi-agent machinery stay.** Phase-7 7b parallel axis-streams, the council, sub-agents, Workflow fan-out, and §12.2.1 fixed-point branching are committed and effective. ICM is sequential-only; adopt its *values* in the governance layer without surrendering the repo's concurrency where it earns its keep (§13.3 already calibrates this).

### Operator decisions required before a spec
1. **Scope of adoption:** governance-layer-only (recommended) vs governance + selected workflows (Tier 2/3).
2. **Caps:** adopt ICM's <80/<200-line caps where, and exempt what (Tier 3, R-ICM-5)?
3. **L0 refactor appetite:** how aggressive on R-ICM-1 — the highest-leverage but most-invasive change to a load-bearing file?

---

## 9. Bottom line

The repo is a **values-aligned, structure-divergent** ICM case. It already lives ICM's philosophy — filesystem as source of truth, one-way references, canonical sources, plain-text everything, human edit-surfaces, stage-audits, single-job decomposition (**90% on values**) — and even carries two working ICM beachheads citing the canonical methodology. It diverges on ICM's *form and minimalism* (**50% on structure/hygiene**): a 335 KB always-loaded L0 that is 2.4–4.0× ICM's own monolithic anti-pattern, no workspace L1/L2 routing layer, and file-size caps violated wholesale.

The deepest truth is the **philosophical inversion**: this is a project to *build and operate* the multi-agent coordination machinery ICM says you don't need — and its own §13.3 retrospective quietly vindicates ICM from the inside. The realistic adoption target is therefore **reconciliation, not conversion**: take ICM's layered-context and stage-contract discipline into the *workspace governance layer* (Tiers 1–3, starting with the L0 split), and explicitly record the product's coordination-framework nature as a documented non-goal (Tier 4). The foundation for that spec is unusually strong because the repo already understands, cites, and partially practices ICM.

---

## Appendix A — Per-element rubric ledger (23 elements)

| # | Category | Element | Score |
|---|---|---|---|
| 1 | Principles | One Stage, One Job | 1.0 |
| 2 | Principles | Plain-Text Interface | 1.0 |
| 3 | Principles | Layered Context Loading | 0.5 |
| 4 | Principles | Edit Surfaces | 1.0 |
| 5 | Principles | Factory Config | 1.0 |
| 6 | Layers | L0 present + budget | 0.5 |
| 7 | Layers | L1 present + budget | 0.0 |
| 8 | Layers | L2 present + budget | 0.0 |
| 9 | Layers | L3 present | 1.0 |
| 10 | Layers | L4 present + uncommitted | 1.0 |
| 11 | Stage contract | Inputs table | 0.5 |
| 12 | Stage contract | Process | 0.5 |
| 13 | Stage contract | Outputs table | 0.5 |
| 14 | Conventions | One-way references | 1.0 |
| 15 | Conventions | Canonical sources | 0.5 |
| 16 | Conventions | Selective section routing | 1.0 |
| 17 | Conventions | Specs-as-contracts | 1.0 |
| 18 | Conventions | Docs-over-outputs | 1.0 |
| 19 | Hygiene | CONTEXT.md < 80 lines | 0.0 |
| 20 | Hygiene | Reference files < 200 lines | 0.0 |
| 21 | Hygiene | Outputs uncommitted / .gitkeep | 0.5 |
| 22 | Hygiene | No circular dependencies | 1.0 |
| 23 | Hygiene | Stage audits | 1.0 |
| | | **TOTAL** | **15.5 / 23 (67.4%)** |

## Appendix B — Key metrics

- Root `CLAUDE.md`: 342,823 B / **85,705 tok** / 762 lines — ~107× the ~800-tok L0 target.
- Session-start global load (root + MEMORY): 354,535 B / **88,633 tok** — 2.95× / 1.77× the 30K/50K anti-pattern.
- Worst-case load (+4 axis CLAUDE.md): 485,970 B / **121,492 tok** — 4.05× / 2.43×.
- `CONTEXT.md` files: **3** (`_bmad/`, `.harness/spec-code-overlay/`, `.harness/spec-code-overlay/stages/01-exploration/`). Zero at workspace root.
- Numbered `stages/NN-*/` convention: present in 2 `.harness/` subtrees; absent at root.
- `.gitkeep` files: 3 repo-wide.
- `§N` citations in root CLAUDE.md: ~1,300. In a sample spec: 338.
- `design-substrate/*.md`: 196/214 over 80 lines; 81/214 over 200 lines.
- SKILL.md files: 38; 19/38 over 200 lines.
- Coexisting versioned files: CP spec v1.2…v1.30; OD plan ~27 versions.

*— End of audit. Read-only; the only file written was this report.*
