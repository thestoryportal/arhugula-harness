# Phase 7d Retirement Events — Batch 31

| Field | Value |
|---|---|
| Batch number | 31 |
| Filed at | 2026-05-28 (post mech-β test-fixture closure PR #14 merge at `24a9363` → `just retire-as-8d` green against real Anthropic on main; AC #7 e2e exercises operator-bound `SkillActivationHookConfig` + asserts `skill.activation` span emitted with all 6 AS spec v1.7 §14.4 attributes via per-LLM-dispatch hook firing site) |
| Filed by | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5; deployment-time opt-in gate closure per X-AL-2 second conjunct (operator-bound + real-substrate exercise) |
| Predecessor batch | `phase-7d-retirement-events-batch-30.md` (2026-05-28, 1 PARTIAL → RETIRE-READY → RETIRED joint single-batch transit for H_T-CP-11 via operator-discretion ratification of v1.6 MVP cascade_policy carve-out — sub-species 7 THIRD closure; cumulative 35/54 RETIRED + 2/54 RETIRE-READY + 4/54 PARTIAL + 11/54 STILL-BOUNDED + 2/54 STILL-BOUNDED-INDEFINITELY = 41/54 = 75.9% pipeline-advanced) |

---

## §0 Batch context

**Status type: 1 RETIRE-READY → RETIRED transit (H_T-AS-8d). Cumulative RETIRED count advances 35/54 → 36/54 (64.8% → 66.7%); RETIRE-READY count decrements 2/54 → 1/54 (OD-5 only — sibling closure routes to batch-32 same arc); PARTIAL count unchanged at 4/54; STILL-BOUNDED count unchanged at 11/54; STILL-BOUNDED-INDEFINITELY count unchanged at 2/54; pipeline-advanced 41/54 = 75.9% (unchanged — within-tier promotion RETIRE-READY → RETIRED). Cardinality check: 36 + 1 + 4 + 11 + 2 = 54 ✓.** EIGHTH RETIRE-READY → RETIRED close in ledger history (joins CP-16 batch-14, joint CP-18+AS-2 batch-16, CP-21 batch-17 corrective, joint CP-22 batch-18, CP-19 batch-22, CP-14 batch-29, CP-11 batch-30). **FIRST AS-axis deployment-time-opt-in-gate closure in ledger history** (CP-axis precedents at batches 14/16/17/18 + 22/29/30 are operator-discretion or single-deployment-surface scope; AS-8d is the first AS-axis row to ratify via the deployment-time-opt-in sub-species 7 pattern via real-LLM e2e proof). **AS-axis crosses 9/11 RETIRED at sub-row layer (81.8%)** + **active-substitution view 9/9 = 100.0% pipeline-advanced** (AS-8d transits OUT of RETIRE-READY into RETIRED at the active-substitution denominator; bucket-membership at active layer is now ZERO RETIRE-READY).

This batch records the deployment-time-opt-in-gate closure for **H_T-AS-8d** (skill.* 6-attribute observability namespace per AS spec v1.7 §14.4 / C-AS-15 §15.4; carriers U-RT-99 + U-RT-100 + U-RT-101 at runtime plan v2.28 L9-quindecies cluster; Meta-Architecture §5.2 row 6 sub-row d) from RETIRE-READY → RETIRED via PR #14 merge at single bundled arc:

| Commit | Artifact | Authority |
|---|---|---|
| `24a9363` | `harness-runtime/tests/integration/{conftest.py, test_track_b_e2e.py}` — `_FakeSpanContext` OTel `Span` surface completion (set_status / record_exception / add_event / end / get_span_context) enabling AC #7 to exercise the per-LLM-dispatch hook firing site end-to-end against real Anthropic | PR #14 squash-merge to main 2026-05-28 |
| (this commit) | `.harness/phase-7d-retirement-events-batch-31.md` (this file) — retirement event filing documenting Condition A + B (structural + operational + deployment-time opt-in) all MET | X-AL-2 second conjunct: operator-bound + real-substrate exercise |
| (this commit) | `harness-as/CLAUDE.md` §4.1 row RETIRE-READY → RETIRED transition for H_T-AS-8d; sub-row substitution-status table refresh | Workspace bookkeeping discipline per `.harness/phase-7d-retirement-ledger-v2.md` |
| (this commit) | `.harness/phase-7d-retirement-ledger-v2.md` §11.4d supersession entry adding H_T-AS-8d deployment-time-opt-in close at batch-31 | Forward-only ledger discipline per §0.5 |
| (this commit) | Memory entry `h-t-as-8d-retired-batch-31.md` documenting the deployment-time-opt-in-gate close pattern (first AS-axis member of sub-species 7) | Workspace memory discipline |

Per the operator-ratified runtime-only substitution-site reading at `.harness/phase-7d-retirement-ledger-v2.md` §2.1 + line-33 strict-reading discipline + the batch-16 §6 verification-shape sharpening discipline (ninth prospective application at batch-31):

> RETIRED = (criterion A MET) ∧ (criterion B structural-MET) ∧ (criterion B operational-MET) — where operational-MET requires all 3 binding-chain stages empirically verified: (1) carrier landed; (2) production span site / consumer site exists; (3) e2e exercise PASS against a real substrate exercising the contract semantic.

Under that discipline, H_T-AS-8d transitions RETIRE-READY → **RETIRED** via mech-β AC #7 green on main:

- **Criterion A** (cited unit IDs landed). MET pre-batch (batch-25): U-RT-99 + U-RT-100 + U-RT-101 (runtime plan v2.28 L9-quindecies cluster) per runtime spec v1.32 §14.17 C-RT-27 `SkillActivationSpanEmitter` + `SkillActivationHook` Protocol + 3 hook binding sites.
- **Criterion B structural-MET pre-batch (batch-25).** Factory-wired at `bootstrap/factories/skill_activation_emitter_factory.py`; 3 hook binding sites at production: per-LLM-dispatch (`lifecycle/llm_dispatch.py`), per-workflow-init (`harness-cp/.../workflow_driver.py`), operator-explicit (`HarnessContext.activate_skill`). Per-binding `activation_mode` value: `tool_search` / `frontmatter_only` / `filesystem_read` respectively per AS spec v1.7 §14.4.
- **Criterion B operational-MET at this batch.** Three binding-chain stages empirically verified:
  - Stage 1 (carrier landed) — `SkillActivationSpanEmitter` at `harness-runtime/src/harness_runtime/lifecycle/skill_activation.py` opens `skill.activation` span carrying all 6 AS spec §14.4 attributes (`skill.id` + `skill.name` + `skill.version_sha` + `skill.frontmatter.version` + `skill.body_tokens` + `skill.activation_mode`) + the `workflow.id` trace-context primitive.
  - Stage 2 (production consumer site) — Per-LLM-dispatch hook-2 firing at `lifecycle/llm_dispatch.py:330-351` pre-provider-resolution per C-RT-27 §14.17.2 invocation contract.
  - **Stage 3 (e2e exercise PASS against real substrate) — MET at this batch via mech-β AC #7 green on main.** `test_ac7_skill_activation_emits_skill_namespace_span` binds `SkillActivationHookConfig(hook=_TestHook())` at config + dispatches a real INFERENCE_STEP against `anthropic:claude-haiku-4-5` + asserts `_TestHook.select_for_llm_dispatch` fired with workflow-scope kwargs + asserts exactly one `skill.activation` span captured with all 6 §14.4 attrs + `workflow.id == "wf-ac7-skill-activation"`. The X-AL-2 second conjunct ("operator-bound + real-substrate exercise") is empirically MET — operator-supplied hook + real-LLM dispatch + production-emitted span observed.

**Deployment-time opt-in gate closure (sub-species 7 — first AS-axis member).** AS-8d entered RETIRE-READY at batch-25 (2026-05-28) per the "Terminal in-CLI state" framing — the production substrate is structurally complete + factory-wired, but the RETIRED transit explicitly required operator-bound `RuntimeConfig.skill_activation_hook_config` non-None at deployment plus e2e exercise observing the span at ≥1 hook site per X-AL-2 retirement criterion + runtime spec v1.32 §14.17.6 scope. PR #14 enables `just retire-as-8d` to run green against real Anthropic on main — this IS the deployment-time opt-in exercise (operator-supplied `_TestHook` ratifies the substrate; real LLM dispatches ratify the runtime path).

**Conclusion (preview):** **1 new RETIRED transition** (H_T-AS-8d) — cumulative **36/54 RETIRED** (66.7%, +1 from batch-30). RETIRE-READY count **2/54 → 1/54** (OD-5 carries forward — routes to batch-32 same arc same merge). PARTIAL count unchanged at **4/54**. Pipeline advanced unchanged at **41/54 = 75.9%** (within-tier promotion). **AS-axis crosses 9/11 = 81.8% RETIRED** at sub-row layer; **active-substitution view 9/9 = 100.0% pipeline-advanced** (RETIRE-READY bucket empty in active denominator after AS-8d transit). **EIGHTH RETIRE-READY → RETIRED close** in ledger history. **FIRST AS-axis deployment-time-opt-in-gate closure** in ledger. ZERO cross-axis cascade (intra-AS-axis only; ZERO production code change at the retirement arc itself; pure deployment-time opt-in gate close via mech-β e2e green proof).

---

## §1 H_T-AS-8d RETIRE-READY → RETIRED

### §1.1 Pre-transition state (batch-25, 2026-05-28)

Per `harness-as/CLAUDE.md` §4.1 line 172:

> H_T-AS-8d (skill.* 6-attribute observability namespace) | **RETIRE-READY** (operator-opt-in pattern, mirrors CP-18/CP-21/CP-22/RT-94 precedent) 2026-05-28 | Producer-binding chain LANDED at runtime spec v1.32 §14.17 NEW C-RT-27 + plan v2.28 L9-quindecies cluster (U-RT-99/100/101). ... **Terminal in-CLI state at RETIRE-READY 2026-05-28 (batch-25).** No further in-CLI close pathway. Full RETIRED gates on operator-bound `RuntimeConfig.skill_activation_hook_config` non-None + e2e exercise observing `skill.activation` span emission at ≥1 hook site per X-AL-2 retirement criterion + spec §14.17.6 scope. Bounded-residual carry per X-AL-2; not a defect.

The RETIRE-READY classification was the canonical terminal-in-CLI state for AS-8d pre-batch-31. The X-AL-2 second-conjunct closure required operator-bound deployment substrate AND real-substrate exercise; neither was exercisable from CLI scope without `ANTHROPIC_API_KEY` + the test-fixture closure (the `_FakeSpanContext` OTel surface was incomplete pre-PR-#14 — `set_status` / `record_exception` / `add_event` / `end` / `get_span_context` all missing — and propagated as `AttributeError` through the retry-loop, exhausting the fallback chain, failing the workflow before reaching the skill-activation span assertion).

### §1.2 Closure event (mech-β AC #7 green on main, 2026-05-28)

PR #14 merge at `24a9363` (2026-05-28, post `0850278` SKILLS fixture merge) completed the `_FakeSpanContext` OTel `Span` API surface at `harness-runtime/tests/integration/conftest.py`:

| Method | Surface | Production-site consumer |
|---|---|---|
| `set_status` | No-op shim | `hitl_gate_composer.py:1138` + `validator_escalation_composer.py:246` |
| `record_exception` | No-op shim | Sibling to `set_status` at audit-compose-failure path |
| `add_event` | No-op shim | `retry_breaker_fallback.py:329` (`fallback.exhausted`) + per-step lifecycle |
| `end` | No-op shim | Explicit-end paths outside `with` blocks |
| `get_span_context` | Returns `_FakeSpanContextHandle(span_id=int, is_valid=True)` | `_format_span_id_hex` at retry-instrumentation site |

With the surface complete, `just retire-as-8d` (`uv run pytest harness-runtime/tests/integration/test_track_b_e2e.py::test_ac7_skill_activation_emits_skill_namespace_span -v`) executes the operator-supplied `_TestHook` against real Anthropic and observes:

- `_TestHook.select_for_llm_dispatch` fires with `workflow_id="wf-ac7-skill-activation"` + `step_index=0`
- Exactly one `skill.activation` span captured at `FakeTracerProvider.spans`
- Span attributes: `skill.id == "ac7-test-skill"` + `skill.name == "AC7 Test Skill"` + `skill.activation_mode == "tool_search"` + `skill.frontmatter.version == "1.0.0"` + `skill.version_sha` present + `skill.body_tokens` present + `workflow.id == "wf-ac7-skill-activation"`

This satisfies the X-AL-2 second conjunct verbatim: operator-bound substrate (operator-supplied hook) + real-substrate exercise (real Anthropic LLM dispatch) + production-emitted span observed (`skill.activation` with full 6-attr §14.4 set).

### §1.3 Binding-chain stage verification (batch-31 close)

| Stage | Required evidence | Verified at | Verification shape |
|---|---|---|---|
| 1. Carrier landed | `SkillActivationSpanEmitter` + `SkillActivationHook` Protocol + `SkillActivationHookConfig` dataclass + `SkillManifest` 2-field extension | U-RT-99 + U-RT-100 (runtime plan v2.28) | `harness-runtime/src/harness_runtime/lifecycle/skill_activation.py`; full v1.32 §14.17 schema |
| 2. Production consumer site | Per-LLM-dispatch hook-2 firing site + factory-wiring at stage-5 LOOP_INIT | U-RT-100 + U-RT-101 | `lifecycle/llm_dispatch.py:330-351` + `bootstrap/factories/skill_activation_emitter_factory.py` |
| 3. E2E exercise PASS against real substrate | Operator-supplied hook + real Anthropic LLM dispatch + `skill.activation` span emitted with full 6 §14.4 attrs | mech-β AC #7 green at PR #14 merge `24a9363` (this batch) | `test_ac7_skill_activation_emits_skill_namespace_span` PASS at `just retire-as-8d` (operator-bound exercise on main) |

**All 3 stages empirically MET.** Per [[verification-shape-sharpened-grep-vs-e2e]] discipline this is RETIRED at the C-RT-27 contract surface — binding chain structurally + operationally complete via deployment-time opt-in exercise.

### §1.4 Cross-axis cascade verification

ZERO cross-axis cascade verified empirically at the close arc:

- **Retirement-audit ratification scope**: Documentation-only (this batch filing + harness-as/CLAUDE.md row bump + ledger v2 + memory entry). ZERO production code change at the retirement arc itself; PR #14 was test-side fixture completion + one test-typo fix (`retry.attempt.number` → `retry.attempt_number`) — production code unchanged.
- **Spec scope**: ZERO spec amendment — runtime spec v1.32 §14.17 already declares the operator-opt-in retirement scope at §14.17.6 (Q5=β NO new CXA edge per Reading B Q-set ratification 2026-05-28).
- **CXA v2.15 + AS spec v1.7 + OD spec v1.24 + CP spec v1.24 unchanged**. The `skill.*` namespace is AS-axis-owned + intra-axis (no cross-axis edge per Q5=β at filing arc).

### §1.5 Sibling row impact (AS-axis post-batch-31)

| Row | Status (post batch-25) | Status (post batch-31) | Reason |
|---|---|---|---|
| H_T-AS-1 / AS-2 / AS-4 / AS-5 / AS-8a / AS-8b / AS-8c / AS-9 | RETIRED (8) | Unchanged | — |
| H_T-AS-8d | **RETIRE-READY** | **RETIRED** | **This batch — deployment-time opt-in gate closed via mech-β AC #7 green on main** |
| H_T-AS-8e / AS-8f | STILL-BOUNDED-INDEFINITELY (2) | Unchanged | — |

**AS-axis cumulative post-batch-31 (ledger-v2 sub-row layer):** **9 / 11 RETIRED (81.8%, +1 from batch-26 baseline)** + **0 / 11 RETIRE-READY (bucket EMPTY)** + **0 / 11 PARTIAL** + **2 / 11 STILL-BOUNDED-INDEFINITELY (18.2%, AS-8e + AS-8f)**. **Active substitutions (excluding both INDEFINITE deferrals): 9 / 9 = 100.0% RETIRED.** Pipeline advanced raw (R+RR+P): **9/11 = 81.8%** (unchanged — within-tier transit). **AS-axis becomes the second axis after IS-axis to clear the active-substitution RETIRE-READY bucket completely at the ledger-v2 sub-row layer.** **Meta-Arch §2.2 view preserved verbatim** (6 AS rows; AS-8 monolithic NOT decomposed at design-declaration layer per X-AL-3).

---

## §2 Sub-species 7 catalogue — FIRST AS-axis member (deployment-time-opt-in-gate variant)

Pattern members across batches 10–31: **10 historical members** (CP-16, CP-18, AS-2, CP-21, CP-22, AS-4, CP-19, CP-14, CP-11, AS-8d); **9 RETIRED** (all of the above except OD-5 which is the sibling closure routed to batch-32 same arc).

**Sub-species 7 catalogue post-batch-31 lineage discriminator refinement:**

- **7.operator-discretion-ratification-at-spec-explicit-path** (CP-19 batch-22 + CP-14 batch-29 + CP-11 batch-30) — three closures via spec-explicit operator-discretion language (runtime spec v1.6 §14.7.2 step 5 carve-out language + CP-19 in-process reframe at fork ratification).
- **7.deployment-time-opt-in-gate** (AS-8d batch-31) — FIRST member at this batch. Distinct closure shape: substrate is structurally complete + factory-wired, but RETIRED transit requires operator-bound deployment config substrate AND real-substrate exercise (X-AL-2 second conjunct two-step gate). Closure event is a green real-LLM e2e test on main, not a spec-section ratification.

Common-ancestor: both sub-species are *X-AL-2-second-conjunct closures requiring operator-bound deployment substrate*. Distinct closure-event-class: spec-explicit-path (operator AskUserQuestion + spec section invocation) vs deployment-time-opt-in-gate (test-fixture closure + real-substrate exercise on main).

**Pattern catalogued — deployment-time-opt-in-gate sub-species: substrate-complete RETIRE-READY rows close on the FIRST green real-substrate e2e exercise observation, NOT on spec-section ratification.** The closure event is empirical, not interpretive — once the operator-bound real-substrate exercise observes the production-emitted span, the X-AL-2 second conjunct is mechanically MET. No operator AskUserQuestion required because the criterion is empirically discriminable (test green / test red).

---

## §3 Adjacent observations

(a) **Test-fixture closure was the operational unblock.** Pre-PR-#14 the `_FakeSpanContext` lacked OTel `Span` surface; AC #7 reached the skill-activation span assertion via real Anthropic but exhausted the fallback chain on `AttributeError` propagation through the retry-loop. Production code at `lifecycle/llm_dispatch.py:330-351` + `lifecycle/skill_activation.py:225-237` was unchanged across the retirement arc. The retirement criterion gate closed via test-substrate completion enabling empirical observation of the always-correct production emission.

(b) **`just retire-as-8d` recipe is the canonical deployment-time-opt-in-gate operator command.** `mech-beta` ran 4/4 green pre-filing; the operator-design intent at the justfile (`retire-as-8d`/`retire-od-5` named after the retirement targets) is for AC #7 green = AS-8d RETIRED. This batch ratifies that intent verbatim.

(c) **Sibling closure OD-5 routes to batch-32 same arc same merge.** PR #14 enables BOTH `just retire-as-8d` AND `just retire-od-5` to pass on main (AC #7 + AC #8 fixture both repaired in the same PR). OD-5 closure (deployment-time-opt-in-gate sub-species — second member after AS-8d) files at batch-32 as a separate event-doc per per-row close discipline + ledger-v2 §11.4 per-row supersession discipline.

(d) **`harness-as/CLAUDE.md` §4.1 RETIRED-row footnote shape**: align with CP-axis precedents at batch-22 CP-19 + batch-29 CP-14 + batch-30 CP-11 — close-event + commit cite (PR #14 / `24a9363`) + retirement-criterion gate (X-AL-2 second conjunct via mech-β AC #7 green on main) + scope note (operator-bound `_TestHook` + real Anthropic at justfile-bound `retire-as-8d` recipe).

(e) **`harness-as/CLAUDE.md` §1.3 substitution-mechanism enumeration row remains canonical post-batch-31 at the RETIRED row.** Substitution-mechanism enumeration is invariant across retirement-state machine per batch-21 §3(d) + batch-22 §3(g) + batch-29 §3(f) + batch-30 §3(e) precedent.

(f) **Workspace `CLAUDE.md` retirement count line refresh owed.** Per workflow v1.12 §7.4.7.3.C retirement-tier-transit audit (NEW canonicalization at v1.12, this session's THIRD §7.4.7.3.B session-resumption application): the workspace `CLAUDE.md` cumulative-counts line MUST refresh in lockstep with the per-axis CLAUDE.md row update at any retirement-tier transit. This batch + batch-32 are JOINT transit events; the workspace line bumps once at batch-32 close to reflect the combined `35/54 → 37/54 RETIRED` + `2/54 → 0/54 RETIRE-READY` deltas.

(g) **NO new fork doc filed.** The closure event is a test-substrate completion + real-substrate exercise; the X-AL-2 second conjunct is empirically discriminable. The pre-existing fork doc at `.harness/class_1_fork_as_8d_skill_activation_surface_absence.md` Reading B Q-set (operator-ratified 2026-05-28) is the canonical authority for the apply-arc (batch-25); this batch closes the RETIRE-READY → RETIRED transit per the same authority anchor.

(h) **Adversarial review not run.** This batch lands the close in single-session arc with ZERO production code change at the retirement arc itself. Adversarial review pass deferred to operator-discretion follow-on arc.

(i) **Memory anchor write owed.** NEW memory entry `h-t-as-8d-retired-batch-31.md` documenting the deployment-time-opt-in-gate close pattern (FIRST sub-species 7 closure of this variant) + cross-link to `[[h-t-od-5-retired-batch-32]]` (sibling closure same arc) + `[[fork-as-8d-skill-activation-production-only-surface]]` (apply-arc authority anchor).

(j) **NEW sub-species refinement at this batch: 7.deployment-time-opt-in-gate as distinct closure-event-class.** Distinct from 7.operator-discretion-ratification-at-spec-explicit-path (CP-19/CP-14/CP-11). Distinguishing characteristic: the closure event is mechanically discriminable (test green/red), not interpretive (spec-section invocation). Operator AskUserQuestion route not required for closure event identification. The sub-species refinement is a strengthening candidate for workflow v1.12 §7.4.7.2 species-7 sub-species enumeration extension.

---

## §4 Filing footer

| Field | Value |
|---|---|
| Batch | 31 |
| Cumulative RETIRED | 36/54 (66.7%) — IS:7 + AS:9 + CP:17 + OD:2 + CXA:1 |
| Cumulative RETIRE-READY | 1/54 (1.9%) — OD-5 (routes to batch-32 same arc) |
| Cumulative PARTIAL | 4/54 (7.4%) — CP-8 + CP-9 + CP-17 + OD-6 |
| Cumulative STILL-BOUNDED | 11/54 (20.4%) — IS:2 (IS-2 + IS-4) + CP:2 (CP-12 + CP-23) + OD:4 (OD-1/3/4/7) + CXA:3 |
| Cumulative STILL-BOUNDED-INDEFINITELY | 2/54 (3.7%) — AS-8e + AS-8f |
| Cumulative pipeline-advanced (R + RR + P) | 41/54 (75.9%) |
| Cardinality check | 36 + 1 + 4 + 11 + 2 = 54 ✓ |
| New RETIRED transitions | 1 (H_T-AS-8d RETIRE-READY → RETIRED via mech-β AC #7 green on main at PR #14 merge `24a9363`) |
| New RETIRE-READY transitions | 0 |
| Filed as | `phase-7d-retirement-events-batch-31.md` |
| Co-published bookkeeping | `harness-as/CLAUDE.md` §4.1 row RETIRE-READY → RETIRED; `.harness/phase-7d-retirement-ledger-v2.md` §11.4d supersession entry; memory entry `h-t-as-8d-retired-batch-31.md` |
| Predecessor | `phase-7d-retirement-events-batch-30.md` |
| Date | 2026-05-28 |
