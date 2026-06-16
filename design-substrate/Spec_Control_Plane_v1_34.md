# Spec: Control Plane — v1.34 (delta over v1.33)

---

## Change-note (v1.33 → v1.34)

**Scope of revision.** A single additive sub-section at **C-CP-27 §27** — NEW **§27.8** committing the `MCPServerTrustLevel → MCPTrustTier` projection as **identity-by-ordinal**, the per-server trust **telemetry** projection. This is the **B2-spec-1 (reshape) leg** of the R-FS-1 B2 multi-server-MCP sub-program — the CP-side companion to the runtime spec v1.51 host-multiplicity reshape (the runtime spec consumes this projection for the `mcp.server.trust_tier` span attribute). Sub-decision **D3** of the B2 reshape fork.

**The amendment.** C-CP-27 §27 (PerServerTrustEvaluator + MCPClientNamespaceEmitter, canonical body at `Spec_Control_Plane_v1_10.md` §27) reuses `MCPTrustTier` as a canonical carrier but never specified the projection FROM the AS-owned per-server declared `MCPServerTrustLevel` (carried on `MCPClientConfig.trust_level`) TO `MCPTrustTier` (carried on `MCPHostHealth.trust_tier` for the `mcp.server.trust_tier` telemetry). That projection has been realized in the runtime host factory (`mcp_client_host_factory.py` `_trust_tier_from_level`) as a **constant-collapse stub** returning `LEVEL_0_REFUSE_REMOTE` for every input — vacuously flattening per-server trust telemetry across all servers. v1.34 commits the spec mapping as **identity-by-ordinal**: each `MCPServerTrustLevel` member maps to the `MCPTrustTier` member of the same ordinal — `L0_REFUSE_REMOTE → LEVEL_0_REFUSE_REMOTE`; `L1_SIGNED_PINNED → LEVEL_1_SIGNED_PINNED`; `L2_SANDBOX_ALL → LEVEL_2_SANDBOX_ALL`; `L3_ALLOW_WITH_AUDIT → LEVEL_3_ALLOW_WITH_AUDIT` (byte-identical suffix per ordinal) — retiring the stub.

**Why identity-by-ordinal (council-converged + adversarial-verified).** The AS `MCPServerTrustLevel` and CP `MCPTrustTier` are the **same closed 4-value set** — the CP `MCPTrustTier` docstring is a "byte-exact factor-out of the AS-owned value set" enumerated at `Spec_Action_Surface_v1.md` C-AS-10 §10.3. When two enums are the identical closed value-set, identity is the unique faithful realization. **No transport-aware clamp inside the projection** — transport severity is already owned by the AS per-transport sandbox floor (`Spec_Action_Surface_v1.md` C-AS-10 §10.1 / `sandbox_tier_floor`, which prices STDIO→microVM / remote-L0→REFUSE / remote-L2→full-VM independently of the trust tier); a clamp inside the projection would be a one-source-of-truth violation. The unknown/undeclared-server case is independently refuse-defaulted at the §27.6 inv-4 evaluator (`TrustPolicy.default_tier` + the CONSERVATIVE tier-derivation). Resolved by a **genuine dyadic C10⊥C11 council** (dedicated agents, probe-resolved — `.harness/council/b2-trust-projection-{c10,c11}.md`; design §6): C10 (action-safety) vetoed RETAINING the conservative-collapse stub (it vacates the operator's declared per-server field) AND vetoed any transport-clamp-in-projection (one-source-of-truth); C11 (operator-loop) converged (the stub is a surprise override of declared config).

**TELEMETRY scope — NOT the HITL gate axis (adversarial F2-01, verified at HEAD).** The projection output `host.trust_tier` is **telemetry-only** — grounded on the code trace (not a docstring): it is read solely into the `mcp.server.trust_tier` span attribute via `runtime_tool_dispatcher_factory.py:184` → `MCPClientNamespaceEmitter`; the dispatcher has ZERO `trust_tier` reads. (The `mcp_client_host.py:128-130` docstring's trailing "and gate" clause is stale — a B2-impl docstring fix.) It does NOT feed the dispatch trust **gate** (which resolves from `TrustPolicy` keyed on `server_name` per §27, never from `host.trust_tier`), NOR the locked T-perm-1 HITL **gate** axis `per_mcp_server_trust_tier` (fed by a *separate* hardcoded constant at `hitl_gate_composer.py:462`). Therefore retiring the stub un-flattens per-server trust **telemetry**, not the gate axis. **Un-flattening the locked gate axis (defining `MCP_TRUST_GATE_LEVEL_FLOOR` + adding `Axis.MCP_TRUST_TIER` to `gate_level()`) is the separate B2-spec-2 leg** (CP §19.1, spec-silent today) — carved out with a genuine T-B2-2 C10⊥C11 council per `.harness/class_1_fork_b2_multi_server_mcp_client_reshape.md` §5.

**Authoring authority.** R-FS-1 B2 sub-program, B2-spec-1 leg, per B2-DESIGN (`.harness/r-fs-1-b2-multi-server-mcp-design-v1.md`, #579) §2 D3 + the adversarial review (`.harness/adversarial_review_b2_design.md`, F2-01 telemetry-only correction folded) + `.harness/class_1_fork_b2_multi_server_mcp_client_reshape.md` D3. **Adopt-and-note (no operator AUQ)** — the mapping is council-converged + adversarial-verified + reversible (workspace `CLAUDE.md` §12.4.1); the PR merge is the operator's ratification. Directive: `[[feedback-full-spec-beyond-mvp-nothing-deferred]]` (FULL-SPEC standing directive, roadmap §5.0).

**v1.33 + prior body PRESERVED VERBATIM.** All v1.33 content — §7.4 reconciler-loop substrate-deferral + §7.1–§7.3 + §8 + §25–§29 — is PRESERVED VERBATIM per the delta-only-spec-file convention. C-CP-27 §27.1–§27.7 (canonical body at `Spec_Control_Plane_v1_10.md` §27) is **PRESERVED VERBATIM**; the **only** change is the additive §27.8 below.

**No new contract ID; no new ADR; no enum change; no `MCPTrustTier` / `MCPServerTrustLevel` member change.** Both enums are closed 4-value sets (unchanged); v1.34 commits the *mapping between them* — it mints no new primitive (X-AL-3-clean — the X-AL-3 territory is the runtime C-RT-04 reshape, filed at the B2 reshape fork; this CP delta is the trust-telemetry companion).

---

## §27.8 (NEW) C-CP-27 — `MCPServerTrustLevel → MCPTrustTier` telemetry projection (identity-by-ordinal)

**Contract.** The per-server declared trust level — AS-owned `MCPServerTrustLevel` (carried on `MCPClientConfig.trust_level`, REQUIRED, no default; the value-set enumerated at `Spec_Action_Surface_v1.md` C-AS-10 §10.3) — projects to `MCPTrustTier` (carried on `MCPHostHealth.trust_tier` per runtime spec §14.9.1) by **identity-by-ordinal**:

| `MCPServerTrustLevel` (AS) | `MCPTrustTier` (CP) |
|---|---|
| `L0_REFUSE_REMOTE` | `LEVEL_0_REFUSE_REMOTE` |
| `L1_SIGNED_PINNED` | `LEVEL_1_SIGNED_PINNED` |
| `L2_SANDBOX_ALL` | `LEVEL_2_SANDBOX_ALL` |
| `L3_ALLOW_WITH_AUDIT` | `LEVEL_3_ALLOW_WITH_AUDIT` |

The two enums are the same closed 4-value set (`MCPTrustTier` is a byte-exact factor-out of the AS value-set per C-AS-10 §10.3) — the actual carrier members above (`harness-as` `MCPServerTrustLevel` ↔ `harness-cp` `MCPTrustTier` `cp_shared_types.py`) share the byte-identical `{REFUSE_REMOTE, SIGNED_PINNED, SANDBOX_ALL, ALLOW_WITH_AUDIT}` suffixes per ordinal, so the projection is the ordinal identity — the unique faithful realization. (Implementers translating into `_trust_tier_from_level` map by the full member name above, not the bare ordinal.)

**Purpose (telemetry-fidelity).** The projection output populates the per-server `mcp.server.trust_tier` span attribute (runtime §14.9.1 step 7 / §27.4 `mcp.tool.call` mutation, via `MCPClientNamespaceEmitter`). With identity-by-ordinal, that telemetry honestly reflects each server's declared trust across N servers (the runtime v1.51 multi-server reshape); the prior constant-collapse stub flattened it to `LEVEL_0_REFUSE_REMOTE` for every server.

**No transport clamp.** The projection takes ONLY the declared `MCPServerTrustLevel`; it does NOT re-take transport. Transport severity is owned by the AS per-transport sandbox floor (C-AS-10 §10.1) — pricing it again inside the projection would be a one-source-of-truth violation. The narrow `level`-only projection signature is positive evidence that transport belongs to the floor.

**Scope — telemetry, NOT gating.** This projection is the per-server trust **telemetry** mapping. It does NOT change:
- the **dispatch trust gate** (§27 `PerServerTrustEvaluator.evaluate(server_name, …)` — resolves from `TrustPolicy`, never from the projected `host.trust_tier`; §27.6 invariants 1–5 unchanged), nor
- the **HITL gate axis** `per_mcp_server_trust_tier` of the locked T-perm-1 composition (ADR-D2 §1.5) — that axis's materialization (`MCP_TRUST_GATE_LEVEL_FLOOR: dict[MCPTrustTier, GateLevel]` + adding `Axis.MCP_TRUST_TIER` to `gate_level()`, spec-silent at §19.1 today) is the separate **B2-spec-2** leg, with a genuine T-B2-2 C10⊥C11 council on the mapping direction (does higher trust loosen the gate?). See `.harness/class_1_fork_b2_multi_server_mcp_client_reshape.md` §5.

**Home.** CP-side, per `harness-as/CLAUDE.md` §1.4 (the trust-framework function lives in CP; AS declares the per-transport floor only). The runtime host factory (`mcp_client_host_factory.py` `_trust_tier_from_level`) realizes this CP-owned mapping at B2-impl (retiring the stub at `:197`).

**Invariant.** The projection is total + injective over the closed 4-value set (ordinal identity); every `MCPServerTrustLevel` member has exactly one `MCPTrustTier` image of the same ordinal; no member collapses to another.

---

## §-preserved-verbatim

| Section | Identity | v1.34 status |
|---|---|---|
| §1 — §25 (incl. §7.4 v1.33 reconciler-loop deferral, §25.10–§25.18) | — | PRESERVED VERBATIM |
| §26 / C-CP-26 | **PauseResumeProtocol** | PRESERVED VERBATIM |
| §27.1 — §27.7 / C-CP-27 | **PerServerTrustEvaluator + MCPClientNamespaceEmitter** (canonical body at `Spec_Control_Plane_v1_10.md` §27) | PRESERVED VERBATIM (only the additive §27.8 above) |
| §28 / C-CP-28 | **ValidatorFramework** | PRESERVED VERBATIM |
| §29 / C-CP-29 | **PromptSelectionManifest** | PRESERVED VERBATIM |

§27.8 is an additive sub-section to the existing C-CP-27 contract; no prior section is amended, reinterpreted, or superseded. §19.1 (the HITL gate-axis composition) is UNTOUCHED — its `mcp_trust_tier` materialization is the B2-spec-2 leg.

---

## §-filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_34.md` |
| Authored at | Phase 7 / R-FS-1 B2 sub-program (B2-spec-1 — identity-by-ordinal trust telemetry projection), 2026-06-16 |
| Authoring authority | `.harness/r-fs-1-b2-multi-server-mcp-design-v1.md` §2 D3 + `.harness/adversarial_review_b2_design.md` (F2-01) + `.harness/class_1_fork_b2_multi_server_mcp_client_reshape.md` D3 + the C10⊥C11 council (`.harness/council/b2-trust-projection-{c10,c11}.md`); adopt-and-note (no AUQ, reversible/council-converged); R-FS-1 §5.0 full-spec directive |
| Predecessor | `Spec_Control_Plane_v1_33.md` (v1.33) |
| Co-published (this PR) | the B2 reshape fork doc + runtime spec v1.51 + AS spec v1.10 + clearance marker `.harness/clearance/Spec_Control_Plane-v1_34-cleared-2026-06-16.md` + pointer refreshes (root `CLAUDE.md` §2.3, `harness-cp/CLAUDE.md` §1.2, `claude-artifact-pointers.md` §2.3 — CP spec head v1_33 → v1_34). **Owed at post-merge:** the §12.2.1 roadmap fixed-point refresh (terminating refresh PR, not part of this substantive PR). |
| Coordinated next arcs | B2-spec-2 (gate-axis F2-02 `MCP_TRUST_GATE_LEVEL_FLOOR` + §19.1 `Axis.MCP_TRUST_TIER` + T-B2-2 council) → B2-plan → B2-impl (realize the projection at `mcp_client_host_factory.py` `_trust_tier_from_level`, retiring the stub). |
| Revision policy | Delta-only spec file per workspace `CLAUDE.md` §2.3 convention; v1.33 body + §27.1–§27.7 + §19.1 PRESERVED VERBATIM; the additive §27.8 only |

---

*End of `Spec_Control_Plane_v1_34.md`. Parent guidance at workspace root `CLAUDE.md`. C-CP-27 §27 canonical body at `Spec_Control_Plane_v1_10.md` §27. B2 design at `.harness/r-fs-1-b2-multi-server-mcp-design-v1.md`. B2 reshape fork at `.harness/class_1_fork_b2_multi_server_mcp_client_reshape.md`. Gate-axis materialization → B2-spec-2.*
