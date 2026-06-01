# Class 1 fork — TOOL_STEP not dispatchable via `api.run`: no operator path to supply `tool_contract_converter`

**Status:** PROPOSING — awaiting operator ratification.
**Filed:** 2026-05-31, during R-100-mvp-real-workflow-execution use-the-product probe (authoring the multi-step + tool-dispatch e2e).
**Class:** 1 (architectural — the operator-facing tool-dispatch path is structurally unreachable; fix needs a config-surface decision).
**Blocks:** R-100-mvp-real-workflow-execution AC #2 ("tool dispatch surface exercised ≥1 site") *via the operator `api.run` path*. Does NOT block the tool-dispatch surface at the dispatcher level (U-RT-86 e2e exercises it by hand-constructing the host with a converter).

---

## 1. The divergence

A `StepKind.TOOL_STEP` cannot be dispatched through the full bootstrap (`api.run` → `run_bootstrap` → stage 3a MCP host → stage 5 tool dispatcher), because the bootstrap-built `MCPClientHost` has no `tool_contract_converter`, and an operator has no config surface to supply one.

## 2. Evidence (code-level, conclusive)

1. **`MCPClientHost` defaults the converter to a raise-on-every-call stub.** `harness-runtime/src/harness_runtime/lifecycle/mcp_client_host.py:169` — `tool_contract_converter: MCPToolContractConverter | None = None`; line 224-225 — `self._tool_contract_converter = tool_contract_converter or _default_tool_contract_converter`; lines 99-110 — `_default_tool_contract_converter` `raise LookupError(...)` on every invocation. The converter is required to map an MCP `mcp.types.Tool` → AS `ToolContract` (the AS-side sandbox/blast-radius policy fields can't be defaulted).

2. **The bootstrap factory passes no converter.** `harness-runtime/src/harness_runtime/bootstrap/factories/mcp_client_host_factory.py:126-131` — `materialize_mcp_client_host_stage` constructs `MCPClientHost(transport=..., server_name=..., trust_tier=..., transport_config=...)` with no `tool_contract_converter=` kwarg → the default-that-raises is used.

3. **No operator config surface for a converter.** `RuntimeConfig` (`harness-runtime/src/harness_runtime/types.py`) has no `tool_contract_converter` field (only a static `tool_contracts: dict[ToolName, ToolContract]` at :1381). `MCPClientConfig` (:439) carries only `client_name / transport / trust_level / blast_radius / connection_url` — no converter.

4. **U-RT-86 self-documents the gap.** `test_u_rt_86_mcp_client_external_server_e2e.py:262-288` constructs a *parallel* `MCPClientHost` by hand with `tool_contract_converter=_make_tool_converter()` precisely because "the factory does not wire `tool_contract_converter` (operator policy per advisor reconciliation 2026-05-24)." The e2e exercises the dispatcher path, not `api.run`.

So at production HEAD, the only way a TOOL_STEP dispatches is if an operator hand-builds an `MCPClientHost` with a converter — which the `harness` CLI / `api.run` provides no path to do.

## 3. The decision (why Class 1, not a clean impl)

A converter encodes per-tool **sandbox tier + blast-radius policy** (`ToolContract.minimum_tier`, `blast_radius_tier`). It is genuinely operator policy, not a defaultable value (defaulting it would silently assign a sandbox posture to every discovered tool). So the fix is a config-surface decision:

- **(A) Per-server static ToolContract map.** Operator declares `tool_contracts` per MCP server in `MCPClientConfig`; the host looks up the contract by tool name instead of converting. (`RuntimeConfig.tool_contracts` already exists — possibly the intended path; verify it's consulted at dispatch.)
- **(B) Declarative per-server default policy.** `MCPClientConfig` gains `{default_minimum_tier, default_blast_radius}`; the factory builds a converter that stamps every tool with those. Simple; coarse.
- **(C) Converter plugin path.** A config field naming an importable converter callable (operator-authored module). Most flexible; heaviest.
- **(D) Spec amendment.** Declare TOOL_STEP-via-`api.run` out of MVP scope (operators wire the dispatcher manually), matching the current de-facto state.

## 4. Impact on R-100-mvp-real-workflow-execution

AC #2 ("tool dispatch surface exercised ≥1 site") is satisfiable at the dispatcher level today (U-RT-86, passing on main) but NOT inside a real operator `api.run` multi-step workflow. The R-100 real-workflow e2e therefore covers AC #1 (3+ inference steps) + AC #3 (step ledger) via `api.run`; AC #2 is met by the existing U-RT-86 dispatcher-level coverage + this fork tracks the operator-path closure. Same shape as `class_1_fork_harness_toml_default_discovery_unimplemented.md` (a declared surface with no operator wiring).

## 5. Tracking

Roadmap: note on R-100-mvp-real-workflow-execution + a follow-on R-NNN if ratified. Does not block the MVP demonstration (the surface is exercised; the operator-path wiring is the gap).
