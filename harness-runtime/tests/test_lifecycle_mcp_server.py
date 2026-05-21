"""U-RT-62 — `HarnessMCPServer` primitive declaration tests (AC #1).

Per Phase 2 Session 3 plan v2.10 §2 L9-quinquies U-RT-62 AC #1:
- `HarnessMCPServer` is a frozen dataclass distinct from `MCPHost`.
- Carries `server` (FastMCP instance handle), `started: bool`, mutable
  `workflow_registry` + `_state` holders.
- `HarnessContext` schema admits both `mcp_host: MCPHost` (existing,
  H_T-as-MCP-client) AND `mcp_server: HarnessMCPServer | None` (new,
  H_T-as-MCP-server). The two roles are orthogonal per Q3 + Q4
  sibling-primitive ratification at the C-RT-18 v1.12 fork.
"""

from __future__ import annotations

import dataclasses

import pytest
from harness_runtime.lifecycle.mcp_host import MCPHost
from harness_runtime.lifecycle.mcp_server import HarnessMCPServer


def test_harness_mcp_server_is_frozen_dataclass() -> None:
    """AC #1: frozen dataclass; binding immutable post-construction."""
    server = HarnessMCPServer(server=object(), started=False)
    assert dataclasses.is_dataclass(server)
    assert dataclasses.fields(server)  # has fields
    with pytest.raises(dataclasses.FrozenInstanceError):
        server.started = True  # type: ignore[misc]


def test_harness_mcp_server_carries_required_fields() -> None:
    """AC #1: server + started + workflow_registry + _state present."""
    server_instance = object()
    server = HarnessMCPServer(server=server_instance)
    assert server.server is server_instance
    assert server.started is False  # default
    assert server.workflow_registry == {}
    assert server._state == {}


def test_workflow_registry_is_mutable_on_frozen_dataclass() -> None:
    """AC #1: dict-valued field mutable even on frozen dataclass.

    Required because `api.run()` writes the operator-supplied
    `WorkflowObject` to the registry per workflow.workflow_id before
    invoking the `run_workflow` MCP tool (per AC #5 thin-wrapper reframe).
    """
    server = HarnessMCPServer(server=object())
    server.workflow_registry["wf-1"] = object()  # type: ignore[assignment]
    assert "wf-1" in server.workflow_registry


def test_state_holder_is_mutable_on_frozen_dataclass() -> None:
    """AC #1 + AC #4 prerequisite: `_state` holder accepts per-invocation
    writes from the `run_workflow` tool handler body + reads from
    `ServerCtxElicitCallback`. Loop-thread-safe because both sites
    execute on the main event loop (the worker-thread bridge submits
    back via `run_coroutine_threadsafe` before the read fires).
    """
    server = HarnessMCPServer(server=object())
    sentinel_ctx = object()
    server._state["_current_tool_ctx"] = sentinel_ctx
    assert server._state["_current_tool_ctx"] is sentinel_ctx
    server._state.pop("_current_tool_ctx", None)
    assert "_current_tool_ctx" not in server._state


def test_harness_mcp_server_distinct_from_mcp_host() -> None:
    """AC #1 + AC #7 (Q4 ratification): `HarnessMCPServer` is a separate
    sibling primitive — NOT a refinement of `MCPHost`. The two MCP roles
    (H_T-as-client per U-RT-15; H_T-as-server per U-RT-62) coexist.
    """
    server = HarnessMCPServer(server=object())
    host = MCPHost(started=False)
    assert type(server) is not type(host)
    assert not isinstance(server, MCPHost)
    assert not isinstance(host, HarnessMCPServer)


def test_harness_context_field_admits_both_mcp_roles() -> None:
    """AC #1: `HarnessContext.mcp_server` field admits `HarnessMCPServer`
    sibling to existing `mcp_host: MCPHost`. The `mcp_server` field is
    Optional (`None` default) for transitional bootstrap-builder shapes;
    post-U-RT-62 bootstrap completion writes a populated instance.
    """
    from harness_runtime.types import HarnessContext

    fields = HarnessContext.model_fields
    assert "mcp_host" in fields
    assert "mcp_server" in fields
    # mcp_server is Optional (default None) per AC #1 transitional shape.
    mcp_server_field = fields["mcp_server"]
    assert mcp_server_field.default is None
