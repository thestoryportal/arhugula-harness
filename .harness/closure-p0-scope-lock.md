---
title: Closure Plan — Phase 0 Scope-Lock
phase: P0 (R-CL-P0)
status: complete (scope frozen; awaiting operator ratification of the 2 filed forks)
created: 2026-06-10
grounded_at_head: 37b7c80
parent: .harness/post-mvp-full-closure-plan-v1.md
---

# Phase 0 — Ground + Scope-Lock (verified)

*Output of closure-plan Phase 0: every Cat-1..4 surface re-verified against HEAD `37b7c80` (3 parallel grounding agents + direct re-verification of the 2 highest-impact findings), the forward register's "closed" claims re-checked, and the design-gated forks filed. This freezes the authoritative work-list. The register's snapshot (compiled 2026-06-01) was confirmed stale-optimistic in two material places — both corrected below.*

## 0. Method + confidence

- 3 parallel grounding agents (routing build-vs-fork; Cat-1 + register-closed-claims; design-gated surfaces) → file:line / version:§ cites.
- Per `[[subagent-landscape-reports-need-regrounding]]`, the **2 highest-impact findings directly re-verified** by me (the sandbox-driver wiring gap; the C-CP-02 §2.1 spec shape). `[HIGH]` where re-verified; `[MODERATE]` where agent-cited only.

## 1. The two material corrections to the forward register (`[HIGH]` — re-verified)

| # | Register claimed | HEAD reality (verified) | Impact |
|---|---|---|---|
| **C-1** | B-3/B-4 sandbox tiers (R-410/411/412) **RESOLVED** — drivers "wired into `RuntimeToolDispatcher`" | The `Docker`/`GVisorRunsc`/`E2BManagedFullVM` driver classes exist + conform + pass *injected* e2e, but the **production bootstrap dispatcher never selects them**: `runtime_tool_dispatcher_factory.py:199` omits `tool_execution_driver=` → defaults to `MCPHostToolExecutionDriver` (`runtime_tool_dispatcher.py:343`). **No tier→driver selection seam** in `deployment_matrix.py`. A production TOOL_STEP cannot actually run in a Docker/gVisor/E2B sandbox. | **NEW buildable scope item** (sandbox driver→dispatch wiring). The register's "RESOLVED" was true *for the e2e*, not for production. Folded into P2. |
| **C-2** | P1/B-1 routing "Cat-1 *iff* spec'd at C-CP-02 §2.2, else design-gated" (the plan's hedge) | C-CP-02 §2.1 (`Spec_Control_Plane_v1_2.md:286-306`, preserved at v1.3) **specifies the algorithm shape + I/O contract** (k-NN-over-embedding + confidence threshold → `RoutingBinding`; router model + `call_site_context` → provider+model+rationale); `:327` defers only the **params** (embedding model, k, threshold, router prompt, router model) "to implementation discretion." ADR-F1 confirms these are "D-derivative downstream, not F-layer commitment." | **Hedge resolves to: P1 is Cat-1 pure Phase-7 impl — NO fork.** Building the EMBEDDING + LLM_AS_ROUTER decision-fn internals is authorized impl-discretion. (Fork owed ONLY if changing algorithm shape / `LAYER_ORDER` / `RoutingBinding` contract — none required.) |

## 2. Frozen work-list (per closure-plan phase)

| Surface | Cat | Verdict (verified) | Phase | Evidence |
|---|---|---|---|---|
| Routing EMBEDDING + LLM_AS_ROUTER layers | **1 (pure impl)** | Shape spec'd; params impl-discretion → **build, no fork** | P1 | `Spec_CP_v1_2.md:286-327`; `llm_dispatch.py:489` (only DECLARATIVE-echo bound) `[HIGH]` |
| C-CP-03 LayerBudget + C-CP-04 fallback chain | 1 | **Fully specified** (only timeout *values* deferred) | P1 | `Spec_CP_v1_2.md:346-454` `[MODERATE]` |
| Sandbox driver→dispatch wiring **(NEW — C-1)** | **1** | Drivers built+e2e; **production selection seam absent** | P2 | `runtime_tool_dispatcher_factory.py:199`; `runtime_tool_dispatcher.py:343` `[HIGH]` |
| Engine-recovery driver | 1 | Loop **dormant** (no production caller); PR #475 substrate unwired | P2 | `r_cxa_2_producer_loop_factory.py:208`; zero prod invocation `[HIGH]` |
| External-engine adapters (Temporal/K8s/Kafka/save-point) | **2** | Build seam + reference adapter + deterministic test; live-proof operator-gated (D-2) | P2 | engine_class.py; I-6 |
| Persona-tier TEAM_BINDING | 3→**build** | **Specified + src-branch-cased across all 4 behaviors** (HITL/redaction/sampler/cost); owed = **e2e proof, NOT fork** | P3 | `gate_level_rule.py:152`; `redaction_gradient.py:96`; `base_rate_set_and_envelope.py:141`; `cost_attribution_dashboard_binding.py:186` `[MODERATE]` |
| Prompts surface + `active_prompt_version` (3rd hash component) | **3 (fork)** | **Genuinely unspecified → fork FILED** (`class_1_fork_prompts_management_surface_active_prompt_version.md`) | P4 (blocked on fork) | `procedural_tier_snapshot.py:10-16`; `Spec_IS_v1.3:§5.2` `[HIGH]` |
| Keying-tuple ↔ entry-shape D-ADR | **3 (fork)** | **Unauthored D-ADR → fork FILED** (`class_1_fork_keying_tuple_entry_shape_d_adr.md`); §7.4 F2-12 cite stale | P4 (blocked on fork) | `Spec_IS_v1.3:§7.4`; `ADR-F2.md:63-64` `[MODERATE]` |
| OD tail-keep bounded-buffer | 1 | **Unbounded** confirmed (no trace/span cap) | P5 | `tail_keep_span_processor.py:120-123,66-70` `[HIGH]` |
| 22 CXA "phase-2-runtime" edges | 1→**mostly verify** | Composers wired at stage-6; phase-2 = *runtime-behavior, not compile-time wiring* → **no wiring task**; verify producers emit (OD-6 materialized; CP→IS-17 rest on composer running). Doc-drift: `stage_6_cxa_wiring.py:4` says "24" (stale v2.3) vs canonical 22 | P5 | `CXA_v2_19:51,119`; `stage_6_cxa_wiring.py:57-105` `[MODERATE]` |
| Cost-attribution rate tables | 2 | Chain built; bind per-provider rate/overhead coefficients (+ default table) | P5 | C-OD-17 |
| Validator-framework thresholds | 1/2 | Bind which validator at which sandbox-tier threshold | P5 | ADR-D2 §1.9 |
| Spec-prose drift (AS Files/managed-agents "deferred indefinitely") | 1 | Spec footers stale vs landed R-810/R-820 → refresh | P6 | AS C-AS-14 §14.5/§14.6 |

**Register claims re-verified CLOSED (no action):** memory backends ×4 (`memory_tool_{filesystem,sqlite,s3,managed_db}.py`); MCP host start/shutdown (`stage_3a_cp_clients.py:59` + `shutdown.py:487`, both guarded). `[HIGH]`

## 3. Cat-4 (impl-discretion — closed-at-spec, NOT pending development)

Confirmed genuinely-deferred-by-discretion (record, do not build): git commit cadence/message conventions, canonicalization library binding (RFC 8785 JCS per language), worktree/shadow-ref naming, composer caching shape (v1.30 §1.6), validator-tier *parameter* values, routing layer *param* values (model/k/threshold/prompt). These are the spec's affirmative "Phase-7-may-proceed" markers, not gates.

## 4. Forks filed (P0 gate → operator ratification owed)

1. `class_1_fork_prompts_management_surface_active_prompt_version.md` — **blocks R-CL-P4.**
2. `class_1_fork_keying_tuple_entry_shape_d_adr.md` — **blocks the §7.4 portion of R-CL-P4** (+ flags the stale §7.4 F2-12 cite for refresh).

## 5. Scope-lock exit gate

Per the plan, P0 exits when the operator **ratifies the frozen scope** (incl. the 2 forks). The capability phases split:
- **P1 / P2 / P3 / P5 / P6** are unblocked once scope is ratified (no fork dependency).
- **P4** is blocked on the 2 forks' ratification (design-before-build).

**Net change from the plan's snapshot:** routing de-hedged to pure-impl (C-2); one NEW item added (sandbox driver→dispatch wiring, C-1); P5's CXA-edge portion downgraded from "build" to "verify + doc-fix"; TEAM_BINDING confirmed build-not-fork; the 2 design forks filed.
