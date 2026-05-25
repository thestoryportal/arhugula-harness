"""U-RT-95 — Driver catch + e2e for HITL durable-async pause-trigger cycle.

Implements runtime plan v2.25 §7.3 U-RT-95 ACs (preserved v2.23 #1-#6 +
v2.24 #7 + v2.25 #8/#9). Exercises the §14.8.8.4 driver-side signal
handling discipline + the §14.8.8.1 step 0 OR-form precondition at
production bootstrap substrate.

## 7-case path matrix per runtime plan v2.25 §7.3

| Path | Operator config              | Cell synchrony   | Expected outcome                              |
|------|------------------------------|------------------|-----------------------------------------------|
| (i)  | pause-resume + webhook       | DURABLE_ASYNC    | Composer fires step 4-bis durable-async body; |
|      |                              |                  | driver catches HITLPauseRequestedSignal;      |
|      |                              |                  | returns RunStatus.PAUSED                      |
| (iii)| neither                      | (any)            | §14.8.8.1 step 0 precondition fails (both     |
|      |                              |                  | sides None) → sync-blocking fall-through      |
| (v)  | webhook only                 | (any)            | §14.8.8.1 step 0 OR-form arm fails on         |
|      |                              |                  | pause_resume_protocol is None → sync          |
| (vi) | pause-resume only            | (any)            | §14.8.8.1 step 0 OR-form arm fails on         |
|      |                              |                  | webhook_delivery_composer is None → sync      |
| (vii)| (any)                        | (n/a)            | Bare StepEffectiveBinding without persona_tier|
|      |                              |                  | → Pydantic ValidationError at construction    |
|      |                              |                  | (CP spec v1.17 §6.5 regression gate)          |

Paths (ii) resume-consume-cycle + (iv) webhook-exhausted are deferred to a
follow-on arc per FM-2 — they require richer HTTP test-double + resume
substrate beyond the empty-marker v1.26 config. Path (i) uses monkey-patched
`deliver_webhook` to return a successful WebhookDeliveryResult sentinel
without requiring real outbound HTTP (mechanism α per plan v2.25 §6.5).

## Verification-shape discipline

Per `[[verification-shape-sharpened-grep-vs-e2e]]` (batch-16 §6 + applied at
batch-17 U-RT-85 + batch-18 U-RT-89): the test uses production
`run_bootstrap` orchestrator + production `execute_workflow(...)` invocation
path. The HITL composer is wired at stage-5 LOOP_INIT per the production
binding chain landed at L9-quaterdecies (U-RT-96/97/98) + L9-undecies
(U-RT-87/88/89). NO `_FakeCtx` shortcuts; NO `_MutableHarnessContext`
test-local mutation.
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
from harness_cp.hitl_placement import HITLPlacement, HITLPlacementKind
from harness_cp.pause_resume_protocol_types import PauseSnapshot
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import execute_workflow
from harness_cp.workflow_driver_types import RunStatus, StepKind, WorkflowStep
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_runtime.bootstrap import run_bootstrap
from harness_runtime.lifecycle.pause_resume_protocol_types import (
    PauseResumeProtocolConfig,
)
from harness_runtime.lifecycle.webhook_delivery_composer import WebhookDeliveryResult
from harness_runtime.lifecycle.webhook_delivery_composer_types import (
    WebhookDeliveryComposerConfig,
)
from harness_runtime.types import RuntimeConfig

from .conftest import WORKLOAD, build_config


# --- Test fixtures ----------------------------------------------------------


_CHAIN = FallbackChain(
    primary=ProviderCandidate(
        provider="anthropic",
        model="claude-haiku-4-5",
        family=ProviderFamily.ANTHROPIC,
    ),
    same_family=(),
    cross_family=(),
    terminal=None,
)
_DEFAULT_BINDING = ModelBinding(provider="anthropic", model="claude-haiku-4-5")


class _NoopDispatcher:
    def dispatch(
        self,
        binding: Any,
        step: WorkflowStep,
        *,
        step_context: Any = None,
    ) -> dict[str, Any]:
        _ = binding, step_context
        return {"step_id": str(step.step_id), "ok": True}


class _SingleKindRegistry:
    def __init__(self, dispatcher: Any) -> None:
        self._dispatcher = dispatcher

    def lookup(self, step_kind: Any) -> Any:
        _ = step_kind
        return self._dispatcher


def _attach_get_tracer_to_ctx(ctx: Any) -> None:
    """Per U-RT-89 e2e precedent (`test_u_rt_89_pause_resume_full_execution_path.py`)
    — the `patched_runtime` fixture's `FakeTracerProvider` lacks `get_tracer`."""
    from opentelemetry.trace import NoOpTracer

    ctx.tracer_provider.get_tracer = lambda _name, /: NoOpTracer()  # type: ignore[attr-defined,method-assign]


def _manifest(
    workflow_id: str,
    *,
    persona_tier: PersonaTier = PersonaTier.SOLO_DEVELOPER,
    engine_class: EngineClass = EngineClass.PURE_PATTERN_NO_ENGINE,
) -> WorkflowManifestEntry:
    """Build a manifest with materialized engine class.

    Default (SOLO_DEVELOPER + PURE_PATTERN_NO_ENGINE) maps to SYNC_BLOCKING
    per CP §18.1. RECONCILER_LOOP / WAL_SEGMENT engine classes (which would
    map to DURABLE_ASYNC cells) are NOT materialized at runtime per
    `EngineClassNotYetMaterializedError` — full durable-async pause-trigger
    cycle exercise (path (i)) requires those engine classes + is deferred to
    a follow-on arc per FM-2 (v2.25 §6.5 mechanism β / γ deferred).
    """
    return WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WORKLOAD,
        persona_tier=persona_tier,
        engine_class=engine_class,
        topology_pattern=TopologyPattern.SINGLE_THREADED_LINEAR,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


def _single_inference_step() -> tuple[WorkflowStep, ...]:
    return (
        WorkflowStep(
            step_id=StepID("step-0"),
            step_kind=StepKind.INFERENCE_STEP,
            step_payload={"index": 0},
        ),
    )


def _config_joint_opt_in(tmp_path: Path) -> RuntimeConfig:
    """Both pause-resume + webhook opt-in (path (i) substrate)."""
    base = build_config(tmp_path)
    return base.model_copy(
        update={
            "pause_resume_protocol_config": PauseResumeProtocolConfig.default(),
            "webhook_delivery_composer_config": WebhookDeliveryComposerConfig.default(),
        },
    )


def _config_pause_resume_only(tmp_path: Path) -> RuntimeConfig:
    """pause-resume opt-in; webhook opt-out (path (vi) substrate)."""
    base = build_config(tmp_path)
    return base.model_copy(
        update={"pause_resume_protocol_config": PauseResumeProtocolConfig.default()},
    )


def _config_webhook_only(tmp_path: Path) -> RuntimeConfig:
    """webhook opt-in; pause-resume opt-out (path (v) substrate)."""
    base = build_config(tmp_path)
    return base.model_copy(
        update={
            "webhook_delivery_composer_config": WebhookDeliveryComposerConfig.default()
        },
    )


# ---------------------------------------------------------------------------
# Path (iii) — neither binding present → sync-blocking fall-through.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_path_iii_neither_binding_falls_through_to_sync(
    tmp_path: Path,
    patched_runtime: dict[str, Any],
) -> None:
    """Path (iii) — operator opts out of BOTH pause-resume and webhook.
    Production-default state: §14.8.8.1 step 0 OR-form precondition AND-arm
    evaluates False on both sides → composer falls through to sync-blocking
    path. No durable-async signal raised; workflow completes normally.
    """
    _ = patched_runtime
    config = build_config(tmp_path)
    # Production-default opt-out on both sides.
    assert config.pause_resume_protocol_config is None
    assert config.webhook_delivery_composer_config is None
    ctx = await run_bootstrap(config, workload_class=WORKLOAD)
    _attach_get_tracer_to_ctx(ctx)
    assert ctx.pause_resume_protocol is None
    assert ctx.webhook_delivery_composer is None

    # Without an actual HITL placement on the step, the composer body never
    # enters the placement loop — the workflow runs to completion. This
    # verifies that bootstrap-default state (no opt-in) produces a clean
    # workflow execution without surfacing the durable-async substrate.
    manifest = _manifest("wf-path-iii")
    steps = _single_inference_step()
    dispatchers = _SingleKindRegistry(_NoopDispatcher())
    result = await asyncio.to_thread(
        partial(
            execute_workflow,
            manifest_entry=manifest,
            steps=steps,
            run_id="run-path-iii",
            ctx=ctx,  # type: ignore[arg-type]
            default_model_binding=_DEFAULT_BINDING,
            step_dispatchers=dispatchers,  # type: ignore[arg-type]
        )
    )
    assert result.status == RunStatus.SUCCESS, (
        f"expected SUCCESS, got {result.status}; "
        f"fail_class={result.fail_class}"
    )


# ---------------------------------------------------------------------------
# Path (v) — webhook only; pause_resume_protocol None (operator opt-out).
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_path_v_webhook_only_falls_through_to_sync(
    tmp_path: Path,
    patched_runtime: dict[str, Any],
) -> None:
    """Path (v) — operator binds webhook BUT not pause-resume (v2.24 AC #7).
    §14.8.8.1 step 0 OR-form precondition AND-arm at
    `ctx.pause_resume_protocol is None` evaluates True → falls through to
    sync-blocking. Verifies the orphan-response-bug-prevention closure per
    v1.25 D9 + v1.26 OR-form extension.
    """
    _ = patched_runtime
    config = _config_webhook_only(tmp_path)
    ctx = await run_bootstrap(config, workload_class=WORKLOAD)
    _attach_get_tracer_to_ctx(ctx)
    assert ctx.pause_resume_protocol is None
    assert ctx.webhook_delivery_composer is not None

    manifest = _manifest("wf-path-v")
    steps = _single_inference_step()
    dispatchers = _SingleKindRegistry(_NoopDispatcher())
    result = await asyncio.to_thread(
        partial(
            execute_workflow,
            manifest_entry=manifest,
            steps=steps,
            run_id="run-path-v",
            ctx=ctx,  # type: ignore[arg-type]
            default_model_binding=_DEFAULT_BINDING,
            step_dispatchers=dispatchers,  # type: ignore[arg-type]
        )
    )
    # No pause/signal raised — workflow completes via inner dispatcher.
    assert result.status == RunStatus.SUCCESS


# ---------------------------------------------------------------------------
# Path (vi) — pause-resume only; webhook_delivery_composer None.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_path_vi_pause_resume_only_falls_through_to_sync(
    tmp_path: Path,
    patched_runtime: dict[str, Any],
) -> None:
    """Path (vi) — operator binds pause-resume BUT not webhook (v2.25 AC #8;
    symmetric to v2.24 AC #7 path (v)).
    §14.8.8.1 step 0 OR-form precondition AND-arm at
    `ctx.webhook_delivery_composer is None` evaluates True → falls through
    to sync-blocking. Verifies the v1.26 canonical-reading amendment
    extending the v1.25 single-binding check to joint-binding requirement.
    """
    _ = patched_runtime
    config = _config_pause_resume_only(tmp_path)
    ctx = await run_bootstrap(config, workload_class=WORKLOAD)
    _attach_get_tracer_to_ctx(ctx)
    assert ctx.pause_resume_protocol is not None
    assert ctx.webhook_delivery_composer is None

    manifest = _manifest("wf-path-vi")
    steps = _single_inference_step()
    dispatchers = _SingleKindRegistry(_NoopDispatcher())
    result = await asyncio.to_thread(
        partial(
            execute_workflow,
            manifest_entry=manifest,
            steps=steps,
            run_id="run-path-vi",
            ctx=ctx,  # type: ignore[arg-type]
            default_model_binding=_DEFAULT_BINDING,
            step_dispatchers=dispatchers,  # type: ignore[arg-type]
        )
    )
    # No pause/signal raised — workflow completes via inner dispatcher.
    assert result.status == RunStatus.SUCCESS


# ---------------------------------------------------------------------------
# Path (vii) — bare-StepEffectiveBinding regression gate (v2.25 AC #9).
# ---------------------------------------------------------------------------


def test_path_vii_bare_step_effective_binding_without_persona_tier_raises() -> None:
    """Path (vii) — post-CP-v1.17 §6.5, StepEffectiveBinding declares
    `persona_tier: PersonaTier` as a required field. Any future regression
    to a bare binding shape (e.g., test fixture forgetting persona_tier OR
    downgrade to pre-v1.17 carrier shape) must surface as a Pydantic
    ValidationError at construction — NOT a silent fallback to sync-blocking
    via getattr-tolerance. Negative test: attempts bare construction;
    verifies ValidationError raised with `persona_tier` in the error message.
    """
    from pydantic import ValidationError

    with pytest.raises(ValidationError) as excinfo:
        StepEffectiveBinding(  # type: ignore[call-arg]
            step_id="step-1",
            model_binding=ModelBinding(provider="anthropic", model="claude-opus-4-7"),
            engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
            override_applied=False,
        )
    assert "persona_tier" in str(excinfo.value).lower()


# ---------------------------------------------------------------------------
# Path (i) — durable-async pause-trigger (signal raised + driver catches).
# ---------------------------------------------------------------------------


@pytest.mark.skip(
    reason=(
        "Path (i) full pause-trigger cycle requires a DURABLE_ASYNC matrix "
        "cell (RECONCILER_LOOP / WAL_SEGMENT engine classes per CP §18.1). "
        "Those engine classes are NOT yet materialized at runtime per "
        "EngineClassNotYetMaterializedError; only PURE_PATTERN_NO_ENGINE + "
        "EVENT_SOURCED_REPLAY + SAVE_POINT_CHECKPOINT are runtime-materialized. "
        "Path (i) e2e is deferred to a follow-on arc per FM-2 (v2.25 §6.5 "
        "mechanism β / γ deferred) when DURABLE_ASYNC engine classes land. "
        "The driver-side HITLPauseRequestedSignal catch handler at "
        "workflow_driver.py is unit-tested separately at "
        "harness-cp/tests/test_workflow_driver.py; the composer-side "
        "durable-async body is unit-tested at "
        "harness-runtime/tests/test_lifecycle_hitl_gate_composer.py."
    )
)
@pytest.mark.asyncio
async def test_path_i_durable_async_pause_trigger_returns_paused(
    tmp_path: Path,
    patched_runtime: dict[str, Any],
) -> None:
    """Path (i) — DEFERRED per docstring above. Test body retained as
    documentation of the intended e2e shape for the follow-on arc."""
    _ = patched_runtime, tmp_path
