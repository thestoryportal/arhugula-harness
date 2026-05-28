# Phase 7d Retirement Events — Batch 24

| Field | Value |
|---|---|
| Batch number | 24 |
| Filed at | 2026-05-28 (post H_T-AS-5 RETIRED batch-23 close; AS-8 PARTIAL → 6-sub-row decomposition + 3 immediate sub-RETIRED transits at ledger-v2-layer per operator AskUserQuestion Option A 2026-05-28 ratification + advisor pre-substantive consultation Scope B affirmation) |
| Filed by | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5 + retirement-ID-scoping correction per drift doc `.harness/class_3_drift_as_8_partial_row_per_namespace_breakdown.md` §5(b) operator-discretion routing trigger |
| Predecessor batch | `phase-7d-retirement-events-batch-23.md` (2026-05-28, 1 STILL-BOUNDED → RETIRED direct transit for H_T-AS-5; cumulative 30/49 RETIRED + 0/49 RETIRE-READY + 6/49 PARTIAL + 13/49 STILL-BOUNDED = 36/49 advanced) |

---

## §0 Batch context

**Status type: 1 retirement-ID-scoping correction (AS-8 monolithic → 6 sub-rows AS-8a/b/c/d/e/f at ledger-v2-layer) + 3 simultaneous RETIRED transits (AS-8a + AS-8b + AS-8c).** Decomposition scope per advisor Scope B: ledger-v2 + harness-as/CLAUDE.md + workspace CLAUDE.md edits ONLY; **Meta-Arch §2.2 PRESERVED VERBATIM** at design-declaration layer per X-AL-3 + drift doc §5(b) framing.

**Counting math (explicit dual-view per operator Option A "Workspace cardinality 49 → 54 rows; RETIRED 30 → 33"):**

Pre-decomp ledger-v2 view (post-batch-23):
- AS-axis at ledger v2 §4: 4/5 RETIRED (AS-1/2/4/5 RETIRED; AS-8 PARTIAL) — AS-9 not in ledger (authoring-only)
- Workspace ledger cumulative: 30/49 RETIRED (per batch-23 close)

Decomposition event at this batch:
- AS-8 row (1 substitution) → AS-8a / AS-8b / AS-8c / AS-8d / AS-8e / AS-8f (6 sub-substitutions)
- Net denominator delta: +5 (1 → 6)
- AS-axis ledger denominator: 5 → 10
- Workspace ledger denominator: 49 → 54

Immediate close transits (criteria already MET pre-decomp; close lands at decomp event):
- AS-8a (anthropic.* 10/10 LANDED): PARTIAL-ADVANCE → RETIRED
- AS-8b (mcp.* 7/7 LANDED): PARTIAL-ADVANCE → RETIRED
- AS-8c (memory.* 6/6 LANDED): PARTIAL-ADVANCE → RETIRED

Carry-forward sub-rows (not in this batch's RETIRED set):
- AS-8d (skill.* 0/6): STILL-BOUNDED (gates on Skills loading runtime composer authoring)
- AS-8e (files.* 0/8): STILL-BOUNDED-INDEFINITELY (Files arc DEFERRED per runtime spec v1.17 §14.C)
- AS-8f (managed_agents.* 0/3): STILL-BOUNDED (gates on managed_agents SDK integration)

Post-decomp ledger v2 view (post-batch-24):
- AS-axis at ledger v2 §4 (decomposed view): 7/10 RETIRED + 3/10 STILL-BOUNDED (AS-8d/e/f)
- Workspace ledger cumulative: 33/54 RETIRED (61.1%)
- Numerator delta: +3 (AS-8a/b/c immediate close)
- Denominator delta: +5 (AS-8 → 6 sub-rows)
- Net percentage: 30/49 = 61.2% → 33/54 = 61.1% (flat; decomposition is structural-not-progress)

**AS-axis effective-active view (excluding INDEFINITE deferrals):**
- AS-8e files.* INDEFINITELY-DEFERRED is excluded from active-substitution denominator
- Active AS-axis denominator: 10 - 1 (AS-8e) + 1 (AS-9 from Meta-Arch) = 10 (AS-axis 11 total Meta-Arch + ledger minus AS-8e DEFERRED; or 9 if AS-9 also excluded as authoring-only)
- Active AS-axis RETIRED: 7 ledger + 1 AS-9 = 8 → 8/10 active = 80.0%

This matches operator's "8/9" framing if interpreted as: 5 ledger-RETIRED (AS-1/2/4/5) + 3 new AS-8 sub-RETIRED (a/b/c) + 1 AS-9 authoring = 9 active substitutions excluding both AS-8e INDEFINITE and AS-8d/f future-gated; 8 RETIRED of those 9 + 1 STILL-BOUNDED (the operator framing collapsed AS-8d + AS-8f into "1 remaining"). Either reading is empirically grounded; this batch publishes all three (raw 11 / active 10 / operator-collapsed 9) to avoid silent reading-collapse.

This batch records the retirement-ID-scoping correction event per drift doc §5(b) operator-discretion routing trigger:

| Commit | Artifact | Authority |
|---|---|---|
| (this commit) | `harness-as/CLAUDE.md` §4.1 — H_T-AS-8 monolithic row REPLACED with 6 sub-rows (AS-8a/b/c/d/e/f) + H_T-AS-5 row updated to RETIRED per batch-23 close | Operator AskUserQuestion ratification 2026-05-28 Option A + advisor Scope B pre-substantive consultation 2026-05-28 + drift doc §5(b) routing trigger |
| (this commit) | NEW `.harness/phase-7d-retirement-events-batch-24.md` (this file) | Retirement-ledger discipline per `phase-7-substitution-retirement` skill §3.2 |
| (this commit) | Co-published bookkeeping: workspace `CLAUDE.md` §2.4 AS plan row appended with batch-24 decomposition note + cumulative-RETIRED math 30/49 → 33/54 | Workspace bookkeeping discipline per ledger-v2 §0.5 forward-only ledger + per-axis CLAUDE.md authoritative-current-state |
| (this commit) | `.harness/phase-7d-retirement-ledger-v2.md` §11 NEW supersession entry §11.X documenting AS-8 decomposition event (frozen snapshot preservation per §0.5) | Ledger-v2 forward-only discipline + §11 surfaced-supersession-sites convention |

**Reframing closure note.** Per AS-5 batch-23 §1.2 + CP-19 batch-22 §1.2 sub-species 7 lineage: this batch surfaces a *third* shape of gate-text-stale-vs-production. Sub-species 7 was catalogued at batch-22 as "operator-explicit-deferred-close-gate" (CP-19 RETIRE-READY tier); generalized at batch-23 as "gate-text-stale-vs-production-architecture" (AS-5 STILL-BOUNDED tier). Batch-24 surfaces a *retirement-ID-scoping-too-coarse* shape (AS-8 PARTIAL tier — the monolithic ID was wrongly scoped to cover 6 independent producer sites with 6 distinct close gates). Future workflow-doc revision may catalogue this as sub-species 7c (or 8) distinct from 7a (CP-19 shape) + 7b (AS-5 shape). Pre-decomp at AS-8: "all-or-nothing closure friction" per drift doc §5(b); post-decomp: per-sub-row close enables 3 immediate RETIRED transits + preserves 3 sub-rows with explicit-distinct gates.

**Conclusion (preview):** **1 decomposition event + 3 sub-RETIRED transits.** Workspace ledger cumulative: **33/54 RETIRED** (61.1%, structural cardinality bump 49 → 54; numerator +3). AS-axis ledger decomposed view: **7/10 RETIRED** (70.0%; was 4/5 = 80.0% monolithic). Active-substitution view (excluding INDEFINITE deferrals): **8/10 RETIRED** (80.0%). Meta-Arch §2.2 design-declaration view UNCHANGED (6 AS rows preserved). **ZERO cross-axis cascade** verified — sub-row decomposition is intra-AS-axis-ledger only.

---

## §1 AS-8 monolithic → 6 sub-rows decomposition

### §1.1 H_T-AS-8a (anthropic.* 10-attribute observability namespace) — RETIRED

**Pre-decomp state.** anthropic.* 10/10 LANDED per AS-8 discriminator audit close 2026-05-26 (4/10 cache subset pre-existing + 6/10 closed at discriminator arc): `thinking_mode`, `thinking_budget_tokens`, `thinking_effort`, `batch_id`, `tokenizer_version`, `inference_geo`. Producer site: `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:386-432` gen_ai span.

**Binding-chain verification.**

| Stage | Required evidence | Verified at | Verification shape |
|---|---|---|---|
| 1. Carrier landed | `_AnthropicRequestAttrs` + `_extract_anthropic_request_attrs` | Pre-existing | Per discriminator audit close 2026-05-26 |
| 2. Production consumer site | `gen_ai` span sets all 10 attributes | `llm_dispatch.py:386-432` | Reads carrier; sets attribute at span via `_set(span, "anthropic.*", value)` |
| 3. E2E exercise PASS | gen_ai span carries 10 attrs end-to-end | runtime test suite (1092/1092 pass) | `_AnthropicRequestAttrs` extraction + span attribute set verified at production dispatch path |

All 3 stages MET pre-decomp. RETIRED at batch-24.

**Cross-axis cascade.** AS-8a anthropic.* namespace satisfies the §6.3.1 H_T-CP-1 → H_T-AS-8 cross-axis cascade reference per ledger v2 §8.1. CP-1 still STILL-BOUNDED gating on multi-LLM call site; the anthropic.* attribute emission IS satisfied per CP-1 dependency relaxation (CP-1's gate is the *call site existence*, not the *attribute emission* — and the attribute emission has landed end-to-end at gen_ai span). Ledger v2 §8.1 cascade reference preserved verbatim (§0.5 forward-only).

### §1.2 H_T-AS-8b (mcp.* 7-attribute observability namespace) — RETIRED

**Pre-decomp state.** mcp.* 7/7 LANDED per L9-sexies + L9-septies cluster closes 2026-05-22. Producer site: `mcp_client_namespace_emitter.py:73-79` + `runtime_tool_dispatcher.py:375` (`mcp.tool.call` span).

**Binding-chain verification.**

| Stage | Required evidence | Verified at | Verification shape |
|---|---|---|---|
| 1. Carrier landed | `MCPClientNamespaceEmitter` 7-attribute schema | Pre-existing per L9-sexies | U-CP-69 close `83d3b54` 2026-05-22 |
| 2. Production consumer site | `runtime_tool_dispatcher.py:375` invokes `emit_mcp_call_span` on `mcp.tool.call` span | Pre-existing per L9-septies | U-RT-67 dispatch body + U-RT-75 stage-5 callsite |
| 3. E2E exercise PASS | mcp.tool.call span carries 7 attrs at production dispatch | U-RT-86 L9-novies e2e + batch-16 joint AS-2 close (2026-05-24) | 2/2 e2e tests at `test_runtime_tool_dispatcher_e2e.py` against in-process stdio MCP echo fixture |

All 3 stages MET pre-decomp. RETIRED at batch-24.

**Note.** AS-8b retirement is jointly anchored to AS-2 RETIRED (batch-16 joint close with CP-18) — same MCP-client substrate. AS-8b makes the namespace-attribute-emission slice of that substrate explicit at sub-row layer.

### §1.3 H_T-AS-8c (memory.* 6-attribute observability namespace) — RETIRED

**Pre-decomp state.** memory.* 6/6 LANDED per L9-octies cluster close 2026-05-23 (`42c9a30`). Producer site: `memory_tool_dispatch.py:286-338` (`memory.operation` span); consumer chain at `llm_dispatch.py:354` via `execute_with_memory_callbacks`.

**Binding-chain verification.**

| Stage | Required evidence | Verified at | Verification shape |
|---|---|---|---|
| 1. Carrier landed | `memory.operation` span 6-attribute schema per AS spec C-AS-14 §14.7 | Pre-existing per L9-octies | U-RT-76..U-RT-82 close `42c9a30` 2026-05-23 |
| 2. Production consumer site | `memory_tool_dispatch.py:286-338` opens span + sets 6 attributes | Pre-existing per L9-octies | Producer-side mutation discipline per AS spec v1.5 §14.7 producer-site reference note |
| 3. E2E exercise PASS | memory.operation span emits 6 attrs at memory tool invocation | U-RT-82 e2e at L9-octies close | Real Anthropic API messages.create with tools=[memory_tool] + deterministic-prompt fixture forcing write-path |

All 3 stages MET pre-decomp. RETIRED at batch-24.

**Note.** AS-8c retirement is the FIRST close-event for an observability namespace at memory primitive — H_T-CP-16 memory primitives retirement (RETIRE-READY → RETIRED at batch-14) is jointly anchored.

### §1.4 H_T-AS-8d (skill.* 6-attribute observability namespace) — STILL-BOUNDED

**Pre-decomp state.** skill.* 0/6 — no producer site. Gates on Skills loading runtime composer + `SkillActivationSpanEmitter` carrier authoring.

**RETIRED gate (future).** Estimated ~3-5 commits: (1) `SkillActivationSpanEmitter` carrier at AS-axis or harness-cp Skills loader; (2) producer-site invocation at Skills loading path opening `skill.activation` span; (3) tests + e2e against real Skills fixture.

**Carry-forward.** Sub-row STILL-BOUNDED post-batch-24; awaits future Skills-loader arc.

### §1.5 H_T-AS-8e (files.* 8-attribute observability namespace) — STILL-BOUNDED-INDEFINITELY

**Pre-decomp state.** files.* 0/8 — Files arc DEFERRED INDEFINITELY per runtime spec v1.17 §14.C (Memory-only scope ratified 2026-05-23 at `.harness/class_1_fork_h_t_cp_16_17_executable_consumer_absence.md` §16 ratified absorption).

**RETIRED gate (future, INDEFINITE).** Not gated on observability decisions; gated on Files API surface authoring decision at operator-discretion timing. If/when Files arc opens, AS-8e will land with the Files producer composer.

**Carry-forward.** Sub-row STILL-BOUNDED-INDEFINITELY per X-AL-2 bounded-residual carry; not a defect.

### §1.6 H_T-AS-8f (managed_agents.* 3-attribute observability namespace) — STILL-BOUNDED

**Pre-decomp state.** managed_agents.* 0/3 — no producer site. Gates on Anthropic managed_agents beta SDK integration into H_T as a separate H_T primitive landing.

**RETIRED gate (future).** Beta SDK shape: `AgentCreateParams` per Anthropic SDK `/anthropics/anthropic-sdk-python` docs. Integration arc would land managed_agents primitives at LLM-dispatch layer + observability emission at `managed_agents.runtime` span.

**Carry-forward.** Sub-row STILL-BOUNDED post-batch-24; awaits future managed_agents integration arc.

### §1.7 Sibling row impact

| Row | Status (post batch-23) | Status (post batch-24) | Reason |
|---|---|---|---|
| H_T-AS-1 | RETIRED | Unchanged | — |
| H_T-AS-2 | RETIRED | Unchanged | — |
| H_T-AS-4 | RETIRED | Unchanged | — |
| H_T-AS-5 | RETIRED (batch-23) | Unchanged | Carried forward to refresh harness-as CLAUDE.md row at this batch |
| H_T-AS-8 (monolithic) | PARTIAL | **DECOMPOSED → AS-8a/b/c/d/e/f** | **This batch — retirement-ID-scoping correction** |
| H_T-AS-8a | (did not exist) | **RETIRED** | **This batch — immediate close at decomposition; criteria already MET pre-decomp** |
| H_T-AS-8b | (did not exist) | **RETIRED** | **This batch — immediate close at decomposition; criteria already MET pre-decomp** |
| H_T-AS-8c | (did not exist) | **RETIRED** | **This batch — immediate close at decomposition; criteria already MET pre-decomp** |
| H_T-AS-8d | (did not exist) | STILL-BOUNDED | **This batch — gate on future Skills loader runtime composer** |
| H_T-AS-8e | (did not exist) | STILL-BOUNDED-INDEFINITELY | **This batch — Files arc DEFERRED INDEFINITELY per runtime spec v1.17 §14.C** |
| H_T-AS-8f | (did not exist) | STILL-BOUNDED | **This batch — gate on future managed_agents SDK integration** |
| H_T-AS-9 | RETIRED (authoring) | Unchanged | — |

---

## §2 Operator-opt-in RETIRE-READY pattern (post-batch-24)

Pattern members across batches 10–24: **7 historical members** (CP-16, CP-18, AS-2, CP-21, CP-22, AS-4, CP-19); **all 7 RETIRED**. **Operator-opt-in RETIRE-READY bucket REMAINS EMPTY post-batch-24** (no new entrants — batch-24 is a decomposition + immediate-close event, not a RETIRE-READY transit).

**Pattern sub-species evolution.** Sub-species 7 (gate-text-stale-vs-production) catalogued at batch-22 §2 has now evolved across 3 distinct closure shapes:

| Sub-species | Tier shape | First close event | Distinctive feature |
|---|---|---|---|
| 7a operator-explicit-deferred-close-gate | RETIRE-READY → RETIRED via reframe | CP-19 batch-22 | Operator-deferred gate-text revealed as in-process contract surface |
| 7b gate-text-stale-vs-production-architecture | STILL-BOUNDED → RETIRED via reframe | AS-5 batch-23 | Helper-vs-OTel-span abstraction mismatch; literal gate-text structurally impossible |
| 7c retirement-ID-scoping-too-coarse | PARTIAL → decompose + immediate sub-close | AS-8 batch-24 | Monolithic ID covered 6 independent producer sites; decomposition enables per-sub-row close |

Future workflow-doc revision MAY canonicalize the sub-species 7 split at §7.4.7.2 sub-species column. Pattern: pre-substantive advisor consultation surfaced all 3 distinct closure-event-classes; operator AskUserQuestion ratified the reframe shape; same-session close at each.

---

## §3 Adjacent observations

(a) **Workflow v1.10 §7.4.7.3.B production application #2.** Session-resumption inherited-framing audit operationally validated SECOND PRODUCTION USE this session (first was AS-5 batch-23 §7.4.7.3.B audit). Checkpoint framing "AS-8 PARTIAL → RETIRED next arc" was empirically falsified at §7.4.7.3.B audit; reframe routed via AskUserQuestion. Discipline canonical.

(b) **Drift doc §5(b) cite-shape correction owed.** `class_3_drift_as_8_partial_row_per_namespace_breakdown.md` §5(b) cites "retirement-ledger v2 §6 layer" but AS-axis is at ledger v2 §4 (§6 is OD-axis). Sibling-section audit candidate per workflow v1.10 §7.4.7.3.A — when an attribute/carrier/enum/contract surface is amended at one section, audit sibling sections for stale-carry-text. NOT patched at this batch per FM-2; future Class 3 drift refresh would close.

(c) **Meta-Arch §2.2 row 423 PRESERVED VERBATIM** per X-AL-3 + advisor Scope B framing. Meta-Arch is design declaration; ledger v2 is retirement-state tracking. Split-view pattern follows AS-9 precedent (in Meta-Arch §2.2; excluded from ledger v2 §4). Future Meta-Arch revision MAY canonicalize AS-8 decomposition if operator-discretion design-phase back-flow opens for AS-axis design extensions; out-of-scope at batch-24.

(d) **Ledger v2 §0.5 frozen-snapshot discipline preserved.** §4 AS-axis row text PRESERVED VERBATIM per forward-only ledger convention. Decomposition event documented at §11 supersession entry per §0.5 reading-order guidance.

(e) **Cumulative percentage net-flat (61.2% → 61.1%).** Decomposition is structural cardinality rebalance, not pipeline-progress. Net effect: AS-axis loses monolithic-RETIRED-bias when sub-rows expand denominator faster than numerator (3/6 sub-rows close immediately; 3/6 remain STILL-BOUNDED). Future sub-RETIRED transits (AS-8d Skills + AS-8f managed_agents) would advance the percentage; AS-8e files INDEFINITE remains carry.

(f) **Operator's "8/9" framing in AskUserQuestion Option A absorbed at §0 dual-view math.** Three counting views published: raw ledger (33/54 = 61.1%); active-substitution excluding AS-8e INDEFINITE (32/53); operator-collapsed view (8/9 = 88.9% if AS-8d + AS-8f also excluded as future-gated, leaving 9 active substitutions in AS-axis). All 3 readings empirically grounded; no silent reading-collapse.

(g) **Workspace CLAUDE.md cardinality drift candidate.** Workspace CLAUDE.md §2.5 AS axis row cites Meta-Arch counts (6 AS substitutions); does NOT track ledger v2 sub-row decomposition view. Future workspace CLAUDE.md revision MAY add ledger-vs-Meta-Arch dual-view annotation if multiple sub-row decompositions accumulate. Current single-decomposition scope at AS-8 does not yet warrant the annotation; FM-2 deferred.

(h) **Pattern catalogued — retirement-ID-scoping correction at ledger layer.** First instance in ledger history. Mechanism: monolithic substitution ID covers N independent producer sites with N distinct close gates → "all-or-nothing closure friction" → ledger-layer decomposition into N sub-rows enables per-sub-row close. Distinct from sub-species 7a/7b (gate-text-stale-vs-production at fixed scope); this is gate-text-correctly-scoped-but-aggregating-too-many-gates. Future operator-discretion: AS-8d + AS-8f advance via per-sub-row close at their respective producer-site landings; no need to wait for AS-8e Files arc to close before advancing the AS-axis pipeline.

(i) **harness-as helpers (`attach_idempotency_key_to_sandbox_event` / `derive_sub_agent_idempotency_key` / `join_cost_attribution_by_idempotency_key`) remain bounded-residual.** Carried from batch-23 §3(h); production never invokes these Pydantic-event-shape helpers. NOT relevant to AS-8 decomposition; preserved as bounded-residual per X-AL-2.

---

## §4 Filing footer

| Field | Value |
|---|---|
| Batch | 24 |
| Cumulative RETIRED (raw ledger view) | 33/54 (61.1%) |
| Cumulative RETIRED (active view, excluding AS-8e INDEFINITE) | 33/53 (62.3%) |
| Cumulative RETIRE-READY | 0/54 (bucket EMPTY) |
| Cumulative PARTIAL | 5/54 (was 6/49 — AS-8 monolithic removed; sub-rows distributed to RETIRED + STILL-BOUNDED) |
| Cumulative STILL-BOUNDED | 16/54 (was 13/49 — AS-8d + AS-8f added; AS-8e STILL-BOUNDED-INDEFINITELY) |
| Cumulative pipeline-advanced (R+RR+P) | 38/54 (70.4%) |
| New RETIRED transitions | 3 (AS-8a anthropic.* + AS-8b mcp.* + AS-8c memory.* immediate close at decomposition) |
| New decomposition events | 1 (AS-8 monolithic → 6 sub-rows at ledger-v2-layer) |
| New RETIRE-READY transitions | 0 |
| Filed as | `phase-7d-retirement-events-batch-24.md` |
| Co-published bookkeeping | `harness-as/CLAUDE.md` §4.1 (H_T-AS-5 RETIRED row refresh + H_T-AS-8 monolithic REPLACED with 6 sub-rows + cumulative summary post-batch-24); workspace `CLAUDE.md` §2.4 AS plan row batch-24 note; `.harness/phase-7d-retirement-ledger-v2.md` §11 NEW supersession entry §11.X |
| Predecessor | `phase-7d-retirement-events-batch-23.md` |
| Date | 2026-05-28 |
