# Adversarial Review — R-FS-1 B2-plan (multi-server MCP + gate-axis atomic-unit decomposition)

## Summary

- **Mode:** Phase-7 pre-implementation review (red-team an axis's plan corpus for the atomic units about to land). Per `harness-adversarial-reviewer` SKILL.md + root `CLAUDE.md` §10.9 standing posture.
- **Artifacts reviewed:**
  - `.harness/r-fs-1-b2-plan-decomposition.md` (companion summary)
  - `design-substrate/Implementation_Plan_Control_Plane_v2_36.md` (delta over v2.35; +1 unit U-CP-98)
  - `design-substrate/Implementation_Plan_Harness_Runtime_v2_47.md` (delta over v2.46; +7 units U-RT-125..131)
  - clearance markers + pointer bumps (root `CLAUDE.md` §2.4, `.harness/claude-artifact-pointers.md` §2.4, fork `class_1_fork_b2_spec_2_gate_axis_materialization.md` §4)
- **Date:** 2026-06-16
- **Finding count by class (§4.1 review-severity scale):** Class 3 (severe): 0 · Class 2 (moderate): 1 · Class 1 (minor): 3
- **Highest-severity finding:** F2-01 — the co-land pin is **necessary but INCOMPLETE**: the composer gates inference + sub-agent steps too (not only `TOOL_STEP`s), and the plan/spec do not specify the `mcp_trust_tier` value the composer feeds when there is **no resolved MCP host**. If U-RT-131 fixes only the tool-step branch and the non-tool path keeps `LEVEL_0_REFUSE_REMOTE`, then **U-CP-98 ⊕ U-RT-131 together still DENY-floor every inference/sub-agent gate**.
- **Disposition recommendation:** **APPROVE-WITH-FINDINGS.** The decomposition is structurally sound, delta-only-clean, X-AL-3-clean, and the central co-land-pin HAZARD analysis is empirically correct and load-bearing. F2-01 (confirmed by execution-path read — production inference/sub-agent steps DO traverse to the L0 construction site) requires a **tightening of the U-RT-131 AC in the plan now** (the Class-2 current-phase revision): the AC must specify the non-MCP-step default `mcp_trust_tier` as the no-floor / `AUTO`-contributing tier (e.g. `LEVEL_3_ALLOW_WITH_AUDIT`), plus an inference-step contrasting-baseline that does NOT become DENY after U-CP-98. This is a **plan-AC tightening, not a fork** (the spec §19.1.2 floor table is cleared; the gap is the producer's non-tool default, which is plan/impl-layer, not a spec-contract defect). The three Class-1 items are inline fixes.

---

## Load-bearing co-land-pin verification (the highest-value check)

**What I verified by direct read at HEAD (not from the plan's self-description):**

1. **`gate_level()` composes exactly 3 axes today** — `gate_level_rule.py:214-218` builds `per_axis_floors = {PER_TOOL_GATE_LEVEL, BLAST_RADIUS, PERSONA_TIER}`. `Axis.MCP_TRUST` is NOT in the dict. `mcp_trust_tier` is a declared-but-unconsumed field (`gate_level_rule.py:104`). ✓ matches the plan.
2. **The gate is `max()` over escalation rank** `AUTO(0) < ASK(1) < DENY(2)` — `gate_level_rule.py:63-76` (`_GateRank`) + `:219-221` (`max()` by `_RANK`). ✓ A floor can only RAISE the composed gate.
3. **The composer pins `mcp_trust_tier=MCPTrustTier.LEVEL_0_REFUSE_REMOTE`** — `hitl_gate_composer.py:462`, inside a real `gate_level(GateLevelInput(...))` call at `:457`. ✓
4. **Table A maps L0→DENY** — CP spec v1.35 §19.1.2 (`Spec_Control_Plane_v1_35.md:33`): `MCPTrustTier.LEVEL_0_REFUSE_REMOTE: GateLevel.DENY` (L1→ASK, L2→ASK, L3→AUTO at `:34-36`). ✓
5. **The production call site is LIVE (not test-only).** The `:462` `GateLevelInput` is constructed inside `_compute_gate_decision` (`hitl_gate_composer.py:409`), called at `:1150` inside `RuntimeHITLGateComposer.dispatch` (class at `:659`, `async def dispatch` at `:1034`). `RuntimeHITLGateComposer` is constructed in production at `stage_5_loop_init.py:337` (`hitl_inference`) + `:431` (`hitl_sub_agent`) and bound into the bootstrap loop. **The hazard fires in production, not just in tests.** ✓
6. **`RT-FAIL-MCP-TOOL-NAME-COLLISION` is CLEARED at runtime spec v1.51** — `Spec_Harness_Runtime_v1.md:4046` (fail-class row) + `:4049` (routing-index-total invariant) + `:13` (change-note). The plan is NOT inventing it. X-AL-3-clean. ✓
7. **The `_trust_tier_from_level` stub IS constant-collapsing** — `mcp_client_host_factory.py:184-197`: `_ = level; return MCPTrustTier.LEVEL_0_REFUSE_REMOTE` regardless of input. Confirms U-RT-129's "retire the constant-collapse stub" framing. ✓
8. **All cited carrier line numbers resolve** — `mcp_client_host_factory.py:173` (`config.mcp_clients[0]`), `:178/:197` (stub), `runtime_tool_dispatcher_factory.py:269/:281` (`config.mcp_clients[0]`), `mutable_context.py:212` + `types.py:1837` (`mcp_client_host` field). ✓ No phantom cites. `test_cxa_pattern_p1.py` exists at `harness-runtime/tests/integration/`. ✓

**Verdict on the HAZARD direction (U-CP-98-alone → harm):** **CORRECT.** Composing `Axis.MCP_TRUST: MCP_TRUST_GATE_LEVEL_FLOOR[L0]=DENY` into the `max()` while the composer still pins L0 forces every gate-evaluated step through the composer to `DENY`. The plan's analysis is byte-grounded and right.

**Verdict on the REMEDY direction (U-CP-98 ⊕ U-RT-131 → correct):** **INCOMPLETE — see F2-01.** The plan's harm analysis and U-RT-131's scope/AC speak ONLY of the `TOOL_STEP` case ("a `TOOL_STEP` routed to an L0 server forces `DENY`... for the host resolved via the routing index" — `Implementation_Plan_Harness_Runtime_v2_47.md:423/:433`). But `RuntimeHITLGateComposer.dispatch` (`:1034`) is **generic over `binding`/`step`** — it gates ANY step with a matching HITL placement (`:1077-1101`), including inference and sub-agent steps (the two production composer instances at `stage_5_loop_init.py:337/:431`). For a non-tool step there is **no `tool_id`, no routing-index hit, no resolved owning host** — so "the resolved host's trust" is undefined. The spec §14.8.2 step-4c formula (`Spec_Harness_Runtime_v1.md:3447`) is generic with no non-tool carve-out, and CP §19.1.2 Producer ¶ (`Spec_Control_Plane_v1_35.md:56`) only covers the tool-step host-resolution path. **Nothing in the plan or the cleared specs specifies the non-MCP-step `mcp_trust_tier` default.** If U-RT-131 leaves the non-tool branch at the L0 constant (the path of least resistance — the implementer "replaces `:462`" for the resolved-host case but the same `GateLevelInput` is constructed for ALL steps), then U-CP-98 ⊕ U-RT-131 still puts `DENY` into the `max()` for every inference/sub-agent gate. The co-land pin neutralizes the tool-step path but not the broader gate.

**Verdict on the ENCODING (co-land pin vs DAG edge):** **CORRECT conclusion, soft stated rationale (F1-01).** Co-land is the right encoding, but for the reason the plan states secondarily, not primarily: a `U-CP-98 → U-RT-131` DAG edge *would* express the safe ordering — it is forbidden only because it is a **CP→RT cross-axis dependency** (axis-isolation, `harness-cp` must not import `harness-runtime`). The plan leads with the weaker "the constraint is the reverse of a dependency" argument; the load-bearing reason is the forbidden CP→RT direction (which the plan does name at `Implementation_Plan_Control_Plane_v2_36.md` §3.7 / runtime `:490`). Conclusion stands.

**Verdict on "U-RT-131-alone is harmless":** **CORRECT.** U-RT-131 sets an accurate `mcp_trust_tier` that `gate_level()` still ignores (3-axis composition until U-CP-98) → no behavior change. Permitted-but-pointless alone. ✓

---

## Class 2 findings (moderate — current-phase plan-AC revision)

### F2-01 — Co-land pin neutralizes only the TOOL_STEP path; the non-MCP-step gate default is unspecified
- **Location:** `Implementation_Plan_Harness_Runtime_v2_47.md:423` (U-RT-131 Scope), `:433` (U-RT-131 AC), `:595` (§6 finding #1); `.harness/r-fs-1-b2-plan-decomposition.md` §5; CP plan v2.36 §3.7.3 (the cited full analysis). Code: `hitl_gate_composer.py:462` (the L0 constant) reached from `:1150`/`:1034` for ALL gated steps; `stage_5_loop_init.py:337` (`hitl_inference`) + `:431` (`hitl_sub_agent`) — the two non-tool composer instances.
- **Defect:** The composer gates inference and sub-agent steps via the same `dispatch` → `_compute_gate_decision` → `GateLevelInput(mcp_trust_tier=LEVEL_0_REFUSE_REMOTE)` path as tool steps. U-RT-131's scope/AC address only the `TOOL_STEP` resolved-host case. The plan's harm analysis says "every MCP **tool** gate becomes DENY" — it UNDERSTATES the breadth: after U-CP-98, `MCP_TRUST_FLOOR[L0]=DENY` floors **every** gated step (inference + sub-agent included), none of which has a resolved MCP host. Neither the plan nor the cleared specs (CP §19.1.2 Producer ¶; runtime §14.8.2 step-4c) specify what `mcp_trust_tier` the composer feeds for a no-host step. If the non-tool branch keeps L0, U-CP-98 ⊕ U-RT-131 **still** DENY-floors every inference/sub-agent gate — the co-land pin is then insufficient, not merely the harm-description imprecise.
- **Discriminator that classifies as Class 2:** (a) — affects substantive content of the current-phase artifact (the U-RT-131 AC must state the non-MCP-step default). It does NOT require upstream spec revision: the §19.1.2 floor table is cleared and unchanged; the "no-host → AUTO-contributing tier" choice is a producer-side default, which is a plan/impl-layer concern (the spec already delegates the `GateLevelInput` carrier-shape + composer producer to B2/B3-plan per `Spec_Control_Plane_v1_35.md:56` "the resolved-host read + the constant replacement are B2-impl conformance"). So discriminator (b)/(c) do not fire → Class 2, not Class 3.
- **Evidence (traversal-to-harm-site CONFIRMED by execution-path read, not asserted):** The two short-circuits between `dispatch` and the `:462` construction were both checked and do NOT fire for production non-tool steps:
  - The placement filter (`:1078`/`:1084`) only short-circuits steps with no matching placement; `hitl_inference` is `applicable_placements={PRE_ACTION}` (`stage_5_loop_init.py:339`) and `hitl_sub_agent` is `{SUB_AGENT_BOUNDARY}` (`:433`) — inference/sub-agent steps with those placements pass through.
  - The binding-completeness guard `_compute_gate_decision:448` (returns `None` if `persona_tier is None` OR `blast_radius_tier` isn't a `BlastRadiusTier`) is SATISFIED for production non-tool steps: (i) `resolve_step_blast_radius` (`step_blast_radius.py:111-139`) returns a **concrete `BlastRadiusTier` for every step kind** — `READ_ONLY` for read-only/inference kinds (`:119`), the `compute_child_blast_radius_ceiling(...)`→`READ_ONLY` for `SUB_AGENT_DISPATCH` (`:128`) — never `None`; both composers are constructed WITH `blast_radius_resolver=make_step_blast_radius_resolver(ctx)` (`stage_5_loop_init.py:334/:351/:445`); (ii) `persona_tier` is a required field on `StepEffectiveBinding` post-CP-v1.17 (`hitl_gate_composer.py:486`), so production bindings carry it. The `:448` guard only short-circuits test-fixture/partial bindings, NOT production. **Therefore a production inference/sub-agent step reaches `:457-462` and constructs `GateLevelInput(mcp_trust_tier=LEVEL_0_REFUSE_REMOTE)`** — the single construction site shared by all step kinds. After U-CP-98, `MCP_TRUST_FLOOR[L0]=DENY` enters the `max()` for that gate.
  - Supporting: `Spec_Harness_Runtime_v1.md:3447` (the step-4c `gate_level = max(...per_mcp_server_trust_floor(server)...)` formula is generic — no non-tool carve-out); `Implementation_Plan_Harness_Runtime_v2_47.md:433` (the AC scopes to "a `TOOL_STEP` routed to an L0 server... for the host resolved via the routing index").
- **Resolution path (shape only):** Tighten the **U-RT-131 AC in the plan now** (this is the Class-2 current-phase revision of the artifact under review — NOT a deferral to impl execution). The AC must specify the `mcp_trust_tier` value the composer feeds when there is no resolved MCP host (inference/sub-agent steps, and tool steps with no MCP routing) — it must map to a tier whose floor contributes nothing to the `max()` (the highest-trust / `AUTO`-floor sentinel) so the gate falls through to blast/persona/per-tool. Add a contrasting-baseline AC for the co-land arc that an **inference** step (no MCP host) does NOT become DENY after U-CP-98. Verify by execution (run an inference-step gate through the 4-axis composition), not by grep. Decision label: **decided** (the execution path is confirmed; the only judgment is the default's value, which the floor-only/monotone invariant at §19.1.2 dictates must be the no-floor tier).

---

## Class 1 findings (minor — documentation drift)

### F1-01 — "NOT expressible as a DAG edge" leads with the weaker rationale
- **Location:** `.harness/r-fs-1-b2-plan-decomposition.md:91` (§4); `Implementation_Plan_Harness_Runtime_v2_47.md:431/:490`; CP plan v2.36 §3.7.
- **Defect:** The plan's primary justification for co-land-vs-DAG-edge is "the constraint is the reverse of a normal dependency, so a DAG edge cannot express it." A `U-CP-98 → U-RT-131` dependency edge *would* express the safe ordering (U-RT-131 lands before U-CP-98 is permitted). The load-bearing reason co-land is correct is that such an edge is a **CP→RT cross-axis dependency, forbidden by axis-isolation** (`harness-cp` cannot import `harness-runtime`). The plan does name this ("CP→RT is the forbidden direction") but secondarily.
- **Resolution:** Re-order the rationale to lead with the forbidden-CP→RT-direction argument. Inline fix; the conclusion (co-land is the right encoding) is unaffected.

### F1-02 — `five_axis_composition.py` omitted from the §5 `gate_level()` consumer enumeration
- **Location:** `.harness/r-fs-1-b2-plan-decomposition.md:107` (§5 names only `hitl_gate_composer.py:457` + `test_cxa_pattern_p1.py` as consumers). Code: `harness-cp/src/harness_cp/five_axis_composition.py:98-118` (`compose_five_axis` calls `gate_level()` at `:111`).
- **Defect:** `compose_five_axis` is a SECOND `gate_level()` consumer not enumerated in the harm analysis. It is currently **benign**: it has NO production caller (only `harness-cp/tests/test_five_axis_composition.py`), it passes `mcp_trust_tier` through from its input (not a hardcoded L0), and the test fixture supplies `LEVEL_2_SANDBOX_ALL`→ASK (not L0) with value-agnostic asserts (`result.gate_level is not None`). So U-CP-98-alone does NOT break it today. But the §5 enumeration claims to inventory the consumers and silently omits it; a future production wiring of `compose_five_axis` or an L0 fixture change would reintroduce exposure that the plan's analysis doesn't cover.
- **Resolution:** Add `five_axis_composition.py` to the §5 consumer list with a one-line "currently test-only, L2 fixture, value-agnostic asserts → benign" note. Documentation completeness; not a behavior change.

### F1-03 — Plan unit-count phrasing ("3-of-4 / 4-of-4") vs adjacent "5-axis" surfaces invites confusion
- **Location:** `.harness/r-fs-1-b2-plan-decomposition.md:65` (O-CP-3 completeness honesty); CP plan v2.36 / runtime v2.47 "4-of-4". Adjacent: `gate_level_rule.py` docstrings + `five_axis_composition.py` (§19.3 "5-axis") + runtime spec v1.51 change-note "3 of 5 axes" (`Spec_Harness_Runtime_v1.md:20`).
- **Defect:** The plan correctly uses "§19.1 4-axis" (the HITL gate `max()`: per_tool + blast + persona + mcp_trust). But sibling surfaces speak of "5-axis" (§19.3 D2-layer: adds the orthogonal `sandbox_tier`) and the runtime spec v1.51 change-note says "3 of 5 axes." These are DIFFERENT compositions (§19.1 D5-layer HITL gate vs §19.3 D2-layer sandbox+gate orthogonal product). The plan's "3-of-4 → 4-of-4" is correct for §19.1; the drift risk is a reader conflating the two axis-counts. The O-CP-3 completeness-honesty claim (after B2, gate composes 4-of-4 §19.1 axes but `per_tool_gate_level` stays a degenerate default-AUTO axis until its O-CP-3 producer lands) is **correct** — verified against `gate_level_rule.py:95-99` (per_tool is a direct-value degenerate axis) and the registered-forward O-CP-3 disposition.
- **Resolution:** Optional inline note distinguishing the §19.1 4-axis (HITL gate) count from the §19.3 5-axis (sandbox-orthogonal) count where the plan first uses "4-of-4." Cosmetic; the plan's own usage is internally correct.

---

## Preservation / X-AL-3 / coverage subsection

**Delta-only preservation (author claims 0 prior-body lines changed) — CONFIRMED.**
- CP plan v2.35 (661 lines) → v2.36 (740 lines), +79. Diff of removed (`<`) lines = 33 non-blank lines, ALL confined to the v2.35 change-note header + change-note tables + filing-footer rows (the new version supersedes the prior change-note, preserving it as historical record — correct delta-only behavior). **No prior unit body (U-CP-01..97) was removed or altered.** U-CP-98 present; U-CP-01..97 present.
- Runtime plan v2.46 (448) → v2.47 (614), +166. Removed lines = 31, ALL confined to the v2.46 change-note + footer. **No prior unit body (U-RT-01..124) removed or altered.** U-RT-125..131 present; U-RT-122..124 preserved.
- Verified by `diff` (presence of removed lines), then classified each removed line by section — the correct verification shape for a delta-only claim.

**X-AL-3 (anti-extension) — CLEAN.**
- The new fail-class `RT-FAIL-MCP-TOOL-NAME-COLLISION` is **cleared at runtime spec v1.51 §14.9.10/§14.9.5** (`Spec_Harness_Runtime_v1.md:4046/:4049/:13`) — the plan consumes a cleared contract, it does not invent it.
- U-CP-98 composes a floor table (`MCP_TRUST_GATE_LEVEL_FLOOR`) that is cleared at CP spec v1.35 §19.1.2; `Axis.MCP_TRUST` is already a closed `Axis` enum member (`cp_shared_types.py`). No new contract ID, no new enum member, no new primitive. Impl-against-cleared-spec.
- `ServerName` is a `NewType` over `str` (cleared at runtime v1.51 §14.9.10) — no new primitive.
- All 8 units consume cleared contracts (runtime v1.51 D1-D4 + the canonical-reading amendments; CP v1.34 §27.8 D3; CP v1.35 §19.1.2 gate axis). No silent design extension.

**Coverage completeness — BOTH spec legs covered; no silent gap.**
- B2-spec-1 reshape: D1 → U-RT-125+126; D2 → U-RT-127+128; D3 → U-RT-129 (runtime, citing CP §27.8 — correctly homed where the code lives, `_trust_tier_from_level`); D4 → U-RT-130. ✓
- B2-spec-2 gate axis: §19.1.2 floor table + composition → U-CP-98 (CP-homed, where `gate_level_rule.py` lives); Producer ¶ → U-RT-131 (runtime-homed, where `hitl_gate_composer.py` lives). Homing is correct. ✓
- Registered-forward dispositions (NOT silent gaps): O-CP-3 (`per_tool_gate_level` producer), B2-restart (D5), server-qualified addressing, B6 (per-tool sandbox), AS C-AS-10 §10.3 (already landed, consumed not re-implemented). Each carries an explicit disposition. ✓
- The reshape fork F1-03 docstring fix (`mcp_client_host.py:128-130`) bundled into U-RT-129; the gate-axis fork F3-01 docstring fix (5 `gate_level_rule.py` "spec-silent" sites) bundled into U-CP-98. ✓

**DAG / acyclicity — CONFIRMED.**
- 8 nodes (1 CP leaf U-CP-98 + 7 RT). Topological order `{U-RT-125, U-RT-129, U-CP-98}` → U-RT-126 → `{U-RT-127, U-RT-130}` → U-RT-128 → U-RT-131. Every RT edge points to a strictly-earlier node; no back-edge. ✓
- "0 cross-axis DAG edges" claim — CONFIRMED: `GateLevelInput.mcp_trust_tier` pre-exists (`gate_level_rule.py:104`); the composer's `harness_cp` import pre-exists (`hitl_gate_composer.py:439-440`). U-CP-98 is an independent CP leaf reading an existing field; U-RT-131 sets a field on an existing import. No new cross-axis carrier → no CP↔RT dependency edge → no cycle. ✓ (The co-land pin is a §5/§6 sequencing constraint, correctly NOT modeled as a DAG edge — F1-01 nuance aside.)

**Pointer / count accuracy — SANE.**
- Root `CLAUDE.md` §2.4: CP `Implementation_Plan_Control_Plane_v2_36.md`, Runtime `Implementation_Plan_Harness_Runtime_v2_47.md`. ✓
- `claude-artifact-pointers.md` §2.4: CP "99 units" (U-CP-00/00b/00c + U-CP-01..98; +1 from v2.35's 98 = U-CP-98); Runtime "129 units" (122→129, +7). Internally consistent with the +1 CP / +7 RT delta. ✓

---

## Findings considered and rejected (transparency)

1. **Co-land-pin HAZARD direction (U-CP-98-alone → DENY).** Attack: is the harm real? → **Real, verified byte-for-byte** at `gate_level_rule.py:214-221` + `hitl_gate_composer.py:462` + CP §19.1.2 Table A L0→DENY. Not a finding (the plan is correct); the breadth-understatement is captured at F2-01.
2. **Production reachability of the harm.** Attack: is `hitl_gate_composer.py:457` test-only (the §13.1 test-bypass-as-runtime-truth pattern)? → **No, live** — reached from `RuntimeHITLGateComposer.dispatch:1034`, constructed at `stage_5_loop_init.py:337/:431`. Not a finding.
3. **Forward-looking cite phantom (checklist item 3).** Attack: do `test_cxa_pattern_p1.py`, `types.py:1837`, `mcp_client_host_factory.py:178/:197`, `runtime_tool_dispatcher_factory.py:269/:281` exist at HEAD? → **All resolve.** Not a finding.
4. **Plan-revision-against-not-yet-built-substrate (checklist item 5).** Attack: do the cited carriers (`GateLevelInput.mcp_trust_tier`, the composer's `harness_cp` import, the `Axis.MCP_TRUST` enum member) exist at HEAD so the "0 cross-axis edges" claim holds? → **All pre-exist.** Not a finding.
5. **Fail-class invention / X-AL-3 (checklist item 8).** Attack: is `RT-FAIL-MCP-TOOL-NAME-COLLISION` invented by the plan or cleared? → **Cleared at runtime v1.51 §14.9.10/§14.9.5.** Not a finding.
6. **Delta-only preservation (checklist item 1/2).** Attack: did any prior unit body change? → **No** — removed lines are change-note/footer only. Not a finding.
7. **Spec-prose-vs-plan-body drift (checklist item 6).** Attack: do U-CP-98 / U-RT-129 / U-RT-131 ACs match the cleared spec bodies (CP §19.1.2 Table A; CP §27.8 identity-by-ordinal; runtime §14.9.10)? → **Match** (Table A values, identity projection, routing index). The one drift is the §19.1.2 Producer ¶ tool-step scoping vs the generic composer — captured at F2-01.
8. **Halt-route-split-AC (checklist item 9).** Attack: does any AC bundle materializable + unmaterializable atoms? → **No** — the co-land pin is correctly surfaced as a build-sequencing constraint, not a silently-absorbed unmaterializable AC; the e2e fixture (≥2 mock MCP servers) is the one genuinely-new build asset, called out.
9. **Cross-spec drift grep (posture C).** Attack: grep siblings for stale `gate_level()` 3-axis cite-shapes / §19.1.2 floor-table cite-shapes. → `gate_level_rule.py` carries 5 "MCP_TRUST 4th axis remains unmaterialized / §0.8 row 2 PARTIAL-ADVANCE / spec-silent" docstrings (`:1-34`, `:105-111`, `:138-145`, `:193-195`) that become stale at v1.35 — but the plan EXPLICITLY schedules their refresh in U-CP-98 (gate-axis fork F3-01, `decomposition.md:62`). Not a new finding (the plan owns it); confirms the plan caught the sibling-staleness.
10. **Homing correctness.** Attack: is D3 (CP §27.8 contract) wrongly CP-homed? → **No** — U-RT-129 is runtime-homed (the `_trust_tier_from_level` code lives in runtime) and cites the CP contract — the correct code-location homing precedent. U-CP-98 is CP-homed (`gate_level_rule.py`); U-RT-131 runtime-homed (`hitl_gate_composer.py`). Not a finding.
11. **O-CP-3 completeness honesty.** Attack: is "4-of-4 §19.1 axes but per_tool stays inert" correct? → **Correct** — per_tool is a degenerate direct-value axis (`gate_level_rule.py:95-99`); its producer is registered-forward O-CP-3. Captured only as cosmetic F1-03 (4-axis-vs-5-axis phrasing).

---

## Disposition

**APPROVE-WITH-FINDINGS** (per §4.1: only Class 2 + Class 1 findings → clearance with current-phase revision of the flagged AC + inline fixes; no Class 3 → no phase re-opening, no back-flow owed).

The B2-plan decomposition is well-constructed: delta-only-clean, X-AL-3-clean, correctly homed, acyclic, both spec legs covered with no silent gap, and the central co-land-pin HAZARD analysis is empirically correct and genuinely load-bearing (it prevents a "every gate DENY" production regression). The decomposition correctly identifies U-CP-98 as HARMFUL-if-alone and pins it to co-land with U-RT-131.

The one material gap (**F2-01**, confirmed by execution-path read — production inference/sub-agent steps reach the L0 construction site; the `:448` guard short-circuits only test-fixture bindings) is that the harm is BROADER than the plan states (every gated step, not only MCP tool steps) and the REMEDY (U-RT-131) as scoped fixes only the tool-step branch — leaving the non-MCP-step `mcp_trust_tier` default unspecified. **This must be closed by tightening the U-RT-131 AC in the plan now** (the artifact under review) — specify the no-resolved-host default as the no-floor/AUTO-contributing tier, and add an inference-step contrasting-baseline that does NOT become DENY. It is a current-phase plan revision, not a deferral to impl execution. Because the §19.1.2 floor table is cleared and the default is a producer-side plan/impl concern (the spec delegates the composer producer to B2-impl), F2-01 is a plan-AC tightening, **not a fork / not back-flow**. The pin remains the right shape; its AC must be widened to the full gate surface.

**§2.7.6 fork-class note:** No Phase-7 execution fork results from this review. F2-01 is a §4.1 Class-2 (current-phase plan-AC revision); it does NOT trigger a §2.7.6 Class-1 halt (no design-substrate spec/ADR revision required). The two taxonomies are not conflated here.
