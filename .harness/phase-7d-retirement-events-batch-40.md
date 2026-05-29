# Phase 7d Retirement Events — Batch 40

| Field | Value |
|---|---|
| Batch number | 40 |
| Filed at | 2026-05-28 (same-session-sequel to batch-39 IS-4 closure; U-RT-59 overlooked-sibling close pattern surfaced via CP-axis STILL-BOUNDED audit) |
| Filed by | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5 + workflow v1.12 §7.4.7.3.C retirement-tier-transit audit-template + 34th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` |
| Predecessor batch | `phase-7d-retirement-events-batch-39.md` (2026-05-28 — H_T-IS-4 STILL-BOUNDED → RETIRED-AS-AUTHORING-ONLY) |

---

## §0 Batch context

**Status type: 1 STILL-BOUNDED → RETIRED transit (H_T-CP-12) via substantive substitution-retirement under U-RT-59 overlooked-sibling close pattern. Cumulative RETIRED count increments 40/54 → 41/54 (75.9%); STILL-BOUNDED count decrements 7/54 → 6/54 (11.1%); RETIRE-READY + PARTIAL + STILL-BOUNDED-INDEFINITELY counts unchanged. Pipeline-advanced 45/54 → 46/54 = 85.2% (+1.9 percentage points). Cardinality check: 41 + 2 + 3 + 6 + 2 = 54 ✓.**

**Workspace crosses 75% RETIRED + 85% pipeline-advanced thresholds. CP-axis crosses 18/22 = 81.8% RETIRED — third axis above 80% RETIRED (after IS-axis 88.9% + AS-axis 81.8%).**

This batch records the **STILL-BOUNDED → RETIRED transit** for H_T-CP-12 (sub-agent privilege inheritance + monotonic-only descent) via **substantive substitution-retirement**. This is the **U-RT-59 overlooked-sibling close pattern**: U-RT-59 sub-agent dispatch composer landing (which closed CP-14 at batch-29) ALSO operationalized C-CP-12 §12.1-§12.5 contract surfaces end-to-end at production. The pre-batch-40 ledger v2 gate text was set pre-U-RT-59 + pre-AS-4 batch-19 and never refreshed; advisor pre-substantive audit + empirical grep at HEAD discriminated cleanly to substantive retirement.

**Distinct from sub-species 10** (gate-text-stale-vs-production-landings) catalogued at OD-1/OD-7/IS-4 — those closures had H_T contract = typed-declaration-itself OR H_E-surface-IS-canonical-substrate OR no-automated-H_E-surface. CP-12 has substantive runtime contract surfaces (§12.1 default-downgrade rule + §12.2 max() gate-level composition formula + §12.3 monotonic-only descent enforcement + §12.4 per-class override + §12.5 audit-ledger discipline) that ALL require runtime invocation — and production invokes ALL of them via the U-RT-59 chain.

| Check | Finding | Authority |
|---|---|---|
| 1. CP spec C-CP-12 §12.1 default-downgrade rule per blast-radius tier (4-row table) | Substrate `harness-cp/src/harness_cp/default_downgrade_rule.py` (`DEFAULT_DOWNGRADE_RULE` + `compute_child_blast_radius_ceiling`); runtime invocation at `handoff.py:136` ("Per C-CP-12 §12.2-§12.4: child blast-radius ceiling from the [default-downgrade rule]"); `fallback_chain.py:146` carries `DEFAULT_DOWNGRADE_RULE` directly per "AC #2: downgrade rule" comment at line 24. | empirical grep this session |
| 2. CP spec C-CP-12 §12.2 sub-agent gate-level composition formula (`max(parent, per_tool, blast_radius_floor, mcp_server_trust, persona_tier)`) | Substrate `harness-cp/src/harness_cp/sub_agent_gate_level_descent.py` (`dispatch_sub_agent` + `compute_child_blast_radius_ceiling`); runtime invocation at `handoff.py:159` `assert_ascent` docstring "Enforce the C-CP-12 §12.2 monotonic-descent invariant"; `types.py:742` `_max_gate_level_descent` docstring "Enforce C-CP-12 §12.2 monotonic-descent (child <= parent gate level)"; `workflow_driver.py:174` cites "(C-RT-17) per C-CP-12 §12.2 gate-level composition + C-CP-13 §13.5" at gate-level composition site. | empirical grep this session |
| 3. CP spec C-CP-12 §12.3 monotonic-only descent (3-dim joint ascent: gate_level + sandbox_tier + persona_tier) | gate_level dim: §12.2 invocation per Check 2; sandbox_tier dim: AS-1 RETIRED via `handoff.py:174` monotonic-ascent per harness-as/CLAUDE.md; persona_tier dim: tenant_id binding lift (CP spec v1.22) + persona_tier plumbing arc (PRs #24+#25 merged at `056d651` 2026-05-28). All 3 dimensions operational at runtime. | OD-3+OD-4 persona_tier plumbing arc this session + AS-1 RETIRED at 2026-05-20 |
| 4. CP spec C-CP-12 §12.4 per-class override surface | `workflow_driver.py:804` cite "MVP defaults per C-CP-12 §12.4 + Spec_Control_Plane_v1_6.md §25.2.1" at workflow driver composition. | empirical grep this session |
| 5. CP spec C-CP-12 §12.5 audit-ledger discipline at sub-agent dispatch | `types.py:766` `dispatch_response_hash` docstring "`response_hash = sha256(canonicalize(SubAgentBrief))` per C-CP-12 §12.5"; `types.py:775` `compose_dispatch_audit` docstring "Compose the C-CP-12 §12.5 sub-agent-dispatch audit-ledger entry"; `handoff.py:220` `emit_sub_agent_dispatch_audit` invocation; `sub_agent_dispatch.py:454` audit composition at production at `RuntimeSubAgentDispatcher.dispatch`. | empirical grep this session |
| 6. Pre-batch-40 ledger v2 gate text staleness | Ledger v2 line 115 gate text: "`SandboxDispatchTable` materialized at bootstrap; `workflow_driver.py` does not invoke sub-agent dispatch / sandbox-tier branching. No `sandbox.*` runtime emission" — claims #2 + #3 STALE: (i) workflow_driver DOES invoke sub-agent dispatch via U-RT-59 cluster landing → CP-14 batch-29 close; (ii) sandbox.* DOES emit via AS-4 batch-19 close at `_emit_sandbox_violation`. Claim #1 (SandboxDispatchTable observed at bootstrap) is positive observation; SandboxDispatchTable is AS-09 substrate (`U-RT-16 — Sandbox-tier dispatch binding`), NOT C-CP-12 substrate — bundled into ledger gate-text observationally. | ledger v2 §3 row CP-12 vs production at HEAD |
| 7. H_E substitution surface — Claude Code permission modes | Per Meta-Arch §5.4 row 12 H_E classification: "~ partial (H_E covers subset) — `permission modes ≠ sandbox-tier dispatch` (Claude Code permission modes are a coarse UX surface)". Permission-mode coarse default-downgrade ≠ H_T's typed 4-row blast-radius table + max() gate-level formula + 3-dim monotonic-ascent enforcement. At H_T workflow runtime, permission-mode surface is NOT invoked at sub-agent dispatch path — H_T primitives at `handoff_registry.dispatch` + `sub_agent_gate_level_descent.dispatch_sub_agent` displace the H_E coarse approximation. Permission-mode remains an H_E UX surface for interactive Claude Code session, NOT the H_T workflow execution substrate. | Meta-Arch §5.4 row 12 |

**Discriminator outcome:** All 5 §12.1-§12.5 contract surfaces invoked at production runtime via U-RT-59 sub-agent dispatch composer chain; production cites C-CP-12 §N.M by section ID at 5+ invocation sites (handoff.py:136+159+220 + types.py:742+766+775 + workflow_driver.py:174+804 + fallback_chain.py:24+146 + sub_agent_dispatch.py:454). H_E permission-mode coarse surface displaced at H_T workflow execution. Authority anchor for criterion A is the docstring cite chain at production code, NOT a v1.6 MVP carve-out (distinct from CP-11 batch-30 + CP-14 batch-29 sub-species 7 closures which required §14.7.2 step 5 line 2546 explicit ratification path).

**Disposition: STILL-BOUNDED → RETIRED via substantive substitution-retirement.** U-RT-59 overlooked-sibling close pattern: U-RT-59 cluster landing operationalized CP-14 (multi-agent span hierarchy) + CP-12 (sub-agent privilege inheritance) jointly; CP-14 retired at batch-29; CP-12 retired here at batch-40 via the same composer chain. Per X-AL-2 retirement criterion: (cited unit IDs landed: U-CP-30 + U-CP-31 + U-CP-32 + U-RT-59 chain LANDED end-to-end at handoff.py + sub_agent_gate_level_descent + default_downgrade_rule + sub_agent_dispatch composer) ∧ (substituted H_E surface no longer invoked at substitution site: H_E permission-mode coarse surface displaced at H_T workflow execution per Meta-Arch §5.4 row 12).

Operator-ratified routing (α) at AskUserQuestion 2026-05-28 over (β) PARTIAL (SandboxDispatchTable bundled gate-text artifact) + (γ) keep STILL-BOUNDED + further audit + (δ) Class 1 fork ledger gate-text amendment.

---

## §1 Criterion verification

- **Criterion A** (cited unit IDs landed). MET — production invocation chain landed at U-RT-59 cluster + U-CP-30/31/32 + U-CP-29 (default-downgrade rule):
  - §12.1: `DEFAULT_DOWNGRADE_RULE` + `compute_child_blast_radius_ceiling` at `harness-cp/.../default_downgrade_rule.py`; consumed at `fallback_chain.py:146` + `handoff.py:136`
  - §12.2: `dispatch_sub_agent` + `assert_ascent` at `harness-cp/.../sub_agent_gate_level_descent.py` + `harness-runtime/.../lifecycle/handoff.py:159`; `_max_gate_level_descent` at `harness-runtime/.../types.py:742`
  - §12.3: 3-dim monotonic-ascent enforcement composed from §12.2 (gate_level) + AS-1 RETIRED (sandbox_tier at `handoff.py:174`) + persona_tier plumbing arc PRs #24+#25 (`056d651`)
  - §12.4: MVP defaults binding at `workflow_driver.py:804`
  - §12.5: `dispatch_response_hash` + `compose_dispatch_audit` + `emit_sub_agent_dispatch_audit` at `types.py:766+775` + `handoff.py:220` + `sub_agent_dispatch.py:454`

- **Criterion B** (substituted H_E surface no longer invoked at substitution site). MET. Per Meta-Arch §5.4 row 12: H_E permission-mode coarse surface ≠ H_T's typed 4-row blast-radius table + max() gate-level formula + 3-dim monotonic-ascent enforcement; at H_T workflow runtime, sub-agent dispatch goes through `handoff_registry.dispatch` → `sub_agent_gate_level_descent.dispatch_sub_agent` (all H_T primitives); H_E permission-mode surface not invoked at H_T workflow execution path. Permission-mode remains an H_E UX surface for the interactive Claude Code session, NOT the H_T workflow execution substrate.

**Adjacent residual (NOT a CP-12 gate):** SandboxDispatchTable (AS-09 / U-RT-16 substrate at `harness-runtime/.../lifecycle/sandbox_dispatch.py`) has ZERO consumers outside its own module + bootstrap wiring at `stage_2_as.py:71` + `mutable_context.py:60+126+187+369` + `types.py:174+571+1380`. SandboxDispatchTable is a `SandboxTier → SandboxProviderClass` reverse lookup table per C-AS-09 §9.2 (NOT a C-CP-12 primitive); was bundled observationally into the ledger v2 gate-text. Substrate-pre-landed-consumer-deferred residual remains at AS-09 row (orthogonal to CP-12 retirement); separate audit candidate at next-arc AS-axis sweep.

---

## §2 Sub-row substitution-status table

Pre-batch-40 CP-axis bucket (post-batch-30):

| Substitution | Status | Source |
|---|---|---|
| H_T-CP-12 (sub-agent privilege inheritance + monotonic-only descent) | **STILL-BOUNDED → RETIRED at this batch (batch-40)** | C-CP-12 §12.1-§12.5 ALL invoked at production via U-RT-59 chain; production cites C-CP-12 §N.M by ID at 5+ invocation sites; H_E permission-mode displaced |
| H_T-CP-23 (bridging-arc traversal composition F1+D1+D4) | STILL-BOUNDED | Substrate U-CP-53 `t_perm_3_composition.py` LANDED; ZERO production callers; pattern is `substrate-pre-landed-consumer-deferred` (NOT sub-species 10); no explicit runtime spec §14.7 MVP carve-out cite parallel to CP-11/CP-14 — deferred at batch-39 audit per advisor pre-substantive consultation; remains STILL-BOUNDED at batch-40 |
| H_T-CP-8 | PARTIAL (preserved) | F2-substrate-join — 1 of 17 edges wired; Phase 6 CP plan revision-pass required |
| H_T-CP-9 | PARTIAL (preserved) | ResumptionKind 5-class driver emits binary only per CP spec v1.23 §25.5 v1.4 scope carve-out |
| H_T-CP-17 | PARTIAL (preserved) | files.* CP-side consumer; Files arc deferred indefinitely per runtime spec v1.17 §14.C |
| 17 prior RETIRED rows | RETIRED (preserved verbatim) | per row-history at batch-30 close |

Post-batch-40 CP-axis bucket: **18 RETIRED + 0 RETIRE-READY + 3 PARTIAL + 1 STILL-BOUNDED (CP-23 only) + 0 STILL-BOUNDED-INDEFINITELY = 22 ✓**.

**CP-axis pipeline-advanced: 21/22 = 95.5%** (+4.6 pp from 20/22 = 90.9% pre-batch-40 via within-tier promotion CP-12 PARTIAL→ RETIRED + cross-tier promotion STILL-BOUNDED → RETIRED). CP-axis crosses **81.8% RETIRED** (third axis above 80% RETIRED). CP-23 remains the sole STILL-BOUNDED — substrate-pre-landed-consumer-deferred at U-CP-53; closure requires either explicit runtime spec §14.7 MVP carve-out OR substantive runtime composer landing.

Workspace-layer cumulative post-batch-40: **41/54 RETIRED (75.9%) + 2/54 RETIRE-READY (3.7%) + 3/54 PARTIAL (5.6%) + 6/54 STILL-BOUNDED (11.1%) + 2/54 STILL-BOUNDED-INDEFINITELY (3.7%)**. Pipeline-advanced (R+RR+P): **46/54 = 85.2%** (+1.9 percentage points from batch-39).

---

## §3 Adjacent observations

(a) **U-RT-59 overlooked-sibling close pattern catalogued.** U-RT-59 sub-agent dispatch composer cluster landing operationalized THREE CP-axis substitutions jointly at production runtime: CP-14 (multi-agent span hierarchy — closed at batch-29 via v1.6 MVP single-sub-agent slice ratification) + CP-11 (D4 multiplicative tunable — closed at batch-30 via sibling-arc cascade_policy carve-out) + CP-12 (sub-agent privilege inheritance + monotonic-only descent — closed at batch-40 via substantive substitution-retirement under THIS batch). All 3 transit STILL-BOUNDED/PARTIAL → RETIRED via the SAME U-RT-59 substrate-landing arc; CP-12 differs from CP-11/CP-14 by NOT requiring a v1.6 MVP carve-out cite (CP-12 contract is FULLY met at production, not narrowly scoped). Pattern catalogued: when a multi-row cluster landing operationalizes substrate spanning multiple ledger rows, retirement-audit should sweep ALL affected rows post-landing (not just the primary cluster owner). At U-RT-59 landing 2026-05-20, only CP-14 was reviewed; CP-11 + CP-12 closures landed 8 days later via post-hoc audit. Workflow doc revision candidate at §7.4.7.2 species or §7.4.7.3 audit-template strengthening.

(b) **CP-axis crosses 81.8% RETIRED — third axis above 80% RETIRED.** AS-axis at 81.8% (8/11 RETIRED + 2/11 STILL-BOUNDED-INDEFINITELY = active 8/9 RETIRED + 1/9 RETIRE-READY = 100% active pipeline-advanced); OD-axis at 62.5% RETIRED (5/8) + 100% pipeline-advanced (8/8); IS-axis at 88.9% RETIRED (8/9) + 88.9% pipeline-advanced; CP-axis crosses 81.8% RETIRED (18/22) + 95.5% pipeline-advanced (21/22) at batch-40. Workspace pipeline-advanced 85.2% reflects 4-axis convergence on terminal closure pre-deployment.

(c) **CP-23 remains sole CP-axis STILL-BOUNDED.** Substrate U-CP-53 `t_perm_3_composition.py` LANDED with ZERO production callers; pattern is `substrate-pre-landed-consumer-deferred` (distinct from sub-species 10); closure requires either (α) operator AskUserQuestion ratifying explicit v1.6 MVP scope-extension covering bridging-arc (advisor flagged X-AL-3 risk pre-substantive at batch-39 — would be silent extension via AskUserQuestion route); OR (β) substantive runtime composer landing invoking U-CP-53. NOT patched per FM-2 single-focus arc at batch-40; precedent rigor from batch-39 §3(e) preserved.

(d) **SandboxDispatchTable AS-09 residual surfaced as orthogonal observation.** Per empirical grep this session: SandboxDispatchTable (`harness-runtime/.../lifecycle/sandbox_dispatch.py`) is C-AS-09 §9.2 substrate (NOT C-CP-12) per its own docstring "U-RT-16 — Sandbox-tier dispatch binding ... AS shipped the primitive functions ... but no dispatch-table type"; ZERO consumers outside its own module + bootstrap wiring + types.py declaration. Substrate-pre-landed-consumer-deferred residual at AS-09 row (orthogonal to CP-12 retirement); separate audit candidate at next-arc AS-axis sweep against ledger v2 row AS-09 (if any).

(e) **34th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]`.** Advisor at arc opening: (1) flagged SandboxDispatchTable consumer-check as decisive between substantive-retirement (if CP-12 contract met without ST consumer) vs partial-retirement-is-non-retirement (if ST is a CP-12 gate); (2) confirmed §12.1-§12.5 invocation chain via docstring cite chain at handoff.py + types.py + workflow_driver.py is substantively-retired-shape (not sub-species 10); (3) recommended AskUserQuestion route + checkpoint hand-off. Empirical orientation discriminated cleanly: SandboxDispatchTable is AS-09 substrate (NOT CP-12); ZERO consumers confirms substrate-pre-landed-consumer-deferred at AS-09 row but ORTHOGONAL to CP-12 gate. Discipline pattern validation: pre-substantive advisor consultation enabled clean substantive-retirement classification vs PARTIAL classification confusion.

(f) **ZERO cross-axis cascade.** Intra-CP-axis doc-hygiene only. NO CP spec / CP plan / OD spec / AS spec / runtime spec / CXA / ADR / ADD / PRD amendment. NO production code change. NO test addition. NO carrier change. NO Meta-Arch refresh (Meta-Arch §5.4 row 12 H_E classification "permission modes ≠ sandbox-tier dispatch" already accurate; ZERO Meta-Arch row vocab drift surfaced this audit).

(g) **Workspace-wide retirement velocity catalogue.** Single calendar day 2026-05-28 closures: batch-37 OD-1 + batch-38 OD-7 + batch-39 IS-4 + batch-40 CP-12 = 4 STILL-BOUNDED → RETIRED transits + 2 RETIRE-READY → RETIRED transits (OD-3 batch-36; not at this batch) + 1 STILL-BOUNDED → PARTIAL transit (OD-3 batch-34; not at this batch) + 1 STILL-BOUNDED → PARTIAL transit (OD-4 batch-35; not at this batch) = ~8 ledger transits in single day across 4 axes. Workspace transitions from 38/54 RETIRED at batch-36 close to 41/54 RETIRED at batch-40 close (+3 RETIRED in single calendar day). Pattern enabled by: (1) sub-species 10 audit catalogue; (2) advisor pre-substantive discipline; (3) operator AskUserQuestion ratification discipline; (4) U-RT-59 overlooked-sibling close pattern catalogued at this batch.

(h) **Audit footprint at this arc: ~10 file reads + 8 grep operations + 2 advisor calls + 1 AskUserQuestion = ~10 minutes wall-clock to discriminate substantive retirement from PARTIAL bundling artifact.** Compared with substantive runtime composer arc estimates, U-RT-59 overlooked-sibling close pattern delivers ~10-100x leverage when applicable (substrate already landed at prior cluster; production already invokes; only doc-hygiene reclassification needed).

---

## §4 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/phase-7d-retirement-events-batch-40.md` |
| Filed at | 2026-05-28 |
| Phase | Phase 7 sub-phase 7d — substitution retirement |
| Predecessor batch | batch-39 (H_T-IS-4 STILL-BOUNDED → RETIRED-AS-AUTHORING-ONLY) |
| Co-published artifacts | `harness-cp/CLAUDE.md` §4.1 CP-12 row transit + cumulative-counts line refresh + memory entries |
| Cross-axis cascade | ZERO (intra-CP-axis doc-hygiene only) |
| Production code change | ZERO |
| Test addition | ZERO |
| Spec / plan amendment | ZERO (CP spec preserved verbatim; ADR-D4 preserved verbatim; Meta-Arch §5.4 row 12 preserved verbatim — no vocab drift surfaced at CP-12 audit) |
| Advisor application count this arc | 34th — pre-substantive SandboxDispatchTable-consumer-check discrimination + substantive-retirement vs PARTIAL bundling-artifact distinction |
