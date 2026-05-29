# Implementation Plan — Harness Runtime — v2.36

*Delta over v2.35. v2.36 is a Phase 7 → design-phase Class 1 sequel-rescope per `.harness/class_1_tension_u_rt_111_engine_layer_substrate_absence.md` §9 NEW (operator-ratified 2026-05-29 single-day sequel to v2.35). v2.35 STRUCK ACs #4/#5/#6/#10 against ENGINE-LAYER and CP-AXIS DISAMBIGUATOR gaps at the workflow-layer-vs-engine-layer + RewrittenToolCall surfaces; v2.36 STRIKES AC #1 against a DIFFERENT structural shape — the U-CP-14 composer surface requires `override_id` + `policy_id` kw inputs that are NOT fields on the `StepOverride` model (per `harness-cp/src/harness_cp/workflow_manifest_entry.py:51-65` empirical orientation at HEAD `a35c716`). Same closure-event-class as v2.35's AC #4 STRIKE (missing-disambiguator-field gap) but distinct surface (override-input-surface vs HITL-tool-call-rewriting-input-surface). RETAINS ACs #2 + #3 + #7 + #9 + #11 + #12 (v2.36 reframed); REFRAMES AC #10 e2e from 3-or-4 sites to 3 sites (drops the override caller-site pair); H_T-RT-35 transit posture PRESERVED at PARTIAL post-v2.36 impl arc per v2.35 §1.2 AC #12 framing.*

## §0 Change note (v2.35 → v2.36)

### §0.1 What changed

| Element | v2.35 | v2.36 |
|---|---|---|
| U-RT-111 unit body | 8 ACs (12 declared with 4 STRUCK at v2.35) covering 4-or-5 caller-site invocation surfaces | 7 ACs (12 declared with 5 STRUCK total — v2.35's 4 + v2.36's NEW AC #1 strike) covering 3 caller-site invocation surfaces |
| AC #1 (override @ workflow_driver:777 + override_evaluator:61) | RETAINED at v2.35; "override_id + policy_id from manifest_entry.per_step_overrides[step_id] access" | **STRUCK at v2.36** per fork doc §9 NEW gap finding — `StepOverride` model has NO `override_id` NOR `policy_id` field; synthesizing at runtime would be X-AL-3 silent design extension per CP spec v1.26 §16.5.4 row U-CP-14 silence on derivation; routes to CP-axis design-phase per `.harness/class_1_tension_u_rt_111_engine_layer_substrate_absence.md` §9 (sequel item) |
| AC #10 (reframed e2e) | 3-or-4 implementable caller-sites (override + workload-class-selection + sibling-ledger + possibly pause-resume workflow-layer if AC #3 verifies clean) | **3 caller-sites** (workload-class-selection + pause-resume workflow-layer [AC #3 verified clean at v2.36 §0.3] + sibling-ledger) |
| §1 unit count | 109 (UNCHANGED from v2.34) | 109 (UNCHANGED — canonical-reading sequel-rescope, NOT a new unit) |
| §2 DAG | UNCHANGED from v2.34 | UNCHANGED from v2.35 |
| H_T-RT-35 transit framing | STAYS PARTIAL post-v2.35 impl arc per AC #12 reframe | UNCHANGED — STAYS PARTIAL post-v2.36 impl arc (already-correct posture; v2.36 doesn't re-litigate) |
| CXA v2.16 → v2.17 transit | 2-or-3 PENDING → LANDED at v2.35 impl arc PR merge (U-CP-74 override + U-CP-75 workload-class-selection + possibly U-CP-76 if AC #3 verified clean) | **2 PENDING → LANDED at v2.36 impl arc PR merge** (U-CP-75 workload-class-selection + U-CP-76 pause-resume workflow-layer). U-CP-74 (override) carry to CP-axis disambiguator-extension arc per fork §9 routing. Remaining 3-of-6 PENDING (U-CP-77/78/79) carry to upstream engine-layer impl arc (UNCHANGED from v2.35) |

### §0.2 Scope discipline

§0 (this change note); §1 U-RT-111 unit-body canonical-reading amendment STRIKING AC #1; §2 DAG preservation (ZERO edge changes); §3 adjacent observations + carry-forward; §4 filing footer. All v2.35 unit bodies + v2.34 + v2.33 + ... + v1 lineage PRESERVED VERBATIM per delta-only-plan-chain convention except the U-RT-111 AC #1 entry which is STRUCK at v2.36 + the AC #10 e2e site enumeration which is narrowed from 3-or-4 to 3 + the §3 (c) CXA transit count which is refreshed.

### §0.3 Authoring rationale + the v2.36 empirical finding

v2.35 §0.3 documented the empirical orientation finding at ACs #4/#5/#6 (HITL disambiguator gap + 2 engine-layer NotImplementedError stubs). At the v2.36 impl arc empirical orientation pass (worktree `u-rt-111-impl-v2-35`, branched off main `a35c716` post-PR #60 v2.35 merge), the AC #1 caller-site investigation surfaced a **SECOND structural disambiguator gap** that v2.35 itself missed at authoring time:

The U-CP-14 composer `emit_override_state_ledger_entry` at `harness-cp/src/harness_cp/per_step_override_evaluator.py:282-315` declares the signature:

```
async def emit_override_state_ledger_entry(
    *,
    workflow_id: str,
    step_id: str,
    override_id: str,            # ← REQUIRED kw input
    policy_id: str,              # ← REQUIRED kw input
    post_override_step_config: Mapping[str, Any],
    actor: ActorIdentity,
    ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]],
) -> WriteResult:
```

The CP spec v1.26 §16.5.4 row U-CP-14 idempotency-key formula names `override_id` + `policy_id` as the per-composer disambiguator segments:

> `workflow_id || step_id || override_id || policy_id || sha256(outcome_canonical_bytes).hex()`

BUT — the `StepOverride` model at `harness-cp/src/harness_cp/workflow_manifest_entry.py:51-65` has the empirical field set `{step_id, model_binding, engine_class, hitl_placement}` — **NO `override_id` field; NO `policy_id` field**. Neither field is sourceable from `manifest_entry.per_step_overrides[step_id]` access.

The v2.35 §1.2 row 1 wrote "`override_id` + `policy_id` from `manifest_entry.per_step_overrides[step_id]` access (the override the function applied)" — that wording was authored at v2.35 WITHOUT empirical grep-verification of the `StepOverride` field set against the CP spec §16.5.4 disambiguator field names. v2.35 IS the rescope that explicitly catalogued this failure-mode at v2.35 §3 (j) sub-species candidate `plan-revision-against-not-yet-built-substrate` — and now v2.36 documents the **second instance** of the same sub-species at the same atomic-unit, surfaced 19 hours after v2.35 publication.

CP spec v1.26 §16.5.4 row U-CP-14 has NO per-composer disambiguator note (the per-composer notes at §16.5.4 cover rows U-CP-27, U-CP-30, U-CP-37, U-CP-49, U-CP-50 only). The spec is SILENT on whether `override_id` + `policy_id` are caller-supplied from external source OR derivable via spec-authoritative rule. Synthesizing at runtime axis under spec-silence would be X-AL-3 silent design extension per `Phase_7_Meta_Architecture_v1.md` §7.7 — structurally identical to v2.35's AC #4 STRIKE rationale.

Per `[[advisor-before-substantive-work-for-cross-axis-blockers]]` 39th application at v2.36 authoring: advisor confirmed "default verdict — HALT, don't silent-absorb" upon finding the gap. Operator ratified Reading (A) sequel-strike via AskUserQuestion 2026-05-29 (option 1 — STRIKE AC #1 + amend to v2.36; file gap finding at existing v2.35 fork doc + bundle as same-PR back-flow).

### §0.4 Out-of-scope at v2.36 (owed separately, extending v2.35 §0.4)

| Owed arc | Routing target | Rationale |
|---|---|---|
| **NEW at v2.36:** CP spec v1.26 → v1.27 amendment OR `StepOverride` field-set extension at CP plan v2.29 → v2.30 surfacing `override_id` + `policy_id` as canonical caller-supplied fields | CP-axis design-phase routing per `Project_Workflow_v1_12.md` §2.7.6 | Pre-v2.36 spec is silent on derivation; impl-discretion synthesis is X-AL-3. Options at upstream arc: (a) CP spec §16.5.4 row U-CP-14 disambiguator note authoring rule for `override_id` (e.g., `override_id = f"override:{workflow_id}:{step_id}"`) + `policy_id` (e.g., `policy_id = workflow_id` for single-policy-per-workflow MVP); OR (b) `StepOverride` model field-set extension to carry `override_id: str` + `policy_id: str` as required fields. Operator-discretion at upstream arc. |
| CP plan v2.29 → v2.30 NEW units for engine-layer impl (U-CP-49 + U-CP-50 bodies materialized) | CP-axis design-phase routing | UNCHANGED carry from v2.35 §0.4 |
| CP spec v1.26 → v1.27 amendments for `RewrittenToolCall.semantic_variant_binding_id` + `PauseEvent.pause_event_id` + `resume_attempt_count` field extensions | CP-axis design-phase routing OR engine-layer impl arc absorption | UNCHANGED carry from v2.35 §0.4 |
| CXA v2.16 → v2.17 §2.3.2 enumeration refresh — full 6 PENDING → 6 LANDED | Retirement-batch filing arc post-engine-layer-landing | v2.36 lands 2-of-6 PENDING (U-CP-75 + U-CP-76); 4-of-6 carry (U-CP-74 owed at override-disambiguator-resolution arc + U-CP-77/78/79 owed at engine-layer + HITL arcs) |
| Runtime spec §12.3 prose alignment per v2.33 (C-defer) | Next runtime-spec revision pass | UNCHANGED carry from v2.35 §0.4 |

---

## §1 U-RT-111 unit-body canonical-reading amendment (v2.36)

### §1.1 Site

PRESERVED VERBATIM from v2.35 §1.1 — U-RT-111 slots at the L7-and-later wiring-consumer layer, singleton extension of U-RT-110's stage-6 surface.

### §1.2 U-RT-111 — Body (v2.36 canonical reading)

**Implements:** UNCHANGED from v2.35 §1.2 (CP spec v1.26 §16.5.7 firing-site discipline; CP spec v1.26 §16.5.9 invariants 1-7; runtime spec v1.7 §12.3 17-edge enumeration — **2 of 7 CP-materializable edges at this arc** per v2.36 strike; remaining 5 deferred to upstream engine-layer impl arc + CP-axis disambiguator extension arc[s]; cross-axis composition per CXA v2.16 §0.4 — 2 PENDING → 2 LANDED upon v2.36 impl arc completion + e2e verification PASS).

**Files (v2.36 narrowed from v2.35):**
- ~~`harness-cp/src/harness_cp/workflow_driver.py` (EXTEND at the `resolve_step_binding(...)` immediate-caller site near line 777)~~ — **REMOVED at v2.36** per AC #1 STRIKE
- ~~`harness-runtime/src/harness_runtime/lifecycle/override_evaluator.py` (EXTEND at the `resolve_step_binding(...)` immediate-caller site at line 61)~~ — **REMOVED at v2.36** per AC #1 STRIKE
- `harness-runtime/src/harness_runtime/lifecycle/engine_selector.py` (EXTEND at the `select_engine_class(...)` immediate-caller site at line 145; existing body PRESERVED VERBATIM at non-firing-site lines)
- `harness-cp/src/harness_cp/workflow_driver.py` (EXTEND at 3 `PauseResumeProtocol` class method invocation sites — line 546 RESUME_ATTEMPTED + line 756 PAUSE_CAPTURED drain-flag path + line 881 PAUSE_CAPTURED HITL-signal path; existing body PRESERVED VERBATIM at non-firing-site lines)
- `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py` (EXTEND at the canonical sub_agent_dispatch step 8 post-audit-composition site per spec v1.7 §14.7.2 step 8b state-ledger-entry-write; existing body PRESERVED VERBATIM at non-firing-site lines)
- `harness-runtime/tests/test_cp_is_caller_site_integration.py` (NEW — 3 per-caller-site unit tests + 1 sibling-ledger residual test + 1 scoped e2e covering the 3 implementable sites in a single workflow lifecycle + 1 negative-path test (no-binding short-circuit) = **6 tests; reframed from v2.35's 6-or-7 to fixed 6**)

**Signatures introduced:** NONE at U-RT-111 (UNCHANGED from v2.35 §1.2) — v2.36 modifies existing function bodies at 3 caller-site locations to invoke U-RT-110's methods.

**Per-caller-site invocation contract (3 invocations at v2.36):**

| # | Caller site (file:line at HEAD `a35c716`) | U-RT-110 method invoked | Composer args sourced at caller site | Spec authority |
|---|---|---|---|---|
| 1 | ~~`harness-cp/src/harness_cp/workflow_driver.py:777` + `override_evaluator.py:61`~~ — **STRUCK at v2.36** | ~~`emit_override_state_ledger_entry`~~ | ~~per v2.35 §1.2 row 1 — empirically blocked at HEAD by `StepOverride` field-set absence~~ | Routes to CP-axis disambiguator-extension arc per fork §9 |
| 2 | `harness-runtime/src/harness_runtime/lifecycle/engine_selector.py:145` immediate-post-`select_engine_class(input)` invocation (PRESERVED VERBATIM from v2.35 §1.2 row 2) | `emit_workload_class_selection_state_ledger_entry(workflow_id, step_id, selection_result, actor)` | `workflow_id` synthesized as `f"workflow.init:{input.workload_class.value}"` per CP-IS convention at C-IS-10 §10.1; `step_id` synthetic `"workflow.init"`; `selection_result` from `select_engine_class(...)` return; `actor` from runtime context (impl-discretion at engine_selector scope) | CP spec v1.26 §16.5.7 row U-CP-27 |
| 3 | `harness-cp/src/harness_cp/workflow_driver.py:546` post-`protocol.attempt_resume(...)` + `:756` post-`protocol.capture_pause_snapshot(...)` drain-flag path + `:881` post-`protocol.capture_pause_snapshot(...)` HITL-signal path (PRESERVED VERBATIM from v2.35 §1.2 row 3 — AC #3 verified CLEAN at v2.36 empirical orientation per fork §9; PauseResumeProtocol class methods at `pause_resume_protocol.py:263` + `:296` are IMPLEMENTED, not NotImplementedError stubs) | `emit_pause_resume_state_ledger_entry(workflow_id, step_id, protocol_event_kind, event_sequence_id, protocol_state_snapshot, actor)` | `workflow_id` from `manifest_entry.workflow_id`; `step_id` from current `step.step_id` (or `"workflow.init"` synthetic if pre-step-loop site); `protocol_event_kind` = `PauseResumeProtocolEventKind.RESUME_ATTEMPTED` at line 546 OR `PAUSE_CAPTURED` at lines 756 + 881; `event_sequence_id` from `step_index` (impl-discretion per CP spec v1.26 §16.5.4 silence on source — at v1.6 MVP each step invokes the protocol at most once per kind; collisions documented as deferred at follow-on arc); `protocol_state_snapshot` from `resume_result.model_dump()` at line 546 OR `pause_snapshot.model_dump()` at lines 756 + 881; `actor` from `ctx.ledger_writer.actor` | CP spec v1.26 §16.5.7 row U-CP-30 (workflow-layer per CP spec v1.11 §26 NEW NOTE coexistence) |
| 11 (renumbered from v2.34 §1.2 AC #11; PRESERVED VERBATIM from v2.35 §1.2 row 11) | `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py` post-step-8 audit-composition success path | `emit_sibling_ledger_entry(parent_action_id, sibling_thread_id, step_index, tool, canonical_args, sibling_agent_identity, timestamp)` (the U-RT-35 LANDED synchronous method at `RuntimeCpIsWiring`; U-CP-34 residual closure) | Source args at sub_agent_dispatch step 8 success-path site per spec v1.7 §14.7.2 step 8b state-ledger-entry-write semantics | CP spec v1.26 §16.5.7 (transitively via U-CP-34 LANDED at U-RT-35); v1.7 §14.7.2 step 8b |

**Depends on:** PRESERVED VERBATIM from v2.35 §1.2 — U-RT-110 (within-axis), U-RT-12 (transitive), U-CP-74..U-CP-79 (cross-axis transitive via U-RT-110), U-CP-34 (cross-axis for AC #11).

**Acceptance criteria (v2.36 reframed from v2.35):**

1. ~~**Caller-site (1) override-application — workflow_driver + override_evaluator.**~~ **STRUCK at v2.36** per fork doc §9 NEW gap finding: `StepOverride` model at `harness-cp/.../workflow_manifest_entry.py:51-65` has the field set `{step_id, model_binding, engine_class, hitl_placement}` — NEITHER `override_id` NOR `policy_id` is a field. U-CP-14 composer `emit_override_state_ledger_entry` at `per_step_override_evaluator.py:282-315` requires both as kw inputs per CP spec v1.26 §16.5.4 row U-CP-14 idempotency-key formula. Spec is SILENT on derivation (no per-composer disambiguator note for U-CP-14 at §16.5.4). Synthesizing at runtime axis would be X-AL-3 silent design extension. Routes to CP-axis design-phase per §0.4 NEW row.

2. **Caller-site (2) workload-class-selection @ engine_selector.py:145.** PRESERVED VERBATIM from v2.35 §1.2 AC #2 — at `engine_selector.py:145` immediate-post-`select_engine_class(input)`: invoke `emit_workload_class_selection_state_ledger_entry(...)` with `step_id="workflow.init"` synthetic identifier per CP-IS convention at C-IS-10 §10.1 (engine selection IS workflow-init-time). `workflow_id` synthesized at impl arc per engine_selector context — see §1.2 row 2 for implementer-discretion shape.

3. **Caller-site (3) pause-resume workflow-layer (VERIFIED CLEAN at v2.36).** PRESERVED VERBATIM from v2.35 §1.2 AC #3 + v2.35 AMBER → v2.36 CLEAN per fork §9 verification — `PauseResumeProtocol` class methods at `pause_resume_protocol.py:263` (`capture_pause_snapshot`) + `:296` (`attempt_resume`) ARE IMPLEMENTED (NOT NotImplementedError stubs like the engine-layer free funcs at `:106` + `:128`). The 3 firing sites at `workflow_driver.py:546` + `:756` + `:881` ARE reachable in production execution. AC proceeds per the v2.35 AC #3 details.

4-6. ~~**Caller-site (4)/(5)/(6).**~~ **STRUCK at v2.35** (preserved verbatim per v2.35 §1.2 ACs #4/#5/#6 strikethrough rationale).

7. **CP-axis production functions PRESERVED VERBATIM.** PRESERVED VERBATIM from v2.35 §1.2 AC #7 — ZERO modification to any CP-axis function signature; ZERO return-type widening at CP-axis. At v2.36: the 3 sites at `workflow_driver.py:546+756+881` extend the SURROUNDING function (`execute_workflow` + `_execute_workflow_body`) bodies with the NEW emission invocations; the `PauseResumeProtocol` class method signatures at `pause_resume_protocol.py:263+296` PRESERVED VERBATIM (the emission fires AFTER the method return, not by modifying the method).

8. ~~**Disambiguator-availability halt.**~~ **STRUCK at v2.35** (preserved at v2.36).

9. **Actor-source verification.** PRESERVED VERBATIM from v2.35 §1.2 AC #9.

10. **3-site full chain e2e (REFRAMED from v2.35's 3-or-4 to v2.36's 3).** `harness-runtime/tests/test_cp_is_caller_site_integration.py` exercises 3 caller-site invocations (workload-class-selection + pause-resume workflow-layer + sibling-ledger) within a single end-to-end workflow lifecycle. Assert: persisted ledger contains entries with `action_id ∈ {cp.workload-binding-class-selection, cp.pause-resume-protocol, cp-sibling-ledger-entry-action-id-per-U-RT-35}` (the v2.36 implementable subset); `chain_verification` per C-IS-06 §6 passes for the multi-entry chain.

11. **U-CP-34 LANDED-but-never-fired residual closure.** PRESERVED VERBATIM from v2.35 §1.2 AC #11.

12. **H_T-RT-35 transit posture PRESERVED at v2.36.** v2.35 AC #12 PRESERVED VERBATIM at v2.36 — H_T-RT-35 STAYS PARTIAL post-v2.36 impl arc. NO retirement-event filing at v2.36 impl arc per X-AL-2 second-conjunct unreachability finding at fork doc §3 + §9. The override-disambiguator gap at AC #1 STRIKE adds a SECOND upstream-arc blocker (alongside engine-layer impl + HITL disambiguator); H_T-RT-35 RETIRE-READY transit gated on ALL three upstream arcs landing + e2e exercising the full chain.

**Tests (v2.36 reframed):** `test_caller_site_workload_class_selection_emission_engine_selector` (PRESERVED from v2.35); `test_caller_site_pause_resume_protocol_emission_resume_attempted` (NEW); `test_caller_site_pause_resume_protocol_emission_pause_captured_drain_flag` (NEW); `test_caller_site_pause_resume_protocol_emission_pause_captured_hitl_signal` (NEW); `test_sibling_ledger_entry_emission_at_sub_agent_dispatch_step_8b` (AC #11; PRESERVED from v2.35); `test_three_caller_sites_full_chain_verification_passes_e2e` (AC #10 reframed from v2.35); `test_no_pause_resume_protocol_binding_does_not_emit_state_ledger_entry` (NEW — operator-opt-out negative path covering all 3 PAUSE_RESUME sites).

**Rollback boundary:** UNCHANGED from v2.35 §1.2.

---

## §2 DAG delta

ZERO DAG edge changes at v2.36 (UNCHANGED from v2.35). The sequel-rescope drops one more AC (AC #1) at U-RT-111; it does NOT drop the unit itself, the unit's dependency edges, or its position in the topological sort. v2.34 + v2.35 §2 DAG declarations PRESERVED VERBATIM.

Unit count: 109 (UNCHANGED from v2.35).

---

## §3 Adjacent observations + carry-forward

(a) **CP plan v2.29 → v2.30 NEW units for engine-layer impl OWED at separate design-phase routing.** PRESERVED VERBATIM from v2.35 §3 (a).

(b) **CP spec v1.26 → v1.27 disambiguator-field amendments OWED at separate arc.** EXTENDED at v2.36: now covers 4 disambiguator fields — `RewrittenToolCall.semantic_variant_binding_id` + `PauseEvent.pause_event_id` + `resume_attempt_count` on `ResumeAttempt` or `ResumeOutcome` (v2.35 carry) PLUS NEW at v2.36: `override_id` + `policy_id` derivation rule OR `StepOverride` model field-set extension. Implementer-discretion at the upstream arcs.

(c) **CXA v2.16 §0.4 forward-tracking partial transit at v2.36 impl arc.** REFRESHED at v2.36: **2 PENDING → 2 LANDED at v2.36 impl arc PR merge** for U-CP-75 (workload-class-selection) + U-CP-76 (pause-resume workflow-layer). Remaining 4 PENDING carry to upstream arcs: U-CP-74 (override) → CP-axis disambiguator-extension arc per fork §9; U-CP-77 (HITL tool-call rewriting) → CP-axis disambiguator-extension arc OR CP-axis HITL impl arc; U-CP-78 + U-CP-79 (engine-layer pause/resume) → upstream engine-layer impl arc.

(d) **H_T-RT-35 batch-filing precedent NOT applicable at v2.36.** PRESERVED VERBATIM from v2.35 §3 (d). Now requires 4-arc convergence (v2.36 impl arc + override-disambiguator arc + HITL disambiguator arc + engine-layer impl arc) for full RETIRE-READY transit per X-AL-2 second-conjunct.

(e) **U-CP-34 LANDED-but-never-fired residual closes at v2.36 impl arc per AC #11 (PRESERVED).** PRESERVED VERBATIM from v2.35 §3 (e).

(f) **Workspace `CLAUDE.md` §2.4 runtime plan row bump owed.** Runtime plan row v2.35 → v2.36 at workspace root `CLAUDE.md` §2.4. Co-publication this arc. Unit count: 109 (UNCHANGED).

(g) **`harness-runtime/CLAUDE.md` plan-unit anchor refresh owed at impl arc.** PRESERVED VERBATIM from v2.35 §3 (g).

(h) **PR-shape recommendation.** v2.36 sequel-rescope arc + impl arc BUNDLED at single PR (mixed-posture bundled-absorption arc per CLAUDE.md §11.4; the v2.35 fork doc §9 amendment IS the back-flow record; X-AL-3 CI guard at PR #48 satisfied via fork doc co-location at same PR). PR title shape: `feat(runtime): U-RT-111 v2.36-scope impl arc — 3 caller sites + plan v2.35→v2.36 STRIKE AC #1 + fork doc §9`. Branching: off main post-PR #60 merge.

(i) **39th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]`.** Pre-substantive advisor consultation at v2.36 authoring caught the AC #1 disambiguator gap upon first checking the U-CP-14 composer signature. Advisor sharpened the framing to "default verdict — HALT, don't silent-absorb" + identified spec-silence at §16.5.4 row U-CP-14 as the discriminator. Memory posture continues to validate.

(j) **Sub-species `plan-revision-against-not-yet-built-substrate` cardinality 1 → 2 at workflow doc §7.4.7.2.** v2.35 §3 (j) catalogued the candidate at cardinality 1 (v2.34 → v2.35 transit). v2.36 IS the SECOND instance of the same sub-species at the SAME atomic-unit (U-RT-111) in a 19-hour window. Workflow-doc revision candidate strengthens — empirical cardinality 2 across 2 sibling arcs in 1 calendar day suggests sub-species inclusion at workflow doc §7.4.7.2 next revision.

(k) **Plan-revision discipline preserved at v2.36.** UNCHANGED from v2.35 §3 (k). v2.36 cites CP spec v1.26 §16.5 (UNCHANGED); does NOT invent any commitment; does NOT amend any cited spec; preserves dependency edges; coverage matrix UNCHANGED.

---

## §4 Filing footer

| Field | Value |
|---|---|
| Plan version | v2.36 |
| Predecessor | v2.35 (runtime plan v2.34 → v2.35 NEW U-RT-111 narrow-scope rescope; PR #60) |
| Successor consumption | U-RT-111 v2.36-scope implementation arc (3 caller-site invocations + sibling-ledger residual + scoped 3-site e2e) — bundled at the same PR as this plan revision per CLAUDE.md §11.4 |
| Cross-axis cascade | ZERO at v2.36 plan (per §0.3 + §0.4). 1 within-axis dependency edge UNCHANGED. CXA v2.17 §2.3.2 enumeration refresh partial (2 of 6 LANDED at v2.36 impl arc; remainder gated on upstream arcs). |
| Authority anchors | `.harness/class_1_tension_u_rt_111_engine_layer_substrate_absence.md` §9 NEW (operator-ratified sequel-strike Reading A 2026-05-29); `Phase_7_Meta_Architecture_v1.md` §7.7 X-AL-2 + X-AL-3; `Project_Workflow_v1_12.md` §2.7.6 Class 1 back-flow; CP spec v1.26 §16.5.4 row U-CP-14 (spec-silent on `override_id` + `policy_id` derivation); runtime plan v2.35 §1.2 (this v2.36 amends in-place at delta-only-plan-chain layer) |
| Co-publications | Fork doc §9 NEW filed at same PR (sequel amendment to existing v2.35 fork doc); workspace `CLAUDE.md` §2.4 row bump (v2.35 → v2.36; unit count 109 UNCHANGED); runtime impl arc landed at same PR |
| Date | 2026-05-29 |
