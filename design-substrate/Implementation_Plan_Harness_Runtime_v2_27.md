# Implementation Plan — Harness Runtime v2.27

## Change-note (v2.26 → v2.27)

**Scope of revision.** Narrow-scope substantive amendment at U-RT-02 in-place absorbing runtime spec v1.30 → v1.31 NEW §3 C-RT-03 `step_dispatch_timeout_seconds: float = 30.0` field + NEW §11 `RT-FAIL-STEP-DISPATCH-TIMEOUT` fail-class. Single-unit-body amendment per Q3(β) operator ratification 2026-05-28 (primitive-scalar field-set extension shape per CP plan v2.25 U-CP-13 + runtime plan v2.26 U-RT-94 precedent; binding-chain L9-N cluster shape reserved for sub-model + factory bindings). NO new units; NO new cluster; NO DAG topology change; ZERO cross-axis cascade. Co-published with runtime spec v1.31 + harness-runtime impl (`types.py` field landing + `stage_5_loop_init.py:332/336/356` 3 callsite updates + comment-marker removal + fail-class registration) + NEW tests + `class_3_tension_u_rt_59_spec_prose_drift.md` Status closure (OPEN → 8-OF-8 CLOSED at §7) + workspace `CLAUDE.md` row bump + fork doc Status PROPOSING → ✅ APPLIED. 2026-05-28.

**v2.26 substantive content preserved verbatim.** All v2.25 NEW §6 L9-quaterdecies cluster (U-RT-96/97/98) preserved unchanged. v2.25/v2.26 §7.1 + §7.3 preserved verbatim. v2.26 §1 U-RT-94 AC #13 in-place amendment preserved verbatim. v2.27 amends U-RT-02 in-place at §1 below; all other unit bodies PRESERVED VERBATIM.

**Source of fix.** Runtime spec v1.30 → v1.31 NEW §3 row + §11 row publication this arc + `.harness/class_1_fork_step_dispatch_timeout_seconds_field_extension.md` Reading A + operator ratification 2026-05-28 (Q1=A required-with-default; Q2=30.0s; Q3=β in-place at U-RT-02; Q4=p `RT-FAIL-STEP-DISPATCH-TIMEOUT`).

**Single amendment site (1 in-place unit-body amendment at U-RT-02).**

| Site | Amendment shape |
|---|---|
| **§1 (NEW at v2.27)** | U-RT-02 (`RuntimeConfig` + `HarnessContext` schemas authoring unit; original authoring at v2.5-or-earlier per delta-only-plan-chain convention) gains: (a) NEW Inputs cite to runtime spec v1.31 §3 row + §11 row; (b) NEW AC absorbing `step_dispatch_timeout_seconds: float = 30.0` field declaration on `RuntimeConfig` (Pydantic v2 BaseModel frozen field; default 30.0; sibling to `drain_timeout_seconds: float = 60.0`); (c) NEW AC absorbing `RT-FAIL-STEP-DISPATCH-TIMEOUT` fail-class registration at the runtime fail-class enum; (d) Files-line extension adding `harness-runtime/src/harness_runtime/bootstrap/stage_5_loop_init.py` (3 callsite updates at lines 332/336/356 reading `config.step_dispatch_timeout_seconds` instead of `config.drain_timeout_seconds`; drift-item-7 comment-marker removal at lines 325-331); (e) NEW Tests-line entries covering `test_step_dispatch_timeout_seconds_default_is_30_seconds` (RuntimeConfig field default assertion) + per-step-timeout-fires-before-drain semantics e2e test. AC count at U-RT-02 +2 (new fail-class AC + new field AC); Files-line +1 entry; Tests-line +2 entries. |

**Adjacent observations (NOT patched per FM-2).**

(i) **The U-RT-02 unit body lives at the v2.5-or-earlier authoring plan version** per delta-only-plan-chain convention; v2.27 IS a delta change-note that downstream readers MUST apply when interpreting the U-RT-02 unit body. v2.11+ delta files do not contain U-RT-02 body text. NO body-text amendment owed at v2.27; the canonical-reading amendment in §1 above IS the canonical interpretation of U-RT-02 going forward.

(ii) **Class 1 fork document closure timing.** Fork doc `.harness/class_1_fork_step_dispatch_timeout_seconds_field_extension.md` Status refresh PROPOSING → ✅ APPLIED published this arc as co-publication with v2.27 (mirror shape with `class_1_fork_h_t_cp_19_default_gate_level_spec_extension.md` single-day 3-arc filing → ratification → application precedent at 2026-05-27). ZERO contract change at any other contract; ZERO unit re-decomposition; ZERO new units; ZERO DAG topology change; ZERO coverage matrix structural delta.

(iii) **`class_3_tension_u_rt_59_spec_prose_drift.md` 8-of-8 closure event.** This arc closes the final outstanding item in the 8-item u_rt_59 spec-prose drift catalogue. The fork doc was filed 2026-05-20 at U-RT-59 Path B wiring landing (`d64d8cf`); 7 items absorbed at v1.30 / v2.26 (2026-05-28 prior arc this session); item §7 absorbed at v1.31 / v2.27 (this arc). Total carry-window: 22 + 1 = 23 delta versions × 8 days. Sub-species at v1.31: **bundled-absorption arc then single-item-residual closure arc** — distinct from prior bundled-absorption sub-species at v1.30 §"Pattern catalogued" because the closure event happens at a SEPARATE arc when one item was carved out from the bundled arc per X-AL-3. Pattern catalogued separately.

**Status posture.** Proposed (v2.26) → **Proposed (v2.27)**. v2.27 is a narrow-scope substantive amendment absorbing the v1.31 spec extension at the plan layer. ZERO new units; unit count 96 → 96.
