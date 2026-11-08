"""CP v1.130 §25.11.1 — `derive_worker_plan`, the manifest selection field and its snapshot carrier.

Unit witnesses for the pure parser (§25.11.1.3), the W10 manifest rule and the W6c snapshot leg.
The driver-level W1-W9 witnesses run through `execute_workflow` in the orchestrator test files.
"""

from __future__ import annotations

from typing import Any

import pytest
from harness_core import PersonaTier, StepID, WorkloadClass
from harness_cp.cross_family_fallback_chain import FallbackChain, ProviderCandidate, ProviderFamily
from harness_cp.engine_class import EngineClass
from harness_cp.pause_resume_protocol_types import FanOutResumeState
from harness_cp.sub_agent_brief import SubAgentBrief, compute_brief_summary_hash
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.worker_plan import WorkerPlanInvalid, WorkerSelection, derive_worker_plan
from harness_cp.workflow_driver_types import StepKind, WorkflowStep
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from pydantic import ValidationError

_BRIEF: dict[str, Any] = {
    "objective": "Summarize the lead's findings.",
    "output_format": {"schema_kind": "free_text"},
    "guidance": "Be brief.",
    "task_boundaries": {"in_scope": ["a"], "out_of_scope": [], "termination_criteria": ["done"]},
}


def _step(step_id: str, kind: StepKind = StepKind.TOOL_STEP) -> WorkflowStep:
    return WorkflowStep(step_id=StepID(step_id), step_kind=kind, step_payload={"declared": step_id})


_POOL = (_step("a"), _step("b"), _step("c", StepKind.SUB_AGENT_DISPATCH))


def _lead(plan: object) -> list[tuple[str, int, SubAgentBrief | None]]:
    derived = derive_worker_plan(WorkerSelection.LEAD_PLAN, {"worker_plan": plan}, _POOL)
    return [(str(a.step.step_id), a.declared_index, a.brief) for a in derived.assignments]


def test_declared_pool_ignores_a_worker_plan_key() -> None:
    """W1 parser leg: DECLARED_POOL is the whole pool in declared order, never the output's plan."""
    derived = derive_worker_plan(
        WorkerSelection.DECLARED_POOL, {"worker_plan": [{"worker": "c", "brief": _BRIEF}]}, _POOL
    )
    assert [(str(a.step.step_id), a.declared_index, a.brief) for a in derived.assignments] == [
        ("a", 1, None),
        ("b", 2, None),
        ("c", 3, None),
    ]


def test_lead_plan_selects_orders_and_keeps_declared_identity() -> None:
    """W2 parser leg: plan order is kept and `declared_index` is the declaration's, not the plan's."""
    assert _lead([{"worker": "b"}, {"worker": "a"}]) == [("b", 2, None), ("a", 1, None)]


def test_lead_brief_hash_is_computed_never_supplied() -> None:
    """W3 parser leg: the lead brief is parsed and its `summary_hash` has one source."""
    [(worker, index, brief)] = _lead([{"worker": "c", "brief": _BRIEF}])
    assert (worker, index) == ("c", 3)
    assert brief is not None
    assert brief.objective == _BRIEF["objective"]
    assert brief.summary_hash == compute_brief_summary_hash(brief)
    assert len(brief.summary_hash) == 64


def test_empty_plan_is_a_valid_plan() -> None:
    """W5 parser leg: an empty sequence is zero assignments, not invalid and not "all workers"."""
    assert _lead([]) == []


@pytest.mark.parametrize(
    ("output", "reason"),
    [
        ({}, "missing-worker-plan"),
        ({"worker_plan": "a"}, "not-a-sequence"),
        ({"worker_plan": {"worker": "a"}}, "not-a-sequence"),
        ({"worker_plan": ["a"]}, "not-a-sequence"),
        ({"worker_plan": [{}]}, "malformed-assignment"),
        ({"worker_plan": [{"worker": "a", "why": "x"}]}, "malformed-assignment"),
        ({"worker_plan": [{"worker": 1}]}, "malformed-assignment"),
        ({"worker_plan": [{"worker": "a", 2: "x"}]}, "malformed-assignment"),
        ({"worker_plan": [{"worker": "orch"}]}, "unknown-worker:orch"),
        ({"worker_plan": [{"worker": "synthesis"}]}, "unknown-worker:synthesis"),
        ({"worker_plan": [{"worker": "a"}, {"worker": "a"}]}, "duplicate-worker:a"),
        ({"worker_plan": [{"worker": "c"}]}, "missing-brief:c"),
        ({"worker_plan": [{"worker": "a", "brief": _BRIEF}]}, "brief-on-non-subagent:a"),
        ({"worker_plan": [{"worker": "c", "brief": {"objective": "x"}}]}, "malformed-brief:c"),
        ({"worker_plan": [{"worker": "c", "brief": "x"}]}, "malformed-brief:c"),
        (
            {"worker_plan": [{"worker": "c", "brief": {**_BRIEF, "summary_hash": "0" * 64}}]},
            "malformed-brief:c",
        ),
    ],
)
def test_invalid_plan_names_its_reason(output: dict[str, Any], reason: str) -> None:
    """W4 parser leg: every §25.11.1.3(4) reason raises; nothing is skipped or defaulted."""
    with pytest.raises(WorkerPlanInvalid) as caught:
        derive_worker_plan(WorkerSelection.LEAD_PLAN, output, _POOL)
    assert caught.value.reason == reason


_CHAIN = FallbackChain(
    primary=ProviderCandidate(
        provider="anthropic", model="claude-haiku-4-5", family=ProviderFamily.ANTHROPIC
    ),
    same_family=(),
    cross_family=(),
    terminal=None,
)


def _manifest(topology: TopologyPattern, selection: WorkerSelection) -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id="wf",
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=topology,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
        worker_selection=selection,
    )


@pytest.mark.parametrize("topology", list(TopologyPattern))
def test_lead_plan_requires_an_orchestrator_topology(topology: TopologyPattern) -> None:
    """W10: LEAD_PLAN validates only on ORCHESTRATOR_WORKERS / HIERARCHICAL_DELEGATION."""
    assert _manifest(topology, WorkerSelection.DECLARED_POOL).worker_selection is (
        WorkerSelection.DECLARED_POOL
    )
    if topology in (TopologyPattern.ORCHESTRATOR_WORKERS, TopologyPattern.HIERARCHICAL_DELEGATION):
        assert _manifest(topology, WorkerSelection.LEAD_PLAN).worker_selection is (
            WorkerSelection.LEAD_PLAN
        )
    else:
        with pytest.raises(ValidationError, match="requires an orchestrator topology"):
            _manifest(topology, WorkerSelection.LEAD_PLAN)


def _resume_state(**extra: Any) -> FanOutResumeState:
    return FanOutResumeState(
        orchestrator_output={"o": 1},
        orchestrator_step_id="orch",
        branches=(),
        worker_count=2,
        **extra,
    )


def test_resume_state_selection_round_trips_and_old_snapshots_stay_byte_identical() -> None:
    """W6c snapshot leg: DECLARED_POOL dumps exactly as a pre-v1.130 carrier (so its snapshot
    hash is unchanged) and reads back as DECLARED_POOL; LEAD_PLAN is dumped and hash-covered."""
    declared = _resume_state().model_dump(mode="json")
    assert "worker_selection" not in declared
    assert FanOutResumeState.model_validate(declared).worker_selection is (
        WorkerSelection.DECLARED_POOL
    )
    lead = _resume_state(worker_selection=WorkerSelection.LEAD_PLAN).model_dump(mode="json")
    assert lead["worker_selection"] == "lead-plan"
    assert FanOutResumeState.model_validate(lead).worker_selection is WorkerSelection.LEAD_PLAN
