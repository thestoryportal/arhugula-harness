# Class 1 Tension — U-RT-44 in-flight step drain unmaterializable until CP workflow loop lands

**Status:** ✅ **FULLY CLOSED 2026-05-20.** Lane 6 runtime un-strike landed U-RT-44 AC #2 + U-RT-49 state-ledger + lifecycle-event ACs. Cost-attribution residual (U-RT-49 AC #5) closed at this arc: CP spec v1.4 → v1.5 (§25.9 step-body-owned propagated cost-attribution emission per Q1e) + CP plan v2.12 → v2.13 (convention-level absorption) + `harness-runtime/tests/integration/test_run_smoke.py::test_e2e_run_step_body_fires_cost_attribution_chain` materializes the convention via Q3c mock-rate bypass and produces a 12-field `SpanCostRecord`. Sub-fork `[[fork_u_rt_49_cost_attribution_invocation_underspec]]` CLOSED. `PRICE_TABLE_REF` substitution residual carries forward at `[[fork_price_table_ref_substitution_retirement]]` — bounded X-AL-2 residual, NOT retired by this arc. 2204 tests on the resolution branch (+1 from 2203 on main HEAD `b7df032`).
**Filed:** 2026-05-20 (Phase 2 Session 7, U-RT-44 landing)
**Trigger unit:** U-RT-44 (`design-substrate/Spec_Harness_Runtime_v1.md` §11 C-RT-11)
**Pattern:** `[[halt-route-split-AC-pattern]]`
**Routing target:** runtime spec C-RT-11 + CP-axis workflow loop primitive (not yet specified)

---

## Surface

`Spec_Harness_Runtime_v1.md` §11 C-RT-11 commits 3 drain surfaces:

1. ✅ `HarnessContext.drained_flag` set by signal handler — runtime-owned, landed at U-RT-44.
2. ❌ **CP workflow lifecycle loop polls `ctx.drained_flag.is_set()` at each lifecycle boundary** (per-step entry, per-step exit, per-topology-dispatch entry); on flag-set, completes current step, emits event, returns `RunResult(status='drained')`.
3. ✅ `harness_runtime.run()` rejects new invocations with `HarnessDraining` — runtime-owned, landed at U-RT-44.

Surface (2) is the materialization site for U-RT-44 AC #2: "an in-flight step completes within bounded wait OR surfaces typed timeout."

## Defect

**There is no CP workflow lifecycle loop landed in the runtime body.** `harness_runtime.api.run()` raises `WorkflowExecutionNotYetLandedError` post-bootstrap. Bootstrap completes; execution body is the next-unit horizon. No in-flight step exists to drain.

The spec acknowledges this asymmetry in §11 risk surface:

> If CP later surfaces a native drain primitive (e.g., a CP-level `WorkflowDrainController` type), refactor `harness-runtime/` to delegate drain to CP. This contract becomes a thin adapter. Until then, drain ownership is runtime-axis-local.

But the spec's "runtime-axis-local drain" presumes a runtime-owned workflow loop polls the flag. No such loop exists in the runtime body — and the session-3 atomic decomposition assigns workflow-loop execution to CP-axis composition, not the runtime axis.

## U-RT-44 partial-land

- AC #1 (SIGTERM sets flag) — LAND.
- AC #3 (no new ingress post-drain) — LAND.
- **AC #2 (in-flight step drain) — STRUCK** pending fork resolution.

## Resolution paths

### Path A — Wait for CP workflow loop unit; refactor U-RT-44 at that point [RECOMMENDED]

When the CP workflow loop primitive lands (likely U-RT-49+ E2E surface or a CP-axis follow-up), refactor U-RT-44 to:

- Add `_should_drain(ctx)` polling hook called at lifecycle boundaries by the CP loop.
- Add bounded-wait timeout primitive (composable with `shutdown(ctx, timeout=...)` per C-RT-10).
- Add `RunResult(status='drained')` return path from the CP loop on flag detection.

**Pros:** matches spec §11 risk surface's explicit guidance ("until then, drain ownership is runtime-axis-local" — but in practice no runtime-axis loop exists yet); smallest blast radius; respects axis boundaries; AC #2 lands at the natural materialization site.

**Cons:** AC #2 lives in carry-forward state until the loop unit lands. Carry-forward tracked at `[[carried-fork-audit-before-cluster]]`.

### Path B — Land runtime-side workflow loop scaffolding now [REJECTED]

Add a thin polling loop in `harness_runtime/` that wraps a `WorkflowObject.execute_step()` callable (currently undefined) and polls `drained_flag` between steps.

**Pros:** AC #2 lands now.

**Cons:** scope creep (not in U-RT-44 atomic decomposition); commits to a workflow-step contract that should be a CP-axis decision; risks anti-leakage violation (X-AL-3 silent H_T design extension at Phase 7 execution time).

### Path C — Re-spec C-RT-11 to drop AC #2 from runtime axis entirely [REJECTED]

Move AC #2 commitments to the CP-axis spec (`Spec_Control_Plane_v1_3.md`).

**Pros:** clean axis boundaries.

**Cons:** spec architectural call — Phase 7 execution should not unilaterally restructure axis ownership. If the operator wants this, route through design-substrate revision.

## Operator decision

**Path A recommended.** Sign-off via in-session AskUserQuestion at U-RT-44 land time.

## Carry-forward state

- AC #2 added to `[[phase-7-remaining-workflow]]` under "Open carry-forwards".
- `[[carried-fork-audit-before-cluster]]` discipline applies before L11 (E2E + Pattern P1) opens.
- Refactor target unit: most likely U-RT-49 (E2E happy-path) or a follow-up CP-axis unit that lands the workflow lifecycle loop.

## Provenance

- Spec source: `design-substrate/Spec_Harness_Runtime_v1.md` v1.1 §11 C-RT-11 lines 618–642
- Decomposition source: `.harness/phase-2-session-3-track-a-atomic-decomposition.md` L10 U-RT-44 block
- Predecessor session checkpoint: `~/.gstack/projects/arhugula-v2/checkpoints/20260520-011553-l9-opens-u-rt-43-bootstrap-orchestrator-landed.md`

---

## Resolution status (2026-05-20 — DEFERRED → OPEN-RESOLVING)

**Status flip.** Path D (defer to follow-up phase, recorded at commit `0b7a378`)
superseded. New entry-point locked: **author CP-axis contract C-CP-25
`WorkflowDriver` scoped to `SINGLE_THREADED_LINEAR` topology only**, against
`design-substrate/Spec_Control_Plane_v1_3.md` → v1.4.

**Verification (this session).** Audit of CP spec v1.3 + CP plan v2.10 (with
underlying v2 unit bodies) confirmed: no workflow execution driver contract or
unit exists. U-CP-13 declares the manifest schema; U-CP-14 resolves per-step
binding given a `step_id` (callee, no iteration); U-CP-10 declares the 8
lifecycle event classes; U-CP-15 declares the engine-class enum. No contract
specifies the iterator that calls these per step in order. Advisor-vetted via
wider iteration-vocabulary grep (`iterate|step.by.step|orchestrate|
execute.*step|step.execution|workflow.execution|step.sequence|step.runner`) —
zero hits. Prior session's "no CP workflow loop" diagnosis re-verified, not
inherited.

**Scoping decision (operator-ratified).** New contract scoped to
`SINGLE_THREADED_LINEAR` only. Other 5 topology patterns
(orchestrator-workers / decentralized-handoff / hierarchical-delegation /
evaluator-optimizer / parallelization) deferred until downstream work demands
them — per X-AL-3 (no silent design extension at Phase 7).

**Resolution path (sequential).**
1. ✅ **DONE** — Status DEFERRED → OPEN-RESOLVING; C-CP-25 entry locked.
2. ✅ **DONE** — `systems-architect` skill produced
   `.harness/c_cp_25_workflow_driver_recommendation.md`. Operator ratified
   2026-05-20 (4/4 sign-off points).
3. ✅ **DONE** — `spec-writer` skill applied ratified recommendation into
   `design-substrate/Spec_Control_Plane_v1_4.md` §25 C-CP-25 contract +
   §[traceability] C-CP-25 row + §[coherence pass] v1.4 verification line +
   Filing footer. Adjacent-defect findings surfaced in Change-note per
   no-extension discipline (Anti-finding §6.2 CLAUDE.md table pointer drift —
   not patched at v1.4; informational only).
4. ✅ **DONE** — `implementation-planner` skill produced
   `design-substrate/Implementation_Plan_Control_Plane_v2_11.md` adding
   U-CP-56 (driver core: §25.1/§25.2/§25.3/§25.5/§25.6/§25.7 modes 1–4) +
   U-CP-57 (drain composition: §25.4/§25.7 mode 5). Dependency-graph delta:
   6 new edges (5 within-CP + 3 cross-axis IS + 1 cross-axis runtime);
   acyclic invariant preserved. Coverage matrix: C-CP-25 fully covered.
5. **DONE (with one carry-forward)** — `phase-7-implementation` skill:
   - ⚠️ U-CP-56 (driver core) **PARTIAL-LAND** 2026-05-20 at commit `402a7ea`:
     8 of 9 ACs LAND (#1-#5, #7-#9); AC #6 (save-point-checkpoint selective
     replay-resumption) STRUCK pending Class 1 fork at
     `.harness/class_1_tension_u_cp_56_resumption_underspec.md` (Path A —
     extend U-CP-13 manifest + IS prefix-match read primitive). Weaker
     behavior shipped: RESUMPTION emits on any non-genesis ledger.
   - ✅ U-CP-57 (drain composition) LANDED 2026-05-20: all 6 ACs LAND
     (driver-entry / pre-step / post-step drain checks + no-mid-step
     interruption + bounded-wait composition + drained_flag-not-auto-set).
     `DriverContext` Protocol extended with `drained_flag: asyncio.Event`
     (structurally satisfied by HarnessContext from U-RT-44). 12 new tests
     pass (test_workflow_driver_drain.py); full CP suite 498 pass (486 +
     12 new); runtime suite 651 pass (no regression); pyright + ruff clean.
   - PENDING — U-CP-56 AC #6 finish — Path A: extend U-CP-13 manifest with
     `entry_version` + add IS prefix-match read primitive. Tracked at
     `[[fork-u-cp-56-resumption-underspec]]`. This is the residual gap
     blocking full closure of this parent fork.
6. ✅ **DONE — Runtime un-strike (lane 6).** Refactored
   `harness_runtime.api.run()` to delegate workflow body execution to
   `harness_cp.workflow_driver.execute_workflow()` (C-CP-25 §25). The
   `WorkflowObject` runtime-local Protocol grew via 4 new read-only
   properties (`manifest_entry`, `steps`, `step_dispatcher`,
   `default_model_binding`) per the §8 risk-surface non-breaking-growth
   authorization (Path A operator-ratified 2026-05-20). The synchronous
   CP driver runs via `asyncio.to_thread` so the asyncio loop remains
   responsive to signal handlers; in-flight step bounded-wait materializes
   via this composition (signal → flag → next-boundary DRAINED). The
   `WorkflowExecutionNotYetLandedError` stub surface is removed.

   **Un-struck:**
   - U-RT-44 AC #2 BOTH branches:
     - bounded-wait branch — composed via drain-flag-poll-at-boundary in
       the CP driver (signal sets flag → driver returns DRAINED at next
       boundary).
     - typed-timeout branch — `asyncio.wait_for(...,
       timeout=config.drain_timeout_seconds)` wraps the driver call; on
       `TimeoutError`, runtime surfaces `FailureCause(runtime_fail_class=
       "RT-FAIL-DRAIN-TIMEOUT", ...)` on a DRAINED `RunResult` per
       C-RT-14. Thread NOT cancelled — spec §11 invariant
       ("exceeding the bound forces shutdown to proceed regardless").
       New `RuntimeConfig.drain_timeout_seconds: float = 60.0` field;
       authorized via spec §3 (C-RT-03) "Deferred to implementation
       discretion" clause.
   - U-RT-49 "state-ledger workflow entries" — CP driver writes step
     entries to `ctx.ledger_writer.append` per C-CP-25 §25.3.3.
   - U-RT-49 "lifecycle-event spans" — emitter records workflow.start +
     step events per C-CP-25 §25.5.

   **STILL STRUCK** (carry-forward, not blocking this fork's closure):
   - U-RT-49 "cost-attribution chain produced an entry" — **LAND**
     2026-05-20 at this arc. Sub-fork
     `[[fork_u_rt_49_cost_attribution_invocation_underspec]]` resolved
     via Q1e + Q2-bounded + Q3c + Q4. CP spec v1.5 §25.9 establishes
     the step-body-owned propagated cost-attribution emission contract;
     `harness-runtime/tests/integration/test_run_smoke.py::test_e2e_run_step_body_fires_cost_attribution_chain`
     materializes the convention and asserts a 12-field `SpanCostRecord`
     is produced with §14.4 idempotency-key join. `PRICE_TABLE_REF`
     substitution carries forward at
     `[[fork_price_table_ref_substitution_retirement]]` (bounded X-AL-2
     residual; rate-table authoring out of scope at this arc, deferred
     to sub-phase 7d substitution-retirement events).

   **Tests landed:** 2 new integration tests at
   `harness-runtime/tests/integration/test_run_smoke.py`:
   - `test_e2e_run_executes_workflow_via_cp_driver` — full `run()`
     delegation; asserts ledger entries written via captured append.
   - `test_e2e_run_returns_drained_when_flag_set_before_execute` —
     drain-flag-pre-execute surfaces RunStatus.DRAINED through to runtime
     `RunResult.status == "drained"`.

   **Test totals on worktree:** Runtime 653 pass (was 651; +2 new). CP /
   IS / AS / core unchanged at 498 / 125 / 302 / 18. pyright clean on
   `harness-runtime/src/`; ruff clean.

   **Independent open fork:** `[[fork-u-cp-56-resumption-underspec]]`
   (U-CP-56 AC #6 — Path A: extend U-CP-13 manifest with `entry_version`
   field + IS prefix-match read primitive). Not blocking THIS fork's
   closure since runtime never depended on selective replay-resumption.

**Estimated arc:** 3.5–4.5 sessions (single-pattern scoping vs 5–7+ for full
6-pattern coverage).

**Predecessor session checkpoint (entry-point-lock session):**
`~/.gstack/projects/arhugula-v2/checkpoints/20260520-035000-cp-workflow-driver-spec-gap-locked.md`

**Drafted recommendation (2026-05-20, this session):**
`.harness/c_cp_25_workflow_driver_recommendation.md` — `systems-architect`
tension-resolution mode output; DRAFT pending operator ratification of 4 sign-off
points (scope / engine-class scope / drain semantics / lifecycle-event filter)
plus 1 optional cleanup (CLAUDE.md §2.2 ADR table fix) per recommendation §8.
Anti-finding summary:
- §6.1 Anti-finding A: RECLASSIFIED to NOT-A-FINDING after advisor-prompted
  verification. CP plan v2.6 D9 / Q-R4-7 already aligned U-CP-10's
  `LifecycleEventClass` → harness-core's `WorkflowEventClass` matching spec
  §5.1 verbatim; runtime ships with the spec enum (`harness-core/src/
  harness_core/workflow_event_class.py` + 651 runtime tests on main).
- §6.2 Anti-finding B (Class 3 informational): workspace root `CLAUDE.md` §2.2
  ADR table mislabels 4 of 5 F-ADR rows (F2/F3/F4/F5 titles all incorrect; F1
  correct). Non-blocking cleanup.

---

## Audit reconciliation (2026-05-20)

**Verified status:** RESOLVED

**Resolving artifact / evidence:** Already labeled FULLY CLOSED 2026-05-20 (CP spec v1.4 + plan v2.13 + runtime delegation to CP driver; 2204 tests green at closure). Audit confirms.

**Audit context:** Workspace-wide tension-record audit 2026-05-20 (post-U-RT-52 merge to main at 2b945ab). 33 records reviewed against current code + spec state. Result: 28 RESOLVED, 5 DEFERRED-PARTITION, 0 STILL-OPEN. The 'Status' line earlier in this record predates the audit; this section is the current verified state.
