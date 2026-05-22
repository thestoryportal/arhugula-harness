# Implementation Plan — Operational Discipline v2.15

## Change-note (v2.14 → v2.15)

**Scope of revision.** Path γ enum citation absorption per `.harness/class_1_fork_u_cp_63_pause_reason_collision.md` (operator-ratified 2026-05-21) co-published with CP spec v1.11 + OD spec v1.9 + CP plan v2.17 + CXA v2.8. The U-OD-51 plan-body cites OD spec §C-OD-30.1 + §C-OD-30.2 + CP spec §26 producer; the CP-side enum identifier `PauseReason` renamed to `WorkflowPauseReason` at CP spec v1.11 + OD spec v1.9 §C-OD-30.1 attribute-type cite. v2.15 absorbs the enum-citation rename at U-OD-51 ACs. ZERO change to attribute count (8), attribute-name strings (lowercase dot-notation `pause.reason` etc.), Pattern-P1 byte-exact alignment with producer, or AuditPayload field set.

**v2.14 substantive content preserved verbatim.** All v2.14 content (U-OD-00 through U-OD-54; clusters 1 through 4-OD-E; DAG topology; coverage matrix; cross-axis edge enumeration) preserved unchanged outside the U-OD-51 enum-citation absorption. The v2.13 + v2.12 + ... + v2 chain all preserved.

**Source of fix.** Co-published artifact at the path γ rename arc per workspace `CLAUDE.md` §4.3 silent-absorption discipline — when a producer-side identifier renames at the producer spec (CP spec v1.10 → v1.11), consumer-side plans citing the producer identifier MUST absorb the rename byte-exact at the AC level where the identifier is cited.

**Single amendment site.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **U-OD-51 — enum citation absorption** | AC #1 (schema declares 8 attributes per §C-OD-30.1) preserved verbatim — schema declaration cites section number + attribute names, not enum class identifier. AC #2 (PauseResumeAuditPayload extends AuditPayload) preserved verbatim — `pause_reason: str \| None` annotation references enum string value, not class. AC #3 (Pattern-P1 byte-exact alignment with CP spec v1.11 §26.4) — spec-version cite bump v1.10 → v1.11. AC #4 (Optional fields per path) preserved verbatim. AC #5 (Unit test: schema verbatim match) preserved verbatim. Plan-body Implements line cites OD spec §C-OD-30.1 + §C-OD-30.2 (preserved) — v1.8 → v1.9 spec-version cite bump. Plan-body Depends on cite (U-CP-62 cross-axis) preserved verbatim. | OD spec v1.9 §C-OD-30.1 + CP spec v1.11 §26.2 |

**Plan shape preserved.** v2.14's 55-unit axis-led structure preserved verbatim. No new units; no DAG topology change; no cluster boundary change; no coverage matrix change; no AC count change at U-OD-51 (5 → 5 ACs); no cross-axis dependency change (U-OD-51 → U-CP-62 cross-axis remains).

**Status posture.** Proposed (v2.14) → **Proposed (v2.15)**. v2.15 is a citation-bookkeeping patch — spec-version cite bump at U-OD-51 plan-body Implements line + AC #3 byte-exact-alignment cite line.

**Downstream absorption owed (post-v2.15).**
(a) Workspace `CLAUDE.md` §2.4 OD plan row version bump (v2.14 → v2.15).
(b) `harness-od/CLAUDE.md` pointer rows preserved verbatim (the rename does not affect OD-side substitution state).
(c) Phase 7b cluster-open authorization for 4-OD-E continuation (U-OD-53 + U-OD-54 — independent; U-OD-51 cross-axis-blocked on U-CP-62) per `phase-7-implementation` skill discipline.

**Adjacent defects surfaced (not patched per FM-2 no-extension discipline).** None — apply pass is fidelity-pure citation absorption.

---

## §1 — U-OD-51 plan-body amendment (v2.15)

The U-OD-51 declaration last canonically authored at `Implementation_Plan_Operational_Discipline_v2_14.md` §240–251 is amended at v2.15 as follows. Original v2.14 content preserved verbatim except for the spec-version cite bumps at the Implements + AC #3 lines.

### U-OD-51 — pause/resume schema + PauseResumeAuditPayload dataclass (v2.15 amendment — spec-version cite bumps absorbing CP spec v1.11 + OD spec v1.9 path γ enum citation rename; attribute count + Pattern-P1 alignment preserved verbatim)

**Amendment delta (v2.14 → v2.15).** Spec-version cite bumps absorb path γ enum rename (`PauseReason` → `WorkflowPauseReason`) at consumer-side schema. Plan body AC content preserved verbatim except for the AC #3 spec-version cite bump.

- **Implements:** OD spec v1.9 §C-OD-30.1 (8 attributes) + §C-OD-30.2 (PauseResumeAuditPayload) *(v2.15 amendment — was OD spec v1.8 at v2.14; v1.9 absorbs WorkflowPauseReason rename)*
- **Files:** `harness-od/src/harness_od/pause_resume_namespace.py` (NEW)
- **Signatures:** `PAUSE_RESUME_SPAN_NAMESPACE_SCHEMA`; `@dataclass(frozen=True) class PauseResumeAuditPayload(AuditPayload)`
- **Depends on:** [U-CP-62 (cross-axis: CP)] *(preserved verbatim; U-CP-62 is the CP-side carrier of `WorkflowPauseReason` post-v1.11)*
- **ACs (v2.15 amendment — AC #3 spec-version cite bump; ACs #1, #2, #4, #5 preserved verbatim):**
  1. Schema declares 8 attributes per §C-OD-30.1
  2. PauseResumeAuditPayload extends AuditPayload with 8 pause/resume-specific fields (pause OR resume path)
  3. Pattern-P1 byte-exact alignment with CP spec v1.11 §26.4 *(v2.15 amendment — was CP spec v1.10 at v2.14; v1.11 absorbs WorkflowPauseReason rename byte-exact)*
  4. Optional fields per path (pause_reason populated on pause path; resume_outcome on resume path)
  5. Unit test: schema verbatim match

**Rollback boundary (preserved verbatim from v2.14).** Revert the `pause_resume_namespace.py` module. U-CP-65 cross-axis Pattern-P1 alignment check loses consumer-side schema reference.

---

## §2 — DAG topology + coverage matrix preservation

DAG topology preserved verbatim from v2.14. Coverage matrix preserved verbatim: §C-OD-30.1 + §C-OD-30.2 → U-OD-51.

Cross-axis edges enumeration preserved verbatim: U-OD-51 → U-CP-62 (cross-axis).

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Operational_Discipline_v2_15.md` |
| Version | v2.15 |
| Filing event | Path γ enum citation absorption — co-published with CP spec v1.11 + OD spec v1.9, 2026-05-21 |
| Predecessor | `Implementation_Plan_Operational_Discipline_v2_14.md` (v2.14 substantive content preserved verbatim outside U-OD-51 spec-version cite bumps) |
| Co-published artifacts | CP spec v1.11; OD spec v1.9; CP plan v2.17; CXA v2.8; workspace CLAUDE.md + per-axis CLAUDE.md pointer bumps |
| Operator authority | `.harness/class_1_fork_u_cp_63_pause_reason_collision.md` path γ ratification 2026-05-21 |
| Unit-count change | None (55 → 55; no new units) |
| Cluster-count change | None |
| AC-count change | None (U-OD-51 stays at 5 ACs; only AC #3 spec-version cite updated) |
| Skill discipline | `phase-7-back-flow-routing` Class 1 fork detection (co-published consumer-side citation absorption) |
| Date | 2026-05-21 |
