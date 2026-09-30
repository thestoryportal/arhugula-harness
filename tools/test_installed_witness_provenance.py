"""The shared installed-witness prover: what every installed witness must rest on.

These tests cover the reusable seam only: the parent-side gates that must refuse BEFORE any
child is admitted (pinned head, clean tree, receipt, startup code, wheels), the one loaded-module
floor, and the single-owner wiring the B-104 witness (and the later nested witness) consume.
The pure recorded-provenance parser keeps its behavioural suite in
`test_b104_installed_public_witness.py`. Nothing here starts an installed interpreter, a
listener, a model or a provider; the synthetic candidate, venv and wheels live under `tmp_path`.
"""

from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
import zipfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import b104_installed_public_witness as w
import installed_witness_provenance as prover

TOOLS = Path(__file__).resolve().parent
SHA_A = "a" * 64


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    ).stdout.strip()


class Fixture:
    """A synthetic pinned candidate, seven wheels, a venv with startup hooks and a receipt."""

    def __init__(self, base: Path) -> None:
        self.base = base
        self.candidate = (base / "candidate").resolve()
        self.venv = (base / "venv").resolve()
        self.wheel_dir = base / "wheels"
        self.receipt_path = base / "receipt.json"
        self.candidate.mkdir()
        self.wheel_dir.mkdir()
        self.site = self.venv / "lib" / "python3.12" / "site-packages"
        self.site.mkdir(parents=True)
        (self.venv / "bin").mkdir()
        (self.venv / "bin" / "python").write_text("#!/bin/sh\n")
        self.hooks = {
            "_virtualenv.pth": b"import _virtualenv\n",
            "_virtualenv.py": b"# synthetic startup hook\n",
        }
        for name, data in self.hooks.items():
            (self.site / name).write_bytes(data)
        self.wheels: list[dict[str, str]] = []
        for package in sorted(prover.PACKAGES):
            source = self.candidate / package.replace("_", "-") / "src" / package
            source.mkdir(parents=True)
            files = {"__init__.py": f"# {package}\n".encode(), "core.py": b"VALUE = 1\n"}
            for name, data in files.items():
                (source / name).write_bytes(data)
            wheel = self.wheel_dir / f"{package}-0.0.0-py3-none-any.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                for name, data in files.items():
                    archive.writestr(f"{package}/{name}", data)
            self.wheels.append({"path": str(wheel), "sha256": _sha(wheel.read_bytes())})
        _git(self.candidate, "init", "-q")
        _git(self.candidate, "add", "-A")
        _git(self.candidate, "commit", "-q", "-m", "synthetic candidate")
        self.head = _git(self.candidate, "rev-parse", "HEAD")
        self.receipt = self.build_receipt()
        self.write_receipt()

    def build_receipt(self) -> dict[str, Any]:
        return {
            "schema": 2,
            "candidate": str(self.candidate),
            "candidate_head": self.head,
            "venv": str(self.venv),
            "wheels": [dict(item) for item in self.wheels],
            "installed_record_sha256": {package: SHA_A for package in sorted(prover.PACKAGES)},
            "startup_hooks": {
                "site_packages": str(self.site),
                "files": {name: _sha(data) for name, data in self.hooks.items()},
                "absent": ["sitecustomize.py", "usercustomize.py"],
            },
        }

    def write_receipt(self) -> None:
        self.receipt_path.write_text(json.dumps(self.receipt))

    def check(self, expected_head: str | None = None) -> dict[str, Any]:
        return prover.checked_provenance(
            self.receipt_path, self.candidate, self.venv, expected_head or self.head
        )


@pytest.fixture
def fx(tmp_path: Path) -> Fixture:
    return Fixture(tmp_path)


# --- the honest synthetic artifact is admitted, so every refusal below is a real one -------------


def test_an_honest_synthetic_artifact_is_admitted(fx: Fixture) -> None:
    root, installed, python = prover.checked_candidate(fx.candidate, fx.venv, fx.head)
    data = fx.check()

    assert (root, installed) == (fx.candidate, fx.venv) and python == fx.venv / "bin" / "python"
    assert data["source_python_files_checked"] == {p: 2 for p in prover.PACKAGES}
    assert data["startup_hooks_verified"]["site_packages"] == str(fx.site)


# --- head: the parent refuses before it does anything else ----------------------------------------


@pytest.mark.parametrize("pin", ["", "abc", "A" * 40, "g" * 40, "a" * 39, "a" * 41])
def test_a_pin_that_is_not_a_full_lowercase_sha_is_refused(fx: Fixture, pin: str) -> None:
    with pytest.raises(ValueError, match="full lowercase Git SHA"):
        prover.checked_candidate(fx.candidate, fx.venv, pin)


def test_a_head_other_than_the_pin_is_refused(fx: Fixture) -> None:
    with pytest.raises(ValueError, match="differs from pin or tree is not clean"):
        prover.checked_candidate(fx.candidate, fx.venv, "0" * 40)


@pytest.mark.parametrize("dirt", ["tracked", "untracked"])
def test_a_dirty_candidate_tree_is_refused(fx: Fixture, dirt: str) -> None:
    if dirt == "tracked":
        (fx.candidate / "harness-core" / "src" / "harness_core" / "core.py").write_text("X = 2\n")
    else:
        (fx.candidate / "stray.txt").write_text("stray\n")

    with pytest.raises(ValueError, match="differs from pin or tree is not clean"):
        prover.checked_candidate(fx.candidate, fx.venv, fx.head)


def test_a_missing_installed_python_is_refused(fx: Fixture) -> None:
    (fx.venv / "bin" / "python").unlink()

    with pytest.raises(ValueError, match="installed Python is missing"):
        prover.checked_candidate(fx.candidate, fx.venv, fx.head)


def test_the_pure_head_verdict_needs_the_pin_and_no_status() -> None:
    prover.require_clean_pinned("a" * 40, "", "a" * 40)
    for head, status in (("b" * 40, ""), ("a" * 40, " M file")):
        with pytest.raises(ValueError):
            prover.require_clean_pinned(head, status, "a" * 40)


# --- receipt: candidate, head, venv and shape must match what the parent pinned -------------------


def _refuses(fx: Fixture, mutate: Callable[[dict[str, Any]], None], match: str) -> None:
    mutate(fx.receipt)
    fx.write_receipt()
    with pytest.raises(ValueError, match=match):
        fx.check()


@pytest.mark.parametrize(
    "mutate",
    [
        lambda r: r.update(schema=1),
        lambda r: r.update(schema=True),
        lambda r: r.update(candidate="/other/candidate"),
        lambda r: r.update(candidate_head="1" * 40),
        lambda r: r.update(venv="/other/venv"),
    ],
    ids=["schema-1", "schema-bool", "candidate", "head", "venv"],
)
def test_a_receipt_for_another_schema_candidate_head_or_venv_is_refused(
    fx: Fixture, mutate: Callable[[dict[str, Any]], None]
) -> None:
    _refuses(fx, mutate, "does not match candidate, HEAD or venv")


def test_a_receipt_head_other_than_the_pin_the_parent_holds_is_refused(fx: Fixture) -> None:
    with pytest.raises(ValueError, match="does not match candidate, HEAD or venv"):
        fx.check(expected_head="2" * 40)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda r: r["wheels"].pop(),
        lambda r: r["wheels"].append(dict(r["wheels"][0])),
        lambda r: r["wheels"][0].update(extra="x"),
        lambda r: r["wheels"][0].pop("sha256"),
    ],
    ids=["six-wheels", "eight-wheels", "extra-key", "missing-hash"],
)
def test_a_receipt_that_does_not_pin_exactly_seven_wheels_is_refused(
    fx: Fixture, mutate: Callable[[dict[str, Any]], None]
) -> None:
    _refuses(fx, mutate, "seven pinned package wheels|malformed wheel entry")


def test_a_wheel_whose_bytes_differ_from_the_receipt_is_refused(fx: Fixture) -> None:
    Path(fx.wheels[0]["path"]).write_bytes(b"not the pinned wheel")

    with pytest.raises(ValueError, match="wheel hash differs from installation receipt"):
        fx.check()


def test_a_wheel_that_does_not_match_the_pinned_source_tree_is_refused(fx: Fixture) -> None:
    core = fx.candidate / "harness-core" / "src" / "harness_core" / "core.py"
    core.write_bytes(b"VALUE = 2\n")  # the receipt's wheel still carries VALUE = 1

    with pytest.raises(ValueError, match="wheel/source Python file bytes differ"):
        fx.check()


def test_a_wheel_with_an_extra_python_file_is_refused(fx: Fixture) -> None:
    wheel = Path(fx.wheels[0]["path"])
    with zipfile.ZipFile(wheel, "a") as archive:
        archive.writestr(f"{wheel.name.split('-', 1)[0]}/extra.py", b"X = 1\n")
    fx.receipt["wheels"][0]["sha256"] = _sha(wheel.read_bytes())
    fx.write_receipt()

    with pytest.raises(ValueError, match="wheel/source Python file inventory differs"):
        fx.check()


def test_seven_wheels_of_which_one_repeats_a_package_are_refused(fx: Fixture) -> None:
    fx.receipt["wheels"][1] = dict(fx.receipt["wheels"][0])
    fx.write_receipt()

    with pytest.raises(ValueError, match="all seven harness package wheels"):
        fx.check()


def test_installed_record_hashes_must_cover_all_seven_packages(fx: Fixture) -> None:
    _refuses(
        fx,
        lambda r: r["installed_record_sha256"].pop("harness_cp"),
        "seven installed RECORD hashes",
    )


def test_record_hashes_observed_in_the_venv_must_equal_the_receipt(fx: Fixture) -> None:
    observed = {p: {"record_sha256": SHA_A} for p in prover.PACKAGES}
    prover.checked_provenance(fx.receipt_path, fx.candidate, fx.venv, fx.head, observed)

    observed["harness_cp"] = {"record_sha256": "b" * 64}
    with pytest.raises(
        ValueError, match="installed RECORD hashes differ from installation receipt"
    ):
        prover.checked_provenance(fx.receipt_path, fx.candidate, fx.venv, fx.head, observed)


# --- startup: the venv's own code is pinned before its interpreter can run ------------------------


@pytest.mark.parametrize(
    "mutate",
    [
        lambda r: r["startup_hooks"].pop("absent"),
        lambda r: r["startup_hooks"].update(extra=1),
        lambda r: r["startup_hooks"]["files"].pop("_virtualenv.py"),
        lambda r: r["startup_hooks"].update(absent=["sitecustomize.py"]),
        lambda r: r["startup_hooks"].update(absent=["sitecustomize.py", "other.py"]),
        lambda r: r["startup_hooks"].update(site_packages=123),
    ],
    ids=["no-absent", "extra-key", "one-file", "one-absent", "wrong-absent", "site-not-str"],
)
def test_a_malformed_startup_pin_is_refused(
    fx: Fixture, mutate: Callable[[dict[str, Any]], None]
) -> None:
    _refuses(fx, mutate, "startup_hooks object|malformed startup hook pins")


def test_a_startup_pin_for_a_different_site_packages_prefix_is_refused(fx: Fixture) -> None:
    _refuses(
        fx,
        lambda r: r["startup_hooks"].update(site_packages=str(fx.base / "elsewhere")),
        "site-packages path differs from selected venv",
    )


def test_an_extra_startup_pth_file_is_refused(fx: Fixture) -> None:
    (fx.site / "extra.pth").write_text("import os\n")

    with pytest.raises(ValueError, match=r"startup \.pth inventory differs"):
        fx.check()


def test_a_changed_startup_hook_file_is_refused(fx: Fixture) -> None:
    (fx.site / "_virtualenv.py").write_bytes(b"# tampered\n")

    with pytest.raises(ValueError, match=r"startup hook differs from receipt: _virtualenv\.py"):
        fx.check()


@pytest.mark.parametrize("name", ["sitecustomize.py", "usercustomize.py"])
def test_a_startup_customization_file_is_refused(fx: Fixture, name: str) -> None:
    (fx.site / name).write_text("import os\n")

    with pytest.raises(ValueError, match=f"unexpected venv startup customization: {name}"):
        fx.check()


def test_a_venv_with_two_site_packages_directories_is_refused(fx: Fixture) -> None:
    (fx.venv / "lib" / "python3.13" / "site-packages").mkdir(parents=True)

    with pytest.raises(ValueError, match="exactly one site-packages directory"):
        fx.check()


# --- the one loaded-module floor ------------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "meets"),
    [
        (7, True),
        (12, True),
        (6, False),
        (0, False),
        (-1, False),
        (True, False),
        (7.0, False),
        ("7", False),
        (None, False),
        ([7], False),
    ],
)
def test_the_loaded_module_floor_is_the_seven_packages_as_an_exact_int(
    value: object, meets: bool
) -> None:
    assert prover.loaded_modules_meet_floor(value) is meets
    assert prover.MIN_LOADED_HARNESS_MODULES == len(prover.PACKAGES) == 7


# --- one owner: the witnesses consume it, none keeps a second copy --------------------------------

SHARED_NAMES = (
    "PACKAGES",
    "MIN_LOADED_HARNESS_MODULES",
    "WORKSPACE_DIST_VERSION",
    "sha256",
    "checked_wheel_source",
    "checked_candidate",
    "checked_startup_hooks",
    "checked_provenance",
    "installed_origins",
    "interpreter_evidence",
    "loaded_harness_origins",
    "installed_prover",
    "origin_reasons",
    "provenance_reasons",
    "loaded_modules_meet_floor",
)


@pytest.mark.parametrize("name", SHARED_NAMES)
def test_the_b104_witness_exposes_the_shared_owner_object_not_a_copy(name: str) -> None:
    assert getattr(w, name) is getattr(prover, name)


def test_the_witness_is_bound_to_the_module_beside_it_and_pins_its_bytes() -> None:
    assert w.PROVER is prover
    assert w.SHARED_PROVER_PATH == TOOLS / "installed_witness_provenance.py"
    tree = ast.parse((TOOLS / "b104_installed_public_witness.py").read_text())
    defined = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    assert defined.isdisjoint(SHARED_NAMES)  # the proof is defined once, in the shared owner


def test_loading_the_witness_adds_no_sys_path_entry_and_reuses_the_shared_module(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`python -I` has no script directory on the path, and a child refuses foreign entries."""
    import importlib.util

    before = list(sys.path)
    spec = importlib.util.spec_from_file_location("b104_witness_fresh", Path(w.__file__))
    assert spec is not None and spec.loader is not None
    fresh = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "b104_witness_fresh", fresh)  # its dataclasses need it
    spec.loader.exec_module(fresh)

    assert sys.path == before
    assert fresh.PROVER is prover


def test_the_public_plan_command_still_runs_under_isolated_mode() -> None:
    """The child is `python -I <helper>`: it must import its sibling shared owner unaided."""
    result = subprocess.run(
        [sys.executable, "-I", str(TOOLS / "b104_installed_public_witness.py"), "plan"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == w.PLAN


# --- refusal happens before any child is admitted -------------------------------------------


@pytest.fixture
def no_child_may_start(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    started: list[str] = []

    def boom(*_args: object, **_kwargs: object) -> object:
        started.append("started")
        raise AssertionError("a child or service was started before provenance was proved")

    monkeypatch.setattr(w, "spawn", boom)
    monkeypatch.setattr(w, "with_services", boom)
    return started


def _run_witness(fx: Fixture, tmp_path: Path, *, expected_head: str | None = None) -> None:
    w.run(
        fx.candidate,
        fx.venv,
        expected_head or fx.head,
        fx.receipt_path,
        tmp_path / "scenario",
        tmp_path / "out" / "report.json",
    )


def test_a_wrong_pin_stops_the_witness_before_any_child_or_output(
    fx: Fixture, tmp_path: Path, no_child_may_start: list[str]
) -> None:
    with pytest.raises(ValueError, match="differs from pin or tree is not clean"):
        _run_witness(fx, tmp_path, expected_head="3" * 40)

    assert no_child_may_start == [] and not (tmp_path / "scenario").exists()


@pytest.mark.parametrize(
    "mutate",
    [
        lambda r: r.update(candidate_head="4" * 40),
        lambda r: r["startup_hooks"]["files"].__setitem__("_virtualenv.py", "5" * 64),
        lambda r: r["wheels"][0].update(sha256="6" * 64),
    ],
    ids=["receipt-head", "startup-pin", "wheel-pin"],
)
def test_a_mismatched_receipt_stops_the_witness_before_any_child_or_output(
    fx: Fixture,
    tmp_path: Path,
    no_child_may_start: list[str],
    mutate: Callable[[dict[str, Any]], None],
) -> None:
    mutate(fx.receipt)
    fx.write_receipt()

    with pytest.raises(ValueError):
        _run_witness(fx, tmp_path)

    assert no_child_may_start == [] and not (tmp_path / "scenario").exists()
    assert not (tmp_path / "out").exists()


def test_a_foreign_module_already_registered_under_the_shared_name_is_refused(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The load seam has no generic fallback: only the file beside the helper is the owner."""
    import types

    imposter = types.ModuleType("installed_witness_provenance")
    imposter.__file__ = str(tmp_path / "installed_witness_provenance.py")
    monkeypatch.setitem(sys.modules, "installed_witness_provenance", imposter)

    with pytest.raises(ImportError, match="different module is already registered"):
        w._load_shared_prover()  # pyright: ignore[reportPrivateUsage]
