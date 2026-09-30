"""Behavioural witnesses for C-RT-36 (external state root), C-RT-37 (Ollama evaluator verdict)
and C-RT-38 (model tool-call gate enforcement).

Each test drives the real boundary the contract names (Runtime spec §14.25-§14.27) and
asserts its fail-closed outcome with hand-derived values. They exist so the Q3 evidence matrix
counts these contracts because a behaviour is pinned, not because an identifier is mentioned.
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from harness_core import PersonaTier
from harness_core.deployment_surface import DeploymentSurface
from harness_core.workload_class import WorkloadClass
from harness_cp.cp_shared_types import ActorIdentity
from harness_cp.evaluator_verdict import EvaluatorVerdictMalformedError
from harness_cp.gate_level_rule import GateLevel
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.persona_engine_hitl_matrix import SynchronyClass
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.validator_fail_transient_staircase import CrossTrustBoundaryState
from harness_is.path_class_registry import PathClass
from harness_is.path_resolver import PathResolver
from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier
from harness_runtime.config.path_bindings import build_path_binding
from harness_runtime.config.state_placement import (
    StatePlacementRefusal,
    StateRootPlacementError,
    VerifiedStateRoot,
    bootstrap_state_root,
)
from harness_runtime.lifecycle.cp_is_wiring import materialize_cp_is_wiring_stage
from harness_runtime.lifecycle.evaluator_verdict import read_ollama_evaluator_verdict
from harness_runtime.lifecycle.hitl_placement import RuntimeHITLPlacementRegistry
from harness_runtime.lifecycle.hitl_tool_loop import (
    HITLGateDecision,
    HITLToolCallAssessment,
    HITLToolLoopCallResult,
    HITLToolLoopContext,
    HITLToolRefusalReason,
    ModelToolCall,
    RuntimeHITLToolLoop,
)
from harness_runtime.lifecycle.state_ledger import materialize_state_ledger
from harness_runtime.types import (
    CollectorConfig,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
    StatePlacementConfig,
)

from .test_hitl_tool_loop import _Auditor

# --- C-RT-36 §14.25: the persistent state root lives outside every Git checkout ----------


def _ext4(_path: Path) -> str | None:
    return "ext4"


@pytest.fixture
def git_free(tmp_path: Path) -> Iterator[Path]:
    """A scratch with no `.git` at or above it, as `test_state_placement.world` chooses one.

    The verifier refuses any root under a checkout, so a `tmp_path` below one is unusable;
    fall back to /dev/shm like the existing suite, and fail (never skip) when neither is free.
    """
    for parent in (tmp_path, Path("/dev/shm")):
        if parent.is_dir() and not any(
            os.path.lexists(p / ".git") for p in (parent, *parent.parents)
        ):
            scratch = Path(tempfile.mkdtemp(prefix="c-rt-36-", dir=parent))
            break
    else:
        pytest.fail("no scratch directory free of a .git ancestor for the C-RT-36 witnesses")
    try:
        yield scratch
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def _checkout(tmp_path: Path) -> tuple[Path, Path]:
    """A fake checkout and a private state directory beside it, under a Git-free scratch."""
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / ".harness").mkdir()
    state = tmp_path / "home" / "state"
    state.mkdir(parents=True, mode=0o700)
    os.chmod(tmp_path / "home", 0o755)
    return repo, state


def _bootstrap(repo: Path, root: Path) -> VerifiedStateRoot:
    ledger = {
        "path_class": "STATE_LEDGER",
        "workflow_class": "software-engineering",
        "deployment_surface": "local-development",
        "path": str(root / "ledger"),
    }
    return bootstrap_state_root(
        StatePlacementConfig(state_root=root, forbidden_roots=()),
        repository_root=repo,
        worktree_base=repo / ".harness" / "worktrees",
        path_bindings=PathBindingConfig(raw_entries=(ledger,)),
        filesystem_type=_ext4,
    )


def test_c_rt_36_a_state_root_inside_the_checkout_is_refused_and_nothing_is_created(
    git_free: Path,
) -> None:
    repo, _state = _checkout(git_free)
    inside = repo / ".harness" / "state"

    with pytest.raises(StateRootPlacementError) as refused:
        _bootstrap(repo, inside)

    assert refused.value.reason is StatePlacementRefusal.INSIDE_CHECKOUT
    assert not inside.exists()


def test_c_rt_36_a_private_root_outside_the_checkout_is_verified(git_free: Path) -> None:
    repo, state = _checkout(git_free)

    assert isinstance(_bootstrap(repo, state), VerifiedStateRoot)


# --- C-RT-37 §14.26: a completed Ollama reply is a strict evaluator verdict, or refused ----


def _reply(content: str, **overrides: object) -> dict[str, object]:
    reply: dict[str, object] = {
        "done": True,
        "done_reason": "stop",
        "message": {"role": "assistant", "content": content},
    }
    reply.update(overrides)
    return reply


def test_c_rt_37_a_strict_json_verdict_is_accepted() -> None:
    verdict = read_ollama_evaluator_verdict(
        _reply(json.dumps({"accepted": False, "feedback": "cite the spec section"}))
    )

    assert (verdict.accepted, verdict.feedback) == (False, "cite the spec section")


@pytest.mark.parametrize(
    "reply",
    [
        _reply('{"accepted": "true"}'),
        _reply('{"accepted": true, "accepted": false}'),
        _reply('{"accepted": true}', done_reason="length"),
        _reply('{"accepted": true}', done=False),
        _reply("accepted"),
    ],
    ids=["string-boolean", "duplicate-key", "truncated", "incomplete", "not-json"],
)
def test_c_rt_37_a_malformed_reply_is_refused_without_echoing_model_text(
    reply: dict[str, object],
) -> None:
    with pytest.raises(EvaluatorVerdictMalformedError) as refused:
        read_ollama_evaluator_verdict(reply)

    assert "accepted" not in str(refused.value)
    assert refused.value.__cause__ is None and refused.value.__context__ is None


# --- C-RT-38 §14.27: an uncomputable or malformed gate level refuses; nothing asks or runs ---


#: A foreign value an evaluator could return as a level; the loop must not trust it as one.
_STRING_LEVEL: Any = "AUTO"


class _Gate:
    """Records every operator prompt; always answers APPROVE."""

    def __init__(self) -> None:
        self.asked: list[tuple[ModelToolCall, frozenset[HITLResponse]]] = []

    async def decide(
        self,
        *,
        call: ModelToolCall,
        context: HITLToolLoopContext,
        palette: frozenset[HITLResponse],
    ) -> HITLGateDecision:
        _ = context
        self.asked.append((call, palette))
        return HITLGateDecision(response=HITLResponse.APPROVE)


class _Dispatcher:
    """Records every tool dispatch."""

    def __init__(self) -> None:
        self.dispatched: list[ModelToolCall] = []

    async def dispatch(self, call: ModelToolCall, context: HITLToolLoopContext) -> dict[str, Any]:
        _ = context
        self.dispatched.append(call)
        return {"ok": True}


def _run(tmp_path: Path, assess: Any) -> tuple[HITLToolLoopCallResult, _Gate, _Dispatcher]:
    """One model tool call through the real loop, CP/IS wiring and state ledger."""
    resolver = PathResolver(
        build_path_binding(
            PathBindingConfig(
                raw_entries=(
                    {
                        "path_class": PathClass.STATE_LEDGER,
                        "workflow_class": WorkloadClass.SOFTWARE_ENGINEERING,
                        "deployment_surface": DeploymentSurface.LOCAL_DEVELOPMENT,
                        "path": str(tmp_path / "state.jsonl"),
                    },
                )
            )
        )
    )
    ledger = materialize_state_ledger(
        resolver,
        workflow_class=WorkloadClass.SOFTWARE_ENGINEERING,
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        actor=Actor(actor_class=ActorClass.AGENT, actor_id="c-rt-38-witness"),
    )
    config = RuntimeConfig(
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        repository_root=tmp_path,
        path_bindings=PathBindingConfig(),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4317"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
    )
    wiring = materialize_cp_is_wiring_stage(config, ledger, lambda: Identifier("a" * 64)).wiring
    gate, dispatcher = _Gate(), _Dispatcher()
    loop = RuntimeHITLToolLoop(
        wiring=wiring,
        placement_registry=RuntimeHITLPlacementRegistry(),
        assess=assess,
        gate=gate,
        dispatcher=dispatcher,
        response_auditor=_Auditor(),
    )
    call = ModelToolCall(
        tool_call_id="call-1",
        tool="search",
        server="model-claimed-host",
        arguments={"query": "c-rt-38"},
        provider="anthropic",
        model="fixture-model",
    )
    context = HITLToolLoopContext(
        workflow_id="wf-c-rt-38",
        step_id="step-1",
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        cell_synchrony_class=SynchronyClass.SYNC_BLOCKING,
        cross_trust_boundary_state=CrossTrustBoundaryState.NONE,
        actor=ActorIdentity("c-rt-38-witness"),
        inherited_gate_floor=GateLevel.AUTO,
    )
    [result] = asyncio.run(loop.run_tool_calls([call], context))
    return result, gate, dispatcher


@pytest.mark.parametrize(
    "malformed",
    [
        None,
        GateLevel.AUTO,
        HITLToolCallAssessment(level=GateLevel.AUTO, owner=""),
        HITLToolCallAssessment(level=_STRING_LEVEL, owner="registry-host"),
    ],
    ids=["none", "bare-level", "empty-owner", "string-level"],
)
def test_c_rt_38_a_malformed_assessment_is_refused_without_prompt_or_dispatch(
    tmp_path: Path, malformed: object
) -> None:
    result, gate, dispatcher = _run(tmp_path, lambda _call, _context: malformed)

    assert result.refusal is not None
    assert result.refusal.reason is HITLToolRefusalReason.MALFORMED_GATE_LEVEL
    assert (gate.asked, dispatcher.dispatched, result.dispatched) == ([], [], False)


def test_c_rt_38_an_evaluator_that_raises_is_refused_without_prompt_or_dispatch(
    tmp_path: Path,
) -> None:
    def fails(_call: ModelToolCall, _context: HITLToolLoopContext) -> HITLToolCallAssessment:
        raise LookupError("registry unavailable")

    result, gate, dispatcher = _run(tmp_path, fails)

    assert result.refusal is not None
    assert result.refusal.reason is HITLToolRefusalReason.EVALUATOR_FAILED
    assert (gate.asked, dispatcher.dispatched, result.dispatched) == ([], [], False)


def test_c_rt_38_deny_asks_only_reject_or_respond_and_never_dispatches(tmp_path: Path) -> None:
    """Control: the gate sink records a prompt, yet an APPROVE reply to DENY runs nothing."""
    result, gate, dispatcher = _run(
        tmp_path, lambda _call, _context: HITLToolCallAssessment(GateLevel.DENY, "registry-host")
    )

    [(asked, palette)] = gate.asked
    assert asked.server == "registry-host"
    assert palette == frozenset({HITLResponse.REJECT, HITLResponse.RESPOND})
    assert (dispatcher.dispatched, result.dispatched) == ([], False)


def test_c_rt_38_an_auto_call_dispatches_under_the_registry_owner(tmp_path: Path) -> None:
    """Control: the dispatch sink records a call, under the assessed owner, not the model's."""
    result, gate, dispatcher = _run(
        tmp_path, lambda _call, _context: HITLToolCallAssessment(GateLevel.AUTO, "registry-host")
    )

    assert result.refusal is None and result.dispatched
    assert gate.asked == []
    assert [call.server for call in dispatcher.dispatched] == ["registry-host"]
