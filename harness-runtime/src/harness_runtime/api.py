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

**Bootstrap landed at U-RT-43; workflow execution deferred to U-RT-44+.**
U-RT-43 wires `run()` → `run_bootstrap()` → ... → execute stub. The
`BootstrapNotYetLandedError` surface is removed; the new stub-call
surface is `WorkflowExecutionNotYetLandedError` (raised post-bootstrap
because workflow execution + shutdown lands at U-RT-44+). The
`WorkflowObject` Protocol grows with `workload_class` (authorized at
the original L8 landing per the line 110-112 docstring note).

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
from typing import Any, Literal, Protocol, runtime_checkable

from harness_core.identity import WorkflowID
from harness_core.workload_class import WorkloadClass
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


class WorkflowExecutionNotYetLandedError(NotImplementedError):
    """Stub-call surface — workflow execution + shutdown lands at U-RT-44+.

    Raised when `run()` has successfully bootstrapped a `HarnessContext`
    (U-RT-43) and reaches the workflow-execution call site. Subclasses
    `NotImplementedError` so generic handlers catch it; the dedicated
    type lets U-RT-44+ remove this surface cleanly when workflow
    execution + drain + shutdown sequence lands.

    Predecessor: `BootstrapNotYetLandedError` (U-RT-42), removed at the
    U-RT-43 landing — the bootstrap surface is no longer a stub.
    """


# ---------------------------------------------------------------------------
# `WorkflowObject` runtime-local Protocol (Option C per spec §8 Risk surface).
# ---------------------------------------------------------------------------


@runtime_checkable
class WorkflowObject(Protocol):
    """Structural workflow-object surface (C-RT-08 Option C resolution).

    Minimum surface CP's lifecycle loop needs at HEAD: a stable
    `workflow_id` identity + a `workload_class` for bootstrap-time
    routing/state-ledger composition. CP's executable workflow primitive
    lives at `WorkflowManifestEntry` (C-CP-06 §6.1) which carries both
    fields; structural conformance is satisfied. Per the original L8
    docstring note: "growth is non-breaking when fields are optional or
    read-only" — `workload_class` is read-only (`@property`), so this
    growth at U-RT-43 is authorized inline.
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
    WorkflowExecutionNotYetLandedError
        Stub-call surface — workflow execution + shutdown lands at
        U-RT-44+. Removed at U-RT-44 landing.
    """
    if not isinstance(workflow, WorkflowObject):
        raise InvalidWorkflowError(
            f"`run()` requires a `WorkflowObject` (with `workflow_id` + "
            f"`workload_class` properties); got {type(workflow).__name__!r}"
        )
    if _run_lock.locked():
        raise ConcurrentRunNotSupported(
            "a `run()` invocation is already in flight in this process; "
            "Track A is bootstrap-per-call (no cached context). Serialize "
            "calls or move to a cached-context entry point (Track B)."
        )
    # Lazy import to keep the api.py → bootstrap edge one-way at type-check
    # time (bootstrap imports from api.py is forbidden; this lazy import
    # plus a TYPE_CHECKING-free api surface prevents the cycle).
    from harness_runtime.bootstrap import run_bootstrap

    async with _run_lock:
        resolved_config = config if config is not None else _default_config()
        _ctx = await run_bootstrap(
            resolved_config,
            workload_class=workflow.workload_class,
        )
        # Workflow execution + drain + shutdown lands at U-RT-44+.
        raise WorkflowExecutionNotYetLandedError(
            f"bootstrap succeeded (HarnessContext frozen at stage 7); "
            f"workflow execution + drain + shutdown body lands at U-RT-44+. "
            f"workflow_id={workflow.workflow_id!r}"
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
