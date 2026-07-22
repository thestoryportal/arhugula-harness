# Implementation Plan: Control Plane — v2.40 (delta over v2.39)

*v2.40 is the CP plan leg of the RATIFIED **B-65 post-effect signing-carrier cascade-disposition arc** (`.harness/class_2_fork_b65_post_effect_signing_carrier_cascade_disposition.md`, **RATIFIED 2026-07-21 — the operator selected OPTION A AS RECOMMENDED**: §3 terminal-with-result rider + §3b protected result store), absorbing **CP spec v1.103** (`Spec_Control_Plane_v1_103.md`, filed 2026-07-22 — the ONE CP-owned rider section: AMENDED §25.15 branch-terminal-with-result under every `cascade_policy`). The spec surface + the change-note's fork §2 witnesses (a)–(c) home at **ONE EXISTING unit — U-CP-85** (the §25.15 `cascade_policy` consumption owner per v2.39 §0.2: *"§25.15 `cascade_policy` consumption is U-CP-85"*); witness (d)'s store half is Runtime-owned at the same-arc Runtime plan v2.51 (NEW U-RT-145) — cross-referenced, never restated. ZERO new units; unit count stays 102. All sections except the §0 change note, the §1 U-CP-85 amendment, and the §2 coverage delta below are PRESERVED VERBATIM from v2.39 (delta-only-plan-chain convention).*

**Status:** Proposed

---

## §0 Change-note (v2.39 → v2.40)

### §0.1 Predecessor

`Implementation_Plan_Control_Plane_v2_39.md` (v2.39 — the B-48 CP leg; U-CP-82/85/86/88/89 amended + NEW U-CP-101).

### §0.2 Revision context — CP spec v1.103 absorption

Per the fork's §2 prescription shape ("wire a name-match fence (`type(exc).__name__ == "PostEffectAuditSigningError"` — the established `StepDispatchTimeoutError` precedent; harness-cp cannot import the runtime type) AHEAD of the branch-failure → PAUSED/PARTIAL conversions in `workflow_driver.py`, so the condition stays TERMINAL and RESULT-REFERENCED"). **Empirically verified home unit (this apply pass):** §25.15 `cascade_policy` consumption is U-CP-85 (v2.39 §0.2); the fence applies at the branch-failure → PAUSED/PARTIAL conversion sites of BOTH fan-out strategies' cascade handling (the shared machinery U-CP-85's §25.15.2 obligations govern), so ONE amended unit covers the CP surface — no unit-less impl scope, no new unit.

### §0.3 Sections revised

§0 (this change note); §1 (the U-CP-85 amendment); §2 (coverage delta). All other sections — U-CP-01..U-CP-101 bodies except U-CP-85, all dependency graphs, cross-cutting units, open items — PRESERVED VERBATIM from v2.39.

### §0.4 Scope discipline

Amended-unit scope only. ZERO new atomic units; ZERO new contract IDs; ZERO new DAG edges. Cross-axis co-land pin (recorded, not a DAG edge — one B-65 impl arc): U-CP-85 ⊕ Runtime plan v2.51 U-RT-145 (the protected result store + widened `result_ref` the CP fold carries as an opaque reference VALUE (a discriminated union of live-ref | unresolvable-declaration — carried verbatim with the discriminator intact, never lossily stringified); the fence itself is import-free name-match, so no new package dependency and no new CXA seam). The CP witness classes (fork §2 (a)–(c), each mutation-probed per Workflow v1.18 PD-8) are transcribed as `Tests:` criteria at U-CP-85; witness (d)'s store-resolution half homes at U-RT-145.

---

## §1 U-CP-85 amendment — post-effect signing-carrier fence + terminal-with-result fold semantics (CP v1.103 §1)

The v2.37 U-CP-85 body (the 8 §25.15.2 obligations) + the v2.39 additions are PRESERVED VERBATIM; v2.40 adds:

**Implements (addition):** + C-CP-25 §25.15 (AMENDED at CP v1.103 §1 — the post-effect audit-signing carrier is BRANCH-TERMINAL-WITH-RESULT under EVERY `cascade_policy`).

**Acceptance criteria (v2.40 additions):**

- **(CP v1.103 §1 row 2 — the fence.)** A name-match fence (`type(exc).__name__ == "PostEffectAuditSigningError"` — the established import-free idiom; `harness-cp` cannot import the runtime type) is wired AHEAD of the branch-failure → PAUSED/PARTIAL conversions in `workflow_driver.py`, at the cascade-handling conversion sites of BOTH fan-out strategies — the carrier branch's condition stays TERMINAL and RESULT-REFERENCED before any generic conversion runs. Every other branch-failure class keeps its existing §25.15.1 handling byte-verbatim.
- **(CP v1.103 §1 row 3 — `pause`.)** Under `cascade_policy=pause`, NO resumable PAUSED path is minted for the carrier branch: the branch enters the terminal disposition set (a DISTINCT terminal disposition on the resume-visible record, value naming implementation-discretion per the v1.74 scoped-abort precedent; no IS-hash-bearing ledger change), and §25.15.2 obligation 7's resume-terminality applies — no resume path re-dispatches it, in-resume and crash-resume alike. The REMAINING branches pause per policy (run-level `PAUSED` unchanged).
- **(CP v1.103 §1 row 4 — the folds.)** Under `proceed`/`cascade-cancel`, the PARTIAL/FAILED report fold CARRIES the carrier's `result_ref` — the completed effect's reference is never dropped from the fold. The reference field is carried VERBATIM as an OPAQUE value — the live-ref | unresolvable-declaration discriminated union with the discriminator INTACT, never a lossy stringification (CP neither reads, writes, nor interprets the protected store — Runtime-owned at v1.103 §14.8.11 / U-RT-145).
- **(CP v1.103 §1 row 5.)** Run-level `RunStatus` follows the existing §25.15.1 policy mapping over the REMAINING branches — NO new `RunStatus` value, control-transfer mode, or cascade row.

**Tests (v2.40 additions — mutation-probed per PD-8):**

> **Witness (a) — no resumable PAUSED for the carrier branch:** `test_carrier_branch_under_pause_policy_terminal_no_resumable_paused_snapshot` (a fan-out under `cascade_policy=pause` whose branch raises the carrier mints NO resume path re-dispatching that branch; remaining branches pause per policy; mutation probe: removing the fence converts the carrier branch to resumable PAUSED and fails). **Witness (b) — surfaced failure carries `result_ref`:** `test_partial_and_failed_folds_carry_carrier_result_ref` (parametrized over `proceed`/`cascade-cancel`; mutation probe: dropping the ref from the fold fails). **Witness (c) — no re-dispatch path can re-fire:** `test_no_resume_or_crash_resume_path_redispatches_carrier_branch` (in-resume AND crash-resume, per the scoped-abort precedent; mutation probe: recording the branch under a non-terminal disposition lets resume re-dispatch it and fails). **Witness (d)** (store resolution under the owning tenant + typed cross-tenant refusal) rides Runtime plan v2.51 U-RT-145 — co-land pin.

---

## §2 Coverage matrix delta (v2.39 → v2.40)

| Contract surface | Units covering (delta) |
|---|---|
| C-CP-25 §25.15 post-effect signing-carrier branch-terminality rider (AMENDED at CP v1.103 §1) | **U-CP-85 (amended)** (result-store half Runtime-owned at Runtime plan v2.51 U-RT-145 — cross-axis co-land pin) |

---

## §3 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_40.md` (delta over v2.39) |
| Authored at | Phase 7 — B-65 post-effect signing-carrier cascade-disposition apply leg (2026-07-22) |
| Authoring authority | CP spec v1.103 (`Spec_Control_Plane_v1_103.md`, filed 2026-07-22) + `.harness/class_2_fork_b65_post_effect_signing_carrier_cascade_disposition.md` (RATIFIED 2026-07-21, OPTION A AS RECOMMENDED) |
| Predecessor | `Implementation_Plan_Control_Plane_v2_39.md` (v2.39 — B-48 CP leg) |
| Siblings (same arc) | `Implementation_Plan_Harness_Runtime_v2_51.md` |
| Revision policy | Delta-only per workspace `CLAUDE.md` §2.4; revisions route to design-phase back-flow |
