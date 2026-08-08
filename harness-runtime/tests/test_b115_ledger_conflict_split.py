"""`B-115` (b′) — the deterministic ledger-conflict split, END-TO-END.

The determinism the §14.6.3 row-6 waiver rests on is witnessed one layer down,
at `harness-is/tests/test_b115_ledger_conflict_determinism.py` (W-D1..W-D4).
THIS module witnesses the split itself: that the refusal reaches the executor as
`MemoryToolExecutionLedgerConflictError` on all three surfaces it can surface
from, that the type-level partition against genuinely transient store I/O holds,
and that the retry/breaker disposition changed in exactly the intended way.

Unit U-RT-153; `Spec_Harness_Runtime_v1.md` v1.113 §14.6.3 row 6.
"""

from __future__ import annotations

import inspect
import json
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path

import pytest
from harness_as.memory_tool_contracts import MemoryToolName
from harness_core import DeploymentSurface
from harness_is import MemoryOperationIdempotencyConflictError
from harness_is.memory_observability import MemoryTelemetryFailureClass, classify_memory_failure
from harness_is.memory_path_registry import MemoryRootBinding
from harness_is.memory_policy import (
    AccessDecision,
    CaptureDecision,
    MemoryPolicyDocument,
    MemoryPolicyResolver,
    PromotionDecision,
    ReviewMode,
)
from harness_is.memory_record_envelope import MemoryScope, MemoryVisibility
from harness_is.memory_retrieval import MemoryRetriever
from harness_is.memory_retrieval_index import DerivedRetrievalIndexStore
from harness_is.memory_store import CanonicalMemoryStore
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_runtime.lifecycle.retry_breaker_fallback import (
    _BREAKER_CHARGE_WAIVED_TYPES,
    _classify_provider_exception,
    _is_breaker_charge_waived,
)
from harness_runtime.memory_capture import (
    EpisodicMemoryCapture,
    MemoryCaptureFailureKind,
    MemoryCaptureResult,
    MemoryCaptureStatus,
    SummaryProvenance,
    SummarySource,
)
from harness_runtime.memory_tool_executor import (
    MemoryToolExecutionContext,
    MemoryToolExecutionError,
    MemoryToolExecutionLedgerConflictError,
    MemoryToolExecutionRequest,
    MemoryToolExecutionStoreError,
    StandardMemoryToolExecutor,
)
from pydantic import ValidationError

_NOW = datetime(2026, 8, 8, 12, 0, 0, tzinfo=UTC)
_POLICY_REF = "policy:b115"
_SCOPE_REF = "scope:b115"
_NOTE = "A note replayed across fallback candidates."


def _scope() -> MemoryScope:
    return MemoryScope(
        project="arhugula-v2",
        workflow="memory-substrate",
        workload_class="coding-arc",
        provider_family="openai",
        cli_profile="codex",
        visibility=MemoryVisibility.WORKFLOW,
    )


def _context(*, provider: str, model: str = "gpt-5") -> MemoryToolExecutionContext:
    return MemoryToolExecutionContext(
        run_id="run-b115",
        workflow_id="memory-substrate",
        workload_class="coding-arc",
        step_id="step-b115",
        provider=provider,
        model=model,
        cli_profile="codex",
        scope=_scope(),
        scope_ref=_SCOPE_REF,
        policy_ref=_POLICY_REF,
        token_budget=120,
        timestamp=_NOW,
        actor=Actor(actor_class=ActorClass.AGENT, actor_id="agent-b115"),
    )


def executor_for(tmp_path: Path) -> tuple[CanonicalMemoryStore, StandardMemoryToolExecutor]:
    """A REAL executor over a real filesystem store.

    A fake store cannot witness any of this: the refusal under test is the
    canonical ledger's own, raised inside its cross-process critical section.
    """

    binding = MemoryRootBinding(default_root=tmp_path / "memory")
    surface = DeploymentSurface.LOCAL_DEVELOPMENT
    store = CanonicalMemoryStore(root_binding=binding, deployment_surface=surface)
    index_store = DerivedRetrievalIndexStore(root_binding=binding, deployment_surface=surface)
    index_store.rebuild(indexed_at=_NOW)
    resolver = MemoryPolicyResolver(
        MemoryPolicyDocument(
            policy_id=_POLICY_REF,
            enabled=True,
            capture_decision=CaptureDecision.CAPTURE_FULL,
            promotion_decision=PromotionDecision.PROPOSE_SEMANTIC,
            retrieval_access=AccessDecision.RETRIEVAL_ONLY,
            standard_tool_access=AccessDecision.STANDARD_TOOLS,
            review_mode=ReviewMode.OPERATOR_REQUIRED,
        )
    )
    return store, StandardMemoryToolExecutor(
        store=store,
        index_store=index_store,
        retriever=MemoryRetriever(
            store=store,
            index_store=index_store,
            policy_resolver=resolver,
            policy_ref=_POLICY_REF,
        ),
        policy_resolver=resolver,
    )


def request_for(
    tool: MemoryToolName,
    arguments: Mapping[str, object],
    *,
    provider: str,
) -> MemoryToolExecutionRequest:
    return MemoryToolExecutionRequest(
        tool_name=tool,
        arguments=dict(arguments),
        context=_context(provider=provider),
    )


def write_note(
    executor: StandardMemoryToolExecutor,
    *,
    provider: str,
    note: str = _NOTE,
) -> dict[str, object]:
    return executor.execute(
        request_for(
            MemoryToolName.WRITE_NOTE,
            {
                "note": note,
                "scope_ref": _SCOPE_REF,
                "policy_ref": _POLICY_REF,
                "idempotency_key": "note:b115",
            },
            provider=provider,
        )
    )


def search_args() -> dict[str, object]:
    return {"query": "note", "limit": 3, "scope_ref": _SCOPE_REF, "policy_ref": _POLICY_REF}


def redaction_args(memory_ref: str) -> dict[str, object]:
    return {
        "memory_ref": memory_ref,
        "reason": "operator request",
        "scope_ref": _SCOPE_REF,
        "policy_ref": _POLICY_REF,
    }


def tool_event_lines(tmp_path: Path, memory_ref: str) -> int:
    """Physical lines in the EPISODIC tool-events JSONL carrying `memory_ref`.

    Scoped to `episodic/**/tool_events.jsonl` deliberately: the ref also appears
    in the operation ledger and the derived index, and counting those would
    conflate the record-duplication question with the ledger's own idempotency
    answer, which these witnesses assert separately.
    """

    root = tmp_path / "memory" / "episodic"
    if not root.exists():
        return 0
    return sum(
        1
        for path in root.rglob("tool_events.jsonl")
        for line in path.read_text(encoding="utf-8").splitlines()
        if memory_ref in line
    )


# ---------------------------------------------------------------------------
# 1. The THREE executor surfaces, each EXECUTED.
#
# The register row enumerated ONE (`_write_note`). Grounding at this leg found
# three, and the two it missed escaped RAW - the ledger's own exception type
# reaching `_classify_provider_exception` with no memory-family wrapper at all,
# where the catch-all routed it to the staircase. Each surface below is
# witnessed rather than argued, because the row's own close_out requires it:
# "a code-read inference is not sufficient for this row".
# ---------------------------------------------------------------------------


def test_surface_1_capture_path_write_note(tmp_path: Path) -> None:
    """Surface 1 - `_write_note` -> `capture_tool_event`.

    The originally-registered one. Same text, same model NAME, different
    PROVIDER: `memory_id` collides (provider is not hashed into the content),
    the ledger's 18-field equivalence payload diverges on `provider`, and the
    executor re-types the result.

    This surface discriminates on a VALUE, not on a caught exception, and the
    distinction is the leg's one build-time correction. Propagating the ledger
    exception out of `_capture` was tried and FALSIFIED: `FAILED`-on-conflict is
    a CONTRACTED outcome for at least two of `_capture`'s six entry points
    (U-MEM-26 / Codex R6+R8 - see
    `test_u_mem_26_write_boundary.py::test_a_non_run_start_idempotency_conflict_still_fails_the_capture`,
    whose docstring says widening the catch would silently mask the divergence).
    So the capture layer reports `failure_kind` AND retains the exception on
    `failure_cause`, and the executor re-types `from` it — so this surface
    chains exactly like the two direct-append surfaces do.
    """

    _store, executor = executor_for(tmp_path)
    write_note(executor, provider="openai")

    with pytest.raises(MemoryToolExecutionLedgerConflictError) as excinfo:
        write_note(executor, provider="azure-openai")

    assert MemoryOperationIdempotencyConflictError.__name__ in str(excinfo.value), (
        "the re-type must carry the ledger's own exception name, not discard the provenance"
    )
    assert isinstance(excinfo.value.__cause__, MemoryOperationIdempotencyConflictError), (
        "the capture surface must CHAIN the ledger's own exception (AC #2), not "
        "reduce it to a message — an unchained re-type loses the refusal's traceback origin"
    )


def test_surface_1_discriminates_on_the_value_not_on_the_status(tmp_path: Path) -> None:
    """The capture layer's own half of surface 1, asserted directly.

    Without this, AC #2's end-to-end witness could pass against an executor that
    re-typed by inspecting `failure_reason` wording - exactly the message
    guessing `B-88` round 2 refused, and exactly what the new `failure_kind`
    enum exists to replace. The two failure kinds are asserted to be
    DISTINGUISHABLE at the capture boundary, independently of the executor.
    """

    store, _executor = executor_for(tmp_path)

    def _capture(provider: str) -> object:
        return EpisodicMemoryCapture(
            store=store,
            actor=Actor(actor_class=ActorClass.AGENT, actor_id="agent-b115"),
            project="arhugula-v2",
            visibility=MemoryVisibility.WORKFLOW,
            record_scope=_scope(),
        ).capture_tool_event(
            run_id="run-b115",
            tool_event_id="note:b115",
            tool_name=MemoryToolName.WRITE_NOTE.value,
            summary_text=_NOTE,
            summary=SummaryProvenance(source=SummarySource.MODEL_GENERATED, model="gpt-5"),
            step_id="step-b115",
            timestamp=_NOW,
            provider=provider,
            model="gpt-5",
            cli_profile="codex",
            engine_class=None,
            policy_ref=_POLICY_REF,
            procedural_snapshot_ref=None,
        )

    first = _capture("openai")
    second = _capture("azure-openai")

    # A CAPTURED result cannot carry a failure kind - illegal state, not policy.
    assert first.status is MemoryCaptureStatus.CAPTURED
    assert first.failure_kind is None
    assert first.failure_cause is None

    # Control flow is BYTE-UNCHANGED for every existing caller: still FAILED.
    assert second.status is MemoryCaptureStatus.FAILED
    # What is new is the discriminator, carried as a value...
    assert second.failure_kind is MemoryCaptureFailureKind.LEDGER_CONFLICT
    # ...and the ORIGINAL exception, retained so the executor can chain it.
    assert isinstance(second.failure_cause, MemoryOperationIdempotencyConflictError)
    # Provenance survives without the executor having to parse it.
    assert MemoryOperationIdempotencyConflictError.__name__ in (second.failure_reason or "")


def test_every_conflict_surface_chains_the_ledger_exception(tmp_path: Path) -> None:
    """The SYMMETRY claim, asserted once over all three surfaces together.

    Each surface witness above asserts its own chaining, but only a joint
    assertion catches the failure mode that actually occurred at this leg's
    first round: two surfaces chained and one did not, so the same substrate
    event lost its traceback origin depending on which surface caught it. A
    per-surface witness passes happily in that world.
    """

    causes: list[BaseException | None] = []

    store_a, exec_a = executor_for(tmp_path / "capture")
    write_note(exec_a, provider="openai")
    with pytest.raises(MemoryToolExecutionLedgerConflictError) as capture_exc:
        write_note(exec_a, provider="azure-openai")
    causes.append(capture_exc.value.__cause__)

    store_b, exec_b = executor_for(tmp_path / "tool-call")
    exec_b.execute(request_for(MemoryToolName.SEARCH, search_args(), provider="openai"))
    with pytest.raises(MemoryToolExecutionLedgerConflictError) as call_exc:
        exec_b.execute(request_for(MemoryToolName.SEARCH, search_args(), provider="ollama"))
    causes.append(call_exc.value.__cause__)

    store_c, exec_c = executor_for(tmp_path / "redaction")
    ref = str(write_note(exec_c, provider="openai")["memory_ref"])
    args = redaction_args(ref)
    exec_c.execute(request_for(MemoryToolName.REQUEST_REDACTION, args, provider="openai"))
    with pytest.raises(MemoryToolExecutionLedgerConflictError) as redact_exc:
        exec_c.execute(request_for(MemoryToolName.REQUEST_REDACTION, args, provider="ollama"))
    causes.append(redact_exc.value.__cause__)

    assert len(causes) == 3
    for cause in causes:
        assert isinstance(cause, MemoryOperationIdempotencyConflictError), (
            "every conflict surface must chain the ledger's own exception - "
            f"got {type(cause).__name__}"
        )


def test_the_result_model_forbids_a_kind_cause_mismatch() -> None:
    """The `failure_cause` invariant, asserted in BOTH directions.

    A `LEDGER_CONFLICT` without a cause is the dangerous half: the executor's
    `raise ... from result.failure_cause` would become `raise ... from None`,
    which SUPPRESSES the context rather than merely omitting it - actively
    hiding the origin. A cause on any other kind asserts a ledger refusal that
    did not happen.
    """

    with pytest.raises(ValidationError):
        MemoryCaptureResult(
            status=MemoryCaptureStatus.FAILED,
            event_kind="tool_event",
            failure_kind=MemoryCaptureFailureKind.LEDGER_CONFLICT,
            failure_cause=None,
        )

    with pytest.raises(ValidationError):
        MemoryCaptureResult(
            status=MemoryCaptureStatus.FAILED,
            event_kind="tool_event",
            failure_kind=MemoryCaptureFailureKind.STORE_IO,
            failure_cause=MemoryOperationIdempotencyConflictError("k"),
        )

    # And the legal pairing constructs cleanly.
    ok = MemoryCaptureResult(
        status=MemoryCaptureStatus.FAILED,
        event_kind="tool_event",
        failure_kind=MemoryCaptureFailureKind.LEDGER_CONFLICT,
        failure_cause=MemoryOperationIdempotencyConflictError("k"),
    )
    assert isinstance(ok.failure_cause, MemoryOperationIdempotencyConflictError)


def test_the_live_cause_field_does_not_break_the_models_serialization_contract() -> None:
    """`B-115` (b′) round 3 — the field is in-process ONLY, and BOTH Pydantic
    APIs it would otherwise break are asserted working.

    `MemoryCaptureResult` is PUBLICLY EXPORTED from `harness_runtime`, so
    `model_dump_json()` and `model_json_schema()` are part of its API contract.
    A live exception field regressed both from working to raising
    (`PydanticSerializationError` / `PydanticInvalidForJsonSchema`), and the
    schema break was at the CLASS level — it applied to every instance, not only
    conflicting ones, which is why the CAPTURED row below is not redundant.

    The regression is the workspace's serialization-boundary hazard class (the
    `B-101` / `B-107` lineage), so it is witnessed rather than assumed fixed.
    """

    captured = MemoryCaptureResult(status=MemoryCaptureStatus.CAPTURED, event_kind="tool_event")
    conflict = MemoryCaptureResult(
        status=MemoryCaptureStatus.FAILED,
        event_kind="tool_event",
        failure_reason="MemoryOperationIdempotencyConflictError: idempotency_key 'k' ...",
        failure_kind=MemoryCaptureFailureKind.LEDGER_CONFLICT,
        failure_cause=MemoryOperationIdempotencyConflictError("k"),
    )

    # Both instances serialize; the conflict one is the row that used to raise.
    assert json.loads(captured.model_dump_json())["status"] == "captured"
    payload = json.loads(conflict.model_dump_json())
    assert payload["status"] == "failed"
    assert payload["failure_kind"] == "ledger_conflict"

    # Schema generation works at the CLASS level, and the excluded field is
    # absent from it rather than emitted as an unrepresentable type.
    schema = MemoryCaptureResult.model_json_schema()
    assert "failure_cause" not in schema["properties"]

    # EXCLUSION IS NOT LOSS — the whole point. The live object is still there
    # for the chaining the executor performs; only the WIRE form omits it.
    assert isinstance(conflict.failure_cause, MemoryOperationIdempotencyConflictError)
    assert "failure_cause" not in conflict.model_dump()

    # And nothing was lost from the JSON projection either: `failure_reason`
    # already carries the serializable statement of the same fact, which is why
    # a second serialized copy would have been a drifting duplicate rather than
    # added information.
    assert MemoryOperationIdempotencyConflictError.__name__ in payload["failure_reason"]


def test_surface_2_standard_tool_call_append(tmp_path: Path) -> None:
    """Surface 2 - `_append_standard_tool_call`, the WIDEST of the three.

    It runs after EVERY successful standard tool call, so a READ-ONLY tool
    replayed with identical arguments from a different candidate reaches it
    with no `write_note` in the picture. `memory.search` is used rather than
    `memory.read` because it needs no retrievable index entry, which keeps the
    witness about the ledger rather than about retrieval policy.

    Before the split this surface raised the ledger type RAW - no memory-family
    wrapper - so it fell to `_classify_provider_exception`'s catch-all and
    travelled the staircase. That is asserted as closed below.
    """

    _store, executor = executor_for(tmp_path)
    executor.execute(request_for(MemoryToolName.SEARCH, search_args(), provider="openai"))

    with pytest.raises(MemoryToolExecutionLedgerConflictError) as excinfo:
        executor.execute(request_for(MemoryToolName.SEARCH, search_args(), provider="ollama"))

    assert isinstance(excinfo.value.__cause__, MemoryOperationIdempotencyConflictError)


def test_surface_3_request_redaction_append(tmp_path: Path) -> None:
    """Surface 3 - `_request_redaction`'s direct ledger append.

    Its `event_hash` covers tool_name / memory_ref / reason / policy_ref /
    run_id and NOT the provider, while the payload sets `provider`, so the
    identical redaction request from another candidate diverges. Also raised
    RAW before the split.
    """

    _store, executor = executor_for(tmp_path)
    memory_ref = str(write_note(executor, provider="openai")["memory_ref"])
    args = redaction_args(memory_ref)
    executor.execute(request_for(MemoryToolName.REQUEST_REDACTION, args, provider="openai"))

    with pytest.raises(MemoryToolExecutionLedgerConflictError) as excinfo:
        executor.execute(request_for(MemoryToolName.REQUEST_REDACTION, args, provider="ollama"))

    assert isinstance(excinfo.value.__cause__, MemoryOperationIdempotencyConflictError)


def test_no_executor_surface_leaks_the_raw_ledger_type(tmp_path: Path) -> None:
    """The partition's COMPLETENESS half, asserted structurally.

    Every `append_memory_operation` call the executor makes must route through
    `_append_operation_refusing_divergent_replay` (or, for the capture path,
    through `_capture_tool_event`). A fourth direct append added later would
    leak the raw ledger type back onto the staircase - silently, because no
    behavioural test would cover a surface that does not exist yet.

    Asserted over the module's SOURCE rather than by exercising every tool: the
    claim is about which call shape exists, which is exactly what source can
    answer and a behavioural sweep cannot.
    """

    from harness_runtime import memory_tool_executor as module

    source = inspect.getsource(module)
    direct = source.count("self._store.append_memory_operation(")
    assert direct == 1, (
        f"expected exactly ONE direct `self._store.append_memory_operation(` call "
        f"(inside `_append_operation_refusing_divergent_replay`), found {direct}. "
        "A new direct append must route through that helper or it will leak "
        "`MemoryOperationIdempotencyConflictError` raw onto the retry staircase."
    )
    helper = inspect.getsource(
        module.StandardMemoryToolExecutor._append_operation_refusing_divergent_replay
    )
    assert "MemoryOperationIdempotencyConflictError" in helper
    assert "MemoryToolExecutionLedgerConflictError" in helper


# ---------------------------------------------------------------------------
# 2. The TYPE-LEVEL raise-site partition witness (the U-RT-152 3/25 analogue).
# ---------------------------------------------------------------------------


def test_raise_site_partition_is_type_level_and_exhaustive() -> None:
    """The partition witness U-RT-152's 3/25 precedent makes owed here.

    U-RT-152 partitioned 28 payload-shape raise SITES 3 pre-flight / 25
    response-parsing, because the two populations shared one type. This
    partition is cleaner and the shape is different: it is TYPE-level. The
    ledger has exactly ONE raise site, and everything reaching the executor
    from it is deterministic; everything else the durable-write pair can raise
    is transient. So the partition to pin is not a site count but the
    DISPOSITION SPLIT across the two types, in BOTH directions - a one-sided
    assertion would pass against a wholesale reclassification of the family.

    HONESTLY SCOPED (survey of every non-test `append_memory_operation` caller,
    run at this leg):

    * `memory_tool_executor` - THREE surfaces, all covered above.
    * `memory_capture._capture` - covered via surface 1.
    * `memory_promotion`'s decision append - key is
      `idempotent:promotion:{kind}:{candidate_id}:{memory_id}`, provider-BLIND,
      while the payload sets `provider`: the SAME shape, and reachable from the
      executor's promotion tool. NOT re-typed at this leg (it is outside the
      three surfaces the ratified scope names) and recorded here rather than
      smuggled - it remains a raw-escape path.
    * `memory_context`'s injection append - key HASHES `selected_provider`, so
      a provider change yields a different key and no conflict. Not this shape.
    * `memory_retrieval`'s retrieval append - key hashes the `actor`, which
      discriminates in practice; measured at this leg across three providers
      with no conflict. Not this shape.
    * `memory_compaction_safety` - wraps its append in `except Exception ->
      CompactionDispositionWriteError`, so the ledger type never escapes raw.
      Not this shape.
    """

    conflict = MemoryToolExecutionLedgerConflictError("ledger refused a divergent replay")
    transient = MemoryToolExecutionStoreError("OSError: disk full")

    # Direction 1 - the deterministic half fail-fasts and is waived.
    assert _classify_provider_exception(conflict) is None
    assert _is_breaker_charge_waived(conflict) is True

    # Direction 2 - the transient half is UNMOVED. This is what makes the
    # change a split rather than a reclassification of the memory family.
    assert _classify_provider_exception(transient) is not None
    assert _is_breaker_charge_waived(transient) is False

    # Direction 3 - neither disposition arrived via the family base.
    assert _classify_provider_exception(MemoryToolExecutionError("base")) is not None
    assert _is_breaker_charge_waived(MemoryToolExecutionError("base")) is False
    assert not issubclass(MemoryToolExecutionLedgerConflictError, MemoryToolExecutionStoreError)
    assert not issubclass(MemoryToolExecutionStoreError, MemoryToolExecutionLedgerConflictError)

    # Direction 4 - guard and classifier agree on membership (§14.6.3's
    # classifier-consistency rule).
    assert MemoryToolExecutionLedgerConflictError in _BREAKER_CHARGE_WAIVED_TYPES
    assert MemoryToolExecutionStoreError not in _BREAKER_CHARGE_WAIVED_TYPES
    assert len(_BREAKER_CHARGE_WAIVED_TYPES) == 5


def test_the_new_type_inherits_the_c_mem_19_residual() -> None:
    """C-MEM-19: the new type declares NO class and inherits the base residual.

    Decided rather than defaulted. `io_failure` would be a positively WRONG
    claim about a ledger refusal; a dedicated `ledger_conflict` value would
    widen C-MEM-19's ratified vocabulary, which is an operator-gated Class 2
    decision an impl leg may not take (registered as forward row `B-134`). The
    residual is the honest third option: per C-MEM-19 v1.3 it is the ABSENCE of
    a claim, so this WITHDRAWS a false positive without asserting adapter-hood.
    """

    assert "memory_failure_class" not in vars(MemoryToolExecutionLedgerConflictError), (
        "the type must DECLARE nothing and inherit the base residual"
    )
    assert (
        classify_memory_failure(MemoryToolExecutionLedgerConflictError("x"))
        is MemoryTelemetryFailureClass.PROVIDER_ADAPTER_FAILURE
    )
    # The store subtype's own declaration is untouched.
    assert (
        classify_memory_failure(MemoryToolExecutionStoreError("OSError: disk full"))
        is MemoryTelemetryFailureClass.IO_FAILURE
    )


# ---------------------------------------------------------------------------
# 3. What the split actually BUYS - the duplicate-line amplification.
# ---------------------------------------------------------------------------


def test_fail_fast_stops_the_per_attempt_duplicate_record_line(tmp_path: Path) -> None:
    """The harm the staircase half caused, measured in durable bytes.

    `write_record` runs BEFORE the ledger append, so every attempt that reaches
    the capture appends a physical JSONL line and only THEN gets refused. Under
    the old `TRANSIENT_RETRY` classification the staircase re-ran the whole
    dispatch, so the line count grew once per attempt against a refusal that
    could never clear.

    This witness measures the mechanism directly rather than through a
    dispatcher: N conflicting attempts append N lines. The split does not stop
    an INDIVIDUAL attempt from appending (that is the separate, still-open
    duplicate-record half, and W-5 cell (3)'s preserved `== 2` assertion says
    so) - what it stops is the RETRY that turns one duplicate into
    `max_attempts` duplicates, by removing this class from the staircase.
    """

    _store, executor = executor_for(tmp_path)
    first = str(write_note(executor, provider="openai")["memory_ref"])
    assert tool_event_lines(tmp_path, first) == 1

    for _ in range(4):
        with pytest.raises(MemoryToolExecutionLedgerConflictError):
            write_note(executor, provider="azure-openai")

    assert tool_event_lines(tmp_path, first) == 5, (
        "each conflicting attempt appends a line before the ledger refuses - "
        "which is exactly why the class must not re-enter the retry staircase"
    )
    # And the refusal is REPEAT-INVARIANT end-to-end, not just at the ledger:
    # the four attempts above all raised the same type.
    assert _classify_provider_exception(MemoryToolExecutionLedgerConflictError("x")) is None


def test_returning_to_the_origin_candidate_still_succeeds(tmp_path: Path) -> None:
    """W-D3's end-to-end mirror, and the honest boundary restated at the
    executor: the refusal is deterministic over the SAME inputs, not permanent
    under all inputs. Re-presenting the ORIGIN candidate's payload succeeds.

    Stated here so the (b′) disposition is not read as claiming the fault is
    unrecoverable. What §14.6.3's recovery-model test asks is whether a
    half-open trial could differ ATTRIBUTABLY to the `{provider, model}` the
    breaker is keyed to; it could not - what changes the answer is the payload.
    """

    _store, executor = executor_for(tmp_path)
    first = str(write_note(executor, provider="openai")["memory_ref"])

    with pytest.raises(MemoryToolExecutionLedgerConflictError):
        write_note(executor, provider="azure-openai")

    replay = write_note(executor, provider="openai")
    assert str(replay["memory_ref"]) == first
