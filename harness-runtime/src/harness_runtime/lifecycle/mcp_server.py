"""U-RT-62 — FastMCP server hosting (H_T-as-MCP-server topology).

Per `Spec_Harness_Runtime_v1.md` v1.12 §14.8.3 v1.12 workflow-initiation
topology pin: H_T runtime is the **MCP server**; Claude Code is the
registered MCP client; workflow execution is invoked by Claude Code
calling the `run_workflow` MCP tool; HITL `ctx.elicit(...)` rides the
active server session outbound back to Claude Code.

Sibling to `lifecycle/mcp_host.py` (U-RT-15 — H_T-as-MCP-client surface).
The two MCP roles are orthogonal per Q3 + Q5 disjointness ratification at
fork `class_1_tension_c_rt_18_mcp_workflow_initiation_topology_underspec.md`.

Composition surface
-------------------

- `HarnessMCPServer`: frozen dataclass wrapping a `mcp.server.fastmcp.FastMCP`
  instance + lifecycle state. The `started` field is set `True` after the
  `run_workflow` tool registration completes at bootstrap stage 2.
- `workflow_registry`: `dict[str, WorkflowObject]` — mutable holder keyed
  by `workflow.workflow_id`. `api.run()` pre-registers each workflow before
  invoking the in-process `run_workflow` tool.
- `_state`: mutable holder dict carrying post-bootstrap state that the
  `run_workflow` tool handler reads:
    - `_harness_ctx`: the full post-bootstrap `HarnessContext` —
      consumed by the tool body to reach `ctx.step_dispatchers` +
      `ctx.audit_writer` etc. when dispatching `execute_workflow`.
- `_CURRENT_TOOL_CTX` (module-level `contextvars.ContextVar`): the
  in-flight `Context[ServerSession, None]` — set by the `run_workflow`
  tool handler on entry; read by `ServerCtxElicitCallback` (per AC #4)
  to invoke `await ctx.elicit(...)` outbound on the active server session.

The `_state` holder is required because the frozen dataclass is
constructed at stage 2 — before stage 5 LOOP_INIT wiring completes — yet
the tool handler (registered at stage 2) consumes state populated at
`api.run()` time (post-bootstrap).

**Per-session ctx isolation (spec v1.36 §14.18 chapeau).** The active
MCP tool ctx is held in a module-level `contextvars.ContextVar`, NOT a
`_state` dict key. This is required by the spec-MUST invariant that
concurrent `run_workflow` invocations from distinct MCP client sessions
are INDEPENDENT runs (not concurrent re-entry of the same `api.run()`).
A shared `_state` key would race across concurrent invocations and route
the wrong client's ctx into `ServerCtxElicitCallback`. ContextVar gives
each asyncio task its own value; propagation across the
`asyncio.to_thread` → `SyncDispatcherFacade.run_coroutine_threadsafe`
bridge is preserved (verified empirically at
`tests/test_contextvar_bridge_propagation.py`).
"""

from __future__ import annotations

import asyncio
import contextvars
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from mcp.server.fastmcp import Context, FastMCP

_MANIFEST_PATH_SUFFIXES: frozenset[str] = frozenset({".yaml", ".yml", ".toml"})


def _looks_like_manifest_path(workflow_id: str) -> bool:
    """Discriminator for the daemon-mode workflow_id-as-path widening.

    Per `.harness/class_1_fork_u_rt_107_daemon_run_workflow_signature_
    underspec.md` Reading (A) + Q2=(i) ratification 2026-05-28: workflow_id
    is treated as a filesystem path iff it contains '/' OR ends in one of
    `.yaml` / `.yml` / `.toml`.
    """
    if "/" in workflow_id:
        return True
    # Fast-path suffix check without constructing Path objects.
    lower = workflow_id.lower()
    return any(lower.endswith(suffix) for suffix in _MANIFEST_PATH_SUFFIXES)


if TYPE_CHECKING:
    from harness_runtime.api import WorkflowObject

__all__ = [
    "HarnessMCPServer",
    "materialize_mcp_server_stage",
]


# Per-session ctx isolation per spec v1.36 §14.18 chapeau. Each concurrent
# `run_workflow` invocation gets its own asyncio task; the ContextVar binds
# the in-flight MCP tool ctx for the duration of that task and is read by
# `ServerCtxElicitCallback` via `HarnessMCPServer.get_current_tool_ctx()`.
# Bridge propagation (asyncio.to_thread → run_coroutine_threadsafe) verified
# at `tests/test_contextvar_bridge_propagation.py`.
_CURRENT_TOOL_CTX: contextvars.ContextVar[Context[Any, Any] | None] = contextvars.ContextVar(
    "harness.current_tool_ctx", default=None
)


@dataclass(frozen=True)
class HarnessMCPServer:
    """Runtime composition primitive — H_T-as-MCP-server hosting.

    Distinct from `MCPHost` (U-RT-15 H_T-as-MCP-client surface). The
    `HarnessContext` schema carries both: `mcp_host` for the client
    surface (consumes filesystem / GitHub / sandbox MCP servers) and
    `mcp_server` for the server surface (hosts the `run_workflow` tool
    that Claude Code invokes to execute workflows).

    The dataclass is frozen at the binding level; mutable state required
    by the tool handler lives in `workflow_registry` + `_state` dicts.
    """

    server: Any
    """The wrapped `mcp.server.fastmcp.FastMCP` instance.

    Typed `Any` to avoid pulling the FastMCP type into the static
    binding here (FastMCP is a heavyweight class with non-trivial type
    surface); the `lifecycle/mcp_server.py` constructor pins the type
    at materialization, and consumers (tool handler body,
    `ServerCtxElicitCallback`) operate against the runtime instance.
    """

    started: bool = False
    """Lifecycle flag — `True` after `materialize_mcp_server_stage()`
    registers the `run_workflow` tool. Bootstrap stage 2 rollback
    discipline (per existing 9-stage error handling) is preserved:
    on tool registration failure, the stage raises and the
    constructed `HarnessMCPServer(started=False)` is discarded."""

    workflow_registry: dict[str, WorkflowObject] = field(default_factory=dict)
    """Workflow lookup table keyed by `workflow.workflow_id`.

    `api.run()` writes the operator-supplied `WorkflowObject` here
    before invoking the `run_workflow` MCP tool. The tool handler
    body reads back by id and dispatches via `execute_workflow`.
    Mutable on a frozen dataclass: the field binding is frozen but
    the dict's contents are not.
    """

    _state: dict[str, Any] = field(default_factory=dict)
    """Post-bootstrap state holder. Written once by `api.run()` before
    invoking the `run_workflow` tool; read by the tool handler body.

    Keys:
    - `_harness_ctx`: the full post-bootstrap `HarnessContext` — set by
      `api.run()` before opening the in-process `ClientSession`. Singleton
      per process (mandated by C-RT-06 set_tracer_provider one-per-process
      invariant; shared across concurrent daemon-mode client sessions).

    NOTE: the in-flight MCP tool ctx is NOT held on `_state` — it lives on
    the module-level `_CURRENT_TOOL_CTX` ContextVar so concurrent
    `run_workflow` invocations from distinct MCP clients see isolated ctx
    values per spec v1.36 §14.18 chapeau. Access via the
    `get_current_tool_ctx()` / `set_current_tool_ctx()` /
    `reset_current_tool_ctx()` methods below.
    """

    def get_current_tool_ctx(self) -> Context[Any, Any] | None:
        """Return the in-flight MCP tool ctx for the current asyncio task,
        or None if no `run_workflow` invocation is in flight on this task.

        Read site for `ServerCtxElicitCallback`. ContextVar semantics
        guarantee each concurrent `run_workflow` task sees its own value.
        """
        return _CURRENT_TOOL_CTX.get()

    def set_current_tool_ctx(
        self, ctx: Context[Any, Any]
    ) -> contextvars.Token[Context[Any, Any] | None]:
        """Bind the in-flight MCP tool ctx for the current asyncio task.

        Returns a `contextvars.Token` that must be passed to
        `reset_current_tool_ctx` in a `finally` block to release the binding.
        Per spec v1.36 §14.18 chapeau per-session ctx isolation.
        """
        return _CURRENT_TOOL_CTX.set(ctx)

    def reset_current_tool_ctx(self, token: contextvars.Token[Context[Any, Any] | None]) -> None:
        """Release a binding previously installed by `set_current_tool_ctx`.

        Mirrors the `try/finally` discipline that `_state.pop(...)` used in
        the pre-isolation implementation, but operates on task-local
        ContextVar state instead of shared dict state.
        """
        _CURRENT_TOOL_CTX.reset(token)


def materialize_mcp_server_stage(
    *,
    drain_timeout_seconds: float,
) -> HarnessMCPServer:
    """Bootstrap stage 2 AS — construct FastMCP server + register `run_workflow`.

    Per `Spec_Harness_Runtime_v1.md` v1.12 §14.8.3 v1.12 workflow-initiation
    topology pin + Phase 2 Session 3 plan v2.10 §2 L9-quinquies U-RT-62 AC #2.

    Steps
    -----
    1. Construct `mcp.server.fastmcp.FastMCP(name="harness-runtime")`.
    2. Allocate mutable `workflow_registry` + `_state` dicts (captured by
       the tool handler's closure; the same instances are placed on the
       returned `HarnessMCPServer` dataclass so post-bootstrap `api.run()`
       can write to them by reference).
    3. Register the `run_workflow` MCP tool via `@fastmcp.tool()` decorator.
       The handler body dispatches `execute_workflow` from the CP axis on
       a worker thread (via `asyncio.to_thread`); the HITL gate composer
       inside `execute_workflow` bridges back to the main loop via
       `SyncDispatcherFacade.run_coroutine_threadsafe` and awaits
       `ctx.ask_user_question_surface.ask(...)` — which routes through
       `ServerCtxElicitCallback` (per AC #4) to call `await ctx.elicit(...)`
       outbound on the active server session per the v1.12 topology pin.
    4. Return `HarnessMCPServer(started=True, ...)` after registration
       completes. Bootstrap stage 2 rollback discipline preserved: on
       FastMCP constructor failure OR tool registration failure, this
       function raises and the partial state is discarded.

    Returns
    -------
    HarnessMCPServer
        Frozen dataclass with `started=True` after tool registration.
    """
    # Lazy import to keep the `lifecycle/mcp_server.py` → `harness_cp` edge
    # at runtime invocation (the CP driver does not need to load at module
    # import time when the FastMCP server is constructed at stage 2 but
    # not yet exercised; the import resolves on first tool invocation via
    # the closure lookup).
    from harness_cp.workflow_driver import execute_workflow as _execute_workflow

    fastmcp = FastMCP(name="harness-runtime")
    workflow_registry: dict[str, Any] = {}
    state: dict[str, Any] = {}

    @fastmcp.tool()
    async def run_workflow(workflow_id: str, ctx: Context[Any, Any]) -> dict[str, Any]:
        """Execute one workflow per the v1.12 H_T-as-MCP-server topology.

        The workflow body executes inside this tool handler's `ctx` per the
        topology pin. The HITL gate composer (per U-RT-60) bridges back to
        the main loop via `SyncDispatcherFacade.run_coroutine_threadsafe`
        and reaches `await ctx.elicit(...)` through
        `ServerCtxElicitCallback` (per AC #4) which reads this `ctx` from
        the module-level `_CURRENT_TOOL_CTX` ContextVar bound below. Each
        concurrent `run_workflow` invocation runs in its own asyncio task
        and sees its own ContextVar value per spec v1.36 §14.18 chapeau
        per-session ctx isolation.

        Parameters
        ----------
        workflow_id
            Key into `workflow_registry`; the operator-supplied
            `WorkflowObject` was pre-registered by `api.run()` per AC #5.
        ctx
            In-flight FastMCP tool handler context; carries the active
            server session for outbound `ctx.elicit(...)` calls.

        Returns
        -------
        dict[str, Any]
            JSON-serializable form of the CP driver's `RunResult`. The
            `api.run()` caller per AC #5 re-parses into the CP model and
            projects to the runtime-facing `RunResult` per C-RT-09.
        """
        harness_ctx = state.get("_harness_ctx")
        if harness_ctx is None:
            raise RuntimeError(
                "`run_workflow` invoked before `api.run()` bound the post-bootstrap "
                "`HarnessContext` on `HarnessMCPServer._state['_harness_ctx']`. "
                "The tool is intended for in-process invocation from `api.run()` "
                "per spec v1.12 §14.8.3 topology pin (Reading α)."
            )

        # workflow_id discriminator per `.harness/class_1_fork_u_rt_107_daemon_
        # run_workflow_signature_underspec.md` Reading (A) + Q2=(i) ratification
        # 2026-05-28. workflow_id is treated as a filesystem path iff it
        # contains '/' OR ends in one of `.yaml` / `.yml` / `.toml`; otherwise
        # registry key. Path-input invocations (daemon-client mode per U-RT-108)
        # load the manifest via `WorkflowManifestLoader.load_workflow(path)` on
        # every invocation (Q3=(a) no-cache). Registry-key path preserves the
        # in-process `api.run()` pre-registration semantics verbatim.
        if _looks_like_manifest_path(workflow_id):
            from harness_runtime.lifecycle.workflow_manifest_loader import (
                WorkflowManifestLoader,
                WorkflowManifestLoadError,
            )

            try:
                workflow = WorkflowManifestLoader.load_workflow(Path(workflow_id))
            except WorkflowManifestLoadError as exc:
                raise RuntimeError(
                    f"daemon-client run_workflow failed to load manifest at "
                    f"path {workflow_id!r}: {exc.FAIL_CLASS}: {exc.reason}"
                ) from exc
        else:
            workflow = workflow_registry.get(workflow_id)
            if workflow is None:
                raise RuntimeError(
                    f"workflow {workflow_id!r} not registered in "
                    f"`HarnessMCPServer.workflow_registry`; `api.run()` writes the "
                    f"`WorkflowObject` keyed by `workflow.workflow_id` before "
                    f"invoking the `run_workflow` tool per AC #5."
                )

        run_id = uuid.uuid4().hex
        # Bind the in-flight tool ctx for the duration of the workflow
        # execution per spec v1.36 §14.18 chapeau per-session ctx isolation.
        # `ServerCtxElicitCallback` (per AC #4) reads via the module-level
        # ContextVar to reach `await ctx.elicit(...)` from the HITL gate
        # composer; each concurrent invocation sees its own value.
        ctx_token = _CURRENT_TOOL_CTX.set(ctx)

        # Workflow-supplied dispatcher override (test-fixture surface);
        # falls back to `ctx.step_dispatchers` from stage 5 LOOP_INIT.
        workflow_step_dispatchers = getattr(workflow, "step_dispatchers", None)
        effective_step_dispatchers = (
            workflow_step_dispatchers
            if workflow_step_dispatchers is not None
            else getattr(harness_ctx, "step_dispatchers", None)
        )

        try:
            # Same composition pattern as the v1.11 `api.run()` baseline
            # (asyncio.to_thread for the sync CP driver; asyncio.wait_for
            # to enforce `RT-FAIL-DRAIN-TIMEOUT` per C-RT-14 + U-RT-44 AC #2).
            cp_result = await asyncio.wait_for(
                asyncio.to_thread(
                    _execute_workflow,
                    workflow.manifest_entry,
                    workflow.steps,
                    run_id,
                    cast(Any, harness_ctx),
                    default_model_binding=workflow.default_model_binding,
                    step_dispatchers=cast(Any, effective_step_dispatchers),
                ),
                timeout=drain_timeout_seconds,
            )
            return cast(dict[str, Any], cp_result.model_dump(mode="json"))
        except TimeoutError:
            # `RT-FAIL-DRAIN-TIMEOUT` projection per U-RT-44 AC #2;
            # the api.run caller per AC #5 unmarshals and re-builds the
            # runtime RunResult with status='drained'.
            from harness_cp.workflow_driver_types import (
                RunResult as _CpRunResult,
            )
            from harness_cp.workflow_driver_types import (
                RunStatus as _CpRunStatus,
            )

            drained = _CpRunResult(
                workflow_id=workflow.manifest_entry.workflow_id,
                run_id=run_id,
                status=_CpRunStatus.DRAINED,
                terminal_step_index=None,
                partial_state=None,
                final_state=None,
                fail_class="RT-FAIL-DRAIN-TIMEOUT",
            )
            return cast(dict[str, Any], drained.model_dump(mode="json"))
        finally:
            _CURRENT_TOOL_CTX.reset(ctx_token)

    return HarnessMCPServer(
        server=fastmcp,
        started=True,
        workflow_registry=workflow_registry,
        _state=state,
    )
