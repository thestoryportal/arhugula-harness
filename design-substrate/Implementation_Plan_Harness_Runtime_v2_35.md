# Implementation Plan — Harness Runtime — v2.35

*Delta over v2.34. v2.35 is a Phase 7 → design-phase Class 1 back-flow apply pass per `.harness/class_1_tension_u_rt_111_engine_layer_substrate_absence.md` Reading (A) operator-ratified 2026-05-29. Authors a narrow-scope canonical-reading amendment at U-RT-111 (v2.34 NEW unit) that DROPS ACs #4 + #5 + #6 + #10 as structurally-blocked per engine-layer absence + 3 disambiguator gaps + the X-AL-2 second-conjunct transit-unreachability finding; RETAINS ACs #1 + #2 + #3 + #7 + #9 + #11 + #12 (reframed); REFRAMES the e2e test substrate to cover only the implementable subset (3-or-4 sites depending on AC #3 verification at impl arc). H_T-RT-35 PARTIAL → RETIRE-READY transit posture reframed honestly — STAYS PARTIAL post-impl arc; the (F) FULL-WIRE-paired transit claim at v2.33 §0.3 + v2.34 §0.3 was based on the implicit assumption that engine-layer substrate was landed; the assumption is empirically false at HEAD `a2a0fc2`. RETIRE-READY transit gated on the upstream engine-layer impl arc routed separately to design-phase per `Project_Workflow_v1_12.md` §2.7.6.*

## §0 Change note (v2.34 → v2.35)

### §0.1 What changed

| Element | v2.34 | v2.35 |
|---|---|---|
| U-RT-111 unit body | 12 ACs covering 6 caller-sites + sibling-residual + scoped subset support | 8 ACs covering 4 caller-sites + sibling-residual; ACs #4/#5/#6/#10 STRUCK with canonical-reading explanation |
| §1 unit count | 109 (with U-RT-111 at 12 ACs) | 109 (with U-RT-111 at 8 ACs; canonical-reading reframe — NOT a new unit) |
| §2 DAG | U-RT-111 → U-RT-110 (1 within-axis edge); transitive cross-axis to U-CP-74..U-CP-79 | UNCHANGED — DAG edges PRESERVED VERBATIM (the rescope drops ACs, not dependency edges) |
| H_T-RT-35 transit framing | PARTIAL → RETIRE-READY eligible at v2.34 impl arc + e2e PASS | PARTIAL STAYS PARTIAL post-v2.35 impl arc; RETIRE-READY gated on upstream engine-layer impl arc (separate Class 1 back-flow owed at CP-axis design-phase routing) |
| CXA v2.16 → v2.17 transit | 6 PENDING → 6 LANDED at impl arc PR merge + retirement-batch filing | 3 PENDING → 3 LANDED at v2.35 impl arc PR merge (U-CP-74/75/77 if all 4 implementable ACs land; possibly 4 LANDED if AC #3 verifies clean); 3 PENDING carry to engine-layer impl arc (U-CP-78/79) + 1 PENDING carry to CP-axis disambiguator extension arc (U-CP-77 if blocked by `semantic_variant_binding_id` — see §0.3 below) |

### §0.2 Scope discipline

§0 (this change note); §1 U-RT-111 unit-body canonical-reading amendment + ACs reframed; §2 DAG preservation (ZERO edge changes); §3 adjacent observations + carry-forward; §4 filing footer. All v2.34 unit bodies + v2.33 + ... + v1 lineage PRESERVED VERBATIM per delta-only-plan-chain convention except the U-RT-111 unit body which is canonical-reading-amended at v2.35.

### §0.3 Authoring rationale + the empirical finding that drove the rescope

The v2.34 §0.3 (F) FULL-WIRE-paired framing claimed H_T-RT-35 PARTIAL → RETIRE-READY transit eligibility at U-RT-110 (binding-side, v2.33) + U-RT-111 (caller-side, v2.34) + e2e PASS. Pre-substantive empirical orientation at the U-RT-111 impl arc (worktree `u-rt-111-impl`, HEAD `a2a0fc2` post-PR #59 merge) verified each of the 5 risk surfaces flagged at v2.34 §1.2 ACs #8 + #9 and surfaced **7 gaps** between the plan's optimistic framing and the actual production state.

The decisive finding: **2 of the 6 caller-site target functions are `NotImplementedError` stubs** (`capture_pause_snapshot(...)` at `harness-cp/.../pause_resume_protocol.py:106`; `attempt_resume(...)` at line 128). Wiring caller-sites to never-fired paths cannot satisfy X-AL-2 second-conjunct (substituted H_E surface must no longer be invoked at the substitution site); the engine-layer `NotImplementedError` raise IS the H_E substitute being invoked. Until the upstream engine-layer impl arc lands real bodies for those stubs, H_T-RT-35 RETIRE-READY transit is structurally unreachable, regardless of how cleanly the runtime caller-site wiring is authored.

3 disambiguator gaps compound the issue at ACs #4 + #5 + #6: `RewrittenToolCall.semantic_variant_binding_id`, `PauseEvent.pause_event_id`, and `resume_attempt_count` (on either `ResumeAttempt` or `ResumeOutcome`) are NOT fields on their stated source types. Synthesizing them at runtime axis would be X-AL-3 silent design extension per the explicit halt-condition wording at v2.34 ACs #8.

Per Reading (A) operator-ratified 2026-05-29 via AskUserQuestion: rescope U-RT-111 at the planning layer rather than land partial wiring under a plan that promises transit it cannot deliver. v2.35 IS the rescope.

### §0.4 Out-of-scope at v2.35 (owed separately)

| Owed arc | Routing target | Rationale |
|---|---|---|
| CP plan v2.29 → v2.30 NEW units for engine-layer impl (U-CP-49 + U-CP-50 bodies materialized) | CP-axis design-phase routing per `Project_Workflow_v1_12.md` §2.7.6 | Engine-layer substrate is the upstream blocker for H_T-RT-35 RETIRE-READY transit; the engine-class taxonomy at ADR-D1 v1.2 §1.1.1 anchors the work; out-of-scope at runtime-axis |
| CP spec v1.26 → v1.27 amendments for 3 disambiguator field extensions | CP-axis design-phase routing OR absorbed naturally at engine-layer impl arc when fields become surfaced | `RewrittenToolCall.semantic_variant_binding_id` + `PauseEvent.pause_event_id` + `ResumeAttempt.resume_attempt_count` (or sibling) extensions; X-AL-3 forbids runtime-axis synthesis |
| CXA v2.16 → v2.17 §2.3.2 enumeration refresh — full 6 PENDING → 6 LANDED | Retirement-batch filing arc post-engine-layer-landing | At v2.35 impl arc, 3-or-4 PENDING transit (partial); remaining transit gated on engine-layer impl arc completion |
| Runtime spec §12.3 prose alignment per v2.33 (C-defer) | Next runtime-spec revision pass | UNCHANGED from v2.33 + v2.34 carry; v2.35 conforms to IS HEAD via U-RT-110's adapter encapsulation per CP spec v1.26 §16.5.8 Q4 |

---

## §1 U-RT-111 unit-body canonical-reading amendment

### §1.1 Site

PRESERVED VERBATIM from v2.34 §1.1 — U-RT-111 slots at the L7-and-later wiring-consumer layer, singleton extension of U-RT-110's stage-6 surface.

### §1.2 U-RT-111 — Body (v2.35 canonical reading)

**Implements:** CP spec v1.26 §16.5.7 firing-site discipline (the canonical "fires AFTER X resolves; BEFORE returning the result" semantic, satisfied at the immediate-caller level per (S) sibling-variant architectural commitment); CP spec v1.26 §16.5.9 invariants 1-7 (composer-side composition discipline at the caller layer); runtime spec v1.7 §12.3 17-edge enumeration (3-or-4 of 7 CP-materializable edges at this arc per the rescope; remaining 3 deferred to upstream engine-layer impl arc + 1 deferred to CP-axis disambiguator extension arc); cross-axis composition per CXA v2.16 §0.4 (3 PENDING → 3 LANDED upon v2.35 impl arc completion + e2e verification PASS; possibly 4 LANDED if AC #3 verifies clean).

**Files:**
- `harness-cp/src/harness_cp/workflow_driver.py` (EXTEND at the `resolve_step_binding(...)` immediate-caller site near line 777; existing workflow_driver body PRESERVED VERBATIM at non-firing-site lines)
- `harness-runtime/src/harness_runtime/lifecycle/override_evaluator.py` (EXTEND at the `resolve_step_binding(...)` immediate-caller site at line 61; existing body PRESERVED VERBATIM at non-firing-site lines)
- `harness-runtime/src/harness_runtime/lifecycle/engine_selector.py` (EXTEND at the `select_engine_class(...)` immediate-caller site at line 145; existing body PRESERVED VERBATIM at non-firing-site lines)
- `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py` (EXTEND at the canonical sub_agent_dispatch firing-site per spec v1.7 §14.7.2 step 8b state-ledger-entry-write; existing body PRESERVED VERBATIM at non-firing-site lines)
- *(IF AC #3 verifies clean at impl arc)* `harness-cp/src/harness_cp/workflow_driver.py` (EXTEND at the `PauseResumeProtocol` class method invocation sites — implementer-discretion at impl arc per AC #3 verification result)
- `harness-runtime/tests/test_cp_is_caller_site_integration.py` (NEW — 1 integration test per implementable caller-site = 3 unit-test variants + 1 sibling-ledger residual test + 1 scoped e2e covering the 3-or-4 implementable sites in a single workflow lifecycle + 1 negative-path test for AC #1 dual-emission discipline = 6-or-7 tests; reframed from v2.34's 10-test scope)

**Signatures introduced:** NONE at U-RT-111 (PRESERVED VERBATIM from v2.34 §1.2) — v2.35 modifies existing function bodies at 3-or-4 caller-site locations to invoke U-RT-110's methods.

**Per-caller-site invocation contract (3-or-4 invocations):**

| # | Caller site (file:line at HEAD `a2a0fc2`) | U-RT-110 method invoked | Composer args sourced at caller site | Spec authority |
|---|---|---|---|---|
| 1 | `harness-cp/src/harness_cp/workflow_driver.py:777` immediate-post-`resolve_step_binding(...)` + `harness-runtime/src/harness_runtime/lifecycle/override_evaluator.py:61` immediate-post-`resolve_step_binding(...)` | `emit_override_state_ledger_entry(workflow_id, step_id, override_id, policy_id, post_override_step_config, actor)` | `workflow_id` from `step_context.workflow_id`; `step_id` from the `step_id` arg passed to `resolve_step_binding`; `override_id` + `policy_id` from `manifest_entry.per_step_overrides[step_id]` access (the override the function applied); `post_override_step_config` derived from the returned `StepEffectiveBinding`; `actor` from `step_context.parent_actor` per CP spec v1.6 §25.2.1 (empirically verified reachable at workflow_driver_types.py:222 + workflow_driver.py:826 callsite) | CP spec v1.26 §16.5.7 row U-CP-14; v1.26 §16.5.6 dual-emission discipline |
| 2 | `harness-runtime/src/harness_runtime/lifecycle/engine_selector.py:145` immediate-post-`select_engine_class(input)` invocation (REFRAMED from v2.34 §1.2 row 2 — empirically verified at the runtime-side engine_selector module, NOT at workflow_driver bootstrap) | `emit_workload_class_selection_state_ledger_entry(workflow_id, step_id, selection_result, actor)` | `workflow_id` from engine_selector context (impl arc verifies; likely synthesized as `"workflow.init"` per recommendation 2.a — engine selection IS workflow-init-time); `step_id` synthetic `"workflow.init"` per CP-IS convention at C-IS-10 §10.1; `selection_result` from `select_engine_class(...)` return; `actor` from runtime context | CP spec v1.26 §16.5.7 row U-CP-27 |
| 3 | *(IF AC #3 verifies clean at impl arc)* workflow_driver `PauseResumeProtocol` class method invocation sites at workflow-layer transitions (firing-site verified at impl arc per existing `RunStatus.PAUSED` integration at U-RT-89) | `emit_pause_resume_state_ledger_entry(workflow_id, step_id, protocol_event_kind, event_sequence_id, protocol_state_snapshot, actor)` | `workflow_id` from workflow-driver context; `step_id` from current-step context at the protocol-transition firing point; `protocol_event_kind` from `PauseResumeProtocolEventKind` enum value matching the class method invoked; `event_sequence_id` from monotonic counter at workflow-driver scope; `protocol_state_snapshot` from the protocol-transition outcome state; `actor` from workflow context | CP spec v1.26 §16.5.7 row U-CP-30 (workflow-layer per CP spec v1.11 §26 NEW NOTE coexistence — IF the `PauseResumeProtocol` class methods themselves are implemented at HEAD; verify at impl arc; if NotImplementedError stub like the engine-layer free funcs, this AC routes to the same upstream impl arc as ACs #5/#6 from v2.34) |
| 11 (renumbered from v2.34 §1.2 AC #11) | `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py` post-sibling-composition step per spec v1.7 §14.7.2 step 8b | `emit_sibling_ledger_entry(parent_action_id, sibling_thread_id, step_index, tool, canonical_args, sibling_agent_identity, timestamp)` (the U-RT-35 LANDED synchronous method at `RuntimeCpIsWiring`; U-CP-34 residual closure) | Source args at sub_agent_dispatch firing site per spec v1.7 §14.7.2 step 8b state-ledger-entry-write semantics (impl arc verifies specific line + arg-sourcing) | CP spec v1.26 §16.5.7 (transitively via U-CP-34 LANDED at U-RT-35); v1.7 §14.7.2 step 8b |

**Depends on:** PRESERVED VERBATIM from v2.34 §1.2 — U-RT-110 (within-axis), U-RT-12 (transitive), U-CP-74..U-CP-79 (cross-axis transitive via U-RT-110), U-CP-34 (cross-axis for AC #11).

**Acceptance criteria (v2.35 reframed):**

1. **Caller-site (1) override-application — workflow_driver + override_evaluator.** PRESERVED VERBATIM from v2.34 §1.2 AC #1 — invocation at `workflow_driver.py:777` + `override_evaluator.py:61` immediate-post-`resolve_step_binding(...)`; fires ONLY if `manifest_entry.per_step_overrides.get(step_id)` was non-None at the resolve site (no-override path SHOULD NOT emit per spec §16.5.6 dual-emission discipline). v2.33 dual-emission discipline preserved: existing `emit_override_audit_entry(...)` at `per_step_override_evaluator.py:208` UNCHANGED.

2. **Caller-site (2) workload-class-selection @ engine_selector.py:145 (REFRAMED).** At `engine_selector.py:145` immediate-post-`select_engine_class(input)`: invoke `emit_workload_class_selection_state_ledger_entry(...)` with `step_id="workflow.init"` synthetic identifier per CP-IS convention at C-IS-10 §10.1 (engine selection IS workflow-init-time). `workflow_id` synthesized at impl arc per engine_selector context — implementation-discretion. v2.34 §1.2 AC #2 mentioned workflow_driver bootstrap as the site; empirical orientation found the actual site at `harness-runtime/.../lifecycle/engine_selector.py:145` — v2.35 reframe locks in the empirically-verified location.

3. **Caller-site (3) pause-resume workflow-layer (CONDITIONAL).** PRESERVED VERBATIM from v2.34 §1.2 AC #3 at the canonical-reading layer EXCEPT: implementation conditional on impl-arc verification that `PauseResumeProtocol` class methods are implemented at HEAD (NOT NotImplementedError stubs like the engine-layer free functions at `pause_resume_protocol.py:106 + 128`). If the class methods are stubs too, this AC routes to the same upstream impl arc as the v2.34-STRUCK ACs #5/#6 and is filed as a sibling Class 1 fork (NOT absorbed at v2.35 silently). If class methods are implemented, AC proceeds per the v2.34 AC #3 details.

4. ~~**Caller-site (4) HITL-tool-call-rewriting.**~~ **STRUCK at v2.35** per fork doc §2 row #4: `RewrittenToolCall.semantic_variant_binding_id` is NOT a field on the class at HEAD; synthesizing at runtime axis would be X-AL-3 silent design extension; routes to CP-axis disambiguator-extension arc (out-of-scope per §0.4).

5. ~~**Caller-site (5) pause-captured engine-layer.**~~ **STRUCK at v2.35** per fork doc §2 row #5: `capture_pause_snapshot(...)` is NotImplementedError stub; `pause_resume_composer.py` does NOT exist; `PauseEvent.pause_event_id` is NOT a field; `PauseEvent` vs `PauseSnapshot` type mismatch. Composite 4-gap blocker. Routes to upstream engine-layer impl arc (out-of-scope per §0.4).

6. ~~**Caller-site (6) resume-attempted engine-layer.**~~ **STRUCK at v2.35** per fork doc §2 row #6: `attempt_resume(...)` is NotImplementedError stub; `pause_resume_composer.py` does NOT exist; `resume_attempt_count` is NOT a field on `ResumeAttempt` or `ResumeOutcome`. Composite 3-gap blocker. Routes to upstream engine-layer impl arc (out-of-scope per §0.4).

7. **CP-axis production functions PRESERVED VERBATIM.** PRESERVED VERBATIM from v2.34 §1.2 AC #7 — ZERO modification to any CP-axis function signature; ZERO return-type widening at CP-axis.

8. ~~**Disambiguator-availability halt.**~~ **STRUCK at v2.35** — the halt fired correctly at the impl-arc empirical orientation; ACs #4/#5/#6 (the AC #8-flagged surfaces) are now STRUCK from v2.35 scope. AC #8 served its purpose at v2.34 + v2.35 transition; preservation at v2.35 would be redundant guard against ACs that no longer exist at v2.35.

9. **Actor-source verification.** PRESERVED VERBATIM from v2.34 §1.2 AC #9 — `step_context.parent_actor` empirically verified at `workflow_driver_types.py:222` field declaration + `workflow_driver.py:826` callsite reachable at all step-execution-time sites (ACs #1, #2, #3).

10. ~~**6-site full chain e2e.**~~ **STRUCK + REFRAMED at v2.35** — the v2.34 AC #10 6-site e2e is structurally blocked (depends on STRUCK ACs #5/#6). REFRAMED at v2.35: `harness-runtime/tests/test_cp_is_caller_site_integration.py` exercises 3-or-4 implementable caller-site invocations (override + workload-class-selection + sibling-ledger + possibly pause-resume workflow-layer if AC #3 verifies clean) within a single end-to-end workflow lifecycle. Assert: persisted ledger contains entries with `action_id ∈ {cp.per-step-override-application, cp.workload-binding-class-selection, cp.pause-resume-protocol (IF #3), cp-sibling-ledger-entry-action-id}` (the v2.35 implementable subset; NOT the v2.34 full-6-set); `chain_verification` per C-IS-06 §6 passes for the multi-entry chain.

11. **U-CP-34 LANDED-but-never-fired residual closure.** PRESERVED VERBATIM from v2.34 §1.2 AC #11 — sub_agent_dispatch firing-site insertion of `emit_sibling_ledger_entry(...)` at `sub_agent_dispatch.py` post-sibling-composition step per spec v1.7 §14.7.2 step 8b.

12. **H_T-RT-35 transit posture REFRAMED at v2.35.** v2.34 AC #12 ("NO retirement event filing at v2.34 publication") and the implied "transit eligible at v2.34 impl arc completion + e2e PASS" REFRAMED at v2.35: H_T-RT-35 STAYS PARTIAL post-v2.35 impl arc. NO retirement-event filing at v2.35 impl arc per X-AL-2 second-conjunct unreachability finding at fork doc §3 — until the upstream engine-layer impl arc lands real bodies for `capture_pause_snapshot(...)` + `attempt_resume(...)` AND the CP-axis disambiguator-extension arc lands `RewrittenToolCall.semantic_variant_binding_id` (or equivalent), the substituted H_E surface (the NotImplementedError stubs + the synthesized-disambiguator gap) IS still invoked at the substitution site. Wiring 3-or-4 caller-sites cleanly cannot satisfy X-AL-2 by itself.

**Tests (v2.35 reframed):** `test_caller_site_override_emission_workflow_driver`; `test_caller_site_override_emission_override_evaluator`; `test_caller_site_workload_class_selection_emission_engine_selector` (renamed from v2.34's `_caller_site_workload_class_selection_emission` per the §1.2 row 2 reframe); `test_caller_site_pause_resume_workflow_layer_emission` (CONDITIONAL on AC #3 verification); `test_no_override_path_does_not_emit_state_ledger_entry` (AC #1 dual-emission discipline negative-path); `test_sibling_ledger_entry_emission_at_sub_agent_dispatch` (AC #11 U-CP-34 residual closure); `test_three_or_four_caller_sites_full_chain_verification_passes_e2e` (REFRAMED from v2.34's `_six_caller_sites_*` — scope reflects the implementable subset).

**Rollback boundary:** Single coherent change at the rescope; revertible as single PR / commit family. Reverting v2.35 impl arc DOES NOT regress v2.33's U-RT-110 binding-side (PRESERVED at HEAD) NOR v2.34's plan-side authoring (which is pure design-substrate authoring with ZERO production code impact). v2.35 revert returns the runtime axis to U-RT-110 LANDED-but-implementable-caller-sites-unwired posture.

---

## §2 DAG delta

ZERO DAG edge changes at v2.35. The rescope drops ACs (acceptance criteria) at U-RT-111; it does NOT drop the unit itself, the unit's dependency edges, or its position in the topological sort. v2.34 §2 DAG declarations PRESERVED VERBATIM.

Unit count: 109 (UNCHANGED from v2.34).

---

## §3 Adjacent observations + carry-forward

(a) **CP plan v2.29 → v2.30 NEW units for engine-layer impl OWED at separate design-phase routing.** Per fork doc §4 Reading A out-of-scope clause + §0.4 of this v2.35 change-note: the upstream engine-layer impl arc (U-CP-49 + U-CP-50 unit bodies materialized at CP-axis against real engine substrate per ADR-D1 v1.2 §1.1.1) is the dominant blocker for H_T-RT-35 RETIRE-READY transit. Routes separately per `Project_Workflow_v1_12.md` §2.7.6 to CP-axis design-phase. NOT authored at v2.35 (out-of-axis).

(b) **CP spec v1.26 → v1.27 disambiguator-field amendments OWED at separate arc.** 3 disambiguator fields (`RewrittenToolCall.semantic_variant_binding_id` + `PauseEvent.pause_event_id` + `resume_attempt_count` on `ResumeAttempt` or `ResumeOutcome`) require either (a) direct CP spec extension at v1.27 OR (b) absorption at the engine-layer impl arc when the fields become naturally surfaced. Implementer-discretion at the upstream arcs. NOT authored at v2.35 (out-of-axis).

(c) **CXA v2.16 §0.4 forward-tracking partial transit at v2.35 impl arc.** 3 PENDING → 3 LANDED at v2.35 impl arc PR merge for U-CP-74 (override) + U-CP-75 (workload-class-selection) + U-CP-34 (sibling-ledger residual — wait, this isn't a §16.5 row; let me check — U-CP-34 is NOT in CXA v2.16 §0.4 tracker per the §16.5 6-row focus. So the CXA tracker transit is 2 PENDING → 2 LANDED at v2.35 for U-CP-74 + U-CP-75; possibly 3 PENDING → 3 LANDED if AC #3 verifies clean and U-CP-76 caller-site lands too). Remaining 3-or-4 PENDING carry to upstream engine-layer impl arc (U-CP-78 + U-CP-79 always; U-CP-77 if disambiguator extension arc lands its CP-axis prerequisite; U-CP-76 if AC #3 verification routes to engine-layer impl arc instead of clean-at-v2.35).

(d) **H_T-RT-35 batch-filing precedent NOT applicable at v2.35.** Per fork doc §3 X-AL-2 second-conjunct unreachability finding: the `[[h-t-cp-19-default-gate-level-spec-extension]]` batch-filing pattern precedent at v2.34 §3 (d) was based on the implicit assumption that the upstream engine-layer substrate was landed. The assumption is empirically false at HEAD. The retirement-batch filing is owed at a future arc when BOTH (a) v2.35 impl arc + (b) upstream engine-layer impl arc + (c) CP-axis disambiguator extension arc all land (3-arc convergence; sequencing TBD at upstream arc closures).

(e) **U-CP-34 LANDED-but-never-fired residual closes at v2.35 impl arc per AC #11 (PRESERVED).** PRESERVED VERBATIM from v2.34 §3 (e) — sub_agent_dispatch firing-site insertion closes the U-RT-35 PARTIAL-LAND residual. U-CP-34 residual closure is INDEPENDENT of the §16.5 6-row engine-layer + disambiguator blockers — completes within v2.35 scope.

(f) **Workspace `CLAUDE.md` §2.4 runtime plan row bump owed.** Runtime plan row v2.34 → v2.35 at workspace root `CLAUDE.md` §2.4. Co-publication this arc. Unit count: 109 (UNCHANGED).

(g) **`harness-runtime/CLAUDE.md` plan-unit anchor refresh owed at impl arc.** Per-axis `harness-runtime/CLAUDE.md` plan-unit anchors may carry "U-RT-111 v2.35 narrow-scope rescope" entry per the established per-axis-CLAUDE.md plan-anchor discipline; specific row shape per `harness-runtime/CLAUDE.md` §4.1 conventions at the impl arc PR.

(h) **PR-shape recommendation.** v2.35 plan-revision arc lands at a single PR (design-phase posture per CLAUDE.md §11; X-AL-3 CI guard at PR #48 satisfied via back-flow doc inclusion at same PR — the fork doc at `.harness/class_1_tension_u_rt_111_engine_layer_substrate_absence.md` IS the back-flow record). PR title shape: `plan: runtime v2.34 → v2.35 narrow-scope rescope at U-RT-111 (engine-layer absence + X-AL-2 unreachability)`. Branching: off main post-PR #59 merge. Impl arc PR (separate from this v2.35 plan-revision PR) lands at L9-septdecies single-unit cluster shape per v2.34 §3 (h) precedent (now reframed at v2.35).

(i) **38th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]`.** Pre-substantive advisor consultation at v2.35 authoring caught the X-AL-2 second-conjunct unreachability finding which I would not have surfaced absent the call. The advisor identified the engine-layer NotImplementedError stubs as the dominant structural blocker — sharper framing than the disambiguator-gap framing I initially drafted. Memory posture continues to validate operationally; the advisor-pre-substantive + empirical-orientation pair at v2.35 authoring is the workspace-canonical discipline for plan-revision arcs surfacing impl-time grounding gaps.

(j) **Sub-species candidate at workflow doc §7.4.7.2: plan-revision-against-not-yet-built-substrate.** v2.34 §0.3 + v2.33 §0.3 (F) FULL-WIRE-paired framing implicitly assumed engine-layer substrate was LANDED because the framing cited CP plan U-CP-49/U-CP-50 as having LANDED units (PRs #43/#44). The PRs landed the §16.5 *composer* free functions, NOT the engine-layer *substrate* free functions at the same module — distinct closure events conflated at the plan-authoring time. Catalogue candidate at workflow doc revision pass.

(k) **Plan-revision discipline preserved at v2.35.** v2.35 cites CP spec v1.26 §16.5.7 + §16.5.9 (UNCHANGED from v2.34) at the spec-traceability surface; does NOT invent any commitment absent from the cited specs; does NOT amend any cited spec; does NOT widen any CP-axis function signature or return type; preserves all dependency edges; coverage matrix at runtime-axis aggregate UNCHANGED (canonical-reading rescope, NOT coverage extension). Per implementation-planner §4 four-sub-discipline checklist: atomicity ✓ (narrow-scope rescope at U-RT-111 ACs); spec-traceability ✓ (cites CP spec v1.26 §16.5 + the fork doc as authority); dependency-awareness ✓ (preserved edges; flagged upstream blockers as out-of-scope); implementation-grade-detail ✓ (per-AC strikethrough rationale + reframed AC body text per fork doc findings).

---

## §4 Filing footer

| Field | Value |
|---|---|
| Plan version | v2.35 |
| Predecessor | v2.34 (runtime plan v2.33 → v2.34 NEW U-RT-111 caller-site invocation unit; PRs #53 → #58) |
| Successor consumption | U-RT-111 v2.35-scope implementation arc (3-or-4 caller-site invocations + sibling-ledger residual + scoped e2e) — branches off main post-PR-N merge |
| Cross-axis cascade | ZERO at v2.35 (per §0.3 + §0.4). 1 within-axis dependency edge UNCHANGED (U-RT-111 → U-RT-110). 6 cross-axis citations PRESERVED transitively via U-RT-110. CXA v2.17 §2.3.2 enumeration refresh partial (2-or-3 of 6 LANDED at v2.35 impl arc; remainder gated on upstream arcs). |
| Authority anchors | `.harness/class_1_tension_u_rt_111_engine_layer_substrate_absence.md` (operator-ratified Reading A 2026-05-29); `Phase_7_Meta_Architecture_v1.md` §7.7 X-AL-2 + X-AL-3; `Project_Workflow_v1_12.md` §2.7.6 Class 1 back-flow; CP spec v1.26 §16.5; CP spec v1.11 §26 NEW NOTE; runtime spec v1.7 §12.3; runtime plan v2.34 §1.2 ACs #8 + #9 halt-condition wording |
| Co-publications | Fork doc filed at same PR; workspace `CLAUDE.md` §2.4 row bump (v2.34 → v2.35; unit count 109 UNCHANGED); closure-back-reference annotation at runtime plan v2.34 §0.3 owed at the impl arc PR (or this same PR per operator discretion) |
| Date | 2026-05-29 |
