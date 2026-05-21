# Phase 7d Retirement Events — Batch 9

| Field | Value |
|---|---|
| Batch number | 9 |
| Filed at | 2026-05-21 (post-U-RT-62 FastMCP server impl arc landing — C-RT-18 v1.12 workflow-initiation topology pin RATIFIED → APPLIED) |
| Filed by | U-RT-62 follow-on impl arc per plan v2.10 §2 L9-quinquies AC #J |
| Predecessor batch | `phase-7d-retirement-events-batch-8.md` (2026-05-21, U-RT-60 wrap-asymmetry impl arc — H_T-CP-20 STILL-BOUNDED → RETIRE-READY; cumulative 21/49 unchanged; introduced RETIRE-READY ledger category) |

---

## §0 Batch context

**Status type: substitution-retirement transition (1 RETIRE-READY → RETIRED) — first new RETIRED transition since batch 4 (2026-05-20).**

This batch documents the U-RT-62 FastMCP server hosting impl arc APPLIED landing (commits `0d59943` HarnessMCPServer primitive + AC #1, `9e07f4a` materialize_mcp_server_stage + run_workflow tool registration AC #2 + #3, `70f3f53` ServerCtxElicitCallback AC #4, `bfdd30e` api.run() thin-wrapper reframe AC #5 + #7 + #8, `8b9c14c` AC #6 e2e topology test, `2acdce9` AC #9 placeholder retention reading + Class 3 carry-forward closure, and this commit's AC #J retirement event filing). The arc materializes the spec v1.12 §14.8.3 v1.12 workflow-initiation topology pin (Reading α CC-initiates) end-to-end: H_T runtime hosts a FastMCP server; the `run_workflow` MCP tool is registered + discoverable; the production `ServerCtxElicitCallback` invokes `await ctx.elicit(...)` outbound on the active server session; the e2e integration test exercises the full path CC → run_workflow → HITL gate fire → ctx.elicit → response → continuation → RunResult through the in-process MCP envelope.

The retirement event recorded here is **H_T-CP-20 RETIRE-READY → RETIRED**. This is the first new RETIRED transition since batch 4 (CP-10 + CP-13, 2026-05-20). The transition is "criterion A met + criterion B FULLY met" per X-AL-2 reading — both the structural reading ("H_E AskUserQuestion surface reached only via MCP envelope") AND the end-to-end operational reading ("substitution site terminally delivers + receives response via the MCP envelope") are satisfied by the AC #6 e2e test (load-bearing for criterion B verification per spec v1.12 §14.8.3 v1.12 RETIRE-READY → RETIRED gate paragraph).

**Q5 disjointness pin (load-bearing).** Per the operator-ratified Q5 reading at `.harness/class_1_tension_c_rt_18_mcp_workflow_initiation_topology_underspec.md`: H_T-CP-18 (MCP integration + per-server trust + `mcp.*` consumption per Meta-Architecture §5 line 124) does NOT advance jointly with H_T-CP-20 at this retirement event. CP-18's substitution site is the H_T-as-MCP-client surface (the runtime consumes other MCP servers — filesystem, GitHub, sandbox MCP servers — gated by per-server-trust framework + `mcp.*` namespace emission at the client-side per U-RT-15 lifecycle). U-RT-62's H_T-as-MCP-server workflow-execution hosting is orthogonal; CP-18 retirement remains a separate arc gated on the per-server-trust framework landing + `mcp.*` namespace emission at the H_T-as-client surface. **This amends the batch 8 §3 carry-forward language** ("Coupled with H_T-CP-18 retirement … both substitutions advance to RETIRED at that arc landing") per forward-only ledger discipline at workspace `CLAUDE.md` §4.3 — new batch record, NOT retroactive edit to batch 8.

**Conclusion (preview):** 1 new RETIRED transition (H_T-CP-20); 1 RETIRE-READY → 0 RETIRE-READY; cumulative 21/49 → **22/49 RETIRED** (44.9%). CP-axis: 9/22 + 1/22 RETIRE-READY → **10/22 + 0/22 RETIRE-READY** (45.5%). H_T-CP-18 disjointness pinned per Q5; remains STILL-BOUNDED.

---

## §1 H_T-CP-20 RETIRE-READY → RETIRED

| Field | Value |
|---|---|
| Substitution ID | H_T-CP-20 |
| Primitive | HITL primitive + 4-response palette + `hitl.*` / `audit.*` namespace emission |
| Prior status | RETIRE-READY per batch 8 §1 (2026-05-21) |
| Transition this batch | RETIRE-READY → **RETIRED** |
| Triggering arc | U-RT-62 FastMCP server hosting impl arc APPLIED landing (HarnessMCPServer primitive + materialize_mcp_server_stage + run_workflow tool + ServerCtxElicitCallback + api.run thin-wrapper reframe + AC #6 e2e topology test) |

### §1.1 Criterion A (cited unit IDs landed) — MET

Per `Spec_Harness_Runtime_v1.md` v1.12 §14.8.3 v1.12 RETIRE-READY → RETIRED gate paragraph: "(a) `HarnessMCPServer` primitive materialized + `run_workflow` MCP tool registered + Claude Code MCP-client connection verified at runtime (criterion A condition — cited unit IDs landed: existing 8 units of v1.10 list + U-RT-62 added at runtime plan v2.10)":

| Unit | Landing commit | Surface |
|---|---|---|
| U-CP-37 / U-CP-38 / U-CP-39 / U-CP-40 / U-CP-41 / U-CP-46 / U-RT-25 / U-RT-60 | per batch 8 §1.1 (HITL palette + placement + matrix + composer + wrap chain landed) | (See batch 8 for full table) |
| **U-RT-62** | **landed this arc** (FastMCP server hosting + run_workflow tool + HarnessMCPServer + ServerCtxElicitCallback + api.run reframe) | `harness-runtime/.../lifecycle/mcp_server.py` (NEW) + `.../lifecycle/mcp_backed_ask_user_question_surface.py` (ServerCtxElicitCallback class added) + `.../bootstrap/stage_2_as.py` (mcp_server materialization step) + `.../bootstrap/stage_5_loop_init.py` (default-binding rebind) + `.../api.py` (thin-wrapper reframe via in-process ClientSession) |

**Criterion A status: MET.** All 9 cited units landed end-to-end at U-RT-62 APPLIED.

### §1.2 Criterion B (substituted H_E surface no longer invoked) — FULLY MET

Per X-AL-2: "Retirement = (cited unit IDs landed) ∧ (substituted H_E surface no longer invoked at substitution site). **Both conditions required.**"

**Substitution site analysis at U-RT-62 APPLIED.** H_T-CP-20's substituted H_E surface was Claude Code's `AskUserQuestion` tool invoked directly by convention (`CLAUDE.md`-prose-routed at operator discretion). At v1.12 with U-RT-62 landed:

- The composer body invokes `await ctx.ask_user_question_surface.ask(prompt, options, timeout)` (no direct `AskUserQuestion` invocation).
- `ctx.ask_user_question_surface` is bound to `MCPBackedAskUserQuestionSurface` carrying `ServerCtxElicitCallback` (production default per stage 5 wiring at AC #4) instead of the prior `_PlaceholderMCPCallback`.
- `ServerCtxElicitCallback.__call__` reads the in-flight `run_workflow` tool ctx from `HarnessMCPServer._state['_current_tool_ctx']` + invokes `await ctx.elicit(message, schema)` outbound on the active server session per the v1.12 topology pin (Reading α).
- The MCP client (Claude Code in production; test fixture in AC #6 e2e) receives the elicitation request via the MCP envelope + delivers the response back through the MCP response channel.

**Both readings of criterion B MET:**

1. **Strict structural reading** ("is the H_E surface — Claude Code `AskUserQuestion` tool, direct invocation — still invoked at the substitution site?"): **NO**. The composer body invokes the typed `AskUserQuestionSurface` Protocol through the MCP-backed surface → `ServerCtxElicitCallback` → `ctx.elicit(...)`. The H_E delivery primitive is reached only through the MCP envelope per X-AL-1 (workspace `CLAUDE.md` invariant I-4 — process isolation at the MCP server process boundary). **MET.**

2. **End-to-end operational reading** ("does the substitution site terminally deliver to an operator surrogate and receive a response?"): **YES**. The AC #6 e2e integration test (`test_e2e_run_workflow_elicit_round_trip` at `harness-runtime/tests/integration/test_run_workflow_elicitation_e2e.py`) exercises the full path Claude Code surrogate (in-process ClientSession) → `run_workflow` MCP tool → workflow body → HITL gate composer fire on PRE_ACTION placement → `ctx.elicit` invoked exactly once → canned elicitation_callback returns `ElicitResult(action="accept", content={"response": "approve", ...})` → composer continues to inner dispatcher → workflow completes → `RunResult(status='success')` returned through MCP response channel. **MET.**

### §1.3 Production callsite invocation evidence

Production wrap chain unchanged from batch 8 §1.3 (per fork §7.2 Q1 code block at U-RT-60 APPLIED); U-RT-62 adds:

```
Bootstrap stage 2 AS (new step 3-bis):
  ctx.mcp_server = materialize_mcp_server_stage(drain_timeout_seconds=...)
    → HarnessMCPServer(
        server=FastMCP(name="harness-runtime"),
        started=True,
        workflow_registry={},
        _state={},
      )
    + run_workflow MCP tool registered at fastmcp instance

Bootstrap stage 5 LOOP_INIT (rebinding):
  ctx.ask_user_question_surface = materialize_mcp_backed_ask_user_question_surface_stage(
    ctx.mcp_host,
    harness_mcp_server=ctx.mcp_server,  # NEW — triggers ServerCtxElicitCallback default
  )
    → MCPBackedAskUserQuestionSurface(
        mcp_host=...,
        mcp_callback=ServerCtxElicitCallback(mcp_server=ctx.mcp_server),
      )

api.run() body (reframed):
  await run_bootstrap(...)
  ctx.mcp_server._state["_harness_ctx"] = ctx
  ctx.mcp_server.workflow_registry[workflow.workflow_id] = workflow
  async with create_connected_server_and_client_session(
      ctx.mcp_server.server,
      elicitation_callback=_refuse_elicitation_in_api_run,
      raise_exceptions=True,
  ) as session:
      tool_result = await session.call_tool("run_workflow", {"workflow_id": ...})
  cp_result = parse(tool_result.content[0].text)
  await _shutdown(ctx)
  return _build_run_result(cp_result, ...)
```

Verification evidence:

- `harness-runtime/tests/test_lifecycle_mcp_server.py` (10 cases — AC #1 + AC #2 + AC #3 + AC #4 surface verification: HarnessMCPServer frozen + required fields + dict-mutability + state-holder mutability + distinct-from-MCPHost; materialize returns started=True; run_workflow tool registered; unknown workflow_id rejected; unbound harness_ctx rejected; HarnessContext field admits both MCP roles).
- `harness-runtime/tests/test_lifecycle_server_ctx_elicit_callback.py` (10 cases — AC #4 verification: accept with valid data; EDIT carries proposal; decline → synthesized REJECT; cancel → AskUserQuestionTimeoutError; accept-missing-data → MCPSurfaceCallbackNotBoundError; accept-off-palette → MCPSurfaceCallbackNotBoundError; no-ctx-bound → MCPSurfaceCallbackNotBoundError; materialize precedence — 3 cases).
- `harness-runtime/tests/test_bootstrap.py::test_bootstrap_populates_every_required_harness_context_field` extended (asserts `ctx.mcp_server is not None` + `ctx.mcp_server.started is True` post-bootstrap per AC #2).
- **`harness-runtime/tests/integration/test_run_workflow_elicitation_e2e.py` (load-bearing for criterion B)** — 2 cases: `test_e2e_run_workflow_elicit_round_trip` (full topology end-to-end: bootstrap → in-process ClientSession with canned accept-callback → call run_workflow tool → HITL gate fires → ctx.elicit invoked exactly once with composed prompt → APPROVE response delivered → composer continues → workflow completes with status='success'; criterion B FULLY MET); `test_e2e_run_workflow_decline_maps_to_reject` (decline path drives composer branch selection vs silent absorption — verifies the elicitation response IS load-bearing for composer behavior).
- 768/768 harness-runtime tests pass (+22 net from baseline 746 across the 7 implementation commits).

### §1.4 Q5 disjointness pin — H_T-CP-18 does NOT advance jointly

Per `Spec_Harness_Runtime_v1.md` v1.12 §14.8.3 v1.12 H_T-CP-18 retirement disjointness pin paragraph + the operator-ratified Q5 reading at `.harness/class_1_tension_c_rt_18_mcp_workflow_initiation_topology_underspec.md`:

H_T-CP-18 (MCP integration + per-server trust + `mcp.*` consumption per `Phase_7_Meta_Architecture_v1.md` §5 line 124 row body "consumption" = **client-side** surface) does NOT advance jointly with H_T-CP-20 at this retirement event. CP-18's substitution site is the H_T-as-MCP-client surface (the runtime consumes other MCP servers — e.g., filesystem MCP server, GitHub MCP server, sandbox MCP server — gated by per-server-trust framework + `mcp.*` namespace emission at the client-side per U-RT-15 lifecycle). U-RT-62's H_T-as-MCP-server workflow-execution hosting is orthogonal:

| Substitution | Substitution site | Status at this batch |
|---|---|---|
| H_T-CP-20 | HITL primitive + 4-response palette + `hitl.*` / `audit.*` emission via `ctx.ask_user_question_surface.ask(...)` → `ServerCtxElicitCallback` → `ctx.elicit(...)` outbound on H_T-as-MCP-server session | **RETIRED** (this batch) |
| H_T-CP-18 | MCP integration + per-server trust + `mcp.*` namespace emission at H_T-as-MCP-client side (consumes other MCP servers per U-RT-15 lifecycle: filesystem, GitHub, sandbox, etc.) | **STILL-BOUNDED** (orthogonal arc) |

**Amendment to batch 8 §3 carry-forward language.** Batch 8 §3 stated: "Coupled with H_T-CP-18 retirement (MCP integration + per-server trust); both substitutions advance to RETIRED at that arc landing." Under the Q5 disjointness ratification, this coupling is **INACCURATE**: the two substitution sites are orthogonal (server-side vs client-side surfaces of the MCP integration). The corrected reading at this batch: H_T-CP-20 retires at U-RT-62 (H_T-as-MCP-server arc); H_T-CP-18 retires at a separate future arc gated on per-server-trust framework + `mcp.*` namespace emission at the H_T-as-MCP-client surface. Per forward-only ledger discipline at workspace `CLAUDE.md` §4.3, this batch records the amended reading; batch 8 §3 stands verbatim (no retroactive edit).

---

## §2 H_T-CP-18 disjointness preservation (NO transition)

| Field | Value |
|---|---|
| Substitution ID | H_T-CP-18 |
| Primitive | MCP integration + per-server trust + `mcp.*` consumption (H_T-as-MCP-client surface) |
| Prior status | STILL-BOUNDED per ledger §5 |
| Batch 9 surface | U-RT-62 H_T-as-MCP-server hosting orthogonal — does NOT touch the H_T-as-MCP-client surface where CP-18's substitution site lives |
| Status post batch 9 | STILL-BOUNDED (unchanged; preserved per Q5 disjointness pin) |
| Gates on | New future arc — (a) per-server-trust framework landing (signed-pinned-only / signed-not-pinned / unsigned trust tiers per AS-axis sandbox-tier-floor); (b) `mcp.*` namespace emission at the H_T-as-MCP-client surface (per U-RT-15 lifecycle); (c) MCP client lifecycle composer landing |

CP-18 retirement remains a separate arc per the Q5 disjointness ratification. No coupling to U-RT-62; no batch 9 transition.

---

## §3 Bounded carry-forward — none new

The batch 8 §3 carry-forward (`mcp-backed-ask-user-question-surface-fast-mcp-handler`) is **CLOSED** at this batch: the FastMCP transport-level handler registration landed at U-RT-62 AC #2 + AC #3 + AC #4 (materialize_mcp_server_stage + run_workflow tool + ServerCtxElicitCallback replacing _PlaceholderMCPCallback as production default).

No new bounded carry-forwards introduced this batch. The 7 Class 3 records from the U-RT-60 → U-RT-62 arc are independent (see workspace memory at `[[phase-7-bootstrap-status]]`):

| Record | Status at batch 9 |
|---|---|
| `class_3_tension_q6_scope_widening_contract_shape_composability.md` | OPEN (independent arc) |
| `class_3_tension_meta_architecture_hitl_palette_drift.md` | OPEN (carried) |
| `class_3_tension_per_axis_claude_md_v2_1_to_v2_4_count_drift.md` | OPEN (carried) |
| `class_3_tension_u_rt_59_spec_prose_drift.md` | OPEN (carried) |
| C-RT-04 §4 spec field-table drift | OPEN (carried) |
| §14.8.3 line 1715 impl-discretion broad-reading carry-forward | **CLOSED** at AC #9 docstring update (commit `2acdce9`) |
| Spec §15 U-RT-62 row addition | OPEN-NEW (owed at next spec revision pass) |

---

## §4 Cumulative retirement ledger (post batch 9)

Per `.harness/phase-7d-retirement-ledger-v2.md` §5 + batches 1-8:

| Status | Count | Substitutions |
|---|---|---|
| RETIRED (post batch 9) | **22 / 49 (44.9%)** | (15 from batches 1-2) + CP-3 / CP-4 / CP-5 / CXA-5 (batch 3) + CP-10 / CP-13 (batch 4) + **H_T-CP-20 (batch 9 NEW)** |
| RETIRE-READY (post batch 9) | **0 / 49** | (H_T-CP-20 transitioned to RETIRED this batch) |
| PARTIAL (post batch 9) | 2 / 49 (unchanged) | AS-8 (batch 2) + CP-14 single-sub-agent slice (batch 4) |
| STILL-BOUNDED (post batch 9) | 9 / 49 (unchanged) | Per-axis CLAUDE.md inventories; CP-18 preserved per Q5 disjointness; CP-12 / CP-16 / CP-17 / CP-19 / CP-21 / CP-22 / CP-23 + 2 others |

CP-axis post-batch-9: **10 / 22 RETIRED (45.5%) + 0 RETIRE-READY + 1 PARTIAL (CP-14 single-sub-agent slice) + 11 STILL-BOUNDED**. Cumulative 22/49 RETIRED (44.9%). The RETIRE-READY ledger category introduced at batch 8 is now empty (the one entry — H_T-CP-20 — transitioned to RETIRED at this batch); the category remains in the ledger for future RETIRE-READY transitions.

**Quality delta this batch:** The U-RT-62 FastMCP server hosting impl arc materializes the spec v1.12 §14.8.3 v1.12 workflow-initiation topology pin end-to-end. The H_T-as-MCP-server hosting topology is operational: bootstrap stage 2 materializes the FastMCP server + registers the `run_workflow` MCP tool; stage 5 rebinds the surface's default callback from `_PlaceholderMCPCallback` to `ServerCtxElicitCallback`; the e2e integration test exercises the full Claude Code → run_workflow → HITL gate → ctx.elicit → response → continuation → RunResult path through the in-process MCP envelope. H_T-CP-20 transitions RETIRE-READY → RETIRED honestly per X-AL-2 strict reading. The C-RT-18 contract surface has now seen 3 Class 1 forks resolved across 3 sessions: binding-mechanism APPLIED @ `fb545ec` (v1.10); span-attr-carrier-drift APPLIED @ `9b6b007` (v1.11); wrap-asymmetry sync/async APPLIED @ `e9b9c49` (v1.11 §14.8.1); workflow-initiation topology APPLIED @ this arc (v1.12 §14.8.3).

---

## §5 Cross-axis cascade impact

§6.3.1 H_T-CP-1 → H_T-AS-8 anthropic.* namespace emission: **DORMANT** (preserved at this batch).

§6.3.2 F-CP-01 Stage 3b inversion cascade: **FULLY DISCHARGED at batch 3** (preserved).

§6.3.3 (no §6.3.3 declared at Meta-Architecture §6.3 — preserved).

**U-RT-62 cascade impact:** H_T-CP-20 RETIRE-READY → RETIRED does NOT advance H_T-CP-18 per Q5 disjointness pin (server-side vs client-side surface orthogonality). No cross-axis cascade at the IS / AS / OD axes — the FastMCP server hosting is harness-runtime-internal per the v1.12 topology pin. The CP→OD CXA edge at U-CP-46 → U-OD-00 (HITL gate response audit-write per CXA v2.5 §2.3.7) remains operational; no new CXA edges introduced by U-RT-62 (the H_T-as-MCP-server hosting is runtime-spec-internal per Q5 disjointness — no per-axis spec amendments required).

---

## §6 Cross-references — per-axis CLAUDE.md updates owed

Per AC #J amendment requirement: "Updates `harness-cp/CLAUDE.md` §4.1 substitution-table status entries (H_T-CP-20 row: RETIRE-READY → RETIRED; H_T-CP-18 row: STILL-BOUNDED preserved)."

| File | Owed update | Status |
|---|---|---|
| `harness-cp/CLAUDE.md` §4.1 | Move H_T-CP-20 from RETIRE-READY row to RETIRED 2026-05-21 (batch 9) row; preserve H_T-CP-18 in STILL-BOUNDED row | Owed at next harness-cp/CLAUDE.md revision pass (cross-file back-reference; per the spec-writer SKILL.md §5 procedure pattern for downstream absorption; non-blocking for batch 9 filing). |

---

## §7 Filing footer

| Field | Value |
|---|---|
| Filed at | 2026-05-21 (U-RT-62 FastMCP server impl arc APPLIED landing — AC #J batch 9 retirement event) |
| Cumulative status | **22/49 RETIRED (44.9%, +1 from batch 8)** + 0/49 RETIRE-READY (down from 1; H_T-CP-20 transitioned) + 2 PARTIAL (AS-8 + CP-14) + 9 STILL-BOUNDED (unchanged; CP-18 preserved per Q5 disjointness) |
| Predecessor batch | `phase-7d-retirement-events-batch-8.md` (post-U-RT-60 wrap-asymmetry impl arc; H_T-CP-20 STILL-BOUNDED → RETIRE-READY; cumulative 21/49 unchanged) |
| Audit scope | 7 U-RT-62 implementation commits (`0d59943` AC #1 HarnessMCPServer + `9e07f4a` AC #2/#3 stage 2 wiring + tool registration + `70f3f53` AC #4 ServerCtxElicitCallback + `bfdd30e` AC #5/#7/#8 api.run reframe + `8b9c14c` AC #6 e2e topology test + `2acdce9` AC #9 placeholder retention reading + this commit AC #J retirement event filing) |
| Substantive content | §1 H_T-CP-20 RETIRE-READY → RETIRED (criterion A met + criterion B FULLY met per AC #6 e2e load-bearing test); §1.4 Q5 disjointness pin — H_T-CP-18 does NOT advance jointly + amends batch 8 §3 carry-forward language; §2 CP-18 disjointness preservation; §3 batch 8 §3 carry-forward CLOSED (FastMCP transport-level handler registration landed at U-RT-62); §4 cumulative ledger 22/49 RETIRED (44.9%); §5 cross-axis cascade no impact; §6 harness-cp/CLAUDE.md §4.1 update owed |
| Successor batch | TBD — gates on (a) FastMCP H_T-as-MCP-client surface arc landing (jointly progresses CP-18 retirement); (b) PRICE_TABLE_REF rate-table authoring (OD-5 STILL-BOUNDED unblock per `[[fork-price-table-ref-substitution-retirement]]` + `[[fork-cost-record-audit-ledger-wiring-residual]]`); (c) validator composer + pause/resume composer arcs (CP-21 + CP-22 STILL-BOUNDED unblock) |
| Revision policy | Forward-only ledger discipline per workspace `CLAUDE.md` §4.3 — batch 9 is a new filing referencing batches 1-8; **amends batch 8 §3 carry-forward language** (Q5 disjointness pin re H_T-CP-18 orthogonality) per forward-only discipline (new batch record, NOT retroactive edit to batch 8 §3). |

*Batch 9 retirement event filed per the U-RT-62 FastMCP server hosting impl arc APPLIED landing. **1 RETIRE-READY → RETIRED transition** (H_T-CP-20; criterion A met + criterion B FULLY met via AC #6 e2e load-bearing test). **First new RETIRED transition since batch 4 (2026-05-20).** Cumulative 22/49 RETIRED (44.9%, +1 from batch 8). Q5 disjointness pin amends batch 8 §3 carry-forward language: H_T-CP-18 does NOT advance jointly with H_T-CP-20 — orthogonal substitution sites (server-side vs client-side MCP surfaces) per the v1.12 topology pin (Reading α). Per-axis CLAUDE.md §4.1 update owed at next revision pass.*
