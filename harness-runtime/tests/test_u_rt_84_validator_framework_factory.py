"""U-RT-84 — `materialize_validator_framework_stage` factory + stage-4 wiring tests.

ACs per runtime plan v2.17 §1 U-RT-84:

1. Factory authored with signature
   `async def materialize_validator_framework_stage(config) → ValidatorFramework | None`.
2. Opt-out branch: `config.validator_framework_config is None` → factory
   returns `None` unconditionally.
3. Opt-in branch (Trial193.4h4): every `ValidatorBinding` resolves to an
   operator `Validator` constructed with its params; the factory returns the
   async-Protocol `ConcreteValidatorFramework` itself (Runtime v1.138
   §14.13.2/.5), whose registry dispatches those validators; each run's sync
   `ValidatorRunBinding` is opened over it (§14.13.8). Unresolvable, failing,
   non-Protocol or sync-`validate` bindings raise
   `ValidatorFrameworkStageMaterializeError` before any dispatch.
4. Stage-4 OD-bucket wiring: factory invocation appended AFTER tracer +
   collector + cost + audit in `stage_4_od.py`; output bound to
   `ctx.validator_framework`.
5. `HarnessContext.validator_framework` field type narrowed `object | None`
   → `ValidatorFramework | None` (verified by schema inspection +
   pyright-clean import).
6. `ValidatorFrameworkStageMaterializeError` typed exception authored;
   carries the `RT-FAIL-VALIDATOR-STAGE-MATERIALIZE:` prefix when raised.
7. Spec §14.13.5 invariants: single instance per bootstrap (factory bound
   exactly once at stage 4), empty-sentinel preserves backward compat,
   CP-canonical Protocol satisfaction, no validator-composer arc
   resolutions.
8. Importable.
"""

from __future__ import annotations

import asyncio
import inspect
from pathlib import Path
from typing import Any

import pytest
from harness_core.deployment_surface import DeploymentSurface
from harness_core.identity import StepID
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.validator_framework import ConcreteValidatorFramework, open_validator_run
from harness_cp.validator_framework_types import (
    ValidatorBurdenLedger,
    ValidatorFailClass,
    ValidatorFramework,
    ValidatorNextAction,
    ValidatorOutcome,
    ValidatorResult,
)
from harness_cp.workflow_driver_types import StepKind, WorkflowStep
from harness_runtime.bootstrap.factories.validator_framework_factory import (
    ValidatorFrameworkStageMaterializeError,
    materialize_validator_framework_stage,
)
from harness_runtime.config_source import RuntimeConfigLoadError, RuntimeConfigSource
from harness_runtime.lifecycle.validator_framework_types import (
    ValidatorBinding,
    ValidatorFrameworkConfig,
)
from harness_runtime.types import (
    CollectorConfig,
    HarnessContext,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
)


def _minimal_runtime_config_kwargs(tmp_path: Path) -> dict[str, Any]:
    return {
        "deployment_surface": DeploymentSurface.LOCAL_DEVELOPMENT,
        "repository_root": tmp_path,
        "path_bindings": PathBindingConfig(),
        "provider_secrets": ProviderSecretsConfig(),
        "otel": OTelConfig(otlp_endpoint="http://localhost:4318"),
        "collector": CollectorConfig(),
        "default_topology": TopologyPattern.SINGLE_THREADED_LINEAR,
    }


# AC #1 — factory signature.


def test_factory_is_async() -> None:
    assert inspect.iscoroutinefunction(materialize_validator_framework_stage)


def test_factory_signature_accepts_config_returns_framework_or_none() -> None:
    sig = inspect.signature(materialize_validator_framework_stage)
    params = list(sig.parameters)
    # Per spec v1.18 §14.13.1 first positional is `config`. Per CP spec
    # v1.24 §28.10.5 mechanism (a) the factory accepts optional kw-only
    # cost-attribution substrates (rate_table, cost_chain, audit_writer).
    assert params[0] == "config", (
        f"factory signature first param must be `config` per spec §14.13.1; got {params}"
    )
    # Cost-attribution substrates per U-OD-40 hook binding extension.
    for name in ("rate_table", "cost_chain", "audit_writer"):
        assert name in params, (
            f"factory must accept kw-only `{name}` per CP spec v1.24 "
            f"§28.10.5 mechanism (a); got {params}"
        )
        assert sig.parameters[name].kind == inspect.Parameter.KEYWORD_ONLY
        assert sig.parameters[name].default is None
    # Return annotation is `ValidatorFramework | None` — str-rendered.
    return_annotation = sig.return_annotation
    rendered = str(return_annotation)
    assert "ValidatorFramework" in rendered
    assert "None" in rendered


# AC #2 — opt-out branch.


@pytest.mark.asyncio
async def test_factory_returns_none_when_config_is_none(tmp_path: Path) -> None:
    config = RuntimeConfig(
        **_minimal_runtime_config_kwargs(tmp_path),
        validator_framework_config=None,
    )
    result = await materialize_validator_framework_stage(config)
    assert result is None


@pytest.mark.asyncio
async def test_factory_returns_none_when_field_omitted(tmp_path: Path) -> None:
    """Backwards-compatibility branch: caller never supplied the field."""
    config = RuntimeConfig(**_minimal_runtime_config_kwargs(tmp_path))
    assert await materialize_validator_framework_stage(config) is None


# AC #3 — opt-in branch: operator bindings become dispatchable validators.


class _ThresholdValidator:
    """Passes a step whose output `score` reaches the configured threshold."""

    def __init__(self, *, threshold: int) -> None:
        self.threshold = threshold

    async def validate(
        self, step: WorkflowStep, step_result: Any, *, step_context: Any
    ) -> ValidatorResult:
        _ = step, step_context
        if step_result["score"] >= self.threshold:
            return ValidatorResult(outcome=ValidatorOutcome.PASS)
        return ValidatorResult(
            outcome=ValidatorOutcome.PERMANENT_FAIL,
            fail_class=ValidatorFailClass.SCHEMA_VIOLATION,
        )


class _SyncValidateValidator:
    def validate(self, step: Any, step_result: Any, *, step_context: Any) -> ValidatorResult:
        _ = step, step_result, step_context
        return ValidatorResult(outcome=ValidatorOutcome.PASS)


class _NotAValidator:
    pass


class _ExplodingValidator:
    def __init__(self, *, token: str) -> None:
        raise RuntimeError(f"cannot use {token}")


_NOT_A_CLASS = object()


def _ref(name: str) -> str:
    return f"{__name__}:{name}"


def _opt_in_config(tmp_path: Path, *bindings: ValidatorBinding) -> RuntimeConfig:
    return RuntimeConfig(
        **_minimal_runtime_config_kwargs(tmp_path),
        validator_framework_config=ValidatorFrameworkConfig(bindings=bindings),
    )


def _step(step_id: str) -> WorkflowStep:
    return WorkflowStep(step_id=StepID(step_id), step_kind=StepKind.INFERENCE_STEP, step_payload={})


@pytest.mark.asyncio
async def test_factory_dispatches_bound_validator_on_step_output(tmp_path: Path) -> None:
    """The configured class and params decide the outcome from the real output."""
    config = _opt_in_config(
        tmp_path,
        ValidatorBinding(
            step_id=StepID("score"),
            class_qualified_name=_ref(_ThresholdValidator.__qualname__),
            params={"threshold": 5},
        ),
    )
    framework = await materialize_validator_framework_stage(config)

    assert isinstance(framework, ConcreteValidatorFramework)
    # §14.13.5 invariant 3 — the returned value itself is the async CP Protocol.
    assert isinstance(framework, ValidatorFramework)
    assert inspect.iscoroutinefunction(framework.evaluate)
    burden = ValidatorBurdenLedger()
    passed = await framework.evaluate(
        _step("score"),
        {"score": 7},
        step_context=None,
        burden=burden,  # type: ignore[arg-type]
    )
    failed = await framework.evaluate(
        _step("score"),
        {"score": 4},
        step_context=None,
        burden=burden,  # type: ignore[arg-type]
    )
    assert passed.next_action is ValidatorNextAction.PROCEED
    assert failed.next_action is ValidatorNextAction.ABORT


@pytest.mark.asyncio
async def test_run_binding_evaluates_from_driver_worker_thread(tmp_path: Path) -> None:
    """§14.13.8 — a binding opened over the factory's framework is what the sync
    driver calls from `asyncio.to_thread`."""
    config = _opt_in_config(
        tmp_path,
        ValidatorBinding(
            step_id=StepID("score"),
            class_qualified_name=f"{__name__}.{_ThresholdValidator.__qualname__}",
            params={"threshold": 1},
        ),
    )
    framework = await materialize_validator_framework_stage(config)
    assert framework is not None
    binding = open_validator_run(framework, result_timeout_seconds=5.0)

    evaluation = await asyncio.to_thread(
        binding.evaluate,
        _step("score"),
        {"score": 1},
        step_context=None,  # type: ignore[arg-type]
    )
    assert evaluation.result.outcome is ValidatorOutcome.PASS


@pytest.mark.parametrize(
    ("class_name", "params", "reason"),
    [
        ("_NoSuchValidator", {}, "did not resolve"),
        ("_NOT_A_CLASS", {}, "did not resolve"),
        (_ThresholdValidator.__qualname__, {}, "raised TypeError during construction"),
        (_ThresholdValidator.__qualname__, {"threshold": 1, "extra": 2}, "raised TypeError"),
        (_NotAValidator.__qualname__, {}, "does not satisfy the Validator Protocol"),
        (_SyncValidateValidator.__qualname__, {}, "does not satisfy the Validator Protocol"),
    ],
)
@pytest.mark.asyncio
async def test_factory_refuses_undispatchable_binding(
    tmp_path: Path, class_name: str, params: dict[str, int], reason: str
) -> None:
    config = _opt_in_config(
        tmp_path,
        ValidatorBinding(
            step_id=StepID("step"), class_qualified_name=_ref(class_name), params=params
        ),
    )
    with pytest.raises(ValidatorFrameworkStageMaterializeError) as excinfo:
        await materialize_validator_framework_stage(config)
    message = str(excinfo.value)
    assert message.startswith("RT-FAIL-VALIDATOR-STAGE-MATERIALIZE:")
    assert reason in message
    assert "'step'" in message


@pytest.mark.asyncio
async def test_factory_construction_failure_does_not_echo_params(tmp_path: Path) -> None:
    config = _opt_in_config(
        tmp_path,
        ValidatorBinding(
            step_id=StepID("step"),
            class_qualified_name=_ref(_ExplodingValidator.__qualname__),
            params={"token": "s3cr3t-value"},
        ),
    )
    with pytest.raises(ValidatorFrameworkStageMaterializeError) as excinfo:
        await materialize_validator_framework_stage(config)
    assert "RuntimeError" in str(excinfo.value)
    assert "s3cr3t-value" not in str(excinfo.value)


def test_config_refuses_empty_catalog() -> None:
    with pytest.raises(ValueError, match="at least one validator"):
        ValidatorFrameworkConfig(bindings=())


def test_config_refuses_step_bound_twice() -> None:
    with pytest.raises(ValueError, match=r"\['dup'\] more than once"):
        ValidatorFrameworkConfig(
            bindings=(
                ValidatorBinding(step_id=StepID("dup"), class_qualified_name=_ref("A")),
                ValidatorBinding(step_id=StepID("ok"), class_qualified_name=_ref("B")),
                ValidatorBinding(step_id=StepID("dup"), class_qualified_name=_ref("C")),
            )
        )


def test_toml_bindings_load_into_runtime_config(tmp_path: Path) -> None:
    config_file = tmp_path / "harness.toml"
    config_file.write_text(
        "[[runtime.validator_framework_config.bindings]]\n"
        'step_id = "score"\n'
        'class_qualified_name = "pkg.mod:Check"\n'
        'params = { threshold = 3, strict = true, ratio = 0.5, label = "x" }\n'
    )
    config = RuntimeConfigSource.load(
        config_file=config_file, cli_overrides=_minimal_runtime_config_kwargs(tmp_path)
    )
    assert config.validator_framework_config == ValidatorFrameworkConfig(
        bindings=(
            ValidatorBinding(
                step_id=StepID("score"),
                class_qualified_name="pkg.mod:Check",
                params={"threshold": 3, "strict": True, "ratio": 0.5, "label": "x"},
            ),
        )
    )


@pytest.mark.parametrize(
    ("toml", "error"),
    [
        ("[runtime.validator_framework_config]\nbindings = []\n", "at least one validator"),
        (
            "[[runtime.validator_framework_config.bindings]]\n"
            'step_id = "s"\nclass_qualified_name = "m:C"\nparms = {}\n',
            "parms",
        ),
        (
            "[[runtime.validator_framework_config.bindings]]\n"
            'step_id = "s"\nclass_qualified_name = "m:C"\nparams = { n = [1] }\n',
            "params",
        ),
    ],
)
def test_toml_refuses_malformed_catalog(tmp_path: Path, toml: str, error: str) -> None:
    config_file = tmp_path / "harness.toml"
    config_file.write_text(toml)
    with pytest.raises(RuntimeConfigLoadError, match=error):
        RuntimeConfigSource.load(
            config_file=config_file, cli_overrides=_minimal_runtime_config_kwargs(tmp_path)
        )


# AC #4 — stage-4 wiring source-inspection.


def test_stage_4_od_invokes_factory_after_audit_writer() -> None:
    """AC #4 + spec §14.13.3 — validator framework is the FINAL stage-4 binding.

    Source-level verification: the factory invocation appears after
    `audit = materialize_audit_writer_stage(...)` in the execute body, and
    no other stage-4 binding follows. Integration test exercising full
    bootstrap lives at U-RT-85.
    """
    from harness_runtime.bootstrap import stage_4_od

    source = inspect.getsource(stage_4_od.execute)
    # Factory is invoked (signature widened at U-OD-40 to thread cost-
    # attribution substrates per CP spec v1.24 §28.10.5 mechanism (a) —
    # accept any positional-or-kw invocation containing `config`).
    assert "materialize_validator_framework_stage(" in source
    assert "config" in source[source.find("materialize_validator_framework_stage") :]
    # And bound to ctx.validator_framework.
    assert "ctx.validator_framework = " in source
    # And the invocation comes AFTER audit_writer.
    audit_idx = source.find("materialize_audit_writer_stage")
    validator_idx = source.find("materialize_validator_framework_stage")
    assert audit_idx > 0
    assert validator_idx > audit_idx, (
        "validator framework factory must appear AFTER audit_writer per "
        "spec §14.13.3 ordering pin (validator framework as final stage-4 binding)"
    )


# AC #5 — HarnessContext field type narrowing.


def test_harness_context_validator_framework_field_is_the_async_protocol() -> None:
    """AC #5 (Runtime v1.138 §14.13.2) — the context carries the shared async CP
    `ValidatorFramework`, or `None` at opt-out; sync bindings live per run."""
    field = HarnessContext.model_fields["validator_framework"]
    assert field.annotation == ValidatorFramework | None


def test_freeze_signature_carries_validator_framework_kwarg() -> None:
    """AC #4 plumbing — _MutableHarnessContext.freeze passes validator_framework
    through to HarnessContext."""
    from harness_runtime.bootstrap import mutable_context

    freeze_source = inspect.getsource(mutable_context._MutableHarnessContext.freeze)
    assert "validator_framework=self.validator_framework" in freeze_source


# AC #6 — typed exception authored.


def test_fail_class_exception_authored() -> None:
    assert issubclass(ValidatorFrameworkStageMaterializeError, Exception)


def test_fail_class_prefix_documented_in_message_convention() -> None:
    """Per spec §14.13.4 fail class — the exception message convention carries
    the RT-FAIL-VALIDATOR-STAGE-MATERIALIZE: prefix when raised. Verified via
    source inspection: the only raise site uses this prefix."""
    source = inspect.getsource(materialize_validator_framework_stage)
    if "raise ValidatorFrameworkStageMaterializeError" in source:
        assert "RT-FAIL-VALIDATOR-STAGE-MATERIALIZE:" in source


# AC #7 — invariant 4 (no §14.8.2 touch).


def test_no_validator_composer_arc_resolutions() -> None:
    """AC #7 invariant 4 — factory module does NOT import any §14.8.2 surface
    (VALIDATOR_ESCALATION, _hitl_required composer, palette restriction).
    Reading A scope discipline."""
    import harness_runtime.bootstrap.factories.validator_framework_factory as mod

    source = inspect.getsource(mod)
    assert "VALIDATOR_ESCALATION" not in source
    assert "_hitl_required" not in source
    assert "PALETTE_RESTRICTION" not in source


# AC #8 — importable.


def test_carriers_importable() -> None:
    assert callable(materialize_validator_framework_stage)
    assert ValidatorFrameworkStageMaterializeError is not None
    assert ValidatorFramework is not None
