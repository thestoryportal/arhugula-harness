# Spec: Harness Runtime — v1.142 (delta over cleared v1.141)

*Delta-only file. Amendment sites: the `RT-FAIL-SUB-AGENT-CHILD-FAILED` rows in the C-RT-17
§14.7 failure-mode taxonomy and the C-RT-14 §14 Runtime-local fail-class taxonomy; the composer
§14.7.2 step 7 FAILED mapping seam; and items (b) and (c) of the C-RT-24 §14.14.8 paragraph
"Refusal typing and precedence (AMENDED at v1.130)" (`Spec_Harness_Runtime_v1_132.md:6512`, not
amended by v1.133 through v1.141). Every other v1.141 and earlier term remains in force. Cleared predecessor files
are not edited.*

**Status: CLEARED 2026-11-07 — ratified by the integration lead at LIT `cmt-756042fc-eb54-4a73-b152-61488707f1a2`
on the frozen reviewed body `745f234f0000e9abcd0f87624e64883bd57e1494` (independent contract GREEN
`cmt-553de0a0-3dcd-4af9-b87e-dd9987bad06e`); clearance `.harness/clearance/spec-harness-runtime-v1-142-cleared-2026-11-07.md`.
Contract clearance only; source conformance, CI, landing and installed acceptance remain owed.**

**Lineage:** folded onto cleared head v1.141 (`.harness/clearance/spec-harness-runtime-v1-141-cleared-2026-11-05.md`)
by the integration lead's scope and numbering decision (LIT `arhugula-harness-trial-193` `cmt-7836db07-b27b-4248-849b-50101a522c0e`).
This is the former Proposed v1.136 (U-RT-159) with its semantics unchanged; it was drafted over cleared
v1.134 (A3). Cleared v1.137 through v1.141 amend none of its sites: v1.137 (root resume supersession and
its refusals), v1.138 (validator lifetime), v1.139 (skills), v1.140 (§14.7.2 step 1 effective brief; this
delta amends the step 7 FAILED mapping, not step 1) and v1.141 (daemon MCP resume). Their terms are
preserved. v1.137 recorded the fold order A3 → A5 → A4 → v1.137; this decision instead folds A4 after
v1.141. A5 v1.135 (U-RT-158) stays Proposed and unfolded; this delta does not overlap its C-RT-05 site,
and the actual A5 interfaces are bound before an affected A4 candidate is frozen or integrated. Exact
authority identifiers are in the fork record; source and version dependencies are in
`.harness/a4_contract_authority.md`.
Authority: CP v1.131 §0.3–§0.4 (proposed, same arc); fork record
`.harness/class_1_fork_a4_typed_resume_refusal.md`.

## §0 Change-note (v1.141 → v1.142)

### §0.1 C-RT-17 / C-RT-14 failure taxonomy rows and §14.7.2 step 7 (AMENDED)

<!-- [APPSPEC:errors-are-api] The caller must distinguish a refused child from a child that ran and failed. -->
**Taxonomy rows (replacement text).** In both taxonomies the `RT-FAIL-SUB-AGENT-CHILD-FAILED` row's
trigger is narrowed to: "child sub-workflow's terminal `RunResult.status == FAILED` with
`resume_refusal` `None`, after the composer's child-runner invocation (§14.7.2 step 6)". Its
behavior column is unchanged. A FAILED child with `resume_refusal` set no longer enters this row:
the composer raises the typed refusal of item 1 below, and the Control Plane's
`ChildResumeRefusedError` handling (C-CP-25; CP v1.131) owns the run outcome. This delta adds no
`RT-FAIL-*` class.

This Proposed delta also supersedes
§14.7.2 step 7's historical "do NOT raise" clause for FAILED children: set
`subagent.result_status = "failed"`, perform the applicable best-effort audit, then raise the
typed error below. The SUCCESS and DRAINED mappings are unchanged. Resolving that contradiction
is part of the pending Proposed fold; it does not assert that cleared v1.132 through v1.141 already
resolved it or that this delta is cleared.

When the child workflow returns `RunStatus.FAILED`:

1. **With `resume_refusal` (the returned arm).** The child workflow returned a completed result.
   Steps of its own descendants or siblings may have completed effects before the refusal was
   recorded (CP v1.131 §0.5), and the dispatcher cannot tell whether any did. It composes the same
   best-effort audit as the raised arm, then raises `ChildResumeRefusedError` carrying the child's
   complete `ResumeRefusal` (every reason, the signing fact). If audit signing fails under
   fail-closed (`AUDIT_SIGNING_HARD_FAILURES`), it raises `RefusedChildResultAuditSigningError`,
   chained to the signing failure. This carrier is both:
   - a `ChildResumeRefusedError` storing the complete `ResumeRefusal` with `audit_signing_failed`
     true, so the Control Plane records it as this child's refusal exactly as it records
     `RefusedChildAuditSigningError`; and
   - a `PostEffectAuditSigningError` with `effect_class = sub-agent-result`, `result` = the child's
     `RunResult` and a `result_ref` the raise site resolves through the protected result store
     under the owning tenant before constructing the carrier (C-RT-18 §14.8.11), as for the
     existing returned-FAILED carrier. The outermost Runtime dispatch boundary therefore reports
     the preserved result keyed by `result_ref` before the Control Plane sees the exception.

   It belongs to the typed signing family through both bases. It is never the refusal-only
   `RefusedChildAuditSigningError`, which would discard the completed result, never a plain
   `PostEffectAuditSigningError`, which would discard the typed refusal, and never
   `SubAgentChildFailedError`.
2. **Without `resume_refusal`.** Preserved genuine-failure behavior: `SubAgentChildFailedError`
   (and, under a fail-closed signing failure, the existing `PostEffectAuditSigningError` carrier).
   A fail class that merely contains a refusal reason's text is not a refusal.

**The raised arm.** When Runtime's child runner raises `ChildResumeRefusedError` before any step of
the child runs (for example a claim, start or verification refusal), no child result exists. That
arm keeps the refusal-only `RefusedChildAuditSigningError` under a fail-closed signing failure, now
carrying the complete `ResumeRefusal` rather than a single reason. Cancellation and dispatch-fence
`BaseException` signals are untouched on both arms.

### §0.2 Observable consequence

When a leaf refusal two levels down is recorded before each owning fan-out barrier ends, the root
ends FAILED with `orchestrator-workers-child-resume-refused (hitl-gate-config-changed)` and
`resume_refusal` set, and no new pause capture. An existing Runtime refusal (for example
`claim-busy`) at depth 2 reaches the root the same way. Under `proceed`, a refusal still in flight
when a barrier deadline cancels its branch is not recorded at that level: that run is PARTIAL with
no refusal carrier and no suffix, and nothing from that branch propagates further (CP v1.124 §0.4,
preserved by CP v1.131 §0.5). The refusing descendant ran no step; intermediate siblings may have.
A grandchild that genuinely ran and failed keeps the existing semantics at every level.

### §0.3 C-RT-24 §14.14.8 "Refusal typing and precedence", items (b) and (c) (AMENDED)

These items, as last amended at v1.130 and carried unchanged in cleared v1.132 through v1.141, are
superseded as follows. Items (a) and (d) are unchanged; (d)'s recorded-before-the-barrier limit
applies to both arms of §0.1.

- **(b)** The `ChildResumeRefusal` enumeration is the ten values of CP v1.131 §0.2: the nine named
  there before plus `hitl-gate-config-changed`. `ChildResumeRefusedError` stores one
  `ResumeRefusal` (CP v1.131 §0.3). The single-reason constructor
  `(reason, detail, *, audit_signing_failed)` remains, `reasons` and `audit_signing_failed` derive
  from the stored value, and `reason` is available only for a single-reason refusal. The fail-class
  rendering is CP v1.131 §0.4 item 3. The rest of (b), including terminal handling and the S1
  gateway phase mapping, is unchanged.
- **(c)** On the raised arm the carrier is `RefusedChildAuditSigningError` carrying the complete
  `ResumeRefusal`; its statement that no child effect completed now applies to the raised arm only.
  The returned arm follows §0.1 item 1.

## §1 Source, tests and evidence limits

Source: `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py`,
`audit_signing_errors.py`. Tests: `harness-runtime/tests/test_child_resume_refusal_propagation.py`.
Source evidence only, from unlanded source preparation: the A4 changes to these modules and both A4 test files are not on main. The public `api.resume` durable-claim integration (second resume claim-refused) is exercised by a source test committed at a preparation head, `harness-runtime/tests/test_public_nested_resume_refusal.py`; its evidence limits are recorded in the fork record. Installed N1 remains a
separate consent-gated run.

The preparation source implements the earlier returned-arm text, the refusal-only carrier. The
result-preserving `RefusedChildResultAuditSigningError` of §0.1 item 1, and witnesses that
discriminate it at the applicable source head, are owed source work. No current-head observation of
either arm is claimed.
