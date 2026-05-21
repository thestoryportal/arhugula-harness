# Phase A.3 — Spec Drift Reconciliation Ledger

**Filed:** 2026-05-21 (Remaining-Work Closure Arc, Phase A sub-arc A.3)
**Skill:** Phase A.3 drift-reconciliation sub-arc (operator-ratified separate sub-arc per plan file)
**Scope:** 23 drift items (12 spec NOTE-deferred + 8 Class 3 informational from Phase 1 Explore Agent 2 + 2 from Phase A.1 + 1 from Phase A.2)
**Method:** Each item gets one disposition: **ABSORBED** (resolved + change-note logged) / **DEFERRED-WITH-RATIONALE** (explicit routing to future arc) / **STALE-SUPERSEDED** (already resolved upstream).

---

## §1 Disposition table

| ID | Item | Source | Disposition | Routing |
|---|---|---|---|---|
| **B.1** | Per-axis CLAUDE.md v2.1→v2.4 citation drift (CP+OD edge counts) | `.harness/class_3_tension_per_axis_claude_md_v2_1_to_v2_4_count_drift.md` | **DEFERRED-WITH-RATIONALE** | Next CP plan revision pass touching edge counts (already partially absorbed at CP back-edge arc per memory `class_3_tension_cxa_v2_4_axis_back_edge`) |
| **B.2** | Meta-Architecture HITL palette-value drift | `.harness/class_3_tension_meta_architecture_hitl_palette_drift.md` | **DEFERRED-WITH-RATIONALE** | Phase 7 meta-architecture revision pass (informational; no contract impact) |
| **B.3** | CXA v2.4 axis back-edge (first cross-axis back-edge) | `.harness/class_3_tension_cxa_v2_4_axis_back_edge.md` | **STALE-SUPERSEDED** | Already RESOLVED 2026-05-20 per memory + record footer; no action |
| **B.4** | U-RT-59 spec-prose-plan-body drift (8 items) | `.harness/class_3_tension_u_rt_59_spec_prose_drift.md` | **DEFERRED-WITH-RATIONALE** | Next runtime spec revision touching U-RT-59 specification section; non-blocking (plan body unambiguous) |
| **B.5** | Q6 systemic-pattern scope-widening: contract-shape composability | `.harness/class_3_tension_q6_scope_widening_contract_shape_composability.md` | **DEFERRED-WITH-RATIONALE** | Q6 follow-on arc (operator-scheduled); 3-skill extension scope-widening pass at `.claude/skills/{harness-adversarial-reviewer,phase-7-implementation,spec-writer}/SKILL.md` |
| **B.6** | OD→IS edge count drift (bounded; C3-15 self-flagged) | OD-side drift acknowledged at CP/OD CLAUDE.md self-flag | **DEFERRED-WITH-RATIONALE** | OD plan revision pass; bounded by existing C3-15 self-flag |
| **B.7** | Spec §4 HarnessContext field-table drift | `.harness/class_1_tension_u_rt_60_wrap_asymmetry_sync_async_mismatch.md` §9.4 | **DEFERRED-WITH-RATIONALE** | Next runtime spec revision touching HarnessContext schema; implementation-side complete (test asserts) |
| **B.8** | MCPBackedAskUserQuestionSurface broad-reading carry-forward | `.harness/class_1_tension_u_rt_60_wrap_asymmetry_sync_async_mismatch.md` §9.4 + §9.5 | **DEFERRED-WITH-RATIONALE** | FastMCP transport-level handler arc (Phase 7d or later); bounded by production-handler scope. **NOTE:** A.2 expanded scope to STDIO + HTTP + SSE per Decision 1.D4 — runtime spec v1.13 §14.9 now covers HTTP/SSE; the broad-reading carry-forward narrows to the *transport-level handler registration* nuance, not the transport itself |
| **D.1** | Pattern-D structured types (9 deferred) | Spec_Control_Plane v1.3 (NOTE deferred) | **STALE-SUPERSEDED** | RESOLVED at A.1 (CP plan v2.9 T2 X-AL-3 FACTOR-OUT, 16 types + v2.10 R-2/W-2, 2 types); 15 types total inherited by CP spec v1.10 per A.2 §1 |
| **D.2** | Spec §14.8 AskUserQuestionSurface construction timing | Runtime spec v1.10+ §14.8.3 | **STALE-SUPERSEDED** | CLOSED at U-RT-60 landing (HOW pinned at v1.10 §14.8.3; implementation binding landed) |
| **D.3** | Retry-of-HITL-gate per-attempt re-evaluation | Runtime spec v1.9 §14.8.7 NOTE 6-iii + v1.11 reaffirmation | **STALE-SUPERSEDED** | CLOSED at U-RT-60 landing (literal semantics preserved via async HITL; per-attempt audit-trail wired); operator-burden mitigation deferred to ops-burden-reduction arc — that's the cross-link to A.2 §25 ValidatorFramework + §14.10 OperatorBurdenEvaluator |
| **D.4** | Multi-placement same-step semantics (§14.8.2 step 4 loop per placement) | Runtime spec v1.9 §14.8.7 NOTE 6-i | **DEFERRED-WITH-RATIONALE** | Workflow-grammar arc; v1.9/v1.10/v1.11/v1.12/v1.13 MVP single-placement-per-step only |
| **D.5** | `edited_proposal` mutation semantics (field-level vs full replacement) | Runtime spec v1.9 §14.8.7 NOTE 6-ii | **DEFERRED-WITH-RATIONALE** | Workflow-mutation-discipline arc; replacement semantics implemented at MVP |
| **D.6** | Timestamp + prior_event_hash CP audit population (§14 NOTE 8a-iii) | Runtime spec v1.8 §14 NOTE 8a-iii | **DEFERRED-WITH-RATIONALE** | Multi-sibling dispatch fan-out arc; CP entry timestamp/prior_event_hash empty at MVP |
| **D.7** | `brief_hash` + `descent.child_index` persistence (§14 NOTE 8a-iv) | Runtime spec v1.8 §14 NOTE 8a-iv | **DEFERRED-WITH-RATIONALE** | Multi-sibling dispatch fan-out arc (same trigger as D.6) |
| **D.8** | TOOL_STEP dispatcher binding + tool-dispatch composer | Runtime spec v1.9 §14.7.1 line 1596 | **STALE-SUPERSEDED** | RESOLVED at A.2 — runtime spec v1.13 §14.9 C-RT-19 RuntimeToolDispatcher binds TOOL_STEP; raises `StepKindDispatcherNotBoundError` carry-forward closed |
| **D.9** | Cross-trust-boundary palette restriction (C-CP-19 §19.4) | Runtime spec v1.9 §14.8.2 step 4d + NOTE 6-iv | **DEFERRED-WITH-RATIONALE** | Validator-composer arc; v1.9-v1.13 MVP uses full palette unconditionally. **NOTE:** A.2 §25 C-CP-25 ValidatorFramework now exists; cross-trust-boundary palette restriction is the validator-composer extension owed at Phase C |
| **D.10** | HITL-as-tool-call rewriting (C-CP-17 §17.2) | Runtime spec v1.9 §14.8.2 step 4 + line 1654 PRE_ACTION note | **DEFERRED-WITH-RATIONALE** | Tool-dispatch arc — partially unblocked by A.2 (runtime spec v1.13 §14.9 lands tool-dispatch composer); explicit HITL-as-tool-call rewriting at evaluator owed at next CP arc |
| **D.11** | `response_summary_hash` content-shape (v1.11 NEW) | Runtime spec v1.11 §14.8.2 step 4g | **DEFERRED-WITH-RATIONALE** | Closed at U-RT-60 AC #13 landing per impl-discretion; spec carries open-question marker until follow-up arc formalizes the hash recipe |
| **D.12** | `requires_hitl` field absence from HITLPlacement schema | Runtime spec v1.11 §14.8.1 | **DEFERRED-WITH-RATIONALE** | Workflow-grammar arc + spec prose-drift reconciliation; implementation workaround `getattr(placement, 'requires_hitl', True)` in place at composer body |
| **D-A.1-01** | Stale tension-record header at `class_1_tension_cp_batch_blocked_units_2026_05_16.md` | Phase A.1 §4.4 surfaced | **ABSORBED** | Header amended this sub-arc (preserved original HALT framing for traceability + added RESOLVED status pointing to in-record resolution + A.1 record). The role_routing record already carried correct RESOLVED header. |
| **D-A.1-02** | Plan-file scope-wording "Pattern-D: FULL formalization for all 13 types" | Phase A.1 §4.4 surfaced | **ABSORBED** | Resolved implicitly by Phase A.2 inheritance citation; the plan file is operator-authored and not auto-amended by spec-writer. Phase E handoff artifact records the implementation as "Pattern-D inherited from CP plan v2.9 + v2.10; no re-authoring" per CP spec v1.10 change-note |
| **D-A.2-01** | Worktree baseRef drift (worktree branched from origin/main, missing 11 commits in local main including spec v1.12) | Phase A.2 sidebar finding | **ABSORBED** | Rebased worktree onto local `main` before applying A.2 edits (clean, no conflicts). Future arc: surface to operator that `EnterWorktree` `baseRef: "fresh"` default uses `origin/<default-branch>` not local `<default-branch>` — operator may prefer setting `worktree.baseRef: "head"` in `.claude/settings.json` to match local-main when origin is behind local. Non-blocking operational drift |

---

## §2 Summary by disposition

| Disposition | Count | IDs |
|---|---|---|
| **ABSORBED** | 3 | D-A.1-01, D-A.1-02, D-A.2-01 |
| **STALE-SUPERSEDED** | 4 | B.3, D.1, D.2, D.3, D.8 (5 actually — let me recount) |
| **STALE-SUPERSEDED (recount)** | 5 | B.3, D.1, D.2, D.3, D.8 |
| **DEFERRED-WITH-RATIONALE** | 15 | B.1, B.2, B.4, B.5, B.6, B.7, B.8, D.4, D.5, D.6, D.7, D.9, D.10, D.11, D.12 |
| **TOTAL** | 23 | ✓ |

---

## §3 Cross-link summary — A.2 contracts touching deferred items

The A.2 apply pass landed 5 new contracts that intersect 4 of the 15 deferred items (DEFERRED-WITH-RATIONALE items where A.2 partially unblocks them):

| Deferred item | A.2 contract that touches it | Residual scope |
|---|---|---|
| D.3 (retry-of-HITL operator-burden mitigation) | CP spec v1.10 §25 ValidatorFramework + runtime spec v1.13 §14.10 OperatorBurdenEvaluator | Cross-step burden aggregation surface NOW EXISTS; operator-burden-cache-for-retry-attempts optimization (cited at U-RT-60 NOTE) still deferred |
| D.9 (cross-trust-boundary palette restriction) | CP spec v1.10 §25 ValidatorFramework (escalation arc) | Palette-restriction logic owed at validator-composer extension; the framework surface now exists for it |
| D.10 (HITL-as-tool-call rewriting at PRE_ACTION) | Runtime spec v1.13 §14.9 RuntimeToolDispatcher (tool-dispatch composer) | Tool-dispatch composer now exists; explicit HITL-as-tool-call rewriting at evaluator owed at next CP arc |
| B.8 (FastMCP transport-level handler — narrowed) | Runtime spec v1.13 §14.9 (STDIO + HTTP + SSE all in scope) | Transport-level handler registration nuance narrowed; remaining scope = production handler binding details |

These are NOT closures — they are scope-narrowings noting that A.2 surfaced the composer infrastructure those deferred items will land against.

---

## §4 Files edited this sub-arc

1. `.harness/class_1_tension_cp_batch_blocked_units_2026_05_16.md` — header amended (D-A.1-01 absorption): RESOLVED status added; original HALT line preserved for traceability under explicit historical marker.

NO other spec or plan files edited. The 15 DEFERRED-WITH-RATIONALE items remain at their canonical sites with their existing NOTE markers; Phase A.3's disposition is the explicit routing record, not a re-edit of those NOTE markers themselves.

---

## §5 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/Spec_Drift_Reconciliation_v1.md` |
| Sub-arc | Phase A.3, Remaining-Work Closure Arc, 2026-05-21 |
| Items processed | 23 (12 NOTE-deferred + 8 Class 3 + 2 Phase A.1 + 1 Phase A.2) |
| Dispositions | 3 ABSORBED + 5 STALE-SUPERSEDED + 15 DEFERRED-WITH-RATIONALE |
| Files edited | 1 (`.harness/class_1_tension_cp_batch_blocked_units_2026_05_16.md` header) |
| Spec/plan files touched | 0 — A.3 is reconciliation accounting, not spec amendment |
| Next sub-arc | Phase A.4 (CXA v2.5 → v2.6 — new edges for A.2 composer landings) |
| Class 1 readiness | None of the 23 items rise to Class 1; no halt-execution surface |
| Phase B readiness | All A-phase deferrals explicitly routed; spec adversarial review can begin after A.4 + A.5 |
