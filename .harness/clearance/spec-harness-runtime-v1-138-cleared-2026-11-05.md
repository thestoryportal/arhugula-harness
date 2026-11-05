---
artifact: design-substrate/Spec_Harness_Runtime_v1_138.md
version: v1.138
cleared_at: 2026-11-05T04:34:19Z
clearance_status: cleared
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - ".harness/class_1_fork_validator_run_binding.md"
  - "LIT arhugula-harness-trial-193.4h4 cmt-f47c682d-6ea5-4d9d-97c1-8d5b5f35531a (Option A selection)"
  - "LIT arhugula-harness-trial-193.4h4 cmt-06b3e823-dbec-4549-92c4-049de48f9daa (Buford ratification of exact H d2bacef40d8b4d5755da115a6cde87da5f04c534, tree ab3257e3)"
merge_commit: "pending (bundled with the 4h4 source correction under claim cmt-90deb2e0; no main landing claimed)"
reviewer_chain:
  - "Independent Codex review NEEDS CORRECTION (F3) of fcbfd27e, reviewer implementer 01a1a9cc: LIT cmt-c8295223-8d1d-4de0-acaf-d07c5b9ac67d"
  - "Independent Codex affected-delta GREEN of fcbfd27e..d2bacef4, reviewer implementer 01a1a9f5: LIT cmt-e1383916-8a8d-4e75-bdba-64e21120e36e"
  - "Buford integration-lead ratification cmt-06b3e823; profile-coder applied this marker as the delegated mechanical apply, which Buford verifies before landing"
supersedes: spec-harness-runtime-v1-137-cleared-2026-11-04.md
---

# Clearance — Runtime v1.138

This marker clears C-RT-23 §14.13.8 for source consumption: the stage-4 factory returns the CP async Protocol instance, the MCP `run_workflow` ingress opens one binding per invocation (fresh at zero on resume), sub-agent dispatch opens one child binding per child execution from `step_context.validator_run`, and the child runner forwards its required `validator_run` argument to `execute_workflow_at_depth`. §14.13.9 fixes the witnesses and mutants the source correction must carry.

The Proposed A5 (v1.135) and A4 (v1.136) deltas are not cleared here. This marker accepts no implementation. Source correction review, PR CI, main landing, post-main CI and installed acceptance remain owed; B7 acceptance/exposure and the cross-trust palette gap at `workflow_driver.py:6047` stay unaccepted.
