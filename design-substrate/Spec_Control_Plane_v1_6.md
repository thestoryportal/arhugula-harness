# Specification — Control Plane v1.6

## Change-note (v1.5 → v1.6)

**Scope of revision.** Phase-7 in-CLI spec growth absorbing operator-ratified Path A resolution of `.harness/class_1_tension_c_rt_17_step_dispatcher_parent_context_gap.md` (filed 2026-05-20 at `0787f03`; Path A ratified same session). U-RT-59 spec authoring pre-survey + advisor cross-check surfaced a structural gap: the `StepDispatcher` Protocol declared at `harness-cp/src/harness_cp/workflow_driver.py:151` (`dispatch(binding: StepEffectiveBinding, step: WorkflowStep) -> Mapping[str, Any]`) lacks the per-step parent context surface that C-CP-12 §12.2 sub-agent gate-level composition + C-CP-13 §13.5 audit-trail-link composition + C-CP-14 §14.2 multi-agent span emission require. Resolution per operator-ratified Path A: extend Protocol with new keyword-only `step_context: StepExecutionContext` parameter; CP-axis declares the schema; driver composes per-step from run-level state; dispatchers consume as needed. Co-published with `Spec_Harness_Runtime_v1.md` v1.6 §14.7 (the C-RT-17 sub-agent dispatch composer contract consuming `step_context`).

**Two amendment sites.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **§25.2 Signatures + new §25.2.1 StepExecutionContext schema** | New 8-field record `StepExecutionContext` declared at §25.2.1; `StepDispatcher` Protocol declared formally at §25.2 (pre-v1.6 the Protocol existed at the code surface but was not pinned in spec); Protocol shape extended with keyword-only `step_context: StepExecutionContext` parameter; documented MVP-default conventions for the 4 deferred-to-impl-discretion fields (`parent_gate_level`, `parent_sandbox_tier`, `parent_entry_hash`, `tenant_id`) per the v1.6 reading of the C-CP-12 §12.4 deferral pattern. | Operator-ratified `.harness/class_1_tension_c_rt_17_step_dispatcher_parent_context_gap.md` §6 Path A; C-CP-12 §12.2 sub-agent gate-level composition formula; C-CP-12 §12.4 deferred-to-implementation-discretion pattern; `Spec_Harness_Runtime_v1.md` v1.6 §14.7 C-RT-17 consumer surface |
| **§25.3.3.4 Dispatch step body** | Amended to cite `step_context` keyword parameter passed by the driver to the dispatcher; preserves the existing "Step body is opaque to the driver" invariant by clarifying that `step_context` carries metadata about the step's execution environment (driver-composed) — NOT step body content (operator-authored, opaque). | Operator-ratified Path A; existing C-CP-25 §25.3.3.4 surface |

**Sections preserved verbatim from v1.5.** All v1.5 content outside §25.2 + §25.3.3.4 preserved unchanged. §25.9 (cost-attribution emission composition) stands; §25.7 failure-mode taxonomy stands; §25.1 in-scope set stands.

**Status posture.** Proposed (v1.5) → **Proposed (v1.6)**. Adversarial-review pass scheduled at U-RT-59 landing per Phase 7 sub-phase 7b discipline (in keeping with the U-RT-58 / v1.4-then-landing pattern).

**Downstream absorption owed.** Code-side amendments landed in the same Path A Stage 1 plumbing commit: `StepExecutionContext` Pydantic v2 type at `harness-cp/src/harness_cp/workflow_driver_types.py`; `StepDispatcher` Protocol signature updated at `harness-cp/src/harness_cp/workflow_driver.py:151`; `execute_workflow` driver loop composes `StepExecutionContext` per step + passes to `step_dispatcher.dispatch(...)` per the v1.6 Path A semantics; `RetryBreakerFallbackDispatcher` (C-RT-16) + `RuntimeLLMDispatcher` (C-RT-15) accept the new parameter via Protocol conformance (neither consumes at v1.6; reserved for v1.7+ surfaces). U-RT-59 plan body HALT marker dropped at the same commit; runtime spec §14.7 TBD markers replaced with `step_context.X` references. No fork-record back-reference at this contract beyond the Class 1 record cited above.

---

## Status block

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_5.md` |
| Status | **Proposed** — Phase-7 design-substrate revision absorbing operator-ratified Q1e cost-attribution emission composition (see Change-note v1.4 → v1.5). v1.4 promotion path (C-CP-25 atomic units land + runtime un-strike) carries forward unchanged at v1.5. |
| Revision | v1 → v1.1 (P5-CK iter-1 close mechanical revision) → v1.2 (P5-CK iter-2 mechanical-alignment) → v1.3 (F2-12 cascade Step 5a revision pass authored 2026-05-14) → v1.4 (Phase-7 architectural-tension revision pass authored 2026-05-20 per `.harness/class_1_tension_u_rt_44_workflow_loop_drain.md` + `.harness/c_cp_25_workflow_driver_recommendation.md`; absorbed C-CP-25 `WorkflowDriver` contract scoped to `SINGLE_THREADED_LINEAR` topology pattern + engine classes `pure-pattern-no-engine` + `save-point-checkpoint`) → **v1.5 (Phase-7 architectural-tension revision pass authored 2026-05-20 per `.harness/fork_u_rt_49_cost_attribution_invocation_underspec.md` Q1e operator-ratified; absorbs new §25.9 Cost-attribution emission composition — step-body-owned propagated pattern; preserves §5.1 closed-at-8 lifecycle event taxonomy verbatim; no new §5.1 event class)** |
| Revision date | 2026-05-20 (v1.5 revision pass, same day as v1.4) |
| Phase | 7 — Phase-7 design-substrate revision absorbing operator-ratified `fork_u_rt_49_cost_attribution_invocation_underspec` Q1e recommendation; in-CLI per workspace convention (design-phase back-flow deprecated 2026-05-15); `spec-writer` skill (spec-revision-pass sub-mode) applies the decided fix. |
| Skill | `spec-writer` (spec-revision-pass sub-mode) at v1.5 |
| Promotion path | Accepted at C-CP-25 plan + implementation landing close (CP plan v2.13 absorbing v1.5 §25.9 + landed driver units + runtime un-strike of U-RT-44 AC #2 + U-RT-49 workflow-execution ACs including the cost-attribution AC un-struck per Q1e + Q3c materialization) |
| Source-set | All v1.4 inputs (preserved) + `.harness/fork_u_rt_49_cost_attribution_invocation_underspec.md` (Q1–Q4 operator-ratified 2026-05-20) + `Spec_Operational_Discipline_v1_4.md` C-OD-14 5-step cost-attribution chain composition + `Phase_7_Meta_Architecture_v1.md` X-AL-2 substitution retirement criterion + Phase-7 sub-phase 7b execution context |
| Entry authorization | `.harness/fork_u_rt_49_cost_attribution_invocation_underspec.md` (Class 1 fork, status OPEN-RESOLVING 2026-05-20; Q1e + Q2-bounded + Q3c + Q4-resolve-next-session ratified) + `CLAUDE.md` §4.3 back-flow routing (Class 1 spec revision authorized in-CLI per workspace governance) |
| Exit gate | CP plan v2.12 → v2.13 revision-pass (`implementation-planner` skill) consuming this CP spec v1.5 §25.9 contract as substrate; downstream runtime un-strike at U-RT-49 cost-attribution AC at smoke test extension; full closure of parent `.harness/class_1_tension_u_rt_44_workflow_loop_drain.md` (CLOSED-PARTIAL since Lane 6 → fully CLOSED at this arc completion) |

## Change-note (v1.3 → v1.4)

**Scope of revision.** Phase-7 design-substrate revision per `Project_Workflow_v1_8.md` §2.7.6 (Class 1 fork back-flow routing) absorbing operator-ratified C-CP-25 `WorkflowDriver` contract from `.harness/c_cp_25_workflow_driver_recommendation.md`. The revision adds one new contract (C-CP-25) and updates the §[traceability] matrix + §[coherence pass] for v1.4 verification + Filing footer. Five amendment sites:

| Site | Amendment shape | Substrate source |
|---|---|---|
| **§25 C-CP-25 (NEW contract — workflow execution driver)** | New contract added: workflow execution driver scoped to `SINGLE_THREADED_LINEAR` topology pattern only + engine classes `pure-pattern-no-engine` + `save-point-checkpoint` only at v1.4; specifies signature (input: `WorkflowManifestEntry` per §6.1 + `run_id` + `HarnessContext` per `Spec_Harness_Runtime_v1.md` §11; output: `RunResult` with `RunStatus` 4-value enum); step iteration discipline (validates topology + engine-class scope → emits `workflow.start` → iterates steps in declaration order under §6.2 per-step override + U-CP-14 resolver + U-CP-01 router dispatch + state-ledger append per C-IS-05/§8.2 idempotency-key join); drain protocol (4-site check pattern: driver entry + per-step pre-entry + per-step post-exit + NO mid-step interruption, per `Spec_Harness_Runtime_v1.md` §11 settlement); lifecycle event emission boundaries (strict composition against §5.1 8-class taxonomy filtered to single-threaded-linear); composition with C-CP-08 §8.2 idempotency-key join for replay-resumption under `save-point-checkpoint`; failure-mode taxonomy (4 driver-owned + 1 runtime-owned); deferral notation for 5 other topology patterns + 3 other engine classes per X-AL-3 anti-leakage rule. | Operator-ratified `.harness/c_cp_25_workflow_driver_recommendation.md` §4 (4/4 sign-off points approved 2026-05-20); ADR-F3 v1.1 §Decision (iv) (workflow lifecycle event surface foundational commitment); `Spec_Harness_Runtime_v1.md` §11 C-RT-11 (drain ownership composition seam) |
| **§[traceability] — C-CP-25 row addition** | New row added: C-CP-25 × R-CP-04 (workflow lifecycle event surface — driver materializes the emission site); C-CP-25 × R-CP-07 (replay-resumption semantics — driver composes with §8.2 idempotency-key join at re-entry under `save-point-checkpoint`). Per-row cell marks per traceability matrix convention. | C-CP-25 §4.6 lifecycle event filter table + §4.7 idempotency-key composition |
| **§[coherence pass] — v1.4 verification line** | Extended with v1.4 amendment-site verification line per Workflow v1.7 §7 fidelity-grammar: inputs read (operator-ratified recommendation + ADR-F3 v1.1 + Runtime spec §11); ingestion contract (Phase-7 architectural-tension-resolution substrate per `systems-architect` skill §4A); tensions surfaced (Class 1 fork at `.harness/class_1_tension_u_rt_44_workflow_loop_drain.md` — RESOLVING at v1.4 + CP plan v2.11); self-audit (no Pattern P1 name drift — C-CP-25 cites §5.1 8-class taxonomy verbatim; no Pattern P2 verbatim-claim-contradicted — every citation byte-exact). | `systems-architect` §4A protocol + workspace `CLAUDE.md` invariant I-1 |
| **Status block (multiple rows)** | Revision row extended with v1.4 entry; Revision date row updated to 2026-05-20; Source-set extended with recommendation + ADR-F3 + Runtime spec §11 entries; Entry authorization extended with tension record + operator ratification + `CLAUDE.md` §4.3; Exit gate extended with CP plan v2.11 + runtime un-strike target. | `.harness/class_1_tension_u_rt_44_workflow_loop_drain.md` resolution-status section |
| **Filing footer** | Artifact line updated to `Spec_Control_Plane_v1_4.md`; Status line updated; Predecessor extended with v1.3 entry; Successor updated to CP plan v2.11; Substrate consumed extended with recommendation + ADR-F3 §Decision (iv) + Runtime spec §11; Date updated. | Workspace filing convention |

Workflow v1.7 §7 fidelity-grammar discipline applied across all v1.4 amendment sites: no Pattern P1 cross-artifact name drift (`WorkflowEventClass` per harness-core / spec §5.1 8 values consumed verbatim at §25 §4.6; engine-class enum values per §7.1 + §8.1 consumed verbatim at §25 §4.2 + §4.4.1; `RunStatus` 4-value enum is C-CP-25-introduced and does not collide with any prior name); no Pattern P2 verbatim-claim-contradicted (all "per §N" + "per ADR-X" citations verify against source files); citation anchors substrate-verified per `Project_Workflow_v1_8.md` §7.4.2 byte-exact grammar + `CLAUDE.md` invariant I-1.

**Status posture.** `Status: Proposed` per workspace convention (per `Project_Workflow_v1_8.md` §3.1) — promotion to `Accepted` blocked until C-CP-25 atomic units land at CP plan v2.11 + runtime un-strike completes at U-RT-44 AC #2 + U-RT-49 workflow-execution ACs.

**Sections preserved verbatim from v1.3.** §Front-matter (Axis declaration; Axis-grounding note; PRD requirement scope; ADR scope; Cross-axis citation substrate; Persona-linkage substrate; Scope and out-of-scope); §1 C-CP-01 through §9 C-CP-09 (including all v1.3 amendment sites — §3.5 retry.* sub-tree; §5.4 sampling table; §8 C-CP-08 + §8.4 F2-12 closure; §9 C-CP-09 + §9.1 4-attribute engine.* declaration; v1.3 amendment markings preserved unchanged); §10 C-CP-10 through §24 C-CP-24 (preserved-verbatim stubs unchanged from v1.3); §[carry-forwards] [CF-1] F2-12 closure status (preserved verbatim from v1.3 — ✅ CLOSED at v1.3 unchanged); §[carry-forwards] [CF-2] Workflow §7 substrate-skill propagation (preserved verbatim from v1.2 onward, unchanged at v1.4); §[traceability] matrix (preserved verbatim from v1.3 except one new C-CP-25 row added at §[traceability] — see amendment-sites table above); §[coherence pass] (preserved verbatim from v1.3 except extended with v1.4 amendment-site verification line — see amendment-sites table above).

**Changes inline.** Status block (Revision row extended with v1.4 entry; Revision date updated to 2026-05-20; Source-set extended; Entry authorization extended; Exit gate updated). This Change-note (v1.3 → v1.4) section. §25 C-CP-25 new contract (added after §24 stub, before §[carry-forwards]). §[traceability] matrix C-CP-25 row addition. §[coherence pass] v1.4 verification line extension. Filing footer updated to v1.4.

**Cross-cascade-step coordination.** CP spec v1.4 produces one downstream effect:

| Downstream step | Substrate consumed from CP spec v1.4 |
|---|---|
| CP plan v2.11 revision-pass (`implementation-planner`) | §25 C-CP-25 contract → new atomic units `U-CP-NN` (driver core implementing §25.4 iteration loop + §25.6 lifecycle emission filter) + `U-CP-NN+1` (drain composition with `HarnessContext` per §25.5 + `RunResult` terminal type per §25.3). Dependency-graph delta: new units depend on U-CP-13 (manifest schema) + U-CP-14 (per-step resolver) + U-CP-10 (WorkflowEventClass enum) + U-CP-15 (EngineClass enum) + U-CP-01 (cap-aware router) + U-IS-07 (ledger entry shape) + U-IS-10 (export) + U-IS-11 (append) + U-RT-44 (HarnessContext). |

Downstream Phase-7 implementation effect: at C-CP-25 atomic units land, refactor `harness-runtime/` to delegate workflow execution drain to the new driver per `Spec_Harness_Runtime_v1.md` §11 risk-surface guidance ("If CP later surfaces a native drain primitive... refactor `harness-runtime/` to delegate drain to CP. This contract becomes a thin adapter."); un-strike U-RT-44 AC #2 + U-RT-49 workflow-execution ACs; mark `.harness/class_1_tension_u_rt_44_workflow_loop_drain.md` CLOSED.

**Adjacent-defect findings surfaced (not patched at v1.4).** Per `spec-writer` skill §"Failure mode FM-2" no-extension discipline, the following adjacent defects were surfaced during this revision but are NOT patched at v1.4 (would constitute spec extension beyond authorized fix):

- **Anti-finding §6.2 from recommendation (Class 3 informational).** Workspace root `CLAUDE.md` §2.2 ADR table mislabels 4 of 5 F-ADR rows (F2 labeled "State ledger primitive" — actual title "Filesystem + git canonical state"; F3 labeled "Index primitive" — actual title "Stateless-reducer / launch-pause-resume durable-execution"; F4 labeled "Workflow lifecycle primitive" — actual title "Four-tier sandbox isolation"; F5 labeled "Observability substrate primitive" — actual title "Tier-aware secrets fetch"). NOT a CP-spec defect. Pointer fix at next `CLAUDE.md` revision pass; non-blocking.

- **Adjacent finding §B (CP-spec under-specification surfaced; not patched at v1.4; routed to follow-up CP spec revision).** §25.5 lifecycle event emission table at the `lease.acquired` / `lease.released` row could not cite a per-engine-class lease-assignment mapping. The original recommendation pointed at §9.1; verification at spec-writer time: §9.1 `engine.*` namespace declares 4 attributes (`engine.class`, `engine.event_history.tier`, `engine.event.id`, `engine.replay_disposition`) — none of these is a lease-assignment row. §5.3 `lease.*` namespace declares the `lease.mechanism` 6-value enum (`engine_native, redis_lease, db_unique_constraint, worktree_isolation, etcd_cas, per_segment`) but does NOT declare per-engine-class-to-`lease.mechanism` binding. Net under-specification: CP spec v1.4 carries lease semantics + engine-class enum + lease-mechanism enum, but no contract surface explicitly maps `engine.class` → required-lease-mechanism. §25.5 lease row reworded at v1.4 to cite §5.3 directly (correcting the recommendation's mis-cited §9.1) and to flag the substrate gap. C-CP-25 driver contract therefore states "emit `lease.acquired/released` per binding's required lease mechanism per §5.3" without asserting the per-engine-class binding rule (which is not on the spec). Routing to follow-up CP spec revision: a separate revision pass (when first non-`SINGLE_THREADED_LINEAR` topology or non-`pure-pattern-no-engine` engine class is materialized) should add a per-engine-class lease-mechanism row at §9.1 or §7.1 or a new §X.

- **Adjacent finding §C (symmetry-introduced typed error name).** §25.7 introduces `EngineClassNotYetMaterializedError` as the typed error for out-of-v1.4-scope engine classes, by symmetry with `TopologyPatternNotYetMaterializedError` (which the recommendation explicitly named at §4.2 + §4.8). The recommendation did not name an engine-class error directly. Spec-writer authored the name for parity per operator sign-off point 2 (engine-class scoping). Pure name introduction; no architectural extension. Operator may rename at next revision-pass; mechanical token replacement.

- **Adjacent finding §D (operator-ratified deviation from recommendation at §25.3.3.1 + §25.4 + §25.5 — Path B).** The recommendation §4.4.3.1 + §4.5 pre-step-entry-drain row + §4.6 lifecycle event filter specified emission of a terminal `step.boundary` event with `step.kind='drain-aborted-pre-entry'` at the pre-step drain site. Spec-writer audit surfaced: §5.2 declares `step.kind ∈ {declarative-step, inference-step, tool-step, HITL-step, sub-agent-dispatch}` (5 values, no explicit closure marker; other CP enums explicitly mark closure — §5.1 closed-at-8, §10.1 closed-at-6 — and §5.2 does not). Adding a 6th value is interpretive: defensible as "open by absence of marker," contestable as silent enum extension. Operator ratified Path B 2026-05-20 (drop the pre-step-entry `step.boundary` emit; preserve §5.2 5-value enum verbatim; terminal observability via `RunResult.status='drained'` + `terminal_step_index` return only at this site). §25.3.3.1 + §25.4 row "Per-step pre-entry" + §25.5 `step.boundary` row + §25.8 deferral list amended accordingly. This is a documented deviation from the original recommendation §4 contract content, applied with operator authority per spec-writer "bright line" rule §"Activation discipline" + Workflow §4.1.2 conservative-default discipline.

- **In-session amendment §F (Class 1 fork OPEN at implementation-time: §25.6 replay-resumption under-implementable).** Spec v1.4 §25.6 specifies (a) `run_idempotency_key = sha256(run_id, workflow_id, entry_version)` composition, (b) prefix-match read against C-IS-07 state-ledger, (c) selective RESUMPTION emission on match, (d) step skip + resume at first unmaterialized. U-CP-56 implementation 2026-05-20 surfaced two substrate gaps: (1) `WorkflowManifestEntry` (U-CP-13 landed) has no `entry_version` field for the hash composition; (2) no IS prefix-match read primitive landed. U-CP-56 PARTIAL-LAND ships the weaker behavior (RESUMPTION emit on any non-genesis ledger). AC #6 STRUCK at plan v2.11 pending resolution. Class 1 fork filed at `.harness/class_1_tension_u_cp_56_resumption_underspec.md`. Resolution Path A (recommended): CP plan v2.12 + CP spec v1.5 extending `WorkflowManifestEntry` with `entry_version` field + IS read primitive (cross-axis coordination); §25.6 contract content preserved unchanged at v1.5 with full materialization at follow-up.

- **In-session amendment §E (Class 1 fork resolved at implementation-time: step sequence source).** Spec v1.4 §25.3.3 iteration discipline as originally drafted referenced `manifest_entry.steps` (e.g., "For each step `s` in `manifest_entry.steps`"). At implementation-time materialization of U-CP-56, `phase-7-implementation` audit surfaced: `WorkflowManifestEntry` (U-CP-13 landed per CP plan v2.10) declares 10 fields — none of them `steps`. The closest is `per_step_overrides: dict[StepID, StepOverride]` (per-step override subset, NOT the full step sequence). The full step sequence lives in the workflow body / definition file (per §6.2 `@step("classify_intent")` example — runtime workflow code, not manifest data). Operator ratified Path A 2026-05-20 (extend `execute_workflow()` signature with a separate `steps: Sequence[WorkflowStep]` parameter; introduces a new `WorkflowStep` record + new `StepKind` enum materializing §5.2's 5-value step-kind taxonomy verbatim). §25.2 signature amended in-place this session (pre-Accepted promotion; not yet consumed by downstream artifacts beyond the in-session CP plan v2.11 which is also amended in-session). Plan v2.11 U-CP-56 signature + AC #1 / #4 absorbed the parameter change at the same session. Both files carry the v1.4 in-session-amendment marker. This is the second adjacent-finding-class amendment at v1.4 (the first being Path B per §D above); both are operator-authority-applied per Phase-7 in-CLI revision discipline.

**Phase-7 fork-resolution status.** `.harness/class_1_tension_u_rt_44_workflow_loop_drain.md` status: OPEN-RESOLVING (entry-point lock 2026-05-20) → spec-side absorbed at v1.4 → plan-side pending at CP plan v2.11 → implementation pending → runtime un-strike pending → CLOSED at full arc completion. Per `Project_Workflow_v1_8.md` §2.7.6: Phase-7 sub-phase 7b execution may resume at CP plan v2.11 + C-CP-25 unit land; U-RT-44 AC #2 + U-RT-49 ACs remain STRUCK until runtime refactor.

## Change-note (v1.4 → v1.5)

**Scope of revision.** Phase-7 design-substrate revision per `Project_Workflow_v1_8.md` §2.7.6 (Class 1 fork back-flow routing) absorbing operator-ratified Q1e + Q2-bounded + Q3c + Q4-resolve-next-session recommendations from `.harness/fork_u_rt_49_cost_attribution_invocation_underspec.md`. The revision adds one new subsection (§25.9 Cost-attribution emission composition) and updates the §[traceability] matrix C-CP-25 row + §[coherence pass] for v1.5 verification + Filing footer. Three amendment sites:

| Site | Amendment shape | Substrate source |
|---|---|---|
| **§25.9 NEW subsection — Cost-attribution emission composition (propagated; step-body-owned)** | New subsection appended after §25.8. Establishes that cost-attribution invocation follows the §25.5 propagated pattern (analogous to retry.attempt / breaker.tripped / fallback.triggered "Driver does not synthesize; it propagates step body's emission"). Step body owns the chain invocation site; driver passes through; `DriverContext` Protocol per §25.2 carries no cost-chain field obligation at v1.5; chain output is a 12-field `SpanCostRecord` carrier (per OD plan v2.8 §3.5.3 D-5 growth) which downstream OD audit-ledger writers consume at their own composition seam (NOT specified at §25.9; not materialized at HEAD; tracked at `.harness/fork_cost_record_audit_ledger_wiring_residual.md`); cost-attribution invocation is separate from the §5.1 closed-at-8 lifecycle event channel — no new event class introduced; `SpanCostInputs` sourced from step body's local provider-invocation closure (no shared cross-axis carrier at v1.5; scope-bounded to `SINGLE_THREADED_LINEAR` per §25.1); composition with §25.6 replay-resumption skip semantics (skipped steps do NOT re-fire cost-attribution invocation, preserving per-attempt-once discipline); `PRICE_TABLE_REF` substitution remains a bounded H_E residual per X-AL-2, tracked at `.harness/fork_price_table_ref_substitution_retirement.md` (filed alongside this revision); cost-attribution failure absorbed into §25.7 `CP-FAIL-DRIVER-STEP-FAILURE` (no new fail class). | Operator-ratified `.harness/fork_u_rt_49_cost_attribution_invocation_underspec.md` Q1–Q4 (2026-05-20); `Spec_Operational_Discipline_v1_3.md` C-OD-14 composition (§14.1 per-span cost formula + §14.2 sandbox-tier overhead + §14.4 idempotency-key join contract — `SpanCostRecord` carries parent's `idempotency_key` per C-IS-05); `Phase_7_Meta_Architecture_v1.md` X-AL-2 retirement criterion |
| **§[traceability] — C-CP-25 row extension at v1.5** | C-CP-25 row (originally added at v1.4) extended with a new cross-axis substrate consumed entry: `Spec_Operational_Discipline_v1_4.md` C-OD-14 §14.1 + §14.2 + §14.4 + §14.5 (cost-attribution chain composition consumed by step-body-owned propagated emission per §25.9). No new R-CP-NN row cell mark — cost-attribution emission is a §25.9 composition obligation, not a new PRD requirement. ADR commitment row preserved verbatim from v1.4 — ADR-F3 / ADD §3.1.1 / ADD §3.1.2 still apply; no new ADR introduced at v1.5. | §25.9 cross-axis substrate consumption |
| **§[coherence pass] — v1.5 verification line** | Extended with v1.5 amendment-site verification line per Workflow v1.7 §7 fidelity-grammar: inputs read (operator-ratified Q1e/Q2/Q3/Q4 from sub-fork record + OD spec v1.4 C-OD-14 5-step composition + Meta-Architecture X-AL-2); ingestion contract (Phase-7 architectural-tension-resolution substrate; in-CLI per CLAUDE.md §4.3); tensions surfaced (Class 1 sub-fork at `.harness/fork_u_rt_49_cost_attribution_invocation_underspec.md` — RESOLVING at v1.5 spec absorption + downstream CP plan v2.13 + runtime smoke test extension); self-audit (no Pattern P1 cross-artifact name drift — §25.9 cites §5.1 closed-at-8 + §25.5 propagated-pattern rows + C-OD-14 5-step + §14.5 12-field carrier + §25.6 skip semantics + §25.7 fail-class taxonomy verbatim with section anchors; no new enum / no new type / no new fail class introduced at v1.5; no Pattern P2 verbatim-claim-contradicted — every citation byte-exact). | `spec-writer` §"Workflow at runtime" protocol + workspace `CLAUDE.md` invariant I-1 |

Workflow v1.7 §7 fidelity-grammar discipline applied across all v1.5 amendment sites: no Pattern P1 cross-artifact name drift (§5.1 closed-at-8 lifecycle event taxonomy preserved verbatim — cost-attribution is NOT a §5.1 event class; §25.5 propagated-pattern row vocabulary reused at §25.9 verbatim; C-OD-14 5-step composition citations match `Spec_Operational_Discipline_v1_4.md` byte-exact; `SpanCostRecord` 12-field carrier shape consumed verbatim from OD spec v1.4 §14.5); no Pattern P2 verbatim-claim-contradicted (all "per §N" + "per C-OD-NN §M" + "per X-AL-N" citations verify against source files); citation anchors substrate-verified per `Project_Workflow_v1_8.md` §7.4.2 byte-exact grammar + `CLAUDE.md` invariant I-1.

**Status posture.** `Status: Proposed` carries forward from v1.4 — promotion to `Accepted` blocked until C-CP-25 atomic units land at CP plan v2.13 + runtime un-strike completes at U-RT-49 cost-attribution AC.

**Sections preserved verbatim from v1.4.** All v1.4 content — Status block (revision pass extends the row; substantive content of v1.4 entries preserved); Change-note (v1.3 → v1.4) section in full including Adjacent-defect findings; §Front-matter; §1 C-CP-01 through §9 C-CP-09; §10 C-CP-10 through §24 C-CP-24; §25 C-CP-25 §25.1 through §25.8 (the v1.4-authored core driver contract — entirely preserved at v1.5; v1.5 amendment is purely additive at §25.9); §[carry-forwards] [CF-1] + [CF-2]; §[traceability] matrix (preserved except C-CP-25 row extended with C-OD-14 substrate-consumed entry); §[coherence pass] v1.3 + v1.4 verification lines preserved.

**Changes inline.** Status block (Revision row extended with v1.5 entry; Revision date row extended noting same-day v1.5 pass; Source-set extended with sub-fork record + OD spec v1.4 + X-AL-2; Entry authorization replaced with v1.5 sub-fork; Exit gate updated to cite CP plan v2.13 + smoke test extension + parent fork closure). This Change-note (v1.4 → v1.5) section. §25.9 new subsection (added after §25.8, before `---` separator). §[traceability] matrix C-CP-25 row extension. §[coherence pass] v1.5 verification line extension. Filing footer updated to v1.5.

**Cross-cascade-step coordination.** CP spec v1.5 produces one downstream effect:

| Downstream step | Substrate consumed from CP spec v1.5 |
|---|---|
| CP plan v2.12 → v2.13 revision-pass (`implementation-planner`) | §25.9 cost-attribution emission composition → single-section absorption at CP plan §25.9 footnote / U-CP-NN unit referring to step-body invocation site; no new atomic unit required (the §25.9 contract is convention-level, materializable at step body authoring time; the U-RT-49 smoke test step body materializes the convention). Plan revision is a contract-prose absorption pass, not a unit-decomposition pass. |

Downstream Phase-7 implementation effect: at smoke test extension, `harness-runtime/tests/integration/test_run_smoke.py` step body fires `ctx.cost_chain.compute_per_attempt_cost(inputs, mock_rates)` via `compute_span_cost_with_rates` bypass; un-strikes U-RT-49 cost-attribution AC; un-strikes the U-RT-49 fork-extension record's STRIKE row; closes `.harness/fork_u_rt_49_cost_attribution_invocation_underspec.md`; fully closes the parent `.harness/class_1_tension_u_rt_44_workflow_loop_drain.md` (CLOSED-PARTIAL since Lane 6 → fully CLOSED).

**Adjacent-defect findings surfaced (not patched at v1.5).** Per `spec-writer` skill §"Failure mode FM-2" no-extension discipline:

- **Open architectural question carried forward (cross-topology cost-attribution boundary; Class 3 informational).** At `SINGLE_THREADED_LINEAR` (v1.4 scope) the "step body owns cost-attribution" convention is unambiguous — one step body = one provider call = one cost-attribution invocation site. At non-linear topologies (sub-agent-dispatch / orchestrator-workers / multi-attempt per §10.1 6-class taxonomy) the "step body" boundary becomes ambiguous: a dispatched sub-agent is itself a workflow with its own cost emissions; cost composition across the parent / child boundary needs a contract. NOT a v1.5 defect — v1.5 scope explicitly carries forward §25.1 SINGLE_THREADED_LINEAR-only scope. Surface as a Phase 7 sub-phase 7c CXA seam candidate when the first non-linear topology is materialized; new CP spec revision-pass owed at that time.

- **`PRICE_TABLE_REF` bounded substitution carried forward (X-AL-2 residual; Class 3 substitution-retirement).** Filed at `.harness/fork_price_table_ref_substitution_retirement.md` alongside this v1.5 spec revision. Rate-table authoring is genuine OD-axis work (~100–200 LOC: rate tables for the 3 committed providers per ADR-F1 v1.2 — Anthropic / OpenAI / Ollama — per-model pricing + refresh contract). Scope-bounded; carries into sub-phase 7d substitution-retirement events. Filing the carry-forward record IS in scope at v1.5; resolving it is not.

- **`SpanCostRecord` → audit-ledger writer wiring residual (Class 3 informational; bounded; caught at v1.5 spec-writer audit).** Initial §25.9 draft included the prose "emission target is the OD audit-ledger substrate per C-OD-14 §14.4 idempotency-key join contract." Verification against OD spec v1.3 source text §14.4 surfaced that §14.4 is the *join key contract* (cost record carries parent's `idempotency_key` per C-IS-05), NOT an emission contract — Pattern P2 candidate (verbatim-claim-contradicted). §25.9 prose re-worded to drop the false emission claim and describe carrier production only; the downstream wiring path between the produced `SpanCostRecord` and the OD audit-ledger writer is left out of scope at v1.5 and is not materialized at HEAD. Filed at `.harness/fork_cost_record_audit_ledger_wiring_residual.md` as a bounded residual. Resolution may require an OD spec amendment naming the seam (the canonical §-pin owning the audit-ledger ingestion contract for `SpanCostRecord` is unclear at audit time — `harness-od/CLAUDE.md` §1.3 contains an unverified citation to "C-OD-14 §14.5.1" that does not match the OD spec v1.3 source text at §14.5.1 either). Surface as 7c CXA seam candidate or 7d substitution-retirement adjacent event.

**Phase-7 fork-resolution status (v1.5 update).** `.harness/fork_u_rt_49_cost_attribution_invocation_underspec.md` status: OPEN-RESOLVING (Q1–Q4 ratified 2026-05-20) → spec-side absorbed at v1.5 → plan-side pending at CP plan v2.13 → runtime un-strike pending at smoke test extension → CLOSED at smoke test materializes U-RT-49 AC un-strike. Parent `.harness/class_1_tension_u_rt_44_workflow_loop_drain.md`: CLOSED-PARTIAL → fully CLOSED at the same arc completion.

---

## Front-matter

[§Axis declaration + §Axis-grounding note + §PRD requirement scope + §ADR scope + §Cross-axis citation substrate + §Persona-linkage substrate + §Scope and out-of-scope preserved verbatim from v1.3 (which preserved verbatim from v1.2 except [carry-forwards] line revised at v1.3 to closure).]

---

## §1 C-CP-01 — Capability-aware multi-LLM provider abstraction

[Preserved verbatim from v1.3 (which preserved verbatim from v1.2).]

## §2 C-CP-02 — Layered cheapest-deterministic-first routing strategy

[Preserved verbatim from v1.3 (which preserved verbatim from v1.2).]

## §3 C-CP-03 — Per-layer time budget with deterministic-fallback-on-budget-exceeded

[§3.1 + §3.2 + §3.3 + §3.4 preserved verbatim from v1.3 (which preserved verbatim from v1.2).]

### §3.5 `fallback.*` and `harness.breaker.*` and `retry.*` span attribute namespaces declared at this contract (v1.3 amendment absorbing D6 v1.2 §1.2.2)

[Preserved verbatim from v1.3.]

---

## §4 C-CP-04 — Cross-family fallback chain composition

[Preserved verbatim from v1.3 (which preserved verbatim from v1.2).]

## §5 C-CP-05 — F3 capability-floor lifecycle event surface

[§5.1 + §5.2 + §5.3 preserved verbatim from v1.3 (which preserved verbatim from v1.2).]

### §5.4 Sampling discipline per event class (v1.3 amendment to retry.attempt row)

[Preserved verbatim from v1.3.]

[§5.5 + §5.6 + §5.7 preserved verbatim from v1.3 (which preserved verbatim from v1.2).]

---

## §6 C-CP-06 — Manifest-declaration invocation discipline with per-step opt-in override

[Preserved verbatim from v1.3 (which preserved verbatim from v1.2).]

## §7 C-CP-07 — Engine class committed per deployment surface

[Preserved verbatim from v1.3 (which preserved verbatim from v1.2).]

## §8 C-CP-08 — Replay-resumption semantics per engine class (R-CP-07 — F2-12 ✅ CLOSED at v1.3)

[Preserved verbatim from v1.3 (including all v1.3 amendments at contract surface + PRD requirement satisfied + ADR commitments honored + Cross-axis citation rows + §8.1 + §8.2 + §8.3 stubs + §8.4 F2-12 closure record).]

---

## §9 C-CP-09 — `engine.*` span attribute namespace declaration (v1.3 amendment absorbing D1 v1.2)

[Preserved verbatim from v1.3 (including §9.1 4-attribute declarations table + §9.2 + §9.3 + §9.4 D6 ingestion contract).]

---

## §10 C-CP-10 through §24 C-CP-24

[All sub-sections preserved verbatim from v1.3 (which preserved verbatim from v1.2).]

---

## §25 C-CP-25 — Workflow execution driver (v1.4 amendment — new contract scoped to `SINGLE_THREADED_LINEAR` topology + `pure-pattern-no-engine` / `save-point-checkpoint` engine classes)

**Contract surface.** A deterministic step iteration driver that consumes a `WorkflowManifestEntry` (per §6.1) + `HarnessContext` (per `Spec_Harness_Runtime_v1.md` U-RT-44 surfaces), dispatches each step through the cap-aware router (per §1) under the manifest's effective bindings (per §6.2 + U-CP-14 resolver), emits the 8-class lifecycle event surface at its declared boundaries (per §5.1) including `workflow.start` / per-step `step.boundary` / terminal exit, polls `ctx.drained_flag` at per-step boundaries (per `Spec_Harness_Runtime_v1.md` §11 C-RT-11), and returns a typed `RunResult` whose `status` enum admits `drained` (per `Spec_Harness_Runtime_v1.md` §11 settlement — terminal-status observability replaces a `DRAINED` lifecycle-event class which does not exist in the §5.1 closed-at-8 taxonomy).

**PRD requirement(s) satisfied.** R-CP-04 (workflow lifecycle event surface visible at run-event surface as distinct event classes — driver materializes the emission site for `workflow.start` + per-step `step.boundary` + conditionally `workflow.resumption` + conditionally `lease.acquired` / `lease.released` at this contract); R-CP-07 (replay-resumption semantics visible at run resumption — driver composes with §8.2 idempotency-key join at re-entry under `save-point-checkpoint`).

**ADR commitment(s) honored.** ADR-F3 v1.1 §Decision (iv) (F3 capability-floor (iv) — "workflow lifecycle event surface visible at run-event surface as distinct event classes" — C-CP-25 is the derivative materialization site for this foundational commitment); ADD v1.3 §3.1.1 (D1 v1.2 engine-class taxonomy parametric commitment per deployment surface — C-CP-25 consumes `EngineClass` enum via §7.1 + §8.1 binding); ADD v1.3 §3.1.2 (D4 v1.1 / D5 v1.3 six-pattern topology taxonomy — C-CP-25 consumes `TopologyPattern` enum via §10.1 and at v1.4 materializes one row).

**Cross-axis citation.** `Spec_Information_Substrate_v1.md` C-IS-05 (state-ledger entry shape — driver per-step ledger-entry composition); C-IS-07 (state-ledger read contract — driver replay-resumption read); C-IS-10 §10.1 (state-ledger-entry-shape export); C-IS-10 §10.2 (idempotency-key join export — driver re-entry); C-IS-11 (state-ledger append discipline); `Spec_Harness_Runtime_v1.md` §11 C-RT-11 (drain semantics composition seam — driver consumes `HarnessContext.drained_flag` ownership).

**Persona linkage.** Persona §4 (99.9%+ SLO at tens-concurrent — driver determinism + drain composition + replay-resumption are foundational to SLO surface); §7 (workflow-definition surface — driver materializes manifest execution); §10.1 (durable-execution capability requirement — driver is the workflow-iteration site composing with F3 capability-floor (iv)).

**Specification content.**

### §25.1 Scope (in scope at v1.4)

In scope at v1.4: topology pattern `SINGLE_THREADED_LINEAR` only (per §10.1 six-pattern topology taxonomy, row 1); engine classes `pure-pattern-no-engine` + `save-point-checkpoint` only (per §7.1 five-element engine-class taxonomy, rows 3 + 2 respectively).

**Explicitly deferred at v1.4** (per workspace `Phase_7_Meta_Architecture_v1.md` §7.7 X-AL-3 — no silent design extension at Phase-7 execution-time):

| Topology pattern | Deferral notation |
|---|---|
| `orchestrator-workers` | Extension contract (C-CP-25.b or C-CP-26) authored when the first multi-worker workflow unit demands materialization. |
| `decentralized-handoff` | Same as above. |
| `hierarchical-delegation` | Same as above. |
| `evaluator-optimizer` | Same as above. |
| `parallelization` | Same as above. |

| Engine class | Deferral notation |
|---|---|
| `event-sourced-replay` | Engine-class extension to C-CP-25 (or separate contract) authored when first event-sourced-replay workflow unit demands materialization. |
| `reconciler-loop` | Same — extended when first K8s-resident workflow demands materialization. |
| `WAL-segment` | Same — extended when first segmented-resume workflow demands materialization. |

Any attempt at v1.4 to drive a workflow whose `manifest_entry.topology` is non-`SINGLE_THREADED_LINEAR` raises a typed `TopologyPatternNotYetMaterializedError` (per §25.8 failure-mode taxonomy). Manifest validation at workflow-binding time (per §6.1 manifest schema + §6.4 audit-surface composition) rejects manifests whose `topology` field is non-`SINGLE_THREADED_LINEAR` at v1.4 with this typed error. Same discipline applies to non-in-scope engine classes via `EngineClassNotYetMaterializedError`.

### §25.2 Signatures

```text
record RunResult {
  workflow_id        : string
  run_id             : string
  status             : RunStatus
  terminal_step_index: Optional<int>            // present on drained/failed
  partial_state      : Optional<TerminalState>  // present on drained/failed
  final_state        : Optional<TerminalState>  // present on success
  fail_class         : Optional<FailClass>      // present on failed
}

enum RunStatus {
  SUCCESS,
  DRAINED,                                       // per Spec_Harness_Runtime_v1.md §11 C-RT-11
  FAILED,
  PARTIAL                                        // reserved for future multi-step error modes
}

// In-session amendment §E (2026-05-20) — step-sequence source.
// Step sequence lives in the workflow body, not the manifest. The driver
// takes the step sequence as an explicit parameter alongside manifest_entry.
record WorkflowStep {
  step_id      : StepID                          // per harness-core
  step_kind    : StepKind                        // per §5.2 5-value enum verbatim
  step_payload : Mapping[str, Any]               // opaque to driver; consumed by router per §1
}

enum StepKind {
  DECLARATIVE_STEP,                              // "declarative-step" per §5.2
  INFERENCE_STEP,                                // "inference-step"   per §5.2
  TOOL_STEP,                                     // "tool-step"        per §5.2
  HITL_STEP,                                     // "HITL-step"        per §5.2
  SUB_AGENT_DISPATCH                             // "sub-agent-dispatch" per §5.2
}
// Closed at cardinality 5 — extension would require Workflow §4.1.2 Class-2
// revision of §5.2 step.kind enum.

function execute_workflow(
    manifest_entry : WorkflowManifestEntry,     // per §6.1 schema
    steps          : Sequence[WorkflowStep],    // step sequence in declaration order (in-session amendment §E)
    run_id         : string,                     // harness-unique; root idempotency_key derives from this
    ctx            : HarnessContext              // per Spec_Harness_Runtime_v1.md §11 U-RT-44 — carries drained_flag, ledger handle, OTel tracer
) -> RunResult
    // SINGLE_THREADED_LINEAR + (pure-pattern-no-engine | save-point-checkpoint) only at v1.4;
    // rejects out-of-scope topology / engine class at entry.
```

`TerminalState` record shape: workflow-class-dependent; deferred to implementation discretion (per §25.9).

`FailClass` enum: per §25.8 failure-mode taxonomy + composition with C5 cause-attribution catalog at `c5-validation-contract` SKILL.md (substrate-anchored).

### §25.2.1 StepDispatcher Protocol + StepExecutionContext (v1.6 amendment per operator-ratified Path A — `.harness/class_1_tension_c_rt_17_step_dispatcher_parent_context_gap.md`)

**StepDispatcher Protocol.** The driver invokes step bodies through a Protocol-typed dispatcher. Pre-v1.6 the Protocol existed at the code surface (`harness-cp/src/harness_cp/workflow_driver.py:151`) but was not formally pinned in the spec; v1.6 pins it explicitly as part of the Path A resolution. The Protocol shape at v1.6:

```text
@runtime_checkable
class StepDispatcher(Protocol):
    def dispatch(
        binding      : StepEffectiveBinding,        // per C-CP-06 §6.2 per-step override evaluator output
        step         : WorkflowStep,                 // per §25.2 record (step_payload opaque per §25.3.3.4)
        *,
        step_context : StepExecutionContext,        // per §25.2.1 below — keyword-only at v1.6
    ) -> Mapping[str, Any]                          // step output (driver accumulates into final/partial_state)
        ...
```

The keyword-only `step_context` parameter is required by Protocol conformance at v1.6. Dispatchers that do not need parent context (e.g., the v1.6 C-RT-15 LLM-dispatch composer and the C-RT-16 retry/breaker/fallback wrapper) accept it via Protocol conformance but do not consume it; reserved for v1.7+ surfaces that may bind parent context to dispatcher-specific span attributes. Dispatchers that need parent context (the v1.6 C-RT-17 sub-agent dispatch composer per `Spec_Harness_Runtime_v1.md` v1.6 §14.7) consume `step_context` to compose `HandoffContext` per C-CP-13 §13.1 + invoke `RuntimeHandoffRegistry.dispatch(...)` per C-CP-12 + compose audit-trail-link per C-CP-13 §13.5.

**StepExecutionContext record.** 8-field record composed by the driver per step from run-level state + per-step-iteration state:

```text
record StepExecutionContext {
  parent_action_id         : string         // composed: f"workflow:{workflow_id}:step:{step_index}" per
                                            //   existing pattern at workflow_driver.py
                                            //   (_append_step_ledger_entry)
  parent_gate_level        : GateLevel      // seed input for C-CP-12 §12.2 sub-agent gate-level
                                            //   max() composition; v1.6 MVP default GateLevel.AUTO
                                            //   per C-CP-12 §12.4 deferred-to-implementation-discretion
                                            //   (v1.7+ operator surfaces via WorkflowManifestEntry
                                            //   extension)
  parent_sandbox_tier      : SandboxTier    // seed input for C-AS-11 monotonic-ascension at sub-agent
                                            //   dispatch; v1.6 MVP default SandboxTier.TIER_1_PROCESS
                                            //   (lowest tier; consistent with sandbox_tier_floor
                                            //   pattern's lowest tier); v1.7+ manifest-surfaced
  parent_actor             : Actor          // from ctx.ledger_writer.actor per
                                            //   LedgerWriter construction-time identity
                                            //   (IS-axis Actor type per C-IS-05 §5)
  parent_entry_hash        : string         // hash of prior-step audit-ledger entry per C-CP-13 §13.5
                                            //   LedgerEntryRef.entry_hash. v1.6 MVP empty-string
                                            //   sentinel — child sub-workflow shares parent
                                            //   LedgerWriter per Spec_Harness_Runtime_v1.md v1.6
                                            //   §14.7.4 child-context sharing discipline; explicit
                                            //   entry-hash propagation deferred to v1.7+ arc that
                                            //   adds LedgerWriter.last_appended_entry_hash API
  parent_idempotency_key   : string         // derived from existing _compute_step_idempotency_key
                                            //   (run_idempotency_key, step_index) per §25.3.3.7 +
                                            //   §25.6
  tenant_id                : Optional<string>  // None at v1.6 MVP — multi-tenancy not committed at
                                               //   v1.6 stack per Target_Stack_Commitment_v1.md;
                                               //   v1.7+ extension when multi-tenancy commits
                                               //   (sourced from future HarnessContext.tenant_id
                                               //   or RuntimeConfig.tenant_id)
  step_index               : int            // per-iteration loop variable from §25.3.3 step
                                            //   enumeration
}
```

**Composition discipline at the driver.** The driver composes one `StepExecutionContext` per step at the §25.3.3.4 dispatch site, before invoking `step_dispatcher.dispatch(binding, step, step_context=step_context)`. Composition is from driver-tracked state (4 fields composed deterministically: `parent_action_id`, `parent_actor`, `parent_idempotency_key`, `step_index`) + 4 MVP-default-bounded fields (`parent_gate_level`, `parent_sandbox_tier`, `parent_entry_hash`, `tenant_id`).

**Anti-extension invariant.** The 4 MVP-default-bounded fields are documented as deferred-to-implementation-discretion at v1.6 per the C-CP-12 §12.4 pattern. v1.7+ extension to surface them via operator-authored `WorkflowManifestEntry` extension fields is a Workflow §4.1.2 Class-2 amendment to this contract, NOT a Phase-7 implementation-time amendment (per X-AL-3). Implementation MUST NOT introduce silent extensions to surface the 4 fields from non-spec-pinned sources at v1.6.

**Step body opaque-to-driver invariant preserved.** `step_context` carries metadata about the step's execution environment (driver-composed); the existing C-CP-25 §25.3.3.4 invariant that "Step body is opaque to the driver" remains — `step_context` is NOT step body content, and the driver does not introspect `step.step_payload` to compose `step_context`.

### §25.3 Iteration discipline

The driver implements the following deterministic sequence (preserved structurally from `.harness/c_cp_25_workflow_driver_recommendation.md` §4.4 verbatim):

1. **Validate.** Reject if `manifest_entry.topology` ≠ `SINGLE_THREADED_LINEAR` → raise `TopologyPatternNotYetMaterializedError`. Reject if `manifest_entry.engine_class` ∉ `{pure-pattern-no-engine, save-point-checkpoint}` at v1.4 → raise `EngineClassNotYetMaterializedError`.
2. **Emit `workflow.start`** per §5.1 with minimum attributes per §5.2 (`workflow.id`, `workflow.class`, `engine.class`, `manifest.entry_id`, `idempotency_key` root). Always-sampled per §5.4.
3. **Iterate steps in declaration order.** For each step `s` in the `steps` parameter (declaration-order per in-session amendment §E; SINGLE_THREADED_LINEAR has no parallel / fan-out branching):
   1. **Drain check (pre-step).** If `ctx.drained_flag.is_set()`: do NOT enter step, do NOT emit a `step.boundary` event (preserves §5.2 step.kind 5-value enum without extension; matches §25.4 driver-entry row pattern of return-without-emit), return `RunResult(status=DRAINED, terminal_step_index=s.index-1, partial_state=<accumulated>)`. Terminal observability is the `RunResult.status='drained'` + `terminal_step_index` return (no lifecycle event at this site).
   2. **Resolve binding.** `binding = resolve_step_binding(manifest_entry, s.id)` per U-CP-14 (§6.2 per-step override surface).
   3. **Acquire lease (if binding requires).** Per §5.1 + §5.3: if `binding` requires lease acquisition under §5.3 `lease.mechanism` enum (mechanism-to-engine-class mapping is under-specified at CP spec v1.4 per Change-note "Adjacent finding §B"; resolved at implementation time per `c1-orchestration-control` SKILL.md substrate), acquire and emit `lease.acquired` per §5.2 minimum attribute set.
   4. **Dispatch.** Invoke the step body through the cap-aware router (`route_invocation(binding, s.payload, ctx)` per §1 / §1.3 manifest-as-auditable-default routing surface). Step body is opaque to the driver; the router owns provider / model / engine dispatch. **v1.6 Path A amendment**: the driver composes a `StepExecutionContext` per §25.2.1 from driver-tracked run-level state (`run_id`, `workflow_id`, `step_index`, `ctx.ledger_writer.actor`, run-scope idempotency key, plus the 4 MVP-default-bounded fields) and passes it to the dispatcher via the new keyword-only `step_context` parameter (`step_dispatcher.dispatch(binding, step, step_context=step_context)`). The composition is metadata about the step's execution environment, not step body content — the opaque-to-driver invariant on `step.step_payload` is preserved verbatim.
   5. **Emit `step.boundary`.** Per §5.1 + §5.2 attribute set (`workflow.id`, `step.index`, `step.kind`, `idempotency_key` per `Spec_Information_Substrate_v1.md` C-IS-05). Sampling per §5.4 (head-based-dev base-rate / tail-based-prod default).
   6. **Release lease (if held).** Emit `lease.released` per §5.1 + §5.2.
   7. **State-ledger append.** Compose per `Spec_Information_Substrate_v1.md` C-IS-05 entry shape via C-IS-10 §10.1 export → C-IS-11 append. `idempotency_key` derives from `(run_id, step.index)` per §8.2 join discipline.
   8. **Drain check (post-step).** If `ctx.drained_flag.is_set()`: return `RunResult(status=DRAINED, terminal_step_index=s.index, partial_state=<accumulated including this step>)`.
4. **Emit terminal.** No new event class — the absence of a further `step.boundary` plus the `RunResult.status` return is the terminal observable. (Per `Spec_Harness_Runtime_v1.md` §11 v1.2 settlement — no `DRAINED` event class in §5.1 closed-at-8 taxonomy; terminal status is observable via return value, not via lifecycle event.)
5. **Return** `RunResult(status=SUCCESS, final_state=<accumulated>)`.

### §25.4 Drain protocol — composition with `Spec_Harness_Runtime_v1.md` §11 C-RT-11

| Site | Driver behavior |
|---|---|
| **Driver entry** | If `ctx.drained_flag.is_set()` at entry: return `RunResult(status=DRAINED, terminal_step_index=null, partial_state=null)` BEFORE emitting `workflow.start` AND BEFORE topology + engine-class validation (operator-ratified ordering 2026-05-20). Drain is a system-shutdown signal that supersedes typed-validation-error surfacing; manifest defects in a workflow whose caller is mid-shutdown surface DRAINED, not the typed error. Trade-off: programming defects (invalid manifest at v1.4 in-scope set) are silently absorbed under drain. Acceptable because drain is the shutdown contract — caller has already abandoned the workflow. (If a future workload class needs typed-error surfacing under drain, a per-manifest opt-in can be added at C-CP-25 v1.5+ without breaking this contract.) |
| **Per-step pre-entry** (§25.3.3.1) | Drain check before entering next step. On flag-set: do NOT emit `step.boundary` (preserves §5.2 step.kind 5-value enum); do NOT dispatch step body; return `RunResult(status=DRAINED, terminal_step_index=s.index-1)`. Terminal observability is the `RunResult` return only at this site. |
| **Per-step post-exit** (§25.3.3.8) | Drain check after step body completes + state-ledger append. On flag-set: state-ledger append for the just-completed step HAS persisted; return DRAINED with that step counted. |
| **Mid-step** | NO drain check. Step bodies run to completion (or to their own internal failure). This matches `Spec_Harness_Runtime_v1.md` §11 v1.2: "Completes the current in-flight step (no mid-step interruption)." |
| **Bounded wait** | The driver does NOT own the bounded-wait timeout itself. Per `Spec_Harness_Runtime_v1.md` §11 the timeout lives in `shutdown(ctx, timeout=...)` at C-RT-10. If the step body exceeds the wait, runtime force-shutdown proceeds; driver may not complete its post-step accounting. `Spec_Harness_Runtime_v1.md` C-RT-14 `RT-FAIL-DRAIN-TIMEOUT` covers this. |

### §25.5 Lifecycle event emission boundaries (single-threaded-linear filter over §5.1 closed-at-8 taxonomy)

| §5.1 event class | Emitted at `SINGLE_THREADED_LINEAR` at v1.4? | Site |
|---|---|---|
| `workflow.start` | **YES (always)** | §25.3.2 driver entry post-validation |
| `step.boundary` | **YES (per completed step exit)** | §25.3.3.5 every step exit AFTER step body completes. NOT emitted at pre-step-entry drain (per §25.3.3.1; preserves §5.2 step.kind 5-value enum). |
| `fallback.triggered` | **CONDITIONAL** | Only if step body triggers fallback (per §3.5 `fallback.*` namespace). Driver does not synthesize; it propagates step body's emission. |
| `retry.attempt` | **CONDITIONAL** | Same — step body owns; driver propagates. |
| `breaker.tripped` | **CONDITIONAL** | Same. |
| `lease.acquired` / `lease.released` | **CONDITIONAL** | Lease emission per §5.3 `lease.*` namespace contract (`lease.mechanism` enum: `{engine_native, redis_lease, db_unique_constraint, worktree_isolation, etcd_cas, per_segment}`); specific per-engine-class lease requirement is NOT explicitly enumerated at CP spec v1.4 — see Change-note "Adjacent-defect findings" §B. Driver contract states "emit `lease.acquired` + `lease.released` if and only if the step's effective binding requires lease acquisition under §5.3 `lease.mechanism` enum; mechanism-to-engine-class mapping is under-specified at CP spec and resolved at implementation time per `c1-orchestration-control` SKILL.md substrate." Not a fixed assertion per engine class. |
| `workflow.resumption` | **CONDITIONAL** | Only if driver entry is a re-entry per §8 replay-resumption semantics. At v1.4 scope: emit on re-entry if `manifest_entry.engine_class == 'save-point-checkpoint'` AND `run_id` matches a prior `Spec_Information_Substrate_v1.md` C-IS-05 ledger entry. Always-sampled per §5.4. Composition with §8.2 idempotency-key join. |

No new event classes introduced at v1.4 — C-CP-25 strictly composes against the §5.1 closed-at-8 taxonomy. (Extension to the §5.1 taxonomy would require a separate ADR-level Workflow §4.1.2 Class-2 revision per §5.1 closure invariant.)

### §25.6 Composition with §8.2 idempotency-key join (replay-resumption seam)

Per §8.2 per-engine-class F2 join discipline (preserved verbatim from v1.3):

- **`pure-pattern-no-engine` row** (§8.2): "F2 state-ledger native — `idempotency_key` is the primary dedup substrate; replay reads F2 entries chronologically per C-IS-07 read contract."
- **`save-point-checkpoint` row** (§8.2): "Checkpointer state joins F2 state-ledger on `idempotency_key`; harness composition layer reads F2 entries by `action_id` and applies dedup per `prior_event_hash` chain integrity (C-IS-06)."

At driver re-entry under either engine class within v1.4 scope:

1. Driver computes `run_idempotency_key = sha256(run_id, manifest_entry.workflow_id, manifest_entry.entry_version)`.
2. Reads `Spec_Information_Substrate_v1.md` F2 state-ledger via C-IS-07 read contract for entries matching `run_idempotency_key` prefix.
3. If matches exist, emits `workflow.resumption` per §5.1 + §5.2 minimum attribute set (with `resumption.kind` per §8.1).
4. Skips already-replayed steps; resumes at first unmaterialized step.
5. Per-step `idempotency_key = sha256(run_idempotency_key, step.index)` per §8.2 dedup semantics.

`pure-pattern-no-engine` is the simpler case (no engine-internal replay state; F2 ledger is the sole substrate). `save-point-checkpoint` requires the resumption read above plus composition with checkpointer state per §8.2 row 2.

### §25.7 Failure-mode taxonomy

| Fail class | Trigger | Driver behavior |
|---|---|---|
| `CP-FAIL-DRIVER-TOPOLOGY-UNSUPPORTED` | `manifest_entry.topology` outside v1.4 scope | `TopologyPatternNotYetMaterializedError` typed error raised at §25.3.1; no events emitted; no ledger entries. |
| `CP-FAIL-DRIVER-ENGINE-CLASS-UNSUPPORTED` | `manifest_entry.engine_class` outside v1.4 scope | `EngineClassNotYetMaterializedError` typed error raised at §25.3.1; no events emitted; no ledger entries. |
| `CP-FAIL-DRIVER-STEP-FAILURE` | Step body raises uncaught exception | Emit `step.boundary` with failure attribute set per §5.2; return `RunResult(status=FAILED, fail_class=<step-specific per c5-validation-contract catalog>)`; drain-flag NOT auto-set (failure ≠ drain). |
| `CP-FAIL-DRIVER-LEDGER-APPEND-FAILURE` | C-IS-11 append fails | Fail-loud; return `RunResult(status=FAILED, fail_class='ledger-append-failed')`. State-ledger fidelity is non-negotiable per ADR-F2 v1.2. |
| `RT-FAIL-DRAIN-TIMEOUT` | (Owned by runtime C-RT-14) | Driver may not complete post-step accounting; runtime force-shutdown. Driver contract is composition-only at this fail class; no driver-side action. |

### §25.8 Deferred to implementation discretion

- Specific `TerminalState` record shape (workflow-class-dependent per §3.1 four-class set + extension flag; downstream cell decision at CP plan v2.11 + implementation).
- Specific runtime structure of step iteration (async generator / coroutine / state machine / etc.) — deferred to implementation; this contract specifies observable behavior, not implementation shape.
- Specific dispatch ordering for step body invocation when the step body is itself an LLM call vs. a tool call vs. a sub-routine — covered by §1 cap-aware router contract.
- Concurrency of `lease.acquired` + `step.boundary` span emission (separate spans or combined-attribute single span) — implementation discretion; sampling per §5.4 preserved across either shape.
- (Removed at v1.4 spec-writer-time per operator Path B: no `drain-aborted-pre-entry` `step.kind` value introduced. §5.2 step.kind 5-value list preserved verbatim. Pre-step-entry drain has no `step.boundary` lifecycle event by design; terminal observability is `RunResult.status='drained'` + `terminal_step_index`.)

### §25.9 Cost-attribution emission composition (v1.5 — propagated; step-body-owned per §25.3.3.4 dispatch)

Per operator ratification 2026-05-20 of recommendation Q1e from `.harness/fork_u_rt_49_cost_attribution_invocation_underspec.md`: cost-attribution emission follows the §25.5 propagated pattern (analogous to `retry.attempt` / `breaker.tripped` / `fallback.triggered` per §25.5 rows: "Driver does not synthesize; it propagates step body's emission").

**Ownership.** The step body — invoked via §25.3.3.4 cap-aware router dispatch — owns the cost-attribution chain invocation site. On step body exit, the step body fires the cost-attribution chain steps per `Spec_Operational_Discipline_v1_3.md` C-OD-14 composition (§14.1 per-attempt cost formula → §14.2 sandbox-tier overhead addition → §14.4 idempotency-key join, which sets the parent's `idempotency_key` per C-IS-05 on the produced `SpanCostRecord`). Driver passes through; driver is unaware of cost-attribution invocation; `DriverContext` Protocol per §25.2 carries no cost-chain field obligation at v1.5.

**Chain output.** Cost-attribution invocation produces a `SpanCostRecord` carrier (12-field shape per OD plan v2.8 §3.5.3 D-5 growth — `provider_discriminator` + `gen_ai_provider_name` + `gen_ai_request_model` rollup keys added). This is the carrier U-OD-21 `rollup_costs_by_axis` consumes (per OD-axis §[traceability] / acc #1) and the carrier downstream OD audit-ledger writers consume at their own composition seam. The §25.9 contract specifies *production of the carrier* via the step-body-owned chain invocation; it does NOT specify the audit-ledger emission wiring (which is OD-owned downstream of carrier production and not yet materialized at HEAD — see `.harness/fork_cost_record_audit_ledger_wiring_residual.md` for the residual record). Cost-attribution emission is a separate substrate channel from §5.1 closed-at-8 lifecycle event taxonomy — no new §5.1 lifecycle event class introduced at v1.5; §5.1 closure invariant preserved verbatim.

**Input sourcing.** The step body sources `SpanCostInputs` (`model`, `provider`, `input_tokens`, `output_tokens`, `rate_key`) from its local provider-invocation closure — the step body invoked the router which invoked the provider client and received the response carrying token counts and model identity; that data is locally available at step exit without requiring a cross-axis carrier. No shared `StepExecutionResult` / `ProviderInvocationRecord` shape authored at v1.5 (scope-bounded to `SINGLE_THREADED_LINEAR` per §25.1; cross-topology composition deferred to first non-linear topology materialization per X-AL-3 anti-leakage).

**Composition with §25.6 replay-resumption.** At driver re-entry, already-replayed steps are skipped per §25.6 step 4 ("Skips already-replayed steps; resumes at first unmaterialized step"). Skipped steps do NOT re-fire cost-attribution emission — the original `SpanCostRecord` (emitted at the original step body exit) persists in the OD audit-ledger substrate per C-OD-14 §14.5 per-attempt discipline. Re-emission of a `SpanCostRecord` for a replayed step would double-count cost; the §25.6 skip semantics intrinsically prevents this.

**Rate substitution carry-forward (v1.5 informational; not patched at v1.5).** The `PRICE_TABLE_REF` substitution at `harness-od/src/harness_od/cost_formula.py` remains a deferred H_E substitution per `Phase_7_Meta_Architecture_v1.md` X-AL-2 retirement criterion ((cited unit IDs landed) ∧ (substituted H_E surface no longer invoked)). U-OD-21 landed at commit `e8fae9c` (first criterion met); `_lookup_rates` raises `RateLookupError` unconditionally at HEAD (second criterion unmet). Step bodies that invoke `compute_per_attempt_cost` at v1.5 supply an explicit `PriceRateEntry` snapshot via the `compute_span_cost_with_rates` bypass surface per OD `cost_formula.py:175-188` documented intent. A separate substitution-retirement record (filed alongside this v1.5 amendment at `.harness/fork_price_table_ref_substitution_retirement.md`) tracks the bounded residual; rate-table authoring is out of scope for v1.5 + this fork-resolution arc.

**Failure-mode.** Cost-attribution emission failure (step body's chain invocation raises) is owned by the step body — the driver propagates by re-raising or absorbing per step-body discipline (typically: log + continue; cost-attribution emission is observability-grade, not state-ledger-grade fidelity per ADR-F2 v1.2). The driver's §25.7 failure-mode taxonomy (5 fail classes) is preserved verbatim from v1.4 — no new fail class for cost-attribution emission. A step body that itself raises during cost-attribution surfaces as `CP-FAIL-DRIVER-STEP-FAILURE` per §25.7 row 3 (step body raised uncaught exception).

---

## §[carry-forwards]

### [CF-1] F2-12 — D1 v1.1 → v1.2 + D6 v1.1 → v1.2 replay-trace-emission contract (✅ CLOSED at v1.3)

[Preserved verbatim from v1.3.]

### [CF-2] Workflow §7 substrate-skill propagation

[Preserved verbatim from v1.3 (which preserved verbatim from v1.2).]

---

## §[traceability]

[Preserved verbatim from v1.3 (which preserved verbatim from v1.2 except D1 + D6 row-label versions updated v1.1 → v1.2) except one row added at v1.4: C-CP-25 row added with R-CP-04 cell mark (driver materializes the emission site for the workflow lifecycle event surface) + R-CP-07 cell mark (driver composes with §8.2 idempotency-key join at replay re-entry); per-row cell marks per traceability matrix convention.]

**C-CP-25 row (v1.4 addition):**

| Contract | R-CP-04 (workflow lifecycle event surface) | R-CP-07 (replay-resumption semantics) | Cross-axis substrate consumed | ADR commitment(s) honored |
|---|---|---|---|---|
| C-CP-25 (workflow execution driver) | ✓ — driver materializes `workflow.start` + per-step `step.boundary` + terminal exit emission per §25.5 lifecycle event filter table | ✓ — driver composes with §8.2 idempotency-key join at re-entry under `save-point-checkpoint` engine class per §25.6 | C-IS-05 (state-ledger entry shape); C-IS-07 (state-ledger read contract); C-IS-10 §10.1 (entry-shape export); C-IS-10 §10.2 (idempotency-key join export); C-IS-11 (append discipline); `Spec_Harness_Runtime_v1.md` §11 C-RT-11 (drain semantics seam); **(v1.5 extension):** `Spec_Operational_Discipline_v1_3.md` C-OD-14 §14.1 (per-span cost formula) + §14.2 (sandbox-tier overhead addition) + §14.4 (idempotency-key join contract — cost record carries parent's `idempotency_key` per C-IS-05) — composition consumed by step-body-owned cost-attribution invocation per §25.9; produces a `SpanCostRecord` carrier (12-field per OD plan v2.8 §3.5.3 D-5) | ADR-F3 v1.1 §Decision (iv) (F3 capability-floor (iv) workflow lifecycle event surface — derivative materialization); ADD v1.3 §3.1.1 (D1 v1.2 engine-class taxonomy); ADD v1.3 §3.1.2 (D4 / D5 topology taxonomy) |

---

## §[coherence pass]

[Audits preserved verbatim from v1.3 (which preserved verbatim from v1.2 as v1.2 point-in-time historical audit per Stage 2 + Stage 3a precedent; v1.3 amendment-site verification inline per Workflow v1.7 §7 fidelity-grammar discipline). The four `spec-writer` SKILL.md "Workflow at runtime" disciplines verify at each v1.3 amendment site: inputs read (PRD v1.1 + ADD v1.3 + ADR-D1 v1.2 + ADR-D6 v1.2); ingestion contract per layer (council deliberation substrate + ADR substrate); tensions surfaced (T-perm-2 + T-perm-3 ENGAGED at council §7; preserved at v1.3); self-audit (no Pattern P1 cross-artifact name drift; no Pattern P2 verbatim-claim-contradicted).]

**v1.4 amendment-site verification (extension per Workflow v1.7 §7 fidelity-grammar discipline applied in-CLI per `CLAUDE.md` §4.3 design-substrate revision discipline).** The four `spec-writer` SKILL.md fidelity disciplines verify at the v1.4 §25 amendment site: inputs read (`.harness/c_cp_25_workflow_driver_recommendation.md` operator-ratified 2026-05-20 + `.harness/class_1_tension_u_rt_44_workflow_loop_drain.md` Class 1 fork OPEN-RESOLVING + ADR-F3 v1.1 §Decision (iv) + `Spec_Harness_Runtime_v1.md` §11 C-RT-11); ingestion contract (Phase-7 architectural-tension-resolution substrate per `systems-architect` skill §4A; operator ratification authorization per workspace `CLAUDE.md` §4.3); tensions surfaced (Class 1 fork at the workflow-execution-driver gap — RESOLVING at v1.4 spec absorption + downstream CP plan v2.11 + runtime un-strike); self-audit (no Pattern P1 cross-artifact name drift: §25 cites §5.1 8-class taxonomy + §6.1 manifest schema + §6.2 per-step override + §7.1 engine-class enum + §8.1 resumption-kind + §8.2 idempotency-key join + §10.1 topology taxonomy verbatim with section anchors; new `RunStatus` 4-value enum is contract-introduced and non-colliding; `TopologyPatternNotYetMaterializedError` + `EngineClassNotYetMaterializedError` are contract-introduced typed-error names per §25.7; no Pattern P2 verbatim-claim-contradicted — every "per §N" + "per ADR-X" + "per `Spec_X_v_Y.md` §Z" citation is substrate-verified at this revision).

**v1.5 amendment-site verification (extension per Workflow v1.7 §7 fidelity-grammar discipline applied in-CLI per `CLAUDE.md` §4.3 design-substrate revision discipline).** The four `spec-writer` SKILL.md fidelity disciplines verify at the v1.5 §25.9 amendment site: inputs read (`.harness/fork_u_rt_49_cost_attribution_invocation_underspec.md` Q1–Q4 operator-ratified 2026-05-20 + `Spec_Operational_Discipline_v1_3.md` C-OD-14 §14.1 per-span cost formula + §14.2 sandbox-tier overhead addition + §14.4 idempotency-key join contract — verified byte-exact against OD spec v1.3 source text: §14.4 specifies *the cost record carries the parent's `idempotency_key` per C-IS-05*, NOT audit-ledger emission; OD plan v2.8 §3.5.3 D-5 12-field `SpanCostRecord` carrier; `Phase_7_Meta_Architecture_v1.md` X-AL-2 retirement criterion); ingestion contract (Phase-7 architectural-tension-resolution substrate; operator ratification authorization per workspace `CLAUDE.md` §4.3); tensions surfaced (Class 1 sub-fork at the cost-attribution invocation gap — RESOLVING at v1.5 spec absorption + downstream CP plan v2.13 + runtime smoke test extension; parent `class_1_tension_u_rt_44_workflow_loop_drain.md` CLOSED-PARTIAL → fully CLOSED at arc completion; new bounded residual `fork_cost_record_audit_ledger_wiring_residual` filed for the downstream audit-ledger writer wiring NOT specified at §25.9 — §25.9 specifies carrier production only, not the audit-ledger emission seam); self-audit (no Pattern P1 cross-artifact name drift: §25.9 cites §5.1 closed-at-8 taxonomy + §25.5 propagated-pattern row vocabulary + C-OD-14 §14.1/§14.2/§14.4 + 12-field `SpanCostRecord` per OD plan v2.8 §3.5.3 + §25.6 skip semantics + §25.7 fail-class taxonomy + §25.1 SINGLE_THREADED_LINEAR scope verbatim with section anchors; no new enum / no new type / no new fail class / no new event class introduced at v1.5; v1.4 spec-writer audit caught Pattern P2 candidate at v1.5 draft — initial §25.9 wording cited §14.4 as "emission target," verification against OD spec v1.3 §14.4 surfaced this was the JOIN contract not the EMISSION contract; §25.9 re-worded to describe carrier production only and filed `fork_cost_record_audit_ledger_wiring_residual` for the un-specified downstream emission wiring; no Pattern P2 verbatim-claim-contradicted at filed v1.5 — every "per §N" + "per C-OD-NN §M" + "per X-AL-N" citation is substrate-verified at this revision).

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_5.md` |
| Filing destination | `design-substrate/Spec_Control_Plane_v1_5.md` |
| Status | Proposed (pending CP plan v2.13 absorption + runtime smoke test extension un-striking U-RT-49 cost-attribution AC + full closure of parent `class_1_tension_u_rt_44_workflow_loop_drain.md`) |
| Predecessor | `Spec_Control_Plane_v1_4.md` (v1.0 → v1.1 → v1.2 → v1.3 → v1.4 → v1.5 baseline) |
| Substrate consumed | All v1.4 substrate (preserved) + `.harness/fork_u_rt_49_cost_attribution_invocation_underspec.md` (Q1–Q4 operator-ratified 2026-05-20) + `Spec_Operational_Discipline_v1_4.md` C-OD-14 5-step composition (§14.1 + §14.2 + §14.4 + §14.5) + `Phase_7_Meta_Architecture_v1.md` X-AL-2 retirement criterion |
| Successor | `Implementation_Plan_Control_Plane_v2_13.md` (Phase-7 CP plan revision-pass absorbing §25.9 cost-attribution emission composition; single-section absorption — convention-level, no new atomic unit required) |
| Phase-7 fork-resolution status | `.harness/fork_u_rt_49_cost_attribution_invocation_underspec.md` — spec-side ABSORBED at v1.5; plan-side PENDING at CP plan v2.13; runtime un-strike PENDING at smoke test extension; full closure of parent `.harness/class_1_tension_u_rt_44_workflow_loop_drain.md` (CLOSED-PARTIAL since Lane 6) PENDING at the same arc completion |
| Workflow discipline | `Project_Workflow_v1_8.md` §7 fidelity-grammar + `CLAUDE.md` invariant I-1 (citations resolve byte-exact) |
| Date | 2026-05-20 |

*Filed at Phase-7 architectural-tension-resolution revision pass close per `spec-writer` skill spec-revision-pass sub-mode. §25.9 Cost-attribution emission composition added as new subsection scoped to `SINGLE_THREADED_LINEAR` topology (v1.4 §25.1 scope preserved verbatim) per operator ratification 2026-05-20 of `.harness/fork_u_rt_49_cost_attribution_invocation_underspec.md` Q1e (step-body-owned propagated) + Q2-bounded (no shared carrier) + Q3c (mock-route bypass) + Q4 (resolve next session) recommendations. §[traceability] matrix C-CP-25 row extended with C-OD-14 5-step substrate-consumed entry. §[coherence pass] extended with v1.5 amendment-site verification line. Filing footer updated to v1.5. Adjacent-defect findings surfaced in Change-note "Adjacent-defect findings surfaced (not patched at v1.5)" section: cross-topology cost-attribution boundary (open architectural question, deferred to 7c) + `PRICE_TABLE_REF` bounded substitution (X-AL-2 residual, tracked at separate fork). Cascade segment boundary per Phase-7 sub-phase 7b execution discipline. Recommended next step: CP plan v2.12 → v2.13 revision-pass (`implementation-planner` skill) consuming §25.9 as substrate for convention-level absorption; downstream: extend `harness-runtime/tests/integration/test_run_smoke.py` step body to materialize §25.9 convention; un-strike U-RT-49 cost-attribution AC; close `fork_u_rt_49_cost_attribution_invocation_underspec.md`; fully close parent `class_1_tension_u_rt_44_workflow_loop_drain.md`.*
