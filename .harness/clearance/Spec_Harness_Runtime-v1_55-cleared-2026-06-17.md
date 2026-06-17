---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.55
cleared_at: 2026-06-17T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc (additive C-RT-28 back-flow; paired with the operator-gated CP v1.39 StepKind extension)
back_reference:
  - .harness/class_1_fork_m_managed_agents_stepkind_c_rt_28.md
  - .harness/clearance/Spec_Control_Plane-v1_39-cleared-2026-06-17.md (the paired CP StepKind extension — the gated half)
  - .harness/beyond-mvp-capability-boundary-ledger.md (arc M spine registration)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - advisor (pre-substantive, full-transcript) — affirmed Option B; directed the §4.1.2 + PAUSED-landing verification before treating the StepKind extension as un-gated
  - operator ratification via AskUserQuestion 2026-06-17 (Option B; the gated half is the paired CP v1.39 StepKind extension)
  - standing FULL-SPEC operator directive 2026-06-12 (C-RT-28 additive back-flow pre-authorized)
  - out-of-family Codex review at the impl-diff PR (decorrelated; Slice 2+ diff)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.55`

v1.55 adds **§14.20 C-RT-28 `ManagedAgents` executable-consumer contract** (R-FS-1 arc M). It formalizes the already-built, R-820-live-proven carrier `harness-runtime/.../lifecycle/managed_agents.py` (`ManagedAgentsClientProtocol` + `AnthropicManagedAgentsClient` + the records + `managed_agents_runtime_span` + `ANTHROPIC_MANAGED_AGENTS_BETA`) and authors the missing production-wiring surface: a `ManagedAgentsStepDispatcher` (satisfying the CP `StepDispatcher` Protocol) bound to the NEW `StepKind.MANAGED_AGENTS` (paired CP v1.39) in the `StepKindDispatcherRegistry`, a `RuntimeConfig.managed_agents_config` opt-in (§3 — carries the operator client + a decoupled `step_timeout_seconds`), a `HarnessContext.managed_agents_client` field (§4), a stage-5 `materialize_managed_agents_dispatcher_stage` factory (gated on `DeploymentSurface.MANAGED_CLOUD` + opt-in), and `RT-FAIL-MANAGED-AGENTS-{STAGE-MATERIALIZE,SESSION}` fail classes (§11). Mirrors the §14.17 C-RT-27 operator-opt-in stage-5-factory precedent. The stale line-703 "no §14.18 C-RT-28 sibling" prose is forward-annotated as superseded (C-RT-28 → §14.20; §14.18/19 are C-RT-29/30 since v1.35).

**Decorrelated-review hardening (same unmerged arc; advisor + Codex; no version bump — v1.55 has not merged).** Three correctness findings landed against the as-built and reconciled into §14.20: (1) the `StepKind.MANAGED_AGENTS` facade timeout is decoupled from the shared 30s `step_dispatch_timeout_seconds` into `managed_agents_config.step_timeout_seconds` (600s default; §14.20.5 invariant 7) — a vendor session runs minutes, and the shared bound would fire `RT-FAIL-STEP-DISPATCH-TIMEOUT` prematurely while the vendor session keeps running, billable, never cancelled; (2) the dispatcher best-effort cancels-on-give-up on poll-budget exhaustion (§14.20.2 step 4) — no orphaned billable session; (3) `_MutableHarnessContext.freeze()` preserves the `managed_agents_client` carrier (Codex — it was a write-only carrier silently dropping to `None` at freeze). §14.20.1/.3 were also reconciled to the as-built (config carries `client` + `step_timeout_seconds`, not an empty marker; the factory returns the dispatcher and the stage-5 caller binds + facade-wraps).

**The C-RT-28 contract is additive back-flow (no operator gate of its own); the gated decision is the paired CP v1.39 closed-at-5 StepKind extension, RATIFIED 2026-06-17 (Option B).** C-RT-28's surfaces are all opt-in + surface-gated + backward-compatible (default-config workflows bind nothing, emit nothing). Option A (riding `SUB_AGENT_DISPATCH`) was probe-foreclosed (that dispatcher hard-requires topology-admissibility + child-manifest recursion a vendor session cannot honor). The live managed-cloud run (the credential/vendor gate — `ANTHROPIC_API_KEY` + GCP IAM + Cloud-Trace) is surfaced at the dispatch boundary, **never auto-fired**.

Reviewed during clearance: the contract surface over the built carrier (signatures grounded by direct read of `managed_agents.py`); the async-dispatch-via-`SyncDispatcherFacade` binding (C-RT-15/C-RT-17 precedent); the surface-gating + fail-closed-when-unbound discipline; the vendor-owns-the-loop distinction from `SUB_AGENT_DISPATCH` (no topology-admissibility, no `subagent.*` spans); the §14.20 slot + C-RT-28 contract-id (honor reserved; §14.18/19 = C-RT-29/30 verified).

## Notes

- Phase 7 consumers may rely on this version as canonical **only after** the paired CP v1.39 clearance + the bundled impl land together (`merge_commit` pinned at the post-merge refresh).
- The live managed-cloud production run remains a surfaced vendor-gate (Slice 6); H_T-AS-8f is already SUBSTANTIVE_RETIRED (R-820), so the live run is NOT a retirement prerequisite.
- See `.harness/clearance/README.md` for marker discipline.
