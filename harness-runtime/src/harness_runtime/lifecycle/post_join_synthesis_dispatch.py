"""Runtime `POST_JOIN_SYNTHESIS` step dispatcher (R-FS-1 arc B-POSTJOIN-LLM-SYNTHESIS).

Per CP spec v1.54 §5.2/§25.2/§3 + the paired runtime contract: the opt-in
terminal `StepKind.POST_JOIN_SYNTHESIS` step's body is an **LLM-composed
synthesis** over a concurrent fan-out's branch-index-ordered sibling outputs.
The CP driver carves the terminal synthesis step out of the branch set, drains
the fan-out barrier, then dispatches this step SYNC post-barrier supplying the
siblings on `StepExecutionContext.sibling_outputs` (CP spec v1.54 §3); this
dispatcher composes them into the synthesis step's LLM input and dispatches
through the inner LLM dispatcher (the same C-RT-16 `RetryBreakerFallbackDispatcher`
chain `INFERENCE_STEP` uses, wrapped in the stage-5 `SyncDispatcherFacade`).

**Read-only / effect-free** (CP spec v1.54 change-note): a pure read-of-siblings
+ compose; no effect-fence-carrying tool dispatch. The non-determinism of the LLM
compose is the §25.12 Point-2 (aggregator-purity) sacrifice, disclosed at the CP
driver's synthesis step ledger entry + trace event — NOT here.

**Minimal dispatch** (CP spec v1.54 "out of scope: operator-supplied prompt
templating beyond the minimal synthesis dispatch"): the siblings are appended as
one branch-index-ordered context `user` message AFTER the synthesis step's own
declared `payload.messages` (the operator's synthesis instruction). Reducer DSLs /
configurable templating are the registered follow-on, not this arc.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.workflow_driver import StepDispatcher
from harness_cp.workflow_driver_types import WorkflowStep

__all__ = [
    "POST_JOIN_SYNTHESIS_SIBLINGS_PREFIX",
    "PostJoinSynthesisStepDispatcher",
]

#: Prefix labelling the injected branch-index-ordered sibling-output context
#: message, so a model (and a test) can distinguish the synthesis material from
#: the step's own declared synthesis-instruction messages (mirrors the B-INTERSTEP
#: `_UPSTREAM_CONTEXT_PREFIX` convention).
POST_JOIN_SYNTHESIS_SIBLINGS_PREFIX = "[post-join siblings]\n"


def _compose_synthesis_payload(
    payload: Mapping[str, Any],
    siblings: Sequence[tuple[int, Mapping[str, Any]]],
) -> dict[str, Any]:
    """Append the branch-index-ordered sibling outputs as one context ``user``
    message to the synthesis step's payload ``messages``.

    The siblings are the material the model composes; they are appended AFTER the
    step's declared messages (the operator's synthesis instruction). Deterministic
    serialization (`sort_keys`, `default=str`) keeps the injected content stable;
    the dispatcher does NOT introspect the opaque step body otherwise (the
    `workflow_driver` §25.3.3.4 step-body-opaque discipline)."""
    composed = dict(payload)
    # Out-of-family Codex [P2]: the LLM translators do `kwargs.update(payload.params)`,
    # so a `params["messages"]` escape-hatch would OVERWRITE the appended sibling
    # context — the model would receive NO branch outputs while the run still reports
    # a synthesized final state. The synthesis OWNS its messages (it composes the
    # siblings); reject the conflicting escape-hatch fail-closed (the driver's
    # failure-mapping converts this to a FAILED RunResult).
    _params = composed.get("params")
    if isinstance(_params, Mapping) and "messages" in _params:
        raise ValueError(
            "post-join-synthesis payload may not set params['messages']: the provider "
            "escape-hatch overwrites the appended sibling-context message (the model "
            "would receive no branch outputs). Put the synthesis instruction in "
            "payload['messages'] instead."
        )
    messages: list[Any] = list(composed.get("messages", ()))
    sibling_message: dict[str, Any] = {
        "role": "user",
        "content": POST_JOIN_SYNTHESIS_SIBLINGS_PREFIX
        + json.dumps(
            [{"branch_index": bi, "output": dict(out)} for bi, out in siblings],
            sort_keys=True,
            default=str,
        ),
    }
    composed["messages"] = [*messages, sibling_message]
    return composed


class PostJoinSynthesisStepDispatcher:
    """`StepDispatcher` for `StepKind.POST_JOIN_SYNTHESIS` (CP spec v1.54).

    Wraps the inner LLM dispatcher (the stage-5 `inference_step_dispatcher`
    `SyncDispatcherFacade` — already sync), so this dispatcher is itself sync and
    needs no further facade. On `dispatch`: read the branch-index-ordered siblings
    from `step_context.sibling_outputs`, compose them into the synthesis step's LLM
    input, and dispatch the composed step through the inner LLM dispatcher.
    Satisfies the `@runtime_checkable` `StepDispatcher` Protocol (sync
    `dispatch(binding, step, *, step_context)`)."""

    def __init__(self, *, inner: StepDispatcher) -> None:
        self._inner = inner

    def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: Any = None,
    ) -> Mapping[str, Any]:
        siblings: Sequence[tuple[int, Mapping[str, Any]]] = (
            getattr(step_context, "sibling_outputs", None) or ()
        )
        composed_payload = _compose_synthesis_payload(step.step_payload, siblings)
        synthesis_step = step.model_copy(update={"step_payload": composed_payload})
        return self._inner.dispatch(binding, synthesis_step, step_context=step_context)
