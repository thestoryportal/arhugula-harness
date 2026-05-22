# Cross-Axis Composition Document (v2.8)

*Delta over v2.7. v2.8 is a citation-bookkeeping patch absorbing the path-γ rename of the C-CP-26 §26.2 `PauseReason` Python identifier to `WorkflowPauseReason` (operator-ratified 2026-05-21 per `.harness/class_1_fork_u_cp_63_pause_reason_collision.md`). Spec-version citation bumps at §2.3.7 row 6 (C-CP-26 §26 producer) — CP spec v1.10 → v1.11 + OD spec v1.8 → v1.9. No edge cardinality change; no classification change; no bucket count change. The v2.7 §0.11 promotion-candidate notes preserved verbatim. The v2.6 aggregate (99 cross-axis relationships; 29 genuine-typed-seam; 46 convention-level; 24 phase-2-runtime) preserved verbatim. All other v2.7 + v2.6 substantive content preserved verbatim by reference.*

## §0 Change note (v2.7 → v2.8)

### §0.1 Revision context — path γ citation reconciliation

Per `.harness/class_1_fork_u_cp_63_pause_reason_collision.md` (operator-ratified path γ, 2026-05-21): the NEW C-CP-26 §26.2 Python identifier `PauseReason` (5-class workflow-layer pause taxonomy) was renamed at the spec layer to `WorkflowPauseReason` to disambiguate from the OLD C-CP-22 §22.1 `PauseReason` (4-class engine-layer replay-pause taxonomy; landed at U-CP-49; preserved verbatim at CP spec v1.10/v1.11). The CXA v2.6 §2.3.7 row 6 NEW CP→OD edge entry (C-CP-26 producer) cites the CP spec by section number, not by Python identifier — but the spec-version cite (`CP spec v1.10 §26`) must bump to `CP spec v1.11 §26` byte-exact. Similarly, the OD spec citation (`OD spec v1.8 §C-OD-30`) bumps to `OD spec v1.9 §C-OD-30`. The audit-payload field name `pause_reason` (lowercase snake_case at the AuditPayload row prose) is independent of the Python enum class identifier — preserved verbatim. The OTel attribute name `pause.reason` (lowercase dot-notation at §26.4 + §C-OD-30.1) is independent of the Python enum class identifier — preserved verbatim.

### §0.2 Sections revised

§0 (this change note); §2.3.7 row 6 (C-CP-26 §26 producer) spec-version citation bumps at CP-spec-version + OD-spec-version cells. All other sections preserved verbatim from v2.7.

### §0.3 §2.3.7 row 6 amendment (CP→OD bucket, C-CP-26 producer)

The v2.6 §2.3.7 row 6 (preserved verbatim through v2.7) is amended at v2.8 with spec-version cite bumps only. Edge classification (G — genuine-typed-seam), shared-converter discipline (`pause:` + `resume:` action_id prefix discriminators sharing the converter row), and audit-row-shape enumeration preserved verbatim:

> **C-CP-26 §26 (PauseResumeProtocol)** | **U-OD-00** | **CP spec v1.11 §26.4 (pause.captured + resume.attempted spans) + OD spec v1.9 §C-OD-30 (`pause.*` + `resume.*` 8-attribute namespace + PauseResumeAuditPayload)** *(v2.8 amendment — was CP spec v1.10 + OD spec v1.8 at v2.6/v2.7)* | **G — `AuditLedgerEntry` as converter output type at pause/resume audit-write; share converter via `pause:` and `resume:` action_id prefix discriminators (two action_id patterns share the bucket row — one converter, two distinct audit-trail patterns at OD-side); 1-row audit shape includes `pause_reason` + `snapshot_hash` + `step_index` + `state_ledger_anchor` (pause path) OR `diff_detected` + `diff_summary_hash` + `diff_policy` + `outcome` (resume path). (NEW v2.6; spec-version cites bumped at v2.8)**

The audit-row-shape prose retains lowercase field name `pause_reason` (matching the AuditPayload field declaration at OD spec §C-OD-30.2 — `pause_reason: str | None`); this is independent of the Python enum class identifier `WorkflowPauseReason` (v1.11 rename).

### §0.4 Cost-attribution audit-write seam row 8 — STILL OWED at future v2.x

**Critical preservation note (advisor-flagged).** The §2.3.7 row 8 cost-attribution audit-write seam amendment owed per `.harness/Remaining_Work_Closure_Arc_Handoff_v1.md` §6 + workspace `CLAUDE.md` §2.4 v2.x amendment note (paired with U-CP-72 implementation) is **NOT** part of this v2.8. v2.8 publishes ONLY for path γ enum citation absorption — narrow scope, single-row spec-version cite bump at row 6. The cost-attribution row 8 (paired with U-CP-72) remains owed at a future v2.9 (or later) when paired with U-CP-72 implementation per workspace CLAUDE.md §2.4 published-pairing constraint.

This v2.8 advances the CXA version counter by one. The cost-attribution amendment becomes v2.9 (or higher if intervening amendments) instead of v2.8 — flag for downstream traceability so the cost-attribution owe is NOT confused as already-closed by v2.8 publication.

### §0.5 Status posture

Proposed (v2.7) → **Proposed (v2.8)**. v2.8 is a citation-bookkeeping patch — single-row spec-version cite bump at §2.3.7 row 6. No new edge, no classification change, no acceptance criterion change, no aggregate count change.

### §0.6 Downstream absorption owed (post-v2.8)

(a) Workspace `CLAUDE.md` §2.4 CXA row version bump (v2.7 → v2.8).
(b) Co-published artifacts at the path-γ rename arc:
- `Spec_Control_Plane_v1_11.md` (§26.2 enum identifier rename + §26 NEW NOTE coexistence)
- `Spec_Operational_Discipline_v1_9.md` (§C-OD-30.1 attribute-type cite absorbed)
- `Implementation_Plan_Control_Plane_v2_17.md` (U-CP-62 carrier rename + U-CP-63/64 AC #4 strike + Files-column note amendment)
- `Implementation_Plan_Operational_Discipline_v2_15.md` (U-OD-51 spec-version cite bumps)
(c) v2.9 (or later) — cost-attribution audit-write seam row 8 (paired with U-CP-72 implementation; OWED per workspace CLAUDE.md §2.4).

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Cross_Axis_Composition_Document_v2_8.md` |
| Version | v2.8 |
| Filing event | Path γ citation reconciliation — §2.3.7 row 6 spec-version cite bumps, 2026-05-21 |
| Predecessor | `Cross_Axis_Composition_Document_v2_7.md` (preserved verbatim outside §2.3.7 row 6 spec-version cite cells) |
| Successor | (none — current canonical) |
| Aggregate count | Preserved (99 / 29 / 46 / 24) |
| Cost-attribution row 8 status | **STILL OWED** at future v2.x (paired with U-CP-72 implementation per workspace CLAUDE.md §2.4) — v2.8 publishes ONLY for path γ enum citation, NOT for cost-attribution |
| Operator authority | `.harness/class_1_fork_u_cp_63_pause_reason_collision.md` path γ ratification 2026-05-21 |
| Date | 2026-05-21 |
