# Class 1 Fork — Path (i) DURABLE_ASYNC Engine Class Materialization Gate

**Filed**: 2026-05-25
**Workspace HEAD at filing**: `bd50cd6` (post-Reading A path 1 arc close; `main` = `origin/main`)
**Routing class**: Class 1 (halt-execution; design-phase back-flow required per X-AL-3)
**Status:** CLOSED-DEFERRED 2026-05-25 — operator routed to §4 option (E) "Defer indefinitely + fix §3(a) doc-drift"; §3(a) doc-drift patched at skip-reason text this arc; un-skip gates on future DURABLE_ASYNC engine class materialization via full design-phase back-flow

---

## §1 — Gate

`harness-runtime/tests/integration/test_u_rt_95_hitl_pause_trigger_durable_async_full_execution_path.py::test_path_i_durable_async_pause_trigger_returns_paused` is `@pytest.mark.skip`'d. The skip-reason cites: "Path (i) full pause-trigger cycle requires a DURABLE_ASYNC matrix cell (RECONCILER_LOOP / WAL_SEGMENT engine classes per CP §18.1)."

Un-skipping Path (i) requires at least one of `RECONCILER_LOOP` / `WAL_SEGMENT` to be added to `_IN_SCOPE_ENGINE_CLASSES` at `harness-cp/src/harness_cp/workflow_driver.py:81-83` such that the driver's `EngineClassNotYetMaterializedError` raise at `:604-605` does not short-circuit the durable-async cell composition.

## §2 — Empirical engine-class materialization state at HEAD `bd50cd6`

| Engine class | In `_IN_SCOPE_ENGINE_CLASSES`? | Substrate implication |
|---|---|---|
| `PURE_PATTERN_NO_ENGINE` | YES | none (in-process) |
| `SAVE_POINT_CHECKPOINT` | YES | filesystem checkpoint |
| `EVENT_SOURCED_REPLAY` | NO | event store (deterministic replay) |
| `RECONCILER_LOOP` | NO | K8s control plane per `engine_class_candidate.py:70` |
| `WAL_SEGMENT` | NO | write-ahead log |

Only 2 of 5 engine classes are runtime-materialized at HEAD.

## §3 — Adjacent doc-drift findings (NOT fixed at filing per FM-2)

(a) Skip-reason text at `test_u_rt_95_...:354-368` claims `EVENT_SOURCED_REPLAY` is runtime-materialized. Empirical verification at `_IN_SCOPE_ENGINE_CLASSES` contradicts — only PURE_PATTERN_NO_ENGINE + SAVE_POINT_CHECKPOINT are in-scope. Class 3 doc-drift surfaced for operator-discretion repair at follow-on arc.

(b) Prior checkpoint summary at `20260524-233326-reading-a-path-1-arc-complete-20-commits.md` inherited the same stale claim — same drift, same fix surface.

## §4 — Routing options for operator

| Option | Scope | Substrate work | Commits | X-AL-3 status |
|---|---|---|---|---|
| **(A) RECONCILER_LOOP full materialization** | New driver dispatch + workload binding + topology overlay + K8s controller substrate (Operator pattern; reconciler tick loop; per-iteration state read/diff/converge) | K8s control plane | 25–45, multi-axis, multi-session | Design-phase back-flow required |
| **(B) WAL_SEGMENT full materialization** | New driver dispatch + workload binding + topology overlay + write-ahead log substrate (segment writer; segment replay; idempotent consumer state) | WAL infrastructure | 20–35, multi-axis, multi-session | Design-phase back-flow required |
| **(C) EVENT_SOURCED_REPLAY full materialization** | New driver dispatch + event store + deterministic replay engine. NOTE: not a DURABLE_ASYNC class in the strict §18.1 reading — this option ALSO requires confirmation that EVENT_SOURCED_REPLAY satisfies the Path (i) DURABLE_ASYNC matrix cell semantics, OR the test gate must be re-scoped to "any non-default engine class". | Event store | 15–25, multi-axis | Design-phase back-flow required + scope clarification |
| **(D) Test-only synthetic in-scope marker** | Widen `_IN_SCOPE_ENGINE_CLASSES` with a synthetic DURABLE_ASYNC marker at the driver layer just to land Path (i) e2e against a stub durable-async substrate. Composer body + driver catch already work — this proves the binding chain end-to-end. | Stub fixture | 2–4, single-session | Still an X-AL-3 surface — adding to `_IN_SCOPE_ENGINE_CLASSES` is a design-extension at the driver boundary. Fidelity question for operator. |
| **(E) Defer indefinitely** | No work; Path (i) stays `@pytest.mark.skip`. Composer body + driver catch are already unit-tested at `test_lifecycle_hitl_gate_composer.py` + `test_workflow_driver.py`. | None | 0 | Preserves status quo. Optionally fix §3(a) doc-drift in a tiny separate commit. |

## §5 — Recommendation framing (operator decides)

(D) is the lowest-cost option but is **not** fidelity-pure: it grows the in-scope engine-class set at the driver layer for non-substantive reasons. (E) is fidelity-pure but leaves a single skipped test as the only e2e gap; the underlying mechanism is already unit-tested.

(A)/(B)/(C) are substantial design-phase arcs that ship real durable-async substrate. (C) is the lowest-substrate of the three but requires scope clarification on whether EVENT_SOURCED_REPLAY counts as a DURABLE_ASYNC matrix cell.

If operator priority is **closing the skip-list with high fidelity**: (E) + tiny §3(a) doc-drift fix.
If operator priority is **proving the binding chain e2e against any engine class**: (D).
If operator priority is **shipping production durable-async**: (C) is the lowest-substrate path with real value (deterministic event-sourced replay is independently useful); (B) is the canonical DURABLE_ASYNC choice; (A) is infrastructure-heavy.

## §6 — What does NOT happen at this fork's filing

- No code change.
- No spec amendment.
- No plan amendment.
- No `_IN_SCOPE_ENGINE_CLASSES` widening.
- No driver re-dispatch logic.

This file is the entire deliverable until operator routes.

## §7 — Closure conditions

This fork closes when:
- Operator picks one of (A)/(B)/(C)/(D)/(E), AND
- For (A)/(B)/(C): design-phase back-flow re-issues the relevant spec + plan artifacts AND the Phase 7 impl arc lands at this workspace; OR
- For (D): operator ratifies the fidelity trade-off and the 2–4 commit narrow arc lands; OR
- For (E): operator confirms indefinite deferral and the skip-reason text is corrected for the §3(a) drift.

## §8 — References

- Skip site: `harness-runtime/tests/integration/test_u_rt_95_hitl_pause_trigger_durable_async_full_execution_path.py:354-368`
- Gate site: `harness-cp/src/harness_cp/workflow_driver.py:81-83` (`_IN_SCOPE_ENGINE_CLASSES`) + `:604-605` (raise site)
- Error definition: `harness-cp/src/harness_cp/workflow_driver_errors.py:41-58` (`EngineClassNotYetMaterializedError`)
- Workload→engine selection: `harness-cp/src/harness_cp/workload_binding_engine_class_selection.py:102-104`
- Topology overlay: `harness-cp/src/harness_cp/per_engine_class_topology_overlay.py:72-96`
- Workspace authority: `CLAUDE.md` §4.3 + §4.4 (X-AL-3 — no silent H_T design extension at Phase 7)

---

## §9 — Closure block

**Closure timestamp**: 2026-05-25
**Operator routing**: §4 option **(E) Defer indefinitely + fix §3(a) doc-drift**
**Closure arc**: single commit on `worktree-fork-path-i-engine-class-mat`; merges to `main` post-test-pass

**Resolution work at closure arc:**
1. Skip-reason text at `test_u_rt_95_..._full_execution_path.py:354-368` corrected:
   - REMOVED: false claim that `EVENT_SOURCED_REPLAY` is runtime-materialized.
   - REPLACED with: empirical statement that only `PURE_PATTERN_NO_ENGINE` and `SAVE_POINT_CHECKPOINT` are in `_IN_SCOPE_ENGINE_CLASSES` at HEAD.
   - ADDED: explicit pointer to this fork doc at `.harness/class_1_fork_path_i_durable_async_engine_class_materialization.md §4 option (E)` documenting the indefinite-deferral routing.
2. This fork doc retained as the operator-routed deferral record. Path (i) un-skip gate = future DURABLE_ASYNC engine class materialization through full design-phase back-flow (options A/B/C/D NOT chosen).

**Adjacent defect §3(b) NOT patched at this arc per FM-2** — prior checkpoint summary at `20260524-233326-reading-a-path-1-arc-complete-20-commits.md` carries the same stale claim. Checkpoint summaries are immutable historical records; they are not re-written for downstream doc-drift discoveries.

**Coverage posture at closure** — Path (i) e2e remains the single skipped test in `test_u_rt_95_...full_execution_path.py`. The underlying mechanism (composer durable-async body + driver-side `HITLPauseRequestedSignal` catch) is unit-tested at `test_lifecycle_hitl_gate_composer.py` + `test_workflow_driver.py`. Empirical-verification gap = e2e wiring through `execute_workflow` against a real DURABLE_ASYNC engine class; gap deferred per operator decision.

**Un-skip trigger** — when operator opens any of §4 options (A)/(B)/(C)/(D) at a future arc, re-evaluate this fork's CLOSED-DEFERRED status. Reopening requires: re-classifying CLOSED-DEFERRED → PROPOSING + new operator routing decision + new closure arc.

**Re-verification at closure**:
- `_IN_SCOPE_ENGINE_CLASSES` at `harness-cp/src/harness_cp/workflow_driver.py:81-83` = `{PURE_PATTERN_NO_ENGINE, SAVE_POINT_CHECKPOINT}` (2 members, unchanged at this arc).
- Path (i) test still `@pytest.mark.skip`'d with corrected reason text.
- No spec / plan / driver / `_IN_SCOPE_ENGINE_CLASSES` change at this arc.

**No retirement-ledger update owed** — this fork does not advance any H_T substitution row; it is a doc-drift fix + deferral record.
