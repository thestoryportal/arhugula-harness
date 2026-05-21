"""`harness_runtime.run` Python API + `RunResult` shape (U-RT-42; U-RT-43 wires bootstrap).

Per `Spec_Harness_Runtime_v1.md` v1.1 §8 (C-RT-08 — `run()` Python API
contract; F-P2-2 absorption) + §9 (C-RT-09 — `RunResult` shape) + §14
(C-RT-14 — runtime-local fail-class taxonomy; FailureCause mirror).

**Closes L8 stage 5 LOOP_INIT.** U-RT-42 lands the operator-facing
ingress signature + result schema. Per the spec §16 #4 decided posture
(async-only at Track A), `run` is the single Track A entry. The
bootstrap orchestrator body lands at U-RT-43; this module wires the
pre-bootstrap ingress (workflow validation + concurrency guard) and
stubs the bootstrap call so the bootstrap-not-yet-landed path is a
typed surface.

**Resolves the standing entrypoint design gap.** The Class 1 record at
`.harness/class_1_tension_runtime_entrypoint_design_gap.md` (filed
2026-05-16) documented the absence of an entrypoint signature in the
design corpus. `Spec_Harness_Runtime_v1.md` v1.1 (filed Phase 2
Session 4) is the operator resolution; U-RT-42 implements that
resolution at the package root.

**WorkflowObject typing decision (Option C — runtime-local Protocol).**
Spec C-RT-08 Risk surface enumerates 3 options for the `WorkflowObject`
typed source: (a) CP spec extension, (b) `harness-core` carrier,
(c) runtime structural Protocol. "The choice is made at U-RT-42
landing time, not now." This landing picks Option C — smallest blast
radius, doesn't touch CP or harness-core, satisfies the C-RT-08
signature requirement, defers cross-axis type negotiation until a
caller surfaces a real `WorkflowObject` shape. Runtime-local
`WorkflowObject` Protocol declared here.

**CostAttribution spec-vs-OD-type drift (Class 3 informational).** Spec
C-RT-09 names the `cost_attribution` field type as `CostAttribution
(OD type)`. The OD axis exports no type literally named
`CostAttribution`; the closest OD-materialized aggregate is
`harness_od.cross_family_rollup.CrossFamilyCostRollup` (C-OD-15 §15.1
— aggregated cost rollup along one `RollupAxis`). This landing types
the field as `tuple[CrossFamilyCostRollup, ...]` — the natural
materialized shape of the spec's "aggregated 5-step cost-attribution
rollup". Same shape as the U-RT-34 Class 3 spec-prose-plan-body
drift; non-blocking; logged inline for future runtime-spec revision
pass.

**Workflow execution landed at Lane 6 (2026-05-20).** `run()` now
delegates workflow body execution to `harness_cp.workflow_driver.
execute_workflow()` (C-CP-25 §25) per `Spec_Harness_Runtime_v1.md` §11
risk-surface guidance ("If CP later surfaces a native drain primitive,
refactor harness-runtime to delegate drain to CP — this contract
becomes a thin adapter"). The `WorkflowExecutionNotYetLandedError`
stub surface is removed at this landing. `run()` owns the full
bootstrap → execute → shutdown lifecycle per C-RT-08 + C-RT-10. The
synchronous CP driver is offloaded to a worker thread via
`asyncio.to_thread` so the asyncio loop remains responsive to signal
handlers — this composition is what materializes U-RT-44 AC #2's
in-flight step bounded-wait (drain flag set by signal → driver returns
DRAINED at next boundary → to_thread future resolves). The
`WorkflowObject` Protocol grows with 4 new read-only properties
(`manifest_entry`, `steps`, `default_model_binding`)
per the §8 risk-surface "growth is non-breaking when fields are
optional or read-only" authorization; Path A operator-ratified
2026-05-20. Closes `[[fork-u-rt-44-workflow-loop-drain]]` for U-RT-44
AC #2 + U-RT-49 state-ledger / lifecycle-event ACs. Residual:
cost-attribution AC stays STRUCK pending U-OD-21 fork resolution.

**Concurrency guard via module-level `asyncio.Lock`.** Per C-RT-08
v1.1 idempotency-and-concurrency invariant: "Concurrent invocations
from the same process surface typed `ConcurrentRunNotSupported` — the
second concurrent call detects an existing in-flight `HarnessContext`
(via process-local lock initialized at module import) and fails fast
before stage 0." The lock is module-level; acquired non-blocking by
`run()`; release in `finally` so a failed bootstrap doesn't permanently
poison the lock.
"""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import Sequence
from typing import Any, Literal, Protocol, cast, runtime_checkable

from harness_core.identity import WorkflowID
from harness_core.workload_class import WorkloadClass
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.workflow_driver import (
    DriverContext as _CpDriverContext,
)
from harness_cp.workflow_driver import (
    execute_workflow,
)
from harness_cp.workflow_driver_types import RunResult as _CpRunResult
from harness_cp.workflow_driver_types import (
    RunStatus as _CpRunStatus,
)
from harness_cp.workflow_driver_types import WorkflowStep
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_od.cross_family_rollup import CrossFamilyCostRollup
from pydantic import BaseModel, ConfigDict

from harness_runtime.types import RuntimeConfig

# ---------------------------------------------------------------------------
# Typed errors (C-RT-08 + C-RT-14).
# ---------------------------------------------------------------------------


class InvalidWorkflowError(Exception):
    """`RT-FAIL-INVALID-WORKFLOW` — pre-bootstrap workflow-type rejection."""


class ConcurrentRunNotSupported(Exception):  # noqa: N818 — domain-anchored name
    """`RT-FAIL-CONCURRENT-RUN` — second concurrent `run()` detected (C-RT-08 v1.1)."""


class HarnessDraining(Exception):  # noqa: N818 — domain-anchored name
    """`RT-FAIL-HARNESS-DRAINING` — `run()` invoked after process-level drain set.

    Per `Spec_Harness_Runtime_v1.md` v1.1 §11 C-RT-11: "After flag-set,
    `harness_runtime.run(...)` rejects new invocations with typed
    `HarnessDraining` error." The process-level drain flag at
    `harness_runtime.drain._process_drained` is one-way; a new harness
    invocation requires process restart.

    Raised pre-bootstrap before the module-level `_run_lock` is acquired
    so a drained process surfaces the typed error without constructing a
    new `HarnessContext`.
    """


# ---------------------------------------------------------------------------
# `WorkflowObject` runtime-local Protocol (Option C per spec §8 Risk surface).
# ---------------------------------------------------------------------------


@runtime_checkable
class WorkflowObject(Protocol):
    """Structural workflow-object surface (C-RT-08 Option C resolution).

    **Growth at Lane 6 (2026-05-20) — Path A (operator-ratified).** Per the
    spec §8 risk surface's "growth is non-breaking when fields are optional
    or read-only" authorization, this Protocol grows from the U-RT-43
    minimum-viable shape (`workflow_id` + `workload_class`) to carry the
    surface the CP workflow driver (`harness_cp.workflow_driver.execute_
    workflow`, C-CP-25 §25) needs. Callers pre-Lane-6 still conform if
    they implement the four new read-only properties; `run()` now
    delegates execution to the CP driver rather than raising
    `WorkflowExecutionNotYetLandedError`.

    All six surfaces are `@property` (read-only), satisfying the
    non-breaking-growth invariant. The driver consumes the substrate
    via runtime-local Protocols on `HarnessContext` — those Protocols
    are at `harness_cp.workflow_driver.{LedgerWriterLike,
    LifecycleEventEmitterLike, DriverContext}` and are structurally
    satisfied by the bootstrapped context.
    """

    @property
    def workflow_id(self) -> str:
        """Stable identity of the workflow being executed."""
        ...

    @property
    def workload_class(self) -> WorkloadClass:
        """The workflow's workload class — threaded into bootstrap stage 1
        state-ledger composition + stage 3b routing-manifest residence."""
        ...

    @property
    def manifest_entry(self) -> WorkflowManifestEntry:
        """CP workflow manifest entry per C-CP-06 §6.1.

        Carries `engine_class`, `topology_pattern`, per-step overrides,
        fallback chain, HITL placements, layer budgets. Consumed by the
        CP driver at C-CP-25 §25.3.1 validation + §25.6 replay-resumption
        composition + §25.5 lifecycle-event filtering.
        """
        ...

    @property
    def steps(self) -> Sequence[WorkflowStep]:
        """Step sequence in declaration order (CP spec v1.4 §25 amendment §E).

        Decoupled from `manifest_entry` per the operator-ratified Path A
        decision at U-CP-56 land time: manifest carries config; steps
        carry the declarative body. The CP driver iterates this sequence
        under SINGLE_THREADED_LINEAR topology (no parallel branching at
        v1.4).
        """
        ...

    @property
    def default_model_binding(self) -> ModelBinding:
        """Default `(provider, model)` binding for steps without per-step
        override (C-CP-06 §6.2 + C-CP-13 §13.3 lead-agent binding)."""
        ...


# ---------------------------------------------------------------------------
# `FailureCause` (C-RT-09 deferred-to-discretion; C-RT-14 mirror per spec).
# ---------------------------------------------------------------------------


class FailureCause(BaseModel):
    """`RunResult.failure_cause` typed shape (C-RT-09 + C-RT-14 mirror).

    Spec C-RT-09 says "Deferred to implementation discretion;
    alternatively reuse C-RT-14 runtime-local fail-class set." This
    landing reuses the C-RT-14 set as a string-tagged record. CP-side
    workflow-step failures (per `validator_fail_taxonomy`) compose
    through `validator_fail_class` when they bubble through the runtime
    boundary; pre-bootstrap and shutdown-side failures use the
    runtime-local tag.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    runtime_fail_class: str
    """The `RT-FAIL-*` tag from C-RT-14 (e.g. `'RT-FAIL-INVALID-WORKFLOW'`)."""

    detail: str
    """Operator-readable failure detail (no PII / secret content per X-AL-3)."""

    validator_fail_class: str | None = None
    """CP-side validator-fail tag, populated when the failure bubbled through
    CP's workflow-step validator (per C-CP-05 §5 5-class set)."""


# ---------------------------------------------------------------------------
# `RunResult` (C-RT-09).
# ---------------------------------------------------------------------------


class RunResult(BaseModel):
    """Terminal `run()` result schema (C-RT-09).

    Frozen Pydantic v2; `arbitrary_types_allowed=True` to carry the
    `CrossFamilyCostRollup` rollup tuple (a Pydantic v2 model). Field
    invariants per C-RT-09 — `status='failed'` implies
    `failure_cause is not None`; `audit_ledger_head_hash` always
    present.
    """

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    status: Literal["completed", "drained", "failed"]
    """Terminal status of the workflow execution."""

    workflow_id: WorkflowID
    """Identity of the executed workflow."""

    terminal_state: dict[str, Any]
    """Workflow's terminal state object per CP lifecycle loop contract.
    May be `{}` for trivial workflows."""

    audit_ledger_head_hash: str
    """Post-execution audit-ledger head hash (hex) for verification.
    Always present per C-RT-09 invariants."""

    trace_ids: tuple[str, ...]
    """Root span trace IDs emitted by the workflow execution."""

    cost_attribution: tuple[CrossFamilyCostRollup, ...]
    """Aggregated 5-step cost-attribution rollup (C-OD-15 §15.1).

    Spec C-RT-09 names this `CostAttribution (OD type)`; OD exports no
    type literally named `CostAttribution`. `CrossFamilyCostRollup` is
    the C-OD-15 §15.1 aggregated cost-rollup primitive — the natural
    materialized shape of the spec's "Aggregated 5-step cost-attribution
    rollup". Class 3 spec-prose-vs-OD-type drift; non-blocking.
    """

    failure_cause: FailureCause | None = None
    """`None` unless `status == 'failed'` (C-RT-09 invariant)."""


# ---------------------------------------------------------------------------
# Module-level concurrency lock (C-RT-08 v1.1 idempotency-and-concurrency).
# ---------------------------------------------------------------------------


_run_lock: asyncio.Lock = asyncio.Lock()


# ---------------------------------------------------------------------------
# U-RT-62 AC #5 — in-process MCP tool invocation helper.
# ---------------------------------------------------------------------------


async def _refuse_elicitation_in_api_run(
    context: Any, params: Any
) -> Any:
    """Elicitation callback for `api.run()`'s in-process ClientSession.

    Per the operator-ratified Q2+Q3 reading at the C-RT-18 v1.12 fork:
    `api.run()` is the carrier-preservation surface for the 4 existing
    test callsites importing `from harness_runtime.api import run`.
    Production HITL routes via Claude Code as the registered MCP client
    per Reading α; `api.run()` is NOT structurally an HITL-bearing
    entry point at v1.12 MVP.

    If a workflow invoked via `api.run()` fires a HITL gate, this callback
    runs on the in-process ClientSession side. We respond with `decline`
    + a clear rejection reason — the composer at step 4i REJECT branch
    maps this to a controlled workflow termination (rather than a hang
    or silent absorption). Future arcs may bind a richer test-fixture
    callback to exercise the elicitation surface from api.run-driven
    integration tests.
    """
    _ = (context, params)
    from mcp.shared.context import RequestContext  # noqa: F401 — type-pin
    from mcp.types import ElicitResult

    return ElicitResult(
        action="decline",
        content=None,
    )


async def _invoke_run_workflow_via_in_process_mcp(
    fastmcp_server: Any,
    workflow_id: str,
) -> _CpRunResult:
    """Open an in-memory MCP client session against `fastmcp_server` +
    call the `run_workflow` tool with `workflow_id`.

    Per U-RT-62 AC #5 + the MCP SDK 1.27.1 `create_connected_server_and_
    client_session` in-memory transport helper. Returns the unmarshalled
    CP `RunResult`; raises `MCPToolError` (passes through) on any
    non-result tool-side exception.

    The tool body returns a JSON-serializable dict via
    `cp_result.model_dump(mode="json")`; FastMCP 1.27.1 places the
    serialization at `CallToolResult.content[0].text` (TextContent, JSON
    string). `structuredContent` is None at this transport — we parse
    the text payload directly via `_CpRunResult.model_validate_json`.
    """
    import json

    from mcp.shared.memory import create_connected_server_and_client_session

    async with create_connected_server_and_client_session(
        fastmcp_server,
        elicitation_callback=_refuse_elicitation_in_api_run,
        raise_exceptions=True,
    ) as session:
        tool_result = await session.call_tool(
            "run_workflow", {"workflow_id": workflow_id}
        )

    if tool_result.isError:
        # Tool body raised. FastMCP serializes the error text into
        # `content[0].text`; surface as a runtime error (the existing
        # api.run semantics propagate driver-side exceptions).
        error_text = (
            tool_result.content[0].text  # type: ignore[union-attr]
            if tool_result.content
            else "unknown tool error"
        )
        raise RuntimeError(
            f"run_workflow MCP tool raised inside in-process invocation: "
            f"{error_text}"
        )

    if not tool_result.content:
        raise RuntimeError(
            "run_workflow MCP tool returned empty content; expected "
            "TextContent with JSON-serialized RunResult dict"
        )

    text_block = tool_result.content[0]
    payload_text = getattr(text_block, "text", None)
    if payload_text is None:
        raise RuntimeError(
            f"run_workflow MCP tool returned non-text content: "
            f"{type(text_block).__name__}"
        )

    # FastMCP wraps dict returns in a top-level JSON object; verify the
    # shape matches the CP RunResult schema rather than the dict wrapper.
    parsed = json.loads(payload_text)
    # FastMCP 1.27.1 returns the dict as-is (not wrapped in {"result": ...});
    # the v1.11 baseline test substrate validates this assumption via
    # _CpRunResult.model_validate which raises on schema mismatch.
    return _CpRunResult.model_validate(parsed)


# ---------------------------------------------------------------------------
# `run()` entry point (C-RT-08).
# ---------------------------------------------------------------------------


async def run(
    workflow: WorkflowObject,
    *,
    config: RuntimeConfig | None = None,
) -> RunResult:
    """Execute one workflow end-to-end (C-RT-08 Track A operator-facing API).

    Bootstrap → execute → shutdown per C-RT-02. Async-only at Track A
    per spec §16 #4 (decided 2026-05-19). Single workflow per call;
    multi-workflow ingest is Track B (out of scope).

    Raises
    ------
    InvalidWorkflowError
        `RT-FAIL-INVALID-WORKFLOW` — `workflow` does not conform to the
        `WorkflowObject` structural Protocol. Pre-bootstrap rejection;
        no `HarnessContext` constructed.
    ConcurrentRunNotSupported
        `RT-FAIL-CONCURRENT-RUN` — a second `run()` invocation detected
        the module-level lock held by an in-flight call. Caller
        serializes or moves to a cached-context entry point (Track B).
    harness_runtime.bootstrap.BootstrapFailure
        `RT-FAIL-BOOTSTRAP` — one of the 9 bootstrap stages raised;
        stages 0..N-1 rolled back in reverse order. Original cause
        attached.
    """
    # Pre-bootstrap drain check (C-RT-11 surface (3)). Checked before
    # `_run_lock` acquisition so a drained process surfaces `HarnessDraining`
    # without constructing a new `HarnessContext`. Import lazily so the
    # api.py → drain.py edge stays at runtime (drain.py is a leaf module).
    from harness_runtime.drain import is_process_drained

    if is_process_drained():
        raise HarnessDraining(
            "process-level drain flag set (SIGTERM/SIGINT received in a "
            "prior `run()` invocation); spec §11 invariant: the flag is "
            "one-way for process lifetime — a new invocation requires "
            "process restart."
        )
    if not isinstance(workflow, WorkflowObject):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise InvalidWorkflowError(
            f"`run()` requires a `WorkflowObject` (with `workflow_id`, "
            f"`workload_class`, `manifest_entry`, `steps`, "
            f"`default_model_binding` properties); got "
            f"{type(workflow).__name__!r}"
        )
    if _run_lock.locked():
        raise ConcurrentRunNotSupported(
            "a `run()` invocation is already in flight in this process; "
            "Track A is bootstrap-per-call (no cached context). Serialize "
            "calls or move to a cached-context entry point (Track B)."
        )
    # Lazy imports to keep api.py → bootstrap / shutdown edges one-way at
    # type-check time and to avoid bootstrap-time import cost when
    # `InvalidWorkflowError` / `ConcurrentRunNotSupported` fire pre-bootstrap.
    from harness_runtime.bootstrap import run_bootstrap
    from harness_runtime.shutdown import shutdown as _shutdown

    async with _run_lock:
        resolved_config = config if config is not None else _default_config()
        ctx = await run_bootstrap(
            resolved_config,
            workload_class=workflow.workload_class,
        )
        try:
            # U-RT-62 AC #5 — thin-wrapper reframe per spec v1.12 §14.8.3
            # workflow-initiation topology pin (Reading α CC-initiates). The
            # operator-facing `api.run()` symbol is preserved as carrier-
            # preservation per Q2 ratification at the C-RT-18 v1.12 fork;
            # the body now invokes the MCP-tool path via an in-process
            # `ClientSession` against `ctx.mcp_server.server` (the FastMCP
            # server materialized at bootstrap stage 2 per AC #2). This
            # exercises the same H_T-as-MCP-server hosting topology that
            # production CC→`run_workflow` invocation uses, so the e2e
            # contract is unified at criterion B verification per spec
            # v1.12 §14.8.3 v1.12 RETIRE-READY → RETIRED gate (AC #6).
            #
            # The tool body internalizes the asyncio.to_thread → wait_for
            # composition + the workflow.step_dispatchers override fallback;
            # api.run's role here is bootstrap → workflow registration →
            # in-process tool call → CP result parse → shutdown.
            assert ctx.mcp_server is not None, (
                "ctx.mcp_server is None post-bootstrap — stage 2 AS did not "
                "materialize the FastMCP server per U-RT-62 AC #2"
            )
            # Bind the post-bootstrap context on the mutable holder so the
            # `run_workflow` tool body can reach `ctx.step_dispatchers` etc.
            ctx.mcp_server._state["_harness_ctx"] = ctx
            # Register the workflow keyed by workflow_id so the tool body
            # can look it up. WorkflowObject is a runtime-local structural
            # Protocol; not MCP-serializable. The serializable wire is the
            # `workflow_id` string only.
            ctx.mcp_server.workflow_registry[workflow.workflow_id] = workflow
            try:
                cp_result = await _invoke_run_workflow_via_in_process_mcp(
                    ctx.mcp_server.server, workflow.workflow_id
                )
            finally:
                # Defensive cleanup — `_run_lock` serializes invocations but
                # the registry + state holders MUST NOT carry stale entries
                # across calls (Track B future cached-context entry point;
                # pytest-asyncio loop reuse).
                ctx.mcp_server.workflow_registry.pop(workflow.workflow_id, None)
                ctx.mcp_server._state.pop("_harness_ctx", None)
            # Per AC #5 advisor reconcile pin — `timed_out` derived from the
            # CP result (the tool body absorbed the TimeoutError and emitted
            # a DRAINED CP result with `RT-FAIL-DRAIN-TIMEOUT` fail_class).
            timed_out = (
                cp_result.status == _CpRunStatus.DRAINED
                and cp_result.fail_class == "RT-FAIL-DRAIN-TIMEOUT"
            )
        finally:
            # Per C-RT-08 + C-RT-10: run() owns the full bootstrap → execute
            # → shutdown lifecycle. Shutdown after execute, regardless of CP
            # status. ShutdownReport carries the audit-ledger head hash.
            shutdown_report = await _shutdown(ctx)
        return _build_run_result(cp_result, shutdown_report, timed_out=timed_out)


# ---------------------------------------------------------------------------
# CP RunResult → runtime RunResult conversion (C-RT-09 + C-CP-25 §25.2).
# ---------------------------------------------------------------------------


_CP_TO_RT_STATUS: dict[_CpRunStatus, Literal["completed", "drained", "failed"]] = {
    _CpRunStatus.SUCCESS: "completed",
    _CpRunStatus.DRAINED: "drained",
    _CpRunStatus.FAILED: "failed",
    # PARTIAL is reserved at C-CP-25 §25.2 for future multi-step error modes;
    # at v1.4 the driver never returns PARTIAL. Map to "failed" defensively
    # so the runtime-side Literal type narrows cleanly.
    _CpRunStatus.PARTIAL: "failed",
}


def _build_run_result(
    cp_result: _CpRunResult, shutdown_report: Any, *, timed_out: bool = False
) -> RunResult:
    """Project a CP driver `RunResult` + runtime `ShutdownReport` into the
    runtime-facing `RunResult` per C-RT-09.

    Field mapping:
    - `status`: closed enum projection per `_CP_TO_RT_STATUS`.
    - `workflow_id`: pass-through from CP result.
    - `terminal_state`: `cp_result.final_state` if SUCCESS, else `partial_state`
      (drained) or `{}` (failed without partial). C-RT-09 invariant: dict, never
      None.
    - `audit_ledger_head_hash`: from `shutdown_report.audit_ledger_head_hash`.
      Spec C-RT-09 says "always present"; in practice may be empty string at
      v1.4 if no audit-ledger entries were written (state-ledger entries from
      the CP driver land on `ctx.ledger_writer`, a distinct writer from
      `ctx.audit_writer`). Class 3 informational drift; non-blocking — the
      U-RT-49 ledger-entry AC verifies via `read_ledger(handle)`, not via
      this field.
    - `trace_ids`: empty tuple at v1.4 (driver does not surface root span trace
      IDs through `RunResult`; spec §25 deferred-to-discretion). Class 3
      informational gap; queued for a future runtime + driver coherence pass.
    - `cost_attribution`: empty tuple — `U-OD-21` (`SpanCostRecord` rollup keys)
      is HALTED Class 1 per `.harness/class_1_tension_u_od_21_span_cost_record_
      missing_rollup_keys.md`. Cost attribution AC of U-RT-49 stays STRUCK; the
      empty tuple is the carry-forward shape.
    - `failure_cause`: populated when status is "failed"; tags through
      `cp_result.fail_class`.
    """
    status = _CP_TO_RT_STATUS[cp_result.status]

    if cp_result.status is _CpRunStatus.SUCCESS:
        terminal_state: dict[str, Any] = dict(cp_result.final_state or {})
    elif cp_result.status is _CpRunStatus.DRAINED:
        terminal_state = dict(cp_result.partial_state or {})
    else:
        terminal_state = dict(cp_result.partial_state or {})

    failure_cause: FailureCause | None = None
    if timed_out:
        # U-RT-44 AC #2 typed-timeout branch — surface
        # `RT-FAIL-DRAIN-TIMEOUT` per C-RT-14 even though status is
        # `drained` (DRAINED-with-timeout-cause). Caller introspects
        # `failure_cause.runtime_fail_class` to disambiguate
        # graceful-drain from timeout-forced-drain.
        failure_cause = FailureCause(
            runtime_fail_class="RT-FAIL-DRAIN-TIMEOUT",
            detail=(
                "in-flight workflow step did not complete within "
                "`RuntimeConfig.drain_timeout_seconds`; the driver thread "
                "was not cancelled — spec §11 invariant ('in-flight step "
                "may be in inconsistent state') applies"
            ),
            validator_fail_class=None,
        )
    elif status == "failed":
        failure_cause = FailureCause(
            runtime_fail_class="RT-FAIL-WORKFLOW",
            detail=(
                f"workflow execution returned status={cp_result.status.value!r} "
                f"with fail_class={cp_result.fail_class!r}"
            ),
            validator_fail_class=cp_result.fail_class,
        )

    head_hash: str = shutdown_report.audit_ledger_head_hash or ""

    return RunResult(
        status=status,
        workflow_id=WorkflowID(cp_result.workflow_id),
        terminal_state=terminal_state,
        audit_ledger_head_hash=head_hash,
        trace_ids=(),
        cost_attribution=(),
        failure_cause=failure_cause,
    )


def _default_config() -> RuntimeConfig:
    """Fallback `RuntimeConfig` when caller passes `config=None`.

    Per C-RT-08 §8 "config=None default behavior": materialize
    `RuntimeConfig` from defaults + env vars per C-RT-03 precedence.
    Full env-var ingestion lives at `harness_runtime.config.loader`;
    this fallback is the minimal-defaults form used when no caller-side
    config is supplied. Raises if required fields cannot be resolved.
    """
    from harness_runtime.config.loader import materialize_runtime_config

    return materialize_runtime_config()
