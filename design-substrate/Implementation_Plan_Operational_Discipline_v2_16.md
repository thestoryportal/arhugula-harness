# Implementation Plan — Operational Discipline v2.16

## Change-note (v2.15 → v2.16)

**Scope of revision.** Cross-axis-block lift at U-OD-51 — the v2.15 §0 status-block (c) clause declared U-OD-51 "cross-axis-blocked on U-CP-62" at filing date 2026-05-21. U-CP-62 (`WorkflowPauseReason` + `MaterialDiffPolicy` + `PauseSnapshot` + `ResumeResult` carriers) subsequently landed at commit `49617e7` (cluster 10-CP-B impl arc commit 1/4, 2026-05-22) per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` §2.1 routing target (a). The cross-axis prerequisite is now satisfied; U-OD-51 transitions from cross-axis-blocked to implementation-ready at HEAD `514ff0d`. v2.16 absorbs this status-block update as a single-clause amendment under FM-2 no-extension discipline.

**v2.15 substantive content preserved verbatim.** All v2.15 content (U-OD-00 through U-OD-54; clusters 1 through 4-OD-E; DAG topology; coverage matrix; cross-axis edge enumeration; U-OD-51 plan-body declaration including 5 ACs, Implements line, Files line, Signatures line, Depends-on line, Rollback boundary line) preserved unchanged at v2.16. The U-OD-51 Depends-on cite `[U-CP-62 (cross-axis: CP)]` is preserved verbatim — the DAG dependency itself remains canonical; what lifts is the "blocked" status-claim at the §0 status-block, not the plan-body dependency relation. The v2.14 + v2.13 + ... + v2 chain all preserved.

**Source of fix.** Sub-arc A of the 3-arc cascade per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` §6 + batch-11 §9(e) + batch-12 §7(c). U-CP-62 landing at `49617e7` is the structural unblock event; this plan v2.16 absorbs the unblock at the consumer-side plan layer. Sub-arc B (CostRecordAuditPayload authoring at OD spec v1.10 + CXA v2.9 amendment + U-OD-41 revision) carried as separately-authored follow-on arc per operator-discretion sequencing (operator preference (i) revise-U-OD-41-signature noted at session checkpoint for Sub-arc B pickup).

**Single amendment site.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **§0 status-block (c) clause** | "Phase 7b cluster-open authorization for 4-OD-E continuation (U-OD-53 + U-OD-54 — independent; **U-OD-51 cross-axis-blocked on U-CP-62**)" → "Phase 7b cluster-open authorization for 4-OD-E continuation (U-OD-53 + U-OD-54 — independent; **U-OD-51 cross-axis-prerequisite met at U-CP-62 landing `49617e7` 2026-05-22 — implementation-ready**)". Single-clause delta; no carrier change. | `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` §2.1 + commit `49617e7` |

**Plan shape preserved.** v2.15's 55-unit axis-led structure preserved verbatim. No new units; no DAG topology change; no cluster boundary change; no coverage matrix change; no AC count change at U-OD-51 (5 → 5 ACs); no cross-axis dependency change at the plan-body Depends-on cite (preserved verbatim — DAG dependency canonical; status-claim lift is orthogonal); no AC text change at U-OD-51; no plan-body content change at U-OD-51.

**Status posture.** Proposed (v2.15) → **Proposed (v2.16)**. v2.16 is a status-block bookkeeping patch — single-clause `cross-axis-blocked` → `implementation-ready` update at §0 status-block (c) clause. No spec change, no plan body change, no DAG change, no AC change.

**Downstream absorption owed (post-v2.16).**
(a) Workspace `CLAUDE.md` §2.4 OD plan row version bump (v2.15 → v2.16). Light-touch pointer update; operator-discretion timing.
(b) `harness-od/CLAUDE.md` pointer rows preserved verbatim (the cross-axis-block lift does not affect OD-side substitution state; H_T-OD-* retirement table at the post-batch-12 axis-CLAUDE.md refresh already documented H_T-CP-22 PARTIAL with U-CP-62 landing acknowledged at the cross-axis cite chain footnote).
(c) Phase 7b cluster-open authorization for U-OD-51 implementation arc (cluster 4-OD-B continuation per `phase-7-implementation` skill discipline). U-OD-51 now ready-to-implement at next phase-7-implementation skill activation; carrier of `PauseResumeAuditPayload` extending `AuditPayload` with 8 pause/resume-specific fields per OD spec v1.9 §C-OD-30.2 + Pattern-P1 byte-exact alignment with CP spec v1.11 §26.4 (U-CP-65 producer-side).
(d) Sub-arc B sequel (separately-authored): CostRecordAuditPayload at OD spec v1.9 → v1.10 NEW §C-OD-NN + CXA v2.8 → v2.9 amendment row 8 + OD plan revision at U-OD-41 (operator preference (i) revise-signature noted at session checkpoint; not authored at this arc per operator-discretion scope split).

**Adjacent defects surfaced (not patched per FM-2 no-extension discipline).** None — apply pass is fidelity-pure status-block update absorbing an upstream-cross-axis-landing event. The plan-body content + ACs + signatures + DAG all preserve verbatim from v2.15.

---

## §1 — §0 status-block (c) clause amendment (v2.16)

The v2.15 §0 status-block "Downstream absorption owed" enumeration (c) clause is amended at v2.16 as follows.

### v2.15 → v2.16 single-clause delta

| Version | (c) clause text |
|---|---|
| **v2.15** (line 24) | "(c) Phase 7b cluster-open authorization for 4-OD-E continuation (U-OD-53 + U-OD-54 — independent; U-OD-51 cross-axis-blocked on U-CP-62) per `phase-7-implementation` skill discipline." |
| **v2.16** | "(c) Phase 7b cluster-open authorization for 4-OD-E continuation (U-OD-53 + U-OD-54 — independent; **U-OD-51 cross-axis-prerequisite met at U-CP-62 landing `49617e7` 2026-05-22 — implementation-ready**) per `phase-7-implementation` skill discipline." |

**Amendment delta scope.** Single-clause status-claim update at §0 status-block. The 4-OD-E independence of U-OD-53 + U-OD-54 (which already landed at commits `0aed0ac` + `128ab4f` 2026-05-22 — surfaced at the post-batch-12 harness-od/CLAUDE.md refresh) is preserved verbatim. The forward-going implementation-readiness state of U-OD-51 is the substantive change.

**Note on v2.15 §0 (c) clause being descriptively stale.** As of HEAD `514ff0d`, U-OD-53 + U-OD-54 themselves have landed (per harness-od/CLAUDE.md post-batch-12 refresh + batch-11 §9 observations). The v2.15 §0 (c) clause "Phase 7b cluster-open authorization for 4-OD-E continuation" describes a state at v2.15 filing time (2026-05-21) which has subsequently advanced. Per FM-2 forward-only ledger discipline, this descriptive staleness is preserved as v2.15 historical state; v2.16 amends only the U-OD-51 blocked-claim component (which is the substantive amendment per Sub-arc A scope). The 4-OD-E sub-clause continues to describe the v2.15 state at filing time and is preserved verbatim within the broader rewritten clause.

---

## §2 — U-OD-51 plan-body preservation (v2.16)

The U-OD-51 declaration last canonically authored at `Implementation_Plan_Operational_Discipline_v2_15.md` §1 (lines 30–49) is preserved verbatim at v2.16. No plan-body content change, no AC change, no signature change, no Depends-on change, no Implements cite change.

The Depends-on cite `[U-CP-62 (cross-axis: CP)]` preserved verbatim per FM-2 — the DAG dependency relation is canonical and persists regardless of U-CP-62's landed-vs-bounded state. The cross-axis-block status-claim at §0 (c) is a meta-pointer descriptor for orchestration-time clustering decisions, not a plan-body DAG fact. The two surfaces are operationally distinct under workspace `CLAUDE.md` §4.3 forward-only ledger discipline: plan-body Depends-on = canonical DAG relation; §0 status-block = orchestration-state-snapshot at filing time.

---

## §3 — DAG topology + coverage matrix + cross-axis edges preservation

DAG topology preserved verbatim from v2.15. Coverage matrix preserved verbatim: §C-OD-30.1 + §C-OD-30.2 → U-OD-51.

Cross-axis edges enumeration preserved verbatim: U-OD-51 → U-CP-62 (cross-axis).

---

## §4 — Sub-arc B carry-forward (NOT amended at this arc)

Per operator scope-split decision 2026-05-23 (AskUserQuestion: "Sub-arc scope" — chosen A only), Sub-arc B of the 3-arc cascade per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` §6 is **NOT** authored at this v2.16. Sub-arc B's owed artifacts:

| Artifact | Status post-v2.16 |
|---|---|
| OD spec v1.9 → v1.10 NEW §C-OD-NN `CostRecordAuditPayload` declaration | OWED at future spec-writer skill arc; CostRecordAuditPayload subclass NOT YET contracted at OD spec |
| CXA v2.8 → v2.9 §2.3.7 row 8 cost-attribution audit-write seam | OWED per CXA v2.8 §0.4 + workspace `CLAUDE.md` §2.4 published-pairing constraint (paired with U-CP-72 implementation, which has partially landed 6/8 prefix branches) |
| OD plan v2.16 → v2.17 U-OD-41 signature revision | OWED per fork doc §6 "reviewer to confirm bucket sizing or extend U-CP-72" + operator preference (i) revise-U-OD-41-signature noted at session checkpoint 2026-05-23 |
| OD plan v2.16 → v2.17 status-block authorization clause | OWED — sub-arc-B-completion event marker |

**Operator preference (i) noted at AskUserQuestion 2026-05-23.** When Sub-arc B opens, U-OD-41 should be revised in-place (signature returns `CostRecordAuditPayload` instead of `CPAuditLedgerEntry`); no new dedicated AuditPayload-author unit. The producer/AuditPayload-wrapping roles consolidate at U-OD-41 per (i). Plan-revision arc at Sub-arc B opening should reflect this preference at AC #3 rewrite (the "reviewer to confirm bucket sizing or extend U-CP-72" clause un-strikes to a concrete signature-revision specification).

**Status:** Sub-arc B fully scoped + operator-decided; sequencing routed to follow-on session per scope-split discipline.

---

## §5 — Cross-axis cite chain U-OD-51 ↔ U-CP-62 ↔ U-CP-72 status (post-v2.16)

Per batch-12 §7(c) coupled-front observation + `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` §2.1:

| Link | Status post-v2.16 |
|---|---|
| U-CP-62 (`WorkflowPauseReason` + carriers) | LANDED at `49617e7` (cluster 10-CP-B commit 1/4, 2026-05-22) |
| U-OD-51 cross-axis-prerequisite | **MET at this v2.16 absorption (was: blocked at v2.15 §0 (c))** |
| U-OD-51 implementation-readiness | **READY** — eligible for `phase-7-implementation` skill activation at next arc |
| U-CP-72 `pause:` / `resume:` branch un-STRIKE | OWED at U-OD-51 implementation + landing arc (separate from this plan-revision arc) |
| H_T-CP-22 PARTIAL → RETIRE-READY transition | Gated on U-OD-51 implementation arc + workflow_driver pause-event handler invocation of PauseResumeProtocol (per batch-11 §5 H_T-CP-22 PARTIAL → RETIRE-READY gate) |

**3-arc cascade progress:** Sub-arc A (this v2.16) **COMPLETE** at the cross-axis-block lift level (plan layer). Sub-arc A landing event = U-OD-51 implementation + `pause:` / `resume:` branch un-STRIKE at U-CP-72. Sub-arc B (cost-attribution) unchanged — separately-authored future arc per §4.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Operational_Discipline_v2_16.md` |
| Version | v2.16 |
| Filing event | Sub-arc A cross-axis-block lift at U-OD-51 (§0 status-block (c) clause amendment absorbing U-CP-62 landing at `49617e7` 2026-05-22), 2026-05-23 |
| Predecessor | `Implementation_Plan_Operational_Discipline_v2_15.md` (v2.15 substantive content preserved verbatim outside §0 (c) clause single-clause status-block update) |
| Co-published artifacts | None — v2.16 is a standalone consumer-side plan-revision absorbing an upstream cross-axis landing event (U-CP-62 at `49617e7` already published) |
| Operator authority | `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` §2.1 routing target (a); operator scope-split ratification at AskUserQuestion 2026-05-23 ("Sub-arc scope" = A only) |
| Unit-count change | None (55 → 55; no new units) |
| Cluster-count change | None |
| AC-count change | None (U-OD-51 stays at 5 ACs; no AC text change) |
| Plan-body change | None at U-OD-51 plan body; single-clause amendment at §0 status-block (c) clause |
| Skill discipline | `phase-7-back-flow-routing` Class 1 fork detection (Sub-arc A partial resolution at consumer-side plan layer); implementation-planner skill revision-pass mode scope (light-touch status-block amendment under FM-2 no-extension discipline) |
| Date | 2026-05-23 |
| Class 1 fork status post-v2.16 | `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` — PARTIAL-RESOLVED → **partially-advanced-Sub-arc-A** (cross-axis-block lift at plan layer; Sub-arc A landing event pending U-OD-51 implementation; Sub-arc B unchanged) |

---

*End of OD plan v2.16. Sub-arc A cross-axis-block lift at U-OD-51 per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` §2.1 routing target (a). Single-clause status-block amendment under FM-2 no-extension discipline. v2.15 substantive content preserved verbatim outside the §0 (c) clause amendment. Sub-arc B carried forward as separately-authored follow-on arc per operator scope-split.*
