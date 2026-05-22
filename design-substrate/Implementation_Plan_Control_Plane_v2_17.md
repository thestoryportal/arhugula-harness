# Implementation Plan — Control Plane v2.17

## Change-note (v2.16 → v2.17)

**Scope of revision.** Path γ enum identifier rename absorption per `.harness/class_1_fork_u_cp_63_pause_reason_collision.md` (operator-ratified 2026-05-21) co-published with CP spec v1.11. The U-CP-62 plan-body carrier declaration renames Python enum `PauseReason` → `WorkflowPauseReason` (5-class, workflow-layer pause taxonomy). U-CP-63 + U-CP-64 acceptance criterion #4 (close `pause_resume_protocol.py:121` / `:143` NotImplementedError sites) is STRUCK at v2.17 — those lines hold the OLD U-CP-49 / C-CP-22 §22.1 free-function surface (preserved verbatim at CP spec v1.10/v1.11), which is a distinct architectural primitive from C-CP-26 §26 per the v1.11 §26 NEW NOTE coexistence statement. U-CP-65 cited consumer-side enum at U-OD-51 — preserved by section number (§C-OD-30.1) which itself absorbs the rename; no AC-text change at U-CP-65.

**v2.16 substantive content preserved verbatim.** All v2.16 content (U-CP-00 through U-CP-72; the v2.16 path-β `ValidatorFailClass` → `ValidatorRetryExitClass` rename at U-CP-47 + U-CP-48; all clusters; DAG topology; coverage matrix) preserved unchanged outside the 3 amendment sites enumerated below. The v2.15 + v2.14 + ... + v2 chain all preserved.

**Source of fix.** Phase 7b implementation-arc fork detection per `phase-7-back-flow-routing` skill discipline:
- Pre-implementation carrier-surface inspection at U-CP-62 entry surfaced the `PauseReason` namespace collision (NEW C-CP-26 §26.2 5-class vs OLD C-CP-22 §22.1 4-class).
- Operator-ratified path γ (rename NEW enum to `WorkflowPauseReason`) over alternatives α / β / δ.
- Operator-ratified inclusion of §22 ↔ §26 coexistence NOTE at CP spec v1.11.
- Operator-ratified naming: `WorkflowPauseReason` over `ProtocolPauseReason` / `ExplicitPauseReason` (advisor-flagged: `ExplicitPauseReason` semantically wrong for system-triggered members TIMEOUT_BOUNDARY + EXTERNAL_DEPENDENCY).
- The v1.11 §26 NEW NOTE explicitly states: "The OLD `pause_resume_protocol.py:121` + `:143` NotImplementedError sites belong to the OLD §22 / U-CP-49 surface and are NOT closed by C-CP-26 / U-CP-63 / U-CP-64." → AC #4 strike at v2.17.
- Co-published artifacts: CP spec v1.11; OD spec v1.9; OD plan v2.15; CXA v2.8.

**Three amendment sites.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **U-CP-62 — carrier identifier rename** | Plan body Python enum identifier `PauseReason` renames to `WorkflowPauseReason`. Member values + cardinality (5) + string-value mapping preserved verbatim. AC #1 + AC #2 text updates to cite renamed identifier. File path (`harness-cp/src/harness_cp/pause_resume_protocol_types.py` NEW) preserved. | CP spec v1.11 §26.2 rename |
| **U-CP-63 — AC #4 strike** | The v2.15-authored AC #4 "Existing `harness-cp/src/harness_cp/pause_resume_protocol.py:121` NotImplementedError closed" is STRUCK at v2.17. CP spec v1.11 §26 NEW NOTE: line 121 is the OLD U-CP-49 free-function surface, NOT the NEW class-method surface. AC #1 + AC #2 + AC #3 + AC #5 preserved verbatim. AC count: 5 → 4 (renumbered for cleanliness — original AC #5 becomes v2.17 AC #4). | CP spec v1.11 §26 NEW NOTE |
| **U-CP-64 — AC #4 strike** | Symmetric to U-CP-63 — the v2.15-authored AC #4 "EXTEND — closes line 143 NotImplementedError" interpretation STRUCK. AC text in v2.15 actually has different content at #4 (`OPERATOR_ARBITRATE policy`); the file-EXTEND-closes-line-143 instruction at the Files column is preserved (the file is EXTENDED — but the new class-method body is added; old free-function at line 128–147 stays as-is). The Files column citation is amended: was "EXTEND — closes line 143 NotImplementedError"; v2.17: "EXTEND — adds `PauseResumeProtocol.attempt_resume()` method; OLD free-function `attempt_resume(attempt: ResumeAttempt)` at lines 128–147 preserved verbatim per CP spec v1.11 §26 NEW NOTE coexistence". AC #1 through AC #5 text preserved verbatim. | CP spec v1.11 §26 NEW NOTE |

**Symmetric Files-column amendment at U-CP-63.** Similarly, the v2.15-authored U-CP-63 Files column note "EXTEND — closes line 121 NotImplementedError" is amended at v2.17: "EXTEND — adds `PauseResumeProtocol.capture_pause_snapshot()` method; OLD free-function `capture_pause_snapshot(workflow_id, pause_reason)` at lines 106–125 preserved verbatim per CP spec v1.11 §26 NEW NOTE coexistence".

**U-CP-65 status.** U-CP-65 cites U-OD-51 cross-axis soft-dep + OD spec §C-OD-30.1 attribute names. §C-OD-30.1 attribute `pause.reason` attribute-name string preserved verbatim at OD spec v1.9; only the attribute-TYPE cite renames (enum class name). U-CP-65 ACs cite section numbers, not Python class identifiers — no AC-text change. **U-CP-65 preserved verbatim from v2.16.**

**Plan shape preserved.** v2.16's 73-unit axis-led structure preserved verbatim. No new units; no DAG topology change (U-CP-62 stays L0-within-Cluster-10 delta; U-CP-63/64 at L1/L2; U-CP-65 at L3 with cross-axis soft-dep); no coverage matrix change (§26 → U-CP-62/63/64/65 still). v2.17 is a citation-and-AC-bookkeeping patch absorbing the path γ rename.

**Status posture.** Proposed (v2.16) → **Proposed (v2.17)**. v2.17 is a fidelity-bookkeeping patch — single-identifier rename at U-CP-62 plan body + two AC #4 strikes at U-CP-63/64 + two Files-column note amendments at U-CP-63/64. No v2.16 unit re-decomposition; no contract removal; no signature change beyond the enum identifier; no DAG change.

**Downstream absorption owed (post-v2.17).**
(a) Workspace `CLAUDE.md` §2.4 CP plan row version bump (v2.16 → v2.17).
(b) `harness-cp/CLAUDE.md` retirement-table preserved verbatim (the rename does not affect retirement state — substitution H_T-CP-22 surface is the C-CP-22 / U-CP-49 surface; the v2.17 amendment preserves that surface untouched).
(c) Phase 7b cluster-open authorization for 10-CP-B (U-CP-62 + U-CP-63 + U-CP-64 + U-CP-65 + U-OD-51 cross-axis) at next session per `phase-7-implementation` skill discipline — UNBLOCKED post-v2.17 absorption.

**Adjacent defects surfaced (not patched per FM-2 no-extension discipline).** One observation — the v2.15-authored U-CP-63/64 AC #4 "close NotImplementedError" was itself a silent-absorption of the §22 ↔ §26 coexistence ambiguity (the v2.15 / v2.16 plan author absorbed the line-121/143 closure as the new-spec surface; the v1.11 NEW NOTE makes the coexistence explicit and the v2.17 AC #4 strike unwinds the silent absorption). The v2.17 absorption preserves AC #4 strike as the unwinding mechanism; no further plan-text amendment owed beyond the strike + Files-column note amendment.

---

## §1 — U-CP-62 plan-body amendment (v2.17)

The U-CP-62 declaration last canonically authored at `Implementation_Plan_Control_Plane_v2_15.md` §1 is amended at v2.17 as follows. Original v2.15 content preserved verbatim except for the identifier rename. v2.16 path-β absorption preserved verbatim (v2.16 did not touch U-CP-62).

### U-CP-62 — WorkflowPauseReason + MaterialDiffPolicy + PauseSnapshot + ResumeResult schemas (v2.17 amendment — enum identifier rename `PauseReason` → `WorkflowPauseReason` per path γ disambiguation; member values + cardinality + Pattern-D inheritance preserved verbatim)

**Amendment delta (v2.15 → v2.17).** The 5-class enum identifier renames from `PauseReason` to `WorkflowPauseReason`. All other plan-body content (member values, MaterialDiffPolicy 3-class, PauseSnapshot dataclass field set, ResumeResult dataclass field set, signatures, acceptance criteria #3-#5, tests, rollback boundary) preserved verbatim from v2.15.

- **Implements:** CP spec v1.11 §26.2 (WorkflowPauseReason 5-class enum + MaterialDiffPolicy 3-class enum + PauseSnapshot dataclass + ResumeResult dataclass)
- **Files:** `harness-cp/src/harness_cp/pause_resume_protocol_types.py` (NEW)
- **Signatures:** 2 enums + 2 dataclasses
- **Depends on:** (none within this delta) [HIGH]
- **ACs (v2.17 amendment):**
  1. **(v2.17 amendment — enum identifier renamed; member values + cardinality preserved.)** `WorkflowPauseReason` 5-class enum with all members per CP spec v1.11 §26.2: `EXPLICIT_OPERATOR` (`explicit_operator`), `HITL_PENDING` (`hitl_pending`), `VALIDATOR_ESCALATION` (`validator_escalation`), `TIMEOUT_BOUNDARY` (`timeout_boundary`), `EXTERNAL_DEPENDENCY` (`external_dependency`).
  2. `MaterialDiffPolicy` default value = `STRICT` (per Decision 2.D7 RATIFIED)
  3. `PauseSnapshot.state_summary` typed against existing CP plan v2.9 `StateSummary` (Pattern-D inherited)
  4. `PauseSnapshot.snapshot_hash` is sha256 hex string (64 chars)
  5. `ResumeResult.diff_summary_hash` optional per spec §26.2

**Rollback boundary (preserved verbatim from v2.15).** Revert the 2-enum + 2-dataclass module. U-CP-63 + U-CP-64 + U-CP-65 (within-axis dependents) release. U-OD-51 (cross-axis dep on U-CP-62) loses producer-side carrier.

---

## §2 — U-CP-63 plan-body amendment (v2.17)

### U-CP-63 — PauseResumeProtocol.capture_pause_snapshot() (v2.17 amendment — AC #4 STRUCK + Files-column note amended per CP spec v1.11 §26 NEW NOTE coexistence)

**Amendment delta (v2.15 → v2.17).** AC #4 (line-121 NotImplementedError closure) STRUCK. Files-column note amended to reflect coexistence with OLD U-CP-49 free-function surface. All other plan-body content (signatures, AC #1, AC #2, AC #3, AC #5, tests, rollback boundary) preserved verbatim from v2.15.

- **Implements:** CP spec v1.11 §26.1 capture_pause_snapshot signature + §26.6 invariants 1-3
- **Files:** `harness-cp/src/harness_cp/pause_resume_protocol.py` (EXTEND — adds `PauseResumeProtocol.capture_pause_snapshot()` class method; OLD free-function `capture_pause_snapshot(workflow_id, pause_reason)` at lines 106–125 preserved verbatim per CP spec v1.11 §26 NEW NOTE coexistence)
- **Signatures:** `async def capture_pause_snapshot(self, workflow_id, run_id, step_index, pause_reason) -> PauseSnapshot` (class method on `PauseResumeProtocol`)
- **Depends on:** [U-CP-62]
- **ACs (v2.17 amendment — AC #4 STRUCK; AC #5 renumbered to AC #4):**
  1. Snapshot computes `snapshot_hash` via canonical serialization of (workflow_id + run_id + step_index + state_summary)
  2. Snapshot immutable after capture (frozen dataclass)
  3. State-ledger anchor populated with current `entry_hash` from `ctx.state_ledger_writer`
  4. Unit test: capture + verify hash + verify immutability *(v2.17 — renumbered from v2.15 AC #5; v2.15 AC #4 "Existing harness-cp/src/harness_cp/pause_resume_protocol.py:121 NotImplementedError closed" STRUCK per CP spec v1.11 §26 NEW NOTE — line 121 is the OLD §22 / U-CP-49 surface, not the NEW §26 / U-CP-63 class-method surface)*

**Rollback boundary (preserved verbatim from v2.15).** Revert the `PauseResumeProtocol.capture_pause_snapshot()` class method. U-CP-64 (within-axis dep) loses producer side; U-CP-65 (span emission) loses capture-site emission.

---

## §3 — U-CP-64 plan-body amendment (v2.17)

### U-CP-64 — PauseResumeProtocol.attempt_resume() + material-diff detection (v2.17 amendment — Files-column note amended per CP spec v1.11 §26 NEW NOTE coexistence; line-143 closure interpretation STRUCK)

**Amendment delta (v2.15 → v2.17).** Files-column note amended to reflect coexistence with OLD U-CP-49 free-function surface. v2.15 ACs at U-CP-64 do NOT include a line-143-closure AC item (v2.15 AC #5 at U-CP-64 is "Coexist with U-CP-56 prefix-replay-based resumption" — preserved verbatim); the line-143 closure interpretation lived only at the Files-column note, and v2.17 amends that note. All plan-body ACs (#1 through #5) preserved verbatim from v2.15.

- **Implements:** CP spec v1.11 §26.1 attempt_resume signature + §26.6 invariants 4-5
- **Files:** `harness-cp/src/harness_cp/pause_resume_protocol.py` (EXTEND — adds `PauseResumeProtocol.attempt_resume()` class method; OLD free-function `attempt_resume(attempt: ResumeAttempt)` at lines 128–147 preserved verbatim per CP spec v1.11 §26 NEW NOTE coexistence)
- **Signatures:** `async def attempt_resume(self, snapshot, *, material_diff_policy) -> ResumeResult` (class method on `PauseResumeProtocol`)
- **Depends on:** [U-CP-62, U-CP-63]
- **ACs (preserved verbatim from v2.15):**
  1. Snapshot hash validated on resume; corruption → `CP-FAIL-PAUSE-SNAPSHOT-CORRUPTION`
  2. Material diff detected when `state_ledger_anchor` no longer reachable from current entry chain
  3. STRICT policy: diff → `CP-FAIL-RESUME-MATERIAL-DIFF-DETECTED`
  4. OPERATOR_ARBITRATE policy: diff → `CP-FAIL-RESUME-OPERATOR-ARBITRATION-OWED` + HITL escalation
  5. Coexist with U-CP-56 prefix-replay-based resumption (Path A-modified preserved)

**Rollback boundary (preserved verbatim from v2.15).** Revert the `PauseResumeProtocol.attempt_resume()` class method. U-CP-65 (span emission) loses resume-site emission. The 3 CP-FAIL classes go un-raised.

---

## §4 — U-CP-65 status (v2.17 — preserved verbatim from v2.16)

U-CP-65 cites OD spec §C-OD-30.1 attribute names (lowercase dot-notation string literals at OTel emission). The §C-OD-30.1 attribute-name layer is independent of the Python enum identifier layer (the rename absorbs at the attribute-TYPE cite cell only). U-CP-65 ACs reference section numbers, not Python class identifiers. **U-CP-65 declaration preserved verbatim from v2.16; no amendment owed at v2.17.**

---

## §5 — DAG topology + coverage matrix preservation

DAG topology preserved verbatim from v2.16. Coverage matrix preserved verbatim: §26.1 + §26.2 + §26.6 → U-CP-62, U-CP-63, U-CP-64; §26.4 → U-CP-65 (with U-OD-51 cross-axis soft-dep).

Cluster 10-CP-B (U-CP-62 + U-CP-63 + U-CP-64 + U-CP-65 + U-OD-51 cross-axis) — UNBLOCKED for next implementation arc post-v2.17 absorption.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_17.md` |
| Version | v2.17 |
| Filing event | Path γ enum identifier rename absorption + U-CP-63/64 AC #4 + Files-column-note strike, 2026-05-21 |
| Predecessor | `Implementation_Plan_Control_Plane_v2_16.md` (v2.16 substantive content preserved verbatim outside U-CP-62 + U-CP-63 + U-CP-64 amendment sites) |
| Co-published artifacts | CP spec v1.11; OD spec v1.9; OD plan v2.15; CXA v2.8; workspace CLAUDE.md + per-axis CLAUDE.md pointer bumps |
| Operator authority | `.harness/class_1_fork_u_cp_63_pause_reason_collision.md` path γ ratification 2026-05-21 |
| Unit-count change | None (73 → 73; no new units) |
| Cluster-count change | None |
| AC-count change | U-CP-63: 5 → 4 (AC #4 line-121-closure STRUCK; AC #5 renumbered to #4). U-CP-62 + U-CP-64 + U-CP-65: unchanged. |
| Skill discipline | `phase-7-back-flow-routing` Class 1 fork detection + `phase-7-implementation` carrier-surface inspection (`[[carrier-surface-inspection-catches-namespace-collision]]` pattern applied at U-CP-62 entry) + advisor pre-execution pass |
| Date | 2026-05-21 |
