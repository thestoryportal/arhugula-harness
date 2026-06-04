# CONTEXT — stage 01: exploration  *(Layer 2: stage contract)*

**Goal:** ground the arc's premise before any design — is the spec↔code traceability layer (a) real, (b) machine-extractable, (c) worth overlaying — and assess understand-anything as a candidate substrate.

**Status:** ✅ complete (seed). Output below is the input to stage 02 (design).

## Inputs

| Load | Sections |
|---|---|
| `harness-*/src/**/*.py` | docstring authority cites (`C-*-NN` / `U-*` / `ADR-*` / `§N` / `H_T-*`) — presence only |
| understand-anything v2.7.6 graph of `harness-is/` | `.understand-anything/knowledge-graph.json` (nodes/edges/hubs) |
| `tools/substitution_ledger.py` | the deterministic-derivation + CI-gate shape |

## Process

1. Drive the understand-anything dashboard live; assess GUI-vs-data fit for agents, staleness behaviour, and what relationship it models.
2. Probe spec/authority-cite coverage across all 7 packages by grep (presence of a parseable cite per source file).
3. Synthesize: tool-fit, traceability-layer extractability, and a cheapest-core (deterministic linter) candidate — under the solo-dev proportionality filter.

## Outputs

| Artifact | Location |
|---|---|
| Exploration findings (tool assessment + cross-axis cite-coverage probe + linter-MVP shape + open questions) | `output/understand-anything-and-spec-cite-traceability.md` |

## Hand-off to stage 02

Open questions to carry forward (from the findings doc): overlay JSON schema · linter-only vs +visualization · fork-vs-sidecar · freshness home (hook/CI) · gate-vs-advisory · composition with the council context-memory arc. When stage 02 opens, promote the durable findings to a `references/` doc per docs-over-outputs.
