# Class 1 Tension Record — C-RT-16 retry.* attribute schema drift vs CP §3.5 canonical

**Filed:** 2026-05-20 (during U-RT-58 implementation arc)
**Class:** 1 (halt-execution; design-phase artifact requires revision)
**Status:** OPEN — execution halted at U-RT-58 AC #4 verification pending operator ratification
**Surfaced by:** `phase-7-implementation` skill §6 halt-condition + advisor cross-check against CP §3.5 canonical schema

---

## 1. The defect

`Spec_Harness_Runtime_v1.md` v1.4 §14.6 C-RT-16 names a "retry.* 6-attribute namespace" but the attribute names listed do NOT match the canonical CP-axis schema at `Spec_Control_Plane_v1_3.md` §3.5. Per workspace `CLAUDE.md` §1.3 authority chain, CP per-axis spec is canonical for CP-owned namespaces (`retry.*` is a CP-owned namespace per `harness-cp/CLAUDE.md` §1.1). The runtime spec is a downstream consumer and cannot rename CP's attributes.

### Runtime spec v1.4 §14.6 (claimed but drifted)

> "Inner span carries the C-CP-03 §3.5 retry.* 6-attribute namespace (`retry.attempt`, `retry.attempt_count`, `retry.policy_id`, `retry.backoff_ms`, `retry.cause_class`, `retry.terminal`)."

Plan body U-RT-58 AC #4 inherits this list verbatim.

### CP spec v1.3 §3.5 (canonical)

> "**`retry.*` (v1.3 amendment; was 4 attributes at v1.2 — `retry.attempt`, `retry.cause`, `retry.backoff_ms`, `retry.policy`; now 6 retry-attempt child span attributes per D6 v1.2 §1.2.2.1)**: `retry.attempt_number` (integer; 1-indexed), `retry.original_span_id` (string; 16-hex OTel W3C Trace Context format; recovered from F2 state-ledger entry filtered by `idempotency_key`), `retry.delay_ms` (integer; jittered delay per C9 full-jitter backoff), `retry.cause_attribution` (string; open-set enum from C5 cause_attribution catalog per C-CP-21), `retry.fail_class` (enum: `{transient-retry, Reflexion-recoverable, HITL-recoverable, permanent-fail-exit, terminal-fail-exit}`; from C5 5-class fail-class taxonomy), and `engine.replay_disposition` (composition with sub-scope (i); inherits parent operation's value per D1 v1.2 §1.1.1)"

These attributes are also declared as landed constants at `harness_cp/src/harness_cp/retry_fallback_namespace.py:153-189` (`RETRY_ATTEMPT_CHILD_SPAN_SCHEMA`) — a canonical producer surface already exists.

---

## 2. Side-by-side

| Position | Runtime spec §14.6 (drifted) | CP spec §3.5 (canonical) |
|---|---|---|
| 1 | `retry.attempt` | `retry.attempt_number` |
| 2 | `retry.attempt_count` | `retry.original_span_id` |
| 3 | `retry.policy_id` | `retry.delay_ms` |
| 4 | `retry.backoff_ms` | `retry.cause_attribution` |
| 5 | `retry.cause_class` | `retry.fail_class` |
| 6 | `retry.terminal` | `engine.replay_disposition` |

**Zero overlap.** The runtime spec's list resembles the *pre-v1.3* CP attribute set (which had `retry.attempt`, `retry.cause`, `retry.backoff_ms`, `retry.policy`) plus invented additions (`retry.attempt_count`, `retry.policy_id`, `retry.terminal`). The drift appears to be drafting-time slippage — the runtime spec author worked from an older CP attribute set and improvised.

---

## 3. Cross-cutting impact

This attribute drift contaminates retirement criterion B for the H_T-CP-3 substitution:

> H_T-CP-3 RETIRE-READY criterion (per `.harness/phase-7d-retirement-ledger-v2.md` §5 + AC #10 of U-RT-58): "retry.* namespace runtime emits at production execution path."

"retry.* namespace" is CP-canonical, not runtime-spec-named. Emitting drifted names doesn't satisfy the criterion — OD ingestion (per OD spec §1.2 `retry.*` row), audit-ledger composition (per C-CP-21 §21.2 staircase + `retry.fail_class` row), and cost-attribution chain (per C-OD-13 5-step chain dedup keyed on `retry.original_span_id`) all consume the CP-canonical schema. A runtime that emits drifted names breaks downstream consumers silently.

Per workspace `CLAUDE.md` §4.3: **silent absorption of inter-axis spec drift is the worst failure mode.** Halting now is cheaper than three retirements downstream.

---

## 4. Routing options

### Path A (recommended) — CP canonical wins; runtime spec amended

1. Revise `Spec_Harness_Runtime_v1.md` v1.4 → v1.5: §14.6 step 4 narrative re-states the canonical 6-attribute set from CP §3.5 verbatim; explicitly cites `harness_cp.retry_fallback_namespace.RETRY_ATTEMPT_CHILD_SPAN_SCHEMA` as the producer-side reference.
2. Revise U-RT-58 plan body AC #4: attribute list updated to canonical CP-§3.5 set.
3. Re-emit AC #4 assertions in `test_lifecycle_retry_breaker_fallback.py` against canonical names.
4. Wrapper implementation: imports `RETRY_ATTEMPT_CHILD_SPAN_SCHEMA` and emits per the carrier; no hand-coded attribute strings in the runtime module.

**Cost:** small. Implementation structure unchanged (wrapper, candidate loop, breaker integration, factory all correct); only attribute names + value-derivation logic at the per-attempt-span emission site changes.

### Path B — Runtime spec wins; CP spec amended

Strikes the CP-canonical attribute names; replaces with runtime-spec names. **Not recommended** — violates the authority chain (CP per-axis spec is canonical for CP-owned namespaces per `CLAUDE.md` §1.3); contaminates U-CP-07 + U-CP-20 + landed `harness_cp.retry_fallback_namespace` carrier. Worse, it propagates to OD ingestion + audit ledger + cost attribution.

### Path C — Dual emission

Wrapper emits BOTH the CP-canonical 6-attribute set + the runtime-spec drifted set as runtime-axis-private attributes (different namespace). **Not recommended** — schema bloat, OTel attribute-bag thrashing, no consumer for runtime-private attribute set.

---

## 5. Implementation status at halt

The structural implementation is correct and lands cleanly under Path A:

| Surface | Status |
|---|---|
| `harness_runtime/lifecycle/retry_breaker_fallback.py` — wrapper class, candidate loop, breaker pre-check, retry loop, fallback advancement, typed terminal error | Correct |
| `harness_runtime/lifecycle/retry_breaker.py` — reserved-key default injection at materializer | Correct |
| `harness_cp/routing_manifest_residence.py` — `ReservedToolNameError` + validator rejection of reserved name | Correct |
| `harness_runtime/bootstrap/stage_5_loop_init.py` — wraps bare dispatcher; binds wrapper to `ctx.llm_dispatcher` | Correct |
| `harness_runtime/bootstrap/mutable_context.py` — `LLMDispatcher \| None` Protocol-typed field | Correct |
| `harness_runtime/tests/test_lifecycle_retry_breaker_fallback.py` — 14 tests covering ACs #1–#9 | Correct EXCEPT attribute-name assertions at AC #4 |
| `harness_runtime/tests/integration/test_run_smoke.py` — AC #9 wrapper-type assertion at full bootstrap path | Correct |

**The only change Path A requires:**

- ~6 attribute-name strings in `retry_breaker_fallback.py:_run_per_candidate_attempts` (per-attempt span attribute emission).
- ~6 attribute-name strings in the AC #4 test assertions.
- Value-derivation for the new attributes: `retry.attempt_number` is 1-indexed (vs my 0-indexed `retry.attempt`); `retry.original_span_id` requires plumbing the original span's W3C trace-context span ID; `retry.fail_class` is a 5-value enum (vs my freeform string); `engine.replay_disposition` requires composition with engine namespace per D1 v1.2 §1.1.1.

The `retry.original_span_id` and `engine.replay_disposition` attribute value-derivations are the load-bearing ones — they require non-trivial cross-axis lookups (F2 state-ledger filter by idempotency_key; engine-class composition). These may have their own implementation discovery once Path A is ratified.

---

## 6. Routing decision pending

Per `Project_Workflow_v1_8.md` §2.7.6 Class 1 routing + skill §6 halt condition: HALT U-RT-58 execution at AC #4 verification. Surface to operator for path ratification. Do NOT proceed to commit until path is ratified.

Operator decision needed:
- **Path A (recommended):** apply runtime spec v1.5 amendment via `spec-writer` skill; revise U-RT-58 plan body AC #4; resume implementation with canonical attribute names.
- **Path B or other:** explicit operator ratification with documented rationale.

---

## 7. Filing footer

| Field | Value |
|---|---|
| Surfaced at | U-RT-58 AC #4 verification, 2026-05-20 |
| Surfacing skill | `phase-7-implementation` (advisor cross-check) |
| Authority cited | `Spec_Control_Plane_v1_3.md` §3.5 (canonical CP `retry.*` schema); `Spec_Harness_Runtime_v1.md` v1.4 §14.6 (drifted runtime restatement); `harness_cp/retry_fallback_namespace.py:153-189` (landed canonical producer); `CLAUDE.md` §1.3 (authority chain); §4.3 (silent absorption is worst failure mode) |
| Cross-references | `.harness/class_3_tension_c_rt_16_spec_internal_drift.md` (related but distinct — internal §14.6 inconsistency about operator-supplied reserved key); `.harness/phase-7d-retirement-ledger-v2.md` §5 (retirement criterion B for H_T-CP-3) |
| Resolution target | Operator ratification of Path A → `spec-writer` skill applies runtime spec v1.5 amendment → resume U-RT-58 implementation with canonical names |
| Blocking | U-RT-58 commit; H_T-CP-3 retirement (AC #10); §6.3.2 CXA-5 cascade re-evaluation |
