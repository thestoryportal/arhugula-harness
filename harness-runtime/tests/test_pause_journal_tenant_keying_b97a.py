"""`B-97` half (a) — per-tenant pause-journal path segregation (U-RT-149).

Runtime spec v1.108 §14.14.8 (tenant-composite keying + the TOTAL injective
constant encoding + the (3a) abandon disposition + the orphan statement) +
§14.14.9.1 (parallel keying on the accessor) + §30 (the tenant-scoped `absent`
and the `B-102` reachability qualification). Plan `Implementation_Plan_Harness_Runtime_v2_56.md`
U-RT-149 AC #1-#6, #8, #12.

**Witness shape.** Every assertion here is BY EXECUTION. The arc's central
claim — *a wrong-tenant read resolves the caller's OWN path and truthfully finds
nothing, rather than opening another tenant's file* — is precisely the kind a
presence check cannot test.

**PD-8 mutation probes are FIRST-CLASS here** (`test_mutation_probe_*`), not
commentary: green-alone is not proof a guard is load-bearing. Each probe reverts
the guard in-process, asserts the corresponding witness FAILS, and restores.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
from harness_cp.handoff_context import StateSummary
from harness_cp.pause_resume_protocol_types import PauseSnapshot, WorkflowPauseReason
from harness_is.state_ledger_entry_schema import Identifier
from harness_runtime.lifecycle import journal_workflow_pause_store as store_module
from harness_runtime.lifecycle.journal_workflow_pause_store import (
    JournalWorkflowPauseStore,
    PauseJournalReadCause,
    encode_pause_journal_key,
    legacy_pause_journal_filename,
    pause_journal_filename,
)

_WORKFLOW_ID = "wf-b97a"
_TENANT_A = "tenant-a"
_TENANT_B = "tenant-b"


def _snapshot(workflow_id: str = _WORKFLOW_ID, *, run_id: str = "run-1") -> PauseSnapshot:
    return PauseSnapshot(
        workflow_id=workflow_id,
        run_id=run_id,
        step_index=0,
        pause_reason=WorkflowPauseReason.HITL_PENDING,
        state_summary=StateSummary(
            relevant_entries=(),
            summary_text="",
            summary_hash="0" * 64,
            idempotency_key=Identifier(""),
            external_references=(),
        ),
        snapshot_hash="0" * 64,
        created_at=0,
        state_ledger_anchor="0" * 64,
    )


# ---------------------------------------------------------------------------
# AC #1 — the per-tenant stream, run BOTH ways. THE LOAD-BEARING WITNESS.
# ---------------------------------------------------------------------------


def test_ac1a_two_os_processes_differently_tenanted_keep_their_own_streams(
    tmp_path: Path,
) -> None:
    """AC #1(a) — TWO OS PROCESSES, one journal dir, SAME `workflow_id`.

    Genuinely separate interpreters (`subprocess`, never `multiprocessing` — the
    fork-after-lock hazard), each capturing under its own tenant scope, and each
    reading back ITS OWN snapshot. **This is the witness that would have FAILED
    under the non-segregated readings**: before v1.108 both processes addressed
    `sha256(workflow_id)` and the second capture's record became the first's
    latest, so tenant A's read returned tenant B's snapshot.
    """
    journal_dir = tmp_path / "pause-journal"
    script = """
import sys
from pathlib import Path
from harness_cp.handoff_context import StateSummary
from harness_cp.pause_resume_protocol_types import PauseSnapshot, WorkflowPauseReason
from harness_is.state_ledger_entry_schema import Identifier
from harness_runtime.lifecycle.journal_workflow_pause_store import JournalWorkflowPauseStore

journal_dir, tenant, run_id, workflow_id = sys.argv[1:5]
snap = PauseSnapshot(
    workflow_id=workflow_id, run_id=run_id, step_index=0,
    pause_reason=WorkflowPauseReason.HITL_PENDING,
    state_summary=StateSummary(
        relevant_entries=(), summary_text="", summary_hash="0" * 64,
        idempotency_key=Identifier(""), external_references=(),
    ),
    snapshot_hash="0" * 64, created_at=0, state_ledger_anchor="0" * 64,
)
store = JournalWorkflowPauseStore(journal_dir=Path(journal_dir), tenant_id=tenant)
store.capture(snap)
read_back = store.read_latest(workflow_id)
assert read_back is not None, "own capture unreadable"
assert read_back.run_id == run_id, (
    "CROSS-TENANT LEAK: read back %r under tenant %r" % (read_back.run_id, tenant)
)
"""
    for tenant, run_id in ((_TENANT_A, "run-a"), (_TENANT_B, "run-b")):
        completed = subprocess.run(
            [sys.executable, "-c", script, str(journal_dir), tenant, run_id, _WORKFLOW_ID],
            capture_output=True,
            check=False,
        )
        assert completed.returncode == 0, completed.stderr.decode()

    # And from a THIRD process's perspective: both records survive, at two paths.
    assert (journal_dir / pause_journal_filename(_TENANT_A, _WORKFLOW_ID)).is_file()
    assert (journal_dir / pause_journal_filename(_TENANT_B, _WORKFLOW_ID)).is_file()
    a = JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=_TENANT_A)
    b = JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=_TENANT_B)
    a_read = a.read_latest(_WORKFLOW_ID)
    b_read = b.read_latest(_WORKFLOW_ID)
    assert a_read is not None and a_read.run_id == "run-a"
    assert b_read is not None and b_read.run_id == "run-b"


def test_ac1b_two_sequential_stores_in_one_process_keep_their_own_streams(
    tmp_path: Path,
) -> None:
    """AC #1(b) — TWO SEQUENTIAL stores in ONE process, different `tenant_id`.

    The single-process reachability route the fork established: it needs no
    multi-deployment topology, and it is the shape an operator reaches
    ACCIDENTALLY (two `run()` calls with different `config.tenant_id` against one
    resolved directory). A green (a) alone does not discharge AC #1.
    """
    journal_dir = tmp_path / "pause-journal"
    a = JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=_TENANT_A)
    b = JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=_TENANT_B)

    a.capture(_snapshot(run_id="run-a"))
    b.capture(_snapshot(run_id="run-b"))

    a_read = a.read_latest(_WORKFLOW_ID)
    b_read = b.read_latest(_WORKFLOW_ID)
    assert a_read is not None and a_read.run_id == "run-a"
    assert b_read is not None and b_read.run_id == "run-b"


def test_ac1_wrong_tenant_read_resolves_its_own_path_and_finds_nothing(
    tmp_path: Path,
) -> None:
    """The arc's central claim, asserted directly.

    A wrong-tenant lookup resolves the caller's OWN path and returns the ordinary
    `absent` — *and under a segregated address space that is the TRUTH, not a
    misleading diagnosis*. The other tenant's file is never opened; there is
    nothing to refuse.
    """
    journal_dir = tmp_path / "pause-journal"
    JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=_TENANT_A).capture(_snapshot())

    result = JournalWorkflowPauseStore(
        journal_dir=journal_dir, tenant_id=_TENANT_B
    ).read_latest_attributed(_WORKFLOW_ID)

    assert result.snapshot is None
    assert result.cause is PauseJournalReadCause.ABSENT
    assert result.record_count == 0


# ---------------------------------------------------------------------------
# AC #2 — injectivity, over ALL THREE hazards + the no-configuration assertion.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("left", "right"),
    [
        # The recorded field-boundary pair: `tenant + "\0" + workflow_id` maps
        # both of these to identical preimage bytes.
        (("a", "b\0c"), ("a\0b", "c")),
        # A length-varying family around it — a naive delimiter concatenation
        # fails EVERY row here, which is exactly why the family exists.
        (("ab", "cd"), ("a", "bcd")),
        (("", "abc"), ("a", "bc")),
        (("abc", ""), ("ab", "c")),
        (("x" * 3, "y" * 5), ("x" * 5, "y" * 3)),
    ],
)
def test_ac2a_field_boundary_shift_is_injective(
    left: tuple[str, str], right: tuple[str, str]
) -> None:
    """AC #2(a) — FIELD-BOUNDARY SHIFT, plus a length-varying family."""
    assert encode_pause_journal_key(*left) != encode_pause_journal_key(*right)
    assert pause_journal_filename(*left) != pause_journal_filename(*right)


@pytest.mark.parametrize(
    "tenant",
    [
        "a",
        "_single",  # what a reserved-literal scheme would have had to reserve
        "_untenanted",  # the sibling store's own recorded sentinel defect
        "u",  # the sibling's untenanted marker character
        "none",
        "None",
        "",
    ],
)
def test_ac2b_untenanted_branch_never_collides_with_any_real_scope(tenant: str) -> None:
    """AC #2(b) — BRANCH COLLISION: the untenanted `None` scope against EVERY
    real tenant scope, *including any string a reserved-literal scheme would have
    had to reserve*.

    Closed by SEGMENT COUNT alone — the untenanted branch is the ONE-segment form
    and a real scope the TWO-segment form — so **no literal needs reserving at
    all**. `normalize_tenant_scope` is bypassed here deliberately: the encoding's
    totality must hold over the raw domain, not only over what the validator
    admits.
    """
    assert encode_pause_journal_key(None, "wf") != encode_pause_journal_key(tenant, "wf")
    assert pause_journal_filename(None, "wf") != pause_journal_filename(tenant, "wf")


@pytest.mark.parametrize("hostile", ["|", ":", "5:x", "a|b", "3:a|3:b", "\0", "\n"])
def test_ac2c_delimiter_collision_in_either_position(hostile: str) -> None:
    """AC #2(c) — DELIMITER COLLISION: a tenant scope, AND a `workflow_id`, each
    containing whatever character the composition uses.

    Length prefixes mean the delimiter is never SEARCHED for, only counted past.
    Delimiter REJECTION is explicitly NOT the answer — it would narrow a public
    input contract, which this arc may not do — so these values stay VALID and
    must merely be distinguishable.
    """
    assert encode_pause_journal_key(hostile, "wf") != encode_pause_journal_key("wf", hostile)
    assert encode_pause_journal_key(hostile, "wf") != encode_pause_journal_key(None, hostile + "wf")
    assert pause_journal_filename(hostile, "wf") != pause_journal_filename("t", hostile)


@pytest.mark.parametrize(
    "identifier",
    [
        "é",  # the non-ASCII case the two in-house length-prefix forms disagree on
        "日本語",
        "\ud800",  # a LONE SURROGATE — strict UTF-8 REFUSES this
        "a\ud800b",
        "🙂",
    ],
)
def test_ac2_encoding_is_total_over_non_ascii_and_lone_surrogates(identifier: str) -> None:
    """The encoding is TOTAL over the full `(str | None) × str` domain.

    `RuntimeConfig.tenant_id` and `workflow_id` are plain `str` fields that accept
    a LONE SURROGATE, which STRICT UTF-8 encoding REFUSES — a strict encoder would
    make the encoding PARTIAL over its own declared domain and turn a config-valid
    deployment's capture into a CRASH. The `surrogatepass` handler is therefore
    part of the PINNED GRAMMAR, not an implementation detail.
    """
    assert pause_journal_filename(identifier, "wf")
    assert pause_journal_filename("t", identifier)
    assert pause_journal_filename(None, identifier)


def test_ac2_grammar_is_pinned_to_the_utf8_byte_count_form() -> None:
    """The BYTE GRAMMAR is a CONTRACT TERM, and *"the in-house length-prefixed
    shape" is NOT one shape*.

    The codebase ships TWO mutually incompatible length-prefix precedents — OD's
    canonical signing message prefixes each segment with its CHARACTER count,
    while OD's cutover-record message prefixes with its UTF-8 BYTE count. Both
    are injective, and **they emit different bytes for any non-ASCII
    identifier**. For a durable address space the consequence is not a collision
    but something equally bad: two conformant implementations addressing the same
    journal at two different paths with no migration between them. v1.108 pins
    the BYTE-count variant; this asserts the shipped bytes are that one.
    """
    assert encode_pause_journal_key(None, "é") == b"2:\xc3\xa9"
    assert encode_pause_journal_key("t", "é") == b"1:t|2:\xc3\xa9"
    # The character-count variant would have emitted `1:` for "é" — pinned out.
    assert encode_pause_journal_key(None, "é") != b"1:\xc3\xa9"
    # `surrogatepass`, byte-counted.
    assert encode_pause_journal_key(None, "\ud800") == b"3:\xed\xa0\x80"


def test_ac2_derivation_reads_no_configuration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC #2 — **the derivation reads NO configuration.**

    No `RuntimeConfig` field, no env var, no file, so *a future knob cannot be
    added without failing a test*. A configurable key derivation would be a
    SECOND AUTHORITY over one durable address space: flipping it re-addresses
    every `(tenant, workflow_id)` pair, orphaning every journal silently with no
    migration and no diagnostic.

    Witnessed by EXECUTION, not by reading the source: every `os.environ` read
    and every filesystem open is intercepted for the duration of a derivation.
    """
    import builtins
    import os

    env_reads: list[str] = []
    opens: list[str] = []
    real_open = builtins.open
    real_getenv = os.getenv

    class _SpyEnviron(dict[str, str]):
        def __getitem__(self, key: str) -> str:
            env_reads.append(key)
            return super().__getitem__(key)

        def get(self, key: str, default: object = None) -> object:  # type: ignore[override]
            env_reads.append(key)
            return super().get(key, default)  # type: ignore[arg-type]

    def _spy_getenv(key: str, default: object = None) -> object:
        env_reads.append(key)
        return real_getenv(key, default)  # type: ignore[arg-type]

    def _spy_open(file: object, *args: object, **kwargs: object) -> object:
        opens.append(str(file))
        return real_open(file, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(os, "environ", _SpyEnviron(os.environ))
    monkeypatch.setattr(os, "getenv", _spy_getenv)
    monkeypatch.setattr(builtins, "open", _spy_open)

    pause_journal_filename(_TENANT_A, _WORKFLOW_ID)
    encode_pause_journal_key(None, _WORKFLOW_ID)

    assert env_reads == [], f"the derivation read configuration from env: {env_reads}"
    assert opens == [], f"the derivation opened a file: {opens}"


# ---------------------------------------------------------------------------
# AC #3 — the untenanted default's path CHANGES, and that is the RATIFIED COST.
# ---------------------------------------------------------------------------


def test_ac3_untenanted_default_resolves_to_a_different_path_than_the_legacy_key() -> None:
    """AC #3 — the single-tenant local default (`tenant_id=None`) resolves to a
    DIFFERENT path than the pre-v1.108 `sha256(workflow_id)`.

    **This is not a defect to be softened — it is the (3a) abandonment.** A
    witness that asserts it prevents a later session "fixing" it with the
    fallback read the spec forbids.
    """
    legacy = legacy_pause_journal_filename(_WORKFLOW_ID)
    current = pause_journal_filename(None, _WORKFLOW_ID)
    assert legacy != current
    assert legacy == f"{hashlib.sha256(_WORKFLOW_ID.encode()).hexdigest()}.jsonl"


def test_ac3_a_pre_existing_legacy_journal_is_not_read_and_there_is_no_fallback(
    tmp_path: Path,
) -> None:
    """AC #3 — a pre-existing legacy journal is therefore NOT READ, and **no code
    path consults the legacy key.**

    Asserted by EXECUTION plus an open-spy: the store is given a directory whose
    ONLY journal is the legacy one, and the read must both return `absent` AND
    never have opened that file. A fallback would create a second read authority
    over one key and fail open at exactly the boundary being built.
    """
    journal_dir = tmp_path / "pause-journal"
    journal_dir.mkdir(parents=True)
    legacy = journal_dir / legacy_pause_journal_filename(_WORKFLOW_ID)
    legacy.write_text(
        json.dumps(
            {
                "workflow_id": _WORKFLOW_ID,
                "pause_snapshot": _snapshot().model_dump(mode="json"),
            }
        )
        + "\n"
    )

    opened: list[str] = []
    real_read_text = Path.read_text

    def _spy_read_text(self: Path, *args: object, **kwargs: object) -> str:
        opened.append(str(self))
        return real_read_text(self, *args, **kwargs)  # type: ignore[arg-type]

    store = JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=None)
    monkey = pytest.MonkeyPatch()
    try:
        monkey.setattr(Path, "read_text", _spy_read_text)
        result = store.read_latest_attributed(_WORKFLOW_ID)
    finally:
        monkey.undo()

    assert result.snapshot is None
    assert result.cause is PauseJournalReadCause.ABSENT
    assert str(legacy) not in opened, "the read consulted the LEGACY key — no fallback is permitted"


# ---------------------------------------------------------------------------
# AC #4 — the amended `absent`, the closed vocabulary, and the `B-102` flip.
# ---------------------------------------------------------------------------


def test_ac4a_wrong_tenant_and_legacy_only_both_report_the_ordinary_absent(
    tmp_path: Path,
) -> None:
    """AC #4(a) — a wrong-tenant lookup AND a legacy-only journal each report the
    ORDINARY `absent` — not a new cause, not an error.

    Both are among §30's THREE underlying states that deliberately share this
    cause. A discriminator here would be the existence oracle path segregation
    removes.
    """
    journal_dir = tmp_path / "pause-journal"
    JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=_TENANT_A).capture(_snapshot())
    (journal_dir / legacy_pause_journal_filename("wf-legacy-only")).write_text(
        json.dumps(
            {
                "workflow_id": "wf-legacy-only",
                "pause_snapshot": _snapshot("wf-legacy-only").model_dump(mode="json"),
            }
        )
        + "\n"
    )

    wrong_tenant = JournalWorkflowPauseStore(
        journal_dir=journal_dir, tenant_id=_TENANT_B
    ).read_latest_attributed(_WORKFLOW_ID)
    legacy_only = JournalWorkflowPauseStore(
        journal_dir=journal_dir, tenant_id=None
    ).read_latest_attributed("wf-legacy-only")

    assert wrong_tenant.cause is PauseJournalReadCause.ABSENT
    assert legacy_only.cause is PauseJournalReadCause.ABSENT
    # A NEVER-JOURNALED workflow is INDISTINGUISHABLE from both — same cause,
    # same fields. (AC #5's no-oracle property, asserted on the field level.)
    never = JournalWorkflowPauseStore(
        journal_dir=journal_dir, tenant_id=None
    ).read_latest_attributed("wf-never-existed")
    assert never == legacy_only._replace() == wrong_tenant._replace()


def test_ac4b_the_cause_vocabulary_is_still_exactly_five() -> None:
    """AC #4(b) — asserted PROGRAMMATICALLY over the shipped enum, not eyeballed."""
    members = {member.value for member in PauseJournalReadCause}
    assert members == {
        "absent",
        "empty-journal",
        "read-error",
        "corrupt-latest",
        "workflow-mismatch",
    }
    assert len(PauseJournalReadCause) == 5


def test_ac4c_absent_now_carries_the_indeterminate_disposition(tmp_path: Path) -> None:
    """AC #4(c) — `B-102`'s impl half for `absent`.

    A `capture()` dispatched but not yet having created its journal file reports
    `absent`, and that capture may complete immediately after this read — the
    same reachability argument `empty-journal` already carried.
    """
    result = JournalWorkflowPauseStore(
        journal_dir=tmp_path / "pause-journal", tenant_id=None
    ).read_latest_attributed(_WORKFLOW_ID)
    assert result.cause is PauseJournalReadCause.ABSENT
    assert result.indeterminate is True
    assert result.retryable is False


def test_ac4c_corrupt_latest_parse_branch_is_indeterminate(tmp_path: Path) -> None:
    """AC #4(c) — the PARSE-failure branch of `corrupt-latest` is INDETERMINATE.

    A torn trailing line is exactly what an in-flight append looks like from a
    reader, so a read landing mid-append attributes `corrupt-latest` to a record
    that is about to become well-formed.
    """
    journal_dir = tmp_path / "pause-journal"
    store = JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=None)
    store.capture(_snapshot())
    journal = journal_dir / pause_journal_filename(None, _WORKFLOW_ID)
    with journal.open("a", encoding="utf-8") as handle:
        handle.write('{"workflow_id": "wf-b97a", "pause_sn')  # torn tail

    result = store.read_latest_attributed(_WORKFLOW_ID)
    assert result.cause is PauseJournalReadCause.CORRUPT_LATEST
    assert result.indeterminate is True


def test_ac4c_corrupt_latest_decode_branch_stays_unconditionally_permanent(
    tmp_path: Path,
) -> None:
    """AC #4(c) — **and the DECODE branch is NOT indeterminate.**

    A blanket flip would route persistent corruption into a futile re-read loop —
    the exact misrouting §30's cause refinement exists to prevent. Invalid bytes
    persist on disk, an append leaves them in place, and every re-read reproduces
    them.
    """
    journal_dir = tmp_path / "pause-journal"
    journal_dir.mkdir(parents=True)
    journal = journal_dir / pause_journal_filename(None, _WORKFLOW_ID)
    journal.write_bytes(b"\xff\xfe not valid utf-8 \xff\n")

    result = JournalWorkflowPauseStore(
        journal_dir=journal_dir, tenant_id=None
    ).read_latest_attributed(_WORKFLOW_ID)
    assert result.cause is PauseJournalReadCause.CORRUPT_LATEST
    assert result.indeterminate is False, (
        "a DECODE failure is UNCONDITIONALLY PERMANENT — routing it indeterminate "
        "sends the operator into a futile re-read loop"
    )


def test_ac4c_workflow_mismatch_stays_decisive(tmp_path: Path) -> None:
    """`workflow-mismatch` is NOT swept into the flip — no concurrent append
    changes the fact that the handle names a different workflow."""
    journal_dir = tmp_path / "pause-journal"
    journal_dir.mkdir(parents=True)
    journal = journal_dir / pause_journal_filename(None, _WORKFLOW_ID)
    journal.write_text(
        json.dumps(
            {"workflow_id": "someone-else", "pause_snapshot": _snapshot().model_dump(mode="json")}
        )
        + "\n"
    )
    result = JournalWorkflowPauseStore(
        journal_dir=journal_dir, tenant_id=None
    ).read_latest_attributed(_WORKFLOW_ID)
    assert result.cause is PauseJournalReadCause.WORKFLOW_MISMATCH
    assert result.indeterminate is False


# ---------------------------------------------------------------------------
# AC #5 — NO ORACLE.
# ---------------------------------------------------------------------------


def test_ac5_legacy_only_read_is_indistinguishable_from_never_existed(
    tmp_path: Path,
) -> None:
    """AC #5 — a tenant-scoped read of a `workflow_id` whose ONLY journal is the
    untenanted LEGACY one is **INDISTINGUISHABLE** — same cause, same fields —
    from a read of a `workflow_id` that never existed.

    *This is the witness that would have failed under the withdrawn read-path
    diagnostic, and it is what makes the §13.7 surface admissible: the disclosure
    lives on an operator-only tier, never on the tenant-facing read path.*
    """
    journal_dir = tmp_path / "pause-journal"
    journal_dir.mkdir(parents=True)
    (journal_dir / legacy_pause_journal_filename("wf-has-legacy")).write_text(
        json.dumps(
            {
                "workflow_id": "wf-has-legacy",
                "pause_snapshot": _snapshot("wf-has-legacy").model_dump(mode="json"),
            }
        )
        + "\n"
    )
    store = JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=_TENANT_A)

    has_legacy = store.read_latest_attributed("wf-has-legacy")
    never_existed = store.read_latest_attributed("wf-never-existed")

    assert has_legacy == never_existed, (
        "the read DISCLOSED the existence of an untenanted legacy record — this "
        "is the existence oracle path segregation exists to remove"
    )


# ---------------------------------------------------------------------------
# AC #6 — THE MUTATION PROBES (Workflow v1.18 PD-8).
# ---------------------------------------------------------------------------


def test_ac6_mutation_probe_removing_the_tenant_component_fails_ac1(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC #6 — **revert the guard, confirm the test FAILS, restore.**

    Remove the tenant component from the path composition (the pre-v1.108
    derivation) and assert AC #1(b) FAILS: both tenants collapse onto one file
    and tenant A reads back tenant B's record. Green-alone is not proof a guard
    is load-bearing.
    """

    def _de_tenanted(tenant_scope: str | None, workflow_id: str) -> str:
        return legacy_pause_journal_filename(workflow_id)

    monkeypatch.setattr(store_module, "pause_journal_filename", _de_tenanted)

    journal_dir = tmp_path / "pause-journal"
    a = JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=_TENANT_A)
    b = JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=_TENANT_B)
    a.capture(_snapshot(run_id="run-a"))
    b.capture(_snapshot(run_id="run-b"))

    a_read = a.read_latest(_WORKFLOW_ID)
    assert a_read is not None
    assert a_read.run_id == "run-b", (
        "the mutation probe did not reproduce the pre-v1.108 defect — AC #1 is "
        "not actually guarding the keying"
    )
    # monkeypatch restores the real derivation at teardown; the next test's
    # green is the restore half of the probe.


def test_ac6_mutation_probe_naive_delimiter_concatenation_fails_ac2a() -> None:
    """AC #6 — the same probe against AC #2(a).

    Substitute a naive delimiter concatenation for the length-prefixed encoding
    and assert the injectivity witness FAILS on the recorded field-boundary pair.
    """

    def _naive(tenant_scope: str | None, workflow_id: str) -> bytes:
        return (tenant_scope or "").encode() + b"\x00" + workflow_id.encode()

    assert _naive("a", "b\0c") == _naive("a\0b", "c"), (
        "the naive concatenation this probe substitutes is NOT actually "
        "collidable on the recorded pair — the probe would be vacuous"
    )
    # And the shipped encoding is not.
    assert encode_pause_journal_key("a", "b\0c") != encode_pause_journal_key("a\0b", "c")


# ---------------------------------------------------------------------------
# AC #8 — the orphan statement, AS BEHAVIOUR.
# ---------------------------------------------------------------------------


def test_ac8_the_store_never_removes_a_journal_on_any_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC #8 — the harness NEVER removes an orphaned journal on any path.

    *State the negative as a test, because the spec states it as a PERMANENCE
    PROMISE an operator must be able to rely on.* Every removal primitive is
    intercepted across a capture, a read, and a wrong-tenant read over a
    directory holding a legacy orphan.
    """
    import os
    import shutil

    journal_dir = tmp_path / "pause-journal"
    journal_dir.mkdir(parents=True)
    orphan = journal_dir / legacy_pause_journal_filename(_WORKFLOW_ID)
    orphan.write_text("{}\n")

    removals: list[str] = []
    monkeypatch.setattr(Path, "unlink", lambda self, **kw: removals.append(str(self)))
    monkeypatch.setattr(os, "remove", lambda p, **kw: removals.append(str(p)))
    monkeypatch.setattr(os, "unlink", lambda p, **kw: removals.append(str(p)))
    monkeypatch.setattr(shutil, "rmtree", lambda p, **kw: removals.append(str(p)))
    monkeypatch.setattr(Path, "rmdir", lambda self: removals.append(str(self)))

    store = JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=None)
    store.capture(_snapshot())
    store.read_latest(_WORKFLOW_ID)
    JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=_TENANT_A).read_latest(
        _WORKFLOW_ID
    )

    assert removals == [], f"the store removed something: {removals}"
    assert orphan.is_file(), "the legacy orphan was reclaimed — permanence is broken"


def test_ac8_no_pruner_exists_on_the_store() -> None:
    """AC #8 — *and no pruner exists.* A retention POLICY (default, tunable,
    sweep trigger) is a FOLLOW-ON ARC and is explicitly NOT owed here."""
    forbidden = {"prune", "sweep", "compact", "rotate", "gc", "reclaim", "purge", "truncate"}
    surface = {name.lower() for name in dir(JournalWorkflowPauseStore)}
    assert not (forbidden & surface), f"a pruner appeared on the store: {forbidden & surface}"


# ---------------------------------------------------------------------------
# AC #12 — byte-compatibility of everything the arc did NOT change.
# ---------------------------------------------------------------------------


def test_ac12_the_record_shape_is_byte_identical_and_carries_no_wrapper_tenant_key(
    tmp_path: Path,
) -> None:
    """AC #12 — the record shape is BYTE-IDENTICAL before and after, and
    `snapshot_hash` is unchanged. **The tenant scope enters the PATH, never the
    payload** — which is what keeps `snapshot_hash` untouched and the five-member
    cause vocabulary closed.
    """
    snapshot = _snapshot()
    untenanted_dir = tmp_path / "untenanted"
    tenanted_dir = tmp_path / "tenanted"
    JournalWorkflowPauseStore(journal_dir=untenanted_dir, tenant_id=None).capture(snapshot)
    JournalWorkflowPauseStore(journal_dir=tenanted_dir, tenant_id=_TENANT_A).capture(snapshot)

    untenanted_bytes = (untenanted_dir / pause_journal_filename(None, _WORKFLOW_ID)).read_bytes()
    tenanted_bytes = (tenanted_dir / pause_journal_filename(_TENANT_A, _WORKFLOW_ID)).read_bytes()
    assert untenanted_bytes == tenanted_bytes, (
        "the tenant scope leaked into the RECORD — Reading A keeps the record "
        "shape unchanged; only the address moves"
    )

    record = json.loads(untenanted_bytes.decode())
    assert set(record) == {"workflow_id", "pause_snapshot"}, (
        f"a wrapper key was added: {sorted(record)}"
    )
    assert record["pause_snapshot"]["snapshot_hash"] == snapshot.snapshot_hash


def test_ac12_a_reserved_or_empty_tenant_scope_is_refused_at_construction(
    tmp_path: Path,
) -> None:
    """The Runtime-LOCAL normalization authority is the delegate, and it REFUSES
    `""` and the reserved `_single` literal (`None -> None`).

    Delegated, never re-derived: `harness_od`'s `sidecar_tag` / `_tenant_tag`
    would map `None -> "_single"`, an INCOMPATIBLE untenanted disposition that
    would bind this store to a reserved literal it has no need to reserve.
    """
    for reserved in ("", "_single"):
        with pytest.raises(ValueError, match="reserved sidecar tag|must not be empty"):
            JournalWorkflowPauseStore(journal_dir=tmp_path / "pj", tenant_id=reserved)
    # `None` passes through as the untenanted branch.
    assert JournalWorkflowPauseStore(journal_dir=tmp_path / "pj", tenant_id=None) is not None
