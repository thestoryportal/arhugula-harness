"""Typer parent app for the operator-facing `harness` CLI.

C-RT-29 contract surface (runtime spec v1.35 §14.18). U-RT-102 lands the
scaffolding: parent Typer app, `run` + `daemon` subcommand stubs, and the
arg-parse-failure → RT-FAIL-CLI-ARG-INVALID → exit-3 remap.

Concrete subcommand bodies land downstream:
- `harness run <file>`             → U-RT-106 (one-shot mode)
- `harness run <file> --daemon`    → U-RT-108 (daemon-client mode)
- `harness daemon`                 → U-RT-107 (daemon entrypoint)
"""

from __future__ import annotations

import sys
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer

_STUB_RUN_MESSAGE = (
    "Not yet implemented — landing at U-RT-106 (one-shot) / U-RT-108 (daemon-client)"
)
_STUB_DAEMON_MESSAGE = "Not yet implemented — landing at U-RT-107 (daemon entrypoint)"


class OutputFormat(StrEnum):
    """`harness run --output` format selector per Q-F at G1 ratification."""

    text = "text"
    json = "json"


app = typer.Typer(
    name="harness",
    help="Multi-LLM Agent Harness operator-facing CLI",
    no_args_is_help=True,
    add_completion=False,
)


@app.command("run")
def run_command(
    workflow_file: Annotated[
        Path,
        typer.Argument(
            help="Workflow manifest path (.yaml / .yml / .toml)",
            show_default=False,
        ),
    ],
    config: Annotated[
        Path | None,
        typer.Option("--config", help="Override default harness.toml config path"),
    ] = None,
    daemon: Annotated[
        bool,
        typer.Option("--daemon", help="Daemon-client mode (sibling to one-shot default)"),
    ] = False,
    output: Annotated[
        OutputFormat,
        typer.Option("--output", help="RunResult output format"),
    ] = OutputFormat.text,
    provider: Annotated[
        str | None,
        typer.Option("--provider", help="Override default_model_binding.provider"),
    ] = None,
    model: Annotated[
        str | None,
        typer.Option("--model", help="Override default_model_binding.model"),
    ] = None,
    tenant_id: Annotated[
        str | None,
        typer.Option("--tenant-id", help="Override RuntimeConfig.tenant_id"),
    ] = None,
) -> None:
    """Invoke a workflow (one-shot, or daemon-client when ``--daemon`` is set)."""
    del workflow_file, config, daemon, output, provider, model, tenant_id
    typer.echo(_STUB_RUN_MESSAGE, err=True)
    raise typer.Exit(code=4)


@app.command("daemon")
def daemon_command(
    config: Annotated[
        Path | None,
        typer.Option("--config", help="Override default harness.toml config path"),
    ] = None,
) -> None:
    """Start the harness daemon (FastMCP server, Unix-socket transport)."""
    del config
    typer.echo(_STUB_DAEMON_MESSAGE, err=True)
    raise typer.Exit(code=4)


# Click UsageError exits with code 2 by default. Per runtime spec v1.35
# §14.18.4 + §14.18.2, CLI arg-parse failures map to RT-FAIL-CLI-ARG-INVALID
# → exit code 3. Remap at the main() entrypoint.
_USAGE_ERROR_EXIT_CODE = 2
_ARG_INVALID_EXIT_CODE = 3
_ARG_INVALID_FAIL_CLASS = "RT-FAIL-CLI-ARG-INVALID"


def main() -> None:
    """Top-level entrypoint mapped at ``[project.scripts] harness``."""
    try:
        app()
    except SystemExit as exc:
        if exc.code == _USAGE_ERROR_EXIT_CODE:
            print(_ARG_INVALID_FAIL_CLASS, file=sys.stderr)
            raise SystemExit(_ARG_INVALID_EXIT_CODE) from exc
        raise
