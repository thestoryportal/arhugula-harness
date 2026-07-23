# Implementation Plan: Harness Runtime — v2.54 (delta over v2.53)

*v2.54 is the Runtime plan leg of the RATIFIED **B-39 nested paused-child HITL-response-routing arc**'s **spec leg** (`.harness/class_1_fork_b39_nested_hitl_response_threading.md`, RATIFIED 2026-07-23), absorbing **Runtime spec v1.105 → v1.106** (RETIRE §14.8.8.9 `ResumeContextHolder` AS A CTX-LEVEL BINDING; NEW §14.8.8.10 CONTRACT-altitude replacement-mechanism requirements, CORRECTED same-day after out-of-family review). This delta AMENDS the EXISTING **U-RT-94** (the HITL gate composer body unit that has owned §14.8.8.5 resume-side one-shot delivery since its v2.23 authoring — AC #7/#8 specifically enumerated the `ctx.resume_context` binding-site question this retirement answers) + adds a confirmation note at **U-RT-95** (the e2e resume-consume-cycle test, whose fixture setup changes — it no longer constructs a ctx-level `ResumeContextHolder`, but the test SCENARIO and public call shape are unchanged). ZERO new units; ZERO new cluster; ZERO DAG topology change; ZERO cross-axis cascade asserted. This is the SPEC LEG's plan absorption only — impl (code + tests) is a separate follow-on arc per the B-33/B-59 precedent.*

**Status:** Proposed

---

## §0 Change-note (v2.53 → v2.54)

### §0.1 Predecessor

`Implementation_Plan_Harness_Runtime_v2_53.md` (v2.53 — the B-33 arc's Runtime plan leg; NEW U-RT-147).

### §0.2 Revision context — Runtime spec v1.106 absorption, CONTRACT-altitude correction pass

Per `Spec_Harness_Runtime_v1.md` v1.106 §14.8.8.10: the `ResumeContextHolder` sidecar (§14.8.8.9) is RETIRED as a ctx-level, run-tree-wide-shared binding. U-RT-94's original AC #7 ("resume-side one-shot delivery... `ctx.resume_context.hitl_response`") and AC #8 (the binding-site discretion enumeration) are the EXACT surfaces this retirement answers — U-RT-94 is the empirically-verified owning unit (v2.23 original authoring, `Implementation_Plan_Harness_Runtime_v2_23.md` §2, PRESERVED VERBATIM through the v2.30 Reading-H additive refactor and every version since). No Runtime surface of this arc lacks an owning unit → ZERO new units.

**Correction note (same-day, this arc).** A first draft of this delta's AC #7/#8 asserted that the composer consumes a bare `resolved_hitl_response` call parameter and that one-shot delivery is "now structural... by construction." Out-of-family review (`just codex-review-uncommitted`) plus an `Explore` grounding pass found this false: the EXISTING retry composition (`RetryBreakerFallbackDispatcher` wraps the HITL gate composer as `inner`, re-invoking `dispatch()` on every retry attempt within ONE `execute_workflow` invocation) means a bare parameter re-supplied identically on every retry attempt would incorrectly REPLAY the resolved response instead of letting the retry re-fire the gate — a real regression versus the retired holder's `consume_and_clear()`, which correctly returned `None` on a second same-cycle attempt. AC #7/#8 are rewritten below at CONTRACT altitude: what the replacement mechanism must guarantee, without prescribing its exact shape.

### §0.3 Sections revised

§0 (this change note); §1 (the U-RT-94 amendment); §2 (the U-RT-95 confirmation note). All other sections — every other `U-RT-NN` body, all dependency graphs, cross-cutting units, open items — PRESERVED VERBATIM from v2.53.

### §0.4 Scope discipline

ADDITIVE / amended-unit scope only. ZERO new atomic units; ZERO new contract IDs; ZERO new DAG edges (U-RT-94's existing within-axis-cross-package dependency on CP plan's U-CP-64 is UNCHANGED in shape — both sides bump version, U-CP-64 at CP plan v2.42, U-RT-94 here at v2.54).

---

## §1 U-RT-94 amendment — resume-side one-shot delivery: CONTRACT, not mechanism (retires the ctx-level `ResumeContextHolder` binding)

The v2.23 U-RT-94 body (PRESERVED VERBATIM through the v2.30 additive `WebhookDeliveryComposer` refactor and every version since) is amended as follows. AC #1-#6 (the durable-async composer body — synchrony-class branch, brief composition, idempotency key, webhook delivery invocation, exhausted-delivery fail path, success-path flag-set+signal-raise) are UNCHANGED. AC #7 and AC #8 are AMENDED (rewritten at this correction pass); the v2.30 additive ctor/`deliver_webhook_for_brief` rows are UNCHANGED.

- **Implements (amendment):** §14.8.8.5 resume-side one-shot delivery — AMENDED to consume a value satisfying the CONTRACT at Runtime spec v1.106 §14.8.8.10.1/§14.8.8.10.2, superseding the RETIRED §14.8.8.9 `ResumeContextHolder` ctx-level binding. §14.8.8.7 invariant 3 (one-shot delivery) — UNCHANGED IN SUBSTANCE, restated as a binding contract on the replacement mechanism per §14.8.8.10.4 (NOT a "structural by construction" claim — corrected at this pass).
- **Files (AMEND — exact disposition is impl discretion, not asserted here):** `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py` (AMEND `RuntimeHITLGateComposer.dispatch(...)` resumed-step gate-evaluation to consume a resolved value satisfying §14.8.8.10.1's three properties — per-branch-distinct, one-shot-under-retry, no new global sharing; exact parameter/attribute shape is implementation discretion, verified by execution at the impl leg) + `harness-runtime/src/harness_runtime/bootstrap/stage_5_loop_init.py` (AMEND to remove the CTX-LEVEL `ResumeContextHolder` construction/binding this unit's own v1.25-era body performed; whether a per-resume-cycle-scoped construction replaces it at a DIFFERENT site is impl discretion) + `harness-runtime/src/harness_runtime/types.py` (AMEND `HarnessContext` — REMOVE `resume_context_holder: ResumeContextHolder` field per C-RT-04 RETIRED row; this is the one unconditional removal this unit owns) + `harness-runtime/src/harness_runtime/lifecycle/resume_context_holder.py` (DISPOSITION IS IMPL DISCRETION — the impl leg may delete this module and author a new type, or repurpose it, so long as the result satisfies §14.8.8.10.1 AND is never bound at ctx-level/run-tree-wide scope again; Q1=(A)'s retirement of that BINDING is fixed, not impl discretion, per Runtime spec v1.106 §14.8.8.10.5's round-4 clarification)
- **Signatures:** No signature asserted by this unit (a prior draft asserted the composer's `dispatch(...)` gains no new top-level signature "since the binding-site shape is implementer's call" — that framing stands, but is now explicitly a non-assertion, not a settled design).
- **Depends on:** [U-RT-93] (within-cluster L0 → L1, UNCHANGED); within-axis-cross-package: **U-CP-64 at CP plan v2.42** (`ResumeContext.hitl_responses`/`hitl_response_for`, keyed by the paused child's own `run_id` per a round-2 correction — NOT `branch_path`, which was found to collide on repeated same-`child_workflow_id` dispatch — + `DriverContext.resume_context_holder` field retirement) — UPDATED from the original v2.21 pin, same edge shape. **NOTE:** the propagation-mechanism wiring itself (how a resolved value reaches this unit's composer, including for nested children) is NOT yet assigned to a specific set of units on either axis — see CP plan v2.42 §5's deferred-scope row, mirrored here.
- **ACs (preserved verbatim #1-#6 from v2.23 through the v2.30 additive rows; AC #7/#8 REWRITTEN at this correction pass; v2.30's additive ctor/brief-surface ACs preserved verbatim):**
  1-6. (preserved verbatim — durable-async composer body per §14.8.8.1)
  7. **REWRITTEN at this correction pass (was: "one-shot delivery is now structural — the value is a call-scoped parameter... no explicit clear step").** At resumed-step gate-evaluation, the composer consumes a resolved `HITLResult | None` value satisfying Runtime spec v1.106 §14.8.8.10.1: (a) if present and this is the FIRST dispatch of this resume cycle → `gate_result = <the value>`; (b) if this is a RETRY attempt within the SAME resume cycle (the retry loop re-invoking `dispatch()` for the same step) → the mechanism MUST NOT re-supply the already-consumed value; the gate falls through to the normal fire path. Unit test verifies BOTH: first-attempt consumption succeeds, AND a simulated same-cycle retry does NOT receive the value a second time (this second assertion is NEW at this correction pass — a prior draft's test only covered the first-attempt case, the exact gap the retry-replay defect would have slipped through). Mutation probe: reverting to unconditionally re-supplying the same resolved value on every dispatch attempt (the falsified "bare parameter" design) causes the retry-replay test to FAIL, proving the fix is load-bearing.
  8. **REWRITTEN at this correction pass (was: an implementer-discretion menu naming a "new composer `dispatch(...)` parameter" or "per-step-scoped context object" as the only remaining choices, framed as settled).** The `ResumeContextHolder` sidecar's CTX-LEVEL, RUN-TREE-WIDE-SHARED binding is RETIRED — it is no longer a valid implementer choice at that scope. Implementation MUST satisfy, exactly per Runtime spec v1.106 §14.8.8.10.1: (i) per-branch-distinct delivery; (ii) one-shot-per-resume-cycle preserved under retry (AC #7 above); (iii) no new global/run-tree-wide sharing. The exact binding-site mechanism — including whether it is a new composer parameter, a per-step-scoped context object, a freshly-scoped instance of a NEW or repurposed type, or something else — is implementer's call, verified by execution against the REAL call graph (§1's Files note above) at the impl leg, PROVIDED it is never bound at ctx-level/run-tree-wide scope (Q1=(A) is fixed, not impl discretion — spec §14.8.8.10.5's round-4 clarification). This AC does not prescribe which.

**Rollback boundary (preserved verbatim from v2.23; extended at v2.54).** Revert the composer body amend + revert the `stage_5_loop_init.py` ctx-level construction/binding removal + revert `HarnessContext.resume_context_holder` field removal (restore the field). U-RT-95 (within-cluster L2 dependent) loses the substrate; its e2e test would need to revert to asserting against the (restored) ctx-level holder.

---

## §2 U-RT-95 confirmation note — e2e resume-consume-cycle fixture-setup change

The v2.23 U-RT-95 body (PRESERVED VERBATIM) requires NO signature/Files/Depends-on change. AC #3 (the e2e resume-consume-cycle path) is CONFIRMED to still exercise the IDENTICAL operator-facing call shape — `attempt_resume(snapshot, material_diff_policy=STRICT, resume_context=ResumeContext(hitl_response=HITLResult(...)))` — unchanged at the public `attempt_resume`/`api.resume()` surface (CP spec v1.106 §1's contract does not touch `attempt_resume`'s own signature). What changes is INTERNAL to the test fixture: any setup that referenced a ctx-level `ResumeContextHolder` directly is updated to whatever substrate U-RT-94's impl leg lands (§1 above) — the exact fixture shape is therefore deferred alongside U-RT-94's own deferred wiring, NOT asserted here. No NEW acceptance criterion is added at U-RT-95; this remains a confirmation-and-fixture-update note, not a scope change. **Additionally owed at the impl leg (NEW at this correction pass):** a same-cycle-retry e2e scenario (a resumed step whose first dispatch attempt fails transiently and retries within the SAME resume cycle) exercising U-RT-94 AC #7's retry-replay guard end-to-end, not just at the composer's own unit-test boundary.

---

## §3 — Coverage matrix delta

| Spec contract | Plan unit(s) |
|---|---|
| Runtime spec v1.106 §14.8.8.10.1 (contract — retires §14.8.8.9 as a ctx-level binding) | U-RT-94 |
| Runtime spec v1.106 §14.8.8.10.2 (resumed-step gate-evaluation consumption, supersedes §14.8.8.5) | U-RT-94 |
| Runtime spec v1.106 §14.8.8.10.3 (composition with existing surfaces, supersedes §14.8.8.6 holder-reference) | U-RT-94 (doc-level; no new test — spans/audit/fail-classes unchanged in shape) |
| Runtime spec v1.106 §14.8.8.10.4 (invariant 3 — contract restated, NOT "now structural") | U-RT-94 |
| Runtime spec v1.106 §14.8.8.10.5 (binding-site + entry-point + nested-child wiring — ALL impl discretion) | **DEFERRED — no unit owned at this spec leg beyond U-RT-94's ctx-field removal.** Mirrors CP plan v2.42 §5's deferred-scope row; the impl leg's scope-discovery pass determines final unit assignment across both axes. |
| Runtime spec v1.106 C-RT-04 `resume_context_holder` row RETIRED (ctx-level binding only) | U-RT-94 |
| e2e fixture-setup confirmation + retry-replay e2e (NEW) | U-RT-95 |

DAG topology preserved verbatim from v2.53 — ZERO new edges, ZERO new units.

---

## §4 — Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Harness_Runtime_v2_54.md` |
| Version | v2.54 |
| Filing event | B-39 spec leg plan absorption; CONTRACT-altitude correction pass same-day after out-of-family review + empirical re-grounding falsified the AC #7/#8 mechanism premise (round 1); a round-2 out-of-family pass separately found the CP-owned `hitl_responses` key shape collides on repeated same-`child_workflow_id` dispatch — CP-owned fix, this file's own Depends-on note updated to match |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_53.md` |
| Operator authority | Fork ratification 2026-07-23 (Q1/Q2 original); `AskUserQuestion` 2026-07-23 (Q2 carrier-shape reconcile, CP-side) |
| Co-published artifacts (this arc) | `Spec_Harness_Runtime_v1.md` v1.106; `Spec_Control_Plane_v1_106.md`; `Implementation_Plan_Control_Plane_v2_42.md`; clearance markers for both specs; workspace `CLAUDE.md` + `harness-cp/CLAUDE.md` pointer bumps |
| Unit-count change | None — single amended-unit-body amendment (U-RT-94) + one confirmation note (U-RT-95) |
| Cluster-count change | None |
| DAG topology change | None |
| Cross-axis cascade | None asserted by this delta beyond the pre-existing U-RT-94 → U-CP-64 edge (unchanged shape); the propagation-mechanism wiring's eventual cross-axis footprint is impl-leg scope-discovery work (§3 deferred row) |
| Impl leg | NOT bundled — code + tests land as a separate follow-on arc per the B-33/B-59 precedent; the impl leg additionally owes the scope-discovery pass §3 defers, plus the by-execution call-graph verification the spec's §14.8.8.10.5 deliberately declined to assert |
| Skill discipline | `implementation-planner` Phase-7 revision-pass absorbing upstream Runtime spec v1.106 into one existing unit body + one confirmation note; fidelity-pure amendment-only pass; NO contract addition beyond the spec; NO unit re-decomposition; NO DAG topology change; NO assertion of unverified wiring (corrected from a first draft that did) |
| Date | 2026-07-23 |
