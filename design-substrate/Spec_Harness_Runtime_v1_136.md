# Spec: Harness Runtime — v1.136 (PROPOSED delta over cleared v1.133)

*Delta-only file. One amendment site: C-RT-17 §14.7.2 step 7, the FAILED row of the sub-agent
dispatch result mapping. Every other v1.133 and earlier term remains in force.*

**Status: PROPOSED — not cleared.** No clearance marker, artifact-head row or pointer is filed.

**Lineage (pending fold):** grounded on cleared v1.133. v1.134 (A3 Ollama MCP loop and post-effect
fence; on main through PR #1633, `763e726585fced31f7c768ee7f503da1955773fd`) and v1.135 (A5 Codex read boundary; on main through PR #1635, `01cb8d17b18d7d3b531a75d29d778781f3ac03d1`) are separately PROPOSED and not cleared; v1.133 remains the cleared head. Root settled the Proposed fold order A3 (v1.134, U-RT-157) → A5 (v1.135, U-RT-158) → A4 (this v1.136, U-RT-159). This delta does not overlap their
amendment sites and must be folded after them before any clearance is filed. Exact authority identifiers are in the fork record.
Authority: CP v1.128 §0.3–§0.4 (proposed, same arc); fork record
`.harness/class_1_fork_a4_typed_resume_refusal.md`.

## §0 Change-note (v1.133 → v1.136)

### §0.1 C-RT-17 §14.7.2 step 7, FAILED row (AMENDED)

When the child workflow returns `RunStatus.FAILED`:

1. **With `resume_refusal`.** The dispatcher composes the same best-effort audit as the existing
   raised-refusal path, then raises `ChildResumeRefusedError` carrying the child's complete
   `ResumeRefusal` (every reason, the signing fact). If audit signing fails under fail-closed, it
   raises `RefusedChildAuditSigningError` carrying the complete refusal with `audit_signing_failed`
   true, chained to the signing failure. It never raises `PostEffectAuditSigningError` for a refusal:
   no child effect completed.
2. **Without `resume_refusal`.** Unchanged: `SubAgentChildFailedError` (and, under a fail-closed signing
   failure, the existing `PostEffectAuditSigningError` carrier). A fail class that merely contains a
   refusal reason's text is not a refusal.

The existing raised-refusal arm now forwards the complete refusal (not a single reason) into
`RefusedChildAuditSigningError`. Cancellation and dispatch-fence `BaseException` signals are untouched.

### §0.2 Observable consequence

A leaf refusal two levels down ends the root FAILED with
`orchestrator-workers-child-resume-refused (hitl-gate-config-changed)` and `resume_refusal` set, no
new pause capture; an existing Runtime refusal (for example `claim-busy`) at depth 2 reaches the root
the same way. A grandchild that genuinely ran and failed keeps the existing semantics at every level.

## §1 Source, tests and evidence limits

Source: `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py`,
`audit_signing_errors.py`. Tests: `harness-runtime/tests/test_child_resume_refusal_propagation.py`.
Source evidence only, from unlanded source preparation: the A4 changes to these modules and both A4 test files are not on main. The public `api.resume` durable-claim integration (second resume claim-refused) is exercised by a source test committed at a preparation head, `harness-runtime/tests/test_public_nested_resume_refusal.py`; its evidence limits are recorded in the fork record. Installed N1 remains a
separate consent-gated run.
