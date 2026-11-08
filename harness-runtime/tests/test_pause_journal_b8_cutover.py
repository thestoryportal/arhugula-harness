"""U-RT-160c — journals at the old location (Runtime spec v1.137 Rule B8, witness I.15).

Cutover: with the installation's root bound and holding no file for W, a valid snapshot
journal for W at the old `<state_ledger_dir>/pause-journal` derivation is invisible to every
journal operation. A resume by handle refuses `handle`/`absent` before any claim or body, a
fresh run writes no supersession record, and the legacy file stays byte-identical and
unclaimed.

Operator inventory: `harness-inspect` reads one directory. That is the explicit
`--pause-journal-dir`, else the resolved root, else the `<ledger dir>/pause-journal` default
only while the root is `unresolved(unbound)`. Any other unresolved cause is an unreadable
pause-journal directory.
"""

from __future__ import annotations

import json
import stat
import sys
from collections.abc import Mapping
from pathlib import Path

import pytest
from harness_runtime import bootstrap as bootstrap_module
from harness_runtime.admin.inspect import main
from harness_runtime.api import ResumeHandleUnknownError, resume
from harness_runtime.bootstrap.factories import pause_resume_protocol_factory
from harness_runtime.config_source import RuntimeConfigLoadError, RuntimeConfigSource
from harness_runtime.lifecycle import pause_journal_root_resolver, root_resume_admission
from harness_runtime.lifecycle.journal_workflow_pause_store import (
    PAUSE_JOURNAL_SUBDIR,
    JournalWorkflowPauseStore,
)
from harness_runtime.lifecycle.root_resume_admission import FreshRunAdmission
from harness_runtime.resume_refusal import HandleCause, HandleRefusal, project
from harness_runtime.shutdown import shutdown

from .integration.test_r_cc_1_api_resume import (
    _patched_runtime,  # noqa: F401  # pyright: ignore[reportPrivateUsage, reportUnusedImport]
    _snapshot_for,  # pyright: ignore[reportPrivateUsage]
)
from .pause_journal_roots import declare_pause_journal_root, write_installation_state
from .test_admin_inspect import _write_n_entries  # pyright: ignore[reportPrivateUsage]
from .test_b104_root_resume_facade import (
    _WORKFLOW_ID,  # pyright: ignore[reportPrivateUsage]
    _WORKLOAD,  # pyright: ignore[reportPrivateUsage]
    Harness,
    _Dispatcher,  # pyright: ignore[reportPrivateUsage]
    _durable_filesystem,  # noqa: F401  # pyright: ignore[reportPrivateUsage, reportUnusedImport]
    _outcome,  # pyright: ignore[reportPrivateUsage]
    _Workflow,  # pyright: ignore[reportPrivateUsage]
    harness,  # noqa: F401  # pyright: ignore[reportUnusedImport]
)
from .test_state_placement import world  # noqa: F401  (fixture: scratch dir with no .git above)

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="the journal lock is POSIX flock")

_EXIT_INSPECT_PATH = 2


def _files(directory: Path) -> list[tuple[str, bytes]]:
    return sorted((p.name, p.read_bytes()) for p in directory.iterdir())


async def _legacy_journal(harness: Harness) -> Path:  # noqa: F811
    """A valid snapshot journal for W at the pre-root `<state_ledger_dir>/pause-journal`."""
    ctx = await bootstrap_module.run_bootstrap(harness.config, workload_class=_WORKLOAD)
    try:
        legacy = ctx.ledger_writer.handle.canonical_path.parent / PAUSE_JOURNAL_SUBDIR
    finally:
        await shutdown(ctx)
    JournalWorkflowPauseStore(journal_dir=legacy, tenant_id=None).capture(
        _snapshot_for(_WORKFLOW_ID), depth=None
    )
    return legacy


# --- cutover: no journal operation reads, writes or claims the old location ----------------------


@pytest.mark.asyncio
async def test_a_resume_with_only_a_legacy_journal_refuses_absent_before_any_claim(
    harness: Harness,  # noqa: F811
    _patched_runtime: None,  # noqa: F811
) -> None:
    legacy = await _legacy_journal(harness)
    before = _files(legacy)
    dispatcher = _Dispatcher()

    outcome = await _outcome(
        resume(_Workflow(dispatcher), resume_handle=_WORKFLOW_ID, config=harness.config)
    )

    assert dispatcher.steps == []
    assert isinstance(outcome, ResumeHandleUnknownError), outcome
    refusal = project(outcome)
    assert isinstance(refusal, HandleRefusal) and refusal.cause is HandleCause.ABSENT
    assert harness.claim_files() == []
    assert _files(legacy) == before
    assert harness.journal().read_latest(_WORKFLOW_ID) is None


@pytest.mark.asyncio
async def test_a_fresh_run_with_only_a_legacy_journal_writes_no_supersession(
    harness: Harness,  # noqa: F811
    _patched_runtime: None,  # noqa: F811
) -> None:
    legacy = await _legacy_journal(harness)
    before = _files(legacy)

    ctx = await bootstrap_module.run_bootstrap(harness.config, workload_class=_WORKLOAD)
    try:
        ran = FreshRunAdmission(workflow_id=_WORKFLOW_ID, run_id="run-fresh").run(
            ctx, lambda _: "body ran"
        )
    finally:
        await shutdown(ctx)

    assert ran == "body ran"
    assert not harness.journal()._journal_file(_WORKFLOW_ID).exists()  # pyright: ignore[reportPrivateUsage]
    assert harness.claim_files() == []
    assert _files(legacy) == before


@pytest.mark.asyncio
async def test_mutation_probe_a_resume_reading_the_legacy_location_is_not_absent(
    harness: Harness,  # noqa: F811
    _patched_runtime: None,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The absent witness is not vacuous: pointing the journal sites at the legacy directory
    finds the record, so the resume is no longer refused `handle`/`absent`."""
    legacy = await _legacy_journal(harness)
    for module in (
        pause_journal_root_resolver,
        pause_resume_protocol_factory,
        root_resume_admission,
    ):
        monkeypatch.setattr(module, "resolve_pause_journal_root", lambda _config: legacy)

    outcome = await _outcome(
        resume(_Workflow(_Dispatcher()), resume_handle=_WORKFLOW_ID, config=harness.config)
    )

    assert not isinstance(outcome, ResumeHandleUnknownError), outcome


# --- operator inventory: one directory per invocation ------------------------------------------


def _inventory_site(tmp_path: Path) -> tuple[Path, Path, Path]:
    """A ledger whose default directory holds `wf-legacy`, and a root dir holding `wf-root`."""
    ledger = tmp_path / "ledger" / "state.jsonl"
    ledger.parent.mkdir()
    _write_n_entries(ledger, 1)
    legacy = ledger.parent / PAUSE_JOURNAL_SUBDIR
    JournalWorkflowPauseStore(journal_dir=legacy, tenant_id=None).capture(
        _snapshot_for("wf-legacy"), depth=None
    )
    root = tmp_path / "root"
    JournalWorkflowPauseStore(journal_dir=root, tenant_id=None).capture(
        _snapshot_for("wf-root"), depth=None
    )
    return ledger, legacy, root


def _runtime_config(tmp_path: Path) -> str:
    """A usable `RuntimeConfig` file, which a declared root needs for its overlap judgment."""
    config_file = tmp_path / "harness.toml"
    config_file.write_text(
        "[runtime]\n"
        'deployment_surface = "local-development"\n'
        f'repository_root = "{tmp_path}"\n'
        'default_topology = "single-threaded-linear"\n'
        "\n[runtime.otel]\n"
        'otlp_endpoint = "http://localhost:4317"\n'
    )
    return str(config_file)


def _listed(ledger: Path, capsys: pytest.CaptureFixture[str], *extra: str) -> list[str]:
    assert main(["--ledger-path", str(ledger), "--json", *extra]) == 0
    return [row["workflow_id"] for row in json.loads(capsys.readouterr().out)["pause_journals"]]


def test_unbound_lists_the_ledger_default(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    ledger, _, _ = _inventory_site(tmp_path)
    assert _listed(ledger, capsys) == ["wf-legacy"]


def test_bound_default_lists_the_root_and_the_explicit_dir_lists_the_legacy_journals(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    ledger, legacy, root = _inventory_site(tmp_path)
    declare_pause_journal_root(root)
    config = ("--runtime-config", _runtime_config(tmp_path))

    assert _listed(ledger, capsys, *config) == ["wf-root"]
    assert _listed(ledger, capsys, *config, "--pause-journal-dir", str(legacy)) == ["wf-legacy"]


def test_bound_inventory_is_read_only(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    ledger, legacy, root = _inventory_site(tmp_path)
    declare_pause_journal_root(root)
    config = ("--runtime-config", _runtime_config(tmp_path))
    before = {d: _files(d) for d in (legacy, root)}

    for d in before:
        d.chmod(stat.S_IRUSR | stat.S_IXUSR)
    try:
        listed = (
            _listed(ledger, capsys, *config),
            _listed(ledger, capsys, *config, "--pause-journal-dir", str(legacy)),
        )
    finally:
        for d in before:
            d.chmod(stat.S_IRWXU)

    assert listed == (["wf-root"], ["wf-legacy"])
    assert {d: _files(d) for d in before} == before


@pytest.mark.parametrize(
    ("cause", "declarations"),
    [
        ("malformed", ({},)),
        ("conflicting", ({"installation_root": "/a"}, {"installation_root": "/b"})),
        ("missing", ({"installation_root": "/nonexistent/pause-journal-root"},)),
    ],
)
def test_an_unresolved_root_other_than_unbound_is_an_unreadable_directory(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    cause: str,
    declarations: tuple[Mapping[str, object], ...],
) -> None:
    """A populated ledger default is never the fallback for a declared-but-unresolved root."""
    ledger, _, _ = _inventory_site(tmp_path)
    write_installation_state(json.dumps({"pause_journal_root_declarations": list(declarations)}))

    code = main(["--ledger-path", str(ledger), "--runtime-config", _runtime_config(tmp_path)])
    assert code == _EXIT_INSPECT_PATH
    captured = capsys.readouterr()
    assert "RT-FAIL-INSPECT-PATH — pause-journal directory unreadable" in captured.err
    assert f"({cause})" in captured.err
    assert "wf-legacy" not in captured.out


def test_a_bound_root_without_a_usable_config_is_an_unreadable_directory(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """The resolver needs config to judge overlap, so a declared root it cannot judge is
    unresolved, not unbound."""
    ledger, _, root = _inventory_site(tmp_path)
    declare_pause_journal_root(root)

    def _unusable(*_args: object, **_kwargs: object) -> object:
        raise RuntimeConfigLoadError("unusable ambient harness.toml")

    monkeypatch.setattr(RuntimeConfigSource, "load", _unusable)

    assert main(["--ledger-path", str(ledger)]) == _EXIT_INSPECT_PATH
    captured = capsys.readouterr()
    assert "RT-FAIL-INSPECT-PATH — pause-journal directory unreadable" in captured.err
    assert "wf-legacy" not in captured.out and "wf-root" not in captured.out
