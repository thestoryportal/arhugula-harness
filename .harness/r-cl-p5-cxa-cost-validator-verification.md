# R-CL-P5 — CXA phase-2 edge verification + cost-model + validator depth

**Filed at:** R-CL-P5 close (2026-06-10). Phase-7 posture (verify-emit + impl-docstring hygiene + roadmap-framing correction).
**Authority:** `Project_Roadmap_v1.md` §5.15 R-CL-P5; `.harness/post-mvp-full-closure-plan-v1.md` Phase P5.
**Grounding:** advisor-confirmed (two passes — the first hypothesized "cost is the real build"; the bootstrap-wiring grep overturned it; reconciled to verify-emit). Decorrelation record below.

This is the **verify-emit** record for R-CL-P5. The roadmap's optimistic "bind default tables + wire edges" framing was grounding-falsified across all three sub-parts: the CXA phase-2 edges are already materialized at stage 6 (CXA-4 0-wireable precedent, CXA v2.19 §0.9), the cost default table + chain are already wired through bootstrap, and the validator sub-part rests on a mis-citation of already-built surfaces. The genuine deliverables are: per-edge disposition (no padding, no rescue of deferred edges), two stale-docstring fixes, the cost verify-emit record, and a roadmap-framing correction.

---

## §1 — CXA 22/24 phase-2-runtime edges (must_pass #1 + #4)

### §1.1 Canonical count + the 24-vs-22 residual

- **Canonical headline: 22 phase-2-runtime** per CXA v2.19 §0.4 (`37 genuine + 48 convention + 22 phase-2-runtime = 107`) + root `CLAUDE.md` §1.1 + roadmap AC.
- **The §2.3.x bucket row-tables enumerate 24 R-tagged edges** (stable v2.3 → v2.17, "24 phase-2-runtime unchanged" at every delta; v2.19 preserved the §2.3.x tables verbatim). Per-edge classification + consumer evidence at `.harness/cxa_7c_audit_cp_buckets.md` + `.harness/cxa_7c_audit_od_buckets.md`.
- **The 2-edge gap (24 row-tagged vs 22 aggregate)** is a **design-substrate §2.3-rows-vs-§2.1-aggregate bookkeeping residual** introduced across the v2.14 (30G/46C/24R=100) → v2.17 (37G/48C/22R=107) delta growth. It is a **Class 3 informational** finding: it is NOT resolved here (editing the CXA doc to reconcile the row-tags to the aggregate is design-phase posture / X-AL-3 from a phase-7 session). Routed to a future CXA fidelity-pass per the v2.19 §0.6 wrong-version-read precedent.

### §1.2 Per-edge disposition (the 24 §2.3.x R-tagged edges — NOT padded)

**G** wired+emitting (verify-emit) · **C** convention/0-wireable (bootstrap verify, honest) · **D** deferred (U-RT-35 tension; NOT rescued — X-AL-3).

| Bucket | Edge(s) | n | Disp | Carrier / proof |
|---|---|---|---|---|
| AS→IS | U-AS-27 → U-IS-11 | 1 | **G** | `as_is_wiring.py` `RuntimeAsIsWiring.emit_secret_fetch_audit_entry` → `ledger_writer.append`; `test_lifecycle_as_is_wiring.py` (round-trip APPENDED + chain). |
| CP→IS | U-CP-14 → U-IS-07/08/09/11 | 4 | **G** | U-CP-74 `emit_override_state_ledger_entry`; consumed `workflow_driver.py:859`. |
| CP→IS | U-CP-27 → U-IS-07/09/11 | 3 | **G** | U-CP-75 `emit_workload_class_selection_state_ledger_entry`; consumed `stage_3b_cp_routing.py:122`. |
| CP→IS | U-CP-30 → U-IS-07 | 1 | **G** | U-CP-76 `emit_pause_resume_state_ledger_entry`; consumed `workflow_driver.py:582/808/965`. |
| CP→IS | U-CP-34 → U-IS-08/09 | 2 | **C** | Canonicalize/hash (U-IS-08) + chain-construction (U-IS-09) are **discharged inside the IS `append_ledger_entry`** triggered by `emit_sibling_ledger_entry` — NOT a separate CP producer-emit (`cxa_7c_audit_cp_buckets.md` rows 20–21: "happen inside that append call; no U-IS-08/09 symbol imported"). The genuine `U-CP-34 → U-IS-11` sibling seam (what `sibling_ledger_entry_composition` proves; `test_lifecycle_cp_is_wiring.py`) is a **genuine-class** seam, separate from the phase-2-runtime 24. |
| CP→IS | U-CP-37 → U-IS-07/09 | 2 | **G** | U-CP-77 `emit_hitl_tool_call_rewriting_state_ledger_entry`; wired into `cp_is_wiring.py`. |
| CP→IS | U-CP-49 → U-IS-11 | 1 | **G** | U-CP-78 `emit_pause_captured_state_ledger_entry`. |
| CP→IS | U-CP-50 → U-IS-11 | 1 | **G** | U-CP-79 `emit_resume_attempted_state_ledger_entry`. |
| CP→IS | **U-CP-12 → U-IS-07** | 1 | **D** | NO composer at HEAD (`per_class_attribute_composition.py`). Authoring a runtime-layer composer = X-AL-3 per `.harness/class_1_tension_u_rt_35_cp_is_wiring_gaps.md`. |
| CP→IS | **U-CP-52 → U-IS-07/11** | 2 | **D** | NO composer at HEAD (`hitl_timeout_degradation.py` / `hitl_placement.py`). X-AL-3 per the same tension doc. |
| OD→IS | U-OD-30 → U-IS-11 | 1 | **G** | audit-ledger write composition; `od_is_wiring` re-exposes the stage-4-bound `audit_writer`. |
| OD→IS | U-OD-34 → U-IS-17 | 1 | **C** | terminal-exporter manifest string-ref; `resolve_od_is_manifest_references` (bootstrap). |
| OD→AS | U-OD-34 → U-AS-33 | 1 | **C** | manifest string-ref + `verify_as_namespace_coverage` (bootstrap). |
| OD→CP | U-OD-09 → U-CP-54 | 1 | **C** | F-CP-01 Stage 3b inversion: `verify_harness_breaker_namespace_inversion` (bootstrap). |
| OD→CP | U-OD-34 → U-CP-54 | 1 | **C** | manifest string-ref. |
| OD→CP | U-OD-34 → U-CP-55 | 1 | **C** | F2-12 carry-forward manifest ref. |

**Totals: 24 R-tagged edges = 14 G (separate producer-emit) + 7 C (convention / 0-wireable / runtime-delegated-to-IS-internals) + 3 D (deferred).** No edge is padded; the 3 deferred edges are honestly recorded, NOT rescued by runtime-layer wiring (the U-RT-35 tension doc names that exact move as X-AL-3). Within CP→IS (17 edges): 12 G + 2 C (U-CP-34) + 3 D.

> **U-CP-34 enumeration divergence (Class 3 informational).** Runtime spec §12.3 enumerates U-CP-34's CP→IS edge as `→ U-IS-11` (the genuine sibling-ledger append seam; `cp_is_wiring.emit_sibling_ledger_entry`), whereas CXA §2.3.2 tags U-CP-34's phase-2-runtime edges as `→ U-IS-08/09` (the hash/chain steps discharged inside that append). The two specs enumerate U-CP-34's CP→IS contribution differently — a cross-spec edge-enumeration drift routed to a future CXA/Runtime fidelity-pass (NOT resolved here — design-phase posture).

### §1.3 The U-CP-74..79 back-flow landed (cp_is_wiring docstring was stale)

The 2026-05-28 RE-OPENED `class_1_tension_u_rt_35_cp_is_wiring_gaps.md` (1-of-17 wired; 7 gap-A units + U-CP-14 gap-B deferred) was **resolved via the CP plan v2.28 U-CP-74..79 cohort**: U-CP-74 (override / gap-B U-CP-14), U-CP-75 (U-CP-27), U-CP-76 (U-CP-30), U-CP-77 (U-CP-37), U-CP-78 (U-CP-49), U-CP-79 (U-CP-50) — all six §16.5 `emit_*_state_ledger_entry` composers exist, are imported into `cp_is_wiring.py`, and are consumed by real producers (`workflow_driver.py`, `stage_3b_cp_routing.py`). The `cp_is_wiring.py` module docstring still claimed "1 of 17 / U-CP-12/27/30/37/49/50/52 DEFERRED" — **stale**; reconciled in this PR. Current state: **7 of 9 CP→IS source units wired (U-CP-34 + U-CP-74..79); 2 still deferred (U-CP-12, U-CP-52)**.

### §1.4 Doc-drift fixes (must_pass #4)

- `stage_6_cxa_wiring.py:4` — `24` → `22` canonical (CXA v2.19 §0.4) + removed the false "all wired" completeness claim (3 edges deferred).
- `cp_is_wiring.py` module docstring — `1 of 17 / 7 deferred` header reconciled to the U-CP-74..79-landed reality (2 source units deferred).

---

## §2 — Cost-attribution rate tables (must_pass #2) — VERIFY-EMIT (already wired)

**Finding: the cost default table + 5-step chain are already wired end-to-end through the production bootstrap.** No build owed.

- **Default table built:** `harness_od/rate_table_v1.py` `RATE_TABLE_V1` (U-OD-47) — per-provider default rates for the 3 ADR-F1 providers (anthropic input $3 / output $15 /MTok + cache; openai $2.50/$10; ollama $0). PLACEHOLDER list-price snapshots, operator-overridable per §C-OD-28.5.
- **Wired through bootstrap:** `stage_4_od.py:106` + `stage_5_loop_init.py:193/202` thread `rate_table=RATE_TABLE_V1` into the tool dispatcher, validator dispatch, and LLM dispatch (`llm_dispatch.py:721/1341`). The live path uses the **explicit-`rate_table` param** (the deployment-binding-time default route the OD plan §3.5.4 authorizes: "rate-table residence deferred to U-OD-21 **or deployment-binding-time refresh**"). The `_lookup_rates(PRICE_TABLE_REF)` raise is the **dead/bypassed opaque-singleton path**, not the live one — so "until U-OD-21 lands" is not a blocker.
- **Non-zero proof against the real default table:** `test_lifecycle_cost_attribution_llm_dispatch.py` imports `RATE_TABLE_V1` and asserts non-zero cost from its anthropic rates (NOT an injected fixture — addresses the `[[test-bypass-as-runtime-truth-pattern]]` risk).
- **Fires-through-bootstrap proof:** `test_r100_real_workflow_e2e.py` AC #4 drives a real workflow through stage-5 bootstrap; each LLM dispatch invokes `attribute_llm_dispatch_cost → audit_writer.append` (presence per dispatch). A live provider is NOT required — cost runs post-usage from token counts.
- **LLM, not tool, is the non-zero path:** `RATE_TABLE_V1.tool_rates` ships empty (`_DEFAULT_TOOL_RATES = {}`); a default tool dispatch fail-closed-swallows (`ToolRateMissingError` → best-effort no-op). Non-zero is satisfied by the **LLM** dispatch against populated provider rates.

**Honest residual:** `RunResult.cost_attribution = ()` is hardcoded empty (`api.py:602`) — the U-RT-49-struck **aggregate-surfacing** at the workflow-driver boundary. The per-dispatch `cost:` writes land in the **audit ledger**, not RunResult. Surfacing the aggregate on RunResult remains a separate bounded residual (U-RT-49), not a P5 deliverable.

---

## §3 — Validator-framework thresholds (must_pass #3) — VERIFY-EMIT + roadmap mis-cite correction

**Finding: the roadmap's "bind which validator runs at which sandbox-tier threshold (ADR-D2 §1.9)" is a category-confused mis-citation of already-built surfaces.** No row-11 to build (the Explore agent's proposed "validator-outcome → tier-elevation" row self-flagged "design decision required" = the X-AL-3 tell — NOT built). No design defect to fork — the design is fine; the roadmap's *summary* of it was wrong.

- **ADR-D2 §1.9 is "Sandbox-pool warm-up protocol"** (ADR-D2.md:297), NOT a validator-tier binding. Confirmed.
- **The actual validator/tier surfaces are already built + spec'd:**
  1. **Validator fires post-step** — `harness_cp/validator_framework.py` `ValidatorFramework` + `ValidatorOutcome → ValidatorNextAction` map (PASS→PROCEED, ESCALATE→ESCALATE_HITL, PERMANENT_FAIL→ABORT, …); tested `test_validator_framework.py`.
  2. **`sandbox_tier` is the 5th gate-level floor** — ADR-D2 §332(d): "With D5 §1.5 multiplicative gate-level rule: D2 specializes the four-axis tunable to **five axes adding `sandbox_tier`**." Built at `harness_as/gate_level_composition.py` (`max()` over 5 floors incl. `sandbox_tier_floor`); tested `test_sandbox_tier_floor.py`.
  3. **sandbox-violation → validator-escalation staircase** — ADR-D2 §2.3 / §1.8 + AS spec §513 + D5 §1.5/§1.10: 1st fail → C9 backoff; 2nd → C6 model-tier escalation; 3rd → C11 HITL; permanent-fail (escape_attempt) → immediate HITL. The validator-failure shape generalizes the sandbox-violation case (`c5-validation-contract` taxonomy).
- **Disposition:** verify-emit (all three surfaces built + tested) + correct the roadmap R-CL-P5 entry's mis-cite (ADR-D2 §1.9 → §2.3/§332(d) + D5 §1.5). Process-substrate correction (mode-agnostic), not a design-substrate edit.

---

## §4 — Decorrelation record (advisor × grounding)

The advisor (transcript-aware) hypothesized "cost is the real build; closing P5 as all-verify would be the scope-narrowing failure" — a correct guard against my initial swing toward all-verify/fork. The bootstrap-wiring grep (`stage_4_od.py:106` / `stage_5_loop_init.py:193`) overturned the hypothesis: cost is already wired. On reconcile, the advisor accepted the primary evidence ("ignore my 'cost is the real build'") and sharpened the verify-emit close (LLM-not-tool non-zero path; RATE_TABLE_V1-not-fixture proof; audit-ledger-not-RunResult assertion). Net: the decorrelation forced the check that produced the accurate disposition — neither over-claim (a build that wasn't owed) nor under-claim (silent scope-narrowing). One environment artifact was caught en route (§14.3): an early "RATE_TABLE_V1 is an orphan" grep returned empty due to RTK pipe-mangling; re-grounding found the 4 bootstrap consumers.

## §5 — Residuals carried forward (re-open triggers)

| Residual | Class | Re-open trigger |
|---|---|---|
| U-CP-12 + U-CP-52 CP→IS edges (3) unwired | Class 1 (U-RT-35) | CP plan composer authoring for `per_class_attribute_composition` + `hitl_timeout_degradation`/`hitl_placement` (design-phase back-flow) — same route as the U-CP-74..79 cohort. |
| CXA §2.3-rows (24R) vs §2.1-aggregate (22) | Class 3 informational | Future CXA fidelity-pass (v2.19 §0.6 wrong-version-read precedent). |
| `RunResult.cost_attribution = ()` aggregate-surfacing | Bounded residual (U-RT-49) | A real workflow-driver cost-rollup surfacing arc. |
