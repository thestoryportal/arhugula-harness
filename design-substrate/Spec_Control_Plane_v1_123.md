# Spec: Control Plane — v1.123 (delta over v1.122)

*Delta-only file. C-CP-25 §25.11 is amended below: the Control Plane's own refusal types and
their terminal handling in both fan-out families, and the order of the three run-level decisions
under the `proceed` cascade policy. Every other v1.122 and earlier C-CP-01 … C-CP-29 term remains
in force. No contract number, `RunStatus` value or pause-snapshot hash byte is added or changed.*

**Status: DRAFT — not cleared. No clearance marker is filed and no artifact head is regenerated.**

**Filed:** 2026-09-25

**Authority:** ratified B-104 at-most-once durable HITL terms, recorded in
`evaluation/production-readiness-arch/b104-operator-amendment-proposal-1.md`. Source: the
isolated Control Plane correction at `3b5100052d82eda703e0866ab7aaf40e5ce114b5`, independently
source-cleared by Opus (`evidence-b104-refusal-deadline-opus-review-1/SHA256SUMS`, SHA256
`c6a5304cf43693211e5e8359288d7e409e68a875a9b266d703eb47782c36bb6e`), whose review names the limit stated
in §0.5. The Runtime v1.129 draft HOLD (`evidence-b104-task4-runtime-v129-review-opus-1/SHA256SUMS`, SHA256
`d84dd24ff65ff4bc0b8d166e70a3b8f63f827f9a1670dd661696aaf593c266a2`) found that these Control-Plane terms had no
Control-Plane text.

**Predecessor:** `Spec_Control_Plane_v1_122.md`

**Paired Runtime successor:** Runtime v1.129, revised to cite this delta, is owed. This delta does
not admit a durable child resume and does not install the Task 5 claim/`started` gateway.

## §0 Change-note (v1.122 → v1.123)

### §0.1 The gap

v1.122 §0.4 says a legacy ref-less child is not silently promoted to a durable exact record and that
"Runtime determines whether it can be resumed under the Task 4 refusal rule." It never states what the
Control Plane does when Runtime refuses. The refusal's value set, its error type and its terminal
handling existed only in source, and the Runtime draft called them "CP-owned" with no CP text behind
the claim. Independent review also found that, under `proceed`, a barrier deadline was decided
before the refusal check, so a refusal already recorded could be degraded into PARTIAL without its
reason. The source was corrected at `3b51000`; this delta is the contract for it.

### §0.2 C-CP-25 §25.11 (AMENDED) — the refusal types

`ChildResumeRefusal` is a closed string enumeration with exactly six members, spelled as follows
(machine-read): `missing-ref`, `unreadable-record`, `snapshot-mismatch`, `depth-mismatch`,
`gateway-not-installed`, `workflow-mismatch`. The Control Plane treats every member alike. When each
is raised, and what Runtime checks first, is Runtime's contract (Runtime v1.129). Adding a member is a
contract change here, because the value is written into a fail class (§0.3).

`ChildResumeRefusedError(reason, detail="", *, audit_signing_failed=False)` states that a durable
paused child was refused before any of its steps ran. It carries `reason` (a `ChildResumeRefusal`),
`detail` (human text that never enters a fail class) and `audit_signing_failed`.
`audit_signing_failed` is a plain boolean field defined by the Control Plane so the terminal fail
class can render it without the Control Plane importing the audit-signing error family. Runtime sets
it `True` when it also failed to sign the audit record for this refusal under fail-closed (Runtime
v1.129); the Control Plane only renders it.
The error is defined in the Control Plane so the fan-out barrier catches it typed. Within that run, a refused
child is never retried, re-dispatched as fresh work, or re-captured as a pause. A later resume of the
unchanged parent pause (§0.3 leaves it the latest durable record) presents the child again, and Runtime
verifies and admits or refuses it anew (Runtime v1.129; Task 5). Every refusal
raised inside a fan-out dispatch is caught at the dispatch boundary and recorded under its branch
ordinal before the exception continues, so the terminal decision below reads the refusals recorded so
far.

### §0.3 C-CP-25 §25.11 / §25.15 (AMENDED) — the terminal outcome and its fail class

When the run's refusal record is non-empty at the run's terminal decision, the run returns
`RunStatus.FAILED` with these observable properties: `pause_snapshot` is `None`; no pause capture is
made and none is written to the durable journal, so the prior durable pause stays the only record;
`final_state` and `partial_state` are both `None` (no partial output is salvaged; the new tests
assert `final_state`, and `partial_state` is source-traced); no refused child is dispatched again; and the
ledger entries already buffered by the fan-out's branches are still written. The `fail_class` is

`<family>-child-resume-refused (<reasons>[; audit-signing-failed])`

where `<family>` is `parallelization` for PARALLELIZATION peer fan-out and `orchestrator-workers` for
the worker fan-out (ORCHESTRATOR_WORKERS, and HIERARCHICAL_DELEGATION, which runs through it).
`<reasons>` is the set of distinct `reason` values across the recorded refusals, sorted ascending by
string value and joined with `"; "`. If any recorded refusal has `audit_signing_failed` true, the
literal `audit-signing-failed` follows as the last element (it is appended, not sorted among the
reasons). Nothing else — no detail text, branch id or ordinal — appears. Examples:
`parallelization-child-resume-refused (unreadable-record)` and
`orchestrator-workers-child-resume-refused (snapshot-mismatch; unreadable-record; audit-signing-failed)`.

### §0.4 C-CP-25 §25.15 (AMENDED) — order of decisions under `proceed`

Under the `proceed` cascade policy the parent decides, in this order, from state at the moment the
fan-out's barrier ends (by completion or by deadline):

1. **A recorded refusal → FAILED.** If any refusal is recorded, the outcome is §0.3's, whether or not the
   barrier deadline also struck. This is checked before the deadline.
2. **Otherwise the deadline → PARTIAL.** If the deadline struck and no refusal is recorded, the run is
   `PARTIAL` with `fail_class=None` and salvage enabled, exactly as before this delta.
3. **Otherwise a paused child → FAILED, not resumable.** If a child paused and no deadline struck and no
   refusal is recorded, the run is `FAILED` with
   `<family>-child-paused-not-resumable-under-proceed` (`parallelization` / `orchestrator-workers`).
   A paused child stashed before the deadline struck is decided by step 2 (PARTIAL), which is unchanged.

Otherwise the existing `proceed` outcomes apply (`PARTIAL` if any branch failed, else `SUCCESS`).

**Ledger terminals.** The refused branch records no terminal of its own at refusal; the terminal
synthesis at the run's exit records it as `cancelled`. A sibling still in flight when the deadline cut
it has already recorded `timed_out` at its cancellation. A branch that never dispatched records
`cancelled`. Where no sibling was cut, no `timed_out` is written.

**`cascade-cancel` and `pause`.** These are not changed by this delta. Source-traced by independent
review: on both, after the fan-out barrier — including after a barrier deadline — a recorded refusal
forces `FAILED` with §0.3's fail class and without salvage, before the effect-fence and cascade-policy
branching, so a refusal takes precedence over the deadline there too and nothing re-pauses. Refusal
tests on the `pause` tier exist in the refusal test file (the parent-fails-terminally case and the
in-flight-cancellation case) but have no passing run, because that file stalled at base and head.
`cascade-cancel` has no test. This behaviour is stated from the source trace, not from a passing test.

### §0.5 What "recorded" means, and what is not claimed

The precedence of §0.4 step 1 and the `audit-signing-failed` suffix apply only to a refusal **recorded
before the barrier ends**. A refusal is recorded by its branch on the fan-out's event loop, and when
the barrier ends that loop is stopped, so a branch that has not yet recorded cannot record afterward.
If the deadline cancels a refusing branch before it records — for example while Runtime is still inside
its best-effort audit signing for that refusal — the branch is recorded `timed_out`, the run is
`PARTIAL` under step 2, no refusal reason appears, and no `audit-signing-failed` suffix appears even
if that signing attempt would have failed. The child never ran in that case either. Consequently this
delta does not say every refused attempt is reported in the run result, and it does not make the
result's `fail_class` a complete record of refusals. It says only: a refusal recorded before the
barrier ends is never degraded into `PARTIAL` or `SUCCESS`, and a refused child's steps never run.

The at-most-once statement is therefore exact and narrow. Refusal precedes any step of the child (a
Runtime obligation, Runtime v1.129), and CP admits no path from a refusal to a dispatch, a re-pause or
a capture of that child. The Control Plane supplies neither recency, a claim, a lease nor a `started`
barrier; those remain the Task 5 gateway's.

### §0.6 Preservation

| Element | Disposition |
|---|---|
| v1.122 capture, depth, exact record ref and child-ref carrier terms | Preserved unchanged |
| `RunStatus` values, contract numbers, pause-snapshot and hash bytes | Unchanged |
| `proceed` deadline → `PARTIAL` when no refusal is recorded; stash-then-deadline → `PARTIAL` | Preserved |
| `cascade-cancel` and `pause` exits | Not changed; refusal precedence source-traced, `pause` tests have no passing run, `cascade-cancel` untested (§0.4) |
| Task 5 claim, lease, `started`, worker handoff, installed acceptance | Outside this delta |

## §1 Acceptance for the paired implementation, and the evidence limits

The corrected source is `3b51000`. Provider-free tests that ran green there are cited by file and
name: `test_proceed_deadline_preserves_a_recorded_child_refusal` (both fan-out families, with and
without `audit-signing-failed`; a refusing worker and a sibling held in flight, barrier shortened to
0.5 s; asserts FAILED, the exact fail class, no `final_state`, no pause snapshot, no capture, and both
workers dispatched) in `harness-cp/tests/test_b104_task4c_child_resume_refusal.py`, and the two
deadline controls in `harness-cp/tests/test_workflow_driver_parallelization.py` and
`harness-cp/tests/test_workflow_driver_orchestrator_workers.py` (PARTIAL and a tripped cancel token
when no refusal is recorded). The order and format above are read from
`harness-cp/src/harness_cp/workflow_driver.py` (the shared fail-class builder and both `proceed`
decision blocks) and `harness-cp/src/harness_cp/workflow_driver_types.py` (the enumeration and error).

Not established: the full refusal test file stalled at both base and head, so it has no passing run;
no wider Control Plane suite was run. The ledger terminals in §0.4 and the deadline-before-recorded
outcome in §0.5 are stated from a source trace and are asserted by no test that ran. The tests refuse
on a first dispatch, not on a Runtime resume of a real durable pause. Recording before the deadline
relies on the 0.5 s margin, which can only fail spuriously on a slow machine, never pass falsely.
On `cascade-cancel` and `pause` the refusal outcome is source-traced only: the `pause`-tier
refusal tests sit in the stalled file (no passing run) and `cascade-cancel` has no test. `partial_state`
being `None` on a refusal is likewise source-traced; the new tests assert `final_state`. No result here is an installed, live-model or RC
witness. Independent review of this delta and Runtime v1.129 clearance are required before local RC
integration.
