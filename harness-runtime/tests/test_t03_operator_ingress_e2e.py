"""T03 (Runtime v1.144 C1-C5): operator gate decisions through the public `api.run` ingress.

One solo-developer linear workflow whose single tool step `s-gated` calls `witness.a` behind a
pre-action placement. The witness tool server is a real loopback MCP process; its call log is the
effect marker. The webhook receiver and Ollama are owned loopback stubs; provider, daemon and
collector stages are the shared in-process fakes; the tracer is a real SDK provider whose
finished spans the test reads. The CLI rows call the `harness run` command in-process with its
stdin and stderr bound to a pseudo-terminal the test answers through.
"""

from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import json
import os
import select
import socket
import subprocess
import sys
import threading
import time
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
import typer
import yaml
from harness_cp import workflow_driver
from harness_cp.hitl_placement import HITLResponse, HITLResult, PendingHITLDecision
from harness_cp.pause_resume_protocol_types import (
    HITLDeliveryCell,
    ResumeContext,
    WorkflowPauseReason,
)
from harness_runtime import api
from harness_runtime.bootstrap import stage_1_is
from harness_runtime.config import state_placement as sp
from harness_runtime.lifecycle import hitl_gate_composer as composer
from harness_runtime.lifecycle import mcp_backed_ask_user_question_surface as surface
from harness_runtime.lifecycle.ask_user_question_surface import AskUserQuestionResult
from harness_runtime.lifecycle.hitl_gate_composer import post_mutation_payload_hash
from harness_runtime.lifecycle.installation_state import (
    installation_state_bound,
    installation_state_path,
)
from harness_runtime.lifecycle.operator_input import (
    INVALID_OPERATOR_INPUT,
    NONINTERACTIVE_REASON,
    UNATTENDED_REASON,
    OperatorDecision,
    OperatorRequest,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from pydantic import ValidationError

from .integration.test_r_cc_1_api_resume import (
    _patched_runtime,  # noqa: F401  # pyright: ignore[reportPrivateUsage, reportUnusedImport]
    _stage_4_od_mod,  # pyright: ignore[reportPrivateUsage]
)

_TOOLS = Path(__file__).resolve().parents[2] / "tools"

pytestmark = [
    pytest.mark.skipif(sys.platform == "win32", reason="claim leases require POSIX flock"),
    pytest.mark.usefixtures("_patched_runtime"),
]

_WORKFLOW_ID = "wf-t03-operator-ingress"
_GATED_STEP = "s-gated"
_GATED_PAYLOAD = {"tool_id": "witness.a", "tool_args": {"value": _GATED_STEP}}
_FOLLOWUP_STEP = "s-followup"
_FOLLOWUP_PAYLOAD = {"tool_id": "witness.a", "tool_args": {"value": _FOLLOWUP_STEP}}
_CHILD_STEP = "s-child"


def _witness() -> ModuleType:
    # [LAW:one-source-of-truth] The layout, services and operator TOML are the preaction
    # witness's own; this test drives them in-process instead of keeping a second copy.
    name = "preaction_installed_witness"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, _TOOLS / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


pw = _witness()
# The `harness_runtime.cli` package re-exports its Typer `app` under the submodule's name.
cli = importlib.import_module("harness_runtime.cli.app")


def _workflow(
    payload: dict[str, Any] = _GATED_PAYLOAD,
    *,
    place_gate: bool = True,
    followup_step: bool = False,
    child_step: bool = False,
) -> Any:
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

    from .test_lifecycle_sub_agent_dispatch import _payload as child_payload

    child = (
        child_payload(child_step_kinds=(StepKind.DECLARATIVE_STEP,)).model_copy(
            update={
                "child_steps": (
                    WorkflowStep(
                        step_id=StepID("child-step-0"),
                        step_kind=StepKind.DECLARATIVE_STEP,
                        step_payload={"output": {"child": "ok"}},
                    ),
                )
            }
        )
        if child_step
        else None
    )
    chain = FallbackChain(
        primary=ProviderCandidate(
            provider="ollama", model="llama3.2:3b", family=ProviderFamily.LOCAL_OPEN_WEIGHT
        ),
        same_family=(),
        cross_family=(),
        terminal=None,
    )
    entry = WorkflowManifestEntry(
        workflow_id=_WORKFLOW_ID,
        workload_class=WorkloadClass.SOFTWARE_ENGINEERING,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        # The solo pure-pattern cell is sync-blocking: the gate asks the operator in-line.
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=TopologyPattern.SINGLE_THREADED_LINEAR,
        layer_budgets=(),
        fallback_chain=chain,
        hitl_placements=(
            (HITLPlacement(position=HITLPlacementKind.PRE_ACTION, tool_filter=("witness.a",)),)
            if place_gate
            else ()
        ),
        per_step_overrides={},
    )

    class Workflow:
        workflow_id = _WORKFLOW_ID
        workload_class = WorkloadClass.SOFTWARE_ENGINEERING
        default_model_binding = ModelBinding(provider="ollama", model="llama3.2:3b")
        manifest_entry = entry
        steps = (
            WorkflowStep(
                step_id=StepID(_GATED_STEP), step_kind=StepKind.TOOL_STEP, step_payload=payload
            ),
            *(
                (
                    WorkflowStep(
                        step_id=StepID(_FOLLOWUP_STEP),
                        step_kind=StepKind.TOOL_STEP,
                        step_payload=_FOLLOWUP_PAYLOAD,
                    ),
                )
                if followup_step
                else ()
            ),
            *(
                (
                    WorkflowStep(
                        step_id=StepID(_CHILD_STEP),
                        step_kind=StepKind.SUB_AGENT_DISPATCH,
                        step_payload=child.model_dump(),
                    ),
                )
                if child is not None
                else ()
            ),
        )

    return Workflow()


class Scenario:
    def __init__(self, layout: Any, spans: InMemorySpanExporter) -> None:
        self.layout = layout
        self.spans = spans

    def config(self) -> Any:
        return pw._config(self.layout)  # pyright: ignore[reportPrivateUsage]

    def marker(self) -> list[str]:
        """The values the gated tool was called with, in call order."""
        path = self.layout.tool_calls
        lines = path.read_text().splitlines() if path.exists() else []
        return [json.loads(line)["value"] for line in lines if line.strip()]

    def gated_dispatch_count(self) -> int:
        """Count the gated step's durable dispatch facts, independent of the tool marker."""
        path = self.layout.ledger_dir / "state.jsonl"
        lines = path.read_text().splitlines() if path.exists() else []
        action_id = f"workflow:{_WORKFLOW_ID}:step:0"
        return sum(json.loads(line)["action_id"] == action_id for line in lines if line.strip())

    def assert_zero_effects(self) -> None:
        # [LAW:behavior-not-structure] A refusal must leave both public effect witnesses empty.
        assert self.marker() == []
        assert self.gated_dispatch_count() == 0

    def manifest(
        self,
        payload: dict[str, Any] = _GATED_PAYLOAD,
        *,
        place_gate: bool = True,
        followup_step: bool = False,
        child_step: bool = False,
    ) -> Path:
        """The gated workflow as the YAML manifest `harness run` loads."""
        wf = _workflow(
            payload, place_gate=place_gate, followup_step=followup_step, child_step=child_step
        )
        document = {
            "version": 1,
            "workflow": wf.manifest_entry.model_dump(mode="json", exclude_defaults=True),
            "default_model_binding": wf.default_model_binding.model_dump(mode="json"),
            "steps": [step.model_dump(mode="json") for step in wf.steps],
        }
        path = self.layout.tmp / "workflow.yaml"
        path.write_text(yaml.safe_dump(document, sort_keys=False))
        return path

    def ingresses(self) -> list[str]:
        """`hitl.response.ingress` of every finished HITL span that carries it, in end order."""
        return [
            str(span.attributes["hitl.response.ingress"])
            for span in self.spans.get_finished_spans()
            if span.attributes and "hitl.response.ingress" in span.attributes
        ]

    def hitl_audits(self) -> list[dict[str, Any]]:
        """The step-4h OD audit attributes of every `hitl:` entry, in append order."""
        path = self.layout.ledger_dir / "audit-entries.jsonl"
        lines = path.read_text().splitlines() if path.exists() else []
        payloads = [json.loads(line)["entry"]["payload"] for line in lines if line.strip()]
        return [
            p["audit_namespace_attrs"] for p in payloads if str(p["entry_core"]).startswith("hitl:")
        ]


def _ext4(_path: Path) -> str | None:
    return "ext4"


class _TracerStage:
    def __init__(self, provider: TracerProvider) -> None:
        self.provider = provider
        self.registered_globally = False


@pytest.fixture
def gated(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    _patched_runtime: None,  # noqa: F811  # pyright: ignore[reportRedeclaration]
) -> Iterator[Scenario]:
    spans = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(spans))
    monkeypatch.setattr(
        _stage_4_od_mod,
        "materialize_tracer_provider_stage",
        lambda config, **_: _TracerStage(provider),
    )
    # Scratch dirs may be tmpfs; the real filesystem resolver is covered in test_state_placement.
    monkeypatch.setattr(stage_1_is, "linux_filesystem_type", _ext4)
    monkeypatch.setattr(sp, "linux_filesystem_type", _ext4)
    for fn in vars(sp).values():  # the placement entry points bind the probe as a default
        if "filesystem_type" in (getattr(fn, "__kwdefaults__", None) or {}):
            monkeypatch.setitem(fn.__kwdefaults__, "filesystem_type", _ext4)
    layout = pw.Layout(tmp_path / "t03")
    pw.prepare_layout(layout)
    for name, value in pw.HELPERS.child_env(layout).items():
        monkeypatch.setenv(name, value)
    prefix = tmp_path / "prefix"
    prefix.mkdir()
    monkeypatch.setattr(sys, "prefix", str(prefix))
    declaration = pw.HELPERS.installation_declaration(layout)
    with (
        pw.HELPERS.installation_state_provisioned(installation_state_path(), declaration),
        installation_state_bound(),
        pw.Owners() as owners,
    ):
        webhook = _serving(pw.WebhookCapture(), owners)
        ollama = _serving(pw.OllamaListStub(), owners)
        port = pw.HELPERS.free_loopback_port()
        pw.HELPERS.write_new(layout.mcp_server, pw.MCP_SERVER_SOURCE)
        # The solo default auto-approves the witness's READ_ONLY tool; the operator opts out so
        # the placement asks.
        config = pw.config_text(layout, webhook.port, port, ollama.port) + (
            "[runtime.hitl_auto_approve_policy]\nsolo_persona_floor_auto = false\n"
        )
        pw.HELPERS.write_new(layout.config, config)
        server = subprocess.Popen(
            [sys.executable, "-I", str(layout.mcp_server), str(layout.tool_calls), str(port)],
            cwd=layout.tmp,
        )
        owners.callback(server.wait)
        owners.callback(server.kill)
        assert _listening(server, port), "the witness tool server never listened"
        pw.HELPERS.phase_provision(layout)
        yield Scenario(layout, spans)


def _serving(listener: Any, owners: Any) -> Any:
    owners.callback(listener.server.server_close)
    listener.thread.start()
    owners.callback(listener.stop)
    return listener


def _listening(server: subprocess.Popen[bytes], port: int) -> bool:
    limit = time.monotonic() + pw.CHILD_CAP_SECONDS
    while time.monotonic() < limit and server.poll() is None:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.05)
    return False


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _answering(decision: OperatorDecision, seen: list[OperatorRequest]) -> Any:
    async def operator(request: OperatorRequest) -> OperatorDecision:
        seen.append(request)
        return decision

    return operator


def _assert_rejected(result: Any) -> None:
    assert result.status == "failed", result
    # The driver reports a failed step as RT-FAIL-WORKFLOW; the gate's own class rides its detail.
    assert result.failure_cause.runtime_fail_class == "RT-FAIL-WORKFLOW", result
    assert "RT-FAIL-HITL-GATE-REJECTED" in result.failure_cause.detail, result


def _run(gated: Scenario, operator: Any) -> Any:
    return asyncio.run(api.run(_workflow(), config=gated.config(), operator=operator))


def test_1_approve_dispatches_once_and_the_operator_saw_the_gated_step(gated: Scenario) -> None:
    seen: list[OperatorRequest] = []

    result = _run(gated, _answering(OperatorDecision(action="approve"), seen))

    assert result.status == "completed", result
    assert gated.marker() == [_GATED_STEP]
    assert gated.gated_dispatch_count() == 1
    [audit] = gated.hitl_audits()
    assert audit["audit.cp.response"] == "approve", audit
    [request] = seen
    assert request.step_id == _GATED_STEP
    assert request.payload == _GATED_PAYLOAD
    canonical = json.dumps(_GATED_PAYLOAD, sort_keys=True, separators=(",", ":"))
    assert request.payload_sha256 == _sha(canonical)
    assert gated.ingresses() == ["python"]


def test_2_edit_dispatches_the_edited_payload_and_audits_its_hash(gated: Scenario) -> None:
    # The gated step is a tool step, so the edited proposal must still name its tool and args.
    edited = {"tool_id": "witness.a", "tool_args": {"value": "edited"}}
    decision = OperatorDecision(action="edit", edited_proposal=json.dumps(edited))

    result = _run(gated, _answering(decision, []))

    assert result.status == "completed", result
    assert gated.marker() == ["edited"]
    [audit] = gated.hitl_audits()
    assert audit["audit.cp.response"] == "edit", audit
    assert audit["audit.cp.edited_proposal_hash"] == post_mutation_payload_hash(edited), audit


def test_3_reject_has_zero_effects_and_audits_the_operator_reason(gated: Scenario) -> None:
    decision = OperatorDecision(action="reject", rejection_reason="no")

    result = _run(gated, _answering(decision, []))

    _assert_rejected(result)
    gated.assert_zero_effects()
    [audit] = gated.hitl_audits()
    assert audit["audit.cp.response"] == "reject", audit
    assert audit["audit.cp.rejection_reason_hash"] == _sha("no"), audit
    assert gated.ingresses() == ["python"]


def test_4_no_operator_refuses_as_unattended(gated: Scenario) -> None:
    result = _run(gated, None)

    _assert_rejected(result)
    gated.assert_zero_effects()
    [audit] = gated.hitl_audits()
    assert audit["audit.cp.response"] == "reject", audit
    assert audit["audit.cp.rejection_reason_hash"] == _sha(UNATTENDED_REASON), audit
    assert gated.ingresses() == ["unattended"]


def test_5_a_raising_operator_refuses_naming_the_failure(gated: Scenario) -> None:
    async def failing(_request: OperatorRequest) -> OperatorDecision:
        raise ValueError("boom")

    result = _run(gated, failing)

    _assert_rejected(result)
    gated.assert_zero_effects()
    [audit] = gated.hitl_audits()
    assert audit["audit.cp.response"] == "reject", audit
    reason = "operator input callback failed: ValueError"
    assert audit["audit.cp.rejection_reason_hash"] == _sha(reason), audit
    assert gated.ingresses() == ["python"]


# --- `harness run` (C2 cli-tty) -----------------------------------------------------------------

_CLI_BOUND_SECONDS = 30.0


class Terminal:
    """A pseudo-terminal the CLI's stdin and stderr are bound to; the test is its operator."""

    def __init__(self) -> None:
        self.master, self._slave = os.openpty()
        # A terminal is not seekable, so the CLI gets separate read and write streams on it.
        self.stdin = open(self._slave, closefd=False)
        self.stderr = open(self._slave, "w", buffering=1, closefd=False)
        self.shown = ""

    def read_until(self, text: str) -> str:
        """Everything shown up to and including `text`; fails if it never appears in time."""
        limit = time.monotonic() + _CLI_BOUND_SECONDS
        while text not in self.shown:
            ready, _, _ = select.select([self.master], [], [], max(0.0, limit - time.monotonic()))
            assert ready, f"{text!r} never shown; got {self.shown[-300:]!r}"
            self.shown += os.read(self.master, 65536).decode(errors="replace")
        return self.shown

    def answer(self, line: str) -> None:
        os.write(self.master, f"{line}\n".encode())

    def __enter__(self) -> Terminal:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def close(self) -> None:
        self.stdin.close()
        self.stderr.close()
        os.close(self._slave)
        os.close(self.master)


@pytest.fixture
def terminal() -> Iterator[Terminal]:
    pty = Terminal()
    yield pty
    pty.close()


def _harness_run(
    gated: Scenario,
    stdin: Any,
    stderr: Any,
    payload: dict[str, Any] = _GATED_PAYLOAD,
    socket_path: Path | None = None,
) -> int:
    """`harness run <manifest>` on the calling (main) thread; ingress installs signal wakeups."""
    # The command binds its terminal operator from `sys.stdin`/`sys.stderr`.
    with pytest.MonkeyPatch.context() as streams:
        streams.setattr(sys, "stdin", stdin)
        streams.setattr(sys, "stderr", stderr)
        with pytest.raises(typer.Exit) as exit_:
            cli.run_command(
                gated.manifest(payload),
                config=gated.layout.config,
                daemon=socket_path is not None,
                output=cli.OutputFormat.json,
                provider=None,
                model=None,
                tenant_id=None,
                socket_path=socket_path,
                daemon_result_timeout_seconds=None,
            )
    return exit_.value.exit_code


class Operator:
    """Answers the terminal's first prompt once it is fully shown, recording what preceded it."""

    def __init__(self, gated: Scenario, terminal: Terminal, line: str) -> None:
        self.shown = ""
        self.marker_before_answer: list[str] | None = None
        self._thread = threading.Thread(target=self._answer, args=(gated, terminal, line))
        self._thread.start()

    def _answer(self, gated: Scenario, terminal: Terminal, line: str) -> None:
        self.shown = terminal.read_until("answer (")
        self.marker_before_answer = gated.marker()
        terminal.answer(line)

    def done(self) -> Operator:
        self._thread.join(_CLI_BOUND_SECONDS)
        assert not self._thread.is_alive(), "the prompt was never shown"
        return self


def _assert_gate_shown(operator: Operator) -> None:
    canonical = json.dumps(_GATED_PAYLOAD, sort_keys=True, separators=(",", ":"))
    assert f"step: {_GATED_STEP} (tool-step)" in operator.shown
    assert f"payload sha256: {_sha(canonical)}" in operator.shown
    assert operator.marker_before_answer == []  # nothing dispatched before the answer


def test_6_harness_run_without_a_terminal_refuses_as_noninteractive(gated: Scenario) -> None:
    started = time.monotonic()
    with open(os.devnull) as stdin:
        code = _harness_run(gated, stdin, sys.__stderr__)

    assert code == cli.EXIT_WORKFLOW_FAIL
    assert time.monotonic() - started < _CLI_BOUND_SECONDS
    gated.assert_zero_effects()
    [audit] = gated.hitl_audits()
    assert audit["audit.cp.response"] == "reject", audit
    assert audit["audit.cp.rejection_reason_hash"] == _sha(NONINTERACTIVE_REASON), audit
    assert gated.ingresses() == ["cli-tty"]


def test_7_harness_run_on_a_terminal_shows_the_gate_then_approves(
    gated: Scenario, terminal: Terminal
) -> None:
    operator = Operator(gated, terminal, "approve")

    assert _harness_run(gated, terminal.stdin, terminal.stderr) == cli.EXIT_SUCCESS
    _assert_gate_shown(operator.done())
    assert gated.marker() == [_GATED_STEP]
    assert gated.ingresses() == ["cli-tty"]


def test_7_harness_run_on_a_terminal_refuses_invalid_input(
    gated: Scenario, terminal: Terminal
) -> None:
    operator = Operator(gated, terminal, "bogus")

    assert _harness_run(gated, terminal.stdin, terminal.stderr) == cli.EXIT_WORKFLOW_FAIL
    _assert_gate_shown(operator.done())
    gated.assert_zero_effects()
    [audit] = gated.hitl_audits()
    assert audit["audit.cp.rejection_reason_hash"] == _sha(INVALID_OPERATOR_INPUT), audit
    assert gated.ingresses() == ["cli-tty"]


def test_4_to_7_refusal_reasons_are_pairwise_distinct() -> None:
    reasons = (
        UNATTENDED_REASON,
        "operator input callback failed: ValueError",
        NONINTERACTIVE_REASON,
        INVALID_OPERATOR_INPUT,
    )
    assert len({_sha(reason) for reason in reasons}) == len(reasons)


def test_16_a_large_payload_is_shown_in_full_before_the_answer(
    gated: Scenario, terminal: Terminal
) -> None:
    # Canonical JSON sorts keys, so the padding precedes `danger_tail` past the 8192-byte mark.
    payload = {**_GATED_PAYLOAD, "aa_padding": "x" * 9000, "danger_tail": "rm -rf ~"}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    assert canonical.index('"danger_tail"') > 8192
    operator = Operator(gated, terminal, "approve")

    assert _harness_run(gated, terminal.stdin, terminal.stderr, payload) == cli.EXIT_SUCCESS
    operator.done()
    assert canonical in operator.shown
    assert '"danger_tail":"rm -rf ~"' in operator.shown
    assert operator.marker_before_answer == []
    assert gated.marker() == [_GATED_STEP]


# --- `harness run --daemon` (C2 daemon-client-tty) ----------------------------------------------

# The daemon is its own process; it reads the fixture's provisioned installation state through the
# same interpreter prefix the in-process rows use, writes the attributes of each span it finishes
# as one JSON line, and waits on the elicitation deadline it is given.
_DAEMON_LAUNCH = """
import json, sys
sys.prefix, spans, deadline = sys.argv.pop(1), sys.argv.pop(1), sys.argv.pop(1)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from harness_runtime.bootstrap import stage_4_od
from harness_runtime.lifecycle import mcp_backed_ask_user_question_surface as surface
provider = TracerProvider()
sink = open(spans, "a", buffering=1)
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter(
    out=sink, formatter=lambda span: json.dumps(dict(span.attributes or {})) + "\\n"
)))
class Stage:
    registered_globally = False
Stage.provider = provider
stage_4_od.materialize_tracer_provider_stage = lambda config, **_: Stage
surface.OPERATOR_ELICITATION_DEADLINE_SECONDS = float(deadline)
from harness_runtime.cli.app import app
app(prog_name="harness")
"""
_PATCHED_DEADLINE_SECONDS = 2.0
_DEADLINE_SLACK_SECONDS = 8.0


def _daemon_spans(gated: Scenario) -> Path:
    return gated.layout.tmp / "daemon-spans.jsonl"


def _daemon_ingresses(gated: Scenario) -> list[str]:
    """`hitl.response.ingress` of every HITL span the daemon finished, in end order."""
    path = _daemon_spans(gated)
    rows = [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
    return [str(row["hitl.response.ingress"]) for row in rows if "hitl.response.ingress" in row]


def _serve_daemon(gated: Scenario, deadline_seconds: float) -> Iterator[Path]:
    socket_path = gated.layout.tmp / "harness-daemon.sock"
    argv = [sys.executable, "-c", _DAEMON_LAUNCH, sys.prefix, str(_daemon_spans(gated))]
    argv += [str(deadline_seconds), "daemon", "--config", str(gated.layout.config)]
    argv += ["--socket-path", str(socket_path)]
    log = gated.layout.tmp / "daemon.log"
    with log.open("wb") as sink:
        server = subprocess.Popen(argv, cwd=gated.layout.tmp, stdout=sink, stderr=sink)
    limit = time.monotonic() + pw.CHILD_CAP_SECONDS
    while not socket_path.exists() and server.poll() is None and time.monotonic() < limit:
        time.sleep(0.05)
    assert socket_path.exists(), f"daemon never bound: {log.read_text()[-2000:]}"
    yield socket_path
    server.terminate()
    assert server.wait(pw.CHILD_CAP_SECONDS) is not None


@pytest.fixture
def daemon(gated: Scenario) -> Iterator[Path]:
    yield from _serve_daemon(gated, surface.OPERATOR_ELICITATION_DEADLINE_SECONDS)


@pytest.fixture
def hasty_daemon(gated: Scenario) -> Iterator[Path]:
    """A daemon whose elicitation deadline is patched to 2 s (assertion 13)."""
    yield from _serve_daemon(gated, _PATCHED_DEADLINE_SECONDS)


def test_8_one_daemon_serves_an_approve_then_a_reject_on_a_terminal(
    gated: Scenario, daemon: Path
) -> None:
    with Terminal() as first:
        operator = Operator(gated, first, "approve")
        code = _harness_run(gated, first.stdin, first.stderr, socket_path=daemon)
        _assert_gate_shown(operator.done())
    assert code == cli.EXIT_SUCCESS
    assert gated.marker() == [_GATED_STEP]

    with Terminal() as second:
        operator = Operator(gated, second, "reject")
        code = _harness_run(gated, second.stdin, second.stderr, socket_path=daemon)
        assert operator.done().marker_before_answer == [_GATED_STEP]
    assert code == cli.EXIT_WORKFLOW_FAIL
    assert gated.marker() == [_GATED_STEP]
    assert gated.gated_dispatch_count() == 1
    approve, reject = gated.hitl_audits()
    assert (approve["audit.cp.response"], reject["audit.cp.response"]) == ("approve", "reject")
    assert _daemon_ingresses(gated) == ["daemon-client-tty", "daemon-client-tty"]


# --- `cancel`, the bounded wait and replies outside C1/C5 (C3, C3a, C5) -------------------------


def _harness_client(gated: Scenario, socket_path: Path, terminal: Terminal) -> Any:
    """`harness run --daemon` as its own process on `terminal`, so the test can kill it."""
    argv = [sys.executable, "-c", _DAEMON_LAUNCH, sys.prefix, os.devnull, "0", "run"]
    argv += [str(gated.manifest()), "--daemon", "--socket-path", str(socket_path)]
    argv += ["--config", str(gated.layout.config)]
    slave = terminal.stdin.fileno()
    return subprocess.Popen(argv, cwd=gated.layout.tmp, stdin=slave, stdout=slave, stderr=slave)


def _eliciting(monkeypatch: pytest.MonkeyPatch, reply: Any) -> None:
    """Bind `api.run`'s in-process client to one raw MCP elicitation reply, as another client."""

    async def answer(_context: Any, _params: Any) -> Any:
        return reply

    monkeypatch.setattr(api, "operator_elicitation_callback", lambda *_: answer)


def test_12_cancel_through_api_run_refuses_under_the_python_ingress(gated: Scenario) -> None:
    result = _run(gated, _answering(OperatorDecision(action="cancel"), []))

    _assert_rejected(result)
    gated.assert_zero_effects()
    assert gated.ingresses() == ["python"]


def test_12_cancel_on_a_terminal_refuses_under_the_cli_tty_ingress(
    gated: Scenario, terminal: Terminal
) -> None:
    operator = Operator(gated, terminal, "cancel")

    assert _harness_run(gated, terminal.stdin, terminal.stderr) == cli.EXIT_WORKFLOW_FAIL
    _assert_gate_shown(operator.done())
    gated.assert_zero_effects()
    assert gated.ingresses() == ["cli-tty"]


def test_12_cancel_through_the_daemon_refuses_under_the_daemon_client_tty_ingress(
    gated: Scenario, daemon: Path
) -> None:
    with Terminal() as pty:
        operator = Operator(gated, pty, "cancel")
        code = _harness_run(gated, pty.stdin, pty.stderr, socket_path=daemon)
        _assert_gate_shown(operator.done())

    assert code == cli.EXIT_WORKFLOW_FAIL
    gated.assert_zero_effects()
    assert _daemon_ingresses(gated) == ["daemon-client-tty"]


def test_12_an_mcp_native_cancel_refuses_as_unreported(
    gated: Scenario, monkeypatch: pytest.MonkeyPatch
) -> None:
    from mcp.types import ElicitResult

    _eliciting(monkeypatch, ElicitResult(action="cancel"))

    _assert_rejected(_run(gated, None))
    gated.assert_zero_effects()
    assert gated.ingresses() == ["unreported"]


def test_13_the_unpatched_elicitation_deadline_is_900_seconds() -> None:
    assert surface.OPERATOR_ELICITATION_DEADLINE_SECONDS == 900


@pytest.fixture
def hasty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(surface, "OPERATOR_ELICITATION_DEADLINE_SECONDS", _PATCHED_DEADLINE_SECONDS)


def _within_deadline(started: float) -> None:
    assert time.monotonic() - started < _PATCHED_DEADLINE_SECONDS + _DEADLINE_SLACK_SECONDS


@pytest.mark.usefixtures("hasty")
def test_13a_an_api_run_operator_that_never_answers_is_refused_at_the_deadline(
    gated: Scenario,
) -> None:
    async def silent(_request: OperatorRequest) -> OperatorDecision:
        await asyncio.Event().wait()
        raise AssertionError("unreachable")

    started = time.monotonic()
    result = _run(gated, silent)

    _within_deadline(started)
    _assert_rejected(result)
    gated.assert_zero_effects()
    assert gated.ingresses() == ["none"]


def test_13b_a_daemon_client_killed_at_the_prompt_ends_its_run_then_the_daemon_serves_on(
    gated: Scenario, hasty_daemon: Path
) -> None:
    with Terminal() as pty:
        client = _harness_client(gated, hasty_daemon, pty)
        pty.read_until("answer (")
        started = time.monotonic()
        client.kill()
        assert client.wait(_CLI_BOUND_SECONDS) is not None
        while not _daemon_ingresses(gated):
            assert time.monotonic() - started < _CLI_BOUND_SECONDS, "the daemon's gate never ended"
            time.sleep(0.05)
    _within_deadline(started)
    gated.assert_zero_effects()
    assert _daemon_ingresses(gated) == ["none"]

    with Terminal() as following:
        operator = Operator(gated, following, "approve")
        code = _harness_run(gated, following.stdin, following.stderr, socket_path=hasty_daemon)
        operator.done()
    assert code == cli.EXIT_SUCCESS
    assert gated.marker() == [_GATED_STEP]


@pytest.mark.usefixtures("hasty")
def test_13c_an_attached_silent_terminal_is_refused_at_the_deadline(
    gated: Scenario, terminal: Terminal
) -> None:
    started = time.monotonic()
    code = _harness_run(gated, terminal.stdin, terminal.stderr)

    _within_deadline(started)
    assert code == cli.EXIT_WORKFLOW_FAIL
    assert "answer (" in terminal.read_until("answer (")
    gated.assert_zero_effects()
    assert gated.ingresses() == ["none"]


def test_13c_an_attached_silent_terminal_through_the_daemon_is_refused_at_the_deadline(
    gated: Scenario, hasty_daemon: Path
) -> None:
    with Terminal() as pty:
        started = time.monotonic()
        code = _harness_run(gated, pty.stdin, pty.stderr, socket_path=hasty_daemon)
        _within_deadline(started)
        assert "answer (" in pty.read_until("answer (")

    assert code == cli.EXIT_WORKFLOW_FAIL
    gated.assert_zero_effects()
    assert _daemon_ingresses(gated) == ["none"]


@pytest.mark.parametrize(
    "content",
    [
        {"response": "approve", "ingress": "root"},
        {"response": "refuse", "ingress": "python"},
    ],
    ids=["ingress-root", "refuse-without-reason"],
)
def test_14_a_reply_outside_c1_c5_is_refused_with_zero_effects(
    gated: Scenario, monkeypatch: pytest.MonkeyPatch, content: dict[str, str]
) -> None:
    from mcp.types import ElicitResult

    _eliciting(monkeypatch, ElicitResult(action="accept", content=content))

    result = _run(gated, None)

    assert result.status == "failed", result
    gated.assert_zero_effects()


# --- `hold` into the durable pause, then one public resume (C3, C4) ----------------------------


class Resumed:
    """What the public resume admitted and what the resumed gate routed for it."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.entries: list[Any] = []
        self.routed: list[HITLResult] = []
        self.live_action_kinds: list[str] = []
        admit, build = api.admit_root_resume, composer._hitl_result_from_pending  # pyright: ignore[reportPrivateUsage]
        derive = composer._compose_hitl_handoff_context  # pyright: ignore[reportPrivateUsage]

        async def admitted(*args: Any, **kwargs: Any) -> Any:
            entry = await admit(*args, **kwargs)
            self.entries.append(entry)
            return entry

        def routed(*args: Any, **kwargs: Any) -> HITLResult:
            result = build(*args, **kwargs)
            self.routed.append(result)
            return result

        def live(*args: Any, **kwargs: Any) -> Any:
            context = derive(*args, **kwargs)
            self.live_action_kinds.append(str(context.proposed_action.action_kind))
            return context

        monkeypatch.setattr(api, "admit_root_resume", admitted)
        monkeypatch.setattr(composer, "_hitl_result_from_pending", routed)
        monkeypatch.setattr(composer, "_compose_hitl_handoff_context", live)


@pytest.fixture
def resumed(monkeypatch: pytest.MonkeyPatch) -> Resumed:
    return Resumed(monkeypatch)


def _harness_resume(
    gated: Scenario,
    response: Any = None,
    edited_proposal: str | None = None,
    *,
    place_gate: bool = True,
    followup_step: bool = False,
    child_step: bool = False,
    response_text: str | None = None,
) -> int:
    """`harness resume <manifest> [--hitl-response ...]`; the manifest names the handle."""
    with pytest.raises(typer.Exit) as exit_:
        cli.resume_command(
            gated.manifest(
                place_gate=place_gate, followup_step=followup_step, child_step=child_step
            ),
            config=gated.layout.config,
            tenant_id=None,
            output=cli.OutputFormat.json,
            hitl_response=response,
            edited_proposal=edited_proposal,
            response_text=response_text,
            rejection_reason=None,
        )
    return exit_.value.exit_code


def _held(gated: Scenario) -> Any:
    """`api.run` whose operator holds: PAUSED at the gate with the durable resume handle."""
    result = _run(gated, _answering(OperatorDecision(action="hold"), []))
    assert result.status == "paused", result
    assert result.pause_snapshot.workflow_id == _WORKFLOW_ID
    assert result.pause_snapshot.pause_reason is WorkflowPauseReason.HITL_PENDING
    gated.assert_zero_effects()
    assert gated.hitl_audits() == []
    return result.pause_snapshot


def test_9_hold_then_one_public_resume_approves_under_the_gates_own_audit_identity(
    gated: Scenario, resumed: Resumed
) -> None:
    snapshot = _held(gated)
    started = datetime.now(UTC)

    assert _harness_resume(gated, cli.HITLResumeResponse.approve) == cli.EXIT_SUCCESS

    assert gated.marker() == [_GATED_STEP]
    [entry] = resumed.entries
    context = entry.resume_context
    assert context.pending_hitl_decision == PendingHITLDecision(response=HITLResponse.APPROVE)
    assert (context.hitl_response, context.hitl_responses) == (None, None)
    # Neither a child run nor any other run id is addressed by the pending decision.
    assert context.hitl_response_for(snapshot.run_id) is None
    [routed] = resumed.routed  # the resumed root gate consumed it once
    [audit] = gated.hitl_audits()
    audit_id = audit["audit.cp.action_id"]
    assert routed.audit_ledger_entry_id == audit_id
    approve = AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=0.0)
    assert routed.response_summary_hash == composer._compute_response_summary_hash(approve)  # pyright: ignore[reportPrivateUsage]
    assert started <= datetime.fromisoformat(routed.timestamp) <= datetime.now(UTC)
    assert audit_id != snapshot.state_ledger_anchor
    assert entry.pause_snapshot.state_ledger_anchor == snapshot.state_ledger_anchor


def test_9_optional_approval_note_resumes_as_approval(gated: Scenario, resumed: Resumed) -> None:
    _held(gated)

    result = asyncio.run(
        api.resume(
            _workflow(),
            resume_handle=_WORKFLOW_ID,
            operator_decision=OperatorDecision(
                action="approve", response_text="approved with note"
            ),
            config=gated.config(),
        )
    )

    assert result.status == "completed"
    assert gated.marker() == [_GATED_STEP]
    [entry] = resumed.entries
    assert entry.resume_context.pending_hitl_decision == PendingHITLDecision(
        response=HITLResponse.APPROVE
    )
    [audit] = gated.hitl_audits()
    assert audit["audit.cp.response"] == "approve"


def test_9_pending_decision_does_not_answer_a_later_gate(gated: Scenario) -> None:
    result = asyncio.run(
        api.run(
            _workflow(followup_step=True),
            config=gated.config(),
            operator=_answering(OperatorDecision(action="hold"), []),
        )
    )
    assert result.status == "paused", result
    gated.assert_zero_effects()

    # The public resume answers step 0. Step 1 has no operator and must refuse.
    assert (
        _harness_resume(gated, cli.HITLResumeResponse.approve, followup_step=True)
        == cli.EXIT_WORKFLOW_FAIL
    )
    assert gated.marker() == [_GATED_STEP]
    assert gated.gated_dispatch_count() == 1
    assert [audit["audit.cp.response"] for audit in gated.hitl_audits()] == [
        "approve",
        "reject",
    ]


def test_9_pending_decision_is_not_delivered_to_a_child_run(
    gated: Scenario, monkeypatch: pytest.MonkeyPatch
) -> None:
    step_context = workflow_driver.StepExecutionContext
    observed: list[tuple[str, int, bool]] = []

    def record_context(**fields: Any) -> Any:
        observed.append(
            (
                str(fields["parent_action_id"]),
                int(fields["descent_depth"]),
                fields.get("hitl_delivery_holder") is None,
            )
        )
        return step_context(**fields)

    monkeypatch.setattr(workflow_driver, "StepExecutionContext", record_context)
    result = asyncio.run(
        api.run(
            _workflow(child_step=True),
            config=gated.config(),
            operator=_answering(OperatorDecision(action="hold"), []),
        )
    )
    assert result.status == "paused", result
    gated.assert_zero_effects()

    assert _harness_resume(gated, cli.HITLResumeResponse.approve, child_step=True) == (
        cli.EXIT_SUCCESS
    )
    assert gated.marker() == [_GATED_STEP]
    assert gated.gated_dispatch_count() == 1
    assert (f"workflow:{_WORKFLOW_ID}:step:0", 0, False) in observed
    assert (f"workflow:{_WORKFLOW_ID}:step:1", 0, True) in observed
    child = [item for item in observed if item[1] > 0]
    assert child, observed
    assert all(no_delivery for _, _, no_delivery in child)


def test_9_the_pending_decision_is_one_response_authority_consumed_once() -> None:
    pending = PendingHITLDecision(response=HITLResponse.APPROVE)
    approve = HITLResult(
        response=HITLResponse.APPROVE,
        timestamp="t",
        audit_ledger_entry_id="a",
        response_summary_hash="h",
    )
    with pytest.raises(ValidationError):
        ResumeContext(pending_hitl_decision=pending, hitl_response=approve)
    with pytest.raises(ValidationError):
        ResumeContext(pending_hitl_decision=pending, hitl_responses={"run": approve})
    cell = HITLDeliveryCell(pending)
    assert cell.consume_and_clear() == pending
    assert cell.consume_and_clear() is None


def test_9_hold_on_a_terminal_pauses_then_resumes_once(gated: Scenario, terminal: Terminal) -> None:
    operator = Operator(gated, terminal, "hold")

    assert _harness_run(gated, terminal.stdin, terminal.stderr) == cli.EXIT_PAUSED
    _assert_gate_shown(operator.done())
    gated.assert_zero_effects()
    assert gated.hitl_audits() == []

    assert (
        _harness_resume(gated, cli.HITLResumeResponse.approve, response_text="approved with note")
        == cli.EXIT_SUCCESS
    )
    assert gated.marker() == [_GATED_STEP]


def test_9_a_decision_against_a_non_hitl_pause_is_refused_before_any_claim(
    gated: Scenario,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    execute = workflow_driver.execute_workflow
    pause_first = True

    def pause_before_step(manifest_entry: Any, steps: Any, run_id: str, ctx: Any, **kw: Any) -> Any:
        nonlocal pause_first
        if pause_first:
            ctx.pause_requested_flag.set()
            pause_first = False
        return execute(manifest_entry, steps, run_id, ctx, **kw)

    monkeypatch.setattr(workflow_driver, "execute_workflow", pause_before_step)
    result = asyncio.run(api.run(_workflow(place_gate=False), config=gated.config()))
    assert result.status == "paused", result
    assert result.pause_snapshot.pause_reason is WorkflowPauseReason.EXPLICIT_OPERATOR
    gated.assert_zero_effects()

    assert _harness_resume(gated, cli.HITLResumeResponse.approve, place_gate=False) == (
        cli.EXIT_RESUME_REFUSED
    )
    gated.assert_zero_effects()
    # The public argument refusal spent no claim; the same durable handle still resumes.
    assert _harness_resume(gated, place_gate=False) == cli.EXIT_SUCCESS
    assert gated.marker() == [_GATED_STEP]
    assert gated.gated_dispatch_count() == 1


def test_10_hold_without_the_durable_pause_binding_is_an_audited_reject(gated: Scenario) -> None:
    binding = "[runtime.pause_resume_protocol_config]\ndurable = true\n"
    config = gated.layout.config.read_text()
    assert config.count(binding) == 1
    gated.layout.config.write_text(config.replace(binding, ""))

    result = _run(gated, _answering(OperatorDecision(action="hold"), []))

    _assert_rejected(result)
    gated.assert_zero_effects()
    [audit] = gated.hitl_audits()
    assert audit["audit.cp.response"] == "reject", audit
    reason = "hold unavailable: no durable pause binding"
    assert audit["audit.cp.rejection_reason_hash"] == _sha(reason), audit


def test_11_a_second_resume_of_a_resumed_handle_is_refused(gated: Scenario) -> None:
    _held(gated)
    assert _harness_resume(gated, cli.HITLResumeResponse.approve) == cli.EXIT_SUCCESS

    assert _harness_resume(gated, cli.HITLResumeResponse.approve) == cli.EXIT_RESUME_CLAIM_REFUSED
    assert gated.marker() == [_GATED_STEP]
    assert gated.gated_dispatch_count() == 1


def test_17_public_resume_edit_keeps_the_live_action_kind_and_dispatches_the_edit(
    gated: Scenario, resumed: Resumed
) -> None:
    _held(gated)
    [live_kind] = resumed.live_action_kinds  # the held gate's own derivation, before the hold
    edited = {"tool_id": "witness.a", "tool_args": {"value": "edited"}}

    code = _harness_resume(gated, cli.HITLResumeResponse.edit, json.dumps(edited))

    assert code == cli.EXIT_SUCCESS
    [routed] = resumed.routed
    assert routed.edited_proposal is not None
    assert str(routed.edited_proposal.action_kind) == live_kind
    assert routed.edited_proposal.payload == edited
    assert gated.marker() == ["edited"]
    [audit] = gated.hitl_audits()
    assert audit["audit.cp.edited_proposal_hash"] == post_mutation_payload_hash(edited), audit


@pytest.mark.parametrize("proposal", ["not json", "[1]"])
def test_17_an_undecodable_edit_is_refused_without_spending_the_handle(
    gated: Scenario, proposal: str
) -> None:
    _held(gated)

    code = _harness_resume(gated, cli.HITLResumeResponse.edit, proposal)

    assert code == cli.EXIT_RESUME_REFUSED
    gated.assert_zero_effects()
    assert gated.hitl_audits() == []
    assert _harness_resume(gated, cli.HITLResumeResponse.approve) == cli.EXIT_SUCCESS
    assert gated.marker() == [_GATED_STEP]


async def _daemon_resume(socket_path: Path, manifest: Path, decision: dict[str, str]) -> Any:
    """The daemon's public `resume_workflow` tool over its Unix socket, as a client calls it."""
    import httpx
    from mcp import ClientSession
    from mcp.client.streamable_http import streamable_http_client

    transport = httpx.AsyncHTTPTransport(uds=str(socket_path))
    timeout = httpx.Timeout(_CLI_BOUND_SECONDS)
    async with (
        httpx.AsyncClient(transport=transport, timeout=timeout) as http,
        streamable_http_client(
            cli._DAEMON_CLIENT_STREAMABLE_HTTP_URL,  # pyright: ignore[reportPrivateUsage]
            http_client=http,
        ) as (read, write, _session_id),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        arguments = {"workflow_id": str(manifest), "operator_decision": decision}
        return await session.call_tool("resume_workflow", arguments)


def test_9_hold_through_the_daemon_pauses_then_its_resume_approves_once(
    gated: Scenario, daemon: Path
) -> None:
    with Terminal() as pty:
        operator = Operator(gated, pty, "hold")
        code = _harness_run(gated, pty.stdin, pty.stderr, socket_path=daemon)
        _assert_gate_shown(operator.done())
    assert code == cli.EXIT_PAUSED
    gated.assert_zero_effects()
    assert gated.hitl_audits() == []

    reply = asyncio.run(
        _daemon_resume(
            daemon, gated.manifest(), {"action": "approve", "response_text": "approved with note"}
        )
    )

    assert not reply.isError, reply
    assert reply.structuredContent["status"] == "success", reply  # the CP RunResult wire value
    assert gated.marker() == [_GATED_STEP]
    [audit] = gated.hitl_audits()
    assert audit["audit.cp.response"] == "approve", audit
