---
artifact: design-substrate/Spec_Control_Plane_v1_34.md
version: v1.34
cleared_at: 2026-06-16T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc (B2-spec-1 — identity-by-ordinal MCPServerTrustLevel→MCPTrustTier trust telemetry projection; C-CP-27 NEW §27.8; design-substrate-only, impl deferred to B2-impl)
back_reference:
  - .harness/class_1_fork_b2_multi_server_mcp_client_reshape.md (B2 reshape fork — D3)
  - .harness/r-fs-1-b2-multi-server-mcp-design-v1.md (#579 — §2 D3)
  - .harness/adversarial_review_b2_design.md (F2-01 telemetry-only correction folded)
  - .harness/council/b2-trust-projection-c10.md + .harness/council/b2-trust-projection-c11.md (the genuine dyadic C10⊥C11 council — both converged on identity-by-ordinal)
  - design-substrate/Spec_Control_Plane_v1_10.md §27 (C-CP-27 canonical body — preserved verbatim)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - spec-writer-style apply pass (Claude, this session) — located C-CP-27 §27's last substantive definition at v1_10 (preserved verbatim through v1_33); authored the v1.33→v1.34 delta file (additive NEW §27.8 only; §27.1–§27.7 + §19.1 PRESERVED VERBATIM). Verified the two enums are the same closed 4-value set in code (CP MCPTrustTier {LEVEL_0_REFUSE_REMOTE…LEVEL_3_ALLOW_WITH_AUDIT} cp_shared_types.py:180-189 ↔ AS MCPServerTrustLevel {L0_REFUSE_REMOTE…L3_ALLOW_WITH_AUDIT}; byte-identical suffix per ordinal).
  - harness-adversarial-reviewer (genuine dedicated agent) — APPROVE-WITH-FINDINGS (shared chain at the runtime v1.51 marker). Verified §27.8 scopes the projection as telemetry-only + carves the gate-axis (F2-02) + T-B2-2 to B2-spec-2; enum identity sound; cross-spec cites (CP↔AS) resolve byte-exact.
  - out-of-family Codex review (decorrelated, $0 subscription) — [P2-2 APPLIED] the §27.8 projection table + change-note now use the actual carrier member names (L0_REFUSE_REMOTE/L1_SIGNED_PINNED/L2_SANDBOX_ALL/L3_ALLOW_WITH_AUDIT ↔ LEVEL_*_*) rather than bare ordinals — the normative-contract-precision fix (won the tie vs the adversarial agent's reject-as-non-finding). [P2-3 APPLIED] this marker.
  - advisor (pre-substantive split + pre-done, transcript-aware) — endorsed putting the routine telemetry projection in B2-spec-1 (council-converged, reversible, adopt-and-note) and carving the gate-axis to B2-spec-2. Pre-done concurred APPROVE-WITH-FINDINGS + surfaced 2 process findings (marker-provenance pre-assertion + B2-spec-2 spine-registration), BOTH APPLIED — see the runtime v1.51 marker's advisor line for the full outcome.
supersedes:
superseded_by:
---

# Clearance — `Spec_Control_Plane v1.34`

v1.34 is the CP-side companion to the runtime v1.51 B2-spec-1 reshape — a single additive sub-section **C-CP-27 NEW §27.8** committing the `MCPServerTrustLevel → MCPTrustTier` projection as **identity-by-ordinal** (the per-server trust **telemetry** projection populating the `mcp.server.trust_tier` span attribute). The two enums are the same closed 4-value set (CP `MCPTrustTier` is a byte-exact factor-out of the AS value-set per C-AS-10 §10.3; the actual members share byte-identical `{REFUSE_REMOTE, SIGNED_PINNED, SANDBOX_ALL, ALLOW_WITH_AUDIT}` suffixes per ordinal), so identity is the unique faithful realization. No transport clamp inside the projection (transport severity is owned by the AS per-transport floor — one-source-of-truth). Resolved by a genuine dyadic C10⊥C11 council (both voices converged on identity-by-ordinal, probe-resolved).

**Scope — telemetry, NOT gating.** Per the adversarial F2-01 correction, the projection output `host.trust_tier` is telemetry-only (the dispatch trust gate resolves from `TrustPolicy` keyed on `server_name`, never from `host.trust_tier`; the HITL gate axis is fed by a separate hardcoded constant). §27.8 does NOT change the §27 trust gate (§27.1–§27.7 preserved verbatim) nor the §19.1 HITL gate-axis composition (untouched). The gate-axis materialization (`MCP_TRUST_GATE_LEVEL_FLOOR` + `Axis.MCP_TRUST_TIER`, spec-silent at §19.1 today) + the T-B2-2 mapping-direction council are the separate **B2-spec-2** leg. No new contract ID, no new ADR, no enum change.

**Caveat for Phase 7 consumers.** Design-substrate only — the projection is realized at B2-impl (the runtime `mcp_client_host_factory.py` `_trust_tier_from_level`, retiring the constant-collapse stub at `:197`). Delta-only file: v1.33 body + §27.1–§27.7 + §19.1 PRESERVED VERBATIM.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
