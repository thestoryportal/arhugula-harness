# Adversarial Review — R-FS-1 arc #12 / B1-impl-6 — U-CP-86 `PARALLELIZATION` driver strategy

## Summary

- **Mode:** Phase-7 pre-implementation review (pre-merge gate; standing posture A). Red-team of a completed impl arc against previously-cleared spec/plan.
- **Arc:** R-FS-1 arc #12 / B1-impl-6 — `PARALLELIZATION` driver strategy (the FIRST non-linear topology strategy). Branch `r-fs-1-arc-12-u-cp-86-parallelization`, commit `82b1469`.
- **Artifacts reviewed:**
  - `harness-cp/src/harness_cp/workflow_driver.py` (strategy + dispatch routing; the additive U-CP-86 block at lines 2105–2427 + the dispatch flip at 102–155 + the early-return at 1293–1314)
  - `harness-cp/tests/test_workflow_driver_parallelization.py` (new, 511 lines, 12 tests)
  - `harness-cp/tests/test_workflow_driver_branch_substrate.py` + `test_workflow_driver.py` (regression-test updates)
- **Cleared authority verified byte-exact:** CP spec `Spec_Control_Plane_v1_32.md` §25.10–§25.18; CP plan `Implementation_Plan_Control_Plane_v2_32.md` U-CP-86 + §3; IS spec `Spec_Information_Substrate_v1.md` §5.4; runtime spec `Spec_Harness_Runtime_v1.md` v1.48 §2.2 + §9.
- **Date:** 2026-06-14
- **Finding count by §4.1 review-severity:** Class 3: 0 · Class 2: 0 · Class 1: 1 (informational doc-nit, NON-blocking)
- **Highest-severity finding:** none above Class 1.
- **Disposition recommendation:** **VERDICT CLEAR / APPROVE — merge-ready.** No §2.7.6 Phase-7 fork triggered. The single Class-1 nit is an inline doc-comment polish, foldable post-merge.

The verdict-deciding check (per the decorrelated reviewer): *can `PARALLELIZATION` bind effectful / `EXTERNAL_IRREVERSIBLE` steps, and would they dispatch ungated?* — was run FIRST and resolves to **no gap** (see F-REJECTED-01). That check was the APPROVE-vs-HALT discriminator; it cleared.

---

## Class 3 findings (severe — phase re-opening)

None.

## Class 2 findings (moderate — current-phase revision)

None.

## Class 1 findings (minor — documentation drift)

### F1-01 — Inline comment "the emitter is not thread-safe" slightly over-claims the mechanism
- **Location:** `harness-cp/src/harness_cp/workflow_driver.py:2213–2218` (`_drain_and_emit_step_boundaries` docstring) + 2228–2229.
- **Defect:** The docstring says `STEP_BOUNDARY` is single-threaded "because the lifecycle emitter is NOT thread-safe." The *actual* load-bearing reason the emitter is never touched from a worker thread is structural, not a thread-safety workaround: the `append_branch_*` buffering and the emit both run on the single loop/driver thread (the buffering runs *after* `await asyncio.to_thread(...)` returns to the loop; the emit runs after `asyncio.run(_fanout())` returns to the driver worker thread). The thread-safety framing is a true-but-secondary rationale; the primary invariant is "all emitter access is post-await/post-`asyncio.run`, on one thread."
- **Discriminator:** (a/b/c all miss) — prose-clarity only; zero behavior impact, zero contract impact. The behavior is correct and tested (`test_parallelization_emits_workflow_start_and_step_boundaries` asserts exactly 1 WORKFLOW_START + 3 STEP_BOUNDARY).
- **Evidence:** `_run_branch` buffers via `append_branch_step_ledger_entry(...)` at lines 2352–2367, which execute on the event-loop thread after the `await asyncio.to_thread(dispatcher.dispatch, ...)` at 2344 returns; `_drain_and_emit_step_boundaries` runs at 2387/2404/2417 after `asyncio.run(_fanout())` returns (line 2379).
- **Decision-vocabulary:** *decided* (the comment is accurate but the rationale is incomplete; no reading-ambiguity).
- **Resolution:** Inline comment polish — clarify that single-threadedness is structural (post-await on one thread), with thread-safety as the secondary safeguard. Non-blocking; foldable into any later CP touch (e.g. U-CP-87/88). Do NOT block merge.

---

## Findings considered and rejected (transparency — substantive checks applied)

### F-REJECTED-01 — [VERDICT-DECIDING] Ungated effectful fan-out dispatch (§25.15.2 obl. 5 / blast-radius) — NOT a defect
- **Attack:** AS-domain blast-radius monotonicity + CP §25.15.2 obl. 5 ("high-blast-radius pre-dispatch gating"). The concern: `_run_branch` (2343–2346) calls `dispatcher.dispatch` with no *visible* HITL/sandbox gate — could a fan-out dispatch an `EXTERNAL_IRREVERSIBLE` step ungated?
- **Why rejected (two independent reasons):**
  1. **The gate is composed INSIDE the dispatcher, identically for both paths.** The LINEAR path (`workflow_driver.py:1521`) ALSO calls `step_dispatchers.lookup(step.step_kind).dispatch(binding, step, step_context=step_context)` with NO driver-site pre-dispatch gate — the C-AS-02→C-CP-19§19.1→C-CP-16 chain (§25.15.2 obl. 5) lives in the injected runtime dispatcher (which raises `HITLPauseRequestedSignal`, caught at 1548). PARALLELIZATION passes the SAME `step_context` (with `parent_gate_level` / `parent_sandbox_tier`, descended via `compose_branch_child_context`, `workflow_driver_types.py:291–315`) into the SAME dispatcher, fired INLINE via `await asyncio.to_thread(...)`. Buffering defers only the WRITE, never the gate (§25.15.2 obl. 2). So the fan-out is gated EXACTLY as the linear path is — no relative regression.
  2. **PARALLELIZATION cannot bind the dangerous workload classes.** `topology_pattern.py:84–85` admits `PARALLELIZATION` for `WorkloadClass.RESEARCH` + `CONTENT_CREATION` only (C-CP-10 §10.3 cells; admissibility rejected at workflow-binding per §25.10 Invariant 2, NOT re-checked by the driver — correctly, line 2303–2305). These are non-effectful/non-`EXTERNAL_IRREVERSIBLE` cells.
  - **Scoping basis (stated explicitly per the SKILL):** the §25.15.2 obligations are titled "the eight **cascade-cancel** obligations" and §25.15 is `cascade_policy` consumption = U-CP-85, which U-CP-86 deps EXCLUDE. The defensible classification: none of the 8 bind at U-CP-86 — happy-path fan-out + coarse FAILED, with audit-completeness (obl. 3) + discriminating `terminal_status` (obl. 4) + the `proceed`/`pause`/`cascade-cancel` reach correctly deferred to U-CP-85/88. Obl. 5's gate is a COMMITTED primitive (the dispatcher chain), already in force for both paths. Resolves clean.

### F-REJECTED-02 — Determinism: `max()`-on-tie + canonical-JSON aggregate (§25.12 D1.b boundary 2)
- **Attack:** Could `_aggregate_parallelization` (2165–2203) leak completion-order, or pick a non-lowest-index winner on tie?
- **Rejected:** Empirically verified. `sorted_outputs` sorts by branch_index FIRST (2186); votes tally into an insertion-ordered dict in branch-index order (2191–2198); CPython `max()` returns the FIRST-encountered max → among count-ties, the first-inserted (lowest-branch-index) key wins. `json.dumps(output, sort_keys=True, default=str)` is key-order-independent (verified: `{"x":1,"y":2}` and `{"y":2,"x":1}` canonicalize identically). All-distinct → every vote 1 → tie → branch 0 (pinned by `test_parallelization_aggregate_all_distinct_lowest_index_tiebreak` + `test_parallelization_two_way_tie_breaks_to_lowest_index`). The persisted append order is independently deterministic via `drain_branch_buffers` sorting by branch_index (`test_parallelization_completion_order_independent` forces a REVERSE-completion `threading.Event` chain — no `time.sleep`, not timing-flaky — and asserts `[0,0,1,1,2,2,3,3]`). §25.12 boundary 2 ("first to finish wins is forbidden") honored.

### F-REJECTED-03 — Append discipline (§25.12 D1.b / D1 single-threaded-write)
- **Attack:** Does every branch use the BUFFERED path (never inline `_append_step_ledger_entry`)? Is the single-writer boundary preserved (no second `prior_event_hash`)?
- **Rejected:** Each branch is given its own `BufferingLedgerWriter` (2315) which only buffers (`workflow_driver.py:548–550`); `drain_branch_buffers` (573–599) serializes through the ONE real `ctx.ledger_writer` in branch-index order — no second `prior_event_hash`, no DAG entry (matches §25.12 D1 verbatim). The live-e2e (`test_parallelization_live_e2e_real_ledger_chain_valid`) writes through the REAL IS writer (`_RealLedgerWriter` → `append_ledger_entry`) and re-verifies `verify_chain(entries).status is VerificationStatus.VALID` over 8 persisted entries — a GENUINE chain-integrity assertion (not vacuous: it reads back from a real JSONL handle and runs §6.3 verification), confirming the concurrent fan-out's serialized appends form an intact single-parent chain.

### F-REJECTED-04 — No-silent-failure on branch exception (audit-completeness)
- **Attack:** On a branch raising, is anything dropped silently? Is "completed branches persist" tested or hollow?
- **Rejected (with a recorded test-shape caveat, non-blocking):** The `except Exception` handler (2397–2413) drains whatever each branch buffered BEFORE returning FAILED (2404), so completed branches' entries persist. `test_parallelization_branch_failure_returns_failed_and_persists_completed` asserts branch 1 (failed) contributed NO entries while branches 0+2 persisted (`sorted(set(persisted)) == [0, 2]`). The `terminal_status` is correctly `completed` (dispatch-boundary disposition, never `failed` — IS §5.4 closed set `{cancelled, completed, timed_out}`; verified `append_branch_terminal_ledger_entry` forecloses `failed`). **Caveat (recorded, not a finding):** the test uses an INSTANT `_VariedDispatcher`, so siblings buffer before the exception propagates; with slow real dispatch, `bounded_barrier`'s `finally`-cancel could hit a branch still awaiting `to_thread` → `CancelledError` at the await → its post-await `append_branch_*` never runs, while the `to_thread` OS thread runs the sync dispatch to completion (asyncio cannot kill it) → an effect could land without a ledger entry. This is the audit-completeness gap §25.15.2 obl. 3+4 close — and those obligations are EXPLICITLY U-CP-85 scope, which U-CP-86 excludes. At U-CP-86's admissible cells (RESEARCH/CONTENT_CREATION, non-effectful) this is benign; at U-CP-88 (effectful + cascade) the shielded-dispatch machinery (`dispatch_branch_step_shielded`, already landed at U-CP-85) addresses it. NOT a U-CP-86 defect.

### F-REJECTED-05 — Concurrency honesty: `await asyncio.to_thread(sync dispatch)` + timestamp monotonicity
- **Attack:** Is real concurrency achieved? Is the emitter touched from worker threads? Is the single shared `fanout_timestamp` monotonic against the zero-tolerance IS writer?
- **Rejected:** `await asyncio.to_thread(dispatcher.dispatch, ...)` (2344) runs the BLOCKING sync dispatch off-loop → N branches genuinely overlap (the reverse-completion test proves true concurrency: branch i blocks on branch i+1's `threading.Event`, which only succeeds if they run simultaneously). The emitter is NEVER touched from a worker thread (F1-01 confirms the structural reason). The single `fanout_timestamp = datetime.now(UTC)` (2299) is shared by every branch entry → all-equal → trivially non-decreasing under the IS zero-tolerance monotonic-timestamp writer regardless of drain order; the e2e through the real writer confirms no `IDEMPOTENT_NOOP` drop (8/8 land).

### F-REJECTED-06 — Dependency-faithfulness (U-CP-86 deps EXCLUDE U-CP-85)
- **Attack:** Does the code lean on cascade machinery (`cascade_cancel_barrier` / `dispatch_branch_step_shielded`) it shouldn't? It should use only `bounded_barrier`.
- **Rejected:** `_execute_parallelization` calls ONLY `bounded_barrier` (2371) — the policy-neutral, `gather`-based, leak-free barrier (602–657). It does NOT call `cascade_cancel_barrier` (777) or `dispatch_branch_step_shielded`, and uses NO `asyncio.shield` (explicitly documented at 2341–2342). `bounded_barrier` re-raises branch exceptions verbatim for the strategy to map to FAILED. Plan §3.1 (line 271) confirms `[U-CP-80, U-CP-81, U-CP-82, U-CP-84]` — U-CP-85 absent. Faithful.

### F-REJECTED-07 — Regression / §25.10 Invariant 1 (linear path BYTE-UNCHANGED)
- **Attack:** Is `SINGLE_THREADED_LINEAR` byte-unchanged (early return before the linear loop)? Did the dispatch-table/enum change break closed-at-6 exhaustiveness?
- **Rejected:** The PARALLELIZATION dispatch is an early `return _execute_parallelization(...)` at 1303–1314, BEFORE the unchanged linear loop (1330+). The only edits to the linear region are the `resolve_driver_strategy(...)` return-value capture (1288, previously a bare call) + the early-return block — the loop body is untouched. The enum gains `PARALLELIZATION` but `_DRIVER_STRATEGY_DISPATCH` still maps all 6 `TopologyPattern` members (1 LINEAR_INLINE + 1 PARALLELIZATION + 4 NOT_YET_MATERIALIZED). Empirically matched: `test_workflow_driver.py` + `test_workflow_driver_branch_substrate.py` = 48 passed; `test_engine_class_not_yet_materialized_raised...` correctly re-pointed to `ORCHESTRATOR_WORKERS` (still NOT_YET); `_NON_LINEAR_PATTERNS` → `_NOT_YET_MATERIALIZED_PATTERNS` (4 members, PARALLELIZATION excluded). Parallelization suite = 12 passed.

### F-REJECTED-08 — Reading-1 branch model (claim 1): "each WorkflowStep = one branch, ZERO schema extension"
- **Attack (X-AL-3):** Is "branch = single `WorkflowStep`" a silent semantic the spec didn't authorize? Does it foreclose a legitimate multi-step-branch reading §25.11 requires?
- **Rejected — surfaced as *proposing*/informational (the SKILL's decision-vocabulary; both readings spelled out, no pick):**
  - *Reading A (the impl's):* §25.11 defines "a branch = a sub-sequence of `WorkflowStep`s." A sub-sequence of length 1 is a valid minimal instantiation; mapping each declared `WorkflowStep` to one branch over its varied `step_payload` is the natural fit for PARALLELIZATION's "fan-out N branches over VARIED INPUTS" (§25.11 row + "variation is in *inputs*", §25.11 meaningfulness para). ZERO schema extension is the X-AL-3-AVOIDING move — inventing a branch-spec payload schema would itself BE the design extension.
  - *Reading B (the worry):* a "branch = multi-step sub-sequence" reading is foreclosed.
  - **Resolution:** Reading B does not bind — each strategy gets its OWN `_execute_<strategy>` function (O-CP-1(d) flat-dispatch, decided here), so U-CP-86's length-1 instantiation does NOT constrain U-CP-87+ (EVALUATOR_OPTIMIZER is explicitly a SEQUENTIAL multi-step loop per its plan AC). No contract is narrowed; no spec text is contradicted. Informational, NOT a fork. (X-AL-3 anti-extension check: CLEAN — the arc touches only `harness-cp/src` + tests, no `design-substrate/**`; Phase-7 posture trivially correct.)

### F-REJECTED-09 — Cross-spec / cross-code drift (PARALLELIZATION / `_DriverStrategyStatus` / dispatch table)
- **Attack:** Grep sibling specs + code for stale cite-shapes (the workspace's biggest defect class).
- **Rejected:** No stale "PARALLELIZATION raises NOT_YET_MATERIALIZED" shape survives outside the arc. Sibling specs (CP plan v2.32, runtime v1.48 §2.2) say "the 5 non-linear patterns/strategies" only in CONTRACT-scope statements (correct — the SPEC authored all 5 contracts; the PLAN lands them one unit at a time at U-CP-86..90), never as a materialization-status claim about PARALLELIZATION. `topology_pattern.py` admissibility cells unchanged + consistent. The `.pyc` binary matches are stale bytecode (harmless; suite re-run clean after no source-stale concern). No `cxa_seam_missing_endpoint` / orphan implied (no new cross-axis import — CP-local + already-allowlisted IS imports).

### F-REJECTED-10 — Pre-existing Q1 doc items NOT attributable to this arc
- **Attack:** Does the arc introduce the `§25`/`§28` mislabel or the `RunStatus` "closed at cardinality 4" docstring drift?
- **Rejected:** Both are flagged in the CP spec v1.32's OWN `§-adjacent observations` (a)+(b) as PRE-EXISTING Q1 cite-hygiene residuals predating B1. The arc neither introduces nor is obligated to fix them. Attributed as pre-existing, not this arc's defects.

### F-REJECTED-11 — Runtime `'partial'` projection mis-binding
- **Attack:** Does U-CP-86 wrongly return PARTIAL (which is `proceed`/U-CP-85 machinery)?
- **Rejected:** `_execute_parallelization` returns ONLY `RunStatus.SUCCESS` (clean / empty-steps) or `RunStatus.FAILED` (any branch raise / barrier deadline) — never PARTIAL. Runtime spec v1.48 §9 + §2.2(point 6) bind `'partial'` to `cascade_policy = proceed` (≥1 branch failed, run proceeded with a partial aggregate) — exactly U-CP-85's machinery, which U-CP-86 excludes. The coarse SUCCESS/FAILED at this unit's scope is faithful to §25.18's "PARALLELIZATION → simplest" + the explicit U-CP-85-defers-PARTIAL note (`workflow_driver.py:2398–2403`).

---

## Disposition

**VERDICT CLEAR / APPROVE — merge-ready.**

Per §4.1: only Class-1 findings present (one inline-comment polish) → clearance with optional inline fix. No §4.1 Class 2/3 finding; no §2.7.6 Phase-7 fork (no Class-1 halt, no Class-2 operator decision, no Class-3 design-defect requiring back-flow). The implementation is a faithful, surgical materialization of C-CP-25 §25.10–§25.18 + the U-CP-86 plan unit:

- Both AC parts satisfied + tested: (1) fan-out→barrier→single deterministic aggregate (lowest-branch-index tiebreak; completion-order-independence proven via a non-flaky reverse-completion `threading.Event` chain); (2) branch entries persist in branch-index order with `branch_metadata` causality.
- The dependency exclusion of U-CP-85 is honored structurally (only `bounded_barrier`; SUCCESS/FAILED only; PARTIAL/discriminating-`terminal_status`/cascade-cancel correctly deferred).
- §25.10 Invariant 1 (linear byte-unchanged) verified by early-return placement + 48-test regression pass.
- §25.12 determinism boundary (append-order + aggregate both pure functions of the ordered set) verified empirically.
- Live-e2e re-verifies the §6.3 hash chain VALID through the REAL IS writer — a genuine, not vacuous, integrity assertion.
- O-CP-1(d) `DriverStrategy`-shape decision (flat enum-keyed dispatch, no callable/class registry) is a defensible simplicity-first call faithful to §25.18 impl-discretion.

**Self-audit (per SKILL §8):** severity distribution sane (not all-Class-3 escalation, not all-Class-1 smoothing — a near-empty inventory matching a genuinely-clean surgical arc); every finding/rejection carries a resolving Location + Evidence + discriminator; no author-mode drift (F1-01 resolution describes shape, supplies no replacement text); no context-bleed (no invented expansions); decision-vocabulary applied (F1-01 *decided*; F-REJECTED-08 *proposing* with both readings); rejected-findings populated with 11 substantive checks; §4.1 review-severity kept distinct from §2.7.6 fork-class throughout.

**Empirical verifications run this session:** parallelization suite 12/12 pass (post cache-clear); linear + branch-substrate regression 48/48 pass; `max()`-on-tie + canonical-JSON determinism confirmed in an isolated probe; IS §5.4 + runtime v1.48 §9/§2.2 + CP §25.10–§25.18 + plan U-CP-86/§3 read byte-exact; admissibility cells (`topology_pattern.py:84–85` RESEARCH/CONTENT_CREATION) confirmed; cross-spec/code drift grep clean.

---

## Addendum — out-of-family Codex pre-merge pass (decorrelated, post-fix)

The arc was driven through `just codex-review` (out-of-family, $0 subscription) per CLAUDE.md §13.1/§13.2 alongside this adversarial pass — a decorrelated reviewer with **no transcript**, reviewing the diff cold.

**Codex round 1 — [P1] CONFIRMED + FIXED (decorrelation payoff).** `asyncio.run(_fanout())` joins the default `ThreadPoolExecutor` at shutdown (`loop.shutdown_default_executor()`), so a wedged SYNC branch thread (CPython cannot kill a thread) would block the parent's return at executor shutdown EVEN AFTER `bounded_barrier` raised the §25.11 deadline — re-defeating the cap. This adversarial agent rated the deadline concern benign-for-scope; Codex caught the concrete hang. **Fixed** via `_run_fanout_to_completion` (a dedicated loop + executor; clean→`shutdown(wait=True)` reclaim, exception→`shutdown(wait=False)` abandon) + a regression test (`test_parallelization_barrier_deadline_does_not_hang`). This is the textbook decorrelation outcome: each reviewer caught what the other missed.

**Codex round 2 — [P1] REVIEWED → DISPOSITIONED out-of-scope-by-dependency-partition (NOT fixed).** Codex flagged the `except BaseException → shutdown(wait=False)` path: on an *ordinary branch failure* (not a deadline) it abandons siblings, so a healthy sibling's `to_thread` dispatch can keep running after `execute_workflow` returned FAILED ("external side effects after the run is reported terminal"). **Disposition — keep `wait=False`; this is correct for U-CP-86's scope:**

1. **`wait=True`-on-failure would violate U-CP-86's OWN §25.11 obligation.** A branch that fails fast (t=1s) has already exited `bounded_barrier`'s `asyncio.timeout(deadline)` window; a `wait=True` join of a genuinely-wedged sibling would then block PAST the deadline, forever — the exact "strand the parent indefinitely" failure §25.11 forbids. Any wedge-possible path MUST abandon. Parent-bounding is the obligation U-CP-86 owns and honors.
2. **Sibling-effect-disposition is U-CP-85 scope by design.** "What happens to siblings when a branch fails" is literally the §25.15.1 `cascade_policy` table (`proceed` = run-to-completion / `cascade-cancel` / `pause`). U-CP-86's dependency set EXCLUDES U-CP-85 precisely so it holds no opinion here. A "wait for in-flight up to the deadline" fix would re-implement U-CP-85's `proceed` inside U-CP-86 and collide when that machinery wires in at U-CP-88 — the scope-creep the dependency graph exists to prevent.
3. **No silent-uncompensated-effect results, re-grounded directly (not via subagent):** `topology_pattern.py:73-86` `_CROSS_PATTERN_ADMISSIBLE` admits PARALLELIZATION only at `(PARALLELIZATION, RESEARCH)` + `(PARALLELIZATION, CONTENT_CREATION)` — non-effectful breadth-search / A-B cells — and PARALLELIZATION is NOT any workload's §11.1 primary (no match in `per_workload_class_topology.py`). Further, an effectful step gates BEFORE dispatch *inside* the dispatcher (C-AS-02→C-CP-19→C-CP-16; only the ledger WRITE is buffered, never the gate), so an orphaned sibling either never dispatched (no effect) or already passed its operator gate.

The `except`-path comment (`workflow_driver.py`) was tightened to state both halves of the partition explicitly. Per §13.2, convergence-to-zero with Codex is NOT required when a finding is out-of-scope-by-design (a round-3 pass with no transcript would re-flag the same partition); this is a documented disposition decided with the transcript-aware `advisor()` as tie-breaker, not a silent drop.

**Reconciliation:** advisor() (transcript-aware) broke the reviewer split in favor of this adversarial pass's scope reading — the §25.11-requires-`wait=False` argument is decisive and the partition is clean (U-CP-86 owns parent-bounding; U-CP-85 owns sibling-effect-disposition).
