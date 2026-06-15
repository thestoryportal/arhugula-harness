# R-FS-1 B3-plan — Smart-HITL Atomic-Unit Decomposition

**Authored:** 2026-06-14 · **Arc:** R-FS-1 child arc **B3** (smart-HITL), **B3-plan** leg (arc #20) · **Posture:** design-phase (authors `design-substrate/**` plan deltas + this `.harness/` companion) · **HEAD at authoring:** `a356929`

**What this is.** The implementation-planner decomposition of the two cleared B3 spec legs (**runtime spec v1.49 §3.8** `HITLAutoApprovePolicy` + **runtime spec v1.50 §14.8.9** timeout-degradation dispatch-on-mode) PLUS the design-§8.2 impl-against-cleared-spec gaps, into atomic units across two delta-only plan amendments: **CP v2.32 → v2.33** + **runtime v2.43 → v2.44**. Mirrors the B1-plan precedent (co-published CP + runtime deltas with an aggregate cross-axis DAG). Decomposes; does not author spec/code.

**Inputs re-grounded by direct read at HEAD `a356929`:** the B3 design (`.harness/r-fs-1-b3-smart-hitl-design-v1.md`), runtime spec §3.8 + §14.8.9, both fork docs (F-B3-1 + F-B3-2, both RATIFIED), CP plan v2.32 + runtime plan v2.43, AS spec C-AS-03 §3.1 + C-AS-12 §12.1, AS plan v1.4, and the code surfaces (`hitl_gate_composer.py`, `gate_level_rule.py`, `tool_contract.py`, `hitl_timeout_degradation.py`, `hitl_placement.py`, `ask_user_question_surface.py`).

---

## §1 — The keystone homing fact

The `RuntimeHITLGateComposer` lives in **`harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py`** (verified at HEAD), NOT `harness-cp`. So the gate-site logic (blast resolver, gate_level-once, palette-thread, EDIT-replace, degradation-attr/dispatch, `HITLAutoApprovePolicy` consumption) is **runtime-homed**. The CP package carries only the `GateLevelInput` carrier-shape (U-CP-91) + the `TimeoutDegradationKind` vocab reconciliation (U-CP-92); the AS package owes the G2c `ToolContract.per_tool_gate_level` carrier (registered, O-CP-3). This homing drives the unit-placement split below.

---

## §2 — Unit list

### Runtime plan v2.44 (6 NEW units — U-RT-115..120)

| Unit | Title | Depends on | B3-impl arc | Spec-cite |
|---|---|---|---|---|
| **U-RT-115** | `resolve_step_blast_radius(step, ctx) → BlastRadiusTier` per-step-kind resolver (G1-blast) | (none) | B3-impl-1 | runtime v1.49 §3.8 (in-`max()` consumer); C-CP-19 §19.1 (`BLAST_RADIUS_GATE_LEVEL_FLOOR`); AS C-AS-03 §3.1 (`ToolContract.blast_radius_tier`); C-CP-12 §12.2 (`compute_child_blast_radius_ceiling`); design §3.2 |
| **U-RT-116** | `HITLAutoApprovePolicy` stage-5 ingestion + in-`max()` floor-override consumption (G1-skip) | [U-RT-115, U-CP-91 (cross-axis: CP)] | B3-impl-1 | runtime v1.49 **§3.8** (PRIMARY); F-B3-1; C-CP-19 §19.1 |
| **U-RT-117** | compute `gate_level` once + thread real value to step-4d palette (G2; D-palette) | [U-RT-115, U-RT-116] | B3-impl-1 | runtime §14.8.2 step-4d (Reading B v1.22); C-CP-19 §19.4; design §4 |
| **U-RT-118** | timeout `degradation_mode_applied` attribute wiring (G4a) | (none) | B3-impl-2 | runtime §14.8.2 step-4f; runtime v1.50 §14.8.9 (G4a half); C-CP-21 §21.8; design §6.1 |
| **U-RT-119** | timeout-degradation dispatch-on-mode (G4b) | [U-RT-118, U-CP-92 (cross-axis: CP)] | B3-impl-2 | runtime v1.50 **§14.8.9** (PRIMARY); F-B3-2; C-CP-21 §21.8; ADR-D5 §1.6; §14.8.8 |
| **U-RT-120** | EDIT replace-not-merge `step.step_payload` (G3; D-edit) | (none) | B3-impl-3 | runtime §14.8.2 step-4i + §14.8.7 NOTE 6-ii; design §5; C-CP-13 (`HITLGateResult.edited_proposal`) |

### CP plan v2.33 (2 NEW units — U-CP-91/92)

| Unit | Title | Depends on | B3-impl arc | Spec-cite |
|---|---|---|---|---|
| **U-CP-91** | `GateLevelInput` floor-override carrier-shape (F-B3-1 §3.2 / U-CP-43 plan-carrier) | (none) | B3-impl-1 | C-CP-19 §19.1; F-B3-1 §3.2 (PLAN-carrier, NOT a CP-spec fork); runtime v1.49 §3.8 |
| **U-CP-92** | `TimeoutDegradationKind` vocab-B→vocab-A reconciliation + fail-open config-guard (F-B3-2 AC-1/AC-2) | (none) | B3-impl-2 | F-B3-2; runtime v1.50 §14.8.9 AC-1/AC-2; CP §21.8; ADR-D5 §1.6; CP §20.6 |

**Total: 8 NEW units** (6 RT + 2 CP) + 2 cross-axis edges (both RT→CP, downstream).

---

## §3 — Coverage matrix (every cleared spec subsection + every design §8.2 gap → unit or disposition)

| Cleared spec / design gap | Disposition |
|---|---|
| runtime spec **v1.49 §3.8** (`HITLAutoApprovePolicy` + step-4c in-`max()` consumption + AC-1/AC-2) | **U-RT-116** (+ U-CP-91 carrier, cross-axis) |
| runtime spec **v1.50 §14.8.9** (timeout-degradation dispatch-on-mode + AC-1/2/3) | **U-RT-119** (+ U-CP-92 vocab, cross-axis) |
| design §8.2 **G1-blast** (`resolve_step_blast_radius` per-step-kind producer) | **U-RT-115** |
| design §8.2 **G2** (compute `gate_level` once + thread to 4d palette) | **U-RT-117** |
| design §8.2 **G2c** (`ToolContract.per_tool_gate_level` producer — deny-row-reaching axis) | **REGISTERED — CP plan v2.33 §6 O-CP-3** (owed AS-spec reconciliation; impl-vs-fork class deferred to that gate; NOT a unit, NOT pre-stamped fork, NOT authored as impl) |
| design §8.2 **G3** (EDIT replace-not-merge) | **U-RT-120** (sub-fork conditional on D-edit.B HEAD-check — runtime O-RT-3) |
| design §8.2 **G4a** (degradation-mode attribute) | **U-RT-118** |
| design **G4b** (degradation dispatch — now SPEC'd at §14.8.9) | **U-RT-119** |
| F-B3-1 §3.2 **`GateLevelInput` carrier-shape** (U-CP-43 plan-carrier) | **U-CP-91** |
| F-B3-2 **vocab reconciliation + fail-open guard** | **U-CP-92** |
| design §7 **G5** (HandoffContext non-empty summary) | **OUT of scope** — distinct B3-impl-handoff summarization-producer follow-on arc (design §7; a summarization-model invocation, composes-not-blocks the G1-G4 core) |
| G2b (palette `cross_trust_state=NONE`) | **NO GAP** — spec-correct at wrap-time (§14.8.2 line 3353); preserved by U-RT-117 |

**No silent gap.** Every cleared spec subsection + every design §8.2 impl-against-cleared-spec gap → a unit OR an explicit disposition. G2c is the one **surfaced finding** (see §5).

---

## §4 — Aggregate cross-axis DAG (B3 arc)

8 nodes (2 CP + 6 RT). Cross-axis home: CP plan v2.33 §3.4.

**Per-unit deps:**
- Leaves (`(none)`): U-CP-91, U-CP-92, U-RT-115, U-RT-118, U-RT-120
- U-RT-116 → {U-RT-115, U-CP-91 (cross-axis CP)}
- U-RT-117 → {U-RT-115, U-RT-116}
- U-RT-119 → {U-RT-118, U-CP-92 (cross-axis CP)}

**Topological order:** `U-CP-91, U-CP-92, U-RT-115, U-RT-118, U-RT-120` (foundational) → `U-RT-116, U-RT-119` → `U-RT-117`. A valid linear extension exists ⟹ **DAG**.

**Acyclicity + cross-axis cycle guard:**
- Both cross-axis edges (U-RT-116 → U-CP-91; U-RT-119 → U-CP-92) run **RT→CP**, matching the `harness-runtime` → `harness-cp` package dependency (downstream).
- No CP unit depends on any U-RT-* (U-CP-91/92 are foundational leaves; the composer READS the CP carrier/enum, the CP package never reads back) → **no CP↔RT cycle**.
- RT-internal: every edge points to a strictly-earlier node (115/118/120 foundational; 116→115; 117→115/116; 119→118) → no back-edge.
- **Acyclic confirmed.** No edge to a not-yet-existing unit (U-CP-91/92 are co-published in v2.33; the §14.8.8 webhook surface + `on_hitl_timeout` + both `edited_proposal` carriers all pre-exist at HEAD).

---

## §5 — The one FORK-class finding surfaced (G2c)

**G2c (`ToolContract.per_tool_gate_level` producer) owes an AS-spec reconciliation whose impl-vs-fork classification belongs to that gate — REGISTERED, not pre-decided.**

- The B3 design §4.1 framed G2c as a "faithful carrier factor-out (U-CP-00c precedent)" — pure impl. **Direct read of AS spec C-AS-03 §3.1 partially falsifies the pure-impl framing:** the TYPED `ToolContract` schema declares only `minimum_tier` + `blast_radius_tier` (+ `required_secrets`); there is **NO `per_tool_gate_level` typed field**. `per_tool_gate_level` lives only as (i) a `gate_level()` formula axis at C-AS-12 §12.1 and (ii) a SKILL.md/MCP-manifest authoring-prose token at C-AS-03 §3-frontmatter (AS spec line 1155). The landed `harness_as.tool_contract.ToolContract` matches the §3.1 typed schema.
- This is the **missing-declaration-site shape** (concept spec-committed at the §12.1 axis + §3-frontmatter token; declaration site absent on the §3.1 typed schema). Whether materializing it is a **faithful factor-out** (impl, the U-CP-00c precedent the workspace ratified as such) **or a contract-surface extension** (FORK) is a **ratification-gate call, NOT the planner's** — and the design §4.1 explicitly deferred it ("verify at B3-spec whether a thin AS-spec reconciliation is owed vs a pure impl factor-out").
- **The completed B3-spec-1/2 arcs touched ZERO AS spec** (F-B3-1 cascade: AS spec ZERO; F-B3-2 is CP/ADR-only) — so that verification never happened. **G2c owes an AS-leg of B3-spec that was skipped.**
- **Disposition (CP plan v2.33 §6 O-CP-3):** REGISTERED per FULL-SPEC (not dropped); NOT pre-stamped "fork" (pre-selecting a fork when the gate might rule impl is the inverse error); NOT authored as cleared impl (silently impl'ing an un-cleared AS-package contract surface = X-AL-3 silent-absorption). Routing: when the AS-leg of B3-spec opens, ground AS C-AS-03 §3.1 + C-AS-12 §12.1 + the AS plan, classify impl-vs-fork at that gate, and co-publish a thin AS plan amendment (B1 precedent: co-published 3 plans incl. IS for U-IS-19) OR file the AS-spec back-flow.
- **G2c does NOT block B3-impl-1:** the smart-HITL headline (conditional skip) is delivered by G1 (U-RT-115/116 + U-CP-91) without G2c. G2 (U-RT-117) lands as cleared impl; its deny-row narrowing is behaviorally inert-but-harmless until G2c lands (by the design §4.1 arithmetic, wrap-time `gate_level ∈ {AUTO, ASK}` only — `per_tool` defaults AUTO — so threading the real `gate_level` is correct-but-deny-payoff-dormant, no harm).

**Justified divergence from the design's "G2 + G2c ship together":** rather than block the cleared G2 structural cleanup behind the un-cleared AS gate, U-RT-117 lands G2 independently (X-AL-3-clean; the forbidden silent-impl of G2c is NOT taken). Surfaced to the operator.

---

## §6 — B3-impl sequencing (design §8.3)

| Arc | Units | What it delivers |
|---|---|---|
| **B3-impl-1** | U-CP-91 + U-RT-115 + U-RT-116 + U-RT-117 | G1 conditional-skip headline (the smart-HITL keystone) + G2 palette structural cleanup. G2c registered-not-built (deny-row inert-but-harmless). **AC-1 C10 audit-wiring** (verify §20.1 emission not-vacuous by execution before skip goes live) + **AC-2** (EXTERNAL_REVERSIBLE not representable, contrasting-baseline). |
| **B3-impl-2** | U-CP-92 + U-RT-118 + U-RT-119 | vocab-B→vocab-A reconciliation → degradation-mode attribute → dispatch-on-mode. Closes the OQ-6 producer-gate (the composer timeout path IS the wall-clock-wait orchestrator). **AC-1** (fail-open refused at ALL tiers, detect-then-refuse) + **AC-2** (vocab matches CP §21.8 / ADR-D5 §1.6) + **AC-3** (dispatch not vacuous, per-mode e2e). |
| **B3-impl-3** | U-RT-120 | EDIT replace-not-merge. Sub-fork (D-edit.B) owed ONLY if the §14.8.3 structured-elicitation surface is NOT wired (an executor HEAD-state check, not a planner decision). |
| **B3-impl-handoff** | G5 summarization | Separate follow-on; composes-not-blocks; OUT of B3-plan scope (design §7). |
| **G2c (when AS-leg opens)** | O-CP-3 | AS-spec reconciliation → classify impl-vs-fork → co-publish AS plan amendment or file AS-spec back-flow. |

---

## §7 — Files written

- `design-substrate/Implementation_Plan_Control_Plane_v2_33.md` (delta over v2.32; +2 units U-CP-91/92 + §3.4 B3 aggregate DAG + §4.2 coverage + O-CP-3; all prior content PRESERVED VERBATIM — verified 0 prior unit-body line changes)
- `design-substrate/Implementation_Plan_Harness_Runtime_v2_44.md` (delta over v2.43; +6 units U-RT-115..120 + §2.3 + §3.1a/§3.2 DAG + §4.1a coverage + O-RT-2/3; all prior content PRESERVED VERBATIM — verified)
- `.harness/r-fs-1-b3-plan-decomposition.md` (this summary)

**Clearance markers — ✅ FILED:** `Implementation_Plan_Control_Plane-v2_33-cleared-2026-06-14.md` + `Implementation_Plan_Harness_Runtime-v2_44-cleared-2026-06-14.md`. Workspace `CLAUDE.md` §2.4 + `.harness/claude-artifact-pointers.md` §2.4 plan-head bumps — ✅ APPLIED (CP v2.32→v2.33; runtime v2.43→v2.44).

**Decorrelated review — ✅ COMPLETE (per design §9 precedent):** harness-adversarial-reviewer (genuine dedicated agent) **APPROVE-WITH-CLASS-3** (F3-01 cross-ref-widen applied) + out-of-family Codex (3 [P2] ALL applied: markers filed + pointer bumps + the U-CP-91 impossible-no-field-path foreclosed) + advisor (planner pre-done). Recorded at the clearance markers + `.harness/adversarial-review-r-fs-1-b3-plan.md`. **Decorrelation payoff:** Codex caught the impossible GateLevelInput-lowering path (substantive) the adversarial agent missed; the agent caught the cross-spec-drift docstring (F3-01) Codex missed.
