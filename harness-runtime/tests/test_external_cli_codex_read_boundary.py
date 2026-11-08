"""Runtime v1.135: every real Codex spawn runs through the read-boundary launcher.

Construction without a boundary refuses (the default optional entry degrades), both the
auth check and inference are wrapped, unsafe homes are refused before any process, the
child gets only an allow-listed environment and a private scratch under the configured
root, a launcher refusal is a typed error, and cancellation still settles the group.

The real end-to-end cases launch THIS test interpreter as the pinned "codex" with
test-only read allowances for its own runtime, running owned bounded `-c` programs;
no real Codex, login, credential or model is touched.
"""

from __future__ import annotations

import asyncio
import contextlib
import ctypes
import hashlib
import json
import os
import signal
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from harness_runtime.lifecycle import cli_read_boundary as boundary
from harness_runtime.lifecycle import external_cli_provider as provider
from harness_runtime.lifecycle.external_cli_provider import (
    CLIProcessResult,
    ExternalCLICommandError,
    ExternalCLIProcessTimeout,
    ExternalCLIReadBoundaryError,
    construct_codex_cli_adapter,
)
from harness_runtime.types import (
    CodexReadBoundaryConfig,
    ExternalCLIProviderConfig,
    ExternalCLIProviderKind,
)

from .test_cli_read_boundary import HOST_REFUSAL, SUPPORTED_HOST, UNSUPPORTED_HOST

INTERPRETER = Path(os.path.realpath(sys.executable))
TEST_RUNTIME_READ_ONLY = (
    Path(sys.base_prefix).resolve(),
    Path("/usr/lib"),
    Path("/etc/ld.so.cache"),
)
# The test interpreter is dynamically linked; the kernel must EXECUTE its ELF loader.
_LOADER = (
    "/lib/ld-linux-aarch64.so.1"
    if os.path.exists("/lib/ld-linux-aarch64.so.1")
    else ("/lib64/ld-linux-x86-64.so.2")
)
TEST_RUNTIME_EXECUTABLE = (Path(os.path.realpath(_LOADER)),)


@pytest.fixture(autouse=True)
def _simulated_operator(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A fake operator HOME: the runner derives its protected/sealed roots from it, so no
    case ever names (or stats) the real operator HOME or ``~/.codex``."""
    operator = tmp_path / "operator-home"
    (operator / ".codex").mkdir(parents=True, mode=0o700)
    (operator / ".codex" / "history.jsonl").write_text("fixture history")
    monkeypatch.setenv("HOME", str(operator))
    monkeypatch.delenv("CODEX_HOME", raising=False)
    return operator


def _homes(tmp_path: Path, *, auth: bool = True) -> tuple[Path, Path]:
    home, scratch = tmp_path / "harness-codex-home", tmp_path / "scratch-root"
    home.mkdir(mode=0o700)
    scratch.mkdir(mode=0o700)
    if auth:
        (home / "auth.json").write_text("{}")  # a fixture, never a real credential
    return home, scratch


def _boundary(home: Path, scratch: Path, **overrides: Any) -> CodexReadBoundaryConfig:
    fields: dict[str, Any] = {
        "executable": INTERPRETER,
        "executable_sha256": hashlib.sha256(INTERPRETER.read_bytes()).hexdigest(),
        "codex_home": home,
        "scratch_root": scratch,
        "read_only_paths": TEST_RUNTIME_READ_ONLY,
        "executable_paths": TEST_RUNTIME_EXECUTABLE,
    }
    fields.update(overrides)
    return CodexReadBoundaryConfig(**fields)


def _config(read_boundary: CodexReadBoundaryConfig | None, **kw: Any) -> ExternalCLIProviderConfig:
    return ExternalCLIProviderConfig(
        provider="codex",
        kind=ExternalCLIProviderKind.CODEX,
        command="codex",
        read_boundary=read_boundary,
        **kw,
    )


# --- no boundary, no Codex process ------------------------------------------------------


@pytest.mark.parametrize("auth_check", [True, False])
async def test_an_unconfigured_codex_refuses_to_construct(auth_check: bool) -> None:
    with pytest.raises(ExternalCLIReadBoundaryError, match="read_boundary"):
        await construct_codex_cli_adapter(_config(None, auth_check=auth_check))


def test_the_refusal_is_a_command_error_so_the_optional_default_degrades() -> None:
    assert issubclass(ExternalCLIReadBoundaryError, ExternalCLICommandError)
    from harness_runtime.types import DEFAULT_EXTERNAL_CLI_PROVIDERS

    [codex] = [p for p in DEFAULT_EXTERNAL_CLI_PROVIDERS if p.kind is ExternalCLIProviderKind.CODEX]
    assert codex.optional is True and codex.read_boundary is None


def test_a_boundary_is_codex_only() -> None:
    with pytest.raises(ValueError, match="codex"):
        ExternalCLIProviderConfig(
            provider="claude_code",
            kind=ExternalCLIProviderKind.CLAUDE_CODE,
            read_boundary=CodexReadBoundaryConfig(
                executable=Path("/opt/codex"),
                executable_sha256="a" * 64,
                codex_home=Path("/var/lib/h/codex"),
                scratch_root=Path("/var/lib/h/scratch"),
            ),
        )


@pytest.mark.parametrize(
    "field,value",
    [("executable", Path("codex")), ("codex_home", Path("rel")), ("executable_sha256", "XYZ")],
)
def test_the_boundary_config_rejects_relative_paths_and_bad_pins(field: str, value: Any) -> None:
    base: dict[str, Any] = {
        "executable": Path("/opt/codex"),
        "executable_sha256": "a" * 64,
        "codex_home": Path("/var/lib/h/codex"),
        "scratch_root": Path("/var/lib/h/scratch"),
    }
    base[field] = value
    with pytest.raises(ValueError):
        CodexReadBoundaryConfig(**base)


# --- both real Codex processes are wrapped ------------------------------------------------


async def test_auth_and_inference_both_run_through_the_launcher(tmp_path: Path) -> None:
    home, scratch = _homes(tmp_path)
    adapter = await construct_codex_cli_adapter(_config(_boundary(home, scratch), auth_check=False))
    runner = adapter.runner
    assert isinstance(runner, provider._CodexReadBoundaryRunner)

    for tail in (provider._codex_auth_argv("codex"), provider._codex_inference_argv("codex", "m")):
        token = boundary.new_refusal_token()
        argv = runner.launcher_argv(tail, scratch=scratch / "call", refusal_token=token)
        assert argv[:3] == (os.path.realpath(sys.executable), "-I", "-S")
        assert argv[3] == str(boundary.LAUNCHER_PATH)
        spec = boundary.RulesetSpec.from_json(argv[4])
        assert spec.executable == str(INTERPRETER) and spec.refusal_token == token
        assert all(token not in arg for arg in argv[5:])  # the target never receives it
        assert str(home) in spec.read_write_dirs and str(scratch / "call") in spec.read_write_dirs
        assert argv[5] == "--" and argv[6] == str(INTERPRETER) and argv[7:] == tail[1:]


# --- pre-spawn refusals --------------------------------------------------------------------


async def _run_once(runner: Any) -> CLIProcessResult:
    return await runner.run(("codex", "-c", "print('ran')"), stdin="", timeout_seconds=30)


@pytest.mark.parametrize("defect", ["missing-auth", "loose-mode", "symlinked-home", "missing-root"])
async def test_an_unsafe_home_is_refused_before_any_process(tmp_path: Path, defect: str) -> None:
    home, scratch = _homes(tmp_path, auth=defect != "missing-auth")
    if defect == "loose-mode":
        home.chmod(0o755)
    if defect == "symlinked-home":
        link = tmp_path / "home-link"
        link.symlink_to(home)
        home = link
    if defect == "missing-root":
        scratch = tmp_path / "absent"
    runner = provider._CodexReadBoundaryRunner(_boundary(home, scratch))
    with pytest.raises(ExternalCLIReadBoundaryError):
        await _run_once(runner)


@SUPPORTED_HOST
@pytest.mark.parametrize(
    "alias", ["dot-codex", "inside-dot-codex", "operator-codex-home-env", "dot-codex-other-env"]
)
async def test_the_operator_interactive_codex_home_is_not_a_dedicated_home(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, _simulated_operator: Path, alias: str
) -> None:
    """Review P2-2: a private 0700 ``.codex`` with ``auth.json`` is still the operator's.

    PR1688 P2: an inherited ``CODEX_HOME`` naming another directory seals that residence
    too; it never unseals ``~/.codex``."""
    _, scratch = _homes(tmp_path)
    residence = _simulated_operator / ".codex"
    if alias == "inside-dot-codex":
        residence = residence / "harness"
        residence.mkdir(mode=0o700)
    if alias == "operator-codex-home-env":
        residence = tmp_path / "operator-chosen-codex"
        residence.mkdir(mode=0o700)
        monkeypatch.setenv("CODEX_HOME", str(residence))
    if alias == "dot-codex-other-env":
        elsewhere = tmp_path / "operator-chosen-codex"
        elsewhere.mkdir(mode=0o700)
        monkeypatch.setenv("CODEX_HOME", str(elsewhere))
    (residence / "auth.json").write_text("{}")  # fixture text only
    runner = provider._CodexReadBoundaryRunner(_boundary(residence, scratch))
    program = "import os, sys; os.close(os.open(sys.argv[1], os.O_RDONLY)); print('read')"
    target = str(_simulated_operator / ".codex" / "history.jsonl")
    with pytest.raises(ExternalCLIReadBoundaryError, match="sealed"):
        await runner.run(("codex", "-I", "-S", "-c", program, target), stdin="", timeout_seconds=30)


def test_a_named_codex_provider_cannot_select_another_kind() -> None:
    """Review P2-4: provider identity and adapter kind cannot disagree in a config."""
    entry = {
        "provider": "codex",
        "kind": "generic-command",
        "command": "codex",
        "auth_check": False,
    }
    with pytest.raises(ValueError, match="codex"):
        ExternalCLIProviderConfig.model_validate(entry)


@pytest.mark.parametrize("optional", [True, False])
async def test_default_construction_of_the_named_codex_never_runs_unconfined(
    tmp_path: Path, optional: bool
) -> None:
    """The real stage-3a default constructor: no boundary means degrade or raise, never run."""
    import warnings

    from harness_core.deployment_surface import DeploymentSurface
    from harness_cp.topology_pattern import TopologyPattern
    from harness_runtime.config.provider_secrets import make_keyring_resolver
    from harness_runtime.lifecycle.providers import (
        ProviderTransientError,
        materialize_provider_clients_stage,
    )
    from harness_runtime.types import (
        CollectorConfig,
        OTelConfig,
        PathBindingConfig,
        ProviderSecretsConfig,
        RuntimeConfig,
    )

    config = RuntimeConfig(
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        repository_root=tmp_path,
        path_bindings=PathBindingConfig(),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4317"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        enabled_provider_names=("codex", "ollama"),
        external_cli_providers=(_config(None, auth_check=False, optional=optional),),
    )

    async def ollama() -> Any:
        return object()

    resolver = make_keyring_resolver(ProviderSecretsConfig())
    if optional:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            stage = await materialize_provider_clients_stage(
                config, resolver, ollama_construct=ollama, max_attempts=1
            )
        assert "codex" not in stage.providers
        assert any("read_boundary" in str(w.message) for w in caught)
    else:
        with pytest.raises(ProviderTransientError, match="read_boundary"):
            await materialize_provider_clients_stage(
                config, resolver, ollama_construct=ollama, max_attempts=1
            )


# --- real launch: environment, scratch, refusal mapping, cancellation ---------------------


ENV_PROBE = "import json, os; print(json.dumps({'env': dict(os.environ), 'cwd': os.getcwd()}))"


@SUPPORTED_HOST
async def test_the_child_gets_only_the_allow_listed_environment_and_private_scratch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ARHUGULA_DUMMY_SECRET", "dummy-not-a-credential")
    home, scratch = _homes(tmp_path)
    runner = provider._CodexReadBoundaryRunner(_boundary(home, scratch))

    result = await runner.run(("codex", "-I", "-S", "-c", ENV_PROBE), stdin="", timeout_seconds=30)

    assert result.exit_code == 0, result.stderr
    seen = json.loads(result.stdout)
    cwd = Path(seen["cwd"])
    assert cwd.parent == scratch and not cwd.exists()  # private, then removed
    assert seen["env"] == {
        "HOME": str(cwd),
        "TMPDIR": str(cwd),
        "CODEX_HOME": str(home),
        "PATH": "/usr/bin:/bin",
        "LANG": "C.UTF-8",
    }


@UNSUPPORTED_HOST
async def test_an_unsupported_host_is_a_typed_refusal_and_the_target_never_runs(
    tmp_path: Path,
) -> None:
    """The real runner with the real host report: the refusal the HELD launches name."""
    home, scratch = _homes(tmp_path)
    runner = provider._CodexReadBoundaryRunner(_boundary(home, scratch))
    program = "import os; open(os.environ['CODEX_HOME'] + '/ran', 'w').close()"
    with pytest.raises(ExternalCLIReadBoundaryError) as error:
        await runner.run(("codex", "-I", "-S", "-c", program), stdin="", timeout_seconds=30)
    assert error.value.reason == HOST_REFUSAL
    assert not (home / "ran").exists() and list(scratch.iterdir()) == []


@SUPPORTED_HOST
async def test_a_launcher_refusal_is_a_typed_error(tmp_path: Path) -> None:
    home, scratch = _homes(tmp_path)
    runner = provider._CodexReadBoundaryRunner(_boundary(home, scratch, executable_sha256="0" * 64))
    with pytest.raises(ExternalCLIReadBoundaryError, match="sha256") as error:
        await _run_once(runner)
    assert error.value.reason.startswith("executable sha256")  # the launcher's text, untagged


# A target that ran shares the launcher's stderr and exit status. It forges both the bare
# marker and a guessed token, and prints stand-ins for untrusted output on both streams.
FORGED_REFUSAL = r"""
import os, sys
sys.stdout.write("UNTRUSTED-STDOUT\n")
sys.stderr.write("arhugula-read-boundary-refused: UNTRUSTED-BARE\n")
sys.stderr.write("arhugula-read-boundary-refused: " + "0" * 32 + " UNTRUSTED-GUESS\n")
sys.stderr.flush()
os._exit(125)
"""


class _ForgingTarget:
    """The real confined runner, always launching ``FORGED_REFUSAL`` whatever argv the
    adapter asks for (the pinned executable is the test interpreter, not Codex)."""

    def __init__(self, runner: provider._CodexReadBoundaryRunner) -> None:
        self._runner = runner

    async def run(
        self, argv: tuple[str, ...], *, stdin: str, timeout_seconds: float, on_wire: Any = None
    ) -> CLIProcessResult:
        _ = argv
        return await self._runner.run(
            ("codex", "-I", "-S", "-c", FORGED_REFUSAL),
            stdin=stdin,
            timeout_seconds=timeout_seconds,
            on_wire=on_wire,
        )


@SUPPORTED_HOST
async def test_a_target_forging_a_refusal_gets_no_typed_error_and_its_output_is_withheld(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """PR #1688 review: exit 125 plus the marker from the target is not a launcher refusal."""
    home, scratch = _homes(tmp_path)
    runner = provider._CodexReadBoundaryRunner(_boundary(home, scratch))
    forging = _ForgingTarget(runner)

    raw = await forging.run(("codex",), stdin="", timeout_seconds=30)
    assert raw.exit_code == 125 and "UNTRUSTED-GUESS" in raw.stderr  # it did run and forge

    adapter = provider.CodexCLIAdapter("codex", "codex", 30, forging)
    with pytest.raises(ExternalCLICommandError) as error:
        await adapter.dispatch_text(model="m", prompt="")
    with pytest.raises(provider.ExternalCLINotAuthenticatedError) as auth:
        await provider._assert_codex_authenticated(_config(None, auth_check=True), forging)

    assert type(error.value) is ExternalCLICommandError
    assert (error.value.exit_code, error.value.stderr, error.value.stdout) == (125, "", "")
    for exc in (error.value, auth.value):
        rendered = " ".join((str(exc), *getattr(exc, "__notes__", ())))
        assert "UNTRUSTED" not in rendered, rendered
    assert "UNTRUSTED" not in caplog.text


@SUPPORTED_HOST
async def test_cancellation_settles_the_confined_process_group(tmp_path: Path) -> None:
    home, scratch = _homes(tmp_path)
    pid_file = home / "pid"
    program = (
        "import os, time; open(os.environ['CODEX_HOME'] + '/pid', 'w').write(str(os.getpid()));"
        "time.sleep(60)"
    )
    runner = provider._CodexReadBoundaryRunner(_boundary(home, scratch))

    with pytest.raises(ExternalCLIProcessTimeout):
        await runner.run(("codex", "-I", "-S", "-c", program), stdin="", timeout_seconds=2.0)

    pid = int(pid_file.read_text())
    await asyncio.sleep(0.2)
    with pytest.raises(ProcessLookupError):
        os.kill(pid, 0)


# The confined leader forks a member that leaves the output pipes, records its pid and
# group in CODEX_HOME and keeps writing into its scratch HOME. The leader exits (success,
# or a forged refusal: exit 125 with the bare marker) or blocks (cancellation) only once
# that member exists, so the member outlives the leader.
OUTLIVING_MEMBER = r"""
import os, sys, time
home = os.environ["CODEX_HOME"]
if os.fork() == 0:
    null = os.open("/dev/null", os.O_RDWR)
    for fd in (0, 1, 2):
        os.dup2(null, fd)
    with open(os.environ["HOME"] + "/beat", "w") as fh:
        fh.write("x")
    with open(home + "/member.tmp", "w") as fh:
        fh.write(f"{os.getpid()} {os.getpgrp()}")
    os.rename(home + "/member.tmp", home + "/member")
    while True:
        try:
            with open(os.environ["HOME"] + "/beat", "w") as fh:
                fh.write("x")
        except OSError:
            pass
        time.sleep(0.01)
while not os.path.exists(home + "/member"):
    time.sleep(0.01)
outcome = sys.argv[1]
if outcome == "forged":
    sys.stderr.write("arhugula-read-boundary-refused: fixture refusal\n")
    sys.stderr.flush()
    os._exit(125)
if outcome == "cancel":
    time.sleep(60)
"""


@SUPPORTED_HOST
@pytest.mark.parametrize("outcome", ["success", "forged", "cancel"])
async def test_scratch_is_removed_only_after_an_outliving_group_member_settles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, outcome: str
) -> None:
    """Items 4 and 8: removal waits for the whole group, not only the reaped leader."""
    home, scratch = _homes(tmp_path)
    member_file = home / "member"
    removals: list[dict[str, Any]] = []
    real_rmtree = provider.shutil.rmtree

    def observed_rmtree(path: str) -> None:
        member, group = (int(n) for n in member_file.read_text().split())
        removals.append(
            {
                "scratch": Path(path).parent == scratch and (Path(path) / "beat").exists(),
                "member_alive": _exists(lambda: os.kill(member, 0)),
                "group_alive": _exists(lambda: os.kill(-group, 0)),
                "leader_group": group != os.getpgrp(),
            }
        )
        real_rmtree(path)

    monkeypatch.setattr(provider.shutil, "rmtree", observed_rmtree)
    runner = provider._CodexReadBoundaryRunner(_boundary(home, scratch))
    run = runner.run(
        ("codex", "-I", "-S", "-c", OUTLIVING_MEMBER, outcome), stdin="", timeout_seconds=30
    )

    async with asyncio.timeout(20):
        if outcome != "cancel":
            # A target that ran never yields the typed refusal, even when it forges one.
            result = await run
            assert result.exit_code == {"success": 0, "forged": 125}[outcome], result.stderr
        else:
            task = asyncio.create_task(run)
            while not member_file.exists():
                await asyncio.sleep(0.01)
            task.cancel("caller cancelled")
            with pytest.raises(asyncio.CancelledError, match="caller cancelled"):
                await task

    assert removals == [
        {"scratch": True, "member_alive": False, "group_alive": False, "leader_group": True}
    ]
    assert list(scratch.iterdir()) == []


def _exists(probe: Any) -> bool:
    try:
        probe()
    except ProcessLookupError:
        return False
    return True


_PR_SET_CHILD_SUBREAPER = 36


@pytest.fixture
def held_orphans() -> Iterator[list[int]]:
    """Make this test process the child subreaper. A group member killed with or after its
    leader then stays a zombie inside the group until the test reaps it, so the member
    outlives the leader on every exit path. Listed pids are killed and reaped on exit."""
    libc = ctypes.CDLL(None, use_errno=True)
    assert libc.prctl(_PR_SET_CHILD_SUBREAPER, 1, 0, 0, 0) == 0
    held: list[int] = []
    try:
        yield held
    finally:
        for pid in held:
            with contextlib.suppress(ProcessLookupError):
                os.kill(pid, signal.SIGKILL)
            with contextlib.suppress(ChildProcessError):
                os.waitpid(pid, 0)
        assert libc.prctl(_PR_SET_CHILD_SUBREAPER, 0, 0, 0, 0) == 0


def _zombie(pid: int) -> bool:
    return Path(f"/proc/{pid}/stat").read_text().rpartition(")")[2].split()[0] == "Z"


def _reap_zombie(pid: int) -> bool:
    """Reap ``pid`` without blocking; True only if it had already exited."""
    return os.waitpid(pid, os.WNOHANG)[0] == pid


@SUPPORTED_HOST
@pytest.mark.parametrize("outcome", ["success", "forged", "cancel"])
async def test_scratch_is_kept_and_reported_when_the_group_does_not_settle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    held_orphans: list[int],
    outcome: str,
) -> None:
    """Items 4 and 8 past the bounded wait: a group still present keeps its scratch, and
    the outcome and log say which directory was kept."""
    home, scratch = _homes(tmp_path)
    member_file = home / "member"
    monkeypatch.setattr(provider, "_CLEANUP_WAIT_SECONDS", 0.3)
    removed: list[str] = []
    monkeypatch.setattr(provider.shutil, "rmtree", removed.append)
    runner = provider._CodexReadBoundaryRunner(_boundary(home, scratch))
    run = runner.run(
        ("codex", "-I", "-S", "-c", OUTLIVING_MEMBER, outcome), stdin="", timeout_seconds=30
    )

    caught: BaseException | None = None
    async with asyncio.timeout(20):
        if outcome != "cancel":
            assert (await run).exit_code == {"success": 0, "forged": 125}[outcome]
        else:
            task = asyncio.create_task(run)
            while not member_file.exists():
                await asyncio.sleep(0.01)
            task.cancel("caller cancelled")
            with pytest.raises(asyncio.CancelledError, match="caller cancelled") as cancel:
                await task
            caught = cancel.value

    member, group = (int(n) for n in member_file.read_text().split())
    held_orphans.append(member)
    # The leader is reaped; its killed member still holds the group past the deadline.
    assert not _exists(lambda: os.kill(group, 0))
    assert _zombie(member) and _exists(lambda: os.kill(-group, 0))
    (cwd,) = scratch.iterdir()
    assert removed == [] and (cwd / "beat").exists()
    retained = f"{provider._SCRATCH_RETAINED}: {cwd}"
    assert retained in caplog.text and provider._CLEANUP_UNCERTAIN in caplog.text
    if caught is not None:
        assert retained in caught.__notes__


@SUPPORTED_HOST
async def test_cancellation_removes_scratch_only_after_an_outliving_member_settles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, held_orphans: list[int]
) -> None:
    """Item 4 on cancellation: the leader is reaped while its member still holds the group,
    and the scratch goes only once that member is gone."""
    home, scratch = _homes(tmp_path)
    member_file = home / "member"
    events: list[str] = []
    real_rmtree = provider.shutil.rmtree

    def observed_rmtree(path: str) -> None:
        events.append("removed-under-group" if _exists(lambda: os.kill(-group, 0)) else "removed")
        real_rmtree(path)

    monkeypatch.setattr(provider.shutil, "rmtree", observed_rmtree)
    runner = provider._CodexReadBoundaryRunner(_boundary(home, scratch))
    task = asyncio.create_task(
        runner.run(
            ("codex", "-I", "-S", "-c", OUTLIVING_MEMBER, "cancel"), stdin="", timeout_seconds=30
        )
    )
    async with asyncio.timeout(20):
        while not member_file.exists():
            await asyncio.sleep(0.01)
        member, group = (int(n) for n in member_file.read_text().split())
        held_orphans.append(member)
        task.cancel("caller cancelled")
        while _exists(lambda: os.kill(group, 0)) or not _zombie(member):
            await asyncio.sleep(0.01)
        events.append("leader-reaped")
        assert not task.done()
        assert _reap_zombie(member)
        events.append("member-reaped")
        with pytest.raises(asyncio.CancelledError, match="caller cancelled"):
            await task

    assert events == ["leader-reaped", "member-reaped", "removed"]
    assert list(scratch.iterdir()) == []


OPERATOR_TOML = """
[[runtime.external_cli_providers]]
provider = "codex"
kind = "codex"
command = "codex"
optional = false

[runtime.external_cli_providers.read_boundary]
executable = "/home/operator/.local/share/mise/installs/codex/0.159.2/bin/codex"
executable_sha256 = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
codex_home = "/home/operator/.local/state/arhugula/codex-home"
scratch_root = "/home/operator/.local/state/arhugula/codex-scratch"
"""


def test_the_documented_operator_toml_parses_into_the_typed_boundary() -> None:
    """The exact snippet in docs/operations/omarchy-codex-read-boundary.md."""
    import tomllib

    [entry] = tomllib.loads(OPERATOR_TOML)["runtime"]["external_cli_providers"]
    config = ExternalCLIProviderConfig.model_validate(entry)
    assert config.read_boundary is not None
    assert config.read_boundary.executable == Path(
        "/home/operator/.local/share/mise/installs/codex/0.159.2/bin/codex"
    )
    assert config.read_boundary.read_only_paths[0] == Path("/etc/hosts")
