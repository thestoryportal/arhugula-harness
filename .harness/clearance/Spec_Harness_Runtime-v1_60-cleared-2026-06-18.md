---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.60
cleared_at: 2026-06-18T21:30:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_b_effect_fence_at_most_once_execution.md
  - .harness/beyond-mvp-capability-boundary-ledger.md (line 49 — B-EFFECT-FENCE)
  - .harness/r-fs-1-e-impl-3b-finding.md (§4 F-2 — the surfacing finding)
merge_commit: pending (R-FS-1 B-EFFECT-FENCE bundled-absorption PR)
reviewer_chain:
  - advisor (full-transcript) — non-vacuity-FIRST (prove the fence is reached on a legitimate resume nothing else prevents, before authoring the contract); the durable-resume scoping that collapses the C10⊥C11 fence-scope tension; suppress-not-replay (defer replay to B-ENGINE-OUTPUT-REPLAY); the RESERVE-is-the-new-piece / COMMIT-is-the-existing-ledger-entry decomposition
  - out-of-family Codex (pre-merge, on the diff)
  - impl-time grounding pass (worktree off origin/main f2897fb5)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.60`

v1.60 adds a **NEW contract §14.22 C-RT-31 `RuntimeEffectFence`** — a hand-rolled (I-6) durable, operator-opt-in **effect-boundary fence** at the `RuntimeToolDispatcher` `call_tool` sink that guarantees **at-most-once EXECUTION** of a non-idempotent tool-step effect across durable-engine retries and resumes. R-FS-1 standalone `B-*` arc `B-EFFECT-FENCE`, spine ledger line 49 (`design-fork-first per X-AL-3, since a sink-fencing surface is new`; surfaced as the E-impl-3b finding F-2). Closes the floor-(ii) "at-most-once execution" gap the durable engine classes advertise but did not deliver — the U-RT-123 reconciler CAS guarantees at-most-once *claim of a revision*, not at-most-once *execution* of the steps a resume re-runs.

**No operator gate — additive + operator-opt-in.** Gated on a NEW `RuntimeConfig.effect_fencing: bool = False`; default `False` → no fence constructed → byte-identical to pre-v1.60. The `StepDispatcher.dispatch` signature is UNCHANGED (the fence is read off the dispatcher's construction reference + keys on the existing `step_context.parent_idempotency_key`). The one nameable C10⊥C11 fence-scope tension (uniform / per-tool-classified / opt-in) is probe-resolved by scoping to "tool steps under a durable/resumable engine" — no `ToolContract` classification field, no AS fork → advisor, not council. No committed invariant sacrificed (I-6 hand-roll + ADR-F2 single-write honored; the fence is a separate store, COMMIT = the existing per-step ledger entry).

**At-most-once, NOT exactly-once (the honest residual — mirrors the reconciler).** `try_reserve(idempotency_key)` crash-atomically claims the effect before `call_tool`; the first dispatch wins (fires), any re-dispatch loses (resume re-dispatch of an effected-but-uncommitted step, OR an in-process retry — the fence error fail-fasts, not retried). A lost claim raises `EffectFenceReservedUncommittedError` → fail-closed to §22.1 rather than risk a double-execution. The genuine fire-then-crash-before-commit window is ambiguous, so the conservative fail-close is the honest answer.

**Genuine non-vacuity (the live trap — cf. B-TOOL-GATE #653 wired-but-production-dead).** Proven by-execution with NO proxy: a real `RuntimeToolDispatcher` re-dispatching the same effect fires the underlying counting MCP tool EXACTLY ONCE; a NEGATIVE CONTROL proves double-fire without the fence; a fresh-dispatcher-over-the-same-on-disk-fence-dir test is a genuine restart (crash-then-resume); the driver hands the sink a byte-identical key on the real `execute_workflow` resume path.

## Notes

- Scope: ONLY §14.22 (the new contract); all of §9 / §14.x / §14.20 / §14.21 + the existing `RunResult` fields are PRESERVED VERBATIM. No §5.2-hash / IS-spec / CP-spec / OD-spec / ADR change; the fence claim is a side file, not a state-ledger entry. The interim fail-close (FAILED RunResult) + the §22.1 HITL routing / suppress-and-continue is the registered `B-EFFECT-FENCE-HITL-ROUTE` follow-on (§14.22.7).
- Three follow-ons registered (§14.22.7): `B-EFFECT-FENCE-DURABLE-AUTO`, `B-EFFECT-FENCE-PER-TOOL`, `B-EFFECT-FENCE-HITL-ROUTE`.
- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
