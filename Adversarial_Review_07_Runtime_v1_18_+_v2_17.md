# Adversarial Review 07 — Runtime Spec v1.18 + Runtime Plan v2.17 (Reading A validator-framework stage-4 binding chain)

## Summary

- **Checkpoint:** P5-CK (runtime spec v1.18 §14.13 NEW C-RT-23) + P6-CK (runtime plan v2.17 NEW L9-decies cluster U-RT-83/84/85)
- **Artifact reviewed:**
  - `design-substrate/Spec_Harness_Runtime_v1.md` at commit `1707867`
  - `design-substrate/Implementation_Plan_Harness_Runtime_v2_17.md` at commit `34a1871`
- **Date:** 2026-05-24
- **Finding count by class:** Class 3: 0 · Class 2: 0 · Class 1: 3
- **Highest-severity finding:** F1-01 (spec §14.13.3 stage-4 sub-ordering self-contradiction)
- **Disposition recommendation:** **CLEARED with inline documentation fixes.** No Class 2 or Class 3 findings; Reading A scope discipline preserved; §14.8.2 deferrals verbatim-preserved (empirically verified via `git diff`); all cited line numbers + commit SHAs resolve byte-exact at HEAD. Three Class 1 inline-clarification findings surfaced — none gate impl arc opening.

---

## Class 3 findings (severe — phase re-opening)

*None surfaced.*

## Class 2 findings (moderate — current-phase revision)

*None surfaced.*

## Class 1 findings (minor — documentation drift)

### F1-01 — Spec §14.13.3 stage-4 sub-ordering self-contradiction

- **Location:** `Spec_Harness_Runtime_v1.md` §14.13.3 line 2554 (ordering enumeration) vs §"Adjacent defects surfaced" item (v) at line 39 (sub-ordering disclaimer)
- **Defect:** §14.13.3 prose enumerates an explicit four-position total order — *"Ordering within stage 4: `tracer_provider` → `audit_writer` → `cost_chain` → `collector_daemon` → `materialize_validator_framework_stage`"* — while the same revision's change-note adjacent observation (v) explicitly disclaims *"Stage-4 ordering within OD bucket not pinned at sub-second granularity. §14.13.3 specifies stage 4 placement but does not pin sub-ordering within stage 4 (`tracer_provider` + `audit_writer` + `cost_chain` + `collector_daemon` are sibling stage-4 bindings)."* These two readings are mutually inconsistent. Two valid interpretations: (a) §14.13.3 enumerates strict total order — implementer must reorder existing `stage_4_od.py` (currently `tracer → collector_daemon → cost_chain → audit_writer` per the empirical bootstrap module) to match the spec; (b) §14.13.3 enumerates partial order ("validator framework as the final stage-4 binding" — comes after all four, intermediate order unconstrained). Plan U-RT-84 AC #4 safely uses partial-order phrasing ("factory invocation runs AFTER `tracer_provider` + `audit_writer` + `cost_chain` + `collector_daemon`") and is unambiguous; the defect lives at the spec.
- **Discriminator that classifies as Class 1:** (a/b/c all miss for severity escalation — implementer-discretion safety net at plan AC #4 covers the ambiguity; impl arc can proceed without spec revision). Spec text drift only.
- **Evidence:** spec line 2554 enumeration (total-order form); spec line 39 change-note disclaimer (no-sub-ordering); HEAD `harness-runtime/src/harness_runtime/bootstrap/stage_4_od.py` lines 51, 62, 75, 79 show actual order `tracer → collector_daemon → cost_chain → audit_writer` (audit_writer is empirically LAST at stage 4 at HEAD).
- **Anti-fabrication attack engaged:** A2 silent scope narrowing (spec text appears to enumerate one ordering scope while change-note disclaims it).
- **Axis-domain attack engaged:** OD-axis (lifecycle ordering of OD-bucket primitives).
- **Resolution path:** Spec inline clarification at §14.13.3 — either explicit "partial order: validator_framework after all four; intermediate order unconstrained at v1.18" OR strike of the four-position total-order enumeration. No upstream-artifact revision required. Resolves within current-phase artifact at the next spec touch.

### F1-02 — Plan U-RT-83 AC #4 mis-attaches "Pydantic v2 frozen-model validation" to dataclass shape

- **Location:** `Implementation_Plan_Harness_Runtime_v2_17.md` U-RT-83 AC #4 (line 68)
- **Defect:** AC #4 reads *"`RuntimeConfig(validator_framework_config=None)` constructs successfully + `RuntimeConfig(validator_framework_config=ValidatorFrameworkConfig.default())` constructs successfully. Both shapes pass Pydantic v2 frozen-model validation."* The phrase "Both shapes pass Pydantic v2 frozen-model validation" attaches Pydantic validation to the `ValidatorFrameworkConfig` shape itself; empirically `ValidatorFrameworkConfig` is `@dataclass(frozen=True)` per spec §14.13.1 line 2469, NOT a Pydantic v2 BaseModel. The validation discipline applies to the outer `RuntimeConfig` (which IS Pydantic v2), not to the inner sub-model. Plain reading is recoverable ("the RuntimeConfig construction in both shapes passes its Pydantic validation"), but literal reading is incorrect.
- **Discriminator that classifies as Class 1:** (a) miss — implementer can verify the intended check (RuntimeConfig construction) without ambiguity at impl arc; the AC's testable observable is unambiguous even if the explanatory phrase is mis-attached. Pure documentation drift.
- **Evidence:** plan line 68 (AC #4 text); spec line 2469 (`@dataclass(frozen=True)` decorator on ValidatorFrameworkConfig); HEAD `harness-runtime/src/harness_runtime/lifecycle/memory_tool_types.py:92-93` (parallel `MemoryToolBackendConfig` precedent is also `@dataclass(frozen=True)`, confirming the chosen decorator is correct).
- **Anti-fabrication attack engaged:** A1 silent grounding collapse (the validation-discipline cite attaches to wrong target).
- **Axis-domain attack engaged:** none specifically; type-discipline cross-cutting.
- **Resolution path:** AC #4 reword to disambiguate which model carries Pydantic validation — e.g., "Both shapes pass `RuntimeConfig` Pydantic v2 frozen-model validation; `ValidatorFrameworkConfig.default()` constructs without raising per dataclass `frozen=True` discipline." Inline plan fix at next plan touch.

### F1-03 — Plan U-RT-83 module-organization "parallel to §14.12 precedent" mismatch with empirical layout

- **Location:** `Implementation_Plan_Harness_Runtime_v2_17.md` U-RT-83 Files section (line 56) + change-note adjacent observation (d) line 30
- **Defect:** Plan recommends new top-level module `harness-runtime/src/harness_runtime/validator_framework_config.py` (line 56) and characterizes the choice as *"parallel to `harness-runtime/src/harness_runtime/lifecycle/memory_tool_*.py` module-organization pattern for runtime-internal sub-models per spec §14.12"*. Empirical inventory shows the cited §14.12 precedent `MemoryToolBackendConfig` lives at `harness-runtime/src/harness_runtime/lifecycle/memory_tool_types.py:93` — under a `lifecycle/` subdirectory, in a types-aggregation file. The plan's recommended path (top-level `validator_framework_config.py`) is NOT parallel to that precedent at file-organization granularity. AC #3 (line 67) has an implementer-discretion safety net — *"or equivalent runtime-package-internal module organization at implementer discretion"* — so the impl arc can resolve consistent with §14.12 without plan revision; the defect is the claim-vs-precedent drift, not a blocker.
- **Discriminator that classifies as Class 1:** (a) miss — implementer-discretion clause at AC #3 absorbs the resolution. Drift-only between recommended-path text and cited precedent.
- **Evidence:** plan line 56 (recommended path); plan line 30 (parallel-to claim); HEAD `harness-runtime/src/harness_runtime/lifecycle/memory_tool_types.py:93` (actual §14.12 precedent file path).
- **Anti-fabrication attack engaged:** A1 silent grounding collapse (the "parallel" precedent doesn't match the empirical layout at file path).
- **Axis-domain attack engaged:** none; module-organization cross-cutting.
- **Resolution path:** Plan inline fix at U-RT-83 Files section — either (a) update recommended path to `harness-runtime/src/harness_runtime/lifecycle/validator_framework_types.py` for true §14.12 parallel, OR (b) reword the "parallel to" claim to "in `harness-runtime` package per §14.12 carrier-home precedent; implementer selects file organization at impl arc". No upstream-artifact revision required.

---

## Findings considered and rejected (transparency)

The following attacks were applied against the spec + plan and did NOT surface findings — the artifacts handle them cleanly:

1. **§14.8.2 deferrals preservation verbatim (Reading A critical scope discipline).** Empirically verified via `git diff 1c55138..1707867 -- design-substrate/Spec_Harness_Runtime_v1.md`: 198 insertions + 1 deletion (the deletion is the v1.17 → v1.18 version-header bump only). Lines 1827 (step 3 VALIDATOR_ESCALATION foreclosure), 1831 (step 4c `_hitl_required` deferral), 1832 (step 4d palette restriction deferral) all unchanged. Spec §14.13.5 invariant 4 + §14.13.7 explicit pointers + change-note (i)/(ii)/(iii) adjacent observations triple-confirm preservation. ✓

2. **A4 fabricated citations — CP-axis closure commits exist.** `git cat-file -e` verified all 4 commits cited at plan §2 cluster-boundary edges: `16cf6d7` (U-CP-58 ValidatorFailClass), `cdf83b1` (U-CP-59 Protocol envelopes), `5ca86aa` (U-CP-60 ConcreteValidatorFramework), `9b009d3` (U-CP-61 workflow_driver:668 hook). ✓

3. **A4 fabricated citations — CP-axis file path + line number resolution.** Empirically verified: `harness-cp/src/harness_cp/validator_framework.py:130` (ConcreteValidatorFramework), `:303` (SyncValidatorFrameworkLike), `:323` (SyncValidatorFrameworkFacade), `:361` (materialize_sync_validator_framework_facade); `harness-cp/src/harness_cp/validator_framework_types.py:69` (ValidatorFailClass), `:192` (Validator Protocol), `:211` (ValidatorFramework Protocol); `harness-cp/src/harness_cp/workflow_driver.py:668` (`if ctx.validator_framework is not None:`); `harness-runtime/src/harness_runtime/types.py:1157` (`validator_framework: object | None = None` v1.17-era untyped carrier). ✓

4. **Carrier-home decision coherence.** Spec + plan place `ValidatorFrameworkConfig` in `harness-runtime` (parallel to `MemoryToolBackendConfig`) NOT in `harness-core` (where `SandboxDecisionPolicy` lives). Empirically: `MemoryToolBackendConfig` at `harness-runtime/src/harness_runtime/lifecycle/memory_tool_types.py:93`; `SandboxDecisionPolicy` at `harness-core/src/harness_core/sandbox_decision_policy.py:30`. Plan change-note adjacent observation (d) rationale (RuntimeConfig sub-models paired with stage factories live in runtime; cross-axis shared types live in core) is consistent with empirical layout. ✓

5. **Cluster-boundary edge enumeration completeness.** Plan §2 enumerates 7 new cluster-boundary edges (U-RT-84 × 3 to U-CP-58/59/60; U-RT-85 × 4 to U-CP-58/59/60/61). Each target is an already-landed cluster 10-CP-A closure commit with empirically verified SHA. No transitive cycle path possible (all targets are landed predecessors, not in-flight). ✓

6. **Within-cluster DAG acyclicity.** Plan §2 enumerates 3 within-cluster edges forming linear chain U-RT-83 → U-RT-84 → U-RT-85. Linear chain trivially acyclic. Kahn-verified at coherence pass §4. ✓

7. **AC verifiability under U-RT-84 option (i)/(ii) shapes per `[[halt-route-split-AC-pattern]]`.** AC #3 explicitly enumerates option (i) NotImplementedError on opt-in branch (deferring construction body) vs option (ii) minimal construction body (returning Protocol-satisfying instance). Both shapes have testable observables: option (i) verifiable via `pytest.raises(NotImplementedError)` on opt-in branch; option (ii) verifiable via Protocol-conformance check. U-RT-85 AC #5 contingency text ("option (i) at U-RT-84 leaves U-RT-85 needing its own minimal construction shim") covers the e2e gate under both options. ✓

8. **U-RT-85 mechanism α default sufficiency for AC #4 minimum.** Plan U-RT-85 §"Test-substrate mechanism" enumerates α (single PASS-returning fixture, recommended default) / β (PASS + PERMANENT_FAIL) / γ (env-var-gated). AC #4 requires "at minimum the `PASS` outcome is exercised; other outcomes implementer-discretion at mechanism-β selection; not required at mechanism-α minimum AC-satisfying shape" — α is sufficient. Mechanism enumeration honors FM-2 implementer-discretion per `[[advisor-before-substantive-work-for-cross-axis-blockers]]` recommendation. ✓

9. **ZERO cross-axis cascade claim.** Spec §14.13.6 + plan §2 both assert no new CXA edge introduction. Workspace `CLAUDE.md` §2.3 shows CP spec at v1.11 + OD spec at v1.9 + CXA at v2.8 (all unchanged from pre-fork). Runtime row at v1.17 — would bump to v1.18 + plan row to v2.17 post-clearance via downstream absorption owe (a) per change-note. ✓

10. **A8 framing contamination — Reading A scope discipline preserved.** Spec change-note §"Adjacent defects surfaced" items (i)/(ii)/(iii) explicitly preserve §14.8.2 deferrals; §14.13.5 invariant 4 doubles down ("No validator-composer arc resolutions at v1.18"); §14.13.7 contains 5 deferral-pointer entries with EXPLICIT POINTER markers + verbatim preservation language. No overcommitment. ✓

11. **A1 silent grounding — every citation resolves.** Every spec + plan citation traces to a design-substrate file, a `.harness/` fork doc, or a commit SHA verified above. No "general knowledge" or "best practice" citations. ✓

12. **FM-D axis-domain mechanical application.** Every axis-domain attack applied (OD lifecycle stage placement, CP Protocol-conformance, runtime fail-class taxonomy) was checked against artifact content — findings F1-01 + F1-02 + F1-03 each cite the artifact's content directly, not generic domain principles. ✓

---

## Disposition

**CLEARED with inline documentation fixes (Class 1 only).**

Per `Project_Workflow_v1_8.md` §4.1.1 (Class 1 disposition = clearance with inline fixes), this checkpoint clears. The three Class 1 findings are documentation drift surfaceable at the next spec/plan touch (e.g., the downstream absorption arc that bumps workspace `CLAUDE.md` §2.3 runtime row v1.17 → v1.18 + §2.4 runtime plan row v2.16 → v2.17). No Class 2 finding requiring current-phase revision; no Class 3 finding requiring phase re-opening.

**Reading A scope discipline:** verified preserved verbatim. §14.8.2 step 3 VALIDATOR_ESCALATION foreclosure + step 4c full 4-axis `_hitl_required` deferral + step 4d cross-trust-boundary palette restriction deferral all bit-exact unchanged (empirical `git diff` over 198 insertions / 1 deletion).

**Impl arc readiness:** L9-decies cluster ready to open per `phase-7-implementation` skill at U-RT-83 → U-RT-84 → U-RT-85 topological sort. U-RT-84 implementer selects option (i)/(ii) at AC #3; U-RT-85 implementer selects mechanism α/β/γ at FM-2 discretion (recommended default α).

**Cross-artifact pattern check:** No systemic finding shape recurring across both artifacts. Findings are surgical and per-artifact (F1-01 spec; F1-02 + F1-03 plan). No workflow §7 session-prompt-template revision recommendation.

**Phase-7 fork class disambiguation (per CLAUDE.md title-section discipline):** No §2.7.6 fork triggered by these findings — all three Class 1 (§4.1) findings resolve inline at the current artifact layer without halting Phase 7 execution.

---

*Reviewer self-audit per skill §7:*
- Severity distribution sanity: 0/0/3 — bottom-heavy, plausible for a surgical Reading A scope ✓
- Evidence on every finding: ✓ (line numbers + empirical file/commit references on all 3)
- Discriminator on every finding: ✓ (each finding names the discriminator + why it doesn't escalate)
- Author-mode drift check: ✓ (resolution paths describe shape, not replacement text)
- Context-bleed check: ✓ (no candidate-definition offering; no general-knowledge claims)
- Decision-vocabulary application: all 3 findings are *decided* (text supports single reading)
- Rejected-findings completeness: 12 substantive checks itemized ✓
- Cross-artifact pattern surfacing: N/A (no systemic recurrence) ✓
- Disposition-evidence match: Class 1 only → clearance with inline fixes per §4.1.1 ✓
