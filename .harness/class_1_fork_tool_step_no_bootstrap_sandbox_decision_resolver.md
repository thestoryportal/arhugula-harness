# Class 1 fork — TOOL_STEP not dispatchable via `api.run`: no bootstrap-supplied `sandbox_decision_resolver`

**Status:** PROPOSING (needs operator AskUserQuestion) — filed 2026-06-01 during the `class_1_fork_tool_step_no_operator_supplied_converter.md` Reading B apply arc (spec v1.40).
**Filed:** 2026-06-01, at the apply-arc pre-substantive empirical orientation (39th-shape `[[advisor-before-substantive-work-for-cross-axis-blockers]]` application — advisor reconcile call confirmed the gap is real and the ratified converter fix is necessary-but-not-sufficient).
**Class:** 1 (architectural — a second operator-policy callable on the TOOL_STEP dispatch path is structurally unreachable through the bootstrap; closing it requires a config-surface / discretion decision).
**Blocks:** R-100-mvp-real-workflow-execution **AC #2** ("tool dispatch surface exercised ≥1 site") *via the operator `api.run` path*. This is the **same AC** the converter fork blocked — converter-only does NOT unblock it. Does NOT block the dispatcher-level surface (U-RT-86 e2e exercises it by hand-supplying both callables).
**Sibling of:** `.harness/class_1_fork_tool_step_no_operator_supplied_converter.md` (RATIFIED-AS-READING-B, applied at spec v1.40). That fork closed the `tool_contract_converter` half; this fork is the `sandbox_decision_resolver` half.

---

## 1. The divergence

A `StepKind.TOOL_STEP` dispatched through the full bootstrap (`api.run` → `run_bootstrap` → stage 5 `materialize_runtime_tool_dispatcher_stage` → `RuntimeToolDispatcher.dispatch`) raises before doing any work, because the bootstrap-built `RuntimeToolDispatcher` has no `sandbox_decision_resolver`, and an operator has no config surface to supply one. The default resolver raises `LookupError` on every invocation.

This is structurally identical to the converter gap (sibling fork) but at a **different callable on the same path**. With the converter fix (spec v1.40) in place, a TOOL_STEP now gets past tool-contract conversion — and then dies at the sandbox-decision step.

## 2. Evidence (code-level, conclusive — verified at HEAD `b220dd5`)

1. **The dispatcher defaults the resolver to a raise-on-every-call stub.** `harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py:221` — `sandbox_decision_resolver: SandboxDecisionResolver | None = None`; line 270 — `self._sandbox_resolver = sandbox_decision_resolver or _default_sandbox_decision_resolver`; lines 99-115 — `_default_sandbox_decision_resolver` `raise LookupError(...)` on every invocation. The resolver maps `(ToolContract, WorkflowStep) → SandboxDispatchDecision` (the 5-field carrier: `tier / tech / provider / assigned_tier_reason / cost_tier_overhead_ms`).

2. **The bootstrap factory passes no resolver.** `harness-runtime/src/harness_runtime/bootstrap/factories/runtime_tool_dispatcher_factory.py:117` — the bare `RuntimeToolDispatcher(...)` construction passes `mcp_client_host / per_server_trust_evaluator / mcp_namespace_emitter / trust_policy / tracer_provider / cost_chain / audit_writer / rate_table` — **no `sandbox_decision_resolver=`** → the default-that-raises is used.

3. **`config.sandbox_decision_policy` exists but is read-and-discarded.** The factory reads `config.sandbox_decision_policy` (defaulting to `SandboxDecisionPolicy.default()`) and then does `_ = sandbox_decision_policy` with the inline comment "the existing C-RT-19 dispatcher predates the field and does not yet consume it ... received here for spec-contract conformance + future-arc consumption." So a config surface exists at the policy level, but it is (a) an empty-marker dataclass (no fields, per `class_1_fork_sandbox_decision_policy_phantom_cite.md` Q1=C-i), and (b) not bridged to a `sandbox_decision_resolver`.

4. **Dispatch invokes the resolver BEFORE the tier-floor check.** `runtime_tool_dispatcher.py:449` — `sandbox_decision = self._sandbox_resolver(contract, step)` (raises here under the default stub); `:451` — `if _SANDBOX_TIER_RANK[sandbox_decision.tier] < _SANDBOX_TIER_RANK[contract.minimum_tier]: raise SandboxTierFloorViolationError(...)`. So even a perfectly-stamped `ToolContract.minimum_tier` from the v1.40 converter cannot reach the floor comparison — the resolver raises first.

5. **U-RT-86 self-documents the gap.** `test_u_rt_86_mcp_client_external_server_e2e.py:296-302` hand-constructs the `RuntimeToolDispatcher` with `sandbox_decision_resolver=_make_sandbox_resolver()` (lines 224-234), alongside the hand-supplied `tool_contract_converter`. The e2e exercises the dispatcher path, not `api.run`. **Both** callables are hand-supplied precisely because the factory wires neither.

So at production HEAD, a TOOL_STEP dispatches only if an operator hand-builds BOTH a converter (closed at v1.40) AND a resolver (this fork) — neither of which the `harness` CLI / `api.run` provides a path to do.

## 3. The decision (the sharp question)

**Is `sandbox_decision_resolver` implementer-discretion or operator-policy?** The evidence cuts both ways:

- **Implementer-discretion reading.** `SandboxDispatchDecision`'s own docstring (`runtime_tool_dispatcher.py:79-86`) says the decision is "deferred to implementation discretion per spec §14.9.7." On this reading the runtime MAY wire a default resolver at the factory **without operator ratification** — it is an implementation detail, not a design surface.
- **Operator-policy reading (parity with the converter).** The default resolver raises-loud — the exact loud-on-misconfig discipline the converter used, and the converter was treated as ratification-required at the sibling fork because "defaulting it would silently assign a sandbox posture to every discovered tool." The resolver *resolves the actual sandbox mechanism + tier at dispatch* — assigning a sandbox posture is precisely what it does. On this reading it is operator policy and a silent default is an X-AL-3 design extension.

(Note: do NOT lean on spec v1.16 finding (i) here — that finding is about `sandbox_decision_policy`, the empty-marker config, not the `sandbox_decision_resolver` callable. Related, not identical.)

### Readings

- **(A) Identity resolver — MVP-cleanest.** The factory wires a trivial resolver: `tier = contract.minimum_tier`, with placeholder `tech` / `provider` / `assigned_tier_reason="default-policy-converter-identity"` / `cost_tier_overhead_ms=0`. No new config fields. Always passes the floor (`tier == minimum_tier`). The v1.40 converter-stamped `minimum_tier` becomes the **single source of truth** for the tool's sandbox tier — the operator declares it once (per-server `default_minimum_tier`), and the resolver honors it. Makes no independent isolation *decision*, which is the strongest argument that it is NOT operator policy. Coarse but coherent with Reading B's per-server-default model.
- **(B) Per-server default sandbox-mechanism fields.** `MCPClientConfig` gains `{default_sandbox_tier, default_sandbox_tech, default_sandbox_provider}` (and possibly overhead); the factory builds a resolver from them. Symmetric with the converter's per-server defaults. Heaviest — adds a second field cluster and lets the resolved tier diverge from `minimum_tier` (re-introducing a genuine floor check). Most faithful to "the resolver is operator policy."
- **(C) Defer.** Declare TOOL_STEP-via-`api.run` out of MVP scope; operators wire the dispatcher manually (current de-facto state). AC #2 stays unreachable via the operator path.

### Recommendation

**Parity-with-the-converter reading** (the resolver IS operator policy in principle), implemented via **(A) the identity resolver** as the MVP-cleanest shape: it honors the operator's already-ratified per-server tier declaration (`default_minimum_tier`) without a second config cluster, and it makes the converter-stamped tier authoritative. (B) is the most faithful if the operator wants the resolved tier to be able to *exceed* the tool's declared floor; that is a richer model than the MVP needs. **Flag explicitly:** the §14.9.7 implementer-discretion clause genuinely supports wiring (A) *without* a fork — but the converter precedent (raises-loud, assigns sandbox posture → ratification-required) argues the symmetric callable deserves the same ratification, so this is filed rather than silently wired.

## 4. Impact on R-100-mvp-real-workflow-execution

AC #2 ("tool dispatch surface exercised ≥1 site" via the operator `api.run` path) **remains BLOCKED after spec v1.40** (converter half). It closes only when BOTH the converter (done) and the resolver (this fork) are wired into the bootstrap. The R-100 e2e (`test_r100_real_workflow_e2e.py`) carries a TOOL_STEP-via-`api.run` test authored as **xfail pending this fork** (mirroring how AC #2 + AC #4 were originally filed as blocked-with-fork).

Tracked at roadmap `R-100-tool-step-sandbox-resolver` (NEW entry; sibling to `R-100-tool-step-converter`).
