# Specification — Control Plane v1.15

## Change-note (v1.14 → v1.15)

**Scope of revision.** Narrow-scope spec clarification — explicitly re-states the v1.2-lineage §19.1 4-axis `_hitl_required` / `gate_level` composition canonical input set as `{per_tool_gate_level, blast_radius_floor, per_mcp_server_trust_floor, persona_tier_floor}` per ADR-D5 v1.3 §1.3.2 + AS spec C-AS-03 (tool-contract per-tool gate-level declaration) + AS spec C-AS-10 §10.3 (MCP server trust framework) + AS spec C-AS-12 (T-perm-1 D2-layer 5-axis composition). Disambiguates the v1.2 narrative which enumerates the 4 axes in code-comment shorthand but does not explicitly call out the per-axis cite-shape. Resolves FM-2 item (a) from Reading B close checkpoint per operator AskUserQuestion 2026-05-24 selecting (B2) plan-follows-spec disposition. ZERO contract change at C-CP-19; ZERO signature change; ZERO acceptance criterion change at any contract; ZERO behavior change at composer body (the canonical formula was always 4-axis with per_tool_gate_level as the C4-contract input; v1.15 makes the per-axis cite-shape explicit).

**v1.14 substantive content preserved verbatim.** All v1.14 canonical-reading amendments (the 4 cite cells at v1.2 §19.1 + §21.3 "C10 five-tier" → "C10 four-tier per AS C-AS-10 §10.3") preserved unchanged. All v1.13 §28 ValidatorFramework rename preserved. All v1.12 §25.2.1 9th-field amendment preserved. All v1.11 / v1.10 / v1.6 / v1.2 substantive content preserved.

**Source of fix.** CP plan v2.4 §0.8 "U-CP-43 4-axis input-set divergence (two facets)" carried-pending-operator-decision row + Reading B close checkpoint FM-2 item (a) + Reading B mid-arc Class 1 surface ("CP-axis `GateLevelInput` shape (4-axis `{persona_tier_tier, blast_radius_tier, deployment_surface, mcp_trust_tier}`) diverges from runtime spec v1.22 spec-canonical 4-axis (`{per_tool_gate_level, blast_radius, server_trust, persona_tier}`)") + operator AskUserQuestion 2026-05-24 disposition selection (B2 plan-follows-spec).

**Authority basis for fix direction.** The CP-axis-side §19.1 canonical 4-axis composition was always `{per_tool_gate_level, blast_radius_floor, per_mcp_server_trust_floor, persona_tier_floor}` per the v1.2 narrative text + the cross-axis cite chain:
- **ADR-D5 v1.3 §1.3.2** — declares the per-tool gate-level input as the C4-contract tool-frontmatter / MCP-manifest-declared gate level `tier ∈ {auto, ask, deny}`; this IS the `per_tool_gate_level` axis.
- **AS spec C-AS-03** — tool contract schema declares the per-tool gate-level field at the SKILL.md frontmatter / MCP server manifest layer; this is the data carrier for `per_tool_gate_level`.
- **AS spec C-AS-10 §10.3** — MCP server trust-tier framework 4-level enumeration; this is the data carrier for `per_mcp_server_trust_floor`.
- **AS spec C-AS-12** — T-perm-1 D2-layer 5-axis composition (`per_tool_gate_level × per_mcp_server_trust_tier × persona_tier × blast_radius_tier × sandbox_tier`) specializes the D5-layer 4-axis composition by adding `sandbox_tier`; the underlying 4-axis structure at the D5 layer is preserved.

The plan-as-landed `GateLevelInput` at CP plan v2.4 U-CP-43 substituted `deployment_surface` for `per_tool_gate_level` — this was a plan-side authoring divergence from the spec-canonical 4-axis. The `deployment_surface` axis belongs at the D2-layer sandbox composition (§19.3 — 5-axis `sandbox_tier_floor` per AS C-AS-02 + C-AS-12), NOT at the D5-layer HITL composition (§19.1). v1.15 re-states the spec-canonical 4-axis explicitly so the plan/runtime layer can conform to the canonical shape per operator-ratified (B2) disposition.

**One amendment site (1 NEW sub-section — §19.1.1 canonical 4-axis statement).**

| Site | Amendment shape |
|---|---|
| **§19.1.1 (NEW) — Canonical 4-axis statement (consumer disambiguation)** | NEW sub-section appended at §19.1 (v1.2 §19.1 substantive composition body preserved verbatim outside this addition). Authors explicit per-axis enumeration table mapping each of the 4 spec-canonical axes to its source-of-truth carrier: (i) `per_tool_gate_level: GateLevel` — per ADR-D5 v1.3 §1.3.2 + AS spec C-AS-03 (tool contract SKILL.md frontmatter / MCP server manifest field — `tier ∈ {auto, ask, deny}` declared per-tool); the per-tool axis IS the gate level (no per-tier mapping; direct value); (ii) `blast_radius_floor: GateLevel` — per v1.2 §19.1 `BLAST_RADIUS_GATE_LEVEL_FLOOR` table mapping `BlastRadiusTier` → `GateLevel` (preserved verbatim from v1.2); (iii) `per_mcp_server_trust_floor: GateLevel` — per AS spec C-AS-10 §10.3 4-level `MCPTrustTier` enumeration mapping (mapping table itself remains §0.8-carried at CP plan — v1.15 cites the enumerating contract; per-tier→gate-level mapping is owed at follow-on spec-extension arc); (iv) `persona_tier_floor: GateLevel` — per v1.2 §19.1 `PERSONA_TIER_GATE_LEVEL_FLOOR` table (preserved verbatim from v1.2). Plus explicit non-axis statement: (v) `deployment_surface` is NOT an axis at §19.1 D5-layer HITL composition — `deployment_surface` belongs at §19.3 D2-layer sandbox composition only. |

**Adjacent harmonization sites.** None — the §19.1 composition formula body, the `_hitl_required` predicate (§19.4), the `BLAST_RADIUS_GATE_LEVEL_FLOOR` / `PERSONA_TIER_GATE_LEVEL_FLOOR` tables (§19.1), the cross-deployment monotonicity (§19.2), and the 5-axis D2 specialization (§19.3) are all preserved verbatim from v1.2. The amendment is additive disambiguation only.

**Sections preserved verbatim from v1.14.** All v1.14 canonical-reading amendments preserved. All v1.13 §28 rename preserved. All v1.12 9th-field amendment preserved. All v1.11/v1.10/v1.6/v1.2 substantive content preserved.

**Status posture.** Proposed (v1.14) → **Proposed (v1.15)**. v1.15 is a fidelity-pure clarification patch — one NEW sub-section authoring canonical 4-axis statement. NO v1.14 contract removed; NO v1.14 contract re-decomposition; NO new contract authored. Contract count unchanged at 27. Fail-class count unchanged. Signature change at any Protocol: none. Acceptance criterion change at any contract: none. Behavior change: none (the canonical formula was always 4-axis with per_tool_gate_level).

**Downstream absorption owed (post-v1.15).**

(a) Workspace `CLAUDE.md` §2.3 CP spec row version bump (v1.14 → v1.15); co-published this arc.

(b) **CP plan v2.19 → v2.20** U-CP-43 revise: add `per_tool_gate_level: GateLevel` field to `GateLevelInput`; drop `deployment_surface` field; retire `DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR` (struck per spec §19.1.1 (v) non-axis statement); `MCP_TRUST_GATE_LEVEL_FLOOR` mapping table remains §0.8-carried (per-tier→gate-level mapping owed at follow-on spec-extension arc); CP plan §0.8 row status advance "U-CP-43 4-axis input-set divergence" → RESOLVED-as-plan-conformed-to-spec at v2.20. Co-published this arc.

(c) **Runtime plan v2.21 → v2.22** L9-duodecies (U-RT-90/91/92) AC amendments: ACs that consume `GateLevelInput` thin-wrap update to consume the spec-canonical 4-axis (drop `deployment_surface`, add `per_tool_gate_level`); pragmatic-path Class 3 informational divergence note at v2.21 advance status to RESOLVED-via-CP-axis-conformance. Co-published this arc.

(d) **harness-cp impl** updates: `harness-cp/src/harness_cp/gate_level_rule.py` `GateLevelInput` Pydantic model: ADD `per_tool_gate_level: GateLevel` field; DROP `deployment_surface: DeploymentSurface` field; `gate_level()` composition body: ADD `per_tool_gate_level` to `per_axis_floors` dict + `max()` composition; `five_axis_composition.py` consumer: update `GateLevelInput` construction site. Tests update: replace deployment_surface tests with per_tool_gate_level tests; preserve existing blast_radius / persona_tier tests. Co-published this arc.

(e) **harness-runtime impl** updates: `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py` `GateLevelInput` construction site sentinel-defaults update (deployment_surface sentinel → per_tool_gate_level sentinel); `hitl_required_consumption.py` is a pure delegate — no change owed. Tests update. Co-published this arc.

(f) **harness-cp/CLAUDE.md** — no immediate update owed (§4.1 substitution status table preserved; the 4-axis disposition is spec/plan/impl-side).

(g) ADR-D5 / ADD §5.2.1 / AS spec C-AS-12 — no cite retag owed at v1.15 (all already cite per_tool_gate_level as canonical; v1.15 RESTATES rather than CHANGES the canonical input set, so existing cites resolve byte-exact to v1.15 §19.1.1).

**Adjacent defects surfaced (NOT patched per FM-2 no-extension discipline).**

(i) **MCP_TRUST per-tier → gate-level mapping table.** v1.15 §19.1.1 (iii) cites AS spec C-AS-10 §10.3 as the data carrier for `per_mcp_server_trust_floor` 4-level enumeration. The mapping `MCPTrustTier → GateLevel` (i.e., what gate level each of `{LEVEL_0_REFUSE_REMOTE, LEVEL_1_SIGNED_PINNED, LEVEL_2_SANDBOX_ALL, LEVEL_3_ALLOW_WITH_AUDIT}` floors to) remains §0.8-carried — spec-silent at both CP §19.1 and AS §10. Surfaced; NOT patched at v1.15 per FM-2 (separate spec-extension arc owed; not blocking the (B2) plan-follows-spec disposition for per_tool_gate_level + deployment_surface facets).

(ii) **`PER_TOOL_GATE_LEVEL_FLOOR` table is degenerate.** Unlike `BLAST_RADIUS_GATE_LEVEL_FLOOR` and `PERSONA_TIER_GATE_LEVEL_FLOOR` (which map enum keys to GateLevel values), `per_tool_gate_level` IS itself a GateLevel value (declared per-tool at C-AS-03 SKILL.md frontmatter / MCP manifest). The composition consumes the GateLevel directly without a lookup table. v1.15 §19.1.1 (i) is explicit about this degeneracy; no table needed at v1.15. Plan + impl conformance at downstream absorption (b) + (d) should NOT author a `PER_TOOL_GATE_LEVEL_FLOOR` table — the field is the value.

(iii) **CP plan v2.4 §0.8 row 1 disposition is "RESOLVED-as-plan-conformed-to-spec" not "spec-extension".** Operator AskUserQuestion 2026-05-24 selected (B2) plan-follows-spec, which means the spec (this v1.15) ARTICULATES the canonical 4-axis explicitly + plan/impl revise to match. NOT (B1) "spec follows plan" (which would have canonicalized the plan-as-landed 4-axis with deployment_surface). The disposition is "plan returns to spec-canonical structure"; spec is the senior authority.

---

## §19.1.1 (NEW) — Canonical 4-axis statement (consumer disambiguation)

The v1.2 §19.1 composition formula `gate_level = max(per_tool_gate_level, blast_radius_floor(tool), per_mcp_server_trust_floor(mcp_server), persona_tier_floor(persona_tier))` (preserved verbatim through v1.13 / v1.14) is the canonical 4-axis multiplicative gate-level rule. v1.15 makes the per-axis cite-shape explicit for consumer disambiguation.

### §19.1.1.1 Per-axis canonical enumeration

| Axis # | Axis name | Type | Source-of-truth carrier | Mapping shape |
|---|---|---|---|---|
| 1 | `per_tool_gate_level` | `GateLevel` (direct value) | ADR-D5 v1.3 §1.3.2 (per-tool gate-level declaration) + AS spec C-AS-03 (tool contract schema — SKILL.md frontmatter / MCP server manifest `tier` field) | Degenerate — `per_tool_gate_level` IS the gate-level value; no per-tier → gate-level mapping; consumed directly at `max()` |
| 2 | `blast_radius_floor(tool)` | `Map<BlastRadiusTier, GateLevel>` | v1.2 §19.1 `BLAST_RADIUS_GATE_LEVEL_FLOOR` table (preserved verbatim through v1.14) — 4-value enum `BlastRadiusTier` mapped to `{AUTO, ASK, DENY}` per ADR-D5 v1.3 §1.3.2 + AS spec C-AS-12 §12.5 | Lookup table — `BlastRadiusTier → GateLevel`; consumed by indexing |
| 3 | `per_mcp_server_trust_floor(mcp_server)` | `Map<MCPTrustTier, GateLevel>` | AS spec C-AS-10 §10.3 4-level enumeration (`MCPTrustTier` value set canonical at AS-side per v1.14 narrative reconciliation: `{LEVEL_0_REFUSE_REMOTE, LEVEL_1_SIGNED_PINNED, LEVEL_2_SANDBOX_ALL, LEVEL_3_ALLOW_WITH_AUDIT}`) | Lookup table — `MCPTrustTier → GateLevel`; **per-tier → gate-level mapping is §0.8-carried** (owed at follow-on spec-extension arc); type signature is determinate, content is spec-silent |
| 4 | `persona_tier_floor(persona_tier)` | `Map<PersonaTier, GateLevel>` | v1.2 §19.1 `PERSONA_TIER_GATE_LEVEL_FLOOR` table (preserved verbatim through v1.14) — 3-value `PersonaTier` enum mapped to `{AUTO, ASK, DENY}` per ADR-D5 v1.3 §1.4 | Lookup table — `PersonaTier → GateLevel`; consumed by indexing |

### §19.1.1.2 Non-axis statement (deployment_surface exclusion)

**`deployment_surface` is NOT an axis at §19.1 D5-layer HITL composition.** `deployment_surface` is an axis at §19.3 D2-layer sandbox composition only (the 5-axis specialization `sandbox_tier_floor(tool, deployment_surface, blast_radius_tier, mcp_transport, mcp_server) -> SandboxTier | REFUSE` per AS spec C-AS-02 + ADR-D2 v1.2 §1.5.1). Plan-as-landed authoring at CP plan v2.4 U-CP-43 substituted `deployment_surface` for `per_tool_gate_level` in `GateLevelInput` — this was a plan-side divergence from the spec-canonical 4-axis. The (B2) plan-follows-spec disposition at v1.15 directs the plan to add `per_tool_gate_level` and drop `deployment_surface` at the §19.1 layer; `deployment_surface` participation at §19.3 D2-layer sandbox composition is unaffected.

### §19.1.1.3 Consumer implication

Consumers of the §19.1 composition formula (CP plan U-CP-43 `GateLevelInput` Pydantic model + downstream runtime composers at runtime spec v1.22 §14.8 + §14.15) MUST consume the 4-axis canonical input set per §19.1.1.1 above. v1.15 §19.1.1 is the disambiguation authority for the per-axis cite-shape; consumers reading v1.15 conform to the canonical 4-axis without ambiguity.

### §19.1.1.4 Verbatim-layer integrity

The v1.2 file (`Spec_Control_Plane_v1_2.md`) is NOT edited at v1.15 — delta-only spec-chain preservation discipline preserved per v1.13 §1.3 + v1.14 §1.3 verbatim-layer-integrity precedent. Consumers reading the delta chain interpret the v1.2 §19.1 composition formula AS canonically supplemented at v1.15 §19.1.1 per this change-note.

---

## §2 — Preservation guarantees

| Element | Disposition |
|---|---|
| v1.14 4-cite-cell canonical-reading amendment ("five-tier" → "four-tier") | Preserved verbatim |
| v1.13 §28 ValidatorFramework rename | Preserved verbatim |
| v1.12 §25.2.1 9th-field `workflow_id` amendment | Preserved verbatim |
| v1.11 / v1.10 / v1.6 / v1.2 substantive contract bodies | Preserved verbatim |
| v1.2 §19.1 composition formula `max()` over 4 axes | Preserved verbatim — v1.15 §19.1.1 supplements with per-axis cite-shape disambiguation; does NOT modify the formula |
| v1.2 `BLAST_RADIUS_GATE_LEVEL_FLOOR` + `PERSONA_TIER_GATE_LEVEL_FLOOR` tables | Preserved verbatim |
| v1.2 §19.3 5-axis D2-layer sandbox composition (`sandbox_tier_floor`) | Preserved verbatim |
| v1.2 §19.4 `_hitl_required` predicate evaluation | Preserved verbatim |
| AS spec C-AS-03 (tool contract schema) | Unchanged at AS-side |
| AS spec C-AS-10 §10.3 (4-level MCPTrustTier enumeration) | Unchanged at AS-side (v1.14 narrative reconciliation completed) |
| AS spec C-AS-12 (T-perm-1 D2-layer 5-axis composition) | Unchanged at AS-side |
| ADR-D5 v1.3 §1.3.2 (per-tool gate-level declaration) | Unchanged at ADR-side |
| ADD §5.2.1 (4-axis multiplicative max formula) | Unchanged at ADD-side |
| All other v1.x contracts | Preserved verbatim |

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_15.md` |
| Version | v1.15 |
| Filing event | FM-2 item (a) from Reading B close checkpoint absorption — CP plan §0.8 U-CP-43 4-axis input-set divergence disposition (B2) plan-follows-spec per operator AskUserQuestion 2026-05-24 |
| Predecessor | `Spec_Control_Plane_v1_14.md` (v1.14 substantive content preserved verbatim outside the NEW §19.1.1 sub-section) |
| Successor | (none — current canonical) |
| Co-published artifacts (this arc) | Workspace `CLAUDE.md` §2.3 CP row bump v1.14 → v1.15; CP plan v2.19 → v2.20 (U-CP-43 revise + §0.8 row status advance); Runtime plan v2.21 → v2.22 (L9-duodecies AC amendments); harness-cp impl (`gate_level_rule.py` + `five_axis_composition.py`); harness-runtime impl (`hitl_gate_composer.py`); tests |
| Downstream absorption owed (next arcs) | MCP_TRUST per-tier → gate-level mapping table spec-extension (separate arc; preserved §0.8-carried) |
| Operator authority | AskUserQuestion 2026-05-24 selecting (B) spec extension at §19.1 + sub-selection (B2) plan-follows-spec (add per_tool_gate_level, drop deployment_surface); CP plan v2.4 §0.8 row 1 carried-pending-operator-decision row |
| Contract-count change | None |
| Fail-class-count change | None |
| Signature change at any Protocol | None |
| Field-set change at any field set | None at spec-side (CP plan + impl-side `GateLevelInput` field-set DOES change at downstream absorption (b) + (d) per (B2) disposition; spec-side §19.1 4-axis formula was always 4-axis, v1.15 makes the per-axis cite explicit) |
| Acceptance criterion change at any contract | None at spec-side (CP plan U-CP-43 acceptance criteria DO change at downstream absorption (b) per (B2) disposition) |
| Behavior change | None at spec-side (the canonical formula was always 4-axis with per_tool_gate_level) |
| Cross-axis cascade | ZERO at semantics layer — ADR-D5 / ADD / AS spec / runtime spec already cite per_tool_gate_level as canonical 4-axis input; v1.15 RESTATES rather than CHANGES, so existing cites resolve byte-exact |
| Skill discipline | `spec-writer` Phase-7 spec-clarification application of operator-ratified (B2) disposition; fidelity-pure clarification patch; NO contract change; NO extension at spec-canonical surface (v1.15 makes explicit what was always canonical); preservation audit PASSED |
| Date | 2026-05-24 |
