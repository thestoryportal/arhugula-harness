---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.54
cleared_at: 2026-06-17T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_b6_stdio_transport_floor_per_host_composition.md
  - .harness/beyond-mvp-capability-boundary-ledger.md (B6 execution-decomposition + B-PER-TOOL-SANDBOX-TIER)
  - .harness/r-fs-1-remaining-arcs-grounding-sweep-v1.md (§"Arc B6")
merge_commit: <pending — same PR as the v1.54 amendment>
reviewer_chain:
  - advisor (full-transcript, pre-build) — confirmed the Slice 1/Slice 2 decomposition + gate-free disposition; sharpened mcp_transport_floor (per-host) vs sandbox_tier_floor (per-tool); directed the test-cascade sizing + C10⊥C11 naming
  - probe at ADR-D2 §1.3 / §1.5 (C10⊥C11 resolved in C10's favor — STDIO Tier-3 floor is a cleared hard mandate, not a new decision)
  - Codex out-of-family review (just codex-review, pre-merge) — on the diff
  - bundled-absorption arc (runtime spec v1.54 + harness-runtime/src impl + tests co-land; X-AL-3 back-flow = this fork doc)
---

# Clearance — `Spec_Harness_Runtime_v1.md v1.54`

v1.54 composes the **per-MCP-transport sandbox-tier floor into the per-server §14.9.8 resolver** (R-FS-1 arc **B6 Slice 1**). The stage-5 factory's per-host resolver/driver loop (per-host since B2/§14.9.10 D4) now computes `resolved_tier = tier_max(effective.sandbox_tier, mcp_transport_floor(transport, trust_level, blast_radius).tier)`, so a STDIO host resolves to ≥ `TIER_3_MICROVM` and an L2-remote host to `TIER_4_FULL_VM` — realizing the ADR-D2 §1.3 STDIO-Tier-3 floor + §1.5 `max()` composition at the dispatch resolver and closing the gap the v1.43 §14.9.9 change-note carved out as a future arc. The §14.9.9 FR-1/FR-2 driver machinery then delivers that tier or fail-closes (`RT-FAIL-SANDBOX-DRIVER-UNAVAILABLE`).

**No operator gate — impl-to-cleared-ADR.** Unlike the operator-gated v1.52 (a committed-§14.5.3-invariant relaxation), v1.54 **fulfills** a committed mandate (ADR-D2 §1.3, a hard floor even at local-development per the §1.5 `max()` composition) and **sacrifices no committed invariant** — **per-server-uniform is PRESERVED** (`mcp_transport_floor` is fed the per-host `MCPClientConfig.blast_radius` ⇒ one tier per host). The apparent C10⊥C11 tension was probe-resolved at ADR-D2 §1.3 in C10's favor. Adopt-and-note per workspace `CLAUDE.md` §12.4.1; advisor-confirmed (advisor-not-council, no AUQ).

**Caveats for Phase 7 consumers.** (1) **Real out-of-box behavioral change:** enforcing the floor flips local-dev STDIO `TIER_1_PROCESS` → `TIER_3_MICROVM` (and L2-remote → `TIER_4_FULL_VM`), so those hosts now require a configured `sandbox_driver` or bootstrap fail-closes — the cleared ADR-D2 §1.3 mandate, made safe by the §14.9.9 fail-loud floor (no silent under-sandbox). (2) **Per-tool granularity is NOT in this version** — the full `sandbox_tier_floor` per-cell composition (rows 1-2 forcing + rows 7-10 per-tool blast) + its coupled per-dispatch driver granularity (an inv-3 relaxation) + a `ToolContract` carrier extension remain the distinct future arc **B6 Slice 2** (`B-PER-TOOL-SANDBOX-TIER`), which IS operator-gated. (3) Scope: v1.54 amends ONLY §14.9.8 (adds the transport-floor composition + refines the per-server-uniform scope note) + the §14.9.9 Scope boundary; no new C-RT-NN, no new fail class, no IS/§5.2-hash change, no ADR change.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
