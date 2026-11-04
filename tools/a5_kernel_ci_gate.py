"""Fail-closed kernel-venue gate for the A5 Landlock read-boundary canaries.

The package suite skips the SUPPORTED_HOST canaries on a host the launcher refuses and the
UNSUPPORTED_HOST refusal tests on a host it accepts, so a green suite proves neither venue
on its own. Each `package-tests` matrix leg therefore runs two subcommands around the
unchanged suite:

* ``preflight`` (before pytest) runs the REAL launcher host check on the runner's actual
  architecture and measured Landlock ABI, binds the result to image, kernel, run and commit
  identity, and fails unless the allocation is exactly the venue it was selected as.
* ``check`` (after pytest) reads that leg's fresh JUnit by exact node ID and fails unless
  every guarded ID appears exactly once with the outcome its venue requires.

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
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

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
# A record from a different run, attempt or commit is stale evidence for this leg.
_SAME_LEG = ("CI_HEAD", "CI_BASE", "CI_TESTED", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT")


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
    for path, want in expected_blobs.items():
        if blobs.get(path) != want:
            problems.append(f"{path} is blob {blobs.get(path)}, expectations bind {want}: stale")
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


def _read_blob(path: Path) -> str | None:
    return git_blob(path.read_bytes()) if path.is_file() else None


def preflight(venue_id: str, expectations: Expectations, raw_sha256: str) -> dict[str, Any]:
    venue = expectations.venues[venue_id]
    started_at = datetime.now(UTC).isoformat()
    env = {name: os.environ.get(name, "") for name in _BINDING_ENV}
    host = _measure_host()
    blobs = {p: _read_blob(ROOT / p) for p in expectations.bound_blobs}
    checked_out = _git("rev-parse", "HEAD")
    parents = _git("rev-list", "--parents", "-n", "1", "HEAD").split()[1:]
    return {
        "venue": venue_id,
        "started_at": started_at,
        "host": {
            "machine": host.machine,
            "landlock_abi": host.abi,
            "launcher": "accepted" if host.refusal is None else "refused",
            "refusal": host.refusal,
            "kernel": platform.release(),
            "os": platform.freedesktop_os_release().get("PRETTY_NAME", ""),
        },
        "binding": env,
        "checked_out": checked_out,
        "parents": parents,
        "blobs": blobs,
        "expectations_sha256": raw_sha256,
        "problems": judge_preflight(venue, host, env, blobs, expectations.bound_blobs, checked_out),
    }


# --- check --------------------------------------------------------------------------


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
    venue_id: str, expectations: Expectations, preflight_path: Path, junit_path: Path
) -> dict[str, Any]:
    record: dict[str, Any] = {"venue": venue_id, "outcomes": {}}
    try:
        prior = json.loads(preflight_path.read_text())
    except (OSError, ValueError) as exc:
        return record | {"problems": [f"preflight record unreadable: {exc}"]}
    record["preflight_sha256"] = hashlib.sha256(preflight_path.read_bytes()).hexdigest()
    problems = [f"preflight: {p}" for p in prior.get("problems", ["record has no problems list"])]
    if prior.get("venue") != venue_id:
        problems.append(f"preflight is for venue {prior.get('venue')!r}")
    binding = prior.get("binding", {})
    for name in _SAME_LEG:
        if binding.get(name) != os.environ.get(name):
            problems.append(f"preflight {name}={binding.get(name)!r} is not this leg's")
    try:
        text = junit_path.read_text()
        record["junit_sha256"] = hashlib.sha256(text.encode()).hexdigest()
        outcomes = parse_junit(text, datetime.fromisoformat(prior["started_at"]))
    except (OSError, KeyError, ValueError) as exc:
        return record | {"problems": [*problems, f"JUnit not usable: {exc}"]}
    observed, outcome_problems = judge_outcomes(
        required_outcomes(expectations, expectations.venues[venue_id]), outcomes
    )
    return record | {"outcomes": observed, "problems": problems + outcome_problems}


# --- CLI ----------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="A5 kernel CI venue gate")
    parser.add_argument("command", choices=("preflight", "check"))
    parser.add_argument("--venue", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--expectations", type=Path, default=EXPECTATIONS)
    parser.add_argument("--preflight", type=Path, help="check: this leg's preflight record")
    parser.add_argument("--junit", type=Path, help="check: this leg's fresh JUnit file")
    args = parser.parse_args(argv)

    raw_bytes = args.expectations.read_bytes()
    try:
        expectations = parse_expectations(json.loads(raw_bytes))
    except (ExpectationsError, ValueError) as exc:
        print(f"a5-kernel-ci: {exc}", file=sys.stderr)
        return 2
    if args.venue not in expectations.venues:
        print(f"a5-kernel-ci: unknown venue {args.venue!r}", file=sys.stderr)
        return 2
    if args.command == "check" and (args.preflight is None or args.junit is None):
        parser.error("check needs --preflight and --junit")

    raw_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    record = (
        preflight(args.venue, expectations, raw_sha256)
        if args.command == "preflight"
        else check(args.venue, expectations, args.preflight, args.junit)
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
