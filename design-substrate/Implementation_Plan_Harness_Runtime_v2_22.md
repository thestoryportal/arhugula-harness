# Implementation Plan — Harness Runtime v2.22

## Change-note (v2.21 → v2.22)

**Scope of revision.** Narrow-scope status advance — Reading B Class 3 informational divergence carry resolution. v2.21 §"Adjacent observation (a)" recorded the U-CP-43 4-axis input-set divergence carry "persists at CP plan v2.19 (delta-only convention; no carry-resolving revision in delta chain)" + "The U-CP-43 carry-finding remains an open CP-plan-side disposition for separate follow-on routing". With CP spec v1.14 → v1.15 publication (NEW §19.1.1 canonical 4-axis statement) + CP plan v2.19 → v2.20 publication (U-CP-43 GateLevelInput conform per (B2) plan-follows-spec disposition) at this session prior commits, the carry is RESOLVED. v2.22 status-advances the §"Adjacent observation (a)" note + retires the Reading B pragmatic-path Class 3 informational divergence framing. ZERO contract change at C-RT-25; ZERO signature change at any factory; ZERO acceptance criterion change at U-RT-90/91/92 (the ACs were always authored at spec-canonical 4-axis shape per scoping doc §4 — the impl thin-wrap was the divergence, now realigned by CP-axis conformance); ZERO behavior change at composer body.

**v2.21 substantive content preserved verbatim.** All v2.21 L9-duodecies cluster (U-RT-90/91/92) unit bodies + DAG topology + coverage matrix + cluster-boundary edge declarations preserved unchanged. All v2.20 / v2.19 / ... / v2 substantive content preserved.

**Source of fix.** CP spec v1.14 → v1.15 NEW §19.1.1 canonical 4-axis statement publication (this session, prior commit `44fc925`) + CP plan v2.19 → v2.20 U-CP-43 GateLevelInput conform publication (same commit) + harness-cp impl realignment (`gate_level_rule.py` GateLevelInput field-set: add per_tool_gate_level, drop deployment_surface). The Reading B pragmatic-path mid-arc Class 1 decision at runtime impl (thin-wrap CP-axis-as-landed) was explicitly temporary pending CP plan §0.8 carry resolution per the original Reading B operator AskUserQuestion ratification. With the carry now RESOLVED at CP-axis-side, the thin-wrap path consumes a now-spec-canonical CP-axis surface — the pragmatic-path divergence is dissolved by conformance, not removed.

**One amendment site.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **v2.21 §"Adjacent observation (a)" (line 26)** | Status advance: "**Reading B authoring proceeds at v2.21 without blocker** because: (i) ... (ii) ... (iii) ... The U-CP-43 carry-finding remains an open CP-plan-side disposition for separate follow-on routing; Reading B's runtime consumption does not require it." → **"**RESOLVED at v2.22 per CP spec v1.15 §19.1.1 + CP plan v2.20 U-CP-43 GateLevelInput conform 2026-05-24 (this session prior commit). The CP-axis `GateLevelInput` now exposes the spec-canonical 4-axis `{per_tool_gate_level, persona_tier, blast_radius_tier, mcp_trust_tier}` per CP spec v1.15 §19.1.1.1 + (B2) plan-follows-spec disposition; the v2.21-era thin-wrap consumption path (`evaluate_hitl_required(input: GateLevelInput) -> bool` at `hitl_required_consumption.py`) now reads from a spec-canonical CP-axis surface rather than the v2.4-era as-landed surface. The Reading B pragmatic-path Class 3 informational divergence framing at v2.21 is retired at v2.22 — the conformance dissolves the divergence at semantics layer."** Plus footer historical note: original v2.21 carry-preservation prose preserved verbatim at the file layer; v2.22 canonical-reading at consumer layer per this change-note. | CP spec v1.15 §19.1.1 + CP plan v2.20 §0.8 row 1 RESOLVED-as-plan-conformed-to-spec |
| **v2.21 §"Adjacent observation (a) carry" line 213** | Status advance: "**Adjacent observation (a) carry**: U-CP-43 v2.4 §0.8 carried items (4-axis input-set divergence — `per_tool_gate_level` axis absence + `deployment_surface_gate_level_floor` plan-invention) persist at CP plan v2.19. Reading B does NOT close this carry; the runtime-axis consumption sources `per_tool_gate_level` from workflow-manifest layer per spec §19.1 line 1702 + line 1507 (NOT from a CP-axis function). U-CP-43 carry remains open CP-plan-side disposition." → **"**RESOLVED at v2.22 per CP spec v1.15 §19.1.1 + CP plan v2.20 U-CP-43 GateLevelInput conform 2026-05-24 (this session prior commit). The (B2) plan-follows-spec disposition added `per_tool_gate_level` to GateLevelInput + dropped `deployment_surface` + retired DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR. U-CP-43 carry status at CP plan v2.20 §0.8 row 1 → RESOLVED-as-plan-conformed-to-spec; row 2 (MCP_TRUST mapping) → PARTIAL-ADVANCE (mapping facet preserved §0.8-carried). The runtime-axis consumption now reads `per_tool_gate_level` from binding context per the thin-wrap path's binding-tolerant getattr (see `_evaluate_hitl_required_tolerant` at `hitl_gate_composer.py:271-289` v2.20 amendment) — the workflow-manifest source-of-truth path remains canonical at spec §19.1 line 1507; binding-context propagation from manifest to binding is an implementation detail at follow-on workflow-manifest-binding arc."** | CP spec v1.15 §19.1.1 + CP plan v2.20 §0.8 row 1 + harness-runtime impl (`hitl_gate_composer.py` v2.20 amendment) |

**Adjacent harmonization sites.** None — the amendment is two status-advance notes only. The U-RT-90/91/92 unit bodies + ACs + dependencies + DAG topology preserved verbatim per v2.21.

**Sections preserved verbatim from v2.21.** All v2.21 substantive content + all v2.20 prior content + all v2.19 / v2.18 / ... / v2 chain preserved verbatim outside the two status-advance amendment sites enumerated above.

**Status posture.** Proposed (v2.21) → **Proposed (v2.22)**. v2.22 is a status-advance bookkeeping refresh — two carry-status-note amendments absorbing upstream CP-axis conformance. NO new units; NO DAG topology change; NO coverage matrix change; NO acceptance criterion change; NO contract addition; ZERO cross-axis cascade beyond the upstream CP-axis publication already absorbed.

**Downstream absorption owed (post-v2.22).**

(a) Workspace `CLAUDE.md` §2.4 runtime plan row version bump (v2.21 → v2.22); co-published this arc.

(b) Reading B follow-on workflow-manifest-binding arc — propagate `per_tool_gate_level` from workflow-manifest layer (`step.tool_gate_level` per spec §19.1 line 1507 + line 1702) through binding context to `_evaluate_hitl_required_tolerant`'s `getattr(binding, "per_tool_gate_level", GateLevel.AUTO)` site. Operator-discretion timing; not gating any retirement event. NOT scoped at v2.22 per FM-2.

**Adjacent defects surfaced (NOT patched per FM-2 no-extension discipline).**

(i) **U-CP-45 §19.3 5-axis composition parallel drift.** CP plan v2.20 §0 commit message flagged this carry: `FiveAxisCompositionInput` preserves `deployment_surface` field for U-CP-45 §19.3 consumer compatibility at v2.20 revision; AS spec C-AS-12 spec-canonical 5-axis `{per_tool_gate_level, server_trust, persona_tier, blast_radius, sandbox_tier}` does NOT carry `deployment_surface` either. Full §19.3 spec-canonical conformance is out of (B2) scope and remains a parallel drift logged for future follow-on. Surfaced; NOT patched at v2.22 (separate arc).

(ii) **U-RT-90 thin-wrap signature shape vs scoping-doc-recommended 4-arg signature.** v2.21 scoping doc §4 recommended a 4-arg `evaluate_hitl_required(persona_tier, blast_radius_tier, server_trust_tier, per_tool_gate_level) -> bool` signature. Landed impl at HEAD is 1-arg `evaluate_hitl_required(input: GateLevelInput) -> bool` (thin-wrap envelope). The envelope shape provides the same 4 inputs + is semantically equivalent; signature-shape variation is acceptable per implementer-discretion at the landing arc. v2.22 does NOT amend this to the 4-arg explicit-field shape per FM-2 no-extension. Surfaced.

---

## §1 — v2.21 §"Adjacent observation (a)" canonical-reading amendment

Per delta-only plan-file preservation convention (parallel to v2.20 §1 + v2.19 §1 + CP spec v1.13 / v1.14 / v1.15 verbatim-layer-integrity precedents), the v2.21 plan file containing the Reading B change-note + the §"Adjacent observation (a)" prose is NOT edited at v2.22 — the canonical reading at v2.22 incorporates the status-advance per the §0 Amendments table above.

### §1.1 Verbatim-layer integrity

The v2.21 plan file (`Implementation_Plan_Harness_Runtime_v2_21.md`) is NOT edited at v2.22. Consumers reading the delta chain interpret the v2.21 §"Adjacent observation (a)" carry-preservation prose AS canonically status-advanced per §0 above at v2.22.

### §1.2 Authority basis

Both amendment sites cite the same authority chain:
1. CP spec v1.14 → v1.15 NEW §19.1.1 canonical 4-axis statement publication (this session, prior commit `44fc925`).
2. CP plan v2.19 → v2.20 U-CP-43 GateLevelInput conform publication (same commit) + §0.8 row 1 status advance → RESOLVED-as-plan-conformed-to-spec.
3. harness-runtime impl `hitl_gate_composer.py` `_evaluate_hitl_required_tolerant` v2.20 amendment (binding-tolerant per_tool_gate_level getattr) + `hitl_required_consumption.py` test fixture realignment (same commit).
4. Operator AskUserQuestion 2026-05-24 (B2) plan-follows-spec disposition.

### §1.3 Reading B Class 3 informational divergence retirement

The Reading B mid-arc Class 1 surface (CP-axis `GateLevelInput` shape 4-axis `{persona_tier, blast_radius_tier, deployment_surface, mcp_trust_tier}` diverges from runtime spec v1.22 spec-canonical 4-axis `{per_tool_gate_level, blast_radius, server_trust, persona_tier}`) + the operator-selected "Pragmatic path: thin-wrap CP-as-landed surface" decision per Reading B mid-arc AskUserQuestion 2026-05-24 are documented at:
- `[[advisor-before-substantive-work-for-cross-axis-blockers]]` 14th application memory entry (Reading B close)
- Reading B close checkpoint § "Pragmatic-path operator decision (D5)"
- CP plan v2.20 commit message footer (Class 3 informational note)

With v2.22 status-advance, the divergence framing is retired — the CP-axis GateLevelInput now conforms to spec-canonical 4-axis per v2.20; the runtime thin-wrap path consumes a now-spec-canonical CP-axis surface; the divergence at semantics layer is dissolved.

---

## §2 — Preservation guarantees

| Element | Disposition |
|---|---|
| v2.21 L9-duodecies cluster (U-RT-90/91/92) unit bodies + ACs + dependencies | Preserved verbatim |
| v2.21 §14.15 C-RT-25 ValidatorEscalationGateComposer cluster-boundary edges | Preserved verbatim |
| v2.21 change-note (Reading B authoring) outside the 2 status-advance sites | Preserved verbatim |
| v2.20 / v2.19 / v2.18 / ... / v2 substantive plan content | Preserved verbatim |
| 90-unit count + DAG topology + coverage matrix | Preserved verbatim |
| All within-cluster + cluster-boundary edges | Preserved verbatim |
| All ACs at U-RT-90 / U-RT-91 / U-RT-92 | Preserved verbatim |

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Harness_Runtime_v2_22.md` |
| Version | v2.22 |
| Filing event | FM-2 item (a) Reading B follow-on absorption — runtime plan §"Adjacent observation (a)" carry status advance to RESOLVED-via-CP-axis-conformance per CP spec v1.15 §19.1.1 + CP plan v2.20 U-CP-43 GateLevelInput conform 2026-05-24 |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_21.md` (v2.21 substantive content preserved verbatim outside the 2 status-advance sites) |
| Successor | (none — current canonical) |
| Co-published artifacts (this arc) | CP spec v1.15 + CP plan v2.20 (prior commit `44fc925`); harness-cp + harness-runtime impl (same prior commit); Workspace `CLAUDE.md` §2.4 runtime plan row bump v2.21 → v2.22 |
| Downstream absorption owed (next arcs) | Workflow-manifest-binding propagation of `per_tool_gate_level` from `step.tool_gate_level` to binding context (operator-discretion timing); U-CP-45 §19.3 5-axis conformance (parallel drift, separate arc); U-RT-90 4-arg vs envelope signature-shape harmonization (implementer-discretion) |
| Operator authority | AskUserQuestion 2026-05-24 selecting (B) spec extension + sub-selection (B2) plan-follows-spec; Reading B mid-arc operator-ratified pragmatic-path explicit-temporary framing |
| Contract-count change | None |
| Fail-class-count change | None |
| Signature change at any factory | None at v2.22 (the v2.20 CP-axis GateLevelInput field-set change is upstream-absorbed; runtime signatures unchanged) |
| Acceptance criterion change at U-RT-90/91/92 | None |
| Behavior change | None at semantics layer (the v2.20 CP-axis conformance dissolved the divergence; runtime thin-wrap continues consuming the now-spec-canonical surface) |
| Cross-axis cascade | ZERO at v2.22 (CP-axis conformance was the upstream cascade; v2.22 is downstream status advance) |
| Skill discipline | `implementation-planner` Phase-7 revision-pass — narrow-scope status-advance bookkeeping; preservation audit PASSED |
| Date | 2026-05-24 |
