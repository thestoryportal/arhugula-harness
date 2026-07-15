# merge-gate audit log

Append-only. One entry per gated PR — see `.claude/skills/merge-gate/SKILL.md`.

---

## PR #1011 — feat(cp): B-31 resume guard validates paused-child workflow identity
Branch: feat/b31-paused-child-workflow-id-guard · Date: 2026-07-15

**Round 1:**
- Concurrency: APPROVE
- Spec-conformance: APPROVE
- Test-witness: BLOCK — byte-compat drop-when-None strip for `child_workflow_id` had zero test coverage, unlike the `synthesis_step_id` precedent it mirrors.

**Fix applied:** added `test_paused_child_absent_workflow_id_byte_compat_hash`, mutation-probed (confirmed fails when the strip is disabled, restored). Also backfilled `pr: "#PENDING"` → `"#1011"` in forward-register.yaml (spec-conformance round-1 minor note).

**Round 2 (final, cap reached):**
- Concurrency: APPROVE
- Spec-conformance: APPROVE
- Test-witness: APPROVE

**Outcome:** All-approve → merged without HIL per standing CI-green directive.
