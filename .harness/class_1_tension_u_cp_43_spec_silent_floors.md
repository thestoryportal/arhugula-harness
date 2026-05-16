# Class 1 Tension — U-CP-43 spec-silent gate-level floors

**Filed:** 2026-05-16 — Phase 7 sub-phase 7b, CP axis-stream.
**Unit:** U-CP-43 — 4-axis multiplicative gate-level rule (C-CP-19 §19.1/§19.2/§19.4).
**Disposition:** halt-route-split-AC — U-CP-43 partial-landed; two acceptance
criteria struck. CP plan v2.4 §0.8 already carries these as flagged spec-silence
findings — this record tracks the execution-time disposition.

## Defect

The CP plan v2.4 U-CP-43 body declares four floor tables but conforms only two
to CP spec §19.1. The other two are §0.8-carried because **CP spec §19.1 is
genuinely silent** on their content:

1. **`MCP_TRUST_GATE_LEVEL_FLOOR`** — CP spec §19.1 names a "C10 five-tier
   framework" for `per_mcp_server_trust_floor` but does NOT enumerate the five
   tier values inside §19.1, and provides no verbatim per-tier → gate-level
   mapping. AS C-AS-10 §10.1 is a per-MCP-*transport* floor table, not a named
   5-tier trust enum. (The landed `MCPTrustTier` at U-CP-00c has 4 values, byte-
   exact with `Spec_Action_Surface_v1.md` C-AS-10 §10.3 — a further cardinality
   mismatch with §19.1's narrative "five".)

2. **`DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR`** — CP spec §19.1's 4-axis `max()`
   does not carry `deployment_surface` as an axis. Deployment-surface gating
   appears only inside `sandbox_tier_floor` at CP spec §19.3 (the D2 5-axis
   composition). §19.1 contains no per-deployment-surface → gate-level mapping;
   the plan's `DEPLOYMENT_SURFACE` axis is a plan-invention with no §19.1
   mapping to conform to.

The plan body itself (v2.4 acc #5/#6) states the per-tier mappings are
"[carried — pending operator decision per §0.8]" and that "authoring them now
would bake an unverified mapping". Inventing the mappings at code-emission time
would be an X-AL-3 silent design extension.

## Disposition at landing

- **Landed (materializable surface):** `GateLevel` 3-value enum (§19.1/§16.2
  verbatim), `GateLevelInput` / `GateLevelComputation` records,
  `BLAST_RADIUS_GATE_LEVEL_FLOOR` (§19.1 verbatim), `PERSONA_TIER_GATE_LEVEL_
  FLOOR` (all three → ASK, §19.1 verbatim), `gate_level()` multiplicative
  `max()` over the two materialized floors, `hitl_required()` / `_hitl_required`
  predicate (§19.4), `assert_cross_persona_monotonicity()` (§19.2).
- **Struck — acc #5:** `MCP_TRUST_GATE_LEVEL_FLOOR` not declared (no faithful
  content).
- **Struck — acc #6:** `DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR` not declared.
- **Degraded — acc #2:** `gate_level()` `max()` ranges over the two materialized
  §19.1-conformed floors only (`BLAST_RADIUS` + `PERSONA_TIER`), not the plan's
  4-axis input set. `GateLevelInput` still carries `deployment_surface` /
  `mcp_trust_tier` fields (plan signature shape) but they are unconsumed.
- **Informational — acc #9:** the plan's 4-axis input-set divergence from
  §19.1's `{per_tool_gate_level, blast_radius_floor, per_mcp_server_trust_floor,
  persona_tier_floor}` — flagged, not resolved (already §0.8-flagged).
- Carried-item tests for the two struck floors deliberately NOT authored.

## Routing target

Phase 5 CP spec revision-pass — `spec-writer` extension of `Spec_Control_Plane`
§19.1 to (a) enumerate the per-MCP-trust-tier → gate-level mapping and
reconcile the 4-vs-5 cardinality against the landed `MCPTrustTier`, and (b)
decide whether `deployment_surface` is a §19.1 `max()` axis or whether the
plan's `DEPLOYMENT_SURFACE` axis is retired. Distinct from the CP-scope-
discrepancy record (`class_1_tension_cp_scope_discrepancy.md`).

**Status:** OPEN — partial land complete; spec extension pending operator
decision per CP plan v2.4 §0.8.
