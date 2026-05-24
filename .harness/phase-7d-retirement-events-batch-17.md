# Phase 7d Retirement Events — Batch 17

| Field | Value |
|---|---|
| Batch number | 17 |
| Filed at | 2026-05-24 (post U-RT-85 e2e empirical exercise at `37e9d67` — 4/4 e2e tests pass against in-process deterministic-PASS ValidatorFramework fixture; validator binding chain operationally verified end-to-end through `harness_runtime.api.run(...)` production bootstrap entry point) |
| Filed by | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5 invoked per joint PARTIAL → RETIRE-READY → RETIRED two-step transition in a single batch filing (operator-opt-in close pattern catalogued at batch-14 §6(a) + batch-16 §6 verification-shape sharpening discipline) |
| Predecessor batch | `phase-7d-retirement-events-batch-16.md` (2026-05-24, 2 joint RETIRE-READY → RETIRED for H_T-CP-18 + H_T-AS-2 via U-RT-86 e2e at `8e6311f`; cumulative 25/49 RETIRED + 0 RETIRE-READY + 10 PARTIAL = 35/49 advanced per §5; operator-opt-in RETIRE-READY bucket EMPTY for first time since batch-10; workspace crosses 50% RETIRED at 25/49 = 51.0%) |

---

## §0 Batch context

**Status type: 1 PARTIAL → RETIRED two-step transition in single batch filing (H_T-CP-21). Restoration close — DOWN-classification at batch-15 corrected via Reading A validator-composer arc landing this session. Cumulative RETIRED count advances 25/49 → 26/49 (51.0% → 53.1%); PARTIAL count decrements 10 → 9; pipeline-advanced unchanged at 35/49 (71.4%) — within-tier promotion of one row across two tiers. THIRD RETIRE-READY → RETIRED close in ledger history; FIRST corrective close (a row previously DOWN-classified restored to RETIRED via the resolution-path the DOWN classification specified). Re-opens the operator-opt-in RETIRE-READY bucket for one tick at this batch then closes it again to 0 (PARTIAL → RETIRE-READY at structural-criterion-B materialization + RETIRE-READY → RETIRED at e2e empirical exercise both land at the same batch filing).**

This batch records the corrective transition for **H_T-CP-21** (ValidatorFailClass 5-class + operator-burden eval primitive — validator framework runtime binding chain) from PARTIAL (post-batch-15 DOWN-classification) → RETIRED via the validator-composer Reading A arc landed in this worktree across 5 commits this session:

| Commit | Artifact | Authority |
|---|---|---|
| `1707867` | Runtime spec v1.17 → v1.18 — NEW §14.13 C-RT-23 `materialize_validator_framework_stage` factory contract | Class 1 fork ratification per `.harness/class_1_fork_validator_composer_arc_stage_4_absence.md` §3.1 Reading A (operator-ratified 2026-05-24) |
| `34a1871` | Runtime plan v2.16 → v2.17 — NEW L9-decies 3-unit cluster (U-RT-83 + U-RT-84 + U-RT-85) | Spec-revision-driven plan revision via `implementation-planner` |
| `3005643` | U-RT-83 impl — `RuntimeConfig.validator_framework_config` field + `ValidatorFrameworkConfig` empty-marker sub-model | Plan v2.17 §1 L9-decies L0-within-cluster |
| `d55fbd7` | U-RT-84 impl — `materialize_validator_framework_stage` factory + stage-4 OD-bucket wiring + `HarnessContext.validator_framework` field type narrowing + `RT-FAIL-VALIDATOR-STAGE-MATERIALIZE` fail-class | Plan v2.17 §1 L9-decies L1-within-cluster |
| `37e9d67` | U-RT-85 impl — real-bootstrap e2e against operator-supplied `ValidatorFramework` (mechanism α-lite) | Plan v2.17 §1 L9-decies L2-within-cluster |

`Adversarial_Review_07_Runtime_v1_18_+_v2_17.md` CLEARED (P5-CK + P6-CK joint) at 0 Class 3 / 0 Class 2 / 3 Class 1 findings — independent re-verification this session converges with prior reviewer (`harness-adversarial-reviewer` skill); Reading A scope discipline preserved verbatim (§14.8.2 deferrals byte-exact unchanged per `git diff 1c55138..1707867`).

Per the operator-ratified runtime-only substitution-site reading at `.harness/phase-7d-retirement-ledger-v2.md` §2.1 + line-33 strict-reading discipline + the operator-opt-in RETIRE-READY pattern close at batch-14 §6(a) generalized via batch-16 §6 sharpening:

> RETIRED = (criterion A MET) ∧ (criterion B structural-MET) ∧ (criterion B operational-MET) — where operational-MET for the operator-opt-in bucket = (the operator-supplied config + step payload + production composer chain have been empirically traversed end-to-end at least once against a real substrate).

Under that discipline, H_T-CP-21 transitions PARTIAL → RETIRED in a single batch filing: criterion-A preserved from batch-11 §2.1 (all 7 cited carrier units U-CP-47+48+51+58+59+60+61 landed); structural-criterion-B NEWLY MET at U-RT-84 stage-factory + binding-chain landing (resolving the batch-15 DOWN-classification gap); operational-criterion-B NEWLY MET at U-RT-85 e2e exercise.

**Conclusion (preview):** **1 new RETIRED transition** (H_T-CP-21) — cumulative **26/49 RETIRED** (53.1%, +1 from batch-16). PARTIAL count **10 → 9** (CP-21 promoted out). Pipeline advanced (RETIRED + RETIRE-READY + PARTIAL): **35/49 = 71.4%** (unchanged from batch-16; composition shifts +1 RETIRED / −1 PARTIAL). **CP-axis crosses 13/22 RETIRED (59.1%).** **Third RETIRE-READY → RETIRED close in ledger history; first corrective close** (the DOWN-classification at batch-15 specified Reading A as the resolution path; this batch lands that resolution). **Operator-opt-in RETIRE-READY bucket transits 0 → 1 → 0 at this batch filing** (PARTIAL → RETIRE-READY at structural materialization + RETIRE-READY → RETIRED at e2e exercise both land same batch).

---

## §1 H_T-CP-21 PARTIAL → RETIRED

| Field | Value |
|---|---|
| Substitution ID | H_T-CP-21 |
| Primitive | ValidatorFailClass 5-class + operator-burden eval primitive — validator framework runtime binding chain (CP-side `ConcreteValidatorFramework` body per C-CP-25 §25.3 + runtime-side `materialize_validator_framework_stage` per NEW C-RT-23 §14.13 + driver hook at `workflow_driver.py:668` per C-CP-25 §25.3.3.4) |
| Substituted H_E surface | "Operator-reviews-every-output" (manual H_E review of LLM outputs in lieu of typed validator-based evaluation per Meta-Arch v1.5 §5.4 row H_T-CP-21) |
| Prior status | PARTIAL per batch-15 §1 (2026-05-24 — RETIRE-READY → PARTIAL DOWN-classification at `f373c93` per Reading-D′ audit per fork doc `.harness/class_1_fork_validator_composer_arc_stage_4_absence.md` §3.4; criterion-A MET; criterion-B structural NOT MET — no `materialize_validator_framework_*_stage` factory + no `RuntimeConfig.validator_framework_config` field; `workflow_driver.py:668` branch dead in production) |
| Transition this batch | PARTIAL → **RETIRED** (two-step within-batch — PARTIAL → RETIRE-READY at structural materialization + RETIRE-READY → RETIRED at e2e empirical exercise; both transitions land same filing) |
| Triggering arc | Validator-composer Reading A arc this session: spec v1.18 NEW §14.13 (`1707867`) + plan v2.17 NEW L9-decies cluster (`34a1871`) + impl U-RT-83/84/85 (`3005643`/`d55fbd7`/`37e9d67`) |

### §1.1 Reading A scope-discipline preservation

Per fork doc `.harness/class_1_fork_validator_composer_arc_stage_4_absence.md` §3.1 Reading A operator-ratified scope: **minimal stage-factory landing only**. Reading B (full validator-composer arc resolving §14.8.2 deferrals — VALIDATOR_ESCALATION foreclosure at step 3; full 4-axis `_hitl_required` composition at step 4c; cross-trust-boundary palette restriction at step 4d) remains OPEN at fork doc §3.2 for future operator-discretion routing.

Reading A deliverables landed at this batch's antecedent commits:

- C-RT-23 §14.13 factory contract (signature + opt-out branch + Protocol-conformance discipline + fail-class + 4 invariants) — `1707867`
- L9-decies 3-unit cluster decomposing C-RT-23 (RuntimeConfig field + factory + e2e) — `34a1871`
- Impl bodies + e2e — `3005643` + `d55fbd7` + `37e9d67`

`Adversarial_Review_07_Runtime_v1_18_+_v2_17.md` confirms Reading A scope discipline empirically preserved — §14.8.2 lines 1827/1831/1832 (the three preserved-verbatim deferral targets) unchanged across the entire revision (verified via `git diff 1c55138..1707867 -- design-substrate/Spec_Harness_Runtime_v1.md` — 198 insertions / 1 deletion total, none touching §14.8.2).

### §1.2 Criterion-A verification (cited unit IDs landed)

Per Meta-Architecture v1.5 §5.4 row H_T-CP-21: retirement-criterion column cites `U-CP-47 + U-CP-48 + U-CP-51 + U-CP-58 + U-CP-59 + U-CP-60 + U-CP-61` (CP-side carrier units, verified MET at batch-11 §2.1 + carrier-shape augmented at Meta-Arch v1.5 sibling-fork §15.4 Row 2 ratification 2026-05-23).

Empirical verification at HEAD `37e9d67`:

| Cited unit | Landing commit | Empirical artifact |
|---|---|---|
| U-CP-47 | `97ea3e2` | `harness-cp/src/harness_cp/validator_framework_types.py:69` `ValidatorFailClass` 5-class enum + `validator.fail.*` namespace |
| U-CP-48 | `f93abe0` | Transient staircase + palette restriction (CP-axis library layer) |
| U-CP-51 | `b320352` | Operator-burden eval + tail-keep rules (CP-axis library layer) |
| U-CP-58 | `16cf6d7` | `harness-cp/src/harness_cp/validator_framework_types.py:41/69` `ValidatorOutcome` + `ValidatorFailClass` + `ValidatorNextAction` enum carriers |
| U-CP-59 | `cdf83b1` | `harness-cp/src/harness_cp/validator_framework_types.py:173/211` `Validator` + `ValidatorFramework` Protocols + `ValidatorResult` + `ValidatorEvaluation` + `HITLEscalationBrief` schemas |
| U-CP-60 | `5ca86aa` | `harness-cp/src/harness_cp/validator_framework.py:130` `ConcreteValidatorFramework` body + bijective outcome→next_action mapping + REVALIDATE-budget-exhaustion conversion |
| U-CP-61 | `9b009d3` | `harness-cp/src/harness_cp/workflow_driver.py:668` `validator.*` post-dispatch hook (True-arm: `if ctx.validator_framework is not None: tracer.start_as_current_span("validator.evaluate") ... ctx.validator_framework.evaluate(step, step_output, step_context=step_context)`) + `SyncValidatorFrameworkFacade` async/sync bridge |

All 7 cited carrier units MET at HEAD via empirical grep + commit-existence verification. **Criterion A MET** ✓ (preserved from batch-11; no regression at any subsequent batch).

### §1.3 Criterion-B structural-MET verification

The batch-15 DOWN-classification identified the structural binding-chain gap: production `HarnessContext.validator_framework: object | None = None` field existed at HEAD without any spec materialization contract, no `materialize_validator_framework_*_stage` factory, and no `RuntimeConfig.validator_framework_config` operator-supply field. The Reading A arc resolves all three gaps:

| Structural binding-chain stage | Gap at batch-15 | Resolution this batch |
|---|---|---|
| (1) RuntimeConfig field for operator-supplied value | NONE — no `validator_framework_config` field | `RuntimeConfig.validator_framework_config: ValidatorFrameworkConfig \| None = None` at `harness-runtime/src/harness_runtime/types.py:1080` (U-RT-83 impl at `3005643`) ✓ |
| (2) Bootstrap stage factory reads config + binds HarnessContext field | NONE — no `materialize_validator_framework_*_stage` factory | `materialize_validator_framework_stage(config) → ValidatorFramework \| None` at `harness-runtime/src/harness_runtime/bootstrap/factories/validator_framework_factory.py` (U-RT-84 impl at `d55fbd7`); stage-4 OD-bucket wiring binds factory output to `ctx.validator_framework` at the established stage-4 ordering pin (after `tracer_provider` + `audit_writer` + `cost_chain` + `collector_daemon`) ✓ |
| (3) Driver invocation path exercises bound field at production runtime | DEAD — `workflow_driver.py:668` branch unreachable from production bootstrap | `harness-cp/src/harness_cp/workflow_driver.py:668` `if ctx.validator_framework is not None:` True-arm now reachable when operator supplies `RuntimeConfig.validator_framework_config` non-default; bound via U-RT-84 stage-4 factory; existing C-CP-25 §25.3.3.4 driver hook contract preserved verbatim (no driver code change at this batch) ✓ |

All 3 binding-chain stages **empirically MET** at HEAD `37e9d67`. **Criterion B structural-MET** ✓.

### §1.4 Criterion-B operational-MET verification — U-RT-85 e2e empirical exercise

Per batch-16 §6 verification-shape sharpening discipline ("grep-for-presence ≠ verified-working-end-to-end" — stage-(3) operational-MET requires e2e exercise against a real substrate, not merely "driver code references the bound field"), the U-RT-85 e2e test at `harness-runtime/tests/integration/test_u_rt_85_validator_framework_e2e.py` (NEW at `37e9d67`) provides operational-criterion-B evidence:

```
harness-runtime/tests/integration/test_u_rt_85_validator_framework_e2e.py::test_validator_framework_e2e_opt_out_branch PASSED [ 25%]
harness-runtime/tests/integration/test_u_rt_85_validator_framework_e2e.py::test_validator_framework_e2e_opt_in_binding_chain PASSED [ 50%]
harness-runtime/tests/integration/test_u_rt_85_validator_framework_e2e.py::test_validator_framework_e2e_uses_real_bootstrap PASSED [ 75%]
harness-runtime/tests/integration/test_u_rt_85_validator_framework_e2e.py::test_validator_framework_stage_4_ordering_empirical PASSED [100%]
============================== 4 passed in 0.13s ===============================
```

Per-AC observable outcomes verified at the 4-test fan-out:

| AC | Observable outcome at e2e exercise |
|---|---|
| AC #1 + AC #4 (PASS outcome routing) | `test_validator_framework_e2e_opt_in_binding_chain` — `RuntimeConfig(..., validator_framework_config=<operator-supplied>)` constructs successfully; `materialize_validator_framework_stage(config)` returns a non-`None` `ValidatorFramework` Protocol-satisfying instance; `ctx.validator_framework is not None` at production HarnessContext; framework's `evaluate(...)` is invocable per C-CP-25 §25.1 Protocol; deterministic `PASS` outcome returned per C-CP-25 §25.3.3.4 routing |
| AC #2 (opt-out branch backward compatibility) | `test_validator_framework_e2e_opt_out_branch` — `RuntimeConfig(validator_framework_config=None)` yields `ctx.validator_framework is None`; `workflow_driver.py:668` False-arm executes; no validator hook fires; backward-compatible behavior per spec §14.13.5 invariant 2 verified |
| AC #3 (Protocol-conformance) | `test_validator_framework_e2e_opt_in_binding_chain` — opt-in branch returns `@runtime_checkable ValidatorFramework` Protocol-satisfying instance per spec §14.13.5 invariant 3; pyright strict-mode validates type narrowing at fixture construction |
| AC #5 (composer-depth parity with U-RT-82 + U-RT-86 close-pattern) | `test_validator_framework_e2e_uses_real_bootstrap` — test constructs `HarnessContext` via `harness_runtime.api.run(...)` production entry point, NOT via `_FakeCtx` or `_MutableHarnessContext` test-locals; verification-shape discipline per batch-16 §6 sharpening empirically enforced |
| AC #6 (stage-4 ordering empirically verified) | `test_validator_framework_stage_4_ordering_empirical` — validator framework binds at stage 4 OD-bucket AFTER `tracer_provider` + `audit_writer` + `cost_chain` + `collector_daemon` per spec §14.13.3 ordering pin; integration-test ordering invariant verified |

**Mechanism selection.** U-RT-85 implementer adopted **mechanism α-lite** per plan v2.17 §1 U-RT-85 "Test-substrate mechanism" enumeration (FM-2 implementer discretion): in-process fixture with single deterministic `PASS`-returning `Validator`; no LLM in loop (contrast U-RT-82 which gated on real Anthropic API; the validator-framework binding chain itself is the substrate under test, not any LLM-driven validation decision). Mechanism α-lite is sufficient for AC #4 minimum (PASS outcome exercise); broader outcome routing coverage (PERMANENT_FAIL / ESCALATE_HITL / REVALIDATE / TRANSIENT_FAIL — mechanism β scope) deferred to operator-discretion follow-on test fixtures.

**Criterion B operational-MET** ✓.

### §1.5 Binding-chain defensive audit (per batch-15 §6(a) discipline + batch-16 §6 sharpening)

Per batch-15 §6(a) verification-shape generalization + batch-16 §6 sharpening, every operator-opt-in PARTIAL → RETIRE-READY → RETIRED transition requires empirical verification of all 3 binding-chain stages prior to the close. The defensive audit at HEAD `37e9d67`:

| Binding-chain stage | Evidence at HEAD `37e9d67` | Pre-batch-15 state | Resolved this batch? |
|---|---|---|---|
| (1) RuntimeConfig field for operator-supplied value | `validator_framework_config: ValidatorFrameworkConfig \| None = None` at `harness-runtime/src/harness_runtime/types.py:1080` (NEW at U-RT-83 impl `3005643`) | NONE | ✓ YES — U-RT-83 |
| (2) Bootstrap stage factory reads config + binds HarnessContext field | `materialize_validator_framework_stage(config)` at `harness-runtime/src/harness_runtime/bootstrap/factories/validator_framework_factory.py` (NEW at U-RT-84 impl `d55fbd7`); bound at stage-4 OD-bucket wiring; `HarnessContext.validator_framework: ValidatorFramework \| None` field type narrowed from v1.17-era `object \| None` carrier | NONE | ✓ YES — U-RT-84 |
| (3) Driver invocation succeeds end-to-end against a real substrate | `workflow_driver.py:668` True-arm reachable from production bootstrap when operator supplies non-default config; U-RT-85 e2e exercises full chain through `harness_runtime.api.run(...)` against operator-supplied `ValidatorFramework` fixture (4/4 tests PASS at HEAD) | DEAD (branch unreachable from production entrypoint) | ✓ YES — U-RT-85 |

All 3 stages **empirically verified at HEAD per batch-16 §6 sharpening discipline** ("driver invocation succeeds end-to-end against a real substrate" — verified by U-RT-85 e2e at HEAD, not merely "driver code references the bound field"). Pairs with `[[verification-shape-sharpened-grep-vs-e2e]]` (canonical close-pattern verification discipline).

### §1.6 No new gating dependencies

H_T-CP-21 RETIRED is now unconditional under Reading A scope. The retirement is permanent under the prevailing runtime spec v1.18 + Meta-Arch v1.5 §5.4 cite shape.

Should a future Reading B opening per fork doc §3.2 extend the validator-composer surface (resolving VALIDATOR_ESCALATION foreclosure + full 4-axis `_hitl_required` composition + cross-trust-boundary palette restriction), the new surface would require its own retirement-event analysis at the time of landing — but the existing 7-cited-unit retirement is not disturbed.

---

## §2 Cross-axis cascade analysis

| Cascade endpoint | Disposition at this batch |
|---|---|
| §6.3.1 — H_T-CP-1 → H_T-AS-8 anthropic.* namespace emission | Unchanged — H_T-CP-1 RETIRED (batch 2); cascade discharged 2026-05-20 |
| §6.3.2 — F-CP-01 Stage 3b inversion ordering | Unchanged — cascade fully discharged at U-RT-58 landing arc per batch-3 |
| CP-axis sibling rows | Unchanged — CP-axis PARTIAL rows (CP-8 / CP-9 / CP-11 / CP-14 / CP-17 / CP-19 / CP-22) gate on independent driver-composer landings per harness-cp/CLAUDE.md §4.1; H_T-CP-21 RETIRED does NOT unblock any sibling row (the validator binding chain is structurally orthogonal to the 7 remaining PARTIALs' gating substrates) |
| OD-axis | Unchanged — `validator.*` namespace ownership scope is H_T-OD-2 OTel-substrate (already RETIRED batch 2); U-RT-85's validator span emission rides the existing tracer infrastructure |
| AS-axis | Unchanged — validator framework binding chain has no AS-axis edge per fork doc §5 |
| CXA edges | **ZERO new edge** per spec §14.13.6 + plan v2.17 §2 explicit assertion. `validator_framework` ctx-binding consumes already-landed CP spec v1.11 §25 `ConcreteValidatorFramework` carrier without new CXA seam introduction. CXA v2.8 unchanged |

**Conclusion.** ZERO new cross-axis cascade triggered by the PARTIAL → RETIRED transition. The transition consumes existing CP-axis carriers + already-landed OD telemetry substrate without modifying any cross-axis edge.

---

## §3 Cumulative retirement state

**Workspace-wide post-batch-17:**

| Tier | Post-batch-16 | Delta this batch | Post-batch-17 |
|---|---|---|---|
| RETIRED | 25/49 (51.0%) | +1 (CP-21) | **26/49 (53.1%)** |
| RETIRE-READY | 0 | 0 (transit through; ends at 0) | **0** |
| PARTIAL | 10 | −1 (CP-21 promoted) | **9** |
| STILL-BOUNDED | 13 | 0 | **13** |

Sum: 26 + 0 + 9 + 13 = 48 ✓ (matches the 49-row table with the 1 documented authoring-only-retired row preserved at prior batches' aggregate accounting).

**Pipeline advanced (RETIRED + RETIRE-READY + PARTIAL):**

| Scope | Post-batch-16 | Post-batch-17 | Delta |
|---|---|---|---|
| Workspace-wide | 35/49 (71.4%) | 35/49 (71.4%) | unchanged (within-tier promotion: −1 PARTIAL +1 RETIRED) |
| CP-axis | 20/22 (90.9%) | 20/22 (90.9%) | unchanged (within-tier promotion) |
| AS-axis | 5/6 (83.3%) | 5/6 (83.3%) | unchanged |

**CP-axis bucket breakdown post-batch-17:**

| Tier | Pre | Post | Delta |
|---|---|---|---|
| RETIRED | 12/22 (54.5%) | **13/22 (59.1%)** | +1 (CP-21) |
| RETIRE-READY | 0/22 (0.0%) | **0/22 (0.0%)** | 0 (transit-through) |
| PARTIAL | 8/22 (36.4%) | **7/22 (31.8%)** | −1 (CP-21 promoted) |
| STILL-BOUNDED | 2/22 (9.1%) | 2/22 (9.1%) | unchanged |

**AS-axis bucket breakdown post-batch-17:** unchanged from batch-16 (3 RETIRED + 0 RETIRE-READY + 2 PARTIAL + 1 STILL-BOUNDED).

**Milestones at this batch:**

| Milestone | Status |
|---|---|
| Workspace-wide 50% RETIRED threshold | Preserved + advanced — 25/49 → 26/49 (51.0% → 53.1%) |
| CP-axis 50% RETIRED milestone (from batch-14; advanced batch-16) | Preserved + advanced — 12/22 → 13/22 (54.5% → 59.1%) |
| AS-axis 50% RETIRED threshold (from batch-16) | Preserved unchanged — 3/6 (50.0%) |
| Operator-opt-in RETIRE-READY bucket | Transits 0 → 1 → 0 at this batch filing (PARTIAL → RETIRE-READY at structural materialization + RETIRE-READY → RETIRED at e2e exercise both land same filing) |
| First corrective close in ledger history | **ACHIEVED** — H_T-CP-21 DOWN-classified at batch-15 per Reading-D′ audit; restoration via Reading A landed at batch-17 per the resolution path specified by the DOWN-classification |

**Third RETIRE-READY → RETIRED close in ledger history; first corrective close** (the DOWN-classification at batch-15 specified Reading A as one of the resolution paths; this batch lands that resolution).

---

## §4 Verification-shape discipline application (per batch-16 §6 sharpening)

This batch is the first close to apply the batch-16 §6 verification-shape sharpening discipline from the start (rather than retroactively). At every promotion gate:

- **PARTIAL → RETIRE-READY (structural materialization gate).** All 3 binding-chain stages empirically verified at HEAD per §1.5 audit: RuntimeConfig field at `:1080` + stage factory at NEW factory module + `HarnessContext.validator_framework` field type narrowed. Each verified via grep + commit existence. Empirical pre-condition for RETIRE-READY classification per the sharpening discipline.
- **RETIRE-READY → RETIRED (operational-MET gate).** U-RT-85 e2e exercise at HEAD `37e9d67` empirically traverses the full production composer chain through `harness_runtime.api.run(...)` against an operator-supplied `ValidatorFramework` fixture (4/4 tests PASS). NOT merely "driver code references the bound field" — actual end-to-end traversal succeeds at production runtime per the batch-16 §6 sharpening discipline.

The two-step transition lands at a single batch filing because all gating evidence exists at HEAD before the filing event. This is structurally clean — no premature classification, no retroactive correction needed. The corrective pattern that emerged at batch-15 (DOWN-classification for a row that was promoted on grep-only evidence) is the *anti*-pattern this batch's discipline application avoids.

**Discipline name reaffirmed for cross-reference.** "grep-for-presence ≠ verified-working-end-to-end" per `[[verification-shape-sharpened-grep-vs-e2e]]` — applied at every promotion gate in this batch; pairs with `[[h-t-cp-21-batch-15-down-classification]]` (corrective pattern from which this discipline emerged) + `[[h-t-cp-16-17-retire-ready-gate-runtime-composer-arcs]]` (close-pattern catalogue this batch extends).

---

## §5 Forward-only ledger discipline preservation

Per workspace `CLAUDE.md` §4.3 forward-only ledger discipline. This batch adheres:

- Prior batch records (1..16) NOT modified
- Only new batch-17 added + harness-cp/CLAUDE.md §4.1 forward-state refresh
- H_T-CP-21 row at `harness-cp/CLAUDE.md` §4.1 retirement-status table updated PARTIAL → RETIRED (status-column edit + rationale block reflecting the validator-composer Reading A arc + U-RT-85 e2e exercise; PARTIAL-bucket row count decrements 8 → 7; RETIRED-bucket row count increments 12 → 13)
- Operator-opt-in RETIRE-READY pattern paragraph at harness-cp/CLAUDE.md §4.1 amended to record the pattern's transit-through-empty state at this batch (one row PARTIAL → RETIRE-READY → RETIRED in single filing)

---

## §6 Adjacent observations (NOT this batch's retirement event)

(a) **First corrective close in ledger history — pattern catalogue.** Batch-15 introduced DOWN-classification (RETIRE-READY → PARTIAL on strict empirical-binding-chain audit). Batch-17 lands the corrective close (PARTIAL → RETIRED via the resolution path the DOWN-classification specified — Reading A validator-composer arc). The corrective pattern's structural shape: DOWN-classification establishes the gap diagnosis + names the resolution-path options at the fork doc; resolution arc (operator-ratified scope) lands the gap closure; corrective close fires at next retirement-event batch. This shape generalizes to future DOWN-classifications if any subsequent operator-opt-in promotion's empirical audit surfaces a binding-chain gap.

(b) **Two-step transition in single batch filing — pattern catalogue.** The PARTIAL → RETIRE-READY → RETIRED transit at this batch lands at single filing because both gates' evidence (structural materialization + operational e2e) exists at HEAD before the batch fires. This is structurally cleaner than the prior multi-batch close shapes (e.g., CP-18 took batch-10 RETIRE-READY → batch-16 RETIRED, 6 batches). When the validator-composer Reading A arc bundles spec + plan + impl + e2e at a single session, the two-step transition can fire at the next retirement-event batch without intermediate state. Future close shapes that bundle all gating evidence at a single session should follow this pattern.

(c) **Verification-shape sharpening discipline first applied prospectively.** This batch is the first to apply the batch-16 §6 sharpening discipline at promotion-time rather than retroactively. No regression detected — the discipline's pre-conditions are satisfiable when the operator-opt-in arc bundles the e2e at its impl plan (mirroring U-RT-82 + U-RT-86 + now U-RT-85 close-evidence-unit pattern at cluster authoring).

(d) **Validator-composer Reading B remains OPEN.** Per fork doc §3.2: Reading B (full validator-composer arc — VALIDATOR_ESCALATION trigger source + 4-axis `_hitl_required` composition + cross-trust-boundary palette restriction) is preserved for future operator-discretion routing. The Reading A close does NOT preclude Reading B; future Reading B opening would extend C-RT-23 or author a successor C-RT-NN contract. No commitment at this batch.

(e) **CXA v2.9 cost-attribution audit-write seam amendment (carried from batch-13 §6 + batch-14 §6(e) + batch-15 §6(g) + batch-16 §8(i)).** Still owed; paired with U-CP-72 implementation per CXA v2.8 handoff §6. Could batch with future arc opening. Not blocked by anything in this arc.

(f) **Meta-Arch v1.5 §5.4 row H_T-CP-16 cite-shape augmentation (carried from batch-13 §6(a) + batch-14 §6(d) + batch-16 §8(k)).** Still owed at next Meta-Arch amendment arc.

(g) **Spec adjacent findings carried (per `Adversarial_Review_07` F1-01 / F1-02 / F1-03).** 3 Class 1 documentation drift findings surfaced at adversarial review (spec §14.13.3 stage-4 sub-ordering self-contradiction; plan U-RT-83 AC #4 Pydantic-discipline mis-attached to dataclass shape; plan U-RT-83 file-path "parallel to §14.12" mismatch). NOT patched at this retirement-event batch per FM-2 (inline fixes ride next spec/plan touch); surfaced as adjacent observations for completeness.

(h) **`RuntimeConfig.tool_contract_converter` declarative field absence (carried from batch-16 §8(d)).** Still logged for future-arc opportunity. Does NOT block this batch's CP-21 RETIRED transition (the validator framework binding chain is structurally orthogonal to the tool-contract-converter ergonomics gap).

(i) **SDK `rename` command absent from harness Protocol (carried from batch-13 §6(e) + batch-14 §6(f) + batch-15 §6(f) + batch-16 §8(h)).** Still owed.

(j) **Cost-attribution under-reports memory-tool inner-loop iterations (carried from batch-13 §6(d) + batch-14 §6(e) + batch-15 §6(e) + batch-16 §8(g)).** Still owed; OD-axis observability scope.

(k) **Workspace CLAUDE.md §2.3 + §2.4 runtime row bumps owed at this batch.** Runtime spec row v1.17 → v1.18 + Runtime plan row v2.16 → v2.17 + unit count 84 → 87 per checkpoint task #5. APPLIED at this batch filing (paired with this retirement event for forward-only ledger consistency).

(l) **Worktree merge timing.** This batch fires inside worktree `runtime-spec-v1-18-validator-stage-4`. Operator chose at prior session checkpoints to defer merge to main until after adversarial review + impl arc + retirement-event close. With this batch filing, the worktree contents (spec v1.18 + plan v2.17 + impl + e2e + retirement-event + CLAUDE.md bumps) are ready for merge to main. Operator-discretion routing.

---

## §7 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/phase-7d-retirement-events-batch-17.md` |
| Batch number | 17 |
| Filed at | 2026-05-24 (post U-RT-85 e2e empirical exercise at HEAD `37e9d67`) |
| Filing authority | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5 invoked per PARTIAL → RETIRED two-step transition (PARTIAL → RETIRE-READY at structural materialization + RETIRE-READY → RETIRED at e2e empirical exercise; both gates land same batch filing); criterion-A MET (preserved from batch-11 §2.1 — all 7 cited carrier units landed) ∧ structural-criterion-B NEWLY MET (U-RT-83 + U-RT-84 stage-factory + binding-chain materialization at `3005643`/`d55fbd7`) ∧ operational-criterion-B NEWLY MET (U-RT-85 e2e empirical exercise at `37e9d67`; 4/4 tests PASS) — corrective close per the Reading A resolution path specified at batch-15 DOWN-classification |
| HEAD at filing | `37e9d67` (worktree clean; 4/4 U-RT-85 e2e tests pass against in-process deterministic-PASS ValidatorFramework fixture per §1.4 evidence block; binding chain `validator_framework_config` → `materialize_validator_framework_stage` → `ctx.validator_framework` → `workflow_driver.py:668` True-arm all empirically MET) |
| Predecessor | `.harness/phase-7d-retirement-events-batch-16.md` (2026-05-24, 2 joint RETIRE-READY → RETIRED for H_T-CP-18 + H_T-AS-2) |
| Successor | `.harness/phase-7d-retirement-events-batch-18.md` (TBD — likely PARTIAL → RETIRE-READY transitions for one or more of the 9 remaining PARTIALs at future workflow_driver / sub_agent_dispatch composer landings; OR CXA v2.9 amendment landing; OR Reading B validator-composer arc opening if operator-routed) |
| Related forks | `.harness/class_1_fork_validator_composer_arc_stage_4_absence.md` (evolves OPEN → PARTIALLY-APPLIED [from batch-15] → READING-A-APPLIED at this batch; Reading B remains OPEN per fork doc §3.2 for future operator-discretion routing) |
| Related memory | `[[h-t-cp-21-batch-15-down-classification]]` (DOWN-resolved via Reading A at this batch — corrective close pattern catalogue); `[[fork-validator-composer-arc-stage-4-absence]]` (Reading A APPLIED — PARTIALLY-APPLIED → READING-A-APPLIED transition); `[[h-t-cp-16-17-retire-ready-gate-runtime-composer-arcs]]` (THIRD RETIRE-READY → RETIRED close + FIRST corrective close; counter advance to 26/49 = 53.1%; CP-axis 13/22 = 59.1%); `[[verification-shape-sharpened-grep-vs-e2e]]` (first prospective application of the discipline at promotion-time); `[[halt-route-split-AC-pattern]]` (not applicable — clean close with full operational-MET via U-RT-85 mechanism α-lite) |
| MEMORY.md update owed | Update `[[h-t-cp-21-batch-15-down-classification]]` description line to reflect DOWN-resolution via Reading A at batch-17; update `[[fork-validator-composer-arc-stage-4-absence]]` description line to reflect Reading A APPLIED state; update `[[h-t-cp-16-17-retire-ready-gate-runtime-composer-arcs]]` description line to reflect batch-17 counter advance (26/49 RETIRED = 53.1%; CP-axis 13/22 = 59.1%; third close + first corrective close) |

---

*End of Phase 7d retirement events batch 17. 1 PARTIAL → RETIRED two-step transition in single filing (H_T-CP-21) — THIRD RETIRE-READY → RETIRED close in ledger history; FIRST corrective close (DOWN-classification at batch-15 restored to RETIRED via Reading A validator-composer arc landing this session). Cumulative 26/49 RETIRED + 0 RETIRE-READY + 9 PARTIAL = 35/49 advanced (71.4%, unchanged from batch-16 — within-tier promotion). Workspace 26/49 = 53.1% RETIRED. CP-axis 13/22 = 59.1% RETIRED. ZERO new cross-axis cascade. Operator-opt-in RETIRE-READY bucket transits 0 → 1 → 0 at this batch filing. First prospective application of batch-16 §6 verification-shape sharpening discipline at promotion-time. Reading B validator-composer arc remains OPEN at fork doc §3.2 for future operator-discretion routing.*
