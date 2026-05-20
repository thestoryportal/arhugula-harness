# Class 2 Fork Record — Tool-invocation runtime composer scope decision

**Filed:** 2026-05-20 (post-U-RT-58 + batch-3 retirements arc; preparing for next arc).
**Class:** 2 (in-execution operator decision; no defect — the spec is silent on this surface by design, and the operator owns silence-vs-extension).
**Status:** OPEN — awaiting operator ratification of one of three sub-paths.
**Surfaced by:** `phase-7-substitution-retirement` skill activation against AS/CXA STILL-BOUNDED retirements + advisor cross-check against v2 ledger §9.2.2.

---

## 1. The decision the v2 ledger names

`.harness/phase-7d-retirement-ledger-v2.md` §9.2.2 line 195 explicitly:

> **Tool-invocation runtime composer scope decision.** Operator decision: does the tool-invocation runtime (AS-2/4/5/8 unblock) route to a Phase-7-deferred runtime unit, a Phase-3 design effort, or a back-flow Class 1 spec extension? Out of scope for this verification ledger.

The decision is documented, operator-owned, and not architectural-defect-driven (no halt; the spec is silent by design at this surface). It IS the next-arc gating decision for ~5 substitutions (AS-2 + AS-4 + AS-5 + AS-8 remaining + likely CXA-1).

---

## 2. What's actually missing at runtime

Current state (verified 2026-05-20 at `33252c5`):

| Surface | Current state | Gap to retirement |
|---|---|---|
| `harness_runtime.lifecycle.tool_registry.ToolRegistry` | Typed surface met (register / get / names / `__len__` / `__contains__`); duplicate-name rejection wired | `materialize_tool_registry(skills)` returns **empty** registry; no tool population from MCP server `list_tools` or skill-declared contracts |
| `harness_runtime.lifecycle.mcp_host.MCPHost` | Frozen placeholder dataclass with `started=False` | **No real FastMCP server startup**; no subprocess management; no protocol handshake; no client connection pool |
| `harness_runtime.lifecycle.mcp_host.MCPClient` | Wraps `MCPClientConfig` with `ready=True` after transport-floor check | Doesn't actually connect to anything; `ready` is a static flag |
| `harness_cp.workflow_driver_types.StepKind.TOOL_STEP` | Enum value exists; CP §5.2 5-value taxonomy verbatim | Driver at `workflow_driver.py:379` invokes `step_dispatcher.dispatch(binding, step)` without per-step-kind branching; current bound dispatcher (the U-RT-58 wrapper around `RuntimeLLMDispatcher`) is LLM-only |
| `harness_as.sandbox_*` carriers (`sandbox_span_schema.py`, `sandbox_attribute_schema.py`, `sandbox_event_sampling.py`) | All landed | **Zero runtime references**; no `start_span` invocation at any sandbox-event site; `sandbox.*` 7-attribute namespace never emitted |
| `harness_as.anthropic_*` + `mcp_*` library carriers | All landed | Same pattern: library exists; zero production callsite invocations |

Net: the building blocks exist at axis-package level. The runtime composition site (the analog of `RuntimeLLMDispatcher` for tools) does not exist. AS-2 PARTIAL = "registry surface but no population"; AS-4 / AS-5 STILL-BOUNDED = "no production span emission"; AS-8 remaining = "no production namespace emission".

---

## 3. The three sub-paths the ledger names

### Path X — Phase-7-deferred runtime unit (U-RT-58 shape)

**Shape.** Mirror U-RT-58: one new spec contract (e.g., C-RT-17 — Tool-invocation composer) at `Spec_Harness_Runtime_v1.md` v1.5 → v1.6; one new plan unit (e.g., U-RT-59) at L9-bis (alongside U-RT-58) or L10; one new module `harness-runtime/.../lifecycle/tool_invocation.py`; bootstrap stage 5 binds it; driver branches on `step.step_kind` to dispatch via the tool composer for `TOOL_STEP`.

**Scope of work.**

- Real FastMCP integration via `mcp` Python SDK (STDIO transport for MVP; HTTP/SSE deferred).
- Subprocess MCP server lifecycle management (start + health check + shutdown).
- `list_tools` protocol call at host-startup to populate `ToolRegistry`.
- `call_tool` protocol call at dispatch time.
- `sandbox.*` 7-attribute namespace emission at sandbox-event sites (per C-AS-12 §12 + C-AS-15 §15).
- `mcp.*` namespace emission at MCP-call sites (per C-AS-14).
- Per-MCP-server trust framework function composition.
- Driver-side step-kind branching (or step_dispatcher-table refactor).

**Effort estimate.** 2-4× U-RT-58 (genuinely larger because new infrastructure, not orchestration over landed primitives). Realistic at CC pace: 2-4 hours of focused work. Human pace: 2-3 days.

**Retirements unlocked.** AS-2 PARTIAL→RETIRED + AS-4 STILL-BOUNDED→RETIRED + AS-5 STILL-BOUNDED→RETIRED + AS-8 PARTIAL→RETIRED + likely CXA-1 if AS→IS edges materialize at the tool-dispatch site. ~5 retirements.

**Risk.** Mid-arc scope creep if FastMCP integration surfaces undocumented edges (likely — the SDK is large + the protocol has edges; the existing `mcp_host.py` Class 1 risk-flag absorption note already acknowledges "Real FastMCP server startup is heavyweight").

### Path Y — Phase-3 design effort

**Shape.** Author a new design-substrate artifact (e.g., `Spec_Tool_Invocation_v1.md`) at design-substrate workspace; route through `harness-adversarial-reviewer` skill pass; ratify; THEN implement under a multi-unit per-axis plan. Adds adversarial review + spec-writer discipline + per-unit decomposition.

**Effort estimate.** Heavier than Path X by ~2× because the design-phase loop runs before implementation. Realistic at CC pace: 1-2 sessions of design + ratification, then 1-2 sessions of implementation. Human pace: 1-2 weeks.

**Retirements unlocked.** Same ~5 as Path X, plus more durable specification (downstream consumers reference the spec, not the implementation).

**When to pick.** If the tool-invocation surface is load-bearing for substantial downstream work (e.g., Track B operator-facing surface, multi-skill workflows, agent-team composition). The spec becomes the canonical reference.

### Path Z — Back-flow Class 1 spec extension (narrowest)

**Shape.** Amend AS spec §X to declare the missing tool-invocation runtime contract (filling the silent gap with a thin spec addition). Less than full Path Y design effort. More than direct implementation.

**Effort estimate.** ~1× U-RT-58 for the spec amendment + plan revision; implementation comparable to Path X but cleaner because spec exists first.

**When to pick.** If the existing AS spec almost-but-not-quite specifies the runtime surface and the gap is bounded (e.g., "AS specifies tool-contract schema + sandbox tier; misses the runtime invocation site that wires them"). Narrower than Phase-3 effort; broader than just-implement.

**Risk.** Surfaces the silent gap as a tension record + spec revision; downstream costs from cascading spec consumers.

### Path W (alternative) — Defer; carry as bounded-residual

**Shape.** Don't open the arc this session (or this phase). Mark AS-2/4/5/8 + CXA-1 as bounded-residuals per v2 ledger §9.2.5 ("7d closure with documented rationale per X-AL-2"); document the operator-known scope at this Class 2 record; move to a different arc (sub-agent dispatch composer, HITL composer, validator composer, ResumptionKind expansion, or Track B scoping).

**Effort estimate.** Zero — explicit deferral.

**Retirements unlocked.** None directly; opens room for a different next arc.

**When to pick.** If the operator's nearer-term priorities are elsewhere (e.g., HITL or sub-agent dispatch unblock more dependencies; Track B is the next concrete goal). The Path X/Y/Z decision can wait.

---

## 4. Routing options for this fork

The skill's `phase-7-back-flow-routing` activation surface names Class 2 as "in-execution operator decision". Per `Project_Workflow_v1_8.md` §2.7.6: surface to operator at this workspace; record decision at sub-phase log; no design-phase back-flow.

Operator decision needed:

1. **Pick a path** (X / Y / Z / W).
2. **If X or Y or Z**: also pick MVP scope of the composer (real STDIO subprocess vs mocked MCP client vs in-process FastMCP). Each gives different retirement footprints.
3. **If W**: pick the alternative next arc (sub-agent dispatch / HITL / validator / ResumptionKind / Track B prep / other).

---

## 5. Recommendation (informational)

Path **W** for this session, with a follow-on session opening Path **X** at operator timing. Rationale:

- This session has already landed substantial work (workspace cleanup, U-RT-58 retry/breaker/fallback composer + Class 1 spec drift resolution + Class 3 record, batch-3 retirements). Cadence-wise, opening a 2-4× U-RT-58 arc within the same session risks the architectural-shape drift the prior two halts caught.
- The sub-agent dispatch composer (CP-10 + CP-13 + CP-14) is comparable-shape work to U-RT-58 (orchestration over landed primitives — `TopologyDispatcher`, `HandoffContext`, `subagent.*` namespace carriers all exist); it would be a cleaner next-session arc.
- The tool-invocation composer warrants its own session for the Path X/Y/Z decision + scope-shape investigation. Surfacing now and deferring honors the v2 ledger §9.2.2 operator-decision discipline.

This is informational only — operator picks.

---

## 6. Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/class_2_fork_tool_invocation_composer_scope.md` |
| Surfaced at | Post-U-RT-58 arc; pre-next-major-arc decision point, 2026-05-20 |
| Surfacing skill | `phase-7-substitution-retirement` activation + advisor cross-check |
| Authority cited | `.harness/phase-7d-retirement-ledger-v2.md` §9.2.2 line 195 (operator-decision pinning); Workflow v1.8 §2.7.6 Class 2 routing |
| Cross-references | `harness-runtime/.../lifecycle/tool_registry.py` + `mcp_host.py` (current state); `harness_as.sandbox_*` + `anthropic_*` + `mcp_*` carriers (landed primitives); `harness_cp.workflow_driver_types.StepKind.TOOL_STEP` (typed step-kind); `Spec_Action_Surface_v1.md` v1.3 §12 + §14 + §15 (existing AS contracts) |
| Resolution target | Operator decision per §4; record at this file's "Operator decision" addendum; if X/Y/Z then route into a new arc; if W then move to next arc |
| Blocking | The tool-invocation composer arc (whichever path); the AS-2/4/5/8 + CXA-1 retirements (whichever batch they land in) |
