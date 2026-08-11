# B-145 grounding — GAP 1 is a stale pre-rename alias; GAP 2 splits again

*Filed 2026-08-11 by the loop orchestrator (close-out steps 1+2+3 discharge;
all cites re-read at HEAD this session; codex round-1 corrections absorbed:
cite repair, tool-path reachability re-ground, register-prose sync).*

## The step-1 re-ground (offsets unchanged at HEAD)

`Spec_Harness_Runtime_v1.md` §14.6 step bullets `:4227-4230` and §14.9 bullets
`:5684-5687` stand as the register row describes: five `retry.terminal` values
per path (success / fail-fast / retry / max-attempts / escalate), plus
`retry.backoff_ms` at the retry bullets (:4229, :5685) and
`retry.cause_class = "{class_name}"` at the fail-fast bullets (:4228, :5686).

## GAP 1 — the step-3 check: stale pre-rename aliases, not missing derivations

The close-out ordered: *"CHECK FIRST whether that duplicates … the honest
disposition may be a spec correction retiring the redundant attribute rather
than an emission."* The check hits both GAP-1 keys, with lineage:

- **`retry.backoff_ms` is the RETIRED v1.2-era name.** The CP §3.5 baseline
  row at `Spec_Control_Plane_v1_3.md:76` says it outright: *"was 4 attributes
  at v1.2 — `retry.attempt`, `retry.cause`, **`retry.backoff_ms`**,
  `retry.policy`; now 6 retry-attempt child span attributes per D6 v1.2
  §1.2.2.1"* — the 6-attribute replacement carries **`retry.delay_ms`
  (integer; jittered delay per C9 full-jitter backoff)** and
  **`retry.cause_attribution` (open-set enum from the C5 catalog)**. The
  Runtime step bullets are carrying the stale pre-rename name.
- **The same Runtime sections already bind the §3.5 names.** `:4225` (§14.6
  inner-span bullet) and `:5682` (§14.9) declare the inner span carries the
  canonical C-CP-03 §3.5 6-attribute schema — explicitly naming
  `retry.delay_ms` + `retry.cause_attribution`; the Runtime's own §24-region
  table repeats the rows at `Spec_Harness_Runtime_v1.md:2715-2716`.
- **The producers conform to the §3.5 names.**
  `harness-runtime/src/harness_runtime/lifecycle/retry_breaker_tool.py`:
  `retry.delay_ms` at :245/:263/:277/:291/:301 and
  `retry.cause_attribution = type(exc).__name__` at :292 (the fail-fast
  branch — exactly the "{class_name}" the `retry.cause_class` bullet asks
  for); `retry_breaker_fallback.py` staircase region mirrors.

**Disposition: spec leg** (design-substrate; route per X-AL-3 before
building). Align the four bullet mentions (:4228, :4229, :5685, :5686) to the
§3.5 names — the v1.3 rename the bullets missed — plus the paired
`RETRY_WIRE_REGISTER` re-disposition (the two `emitted=False` rows at
`harness-cp/src/harness_cp/retry_fallback_namespace.py:288-301` become
retired aliases, with `test_unemitted_keys_are_exactly_the_two_b145_registers`
changed in the same commit). Wiring the bullet names as-written would put
duplicate keys on the wire for every retry attempt.

## GAP 2 — re-grounded: the tool half is NOT a telemetry stamp

- **GAP 2a (tool path) — the escalate clause is UNREACHABLE BY
  CONSTRUCTION** (codex round-1 catch). `RetryBreakerToolDispatcher` calls
  `advance_staircase(StaircaseStage.STAGE_1_REFLEXION,
  ValidatorRetryExitClass.TRANSIENT_RETRY, attempt)` with STAGE_1 hard-coded
  on EVERY attempt (`retry_breaker_tool.py:252-256`); the §21.2 table maps
  `(STAGE_1, TRANSIENT_RETRY)` unconditionally to STAGE_2
  (`validator_fail_transient_staircase.py:114-119`) and `attempt` does not
  alter the lookup (`:255` docstring: stage-keyed). The stage is never
  threaded across attempts, so "staircase result escalates beyond
  RETRY_WITH_BACKOFF" cannot occur on this path — the collapsed else at
  `:274-288` genuinely means last-attempt exhaustion today, and a naive
  "escalate" witness could only pass by mocking an impossible transition.
  **Disposition: a spec/control-flow discrepancy needing its own leg** —
  either the tool dispatcher must thread the staircase stage across attempts
  (making Runtime :5685's escalate clause reachable; a behavioral change to
  ground against C-CP-21 §21.2 first) or the escalate clause is
  ratified-unreachable on the tool path and the spec text needs the
  corresponding carve-out. NOT buildable as a per-branch telemetry stamp.
- **GAP 2b (dispatch path) — zero of five terminal values, reachability to
  be re-grounded per-branch before wiring.** `retry_breaker_fallback.py` sets
  `retry.terminal` at exactly one site (:1294, the non-mandated
  `audit-signing-fail-closed`) despite carrying the staircase branch at
  ~:1364-1431. Wiring the five mandated values remains the impl repair, but
  the GAP-2a lesson binds: verify which staircase outcomes each branch can
  actually reach (skip-staircase classes route directly to STAGE_5; whether
  the dispatch loop threads stages across attempts must be read, not
  assumed) and witness only reachable transitions.

## Register effect

`B-145` stays `registered_finding` with this split recorded in its build-state
and mirrored in the register prose block (rendered by
`just forward-register --detail B-145`). Next closer picks up: GAP 1 spec leg;
GAP 2a control-flow/spec leg; GAP 2b impl repair with per-branch reachability
grounding. The step-1 sweep discipline (emission-position, not bare literal)
was honored: producer sites read directly, register declaration home excluded.
