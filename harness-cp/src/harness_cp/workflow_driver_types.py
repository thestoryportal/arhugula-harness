"""Workflow execution driver types — U-CP-56 + U-RT-59 (Path A).

Implements C-CP-25 §25.2 verbatim:
- `RunStatus` 4-value closed enum
- `RunResult` 7-field record
- `StepKind` 5-value enum (verbatim from CP spec v1.4 §5.2; materialized as a
  named enum at C-CP-25 §25.2 in-session amendment §E 2026-05-20)
- `WorkflowStep` record (in-session amendment §E — step-sequence source
  decoupled from `WorkflowManifestEntry` per operator Path A)
- `StepExecutionContext` 9-field record (NEW at v1.6 Path A as 8-field;
  extended at v1.12 with 9th field `workflow_id` per
  `.harness/class_1_fork_step_execution_context_workflow_id_field_absence.md`
  Path A ratification — per-step parent context surface composed by the
  driver and passed to the `StepDispatcher` Protocol per the U-RT-59
  sub-agent dispatch composer needs + OD-axis cost-attribution audit-write
  wiring per OD spec v1.10 §C-OD-26.6.1 step 2 cite)

Authority:
- `Spec_Control_Plane_v1_4.md` §25.2 (signatures) + §25 in-session amendment §E
- `Spec_Control_Plane_v1_5.md` v1.5 → v1.6 amendment (Path A resolution of
  C-RT-17 StepDispatcher parent-context gap; new §25.2.1 declaring
  `StepExecutionContext` schema)
- `Spec_Harness_Runtime_v1.md` v1.6 §14.7 C-RT-17 (sub-agent dispatch composer
  consumer of `StepExecutionContext`)
- `Implementation_Plan_Control_Plane_v2_11.md` U-CP-56 acceptance criterion #1
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import Any, Literal

from harness_as.sandbox_tier import SandboxTier
from harness_core.identity import StepID
from harness_is.state_ledger_entry_schema import Actor, BranchMetadata, Identifier
from pydantic import BaseModel, ConfigDict

from harness_cp.cp_shared_types import AgentRole
from harness_cp.gate_level_rule import GateLevel
from harness_cp.hitl_placement import HITLPlacement
from harness_cp.pause_resume_protocol_types import PauseSnapshot


class RunStatus(StrEnum):
    """The 4 terminal statuses of a driver run (C-CP-25 §25.2).

    Closed at cardinality 4 per the §25.2 enum declaration. Extension would
    require a Workflow §4.1.2 Class-2 revision of §25.2.

    `DRAINED` is the terminal-status observable that replaces a `DRAINED`
    lifecycle event class (no such event class exists in the §5.1 closed-at-8
    taxonomy per CP spec v1.4 §25 + Path B operator decision).
    """

    SUCCESS = "success"
    DRAINED = "drained"
    FAILED = "failed"
    PARTIAL = "partial"  # reserved for future multi-step error modes
    PAUSED = "paused"  # U-RT-89 (v2.20) — workflow paused via PauseResumeProtocol;
    # `pause_snapshot` populated for caller-side resume invocation. Additive
    # minor-version evolution per runtime spec v1.21 §14.14.5 invariant 4.


class StepKind(StrEnum):
    """The 6 step kinds (CP spec §5.2; materialized at §25.2 per in-session
    amendment §E 2026-05-20; extended to 6 at CP spec v1.39).

    Member string values match §5.2's verbatim listing:
    `declarative-step / inference-step / tool-step / HITL-step /
    sub-agent-dispatch / managed-agents`.

    Closed at cardinality 6 — extension is a Workflow §4.1.2 Class-2 revision
    of §5.2. The `managed-agents` member is the operator-ratified (2026-06-17,
    Option B) R-FS-1 arc-M extension (CP spec v1.39); it is dispatched by the
    runtime `ManagedAgentsStepDispatcher` (C-RT-28 §14.20) to a vendor-run
    Managed Agents session — distinct from `sub-agent-dispatch`, whose
    dispatcher orchestrates a harness-run child loop.
    """

    DECLARATIVE_STEP = "declarative-step"
    INFERENCE_STEP = "inference-step"
    TOOL_STEP = "tool-step"
    HITL_STEP = "HITL-step"
    SUB_AGENT_DISPATCH = "sub-agent-dispatch"
    MANAGED_AGENTS = "managed-agents"


class WorkflowStep(BaseModel):
    """A single step in the workflow's step sequence (C-CP-25 §25.2
    in-session amendment §E).

    Step sequence is decoupled from `WorkflowManifestEntry`: the manifest
    carries config (engine class, topology, layer budgets, fallback chain,
    HITL placements, per-step overrides), the step sequence carries the
    declarative body steps.

    `step_payload` is opaque to the driver — consumed by the injected
    `step_dispatcher` per the per-axis composition pattern.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    step_id: StepID
    step_kind: StepKind
    step_payload: Mapping[str, Any]


class RunResult(BaseModel):
    """The terminal return shape of a driver run (C-CP-25 §25.2).

    Per-field semantics per §25.2 + §25.3:
    - `status == SUCCESS` → `final_state` populated; `partial_state` /
      `terminal_step_index` / `fail_class` null.
    - `status == DRAINED` → `partial_state` populated; `terminal_step_index`
      populated; `final_state` null; `fail_class` null.
    - `status == FAILED` → `fail_class` populated; one of `partial_state` /
      `terminal_step_index` populated per failure site; `final_state` null.
    - `status == PARTIAL` → reserved.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, arbitrary_types_allowed=True)

    workflow_id: str
    run_id: str
    status: RunStatus
    terminal_step_index: int | None = None
    partial_state: Mapping[str, Any] | None = None
    final_state: Mapping[str, Any] | None = None
    fail_class: str | None = None
    pause_snapshot: PauseSnapshot | None = None
    """U-RT-89 (v2.20) — pause snapshot when `status == PAUSED`.

    Populated by the workflow_driver per-step pre-entry pause-trigger detection
    branch when `ctx.pause_resume_protocol is not None` and
    `ctx.pause_requested_flag.is_set()` — the captured `PauseSnapshot` is
    threaded back to the caller via this field so that a follow-on
    `execute_workflow(..., pause_snapshot_input=<captured>)` invocation can
    resume. `None` for all non-PAUSED returns per runtime spec v1.21 §14.14.5
    invariant 4. Additive minor-version evolution.
    """


class StepExecutionContext(BaseModel):
    """Per-step parent context surface composed by the driver and passed to
    the `StepDispatcher` Protocol (NEW at C-CP-25 v1.6 Path A — resolves the
    C-RT-17 Class 1 fork on StepDispatcher Protocol parent-context gap).

    The driver composes one `StepExecutionContext` per step from run-level
    state + per-step-iteration state. The dispatcher consumes it as a
    keyword-only `step_context` parameter. The `StepDispatcher` Protocol does
    NOT introspect step-payload content via this surface — `step_context`
    carries metadata about the step's execution environment, NOT step body
    content. This preserves the C-CP-25 §25.3.3.4 "step body opaque to
    driver" invariant.

    Field semantics:

    - ``workflow_id`` (NEW at v1.12 per CP spec v1.12 §25.2.1): the parent
      workflow's identifier sourced from ``manifest_entry.workflow_id`` at
      the driver §25.3.3.4 composition site. Required (NOT Optional).
      Discrete typed surface for consumer dispatchers + OD-axis cost-
      attribution audit-write wiring per OD spec v1.10 §C-OD-26.6.1 step 2
      cite (`cost:<workflow_id>:<step_action_id>` audit action_id pattern).
      The value is already in driver scope at the existing composition site
      where ``parent_action_id`` is composed via string interpolation from
      the same value (``f"workflow:{workflow_id}:step:{step_index}"``).
    - ``parent_action_id``: composed by the driver per the existing pattern
      ``ActionID(f"workflow:{workflow_id}:step:{step_index}")`` (per
      ``workflow_driver.py:_append_step_ledger_entry``).
    - ``parent_gate_level``: the seed input for the C-CP-12 §12.2 sub-agent
      gate-level composition formula. At v1.20 (post Reading A absorption
      per `.harness/class_1_fork_h_t_cp_19_default_gate_level_spec_extension.md`):
      sourced from ``manifest_entry.default_gate_level`` when surfaced;
      falls back to ``GateLevel.AUTO`` (the v1.6 MVP default; matches the
      harness solo-developer persona) when the field is None. Composition
      site at ``workflow_driver.py`` reads ``default_gate_level if not
      None else GateLevel.AUTO`` per CP spec v1.20 §6.1.Y. Per C-CP-12
      §12.4: source-of-the-seed implementation-discretion-bounded at v1.6
      was lifted to operator-surfaceable at v1.20.
    - ``parent_sandbox_tier``: the seed input for the C-AS-11 monotonic-
      ascension composition at sub-agent dispatch. v1.6 MVP default:
      ``SandboxTier.TIER_1_PROCESS`` (lowest tier; consistent with existing
      ``sandbox_tier_floor`` pattern's lowest tier). v1.7+ operator-surfaced
      per manifest extension.
    - ``parent_actor``: from ``ctx.ledger_writer.actor`` (LedgerWriter
      construction-time identity per ``state_ledger.py:71``).
    - ``parent_entry_hash``: the hash of the prior-step audit-ledger entry
      per C-CP-13 §13.5 ``LedgerEntryRef.entry_hash``. v1.6 MVP: empty
      string sentinel — the audit chain extends naturally via the parent
      ``LedgerWriter`` sharing at C-RT-17 §14.7.4 v1.6 MVP child-context
      sharing discipline; explicit entry-hash propagation deferred to v1.7+
      arc that adds ``last_appended_entry_hash`` to the LedgerWriter API.
    - ``parent_idempotency_key``: derived per the existing
      ``_compute_step_idempotency_key(run_idempotency_key, step_index)``
      helper at ``workflow_driver.py:222``.
    - ``tenant_id``: sourced from ``ctx.tenant_id`` at the workflow_driver
      composition site (HarnessContext exposes the value as a computed
      property reading ``self.config.tenant_id`` so DriverContext is
      structurally satisfied without duplicating storage). ``None`` =
      single-tenant (the v1.6 MVP default; preserved at audit-writer via
      the ``_SINGLE_TENANT_TAG`` sentinel); operator-supplied non-None
      values flow through the 4-substep audit composition unchanged. The
      v1.6 MVP hardcode at workflow_driver.py was lifted as a binding fix
      (NOT a WorkflowManifestEntry schema extension — tenant_id is per-
      deployment scoping sourced from RuntimeConfig, not per-workflow
      operator-surfaced).
    - ``step_index``: the per-iteration loop variable from the driver's
      ``for step_index, step in enumerate(steps[resume_at:], start=resume_at)``.

    The deferred-to-MVP-default fields originally enumerated 4 at v1.6
    (``parent_gate_level``, ``parent_sandbox_tier``, ``parent_entry_hash``,
    ``tenant_id``). ``parent_gate_level`` was lifted at v1.20 per the CP-19
    Reading A fork resolution; ``tenant_id`` was lifted as a binding fix
    (per-deployment scoping via RuntimeConfig — not a WorkflowManifestEntry
    schema extension). The remaining 2 (``parent_sandbox_tier``,
    ``parent_entry_hash``) preserve the v1.6 anti-extension invariant
    pending their respective retirement events. The driver-composed fields
    (``workflow_id``, ``parent_action_id``, ``parent_actor``,
    ``parent_idempotency_key``, ``step_index``) follow the existing
    deterministic patterns.

    Branch-context extension (NEW at v1.32 §25.11/§25.12/§25.14, U-CP-81):

    - ``branch_index`` (Optional, default ``None``): the 0-based fan-out
      ordinal of a branch under a non-linear topology strategy. ``None`` on
      the ``SINGLE_THREADED_LINEAR`` path — the linear strategy composes no
      branch child context (regression-safe; no branch field is set on the
      linear path). Composed at branch-spawn by
      ``compose_branch_child_context``.
    - ``agent_role`` (Optional, default ``None``): the branch ``AgentRole``
      (the CP-half of the §25.14 role seam). ``None`` on the linear path.
      The runtime dispatch read (U-RT-114) makes per-role model routing
      effective; the per-role *prompt* is the distinct B4 child-arc.

    Branch identity is ``(parent_action_id, branch_index)`` where
    ``parent_action_id`` is the spawning step's ``action_id`` set verbatim by
    ``compose_branch_child_context``. Per IS spec v1.8 §5.4, ``action_id`` is
    globally unique (IS §5), so that pair uniquely identifies a branch even
    under nested fan-out with NO ``branch_path`` at the causality key
    (``branch_path`` is the distinct CP §25.16 idempotency-key composition,
    U-CP-83).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    workflow_id: str
    parent_action_id: str
    parent_gate_level: GateLevel
    parent_sandbox_tier: SandboxTier
    parent_actor: Actor
    parent_entry_hash: str
    parent_idempotency_key: str
    tenant_id: str | None
    step_index: int
    branch_index: int | None = None
    agent_role: AgentRole | None = None
    hitl_placements: tuple[HITLPlacement, ...] = ()
    """The workflow's declared HITL placements (C-CP-17 §17.3
    `WorkflowManifestEntry.hitl_placements`), surfaced onto the per-step
    execution context at workflow-binding time so the runtime wrap-time HITL
    gate composer (runtime §14.8.2 step 1) can read them per-step.

    R-FS-1 `B-HITL-PLACEMENT-PER-STEP-PRODUCER` addition. The driver composes
    this from `manifest_entry.hitl_placements` at every per-step
    `StepExecutionContext` construction (linear + the 5 non-linear strategies;
    branch children inherit it via `compose_branch_child_context`'s
    `model_copy`). Default `()` → no placement declared → the composer
    short-circuits to the inner dispatcher (byte-identical to pre-arc; a gate
    fires only when the operator declares a placement in the manifest).

    Workflow-scoped (identical for every step of a workflow), NOT a per-step
    override — placements are workflow config per C-CP-25 §25.2, so this rides
    `StepExecutionContext` (the per-step execution metadata), NOT
    `StepEffectiveBinding` (whose `model_dump` feeds the per-step override
    outcome-hash). The per-step `StepOverride.hitl_placement` override fold is
    the separate follow-on arc `B-HITL-PLACEMENT-PER-STEP-OVERRIDE-FOLD`."""


def compose_branch_child_context(
    parent_context: StepExecutionContext,
    *,
    branch_index: int,
    agent_role: AgentRole,
) -> StepExecutionContext:
    """Compose a branch child ``StepExecutionContext`` at branch-spawn.

    C-CP-25 §25.11 (a branch = a sub-sequence dispatched under a child
    context) + §25.12 (the causality fields the buffered drain + write-cadence
    consume) + §25.14 (the ``AgentRole`` carry, CP-half of the role seam).
    Runtime spec v1.48 §2.2(d) (branch ``StepExecutionContext`` composition
    deliverable — discharged CP-side here). The ``SINGLE_THREADED_LINEAR`` path
    composes no branch child context — it uses the existing per-step context
    verbatim (``branch_index``/``agent_role`` stay ``None``).

    The child carries:

    - ``parent_action_id``: the spawning step's ``action_id`` set **VERBATIM**
      (``parent_context.parent_action_id``, the spawning context's identity).
      Branch causality is ``(parent_action_id, branch_index)``; per IS spec
      v1.8 §5.4 the persisted carrier's ``parent_action_id`` "resolves to a
      prior persisted entry's ``action_id``" and ``action_id`` is globally
      unique per IS §5, so ``(parent_action_id, branch_index)`` uniquely
      identifies a branch **even under NESTED fan-out** with **no
      ``branch_path``** at this causality key. (``branch_path`` is the distinct
      CP-side §25.16 *idempotency-key* composition — U-CP-83 — NOT the
      causality key; and Route X — encoding causality into ``action_id`` — was
      rejected at the B1 branch-causality fork.) Nested-uniqueness therefore
      rests on the spawning step's ``action_id`` being globally unique, which
      the branch-step ``action_id`` composition (U-CP-82+) must honor — this
      composer does not synthesize identity, it passes the spawning
      ``action_id`` through.
    - ``branch_index``: the 0-based fan-out ordinal (the local drain order
      key, U-CP-82; unique per ``parent_action_id`` per IS §5.4). Must be
      ``>= 0`` per IS spec v1.8 §5.4.
    - ``agent_role``: the per-worker role (the runtime read U-RT-114 makes
      per-role model routing effective).
    - ``parent_gate_level``: descended per C-CP-12 §12.2 — the child gate-level
      descends monotonically (``<= parent``). Equality is the valid §12.2
      default (mirrors ``dispatch_sub_agent``'s no-override default); the
      gate-level seed for the branch's own sub-agents is therefore the
      spawning context's gate level, never an ascent.

    All other fields are inherited from ``parent_context`` (``workflow_id``,
    ``parent_sandbox_tier``, ``parent_actor``, ``parent_entry_hash``,
    ``parent_idempotency_key``, ``tenant_id``, ``step_index``); the
    branch-scoped idempotency key is composed downstream (U-CP-83).
    """
    if branch_index < 0:
        msg = f"branch_index must be >= 0 (IS spec v1.8 §5.4); got {branch_index}"
        raise ValueError(msg)
    return parent_context.model_copy(
        update={
            # IS spec v1.8 §5.4: the spawning step's action_id VERBATIM (no
            # branch_path — action_id global uniqueness per IS §5 makes
            # (parent_action_id, branch_index) unique under nested fan-out).
            "parent_action_id": parent_context.parent_action_id,
            "branch_index": branch_index,
            "agent_role": agent_role,
            # C-CP-12 §12.2 monotonic descent — child <= parent; equality is
            # the valid default (dispatch_sub_agent's no-override default).
            "parent_gate_level": parent_context.parent_gate_level,
        }
    )


def _require_branch(branch_context: StepExecutionContext) -> int:
    """Return the branch ``branch_index``, rejecting a linear (non-branch) context.

    ``compose_branch_step_action_id`` and ``compose_branch_path`` are
    branch-only composers — a ``SINGLE_THREADED_LINEAR`` per-step context
    (``branch_index is None``) uses the flat ``action_id`` + the plain
    ``sha256(run_idempotency_key, step_index)`` idempotency key instead. Passing
    a linear context here is a caller error, not a silent fall-through.
    """
    if branch_context.branch_index is None:
        msg = (
            "branch composer requires a branch child context "
            "(branch_index set); got a linear (SINGLE_THREADED_LINEAR) context"
        )
        raise ValueError(msg)
    return branch_context.branch_index


def compose_branch_step_action_id(
    branch_context: StepExecutionContext,
    local_step_index: int,
) -> str:
    """Compose a globally-unique ``action_id`` for a step running inside a branch.

    C-CP-25 §25.12 + the U-CP-81 forward obligation: a step inside a branch must
    NOT reuse the flat ``workflow:{wf}:step:{N}`` ``action_id`` shape — N
    sibling branches at the same declared ``step_index`` would collide,
    breaking the IS §5 global-``action_id``-uniqueness invariant. The branch
    identity ``(parent_action_id, branch_index)`` is globally unique (IS spec
    v1.8 §5.4: ``parent_action_id`` is the spawning step's globally-unique
    ``action_id`` set verbatim), so embedding it yields a globally-unique
    branch-step ``action_id``:

        ``{parent_action_id}:branch:{branch_index}:step:{local_step_index}``

    e.g. branch 0's step 7 under the fan-out at ``workflow:wf-1:step:3`` →
    ``workflow:wf-1:step:3:branch:0:step:7``. The shape composes recursively
    under nested fan-out (the inner spawning step's ``action_id`` is itself a
    branch-step ``action_id``), so global uniqueness holds at every depth.

    This is the distinct ``action_id`` composition — separate from both the
    causality key ``(parent_action_id, branch_index)`` (no path) and the
    §25.16 idempotency ``branch_path`` (``compose_branch_path``). Raises
    ``ValueError`` on a linear context (use the flat shape there instead).
    """
    branch_index = _require_branch(branch_context)
    return f"{branch_context.parent_action_id}:branch:{branch_index}:step:{local_step_index}"


def compose_branch_path(branch_context: StepExecutionContext) -> str:
    """Compose the §25.16 ``branch_path`` for the branch-scoped idempotency key.

    C-CP-25 §25.16: under fan-out, N branches at the same declared
    ``step_index`` would collapse to one ledger entry under the IS writer's
    ``idempotency_key``-only dedup (C-IS-07 §7.5) unless ``branch_path`` enters
    the idempotency-key composition. ``branch_path`` derives from the branch
    identity ``(parent_action_id, branch_index)``:

        ``{parent_action_id}:{branch_index}``

    ``parent_action_id`` is globally unique per IS §5.4, so ``branch_path`` is
    unique under nested fan-out. This is the distinct *idempotency-key*
    composition — NOT the causality key (no path) and NOT the ``action_id``
    (``compose_branch_step_action_id``, which additionally carries the
    per-branch step ordinal). Raises ``ValueError`` on a linear context (the
    linear path composes ``sha256(run_idempotency_key, step_index)`` with no
    ``branch_path``).
    """
    branch_index = _require_branch(branch_context)
    return f"{branch_context.parent_action_id}:{branch_index}"


def compose_branch_metadata(
    branch_context: StepExecutionContext,
    *,
    terminal_status: Literal["cancelled", "completed", "timed_out"] | None = None,
) -> BranchMetadata:
    """Compose the `branch_metadata` IS sidecar carrier for a branch entry (U-CP-84).

    C-CP-25 §25.13 (the Route-Y producer obligation — the CP `WorkflowDriver` is
    the producer that composes `branch_metadata` at branch-spawn + termination) +
    IS spec v1.8 §5.4 (the carrier shape U-IS-19 authored). The branch causality
    is read **verbatim** from the branch child context's identity:

    - ``parent_action_id`` = ``branch_context.parent_action_id`` (the spawning
      step's globally-unique ``action_id``, set verbatim by
      ``compose_branch_child_context``).
    - ``branch_index`` = the branch's 0-based fan-out ordinal.

    ``(parent_action_id, branch_index)`` uniquely identifies a branch even under
    nested fan-out (IS §5.4: ``action_id`` is globally unique per IS §5) — no
    ``branch_path`` at the causality carrier.

    ``terminal_status`` is the branch's **dispatch-boundary terminal disposition**
    and is **supplied by the caller**, not decided here: per-step entries pass the
    default ``None`` (causality only); a branch's terminal entry passes one of
    ``{cancelled, completed, timed_out}`` (U-CP-85's cascade logic decides *which*;
    U-CP-84 only persists the value it is handed). The carrier's ``Literal`` type
    forecloses ``failed`` — a ran-and-errored branch's terminal entry is
    ``completed`` (dispatch-boundary, not step-outcome; its step failure lives at
    that step's own ordinary entry per CP §25.15.2 obl. 3).

    Raises ``ValueError`` on a linear (``SINGLE_THREADED_LINEAR``) context — the
    linear path composes no ``branch_metadata`` (it stays the carrier default
    ``None``; ``_append_step_ledger_entry`` is byte-identical).
    """
    branch_index = _require_branch(branch_context)
    return BranchMetadata(
        parent_action_id=Identifier(branch_context.parent_action_id),
        branch_index=branch_index,
        terminal_status=terminal_status,
    )


def compose_branch_terminal_action_id(branch_context: StepExecutionContext) -> str:
    """Compose the globally-unique ``action_id`` for a branch's **fresh terminal entry** (U-CP-84).

    Runtime spec v1.48 §2.2(c) + IS spec v1.8 §5.4 append-only invariant: a
    branch's terminal disposition is written at a **fresh terminal entry**
    appended at the barrier drain — **never** by mutating an already-written step
    entry (mutation would re-hash a persisted entry and break the IS §6.3 chain).
    That terminal marker needs its own globally-unique ``action_id``, distinct
    from every per-step branch ``action_id`` (``:step:{n}``):

        ``{parent_action_id}:branch:{branch_index}:terminal``

    e.g. the terminal marker for branch 0 of the fan-out at
    ``workflow:wf-1:step:3`` → ``workflow:wf-1:step:3:branch:0:terminal``. Global
    uniqueness rests on ``parent_action_id`` being the spawning step's
    globally-unique ``action_id`` (IS §5.4); ``:terminal`` cannot collide with any
    ``:step:{int}`` suffix. Raises ``ValueError`` on a linear context.
    """
    branch_index = _require_branch(branch_context)
    return f"{branch_context.parent_action_id}:branch:{branch_index}:terminal"


def compose_branch_terminal_path(branch_context: StepExecutionContext) -> str:
    """Compose the ``branch_path`` for a branch's **terminal-entry** idempotency key (U-CP-84).

    The terminal marker's ``idempotency_key`` must be distinct from every
    per-step ``idempotency_key`` of the same branch, or the IS writer's
    ``idempotency_key``-only dedup (C-IS-07 §7.5) would drop the terminal entry as
    an idempotent no-op and the persisted disposition would silently vanish (the
    arc-9 dedup-collision defect class). The step keys derive from the plain
    ``compose_branch_path`` (``{parent_action_id}:{branch_index}``); the terminal
    key derives from a ``:terminal``-suffixed distinct path:

        ``{parent_action_id}:{branch_index}:terminal``

    Because the path string differs from every step's ``branch_path``, the
    composed ``sha256(run_idempotency_key, step_index, branch_path)`` differs
    regardless of ``step_index`` — the terminal key cannot collide with a step
    key. This is the distinct *idempotency-key* composition — NOT the causality
    key and NOT the ``action_id``. Deterministic + branch-scoped so resume-
    terminality (U-CP-85 obl. 7) can reconstruct it. Raises ``ValueError`` on a
    linear context.
    """
    branch_index = _require_branch(branch_context)
    return f"{branch_context.parent_action_id}:{branch_index}:terminal"


__all__ = [
    "RunResult",
    "RunStatus",
    "StepExecutionContext",
    "StepKind",
    "WorkflowStep",
    "compose_branch_child_context",
    "compose_branch_metadata",
    "compose_branch_path",
    "compose_branch_step_action_id",
    "compose_branch_terminal_action_id",
    "compose_branch_terminal_path",
]
