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
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
import typer
import yaml
from harness_runtime import api
from harness_runtime.bootstrap import stage_1_is
from harness_runtime.config import state_placement as sp
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


def _workflow(payload: dict[str, Any] = _GATED_PAYLOAD) -> Any:
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
            HITLPlacement(position=HITLPlacementKind.PRE_ACTION, tool_filter=("witness.a",)),
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
                step_id=StepID(_GATED_STEP),
                step_kind=StepKind.TOOL_STEP,
                step_payload=payload,
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

    def manifest(self, payload: dict[str, Any] = _GATED_PAYLOAD) -> Path:
        """The gated workflow as the YAML manifest `harness run` loads."""
        wf = _workflow(payload)
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
    assert gated.marker() == []
    [audit] = gated.hitl_audits()
    assert audit["audit.cp.response"] == "reject", audit
    assert audit["audit.cp.rejection_reason_hash"] == _sha("no"), audit
    assert gated.ingresses() == ["python"]


def test_4_no_operator_refuses_as_unattended(gated: Scenario) -> None:
    result = _run(gated, None)

    _assert_rejected(result)
    assert gated.marker() == []
    [audit] = gated.hitl_audits()
    assert audit["audit.cp.response"] == "reject", audit
    assert audit["audit.cp.rejection_reason_hash"] == _sha(UNATTENDED_REASON), audit
    assert gated.ingresses() == ["unattended"]


def test_5_a_raising_operator_refuses_naming_the_failure(gated: Scenario) -> None:
    async def failing(_request: OperatorRequest) -> OperatorDecision:
        raise ValueError("boom")

    result = _run(gated, failing)

    _assert_rejected(result)
    assert gated.marker() == []
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
    gated: Scenario, stdin: Any, stderr: Any, payload: dict[str, Any] = _GATED_PAYLOAD
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
                daemon=False,
                output=cli.OutputFormat.json,
                provider=None,
                model=None,
                tenant_id=None,
                socket_path=None,
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
    assert gated.marker() == []
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
    assert gated.marker() == []
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
