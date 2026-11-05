---
artifact: design-substrate/Spec_Control_Plane_v1_130.md
version: v1.130
cleared_at: 2026-11-05T08:09:07+00:00
clearance_type: Phase-7-absorbed-via-architect-recommendation
back_reference:
  - "LIT arhugula-harness-trial-193.qrf cmt-35ae37ac-54fe-4706-9274-0219dfad7e2b"
  - "Independent contract GREEN cmt-1ced7828-9dc5-48ec-b0f0-39c800d46282"
merge_commit: pending
reviewer_chain:
  - "profile-coder contract authors bf1a145e, e54b8a39 and db8fc857; all findings F1-F4 and spent passes retained"
  - "implementer independent contract review: RED cmt-c8015364 and cmt-cc86991a (01a1aa9f), RED cmt-c6a964c1 and final GREEN cmt-1ced7828 (01a1aaa9)"
  - "Buford integration lead 01a1aabd ratification cmt-35ae37ac on frozen 78f6dcb7963411a1508794f2d96d6a45a650a021, tree 2e6c85ef7446fcc9d6ede57373cf1de099f2154f; attribution correction cmt-c602e272"
---

# Clearance — Control Plane v1.130

Control Plane v1.130 is cleared for the bounded dynamic-orchestration implementation under Trial193.qrf. The independently reviewed contract adds C-CP-25 §25.11.1: an `ORCHESTRATOR_WORKERS` manifest may declare `LEAD_PLAN`, under which the orchestrator output's worker plan selects workers from the declared pool, orders them and supplies their briefs. Invalid plans dispatch nothing, the recorded selection and briefs persist across pause and crash resume, and orphan markers refuse. `HIERARCHICAL_DELEGATION` inherits the rule at every level. `DECLARED_POOL` behavior is unchanged.

The normative body reviewed at `78f6dcb7963411a1508794f2d96d6a45a650a021` is the accepted text. Its PROPOSED banner is superseded by the ratification above and is updated mechanically by the author. This marker is prepared before merge and establishes contract clearance only. Source review, the W1–W10, W6b–d, W7a/b, W8b and RW1/RW2 conformance witnesses, required exact-candidate CI, safe merge and own-main CI remain owed.

B7 retained storage remains unselected and unbound. Installed acceptance, resume exposure, cross-trust, Source09 and unrelated repair holds remain in force. The implementation owner is profile-coder under claim `cmt-9e26c9ad`; Runtime owns the later installed witness after its prerequisites are satisfied. The LLM_CALL structured worker_plan producer stays visible in qrf scope with its disposition owned by Buford (`cmt-c602e272`); this clearance does not deliver it.
