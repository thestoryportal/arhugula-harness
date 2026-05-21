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
- `_state`: mutable holder dict carrying per-invocation state that the
  `run_workflow` tool handler binds for the duration of the call:
    - `_current_tool_ctx`: the in-flight `Context[ServerSession, None]` —
      read by `ServerCtxElicitCallback` (per AC #4) to invoke
      `await ctx.elicit(...)` outbound on the active server session.
    - `_harness_ctx`: the full post-bootstrap `HarnessContext` —
      consumed by the tool body to reach `ctx.step_dispatchers` +
      `ctx.audit_writer` etc. when dispatching `execute_workflow`.

The mutable holders are required because the frozen dataclass is
constructed at stage 2 — before stage 5 LOOP_INIT wiring completes — yet
the tool handler (registered at stage 2) consumes state populated at
`api.run()` time (post-bootstrap). Contextvar propagation across the
`asyncio.to_thread` → `SyncDispatcherFacade.run_coroutine_threadsafe`
bridge is unreliable (the run_coroutine_threadsafe submission copies the
context from the calling thread, not the awaiting tool handler frame);
the mutable-holder pattern is loop-thread-safe because both the tool
handler write site and the `ServerCtxElicitCallback` read site execute
on the main event loop.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP

    from harness_runtime.api import WorkflowObject

__all__ = [
    "HarnessMCPServer",
]


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

    workflow_registry: dict[str, "WorkflowObject"] = field(default_factory=dict)
    """Workflow lookup table keyed by `workflow.workflow_id`.

    `api.run()` writes the operator-supplied `WorkflowObject` here
    before invoking the `run_workflow` MCP tool. The tool handler
    body reads back by id and dispatches via `execute_workflow`.
    Mutable on a frozen dataclass: the field binding is frozen but
    the dict's contents are not.
    """

    _state: dict[str, Any] = field(default_factory=dict)
    """Per-invocation mutable holder for tool-handler-bound state.

    Keys written by the `run_workflow` tool handler body:
    - `_current_tool_ctx`: the in-flight `mcp.server.fastmcp.Context`
      object — set on tool entry, cleared in `finally`.
    - `_harness_ctx`: the full post-bootstrap `HarnessContext` — set by
      `api.run()` before opening the in-process `ClientSession`.

    Read by `ServerCtxElicitCallback.__call__` to reach the active
    `ctx` for `await ctx.elicit(...)`; read by the tool handler body
    to reach `ctx.step_dispatchers` etc.

    Loop-thread-safe: both the tool handler frame and the elicit
    callback execute on the main event loop; the worker-thread bridge
    (`SyncDispatcherFacade.run_coroutine_threadsafe`) submits the
    composer coroutine back to the main loop before the read fires.
    """
