# Overlay Advisory Traceability Audit — 2026-07-27

> Phase D **re-audit** of the release-candidate deployment-readiness arc (runbook §6).
> Supersedes `.harness/overlay-advisory-traceability-audit-2026-06-10.md` as the current
> advisory-bucket baseline; the 2026-06-10 file is retained as the historical snapshot at
> the arc's GO close (`.harness/release-candidate-deployment-readiness-report-2026-06-10.md`).
> Process-substrate. Classifies each advisory overlay orphan bucket as **fixed / accepted / escalated**.

## Source

- `just overlay-check` + `just overlay` + `just overlay-query --orphans` (semantic overlay
  R-IF-112), re-run at branch `rc-rebaseline-phase-d-reaudit`, merge-base `1abfaae3`
  (`ops: roadmap status refresh post-#1134`).
- Hard gate (`just overlay-check`): **clean — `semantic overlay OK — 389 nodes, 36/36 seams wired`.**
- Overlay summary at this run: 389 source files · 387 carrying a cite (99.5 %) · 147 distinct
  contracts cited of 155 scanned · 376 distinct units cited · 13 ADRs · 36/36 CXA seams wired
  · 15/55 substitutions with a direct `H_T-*` carrier file.

The 2026-06-10 audit was run at HEAD `788e69f4`. That commit is **not an ancestor of current
`main`** — repository history was re-created 2026-07-25 (`main`'s root commit is `ebab176d`,
2026-07-25), so the two runs are compared by content, not by git range.

## Bucket counts (this run vs 2026-06-10)

| Bucket | 2026-07-27 (pre-fix) | 2026-07-27 (post-fix) | 2026-06-10 | Drift |
|---|---|---|---|---|
| `code_without_cite` | 2 | **0** | 14 | −14 (12 by prior arcs; last 2 FIXED here) |
| `contract_without_code` | 0 | 0 | 8 | −8 — **bucket closed** |
| `unit_without_code` | 2 | 2 | *(not enumerated)* | new enumeration; bucket did not exist in the old audit's table |
| `substitution_without_carrier` | 40 | 40 | 47 | −7 (carriers grew 8 → 15 of 55) |
| `cxa_seam_missing_endpoint` | 0 | 0 | 0 | none (HARD gate clean) |

Graph size grew 304 → 389 nodes and CXA seams 31/31 → 36/36 wired over the same interval, so
the advisory surface shrank while the code and seam surfaces grew.

## Classification

### `cxa_seam_missing_endpoint`: 0 — **N/A (clean)**

The only HARD overlay class. Empty, as at 2026-06-10, now over 36 wired seams rather than 31.
Nothing to do.

### `contract_without_code`: 0 — **CLOSED (was 8; no action owed)**

The 2026-06-10 audit accepted 8 (`C-CP-30`, `C-CP-37`, `C-CP-43`, `C-CP-49`, `C-CP-50`,
`C-IS-11`, `C-OD-3`, `C-RT-28`) as declarative / deferred / failure-mode contracts. The bucket
now reports **0** — the intervening arcs either landed carriers or (per `B-35`, closed) moved
the phantom-contract exclusions into the shared
`tools/semantic_overlay/overlay.py::DOCUMENTED_NON_CONTRACTS` single source of truth, and the
orphan class was subsequently re-scoped to canonical spec heads only. **Nothing accepted,
nothing escalated — the bucket is empty.**

### `code_without_cite`: 2 → 0 — **FIXED-this-PR (comment-only)**

Both remaining files already carried direct spec evidence in prose; only the machine-readable
`C-*` / `U-*` token the scanner greps for was missing. This is cite-formalization, not
invention — no source behavior was touched, both edits are inside module docstrings.

| File | Cite added | Evidence |
|---|---|---|
| `harness-runtime/src/harness_runtime/bootstrap/factories/protected_result_store_factory.py` | `U-RT-145` | The file's own docstring already cited "`Spec_Harness_Runtime_v1.md` v1.103 §14.8.11". `Implementation_Plan_Harness_Runtime_v2_51.md` §3 maps `\| §14.8.11 protected post-effect result store (surface A) \| U-RT-145 \|`, and §1.1's files-affected list names "the composition-root factories that build those dispatchers (the store dependency + owning tenant scope are INJECTED there — a raise site the injection does not reach is an acceptance FAILURE)". This module IS that injection site. |
| `harness-runtime/src/harness_runtime/lifecycle/audit_offload.py` | `U-RT-145` + `U-RT-141` (cross-ref) | `Spec_Harness_Runtime_v1.md` v1.102 §14.8.10.1 names this pool verbatim — "the 4-worker audit-offload executor" — when ruling it INELIGIBLE for B-48's sub-agent offload (whose own executor, `lifecycle/sub_agent_dispatch_executor.py`, is U-RT-141). Independently, the module hosts `resolve_result_ref_off_loop`, the off-loop half of U-RT-145's §14.8.11 protected-result-store resolution (its function docstring already cited "B-65-A codex round-4 P1" and imports `ProtectedResultStore` / `resolve_result_ref`). |

The `audit_offload.py` cite is deliberately **scoped in prose** — it states which surfaces the
module carries (the §14.8.10.1-named executor venue; U-RT-145's off-loop resolution helper),
not that the module implements U-RT-145 wholesale. Per the overlay README, a cite is *presence*,
not an implementation-correctness assertion.

Post-fix verification: `just overlay-check` → `semantic overlay OK — 389 nodes, 36/36 seams
wired`; `just overlay-query --orphans` → `code_without_cite: []`.

### `unit_without_code`: 2 — **ACCEPTED (both non-gaps; bucket never enumerated at 2026-06-10)**

This advisory class is canonical-head-scoped and was not tabled by the 2026-06-10 audit. Both
rows are known non-gaps, not missing implementation:

| Unit | Spec home | Disposition |
|---|---|---|
| `U-MEM-17` — "Refactor Anthropic native memory adapter onto canonical store" | `design-substrate/Implementation_Plan_Memory_Substrate_v1.md` | **ACCEPTED — tests-only carrier.** The unit IS implemented: `harness-runtime/src/harness_runtime/lifecycle/native_memory_adapter.py` ("Anthropic native Memory tool adapter over the canonical memory store"). The `U-MEM-17` token appears only at `harness-runtime/tests/test_native_memory_adapter.py`, and the overlay scans `<pkg>/src/**` only (`_iter_source_files`), so a tests-only cite reads as an orphan. Traceability-join thinness, not an implementation gap. |
| `U-RT-00` | `design-substrate/Spec_Harness_Runtime_v1.md` (+ 9 superseded Runtime plan versions) | **ACCEPTED — authoring unit by construction.** The Runtime spec's own coverage row reads `\| U-RT-00 \| (this spec entirely — U-RT-00 IS the spec authoring unit) \| Hard gate \|`. There is no code carrier to expect. Its only non-`design-substrate` appearance is `tools/test_closure_gate.py`, where it is a **test fixture literal** (`"unit_without_code": [{"id": "U-RT-00"}]`) — a phantom token, not a carrier. |

Neither row is escalated. A cite-enrichment option exists for `U-MEM-17` (adding the token to
the adapter's `src` docstring) but was **not** taken here: the runbook's cleanup rule admits a
cite only on direct evidence, and the honest evidence is that the *tests* cite the unit while
the adapter module cites its contracts. Recorded as optional polish below.

### `substitution_without_carrier`: 40 — **ACCEPTED (expected thinness; improved −7)**

Disposition breakdown of the 40 rows (derived by joining the orphan list to
`.harness/substitutions.yaml`):

| Disposition | Count (2026-07-27) | Count (2026-06-10) | Why no code carrier is expected |
|---|---|---|---|
| `AUTHORING_ONLY` | 9 | 9 | The H_T contract *is* the typed declaration itself; no runtime behavior to carry. A code cite would be wrong. |
| `BOUNDED_RESIDUAL` | **0** | 1 | Both `BOUNDED_RESIDUAL` rows in the YAML (`H_T-CP-16`, `H_T-OD-6`) now have direct docstring carriers — an improvement, not a gap. |
| `SUBSTANTIVE_RETIRED` | 31 | 37 | Retirement is proven via the substitution ledger + batch records, not via the overlay's automated substitution→carrier join. Traceability-join thinness. |

By axis: IS 8 · AS 8 · CP 17 · OD 4 · CXA 3.

The substitution ledger gate remains authoritative and passes: `python3 tools/substitution_ledger.py
--check` → `ledger OK — 54/54 RETIRED, 54/54 pipeline-advanced`. The overlay carrier-join is a
*secondary* traceability lens whose thinness on retired rows is expected and does not contradict
the ledger. **Accepted; not escalated.**

## Disposition summary

| Bucket | Count | Disposition |
|---|---|---|
| `cxa_seam_missing_endpoint` | 0 | N/A — clean (HARD gate) |
| `contract_without_code` | 0 | Closed — bucket empty (was 8, all accepted at 2026-06-10) |
| `code_without_cite` | 0 | **FIXED-this-PR** — 2 comment-only cite formalizations, direct evidence in both files |
| `unit_without_code` | 2 | Accepted — tests-only carrier (`U-MEM-17`) + authoring-unit-by-construction (`U-RT-00`) |
| `substitution_without_carrier` | 40 | Accepted — expected thinness (9 authoring-only by design; 31 retired-via-ledger, not overlay-join) |

**Two fixes landed (docstring cites only, no behavior touched); nothing escalated (no real
implementation gap surfaced).** The advisory surface improved on every comparable bucket since
2026-06-10 while the graph grew 304 → 389 nodes.

## Optional-polish follow-ups (not RC-blocking)

1. `U-MEM-17` cite-enrichment: decide whether a tests-only unit cite should count for the
   overlay's `unit_without_code` class (tool-side change), or whether
   `lifecycle/native_memory_adapter.py` should carry the `U-MEM-17` token (source-side change).
   Tool-side is the more honest fix — the adapter genuinely implements the unit.
2. `U-RT-00` suppression: the Runtime spec declares it the spec-authoring unit, so it could join
   `DOCUMENTED_NON_CONTRACTS`' unit-side analogue rather than being re-classified every audit.

These are traceability-tidy work, not implementation gaps.
