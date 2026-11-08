"""U-RT-85 / Trial193.4h4 — Real-bootstrap e2e: configured validators decide workflow output.

Exercises the operator path end-to-end with no framework substitution:
a TOML `validator_framework_config` loaded by `RuntimeConfigSource` →
`run_bootstrap` (stage-4 factory resolves and constructs the bound validator
classes) → the bootstrapped `ctx.validator_framework` → the sync CP
`execute_workflow` driver, run on a worker thread exactly as the MCP
`run_workflow` tool runs it.

The fixture validator decides from the step's actual dispatched output, so a
PASS, a PERMANENT_FAIL and an ESCALATE each come from what the step produced,
not from a canned framework. Coverage:

- **Opt-out** (`validator_framework_config` unset): `ctx.validator_framework
  is None`; spec §14.13.5 invariant 2.
- **PASS** proceeds and the step output reaches `final_state`.
- **PERMANENT_FAIL** returns a typed `CP-FAIL-VALIDATOR-PERMANENT` failure
  with no `final_state`.
- **ESCALATE** opens the AskUserQuestion surface offering only responses
  inside the validator brief's proposed palette.
- **Refusal**: a binding whose class cannot be resolved stops bootstrap
  instead of materializing a framework that reports success.

Retained 4h4 gap (not attested here): the driver passes
`CrossTrustBoundaryState.NONE` to the escalation composer, so inherited
cross-trust palette restriction is not proven by the ESCALATE case.
"""

from __future__ import annotations

import asyncio
from functools import partial
from pathlib import Path
from typing import Any

import pytest
from harness_core.identity import StepID
from harness_core.persona_tier import PersonaTier
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.validator_framework import open_validator_run
from harness_cp.validator_framework_types import (
    HITLEscalationBrief,
    ValidatorFailClass,
    ValidatorOutcome,
    ValidatorResult,
)
from harness_cp.workflow_driver import execute_workflow
from harness_cp.workflow_driver_types import (
    RunResult,
    RunStatus,
    StepKind,
    WorkflowStep,
)
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_runtime.bootstrap import run_bootstrap
from harness_runtime.config_source import RuntimeConfigSource
from harness_runtime.lifecycle.ask_user_question_surface import (
    AskUserQuestionResult,
    AskUserQuestionSurface,
)
from harness_runtime.lifecycle.validator_framework_types import (
    ValidatorBinding,
    ValidatorFrameworkConfig,
)
from harness_runtime.types import HarnessContext, RuntimeConfig

from .conftest import WORKLOAD, build_config

_ESCALATION_PALETTE = frozenset({HITLResponse.APPROVE, HITLResponse.REJECT})


class _OutputVerdictValidator:
    """Operator validator judging the `verdict` the step actually produced."""

    def __init__(self, *, accept: str) -> None:
        self._accept = accept

    async def validate(
        self,
        step: WorkflowStep,
        step_result: Any,
        *,
        step_context: Any,
    ) -> ValidatorResult:
        _ = step_context
        verdict = step_result["verdict"]
        if verdict == self._accept:
            return ValidatorResult(outcome=ValidatorOutcome.PASS)
        if verdict == "unsure":
            return ValidatorResult(
                outcome=ValidatorOutcome.ESCALATE,
                fail_class=ValidatorFailClass.SCHEMA_VIOLATION,
                escalation_brief=HITLEscalationBrief(
                    parent_step_id=str(step.step_id),
                    parent_action_id="validator-e2e",
                    fail_class=ValidatorFailClass.SCHEMA_VIOLATION,
                    escalation_reason=f"step produced verdict {verdict!r}",
                    proposed_response_palette=_ESCALATION_PALETTE,
                ),
            )
        return ValidatorResult(
            outcome=ValidatorOutcome.PERMANENT_FAIL,
            fail_class=ValidatorFailClass.SCHEMA_VIOLATION,
        )


class _VerdictDispatcher:
    """Produces the step payload's verdict as the step output."""

    def dispatch(
        self, binding: Any, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        _ = binding, step_context
        return {"verdict": step.step_payload["verdict"]}


class _SingleKindRegistry:
    def __init__(self, dispatcher: Any) -> None:
        self._dispatcher = dispatcher

    def lookup(self, step_kind: Any) -> Any:
        _ = step_kind
        return self._dispatcher


class _RecordingSurface(AskUserQuestionSurface):
    def __init__(self) -> None:
        self.options: list[list[HITLResponse]] = []

    async def ask(self, prompt: str, options: Any, timeout: float | None) -> AskUserQuestionResult:
        _ = prompt, timeout
        self.options.append(list(options))
        return AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=1.0)


_STEPS = ("step-accepted", "step-rejected", "step-escalated")
_VALIDATOR_REF = f"{__name__}:{_OutputVerdictValidator.__qualname__}"

_TOML = "\n".join(
    [
        "[runtime.validator_framework_config]",
        *(
            f'[[runtime.validator_framework_config.bindings]]\nstep_id = "{step_id}"\n'
            f'class_qualified_name = "{_VALIDATOR_REF}"\n'
            'params = { accept = "ok" }'
            for step_id in _STEPS
        ),
    ]
)


def _load_toml_config(tmp_path: Path) -> RuntimeConfig:
    """Operator TOML for the validator catalog; the test substrate for the rest."""
    config_file = tmp_path / "harness.toml"
    config_file.write_text(_TOML)
    substrate = {
        name: value
        for name, value in build_config(tmp_path)
        if name != "validator_framework_config"
    }
    return RuntimeConfigSource.load(config_file=config_file, cli_overrides=substrate)


def _manifest(workflow_id: str) -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WORKLOAD,
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=TopologyPattern.SINGLE_THREADED_LINEAR,
        layer_budgets=(),
        fallback_chain=FallbackChain(
            primary=ProviderCandidate(
                provider="anthropic", model="claude-haiku-4-5", family=ProviderFamily.ANTHROPIC
            ),
            same_family=(),
            cross_family=(),
            terminal=None,
        ),
        hitl_placements=(),
        per_step_overrides={},
    )


async def _run_single_step(ctx: HarnessContext, step_id: str, verdict: str) -> RunResult:
    from opentelemetry.trace import NoOpTracer

    # patched_runtime's fake tracer provider has no get_tracer; the driver needs one.
    ctx.tracer_provider.get_tracer = lambda _name, /: NoOpTracer()  # type: ignore[attr-defined]
    step = WorkflowStep(
        step_id=StepID(step_id),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={"verdict": verdict},
    )
    assert ctx.validator_framework is not None
    # Runtime v1.138 §14.13.8(2): each run opens its own binding over the bootstrap
    # framework on this loop, as `run_workflow` ingress does.
    validator_run = open_validator_run(
        ctx.validator_framework,
        result_timeout_seconds=ctx.config.step_dispatch_timeout_seconds,
    )
    return await asyncio.to_thread(
        partial(
            execute_workflow,
            manifest_entry=_manifest(f"wf-{step_id}"),
            steps=(step,),
            run_id=f"run-{step_id}",
            ctx=ctx,  # type: ignore[arg-type]
            default_model_binding=ModelBinding(provider="anthropic", model="claude-haiku-4-5"),
            step_dispatchers=_SingleKindRegistry(_VerdictDispatcher()),  # type: ignore[arg-type]
            validator_run=validator_run,
        )
    )


@pytest.mark.asyncio
async def test_validator_framework_e2e_opt_out_branch(
    tmp_path: Path,
    patched_runtime: dict[str, Any],
) -> None:
    _ = patched_runtime
    config = build_config(tmp_path)
    assert config.validator_framework_config is None

    ctx = await run_bootstrap(config, workload_class=WORKLOAD)

    assert ctx.validator_framework is None


@pytest.mark.asyncio
async def test_toml_bound_validator_passes_rejects_and_escalates_real_output(
    tmp_path: Path,
    patched_runtime: dict[str, Any],
) -> None:
    _ = patched_runtime
    config = _load_toml_config(tmp_path)
    assert config.validator_framework_config == ValidatorFrameworkConfig(
        bindings=tuple(
            ValidatorBinding(
                step_id=StepID(step_id),
                class_qualified_name=_VALIDATOR_REF,
                params={"accept": "ok"},
            )
            for step_id in _STEPS
        )
    )
    surface = _RecordingSurface()
    bootstrapped = await run_bootstrap(config, workload_class=WORKLOAD)
    ctx = bootstrapped.model_copy(update={"ask_user_question_surface": surface})

    accepted = await _run_single_step(ctx, "step-accepted", "ok")
    assert accepted.status == RunStatus.SUCCESS, accepted.fail_class
    assert accepted.final_state is not None
    assert {"verdict": "ok"} in accepted.final_state.values()

    rejected = await _run_single_step(ctx, "step-rejected", "wrong")
    assert rejected.status == RunStatus.FAILED
    assert rejected.final_state is None
    assert rejected.fail_class is not None
    assert rejected.fail_class.startswith("CP-FAIL-VALIDATOR-PERMANENT")

    assert surface.options == []
    escalated = await _run_single_step(ctx, "step-escalated", "unsure")
    assert len(surface.options) == 1
    offered = set(surface.options[0])
    assert offered and offered <= _ESCALATION_PALETTE
    # The recording surface approves, so the escalated step proceeds.
    assert escalated.status == RunStatus.SUCCESS, escalated.fail_class


@pytest.mark.asyncio
async def test_unresolvable_binding_refuses_bootstrap(
    tmp_path: Path,
    patched_runtime: dict[str, Any],
) -> None:
    _ = patched_runtime
    config = build_config(tmp_path).model_copy(
        update={
            "validator_framework_config": ValidatorFrameworkConfig(
                bindings=(
                    ValidatorBinding(
                        step_id=StepID("step-accepted"),
                        class_qualified_name=f"{__name__}:_NoSuchValidator",
                    ),
                )
            )
        }
    )

    with pytest.raises(Exception, match="RT-FAIL-VALIDATOR-STAGE-MATERIALIZE"):
        await run_bootstrap(config, workload_class=WORKLOAD)
