"""Tests for the external CLI provider temp-config helper."""

from __future__ import annotations

import importlib.util
import tomllib
from pathlib import Path
from types import ModuleType

import pytest


def _load_helper() -> ModuleType:
    helper_path = Path(__file__).resolve().parents[2] / "tools" / "external_cli_provider_config.py"
    spec = importlib.util.spec_from_file_location("external_cli_provider_config", helper_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _base_config(root: Path) -> str:
    return f"""[runtime]
deployment_surface = "local-development"
repository_root = "{root.as_posix()}"
default_topology = "single-threaded-linear"
anthropic_optional = false
openai_optional = true
ollama_optional = true

[runtime.provider_secrets]
backend = "local-keyring-env-fallback"
keyring_service = "harness"

[runtime.otel]
otlp_endpoint = "http://localhost:4318"

[runtime.routing_manifest]
manifest_version = 1
per_role_bindings = {{}}
per_workload_overrides = {{}}
retry_policies = {{}}
fallback_chains = [
    {{ primary = {{ provider = "anthropic", model = "claude-haiku-4-5", family = "anthropic" }}, same_family = [], cross_family = [] }},
]
"""


def test_materialize_codex_config_without_modifying_base(tmp_path: Path) -> None:
    helper = _load_helper()
    repo_root = tmp_path / "checkout"
    repo_root.mkdir()
    base_path = tmp_path / "harness.toml"
    base_text = _base_config(repo_root)
    base_path.write_text(base_text, encoding="utf-8")
    out_path = tmp_path / "codex.toml"

    result = helper.materialize_external_cli_config(
        provider="codex",
        base_config=base_path,
        repo_root=repo_root,
        output=out_path,
        model="gpt-5",
    )

    assert result == out_path
    assert base_path.read_text(encoding="utf-8") == base_text
    data = tomllib.loads(out_path.read_text(encoding="utf-8"))
    runtime = data["runtime"]
    assert runtime["enabled_provider_names"] == ["codex"]
    provider = runtime["external_cli_providers"][0]
    assert provider["provider"] == "codex"
    assert provider["kind"] == "codex"
    assert provider["command"] == "codex"
    primary = runtime["routing_manifest"]["fallback_chains"][0]["primary"]
    assert primary == {"provider": "codex", "model": "gpt-5", "family": "openai"}


def test_materialize_custom_generic_config_with_argv_templates(tmp_path: Path) -> None:
    helper = _load_helper()
    repo_root = tmp_path / "checkout"
    repo_root.mkdir()
    base_path = tmp_path / "harness.toml"
    base_path.write_text(_base_config(repo_root), encoding="utf-8")
    out_path = tmp_path / "custom.toml"

    helper.materialize_external_cli_config(
        provider="generic-command",
        provider_name="local_llm",
        command="my-llm",
        args=("--model", "{model}", "--json"),
        auth_args=("auth", "status"),
        response_format="json",
        family="openai",
        model="demo-model",
        base_config=base_path,
        repo_root=repo_root,
        output=out_path,
    )

    runtime = tomllib.loads(out_path.read_text(encoding="utf-8"))["runtime"]
    provider = runtime["external_cli_providers"][0]
    assert provider["provider"] == "local_llm"
    assert provider["kind"] == "generic-command"
    assert provider["args"] == ["--model", "{model}", "--json"]
    assert provider["auth_args"] == ["auth", "status"]
    # No-preset derivation: declared auth_args imply auth_check unless
    # explicitly overridden — `bool(auth_args)` at _build_provider_entry.
    assert provider["auth_check"] is True
    assert provider["response_format"] == "json"
    assert runtime["routing_manifest"]["fallback_chains"][0]["primary"] == {
        "provider": "local_llm",
        "model": "demo-model",
        "family": "openai",
    }


def test_cli_prints_materialized_provider_config_path(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    helper = _load_helper()
    repo_root = tmp_path / "checkout"
    repo_root.mkdir()
    base_path = tmp_path / "harness.toml"
    base_path.write_text(_base_config(repo_root), encoding="utf-8")
    out_path = tmp_path / "gemini.toml"

    exit_code = helper.main(
        [
            "gemini",
            "--base",
            str(base_path),
            "--repo-root",
            str(repo_root),
            "--output",
            str(out_path),
        ]
    )

    assert exit_code == 0
    assert capsys.readouterr().out.strip() == out_path.as_posix()
    runtime = tomllib.loads(out_path.read_text(encoding="utf-8"))["runtime"]
    assert runtime["enabled_provider_names"] == ["gemini"]
    provider = runtime["external_cli_providers"][0]
    assert provider["kind"] == "gemini"
    # The legacy Gemini preset declares its auth probe, so the materialized
    # entry carries it even though no ``--auth-arg`` was passed. ``auth_check``
    # stays false: firing the probe is an outward model call, operator opt-in.
    assert provider["auth_args"] == ["--skip-trust", "-p", "Reply with the single word OK."]
    assert provider["auth_check"] is False


def test_explicit_auth_args_override_the_gemini_preset_declaration(tmp_path: Path) -> None:
    helper = _load_helper()
    repo_root = tmp_path / "checkout"
    repo_root.mkdir()
    base_path = tmp_path / "harness.toml"
    base_path.write_text(_base_config(repo_root), encoding="utf-8")
    out_path = tmp_path / "gemini-override.toml"

    helper.materialize_external_cli_config(
        provider="gemini",
        auth_args=("--version",),
        base_config=base_path,
        repo_root=repo_root,
        output=out_path,
    )

    runtime = tomllib.loads(out_path.read_text(encoding="utf-8"))["runtime"]
    assert runtime["external_cli_providers"][0]["auth_args"] == ["--version"]


def test_cli_auth_check_flag_activates_the_gemini_preset_probe(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """G3 (PR #1137 follow-up) — the gemini preset ships ``auth_check=False``
    plus a declared probe, so the probe is inert unless the operator passes
    ``--auth-check``. No test passed an explicit ``auth_check`` at all, which
    let the explicit-argument override term be dropped silently."""
    helper = _load_helper()
    repo_root = tmp_path / "checkout"
    repo_root.mkdir()
    base_path = tmp_path / "harness.toml"
    base_path.write_text(_base_config(repo_root), encoding="utf-8")
    out_path = tmp_path / "gemini-auth-check.toml"

    exit_code = helper.main(
        [
            "gemini",
            "--auth-check",
            "--base",
            str(base_path),
            "--repo-root",
            str(repo_root),
            "--output",
            str(out_path),
        ]
    )

    assert exit_code == 0
    assert capsys.readouterr().out.strip() == out_path.as_posix()
    runtime = tomllib.loads(out_path.read_text(encoding="utf-8"))["runtime"]
    provider = runtime["external_cli_providers"][0]
    assert provider["auth_check"] is True
    assert provider["auth_args"] == ["--skip-trust", "-p", "Reply with the single word OK."]


def test_cli_no_auth_check_flag_disables_presets_that_default_to_true(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """G3 (PR #1137 follow-up) — the ``--no-auth-check`` half of the explicit
    override, on the presets whose declared default is ``auth_check=True``."""
    helper = _load_helper()
    repo_root = tmp_path / "checkout"
    repo_root.mkdir()
    base_path = tmp_path / "harness.toml"
    base_path.write_text(_base_config(repo_root), encoding="utf-8")

    for name in ("claude_code", "codex", "antigravity"):
        out_path = tmp_path / f"{name}-no-auth-check.toml"
        exit_code = helper.main(
            [
                name,
                "--no-auth-check",
                "--base",
                str(base_path),
                "--repo-root",
                str(repo_root),
                "--output",
                str(out_path),
            ]
        )

        assert exit_code == 0
        assert capsys.readouterr().out.strip() == out_path.as_posix()
        runtime = tomllib.loads(out_path.read_text(encoding="utf-8"))["runtime"]
        assert runtime["external_cli_providers"][0]["auth_check"] is False


def test_cli_no_auth_check_flag_overrides_the_no_preset_derivation(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The explicit override must also win on the no-preset (generic-command)
    path, where the default is derived as ``bool(auth_args)`` — a variant
    mutation restricting the override term to preset providers would silently
    ignore ``--no-auth-check`` here while every preset-path test stays green."""
    helper = _load_helper()
    repo_root = tmp_path / "checkout"
    repo_root.mkdir()
    base_path = tmp_path / "harness.toml"
    base_path.write_text(_base_config(repo_root), encoding="utf-8")
    out_path = tmp_path / "generic-no-auth-check.toml"

    exit_code = helper.main(
        [
            "generic-command",
            "--provider-name",
            "local_llm",
            "--command",
            "my-llm",
            "--model",
            "demo-model",
            "--family",
            "openai",
            "--auth-arg",
            "auth",
            "--auth-arg",
            "status",
            "--no-auth-check",
            "--base",
            str(base_path),
            "--repo-root",
            str(repo_root),
            "--output",
            str(out_path),
        ]
    )

    assert exit_code == 0
    assert capsys.readouterr().out.strip() == out_path.as_posix()
    provider = tomllib.loads(out_path.read_text(encoding="utf-8"))["runtime"][
        "external_cli_providers"
    ][0]
    assert provider["auth_args"] == ["auth", "status"]
    assert provider["auth_check"] is False


def test_presets_without_declared_auth_args_emit_no_auth_args(tmp_path: Path) -> None:
    helper = _load_helper()
    repo_root = tmp_path / "checkout"
    repo_root.mkdir()
    base_path = tmp_path / "harness.toml"
    base_path.write_text(_base_config(repo_root), encoding="utf-8")

    for name in ("claude_code", "codex", "antigravity"):
        out_path = tmp_path / f"{name}.toml"
        helper.materialize_external_cli_config(
            provider=name,
            base_config=base_path,
            repo_root=repo_root,
            output=out_path,
        )
        runtime = tomllib.loads(out_path.read_text(encoding="utf-8"))["runtime"]
        assert "auth_args" not in runtime["external_cli_providers"][0]


def test_cli_materializes_antigravity_print_mode_config(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    helper = _load_helper()
    repo_root = tmp_path / "checkout"
    repo_root.mkdir()
    base_path = tmp_path / "harness.toml"
    base_path.write_text(_base_config(repo_root), encoding="utf-8")

    out_path = tmp_path / "antigravity.toml"

    exit_code = helper.main(
        [
            "antigravity",
            "--base",
            str(base_path),
            "--repo-root",
            str(repo_root),
            "--output",
            str(out_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.strip() == out_path.as_posix()
    assert captured.err == ""
    runtime = tomllib.loads(out_path.read_text(encoding="utf-8"))["runtime"]
    assert runtime["enabled_provider_names"] == ["antigravity"]
    provider = runtime["external_cli_providers"][0]
    assert provider["provider"] == "antigravity"
    assert provider["kind"] == "antigravity"
    assert provider["command"] == "agy"
    # No flag passed: the preset's declared auth_check=True must survive the
    # argparse default (a `default=False` regression would silently disable
    # the auth probe for every default-True preset).
    assert provider["auth_check"] is True
    primary = runtime["routing_manifest"]["fallback_chains"][0]["primary"]
    assert primary == {
        "provider": "antigravity",
        "model": "Gemini 3.5 Flash (Low)",
        "family": "google",
    }


def test_materialize_rejects_unknown_provider_choice(tmp_path: Path) -> None:
    """B-28 finding #15 (test-quality preflight 2026-07-12) — no test
    exercised any of this helper's validation/error branches; an unknown
    provider (not a preset and not ``generic-command``) must raise."""
    helper = _load_helper()
    repo_root = tmp_path / "checkout"
    repo_root.mkdir()
    base_path = tmp_path / "harness.toml"
    base_path.write_text(_base_config(repo_root), encoding="utf-8")

    with pytest.raises(ValueError, match="provider must be one of"):
        helper.materialize_external_cli_config(
            provider="not-a-real-provider",
            base_config=base_path,
            repo_root=repo_root,
        )


def test_generic_command_requires_provider_name(tmp_path: Path) -> None:
    """B-28 finding #15 — ``generic-command`` without ``--provider-name``
    (``provider_name=None``) must raise."""
    helper = _load_helper()
    repo_root = tmp_path / "checkout"
    repo_root.mkdir()
    base_path = tmp_path / "harness.toml"
    base_path.write_text(_base_config(repo_root), encoding="utf-8")

    with pytest.raises(ValueError, match="requires --provider-name"):
        helper.materialize_external_cli_config(
            provider="generic-command",
            command="my-llm",
            model="demo-model",
            family="openai",
            base_config=base_path,
            repo_root=repo_root,
        )


def test_generic_command_requires_command(tmp_path: Path) -> None:
    """B-28 finding #15 — ``generic-command`` without ``--command`` must raise."""
    helper = _load_helper()
    repo_root = tmp_path / "checkout"
    repo_root.mkdir()
    base_path = tmp_path / "harness.toml"
    base_path.write_text(_base_config(repo_root), encoding="utf-8")

    with pytest.raises(ValueError, match="requires --command"):
        helper.materialize_external_cli_config(
            provider="generic-command",
            provider_name="local_llm",
            model="demo-model",
            family="openai",
            base_config=base_path,
            repo_root=repo_root,
        )


def test_generic_command_requires_model(tmp_path: Path) -> None:
    """B-28 finding #15 — ``generic-command`` without ``--model`` must raise."""
    helper = _load_helper()
    repo_root = tmp_path / "checkout"
    repo_root.mkdir()
    base_path = tmp_path / "harness.toml"
    base_path.write_text(_base_config(repo_root), encoding="utf-8")

    with pytest.raises(ValueError, match="requires --model"):
        helper.materialize_external_cli_config(
            provider="generic-command",
            provider_name="local_llm",
            command="my-llm",
            family="openai",
            base_config=base_path,
            repo_root=repo_root,
        )


def test_generic_command_requires_family(tmp_path: Path) -> None:
    """B-28 finding #15 — ``generic-command`` without ``--family`` must raise."""
    helper = _load_helper()
    repo_root = tmp_path / "checkout"
    repo_root.mkdir()
    base_path = tmp_path / "harness.toml"
    base_path.write_text(_base_config(repo_root), encoding="utf-8")

    with pytest.raises(ValueError, match="requires --family"):
        helper.materialize_external_cli_config(
            provider="generic-command",
            provider_name="local_llm",
            command="my-llm",
            model="demo-model",
            base_config=base_path,
            repo_root=repo_root,
        )


def test_cli_prints_error_and_exits_2_on_invalid_provider(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """B-28 finding #15 — the CLI ``main()`` entry point's ``except
    ValueError`` branch (print to stderr, exit code 2) was never exercised."""
    helper = _load_helper()
    repo_root = tmp_path / "checkout"
    repo_root.mkdir()
    base_path = tmp_path / "harness.toml"
    base_path.write_text(_base_config(repo_root), encoding="utf-8")

    exit_code = helper.main(
        [
            "not-a-real-provider",
            "--base",
            str(base_path),
            "--repo-root",
            str(repo_root),
        ]
    )

    assert exit_code == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "error:" in captured.err
    assert "provider must be one of" in captured.err
