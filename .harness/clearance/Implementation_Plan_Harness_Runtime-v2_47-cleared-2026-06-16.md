---
artifact: design-substrate/Implementation_Plan_Harness_Runtime_v2_47.md
version: v2.47
cleared_at: 2026-06-16T00:00:00-06:00
clearance_type: Phase-6-plan-amendment (atomic-unit decomposition of the B2 multi-server-MCP reshape + gate-axis producer runtime surfaces — impl-against-cleared-spec post runtime-v1.51 / CP-v1.34 / CP-v1.35; R-FS-1 B2-plan; runtime-axis leg)
back_reference:
  - .harness/r-fs-1-b2-plan-decomposition.md (the B2-plan decomposition summary + coverage matrix + DAG + the U-RT-131 ⊕ U-CP-98 co-land finding)
  - design-substrate/Spec_Harness_Runtime_v1.md §14.9.10 (v1.51 — the B2-spec-1 multi-server reshape: C-RT-04 singular→mapping + routing index + RT-FAIL-MCP-TOOL-NAME-COLLISION + per-host sandbox)
  - design-substrate/Spec_Control_Plane_v1_34.md §27.8 (the identity-by-ordinal trust telemetry projection, D3) + Spec_Control_Plane_v1_35.md §19.1.2 Producer ¶ (the composer resolved-host trust feed)
  - .harness/class_1_fork_b2_multi_server_mcp_client_reshape.md (✅ APPLIED) + .harness/class_1_fork_b2_spec_2_gate_axis_materialization.md (✅ APPLIED)
  - design-substrate/Implementation_Plan_Harness_Runtime_v2_46.md (the delta base — preserved verbatim per delta-only-plan-chain; 0 prior unit-body lines changed, full-file diff verified)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - implementation-planner discipline (grounded at HEAD b8282564) — produced 7 NEW RT units (U-RT-125 host-dict carrier + ServerName; U-RT-126 stage-3a all-hosts factory; U-RT-127 routing index + RT-FAIL-MCP-TOOL-NAME-COLLISION; U-RT-128 dispatch tool→server resolution + ~10 consumer reshapes; U-RT-129 D3 identity-by-ordinal trust projection + the telemetry-only docstring fix; U-RT-130 per-host sandbox resolver/driver; U-RT-131 gate-axis composer no-floor default for the host-less gate sites — re-scoped from resolved-host wiring per the adversarial F2-01 composer-architecture finding, now a leaf, with the real per-server producer registered as the `B-TOOL-GATE` forward arc) + §3.1d DAG delta (0 cross-axis edges + the co-land pin) + §4.1d coverage + §6 O-RT-7 (incl. the B-TOOL-GATE forward-producer item). The reshape consumes the cleared runtime v1.51 §14.9.10 contracts + the existing config plurality / carriers / import; the one new fail-class (RT-FAIL-MCP-TOOL-NAME-COLLISION) is cleared at runtime v1.51 §14.9.10/§14.9.5.
  - harness-adversarial-reviewer Phase-7 pre-merge review (dedicated agent adopting the SKILL) — (recorded at the PR; see `.harness/adversarial-review-r-fs-1-b2-plan.md`)
  - out-of-family Codex review (just codex-review, $0 subscription, decorrelated) — (recorded at the PR)
  - advisor (transcript-aware) — confirmed full-scope (reshape + gate-axis, not gate-only); confirmed the ~7-RT + 1-CP decomposition + the D3 runtime homing; surfaced the U-CP-98 ⊕ U-RT-131 co-land pin (the load-bearing finding); directed the broader-suite impl-AC (the C-RT-04 HarnessContext shape change ripples to cross-axis field-shape asserts + the CXA-P1 enumeration); and confirmed the post-review F2-01 disposition — the composer gates only host-less inference/sub-agent steps (no tool-step gate site), so U-RT-131 is a **bounded re-scope** to a no-floor default mapping onto the O-CP-3 forward-producer pattern (NOT a Class 1 fork; §19.1.2 invariant 3 licenses the no-floor reading), with the real per-server producer registered as the `B-TOOL-GATE` forward arc.
supersedes: design-substrate/Implementation_Plan_Harness_Runtime_v2_46.md
superseded_by:
---

# Clearance — `Implementation Plan: Harness Runtime v2.47`

v2.47 is the **runtime-axis leg of R-FS-1 — B2-plan** — the atomic-unit decomposition of the multi-server-MCP reshape (B2-spec-1) + the gate-axis producer (B2-spec-2), all impl-against-cleared-spec. **7 NEW RT units:**

- **U-RT-125** — `ServerName` NewType + `HarnessContext.mcp_client_host` → `mcp_client_hosts: dict[ServerName, MCPClientHost]` carrier reshape (D1). Leaf.
- **U-RT-126** — stage-3a factory materializes ALL `config.mcp_clients` (retire the `[0]`), returns the host-dict (D1). [U-RT-125].
- **U-RT-127** — cross-host routing index `dict[ToolId, ServerName]` + `RT-FAIL-MCP-TOOL-NAME-COLLISION` fail-loud (D2). [U-RT-126].
- **U-RT-128** — dispatcher tool→server resolution + the ~10 `ctx.mcp_client_host` consumer reshapes (D2). [U-RT-127].
- **U-RT-129** — D3 identity-by-ordinal `MCPServerTrustLevel → MCPTrustTier` projection (retire the constant stub) + the `mcp_client_host.py` telemetry-only docstring fix. Leaf; realizes CP §27.8 in runtime code.
- **U-RT-130** — per-host sandbox resolver/driver (replace `config.mcp_clients[0]` with per-host config) (D4). [U-RT-126].
- **U-RT-131** — gate-axis composer **no-floor default** for the host-less gate sites (replace the harmful `hitl_gate_composer.py:462` `LEVEL_0_REFUSE_REMOTE` constant with the L3 AUTO-mapping default — the composer gates only host-less inference/sub-agent steps, so no owning MCP host exists at any gate site; the `per_tool_gate_level`/O-CP-3 degenerate-default analog). **Leaf** (re-scoped per the adversarial F2-01 composer-architecture finding, advisor-confirmed bounded re-scope NOT a fork); **co-land with CP U-CP-98**. The resolved-owning-host feed = the registered `B-TOOL-GATE` forward arc.

ZERO spec amendment, ZERO new contract ID beyond the cleared `RT-FAIL-MCP-TOOL-NAME-COLLISION`. All prior units (U-RT-01..124) byte-identical; v2.46 untouched.

**The load-bearing finding for B2-impl consumers — the U-RT-131 ⊕ CP U-CP-98 CO-LAND PIN (§3.1d / §6 O-RT-7).** CP U-CP-98 (the `gate_level()` 4th-axis composition) is **HARMFUL-if-landed-alone** — while this runtime composer still pins the `hitl_gate_composer.py:462` `mcp_trust_tier=L0→DENY` constant, composing the axis forces **every** host-less gate (inference + sub-agent — the only gate sites that exist) to `DENY`. U-RT-131 (the composer no-floor-default change that replaces the L0 constant with the L3 AUTO-mapping default) + U-CP-98 land in the **same final impl arc (B2-impl-3)**; U-CP-98 MUST NOT merge before U-RT-131. U-RT-131-alone is harmless (changes a constant `gate_level()` still ignores); U-CP-98-alone is harmful. NOT a DAG edge (the constraint is the reverse of a dependency; CP→RT is forbidden anyway), NOT a fork (both B2 spec legs cleared).

**The composer-architecture sub-finding (B2-impl-3 consumers MUST read — §3.1d / §6 O-RT-7 item 2 / companion §5.1).** The runtime HITL gate composer is constructed for ONLY two host-less placements — `hitl_inference` (`stage_5_loop_init.py:337`, `PRE_ACTION`) + `hitl_sub_agent` (`:431`, `SUB_AGENT_BOUNDARY`); `TOOL_STEP`s dispatch through `runtime_tool_dispatcher.py`, which composes NO HITL gate. So the §19.1.2 Producer ¶ "resolved owning MCP host" has **no gate site to populate** at HEAD. U-RT-131 was re-scoped (adversarial F2-01; advisor-confirmed bounded re-scope, NOT a Class 1 fork — §19.1.2 invariant 3 licenses the no-floor reading) from "wire the resolved owning host's trust" → "install the L3 no-floor default at the host-less sites," and is now a leaf. The real per-server producer — a **tool-step HITL gate site** — is the registered `B-TOOL-GATE` forward BUILD arc (SPINE ledger Bucket B; §6 O-RT-7 item 2). B2-impl-3 closes the §19.1 4th-axis *composition*, NOT *producer*-completeness (BOTH `mcp_trust` and `per_tool_gate_level` feed degenerate defaults until their real producers land).

**Caveat for B2-impl consumers.** The `C-RT-04` `HarnessContext` shape change (singular `mcp_client_host` → `mcp_client_hosts` mapping) ripples to cross-axis field-shape asserts + the CXA-P1 enumeration allowlist (`test_cxa_pattern_p1.py`) — B2-impl MUST run the BROADER suite, not a single-package run. The ≥2-mock-MCP-server fixture (U-RT-127/128 e2e) is the one genuinely-new build asset. Reshape forward items (B2-restart / server-qualified addressing / B6) are registered forward (O-RT-7), NOT this arc.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- Co-publishes with CP plan v2.36 (U-CP-98 — the `gate_level()` 4th-axis composition). See the CP v2.36 clearance marker for the shared B2-plan decomposition verifications.
- See `.harness/clearance/README.md` for marker discipline.
