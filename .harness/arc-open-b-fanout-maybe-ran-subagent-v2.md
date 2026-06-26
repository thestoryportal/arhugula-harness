# Arc-open (v2 build) — `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT` (R-FS-1)

*Durable, resumable build checkpoint. Authored 2026-06-26 at arc-open on branch `feat/r-fs-1-maybe-ran-subagent-v2`. Supersedes the #746 `arc-open-b-fanout-maybe-ran-subagent.md` (that branch was REVERTED). advisor-vetted (full-transcript, GO). The prerequisite this arc waited on — `B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT` — is NOW BUILT on HEAD (#764/#766/#768) and witnessed for the LINEAR child (#770).*

## Why this can close now (it could not at #746)

The #746 revert was on TWO Codex [P1]s:
- **[P1-a] result-fidelity**: a re-dispatched child returned a suffix-only `final_state` (the parent fold corrupts). **CLOSED on HEAD**: `B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT` seeds `accumulated` from the durable output store on a `{ESR,WAL}` resume (`workflow_driver.py:3369`, opt-in `reconstruct_final_state=True`, child runner passes it at `child_workflow_runner.py:187`). #770 witnessed it for the LINEAR child over a REAL run_key-respecting `EngineOutputStore`.
- **[P1-b] resumed-manifest replay gate**: the gate trusted the dispatch-time fact but re-dispatched the (possibly operator-edited) resumed child. The reverted branch's `6930e7ef` fix added the dual dispatch∧resumed replay-capable gate — REUSED here.

## Design (reuses the reverted branch structure + TWO corrections)

Reference (NOT port): `feat/b-fanout-maybe-ran-subagent` @ `6930e7ef`. The E1 mechanism + extractor/marker/classifier STRUCTURE is reusable; the recoverability PREDICATE is the suspect part (advisor #4) and is CORRECTED here.

### Correction 1 — LINEAR narrowing in the recoverability predicate (the [P1-a] fix)

The reverted extractor keyed recoverability on `child engine ∈ _FANOUT_REPLAY_ENGINE_CLASSES` ({ESR,WAL}) ONLY. That admits a FAN-OUT child, whose own fan-out reconstruction is unwitnessed (`#770`: "fan-out child stays a registered follow-on"). The corrected predicate:

```
recoverable(child) = (child.engine_class ∈ {EVENT_SOURCED_REPLAY, WAL_SEGMENT})
                   ∧ (child.topology_pattern == SINGLE_THREADED_LINEAR)
                   ∧ (every child step kind ∉ {SUB_AGENT_DISPATCH, MANAGED_AGENTS})
```

The 3rd conjunct holds the witnessed LEAF scope (the #770 witness = a LINEAR child with a committed TOOL step). A LINEAR child with a nested SUB_AGENT/MANAGED step is the deeper recursion → a registered follow-on, NOT this slice.

`_FANOUT_REPLAY_ENGINE_CLASSES` is ALREADY exactly `{ESR, WAL}` on HEAD (`workflow_driver.py:697`) — the reconstruction-capable set (a SUBSET of the runtime's 4 auto-fence classes). SAVE_POINT/RECONCILER children are NOT in it → fail closed (their reconstruction is the still-registered `B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT-SAVE-POINT-RECONCILER`).

### Correction 2 — composer SEED-GATING (a real [P1-a]-class bug in the reverted branch)

The reverted composer passed `child_run_id_seed` UNCONDITIONALLY on every SUB_AGENT dispatch. A deterministic child run_id makes the child auto-resume on ANY re-dispatch — including the LINEAR-PARENT-resume path (which the fan-out classifier does NOT gate) and SAVE_POINT/RECONCILER children (which have NO reconstruction store). Result: a maybe-ran SAVE_POINT-child SUB_AGENT on a linear-parent resume → deterministic id → child auto-resumes → suffix-only `final_state` → silent fold corruption. The exact [P1-a] failure mode, through a different door (advisor #1).

**Fix:** gate the seed on recoverability in the composer:
```
child_run_id_seed = compose_child_run_id_seed(...) if subagent_child_recoverable(payload) else None
```
`None` → legacy fresh-uuid → no auto-resume → non-recoverable children retain PRE-EXISTING behavior (no regression). The deterministic-auto-resume is scoped EXACTLY to the `{ESR,WAL}∧LINEAR∧leaf` set where reconstruction makes it sound. Complements (does not duplicate) the CP fan-out classifier gate.

## Build manifest (files + change)

1. **`harness-runtime/.../child_workflow_runner.py`** — E1: add `child_run_id_seed: str | None = None` to the `ChildWorkflowRunner` Protocol + `_runner`; `child_run_id = snapshot.run_id if resume else (seed if seed is not None else uuid4)`. (Reuse the reverted diff verbatim.)
2. **`harness-runtime/.../sub_agent_dispatch.py`** — `compose_child_run_id_seed(parent_idempotency_key, child_workflow_id)` (reuse verbatim) + `subagent_child_recoverable(payload) -> bool` (typed, the corrected 3-conjunct predicate) + seed-gating at the runner call (Correction 2).
3. **`harness-runtime/.../engine_output_store.py`** — `record_branch_dispatched(..., child_recoverable: bool | None = None)` (omit field when None → byte-identical markers) + reader `subagent_child_recoverable_indexes(run_key) -> set[int]` (torn/absent → not in set → fail closed).
4. **`harness-cp/.../workflow_driver.py`** —
   - `_subagent_child_recoverable(step) -> bool | None`: defensive structural read of the opaque `step_payload["child_manifest_entry"]` engine_class + topology_pattern + `child_steps[].step_kind` (CORRECTED predicate; mirror of the runtime typed one; any parse failure → False/fail-closed). Imports only CP-owned `EngineClass`/`TopologyPattern`/`StepKind` enums.
   - `_resumed_subagent_recoverable_by_ordinal(...)`: the [P1-b] resumed-side set (calls `_subagent_child_recoverable` on the resumed step).
   - `_mark_branch_dispatched`: for a SUB_AGENT step, compute `_subagent_child_recoverable(step)` + record it in the marker.
   - `_fence_unrecoverable_maybe_ran_indices`: add the SUB_AGENT recoverable disjunct — `dispatched_kind==SUB_AGENT ∧ resumed_kind==SUB_AGENT ∧ same step_id ∧ bi ∈ dispatch-marker-recoverable ∧ bi ∈ resumed-recoverable` (the [P1-b] dual gate). Update all 3 classifier consume sites + the cardinality-only site.
5. **Witness** (`test_workflow_driver_fanout_output_replay_full_chain.py` / a sibling) — convert #770's PINNED-run_id witness to E1-LIVE (the seed derives the id; not pinned) full-chain: real `compose_child_workflow_runner → execute_workflow`, real `EngineOutputStore`, parent crash mid-fan-out → branch maybe-ran → resume → assert recovered child `final_state` == no-crash `final_state` AND child TOOL fired once. NEGATIVE CONTROLS: (a) SAVE_POINT child → seed=None + classifier fail-closed; (b) fan-out child → not recoverable (LINEAR narrowing); (c) [P1-b] child edited LINEAR→fan-out between dispatch+resume → fail closed.
6. **Specs**: CP spec delta (new §; `_fence_unrecoverable_maybe_ran_indices` SUB_AGENT disjunct) + runtime spec delta (C-RT-17 §14.7.4 `child_run_id_seed` + the recoverability predicate) + 2 clearance markers.
7. **arc-ledger**: flip `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT` → closed; REGISTER the residuals (LINEAR-child-with-nested-subagent recursion; fan-out child already covered by the orchestrator/`-SAVE-POINT-RECONCILER` arcs — confirm no duplicate). + spine + dashboard regen.
8. **Convergence**: out-of-family Codex (`just codex-review --base main`) to convergence (≥1 round expected — the family's pattern) + advisor pre-done + adversarial reviewer. Then PR (bundled CP+runtime+design-substrate w/ clearance → X-AL-3 passes) + §12.2.1 terminating refresh.

## Decompose-at-open cut (the stop boundary)

- **CLOSE**: maybe-ran SUB_AGENT_DISPATCH **worker**, LINEAR `{ESR,WAL}` leaf child, fan-out crash-resume (strict tier). Whole recovery (E1 + seed-gating + marker + classifier + [P1-b]) + the E1-live witness.
- **REGISTER / already-registered**: fan-out child reconstruction (`-SAVE-POINT-RECONCILER` + the orchestrator arc); LINEAR child with nested sub-agent (deeper recursion); the ORCHESTRATOR analogue (`B-FANOUT-CRASH-RESUME-ORCHESTRATOR-MAYBE-RAN-SUBAGENT`, builds on this mechanism).
- **STOP**: if [P1-b] or the witness surfaces a semantic that needs an operator gate, or the build can't land sound this iteration → leave registered + reschedule once (the branch is the durable checkpoint). Do NOT fix-forward a half-mechanism (E1 has no consumer without the full recovery — `[[wired-handler-unreachable]]`).

## At-most-once invariants

- Per-branch key-bind unchanged; ABORT run-level-terminal; absent resolution re-pauses INERT.
- Deterministic child key collision-free for the DAG (parent_idempotency_key encodes run+step+branch); child-workflow-id swap = accepted parity (per-child at-most-once).
- Non-recoverable child → seed=None → fresh uuid → pre-existing behavior (no regression); fail-closed at the fan-out classifier.
- The dispatch-marker recoverability is the DISPATCH-TIME value (changed-manifest guard); resumed re-check is the [P1-b] half; require BOTH.
