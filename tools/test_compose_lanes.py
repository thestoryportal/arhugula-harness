"""C-HE-11 §1: per-lane Compose project name + host-port block (U-HE-31).

Three witnesses at three costs. The formula and the compose wiring are pure text/data and
run everywhere; the two-lanes-up proof needs a Docker daemon and is skip-marked with the
one legal reason (`docker-daemon-absent`, spec §8.1). The daemon-gated case is the only
one that can actually prove "no port bind conflict" — the formula test proves the numbers
are disjoint, which is a different claim from two real stacks coexisting.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import lane_ports

REPO = Path(__file__).resolve().parent.parent
COMPOSE = REPO / "deploy" / "self-hosted-local" / "compose.yaml"


def test_lane_port_formula() -> None:
    assert lane_ports.ports(0) == {
        "grafana": 3000,
        "tempo": 3200,
        "otel_grpc": 4317,
        "otel_http": 4318,
    }
    assert lane_ports.ports(1) == {
        "grafana": 30100,
        "tempo": 30101,
        "otel_grpc": 30102,
        "otel_http": 30103,
    }
    # The `base + 100*k` form that was rejected: grafana 3000 + 200 would be lane 0's tempo.
    assert lane_ports.ports(2)["grafana"] == 30200
    assert lane_ports.ports(2)["tempo"] != lane_ports.ports(0)["tempo"]
    with pytest.raises(ValueError):
        lane_ports.ports(350)
    with pytest.raises(ValueError):
        lane_ports.ports(-1)
    assert lane_ports.project(0) == "arhugula-r420-self-hosted-local"
    assert lane_ports.project(3) == "arhugula-r420-self-hosted-local-lane3"


def test_every_lane_pair_is_port_disjoint() -> None:
    """Disjointness is the property; the formula is only how it is obtained."""
    seen: dict[int, int] = {}
    for k in range(0, 350):
        for port in lane_ports.ports(k).values():
            assert port not in seen, f"lane {k} reuses port {port} from lane {seen[port]}"
            seen[port] = k
        assert max(lane_ports.ports(k).values()) < 65536


def test_lane_index_rejects_a_non_numeric_value() -> None:
    """A silent fallback to 0 would put a second lane on lane 0's ports and project."""
    assert lane_ports.lane_index({"HARNESS_LANE_INDEX": "4"}) == 4
    assert lane_ports.lane_index({}) == 0
    assert lane_ports.lane_index({"HARNESS_LANE_INDEX": ""}) == 0
    with pytest.raises(ValueError):
        lane_ports.lane_index({"HARNESS_LANE_INDEX": "lane-two"})


def test_compose_uses_port_variables() -> None:
    text = COMPOSE.read_text(encoding="utf-8")
    for var in (
        "R420_PORT_GRAFANA",
        "R420_PORT_TEMPO",
        "R420_PORT_OTEL_GRPC",
        "R420_PORT_OTEL_HTTP",
    ):
        assert var in text, f"{var} not parameterized in compose.yaml"
    # Lane 0 must be unchanged for an operator who never sets HARNESS_LANE_INDEX.
    for default in (
        "${R420_PORT_GRAFANA:-3000}",
        "${R420_PORT_TEMPO:-3200}",
        "${R420_PORT_OTEL_GRPC:-4317}",
        "${R420_PORT_OTEL_HTTP:-4318}",
    ):
        assert default in text, f"missing lane-0 default {default}"


def test_shell_mode_emits_project_and_every_port() -> None:
    out = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lane_ports.py"), "--shell"],
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, "HARNESS_LANE_INDEX": "2"},
    ).stdout
    assert "export R420_PROJECT=arhugula-r420-self-hosted-local-lane2" in out
    assert "export R420_PORT_GRAFANA=30200" in out
    assert "export R420_PORT_OTEL_HTTP=30203" in out
    proj = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lane_ports.py"), "--project"],
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, "HARNESS_LANE_INDEX": "2"},
    ).stdout.strip()
    assert proj == "arhugula-r420-self-hosted-local-lane2"


def test_stack_recipes_pass_a_per_lane_project() -> None:
    """A recipe that omits `-p` silently reuses compose.yaml's fixed top-level name."""
    justfile = (REPO / "justfile").read_text(encoding="utf-8")
    for recipe in (
        "r420-self-hosted-stack-up",
        "r420-self-hosted-stack-down",
        "r420-self-hosted-stack-status",
    ):
        start = justfile.index(f"\n{recipe}:")
        body = justfile[start + 1 : justfile.index("\n\n", start)]
        # The ARGUMENT, not merely the name: `R420_PROJECT` also appears in the
        # lane_ports export/eval setup, so grepping the bare name leaves this gate green
        # with the `-p` dropped — every lane back on Compose's fixed project name.
        assert '-p "$R420_PROJECT"' in body, f'{recipe} does not pass -p "$R420_PROJECT"'


@pytest.mark.skipif(
    shutil.which("docker") is None
    or subprocess.run(["docker", "info"], capture_output=True).returncode != 0,
    reason="docker-daemon-absent",
)
def test_two_lanes_disjoint_names_and_ports() -> None:
    # Never the low indices: this case brings stacks UP and tears them DOWN by project name,
    # so on a machine where a real lane 1 or 2 is live it would reap that operator's stack.
    # 348/349 sit at the very top of the k<350 range and lane-init allocates upward from 0.
    # That makes collision implausible, not impossible — so the projects are also checked to
    # be ABSENT first, and only the stacks this test actually started are torn down. A
    # pre-existing stack under either name fails the test loudly instead of being adopted.
    # RESIDUAL, named rather than argued away: the absence check is not atomic with `up`, so
    # a real lane starting at 348/349 in that window would still be adopted. Closing it would
    # mean taking registry claims in the operator's live queue from a test process — a worse
    # trade for a window that requires 348 concurrent lanes to have been allocated first.
    a, b = 348, 349
    env = {**os.environ, "HARNESS_RAM_FLOOR_GB": "0"}  # the RAM guard is not under test here

    def up(k: int) -> None:
        subprocess.run(
            ["just", "r420-self-hosted-stack-up"],
            env={**env, "HARNESS_LANE_INDEX": str(k)},
            check=True,
            capture_output=True,
            text=True,
            timeout=600,
            cwd=REPO,
        )

    def down(k: int) -> int:
        return subprocess.run(
            ["just", "r420-self-hosted-stack-down"],
            env={**env, "HARNESS_LANE_INDEX": str(k)},
            capture_output=True,
            text=True,
            timeout=300,
            cwd=REPO,
        ).returncode

    def ps(k: int) -> list[dict]:
        out = subprocess.run(
            [
                "docker",
                "compose",
                "-p",
                lane_ports.project(k),
                "-f",
                str(COMPOSE),
                "ps",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            check=True,
            cwd=REPO,
        ).stdout
        return [json.loads(line) for line in out.splitlines() if line.strip()]

    for k in (a, b):
        assert not ps(k), (
            f"a stack already exists under {lane_ports.project(k)} — refusing to adopt or "
            f"tear down a project this test did not create"
        )

    started: list[int] = []
    try:
        up(a)
        started.append(a)
        up(b)
        started.append(b)
        c1, c2 = ps(a), ps(b)
        assert len(c1) == 3 and len(c2) == 3, (c1, c2)
        assert {c["Name"] for c in c1}.isdisjoint({c["Name"] for c in c2})
        assert all(c["State"] == "running" for c in c1 + c2), "port bind conflict"
        p1, p2 = lane_ports.ports(a), lane_ports.ports(b)
        pub1 = " ".join(str(c.get("Publishers", "")) for c in c1)
        pub2 = " ".join(str(c.get("Publishers", "")) for c in c2)
        assert str(p1["grafana"]) in pub1
        assert str(p2["grafana"]) in pub2
        assert str(p2["grafana"]) not in pub1
        vols = subprocess.run(
            ["docker", "volume", "ls", "--format", "{{.Name}}"],
            capture_output=True,
            text=True,
        ).stdout
        assert f"{lane_ports.project(a)}_grafana-data" in vols
        assert f"{lane_ports.project(b)}_grafana-data" in vols
    finally:
        # A swallowed cleanup failure leaves lane348/lane349 containers running and the test
        # green — the next run of this same case then trips its own absence check, or a real
        # lane inherits them. Reported unless a real failure is already propagating.
        failed = [k for k in started if down(k) != 0]
        if failed and sys.exc_info()[0] is None:
            raise AssertionError(
                f"stack-down failed for lane(s) {failed}; containers may still be running"
            )
