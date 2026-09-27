"""Evaluation-only nested PRE_ACTION inheritance witness: source rehearsal G1, installed run later.

Scenario P drives a three-level durable pause through the PUBLIC API only: root R
(ORCHESTRATOR_WORKERS) -> child C (ORCHESTRATOR_WORKERS) -> grandchild G (linear), all
TEAM_BINDING x RECONCILER_LOOP (the durable-async cell), with real tools served by an owned loopback
MCP server (READ_ONLY, L3) and an owned loopback webhook. No `step_dispatchers` override and no
direct child resume are used: that would remove the behaviour this witness proves.

    R  PRE_ACTION(witness.a)          orchestrator TOOL_STEP witness.b ; worker -> C
    C  PRE_ACTION(witness.a),         orchestrator TOOL_STEP witness.b ; worker -> G
       PRE_ACTION(witness.c)
    G  PRE_ACTION(witness.z)          TOOL_STEP witness.b, a, c, d

`run` pauses at G's `witness.a` (inherited from R, duplicated by C); `resume-1` approves it through
the ROOT handle with a response keyed by G's actual `run_id`, runs `witness.a` once and pauses again
at `witness.c` (declared only by C); `resume-2` approves that and finishes with `witness.d`. The
verdict is per-phase typed outcomes (the reviewed B-104 states and sequence grammar) then behaviour.

Negatives, each on its own state root: N1 resumes after R's placement was lowered. The first
resume must end as a terminal FAILED carrying the child's refusal (no new root record, no
`witness.a`, `c` or `d`, no audit or webhook) and a second resume of the same record must be
claim-refused. N2 resumes a depth>0 handle directly (typed refusal, no claim); N3 is a
receipt/head/startup/wheel mismatch refused by the
SHARED prover before any child.

Provenance is the reviewed shared owner `installed_witness_provenance` (loaded by explicit path, as
in the B-104 witness, because `python -I` has no script directory on `sys.path`). Generic process
ownership helpers (spawn, bounded finish, group kill proof, output records) are the B-104 witness's,
imported not copied. Source rehearsal proves seams in-process; it is never installed acceptance.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import json
import os
import re
import signal
import sys
import threading
import time
import traceback
from collections import Counter
from collections.abc import Callable, Generator
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from types import FrameType, ModuleType
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # static types only: the product is never imported by the parent process
    from collections.abc import Sequence

    from b104_installed_public_witness import (
        Broken,
        Completed,
        PhaseState,
        TimedOut,
        Unstarted,
    )
    from harness_core import JournalRecordRef
    from harness_cp.pause_resume_protocol_types import PauseSnapshot
    from harness_cp.workflow_driver_types import WorkflowStep
    from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
    from harness_runtime.api import WorkflowObject
    from harness_runtime.types import RuntimeConfig

# --- sibling owners, loaded by explicit path (no sys.path entry; see module docstring) ----------


def _sibling_path(name: str) -> Path:
    return Path(__file__).resolve(strict=True).with_name(f"{name}.py")


def _load_sibling(name: str) -> ModuleType:
    path = _sibling_path(name)
    existing = sys.modules.get(name)
    if existing is not None:
        if Path(getattr(existing, "__file__", "") or "").resolve() != path:
            raise ImportError(f"a different module is already registered as {name}: {existing}")
        return existing
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load sibling module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PROVER = _load_sibling("installed_witness_provenance")
HELPERS = _load_sibling("b104_installed_public_witness")  # generic process-ownership helpers
if not TYPE_CHECKING:  # the typed views of the B-104 phase states are imported above
    Broken, Completed, TimedOut, Unstarted = (
        HELPERS.Broken,
        HELPERS.Completed,
        HELPERS.TimedOut,
        HELPERS.Unstarted,
    )
SHARED_PROVER_PATH = _sibling_path("installed_witness_provenance")
HELPERS_PATH = _sibling_path("b104_installed_public_witness")

# --- the scenario's fixed facts -----------------------------------------------------------------

ROOT_ID, MID_ID, LEAF_ID = "preaction-root", "preaction-mid", "preaction-leaf"
TOOLS = ("witness.a", "witness.b", "witness.c", "witness.d", "witness.z")
CHILD_CAP_SECONDS = 60
OVERALL_CAP_SECONDS = 600
MAX_BODY_BYTES = 4096
# The composer's audit identity is `hitl:{parent_action_id}:{position}` of the GATED step; the
# gated steps are G's steps 1 (witness.a) and 2 (witness.c). Asserted only inside the `hitl:` space.
KEY_A = f"hitl:workflow:{LEAF_ID}:step:1:pre-action"
KEY_C = f"hitl:workflow:{LEAF_ID}:step:2:pre-action"
# The public `RunResult.failure_cause` of a failed workflow: this runtime class, with the CP class
# in `validator_fail_class`. The leaf's resume guard names REFUSAL_REASON when the inherited gate
# configuration changed; it is checked in the structured field, never in the human `detail`.
WORKFLOW_FAILURE_CLASS = "RT-FAIL-WORKFLOW"
REFUSAL_REASON = "hitl-gate-config-changed"
# The root's topology family in CP v1.123 §0.3's terminal grammar
# `<family>-child-resume-refused (<reasons>[; audit-signing-failed])`: ORCHESTRATOR_WORKERS.
ROOT_FAMILY = "orchestrator-workers"
AUDIT_SIGNING_FAILED = "audit-signing-failed"

PHASES_P = ("run", "resume-1", "resume-2")
PHASES_N1 = ("run", "resume-lowered", "resume-lowered-again")
PHASES_N2 = ("run", "resume-child-handle")
SCENARIOS: dict[str, tuple[str, ...]] = {"p": PHASES_P, "n1": PHASES_N1, "n2": PHASES_N2}

PLAN = {
    "scope": "nested PRE_ACTION inheritance through the public api.run / api.resume",
    "scenarios": {name: list(phases) for name, phases in SCENARIOS.items()},
    "n3": "shared-prover refusal of a mismatched receipt/head/startup/wheel before any child",
    "provider_free": "owned loopback MCP tool server and webhook; no model, no step_dispatchers",
    "child_cap_seconds": CHILD_CAP_SECONDS,
    "overall_cap_seconds": OVERALL_CAP_SECONDS,
    "attempts": 1,
    "state_root": "one new non-tmpfs directory per scenario, outside every Git checkout",
    "outcome": "PASS needs every case; a single timed-out phase is INCONCLUSIVE; else FAIL",
    "s5": "process/filesystem behaviour only; says nothing about VM reset durability",
}


@dataclass(frozen=True)
class Layout:
    """Every path one scenario uses, derived from its own root (one state root per scenario)."""

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
        return self.root / "preaction_witness_mcp_server.py"

    @property
    def tool_calls(self) -> Path:
        return self.root / "tool-calls.jsonl"

    @property
    def results(self) -> Path:
        return self.root / "results"

    def result(self, phase: str) -> Path:
        return self.results / f"{phase}.json"

    def provenance_record(self, phase: str) -> Path:
        return self.results / f"{phase}.provenance.json"


MCP_SERVER_SOURCE = '''"""Preaction witness loopback MCP server: five recording tools."""
import json
import os
import sys
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("preaction-installed-witness", host="127.0.0.1", port=int(sys.argv[2]))


def _record(tool: str, value: str) -> str:
    with open(sys.argv[1], "a", encoding="utf-8") as calls:
        calls.write(json.dumps({"tool": tool, "value": value, "pid": os.getpid()}) + "\\n")
    return value


@mcp.tool(name="witness.a")
def witness_a(value: str) -> str:
    """Gated by the inherited placement."""
    return _record("witness.a", value)


@mcp.tool(name="witness.b")
def witness_b(value: str) -> str:
    """Never gated: no placement names it."""
    return _record("witness.b", value)


@mcp.tool(name="witness.c")
def witness_c(value: str) -> str:
    """Gated only by the child's own placement."""
    return _record("witness.c", value)


@mcp.tool(name="witness.d")
def witness_d(value: str) -> str:
    """Never gated: no placement names it."""
    return _record("witness.d", value)


@mcp.tool(name="witness.z")
def witness_z(value: str) -> str:
    """Named only by the grandchild's narrower placement; the workflow never calls it."""
    return _record("witness.z", value)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
'''


def config_text(layout: Layout, webhook_port: int, mcp_port: int) -> str:
    """The reviewed B-104 operator TOML (placed state, webhook, loopback L3 READ_ONLY MCP)."""
    return HELPERS.config_text(layout, webhook_port, mcp_port)


# --- the public WorkflowObject -----------------------------------------------------------------


def build_workflow(*, root_has_placement: bool = True) -> WorkflowObject:
    """R -> C -> G as ordinary manifests and steps; `root_has_placement=False` is negative N1."""
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
    from harness_cp.sub_agent_brief import (
        ClearTaskBoundaries,
        OutputSchema,
        OutputSchemaKind,
        SubAgentBrief,
    )
    from harness_cp.topology_pattern import TopologyPattern
    from harness_cp.workflow_driver_types import StepKind, WorkflowStep
    from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
    from harness_runtime.lifecycle.sub_agent_dispatch import SubAgentDispatchPayload

    chain = FallbackChain(
        primary=ProviderCandidate(
            provider="ollama", model="llama3.2:3b", family=ProviderFamily.LOCAL_OPEN_WEIGHT
        ),
        same_family=(),
        cross_family=(),
        terminal=None,
    )

    def pre(*tools: str) -> HITLPlacement:
        return HITLPlacement(position=HITLPlacementKind.PRE_ACTION, tool_filter=tools)

    def manifest(
        workflow_id: str,
        topology: TopologyPattern,
        placements: tuple[HITLPlacement, ...],
        workload: WorkloadClass = WorkloadClass.SOFTWARE_ENGINEERING,
    ) -> WorkflowManifestEntry:
        return WorkflowManifestEntry(
            workflow_id=workflow_id,
            workload_class=workload,
            persona_tier=PersonaTier.TEAM_BINDING,
            engine_class=EngineClass.RECONCILER_LOOP,
            topology_pattern=topology,
            layer_budgets=(),
            fallback_chain=chain,
            hitl_placements=placements,
            per_step_overrides={},
        )

    def tool(step_id: str, name: str) -> WorkflowStep:
        return WorkflowStep(
            step_id=StepID(step_id),
            step_kind=StepKind.TOOL_STEP,
            step_payload={"tool_id": name, "tool_args": {"value": step_id}},
        )

    brief = SubAgentBrief(
        objective="descend one level and run its own steps",
        output_format=OutputSchema(schema_kind=OutputSchemaKind.FREE_TEXT),
        guidance="provider-free witness",
        task_boundaries=ClearTaskBoundaries(
            in_scope=("the declared steps",),
            out_of_scope=("everything else",),
            termination_criteria=("all declared steps complete",),
        ),
        summary_hash="0" * 64,
    )

    def dispatch(step_id: str, child: WorkflowManifestEntry, steps: tuple[WorkflowStep, ...]):
        payload = SubAgentDispatchPayload(
            child_workflow_id=child.workflow_id,
            child_manifest_entry=child,
            child_steps=steps,
            brief=brief,
        )
        return WorkflowStep(
            step_id=StepID(step_id),
            step_kind=StepKind.SUB_AGENT_DISPATCH,
            step_payload=payload.model_dump(),
        )

    # The linear leaf needs a workload class whose admissible topologies include it (a child's
    # topology/workload pair is checked at sub-agent dispatch); the fan-out levels keep the
    # software-engineering class the B-104 witness already proved bootstraps.
    leaf = manifest(
        LEAF_ID,
        TopologyPattern.SINGLE_THREADED_LINEAR,
        (pre("witness.z"),),
        WorkloadClass.PIPELINE_AUTOMATION,
    )
    leaf_steps = (
        tool("g-b", "witness.b"),
        tool("g-a", "witness.a"),
        tool("g-c", "witness.c"),
        tool("g-d", "witness.d"),
    )
    mid = manifest(
        MID_ID,
        TopologyPattern.ORCHESTRATOR_WORKERS,
        (pre("witness.a"), pre("witness.c")),
    )
    mid_steps = (tool("c-orchestrator", "witness.b"), dispatch("c-worker", leaf, leaf_steps))
    root_placements = (pre("witness.a"),) if root_has_placement else ()
    root = manifest(ROOT_ID, TopologyPattern.ORCHESTRATOR_WORKERS, root_placements)
    root_steps = (tool("r-orchestrator", "witness.b"), dispatch("r-worker", mid, mid_steps))

    class Workflow:
        workflow_id = ROOT_ID
        workload_class = WorkloadClass.SOFTWARE_ENGINEERING
        default_model_binding = ModelBinding(provider="ollama", model="llama3.2:3b")
        manifest_entry = root
        steps = root_steps

    return Workflow()


# --- owned loopback webhook ---------------------------------------------------------------------


class WebhookCapture:
    """One owned 127.0.0.1 listener recording every delivery with its headers."""

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
                        {
                            "path": self.path,
                            "idempotency_key": self.headers.get("Idempotency-Key"),
                            "headers": sorted(k.lower() for k in self.headers.keys()),
                            "body_sha256": hashlib.sha256(body).hexdigest(),
                            "body_bytes": len(body),
                        }
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

            def log_message(self, format: str, *args: object) -> None:
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
            raise RuntimeError("owned loopback webhook listener did not stop")


def tool_counts(layout: Layout) -> dict[str, int]:
    """Calls recorded so far per witness tool, read from the tool server's own log."""
    if not layout.tool_calls.exists():
        return {}
    lines = [ln for ln in layout.tool_calls.read_text().splitlines() if ln.strip()]
    return dict(Counter(json.loads(ln)["tool"] for ln in lines))


# --- child phases (harness imports stay inside each function) -------------------------------------


def _config(layout: Layout) -> RuntimeConfig:
    from harness_runtime.config_source import RuntimeConfigSource

    return RuntimeConfigSource.load(config_file=layout.config)


@dataclass(frozen=True)
class LatestRecord:
    """The journal's latest record for one workflow: exact ref, recorded depth, full snapshot."""

    ref: JournalRecordRef
    depth: int | None
    snapshot: PauseSnapshot


def _latest_root(layout: Layout, config: RuntimeConfig, workflow_id: str = ROOT_ID) -> LatestRecord:
    """The journal's latest record for `workflow_id`, as a typed record (absent is an error)."""
    from harness_core import JournalRecordRef
    from harness_runtime.lifecycle.journal_workflow_pause_store import (
        JournalWorkflowPauseStore,
        pause_journal_dir_for,
    )
    from harness_runtime.lifecycle.protected_result_store import normalize_tenant_scope

    journal_dir = pause_journal_dir_for(layout.ledger_dir)
    read = JournalWorkflowPauseStore(
        journal_dir=journal_dir, tenant_id=config.tenant_id
    ).read_latest_attributed(workflow_id)
    if read.snapshot is None or read.latest_record_digest is None:
        raise ValueError(f"no durable record for {workflow_id}: cause={read.cause}")
    ref = JournalRecordRef(
        tenant=normalize_tenant_scope(config.tenant_id),
        workflow_id=read.snapshot.workflow_id,
        run_id=read.snapshot.run_id,
        record_count=read.record_count,
        latest_digest=read.latest_record_digest,
        snapshot_hash=read.snapshot.snapshot_hash,
    )
    return LatestRecord(ref=ref, depth=read.depth, snapshot=read.snapshot)


def _paused_children(snapshot: PauseSnapshot) -> list[PauseSnapshot]:
    """The child snapshots the level carries as paused fan-out branches."""
    return [
        branch.child_snapshot
        for holder in (snapshot.fan_out_resume, snapshot.peer_fan_out_resume)
        if holder is not None
        for branch in holder.paused_child_branches
    ]


def nested_chain(snapshot: PauseSnapshot) -> list[dict[str, object]]:
    """Walk the carried paused children: [{workflow_id, run_id}] from the given snapshot down."""
    chain: list[dict[str, object]] = [
        {"workflow_id": snapshot.workflow_id, "run_id": snapshot.run_id}
    ]
    current = snapshot
    while True:
        children = _paused_children(current)
        if len(children) != 1:
            return chain
        current = children[0]
        chain.append({"workflow_id": current.workflow_id, "run_id": current.run_id})


def _branch_rows(snapshot: PauseSnapshot) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for holder in (snapshot.fan_out_resume, snapshot.peer_fan_out_resume):
        if holder is not None:
            rows.extend(
                {
                    "branch_index": row.branch_index,
                    "step_id": row.step_id,
                    "terminal_status": row.terminal_status,
                    "output": json.loads(json.dumps(row.output, default=str)),
                }
                for row in holder.branches
            )
    return rows


def level_view(snapshot: PauseSnapshot) -> list[dict[str, object]]:
    """Each carried level's pause_reason and its terminal fan-out branch rows, root first."""
    levels: list[dict[str, object]] = []
    current = snapshot
    while True:
        levels.append(
            {
                "workflow_id": current.workflow_id,
                "pause_reason": current.pause_reason.value,
                "branches": _branch_rows(current),
            }
        )
        children = _paused_children(current)
        if len(children) != 1:
            return levels
        current = children[0]


def declared_placements(workflow: WorkflowObject) -> dict[str, list[list[str]]]:
    """Each level's own declared PRE_ACTION tool filters, read from the workflow itself."""
    from harness_cp.workflow_driver_types import StepKind
    from harness_runtime.lifecycle.sub_agent_dispatch import SubAgentDispatchPayload

    found: dict[str, list[list[str]]] = {}

    def walk(entry: WorkflowManifestEntry, steps: Sequence[WorkflowStep]) -> None:
        found[str(entry.workflow_id)] = [list(p.tool_filter or ()) for p in entry.hitl_placements]
        for step in steps:
            if step.step_kind == StepKind.SUB_AGENT_DISPATCH:
                payload = SubAgentDispatchPayload.model_validate(step.step_payload)
                walk(payload.child_manifest_entry, payload.child_steps)

    walk(workflow.manifest_entry, workflow.steps)
    return found


def _claim_view(layout: Layout, config: RuntimeConfig, ref: JournalRecordRef) -> dict[str, object]:
    from harness_runtime.config.state_placement import place_state_dir, probe_declared_state_root
    from harness_runtime.lifecycle.journal_workflow_pause_store import pause_journal_dir_for
    from harness_runtime.lifecycle.resume_claim_store import (
        InvalidClaim,
        ResumeClaimStore,
        StartedOrUnknown,
        UnstartedProof,
        parse_claim,
    )

    placement = place_state_dir(
        pause_journal_dir_for(layout.ledger_dir),
        config,
        probe_declared_state_root(config),
        what="witness pause journal",
    )
    paths = ResumeClaimStore(placement=placement, tenant_id=config.tenant_id).paths_for(ref)
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
    return {
        "phase": phase,
        "claim_sha256": None if raw is None else hashlib.sha256(raw).hexdigest(),
    }


def _od_hitl_entries(path: Path) -> list[dict[str, object]]:
    """The OD audit entries in the `hitl:` namespace: key, gate level and operator response."""
    if not path.exists():
        return []
    found: list[dict[str, object]] = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)["entry"]["payload"]
        if str(payload["entry_core"]).startswith("hitl:"):
            attrs = payload["audit_namespace_attrs"]
            found.append(
                {
                    "key": payload["entry_core"],
                    "gate_level": attrs.get("audit.cp.gate_level"),
                    "response": attrs.get("audit.cp.response"),
                }
            )
    return found


def hitl_audit_view(layout: Layout) -> dict[str, object]:
    """Every state-ledger entry whose idempotency key is in the `hitl:` namespace, by key."""
    from harness_is.jsonl_event_ledger_lifecycle import JsonlLedgerHandle
    from harness_is.state_ledger_write import read_ledger

    od_entries = _od_hitl_entries(layout.ledger_dir / "audit-entries.jsonl")
    path = layout.ledger_dir / "state.jsonl"
    if not path.exists():
        return {"entries": [], "entry_count": 0, "od_entries": od_entries}
    handle = JsonlLedgerHandle(
        canonical_path=path,
        exists=True,
        entry_count=sum(1 for line in path.read_text().splitlines() if line.strip()),
    )
    entries = read_ledger(handle)
    return {
        "entry_count": len(entries),
        "od_entries": od_entries,
        "all_entries": [
            {"key": str(entry.idempotency_key), "action_id": str(entry.action_id)}
            for entry in entries[:200]
        ],
        "entries": [
            {"key": str(entry.idempotency_key), "action_id": str(entry.action_id)}
            for entry in entries
            if str(entry.idempotency_key).startswith("hitl:")
        ],
    }


def _observe_common(layout: Layout, config: RuntimeConfig) -> dict[str, object]:
    latest = _latest_root(layout, config)
    return {
        "ref": latest.ref.model_dump(mode="json"),
        "depth": latest.depth,
        "chain": nested_chain(latest.snapshot),
        "levels": level_view(latest.snapshot),
        "audits": hitl_audit_view(layout),
    }


def phase_run(layout: Layout, *, root_has_placement: bool = True) -> dict[str, object]:
    import asyncio

    from harness_runtime import api

    config = _config(layout)
    workflow = build_workflow(root_has_placement=root_has_placement)
    result = asyncio.run(api.run(workflow, config=config))
    observed = _observe_common(layout, config)
    observed["status"] = result.status
    observed["declared_placements"] = declared_placements(workflow)
    return observed


def _approval(leaf_run_id: str) -> Any:
    from harness_core.identity import EntryID
    from harness_cp.hitl_placement import HITLResult
    from harness_cp.hitl_response_palette import HITLResponse
    from harness_cp.pause_resume_protocol_types import ResumeContext

    return ResumeContext(
        hitl_responses={
            leaf_run_id: HITLResult(
                response=HITLResponse.APPROVE,
                timestamp="2026-01-01T00:00:00Z",
                audit_ledger_entry_id=EntryID("witness-operator-approval"),
                response_summary_hash="0" * 64,
            )
        }
    )


def phase_resume(layout: Layout, *, root_has_placement: bool = True) -> dict[str, object]:
    """Public `api.resume` through the ROOT handle, answering the actual leaf run_id."""
    import asyncio

    from harness_runtime import api

    config = _config(layout)
    before = _latest_root(layout, config)
    leaf_run_id = str(nested_chain(before.snapshot)[-1]["run_id"])
    outcome: dict[str, object] = {
        "addressed_run_id": leaf_run_id,
        "before_ref": before.ref.model_dump(mode="json"),
    }
    workflow = build_workflow(root_has_placement=root_has_placement)
    outcome["declared_placements"] = declared_placements(workflow)
    try:
        result = asyncio.run(
            api.resume(
                workflow,
                resume_handle=ROOT_ID,
                resume_context=_approval(leaf_run_id),
                config=config,
            )
        )
    except Exception as exc:  # a typed refusal is an outcome to record, not a crash
        reason = getattr(getattr(exc, "reason", None), "value", None)
        outcome |= {
            "outcome": "raised",
            "error_type": f"{type(exc).__module__}.{type(exc).__qualname__}",
            "reason": reason,
            "message": str(exc)[:400],
        }
    else:
        cause = result.failure_cause
        snapshot = result.pause_snapshot
        outcome |= {
            "outcome": "returned",
            "status": result.status,
            "failure_cause": None if cause is None else cause.model_dump(mode="json"),
            "has_pause_snapshot": snapshot is not None,
            "returned_pause_reason": None
            if snapshot is None
            else getattr(snapshot.pause_reason, "value", str(snapshot.pause_reason)),
        }
    after = _observe_common(layout, config)
    outcome |= after
    outcome["before_claim"] = _claim_view(layout, config, before.ref)
    return outcome


def phase_resume_child_handle(layout: Layout) -> dict[str, object]:
    """N2: a direct handle to the depth>0 leaf record must be refused before any effect."""
    import asyncio

    from harness_runtime import api

    config = _config(layout)
    root = _latest_root(layout, config)
    leaf = _latest_root(layout, config, LEAF_ID)
    outcome: dict[str, object] = {
        "leaf_depth": leaf.depth,
        "leaf_ref": leaf.ref.model_dump(mode="json"),
        "root_before_ref": root.ref.model_dump(mode="json"),
        "root_before_claim": _claim_view(layout, config, root.ref),
    }
    try:
        asyncio.run(api.resume(build_workflow(), resume_handle=LEAF_ID, config=config))
    except Exception as exc:
        outcome |= {
            "outcome": "raised",
            "error_type": f"{type(exc).__module__}.{type(exc).__qualname__}",
            "message": str(exc)[:400],
        }
    else:
        outcome["outcome"] = "returned"
    outcome["leaf_claim"] = _claim_view(layout, config, leaf.ref)
    root_after = _latest_root(layout, config)
    outcome["root_ref"] = root_after.ref.model_dump(mode="json")
    outcome["root_claim"] = _claim_view(layout, config, root.ref)
    outcome["audits"] = hitl_audit_view(layout)
    return outcome


PHASE_BODIES: dict[str, Callable[[Layout], dict[str, object]]] = {
    "run": phase_run,
    "resume-1": phase_resume,
    "resume-2": phase_resume,
    "resume-lowered": lambda layout: phase_resume(layout, root_has_placement=False),
    "resume-lowered-again": lambda layout: phase_resume(layout, root_has_placement=False),
    "resume-child-handle": phase_resume_child_handle,
}


def verified_paths(evidence: dict[str, object]) -> set[str]:
    """Every installed file the prover verified, read only from a record its own parser accepts.

    [LAW:parse-dont-validate] [LAW:single-enforcer] The shared prover owns the shape of its
    evidence (`provenance_reasons`: interpreter flags and prefix, receipt digest, every package
    origin). A record it rejects raises here and is never read as "no files", which would let the
    loaded-module proof pass vacuously.
    """
    receipt = evidence.get("installation_receipt_sha256")
    problems = PROVER.provenance_reasons(evidence, receipt if isinstance(receipt, str) else "")
    if problems:
        raise ValueError(f"prover evidence is not parseable provenance: {problems}")
    return {
        path
        for entry in _d(evidence["installed_origins"]).values()
        for path in _d(entry)["verified_files"]
    }


def run_phase(layout: Layout, phase: str, prove: Callable[[], dict[str, object]] | None) -> int:
    """Prove this interpreter (installed mode), run one phase body, re-prove modules, record once.

    `prove is None` is the source rehearsal: no installed interpreter exists to prove, so no
    provenance is recorded and the record cannot satisfy the installed verdict.
    """
    try:
        evidence = None if prove is None else prove()
        verified: set[str] = set()
        if evidence is not None:
            verified = verified_paths(evidence)
            loaded_before = PROVER.loaded_harness_origins(verified)
            HELPERS.write_json_new(
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
        record: dict[str, object] = {"phase": phase, "ok": True, "observed": observed}
        if evidence is not None:
            record["provenance"] = evidence
            record["loaded_harness_modules"] = len(PROVER.loaded_harness_origins(verified))
        HELPERS.write_json_new(layout.result(phase), record)
        return 0
    except BaseException as exc:  # recorded, then re-raised: a crash is evidence, not a pass
        HELPERS.write_json_new(
            layout.result(phase),
            {"phase": phase, "ok": False, "error": repr(exc), "traceback": traceback.format_exc()},
        )
        raise


# --- the parent: owned services, one child per phase, bounded ------------------------------------


def prepare_layout(layout: Layout) -> None:
    for directory in (layout.root, layout.repo, layout.home, layout.tmp, layout.results):
        directory.mkdir(mode=0o700, parents=True)


Launcher = Callable[[str], Any]


@contextlib.contextmanager
def term_as_interrupt() -> Generator[None]:
    """Turn an outside SIGTERM into an exception so the owners' `finally` cleanup runs.

    Same mechanism as the B-104 witness's `run`; without it the default action ends this process
    at once and every child, started in its own session, is orphaned. The previous handler is
    restored on exit.
    """
    previous = signal.getsignal(signal.SIGTERM)

    def stop(_signum: int, _frame: FrameType | None) -> None:
        raise InterruptedError("witness interrupted by SIGTERM")

    signal.signal(signal.SIGTERM, stop)
    try:
        yield
    finally:
        signal.signal(signal.SIGTERM, previous)


def _no_scenario_evidence() -> dict[str, object]:
    return {"runs": {}, "results": {}, "services": {}}


@contextlib.contextmanager
def term_deferred() -> Generator[None]:
    """Hold SIGTERM delivery for one short region; a pending TERM is delivered on exit.

    [LAW:no-ambient-temporal-coupling] A TERM must not land between a child being created and its
    handle being owned, nor half-way through cleanup: both regions are bounded and use this.
    """
    blocked = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGTERM})
    try:
        yield
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, blocked)


@dataclass
class Fleet:
    """Every phase child this attempt started, so cleanup reaches the one in flight.

    The handle is owned in the same deferred-TERM region that creates it. Only groups this helper
    started (`start_new_session`) are ever signalled, and only while their process still runs.
    """

    children: list[Any]

    def launch(self, launch: Launcher, phase: str) -> Any:
        with term_deferred():
            child = launch(phase)
            self.children.append(child)
        return child

    def kill_running(self) -> list[dict[str, object]]:
        return [HELPERS.kill_group(child) for child in self.children if child.proc.poll() is None]


def with_services(
    layout: Layout,
    python: Path,
    logs: Path,
    deadline: float,
    fleet: Fleet,
    body: Callable[[WebhookCapture], dict[str, object]],
) -> dict[str, object]:
    """Own the webhook listener and the tool server for exactly one scenario's life."""
    capture = WebhookCapture()
    tool_port = HELPERS.free_loopback_port()
    HELPERS.write_new(layout.mcp_server, MCP_SERVER_SOURCE)
    HELPERS.write_new(layout.config, config_text(layout, capture.port, tool_port))
    capture.start()
    with term_deferred():
        server = HELPERS.spawn(
            [str(python), "-I", str(layout.mcp_server), str(layout.tool_calls), str(tool_port)],
            {"PATH": "/usr/bin:/bin", "HOME": str(layout.home), "TMPDIR": str(layout.tmp)},
            layout.tmp,
            logs,
            "tool-server",
        )
    ready = False
    try:
        ready = HELPERS.wait_listening(server, tool_port, deadline)
        evidence = body(capture) if ready else _no_scenario_evidence()
    finally:
        with term_deferred():
            phase_cleanup = fleet.kill_running()
            tool_server = {
                **HELPERS.stream_record(server),
                "ready": ready,
                "kill": HELPERS.kill_group(server),
            }
            capture.close()
    evidence["phase_cleanup"] = phase_cleanup
    evidence["tool_server"] = tool_server
    evidence["webhook_requests"] = capture.requests
    evidence["webhook_errors"] = capture.errors
    return evidence


def settle_group(pgid: int) -> bool:
    """True if any process of the child's OWN group outlived it; those survivors are then killed.

    The parent only ever signals the group it started (`start_new_session`), never a pid it found.
    """
    survivors = False
    for _ in range(20):
        try:
            os.killpg(pgid, 0)
        except ProcessLookupError:
            return survivors
        survivors = True
        try:
            os.killpg(pgid, signal.SIGKILL)
        except ProcessLookupError:
            return survivors
        time.sleep(0.05)
    return survivors


@dataclass(frozen=True)
class PhaseRun:
    """The three facts the parent loop acts on, parsed from a waited child's run record."""

    pgid: int
    timed_out: bool
    exit_code: int


def parse_phase_run(record: dict[str, object]) -> PhaseRun:
    """A waited child's record as typed facts; a malformed record raises, it does not continue.

    [LAW:parse-dont-validate] `settle_group` signals a process group, so its id must be a real
    int (a bool or a string is refused) before it reaches `killpg`.
    """
    pgid, code = PROVER.exact_int(record.get("pgid")), PROVER.exact_int(record.get("exit"))
    timed_out = record.get("timeout")
    if pgid is None or code is None or not isinstance(timed_out, bool):
        raise ValueError(f"malformed phase run record: {sorted(record)}")
    return PhaseRun(pgid=pgid, timed_out=timed_out, exit_code=code)


def run_scenario(
    name: str,
    layout: Layout,
    launch: Launcher,
    fleet: Fleet,
    capture: WebhookCapture,
    deadline: float,
) -> dict[str, object]:
    """Run one scenario's phases in order, stopping at the first that cannot continue.

    After every phase the parent snapshots what the owned services saw so far, so per-phase effects
    (webhooks, tool calls) are attributable without trusting the child.
    """
    runs: dict[str, object] = {}
    results: dict[str, object] = {}
    services: dict[str, object] = {}
    for phase in SCENARIOS[name]:
        finished = HELPERS.finish(fleet.launch(launch, phase), deadline)
        run = parse_phase_run(finished)
        runs[phase] = {**finished, "group_survivors": settle_group(run.pgid)}
        results[phase] = HELPERS.load_result(layout, phase)
        services[phase] = {
            "webhook_keys": [str(r["idempotency_key"]) for r in capture.requests],
            "tool_counts": tool_counts(layout),
        }
        if run.timed_out or run.exit_code != 0:
            break
    return {"runs": runs, "results": results, "services": services}


def child_argv_source(
    python: Path, helper: Path, name: str, phase: str, fixed: list[str]
) -> list[str]:
    """Source rehearsal only: no `-I` (the product is on PYTHONPATH), no provenance."""
    return [str(python), str(helper), "_child", name, phase, "--source-rehearsal", *fixed]


def child_argv_installed(
    python: Path, helper: Path, name: str, phase: str, fixed: list[str]
) -> list[str]:
    return [str(python), "-I", str(helper), "_child", name, phase, *fixed]


# --- the verdict: typed phase states (reviewed B-104 grammar), then behaviour --------------------
#
# [LAW:parse-dont-validate] Installed evidence is judged through the SAME typed per-phase parsers
# and sequence grammar as the B-104 witness (`Completed`/`TimedOut`/`Unstarted`/`Broken`), which
# call the shared provenance owner; a phase is only `Completed` if exit, output bound, result and
# installed-child provenance all parse. Behaviour is judged only over Completed phases. The
# source rehearsal has no installed interpreter, so it cannot produce provenance: its phases are
# judged by `rehearsal_state` and its verdict is labelled REHEARSAL, never PASS.


def _d(value: object) -> dict[str, Any]:
    return PROVER.dict_or_empty(value)


_TOKEN = r"[a-z]+(?:-[a-z]+)*"
_TERMINAL_REFUSAL = re.compile(
    rf"(?P<family>{_TOKEN})-child-resume-refused \((?P<body>{_TOKEN}(?:; {_TOKEN})*)\)"
)


@dataclass(frozen=True)
class TerminalRefusal:
    """A parsed CP v1.123 §0.3 terminal fail class: the proof is the type, not a substring."""

    family: str
    reasons: frozenset[str]
    audit_signing_failed: bool


def parse_terminal_refusal(fail_class: object) -> TerminalRefusal | None:
    """The whole string must be the grammar: sorted distinct reasons, then optionally the literal
    `audit-signing-failed` last. Anything else (a raw child class, text around it, a lookalike) is
    `None`, never a partial match.

    [LAW:parse-dont-validate] One parser; the verdict consumes its typed result.
    """
    if not isinstance(fail_class, str):
        return None
    match = _TERMINAL_REFUSAL.fullmatch(fail_class)
    if match is None:
        return None
    parts = match["body"].split("; ")
    signing = parts[-1] == AUDIT_SIGNING_FAILED
    reasons = parts[:-1] if signing else parts
    if not reasons or reasons != sorted(set(reasons)) or AUDIT_SIGNING_FAILED in reasons:
        return None
    return TerminalRefusal(match["family"], frozenset(reasons), signing)


def rehearsal_state(phase: str, run: object, result: object) -> PhaseState:
    """A rehearsal phase: clean exit, bounded output, an ok result with an observed record."""
    if run is None and result is None:
        return Unstarted(phase)
    record, res = _d(run), _d(result)
    reasons: list[str] = []
    if record.get("timeout") is not False:
        reasons.append("timeout-or-malformed")
    if PROVER.exact_int(record.get("exit")) != 0:
        reasons.append("exit-nonzero")
    if record.get("output_ok") is not True:
        reasons.append("output-capped")
    if res.get("ok") is not True or not isinstance(res.get("observed"), dict):
        reasons.append("result-not-ok")
    if reasons:
        return Broken(phase, tuple(reasons))
    return Completed(phase, _d(res["observed"]))


def scenario_states(
    name: str, ev: dict[str, Any], expected_receipt: str | None
) -> list[PhaseState]:
    states: list[PhaseState] = []
    for phase in SCENARIOS[name]:
        run, result = _d(ev.get("runs")).get(phase), _d(ev.get("results")).get(phase)
        if expected_receipt is None:
            states.append(rehearsal_state(phase, run, result))
        else:
            states.append(HELPERS.parse_waited_phase(phase, run, result, expected_receipt))
    return states


def _tool_count_reasons(counts: dict[str, Any], want: dict[str, int], label: str) -> list[str]:
    reasons: list[str] = []
    seen = {k: PROVER.exact_int(v) for k, v in counts.items()}
    for tool in TOOLS:
        have, need = seen.get(tool, 0) or 0, want.get(tool, 0)
        if have == need:
            continue
        if tool == "witness.b" and have > need:
            reasons.append(f"{label}:replay:{tool}")
        elif have > need and tool in ("witness.a", "witness.c", "witness.d"):
            reasons.append(f"{label}:{'duplicate' if need else 'inheritance-missing'}:{tool}")
        elif have < need:
            reasons.append(f"{label}:effect-missing:{tool}")
        else:
            reasons.append(f"{label}:unexpected-count:{tool}")
    return reasons


def _key_reasons(keys: list[str], want: list[str], label: str) -> list[str]:
    if keys == want:
        return []
    reasons = [f"{label}:filter-leakage:{k}" for k in keys if k not in (KEY_A, KEY_C)]
    counts = Counter(keys)
    reasons += [f"{label}:duplicate:{k}" for k, n in counts.items() if n > 1]
    reasons += [f"{label}:missing:{k}" for k in want if k not in counts]
    reasons += [f"{label}:unexpected:{k}" for k in counts if k in (KEY_A, KEY_C) and k not in want]
    return reasons or [f"{label}:order-or-shape"]


def _audit_reasons(observed: dict[str, Any], want: list[str], label: str) -> list[str]:
    """F2 ledger entries and OD audit entries in the `hitl:` space: one paired approve per key."""
    audits = _d(observed.get("audits"))
    f2 = [str(_d(e).get("key")) for e in audits.get("entries", [])]
    od = audits.get("od_entries", [])
    reasons = _key_reasons(f2, want, f"{label}:f2")
    reasons += _key_reasons([str(_d(e).get("key")) for e in od], want, f"{label}:od")
    for entry in od:
        if _d(entry).get("response") != "approve" or _d(entry).get("gate_level") != "ask":
            reasons.append(f"{label}:od-not-approved-at-ask:{_d(entry).get('key')}")
    return reasons


def _run_reasons(name: str, run: dict[str, Any], svc: dict[str, Any]) -> list[str]:
    """`run` of every scenario: the descent reached G through two levels and paused at witness.a."""
    reasons: list[str] = []
    if run.get("status") != "paused":
        reasons.append(f"{name}:run:not-paused")
    if run.get("depth") != 0:
        reasons.append(f"{name}:run:root-depth-not-zero")
    ids = [_d(c).get("workflow_id") for c in run.get("chain", [])]
    if ids != [ROOT_ID, MID_ID, LEAF_ID]:
        reasons.append(f"{name}:run:nested-carrier-missing")
    reasons += _tool_count_reasons(_d(svc.get("tool_counts")), {"witness.b": 3}, f"{name}:run")
    reasons += _key_reasons(list(svc.get("webhook_keys", [])), [KEY_A], f"{name}:run:webhook")
    reasons += _audit_reasons(run, [], f"{name}:run")
    return reasons


def _phase_reasons(
    label: str,
    observed: dict[str, Any],
    svc: dict[str, Any],
    tools: dict[str, int],
    webhooks: list[str],
    audits: list[str],
) -> list[str]:
    reasons = _tool_count_reasons(_d(svc.get("tool_counts")), tools, label)
    reasons += _key_reasons(list(svc.get("webhook_keys", [])), webhooks, f"{label}:webhook")
    return reasons + _audit_reasons(observed, audits, label)


def _unchanged(before: object, after: object, label: str) -> list[str]:
    """Two observed records must both exist and be equal; two absent ones are not "unchanged"."""
    first, second = _d(before), _d(after)
    if not first or not second:
        return [f"{label}-unobserved"]
    return [] if first == second else [f"{label}-changed"]


def _n1_first_resume_reasons(low: dict[str, Any], svc: dict[str, Any]) -> list[str]:
    """The lowered resume must be a terminal refusal: FAILED, the child's reason, no new record."""
    label = "n1:resume-lowered"
    status = low.get("status") if low.get("outcome") == "returned" else None
    reasons: list[str] = []
    if status == "completed":
        reasons.append(f"{label}:completed-without-the-child")
    elif status == "paused":
        reasons.append(f"{label}:paused-instead-of-refused")
    elif status != "failed":
        reasons.append(f"{label}:not-failed")
    if low.get("has_pause_snapshot") is not False:
        reasons.append(f"{label}:new-pause-snapshot")
    reasons += [
        r.replace("record-changed", "record-advanced")
        for r in _unchanged(low.get("before_ref"), low.get("ref"), f"{label}:root-record")
    ]
    cause = _d(low.get("failure_cause"))
    if cause.get("runtime_fail_class") != WORKFLOW_FAILURE_CLASS:
        reasons.append(f"{label}:failure-not-a-workflow-failure")
    fail_class = cause.get("validator_fail_class")
    refusal = parse_terminal_refusal(fail_class)
    if fail_class is None:
        reasons.append(f"{label}:child-refusal-reason-missing")
    elif refusal is None:
        reasons.append(f"{label}:terminal-refusal-grammar")
    elif refusal.family != ROOT_FAMILY:
        reasons.append(f"{label}:terminal-refusal-wrong-family")
    elif REFUSAL_REASON not in refusal.reasons:
        reasons.append(f"{label}:child-refusal-reason-missing")
    if _d(low.get("before_claim")).get("phase") != "started":
        reasons.append(f"{label}:root-claim-not-admitted")
    return reasons + _phase_reasons(label, low, svc, {"witness.b": 3}, [KEY_A], [])


def _n1_second_resume_reasons(
    low: dict[str, Any], again: dict[str, Any], svc: dict[str, Any]
) -> list[str]:
    """A second resume of the SAME root record must be claim-refused, with no effect."""
    label = "n1:resume-lowered-again"
    error = str(again.get("error_type", ""))
    reasons: list[str] = []
    if (
        again.get("outcome") != "raised"
        or not error.endswith(".ResumeClaimRefusedError")
        or again.get("reason") != "claim-refused"
    ):
        reasons.append(f"{label}:not-claim-refused")
    reasons += [
        r.replace("record-changed", "different-record")
        for r in _unchanged(low.get("before_ref"), again.get("before_ref"), f"{label}:record")
    ]
    return reasons + _phase_reasons(label, again, svc, {"witness.b": 3}, [KEY_A], [])


def behaviour_failures(
    name: str, observed: dict[str, dict[str, Any]], services: dict[str, Any]
) -> list[str]:
    """Judge one scenario's completed phases; every reason names the property that broke."""
    svc = {p: _d(services.get(p)) for p in observed}
    reasons = _run_reasons(name, observed["run"], svc["run"])
    chain = observed["run"].get("chain")
    leaf_id = _d(chain[-1]).get("run_id") if chain else None
    keys = [KEY_A, KEY_C]
    if name == "p":
        r1, r2 = observed["resume-1"], observed["resume-2"]
        for label, r in (("resume-1", r1), ("resume-2", r2)):
            if r.get("outcome") != "returned":
                reasons.append(f"p:{label}:not-returned")
            if r.get("addressed_run_id") != leaf_id:
                reasons.append(f"p:{label}:response-not-addressed-to-leaf")
            if _d(r.get("before_claim")).get("phase") != "started":
                reasons.append(f"p:{label}:prior-claim-not-started")
        if r1.get("status") != "paused":
            reasons.append("p:resume-1:placement-lost-across-resume")
        if _d(r1.get("ref")) == _d(r1.get("before_ref")):
            reasons.append("p:resume-1:record-not-advanced")
        if r2.get("status") != "completed":
            reasons.append("p:resume-2:not-completed")
        first = {"witness.a": 1, "witness.b": 3}
        reasons += _phase_reasons("p:resume-1", r1, svc["resume-1"], first, keys, [KEY_A])
        last = {"witness.a": 1, "witness.b": 3, "witness.c": 1, "witness.d": 1}
        reasons += _phase_reasons("p:resume-2", r2, svc["resume-2"], last, keys, keys)
    elif name == "n1":
        low, again = observed["resume-lowered"], observed["resume-lowered-again"]
        reasons += _n1_first_resume_reasons(low, svc["resume-lowered"])
        reasons += _n1_second_resume_reasons(low, again, svc["resume-lowered-again"])
        mid_declared: list[Any] = _d(low.get("declared_placements")).get(MID_ID) or []
        if ["witness.a"] not in mid_declared:
            reasons.append("n1:fixture:mid-lost-own-a-placement")
    elif name == "n2":
        direct = observed["resume-child-handle"]
        error = str(direct.get("error_type", ""))
        if direct.get("outcome") != "raised" or not error.endswith(".ResumeDirectChildHandleError"):
            reasons.append("n2:direct-child-handle-not-refused")
        depth = direct.get("leaf_depth")
        if not isinstance(depth, int) or isinstance(depth, bool) or depth < 1:
            reasons.append("n2:leaf-record-not-below-root")
        if _d(direct.get("leaf_claim")).get("phase") != "absent":
            reasons.append("n2:claim-created-for-refused-handle")
        reasons += _unchanged(
            direct.get("root_before_ref"), direct.get("root_ref"), "n2:root-record"
        )
        reasons += _unchanged(
            direct.get("root_before_claim"), direct.get("root_claim"), "n2:root-claim"
        )
        unchanged = {"witness.b": 3}
        reasons += _phase_reasons(
            "n2:resume", direct, svc["resume-child-handle"], unchanged, [KEY_A], []
        )
    return reasons


def evaluate(
    evidence: dict[str, dict[str, Any]], *, expected_receipt_sha256: str | None
) -> dict[str, object]:
    """Typed phase states -> sequence grammar -> behaviour. `None` receipt = source rehearsal."""
    failures: list[str] = []
    timed_out: list[str] = []
    per_scenario: dict[str, object] = {}
    for name in SCENARIOS:
        ev = _d(evidence.get(name))
        states = scenario_states(name, ev, expected_receipt_sha256)
        for state in states:
            if isinstance(state, Broken):
                failures.append(f"{name}:{state.phase}:{'+'.join(state.reasons)}")
            elif isinstance(state, TimedOut):
                timed_out.append(f"{name}:{state.phase}")
        failures += [f"{name}:{f}" for f in HELPERS.sequence_failures(states)]
        kill = _d(ev.get("tool_server")).get("kill")
        failures += [f"{name}:tool-server:{r}" for r in HELPERS.kill_reasons(kill, sigkill=True)]
        if ev.get("webhook_errors"):
            failures.append(f"{name}:webhook-listener-errors")
        for phase, run in _d(ev.get("runs")).items():
            if _d(run).get("group_survivors") is not False:
                failures.append(f"{name}:{phase}:surviving-process-group")
        completed = [s for s in states if isinstance(s, Completed)]
        if len(completed) == len(states):
            observed = {s.phase: s.observed for s in completed}
            failures += behaviour_failures(name, observed, _d(ev.get("services")))
        per_scenario[name] = [type(s).__name__ for s in states]
    if failures:
        status = "FAIL"
    elif len(timed_out) == 1:
        status = "INCONCLUSIVE"
    elif timed_out:
        status = "FAIL"
        failures.append("more-than-one-timed-out-phase")
    else:
        status = "PASS"
    label = status if expected_receipt_sha256 is not None else f"REHEARSAL-{status}"
    return {
        "status": label,
        "failure_reasons": sorted(set(failures)),
        "timed_out_phases": timed_out,
        "phase_states": per_scenario,
    }


def rehearse(
    python: Path, product_src: list[Path], root: Path, logs_root: Path
) -> dict[str, dict[str, object]]:
    """G1: every scenario through the public API, one fresh Python process per phase.

    One process per phase is required, not a choice: `api.run` registers the process-wide tracer
    provider exactly once (C-RT-06), so a second `api.run`/`api.resume` in the same process refuses.
    The children import the pinned product from source; nothing here is an installed interpreter.
    """
    helper = Path(__file__).resolve(strict=True)
    deadline = time.monotonic() + OVERALL_CAP_SECONDS
    evidence: dict[str, dict[str, object]] = {}
    fleet = Fleet([])
    with term_as_interrupt():
        for name in SCENARIOS:
            layout = Layout(root / name)
            prepare_layout(layout)
            logs = logs_root / name
            logs.mkdir(parents=True, mode=0o755)
            env = {
                **HELPERS.child_env(layout),
                "PYTHONPATH": os.pathsep.join(str(p) for p in product_src),
            }
            fixed = ["--scenario", str(layout.root)]

            def launch(
                phase: str,
                *,
                name: str = name,
                env: dict[str, str] = env,
                layout: Layout = layout,
                logs: Path = logs,
                fixed: list[str] = fixed,
            ) -> Any:
                argv = child_argv_source(python, helper, name, phase, fixed)
                return HELPERS.spawn(argv, env, layout.tmp, logs, f"{name}-{phase}")

            evidence[name] = with_services(
                layout,
                python,
                logs,
                deadline,
                fleet,
                lambda capture, name=name, layout=layout, launch=launch: run_scenario(
                    name, layout, launch, fleet, capture, deadline
                ),
            )
            evidence[name]["ledger_dir"] = str(layout.ledger_dir)
    return evidence


def run(
    candidate: Path,
    venv: Path,
    expected_head: str,
    receipt: Path,
    scenario_root: Path,
    output: Path,
) -> dict[str, object]:
    """One bounded installed attempt (needs separate approval): gates first, then every scenario.

    [LAW:no-ambient-temporal-coupling] The shared prover's parent gates (pinned head, clean tree,
    receipt, startup hooks, wheels) and the scenario-root check run BEFORE any service or child
    starts, so a mismatched receipt/head/venv is refused with nothing spawned (negative N3).
    """
    deadline = time.monotonic() + OVERALL_CAP_SECONDS
    root, installed, python = PROVER.checked_candidate(candidate, venv, expected_head)
    provenance = PROVER.checked_provenance(receipt, root, installed, expected_head)
    placement = HELPERS.checked_scenario_root(
        scenario_root, Path("/proc/self/mountinfo").read_text()
    )
    if not output.parent.is_dir() or os.path.lexists(output):
        raise ValueError("output parent must exist and output must be new")
    if output.resolve(strict=False).is_relative_to(scenario_root):
        raise ValueError("report must be outside the scenario root")
    logs = output.with_suffix(".logs")
    logs.mkdir(mode=0o755)
    scenario_root.mkdir(mode=0o700)
    helper = Path(__file__).resolve(strict=True)
    report: dict[str, object] = {
        "plan": PLAN,
        "helper_sha256": PROVER.sha256(helper),
        "shared_prover_sha256": PROVER.sha256(SHARED_PROVER_PATH),
        "b104_helpers_sha256": PROVER.sha256(HELPERS_PATH),
        "parent_interpreter": {"executable": sys.executable, "isolated": sys.flags.isolated},
        "candidate": str(root),
        "expected_head": expected_head,
        "venv": str(installed),
        "installation_receipt_sha256": PROVER.sha256(receipt),
        "wheel_sha256": {item["path"]: item["sha256"] for item in provenance["wheels"]},
        "scenario_root": placement,
        "status": "INCONCLUSIVE",
    }
    evidence: dict[str, dict[str, object]] = {}
    fleet = Fleet([])
    with term_as_interrupt():
        for name in SCENARIOS:
            layout = Layout(scenario_root / name)
            prepare_layout(layout)
            scenario_logs = logs / name
            scenario_logs.mkdir(mode=0o755)
            env = HELPERS.child_env(layout)
            fixed = [
                "--scenario-root",
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

            def launch(
                phase: str,
                *,
                name: str = name,
                env: dict[str, str] = env,
                layout: Layout = layout,
                scenario_logs: Path = scenario_logs,
                fixed: list[str] = fixed,
            ) -> Any:
                argv = child_argv_installed(python, helper, name, phase, fixed)
                return HELPERS.spawn(argv, env, layout.tmp, scenario_logs, f"{name}-{phase}")

            evidence[name] = with_services(
                layout,
                python,
                scenario_logs,
                deadline,
                fleet,
                lambda capture, name=name, layout=layout, launch=launch: run_scenario(
                    name, layout, launch, fleet, capture, deadline
                ),
            )
    report["evidence"] = evidence
    report.update(evaluate(evidence, expected_receipt_sha256=PROVER.sha256(receipt)))
    HELPERS.write_new(
        output, json.dumps(report, sort_keys=True, indent=2, default=str) + "\n", 0o644
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", nargs="?", default="plan", choices=("plan", "run", "rehearse", "_child")
    )
    parser.add_argument("scenario", nargs="?", choices=tuple(SCENARIOS))
    parser.add_argument("phase", nargs="?")
    parser.add_argument("--scenario-root", "--scenario", dest="scenario_root", type=Path)
    parser.add_argument("--source-rehearsal", action="store_true")
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--venv", type=Path)
    parser.add_argument("--provenance", type=Path)
    parser.add_argument("--expected-head")
    parser.add_argument("--python", type=Path)
    parser.add_argument("--product-src", type=Path, action="append", default=[])
    parser.add_argument("--work", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "plan":
        print(json.dumps(PLAN, sort_keys=True, indent=2))
        return 0
    if args.command == "_child":
        if (
            args.scenario is None
            or args.phase not in SCENARIOS[args.scenario]
            or args.scenario_root is None
        ):
            parser.error("_child needs SCENARIO PHASE and --scenario-root")
        prove = None
        if not args.source_rehearsal:
            if None in (args.candidate, args.venv, args.expected_head, args.provenance):
                parser.error(
                    "an installed _child needs --candidate --venv --expected-head --provenance"
                )
            prove = PROVER.installed_prover(
                args.candidate, args.venv, args.expected_head, args.provenance
            )
        return run_phase(Layout(args.scenario_root), args.phase, prove)
    if args.command == "run":
        if None in (args.candidate, args.venv, args.provenance, args.expected_head, args.output):
            parser.error("run needs --candidate --venv --provenance --expected-head --output")
        if args.scenario_root is None:
            parser.error("run needs --scenario-root (a new directory)")
        report = run(
            args.candidate,
            args.venv,
            args.expected_head,
            args.provenance,
            args.scenario_root,
            args.output,
        )
        print(
            json.dumps({"status": report["status"], "failure_reasons": report["failure_reasons"]})
        )
        return 0 if report["status"] == "PASS" else 1
    if None in (args.python, args.work, args.output) or not args.product_src:
        parser.error("rehearse needs --python --product-src (repeatable) --work --output")
    args.work.mkdir(mode=0o755)
    logs_root = args.work / "logs"
    logs_root.mkdir(mode=0o755)
    evidence = rehearse(args.python, args.product_src, args.work / "scenarios", logs_root)
    verdict = evaluate(evidence, expected_receipt_sha256=None)
    report = {"plan": PLAN, "evidence": evidence, **verdict}
    HELPERS.write_new(
        args.output, json.dumps(report, sort_keys=True, indent=2, default=str) + "\n", 0o644
    )
    print(json.dumps({"status": verdict["status"], "failure_reasons": verdict["failure_reasons"]}))
    return 0 if verdict["status"] == "REHEARSAL-PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
