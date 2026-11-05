---
artifact: design-substrate/Spec_Control_Plane_v1_129.md
version: v1.129
cleared_at: 2026-11-05T04:34:19Z
clearance_status: cleared
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - ".harness/class_1_fork_validator_run_binding.md"
  - "LIT arhugula-harness-trial-193.4h4 cmt-f47c682d-6ea5-4d9d-97c1-8d5b5f35531a (Option A selection)"
  - "LIT arhugula-harness-trial-193.4h4 cmt-06b3e823-dbec-4549-92c4-049de48f9daa (Buford ratification of exact H d2bacef40d8b4d5755da115a6cde87da5f04c534, tree ab3257e3, incl. StepExecutionContext.validator_run carrier and path amendment)"
merge_commit: "pending (bundled with the 4h4 source correction under claim cmt-90deb2e0; no main landing claimed)"
reviewer_chain:
  - "Independent Codex review NEEDS CORRECTION (F3) of fcbfd27e, reviewer implementer 01a1a9cc: LIT cmt-c8295223-8d1d-4de0-acaf-d07c5b9ac67d"
  - "Independent Codex affected-delta GREEN of fcbfd27e..d2bacef4, reviewer implementer 01a1a9f5: LIT cmt-e1383916-8a8d-4e75-bdba-64e21120e36e"
  - "Buford integration-lead ratification cmt-06b3e823; profile-coder applied this marker as the delegated mechanical apply, which Buford verifies before landing"
supersedes: spec-control-plane-v1-124-cleared-2026-09-25.md
---

# Clearance — Control Plane v1.129

This marker clears the ratified run-owned validator evaluation binding for source consumption: the per-execution `ValidatorBurdenLedger` replacing framework-instance burden state, `evaluate(..., burden=)`, `ValidatorRunBinding` as the only synchronous adapter with `open_validator_run` and `open_child`, the explicit driver `validator_run` argument, and the hash-inert `StepExecutionContext.validator_run` carrier of §28.11.5 with its declared `[LAW:types-are-the-program]` default-`None` exception.

Proposed v1.125–v1.128 are not heads and are not cleared here. This marker accepts no implementation. Source correction review, PR CI, main landing, post-main CI and installed acceptance remain owed; B7 acceptance/exposure and the cross-trust palette gap at `workflow_driver.py:6047` stay unaccepted.
