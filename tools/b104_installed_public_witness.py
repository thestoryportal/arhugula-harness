"""Evaluation-only installed B-104 root-resume witness; `run` needs separate approval.

One bounded attempt against a noneditable installed venv. The parent (stdlib only,
`python -I`) verifies the pinned candidate, wheels and startup hooks, owns a loopback
webhook listener and a fresh non-tmpfs scenario root, and runs each phase as its own
installed-venv `python -I` child in a private process group:

1. `capture`: public `api.run` of a provider-free TOOL_STEP whose PRE_ACTION HITL gate is
   durable-async (TEAM_BINDING x RECONCILER_LOOP). The gate delivers one webhook and the
   run PAUSES; the durable journal holds the depth-0 root record. The tool never runs.
2. `resume-a`: public `api.resume(resume_handle=...)`. The workflow's own step dispatcher
   is an explicit in-body barrier: it writes a marker, then blocks until killed.
3. `observe-held`: while A blocks, installed claim code reads the claim as `started` and
   the lease as busy. The parent then SIGKILLs only A's process group and reaps it.
4. `resume-b`: a fresh process resumes the same record and must get the typed
   `ResumeClaimRefusedError(claim-refused)` with no body, webhook or tool replay.
5. `recover`: installed `PauseClaimRecovery`. A release of the started claim must be HELD
   with no mutation; an abandon, attested by the parent's kill record, must be ABANDONED
   with a durable INTENT and COMPLETE audit and a tombstone.
6. `resume-after-abandon`: a fresh resume is refused again with no body.

Every child re-proves its own interpreter, `sys.path`, installed RECORD bytes and the
origin of every loaded `harness_*` module before and after its phase.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib
import importlib.metadata
import json
import os
import signal
import socket
import stat
import subprocess
import sys
import threading
import time
import traceback
import zipfile
from collections.abc import Callable
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

WORKFLOW_ID = "b104-installed-root-witness"
TOOL_NAME = "b104_witness_echo"
CHILD_CAP_SECONDS = 60
OVERALL_CAP_SECONDS = 420
MAX_BODY_BYTES = 4096
OUTPUT_CAP_BYTES = 1024 * 1024
NON_DURABLE_FILESYSTEMS = frozenset({"tmpfs", "ramfs"})
# The four IS path classes (C-IS-01 §1). The parent is stdlib-only, so a pure test pins
# this list against `harness_is.path_class_registry.PathClass`.
PATH_CLASSES = ("SKILLS", "PROMPTS", "ROUTING_MANIFEST", "STATE_LEDGER")
PHASES = (
    "capture",
    "resume-a",
    "observe-held",
    "resume-b",
    "recover",
    "resume-after-abandon",
)
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
PLAN = {
    "scope": "installed public api.run pause, then api.resume by handle in two processes",
    "phases": list(PHASES),
    "provider_free": "TOOL_STEP gated before dispatch; the witness MCP tool must never run",
    "external_effects": "owned 127.0.0.1 webhook listener and loopback MCP tool server",
    "child_cap_seconds": CHILD_CAP_SECONDS,
    "overall_cap_seconds": OVERALL_CAP_SECONDS,
    "attempts": 1,
    "state_root": "new directory on a non-tmpfs filesystem outside every Git checkout",
    "s5": "process/filesystem behaviour only; says nothing about VM reset durability",
    "outcome": "PASS needs every case; a timeout is INCONCLUSIVE; anything else FAILs",
}


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


def checked_candidate(candidate: Path, venv: Path, expected_head: str) -> tuple[Path, Path, Path]:
    """Require a clean pinned tree and a selected installed Python before effects."""
    root = candidate.resolve(strict=True)
    if len(expected_head) != 40 or any(c not in "0123456789abcdef" for c in expected_head):
        raise ValueError("expected-head must be a full lowercase Git SHA")
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
    if head != expected_head or status:
        raise ValueError("candidate HEAD differs from pin or tree is not clean")
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


# --- the scenario root: fresh, owned, durable, outside every checkout ---------------------


def filesystem_type(mountinfo: str, path: Path) -> str | None:
    """Filesystem type of the longest mount covering `path` (later lines win on ties)."""
    best: tuple[int, str] | None = None
    for line in mountinfo.splitlines():
        fields = line.split(" ")
        if "-" not in fields[6:]:
            continue
        separator = fields.index("-", 6)
        mount = Path(fields[4].encode().decode("unicode_escape"))
        if path == mount or mount in path.parents:
            depth = len(mount.parts)
            if best is None or depth >= best[0]:
                best = (depth, fields[separator + 1])
    return None if best is None else best[1]


def checked_scenario_root(root: Path, mountinfo: str) -> dict[str, object]:
    """Accept only a new directory under an owned, durable parent outside every checkout."""
    if not root.is_absolute() or root.name in {"", ".", ".."}:
        raise ValueError("scenario root must be an absolute new directory name")
    if os.path.lexists(root):
        raise ValueError("scenario root must not exist yet")
    parent = root.parent
    meta = parent.lstat()
    if not stat.S_ISDIR(meta.st_mode) or meta.st_uid != os.geteuid():
        raise ValueError("scenario root parent must be an owned real directory")
    if parent.resolve(strict=True) != parent:
        raise ValueError("scenario root parent path contains a symlink")
    checkouts = [p for p in (parent, *parent.parents) if os.path.lexists(p / ".git")]
    if checkouts:
        raise ValueError(f"scenario root is inside a Git checkout: {checkouts[0]}")
    fs_type = filesystem_type(mountinfo, parent)
    if fs_type is None or fs_type in NON_DURABLE_FILESYSTEMS:
        raise ValueError(f"scenario root filesystem is not durable: {fs_type}")
    return {"root": str(root), "parent": str(parent), "filesystem_type": fs_type}


@dataclass(frozen=True)
class Layout:
    """Every path the scenario uses, derived from its one root."""

    root: Path

    @property
    def repo(self) -> Path:
        return self.root / "repo"

    @property
    def state_root(self) -> Path:
        return self.root / "state"

    @property
    def ledger_dir(self) -> Path:
        return self.state_root / "state-ledger"

    @property
    def home(self) -> Path:
        return self.root / "home"

    @property
    def tmp(self) -> Path:
        return self.root / "tmp"

    @property
    def config(self) -> Path:
        return self.root / "harness.toml"

    @property
    def mcp_server(self) -> Path:
        return self.root / "b104_witness_mcp_server.py"

    @property
    def tool_calls(self) -> Path:
        return self.root / "tool-calls.log"

    @property
    def results(self) -> Path:
        return self.root / "results"

    @property
    def markers(self) -> Path:
        return self.root / "markers"

    def result(self, phase: str) -> Path:
        return self.results / f"{phase}.json"


MCP_SERVER_SOURCE = '''"""B-104 witness loopback MCP server: one tool that must never be called."""
import sys
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("b104-installed-witness", host="127.0.0.1", port=int(sys.argv[2]))


@mcp.tool()
def b104_witness_echo(value: str) -> str:
    """Record the call; the witness fails if any call is recorded."""
    with open(sys.argv[1], "a", encoding="utf-8") as calls:
        calls.write(value + "\\n")
    return value


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
'''


def config_text(layout: Layout, webhook_port: int, mcp_port: int) -> str:
    """The operator TOML: placed durable state, loopback webhook and the witness MCP tool.

    The tool server is loopback streamable-HTTP at L3 with a READ_ONLY blast radius, so its
    sandbox floor is the process tier; a stdio server would floor to a microVM tier that
    needs an execution driver this host does not have.
    """
    lines = [
        "[runtime]",
        'deployment_surface = "local-development"',
        f"repository_root = {json.dumps(str(layout.repo))}",
        'default_topology = "single-threaded-linear"',
        "ollama_optional = true",
        # A's body blocks at the barrier until the parent kills it; the drain bound must
        # not answer first.
        f"drain_timeout_seconds = {OVERALL_CAP_SECONDS}",
        "[runtime.state_placement]",
        f"state_root = {json.dumps(str(layout.state_root))}",
        "forbidden_roots = []",
        "[runtime.pause_resume_protocol_config]",
        "durable = true",
        "[runtime.otel]",
        'otlp_endpoint = "http://127.0.0.1:9"',
        "[runtime.webhook_delivery_composer_config]",
        'webhook_id = "b104-installed-witness"',
        f'endpoint_url = "http://127.0.0.1:{webhook_port}/hook"',
        "timeout_seconds = 3",
        "[[runtime.mcp_clients]]",
        'client_name = "b104-witness"',
        'transport = "streamable_http_l3"',
        'trust_level = "L3_ALLOW_WITH_AUDIT"',
        'blast_radius = "READ_ONLY"',
        f'connection_url = "http://127.0.0.1:{mcp_port}/mcp"',
        "[runtime.routing_manifest]",
        "manifest_version = 1",
        "per_role_bindings = {}",
        "per_workload_overrides = {}",
        "retry_policies = {}",
        'fallback_chains = [{ primary = { provider = "ollama", model = "llama3.2:3b", '
        'family = "local_open_weight" }, same_family = [], cross_family = [] }]',
    ]
    for path_class in PATH_CLASSES:
        cell = (
            layout.ledger_dir
            if path_class == "STATE_LEDGER"
            else layout.repo / "bindings" / path_class.lower()
        )
        lines.extend(
            (
                "[[runtime.path_bindings.raw_entries]]",
                f"path_class = {json.dumps(path_class)}",
                'workflow_class = "software-engineering"',
                'deployment_surface = "local-development"',
                f"path = {json.dumps(str(cell))}",
            )
        )
    return "\n".join(lines) + "\n"


def write_new(path: Path, text: str, mode: int = 0o600) -> None:
    """Create `path` exactly once with `mode`, fsynced."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC, mode)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(text)
        stream.flush()
        os.fsync(stream.fileno())


def write_json_new(path: Path, value: object) -> None:
    write_new(path, json.dumps(value, sort_keys=True, indent=2, default=str) + "\n")


# --- child phases (installed Python only; harness imports stay inside) --------------------


def _workflow(dispatcher: object | None) -> object:
    """The public `WorkflowObject`: one gated TOOL_STEP; `None` uses the real registry."""
    from harness_core.identity import StepID
    from harness_core.persona_tier import PersonaTier
    from harness_core.workload_class import WorkloadClass
    from harness_cp.cp_shared_types import ModelBinding
    from harness_cp.cross_family_fallback_chain import (
        FallbackChain,
        ProviderCandidate,
        ProviderFamily,
    )
    from harness_cp.engine_class import EngineClass
    from harness_cp.hitl_placement import HITLPlacement, HITLPlacementKind
    from harness_cp.topology_pattern import TopologyPattern
    from harness_cp.workflow_driver_types import StepKind, WorkflowStep
    from harness_cp.workflow_manifest_entry import WorkflowManifestEntry

    chain = FallbackChain(
        primary=ProviderCandidate(
            provider="ollama", model="llama3.2:3b", family=ProviderFamily.LOCAL_OPEN_WEIGHT
        ),
        same_family=(),
        cross_family=(),
        terminal=None,
    )

    class Workflow:
        workflow_id = WORKFLOW_ID
        workload_class = WorkloadClass.SOFTWARE_ENGINEERING
        default_model_binding = ModelBinding(provider="ollama", model="llama3.2:3b")
        # TEAM_BINDING x RECONCILER_LOOP is the DURABLE_ASYNC cell, and TEAM_BINDING's
        # ASK floor cannot be lowered by the solo auto-approve policy: the gate pauses.
        manifest_entry = WorkflowManifestEntry(
            workflow_id=WORKFLOW_ID,
            workload_class=WorkloadClass.SOFTWARE_ENGINEERING,
            persona_tier=PersonaTier.TEAM_BINDING,
            engine_class=EngineClass.RECONCILER_LOOP,
            topology_pattern=TopologyPattern.SINGLE_THREADED_LINEAR,
            layer_budgets=(),
            fallback_chain=chain,
            hitl_placements=(HITLPlacement(position=HITLPlacementKind.PRE_ACTION),),
            per_step_overrides={},
        )
        steps = (
            WorkflowStep(
                step_id=StepID("step-0"),
                step_kind=StepKind.TOOL_STEP,
                step_payload={"tool_id": TOOL_NAME, "tool_args": {"value": "b104"}},
            ),
        )

    class OverrideWorkflow(Workflow):
        def __init__(self, body: object) -> None:
            self.step_dispatchers = _Registry(body)

    return Workflow() if dispatcher is None else OverrideWorkflow(dispatcher)


class _Registry:
    def __init__(self, dispatcher: object) -> None:
        self._dispatcher = dispatcher

    def lookup(self, step_kind: object) -> object:
        _ = step_kind
        return self._dispatcher


class _MarkerBody:
    """A resumed step body that records its entry durably, then optionally holds."""

    def __init__(self, marker: Path, *, hold: bool) -> None:
        self._marker = marker
        self._hold = hold

    def dispatch(self, binding: object, step: Any, *, step_context: object = None) -> object:
        _ = binding, step_context
        write_json_new(
            self._marker,
            {"pid": os.getpid(), "pgid": os.getpgid(0), "step_id": str(step.step_id)},
        )
        if self._hold:
            # [LAW:no-ambient-temporal-coupling] The explicit in-body barrier: the parent
            # observes the marker, inspects the claim, then kills this process group.
            threading.Event().wait()
        return {"body": "ran"}


def _config(layout: Layout) -> Any:
    from harness_runtime.config_source import RuntimeConfigSource

    return RuntimeConfigSource.load(config_file=layout.config)


def _record(layout: Layout, config: Any) -> dict[str, object]:
    """The journal's latest record for the workflow, as its exact ref, via installed code."""
    from harness_core import JournalRecordRef
    from harness_runtime.lifecycle.journal_workflow_pause_store import (
        JournalWorkflowPauseStore,
        pause_journal_dir_for,
    )
    from harness_runtime.lifecycle.protected_result_store import normalize_tenant_scope

    journal_dir = pause_journal_dir_for(layout.ledger_dir)
    read = JournalWorkflowPauseStore(
        journal_dir=journal_dir, tenant_id=config.tenant_id
    ).read_latest_attributed(WORKFLOW_ID)
    if read.snapshot is None or read.latest_record_digest is None:
        raise ValueError(f"no durable root record: cause={read.cause}")
    ref = JournalRecordRef(
        tenant=normalize_tenant_scope(config.tenant_id),
        workflow_id=read.snapshot.workflow_id,
        run_id=read.snapshot.run_id,
        record_count=read.record_count,
        latest_digest=read.latest_record_digest,
        snapshot_hash=read.snapshot.snapshot_hash,
    )
    return {"journal_dir": journal_dir, "ref": ref, "depth": read.depth}


def _store(journal_dir: Path, config: Any) -> Any:
    from harness_runtime.config.state_placement import place_state_dir, probe_declared_state_root
    from harness_runtime.lifecycle.resume_claim_store import ResumeClaimStore

    placement = place_state_dir(
        journal_dir, config, probe_declared_state_root(config), what="witness pause journal"
    )
    return placement, ResumeClaimStore(placement=placement, tenant_id=config.tenant_id)


def _claim_view(store: Any, ref: Any) -> dict[str, object]:
    """The claim phase and lease state for `ref`, read through installed claim code."""
    from harness_runtime.lifecycle.resume_claim_store import (
        HeldLease,
        InvalidClaim,
        LeaseBusy,
        LeaseMissing,
        StartedOrUnknown,
        UnstartedProof,
        parse_claim,
    )

    paths = store.paths_for(ref)
    raw = paths.claim.read_bytes() if paths.claim.exists() else None
    match None if raw is None else parse_claim(raw, ref):
        case None:
            phase = "absent"
        case UnstartedProof():
            phase = "claimed"
        case StartedOrUnknown(phase=started):
            phase = started
        case InvalidClaim():
            phase = "invalid"
    probe = store.probe_lease(ref)
    lease = {HeldLease: "free", LeaseBusy: "busy", LeaseMissing: "missing"}.get(
        type(probe), "invalid"
    )
    if isinstance(probe, HeldLease):
        probe.close()
    return {
        "claim_path": str(paths.claim),
        "claim_sha256": None if raw is None else hashlib.sha256(raw).hexdigest(),
        "claim_text": None if raw is None else raw.decode("utf-8", "replace"),
        "phase": phase,
        "lease": lease,
    }


def _ref_json(ref: Any) -> dict[str, object]:
    return ref.model_dump(mode="json")


def _resume_outcome(layout: Layout, marker: Path, *, hold: bool) -> dict[str, object]:
    """Public `api.resume` by handle; the typed refusal is an outcome, not a crash."""
    import asyncio

    from harness_runtime import api

    config = _config(layout)
    try:
        result = asyncio.run(
            api.resume(
                _workflow(_MarkerBody(marker, hold=hold)),
                resume_handle=WORKFLOW_ID,
                config=config,
            )
        )
    except api.ResumeClaimRefusedError as refused:
        causes = []
        cause = refused.__cause__
        while cause is not None:
            causes.append(f"{type(cause).__module__}.{type(cause).__qualname__}")
            cause = cause.__cause__
        outcome: dict[str, object] = {
            "outcome": "refused",
            "error_type": f"{type(refused).__module__}.{type(refused).__qualname__}",
            "reason": refused.reason.value,
            "message": str(refused),
            "cause_chain": causes,
        }
    else:
        outcome = {"outcome": "returned", "status": result.status}
    record = _record(layout, config)
    _placement, store = _store(record["journal_dir"], config)
    outcome["ref"] = _ref_json(record["ref"])
    outcome["claim"] = _claim_view(store, record["ref"])
    outcome["body_marker_present"] = marker.exists()
    return outcome


def phase_capture(layout: Layout) -> dict[str, object]:
    import asyncio

    from harness_runtime import api

    config = _config(layout)
    result = asyncio.run(api.run(_workflow(None), config=config))
    snapshot = result.pause_snapshot
    record = _record(layout, config)
    _placement, store = _store(record["journal_dir"], config)
    journal_file = store.paths_for(record["ref"]).journal
    return {
        "status": result.status,
        "run_id": None if snapshot is None else snapshot.run_id,
        "snapshot_hash": None if snapshot is None else snapshot.snapshot_hash,
        "depth": record["depth"],
        "ref": _ref_json(record["ref"]),
        "journal_file": str(journal_file),
        "journal_sha256": sha256(journal_file),
        "claim": _claim_view(store, record["ref"]),
    }


def phase_resume_a(layout: Layout) -> dict[str, object]:
    # Only reached if the barrier releases: the parent kills this process at the barrier.
    return _resume_outcome(layout, layout.markers / "a-body.json", hold=True)


def phase_observe_held(layout: Layout) -> dict[str, object]:
    config = _config(layout)
    record = _record(layout, config)
    _placement, store = _store(record["journal_dir"], config)
    return {"ref": _ref_json(record["ref"]), "claim": _claim_view(store, record["ref"])}


def phase_resume_b(layout: Layout) -> dict[str, object]:
    return _resume_outcome(layout, layout.markers / "b-body.json", hold=False)


def phase_resume_after_abandon(layout: Layout) -> dict[str, object]:
    return _resume_outcome(layout, layout.markers / "d-body.json", hold=False)


def _journal_inventory(journal_dir: Path, ledger: Path) -> dict[str, str]:
    files = {p.name: sha256(p) for p in sorted(journal_dir.iterdir()) if p.is_file()}
    files["<ledger>"] = sha256(ledger) if ledger.exists() else "absent"
    return files


def phase_recover(layout: Layout) -> dict[str, object]:
    from datetime import UTC, datetime

    from harness_is.jsonl_event_ledger_lifecycle import JsonlLedgerHandle
    from harness_is.state_ledger_entry_schema import QuiescenceAttestation
    from harness_is.state_ledger_write import read_ledger
    from harness_runtime.admin.pause_claim_recovery import (
        ClaimAbandon,
        ClaimRelease,
        PauseClaimRecovery,
    )
    from harness_runtime.lifecycle.resume_claim_store import parse_claim

    config = _config(layout)
    record = _record(layout, config)
    ref = record["ref"]
    placement, store = _store(record["journal_dir"], config)
    claim = store.paths_for(ref).claim
    claimed_ref = getattr(parse_claim(claim.read_bytes(), ref), "record_ref", None)
    ledger_path = layout.ledger_dir / "state.jsonl"
    ledger = JsonlLedgerHandle(
        canonical_path=ledger_path,
        exists=ledger_path.exists(),
        entry_count=sum(1 for line in ledger_path.read_text().splitlines() if line.strip()),
    )
    recovery = PauseClaimRecovery(placement=placement, tenant_id=config.tenant_id, ledger=ledger)
    uid = os.getuid()
    kill_record = layout.result("a-kill")
    before = _journal_inventory(record["journal_dir"], ledger_path)
    release = recovery.recover(
        ClaimRelease(
            record_ref=ref,
            action_id="b104w-release-1",
            operator_uid=uid,
            reason_digest=hashlib.sha256(
                b"b104 witness: a started claim is not released"
            ).hexdigest(),
        )
    )
    after_release = _journal_inventory(record["journal_dir"], ledger_path)
    abandon = recovery.recover(
        ClaimAbandon(
            record_ref=ref,
            action_id="b104w-abandon-1",
            operator_uid=uid,
            reason_digest=hashlib.sha256(b"b104 witness: holder killed at barrier").hexdigest(),
            quiescence_attestation=QuiescenceAttestation(
                operator_uid=uid,
                attested_at=datetime.now(UTC),
                stopped_services_digest=sha256(kill_record),
                no_workers_observed=True,
                restart_disabled=True,
            ),
        )
    )
    after_abandon = _journal_inventory(record["journal_dir"], ledger_path)
    identity = (ref.tenant, ref.workflow_id, ref.record_count, ref.latest_digest)
    audits = [
        {
            "scope": audit.scope,
            "phase": audit.phase,
            "action": audit.action,
            "action_id": audit.action_id,
            "stopped_services_digest": None
            if audit.quiescence_attestation is None
            else audit.quiescence_attestation.stopped_services_digest,
        }
        for entry in read_ledger(ledger)
        if (audit := entry.recovery_audit) is not None
        and (
            audit.record_identity.tenant_id,
            audit.record_identity.workflow_id,
            audit.record_identity.record_count,
            audit.record_identity.latest_digest,
        )
        == identity
    ]
    return {
        "ref": _ref_json(ref),
        "claim_frame_names_record": claimed_ref == ref,
        "kill_record_sha256": sha256(kill_record),
        "release": {"outcome": release.outcome.value, "reason": release.reason},
        "abandon": {"outcome": abandon.outcome.value, "reason": abandon.reason},
        "inventory_before": before,
        "inventory_after_release": after_release,
        "inventory_after_abandon": after_abandon,
        "tombstones": sorted(n for n in after_abandon if ".resume-tombstone-" in n),
        "audits": audits,
        "claim_after": _claim_view(store, ref),
    }


PHASE_BODIES: dict[str, Callable[[Layout], dict[str, object]]] = {
    "capture": phase_capture,
    "resume-a": phase_resume_a,
    "observe-held": phase_observe_held,
    "resume-b": phase_resume_b,
    "recover": phase_recover,
    "resume-after-abandon": phase_resume_after_abandon,
}


def run_phase(layout: Layout, phase: str, prove: Callable[[], dict[str, object]]) -> int:
    """Prove this interpreter, run one phase, re-prove the loaded modules, record once."""
    try:
        evidence = prove()
        observed = PHASE_BODIES[phase](layout)
        verified = {
            path
            for item in evidence.get("installed_origins", {}).values()
            for path in item["verified_files"]
        }
        loaded = loaded_harness_origins(verified) if verified else {}
        write_json_new(
            layout.result(phase),
            {
                "phase": phase,
                "ok": True,
                "provenance": evidence,
                "observed": observed,
                "loaded_harness_modules": len(loaded),
            },
        )
        return 0
    except BaseException as exc:  # recorded, then re-raised: a crash is evidence, not a pass
        write_json_new(
            layout.result(phase),
            {"phase": phase, "ok": False, "error": repr(exc), "traceback": traceback.format_exc()},
        )
        raise


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


# --- the parent: listener, children, kill, evaluation --------------------------------------


class LoopbackCapture:
    """One owned 127.0.0.1 server recording every request; only the capture may call it."""

    def __init__(self) -> None:
        self.requests: list[dict[str, object]] = []
        self.errors: list[str] = []
        owner = self

        class Handler(BaseHTTPRequestHandler):
            timeout = 3

            def do_POST(self) -> None:
                self.connection.settimeout(3)
                try:
                    raw_length = self.headers.get("Content-Length")
                    if raw_length is None or not raw_length.isdecimal():
                        raise ValueError("missing or invalid Content-Length")
                    length = int(raw_length)
                    if length > MAX_BODY_BYTES or self.headers.get("Transfer-Encoding"):
                        raise ValueError("oversized or chunked request")
                    body = self.rfile.read(length)
                    owner.requests.append(
                        {"path": self.path, "at": time.monotonic(), "body": json.loads(body)}
                    )
                    self.send_response(200)
                except (OSError, ValueError) as exc:
                    owner.errors.append(str(exc))
                    self.send_response(400)
                self.send_header("Content-Length", "0")
                self.send_header("Connection", "close")
                self.end_headers()

            def do_GET(self) -> None:
                owner.errors.append(f"unexpected {self.command} request")
                self.send_response(405)
                self.send_header("Content-Length", "0")
                self.end_headers()

            def log_message(self, _format: str, *_args: object) -> None:
                return

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(
            target=self.server.serve_forever, kwargs={"poll_interval": 0.05}
        )

    @property
    def port(self) -> int:
        return int(self.server.server_address[1])

    def start(self) -> None:
        self.thread.start()

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        if self.thread.is_alive():
            raise RuntimeError("owned loopback listener did not stop")


@dataclass
class Child:
    """One started phase process in its own group, with its log paths."""

    phase: str
    proc: subprocess.Popen[bytes]
    stdout: Path
    stderr: Path
    started: float


Launcher = Callable[[str], Child]


def child_argv(python: Path, helper: Path, phase: str, fixed: list[str]) -> list[str]:
    return [str(python), "-I", str(helper), "_child", phase, *fixed]


def child_env(layout: Layout) -> dict[str, str]:
    return {
        "PATH": "/usr/bin:/bin",
        "HOME": str(layout.home),
        "TMPDIR": str(layout.tmp),
        "LANG": "C.UTF-8",
        "NO_COLOR": "1",
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "OTEL_EXPORTER_OTLP_TIMEOUT": "1",
    }


def spawn(argv: list[str], env: dict[str, str], cwd: Path, logs: Path, phase: str) -> Child:
    stdout, stderr = logs / f"{phase}.stdout", logs / f"{phase}.stderr"
    with stdout.open("xb") as out, stderr.open("xb") as err:
        proc = subprocess.Popen(
            argv,
            cwd=cwd,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=out,
            stderr=err,
            start_new_session=True,
        )
    return Child(phase, proc, stdout, stderr, time.monotonic())


def kill_group(child: Child) -> dict[str, object]:
    """SIGKILL only this child's own process group, reap it, and prove the group is gone."""
    pgid = child.proc.pid
    try:
        os.killpg(pgid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        code = child.proc.wait(timeout=5)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"{child.phase} group did not reap after KILL") from exc
    gone = False
    for _ in range(100):
        try:
            os.killpg(pgid, 0)
        except ProcessLookupError:
            gone = True
            break
        time.sleep(0.05)
    return {"pgid": pgid, "signal": "SIGKILL", "returncode": code, "group_gone": gone}


def finish(child: Child, deadline: float) -> dict[str, object]:
    """Wait within the child and overall caps; a timeout kills the group and is recorded."""
    cap = min(CHILD_CAP_SECONDS - (time.monotonic() - child.started), deadline - time.monotonic())
    timed_out = False
    try:
        child.proc.wait(timeout=max(cap, 0.0))
    except subprocess.TimeoutExpired:
        timed_out = True
    kill = kill_group(child) if timed_out else None
    return {
        **stream_record(child),
        "exit": child.proc.returncode,
        "timeout": timed_out,
        "kill": kill,
    }


def stream_record(child: Child) -> dict[str, object]:
    sizes = {"stdout": child.stdout.stat().st_size, "stderr": child.stderr.stat().st_size}
    return {
        "phase": child.phase,
        "pid": child.proc.pid,
        "pgid": child.proc.pid,
        "streams": {
            name: {"path": str(path), "bytes": sizes[name], "sha256": sha256(path)}
            for name, path in (("stdout", child.stdout), ("stderr", child.stderr))
        },
        "output_ok": all(size < OUTPUT_CAP_BYTES for size in sizes.values()),
        "elapsed_seconds": round(time.monotonic() - child.started, 3),
    }


def wait_for_marker(child: Child, marker: Path, deadline: float) -> bool:
    """Wait for A's in-body marker while A lives, within the child and overall caps."""
    limit = min(child.started + CHILD_CAP_SECONDS, deadline)
    while time.monotonic() < limit:
        if marker.exists():
            return True
        if child.proc.poll() is not None:
            return False
        time.sleep(0.05)
    return marker.exists()


def free_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def wait_listening(child: Child, port: int, deadline: float) -> bool:
    """Wait for the tool server's loopback port while it lives, within its caps."""
    limit = min(child.started + CHILD_CAP_SECONDS, deadline)
    while time.monotonic() < limit and child.proc.poll() is None:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.05)
    return False


def with_services(
    layout: Layout,
    python: Path,
    logs: Path,
    deadline: float,
    body: Callable[[LoopbackCapture], dict[str, object]],
) -> dict[str, object]:
    """Own the webhook listener and the witness tool server for exactly the scenario's life."""
    capture = LoopbackCapture()
    tool_port = free_loopback_port()
    write_new(layout.mcp_server, MCP_SERVER_SOURCE)
    write_new(layout.config, config_text(layout, capture.port, tool_port))
    capture.start()
    server = spawn(
        [str(python), "-I", str(layout.mcp_server), str(layout.tool_calls), str(tool_port)],
        {"PATH": "/usr/bin:/bin", "HOME": str(layout.home), "TMPDIR": str(layout.tmp)},
        layout.tmp,
        logs,
        "tool-server",
    )
    ready = False
    try:
        ready = wait_listening(server, tool_port, deadline)
        evidence = body(capture) if ready else {"runs": {}, "results": {}}
    finally:
        tool_server = {**stream_record(server), "ready": ready, "kill": kill_group(server)}
        capture.close()
    evidence["tool_server"] = tool_server
    evidence["webhook_requests"] = capture.requests
    evidence["webhook_errors"] = capture.errors
    evidence["tool_calls"] = (
        len(layout.tool_calls.read_text().splitlines()) if layout.tool_calls.exists() else 0
    )
    return evidence


def load_result(layout: Layout, phase: str) -> dict[str, object] | None:
    path = layout.result(phase)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def scenario(
    layout: Layout, launch: Launcher, capture: LoopbackCapture, deadline: float
) -> dict[str, object]:
    """Run the phases in order, stopping at the first phase that cannot continue."""
    runs: dict[str, object] = {}
    results: dict[str, object] = {}

    def complete(phase: str) -> bool:
        runs[phase] = finish(launch(phase), deadline)
        results[phase] = load_result(layout, phase)
        return not runs[phase]["timeout"] and runs[phase]["exit"] == 0

    if complete("capture"):
        webhooks_after_capture = len(capture.requests)
        a = launch("resume-a")
        entered = wait_for_marker(a, layout.markers / "a-body.json", deadline)
        observed = entered and complete("observe-held")
        # A genuine timeout is A still running without its marker; A exiting early without
        # one is a failure, not a timeout.
        still_running = a.proc.poll() is None
        runs["resume-a"] = {
            **stream_record(a),
            "exit": None,
            "timeout": not entered and still_running,
            "kill": kill_group(a),
            "barrier_entered": entered,
        }
        results["resume-a"] = load_result(layout, "resume-a")
        write_json_new(layout.result("a-kill"), runs["resume-a"]["kill"])
        if observed and complete("resume-b") and complete("recover"):
            complete("resume-after-abandon")
        runs["webhooks_after_capture"] = webhooks_after_capture
    return {"runs": runs, "results": results}


def _dict(value: object) -> dict[str, Any]:
    """A record as a mapping; a missing or malformed record reads as empty and fails its checks."""
    return value if isinstance(value, dict) else {}  # pyright: ignore[reportUnknownVariableType]


def _observed(results: dict[str, object], phase: str) -> dict[str, Any]:
    item = _dict(results.get(phase))
    return _dict(item.get("observed")) if item.get("ok") is True else {}


def evaluate(evidence: dict[str, object]) -> dict[str, object]:
    """Pure per-case predicates over the recorded evidence; PASS needs every check.

    Verdict order: a surviving owned process group FAILs (cleanup is never inconclusive);
    otherwise a genuine timeout is INCONCLUSIVE; otherwise PASS only if every check holds.
    """
    runs = _dict(evidence.get("runs"))
    results = _dict(evidence.get("results"))
    webhooks = evidence.get("webhook_requests")
    tool_server = _dict(evidence.get("tool_server"))
    tool_calls = evidence.get("tool_calls")
    capture = _observed(results, "capture")
    held = _observed(results, "observe-held")
    b = _observed(results, "resume-b")
    recover = _observed(results, "recover")
    d = _observed(results, "resume-after-abandon")
    ref = capture.get("ref")
    run_a = _dict(runs.get("resume-a"))
    kill = _dict(run_a.get("kill"))
    # A result without its provenance counts as uninstalled, never as a crash of the verdict.
    provenance = [
        _dict(item.get("provenance"))
        for item in map(_dict, results.values())
        if item.get("ok") is True
    ]
    receipt_hashes = {p.get("installation_receipt_sha256") for p in provenance}
    raw_audits = recover.get("audits")
    audits = [_dict(a) for a in raw_audits] if isinstance(raw_audits, list) else []
    abandon_audits = [a for a in audits if a.get("action_id") == "b104w-abandon-1"]
    release = _dict(recover.get("release"))

    def refused_without_replay(outcome: dict[str, Any]) -> dict[str, bool]:
        return {
            "typed_refusal": outcome.get("outcome") == "refused"
            and outcome.get("error_type")
            == "harness_runtime.lifecycle.root_resume_admission.ResumeClaimRefusedError"
            and outcome.get("reason") == "claim-refused",
            "no_body": outcome.get("body_marker_present") is False,
            "same_record": outcome.get("ref") == ref,
            "claim_still_started": _dict(outcome.get("claim")).get("phase") == "started",
        }

    # [LAW:no-silent-failure] Every owned group the parent killed must be proven gone, and
    # every phase it waited for must have exited 0 within its cap with bounded output.
    killed = {"tool-server": _dict(tool_server.get("kill"))} | {
        phase: _dict(_dict(run).get("kill"))
        for phase, run in runs.items()
        if _dict(run).get("kill") is not None
    }
    cleanup = {f"{phase}-group-gone": k.get("group_gone") is True for phase, k in killed.items()}
    processes = (
        {
            f"{phase}-exited-0": _dict(runs.get(phase)).get("exit") == 0
            and _dict(runs.get(phase)).get("timeout") is False
            for phase in PHASES
            if phase != "resume-a"
        }
        | {
            f"{phase}-output-bounded": _dict(runs.get(phase)).get("output_ok") is True
            for phase in PHASES
        }
        | {"tool-server-output-bounded": tool_server.get("output_ok") is True}
    )
    cases: dict[str, dict[str, bool]] = {
        "cleanup": cleanup,
        "processes": processes,
        "provenance": {
            "every_phase_recorded": all(
                isinstance(results.get(p), dict) for p in PHASES if p != "resume-a"
            ),
            "every_child_installed": len(provenance) == len(PHASES) - 1
            and all(_dict(p.get("interpreter")).get("isolated") for p in provenance),
            "one_receipt": len(receipt_hashes) == 1,
        },
        "capture": {
            "paused": capture.get("status") == "paused",
            "root_record": capture.get("depth") == 0 and ref is not None,
            "snapshot_is_record": capture.get("snapshot_hash") == _dict(ref).get("snapshot_hash"),
            "no_claim_yet": _dict(capture.get("claim")).get("phase") == "absent",
            "one_webhook": runs.get("webhooks_after_capture") == 1,
        },
        "resume-a-started": {
            "barrier_entered": run_a.get("barrier_entered") is True,
            "started_before_kill": _dict(held.get("claim")).get("phase") == "started",
            "lease_held_by_a": _dict(held.get("claim")).get("lease") == "busy",
            "same_record": held.get("ref") == ref,
            "killed_by_parent": kill.get("signal") == "SIGKILL"
            and kill.get("returncode") == -signal.SIGKILL
            and kill.get("group_gone") is True,
            "no_result_from_a": results.get("resume-a") is None,
        },
        "resume-b-refused": {
            **refused_without_replay(b),
            "lease_released_by_kill": _dict(b.get("claim")).get("lease") == "free",
            "claim_bytes_unchanged": _dict(b.get("claim")).get("claim_sha256")
            == _dict(held.get("claim")).get("claim_sha256"),
        },
        "release-held": {
            "held": release.get("outcome") == "held"
            and str(release.get("reason", "")).startswith("release-forbidden"),
            "no_mutation": recover.get("inventory_before") is not None
            and recover.get("inventory_before") == recover.get("inventory_after_release"),
            "no_release_audit": isinstance(raw_audits, list)
            and not any(a.get("action") == "release" for a in audits),
        },
        "abandon-audited": {
            "abandoned": _dict(recover.get("abandon")).get("outcome") == "abandoned",
            "exact_record": recover.get("claim_frame_names_record") is True
            and recover.get("ref") == ref,
            "intent_and_complete": sorted(str(a.get("phase")) for a in abandon_audits)
            == ["complete", "intent"],
            "attested_by_kill_record": all(
                a.get("stopped_services_digest") == recover.get("kill_record_sha256")
                for a in abandon_audits
            ),
            "tombstoned": isinstance(recover.get("tombstones"), list)
            and len(recover["tombstones"]) == 1,
            "claim_bytes_kept": _dict(recover.get("claim_after")).get("claim_sha256")
            == _dict(held.get("claim")).get("claim_sha256"),
        },
        "resume-after-abandon-refused": refused_without_replay(d),
        "no-replay": {
            "tool_server_ready": tool_server.get("ready") is True,
            "webhooks_total": isinstance(webhooks, list)
            and len(webhooks) == 1
            and evidence.get("webhook_errors") == [],
            "tool_never_called": tool_calls == 0,
        },
    }
    failed = sorted(
        f"{case}.{name}" for case, checks in cases.items() for name, ok in checks.items() if not ok
    )
    timed_out = sorted(p for p, r in runs.items() if _dict(r).get("timeout") is True)
    if not all(cleanup.values()):
        status = "FAIL"
    elif timed_out:
        status = "INCONCLUSIVE"
    else:
        status = "FAIL" if failed else "PASS"
    return {
        "status": status,
        "cases": cases,
        "failed_checks": failed,
        "timed_out_phases": timed_out,
    }


def retain_artifacts(layout: Layout, destination: Path) -> dict[str, str]:
    """Copy the journal, claim, lease, tombstone and ledger bytes; return their hashes."""
    destination.mkdir(mode=0o755)
    hashes: dict[str, str] = {}
    journal_dir = layout.ledger_dir / "pause-journal"
    sources = (
        [p for p in sorted(journal_dir.iterdir()) if p.is_file()] if journal_dir.is_dir() else []
    )
    ledger = layout.ledger_dir / "state.jsonl"
    for source in [*sources, *([ledger] if ledger.is_file() else [])]:
        target = destination / source.name
        target.write_bytes(source.read_bytes())
        hashes[source.name] = sha256(target)
    return hashes


def run(
    candidate: Path,
    venv: Path,
    expected_head: str,
    receipt: Path,
    scenario_root: Path,
    output: Path,
) -> dict[str, object]:
    deadline = time.monotonic() + OVERALL_CAP_SECONDS
    root, installed, python = checked_candidate(candidate, venv, expected_head)
    provenance = checked_provenance(receipt, root, installed, expected_head)
    placement = checked_scenario_root(scenario_root, Path("/proc/self/mountinfo").read_text())
    if not output.parent.is_dir() or os.path.lexists(output):
        raise ValueError("output parent must exist and output must be new")
    if output.resolve(strict=False).is_relative_to(scenario_root):
        raise ValueError("report must be outside the scenario root")
    logs = output.with_suffix(".logs")
    logs.mkdir(mode=0o755)
    layout = Layout(scenario_root)
    for directory in (
        layout.root,
        layout.repo,
        layout.home,
        layout.tmp,
        layout.results,
        layout.markers,
    ):
        directory.mkdir(mode=0o700)
    helper = Path(__file__).resolve(strict=True)
    fixed = [
        "--scenario",
        str(layout.root),
        "--candidate",
        str(root),
        "--venv",
        str(installed),
        "--provenance",
        str(receipt.resolve(strict=True)),
        "--expected-head",
        expected_head,
    ]
    env = child_env(layout)

    def launch(phase: str) -> Child:
        return spawn(child_argv(python, helper, phase, fixed), env, layout.tmp, logs, phase)

    report: dict[str, object] = {
        "plan": PLAN,
        "helper_sha256": sha256(helper),
        "parent_interpreter": {"executable": sys.executable, "isolated": sys.flags.isolated},
        "candidate": str(root),
        "expected_head": expected_head,
        "venv": str(installed),
        "installation_receipt_sha256": sha256(receipt),
        "wheel_sha256": {item["path"]: item["sha256"] for item in provenance["wheels"]},
        "scenario_root": placement,
        "status": "INCONCLUSIVE",
    }
    previous_term = signal.getsignal(signal.SIGTERM)

    def stop(_signum: int, _frame: object) -> None:
        raise InterruptedError("witness interrupted by SIGTERM")

    signal.signal(signal.SIGTERM, stop)
    try:
        evidence = with_services(
            layout,
            python,
            logs,
            deadline,
            lambda capture: scenario(layout, launch, capture, deadline),
        )
    finally:
        signal.signal(signal.SIGTERM, previous_term)
    report["config_sha256"] = sha256(layout.config)
    report["evidence"] = evidence
    report["artifacts"] = retain_artifacts(layout, output.with_suffix(".artifacts"))
    report.update(evaluate(evidence))
    write_new(output, json.dumps(report, sort_keys=True, indent=2, default=str) + "\n", 0o644)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", default="plan", choices=("plan", "run", "_child"))
    parser.add_argument("phase", nargs="?", choices=PHASES)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--venv", type=Path)
    parser.add_argument("--provenance", type=Path)
    parser.add_argument("--expected-head")
    parser.add_argument("--scenario", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "plan":
        print(json.dumps(PLAN, sort_keys=True, indent=2))
        return 0
    if None in (args.candidate, args.venv, args.provenance, args.expected_head, args.scenario):
        parser.error(
            "run/_child need --candidate, --venv, --provenance, --expected-head, --scenario"
        )
    if args.command == "_child":
        if args.phase is None:
            parser.error("_child needs a phase")
        prove = installed_prover(args.candidate, args.venv, args.expected_head, args.provenance)
        return run_phase(Layout(args.scenario), args.phase, prove)
    if args.output is None:
        parser.error("run needs --output")
    report = run(
        args.candidate,
        args.venv,
        args.expected_head,
        args.provenance,
        args.scenario,
        args.output,
    )
    print(json.dumps({"status": report["status"], "failed_checks": report["failed_checks"]}))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
