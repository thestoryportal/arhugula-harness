# Finding v2 — `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT` option (a) is ALSO unsound: the [P1-a] result-fidelity gap is NOT fan-out-specific

*R-FS-1 forward-arc design finding, second attempt. 2026-06-26. Mode-agnostic process-substrate (no design-substrate change, no code change). Supersedes the framing in `b-fanout-crash-resume-maybe-ran-subagent-design-finding-v1.md` on ONE point (the scope of [P1-a]); the v1 doc's §2 reusable grounding + §3/§4 constraints otherwise stand. The arc STAYS `registered` in `.harness/arc-ledger.yaml` — disposition is now **option (b) confirmed-correct + a precise named prerequisite**, not "attempt option (a) in a fresh context."*

---

## 0. TL;DR

The v1 finding (2026-06-25) concluded the arc is "not a clean leaf-fenced single-level slice" and prescribed, for the next attempt, **option (a)**: narrow the recovery to a `topology == SINGLE_THREADED_LINEAR` child, on the theory that the [P1-a] recursive RESULT-fidelity gap was specific to **fan-out children** (a PARALLELIZATION/ORCHESTRATOR_WORKERS child engaging its *own* fan-out crash-resume reconstruction). 

**This second attempt establishes — by code-reading + a by-execution witness — that [P1-a] is NOT fan-out-specific.** A re-dispatched maybe-ran child returns a **silently suffix-only `final_state`** for a *LINEAR* child too, because the gap is the generic `execute_workflow` resume behavior: on a re-run over an F2-committed prefix, the loop starts at `resume_at` with `accumulated` initialized EMPTY, and the prefix outputs are NOT replayed into `accumulated` ("degenerate at HEAD"). The child folds this truncated state into the parent aggregate.

**Therefore option (a) does not soundly close the arc.** The disposition reverts to **option (b)** (keep all maybe-ran SUB_AGENT fail-closed — the CURRENT, correct behavior) and names the true prerequisite: **child-final_state-reconstruction** (replay the durably-stored prefix outputs into `accumulated` on resume), which is the still-degenerate half of the `B-ENGINE-OUTPUT-REPLAY` family (`.harness/r-fs-1-e-impl-1-finding.md`). No maybe-ran SUB_AGENT recovery — linear OR fan-out, worker OR orchestrator — can be result-faithful until that prerequisite is built.

This was found **cheaply** (code-read + a ~1-second execution witness) BEFORE building the multi-hour real-recursive-child fixture — the go/no-go discipline (`[[feedback-autonomous-loop-dont-stop-to-ask]]` deep-arc rule + the in-session go/no-go contract) working as intended.

---

## 1. The witness (by execution, not just reading)

A throwaway pytest (now removed) reused the existing `test_workflow_driver.py` fakes (`_FakeCtx` / `_FakeLedger` / `_FakeLedgerReader` / `_EchoDispatcher`) to run the REAL `execute_workflow` twice over a 3-step LINEAR workflow:

- **no-crash baseline** (genesis ledger): all 3 steps dispatch → `final_state = {step-0, step-1, step-2}`, status SUCCESS.
- **resume** (same `run_id`, steps 0+1 already F2-committed via the ledger_reader): only step-2 dispatches → `final_state = {step-2}`, status **SUCCESS**.

Result, identical for BOTH durable auto-fence engine classes tested:

```
=== save-point-checkpoint ===          === event-sourced-replay ===
  no-crash final_state: [0,1,2]          no-crash final_state: [0,1,2]
  resume   final_state: [2]              resume   final_state: [2]
  status base=success resume=success     status base=success resume=success
  *** [P1-a] CONFIRMED: DROPS [0,1]      *** [P1-a] CONFIRMED: DROPS [0,1]
```

The resumed run reports **SUCCESS with a truncated `final_state`** — a silent corruption, not a fail-closed. Both `SAVE_POINT_CHECKPOINT` and `EVENT_SOURCED_REPLAY` (and, by the same `_determine_resume_at` prefix-skip code path, `WAL_SEGMENT` and `RECONCILER_LOOP`) — i.e. ALL four `_DURABLE_AUTO_FENCE_ENGINE_CLASSES`, which is exactly the set a SUB_AGENT child must use to be fence-recoverable in the first place.

## 2. Why this happens (code anchors, HEAD `0bc26549`)

`harness-cp/src/harness_cp/workflow_driver.py`:

- **`accumulated: dict[str, Any] = {}`** (line 3246) — the final_state accumulator starts EMPTY every envelope.
- **`for step_index, step in enumerate(steps[resume_at:], start=resume_at)`** (line 3268) — the loop skips the committed prefix; `accumulated[str(step.step_id)] = dict(step_output)` (line 3932) only ever records steps executed in THIS envelope.
- **`final_state=dict(accumulated)`** (line 3967) — SUCCESS returns only this envelope's steps.
- **`resume_at`** is computed by `_determine_event_replay_resume_at` → `_determine_resume_at` (lines 4020/3972), which advances over the contiguous F2-ledger prefix keyed by per-step `idempotency_key` derived from the (reused) `run_idempotency_key`.
- The cached-output-replay-into-downstream-state refinement is **"degenerate at HEAD"** (lines 2978–2981, 4038–4045): the F2 `EntryPayload` carries only `response_hash` (no activity output), and the existing `_rehydrate_inter_step_channel_on_replay` replays prefix outputs into the **inter-step channel** (B-INTERSTEP dataflow), NOT into `accumulated`/final_state. So the resumed `final_state` is structurally suffix-only.

A child sub-workflow runs through this SAME `execute_workflow` (`harness-runtime/.../child_workflow_runner.py:163-171` calls it and returns its `RunResult` verbatim). So E1 (deterministic child `run_id`, the v1 §2 mechanism) is **necessary but not sufficient**: it gives at-most-once for the child's TOOLS (the per-`(child_run_idempotency_key, step_id, tool_id)` fence at `effect_fence.py`), but the child's FINAL_STATE is still suffix-only/empty whenever the child committed ≥1 step before the parent crash.

**The parent fold consumes exactly that truncated state (airtight cite).** `harness-runtime/.../sub_agent_dispatch.py:660-663` — on child SUCCESS the composer sets `step_output = dict(child_result.final_state or {})`, and that `step_output` is the SUB_AGENT worker's branch output the parent fan-out aggregate folds (`_aggregate_orchestrator_workers` / `_aggregate_parallelization`). A suffix-only child `final_state` → a suffix-only worker `step_output` → a silently-corrupted parent aggregate (the run still reports SUCCESS). This closes the one v1-carried link not re-verified this session.

## 3. What this corrects in v1

- v1 §3 [P1-a] framed the result-fidelity leak as a property of a **fan-out-of-TOOL-steps child** ("re-dispatching such a child engages the child's OWN fan-out crash-resume reconstruction"). 
- v2 establishes the leak is the **generic linear resume behavior** (prefix-skip + empty accumulator), so v1 §4.1's prescription ("a genuinely-single-level slice must require `topology == SINGLE_THREADED_LINEAR`") is **insufficient** — a LINEAR child leaks identically.
- v1 §2/§3 [P1-b] (the resumed-fence-gate gap) and §4.2 (dual-gate) still stand as additional constraints, but are moot until the prerequisite below is built.

## 4. The true prerequisite (the real next-buildable unblocker)

**`B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT` — child-final_state-reconstruction:** on a durable-engine-class resume, the committed prefix's step outputs must be replayed into `accumulated` so the resumed `final_state` equals the no-crash `final_state` (status SUCCESS today returns suffix-only).

**Crucial correction vs a first reading:** the durable output store ALREADY EXISTS. `B-ENGINE-OUTPUT-REPLAY` (arc-ledger `B-ENGINE-OUTPUT-REPLAY`, runtime C-RT-32 §14.23, #665) records each step's output to the `EngineOutputStore` for `EVENT_SOURCED_REPLAY` (and `WAL_SEGMENT` via `B-ENGINE-OUTPUT-REPLAY-WAL-SEGMENT`). But it replays the stored prefix into the **inter-step CHANNEL** (a downstream step's INPUT), NOT into `accumulated` (the run's OUTPUT/final_state) — `accumulated` "is never read downstream" (`r-fs-1-e-impl-1-finding.md`; `workflow_driver.py` accumulator). So the missing capability is narrow and distinct: **on resume, also seed `accumulated[step_id]` from the stored prefix outputs** so the returned `final_state` reconstructs. The store is not the gap; the final_state-seeding is.

**The fork question to ground at open (the §4.2 distinction preserved):**
- Seeding `accumulated` at the TOP-LEVEL resume CHANGES the currently-ACCEPTED "degenerate" suffix-only resume semantic → a candidate spec/ADR fork (is suffix-only an intended committed semantic or an unclosed gap?).
- A **child-scoped** reconstruction — rebuild only the CHILD's returned `final_state` from its durable outputs at the `child_workflow_runner` / `sub_agent_dispatch` fold boundary, WITHOUT touching top-level resume — may close the SUBAGENT arcs **without** a fork. That child-scoped vs general framing is the first thing the next session grounds; it is flagged in the registration so it is not rediscovered.

Until `B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT` lands, NO maybe-ran SUB_AGENT recovery is result-faithful. This blocks BOTH registered recursive-child arcs: `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT` (worker) and `B-FANOUT-CRASH-RESUME-ORCHESTRATOR-MAYBE-RAN-SUBAGENT` (orchestrator).

## 4.5 Reconciliation with prior untracked work + a pre-existing latent defect

This second attempt was conducted fresh and then **discovered the #746 session had already found the same suffix-only fold** and left two UNTRACKED (never-committed, never-merged) docs in the working tree:

- `.harness/class_3_child_resume_final_state_suffix_only_fold.md` — the original Class-3 record of the suffix-only fold (filed 2026-06-25). Its line cites (`:3165` / `:3851` / `:3886`) are the **pre-revert** numbers; this v2 carries the HEAD-current cites (`:3246` / `:3932` / `:3967`). The naming `B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT` is adopted from that doc for continuity.
- `.harness/arc-open-b-fanout-maybe-ran-subagent.md` — the #746 arc-open checkpoint; its "corrected decomposition" (prerequisite #1 = deterministic child identity [built on the reverted branch]; prerequisite #2 = child-final_state-reconstruction) matches this v2's conclusion. Its "branch state" + tally are #746-era stale (the `feat/b-fanout-maybe-ran-subagent` branch was reverted; the ledger tally has since moved).

Both prior docs were **never landed in the tracked arc-ledger** — so the corrected understanding was lost and this v2 re-derived it. This PR **lands it durably** (registers the prerequisite arc + repoints the SUBAGENT blockers) so it is not lost a third time. v2's distinct contribution beyond the prior docs: the explicit **LINEAR-does-not-escape** witness (the v1 finding's option-(a) prescription is invalidated, not just refined) + the airtight parent-fold cite + HEAD-current line numbers.

**Pre-existing latent defect surfaced by the prior session (carried forward here, do not lose again):** the suffix-only resume `final_state` is a **general** `execute_workflow` property, so the EXISTING, CLEARED, MERGED **B-HIERARCHICAL-PAUSE** captured-child-resume fold (#680 — `SubAgentChildPausedError` → re-enter child via `child_resume_snapshot` → fold the resumed child's `final_state`) ALSO returns suffix-only output → a corrupted aggregate. This is NOT introduced by the (unbuilt) SUBAGENT arc; it is a latent result-fidelity gap in shipped code, gated behind narrow conditions (HIERARCHICAL child pause + a committed child prefix). The prior session classified it Class-3 (informational, non-blocking) and advisor-reconciled that. It is fixed by the SAME `B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT` prerequisite. Flagged here + on the prerequisite arc's `anticipated_scope` so the eventual builder closes both with one mechanism. (A fresh re-verification of its reachability/severity — vs. the prior session's classification — is itself a candidate task, NOT done this session.)

## 5. Disposition

- **`B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT` STAYS `registered`.** The current fail-closed behavior (option b) is CORRECT — re-dispatch would silently corrupt the parent aggregate. Option (a) is ruled out (this finding). No code change this session.
- **`B-FANOUT-CRASH-RESUME-ORCHESTRATOR-MAYBE-RAN-SUBAGENT` STAYS `registered`** for the same reason (same prerequisite).
- The genuine forward unblocker for the SUBAGENT family is **child-final_state-reconstruction** (§4), which deserves its own grounded arc (possibly a fork on the top-level resume semantic) in a fresh context — NOT a continuation of this already-deep session (the v1 §6 loop-trap caution).

## 6. Reviewer chain

- **Code grounding** (direct read at HEAD `0bc26549`): the `accumulated`-empty / `resume_at`-skip / `final_state=dict(accumulated)` chain + the "degenerate at HEAD" replay comments.
- **By-execution witness** (throwaway pytest over the real `execute_workflow`): suffix-only `final_state` on resume for `SAVE_POINT_CHECKPOINT` + `EVENT_SOURCED_REPLAY` (status SUCCESS — silent), verified RED against the no-crash baseline.
- **advisor** (full-transcript, ×2): go/no-go contract bound BEFORE code (build-order + stop-rule + the "no half-mechanism" constraint); disposition reconcile AFTER the witness — affirmed STOP, directed (1) register the prerequisite structurally not prose-only, (2) airtighten the parent-fold cite. Both done.
- **Continuity catch** (`[[porting-old-branch-wip-may-be-superseded]]` / root CLAUDE.md §10.8): the two untracked #746 docs were found before shipping → this PR reconciles + lands them rather than duplicating; the prior `B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT` name + the B-HIERARCHICAL-PAUSE latent-defect observation are carried forward.
