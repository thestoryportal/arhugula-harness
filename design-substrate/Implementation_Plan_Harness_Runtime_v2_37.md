# Implementation Plan — Harness Runtime — v2.37

*Delta over v2.36. v2.37 is a Phase 7 → design-phase Class 1 sequel-rescope per `.harness/class_1_tension_u_rt_111_engine_layer_substrate_absence.md` §10 NEW (operator-ratified 2026-05-29 same-calendar-day sequel to v2.36). v2.35 STRUCK ACs #4/#5/#6/#10 at HITL + engine-layer disambiguator gaps; v2.36 STRUCK AC #1 at the `StepOverride` field-set / U-CP-14 disambiguator gap; v2.37 STRIKES AC #11 at a **third structural shape — primitive-scope mismatch between firing site and CP spec C-CP-15 §15.1 binding**. The U-CP-34 `emit_sibling_ledger_entry` primitive is canonically bound at CP spec §15.1 to **per-sibling tool-call events inside child agent execution** (test fixture conformant: `tool="Bash"`, `canonical_args='{"cmd":"echo hi"}'`); v2.34/v2.35/v2.36 §1.2 row 11 wires it at the parent sub-agent dispatch site (`sub_agent_dispatch.py:716` post-step-8 success). The `tool` + `canonical_args` slots have no spec-anchored value at the dispatch site (the brief's hash IS the F2 `response_hash` at step 8b, not §15.1's "canonical args"). Synthesizing the convention at runtime axis under spec-silence is X-AL-3 silent design extension — same closure-event-class as v2.35 AC #4 + v2.36 AC #1 STRIKES (`[[plan-revision-against-not-yet-built-substrate]]` sub-species at workflow doc §7.4.7.2). RETAINS ACs #2 + #3 + #7 + #9 + #10 (v2.37 reframed) + #12; REFRAMES AC #10 e2e from v2.36's 3 sites to v2.37's 2 sites; H_T-RT-35 transit posture PRESERVED at PARTIAL post-v2.37 impl arc per v2.35/v2.36 §1.2 AC #12 framing.*

## §0 Change note (v2.36 → v2.37)

### §0.1 What changed

| Element | v2.36 | v2.37 |
|---|---|---|
| U-RT-111 unit body | 7 ACs (12 declared with 5 STRUCK at v2.36 — v2.35's 4 + v2.36's #1) covering 3 caller-site invocation surfaces | 6 ACs (12 declared with 6 STRUCK total — v2.35's 4 + v2.36's #1 + v2.37's #11) covering 2 caller-site invocation surfaces |
| AC #11 (sibling-ledger emission @ sub_agent_dispatch.py:716 post-step-8 success path) | RETAINED at v2.36 (PRESERVED VERBATIM from v2.34/v2.35); "Source args at sub_agent_dispatch step 8 success-path site per spec v1.7 §14.7.2 step 8b state-ledger-entry-write semantics" | **STRUCK at v2.37** per fork doc §10 NEW gap finding — CP spec v1.2 §15.1 binds `emit_sibling_ledger_entry` to **per-sibling tool calls inside child agent execution**, NOT to parent dispatch-completion. Test fixture at `harness-runtime/tests/test_lifecycle_cp_is_wiring.py:106-123` exercises the §15.1 canonical use (`tool="Bash"`, `canonical_args='{"cmd":"echo hi"}'`). At the parent dispatch site, the `tool` + `canonical_args` slots have no spec-anchored value (the brief's hash IS the F2 `response_hash` at step 8b, not §15.1's "canonical args"); synthesizing the convention at runtime axis under spec-silence is X-AL-3 silent design extension. Routes to CP-axis design-phase per `.harness/class_1_tension_u_rt_111_engine_layer_substrate_absence.md` §10 (NEW sequel item) |
| AC #10 (reframed e2e) | 3 caller-sites (workload-class-selection + pause-resume workflow-layer + sibling-ledger) | **2 caller-sites** (workload-class-selection + pause-resume workflow-layer) |
| §1 unit count | 109 (UNCHANGED) | 109 (UNCHANGED — canonical-reading sequel-rescope, NOT a new unit) |
| §2 DAG | UNCHANGED | UNCHANGED |
| H_T-RT-35 transit framing | STAYS PARTIAL post-v2.36 impl arc per AC #12 reframe (3 upstream-arc blockers) | UNCHANGED — STAYS PARTIAL post-v2.37 impl arc. **4 upstream-arc blockers** now: engine-layer impl + HITL disambiguator + override disambiguator + **NEW: sibling-ledger firing-site canonical-reading clarification or alternate-site spec amendment** |
| CXA v2.16 → v2.17 transit | 2 PENDING → LANDED at v2.36 impl arc (U-CP-75 workload-class-selection + U-CP-76 pause-resume workflow-layer); U-CP-34 LANDED-but-never-fired residual closes at AC #11 | **1 PENDING → LANDED at v2.37 impl arc** (U-CP-75 + U-CP-76 — UNCHANGED, both still LANDED at this arc; aggregate count expressed as "2 PENDING → 2 LANDED" UNCHANGED from v2.36 since U-CP-34 was already LANDED at U-RT-35, not a CXA §0.4 PENDING row). **U-CP-34 LANDED-but-never-fired residual NOT closed at v2.37** — carries to upstream sibling-ledger firing-site arc. AC #11 STRIKE explicitly removes the residual-closure claim |

### §0.2 Scope discipline

§0 (this change note); §1 U-RT-111 unit-body canonical-reading amendment STRIKING AC #11; §2 DAG preservation (ZERO edge changes); §3 adjacent observations + carry-forward; §4 filing footer. All v2.36 + v2.35 + v2.34 + ... + v1 lineage PRESERVED VERBATIM per delta-only-plan-chain convention except the U-RT-111 AC #11 entry which is STRUCK at v2.37 + the AC #10 e2e site enumeration which is narrowed from 3 to 2 + the §3 (c) CXA transit count which is refreshed (U-CP-34 residual line) + the §3 (e) U-CP-34 residual closure framing which is REVERSED.

### §0.3 Authoring rationale + the v2.37 empirical finding

v2.36 §0.3 documented the empirical orientation finding at AC #1 (U-CP-14 composer requires `override_id` + `policy_id` not present on `StepOverride`). At the v2.37 impl arc empirical orientation pass (worktree `u-rt-111-impl-v2-35`, PR #61 head `9cca6d6` post-v2.36 Phase 1 plumbing landing), the AC #11 caller-site investigation surfaced a **third structural disambiguator gap** that v2.34/v2.35/v2.36 all missed at authoring time:

The U-CP-34 composer `emit_sibling_ledger_entry` at `harness-runtime/src/harness_runtime/lifecycle/cp_is_wiring.py:112-145` declares the signature (7 kw-only args):

```
def emit_sibling_ledger_entry(
    *,
    parent_action_id: str,
    sibling_thread_id: str,
    step_index: int,
    tool: str,                       # ← what tool name at dispatch site?
    canonical_args: str,             # ← what canonical args at dispatch site?
    sibling_agent_identity: ActorIdentity,
    timestamp: datetime,
) -> WriteResult:
```

CP spec v1.2 §15.1 (preserved through v1.26 delta-only chain) declares the canonical binding:

> Per-sibling **tool calls** produce ledger entries keyed on the sibling's `thread_id` and honoring F2's six-field entry shape:
>
> ```
> sibling_ledger_entry = (
>     action_id           : ParentActionID || sibling_thread_id || step_index,
>     idempotency_key     : sha256(parent_action_id, sibling_thread_id, step_index,
>                                   tool, canonical_args)
>     actor               : sibling_agent_identity,
>     response_hash       : sha256(canonicalize(tool_output)),
>     ...
> )
> ```

Three convergent evidence vectors confirm the primitive scope is **per-sibling tool-call events inside child execution**, NOT parent dispatch-site emission:

1. **Spec text.** §15.1 reads "Per-sibling **tool calls** produce ledger entries"; `response_hash = sha256(canonicalize(tool_output))` — there is no "tool_output" at the parent dispatch moment (the child has just started or completed its run; the brief was the INPUT, not the output).
2. **Test fixture (only canonical usage at HEAD).** `harness-runtime/tests/test_lifecycle_cp_is_wiring.py:106-123` `_sibling_kwargs(...)` defaults: `tool="Bash"`, `canonical_args='{"cmd":"echo hi"}'`, `sibling_agent_identity=ActorIdentity("agent-1")`. The fixture exercises the §15.1 canonical use (a sibling agent invoking the Bash tool with a command).
3. **Zero non-test callers** (grep at HEAD `9cca6d6` across all `harness-*/src/`). The "U-CP-34 LANDED-but-never-fired residual" framing at v2.34/v2.35/v2.36 §3 (e) presupposes that the dispatch-site IS the residual-closure firing point; the spec-vs-fixture audit REVERSES this presupposition.

At the parent dispatch site (`sub_agent_dispatch.py:716` post-step-8 success), the `tool` + `canonical_args` slots have no spec-anchored value:
- The "tool" being invoked is the sub-agent dispatch operation itself; the action_id pattern at step 8b uses prefix `dispatch:` (per spec §14.7.2 step 8b), but §15.1's `tool` field maps to a TOOL NAME (Bash, Read, etc.), not an operation pattern.
- The `canonical_args` would map to "the brief contents" — but the brief's hash (`brief_hash` at line 453) is ALREADY consumed as the F2 `response_hash` at step 8b, not as §15.1's `canonical_args`. Re-purposing it would conflate two distinct hash-roles in the per-sibling shape.

The v2.34 plan row 11 wrote "Source args at sub_agent_dispatch step 8 success-path site per spec v1.7 §14.7.2 step 8b state-ledger-entry-write semantics" — but spec §14.7.2 step 8b is about the F2 dispatch-entry write contract, NOT the per-sibling tool-call ledger entry contract. The row conflates two distinct ledger-write surfaces at adjacent spec sections.

CP spec v1.26 §16.5 (the v1.25 NEW state-ledger composer contract) does NOT include U-CP-34 — §16.5.7 enumerates rows U-CP-27 / U-CP-30 / U-CP-37 / U-CP-49 / U-CP-50 / U-CP-14 (6 composers, all greenfield); U-CP-34's `sibling_ledger_entry_composition` predates §16.5 and remains anchored at C-CP-15 §15.1 with the test-fixture-conformant canonical scope. Synthesizing a parent-dispatch-site convention at runtime axis under spec-silence is X-AL-3 silent design extension per `Phase_7_Meta_Architecture_v1.md` §7.7 — structurally identical to v2.35's AC #4 + v2.36's AC #1 STRIKE rationales.

Per `[[advisor-before-substantive-work-for-cross-axis-blockers]]` 39th application at v2.37 authoring: advisor flagged the `canonical_args` source-derivation as load-bearing pre-substantive ("brief_hash is convenient not principled") + recommended single operator AskUserQuestion if zero callers exist for the dispatch-site convention. Grep returned zero non-test callers; spec audit revealed primitive-scope mismatch. Operator ratified Reading (A) sequel-strike via AskUserQuestion 2026-05-29 (option 1 — STRIKE AC #11 + amend to v2.37; file gap finding at existing fork doc §10 NEW + bundle as same-PR back-flow).

### §0.4 Out-of-scope at v2.37 (owed separately, extending v2.36 §0.4)

| Owed arc | Routing target | Rationale |
|---|---|---|
| **NEW at v2.37:** CP spec v1.26 → v1.27 canonical-reading amendment clarifying U-CP-34 `emit_sibling_ledger_entry` firing-site scope (per-sibling tool-call inside child execution vs. parent dispatch-completion), OR alternate-site spec amendment authoring a NEW firing site if dispatch-side emission is desired with disambiguator-bearing slots | CP-axis design-phase routing per `Project_Workflow_v1_12.md` §2.7.6 | Pre-v2.37 spec §15.1 is unambiguous on per-sibling-tool-call binding; plan v2.34 row 11 conflated with §14.7.2 step 8b dispatch-entry contract. Options at upstream arc: (a) canonical-reading amendment confirming §15.1 scope + plan-side reframe of AC #11 to fire INSIDE child execution at tool-invocation sites (much larger arc — needs child-side hook plumbing in `child_workflow_runner` Protocol + per-tool-call interception in workflow_driver's STEP_TYPE dispatch); OR (b) NEW spec primitive `emit_dispatch_ledger_entry` or similar for parent-dispatch-site emission with brief-derived disambiguators; OR (c) operator decision that U-CP-34 emission is fan-out-arc-deferred and the dispatch-site emission is NOT required at v1.6 MVP single-sub-agent scope. Operator-discretion at upstream arc. |
| CP plan v2.29 → v2.30 NEW units for engine-layer impl | CP-axis design-phase routing | UNCHANGED carry from v2.36 §0.4 |
| CP spec v1.26 → v1.27 amendments for HITL + override + engine-layer disambiguator fields | CP-axis design-phase routing OR engine-layer impl arc absorption | UNCHANGED carry from v2.36 §0.4 |
| CXA v2.16 → v2.17 §2.3.2 enumeration refresh — full 6 PENDING → 6 LANDED | Retirement-batch filing arc post-engine-layer-landing | v2.37 lands 2-of-6 PENDING (U-CP-75 + U-CP-76 — UNCHANGED from v2.36); 4-of-6 carry to upstream arcs (UNCHANGED) |
| Runtime spec §12.3 prose alignment per v2.33 (C-defer) | Next runtime-spec revision pass | UNCHANGED carry |

---

## §1 U-RT-111 unit-body canonical-reading amendment (v2.37)

### §1.1 Site

PRESERVED VERBATIM from v2.36 §1.1 — U-RT-111 slots at the L7-and-later wiring-consumer layer, singleton extension of U-RT-110's stage-6 surface.

### §1.2 U-RT-111 — Body (v2.37 canonical reading)

**Implements:** UNCHANGED structurally from v2.36 §1.2 (CP spec v1.26 §16.5.7 firing-site discipline for the 2 retained caller-sites; CP spec v1.26 §16.5.9 invariants 1-7; runtime spec v1.7 §12.3 17-edge enumeration — **2 of 7 CP-materializable edges at this arc** UNCHANGED from v2.36; cross-axis composition per CXA v2.16 §0.4 — 2 PENDING → 2 LANDED upon v2.37 impl arc completion + e2e verification PASS UNCHANGED).

**Files (v2.37 narrowed from v2.36):**
- `harness-runtime/src/harness_runtime/lifecycle/engine_selector.py` (EXTEND at the `select_engine_class(...)` immediate-caller site at line 145; existing body PRESERVED VERBATIM at non-firing-site lines)
- `harness-cp/src/harness_cp/workflow_driver.py` (EXTEND at 3 `PauseResumeProtocol` class method invocation sites — line 546 RESUME_ATTEMPTED + line 756 PAUSE_CAPTURED drain-flag path + line 881 PAUSE_CAPTURED HITL-signal path; existing body PRESERVED VERBATIM at non-firing-site lines)
- ~~`harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py` (EXTEND at the canonical sub_agent_dispatch step 8 post-audit-composition site per spec v1.7 §14.7.2 step 8b state-ledger-entry-write)~~ — **REMOVED at v2.37** per AC #11 STRIKE
- `harness-runtime/tests/test_cp_is_caller_site_integration.py` (NEW — 2 per-caller-site unit tests + 1 scoped e2e covering the 2 implementable sites in a single workflow lifecycle + 1 negative-path test (no-binding short-circuit) = **4 tests; reframed from v2.36's 6 to fixed 4**)

**Signatures introduced:** NONE at U-RT-111 (UNCHANGED from v2.36 §1.2) — v2.37 modifies existing function bodies at 2 caller-site locations to invoke U-RT-110's methods.

**Per-caller-site invocation contract (2 invocations at v2.37):**

| # | Caller site (file:line at HEAD `9cca6d6`) | U-RT-110 method invoked | Composer args sourced at caller site | Spec authority |
|---|---|---|---|---|
| 1 | ~~`harness-cp/src/harness_cp/workflow_driver.py:777` + `override_evaluator.py:61`~~ — **STRUCK at v2.36** | ~~`emit_override_state_ledger_entry`~~ | ~~per v2.35 §1.2 row 1~~ | Routes to CP-axis disambiguator-extension arc per fork §9 |
| 2 | `harness-runtime/src/harness_runtime/lifecycle/engine_selector.py:145` immediate-post-`select_engine_class(input)` invocation (PRESERVED VERBATIM from v2.36 §1.2 row 2) | `emit_workload_class_selection_state_ledger_entry(workflow_id, step_id, selection_result, actor)` | `workflow_id` synthesized as `f"workflow.init:{input.workload_class.value}"` per CP-IS convention at C-IS-10 §10.1; `step_id` synthetic `"workflow.init"`; `selection_result` from `select_engine_class(...)` return; `actor` from runtime context (impl-discretion at engine_selector scope) | CP spec v1.26 §16.5.7 row U-CP-27 |
| 3 | `harness-cp/src/harness_cp/workflow_driver.py:546` post-`protocol.attempt_resume(...)` + `:756` post-`protocol.capture_pause_snapshot(...)` drain-flag path + `:881` post-`protocol.capture_pause_snapshot(...)` HITL-signal path (PRESERVED VERBATIM from v2.36 §1.2 row 3) | `emit_pause_resume_state_ledger_entry(workflow_id, step_id, protocol_event_kind, event_sequence_id, protocol_state_snapshot, actor)` | per v2.36 §1.2 row 3 detail | CP spec v1.26 §16.5.7 row U-CP-30 (workflow-layer per CP spec v1.11 §26 NEW NOTE coexistence) |
| 11 | ~~`harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py` post-step-8 audit-composition success path~~ — **STRUCK at v2.37** | ~~`emit_sibling_ledger_entry(parent_action_id, sibling_thread_id, step_index, tool, canonical_args, sibling_agent_identity, timestamp)`~~ | ~~Source args at sub_agent_dispatch step 8 success-path site per spec v1.7 §14.7.2 step 8b state-ledger-entry-write semantics~~ — empirically blocked at fork §10: CP spec v1.2 §15.1 binds the primitive to per-sibling tool-call events, NOT parent dispatch-completion; `tool` + `canonical_args` slots have no spec-anchored value at the dispatch site | Routes to CP-axis canonical-reading or alternate-site spec amendment arc per fork §10 |

**Depends on:** PRESERVED VERBATIM structurally from v2.36 §1.2 — U-RT-110 (within-axis), U-RT-12 (transitive), U-CP-74..U-CP-79 (cross-axis transitive via U-RT-110). **U-CP-34 cross-axis edge for AC #11 NO LONGER consumed at v2.37 impl arc** (AC #11 STRUCK); edge declaration carries to upstream sibling-ledger firing-site arc.

**Acceptance criteria (v2.37 reframed from v2.36):**

1. ~~**Caller-site (1) override-application.**~~ **STRUCK at v2.36** (preserved at v2.37).

2. **Caller-site (2) workload-class-selection @ engine_selector.py:145.** PRESERVED VERBATIM from v2.36 §1.2 AC #2.

3. **Caller-site (3) pause-resume workflow-layer (VERIFIED CLEAN at v2.36).** PRESERVED VERBATIM from v2.36 §1.2 AC #3.

4-6. ~~**Caller-site (4)/(5)/(6).**~~ **STRUCK at v2.35** (preserved verbatim).

7. **CP-axis production functions PRESERVED VERBATIM.** PRESERVED VERBATIM from v2.36 §1.2 AC #7 — ZERO modification to any CP-axis function signature; ZERO return-type widening at CP-axis. v2.37: the 2 sites at `workflow_driver.py:546+756+881` extend the SURROUNDING function bodies with the NEW emission invocations; the `PauseResumeProtocol` class method signatures PRESERVED VERBATIM.

8. ~~**Disambiguator-availability halt.**~~ **STRUCK at v2.35** (preserved).

9. **Actor-source verification.** PRESERVED VERBATIM from v2.36 §1.2 AC #9.

10. **2-site full chain e2e (REFRAMED from v2.36's 3 to v2.37's 2).** `harness-runtime/tests/test_cp_is_caller_site_integration.py` exercises 2 caller-site invocations (workload-class-selection + pause-resume workflow-layer) within a single end-to-end workflow lifecycle. Assert: persisted ledger contains entries with `action_id ∈ {cp.workload-binding-class-selection, cp.pause-resume-protocol}` (the v2.37 implementable subset); `chain_verification` per C-IS-06 §6 passes for the multi-entry chain.

11. ~~**U-CP-34 LANDED-but-never-fired residual closure.**~~ **STRUCK at v2.37** per fork doc §10 NEW gap finding: CP spec v1.2 §15.1 binds `emit_sibling_ledger_entry` to per-sibling tool-call events inside child agent execution (test fixture conformant: `tool="Bash"`, `canonical_args='{"cmd":"echo hi"}'`); the parent dispatch site has no spec-anchored mapping for the `tool` + `canonical_args` slots. Synthesizing the convention at runtime axis under spec-silence would be X-AL-3 silent design extension. The U-CP-34 LANDED-but-never-fired residual carries to upstream sibling-ledger firing-site arc per §0.4 NEW row.

12. **H_T-RT-35 transit posture PRESERVED at v2.37.** v2.36 AC #12 PRESERVED VERBATIM — H_T-RT-35 STAYS PARTIAL post-v2.37 impl arc. NO retirement-event filing at v2.37 impl arc per X-AL-2 second-conjunct unreachability finding at fork doc §3 + §9 + §10. The sibling-ledger firing-site gap at AC #11 STRIKE adds a **fourth upstream-arc blocker** (alongside engine-layer impl + HITL disambiguator + override disambiguator); H_T-RT-35 RETIRE-READY transit gated on ALL four upstream arcs landing + e2e exercising the full chain.

**Tests (v2.37 reframed):** `test_caller_site_workload_class_selection_emission_engine_selector` (PRESERVED from v2.36); `test_caller_site_pause_resume_protocol_emission_resume_attempted` (PRESERVED from v2.36); `test_caller_site_pause_resume_protocol_emission_pause_captured_drain_flag` (PRESERVED from v2.36); `test_caller_site_pause_resume_protocol_emission_pause_captured_hitl_signal` (PRESERVED from v2.36); `test_two_caller_sites_full_chain_verification_passes_e2e` (AC #10 reframed from v2.36's 3-site test name); `test_no_pause_resume_protocol_binding_does_not_emit_state_ledger_entry` (PRESERVED from v2.36 — operator-opt-out negative path covering all 3 PAUSE_RESUME sites). **REMOVED at v2.37:** `test_sibling_ledger_entry_emission_at_sub_agent_dispatch_step_8b` (covered AC #11 STRUCK at v2.37).

**Rollback boundary:** UNCHANGED from v2.36 §1.2.

---

## §2 DAG delta

ZERO DAG edge changes at v2.37 (UNCHANGED from v2.36). The sequel-rescope drops one more AC (AC #11) at U-RT-111; it does NOT drop the unit itself, the unit's dependency edges, or its position in the topological sort. v2.34 + v2.35 + v2.36 §2 DAG declarations PRESERVED VERBATIM.

Unit count: 109 (UNCHANGED from v2.36).

---

## §3 Adjacent observations + carry-forward

(a) **CP plan v2.29 → v2.30 NEW units for engine-layer impl OWED at separate design-phase routing.** PRESERVED VERBATIM from v2.36 §3 (a).

(b) **CP spec v1.26 → v1.27 disambiguator-field amendments OWED at separate arc.** EXTENDED at v2.37: now covers 5 disambiguator surfaces — `RewrittenToolCall.semantic_variant_binding_id` + `PauseEvent.pause_event_id` + `resume_attempt_count` (v2.35 carry) + `override_id` + `policy_id` derivation rule OR `StepOverride` model field-set extension (v2.36 carry) + **NEW at v2.37: U-CP-34 `emit_sibling_ledger_entry` firing-site canonical-reading clarification or alternate-site spec amendment per §0.4 NEW row**. Implementer-discretion at the upstream arcs.

(c) **CXA v2.16 §0.4 forward-tracking partial transit at v2.37 impl arc — UNCHANGED.** **2 PENDING → 2 LANDED at v2.37 impl arc PR merge** for U-CP-75 (workload-class-selection) + U-CP-76 (pause-resume workflow-layer) — UNCHANGED from v2.36. Remaining 4 PENDING carry to upstream arcs (UNCHANGED from v2.36). NOTE: U-CP-34 is NOT a CXA §0.4 PENDING row (U-CP-34 was already LANDED at U-RT-35 PR #29); v2.37 STRIKE removes the "LANDED-but-never-fired residual closure" claim at AC #11 but does NOT change the CXA §0.4 row count.

(d) **H_T-RT-35 batch-filing precedent NOT applicable at v2.37.** PRESERVED VERBATIM from v2.36 §3 (d). Now requires **5-arc convergence** (v2.37 impl arc + override-disambiguator arc + HITL disambiguator arc + engine-layer impl arc + **NEW: sibling-ledger firing-site arc**) for full RETIRE-READY transit per X-AL-2 second-conjunct.

(e) ~~**U-CP-34 LANDED-but-never-fired residual closes at v2.36 impl arc per AC #11 (PRESERVED).**~~ **REVERSED at v2.37** — the U-CP-34 residual does NOT close at v2.37 impl arc per AC #11 STRIKE. Residual carries to upstream sibling-ledger firing-site arc per §0.4 NEW row + §3 (b) extended.

(f) **Workspace `CLAUDE.md` §2.4 runtime plan row bump owed.** Runtime plan row v2.36 → v2.37 at workspace root `CLAUDE.md` §2.4. Co-publication this arc. Unit count: 109 (UNCHANGED).

(g) **`harness-runtime/CLAUDE.md` plan-unit anchor refresh owed at impl arc.** PRESERVED VERBATIM from v2.36 §3 (g).

(h) **PR-shape recommendation.** v2.37 sequel-rescope arc + impl arc BUNDLED at PR #61 (same branch `worktree-u-rt-111-impl-v2-35`; Phase 1 plumbing already shipped at `9cca6d6`; Phase 2 plan v2.37 + fork §10 + workspace CLAUDE.md bump landed as additional commit). Mixed-posture bundled-absorption arc per CLAUDE.md §11.4; the fork doc §10 amendment IS the back-flow record; X-AL-3 CI guard satisfied via fork doc co-location at same PR.

(i) **40th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]`.** Pre-substantive advisor consultation at v2.37 authoring caught the `canonical_args` source-derivation as load-bearing pre-substantive ("brief_hash is convenient not principled"). Advisor recommended single operator AskUserQuestion if zero callers exist for the dispatch-site convention. Grep returned zero non-test callers; spec audit revealed primitive-scope mismatch at CP spec §15.1. Memory posture continues to validate.

(j) **Sub-species `plan-revision-against-not-yet-built-substrate` cardinality 2 → 3 at workflow doc §7.4.7.2.** v2.36 §3 (j) catalogued cardinality 2 (v2.34 + v2.35 + v2.36 transit). v2.37 IS the **THIRD instance** of the same sub-species at the SAME atomic-unit (U-RT-111) in a single calendar day (2026-05-29). Workflow-doc revision candidate strengthens further — empirical cardinality 3 across 3 sibling arcs in 1 calendar day is strong empirical signal that the sub-species warrants formal inclusion at workflow doc §7.4.7.2 next revision pass. **Distinct closure-event-class at v2.37 from v2.35/v2.36 instances:** v2.35 + v2.36 instances were "missing carrier-field at downstream type" + "missing field-set on caller-side model" (downstream-substrate-absence shape); v2.37 instance is "**primitive-scope mismatch between firing site and spec-anchored canonical use**" (semantic-scope-conflation shape). Same meta-pattern (plan claims wiring against not-spec-anchored substrate); distinct surface (semantic-scope-conflation in plan-authoring vs missing-field-on-existing-type).

(k) **Plan-revision discipline preserved at v2.37.** UNCHANGED from v2.36 §3 (k). v2.37 cites CP spec v1.2 §15.1 (UNCHANGED); does NOT invent any commitment; does NOT amend any cited spec; preserves dependency edges; coverage matrix UNCHANGED.

---

## §4 Filing footer

| Field | Value |
|---|---|
| Plan version | v2.37 |
| Predecessor | v2.36 (runtime plan v2.35 → v2.36 sequel-rescope at U-RT-111 + structural plumbing; PR #61 Phase 1) |
| Successor consumption | U-RT-111 v2.37-scope implementation arc (2 caller-site invocations + scoped 2-site e2e) — bundled at PR #61 per CLAUDE.md §11.4 |
| Cross-axis cascade | ZERO at v2.37 plan (per §0.3 + §0.4). 1 within-axis dependency edge UNCHANGED. CXA v2.17 §2.3.2 enumeration refresh partial UNCHANGED from v2.36 (2 of 6 LANDED at v2.37 impl arc; remainder gated on 4 upstream arcs — now including NEW sibling-ledger firing-site arc). |
| Authority anchors | `.harness/class_1_tension_u_rt_111_engine_layer_substrate_absence.md` §10 NEW (operator-ratified sequel-strike Reading A 2026-05-29); `Phase_7_Meta_Architecture_v1.md` §7.7 X-AL-2 + X-AL-3; `Project_Workflow_v1_12.md` §2.7.6 Class 1 back-flow; CP spec v1.2 §15.1 (per-sibling tool-call canonical binding); CP spec v1.26 §16.5 (does NOT include U-CP-34); runtime plan v2.36 §1.2 (this v2.37 amends in-place at delta-only-plan-chain layer) |
| Co-publications | Fork doc §10 NEW filed at same PR (sequel amendment to existing v2.35/v2.36 fork doc); workspace `CLAUDE.md` §2.4 row bump (v2.36 → v2.37; unit count 109 UNCHANGED) |
| Date | 2026-05-29 |
