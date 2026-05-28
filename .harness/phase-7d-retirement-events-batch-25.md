# Phase 7d Retirement Events — Batch 25

| Field | Value |
|---|---|
| Batch number | 25 |
| Filed at | 2026-05-28 (post H_T-AS-8d STILL-BOUNDED → RETIRE-READY transit at C-RT-27 SkillActivationSpanEmitter apply arc; same-session ~3-hour cluster after AS-8d Class 1 fork filing + ratification + apply at commits `20a4fe5` / `f780ef8` / `471e0e2` / `83251b2` / `6ca6572` + U-RT-101 e2e at this arc) |
| Filed by | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5; X-AL-2 criterion empirically MET via U-RT-101 e2e binding-chain materialization + ≥1 hook-site span emission observation per `tests/integration/test_u_rt_101_skill_activation_binding_chain.py::test_skill_activation_e2e_opt_in_with_hook_branch` |
| Predecessor batch | `phase-7d-retirement-events-batch-24.md` (2026-05-28, AS-8 monolithic → 6-sub-row decomposition + 3 immediate sub-RETIRED transits AS-8a/b/c; cumulative 33/54 = 61.1%) |

---

## §0 Batch context

**Status type: 1 STILL-BOUNDED → RETIRE-READY transit (H_T-AS-8d).** Closure-event-class: producer-binding-chain MET + ≥1-hook-site empirical-emission observation MET per fork §14.17.6 retirement criterion + spec v1.32 §14.17.5 invariants. Reading B operator-opt-in shape per `.harness/class_1_fork_as_8d_skill_activation_surface_absence.md` Q1=(B) ratification 2026-05-28.

**Distinction from AS-8a/b/c batch-24 transits:** AS-8a/b/c were *direct* PARTIAL-ADVANCE → RETIRED transits at ledger-v2-layer decomposition (criteria MET pre-decomp; close at decomp event). AS-8d at batch-25 transits STILL-BOUNDED → RETIRE-READY (operator-opt-in pattern; structural-criterion-B MET via factory wiring; full RETIRED gates on operator deployment-time activation hook supply per fork §14.17.6 + plan v2.28 U-RT-101 AC #8). Mirrors CP-18 / CP-21 / CP-22 / RT-94 RETIRE-READY precedent.

**Counting math (ledger-v2-layer post-batch-24):**

Pre-batch-25:
- AS-axis ledger v2: 7/10 RETIRED (AS-1/2/4/5 + AS-8a/8b/8c) + 3/10 STILL-BOUNDED (AS-8d / AS-8e indefinite / AS-8f) — AS-9 authoring-only out of ledger
- Workspace ledger cumulative: 33/54 RETIRED = 61.1%

Post-batch-25 (AS-8d STILL-BOUNDED → RETIRE-READY):
- AS-axis ledger v2: 7/10 RETIRED + **1/10 RETIRE-READY (AS-8d)** + 2/10 STILL-BOUNDED (AS-8e indefinite / AS-8f)
- Workspace ledger cumulative: 33/54 RETIRED + **1/54 RETIRE-READY (AS-8d)** + 5/54 PARTIAL + 15/54 STILL-BOUNDED
- Pipeline-advanced (R + RR + P): 33 + 1 + 5 = **39/54 = 72.2%** (up from 38/54 = 70.4% post-batch-24)

**AS-axis active-substitution view (excluding AS-8e STILL-BOUNDED-INDEFINITELY per Files arc deferral):**
- 7/9 RETIRED + 1/9 RETIRE-READY (AS-8d) + 1/9 STILL-BOUNDED (AS-8f) = 8/9 = 88.9% pipeline-advanced

**No new design-substrate edits at batch-25.** AS-spec / Runtime-spec / CP-spec / OD-spec / CXA / ADR / ADD / PRD / harness-* CLAUDE.md updates landed at the apply-arc commits (`471e0e2` + `83251b2` + `6ca6572`) — batch-25 is the retirement-event filing layer ONLY.

---

## §1 Retirement event — H_T-AS-8d STILL-BOUNDED → RETIRE-READY

**Substitution identity:** H_T-AS-8d (`skill.*` 6-attribute observability namespace producer-site at H_T runtime).

**Pre-batch state (post-batch-24 / ledger v2):** STILL-BOUNDED. Gate-text: "No producer site at `harness-runtime/src/`. Gates on Skills loading runtime composer + `SkillActivationSpanEmitter` carrier authoring (NEW H_T primitive; ~3-5 commits scope)."

**Closure-event lineage:**
1. Fork doc filing — `.harness/class_1_fork_as_8d_skill_activation_surface_absence.md` filed 2026-05-28 at commit `20a4fe5` per `[[advisor-before-substantive-work-for-cross-axis-blockers]]` posture (24th application). 4 gaps catalogued (Gap 1 no producer site / Gap 2 3-of-6 attributes uncomputed / Gap 3 no activation event at H_T / Gap 4 Claude Code taxonomy untransplanted).
2. Operator ratification — AskUserQuestion 2026-05-28 same-session as filing. Q1=(B) IN-SCOPE-MVP + Q2=(d) HYBRID all 3 hooks + Q3=(i) PRESERVE Claude Code taxonomy + Q4=(q) NEW module per Memory-tool precedent + Q5=(β) NO new CXA edge. Status RATIFIED at commit `f780ef8`.
3. Apply arc (3 commits) — spec v1.31 → v1.32 NEW §14.17 C-RT-27 + AS v1.7 §14.4 footer + runtime plan v2.27 → v2.28 NEW L9-quindecies cluster (U-RT-99/100/101) at `471e0e2`; harness-runtime + harness-cp production binding + 16 NEW unit tests at `83251b2`; CLAUDE.md row bumps + AS-8d STILL-BOUNDED → RETIRE-READY at `6ca6572`.
4. e2e closure arc — U-RT-101 real-bootstrap e2e at `tests/integration/test_u_rt_101_skill_activation_binding_chain.py` (4 tests covering opt-out / opt-in-no-hook / opt-in-with-hook / joint-with-other-bindings); FakeTracerProvider extended with `get_tracer` + span capture surface; ≥1 hook-site empirical span emission observation MET at the opt-in-with-hook test (operator-explicit `ctx.activate_skill(...)` emits one `skill.activation` span carrying all 6 AS spec v1.7 §14.4 attributes + `activation_mode = filesystem_read`).

**Post-batch state:** **RETIRE-READY** (operator-opt-in pattern; structural-criterion-B MET via factory wiring + 3 hook surfaces at production + ≥1-hook-site e2e emission observation).

**Verification-shape applied (per `[[verification-shape-sharpened-grep-vs-e2e]]`):** Empirical e2e against real `run_bootstrap` orchestrator (not `_FakeCtx` or `_MutableHarnessContext` test-local shortcuts); stage-5 LOOP_INIT bucket invokes `materialize_skill_activation_emitter_stage` with the real factory; the test asserts (a) binding-chain post-conditions for all 3 opt-out / opt-in-no-hook / opt-in-with-hook branches, (b) ≥1 hook-site empirical span emission with all 6 AS spec §14.4 attributes verified at the captured span, (c) joint-binding substrate orthogonality with validator_framework_config / pause_resume_protocol_config / webhook_delivery_composer_config siblings.

**Plan AC #8 ↔ fork §14.17.6 divergence disposition:** Plan v2.28 U-RT-101 AC #8 prescribes "all 3 hook sites emit skill.activation spans" (stricter scope). Fork doc §14.17.6 retirement criterion requires "≥1 hook site" emission. The e2e exercises operator-explicit hook-3 emission; per-LLM-dispatch (hook-2) + per-workflow-init (hook-1) firings require workflow-execution-loop coverage which exceeds the binding-chain e2e scope at U-RT-101. The X-AL-2 criterion is MET via hook-3; the AC #8 full-3-hook coverage is deferred to a follow-on workflow-execution e2e arc per spec §14.17.7 deferred-discretion. Sub-species candidate: **plan-AC-stricter-than-fork-criterion** — distinct from prior species 7 sub-species in workspace history; characteristic of Reading B operator-opt-in landings where plan ACs document the full-coverage target but X-AL-2 retirement criterion accepts the structural-only-MET shape.

**Full RETIRED gate** (RETIRE-READY → RETIRED at a future batch):
1. Operator deployment binds `RuntimeConfig.skill_activation_hook_config` non-None with concrete `SkillActivationHook` Protocol implementation
2. Production deployment exercises ≥1 hook site at workflow runtime (operator-explicit `ctx.activate_skill` OR automatic workflow-init / LLM-dispatch hook activation observed against real workflow execution)
3. Real `skill.activation` spans observed at the production tracer backend (Honeycomb / OTel collector / etc.) carrying the 6-attribute namespace

**No cross-axis cascade.** Per Q5=(β) ratification at fork doc: CXA v2.15 unchanged; AS spec §14.4 attribute SET preserved verbatim; CP / OD / ADR / ADD / PRD unchanged.

---

## §2 AS-axis cumulative post-batch-25

| Status | Count | Substitutions |
|---|---|---|
| RETIRED | 7/10 | AS-1 + AS-2 + AS-4 + AS-5 + AS-8a + AS-8b + AS-8c (+ AS-9 authoring-only outside ledger v2 → 8/11 if counted) |
| **RETIRE-READY** | **1/10** | **AS-8d (this batch)** |
| STILL-BOUNDED | 2/10 | AS-8e (INDEFINITELY per Files arc deferral) + AS-8f (managed_agents — open multi-commit arc) |

**Pipeline-advanced (R + RR + P):** 8/10 = 80.0% (was 7/10 = 70.0% post-batch-24).

**Active-substitution view (excluding AS-8e INDEFINITE):** 7/9 RETIRED + 1/9 RETIRE-READY = 8/9 = **88.9% pipeline-advanced** (was 7/9 = 77.8% post-batch-24).

---

## §3 Workspace cumulative post-batch-25

| Status | Count (54 ledger-v2 rows) | Δ vs batch-24 |
|---|---|---|
| RETIRED | 33/54 (61.1%) | unchanged |
| **RETIRE-READY** | **1/54 (1.9%)** | **+1 (AS-8d this batch)** |
| PARTIAL | 5/54 (9.3%) | unchanged |
| STILL-BOUNDED | 15/54 (27.8%) | -1 (AS-8d transit) |

**Pipeline-advanced (R + RR + P):** 39/54 = **72.2%** (was 38/54 = 70.4% post-batch-24; +1.8 percentage points).

---

## §4 Substrate-edits map

- `harness-as/CLAUDE.md` AS-8d row — **RETIRE-READY** with cite to runtime spec v1.32 §14.17 + producer-binding chain at `harness-runtime/src/harness_runtime/lifecycle/skill_activation.py` + 3 hook binding sites enumerated (already landed at apply-arc commit `6ca6572` — verification-only at batch filing)
- `harness-as/CLAUDE.md` AS-axis cumulative line — 8/11 RETIRED + 1/11 RETIRE-READY (AS-8d) + 0 PARTIAL + 2 STILL-BOUNDED (AS-8e + AS-8f) (already landed at commit `6ca6572`)
- `CLAUDE.md` (workspace) §2.3 Runtime spec row v1.31 → v1.32 (already landed at commit `6ca6572`)
- `CLAUDE.md` (workspace) §2.4 Runtime plan row v2.27 → v2.28 (already landed at commit `6ca6572`)
- This batch-25 retirement event file — NEW at this commit

ZERO substrate-edit at AS spec / CP spec / OD spec / CXA / ADR / ADD / PRD / IS spec / IS plan / OD plan / CP plan / AS plan / `harness-cp/CLAUDE.md` / `harness-od/CLAUDE.md` / `harness-is/CLAUDE.md` / `harness-cxa/CLAUDE.md` / Meta-Arch (§2.2 AS-axis substitution count preserved verbatim per X-AL-3 + batch-24 §0 framing).

---

## §5 Adjacent observations

(a) **Same-session 5-commit Class 1 fork lifecycle.** AS-8d fork doc filing → operator ratification → spec+plan amendments → impl+tests → e2e + retirement event all landed within a single session 2026-05-28. Mirrors `class_1_fork_h_t_cp_19_default_gate_level_spec_extension.md` 3-arc single-day precedent (2026-05-27); AS-8d at 5 commits is slightly heavier than h_t_cp_19's 3 commits due to Q2=(d) hybrid 3-hook scope. Pattern reinforced: well-scoped Reading B operator-opt-in arcs CAN land same-session when (i) advisor pre-substantive consultation sharpens the Q-set + (ii) the apply arc has clear precedent (CP-22 / RT-94 binding-chain shape) + (iii) operator AskUserQuestion ratification is single-round.

(b) **Plan AC #8 ↔ fork §14.17.6 retirement criterion divergence.** Plan v2.28 U-RT-101 AC #8 prescribes full-3-hook e2e coverage; fork §14.17.6 retirement criterion accepts ≥1-hook coverage. e2e at U-RT-101 satisfies ≥1 (operator-explicit hook-3); full-3-hook deferred to follow-on workflow-execution-e2e arc (per-LLM-dispatch + per-workflow-init firings require workflow loop). Class 3 informational divergence; not patched at batch-25 per FM-2.

(c) **FakeTracerProvider extension at integration conftest.** U-RT-101 e2e required `FakeTracerProvider.get_tracer(...)` surface which was absent at the pre-batch-25 fixture. Extended with minimal `_FakeTracer` + `_FakeSpanContext` shim (capture-only; no tracing semantics). Mirrors `_FakeTracerProvider` shape at `harness-runtime/tests/test_shutdown.py:51` (private to that test file). The extension at `tests/integration/conftest.py` is reusable across future integration tests that need tracer surface — sibling-shape to providers + daemon fakes. Sub-species candidate: **test-fixture-extension-at-emitter-landing** — distinct from prior sub-species; characteristic of e2e closure arcs where emitter contracts require tracer surface that test fixtures previously didn't need.

(d) **MVP `body_tokens` heuristic disposition.** Plan v2.28 U-RT-99 AC #6 + spec §14.17.7 deferred-discretion: `body_tokens` computed via `len(description) // 4` MVP heuristic. Real-workflow body-token computation (full SKILL.md body read) is owed at a follow-on arc — cost-attribution accuracy at production deployment depends on the correct denominator. Class 3 informational; documented at e2e test docstring + spec §14.17.7 + plan U-RT-99 AC #6 MVP-shape acknowledgement. Not patched at batch-25.

(e) **AS-axis crosses 80% pipeline-advanced + 88.9% active-substitution.** Post-batch-25 AS-axis is the second axis (after IS-axis) to cross 80% pipeline-advanced threshold at the workspace ledger view. The remaining gaps are AS-8e (indefinite — Files arc) + AS-8f (managed_agents — open multi-commit fork). AS-8f is the natural next AS-axis arc but is genuinely fresh-session shape per advisor stop-point at U-RT-101 closure.

---

## §6 Filing footer

| Field | Value |
|---|---|
| Filed at commit | TBD (this commit) |
| Filed by | `phase-7-substitution-retirement` skill §3.2 |
| Verification source | `harness-runtime/tests/integration/test_u_rt_101_skill_activation_binding_chain.py` 4/4 PASS @ commit-this-arc; harness-runtime 1114/1114 + 4 skipped; harness-cp 708/708; harness-as 317/317 |
| Predecessor lineage | `phase-7d-retirement-events-batch-24.md` (2026-05-28 ledger-v2-layer decomposition + AS-8a/b/c immediate close) |
| Successor candidate | AS-8f managed_agents Class 1 fork filing arc (fresh-session shape); OR AS-8d RETIRE-READY → RETIRED at production deployment-time gate |
| Status | ✅ FILED |
