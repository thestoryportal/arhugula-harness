# Spec: Control Plane — v1.128 (PROPOSED delta over cleared v1.124)

*Delta-only file. One amendment site: C-CP-25 §25.11/§25.15/§25.2, the typed resume refusal. Every
other v1.124 and earlier C-CP-01 … C-CP-29 term remains in force. No `RunStatus` value, pause-snapshot
hash byte or fail-class prefix is added or changed.*

**Status: PROPOSED — not cleared.** No clearance marker, artifact-head row or pointer is filed by this
draft.

**Lineage:** grounded on cleared v1.124 (`.harness/clearance/spec-control-plane-v1-124-cleared-2026-09-25.md`).
Slots v1.125 … v1.127 exist only as historical drafts in preserved worktrees and are NOT ratified;
this delta neither revives nor supersedes them. Buford owns the version fold and numbering at filing.
The concurrent Proposed Runtime folds (A3 v1.134, A5 v1.135, A4 Runtime v1.136 / U-RT-159) change no CP spec or plan file. Whether they affect CP contracts in meaning is not judged here.

**Authority:** A4 typed-refusal arc (LIT `arhugula-harness-trial-193` `cmt-7d8db0b5-6fe0-4f33-8529-9f1c9dd5e821`), independent
design GO `.harness/review-evidence/a4-contract-authority/a4-opus-design-review.md`; fork record
`.harness/class_1_fork_a4_typed_resume_refusal.md`.

## §0 Change-note (v1.124 → v1.128)

### §0.1 The gap

A durable paused leaf that its own resume refuses (its applicable HITL gate configuration differs
from the capture) returns `FAILED` with a human fail class only. A parent's dispatch of that child
cannot tell it from a child that genuinely ran and failed, so under `cascade_policy = pause` every
ancestor records the branch as done and pauses; a later resume completes silently. A refusal returned
(not raised) by a middle fan-out is lost the same way one level up. v1.124 §0.2–§0.4 closed the
Runtime-raised set but said nothing about a refusal crossing more than one level.

### §0.2 C-CP-25 §25.11 (AMENDED) — the closed enumeration is ten values

`ChildResumeRefusal` adds `hitl-gate-config-changed`: the child was admitted, and its own resume found
its applicable HITL gate configuration differs from the capture, before any of its steps ran. The
other nine values and their spellings are unchanged.

### §0.3 C-CP-25 §25.2 (AMENDED) — the typed refusal on `RunResult`

- `ResumeRefusal` is a frozen value: a non-empty set of `ChildResumeRefusal` reasons and
  `audit_signing_failed: bool`. An empty reason set is invalid at construction.
- `RunResult.resume_refusal: ResumeRefusal | None`. It is non-None only when `status == FAILED`; any
  other status with a refusal is invalid at construction. It is `None` on every FAILED run whose own
  steps ran, whatever its fail-class text contains.
- `ChildResumeRefusedError` stores one `ResumeRefusal`. Its single-reason constructor
  `(reason, detail, *, audit_signing_failed)` remains; it also accepts a `ResumeRefusal`. `reasons`
  and `audit_signing_failed` are derived from the stored value; `reason` exists only for a single-reason
  refusal and raises for a multi-reason one (no reason is ever selected from a set).

### §0.4 Where the refusal is set (AMENDED)

1. **Pre-step guards.** The LINEAR, EVALUATOR_OPTIMIZER and DECENTRALIZED_HANDOFF resume guards that
   reject a changed HITL gate configuration return FAILED with
   `resume_refusal = {hitl-gate-config-changed}`, no step dispatched. Their fail-class text is unchanged.
2. **Fan-out gate-owning branches.** The PARALLELIZATION and ORCHESTRATOR_WORKERS resume-body checks
   that reject a gate-owning branch's changed configuration return the same refusal. The mismatch is
   typed at its origin; it is never derived from the fail-class text. Every other body mismatch
   (branch count, index, material diff) stays a plain named FAILED with no refusal (named follow-up).
3. **C-CP-25 §25.15 — refused-terminal fail-class rendering (AMENDED).** A PARALLELIZATION or
   ORCHESTRATOR_WORKERS run (and HIERARCHICAL_DELEGATION,
   which reuses it) ended by refused durable children returns FAILED with `resume_refusal` = the union
   of every recorded refusal's reasons and signing fact, and a fail class rendered from that same value:
   `<family>-child-resume-refused (<sorted reasons>[; audit-signing-failed])` (v1.124 §0.3 format).

### §0.5 At-most-once limit (RESTATED)

The refused descendant ran no step. At an intermediate ancestor, siblings already dispatched in the
same resume may have run, under the existing barrier terms (v1.124 §0.4). Every ancestor ends FAILED
with no new pause capture. The root record is consumed by its started claim, so a second resume of
it is claim-refused (Runtime C-RT-06; not re-specified here).

### §0.6 Preservation

`RunStatus`, every fail-class prefix and its rendering order, the snapshot hash, the v1.124 public
verifier, cascade-policy semantics for genuinely failed branches, and cancellation/fence signal
identity are unchanged.

## §1 Source, tests and evidence limits

Source: `harness-cp/src/harness_cp/workflow_driver_types.py`, `workflow_driver.py`. Tests:
`harness-cp/cp_tests/test_resume_refusal_propagation.py` (new),
`test_b104_child_resume_refusal_values.py` (ten values). Source/test evidence only; no installed or
live claim. These are unlanded source preparation: the A4 changes to both modules, the new test module and the
ten-value version of `test_b104_child_resume_refusal_values.py` are not on main, where that test still
asserts the nine pre-A4 values. The preparation commits are recorded in the fork record. The installed N1 witness run remains a separate consent-gated obligation.
