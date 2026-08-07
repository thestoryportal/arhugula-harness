"""B-88 - `classify_memory_failure` type-keyed classification (C-MEM-19 Invariants).

Two contracts live here, both IS-local:

1. The DECLARATION mechanism - an exception type that declares a
   `memory_failure_class` decides its own C-MEM-19 class, ahead of every
   message heuristic, and only a real vocabulary member counts.
2. The RESIDUAL heuristics - what an exception type that declares nothing
   still gets. The residual is deliberately weaker than it was: the
   `"io" in type-name` rule is gone (it matched "execut-io-n" /
   "operat-io-n" / "validat-io-n"), leaving `isinstance(exc, OSError)`.

The population table over the REAL memory-tool / native-adapter exception
families lives at `harness-runtime/tests/test_memory_failure_classification.py`
(those types are runtime-side and harness-is cannot import them).
"""

from __future__ import annotations

from typing import ClassVar

import pytest
from harness_is.memory_observability import (
    MEMORY_FAILURE_CLASS_ATTRIBUTE,
    MemoryTelemetryFailureClass,
    classify_memory_failure,
)
from harness_is.memory_operation_ledger import MemoryOperationIdempotencyConflictError
from harness_is.memory_store import MemoryStoreRecordUnavailableError


class _DeclaredDenialError(Exception):
    """Declares `policy_denial` while its message reads like an IO failure."""

    memory_failure_class: ClassVar[MemoryTelemetryFailureClass] = (
        MemoryTelemetryFailureClass.POLICY_DENIAL
    )


class _DeclaredSubclassError(_DeclaredDenialError):
    """Declares nothing of its own - inherits the parent's declaration."""


class _OverridingSubclassError(_DeclaredDenialError):
    """Overrides the inherited declaration."""

    memory_failure_class: ClassVar[MemoryTelemetryFailureClass] = (
        MemoryTelemetryFailureClass.SERIALIZATION_FAILURE
    )


class _BogusDeclarationError(Exception):
    """Declares a non-member value - must be ignored, not emitted.

    U-MEM-28 re-key. The literal used to be `"input_validation_failure"`, which
    was a genuine non-member when the C-MEM-19 vocabulary had six values. Memory
    spec v1.3 makes it a REAL member's value, so this fixture would have named a
    member while intending a non-member. It is re-keyed to a literal that is
    non-member on BOTH counts (not an enum member, not any member's value), and
    the type-gate half moved to `_NonMemberTypeDeclarationError` below.
    """

    memory_failure_class: ClassVar[str] = "definitely_not_a_failure_class"


class _NonMemberTypeDeclarationError(Exception):
    """Declares a REAL member's VALUE as a plain `str` - still must be ignored.

    U-MEM-28. `_declared_failure_class` gates on
    `isinstance(declared, MemoryTelemetryFailureClass)`, NOT on membership, so
    this fixture pins the TYPE gate independently of the vocabulary: a plain
    `str` that happens to equal a member's value is not an instance of the
    `StrEnum` subclass and is ignored. Without it the gate would be witnessed
    only by a literal that is non-member on both counts, and a membership check
    would satisfy the suite while the type check rotted.
    """

    memory_failure_class: ClassVar[str] = "input_validation_failure"


def test_declaration_attribute_name_is_the_documented_one() -> None:
    assert MEMORY_FAILURE_CLASS_ATTRIBUTE == "memory_failure_class"


@pytest.mark.parametrize(
    ("exc", "expected"),
    [
        # The declaration WINS over a message that the residual would classify
        # DIFFERENTLY: "path traversal" trips residual rule 2 (path_violation),
        # so this row fails if the declaration ever stops taking precedence.
        (
            _DeclaredDenialError("path traversal rejected for /memories/x.txt"),
            MemoryTelemetryFailureClass.POLICY_DENIAL,
        ),
        # ... and over a message that trips no heuristic at all (the residual
        # would return provider_adapter_failure here).
        (_DeclaredDenialError("is superseded"), MemoryTelemetryFailureClass.POLICY_DENIAL),
        # Inheritance: `getattr` walks the MRO, so a subclass is covered free.
        (_DeclaredSubclassError("anything"), MemoryTelemetryFailureClass.POLICY_DENIAL),
        # ... and an override wins over the inherited value.
        (
            _OverridingSubclassError("anything"),
            MemoryTelemetryFailureClass.SERIALIZATION_FAILURE,
        ),
        # (b1) A non-member declaration is ignored: the closed C-MEM-19
        # vocabulary cannot be widened by an attribute, so this falls to the
        # residual. The literal is non-member on BOTH counts - not an enum
        # member, and not any member's value.
        (
            _BogusDeclarationError("malformed argument"),
            MemoryTelemetryFailureClass.PROVIDER_ADAPTER_FAILURE,
        ),
        # (b2) U-MEM-28. The DISTINCT second gate: a plain `str` carrying a REAL
        # member's value is still ignored, because `_declared_failure_class`
        # tests `isinstance(..., MemoryTelemetryFailureClass)` and a `str` is not
        # an instance of the `StrEnum` subclass. b1 must NOT name a real member's
        # value and b2 MUST - one fixture cannot serve both gates.
        (
            _NonMemberTypeDeclarationError("malformed argument"),
            MemoryTelemetryFailureClass.PROVIDER_ADAPTER_FAILURE,
        ),
    ],
)
def test_declared_failure_class_is_the_authority(
    exc: BaseException,
    expected: MemoryTelemetryFailureClass,
) -> None:
    assert classify_memory_failure(exc) is expected


def test_instance_level_assignment_cannot_shadow_the_type_declaration() -> None:
    """codex R1 — only the exception HIERARCHY is the declaration authority.

    The attribute is read from ``type(exc)``: an instance-level assignment
    (or a raising instance property) must not override the class declaration,
    or classification would depend on per-object mutation rather than the
    type contract.
    """
    exc = _DeclaredDenialError("is superseded")
    exc.memory_failure_class = MemoryTelemetryFailureClass.IO_FAILURE  # type: ignore[misc]
    assert classify_memory_failure(exc) is MemoryTelemetryFailureClass.POLICY_DENIAL


@pytest.mark.parametrize(
    ("exc", "expected"),
    [
        # Rule 1 - policy wording, the residual's only denial key.
        (RuntimeError("denied by policy"), MemoryTelemetryFailureClass.POLICY_DENIAL),
        (RuntimeError("record is unavailable"), MemoryTelemetryFailureClass.POLICY_DENIAL),
        # Rule 2 - path wording.
        (RuntimeError("path traversal rejected"), MemoryTelemetryFailureClass.PATH_VIOLATION),
        # Rule 3 - genuine IO, now `isinstance(exc, OSError)` ONLY.
        (OSError("ledger offline"), MemoryTelemetryFailureClass.IO_FAILURE),
        (FileNotFoundError("no such file"), MemoryTelemetryFailureClass.IO_FAILURE),
        # Rule 4 - record codec faults.
        (
            UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte"),
            MemoryTelemetryFailureClass.SERIALIZATION_FAILURE,
        ),
        # Residual.
        (
            RuntimeError("something else entirely"),
            MemoryTelemetryFailureClass.PROVIDER_ADAPTER_FAILURE,
        ),
        # B-88 TRIPWIRE - the type name contains "operat-io-n" but the failure
        # is an idempotency conflict, not IO. Restoring the `"io" in exc_name`
        # rule turns this row `io_failure` and fails the suite.
        (
            MemoryOperationIdempotencyConflictError(
                "idempotency_key 'k' already records a different operation"
            ),
            MemoryTelemetryFailureClass.PROVIDER_ADAPTER_FAILURE,
        ),
        # Unchanged by B-88, pinned so the residual's reach is visible: an IS
        # store LookupError has no declaration and no keyword, so it lands in
        # the residual class both before and after.
        (
            MemoryStoreRecordUnavailableError("record mem-1 is tombstoned"),
            MemoryTelemetryFailureClass.PROVIDER_ADAPTER_FAILURE,
        ),
    ],
)
def test_residual_heuristics_for_undeclared_types(
    exc: BaseException,
    expected: MemoryTelemetryFailureClass,
) -> None:
    assert classify_memory_failure(exc) is expected


def test_c_mem_19_failure_vocabulary_is_exactly_the_seven_spec_values() -> None:
    """U-MEM-28 - the seventh member is ADDITIVE, and nothing else moved.

    `Spec_Memory_Substrate_v1.md` v1.3 C-MEM-19 Invariants: "Failure telemetry
    must distinguish policy denial, path violation, IO failure, serialization
    failure, provider adapter failure, input validation failure, and retrieval
    empty-result". Pinned as an ordered value tuple rather than a count, so a
    rename or a re-valuing of any of the pre-existing six fails here instead of
    passing a size check.
    """

    assert tuple(member.value for member in MemoryTelemetryFailureClass) == (
        "policy_denial",
        "path_violation",
        "io_failure",
        "serialization_failure",
        "provider_adapter_failure",
        "input_validation_failure",
        "retrieval_empty_result",
    )


def test_every_returned_class_is_a_closed_vocabulary_member() -> None:
    """The classifier is total into the closed seven-value C-MEM-19 vocabulary."""

    samples: list[BaseException] = [
        _DeclaredDenialError("x"),
        _BogusDeclarationError("x"),
        _NonMemberTypeDeclarationError("x"),
        OSError("x"),
        RuntimeError("x"),
        RuntimeError("denied"),
        RuntimeError("path"),
        RuntimeError("failed to decode"),
    ]
    assert all(classify_memory_failure(exc) in set(MemoryTelemetryFailureClass) for exc in samples)
