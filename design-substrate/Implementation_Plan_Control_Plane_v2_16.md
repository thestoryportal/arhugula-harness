# Implementation Plan — Control Plane v2.16

## Change-note (v2.15 → v2.16)

**Scope of revision.** Path β U-CP-47 enum identifier rename absorption per `.harness/class_1_fork_u_cp_58_validator_fail_class_collision.md` (operator-ratified 2026-05-21). The OLD C-CP-21 §21.1 Python identifier `ValidatorFailClass` (defined in U-CP-47 plan body across base v2 + v2.1 + v2.4 amendment) was renamed at the landed code layer to `ValidatorRetryExitClass` to disambiguate from the NEW C-CP-25 §25.2 `ValidatorFailClass` introduced at CP spec v1.10. v2.16 documents the rename absorption at the plan layer; U-CP-47's plan-body declaration (last canonically amended at v2.4) retains its 5-member surface (TRANSIENT_RETRY / REFLEXION_RECOVERABLE / HITL_RECOVERABLE / PERMANENT_FAIL_EXIT / TERMINAL_FAIL_EXIT) verbatim — only the class identifier renames.

**v2.15 substantive content preserved verbatim.** All v2.15 content (U-CP-00, U-CP-00b, U-CP-00c, U-CP-01 – U-CP-72; all clusters; DAG topology; coverage matrix) preserved unchanged. v2.14 + v2.13 + ... + v2 chain preserved. The U-CP-58 declaration at v2.15 §1 — which cites the NEW C-CP-25 §25.2 `ValidatorFailClass` — is preserved verbatim; the NEW enum's name is unchanged by path β.

**Source of fix.** Phase 7b implementation-arc fork detection per `phase-7-back-flow-routing` skill discipline:
- Pre-implementation carrier-surface inspection at U-CP-58 entry surfaced the `ValidatorFailClass` namespace collision (NEW C-CP-25 §25.2 vs OLD C-CP-21 §21.1).
- Operator ratification of path β (rename existing C-CP-21 enum) over alternatives α / γ / δ per fork file.
- Spec-writer skill exited at scope check (CP spec v1.10 file has no rename surface — the Python identifier for C-CP-21 lives at plan + code, not spec).
- Co-published artifacts: runtime spec v1.14 (`Spec_Harness_Runtime_v1.md` §14.6 citation update); CXA v2.7 (§0.11 promotion-candidate citation update); 10 landed code files (commit `744848c`).

**U-CP-47 amendment site.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **U-CP-47 enum identifier rename** | The plan-body declaration of U-CP-47 (last canonically amended at CP plan v2.4 §4A verbatim-divergence cluster resolution; preserved through v2.5 → v2.15) renames `enum ValidatorFailClass` → `enum ValidatorRetryExitClass`. All internal back-references within U-CP-47's plan body (Signatures + acceptance criteria + Tests + Rollback boundary) update the identifier. Member values + metadata schema + namespace schema preserved verbatim. The cross-unit propagation from U-CP-47 → U-CP-48 (per CP plan v2.4 §0 cross-unit-propagation declaration: `TRANSIENT_STAIRCASE_TRANSITIONS on_cause: ValidatorFailClass`) also renames to `ValidatorRetryExitClass`. | Path β operator ratification 2026-05-21 |

**Rename propagation surface (informational — not amended at this plan, but documented for traceability).**

| Surface | Site | Disposition |
|---|---|---|
| Landed code | 10 files in `harness-cp/` + `harness-runtime/`, 80 occurrences | RENAMED at commit `744848c` |
| Spec citations | `Spec_Harness_Runtime_v1.md` v1.13 → v1.14 §14.6 | RENAMED at commit `4708d2c` |
| Cross-axis citations | `Cross_Axis_Composition_Document_v2_6.md` → v2.7 §0.11 row 1 | RENAMED at commit `4708d2c` |
| Historical plan versions | `Implementation_Plan_Control_Plane_v2.md` + `_v2_1.md` + `_v2_4.md` | PRESERVED VERBATIM (historical snapshots; per delta-versioning discipline historical versions retain the original at-time-of-authoring identifier) |
| Historical spec versions | `Spec_Control_Plane_v1_2.md` through `_v1_9.md` | PRESERVED VERBATIM (none use the Python identifier; spec prose uses `validator.fail.class` lowercase attribute name + descriptive "5-class taxonomy") |
| Historical CXA versions | `Cross_Axis_Composition_Document_v2_3.md` through `_v2_6.md` | PRESERVED VERBATIM |
| `Phase_7_Meta_Architecture_v1.md` | Lines 127 + 385 descriptive references | PRESERVED VERBATIM (project-level descriptive snapshot; not authoritative code citation) |

**Plan shape preserved.** v2.15's axis-led structure preserved verbatim. No new units; no DAG topology change; no coverage matrix change; no acceptance criterion change. v2.16 is a citation-bookkeeping patch absorbing a single identifier rename at U-CP-47's plan-body declaration.

**Status posture.** Proposed (v2.15) → **Proposed (v2.16)**. v2.16 is a citation-bookkeeping patch — single-identifier rename at U-CP-47 plan body + cross-unit propagation to U-CP-48 plan body. No v2.15 unit re-decomposition; no contract removal; no signature change.

**Downstream absorption owed (post-v2.16).**
(a) Workspace `CLAUDE.md` §2.4 CP plan row version bump (v2.15 → v2.16).
(b) `harness-cp/CLAUDE.md` retirement-table preserved verbatim (the rename does not affect retirement state — substitution H_T-CP-21 surface is unchanged at the substrate level).
(c) Phase 7 cluster-open authorization for 10-CP-A (U-CP-58 + U-CP-59 + U-CP-60 + U-OD-50 + U-CP-61) at next session per `phase-7-implementation` skill discipline — UNBLOCKED post-v2.16 absorption.

**Adjacent defects surfaced (not patched per FM-2 no-extension discipline).** None — apply pass is fidelity-pure transcription of operator-ratified path β.

---

## §1 — U-CP-47 plan-body amendment (v2.16)

The U-CP-47 declaration last canonically authored at `Implementation_Plan_Control_Plane_v2_4.md` §581 (v2.4 amendment — `ValidatorFailClass`, `VALIDATOR_FAIL_METADATA`, `VALIDATOR_FAIL_NAMESPACE_SCHEMA` conformed to CP spec §21.1/§21.5 verbatim per the §4A verbatim-divergence cluster resolution) is amended at v2.16 as follows. Original v2.4 content preserved verbatim except for the identifier rename.

### U-CP-47 — Declare 5-class fail taxonomy + `validator.fail.*` namespace (v2.16 amendment — enum identifier rename `ValidatorFailClass` → `ValidatorRetryExitClass` per path β disambiguation; member values + metadata + namespace schema preserved verbatim)

**Amendment delta (v2.4 → v2.16).** The enum identifier renames from `ValidatorFailClass` to `ValidatorRetryExitClass`. All other plan-body content (member values, metadata structure, namespace schema, signatures, acceptance criteria, tests, rollback boundary) preserved verbatim from v2.4 §581.

**Renamed type declaration (v2.16 amendment).**

```
// v2.16 amendment — enum identifier renamed to disambiguate from C-CP-25 §25.2 ValidatorFailClass
enum ValidatorRetryExitClass {
  TRANSIENT_RETRY = "transient-retry"
  REFLEXION_RECOVERABLE = "Reflexion-recoverable"
  HITL_RECOVERABLE = "HITL-recoverable"
  PERMANENT_FAIL_EXIT = "permanent-fail-exit"
  TERMINAL_FAIL_EXIT = "terminal-fail-exit"
}

ValidatorFailMetadata {
  fail_class           : ValidatorRetryExitClass
  // ... other fields preserved verbatim from v2.4 ...
}
```

**Acceptance criteria (v2.16 amendment).** Criterion #1 (v2.4-authored) updated to cite the renamed identifier:

1. **(v2.16 amendment — enum identifier renamed; member values + cardinality preserved.)** `ValidatorRetryExitClass` declares exactly five values per C-CP-21 §21.1 verbatim — the SCREAMING_SNAKE_CASE rendering of the §21.1 discriminated five-class `validator.fail.class` taxonomy table: `TRANSIENT_RETRY` (`transient-retry`), `REFLEXION_RECOVERABLE` (`Reflexion-recoverable`), `HITL_RECOVERABLE` (`HITL-recoverable`), `PERMANENT_FAIL_EXIT` (`permanent-fail-exit`), `TERMINAL_FAIL_EXIT` (`terminal-fail-exit`). Closed at cardinality 5; extension requires Workflow §4.1.2 Class-2 D5 revision.

Criteria #2 through #N preserved verbatim from v2.4 (all references to `ValidatorFailClass` in those criteria mechanically become `ValidatorRetryExitClass`).

**Rollback boundary (v2.16 amendment).** Revert `ValidatorRetryExitClass` enum + metadata + namespace. R-CP-11 validator-escalation HITL placement loses fail-class discriminator; U-CP-48 staircase loses cause input; U-CP-54 §24.1.A export manifest loses CP-side source. Cross-axis AS edge to U-AS-03 releases. **(v2.16 note: reverting reintroduces the §4A verbatim divergence AND restores the NEW C-CP-25 §25.2 collision.)**

### U-CP-48 — Cross-unit propagation (v2.16 amendment — `TRANSIENT_STAIRCASE_TRANSITIONS` enumeration of values keys on `ValidatorRetryExitClass`)

The v2.4 amendment introduced `TRANSIENT_STAIRCASE_TRANSITIONS` as a mapping `(StaircaseStage, ValidatorFailClass) → StaircaseTransition`. Under v2.16, the second key tuple element becomes `ValidatorRetryExitClass`. The 5-class enumeration of values (TRANSIENT_RETRY / REFLEXION_RECOVERABLE / HITL_RECOVERABLE / PERMANENT_FAIL_EXIT / TERMINAL_FAIL_EXIT) preserved verbatim.

```
function advance_staircase(current: StaircaseStage, cause: ValidatorRetryExitClass, attempt: int) -> StaircaseTransition
```

**Acceptance criterion #2 (v2.16 amendment).** `TRANSIENT_STAIRCASE_TRANSITIONS` implements C-CP-21 §21.2 cause-attribution branching, keyed on the v2.16-renamed `ValidatorRetryExitClass` retry-exit taxonomy. Per §21.2, the transient staircase runs for `cause ∈ {TRANSIENT_RETRY, REFLEXION_RECOVERABLE}`; `PERMANENT_FAIL_EXIT` and `TERMINAL_FAIL_EXIT` **skip the staircase** (route directly to C11 HITL per §21.1).

---

## §2 — DAG topology + coverage matrix preservation

DAG topology preserved verbatim from v2.15. Coverage matrix preserved verbatim: §21.1 ValidatorRetryExitClass 5-class (formerly ValidatorFailClass at v2.15) → U-CP-47.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_16.md` |
| Version | v2.16 |
| Filing event | Path β citation reconciliation — U-CP-47 enum identifier rename absorption, 2026-05-21 |
| Predecessor | `Implementation_Plan_Control_Plane_v2_15.md` (v2.15 substantive content preserved verbatim) |
| Co-published artifacts | runtime spec v1.13 → v1.14; CXA v2.6 → v2.7; 10 landed code files renamed at commit `744848c` |
| Operator authority | `.harness/class_1_fork_u_cp_58_validator_fail_class_collision.md` path β ratification 2026-05-21 |
| Unit-count change | None (73 → 73; no new units) |
| Cluster-count change | None |
| Skill discipline | `phase-7-back-flow-routing` Class 1 fork detection + `phase-7-implementation` carrier-surface inspection |
| Date | 2026-05-21 |
