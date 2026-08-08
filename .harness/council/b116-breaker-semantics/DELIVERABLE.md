# B-116 Council DELIVERABLE — ratification package (post-E2b, 2026-08-07)

**Process:** E1 (A1 primaries C9/C11 independent → A2 consultants C1/C7 → B cross-read, seam #5 resolved by C9 concession) → E2 adversarial (8 findings, 1 halt-class) → E2b bounded reconcile (operator-authorized; C9 + C7 corrections). Codex E3 leg: NOT run (weekly quota at floor — recorded deviation; decorrelation carried by the genuine adversarial invocation + the four-voice falsification chain, which caught and corrected errors in every single contribution including its own). Ledger: `.harness/council/b116-breaker-semantics/` (charter, 8 contributions, E2 review).

## Ratified reading (council-unanimous, strengthened by every review round)

**Reading (II): a breaker failure means "this provider-model is unhealthy."**

**Normative test (§14.6 amendment language):** *a fault charges the provider-model breaker only if a half-open trial call could return a different result than the trip did, for a reason attributable to the `{provider, model}` the breaker is keyed to.* "Provider-attested" is shorthand; the recovery-model test governs where they diverge.

## Final per-member table (7 rows after the #2 split)

| # | Member | Disposition | Why (recovery-model test) |
|---|---|---|---|
| 1 | `LLMDispatchProviderUnreachableError` | **don't count** *(demoted at E2b — all 3 raise sites are harness registry lookups)* | A trial re-executes an in-process dict built at bootstrap; genuine provider-down travels the TRANSIENT_RETRY staircase and still charges at `:1072`/`:1091` under either reading. |
| 2a | `LLMDispatchPayloadShapeError` — 3 pre-flight sites | **don't count** — via A-ii-precedent re-type to new `LLMDispatchPayloadShapeInternalError` | Validates the harness's own outgoing payload; candidate-independent (the live `:323` chain-wide charge is B-116's own defect class). |
| 2b | `LLMDispatchPayloadShapeError` — 25 response-parsing sites | **count** | Re-parses a NEW provider response; genuine model-instance degradation. |
| 3 | `.status_code ∈ {401,403}` | **count** | Provider-SDK-only carrier; key rotation genuinely changes the half-open answer. |
| 4 | `MemoryToolExecutionInternalError` | **don't count** | Harness wiring fault, candidate-independent. |
| 5 | `MemoryToolExecutionInputError` | **don't count** *(C9 conceded at cross-read; two independent falsifiers)* | Type admits caller-or-model supply; refusal against harness-held state. |
| 6 | B-115 (b′) conflict *(prospective)* | **don't count — CONDITIONAL** | Ships in the tuple only after B-115's build confirms determinism; racy ⇒ VOID, reroute to C5 retry-classification. Row does not close with B-116. |

**Guard:** negative check over the four-type harness-internal tuple at `retry_breaker_fallback.py:1028` (`record_failure` only), **≈30-35 src lines across two files** (incl. the F-02 re-type) + witnesses (Probes B/C as assertions; positive controls: 401 still charges, a response-parsing shape error still charges; a raise-site partition witness so type drift fails a test; PD-8 mutation probes).

## Binding terms (C7-final, post-E2b)

- **t1+t2:** `retry.breaker_waived.reason` + `retry.breaker_waived.candidate` (string pair, INNER attempt span `harness.runtime.retry_attempt`, absent-by-default; ~4 src lines; zero CP/OD schema delta; filed alongside the `retry.skipped.*` precedent).
- **t3′ (in-venue, weaker):** the §14.6 amendment RECORDS that the non-charged residual rides base-rate `retry.*` and REGISTERS the CP§3.5↔OD§9.2 `fallback.exhausted` gap as a named gate. **The full guarantee is the separate `B-116-t3` leg (OD §9.2 18→19, priced: 1 spec delta + clearance marker + 5 fixture edit points + multi-tenant cardinality-budget check). B-116 RATIFIES now but does not CLOSE until the t3 leg lands** — this is the structure that honors C9's and C11's conditional sign-offs (both said the floor term must be attached; sequencing it as a closure gate attaches it durably).
- **t4:** the guard must hold on any future `breaker_persistence=durable` path (sentence in the amendment).
- **t5:** no HITL gate on this path.

## Build legs implied by ratification

1. **B-116 spec leg:** Runtime §14.6 step-4 amendment (normative test + all-member enumeration with dispositions + t1-t5 sentences + persistence pin) — design-substrate delta + clearance marker.
2. **B-116 impl leg:** the guard + re-type + witnesses (~30-35 src + tests).
3. **B-116-t3 leg:** OD §9.2 18→19 + fixtures (closure gate for the row).
4. **B-115 (b′) leg:** proceeds after 1-2, its type joining the tuple only on confirmed determinism.

## Forward rows to register (none priced into B-116)

C9: R1 wire the dead half-open latch (**priority raised** — the normative test depends on it); R2 no per-provider breaker; R3 vacuous transition-emission fields; R4 rename `LLMDispatchProviderUnreachableError` (Class 2 back-flow, C-RT-14 token); R5 bootstrap-time chain-candidate provider validation. C7: tail-keep span-name-vs-event probe; `validator.fail.permanence` inert; `harness.breaker.tool_id` homonym-in-waiting; `retry.skipped.*` precedent accumulation. C1: `exhaustion_cause` mislabel on breaker-open advance; PERMANENT_FAIL_EXIT label/placement divergence; fall-through-vocabulary home for #5's degradation signal; the undeclared null-topology terminal state. C11/C7: `:683` "demote, never delete" detail-erasure row.

## Honest residuals

- The normative test references a recovery path (`attempt_half_open`) with zero production call sites — the R1 forward row is where that debt lives; the test stands as design intent contracted at OD §7.1.
- The E3 codex leg was skipped (quota floor); if the operator wants the out-of-family check before the spec leg lands, it can run at the spec-leg PR per standard §13.1 discipline (quota resets Sat 8/9).
- C9's third revisit-trigger: admitting any provider-attested class to the fail-fast tuple is an effective 3x trip-threshold tightening for that class — must be stated in the amendment.
