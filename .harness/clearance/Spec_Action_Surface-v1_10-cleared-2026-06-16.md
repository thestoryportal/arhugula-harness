---
artifact: design-substrate/Spec_Action_Surface_v1.md
version: v1.10
cleared_at: 2026-06-16T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc (B2-spec-1 — C-AS-10 §10.3 reciprocal Class-3 cross-ref; no substantive AS change)
back_reference:
  - .harness/class_1_fork_b2_multi_server_mcp_client_reshape.md (B2 reshape fork — §3 AS row)
  - design-substrate/Spec_Control_Plane_v1_34.md C-CP-27 §27.8 (the reciprocal target — the AS→CP identity-by-ordinal projection)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - spec-writer-style apply pass (Claude, this session) — authored the v1.9→v1.10 change-note + an additive reciprocal-cross-ref paragraph at §10.3 (between the audit-ledger sentence and the "Deferred" block). The §10.3 four-level table + the per-MCP-server-trust-tier_floor `max()` reference + the "Deferred" block + all v1.9 + prior content PRESERVED VERBATIM. NO substantive AS change — the per-transport floor (§10.1) + the trust-tier framework (§10.3) + the `sandbox_tier_floor` 5-arg composition are unchanged; B2 consumes them per N servers.
  - harness-adversarial-reviewer (genuine dedicated agent) — APPROVE-WITH-FINDINGS (shared chain at the runtime v1.51 marker). Verified the §10.3 reciprocal paragraph is correctly inserted + the four-level table preserved verbatim + the cross-ref scopes the AS→CP projection as telemetry-only with the gate-axis carved to B2-spec-2.
  - out-of-family Codex review (decorrelated, $0 subscription) — no AS-specific [P2] beyond the shared lineage-index refresh ([P2-1], applied at claude-artifact-pointers §2.3 AS-head + harness-as/CLAUDE.md §1.2).
  - advisor (pre-substantive split + pre-done, transcript-aware) — grouped the reciprocal cross-ref into B2-spec-1 (the reshape leg) per the ratification-boundary split. Pre-done concurred APPROVE-WITH-FINDINGS + surfaced 2 process findings (marker-provenance pre-assertion + B2-spec-2 spine-registration), BOTH APPLIED — see the runtime v1.51 marker's advisor line for the full outcome.
supersedes:
superseded_by:
---

# Clearance — `Spec_Action_Surface v1.10`

v1.10 is the AS-side companion to the B2-spec-1 reshape — a single **reciprocal Class-3 cross-ref** at C-AS-10 §10.3 (MCP server trust-tier framework). The AS-owned `MCPServerTrustLevel` value-set (the L0–L3 four-level framework) is the canonical declaration; CP `MCPTrustTier` is a byte-exact factor-out of it. The AS→CP projection is committed identity-by-ordinal at `Spec_Control_Plane_v1_34.md` C-CP-27 §27.8 — the per-server trust **telemetry** projection (consumed by the runtime v1.51 multi-server reshape for the `mcp.server.trust_tier` span attribute). Transport severity is NOT re-priced in that projection — it stays owned here by the §10.1 per-transport floor (one-source-of-truth). The per-MCP-server-trust **gate**-axis materialization into the HITL `max()` composition is the separate **B2-spec-2** leg, not this telemetry cross-ref.

**No substantive AS change.** The §10.3 four-level table, the per-transport floor (§10.1), the `sandbox_tier_floor` 5-arg composition (§2.2/§2.3), and all v1.9 + prior content are PRESERVED VERBATIM. v1.10 adds ONLY the reciprocal-cross-ref paragraph (additive; no existing line edited). No field-set / attribute-list / AS-AL / signature change.

**Caveat for Phase 7 consumers.** Informational cross-ref only — the AS contracts are unchanged; the cross-ref records the bidirectional AS↔CP link the workspace cross-spec-drift discipline values.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
