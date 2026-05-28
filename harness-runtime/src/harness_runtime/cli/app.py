"""Typer parent app for the operator-facing `harness` CLI.

C-RT-29 contract surface (runtime spec v1.35 §14.18). U-RT-102 lands the
scaffolding; U-RT-106 lands the concrete one-shot ``harness run <file>`` body
per spec v1.35 §14.18.1 + admissibility check at dispatch site per spec v1.36
§14.18.4 + plan v2.32 §2.

Concrete subcommand bodies for daemon mode land downstream:
- ``harness run <file> --daemon``  → U-RT-108 (daemon-client mode)
- ``harness daemon``               → U-RT-107 (daemon entrypoint)
"""

from __future__ import annotations

import asyncio
import sys
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Any

import typer
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.engine_class_candidate import ENGINE_CLASS_CANDIDATES

from harness_runtime.config_source import (
    RuntimeConfigLoadError,
    RuntimeConfigSource,
)
from harness_runtime.lifecycle.workflow_manifest_loader import (
    LoadedWorkflow,
    ManifestAdmissibilityError,
    WorkflowManifestLoadError,
    WorkflowManifestLoader,
)

_STUB_DAEMON_MESSAGE = "Not yet implemented — landing at U-RT-107 (daemon entrypoint)"
_STUB_DAEMON_CLIENT_MESSAGE = (
    "Not yet implemented — landing at U-RT-108 (daemon-client mode)"
)


class OutputFormat(StrEnum):
    """`harness run --output` format selector per Q-F at G1 ratification."""

    text = "text"
    json = "json"


# Exit code mapping per runtime spec v1.35 §14.18.2 strict 5-level shape.
EXIT_SUCCESS = 0
EXIT_WORKFLOW_FAIL = 1
EXIT_MANIFEST_ERROR = 2
EXIT_CONFIG_ERROR = 3
EXIT_BOOTSTRAP_ERROR = 4


app = typer.Typer(
    name="harness",
    help="Multi-LLM Agent Harness operator-facing CLI",
    no_args_is_help=True,
    add_completion=False,
)


def _build_cli_overrides(*, tenant_id: str | None) -> dict[str, Any]:
    """Compose CLI overrides for :class:`RuntimeConfigSource.load`.

    ``--provider`` + ``--model`` override the workflow's ``default_model_binding``
    (workflow-level, applied at workflow projection) — NOT ``RuntimeConfig``.
    Only config-level CLI flags flow into ``cli_overrides``.
    """
    overrides: dict[str, Any] = {}
    if tenant_id is not None:
        overrides["tenant_id"] = tenant_id
    return overrides


def _apply_workflow_overrides(
    workflow: LoadedWorkflow,
    *,
    provider: str | None,
    model: str | None,
) -> LoadedWorkflow:
    """Apply CLI ``--provider`` / ``--model`` overrides to the workflow.

    Each override replaces the corresponding field of
    ``workflow.default_model_binding``. When neither flag is set, the workflow
    is returned unchanged.
    """
    if provider is None and model is None:
        return workflow
    current = workflow.default_model_binding
    new_binding = ModelBinding(
        provider=provider if provider is not None else current.provider,
        model=model if model is not None else current.model,
    )
    return workflow.model_copy(update={"default_model_binding": new_binding})


def _check_engine_class_admissibility(workflow: LoadedWorkflow, *, config: Any) -> None:
    """Verify the manifest engine_class is admissible for the deployment surface.

    Plan v2.32 §2 NEW AC #4 — admissibility deferred from U-RT-104 loader site
    to U-RT-106 dispatch site per spec v1.36 §14.19.2 row 7 + §14.19.4
    invariant 2. ``engine_class`` MUST appear in the candidate_set of the
    :data:`ENGINE_CLASS_CANDIDATES` entry whose ``deployment_surface`` matches
    ``config.deployment_surface``.
    """
    engine_class = workflow.manifest_entry.engine_class
    surface = config.deployment_surface
    candidate = next(
        (c for c in ENGINE_CLASS_CANDIDATES if c.deployment_surface == surface),
        None,
    )
    if candidate is None:
        raise ManifestAdmissibilityError(
            f"no candidate set declared for deployment_surface={surface!r}",
            source="(dispatch)",
        )
    if engine_class not in candidate.candidate_set:
        raise ManifestAdmissibilityError(
            f"engine_class={engine_class.value!r} is not admissible for "
            f"deployment_surface={surface.value!r}; "
            f"candidate_set={sorted(c.value for c in candidate.candidate_set)!r}",
            source="(dispatch)",
        )


def _emit_run_result(result: Any, *, output: OutputFormat) -> None:
    """Emit ``RunResult`` to stdout per ``--output`` mode."""
    if output is OutputFormat.json:
        typer.echo(result.model_dump_json())
        return
    # text mode — operator-readable summary.
    typer.echo(f"status:    {result.status}")
    typer.echo(f"workflow:  {result.workflow_id}")
    typer.echo(f"ledger:    {result.audit_ledger_head_hash}")
    if result.failure_cause is not None:
        typer.echo(f"failure:   {result.failure_cause.runtime_fail_class}", err=True)
        typer.echo(f"detail:    {result.failure_cause.detail}", err=True)


def _print_fail_class(fail_class: str, detail: str) -> None:
    """Emit ``RT-FAIL-*`` fail class + detail to stderr per spec §14.18.4."""
    typer.echo(f"{fail_class}: {detail}", err=True)


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
    if daemon:
        typer.echo(_STUB_DAEMON_CLIENT_MESSAGE, err=True)
        raise typer.Exit(code=EXIT_BOOTSTRAP_ERROR)

    # --- Stage 1: config load (RT-FAIL-CLI-CONFIG-LOAD → exit 3) ----------
    cli_overrides = _build_cli_overrides(tenant_id=tenant_id)
    try:
        runtime_config = RuntimeConfigSource.load(
            config_file=config, cli_overrides=cli_overrides
        )
    except RuntimeConfigLoadError as exc:
        _print_fail_class(exc.FAIL_CLASS, exc.reason)
        raise typer.Exit(code=EXIT_CONFIG_ERROR) from exc

    # --- Stage 2: manifest load (RT-FAIL-CLI-MANIFEST-* → exit 2) ---------
    try:
        workflow = WorkflowManifestLoader.load_workflow(workflow_file)
    except WorkflowManifestLoadError as exc:
        _print_fail_class(exc.FAIL_CLASS, exc.reason)
        raise typer.Exit(code=EXIT_MANIFEST_ERROR) from exc

    # --- Stage 3: workflow-level overrides (--provider / --model) ---------
    workflow = _apply_workflow_overrides(workflow, provider=provider, model=model)

    # --- Stage 4: admissibility check at dispatch site (NEW AC #4) --------
    try:
        _check_engine_class_admissibility(workflow, config=runtime_config)
    except ManifestAdmissibilityError as exc:
        _print_fail_class(exc.FAIL_CLASS, exc.reason)
        raise typer.Exit(code=EXIT_MANIFEST_ERROR) from exc

    # --- Stage 5: dispatch via api.run (synchronous one-shot) -------------
    # Lazy import to keep the CLI cold-path import budget small: api.py pulls
    # bootstrap + shutdown transitively, and `harness --help` should not pay
    # that cost.
    from harness_runtime.api import run as _api_run
    from harness_runtime.bootstrap import BootstrapFailure

    try:
        run_result = asyncio.run(_api_run(workflow, config=runtime_config))
    except BootstrapFailure as exc:
        _print_fail_class("RT-FAIL-BOOTSTRAP", str(exc))
        raise typer.Exit(code=EXIT_BOOTSTRAP_ERROR) from exc

    # --- Stage 6: emit RunResult + exit per §14.18.2 ----------------------
    _emit_run_result(run_result, output=output)
    if run_result.status == "completed":
        raise typer.Exit(code=EXIT_SUCCESS)
    # status ∈ {"drained", "failed"} → exit 1
    raise typer.Exit(code=EXIT_WORKFLOW_FAIL)


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
    raise typer.Exit(code=EXIT_BOOTSTRAP_ERROR)


# Click UsageError exits with code 2 by default. Per runtime spec v1.35
# §14.18.4 + §14.18.2, CLI arg-parse failures map to RT-FAIL-CLI-ARG-INVALID
# → exit code 3. We discriminate UsageError (arg-parse) from legitimate
# command-body exits (e.g. manifest-error → exit 2) by running Click in
# ``standalone_mode=False`` so each exception type surfaces directly.
_ARG_INVALID_EXIT_CODE = 3
_ARG_INVALID_FAIL_CLASS = "RT-FAIL-CLI-ARG-INVALID"


def main() -> None:
    """Top-level entrypoint mapped at ``[project.scripts] harness``."""
    # Typer vendors Click internally as ``typer._click``; the exception
    # classes raised at parse / dispatch time are the vendored ones, NOT
    # ``click.exceptions.*`` from the top-level click package. Catch the
    # vendored variants so arg-parse errors (UsageError / NoSuchOption /
    # MissingParameter / ...) route through the RT-FAIL-CLI-ARG-INVALID
    # remap consistently.
    from typer._click.exceptions import (
        ClickException as _ClickException,
        Exit as _Exit,
        UsageError as _UsageError,
    )

    try:
        app(standalone_mode=False)
    except _UsageError as exc:
        # Click's default formatter writes "Usage: ..." + "Error: ..." to
        # stderr. Mirror that, then append the fail-class line per spec.
        exc.show()
        print(_ARG_INVALID_FAIL_CLASS, file=sys.stderr)
        raise SystemExit(_ARG_INVALID_EXIT_CODE) from exc
    except _Exit as exc:
        # typer.Exit(code=N) → propagates as Click Exit; preserve N verbatim.
        raise SystemExit(exc.exit_code) from exc
    except _ClickException as exc:
        exc.show()
        raise SystemExit(exc.exit_code) from exc
