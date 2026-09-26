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
import hashlib
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
from collections.abc import Callable
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from types import ModuleType
from typing import Any

# --- the shared installed-provenance owner ------------------------------------------------------


def _load_shared_prover() -> ModuleType:
    """Load `installed_witness_provenance.py` from beside this file, by explicit path.

    [LAW:single-enforcer] The candidate/receipt/startup/wheel/origin proof lives in ONE module that
    every installed witness shares. It is loaded by file path and registered in `sys.modules`
    (so a normal import elsewhere gets the same object), never through a `sys.path` entry: the
    child runs `python -I`, where this script's directory is not importable, and its
    `interpreter_evidence` refuses any `sys.path` entry outside the venv and base interpreter.
    """
    import importlib.util

    name = "installed_witness_provenance"
    # The path derives from THIS immutable helper file and nothing else: no sys.path search, no
    # environment variable, no fallback location.
    path = Path(__file__).resolve(strict=True).with_name(f"{name}.py")
    existing = sys.modules.get(name)
    if existing is not None:
        if Path(getattr(existing, "__file__", "") or "").resolve() != path:
            raise ImportError(f"a different module is already registered as {name}: {existing}")
        return existing
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load the shared installed-witness provenance module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PROVER = _load_shared_prover()
SHARED_PROVER_PATH = Path(PROVER.__file__).resolve(strict=True)
# Re-exports DERIVED from the shared owner, kept so existing call sites and fixtures do not move;
# none of these is a second copy of an invariant.
PACKAGES = PROVER.PACKAGES
MIN_LOADED_HARNESS_MODULES = PROVER.MIN_LOADED_HARNESS_MODULES
WORKSPACE_DIST_VERSION = PROVER.WORKSPACE_DIST_VERSION
sha256 = PROVER.sha256
checked_wheel_source = PROVER.checked_wheel_source
checked_candidate = PROVER.checked_candidate
checked_startup_hooks = PROVER.checked_startup_hooks
checked_provenance = PROVER.checked_provenance
installed_origins = PROVER.installed_origins
interpreter_evidence = PROVER.interpreter_evidence
loaded_harness_origins = PROVER.loaded_harness_origins
installed_prover = PROVER.installed_prover
origin_reasons = PROVER.origin_reasons
provenance_reasons = PROVER.provenance_reasons
loaded_modules_meet_floor = PROVER.loaded_modules_meet_floor
_is_sha256 = PROVER.is_sha256
_exact_int = PROVER.exact_int
_dict = PROVER.dict_or_empty

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

    def provenance_record(self, phase: str) -> Path:
        """The child's pre-body provenance record, written before its phase body starts."""
        return self.results / f"{phase}.provenance.json"


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
        verified = {
            path
            for item in evidence.get("installed_origins", {}).values()
            for path in item["verified_files"]
        }
        # [LAW:no-ambient-temporal-coupling] Written BEFORE the body, for every phase: the held
        # `resume-a` never returns a result, so this record is its only installed-child proof.
        # `loaded_harness_modules` is the count actually loaded at THIS point, which may be
        # fewer than the post-body count in the result; it is never copied from later.
        loaded_before = loaded_harness_origins(verified) if verified else {}
        write_json_new(
            layout.provenance_record(phase),
            {
                "phase": phase,
                "stage": "pre-body",
                "pid": os.getpid(),
                "pgid": os.getpgid(0),
                "provenance": evidence,
                "loaded_harness_modules": len(loaded_before),
            },
        )
        observed = PHASE_BODIES[phase](layout)
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


def read_record(path: Path) -> dict[str, object] | None:
    """A child-written record: absent is `None`; unreadable or not an object is marked, never
    silently treated as absent, so the verdict rejects it instead of reading it as unstarted."""
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"unreadable": True}
    return value if isinstance(value, dict) else {"unreadable": True}


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
            # The marker's own pid/pgid, so the verdict can bind it to the launched A.
            "marker": read_record(layout.markers / "a-body.json") if entered else None,
        }
        results["resume-a"] = load_result(layout, "resume-a")
        write_json_new(layout.result("a-kill"), runs["resume-a"]["kill"])
        if observed and complete("resume-b") and complete("recover"):
            complete("resume-after-abandon")
        runs["webhooks_after_capture"] = webhooks_after_capture
    return {
        "runs": runs,
        "results": results,
        # A's pre-body provenance: the only installed-child proof of the held, killed A.
        "held_provenance": read_record(layout.provenance_record("resume-a")),
    }


# --- the verdict: typed per-phase outcomes, a sequence grammar, then behaviour -------------
#
# [LAW:parse-dont-validate] Each phase's raw run record, result and (for the held A) pre-body
# provenance record are parsed ONCE into a typed outcome. A completed phase is only ever
# `Completed` if its exit, output bound, phase, observed record and installed-child provenance
# all parse; a timed-out phase is only `TimedOut` if its cleanup is proven and it left no
# result. Everything else is `Broken` with named reasons, so no later timeout can excuse a
# missing or malformed proof and no failure becomes an empty valid state.


@dataclass(frozen=True)
class Completed:
    """A phase whose exit, output, result, observed record and provenance are all proved."""

    phase: str
    observed: dict[str, Any]


@dataclass(frozen=True)
class TimedOut:
    """A phase killed at its cap with its group proven gone and no result left behind."""

    phase: str


@dataclass(frozen=True)
class Unstarted:
    """A phase with neither a run record nor a result."""

    phase: str


@dataclass(frozen=True)
class Broken:
    """A phase whose record is missing, malformed or contradicts its own proof."""

    phase: str
    reasons: tuple[str, ...]


PhaseState = Completed | TimedOut | Unstarted | Broken


def kill_reasons(kill: object, *, sigkill: bool) -> tuple[str, ...]:
    """Why a kill record does not prove the owned group gone (and, if `sigkill`, killed)."""
    if not isinstance(kill, dict):
        return ("kill-missing",)
    data = _dict(kill)
    reasons: list[str] = []
    if data.get("group_gone") is not True:
        reasons.append("group-not-gone")
    if sigkill and (
        data.get("signal") != "SIGKILL" or _exact_int(data.get("returncode")) != -signal.SIGKILL
    ):
        reasons.append("not-killed-by-sigkill")
    return tuple(reasons)


def _result_reasons(phase: str, result: object, expected_receipt: str) -> tuple[str, ...]:
    if not isinstance(result, dict):
        return ("result-missing",)
    data = _dict(result)
    reasons: list[str] = []
    if data.get("phase") != phase:
        reasons.append("result-phase-mismatch")
    if data.get("ok") is not True:
        reasons.append("result-not-ok")
    if not isinstance(data.get("observed"), dict):
        reasons.append("observed-missing")
    reasons.extend(provenance_reasons(data.get("provenance"), expected_receipt))
    if not loaded_modules_meet_floor(data.get("loaded_harness_modules")):
        reasons.append("loaded-modules-invalid")
    return tuple(reasons)


def parse_waited_phase(
    phase: str, run: object, result: object, expected_receipt: str
) -> PhaseState:
    """A phase the parent waits on to exit by itself."""
    if run is None and result is None:
        return Unstarted(phase)
    if not isinstance(run, dict):
        return Broken(phase, ("run-missing" if run is None else "run-malformed",))
    record = _dict(run)
    timeout = record.get("timeout")
    if type(timeout) is not bool:
        return Broken(phase, ("timeout-malformed",))
    reasons: list[str] = []
    if record.get("output_ok") is not True:
        reasons.append("output-capped")
    if timeout:
        # A cap race may leave any return code; only the group-gone proof matters.
        reasons.extend(kill_reasons(record.get("kill"), sigkill=False))
        if result is not None:
            reasons.append("timed-out-left-result")
        return Broken(phase, tuple(reasons)) if reasons else TimedOut(phase)
    if _exact_int(record.get("exit")) != 0:
        reasons.append("exit-nonzero")
    if record.get("kill") is not None:
        reasons.append("unexpected-kill")
    reasons.extend(_result_reasons(phase, result, expected_receipt))
    if reasons:
        return Broken(phase, tuple(reasons))
    return Completed(phase, _dict(_dict(result).get("observed")))


def _held_reasons(held: object, run: dict[str, Any], expected_receipt: str) -> tuple[str, ...]:
    """Why A's pre-body provenance record is not proof of A's own installed interpreter."""
    if not isinstance(held, dict):
        return ("held-provenance-missing",)
    data = _dict(held)
    reasons = [f"held-{r}" for r in provenance_reasons(data.get("provenance"), expected_receipt)]
    if data.get("phase") != "resume-a" or data.get("stage") != "pre-body":
        reasons.append("held-record-misplaced")
    if not loaded_modules_meet_floor(data.get("loaded_harness_modules")):
        reasons.append("held-modules-invalid")
    for field in ("pid", "pgid"):
        mine, launched = _exact_int(data.get(field)), _exact_int(run.get(field))
        if mine is None or launched is None or mine != launched:
            reasons.append(f"held-{field}-mismatch")
    return tuple(reasons)


def _marker_reasons(run: dict[str, Any]) -> tuple[str, ...]:
    """Bind the in-body marker's pid and pgid to the launched A; a missing marker is no proof."""
    marker = run.get("marker")
    if marker is None:
        return ("marker-missing",)
    if not isinstance(marker, dict):
        return ("marker-malformed",)
    data = _dict(marker)
    reasons: list[str] = []
    for field in ("pid", "pgid"):
        seen, launched = _exact_int(data.get(field)), _exact_int(run.get(field))
        if seen is None or launched is None or seen != launched:
            reasons.append(f"marker-{field}-mismatch")
    return tuple(reasons)


def parse_held_phase(
    run: object, result: object, held: object, expected_receipt: str
) -> PhaseState:
    """`resume-a`: held in its body and killed by the parent, so it never leaves a result.

    Its provenance is the pre-body record the child wrote before entering the body; A is
    never provenance-exempt. A record that is present is judged even when A timed out.
    """
    phase = "resume-a"
    if run is None and result is None and held is None:
        return Unstarted(phase)
    if not isinstance(run, dict):
        return Broken(phase, ("run-missing" if run is None else "run-malformed",))
    record = _dict(run)
    entered, timeout = record.get("barrier_entered"), record.get("timeout")
    if type(entered) is not bool or type(timeout) is not bool:
        return Broken(phase, ("barrier-malformed",))
    reasons: list[str] = []
    if record.get("output_ok") is not True:
        reasons.append("output-capped")
    if result is not None:
        reasons.append("a-left-result")
    # A is deliberately killed by the parent, so a SIGKILL return code is required.
    reasons.extend(kill_reasons(record.get("kill"), sigkill=True))
    if held is not None:
        reasons.extend(_held_reasons(held, record, expected_receipt))
    if timeout:
        if entered:
            reasons.append("timed-out-after-barrier")
        return Broken(phase, tuple(reasons)) if reasons else TimedOut(phase)
    if not entered:
        reasons.append("exited-before-barrier")
    if held is None:
        reasons.append("held-provenance-missing")
    # A completed A entered its body, so its marker exists: absence is missing proof, never a
    # weaker variant. Only a genuine no-barrier timeout (above) may lack one.
    reasons.extend(_marker_reasons(record))
    return Broken(phase, tuple(reasons)) if reasons else Completed(phase, {})


def sequence_failures(states: list[PhaseState]) -> list[str]:
    """The grammar `Completed* (TimedOut Unstarted* | nothing)` over the phases in order."""
    failures: list[str] = []
    stopped = False
    for state in states:
        if isinstance(state, TimedOut):
            if stopped:
                failures.append(f"{state.phase}:second-timeout")
            stopped = True
        elif isinstance(state, Completed) and stopped:
            failures.append(f"{state.phase}:completed-after-stop")
        elif isinstance(state, Unstarted) and not stopped:
            failures.append(f"{state.phase}:unstarted-without-timeout")
    return failures


def global_failures(evidence: dict[str, Any]) -> list[str]:
    """Facts no timeout can excuse: the owned tool server, webhook errors, replay, tool calls."""
    tool_server = _dict(evidence.get("tool_server"))
    failures = [f"tool-server:{r}" for r in kill_reasons(tool_server.get("kill"), sigkill=False)]
    if tool_server.get("output_ok") is not True:
        failures.append("tool-server:output-capped")
    if tool_server.get("ready") is not True:
        failures.append("tool-server:not-ready")
    if evidence.get("webhook_errors") != []:
        failures.append("webhook-errors")
    if _exact_int(evidence.get("tool_calls")) != 0:
        failures.append("tool-called")
    webhooks = evidence.get("webhook_requests")
    if not isinstance(webhooks, list):
        failures.append("webhooks-malformed")
    elif len(webhooks) > 1:  # pyright: ignore[reportUnknownArgumentType]
        failures.append("webhook-replay")
    return failures


def _state_view(state: PhaseState) -> dict[str, object]:
    match state:
        case Completed():
            return {"state": "completed", "reasons": []}
        case TimedOut():
            return {"state": "timed-out", "reasons": []}
        case Unstarted():
            return {"state": "unstarted", "reasons": []}
        case Broken(reasons=reasons):
            return {"state": "broken", "reasons": list(reasons)}


def evaluate(evidence: dict[str, object], *, expected_receipt_sha256: str) -> dict[str, object]:
    """Fail-closed verdict over the recorded evidence.

    `expected_receipt_sha256` is the digest the PARENT computed from the installation receipt
    it verified; every proved child record must carry exactly it. FAIL if any phase is
    `Broken`, the phase sequence is invalid, a global fact fails, or a judged behaviour check
    fails. INCONCLUSIVE only if exactly one phase timed out, everything before it is proved
    and complete, cleanup is proved, nothing failed independently and no later phase ran.
    PASS needs all six phases proved, every behaviour true and exactly one webhook.
    """
    if not _is_sha256(expected_receipt_sha256):
        raise ValueError("expected receipt digest must be 64 lowercase hex characters")
    runs = _dict(evidence.get("runs"))
    results = _dict(evidence.get("results"))
    states: dict[str, PhaseState] = {}
    for phase in PHASES:
        if phase == "resume-a":
            states[phase] = parse_held_phase(
                runs.get(phase),
                results.get(phase),
                evidence.get("held_provenance"),
                expected_receipt_sha256,
            )
        else:
            states[phase] = parse_waited_phase(
                phase, runs.get(phase), results.get(phase), expected_receipt_sha256
            )
    ordered = [states[p] for p in PHASES]

    def observed(phase: str) -> dict[str, Any]:
        state = states[phase]
        return state.observed if isinstance(state, Completed) else {}

    capture, held = observed("capture"), observed("observe-held")
    b, recover, d = observed("resume-b"), observed("recover"), observed("resume-after-abandon")
    ref = capture.get("ref")
    webhooks = evidence.get("webhook_requests")
    raw_audits = recover.get("audits")
    audits = [_dict(a) for a in raw_audits] if isinstance(raw_audits, list) else []
    abandon_audits = [a for a in audits if a.get("action_id") == "b104w-abandon-1"]
    release = _dict(recover.get("release"))

    # Each behaviour check names the phases whose proved records it reads; it is judged only
    # when every one of them is `Completed`, and is otherwise recorded as unjudged. The grammar
    # guarantees such phases are only the timed-out phase and the unstarted ones after it.
    def refused_without_replay(
        outcome: dict[str, Any], phase: str
    ) -> dict[str, tuple[bool, tuple[str, ...]]]:
        return {
            "typed_refusal": (
                outcome.get("outcome") == "refused"
                and outcome.get("error_type")
                == "harness_runtime.lifecycle.root_resume_admission.ResumeClaimRefusedError"
                and outcome.get("reason") == "claim-refused",
                (phase,),
            ),
            "no_body": (outcome.get("body_marker_present") is False, (phase,)),
            "same_record": (outcome.get("ref") == ref, (phase, "capture")),
            "claim_still_started": (
                _dict(outcome.get("claim")).get("phase") == "started",
                (phase,),
            ),
        }

    checks: dict[str, dict[str, tuple[bool, tuple[str, ...]]]] = {
        "capture": {
            "paused": (capture.get("status") == "paused", ("capture",)),
            "root_record": (capture.get("depth") == 0 and ref is not None, ("capture",)),
            "snapshot_is_record": (
                capture.get("snapshot_hash") == _dict(ref).get("snapshot_hash"),
                ("capture",),
            ),
            "no_claim_yet": (
                _dict(capture.get("claim")).get("phase") == "absent",
                ("capture",),
            ),
            "one_webhook": (
                _exact_int(runs.get("webhooks_after_capture")) == 1,
                ("capture",),
            ),
        },
        "resume-a-started": {
            "started_before_kill": (
                _dict(held.get("claim")).get("phase") == "started",
                ("observe-held",),
            ),
            "lease_held_by_a": (
                _dict(held.get("claim")).get("lease") == "busy",
                ("observe-held",),
            ),
            "same_record": (held.get("ref") == ref, ("observe-held", "capture")),
        },
        "resume-b-refused": {
            **refused_without_replay(b, "resume-b"),
            "lease_released_by_kill": (
                _dict(b.get("claim")).get("lease") == "free",
                ("resume-b",),
            ),
            "claim_bytes_unchanged": (
                _dict(b.get("claim")).get("claim_sha256")
                == _dict(held.get("claim")).get("claim_sha256"),
                ("resume-b", "observe-held"),
            ),
        },
        "release-held": {
            "held": (
                release.get("outcome") == "held"
                and str(release.get("reason", "")).startswith("release-forbidden"),
                ("recover",),
            ),
            "no_mutation": (
                recover.get("inventory_before") is not None
                and recover.get("inventory_before") == recover.get("inventory_after_release"),
                ("recover",),
            ),
            "no_release_audit": (
                isinstance(raw_audits, list)
                and not any(a.get("action") == "release" for a in audits),
                ("recover",),
            ),
        },
        "abandon-audited": {
            "abandoned": (
                _dict(recover.get("abandon")).get("outcome") == "abandoned",
                ("recover",),
            ),
            "exact_record": (
                recover.get("claim_frame_names_record") is True and recover.get("ref") == ref,
                ("recover", "capture"),
            ),
            "intent_and_complete": (
                sorted(str(a.get("phase")) for a in abandon_audits) == ["complete", "intent"],
                ("recover",),
            ),
            "attested_by_kill_record": (
                all(
                    a.get("stopped_services_digest") == recover.get("kill_record_sha256")
                    for a in abandon_audits
                ),
                ("recover",),
            ),
            "tombstoned": (
                isinstance(recover.get("tombstones"), list) and len(recover["tombstones"]) == 1,
                ("recover",),
            ),
            "claim_bytes_kept": (
                _dict(recover.get("claim_after")).get("claim_sha256")
                == _dict(held.get("claim")).get("claim_sha256"),
                ("recover", "observe-held"),
            ),
        },
        "resume-after-abandon-refused": refused_without_replay(d, "resume-after-abandon"),
        "no-replay": {
            # Zero or one webhook is fine for an unfinished capture; PASS needs exactly one.
            "webhooks_total": (
                isinstance(webhooks, list) and len(webhooks) == 1,  # pyright: ignore[reportUnknownArgumentType]
                ("capture",),
            ),
        },
    }
    judged = {
        (case, name): all(isinstance(states[p], Completed) for p in reads)
        for case, items in checks.items()
        for name, (_ok, reads) in items.items()
    }
    failed = sorted(
        f"{case}.{name}"
        for case, items in checks.items()
        for name, (ok, _reads) in items.items()
        if judged[(case, name)] and not ok
    )
    unjudged = sorted(f"{case}.{name}" for (case, name), was in judged.items() if not was)
    phase_failures = sorted(
        f"{s.phase}:{r}" for s in ordered if isinstance(s, Broken) for r in s.reasons
    )
    grammar = sequence_failures(ordered)
    global_facts = global_failures(evidence)
    # [LAW:one-source-of-truth] One venv, one prover: every PROVED record must report the same
    # installed origins and interpreter prefix. Derived only from records that parsed as proof.
    proved = [
        _dict(_dict(results.get(p)).get("provenance"))
        for p in PHASES
        if p != "resume-a" and isinstance(states[p], Completed)
    ]
    if isinstance(states["resume-a"], Completed | TimedOut) and isinstance(
        evidence.get("held_provenance"), dict
    ):
        proved.append(_dict(_dict(evidence.get("held_provenance")).get("provenance")))
    for field, name in (("installed_origins", "origins"), ("interpreter", "interpreter")):
        seen = {
            json.dumps(
                p.get(field) if field == "installed_origins" else _dict(p.get(field)).get("prefix"),
                sort_keys=True,
            )
            for p in proved
        }
        if len(seen) > 1:
            global_facts.append(f"{name}-inconsistent")
    timed_out = [s.phase for s in ordered if isinstance(s, TimedOut)]
    if phase_failures or grammar or global_facts or failed:
        status = "FAIL"
    elif timed_out:
        status = "INCONCLUSIVE"
    else:
        status = "PASS"
    return {
        "status": status,
        "phase_states": {p: _state_view(states[p]) for p in PHASES},
        "global_failures": global_facts,
        "grammar_failures": grammar,
        "failed_checks": failed,
        "unjudged_checks": unjudged,
        "failure_reasons": sorted({*phase_failures, *grammar, *global_facts, *failed}),
        "cases": {
            case: {name: (ok if judged[(case, name)] else None) for name, (ok, _r) in items.items()}
            for case, items in checks.items()
        },
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
        "shared_prover_sha256": sha256(SHARED_PROVER_PATH),
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
    # [LAW:one-source-of-truth] The digest of the receipt THIS parent verified binds evaluate.
    report.update(evaluate(evidence, expected_receipt_sha256=sha256(receipt)))
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
    print(json.dumps({"status": report["status"], "failure_reasons": report["failure_reasons"]}))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
