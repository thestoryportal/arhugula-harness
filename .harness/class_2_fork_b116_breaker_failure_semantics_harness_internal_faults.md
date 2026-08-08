# Class 2 Fork — B-116: what does a breaker failure MEAN? (deterministic harness-internal faults vs provider health)

**Filed:** 2026-08-07 · B-116 grounding leg (post-#1264, main @ `35afeda1`), design-phase posture. **Status: ⏳ OPEN — operator ratification gate** (the counting-semantics discriminator changes shipped breaker behaviour; per-member disposition table at §5 is the decision surface).

**Venue:** Runtime spec §14.6 (C-RT-16) step-4 amendment + (optionally) a CP/OD definitional clause. **Coupled row:** B-115 — its recommended (b′) build leg adds a NEW deterministic class to the exact branch this fork re-scopes; **sequence: ratify this fork first, then build B-115 (b′)** (cross-row note, grounding report 2026-08-07).

## §1 The fork

`RetryBreakerFallbackDispatcher`'s fail-fast branch (`harness-runtime/src/harness_runtime/lifecycle/retry_breaker_fallback.py:1028`) calls `breaker.record_failure(cause=None)` for **all five** discriminators in `_classify_provider_exception` (`:272`, tuple at `:358-367` + 401/403 duck-type at `:368-370`), while Runtime §14.6 step 4's prescribing bullet (`design-substrate/Spec_Harness_Runtime_v1.md:4145`) enumerates only **two** — `LLMDispatchProviderUnreachableError` and `LLMDispatchPayloadShapeError`. The other three (401/403 duck-type; `MemoryToolExecutionInternalError`; `MemoryToolExecutionInputError`) were admitted to that branch at B-41 / B-88→U-MEM-28 / B-84 **with no §14.6 amendment**.

Because `BreakerStateMachine.record_failure` (`harness-runtime/src/harness_runtime/lifecycle/retry_breaker.py:219`) increments `fail_count` **unconditionally** and `cause` is telemetry-only (`:228-233`; increments at `:241` HALF_OPEN and `:253` CLOSED), a deterministic harness-internal wiring fault consumes breaker budget on a per-`{provider, model}` breaker (`BreakerScope.PER_MODEL`, identifier `f"{candidate.provider}:{candidate.model}"`, `retry_breaker_fallback.py:662-665`).

**No canonical artifact defines what a breaker failure means.** Verified by direct read across all four owners:

| Source | What it says | Definitional? |
|---|---|---|
| C-CP-03 §3.4 (`Spec_Control_Plane_v1_2.md:389-391`) | breakers attach per-`{provider, model}` pair | Scope only |
| C-OD-07 §7.1 (OD spec §7.1; v1.32 delta) | `trigger_count` = "consecutive failures that tripped the breaker"; `cause` optional | Names "failures", never defines one |
| Runtime §14.6 D2 (`Spec_Harness_Runtime_v1.md:4122`) | retry-eligible iff CP §21.2 transient; fail-fast otherwise | Retry split, not breaker split |
| C-MEM-19 (`Spec_Memory_Substrate_v1.md:913`) | "retry and breaker classification are Control Plane and Runtime surfaces, which this contract neither owns nor amends" | Explicit disclaimer |

**The silence is the finding** — exactly the branch the register row's close-out step (2) named.

## §2 Grounded corrections to the row (carried here so the filing, not the row, is cited forward)

1. **Scope correction:** the row says the failure is recorded "against that candidate's PROVIDER". Reality: `BreakerScope.PER_MODEL` with identifier `provider:model` (`retry_breaker_fallback.py:662-665`); `BreakerScope.PER_PROVIDER` exists in the enum (`harness-od/src/harness_od/harness_breaker_schema.py:105-112`) but **no PER_PROVIDER breaker is constructed anywhere**.
2. **Class-name correction:** `record_failure` lives on **`BreakerStateMachine`** (`retry_breaker.py:192-193`, method at `:219`), not "BreakerRegistry" (no such class; the registry type is `RuntimeRetryBreaker` at `:343` and has no `record_failure`).
3. **Mis-cite correction:** the row cites "C-CP-21" for the breaker contract. C-CP-21 (`Spec_Control_Plane_v1_2.md:1829`) is the pre-HITL escalation order + `validator.fail.*` taxonomy. The breaker contract is **C-CP-03 §3.4 + §3.5** (the `harness.breaker.*` namespace at `:402`).

## §3 Probe evidence (executed 2026-08-07 at `35afeda1`; transcripts from the grounding leg)

- **Probe A** — `_classify_provider_exception(MemoryToolExecutionInternalError) → None` fail-class path; `_classify_breaker_cause(...) → None` (`:404-406`): the fault is not mis-tagged; it reaches `:1028` with `cause=None`. (Row claim C4 confirmed.)
- **Probe B** — 3-candidate chain (`anthropic:claude-test-1`, `anthropic:claude-test-2`, `openai:gpt-test-1`), `fail_threshold=5`, ONE dispatch with an unset `RuntimeMemoryContext.record_scope`: terminal `RetryBreakerFallbackExhaustedError`; **all three breakers** record `fail_count=1` — the fault is candidate-independent, so the chain advance (`:726-740`) burns one failure on **every candidate breaker across both providers**.
- **Probe C** — same chain, `fail_threshold=3`, three dispatches: **every breaker in the chain reaches `state=open`, `should_attempt=False`** — one harness-side misconfiguration opens all provider breakers.
- **Probe D** — the landed witness `test_lifecycle_retry_breaker_fallback.py:1089-1170` (`…fail_fast_trip_carries_no_breaker_cause`) already GREEN-asserts a harness-side argument refusal tripping a breaker to `open` with `cause=None`. Nothing at HEAD prevents the harm; a shipped test blesses it.
- Whole-`src` sweep: exactly **three** `record_failure` call sites (`retry_breaker_fallback.py:1028`, `:1072`, `:1091`), all `PER_MODEL`; fail-fast reaches only `:1028`.

## §4 The discriminator to ratify

Does a breaker failure count mean:

- **(I) "this CANDIDATE failed to produce a result"** — the internal fault legitimately counts; the chain is right to advance; current behaviour is CORRECT and §14.6 step 4 just needs its enumeration completed (doc-only amendment). Cost: a repeated harness-side misconfiguration opens every healthy provider's breaker (Probe C) and the operator's breaker telemetry reads as provider unhealth.
- **(II) "this PROVIDER-model is unhealthy"** — deterministic harness-internal members must NOT count; fix = skip `record_failure` (or record on a non-provider scope) for those members only. Cost: a real fault class loses breaker-visible accounting (mitigated: those members already fail fast and surface as typed errors + report-log lines).

## §5 Per-member disposition table (the decision surface — any change MUST be per-member; a wholesale change would silently stop counting real provider auth failures)

| # | Fail-fast member | Nature | Recommended disposition |
|---|---|---|---|
| 1 | `LLMDispatchProviderUnreachableError` | genuine provider fact | **count** (unchanged; already §14.6-named) |
| 2 | `LLMDispatchPayloadShapeError` | provider-boundary fact | **count** (unchanged; already §14.6-named) |
| 3 | `.status_code ∈ {401, 403}` duck-type (B-41) | provider-credential fact | **count** (a real auth failure at the provider) |
| 4 | `MemoryToolExecutionInternalError` (B-88/U-MEM-28) | harness-internal by construction | **don't count** under reading (II) |
| 5 | `MemoryToolExecutionInputError` (B-84) | harness-internal by construction | **don't count** under reading (II) |
| (6) | *prospective:* B-115 (b′) conflict type | harness-internal (ledger idempotency) | same disposition as #4/#5 — decided HERE, before the B-115 build leg |

**Recommendation: reading (II) with the per-member table above** — the breaker exists to protect against provider unhealth (C-CP-03 §3.4 keys it to `{provider, model}`); letting a candidate-independent internal fault open every provider's breaker inverts the mechanism's purpose (Probe C is the harm made concrete). Members #1–#3 keep counting; #4/#5/(#6) stop. Council dyad (C1/C9 ⊥ C11) per the row's conditional: under-counting fails to protect a genuinely failing chain vs over-counting opens healthy providers on operator misconfiguration — the per-member split IS the dyad's resolution (each member lands on the side of the line its nature dictates).

## §6 If ratified toward (II) — priced build leg

~12 src lines at `retry_breaker_fallback.py:1016-1028`: a `_is_deterministic_harness_internal(exc)` guard on the `record_failure` call ONLY (advance/telemetry unchanged). Runtime §14.6 step-4 bullet amendment enumerating all five members with their breaker dispositions (spec leg, clearance marker). ~70 test lines: Probes B + C as assertions (internal fault leaves all chain breakers at `fail_count=0`), a positive control (raw 401 still records), the Probe-D witness re-pinned to the new behaviour, and a PD-8 mutation probe (revert the guard → witnesses fail). If ratified toward (I): §14.6 enumeration amendment only (doc-only spec leg); Probe-D witness stands.

## §7 Cross-refs

Register row `B-116` (this filing discharges its grounding step); `B-115` (coupled — sequence after this ratification); B-41 / B-84 / B-88 (the legs that grew the fail-fast set); `.harness/merge-gate-log.md` #1260/#1263 rows (the gate that surfaced adjacent breaker-telemetry accuracy concerns).
