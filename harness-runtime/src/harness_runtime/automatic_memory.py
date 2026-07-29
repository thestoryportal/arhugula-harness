"""Automatic local memory substrate wiring.

This module binds the existing memory store, derived retrieval index,
retriever, prompt-packet composer, and standard tool executor from
``RuntimeConfig.memory``. The substrate is local-first: provider-native remote
memory is opt-in and remains the lowest-priority access mode.

Realizes the runtime composition of C-MEM-11 (retrieval and ranking),
C-MEM-12 (memory packet assembly), and C-MEM-14 (provider-neutral memory
tools) over the C-MEM-09 policy and C-MEM-08 operation ledger.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Any, Protocol, cast, runtime_checkable

from harness_core import WorkloadClass
from harness_cp.cp_shared_types import ProviderAgnosticPayload
from harness_cp.cross_family_fallback_chain import FallbackChain
from harness_cp.memory_access_mode import reflect_memory_provider_capabilities
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.workflow_driver_types import StepExecutionContext, WorkflowStep
from harness_is.cli_profile import DEFAULT_GENERIC_CLI_PROFILE
from harness_is.memory_operation_ledger import (
    MemoryOperationEngineClass,
    MemoryOperationIdempotencyConflictError,
    MemoryOperationKind,
)
from harness_is.memory_path_registry import MemoryPathRegistry, MemoryRootBinding
from harness_is.memory_policy import (
    AccessDecision,
    CaptureDecision,
    MemoryPolicyDocument,
    MemoryPolicyResolver,
    PromotionDecision,
    ReviewMode,
)
from harness_is.memory_record_envelope import (
    MemoryID,
    MemoryRecordKind,
    MemoryScope,
    MemoryVisibility,
)
from harness_is.memory_retrieval import MemoryRetriever
from harness_is.memory_retrieval_index import (
    DerivedRetrievalIndex,
    DerivedRetrievalIndexMissingError,
    DerivedRetrievalIndexStaleError,
    DerivedRetrievalIndexStore,
)
from harness_is.memory_store import CanonicalMemoryStore, MemoryStoreRecord

from harness_runtime.memory_capture import (
    RUN_START_EVENT_KIND,
    EpisodicMemoryCapture,
    MemoryCaptureMode,
    MemoryCaptureResult,
    MemoryCaptureStatus,
    SummaryProvenance,
    SummarySource,
    capture_operation_action_id,
    stored_capture_event_type,
)
from harness_runtime.memory_context import (
    MemoryContextCompositionRequest,
    RuntimeMemoryContext,
    RuntimeMemoryContextComposer,
)
from harness_runtime.memory_scope_family import canonical_scope_family
from harness_runtime.memory_tool_executor import StandardMemoryToolExecutor
from harness_runtime.types import RuntimeConfig


@runtime_checkable
class AutomaticMemoryRuntime(Protocol):
    """Per-dispatch automatic memory context provider."""

    standard_memory_tool_executor: Any

    def compose_for_dispatch(
        self,
        *,
        binding: StepEffectiveBinding,
        fallback_chain: FallbackChain,
        step: WorkflowStep,
        step_context: StepExecutionContext,
    ) -> RuntimeMemoryContext: ...

    def capture_turn_completion(
        self,
        *,
        memory_context: RuntimeMemoryContext,
        payload: ProviderAgnosticPayload,
        step_context: StepExecutionContext,
        step_id: str,
        provider: str,
        model: str,
        response: Mapping[str, Any],
        input_tokens: int | None,
        output_tokens: int | None,
    ) -> None: ...


class AutoRefreshingDerivedRetrievalIndexStore(DerivedRetrievalIndexStore):
    """Derived index store that rebuilds local indexes on first use or staleness."""

    def read_current(self, *, require_fresh: bool = True) -> DerivedRetrievalIndex:
        try:
            return super().read_current(require_fresh=require_fresh)
        except (DerivedRetrievalIndexMissingError, DerivedRetrievalIndexStaleError):
            return self.rebuild(indexed_at=datetime.now(UTC))


class LocalAutomaticMemoryRuntime:
    """Runtime-local automatic memory composer."""

    def __init__(
        self,
        *,
        config: RuntimeConfig,
        workload_class: WorkloadClass | None = None,
        tracer_provider: object | None = None,
    ) -> None:
        memory_root = config.memory.root_path or (config.repository_root / ".harness" / "memory")
        self._surface = config.deployment_surface
        self._policy = _policy_from_config(config)
        self._policy_resolver = MemoryPolicyResolver(self._policy)
        self._token_budget = config.memory.token_budget
        self._project = config.repository_root.name
        self._workload_class = workload_class
        self._tenant_id = config.tenant_id
        self._capture_run_events = config.memory.capture_run_events
        self._capture_turns = config.memory.capture_turns
        self._tracer_provider = tracer_provider
        self._started_runs: set[str] = set()
        # Provider keys routed through external OAuth/subscription CLIs. Their dispatch
        # is subprocess text-only (no tool loop), so memory must reach them via the
        # prompt-extension packet, not standard memory tools (see compose_for_dispatch).
        self._external_cli_provider_names: frozenset[str] = frozenset(
            provider.provider for provider in config.external_cli_providers
        )

        binding = MemoryRootBinding(default_root=memory_root)
        MemoryPathRegistry(binding).ensure_canonical_roots(self._surface)
        store = CanonicalMemoryStore(
            root_binding=binding,
            deployment_surface=self._surface,
        )
        self._store = store
        # U-MEM-26: `harness-is` declares the C-MEM-03 request-side value domain
        # as an injectable seam because the IS axis has zero outbound cross-axis
        # edges. This is its composition root - absent the injection the read
        # layers compare `provider_family` as the raw string it arrived as, and
        # a crafted raw-key request reaches a legacy raw-key record.
        index_store = AutoRefreshingDerivedRetrievalIndexStore(
            root_binding=binding,
            deployment_surface=self._surface,
            family_canonicalizer=canonical_scope_family,
        )
        index_store.read_current()
        retriever = MemoryRetriever(
            store=store,
            index_store=index_store,
            policy_resolver=self._policy_resolver,
            policy_ref=self._policy.policy_id,
            family_canonicalizer=canonical_scope_family,
        )
        self._composer = RuntimeMemoryContextComposer(
            retriever=retriever,
            operation_store=store,
            tracer_provider=tracer_provider,
        )
        self.standard_memory_tool_executor = (
            StandardMemoryToolExecutor(
                store=store,
                index_store=index_store,
                retriever=retriever,
                policy_resolver=self._policy_resolver,
                tracer_provider=tracer_provider,
            )
            if config.memory.standard_tools_enabled
            else None
        )

    def compose_for_dispatch(
        self,
        *,
        binding: StepEffectiveBinding,
        fallback_chain: FallbackChain,
        step: WorkflowStep,
        step_context: StepExecutionContext,
    ) -> RuntimeMemoryContext:
        model_binding = binding.model_binding
        context = self._composer.compose_run_start(
            MemoryContextCompositionRequest(
                run_id=_run_id(step_context),
                workflow_id=step_context.workflow_id,
                workload_class=(
                    self._workload_class.value if self._workload_class is not None else None
                ),
                query_summary=_query_summary(step.step_payload),
                model_binding=model_binding,
                fallback_chain=fallback_chain,
                cli_profile=DEFAULT_GENERIC_CLI_PROFILE,
                workflow_policy=self._policy,
                step_policy=None,
                token_budget=self._token_budget,
                record_scope=MemoryScope(
                    project=self._project,
                    workflow=step_context.workflow_id,
                    workload_class=(
                        self._workload_class.value if self._workload_class is not None else None
                    ),
                    provider_family=fallback_chain.primary.family.value,
                    cli_profile=DEFAULT_GENERIC_CLI_PROFILE.profile_id,
                    tenant=step_context.tenant_id or self._tenant_id,
                    visibility=MemoryVisibility.PROJECT,
                ),
                allowed_kinds=_retrievable_kinds(),
                timestamp=datetime.now(UTC),
                actor=step_context.parent_actor,
                policy_ref=self._policy.policy_id,
                provider_capabilities=reflect_memory_provider_capabilities(
                    model_binding,
                    is_external_cli=model_binding.provider in self._external_cli_provider_names,
                ),
            )
        )
        self._capture_run_start_once(
            context=context,
            fallback_chain=fallback_chain,
            step_context=step_context,
            engine_class=binding.engine_class,
        )
        return context

    def capture_turn_completion(
        self,
        *,
        memory_context: RuntimeMemoryContext,
        payload: ProviderAgnosticPayload,
        step_context: StepExecutionContext,
        step_id: str,
        provider: str,
        model: str,
        response: Mapping[str, Any],
        input_tokens: int | None,
        output_tokens: int | None,
    ) -> None:
        if not self._capture_turns:
            return
        capture_mode = _capture_mode_from_decision(
            self._policy_resolver.resolve_capture().capture_decision
        )
        if capture_mode is None:
            return
        result = self._recorder(
            actor=step_context.parent_actor,
            scope=memory_context.record_scope,
            capture_mode=capture_mode,
        ).capture_turn_completion(
            run_id=memory_context.run_id,
            turn_id=_turn_id(memory_context.run_id, step_id, step_context.step_index),
            step_id=step_id,
            prompt_summary=_query_summary(_payload_mapping(payload)),
            response_summary=_response_summary(response),
            summary=SummaryProvenance(source=SummarySource.HARNESS_RULE),
            tool_event_refs=(),
            failure_observations=(),
            promotion_candidates=(),
            token_usage=_token_usage(input_tokens=input_tokens, output_tokens=output_tokens),
            timestamp=datetime.now(UTC),
            provider=provider,
            model=model,
            cli_profile=memory_context.selection.cli_profile_ref,
            engine_class=_memory_engine_class(step_context.run_engine_class),
            policy_ref=memory_context.policy_ref,
            procedural_snapshot_ref=None,
            capture_mode=capture_mode,
        )
        _raise_capture_failure(result)

    def _capture_run_start_once(
        self,
        *,
        context: RuntimeMemoryContext,
        fallback_chain: FallbackChain,
        step_context: StepExecutionContext,
        engine_class: object,
    ) -> None:
        if not self._capture_run_events or context.run_id in self._started_runs:
            return
        if (
            _capture_mode_from_decision(self._policy_resolver.resolve_capture().capture_decision)
            is None
        ):
            return
        if self._store.has_run_record(context.run_id):
            # Codex R3 [P2-c] durable-presence idempotence. `_started_runs` is
            # in-process ONLY, so a fresh bootstrap resuming an older run finds
            # it empty and captures run-start again - and EPISODIC_RUN is one
            # `run.json` per run_id, so that second write REPLACES the stored
            # envelope under today's canonical scope. Silently re-scoping a
            # pre-v1.1 record is exactly what the C-MEM-03 forward-only posture
            # forbids, so an existing record ends the capture instead. Two
            # processes racing a genuinely FIRST write still resolve
            # last-writer-wins as before; this closes the resume case, which is
            # the one that rewrites history rather than re-deciding it.
            #
            # Codex R4: presence of the RECORD is not presence of the CAPTURE.
            # `_capture` writes the record before its C-MEM-08 row, so a
            # transient ledger failure leaves the record durable and the row
            # missing - and this presence check then made the retry a no-op, so
            # the required row was never written at all. The stored record
            # still ends the capture; what it no longer does is end the
            # OPERATION.
            self._complete_torn_run_start_capture(
                context=context,
                step_context=step_context,
            )
            self._started_runs.add(context.run_id)
            return
        result = self._recorder(
            actor=step_context.parent_actor,
            scope=context.record_scope,
            capture_mode=MemoryCaptureMode.SUMMARIZED,
        ).capture_run_start(
            run_id=context.run_id,
            workflow_id=step_context.workflow_id,
            thread_id=step_context.parent_action_id,
            provider_route=_provider_route(fallback_chain),
            timestamp=datetime.now(UTC),
            provider=context.selection.selected_provider,
            model=context.selection.selected_model,
            cli_profile=context.selection.cli_profile_ref,
            engine_class=_memory_engine_class(engine_class),
            policy_ref=context.policy_ref,
            procedural_snapshot_ref=None,
        )
        _raise_capture_failure(result)
        self._started_runs.add(context.run_id)

    def _complete_torn_run_start_capture(
        self,
        *,
        context: RuntimeMemoryContext,
        step_context: StepExecutionContext,
    ) -> None:
        """Append the run-start CAPTURE row when the stored record carries none.

        The states a stored record can be in, and what each gets:

        1. record + its run-start row  -> nothing (the R3 resume case, and the
           genuinely-legacy pre-v1.1 runs whose own capture appended their row
           at their own capture time). The envelope is not touched.
        2. RUN-START record, NO row    -> the torn write. The MISSING ROW ONLY
           is appended, against the STORED envelope's own identity. The record
           is not rewritten and its scope is not re-derived, so the
           forward-only posture the presence check exists to protect holds
           unchanged.
        3. any OTHER record, NO row    -> nothing (Codex R7). See below.
        4. no record                   -> not reached; the caller captures
           normally.

        Codex R7: (2) and (3) were one case, and the missing row was read as
        proof of a torn START. It is not. EPISODIC_RUN is ONE `run.json` keyed
        by `run_id` and run-close OVERWRITES it, so a run that started and
        closed before this substrate existed - or that was torn AFTER its
        close - stores a `run_close` record carrying no run-start row, and the
        repair then appended a run-start row asserting a start that this record
        is not evidence of. The stored content's own `event_type` is therefore
        read first, and only a genuine run-start record is repairable.

        A run-close (or unreadable-shape) record gets NO row and an untouched
        envelope: that run's durable history is closed or opaque to us, and
        FABRICATING a start row against it is strictly worse than leaving the
        row missing - a missing row is a gap the ledger honestly shows, while a
        fabricated one is a false attestation in an append-only, hash-chained
        substrate that cannot be retracted. The caller still registers the
        `run_id` in `_started_runs`, so the run proceeds exactly as it does for
        state (1); the record's presence still ends the capture.

        Codex R5: the probe at (1) and the append at (2) are not one atomic
        step, so a SECOND worker can pass the probe while a first worker's row
        is still in flight. Both halves of the answer live here. The repair
        payload takes nothing from THIS worker (`repair_capture_operation`), so
        the racing appends are equivalent and the ledger no-ops the loser
        rather than conflicting. And the conflict that a genuinely divergent
        row still raises - the original torn attempt's own append landing in
        this window, carrying the dispatch metadata a repair cannot know - is
        CAUGHT and read as completion: the ledger only raises when an entry
        already occupies this exact `idempotency_key`, and that key names this
        one capture, so a conflict is positive evidence the row is durable.
        Failing the run over it would report a repair that in fact succeeded.

        Codex R6: that catch covers one ORDERING - the repair losing to the
        original append. The reverse, this repair's row landing FIRST and the
        original's own append then conflicting, raises inside `_capture` and is
        read as completion there, on the same evidence. The two catches are one
        symmetric answer; neither closes the race alone.
        """
        record = self._stored_run_record(context.run_id)
        if record is None:
            return
        # Ahead of the row probe: a non-run-start record is unrepairable
        # whatever the ledger says, and this spares it the whole-ledger read.
        if stored_capture_event_type(record.content) != RUN_START_EVENT_KIND:
            return
        if self._run_start_capture_row_present(record.envelope.memory_id):
            return
        try:
            result = self._recorder(
                # Both inert here - the repair writes no record, so nothing
                # consults the record scope, and its row is attributed to the
                # run-keyed repair actor rather than to this worker. Passed
                # anyway so the recorder is bound the same way on both capture
                # paths.
                actor=step_context.parent_actor,
                scope=context.record_scope,
                capture_mode=MemoryCaptureMode.SUMMARIZED,
            ).repair_capture_operation(
                event_kind=RUN_START_EVENT_KIND,
                record=record,
                timestamp=datetime.now(UTC),
                run_id=context.run_id,
            )
        except MemoryOperationIdempotencyConflictError:
            return
        _raise_capture_failure(result)

    def _stored_run_record(self, run_id: str) -> MemoryStoreRecord | None:
        """The stored run record, or `None` when it cannot be read.

        Identity comes from the STORED envelope and is never re-derived: a
        legacy record's `memory_id` need not equal what today's capture path
        would compute for the same `run_id`, and a repair row that referenced a
        re-derived id would point at a record that does not exist.

        An unreadable record (legacy shape, corrupt bytes) therefore has no
        recoverable identity and no row can honestly reference it, so the
        caller leaves the stored history exactly as it found it - which is the
        durable-presence guard's own posture, not a swallowed failure.

        The whole record is returned, not the envelope alone: the repair row's
        `cli_profile` / `engine_class` / `step_id` come from the stored CONTENT,
        which is where the torn capture recorded them, so the repair stays a
        pure function of what is durable (Codex R5).
        """
        try:
            return self._store.read_run_record(run_id)
        except (LookupError, ValueError):
            return None

    def _run_start_capture_row_present(self, memory_id: MemoryID) -> bool:
        """True when the run-start CAPTURE row for `memory_id` is already durable.

        Keyed on the run-start `action_id`, not on `memory_refs`: run-start and
        run-close write ONE shared EPISODIC_RUN `memory_id`, so a `memory_refs`
        match cannot tell the two capture events apart and a closed run would
        read as an uncaptured one.

        The whole-ledger read is the honest query an append-only C-MEM-08
        ledger offers, and it is reached ONLY once a record already exists - a
        fresh run never pays for it.
        """
        action_id = capture_operation_action_id(RUN_START_EVENT_KIND, memory_id)
        return any(
            entry.action_id == action_id and entry.operation_kind is MemoryOperationKind.CAPTURE
            for entry in self._store.read_memory_operations()
        )

    def _recorder(
        self,
        *,
        actor: object,
        scope: MemoryScope | None,
        capture_mode: MemoryCaptureMode,
    ) -> EpisodicMemoryCapture:
        """Bind a capture API to the run's COMPOSED record scope (`B-89`).

        `record_scope` is what the written records carry; `project` and
        `visibility` remain as the inputs to the residual construction the
        capture API falls back to when no composed scope exists (`scope is
        None`), so the no-scope caller is unchanged.
        """
        return EpisodicMemoryCapture(
            store=self._store,
            actor=cast("Any", actor),
            project=scope.project if scope is not None else self._project,
            visibility=scope.visibility if scope is not None else MemoryVisibility.PROJECT,
            capture_mode=capture_mode,
            tracer_provider=self._tracer_provider,
            record_scope=scope,
        )


def materialize_automatic_memory_runtime(
    config: RuntimeConfig,
    *,
    workload_class: WorkloadClass | None = None,
    tracer_provider: object | None = None,
) -> LocalAutomaticMemoryRuntime | None:
    """Materialize automatic memory when enabled in runtime config."""

    if not config.memory.enabled:
        return None
    return LocalAutomaticMemoryRuntime(
        config=config,
        workload_class=workload_class,
        tracer_provider=tracer_provider,
    )


def _policy_from_config(config: RuntimeConfig) -> MemoryPolicyDocument:
    memory = config.memory
    return MemoryPolicyDocument(
        policy_id=memory.policy_id,
        enabled=memory.enabled,
        capture_decision=(
            CaptureDecision.SUMMARIZE_ONLY
            if memory.capture_run_events or memory.capture_turns
            else CaptureDecision.DENY
        ),
        promotion_decision=PromotionDecision.PROPOSE_SEMANTIC,
        retrieval_access=AccessDecision.RETRIEVAL_ONLY,
        injection_access=(
            AccessDecision.PROMPT_PACKET if memory.prompt_packet_enabled else AccessDecision.DENY
        ),
        standard_tool_access=(
            AccessDecision.STANDARD_TOOLS if memory.standard_tools_enabled else AccessDecision.DENY
        ),
        native_memory_access=(
            AccessDecision.NATIVE_PROVIDER
            if memory.native_provider_enabled
            else AccessDecision.DENY
        ),
        review_mode=ReviewMode.AUTOMATIC,
        eligible_record_kinds=_retrievable_kinds(),
    )


def _retrievable_kinds() -> tuple[MemoryRecordKind, ...]:
    return (
        MemoryRecordKind.SEMANTIC_FACT,
        MemoryRecordKind.PREFERENCE,
        MemoryRecordKind.DECISION,
        MemoryRecordKind.CONVENTION,
        MemoryRecordKind.FAILURE_LEARNING,
        MemoryRecordKind.RESEARCH,
        MemoryRecordKind.PROCEDURAL_SNAPSHOT,
    )


def _run_id(step_context: StepExecutionContext) -> str:
    return step_context.parent_idempotency_key.replace("/", "_").replace("\\", "_")


def _turn_id(run_id: str, step_id: str, step_index: int) -> str:
    return f"turn:{run_id}:{step_id}:{step_index}"


def _query_summary(step_payload: Mapping[str, Any]) -> str:
    messages = step_payload.get("messages")
    if isinstance(messages, list) and messages:
        recent_messages = cast("list[object]", messages[-4:])
        return _compact_json(recent_messages)
    return _compact_json(step_payload)


def _payload_mapping(payload: ProviderAgnosticPayload) -> Mapping[str, Any]:
    return cast("Mapping[str, Any]", payload.model_dump(mode="json"))


def _response_summary(response: Mapping[str, Any]) -> str:
    choices = response.get("choices")
    if isinstance(choices, Sequence) and not isinstance(choices, str | bytes) and choices:
        choices_sequence = cast("Sequence[object]", choices)
        first = choices_sequence[0]
        if isinstance(first, Mapping):
            first_mapping = cast("Mapping[str, object]", first)
            message = first_mapping.get("message")
            if isinstance(message, Mapping):
                message_mapping = cast("Mapping[str, object]", message)
                content = message_mapping.get("content")
                if isinstance(content, str) and content:
                    return _compact_text(content)
                if content is not None:
                    return _compact_json(content)
                tool_calls = message_mapping.get("tool_calls")
                if tool_calls is not None:
                    return _compact_json(tool_calls)
    content = response.get("content")
    if isinstance(content, str) and content:
        return _compact_text(content)
    if isinstance(content, Sequence) and not isinstance(content, str | bytes):
        text_parts: list[str] = []
        content_sequence = cast("Sequence[object]", content)
        for item in content_sequence:
            if isinstance(item, Mapping):
                item_mapping = cast("Mapping[str, object]", item)
                text = item_mapping.get("text")
                if isinstance(text, str):
                    text_parts.append(text)
        if text_parts:
            return _compact_text("\n".join(text_parts))
    return _compact_json(response)


def _token_usage(
    *,
    input_tokens: int | None,
    output_tokens: int | None,
) -> dict[str, int] | None:
    usage: dict[str, int] = {}
    if input_tokens is not None:
        usage["input_tokens"] = int(input_tokens)
    if output_tokens is not None:
        usage["output_tokens"] = int(output_tokens)
    return usage or None


def _provider_route(fallback_chain: FallbackChain) -> tuple[str, ...]:
    candidates = (
        fallback_chain.primary,
        *fallback_chain.same_family,
        *fallback_chain.cross_family,
    )
    return tuple(f"{candidate.provider}:{candidate.model}" for candidate in candidates)


def _memory_engine_class(value: object) -> MemoryOperationEngineClass | None:
    if value is None:
        return None
    try:
        return MemoryOperationEngineClass(str(value))
    except ValueError:
        return None


def _capture_mode_from_decision(decision: CaptureDecision) -> MemoryCaptureMode | None:
    if decision is CaptureDecision.DENY:
        return None
    if decision is CaptureDecision.CAPTURE_FULL:
        return MemoryCaptureMode.FULL
    if decision is CaptureDecision.CAPTURE_REDACTED:
        return MemoryCaptureMode.REDACTED
    return MemoryCaptureMode.SUMMARIZED


def _raise_capture_failure(result: MemoryCaptureResult) -> None:
    if result.status is MemoryCaptureStatus.FAILED:
        raise RuntimeError(result.failure_reason or f"memory capture failed: {result.event_kind}")


def _compact_json(value: object) -> str:
    rendered = json.dumps(value, sort_keys=True, default=str, ensure_ascii=False)
    return _compact_text(rendered) or "dispatch"


def _compact_text(value: str) -> str:
    return value[:2000]


__all__ = [
    "AutoRefreshingDerivedRetrievalIndexStore",
    "AutomaticMemoryRuntime",
    "LocalAutomaticMemoryRuntime",
    "materialize_automatic_memory_runtime",
]
