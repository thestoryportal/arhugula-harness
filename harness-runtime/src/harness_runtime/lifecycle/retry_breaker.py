"""Retry / breaker / idempotency runtime registry — stage 3b CP_ROUTING (U-RT-24).

Per `Spec_Harness_Runtime_v1.md` v1.1 §5 (C-RT-02 stage 3b invariants) and the
Phase 2 Session 3 Track A atomic decomposition §L5 (U-RT-24). The runtime wires
retry + breaker + idempotency-join primitives over landed CP / OD modules:

- `harness_cp.routing_manifest_residence.RetryPolicy` — operator-supplied
  per-tool policy (`max_attempts` / `backoff` / `jitter`) carried on
  `RuntimeConfig.routing_manifest.retry_policies`.
- `harness_cp.validator_fail_transient_staircase.advance_staircase` — the
  C-CP-21 §21.2 transient-staircase advancement function (5-stage table,
  cause-attribution-conditioned branching).
- `harness_od.harness_breaker_schema` — OD-canonical 7-attribute
  `harness.breaker.*` schema + `emit_breaker_trip_span_event` (C-OD-07 §7.1).
- `harness_od.idempotency_join_dedup.dedupe_on_replay` — the C-OD-14 §14.5.1
  trace-ingestion dedup decision.

**Hand-rolled.** Per `Plan_Executability_Audit_v1.md` framework-pull discipline
+ CLAUDE.md §3.2 + I-6: NO `tenacity` / `pybreaker` / `circuitbreaker`. The
breaker state machine and the full-jitter backoff are written here against the
stdlib `random` module.

**Breaker config is spec-deferred.** C-CP-03 §3.5 explicitly defers "specific
breaker trip-threshold values per `{provider, model}` pair; specific cooldown
duration shape per cause class" to implementation discretion. This module
binds bootstrap defaults — `DEFAULT_FAIL_THRESHOLD` / `DEFAULT_COOLDOWN_SECONDS`
/ `DEFAULT_BASE_DELAY_SECONDS` / `DEFAULT_DELAY_CAP_SECONDS` — at the
materialize-stage composer; the composer keyword arguments let operators
override per-runtime without amending the spec.

**Two retry surfaces, by design.** The L4 `_attempt_with_bounded_retry` at
`harness_runtime.lifecycle.providers` is the BOOTSTRAP construction retry —
distinct from this L5 registry. Bootstrap retry has no breaker, no
idempotency join, no staircase; it bounds adapter-construction transient
failures only. This registry handles RUNTIME tool-call retries keyed by tool
name. The two are deliberately separate surfaces (matching the spec's
bootstrap-vs-runtime distinction at C-RT-02 §5).

**Staircase reading.** Per C-CP-21 §21.2, the transient staircase governs
class-to-class transitions (REFLEXION → RETRY_WITH_BACKOFF → CROSS_FAMILY_FALLBACK
→ LOCAL_TERMINAL → HITL_ESCALATION) keyed on `ValidatorRetryExitClass`. The
full-jitter sleep at stage 2 (RETRY_WITH_BACKOFF) is the per-attempt delay
schedule that this registry computes via `compute_full_jitter_delay_seconds`.
The staircase is the escalation envelope; the jitter schedule is the
within-stage retry cadence.

Per-component landing posture:

- `BreakerStateMachine` — mutable per-(scope, identifier) breaker state.
  closed → open at `fail_threshold` consecutive failures; open → half_open
  when the caller invokes `attempt_half_open(now=...)` AND the cooldown has
  elapsed against the caller-recorded `opened_at`; half_open → closed on
  success, → open on failure, → open (re-armed, uncharged) on an
  INCONCLUSIVE trial via `re_arm_half_open_trial(now=...)`. Wired into the
  C-RT-16 composer at `B-118` / U-RT-154 — before that, `attempt_half_open`
  had zero production call sites and `open` was absorbing for the process.
- `BreakerTransition` — frozen record of one state-machine transition,
  consumed by `emit_breaker_transition_event` to produce the `breaker.tripped`
  span event.
- `compute_full_jitter_delay_seconds(attempt)` — pure full-jitter backoff
  computation. `uniform(0, min(cap, base * 2**attempt))`. Test-injectable
  `rng` parameter makes the staircase-observability test deterministic.
- `RuntimeRetryBreaker` — concrete `RetryBreakerRegistry` Protocol
  implementation. Lazily instantiates breakers keyed by `(BreakerScope, str)`.
- `RetryBreakerStage` — frozen materialization stage carrying the registry.
- `materialize_retry_breaker_stage(config, *, ...)` — composer.

Scope discipline (U-RT-24 boundary held): NO HITL/handoff registries
(U-RT-25/26), NO topology dispatch (U-RT-40), NO audit-ledger writer (U-RT-32 —
the dedup decision is exposed here as a pure function over `dedupe_on_replay`;
the writer that *applies* outcomes lands at U-RT-32), NO collector daemon
(U-RT-29). This registry is a binding-time + reference-time surface only; the
LOOP_INIT orchestrator (U-RT-43+) drives the actual retry loop.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Final

from harness_cp.routing_manifest_residence import RetryPolicy
from harness_cp.validator_fail_taxonomy import ValidatorRetryExitClass
from harness_cp.validator_fail_transient_staircase import (
    StaircaseStage,
    StaircaseTransition,
    advance_staircase,
)
from harness_od.harness_breaker_schema import (
    BreakerCause,
    BreakerScope,
    BreakerState,
    HarnessBreakerEvent,
    emit_breaker_trip_span_event,
)
from harness_od.idempotency_join_dedup import (
    DedupOutcome,
    F2StateLedgerEntry,
    SpanIngestionView,
    dedupe_on_replay,
)
from harness_od.otel_genai_base import EventEmission, SpanRef

from harness_runtime.types import RuntimeConfig

__all__ = [
    "DEFAULT_BACKOFF_TOKEN",
    "DEFAULT_BASE_DELAY_SECONDS",
    "DEFAULT_COOLDOWN_SECONDS",
    "DEFAULT_DELAY_CAP_SECONDS",
    "DEFAULT_FAIL_THRESHOLD",
    "DEFAULT_JITTER_TOKEN",
    "DEFAULT_MAX_ATTEMPTS",
    "DEFAULT_RETRY_POLICY",
    "BreakerStateMachine",
    "BreakerTransition",
    "RetryBreakerBindError",
    "RetryBreakerStage",
    "RuntimeRetryBreaker",
    "compute_full_jitter_delay_seconds",
    "materialize_retry_breaker_stage",
]


# --- Implementation-discretion defaults (C-CP-03 §3.5 spec-deferred) --------

#: Bounded-retry attempt cap default — three attempts (matches C-CP-03 §3
#: chain-advancement bound and the L4 bootstrap-construction default).
DEFAULT_MAX_ATTEMPTS: Final[int] = 3

#: Backoff strategy token default — "full-jitter" per C-CP-03 §3.5.
DEFAULT_BACKOFF_TOKEN: Final[str] = "full-jitter"

#: Jitter mode token default — composes with the full-jitter backoff.
DEFAULT_JITTER_TOKEN: Final[str] = "full-jitter"

#: Full-jitter base delay seconds — 500 ms first-attempt cap before jitter.
DEFAULT_BASE_DELAY_SECONDS: Final[float] = 0.5

#: Full-jitter delay cap seconds — caps exponential growth at 30 s per attempt.
DEFAULT_DELAY_CAP_SECONDS: Final[float] = 30.0

#: Breaker fail-threshold default — closed → open after 5 consecutive failures.
DEFAULT_FAIL_THRESHOLD: Final[int] = 5

#: Breaker cooldown seconds default — open → half-open after 30 s elapsed.
DEFAULT_COOLDOWN_SECONDS: Final[float] = 30.0

#: Default per-tool RetryPolicy applied when the manifest has no entry for a
#: tool. Faithful factor-out of the C-CP-03 §3.5 retry.policy three-field
#: vocabulary; carried as a constant so callers can identity-compare.
DEFAULT_RETRY_POLICY: Final[RetryPolicy] = RetryPolicy(
    max_attempts=DEFAULT_MAX_ATTEMPTS,
    backoff=DEFAULT_BACKOFF_TOKEN,
    jitter=DEFAULT_JITTER_TOKEN,
)


class RetryBreakerBindError(Exception):
    """Bootstrap-time retry/breaker registry bind failure (RT-FAIL-BOOTSTRAP).

    Raised when the manifest carries a malformed `RetryPolicy` — e.g.
    `max_attempts < 1` — or when the bootstrap-default policy is invalid.
    Surfaces at `materialize_retry_breaker_stage`, never at runtime."""


@dataclass(frozen=True, slots=True)
class BreakerTransition:
    """One breaker state-machine transition (C-OD-07 §7.1 input shape).

    Frozen → `Eq`. Carries the data needed to compose a `HarnessBreakerEvent`
    + dispatch `emit_breaker_trip_span_event`. The `(scope, identifier)`
    coordinates identify the breaker; `from_state` / `to_state` name the
    transition; `trigger_count` is the consecutive failure count that drove
    the transition (closed→open case) or zero (open→half_open, half_open→closed).

    `cooldown_seconds` is the machine's static cooldown policy value, carried
    on every transition (v1.32); the caller derives `cooldown_ms` from it only
    on an actual trip (`to_state = OPEN`) — see `emit_breaker_transition_event`.
    `cause` is the caller-supplied `BreakerCause | None` (v1.32) — populated by
    `retry_breaker_fallback._classify_breaker_cause` (B-38) at all 3 real
    `record_failure()` call sites; `None` only for an exception the
    duck-typed `.status_code` classifier doesn't recognize (previously
    vacuous at every call site per `.harness/b19-breaker-ambient-attrs-
    redundancy-analysis.md` §3, before B-38)."""

    from_state: BreakerState
    to_state: BreakerState
    scope: BreakerScope
    identifier: str
    trigger_count: int
    cooldown_seconds: float = DEFAULT_COOLDOWN_SECONDS
    cause: BreakerCause | None = None


@dataclass(slots=True)
class BreakerStateMachine:
    """Mutable per-(scope, identifier) breaker state machine.

    Hand-rolled per CLAUDE.md §3.2 — NO `pybreaker` / `circuitbreaker`.
    Three-state machine matching the OD canonical `BreakerState` enum
    (closed, open, half_open). The state transition discipline:

    - **closed → open**: at `fail_threshold` consecutive failures.
    - **open → half_open**: caller-driven via `attempt_half_open(now)` after
      `cooldown_seconds` elapses. The state machine does not hold a clock —
      the caller (the C-RT-16 composer, per Runtime spec §14.6 step 4) reads
      a monotonic clock and threads `now` in; the machine owns the DEADLINE
      STATE (`opened_at`) because that state is per-`(scope, identifier)`
      and the caller holds no per-breaker storage (one-source-of-truth).
    - **half_open → closed**: on a single success (`record_success`).
    - **half_open → open**: on a failure during the half-open trial
      (`record_failure`), or on an INCONCLUSIVE trial
      (`re_arm_half_open_trial`) whose outcome was not attributable to the
      `{provider, model}` — Runtime spec §14.6.4 matrix cells 3 / 6-9.

    **Trial ownership is EPOCH-GUARDED (§14.6.4, `B-118`).** The permit is not
    only "one admission at a time" — it is "only the admitted caller may
    resolve the trial". `attempt_half_open` bumps `trial_epoch`; outcomes
    presented against a different epoch while `half_open` are DROPPED without
    mutating the machine. Without this, a call admitted while the breaker was
    CLOSED and still awaiting the provider can resolve a trial admitted later
    by someone else — and a stale SUCCESS doing so closes an unhealthy
    breaker. `closed`-state outcomes are unaffected and need no token.

    **`should_attempt()` is the single-trial permit (§14.6.4, `B-118`).**
    `half_open` is a TRANSIENT state that exists only between a trial's
    admission and its outcome, so admitting on `state is not open` would let
    every concurrent sibling dispatch join an in-flight trial. The predicate
    is therefore `state is closed`: the permit holder proceeds on the
    `attempt_half_open` transition it just took (it does NOT re-consult
    `should_attempt`), and every sibling is refused for the trial's duration.

    The caller-threaded-clock model keeps this class deterministic +
    clock-free in tests; nothing here ever calls `time.monotonic()`.
    """

    scope: BreakerScope
    identifier: str
    state: BreakerState = BreakerState.CLOSED
    fail_count: int = 0
    fail_threshold: int = DEFAULT_FAIL_THRESHOLD
    cooldown_seconds: float = DEFAULT_COOLDOWN_SECONDS
    trial_epoch: int = 0
    """Monotonically-increasing admission epoch for half-open trials.

    Incremented by `attempt_half_open` on every admission; the admitted caller
    captures the new value as its **trial token** and must present it to
    resolve the trial. This is the `_epoch` guard the sibling
    `BreakerGuardedSigningBackend` carries for the same reason
    (`harness_runtime.config.audit_signing`): a call admitted while the
    breaker was CLOSED can still be in flight when siblings trip the breaker
    and a LATER call admits a trial, and its stale outcome must not be allowed
    to resolve a trial it does not own. See `record_success` /
    `record_failure` / `re_arm_half_open_trial`."""

    opened_at: float | None = None
    """Caller-supplied monotonic instant of the most recent `open` entry.

    Non-`None` whenever `state is open` for any machine that reached `open`
    through this class's own transitions — the cooldown deadline is
    `opened_at + cooldown_seconds`. `None` while `open` is an ILLEGAL state
    reachable only by assigning `state` directly; `attempt_half_open` treats
    it as "cooldown never elapses" (refuse) rather than silently admitting."""

    def record_failure(
        self,
        *,
        cause: BreakerCause | None = None,
        now: float,
        trial_token: int | None = None,
    ) -> BreakerTransition | None:
        """Record one failure; return the transition iff the state changed.

        - In `closed`: increments `fail_count`; transitions to `open` if the
          count reaches `fail_threshold`.
        - In `half_open`: any failure → `open` (the half-open trial failed).
        - In `open`: no-op (the caller should have checked `should_attempt()`
          before invoking the call); returns `None`.

        `cause` (v1.32) is the caller-supplied `BreakerCause | None` for the
        `harness.breaker.cause` attribute — `retry_breaker_fallback
        ._classify_breaker_cause` (B-38) supplies it at all 3 real call
        sites (previously vacuous at every call site per
        `.harness/b19-breaker-ambient-attrs-redundancy-analysis.md` §3,
        before B-38).

        `now` (v1.114, `B-118`) is the caller's monotonic instant, recorded
        as `opened_at` on every transition INTO `open` so the cooldown
        deadline exists. REQUIRED, deliberately without a default: an `open`
        breaker carrying no open-instant can never recover, and a `None`
        default would make that unrecoverable state the silent fallback.

        Returns the `BreakerTransition` on a state change, else `None`.
        """
        if self.state is BreakerState.OPEN:
            return None
        if self.state is BreakerState.HALF_OPEN:
            if trial_token != self.trial_epoch:
                # STALE outcome (v1.114 §14.6.4): this failure belongs to a
                # call admitted under a different epoch — typically one
                # admitted while the breaker was CLOSED, still in flight when
                # siblings tripped it and a LATER call took the trial permit.
                # Dropped entirely: no transition, and `fail_count` is NOT
                # incremented. This is the SAME treatment an outcome arriving
                # while `open` already gets above, and for the same reason —
                # the machine has already concluded this provider-model is
                # unhealthy, so pre-trip evidence adds nothing, while counting
                # it here would inflate the eventual re-trip's `trigger_count`
                # with evidence from a superseded epoch.
                return None
            prior = self.state
            self.fail_count += 1
            self.state = BreakerState.OPEN
            self.opened_at = now
            return BreakerTransition(
                from_state=prior,
                to_state=BreakerState.OPEN,
                scope=self.scope,
                identifier=self.identifier,
                trigger_count=self.fail_count,
                cooldown_seconds=self.cooldown_seconds,
                cause=cause,
            )
        # state is CLOSED
        self.fail_count += 1
        if self.fail_count >= self.fail_threshold:
            self.state = BreakerState.OPEN
            self.opened_at = now
            return BreakerTransition(
                from_state=BreakerState.CLOSED,
                to_state=BreakerState.OPEN,
                scope=self.scope,
                identifier=self.identifier,
                trigger_count=self.fail_count,
                cooldown_seconds=self.cooldown_seconds,
                cause=cause,
            )
        return None

    def record_success(self, *, trial_token: int | None = None) -> BreakerTransition | None:
        """Record one success; return the transition iff the state changed.

        - In `closed`: resets `fail_count` to 0; no transition.
        - In `half_open`: transitions to `closed`; resets `fail_count` and
          clears `opened_at` (the recovery is complete — §14.6.4 cell 1).
        - In `open`: no-op; returns `None`.
        """
        if self.state is BreakerState.HALF_OPEN:
            if trial_token != self.trial_epoch:
                # STALE success (v1.114 §14.6.4). Dropped: a success from a
                # superseded epoch must NOT close a breaker whose trial is
                # still outstanding. Left unguarded this is the sharpest
                # failure in the family — the stale success closes the
                # breaker, the real trial's failure then lands on a CLOSED
                # machine as one ordinary failure well under `fail_threshold`,
                # and an unhealthy provider-model is silently readmitted.
                # Dropping loses nothing: the outstanding trial supplies
                # fresher, epoch-correct evidence momentarily.
                return None
            self.state = BreakerState.CLOSED
            self.fail_count = 0
            self.opened_at = None
            return BreakerTransition(
                from_state=BreakerState.HALF_OPEN,
                to_state=BreakerState.CLOSED,
                scope=self.scope,
                identifier=self.identifier,
                trigger_count=0,
                cooldown_seconds=self.cooldown_seconds,
            )
        if self.state is BreakerState.CLOSED:
            self.fail_count = 0
        return None

    def attempt_half_open(self, *, now: float) -> BreakerTransition | None:
        """Caller-driven open → half_open transition, gated CONJUNCTIVELY on
        the cooldown having elapsed (v1.114 `B-118`; Runtime spec §14.6 step 4).

        The caller threads a monotonic `now`; this machine holds the deadline
        state (`opened_at` + `cooldown_seconds`) but never reads a clock. The
        transition is admitted iff ALL of:

        1. `state is open`,
        2. `opened_at is not None` (an `open` machine with no recorded open
           instant is the illegal state described at the field — refuse
           rather than admit, so a directly-assigned `state` cannot conjure
           a trial out of a deadline that was never set), and
        3. `now - opened_at >= cooldown_seconds`.

        Returning the transition IS the single-trial permit: the state leaves
        `open`, so a second caller gets `None` from this method, and
        `should_attempt()` is False for every sibling while the trial runs.
        `None` on any refused conjunct — the caller skips the candidate.

        **On admission `trial_epoch` is incremented, and the admitted caller
        MUST capture the new value as its trial token** (read
        `breaker.trial_epoch` immediately after this returns) and present it
        to `record_success` / `record_failure` / `re_arm_half_open_trial`.
        Only the token holder can resolve the trial; a stale outcome from an
        earlier epoch is dropped. A refused admission does NOT increment,
        so a refusal mutates nothing.
        """
        if self.state is not BreakerState.OPEN:
            return None
        if self.opened_at is None:
            return None
        if now - self.opened_at < self.cooldown_seconds:
            return None
        self.state = BreakerState.HALF_OPEN
        self.trial_epoch += 1
        return BreakerTransition(
            from_state=BreakerState.OPEN,
            to_state=BreakerState.HALF_OPEN,
            scope=self.scope,
            identifier=self.identifier,
            trigger_count=0,
            cooldown_seconds=self.cooldown_seconds,
        )

    def re_arm_half_open_trial(
        self, *, now: float, trial_token: int | None = None
    ) -> BreakerTransition | None:
        """Return an INCONCLUSIVE half-open trial to `open` with a FRESH
        cooldown (v1.114 `B-118`; Runtime spec §14.6.4 matrix cells 3 / 6-9).

        A trial whose outcome was NOT attributable to the `{provider, model}`
        — a waived fail-fast per §14.6.3, an audit-signing hard failure, a
        terminal HITL control-flow signal, a dispatch-fence trip, a
        cancellation — produced no evidence about provider health. Under the
        §14.6.3 recovery model it is neither a failure nor a success, so it
        must NOT be charged and must NOT be read as recovery.

        Without this, such a trial would strand the machine in `half_open`,
        where `should_attempt()` refuses everyone and `attempt_half_open`
        returns `None` (state is not `open`) — a NEW absorbing state strictly
        worse than the absorbing `open` that `B-118` exists to remove. The
        caller therefore invokes this on EVERY exit path from a trial; it is
        a no-op (`None`) unless the machine is still `half_open`, which is
        exactly the "neither outcome was recorded" test.

        `fail_count` is deliberately UNCHANGED — an inconclusive trial must
        not walk the breaker toward a threshold it never earned — and
        `trigger_count` is 0, the existing non-trip convention, which
        distinguishes this on the wire from a real half_open → open re-trip
        (whose `trigger_count` is `fail_count >= 1`). The cooldown restarts
        from `now` (operator-ratified 2026-08-08, §14.6.4 cell 3): a
        waived-fault storm would otherwise produce back-to-back trials, since
        the original deadline is already in the past.
        """
        if self.state is not BreakerState.HALF_OPEN:
            return None
        if trial_token != self.trial_epoch:
            # STALE (v1.114 §14.6.4): only the permit HOLDER may re-arm its
            # own trial. A non-owner re-arming would abort a live trial and
            # hand the provider a second call it never earned.
            return None
        self.state = BreakerState.OPEN
        self.opened_at = now
        return BreakerTransition(
            from_state=BreakerState.HALF_OPEN,
            to_state=BreakerState.OPEN,
            scope=self.scope,
            identifier=self.identifier,
            trigger_count=0,
            cooldown_seconds=self.cooldown_seconds,
        )

    def should_attempt(self) -> bool:
        """Return True iff a retry attempt may proceed WITHOUT a trial permit.

        `state is closed` — NOT `state is not open` (narrowed at v1.114,
        `B-118`). `half_open` exists only while a trial is in flight, so the
        old predicate admitted every concurrent sibling into a trial that is
        contracted to be a SINGLE call. The permit holder does not consult
        this method; it proceeds on the `attempt_half_open` transition.
        """
        return self.state is BreakerState.CLOSED


def compute_full_jitter_delay_seconds(
    attempt: int,
    *,
    base_seconds: float = DEFAULT_BASE_DELAY_SECONDS,
    cap_seconds: float = DEFAULT_DELAY_CAP_SECONDS,
    rng: random.Random | None = None,
) -> float:
    """Full-jitter backoff delay per C-CP-03 §3.5 retry.policy.

    `delay = uniform(0, min(cap_seconds, base_seconds * 2**attempt))`. The
    "full-jitter" reading: the per-attempt delay is sampled uniformly between
    zero and the exponentially-growing cap. Hand-rolled per CLAUDE.md §3.2 —
    no tenacity. `attempt` is 0-indexed (the first retry uses `attempt=0`).
    Test injection: pass a seeded `random.Random` via `rng` to make the
    delay schedule deterministic across runs (used at the AC #1 transient-
    staircase observability test).
    """
    if attempt < 0:
        raise ValueError(f"attempt must be ≥ 0; got {attempt}")
    if base_seconds < 0:
        raise ValueError(f"base_seconds must be ≥ 0; got {base_seconds}")
    if cap_seconds < 0:
        raise ValueError(f"cap_seconds must be ≥ 0; got {cap_seconds}")
    bounded = min(cap_seconds, base_seconds * (2**attempt))
    chosen_rng = rng if rng is not None else random
    return chosen_rng.uniform(0, bounded)


@dataclass(slots=True)
class RuntimeRetryBreaker:
    """Concrete `RetryBreakerRegistry` Protocol implementation (U-RT-24).

    Carries the manifest's per-tool `RetryPolicy` mapping, a default policy
    for tools without an explicit entry, and a lazily-grown dict of
    `BreakerStateMachine` instances keyed by `(BreakerScope, identifier)`.

    The registry composes three landed primitives:
    - `harness_cp.validator_fail_transient_staircase.advance_staircase`
      (re-exported via `advance_staircase()` for staircase observability).
    - `harness_od.harness_breaker_schema.emit_breaker_trip_span_event`
      (composed via `emit_breaker_transition_event()`).
    - `harness_od.idempotency_join_dedup.dedupe_on_replay` (re-exported via
      `dedupe_decision()` for AC #3 idempotency-join dedup).

    Lookup discipline: `get_breaker` lazily instantiates a breaker on first
    reference; subsequent references return the same machine (identity-stable).
    """

    retry_policies: dict[str, RetryPolicy]
    default_policy: RetryPolicy
    fail_threshold: int = DEFAULT_FAIL_THRESHOLD
    cooldown_seconds: float = DEFAULT_COOLDOWN_SECONDS
    base_delay_seconds: float = DEFAULT_BASE_DELAY_SECONDS
    delay_cap_seconds: float = DEFAULT_DELAY_CAP_SECONDS
    _breakers: dict[tuple[BreakerScope, str], BreakerStateMachine] = field(
        default_factory=lambda: {}
    )

    def get_policy(self, tool_name: str) -> RetryPolicy:
        """Return the per-tool `RetryPolicy` or `default_policy` if unbound.

        Manifest-driven lookup; falls back to `default_policy` (`DEFAULT_RETRY_POLICY`
        at HEAD) when the tool name is absent from `retry_policies`."""
        return self.retry_policies.get(tool_name, self.default_policy)

    def get_breaker(
        self,
        scope: BreakerScope,
        identifier: str,
    ) -> BreakerStateMachine:
        """Return the breaker for `(scope, identifier)` — lazily instantiate.

        First reference for a `(scope, identifier)` key constructs a fresh
        `BreakerStateMachine` with the registry's threshold + cooldown defaults
        and caches it. Subsequent references return the same machine.
        """
        key = (scope, identifier)
        breaker = self._breakers.get(key)
        if breaker is None:
            breaker = BreakerStateMachine(
                scope=scope,
                identifier=identifier,
                fail_threshold=self.fail_threshold,
                cooldown_seconds=self.cooldown_seconds,
            )
            self._breakers[key] = breaker
        return breaker

    def compute_delay_seconds(
        self,
        attempt: int,
        rng: random.Random | None = None,
    ) -> float:
        """Full-jitter delay per `compute_full_jitter_delay_seconds` and registry
        defaults. `attempt` is 0-indexed."""
        return compute_full_jitter_delay_seconds(
            attempt,
            base_seconds=self.base_delay_seconds,
            cap_seconds=self.delay_cap_seconds,
            rng=rng,
        )

    def advance_staircase(
        self,
        current: StaircaseStage,
        cause: ValidatorRetryExitClass,
        attempt: int,
    ) -> StaircaseTransition:
        """Re-export of `harness_cp.validator_fail_transient_staircase.advance_staircase`.

        Composed at the registry so AC #1 (transient-staircase observability)
        can be verified through the registry surface — the runtime threads
        staircase advancement through this method, never imports the CP
        function directly."""
        return advance_staircase(current, cause, attempt)

    def emit_breaker_transition_event(
        self,
        transition: BreakerTransition,
        parent_span_ref: SpanRef,
        *,
        permanent_fail_repeats: int | None = None,
        tool_id: str | None = None,
        model_version: str | None = None,
    ) -> EventEmission:
        """Emit the `breaker.tripped` event for a state transition (C-OD-07 §7.1).

        Composes `transition` + OD-canonical `HarnessBreakerEvent` + the
        `emit_breaker_trip_span_event` emission. Optional `tool_id` /
        `model_version` correlate the event with the spec's per-model scope
        attributes (C-CP-03 §3.5: "harness.breaker.tool_id — per-model scope
        correlation"). When `tool_id` is omitted at PER_MODEL scope, the
        registry defaults to the transition's `identifier` (the breaker key).

        `cause` / `cooldown_ms` (v1.32) are populated only on a real trip
        (`to_state = OPEN`) — `cooldown_ms` from `transition.cooldown_seconds
        * 1000` (a static duration, always known at a trip); `cause` from
        `transition.cause`, populated by `retry_breaker_fallback
        ._classify_breaker_cause` (B-38) at all 3 real `record_failure()`
        call sites (previously vacuous at every call site per
        `.harness/b19-breaker-ambient-attrs-redundancy-analysis.md` §3,
        before B-38). Neither attribute is meaningful on a recovery
        transition (`half_open -> closed`) or the cooldown-elapsed
        `open -> half_open` transition, so both stay `None` there.
        """
        effective_tool_id = tool_id
        if effective_tool_id is None and transition.scope is BreakerScope.PER_MODEL:
            effective_tool_id = transition.identifier
        is_trip = transition.to_state is BreakerState.OPEN
        event = HarnessBreakerEvent(
            scope=transition.scope,
            from_state=transition.from_state,
            to_state=transition.to_state,
            trigger_count=transition.trigger_count,
            permanent_fail_repeats=permanent_fail_repeats,
            tool_id=effective_tool_id,
            model_version=model_version,
            cause=transition.cause if is_trip else None,
            cooldown_ms=int(transition.cooldown_seconds * 1000) if is_trip else None,
        )
        return emit_breaker_trip_span_event(parent_span_ref, event)

    def dedupe_decision(
        self,
        span: SpanIngestionView,
        ledger_entry: F2StateLedgerEntry | None,
    ) -> DedupOutcome:
        """Idempotency-join dedup decision (C-OD-14 §14.5.1).

        Re-export of `harness_od.idempotency_join_dedup.dedupe_on_replay`.
        AC #3 (idempotency join dedupes a replayed request to a single
        ledger entry) is verified through this surface: a first ingestion
        (`ledger_entry is None`) yields `RECORD_FIRST_INGESTION`; a
        subsequent deterministic-replay span with a matching ledger entry
        yields `DROP_DETERMINISTIC_REPLAY_RE_READ` — collapsing to a single
        ledger entry when the U-RT-32 audit writer consumes outcomes."""
        return dedupe_on_replay(span, ledger_entry)


@dataclass(frozen=True, slots=True)
class RetryBreakerStage:
    """Frozen result of stage 3b CP_ROUTING retry/breaker registry materialization.

    Mirrors the L4 / U-RT-21 / U-RT-22 / U-RT-23 stage shape. The bootstrap
    orchestrator (U-RT-43) binds `registry` to `HarnessContext.retry_breaker`.
    """

    registry: RuntimeRetryBreaker


def materialize_retry_breaker_stage(
    config: RuntimeConfig,
    *,
    default_policy: RetryPolicy = DEFAULT_RETRY_POLICY,
    fail_threshold: int = DEFAULT_FAIL_THRESHOLD,
    cooldown_seconds: float = DEFAULT_COOLDOWN_SECONDS,
    base_delay_seconds: float = DEFAULT_BASE_DELAY_SECONDS,
    delay_cap_seconds: float = DEFAULT_DELAY_CAP_SECONDS,
) -> RetryBreakerStage:
    """Build the retry/breaker registry stage at stage 3b CP_ROUTING.

    Stage 3b composer. Pulls `config.routing_manifest.retry_policies` into the
    registry's per-tool mapping. Validates that each policy's `max_attempts`
    is ≥ 1 at bootstrap (per C-CP-03 §3 chain-advancement bound); a malformed
    policy raises `RetryBreakerBindError` (bootstrap-time, never runtime).

    Bootstrap defaults (`fail_threshold` / `cooldown_seconds` /
    `base_delay_seconds` / `delay_cap_seconds`) are per-runtime implementation
    discretion per C-CP-03 §3.5 spec deferral ("specific breaker trip-threshold
    values per `{provider, model}` pair; specific cooldown duration shape per
    cause class" — deferred). Override via keyword arguments at composer time.

    Empty `retry_policies` is fine — `get_policy(tool_name)` falls back to
    `default_policy` for every tool. The runtime can operate with no per-tool
    overrides at all (the default policy + lazy breakers handle the universe).
    """
    if default_policy.max_attempts < 1:
        raise RetryBreakerBindError(
            f"default retry policy has invalid max_attempts="
            f"{default_policy.max_attempts} (must be ≥ 1)"
        )
    manifest = config.routing_manifest
    retry_policies: dict[str, RetryPolicy] = {}
    for tool_name, policy in manifest.retry_policies.items():
        if policy.max_attempts < 1:
            raise RetryBreakerBindError(
                f"retry policy for tool {tool_name!r} has invalid max_attempts="
                f"{policy.max_attempts} (must be ≥ 1)"
            )
        retry_policies[tool_name] = policy
    # Q2=c reserved registry key injection (U-RT-58, C-RT-16 §"Registry key
    # extension"): the runtime's LLM-dispatch retry policy lives under the
    # reserved ``"llm_dispatch"`` key. Operator manifests cannot supply this
    # key — the validator at `harness_cp.routing_manifest_residence.
    # validate_routing_manifest` raises ``ReservedToolNameError`` if they do.
    # Imported lazily here to avoid a `harness-runtime/lifecycle/retry_breaker`
    # → `harness-runtime/lifecycle/retry_breaker_fallback` → `harness-runtime/
    # lifecycle/retry_breaker` import cycle at module load.
    from harness_runtime.lifecycle.retry_breaker_fallback import (
        DEFAULT_LLM_DISPATCH_RETRY_POLICY,
        RESERVED_LLM_DISPATCH_KEY,
    )

    retry_policies[RESERVED_LLM_DISPATCH_KEY] = DEFAULT_LLM_DISPATCH_RETRY_POLICY
    registry = RuntimeRetryBreaker(
        retry_policies=retry_policies,
        default_policy=default_policy,
        fail_threshold=fail_threshold,
        cooldown_seconds=cooldown_seconds,
        base_delay_seconds=base_delay_seconds,
        delay_cap_seconds=delay_cap_seconds,
    )
    return RetryBreakerStage(registry=registry)
