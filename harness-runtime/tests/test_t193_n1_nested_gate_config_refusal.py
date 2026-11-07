"""T193 N1: a nested child's gate-config refusal reaches the root as a terminal typed refusal.

Root ORCHESTRATOR_WORKERS -> mid ORCHESTRATOR_WORKERS -> leaf SINGLE_THREADED_LINEAR, built by the
pre-action witness's own `build_workflow`. The run pauses at the leaf's pre-action gate; the resume
drops the root's `pre("witness.a")` placement, so the leaf's resume guard refuses. Everything on
the path is real: public `api.run`/`api.resume`, bootstrap, the durable journal and claim store,
the child runner and sub-agent dispatch, the tool HITL composer and a loopback MCP tool server.
The webhook receiver is an owned loopback stub; provider, daemon and tracer stages are the shared
in-process fakes.
"""

from __future__ import annotations

import importlib.util
import socket
import subprocess
import sys
import time
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
from harness_runtime.bootstrap import stage_1_is
from harness_runtime.config import state_placement as sp

from .integration.test_r_cc_1_api_resume import (
    _patched_runtime,  # noqa: F401  # pyright: ignore[reportPrivateUsage, reportUnusedImport]
)

_TOOLS = Path(__file__).resolve().parents[2] / "tools"

# Each phase bootstraps in this one process, so the once-per-process provider, daemon and tracer
# stages are the shared fakes; every stage the refusal path crosses stays real.
pytestmark = [
    pytest.mark.skipif(sys.platform == "win32", reason="claim leases require POSIX flock"),
    pytest.mark.usefixtures("_patched_runtime"),
]


def _witness() -> ModuleType:
    # [LAW:one-source-of-truth] The N1 topology, services and observations are the witness's own;
    # this test drives them in-process instead of keeping a second copy that could drift.
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


class Scenario:
    """One N1 layout with its owned webhook, Ollama stub and tool server, provisioned once."""

    def __init__(self, layout: Any, webhook: Any, ollama: Any) -> None:
        self.layout = layout
        self.webhook = webhook
        self.ollama = ollama

    def tools(self) -> dict[str, int]:
        return pw.tool_counts(self.layout)

    def webhook_keys(self) -> list[str]:
        return [str(r["idempotency_key"]) for r in self.webhook.requests]


def _ext4(_path: Path) -> str | None:
    return "ext4"


@pytest.fixture
def n1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Scenario]:
    # Scratch dirs may be tmpfs; the real filesystem resolver is covered in test_state_placement.
    monkeypatch.setattr(stage_1_is, "linux_filesystem_type", _ext4)
    monkeypatch.setattr(sp, "linux_filesystem_type", _ext4)
    for fn in vars(sp).values():  # the placement entry points bind the probe as a default
        if "filesystem_type" in (getattr(fn, "__kwdefaults__", None) or {}):
            monkeypatch.setitem(fn.__kwdefaults__, "filesystem_type", _ext4)
    layout = pw.Layout(tmp_path / "n1")
    pw.prepare_layout(layout)
    for name, value in pw.HELPERS.child_env(layout).items():
        monkeypatch.setenv(name, value)
    with pw.Owners() as owners, pw.HELPERS.installation_bound(layout):
        webhook = _serving(pw.WebhookCapture(), owners)
        ollama = _serving(pw.OllamaListStub(), owners)
        port = pw.HELPERS.free_loopback_port()
        pw.HELPERS.write_new(layout.mcp_server, pw.MCP_SERVER_SOURCE)
        pw.HELPERS.write_new(layout.config, pw.config_text(layout, webhook.port, port, ollama.port))
        server = subprocess.Popen(
            [sys.executable, "-I", str(layout.mcp_server), str(layout.tool_calls), str(port)],
            cwd=layout.tmp,
        )
        owners.callback(server.wait)
        owners.callback(server.kill)
        assert _listening(server, port), "the witness tool server never listened"
        pw.HELPERS.phase_provision(layout)
        yield Scenario(layout, webhook, ollama)


def _serving(listener: Any, owners: Any) -> Any:
    # [LAW:no-ambient-temporal-coupling] `started_under` proves no thread can take SIGINT, which only
    # a single-run witness process can satisfy: the runtime's process-wide audit-offload daemon
    # thread outlives each in-process bootstrap. Nothing here is ordered by signals, so the listener
    # keeps the same socket/thread ownership without that proof.
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


def _paused(n1: Scenario) -> dict[str, Any]:
    run = pw.phase_run(n1.layout)
    assert run["status"] == "paused", run
    # The leaf's gate on witness.a paused it after the root and mid orchestrators ran witness.b.
    assert n1.tools() == {"witness.b": 3}
    assert n1.webhook_keys() == [pw.KEY_A]
    return run


def test_a_dropped_root_placement_refuses_the_nested_resume_terminally_then_claim_refuses(
    n1: Scenario,
) -> None:
    _paused(n1)

    low = pw.phase_resume(n1.layout, root_has_placement=False)

    assert low["outcome"] == "returned", (low.get("error_type"), low.get("message"))
    assert low["status"] == "failed" and low["has_pause_snapshot"] is False, low
    cause = low["failure_cause"]
    assert cause["runtime_fail_class"] == pw.WORKFLOW_FAILURE_CLASS, cause
    refusal = pw.parse_terminal_refusal(cause["validator_fail_class"])
    assert refusal is not None, cause
    assert refusal.family == pw.ROOT_FAMILY
    assert pw.REFUSAL_REASON in refusal.reasons
    assert low["ref"] == low["before_ref"], "the refusal journaled a new root record"
    assert low["before_claim"]["phase"] == "started"
    assert n1.tools() == {"witness.b": 3}  # the refused resume ran no step

    again = pw.phase_resume(n1.layout, root_has_placement=False)

    assert again["outcome"] == "raised", again
    assert again["error_type"].endswith(".ResumeClaimRefusedError")
    assert again["reason"] == "claim-refused"
    assert again["before_ref"] == low["before_ref"]
    assert n1.tools() == {"witness.b": 3}


def test_an_unchanged_config_resume_runs_the_approved_step_and_pauses_at_the_next_gate(
    n1: Scenario,
) -> None:
    _paused(n1)

    resumed = pw.phase_resume(n1.layout)

    assert resumed["outcome"] == "returned", (resumed.get("error_type"), resumed.get("message"))
    assert resumed["status"] == "paused" and resumed["has_pause_snapshot"] is True, resumed
    assert resumed["ref"] != resumed["before_ref"]  # the next gate journaled a new root record
    assert n1.tools() == {"witness.a": 1, "witness.b": 3}
    assert n1.webhook_keys() == [pw.KEY_A, pw.KEY_C]


def test_a_direct_child_handle_is_refused_before_any_effect(n1: Scenario) -> None:
    _paused(n1)

    direct = pw.phase_resume_child_handle(n1.layout)

    assert direct["outcome"] == "raised", direct
    assert direct["error_type"].endswith(".ResumeDirectChildHandleError")
    assert n1.tools() == {"witness.b": 3}
    assert n1.webhook_keys() == [pw.KEY_A]
