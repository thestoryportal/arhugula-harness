# Phase 7d Retirement Events — Batch 42 (2026-05-28)

**Filed:** 2026-05-28 (deployment-readiness closure arc — sole substantive transit ledger v2 row-text vs production state)
**Scope:** Single-row STILL-BOUNDED → PARTIAL transit for H_T-CXA-4 (OD → IS / AS / CP substrate consumption) per empirical re-audit at HEAD `a0ad1be`.
**Closure event class:** Ledger row-text vs production-state supersession (mirror CXA-5 batch-3 supersession at §11.1a 2026-05-28 same calendar day). Distinct from sub-species 10 categorical-mismatch (batch-37..41 cohort) — this transit is empirical-grounded substantive advancement, not doc-hygiene reclassification.

---

## §1 H_T-CXA-4 STILL-BOUNDED → PARTIAL

### §1.1 Row-text staleness evidence

Pre-batch ledger v2 §7 row 156 + workspace `CLAUDE.md` §1.1 + `harness-cxa/CLAUDE.md` (if exists) framed CXA-4 with two claims, both **FALSE at HEAD per empirical grep 2026-05-28**:

| Claim (pre-batch) | Empirical state at HEAD | Production-site evidence |
|---|---|---|
| "`ctx.audit_writer.append` has zero non-test callers in production code (only `read_all` in shutdown)" | **6 production callers** of `audit_writer.append` | `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py:497`; `:cost_attribution_llm_dispatch.py:241`; `:hitl_gate_composer.py:699`; plus `cost_attribution_{tool,validator,webhook}_dispatch.py` (3 sibling production sites) |
| "OD `sign_audit_entry` / `AuditLedgerEntry` compose path not invoked from any runtime driver" | **Compose path exercised at production** | `harness-cxa/src/harness_cxa/cp_audit_conversion.py:321` invokes `sign_audit_entry(payload, key_id=key_id, algo=algo)`; `:324` constructs `AuditLedgerEntry(...)`; consumed by the 6 production `audit_writer.append` sites above |

Both stale claims trace to original CXA-4 row authoring at ledger v2 §7 prior to U-RT-59 + U-OD-39 + U-OD-40 + cost-attribution chain landings. Carry-window: row authored at ledger v2 §7 publication (date unknown; pre-2026-05-20 batches); claims preserved verbatim through batches 12 → 41 (~30 batches, ~10 days). Pattern catalogued — **stale-ledger-row-vs-production-state** sub-species of species 3 (resolved-but-carry-stale-inherited) at workflow v1.12 §7.4.7.2; sibling to CXA-5 §11.1a batch-3-vs-§7 carry catalogued earlier today.

### §1.2 Transit disposition — STILL-BOUNDED → PARTIAL (not RETIRE-READY)

**Refreshed empirical state:**
- **OD → IS bucket (4 canonical edges):** Audit-write seam (edge 1) fully wired-and-exercised at production via `cp_audit_to_od_audit` converter + 6 production callers. ≥1 of 4 edges exercised.
- **OD → AS bucket (10 canonical edges):** 1 materialized via `materialize_od_as_wiring_stage` at `bootstrap/stage_6_cxa_wiring.py:74` (bootstrap stage-6 fires at every harness composition). 1 of 10 materialized.
- **OD → CP bucket (12 canonical edges):** 3 materialized via `materialize_od_cp_wiring_stage` at `bootstrap/stage_6_cxa_wiring.py:78` (manifest-resolution + breaker-inversion verification fires at bootstrap per `od_cp_wiring.py:187-223`). 3 of 12 materialized.
- **Bootstrap composition:** All 3 composer-materialization stages (`od_is_wiring`, `od_as_wiring`, `od_cp_wiring`) fire at `stage_6_cxa_wiring.py:69 + 74 + 78` (verified empirically; not stub paths).

**Net advancement:** ~5 of 26 canonical edges materialized + 1 fully exercised at production beyond bootstrap (audit-write seam). Substantive transit from "zero production exercise" framing to "audit-emission path operational" — meets PARTIAL tier per X-AL-2 partial-retirement-is-non-retirement framing.

**Why not RETIRE-READY:** Per X-AL-2 retirement criterion, RETIRE-READY requires substrate-criterion-B MET (substituted H_E surface no longer invoked at substitution site) across the full canonical 26-edge scope. Empirical state shows ~21 of 26 edges remain unmaterialized at runtime composition layer. The audit-write seam exercise is genuine production advancement but not full-scope structural close.

**Refreshed row text (canonical going forward; row 156 PRESERVED VERBATIM at ledger v2 §7 per forward-only ledger discipline):**

> H_T-CXA-4 | OD → IS / AS / CP substrate consumption (26 canonical: 4+10+12) | **PARTIAL (batch-42)** | Three composer-materialization stages fire at `bootstrap/stage_6_cxa_wiring.py:69+74+78` (od_is_wiring + od_as_wiring + od_cp_wiring); bootstrap manifest-resolution + breaker-inversion verification at `od_cp_wiring.py:187-223` (✓). **OD audit-write seam fully exercised at production** via `cp_audit_to_od_audit` converter (`harness-cxa/.../cp_audit_conversion.py:321,324`) consumed by 6 production callers of `audit_writer.append` (`sub_agent_dispatch.py:497` + `hitl_gate_composer.py:699` + `cost_attribution_{llm,tool,validator,webhook}_dispatch.py`). Of 26 canonical edges: ~5 materialized + 1 fully exercised. PARTIAL → RETIRE-READY transit gated on remaining ~21 edges either (α) materialization at runtime composition layer per Phase 6 plan-revision OR (β) operator-discretion canonical-scope narrowing of CXA-4 26-edge enumeration (parallel to AS-8e/AS-8f indefinite-defer pattern but at typed-edge granularity).

### §1.3 Workspace cumulative refresh

Pre-batch-42:
- 43/54 RETIRED (79.6%) + 2/54 RETIRE-READY (3.7%) + 3/54 PARTIAL (5.6%) + 4/54 STILL-BOUNDED (7.4%) + 2/54 STILL-BOUNDED-INDEFINITELY (3.7%)
- Pipeline-advanced: 48/54 = 88.9%

Post-batch-42:
- 43/54 RETIRED (79.6%) + 2/54 RETIRE-READY (3.7%) + **4/54 PARTIAL (7.4%)** + **3/54 STILL-BOUNDED (5.6%)** + 2/54 STILL-BOUNDED-INDEFINITELY (3.7%)
- Pipeline-advanced: **49/54 = 90.7%** (+1 from CXA-4 entering PARTIAL bucket)

Remaining STILL-BOUNDED bucket post-batch-42: {IS-2, CXA-2, CXA-3} — 3 rows. CXA-3 audit-empty at §11.1b 2026-05-28. CXA-2 + IS-2 covered at sibling closures this session.

---

## §2 ZERO scope outside CXA-4 row transit

- ZERO production code change at this batch
- ZERO test addition / modification
- ZERO spec / plan / CXA / ADR / ADD / PRD substantive amendment (Class 3 informational doc-hygiene at ledger v2 §11.1c — sibling delta this session)
- ZERO cross-axis cascade (intra-CXA-axis row transit only)

---

## §3 Sub-species catalogue impact

**Sub-species 10 catalogue** at workflow v1.12 §7.4.7.2 stays at cardinality 5 (batch-37..41 cohort); batch-42 transit is NOT sub-species 10 (advancement is empirical-grounded production-state-vs-row-text refresh, not categorical-mismatch authoring-only closure).

**Sub-species 3 catalogue** at workflow v1.12 §7.4.7.2 expanded — **NEW sub-species candidate `stale-ledger-row-vs-production-state`** catalogued at batch-42 §1.1. Sibling to CXA-5 §11.1a batch-3-vs-§7 closure-event-class (also 2026-05-28 same calendar day; both surface row text drift from production state across multi-batch carry windows). Cardinality at this candidate now 2 in single calendar day; species 3 sub-species column extension at workflow v1.13 (future) increasingly warranted (10 species-3 sub-species catalogued across the 2-day cluster 2026-05-27 → 2026-05-28).

---

## §4 Filing footer

| Field | Value |
|---|---|
| Closure event | H_T-CXA-4 STILL-BOUNDED → PARTIAL |
| Closure shape | Ledger row-text vs production-state supersession (substantive empirical advancement) |
| Authority anchor | Empirical grep at HEAD `a0ad1be` 2026-05-28 (6 audit_writer.append callers + cp_audit_conversion.py:321,324) |
| Scope (X-AL-3 discipline) | ZERO new H_T contract; ZERO spec extension; row-text refresh only |
| Cross-axis cascade | NONE (intra-CXA-axis) |
| Sub-species | New candidate `stale-ledger-row-vs-production-state` at species 3 (cardinality 2 in single day with CXA-5 §11.1a sibling) |
| Workspace post-batch | 43/54 RETIRED + 2 RR + 4 PARTIAL + 3 STILL-BOUNDED + 2 SB-INDEFINITE = 54 ✓; pipeline-advanced 49/54 = 90.7% |
