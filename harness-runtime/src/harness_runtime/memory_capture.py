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
    memory_telemetry_span,
    set_memory_telemetry_attributes,
)
from harness_is.memory_operation_ledger import (
    MemoryOperationEngineClass,
    MemoryOperationKind,
    MemoryOperationPayload,
    MemoryOperationProjection,
    MemoryOperationWriteResult,
)
from harness_is.memory_record_envelope import (
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
from harness_is.state_ledger_entry_schema import Actor, Identifier
from pydantic import BaseModel, ConfigDict, model_validator

from harness_runtime.memory_scope_family import (
    resolve_scope_family,
    scope_family_out_of_domain_message,
)

_REDACTED_SUMMARY = "[redacted]"
_SCHEMA_VERSION = "episodic-capture/v1"

RUN_START_EVENT_KIND = "run_start"
"""Event kind of the run-start capture, shared with its durable-row probes."""


def capture_operation_action_id(event_kind: str, memory_id: MemoryID) -> Identifier:
    """Return the C-MEM-08 `action_id` a capture of `memory_id` writes.

    Exported because it is the ONLY key that identifies one capture event in
    the ledger: run-start and run-close share a single EPISODIC_RUN
    `memory_id`, so `memory_refs` cannot tell them apart. A caller asking
    whether a specific capture completed must ask by this id, and must build
    it here rather than re-spelling the format.
    """
    return Identifier(f"capture:{event_kind}:{memory_id}")


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


class MemoryCaptureScopeValueDomainError(ValueError):
    """Raised when a capture scope's `provider_family` is out of the value domain.

    U-MEM-26 / C-MEM-03 v1.1. Reached only on the RESIDUAL construction path
    below (no `record_scope` supplied), where the scope is still derived from a
    per-dispatch provider key. A run that supplies its composed `record_scope`
    cannot reach it: that scope's `provider_family` is by construction a
    `ProviderFamily` value derived once from the chain primary.

    It is a refusal, not a substrate fault, so it declares `policy_denial`
    rather than inheriting the message-heuristic residual - the same
    by-construction discipline `B-88` applied to the tool-executor family.
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
        """
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
        record = self._record(
            kind=record_kind,
            content=content,
            timestamp=timestamp,
            source_ref=source_ref,
            run_id=run_id,
            workflow_id=_optional_string(content.get("workflow_id")),
            cli_profile=cli_profile,
            provider=provider,
        )
        payload = self._operation_payload(
            event_kind=event_kind,
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
                operation_result = self._store.append_memory_operation(payload)
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

    def repair_capture_operation(
        self,
        *,
        event_kind: str,
        envelope: MemoryRecordEnvelope,
        timestamp: datetime,
        run_id: str,
        step_id: str | None,
        provider: str | None,
        model: str | None,
        cli_profile: str | None,
        engine_class: MemoryOperationEngineClass | None,
        policy_ref: str | None,
        procedural_snapshot_ref: str | None,
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
        attempt would have written, so it lands in exactly the slot that
        attempt left empty and a concurrent second repair resolves through the
        ledger's own idempotency rule (no-op on an equivalent payload, loud
        conflict otherwise) instead of duplicating - the same semantics two
        concurrent FIRST captures of one run already have.
        """
        payload = self._operation_payload(
            event_kind=event_kind,
            memory_id=envelope.memory_id,
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
            tier=envelope.tier.value,
            provider=provider,
            model=model,
            cli_profile=cli_profile,
            policy_decision=MemoryCaptureStatus.CAPTURED.value,
            record_count=1,
        ) as span:
            try:
                operation_result = self._store.append_memory_operation(payload)
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
            actor=self._actor,
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
    ) -> MemoryStoreRecord:
        content_hash = compute_memory_content_hash(content)
        memory_id = _memory_id_for(kind, content_hash=content_hash, run_id=run_id)
        return MemoryStoreRecord(
            envelope=MemoryRecordEnvelope(
                memory_id=memory_id,
                schema_version=_SCHEMA_VERSION,
                tier=MemoryTier.EPISODIC,
                kind=kind,
                created_at=timestamp,
                updated_at=None,
                source_refs=(source_ref,),
                scope=self._scope_for_record(
                    workflow_id=workflow_id,
                    cli_profile=cli_profile,
                    provider=provider,
                ),
                content_hash=content_hash,
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


__all__ = [
    "RUN_START_EVENT_KIND",
    "EpisodicMemoryCapture",
    "MemoryCaptureMode",
    "MemoryCaptureResult",
    "MemoryCaptureScopeValueDomainError",
    "MemoryCaptureStatus",
    "MemoryCaptureStore",
    "SummaryProvenance",
    "SummarySource",
    "capture_operation_action_id",
]
