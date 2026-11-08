"""The operator's installation-state carrier (IS spec v1.17 §1.1, Buford cmt-4deb3aa1)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from harness_is.pause_journal_root import Unresolved, UnresolvedCause
from harness_runtime.lifecycle.installation_state import (
    installation_state_bound,
    installation_state_path,
    read_installation_state,
)
from harness_runtime.lifecycle.pause_journal_root_resolver import (
    INSTALLATION_STATE,
    STORAGE_UNSELECTED,
    InstallationState,
    installation_root_declaration,
)

from .pause_journal_roots import declare_pause_journal_roots, write_installation_state


def test_the_carrier_is_fixed_under_the_interpreter_prefix() -> None:
    assert installation_state_path() == (
        Path(sys.prefix) / "etc" / "arhugula" / "installation-state.json"
    )


def test_ambient_selectors_cannot_supply_a_document(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Only the prefix carrier counts: a cwd, env or config-dir copy declares nothing."""
    decoy = tmp_path / "etc" / "arhugula" / "installation-state.json"
    decoy.parent.mkdir(parents=True)
    decoy.write_text(
        json.dumps({"pause_journal_root_declarations": [{"installation_root": str(tmp_path)}]})
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ARHUGULA_INSTALLATION_STATE", str(decoy))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "etc"))

    assert read_installation_state() == STORAGE_UNSELECTED
    assert installation_root_declaration() == Unresolved(UnresolvedCause.UNBOUND)


@pytest.mark.parametrize(
    "document",
    [
        "{",
        "[]",
        '"x"',
        "{}",
        '{"pause_journal_root_declarations": {}}',
        '{"pause_journal_root_declarations": "/a"}',
    ],
)
def test_a_document_without_declarations_fails_closed_malformed(document: str) -> None:
    write_installation_state(document)
    assert installation_root_declaration() == Unresolved(UnresolvedCause.MALFORMED)


@pytest.mark.parametrize(
    "document",
    [
        '{"pause_journal_root_declarations": [{"installation_root": "/a"}],'
        ' "pause_journal_root_declarations": [{"installation_root": "/b"}]}',
        '{"pause_journal_root_declarations": [{"installation_root": "/a", "installation_root": "/b"}]}',
    ],
)
def test_a_repeated_key_fails_closed_malformed_instead_of_keeping_the_last(document: str) -> None:
    write_installation_state(document)
    assert installation_root_declaration() == Unresolved(UnresolvedCause.MALFORMED)


def test_undecodable_bytes_fail_closed_malformed() -> None:
    installation_state_path().parent.mkdir(parents=True)
    installation_state_path().write_bytes(b"\xff\xfe{")
    assert read_installation_state() == Unresolved(UnresolvedCause.MALFORMED)


@pytest.mark.parametrize(
    ("roots", "cause"),
    [
        ((), UnresolvedCause.UNBOUND),
        ((7,), UnresolvedCause.MALFORMED),
        (("/a", "/b"), UnresolvedCause.CONFLICTING),
    ],
)
def test_declarations_pass_unjudged_to_the_resolver(
    roots: tuple[object, ...], cause: UnresolvedCause
) -> None:
    declare_pause_journal_roots(*roots)
    assert installation_root_declaration() == Unresolved(cause)


def test_an_ingress_binding_ignores_an_in_process_selector(tmp_path: Path) -> None:
    INSTALLATION_STATE.set(InstallationState(({"installation_root": str(tmp_path)},)))
    with installation_state_bound():
        assert INSTALLATION_STATE.get() == STORAGE_UNSELECTED


def test_the_binding_restores_the_prior_value_on_success_and_error(tmp_path: Path) -> None:
    declare_pause_journal_roots(str(tmp_path))
    INSTALLATION_STATE.set(prior := STORAGE_UNSELECTED)  # a prior binding unlike the document
    with installation_state_bound():
        assert INSTALLATION_STATE.get() == InstallationState(
            ({"installation_root": str(tmp_path)},)
        )
    assert INSTALLATION_STATE.get() == prior

    with pytest.raises(RuntimeError), installation_state_bound():
        raise RuntimeError
    assert INSTALLATION_STATE.get() == prior


def test_separate_processes_of_one_interpreter_read_the_same_document(tmp_path: Path) -> None:
    declare_pause_journal_roots(str(tmp_path))
    script = (
        "import sys; sys.prefix = sys.argv[1]\n"
        "from harness_runtime.lifecycle.installation_state import read_installation_state\n"
        "print(read_installation_state())\n"
    )
    outputs = {
        subprocess.run(
            [sys.executable, "-c", script, sys.prefix], capture_output=True, text=True, check=True
        ).stdout
        for _ in range(2)
    }
    assert outputs == {f"{read_installation_state()}\n"}
