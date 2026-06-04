# `semantic_overlay` — spec ↔ code ↔ CXA-seam ↔ substitution overlay (R-IF-112)

A **deterministic, no-LLM** semantic layer over the code graph. It joins the four
load-bearing relationships of this repo into **one Understand-Anything-format graph
artifact**, so a single `overlay.json` serves three consumers:

| Consumer | How |
|---|---|
| **Agent reference tool** | `overlay.py query` — "what code implements `C-IS-08`?", "who cites `U-RT-112`?", "what's this file's substitution?", "show orphans". Always re-derived fresh from HEAD. |
| **Dashboard / Understand-Anything** | UA-format nodes (`file:src/<pkg>/...` ids) carry the overlay attrs + `cxa_seam` edges, so `enrich-ua` left-joins onto a generated `knowledge-graph.json`. Run `overlay-build` on demand — `overlay.json` is a **gitignored build artifact**, not committed (a committed derived snapshot would go stale node-by-node while a stats-only gate passed — the exact "stale snapshot misleads" failure this arc fights). |
| **CI drift gate** | `overlay.py check` — sibling to `tools/substitution_ledger.py`; exit 1 on hard drift. |

## The four joined layers

1. **spec cites** — `C-{IS,AS,CP,OD,RT}-NN` contracts, `U-{…}-NN` units, `ADR-{F,D}N`,
   `§N.M` sections, parsed from docstrings/comments. ~99 % of source files carry one.
2. **CXA seams** — the 31 genuine typed cross-axis seams, read **code-resident** from
   `harness-runtime/tests/integration/test_cxa_pattern_p1.py` (`PATTERN_P1_SEAMS`), **not**
   the delta-only CXA markdown (`Cross_Axis_Composition_Document_v2_19.md` holds **0**
   physical edge rows — the canonical tables live at v2.3 + additive deltas; reading a
   mid-chain delta as canonical is the `[[wrong-version-read-delta-only-baseline]]` hazard).
3. **substitutions** — `.harness/substitutions.yaml` (55 H_T-* rows), back-linked to the
   source files that cite an `H_T-*` id directly. **This join is honestly thin** (≈9 of 55
   ids are cited in a docstring; most carriers are named in the row `rationale`, not code).
4. **code structure** — the file is the node. Import / contains edges are left to UA itself;
   the overlay adds only the *semantic* edge types (`cxa_seam`, `substitution_carrier`).

The **CXA seams are the navigable layer code↔code graphs are blind to** (stage-01 finding #3):
`--seam` resolves an edge to consumer-file/axis ↔ producer-file/axis + symbol; `--file`
emits a node's resolved inbound/outbound seam endpoints; `--unit` surfaces seams where the
unit is an endpoint. These cross-package seams do **not** appear in `enrich-ua` output — UA
builds per-package graphs, so both endpoints are never in one KG; the cross-axis layer is
delivered via `overlay.json` + the query CLI, not the UA dashboard.

> Cites are *presence*, not implementation-correctness — `query --contract C` returns files
> that **cite** `C` (a "see also" or negation counts); it does not assert they implement it.

## Usage

```bash
just overlay                       # human counts + orphan report (fresh)
just overlay-build                 # write overlay.json (dashboard/enrich artifact)
just overlay-check                 # CI gate: exit 1 on hard drift
just overlay-query --contract C-IS-08          # files citing a contract
just overlay-query --unit U-RT-112             # files citing a unit + seams it's an endpoint of
just overlay-query --file harness-is/src/harness_is/entry_hash.py   # full node + resolved seams
just overlay-query --substitution H_T-CP-19    # substitution metadata + carrier files
just overlay-query --seam "U-CP-30→U-IS-12"    # resolve a CXA seam: consumer ↔ producer + symbol
just overlay-query --orphans

# enrich an Understand-Anything KG (writes <name>.overlay.json beside it; never in place):
uv run python tools/semantic_overlay/overlay.py enrich-ua harness-is/.understand-anything/knowledge-graph.json
```

## Orphan classes (the linter)

| Class | Reliability | Meaning |
|---|---|---|
| `code_without_cite` | **reliable** | a source file with no `C-*`/`U-*`/`ADR-*`/`H_T-*` cite (excludes `__init__.py` aggregators). |
| `cxa_seam_missing_endpoint` | **reliable — HARD gate** | a `PATTERN_P1_SEAMS` producer/consumer module that no longer resolves to a file (cross-axis drift). |
| `substitution_without_carrier` | **advisory** | an `H_T-*` id with no docstring-citing file (expected to be large — most carriers are in `rationale`). |

Only `cxa_seam_missing_endpoint` and a stale committed `overlay.json` are **HARD** (`check`
exits 1). The code-without-cite count and substitution thinness reflect genuine repo state,
not a regression — they are reported, not failed.

## Freshness

**Every** path (`query` / `summary` / `check`) re-derives from HEAD — nothing reads a stale
committed json, because `overlay.json` is gitignored (a committed derived overlay would
*manufacture* the drift it exists to detect — stage-01 finding #2). `build` writes the
artifact for the dashboard/enrich consumer on demand. If a developer does commit it locally,
`check` additionally compares `stats` and fails on a stale snapshot (the
`substitution_ledger.py` snapshot-pin discipline, retained for that case).

## Design boundary (X-AL-3)

This tool **reads** `design-substrate/**` to build the overlay; it never amends it. It is
process-substrate (like the substitution ledger), not design-substrate — no X-AL-3 guard,
no clearance marker. The development ledger for this arc lives at
`.harness/spec-code-overlay/`; the shipped code lives here in `tools/`.
