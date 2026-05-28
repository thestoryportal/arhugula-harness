# Class 1 Tension — U-CP-07 acceptance #7 (dual-emission discipline)

**Status:** ✅ PARTIALLY-CLOSED (verified workspace-wide audit 2026-05-20; status-line refreshed 2026-05-27) — U-CP-07 partial-lands (schemas A/1–6 landed; AC #7 + 5 emission tests struck per `[[halt-route-split-AC-pattern]]`); dual-emission discipline routed to future OTel emitter unit as bounded X-AL-2 residual, NOT open defect. Species 3 stale-carry per workflow v1.9 §7.4.7.2.

| Field | Value |
|---|---|
| Unit | U-CP-07 — Declare `fallback.*` + `harness.breaker.*` + `retry.*` namespaces |
| Sub-phase | 7b — CP axis-stream |
| Fork class | Class 1 (halt-execution — partial-land split) |
| Filed | 2026-05-16 |
| Actor | phase-7-implementation |
| Disposition | **PARTIAL LAND** — schema declarations landed; acceptance #7 + 5 emission tests struck |

## Defect

U-CP-07 (CP plan v2.3 §2.1, canonical-current body) bundles two surfaces of
differing materializability at a single L0 unit:

**(A) Materializable now — data declarations.** `FallbackAttributeSchema` /
`FALLBACK_NAMESPACE_SCHEMA` (9 entries), `HarnessBreakerAttributeSchema` /
`HARNESS_BREAKER_NAMESPACE_SCHEMA` (7), `RetryAttributeSchema` /
`RETRY_NAMESPACE_SCHEMA` (6), `RetryAttemptEventField` /
`RETRY_ATTEMPT_EVENT_SCHEMA` (3), `RetryCause` enum (5). Pure namespace /
attribute-schema declarations — fully specified, no runtime substrate
required. Acceptance criteria #1–#6 all map to these declarations.

**(B) Not materializable at U-CP-07 — runtime emission discipline.**
Acceptance **#7** (v2.3 new) asserts a *runtime emitter* invariant:

> the retry-attempt mechanism MUST emit BOTH the parent-span `retry.attempt`
> event AND the new retry-attempt child span at each retry … retry-attempt
> child spans are CHILDREN of the parent operation span (linked via
> `parent_span_id`); attempts are SIBLINGS to each other.

This is a behavioural contract over an **OTel span emitter** — a runtime
component. No emitter primitive exists at sub-phase 7b L0. U-CP-07's declared
`Files affected` are four *namespace-schema* declarations; it declares no
emitter, no span-producing function, no `parent_span_id`-linking mechanism.
The 5 tests that exercise #7 require a live emitter:

- `test_dual_emission_discipline_required`
- `test_retry_attempt_child_topology_under_parent_operation`
- `test_retry_original_span_id_self_reference_at_attempt_1`
- `test_retry_original_span_id_attempt_1_span_id_at_attempts_2_through_n`
- `test_engine_replay_disposition_inheritance_from_parent_operation`

These cannot be satisfied by a schema-declaration unit. Bundling a runtime
discipline AC into an L0 type-declaration unit is the halt-route-split-AC
pattern (`.harness/halt-route-split-ac-pattern.md`).

## Resolution applied (halt-route-split-AC)

Per the workspace-memory halt-route-split-AC pattern: **partial-land** the
materializable surface (A); **strike** the unmaterializable AC (#7) and its 5
emission tests; route the struck discipline to its proper consumer.

- **Landed:** `harness_cp/retry_fallback_namespace.py` — all schema/enum
  declarations; acceptance #1–#6 fully covered by tests in
  `tests/test_retry_fallback_namespace.py`.
- **Struck from U-CP-07:** acceptance #7 + the 5 emission tests above.
- **Routing target:** the retry-attempt dual-emission discipline belongs to a
  downstream **OTel emission unit** — the span emitter that produces
  `retry.attempt` events + retry-attempt child spans. U-CP-12 (`Implements
  C-CP-05 §5.2/§5.4`) consumes the retry-surface *sampling* discipline but is
  itself a sampling-table declaration, not an emitter. No L0–L2 CP unit owns
  span *emission*. The dual-emission discipline must be re-homed to a
  project-authored emitter unit (GUARDRAIL-class, per `Plan_Executability_Audit_v1.md`
  §3.3) or a future CP plan revision must add an emission unit and move
  acceptance #7 there.

## Recommended back-flow

CP plan revision (Phase 6 plan revision-pass): relocate U-CP-07 acceptance #7 +
its 5 emission tests to a dedicated retry/lifecycle span-emitter unit. Until
that unit is specified, the dual-emission discipline is a documented
carry-forward; the U-CP-07 schemas it would consume are landed and stable.

## Scope of the strike

`FALLBACK_NAMESPACE_SCHEMA`, `HARNESS_BREAKER_NAMESPACE_SCHEMA`,
`RETRY_NAMESPACE_SCHEMA`, `RETRY_ATTEMPT_EVENT_SCHEMA`, `RetryCause` — all
landed, unaffected. Only the runtime-emission behavioural contract is struck.
The struck AC is non-blocking for every downstream consumer of the *schemas*
(U-CP-12 retry-surface sampling consumes the schema shapes, not the emitter).

---

## Audit reconciliation (2026-05-20)

**Verified status:** RESOLVED

**Resolving artifact / evidence:** U-CP-07 partial-lands (schemas A/1–6 landed; AC #7 + 5 emission tests struck per halt-route-split-AC pattern). Dual-emission discipline routed to future OTel emitter unit — bounded residual, not open defect.

**Audit context:** Workspace-wide tension-record audit 2026-05-20 (post-U-RT-52 merge to main at 2b945ab). 33 records reviewed against current code + spec state. Result: 28 RESOLVED, 5 DEFERRED-PARTITION, 0 STILL-OPEN. The 'Status' line earlier in this record predates the audit; this section is the current verified state.
