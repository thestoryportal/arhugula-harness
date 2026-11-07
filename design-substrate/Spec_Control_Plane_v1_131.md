# Spec: Control Plane — v1.131 (PROPOSED delta over cleared v1.130)

*Delta-only file. One amendment site: C-CP-25 §25.11/§25.15/§25.2, the typed resume refusal. Every
other v1.130 and earlier C-CP-01 … C-CP-29 term remains in force. No `RunStatus` value, pause-snapshot
hash byte or fail-class prefix is added or changed.*

**Status: PROPOSED — not cleared.** No clearance marker, artifact-head row or pointer is filed by this
draft.

**Lineage:** folded onto cleared head v1.130 (`.harness/clearance/Spec_Control_Plane-v1_130-cleared-2026-11-05.md`)
by the integration lead's scope and numbering decision (LIT `arhugula-harness-trial-193` `cmt-7836db07-b27b-4248-849b-50101a522c0e`).
This is the former Proposed v1.128 with its semantics unchanged; it was drafted over cleared v1.124, whose
§0.2–§0.4 terms it extends. Slots v1.125 … v1.128 are not ratified and are not heads; this delta neither
revives nor amends them. Cleared v1.129 (C-CP-28 run-owned burden ledger and evaluation binding) and
v1.130 (§25.11.1 orchestrator worker selection) amend no site amended here; their terms are preserved.
The paired Runtime fold is Proposed v1.142 / U-RT-159; Runtime A5 v1.135 stays Proposed and unfolded.
Whether the Runtime folds affect CP contracts in meaning is not judged here.

**Authority:** A4 typed-refusal arc (LIT `arhugula-harness-trial-193` `cmt-7d8db0b5-6fe0-4f33-8529-9f1c9dd5e821`), independent
design GO `.harness/review-evidence/a4-contract-authority/a4-opus-design-review.md`; fork record
`.harness/class_1_fork_a4_typed_resume_refusal.md`.

## §0 Change-note (v1.130 → v1.131)

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
   of the reasons of every refusal recorded before the barrier ended, and the OR of their signing
   facts, and a fail class rendered from that same value:
   `<family>-child-resume-refused (<sorted reasons>[; audit-signing-failed])` (v1.124 §0.3 format).

### §0.5 At-most-once and recorded-before-the-barrier limits (RESTATED)

- **At the origin.** The refused descendant ran no step.
- **At an intermediate ancestor.** Siblings already dispatched in the same resume may have run and
  completed effects, under the existing barrier terms (v1.124 §0.4). The returned FAILED result
  therefore cannot certify that no effect completed below it.
- **Propagation is limited to recorded refusals.** An ancestor's run ends FAILED with this refusal,
  and no new pause capture, only when the refusal was recorded before that ancestor's owning barrier
  ended. The v1.124 §0.4 order is preserved without exception: under `proceed`, a refusal still in
  flight when the barrier deadline cancels its branch is not recorded, and the run is PARTIAL with no
  `resume_refusal` and no fail-class suffix, even though the refusing child never ran. Nothing from
  that branch propagates further. The result is not a complete record of refusals, and this delta
  does not promise late-refusal capture.
- **The root claim.** The root record is consumed by its started claim, so a second resume of it is
  claim-refused (Runtime C-RT-06; not re-specified here).

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
