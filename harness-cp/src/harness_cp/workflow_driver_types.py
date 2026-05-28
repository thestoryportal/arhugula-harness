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
from typing import Any

from harness_as.sandbox_tier import SandboxTier
from harness_core.identity import StepID
from harness_is.state_ledger_entry_schema import Actor
from pydantic import BaseModel, ConfigDict

from harness_cp.gate_level_rule import GateLevel
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
    """The 5 step kinds (CP spec v1.4 §5.2 verbatim; materialized at §25.2
    per in-session amendment §E 2026-05-20).

    Member string values match §5.2's verbatim listing:
    `declarative-step / inference-step / tool-step / HITL-step / sub-agent-dispatch`.

    Closed at cardinality 5 — extension is a Workflow §4.1.2 Class-2 revision
    of §5.2.
    """

    DECLARATIVE_STEP = "declarative-step"
    INFERENCE_STEP = "inference-step"
    TOOL_STEP = "tool-step"
    HITL_STEP = "HITL-step"
    SUB_AGENT_DISPATCH = "sub-agent-dispatch"


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
    - ``tenant_id``: ``None`` at v1.6 MVP (stack discipline does not commit
      to multi-tenancy at v1.6 per ``Target_Stack_Commitment_v1.md``;
      v1.7+ extension when multi-tenancy commits — tenant_id sourced from
      future ``HarnessContext.tenant_id`` or ``RuntimeConfig.tenant_id``).
    - ``step_index``: the per-iteration loop variable from the driver's
      ``for step_index, step in enumerate(steps[resume_at:], start=resume_at)``.

    The 4 deferred-to-MVP-default fields (``parent_gate_level``,
    ``parent_sandbox_tier``, ``parent_entry_hash``, ``tenant_id``) are
    documented as deferred at C-RT-17 §14.7 "Deferred to implementation
    discretion". The remaining 5 fields (at v1.12 — was 4 at v1.6) are
    composed deterministically from driver-tracked state per the existing
    patterns: ``workflow_id``, ``parent_action_id``, ``parent_actor``,
    ``parent_idempotency_key``, ``step_index``.
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


__all__ = [
    "RunResult",
    "RunStatus",
    "StepExecutionContext",
    "StepKind",
    "WorkflowStep",
]
