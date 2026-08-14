"""U-RT-155 — `B-71` escalation-token minter and idempotency-key fold (Runtime half).

Implements `Implementation_Plan_Harness_Runtime_v2_63.md` §0.2 against
`Spec_Harness_Runtime_v1.md` v1.121 sites 1/2/3 and `Spec_Control_Plane_v1_119.md`
§0.2 / §0.4 / §0.4(2-bis) / §0.4.3 / §0.5 / §0.6 / §0.12.

**Co-land pin.** U-CP-102 declares the carriers this unit writes into; its witnesses
live at `harness-cp/tests/test_b71_escalation_correlation_carriers_u_cp_102.py`.
Neither unit is independently observable, so neither closes alone.

Also homed here — because the assertion needs a `harness-runtime` import that
`harness-cp`'s test package cannot take — are **U-CP-102 AC 4** (the §0.4.3 three-arm
read order) and **U-CP-102 AC 5** (a persisted echo is never compared against a
recompute); the resolver those criteria constrain is Runtime-owned. The CP record
carries the diagnosis half of AC 14; the end-to-end OVERWRITE assertion is here, for
the same reason.

**The witness for AC 3 is SPLIT BY VENUE, and that is not a convenience.** A
four-way equality on one escalation is unsatisfiable: `_escalate_to_secondary_channel`
is declared `NoReturn` and raises before `hitl.invocation.audit_ledger_entry_id` is
ever assigned — a fact independently pinned in-tree by
`test_b71_escalation_token_rides_the_tracing_export.py`. So the ESCALATION venue
asserts the webhook key, and the SYNC-GATE venue (where the audit write and the span
attribute are both reached) asserts the other three. An unsplit witness would either
fail forever or be quietly weakened to whatever passes.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from typing import Any, cast

import pytest
from harness_core import EntryID
from harness_core.identity import StepID
from harness_cp.hitl_placement import HITLPlacement, HITLPlacementKind, HITLResult
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.hitl_timeout_degradation import WebhookConfig
from harness_cp.pause_resume_protocol_types import WorkflowPauseReason
from harness_cp.pause_state_projection import (
    PauseLocationVariant,
    PreDispatchUniformFallbackOnlyLocation,
    compose_escalation_instance_id,
    pre_dispatch_gate_owning_branch_identity,
)
from harness_cp.validator_framework_types import HITLEscalationBrief
from harness_cp.workflow_driver_types import (
    StepExecutionContext,
    StepKind,
    WorkflowStep,
)
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_is.state_ledger_entry_schema import Identifier as _Identifier
from harness_od.audit_ledger_types import SignatureAlgorithm
from harness_runtime.lifecycle import hitl_gate_composer as _hgc
from harness_runtime.lifecycle.ask_user_question_surface import (
    AskUserQuestionResult,
    AskUserQuestionSurface,
)
from harness_runtime.lifecycle.hitl_gate_composer import (
    HITLPauseRequestedSignal,
    RuntimeHITLGateComposer,
    compose_hitl_action_id,
    resolve_escalation_instance_id,
)
from harness_runtime.lifecycle.webhook_brief_adapter import project_brief_to_payload
from harness_runtime.lifecycle.webhook_delivery_composer import WebhookDeliveryComposer
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-b71-u-rt-155")
_RUN_ID = "run-b71-rt-1"
_PARENT_ACTION_ID = "workflow:wf-b71:step:0"
_GATE = HITLPlacementKind.SUB_AGENT_BOUNDARY
_SYNC_GATE = HITLPlacementKind.PRE_ACTION


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tracing() -> tuple[TracerProvider, InMemorySpanExporter]:
    provider = TracerProvider()
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    return provider, exporter


def _context(
    *,
    branch_index: int | None = 0,
    basis: str | None = None,
    echo: str | None = None,
) -> StepExecutionContext:
    from harness_as.sandbox_tier import SandboxTier
    from harness_core import ActionID
    from harness_cp.gate_level_rule import GateLevel

    return StepExecutionContext(
        workflow_id="wf-b71",
        parent_action_id=ActionID(_PARENT_ACTION_ID),
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=_ACTOR,
        parent_entry_hash="",
        parent_idempotency_key=_Identifier("b71-rt-key"),
        tenant_id=None,
        step_index=0,
        branch_index=branch_index,
        pre_dispatch_escalation_basis=basis,
        pre_dispatch_escalation_instance_id=echo,
    )


def _fanout_context(branch_index: int) -> StepExecutionContext:
    """A fan-out branch context shaped exactly as the CP driver composes it."""
    return _context(
        branch_index=branch_index,
        basis=pre_dispatch_gate_owning_branch_identity(_RUN_ID, branch_index),
    )


class _Surface:
    """Queue-of-canned-results `AskUserQuestionSurface`, mirroring the composer
    record's own mock."""

    def __init__(self, results: list[AskUserQuestionResult]) -> None:
        self._results = list(results)

    async def ask(
        self, prompt: str, options: Sequence[HITLResponse], timeout: float | None
    ) -> AskUserQuestionResult:
        if not self._results:
            raise RuntimeError("surface queue empty")
        return self._results.pop(0)


class _Inner:
    def dispatch(
        self, binding: Any, step: WorkflowStep, *, step_context: StepExecutionContext
    ) -> Mapping[str, Any]:
        return {"inner_dispatched": True}


class _LedgerWriter:
    def __init__(self) -> None:
        self.appends: list[Any] = []

    def append(self, payload: Any, key: Any) -> Any:
        self.appends.append((payload, key))
        return ("dummy-entry-hash", payload, key)


class _AuditWriter:
    def __init__(self) -> None:
        self.appends: list[Any] = []

    def append(self, *, tenant_id: Any, audit_entry: Any) -> Any:
        self.appends.append((tenant_id, audit_entry))
        return ("dummy-write-result", audit_entry)


class _OkResponse:
    status_code = 200
    text = "ok"

    def json(self) -> dict[str, Any]:
        return {}


class _OkHTTPClient:
    """Minimal `httpx.AsyncClient` double — one 200, no retries needed.

    Shape copied from `test_b71_escalation_token_rides_the_tracing_export.py`'s own
    `_OkClient`; the delivery composer enters it as an async context manager.
    """

    async def __aenter__(self) -> _OkHTTPClient:
        return self

    async def __aexit__(self, *_: Any) -> None:
        return None

    async def post(self, *_: Any, **__: Any) -> _OkResponse:
        return _OkResponse()


def _step(step_id: str = "step-0", placements: tuple[HITLPlacement, ...] = ()) -> WorkflowStep:
    step = WorkflowStep(step_id=StepID(step_id), step_kind=StepKind.INFERENCE_STEP, step_payload={})

    class _StepWithPlacements:
        def __init__(self, inner: WorkflowStep) -> None:
            self._inner = inner
            self.hitl_placements = placements

        def __getattr__(self, name: str) -> Any:
            return getattr(self._inner, name)

    return cast(WorkflowStep, _StepWithPlacements(step))


def _webhook(provider: TracerProvider) -> WebhookDeliveryComposer:
    return WebhookDeliveryComposer(
        retry_max_attempts=1,
        http_client_factory=lambda: _OkHTTPClient(),
        tracer_provider=provider,
        webhook_config=WebhookConfig(
            webhook_id="wh-b71-rt",
            endpoint_url="https://example.test/hook",
            timeout=5,
            degradation_mode="fail-closed",
        ),
    )


def _composer(
    provider: TracerProvider,
    *,
    surface: _Surface | None = None,
    applicable: frozenset[HITLPlacementKind] = frozenset({_GATE}),
    ledger_writer: _LedgerWriter | None = None,
    audit_writer: _AuditWriter | None = None,
    webhook: WebhookDeliveryComposer | None = None,
) -> RuntimeHITLGateComposer:
    return RuntimeHITLGateComposer(
        inner=cast(Any, _Inner()),
        applicable_placements=applicable,
        ask_user_question_surface=cast(
            AskUserQuestionSurface, surface if surface is not None else _Surface([])
        ),
        ledger_writer=cast(Any, ledger_writer or _LedgerWriter()),
        audit_writer=cast(Any, audit_writer or _AuditWriter()),
        tracer_provider=provider,
        audit_signing_key_id="harness-runtime-b71-rt",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        procedural_tier_snapshot_resolver=lambda: _Identifier("b" * 64),
        webhook_delivery_composer=webhook,
    )


async def _escalate(
    provider: TracerProvider, ctx: StepExecutionContext
) -> HITLPauseRequestedSignal:
    """Drive the REAL `_escalate_to_secondary_channel` and return its signal."""
    composer = _composer(provider, webhook=_webhook(provider))
    with pytest.raises(HITLPauseRequestedSignal) as raised:
        await composer._escalate_to_secondary_channel(
            parent_action_id=cast(Any, _PARENT_ACTION_ID),
            step=_step("branch-sub"),
            placement=HITLPlacement(position=_GATE),
            palette=frozenset({HITLResponse.APPROVE}),
            escalation_reason="durable_async_cell_synchrony",
            tenant_id=None,
            step_context=ctx,
        )
    return raised.value


# ---------------------------------------------------------------------------
# AC 1 + AC 2 (= U-CP-102 AC 4 + AC 5) — the three-arm read order
# ---------------------------------------------------------------------------


class _ComputeSpy:
    """Records whether the digest function was entered at all."""

    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, basis: str, position: HITLPlacementKind) -> str:
        self.calls += 1
        return compose_escalation_instance_id(basis, position)


# mutation-probe: reorder `resolve_escalation_instance_id` so the BASIS arm is tried
# first (compute, then fall back to the persisted echo).
def test_arm_one_uses_the_persisted_echo_verbatim_without_entering_the_compute_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """§0.4.3 arm 1 — the arm a passing test can most easily FAKE.

    A recompute that happened to agree would satisfy an output-equality assertion
    while violating the contract, so this observes that the compute path is **not
    entered**, not merely that the output matches. The echo is deliberately a value
    the digest could never produce.
    """
    spy = _ComputeSpy()
    monkeypatch.setattr(_hgc, "compose_escalation_instance_id", spy)
    ctx = _context(
        basis=pre_dispatch_gate_owning_branch_identity(_RUN_ID, 0),
        echo="PERSISTED-ECHO-NOT-A-DIGEST",
    )
    assert resolve_escalation_instance_id(ctx, _GATE) == "PERSISTED-ECHO-NOT-A-DIGEST"
    assert spy.calls == 0, (
        "the persisted echo WINS and the compute path must not be entered at all "
        "(§0.4.3 arm 1) — a recompute-then-agree implementation is non-conforming "
        "even when its output happens to match"
    )


def test_arm_two_computes_from_the_basis_when_nothing_is_persisted() -> None:
    ctx = _fanout_context(0)
    assert resolve_escalation_instance_id(ctx, _GATE) == compose_escalation_instance_id(
        pre_dispatch_gate_owning_branch_identity(_RUN_ID, 0), _GATE
    )


def test_arm_three_yields_none_for_a_population_with_no_gate_owning_branch() -> None:
    assert resolve_escalation_instance_id(_context(branch_index=None), _GATE) is None


# mutation-probe: add a `raise` (or an `assert echo == recompute`) comparing the
# persisted echo against a fresh `compose_escalation_instance_id(basis, position)` in
# `resolve_escalation_instance_id`'s arm 1.
def test_a_persisted_echo_is_never_compared_against_a_recompute() -> None:
    """§0.4.3 arm 1's second half, witnessed DIRECTLY because the natural defensive
    implementation is exactly the one the contract forbids.

    A basis may legitimately evolve between mint and resume. Treating the resulting
    divergence as an error converts a benign evolution into a RUN-ENDING failure on a
    gate the operator is still holding — a mismatch is not an error the contract
    defines.
    """
    diverged = _context(
        basis=pre_dispatch_gate_owning_branch_identity("run-DIFFERENT-since-mint", 7),
        echo="a" * 64,
    )
    assert resolve_escalation_instance_id(diverged, _GATE) == "a" * 64, (
        "a recompute that would differ must NOT fail, and must NOT win"
    )


# ---------------------------------------------------------------------------
# AC 4 + AC 8 — the composed key, absent and present, both PINNED
# ---------------------------------------------------------------------------


# mutation-probe: make `compose_hitl_action_id` append the `":"` separator (or an
# empty suffix) even when `escalation_instance_id is None`.
def test_the_composed_key_is_byte_identical_to_pre_arc_when_the_token_is_absent() -> None:
    """§0.12 / v1.121 site 2 — the seam's acceptance criterion, against a pre-arc
    FIXTURE VALUE rather than a shape assertion."""
    pre_arc = "hitl:workflow:wf-b71:step:0:sub-agent-boundary"
    assert str(compose_hitl_action_id(cast(Any, _PARENT_ACTION_ID), _GATE)) == pre_arc
    assert str(compose_hitl_action_id(cast(Any, _PARENT_ACTION_ID), _GATE, None)) == pre_arc


# mutation-probe: change `compose_hitl_action_id`'s present-case to PREFIX the token
# (`f"{escalation_instance_id}:{base}"`) or to re-hash the composed value.
def test_the_token_present_composed_key_matches_the_pinned_output() -> None:
    """§0.4(2-bis) — the OUTPUT is pinned, not merely the inputs.

    Leaving the present-case format open would let two otherwise-compliant
    implementations append, prefix or re-hash the same token and both pass every
    distinctness test — and then a deployment change WHILE A GATE IS UNRESOLVED would
    emit a different `Idempotency-Key` and F2 ledger key for one escalation,
    duplicating the effect the dedup exists to prevent. AC 4 pins the absent case;
    this pins the present one.
    """
    token = compose_escalation_instance_id(
        pre_dispatch_gate_owning_branch_identity(_RUN_ID, 0), _GATE
    )
    assert (
        str(compose_hitl_action_id(cast(Any, _PARENT_ACTION_ID), _GATE, token))
        == f"hitl:workflow:wf-b71:step:0:sub-agent-boundary:{token}"
    ), "appended as a `:`-separated SUFFIX, never truncated, never re-hashed"
    assert len(token) == 64 and token in str(
        compose_hitl_action_id(cast(Any, _PARENT_ACTION_ID), _GATE, token)
    ), "never truncated in the key (§0.4(1))"


# ---------------------------------------------------------------------------
# AC 3 — the fold reaches ALL THREE invocations (split by venue)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_venue_a_the_escalation_webhook_key_carries_the_folded_token(
    tracing: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """Venue (a): the ESCALATION path. `_escalate_to_secondary_channel` is `NoReturn`
    and raises before `hitl.invocation.audit_ledger_entry_id` is assigned, so the span
    attribute is asserted at venue (b) instead — asserting it here would fail forever.
    """
    provider, exporter = tracing
    ctx = _fanout_context(0)
    signal = await _escalate(provider, ctx)
    expected_token = compose_escalation_instance_id(
        pre_dispatch_gate_owning_branch_identity(_RUN_ID, 0), _GATE
    )
    assert signal.brief.escalation_instance_id == expected_token, "step 1 must MINT onto the brief"
    deliver = [s for s in exporter.get_finished_spans() if s.name == "hitl.webhook.deliver"]
    assert deliver, "the escalation did not reach the webhook delivery span at all"
    emitted = (deliver[0].attributes or {}).get("webhook.idempotency_key")
    assert emitted == str(
        compose_hitl_action_id(cast(Any, _PARENT_ACTION_ID), _GATE, expected_token)
    ), "the webhook `Idempotency-Key` must carry the FOLDED key"
    assert emitted != "hitl:workflow:wf-b71:step:0:sub-agent-boundary", (
        "sanity: the key actually WIDENED — otherwise this witness is vacuous"
    )


# mutation-probe: revert the `:1610` invocation inside `_compose_and_persist_audit`
# to the two-argument `compose_hitl_action_id(parent_action_id, placement.position)`
# (the webhook-only widening).
@pytest.mark.asyncio
async def test_venue_b_the_audit_action_id_and_f2_ledger_key_carry_the_same_folded_key(
    tracing: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """Venue (b): the SYNC-GATE path, where the audit write and `:2238` are reached.

    Widening ONLY the webhook call would make CP §0.2's one-identity-family promise
    FALSE in the shipped system, and would leave AC 5's defect witness operating on an
    unwidened audit key so it could never close.
    """
    provider, exporter = tracing
    ledger, audit = _LedgerWriter(), _AuditWriter()
    composer = _composer(
        provider,
        surface=_Surface([AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=1.0)]),
        applicable=frozenset({_SYNC_GATE}),
        ledger_writer=ledger,
        audit_writer=audit,
    )
    ctx = _context(branch_index=0, basis=pre_dispatch_gate_owning_branch_identity(_RUN_ID, 0))
    step = _step("sync-gated", placements=(HITLPlacement(position=_SYNC_GATE),))
    await composer.dispatch(cast(Any, object()), step, step_context=ctx)

    token = compose_escalation_instance_id(
        pre_dispatch_gate_owning_branch_identity(_RUN_ID, 0), _SYNC_GATE
    )
    expected = str(compose_hitl_action_id(cast(Any, _PARENT_ACTION_ID), _SYNC_GATE, token))
    assert token in expected, "sanity: the expected key is the WIDENED one"

    assert audit.appends, "the sync gate must have written an OD audit entry"
    # `entry_core` is the IS-exported `StateLedgerEntryRef` opaque marker (C-IS-10
    # §10.1) — a plain string carrying the F2 entry's identity, i.e. the same composed
    # key. Asserting it here is what proves the CP→OD converted entry rides the SAME
    # identity family as the webhook and the ledger.
    od_ref = str(audit.appends[0][1].payload.entry_core)
    assert od_ref.strip() and od_ref != "None", (
        f"sanity: the OD entry ref is a real value, not an empty default; got {od_ref!r}"
    )
    assert expected in od_ref, (
        "the CP→OD-converted audit entry must carry the folded key — the same key the "
        "F2 writer dedups on, which is where the second peer's HITL entry was being "
        f"dropped; got {od_ref!r}"
    )
    assert (
        audit.appends[0][1].payload.audit_namespace_attrs.get("audit.action_id", expected)
        == expected
    ), "the `audit.*` namespace must not carry an UNWIDENED key beside the widened one"
    assert ledger.appends, "the sync gate must have written an F2 ledger entry"
    f2_payload = ledger.appends[0][0]
    assert str(f2_payload.action_id) == expected
    assert str(f2_payload.idempotency_key) == expected

    attrs = [
        (s.attributes or {}).get("hitl.invocation.audit_ledger_entry_id")
        for s in exporter.get_finished_spans()
    ]
    assert expected in attrs, (
        "the `:2238` span correlation attribute must name the SAME key the audit "
        f"write used, else it joins to nothing; saw {[a for a in attrs if a]!r}"
    )


# ---------------------------------------------------------------------------
# AC 5 — THE DEFECT WITNESS: two peers, distinct keys, both entries survive dedup
# ---------------------------------------------------------------------------


# mutation-probe: make `resolve_escalation_instance_id` return `None`
# unconditionally (blind the fold to the token).
@pytest.mark.asyncio
async def test_two_peers_sharing_a_child_workflow_id_now_produce_distinct_keys(
    tracing: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """The criterion by which `B-71` CLOSES. Anything weaker witnesses the carriers,
    not the fix.

    Both peers escalate before any child run exists, so no dispatched-child `run_id`
    can discriminate them — the fact that falsified this row's first three repair
    attempts. Under C-IS-07 §7.5's KEY-ONLY dedup, one shared key means the second
    peer's HITL audit entry is dropped as an idempotent no-op.
    """
    provider, _exporter = tracing
    keys: list[str] = []
    for branch_index in (0, 1):
        signal = await _escalate(provider, _fanout_context(branch_index))
        token = signal.brief.escalation_instance_id
        assert token is not None
        keys.append(str(compose_hitl_action_id(cast(Any, _PARENT_ACTION_ID), _GATE, token)))

    assert keys[0] != keys[1], (
        "two peer branches at the same parent action, same placement position and "
        "the SAME child_workflow_id must now compose DISTINCT keys"
    )
    assert len(set(keys)) == len(keys) == 2
    # The dedup this closes is key-only: distinct keys ⇒ both entries survive.
    deduped = {k: None for k in keys}
    assert len(deduped) == 2, (
        "under C-IS-07 §7.5 key-only dedup, both peers' HITL audit entries survive "
        "exactly when their keys differ — which is the §0.1 loss closing"
    )


# ---------------------------------------------------------------------------
# AC 6 + AC 11 — the leak bar at this seam, and the ordinal as PROSE only
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_the_pre_hash_basis_never_reaches_the_webhook_body_or_an_exported_span(
    tracing: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """§0.5, asserted at THIS seam specifically — §14.8.8.1 is where the value crosses
    from internal carriage into the webhook payload and the `hitl.webhook.deliver`
    span. After the composer, it is already on an exported carrier.
    """
    provider, exporter = tracing
    basis = pre_dispatch_gate_owning_branch_identity(_RUN_ID, 0)
    signal = await _escalate(provider, _fanout_context(0))
    body = repr(project_brief_to_payload(signal.brief, "k").model_dump(mode="json"))
    assert basis not in body and _RUN_ID not in body, (
        f"the pre-hash basis reached the webhook body: {body!r}"
    )
    for span in exporter.get_finished_spans():
        rendered = repr(dict(span.attributes or {}))
        assert basis not in rendered, f"basis leaked onto span {span.name!r}"
        assert _RUN_ID not in rendered, f"`run_id` leaked onto span {span.name!r}"


# mutation-probe: in `_escalation_operator_surface`, emit the ordinal as a typed value
# (e.g. add `"branch_index": branch_index` to the returned mapping, and project it as
# its own `payload_body` key in `project_brief_to_payload`).
@pytest.mark.asyncio
async def test_the_branch_ordinal_appears_only_as_prose_and_on_no_other_carrier(
    tracing: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """§0.5's ONE scoped carve-out, held to its stated width.

    The exception is exactly as narrow as the council scoped it: prose on
    `branch_context`, and **nothing else**. It is not precedent for structured ordinal
    export, so the ordinal must appear as no typed or parseable field, on no other
    key, and on no exported span attribute.
    """
    provider, exporter = tracing
    signal = await _escalate(provider, _fanout_context(3))
    payload = project_brief_to_payload(
        signal.brief,
        "k",
        **_hgc._escalation_operator_surface(
            signal.brief.escalation_instance_id, _fanout_context(3)
        ),
    )
    body = dict(payload.payload_body)
    assert isinstance(body["branch_context"], str) and "3" in body["branch_context"]
    for key, value in body.items():
        if key == "branch_context":
            continue
        assert value != 3 and value != "3", (
            f"the ordinal must not appear as a typed/parseable value; found on {key!r}"
        )
    assert not any(k in body for k in ("branch_index", "ordinal", "branch")), (
        f"no structured ordinal key may be minted; got {sorted(body)!r}"
    )
    for span in exporter.get_finished_spans():
        for name, value in dict(span.attributes or {}).items():
            assert not (name.endswith("branch_index") or value == 3), (
                f"the ordinal reached exported span attribute {name!r}"
            )


# ---------------------------------------------------------------------------
# AC 9 + AC 10 — the four `payload_body` keys, through the REAL adapter
# ---------------------------------------------------------------------------


# mutation-probe: delete the `payload_body["escalation_instance_id"] = ...` line from
# `project_brief_to_payload`.
@pytest.mark.asyncio
async def test_the_four_payload_keys_are_projected_on_a_real_fanout_escalation(
    tracing: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    """v1.121 site 3 / §0.6 — witnessed THROUGH the adapter, not by asserting the
    brief carries them.

    The adapter is an explicit field-by-field mapper, so a field present on the brief
    and absent from the mapper silently never reaches the wire — precisely the gap
    out-of-family review found in the spec leg's first draft.

    The BARE token is the key that closes the loop: an operator cannot equality-match
    the composed `Idempotency-Key` against the pause-view projection, because §0.4(1)
    forbids parsing it.
    """
    provider, _exporter = tracing
    ctx = _fanout_context(2)
    signal = await _escalate(provider, ctx)
    token = signal.brief.escalation_instance_id
    assert token is not None

    payload = project_brief_to_payload(
        signal.brief, "k", **_hgc._escalation_operator_surface(token, ctx)
    )
    body = dict(payload.payload_body)
    assert body["escalation_instance_id"] == token, (
        "the BARE token, verbatim — not the composed key, which §0.4(1) forbids parsing back apart"
    )
    assert isinstance(body["branch_context"], str)
    # ONE AUTHORITY, cross-checked rather than asserted twice against a literal.
    # Production stamps this constant; the CP record separately asserts the pause
    # view's own `variant` for the same location. Two independent agreements with the
    # same literal would NOT catch a future divergence between the two surfaces, which
    # is the "second classification authority" §0.6 forecloses (pre-merge
    # witness-adequacy gate, [P2]). So compare the wire value against the variant the
    # CP projection actually assigns to a pre-dispatch gate-owning location.
    projected_variant = PreDispatchUniformFallbackOnlyLocation(
        pause_reason=WorkflowPauseReason.HITL_PENDING,
        step_index=0,
        step_id="branch-sub",
        step_kind=StepKind.SUB_AGENT_DISPATCH,
        branch_index=2,
        escalation_instance_id=token,
    ).variant
    assert body["resolvability"] == projected_variant.value, (
        "the wire's resolution CHANNEL must be the SAME value the pause view assigns "
        f"to this location — got {body['resolvability']!r} vs {projected_variant.value!r}"
    )
    assert projected_variant in set(PauseLocationVariant), (
        "and it must come from the CLOSED v1.112 §2.1 vocabulary — never the "
        "time-varying OUTCOME, and never a newly minted value"
    )
    assert isinstance(body["resolvability_note"], str) and body["resolvability_note"]
    assert sorted(body["proposed_response_palette"]) == sorted(
        r.value for r in signal.brief.proposed_response_palette
    ), "§0.6.1 — the palette is PRESERVED and still projected, never suppressed"


def test_the_adapter_is_byte_identical_when_the_keys_are_absent() -> None:
    """§0.12 — the linear/validator population's wire body against a pre-arc fixture.

    An unset Optional adds no key, which is exactly the property this mapper shape
    already guarantees; the fixture pins it rather than trusting it.
    """
    brief = HITLEscalationBrief(
        parent_step_id="linear-0",
        parent_action_id=_PARENT_ACTION_ID,
        escalation_reason="validator-escalation",
    )
    body = dict(project_brief_to_payload(brief, "k").payload_body)
    assert body == {
        "escalation_reason": "validator-escalation",
        "parent_step_id": "linear-0",
        "fail_class": None,
        "fail_detail_hash": None,
        "proposed_response_palette": sorted(r.value for r in brief.proposed_response_palette),
    }, f"pre-arc wire body must be byte-identical; got {body!r}"


def test_the_operator_surface_is_empty_when_no_token_was_minted() -> None:
    """The keys are emitted only when their SOURCE values are present, so the
    linear/validator call is byte-identical to pre-arc at the call site too."""
    assert _hgc._escalation_operator_surface(None, _context(branch_index=0)) == {}
    assert _hgc._escalation_operator_surface("t" * 64, _context(branch_index=None)) == {}


# ---------------------------------------------------------------------------
# U-CP-102 AC 14 — the validator trust seam, end to end
# ---------------------------------------------------------------------------


# mutation-probe: replace the `escalation_brief = escalation_brief.model_copy(update={
# "escalation_instance_id": None})` overwrite at the validator seam in
# `harness-cp/src/harness_cp/workflow_driver.py` with `pass` — i.e. IGNORE the supplied
# value without overwriting it, which is the failure §0.4(3) names explicitly.
# (Added at out-of-family merge-gate review: the CP plan's §0.2 probe table obliges
# criterion 14 to carry an annotation, and the CP record's own annotation covers the
# DIAGNOSIS side-effect — criterion 16's territory — not the overwrite itself.)
def test_a_validator_supplied_token_never_reaches_the_escalation_composer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """§0.4(3) — the seam OVERWRITES, it does not merely ignore.

    Ignoring without overwriting is NOT sufficient: the operator's value would still
    ride the payload. Homed here because intercepting the runtime composer the
    sanitized brief is handed to needs a `harness-runtime` import; the CP record
    carries the same seam's DIAGNOSIS half.
    """
    import harness_runtime.lifecycle.validator_escalation_composer as vec
    from harness_core import PersonaTier, WorkloadClass
    from harness_cp import workflow_driver as wd
    from harness_cp.cp_shared_types import ModelBinding
    from harness_cp.cross_family_fallback_chain import (
        FallbackChain,
        ProviderCandidate,
        ProviderFamily,
    )
    from harness_cp.engine_class import EngineClass
    from harness_cp.topology_pattern import TopologyPattern
    from harness_cp.validator_framework_types import (
        ValidatorEvaluation,
        ValidatorNextAction,
        ValidatorOutcome,
        ValidatorResult,
    )
    from harness_cp.workflow_manifest_entry import WorkflowManifestEntry

    hostile = "HOSTILE-OPERATOR-SUPPLIED-TOKEN"
    seen: list[HITLEscalationBrief] = []

    async def _capture(*, brief: HITLEscalationBrief, **kwargs: Any) -> Any:
        seen.append(brief)
        # Return a real APPROVE so the run completes normally: this witness is about
        # WHAT the composer received, and raising here would confound the assertion
        # with an unrelated failure path.
        return HITLResult(
            response=HITLResponse.APPROVE,
            timestamp="2026-08-14T00:00:00Z",
            audit_ledger_entry_id=EntryID("e-b71-seam"),
            response_summary_hash="e" * 64,
        )

    monkeypatch.setattr(vec, "compose_validator_escalation_gate", _capture)

    class _Framework:
        def evaluate(self, step: Any, step_result: Any, *, step_context: Any) -> Any:
            return ValidatorEvaluation(
                result=ValidatorResult(
                    outcome=ValidatorOutcome.ESCALATE,
                    escalation_brief=HITLEscalationBrief(
                        parent_step_id=str(step.step_id),
                        parent_action_id=str(step_context.parent_action_id),
                        escalation_reason="operator-authored",
                        escalation_instance_id=hostile,
                    ),
                ),
                span_attributes={},
                next_action=ValidatorNextAction.ESCALATE_HITL,
                burden_count=1,
            )

    class _Ctx:
        def __init__(self) -> None:
            import asyncio

            from opentelemetry.trace import NoOpTracerProvider

            self.ledger_writer = _DriverLedger()
            self.lifecycle_emitter = _NullEmitter()
            self.tracer_provider = NoOpTracerProvider()
            self.validator_framework = _Framework()
            self.ask_user_question_surface = object()
            self.tenant_id = None
            self.ledger_reader = None
            self.pause_resume_protocol = None
            self.drained_flag = asyncio.Event()
            self.pause_requested_flag = asyncio.Event()

    class _DriverLedger:
        actor = _ACTOR

        def __init__(self) -> None:
            self.appends: list[Any] = []

        def append(self, payload: Any, key: Any) -> Any:
            self.appends.append((payload, key))
            return "appended"

        @property
        def is_genesis(self) -> bool:
            return not self.appends

        @property
        def entry_count(self) -> int:
            return len(self.appends)

    class _NullEmitter:
        def emit(self, event_class: Any) -> None:
            return None

    class _OkDispatcher:
        def lookup(self, step_kind: Any) -> Any:
            return self

        def dispatch(self, binding: Any, step: Any, *, step_context: Any = None) -> Any:
            return {"ok": True}

    manifest = WorkflowManifestEntry(
        workflow_id="wf-b71",
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=TopologyPattern.SINGLE_THREADED_LINEAR,
        layer_budgets=(),
        fallback_chain=FallbackChain(
            primary=ProviderCandidate(
                provider="anthropic", model="claude-haiku-4-5", family=ProviderFamily.ANTHROPIC
            ),
            same_family=(),
            cross_family=(),
            terminal=None,
        ),
        hitl_placements=(),
        per_step_overrides={},
    )
    wd.execute_workflow(
        manifest,
        [
            WorkflowStep(
                step_id=StepID("linear-0"),
                step_kind=StepKind.DECLARATIVE_STEP,
                step_payload={"index": 0},
            )
        ],
        run_id=_RUN_ID,
        ctx=cast(Any, _Ctx()),
        default_model_binding=ModelBinding(provider="anthropic", model="claude-haiku-4-5"),
        step_dispatchers=cast(Any, _OkDispatcher()),
    )
    assert seen, "the escalation composer was never reached — the witness is vacuous"
    assert seen[0].escalation_instance_id is None, (
        "the validator-supplied token must be REPLACED with the harness-minted value "
        f"(`None` on this population) before the brief reaches any composer; got "
        f"{seen[0].escalation_instance_id!r}"
    )
    assert seen[0].escalation_reason == "operator-authored", (
        "the overwrite replaces ONE field — it must not discard the escalation"
    )


# ---------------------------------------------------------------------------
# Cross-check: the digest the Runtime half consumes is the CP-owned one
# ---------------------------------------------------------------------------


def test_the_runtime_half_consumes_the_cp_owned_digest_rather_than_re_deriving_it() -> None:
    """One authority for the formula.

    §0.4(2) makes the digest a CONTRACT surface; a Runtime-local re-derivation would
    be a second authority that could drift silently. The vector is restated here so
    this record fails if the Runtime half ever stops calling the CP function.
    """
    basis = "run-root-0001:pre-dispatch-gate:0"
    assert (
        compose_escalation_instance_id(basis, _GATE)
        == hashlib.sha256(
            b"hitl-escalation-instance:run-root-0001:pre-dispatch-gate:0:sub-agent-boundary"
        ).hexdigest()
    )
    assert _hgc.compose_escalation_instance_id is compose_escalation_instance_id
