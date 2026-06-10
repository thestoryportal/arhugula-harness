# Phase 7d Retirement Events — Batch 56

| Field | Value |
|---|---|
| Batch number | 56 |
| Filed at | 2026-06-09 (R-CXA-1 AS->IS seam closeout) |
| Filed by | Codex accounting/back-flow arc; substitution-ledger forward-only transit discipline |
| Predecessor batch | `.harness/phase-7d-retirement-events-batch-55.md` |

---

## §0 Batch Context

**Status type: 1 PARTIAL -> SUBSTANTIVE_RETIRED transit.** This batch updates the live substitution ledger after R-CXA-1's AS->IS producer-gated seam finished both closeout gates:

- must_pass #1: PR #458 moved scoped secret-fetch audit production to the active workflow `TOOL_STEP` dispatch site with non-hollow scope and rotation metadata.
- must_pass #2: `.harness/r-cxa-1-as-is-edge-audit-2026-06-09.md` narrows the stale "remaining ~12 callbacks" wording against the current overlay inventory and this arc threads the R-003 procedural-tier sidecar through the production `RuntimeAsIsWiring` callback.

R-700 remains the historical Phase-8 declaration at **46/54 RETIRED + 49/54 pipeline-advanced**. Batch-52 remains the Files/Managed Agents back-flow to **49/54 RETIRED + 52/54 pipeline-advanced**. Batch-53 remains the OD-4/CXA-4 back-flow to **51/54 RETIRED + 52/54 pipeline-advanced**. Batch-54 remains the CP->AS runtime-composer back-flow to **52/54 RETIRED + 53/54 pipeline-advanced**. Batch-55 remains the CP->IS bounded-residual close to **53/54 RETIRED + 54/54 pipeline-advanced**. This batch records the final live-ledger disposition: CXA-1 moves from PARTIAL to SUBSTANTIVE_RETIRED, so the live ledger advances to **54/54 RETIRED + 54/54 pipeline-advanced**.

**Cardinality delta.** Workspace RETIRED **53/54 -> 54/54** (+1); pipeline-advanced remains **54/54** because CXA-1 was already PARTIAL. Axis delta: CXA RETIRED **4/5 -> 5/5**. No non-RETIRED substitution row remains.

---

## §1 H_T-CXA-1 — AS->IS Substantive Retirement

### §1.1 Evidence

R-CXA-1 previously remained PARTIAL because the AS->IS runtime composer existed but the production secret-fetch audit caller was hollow or absent, and the roadmap carried legacy prose about "remaining ~12 AS source-unit audit-emission callbacks."

The current evidence closes both gaps:

- PR #458 made the scoped secret-fetch producer real at `RuntimeToolDispatcher`'s active `TOOL_STEP` dispatch path.
- `SecretFetchEvent` now carries the workflow identity, step identity, scoped secret name/scope, actor, timestamp, and backend-sourced rotation metadata.
- `RuntimeAsIsWiring.emit_secret_fetch_audit_entry(...)` now writes the R-003 `procedural_tier_snapshot_ref` when the stage-5 resolver is bound.
- Stage 5 binds `ctx.procedural_tier_snapshot_resolver` before constructing the TOOL_STEP dispatcher and passes it through the `RuntimeAsIsWiring` emitter used by `RuntimeToolDispatcher`.
- Stage 6 passes the same resolver to `materialize_as_is_wiring_stage(...)` for direct CXA_WIRING invocation compatibility.
- The edge-scope audit grounds current AS->IS direct edges as two read-only carrier-consumption families (`U-AS-19`, `U-AS-28`) plus the secret-fetch audit emission family (`U-AS-26`/`U-AS-27`), not twelve missing callback sites.

Focused verification:

```text
uv run pytest harness-runtime/tests/test_lifecycle_as_is_wiring.py harness-runtime/tests/test_u_rt_75_runtime_tool_dispatcher_factory.py harness-runtime/tests/test_lifecycle_runtime_tool_dispatcher.py -q
```

Result: `47 passed`.

### §1.2 Disposition

R-CXA-1's MVP-closeable AS->IS producer surface is now accounted for:

- The bootstrap-value secret path remains excluded under the prior Reading-D decision.
- The scoped workflow-time producer is real and emits through the runtime AS->IS callback.
- The remaining edge-scope prose has been narrowed against the overlay inventory; read-only AS consumers of IS carriers do not require callback wiring.
- The AS->IS ledger write now satisfies workflow-context sidecar discipline by carrying `procedural_tier_snapshot_ref` when bound by bootstrap.

**Transit:** `H_T-CXA-1` moves from `PARTIAL` to `SUBSTANTIVE_RETIRED`.

---

## §2 Post-Batch-56 Table

| Substitution | Prior disposition | New disposition | Evidence |
|---|---|---|---|
| H_T-CXA-1 | PARTIAL | SUBSTANTIVE_RETIRED | active TOOL_STEP scoped secret-fetch producer + resolver-bound RuntimeAsIsWiring write + edge-scope audit narrowing stale callback wording |

Live ledger after batch-56:

- RETIRED: **54/54 (100.0%)**
- Pipeline-advanced: **54/54 (100.0%)**
- PARTIAL: **0/54**
- STILL-BOUNDED: **0/54**
- SB-INDEFINITE: **0/54**

---

## §3 Non-Transits

None. Batch-56 is the final live-ledger substitution transit: no canonical row remains outside a counted RETIRED disposition.

---

## §4 Filing Footer

| Field | Value |
|---|---|
| Artifact | `.harness/phase-7d-retirement-events-batch-56.md` |
| Filed at | 2026-06-09 |
| Phase | Phase 7 sub-phase 7d — post-Phase-8 AS->IS seam back-flow |
| Predecessor batch | batch-55 |
| Transits | H_T-CXA-1 PARTIAL -> SUBSTANTIVE_RETIRED |
| Roadmap closures | R-CXA-1 RESOLVED |
| Co-published artifacts | `.harness/substitutions.yaml`; `tools/test_substitution_ledger.py`; `tools/dashboard/generate.py`; `Project_Roadmap_v1.md`; `.harness/roadmap_status.md`; `.harness/post-phase-8-forward-register.md`; `tools/dashboard/roadmap.html`; `.harness/r-cxa-1-as-is-edge-audit-2026-06-09.md` |
| Cross-axis cascade | AS->IS producer-gated seam fully accounted; no remaining non-retired substitution rows |
| Production code change | YES — stage-5 resolver binding plus resolver-aware `RuntimeAsIsWiring` secret-fetch write |
| Test change | Runtime/factory tests plus substitution-ledger expected counts updated to 54/54 retired and 54/54 pipeline-advanced |
| Spec / plan amendment | ZERO |
