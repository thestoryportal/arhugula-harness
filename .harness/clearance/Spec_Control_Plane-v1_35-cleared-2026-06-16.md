---
artifact: design-substrate/Spec_Control_Plane_v1_35.md
version: v1.35
cleared_at: 2026-06-16T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc (B2-spec-2 — MCP_TRUST_GATE_LEVEL_FLOOR per-server trust HITL gate-floor materialization; C-CP-19 NEW §19.1.2; resolves the v1.15 §19.1.1.1 row-3 spec-silence; design-substrate-only, impl deferred to B2-impl)
back_reference:
  - .harness/class_1_fork_b2_spec_2_gate_axis_materialization.md (B2-spec-2 fork — F2-02 + T-B2-2)
  - .harness/class_1_fork_b2_multi_server_mcp_client_reshape.md §5 (F2-02 + T-B2-2 carve-out from B2-spec-1)
  - .harness/r-fs-1-b2-multi-server-mcp-design-v1.md (#579 — §2/§5)
  - .harness/adversarial_review_b2_design.md (F2-02 — the gate-composition consumer the design §5 omitted)
  - design-substrate/Spec_Control_Plane_v1_15.md §19.1.1.1 row 3 (the spec-silence this arc resolves — preserved verbatim)
  - design-substrate/Spec_Control_Plane_v1_2.md §19.1 (composition formula naming per_mcp_server_trust_floor — preserved verbatim)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - spec-writer-style apply pass (Claude, this session) — located the §19.1 canonical body (v1.2 formula + v1.15 §19.1.1 4-axis statement; the §19.1.1.1 row-3 "spec-silent / §0.8-carried" disposition is the deferred content this arc supplies); authored the v1.34→v1.35 delta file (additive NEW §19.1.2 only; §19.1/§19.1.1/§19.3/§19.4/§19.5 + §27.1–§27.8 PRESERVED VERBATIM). Re-grounded the gap in code at HEAD 10b3998d (gate_level_rule.py 3-axis composition + :131-132 U-CP-91 non-override + :104 unconsumed field; Axis.MCP_TRUST already in cp_shared_types.py; hitl_gate_composer.py:462 inert stub; five_axis_composition.py vacuous pass-through).
  - T-B2-2 probe-resolution (NOT council-convened) — the mapping DIRECTION was probe-resolved to floor-only/monotone: the gate is max() over escalation rank so a floor can only RAISE the gate (loosening not expressible), and gate_level_rule.py:131-132 is a LANDED U-CP-91 commitment that mcp_trust is NEVER overridden (loosening would reverse on-main + break the locked T-perm-1 composition). Per CLAUDE.md §10.9 probe-first discipline, surfaced probe-resolved rather than convening a council that would collapse to single-voice (the §10.9 primary-collapse failure mode). C10⊥C11 positions named inline (§13.4 floor).
  - operator AskUserQuestion (2026-06-16) — floor-only direction CONFIRMED + Table A (graduated: L0→DENY, L1→ASK, L2→ASK, L3→AUTO) selected (the genuine remaining HITL-security judgment on a LOCKED axis).
  - harness-adversarial-reviewer (genuine dedicated agent, 26 tool-uses) — APPROVE-WITH-FINDINGS (0 blocking / 0 should-fix-pre-merge / 3 informational). Verified all three high-risk claims TRUE against HEAD 10b3998d (not asserted): X-AL-3-clean (no new contract/ADR/enum/fail-class; Axis.MCP_TRUST already exists; the §19.1 formula named per_mcp_server_trust_floor since v1.2); scope-ONLY-CP CORRECT (runtime v1.49 §14.8.2 step-4c already names mcp_server_trust_tier; v1.51 line 20 carves the wiring to B2-impl; AS §10.3 already forward-points — no runtime/AS/ADR amendment owed); floor table sound (L3→AUTO is the max() identity, never lowers; L0→DENY defense-in-depth; monotone). ZERO phantom cites (every file:line/§ verified byte-exact incl. :131-132 U-CP-91, :462 inert constant, five_axis_composition.py vacuous pass-through). Findings: F3-01 (register the gate_level_rule.py stale-carry docstrings for B2-impl — APPLIED to fork §4); F3-02 (runtime v1.51 "3 of 5" loose — pre-existing on cleared v1.51 / PRESERVED VERBATIM, reconcile at a future runtime delta, NOT this arc); F3-03 (beyond-mvp ledger wrong-name/count — already self-corrected in this PR by the LANDED annotation). Review at .harness/adversarial_review_b2_spec_2.md.
  - out-of-family Codex review (decorrelated, $0 subscription) — staged B2-spec-2 changes "internally consistent"; ZERO substantive finding on the actual change. Its 2 [P2]s targeted the unrelated untracked stragglers (sdlc-research.md + adversarial_review_b3_impl_2/3.md) — correctly EXCLUDED from this commit (only the staged B2-spec-2 files land). Decorrelation validated (Codex + adversarial agent converge on clean-substance).
  - advisor (pre-substantive + pre-done, transcript-aware) — pre-substantive: reframed T-B2-2 from council+AUQ to probe-resolved (the max()-foreclosure + U-CP-91 corroboration), kept the AUQ scoped to the table values; flagged the 3→4 (not 3-of-5) axis framing + the 4-member domain (both honored in the spec text). Pre-done: clear to commit + open PR; confirmed the CP-only scope (B2-spec-2 swaps a value-source for an input the runtime spec already names at §14.8.2 step-4c — unlike B3-spec-1 which introduced a new consumption rule, so no runtime amendment owed). One blocking guard honored: do NOT auto-merge — surface the merge to the operator (substantive design-substrate amendment to a LOCKED T-perm-1 axis; loop off; the T-B2-2 AUQ ratified the content, not the landing).
supersedes:
superseded_by:
---

# Clearance — `Spec_Control_Plane v1.35`

v1.35 is the **B2-spec-2 (gate-axis) leg** of the R-FS-1 B2 multi-server-MCP sub-program — a single additive sub-section **C-CP-19 NEW §19.1.2** committing `MCP_TRUST_GATE_LEVEL_FLOOR: dict[MCPTrustTier, GateLevel]`, the per-server trust **HITL gate**-floor. It resolves the spec-silence carried since v1.15 (§19.1.1.1 row 3: *"per-tier → gate-level mapping is §0.8-carried — owed at follow-on spec-extension arc"*) — materializing the 4th and last unmaterialized axis of the §19.1 multiplicative HITL gate composition (`gate_level()` composed only 3 of 4 axes at HEAD).

**Floor-only / monotone (probe-resolved, NOT council-convened).** The T-B2-2 mapping-direction tension (*does higher trust loosen the gate?*) was foreclosed structurally: the gate is `max()` over escalation rank (a floor can only RAISE the gate), and `mcp_trust_tier` is NEVER overridden (landed U-CP-91 — loosening would reverse on-main + break the locked T-perm-1 composition). Operator-ratified Table A: `L0_REFUSE_REMOTE→DENY`, `L1_SIGNED_PINNED→ASK`, `L2_SANDBOX_ALL→ASK`, `L3_ALLOW_WITH_AUDIT→AUTO` (monotone-decreasing in trust; floor-only — never lowers below blast/persona).

**Scope — gate, distinct from telemetry + dispatch.** v1.35 commits the gate floor (`MCPTrustTier → GateLevel`), orthogonal to the v1.34 §27.8 telemetry projection (`MCPServerTrustLevel → MCPTrustTier`, identity-by-ordinal, span attribute) and to the §27 dispatch trust gate (`PerServerTrustEvaluator`, keyed on `server_name`). All three consume `MCPTrustTier`; only §19.1.2 feeds the `gate_level()` HITL `max()`. §27.1–§27.8 + §19.1/§19.1.1/§19.3/§19.4/§19.5 PRESERVED VERBATIM.

**Caveat for Phase 7 consumers.** Design-substrate only — the gate axis is realized at B2-impl (add `Axis.MCP_TRUST` to `gate_level()` `per_axis_floors`; wire the resolved-host trust into the composer `GateLevelInput.mcp_trust_tier`, retiring the inert `hitl_gate_composer.py:462` stub). ZERO runtime-spec / AS-spec / ADR change (the runtime §14.8.2 step-4c already names `mcp_server_trust_tier` as the composer input). Delta-only file: v1.34 body PRESERVED VERBATIM.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
