# Class 1 Tension — CP-3 retry/breaker composer underspec (runtime composition seam)

**Filed:** 2026-05-20 — Phase 7 sub-phase 7d (post-U-RT-52 close arc at `2b945ab`; post-tension-audit arc at `09bf26d`).
**Surfaced by:** `phase-7-substitution-retirement` skill batch-3 verification pass against the 26 STILL-BOUNDED + 8 PARTIAL substitutions from `phase-7d-retirement-ledger-v2.md`.
**Substitutions at stake:** H_T-CP-3 (per-layer time-budget + `retry.*` 6-attribute namespace + dual-emission), H_T-CP-4 (fallback chain + cross-family fallback), H_T-CP-5 (routing attribute namespaces — PARTIAL after batch-2). Plus cross-axis cascade §6.3.2 to H_T-CXA-5 (F-CP-01 Stage 3b inversion seam).
**Defect class:** Class 1 — H_T primitive under-specification surfaced at retirement-event evaluation (skill §7 halt condition "Retirement reveals H_T primitive under-specification"). X-AL-3 binds: no silent H_T design extension at Phase 7 execution.

---

## Defect

The runtime composer that wraps the per-step LLM-dispatch site at `RuntimeLLMDispatcher.dispatch` with **retry / breaker / fallback orchestration + `retry.*` span emission** is required for H_T-CP-3 / CP-4 / CP-5 retirement but has **no spec contract** and **no plan unit**.

The state of the surrounding artifacts:

| Surface | What it specifies | What it does NOT specify |
|---|---|---|
| `Spec_Control_Plane_v1_5.md` C-CP-03 §3.5 | `retry.*` 6-attribute namespace; dual-emission discipline; retry-policy schema; full-jitter backoff shape; breaker trip-threshold deferred to implementation discretion | WHICH runtime composer invokes the registry; WHERE in the per-step execution path the wrap happens; WHAT failure-mode mapping applies at composer-vs-driver boundary |
| `Spec_Control_Plane_v1_5.md` C-CP-04 §4 | Fallback chain orchestration: per-step chain composition over (provider, model) candidates; cross-family fallback selection; `fallback.exhausted` emit | WHICH runtime composer invokes `advance_or_raise(chain, failed)`; WHERE the chain advances; WHAT the boundary between composer and driver is on chain-exhaustion |
| `Spec_Harness_Runtime_v1.md` v1.3 C-RT-15 §14.5 | Per-step LLM dispatch composer (U-RT-52 close); per-provider dispatch; GenAI semconv binding; `anthropic.cache_*` subset | **EXPLICITLY excludes retry / breaker / fallback** per Q2a scope discipline; "Composer does NOT implement fallback / retry / breaker per Q2a scope discipline; on provider-side exception, composer propagates the exception unmodified" (spec line 958); "CP-3 retry logic (separate future unit) wraps composer when it lands" (spec line 965) |
| `harness-runtime/src/harness_runtime/lifecycle/retry_breaker.py` (U-RT-24) | Registry materialized at stage 3b; `ctx.retry_breaker` exposed; full-jitter backoff function landed; default thresholds bound at composer args | Module docstring: "RUNTIME tool-call retries keyed by **tool name**" — but the LLM-dispatch site is NOT a tool call; no runtime caller of this registry exists outside bootstrap binding |
| Runtime implementation plan | Lists units U-RT-00 through U-RT-57 (per recent v2 ledger references to U-RT-XX) | NO unit owns the "wrap LLM-dispatch with retry/breaker/fallback" composition seam |

The carrier landed under U-RT-24 ("Retry / breaker / idempotency runtime registry"). The contract landed under C-CP-03 §3.5 (CP spec) and C-RT-15 (runtime spec, per-step composer, retry-excluded). The composition seam **between** the U-RT-24 registry and the C-RT-15 dispatch composer has no owner.

## Evidence — current code state at HEAD (`09bf26d`)

```
# No retry.* span emission in production paths (only library + binding-time)
$ grep -rn "retry\.\|set_attribute.*retry" harness-runtime/src/ | grep -v test
harness-runtime/src/harness_runtime/bootstrap/stage_3b_cp_routing.py:53:    ctx.retry_breaker = retry.registry         # binding only
harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:32:# CP-3 (retry.*) follow-on note (no invocation)
harness-runtime/src/harness_runtime/lifecycle/retry_breaker.py:145:# library docstring referencing C-CP-03 §3.5
harness-runtime/src/harness_runtime/lifecycle/retry_breaker.py:295:# full-jitter backoff helper (no caller in runtime)

# No fallback.exhausted emit; advance_or_raise has zero non-library callers
$ grep -rn "fallback\.\|advance_or_raise" harness-runtime/src/
# (only library declarations + bootstrap binding; no production caller)
```

Per `phase-7d-retirement-ledger-v2.md` §5:

> H_T-CP-3 STILL-BOUNDED — `lifecycle/retry_breaker.py` is binding-time + reference-time surface only; LOOP_INIT orchestrator (U-RT-43+) drives the actual retry loop — **not invoked by `workflow_driver`**; no `retry.*` span emit.
>
> H_T-CP-4 STILL-BOUNDED — `lifecycle/fallback_chain.py` exposes `advance_or_raise`; **no driver call site**; no `fallback.exhausted` emit.

Per `phase-7d-retirement-events-batch-2.md` §3 (CP-5 PARTIAL transition):

> Per X-AL-2 "partial retirement is non-retirement", this is recorded as PARTIAL, not RETIRED. ... Follow-on CP-3 / CP-4 unit will full-retire CP-5 when retry/breaker wrappers land.

## Consequence of silent absorption

Implementing the composer without first authoring the spec contract + plan unit would be **silent H_T design extension** at Phase 7 execution-time — the exact anti-pattern X-AL-3 forbids. Concretely:

1. **No spec contract for the composer.** Where does the composer live (runtime axis as new C-RT-NN? CP axis as C-CP-03 §3.5 amendment?). What is its signature? What failure modes does it surface? What spans does it emit and when? At what boundary does it stop retrying? None of this is specified.
2. **No plan unit owning the work.** No acceptance criteria; no test surface; no dependency edges; no coverage-matrix cell.
3. **Q2a foreclosure.** U-RT-52 fork explicitly ratified Q2a ("per-step composer only; fallback / retry / breaker wrappers explicitly out of scope; CP-3 + CP-4 retirements deferred to follow-on units"). The operator already foreclosed silent in-line addition of these wrappers at U-RT-52.
4. **Recording retirement against an unspec'd composer** would violate X-AL-2 (retirement criterion fidelity) — condition B would be met against an undefined contract.

## Routing target

**Path A (operator-ratified 2026-05-20 inline with this filing):** Runtime axis owns the composition seam.

1. **Spec amendment** — Author new contract in `Spec_Harness_Runtime_v1.md`:
   - Tentative ID: **C-RT-16** — Per-step retry/breaker/fallback composer.
   - Scope: defines the runtime-side composer that wraps `RuntimeLLMDispatcher.dispatch` invocation in the per-step path; consumes `ctx.retry_breaker` + `ctx.fallback_chain`; emits `retry.*` 6-attribute spans per C-CP-03 §3.5; emits `fallback.exhausted` per C-CP-04 §4.2; surfaces typed failure modes on chain exhaustion / breaker open / max-attempts.
   - Spec bump: v1.3 → v1.4.
2. **Plan amendment** — Add new atomic unit to the runtime plan:
   - Tentative ID: **U-RT-58** — Retry/breaker/fallback composer at per-step dispatch site.
   - Dependencies: U-RT-24 (registry), U-RT-52 (per-step dispatch site), C-CP-03/C-CP-04 (contracts).
   - Acceptance criteria: per spec C-RT-16; runtime test suite verifies `retry.*` span emission per attempt + `fallback.exhausted` on chain exhaust + breaker-open propagation + retry-then-success path.
   - Cascade: full-retires CP-5 (PARTIAL → RETIRED); enables §6.3.2 CXA-5 cascade closure once CP-3 satisfies condition B.
3. **Implementation** — Open the arc per `phase-7-implementation` skill discipline against U-RT-58 acceptance criteria. Land in a follow-on arc.

Paths B (CP-axis ownership) and C (defer to Phase 2 / Track B) were considered and rejected: B has larger blast radius (CP spec already at v1.5; another bump compounds); C does not unblock the §6.3.2 cascade and leaves CP-3/4/5 + CXA-5 as bounded-residuals indefinitely.

## Operator decision (2026-05-20)

**Path A ratified.** Sequence:

1. This Class 1 tension record stands as the design-back-flow trigger.
2. Next session (or this session, operator-authorized): author C-RT-16 spec amendment + U-RT-58 plan unit in-CLI per [[design-substrate-divergence]] (workspace `design-substrate/` is canonical) + [[spec-tension-record-pattern]].
3. Following session: implement U-RT-58 per `phase-7-implementation` skill discipline.
4. Following landing: file retirement events for H_T-CP-3 + H_T-CP-4 + full-retire H_T-CP-5 (PARTIAL → RETIRED); update §6.3.2 cascade evaluation (CXA-5 unblocks once CP-3 RETIRED).

**Status:** ✅ CLOSED (status-line refreshed 2026-05-28 Phase 1 status-cascade sweep per workflow v1.12 §7.4.7.3.B) — spec C-RT-16 + plan U-RT-58 landed 2026-05-20 at commit `1f2f015` ("spec+plan: C-RT-16 + U-RT-58 — retry/breaker/fallback composer wrapping C-RT-15"); runtime composer arc resolved. H_T-CP-3/CP-4/CP-5 retirement cascade per memory `[[fork-cp-3-retry-breaker-composer-underspec]]`. Species 3 stale-carry per workflow v1.12 §7.4.7.2.

**Status:** OPEN — awaiting spec + plan amendment; runtime composer implementation arc cannot open until both land. *(historical, predates 2026-05-20 closure)*

## Bounded scope (X-AL-3 discipline)

This tension surfaces **one** runtime composition seam (retry/breaker/fallback at per-step dispatch). It does NOT surface:

- Tool-invocation runtime composer (separate gap — AS-2/AS-4/AS-5/AS-8 / CXA-1 blocker; per v2 ledger §9.2.5).
- HITL gate / validator-framework / sub-agent-dispatch runtime composers (separate gap — CP-10/13/14/20/21/22 / OD-7 blocker; per v2 ledger §9.2.5).
- ResumptionKind 5-class taxonomy emit (within-spec contract; targeted edit, not under-specification; separate route).
- OD-6 sqlite write path (deferred at U-RT-30 via [[fork-trace-storage-pathclass-gap]] Path B; separate route).

Each of those gaps requires its own Class 1 surfacing + spec/plan routing if and when the operator opens that arc.

---

## Audit reconciliation (2026-05-20)

**Verified status:** OPEN — design back-flow active

**Resolving artifact / evidence:** Awaiting C-RT-16 spec amendment + U-RT-58 plan unit landing. This record is the design-back-flow trigger per X-AL-3.

**Audit context:** Filed at the same session as the 2026-05-20 workspace-wide tension audit (33 records reviewed at `09bf26d`). This is a NEW tension surfaced post-audit by the `phase-7-substitution-retirement` skill batch-3 verification pass — not present in the audit-time 33-record set.
