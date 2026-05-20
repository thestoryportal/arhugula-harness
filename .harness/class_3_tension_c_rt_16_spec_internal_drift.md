# Class 3 Tension Record — C-RT-16 §14.6 spec-internal drift

**Filed:** 2026-05-20 (during U-RT-58 implementation arc)
**Class:** 3 (informational; non-blocking)
**Status:** OPEN — bounded residual; recommended for resolution at next runtime-spec amendment
**Surfaced by:** `phase-7-implementation` skill against U-RT-58 acceptance criteria

---

## 1. The drift

Within `design-substrate/Spec_Harness_Runtime_v1.md` v1.4 §14.6 C-RT-16, two consecutive paragraphs make mutually inconsistent claims about the reserved `"llm_dispatch"` registry key:

### Paragraph A (one paragraph above the inconsistency)

> "tools may not declare a tool named `"llm_dispatch"` (enforced at manifest-validation time via a typed `ReservedToolNameError`)."

The reservation paragraph asserts that operator manifests cannot supply an entry under the `"llm_dispatch"` key — the validator rejects it.

### Paragraph B (the inconsistent sentence)

> "The reserved key's `RetryPolicy` is operator-supplied at `RuntimeConfig.routing_manifest.retry_policies["llm_dispatch"]`; if absent at runtime, the registry's `materialize_retry_breaker_stage` materializer binds a default `RetryPolicy(...)`."

The materializer-default paragraph asserts that the operator CAN supply the policy at exactly the location that paragraph A says is forbidden.

The two readings are mutually inconsistent. Plan U-RT-58 AC #8 unambiguously aligns with paragraph A: "assert `ReservedToolNameError` raised at manifest-validation time if a tool is named `"llm_dispatch"` in `RoutingManifest.retry_policies`."

---

## 2. Resolution applied at U-RT-58 implementation

Per `[[spec-prose-plan-body-drift-pattern]]` (operate against the testable AC; surface the spec drift):

- **Validator rejects** operator-supplied `"llm_dispatch"` in `retry_policies` (paragraph A reading).
- **Materializer injects** the reserved key + default policy into the registry's internal `retry_policies` map post-validation (NOT back into the manifest, which is frozen). The default `RetryPolicy(max_attempts=3, backoff="full_jitter", jitter="full_jitter")` is declared as `DEFAULT_LLM_DISPATCH_RETRY_POLICY` at `harness_runtime/lifecycle/retry_breaker_fallback.py`.
- **Operator override** of the LLM-dispatch policy is NOT exposed at MVP. The "deferred to implementation discretion" clause at spec §14.6 ("Whether `RetryPolicy.max_attempts` defaults are operator-overridable per-step or per-runtime — MVP suggests per-runtime only; per-step override is a follow-on") explicitly defers operator-override surface to a follow-on arc.

This resolution is type-safe, test-covered (3 new tests at `test_lifecycle_retry_breaker_fallback.py`), and consistent with X-AL-3 (no design extension at execution time — no new `RuntimeConfig` field added).

---

## 3. Recommended spec amendment

At the next `Spec_Harness_Runtime_v1.md` revision pass:

**Strike paragraph B's sentence:** "The reserved key's `RetryPolicy` is operator-supplied at `RuntimeConfig.routing_manifest.retry_policies["llm_dispatch"]`".

**Replace with:** "The reserved key's `RetryPolicy` is injected by `materialize_retry_breaker_stage` post-validation; the default is `DEFAULT_LLM_DISPATCH_RETRY_POLICY` per `harness_runtime/lifecycle/retry_breaker_fallback.py`. Operator-supplied per-runtime override is a follow-on arc per the 'Deferred to implementation discretion' clause."

Update the §14.6 "Deferred to implementation discretion" item that currently reads "Whether RetryPolicy.max_attempts defaults are operator-overridable per-step (via binding.retry_policy_override) or per-runtime (via RuntimeConfig.routing_manifest.retry_policies['llm_dispatch'])" to instead point at a separate operator-override surface — specific field shape deferred (the architectural commitment lives with the operator, not this informational record).

---

## 4. Routing decision

**Class 3 (informational; non-blocking).** The spec drift is internally consistent at the test surface (paragraph A + AC #8) so implementation proceeds. The recommended amendment is a clarity fix at the next runtime-spec revision; no architectural commitment changes.

Per `Project_Workflow_v1_8.md` §2.7.6 Class 3 routing: log at Phase 7 execution log + this `.harness/` record; non-blocking. Update at next spec amendment.

---

## 5. Filing footer

| Field | Value |
|---|---|
| Surfaced at | U-RT-58 implementation, 2026-05-20 |
| Surfacing skill | `phase-7-implementation` |
| Resolution authority | Operator-ratified at U-RT-58 advisor pass (advisor recommendation 2026-05-20: "Apply against AC #8; don't add a new RuntimeConfig field for operator override — that's X-AL-3 design extension at execution time") |
| Cross-references | `Spec_Harness_Runtime_v1.md` v1.4 §14.6; `.harness/phase-2-session-3-track-a-atomic-decomposition.md` v2.3 U-RT-58 AC #8; `harness_runtime/lifecycle/retry_breaker_fallback.py`; `harness_cp/routing_manifest_residence.py` |
| Resolution target | Next `Spec_Harness_Runtime_v1.md` amendment (deferred; not Phase-7-blocking) |
