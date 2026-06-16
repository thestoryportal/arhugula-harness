# Spec: Control Plane — v1.35 (delta over v1.34)

---

## Change-note (v1.34 → v1.35)

**Scope of revision.** A single additive sub-section at **C-CP-19 §19.1** — NEW **§19.1.2** committing `MCP_TRUST_GATE_LEVEL_FLOOR: dict[MCPTrustTier, GateLevel]` (the per-server trust **gate**-floor mapping table), **resolving the §19.1.1.1 row-3 spec-silence** carried since v1.15 ("per-tier → gate-level mapping is §0.8-carried — owed at follow-on spec-extension arc; type signature is determinate, content is spec-silent"). This is the **B2-spec-2 (gate-axis) leg** of the R-FS-1 B2 multi-server-MCP sub-program — the companion to the B2-spec-1 reshape (#581) which committed the CP §27.8 trust **telemetry** projection. v1.35 materializes the distinct **gate** axis: the previously-unmaterialized 4th axis of the C-CP-19 §19.1 multiplicative HITL gate composition. Sub-decision **F2-02** of the B2 reshape fork (carved out from B2-spec-1 per `.harness/class_1_fork_b2_multi_server_mcp_client_reshape.md` §5).

**The amendment.** The v1.2 §19.1 composition formula — `gate_level = max(per_tool_gate_level, blast_radius_floor(tool), per_mcp_server_trust_floor(mcp_server), persona_tier_floor(persona_tier))` (preserved verbatim through v1.34) — **already names `per_mcp_server_trust_floor(mcp_server)` as a composition term**, but its mapping table (`MCPTrustTier → GateLevel`) was spec-silent (v1.15 §19.1.1.1 row 3). The landed `gate_level()` (`gate_level_rule.py:186`) therefore composed only **3 of the 4** §19.1 axes (`per_tool_gate_level` + `blast_radius` + `persona_tier`), passing `mcp_trust_tier` through `GateLevelInput` un-consumed. v1.35 commits the table, materializing the 4th axis. The mapping is **floor-only / monotone**: each `MCPTrustTier` floors to a `GateLevel` that the gate `max()` can only **raise** toward (never below the other axes); trust modulates the HITL ask-floor for a *permitted* server but never **loosens** the gate below what blast-radius + persona require.

**Why floor-only / monotone (T-B2-2 probe-resolved, NOT council-convened).** The B2 reshape fork §5 flagged **T-B2-2** (the mapping DIRECTION — *does higher trust loosen the gate, or only raise floors?*) as a candidate C10⊥C11 council + operator AUQ. A pre-authoring empirical probe **foreclosed the tension structurally** (per workspace `CLAUDE.md` §10.9 probe-first discipline — surface probe-resolved, do not convene a council that would collapse to single-voice):

1. **The gate is `max()` over escalation rank** (`AUTO < ASK < DENY`; `gate_level_rule.py:214-221`). Within a pure `max()`, any axis floor can only **raise** the composed gate — a high-trust tier mapping to a low floor (`AUTO`) contributes nothing to the `max()`; it can **never lower** the gate below blast-radius/persona. Loosening is not expressible as a floor.
2. **`mcp_trust_tier` is NEVER overridden** — a **landed** U-CP-91 (B3-spec-1) commitment, verbatim at `gate_level_rule.py:131-132`: *"`per_tool_gate_level` + `mcp_trust_tier` are NEVER overridden (a `deny`-tier tool / untrusted MCP server still composes its floor verbatim)."* Making trust *loosen* the gate would therefore not merely be ADR-level — it would **reverse a decision already on main** and break the **locked T-perm-1** composition (ADR-D2 §1.5).
3. **C10 ⊥ C11 (named inline, §13.4 floor):** C10 (action-safety/blast-radius) — trust must compose as a pure floor; untrusted forces escalation; trust must never be a lever that lowers HITL. C11 (operator-loop/burden) — would want trust to reduce burden, but inside the locked `max()` + U-CP-91 that is foreclosed; C11's burden lever already exists (B3's `hitl_auto_approve_policy`, §19.5). Both voices converge on floor-only; the only live judgment was the mapping-table *values*.

The mapping-table values were **operator-ratified 2026-06-16** (AskUserQuestion: floor-only direction CONFIRMED + **Table A — graduated** selected). Adopt-and-note posture (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`); the PR merge is the operator's ratification.

**TELEMETRY vs GATE (the distinct MCPTrustTier consumers).** B2-spec-1 §27.8 committed the `MCPServerTrustLevel → MCPTrustTier` **identity-by-ordinal telemetry** projection (populating the `mcp.server.trust_tier` span attribute). v1.35 commits the orthogonal **gate** mapping `MCPTrustTier → GateLevel` (`MCP_TRUST_GATE_LEVEL_FLOOR`). Both consume the closed 4-value `MCPTrustTier` set, but for different sinks: §27.8 = observability (what trust did the server declare); §19.1.2 = HITL gating (what ask-floor does that trust contribute). The HITL gate floor is **distinct from the §27 dispatch trust gate** (`PerServerTrustEvaluator.evaluate(server_name, …)`, which decides *permitted* keyed on `TrustPolicy` deny/allow/tier — never on `host.trust_tier`). `MCP_TRUST_GATE_LEVEL_FLOOR` is the *third* MCPTrustTier consumer and the only one feeding the `gate_level()` HITL `max()`.

**v1.34 + prior body PRESERVED VERBATIM.** All v1.34 content — §27.8 (B2-spec-1 telemetry projection) + §27.1–§27.7 + §7.4 (v1.33 reconciler-loop deferral) + §25–§29 — is PRESERVED VERBATIM per the delta-only-spec-file convention. C-CP-19 §19.1 / §19.1.1 (the v1.15 canonical 4-axis statement) + §19.3 / §19.4 / §19.5 are **PRESERVED VERBATIM**; the **only** change is the additive §19.1.2 below (which resolves the §19.1.1.1 row-3 spec-silence — the row text is NOT edited; v1.35 supplies the deferred content it pointed to).

**No new contract ID; no new ADR; no enum change; no new fail class; no `MCPTrustTier` / `GateLevel` member change.** Both enums are closed (unchanged); v1.35 commits the *mapping between them* for the §19.1 gate axis — it mints no new primitive (X-AL-3-clean: the §19.1 formula already named the term; v1.35 materializes its spec-silent table). **SPEC-ONLY** — no `harness-*/src/**` edit; the gate axis is inert in production until B2-impl.

---

## §19.1.2 (NEW) C-CP-19 — `MCP_TRUST_GATE_LEVEL_FLOOR` per-server trust gate-floor (resolves §19.1.1.1 row-3 spec-silence)

**Contract.** The §19.1.1.1 row-3 axis `per_mcp_server_trust_floor(mcp_server)` — type `Map<MCPTrustTier, GateLevel>`, content spec-silent since v1.15 — is committed at v1.35 as:

```
MCP_TRUST_GATE_LEVEL_FLOOR: dict[MCPTrustTier, GateLevel] = {
    MCPTrustTier.LEVEL_0_REFUSE_REMOTE:   GateLevel.DENY,
    MCPTrustTier.LEVEL_1_SIGNED_PINNED:   GateLevel.ASK,
    MCPTrustTier.LEVEL_2_SANDBOX_ALL:     GateLevel.ASK,
    MCPTrustTier.LEVEL_3_ALLOW_WITH_AUDIT: GateLevel.AUTO,
}
```

(Operator-ratified Table A, 2026-06-16.) The `MCPTrustTier` domain is the closed 4-value set enumerated at `Spec_Action_Surface_v1.md` C-AS-10 §10.3 (AS-owned, byte-exact factor-out per CP §27); the `GateLevel` codomain is the closed 3-value `{AUTO, ASK, DENY}` escalation ladder (C-CP-19 §19.1 + §16.2).

**Per-tier rationale.**
- `LEVEL_0_REFUSE_REMOTE → DENY` — the lowest declared trust forces the most-escalated gate (structural rejection + HITL). Defense-in-depth: refuse-remote is *also* independently enforced at the §27 dispatch trust gate (a remote L0 server is refused at registration/dispatch); the `DENY` gate-floor is the conservative HITL floor for any L0 server that nonetheless reaches the gate (e.g. a non-remote or allow-listed server declared L0).
- `LEVEL_1_SIGNED_PINNED → ASK` — identity-verified (signature + version pin); the operator still confirms (HITL ask), not auto.
- `LEVEL_2_SANDBOX_ALL → ASK` — full-VM-sandboxed with egress allow-list; the sandbox contains blast radius (a *separate* §19.3 axis), but trust does not yet warrant skipping HITL visibility → ASK.
- `LEVEL_3_ALLOW_WITH_AUDIT → AUTO` — the highest declared trust (allow, with per-fetch/call audit-ledger entry); contributes **no** HITL floor. Under `max()`, `AUTO` (rank 0) lets the *other* axes (blast-radius, persona, per-tool) decide — trust never lowers the gate below them, it merely stops *adding* a trust-floor. The audit ledger covers the allow.

**Composition (materializes the 4th §19.1 axis).** `gate_level()` (C-CP-19 §19.1; `gate_level_rule.py`) composes `Axis.MCP_TRUST` into its `per_axis_floors` via `MCP_TRUST_GATE_LEVEL_FLOOR[input.mcp_trust_tier]`, alongside the three already-materialized axes (`PER_TOOL_GATE_LEVEL`, `BLAST_RADIUS`, `PERSONA_TIER`). The composed gate becomes `max()` over **4** materialized floors — the v1.2 §19.1 formula's `per_mcp_server_trust_floor(mcp_server)` term is now non-vacuous. (`Axis.MCP_TRUST` is already a member of the `Axis` enum at `cp_shared_types.py`; v1.35 makes its floor-table determinate so the composition can consume it.)

**Floor-only / monotone invariants.**
1. **Total.** `MCP_TRUST_GATE_LEVEL_FLOOR` is total over the closed 4-value `MCPTrustTier` domain (every member has exactly one `GateLevel` image).
2. **Monotone (weakly) decreasing in trust.** As declared trust ascends `L0 < L1 < L2 < L3`, the gate-floor descends weakly `DENY ≥ ASK ≥ ASK ≥ AUTO` — more trust never *raises* the floor.
3. **Floor-only (never loosens).** Because the gate is `max()` over escalation rank, this axis can only **raise** the composed gate. A high-trust tier mapping to `AUTO` contributes nothing to the `max()`; it cannot lower the gate below `max(blast_radius_floor, persona_tier_floor, per_tool_gate_level)`. Trust modulates the floor *upward* for untrusted servers; it never *lowers* HITL below the other axes (preserves the locked T-perm-1 composition + the U-CP-91 `mcp_trust` non-override commitment).
4. **Gate, not telemetry, not dispatch.** This mapping feeds ONLY the `gate_level()` HITL `max()`. It does NOT change the §27.8 telemetry projection (`MCPServerTrustLevel → MCPTrustTier`, identity-by-ordinal) nor the §27 dispatch trust gate (`PerServerTrustEvaluator`, keyed on `server_name` via `TrustPolicy`).

**Producer (the gate composer reads the resolved host's trust).** The runtime HITL gate composer (`hitl_gate_composer.py`, U-RT-116) populates `GateLevelInput.mcp_trust_tier` from the **resolved owning MCP host's** declared trust — the per-server `MCPClientConfig.trust_level` projected to `MCPTrustTier` per §27.8, for the host resolved via the v1.51 §14.9.10 tool→server routing index. This **replaces** the v1-era inert constant stub (`hitl_gate_composer.py:462`, `mcp_trust_tier=MCPTrustTier.LEVEL_0_REFUSE_REMOTE`) that was admissible only while the floor table was spec-silent (the value was un-consumed by `gate_level()`). The runtime §14.8.2 step-4c already names `mcp_server_trust_tier` as a composer input (B3-spec-1 v1.49); the resolved-host read + the constant replacement are **B2-impl** conformance to the now-complete §19.1 4-axis formula — NOT a runtime-spec change, and NOT this arc.

**Scope — SPEC-ONLY (impl at B2-impl).** v1.35 authors ONLY the §19.1.2 mapping-table commitment. The realizing impl — adding `Axis.MCP_TRUST: MCP_TRUST_GATE_LEVEL_FLOOR[input.mcp_trust_tier]` to `gate_level()`'s `per_axis_floors` (`gate_level_rule.py`), and wiring the resolved-host trust into the composer's `GateLevelInput.mcp_trust_tier` (replacing `hitl_gate_composer.py:462`) — lands at **B2-impl**; no `harness-*/src` edit this arc; the gate axis is inert in production until then. Closure is demonstrated at B2-impl (a `gate_level()` 4-axis composition test asserting each `MCPTrustTier` floor + a contrasting-baseline test that an L0 server forces `DENY` while an L3 server lets blast/persona decide; the `five_axis_composition.py` consumer's `mcp_trust_tier` pass-through becomes non-vacuous).

**Completeness honesty.** Materializing MCP_TRUST moves the §19.1 composition from **3-of-4 → 4-of-4** materialized axes. (`per_tool_gate_level` is already a degenerate direct-value axis; its own per-tool producer — wiring the C-AS-03 SKILL.md-frontmatter / MCP-manifest `tier` field into `GateLevelInput.per_tool_gate_level` — is the registered **O-CP-3** follow-on, not this arc.)

---

## §-preserved-verbatim

| Section | Identity | v1.35 status |
|---|---|---|
| §1 — §18 | — | PRESERVED VERBATIM |
| §19.1 / §19.1.1 (v1.15 canonical 4-axis statement, incl. §19.1.1.1 row 3) | **gate-level `max()` rule** | PRESERVED VERBATIM (the additive §19.1.2 RESOLVES the row-3 spec-silence; the row text is NOT edited) |
| §19.3 (5-axis D2-layer) / §19.4 (`_hitl_required`) / §19.5 (operator-policy override) | C-CP-19 | PRESERVED VERBATIM |
| §20 — §24 | — | PRESERVED VERBATIM |
| §25 / C-CP-25 (incl. §25.10–§25.18) | **WorkflowDriver** | PRESERVED VERBATIM |
| §26 / C-CP-26 | **PauseResumeProtocol** | PRESERVED VERBATIM |
| §27.1 — §27.8 / C-CP-27 (incl. v1.34 §27.8 telemetry projection) | **PerServerTrustEvaluator + MCPClientNamespaceEmitter** | PRESERVED VERBATIM |
| §28 / C-CP-28 | **ValidatorFramework** | PRESERVED VERBATIM |
| §29 / C-CP-29 | **PromptSelectionManifest** | PRESERVED VERBATIM |

§19.1.2 is an additive sub-section to the existing C-CP-19 §19.1 contract; no prior section is amended, reinterpreted, or superseded. The §19.1.1.1 row-3 "spec-silent / §0.8-carried" disposition is RESOLVED (the deferred content is supplied), not edited.

---

## §-filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_35.md` |
| Authored at | Phase 7 / R-FS-1 B2 sub-program (B2-spec-2 — `MCP_TRUST_GATE_LEVEL_FLOOR` gate-axis materialization), 2026-06-16 |
| Authoring authority | `.harness/class_1_fork_b2_spec_2_gate_axis_materialization.md` (B2-spec-2 fork) + `.harness/class_1_fork_b2_multi_server_mcp_client_reshape.md` §5 (F2-02 carve-out) + `.harness/adversarial_review_b2_design.md` (F2-02) + the T-B2-2 probe-resolution (floor-only, `max()`-foreclosure + U-CP-91 corroboration) + operator AskUserQuestion 2026-06-16 (floor-only CONFIRMED + Table A ratified); adopt-and-note (reversible/probe-resolved); R-FS-1 §5.0 full-spec directive |
| Predecessor | `Spec_Control_Plane_v1_34.md` (v1.34) |
| Co-published (this PR) | the B2-spec-2 fork doc + clearance marker `.harness/clearance/Spec_Control_Plane-v1_35-cleared-2026-06-16.md` + pointer refreshes (root `CLAUDE.md` §2.3, `harness-cp/CLAUDE.md` §1.2, `claude-artifact-pointers.md` §2.3 — CP spec head v1_34 → v1_35) + B2 reshape fork §5/§6 update + beyond-mvp ledger update. **Owed at post-merge:** the §12.2.1 roadmap fixed-point refresh (terminating refresh PR, not part of this substantive PR). |
| Coordinated next arcs | B2-plan (CP/runtime atomic units for the `gate_level()` 4th-axis composition + the composer resolved-host wiring) → B2-impl (realize §19.1.2 at `gate_level_rule.py` `per_axis_floors` + `hitl_gate_composer.py:462` resolved-host trust, retiring the inert stub; e2e contrasting-baseline L0→DENY / L3→blast-decides). Registered follow-on: O-CP-3 (the `per_tool_gate_level` producer, the remaining inert §19.1 axis). |
| Revision policy | Delta-only spec file per workspace `CLAUDE.md` §2.3 convention; v1.34 body + §19.1/§19.1.1/§19.3/§19.4/§19.5 + §27.1–§27.8 PRESERVED VERBATIM; the additive §19.1.2 only |

---

*End of `Spec_Control_Plane_v1_35.md`. Parent guidance at workspace root `CLAUDE.md`. C-CP-19 §19.1 canonical 4-axis statement at `Spec_Control_Plane_v1_15.md` §19.1.1; composition formula at `Spec_Control_Plane_v1_2.md` §19.1. B2 design at `.harness/r-fs-1-b2-multi-server-mcp-design-v1.md`. B2-spec-2 fork at `.harness/class_1_fork_b2_spec_2_gate_axis_materialization.md`. Telemetry companion (§27.8) at `Spec_Control_Plane_v1_34.md`.*
