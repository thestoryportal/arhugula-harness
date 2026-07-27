"""U-MEM-24 live external CLI auth confirmations.

The runtime represents external CLI auth as explicit ``ExternalCliRoute``
carriers. These e2e tests bind real local CLI status probes to those carriers
without printing secrets or moving credential material.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shlex
import shutil
import subprocess
from pathlib import Path
from types import ModuleType

import pytest
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import FallbackChain, ProviderCandidate, ProviderFamily
from harness_cp.memory_access_mode import ExternalCliRoute
from harness_is.cli_profile import (
    CliImportPolicy,
    CliInstructionSource,
    CliInstructionSourceKind,
    CliProfileKind,
)
from harness_runtime.cli_profile_loading import CliProfileResolutionRequest, resolve_cli_profile
from harness_runtime.lifecycle.external_cli_provider import (
    ExternalCLINotAuthenticatedError,
    construct_antigravity_cli_adapter,
    construct_gemini_cli_adapter,
    construct_generic_command_cli_adapter,
)
from harness_runtime.types import ExternalCLIProviderConfig, ExternalCLIProviderKind

pytestmark = pytest.mark.e2e


def _instruction_source() -> CliInstructionSource:
    return CliInstructionSource(
        source_id="project-instructions",
        source_kind=CliInstructionSourceKind.PROJECT_INSTRUCTION,
        path="AGENTS.md",
        required=True,
    )


def _chain(provider: str, family: ProviderFamily) -> FallbackChain:
    return FallbackChain(
        primary=ProviderCandidate(provider=provider, model="external-cli", family=family),
        same_family=(),
        cross_family=(),
        terminal=None,
    )


def _resolve_authenticated_route(
    *,
    kind: CliProfileKind,
    provider: str,
    external_cli_kind: str,
    command_name: str,
    family: ProviderFamily,
) -> ExternalCliRoute:
    route = ExternalCliRoute(
        provider_name=provider,
        external_cli_kind=external_cli_kind,
        command_name=command_name,
        auth_check_passed=True,
        optional=False,
        degradation_allowed=False,
    )
    resolved = resolve_cli_profile(
        CliProfileResolutionRequest(
            model_binding=ModelBinding(provider=provider, model="external-cli"),
            fallback_chain=_chain(provider, family),
            profile_kind=kind,
            external_cli_route=route,
            instruction_sources=(_instruction_source(),),
            import_policy=CliImportPolicy.READ_ONLY,
        )
    )
    assert resolved.profile.kind is kind
    assert resolved.external_cli_route == route
    return route


def _run_status(
    argv: list[str], *, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        check=False,
        text=True,
        capture_output=True,
        timeout=20,
        env=env,
    )


def test_claude_code_cli_auth_confirms_claude_code_route() -> None:
    if shutil.which("claude") is None:
        pytest.skip("Claude Code CLI is not installed on PATH")

    result = _run_status(["claude", "auth", "status"])
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        if result.returncode != 0:
            pytest.fail(f"claude auth status failed: {result.stderr or result.stdout}")
        raise
    if payload.get("loggedIn") is not True:
        pytest.skip("Claude Code CLI session auth is not logged in for this execution boundary")

    route = _resolve_authenticated_route(
        kind=CliProfileKind.CLAUDE_CODE,
        provider="claude_code",
        external_cli_kind="claude-code",
        command_name="claude",
        family=ProviderFamily.ANTHROPIC,
    )
    assert route.route_ref == "claude-code:claude"


def test_codex_cli_auth_confirms_codex_route() -> None:
    if shutil.which("codex") is None:
        pytest.skip("Codex CLI is not installed on PATH")

    env = dict(os.environ)
    env.pop("OPENAI_API_KEY", None)
    result = _run_status(
        ["codex", "login", "status", "-c", "preferred_auth_method=chatgpt"],
        env=env,
    )
    if result.returncode != 0:
        pytest.fail(f"codex login status failed: {result.stderr or result.stdout}")
    if "ChatGPT" not in f"{result.stdout}\n{result.stderr}":
        pytest.skip("Codex CLI is not logged in through the ChatGPT subscription boundary")

    route = _resolve_authenticated_route(
        kind=CliProfileKind.CODEX,
        provider="codex",
        external_cli_kind="codex",
        command_name="codex",
        family=ProviderFamily.OPENAI,
    )
    assert route.route_ref == "codex:codex"


def _load_provider_preset_helper() -> ModuleType:
    helper_path = Path(__file__).resolve().parents[3] / "tools" / "external_cli_provider_config.py"
    spec = importlib.util.spec_from_file_location("external_cli_provider_config", helper_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


async def test_antigravity_cli_auth_confirms_antigravity_route() -> None:
    # The Antigravity executable is ``agy``; sourcing it from the single
    # declared preset authority keeps this gate from re-acquiring the
    # wrong-binary-name defect that previously reported it as uninstalled.
    command: str = _load_provider_preset_helper().PROVIDER_PRESETS["antigravity"].command
    if shutil.which(command) is None:
        pytest.skip(f"Antigravity CLI executable {command!r} is not installed on PATH")

    # Drive the real production auth probe (``agy models``, asserted as exit-0
    # with non-empty stdout) through the adapter constructor rather than a bare
    # subprocess, so the live gate binds the shipped code path.
    config = ExternalCLIProviderConfig(
        provider="antigravity",
        kind=ExternalCLIProviderKind.ANTIGRAVITY,
        command=command,
        auth_check=True,
        timeout_seconds=20.0,
    )
    try:
        adapter = await construct_antigravity_cli_adapter(config)
    except ExternalCLINotAuthenticatedError as exc:
        pytest.skip(f"Antigravity CLI session auth is not available: {exc}")
    await adapter.aclose()

    # ``command_name`` on the route is the CLI-profile provenance identity from
    # BUILT_IN_CLI_PROVIDER_BINDINGS ("antigravity"), a separate surface from the
    # executable name above ("agy"); route_ref is derived from that identity.
    route = _resolve_authenticated_route(
        kind=CliProfileKind.ANTIGRAVITY,
        provider="antigravity",
        external_cli_kind="antigravity",
        command_name="antigravity",
        family=ProviderFamily.GOOGLE,
    )
    assert route.route_ref == "antigravity:antigravity"


async def test_gemini_legacy_cli_auth_confirms_gemini_legacy_route() -> None:
    # The legacy Gemini CLI ships no status subcommand, so its declared auth
    # probe is a minimal free-tier prompt. Both the executable name and the
    # probe argv come from the single preset authority, so a wrong-binary or
    # wrong-probe defect cannot recur here either.
    preset = _load_provider_preset_helper().PROVIDER_PRESETS["gemini"]
    command: str = preset.command
    auth_args: tuple[str, ...] = preset.auth_args
    if shutil.which(command) is None:
        pytest.skip(f"legacy Gemini CLI executable {command!r} is not installed on PATH")

    # Drive the declared probe through the shipped constructor rather than a
    # bare subprocess, so the live gate binds the production code path.
    config = ExternalCLIProviderConfig(
        provider="gemini",
        kind=ExternalCLIProviderKind.GEMINI,
        command=command,
        auth_args=auth_args,
        auth_check=True,
        timeout_seconds=60.0,
    )
    try:
        adapter = await construct_gemini_cli_adapter(config)
    except ExternalCLINotAuthenticatedError as exc:
        pytest.skip(f"legacy Gemini CLI declared auth probe did not confirm a session: {exc}")
    await adapter.aclose()

    # ``provider_name`` on the route is the CLI-profile provenance identity
    # from BUILT_IN_CLI_PROVIDER_BINDINGS ("gemini_legacy"), a separate surface
    # from the external CLI kind ("gemini") that composes route_ref.
    route = _resolve_authenticated_route(
        kind=CliProfileKind.GEMINI_LEGACY,
        provider="gemini_legacy",
        external_cli_kind="gemini",
        command_name="gemini",
        family=ProviderFamily.GOOGLE,
    )
    assert route.route_ref == "gemini:gemini"


async def test_generic_command_cli_auth_confirms_operator_declared_route() -> None:
    command = os.getenv("U_MEM_24_GENERIC_COMMAND_AUTH_PROBE", "").strip()
    if not command:
        pytest.skip("U_MEM_24_GENERIC_COMMAND_AUTH_PROBE is not set")
    argv = shlex.split(command)
    executable = argv[0]
    if shutil.which(executable) is None:
        pytest.skip(f"generic auth probe executable {executable!r} is not installed on PATH")

    # Drive the operator-declared probe through the shipped constructor rather
    # than a bare subprocess, so the live gate binds the production auth path.
    # Unlike the absent-CLI skips above, a declared probe that fails to confirm
    # a session is a failure, not a skip.
    config = ExternalCLIProviderConfig(
        provider="generic-command",
        kind=ExternalCLIProviderKind.GENERIC_COMMAND,
        command=executable,
        auth_args=tuple(argv[1:]),
        auth_check=True,
        timeout_seconds=20.0,
    )
    try:
        adapter = await construct_generic_command_cli_adapter(config)
    except ExternalCLINotAuthenticatedError as exc:
        pytest.fail(f"generic command auth probe failed: {exc}")
    await adapter.aclose()

    route = _resolve_authenticated_route(
        kind=CliProfileKind.CUSTOM,
        provider="generic-command",
        external_cli_kind="generic-command",
        command_name="custom",
        family=ProviderFamily.LOCAL_OPEN_WEIGHT,
    )
    assert route.route_ref == "generic-command:custom"
