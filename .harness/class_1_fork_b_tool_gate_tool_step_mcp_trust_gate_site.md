# Class 1 Fork — B-TOOL-GATE (tool-step HITL gate site = the resolved-owning-host MCP-trust feed)

**Filed:** 2026-06-18 · R-FS-1 standalone `B-*` arc **B-TOOL-GATE** (surfaced by U-RT-131 / arc B2-plan; spine ledger `.harness/beyond-mvp-capability-boundary-ledger.md` line 56, registered `Rec: BUILD (runtime gate-site arc)`). Bundled-absorption posture: **`harness-runtime/src` + by-execution tests only — NO design-substrate edit, NO spec bump, NO clearance marker, NO operator gate.**

**Status:** ✅ RESOLVED + BUILT. **Impl-against-cleared-spec** — NOT an X-AL-3 surface extension (contrast `B-INTERSTEP`): the composer input is already spec-named (CP spec **v1.35 §19.1.2 Producer ¶** + runtime **§14.8.2 step-4c** `mcp_server_trust_tier`), and `MCPTrustTier` / `GateLevelInput.mcp_trust_tier` / `MCP_TRUST_GATE_LEVEL_FLOOR` all already exist. This arc mints **no** new contract, field, enum, fail-class, or invariant; it adds the tool-step gate SITE the §19.1.2 Producer ¶ describes (runtime plan v2.48 §6 O-RT-7 item 2 — Rec: BUILD; "confirm no contract widening at build, else design-fork-first per X-AL-3" — confirmed: no widening). Additive + no committed-invariant sacrifice → no operator gate (advisor-confirmed; no nameable cross-domain tension → advisor, not council).

This doc is filed as back-flow + the build-record because the arc surfaced a **decorrelated [P1] finding** (Codex) that materially scopes the arc's impact — see §3.

---

## §1 The build — Option A: a third `RuntimeHITLGateComposer` at the tool-step registry path

Before: the runtime HITL gate composer was constructed for **only two host-less placements** — inference (`PRE_ACTION`) + sub-agent (`SUB_AGENT_BOUNDARY`) — neither with an owning MCP host; `TOOL_STEP`s dispatched through `runtime_tool_dispatcher.py`, which composes **no** HITL gate. So the §19.1.2 Producer ¶ ("resolved owning MCP host's trust") had no gate site to populate, and U-RT-131 correctly installed the L3 *no-floor* default at the host-less sites.

The build (the spec's named producer — Option A over composing the gate inside the tool dispatcher, because only the composer carries the full HITL flow that makes the **ASK** floor for L1/L2 meaningful):

1. **`harness_runtime/lifecycle/step_mcp_trust_tier.py` (NEW)** — `make_step_mcp_trust_tier_resolver(ctx)` + `resolve_step_mcp_trust_tier(step, ctx)`: a `(step) -> MCPTrustTier | None` closure mirroring the sibling `make_step_blast_radius_resolver`. Resolves the `TOOL_STEP`'s `tool_id` → owning host (host-scan over `ctx.mcp_client_hosts[*].tool_registry`) → `MCPClientHost.trust_tier`. The `RT-FAIL-MCP-TOOL-NAME-COLLISION` bootstrap guarantee (a tool in ≥2 hosts aborts startup) makes the host the gate scores provably the host the dispatcher routes to (no gate-L3-but-dispatch-L0 hole). Fail-soft (`None` on unresolvable) — deliberately distinct from the blast resolver's fail-safe raise (the blast resolver runs FIRST at step-4c and raises on the same unresolvable `tool_id`, and the `mcp_trust` axis is a `max()` floor so a missing floor can only under-gate).
2. **`hitl_gate_composer.py`** — NEW optional field `mcp_trust_tier_resolver: Callable[[WorkflowStep], MCPTrustTier | None] | None = None` (the `blast_radius_resolver` sibling); `_compute_gate_decision(... mcp_trust_tier=None)` threads it into `GateLevelInput.mcp_trust_tier` (None → the L3 `_NO_OWNING_MCP_HOST_TRUST_FLOOR` default → host-less composers byte-identical to pre-arc). Step-4c invokes the resolver.
3. **`stage_5_loop_init.py`** — a THIRD composer `hitl_tool` wraps the tool dispatcher at the **registry path**: `tool_step_dispatcher = facade(hitl_tool(ctx.tool_dispatcher))`, `applicable_placements={PRE_ACTION}`, same dep set as the inference/sub-agent composers + the resolver. **`ctx.tool_dispatcher` is NOT mutated** (advisor catch) — the R-CXA-2 producer loop + the provider-turn `hitl_tool_loop` still read the un-gated dispatcher; gating it in place would HITL-gate provider-initiated tool calls + double-gate vs `hitl_tool_loop`. HITL is OUTER of the C-RT-16 retry (gate fires once before dispatch; retries don't re-prompt — a deliberate asymmetry vs the LLM path's HITL-inner-of-retry).

---

## §2 Decorrelated review

- **advisor (pre-build):** confirmed Option A + placement-driven + the impl-to-cleared-spec determination; flagged two correctness blockers — (i) **DENY-reachability** (B-TOOL-GATE makes `gate_level == DENY` reachable in production for the first time; verify the consequence is sane) → verified: `compute_effective_palette(DENY)` narrows the palette to `{REJECT, RESPOND}` and the composer STILL invokes the ask surface (structural-rejection-with-HITL), tested end-to-end (REJECT → `HITLGateRejectedError`); (ii) **wrap the registry path, not `ctx.tool_dispatcher`** → done.
- **Codex (out-of-family, on the diff):** caught a **[P1]** finding advisor + author missed — see §3.

---

## §3 The Codex [P1] finding — the placement-producer gap (impact-scoping, NOT a code defect)

**Finding:** the wrap-time gate is placement-driven — the composer fires only when `getattr(step, "hitl_placements", ())` is non-empty. But `hitl_placements` is declared at the **WORKFLOW** level (`WorkflowManifestEntry.hitl_placements`, "Declared per workflow per C-CP-17 §17.3"; loader `_WorkflowSection.hitl_placements`), and the per-step `WorkflowStep` the driver dispatches is frozen + `extra="forbid"` (only `step_id`/`step_kind`/`step_payload`). **No src binds the workflow-level placements onto the per-step steps**, so `step.hitl_placements` is **always `()`** through the real `WorkflowManifestLoader`→driver path → **no wrap-time HITL gate fires in production for ANY step kind.**

**Grounded + confirmed:** even the existing inference/sub-agent gate e2e tests (`test_run_workflow_elicitation_e2e.py:234-250`, citing "WorkflowStep is frozen + extra=forbid; composer reads getattr(step, 'hitl_placements', ())") attach placements via a `_StepWithPlacements` **test proxy** — `[[test-bypass-as-runtime-truth-pattern]]` at workspace scale. So this is a **PRE-EXISTING gap shared by ALL wrap-time gate sites** (inference, sub-agent, AND this tool gate), NOT introduced by B-TOOL-GATE. It is the unbuilt half of the **B3** spine-ledger residual ("placement composition is a placeholder … the placement matrix + HandoffContext binding … BUILD runtime + CP workflow-grammar arc").

**Disposition (advisor-confirmed) — the three-claim decomposition (never blurred):**
1. **Wiring correct** — proven through real `run_bootstrap` (`test_bootstrap.py`): TOOL_STEP registry = `facade → hitl_tool[resolver bound] → ctx.tool_dispatcher`.
2. **Axis composes when the gate fires** — proven by-execution (L0→DENY→{REJECT,RESPOND}→REJECT raises; L3→AUTO→delegate; real-resolver-over-real-hosts integration). The tests use the `_StepWithPlacements` proxy (same as the existing gate tests) — they prove (2), NOT (3).
3. **Production gate-firing awaits the per-step placement producer** — registered as **`B-HITL-PLACEMENT-PER-STEP-PRODUCER`** (spine ledger), the cross-cutting B3-residual arc that lights up ALL wrap-time gate sites. Spec'd-ness TBD at arc-open (the placement DECLARATION is spec'd at C-CP-17 §17.3 + "workflow-binding-time per U-CP-13/U-CP-38"; the workflow→per-step BINDING semantics may be under-specified → if so, design-fork-first per X-AL-3).

B-TOOL-GATE legitimately lands as the **tool-gate-site + MCP-trust feed** (the §19.1.2-scoped half, at parity with how the inference/sub-agent gates landed — wired + reachable only via the proxy, awaiting the shared producer). Without it, even after the producer lands, tool steps would have no gate site. The "non-vacuous in production" phrasing in the pre-build spine-ledger body + the first-draft code docstrings was an **overclaim**, corrected to "non-vacuous at the tool gate, at parity" across the code + the spine-ledger BUILT note.

**PRE_ACTION forward-coupling (for the producer arc):** the tool gate keys on `{PRE_ACTION}` like the inference gate, so once the producer lands a workflow-level PRE_ACTION placement will gate BOTH inference and tool steps — the producer arc must decide the application semantics.

---

## §4 Verification

- pyright 0/0/0 (touched files, strict); ruff clean.
- `test_step_mcp_trust_tier.py` (8) — resolver: L0/L3 resolution (raise- + dict-registry shapes), unresolvable/missing/non-str `tool_id` → None, non-TOOL_STEP → None, no-hosts → None, closure.
- `test_lifecycle_hitl_gate_composer.py` (+6 B-TOOL-GATE) — `_compute_gate_decision` L0→DENY (winner MCP_TRUST) / L3→AUTO-no-floor; composer L0→DENY→{REJECT,RESPOND}→reject-raises; L3→AUTO→delegate; real-resolver-over-real-hosts integration (L0 denies, L3 delegates); no-placement passthrough byte-identical.
- `test_bootstrap.py::test_bootstrap_stage_5_binds_inference_and_sub_agent_dispatchers` — updated to assert (through real `run_bootstrap`) the TOOL_STEP registry = `facade → RuntimeHITLGateComposer(resolver bound, {PRE_ACTION}) → ctx.tool_dispatcher` (the by-execution wiring proof; the old `tool_step.inner is ctx.tool_dispatcher` assertion would have broken — updating it IS the wiring proof).
- Full `harness-runtime` non-integration suite: **1922 passed / 10 skipped** (no passthrough regression — ~1900 tool tests traverse the new composer passthrough). CXA-P1 34 passed.

---

## §5 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/class_1_fork_b_tool_gate_tool_step_mcp_trust_gate_site.md` |
| Arc | R-FS-1 standalone `B-*` — `B-TOOL-GATE` |
| Posture | Impl-against-cleared-spec (CP v1.35 §19.1.2 + runtime §14.8.2 step-4c); `harness-runtime/src` + tests only; NO design-substrate edit; NO operator gate |
| Decorrelated review | advisor (pre-build approach + DENY-reachability + registry-path; pre-done three-claim discipline) + Codex (the [P1] placement-producer gap) |
| Registered follow-on | `B-HITL-PLACEMENT-PER-STEP-PRODUCER` (spine ledger) — the cross-cutting per-step placement binding that makes ALL wrap-time gates fire in production |
| Owed at post-merge | the §12.2.1 roadmap fixed-point refresh (terminating refresh PR) |
