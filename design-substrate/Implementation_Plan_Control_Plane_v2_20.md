# Implementation Plan — Control Plane v2.20

## Change-note (v2.19 → v2.20)

**Scope of revision.** Plan-follows-spec absorption pass per CP spec v1.14 → v1.15 NEW §19.1.1 canonical 4-axis statement publication (this session, prior commit). Operator-ratified (B2) disposition at AskUserQuestion 2026-05-24: U-CP-43 `GateLevelInput` field-set amendment to conform to spec-canonical 4-axis `{per_tool_gate_level, blast_radius, server_trust, persona_tier}` — ADD `per_tool_gate_level: GateLevel` field; DROP `deployment_surface: DeploymentSurface` field; RETIRE `DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR` constant (struck per spec v1.15 §19.1.1 (v) non-axis statement: `deployment_surface` is NOT a §19.1 D5-layer axis); `MCP_TRUST_GATE_LEVEL_FLOOR` mapping table remains §0.8-carried (per-tier→gate-level mapping owed at separate follow-on spec-extension arc; this disposition closes ONLY the per_tool_gate_level + deployment_surface facets). CP plan v2.4 §0.8 row 1 status advance "U-CP-43 4-axis input-set divergence" → **RESOLVED-as-plan-conformed-to-spec at v2.20**.

**v2.19 substantive content preserved verbatim.** All v2.19 cite-cascade canonical-reading amendment (cluster 10-CP-A §25 → §28 retag) preserved unchanged. All v2.18 / v2.17 / ... / v2 substantive content preserved.

**Source of fix.** CP spec v1.14 → v1.15 NEW §19.1.1 canonical 4-axis statement publication (this session, prior commit `<pending>`). The v1.15 §19.1.1 explicitly enumerates the spec-canonical 4 axes + states `deployment_surface` is NOT an axis at §19.1 D5-layer (it belongs at §19.3 D2-layer sandbox composition only). Operator AskUserQuestion 2026-05-24 selected disposition (B2) plan-follows-spec; this v2.20 absorbs the (B2) disposition by amending U-CP-43 to conform to the spec-canonical 4-axis.

**Authority basis for fix direction.** Spec v1.15 §19.1.1 is senior to plan v2.4 U-CP-43 authoring per workspace `CLAUDE.md` §1.3 authority chain (ADR → ADD → PRD → spec → plan); plan revises to match spec, not vice versa.

**Amendments.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **§0.8 row 1 (v2.4 U-CP-43 4-axis input-set divergence)** | Status advance: "**[carried — pending operator decision per §4A.7]** Same spec-silence shape as U-CP-08 ..." → **"RESOLVED-as-plan-conformed-to-spec at v2.20 per CP spec v1.14 → v1.15 NEW §19.1.1 canonical 4-axis statement publication (this session prior commit) + operator AskUserQuestion 2026-05-24 (B2) plan-follows-spec disposition. The `per_tool_gate_level` axis is ADDED to `GateLevelInput`; the `deployment_surface` axis is DROPPED (deployment_surface belongs at §19.3 D2-layer sandbox composition only, NOT §19.1 D5-layer HITL composition per spec v1.15 §19.1.1 (v)); `DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR` is RETIRED. The `MCP_TRUST` per-tier→gate-level mapping facet remains §0.8-carried separately."** | CP spec v1.15 §19.1.1 + operator (B2) disposition |
| **§0.8 row 2 (v2.4 U-CP-43 `MCP_TRUST_GATE_LEVEL_FLOOR`)** | Status advance: "**[carried — pending operator decision per §4A.7]** ..." → **"PARTIAL-ADVANCE at v2.20: cardinality narrative facet RESOLVED at CP spec v1.14 (canonical 4-level enumeration per AS spec C-AS-10 §10.3); per-tier→gate-level mapping facet remains §0.8-carried (spec-silent at both CP §19.1 and AS §10; spec-extension arc owed at separate follow-on)."** | CP spec v1.14 narrative reconciliation (FM-2 item (b)) — partial advance only |
| **U-CP-43 unit-body field-set amendment (v2.4 §"Implement 4-axis multiplicative gate-level rule" — IDL signature block at lines 449-477)** | `GateLevelInput` Pydantic-pseudo-IDL signature ADD `per_tool_gate_level: GateLevel` field; DROP `deployment_surface: DeploymentSurface` field; preserve `persona_tier`, `blast_radius_tier`, `mcp_trust_tier` verbatim. The `DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR` constant declaration at line 476 STRUCK. The `MCP_TRUST_GATE_LEVEL_FLOOR` constant declaration at line 477 preserved verbatim with §0.8 carry pointer updated to v2.20 §0.8 row 2 partial-advance status. | CP spec v1.15 §19.1.1 (B2) disposition |
| **U-CP-43 acceptance criteria amendment (v2.4 §"Acceptance criteria" — acc #5 + #6 + #9)** | Acc #5 (`MCP_TRUST_GATE_LEVEL_FLOOR` partial conformance): preserved as PARTIAL-CARRIED with v2.20 §0.8 row 2 cite. Acc #6 (`DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR`): **STRUCK** per spec v1.15 §19.1.1 (v) non-axis statement; replaced with NEW acc #6 "v2.20 — `per_tool_gate_level` GateLevel input field added to `GateLevelInput`; consumed directly at `gate_level()` `max()` composition without per-tier mapping (degenerate per spec v1.15 §19.1.1 (i))." Acc #9 (4-axis input-set divergence spec-silence flag): **STRUCK** at v2.20 per CP spec v1.15 §19.1.1 publication; replaced with NEW acc #9 "v2.20 — `GateLevelInput` field-set conformed to spec-canonical 4-axis `{per_tool_gate_level, blast_radius_tier, persona_tier, mcp_trust_tier}` per CP spec v1.15 §19.1.1.1; `deployment_surface` field dropped per §19.1.1 (v) non-axis statement (deployment_surface participation preserved at §19.3 D2-layer 5-axis sandbox composition only)." | CP spec v1.15 §19.1.1 + (B2) disposition |
| **U-CP-43 `gate_level()` composition body amendment (v2.4 §"Acceptance criteria" — acc #2 carrier prose)** | Acc #2 carrier prose: "**(v2.4 note:** §19.1 enumerates the `max()` over `per_tool_gate_level`, `blast_radius_floor`, `per_mcp_server_trust_floor`, `persona_tier_floor` — see acc #9 for the §0.8-carried divergence between the plan's input axes and the §19.1 four axes.)**" → **"(v2.20: §19.1 enumerates the `max()` over `per_tool_gate_level`, `blast_radius_floor`, `per_mcp_server_trust_floor`, `persona_tier_floor`; the plan now conforms to the spec-canonical 4-axis at v2.20 per CP spec v1.15 §19.1.1.1 (B2) disposition. The `gate_level()` body adds `per_tool_gate_level` to the `per_axis_floors` dict + `max()` composition; the `MCP_TRUST` axis remains §0.8-carried (per-tier mapping spec-silent) so the `max()` ranges over the 3 materialized axes `{per_tool_gate_level, blast_radius_floor, persona_tier_floor}` until the MCP_TRUST mapping lands at follow-on spec-extension arc.)"** | CP spec v1.15 §19.1.1 |
| **U-CP-43 Tests amendment (v2.4 §"Tests" — line 500)** | "**Carried-item tests (NOT authored at v2.4):** tests for `MCP_TRUST_GATE_LEVEL_FLOOR` and `DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR` per-tier mappings are **deferred** pending the §0.8 operator decision — authoring them now would bake an unverified mapping." → **"v2.20 amendment: `DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR` tests RETIRED per spec v1.15 §19.1.1 (v) non-axis statement. NEW tests authored at v2.20: `test_per_tool_gate_level_axis_in_max_composition` (verifies `per_tool_gate_level` participates in `max()`); `test_per_tool_gate_level_degenerate_no_floor_table` (verifies no `PER_TOOL_GATE_LEVEL_FLOOR` constant exists — `per_tool_gate_level` IS the value per spec v1.15 §19.1.1 (i)); `test_gate_level_input_no_deployment_surface_field` (verifies field-set conformance to spec-canonical 4-axis). `MCP_TRUST_GATE_LEVEL_FLOOR` per-tier mapping tests remain deferred pending separate spec-extension arc."** | CP spec v1.15 §19.1.1 + (B2) disposition |

**Plan shape preserved.** v2.19's 73-unit axis-led structure preserved verbatim. No new units; no DAG topology change; no coverage matrix change at structural layer (U-CP-43 amendment is within-unit field-set + acceptance criterion + test amendments only). ZERO new contract authoring; ZERO new acceptance criterion authoring beyond the in-unit acc #6 / #9 replacements. The U-CP-43 unit retains its existing edges (Depends on: U-CP-42, U-CP-44; consumed by U-CP-45 5-axis composition).

**Status posture.** Proposed (v2.19) → **Proposed (v2.20)**. v2.20 is a unit-body field-set amendment absorbing CP spec v1.15 NEW §19.1.1 canonical 4-axis statement. The amendment is within the (B2) plan-follows-spec disposition envelope per operator ratification 2026-05-24.

**Downstream absorption owed (post-v2.20).**

(a) Workspace `CLAUDE.md` §2.4 CP plan row version bump (v2.19 → v2.20); co-published this arc.

(b) **harness-cp impl** updates: `harness-cp/src/harness_cp/gate_level_rule.py` `GateLevelInput` Pydantic model: ADD `per_tool_gate_level: GateLevel` field; DROP `deployment_surface: DeploymentSurface` field; `gate_level()` body: ADD `per_tool_gate_level` to `per_axis_floors` dict + `max()` composition; `five_axis_composition.py` consumer: update `GateLevelInput` construction site. Tests update. Co-published this arc.

(c) **harness-runtime impl** updates: `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py` `GateLevelInput` construction site sentinel-defaults update; `hitl_required_consumption.py` is a pure delegate — no signature change owed. Tests update. Co-published this arc.

(d) **Runtime plan v2.21 → v2.22** L9-duodecies (U-RT-90/91/92) AC amendments per the (B2) absorption — Reading B pragmatic-path Class 3 informational divergence status advance to RESOLVED-via-CP-axis-conformance. Co-published this arc.

(e) **MCP_TRUST per-tier→gate-level mapping table spec-extension arc** — separate follow-on; preserved §0.8-carried per row 2 partial-advance.

**Adjacent defects surfaced (NOT patched per FM-2 no-extension discipline).**

(i) **CP plan v2.4 §"Tests" deferred-test author at v2.20 actually IS authored at v2.20.** v2.20 retires the `DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR` deferral and authors NEW per_tool_gate_level tests at the (b) downstream absorption pass. This is a within-(B2)-disposition envelope amendment; not a separate carry.

(ii) **`MCP_TRUST_GATE_LEVEL_FLOOR` mapping spec-silence carry.** The mapping facet is spec-silent at CP §19.1 + AS §10.3 (only the value-set enumeration is canonical at AS §10.3; the per-tier→gate-level mapping is undeclared). v2.20 §0.8 row 2 advances to PARTIAL-ADVANCE (cardinality narrative RESOLVED at v1.14; mapping carried). The spec-extension to author the mapping is a separate operator-discretion arc (not (B2) scope). Surfaced; not patched at v2.20.

---

## §1 — U-CP-43 unit-body canonical-reading amendment table

Per delta-only plan-file preservation convention (parallel to v2.19 §1 cluster 10-CP-A canonical-reading amendment shape; parallel to CP spec v1.13 §1 verbatim-layer-integrity discipline), the v2.4 plan file containing U-CP-43 unit body is NOT edited at v2.20 — the canonical reading at v2.20 incorporates the field-set + acceptance-criterion + test amendments per the §0 Amendments table above.

### §1.1 Per-line canonical-reading enumeration

| v2.4 site | v2.4 verbatim text (preserved at file layer) | v2.20 canonical reading (at consumer layer) |
|---|---|---|
| v2.4 line 449-477 `GateLevelInput` Pydantic-pseudo-IDL block | `record GateLevelInput { persona_tier : PersonaTier; blast_radius_tier : BlastRadiusTier; deployment_surface : DeploymentSurface; mcp_trust_tier : MCPTrustTier }` + `const DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR: Map<DeploymentSurface, GateLevel> // [carried — see §0.8]` + `const MCP_TRUST_GATE_LEVEL_FLOOR: Map<MCPTrustTier, GateLevel>` | `record GateLevelInput { per_tool_gate_level : GateLevel; persona_tier : PersonaTier; blast_radius_tier : BlastRadiusTier; mcp_trust_tier : MCPTrustTier }` + (DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR STRUCK) + `const MCP_TRUST_GATE_LEVEL_FLOOR: Map<MCPTrustTier, GateLevel> // [§0.8 row 2 PARTIAL-ADVANCE — mapping spec-silent]` |
| v2.4 line 494 acc #6 `DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR CARRIED per §0.8` | STRUCK at v2.20 | NEW acc #6 — `per_tool_gate_level: GateLevel` input field added to GateLevelInput; consumed directly at `gate_level()` `max()` composition without per-tier mapping (degenerate per CP spec v1.15 §19.1.1 (i)). |
| v2.4 line 497 acc #9 4-axis input-set divergence spec-silence flag | STRUCK at v2.20 | NEW acc #9 — GateLevelInput field-set conformed to spec-canonical 4-axis per CP spec v1.15 §19.1.1.1; deployment_surface dropped per §19.1.1 (v) non-axis statement; deployment_surface participation preserved at §19.3 D2-layer 5-axis sandbox composition only. |
| v2.4 line 500 Tests carried-item deferral note | "Carried-item tests ... deferred pending the §0.8 operator decision" | v2.20 amendment per §0 Amendments table — DEPLOYMENT_SURFACE tests RETIRED; NEW per_tool_gate_level tests authored; MCP_TRUST mapping tests remain deferred pending separate spec-extension arc. |
| v2.4 line 482-483 acc #1 + #2 `GateLevel` enum conformance | Preserved verbatim | Preserved verbatim — v2.4 (`GateLevel` conformed to spec §19.1/§16.2 verbatim `{AUTO, ASK, DENY}`) unchanged at v2.20 |
| v2.4 lines for `BLAST_RADIUS_GATE_LEVEL_FLOOR` + `PERSONA_TIER_GATE_LEVEL_FLOOR` tables | Preserved verbatim | Preserved verbatim — the 2 materialized floor tables unchanged at v2.20 |
| v2.4 Depends-on edges + Files line + Signatures line outside the field-set block | Preserved verbatim | Preserved verbatim — no edge or file-target change at v2.20 |

### §1.2 Authority basis at each site

All sites cite CP spec v1.15 §19.1.1 (NEW canonical 4-axis statement) as the authority + operator AskUserQuestion 2026-05-24 (B2) plan-follows-spec disposition.

### §1.3 Verbatim-layer integrity

The v2.4 plan file (`Implementation_Plan_Control_Plane_v2_4.md`) is NOT edited at v2.20 — delta-only plan-chain preservation discipline preserved per v2.19 §1 verbatim-layer-integrity precedent. Consumers reading the delta chain interpret the v2.4 U-CP-43 unit body AS canonically amended per §1.1 above at v2.20.

---

## §2 — Preservation guarantees

| Element | Disposition |
|---|---|
| v2.19 cite-cascade canonical-reading amendment (cluster 10-CP-A §25 → §28 retag) | Preserved verbatim |
| v2.18 U-CP-56 9th-field amendment | Preserved verbatim |
| All v2.17 / v2.16 / ... / v2 substantive unit bodies | Preserved verbatim |
| 73-unit axis-led structure + DAG topology + coverage matrix | Preserved verbatim |
| U-CP-43 Depends-on edges + Files line + Signatures-line `gate_level()` + `hitl_required()` signature | Preserved verbatim |
| `BLAST_RADIUS_GATE_LEVEL_FLOOR` + `PERSONA_TIER_GATE_LEVEL_FLOOR` tables | Preserved verbatim |
| `MCP_TRUST_GATE_LEVEL_FLOOR` constant declaration | Preserved verbatim with §0.8 row 2 PARTIAL-ADVANCE cite pointer update |
| All other plan-wide structural elements | Preserved verbatim |

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_20.md` |
| Version | v2.20 |
| Filing event | FM-2 item (a) from Reading B close checkpoint absorption — CP plan §0.8 U-CP-43 4-axis input-set divergence (B2) plan-follows-spec disposition per CP spec v1.15 §19.1.1 publication 2026-05-24 |
| Predecessor | `Implementation_Plan_Control_Plane_v2_19.md` (v2.19 substantive content preserved verbatim outside the §0.8 row 1 + row 2 status advance + U-CP-43 unit-body canonical-reading amendment) |
| Successor | (none — current canonical) |
| Co-published artifacts (this arc) | CP spec v1.14 → v1.15 (NEW §19.1.1 canonical 4-axis statement); Workspace `CLAUDE.md` §2.4 CP plan row bump v2.19 → v2.20; harness-cp impl (`gate_level_rule.py` + `five_axis_composition.py`); harness-runtime impl (`hitl_gate_composer.py`); Runtime plan v2.22 (L9-duodecies AC amendments); tests |
| Downstream absorption owed (next arcs) | MCP_TRUST per-tier → gate-level mapping table spec-extension (separate arc; preserved §0.8 row 2 PARTIAL-ADVANCE-carried) |
| Operator authority | AskUserQuestion 2026-05-24 selecting (B) spec extension at §19.1 + sub-selection (B2) plan-follows-spec; CP plan v2.4 §0.8 row 1 carried-pending-operator-decision row |
| Contract-count change | None |
| Fail-class-count change | None |
| Signature change at any function | `gate_level()` + `hitl_required()` consume `GateLevelInput` whose field-set changes (add per_tool_gate_level, drop deployment_surface); function signatures unchanged at name + return-type layer |
| Field-set change at GateLevelInput | YES — add `per_tool_gate_level: GateLevel`; drop `deployment_surface: DeploymentSurface` per (B2) spec-canonical conformance |
| Acceptance criterion change at U-CP-43 | YES — acc #6 + #9 replaced per (B2) spec-canonical conformance; acc #1/#2/#3/#4/#5 + #7/#8 preserved verbatim |
| Behavior change | YES — `gate_level()` `max()` composition NOW includes `per_tool_gate_level` axis (was 2-axis materialized at v2.4; now 3-axis materialized at v2.20; MCP_TRUST 4th axis remains spec-silent and unmaterialized) |
| Cross-axis cascade | Runtime plan v2.21 → v2.22 + harness-cp + harness-runtime impl updates per (B2) disposition. NO ADR / ADD / AS spec / CXA amendment owed (all already cite per_tool_gate_level as canonical 4-axis input — see CP spec v1.15 §"Downstream absorption owed" (g)). |
| Skill discipline | `implementation-planner` Phase-7 revision-pass — plan-follows-spec absorption per operator-ratified (B2) disposition; preservation audit PASSED |
| Date | 2026-05-24 |
