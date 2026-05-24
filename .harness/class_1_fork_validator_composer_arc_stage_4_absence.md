# Class 1 Fork — Validator-composer arc: stage-4 factory contract absence blocks H_T-CP-21 RETIRED transition

**Filed:** 2026-05-24 at HEAD `4479b07` (post batch-14 H_T-CP-16 RETIRED close).
**Status:** OPEN — awaiting operator routing decision.
**Scope:** Phase 7d substitution-retirement; halt-execution Class 1 per `Project_Workflow_v1_8.md` §2.7.6 + workspace CLAUDE.md §4.3.
**Surfaced by:** `phase-7-substitution-retirement` skill §3.2 verification at H_T-CP-21 RETIRE-READY → RETIRED transition attempt; reconciled via `[[advisor-before-substantive-work-for-cross-axis-blockers]]` (composer-depth check) per skill §5 anti-leakage discipline + I-2 (X-AL-3) preservation.
**Disposition:** H_T-CP-21 stays RETIRE-READY at batch-14 §4 cumulative state. RETIRED transition halted. No code authored at this filing arc.

---

## 1. The gap

### 1.1 Symptom — composer-depth asymmetry against batch-14 close pattern

The batch-14 RETIRE-READY → RETIRED close pattern (per `.harness/phase-7d-retirement-events-batch-14.md` §6(a)) requires:

> 1. Operator supplies the gating substrate (config / step payload / external service / API key)
> 2. The test infrastructure landed alongside the RETIRE-READY transition is exercised
> 3. **The test exercises the same composer depth the production path traverses** — real bootstrap stage factory + real `HarnessContext` field binding + real driver invocation

H_T-CP-16 closed under this pattern at batch-14 via U-RT-82 e2e — `MemoryToolRegistry` constructed via the real `materialize_memory_tool_registry_stage` factory (U-RT-80) + bound to real `HarnessContext.memory_tool_registry` field (U-RT-79) + exercised through real `RuntimeLLMDispatcher.dispatch` inner-loop composer-step (U-RT-81).

**H_T-CP-21 cannot close under the same pattern at HEAD because the production stage factory does not exist.**

### 1.2 Empirical evidence

`grep -rn "validator_framework\|ValidatorFramework\|materialize_validator" harness-runtime/src/` at HEAD `4479b07`:

| Site | Reference shape |
|---|---|
| `harness-runtime/src/harness_runtime/types.py:1157` | `validator_framework: object | None = None` — typed-but-uncontracted field declaration on `HarnessContext` (stage-4 OD bucket per surrounding context) |
| `harness-runtime/src/harness_runtime/bootstrap/stage_4_od.py` | **ZERO references** to `validator_framework` |
| `harness-runtime/src/harness_runtime/bootstrap/` (all 9 stages) | **ZERO references** to `materialize_validator_framework_*` |
| `harness-runtime/src/harness_runtime/types.py` `RuntimeConfig` | **NO** `validator_framework_config` field |

The 440-line `harness-cp/tests/test_workflow_driver_validator_hook.py` (6/6 tests pass at HEAD) exercises the hook via:

```python
ctx = _FakeCtx(tracer_provider=provider, validator_framework=facade)
result = execute_workflow(ctx, ..., step_dispatchers=_registry(...))
```

`_FakeCtx` is a test-local class that bypasses production `HarnessContext` construction entirely. The `facade` is constructed via real `materialize_sync_validator_framework_facade(ConcreteValidatorFramework(...))` — production CP-axis classes — but the production runtime bootstrap never reaches this construction path. An operator running the production `harness_runtime.api.run(config)` entry point cannot inject a `validator_framework`; the field stays default-None for the lifetime of the `HarnessContext`.

### 1.3 Spec contract absence — multiple explicit deferrals

`Spec_Harness_Runtime_v1.md` v1.17 references a "validator-composer arc" as a **named but deferred future arc** at multiple sites:

| Site | Deferral statement |
|---|---|
| §14.8.2 step 3 (line 1783) | "v1.9 MVP `VALIDATOR_ESCALATION` emission is foreclosed: composer MUST NOT raise validator-escalation gate; the placement-trigger evaluator returns `no-placement-match` for `VALIDATOR_ESCALATION` at v1.9. **Validator-composer arc lands the trigger source.**" |
| §14.8.2 step 4c (line 1787) | "v1.9 MVP defers full 4-axis composition (C-CP-19 §19.1) **to the validator-composer arc**" |
| §14.8.2 step 4d (line 1788) | "Cross-trust-boundary palette restriction (per C-CP-19 §19.4) is **deferred to validator-composer arc** per NOTE 6-iv (§14.8.7)" |
| §14.8.2 fail class table (line 1920) | "`RT-FAIL-HITL-PLACEMENT-FORECLOSED-AT-V19` … **resolved at the validator-composer arc landing (future C-RT-NN).**" |
| §14.8.7 (line 1937) | "Whether `_hitl_required` predicate evaluation at step 4c reads from `placement.requires_hitl` (v1.9 MVP shape) or composes the full 4-axis predicate per C-CP-19 §19.1 — v1.9 MVP defers; **validator-composer arc lands the 4-axis composition.**" |
| §0.6 Q5 (line 289) | "C-RT-18 scope = PRE_ACTION + SUB_AGENT_BOUNDARY only; VALIDATOR_ESCALATION foreclosed at v1.9 MVP" |

`Spec_Harness_Runtime_v1.md` v1.17 §4 C-RT-04 HarnessContext field table at line 734 onward does NOT declare a `materialize_validator_framework_*_stage` factory contract for the `validator_framework: object | None = None` field. The field is present as a typed slot with no production wiring contract.

`Implementation_Plan_Harness_Runtime_v2_15.md` (canonical execution authority for runtime-axis units) does NOT contain a U-RT-NN atomic unit decomposing the validator-composer arc. The plan stops at U-RT-82 (Memory tool e2e); no validator-composer cluster declared.

`Implementation_Plan_Control_Plane_v2_17.md` U-CP-61 landed the `validator.*` post-dispatch hook at `workflow_driver.py:668` (CP-side composer-step amendment) — but the CP plan correctly does NOT contract the runtime-side stage factory (that's runtime-axis scope per ADR-F4 + workspace `CLAUDE.md` §1.3 authority chain).

### 1.4 Authoring at HEAD = silent X-AL-3 extension

Per `Phase_7_Meta_Architecture_v1.md` §7.7 X-AL-3:

> **X-AL-3.** **No silent H_T design extension at Phase 7 execution.** New H_T primitives surfaced at execution-time route to design-phase back-flow (Class 1) before implementation proceeds.

Authoring `RuntimeConfig.validator_framework_config` + `materialize_validator_framework_stage` + a real-bootstrap e2e at HEAD without spec/plan revision would:

1. Introduce a new `RuntimeConfig` field not declared at runtime spec v1.17 §3 C-RT-02
2. Introduce a new stage-4 factory contract not declared at runtime spec v1.17 §14 (or wherever stage-4 factories are contracted; the spec currently does not have a stage-4 factory section for validator_framework)
3. Introduce a new C-RT-NN contract surface
4. Introduce a new atomic unit cluster not declared at runtime plan v2.15
5. Bind a primitive whose canonical materialization shape has been explicitly deferred to "the validator-composer arc" at 6 distinct spec sites

Each is independently a silent X-AL-3 extension. Cumulatively this is a sizeable design-phase opening absorbed into a single execution-time arc.

---

## 2. Why this is Class 1 (not Class 3)

Per workspace `CLAUDE.md` §4.3 routing table + memory `[[spec-prose-plan-body-drift-pattern]]`: Class 3 applies when spec prose drifts from plan body BUT the contract is unambiguous. **This is not that pattern** — both spec AND plan are unambiguous in their **deferral** of the validator-composer arc. The defect is not drift; it is a known unstarted arc.

Per `Project_Workflow_v1_8.md` §2.7.6 Class 1 trigger taxonomy at workspace `CLAUDE.md` §4.3:

| Trigger | Match |
|---|---|
| Spec contract under-specifies a surface | ✓ — runtime spec v1.17 declares `validator_framework: object | None = None` field with no materialization contract |
| Plan signature cannot be materialized | ✓ — no U-RT-NN unit decomposes the validator-composer arc; cannot ship under Phase 7 execution authority |
| New H_T primitive surfaced (X-AL-3 violation) | ✓ — `RuntimeConfig.validator_framework_config` + `materialize_validator_framework_stage` are new primitives |
| Cross-axis edge cardinality contradicts CXA | (possibly) — CXA v2.6 §2.3.7 has a ValidatorFramework→OD edge already declared; need to check whether the v2.6 edge presupposes runtime-side wiring shape that this fork's resolution affects |

Per `[[advisor-before-substantive-work-for-cross-axis-blockers]]` pattern: advisor surfaced the composer-depth gap before any code was authored. Honest classification preserved.

---

## 3. The four possible operator routing decisions

### 3.1 Reading A — Minimal stage-factory landing only

**Scope:** Author only the stage-4 factory contract sufficient to bind an operator-supplied `validator_framework` at production `HarnessContext`. Do NOT land VALIDATOR_ESCALATION foreclosure resolution, 4-axis `_hitl_required` composition, or cross-trust palette restriction.

**Design-phase artifacts affected:**

| Artifact | Revision shape |
|---|---|
| `Spec_Harness_Runtime_v1.md` v1.17 → v1.18 | NEW §14.NN C-RT-NN `materialize_validator_framework_stage` factory contract (stage-4 OD bucket); NEW `RuntimeConfig.validator_framework_config: ValidatorFrameworkConfig | None` optional field at §3 C-RT-02; NEW `validator_framework` field-table row at §4 C-RT-04 specifying the materialization contract (currently field exists as untyped `object | None`); change-note section per spec-writer skill §3.2 discipline |
| `Implementation_Plan_Harness_Runtime_v2_15.md` v2.15 → v2.16 | NEW atomic-unit cluster L9-N decomposing the factory landing — at minimum: U-RT-83 (`RuntimeConfig.validator_framework_config` field landing) + U-RT-84 (`materialize_validator_framework_stage` factory + stage-4 wiring) + U-RT-85 (real-bootstrap e2e against operator-supplied `ValidatorFramework` instance, analogous to U-RT-82 for CP-16) |
| `Cross_Axis_Composition_Document_v2_8.md` | Likely unchanged — CXA v2.6 §2.3.7 ValidatorFramework→OD edge already declared; the producer side (validator-composer arc) is what's deferred, not the cross-axis seam shape |

**Execution-time arc estimate (post-spec-+-plan-clearance):** 3 commits (U-RT-83 → U-RT-84 → U-RT-85), then batch-15 H_T-CP-21 RETIRE-READY → RETIRED close per batch-14 §6(a) pattern.

**Trade-off:** Smallest scope; preserves spec-deferred sites at §14.8.2 (VALIDATOR_ESCALATION foreclosure stays in place); enables CP-21 RETIRED transition without unblocking the larger validator-composer arc primitives. Future scope-expansion arcs unblock VALIDATOR_ESCALATION + 4-axis composition + cross-trust palette independently.

### 3.2 Reading B — Full validator-composer arc

**Scope:** Open the full validator-composer arc as currently deferred at runtime spec v1.17. Lands: stage-4 factory (per Reading A) + VALIDATOR_ESCALATION trigger source + 4-axis `_hitl_required` composition + cross-trust palette restriction + any cross-axis seams the full arc requires.

**Design-phase artifacts affected:**

| Artifact | Revision shape |
|---|---|
| `Spec_Harness_Runtime_v1.md` v1.17 → v1.18 (or v1.x with significant body delta) | NEW C-RT-NN validator-composer arc contract (likely paralleling §14.8 HITL-gate composer surface in scope); resolution of all 6 §14.8.2 deferrals enumerated at §1.3; new failure-mode taxonomy entries replacing `RT-FAIL-HITL-PLACEMENT-FORECLOSED-AT-V19`; §0.6 Q5 ratification reversal |
| `Implementation_Plan_Harness_Runtime_v2_15.md` v2.15 → v2.16 | New multi-cluster decomposition (likely L9-N + L9-N+1 + possibly more); estimate 8-15 atomic units (analogous to U-RT-60-cluster L9-quinquies HITL-gate-composer scope) |
| `Spec_Control_Plane_v1_11.md` | Possibly amended — depends on whether the validator-composer arc surfaces any clarification owed at C-CP-28 (ValidatorFramework, renamed from v1.10 C-CP-25 at v1.13 per `[[fork-cp-spec-section-25-contract-id-collision]]` Reading A) / C-CP-26 (PauseResumeProtocol) / C-CP-27 (PerServerTrustEvaluator) producer-side; spec-writer determines at revision time |
| `Cross_Axis_Composition_Document_v2_8.md` | Possibly amended — VALIDATOR_ESCALATION resolution may surface new CP→OD typed seam at §2.3.7 |
| `Spec_Operational_Discipline_v1_9.md` | Possibly amended — `_hitl_required` 4-axis composition may surface new OD-side observability requirements |

**Execution-time arc estimate (post-spec-+-plan-clearance):** 8-15 commits across 1-2 clusters, then batch-15 H_T-CP-21 RETIRED close + likely cascade closes for other RETIRE-READY rows whose gates intersect.

**Trade-off:** Largest scope; resolves all 6 deferral sites simultaneously; high coherence value but large operator commitment for one Phase 7d milestone. Likely 2-3 weeks of design-phase + execution work.

### 3.3 Reading C — Defer validator-composer arc; mark CP-21 RETIRED-BLOCKED-ON-DESIGN-ARC

**Scope:** No spec / plan revision. Update batch-14 §4 + harness-cp/CLAUDE.md §4.1 to re-classify H_T-CP-21 from RETIRE-READY to a new STATUS-FAMILY value (e.g., "RETIRE-READY-BLOCKED-ON-DESIGN-ARC") that distinguishes operator-opt-in gates achievable at HEAD (CP-18 + AS-2) from those gated on design-phase arcs (CP-21).

**Design-phase artifacts affected:**

| Artifact | Revision shape |
|---|---|
| `phase-7d-retirement-ledger-v2.md` | Possibly amended to introduce the new STATUS-FAMILY classification; clarifies the operator-opt-in pattern semantics |
| Forward-only ledger discipline preservation | New batch-15 records the re-classification without modifying prior batch records |

**Execution-time arc estimate:** 1 commit (batch-15 + per-axis CLAUDE.md refresh).

**Trade-off:** Honest classification without spec revision; preserves design-phase authority chain; documents the back-flow blocker without committing to scope. CP-21 stays at RETIRE-READY-equivalent indefinitely until operator chooses Reading A or Reading B.

### 3.4 Reading D — Re-evaluate CP-21 gate definition

**Scope:** Question the operator-opt-in gate definition itself at H_T-CP-21. Per `Phase_7_Meta_Architecture_v1.md` §5 H_T-CP-21 row + `phase-7d-retirement-ledger-v2.md` §2.1 line-33 strict-reading: is the gate genuinely "operator-supplied `validator_framework` non-None at HarnessContext" (which is unachievable without stage factory), or is it "C-CP-28 `ValidatorFramework` Protocol + `ValidatorFailClass` 5-class + 5-class outcome-evaluation hook at workflow_driver" (which IS landed at HEAD via U-CP-58/59/60/61 cluster 10-CP-A; C-CP-28 renamed from v1.10 C-CP-25 at CP spec v1.13 per `[[fork-cp-spec-section-25-contract-id-collision]]` Reading A apply pass)?

If the latter reading is canonical, CP-21 may already be RETIRED at HEAD under the proper gate interpretation, and the batch-11 + harness-cp/CLAUDE.md classification was the over-conservative one (inherited the CP-18/20 external-substrate pattern by name without auditing whether the gate semantics applied).

**Design-phase artifacts affected:**

| Artifact | Revision shape |
|---|---|
| `phase-7d-retirement-ledger-v2.md` | Amended to clarify per-row gate semantics — distinguish library-completion gates (criterion-B satisfied at landing arc) from external-substrate gates (criterion-B operational-MET requires gating substrate) from runtime-wiring gates (criterion-B operational-MET requires bootstrap factory + e2e) |
| `Phase_7_Meta_Architecture_v1.md` §5.4 H_T-CP-21 row | Possibly amended to clarify the canonical gate reading |
| Cumulative retirement-state reconciliation | If Reading D resolves CP-21 to RETIRED at HEAD: batch-15 records the re-classification + cumulative 23/49 → 24/49 RETIRED |

**Execution-time arc estimate:** 1 commit (batch-15 re-classification) if Reading D resolves CP-21 RETIRED at HEAD; or escalates to Reading A/B/C if Reading D's audit finds the gate definition genuinely requires the stage factory.

**Trade-off:** Surfaces possible classification error at batch-11 + batch-14 §4 cumulative state. If correct, CP-21 was already RETIRED at HEAD and no design-phase arc needed. If incorrect, routes to A/B/C anyway. Low cost to verify.

---

## 4. Affected substrate inventory (for Reading A or B routing)

If operator chooses Reading A or Reading B, design-phase back-flow opens at:

| Phase channel | Artifact | Revision shape |
|---|---|---|
| Phase 5 spec revision | `Spec_Harness_Runtime_v1.md` v1.17 → v1.18 | NEW C-RT-NN per Reading A/B scope |
| Phase 6 plan revision | `Implementation_Plan_Harness_Runtime_v2_15.md` v2.15 → v2.16 | NEW cluster per Reading A/B scope |
| Phase 6 CXA revision | `Cross_Axis_Composition_Document_v2_8.md` v2.8 → v2.9 (already-owed at handoff §6 for cost-attribution audit-write seam — could batch with this arc) | NEW seams if Reading B introduces them |
| Phase 5 OD spec revision | `Spec_Operational_Discipline_v1_9.md` v1.9 → v1.10 | Possibly amended at Reading B if `_hitl_required` 4-axis composition requires new OD observability |

**Authority chain ordering** (per workspace `CLAUDE.md` §1.3): ADR (validator framework already anchored at ADR-D1 v1.2 + ADR-D6 v1.2 — likely NO ADR revision needed under Reading A; possibly revisited at Reading B if VALIDATOR_ESCALATION resolution requires new HITL-class anchoring) → ADD v1.3 (likely unchanged; ADD doesn't enumerate stage-factory contracts) → PRD v1.1 (likely unchanged; PRD doesn't enumerate runtime wiring) → per-axis spec → per-axis plan → CXA → Phase 7 execution.

---

## 5. Cross-axis cascade analysis

If Reading A or Reading B resolves:

| Cascade endpoint | Cascade trigger |
|---|---|
| CP-21 RETIRE-READY → RETIRED at batch-15 (Reading A) or batch-16+ (Reading B) | YES — direct retirement transition |
| CXA v2.6 §2.3.7 ValidatorFramework→OD edge | Possibly — depends on Reading B scope (Reading A stays within existing edge) |
| OD spec v1.9 validator.* span attribute schema | Unchanged at Reading A; possibly amended at Reading B `_hitl_required` 4-axis |
| Other RETIRE-READY rows (CP-18, AS-2) | NO cascade — independent gates (external MCP substrate) |
| Other PARTIAL rows (CP-22) | Possibly — CP-22 (PauseResumeProtocol) gates on workflow_driver pause-handler invocation; Reading B's VALIDATOR_ESCALATION resolution may or may not intersect with pause-resume scope |

If Reading C: ZERO cross-axis cascade. Re-classification is bookkeeping only.

If Reading D: ZERO cross-axis cascade if gate-definition audit resolves CP-21 RETIRED at HEAD. Otherwise routes to Reading A/B/C cascade analysis.

---

## 6. Operator-decision surface

Per `phase-7-back-flow-routing` skill §4.4 format:

```
CLASS 1 FORK DETECTED — HALT H_T-CP-21 RETIRE-READY → RETIRED TRANSITION

Defect locus: Spec_Harness_Runtime_v1.md v1.17 §4 + §14 — validator-composer
arc explicitly deferred at 6 spec sites; no materialize_validator_framework_*
stage factory contracted; no RuntimeConfig.validator_framework_config field;
production HarnessContext.validator_framework: object | None = None field
exists without wiring contract.

Defect description: H_T-CP-21 RETIRE-READY → RETIRED transition requires
composer-depth parity with batch-14 H_T-CP-16 close pattern (real bootstrap
factory + real HarnessContext binding + real driver e2e). Existing 440-line
hook test uses _FakeCtx and bypasses production bootstrap entirely. Authoring
the stage factory at HEAD would be silent X-AL-3 extension across 5 distinct
spec/plan surfaces.

Routing target: Phase 5 spec revision (runtime spec v1.17 → v1.18) +
Phase 6 plan revision (runtime plan v2.15 → v2.16), per scope chosen by
operator per §3 readings A/B/C/D.

Halt point: H_T-CP-21 RETIRE-READY → RETIRED transition at batch-14 §4
cumulative state. H_T-CP-21 stays RETIRE-READY honestly.

Resumption requires: design-phase artifact re-issue per chosen reading,
re-loaded into this workspace, then batch-15 close arc opens.

Operator decision required:
  (A) Authorize Reading A — minimal stage-factory landing only (~3-unit
      cluster; ~3 commits post-clearance; CP-21 RETIRED at batch-15)
  (B) Authorize Reading B — full validator-composer arc (8-15 commits;
      resolves all 6 §14.8.2 deferrals; CP-21 RETIRED + cascade closes
      at batch-15/16+)
  (C) Authorize Reading C — defer arc; re-classify CP-21 as RETIRE-READY-
      BLOCKED-ON-DESIGN-ARC at batch-15; no spec revision
  (D) Authorize Reading D first — audit the H_T-CP-21 gate definition at
      Meta-Arch §5.4 + ledger-v2 §2.1 to verify whether stage factory IS
      genuinely required (may resolve to RETIRED at HEAD if not)
```

---

## 7. Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/class_1_fork_validator_composer_arc_stage_4_absence.md` |
| Fork class | Class 1 (halt-execution per `Project_Workflow_v1_8.md` §2.7.6) |
| Filed at | 2026-05-24 at HEAD `4479b07` (post batch-14 H_T-CP-16 RETIRED close) |
| Filing authority | `phase-7-back-flow-routing` skill §4 fork-handling shape steps 1–4; X-AL-3 anti-leakage discipline preservation; `[[advisor-before-substantive-work-for-cross-axis-blockers]]` pattern application |
| HEAD at filing | `4479b07` (workspace clean; tests green workspace-wide except external-substrate-gated suites) |
| Affected substitution row | H_T-CP-21 (ValidatorFailClass 5-class + operator-burden eval) |
| Related forks | `.harness/class_1_fork_u_cp_58_validator_fail_class_collision.md` (RESOLVED 2026-05-21 path β — `ValidatorFailClass` rename; preceded this fork by 3 days; relevant context but distinct scope — that fork was a name collision, this fork is a stage-factory absence) |
| Related memory | `[[advisor-before-substantive-work-for-cross-axis-blockers]]` (advisor surfaced composer-depth gap before code authored); `[[halt-route-split-AC-pattern]]` (no AC-level partial landing applicable — entire arc is design-phase opening, not unit-level partial); `[[h-t-cp-16-17-retire-ready-gate-runtime-composer-arcs]]` (precedent close pattern catalogued at batch-14 §6(a)) |
| Successor | At operator routing decision (A/B/C/D): authorizes the matching design-phase channel opening; this fork doc evolves to APPLIED state at the relevant batch-15 / spec-revision / re-classification arc close |

---

*End of Class 1 fork filing. Validator-composer arc stage-4 factory contract absence. H_T-CP-21 RETIRE-READY → RETIRED transition HALTED pending operator routing decision per §6.*
