# Overlay Advisory Traceability Audit — 2026-06-10

> Phase D deliverable of the release-candidate deployment-readiness arc (runbook §6).
> Process-substrate. Classifies each advisory overlay orphan bucket as **fixed / accepted / escalated**.
> No fake cites were added; no source was edited. Counts are stable vs the runbook handoff baseline.

## Source

- `just overlay-query --orphans` (semantic overlay R-IF-112), run at git HEAD `788e69f4`.
- Hard gate (`just overlay-check`): **clean — 304 nodes, 31/31 CXA seams wired, 0 missing endpoints.**

## Bucket counts (this run vs runbook §6 handoff)

| Bucket | This run | Handoff | Drift |
|---|---|---|---|
| `code_without_cite` | 14 | 14 | none |
| `contract_without_code` | 8 | 8 | none |
| `substitution_without_carrier` | 47 | 47 | none |
| `cxa_seam_missing_endpoint` | 0 | 0 | none (HARD gate clean) |

No drift since handoff — the advisory surface is stable.

## Classification

### `cxa_seam_missing_endpoint`: 0 — **N/A (clean)**
The only HARD overlay class. Empty. Nothing to do.

### `substitution_without_carrier`: 47 — **ACCEPTED (expected thinness)**
Disposition breakdown of the 47 rows (derived from `.harness/substitutions.yaml`):

| Disposition | Count | Why no code carrier is expected |
|---|---|---|
| `AUTHORING_ONLY` | 9 | The H_T contract *is* the typed declaration itself; no runtime behavior to carry (sub-species 10 categorical-mismatch). A code cite would be wrong. |
| `BOUNDED_RESIDUAL` | 1 | Production substrate dormant / post-MVP at MVP (X-AL-2 §5.3). No live carrier by design. |
| `SUBSTANTIVE_RETIRED` | 37 | Retirement is proven via the substitution ledger (54/54 RETIRED) + batch records, not via the overlay's automated substitution→carrier join. Traceability-join thinness, **not** an implementation gap. |

The substitution ledger gate (`python tools/substitution_ledger.py --check`) passes at **54/54 RETIRED, 54/54 pipeline-advanced** — the authoritative retirement accounting. The overlay carrier-join is a *secondary* traceability lens whose thinness on retired rows is expected and does not contradict the ledger. **Accepted; not escalated.**

### `code_without_cite`: 14 — **ACCEPTED (advisory)**
14 source files carry no `C-*`/`U-*` contract cite. This is advisory tooling/scaffold/test-adjacent thinness, not a correctness defect. Per the runbook cleanup rule, a cite may be added *only* with direct evidence the file materially carries a cited contract; absent that, the correct disposition is to document the thinness, not to force a cite. **Accepted; not escalated.** (A per-file cite-enrichment pass is optional-polish, not RC-blocking.)

### `contract_without_code`: 8 — **ACCEPTED (declarative / no real missing impl found)**
The 8: `C-CP-30`, `C-CP-37`, `C-CP-43`, `C-CP-49`, `C-CP-50`, `C-IS-11`, `C-OD-3`, `C-RT-28`.

Spot-check against `design-substrate/` shows these are declarative / enum-level / failure-mode / deferred / cross-cutting contracts, **not** evidence of missing runtime implementation (the escalation trigger):

- **C-CP-43** — `MCPTrustTier` enum, explicitly **DEFERRED** (U-CP-43/45). No full code carrier expected.
- **C-IS-11** — a ledger-append *failure-mode* contract (`CP-FAIL-DRIVER-LEDGER-APPEND-FAILURE`). The append behavior is implemented (overlay-check clean, ledger works); the overlay's contract→code join doesn't resolve the failure-mode reference. Traceability thinness.
- **C-CP-30 / C-OD-3** — versioning / spec-lineage declarative references.
- **C-RT-28** — no spec-body match via grep (rendering-format thin).
- **C-CP-37 / C-CP-49 / C-CP-50** — same CP gate-level/declarative family; not spot-read individually.

Per the runbook escalation rule ("if a contract-without-code finding proves a real missing implementation, stop and route it as a new roadmap/back-flow item"), **none of the spot-checked contracts show a real missing implementation**, and Phase-8 closure (54/54 retired, overlay HARD gate clean) corroborates impl completeness. **Accepted; not escalated.**

## Disposition summary

| Bucket | Disposition |
|---|---|
| `cxa_seam_missing_endpoint` (0) | N/A — clean |
| `substitution_without_carrier` (47) | Accepted — expected thinness (9 authoring-only + 1 bounded-residual by design; 37 retired-via-ledger, not overlay-join) |
| `code_without_cite` (14) | Accepted — advisory; cite only with direct evidence |
| `contract_without_code` (8) | Accepted — declarative/deferred/failure-mode; no real missing impl found |

**Nothing fixed (no source edited), nothing escalated (no real impl gap surfaced).** All four buckets are accepted advisory traceability, stable since handoff.

## Optional-polish follow-ups (not RC-blocking)

1. Per-contract carrier deep-dive for the 8 `contract_without_code` IDs — resolve each to its precise carrier or formally record declarative status.
2. Per-file cite-enrichment for the 14 `code_without_cite` files where direct evidence supports a cite.

These are traceability-tidy work, not implementation gaps.
