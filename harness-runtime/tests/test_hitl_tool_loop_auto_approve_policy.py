"""The model tool-call gate honours `hitl_auto_approve_policy` (runtime spec §3.8).

The PRE_ACTION composer lowers the solo persona floor to AUTO under the default policy, so
a READ_ONLY manifest tool step on an L3 host auto-dispatches; the model tool-call gate must
compute the same level for the identical call, or one operator policy has two enforcers.
Provider-free: host, operator and dispatcher doubles through the real stage-5 factory.
"""

from __future__ import annotations

import asyncio
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest
from harness_as.sandbox_tier import BlastRadiusTier, SandboxTier
from harness_as.tool_contract import ToolContract
from harness_core import PersonaTier
from harness_cp.cp_shared_types import MCPTrustTier
from harness_cp.hitl_response_palette import HITLResponse
from harness_runtime.bootstrap.factories.r_cxa_2_producer_loop_factory import (
    materialize_r_cxa_2_producer_loop_stage,
)
from harness_runtime.lifecycle.hitl_auto_approve_policy import HITLAutoApprovePolicy
from harness_runtime.lifecycle.tool_registry import ToolRegistry

from .test_hitl_tool_loop_deny import _call, _Operator
from .test_r_cxa_2_producer_loop_factory import _context, _post_tool_dispatcher_context

ALL = frozenset(HITLResponse)


class _Host:
    """`MCPClientHost` stand-in whose one tool carries the given blast-radius tier."""

    def __init__(self, trust: MCPTrustTier, tool: str, blast: BlastRadiusTier) -> None:
        self.trust_tier = trust
        self.tool_registry = ToolRegistry()
        self.tool_registry.register(
            ToolContract(
                name=tool,
                description=tool,
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                minimum_tier=SandboxTier.TIER_1_PROCESS,
                blast_radius_tier=blast,
            )
        )


def _run(
    tmp_path: Path,
    hosts: dict[str, Any],
    tool: str,
    *,
    policy: HITLAutoApprovePolicy,
    persona: PersonaTier = PersonaTier.SOLO_DEVELOPER,
) -> tuple[Any, _Operator, Any]:
    order: list[str] = []
    ctx, config, _surface, dispatcher = _post_tool_dispatcher_context(tmp_path, order)
    config = config.model_copy(update={"hitl_auto_approve_policy": policy})
    ctx.mcp_client_hosts = hosts
    operator = _Operator(order, HITLResponse.APPROVE)
    ctx.ask_user_question_surface = operator
    loop = materialize_r_cxa_2_producer_loop_stage(ctx, config).hitl_tool_loop
    context = replace(_context(), persona_tier=persona)
    (result,) = asyncio.run(loop.run_tool_calls([_call(tool)], context))
    return result, operator, dispatcher


DEFAULT = HITLAutoApprovePolicy()
OPTED_OUT = HITLAutoApprovePolicy(solo_persona_floor_auto=False)


def test_the_default_policy_auto_dispatches_a_read_only_call_on_an_l3_host(tmp_path: Path) -> None:
    hosts = {
        "srv": _Host(MCPTrustTier.LEVEL_3_ALLOW_WITH_AUDIT, "read_file", BlastRadiusTier.READ_ONLY)
    }

    result, operator, dispatcher = _run(tmp_path, hosts, "read_file", policy=DEFAULT)

    assert operator.offered == []  # never asked: the solo persona floor is AUTO
    assert result.dispatched is True
    assert len(dispatcher.calls) == 1


def test_the_default_policy_auto_dispatches_search_tools(tmp_path: Path) -> None:
    result, operator, _dispatcher = _run(tmp_path, {}, "search_tools", policy=DEFAULT)

    assert operator.offered == []
    assert result.dispatched is True


def test_opting_out_restores_the_ask(tmp_path: Path) -> None:
    hosts = {
        "srv": _Host(MCPTrustTier.LEVEL_3_ALLOW_WITH_AUDIT, "read_file", BlastRadiusTier.READ_ONLY)
    }

    result, operator, _dispatcher = _run(tmp_path, hosts, "read_file", policy=OPTED_OUT)

    assert operator.offered == [ALL]
    assert result.dispatched is True


@pytest.mark.parametrize(
    "trust", [MCPTrustTier.LEVEL_1_SIGNED_PINNED, MCPTrustTier.LEVEL_2_SANDBOX_ALL]
)
def test_the_trust_floor_is_never_lowered_by_the_policy(
    tmp_path: Path, trust: MCPTrustTier
) -> None:
    hosts = {"srv": _Host(trust, "read_file", BlastRadiusTier.READ_ONLY)}

    result, operator, _dispatcher = _run(tmp_path, hosts, "read_file", policy=DEFAULT)

    assert operator.offered == [ALL]
    assert result.dispatched is True


def test_a_local_mutation_call_asks_unless_the_operator_opts_in(tmp_path: Path) -> None:
    hosts = {
        "srv": _Host(
            MCPTrustTier.LEVEL_3_ALLOW_WITH_AUDIT, "write_file", BlastRadiusTier.LOCAL_MUTATION
        )
    }

    asked, operator, _ = _run(tmp_path, hosts, "write_file", policy=DEFAULT)
    assert operator.offered == [ALL]
    assert asked.dispatched is True

    opted_in = HITLAutoApprovePolicy(solo_local_mutation_floor_auto=True)
    auto, operator, _ = _run(tmp_path, hosts, "write_file", policy=opted_in)
    assert operator.offered == []
    assert auto.dispatched is True


def test_an_external_call_always_asks(tmp_path: Path) -> None:
    hosts = {
        "srv": _Host(
            MCPTrustTier.LEVEL_3_ALLOW_WITH_AUDIT, "send", BlastRadiusTier.EXTERNAL_IRREVERSIBLE
        )
    }
    everything_on = HITLAutoApprovePolicy(solo_local_mutation_floor_auto=True)

    _result, operator, _ = _run(tmp_path, hosts, "send", policy=everything_on)

    assert operator.offered == [ALL]


def test_a_non_solo_persona_is_not_lowered(tmp_path: Path) -> None:
    hosts = {
        "srv": _Host(MCPTrustTier.LEVEL_3_ALLOW_WITH_AUDIT, "read_file", BlastRadiusTier.READ_ONLY)
    }

    _result, operator, _ = _run(
        tmp_path, hosts, "read_file", policy=DEFAULT, persona=PersonaTier.TEAM_BINDING
    )

    assert operator.offered == [ALL]
