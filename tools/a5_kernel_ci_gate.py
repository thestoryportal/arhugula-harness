"""Fail-closed kernel-venue gate for the A5 Landlock read-boundary canaries.

The package suite skips the SUPPORTED_HOST canaries on a host the launcher refuses and the
UNSUPPORTED_HOST refusal tests on a host it accepts, so a green suite proves neither venue
on its own. Each `package-tests` matrix leg therefore runs two subcommands around the
unchanged suite:

* ``preflight`` (before pytest) runs the REAL launcher host check on the runner's actual
  architecture and measured Landlock ABI, binds the result to image, kernel, run and commit
  identity, and fails unless the allocation is exactly the venue it was selected as.
* ``check`` (after pytest) measures the same runner and checkout again, requires the
  preflight record to describe exactly them, re-judges it against the expectations it
  loads now, then reads the leg's fresh JUnit by exact node ID and fails unless every
  guarded ID appears exactly once with the outcome its venue requires.

The guarded IDs, the venues and the git blobs defining them live in
`tools/a5_kernel_ci_expectations.json`. Editing a bound file makes that file stale, and
the gate fails until the expectations are reviewed again.

Both subcommands write their JSON record before exiting, so a failed leg still publishes
its evidence. Exit 0 = venue proved, 1 = venue not proved (the record lists every
problem), 2 = unusable expectations file. They are separate required steps, so neither
can turn a failed pytest step into success.
"""

from __future__ import annotations

import argparse
import enum
import hashlib
import json
import os
import platform
import re
import shutil
import socket
import stat
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from collections.abc import Collection, Iterable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import asdict, dataclass, fields
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any, cast
from urllib.parse import quote, unquote

ROOT = Path(__file__).resolve().parents[1]
EXPECTATIONS = ROOT / "tools" / "a5_kernel_ci_expectations.json"

# Environment the workflow binds: `changes`-job identity plus the runner's own metadata.
_BINDING_ENV = (
    "CI_HEAD",
    "CI_BASE",
    "CI_TESTED",
    "GITHUB_WORKFLOW",
    "GITHUB_RUN_ID",
    "GITHUB_RUN_ATTEMPT",
    "ImageOS",
    "ImageVersion",
    "RUNNER_NAME",
    "RUNNER_ENVIRONMENT",
)


class ExpectationsError(ValueError):
    """The reviewed expectations file cannot be read as expectations."""


@dataclass(frozen=True)
class NodeId:
    """A module-level pytest node ID, which JUnit splits into classname and name."""

    path: str
    name: str

    @classmethod
    def parse(cls, node_id: str) -> NodeId:
        path, sep, name = node_id.partition("::")
        if not sep or "::" in name or not path.endswith(".py") or not name:
            raise ExpectationsError(f"not a module-level node ID: {node_id!r}")
        return cls(path, name)

    @property
    def junit_key(self) -> tuple[str, str]:
        return (self.path.removesuffix(".py").replace("/", "."), self.name)

    def __str__(self) -> str:
        return f"{self.path}::{self.name}"


@dataclass(frozen=True)
class Supported:
    """The launcher must accept this runner."""

    image_os: str


@dataclass(frozen=True)
class Refused:
    """The launcher must refuse this runner's measured ABI, with exactly this reason."""

    image_os: str
    abi: int
    refusal: str


Venue = Supported | Refused


@dataclass(frozen=True)
class Expectations:
    bound_blobs: Mapping[str, str]
    venues: Mapping[str, Venue]
    supported_host_ids: tuple[NodeId, ...]
    unsupported_host_ids: tuple[NodeId, ...]


def parse_expectations(raw: Mapping[str, Any]) -> Expectations:
    # [LAW:parse-dont-validate] The reviewed file crosses here once; everything downstream
    # takes `Expectations` and never re-checks its shape.
    try:
        venues: dict[str, Venue] = {}
        for venue_id, spec in raw["venues"].items():
            match spec["kind"]:
                case "supported":
                    venues[venue_id] = Supported(str(spec["image_os"]))
                case "refused":
                    venues[venue_id] = Refused(
                        str(spec["image_os"]), int(spec["abi"]), str(spec["refusal"])
                    )
                case other:
                    raise ExpectationsError(f"venue {venue_id!r} has unknown kind {other!r}")
        supported = tuple(NodeId.parse(i) for i in raw["supported_host_ids"])
        unsupported = tuple(NodeId.parse(i) for i in raw["unsupported_host_ids"])
        blobs = {str(path): str(blob) for path, blob in raw["bound_blobs"].items()}
    except ExpectationsError:
        raise
    except (KeyError, TypeError, AttributeError, ValueError) as exc:
        raise ExpectationsError(f"malformed expectations: {exc!r}") from exc
    every = supported + unsupported
    if len(set(every)) != len(every):
        raise ExpectationsError("a guarded node ID is listed more than once")
    return Expectations(blobs, venues, supported, unsupported)


# --- Q0 inputs ----------------------------------------------------------------------

# Pins chosen from signed upstream artifacts and reviewed before Q0. Nothing here has a
# default and nothing is taken from a run: base package set, closure, host package
# versions, mounts and root manifests are outputs Q0 observes and Q1 freezes.
GUEST_PACKAGES = ("git",)
LAUNCHER_PACKAGES = ("virtme-ng", "qemu-system-x86", "virtiofsd")
VIRTME_NG_VERSION = "1.40-2"
GUEST_KERNEL_CONFIG = ROOT / "tools" / "a5_guest_kernel.config"

_SHA256 = re.compile(r"[0-9a-f]{64}")
_FINGERPRINT = re.compile(r"[0-9A-F]{40}")
_SNAPSHOT_ID = re.compile(r"[0-9]{8}T[0-9]{6}Z")
_VERSION = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")
_CPYTHON_312 = re.compile(r"3\.12\.[0-9]+")
_TARBALL = re.compile(r"ubuntu-base-[0-9.]+-base-amd64\.tar\.gz")


@dataclass(frozen=True)
class BaseInput:
    release_dir: str
    tarball: str
    tarball_sha256: str
    sha256sums_sha256: str
    signing_key: str


@dataclass(frozen=True)
class ArchiveInput:
    snapshot_id: str
    suite: str
    components: tuple[str, ...]
    signing_key: str


@dataclass(frozen=True)
class KernelInput:
    tarball_sha256: str
    autosigner_key: str
    developer_key: str
    config_sha256: str


@dataclass(frozen=True)
class Inputs:
    base: BaseInput
    archive: ArchiveInput
    guest_packages: tuple[str, ...]
    launcher_packages: tuple[str, ...]
    virtme_ng_version: str
    uv_version: str
    cpython: str
    kernel: KernelInput
    sha256: str  # INPUTS_SHA256: sha256 of the canonical JSON of the raw `inputs` section


def _section(raw: object, name: str, keys: Sequence[str]) -> Mapping[str, object]:
    if not isinstance(raw, Mapping):
        raise ExpectationsError(f"inputs {name} is absent or not an object")
    section = cast(Mapping[str, object], raw)
    if set(section) != set(keys):
        raise ExpectationsError(f"inputs {name} has keys {sorted(section)}, needs {sorted(keys)}")
    return section


def _text(section: Mapping[str, object], key: str, form: re.Pattern[str] | None = None) -> str:
    value = section[key]
    if not isinstance(value, str) or not value:
        raise ExpectationsError(f"inputs field {key} is empty or not a string")
    if form is not None and not form.fullmatch(value):
        raise ExpectationsError(f"inputs field {key}={value!r} is not a {form.pattern}")
    return value


def _names(section: Mapping[str, object], key: str) -> tuple[str, ...]:
    value = section[key]
    if not isinstance(value, list) or not value:
        raise ExpectationsError(f"inputs field {key} is empty or not a list")
    names = tuple(cast(list[object], value))
    if not all(isinstance(n, str) and n for n in names) or len(set(names)) != len(names):
        raise ExpectationsError(f"inputs field {key} needs distinct non-empty names")
    return cast(tuple[str, ...], names)


def inputs_sha256(raw_inputs: Mapping[str, object]) -> str:
    canonical = json.dumps(raw_inputs, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()


def parse_inputs(raw: object) -> Inputs:
    # [LAW:parse-dont-validate] Every subcommand refuses a file whose Q0 inputs are absent,
    # incomplete or empty; there is no fallback value for any field.
    top = _section(
        raw, "section", ("base", "archive", "guest_packages", "launcher", "interpreter", "kernel")
    )
    base = _section(
        top["base"],
        "base",
        ("release_dir", "tarball", "tarball_sha256", "sha256sums_sha256", "signing_key"),
    )
    archive = _section(
        top["archive"], "archive", ("snapshot_id", "suite", "components", "signing_key")
    )
    launcher = _section(top["launcher"], "launcher", ("packages", "virtme_ng"))
    interpreter = _section(top["interpreter"], "interpreter", ("uv", "cpython"))
    kernel = _section(
        top["kernel"],
        "kernel",
        ("tarball_sha256", "autosigner_key", "developer_key", "config_sha256"),
    )
    release_dir = _text(base, "release_dir")
    if not (release_dir.startswith("https://") and release_dir.endswith("/")):
        raise ExpectationsError(f"inputs base release_dir {release_dir!r} is not an https dir")
    if (guest := _names(top, "guest_packages")) != GUEST_PACKAGES:
        raise ExpectationsError(f"inputs guest_packages {list(guest)} must be exactly ['git']")
    if (packages := _names(launcher, "packages")) != LAUNCHER_PACKAGES:
        raise ExpectationsError(f"inputs launcher packages {list(packages)} are not the plan's")
    if (virtme_ng := _text(launcher, "virtme_ng")) != VIRTME_NG_VERSION:
        raise ExpectationsError(f"inputs virtme_ng {virtme_ng!r} is not {VIRTME_NG_VERSION}")
    return Inputs(
        base=BaseInput(
            release_dir,
            _text(base, "tarball", _TARBALL),
            _text(base, "tarball_sha256", _SHA256),
            _text(base, "sha256sums_sha256", _SHA256),
            _text(base, "signing_key", _FINGERPRINT),
        ),
        archive=ArchiveInput(
            _text(archive, "snapshot_id", _SNAPSHOT_ID),
            _text(archive, "suite"),
            _names(archive, "components"),
            _text(archive, "signing_key", _FINGERPRINT),
        ),
        guest_packages=guest,
        launcher_packages=packages,
        virtme_ng_version=virtme_ng,
        uv_version=_text(interpreter, "uv", _VERSION),
        cpython=_text(interpreter, "cpython", _CPYTHON_312),
        kernel=KernelInput(
            _text(kernel, "tarball_sha256", _SHA256),
            _text(kernel, "autosigner_key", _FINGERPRINT),
            _text(kernel, "developer_key", _FINGERPRINT),
            _text(kernel, "config_sha256", _SHA256),
        ),
        sha256=inputs_sha256(top),
    )


def kernel_config_problems(config: str) -> list[str]:
    """Judge the final guest .config before boot: no module loading, so no module share."""
    lines = config.splitlines()
    problems = [
        f"guest .config sets {line!r}" for line in lines if line.startswith("CONFIG_MODULES=")
    ]
    if "# CONFIG_MODULES is not set" not in lines:
        problems.append("guest .config does not record CONFIG_MODULES as unset")
    return problems


# --- preflight ----------------------------------------------------------------------


@dataclass(frozen=True)
class HostReport:
    """What the real launcher check said about this runner."""

    machine: str
    abi: int
    refusal: str | None  # None: the launcher accepted the host


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def judge_preflight(
    venue: Venue,
    host: HostReport,
    env: Mapping[str, str],
    blobs: Mapping[str, str | None],
    expected_blobs: Mapping[str, str],
    checked_out: str,
) -> list[str]:
    problems = [f"binding {name} is unset" for name in _BINDING_ENV if not env.get(name)]
    if env.get("ImageOS") and env["ImageOS"] != venue.image_os:
        problems.append(f"ImageOS {env['ImageOS']!r} is not this venue's {venue.image_os!r}")
    if env.get("CI_TESTED") and checked_out != env["CI_TESTED"]:
        problems.append(f"checked-out {checked_out} is not the bound tested {env['CI_TESTED']}")
    for path in sorted(expected_blobs.keys() | blobs.keys()):
        if (got := blobs.get(path)) != (want := expected_blobs.get(path)):
            problems.append(f"{path} is blob {got}, expectations bind {want}: stale")
    match venue:
        case Supported():
            if host.refusal is not None:
                problems.append(f"launcher refused the supported venue: {host.refusal}")
        case Refused(abi=abi, refusal=refusal):
            if host.abi != abi:
                problems.append(f"measured Landlock ABI {host.abi}, venue requires exactly {abi}")
            if host.refusal != refusal:
                problems.append(f"launcher said {host.refusal!r}, venue requires {refusal!r}")
    return problems


def _measure_host() -> HostReport:
    from harness_runtime.lifecycle import cli_read_boundary as boundary

    machine, abi = platform.machine(), boundary._query_abi()  # pyright: ignore[reportPrivateUsage]
    # [LAW:single-enforcer] The launcher's own step-2 check decides acceptance, fed the
    # one measured report, so the recorded ABI and the decision cannot disagree.
    try:
        boundary.require_supported_abi(machine, lambda: abi)
    except boundary.LauncherRefusalError as refusal:
        return HostReport(machine, abi, str(refusal))
    return HostReport(machine, abi, None)


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


@dataclass(frozen=True)
class Leg:
    """The runner and checkout one job runs on, constant across its steps."""

    host: HostReport
    kernel: str
    os_release: str
    checked_out: str
    parents: tuple[str, ...]


def _measure_leg() -> Leg:
    # [LAW:one-source-of-truth] Both subcommands measure the leg here, so the record
    # preflight writes and the facts check re-measures are the same kind of map.
    return Leg(
        _measure_host(),
        platform.release(),
        platform.freedesktop_os_release().get("PRETTY_NAME", ""),
        _git("rev-parse", "HEAD"),
        tuple(_git("rev-list", "--parents", "-n", "1", "HEAD").split()[1:]),
    )


def _read_blob(path: Path) -> str | None:
    return git_blob(path.read_bytes()) if path.is_file() else None


def preflight(venue_id: str, expectations: Expectations, raw_sha256: str) -> dict[str, Any]:
    venue = expectations.venues[venue_id]
    started_at = datetime.now(UTC).isoformat()
    env = {name: os.environ.get(name, "") for name in _BINDING_ENV}
    leg = _measure_leg()
    host = leg.host
    blobs = {p: _read_blob(ROOT / p) for p in expectations.bound_blobs}
    return {
        "venue": venue_id,
        "started_at": started_at,
        "host": {
            "machine": host.machine,
            "landlock_abi": host.abi,
            "launcher": "accepted" if host.refusal is None else "refused",
            "refusal": host.refusal,
            "kernel": leg.kernel,
            "os": leg.os_release,
        },
        "binding": env,
        "checked_out": leg.checked_out,
        "parents": list(leg.parents),
        "blobs": blobs,
        "expectations_sha256": raw_sha256,
        "problems": judge_preflight(
            venue, host, env, blobs, expectations.bound_blobs, leg.checked_out
        ),
    }


# --- check --------------------------------------------------------------------------


class PreflightError(ValueError):
    """The preflight record is not a complete record of one preflight."""


@dataclass(frozen=True)
class PreflightRecord:
    venue: str
    started_at: datetime
    leg: Leg
    binding: Mapping[str, str]
    blobs: Mapping[str, str | None]
    expectations_sha256: str
    problems: tuple[str, ...]


def _typed[T](raw: Mapping[str, Any], key: str, kind: type[T]) -> T:
    if type(value := raw[key]) is not kind:
        raise PreflightError(f"{key} is {value!r}, not {kind.__name__}")
    return value


def _strings(raw: Mapping[str, Any], key: str) -> tuple[str, ...]:
    items = cast(list[Any], _typed(raw, key, list))
    if any(type(item) is not str for item in items):
        raise PreflightError(f"{key} {items!r} is not a list of strings")
    return tuple(items)


def _blob(value: Any) -> str | None:
    if value is not None and type(value) is not str:
        raise PreflightError(f"blob {value!r} is neither a git blob nor absent")
    return value


def parse_preflight(raw: Any) -> PreflightRecord:
    # [LAW:parse-dont-validate] A record missing any fact preflight writes is refused here,
    # so `check` never mistakes an absent host, binding or blob map for a passing one.
    try:
        host = cast(dict[str, Any], _typed(raw, "host", dict))
        refusal = None if host["refusal"] is None else _typed(host, "refusal", str)
        launcher = _typed(host, "launcher", str)
        if launcher != ("accepted" if refusal is None else "refused"):
            raise PreflightError(f"launcher {launcher!r} contradicts refusal {refusal!r}")
        started_at = datetime.fromisoformat(_typed(raw, "started_at", str))
        if started_at.tzinfo is None:
            raise PreflightError(f"started_at {started_at} has no timezone")
        binding = cast(dict[str, Any], _typed(raw, "binding", dict))
        blobs = cast(dict[str, Any], _typed(raw, "blobs", dict))
        return PreflightRecord(
            venue=_typed(raw, "venue", str),
            started_at=started_at,
            leg=Leg(
                HostReport(
                    _typed(host, "machine", str), _typed(host, "landlock_abi", int), refusal
                ),
                _typed(host, "kernel", str),
                _typed(host, "os", str),
                _typed(raw, "checked_out", str),
                _strings(raw, "parents"),
            ),
            binding={name: _typed(binding, name, str) for name in _BINDING_ENV},
            blobs={path: _blob(blob) for path, blob in blobs.items()},
            expectations_sha256=_typed(raw, "expectations_sha256", str),
            problems=_strings(raw, "problems"),
        )
    except PreflightError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        raise PreflightError(f"incomplete preflight record: {exc!r}") from exc


class Status(enum.Enum):
    PASSED = "passed"
    SKIPPED = "skipped"
    XFAILED = "xfailed"
    FAILED = "failed"
    ERROR = "error"


@dataclass(frozen=True)
class Outcome:
    status: Status
    message: str


@dataclass(frozen=True)
class Required:
    status: Status
    reason: str  # must appear in the outcome message; "" accepts any


class JUnitError(ValueError):
    """The JUnit file is missing, malformed or not from this leg's pytest run."""


def _outcome(case: ET.Element) -> Outcome:
    # A failure or error (setup/call/teardown) outranks a skip on the same testcase.
    for tag, status in (("error", Status.ERROR), ("failure", Status.FAILED)):
        if (element := case.find(tag)) is not None:
            return Outcome(status, element.get("message", ""))
    if (skipped := case.find("skipped")) is not None:
        status = Status.XFAILED if skipped.get("type") == "pytest.xfail" else Status.SKIPPED
        return Outcome(status, skipped.get("message", ""))
    return Outcome(Status.PASSED, "")


def parse_junit(text: str, not_before: datetime) -> dict[tuple[str, str], list[Outcome]]:
    """Every testcase outcome, keyed like `NodeId.junit_key`; duplicates are kept."""
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise JUnitError(f"malformed JUnit: {exc}") from exc
    suites = [root] if root.tag == "testsuite" else root.findall("testsuite")
    if not suites:
        raise JUnitError("JUnit has no testsuite")
    for suite in suites:
        try:
            stamp = datetime.fromisoformat(suite.get("timestamp", ""))
        except ValueError as exc:
            raise JUnitError(f"testsuite timestamp unreadable: {exc}") from exc
        if stamp.tzinfo is None or stamp < not_before:
            raise JUnitError(f"testsuite timestamp {stamp} predates this leg's preflight")
    outcomes: dict[tuple[str, str], list[Outcome]] = {}
    for suite in suites:
        for case in suite.iter("testcase"):
            key = (case.get("classname", ""), case.get("name", ""))
            outcomes.setdefault(key, []).append(_outcome(case))
    return outcomes


def required_outcomes(expectations: Expectations, venue: Venue) -> dict[NodeId, Required]:
    passed = Required(Status.PASSED, "")
    match venue:
        case Supported():
            positive, held = passed, Required(Status.SKIPPED, "")
            return {i: positive for i in expectations.supported_host_ids} | {
                i: held for i in expectations.unsupported_host_ids
            }
        case Refused(refusal=refusal):
            # Each canary must be held for the launcher's actual refusal, not for an
            # unrelated prerequisite that would also have skipped it.
            held = Required(Status.SKIPPED, refusal)
            return {i: held for i in expectations.supported_host_ids} | {
                i: passed for i in expectations.unsupported_host_ids
            }


def judge_outcomes(
    required: Mapping[NodeId, Required], outcomes: Mapping[tuple[str, str], Sequence[Outcome]]
) -> tuple[dict[str, str], list[str]]:
    observed: dict[str, str] = {}
    problems: list[str] = []
    for test_id, want in required.items():
        found = outcomes.get(test_id.junit_key, ())
        if len(found) != 1:
            observed[str(test_id)] = "missing" if not found else "duplicate"
            problems.append(f"{test_id}: {len(found)} JUnit testcases, exactly one required")
            continue
        [got] = found
        observed[str(test_id)] = got.status.value
        if got.status is not want.status or want.reason not in got.message:
            problems.append(
                f"{test_id}: {got.status.value} ({got.message!r}), required "
                f"{want.status.value}" + (f" for {want.reason!r}" if want.reason else "")
            )
    return observed, problems


def check(
    venue_id: str,
    expectations: Expectations,
    expectations_sha256: str,
    env: Mapping[str, str],
    leg: Leg,
    preflight_path: Path,
    junit_path: Path,
) -> dict[str, Any]:
    record: dict[str, Any] = {"venue": venue_id, "outcomes": {}}
    try:
        raw = preflight_path.read_bytes()
        record["preflight_sha256"] = hashlib.sha256(raw).hexdigest()
        prior = parse_preflight(json.loads(raw))
    except (OSError, ValueError) as exc:
        return record | {"problems": [f"preflight record unusable: {exc}"]}
    venue = expectations.venues[venue_id]
    # [LAW:single-enforcer] The recorded facts are re-judged by preflight's own rule against
    # the expectations loaded now, so a stale or edited record cannot carry a pass it did
    # not earn; a record that judged itself the same way contributes no duplicates.
    rejudged = judge_preflight(
        venue,
        prior.leg.host,
        prior.binding,
        prior.blobs,
        expectations.bound_blobs,
        prior.leg.checked_out,
    )
    problems = [f"preflight: {p}" for p in dict.fromkeys([*prior.problems, *rejudged])]
    if prior.venue != venue_id:
        problems.append(f"preflight is for venue {prior.venue!r}")
    if prior.expectations_sha256 != expectations_sha256:
        problems.append(
            f"preflight bound expectations {prior.expectations_sha256}, "
            f"check loaded {expectations_sha256}: stale"
        )
    # The runner, launcher decision and checkout are constant within one job, so a record
    # that is not this leg's measurement describes another host, commit or edit.
    if prior.leg != leg:
        problems.append(f"preflight recorded {prior.leg}, this leg measures {leg}")
    # Every binding is constant within one job, so any difference is another run, attempt,
    # commit or runner.
    problems += [
        f"preflight {name}={prior.binding[name]!r} is not this leg's"
        for name in _BINDING_ENV
        if prior.binding[name] != env.get(name)
    ]
    try:
        text = junit_path.read_text()
        record["junit_sha256"] = hashlib.sha256(text.encode()).hexdigest()
        outcomes = parse_junit(text, prior.started_at)
    except (OSError, ValueError) as exc:
        return record | {"problems": [*problems, f"JUnit not usable: {exc}"]}
    observed, outcome_problems = judge_outcomes(required_outcomes(expectations, venue), outcomes)
    return record | {"outcomes": observed, "problems": problems + outcome_problems}


# --- Q0 observation (host side) -----------------------------------------------------
#
# Provisional record contract from correction-8 (proposal 09276d9f):
# design.bindings_crossing_guest, guest_package_closure step 3h and
# qualification_sequence.Q0_observation. The guest `observe` producer and the CI job
# are not built yet, so nothing calls these outside their tests.

# The one binding.env schema: the host writer, the guest and these checks share it.
BINDING_ENV_KEYS = (
    "CI_HEAD",
    "CI_BASE",
    "CI_TESTED",
    "CI_PARENTS",
    "CI_EVENT",
    "CI_REF",
    "GITHUB_RUN_ID",
    "GITHUB_RUN_ATTEMPT",
    "GITHUB_WORKFLOW",
    "ImageOS",
    "ImageVersion",
    "RUNNER_NAME",
    "RUNNER_ENVIRONMENT",
    "GUEST_BZIMAGE_SHA256",
    "GUEST_CONFIG_SHA256",
    "GUEST_SOURCE_SHA256",
    "BASE_ROOTFS_SHA256",
    "INPUTS_SHA256",
    "HOST_JSON_SHA256",
    "STAGE_MANIFEST_SHA256",
    "HOST_ENV_SHA256",
    "INSTALL_NS_SHA256",
)
# What binds one observation to one run: the host's tested commit, run and attempt, and
# the reviewed inputs it was built from.
Q0_IDENTITY = ("CI_TESTED", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "INPUTS_SHA256")
# The guest's whole environment besides binding.env (pytest_and_aggregate.guest_workdir).
FIXED_GUEST_ENV = {
    "PATH": "/a5/venv/bin:/usr/bin:/bin",
    "VIRTUAL_ENV": "/a5/venv",
    "HOME": "/out/home",
    "TMPDIR": "/out/tmp",
    "COVERAGE_FILE": "/out/.coverage",
    "PYTHONNOUSERSITE": "1",
    "PYTHONDONTWRITEBYTECODE": "1",
    "LANG": "C.UTF-8",
}
# Hashes of host records written before binding.env; only the writer computes them.
DERIVED_BINDINGS = ("HOST_JSON_SHA256", "INSTALL_NS_SHA256")
_HEX64 = re.compile(r"[0-9a-f]{64}")


class Q0Error(ValueError):
    """A Q0 record is absent, not fresh, malformed or not bound to this run."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise Q0Error(f"{path.name} unreadable: {exc}") from exc


def _object(data: bytes, name: str) -> dict[str, Any]:
    try:
        raw = json.loads(data)
    except ValueError as exc:
        raise Q0Error(f"{name} is not JSON: {exc}") from exc
    if type(raw) is not dict:
        raise Q0Error(f"{name} is not a JSON object")
    return cast(dict[str, Any], raw)


def _hex64(raw: Mapping[str, Any], key: str, name: str) -> str:
    value = raw.get(key)
    if type(value) is not str or not _HEX64.fullmatch(value):
        raise Q0Error(f"{name} {key} {value!r} is not 64 lowercase hex")
    return value


def parse_binding_env(data: bytes) -> Mapping[str, str]:
    # [LAW:single-enforcer] Every key exactly once, nothing else, no empty value: a
    # missing, extra, repeated or malformed line fails here with no default.
    try:
        lines = data.decode().splitlines()
    except UnicodeDecodeError as exc:
        raise Q0Error(f"binding.env is not UTF-8: {exc}") from exc
    pairs = [line.partition("=") for line in lines]
    if any(not sep or not value for _, sep, value in pairs):
        raise Q0Error("binding.env has a line that is not KEY=VALUE")
    if sorted(key for key, _, _ in pairs) != sorted(BINDING_ENV_KEYS):
        raise Q0Error(f"binding.env keys {[key for key, _, _ in pairs]} are not the schema")
    env = {key: value for key, _, value in pairs}
    for key in BINDING_ENV_KEYS:
        if key.endswith("_SHA256"):
            _hex64(env, key, "binding.env")
    return env


def guest_env_problems(names: Iterable[str]) -> list[str]:
    """The isolation env-name check: exactly the binding.env schema plus the fixed set."""
    # [LAW:one-source-of-truth] Derived from BINDING_ENV_KEYS, so a name the schema drops
    # is refused here too; any token or runner name is simply outside the set.
    expected, actual = set(BINDING_ENV_KEYS) | FIXED_GUEST_ENV.keys(), set(names)
    return [f"guest environment lacks {name}" for name in sorted(expected - actual)] + [
        f"guest environment has {name} outside the allowlist" for name in sorted(actual - expected)
    ]


def _canonical(record: Mapping[str, Any]) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()


@dataclass(frozen=True)
class HostRecords[T]:
    """The host's binding records, in write order: each one names the hashes before it."""

    install_ns: T
    host_json: T
    binding_env: T
    host_stage: T


def host_records(
    values: Mapping[str, str],
    host: Mapping[str, Any],
    install: Mapping[str, Any],
    self_test: Mapping[str, Any],
    sentinel_sha256: Mapping[str, str],
) -> HostRecords[bytes]:
    """Compose install-ns.json, host.json, binding.env and host-stage.json from run facts."""
    supplied = sorted(values)
    if supplied != sorted(set(BINDING_ENV_KEYS) - set(DERIVED_BINDINGS)):
        raise Q0Error(f"binding values {supplied} are not the schema less {DERIVED_BINDINGS}")
    install_ns = _canonical({"install": install, "self_test": self_test})
    if "INSTALL_NS_SHA256" in host:
        raise Q0Error("host.json INSTALL_NS_SHA256 is derived, not supplied")
    host_json = _canonical({**host, "INSTALL_NS_SHA256": _sha256(install_ns)})
    # [LAW:no-ambient-temporal-coupling] binding.env is built from the bytes of the two
    # earlier records, so it cannot exist before them or name other bytes.
    env = {
        **values,
        "HOST_JSON_SHA256": _sha256(host_json),
        "INSTALL_NS_SHA256": _sha256(install_ns),
    }
    binding_env = "".join(f"{key}={env[key]}\n" for key in BINDING_ENV_KEYS).encode()
    # [LAW:single-enforcer] The writer's output passes the one parser or no record is
    # produced: a missing, empty, multi-line or malformed value fails here.
    parse_binding_env(binding_env)
    host_stage = _canonical(
        {"binding_env_sha256": _sha256(binding_env), "sentinel_sha256": dict(sentinel_sha256)}
    )
    return HostRecords(install_ns, host_json, binding_env, host_stage)


def write_host_records(records: HostRecords[bytes], paths: HostRecords[Path]) -> None:
    for field in fields(HostRecords):
        getattr(paths, field.name).write_bytes(getattr(records, field.name))


@dataclass(frozen=True)
class Q0Observation:
    identity: Mapping[str, str]
    binding_env_sha256: str
    install_ns_sha256: str
    sha256: str


def parse_observation(data: bytes) -> Q0Observation:
    # [LAW:parse-dont-validate] Q0 has no preflight, outcomes or verdict; a record missing
    # its identity or either binding hash is refused before anything compares it.
    raw = _object(data, "observation.json")
    identity = {key: raw.get(key) for key in Q0_IDENTITY}
    if any(type(value) is not str or not value for value in identity.values()):
        raise Q0Error(f"observation.json identity {identity!r} is incomplete")
    _hex64(raw, "INPUTS_SHA256", "observation.json")
    return Q0Observation(
        identity=cast(dict[str, str], identity),
        binding_env_sha256=_hex64(raw, "binding_env_sha256", "observation.json"),
        install_ns_sha256=_hex64(raw, "INSTALL_NS_SHA256", "observation.json"),
        sha256=_sha256(data),
    )


def read_fresh(path: Path, launched: Path) -> bytes:
    """The bytes of a regular file written no earlier than the pre-launch marker."""
    try:
        launched_ns = launched.stat().st_mtime_ns
        # O_NOFOLLOW refuses a symlink and O_NONBLOCK keeps a FIFO from hanging; fstat
        # then judges the very descriptor whose bytes are returned.
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except OSError as exc:
        raise Q0Error(f"{path.name} unreadable: {exc}") from exc
    try:
        status = os.fstat(fd)
        if not stat.S_ISREG(status.st_mode):
            raise Q0Error(f"{path.name} is not a regular file")
        if status.st_mtime_ns < launched_ns:
            raise Q0Error(f"{path.name} predates the guest launch: reused, not fresh")
        with open(fd, "rb", closefd=False) as stream:
            return stream.read()
    finally:
        os.close(fd)


def q0_collect(
    out: Path, launched: Path, identity: Mapping[str, str], evidence: Path
) -> Q0Observation:
    """Copy this run's fresh guest observation into evidence, or refuse it."""
    data = read_fresh(out / "observation.json", launched)
    observation = parse_observation(data)
    # [LAW:no-silent-failure] A timestamp alone cannot tell this attempt from a copied
    # prior one; the identity can, and there is no fallback to any other record.
    mismatches = [
        f"observation.json {key}={observation.identity[key]!r} is not this run's {identity[key]!r}"
        for key in Q0_IDENTITY
        if observation.identity[key] != identity[key]
    ]
    if mismatches:
        raise Q0Error("; ".join(mismatches))
    (evidence / "observation.json").write_bytes(data)
    return observation


def _agreement(values: Mapping[str, str], key: str) -> list[str]:
    return [] if len(set(values.values())) == 1 else [f"{key} values differ: {dict(values)}"]


def binding_verify(
    binding_env: Path, host_stage: Path, guest_record: Path, identity: Mapping[str, str]
) -> dict[str, Any]:
    # [LAW:one-source-of-truth] binding.env is hashed from its retained bytes on each side
    # of the boundary; no hash supplied through the environment is consulted. Its identity
    # must be the run's too, or equal hashes would bind a record of another run.
    record: dict[str, Any] = {}
    try:
        env_bytes = _read(binding_env)
        env = parse_binding_env(env_bytes)
        stage_bytes, guest_bytes = _read(host_stage), _read(guest_record)
        record["host_stage_sha256"] = _sha256(stage_bytes)
        record["guest_record_sha256"] = _sha256(guest_bytes)
        values = {
            "retained": _sha256(env_bytes),
            "host_stage": _hex64(
                _object(stage_bytes, "host-stage.json"), "binding_env_sha256", "host-stage.json"
            ),
            "guest": _hex64(
                _object(guest_bytes, guest_record.name), "binding_env_sha256", guest_record.name
            ),
        }
    except Q0Error as exc:
        return record | {"problems": [str(exc)]}
    return record | {
        "binding_env_sha256": values,
        "problems": _agreement(values, "binding_env_sha256")
        + [
            f"binding.env {key}={env[key]!r} is not this run's {identity[key]!r}"
            for key in Q0_IDENTITY
            if env[key] != identity[key]
        ],
    }


# --- Install boundary (guest_package_closure step 3) --------------------------------

# [LAW:one-source-of-truth] The capabilities the install may not hold, with their
# linux/capability.h bit numbers. The setpriv --bounding-set argument and every mask
# judgement below derive from this one tuple.
FORBIDDEN_CAPS = (
    ("sys_admin", 21),
    ("net_admin", 12),
    ("sys_ptrace", 19),
    ("sys_module", 16),
    ("bpf", 39),
    ("sys_rawio", 17),
)
CAP_SETS = ("CapInh", "CapPrm", "CapEff", "CapBnd", "CapAmb")
# env -i leaves exactly these three: the install's whole environment.
INSTALL_ENV = {
    "PATH": "/usr/sbin:/usr/bin:/sbin:/bin",
    "LC_ALL": "C",
    "DEBIAN_FRONTEND": "noninteractive",
}
DEB_CACHE = "var/cache/a5-debs"
_CAP_MASK = re.compile(r"[0-9a-f]{16}")


@dataclass(frozen=True)
class Deb:
    file: str
    size: int
    sha256: str


def install_argv(
    gate: Path, root: Path, host_netns: str, evidence: Path, debs: Sequence[Deb]
) -> list[str]:
    """Step 3b: the one entry argv, no shell. No variant omits the boundary."""
    return [
        *("sudo", "-n", "--", "/usr/bin/env", "-i"),
        *(f"{name}={value}" for name, value in INSTALL_ENV.items()),
        *("/usr/bin/unshare", "--net", "--pid", "--kill-child", "--"),
        *("/usr/bin/setpriv", "--no-new-privs", "--inh-caps", "-all", "--ambient-caps", "-all"),
        *("--bounding-set", ",".join(f"-{name}" for name, _ in FORBIDDEN_CAPS), "--"),
        *("/usr/bin/python3", "-I", str(gate), "guest-stage", "ns-install"),
        *("--root", str(root), "--host-netns", host_netns, "--evidence", str(evidence)),
        *(deb.file for deb in debs),
    ]


def _masks(raw: object, where: str) -> dict[str, int]:
    if type(raw) is not dict or sorted(cast(dict[str, object], raw)) != sorted(CAP_SETS):
        raise Q0Error(f"{where} capabilities {raw!r} are not exactly {list(CAP_SETS)}")
    masks = cast(dict[str, object], raw)
    for name in CAP_SETS:
        if type(masks[name]) is not str or not _CAP_MASK.fullmatch(cast(str, masks[name])):
            raise Q0Error(f"{where} {name} {masks[name]!r} is not a hex mask")
    return {name: int(cast(str, masks[name]), 16) for name in CAP_SETS}


def _held(mask: int) -> list[str]:
    return [name for name, bit in FORBIDDEN_CAPS if mask >> bit & 1]


def namespace_problems(raw: object) -> list[str]:
    """Step 3c: the pre-dpkg boundary ns-install recorded, judged as pure data."""
    if type(raw) is not dict:
        raise Q0Error(f"namespace record {raw!r} is not an object")
    ns = cast(dict[str, object], raw)
    problems = [
        f"{name} holds forbidden {held}"
        for name, mask in _masks(ns.get("capabilities"), "namespace").items()
        if (held := _held(mask))
    ]
    host, inner = ns.get("host_netns"), ns.get("netns")
    if type(host) is not str or type(inner) is not str or not host or host == inner:
        problems.append(f"netns {inner!r} is not a namespace apart from the host's {host!r}")
    if ns.get("interfaces") != ["lo"]:
        problems.append(f"interfaces {ns.get('interfaces')!r} are not exactly ['lo']")
    if ns.get("environment") != INSTALL_ENV:
        problems.append(f"environment {ns.get('environment')!r} is not exactly {INSTALL_ENV}")
    return problems


def run_problems(raw: object, debs: Sequence[Deb]) -> list[str]:
    """Step 3d: one install run, fail closed on any exit, boundary or package deviation."""
    if type(raw) is not dict:
        raise Q0Error(f"install run {raw!r} is not an object")
    run = cast(dict[str, object], raw)
    ns = run.get("namespace")
    if type(ns) is not dict:
        return [f"wrapper exit {run.get('wrapper_exit')!r}: no namespace record"]
    record = cast(dict[str, object], ns)
    exits = {"wrapper": run.get("wrapper_exit"), "dpkg": record.get("dpkg_exit")}
    expected = [{"file": d.file, "size": d.size, "sha256": d.sha256} for d in debs]
    return (
        [f"{name} exit {code!r} is not 0" for name, code in exits.items() if code != 0]
        + namespace_problems(record)
        + ([] if record.get("debs") == expected else [f"debs {record.get('debs')!r} != {expected}"])
    )


def _proc_caps() -> dict[str, str]:
    lines = Path("/proc/self/status").read_text().splitlines()
    return {
        key: value.strip()
        for key, _, value in (line.partition(":") for line in lines)
        if key.startswith("Cap")
    }


def _deb(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"file": path.name, "size": len(data), "sha256": _sha256(data)}


def ns_install(root: Path, host_netns: str, evidence: Path, files: Sequence[str]) -> int:
    """Inside the namespace: record the boundary, prove it, then dpkg -i once in order."""
    record: dict[str, Any] = {
        "host_netns": host_netns,
        "netns": os.readlink("/proc/self/ns/net"),
        "interfaces": [name for _, name in socket.if_nameindex()],
        "environment": dict(os.environ),
        "debs": [_deb(root / DEB_CACHE / name) for name in files],
        "dpkg_exit": None,
    }
    # Read last, immediately before dpkg is spawned: the exact pre-dpkg boundary.
    record["capabilities"] = _proc_caps()
    try:
        crossed = namespace_problems(record)
    except Q0Error as exc:
        crossed = [str(exc)]
    if not crossed:
        dpkg = ["chroot", str(root), "/usr/bin/dpkg", "-i"]
        record["dpkg_exit"] = subprocess.run(
            [*dpkg, *(f"/{DEB_CACHE}/{name}" for name in files)],
            env=INSTALL_ENV,
            close_fds=True,
            check=False,
        ).returncode
    evidence.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return 0 if record["dpkg_exit"] == 0 else 1


def install_run(
    argv: Sequence[str], namespace_record: Path, env: Mapping[str, str]
) -> dict[str, Any]:
    """Run one 3b argv on the host; its record is the wrapper exit plus ns-install's."""
    if namespace_record.exists():
        raise Q0Error(f"{namespace_record.name} exists before the run: not fresh")
    wrapper_exit = subprocess.run(argv, env=env, close_fds=True, check=False).returncode
    try:
        namespace: object = _object(_read(namespace_record), namespace_record.name)
    except Q0Error:
        namespace = None
    return {"wrapper_exit": wrapper_exit, "namespace": namespace}


# Step 3g: the same bash probe runs as the host control and as the fixture postinst.
NETPROBE_OUT = "a5-netprobe.out"


def netprobe_script(address: str, port: int) -> str:
    # Bash's own redirection opens /proc/self/status, so the masks are the probe's.
    return (
        "#!/bin/bash\n"
        f"if exec 3<>/dev/tcp/{address}/{port}; then echo net=connected; "
        "else echo net=failed; fi\n"
        'echo "sentinel=${A5_SENTINEL_ENV-unset}"\n'
        'while read -r key value; do case "$key" in Cap*:) echo "${key%:}=$value";; esac; '
        "done < /proc/self/status\n"
    )


def netprobe_package(address: str, port: int) -> dict[str, str]:
    """dpkg-deb --build content; the postinst writes its probe result into the root."""
    probe = netprobe_script(address, port)
    return {
        "DEBIAN/control": (
            "Package: a5-netprobe\nVersion: 1\nArchitecture: all\n"
            "Maintainer: a5 gate <a5@invalid>\nDescription: A5 install boundary self-test\n"
        ),
        "DEBIAN/postinst": probe.replace(
            "#!/bin/bash\n", f"#!/bin/bash\nexec > /{NETPROBE_OUT} 2>&1\n", 1
        ),
    }


def _probe(text: object, where: str) -> tuple[str, str, dict[str, int]]:
    if not isinstance(text, str):
        raise Q0Error(f"{where} probe result {text!r} is absent")
    fields = {key: value for key, _, value in (line.partition("=") for line in text.splitlines())}
    caps = {key: value for key, value in fields.items() if key.startswith("Cap")}
    return fields.get("net", ""), fields.get("sentinel", ""), _masks(caps, f"{where} probe")


def netprobe_problems(raw: object) -> list[str]:
    """Step 3g: a discriminating control, then a namespace probe that reaches nothing."""
    if type(raw) is not dict:
        raise Q0Error(f"self-test {raw!r} is not an object")
    test = cast(dict[str, Any], raw)
    sentinel = test.get("sentinel")
    if type(sentinel) is not str or not sentinel:
        raise Q0Error(f"self-test sentinel {sentinel!r} is empty")
    deb = test.get("deb")
    if type(deb) is not dict:
        raise Q0Error(f"self-test deb {deb!r} is not recorded")
    c_net, c_sentinel, c_caps = _probe(test.get("control"), "control")
    i_net, i_sentinel, i_caps = _probe(test.get("inside"), "inside")
    forbidden = [name for name, _ in FORBIDDEN_CAPS]
    problems = [
        f"non-discriminating control: {fact}"
        for fact, ok in (
            (f"net={c_net}", c_net == "connected"),
            (f"sentinel={c_sentinel!r}", c_sentinel == sentinel),
            ("CapBnd lacks a forbidden bit", _held(c_caps["CapBnd"]) == forbidden),
        )
        if not ok
    ]
    problems += [f"inside net={i_net}" for _ in [0] if i_net != "failed"]
    problems += [f"inside sentinel={i_sentinel!r}" for _ in [0] if i_sentinel != "unset"]
    problems += [f"inside {name} holds {held}" for name, m in i_caps.items() if (held := _held(m))]
    if test.get("accepted") != 1:
        problems.append(f"listener accepted {test.get('accepted')!r} connections, not 1")
    return problems + run_problems(test.get("run"), [Deb(**cast(dict[str, Any], deb))])


TEST_NET = "192.0.2.1"  # RFC 5737: the route lookup names the host's outbound source only
_ROUTE_SRC = re.compile(r"\bsrc (\S+)")
DPKG_DEB_TIMEOUT = 60  # seconds, for two gate-written files


def route_source(route: str) -> str:
    """`ip -4 route get TEST_NET` output -> the host's own non-loopback source address."""
    match = _ROUTE_SRC.search(route)
    if match is None or match[1].startswith("127."):
        raise Q0Error(f"no non-loopback source address in route {route!r}")
    return match[1]


def _accepted(listener: socket.socket) -> int:
    # Each probe's connect has completed (or failed) before its process exited, so the
    # backlog is final here: draining it counts every connection the listener accepted.
    listener.setblocking(False)
    count = 0
    while True:
        try:
            listener.accept()[0].close()
        except BlockingIOError:
            return count
        count += 1


def self_test(
    gate: Path, fresh_root: Path, host_netns: str, work: Path, sentinel: str
) -> dict[str, Any]:
    """Step 3g on the host: the control probe, then the fixture through steps 3b-3d.

    `fresh_root` is a fresh base extraction, never /a5-guest/root; its creator discards it.
    """
    route = subprocess.run(
        ["ip", "-4", "route", "get", TEST_NET], capture_output=True, text=True, check=True
    ).stdout
    address = route_source(route)
    env = {**os.environ, "A5_SENTINEL_ENV": sentinel}
    package, control_script = work / "a5-netprobe", work / "a5-netprobe-control"
    pool, record = work / "a5-netprobe-pool", work / "self-test-ns.json"
    deb_path = pool / "a5-netprobe_1_all.deb"
    pool.mkdir()
    with socket.create_server((address, 0)) as listener:
        port = listener.getsockname()[1]
        for name, text in netprobe_package(address, port).items():
            (package / name).parent.mkdir(parents=True, exist_ok=True)
            (package / name).write_text(text)
        (package / "DEBIAN" / "postinst").chmod(0o755)
        control_script.write_text(netprobe_script(address, port))
        control = subprocess.run(
            ["bash", str(control_script)], env=env, capture_output=True, text=True, check=False
        ).stdout
        run_steps(
            [["dpkg-deb", "--root-owner-group", "--build", str(package), str(deb_path)]],
            work,
            DPKG_DEB_TIMEOUT,
        )
        deb = Deb(**_deb(deb_path))
        deliver_debs(pool, fresh_root, [deb])
        run = install_run(install_argv(gate, fresh_root, host_netns, record, [deb]), record, env)
        accepted = _accepted(listener)
    inside = fresh_root / NETPROBE_OUT
    return {
        "sentinel": sentinel,
        "control": control,
        # A postinst that never ran leaves no file; the evaluator refuses the null.
        "inside": inside.read_text() if inside.is_file() else None,
        "accepted": accepted,
        "deb": asdict(deb),
        "run": run,
    }


def evaluate_install_ns(data: bytes, debs: Sequence[Deb]) -> list[str]:
    """Re-parse a retained install-ns.json: the real install and its passed self-test."""
    raw = _object(data, "install-ns.json")
    try:
        self_test = netprobe_problems(raw.get("self_test"))
    except Q0Error as exc:
        raise Q0Error(f"self-test: {exc}") from exc
    return [f"self-test: {p}" for p in self_test] + [
        f"install: {p}" for p in run_problems(raw.get("install"), debs)
    ]


def install_binding(
    install_ns: Path, binding_env: Path, guest_record: Path, debs: Sequence[Deb]
) -> dict[str, Any]:
    # [LAW:single-enforcer] The retained bytes are judged by the same step-3c evaluator,
    # and they are also exactly what INSTALL_NS_SHA256 names on every side.
    try:
        ns_bytes = _read(install_ns)
        boundary = evaluate_install_ns(ns_bytes, debs)
        values = {
            "install_ns": _sha256(ns_bytes),
            "binding_env": parse_binding_env(_read(binding_env))["INSTALL_NS_SHA256"],
            "guest": _hex64(
                _object(_read(guest_record), guest_record.name),
                "INSTALL_NS_SHA256",
                guest_record.name,
            ),
        }
    except Q0Error as exc:
        return {"problems": [str(exc)]}
    return {
        "INSTALL_NS_SHA256": values,
        "problems": boundary + _agreement(values, "INSTALL_NS_SHA256"),
    }


def _persist(path: Path, record: dict[str, Any]) -> dict[str, Any]:
    record = record | {"verdict": "fail" if record["problems"] else "pass"}
    path.write_text(json.dumps(record, indent=2) + "\n")
    return record


def q0_observe(
    out: Path,
    launched: Path,
    identity: Mapping[str, str],
    evidence: Path,
    binding_env: Path,
    host_stage: Path,
    install_ns: Path,
    debs: Sequence[Deb],
) -> dict[str, Any]:
    """Collect, then binding-verify, then install-binding (reviewer F8-R1).

    The observation is completed only when all three pass; the guest having written
    observation.json is never enough.
    """
    try:
        observation = q0_collect(out, launched, identity, evidence)
    except Q0Error as exc:
        return {"completed_observation": False, "problems": [f"collect: {exc}"]}
    guest = evidence / "observation.json"
    # [LAW:dataflow-not-control-flow] Both binding checks always run and persist their
    # evidence; a failure in either leaves the collected file but fails the bindings.
    checks = {
        "binding-verify": _persist(
            evidence / "binding-verify.json",
            binding_verify(binding_env, host_stage, guest, identity),
        ),
        "install-binding": _persist(
            evidence / "install-binding.json",
            install_binding(install_ns, binding_env, guest, debs),
        ),
    }
    problems = [f"{name}: {p}" for name, check in checks.items() for p in check["problems"]]
    return {
        "observation_sha256": observation.sha256,
        "completed_observation": not problems,
        "problems": problems,
    }


# --- Stage manifest (host_guest_boundary.stage_manifest) and pool delivery (step 3a) ---

# The only entries /a5/meta may hold; it is excluded from the manifest that names it.
STAGE_META = ("binding.env", "host.json", "host-env-origin.json", "stage-manifest.json")
_MAX_HOPS = 40  # the kernel's own symlink-follow limit


@dataclass(frozen=True)
class Stage:
    """What one walk of the staged root and /a5 observed, keyed by guest path."""

    manifest: Mapping[str, Mapping[str, Any]]
    pth: Mapping[str, str]  # each .pth file under /a5 -> its text
    meta: tuple[str, ...]  # the names present in /a5/meta


def _within(path: str, top: str) -> bool:
    return path == top or path.startswith(f"{top}/")


def _node(path: Path) -> dict[str, Any]:
    status = path.lstat()
    node: dict[str, Any] = {
        "mode": stat.S_IMODE(status.st_mode),
        "uid": status.st_uid,
        "gid": status.st_gid,
    }
    if stat.S_ISREG(status.st_mode):
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        return node | {"type": "file", "size": status.st_size, "sha256": digest}
    if stat.S_ISLNK(status.st_mode):
        return node | {"type": "symlink", "target": os.readlink(path)}
    if stat.S_ISDIR(status.st_mode):
        return node | {"type": "dir"}
    # A device, fifo or socket is recorded so the judgement below refuses it.
    return node | {"type": stat.filemode(status.st_mode)[0]}


def _walk(host: Path, guest: str, skip: Collection[str]) -> Iterator[tuple[str, Path]]:
    yield guest, host
    if stat.S_ISDIR(host.lstat().st_mode):
        for child in sorted(host.iterdir()):
            if (name := f"{guest.rstrip('/')}/{child.name}") not in skip:
                yield from _walk(child, name, skip)


def scan_stage(root: Path, a5: Path, mounts: Collection[str]) -> Stage:
    """Walk the staged root as / and the /a5 tree as /a5, never entering a mountpoint.

    [LAW:one-source-of-truth] The host (over /a5-guest/root and /a5) and the guest (over
    / and /a5) run this same walk with the same mountpoints, so equal stages give equal
    bytes and the comparison needs no translation.
    """
    skip = {"/a5", "/a5/meta", *mounts}
    manifest = {
        guest: _node(host)
        for top, at in ((root, "/"), (a5, "/a5"))
        for guest, host in _walk(top, at, skip)
    }
    pth = {
        guest: (a5 / guest.removeprefix("/a5/")).read_text()
        for guest, node in manifest.items()
        if _within(guest, "/a5") and node["type"] == "file" and guest.endswith(".pth")
    }
    return Stage(manifest, pth, tuple(sorted(p.name for p in (a5 / "meta").iterdir())))


def resolve(path: str, links: Mapping[str, str]) -> str:
    """Resolve a guest path component by component through the staged symlinks."""
    pending = [part for part in reversed(path.split("/")) if part]
    current, hops = PurePosixPath("/"), 0
    while pending:
        part = pending.pop()
        step = current.parent if part == ".." else current if part == "." else current / part
        target = links.get(str(step))
        if target is None:
            current = step
            continue
        hops += 1
        if hops > _MAX_HOPS:
            raise Q0Error(f"symlink {step} does not resolve within {_MAX_HOPS} hops")
        current = PurePosixPath("/") if target.startswith("/") else current
        pending.extend(part for part in reversed(target.split("/")) if part)
    return str(current)


def stage_problems(stage: Stage) -> list[str]:
    """The fail-closed stage checks that need no expectations (Q0_unavailable_checks)."""
    links = {
        path: node["target"] for path, node in stage.manifest.items() if node["type"] == "symlink"
    }

    def outside(path: str, top: str) -> str | None:
        try:
            resolved = resolve(path, links)
        except Q0Error as exc:
            return str(exc)
        return None if _within(resolved, top) else f"resolves to {resolved}, outside {top}"

    pth_lines = [
        (path, line.strip())
        for path, text in stage.pth.items()
        for line in text.splitlines()
        if line.strip() and not line.startswith("#")
    ]
    return (
        [
            f"{path} is a {node['type']!r} node: no device, fifo or socket may be staged"
            for path, node in stage.manifest.items()
            if node["type"] not in ("file", "dir", "symlink")
        ]
        + [
            f"symlink {path} {problem}"
            for path in links
            if _within(path, "/a5") and (problem := outside(path, "/a5"))
        ]
        # An `import` line names no path, so it resolves outside /a5/src and is refused.
        + [
            f"{path} line {line!r} {problem}"
            for path, line in pth_lines
            if (problem := outside(str(PurePosixPath(path).parent / line), "/a5/src"))
        ]
        + [
            f"/a5/meta/{name} is not one of {list(STAGE_META)}"
            for name in stage.meta
            if name not in STAGE_META
        ]
        + [
            f"{path} is left in the stage (step 3e)"
            for path in stage.manifest
            if _within(path, f"/{DEB_CACHE}")
        ]
    )


def manifest_diff(
    first: Mapping[str, Mapping[str, Any]], second: Mapping[str, Mapping[str, Any]]
) -> list[str]:
    """Every path present in only one manifest or recorded differently in each."""
    return sorted(
        path for path in first.keys() | second.keys() if first.get(path) != second.get(path)
    )


def guest_stage_verify(root: Path, a5: Path, mounts: Collection[str]) -> list[str]:
    """Write /a5/meta/stage-manifest.json and return why the stage may not boot."""
    stage = scan_stage(root, a5, mounts)
    # [LAW:effects-at-boundaries] The manifest is written as evidence whatever the
    # judgement; its sha256 is STAGE_MANIFEST_SHA256 only on a stage with no problem.
    (a5 / "meta" / "stage-manifest.json").write_bytes(_canonical(stage.manifest))
    return stage_problems(stage)


def deliver_debs(pool: Path, root: Path, debs: Sequence[Deb]) -> None:
    """Step 3a: the downloaded pool equals the verified list exactly, then enters the root."""
    present = {path.name: _deb(path) for path in pool.iterdir()}
    expected = {
        deb.file: {"file": deb.file, "size": deb.size, "sha256": deb.sha256} for deb in debs
    }
    problems = [
        f"pool {name}: {present.get(name)} != verified {expected.get(name)}"
        for name in sorted(present.keys() | expected.keys())
        if present.get(name) != expected.get(name)
    ]
    if problems:
        raise Q0Error("; ".join(problems))
    cache = root / DEB_CACHE
    cache.mkdir(parents=True)
    for deb in debs:
        shutil.copyfile(pool / deb.file, cache / deb.file)


def guest_install(
    gate: Path, root: Path, host_netns: str, pool: Path, debs: Sequence[Deb], record: Path
) -> dict[str, Any]:
    """Steps 3a-3e for the real root: deliver, install once in the namespace, remove."""
    deliver_debs(pool, root, debs)
    run = install_run(install_argv(gate, root, host_netns, record, debs), record, os.environ)
    # [LAW:dataflow-not-control-flow] Step 3e runs whatever the run's outcome; the run
    # record carries any failure and the stage manifest refuses a remaining cache path.
    shutil.rmtree(root / DEB_CACHE)
    return run


# --- Bootstrap, closure (guest_package_closure steps 1-2) and the guest kernel ----------

SNAPSHOT_URL = "https://snapshot.ubuntu.com/ubuntu/"
KERNEL_TARBALL = "linux-7.3.1.tar.xz"
KERNEL_URL = "https://cdn.kernel.org/pub/linux/kernel/v7.x/"
KERNEL_LOCALVERSION = "-a5guest"
KERNEL_BUILD_TIMEOUT = 35 * 60  # seconds; a miss fails the leg, with no prebuilt fallback
DPKG_QUERY_FORMAT = "${Package} ${Version} ${Architecture} ${db:Status-Abbrev}\n"
_SUMS_LINE = re.compile(r"([0-9a-f]{64}) [ *](\S+)")
_URI_LINE = re.compile(r"'(\S+)' \S+ ([0-9]+) SHA256:([0-9a-f]{64})")
_INDEX_FIELDS = ("Package", "Version", "Architecture", "Filename", "Size", "SHA256")


def gpgv_argv(keyring: Path, *args: Path | str) -> list[str]:
    """One gpgv call against a keyring holding only the pinned key; status on stdout."""
    return ["gpgv", "--status-fd", "1", "--keyring", str(keyring.resolve()), *map(str, args)]


def signature_problems(status: str, exit_code: int, fingerprint: str) -> list[str]:
    """gpgv's verdict: exit 0 and a VALIDSIG whose primary key is the pinned fingerprint."""
    # VALIDSIG's last field is the primary-key fingerprint, whichever subkey signed.
    signers = [
        line.split()[-1] for line in status.splitlines() if line.startswith("[GNUPG:] VALIDSIG ")
    ]
    return [f"gpgv exited {exit_code}" for _ in [0] if exit_code != 0] + [
        f"no valid signature by pinned {fingerprint} (signers {signers})"
        for _ in [0]
        if fingerprint not in signers
    ]


def sums_entry(text: str, name: str) -> str:
    """The one sha256 a verified checksum list gives for `name`."""
    entries = [
        match[1]
        for line in text.splitlines()
        if (match := _SUMS_LINE.fullmatch(line)) and match[2] == name
    ]
    if len(entries) != 1:
        raise Q0Error(f"checksum list names {name} {len(entries)} times, not once")
    return entries[0]


def tarball_problems(sums: str, name: str, pin: str, tarball_sha256: str) -> list[str]:
    """The tarball's sha256 equals both its signed checksum entry and the reviewed pin."""
    return _agreement({"pin": pin, "sums": sums_entry(sums, name), "tarball": tarball_sha256}, name)


def base_problems(sha256sums: bytes, tarball_sha256: str, base: BaseInput) -> list[str]:
    """Step 1 after gpgv: the pinned SHA256SUMS bytes and the pinned base tarball."""
    return [
        f"SHA256SUMS sha256 {digest} is not the pinned {base.sha256sums_sha256}"
        for digest in [_sha256(sha256sums)]
        if digest != base.sha256sums_sha256
    ] + tarball_problems(sha256sums.decode(), base.tarball, base.tarball_sha256, tarball_sha256)


@dataclass(frozen=True)
class Package:
    name: str
    version: str
    architecture: str


def dpkg_query_argv(root: Path) -> list[str]:
    """Step 1: read the extracted base's own status database, not the host's."""
    return ["dpkg-query", f"--admindir={root}/var/lib/dpkg", "-W", "-f", DPKG_QUERY_FORMAT]


def base_packages(listing: str) -> tuple[Package, ...]:
    # [LAW:parse-dont-validate] A base set exists only when every entry is installed.
    rows = [line.split() for line in listing.splitlines()]
    refused = [" ".join(row) for row in rows if len(row) != 4 or row[3] != "ii"]
    if refused or not rows:
        raise Q0Error(f"base status entries not 'ii': {refused or 'none listed'}")
    return tuple(Package(*row[:3]) for row in rows)


def apt_private(work: Path, root: Path, keyring: Path, archive: ArchiveInput) -> dict[str, str]:
    """Step 2: the private apt configuration, as files to write under `work`.

    Every Dir, source and trust key points into `work` or the extracted base, so the
    resolution reads only the pinned snapshot, signed by the pinned archive key.
    """
    source = f"{SNAPSHOT_URL}{archive.snapshot_id}"
    settings = {
        "Dir::State::status": f"{root}/var/lib/dpkg/status",
        "Dir::State::lists": f"{work}/lists",
        "Dir::Cache": f"{work}/cache",
        "Dir::Etc::sourcelist": f"{work}/sources.list",
        "Dir::Etc::sourceparts": f"{work}/empty",
        "Dir::Etc::trustedparts": f"{work}/empty",
        "Dir::Etc::preferencesparts": f"{work}/empty",
        "APT::Architecture": "amd64",
    }
    return {
        "apt.conf": "".join(f'{key} "{value}";\n' for key, value in settings.items())
        + 'APT::Architectures { "amd64"; };\n',
        "sources.list": f"deb [arch=amd64 signed-by={keyring.resolve()}] {source} "
        f"{archive.suite} {' '.join(archive.components)}\n",
    }


def apt_argv(work: Path, *command: str) -> list[str]:
    return ["apt-get", "-c", str(work / "apt.conf"), *command]


CLOSURE_COMMAND = ("--download-only", "--print-uris", "install", *GUEST_PACKAGES)


@dataclass(frozen=True)
class PoolPackage:
    package: Package
    filename: str  # the pool path in the verified Packages index
    size: int
    sha256: str

    @property
    def deb(self) -> Deb:
        return Deb(PurePosixPath(self.filename).name, self.size, self.sha256)


def packages_index(text: str) -> dict[str, PoolPackage]:
    """A verified Packages index keyed by Filename."""
    index: dict[str, PoolPackage] = {}
    for stanza in filter(str.strip, text.split("\n\n")):
        # A continuation line (leading space) belongs to a multi-line field the gate never reads.
        raw = {
            key: value
            for key, _, value in (line.partition(": ") for line in stanza.splitlines())
            if not key[:1].isspace()
        }
        if missing := [key for key in _INDEX_FIELDS if not raw.get(key)]:
            raise Q0Error(f"Packages stanza {raw.get('Package')!r} lacks {missing}")
        index[raw["Filename"]] = PoolPackage(
            Package(raw["Package"], raw["Version"], raw["Architecture"]),
            raw["Filename"],
            int(raw["Size"]),
            raw["SHA256"],
        )
    return index


def closure(
    print_uris: str, index: Mapping[str, PoolPackage], snapshot_id: str, base: Iterable[Package]
) -> tuple[PoolPackage, ...]:
    """Step 2: each package apt adds, as the verified index records it, in apt's order."""
    source = f"{SNAPSHOT_URL}{snapshot_id}/"
    lines = [line for line in print_uris.splitlines() if line.startswith("'")]
    added: list[PoolPackage] = []
    for line in lines:
        if not (match := _URI_LINE.fullmatch(line)) or not match[1].startswith(source):
            raise Q0Error(f"apt URI line {line!r} is not from the pinned snapshot")
        entry = index.get(unquote(match[1].removeprefix(source)))
        if entry is None or (entry.size, entry.sha256) != (int(match[2]), match[3]):
            raise Q0Error(f"apt URI line {line!r} disagrees with the verified index ({entry})")
        added.append(entry)
    names = [entry.package.name for entry in added]
    in_base = sorted(set(names) & {package.name for package in base})
    if in_base or not set(GUEST_PACKAGES) <= set(names):
        raise Q0Error(f"closure {names} must add {list(GUEST_PACKAGES)} and no base {in_base}")
    return tuple(added)


def _fetch(target: Path, url: str) -> list[str]:
    return ["curl", "-fsSL", "--proto", "=https", "-o", str(target), url]


def kernel_fetch(work: Path) -> list[list[str]]:
    """Acquire the tarball, its developer signature and the autosigned checksum list."""
    names = (KERNEL_TARBALL, KERNEL_TARBALL.replace(".xz", ".sign"), "sha256sums.asc")
    return [_fetch(work / name, f"{KERNEL_URL}{name}") for name in names]


def kernel_build(source: Path, fragment: Path, jobs: int) -> list[list[str]]:
    """build_provenance: defconfig, vng --kconfig, the pinned fragment, then bzImage."""
    make = ["make", f"-j{jobs}", f"LOCALVERSION={KERNEL_LOCALVERSION}"]
    return [
        [*make, "defconfig"],
        ["vng", "--kconfig"],
        ["scripts/kconfig/merge_config.sh", "-m", ".config", str(fragment.resolve())],
        [*make, "olddefconfig"],
        [*make, "bzImage"],
    ]


def run_steps(steps: Sequence[Sequence[str]], cwd: Path, timeout: float) -> None:
    """Run each argv in order under one deadline; any failure or the deadline fails closed."""
    deadline = time.monotonic() + timeout
    for argv in steps:
        try:
            subprocess.run(
                argv,
                cwd=cwd,
                check=True,
                close_fds=True,
                timeout=max(deadline - time.monotonic(), 0),
            )
        except (OSError, subprocess.SubprocessError) as exc:
            # [LAW:no-silent-failure] No retry and no fallback artifact.
            raise Q0Error(f"step {list(argv)} failed: {exc}") from exc


# --- Q0 bootstrap on the host (steps 1, 2, 3a acquisition and 3g) ---------------------

BOOTSTRAP_TIMEOUT = 20 * 60  # seconds for each bootstrap step; a miss fails Q0 closed


def base_fetch(work: Path, base: BaseInput) -> list[list[str]]:
    """Step 1 acquisition: the checksum list, its detached signature and the tarball."""
    names = ("SHA256SUMS", "SHA256SUMS.gpg", base.tarball)
    return [_fetch(work / name, f"{base.release_dir}{name}") for name in names]


def pool_fetch(pool: Path, snapshot_id: str, packages: Sequence[PoolPackage]) -> list[list[str]]:
    """Step 3a acquisition: exactly the closure's files, by their verified pool path."""
    source = f"{SNAPSHOT_URL}{snapshot_id}/"
    return [_fetch(pool / entry.deb.file, source + quote(entry.filename)) for entry in packages]


def extract_argv(tarball: Path, root: Path) -> list[str]:
    return ["tar", "--numeric-owner", "-xpf", str(tarball), "-C", str(root)]


def discard_argv(root: Path) -> list[str]:
    """The self-test's namespace dpkg leaves root-owned files, so only root removes them."""
    return ["sudo", "-n", "--", "rm", "-rf", "--one-file-system", "--", str(root)]


def _stdout(argv: Sequence[str], cwd: Path) -> str:
    try:
        return subprocess.run(
            argv,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
            close_fds=True,
            timeout=BOOTSTRAP_TIMEOUT,
        ).stdout
    except (OSError, subprocess.SubprocessError) as exc:
        raise Q0Error(f"{list(argv)} failed: {exc}") from exc


def verified_base(work: Path, keyring: Path, base: BaseInput) -> Path:
    """Step 1 before extraction: gpgv over SHA256SUMS, then the tarball's two-way pin."""
    sums = work / "SHA256SUMS"
    gpgv = subprocess.run(
        gpgv_argv(keyring, work / "SHA256SUMS.gpg", sums),
        capture_output=True,
        text=True,
        check=False,
    )
    tarball = work / base.tarball
    problems = signature_problems(gpgv.stdout, gpgv.returncode, base.signing_key)
    problems += base_problems(_read(sums), _sha256(_read(tarball)), base)
    if problems:
        raise Q0Error("; ".join(problems))
    return tarball


@contextmanager
def fresh_base(tarball: Path, root: Path) -> Iterator[Path]:
    """A fresh extraction of the verified base, discarded by its creator however it ends."""
    root.mkdir()
    try:
        run_steps([extract_argv(tarball, root)], root.parent, BOOTSTRAP_TIMEOUT)
        yield root
    finally:
        run_steps([discard_argv(root)], root.parent, BOOTSTRAP_TIMEOUT)


def resolve_closure(
    work: Path, root: Path, keyring: Path, archive: ArchiveInput, base: Sequence[Package]
) -> tuple[PoolPackage, ...]:
    """Step 2: host apt under the private configuration verifies InRelease -> Packages."""
    apt = work / "apt"
    for name in ("lists/partial", "cache/archives/partial", "empty"):
        (apt / name).mkdir(parents=True)
    for name, text in apt_private(apt, root, keyring, archive).items():
        (apt / name).write_text(text)
    _stdout(apt_argv(apt, "update"), apt)
    uris = _stdout(apt_argv(apt, *CLOSURE_COMMAND), apt)
    index = {
        filename: entry
        for path in sorted((apt / "lists").glob("*_Packages"))
        for filename, entry in packages_index(path.read_text()).items()
    }
    return closure(uris, index, archive.snapshot_id, base)


@dataclass(frozen=True)
class Bootstrap:
    tarball: Path  # verified; the real root is its second extraction
    base_packages: tuple[Package, ...]
    closure: tuple[PoolPackage, ...]
    pool: Path  # downloaded, unverified: deliver_debs checks it against `closure` at entry
    self_test: dict[str, Any]


def bootstrap(
    gate: Path,
    inputs: Inputs,
    work: Path,
    keyrings: tuple[Path, Path],
    host_netns: str,
    sentinel: str,
) -> Bootstrap:
    """Steps 1, 2, 3a acquisition and 3g; `keyrings` hold only the base and archive keys."""
    base_keyring, archive_keyring = keyrings
    run_steps(base_fetch(work, inputs.base), work, BOOTSTRAP_TIMEOUT)
    tarball = verified_base(work, base_keyring, inputs.base)
    with fresh_base(tarball, work / "base") as fresh:
        packages = base_packages(_stdout(dpkg_query_argv(fresh), work))
        # [LAW:no-ambient-temporal-coupling] apt reads this extraction's status file, so
        # the closure is resolved before the self-test's fixture install changes it.
        added = resolve_closure(work, fresh, archive_keyring, inputs.archive, packages)
        test = self_test(gate, fresh, host_netns, work, sentinel)
    pool = work / "pool"
    pool.mkdir()
    run_steps(pool_fetch(pool, inputs.archive.snapshot_id, added), work, BOOTSTRAP_TIMEOUT)
    return Bootstrap(tarball, packages, added, pool, test)


def root_manifest(root: Path) -> dict[str, Mapping[str, Any]]:
    """One staged root as the guest will see it at /, by guest path."""
    return {guest: _node(host) for guest, host in _walk(root, "/", ())}


def installed_root(
    gate: Path, root: Path, host_netns: str, boot: Bootstrap, record: Path
) -> dict[str, Mapping[str, Any]]:
    """Step 3 into one extraction of the verified base; any run problem fails Q0 (3d)."""
    debs = [entry.deb for entry in boot.closure]
    run = guest_install(gate, root, host_netns, boot.pool, debs, record)
    if problems := run_problems(run, debs):
        raise Q0Error(f"install into {root}: " + "; ".join(problems))
    return root_manifest(root)


def stage_twice(
    gate: Path, boot: Bootstrap, root: Path, evidence: Path, work: Path, host_netns: str
) -> tuple[dict[str, Mapping[str, Any]], dict[str, Mapping[str, Any]]]:
    """Q0_observation stages the root in two fresh directories; only `root` is kept to boot.

    Each is a further extraction of the verified tarball. The repeat exists only so its
    manifest can expose a path that differs between two builds, then root discards it.
    """
    root.mkdir()
    run_steps([extract_argv(boot.tarball, root)], root.parent, BOOTSTRAP_TIMEOUT)
    staged = installed_root(gate, root, host_netns, boot, evidence / "install-ns.json")
    with fresh_base(boot.tarball, work / "root-repeat") as repeat:
        again = installed_root(gate, repeat, host_netns, boot, work / "install-ns-repeat.json")
    return staged, again


# --- CLI ----------------------------------------------------------------------------


@dataclass(frozen=True)
class HostFacts:
    """What Q0_observation needs that only the host can measure.

    They reach the guest only inside /a5/meta/host.json, the one host record that
    crosses into it: `asdict` of this value is that record's facts.
    """

    base_packages: tuple[Package, ...]
    closure: tuple[PoolPackage, ...]
    host_packages: Mapping[str, str]  # package name -> installed version on the host
    # [LAW:types-are-the-program] Exactly the two stagings whose difference Q0 exposes.
    root_manifests: tuple[Mapping[str, Mapping[str, Any]], Mapping[str, Mapping[str, Any]]]
    vng_help: str


# [LAW:one-source-of-truth] The keys observe requires are the fields the host writes.
HOST_FACTS = tuple(field.name for field in fields(HostFacts))
# What the guest reads from its binding environment rather than computing itself.
GUEST_BOUND = (*(key for key in Q0_IDENTITY if key != "INPUTS_SHA256"), "INSTALL_NS_SHA256")
SHARE_FSTYPES = ("virtiofs", "9p")
_MOUNT_ESCAPE = re.compile(r"\\([0-7]{3})")


@dataclass(frozen=True)
class GuestFacts:
    """What the Q0 guest measures of itself, at the edge, before anything is judged."""

    root_top_level: tuple[str, ...]
    mountinfo: str
    shares: tuple[Mapping[str, Any], ...]
    packages: tuple[Package, ...]


def shares(mountinfo: str) -> list[dict[str, str]]:
    """The host-backed mounts in /proc/self/mountinfo: mountpoint, fstype, tag, options."""
    rows: list[dict[str, str]] = []
    for line in mountinfo.splitlines():
        mount, _, filesystem = line.partition(" - ")
        fields_, (fstype, source, options) = mount.split(), filesystem.split()
        mountpoint = _MOUNT_ESCAPE.sub(lambda m: chr(int(m[1], 8)), fields_[4])
        rows.append(
            {
                "mountpoint": mountpoint,
                "fstype": fstype,
                "source": source,
                "options": f"{fields_[5]} {options}",
            }
        )
    return [row for row in rows if row["fstype"] in SHARE_FSTYPES]


def guest_facts() -> GuestFacts:
    mountinfo = Path("/proc/self/mountinfo").read_text()
    listing = subprocess.run(
        dpkg_query_argv(Path("/")), check=True, capture_output=True, text=True
    ).stdout
    return GuestFacts(
        root_top_level=tuple(sorted(os.listdir("/"))),
        mountinfo=mountinfo,
        shares=tuple(
            share | {"content": {g: _node(h) for g, h in _walk(Path(mp), mp, ())}}
            for share in shares(mountinfo)
            if (mp := share["mountpoint"])
        ),
        packages=base_packages(listing),
    )


def observation(
    inputs: Inputs,
    binding_env: bytes,
    host_json: bytes,
    environ: Mapping[str, str],
    guest: GuestFacts,
) -> bytes:
    """The Q0 guest's observation.json: facts and bindings only, never a verdict.

    [LAW:single-enforcer] The host's binding-verify and install-binding compare these
    bindings; the guest records what it read and judges nothing.
    """
    parse_binding_env(binding_env)
    host = _object(host_json, "host.json")
    missing = [key for key in HOST_FACTS if key not in host] + [
        key for key in GUEST_BOUND if not environ.get(key)
    ]
    if missing:
        raise Q0Error(f"observation lacks {missing}")
    raw = host["root_manifests"]
    manifests = cast(list[Mapping[str, Mapping[str, Any]]], raw) if type(raw) is list else []
    if len(manifests) != 2:
        raise Q0Error("host.json root_manifests is not the two stagings")
    first, second = manifests
    return _canonical(
        {key: environ[key] for key in GUEST_BOUND}
        | {key: host[key] for key in HOST_FACTS}
        | {
            "INPUTS_SHA256": inputs.sha256,
            # The record is of the bytes parsed here; no environment variable can name it.
            "binding_env_sha256": _sha256(binding_env),
            "root_manifest_diff": manifest_diff(first, second),
            "root_top_level": list(guest.root_top_level),
            "mountinfo": guest.mountinfo,
            "shares": list(guest.shares),
            "packages": [asdict(package) for package in guest.packages],
        }
    )


def observe(inputs: Inputs, meta: Path, out: Path) -> int:
    """Write out/observation.json from /a5/meta and the guest's own facts; nothing else."""
    try:
        record = observation(
            inputs,
            _read(meta / "binding.env"),
            _read(meta / "host.json"),
            os.environ,
            guest_facts(),
        )
    except Q0Error as exc:
        print(f"a5-kernel-ci observe: {exc}", file=sys.stderr)
        return 1
    out.mkdir(parents=True, exist_ok=True)
    (out / "observation.json").write_bytes(record)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--expectations", type=Path, default=EXPECTATIONS)
    parser = argparse.ArgumentParser(description="A5 kernel CI venue gate")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "check"):
        leg = commands.add_parser(name, parents=[common])
        leg.add_argument("--venue", required=True)
        leg.add_argument("--out", type=Path, required=True)
        leg.add_argument("--preflight", type=Path, help="check: this leg's preflight record")
        leg.add_argument("--junit", type=Path, help="check: this leg's fresh JUnit file")
    # [LAW:no-mode-explosion] ns-install has no option that skips or relaxes the boundary.
    stages = commands.add_parser("guest-stage").add_subparsers(dest="stage", required=True)
    ns = stages.add_parser("ns-install", parents=[common])
    ns.add_argument("--root", type=Path, required=True)
    ns.add_argument("--host-netns", required=True)
    ns.add_argument("--evidence", type=Path, required=True)
    ns.add_argument("debs", nargs="+")
    probe = commands.add_parser("observe", parents=[common])
    probe.add_argument("--meta", type=Path, required=True)
    probe.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    raw_bytes = args.expectations.read_bytes()
    try:
        raw: Any = json.loads(raw_bytes)
        document: Mapping[str, Any] = (
            cast(Mapping[str, Any], raw) if isinstance(raw, Mapping) else {}
        )
        inputs = parse_inputs(document.get("inputs"))
    except (ExpectationsError, ValueError) as exc:
        print(f"a5-kernel-ci: {exc}", file=sys.stderr)
        return 2
    # [LAW:one-way-deps] observe is dispatched before `expectations` is parsed, so no
    # Q1 section can shape a Q0 observation.
    if args.command == "observe":
        return observe(inputs, args.meta, args.out)
    try:
        expectations = parse_expectations(document)
    except (ExpectationsError, ValueError) as exc:
        print(f"a5-kernel-ci: {exc}", file=sys.stderr)
        return 2
    if args.command == "guest-stage":
        return ns_install(args.root, args.host_netns, args.evidence, args.debs)
    if args.venue not in expectations.venues:
        print(f"a5-kernel-ci: unknown venue {args.venue!r}", file=sys.stderr)
        return 2
    if args.command == "check" and (args.preflight is None or args.junit is None):
        parser.error("check needs --preflight and --junit")

    raw_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    record = (
        preflight(args.venue, expectations, raw_sha256)
        if args.command == "preflight"
        else check(
            args.venue,
            expectations,
            raw_sha256,
            os.environ,
            _measure_leg(),
            args.preflight,
            args.junit,
        )
        | {"expectations_sha256": raw_sha256}
    )
    record["verdict"] = "fail" if record["problems"] else "pass"
    # [LAW:effects-at-boundaries] The record is persisted before the verdict exits, so a
    # failing leg still uploads the evidence of why it failed.
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=2) + "\n")
    for problem in record["problems"]:
        print(f"::error title=a5-kernel-ci {args.command} ({args.venue})::{problem}")
    print(f"a5-kernel-ci {args.command} {args.venue}: {record['verdict']} -> {args.out}")
    return 1 if record["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
