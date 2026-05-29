# Class 1 Tension — Sibling-ledger `emit_sibling_ledger_entry` child-agent-recursion-boundary

| Field | Value |
|---|---|
| Status | PROPOSING |
| Filed | 2026-05-29 |
| Filed by | Operator + Claude (post-PR-#63 close, design-phase posture) |
| Class | 1 (architectural; firing-site-absence at LANDED substrate; sibling to `[[class_1_tension_hitl_rewrite_tool_call_pre_dispatch_hook_absence]]` co-published this arc — DISTINCT structural shape per advisor 44th application) |
| Triggers | Upstream blocker (3) for H_T-RT-35 RETIRE-READY per checkpoint 2026-05-29; U-CP-34 STRUCK at runtime plan v2.37 AC #11 empirical anchor |
| Halt scope | None at execution-time (composer LANDED + wiring LANDED; ZERO production reads); back-flow scope for design-phase decision on recursion-boundary semantics |

---

## §1 Finding

`RuntimeCpIsWiring.emit_sibling_ledger_entry` at `harness-runtime/src/harness_runtime/lifecycle/cp_is_wiring.py:112` is LANDED at U-RT-110 (PR #45 merged `35744ab` 2026-05-29). The CP-axis composer `emit_sibling_ledger_entry` at U-CP-34 is also LANDED. 19 test refs across `harness-cp/tests` + `harness-runtime/tests`; ZERO production callers anywhere in `harness-*/src/`.

Per CP spec v1.26 §C-CP-15 §15.1 (preserved verbatim from v1.2 baseline), `emit_sibling_ledger_entry` binds emission to **per-sibling tool-call events INSIDE child agent execution** with `response_hash = sha256(canonicalize(tool_output))`. The `tool_output` does NOT exist at the parent dispatch moment (`harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py:511` `RuntimeSubAgentDispatcher.dispatch`); the parent sees a `SubAgentDispatchPayload → SubAgentDispatchResult` boundary with summary-level outputs, NOT per-tool-call siblings.

Runtime plan v2.37 STRUCK U-RT-111 AC #11 (sibling-ledger emission firing-site at `sub_agent_dispatch.py:716` post-step-8 success path) on primitive-scope-mismatch finding: re-purposing brief-hash as `response_hash` would conflate two hash-roles + defeat §15.1 per-tool-call semantic. The composer is structurally unfireable at the current H_T parent-dispatch boundary because the harness boundary does not see into child-agent recursion.

---

## §2 Empirical orientation (HEAD `9ddb9ba`)

| Surface | Path | State |
|---|---|---|
| CP composer `emit_sibling_ledger_entry` | `harness-cp/src/harness_cp/*` (U-CP-34) | LANDED |
| Runtime wiring `RuntimeCpIsWiring.emit_sibling_ledger_entry` | `harness-runtime/.../lifecycle/cp_is_wiring.py:112` | LANDED |
| Production callers | (none) | **ABSENT** |
| Test callers | 19 refs across both axes | exercises CP §15.1 canonical shape (`tool="Bash"`, `canonical_args='{"cmd":"echo hi"}'`) |
| Parent dispatch site `RuntimeSubAgentDispatcher.dispatch` | `harness-runtime/.../lifecycle/sub_agent_dispatch.py:511` | LANDED; sees `SubAgentDispatchPayload → SubAgentDispatchResult` summary boundary |
| Child-agent recursion mechanism | `sub_agent_dispatch.py:42` cite says `INFERENCE_STEP → ctx.llm_dispatcher` wrap | child agents currently are single-LLM-inference, NOT recursive harness instances |
| CP spec §C-CP-15 §15.1 | `design-substrate/Spec_Control_Plane_v1_26.md` (v1.2 baseline preserved) | binds to per-sibling tool-call events INSIDE child agent execution; `response_hash = sha256(tool_output)` |
| Runtime plan v2.37 AC #11 | `Implementation_Plan_Harness_Runtime_v2_37.md` | STRUCK on primitive-scope mismatch |

---

## §3 Readings

### Reading A — Spec amendment: bind §15.1 emission to parent dispatch site

Amend CP spec §C-CP-15 §15.1 to widen emission scope from per-sibling-tool-call to per-sub-agent-dispatch-boundary. `response_hash` would be sourced from the dispatch-result summary (e.g., `SubAgentDispatchResult.summary_hash` or brief-hash proxy). Fires at `sub_agent_dispatch.py:716` post-step-8 success path.

**Pros:** unblocks U-RT-111 AC #11 + closes the firing-site at established control flow; smallest impl surface (single callsite addition).

**Cons:** defeats v2.37 STRIKE rationale (the STRIKE explicitly rejected this reading); fundamentally changes §15.1's per-tool-call semantic to per-dispatch semantic; brief-hash-as-response_hash conflates F2 dispatch-entry hash-role with §15.1 ledger-emission hash-role; loses per-sibling auditability that §15.1 was designed for.

### Reading B — Recursive-harness architecture

Promote child agents from single-LLM-inference wraps to full harness loop instances. Child harness instance has its own ledger writer reference (or a shared parent-ledger writer reference) and emits `sibling_ledger_entry` at each tool-call event within its execution. Parent harness sees the child's emissions via shared ledger.

**Pros:** preserves §15.1 per-sibling-tool-call semantic; matches CP spec's canonical intent; opens path for full recursive-harness composition (multi-level sub-agent topology per ADR-D4 v1.1 §1.1).

**Cons:** very large architectural surface — touches CP TopologyPattern 6-class enum semantics, sub_agent_dispatch impl, cross-axis state-ledger threading, child-harness lifecycle, error propagation across recursion levels, cost-attribution across recursion levels. Likely requires multiple ADR-class decisions + spec amendments at CP + IS + AS + OD axes. Not an MVP arc.

### Reading C — Bounded-defer per X-AL-2; structurally-unfireable-at-MVP

Acknowledge that `emit_sibling_ledger_entry` is structurally unfireable at the current MVP H_T boundary because the parent-child dispatch boundary does not expose per-sibling tool-call events. Defer the firing-site arc until the recursive-harness architecture decision is made (Reading B path) OR explicitly accept §15.1 semantic narrowing (Reading A path) at a future spec revision arc. Maintain U-CP-34 LANDED-but-never-fired status per X-AL-2 bounded-residual carry-forward.

**Pros:** matches v2.37 STRIKE precedent + Reading D framing at the sibling HITL fork; preserves catalogue coherence (do not author premature firing-site against not-yet-built downstream substrate); aligns with `Phase_7_Meta_Architecture_v1.md` §6 self-hosting milestone gradient (recursive-harness composition is a downstream milestone).

**Cons:** does not advance H_T-RT-35 toward RETIRE-READY at this arc; carries one of the 5 upstream blockers without closure; U-CP-34 LANDED substrate sits unused in the binary.

### Reading D — Reframe §15.1 emission scope (e.g., per-sub-agent-summary instead of per-sibling-tool-call)

Spec amendment that REFRAMES §15.1 from per-sibling-tool-call to per-sub-agent-summary semantic. Different from Reading A: not widening emission scope to parent dispatch (which conflates hash-roles), but explicitly redefining what "sibling" means — siblings of the parent sub-agent dispatch event, not siblings within child agent execution. `response_hash` sources from a well-defined parent-visible summary contract.

**Pros:** preserves §15.1 structural shape (per-event ledger entry; canonical hash discipline); avoids brief-hash conflation; firing-site at parent dispatch is reachable.

**Cons:** requires fresh spec contract authoring (what IS a "sub-agent summary"? what gets hashed?); changes §15.1 canonical reading at a depth that may cascade to CP-axis siblings (§15.2 / §15.3 / etc.); requires architectural Q-set on summary shape; risks being a workaround for the more fundamental Reading B architecture.

---

## §4 Q-set for operator ratification

| Q | Decision space |
|---|---|
| Q1 | Reading: A (spec amendment widening to parent dispatch) / B (recursive-harness architecture) / C (bounded-defer) / D (reframe §15.1 to per-sub-agent-summary) |
| Q2 (if A) | Hash-role conflation: (i) accept brief-hash-as-response_hash conflation as MVP simplification; (ii) define separate `summary_hash` field at `SubAgentDispatchResult` |
| Q3 (if B) | Recursion scope: (i) full recursive harness (child runs full event loop); (ii) shared-ledger-writer-only (child uses parent's ledger writer); (iii) ADR-class scope (file ADR before fork) |
| Q4 (if D) | Summary shape: (i) brief.summary_hash; (ii) new `SubAgentSummary` Pydantic carrier with explicit fields; (iii) implementer-discretion per §16.5.4 disambiguator-note pattern |
| Q5 (any) | Cross-axis cascade scope: (α) intra-CP-spec only; (β) CP + IS spec cascade; (γ) full ADR-class (CP + IS + AS + OD + CXA) |

---

## §5 Cross-axis cascade analysis

| Axis | Touch under each Reading |
|---|---|
| IS | Reading A: NONE. Reading B: MAJOR — shared-ledger writer threading + recursion-aware idempotency. Reading C: NONE. Reading D: spec footnote on response_hash source. |
| AS | Reading A: NONE. Reading B: MAJOR — ToolContract scoping across recursion levels. Reading C: NONE. Reading D: NONE. |
| CP | Reading A: §15.1 semantic widening (single section). Reading B: §C-CP-NN NEW recursive-harness chapter + TopologyPattern interaction. Reading C: NONE. Reading D: §15.1 reframe + possible §15.2/§15.3 sibling reframes. |
| OD | Reading A: cost-attribution across siblings (already-handled via §16.5 emission). Reading B: cost-attribution across recursion levels. Reading C: NONE. Reading D: depends on summary shape. |
| CXA | Reading A: no new edge. Reading B: many new edges (recursion-aware). Reading C: no new edge. Reading D: possible §0.4 forward-tracking marker. |
| Runtime spec | Reading A: callsite addition at `sub_agent_dispatch.py` (no spec change). Reading B: NEW §14.X recursive-harness lifecycle contract. Reading C: NONE. Reading D: §14.X summary-projection contract. |

---

## §6 Recommendation

**Pre-substantive recommendation:** Reading C (bounded-defer) is the structurally-coherent disposition at MVP scope. U-CP-34 v2.37 STRIKE established the structural-unfireability finding decisively; the LANDED composer + LANDED wiring sit as substrate for a future recursive-harness arc OR a future §15.1 reframe arc. Authoring a firing-site at MVP under Reading A would defeat the v2.37 STRIKE rationale; Reading B is an ADR-class arc that exceeds this session's scope; Reading D is a workaround that risks shoehorning a more fundamental architectural decision.

Reading B is the architecturally-canonical long-term path per `Phase_7_Meta_Architecture_v1.md` §6 self-hosting milestone gradient (recursive-harness composition is the natural maturation of the sub_agent_dispatch surface), but it is a multi-arc decomposition that requires ADR-class deliberation. Filing Reading B as the recommended-long-term + Reading C as the recommended-this-arc preserves both forward direction and present-arc coherence.

If operator prefers immediate closure: Reading A is the lowest-surface path but requires explicit acceptance of hash-role conflation + §15.1 semantic widening (operator should ratify Q2 explicitly).

---

## §7 Status posture

| Element | Status |
|---|---|
| Composer LANDED | ✅ (U-CP-34) |
| Wiring LANDED | ✅ (U-RT-110) |
| Production callsite | ❌ ABSENT |
| Recursive-harness substrate | ❌ NOT BUILT at MVP (single-LLM-inference wrap only) |
| H_T-RT-35 RETIRE-READY transit | GATED on this arc + 4 sibling upstream arcs |
| Recommended Q1 | (C) bounded-defer for THIS arc + (B) for the long-term self-hosting milestone trajectory |
| Sibling arc | `[[class_1_tension_hitl_rewrite_tool_call_pre_dispatch_hook_absence]]` co-published this arc (DISTINCT structural shape; HITL firing-site question is pre-dispatch interception hook, NOT recursion-boundary) |

---

*End of fork doc.*
