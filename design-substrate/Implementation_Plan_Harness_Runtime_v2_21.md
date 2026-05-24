# Implementation Plan — Harness Runtime v2.21

## Change-note (v2.20 → v2.21)

**Scope of revision.** Spec-revision-driven plan revision absorbing runtime spec **v1.21 → v1.22** Reading B validator-composer arc landing per `.harness/reading_b_validator_composer_arc_scoping.md` (Mode-3 systems-architect recommendation filed at `f922835` in this worktree) + operator AskUserQuestion ratifications 2026-05-24 (D2 = Open Reading B NOW; D1 = Q2(c-i) absorb cite-completeness fix; spec v1.22 committed at `918f94a` in this worktree). NEW cluster **L9-duodecies** appended at §1 below, containing exactly 3 atomic units: **U-RT-90** (effective-palette computation + 4-axis `_hitl_required` consumption — pure helpers), **U-RT-91** (`ValidatorEscalationGateComposer` + post-dispatch re-entry at workflow_driver hook + foreclosure removal), **U-RT-92** (e2e VALIDATOR_ESCALATION cycle test through `harness_runtime.api.run(...)` production bootstrap). The cluster operationalizes spec v1.22 §14.8.2 step 3 / 4c / 4d consumption + NEW §14.15 C-RT-25 ValidatorEscalationGateComposer mid-step re-entry path. Reading B is the third absorption of the validator-composer arc surfaced at fork doc `.harness/class_1_fork_validator_composer_arc_stage_4_absence.md` — Reading A landed at v2.17 L9-decies (CP-21 RETIRED at batch-17); Reading B lands at v2.21 L9-duodecies (no retirement gate forced — operationally unblocks validator-escalation emission path).

**Source of fix.** Operator-ratified Reading B per AskUserQuestion 2026-05-24 + scoping doc `.harness/reading_b_validator_composer_arc_scoping.md` §4 implementation-plan cluster shape (recommended NEW L9-duodecies 3-unit cluster A → B → C linear chain). Reading B scope at current canonical state materially shrunk from fork doc's 8-15-commit worst-case estimate to **3-5-commit single-axis runtime-spec-only amendment** per scoping doc §3 + §4 (all consumed canonical surfaces — C-CP-19 §19.1 + §19.4 + C-CP-21 §21.3 + C-CP-28 §25.2/§25.3/§25.4/§25.5/§25.7 — already authored at canonical heads; runtime-spec-only envelope per scoping doc §1.3).

**Plan shape preserved.** v2.20's delta (L9-undecies cluster: U-RT-87/88/89) + v2.19 delta + v2.18 delta + v2.17 substantive body all preserved verbatim — L9-decies cluster (U-RT-83/84/85) intact, L9-novies cluster (U-RT-86) intact, L9-octies cluster (U-RT-76..U-RT-82) intact, L9-septies cluster (U-RT-71..U-RT-75) intact, all prior unit bodies intact. NEW **L9-duodecies** cluster appended at §1 below containing 3 atomic units (U-RT-90 + U-RT-91 + U-RT-92). NO existing unit body change; NO AC change at any pre-v2.21 unit; NO DAG topology change at L9-undecies / L9-decies / L9-novies / L9-octies / L9-septies / earlier internal structure; ONLY a new cluster appended with within-cluster linear-chain DAG (U-RT-90 → U-RT-91 → U-RT-92) plus cluster-boundary edges to already-landed substrate (CP-axis carriers at U-CP-43/46/47/58/59/60/61 + runtime-axis L9-decies + L9-quinquies — all already at HEAD).

**Cluster naming.** "L9-duodecies" follows the existing -ies enumeration (septies/octies/novies/decies/undecies/**duodecies** = 7th/8th/9th/10th/11th/12th). Next available -ies-suffix per the v2.12+ runtime-plan-cluster convention.

**Cluster ordering.** L9-duodecies opens with U-RT-90 as L0-within-cluster (foundational pure-helper authoring; no within-cluster predecessors); U-RT-91 at L1-within-cluster (depends on U-RT-90 within-cluster + cluster-boundary deps to existing CP-axis carriers + L9-decies validator framework binding chain); U-RT-92 at L2-within-cluster (depends on U-RT-91 within-cluster — driver invocation + e2e exercises the wired composer through production bootstrap). Cluster-boundary edges declared explicitly per §7 dependency discipline.

**U-RT-60 adjacent-unit check (D4 disposition).** U-RT-60 (HITL gate composer at L9-quinquies; landed at runtime plan v2.10) is grep-verified to contain ZERO foreclosure-referencing ACs (no `VALIDATOR_ESCALATION`/`HITLPlacementForeclosed`/`RT-FAIL-HITL-PLACEMENT-FORECLOSED-AT-V19` cites in v2.10 unit body). The foreclosure was a spec-level concept introduced after U-RT-60 landed, never reflected in plan body. **No U-RT-60 AC amendment owed at v2.21** per scoping doc §6 D4 disposition. The runtime spec v1.22 §14.8 fail-class taxonomy removed `RT-FAIL-HITL-PLACEMENT-FORECLOSED-AT-V19` cleanly — no plan-side back-reference.

**Operator-discretion implementation shape (FM-2).** U-RT-92 implementer selects e2e test fixture mechanism per FM-2 no-extension discipline (mirrors U-RT-82 + U-RT-85 + U-RT-86 + U-RT-89 enumeration patterns). Options:
- **α** — Operator-supplied `ValidatorFrameworkConfig.default()` opt-in instance + concrete `ConcreteValidatorFramework` with a `Validator` returning `ValidatorOutcome.ESCALATE` for a deterministic step input + HITL surface stub capturing `proposed_response_palette`. Test fixture constructs workflow with N steps; bootstrap fires; validator-evaluation post-dispatch returns ESCALATE → §14.15 composer fires → palette assertion under 4 test cases (gate_level × cross_trust 2x2 matrix per scoping doc §2 Q2 truth table) + validator.escalation span emission verification via in-process OTel exporter. Recommended default.
- **β** — Mechanism α + additional REJECT-path test (gate response REJECT → `RT-FAIL-HITL-GATE-REJECTED`) + additional REVALIDATE-path test (validator outcome REVALIDATE → C-RT-16 retry wrapper). Broader coverage of the C-CP-28 §25.2 ValidatorOutcome 5-case enum.
- **γ** — Gate on operator-supplied env var (`VALIDATOR_ESCALATION_E2E_FIXTURE_PATH`) pointing at fixture module; test loads + exercises. Mirrors U-RT-86 mechanism-γ pattern for CI-skipping when fixture unavailable.

Recommended default per `[[advisor-before-substantive-work-for-cross-axis-blockers]]` verification: **mechanism α** (in-process deterministic ESCALATE fixture, single happy-path with 2x2 palette matrix) — sufficient for U-RT-92's AC #1-#5 verification-shape (binding chain succeeds end-to-end against real `ValidatorFramework` instance through real `harness_runtime.api.run(...)`, not via test-locals; mid-step composer fires; palette computation correct; span emission correct; ledger-append blocked until gate resolves); REJECT + REVALIDATE coverage deferred to follow-on operator-discretion arc.

**Adjacent observations (NOT this plan's authoring scope).**

(a) **U-CP-43 4-axis input-set divergence at CP plan v2.4 §0.8 carried items.** CP plan v2.4 §0.8 flags `U-CP-43`'s 4-axis `GateLevelInput` (`{persona_tier, blast_radius_tier, deployment_surface, mcp_trust_tier}`) diverges from CP spec §19.1's 4-axis `gate_level` `max()` over `{per_tool_gate_level, blast_radius_floor, per_mcp_server_trust_floor, persona_tier_floor}` — `per_tool_gate_level` axis is absent at U-CP-43; `deployment_surface_gate_level_floor` is a plan-invention. The carry persists at CP plan v2.19 (delta-only convention; no carry-resolving revision in delta chain). **Reading B authoring proceeds at v2.21 without blocker** because: (i) per spec §19.1 line 1702 "Deferred to implementation discretion" + line 1507, `per_tool_gate_level` is **workflow-manifest-sourced** ("every tool exposed to the agent declares `tier ∈ {auto, ask, deny}` in its SKILL.md frontmatter or MCP server manifest") — NOT a CP-axis carrier-function; runtime consumes `step.tool_gate_level` directly from the workflow-manifest layer (spec v1.22 §14.8 "Deferred to implementation discretion" line cites this source per scoping doc §4); (ii) U-RT-90 cluster-boundary consumes only the 3 CP-axis floors that U-CP-43 lands (`BLAST_RADIUS_GATE_LEVEL_FLOOR` + `PERSONA_TIER_GATE_LEVEL_FLOOR` — both conformed at v2.4; `MCP_TRUST_GATE_LEVEL_FLOOR` — carried-finding cardinality 4 vs spec narrative 5, runtime consumes as-landed); (iii) U-RT-90 does NOT consume `DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR` (plan-invention, no spec mapping, NOT cited at v1.22 spec amendment per spec-canonical reading discipline). The U-CP-43 carry-finding remains an open CP-plan-side disposition for separate follow-on routing; Reading B's runtime consumption does not require it.

(b) **`per_mcp_server_trust_floor` carrier cardinality drift (carried at U-CP-43 v2.4 §0.8).** The `MCP_TRUST_GATE_LEVEL_FLOOR` lookup table at U-CP-43 enumerates 4 invented tier names mapped to invented `GATE_*` values; CP spec §19.1 narratively names "C10 five-tier framework" without enumerating tier values inside §19.1. Runtime layer consumes the U-CP-43-as-landed cardinality-4 table (no FM-2 violation — consumes canonical-as-landed surface). Cardinality drift remains a CP-axis concern requiring separate operator-discretion routing (spec extension OR plan sanction per CP plan v2.4 §0.8 disposition options).

(c) **Cross-trust-state derivation at U-RT-91.** Per spec v1.22 §14.15.8 deferred-discretion: the `cross_trust_state: CrossTrustState` argument source — whether derived from `ctx.binding` snapshot at hook firing time, or from per-step `step.cross_trust_state` declaration, or from a runtime helper consulting `ctx.mcp_client_host` + `ctx.binding.persona_tier` — is implementation discretion at the U-RT-91 landing arc per FM-2. U-RT-91 AC #2 enumerates this as implementer-discretion (recommended: closure-over-ctx derivation per the spec §14.15.8 ordering — read `ctx.mcp_client_host.current_server_trust_tier` + `ctx.binding.persona_tier` + workflow `cross_family_active` flag at hook-firing time).

(d) **`validator:` action_id prefix at U-RT-91 step 7.** Per spec v1.22 §14.15.2 step 7 + adjacent-defect note: the `validator:` action_id prefix (vs `hitl:` / `dispatch:`) is recommended at v1.22; CXA v2.9 §0.3 action-id prefix enumeration refresh is owed at follow-on bookkeeping arc. U-RT-91 AC #4 enforces `validator:` prefix; CXA refresh is OUT OF SCOPE at v2.21 (separate follow-on bookkeeping arc per `phase-7-cross-axis-composition` skill).

(e) **Composition ordering for palette intersection** (U-RT-91 AC #2). Per spec v1.22 change-note adjacent-defect (ii): the composition ordering (validator-proposed palette as outer constraint vs UNION-intersection as outer constraint) is implementation discretion at U-RT-91 landing arc. Both orderings semantically equivalent for canonical-default case (`brief.proposed_response_palette = full per C-CP-16 §16.1`); both must satisfy spec-MUST "final palette ≤ both constraints" per spec §14.15.4 invariant 4. Recommended: UNION-intersection outer (gate_level × cross_trust → effective palette), then narrow by validator-proposed palette (if non-default).

**Downstream absorption owed (post-v2.21).**

(a) Workspace `CLAUDE.md` §2.4 runtime row version bump (v2.20 → v2.21); co-published at L9-duodecies cluster open arc OR follow-on retirement-event arc (whichever fires first). Unit count 90 → 93 (+3 units).

(b) Phase 7 cluster-open authorization for L9-duodecies at follow-on session per `phase-7-implementation` skill discipline. Cluster sequencing: L9-duodecies opens with U-RT-90 as the L0 entry-point; topological sort U-RT-90 → U-RT-91 → U-RT-92.

(c) No retirement gate is forced by Reading B landing per scoping doc §5 cascade analysis (CP-21 already RETIRED at batch-17 via Reading A; no other RETIRE-READY rows intersect). The Reading B arc unblocks the validator framework's escalation emission path operationally — operator-supplied validators that emit ESCALATE → HITL gate fires + operator decides per-case. If a future operator-discretion arc surfaces a Phase-7d-substitution-retirement opportunity tied to validator-escalation emission operability (e.g., an operator-opt-in pattern record at the ledger for "validator framework escalation surface operational"), the close-pattern would mirror batch-14 §6(a) + batch-17 §4 verification-shape sharpening (structural-criterion-B MET at L9-duodecies cluster landing; operationally-MET at U-RT-92 e2e exercise). No such retirement gate is currently declared at the substitution-mapping table.

(d) `Cross_Axis_Composition_Document_v2_9.md` unchanged at v2.21 — spec §14.15.6 cross-axis cascade enumeration confirms ZERO cross-axis cascade. The §14.15 composer consumes already-landed CP spec v1.13 §28 ValidatorFramework + §25.2 HITLEscalationBrief carriers + C-CP-19 §19.1/§19.4 + C-CP-21 §21.3 surfaces without new CXA edge introduction. Existing ValidatorFramework→OD edge (CXA v2.9 §2.3.7 row 6) consumes the §14.15 `validator.escalation` + `hitl.*` spans unchanged.

(e) CP spec v1.13 + OD spec v1.11 + ADR-D1 v1.2 + ADR-D5 v1.4 + ADR-D6 v1.2 unchanged at v2.21. All consumed canonical surfaces preserved verbatim at their canonical heads (scoping doc §1.2 surface inventory verified).

(f) CXA v2.9 §0.3 action-id prefix enumeration refresh per adjacent observation (d) — owed at separate follow-on bookkeeping arc per `phase-7-cross-axis-composition` skill (the `validator:` action_id prefix at U-RT-91 §14.15.2 step 7 is a new discriminator at v1.22; CXA enumeration should reflect; surfaced but NOT patched at v2.21 per FM-2).

(g) CP plan-side U-CP-43 carried-finding disposition per adjacent observation (a)+(b) — owed at separate operator-discretion routing arc per CP plan v2.4 §0.8 disposition options (spec extension OR plan sanction). Surfaced as adjacent finding at v2.21; NOT a v2.21 blocker.

---

## §1 — L9-duodecies cluster (NEW at v2.21)

### U-RT-90 — Effective-palette computation + 4-axis `_hitl_required` consumption (pure helpers)

- **Implements:** Runtime spec **v1.22** §14.8.2 step 4c (full 4-axis `_hitl_required` evaluation per C-CP-19 §19.1) + step 4d (UNION-intersection effective-palette computation per C-CP-19 §19.4 deny-row + C-CP-21 §21.3 cross-trust-boundary). Pure helper module — no I/O, no side effects, no `ctx` dependency at module level.

- **Files:**
  - `harness-runtime/src/harness_runtime/hitl/effective_palette.py` (NEW) — author `compute_effective_palette(gate_level, cross_trust_state, validator_escalation_brief) → frozenset[HITLResponse]` per spec §14.8.2 step 4d UNION-intersection truth-table + spec §14.15.4 invariant 4 "final palette ≤ both constraints".
  - `harness-runtime/src/harness_runtime/hitl/hitl_required_consumption.py` (NEW) — author `evaluate_hitl_required(persona_tier, blast_radius_tier, server_trust_tier, per_tool_gate_level) → bool` per spec §14.8.2 step 4c + C-CP-19 §19.1 4-axis multiplicative `max()` composition rule + §19.4 runtime evaluation surface (returns `True` when `gate_level ∈ {ask, deny}`).
  - `harness-runtime/tests/unit/test_effective_palette.py` (NEW) — 4-case truth-table coverage per scoping doc §2 Q2.
  - `harness-runtime/tests/unit/test_hitl_required_consumption.py` (NEW) — 4-axis composition coverage with `auto`/`ask`/`deny` outputs.

- **Signatures:**
  - `def compute_effective_palette(gate_level: GateLevel, cross_trust_state: CrossTrustState, validator_escalation_brief: HITLEscalationBrief | None) -> frozenset[HITLResponse]` — pure function; sync.
  - `def evaluate_hitl_required(persona_tier: PersonaTier, blast_radius_tier: BlastRadiusTier, server_trust_tier: McpServerTrustTier, per_tool_gate_level: GateLevel) -> bool` — pure function; sync.
  - Optional helper `def compute_gate_level(persona_tier: PersonaTier, blast_radius_tier: BlastRadiusTier, server_trust_tier: McpServerTrustTier, per_tool_gate_level: GateLevel) -> GateLevel` — pure function returning the `max()` result (consumed internally by `evaluate_hitl_required` + exposed for `compute_effective_palette` callers needing the intermediate gate-level value).

- **Depends on:** (within-cluster) (none); (cluster-boundary, CP-axis) [U-CP-43 — `BLAST_RADIUS_GATE_LEVEL_FLOOR` + `PERSONA_TIER_GATE_LEVEL_FLOOR` + `MCP_TRUST_GATE_LEVEL_FLOOR` carriers per CP plan v2.4 conformance landing; `GateLevel` 3-value enum (`auto`/`ask`/`deny`)]; [U-CP-46 — `HITLResponse` 4-class enum per C-CP-16 §16.1]; [U-CP-47 — palette restriction carriers per C-CP-21 §21.3 (verify CP-side impl exposes typed `CrossTrustState` carrier OR runtime layer composes from `ctx.binding`/`ctx.mcp_client_host` per adjacent observation (c))]; (cluster-boundary, runtime-axis) (none — pure-helper module).

- **ACs:**
  1. **`compute_effective_palette` 4-case truth-table coverage** per scoping doc §2 Q2 + spec v1.22 §14.8.2 step 4d UNION-intersection:
     - `gate_level == deny` AND cross-trust active → `frozenset({REJECT, RESPOND})`
     - `gate_level == deny` AND no cross-trust → `frozenset({REJECT, RESPOND})`
     - `gate_level == ask` AND cross-trust active → `frozenset({APPROVE, REJECT, RESPOND})` (when called at §14.15 composer entry; `validator_escalation_brief is not None`)
     - `gate_level == ask` AND no cross-trust → `frozenset({APPROVE, EDIT, REJECT, RESPOND})` (full per C-CP-16 §16.1)
     - When `gate_level == auto`: function should not be called (callers verify `_hitl_required` first); test asserts via `ValueError` raise or precondition annotation per implementer-discretion.
     - When `validator_escalation_brief.proposed_response_palette is not None and != full`: result narrows further via intersection `result ∩ brief.proposed_response_palette`.
  2. **`evaluate_hitl_required` 4-axis composition** per C-CP-19 §19.1 + §19.4: returns `True` iff `max(per_tool_gate_level, BLAST_RADIUS_GATE_LEVEL_FLOOR[blast_radius_tier], MCP_TRUST_GATE_LEVEL_FLOOR[server_trust_tier], PERSONA_TIER_GATE_LEVEL_FLOOR[persona_tier]) ∈ {ask, deny}`. Test coverage: all 3-value enum combinations across the 4 axes (sample-based coverage; not exhaustive 3^4=81; sample the boundary cases — all `auto`, all `deny`, mixed-tier cases per scoping doc §4 spec).
  3. **Pure-function guarantee**: both helpers have no I/O, no `ctx` parameter, no side effects. Test verifies idempotence (same inputs → same output) + no mutation of input arguments + no module-level state.
  4. **Pyright strict 0 errors**. Both modules + test modules pass `uv run pyright --strict harness-runtime/src/harness_runtime/hitl/effective_palette.py harness-runtime/src/harness_runtime/hitl/hitl_required_consumption.py`.
  5. **Importable**: `from harness_runtime.hitl.effective_palette import compute_effective_palette` + `from harness_runtime.hitl.hitl_required_consumption import evaluate_hitl_required` resolve without error.

### U-RT-91 — ValidatorEscalationGateComposer + post-dispatch re-entry + foreclosure removal

- **Implements:** Runtime spec **v1.22** NEW §14.15 C-RT-25 ValidatorEscalationGateComposer contract (§14.15.1 canonical signature + §14.15.2 invocation discipline 8-step body + §14.15.3 lifecycle stage placement + §14.15.4 invariants 1-6 + §14.15.5 fail-class taxonomy NEW `RT-FAIL-VALIDATOR-ESCALATION-GATE-COMPOSE` + §14.15.8 deferred-discretion) + spec **v1.22** §14.8.2 step 3 un-foreclosure (removal of `HITLPlacementForeclosedAtV19Error` raise path + `RT-FAIL-HITL-PLACEMENT-FORECLOSED-AT-V19` fail-class) + spec **v1.22** §14.8.2 step 4c full 4-axis `_hitl_required` consumption at wrap-time composer + spec **v1.22** §14.8.2 step 4d UNION-intersection palette computation at wrap-time composer.

- **Files:**
  - `harness-runtime/src/harness_runtime/hitl/validator_escalation_composer.py` (NEW) — author `async def compose_validator_escalation_gate(ctx, brief, step_action_id, cross_trust_state, gate_level) → HITLResponse` per spec §14.15.1 signature. Module parallels existing `harness-runtime/src/harness_runtime/hitl/runtime_hitl_gate_composer.py` (or equivalent existing wrap-time composer module organization).
  - `harness-runtime/src/harness_runtime/hitl/runtime_hitl_gate_composer.py` (or equivalent) — AMEND step 3 + step 4c + step 4d composer body per spec v1.22 amendments: (i) step 3 — REMOVE `HITLPlacementForeclosedAtV19Error` raise path + filter VALIDATOR_ESCALATION placements out of wrap-time `matching` set; (ii) step 4c — REPLACE `placement.requires_hitl` shortcut with `evaluate_hitl_required(...)` call from U-RT-90; (iii) step 4d — REPLACE `DEFAULT_FULL_PALETTE` unconditional with `compute_effective_palette(...)` call from U-RT-90 with `validator_escalation_brief=None` (wrap-time path).
  - `harness-runtime/src/harness_runtime/fail_classes.py` (or equivalent existing fail-class enum module) — REMOVE `RT-FAIL-HITL-PLACEMENT-FORECLOSED-AT-V19` enum member (existing) + APPEND `RT-FAIL-VALIDATOR-ESCALATION-GATE-COMPOSE` enum member per spec §14.15.5.
  - `harness-cp/src/harness_cp/workflow_driver.py` — AMEND post-dispatch hook (existing C-CP-28 §28.3.3.4 hook site at line ~668): NEW branch `if evaluation.next_action == ValidatorNextAction.ESCALATE_HITL:` invokes `compose_validator_escalation_gate(ctx, brief=evaluation.result.escalation_brief, step_action_id=..., cross_trust_state=..., gate_level=...)` + branches on returned `HITLResponse` per spec §14.15.2 step 8 + §14.15.8 deferred-discretion.
  - `harness-runtime/src/harness_runtime/hitl/escalation_prompt.py` (NEW) — author `compose_escalation_prompt(brief, palette) → str` helper per spec §14.15.8 deferred-discretion (implementation discretion at landing arc; recommended shape incorporates `brief.escalation_reason` + `brief.fail_class` + persona-tier context + palette enumeration).
  - Implementer also DELETES any existing test file that asserts on `HITLPlacementForeclosedAtV19Error` raise behavior at wrap-time step 3 (carried-over from v1.9 MVP foreclosure semantics; the raise path no longer exists at v1.22). Search via `grep -rn "HITLPlacementForeclosedAtV19Error\|RT-FAIL-HITL-PLACEMENT-FORECLOSED-AT-V19" harness-runtime/ harness-cp/`; remove or update the matching test scaffolding to assert on the v1.22 support semantics instead.

- **Signatures:**
  - `async def compose_validator_escalation_gate(ctx: HarnessContext, brief: HITLEscalationBrief, step_action_id: ActionId, cross_trust_state: CrossTrustState, gate_level: GateLevel) -> HITLResponse` per spec §14.15.1.
  - `RT-FAIL-VALIDATOR-ESCALATION-GATE-COMPOSE` — NEW fail-class enum member at runtime-local fail-class taxonomy per spec §14.15.5.
  - `def compose_escalation_prompt(brief: HITLEscalationBrief, palette: frozenset[HITLResponse]) -> str` — pure prompt-composition helper.
  - Workflow_driver hook amendment: NEW `if-branch` at C-CP-28 §28.3.3.4 hook site invoking `compose_validator_escalation_gate(...)`.

- **Depends on:** (within-cluster) [U-RT-90 — `compute_effective_palette` + `evaluate_hitl_required` pure helpers]; (cluster-boundary, CP-axis) [U-CP-58/59/60/61 — C-CP-28 ValidatorFramework body + 5-class `ValidatorOutcome` + 5-class `ValidatorFailClass` + `HITLEscalationBrief` typed payload + 5-class `ValidatorNextAction` enum at cluster 10-CP-A `16cf6d7`/`cdf83b1`/`5ca86aa`/`9b009d3` closure commits]; [U-CP-46 — `HITLResponse` 4-class enum + canonical `hitl.*` + `audit.*` namespace carriers per C-CP-20]; [U-CP-43 — gate-level enum + axis floor carriers per C-CP-19 §19.1]; (cluster-boundary, runtime-axis) [U-RT-83/84/85 — C-RT-23 stage-4 validator framework factory at L9-decies `3005643`/`d55fbd7`/`37e9d67`]; [U-RT-60 — existing C-RT-18 RuntimeHITLGateComposer wrap-time composer at L9-quinquies `e9b9c49` (partial reuse of wrap-time mechanics + AskUserQuestionSurface binding)].

- **ACs:**
  1. **`ValidatorEscalationGateComposer` fires synchronously within step** on `ValidatorEvaluation.next_action == ValidatorNextAction.ESCALATE_HITL` per C-CP-28 §25.2 mapping (both `ValidatorOutcome.ESCALATE` AND `ValidatorOutcome.OPERATOR_BURDEN_EXCEEDED` map to `ESCALATE_HITL` per the v1.10 §25.2 ratification). Workflow_driver post-dispatch hook at C-CP-28 §28.3.3.4 (line ~668 in workflow_driver.py) invokes the composer; sync await; pre-ledger-append per C-CP-28 §25.4 invariant 2.
  2. **`HITLEscalationBrief.proposed_response_palette` composed with `compute_effective_palette`** per Q2 UNION-intersection + spec §14.15.4 invariant 4. Implementation: `effective = compute_effective_palette(gate_level, cross_trust_state, brief); final = effective ∩ brief.proposed_response_palette` (when `brief.proposed_response_palette` is non-default). Cross-trust-state derivation source is implementer-discretion per adjacent observation (c) (recommended: closure-over-ctx).
  3. **`validator.escalation` span emitted** per C-CP-28 §25.5 with `step.id` (from `step_action_id`) + `validator.outcome` (`"escalate"`) + `validator.fail.class` (from `brief.fail_class`); parent-context link to subsequent `hitl.gate.evaluated` span per spec §14.15.4 invariant 5 (OTel `start_as_current_span` nesting at §14.15.2 step 2 + step 3 enforces by-construction).
  4. **C-CP-28 §25.4 invariant 4 ("ESCALATE always emits HITL gate. Escalation cannot be silently dropped.") empirically verified.** Workflow_driver post-dispatch hook has NO execution path that bypasses `compose_validator_escalation_gate(...)` invocation on ESCALATE_HITL outcome. Verified via code-review grep: `grep -n "ESCALATE_HITL" harness-cp/src/harness_cp/workflow_driver.py` returns only the composer-invocation site (no skip / continue / pass branches around ESCALATE_HITL).
  5. **`RT-FAIL-HITL-PLACEMENT-FORECLOSED-AT-V19` fail class REMOVED** from §14.8 failure-mode taxonomy enum + no raise sites in `harness-runtime/` or `harness-cp/` source trees. Verified via `grep -rn "RT-FAIL-HITL-PLACEMENT-FORECLOSED-AT-V19\|HITLPlacementForeclosedAtV19Error" harness-runtime/ harness-cp/` returns ZERO hits post-amendment.
  6. **§14.8.2 step 3 amendment**: VALIDATOR_ESCALATION placements are filtered out of wrap-time `matching` set (no longer raise foreclosure error). Wrap-time composer body at `runtime_hitl_gate_composer.py` step 3 updated per spec v1.22 amendment text.
  7. **§14.8.2 step 4c amendment**: wrap-time composer step 4c invokes `evaluate_hitl_required(persona_tier, blast_radius_tier, server_trust_tier, per_tool_gate_level)` from U-RT-90 (replacing `placement.requires_hitl` shortcut). The `per_tool_gate_level` axis input source is `step.tool_gate_level` workflow-manifest field per spec v1.22 §14.8 "Deferred to implementation discretion" + adjacent observation (a).
  8. **§14.8.2 step 4d amendment**: wrap-time composer step 4d invokes `compute_effective_palette(gate_level, cross_trust_state, validator_escalation_brief=None)` from U-RT-90 (replacing `DEFAULT_FULL_PALETTE` unconditional). The `cross_trust_state` derivation at wrap-time composer is implementer-discretion per adjacent observation (c).
  9. **`RT-FAIL-VALIDATOR-ESCALATION-GATE-COMPOSE` fail class authored** at runtime-local fail-class taxonomy per spec §14.15.5; permanent severity; raised when §14.15.2 step 7 audit-composition substep raises typed error on APPROVE/EDIT/RESPOND path; SUPPRESSED on REJECT path per spec §14.15.5 fail-class table.
  10. **Importable; pyright strict 0 errors.** `from harness_runtime.hitl.validator_escalation_composer import compose_validator_escalation_gate` resolves. Integration test exercising the composer-invocation site at workflow_driver hook passes (unit-level — full e2e is U-RT-92 scope).

### U-RT-92 — End-to-end VALIDATOR_ESCALATION cycle test through production bootstrap

- **Implements:** Runtime spec **v1.22** §14.8.2 + §14.15 C-RT-25 composer e2e exercise through `harness_runtime.api.run(...)` production bootstrap entry point. Operational-MET verification per spec §14.15.4 invariant 1-6 + verification-shape sharpening discipline catalogued at batch-16 §6 + `[[verification-shape-sharpened-grep-vs-e2e]]` ("grep-for-presence ≠ verified-working-end-to-end" — driver invocation must succeed end-to-end against a real substrate).

- **Files:**
  - `harness-runtime/tests/integration/test_u_rt_92_validator_escalation_e2e.py` (NEW — e2e integration test module). Parallel module-organization pattern to `harness-runtime/tests/integration/test_u_rt_85_validator_framework_e2e.py` + `test_u_rt_86_mcp_client_external_server_e2e.py` + `test_u_rt_89_pause_resume_e2e.py`.

- **Signatures:**
  - `async def test_validator_escalation_e2e_happy_path()` — full bootstrap via `harness_runtime.api.run(...)` with operator-supplied `RuntimeConfig(deployment_surface=LOCAL_DEV, ..., validator_framework_config=ValidatorFrameworkConfig.default())` + concrete `ConcreteValidatorFramework` containing a `Validator` that returns `ValidatorOutcome.ESCALATE` for a deterministic step input + HITL surface stub returning `HITLResponse.APPROVE`. Asserts: (i) §14.15 composer fires post-dispatch; (ii) effective palette is the UNION-intersection per 2x2 matrix case; (iii) `validator.escalation` span emitted with parent-context link to `hitl.gate.evaluated`; (iv) state-ledger entry append happens AFTER gate resolves; (v) workflow completes with `RunStatus.SUCCESS` after gate APPROVE response.
  - `async def test_validator_escalation_e2e_palette_matrix()` — parametrized test across 4 cases (gate_level × cross_trust 2x2 matrix per scoping doc §2 Q2 truth table). Each case constructs `RuntimeConfig` + workflow + validator that escalates + HITL surface stub asserting it receives the expected palette under the case's gate-level + cross-trust state.
  - `async def test_validator_escalation_e2e_opt_out_branch()` — separate test verifying opt-out shape: `RuntimeConfig(..., validator_framework_config=None)` yields `ctx.validator_framework is None`; validator-evaluation path bypassed; workflow proceeds to `RunStatus.SUCCESS` normally; backward-compatible behavior preserved per spec §14.13.5 invariant 2.
  - Test gating: all tests marked `@pytest.mark.e2e`; no `@pytest.mark.skipif(...)` at mechanism-α selection (no external dependencies); explicit pytest fixture for HarnessContext lifecycle.

- **Depends on:** (within-cluster) [U-RT-90, U-RT-91]; (cluster-boundary, runtime-axis) [U-RT-83/84/85 — C-RT-23 validator framework factory + binding chain at L9-decies]; [U-RT-60 — HITL gate composer + AskUserQuestionSurface binding at L9-quinquies]; (cluster-boundary, CP-axis) [U-CP-58/59/60/61 — C-CP-28 ValidatorFramework body at cluster 10-CP-A]; [U-CP-43/46/47 — C-CP-19/16/21 gate-level + palette + cross-trust carriers].

- **ACs:**
  1. **Validator returning `ValidatorOutcome.ESCALATE` triggers §14.15 composer mid-step**. Test fixture constructs concrete validator with deterministic outcome; bootstrap fires; validator-evaluation post-dispatch routes to ESCALATE_HITL → workflow_driver hook invokes `compose_validator_escalation_gate(...)`. Verified by HITL surface stub being called with non-None `brief`.
  2. **HITL surface receives correct UNION-intersected palette** under 4 test cases (gate_level × cross_trust 2x2 matrix per scoping doc §2 Q2 truth table). Parametrized test asserts palette equality per truth-table cell.
  3. **`validator.escalation` span emitted with correct attributes** per C-CP-28 §25.5: `step.id` + `validator.outcome` + parent-context link to `hitl.gate.evaluated`. Verified via in-process OTel exporter (`opentelemetry.sdk.trace.export.InMemorySpanExporter` or equivalent) at test fixture; assert spans collected at test teardown match expected hierarchy.
  4. **State-ledger entry append blocked until HITL gate resolves** per C-CP-28 §25.4 invariant 2 + spec §14.15.4 invariant 3. Test asserts ordering: gate-resolved span timestamp PRECEDES state-ledger-entry timestamp.
  5. **All 4 span hierarchy spans** (`validator.escalation` parent → `hitl.gate.evaluated` → `hitl.invocation.opened` → `hitl.invocation.responded` OR `hitl.invocation.timed_out`) emitted with head=1.0 sampling per C-CP-28 §25.5 + spec §14.15.4 invariant 5. Verified via OTel exporter span-list assertion.
  6. **Composer-depth parity with U-RT-82 + U-RT-85 + U-RT-86 + U-RT-89 close-pattern shape**: tests construct `HarnessContext` via the **real** `harness_runtime.api.run(...)` (or equivalent production bootstrap entry point), NOT via `_FakeCtx` or `_MutableHarnessContext` test-locals. This is the critical AC enforcing the verification-shape discipline catalogued at batch-15 §6(a) + batch-16 §6 sharpening + applied at batch-17 (U-RT-85) + batch-18 (U-RT-89); test FAILS at design-review if the test scaffolding bypasses production bootstrap.
  7. **Test cleans up fixture state at teardown** (no test artifacts persisted between runs; no zombie subprocesses; OTel exporter state reset).
  8. **Importable; pyright strict mode passes.** All test functions resolve; integration test suite (broader workspace, including U-RT-85 + U-RT-89 already-landed e2e) remains green at U-RT-92 landing arc.

---

## §2 — DAG topology delta (v2.20 → v2.21)

NEW L9-duodecies cluster appended with cluster-boundary edges to already-landed substrate (CP-axis cluster 10-CP-A closures + CP-axis L9-quinquies carriers + runtime-axis L9-decies + L9-quinquies). No edges into v2.20 units beyond cluster-boundary deps to already-landed clusters. No edges from L9-undecies / L9-decies / L9-novies / L9-octies / L9-septies into L9-duodecies (L9-duodecies is structurally terminal at v2.21 — produces the validator-escalation composer chain; no downstream unit at this plan revision consumes its output beyond U-RT-92's own e2e exercise).

Topological sort within L9-duodecies (acyclic verified — linear chain):

```
L9-duodecies (NEW at v2.21):
  L0-within-cluster: U-RT-90 (within-cluster deps: none;
                              cluster-boundary deps: U-CP-43, U-CP-46, U-CP-47)
  L1-within-cluster: U-RT-91 (within-cluster deps: U-RT-90;
                              cluster-boundary deps: U-CP-58/59/60/61, U-CP-43,
                              U-CP-46, U-RT-83/84/85, U-RT-60)
  L2-within-cluster: U-RT-92 (within-cluster deps: U-RT-90, U-RT-91;
                              cluster-boundary deps: U-RT-83/84/85, U-RT-60,
                              U-CP-58/59/60/61, U-CP-43/46/47)
```

**Cluster-boundary edges (NEW at v2.21):** 14 edges total —
- `U-RT-90 ← U-CP-43` (`GateLevel` enum + 3 axis floor carriers — type/data import)
- `U-RT-90 ← U-CP-46` (`HITLResponse` 4-class enum per C-CP-16 §16.1 — type import)
- `U-RT-90 ← U-CP-47` (`CrossTrustState` carrier per C-CP-21 §21.3 — type import; verify CP-side impl exposes typed carrier or runtime composes per adjacent observation (c))
- `U-RT-91 ← U-CP-58` (C-CP-28 ValidatorFramework Protocol surface — type import for `ctx.validator_framework`)
- `U-RT-91 ← U-CP-59` (`ValidatorOutcome` 5-class + `ValidatorFailClass` 5-class enums — type imports)
- `U-RT-91 ← U-CP-60` (`HITLEscalationBrief` typed payload + `ValidatorEvaluation` envelope — type imports for composer signature)
- `U-RT-91 ← U-CP-61` (workflow_driver post-dispatch hook at C-CP-28 §28.3.3.4 line ~668 — composer-invocation site amendment)
- `U-RT-91 ← U-CP-43` (gate-level + axis floors — composer body consumption)
- `U-RT-91 ← U-CP-46` (HITLResponse + canonical `hitl.*` + `audit.*` namespace carriers — composer body)
- `U-RT-91 ← U-RT-83/84/85` (C-RT-23 validator framework factory + binding chain — `ctx.validator_framework` populated by stage-4 factory)
- `U-RT-91 ← U-RT-60` (existing C-RT-18 wrap-time HITL gate composer + AskUserQuestionSurface binding — partial reuse of mechanics)
- `U-RT-92 ← U-RT-83/84/85` (validator framework factory + binding chain — e2e exercises through production bootstrap)
- `U-RT-92 ← U-RT-60` (HITL gate composer + AskUserQuestionSurface — e2e consumes binding)
- `U-RT-92 ← U-CP-58/59/60/61` (ValidatorFramework body + 5-class enums + escalation brief carrier — e2e fixture construction)

All target already-landed cluster commits (cluster 10-CP-A at `16cf6d7`/`cdf83b1`/`5ca86aa`/`9b009d3`; L9-decies at `3005643`/`d55fbd7`/`37e9d67`; L9-quinquies at `e9b9c49`; U-CP-43/46/47 at CP plan v2.4+ landing commits). No in-flight predecessor; no cycle risk.

**Within-cluster edges (NEW at v2.21):** 3 edges total —
- `U-RT-91 ← U-RT-90` (composer body consumes `compute_effective_palette` + `evaluate_hitl_required` pure helpers)
- `U-RT-92 ← U-RT-90` (e2e test indirectly exercises pure helpers through composer invocation; also direct test scaffolding may verify helpers under e2e bootstrap context)
- `U-RT-92 ← U-RT-91` (e2e test exercises composer + workflow_driver hook amendment)

Linear chain U-RT-90 → U-RT-91 → U-RT-92 acyclic by construction.

**Cross-axis edges:** unchanged from v2.20. L9-duodecies adds ZERO new cross-axis edges per spec §14.15.6 cascade analysis — U-RT-90 + U-RT-91 + U-RT-92 consume already-landed CP-axis carriers (C-CP-19/16/17/21/28 + HITLEscalationBrief + ValidatorFramework Protocol surface) per existing CXA-declared composition seams. CXA v2.9 unchanged. Existing ValidatorFramework→OD edge (CXA v2.9 §2.3.7 row 6) consumes Reading B `validator.escalation` + `hitl.*` spans unchanged.

DAG verified acyclic via Kahn execution (delta layer): 14 new cluster-boundary edges consumed (all targeting already-landed cluster commits); 3 new within-cluster edges (linear chain U-RT-90 → U-RT-91 → U-RT-92); 0 new cross-axis edges. No cycle path within L9-duodecies (linear chain trivially acyclic); no cycle path into L9-duodecies (all cluster-boundary targets fully landed at HEAD, no back-edge possible).

---

## §3 — Coverage matrix delta (v2.20 → v2.21)

| Contract | Units covering | Change at v2.21 |
|---|---|---|
| Runtime spec v1.22 §14.8.2 step 3 (VALIDATOR_ESCALATION un-foreclosure) | U-RT-91 | NEW v2.21 ADD column |
| Runtime spec v1.22 §14.8.2 step 4c (full 4-axis `_hitl_required` consumption at wrap-time composer) | U-RT-90 (helper), U-RT-91 (consumption at wrap-time composer body amendment) | NEW v2.21 ADD column |
| Runtime spec v1.22 §14.8.2 step 4d (UNION-intersection palette consumption at wrap-time composer + cite-fix to C-CP-21 §21.3) | U-RT-90 (helper), U-RT-91 (consumption at wrap-time composer body amendment) | NEW v2.21 ADD column |
| Runtime spec v1.22 §14.8 failure-mode taxonomy (RT-FAIL-HITL-PLACEMENT-FORECLOSED-AT-V19 REMOVAL) | U-RT-91 (impl removal) | NEW v2.21 ADD column |
| Runtime spec v1.22 NEW §14.15 C-RT-25 ValidatorEscalationGateComposer contract (§14.15.1 signature + §14.15.2 invocation discipline + §14.15.3 lifecycle + §14.15.4 invariants 1-6 + §14.15.5 fail-class NEW + §14.15.8 deferred-discretion) | U-RT-91 (composer body), U-RT-92 (e2e verification) | NEW v2.21 ADD column |
| Runtime spec v1.22 §14.15.7 X-AL-2 retirement implications (no retirement gate forced; operationally unblocks validator-escalation surface) | U-RT-92 | NEW v2.21 ADD column |
| Runtime spec v1.22 §0.6 Q5 ratification REVERSAL (VALIDATOR_ESCALATION now bound) | U-RT-91 (impl absorbs reversal) | NEW v2.21 ADD column |
| CP spec v1.13 §28 ValidatorFramework Protocol + 5-class ValidatorOutcome/FailClass/NextAction + HITLEscalationBrief carrier | (pre-v2.21 CP-axis coverage at U-CP-58/59/60/61), U-RT-91 (type import + composer consumption), U-RT-92 (e2e fixture construction) | (no change to CP coverage; runtime-axis ADD column) |
| CP spec v1.2 §19 C-CP-19 (4-axis composition + `_hitl_required` evaluation surface) | (pre-v2.21 CP-axis coverage at U-CP-43), U-RT-90 (consumption at pure helper) | (no change to CP coverage; runtime-axis ADD column) |
| CP spec v1.2 §21 C-CP-21 (cross-trust-boundary palette restriction) | (pre-v2.21 CP-axis coverage at U-CP-47), U-RT-90 (consumption at pure helper) | (no change to CP coverage; runtime-axis ADD column) |
| All other v1.22 + v1.5 + v1.13 + v1.11 contracts | preserved verbatim from v2.20 coverage | (no change) |

**Coverage gap audit:** none surfaced at coherence pass.
- The L9-duodecies units' `Implements` lines cite **only existing filed contracts** (runtime spec v1.22 + CP spec v1.13/v1.2 + ADR-D5 v1.3) — no spec-shaped gap requiring `Phase_7_Class_N_Tension` filing per `implementation-planner` SKILL.md §2.
- The operator-opt-in close pattern's "test infrastructure landed alongside RETIRE-READY transition" obligation per batch-14 §6(a) is NOT applicable at v2.21 — no retirement gate is forced by Reading B landing per scoping doc §5 (CP-21 already RETIRED via Reading A at batch-17). U-RT-92 is included as the e2e verification unit for operational-MET verification (mirrors U-RT-82/85/86/89 close-pattern shape) but no retirement transition is triggered at L9-duodecies landing.
- **Adjacent observation (a) carry**: U-CP-43 v2.4 §0.8 carried items (4-axis input-set divergence — `per_tool_gate_level` axis absence + `deployment_surface_gate_level_floor` plan-invention) persist at CP plan v2.19. Reading B does NOT close this carry; the runtime-axis consumption sources `per_tool_gate_level` from workflow-manifest layer per spec §19.1 line 1702 + line 1507 (NOT from a CP-axis function). U-CP-43 carry remains open CP-plan-side disposition.

**Cite-precision audit:** all v2.21 cites against runtime spec point at **v1.22** (latest filed version per `Project_Workflow_v1_8.md` §7.4 use-latest-version body-citation-alignment clause; v1.22 committed at `918f94a` in this worktree, predecessor v1.21 preserved verbatim by reference). Cross-axis cites: CP spec v1.13 §28 at latest filed version (ValidatorFramework); CP spec v1.2 §19 + §21 at canonical-body version (preserved verbatim through v1.13 delta-only chain); Meta-Arch v1.5 §7.7 at latest filed version; OD spec v1.11 referenced as adjacent context only (no OD amendment owed at v2.21 per scoping doc §2 Q4). No invented `§` pins; no inferred cites.

**Already-landed cluster-boundary consumption cites:**
- CP spec v1.13 §28 ValidatorFramework Protocol body at `harness-cp/src/harness_cp/validator_framework.py:130` per U-CP-58/59/60/61 cluster 10-CP-A closure commits (`16cf6d7`/`cdf83b1`/`5ca86aa`/`9b009d3`) — consumed at U-RT-91 type-import + composer body + U-RT-92 e2e fixture construction.
- CP spec v1.13 §28.2 `ValidatorOutcome` 5-class + `ValidatorFailClass` 5-class + `HITLEscalationBrief` typed payload + `ValidatorNextAction` enum + `ValidatorOutcome → ValidatorNextAction` mapping at `harness-cp/src/harness_cp/validator_framework_types.py` — consumed at U-RT-91 composer body invocation guard + U-RT-92 fixture.
- CP spec v1.13 §28.3.3.4 workflow_driver post-dispatch hook at `harness-cp/src/harness_cp/workflow_driver.py:668` per U-CP-61 closure `9b009d3` — amended at U-RT-91 with NEW `ESCALATE_HITL` branch invoking `compose_validator_escalation_gate(...)`.
- CP spec v1.2 §19 C-CP-19 4-axis composition + `_hitl_required` evaluation surface at CP plan v2.4 U-CP-43 landing — consumed at U-RT-90 helper.
- CP spec v1.2 §21 C-CP-21 cross-trust-boundary palette restriction at CP plan v2.4 U-CP-47 landing (or equivalent CP-axis carrier — verify at U-RT-90 impl arc) — consumed at U-RT-90 helper.
- C-RT-23 stage-4 validator framework factory at runtime plan v2.17 U-RT-83/84/85 closures (`3005643`/`d55fbd7`/`37e9d67`) — consumed at U-RT-91 (factory output is `ctx.validator_framework`) + U-RT-92 (e2e exercises full bootstrap including stage-4).
- C-RT-18 wrap-time HITL gate composer at runtime plan v2.10 U-RT-60 closure (`e9b9c49`) — consumed at U-RT-91 (partial reuse of wrap-time mechanics + AskUserQuestionSurface binding) + U-RT-92 (e2e exercises composer + AskUserQuestion stub).

---

## §4 — Coherence pass

Per `implementation-planner` SKILL.md §5 step 9. Verifying U-RT-90, U-RT-91, U-RT-92 against the four sub-disciplines at §4:

### U-RT-90

1. **Atomicity (§3 four criteria).**
   - 3.1 Single coherent change ✓ — two pure helper functions + two test modules; bound by the 4-axis `_hitl_required` evaluation surface contract.
   - 3.2 Single focused session ✓ — ~1-2-hour implementation including 4-case truth-table tests + pyright validation.
   - 3.3 Independently testable ✓ — pure helpers, no `ctx` dependency; verifiable standalone via unit tests against CP-axis carrier imports.
   - 3.4 Coherent rollback boundary ✓ — one commit revertible (2 modules + 2 test modules).

2. **Spec-traceability (§4.2).** Cites 5 contract sections by ID + section: runtime spec v1.22 §14.8.2 step 4c + step 4d + §14.15.4 invariant 4 + CP spec v1.2 §19.1 + §19.4 + §21.3. All verified against `design-substrate/Spec_Harness_Runtime_v1.md` + `design-substrate/Spec_Control_Plane_v1_2.md` at HEAD `918f94a`. ✓

3. **Dependency-awareness (§4.3).** Declares (within-cluster) none + (cluster-boundary) [U-CP-43, U-CP-46, U-CP-47]. DAG acyclic per §2 Kahn verification. ✓

4. **Implementation-grade-detail (§4.4).** Names files (4 — 2 source modules + 2 test modules); 3 signatures (`compute_effective_palette` + `evaluate_hitl_required` + optional `compute_gate_level` helper); 5 ACs each independently verifiable. AC #1 enumerates 4-case truth-table coverage; AC #2 enumerates 4-axis composition coverage. Does NOT introduce a library not in spec (consumes CP-axis carriers per CP plan v2.4 conformance). Does NOT extend the specification (consumes existing C-CP-19 §19.1 + §19.4 + C-CP-21 §21.3 surfaces verbatim). ✓

### U-RT-91

1. **Atomicity (§3 four criteria).**
   - 3.1 Single coherent change ✓ — one composer module + one wrap-time composer amendment + one fail-class enum amendment (remove + add) + one workflow_driver hook amendment + one escalation-prompt helper. All bound by the C-RT-25 ValidatorEscalationGateComposer contract + foreclosure-removal contract.
   - 3.2 Single focused session ✓ — ~3-4-hour implementation including composer body + wrap-time amendments + workflow_driver hook + unit-level tests + pyright validation.
   - 3.3 Independently testable ✓ — once U-RT-90 lands, U-RT-91's AC #1-#9 can be verified standalone via integration test exercising the composer-invocation site at workflow_driver hook (without full e2e — U-RT-92 scope).
   - 3.4 Coherent rollback boundary ✓ — one commit revertible (composer + wrap-time amendments + fail-class amendment + driver amendment all bound by C-RT-25 contract).

2. **Spec-traceability (§4.2).** Cites 8 contract sections by ID + section: runtime spec v1.22 §14.8.2 step 3 + step 4c + step 4d + §14.15.1 + §14.15.2 + §14.15.3 + §14.15.4 + §14.15.5 + §14.15.8 + §14.8 fail-class taxonomy + §0.6 Q5 + CP spec v1.13 §28.2 + §28.3.3.4. All verified against `design-substrate/Spec_Harness_Runtime_v1.md` + `design-substrate/Spec_Control_Plane_v1_13.md` + `design-substrate/Spec_Control_Plane_v1_10.md` (§28 lineage from v1.10 NEW §25 renamed at v1.13) at HEAD `918f94a`. ✓

3. **Dependency-awareness (§4.3).** Declares within-cluster dep [U-RT-90] + cluster-boundary deps [U-CP-58/59/60/61, U-CP-43, U-CP-46, U-RT-83/84/85, U-RT-60]. DAG acyclic per §2 Kahn verification. ✓

4. **Implementation-grade-detail (§4.4).** Names files (5 — composer module + wrap-time composer amendment + fail-class enum module + workflow_driver amendment + escalation-prompt helper); 4 signatures (composer + fail-class enum + prompt helper + workflow_driver hook amendment); 10 ACs each independently verifiable. AC #4 explicitly enforces C-CP-28 §25.4 invariant 4 ("ESCALATE always emits HITL gate") via grep-verification at workflow_driver hook site. AC #5 + AC #6 enforce foreclosure removal cleanly (both grep-verification + composer body amendment). Does NOT introduce a library not in spec. Does NOT extend the specification (consumes existing CP-axis surfaces + already-landed runtime-axis substrate). ✓

### U-RT-92

1. **Atomicity (§3 four criteria).**
   - 3.1 Single coherent change ✓ — one e2e test module containing 3 test functions (happy-path + palette-matrix parametrized + opt-out branch). Bound by the e2e verification contract for §14.15 composer chain.
   - 3.2 Single focused session ✓ — ~2-3-hour implementation including test fixture authoring + 3 test bodies + OTel exporter integration + pyright validation.
   - 3.3 Independently testable ✓ — once U-RT-90 + U-RT-91 land, U-RT-92's AC can be verified standalone (full bootstrap via `harness_runtime.api.run(...)` + workflow exercise + validator escalation + assertion fan-out).
   - 3.4 Coherent rollback boundary ✓ — one commit revertible.

2. **Spec-traceability (§4.2).** Cites 6 contract sections by ID + section: runtime spec v1.22 §14.8.2 + §14.15.1 + §14.15.2 + §14.15.4 invariants 1-6 + §14.15.7 + CP spec v1.13 §25.5 + §25.4 invariant 2 + Meta-Arch v1.5 §7.7 X-AL-2 (verification-shape sharpening discipline). All verified against `design-substrate/Spec_Harness_Runtime_v1.md` + `design-substrate/Spec_Control_Plane_v1_13.md` + `design-substrate/Spec_Control_Plane_v1_10.md` + `Phase_7_Meta_Architecture_v1.md` + `.harness/phase-7d-retirement-events-batch-{15,16,17,18}.md` at HEAD. ✓

3. **Dependency-awareness (§4.3).** Declares within-cluster deps [U-RT-90, U-RT-91] + cluster-boundary deps [U-RT-83/84/85, U-RT-60, U-CP-58/59/60/61, U-CP-43/46/47]. DAG acyclic per §2 Kahn verification. ✓

4. **Implementation-grade-detail (§4.4).** Names files (1 — test module); 3 test function signatures + test gating + fixture lifecycle; 8 ACs each independently verifiable. AC #6 explicitly enforces composer-depth parity with U-RT-82 + U-RT-85 + U-RT-86 + U-RT-89 close-pattern shape (real bootstrap via `harness_runtime.api.run(...)`, NOT `_FakeCtx`); this is the verification-shape discipline per batch-16 §6 sharpening + applied at batch-17 + batch-18. Does NOT introduce a library not in spec. Does NOT extend the specification. ✓

All four sub-disciplines pass at U-RT-90, U-RT-91, U-RT-92. Cluster-level coherence verified.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Harness_Runtime_v2_21.md` |
| Version | v2.21 |
| Filing event | Spec-revision-driven plan revision — NEW L9-duodecies linear-chain cluster (3 units: U-RT-90 + U-RT-91 + U-RT-92) absorbs runtime spec v1.21 → v1.22 Reading B validator-composer arc landing per scoping doc `.harness/reading_b_validator_composer_arc_scoping.md` (filed at `f922835` in this worktree) + operator AskUserQuestion ratifications 2026-05-24 (D2 = Open Reading B NOW; D1 = Q2(c-i) absorb cite-fix; spec v1.22 committed at `918f94a` in this worktree). 2026-05-24 |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_20.md` (v2.20 + v2.19 + v2.18 + v2.17 substantive content preserved verbatim outside the additive L9-duodecies cluster authoring) |
| New units | 3 — U-RT-90 (effective-palette computation + 4-axis `_hitl_required` consumption — pure helpers), U-RT-91 (ValidatorEscalationGateComposer + post-dispatch re-entry at workflow_driver hook + foreclosure removal + wrap-time composer amendments per §14.8.2 step 3/4c/4d), U-RT-92 (e2e VALIDATOR_ESCALATION cycle test through `harness_runtime.api.run(...)` production bootstrap) |
| Revised units | 0 at this plan (all v2.20 + v2.19 + v2.18 + v2.17 units preserved verbatim per delta-only-plan convention; U-RT-60 grep-verified to require NO AC amendment per D4 disposition + change-note disposition) |
| Cluster | NEW L9-duodecies cluster appended (linear-chain DAG U-RT-90 → U-RT-91 → U-RT-92); L9-undecies + L9-decies + L9-novies + L9-octies + L9-septies + L9-sexies + all earlier clusters preserved verbatim |
| Cross-axis dependencies | unchanged from v2.20. L9-duodecies adds 0 new CXA edges — U-RT-90 + U-RT-91 + U-RT-92 consume already-landed CP-axis carriers (C-CP-19 §19.1 + §19.4 + C-CP-21 §21.3 + C-CP-28 §25.2/§25.3/§25.4/§25.5/§25.7 — all preserved verbatim through canonical CP spec heads) per existing CXA-declared composition seams. CXA v2.9 unchanged per spec §14.15.6 cross-axis cascade enumeration. |
| DAG verification | Kahn-acyclic; 14 new cluster-boundary edges consumed (all targeting already-landed cluster commits — cluster 10-CP-A at `16cf6d7`/`cdf83b1`/`5ca86aa`/`9b009d3`; L9-decies at `3005643`/`d55fbd7`/`37e9d67`; L9-quinquies at `e9b9c49`; U-CP-43/46/47 at CP plan v2.4+ landings); 3 new within-cluster edges (linear chain U-RT-90 → U-RT-91 → U-RT-92); ∅ remaining edges within L9-duodecies (linear-chain trivially complete). |
| Coverage verification | L9-duodecies units cite contract sections across runtime spec v1.22 (§14.8.2 step 3 + 4c + 4d + §14.8 fail-class + §14.15 + §0.6 Q5) + CP spec v1.13 §28 + CP spec v1.2 §19 + §21 + ADR-D5 v1.3 §1.5/§1.10 + Meta-Arch v1.5 §7.7 X-AL-2; all verified against `design-substrate/` at HEAD; no spec-shaped gap surfaced; no `Phase_7_Class_N_Tension` filing required. Adjacent observation (a) U-CP-43 v2.4 §0.8 carried items persist (CP-axis concern, NOT a Reading B blocker per change-note observations). |
| Mechanism discretion | U-RT-91 AC #2 enumerates cross-trust-state derivation source per spec §14.15.8 implementer-discretion. U-RT-91 AC #2 also enumerates composition-ordering for palette intersection per spec change-note adjacent-defect (ii). U-RT-92 ACs accommodate α (recommended default: in-process deterministic ESCALATE fixture + 2x2 palette matrix) / β (broader 5-case ValidatorOutcome coverage) / γ (env-var-gated fixture path) per FM-2 no-extension discipline. |
| Retirement-batch absorption | NO retirement gate forced by Reading B landing per scoping doc §5 cascade analysis (CP-21 already RETIRED at batch-17 via Reading A). Reading B operationally unblocks validator-escalation emission path — operator-supplied validators can emit ESCALATE → HITL gate fires → operator decides per-case. Follow-on operator-discretion retirement-event filing optional if a substitution row covers "validator framework escalation surface operational"; no such gate currently declared. |
| Adjacent findings surfaced | (a) U-CP-43 v2.4 §0.8 carried items (CP-axis); (b) `MCP_TRUST` cardinality drift (CP-axis); (c) cross-trust-state derivation (impl discretion); (d) `validator:` action_id prefix CXA refresh owed; (e) composition ordering for palette intersection (impl discretion). All surfaced per FM-2 discipline; (a)+(b)+(d) require separate follow-on routing; (c)+(e) resolve at U-RT-91 landing arc. |
| Date | 2026-05-24 |
