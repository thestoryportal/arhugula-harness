# Class 1 Tension — U-RT-111 plan-vs-reality gap: engine-layer substrate absence + disambiguator gaps + X-AL-2 transit unreachability

**Status:** APPLIED-AS-(A)-RESCOPE (operator AskUserQuestion ratified 2026-05-29; v2.35 narrow-scope rescope authored at same arc; closure-back-reference owed at runtime plan v2.34 §0.3 + workspace `CLAUDE.md` §2.4)
**Filed:** 2026-05-29
**Surfaced at:** U-RT-111 empirical orientation pass (pre-substantive verification per ACs #8 + #9 halt-conditions per `[[halt-route-split-AC-pattern]]`)
**Class:** 1 (halt-execution — design-phase artifact requires revision per `Project_Workflow_v1_12.md` §2.7.6)
**Reading:** A (rescope at planning layer; drop structurally-unreachable ACs)

---

## §1 Trigger

Pre-substantive empirical orientation at U-RT-111 impl arc (worktree `u-rt-111-impl`, branched off main `a2a0fc2` post-PR #59 U-RT-110 merge) verified each of the 5 risk surfaces flagged at runtime plan v2.34 §1.2 ACs #8 + #9 (disambiguator-availability + actor-source verification). The verification surfaced **7 gaps** between the plan's optimistic framing and the actual production state at HEAD. The gaps compose into a **structural transit-unreachability** at H_T-RT-35 PARTIAL → RETIRE-READY under X-AL-2 second-conjunct discipline.

Per ACs #4/#5/#6/#8 explicit halt-on-disambiguator-absence wording ("DO NOT invent fields at runtime axis — X-AL-3 silent design extension"), the impl arc HALTED before any code edit. This fork doc absorbs the orientation findings into a Class 1 back-flow at the runtime-plan-revision layer.

---

## §2 Findings — per-AC empirical verification

| AC | Plan claim | Empirical state at HEAD `a2a0fc2` | Gap class |
|---|---|---|---|
| #1 override @ workflow_driver + override_evaluator | Sites at `workflow_driver.py:777` immediate-post-`resolve_step_binding(...)` + `override_evaluator.py:61` | ✅ `workflow_driver.py:777` confirmed: `binding = resolve_step_binding(manifest_entry, str(step.step_id), ...)`. ✅ `override_evaluator.py` exists at runtime path | **CLEAN** |
| #2 workload-class-selection | Workflow-driver workload-binding-time site (recommended 2.a synthetic step_id `"workflow.init"`) | ✅ `select_engine_class` call site found at `harness-runtime/src/harness_runtime/lifecycle/engine_selector.py:145` | **CLEAN** (one site, not workflow_driver's bootstrap — minor reframe owed) |
| #3 pause-resume workflow-layer | Workflow_driver `PauseResumeProtocol` class method invocation sites at workflow-layer transitions (likely at existing `RunStatus.PAUSED` integration at U-RT-89) | ⚠️ Needs deeper verification; depends on `PauseResumeProtocol` class methods being implemented (engine-layer free funcs ARE NotImplementedError — the workflow-layer class wraps them) | **AMBER** (needs verification; possibly clean) |
| #4 HITL tool-call rewriting | `semantic_variant_binding_id` from `RewrittenToolCall.semantic_variant_binding_id` field-access at impl line 109 | ❌ `RewrittenToolCall` field set at `hitl_as_tool_call_rewriting.py:116-135` is `{tool, server, hitl_required, variant, response_palette}` — NO `semantic_variant_binding_id` field exists | **BLOCKED** (X-AL-3 silent extension if synthesized at runtime; routes to CP-axis plan extension owed at upstream arc) |
| #5 pause-captured engine-layer | At `pause_resume_composer.py` immediate-post-`capture_pause_snapshot(...)` invocation | ❌ **(a)** `pause_resume_composer.py` does NOT exist at `harness-runtime/src/harness_runtime/lifecycle/`. **(b)** `capture_pause_snapshot(...)` at `harness-cp/.../pause_resume_protocol.py:106` raises `NotImplementedError("capture_pause_snapshot composes the U-IS-11 F2 append + snapshot serialization; the CP plan U-CP-49 unit declares the pause-protocol surface")`. **(c)** `PauseEvent` field set at `pause_resume_protocol.py:46-60` is `{paused_at, pause_reason, state_summary_snapshot, external_refs_captured, pause_audit_entry_id}` — NO `pause_event_id` field; closest is `pause_audit_entry_id` (different semantic). **(d)** `capture_pause_snapshot(...)` returns `PauseEvent` per signature; U-CP-78 `emit_pause_captured_state_ledger_entry` requires `PauseSnapshot` (the 8-field type at `pause_resume_protocol_types.py:92`) — **type mismatch**. | **STRUCTURALLY BLOCKED** (4 composed gaps; engine-layer not built; cannot wire a NotImplementedError stub) |
| #6 resume-attempted engine-layer | At `pause_resume_composer.py` immediate-post-`attempt_resume(...)` invocation | ❌ **(a)** `pause_resume_composer.py` does NOT exist. **(b)** `attempt_resume(...)` at `pause_resume_protocol.py:128` raises `NotImplementedError`. **(c)** `resume_attempt_count` is NOT a field on `ResumeAttempt` (`{paused_workflow_id, resume_at, resume_request_actor}`) NOR on `ResumeOutcome` (`{outcome_kind, material_diff, context_revalidated, resume_audit_entry_id}`) | **STRUCTURALLY BLOCKED** (3 composed gaps) |
| #8 disambiguator-availability halt | "Any missing surface → Class 1 fork at impl arc per `[[halt-route-split-AC-pattern]]`; do NOT invent fields at runtime axis (X-AL-3 silent design extension)" | Halt condition met at ACs #4 + #5 + #6 (3 disambiguator fields missing) | **HALT ACTIVATED** |
| #9 actor-source verification | `step_context.parent_actor` (per CP spec v1.6 §25.2.1 + v1.7 F1-01 inline-fix anchor) reachable at step-execution-time sites | ✅ `StepExecutionContext.parent_actor: Actor` field exists at `workflow_driver_types.py:222`; reachable at all step-execution-time sites | **CLEAN** |
| #10 e2e test substrate (6-site full chain) | All 6 caller-sites firing within a single workflow lifecycle; load-bearing test for H_T-RT-35 transit | ❌ Depends on ACs #5 + #6 firing — both structurally blocked. e2e cannot exercise all 6 source-unit surfaces; the test that the plan declares "load-bearing for H_T-RT-35 transit" cannot be authored | **STRUCTURALLY BLOCKED** (depends on #5 + #6) |
| #11 sibling-ledger residual @ sub_agent_dispatch | Identify canonical sub_agent_dispatch firing-site at `sub_agent_dispatch.py` post-sibling-composition step per spec v1.7 §14.7.2 step 8b | ✅ `sub_agent_dispatch.py` exists at `harness-runtime/.../lifecycle/` | **CLEAN** (specific firing-site line owed at impl verification) |

---

## §3 The decisive structural finding — H_T-RT-35 RETIRE-READY is unreachable at this arc per X-AL-2

The plan's transit framing at v2.34 §0.3 + ACs #10 + #12 claims:

> "H_T-RT-35 PARTIAL → RETIRE-READY transit eligible at v2.34 impl arc completion + e2e verification per `[[verification-shape-sharpened-grep-vs-e2e]]` discipline showing production-callsite-fires-composer-fires-ledger-write at the full 6 source-unit surfaces."

X-AL-2 (`Phase_7_Meta_Architecture_v1.md` §7.7) states the retirement condition:

> "Retirement = (cited unit IDs landed) ∧ (substituted H_E surface no longer invoked at substitution site). Both conditions required."

The H_E substitution at engine-layer pause/resume IS the `NotImplementedError` raise — the runtime production code, when it reaches `capture_pause_snapshot(...)` or `attempt_resume(...)`, encounters the exception instead of a real body. Wiring caller-sites #5 + #6 to **never-fired paths** (because they raise before the emit-state-ledger step) does NOT satisfy the second conjunct: the H_E substitute (the stub raise) IS still invoked at the substitution site.

H_T-RT-35 RETIRE-READY transit therefore requires the **upstream engine-layer impl** (CP plan U-CP-49 + U-CP-50 unit bodies authored against real engine substrate per ADR-D1 v1.2 §1.1.1 + CP spec v1.11 §26.x) to land BEFORE U-RT-111's caller-site wiring can satisfy the transit gate.

The (F) FULL-WIRE-paired framing at v2.33 §0.3 + v2.34 §0.3 implicitly assumed engine-layer substrate WAS LANDED — that assumption is empirically false at HEAD.

**Consequence:** Even if U-RT-111 lands ACs #1/#2/#3/#11 + a scoped e2e covering only the implementable subset, H_T-RT-35 remains PARTIAL. The retirement-batch filing precedent at `[[h-t-cp-19-default-gate-level-spec-extension]]` shape proposed at v2.34 §3 (d) cannot fire.

---

## §4 Readings

### Reading A — Rescope U-RT-111 at the planning layer (operator-ratified 2026-05-29)

**Author runtime plan v2.34 → v2.35 narrow-scope revision.**

- DROP ACs #4 (HITL — blocked by CP-axis disambiguator gap), #5 (pause-captured engine-layer — blocked by engine-layer absence), #6 (resume-attempted engine-layer — blocked by engine-layer absence), #10 (6-site e2e — blocked by #5 + #6 absence).
- RETAIN ACs #1 (override @ workflow_driver + override_evaluator), #2 (workload-class-selection @ engine_selector.py reframed), #3 (pause-resume workflow-layer — AMBER; needs verification at impl arc), #11 (sibling-ledger residual @ sub_agent_dispatch), #7 (CP-axis preservation), #9 (actor-source — already verified clean).
- REFRAME #12 (transit posture): H_T-RT-35 stays PARTIAL post-arc; no RETIRE-READY claim; upstream engine-layer + CP-axis disambiguator-extension blockers documented as out-of-scope.
- AUTHOR a scoped e2e at AC #10 reframe: 3-or-4-site e2e covering only the implementable subset (override + workload-class-selection + sibling-ledger + possibly pause-resume workflow-layer if AC #3 verifies clean); chain_verification per C-IS-06 §6 over the partial chain.

**Co-publications at the same arc:**
- Workspace `CLAUDE.md` §2.4 runtime plan row v2.34 → v2.35.
- Closure-back-reference annotation at runtime plan v2.34 §0.3 pointing to this fork doc + v2.35.
- This fork doc Status: APPLIED-AS-(A)-RESCOPE.

**NOT in scope at this arc** (owed separately):
- CP plan v2.29 → v2.30 NEW units for engine-layer impl (U-CP-49 + U-CP-50 unit bodies materialized) — upstream blocker; routes to design-phase per `Project_Workflow_v1_12.md` §2.7.6.
- CP spec v1.26 → v1.27 amendments for `RewrittenToolCall.semantic_variant_binding_id` + `PauseEvent.pause_event_id` + `ResumeAttempt.resume_attempt_count` field extensions — alternatively absorbed at the engine-layer impl arc if those fields become naturally surfaced at impl time.
- ADR / ADD / PRD touch — none owed; the rescope operates within the runtime-axis canonical-reading layer.

### Reading B — Comprehensive defer

File this fork doc PROPOSING + halt all U-RT-111 work pending engine-layer landing. Slower; cleaner separation. Operator did NOT select this reading.

### Reading C — Partial-land the implementable subset under existing v2.34 (rejected)

Land ACs #1 + #2 + #11 under the existing v2.34 with ACs #4/#5/#6/#10 PARTIAL-LANDED per `[[halt-route-split-AC-pattern]]`; H_T-RT-35 stays PARTIAL. This was an option at the AskUserQuestion but rejected per operator preference for clean planning-layer rescope (avoid landing partial wiring under a plan that promises transit it cannot deliver).

---

## §5 Cross-axis cascade

ZERO cross-axis cascade at the v2.35 rescope itself. The rescope is intra-runtime-axis canonical-reading + AC-set narrowing.

The upstream blockers DO have cross-axis cascade implications (engine-layer impl at CP-axis would cascade to runtime caller-site wiring + IS state-ledger emission + OD audit ingestion), but those cascades are deferred to the upstream impl arc — NOT absorbed here.

---

## §6 Authority anchors

- `Phase_7_Meta_Architecture_v1.md` §7.7 X-AL-2 (retirement-criterion two-conjunct discipline)
- `Phase_7_Meta_Architecture_v1.md` §7.7 X-AL-3 (no silent H_T design extension at Phase 7)
- `Project_Workflow_v1_12.md` §2.7.6 (Class 1 back-flow routing)
- `Project_Workflow_v1_12.md` §4.1 (fork classification discriminator)
- Runtime plan v2.34 §1.2 ACs #8 + #9 (halt-on-disambiguator-absence wording authorizing this halt)
- `Implementation_Plan_Harness_Runtime_v2_34.md` §3 (d) (H_T-RT-35 batch-filing precedent now structurally unreachable per §3 of this fork doc)
- CP spec v1.26 §16.5.2 + §16.5.7 + §16.5.9 (composer firing-site discipline)
- CP spec v1.11 §26 NEW NOTE (engine-layer vs workflow-layer coexistence — anchors the AC #5/#6 engine-layer / AC #3 workflow-layer distinction)
- ADR-D1 v1.2 §1.1.1 (engine-class taxonomy — anchors the pause/resume engine-layer impl gap)

---

## §7 Audit-trail notes

- 37th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` posture — advisor was consulted pre-substantive-work at this arc; advisor identified the X-AL-2 transit-unreachability finding which I would not have surfaced absent the call. Memory posture continues to validate operationally.
- Pre-substantive empirical orientation as the load-bearing discipline: ACs #8 + #9 explicit halt-on-disambiguator-absence wording at v2.34 was the operative guard. The halt fired correctly; ZERO X-AL-3 silent extension occurred; ZERO production code written against unverified surface.
- Sub-species candidate at `Project_Workflow_v1_12.md` §7.4.7.2 — **plan-revision-against-not-yet-built-substrate** — distinct closure-event-class where a planning-layer arc proposes wiring against a downstream substrate that hasn't been built yet, surfacing the gap at impl-time grounding. The (F) FULL-WIRE-paired framing at v2.33 §0.3 + v2.34 §0.3 IS this sub-species: the plan assumed engine-layer substrate was landed (because it cited CP plan U-CP-49/U-CP-50 as "LANDED" via PRs #43/#44, but those PRs landed the §16.5 *composer* free functions, NOT the engine-layer *substrate* free functions at the same module — distinct closure events). Catalogue candidate at workflow doc revision pass.
- Class 1 back-flow at Phase 7 → design-phase routing per CLAUDE.md §4.3: this fork doc IS the back-flow record. PR carrying both fork doc + runtime plan v2.35 satisfies X-AL-3 CI guard at PR #48 (back-flow doc included at same PR as design-substrate edit).

---

## §8 Closure

**Status: APPLIED-AS-(A)-RESCOPE 2026-05-29.** Runtime plan v2.34 → v2.35 narrow-scope revision authored at same arc. Workspace `CLAUDE.md` §2.4 row bump co-published. Closure-back-reference annotation at v2.34 §0.3 owed at the impl arc PR.

H_T-RT-35 transit posture clarified honestly: stays PARTIAL post-v2.35 + post-impl-arc. RETIRE-READY transit gated on the upstream engine-layer impl arc (separate Class 1 back-flow owed at CP-axis design-phase routing — NOT authored at this fork doc).
