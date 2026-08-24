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
import tempfile
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


def production_queue_dir() -> Path:
    """The queue dir a REAL lane on this machine resolves — the PRODUCTION registry.

    Under a tools pytest session the ambient `ARC_METRICS_QUEUE_DIR` is the session
    belt (`tools/conftest.py`), so reading it here would claim lane indices in a
    throwaway registry and void the docker test's collision safety (codex round 13,
    P1). The belt preserves the demoted production value at
    `ARC_METRICS_QUEUE_DIR_PREBELT` (empty string = there was none, fall to the home
    default). This module's tests only run under pytest, so the ambient variable is
    never the right answer here.
    """
    return Path(
        os.environ.get("ARC_METRICS_QUEUE_DIR_PREBELT")
        or str(Path.home() / ".gstack/projects/arhugula-v2/arc-metrics-queue")
    )


def claim_production_lane_indices(indices: tuple[int, ...], owner: str) -> list[Path]:
    """Claim `indices` in the PRODUCTION lane registry, honoring its fences.

    [LAW:single-enforcer] This helper is the one place a test process resolves the
    registry it claims in, and it resolves through `production_queue_dir()` — never
    the ambient `ARC_METRICS_QUEUE_DIR`, which under a tools pytest session is the
    throwaway belt. A claim taken in the belt is invisible to real lanes, voiding
    exactly the collision safety the claim exists to provide (codex rounds 4-5 on
    the skills PR: the belt-vs-production choice had no non-skipped witness while
    the Docker consumer is deselected from codex-parity-check). All-or-nothing: on
    any refusal, every claim this call already took is released before raising.
    """
    lanes_dir = production_queue_dir() / "lanes"
    lanes_dir.mkdir(parents=True, exist_ok=True)
    # Honour the production registry's FENCES as well as its claims. A `.orphaned-<k>`
    # marker says that index was released without a verified-clean teardown, so
    # containers or volumes may survive under its project name — and `ps` cannot see a
    # volume-only remnant. Adopting a fenced index would delete exactly the state the
    # production registry has flagged as unaccounted for.
    for k in indices:
        fence = lanes_dir / f".orphaned-{k}"
        if fence.exists():
            raise AssertionError(
                f"lane index {k} is fenced ({fence}: {fence.read_text().strip()}) — refusing "
                f"to start or tear down a project whose prior stack is unaccounted for"
            )
    claimed: list[Path] = []
    for k in indices:
        claim = lanes_dir / str(k)
        # Published exactly as lane-init publishes one: a complete temp file linked into
        # place. `open(..., "x")` then write makes the claim visible EMPTY in between, and a
        # concurrent initializer reading it there treats it as an unowned corpse to repair.
        tmp = lanes_dir / f".claim.{owner}-{k}"
        tmp.write_text(f"{owner} {REPO}\n", encoding="utf-8")
        try:
            os.link(tmp, claim)
            tmp.unlink(missing_ok=True)
        except FileExistsError:
            tmp.unlink(missing_ok=True)
            for c in claimed:
                c.unlink(missing_ok=True)
            raise AssertionError(
                f"lane index {k} is already claimed ({claim.read_text().strip()}) — refusing "
                f"to run against a live lane's project"
            ) from None
        claimed.append(claim)
    return claimed


# mutation-probe(tools/test_compose_lanes.py): resolve lanes_dir from the ambient queue var
def test_lane_claims_land_in_the_production_registry_not_the_belt(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The Docker consumer's collision safety, witnessed without a daemon.

    Under a tools session the ambient queue variable is the throwaway belt; a claim
    taken there guards nothing. Reverting the helper to the ambient chain puts the
    claim under `belt/` and reds both assertions — the exact regression codex rounds
    4-5 found unwitnessed while the Docker test sits outside codex-parity-check.
    """
    production = tmp_path / "prod"
    belt = tmp_path / "belt"
    monkeypatch.setenv("ARC_METRICS_QUEUE_DIR_PREBELT", str(production))
    monkeypatch.setenv("ARC_METRICS_QUEUE_DIR", str(belt))
    claimed = claim_production_lane_indices((348,), "witness")
    assert claimed == [production / "lanes" / "348"]
    assert claimed[0].read_text(encoding="utf-8") == f"witness {REPO}\n"
    assert not (belt / "lanes").exists(), "the ambient (belt) registry must never be consulted"


# mutation-probe(tools/test_compose_lanes.py): drop the fence check from the claim helper
def test_a_fenced_index_is_refused_and_nothing_is_claimed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    lanes = tmp_path / "prod" / "lanes"
    lanes.mkdir(parents=True)
    (lanes / ".orphaned-348").write_text("unverified teardown\n", encoding="utf-8")
    monkeypatch.setenv("ARC_METRICS_QUEUE_DIR_PREBELT", str(tmp_path / "prod"))
    with pytest.raises(AssertionError, match="fenced"):
        claim_production_lane_indices((348,), "witness")
    assert not (lanes / "348").exists()


# mutation-probe(tools/test_compose_lanes.py): drop the release loop in the FileExistsError arm
def test_a_taken_index_is_refused_and_earlier_claims_are_released(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """All-or-nothing: a partial claim set left behind blocks the next honest taker."""
    lanes = tmp_path / "prod" / "lanes"
    lanes.mkdir(parents=True)
    (lanes / "349").write_text("live-lane /elsewhere\n", encoding="utf-8")
    monkeypatch.setenv("ARC_METRICS_QUEUE_DIR_PREBELT", str(tmp_path / "prod"))
    with pytest.raises(AssertionError, match="already claimed"):
        claim_production_lane_indices((348, 349), "witness")
    assert not (lanes / "348").exists(), "the refused call must release the claim it took first"


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


def _docker_daemon_absent() -> bool:
    """Bounded: a wedged socket makes an unbounded `docker info` hang COLLECTION itself,
    before pytest can apply any skip — the whole run stalls with no output."""
    if shutil.which("docker") is None:
        return True
    try:
        return subprocess.run(["docker", "info"], capture_output=True, timeout=15).returncode != 0
    except (subprocess.TimeoutExpired, OSError):
        return True


@pytest.mark.skipif(_docker_daemon_absent(), reason="docker-daemon-absent")
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

    # Both recipe invocations run from REPO, and lane-init allows a worktree ONE claim — so
    # a shared registry would (correctly) refuse the second lane and the witness would fail
    # before starting its second stack. Each invocation therefore resolves its lane against
    # its own scratch registry; the real-registry claims taken above are the separate thing:
    # a reservation so no concurrent lane can take 348/349 while this runs.
    scratch = Path(tempfile.mkdtemp(prefix="compose-lanes-"))

    def _lane_env(k: int) -> dict[str, str]:
        return {
            **env,
            "HARNESS_LANE_INDEX": str(k),
            "ARC_METRICS_QUEUE_DIR": str(scratch / f"lane-{k}"),
        }

    def up(k: int) -> None:
        subprocess.run(
            ["just", "r420-self-hosted-stack-up"],
            env=_lane_env(k),
            check=True,
            capture_output=True,
            text=True,
            timeout=600,
            cwd=REPO,
        )

    def down(k: int) -> int:
        # Never raises: this runs from the finally block, where an exception would abort the
        # remaining teardown and the claim release — stranding exactly the lanes and stacks
        # this cleanup exists to remove, precisely when Docker is already wedged.
        try:
            return _down(k)
        except (subprocess.TimeoutExpired, OSError):
            return 1

    def _down(k: int) -> int:
        return subprocess.run(
            ["just", "r420-self-hosted-stack-down"],
            env=_lane_env(k),
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
        # Compose emits EITHER a JSON array or one object per line depending on version and
        # formatting; parsing only the line form fails on a compact array (each line is the
        # whole list) and on a pretty-printed one (each line is a fragment).
        text = out.strip()
        if not text:
            return []
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return [json.loads(line) for line in text.splitlines() if line.strip()]
        return parsed if isinstance(parsed, list) else [parsed]

    # CLAIM the two indices in the real registry, exactly as a lane does. The absence check
    # below is not atomic with `up` on its own — a concurrent lane could take 348 in the
    # window and then have its stack adopted and torn down here. Holding the claim closes
    # that window at the same primitive lane-init uses (exclusive create), and the claims
    # are released in the finally. The recipes below resolve their lane against a scratch
    # registry and so never consult the production registry's fences; the helper honours
    # them here, and its belt-vs-production resolution is pinned by the hermetic witnesses
    # beside it (this Docker consumer is deselected from codex-parity-check).
    claimed = claim_production_lane_indices((a, b), "test-compose-lanes")

    started: list[int] = []
    try:
        for k in (a, b):
            assert not ps(k), (
                f"a stack already exists under {lane_ports.project(k)} — refusing to adopt "
                f"or tear down a project this test did not create"
            )
        # Recorded BEFORE the call: a partially-created stack that then fails or times out
        # must still be torn down, and appending after `up` skips exactly that case while
        # the claim is released anyway.
        started.append(a)
        up(a)
        started.append(b)
        up(b)
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
        # The recipe's `down` deliberately keeps named volumes (an operator stopping their
        # own stack must not lose their dashboards). This test CREATED those volumes and
        # asserts on them, so it removes its own: leaving lane348/lane349 volumes behind
        # would feed stale traces to the next run, or to a real lane on those indices.
        for k in started:
            try:
                rc = subprocess.run(
                    [
                        "docker",
                        "compose",
                        "-p",
                        lane_ports.project(k),
                        "-f",
                        str(COMPOSE),
                        "down",
                        "--volumes",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=REPO,
                ).returncode
            except (subprocess.TimeoutExpired, OSError):
                rc = 1
            # A volume left behind feeds stale dashboards and traces to the next run of this
            # case, or to a real lane on that index — an ignored rc would pass regardless.
            if rc != 0 and k not in failed:
                failed.append(k)
        # Only for lanes that actually cleaned up. Releasing a claim whose containers or
        # volumes survive hands that index — and that state — to the next lane to take it.
        for k, c in zip((a, b), claimed, strict=False):
            if k in failed:
                continue
            c.unlink(missing_ok=True)
        shutil.rmtree(scratch, ignore_errors=True)
        if failed and sys.exc_info()[0] is None:
            raise AssertionError(
                f"stack-down failed for lane(s) {failed}; containers may still be running"
            )
