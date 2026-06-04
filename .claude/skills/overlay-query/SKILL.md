---
name: overlay-query
description: Resolve a spec/CXA/substitution cite against the code with the deterministic semantic overlay (R-IF-112) instead of ad-hoc grep. Use when grounding a `C-*`/`U-*`/`ADR-*`/`H_T-*` or `§N.M` cite ("what code cites C-IS-08?", "which files realize U-RT-112?"), navigating or wiring a CXA seam ("resolve the U-CP-30→U-IS-12 seam to its producer/consumer"), checking cross-spec drift / orphans before merge, or about to claim "file X implements contract C" or "no drift". This is the concrete instrument for CLAUDE.md §13.1 empirical cite-grounding + cross-spec drift grep. Do NOT use for free-text / non-cite searches — raw grep stays the right tool there.
---

# overlay-query — ground a cite against the code (R-IF-112)

The agent-facing surface of the shipped `tools/semantic_overlay/` overlay: a deterministic,
no-LLM join of **spec cites · CXA seams · substitutions · code structure**, re-derived fresh
from HEAD on every call. This skill is the WHEN/WHICH-QUERY map; the canonical surface +
caveats live at `tools/semantic_overlay/README.md` and CLAUDE.md §13.1 — **they win on conflict.**

## 0. Posture

Posture-**neutral**. `query` / `summary` / `check` are read-only and re-derive from HEAD —
safe in design-phase, Phase 7, and mode-agnostic alike. No HALT gate (contrast the editing
phase-7-* skills). The overlay *reads* `design-substrate/**`; it never amends it (X-AL-3 clean).

## Which query, when

| Reach for it when… | Command |
|---|---|
| grounding "what code cites this contract?" before editing / claiming coverage | `just overlay-query --contract C-XX-NN` |
| which files realize an atomic unit + the seams it's an endpoint of (phase-7-implementation) | `just overlay-query --unit U-XX-NN` |
| resolve a CXA seam to consumer↔producer file/axis/symbol before wiring (phase-7-cross-axis-composition) | `just overlay-query --seam "U-A→U-B"` |
| "what spec/CXA/substitution context does this file carry?" before touching it | `just overlay-query --file PATH` |
| substitution metadata + carrier files (phase-7-substitution-retirement) | `just overlay-query --substitution H_T-XX-NN` |
| pre-merge / adversarial-review drift sweep: `code_without_cite` (soft) + `cxa_seam_missing_endpoint` (**HARD**) | `just overlay-query --orphans` |
| before claiming "no drift" / in CI; exit 1 on hard drift or a stale committed `overlay.json` | `just overlay-check` |

## Why this over grep

- **The §13.1 cite-grounding instrument.** Empirical cite-grounding = resolve a `C-*`/`U-*`/
  `ADR-*`/`H_T-*` cite or a seam to its *carrier files*, don't recall — `--contract`/`--unit`/
  `--seam`/`--file` do exactly that, deterministically and indexed.
- **A complementary code-side drift surface** (NOT a replacement for the §13.1 cross-spec `rg`):
  `--orphans`/`--seam` catch *code↔cite / cross-axis-seam* decay intra-file grep misses (a seam's
  two endpoints live in different packages). It does not scan sibling specs — see Scope below.
- **`--seam` is the layer code↔code graphs are blind to.** Understand-Anything builds
  *per-package* knowledge graphs, so a cross-package CXA seam's endpoints are never both in one
  KG; the cross-axis layer is delivered via the overlay query, not the UA dashboard.
- Deterministic, indexed, fresh-from-HEAD — no stale snapshot (`overlay.json` is gitignored;
  a committed one would manufacture the drift the gate detects).

## Scope — what it does NOT cover

The overlay derives from **source-file docstring cites + `.harness/substitutions.yaml` +
code-resident `PATTERN_P1_SEAMS`**. It does **not** scan `design-substrate/**` sibling specs/plans
for stale *prose* cite-shapes — that sibling-spec `rg` (CLAUDE.md §13.1 *cross-spec drift grep*) is
a separate step the overlay **complements, not replaces**. `overlay-check` passing means code-side
seams resolve; it makes **no** claim about spec-prose-vs-sibling-spec drift.

## Read the output honestly

- **Cites are *presence*, not implementation-correctness** — `--contract C` returns files that
  *cite* C (a "see also" or negation counts); it does not assert they implement C.
- Seams are read **code-resident** from `PATTERN_P1_SEAMS` (`harness-runtime/tests/integration/test_cxa_pattern_p1.py`), **not** the delta-only CXA markdown — reading a mid-chain delta as
  canonical is the `[[wrong-version-read-delta-only-baseline]]` hazard.
- The `substitution_without_carrier` orphan list is expected to be large (most carriers are named
  in the `.harness/substitutions.yaml` row `rationale`, not docstrings) — **advisory, not drift**.

## Secondary — enrich-ua (dashboard only)

`uv run python tools/semantic_overlay/overlay.py enrich-ua <pkg>/.understand-anything/knowledge-graph.json`
left-joins overlay node-attrs onto a per-package UA graph for the dashboard. Cross-axis seams are
**not** in its output (per-package KGs) — for the cross-axis layer use the query CLI above.
See `tools/semantic_overlay/README.md`.

## Pairs with

`phase-7-implementation` (`--unit`), `phase-7-cross-axis-composition` (`--seam`),
`phase-7-substitution-retirement` (`--substitution`), `phase-7-back-flow-routing` (drift → fork),
`harness-adversarial-reviewer` (cross-spec drift probes, §10.9), `roadmap-continue` (step-3 grounding).
