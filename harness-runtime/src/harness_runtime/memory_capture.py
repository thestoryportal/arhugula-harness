"""Automatic episodic memory capture API - U-MEM-07.

This module is runtime-local glue over the U-MEM-06 canonical store. It turns
runtime observations into C-MEM-04 episodic records and C-MEM-08 durable
``capture`` operation entries. Retrieval, injection, and semantic promotion are
owned by later memory units.
"""

from __future__ import annotations

import hashlib
import unicodedata
from collections.abc import Mapping, Sequence
from datetime import datetime
from enum import StrEnum
from typing import ClassVar, Protocol, Self

from harness_is.memory_observability import (
    MemoryTelemetryFailureClass,
    MemoryTelemetryOperationName,
    classify_memory_failure,
    memory_telemetry_span,
    set_memory_telemetry_attributes,
)
from harness_is.memory_operation_ledger import (
    MemoryOperationEngineClass,
    MemoryOperationEntry,
    MemoryOperationIdempotencyConflictError,
    MemoryOperationKind,
    MemoryOperationPayload,
    MemoryOperationProjection,
    MemoryOperationWriteResult,
)
from harness_is.memory_record_envelope import (
    CapturedCrossFamily,
    MemoryID,
    MemoryRecordEnvelope,
    MemoryRecordKind,
    MemoryScope,
    MemoryTier,
    MemoryVisibility,
    SourceRef,
    SourceRefType,
    compute_memory_content_hash,
    derive_memory_id,
)
from harness_is.memory_store import MemoryStoreRecord, MemoryStoreWriteResult
from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier
from pydantic import BaseModel, ConfigDict, model_validator

from harness_runtime.memory_scope_family import (
    canonical_scope_family,
    resolve_scope_family,
    scope_family_out_of_domain_message,
)

_REDACTED_SUMMARY = "[redacted]"
_SCHEMA_VERSION = "episodic-capture/v1"

RUN_START_EVENT_KIND = "run_start"
"""Event kind of the run-start capture, shared with its durable-row probes.

`capture_run_start` writes this same value as the record's own
`content["event_type"]`, so it is also what `stored_capture_event_type` returns
for a run-start record - one spelling for both the ledger key and the stored
discriminator.
"""


class _ContentOrigin(StrEnum):
    """Whether a capture's stored content derives from a completed dispatch.

    The C-MEM-03 v1.2 content-ORIGIN condition, as a value. A determination
    (`true` / `false`) is recorded ONLY where the stored content derives from
    the output of a completed provider dispatch; everything else is `unknown`.

    This is deliberately NOT a finished tri-state: the family comparison it
    gates needs the record's RESOLVED scope, which does not exist at
    `_capture`. `_capture` decides origin, `_record` decides the value.
    """

    DISPATCH_DERIVED = "dispatch_derived"
    UNDETERMINED = "undetermined"


#: The C-MEM-03 content-origin CONDITION, realized over `event_kind`.
#:
#: The rule is stated over content origin - "did the capturing caller hold a
#: completed dispatch result on THIS invocation" - not over method names and
#: emphatically not over `summary_source` (a harness rule summarizing a real
#: provider response is *harness-summarized* and *dispatch-derived*, so a
#: `summary_source` test would mark every production turn capture `unknown`).
#: `event_kind` is the one signal available centrally, and it identifies the
#: calling method; a method-level entry is a SOUND realization of the rule only
#: where every production invocation of that method shares one origin, which is
#: why each entry below records the invocation set it was grounded against.
#:
#: * `turn_completion` - `LocalAutomaticMemoryRuntime.capture_turn_completion`
#:   (`automatic_memory.py:240-284`) computes `response_summary` from the actual
#:   provider `response` (`:269`) and passes the dispatched `provider` (`:276`).
#:   Dispatch-derived on every production invocation.
#: * `tool_event` - sole production caller `StandardMemoryToolExecutor._write_note`
#:   (`memory_tool_executor.py:339-376`) stores the note the model produced on
#:   the dispatch whose `context.provider` it passes. Dispatch-derived.
#: * `run_start` - written by `compose_for_dispatch` BEFORE the dispatch it
#:   composes for (`automatic_memory.py:232` precedes the return at `:238`), so
#:   the provider in hand is a SELECTION, not a producer.
#: * `run_close` - run-lifecycle metadata (`run_id` / `workflow_id` /
#:   `thread_id` / `engine_class` / `cli_profile` / `provider_route` /
#:   `started_at` / `closed_at` / `close_status`, no summary field of any kind),
#:   which derives from no dispatch output whenever it is written.
#: * `provider_route` - harness-composed route text; derives from a routing
#:   decision, not from dispatch output.
#: * `failure_observation` / `compaction` - origin varies PER INVOCATION (a
#:   failure summary may describe output a dispatch produced, or a dispatch that
#:   produced none), so the method name cannot decide it. Neither has a
#:   production caller at HEAD; both record `unknown` for the invocations they
#:   cannot distinguish, per C-MEM-03's own treatment of that case.
#:
#: An `event_kind` absent from this mapping resolves to `UNDETERMINED`, so a
#: writer added later inherits the conservative disposition rather than a
#: fabricated determination.
_CONTENT_ORIGIN_BY_EVENT_KIND: Mapping[str, _ContentOrigin] = {
    "turn_completion": _ContentOrigin.DISPATCH_DERIVED,
    "tool_event": _ContentOrigin.DISPATCH_DERIVED,
    RUN_START_EVENT_KIND: _ContentOrigin.UNDETERMINED,
    "run_close": _ContentOrigin.UNDETERMINED,
    "provider_route": _ContentOrigin.UNDETERMINED,
    "failure_observation": _ContentOrigin.UNDETERMINED,
    "compaction": _ContentOrigin.UNDETERMINED,
}


def capture_operation_action_id(event_kind: str, memory_id: MemoryID) -> Identifier:
    """Return the C-MEM-08 `action_id` a capture of `memory_id` writes.

    Exported because it is the ONLY key that identifies one capture event in
    the ledger: run-start and run-close share a single EPISODIC_RUN
    `memory_id`, so `memory_refs` cannot tell them apart. A caller asking
    whether a specific capture completed must ask by this id, and must build
    it here rather than re-spelling the format.
    """
    return Identifier(f"capture:{event_kind}:{memory_id}")


_RESERVED_REPAIR_ACTOR_PREFIX = "memory-capture-repair:"
"""The `actor_id` namespace RESERVED for torn-capture repair rows.

Codex R9. `Actor.actor_id` is an unrestricted `str` supplied by whoever binds
an `EpisodicMemoryCapture`, so the R8 occupant test - which discriminates a
synthetic repair row from an ordinary dispatch row by actor equality - was only
as sound as the assumption that no ordinary capture can spell that identity.
Nothing enforced the assumption: a caller binding this prefix would have made a
later DIVERGENT run-start replay misread its own predecessor's row as a repair
and return `CAPTURED` over a durable record/ledger disagreement.

This prefix is therefore refused at the ONE place an ordinary capture's actor
enters (`EpisodicMemoryCapture.__init__`), which makes the R8 discriminator
unforgeable rather than merely conventional. `capture_repair_actor` below is
the sole legitimate producer of an id in this namespace, and it composes it
from this same constant so the reservation and the identity cannot drift apart.
"""


def capture_repair_actor(run_id: str) -> Actor:
    """Return the actor a torn-capture REPAIR row records for `run_id`.

    A repair row is not a dispatch row. The dispatch that tore is gone, and the
    worker that happens to notice the tear later is not its author - binding
    the repair to the NOTICING worker's actor would both misattribute the
    capture and make the payload worker-dependent, which two concurrent
    repairers cannot agree on (they would collide under one idempotency key
    with unequal payloads). The repair is therefore attributed to the harness
    itself, keyed by the run it repairs, so every worker composes the same
    actor for the same run.

    Exported for the same reason `capture_operation_action_id` is: it is the
    only spelling of this identity, and a caller asserting against a repair row
    must build it here rather than re-spell the format.

    The `_RESERVED_REPAIR_ACTOR_PREFIX` namespace is closed to ordinary capture
    (see there), so this function is the only producer of the identity - which
    is what lets `_conflicting_row_is_a_repair` read actor equality as proof.
    """
    return Actor(
        actor_class=ActorClass.AGENT,
        actor_id=f"{_RESERVED_REPAIR_ACTOR_PREFIX}{run_id}",
    )


class SummarySource(StrEnum):
    """Provenance classes for stored episodic summaries."""

    HARNESS_RULE = "harness_rule"
    MODEL_GENERATED = "model_generated"
    OPERATOR = "operator"
    IMPORTED = "imported"


class MemoryCaptureMode(StrEnum):
    """How much source content an automatic capture may persist."""

    FULL = "full"
    SUMMARIZED = "summarized"
    REDACTED = "redacted"


class MemoryCaptureStatus(StrEnum):
    """Observable outcome of one capture attempt."""

    CAPTURED = "captured"
    FAILED = "failed"


class SummaryProvenance(BaseModel):
    """Source metadata stored alongside a summary."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source: SummarySource
    model: str | None = None

    @model_validator(mode="after")
    def _model_generated_names_model(self) -> Self:
        if self.source is SummarySource.MODEL_GENERATED and not self.model:
            raise ValueError("model-generated summaries require a model")
        return self


class MemoryCaptureResult(BaseModel):
    """Result returned by all capture API methods."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: MemoryCaptureStatus
    event_kind: str
    record_kind: MemoryRecordKind | None = None
    memory_id: MemoryID | None = None
    operation_action_id: Identifier | None = None
    operation_result: MemoryOperationWriteResult | None = None
    failure_reason: str | None = None


class MemoryCaptureStore(Protocol):
    """Store surface consumed by ``EpisodicMemoryCapture``."""

    def write_record(self, record: MemoryStoreRecord) -> MemoryStoreWriteResult: ...

    def append_memory_operation(
        self,
        payload: MemoryOperationPayload,
    ) -> MemoryOperationWriteResult: ...

    def read_memory_operations(self) -> list[MemoryOperationEntry]:
        """Read the durable C-MEM-08 ledger.

        Codex R8: capture is a WRITER, and this is the one read it needs - the
        run-start conflict path has to identify WHO already occupies the slot
        before it may read that conflict as completion (`_capture`). It is
        reached ONLY from that path, which is the rare one; every ordinary
        capture still writes without reading the ledger at all.
        """
        ...


class MemoryCaptureScopeValueDomainError(ValueError):
    """Raised when a capture scope's `provider_family` is out of the value domain.

    U-MEM-26 / C-MEM-03 v1.1. Reachable from BOTH branches of
    `_scope_for_record` - the residual construction, where the scope is still
    derived from a per-dispatch provider key, and a scope SUPPLIED by a caller,
    which is no more trusted (Codex R2). The composed production path does not
    raise it in practice: that scope's `provider_family` is by construction a
    `ProviderFamily` value derived once from the chain primary.

    It is a refusal, not a substrate fault, so it declares `policy_denial`
    rather than inheriting the message-heuristic residual - the same
    by-construction discipline `B-88` applied to the tool-executor family.
    """

    memory_failure_class: ClassVar[MemoryTelemetryFailureClass] = (
        MemoryTelemetryFailureClass.POLICY_DENIAL
    )


class MemoryCaptureReservedActorError(ValueError):
    """Raised when a caller binds an actor id inside the reserved REPAIR namespace.

    Codex R9. A sibling refusal to `MemoryCaptureScopeValueDomainError` above
    and classed the same way: it is a caller CONTRACT violation, not a
    substrate fault, so it declares `policy_denial` at its own definition site
    (B-88) rather than inheriting the message-heuristic residual. The
    declaration is load-bearing, not decorative - `StandardMemoryToolExecutor`
    binds a caller-supplied `context.actor` inside its `execute` try, whose
    handler classes the exception by TYPE through `classify_memory_failure`.

    It is raised from `__init__` rather than from a capture method because that
    is where the actor enters and because refusing at construction means the
    refused binding can never write anything at all.
    """

    memory_failure_class: ClassVar[MemoryTelemetryFailureClass] = (
        MemoryTelemetryFailureClass.POLICY_DENIAL
    )


class EpisodicMemoryCapture:
    """Automatic capture API for runtime episodic events."""

    def __init__(
        self,
        *,
        store: MemoryCaptureStore,
        actor: Actor,
        project: str | None = None,
        visibility: MemoryVisibility = MemoryVisibility.PROJECT,
        capture_mode: MemoryCaptureMode = MemoryCaptureMode.SUMMARIZED,
        tracer_provider: object | None = None,
        record_scope: MemoryScope | None = None,
    ) -> None:
        """Bind the capture collaborators.

        `record_scope` is the `B-89` writer-side repair: the run's COMPOSED
        record scope, used for every record this instance writes. The composed
        scope is the single authority for what a run captures, so what a run
        captures and what a run can retrieve share one partition by
        construction (C-MEM-03 v1.1, "The paired writer-side obligation"). It
        is still passed through the write boundary's value domain rather than
        stored verbatim - a supplied scope is not exempt (`_scope_for_record`).

        It defaults to `None` so the residual construction below stays
        available to callers that have no composed scope; that path is bound by
        the value domain instead (`_scope_for_record`). The `provider` argument
        the capture methods take is UNAFFECTED either way - it still feeds the
        C-MEM-08 operation payload and the C-MEM-19 span as the raw per-dispatch
        key it is. Only the RECORD scope stops deriving from it.

        `actor` is the ONLY way an ordinary capture's actor is bound - no
        `capture_*` method takes a per-call actor, and `_operation_payload` is
        reached with exactly two actors: this one and, from
        `repair_capture_operation` alone, `capture_repair_actor(run_id)`. So
        refusing the reserved repair namespace here closes it for every
        ordinary row, which is what makes the R8 occupant test unforgeable
        (`_RESERVED_REPAIR_ACTOR_PREFIX`).
        """
        if actor.actor_id.startswith(_RESERVED_REPAIR_ACTOR_PREFIX):
            raise MemoryCaptureReservedActorError(
                f"actor_id {actor.actor_id!r} is inside the "
                f"{_RESERVED_REPAIR_ACTOR_PREFIX!r} namespace, which is reserved for "
                "torn-capture repair rows and may not be bound by an ordinary capture"
            )
        self._store = store
        self._actor = actor
        self._project = project
        self._visibility = visibility
        self._capture_mode = capture_mode
        self._tracer_provider = tracer_provider
        self._record_scope = record_scope

    def capture_run_start(
        self,
        *,
        run_id: str,
        workflow_id: str | None,
        thread_id: str | None,
        provider_route: Sequence[str],
        timestamp: datetime,
        provider: str | None,
        model: str | None,
        cli_profile: str | None,
        engine_class: MemoryOperationEngineClass | None,
        policy_ref: str | None,
        procedural_snapshot_ref: str | None,
    ) -> MemoryCaptureResult:
        content: dict[str, object] = {
            "event_type": "run_start",
            "run_id": run_id,
            "workflow_id": workflow_id,
            "thread_id": thread_id,
            "engine_class": _engine_class_value(engine_class),
            "cli_profile": cli_profile,
            "provider_route": _string_list(provider_route),
            "started_at": timestamp,
            "closed_at": None,
            "close_status": "open",
        }
        return self._capture(
            event_kind=RUN_START_EVENT_KIND,
            record_kind=MemoryRecordKind.EPISODIC_RUN,
            content=content,
            timestamp=timestamp,
            source_ref=SourceRef(ref_type=SourceRefType.RUN, ref=run_id),
            run_id=run_id,
            step_id=None,
            provider=provider,
            model=model,
            cli_profile=cli_profile,
            engine_class=engine_class,
            policy_ref=policy_ref,
            procedural_snapshot_ref=procedural_snapshot_ref,
        )

    def capture_run_close(
        self,
        *,
        run_id: str,
        workflow_id: str | None,
        thread_id: str | None,
        provider_route: Sequence[str],
        close_status: str,
        started_at: datetime | None,
        timestamp: datetime,
        provider: str | None,
        model: str | None,
        cli_profile: str | None,
        engine_class: MemoryOperationEngineClass | None,
        policy_ref: str | None,
        procedural_snapshot_ref: str | None,
    ) -> MemoryCaptureResult:
        content: dict[str, object] = {
            "event_type": "run_close",
            "run_id": run_id,
            "workflow_id": workflow_id,
            "thread_id": thread_id,
            "engine_class": _engine_class_value(engine_class),
            "cli_profile": cli_profile,
            "provider_route": _string_list(provider_route),
            "started_at": started_at,
            "closed_at": timestamp,
            "close_status": close_status,
        }
        return self._capture(
            event_kind="run_close",
            record_kind=MemoryRecordKind.EPISODIC_RUN,
            content=content,
            timestamp=timestamp,
            source_ref=SourceRef(ref_type=SourceRefType.RUN, ref=run_id),
            run_id=run_id,
            step_id=None,
            provider=provider,
            model=model,
            cli_profile=cli_profile,
            engine_class=engine_class,
            policy_ref=policy_ref,
            procedural_snapshot_ref=procedural_snapshot_ref,
        )

    def capture_turn_completion(
        self,
        *,
        run_id: str,
        turn_id: str,
        step_id: str,
        prompt_summary: str,
        response_summary: str,
        summary: SummaryProvenance,
        tool_event_refs: Sequence[str],
        failure_observations: Sequence[str],
        promotion_candidates: Sequence[str],
        token_usage: Mapping[str, int] | None,
        timestamp: datetime,
        provider: str | None,
        model: str | None,
        cli_profile: str | None,
        engine_class: MemoryOperationEngineClass | None,
        policy_ref: str | None,
        procedural_snapshot_ref: str | None,
        capture_mode: MemoryCaptureMode | None = None,
    ) -> MemoryCaptureResult:
        mode = capture_mode or self._capture_mode
        captured_prompt = _captured_text(prompt_summary, mode)
        captured_response = _captured_text(response_summary, mode)
        content: dict[str, object] = {
            "event_type": "turn_completion",
            "run_id": run_id,
            "turn_id": turn_id,
            "step_id": step_id,
            "prompt_summary": captured_prompt,
            "response_summary": captured_response,
            "summary_source": summary.source.value,
            "summary_model": summary.model,
            "summary_hash": _summary_hash(captured_prompt, captured_response),
            "capture_mode": mode.value,
            "tool_event_refs": _string_list(tool_event_refs),
            "failure_observations": _string_list(failure_observations),
            "promotion_candidates": _string_list(promotion_candidates),
            "token_usage": _token_usage(token_usage),
        }
        return self._capture(
            event_kind="turn_completion",
            record_kind=MemoryRecordKind.EPISODIC_TURN,
            content=content,
            timestamp=timestamp,
            source_ref=SourceRef(ref_type=SourceRefType.TURN, ref=turn_id),
            run_id=run_id,
            step_id=step_id,
            provider=provider,
            model=model,
            cli_profile=cli_profile,
            engine_class=engine_class,
            policy_ref=policy_ref,
            procedural_snapshot_ref=procedural_snapshot_ref,
        )

    def capture_tool_event(
        self,
        *,
        run_id: str,
        tool_event_id: str,
        tool_name: str,
        summary_text: str,
        summary: SummaryProvenance,
        step_id: str | None,
        timestamp: datetime,
        provider: str | None,
        model: str | None,
        cli_profile: str | None,
        engine_class: MemoryOperationEngineClass | None,
        policy_ref: str | None,
        procedural_snapshot_ref: str | None,
        capture_mode: MemoryCaptureMode | None = None,
    ) -> MemoryCaptureResult:
        mode = capture_mode or self._capture_mode
        captured_summary = _captured_text(summary_text, mode)
        content: dict[str, object] = {
            "event_type": "tool_event",
            "run_id": run_id,
            "tool_event_id": tool_event_id,
            "step_id": step_id,
            "tool_name": tool_name,
            "summary": captured_summary,
            "summary_source": summary.source.value,
            "summary_model": summary.model,
            "summary_hash": _summary_hash(captured_summary),
            "capture_mode": mode.value,
        }
        return self._capture(
            event_kind="tool_event",
            record_kind=MemoryRecordKind.TOOL_EVENT,
            content=content,
            timestamp=timestamp,
            source_ref=SourceRef(ref_type=SourceRefType.TOOL_EVENT, ref=tool_event_id),
            run_id=run_id,
            step_id=step_id,
            provider=provider,
            model=model,
            cli_profile=cli_profile,
            engine_class=engine_class,
            policy_ref=policy_ref,
            procedural_snapshot_ref=procedural_snapshot_ref,
        )

    def capture_provider_route(
        self,
        *,
        run_id: str,
        route_id: str,
        provider_route: Sequence[str],
        step_id: str | None,
        timestamp: datetime,
        provider: str | None,
        model: str | None,
        cli_profile: str | None,
        engine_class: MemoryOperationEngineClass | None,
        policy_ref: str | None,
        procedural_snapshot_ref: str | None,
    ) -> MemoryCaptureResult:
        route = _string_list(provider_route)
        summary_text = "provider route: " + " -> ".join(route)
        content: dict[str, object] = {
            "event_type": "provider_route",
            "run_id": run_id,
            "tool_event_id": f"provider-route:{route_id}",
            "route_id": route_id,
            "step_id": step_id,
            "tool_name": "provider_route",
            "provider_route": route,
            "summary": summary_text,
            "summary_source": SummarySource.HARNESS_RULE.value,
            "summary_model": None,
            "summary_hash": _summary_hash(summary_text),
            "capture_mode": MemoryCaptureMode.SUMMARIZED.value,
        }
        return self._capture(
            event_kind="provider_route",
            record_kind=MemoryRecordKind.TOOL_EVENT,
            content=content,
            timestamp=timestamp,
            source_ref=SourceRef(ref_type=SourceRefType.RUN, ref=run_id),
            run_id=run_id,
            step_id=step_id,
            provider=provider,
            model=model,
            cli_profile=cli_profile,
            engine_class=engine_class,
            policy_ref=policy_ref,
            procedural_snapshot_ref=procedural_snapshot_ref,
        )

    def capture_failure_observation(
        self,
        *,
        run_id: str,
        turn_id: str,
        step_id: str,
        observation: str,
        summary: SummaryProvenance,
        timestamp: datetime,
        provider: str | None,
        model: str | None,
        cli_profile: str | None,
        engine_class: MemoryOperationEngineClass | None,
        policy_ref: str | None,
        procedural_snapshot_ref: str | None,
        capture_mode: MemoryCaptureMode | None = None,
    ) -> MemoryCaptureResult:
        mode = capture_mode or self._capture_mode
        captured_observation = _captured_text(observation, mode)
        content: dict[str, object] = {
            "event_type": "failure_observation",
            "run_id": run_id,
            "turn_id": turn_id,
            "step_id": step_id,
            "prompt_summary": "",
            "response_summary": captured_observation,
            "summary_source": summary.source.value,
            "summary_model": summary.model,
            "summary_hash": _summary_hash(captured_observation),
            "capture_mode": mode.value,
            "tool_event_refs": [],
            "failure_observations": [captured_observation],
            "promotion_candidates": [],
            "token_usage": None,
        }
        return self._capture(
            event_kind="failure_observation",
            record_kind=MemoryRecordKind.EPISODIC_TURN,
            content=content,
            timestamp=timestamp,
            source_ref=SourceRef(ref_type=SourceRefType.TURN, ref=turn_id),
            run_id=run_id,
            step_id=step_id,
            provider=provider,
            model=model,
            cli_profile=cli_profile,
            engine_class=engine_class,
            policy_ref=policy_ref,
            procedural_snapshot_ref=procedural_snapshot_ref,
        )

    def capture_compaction_event(
        self,
        *,
        run_id: str,
        compaction_id: str,
        summary_text: str,
        summary: SummaryProvenance,
        input_memory_refs: Sequence[str],
        timestamp: datetime,
        provider: str | None,
        model: str | None,
        cli_profile: str | None,
        engine_class: MemoryOperationEngineClass | None,
        policy_ref: str | None,
        procedural_snapshot_ref: str | None,
        capture_mode: MemoryCaptureMode | None = None,
    ) -> MemoryCaptureResult:
        mode = capture_mode or self._capture_mode
        captured_summary = _captured_text(summary_text, mode)
        content: dict[str, object] = {
            "event_type": "compaction",
            "run_id": run_id,
            "compaction_id": compaction_id,
            "summary": captured_summary,
            "summary_source": summary.source.value,
            "summary_model": summary.model,
            "summary_hash": _summary_hash(captured_summary),
            "capture_mode": mode.value,
            "input_memory_refs": _string_list(input_memory_refs),
        }
        return self._capture(
            event_kind="compaction",
            record_kind=MemoryRecordKind.COMPACTION_EVENT,
            content=content,
            timestamp=timestamp,
            source_ref=SourceRef(ref_type=SourceRefType.COMPACTION, ref=compaction_id),
            run_id=run_id,
            step_id=None,
            provider=provider,
            model=model,
            cli_profile=cli_profile,
            engine_class=engine_class,
            policy_ref=policy_ref,
            procedural_snapshot_ref=procedural_snapshot_ref,
        )

    def _capture(
        self,
        *,
        event_kind: str,
        record_kind: MemoryRecordKind,
        content: Mapping[str, object],
        timestamp: datetime,
        source_ref: SourceRef,
        run_id: str,
        step_id: str | None,
        provider: str | None,
        model: str | None,
        cli_profile: str | None,
        engine_class: MemoryOperationEngineClass | None,
        policy_ref: str | None,
        procedural_snapshot_ref: str | None,
    ) -> MemoryCaptureResult:
        try:
            record = self._record(
                kind=record_kind,
                content=content,
                timestamp=timestamp,
                source_ref=source_ref,
                run_id=run_id,
                workflow_id=_optional_string(content.get("workflow_id")),
                cli_profile=cli_profile,
                provider=provider,
                # C-MEM-03 v1.2. This method is the ONE place `event_kind` is
                # held, so it decides the content-ORIGIN disposition; `_record`
                # holds the raw `provider` and the resolved scope, so it decides
                # the final tri-state. Computing a finished value here would be
                # non-conforming - the scope the comparison needs does not
                # exist at this altitude.
                content_origin=_CONTENT_ORIGIN_BY_EVENT_KIND.get(
                    event_kind, _ContentOrigin.UNDETERMINED
                ),
            )
        except MemoryCaptureScopeValueDomainError as exc:
            # Codex R7: the write-boundary REFUSAL is an outcome C-MEM-19 has a
            # vocabulary for, and it was the one capture outcome that emitted no
            # span at all - the denial fires inside `_record`, which ran BEFORE
            # the span below opened, so an out-of-domain scope was invisible to
            # the telemetry that exists to make denials countable.
            #
            # The span is opened here rather than moving `_record` inside the
            # one below, because the record is what supplies that span's `tier`
            # and its payload's `memory_id` - and because the denial must keep
            # PROPAGATING. Every other failure in this method folds into a
            # `FAILED` result; a refusal is a contract violation by the caller,
            # not an IO fault it may shrug off, and `raise` inside the context
            # manager also lets the span record the exception on its way out.
            #
            # `tier` is EPISODIC by construction - `_record` hardcodes it for
            # every record this class writes - and `record_count` is 0 because
            # the refusal precedes any record. The failure class is read from
            # the exception TYPE (`classify_memory_failure` honours the
            # `memory_failure_class` declaration, B-88) rather than spelled
            # literally here, so a future denial type carries its own class.
            with memory_telemetry_span(
                self._tracer_provider,
                tracer_name="harness.runtime.memory_capture",
                operation_name=MemoryTelemetryOperationName.CAPTURE,
                operation_kind=MemoryOperationKind.CAPTURE.value,
                tier=MemoryTier.EPISODIC.value,
                provider=provider,
                model=model,
                cli_profile=cli_profile,
                policy_decision=MemoryCaptureStatus.FAILED.value,
                failure_class=classify_memory_failure(exc),
                record_count=0,
            ):
                raise
        payload = self._operation_payload(
            event_kind=event_kind,
            actor=self._actor,
            memory_id=record.envelope.memory_id,
            timestamp=timestamp,
            run_id=run_id,
            step_id=step_id,
            provider=provider,
            model=model,
            cli_profile=cli_profile,
            engine_class=engine_class,
            policy_ref=policy_ref,
            procedural_snapshot_ref=procedural_snapshot_ref,
        )
        with memory_telemetry_span(
            self._tracer_provider,
            tracer_name="harness.runtime.memory_capture",
            operation_name=MemoryTelemetryOperationName.CAPTURE,
            operation_kind=MemoryOperationKind.CAPTURE.value,
            tier=record.envelope.tier.value,
            provider=provider,
            model=model,
            cli_profile=cli_profile,
            policy_decision=MemoryCaptureStatus.CAPTURED.value,
            record_count=1,
        ) as span:
            try:
                # Write the record BEFORE the ledger entry that references it
                # (`payload.memory_refs = (record.envelope.memory_id,)`).
                # Appending the ledger entry first would leave a dangling
                # reference — a memory_id the append-only, hash-chained
                # ledger vouches for but that was never persisted — if the
                # record write then failed. Swapped order downgrades a
                # ledger-append failure to an orphaned-but-safe record (the
                # record itself is durable; only its audit trail is
                # incomplete), never a ledger entry pointing at nothing.
                self._store.write_record(record)
                try:
                    operation_result = self._store.append_memory_operation(payload)
                except MemoryOperationIdempotencyConflictError:
                    # Codex R6: the REVERSE of the race the repair call site
                    # catches. There, the repair loses to this append; here,
                    # this append loses to the repair. A second worker can
                    # observe the `run.json` written one line above while this
                    # append is still in flight, read it as a torn capture, and
                    # complete it with `repair_capture_operation`'s
                    # worker-invariant payload. That row diverges from this one
                    # (a repair cannot know the dispatch metadata), so the
                    # ledger raises here - and the broad handler below turned
                    # that into FAILED, aborting a run whose accounting was in
                    # fact durably complete.
                    #
                    # A conflict is NOT by itself evidence of that (Codex R8).
                    # The ledger raises whenever an entry already occupies this
                    # `idempotency_key`, and for EPISODIC_RUN the key is a
                    # function of `event_kind` and a `memory_id` derived from
                    # the RUN_ID ALONE (`_memory_id_for`) - not from content -
                    # so a plain SECOND `capture_run_start` for the same run
                    # with divergent workflow / provider / policy metadata,
                    # called outside `LocalAutomaticMemoryRuntime`'s presence
                    # guard, lands on this same key too. That call has already
                    # OVERWRITTEN `run.json` (one file per run), so reading its
                    # conflict as completion returned CAPTURED over a durable
                    # disagreement: the record holding call-2's data and the
                    # sole ledger row holding call-1's.
                    #
                    # So the occupant is IDENTIFIED before the conflict is
                    # read as completion, and only the synthetic REPAIR row
                    # qualifies. `capture_repair_actor` is run-keyed and is
                    # composed NOWHERE but the repair path; an ordinary capture
                    # always attributes its row to the caller-supplied
                    # `self._actor` (a dispatch actor), so no normal capture can
                    # produce that identity. Any other occupant - a real prior
                    # capture with a divergent payload - re-raises into the
                    # broad handler below and stays FAILED, which is the
                    # pre-R6 strictness for genuine divergent replays.
                    #
                    # The read costs a whole-ledger walk, but only on the
                    # CONFLICT path: an uncontended capture never reaches it.
                    #
                    # Accepted information loss: the durable row is then the
                    # repair's synthetic payload (`provider` / `model` /
                    # `policy_ref` None) rather than this dispatch's richer
                    # metadata. Correcting it would mean REWRITING a
                    # hash-chained append-only ledger row, which is a strictly
                    # worse trade than losing four attributes on a row whose
                    # purpose is to attest that the capture is durable. The
                    # RECORD keeps its full content either way: in this
                    # ordering this worker wrote it, and the repair writes no
                    # record.
                    #
                    # `event_kind` is still checked FIRST, and it is the cheap
                    # half: `repair_capture_operation` is reached from one call
                    # site, always with `RUN_START_EVENT_KIND`, so no other
                    # event kind has a second writer sharing its keys and no
                    # repair row can ever occupy one. A conflict on any of them
                    # is a genuine divergence, must still surface as FAILED,
                    # and is spared the ledger read.
                    #
                    # The span needs no annotation: it already declares
                    # `policy_decision=captured`, and no `failure_class`
                    # belongs on an outcome that is not a failure.
                    if event_kind != RUN_START_EVENT_KIND:
                        raise
                    if not self._conflicting_row_is_a_repair(
                        action_id=payload.action_id,
                        run_id=run_id,
                    ):
                        raise
                    operation_result = None
            except Exception as exc:
                set_memory_telemetry_attributes(
                    span,
                    policy_decision=MemoryCaptureStatus.FAILED.value,
                    failure_class=MemoryTelemetryFailureClass.IO_FAILURE,
                )
                return MemoryCaptureResult(
                    status=MemoryCaptureStatus.FAILED,
                    event_kind=event_kind,
                    record_kind=record_kind,
                    failure_reason=f"{type(exc).__name__}: {exc}",
                )
            return MemoryCaptureResult(
                status=MemoryCaptureStatus.CAPTURED,
                event_kind=event_kind,
                record_kind=record_kind,
                memory_id=record.envelope.memory_id,
                operation_action_id=payload.action_id,
                operation_result=operation_result,
            )

    def _conflicting_row_is_a_repair(self, *, action_id: Identifier, run_id: str) -> bool:
        """True when the row occupying `action_id` is the synthetic REPAIR row.

        Codex R8. The discriminator between the two writers that can legally
        share one run-start `action_id`:

        * `repair_capture_operation` attributes its row to
          `capture_repair_actor(run_id)` - an identity composed there and
          NOWHERE else, keyed by the run so every repairing worker composes the
          same one.
        * every ordinary capture attributes its row to `self._actor`, the
          dispatch actor its caller bound at construction.

        So a repair actor on the occupying row means the occupant is a repair,
        which is the only occupant `_capture` may read as completion.

        Codex R9 - what makes that inference SOUND rather than conventional:
        `actor_id` is an unrestricted `str`, so on its own "no ordinary capture
        composes this identity" was an assumption about caller behaviour, and a
        caller that bound `memory-capture-repair:{run_id}` itself would have
        made a later DIVERGENT run-start replay read this row as a repair and
        return `CAPTURED` over a record/ledger disagreement. The namespace is
        therefore RESERVED at the single point an ordinary actor enters
        (`__init__` refuses `_RESERVED_REPAIR_ACTOR_PREFIX`), leaving
        `repair_capture_operation` its only producer. Actor equality is
        consequently unforgeable, not merely unlikely to collide.

        Absence -
        including a ledger that cannot be read, whose exception propagates into
        the broad handler and fails the capture - is answered `False`, so the
        conflict stays a failure.

        Keyed on `action_id`, not `memory_refs`: run-start and run-close share
        one EPISODIC_RUN `memory_id`, so `memory_refs` cannot tell the two
        capture events apart (the same reason
        `LocalAutomaticMemoryRuntime._run_start_capture_row_present` keys that
        way).
        """
        repair_actor = capture_repair_actor(run_id)
        return any(
            entry.action_id == action_id
            and entry.operation_kind is MemoryOperationKind.CAPTURE
            and entry.actor == repair_actor
            for entry in self._store.read_memory_operations()
        )

    def repair_capture_operation(
        self,
        *,
        event_kind: str,
        record: MemoryStoreRecord,
        timestamp: datetime,
        run_id: str,
    ) -> MemoryCaptureResult:
        """Append the C-MEM-08 CAPTURE row for an ALREADY-STORED record.

        Completes a TORN capture. `_capture` writes the record before its
        ledger row (see the ordering rationale there), so a failed append
        leaves a durable record carrying no operation row - the record's
        presence is therefore not evidence that its capture completed. Re-running
        `_capture` is not the repair: EPISODIC_RUN is one `run.json` per run, so
        it would REWRITE the stored envelope under today's scope, which is
        precisely what the forward-only posture forbids. This writes the
        MISSING ROW ONLY, against the envelope's OWN `memory_id` as stored.

        The row reuses the `action_id` / `idempotency_key` the interrupted
        attempt would have written, so it lands in exactly the slot that attempt
        left empty rather than duplicating.

        Codex R5: the payload is a PURE FUNCTION of the stored record and
        `run_id` - it takes NOTHING from the repairing worker. Two workers
        resuming one torn run compose byte-identical payloads, so the second
        append resolves through the ledger's equivalence check as
        `IDEMPOTENT_NOOP` (`append_memory_operation` compares the 18-field
        equivalence payload, which excludes `timestamp`, and only raises
        `MemoryOperationIdempotencyConflictError` on genuine divergence).
        Sourcing per-worker dispatch metadata here instead is what made the
        second repairer raise, failing a run whose row was already durable.

        Field by field, and why each is worker-invariant:

        * `action_id` / `idempotency_key` / `memory_refs` - the stored
          envelope's own `memory_id`, never re-derived.
        * `actor` - `capture_repair_actor(run_id)`; see there.
        * `run_id` - the key the record was READ by, so identical by
          construction for any worker that reached this repair.
        * `cli_profile` / `engine_class` - read back from the STORED content,
          where the torn capture itself recorded them. These are the original
          capture's values, not the repairer's.
        * `step_id` - read back from stored content too; absent on the
          run-start content shape, which is the `None` the torn attempt carried.
        * `provider` / `model` / `policy_ref` / `procedural_snapshot_ref` -
          `None`. The stored record does not carry them (`provider_route` is
          the CHAIN, not the access-mode SELECTION the torn payload recorded),
          and they describe the dispatch that tore, which the repairer is not.
          `None` is the honest deterministic value: a repair row attests that
          this capture is durable, not which dispatch performed it.

        The idempotency conflict is RAISED, not folded into a `FAILED` result:
        it is a concurrency signal rather than an IO fault, and what it means
        (a row already occupies this exact capture slot) is a judgement for the
        caller that knows it is repairing. Every other append failure still
        returns the `FAILED` result unchanged.
        """
        envelope = record.envelope
        cli_profile = _stored_text(record.content, "cli_profile")
        payload = self._operation_payload(
            event_kind=event_kind,
            actor=capture_repair_actor(run_id),
            memory_id=envelope.memory_id,
            timestamp=timestamp,
            run_id=run_id,
            step_id=_stored_text(record.content, "step_id"),
            provider=None,
            model=None,
            cli_profile=cli_profile,
            engine_class=_stored_engine_class(record.content),
            policy_ref=None,
            procedural_snapshot_ref=None,
        )
        with memory_telemetry_span(
            self._tracer_provider,
            tracer_name="harness.runtime.memory_capture",
            operation_name=MemoryTelemetryOperationName.CAPTURE,
            operation_kind=MemoryOperationKind.CAPTURE.value,
            tier=envelope.tier.value,
            cli_profile=cli_profile,
            policy_decision=MemoryCaptureStatus.CAPTURED.value,
            record_count=1,
        ) as span:
            try:
                operation_result = self._store.append_memory_operation(payload)
            except MemoryOperationIdempotencyConflictError:
                raise
            except Exception as exc:
                set_memory_telemetry_attributes(
                    span,
                    policy_decision=MemoryCaptureStatus.FAILED.value,
                    failure_class=MemoryTelemetryFailureClass.IO_FAILURE,
                )
                return MemoryCaptureResult(
                    status=MemoryCaptureStatus.FAILED,
                    event_kind=event_kind,
                    record_kind=envelope.kind,
                    failure_reason=f"{type(exc).__name__}: {exc}",
                )
            return MemoryCaptureResult(
                status=MemoryCaptureStatus.CAPTURED,
                event_kind=event_kind,
                record_kind=envelope.kind,
                memory_id=envelope.memory_id,
                operation_action_id=payload.action_id,
                operation_result=operation_result,
            )

    def _operation_payload(
        self,
        *,
        event_kind: str,
        actor: Actor,
        memory_id: MemoryID,
        timestamp: datetime,
        run_id: str,
        step_id: str | None,
        provider: str | None,
        model: str | None,
        cli_profile: str | None,
        engine_class: MemoryOperationEngineClass | None,
        policy_ref: str | None,
        procedural_snapshot_ref: str | None,
    ) -> MemoryOperationPayload:
        action_id = capture_operation_action_id(event_kind, memory_id)
        return MemoryOperationPayload(
            action_id=action_id,
            idempotency_key=Identifier(f"idempotent:{action_id}"),
            actor=actor,
            timestamp=timestamp,
            operation_kind=MemoryOperationKind.CAPTURE,
            operation_projection=MemoryOperationProjection.NONE,
            run_id=run_id,
            step_id=step_id,
            provider=provider,
            model=model,
            cli_profile=cli_profile,
            engine_class=engine_class,
            memory_refs=(memory_id,),
            policy_ref=policy_ref,
            procedural_snapshot_ref=procedural_snapshot_ref,
        )

    def _record(
        self,
        *,
        kind: MemoryRecordKind,
        content: Mapping[str, object],
        timestamp: datetime,
        source_ref: SourceRef,
        run_id: str,
        workflow_id: str | None,
        cli_profile: str | None,
        provider: str | None,
        content_origin: _ContentOrigin,
    ) -> MemoryStoreRecord:
        content_hash = compute_memory_content_hash(content)
        memory_id = _memory_id_for(kind, content_hash=content_hash, run_id=run_id)
        # Bound to a local BEFORE the envelope: the C-MEM-03 comparison is
        # against the RESOLVED scope's own `provider_family`, so the resolution
        # cannot stay inline at the `scope=` argument.
        scope = self._scope_for_record(
            workflow_id=workflow_id,
            cli_profile=cli_profile,
            provider=provider,
        )
        return MemoryStoreRecord(
            envelope=MemoryRecordEnvelope(
                memory_id=memory_id,
                schema_version=_SCHEMA_VERSION,
                tier=MemoryTier.EPISODIC,
                kind=kind,
                created_at=timestamp,
                updated_at=None,
                source_refs=(source_ref,),
                scope=scope,
                content_hash=content_hash,
                # Hash-inert by construction: both `content_hash` and
                # `memory_id` are already fixed above, from content alone.
                captured_cross_family=_captured_cross_family(
                    content_origin=content_origin,
                    provider=provider,
                    scope=scope,
                ),
            ),
            content=content,
        )

    def _scope_for_record(
        self,
        *,
        workflow_id: str | None,
        cli_profile: str | None,
        provider: str | None,
    ) -> MemoryScope:
        """Return the scope this capture writes under (`B-89` / `B-90`).

        The run's composed `record_scope` wins when it was supplied - it already
        carries the `tenant` and `workload_class` fields the independently
        constructed residual below omits (`B-90`), and re-deriving any of them
        per turn is precisely the defect `B-89` names. The residual
        construction is kept for callers with no composed scope.

        BOTH paths then pass through the SAME canonicalize-or-deny, because
        this method is the write boundary and a scope arriving from a caller is
        no more trusted than one built here: a registered provider key is
        canonicalized to its `ProviderFamily` value, and an out-of-domain
        identifier is REFUSED rather than stored or degraded to `null` (`null`
        is the unpartitioned wildcard, so degrading would widen the record's
        reach - C-MEM-03 v1.1). On the composed production path the supplied
        scope is already canonical and this is a no-op; returning it VERBATIM
        instead would let any caller persist a raw registered key or an
        out-of-domain value straight past the value domain.
        """
        scope = self._record_scope
        if scope is None:
            scope = MemoryScope(
                project=self._project,
                workflow=workflow_id,
                provider_family=provider,
                cli_profile=cli_profile,
                visibility=self._visibility,
            )
        resolution = resolve_scope_family(scope)
        if resolution.family_out_of_domain:
            raise MemoryCaptureScopeValueDomainError(scope_family_out_of_domain_message(scope))
        return resolution.scope


def _captured_cross_family(
    *,
    content_origin: _ContentOrigin,
    provider: str | None,
    scope: MemoryScope,
) -> CapturedCrossFamily:
    """The C-MEM-03 v1.2 tri-state for one capture.

    The content-origin disposition GATES the family comparison: where the
    stored content was not produced by a completed provider dispatch the
    comparison is not consulted at all, because there is no producing leg for
    it to be about.

    The comparison itself reuses the B-86 / B-89 authorities verbatim -
    `canonical_scope_family`, which binds the fail-closed
    `provider_family_for_scope_check` - against the ALREADY-canonical
    `provider_family` of the resolved scope. No new normalization posture.

    `unknown` (never `false`) in each of the four undetermined cases: content
    not produced by a completed dispatch; no `provider`; an unregistered
    provider key, whose family the fail-closed authority declines to guess;
    and a `null` `scope.provider_family`, the unpartitioned wildcard against
    which "cross-family" is undefined.
    """

    if content_origin is not _ContentOrigin.DISPATCH_DERIVED:
        return CapturedCrossFamily.UNKNOWN
    if provider is None:
        return CapturedCrossFamily.UNKNOWN
    scope_family = scope.provider_family
    if scope_family is None:
        return CapturedCrossFamily.UNKNOWN
    dispatch_family = canonical_scope_family(provider)
    if dispatch_family is None:
        return CapturedCrossFamily.UNKNOWN
    if dispatch_family == scope_family:
        return CapturedCrossFamily.FALSE
    return CapturedCrossFamily.TRUE


def _captured_text(value: str, mode: MemoryCaptureMode) -> str:
    if mode is MemoryCaptureMode.REDACTED:
        return _REDACTED_SUMMARY
    return value


def _summary_hash(*parts: str) -> str:
    normalized = "\n".join(unicodedata.normalize("NFC", part) for part in parts)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _memory_id_for(
    kind: MemoryRecordKind,
    *,
    content_hash: bytes,
    run_id: str,
) -> MemoryID:
    if kind is MemoryRecordKind.EPISODIC_RUN:
        run_digest = hashlib.sha256(unicodedata.normalize("NFC", run_id).encode("utf-8"))
        return MemoryID(f"mem:episodic:{kind.value}:{run_digest.hexdigest()}")
    return derive_memory_id(MemoryTier.EPISODIC, kind, content_hash)


def _string_list(values: Sequence[str]) -> list[str]:
    return [str(value) for value in values]


def _token_usage(token_usage: Mapping[str, int] | None) -> dict[str, int] | None:
    if token_usage is None:
        return None
    return {str(key): int(value) for key, value in token_usage.items()}


def _engine_class_value(engine_class: MemoryOperationEngineClass | None) -> str | None:
    if engine_class is None:
        return None
    return engine_class.value


def _optional_string(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return str(value)


def _stored_text(content: Mapping[str, object], key: str) -> str | None:
    """A stored content field, taken only when it is genuinely text.

    Deliberately stricter than `_optional_string`: that one COERCES, which is
    right when the caller authored the value this turn, and wrong when reading
    a durable record back - `str()` over an unexpected shape would invent a
    field value the original capture never recorded. An absent or non-text
    field reads as `None`, which is what the torn payload carried anyway.
    """
    value = content.get(key)
    return value if isinstance(value, str) else None


def stored_capture_event_type(content: Mapping[str, object]) -> str | None:
    """The `event_type` a stored capture record's content declares.

    Every `capture_*` method opens its content with this field, so it is the
    record's own statement of WHICH event wrote it - the discriminator a reader
    needs when one `memory_id` is shared by several events (EPISODIC_RUN is one
    `run.json` per run, written by run-start and OVERWRITTEN by run-close).

    Exported for the same reason `capture_operation_action_id` is: the field is
    written here, so a caller asking what a durable record IS reads it through
    this module rather than re-spelling the key. Strict (`_stored_text`): an
    absent or non-text field reads as `None` - an unrecognizable record, never
    a guess at one.
    """
    return _stored_text(content, "event_type")


def _stored_engine_class(content: Mapping[str, object]) -> MemoryOperationEngineClass | None:
    """The stored content's `engine_class`, or `None` when it is not one."""
    value = _stored_text(content, "engine_class")
    if value is None:
        return None
    try:
        return MemoryOperationEngineClass(value)
    except ValueError:
        return None


__all__ = [
    "RUN_START_EVENT_KIND",
    "EpisodicMemoryCapture",
    "MemoryCaptureMode",
    "MemoryCaptureReservedActorError",
    "MemoryCaptureResult",
    "MemoryCaptureScopeValueDomainError",
    "MemoryCaptureStatus",
    "MemoryCaptureStore",
    "SummaryProvenance",
    "SummarySource",
    "capture_operation_action_id",
    "capture_repair_actor",
    "stored_capture_event_type",
]
