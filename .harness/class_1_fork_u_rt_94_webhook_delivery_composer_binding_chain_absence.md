# Class 1 Fork — U-RT-94 `ctx.webhook_delivery_composer` binding-chain absence

**Filing event.** Phase 7 sub-phase 7b — `phase-7-implementation` skill arc impl(U-RT-94) HALT-on-discovery, 2026-05-24, post AC #9 carrier-landing commit `ba072f4`.

**Filing operator.** `phase-7-implementation` skill execution per `phase-7-back-flow-routing` discipline.

**Routing classification.** Class 1 (halt-execution; design-phase artifact requires revision) per `Project_Workflow_v1_8.md` §2.7.6 + workspace `CLAUDE.md` §4.3.

**Authority basis for halt.** `phase-7-implementation` SKILL.md §6 halt condition: "Plan signature cannot be materialized at target stack" — runtime spec v1.24 §14.8.8.1 step 3 + v1.25 carryover names `ctx.webhook_delivery_composer.deliver_webhook(brief, idempotency_key)` as the architectural consumption site; empirical-grep at HEAD `ba072f4` confirms NO HarnessContext field, NO `_REQUIRED_FIELDS` entry, NO stage-5 materialize call, NO `_MutableHarnessContext` field, NO `freeze()` wiring. `WebhookDeliveryComposer` carrier class landed at U-RT-69 (`harness-runtime/src/harness_runtime/lifecycle/webhook_delivery_composer.py`) but the production binding chain (HarnessContext field + stage-5 factory + builder + freeze) was never authored.

This is identical-shape to the resolved fork `[[fork-validator-composer-arc-stage-4-absence]]` (filed at `.harness/class_1_fork_validator_composer_arc_stage_4_absence.md`) which required:
- Spec v1.18 §14.13 NEW C-RT-23 `materialize_validator_framework_stage` stage-4 OD-bucket factory
- Plan v2.17 NEW L9-decies cluster (U-RT-83/84/85) decomposing the binding chain
- Impl arc 3 commits (U-RT-83 RuntimeConfig + U-RT-84 factory + U-RT-85 e2e)

**Silent absorption foreclosed.** Per X-AL-3 (Meta-Architecture §7.7) + workspace `CLAUDE.md` §4.3: "silent absorption of design-phase defects is the worst failure mode." Continuing impl(U-RT-94) with inline scope expansion (adding 4 new fields to `RuntimeHITLGateComposer` constructor + materializing `WebhookDeliveryComposer` at stage-5 + extending HarnessContext field-set + extending `_REQUIRED_FIELDS`) would silently extend H_T at Phase 7 execution — exactly the anti-pattern X-AL-3 forecloses.

---

## §1 — Empirical-verification details

### §1.1 Spec-side claims (runtime spec v1.24 §14.8.8.1 step 3, preserved verbatim at v1.25)

> §14.8.8.1 step 3 — `await ctx.webhook_delivery_composer.deliver_webhook(brief, idempotency_key)` per C-RT-20 §14.10.1; returns `WebhookDeliveryResult`.

Spec §14.8.8.6 composition claim:

> The §14.8.8 durable-async branch composes existing v1.23 surfaces (C-RT-20 WebhookDeliveryComposer at U-RT-69; C-RT-24 PauseResumeProtocol stage at L9-undecies) — NO new HarnessContext field at §3+§4 layer per Q4 (b-revised).

Plan v2.23 §0 change-note (preserved at v2.24):

> Cluster-boundary edges to already-landed substrate (C-RT-20 WebhookDeliveryComposer at U-RT-69; C-RT-24 PauseResumeProtocol stage at L9-undecies)

### §1.2 Empirical reality

**Grep verification at HEAD `ba072f4`** (worktree `worktree-hitl-pause-trigger`):

```
$ grep -rn "webhook_delivery_composer\|WebhookDeliveryComposer" harness-runtime/src/harness_runtime/types.py
(no matches)

$ grep -rn "webhook_delivery_composer" harness-runtime/src/harness_runtime/bootstrap/
(no matches)

$ grep -rn "WebhookDeliveryComposer" harness-runtime/src/
harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py:153:from harness_runtime.lifecycle.webhook_delivery_composer import (
harness-runtime/src/harness_runtime/lifecycle/webhook_delivery_composer.py:33:    "WebhookDeliveryComposer",
harness-runtime/src/harness_runtime/lifecycle/webhook_delivery_composer.py:37:    "materialize_webhook_delivery_composer_stage",
harness-runtime/src/harness_runtime/lifecycle/webhook_delivery_composer.py:94:class WebhookDeliveryComposer:
```

**Findings:**
- `WebhookDeliveryComposer` class exists at `lifecycle/webhook_delivery_composer.py:94` (U-RT-69 landing).
- `materialize_webhook_delivery_composer_stage` factory exists at `lifecycle/webhook_delivery_composer.py:262`.
- The factory is NOT invoked anywhere in `harness-runtime/src/harness_runtime/bootstrap/` (no stage-N module calls it).
- `HarnessContext` (`types.py:1140`) does NOT declare a `webhook_delivery_composer` field.
- `_MutableHarnessContext` (`bootstrap/mutable_context.py:153`) does NOT declare a `webhook_delivery_composer` field.
- `_REQUIRED_FIELDS` (`bootstrap/mutable_context.py:110`) does NOT include `webhook_delivery_composer`.
- `freeze()` (`bootstrap/mutable_context.py:307`) does NOT propagate `webhook_delivery_composer`.

**Conclusion:** `ctx.webhook_delivery_composer` does NOT exist on HarnessContext. The production binding chain is absent. U-RT-69 landed the *carrier class* but not the *binding chain* — analogous to U-RT-83 (ValidatorFrameworkConfig empty-marker) landing without U-RT-84 (factory + HarnessContext field + bootstrap wiring) prior to the validator-composer Reading A absorption at batch-17.

---

## §2 — Adjacent finding: U-RT-93 helper unreachability in production

**Surfaced at impl(U-RT-93) landing `2cfc5dc`; documented here per advisor recommendation to keep related findings in one fork doc.**

### §2.1 Spec-side claim (runtime spec v1.24 §14.8.8.3, preserved at v1.25)

> `def _evaluate_cell_synchrony_tolerant(binding: StepEffectiveBinding | None) -> SynchronyClass | None` — returns `matrix_cell_for(binding.persona_tier, binding.engine_class).synchrony_class` per CP spec v1.2 §18.1 (preserved through v1.16); `None` when binding is None.

Scoping doc claim (`.harness/hitl_gate_as_pause_trigger_composition_scoping.md` §0(C)):

> Q4 (b-revised) `StepEffectiveBinding` already carries `binding.persona_tier+binding.engine_class` (existing CP-side carrier at `harness-cp/.../per_step_override_evaluator.py:117`)

### §2.2 Empirical reality

**Grep verification at HEAD `ba072f4`:**

```
$ grep -n "^class StepEffectiveBinding\|^    [a-z_]\+:" harness-cp/src/harness_cp/per_step_override_evaluator.py
117:class StepEffectiveBinding(BaseModel):
126:    step_id: str
127:    model_binding: ModelBinding
130:    engine_class: EngineClass
131:    hitl_placement: HITLPlacement | None = None
132:    override_applied: bool
133:    override_audit_ref: LedgerEntryRef | None = None
```

**Findings:**
- `StepEffectiveBinding.engine_class` IS declared.
- `StepEffectiveBinding.persona_tier` is NOT declared (frozen + `extra="forbid"` per `model_config = ConfigDict(extra="forbid", frozen=True)`).
- Production callers at `harness-runtime/tests/test_lifecycle_runtime_tool_dispatcher.py:138` construct `StepEffectiveBinding(step_id, model_binding, engine_class, override_applied)` with no `persona_tier`.
- Existing `_evaluate_hitl_required_tolerant` (helper sibling at `hitl_gate_composer.py:253`) uses `getattr(binding, "persona_tier", None)` and falls back to a default when missing — i.e., production code does NOT expect `persona_tier` on `StepEffectiveBinding`.
- The existing matrix-cell-resolution callsite at `hitl_gate_composer.py:821` reads `persona_tier = getattr(binding, "persona_tier", None)` + `engine_class = getattr(binding, "engine_class", None)` + branches on whether both are present; when not, falls back to `_SentinelMatrixCell()`.

**Conclusion:** Canonical `StepEffectiveBinding` (the production binding shape) lacks `persona_tier`. The `_evaluate_cell_synchrony_tolerant` helper landed at U-RT-93 returns `None` for any `StepEffectiveBinding` instance in production (the tolerant `getattr` fallback at the helper). Under the deferred composer body (per §14.8.8.1 step 1: `if synchrony is None or synchrony == SYNC_BLOCKING: fall through to step 4f`), the durable-async branch is **dead-code-in-production** — it never fires from any production binding. The helper IS correct per the tolerant semantic; the durable-async branch entry is unreachable.

This adjacency compounds the §1 finding: even if `ctx.webhook_delivery_composer` were bound, the durable-async branch would never be reached at production callsites without an extension to either (a) `StepEffectiveBinding` declaring `persona_tier`, or (b) a production binding-shape carrier that wraps `StepEffectiveBinding` + adds `persona_tier`, or (c) a different routing mechanism for the synchrony evaluation that does not rely on `binding.persona_tier`.

---

## §3 — Routing options

### §3.1 Reading A — Author the webhook binding chain + StepEffectiveBinding persona_tier extension

**Scope (estimated ~6-10 commits, multi-axis):**

1. **Runtime spec v1.25 → v1.26** — NEW §14.X.Y `materialize_webhook_delivery_composer_stage` factory contract at stage-5 LOOP_INIT bucket + §4 C-RT-04 NEW field row `webhook_delivery_composer: WebhookDeliveryComposer | None` (operator-opt-in surface; None = no durable-async cells). NEW `RT-FAIL-WEBHOOK-COMPOSER-STAGE-MATERIALIZE` fail class. §14.8.8.1 step 0 precondition AMENDED to require both `ctx.pause_resume_protocol is not None AND ctx.webhook_delivery_composer is not None` (otherwise fall through to step 4f sync). §14.8.8.6 composition claim AMENDED to acknowledge the binding-chain authoring.

2. **CP spec v1.16 → v1.17** — Author `StepEffectiveBinding.persona_tier: PersonaTier` field addition per scoping doc §0(C) empirical-verification correction (the §0(C) claim was wrong; persona_tier is not on the canonical model). Co-publish at C-CP-06 §6.2 amendment. OR: author a NEW wrapper binding shape that carries StepEffectiveBinding + persona_tier (preserves StepEffectiveBinding contract verbatim).

3. **Runtime plan v2.24 → v2.25** — Re-author U-RT-94 ACs to either consume bound webhook_delivery_composer (if Reading A path 1 chosen) OR add a NEW pre-U-RT-94 unit (call it U-RT-96) decomposing the webhook binding chain. Update U-RT-93 ACs per the persona_tier resolution (path 2: helper consumes `binding.persona_tier` directly; path 3: helper consumes a different per-step carrier).

4. **CP plan v2.21 → v2.22 (optional)** — Re-author per-step-override-evaluator carrier amendment per Reading A path 2 choice (StepEffectiveBinding extension vs wrapper).

5. **Impl arc** — Re-execute U-RT-93 (if persona_tier resolution changes the helper signature) + U-RT-94 (composer body) + U-RT-95 (e2e test).

### §3.2 Reading B — Author webhook binding chain only; DOWN-classify durable-async cell branch as test-fixture-only

**Scope (estimated ~3-5 commits):**

1. **Runtime spec v1.25 → v1.26** — Author webhook binding chain per §3.1 step 1.
2. **Runtime plan v2.24 → v2.25** — Re-author U-RT-94 ACs to gate durable-async branch entry on `binding.persona_tier` presence (via getattr-tolerant pattern). Document at change-note adjacent defect: "production callers pass StepEffectiveBinding which lacks persona_tier → durable-async branch fires only at test-fixture or extension-binding callsites".
3. **Impl arc** — U-RT-94 + U-RT-95 (e2e test exercises duck-typed binding fixture that carries persona_tier).

Reading B accepts that the durable-async cell HITL composition arc is reachable only via test fixtures (or future operator-supplied binding extensions) at v1.x — not via canonical `StepEffectiveBinding`. The webhook binding chain still needs authoring (the runtime spec consumer doesn't exist).

### §3.3 Reading C — DOWN-classify the entire HITL-gate-as-pause-trigger arc

**Scope (~2-3 commits):**

Revert the design-phase arc:
1. Runtime spec v1.25 → v1.26 REMOVES §14.8.8 + §14.8.8.9 sub-sections + reverts §14.8.2 step 4-bis insertion.
2. Runtime plan v2.24 → v2.25 REMOVES L9-terdecies cluster.
3. CP spec v1.16 §26.8 `ResumeContext` carrier + amended `attempt_resume` signature preserved verbatim (independent of the arc; survives DOWN classification).
4. CP plan v2.21 U-CP-64 AC #6 preserved verbatim.

Reading C posture: the HITL-gate-as-pause-trigger composition is deferred indefinitely; the §14.14.7 deferral (i) reverts to its v1.21 state pending a future arc that opens with the full binding-chain authoring at scoping-doc time.

### §3.4 Reading D — Operator-opt-in RETIRE-READY-without-RETIRED pattern

Per the operator-opt-in pattern established at batches 10-17 ([[h-t-cp-16-17-retire-ready-gate-runtime-composer-arcs]]):

1. Runtime spec v1.25 → v1.26 documents the binding-chain absence at §14.8.8.6 composition claim — explicitly NOT a v1.26 promise.
2. U-RT-94 ACs amended to land the composer body shape WITHOUT the webhook binding chain — body fires `NotImplementedError("webhook binding chain absent; operator must opt-in by ...")` when reached.
3. U-RT-95 e2e test verifies that production callers fall through to sync at step 4f (durable-async never reached); fixture-binding callers reach the NotImplementedError raise.

Reading D defers the binding-chain authoring to a future arc but preserves the L9-terdecies cluster shape + commits the composer body skeleton.

---

## §4 — Recommendation

Defer to operator decision via AskUserQuestion. The advisor (consulted at impl(U-RT-94) HALT-on-discovery) recommended:

> "This is identical-shape to `[[fork-validator-composer-arc-stage-4-absence]]` which required spec v1.18 §14.13 NEW C-RT-23 + plan v2.17 L9-decies cluster + 3-unit impl arc. Mirror precedent."

Reading A path 1 (StepEffectiveBinding extension) is the spec-faithful resolution but is the largest scope.

Reading B is the pragmatic in-scope resolution that preserves the spec contracts at face value + documents the reachability adjacency as a separate concern (not a blocker).

Reading C reverts the design-phase arc; pragmatic if the durable-async-cell pattern is not load-bearing for any near-term H_T-CP-* retirement.

Reading D preserves the L9-terdecies cluster shape with a NotImplementedError-style operator-opt-in posture.

---

## §5 — Cross-axis cascade analysis

| Reading | Runtime spec | CP spec | Runtime plan | CP plan | OD spec/plan | CXA |
|---|---|---|---|---|---|---|
| A path 1 (StepEffectiveBinding extension) | v1.25 → v1.26 | v1.16 → v1.17 | v2.24 → v2.25 (NEW unit + U-RT-94 re-author) | v2.21 → v2.22 | unchanged | unchanged |
| A path 2 (NEW wrapper carrier) | v1.25 → v1.26 | v1.16 (preserved) | v2.24 → v2.25 | v2.21 (preserved) | unchanged | unchanged |
| B (DOWN durable-async branch reachability) | v1.25 → v1.26 | unchanged | v2.24 → v2.25 | unchanged | unchanged | unchanged |
| C (DOWN entire arc) | v1.25 → v1.26 (§14.8.8 removed) | v1.16 (preserved per spec §26.8 independence) | v2.24 → v2.25 (L9-terdecies removed) | v2.21 (preserved) | unchanged | unchanged |
| D (skeleton + NotImplementedError) | v1.25 → v1.26 (§14.8.8.6 amendment) | unchanged | v2.24 → v2.25 | unchanged | unchanged | unchanged |

**ZERO OD cascade** across all readings (`PauseResumeAuditPayload` at OD spec §C-OD-30.4 composes from `PauseEvent` + `ResumeOutcome` per §C-OD-30.4.1, not from durable-async cell synchrony machinery).

**ZERO CXA cascade** across all readings (`cp_audit_to_od_audit` converter at CXA §2.3.7 row 6 unaffected; no new cross-axis edge).

---

## §6 — Current carrier landing posture

Per `[[halt-route-split-AC-pattern]]` precedent:

**Committed at `ba072f4` (this session):** U-RT-94 AC #9 only — `ResumeContextHolder` carrier + HarnessContext field + `_MutableHarnessContext` field + `_REQUIRED_FIELDS` extension + freeze() wiring + stage-5 LOOP_INIT initialization. AC #9 is structurally independent of the §14.8.8.1 composer body (the carrier is a sidecar pattern — empty holder is a valid state regardless of whether the composer body fires). All readings A/B/C/D preserve AC #9 verbatim (except Reading C, which would revert the holder landing as part of the broader arc DOWN-classification — but the holder code is trivially removable from `lifecycle/resume_context_holder.py` + types.py + bootstrap/mutable_context.py + bootstrap/stage_5_loop_init.py).

**Deferred at U-RT-94:** ACs #1-#8 + #10 (composer body + integration). All gate on this fork's resolution.

**Test results post-AC-#9 landing:** 1047 runtime + 689 harness-cp tests pass; pyright strict 0 errors on modified modules. Carrier landing is self-consistent.

---

## §7 — Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/class_1_fork_u_rt_94_webhook_delivery_composer_binding_chain_absence.md` |
| Fork class | Class 1 (halt-execution) |
| Surfaced at | impl(U-RT-94) phase-7-implementation skill arc HALT-on-discovery |
| HEAD at filing | `ba072f4` (post AC #9 carrier landing on `worktree-hitl-pause-trigger`) |
| Date | 2026-05-24 |
| Operator action owed | AskUserQuestion routing decision (A path 1 / A path 2 / B / C / D / Other) |
| Related forks (resolved) | `[[fork-validator-composer-arc-stage-4-absence]]` — identical-shape precedent |
| Related memory | `[[halt-route-split-AC-pattern]]` — AC #9 committed; ACs #1-#8+#10 deferred |
| Pattern application | 18th `[[advisor-before-substantive-work-for-cross-axis-blockers]]` trigger — advisor flagged the binding-chain absence + persona_tier adjacency before impl proceeded |
