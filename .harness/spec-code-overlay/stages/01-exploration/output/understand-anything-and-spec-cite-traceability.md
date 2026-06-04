# Overlay Arc — Starter Exploration: understand-anything tooling + the spec-cite traceability layer

*Seed exploration for the **spec / CXA / substitution semantic-overlay-over-code-graph** arc. Captured from a hands-on 2026-06-04 session (driving the understand-anything dashboard live + a repo grep), at commit `7c0ead2`. This is a starting point for agent exploration + design development — not a decision, not a plan. The arc's CONTEXT/charter + plan come next.*

---

## Premise of the arc (one paragraph)

The understand-anything plugin builds a **code↔code** knowledge graph (imports, tested-by, hubs) and serves it as a dashboard. Useful, but blind to *this* repo's load-bearing relationship: **spec-contract ↔ code ↔ CXA-edge ↔ substitution** (e.g. `C-IS-01 §1` ↔ `path_class_registry.py` ↔ a CXA seam ↔ `H_T-IS-1`). The arc's question: **can we overlay that semantic layer onto the code graph, keep it fresh cheaply, and is it worth it?** This doc captures two empirical inputs to that question.

## A. The understand-anything tool, as-built (driven live this session)

A plugin (`understand-anything` v2.7.6) that runs an LLM extraction pass over a codebase → interactive knowledge-graph dashboard (nodes = files/classes/functions; edges = imports/tested-by; plus a curated tour, node inspector, fuzzy/semantic search, diff mode, `OPEN CODE`).

Three observations:

1. **GUI vs data — wrong interface for *agents*, right for *humans*.** `[HIGH]` Everything the dashboard surfaced was obtainable faster + cheaper by reading the underlying `.understand-anything/knowledge-graph.json` + `Read`/`grep` directly (verified: two cheap tool calls beat a browser-driving screenshot sequence). The *artifact* it emits (per-node summaries, fan-in/out hub ranks, tested-by edges, clustering) is useful as **data**; the browser cockpit is useful for a **human** auditing agent work or onboarding to an axis — not for an agent in-loop.

2. **Staleness risk = the drift we fight.** `[HIGH]` The graph is a **static LLM-pass snapshot**; it goes stale on every PR unless regenerated. A stale graph silently misleads — same failure-mode class as stale-carry-text (CLAUDE.md §10.5) + the dashboard fixed-point protocol (§12). Any adoption without regeneration-on-merge would *manufacture* drift, not detect it.

3. **It models the wrong relationship for this repo.** `[HIGH]` Code↔code only. The spec↔code↔CXA↔substitution traceability layer — where the interpretable-context methodology and most real drift live — is invisible to it. That gap is the overlay's reason to exist.

## B. Fresh cross-axis probe — the spec-cite traceability layer is near-universal + machine-extractable

How many source files carry a *parseable* design-substrate/authority cite in their docstrings? Grep across all 7 packages at `7c0ead2` for `C-{IS,AS,CP,OD,RT}-N` / `U-{…}-N` / `ADR-{F,D}N` / `§N` / `H_T-X`:

| package | source files carrying a spec/authority cite |
|---|---|
| harness-core | 7 / 7 |
| harness-is | 18 / 18 |
| harness-as | 33 / 33 |
| harness-cp | 68 / 68 |
| harness-od | 53 / 53 |
| harness-runtime | 97 / 98 |
| harness-cxa | 1 / 1 |
| **total** | **277 / 278 ≈ 99.6 %** |

Plus: **286 distinct `U-*` unit IDs** referenced in source; the full `C-*-NN` contract keyspace (IS/AS/CP/OD/RT) appears in docstrings. The cite layer is **present in essentially every file** and parseable deterministically — **no LLM pass needed.** `[HIGH]`

Corroborating: `path_class_registry.py:3-9` cites its authority chain inline (`C-IS-01 §1`, `U-IS-01`, `ADR-F2 v1.2`); and `tools/substitution_ledger.py` + `.harness/substitutions.yaml` are an existing, CI-gated **deterministic derivation** precedent (CLAUDE.md §4.2 R-600) — the repo has already built this *shape* of tool for the substitution sub-layer.

## Implications for the overlay design (inputs, not decisions)

- **The overlay's cheapest, highest-leverage core is a deterministic *cross-reference linter*, not a visualization.** `[MODERATE]` Section B shows the join keys (`C-*-NN`, `U-*`, `ADR-*`, `H_T-*`) are ~universal + parse-only. A `tools/` linter (sibling to `substitution_ledger.py`) could flag **orphans**: code with no spec cite · a `C-*-NN` contract with no landed code · a CXA seam with no wired producer · a substitution with no carrier. Seconds to run, per-merge/per-save → a real drift-detector.
- **Freshness is a two-tier problem.** `[HIGH]` The deterministic overlay (cites + CXA tables + `substitutions.yaml`) re-derives in seconds (git-hook/CI tier). The *LLM summaries* (the expensive tier) only need incremental regen on touched files — not a full re-run per edit. Keep them separate.
- **Build-vs-adopt.** `[MODERATE]` understand-anything is a third-party plugin; an overlay means forking it (maintenance + upstream drift) or a sidecar emitting its JSON format. The MVP-first read: **build the deterministic linter first (text-native, no fork); add a graph visualization only if the linter proves its worth.**
- **Proportionality (solo-dev filter).** `[MODERATE]` understand-anything GUI for in-loop agents → likely doesn't earn its place (friction + staleness). As an occasional human cockpit → low-cost, earns its own narrow merit. The deterministic orphan-linter → the candidate that most plausibly earns a standing slot.

## Open questions for the arc to take up

- What exactly does the overlay JSON schema look like (node attrs: `spec_contracts[]`, `cxa_edges[]`, `substitution`, `coverage`; new edge type for cross-axis seams)?
- Linter-only, or linter + visualization? If visualization: fork vs sidecar?
- Where does freshness live (pre-commit hook? CI gate? both)? What's the incremental-regen trigger for the LLM tier?
- Does the linter become a CI gate (like the substitution tally gate) or stay advisory?
- How does this compose with the council's context/memory arc (interpretable-context methodology) without duplicating it?

---

*Provenance: hands-on understand-anything v2.7.6 session (dashboard at `127.0.0.1:5173`) + repo grep, both at commit `7c0ead2`, 2026-06-04. Cite-coverage counts are a single grep snapshot (parseable-cite **presence**, not cite-correctness — a cite's existence is counted, its byte-exact resolution is not). No code / design-substrate touched.*
