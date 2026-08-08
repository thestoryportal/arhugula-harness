"""B-88 - the C-MEM-19 failure-class contract for the real memory exception families.

THIS TABLE IS THE CONTRACT. Every population that can reach one of the three
`classify_memory_failure` call sites has a row here, keyed on a REAL exception
instance carrying the message its raise site actually produces:

- `memory_tool_executor.StandardMemoryToolExecutor.execute` blanket `except`
  (`memory_tool_executor.py:167-175`) - the `MemoryToolExecution*` family plus
  whatever the store / retriever / policy layers raise unwrapped.
- `native_memory_adapter._emit_native_failure_span` (`:496`) - the callback
  contract's `MemoryPathViolationError` / `MemoryCallbackIOError` family.
- `memory_redaction` (`memory_redaction.py:260`) - the IS store `ValueError`
  family and raw `OSError`.

Before B-88 the classifier keyed on message substrings and on `"io"` appearing
anywhere in the lowercased type name. Since "execut-io-n" contains "io", the
ENTIRE `MemoryToolExecution*` family emitted `io_failure` unless an earlier
message rule happened to fire - so four genuine policy denials were reported
as IO failures, violating the C-MEM-19 Invariants distinguish rule ("Failure
telemetry must distinguish policy denial, path violation, IO failure,
serialization failure, provider adapter failure, and retrieval empty-result")
on an axis the vocabulary already has. That quotation is the invariant AS IT
STOOD THEN; Memory spec v1.3 (U-MEM-28) inserts `input validation failure` into
the same list, and the SEVEN `MemoryToolExecutionInputError` rows below carry it.
U-MEM-28 landed eight; `B-114` then re-keyed the `_prepare` exhaustiveness
fall-through's row onto `MemoryToolExecutionInternalError` (see that row).

Mutation probes for this table are recorded in the B-88 register row.
"""

from __future__ import annotations

import pytest
from harness_is.memory_observability import MemoryTelemetryFailureClass, classify_memory_failure
from harness_runtime.lifecycle.memory_tool_types import (
    MemoryCallbackIOError,
    MemoryPathViolationError,
)

# Module-private on purpose (a telemetry discriminator, not a public failure
# type); the table pins its classification directly, and the end-to-end span
# assertion lives at `test_native_memory_adapter.py`.
from harness_runtime.lifecycle.native_memory_adapter import _NativeMemoryPolicyDeniedError
from harness_runtime.memory_capture import (
    MemoryCaptureReservedActorError,
    MemoryCaptureScopeValueDomainError,
)
from harness_runtime.memory_tool_executor import (
    MemoryToolExecutionDeniedError,
    MemoryToolExecutionError,
    MemoryToolExecutionInputError,
    MemoryToolExecutionInternalError,
    MemoryToolExecutionLedgerConflictError,
    MemoryToolExecutionStoreError,
)

_POLICY_DENIAL = MemoryTelemetryFailureClass.POLICY_DENIAL
_PATH_VIOLATION = MemoryTelemetryFailureClass.PATH_VIOLATION
_IO_FAILURE = MemoryTelemetryFailureClass.IO_FAILURE
_PROVIDER_ADAPTER = MemoryTelemetryFailureClass.PROVIDER_ADAPTER_FAILURE
_INPUT_VALIDATION = MemoryTelemetryFailureClass.INPUT_VALIDATION_FAILURE


@pytest.mark.parametrize(
    ("exc", "expected"),
    [
        # --- MemoryToolExecutionDeniedError: policy_denial BY CONSTRUCTION ---
        # Every raise-site wording, including the four that emitted io_failure
        # before B-88 because they contain no policy/denied/unavailable word.
        (MemoryToolExecutionDeniedError("standard memory tools denied by policy"), _POLICY_DENIAL),
        (MemoryToolExecutionDeniedError("memory capture policy denies write_note"), _POLICY_DENIAL),
        (
            MemoryToolExecutionDeniedError("memory promotion policy discards candidates"),
            _POLICY_DENIAL,
        ),
        (MemoryToolExecutionDeniedError("memory ref mem-1 denied by policy"), _POLICY_DENIAL),
        (MemoryToolExecutionDeniedError("memory ref mem-1 is unavailable"), _POLICY_DENIAL),
        (
            MemoryToolExecutionDeniedError("memory tool policy_ref does not match context"),
            _POLICY_DENIAL,
        ),
        # WAS io_failure (B-88's named pair) - `memory_tool_executor.py:433/:435`.
        (MemoryToolExecutionDeniedError("memory ref mem-1 is superseded"), _POLICY_DENIAL),
        (MemoryToolExecutionDeniedError("memory ref mem-1 is not retrievable"), _POLICY_DENIAL),
        # WAS io_failure (two further misses found at this arc's grounding) -
        # `memory_tool_executor.py:308` and `:485`.
        (MemoryToolExecutionDeniedError("memory promotion review is forbidden"), _POLICY_DENIAL),
        (
            MemoryToolExecutionDeniedError("memory tool scope_ref does not match context"),
            _POLICY_DENIAL,
        ),
        # --- MemoryToolExecutionInternalError: the residual, by inheritance --
        # B-114. This row's raise site is `_prepare`'s executor-side
        # exhaustiveness fall-through (`memory_tool_executor.py`), a
        # HARNESS-INTERNAL fault that C-MEM-19 v1.3's type boundary forbids
        # raising as the input type. U-MEM-28 left it on the input type on
        # AUTHORITY grounds (the ratified A-ii site list named six sites, all in
        # `lifecycle/llm_dispatch.py`) and recorded the non-conformance; B-114
        # repaired it, and this row re-keyed with it - exactly as U-MEM-28's
        # own comment here said it would.
        #
        # The expected class is the RESIDUAL the family base declares, which
        # this type inherits rather than overriding: C-MEM-19 v1.3 states that a
        # harness-internal fault landing on `provider_adapter_failure` where an
        # implementation declares no dedicated unclassified value is conforming,
        # because such a report is the ABSENCE of a claim, not an assertion of
        # adapter-hood. What the contract forbids is the input-validation class,
        # which the site no longer carries.
        (MemoryToolExecutionInternalError("unsupported memory tool search"), _PROVIDER_ADAPTER),
        # --- MemoryToolExecutionInputError: input_validation_failure --------
        # U-MEM-28. These rows carried the LEAST-WRONG STOPGAP
        # `provider_adapter_failure` from the B-88 impl half (and io_failure
        # before it, except the policy_ref wording, which was policy_denial - a
        # malformed argument asserting a policy decision no resolver made),
        # because the C-MEM-19 vocabulary had no input-validation class. Memory
        # spec v1.3 adds `input_validation_failure` as the seventh member and
        # this type is the single declaration flip site, so exactly the eight
        # rows U-MEM-28 named moved and the other 31 did not. Seven of those
        # eight remain here; the eighth is the B-114 row above.
        (
            MemoryToolExecutionInputError("memory tool argument 'query' must be a string"),
            _INPUT_VALIDATION,
        ),
        (
            MemoryToolExecutionInputError("memory tool argument 'policy_ref' must be a string"),
            _INPUT_VALIDATION,
        ),
        (
            MemoryToolExecutionInputError("memory tool argument 'limit' must be >= 1"),
            _INPUT_VALIDATION,
        ),
        (MemoryToolExecutionInputError("allowed_kinds must be a sequence"), _INPUT_VALIDATION),
        (
            MemoryToolExecutionInputError(
                "unsupported allowed_kinds entry 'nope'; accepted kinds: episodic, semantic"
            ),
            _INPUT_VALIDATION,
        ),
        (MemoryToolExecutionInputError("invalid memory_ref mem-1"), _INPUT_VALIDATION),
        (
            MemoryToolExecutionInputError("unsupported promotion target_kind 'nope'"),
            _INPUT_VALIDATION,
        ),
        # --- MemoryToolExecutionStoreError: the durable-write failure -------
        # Round 2. `_write_note` raises this whenever the capture API returns
        # `status=FAILED`, which it does at exactly ONE place: the `except`
        # around `write_record` + `append_memory_operation`. Round 1's base
        # declaration alone would have reported a disk-full write as
        # `provider_adapter_failure` - a regression this arc introduced and
        # this row closes.
        (MemoryToolExecutionStoreError("OSError: disk full"), _IO_FAILURE),
        (
            MemoryToolExecutionStoreError("PermissionError: [Errno 13] Permission denied"),
            _IO_FAILURE,
        ),
        # WORDING-CONFLICTING row: `failure_reason` is `f"{type(exc).__name__}:
        # {exc}"`, so a store LookupError reads "... is unavailable" - which the
        # RESIDUAL would classify `policy_denial`. Deleting this type's
        # declaration therefore fails this row rather than passing green.
        (
            MemoryToolExecutionStoreError(
                "MemoryStoreRecordUnavailableError: record mem-1 is unavailable"
            ),
            _IO_FAILURE,
        ),
        # --- MemoryToolExecutionLedgerConflictError: the DETERMINISTIC half ---
        # `B-115` (b′). This population USED to sit on the store subtype above,
        # reported `io_failure`, and was recorded there as B-88's honest
        # residual: the capture layer labelled ANY raise from the durable-write
        # pair `io_failure`, so a non-IO exception escaping that pair was
        # reported as IO too, and the executor ADOPTED that rather than
        # inventing a contradicting third answer because the capture result
        # carried no exception to re-classify from.
        #
        # It carries one now. The refusal propagates out of `_capture` instead
        # of being folded into a `FAILED` result, so the executor can re-type
        # it - and this row moved with it. The class flips `io_failure` ->
        # `provider_adapter_failure` because the new type declares NOTHING and
        # inherits the base's RESIDUAL: a ledger refusal is not an I/O fault,
        # and per C-MEM-19 v1.3 a residual report is the ABSENCE of a claim
        # rather than a wrong one. This WITHDRAWS a false positive; it does not
        # withdraw an emission.
        #
        # It also makes the two consumers AGREE: `memory_redaction.py`'s
        # `classify_memory_failure` call site already reports the underlying
        # `MemoryOperationIdempotencyConflictError` as `provider_adapter_failure`
        # (pinned by the two-row discriminating witness at
        # `harness-is/tests/test_memory_redaction.py`). Before this row moved,
        # the same substrate event was reported two different ways depending on
        # which layer caught it.
        (
            MemoryToolExecutionLedgerConflictError(
                "MemoryOperationIdempotencyConflictError: idempotency_key 'k' already records "
                "a different operation"
            ),
            _PROVIDER_ADAPTER,
        ),
        # WORDING-CONFLICTING row for the new type, so its (absent) declaration
        # is not deletable-green: this message would trip the residual
        # message-rules toward `io_failure`, and only the type's inherited
        # residual keeps it on `provider_adapter_failure`.
        (
            MemoryToolExecutionLedgerConflictError(
                "MemoryOperationIdempotencyConflictError: durable write io error on append"
            ),
            _PROVIDER_ADAPTER,
        ),
        # --- MemoryToolExecutionError base: the residual --------------------
        # WAS io_failure before B-88. After round 2 the base's only raise site
        # is `_write_note`'s defensive `memory_id is None` branch (unreachable
        # through the real capture API), so the type determines nothing beyond
        # "not one of the five named substrate faults".
        (MemoryToolExecutionError("write_note capture failed"), _PROVIDER_ADAPTER),
        # WORDING-CONFLICTING row for the BASE declaration. Synthetic message
        # (the real defensive branch can only produce the string above), but
        # required: without a message whose residual differs, deleting the
        # base's declaration would leave the suite green. "denied by policy"
        # trips residual rule 1 -> policy_denial, so this row pins the base's
        # residual declaration as load-bearing.
        (MemoryToolExecutionError("write_note denied by policy"), _PROVIDER_ADAPTER),
        # --- native adapter / callback contract -----------------------------
        (
            MemoryPathViolationError("path '/memories/../x' contains path-traversal segment '..'"),
            _PATH_VIOLATION,
        ),
        (MemoryPathViolationError("path 'x' not prefixed with '/memories/'"), _PATH_VIOLATION),
        # WORDING-CONFLICTING row for the path declaration. Every CURRENT raise
        # site happens to say "path", so without a message that does not, the
        # declaration is deletable-green and only wording holds the class up -
        # exactly B-88's complaint. Synthetic but plausible as a future
        # rewording; the residual would return provider_adapter_failure here.
        (MemoryPathViolationError("'/memories/../x' escapes the memories scope"), _PATH_VIOLATION),
        # Genuine callback IO keeps io_failure - now by the type's own
        # declaration rather than by "io" appearing in its name.
        (MemoryCallbackIOError("view('/memories/x.txt') failed: not found"), _IO_FAILURE),
        (
            MemoryCallbackIOError("str_replace('/memories/x.txt'): substring 'a' not found"),
            _IO_FAILURE,
        ),
        (
            MemoryCallbackIOError("insert('/memories/x.txt', line=9): out of range (1..3)"),
            _IO_FAILURE,
        ),
        (
            MemoryCallbackIOError("memory record content_b64 failed to decode: bad padding"),
            _IO_FAILURE,
        ),
        # Policy denials routed through the callback contract's only failure
        # carrier - policy_denial by construction, not by wording.
        (
            _NativeMemoryPolicyDeniedError("native memory policy denies adapter access"),
            _POLICY_DENIAL,
        ),
        (
            _NativeMemoryPolicyDeniedError("capture policy denies native memory write"),
            _POLICY_DENIAL,
        ),
        (
            _NativeMemoryPolicyDeniedError("memory path '/memories/x.txt' is unavailable"),
            _POLICY_DENIAL,
        ),
        (
            _NativeMemoryPolicyDeniedError("retrieval policy denies memory path '/memories/x.txt'"),
            _POLICY_DENIAL,
        ),
        # --- capture write-boundary refusals (U-MEM-26) ---------------------
        # Both are caller CONTRACT violations, not substrate faults, and both
        # reach `classify_memory_failure` through
        # `StandardMemoryToolExecutor.execute`'s blanket `except`: the executor
        # binds a caller-supplied `context.actor` (reserved-actor refusal at
        # `EpisodicMemoryCapture.__init__`) and writes through the scope value
        # domain (`_scope_for_record`). Both messages are WORDING-CONFLICTING
        # by construction — neither trips a residual rule, so the residual
        # returns provider_adapter_failure and deleting either type's
        # `memory_failure_class` declaration fails its row rather than passing
        # green. Messages are the raise sites' real wording
        # (`memory_capture.py` `_RESERVED_REPAIR_ACTOR_PREFIX` refusal and
        # `memory_scope_family.scope_family_out_of_domain_message`).
        (
            MemoryCaptureReservedActorError(
                "actor_id 'memory-capture-repair:run-1' is inside the "
                "'memory-capture-repair:' namespace, which is reserved for torn-capture "
                "repair rows and may not be bound by an ordinary capture"
            ),
            _POLICY_DENIAL,
        ),
        (
            MemoryCaptureScopeValueDomainError(
                "memory scope provider_family 'not-a-family' is neither a ProviderFamily "
                "value nor a registered provider key (C-MEM-03 value domain)"
            ),
            _POLICY_DENIAL,
        ),
        # --- undeclared populations (the honest residual) -------------------
        (OSError("ledger offline"), _IO_FAILURE),
        (RuntimeError("some unmodelled failure"), _PROVIDER_ADAPTER),
    ],
)
def test_memory_failure_classification_table(
    exc: BaseException,
    expected: MemoryTelemetryFailureClass,
) -> None:
    assert classify_memory_failure(exc) is expected


def test_policy_denial_class_and_policy_decision_attribute_agree() -> None:
    """The two attributes on the executor's failure span must not disagree.

    `memory_tool_executor.py:170-172` already keys `memory.policy.decision` on
    `isinstance(exc, MemoryToolExecutionDeniedError)`. B-88's whole complaint
    is that `failure_class` on the very next line did not - so a "is
    superseded" denial emitted `policy.decision="denied"` alongside
    `failure_class="io_failure"`. Pin the agreement.
    """

    denials = [
        MemoryToolExecutionDeniedError("memory ref mem-1 is superseded"),
        MemoryToolExecutionDeniedError("memory ref mem-1 is not retrievable"),
        MemoryToolExecutionDeniedError("memory promotion review is forbidden"),
        MemoryToolExecutionDeniedError("memory tool scope_ref does not match context"),
    ]
    for exc in denials:
        assert isinstance(exc, MemoryToolExecutionDeniedError)
        assert classify_memory_failure(exc) is _POLICY_DENIAL


def test_policy_denied_callback_error_stays_a_callback_io_error() -> None:
    """The native adapter's private discriminator must not change any contract.

    It has to remain a `MemoryCallbackIOError` for `except` clauses, for
    `pytest.raises`, and for the C-RT-15 `RT-FAIL-MEMORY-CALLBACK-IO`
    (transient) fail-class mapping at §14.5.1.
    """

    exc = _NativeMemoryPolicyDeniedError("native memory policy denies adapter access")
    assert isinstance(exc, MemoryCallbackIOError)
    assert not isinstance(exc, MemoryPathViolationError)
