# Class 1 fork — B2-spec-2: MCP_TRUST gate-axis materialization (F2-02)

**Fork class:** Class 1 (design-substrate amendment — materializes a spec-silent contract on the LOCKED T-perm-1 HITL gate axis).
**Arc:** R-FS-1 B2 (multi-server MCP), **B2-spec-2** leg (the gate-axis leg carved out from B2-spec-1 per `.harness/class_1_fork_b2_multi_server_mcp_client_reshape.md` §5).
**Posture:** Design-phase / X-AL-3 bundled-absorption (design-substrate amendment + clearance marker + this fork doc in one PR).
**Status:** ✅ APPLIED 2026-06-16 — operator-ratified (AskUserQuestion: floor-only direction CONFIRMED + Table A selected). Applied at **CP spec v1.34 → v1.35** (NEW §19.1.2 `MCP_TRUST_GATE_LEVEL_FLOOR`). **SPEC-ONLY** — no `harness-*/src/**` edit; the gate axis is inert until B2-impl. Clearance marker filed.

---

## §0 — What this leg is

**B2-spec-2 = the GATE axis.** Where B2-spec-1 (#581) committed the per-server trust **telemetry** projection (CP §27.8, `MCPServerTrustLevel → MCPTrustTier` identity-by-ordinal, feeding the `mcp.server.trust_tier` span attribute), B2-spec-2 commits the orthogonal per-server trust **HITL gate**-floor: `MCP_TRUST_GATE_LEVEL_FLOOR: dict[MCPTrustTier, GateLevel]`, the 4th and last unmaterialized axis of the C-CP-19 §19.1 multiplicative HITL gate composition.

This leg discharges sub-decision **F2-02** of the B2 reshape fork (reshape fork §5 item 1) + resolves the **T-B2-2** mapping-direction tension (reshape fork §5 item 2). It was correctly carved out of B2-spec-1 on the **ratification boundary**: the reshape (B2-spec-1) had sensible defaults + a converged council → routine; the gate-axis materialization touches the **LOCKED T-perm-1** 5-axis composition and required resolving a live HITL-security mapping decision → its own leg.

---

## §1 — Grounding (the spec-silent gap — the hard surface)

**The gap, byte-grounded at HEAD `10b3998d`:**

- **CP spec v1.15 §19.1.1.1 row 3** declares `per_mcp_server_trust_floor(mcp_server)` as the 3rd of 4 §19.1 axes, type `Map<MCPTrustTier, GateLevel>`, but states verbatim: *"per-tier → gate-level mapping is §0.8-carried (owed at follow-on spec-extension arc); type signature is determinate, content is spec-silent."* B2-spec-2 IS that follow-on arc.
- The v1.2 §19.1 formula `gate_level = max(per_tool_gate_level, blast_radius_floor(tool), per_mcp_server_trust_floor(mcp_server), persona_tier_floor(persona_tier))` **already names the term** — only its table was spec-silent.
- **Code (`harness-cp/src/harness_cp/gate_level_rule.py`):** `gate_level()` (`:186`) composes `per_axis_floors` over only **3** axes (`PER_TOOL_GATE_LEVEL`, `BLAST_RADIUS`, `PERSONA_TIER`; `:214-218`); `GateLevelInput.mcp_trust_tier` (`:104`) is a present-but-unconsumed field (docstring `:105-111` cites the §0.8 spec-silence). `Axis.MCP_TRUST` already exists in the `Axis` enum (`cp_shared_types.py:193`, value `"mcp-trust"`).
- **Producer stub (`harness-runtime/.../lifecycle/hitl_gate_composer.py:462`):** the composer hardcodes `mcp_trust_tier=MCPTrustTier.LEVEL_0_REFUSE_REMOTE` — admissible only while the floor table was spec-silent (the value was un-consumed by `gate_level()`).
- **`five_axis_composition.py:111-118`** passes `mcp_trust_tier` into `gate_level()`, which drops it — confirming the axis is unmaterialized everywhere (not built-but-vacuous in a hidden site).

---

## §2 — The decision (F2-02 + T-B2-2)

### F2-02 — materialize the gate floor

Commit `MCP_TRUST_GATE_LEVEL_FLOOR` at CP §19.1.2 + compose `Axis.MCP_TRUST` into `gate_level()` (3-of-4 → 4-of-4 materialized §19.1 axes). SPEC commits the table; impl (B2-impl) adds it to `per_axis_floors` + wires the resolved-host trust into the composer (replacing the `:462` stub).

### T-B2-2 — the mapping DIRECTION: **probe-resolved to floor-only / monotone**

The reshape fork §5 flagged T-B2-2 (*does higher trust loosen the gate, or only raise floors?*) as a candidate C10⊥C11 council + AUQ. A pre-authoring empirical probe **foreclosed the tension structurally** → surfaced **probe-resolved**, NOT council-convened (workspace `CLAUDE.md` §10.9 probe-first discipline; a council here would collapse to single-voice — the §10.9 primary-collapse failure mode):

1. **`max()`-over-escalation-rank foreclosure.** The gate is `max()` over `AUTO < ASK < DENY` (`gate_level_rule.py:214-221`). Any axis floor can only **raise** the composed gate; a high-trust→low-floor tier contributes nothing to the `max()` and **cannot lower** the gate below blast/persona. Loosening is not expressible as a floor.
2. **U-CP-91 corroboration (landed, on-main).** `gate_level_rule.py:131-132`, verbatim: *"`per_tool_gate_level` + `mcp_trust_tier` are NEVER overridden (a `deny`-tier tool / untrusted MCP server still composes its floor verbatim)."* Trust-loosening would **reverse a decision already on main** + break the locked T-perm-1 composition (ADR-D2 §1.5) — not a B2 mapping choice.
3. **C10 ⊥ C11 (named inline, §13.4 floor — not convened):** C10 (action-safety/blast-radius) — trust must be a pure floor; untrusted forces escalation; never a loosening lever. C11 (operator-loop/burden) — would want burden reduction, but inside the locked `max()` + U-CP-91 it is foreclosed; C11's burden lever already exists (B3 `hitl_auto_approve_policy`, §19.5). Both converge on floor-only.

**The genuine remaining judgment** (the mapping-table *values*) was surfaced to the operator (AskUserQuestion 2026-06-16). Operator CONFIRMED floor-only + selected **Table A — graduated**:

| `MCPTrustTier` | `GateLevel` floor | Rationale |
|---|---|---|
| `LEVEL_0_REFUSE_REMOTE` | `DENY` | untrusted → structural reject + HITL (defense-in-depth; §27 dispatch gate also refuses remote-L0) |
| `LEVEL_1_SIGNED_PINNED` | `ASK` | identity-verified, still confirm |
| `LEVEL_2_SANDBOX_ALL` | `ASK` | sandboxed, still operator-visible |
| `LEVEL_3_ALLOW_WITH_AUDIT` | `AUTO` | trusted; audit covers it — contributes no floor; blast/persona decide |

Monotone (weakly) decreasing in trust (`DENY ≥ ASK ≥ ASK ≥ AUTO`); floor-only (never lowers below the other axes).

---

## §3 — X-AL-3 classification + cascade

**Class 1 — materializes a spec-silent contract on the LOCKED T-perm-1 gate axis.** Routed to design-substrate (CP spec) per `CLAUDE.md` §4.3. **X-AL-3-clean:** the §19.1 formula already named `per_mcp_server_trust_floor`; v1.35 supplies its spec-silent table (the v1.15 §19.1.1.1 row-3 "owed at follow-on arc" disposition) — it does not extend the contract surface, mint a new primitive, change an enum, or touch an ADR. The locked composition is **honored** (floor-only preserves it; loosening was the foreclosed alternative).

**Cascade:** CP spec v1.34 → v1.35 (headline; NEW §19.1.2). **ZERO runtime-spec change** — runtime §14.8.2 step-4c (B3-spec-1 v1.49) already names `mcp_server_trust_tier` as a composer input; v1.51 §14.9.10 already describes the resolved host. The composer's resolved-host read + the `:462` constant replacement are **B2-impl** conformance to the now-complete §19.1 4-axis formula, NOT a spec change (mirrors B3-spec-1's "`GateLevelInput` carrier-shape is a plan/impl concern, not a C-CP-19 spec change"). *(B2-plan refinement — §4 items 2/5: the `:462` replacement realizes as the L3 **no-floor default** at the host-less gate sites the runtime composer actually gates today, with the **resolved-host read** itself registered as the `B-TOOL-GATE` forward arc, since no tool-step gate site exists yet. The spec's resolved-host framing is honored; its realization is split plan-side. NOT a spec defect — §19.1.2 invariant 3 licenses the no-floor reading.)* **ZERO AS-spec change** — the AS↔CP link is already recorded (B2-spec-1 §10.3 reciprocal cross-ref v1.10); the gate-floor mapping homes CP-side (`harness-cp/CLAUDE.md` §1.4: the trust-framework function lives in CP). **ZERO ADR / ADD / PRD change.** No CXA seam touched.

---

## §4 — Forward items (registered, not dropped)

1. **B2-plan** — ✅ DONE 2026-06-16 (CP plan v2.36 U-CP-98 + runtime plan v2.47 U-RT-125..131; companion `.harness/r-fs-1-b2-plan-decomposition.md`). Decomposed BOTH B2 spec legs (the reshape + the gate axis); the gate-axis composition U-CP-98 is **HARMFUL-if-landed-alone** → a hard co-land sequencing pin with the runtime composer no-floor-default change U-RT-131 at B2-impl-3 (CP plan v2.36 §3.7.3). *(Dashboard note: `.harness/roadmap_status.md` still selects B2-plan as next-action until this plan PR merges; the §12.2 post-merge fixed-point refresh re-derives next-action → B2-impl. The "✅ DONE" marker here is the planning-completion record; the dashboard refresh is the post-merge step, not part of this PR's content.)*
2. **B2-impl** — realize §19.1.2 at `gate_level_rule.py` `per_axis_floors` (U-CP-98) + replace the harmful `hitl_gate_composer.py:462` L0 constant with the **L3 no-floor default** for the host-less gate sites (U-RT-131 — the composer gates only inference/sub-agent steps, no owning MCP host; the `per_tool_gate_level`/O-CP-3 degenerate-default analog); **U-CP-98 ⊕ U-RT-131 co-land at B2-impl-3**; AC = the direct `gate_level()` per-tier table test (L0→DENY…L3→AUTO) + a production **non-regression** baseline (host-less gate composes MCP_TRUST=AUTO → identical to the 3-axis path). **The real per-server resolved-host trust feed is the `B-TOOL-GATE` forward arc** (a tool-step HITL gate site — see item 5), NOT B2-impl-3 (no tool-step gate site exists today).
3. **O-CP-3** (pre-existing registered follow-on) — the `per_tool_gate_level` producer (wire C-AS-03 SKILL.md-frontmatter / MCP-manifest `tier` into `GateLevelInput.per_tool_gate_level`); the remaining degenerate-default §19.1 axis (4-of-4 *composition* → full §19.1 *producer*-completeness).
4. **Docstring refresh (B2-impl, bundled with item 2)** — (a) the `hitl_gate_composer.py:462` constant becomes the L3 no-floor default (U-RT-131); (b) the 5+ `gate_level_rule.py` docstring sites that assert the `MCP_TRUST` mapping is "spec-silent / owed at follow-on arc" (module docstring `:6-13` + `:26-27`; `GateLevelInput.mcp_trust_tier` `:105-110`; `GateLevelComputation` `:138-141`; `gate_level()` `:190-195`) become **factually false at v1.35 merge** (stale-carry-text) → refresh them to cite §19.1.2 when B2-impl edits `gate_level_rule.py` (it already adds `Axis.MCP_TRUST` to `per_axis_floors`). Registered here so the docstring drift is not missed at impl. (Decorrelated adversarial finding F3-01.)
5. **`B-TOOL-GATE`** (NEW registered forward — the real per-server MCP-trust producer; SPINE ledger Bucket B; CP plan v2.36 §6 O-CP-6 item 2 / runtime v2.47 §6 O-RT-7 item 2) — a **tool-step HITL gate site** that resolves the owning MCP host (via the v1.51 routing index) + feeds its D3-projected per-server `MCPTrustTier` into `GateLevelInput.mcp_trust_tier`, so an L0-server tool actually floors its gate to DENY. The §19.1.2 Producer ¶ + runtime §14.8.2 step-4c envision this, but the runtime composer gates only host-less inference/sub-agent steps today (`stage_5_loop_init.py:337/:431`); tool steps dispatch through `runtime_tool_dispatcher.py` with no HITL gate. Surfaced by the adversarial F2-01 composer-architecture finding (advisor-confirmed bounded re-scope of U-RT-131, NOT a Class 1 fork — §19.1.2 invariant 3 licenses the no-floor-when-no-host reading). HIGH load-bearing — it makes the MCP-trust gate axis non-vacuous in production.

After B2: the frozen `R → B4 → CA → B5 → B6 → B7 → M` arc order.

---

## §5 — Verification + filing footer

**Verification.** Every cite re-grounded at HEAD `10b3998d` this session: CP §19.1.1.1 row-3 spec-silence (v1.15 lines 67 + change-note (i) line 49); the v1.2 §19.1 formula naming `per_mcp_server_trust_floor`; `gate_level_rule.py` (`:104` field, `:131-132` U-CP-91 non-override, `:186/:214-218` 3-axis composition); `cp_shared_types.py:172` MCPTrustTier 4-member domain + `:193` `Axis.MCP_TRUST`; `hitl_gate_composer.py:462` inert constant; `five_axis_composition.py:111-118` vacuous pass-through; runtime §14.8.2 step-4c (v1.49) `mcp_server_trust_tier` composer-input naming; §27 `PerServerTrustEvaluator.evaluate(server_name, …)` dispatch-gate disjointness. Confidence **[HIGH]** on the grounding, the `max()`-foreclosure + U-CP-91 corroboration (probe conclusive), the X-AL-3 classification, and the CP-only cascade scope. **[MODERATE]** on the exact `L2_SANDBOX_ALL → ASK` vs `→ AUTO` cell (the one genuinely deployment-judgment call — Table A chose ASK; Table C's AUTO is the reversible alternative the operator declined).

| Field | Value |
|---|---|
| Fork | `class_1_fork_b2_spec_2_gate_axis_materialization.md` |
| Authority | reshape fork §5 (F2-02 + T-B2-2 carve-out) + B2-DESIGN (#579) §2/§5 + adversarial review (`adversarial_review_b2_design.md`, F2-02) + the T-B2-2 probe-resolution + operator AskUserQuestion 2026-06-16 (floor-only + Table A); R-FS-1 §5.0 full-spec directive |
| Applied at | CP spec v1.35 (NEW §19.1.2); SPEC-ONLY; clearance marker `.harness/clearance/Spec_Control_Plane-v1_35-cleared-2026-06-16.md` |
| Coordinated next | B2-plan → B2-impl (realize the 4th-axis composition + composer wiring) |
| Revision policy | Design-substrate amendment per `CLAUDE.md` §4.5; the mapping is reversible/probe-resolved + operator-ratified (adopt-and-note) |

---

*End of B2-spec-2 gate-axis materialization fork. Reshape parent at `.harness/class_1_fork_b2_multi_server_mcp_client_reshape.md` §5. Design at `.harness/r-fs-1-b2-multi-server-mcp-design-v1.md`. Spec at `design-substrate/Spec_Control_Plane_v1_35.md` §19.1.2.*
