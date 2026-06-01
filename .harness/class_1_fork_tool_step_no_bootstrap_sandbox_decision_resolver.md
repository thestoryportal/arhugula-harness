# Class 1 fork — TOOL_STEP not dispatchable via `api.run`: no bootstrap-supplied `sandbox_decision_resolver`

**Status:** PROPOSING (needs operator AskUserQuestion) — filed 2026-06-01 during the `class_1_fork_tool_step_no_operator_supplied_converter.md` Reading B apply arc (spec v1.40).
**Filed:** 2026-06-01, at the apply-arc pre-substantive empirical orientation (39th-shape `[[advisor-before-substantive-work-for-cross-axis-blockers]]` application — advisor reconcile call confirmed the gap is real and the ratified converter fix is necessary-but-not-sufficient).
**Class:** 1 (architectural — a second operator-policy callable on the TOOL_STEP dispatch path is structurally unreachable through the bootstrap; closing it requires a config-surface / discretion decision).
**Blocks:** R-100-mvp-real-workflow-execution **AC #2** ("tool dispatch surface exercised ≥1 site") *via the operator `api.run` path*. This is the **same AC** the converter fork blocked — converter-only does NOT unblock it. Does NOT block the dispatcher-level surface (U-RT-86 e2e exercises it by hand-supplying both callables).
**Sibling of:** `.harness/class_1_fork_tool_step_no_operator_supplied_converter.md` (RATIFIED-AS-READING-B, applied at spec v1.40). That fork closed the `tool_contract_converter` config surface (one necessary piece). This fork carries the `sandbox_decision_resolver` design decision. **Do NOT read these as the only two gaps** — §4 lists at least one more open gap (bootstrap never calls `host.start()`) and does not assert the list complete. AC #2 closes only when the full bootstrap TOOL_STEP path is wired AND demonstrated e2e (§4).

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

## 4. The known-gaps list is NOT asserted complete (the sufficiency claim was undercounted twice)

**Do not read this fork as "converter + resolver = sufficient for AC #2."** That two-gap framing was an undercount, surfaced by a pre-merge completeness critic at the converter PR (#171):

- **Gap A — converter (CLOSED at spec v1.40).** `MCPClientHost` had no operator-suppliable `tool_contract_converter`.
- **Gap B — host start() at bootstrap (OPEN; impl, not design).** See §5 — the stage-3a bootstrap body binds the host but never calls `host.start()`, so the registry is never populated and the converter never even runs. This fires at dispatch **step 1** (`RT-FAIL-TOOL-CONTRACT-UNKNOWN`), *before* the trust gate (step 2) and *before* this fork's resolver (step 3). With Gap B open, the v1.40 converter is currently **unreachable through the bootstrap** — green `_FakeTool` unit tests prove the converter function, not the path.
- **Gap C — `sandbox_decision_resolver` (OPEN; the design decision this fork carries).** §1-§3.
- **Gap D? — unknown.** Bootstrap provider construction for a tool-only (no-inference) workflow is a live candidate not yet resolved (does `api.run` require an LLM provider/key even when the workflow has only TOOL_STEPs?). There may be others.

**Canonical framing (non-falsifiable by the next gap):** R-100-mvp-real-workflow-execution **AC #2 closes only when the full bootstrap TOOL_STEP path is wired AND demonstrated end-to-end** (one echo-MCP-via-`api.run` workflow that completes a TOOL_STEP). This fork (Gap C) is one necessary piece; Gap B is another; the converter (Gap A, done) is a third. The closing arc proves sufficiency **by execution, not by unit tests** — the e2e is the only artifact that can establish the path is complete.

The R-100 deterministic xfail marker (`test_u_rt_75_runtime_tool_dispatcher_factory.py::test_ac2_bootstrap_dispatcher_resolves_sandbox_decision`) demonstrates Gap C in isolation (it invokes the resolver directly, bypassing Gaps A+B); it is NOT an AC #2 e2e.

## 5. Gap B — bootstrap never starts the MCP host (sibling impl-gap; lands in the same closing arc)

**Evidence (conclusive, HEAD).** `harness-runtime/src/harness_runtime/bootstrap/stage_3a_cp_clients.py:48` — `ctx.mcp_client_host = await materialize_mcp_client_host_stage(config)` is the LAST statement of `execute()`; there is no `host.start()` call. Grep confirms no `mcp_client_host.start()` anywhere under `harness-runtime/src/harness_runtime/bootstrap/` or `api.py`. The factory returns an **unstarted** host (its docstring: "the stage 3a body is responsible for calling `.start()` afterward if `config.mcp_clients` is non-empty"), and spec §14.9.3 stage-3a mandates "subprocess spawn + protocol handshake + `list_tools` registry population happen here." `start()` is fully implemented (`mcp_client_host.py:379` `call_tool`; `:~310` `start`; `MCPHostStartupError` / `RT-FAIL-MCP-HOST-STARTUP` carrier present) — it is simply never invoked from bootstrap. This was latent (no production workflow reached `mcp_clients` because TOOL_STEP-via-`api.run` was unreachable at the converter gap); closing Gap A makes it the next-firing blocker.

**Disposition.** Gap B is an **impl / spec-conformance bug**, not a design decision — so NO separate fork doc. It lands in the **same closing arc** as Gap C, because only together can one e2e prove the chain (`start → list_tools → converter → registry → trust → resolver → call_tool`). Fixing `start()` alone buys zero forward verification (the resolver still raises at step 3) while incurring integration-test fallout (several bootstrap-going tests populate `mcp_clients=[...]` and currently rely on the host never being started — `test_run_smoke`, `test_track_b_e2e`, integration `conftest`, elicitation e2e). That test-safety question is answered **in the closing arc, in context, with the e2e as proof** — not hastily at the converter PR.

**Flag for the closing arc (do NOT resolve now).** `stage_3a_cp_clients.py`'s module docstring claims provider construction "is the only stage entry point in the runtime that performs network I/O at bootstrap time" — in direct tension with spec §14.9.3 placing a subprocess spawn at stage 3a. Default to the spec (eager start at 3a); the closing arc should confirm eager-start is the intent vs. a deliberate lazy-start choice the docstring hints at. That tension is why Gap B is not cleanly "a one-line typo."

## 6. Tracking

Tracked at roadmap `R-100-tool-step-sandbox-resolver` — broadened to the **AC#2-closing arc**: wire the full bootstrap TOOL_STEP path (Gap B host `start()` + Gap C resolver) and prove it with one echo-MCP-via-`api.run` e2e. Sibling to `R-100-tool-step-converter` (Gap A, RESOLVED — converter config surface only).
