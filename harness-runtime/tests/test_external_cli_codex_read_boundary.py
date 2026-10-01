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
import hashlib
import json
import os
import sys
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
        argv = runner.launcher_argv(tail, scratch=scratch / "call")
        assert argv[:3] == (os.path.realpath(sys.executable), "-I", "-S")
        assert argv[3] == str(boundary.LAUNCHER_PATH)
        spec = boundary.RulesetSpec.from_json(argv[4])
        assert spec.executable == str(INTERPRETER)
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


@pytest.mark.parametrize("alias", ["dot-codex", "inside-dot-codex", "operator-codex-home-env"])
async def test_the_operator_interactive_codex_home_is_not_a_dedicated_home(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, _simulated_operator: Path, alias: str
) -> None:
    """Review P2-2: a private 0700 ``.codex`` with ``auth.json`` is still the operator's."""
    _, scratch = _homes(tmp_path)
    residence = _simulated_operator / ".codex"
    if alias == "inside-dot-codex":
        residence = residence / "harness"
        residence.mkdir(mode=0o700)
    if alias == "operator-codex-home-env":
        residence = tmp_path / "operator-chosen-codex"
        residence.mkdir(mode=0o700)
        monkeypatch.setenv("CODEX_HOME", str(residence))
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


async def test_a_launcher_refusal_is_a_typed_error(tmp_path: Path) -> None:
    home, scratch = _homes(tmp_path)
    runner = provider._CodexReadBoundaryRunner(_boundary(home, scratch, executable_sha256="0" * 64))
    with pytest.raises(ExternalCLIReadBoundaryError, match="sha256"):
        await _run_once(runner)


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
