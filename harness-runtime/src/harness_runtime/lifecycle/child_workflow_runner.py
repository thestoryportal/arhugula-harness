"""In-process recursive child sub-workflow invocation primitive (U-RT-59 AC #7).

Per `Spec_Harness_Runtime_v1.md` v1.6 §14.7.4 (C-RT-17 contract). The
"child workflow runner" callable is injected at `RuntimeSubAgentDispatcher`
construction; the composer invokes it at §14.7.2 step 6 to re-enter
`execute_workflow()` for the child sub-workflow body.

**v1.6 MVP composition (§14.7.4).**

- The child shares the parent's `HarnessContext` for substrate access (state
  ledger, tracer provider, audit ledger writer, retry/breaker registry,
  providers, sandbox tier dispatcher). Full child-context isolation is a
  v1.7+ scope question (CP-AL-1-adjacent boundary).
- The child's spans nest inside the current `subagent.span` via OTel context
  propagation (the runner is invoked from within the composer's
  `start_as_current_span("subagent.span")` block, so the child's
  `workflow.start` becomes a span-context child of `subagent.span`).
- The child's audit-ledger entries write to the same ledger via the same
  `ctx.audit_writer` (no separate ledger primitive at v1.6).
- The child's `RunResult` is returned verbatim to the composer.

**Sync surface (operator-ratified 2026-05-20).** Spec §14.7.4 declares the
`ChildWorkflowRunner` Protocol with `async def __call__`; operator ratified
sync end-to-end per the Stage 1 Protocol freeze at `workflow_driver.py:175`
(`StepDispatcher.dispatch` is sync; `execute_workflow` is sync). Rolled into
the U-RT-59 Class 3 spec-prose-drift note at landing. Recursive sync re-entry
is sufficient at v1.6 MVP because the spec-pinned scope is "single-sub-agent
within linear parent" — no fan-out concurrency at the composer level.

**`default_model_binding` additive extension.** Spec §14.7.4 lists 5 kwargs
on the runner Protocol (`workflow_id`, `manifest_entry`, `steps`,
`handoff_context`, `descent`). `execute_workflow` requires a
`default_model_binding` for the child's per-step binding resolution per
C-CP-06 §6.2; the composer forwards its parent `binding.model_binding`
(per C-CP-13 §13.3 brief-authoring inheritance MVP reading). Additive vs
spec; rolled into the same Class 3 note.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Any, Protocol, cast, runtime_checkable

from harness_cp.cp_shared_types import ModelBinding
from harness_cp.handoff_context import HandoffContext
from harness_cp.sub_agent_gate_level_descent import SubAgentGateLevelDescent
from harness_cp.workflow_driver import DriverContext as _CpDriverContext
from harness_cp.workflow_driver import execute_workflow
from harness_cp.workflow_driver_types import RunResult, WorkflowStep
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry

from harness_runtime.types import HarnessContext

__all__ = [
    "ChildWorkflowRunner",
    "compose_child_workflow_runner",
]


@runtime_checkable
class ChildWorkflowRunner(Protocol):
    """In-process recursive sub-workflow invocation surface (§14.7.4).

    Constructed at bootstrap stage 5 via `compose_child_workflow_runner(ctx)`;
    injected into `RuntimeSubAgentDispatcher.__init__`. The composer invokes
    it at §14.7.2 step 6 to run the child sub-workflow.

    Per `Spec_Harness_Runtime_v1.md` v1.6 §14.7.4 with two sync-vs-spec
    adjustments documented in the module docstring: (1) sync `__call__`
    instead of `async def __call__`; (2) additive `default_model_binding`
    kwarg.
    """

    def __call__(
        self,
        *,
        workflow_id: str,
        manifest_entry: WorkflowManifestEntry,
        steps: Sequence[WorkflowStep],
        handoff_context: HandoffContext,
        descent: SubAgentGateLevelDescent,
        default_model_binding: ModelBinding,
    ) -> RunResult:
        """Run the child sub-workflow and return its terminal `RunResult`."""
        ...


def compose_child_workflow_runner(ctx: HarnessContext) -> ChildWorkflowRunner:
    """Build a `ChildWorkflowRunner` closing over the parent `HarnessContext`.

    Per `Spec_Harness_Runtime_v1.md` v1.6 §14.7.4 "Composer module residence":
    bootstrap stage 5 calls this factory + injects the result into
    `RuntimeSubAgentDispatcher` construction.

    The returned callable re-enters `execute_workflow()` (the same C-CP-25
    §25.3 driver loop the top-level workflow uses per C-RT-08). Child shares
    parent `HarnessContext` per v1.6 MVP — substrate access (state ledger,
    audit writer, tracer provider, retry/breaker registry, providers,
    sandbox tier dispatcher) flows through `ctx` unchanged.

    The child's `step_dispatchers` is the parent's `ctx.step_dispatchers`
    registry — recursive `SUB_AGENT_DISPATCH` steps in the child route
    through the same composer (unbounded stack depth at v1.6 MVP; bounded
    by the operator-authored workflow shape).

    Parameters
    ----------
    ctx
        The parent `HarnessContext`. The runner closes over this context;
        `ctx.step_dispatchers` must be populated (which it is post stage 5
        per the bootstrap orchestrator's stage ordering).
    """

    def _runner(
        *,
        workflow_id: str,
        manifest_entry: WorkflowManifestEntry,
        steps: Sequence[WorkflowStep],
        handoff_context: HandoffContext,
        descent: SubAgentGateLevelDescent,
        default_model_binding: ModelBinding,
    ) -> RunResult:
        child_run_id = uuid.uuid4().hex
        # The CP driver consumes `ctx` via its structural `DriverContext`
        # Protocol (subset of HarnessContext). Cast for the type layer; the
        # runtime objects satisfy both Protocols — same pattern as
        # `harness_runtime.api.run` per the existing api.py:386 invocation.
        return execute_workflow(
            manifest_entry,
            steps,
            child_run_id,
            cast(_CpDriverContext, ctx),
            default_model_binding=default_model_binding,
            step_dispatchers=cast(Any, ctx.step_dispatchers),
        )

    return _runner
