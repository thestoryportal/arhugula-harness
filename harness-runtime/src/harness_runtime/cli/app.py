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


def _default_daemon_socket_path() -> Path:
    """Default Unix-socket path for the daemon — `/tmp/harness-daemon-{pid}.sock`."""
    import os
    import tempfile

    return Path(tempfile.gettempdir()) / f"harness-daemon-{os.getpid()}.sock"


class DaemonStartupError(RuntimeError):
    """Raised when the daemon entrypoint fails to bind / start the server.

    Maps to CLI fail-class ``RT-FAIL-CLI-DAEMON-CONNECTION`` → exit code 4
    per runtime spec v1.35 §14.18.4.
    """

    FAIL_CLASS: str = "RT-FAIL-CLI-DAEMON-CONNECTION"


async def _daemon_main(
    *,
    runtime_config: Any,
    socket_path: Path,
) -> None:
    """Daemon entrypoint body — bootstrap, serve on Unix-socket, shutdown.

    Per `.harness/class_1_fork_u_rt_107_daemon_run_workflow_signature_
    underspec.md` Reading (A) ratification 2026-05-28: workflow_id-as-path
    widening at U-RT-62's `run_workflow` handler. Daemon mode reuses the
    existing tool surface VERBATIM at the wire-level signature; the handler
    body discriminates registry-key vs filesystem path on the input.

    Mechanism α (recommended default): uvicorn serving FastMCP's
    `streamable_http_app()` over Unix-socket via `uvicorn.Config(uds=...)`.
    Per-session ctx isolation (spec §14.18.5 spec-MUST) is NOT addressed at
    this MVP — the post-bootstrap `HarnessContext` at `_state['_harness_ctx']`
    is single-shared across concurrent invocations. Concurrent invariant
    (AC #5) deferred to U-RT-109 e2e per `[[verification-shape-sharpened-
    grep-vs-e2e]]` + L9-undecies precedent.
    """
    import uvicorn
    from harness_core.workload_class import WorkloadClass

    from harness_runtime.bootstrap import BootstrapFailure, run_bootstrap
    from harness_runtime.shutdown import shutdown as _shutdown

    # Bootstrap stage 0..9 — constructs the FastMCP server (stage 2) and
    # installs SIGINT/SIGTERM signal handlers (stage 7). The signal handlers
    # set `ctx.drained_flag`; we await that event to break the serve loop.
    try:
        ctx = await run_bootstrap(
            runtime_config, workload_class=WorkloadClass.SOFTWARE_ENGINEERING
        )
    except BootstrapFailure as exc:
        raise DaemonStartupError(
            f"bootstrap failure during daemon startup: {exc}"
        ) from exc

    try:
        # Bind the post-bootstrap HarnessContext on the MCP server's state
        # dict; the run_workflow tool handler reads from this key. The
        # `HarnessMCPServer` Protocol at `types.py:551` declares the abstract
        # shape; the concrete dataclass at `lifecycle/mcp_server.py:80` carries
        # `server` + `_state`. Cast through `Any` to access the concrete
        # surface; bootstrap stage 2 guarantees `ctx.mcp_server is not None`.
        from typing import cast as _cast

        concrete_server: Any = _cast(Any, ctx.mcp_server)
        concrete_server._state["_harness_ctx"] = ctx

        # Construct uvicorn server bound to the Unix-socket. FastMCP's
        # `streamable_http_app()` returns a Starlette app exposing the MCP
        # streamable-HTTP transport per the mcp-python-sdk default.
        fastmcp: Any = concrete_server.server
        starlette_app: Any = fastmcp.streamable_http_app()
        uv_config = uvicorn.Config(
            starlette_app,
            uds=str(socket_path),
            log_level="warning",
            lifespan="on",
        )
        uv_server = uvicorn.Server(uv_config)

        # Serve until `ctx.drained_flag` fires (bootstrap stage 7 wires SIGINT
        # / SIGTERM → drained_flag.set()). We race the serve task against the
        # drained_flag wait; the first to complete cancels the other.
        serve_task = asyncio.create_task(uv_server.serve(), name="uvicorn-serve")
        drain_task = asyncio.create_task(
            ctx.drained_flag.wait(), name="daemon-drain-wait"
        )
        try:
            done, pending = await asyncio.wait(
                {serve_task, drain_task}, return_when=asyncio.FIRST_COMPLETED
            )
            if drain_task in done:
                # Drain signal received — request uvicorn shutdown.
                uv_server.should_exit = True
                try:
                    await asyncio.wait_for(serve_task, timeout=10.0)
                except (TimeoutError, asyncio.TimeoutError):
                    uv_server.force_exit = True
                    await serve_task
            else:
                # uvicorn exited first (e.g., bind failure or external stop).
                drain_task.cancel()
            for task in pending:
                if not task.done():
                    task.cancel()
        except OSError as exc:
            raise DaemonStartupError(
                f"failed to bind Unix-socket {socket_path}: {exc}"
            ) from exc
    finally:
        await _shutdown(ctx)
        # Best-effort cleanup of the socket file.
        try:
            socket_path.unlink(missing_ok=True)
        except OSError:
            pass


@app.command("daemon")
def daemon_command(
    config: Annotated[
        Path | None,
        typer.Option("--config", help="Override default harness.toml config path"),
    ] = None,
    socket_path: Annotated[
        Path | None,
        typer.Option("--socket-path", help="Unix-socket path for the daemon"),
    ] = None,
) -> None:
    """Start the harness daemon (FastMCP server, Unix-socket transport).

    Per runtime spec v1.35 §14.18.1 + Q-K=(c) Unix-socket transport. Bootstraps
    the harness, binds the FastMCP server's streamable-HTTP app to a Unix
    domain socket, and serves until SIGINT/SIGTERM triggers drain. Reuses the
    existing U-RT-62 `run_workflow` MCP tool (PRESERVED VERBATIM at wire-level
    signature; handler-internal discriminator added per the U-RT-107 Class 1
    fork Reading (A) ratification).
    """
    # --- Stage 1: config load (RT-FAIL-CLI-CONFIG-LOAD → exit 3) -----------
    try:
        runtime_config = RuntimeConfigSource.load(config_file=config)
    except RuntimeConfigLoadError as exc:
        _print_fail_class(exc.FAIL_CLASS, exc.reason)
        raise typer.Exit(code=EXIT_CONFIG_ERROR) from exc

    resolved_socket = (
        socket_path if socket_path is not None else _default_daemon_socket_path()
    )

    # --- Stage 2: daemon serve (RT-FAIL-CLI-DAEMON-CONNECTION → exit 4) ----
    try:
        asyncio.run(
            _daemon_main(runtime_config=runtime_config, socket_path=resolved_socket)
        )
    except DaemonStartupError as exc:
        _print_fail_class(exc.FAIL_CLASS, str(exc))
        raise typer.Exit(code=EXIT_BOOTSTRAP_ERROR) from exc

    raise typer.Exit(code=EXIT_SUCCESS)


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
