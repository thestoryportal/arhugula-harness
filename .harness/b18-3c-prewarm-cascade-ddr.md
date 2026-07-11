# B-18-3C-PREWARM-CASCADE — Design Decision Record

**Arc**: B-18-3C-PREWARM-CASCADE  
**Status**: Pre-build — DDR gate (`decompose_at_open: true`)  
**Filed**: 2026-07-11  
**Advisor review**: Called pre-file (§13.1 gate)  
**Fable-5 review**: R1–R5 REAL, C1–C4 CONCERN, M1 COSMETIC; DDR updated post-review  
**Relates to**: B-18-3C-PREWARM (CP spec v1.87 §25.17), B-18-3C-PREWARM-COHORTKEY (v1.88), B-18-3C-PREWARM-DEFAULT-ON (v1.89, PR #926)  
**Spec target**: CP spec v1.89 → v1.90

---

## 1. Problem

B-18-3C-PREWARM (CP spec v1.87) added the serialized-branch[0] cache warm-up to the **PROCEED** cascade-policy path only (`_proceed_fanout`, `workflow_driver.py:7588`). The same warm-up benefit applies to the **CASCADE_CANCEL** and **PAUSE** paths, which share `_cancel_branch`/`_cancel_fanout` (line 7627–7822). This arc extends `_warmup_gate` and the phase-1/phase-2 serialization to those paths.

Larger review surface than PROCEED:

- `_cancel_branch` uses `dispatch_branch_step_shielded` + the `_BRANCH_INFLIGHT_DISPATCHES` deadline watchdog — shared deadline management is non-trivial.
- `_crash_pause_reestablish` (line 7936–7945) is a PAUSE-specific crash-resume path that must not be invalidated by the warmup's altered dispatch ordering.
- The not-yet-dispatched `cancelled` terminal scan (CASCADE_CANCEL, line 7855–7886) runs AFTER the barrier; its correctness is scope-keyed on dispatch-marker absence, which warmup preserves.

---

## 2. Invariant 1 — Effect-set

**Fable-5 R1 corrected**: the sound argument is NOT "RESEARCH/CONTENT_CREATION = always non-effectful" — `CohortKeyCapable` attests cache-stability, not effect-freedom, and the effect-fence apparatus (lines 7844–7869) exists precisely because effects occur on these paths.

**Correct claim**: warmup WITHHOLDS branches[1..N-1] dispatch until branch[0] completes. If branch[0] fails in Phase 1, branches[1..N-1] never dispatch — they produce no effect. Their effect-set is a proper SUBSET of what non-warmup CASCADE_CANCEL would produce (under non-warmup, a sibling MAY land an effect before cancellation arrives). Warmup is therefore **strictly safer** on effect-set, not just equivalent.

**Authority** (line 6297–6303): the existing code comment argues: "an orphaned sibling either never dispatched (no effect) or already passed its operator gate." The warmup's withheld siblings are in the "never dispatched" category. **Effect-set invariant holds via dispatch-withholding, not workload-class restriction.**

---

## 3. Invariant 2 — Records + crash-resume equivalence

### 3a. `_crash_pause_reestablish` naturally protected by H3

`_crash_pause_reestablish` (line 7936–7945) fires only when `not branch_plan` — all branches recovered-terminal. The H3 guard in `_same_prefix_cohort()` returns False when `len(branch_plan) < 2`, so `_warmup_gate = False` when `branch_plan` is empty. The re-establish path is unreachable under warmup. *(Fable-5 C3 note: the re-establish CAN fire on the non-warmup path in that state — it rests on record-equivalence verified below at §3d.)*

### 3b. Mid-fanout crash: branch[0] failed, branches[1..N-1] not yet started

Crash scenario:
- branch[0] ran-and-errored: dispatch marker + terminal "completed" + no output in durable store
- branches[1..N-1]: NO dispatch marker, NO terminal record
- PAUSED snapshot: NOT yet written (crash happened between Phase 1 raise and snapshot persistence)

On crash-resume re-entry:
- `terminal_dispositions` includes only branch[0] (= "completed")
- `collected` has no branch[0] output
- `branch_plan` = [(1,...),(2,...)] (non-empty — branches 1..N-1 not recovered)
- `_crash_pause_reestablish` condition `not branch_plan` = **FALSE** → re-establish does NOT fire
- The fanout barrier runs (branches[1..N-1] dispatched)

**Critical gap (Fable-5 R2 — open design decision for build)**: if branches[1..N-1] all succeed on re-dispatch, `branch_failed` is False (no live barrier exception) and `_crash_pause_reestablish` is False (branch_plan was non-empty during fanout). The post-barrier check `if branch_failed or _crash_pause_reestablish` is **FALSE** — the code falls through to the SUCCESS/PARTIAL path, silently ignoring branch[0]'s failure. For PAUSE policy this is a semantic violation: branch[0] failed; the run should have paused.

Under non-warmup (pre-arc): the same crash would leave branches[1..N-1] in MAYBE-RAN state (dispatch markers written but no terminal records) → strict-tier crash-resume fails-CLOSED via B-FANOUT-CRASH-RESUME-STRICT-TIER-INCOMPLETE. Warmup creates a CLEANER mid-fanout crash state (definitively not-yet-dispatched) but this removes the strict-tier fail-closed protection.

**Pre-build design decision required**:

Option A (RECOMMENDED): Before the barrier runs, synthesize `branch_failed = True` from seed-loop data: if any recovered terminal is `terminal_dispositions[bi] == "completed" and bi not in collected` and `bi` is NOT in `branch_plan` (i.e., it ran in a prior invocation phase), set `branch_failed = True` pre-barrier. The PAUSE block then fires immediately without re-dispatching siblings.

Option B: Accept the semantic difference (PARTIAL instead of PAUSED in this narrow crash window) with explicit spec rationale.

The build arc MUST resolve this before merging. W6 (below) covers the witness.

### 3c. PAUSE snapshot with branch[0]-fail + branches[1..N-1] not-yet-dispatched (live run)

In a live (non-crash) run where branch[0] fails in Phase 1:
- `branch_failed = True` raised by re-wrapped BaseExceptionGroup
- branches[1..N-1] NEVER dispatched (no dispatch markers, no terminal records)
- For PAUSE: not-yet-dispatched scan deliberately NOT run (§25.15.1 pause semantic, line 7910–7912)
- PAUSE block builds `PeerFanOutResumeState.branches` from `terminal_dispositions` + `collected`: only branch[0]
- Absent ordinals left re-dispatchable by omission (line 7963)
- On resume: branches[1..N-1] re-dispatched; branch[0] skipped (already terminal)
- **Valid for the live-path PAUSE snapshot.**

### 3d. Post-Phase-2 crash (all branches recovered-terminal, warmup ran)

Crash after all branches complete (Phase 1 + Phase 2 both finished) but before PAUSE snapshot written:
- ALL branches are recovered-terminal → `branch_plan` is empty → `not branch_plan` = TRUE
- H3 returns False (len=0 < 2) → `_warmup_gate = False` → non-warmup path
- `_crash_pause_reestablish` fires as normal (if branch[0] failed)
- The reconstructed terminal records from the warmup path MUST match what non-warmup would produce for the re-establish to be correct:
  - branch[0]: `_cancel_branch` writes dispatch marker + terminal "completed" (same as non-warmup)
  - branches[1..N-1]: `_cancel_branch` writes dispatch marker + terminal records (same as non-warmup TaskGroup)
  - Record-equivalence holds: the same `_cancel_branch` function writes the same records regardless of warmup/non-warmup routing.

---

## 4. Deadline management design

`cascade_cancel_barrier` uses two composed mechanisms to bound stuck dispatches (line 2131–2144):

1. **Deadline watchdog** (`_deadline_cutoff` at line 2166): cancels each registered in-flight future from `_BRANCH_INFLIGHT_DISPATCHES` directly — bypasses `asyncio.shield` (which only guards against the BRANCH's own cancellation).
2. **`asyncio.timeout(deadline_seconds)`** (line 2186): cancels TaskGroup tasks stuck at gate-only boundaries with no in-flight dispatch for the watchdog to cut.

**Constraint**: Phase 1 (branch[0] solo) and Phase 2 (branches[1..N-1] in TaskGroup) MUST share ONE deadline budget and ONE watchdog. Splitting into two `cascade_cancel_barrier` calls would grant each phase the full `deadline_seconds`, potentially doubling the maximum wall-clock time.

**Acknowledged semantic change (Fable-5 R4)**: branch[0]'s serial Phase 1 duration consumes siblings' deadline budget. A slow-but-successful branch[0] causes a tighter deadline window for Phase 2 — potentially spurious `timed_out`/`cancelled` records that concurrent dispatch avoided. This is the same tradeoff as the PROCEED warmup (acknowledged at CP spec v1.87 §25.17); it is an explicit opt-in via `concurrent_cache_warmup=True` AND the `CohortKeyCapable` oracle gate. W4 covers the deadline-budget witness.

**Decision**: Inline the barrier setup for the warmup path, matching `cascade_cancel_barrier`'s structure:

```python
async def _cancel_fanout() -> list[None]:
    if not _warmup_gate:
        return await cascade_cancel_barrier(
            (_cancel_branch(*plan) for plan in branch_plan), deadline_seconds=deadline
        )
    # B-18-3C-PREWARM-CASCADE: shared deadline + watchdog across Phase 1 + Phase 2.
    # Inline the cascade_cancel_barrier setup (NOT two barrier calls) so both phases
    # share one deadline_seconds budget and one _BRANCH_INFLIGHT_DISPATCHES registry.
    inflight_dispatches: set[asyncio.Future[Any]] = set()
    parent_chain = _BRANCH_INFLIGHT_DISPATCHES.get() or ()
    registry_token = _BRANCH_INFLIGHT_DISPATCHES.set((*parent_chain, inflight_dispatches))

    async def _deadline_cutoff() -> None:
        await asyncio.sleep(deadline)
        for inflight in list(inflight_dispatches):
            if not inflight.done():
                inflight.cancel()

    cutoff_task = asyncio.ensure_future(_deadline_cutoff())
    try:
        async with asyncio.timeout(deadline):
            # Phase 1: branch[0] solo (cache-write, dispatch marker written).
            # Guard: CancelledError ONLY (Fable-5 R3 correction: asyncio.timeout delivers
            # CancelledError INSIDE the block, not TimeoutError; a bare TimeoutError from
            # _cancel_branch is a branch failure — NOT a deadline — and must NOT be caught
            # here to avoid misclassification as BranchBarrierDeadlineExceededError).
            try:
                await _cancel_branch(*branch_plan[0])
            except asyncio.CancelledError:
                raise
            except BaseException as exc:
                raise BaseExceptionGroup("cascade-warmup-branch0", [exc]) from exc
            # Phase 2: branches[1..N-1] via TaskGroup (cache-hits).
            # On branch failure: TaskGroup raises ExceptionGroup (BaseExceptionGroup
            # subclass) → propagates unchanged → caller: branch_failed = True.
            if len(branch_plan) > 1:
                async with asyncio.TaskGroup() as task_group:
                    tasks = [
                        task_group.create_task(_cancel_branch(*plan))
                        for plan in branch_plan[1:]
                    ]
                return [None, *(t.result() for t in tasks)]
            return [None]
    except TimeoutError as exc:
        raise BranchBarrierDeadlineExceededError(deadline) from exc
    finally:
        cutoff_task.cancel()
        _BRANCH_INFLIGHT_DISPATCHES.reset(registry_token)
```

*Note (Fable-5 C2)*: parameterizing `cascade_cancel_barrier` with a `serialize_first: bool` flag would avoid copy-drift with the original. Deferred to the build arc author to decide; the inline approach keeps the diff self-contained.

---

## 5. Lift `_same_prefix_cohort()` and `_warmup_gate`

Currently `_same_prefix_cohort()` is defined INSIDE `if cascade_policy is CascadePolicy.PROCEED:` (line 7488). The lift:

- Move `_same_prefix_cohort()` definition above the cascade_policy branch
- Compute `_warmup_gate: bool = _d4.concurrent_cache_warmup and _same_prefix_cohort()` before the cascade_policy branch
- The PROCEED block removes its now-redundant local copies

H3 guard (`len(branch_plan) < 2`) uses the LIVE `branch_plan` (post-recovery-seed). On crash-resume with 2-of-3 branches recovered, `branch_plan = [(2,...)]` → H3 returns True (len=1 < 2) → `_warmup_gate = False`. On crash-resume with all branches recovered, `branch_plan = []` → H3 returns True → `_warmup_gate = False`. *(Fable-5 C4 note: on partial-recovery with 2+ remaining branches, warmup applies to the resumed fanout with a NEW "branch[0]" — the first remaining branch. This is plausible but unstated; W4b covers it.)*

---

## 6. Witnesses required

| # | Test | Purpose |
|---|---|---|
| W1 | CASCADE_CANCEL + `_warmup_gate=True`: branch[0] dispatches before branch[1] | Ordering witness — warmup serialization applies |
| W2 | CASCADE_CANCEL + `_warmup_gate=True`, branch[0] fails: branches[1..N-1] have no dispatch marker AND are recorded `cancelled`, run FAILED | not-yet-dispatched scan covers warmup-path non-starters (Fable-5 M1: assert dispatch-marker absence, not just `cancelled` records) |
| W3 | PAUSE + `_warmup_gate=True`, branch[0] fails: snapshot contains only branch[0], resume re-dispatches branches[1..N-1] | PAUSE resume state valid from branch[0]-fail warmup |
| W4 | CASCADE_CANCEL + `_warmup_gate=False` (non-CohortKeyCapable): routes to `cascade_cancel_barrier`, byte-identical to pre-arc behavior | Gate=False baseline unchanged |
| W4b | PAUSE + `_warmup_gate=True`, partial-recovery crash-resume (branches 0+1 recovered, branch 2 re-dispatched): warmup applies with new "branch[0]" = branch 2 | Partial-recovery resume + warmup interaction correct |
| W5 | PROCEED warmup unmodified — existing `test_workflow_driver_parallelization_warmup.py` all green | Lift of `_same_prefix_cohort` didn't break PROCEED |
| W6 | PAUSE + `_warmup_gate=True`, crash-resume after branch[0]-fail + branches[1..N-1] not-yet-dispatched: run DOES NOT silently succeed as PARTIAL; correct outcome (PAUSED or FAILED depending on Option A/B decision at §3b) | Crash-resume gap coverage (Fable-5 R5; the decisive test) |

---

## 7. Open design decision (must resolve before build)

**§3b gap — pre-barrier `branch_failed` synthesis**

The build arc must choose:

**Option A** (recommended): Before `_cancel_fanout`, detect recovered "completed" + not-in-collected branches that are NOT in `branch_plan` (i.e., they ran in a prior phase and failed before snapshot was written). Set `branch_failed = True` pre-barrier. The PAUSE snapshot then fires without re-dispatching siblings, and W6 passes as PAUSED.

Implementation sketch:
```python
# Detect prior-phase branch failure (warmup Phase 1 crash window):
# a recovered "completed" + no-output branch NOT in the current branch_plan
# signals a past-phase failure whose snapshot was never written.
_prior_phase_ids = {
    plan[0] for plan in all_branch_plans
} - {plan[0] for plan in branch_plan}  # branches that already ran
if not branch_failed and any(
    terminal_dispositions.get(_bi) == "completed" and _bi not in collected
    for _bi in _prior_phase_ids
):
    branch_failed = True
```

This check is warmup-window-specific but safe under non-warmup (where `_prior_phase_ids` is either empty or already handled by strict-tier fail-closed).

**Option B**: Accept PARTIAL in this crash window with spec rationale. The window is narrow (branch[0] complete → snapshot not yet written) and PARTIAL is not semantically wrong for the partial-data case. Requires explicit CP spec v1.90 acknowledgment.

---

## 8. Spec delta (CP spec v1.89 → v1.90)

**§25.17 addendum — CASCADE_CANCEL + PAUSE paths**

When `_warmup_gate` is True and `cascade_policy is CascadePolicy.CASCADE_CANCEL` or `CascadePolicy.PAUSE`, the `_cancel_fanout()` serializes branch[0] (Phase 1) before releasing branches[1..N-1] (Phase 2) under the TaskGroup. Both phases share one `asyncio.timeout(deadline)` and one `_BRANCH_INFLIGHT_DISPATCHES` deadline watchdog. The warmup does NOT split into two `cascade_cancel_barrier` calls (which would double the deadline budget).

Phase 1 uses `except asyncio.CancelledError: raise` — NOT `except (asyncio.CancelledError, TimeoutError)` — because `asyncio.timeout` delivers `CancelledError` INSIDE the block; a bare `TimeoutError` from Phase 1 is a branch failure, not a deadline signal.

Effect-set: warmup withholds branches[1..N-1] dispatch until branch[0] completes; on branch[0] failure their effect-set is empty (dispatch-withheld). Warmup is strictly safer (subset effect-set) vs concurrent dispatch.

Crash-resume (PAUSE): the §3b pre-barrier `branch_failed` synthesis (Option A) ensures a mid-fanout crash with branch[0]-failed does not silently produce PARTIAL on re-dispatch success.

Budget: branch[0]'s serial Phase 1 duration consumes siblings' deadline budget. This is the same acknowledged tradeoff as PROCEED warmup (§25.17). Opt-in via `concurrent_cache_warmup` + `CohortKeyCapable` oracle.

---

## 9. Arc decomposition (build arc)

Single Phase 7 session:

1. Resolve §3b design decision (Option A or B)
2. Lift `_same_prefix_cohort()` + `_warmup_gate` above the cascade_policy branch
3. Add `_cancel_fanout` warmup branch (Phase 1 + Phase 2 with shared deadline/watchdog, R3-corrected guard)
4. If Option A: add pre-barrier `branch_failed` synthesis
5. Add W1–W6 witnesses (extend `test_workflow_driver_parallelization_warmup.py`)
6. `just check` green
7. Codex review to convergence
8. Spec delta CP v1.89 → v1.90 + clearance marker
9. Close arc-ledger row B-18-3C-PREWARM-CASCADE
10. PR + §12.2 terminating refresh

**Feature branch**: `b18-3c-prewarm-cascade` off `main` after operator pushes the pending `3f471818` terminating-refresh commit.

---

*Filed by: Claude Code (Sonnet 4.6) — advisor + Fable-5 decorrelated reviews applied*
