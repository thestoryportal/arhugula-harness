# Specification — Operational Discipline v1.9

## Change-note (v1.8 → v1.9)

**Scope of revision.** Path γ enum citation absorption per `.harness/class_1_fork_u_cp_63_pause_reason_collision.md` (operator-ratified 2026-05-21) co-published with CP spec v1.11. The v1.8 §C-OD-30.1 `pause.reason` attribute type cites the CP spec v1.10 §26.2 Python enum identifier `PauseReason`; at CP spec v1.11 that identifier was renamed to `WorkflowPauseReason` (workflow-layer vs engine-layer disambiguation). v1.9 absorbs the citation rename. ZERO change to attribute name, attribute cardinality, attribute count (8), audit-payload field set, or sampling discipline.

**v1.8 substantive content preserved verbatim.** All v1.8 content outside the §C-OD-30.1 attribute-type-citation absorption preserved unchanged. The v1.8 NEW C-OD-25 through C-OD-33 contracts preserved verbatim outside the single citation update at §C-OD-30.1. The v1.7 + v1.6 + ... + v1 chain all preserved.

**Source of fix.** Co-published artifact at the path γ rename arc per workspace `CLAUDE.md` §4.3 silent-absorption discipline — when a cited identifier renames at the producer spec (CP spec v1.10 → v1.11), the consumer spec citation MUST absorb the rename byte-exact. Per `Project_Workflow_v1_8.md` §7.4.2 byte-exact citation discipline.

**Single amendment site.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **§C-OD-30.1 `pause.reason` attribute type citation** | The attribute type cell value "enum (`PauseReason` per CP spec v1.10 §26.2)" updates to "enum (`WorkflowPauseReason` per CP spec v1.11 §26.2)". Attribute name (`pause.reason`, lowercase dot-notation), span site (`pause.captured`), cardinality (1) preserved verbatim. | Path γ co-published artifact 2026-05-21 |

**Audit-payload preservation.** The §C-OD-30.2 `PauseResumeAuditPayload.pause_reason` field declared as `str | None` (enum value serialized as string at the audit-ledger row) — type annotation is `str | None`, not the enum class itself, so no rename absorption needed at the payload declaration. Comment-line cite is preserved as canonical-by-prose ("PauseReason enum value (pause path)") — v1.9 preserves the comment verbatim since the enum-value semantics (5 string values) are unchanged.

**Status posture.** Proposed (v1.8) → **Proposed (v1.9)**. v1.9 is a citation-bookkeeping patch — single attribute-type cell update at §C-OD-30.1 + co-published spec-version pointer. No contract re-decomposition; no field set change; no sampling-discipline change.

**Downstream absorption owed (post-v1.9).**
(a) Workspace `CLAUDE.md` §2.3 OD spec row version bump (v1.8 → v1.9).
(b) `Implementation_Plan_Operational_Discipline_v2_15.md` (co-published this arc) — U-OD-51 cites renamed enum at AC #1 / AC #4 byte-exact.
(c) `Cross_Axis_Composition_Document_v2_8.md` (co-published this arc) — §2.3.7 row 6 OD-spec-version citation bump.

**Adjacent defects surfaced (not patched per FM-2 no-extension discipline).** None — apply pass is fidelity-pure citation absorption.

---

## §1 — §C-OD-30.1 attribute type citation amendment (v1.9)

The v1.8 §C-OD-30.1 canonical attribute set table row 1:

| Attribute | Type | Span site | Cardinality |
|---|---|---|---|
| `pause.reason` | enum (`PauseReason` per CP spec v1.10 §26.2) | `pause.captured` | 1 |

is amended at v1.9 to:

| Attribute | Type | Span site | Cardinality |
|---|---|---|---|
| `pause.reason` | enum (`WorkflowPauseReason` per CP spec v1.11 §26.2) | `pause.captured` | 1 |

All other §C-OD-30.1 attribute rows (rows 2–8) preserved verbatim from v1.8.

---

## §2 — Preservation guarantees

| Element | Disposition |
|---|---|
| All v1.8 contracts (C-OD-25 through C-OD-33) | Preserved verbatim outside §C-OD-30.1 single attribute-type cell |
| v1.8 §C-OD-30.2 `PauseResumeAuditPayload` declaration | Preserved verbatim (`pause_reason: str \| None` annotation references the enum's string value, not the class identifier; comment-prose `PauseReason enum value` is intentional canonical-by-prose, not a Python-identifier cite) |
| v1.8 §C-OD-30.3 sampling discipline (`pause.captured` head=1.0 + `resume.attempted` head=1.0) | Preserved verbatim |
| v1.8 §24 audit-ledger schema + C-OD-24 4-section chain + `compute_entry_hash` helper | Preserved verbatim |
| Pattern-P1 byte-exact alignment guarantee with CP spec v1.11 §26.4 | Preserved (the rename is byte-exact between producer + consumer; v1.9 absorbs the rename byte-exact) |
| All other v1.8 NEW contracts (C-OD-25, C-OD-26, C-OD-27, C-OD-28, C-OD-29, C-OD-31, C-OD-32, C-OD-33) | Preserved verbatim |

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Operational_Discipline_v1_9.md` |
| Version | v1.9 |
| Filing event | Path γ enum citation absorption — co-published with CP spec v1.11, 2026-05-21 |
| Predecessor | `Spec_Operational_Discipline_v1_8.md` (v1.8 substantive content preserved verbatim outside §C-OD-30.1 single attribute-type cell update) |
| Co-published artifacts | CP spec v1.11; CP plan v2.17; OD plan v2.15; CXA v2.8; workspace CLAUDE.md + per-axis CLAUDE.md pointer bumps |
| Operator authority | `.harness/class_1_fork_u_cp_63_pause_reason_collision.md` path γ ratification 2026-05-21 |
| Contract-count change | None (33 → 33; rows preserved) |
| Skill discipline | `phase-7-back-flow-routing` Class 1 fork detection (co-published consumer-side citation absorption) |
| Date | 2026-05-21 |
