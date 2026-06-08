# Phase 7d Retirement Events — Batch 54

| Field | Value |
|---|---|
| Batch number | 54 |
| Filed at | 2026-06-08 (R-CXA-3 CP->AS runtime composer closure) |
| Filed by | Codex implementation arc; substitution-ledger forward-only transit discipline |
| Predecessor batch | `.harness/phase-7d-retirement-events-batch-53.md` |

---

## §0 Batch context

**Status type: 1 STILL-BOUNDED -> RETIRED transit.** This batch updates the live substitution ledger after the operator rejected MVP scope narrowing and explicitly directed the runtime-composer path for R-CXA-3.

R-700 remains the historical Phase-8 declaration at **46/54 RETIRED + 49/54 pipeline-advanced**. Batch-52 remains the Files/Managed Agents back-flow to **49/54 RETIRED + 52/54 pipeline-advanced**. Batch-53 remains the OD-4/CXA-4 back-flow to **51/54 RETIRED + 52/54 pipeline-advanced**. This batch is the next forward-only runtime-composer closure: CXA-3 moves from STILL-BOUNDED to counted retirement, so the live ledger advances to **52/54 RETIRED + 53/54 pipeline-advanced**.

**Cardinality delta.** Workspace RETIRED **51/54 -> 52/54** (+1); pipeline-advanced **52/54 -> 53/54** (+1) because CXA-3 was previously STILL-BOUNDED. Axis delta: CXA RETIRED **2/5 -> 3/5**. Remaining non-RETIRED rows are CXA-1 and CXA-2.

---

## §1 H_T-CXA-3 — CP->AS runtime composer retirement

### §1.1 Evidence

R-CXA-3 previously remained STILL-BOUNDED because no `harness_runtime.lifecycle.cp_as_wiring` runtime composer existed. The typed CP->AS Pattern-P1 import seams were present, but the runtime invocation/composition layer was absent.

This arc closes the runtime-composer path:

- `RuntimeCpAsWiring` now materializes the CP-consumed AS terminal seam export registry at bootstrap stage 6.
- The composer resolves the AS substrate seam exports that declare `ASConsumingAxis.CONTROL_PLANE`.
- The composer fail-closes on AS manifest coverage drift or unresolved CP-consumed AS seam exports.
- Stage 6 binds `cp_as_wiring` alongside the other CXA wiring stages.
- `_MutableHarnessContext.freeze()` exposes the runtime registry as `HarnessContext.cp_as_wiring`.
- Focused lifecycle and bootstrap tests prove the stage shape, identity binding, coverage check, and frozen-context exposure.

### §1.2 Disposition

The operator explicitly rejected MVP scope narrowing and directed the runtime-composer path. With the runtime composer landed and exposed at bootstrap, the R-CXA-3 composer gate is closed.

**Transit:** `H_T-CXA-3` moves from `STILL_BOUNDED` to `SUBSTANTIVE_RETIRED`.

---

## §2 Post-batch-54 table

| Substitution | Prior disposition | New disposition | Evidence |
|---|---|---|---|
| H_T-CXA-3 | STILL_BOUNDED | SUBSTANTIVE_RETIRED | `RuntimeCpAsWiring` stage-6 composer + `HarnessContext.cp_as_wiring` exposure + focused lifecycle/bootstrap tests |

Live ledger after batch-54:

- RETIRED: **52/54 (96.3%)**
- Pipeline-advanced: **53/54 (98.1%)**
- PARTIAL: **1/54** (`H_T-CXA-1`)
- STILL-BOUNDED: **1/54** (`H_T-CXA-2`)
- SB-INDEFINITE: **0/54**

---

## §3 Non-transits

This batch intentionally does **not** move:

- **H_T-CXA-1** — still PARTIAL because the AS->IS secret-fetch audit edge has no production caller; moving it would be a hollow seam until a real AS secret-fetch producer exists.
- **H_T-CXA-2** — still STILL-BOUNDED; the materialized pause/resume, override, and workload-selection methods are covered, but HITL rewriting and engine free-function production firing sites remain bounded-defer until the upstream loops exist.

---

## §4 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/phase-7d-retirement-events-batch-54.md` |
| Filed at | 2026-06-08 |
| Phase | Phase 7 sub-phase 7d — post-Phase-8 runtime-composer back-flow |
| Predecessor batch | batch-53 |
| Transits | H_T-CXA-3 STILL_BOUNDED -> SUBSTANTIVE_RETIRED |
| Roadmap closures | R-CXA-3 RESOLVED |
| Co-published artifacts | `.harness/substitutions.yaml`; `tools/test_substitution_ledger.py`; `tools/dashboard/generate.py`; `Project_Roadmap_v1.md`; `.harness/roadmap_status.md`; `.harness/post-phase-8-forward-register.md`; `tools/dashboard/roadmap.html` |
| Cross-axis cascade | CP->AS runtime composer materialized |
| Production code change | `harness_runtime.lifecycle.cp_as_wiring`; stage-6 bootstrap binding; frozen context exposure |
| Test change | Lifecycle/bootstrap coverage plus substitution-ledger expected counts updated to 52/53/54 |
| Spec / plan amendment | ZERO |
