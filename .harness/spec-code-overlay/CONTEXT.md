# CONTEXT — spec-code-overlay workspace  *(Layer 1: task routing)*

**Arc:** overlay the harness's **spec ↔ code ↔ CXA-edge ↔ substitution** semantic layer onto the code-structure graph, so drift between design-substrate and code is *visible and machine-checkable*.

**Status:** stages 01–03 complete (2026-06-04). The deterministic overlay shipped to
`tools/semantic_overlay/` (extractor + query CLI + drift linter + UA-KG enrichment), CI-gated
(`semantic-overlay` job) + justfile recipes (`just overlay{,-build,-check,-query}`). This
folder remains the development ledger; the shipped code lives in `tools/`.

**Layout:** canonical ICM (`RinDig/Interpreted-Context-Methdology`). Root `CONTEXT.md` routes; numbered `stages/NN-*/` each carry their own `CONTEXT.md` (Inputs/Process/Outputs), `references/`, `output/`. Empty layers (`_config/`, `shared/`, `skills/`, `setup/`) are **not** pre-stubbed — they materialize when a stage needs them (anti-bloat).

---

## Inputs (arc-level)

| Source | Use | Sections |
|---|---|---|
| The repo at HEAD (`harness-*/src`, docstring cites) | the spec↔code traceability layer to overlay | docstring authority cites (`C-*-NN`, `U-*`, `ADR-*`, `H_T-*`) |
| `tools/substitution_ledger.py` + `.harness/substitutions.yaml` | existing deterministic-derivation + CI-gate precedent (the *shape* to mirror) | whole |
| `design-substrate/Cross_Axis_Composition_Document_v2_19.md` | the CXA-edge half of the semantic layer | §2.3.x edge tables |
| understand-anything v2.7.6 (plugin) | candidate code-graph substrate; assessed, not assumed | knowledge-graph.json |
| `.harness/council/context-memory-grounding/` | sibling arc (interpretable-context/memory) — **compose, do not duplicate** | DESIGN.md when committed |

## Process (stages — one-way forward flow)

| Stage | Purpose | Status |
|---|---|---|
| `stages/01-exploration/` | ground the premise: is the traceability layer real, machine-extractable, worth overlaying? assess the tool. | ✅ complete |
| `stages/02-design/` | overlay JSON schema + the cross-reference linter contract; linter-only vs +visualization; fork-vs-sidecar | ✅ resolved (advisor framing): **one UA-format graph artifact, three consumers** (query CLI / dashboard-enrich / `--check`); sidecar not fork; CXA from code-resident `PATTERN_P1_SEAMS`, not delta-only markdown |
| `stages/03-build/` | the linter lands as code in **`tools/`** (not here); freshness hook; gate-vs-advisory | ✅ shipped at `tools/semantic_overlay/` — `overlay.py` (build/summary/check/query/json/enrich-ua) + `test_overlay.py` + `README.md`; CI gate `semantic-overlay`; `query`/`summary` always fresh, committed `overlay.json` `--check`-guarded; advisory orphan classes now cover code-without-cite, design-substrate contract-without-code, and substitution-without-carrier, while CXA missing endpoint remains the hard gate |
| stage-04 (agent-workflow integration) | document *when* in the agent loop to reach for the overlay; route agents to the query CLI by reflex | ✅ doc + light wiring: NEW `.claude/skills/overlay-query/SKILL.md` (query-mode → workflow-moment map; query CLI focus) + CLAUDE.md §13.1 (named instrument for empirical cite-grounding + cross-spec drift grep) + §13.5 cross-ref + `roadmap-continue` step-3 grounding clause + memory `[[overlay-query-agent-workflow]]`. No new R-IF arc (doc+wiring scope per operator). |

## Outputs (arc-level deliverables)

- A deterministic **spec↔code/CXA/substitution cross-reference linter** in `tools/` (orphan detection: code w/o cite · contract w/o code · seam w/o producer · substitution w/o carrier).
- Optionally, a graph overlay (only if the linter earns it).
- A freshness model (deterministic tier = git-hook/CI; LLM-summary tier = incremental).
- This folder is the **design-development ledger**; the shipped code lives in `tools/`.

## Conventions + boundaries

- **Docs-over-outputs:** later stages read `references/` + stage `CONTEXT.md`, not prior `output/`. Promote durable findings to a `references/` doc when stage 02 opens.
- **Code → `tools/`; ledger → here.** Mirrors the `substitution_ledger.py` separation.
- **X-AL-3:** this arc does **not** edit `design-substrate/**`. It *reads* specs to build an overlay; it does not amend them.
- **Proportionality:** the overlay's value is drift-detection, not scaffolding. Build the cheap deterministic core first; add weight only when it earns its place.

## Routing index

- `stages/01-exploration/CONTEXT.md` → stage contract; findings at `stages/01-exploration/output/understand-anything-and-spec-cite-traceability.md`.
