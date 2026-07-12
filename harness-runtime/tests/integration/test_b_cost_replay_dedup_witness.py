"""B-COST-REPLAY-DEDUP-WITNESS — journal_resume completed-run replay does
not double-emit a cost-attribution audit entry (ADR-D6 §1.5 / C-OD-14).

## What this proves, precisely

Initial grounding (R-FS-2 Wave 3 final arc) hypothesized the CP driver's F2
committed-step-prefix skip (`enumerate(steps[resume_at:], ...)`,
`workflow_driver.py:4193`) would keep a replayed `JOURNAL_RESUME` step from
ever re-invoking its dispatcher. **That hypothesis is empirically FALSE for
this engine class**: the driver's `resume_at`-determination `if`/`elif`
chain (`workflow_driver.py` ~3816-3969) branches only on
`SAVE_POINT_CHECKPOINT` / `EVENT_SOURCED_REPLAY` / `RECONCILER_LOOP` /
`WAL_SEGMENT`; `EngineClass.PURE_PATTERN_NO_ENGINE` (`JOURNAL_RESUME`) has
no branch, so `resume_at` stays `0` and every re-drive re-dispatches every
step from scratch — confirmed by instrumented dispatch-call counting during
this arc's build (2 dispatcher invocations across the two
`execute_workflow` calls below, not 1).

**The real mechanism** is one layer down, at the IS state-ledger's
content-addressed write (`harness_is/state_ledger_write.py:append_ledger_entry`,
C-IS-07 §7.1): a write whose `idempotency_key` already exists in the ledger
returns `WriteResult.IDEMPOTENT_NOOP` and is silently dropped — this applies
to every ledger append, including the `RuntimeAuditLedgerWriter.append`
wrap that cost-attribution audit entries go through
(`harness_runtime/lifecycle/audit_writer.py`). The audit entry's
`idempotency_key` there is `f"audit:{tag}:{audit_entry.entry_hash}"`, and
`entry_hash` is a pure SHA-256 over the OD `AuditPayload`'s canonical JSON
(`audit_ledger_types.py:compute_entry_hash`) — **not** timestamped: the cost
projection helper (`cost_record_audit_writer.py:_project_cost_record_to_audit_payload`)
defaults `timestamp=""` (the documented MVP sentinel) and
`attribute_llm_dispatch_cost` never overrides it. So two dispatches of the
identical step (same `span_id` / `workflow_id` / `parent_action_id` / token
counts ⟹ same cost) produce a byte-identical `AuditPayload` ⟹ identical
`entry_hash` ⟹ identical `idempotency_key` ⟹ the second write is recognized
as a duplicate and dropped.

Grounding's other finding stands unmodified: `dedupe_on_replay`
(`harness_od.idempotency_join_dedup`) is confirmed unwired at all four
production cost-emission call sites and plays no role in this outcome — the
IS-layer content-addressed dedup is a *different*, already-satisfied
mechanism for the C-OD-14 "replay must not double-count" invariant.

**Disposition: verified GREEN, no fix.** The invariant holds — via IS-layer
idempotent writes, not the OD replay-disposition join and not a CP-level
re-dispatch guard for this engine class. Neither of the latter two is a
defect: the ledger's content-addressed dedup is the actual, working
exactly-once boundary for audit-ledger appends of any kind, cost included.
See `.harness/r-fs-2-final-closure-implementation-plan-v1.md` §4
`B-COST-REPLAY-DEDUP-WITNESS`.

## Detector validity (mutation-probed)

Two probes run during this arc's build (not committed — ad hoc, deleted
after use):

1. Patching `_determine_resume_at` to always return 0 had NO effect on the
   outcome — confirming it is not on the JOURNAL_RESUME path at all (dead
   end; the true mechanism lies elsewhere, per above).
2. Patching `harness_is.state_ledger_write.append_ledger_entry` to always
   `APPENDED` (removing the idempotency-key dedup check) turned this
   module's positive test RED (`count_after_r2 == 2`, assertion fails) —
   confirming the test is a genuine detector of the real mechanism, not a
   tautology.

The in-file negative control below (`test_journal_resume_fresh_second_run_id_emits_independently`)
is the committed evidence that the exact-count assertions are not vacuously
`==1` regardless of input: two genuinely distinct runs (different `run_id`,
hence different `parent_idempotency_key` propagated into the cost record and
therefore a different `entry_hash`) independently emit 2 entries, not 1.

## Observation layer

Per `test_r100_real_workflow_e2e.py`'s hard-won note: cost-attribution
audit-ledger entries surface on disk as `audit:<tenant>:<hash>` state-ledger
entries (the `cost:<workflow_id>:<step_action_id>` action_id lives inside the
audit entry's `payload`, hashed into `response_hash` — not a literal
top-level `action_id`). For this single-step `PURE_PATTERN_NO_ENGINE`
workflow (no HITL / validator / override), the per-dispatch cost write is the
ONLY audit-thread append, so counting `audit:`-prefixed entries is an exact
proxy for cost-emission count.
"""

from __future__ import annotations

import asyncio
import json
from functools import partial
from pathlib import Path
from typing import Any

import pytest
from harness_core.identity import StepID
from harness_core.persona_tier import PersonaTier
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import execute_workflow
from harness_cp.workflow_driver_types import RunStatus, StepKind, WorkflowStep
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_od.rate_table_v1 import RATE_TABLE_V1
from harness_runtime.bootstrap import run_bootstrap
from harness_runtime.lifecycle.cost_attribution_llm_dispatch import (
    attribute_llm_dispatch_cost,
)

from .conftest import WORKLOAD, build_config

_CHAIN = FallbackChain(
    primary=ProviderCandidate(
        provider="anthropic",
        model="claude-haiku-4-5",
        family=ProviderFamily.ANTHROPIC,
    ),
    same_family=(),
    cross_family=(),
    terminal=None,
)
_DEFAULT_BINDING = ModelBinding(provider="anthropic", model="claude-haiku-4-5")


class _CostFiringDispatcher:
    """Step body invoking the REAL production cost-attribution helper.

    Unlike `test_run_smoke.py`'s `_CostFiringDispatcher` (which hand-composes
    a `SpanCostRecord` for chain-shape verification only), this dispatcher
    calls `attribute_llm_dispatch_cost` itself — the exact function the
    production `RuntimeLLMDispatcher` invokes — so the audit-ledger write
    this test counts is byte-for-byte the real emission path.
    """

    def __init__(self, ctx_holder: dict[str, Any]) -> None:
        self._ctx_holder = ctx_holder

    def dispatch(
        self,
        binding: Any,
        step: WorkflowStep,
        *,
        step_context: Any = None,
    ) -> dict[str, Any]:
        _ = binding
        assert step_context is not None
        ctx = self._ctx_holder["ctx"]
        attribute_llm_dispatch_cost(
            rate_table=RATE_TABLE_V1,
            cost_chain=ctx.cost_chain,
            audit_writer=ctx.audit_writer,
            provider_name="anthropic",
            model="claude-haiku-4-5",
            span_id=f"span-{step.step_id}",
            parent_idempotency_key=step_context.parent_idempotency_key,
            workflow_id=step_context.workflow_id,
            parent_action_id=step_context.parent_action_id,
            input_tokens=10,
            output_tokens=5,
        )
        return {"step_id": str(step.step_id), "ok": True}


class _SingleKindRegistry:
    def __init__(self, dispatcher: Any) -> None:
        self._dispatcher = dispatcher

    def lookup(self, step_kind: Any) -> Any:
        _ = step_kind
        return self._dispatcher


def _manifest(workflow_id: str) -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WORKLOAD,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=TopologyPattern.SINGLE_THREADED_LINEAR,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


def _single_inference_step() -> tuple[WorkflowStep, ...]:
    return (
        WorkflowStep(
            step_id=StepID("step-0"),
            step_kind=StepKind.INFERENCE_STEP,
            step_payload={"index": 0},
        ),
    )


def _count_audit_entries(state_ledger_root: Path) -> int:
    count = 0
    for jsonl in sorted(state_ledger_root.rglob("*.jsonl")):
        for line in jsonl.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if str(entry.get("action_id", "")).startswith("audit:"):
                count += 1
    return count


@pytest.mark.asyncio
async def test_journal_resume_completed_run_retry_does_not_double_emit_cost(
    tmp_path: Path,
    patched_runtime: dict[str, Any],
) -> None:
    """Re-driving a fully-completed JOURNAL_RESUME run (same run_id) emits
    exactly one cost-attribution audit entry, not two — via the IS-layer
    content-addressed idempotent write, per this module's docstring (NOT a
    CP-level re-dispatch guard: the dispatcher genuinely fires twice)."""
    _ = patched_runtime
    config = build_config(tmp_path)
    ctx = await run_bootstrap(config, workload_class=WORKLOAD)
    from opentelemetry.trace import NoOpTracer

    ctx.tracer_provider.get_tracer = lambda _name, /: NoOpTracer()  # type: ignore[attr-defined,method-assign]
    ctx_holder: dict[str, Any] = {"ctx": ctx}
    state_ledger_root = tmp_path / "state_ledger"

    manifest = _manifest("wf-journal-resume-cost")
    steps = _single_inference_step()
    registry = _SingleKindRegistry(_CostFiringDispatcher(ctx_holder))

    def _run() -> Any:
        return execute_workflow(
            manifest_entry=manifest,
            steps=steps,
            run_id="run-journal-resume-cost",
            ctx=ctx,  # type: ignore[arg-type]
            default_model_binding=_DEFAULT_BINDING,
            step_dispatchers=registry,  # type: ignore[arg-type]
        )

    # r1: fresh run — one step dispatches, one cost-attribution entry lands.
    first = await asyncio.to_thread(_run)
    assert first.status is RunStatus.SUCCESS, (
        f"expected SUCCESS, got {first.status}; fail_class={first.fail_class}"
    )
    count_after_r1 = _count_audit_entries(state_ledger_root)
    assert count_after_r1 == 1, (
        f"expected exactly 1 cost-attribution audit entry after the fresh run; got {count_after_r1}"
    )

    # r2: re-drive the COMPLETED run under the SAME run_id (the journal_resume
    # "replay a completed step" scenario). The dispatcher DOES fire again
    # (no CP-level skip for this engine class) but the resulting audit entry
    # is byte-identical to r1's, so the IS ledger's idempotency-key dedup
    # drops it — the count must stay at 1, not double to 2.
    retried = await asyncio.to_thread(_run)
    assert retried.status is RunStatus.SUCCESS, (
        f"expected SUCCESS on completed-run retry, got {retried.status}; "
        f"fail_class={retried.fail_class}"
    )
    count_after_r2 = _count_audit_entries(state_ledger_root)
    assert count_after_r2 == 1, (
        "completed-run retry must not double-emit cost-attribution "
        "(the IS-layer idempotency-key dedup at append_ledger_entry must "
        f"have caught the replayed entry as a duplicate); got count={count_after_r2}"
    )


@pytest.mark.asyncio
async def test_journal_resume_fresh_second_run_id_emits_independently(
    tmp_path: Path,
    patched_runtime: dict[str, Any],
) -> None:
    """Negative control: a DIFFERENT run_id is a genuinely new run, not a
    replay — its cost record carries a different parent_idempotency_key
    (hence a different entry_hash) and must emit its own independent
    cost-attribution entry (proves the ==1 assertions above are not a
    tautology from a broken counter or an over-eager dedup)."""
    _ = patched_runtime
    config = build_config(tmp_path)
    ctx = await run_bootstrap(config, workload_class=WORKLOAD)
    from opentelemetry.trace import NoOpTracer

    ctx.tracer_provider.get_tracer = lambda _name, /: NoOpTracer()  # type: ignore[attr-defined,method-assign]
    ctx_holder: dict[str, Any] = {"ctx": ctx}
    state_ledger_root = tmp_path / "state_ledger"

    manifest = _manifest("wf-journal-resume-cost-control")
    steps = _single_inference_step()
    registry = _SingleKindRegistry(_CostFiringDispatcher(ctx_holder))

    def _run(run_id: str) -> Any:
        return execute_workflow(
            manifest_entry=manifest,
            steps=steps,
            run_id=run_id,
            ctx=ctx,  # type: ignore[arg-type]
            default_model_binding=_DEFAULT_BINDING,
            step_dispatchers=registry,  # type: ignore[arg-type]
        )

    first = await asyncio.to_thread(partial(_run, "run-a"))
    assert first.status is RunStatus.SUCCESS
    second = await asyncio.to_thread(partial(_run, "run-b"))
    assert second.status is RunStatus.SUCCESS

    count = _count_audit_entries(state_ledger_root)
    assert count == 2, (
        f"two distinct run_ids must each independently emit cost-attribution "
        f"(not a replay of one another); got count={count}"
    )
