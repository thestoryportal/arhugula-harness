"""`B-115` (b′) — the DETERMINISM witnesses `Spec_Harness_Runtime_v1.md` §14.6.3
row 6 conditions the breaker-charge waiver on.

WHY THIS MODULE EXISTS, and why it lives at the LEDGER rather than at the
executor. §14.6.3 row 6 admits the `B-115` (b′) type to the waiver tuple *"only
after `B-115`'s build confirms determinism; if racy, this row is VOID and the
type reroutes to C5 retry-classification."* Neither §14.6.3 nor the council
record (`.harness/council/b116-breaker-semantics/DELIVERABLE.md`) DEFINES what
"confirms determinism" means — `REVIEW-e2.md` F-05 flagged exactly that
circularity. This leg supplies the definition, by analogy to the one witness
shape the council DID price (the raise-site partition witness + PD-8 + positive
controls):

* **W-D1 repeat-invariance** — the same conflicting append, repeated, returns
  the same outcome every time.
* **W-D2 candidate-independence** — an unrelated third candidate conflicts too,
  so the outcome is not a function of WHICH candidate is asking.
* **W-D3 state-driven-not-stochastic** (the honest boundary, asserted rather
  than hidden) — the conflict RESOLVES when the payload becomes equivalent
  again. A fault that never resolves is indistinguishable from one that is
  merely broken; a fault that resolves ONLY on an input change is what
  "deterministic over the same inputs" actually means.
* **W-D4 structural clock-exclusion** — the equivalence comparison reads no
  clock. Without this, a later field addition could reintroduce a time input
  and silently falsify W-D1 without failing any behavioural test.
* **W-D5 concurrency** (added at the #1274 merge gate) — N barrier-synchronized
  threads issuing the SAME append yield exactly one `APPENDED` and one durable
  line. W-D1..W-D4 are SEQUENTIAL and establish nothing about interleaving;
  this closes that gap in-tree. It is an invariant assertion, not a timing one:
  the append's read-compare-write runs inside the ledger's own locks, so the
  OUTCOME is serialized even though the SCHEDULING is not.

They are asserted against `append_memory_operation` DIRECTLY, not through the
memory tool executor, and that placement is load-bearing: determinism is a
property of the LEDGER's comparison, and it must stay witnessed there whatever
exception type the executor happens to wrap it in. These are therefore
green both before and after the (b′) split, and a future arc that re-types the
executor surface again cannot silently drop the evidence §14.6.3 cites.

`Spec_Harness_Runtime_v1.md` v1.113 §14.6.3 row 6; plan v2.61 U-RT-153.
"""

from __future__ import annotations

import inspect
import threading
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from harness_is.jsonl_event_ledger_lifecycle import JsonlLedgerHandle
from harness_is.memory_operation_ledger import (
    MemoryOperationEngineClass,
    MemoryOperationIdempotencyConflictError,
    MemoryOperationKind,
    MemoryOperationPayload,
    MemoryOperationProjection,
    MemoryOperationWriteResult,
    append_memory_operation,
)
from harness_is.memory_record_envelope import MemoryID
from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier

_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="agent-b115")
_BASE_TIME = datetime(2026, 8, 8, 12, 0, 0, tzinfo=UTC)

# The ONE key every payload below shares. The whole point of the cell-(3)
# mechanism is that the key is provider-BLIND while the 18-field equivalence
# payload is not, so a provider change lands on this key and diverges there.
_SHARED_KEY = "idempotent:capture:tool_event:b115"


def _handle(tmp_path: Path) -> JsonlLedgerHandle:
    return JsonlLedgerHandle(
        canonical_path=tmp_path / "memory" / "durable" / "memory_ops.jsonl",
        exists=False,
        entry_count=0,
    )


def _payload(
    *,
    provider: str | None,
    timestamp: datetime | None = None,
) -> MemoryOperationPayload:
    """A capture payload that varies ONLY in `provider` (and optionally the
    timestamp, which the equivalence payload excludes by construction)."""

    return MemoryOperationPayload(
        action_id=Identifier("capture:tool_event:b115"),
        idempotency_key=Identifier(_SHARED_KEY),
        actor=_ACTOR,
        timestamp=timestamp or _BASE_TIME,
        operation_kind=MemoryOperationKind.CAPTURE,
        operation_projection=MemoryOperationProjection.for_operation_kind(
            MemoryOperationKind.CAPTURE
        ),
        run_id="run-b115",
        step_id="step-b115",
        provider=provider,
        model="gpt-5",
        cli_profile="codex",
        engine_class=MemoryOperationEngineClass.PURE_PATTERN_NO_ENGINE,
        memory_refs=(MemoryID(f"mem:episodic:tool_event:{11:064x}"),),
        policy_ref="policy:b115",
        procedural_snapshot_ref="snapshot:b115",
    )


# --- W-D1 — repeat-invariance ---------------------------------------------


def test_w_d1_repeated_conflicting_append_is_repeat_invariant(tmp_path: Path) -> None:
    """W-D1: the SAME conflicting append, run 8 times against the same durable
    ledger, produces the SAME outcome every time — same exception type, same
    message, and no drift in the ledger it is comparing against.

    This is the first prong of "confirms determinism": the refusal is a pure
    function of (ledger contents, payload), so repeating it cannot change the
    answer. Eight rather than two because a single repeat cannot distinguish
    "invariant" from "happened to agree once".

    **Scope, stated so the witness is not read as more than it is.** These
    repeats are SEQUENTIAL and in ONE process, so they establish repeat-
    invariance and nothing about CONCURRENCY — they could not surface an
    interleaving race even if one existed, and an earlier revision of this
    docstring wrongly implied they could. The module's header block already
    scopes the four prongs to determinism-over-the-same-inputs. Concurrency is
    W-D5's job, added at the #1274 merge gate after that gate's concurrency lens
    verified the property out-of-band (barrier-synchronized threads and spawned
    processes, 0 anomalies over 50 trials).
    """

    handle = _handle(tmp_path)
    assert append_memory_operation(handle, _payload(provider="openai")) is (
        MemoryOperationWriteResult.APPENDED
    )

    outcomes: set[tuple[str, str]] = set()
    for _ in range(8):
        with pytest.raises(MemoryOperationIdempotencyConflictError) as excinfo:
            append_memory_operation(handle, _payload(provider="azure-openai"))
        outcomes.add((type(excinfo.value).__name__, str(excinfo.value)))

    assert len(outcomes) == 1, f"non-deterministic across repeats: {outcomes}"

    # The ledger did not grow: a REFUSED append writes nothing, so the state the
    # comparison reads is itself stable across the repeats. Without this the
    # single-outcome assertion above could hold for the wrong reason.
    assert len(handle.canonical_path.read_text().splitlines()) == 1


# --- W-D2 — candidate-independence ----------------------------------------


def test_w_d2_conflict_is_candidate_independent(tmp_path: Path) -> None:
    """W-D2: a THIRD, unrelated candidate conflicts on the same key too.

    The second prong. If the refusal were attributable to the `{provider,
    model}` the breaker is keyed to, a different candidate would be a different
    question; it is not — every candidate but the one that wrote the durable row
    meets the same refusal. That is what makes the fault harness-internal in
    §14.6.3's sense rather than provider-attested.
    """

    handle = _handle(tmp_path)
    append_memory_operation(handle, _payload(provider="openai"))

    for other in ("azure-openai", "ollama", "anthropic"):
        with pytest.raises(MemoryOperationIdempotencyConflictError):
            append_memory_operation(handle, _payload(provider=other))


# --- W-D3 — state-driven, not stochastic (the honest boundary) ------------


def test_w_d3_conflict_resolves_when_the_payload_becomes_equivalent(tmp_path: Path) -> None:
    """W-D3, and it is deliberately the awkward one: the refusal RESOLVES.

    Re-presenting the ORIGIN provider's payload returns `IDEMPOTENT_NOOP`, not a
    conflict. Stated plainly so the (b′) disposition is not read as claiming
    more than it has: the fault is NOT "permanent under all inputs" — it is
    deterministic over the SAME inputs, which is exactly the property §14.6.3's
    recovery-model test asks about (*could a half-open trial return a different
    result, ATTRIBUTABLY to the `{provider, model}`*). It could not: what
    changes the answer here is the payload, never the health of the candidate.

    The workspace already treats input variation as a separate dimension rather
    than as provider attribution — W-5's fifth dimension records that a
    re-sampled `idempotency_key` collapses cell (3) into cell (1)
    (`harness-runtime/tests/test_b84_validate_prepass.py`,
    `test_w5_case_3_collapses_into_case_1_when_the_idempotency_key_is_resampled`).
    This witness is the ledger-level statement of the same boundary.

    It doubles as the positive control for W-D1: a refusal that ALWAYS raised,
    including for the equivalent payload, would satisfy W-D1 vacuously.
    """

    handle = _handle(tmp_path)
    append_memory_operation(handle, _payload(provider="openai"))

    with pytest.raises(MemoryOperationIdempotencyConflictError):
        append_memory_operation(handle, _payload(provider="azure-openai"))

    # Back to the origin candidate — resolves, and resolves as a NOOP rather
    # than a second row, so the durable state is unchanged by the round trip.
    assert append_memory_operation(handle, _payload(provider="openai")) is (
        MemoryOperationWriteResult.IDEMPOTENT_NOOP
    )
    assert len(handle.canonical_path.read_text().splitlines()) == 1


# --- W-D4 — structural: the comparison reads no clock ---------------------


def test_w_d4_equivalence_comparison_excludes_the_timestamp(tmp_path: Path) -> None:
    """W-D4, behavioural half: a DIFFERENT timestamp with an otherwise identical
    payload is `IDEMPOTENT_NOOP`, not a conflict.

    The one wall-clock input in the payload cannot perturb the outcome, which is
    what lets W-D1 be a determinism claim rather than a fast-enough claim.
    """

    handle = _handle(tmp_path)
    append_memory_operation(handle, _payload(provider="openai"))

    later = _payload(provider="openai", timestamp=_BASE_TIME + timedelta(hours=9))
    assert append_memory_operation(handle, later) is MemoryOperationWriteResult.IDEMPOTENT_NOOP


def test_w_d4_equivalence_payload_field_set_is_pinned() -> None:
    """W-D4, structural half — the half a behavioural test cannot deliver.

    Pins the 18-field equivalence set BY NAME, so a later field addition that
    reintroduces a clock (or drops `provider`, which is what makes the cell-(3)
    mechanism exist at all) fails HERE rather than silently falsifying the
    determinism claim §14.6.3 row 6 rests on.

    Asserted by reading the two comparison functions' own source rather than by
    invoking them, because their return type is an untyped `dict[str, object]`
    whose keys are the contract: a value-level assertion would pass against a
    function that had quietly started reading `datetime.now()`.
    """

    from harness_is import memory_operation_ledger as ledger

    expected = {
        "action_id",
        "idempotency_key",
        "actor",
        "procedural_tier_snapshot_ref",
        "branch_metadata",
        "rotation_correlation_id",
        "operation_kind",
        "operation_projection",
        "run_id",
        "step_id",
        "provider",
        "model",
        "cli_profile",
        "engine_class",
        "memory_refs",
        "policy_ref",
        "procedural_snapshot_ref",
        "redaction_event",
    }
    assert len(expected) == 18

    entry_keys = set(ledger._equivalence_payload_from_entry(_entry(ledger)))
    payload_keys = set(ledger._equivalence_payload_from_payload(_payload(provider="openai")))

    assert entry_keys == expected
    assert payload_keys == expected
    # The two sides compare EQUAL only if they project the same field set.
    assert entry_keys == payload_keys

    for fn in (ledger._equivalence_payload_from_entry, ledger._equivalence_payload_from_payload):
        source = inspect.getsource(fn)
        assert "timestamp" not in source, f"{fn.__name__} reads a clock input"
        assert "now(" not in source, f"{fn.__name__} reads a clock input"
        assert "provider" in source, f"{fn.__name__} dropped the cell-(3) discriminator"


def _entry(ledger: object) -> object:
    """A ledger ENTRY built from the shared payload, for the field-set pin."""

    return ledger._entry_from_payload(  # type: ignore[attr-defined]
        _payload(provider="openai"),
        prior_entry=None,
    )


# --- W-D5 — the concurrency prong (added at the #1274 merge gate) ----------


def test_w_d5_concurrent_identical_appends_yield_exactly_one_row(tmp_path: Path) -> None:
    """W-D5: N barrier-synchronized threads issuing the SAME append produce
    exactly ONE `APPENDED`, N-1 `IDEMPOTENT_NOOP`, and ONE durable line.

    W-D1..W-D4 establish determinism over the same inputs, SEQUENTIALLY. They
    say nothing about interleaving, and the merge gate's concurrency lens
    verified that half out-of-band. This witness brings the cheap, deterministic
    part of it in-tree: `append_memory_operation` performs its read-compare-
    append inside a cross-process lock plus `_WRITE_LOCK`, so the whole
    critical section is serialized and the OUTCOME is not timing-dependent even
    though the SCHEDULING is. Whichever thread wins appends; every later one
    finds an equivalent entry and no-ops.

    That is why this is a legitimate permanent gate rather than a flaky one:
    the assertions are on the invariant (one row, one APPENDED), not on which
    thread got there first. Losing the lock would break it deterministically.
    """

    handle = _handle(tmp_path)
    workers = 8
    barrier = threading.Barrier(workers)
    outcomes: list[MemoryOperationWriteResult] = []
    errors: list[BaseException] = []
    lock = threading.Lock()

    def _append() -> None:
        try:
            barrier.wait(timeout=30)
            result = append_memory_operation(handle, _payload(provider="openai"))
        except BaseException as exc:
            with lock:
                errors.append(exc)
            return
        with lock:
            outcomes.append(result)

    threads = [threading.Thread(target=_append) for _ in range(workers)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=60)

    assert not errors, f"concurrent append raised: {errors!r}"
    assert len(outcomes) == workers
    assert outcomes.count(MemoryOperationWriteResult.APPENDED) == 1
    assert outcomes.count(MemoryOperationWriteResult.IDEMPOTENT_NOOP) == workers - 1
    assert len(handle.canonical_path.read_text().splitlines()) == 1
