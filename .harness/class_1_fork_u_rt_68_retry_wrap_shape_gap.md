# Class 1 Fork — U-RT-68 retry-wrap shape gap + bootstrap-wiring scope gap

**Filed:** 2026-05-22 at L9-sexies cluster impl arc, post-U-RT-70 landing.
**Status:** ✅ APPLIED 2026-05-22 (status-line refreshed 2026-05-27) — operator ratified Q1=B (new sibling `RetryBreakerToolDispatcher` retry-only, no fallback chain, per-tool breaker scope) + Q2=B2 (new atomic units U-RT-71..U-RT-75 decomposing bootstrap-wiring chain) + Q3=yes (full deferral accepted at filing arc) + Q4=now (resolution arc opens immediately); applied via runtime spec v1.13 → v1.14 + runtime plan v2.11 → v2.12 NEW L9-septies cluster (RuntimeConfig + HarnessContext schema extensions + stage-3a `materialize_mcp_client_host_stage` factory + C-RT-21 `RetryBreakerToolDispatcher` class body + stage-5 `materialize_runtime_tool_dispatcher_stage` factory) + U-RT-68 REWRITTEN at v2.12 per Q1=B + Q1a=(i) ratification (stage-5 callsite consuming new factory); preserves H_T-CP-3/4/5 batch-3 retirement (existing `RetryBreakerFallbackDispatcher` shape untouched); ZERO cross-axis cascade per §5. See `[[fork-u-rt-68-retry-wrap-and-bootstrap-wiring-gap]]`. Species 3 stale-carry per workflow v1.9 §7.4.7.2.

_Original filing footer:_ **Status:** RATIFIED 2026-05-22 — operator ratified Q1=B (new sibling `RetryBreakerToolDispatcher`) + Q2=B2 (new atomic units U-RT-71..N decomposing bootstrap-wiring chain) + Q3=yes (full deferral accepted) + Q4=now (resolution arc opens immediately). Routing target: runtime spec v1.13 → v1.14 (Phase 5 revision via spec-writer) + runtime plan v2.11 → v2.12 (Phase 6 revision via implementation-planner revision-pass).
**Scope:** Phase 7b atomic-unit consumption discipline; halt-execution Class 1
per `Project_Workflow_v1_8.md` §2.7.6 + workspace CLAUDE.md §4.3.
**Surfaced by:** `phase-7-implementation` skill during U-RT-68 (Stage 5
TOOL_STEP binding + retry-wrap registry key) execution.
**Disposition:** U-RT-68 DEFERRED entirely at this arc (no code landed). All 5
ACs gated on fork resolution. The cluster L9-sexies closes at 7/8 units.

---

## 1. The gap

`Spec_Harness_Runtime_v1.md` v1.13 §14.9.2 invariant 4 + §14.9.6 invariant 6
+ §14.9.3 lifecycle stage placement collectively state:

> "Retry/breaker/fallback wrapping applied at C-RT-16 layer by extension: a
> `RetryBreakerFallbackDispatcher` with `inner=ctx.tool_dispatcher` (registry
> key `"tool_dispatch"`) materializes at stage 5 alongside the existing
> `"llm_dispatch"` wrap per C-RT-16 §14.6 D6."
>
> "No retry inside `RuntimeToolDispatcher`. Retry handled at C-RT-16 wrap layer."
>
> "Step-dispatcher table updated: `TOOL_STEP → ctx.tool_dispatcher`. Per
> C-RT-16 §14.6 D6, the registry key `"tool_dispatch"` reserved for
> retry-wrap composition (matching existing `"llm_dispatch"` naming convention)."

The existing `RetryBreakerFallbackDispatcher` at
`harness-runtime/src/harness_runtime/lifecycle/retry_breaker_fallback.py:183`
is hard-typed to LLM-fallback shapes:

```python
@dataclass(slots=True)
class RetryBreakerFallbackDispatcher:
    inner: LLMDispatcher                    # ← typed against LLM dispatcher
    retry_breaker: RetryBreakerRegistry
    fallback_chain: FallbackChain           # ← required; LLM-provider chain
    tracer_provider: Any
    ...
```

The class body reads `policy = self.retry_breaker.get_policy(RESERVED_LLM_DISPATCH_KEY)`
(line 251), iterates `ProviderCandidate` fallback chain (line 259+), and calls
`self.retry_breaker.get_breaker(BreakerScope.PER_MODEL, breaker_identifier)`
(line 267) where `breaker_identifier = f"{candidate.provider}:{candidate.model}"`
(line 266) — all LLM-fallback-shaped semantics.

**For tool dispatch there is no provider/model fallback** — a tool name
resolves to a single MCP server + single tool; there is no "fallback tool".

## 2. The three possible readings

### Reading A — literal reuse (spec literal)

Wrap `RuntimeToolDispatcher` with the existing `RetryBreakerFallbackDispatcher`,
satisfying its `FallbackChain` requirement with a degenerate single-candidate
chain whose `ProviderCandidate(provider, model)` is a meaningless placeholder
(e.g., `("mcp", tool_id)` or `("tool", "n/a")`).

**Problem:** the breaker identifier `f"{candidate.provider}:{candidate.model}"`
becomes meaningless (`"mcp:filesystem.read"` etc.); the breaker scope
`PER_MODEL` doesn't map; the `RESERVED_LLM_DISPATCH_KEY` policy lookup is
wrong (or requires extension to recognize `"tool_dispatch"`). The retry attempts
will "advance candidate" on failure but the candidate is a singleton →
immediate `RetryBreakerFallbackExhaustedError` after the first failure exhausts
the (degenerate) chain. The semantics are wrong despite the type-check passing.

### Reading B — new sibling wrapper

Author a new `RetryBreakerToolDispatcher` class at
`harness-runtime/.../lifecycle/retry_breaker_tool.py` with retry-only semantics
(no fallback): retry on transient failure per a `"tool_dispatch"` registry
policy; raise on terminal failure. Reuses the `RetryBreakerRegistry.get_policy`
+ `BreakerStateMachine` primitives but with a per-tool breaker scope (or no
breaker for the MVP arc).

**Problem:** spec text literally says `RetryBreakerFallbackDispatcher`, not
"a similar wrapper". Reading B violates the literal reading.

### Reading C — extend C-RT-16 to be transport-agnostic

Refactor `RetryBreakerFallbackDispatcher` to be agnostic to LLM-vs-tool by
parameterizing the candidate iteration. Introduce a `CandidateSource` protocol
that returns the iterable to walk; LLM dispatch supplies the existing
`FallbackChain`; tool dispatch supplies a degenerate single-candidate source.
The policy registry key + breaker scope likewise parameterized.

**Problem:** invasive refactor of a load-bearing C-RT-16 surface that has
extensive prior retirement (H_T-CP-3 + H_T-CP-4 + H_T-CP-5 batch 3 retirement
gates on this class's current shape).

## 3. Why U-RT-68 is fully deferred (not partial-landed)

Initial triage considered the `[[halt-route-split-AC]]` partial-land
precedent (4 of 5 ACs met; AC #2 STRUCK pending fork resolution). Deeper
inspection of AC #1's prerequisites surfaced a **second, wider scope gap**:
the unit assumes upstream stage-3a + HarnessContext infrastructure that
**no atomic unit in cluster L9-sexies decomposes**.

### 3.1 The bootstrap-wiring scope gap

For Stage 5 to "instantiate `RuntimeToolDispatcher` bound to
`ctx.tool_dispatcher`" (AC #1), the following must exist:

| Prerequisite | Owner | Status |
|---|---|---|
| `ctx.mcp_client_host` field on `HarnessContext` | runtime spec C-RT-04 | **NOT DECOMPOSED** — neither U-RT-63..67 nor any prior unit modifies the `HarnessContext` schema to add this field |
| `ctx.tool_dispatcher` field on `HarnessContext` | runtime spec C-RT-04 | **NOT DECOMPOSED** — same gap |
| `ctx.per_server_trust_evaluator` field | CP spec § C-CP-27 + runtime C-RT-04 | **NOT DECOMPOSED** — cluster 10-CP-C carriers landed CP-side but not bound to ctx |
| `ctx.mcp_namespace_emitter` field | CP spec § C-CP-27 + runtime C-RT-04 | **NOT DECOMPOSED** — same |
| `materialize_mcp_client_host_stage()` at stage 3a | runtime spec §14.9.3 | **NOT AUTHORED** — spec text pins stage 3a but no factory unit decomposes the operator-supplied `transport_config` ingestion (which MCP servers? what's the bootstrap config schema for the per-server transport list?) |
| `materialize_runtime_tool_dispatcher_stage()` at stage 5 | runtime spec §14.9.3 | **NOT AUTHORED** — spec text pins stage 5 but the operator-supplied `TrustPolicy` + `SandboxDecisionResolver` ingestion is undecomposed |
| `RuntimeConfig.trust_policy` / `RuntimeConfig.sandbox_decision_policy` / `RuntimeConfig.mcp_servers` config schema fields | runtime spec C-RT-02 | **NOT DECOMPOSED** — the bootstrap config carries no tree for these operator inputs at v1.13 |

This is a fundamentally larger gap than the retry-wrap question — it's the
**absence of the operator-config-to-runtime-instance wiring chain** for the
entire cluster L9-sexies primitive surface.

### 3.2 Partial-land would mean either

**(a) Half-land the bootstrap chain too:** add the missing fields + factories
+ config schema in a single mega-commit. **Scope: ~600 LOC across 5 files +
new bootstrap-config decomposition** — well beyond the U-RT-68 atomic-unit
scope, and would itself silently absorb design defects (no decomposed unit
declares the config schema).

**(b) Author the factory + leave invocation skipped:** write
`materialize_runtime_tool_dispatcher_stage()` as a callable factory but do not
modify `stage_5_loop_init.py` to invoke it. **Result:** factory exists,
nothing calls it, AC #3+#4+#5 all STRUCK alongside AC #2. Lands 1 of 5 ACs —
crosses the line from partial-land to non-land. The
`[[halt-route-split-AC]]` precedent requires ≥ 2/3 ACs met for it to count as
partial-land.

### 3.3 Decision: full deferral

Both partial-land options silently absorb design defects, which is the
**worst failure mode** per workspace CLAUDE.md §4.3 ("Silent absorption of
design-phase defects is the worst failure mode — defect absorption at Phase
7 execution contaminates downstream implementation against an invalid spec
and propagates to every dependent atomic unit").

U-RT-68 is therefore **DEFERRED ENTIRELY** at this arc. No code lands. The
cluster closes at 7/8 units; U-RT-68 is filed as RESOLUTION-OWED. The
operator decides at next session:
1. Q1 retry-wrap reading (A/B/C)
2. Bootstrap-wiring scope — author new atomic units (U-RT-71..N) decomposing
   the config schema + stage-3a materialization factories + stage-5 wiring,
   OR amend U-RT-68 ACs to include the bootstrap chain
3. Resolution arc scheduling

## 4. Decision required

| # | Question | Recommendation | Ratification |
|---|---|---|---|
| Q1 | Which retry-wrap reading (A literal / B sibling / C extend) is canonical? | **B** — new sibling `RetryBreakerToolDispatcher` for clean separation; spec amendment at v1.14 to clarify "a C-RT-16-shape wrap (RetryBreaker[Fallback]Dispatcher class family)" rather than literal class reuse | **RATIFIED B 2026-05-22** |
| Q1a | Inside Q1=B, does `RetryBreakerToolDispatcher` use per-tool/per-server breaker or retry-only MVP? Surfaced at spec-writer FM-1 check 2026-05-22: extending `BreakerScope` (canonical 2 values `per_model`/`per_provider` per OD spec §7.1) to add PER_TOOL/PER_SERVER would route to OD back-flow (OD v1.10 + ADR-D6 v1.3 + U-OD-09 re-conformance + OTel cardinality bump) — OUT OF SCOPE for this runtime-spec arc. | **(i)** retry-only MVP at v1.14 (no breaker; defer to future OD-coordinated arc); avoids OD cascade entirely | **RATIFIED (i) 2026-05-22** — `RetryBreakerToolDispatcher` retry-only at v1.14; breaker semantics deferred with explicit pointer at the new D7 contract |
| Q2 | How should the bootstrap-wiring scope gap be closed? | **B2** — decompose new atomic units (U-RT-71..N) for the missing config schema + stage-3a factories + stage-5 wiring; preserves U-RT-68's atomic-unit scope discipline. Alternative B2a: amend U-RT-68 ACs to include the bootstrap chain (~600 LOC scope; violates atomic-unit discipline). | **RATIFIED B2 2026-05-22** |
| Q3 | Is full deferral of U-RT-68 at this arc acceptable? | **Yes** — partial-land would silently absorb design defects per workspace CLAUDE.md §4.3. Full deferral preserves design integrity; cluster L9-sexies closes at 7/8 with explicit gap surfacing. | **RATIFIED Yes 2026-05-22** (no code landed at filing arc) |
| Q4 | When should the resolution arc be scheduled? | After cluster L9-sexies close — pairs naturally with a CP plan v2.18 + runtime spec v1.14 + runtime plan v2.12 co-publication amendment cycle decomposing both the retry-wrap shape AND the bootstrap-wiring decomposition. | **RATIFIED now 2026-05-22** — resolution arc opens at this session |

## 5. Cross-axis impact

NONE. The U-RT-67 dispatcher correctly raises the typed transient errors
(`ToolInvocationTimeoutError` etc.). Without the wrap, those errors propagate
to the driver immediately rather than retrying; the driver maps to
`step-failure: ...` per C-CP-25 §25.3.3.4 (unchanged).

Cluster 10-CP-C consumers (PerServerTrustEvaluator + MCPClientNamespaceEmitter)
operate identically — the wrap is purely the retry layer.

4-OD-D cross-axis blockers (U-OD-39 ← U-RT-67; U-OD-40 ← U-RT-69) — both
already cleared at U-RT-67 + U-RT-69 landings; not gated on this fork.

## 6. Filing footer

| Field | Value |
|---|---|
| Filed at | 2026-05-22, L9-sexies cluster impl arc |
| Filer | phase-7-implementation skill (Claude Opus 4.7) |
| Routing target | Phase 5 spec revision (runtime spec v1.13 → v1.14) + Phase 6 plan revision (runtime plan v2.11 → v2.12) |
| Operator action owed | Q1 ratification (Reading A / B / C); Q2 partial-land confirmation; Q3 resolution scheduling |
| Affected unit | U-RT-68 (partial-landed at this arc with AC #2 STRUCK pending resolution) |
| Implementation arc to resume after resolution | retry-wrap insertion at stage 5 between SyncDispatcherFacade and RuntimeToolDispatcher; will be 1 commit |
| Related memory | `[[halt-route-split-AC-pattern]]` precedent; `[[spec-prose-plan-body-drift-pattern]]` companion |
