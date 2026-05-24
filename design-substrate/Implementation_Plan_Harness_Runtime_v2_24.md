# Implementation Plan — Harness Runtime v2.24

## Change-note (v2.23 → v2.24)

**Scope of revision.** Single-cluster amendment at L9-terdecies (U-RT-93/94/95) absorbing runtime spec v1.24 → v1.25 (this session prior commit, co-published) two amendments: (D9) §14.8.8.1 step 0 precondition `if ctx.pause_resume_protocol is None: fall through to step 4f (treat as SYNC_BLOCKING)` + (D10) NEW §14.8.8.9 `ResumeContextHolder` sidecar carrier + §4 C-RT-04 HarnessContext field row `resume_context_holder: ResumeContextHolder`. Both amendments are pre-implementation advisor-caught architectural gap-fixes (operator-ratified 2026-05-24 via AskUserQuestion D9 + D10). ZERO new units; ZERO new cluster; ZERO DAG topology change.

**Source of fix.** Runtime spec v1.24 → v1.25 publication (this session prior commit) per advisor-caught pre-impl gaps + operator AskUserQuestion D9 (v1.25 spec amendment now) + D10 (ResumeContextHolder sidecar). The v2.23 L9-terdecies cluster body authored at prior commit `fbf44d6` is amended in-place via canonical-reading amendments at U-RT-93 + U-RT-94 + U-RT-95 ACs (no unit re-decomposition; cluster topology + dependency edges preserved verbatim).

**Authority basis for fix direction.** Both v1.25 amendments are fidelity-preserving — D9 makes step 1 mechanically consistent with v1.24 §14.8.8.7 invariant 5 (was claimed-only; now mechanically enforced); D10 closes the v1.24 §14.8.8.8 implementer-discretion deferral with the operator-ratified sidecar option. v2.24 absorbs the spec amendments at the existing L9-terdecies cluster body without adding new units — the gap-fix lands at U-RT-94 ACs (composer body + sidecar carrier integration); U-RT-93 ACs (helper + signal class) are preserved verbatim; U-RT-95 ACs (driver catch + e2e test) gain ONE new AC covering the precondition-arm test case.

**Amendments.**

| Site | Amendment shape |
|---|---|
| **U-RT-94 AC #1 (step 4-bis branch)** | Amend AC #1 to add the §14.8.8.1 step 0 precondition guard BEFORE the synchrony-class branch evaluation. New AC #1 reads: "§14.8.2 step 4-bis branch fires AFTER existing step 4e and BEFORE existing step 4f. **Step 4-bis precondition (v1.25 §14.8.8.1 step 0): `if ctx.pause_resume_protocol is None: fall through to step 4f (treat as SYNC_BLOCKING regardless of cell.synchrony_class value); NO webhook delivery fires; NO flag-set fires; NO signal raise.**" Subsequent branch logic (synchrony-class evaluation when pause_resume_protocol is bound) preserved from v2.23. Unit test verifies precondition-arm + 3 synchrony-class outcomes when precondition passes. |
| **U-RT-94 AC #5/#6 (composer body steps 4-5)** | Preserve v2.23 AC #5 + #6 verbatim. The v1.25 step 0 precondition is the gate for reaching step 1; once past the precondition, the v1.24 6-step body (now renumbered 1-6 OR 2-7 implementer-discretion per v1.25 change-note) fires unchanged. |
| **U-RT-94 NEW AC #9 (ResumeContextHolder sidecar landing)** | NEW AC covering the v1.25 §14.8.8.9 sidecar carrier landing: "ResumeContextHolder Pydantic v2 BaseModel lands at `harness-runtime/src/harness_runtime/types.py` (or sibling carrier file per impl-arc discretion). Frozen-outer (`model_config = ConfigDict(frozen=True)`) + single PrivateAttr field `_current_context: ResumeContext | None = PrivateAttr(default=None)` + public methods `set(resume_context: ResumeContext) -> None` + `consume_and_clear() -> ResumeContext | None` (atomic read-and-clear enforcing one-shot semantic per v1.25 §14.8.8.9.1). HarnessContext field `resume_context_holder: ResumeContextHolder` added per v1.25 §4 row; non-None; initialized at stage 5 LOOP_INIT to empty holder (`ResumeContextHolder()` default). Unit tests verify (a) holder.set() then consume_and_clear() returns the set value (b) double consume_and_clear() second call returns None (one-shot enforcement) (c) double set() between consume_and_clear() calls — last-write-wins per v1.25 change-note adjacent defect (ii). Files-column EXTEND: `harness-runtime/src/harness_runtime/types.py` (ADD ResumeContextHolder BaseModel + HarnessContext.resume_context_holder field; stage-5 initialization at bootstrap stage handler)." |
| **U-RT-94 NEW AC #10 (resume-side consume integration)** | NEW AC covering the v1.25 §14.8.8.9.3 composer-side consumption pattern: "Runtime composer at resumed-step gate-evaluation reads `holder_state = ctx.resume_context_holder.consume_and_clear()` (atomic). IF `holder_state is not None and holder_state.hitl_response is not None` → `gate_result = holder_state.hitl_response`; ELSE fall through to normal gate-fire path (sync at step 4f OR durable-async re-fire pending v1.25 step 0 precondition). The v2.23 AC #7 `ctx.resume_context = None` direct-mutation framing is SUPERSEDED at v2.24 by the `consume_and_clear()` atomic-method call per v1.25 §14.8.8.9.3 — the frozen HarnessContext precludes direct mutation; the sidecar mechanism is the canonical resolution." |
| **U-RT-95 NEW AC #7 (precondition-arm e2e test)** | NEW AC covering the v1.25 §14.8.8.1 step 0 precondition test path: "e2e test path (v) operator-binds-webhook-but-not-pause-resume-protocol: operator supplies `RuntimeConfig` with `webhook_delivery_config` bound (non-empty) BUT `pause_resume_protocol_config = None` (operator opt-out per v1.21 §14.14 default) + StepEffectiveBinding with cell == DURABLE_ASYNC → composer hits v1.25 §14.8.8.1 step 0 precondition (`ctx.pause_resume_protocol is None`) → falls through to step 4f (sync AskUserQuestion path) → NO webhook delivery fires + NO flag-set + NO signal raise. Test verifies precondition-arm preserves sync-blocking semantics + verifies absence of orphan-response bug per v1.25 D9 advisor-caught gap fix." |
| **U-RT-93 ACs (preserved verbatim)** | v2.23 ACs #1-#4 preserved verbatim. The helper + exception class authoring at U-RT-93 is unchanged by v1.25 amendments. |

**Adjacent harmonization sites.** None — the amendments are surgical AC additions/refinements at U-RT-94 + one new AC at U-RT-95. U-RT-93 ACs preserved verbatim. Cluster DAG topology preserved verbatim (U-RT-93 → U-RT-94 → U-RT-95 linear chain). Cluster-boundary edges preserved verbatim (5 to already-landed substrate + 1 within-axis-cross-package to U-CP-64). Coverage matrix preserved verbatim (the v1.25 amendments map to existing U-RT-94 AC enumeration + U-RT-95 e2e expansion).

**Sections preserved verbatim from v2.23.** All v2.23 substantive content + L9-terdecies cluster framing preserved unchanged outside the listed AC amendment sites. All v2.22 + v2.21 + ... + v2 chain preserved.

**Status posture.** Proposed (v2.23) → **Proposed (v2.24)**. v2.24 is a single-cluster AC-refinement amendment absorbing upstream v1.25 spec amendment. NO new units; NO new cluster; NO DAG topology change; NO acceptance criterion removal at any preserved unit. Net ACs at L9-terdecies: +3 (U-RT-94 +2 new ACs #9 #10; U-RT-95 +1 new AC #7). Net Files-column changes at U-RT-94: +1 (`types.py` ResumeContextHolder + HarnessContext field). Net contract-at-runtime-spec-side: +1 carrier (`ResumeContextHolder`) absorbed via v1.25 §14.8.8.9 (NOT plan-side).

**Downstream absorption owed (post-v2.24).**

(a) Workspace `CLAUDE.md` §2.4 runtime plan row version bump (v2.23 → v2.24); co-published this arc.

(b) `harness-runtime` impl at U-RT-93/94/95 landing arcs absorb the v2.24 ACs per `phase-7-implementation` skill — U-RT-93 preserved verbatim; U-RT-94 lands additional ResumeContextHolder carrier + HarnessContext field + composer-body precondition guard + consume-and-clear integration; U-RT-95 adds path (v) precondition-arm test case.

(c) OD spec / OD plan / OD impl / CP spec / CP plan / CXA / ADR: ZERO cascade.

**Adjacent defects surfaced (NOT patched per FM-2 no-extension discipline).**

(i) **U-RT-94 AC count drift.** v2.23 authored ~8 ACs at U-RT-94; v2.24 adds 2 more (AC #9 + #10) bringing total to ~10 ACs. Implementer at U-RT-94 landing may consolidate ACs (e.g., merge #9 + #10 into a single composite AC covering both the carrier landing and the integration) per implementer-discretion at phase-7-implementation skill. v2.24 enumerates separately for clarity; consolidation at impl-arc landing is implementer-discretion.

(ii) **Sidecar holder lifecycle vs WorkflowEnvelope lifecycle.** The `ResumeContextHolder` is bound at HarnessContext per v1.25 §4 row + initialized at stage 5; its lifecycle is the HarnessContext lifecycle (one workflow execution per ctx). Across multiple `execute_workflow` calls in a single bootstrap cycle, the holder is re-initialized per HarnessContext instance. The semantic is correct (no cross-workflow leak) but worth surfacing here for impl-arc reviewer attention. NOT patched per FM-2.

---

## §1 — U-RT-93 plan-body preservation (v2.24)

The U-RT-93 declaration at v2.23 §1 is preserved verbatim at v2.24. No v1.25 amendment affects U-RT-93 — the helper + exception class authoring is structurally orthogonal to the step 0 precondition (which guards entry to step 1; the helper signature + exception class are unchanged) and orthogonal to the ResumeContextHolder sidecar (which is at U-RT-94 Files-column EXTEND).

---

## §2 — U-RT-94 plan-body amendment (v2.24)

The U-RT-94 declaration at v2.23 §2 is amended at v2.24 as follows. v2.23 ACs #1-#8 preserved verbatim except for AC #1 (step 0 precondition addition per Site amendment table) + AC #7 (resume-side consume framing superseded by sidecar mechanism per Site amendment table). NEW AC #9 + AC #10 added per v1.25 absorption.

### U-RT-94 — HITL gate composer body amend (v2.24 amendment — step 0 precondition + ResumeContextHolder sidecar landing)

- **Implements (v2.24):** Runtime spec v1.25 §14.8.2 step 4-bis insertion + v1.25 §14.8.8.1 step 0 precondition (NEW at v1.25) + full §14.8.8.1 6-step durable-async composer body + v1.25 §14.8.8.5 resume-side one-shot delivery via `ResumeContextHolder.consume_and_clear()` + **v1.25 §14.8.8.9 NEW ResumeContextHolder sidecar carrier landing**
- **Files (v2.24 amendment):** `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py` (preserved from v2.23 — amend `RuntimeHITLGateComposer.dispatch(...)` body + add §14.8.8 durable-async branch + resume-side consume-and-clear logic using sidecar) + **NEW (v2.24): `harness-runtime/src/harness_runtime/types.py` (EXTEND — ADD `ResumeContextHolder` Pydantic v2 BaseModel + ADD `HarnessContext.resume_context_holder` field; stage-5 initialization at bootstrap stage handler)**
- **Signatures (v2.24):** No new top-level signature for composer (in-place amendment of existing dispatch body). NEW class `ResumeContextHolder(BaseModel)` with `model_config = ConfigDict(frozen=True)` + `_current_context: ResumeContext | None = PrivateAttr(default=None)` + `set(resume_context: ResumeContext) -> None` + `consume_and_clear() -> ResumeContext | None`.
- **Depends on:** [U-RT-93] (within-cluster L0 → L1) — preserved from v2.23; within-axis-cross-package: U-CP-64 at CP plan v2.21 (`ResumeContext` carrier consumed by `ResumeContextHolder` PrivateAttr type annotation).
- **ACs (v2.24 amendment):**
  1. **AMENDED at v2.24:** §14.8.2 step 4-bis branch fires AFTER existing step 4e and BEFORE existing step 4f. **Step 4-bis precondition (v1.25 §14.8.8.1 step 0): `if ctx.pause_resume_protocol is None: fall through to step 4f (treat as SYNC_BLOCKING regardless of cell.synchrony_class value); NO webhook delivery fires; NO flag-set fires; NO signal raise.**" Branch evaluation logic (synchrony-class evaluation when pause_resume_protocol is bound) preserved from v2.23 — `synchrony = _evaluate_cell_synchrony_tolerant(binding)` then dispatch on None/SYNC_BLOCKING/DURABLE_ASYNC. Unit test verifies precondition-arm + 3 synchrony-class outcomes when precondition passes (4 total test cases).
  2-6. **Preserved verbatim from v2.23.** §14.8.8.1 steps 1-6 composer body (HITLEscalationBrief composition + idempotency key + deliver_webhook + handle exhausted + flag-set + signal-raise) preserved unchanged at v2.24 ACs #2-#6.
  7. **AMENDED at v2.24 — superseded by sidecar mechanism:** §14.8.8.5 resume-side one-shot delivery via `ResumeContextHolder.consume_and_clear()` atomic method. Runtime composer at resumed-step gate-evaluation reads `holder_state = ctx.resume_context_holder.consume_and_clear()`. IF `holder_state is not None and holder_state.hitl_response is not None` → `gate_result = holder_state.hitl_response`; ELSE fall through to normal gate-fire path. The v2.23 AC #7 `ctx.resume_context = None` direct-mutation framing is SUPERSEDED at v2.24 by the `consume_and_clear()` atomic-method call per v1.25 §14.8.8.9.3 — the frozen HarnessContext precludes direct mutation; the sidecar mechanism is the canonical resolution. Unit test verifies atomic consume-and-clear semantic.
  8. **AMENDED at v2.24 — superseded by sidecar:** `ctx.resume_context` direct-binding-site framing at v2.23 AC #8 SUPERSEDED — the v1.25 §14.8.8.9 sidecar IS the binding-site canonical decision. Implementer-discretion at v2.23 AC #8 is CLOSED at v2.24 per D10 operator ratification. NO further binding-site decision owed at impl-arc.
  9. **NEW at v2.24.** `ResumeContextHolder` Pydantic v2 BaseModel lands at `harness-runtime/src/harness_runtime/types.py` per v1.25 §14.8.8.9.1 carrier definition. Frozen-outer (`model_config = ConfigDict(frozen=True)`) + single PrivateAttr field `_current_context: ResumeContext | None = PrivateAttr(default=None)` + public methods `set(resume_context: ResumeContext) -> None` + `consume_and_clear() -> ResumeContext | None` (atomic read-and-clear enforcing §14.8.8.7 invariant 3 one-shot semantic). HarnessContext field `resume_context_holder: ResumeContextHolder` (non-None) added per v1.25 §4 row; initialized at stage 5 LOOP_INIT to empty holder (`ResumeContextHolder()` default). Unit tests verify (a) `holder.set(rc) → consume_and_clear() == rc`; (b) `consume_and_clear() → None` after first consume (one-shot enforcement); (c) `set(rc1); set(rc2); consume_and_clear() == rc2` (last-write-wins per v1.25 change-note adjacent defect (ii)).
  10. **NEW at v2.24.** Stage-5 LOOP_INIT bootstrap stage handler initializes `ctx.resume_context_holder = ResumeContextHolder()` (empty holder; `_current_context = None` default). Initialization is unconditional regardless of `RuntimeConfig.pause_resume_protocol_config` value — the holder is a runtime-loop carrier per v1.25 §14.8.8.9.2 binding-at-HarnessContext discussion. Unit test verifies stage-5 binding shape + holder initial-state.

**Rollback boundary (v2.24).** Revert `RuntimeHITLGateComposer.dispatch(...)` body amend + revert `types.py` ResumeContextHolder + HarnessContext field addition + revert stage-5 bootstrap initialization. U-RT-95 (within-cluster L2 dependent) loses composer-side substrate. Sync-blocking path at step 4f preserved unchanged.

---

## §3 — U-RT-95 plan-body amendment (v2.24)

The U-RT-95 declaration at v2.23 §3 is amended at v2.24 by ONE new AC #7 covering the v1.25 §14.8.8.1 step 0 precondition-arm test case. v2.23 ACs #1-#6 preserved verbatim.

### U-RT-95 — Driver catch + e2e (v2.24 amendment — NEW AC #7 precondition-arm test case)

- **Implements (v2.24):** Runtime spec v1.25 §14.8.8.4 driver-side signal handling discipline + e2e real-bootstrap pause-on-durable-cell cycle per scoping doc D7 mechanism α + **v1.25 §14.8.8.1 step 0 precondition-arm test coverage**
- **Files (v2.24 — preserved from v2.23):** `harness-cp/src/harness_cp/workflow_driver.py` (amend per-step dispatch try-block to catch `HITLPauseRequestedSignal`); `harness-runtime/tests/integration/test_u_rt_95_hitl_pause_trigger_durable_async_full_execution_path.py` (NEW e2e integration test — v2.24 adds path (v) precondition-arm coverage)
- **Depends on:** [U-RT-94] (within-cluster L1 → L2) — preserved from v2.23; cluster-boundary edges to already-landed L9-undecies + L9-quinquies + U-CP-64 preserved.
- **ACs (v2.24 amendment):**
  1-6. **Preserved verbatim from v2.23.** Driver-side catch discipline + e2e paths (i)-(iv) — durable-async pause-trigger / resume-consume-cycle / sync-blocking pass-through / webhook-exhausted failure.
  7. **NEW at v2.24.** e2e test path (v) operator-binds-webhook-but-not-pause-resume-protocol: operator supplies `RuntimeConfig` with `webhook_delivery_config` bound (non-empty config) BUT `pause_resume_protocol_config = None` (operator opt-out per v1.21 §14.14 default) + `StepEffectiveBinding` with `(persona_tier, engine_class)` matrix cell == `DURABLE_ASYNC` per C-CP-18 §18.1 → composer hits v1.25 §14.8.8.1 step 0 precondition (`ctx.pause_resume_protocol is None`) → falls through to step 4f (sync AskUserQuestion path) → NO webhook delivery fires + NO flag-set + NO `HITLPauseRequestedSignal` raise. Test verifies precondition-arm preserves sync-blocking semantics + verifies absence of orphan-response bug per v1.25 D9 advisor-caught gap fix. Test fixture: `_RecordingClient` from `test_lifecycle_webhook_delivery_composer.py` pattern (httpx.AsyncClient test-double); verify zero outbound POST attempts recorded.

**Rollback boundary (v2.24).** Revert path (v) test case + revert driver try-block amend (path-v testing depends on composer step 0 from U-RT-94). Composer-side v1.25 precondition preserved (the precondition is at composer body, NOT at driver).

---

## §4 — Coverage matrix delta (v2.24)

Coverage matrix delta at v2.24:

| Spec contract | Plan unit(s) |
|---|---|
| Runtime spec v1.25 §14.8.8.1 step 0 precondition (NEW at v1.25) | U-RT-94 AC #1 + U-RT-95 AC #7 (precondition-arm e2e) |
| Runtime spec v1.25 §14.8.8.9 ResumeContextHolder sidecar carrier (NEW at v1.25) | U-RT-94 AC #9 + AC #10 |
| Runtime spec v1.25 §4 C-RT-04 HarnessContext.resume_context_holder field (NEW at v1.25) | U-RT-94 AC #9 + AC #10 |
| Runtime spec v1.24 §14.8.x (preserved from v2.23 mapping) | preserved per v2.23 coverage table |

Total coverage matrix rows added at v2.24: +3. All coverage matrix cells populated; ZERO uncovered spec contracts.

---

## §5 — Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Harness_Runtime_v2_24.md` |
| Version | v2.24 |
| Filing event | Runtime spec v1.24 → v1.25 (D9 step 0 precondition + D10 ResumeContextHolder sidecar) absorption per operator AskUserQuestion 2026-05-24 |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_23.md` (substantive content preserved verbatim outside L9-terdecies cluster AC amendments) |
| Successor | (none — current canonical) |
| Co-published artifacts (this arc) | Workspace `CLAUDE.md` §2.4 runtime plan row bump v2.23 → v2.24; runtime spec v1.25 (this session prior commit) |
| Operator authority | AskUserQuestion 2026-05-24 D9 + D10 |
| Unit-count change | None (93 → 93 — single-cluster AC amendment) |
| Cluster-count change | None |
| DAG topology change | None (cluster-boundary + within-cluster edges preserved) |
| Coverage matrix structural change | +3 rows (v1.25 new spec contract coverage) |
| Acceptance criterion count change | +3 (U-RT-94 +2 ACs #9 #10; U-RT-95 +1 AC #7) |
| Cross-axis cascade | None new (within-axis-cross-package to U-CP-64 preserved from v2.23) |
| Skill discipline | `implementation-planner` Phase-7 revision-pass absorbing upstream runtime spec v1.25 publication into existing L9-terdecies cluster bodies; fidelity-pure AC amendment (3 NEW ACs + 2 amended ACs + 0 unit re-decomposition); NO contract addition at plan level; NO acceptance criterion removal; preservation audit PASSED |
| Date | 2026-05-24 |
