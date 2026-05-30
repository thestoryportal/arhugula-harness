---
artifact: design-substrate/Spec_Control_Plane_v1_28.md
version: v1.28
cleared_at: 2026-05-29T21:30:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_2_fork_audit_stub_timestamp_universal_fix_plus_per_tier_annotation.md
  - PR # (this PR)
merge_commit: (pending)
reviewer_chain:
  - advisor 51st application (multi-site-pattern + per-tier-carve-out framing caught pre-substantive)
  - operator AskUserQuestion ratification 2026-05-29 Q-set Q1=(D) hybrid disposition
  - empirical orientation against `harness-cp/src/` + `harness-runtime/src/` for 3 composer construction sites
  - ADR-D5 §1.4 direct read for tier-conditional spec authority
supersedes: Spec_Control_Plane-v1_27-cleared-2026-05-29.md
---

# Clearance — `Spec_Control_Plane_v1_28.md`

v1.28 is a surgical amendment at v1.27 §16.5.6 extending the audit-half stub annotation with NEW §16.5.6.X per-tier-conditional stub field disposition. The amendment closes the universal `timestamp = ""` placeholder at all 3 sibling composer construction sites (`per_step_override_evaluator.py:225-231`, `sub_agent_gate_level_descent.py:199-206`, `hitl_gate_composer.py:713 + :753-762`) via composer-site clock per Q3=(a) precedent established at v1.25 §16.5.4, and annotates `prior_event_hash` + signing as canonical end-state at solo-developer tier per ADR-D5 §1.4 row 1 ("no hash chain required by default ... no signing key required"). v1.27 single-site framing at `emit_override_audit_entry` is superseded per multi-site empirical orientation.

Cleared via Reading (D) hybrid disposition operator-ratified at AskUserQuestion 2026-05-29. Team-binding+ tier closure (CP-audit chain state holder + threading + signing wiring per ADR-D5 §1.4 rows 2-3) carries forward as bounded-residual per X-AL-2 — operator-deployment-time opt-in pattern mirroring AS-8d batch-31 + OD-5 batch-32 + OD-6 batch-33 sub-species 7.deployment-time-opt-in-gate. The `override` + `actor` inputs at `emit_override_audit_entry` remain ignored at v1.28 per the v1.27 framing preserved verbatim — C-CP-16 §16.2 audit-entry shape does not include an `actor` field; `override`'s fields surface at the caller's `StepEffectiveBinding`, not into the audit entry.

Phase 7 consumers may rely on v1.28 as canonical until a successor marker is filed. Solo-developer tier (v1.6 MVP default) is functionally complete at HEAD post-v1.28 apply (timestamp populated; sentinel `prior_event_hash` canonical per ADR-D5 §1.4 row 1; no signing required). Team-binding + multi-tenant-compliance tiers remain PARTIAL with explicit deferral anchor at §16.5.6.X — operator binding to those tiers triggers the follow-on apply-pass arc.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
- 2109/2109 tests pass + 10 skipped (was 2090 at v1.27; +19 net).
- ZERO cross-axis cascade verified at design-substrate/ grep (intra-CP-axis + read-only ADR-D5 §1.4 anchor citation).
