# Phase 7d Retirement Events — Batch 52

| Field | Value |
|---|---|
| Batch number | 52 |
| Filed at | 2026-06-08 (post-Phase-8 accounting/back-flow after R-810 + R-820 live closures) |
| Filed by | Codex accounting/back-flow arc; substitution-ledger forward-only transit discipline |
| Predecessor batch | `.harness/phase-7d-retirement-events-batch-51.md` |

---

## §0 Batch context

**Status type: 3 accepted-indefinite-defer → RETIRED transits.** This batch updates the live substitution ledger after the deferred external-integration arcs became real runtime evidence:

- **H_T-AS-8e** (`files.*` namespace) — closed by R-810.
- **H_T-CP-17** (Files primitives + `files.*` consumption) — closed by R-810.
- **H_T-AS-8f** (`managed_agents.*` namespace) — closed by R-820.

R-700 remains the historical Phase-8 declaration at **46/54 RETIRED + 49/54 pipeline-advanced**. This batch is a forward-only post-Phase-8 back-flow: the three rows that R-700 ratified as accepted-indefinite-defer now have live implementation evidence, so the live ledger advances to **49/54 RETIRED + 52/54 pipeline-advanced**.

**Cardinality delta.** Workspace RETIRED **46/54 → 49/54** (+3); pipeline-advanced **49/54 → 52/54** (+3); SB-INDEFINITE **3/54 → 0/54**. Axis deltas: AS RETIRED **9/11 → 11/11**; CP RETIRED **20/21 → 21/21**. Remaining non-RETIRED rows are OD-4, CXA-1, CXA-2, CXA-3, and CXA-4.

---

## §1 H_T-AS-8e + H_T-CP-17 — Files API / files.* retirement

### §1.1 Evidence

R-810 opened the previously deferred Files arc and closed it with a live managed-cloud proof:

- Runtime port + real Anthropic Files adapter landed.
- Plaintext file upload produced live file `file_011CbqJqTs21yENfK4xfEpqp`.
- The file was referenced by `file_id` and composed into the Batch API request shape.
- `files.operation` exported through the authenticated managed collector.
- Cloud Trace `bfd28fa8fc8ecc3ba973d1e405cdb865` carried the expected `files.*` attributes.
- Cleanup completed; the uploaded file is gone, and temporary GCP TokenCreator IAM was removed.

### §1.2 Disposition

The former accepted-indefinite-defer rationale was "Files arc not opened / Memory-only MVP scope." That condition is no longer true after R-810. The live path exercises both the `files.*` telemetry namespace (`H_T-AS-8e`) and the Files primitive consumption path (`H_T-CP-17`).

**Transit:** `H_T-AS-8e` and `H_T-CP-17` move from `SB_INDEFINITE` to `SUBSTANTIVE_RETIRED`.

---

## §2 H_T-AS-8f — managed_agents.* retirement

### §2.1 Evidence

R-820 closed the managed_agents runtime/integration gate with a real Anthropic Managed Agents SDK/session integration and managed-cloud telemetry proof:

- Session `sesn_019aMgaF8sAW2cXhhpMTYij4` reached `session.status_idle`.
- `managed_agents.runtime` exported through the managed collector.
- Cloud Trace `009d7716b19c75e4ad7edb93e78f8d2b` carried `managed_agents.*` attributes.
- Temporary Cloud Run Token Creator IAM used for the proof was removed and verified absent.

### §2.2 Disposition

The former accepted-indefinite-defer rationale was "managed_agents production-only exclusion / managed-cloud gate." That condition is no longer true after R-820. The live path exercises the `managed_agents.*` namespace at the managed-cloud surface.

**Transit:** `H_T-AS-8f` moves from `SB_INDEFINITE` to `SUBSTANTIVE_RETIRED`.

---

## §3 Post-batch-52 table

| Substitution | Prior disposition | New disposition | Evidence |
|---|---|---|---|
| H_T-AS-8e | SB_INDEFINITE | SUBSTANTIVE_RETIRED | R-810 Files API upload/reference/delete + managed-cloud `files.operation` trace |
| H_T-CP-17 | SB_INDEFINITE | SUBSTANTIVE_RETIRED | R-810 Files primitive consumption + `files.*` trace |
| H_T-AS-8f | SB_INDEFINITE | SUBSTANTIVE_RETIRED | R-820 Managed Agents SDK/session + managed-cloud `managed_agents.*` trace |

Live ledger after batch-52:

- RETIRED: **49/54 (90.7%)**
- Pipeline-advanced: **52/54 (96.3%)**
- PARTIAL: **3/54** (`H_T-OD-4`, `H_T-CXA-1`, `H_T-CXA-4`)
- STILL-BOUNDED: **2/54** (`H_T-CXA-2`, `H_T-CXA-3`)
- SB-INDEFINITE: **0/54**

---

## §4 Non-transits

This batch intentionally does **not** move:

- **H_T-OD-4** — runtime code residual is closed, but its `RETIRED-AS-CROSS-AXIS-DEFERRED` label/count treatment was explicitly ratified by R-700. Any reclassification needs a separate OD-4 accounting decision.
- **H_T-CXA-4** — current grounding says 0 wireable edges, but folding the CXA row into RETIRED is bookkeeping/accounting distinct from the Files/Managed Agents live-integration proof.
- **H_T-CXA-1/2/3** — still have real producer/composer/engine-loop gaps or scope decisions.

---

## §5 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/phase-7d-retirement-events-batch-52.md` |
| Filed at | 2026-06-08 |
| Phase | Phase 7 sub-phase 7d — post-Phase-8 accounting/back-flow |
| Predecessor batch | batch-51 |
| Transits | H_T-AS-8e, H_T-AS-8f, H_T-CP-17 accepted-indefinite-defer → SUBSTANTIVE_RETIRED |
| Roadmap closures | R-005, R-006, R-010 RESOLVED |
| Co-published artifacts | `.harness/substitutions.yaml`; `tools/test_substitution_ledger.py`; `tools/dashboard/generate.py`; `Project_Roadmap_v1.md`; `.harness/roadmap_status.md`; `.harness/post-phase-8-forward-register.md`; `tools/dashboard/roadmap.html` |
| Cross-axis cascade | Accounting-only; no production code change |
| Production code change | ZERO |
| Test change | Substitution-ledger expected counts updated to 49/52/54 |
| Spec / plan amendment | ZERO |
