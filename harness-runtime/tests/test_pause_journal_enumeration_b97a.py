"""`B-97` half (a) — the §13.7 pause-journal ENUMERATION surface (U-RT-149 AC #7).

Runtime spec v1.108 §13.7 (seven terms + 3-bis + 3-ter) + §13.7.1 (the normative
THREE-WAY classification), landed as an extension of the existing
`harness-inspect` binary under the §13 read-only invariant.

**Term by term**, each asserted BY EXECUTION:

- (a) it ENUMERATES and accepts no `workflow_id` to probe — asserted BY INTERFACE;
- (a-bis) the canonical journal-file filter — lock files and adoption artifacts;
- (b) it runs PRE-FLIGHT, against a directory written by a pre-v1.108 store;
- (c) record count + latest-record digest, computed WITHOUT parsing a record;
- (c-bis) the wrapper `workflow_id` + the three-way actionability classification;
- (d) it NEVER parses, returns, or resumes a snapshot;
- (d-bis) the output STATES its upper-bound limit;
- (e) with no journal directory present, output is BYTE-IDENTICAL to before;
- (f) the read-only invariant, re-asserted by the EXISTING chmod fixture.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import os
import stat
from pathlib import Path
from typing import Any

import pytest
from harness_cp.handoff_context import StateSummary
from harness_cp.pause_resume_protocol_types import PauseSnapshot, WorkflowPauseReason
from harness_is.state_ledger_entry_schema import Identifier
from harness_runtime.admin.inspect import main
from harness_runtime.admin.pause_journal_enumeration import (
    JournalIdentityClass,
    enumerate_pause_journals,
    is_canonical_journal_name,
)
from harness_runtime.lifecycle.journal_workflow_pause_store import (
    PAUSE_JOURNAL_LOCK_SUFFIX,
    PAUSE_JOURNAL_SUBDIR,
    JournalWorkflowPauseStore,
    legacy_pause_journal_filename,
    pause_journal_filename,
)

from tests.test_admin_inspect import _write_n_entries

_TENANT = "tenant-a"


def _snapshot(workflow_id: str, *, run_id: str = "run-1") -> PauseSnapshot:
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


def _record(workflow_id: str, *, wrapper_id: str | None = None) -> str:
    """One journal line. `wrapper_id` overrides the WRAPPER key only — the shape
    a MIS-FILED record has (wrapper says `B`, file named for `A`)."""
    return json.dumps(
        {
            "workflow_id": wrapper_id if wrapper_id is not None else workflow_id,
            "pause_snapshot": _snapshot(workflow_id).model_dump(mode="json"),
        }
    )


def _legacy_journal(journal_dir: Path, workflow_id: str) -> Path:
    """A pre-v1.108 journal: named `sha256(workflow_id)`, wrapper `workflow_id`."""
    journal_dir.mkdir(parents=True, exist_ok=True)
    path = journal_dir / legacy_pause_journal_filename(workflow_id)
    path.write_text(_record(workflow_id) + "\n")
    return path


# ---------------------------------------------------------------------------
# Term 1 + (a) — ENUMERATE, never probe a derived path.
# ---------------------------------------------------------------------------


def test_ac7a_the_surface_accepts_no_workflow_id_to_probe() -> None:
    """AC #7(a) — asserted **BY INTERFACE**, not merely that the happy path lists.

    A single-path probe on an admin binary reintroduces the EXISTENCE ORACLE the
    read-path diagnostic was withdrawn for: every tenant would probe the SAME
    legacy path, so a distinct result would disclose that a record exists for a
    GUESSED `workflow_id`. **This is the load-bearing shape term**, so it is
    pinned at the signature — a future `workflow_id=` parameter fails here.

    The pin is EXHAUSTIVE deliberately: an allow-list of forbidden names would
    let a `for_workflow=` synonym through. `scope_known` joined it at round 4 and
    is not a lookup key of any kind — it says only whether `tenant_scope` carries
    a claim about this deployment at all.
    """
    signature = inspect.signature(enumerate_pause_journals)
    assert list(signature.parameters) == ["journal_dir", "tenant_scope", "scope_known"]
    assert signature.parameters["tenant_scope"].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters["scope_known"].kind is inspect.Parameter.KEYWORD_ONLY
    assert "workflow_id" not in signature.parameters


def test_ac7a_bis_lock_files_and_write_aside_artifacts_are_excluded(tmp_path: Path) -> None:
    """AC #7(a-bis) — the CANONICAL JOURNAL-FILE FILTER.

    A directory containing the per-workflow `<digest>.jsonl.lock` files the
    append path creates with `O_CREAT` and NEVER unlinks (one beside every
    journal) yields **journal rows only** — no lock file is counted, classified,
    or reported, and neither is any adoption write-aside artifact. Unfiltered,
    they inflate the at-risk bound and emit spurious identity-ABSENT rows: *a
    lock file carries no bytes and nothing reads it.*
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    # A REAL capture, so the lock sibling is created by the shipped append path
    # rather than fabricated by the test.
    JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=None).capture(_snapshot("wf-1"))
    journal = journal_dir / pause_journal_filename(None, "wf-1")
    lock = journal.with_name(journal.name + PAUSE_JOURNAL_LOCK_SUFFIX)
    if not lock.exists():  # Windows carve-out — the lock is a documented no-op.
        lock.write_bytes(b"")
    # An adoption write-aside artifact, of the shape the publication leaves.
    (journal_dir / ".adopt-tmp-abc123").write_bytes(b"partial")
    # And a plausible-but-non-canonical neighbour.
    (journal_dir / "notes.jsonl").write_text("{}\n")

    rows = enumerate_pause_journals(journal_dir, tenant_scope=None)

    assert [row.path.name for row in rows] == [journal.name]
    assert not is_canonical_journal_name(lock.name)
    assert not is_canonical_journal_name(".adopt-tmp-abc123")
    assert not is_canonical_journal_name("notes.jsonl")


# ---------------------------------------------------------------------------
# Terms 2 + 3 + 4 — pre-flight, the two scalars, and no parsing.
# ---------------------------------------------------------------------------


def test_ac7b_runs_preflight_against_a_pre_v1108_directory(tmp_path: Path) -> None:
    """AC #7(b) — usable BEFORE an upgrade, against a directory written by a
    PRE-v1.108 store.

    *A post-mortem-only surface satisfies the diagnosis need and not the
    RECOURSE need, and the recourse need is why (3a)'s cost bound is stateable at
    all.*
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    _legacy_journal(journal_dir, "wf-legacy")

    rows = enumerate_pause_journals(journal_dir, tenant_scope=None)

    assert len(rows) == 1
    assert rows[0].classification is JournalIdentityClass.LEGACY
    assert rows[0].workflow_id == "wf-legacy"
    assert rows[0].identity_actionable is True


def test_ac7c_reports_count_and_digest_agreeing_with_the_store(tmp_path: Path) -> None:
    """AC #7(c) — record count + latest-record digest, computed WITHOUT parsing.

    The count is **NON-BLANK RAW LINES** and the digest is a hash of the latest
    **raw** line — and both MUST agree with what the store itself reports, or the
    operator gets two numbers for one journal.
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    store = JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=_TENANT)
    store.capture(_snapshot("wf-1", run_id="run-1"))
    store.capture(_snapshot("wf-1", run_id="run-2"))

    (row,) = enumerate_pause_journals(journal_dir, tenant_scope=_TENANT)
    from_store = store.read_latest_attributed("wf-1")

    assert row.record_count == from_store.record_count == 2
    assert row.latest_record_digest == from_store.latest_record_digest
    latest_raw = (
        (journal_dir / pause_journal_filename(_TENANT, "wf-1")).read_text().splitlines()[-1]
    )
    assert row.latest_record_digest == hashlib.sha256(latest_raw.encode()).hexdigest()


def test_ac7c_a_torn_journal_still_yields_a_computable_count(tmp_path: Path) -> None:
    """A *"well-formed lines"* count would require parsing (which term 4 forbids)
    and would have NO computable value on a torn journal — the very case term
    3-bis and the pre-flight requirement demand stay listable."""
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    store = JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=None)
    store.capture(_snapshot("wf-1"))
    journal = journal_dir / pause_journal_filename(None, "wf-1")
    with journal.open("a", encoding="utf-8") as handle:
        handle.write('{"workflow_id": "wf-1", "pause_sn')

    (row,) = enumerate_pause_journals(journal_dir, tenant_scope=None)

    assert row.record_count == 2  # both raw lines counted
    assert row.workflow_id is None, "a torn latest line has no readable wrapper identity"
    assert row.classification is None
    assert row.identity_actionable is False


def test_ac7d_never_constructs_a_pause_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC #7(d) — the surface NEVER parses, returns, or resumes a snapshot.

    Asserted by intercepting `PauseSnapshot.model_validate` for the duration of a
    full enumeration over a directory holding valid records: **no `PauseSnapshot`
    is constructed on this path.** The boundary is the EMBEDDED SNAPSHOT, not the
    record — reading the store-owned wrapper's own keys is permitted and is what
    term 3-ter requires.
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=None).capture(_snapshot("wf-1"))
    _legacy_journal(journal_dir, "wf-legacy")

    constructed: list[object] = []
    real = PauseSnapshot.model_validate

    def _spy(*args: Any, **kwargs: Any) -> Any:
        constructed.append(args)
        return real(*args, **kwargs)

    monkeypatch.setattr(PauseSnapshot, "model_validate", _spy)
    rows = enumerate_pause_journals(journal_dir, tenant_scope=None)

    assert len(rows) == 2
    assert constructed == [], "the enumeration deserialized a PauseSnapshot"


# ---------------------------------------------------------------------------
# Term 3-ter + §13.7.1 — the identity and the THREE-WAY classification.
# ---------------------------------------------------------------------------


def test_ac7c_bis_three_way_classification_over_one_directory(tmp_path: Path) -> None:
    """AC #7(c-bis) / §13.7.1 — **all three classes in ONE directory.**

    (1) a genuine LEGACY journal → identity ACTIONABLE;
    (2) a valid CURRENT-FORMAT journal under this deployment's scope → ordinary
        state, **NOT** reported as mis-filed and **NOT** actionable — *this case
        is what makes the classification three-way rather than a bare binding
        check, and a suite without it passes while the surface slanders every
        post-upgrade journal*;
    (3) a CO-TENANT journal under a DIFFERENT scope → NOT ATTRIBUTABLE FROM HERE,
        with the wrapper identity still REPORTED but marked NOT actionable and
        **no guess** as to whether it is mis-filed or foreign-scoped.
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    _legacy_journal(journal_dir, "wf-legacy")
    JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=_TENANT).capture(
        _snapshot("wf-current")
    )
    JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id="other-tenant").capture(
        _snapshot("wf-cotenant")
    )

    rows = {
        row.workflow_id: row for row in enumerate_pause_journals(journal_dir, tenant_scope=_TENANT)
    }

    assert rows["wf-legacy"].classification is JournalIdentityClass.LEGACY
    assert rows["wf-legacy"].identity_actionable is True
    assert rows["wf-legacy"].adoptable is True

    assert rows["wf-current"].classification is JournalIdentityClass.CURRENT_FORMAT
    assert rows["wf-current"].identity_actionable is False
    assert rows["wf-current"].adoptable is False

    assert rows["wf-cotenant"].classification is JournalIdentityClass.NOT_ATTRIBUTABLE
    assert rows["wf-cotenant"].identity_actionable is False
    # The identity IS reported for every journal — the classification governs
    # ACTIONABILITY, never DISCLOSURE.
    assert rows["wf-cotenant"].workflow_id == "wf-cotenant"


def test_ac7c_bis_a_mis_filed_record_is_reported_but_never_actionable(tmp_path: Path) -> None:
    """§13.7.1's third arm, on the MIS-FILED shape: a journal named
    `sha256(A)` whose wrapper says `B`.

    Classified **not-LEGACY**, identity **NOT actionable** — the surface never
    presents the name `B` as something the operator may act on, and it does not
    guess whether this is a mis-file or a co-tenant's file.
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    journal_dir.mkdir(parents=True)
    (journal_dir / legacy_pause_journal_filename("A")).write_text(
        _record("A", wrapper_id="B") + "\n"
    )

    (row,) = enumerate_pause_journals(journal_dir, tenant_scope=None)

    assert row.workflow_id == "B"
    assert row.classification is JournalIdentityClass.NOT_ATTRIBUTABLE
    assert row.identity_actionable is False
    assert row.adoptable is False


def test_ac7c_bis_every_journal_gets_an_identity_row_including_unreadable_ones(
    tmp_path: Path,
) -> None:
    """A journal whose latest line is torn or undecodable is **STILL LISTED**,
    with the identity reported ABSENT rather than fabricated or omitted."""
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    journal_dir.mkdir(parents=True)
    (journal_dir / pause_journal_filename(None, "wf-undecodable")).write_bytes(b"\xff\xfe\n")
    (journal_dir / pause_journal_filename(None, "wf-empty")).write_text("\n\n")

    rows = enumerate_pause_journals(journal_dir, tenant_scope=None)

    assert len(rows) == 2
    assert all(row.workflow_id is None for row in rows)
    assert all(row.classification is None for row in rows)
    assert all(row.identity_actionable is False for row in rows)
    # Both are READABLE and genuinely hold no usable identity — `record_count`
    # is a real number, never the UNKNOWN sentinel.
    assert all(row.record_count is not None for row in rows)
    assert all(row.unreadable is False for row in rows)


# ---------------------------------------------------------------------------
# Terms 5 + 6 + (d-bis) — engagement, the upper-bound statement, read-only.
# ---------------------------------------------------------------------------


def test_ac7e_output_is_byte_identical_when_no_journal_directory_exists(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """AC #7(e) — with **no journal directory present**, `harness-inspect` output
    is **BYTE-IDENTICAL** to a pre-v1.108 run. Asserted **ON BYTES**, not on a
    substring: the operator's burden is zero and a deployment that has never
    journaled a pause never sees this surface at all.
    """
    ledger = tmp_path / "state.jsonl"
    _write_n_entries(ledger, 2)
    assert not (tmp_path / PAUSE_JOURNAL_SUBDIR).exists()

    assert main(["--ledger-path", str(ledger)]) == 0
    without_dir = capsys.readouterr().out

    # Now create the directory (empty) and re-run: the surface ENGAGES, so the
    # output must differ — which is what proves the byte-identity above is a
    # genuine engagement predicate rather than a surface that never fires.
    (tmp_path / PAUSE_JOURNAL_SUBDIR).mkdir()
    assert main(["--ledger-path", str(ledger)]) == 0
    with_dir = capsys.readouterr().out

    assert "pause journal" not in without_dir
    assert with_dir != without_dir
    assert with_dir.startswith(without_dir.rstrip("\n"))


def test_ac7d_bis_output_states_the_upper_bound_limit(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """AC #7(d-bis) — the listing does **NOT** present itself as an
    outstanding-pause inventory.

    A resolved journal is byte-indistinguishable from an outstanding one (the
    store writes no pause-resolved marker; `B-104`), so the surface states that
    limit **in its own output** rather than letting an operator read the listing
    as a live-pause inventory.
    """
    ledger = tmp_path / "state.jsonl"
    _write_n_entries(ledger, 1)
    _legacy_journal(tmp_path / PAUSE_JOURNAL_SUBDIR, "wf-legacy")

    assert main(["--ledger-path", str(ledger)]) == 0
    human = capsys.readouterr().out
    assert "UPPER BOUND ONLY" in human
    assert "MUST NOT" in human

    assert main(["--ledger-path", str(ledger), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert "UPPER BOUND ONLY" in payload["pause_journal_upper_bound_disclaimer"]
    assert payload["pause_journal_count"] == 1
    assert payload["pause_journals"][0]["workflow_id"] == "wf-legacy"
    assert payload["pause_journals"][0]["classification"] == "legacy"
    assert payload["pause_journals"][0]["identity_actionable"] is True
    # The §13.5 audit sections are COMPOSED WITH, never replaced.
    assert payload["head_hash"] is not None
    assert payload["total_entries"] == 1


def test_ac7f_read_only_invariant_holds_over_the_new_surface(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """AC #7(f) — the READ-ONLY invariant holds over the new surface, re-asserted
    by the **EXISTING** chmod-readonly fixture discipline, not a new one.

    Both halves of the shipped discipline: (1) the whole journal directory tree
    is chmod'd read-only and `harness-inspect` must still succeed; (2) the
    sentinel monkeypatch on `Path.open` / `os.open` catches any write attempt.
    """
    ledger = tmp_path / "state.jsonl"
    _write_n_entries(ledger, 1)
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    journal = _legacy_journal(journal_dir, "wf-legacy")

    real_path_open: Any = Path.open
    real_os_open: Any = os.open
    write_attempts: list[str] = []

    def _spy_path_open(self: Path, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
        if any(c in mode for c in ("w", "a", "x", "+")):
            write_attempts.append(f"Path.open({self}, mode={mode!r})")
        return real_path_open(self, mode, *args, **kwargs)

    def _spy_os_open(path: Any, flags: int, *args: Any, **kwargs: Any) -> int:
        write_flags = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC
        if flags & write_flags:
            write_attempts.append(f"os.open({path}, flags={flags})")
        return real_os_open(path, flags, *args, **kwargs)  # type: ignore[no-any-return]

    journal.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    journal_dir.chmod(stat.S_IRUSR | stat.S_IXUSR)
    try:
        monkeypatch.setattr(Path, "open", _spy_path_open)
        monkeypatch.setattr(os, "open", _spy_os_open)
        code = main(["--ledger-path", str(ledger)])
    finally:
        monkeypatch.undo()
        journal_dir.chmod(stat.S_IRWXU)
        journal.chmod(stat.S_IRUSR | stat.S_IWUSR)

    assert code == 0
    assert write_attempts == [], f"the §13.7 surface attempted a write: {write_attempts}"
    assert "wf-legacy" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Out-of-family review round 1 — the fixes, each with its own witness.
# ---------------------------------------------------------------------------


def test_scalars_are_computed_over_raw_bytes_not_a_decoded_whole_file(tmp_path: Path) -> None:
    """Round 1 [P2] — a journal holding ONE invalid UTF-8 byte anywhere must
    still report its two scalars.

    §13.7 term 3 defines the count as NON-BLANK RAW LINES and the digest as a
    hash of the latest RAW line; neither requires decoding. A whole-file
    `read_text` collapsed a journal with a corrupt EARLIER line — beneath a
    perfectly valid latest record — to `record_count=0`, **understating the
    cutover upper bound on exactly the torn-journal case term 3-bis says must
    stay listable.**
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    journal_dir.mkdir(parents=True)
    journal = journal_dir / legacy_pause_journal_filename("wf-mixed")
    valid_latest = _record("wf-mixed").encode()
    journal.write_bytes(b"\xff\xfe corrupt earlier line\n" + valid_latest + b"\n")

    (row,) = enumerate_pause_journals(journal_dir, tenant_scope=None)

    assert row.record_count == 2, "the corrupt earlier line erased the whole count"
    assert row.latest_record_digest == hashlib.sha256(valid_latest).hexdigest()
    # ... and the identity is still readable, because only the LATEST line's
    # decodability matters to it.
    assert row.workflow_id == "wf-mixed"
    assert row.classification is JournalIdentityClass.LEGACY


def test_an_undecodable_latest_line_costs_the_identity_and_nothing_else(
    tmp_path: Path,
) -> None:
    """The scalars and the identity are INDEPENDENT: an undecodable LATEST line
    reports the identity ABSENT (term 3-ter's mandated disposition) while the two
    scalars stay computable."""
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    journal_dir.mkdir(parents=True)
    journal = journal_dir / pause_journal_filename(None, "wf-x")
    journal.write_bytes(_record("wf-x").encode() + b"\n\xff\xfe undecodable latest\n")

    (row,) = enumerate_pause_journals(journal_dir, tenant_scope=None)

    assert row.record_count == 2
    assert row.latest_record_digest is not None
    assert row.workflow_id is None
    assert row.classification is None


def test_non_regular_files_matching_the_name_shape_are_excluded(tmp_path: Path) -> None:
    """Round 1 [P2] — the name shape alone does not make an entry a FILE.

    A DIRECTORY named `<64hex>.jsonl` would become a phantom zero-count row (and
    later make disposal raise `IsADirectoryError`); a FIFO would BLOCK the read
    indefinitely — on a PRE-FLIGHT surface whose whole purpose is to run before
    an upgrade.
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    journal_dir.mkdir(parents=True)
    real = _legacy_journal(journal_dir, "wf-real")
    (journal_dir / ("a" * 64 + ".jsonl")).mkdir()  # a DIRECTORY, canonical-named
    if hasattr(os, "mkfifo"):
        os.mkfifo(journal_dir / ("b" * 64 + ".jsonl"))

    rows = enumerate_pause_journals(journal_dir, tenant_scope=None)

    assert [row.path.name for row in rows] == [real.name]


def test_an_unreadable_journal_directory_is_a_path_error_not_a_false_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Round 1 [P2] — an unreadable journal DIRECTORY takes the binary's own
    `RT-FAIL-INSPECT-PATH` exit, never an empty listing.

    Swallowing the error would render `pause journals: 0` and present **UNKNOWN
    exposure as a proven zero** — on the pre-flight surface that exists to bound
    what a cutover would abandon. A false zero here is worse than a crash.
    """
    ledger = tmp_path / "state.jsonl"
    _write_n_entries(ledger, 1)
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    _legacy_journal(journal_dir, "wf-legacy")

    real_iterdir = Path.iterdir

    def _denied(self: Path) -> Any:
        if self == journal_dir:
            raise PermissionError(13, "Permission denied")
        return real_iterdir(self)

    monkeypatch.setattr(Path, "iterdir", _denied)
    code = main(["--ledger-path", str(ledger)])
    monkeypatch.undo()

    captured = capsys.readouterr()
    assert code == 2, "an unreadable journal directory did not take the path-error exit"
    assert "RT-FAIL-INSPECT-PATH" in captured.err
    assert "pause journals: 0" not in captured.out


# ---------------------------------------------------------------------------
# Out-of-family review round 3 — the fixes, each with its own witness.
# ---------------------------------------------------------------------------


def test_an_unreadable_journal_reports_unknown_not_zero_records(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Round 3 [P2] — an unreadable journal reports `record_count=None` (UNKNOWN),
    never a fabricated `0`.

    `0` means *known to hold no record*; `None` means *not known at all*. The
    type keeps them apart so the illegal state — an unreadable journal presenting
    itself as an empty one — is unrepresentable, and so the pre-flight surface
    never presents UNKNOWN exposure as proven-zero.
    """
    ledger = tmp_path / "state.jsonl"
    _write_n_entries(ledger, 1)
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    journal = _legacy_journal(journal_dir, "wf-legacy")
    journal.chmod(0)
    try:
        (row,) = enumerate_pause_journals(journal_dir, tenant_scope=None)
        assert row.record_count is None
        assert row.unreadable is True
        assert row.latest_record_digest is None
        assert row.workflow_id is None
        assert main(["--ledger-path", str(ledger)]) == 0
        out = capsys.readouterr().out
        assert "records=UNREADABLE" in out
        assert "records=0" not in out
    finally:
        journal.chmod(0o600)


def test_the_tenant_scope_comes_from_the_normal_config_precedence_chain(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Round 3 [P2] — the classification consults the deployment's config, and
    the ENV layer of §3.7's precedence chain reaches it.

    Without loading the normal `RuntimeConfigSource` chain, a deployment
    configured the ordinary way — `HARNESS_TENANT_ID` over a discovered
    `harness.toml` — was read as UNTENANTED, and every one of its valid
    tenant-keyed journals was slandered as NOT-ATTRIBUTABLE. Here the config
    file supplies the four REQUIRED fields and the ENV supplies the tenant, so a
    green asserts the whole chain was walked rather than just the file.
    """
    ledger = tmp_path / "state.jsonl"
    _write_n_entries(ledger, 1)
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=_TENANT).capture(
        _snapshot("wf-current")
    )
    config_file = tmp_path / "harness.toml"
    config_file.write_text(
        "[runtime]\n"
        'deployment_surface = "local-development"\n'
        f'repository_root = "{tmp_path}"\n'
        'default_topology = "single-threaded-linear"\n'
        "\n[runtime.otel]\n"
        'otlp_endpoint = "http://localhost:4317"\n'
    )

    monkeypatch.setenv("HARNESS_TENANT_ID", _TENANT)
    assert main(["--ledger-path", str(ledger), "--runtime-config", str(config_file), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    monkeypatch.undo()

    assert payload["pause_journal_deployment_scope_known"] is True
    (row,) = payload["pause_journals"]
    assert row["classification"] == "current-format", (
        "the deployment's own live journal was misclassified because the config "
        "precedence chain was not consulted"
    )
    assert row["identity_actionable"] is False


def test_an_undeterminable_scope_is_reported_not_assumed_untenanted(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Round 3 [P2], the other half — when NO usable config exists the scope is
    reported UNAVAILABLE rather than silently taken to be untenanted.

    Assuming untenanted would present a tenanted deployment's own live journals
    as NOT-ATTRIBUTABLE **with no hint that the diagnosis rests on an unknown**.
    Codex's own remedy — *"or report that the scope is unavailable"* — is the one
    taken here, because a stopped-harness admin binary genuinely may not be able
    to reconstruct the config.
    """
    ledger = tmp_path / "state.jsonl"
    _write_n_entries(ledger, 1)
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=_TENANT).capture(
        _snapshot("wf-current")
    )

    assert main(["--ledger-path", str(ledger)]) == 0
    human = capsys.readouterr().out
    assert "DEPLOYMENT SCOPE UNAVAILABLE" in human
    assert "No row below is a diagnosis of mis-filing" in human

    assert main(["--ledger-path", str(ledger), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["pause_journal_deployment_scope_known"] is False
    # The row is still listed — the surface never omits a journal.
    assert payload["pause_journal_count"] == 1


def test_round4_an_unknown_scope_does_not_classify_an_untenanted_journal_current_format(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Round 4 [P2] — **an UNKNOWN scope is not an UNTENANTED one.**

    The round-3 fix reported `scope_known` but still passed `tenant_scope=None`
    to the classifier, and `None` is a *legitimate domain value*: it re-derives
    the UNTENANTED-format filename. So every untenanted-format journal in the
    directory came back CURRENT-FORMAT — *ordinary state, not at risk* — on a
    deployment whose scope could not be determined and which may not own it. A
    JSON consumer reading `identity_actionable: false` acts on that false
    all-clear. Under an unknown scope the CURRENT-FORMAT arm is simply not
    available; LEGACY still proves itself and everything else is honestly
    NOT-ATTRIBUTABLE.

    **This is also the MUTATION PROBE**, by construction: `scope_known` is
    consumed in exactly one place — the `scope_known and ...` conjunct guarding
    the CURRENT-FORMAT arm — so deleting that conjunct makes `scope_known=False`
    behave identically to `scope_known=True`. The `scope_known=True` leg below
    therefore *is* the reverted code's answer on these same bytes, and it is
    `current-format`.
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    # An UNTENANTED-format journal — the shape `tenant_scope=None` re-derives.
    JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=None).capture(
        _snapshot("wf-untenanted")
    )

    (unknown,) = enumerate_pause_journals(journal_dir, tenant_scope=None, scope_known=False)
    assert unknown.workflow_id == "wf-untenanted", "the identity is still reported in full"
    assert unknown.classification is JournalIdentityClass.NOT_ATTRIBUTABLE
    assert unknown.identity_actionable is False

    # The reverted-guard answer on the SAME bytes: the false all-clear.
    (known,) = enumerate_pause_journals(journal_dir, tenant_scope=None, scope_known=True)
    assert known.classification is JournalIdentityClass.CURRENT_FORMAT, (
        "the two legs agree, so the flag is not load-bearing and this witness "
        "would pass against the reverted code"
    )

    # And end-to-end through the binary, where no usable config exists at all.
    ledger = tmp_path / "state.jsonl"
    _write_n_entries(ledger, 1)
    assert main(["--ledger-path", str(ledger), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["pause_journal_deployment_scope_known"] is False
    (row,) = payload["pause_journals"]
    assert row["classification"] == "not-attributable"
    assert row["identity_actionable"] is False


def test_a_lone_surrogate_workflow_id_does_not_crash_human_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Round 3 [P2] — the key encoding deliberately supports EVERY Python string
    via `surrogatepass`, so a persisted `workflow_id` may hold a LONE SURROGATE.

    Rendering it verbatim raises `UnicodeEncodeError` the moment the summary
    reaches a normal UTF-8 stdout, and control characters would corrupt the row
    structure. The identity is therefore rendered escaped.
    """
    surrogate_id = "wf-\ud800-x"
    ledger = tmp_path / "state.jsonl"
    _write_n_entries(ledger, 1)
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    journal_dir.mkdir(parents=True)
    # The CURRENT-format derivation, not the legacy one: `surrogatepass` is what
    # makes the new encoding TOTAL over this id, while the legacy `sha256` used
    # STRICT UTF-8 and could never have produced a file for it at all.
    (journal_dir / pause_journal_filename(None, surrogate_id)).write_bytes(
        json.dumps({"workflow_id": surrogate_id, "pause_snapshot": {}}).encode() + b"\n"
    )

    assert main(["--ledger-path", str(ledger)]) == 0
    out = capsys.readouterr().out

    # Escaped, and therefore safely encodable to a real UTF-8 stream.
    assert "\\ud800" in out
    out.encode("utf-8")
