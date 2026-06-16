---
artifact: design-substrate/Implementation_Plan_Control_Plane_v2_36.md
version: v2.36
cleared_at: 2026-06-16T00:00:00-06:00
clearance_type: Phase-6-plan-amendment (atomic-unit decomposition of the B2 multi-server-MCP gate axis — impl-against-cleared-spec post-CP-spec-v1.35 §19.1.2; R-FS-1 B2-plan; CP-axis leg)
back_reference:
  - .harness/r-fs-1-b2-plan-decomposition.md (the B2-plan decomposition summary + coverage matrix + DAG + the load-bearing U-CP-98 HARMFUL-if-alone co-land finding)
  - design-substrate/Spec_Control_Plane_v1_35.md §19.1.2 (B2-spec-2 — the operator-ratified `MCP_TRUST_GATE_LEVEL_FLOOR` Table A gate-axis materialization; floor-only/monotone probe-resolved)
  - .harness/class_1_fork_b2_spec_2_gate_axis_materialization.md (✅ APPLIED) + .harness/class_1_fork_b2_multi_server_mcp_client_reshape.md §5 (F2-02 carve-out; ✅ APPLIED)
  - design-substrate/Spec_Control_Plane_v1_15.md §19.1.1.1 row 3 (the spec-silence v1.35 resolved) + Spec_Control_Plane_v1_2.md §19.1 (the composition formula naming `per_mcp_server_trust_floor`)
  - design-substrate/Implementation_Plan_Control_Plane_v2_35.md (the delta base — preserved verbatim per delta-only-plan-chain; 0 prior unit-body lines changed, full-file diff verified)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - implementation-planner discipline (grounded at HEAD b8282564) — produced 1 NEW CP unit (U-CP-98 `gate_level()` 4th-axis composition: commit `MCP_TRUST_GATE_LEVEL_FLOOR` Table A + add `Axis.MCP_TRUST` to `per_axis_floors` [3-of-4 → 4-of-4] + the F3-01 stale-docstring refresh) reading the already-present `GateLevelInput.mcp_trust_tier` field; +§2.6 unit + §3.7 B2 aggregate cross-axis home (the co-land pin) + §4.5 coverage + §6 O-CP-6. The composition consumes cleared closed enums (`Axis.MCP_TRUST` already a member) + an existing field + the cleared §19.1.2 floor table — no carrier change, no new contract ID, no enum change.
  - harness-adversarial-reviewer Phase-7 pre-merge review (dedicated agent adopting the SKILL) — (recorded at the PR; see `.harness/adversarial-review-r-fs-1-b2-plan.md`)
  - out-of-family Codex review (just codex-review, $0 subscription, decorrelated) — (recorded at the PR)
  - advisor (transcript-aware) — surfaced the load-bearing U-CP-98 HARMFUL-if-alone hazard pre-authoring (composing `Axis.MCP_TRUST` while the composer pins `mcp_trust_tier=L0→DENY` forces every host-less gate to DENY) → the §3.7.3 / §6 O-CP-6 co-land sequencing pin with runtime U-RT-131; verified against the code (`gate_level_rule.py:214-218` 3-axis composition + `max()` over AUTO<ASK<DENY; `hitl_gate_composer.py:462` L0 constant; CP spec v1.35 §19.1.2 Table A L0→DENY). Post-review, confirmed the F2-01 composer-architecture disposition — the composer gates only host-less inference/sub-agent steps (`stage_5_loop_init.py:337/:431`; no tool-step gate site), so U-RT-131 is a **bounded re-scope** to a no-floor default (the `per_tool_gate_level`/O-CP-3 degenerate-default analog), NOT a Class 1 fork, with the real per-server producer registered as the `B-TOOL-GATE` forward arc.
supersedes: design-substrate/Implementation_Plan_Control_Plane_v2_35.md
superseded_by:
---

# Clearance — `Implementation Plan: Control Plane v2.36`

v2.36 is the **CP-axis leg of R-FS-1 — B2-plan** — the atomic-unit decomposition of the multi-server-MCP sub-program's gate axis (the 4th and last §19.1 HITL-gate axis), impl-against-cleared-spec post-CP-spec-v1.35 §19.1.2. **1 NEW CP unit:**

- **U-CP-98** — `gate_level()` 4th-axis composition (`gate_level_rule.py`): commit the `MCP_TRUST_GATE_LEVEL_FLOOR` floor table (operator-ratified Table A: L0→DENY / L1→ASK / L2→ASK / L3→AUTO), add `Axis.MCP_TRUST: MCP_TRUST_GATE_LEVEL_FLOOR[input.mcp_trust_tier]` to `per_axis_floors` (3-of-4 → 4-of-4 materialized axes), and refresh the 5 stale-carry "spec-silent" docstrings to cite §19.1.2 (F3-01). Reads the already-present `GateLevelInput.mcp_trust_tier` field (`:104`). Leaf.

ZERO spec amendment, ZERO new contract ID, X-AL-3-clean (`Axis.MCP_TRUST` already a closed member; the §19.1.2 floor table cleared at CP spec v1.35; the field + the composer's `harness_cp` import pre-exist). All prior units (U-CP-01..97) byte-identical; v2.35 untouched.

**The load-bearing finding for B2-impl consumers — the U-CP-98 ⊕ U-RT-131 CO-LAND PIN (§3.7.3 / §6 O-CP-6).** U-CP-98 is **HARMFUL-if-landed-alone**: the runtime composer pins `mcp_trust_tier=MCPTrustTier.LEVEL_0_REFUSE_REMOTE` (`hitl_gate_composer.py:462`), Table A maps `L0→DENY`, the gate is `max()` over `AUTO<ASK<DENY` — so composing `Axis.MCP_TRUST` while the composer still pins L0 forces **every** host-less gate (inference + sub-agent — the only gate sites that exist) to `DENY`. U-CP-98 MUST land in the **same final impl arc (B2-impl-3)** as runtime U-RT-131 (the composer **no-floor-default** change that replaces the L0 constant with the L3 AUTO-mapping default); U-CP-98 MUST NOT merge in an earlier arc. This is the inverse of B3's *inert*-if-alone G2c, and is a build-sequencing constraint (NOT a DAG edge — the constraint is "the harmful consumer must not precede the safe producer," the reverse of a dependency; CP→RT is forbidden anyway), NOT a fork (both B2 spec legs cleared).

**Composer-architecture sub-finding (the U-RT-131 re-scope; companion §5.1 / runtime v2.47 §6 O-RT-7 item 2).** The adversarial review (F2-01) + composer-architecture re-grounding found the runtime HITL gate composer is constructed for only two host-less placements (`stage_5_loop_init.py:337/:431`, inference + sub-agent) — `TOOL_STEP`s have no HITL gate — so the §19.1.2 Producer ¶ "resolved owning MCP host" has no gate site to populate. Advisor-confirmed: a **bounded re-scope** of U-RT-131 (→ no-floor default), NOT a Class 1 fork (§19.1.2 invariant 3 licenses the no-floor-when-no-host reading; mapped onto the O-CP-3 forward-producer pattern). The real per-server producer is registered as the `B-TOOL-GATE` forward arc (§6 O-CP-6 item 2). B2-impl-3 closes the §19.1 4th-axis *composition*; *producer*-completeness (for BOTH `mcp_trust` and `per_tool_gate_level`) is the registered forward work.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- The CP-package gate-axis composition (U-CP-98) co-publishes with the runtime reshape + gate-axis producer (runtime plan v2.47 U-RT-125..131). See the runtime v2.47 clearance marker for the shared B2-plan decomposition verifications.
- See `.harness/clearance/README.md` for marker discipline.
