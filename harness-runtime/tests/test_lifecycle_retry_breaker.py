"""U-RT-24 — retry / breaker / idempotency runtime registry tests.

ACs per Phase 2 Session 3 Track A atomic decomposition §L5 U-RT-24:
  #1 transient-staircase observability: injected transient fault N times
     surfaces N escalated retry intervals matching the
     `validator_fail_transient_staircase` table.
     -> test_staircase_advances_through_5_stages_on_transient_retry
     -> test_staircase_emits_n_intervals_for_n_transient_faults
     -> test_compute_delay_seconds_deterministic_under_seeded_rng
     -> test_compute_delay_seconds_monotonic_envelope_until_cap
  #2 breaker state transitions emit `harness.breaker.*` spans on each
     open/half-open/close.
     -> test_breaker_emits_event_on_closed_to_open
     -> test_breaker_emits_event_on_open_to_half_open
     -> test_breaker_emits_event_on_half_open_to_closed
     -> test_breaker_emits_event_on_half_open_to_open_on_retry_fail
  #3 idempotency join dedupes a replayed request to a single ledger entry.
     -> test_dedupe_decision_first_ingestion_then_drop_on_deterministic_replay
     -> test_dedupe_decision_replay_derived_for_checkpoint_resume

Plus bootstrap-failure + manifest-policy plumbing tests:
  -> test_materialize_returns_stage_with_default_policy
  -> test_materialize_loads_per_tool_policies_from_manifest
  -> test_materialize_raises_on_invalid_max_attempts
  -> test_materialize_raises_on_invalid_default_policy
  -> test_get_breaker_returns_same_instance_on_repeat_lookup
  -> test_retry_breaker_stage_is_frozen
"""

from __future__ import annotations

import random
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from harness_core import DeploymentSurface
from harness_cp.engine_namespace import ReplayDisposition
from harness_cp.routing_manifest_residence import (
    RetryPolicy,
    RoutingManifest,
)
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.validator_fail_taxonomy import ValidatorRetryExitClass
from harness_cp.validator_fail_transient_staircase import StaircaseStage
from harness_od.harness_breaker_schema import (
    BreakerScope,
    BreakerState,
)
from harness_od.idempotency_join_dedup import (
    DedupOutcome,
    F2StateLedgerEntry,
    SpanIngestionView,
)
from harness_od.otel_genai_base import EventEmission, SpanRef
from harness_runtime.lifecycle.retry_breaker import (
    DEFAULT_BASE_DELAY_SECONDS,
    DEFAULT_DELAY_CAP_SECONDS,
    DEFAULT_RETRY_POLICY,
    BreakerStateMachine,
    BreakerTransition,
    RetryBreakerBindError,
    RetryBreakerStage,
    RuntimeRetryBreaker,
    compute_full_jitter_delay_seconds,
    materialize_retry_breaker_stage,
)
from harness_runtime.types import (
    CollectorConfig,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
)
from opentelemetry.sdk.trace import TracerProvider

# ---------------------------------------------------------------------------
# Fixtures.
# ---------------------------------------------------------------------------


def _config(
    tmp_path: Path,
    *,
    manifest: RoutingManifest | None = None,
) -> RuntimeConfig:
    """Build a minimal `RuntimeConfig` for materialize tests.

    Duplicated per L5 test-module convention (matches the L4 fake-keyring /
    L5 routing-manifest / engine-selector / fallback-chain pattern).
    """
    if manifest is None:
        return RuntimeConfig(
            deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
            repository_root=tmp_path,
            path_bindings=PathBindingConfig(),
            provider_secrets=ProviderSecretsConfig(),
            otel=OTelConfig(otlp_endpoint="http://localhost:4317"),
            collector=CollectorConfig(),
            default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        )
    return RuntimeConfig(
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        repository_root=tmp_path,
        path_bindings=PathBindingConfig(),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4317"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        routing_manifest=manifest,
    )


def _manifest(
    retry_policies: dict[str, RetryPolicy] | None = None,
) -> RoutingManifest:
    return RoutingManifest(
        manifest_version=1,
        per_role_bindings={},
        per_workload_overrides={},
        fallback_chains=(),
        retry_policies=retry_policies or {},
    )


def _span() -> SpanRef:
    """A live OTel-SDK span handle for `SpanRef`-shaped tests."""
    return TracerProvider().get_tracer("u-rt-24-test").start_span("parent")


# ---------------------------------------------------------------------------
# Bootstrap-failure + manifest-policy plumbing.
# ---------------------------------------------------------------------------


def test_materialize_returns_stage_with_default_policy(tmp_path: Path) -> None:
    """The empty manifest yields a registry that returns `DEFAULT_RETRY_POLICY`
    for every tool name (the default policy carries identity)."""
    stage = materialize_retry_breaker_stage(_config(tmp_path, manifest=_manifest()))
    assert isinstance(stage, RetryBreakerStage)
    assert stage.registry.get_policy("any-tool") is DEFAULT_RETRY_POLICY


def test_materialize_loads_per_tool_policies_from_manifest(tmp_path: Path) -> None:
    """Per-tool policies on the manifest surface verbatim through `get_policy`."""
    tool_policy = RetryPolicy(max_attempts=7, backoff="full-jitter", jitter="full-jitter")
    stage = materialize_retry_breaker_stage(
        _config(
            tmp_path,
            manifest=_manifest({"search-tool": tool_policy}),
        )
    )
    assert stage.registry.get_policy("search-tool") is tool_policy
    # An unbound tool name falls back to the default.
    assert stage.registry.get_policy("unbound-tool") is DEFAULT_RETRY_POLICY


def test_materialize_raises_on_invalid_max_attempts(tmp_path: Path) -> None:
    """A manifest `RetryPolicy` with `max_attempts < 1` raises at bootstrap."""
    bad_policy = RetryPolicy(max_attempts=0, backoff="full-jitter", jitter="full-jitter")
    with pytest.raises(RetryBreakerBindError, match="max_attempts=0"):
        materialize_retry_breaker_stage(
            _config(
                tmp_path,
                manifest=_manifest({"bad-tool": bad_policy}),
            )
        )


def test_materialize_raises_on_invalid_default_policy(tmp_path: Path) -> None:
    """A caller-supplied default policy with `max_attempts < 1` raises."""
    bad_default = RetryPolicy(max_attempts=0, backoff="full-jitter", jitter="full-jitter")
    with pytest.raises(RetryBreakerBindError, match="default retry policy"):
        materialize_retry_breaker_stage(
            _config(tmp_path, manifest=_manifest()),
            default_policy=bad_default,
        )


def test_get_breaker_returns_same_instance_on_repeat_lookup(tmp_path: Path) -> None:
    """Lazy instantiation: the same `(scope, identifier)` returns the same machine."""
    stage = materialize_retry_breaker_stage(_config(tmp_path, manifest=_manifest()))
    a = stage.registry.get_breaker(BreakerScope.PER_MODEL, "tool-x")
    b = stage.registry.get_breaker(BreakerScope.PER_MODEL, "tool-x")
    assert a is b
    # Distinct keys produce distinct breakers.
    c = stage.registry.get_breaker(BreakerScope.PER_PROVIDER, "tool-x")
    assert c is not a


def test_retry_breaker_stage_is_frozen(tmp_path: Path) -> None:
    """`RetryBreakerStage` is a frozen dataclass — assignment raises."""
    stage = materialize_retry_breaker_stage(_config(tmp_path, manifest=_manifest()))
    with pytest.raises(FrozenInstanceError):
        stage.registry = RuntimeRetryBreaker(  # type: ignore[misc]
            retry_policies={}, default_policy=DEFAULT_RETRY_POLICY
        )


# ---------------------------------------------------------------------------
# AC #1 — transient-staircase observability.
# ---------------------------------------------------------------------------


def test_staircase_advances_through_5_stages_on_transient_retry(tmp_path: Path) -> None:
    """Threading `ValidatorRetryExitClass.TRANSIENT_RETRY` through the registry's
    `advance_staircase` walks the 5-stage envelope per C-CP-21 §21.2.

    Stage 1 → Stage 2 (cache kept) → Stage 3 (cache lost; cross-family) →
    Stage 4 (local terminal) → Stage 5 (HITL escalation).
    """
    stage = materialize_retry_breaker_stage(_config(tmp_path, manifest=_manifest())).registry
    cause = ValidatorRetryExitClass.TRANSIENT_RETRY

    t1 = stage.advance_staircase(StaircaseStage.STAGE_1_REFLEXION, cause, 1)
    assert t1.to_stage is StaircaseStage.STAGE_2_RETRY_WITH_BACKOFF
    assert t1.preserves_cache_state is True
    assert t1.emits_fallback_event is False

    t2 = stage.advance_staircase(t1.to_stage, cause, 2)
    assert t2.to_stage is StaircaseStage.STAGE_3_CROSS_FAMILY_FALLBACK
    assert t2.preserves_cache_state is False
    assert t2.emits_fallback_event is True

    t3 = stage.advance_staircase(t2.to_stage, cause, 3)
    assert t3.to_stage is StaircaseStage.STAGE_4_LOCAL_TERMINAL

    t4 = stage.advance_staircase(t3.to_stage, cause, 4)
    assert t4.to_stage is StaircaseStage.STAGE_5_HITL_ESCALATION


def test_staircase_emits_n_intervals_for_n_transient_faults(tmp_path: Path) -> None:
    """AC #1: injected transient fault N times surfaces N escalated retry
    intervals matching the staircase table.

    Driving the staircase N times from `STAGE_1_REFLEXION` collects N
    transitions; each non-terminal stage maps to a `compute_delay_seconds`
    schedule entry. The transitions sequence is the §21.2 escalation envelope.
    """
    registry = materialize_retry_breaker_stage(_config(tmp_path, manifest=_manifest())).registry
    cause = ValidatorRetryExitClass.TRANSIENT_RETRY
    current = StaircaseStage.STAGE_1_REFLEXION

    transitions: list[StaircaseStage] = []
    rng = random.Random(0xC0FFEE)
    intervals: list[float] = []

    for attempt in range(4):
        transition = registry.advance_staircase(current, cause, attempt + 1)
        transitions.append(transition.to_stage)
        # Staircase escalates; the registry's full-jitter schedule is the
        # per-attempt delay envelope (Reading B per the module docstring).
        intervals.append(registry.compute_delay_seconds(attempt, rng=rng))
        current = transition.to_stage

    assert transitions == [
        StaircaseStage.STAGE_2_RETRY_WITH_BACKOFF,
        StaircaseStage.STAGE_3_CROSS_FAMILY_FALLBACK,
        StaircaseStage.STAGE_4_LOCAL_TERMINAL,
        StaircaseStage.STAGE_5_HITL_ESCALATION,
    ]
    # N injected faults → N delay-envelope samples; the schedule is non-empty
    # and each entry honors the full-jitter envelope.
    assert len(intervals) == 4
    for attempt, delay in enumerate(intervals):
        envelope = min(
            DEFAULT_DELAY_CAP_SECONDS,
            DEFAULT_BASE_DELAY_SECONDS * (2**attempt),
        )
        assert 0.0 <= delay <= envelope


def test_compute_delay_seconds_deterministic_under_seeded_rng() -> None:
    """A seeded `random.Random` makes the delay schedule deterministic — the
    test asserts byte-stable output across attempts so AC #1 has a stable
    observable surface."""
    rng_a = random.Random(0xABCD)
    rng_b = random.Random(0xABCD)
    delays_a = [compute_full_jitter_delay_seconds(attempt, rng=rng_a) for attempt in range(4)]
    delays_b = [compute_full_jitter_delay_seconds(attempt, rng=rng_b) for attempt in range(4)]
    assert delays_a == delays_b


def test_compute_delay_seconds_monotonic_envelope_until_cap() -> None:
    """The envelope `min(cap, base * 2**attempt)` is monotonic-non-decreasing
    in `attempt` until the cap; each sampled delay sits in `[0, envelope]`."""
    base = 0.5
    cap = 30.0
    rng = random.Random(0xBEEF)
    envelopes = [min(cap, base * (2**attempt)) for attempt in range(8)]
    for attempt, envelope in enumerate(envelopes):
        delay = compute_full_jitter_delay_seconds(
            attempt, base_seconds=base, cap_seconds=cap, rng=rng
        )
        assert 0.0 <= delay <= envelope


def test_compute_delay_seconds_rejects_negative_inputs() -> None:
    """Defensive: negative attempt / base / cap raise `ValueError`."""
    with pytest.raises(ValueError, match="attempt"):
        compute_full_jitter_delay_seconds(-1)
    with pytest.raises(ValueError, match="base_seconds"):
        compute_full_jitter_delay_seconds(0, base_seconds=-1.0)
    with pytest.raises(ValueError, match="cap_seconds"):
        compute_full_jitter_delay_seconds(0, cap_seconds=-1.0)


# ---------------------------------------------------------------------------
# AC #2 — breaker state transitions emit `harness.breaker.*` spans.
# ---------------------------------------------------------------------------


def test_breaker_emits_event_on_closed_to_open(tmp_path: Path) -> None:
    """closed → open at `fail_threshold` failures; the registry emits a
    `breaker.tripped` event via the OD canonical schema."""
    registry = materialize_retry_breaker_stage(
        _config(tmp_path, manifest=_manifest()),
        fail_threshold=3,
    ).registry
    breaker = registry.get_breaker(BreakerScope.PER_MODEL, "tool-x")

    # First two failures: no transition.
    assert breaker.record_failure(now=0.0) is None
    assert breaker.record_failure(now=0.0) is None
    # Third failure: closed → open.
    transition = breaker.record_failure(now=0.0)
    assert transition is not None
    assert transition.from_state is BreakerState.CLOSED
    assert transition.to_state is BreakerState.OPEN
    assert transition.trigger_count == 3
    assert transition.scope is BreakerScope.PER_MODEL
    assert transition.identifier == "tool-x"

    # Emit the event; verify the OD canonical EventEmission surfaces.
    emission = registry.emit_breaker_transition_event(transition, _span())
    assert isinstance(emission, EventEmission)
    assert emission.event_name == "breaker.tripped"
    assert emission.sampled is True


def test_attempt_half_open_is_conjunctive_on_cooldown_elapse(tmp_path: Path) -> None:
    """`B-118` AC #1: `attempt_half_open(now)` admits iff ALL THREE conjuncts
    hold — state is `open`, `opened_at` was recorded, and the cooldown has
    elapsed. Before v1.114 the method checked ONLY the state, so it would
    have flipped a just-tripped breaker to `half_open` immediately."""
    registry = materialize_retry_breaker_stage(
        _config(tmp_path, manifest=_manifest()),
        fail_threshold=1,
        cooldown_seconds=30.0,
    ).registry
    breaker = registry.get_breaker(BreakerScope.PER_MODEL, "tool-cooldown")

    # Conjunct 1 — not open.
    assert breaker.attempt_half_open(now=1_000.0) is None
    assert breaker.state is BreakerState.CLOSED

    breaker.record_failure(now=100.0)  # closed → open, opened_at = 100.0
    assert breaker.state is BreakerState.OPEN
    assert breaker.opened_at == 100.0

    # Conjunct 3 — cooldown unexpired. Boundary is inclusive at `>=`, so
    # both strictly-before and exactly-one-tick-before are refused.
    assert breaker.attempt_half_open(now=100.0) is None
    assert breaker.attempt_half_open(now=129.999) is None
    assert breaker.state is BreakerState.OPEN
    # A refusal leaves the deadline untouched, so repeated pre-checks cannot
    # walk it forward and postpone recovery indefinitely.
    assert breaker.opened_at == 100.0

    # All three hold at the boundary itself.
    transition = breaker.attempt_half_open(now=130.0)
    assert transition is not None
    assert transition.from_state is BreakerState.OPEN
    assert transition.to_state is BreakerState.HALF_OPEN
    assert transition.trigger_count == 0
    assert breaker.state is BreakerState.HALF_OPEN

    # The transition IS the permit: a second caller gets None.
    assert breaker.attempt_half_open(now=1_000.0) is None


def test_attempt_half_open_refuses_an_open_machine_with_no_opened_at(
    tmp_path: Path,
) -> None:
    """`B-118` AC #1: `state is open` with `opened_at is None` is the illegal
    state reachable only by assigning `state` directly. It must REFUSE (a
    deadline that was never set cannot have elapsed) rather than admit a
    trial from a cooldown that does not exist."""
    registry = materialize_retry_breaker_stage(
        _config(tmp_path, manifest=_manifest()),
        fail_threshold=1,
    ).registry
    breaker = registry.get_breaker(BreakerScope.PER_MODEL, "tool-illegal")
    breaker.state = BreakerState.OPEN  # direct assignment; no opened_at
    assert breaker.opened_at is None
    assert breaker.attempt_half_open(now=1e9) is None
    assert breaker.state is BreakerState.OPEN
    # A REFUSED admission must not mutate the machine AT ALL. Asserting only
    # the `None` return and the unchanged state is too weak: a guard that
    # STAMPED `opened_at = now` and then fell through to the elapsed check
    # would also refuse this first call — and would thereby convert a
    # permanent refusal into "refuse once, then start a cooldown", admitting
    # a trial on the next call. (Found by the P7 mutation probe coming back
    # GREEN against the first draft of this witness.)
    assert breaker.opened_at is None
    assert breaker.attempt_half_open(now=2e9) is None
    assert breaker.state is BreakerState.OPEN


def test_re_arm_half_open_trial_returns_to_open_with_a_fresh_cooldown(
    tmp_path: Path,
) -> None:
    """`B-118` AC #2 / §14.6.4 cell 3 (operator-ratified 2026-08-08): an
    INCONCLUSIVE trial returns to `open` with a FRESH cooldown, `fail_count`
    UNCHANGED, and `trigger_count == 0` — the wire discriminator against a
    real half_open → open re-trip, whose `trigger_count` is `fail_count`."""
    registry = materialize_retry_breaker_stage(
        _config(tmp_path, manifest=_manifest()),
        fail_threshold=2,
        cooldown_seconds=30.0,
    ).registry
    breaker = registry.get_breaker(BreakerScope.PER_MODEL, "tool-rearm")
    breaker.record_failure(now=0.0)
    breaker.record_failure(now=0.0)  # closed → open at threshold 2
    assert breaker.fail_count == 2
    assert breaker.attempt_half_open(now=30.0) is not None

    transition = breaker.re_arm_half_open_trial(now=200.0, trial_token=breaker.trial_epoch)
    assert transition is not None
    assert transition.from_state is BreakerState.HALF_OPEN
    assert transition.to_state is BreakerState.OPEN
    assert transition.trigger_count == 0  # NOT a trip
    assert breaker.state is BreakerState.OPEN
    assert breaker.fail_count == 2  # an inconclusive trial charges nothing
    assert breaker.opened_at == 200.0  # FRESH, not the original 0.0

    # The fresh cooldown really governs: the ORIGINAL deadline is long past,
    # yet no trial is admitted until 30s after the re-arm.
    assert breaker.attempt_half_open(now=201.0) is None
    assert breaker.attempt_half_open(now=230.0) is not None


def test_re_arm_half_open_trial_is_a_no_op_off_half_open(tmp_path: Path) -> None:
    """`B-118` AC #2: the re-arm is a no-op unless the machine is still
    `half_open` — which is exactly the "the trial recorded neither success
    nor a charging failure" test, so the composer may call it on every exit
    path without discriminating the outcome itself."""
    registry = materialize_retry_breaker_stage(
        _config(tmp_path, manifest=_manifest()),
        fail_threshold=1,
    ).registry
    breaker = registry.get_breaker(BreakerScope.PER_MODEL, "tool-rearm-noop")
    assert breaker.re_arm_half_open_trial(now=1.0, trial_token=0) is None  # closed
    breaker.record_failure(now=0.0)
    assert breaker.re_arm_half_open_trial(now=1.0, trial_token=0) is None  # open
    assert breaker.state is BreakerState.OPEN
    assert breaker.opened_at == 0.0  # untouched by the no-op


def test_record_failure_records_the_open_instant_on_both_open_entries(
    tmp_path: Path,
) -> None:
    """`B-118` AC #1: every transition INTO `open` records `opened_at` from
    the caller-supplied `now` — the closed → open trip AND the half_open →
    open re-trip. A re-trip that failed to restamp would leave the breaker
    recoverable against a stale deadline."""
    registry = materialize_retry_breaker_stage(
        _config(tmp_path, manifest=_manifest()),
        fail_threshold=1,
        cooldown_seconds=30.0,
    ).registry
    breaker = registry.get_breaker(BreakerScope.PER_MODEL, "tool-instants")
    breaker.record_failure(now=10.0)
    assert breaker.opened_at == 10.0
    breaker.attempt_half_open(now=40.0)
    transition = breaker.record_failure(
        now=41.0, trial_token=breaker.trial_epoch
    )  # trial failed → re-open
    assert transition is not None
    assert transition.to_state is BreakerState.OPEN
    assert transition.trigger_count == breaker.fail_count >= 1
    assert breaker.opened_at == 41.0  # restamped, not 10.0
    # And a success clears it, so a CLOSED machine carries no stale deadline.
    breaker.attempt_half_open(now=71.0)
    breaker.record_success(trial_token=breaker.trial_epoch)
    assert breaker.state is BreakerState.CLOSED
    assert breaker.opened_at is None


def test_breaker_emits_event_on_open_to_half_open(tmp_path: Path) -> None:
    """open → half_open transition emits an event when the caller-driven
    `attempt_half_open()` fires after cooldown."""
    registry = materialize_retry_breaker_stage(
        _config(tmp_path, manifest=_manifest()),
        fail_threshold=1,
    ).registry
    breaker = registry.get_breaker(BreakerScope.PER_PROVIDER, "anthropic")
    breaker.record_failure(now=0.0)  # closed → open
    transition = breaker.attempt_half_open(now=31.0)
    assert transition is not None
    assert transition.from_state is BreakerState.OPEN
    assert transition.to_state is BreakerState.HALF_OPEN
    emission = registry.emit_breaker_transition_event(transition, _span())
    assert emission.event_name == "breaker.tripped"


def test_breaker_emits_event_on_half_open_to_closed(tmp_path: Path) -> None:
    """half_open → closed on a single success; the event emits + fail_count resets."""
    registry = materialize_retry_breaker_stage(
        _config(tmp_path, manifest=_manifest()),
        fail_threshold=1,
    ).registry
    breaker = registry.get_breaker(BreakerScope.PER_MODEL, "tool-y")
    breaker.record_failure(now=0.0)  # closed → open
    breaker.attempt_half_open(now=31.0)  # open → half_open
    transition = breaker.record_success(trial_token=breaker.trial_epoch)
    assert transition is not None
    assert transition.from_state is BreakerState.HALF_OPEN
    assert transition.to_state is BreakerState.CLOSED
    assert breaker.fail_count == 0
    emission = registry.emit_breaker_transition_event(transition, _span())
    assert emission.event_name == "breaker.tripped"


def test_breaker_emits_event_on_half_open_to_open_on_retry_fail(tmp_path: Path) -> None:
    """half_open → open: a failure during the half-open trial re-opens."""
    registry = materialize_retry_breaker_stage(
        _config(tmp_path, manifest=_manifest()),
        fail_threshold=1,
    ).registry
    breaker = registry.get_breaker(BreakerScope.PER_MODEL, "tool-z")
    breaker.record_failure(now=0.0)  # closed → open
    breaker.attempt_half_open(now=31.0)  # open → half_open
    transition = breaker.record_failure(now=0.0, trial_token=breaker.trial_epoch)
    assert transition is not None
    assert transition.from_state is BreakerState.HALF_OPEN
    assert transition.to_state is BreakerState.OPEN
    emission = registry.emit_breaker_transition_event(transition, _span())
    assert emission.event_name == "breaker.tripped"


def test_breaker_does_not_emit_on_no_op_transitions(tmp_path: Path) -> None:
    """No transition = no event: `record_failure` on `open` is a no-op,
    `record_success` on `closed` is a no-op, `attempt_half_open` on `closed`
    is a no-op."""
    registry = materialize_retry_breaker_stage(
        _config(tmp_path, manifest=_manifest()),
        fail_threshold=1,
    ).registry
    breaker = registry.get_breaker(BreakerScope.PER_MODEL, "tool-no-op")
    assert breaker.record_success() is None  # closed → closed: no transition
    breaker.record_failure(now=0.0)  # closed → open
    assert breaker.record_failure(now=0.0) is None  # open: no-op
    breaker.attempt_half_open(now=31.0)  # open → half_open
    breaker.record_success(trial_token=breaker.trial_epoch)  # half_open → closed
    assert breaker.attempt_half_open(now=31.0) is None  # closed: no-op


def test_breaker_should_attempt_is_the_single_trial_permit(tmp_path: Path) -> None:
    """`should_attempt()` is True iff state is `closed` — NARROWED at v1.114
    (`B-118`) from the prior `state is not open`.

    `half_open` exists only while a trial is in flight, so the old predicate
    admitted every concurrent sibling into a call the contract says is a
    SINGLE trial. Refusing in `half_open` IS the permit; the permit holder
    proceeds on its own `attempt_half_open` transition and never re-consults
    this method. The end-to-end consequence is witnessed at
    `test_lifecycle_retry_breaker_fallback.py`'s concurrent-permit test."""
    registry = materialize_retry_breaker_stage(
        _config(tmp_path, manifest=_manifest()),
        fail_threshold=1,
    ).registry
    breaker = registry.get_breaker(BreakerScope.PER_MODEL, "tool-attempt")
    assert breaker.should_attempt() is True  # closed
    breaker.record_failure(now=0.0)  # → open
    assert breaker.should_attempt() is False
    breaker.attempt_half_open(now=31.0)  # → half_open: a trial is in flight
    assert breaker.should_attempt() is False
    breaker.record_success(trial_token=breaker.trial_epoch)  # → closed
    assert breaker.should_attempt() is True


def test_breaker_emit_threads_optional_per_model_correlation(tmp_path: Path) -> None:
    """At PER_MODEL scope, `tool_id` defaults to the breaker identifier when
    not explicitly supplied."""
    registry = materialize_retry_breaker_stage(
        _config(tmp_path, manifest=_manifest()),
        fail_threshold=1,
    ).registry
    breaker = registry.get_breaker(BreakerScope.PER_MODEL, "search-tool")
    transition = breaker.record_failure(now=0.0)
    assert transition is not None
    # `model_version` explicitly supplied; `tool_id` defaults to identifier.
    emission = registry.emit_breaker_transition_event(
        transition,
        _span(),
        permanent_fail_repeats=2,
        model_version="claude-opus-4-7",
    )
    # 8 of 9 §7.1 attributes populated: the 7 v1-canonical + `cooldown_ms`
    # (this is a real trip, `to_state = open`, so cooldown_ms auto-populates
    # from `cooldown_seconds * 1000`); `cause` stays None (not supplied —
    # vacuous-today per `.harness/b19-breaker-ambient-attrs-redundancy-
    # analysis.md` §3).
    assert emission.attribute_count == 8


# ---------------------------------------------------------------------------
# AC #3 — idempotency join dedupes a replayed request to a single ledger entry.
# ---------------------------------------------------------------------------


def _span_view(
    idempotency_key: str,
    *,
    trace_id: str = "trace-aaaa",
    span_id: str = "span-bbbb",
    disposition: ReplayDisposition = ReplayDisposition.DETERMINISTIC_REPLAY,
    cause: str | None = "transient_provider_error",
) -> SpanIngestionView:
    return SpanIngestionView(
        trace_id=trace_id,
        span_id=span_id,
        idempotency_key=idempotency_key,
        engine_replay_disposition=disposition,
        retry_attempt_number=1,
        retry_cause_attribution=cause,
    )


def _ledger_entry(
    idempotency_key: str,
    *,
    original_trace_id: str = "trace-aaaa",
    original_span_id: str = "span-bbbb",
    cause: str | None = "transient_provider_error",
) -> F2StateLedgerEntry:
    return F2StateLedgerEntry(
        idempotency_key=idempotency_key,
        original_trace_id=original_trace_id,
        original_span_id=original_span_id,
        cause_attribution=cause,
    )


def test_dedupe_decision_first_ingestion_then_drop_on_deterministic_replay(
    tmp_path: Path,
) -> None:
    """AC #3: a replayed request collapses to a single ledger entry.

    First ingestion (`ledger_entry=None`) → `RECORD_FIRST_INGESTION`. The
    second ingestion of the same span with `ReplayDisposition.DETERMINISTIC_REPLAY`
    against a matching ledger entry → `DROP_DETERMINISTIC_REPLAY_RE_READ`.
    When the U-RT-32 audit writer consumes outcomes, a DROP yields no new
    ledger row → exactly one ledger entry total.
    """
    registry = materialize_retry_breaker_stage(_config(tmp_path, manifest=_manifest())).registry
    key = "req-1234"
    span = _span_view(key)

    # First ingestion: no prior ledger entry.
    first = registry.dedupe_decision(span, None)
    assert first is DedupOutcome.RECORD_FIRST_INGESTION

    # Second ingestion: deterministic replay against the now-written entry.
    prior = _ledger_entry(key)
    second = registry.dedupe_decision(span, prior)
    assert second is DedupOutcome.DROP_DETERMINISTIC_REPLAY_RE_READ


def test_dedupe_decision_replay_derived_for_checkpoint_resume(tmp_path: Path) -> None:
    """`checkpoint_resume` replay disposition yields `RECORD_REPLAY_DERIVED`
    (re-emission is expected; the writer records a new replay-derived row)."""
    registry = materialize_retry_breaker_stage(_config(tmp_path, manifest=_manifest())).registry
    span = _span_view("req-5678", disposition=ReplayDisposition.CHECKPOINT_RESUME)
    outcome = registry.dedupe_decision(span, _ledger_entry("req-5678"))
    assert outcome is DedupOutcome.RECORD_REPLAY_DERIVED


def test_dedupe_decision_escalates_on_cause_attribution_mismatch(
    tmp_path: Path,
) -> None:
    """Deterministic replay with a `cause_attribution` mismatch escalates per
    C-OD-14 §14.5.3 invariance check."""
    registry = materialize_retry_breaker_stage(_config(tmp_path, manifest=_manifest())).registry
    span = _span_view("req-9999", cause="rate_limit")
    prior = _ledger_entry("req-9999", cause="transient_provider_error")
    outcome = registry.dedupe_decision(span, prior)
    assert outcome is DedupOutcome.ESCALATE_REPLAY_SEMANTIC_DIVERGENCE


# ---------------------------------------------------------------------------
# BreakerTransition + BreakerStateMachine misc invariants.
# ---------------------------------------------------------------------------


def test_breaker_transition_is_frozen() -> None:
    """`BreakerTransition` is frozen → field reassignment raises."""
    transition = BreakerTransition(
        from_state=BreakerState.CLOSED,
        to_state=BreakerState.OPEN,
        scope=BreakerScope.PER_MODEL,
        identifier="t",
        trigger_count=1,
    )
    with pytest.raises(FrozenInstanceError):
        transition.trigger_count = 99  # type: ignore[misc]


def test_breaker_state_machine_resets_fail_count_on_close_success() -> None:
    """A success in the closed state resets `fail_count` to zero (the registry
    requires consecutive failures to trip)."""
    machine = BreakerStateMachine(
        scope=BreakerScope.PER_MODEL,
        identifier="tool",
        fail_threshold=3,
    )
    machine.record_failure(now=0.0)
    machine.record_failure(now=0.0)
    machine.record_success()  # resets to 0
    machine.record_failure(now=0.0)
    machine.record_failure(now=0.0)
    # Still closed — only 2 consecutive failures after the reset.
    assert machine.state is BreakerState.CLOSED
    assert machine.fail_count == 2


# --- AC #11, stale outcomes while HALF_OPEN (the epoch guard) --------------


def test_b118_stale_success_does_not_close_a_breaker_whose_trial_is_outstanding() -> None:
    """AC #11 / §14.6.4 "stale outcomes", state-machine level: an outcome from
    a SUPERSEDED epoch must not resolve a trial it does not own.

    This is the sharpest failure in the family. Request A enters while the
    breaker is CLOSED and is still awaiting the provider; siblings trip the
    breaker; the cooldown elapses and request B admits a trial. If A's success
    then lands untokened, it CLOSES the breaker — and B's real trial failure
    subsequently arrives at a CLOSED machine as one ordinary failure, far under
    `fail_threshold`, so an unhealthy provider-model is silently readmitted."""
    machine = BreakerStateMachine(
        scope=BreakerScope.PER_MODEL,
        identifier="anthropic:claude-test-1",
        fail_threshold=2,
        cooldown_seconds=30.0,
    )
    # A is admitted while CLOSED and captures the epoch it saw (0 — no trial).
    stale_token_a = machine.trial_epoch
    # Siblings trip the breaker; the cooldown elapses; B admits the trial.
    machine.record_failure(now=0.0)
    machine.record_failure(now=0.0)
    assert machine.state is BreakerState.OPEN
    assert machine.attempt_half_open(now=30.0) is not None
    live_token_b = machine.trial_epoch
    assert live_token_b != stale_token_a

    # A's success finally lands. DROPPED — no transition, no state change.
    assert machine.record_success(trial_token=stale_token_a) is None
    assert machine.state is BreakerState.HALF_OPEN, "the trial is still outstanding"
    assert machine.fail_count == 2
    # A token-less caller is treated identically (there is no implicit owner).
    assert machine.record_success() is None
    assert machine.state is BreakerState.HALF_OPEN

    # B's real trial failure then resolves the trial it owns -> OPEN, not a
    # stray failure on a wrongly-closed breaker.
    transition = machine.record_failure(now=60.0, trial_token=live_token_b)
    assert transition is not None
    assert transition.from_state is BreakerState.HALF_OPEN
    assert transition.to_state is BreakerState.OPEN
    assert machine.state is BreakerState.OPEN
    assert machine.opened_at == 60.0


def test_b118_stale_failure_is_dropped_without_charging() -> None:
    """AC #11 mirror: a stale FAILURE is dropped too, and does NOT increment
    `fail_count`.

    Same treatment an outcome arriving while `open` already receives, and for
    the same reason: the machine has already concluded this provider-model is
    unhealthy, so pre-trip evidence adds nothing — while counting it would
    inflate the eventual re-trip's `trigger_count` with evidence from a
    superseded epoch."""
    machine = BreakerStateMachine(
        scope=BreakerScope.PER_MODEL,
        identifier="anthropic:claude-test-1",
        fail_threshold=2,
        cooldown_seconds=30.0,
    )
    stale_token = machine.trial_epoch
    machine.record_failure(now=0.0)
    machine.record_failure(now=0.0)
    machine.attempt_half_open(now=30.0)
    live_token = machine.trial_epoch

    assert machine.record_failure(now=31.0, trial_token=stale_token) is None
    assert machine.state is BreakerState.HALF_OPEN
    assert machine.fail_count == 2, "a stale failure charges nothing"
    assert machine.opened_at == 0.0, "and mutates no deadline"

    # The owner's outcome still carries the honest trip count.
    transition = machine.record_failure(now=40.0, trial_token=live_token)
    assert transition is not None
    assert transition.trigger_count == 3


def test_b118_a_non_owner_cannot_re_arm_someone_elses_trial() -> None:
    """AC #11: the re-arm is epoch-guarded too. A non-owner re-arming would
    ABORT a live trial and hand the provider a second call it never earned."""
    machine = BreakerStateMachine(
        scope=BreakerScope.PER_MODEL,
        identifier="anthropic:claude-test-1",
        fail_threshold=1,
        cooldown_seconds=30.0,
    )
    stale_token = machine.trial_epoch
    machine.record_failure(now=0.0)
    machine.attempt_half_open(now=30.0)
    live_token = machine.trial_epoch

    assert machine.re_arm_half_open_trial(now=99.0, trial_token=stale_token) is None
    assert machine.state is BreakerState.HALF_OPEN
    assert machine.opened_at == 0.0
    assert machine.re_arm_half_open_trial(now=99.0, trial_token=live_token) is not None
    assert machine.state is BreakerState.OPEN
    assert machine.opened_at == 99.0


def test_b118_closed_state_outcomes_need_no_token_and_are_byte_unchanged() -> None:
    """AC #11 scope bound: the epoch guard binds ONLY the `half_open` arms.

    Ordinary CLOSED-state accounting — the overwhelmingly common path — keeps
    its pre-v1.114 tokenless behaviour exactly, so the guard cannot silently
    start dropping ordinary failures."""
    machine = BreakerStateMachine(
        scope=BreakerScope.PER_MODEL,
        identifier="anthropic:claude-test-1",
        fail_threshold=3,
        cooldown_seconds=30.0,
    )
    assert machine.record_failure(now=0.0) is None
    assert machine.fail_count == 1
    assert machine.record_success() is None
    assert machine.fail_count == 0
    for _ in range(2):
        assert machine.record_failure(now=1.0) is None
    transition = machine.record_failure(now=1.0)  # third -> trip, no token
    assert transition is not None
    assert transition.to_state is BreakerState.OPEN
    assert transition.trigger_count == 3
    # And an outcome arriving while OPEN stays the no-op it always was.
    assert machine.record_failure(now=2.0) is None
    assert machine.record_success() is None
    assert machine.state is BreakerState.OPEN
