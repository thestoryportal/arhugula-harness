# B-19-BREAKER-AMBIENT-ATTRS — ambient-vs-event redundancy analysis + build grounding

**Status:** BUILT (operator-ratified against the grounded recommendation). Spec amendment at `Spec_Operational_Discipline_v1_32.md`.

## 1. The redundancy question (pre-build)

Per `.harness/r-fs-2-final-closure-implementation-plan-v1.md` §5, the drive-to-gate step was: does the existing 7-attribute `harness.breaker.*` **event** schema already answer what the dropped ambient `breaker.cause` / `breaker.cooldown_ms` attributes would add?

**The 7-attribute event schema** (`harness-od/src/harness_od/harness_breaker_schema.py:72-80`) is a single, always-sampled `breaker.tripped` span **event** fired at a state transition — `harness.breaker.scope` / `from_state` / `to_state` / `trigger_count` / `permanent_fail_repeats` / `tool_id` / `model_version`. It is a point-in-time transition record, not a continuously-queryable state surface.

**Internal breaker state** (`harness-runtime/src/harness_runtime/lifecycle/retry_breaker.py`, `BreakerStateMachine`): neither `cause` nor a live "remaining cooldown" exists as tracked state today. `cause` isn't tracked at all. `cooldown_seconds` is a static per-breaker *policy* constant — the state machine is deliberately clock-free (its own docstring: "the state machine does not hold a clock").

**Consumer search.** Grepped CP/OD/runtime/AS/IS/CXA source, the CLI (`app.py`/`admin/`), and dashboard tooling for any real consumer that reads breaker state ambiently (outside the event stream). Found none. The one production breaker-state reader, `retry_breaker_fallback.py:547` `breaker.should_attempt()`, needs only a boolean open/closed gate — its own emitted `retry.skipped` event stays deliberately generic (`"retry.skipped.reason": "breaker-open"`), not even attaching cause detail it could.

**Original recommendation:** skip-and-close — no identified consumer, and building would mean inventing new untracked internal state (a clock, an open-timestamp, a cause field) plus a CLOSED-schema spec-delta, for zero known readers.

## 2. Operator decision

`AskUserQuestion` (2026-07-12): operator chose **build it anyway** — a deliberate FULL-SPEC-completeness choice (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`), not a consumer-driven one. Honored without relitigating (`[[red-team-operator-decision-without-backdooring]]`).

## 3. Build-time grounding: `cooldown_ms` is real; `cause` is vacuous today

**`cooldown_ms` — trivial and real.** CP spec v1.1's own gloss (`Spec_Control_Plane_v1_2.md` line 72) names `breaker.cooldown_ms` as "cooldown duration", not "remaining cooldown". A duration is fully determined at the trip instant (`cooldown_seconds * 1000`, a value the state machine already carries statically) — no clock, no ambient-state subsystem needed.

**`cause` — traced all three reachable classification layers at a real breaker-trip call site** (`harness-runtime/src/harness_runtime/lifecycle/retry_breaker_fallback.py`):

1. **Capability-shortfall pre-check** (`_required_capabilities` / `missing_caps`, lines ~489-532) fires *before* the breaker is ever consulted. A capability-shortfall candidate advances to the next candidate via `_advance_or_exhaust` and never calls `breaker.record_failure()` — `capability_shortfall` is structurally unreachable at a trip site in the current architecture, not merely unimplemented.
2. **Fail-fast branch** (`_classify_provider_exception` returns `None`, line 842-862): only discriminates `LLMDispatchProviderUnreachableError` (routed provider absent from `ctx.providers`) and `LLMDispatchPayloadShapeError` (mis-shaped payload) — both configuration/shape conditions, neither cleanly `auth_failure`.
3. **Transient branch** (`TRANSIENT_RETRY`, everything else): genuinely undifferentiated. `ProviderTransientError`'s own docstring (`providers.py:144-149`) lumps network / rate-limit / 5xx together with no further split available.

**The runtime's only real auth-vs-transient discriminator is bootstrap-only.** `ProviderAuthError` / `_classify_anthropic_ping_failure` / `_classify_openai_ping_failure` (`providers.py`) classify provider **construction-ping** failures at Stage 3a bootstrap ("the stage-3a retry loop will re-attempt" — the docstring's own framing). Traced the call graph: these raise sites live inside `construct_anthropic_adapter` / `construct_openai_adapter` / the external-CLI construct default, invoked only during provider materialization, never from the per-step dispatch path `retry_breaker_fallback.py` wraps. Confirmed no reference to `ProviderAuthError` / `ProviderTransientError` exists anywhere outside `providers.py` itself.

**Conclusion.** None of the four spec-committed values (`rate_limit` / `auth_failure` / `5xx_streak` / `capability_shortfall`) is honestly derivable at a real breaker-trip site with today's runtime. Building a fine-grained provider-exception classifier to make `cause` non-vacuous would itself be the speculative-infrastructure creep the redundancy analysis in §1 already forecloses — a new classifier subsystem built for an attribute with zero known consumers.

## 4. Second operator decision (scope of the amendment)

This is new information the first `AskUserQuestion` could not have surfaced (it only emerges from build-time code tracing, not from the redundancy analysis). Per `[[gate-only-on-meaningful-architecture-change]]` this crossed the bar for a fresh, narrow gate — not a relitigation of build-vs-skip, but a genuine binary on how to land the CLOSED-schema amendment given `cause`'s vacuous-today status:

- (A) Amend the schema once for both attributes — `cooldown_ms` populated, `cause` present as a typed 4-value enum slot, always `None` today.
- (B) Amend now for `cooldown_ms` alone; defer `cause` (and its classifier) to a separate, later amendment.

`AskUserQuestion` (2026-07-12): operator chose **(A)**. Implemented at `Spec_Operational_Discipline_v1_32.md`. A follow-on fine-grained provider-exception classifier arc is registered (not built) at `.harness/post-phase-8-forward-register.md` for if `cause` is ever needed non-vacuously.

## 5. What was built

- `Spec_Operational_Discipline_v1_32.md` — C-OD-07 §7.1 additive amendment, 7→9 attributes.
- `harness-od/src/harness_od/harness_breaker_schema.py` — `BreakerCause` enum + 2 new attributes + emission wiring.
- `harness-runtime/src/harness_runtime/lifecycle/retry_breaker.py` — `cooldown_seconds` + `cause` carried on `BreakerTransition`; computed/threaded at every trip.
- `harness-cp/src/harness_cp/retry_fallback_namespace.py` + `cp_namespace_export_manifest.py` — CP-side composition mirror + cardinality token, 7→9.
- No CP spec file edit — the current CP spec head does not re-table this namespace in prose (delta-only convention); the code-level composition mirror is the load-bearing surface.
