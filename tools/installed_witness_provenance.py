"""Shared installed-witness provenance: one owner of the receipt/origin theorem.

Every evaluation-only installed witness (the B-104 root-resume witness today, the nested
PRE_ACTION witness later) proves its installed artifact with THIS module, so both rest on one
receipt/origin theorem [LAW:single-enforcer]. It has two halves that never mix:

* Boundary I/O, run by the stdlib-only parent before any child starts and by each installed
  child before its phase body: `checked_candidate`, `checked_startup_hooks`,
  `checked_provenance` (parent side: pinned head, clean tree, receipt, wheels, startup code),
  and `interpreter_evidence`, `installed_origins`, `loaded_harness_origins`, `installed_prover`
  (child side: the child is the BYTE AUTHORITY for its own interpreter, `sys.path`, RECORD
  bytes and loaded modules). [LAW:effects-at-boundaries]
* Pure recorded-provenance parsing, run by the parent when it judges what a child recorded:
  `provenance_reasons`, `origin_reasons`, `loaded_modules_meet_floor`. It reads only the record
  values it is handed and never opens, hashes or resolves an installed file's bytes: the
  canonical-spelling check proves recorded path SHAPE, not that a file still exists or is
  unchanged. [LAW:parse-dont-validate]

Everything is driven by explicitly passed candidate, head, venv/prefix, receipt and wheel data;
nothing here imports a harness package at module load or reads ambient configuration.

This module is loaded by explicit file path (see the B-104 witness), never by adding its
directory to `sys.path`, because `python -I` does not put the script directory on the path and
`interpreter_evidence` refuses any foreign `sys.path` entry.
"""

from __future__ import annotations

import base64
import hashlib
import importlib
import importlib.metadata
import json
import os
import subprocess
import sys
import zipfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

PACKAGES = frozenset(
    {
        "harness_core",
        "harness_cp",
        "harness_as",
        "harness_od",
        "harness_is",
        "harness_cxa",
        "harness_runtime",
    }
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


# --- installed provenance (the reviewed AC8 receipt method, unchanged) --------------------


def checked_wheel_source(candidate: Path, wheel: Path, package: str) -> int:
    """Require the wheel's package Python files to equal the pinned source tree."""
    if package not in PACKAGES:
        raise ValueError(f"unexpected workspace wheel package: {package}")
    root = candidate.resolve(strict=True)
    source = (root / package.replace("_", "-") / "src" / package).resolve(strict=True)
    if not source.is_relative_to(root):
        raise ValueError(f"package source escaped candidate: {package}")
    source_files = {}
    for path in source.rglob("*.py"):
        if not path.resolve(strict=True).is_relative_to(source):
            raise ValueError(f"package Python file escaped candidate: {path}")
        source_files[path.relative_to(source).as_posix()] = path
    with zipfile.ZipFile(wheel) as archive:
        prefix = package + "/"
        wheel_names = [
            name.removeprefix(prefix)
            for name in archive.namelist()
            if name.startswith(prefix) and name.endswith(".py")
        ]
        if not wheel_names or len(wheel_names) != len(set(wheel_names)):
            raise ValueError(f"wheel Python file inventory is empty or duplicated: {wheel}")
        if set(wheel_names) != set(source_files):
            raise ValueError(f"wheel/source Python file inventory differs: {package}")
        # [LAW:one-source-of-truth] The clean candidate bytes are the build provenance.
        for name in wheel_names:
            if archive.read(prefix + name) != source_files[name].read_bytes():
                raise ValueError(f"wheel/source Python file bytes differ: {package}/{name}")
    return len(wheel_names)


def require_full_head(expected_head: str) -> None:
    """Pure: the pin must be a full lowercase Git SHA before anything is run against it."""
    if len(expected_head) != 40 or any(c not in "0123456789abcdef" for c in expected_head):
        raise ValueError("expected-head must be a full lowercase Git SHA")


def require_clean_pinned(head: str, status: str, expected_head: str) -> None:
    """Pure verdict on what git reported: the pinned head, and nothing modified."""
    if head != expected_head or status:
        raise ValueError("candidate HEAD differs from pin or tree is not clean")


def checked_candidate(candidate: Path, venv: Path, expected_head: str) -> tuple[Path, Path, Path]:
    """Require a clean pinned tree and a selected installed Python before effects."""
    root = candidate.resolve(strict=True)
    require_full_head(expected_head)
    head = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain"],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    ).stdout.strip()
    require_clean_pinned(head, status, expected_head)
    installed = venv.resolve(strict=True)
    python = installed / "bin" / "python"
    if not python.is_file():
        raise ValueError("selected installed Python is missing")
    return root, installed, python


def installed_origins(venv: Path, wheels: list[dict[str, str]]) -> dict[str, dict[str, object]]:
    """Check every workspace Python file against wheel bytes and installed RECORD."""
    site = venv.resolve(strict=True)
    result: dict[str, dict[str, object]] = {}
    for item in wheels:
        wheel = Path(item["path"]).resolve(strict=True)
        package = wheel.name.split("-", 1)[0]
        dist = importlib.metadata.distribution(package)
        files = dist.files
        if files is None:
            raise ValueError(f"installed RECORD missing: {package}")
        recorded = {str(member): member for member in files}
        record_names = [name for name in recorded if name.endswith(".dist-info/RECORD")]
        if len(record_names) != 1:
            raise ValueError(f"installed RECORD count differs: {package}")
        record_path = Path(dist.locate_file(recorded[record_names[0]])).resolve(strict=True)
        if not record_path.is_relative_to(site) or "site-packages" not in record_path.parts:
            raise ValueError(f"installed RECORD escaped venv: {record_path}")
        checked: list[str] = []
        with zipfile.ZipFile(wheel) as archive:
            members = [
                name
                for name in archive.namelist()
                if name.startswith(package + "/") and name.endswith(".py")
            ]
            if not members:
                raise ValueError(f"wheel has no package Python files: {wheel}")
            recorded_python = {
                name for name in recorded if name.startswith(package + "/") and name.endswith(".py")
            }
            if set(members) != recorded_python:
                raise ValueError(f"installed Python file inventory differs from wheel: {package}")
            for name in members:
                entry = recorded.get(name)
                if entry is None or entry.hash is None or entry.hash.mode != "sha256":
                    raise ValueError(f"installed RECORD has no SHA256 for {name}")
                origin = Path(dist.locate_file(entry)).resolve(strict=True)
                if not origin.is_relative_to(site) or "site-packages" not in origin.parts:
                    raise ValueError(f"installed module escaped venv: {origin}")
                actual = hashlib.sha256(origin.read_bytes()).digest()
                record_digest = base64.urlsafe_b64decode(
                    entry.hash.value + "=" * (-len(entry.hash.value) % 4)
                )
                if actual != record_digest or actual != hashlib.sha256(archive.read(name)).digest():
                    raise ValueError(f"installed module differs from RECORD or wheel: {name}")
                checked.append(str(origin))
        imported = importlib.import_module(package)
        imported_path = Path(imported.__file__).resolve(strict=True)
        expected_init = Path(dist.locate_file(recorded[package + "/__init__.py"])).resolve(
            strict=True
        )
        if imported_path != expected_init or any(
            Path(location).resolve(strict=True) != expected_init.parent
            for location in imported.__path__
        ):
            raise ValueError(f"imported package origin differs from verified files: {package}")
        result[package] = {
            "record_path": str(record_path),
            "record_sha256": sha256(record_path),
            "python_files_checked": len(checked),
            "verified_files": sorted(checked),
        }
    return result


def checked_startup_hooks(data: dict[str, object], venv: Path) -> dict[str, object]:
    """Pin venv site startup code before its Python interpreter can execute."""
    hooks = data.get("startup_hooks")
    if not isinstance(hooks, dict) or set(hooks) != {"site_packages", "files", "absent"}:
        raise ValueError("installation receipt needs exact startup_hooks object")
    site_name = hooks["site_packages"]
    files = hooks["files"]
    absent = hooks["absent"]
    if (
        not isinstance(site_name, str)
        or not isinstance(files, dict)
        or set(files) != {"_virtualenv.pth", "_virtualenv.py"}
        or not isinstance(absent, list)
        or len(absent) != 2
        or not all(isinstance(name, str) for name in absent)
        or set(absent) != {"sitecustomize.py", "usercustomize.py"}
    ):
        raise ValueError("installation receipt has malformed startup hook pins")
    venv_root = venv.resolve(strict=True)
    sites = list(venv_root.glob("lib/python*/site-packages"))
    if len(sites) != 1 or not sites[0].is_dir():
        raise ValueError("selected venv needs exactly one site-packages directory")
    site = sites[0].resolve(strict=True)
    if site_name != str(site) or not site.is_relative_to(venv_root):
        raise ValueError("startup hook site-packages path differs from selected venv")
    if {path.name for path in site.glob("*.pth")} != {"_virtualenv.pth"}:
        raise ValueError("venv startup .pth inventory differs from receipt")
    verified_files: dict[str, str] = {}
    for name, expected_hash in files.items():
        path = site / name
        if (
            not isinstance(expected_hash, str)
            or len(expected_hash) != 64
            or any(char not in "0123456789abcdef" for char in expected_hash)
            or not path.is_file()
            or path.resolve(strict=True) != path
            or sha256(path) != expected_hash
        ):
            raise ValueError(f"venv startup hook differs from receipt: {name}")
        verified_files[name] = expected_hash
    for name in absent:
        path = site / name
        if path.exists() or path.is_symlink():
            raise ValueError(f"unexpected venv startup customization: {name}")
    return {"site_packages": str(site), "files": verified_files, "absent": absent}


def checked_provenance(
    receipt: Path,
    candidate: Path,
    venv: Path,
    expected_head: str,
    origins: dict[str, dict[str, object]] | None = None,
) -> dict[str, object]:
    """Bind the reviewed candidate, wheel files and installed module bytes."""
    data = json.loads(receipt.read_text(encoding="utf-8"))
    if (
        data.get("schema") != 2
        or data.get("candidate") != str(candidate)
        or data.get("candidate_head") != expected_head
        or data.get("venv") != str(venv)
    ):
        raise ValueError("installation receipt does not match candidate, HEAD or venv")
    # [LAW:no-ambient-temporal-coupling] Parent checks startup code before Popen.
    data["startup_hooks_verified"] = checked_startup_hooks(data, venv)
    wheels = data.get("wheels")
    if not isinstance(wheels, list) or len(wheels) != len(PACKAGES):
        raise ValueError("installation receipt needs seven pinned package wheels")
    names = set()
    source_counts: dict[str, int] = {}
    for item in wheels:
        if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
            raise ValueError("installation receipt has malformed wheel entry")
        path = Path(item["path"]).resolve(strict=True)
        package = path.name.split("-", 1)[0]
        names.add(package)
        if path.suffix != ".whl" or sha256(path) != item["sha256"]:
            raise ValueError(f"wheel hash differs from installation receipt: {path}")
        source_counts[package] = checked_wheel_source(candidate, path, package)
    if names != PACKAGES:
        raise ValueError("installation receipt must pin all seven harness package wheels")
    recorded = data.get("installed_record_sha256")
    if not isinstance(recorded, dict) or set(recorded) != PACKAGES:
        raise ValueError("installation receipt must pin seven installed RECORD hashes")
    if origins is not None:
        actual = {name: item["record_sha256"] for name, item in origins.items()}
        if recorded != actual:
            raise ValueError("installed RECORD hashes differ from installation receipt")
    data["source_python_files_checked"] = source_counts
    return data


def interpreter_evidence(venv: Path, candidate: Path) -> dict[str, object]:
    """The exact interpreter and import path of this process, refused unless installed-only.

    `-I` must be in force, the prefix must be the selected venv, and every `sys.path`
    entry must lie in the venv or the base interpreter's own library; nothing may come
    from the candidate checkout or an environment variable.
    """
    venv_root = venv.resolve(strict=True)
    base = Path(sys.base_prefix).resolve(strict=True)
    entries = [str(Path(entry).resolve()) for entry in sys.path if entry]
    foreign = [
        entry
        for entry in entries
        if Path(entry).is_relative_to(candidate)
        or not (Path(entry).is_relative_to(venv_root) or Path(entry).is_relative_to(base))
    ]
    if (
        Path(sys.prefix).resolve() != venv_root
        or not sys.flags.isolated
        or not sys.flags.no_user_site
        or "PYTHONPATH" in os.environ
        or foreign
    ):
        raise ValueError(f"child is not an isolated installed interpreter: foreign={foreign}")
    return {
        "executable": sys.executable,
        "prefix": sys.prefix,
        "base_prefix": sys.base_prefix,
        "version": sys.version,
        "isolated": sys.flags.isolated,
        "no_user_site": sys.flags.no_user_site,
        "sys_path": list(sys.path),
    }


def loaded_harness_origins(verified: set[str]) -> dict[str, str]:
    """Every loaded `harness_*` module's origin must be a RECORD-verified installed file."""
    origins: dict[str, str] = {}
    for name, module in sorted(sys.modules.items()):
        if name.split(".", 1)[0] not in PACKAGES or module is None:
            continue
        spec = getattr(module, "__spec__", None)
        origin = getattr(spec, "origin", None)
        if origin is None or str(Path(origin).resolve()) not in verified:
            raise ValueError(f"loaded module not from a verified installed file: {name}")
        origins[name] = str(Path(origin).resolve())
    return origins


def installed_prover(
    candidate: Path, venv: Path, expected_head: str, receipt: Path
) -> Callable[[], dict[str, object]]:
    def prove() -> dict[str, object]:
        root, installed, _python = checked_candidate(candidate, venv, expected_head)
        interpreter = interpreter_evidence(installed, root)
        provenance = checked_provenance(receipt, root, installed, expected_head)
        origins = installed_origins(installed, provenance["wheels"])
        checked_provenance(receipt, root, installed, expected_head, origins)
        return {
            "interpreter": interpreter,
            "installation_receipt_sha256": sha256(receipt),
            "installed_origins": origins,
            "startup_hooks_verified": provenance["startup_hooks_verified"],
        }

    return prove


_HEX = frozenset("0123456789abcdef")

# [LAW:one-source-of-truth] The floor comes from the real prover: `installed_origins` imports
# every one of the seven harness packages, so any child that has proved itself has at least
# this many `harness_*` modules in `sys.modules` BEFORE its phase body starts (a package
# is itself a loaded module). An empty or tiny count contradicts the installed path.
MIN_LOADED_HARNESS_MODULES = len(PACKAGES)


def loaded_modules_meet_floor(value: object) -> bool:
    """Pure: a recorded loaded-`harness_*`-module count that reaches the prover's floor.

    An exact int (never a bool) of at least `MIN_LOADED_HARNESS_MODULES`: every child that has
    proved itself has all seven packages loaded before its phase body starts.
    """
    count = exact_int(value)
    return count is not None and count >= MIN_LOADED_HARNESS_MODULES


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in _HEX for c in value)


def exact_int(value: object) -> int | None:
    """An int that is not a bool: `True == 1` must never satisfy a numeric proof."""
    return value if type(value) is int else None


def dict_or_empty(value: object) -> dict[str, Any]:
    """A mapping as itself; anything else reads as empty ONLY inside a behaviour check,
    which then fails, never as a proof (proofs are parsed by the functions below)."""
    return value if isinstance(value, dict) else {}  # pyright: ignore[reportUnknownVariableType]


WORKSPACE_DIST_VERSION = "0.0.0"
"""The version of every workspace wheel, hence of every installed `<package>-<version>.dist-info`.

Grounded in the seven `harness-*/pyproject.toml` versions and the RECORD layout `installed_origins`
reads (`dist.files` of the installed distribution); a pure test pins it to those files."""


def _canonical(value: object) -> Path | None:
    """`value` as a path only if it is an absolute, already canonical spelling.

    `installed_origins` emits `Path(...).resolve(strict=True)`: no `..`, no symlink component, no
    repeated separator. A recorded path that differs from its own resolution therefore is not
    something the prover emitted (a traversal, or a symlink that may lead outside), and lexical
    containment of such a spelling would prove nothing about where the file effectively is.
    """
    if not isinstance(value, str) or not os.path.isabs(value):
        return None
    return Path(value) if os.path.realpath(value) == value else None


def _package_origin(
    package: str, entry: dict[str, Any], root: Path | None
) -> tuple[Path | None, set[str]]:
    """Parse ONE package's emitted origin into its site-packages root, or the reasons it is not.

    [LAW:parse-dont-validate] The single owner of path normalisation and layout. Layout rule, from
    `installed_origins`: RECORD is `<site-packages>/<package>-<version>.dist-info/RECORD` and every
    verified file is a `.py` under `<site-packages>/<package>/`, all inside the interpreter's
    (resolved) prefix and all in canonical spelling.
    """
    reasons: set[str] = set()
    site: Path | None = None
    record = _canonical(entry.get("record_path"))
    if record is not None:
        candidate = record.parent.parent
        expected = candidate / f"{package}-{WORKSPACE_DIST_VERSION}.dist-info" / "RECORD"
        if (
            candidate.name == "site-packages"
            and record == expected
            and (root is None or candidate.is_relative_to(root))
        ):
            site = candidate
    if site is None:
        reasons.add("origin-record-path-invalid")
    if not is_sha256(entry.get("record_sha256")):
        reasons.add("origin-record-digest-invalid")
    files = entry.get("verified_files")
    checked = exact_int(entry.get("python_files_checked"))
    files_ok = (
        site is not None
        and isinstance(files, list)
        and bool(files)
        and all(isinstance(f, str) for f in files)  # pyright: ignore[reportUnknownVariableType]
        and files == sorted(set(files))  # pyright: ignore[reportUnknownArgumentType]
        and all(
            (path := _canonical(f)) is not None
            and path.suffix == ".py"
            and path.is_relative_to(site / package)
            for f in files  # pyright: ignore[reportUnknownVariableType]
        )
    )
    if not files_ok:
        reasons.add("origin-files-invalid")
    elif checked is None or checked < 1 or checked != len(files):  # pyright: ignore[reportUnknownArgumentType]
        reasons.add("origin-count-invalid")
    return site, reasons


def origin_reasons(origins: object, prefix: object) -> tuple[str, ...]:
    """Parse every emitted package origin as a proving value, not just a package name.

    All seven packages must parse and share ONE site-packages root under the interpreter's
    prefix. The prefix is resolved before comparison, so a genuine symlinked prefix alias is
    accepted while a recorded path that is itself a non-canonical spelling is not.
    """
    if not isinstance(origins, dict) or set(dict_or_empty(origins)) != PACKAGES:
        return ("origins-incomplete",)
    root = (
        Path(os.path.realpath(prefix))
        if isinstance(prefix, str) and os.path.isabs(prefix)
        else None
    )
    reasons: set[str] = set()
    sites: set[Path] = set()
    for package, item in sorted(dict_or_empty(origins).items()):
        if not isinstance(item, dict):
            reasons.add("origin-malformed")
            continue
        site, problems = _package_origin(package, dict_or_empty(item), root)
        reasons |= problems
        if site is not None:
            sites.add(site)
    if len(sites) > 1:
        reasons.add("origin-site-root-inconsistent")
    return tuple(sorted(reasons))


def provenance_reasons(provenance: object, expected_receipt: str) -> tuple[str, ...]:
    """Why a child provenance record is not proof of an installed, isolated child."""
    if not isinstance(provenance, dict):
        return ("provenance-missing",)
    data = dict_or_empty(provenance)
    reasons: list[str] = []
    receipt = data.get("installation_receipt_sha256")
    if receipt is None:
        reasons.append("receipt-missing")
    elif not is_sha256(receipt):
        reasons.append("receipt-malformed")
    elif receipt != expected_receipt:
        reasons.append("receipt-mismatch")
    interpreter = data.get("interpreter")
    prefix: object = None
    if not isinstance(interpreter, dict):
        reasons.append("interpreter-missing")
    else:
        flags = dict_or_empty(interpreter)
        if exact_int(flags.get("isolated")) != 1:
            reasons.append("not-isolated")
        if exact_int(flags.get("no_user_site")) != 1:
            reasons.append("not-no-user-site")
        prefix = flags.get("prefix")
        if not (isinstance(prefix, str) and Path(prefix).is_absolute()):
            reasons.append("interpreter-prefix-invalid")
    reasons.extend(origin_reasons(data.get("installed_origins"), prefix))
    return tuple(reasons)
