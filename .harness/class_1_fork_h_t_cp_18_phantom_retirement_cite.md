# Class 1 Fork — H_T-CP-18 phantom retirement cite at Meta-Architecture §5.4 line 124

**Filed:** 2026-05-22 at H_T-CP-18 retirement-event filing arc, pre-event-record.
**Status:** ✅ FULLY-APPLIED + RETIRED 2026-05-23..batch-16 (status-line refreshed 2026-05-27) — operator ratified α + γ-audit-appendix at `245d07e`; Meta-Arch v1 → v1.1 absorption at `40d9f78` (α row-124 fix re-pointing U-CP-45 → U-CP-00b + U-RT-73/74/75 + U-RT-68 + NEW §5.1.1 cross-axis cite convention + §5.8 γ-audit appendix surfacing 5 additional phantom cites at H_T-CP-16/17/19/20/21 — all subsequently resolved across Meta-Arch v1.2..v1.5 lineage); batch-10 ledger transit H_T-CP-18 STILL-BOUNDED → RETIRE-READY; H_T-CP-18 RETIRED jointly with H_T-AS-2 at batch-16 `8e6311f` (U-RT-86 e2e vs in-process stdio MCP echo fixture) per `[[h-t-cp-16-17-retire-ready-gate-runtime-composer-arcs]]`. Species 3 stale-carry per workflow v1.9 §7.4.7.2.

_Original filing footer:_ **Status:** RATIFIED 2026-05-23 — α + γ-audit-appendix; α sub-question: YES (cross-axis runtime cites permitted on CP-axis rows, material-location-resident reading).
**Scope:** Phase 7d substitution retirement discipline; halt-execution Class 1
per `Project_Workflow_v1_8.md` §2.7.6 + workspace CLAUDE.md §4.3.
**Surfaced by:** `phase-7-substitution-retirement` skill at §7 halt-condition
("Retirement criterion column at Meta-Architecture §5 is empty or
under-specified for the substitution → Class 1 → Meta-architecture revision
(design-phase back-flow)") during H_T-CP-18 retirement filing arc against
L9-septies cluster close at HEAD `5d6c25c`.
**Disposition:** H_T-CP-18 retirement filing HALTED. NO retirement event
record written. NO RETIRE-READY transition recorded. The L9-septies stage-3a
+ stage-5 landings (U-RT-73 + U-RT-74 + U-RT-75 + U-RT-68 rewrite) materialize
the H_T-side MCP-client surface that *would* satisfy criterion B against a
correctly-pointed retirement cite — but the cite as written points at the
wrong unit.

---

## 1. The gap

`Phase_7_Meta_Architecture_v1.md` §5.4 line 124 states:

> | H_T-CP-18 | MCP integration + per-server trust + `mcp.*` consumption | C-CP-18 §18 | **U-CP-45** | AS consumer |

The cited retirement unit is `U-CP-45`. Empirical inventory:

| Surface | State at HEAD `5d6c25c` |
|---|---|
| `U-CP-45` in `Implementation_Plan_Control_Plane_v2_17.md` | **0 hits** |
| `U-CP-45` in `Implementation_Plan_Control_Plane_v2_16.md` | 0 hits |
| `U-CP-45` in `Implementation_Plan_Control_Plane_v2_{9..15}.md` | 0 hits each |
| `U-CP-45` in `Implementation_Plan_Control_Plane_v2_8.md` | 1 hit (stray cross-reference, no unit body) |
| `U-CP-45` in `Implementation_Plan_Control_Plane_v2_6.md` | 5 hits (carrier-table + DAG cites only — no unit body) |
| `U-CP-45` in `Implementation_Plan_Control_Plane_v2.md` (original) | unit body at line 2366 |

The original v2.0 plan body at line 2366 reads:

> #### U-CP-45 — Implement 5-axis composition (C-AS-12 + C-CP-19) + operator-policy override + key-rotation two-row pattern
>
> **Implements:** [C-CP-19 §19.3, §19.5, C-CP-20 §20.3, §20.3.1]

That is the **C-CP-19 cross-deployment monotonicity + C-CP-20 HITL palette**
surface — NOT the C-CP-18 MCP integration surface. The cite at Meta-Arch §5.4
line 124 ("H_T-CP-18 retired when U-CP-45 lands") is structurally wrong: the
unit it points at implements a different contract entirely.

`MCPTrustTier` appears in U-CP-45's body only as an *input field* to the
5-axis composition (line 2386 input record `mcp_trust_tier: MCPTrustTier`).
The carrier itself lands at **U-CP-00b** per v2.6 line 180
(`MCPTrustTier | U-CP-43, U-CP-45 | [U-CP-00b]`). Meta-Arch row 124 cites
a consumer of the trust-tier enum, not the producer; and not any unit
implementing per-server-trust evaluation or `mcp.*` namespace emission at
runtime.

---

## 2. What's actually materialized at HEAD `5d6c25c`

L9-septies cluster close (commits `bd17b10`..`00da5ef`) landed the
H_T-side MCP-client surface:

| Surface | Materialized at | Status |
|---|---|---|
| `mcp_client_host` carrier + stage-3a factory | `harness-runtime/.../bootstrap/factories/mcp_client_host_factory.py` (U-RT-73) + `stage_3a_cp_clients.py:48` | ✓ stage-3a invokes factory; ctx.mcp_client_host populated |
| `PerServerTrustEvaluator` carrier | `harness-cp/src/harness_cp/per_server_trust_evaluator.py` | ✓ constructed by U-RT-75 step 1 |
| `MCPClientNamespaceEmitter` carrier (7 `mcp.*` attribute keys) | `harness-cp/src/harness_cp/mcp_client_namespace_emitter.py:73-79` | ✓ constructed by U-RT-75 step 2 |
| Stage-5 5-step composition (PerServerTrustEvaluator → emitter → bare RuntimeToolDispatcher → RetryBreakerToolDispatcher wrap → wire ctx) | `harness-runtime/.../bootstrap/factories/runtime_tool_dispatcher_factory.py` (U-RT-75) | ✓ wired at stage 5 |
| `TOOL_STEP → SyncDispatcherFacade(ctx.tool_dispatcher)` driver binding | `stage_5_loop_init.py:301` (U-RT-68 rewrite) | ✓ bound by default |
| `mcp.tool.call` span emission site at production tool-dispatch | `harness-runtime/.../lifecycle/runtime_tool_dispatcher.py:375` | ✓ tracer.start_as_current_span("mcp.tool.call") in production path |

**Criterion B status against the surface description** ("MCP integration +
per-server trust + `mcp.*` consumption"): substantially materialized —
production tool-dispatch invokes the trust evaluator + namespace emitter +
emits `mcp.tool.call` span at the dispatch site. **Bounded carry-forward:**
default config produces empty `mcp_servers=[]`; `mcp_client_host_factory.py:71`
returns a sentinel host with `server_name="<empty-sentinel>"`; with no MCP
servers configured, no live MCP-client traffic exercises the chain end-to-end.
Mirrors the H_T-CP-20 batch-8 RETIRE-READY pattern: structural wiring
materialized + production span emission site present; live operational
end-to-end exercise gated on operator config (`mcp_servers` non-empty) +
external MCP server availability.

**This finding is observation only — it does NOT resolve the fork.** The
fork is about the cite, not the surface. Even if criterion B were
unambiguously met, we cannot file a retirement event against an
incorrectly-pointed cited unit without violating X-AL-2 retirement
criterion fidelity ("Every substitution at §5 carries a retirement
criterion. Retirement = (cited unit IDs landed) ∧ (substituted H_E surface
no longer invoked at substitution site). Both conditions required.").

---

## 3. Three readings

### 3.1 Reading α — re-point Meta-Arch §5.4 row 124 to actual MCP-integration units

**Action:** Amend `Phase_7_Meta_Architecture_v1.md` §5.4 line 124 — replace
cited unit column `U-CP-45` with the actual MCP-integration unit set.
Candidate replacement: `U-CP-00b` (MCPTrustTier carrier landing) + the
L9-septies runtime axis cites (`U-RT-73` + `U-RT-74` + `U-RT-75` + `U-RT-68`
rewrite) since the MCP-integration surface is runtime-axis-resident not
CP-axis-resident at the materialization level.

**Open sub-question:** Does the cited unit column accept cross-axis (runtime)
cites? The meta-arch row format is per-axis (H_T-CP-* row → CP-axis cites).
If the actual implementation surface is runtime-axis-resident, that may
itself be a meta-arch shape gap. Operator decision needed.

**Cost:** Single-row meta-arch edit + version bump. Spec-writer revision-pass
discipline. ZERO cross-axis cascade.

**Downstream:** Re-evaluate criterion B against the re-pointed cites at a
follow-on retirement filing arc. With α's likely re-point, criterion B is
the H_T-CP-20-batch-8-pattern PARTIAL: structural wiring met, end-to-end
exercise gated on config + external MCP server availability. Likely lands
as STILL-BOUNDED → RETIRE-READY transition (not RETIRED).

### 3.2 Reading β — verify against surface description bypassing cite

**Action:** Treat the `U-CP-45` cite at row 124 as effectively orphaned;
verify criterion B against the row's surface description column ("MCP
integration + per-server trust + `mcp.*` consumption") directly without
re-pointing the cite.

**Cost:** No meta-arch edit. Filing proceeds.

**Risk:** Violates X-AL-2 verification discipline — verifies against the
description column, not the citation column. The whole point of the
cited-unit column is to provide an empirically-verifiable retirement
criterion; substituting "the description sounds about right" for "this
unit landed" is the **silent absorption** failure mode workspace CLAUDE.md
§4.3 explicitly forbids ("Silent absorption of design-phase defects is
the worst failure mode"). Recording a retirement event under reading β
contaminates downstream retirement-ledger fidelity and propagates to any
future re-verification pass.

**Disposition:** Not recommended. Documented for completeness.

### 3.3 Reading γ — HALT all CP-axis retirement filings + audit Meta-Arch §5.4 column for additional phantom cites

**Action:** Halt the H_T-CP-18 retirement filing AND defer all pending
CP-axis retirement filings until a Meta-Arch §5.4 audit pass verifies the
cited-unit column for all 24 H_T-CP-* rows against the current plan v2.17.
Pattern-density observation: this is the 3rd phantom-cite Class 1 fork in
2 sessions in the U-RT-68-adjacent author-time-vs-implementation-time
drift cluster (joins `[[fork-sandbox-decision-policy-phantom-cite]]` +
`[[fork-u-rt-68-retry-wrap-and-bootstrap-wiring-gap]]`). The meta-arch
§5.4 column appears to have been authored before plan v2.7 renumbering
and never reconciled. Likelihood of additional phantom cites in the
column is high.

**Cost:** Audit pass against 24 rows; per phantom finding, an α-style
re-point edit. Bounded to single artifact (`Phase_7_Meta_Architecture_v1.md`
§5.4).

**Downstream:** Cleared meta-arch §5.4 column unblocks all CP-axis
retirement events with empirically-verifiable cites; eliminates the
phantom-cite-recurrence pattern.

**Disposition:** Recommended by skill author per `[[advisor-before-
substantive-work-for-cross-axis-blockers]]` trigger condition 1 ("AC body
cites a type/class/producer not grep-confirmed at HEAD"). The 1-row α
fix is minimal but addresses only this surfacing; the column-wide γ audit
addresses the root cause.

---

## 4. Recommendation

**α + γ-audit-appendix.** Apply the α single-row fix to row 124 to unblock
H_T-CP-18's retirement re-evaluation. THEN conduct a γ-style audit pass
across the remaining 23 H_T-CP-* rows in the same meta-arch revision arc
to surface (and resolve) any further phantom cites before they HALT
follow-on retirement filings one at a time.

Both readings are no-axis-spec-extension — neither extends H_T contracts.
Both preserve X-AL-3 (no silent design extension). ZERO cross-axis
cascade for either.

---

## 5. Cross-axis cascade analysis

ZERO axis cascade regardless of reading.

- Reading α: meta-arch single-row edit; no spec change; no plan change;
  no code change.
- Reading β: NOT RECOMMENDED — would contaminate retirement ledger; no
  artifact change otherwise.
- Reading γ: meta-arch column audit; per-finding α-style edits as needed;
  no spec/plan/code change.

L9-septies cluster close stands. 10-CP-D cluster close stands. The 2751
test-pass count stands. The fork is about meta-arch cite fidelity, not
implementation surface correctness.

---

## 6. Routing

Per `Project_Workflow_v1_8.md` §2.7.6 + workspace CLAUDE.md §4.3:

| Step | Action |
|---|---|
| 1 | Operator selects α / β / γ / α+γ |
| 2 | If α or α+γ: route to `spec-writer` skill for `Phase_7_Meta_Architecture_v1.md` §5.4 row 124 amendment (and column audit pass if γ) |
| 3 | If γ-audit surfaces additional phantom cites: file as Class 3 amendments within the same arc (single artifact, bounded scope) |
| 4 | At meta-arch revision close: re-invoke `phase-7-substitution-retirement` skill for H_T-CP-18 against the re-pointed cites; expect RETIRE-READY transition (not RETIRED — bounded by empty-sentinel config carry-forward) |

---

## 7. Related memory

- `[[fork-sandbox-decision-policy-phantom-cite]]` — sibling phantom-cite
  Class 1 fork RESOLVED at L9-septies cluster close per Q1=C-i; first
  instance of the pattern this session-arc cluster
- `[[fork-u-rt-68-retry-wrap-and-bootstrap-wiring-gap]]` — parent fork
  whose absorption arc introduced the prior phantom cite; same pattern
  cluster
- `[[advisor-before-substantive-work-for-cross-axis-blockers]]` — feedback
  memory written this session-arc memorializing the
  AC-cites-unverified-unit trigger condition; this fork is the canonical
  *meta-arch* (not spec/plan) face of that pattern
- `[[halt-route-split-AC-pattern]]` — sibling pattern for
  partial-materializability AC bundles; this fork is the cite-fidelity
  analog applied to retirement criteria

---

## 8. Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/class_1_fork_h_t_cp_18_phantom_retirement_cite.md` |
| Authored at | 2026-05-22 H_T-CP-18 retirement filing arc, pre-event-record |
| Authoring authority | `phase-7-substitution-retirement` skill §7 halt-condition; advisor-before-substantive-work pattern §1 trigger condition |
| Predecessor | None at this fork; parent pattern at sibling memory entries §7 |
| Successor consumption | Operator α/β/γ selection → spec-writer (α path) → re-invoke phase-7-substitution-retirement (re-evaluation pass) |
| HEAD at filing | `5d6c25c` (L9-septies + 10-CP-D cluster closes; 2751 tests green; clean tree) |
| Status | RATIFIED 2026-05-23 — α + γ-audit-appendix; α sub-question Yes (cross-axis runtime cites permitted) |

---

## 9. Ratification

**Ratified:** 2026-05-23 at /checkpoint-resume session.

**Routing decision:** α + γ-audit-appendix.

**α sub-question resolution:** YES — Meta-Arch §5.4 cited-unit column accepts
cross-axis (runtime) cites on CP-axis rows under a material-location-resident
reading (cite where the surface actually landed, not the authority-axis-resident
reading). This is a structural reading of the §5.4 column that may itself warrant
a Class 3 documentation note at the meta-arch revision-pass to make the convention
explicit.

**Spec-writer work items for the meta-arch revision arc:**

1. **α single-row fix at row 124** — cited-unit column: `U-CP-45` → `U-CP-00b` +
   `U-RT-73` + `U-RT-74` + `U-RT-75` + `U-RT-68`. Spec-writer to verify the four
   runtime unit cites resolve at `Implementation_Plan_Harness_Runtime_v2_13.md`
   L9-septies cluster and `U-CP-00b` at `Implementation_Plan_Control_Plane_v2_17.md`.
2. **γ audit appendix** — column-wide pass across all 24 H_T-CP-* rows at §5.4.
   For each phantom finding, apply α-style re-point in the same revision arc.
   File a Class 3 amendment record per finding (single-artifact bounded scope per
   §5 of this fork doc).
3. **Class 3 documentation note** — make the material-location-resident reading
   of the cited-unit column explicit at §5.4 preamble (or wherever §5 column
   conventions are documented) to foreclose ambiguity on future cross-axis
   retirement cites.

**Post-revision:** re-invoke `phase-7-substitution-retirement` skill against
H_T-CP-18 with the re-pointed cites. Expected outcome: RETIRE-READY transition
(structural wiring met; live exercise gated on `mcp_servers` non-empty +
external MCP server availability — mirrors H_T-CP-20 batch-8 pattern).

**Companion memory entry:** `[[fork-h-t-cp-18-phantom-retirement-cite]]` written
at ratification per workspace convention (memory follows ratification, not OPEN).

---

*End of Class 1 fork doc. Filing event-record for H_T-CP-18 HALTED pending
resolution.*
