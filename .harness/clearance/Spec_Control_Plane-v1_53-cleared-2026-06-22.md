---
artifact: design-substrate/Spec_Control_Plane_v1_53.md
version: v1.53
cleared_at: 2026-06-22T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-spine-ledger (committed-invariant amendment, operator-ratified — the CP half of B-HITL-PLACEMENT-PER-STEP-LOOSEN. NEW LoosenablePlacementKind one-member enum [SUB_AGENT_BOUNDARY only — PRE_ACTION/VALIDATOR_ESCALATION structurally unrepresentable] + additive StepOverride.removed_placements + StepEffectiveBinding.removed_placements [frozenset, default empty] + resolve_step_binding propagation + the §6.2/§17.1/§19.1 per-step SUB_AGENT_BOUNDARY removal semantics. Relaxes the monotone-HITL §17.1 "all cells" + §19.1 persona-tier floor — at SOLO only, per-step opt-in, FLOOR-CLAMPED [persona + LOCAL_MUTATION-blast override-able; per_tool/mcp_trust/blast-above-local-mutation NEVER override-able → high-blast/deny-tier/untrusted-MCP REFUSES the removal], auto-audited fail-closed. PREVENTIVE→DETECTIVE residual operator-consciously-accepted. Default empty ⇒ byte-identical + monotone. Provenance rides binding.model_dump [§6.6, the v1.38 agent_role precedent] — NO new §5.2/IS hash field. The runtime hitl_gate_composer step-4c removal branch + placement-removed audit are impl, NOT a runtime-spec contract change.)
back_reference:
  - .harness/r-fs-1-final-closure-plan.md (arc (b) — the C10⊥C11 dyadic council + advisor design this CP v1.53 delta executes; operator AUQ "Ratify as designed" 2026-06-22)
  - .harness/beyond-mvp-capability-boundary-ledger.md (B-HITL-PLACEMENT-PER-STEP-LOOSEN spine BUILT note)
  - design-substrate/Spec_Control_Plane_v1_52.md (the §6.1/§6.2/§6.6 + §17.1 + §19.1 + §19.5 body this extends, PRESERVED VERBATIM)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - C10 action-safety + C11 operator-loop (CP-axis dyadic council, dedicated agents, independent → cross-read — the §13.4 worked-example dyad) at design pass (#709)
  - advisor (full-transcript) — architecture vet pre-impl (the composer-not-fold site + persona_floor_override reuse + solo-only) + the non-vacuity / LOCAL_MUTATION-cell / provenance / fail-closed / audit-honesty sharpenings
  - out-of-family Codex (decorrelated) — pre-merge on the diff (pending at clearance authoring)
  - operator AskUserQuestion ratification 2026-06-22 ("Ratify as designed" — narrow mechanism + conscious acceptance of the bounded preventive→detective residual)
  - standing FULL-SPEC operator directive 2026-06-12 (committed-invariant amendment authorized in principle 2026-06-22)
supersedes:
superseded_by:
---

# Clearance — `Spec_Control_Plane v1.53`

v1.53 is the CP half of the R-FS-1 standalone arc **`B-HITL-PLACEMENT-PER-STEP-LOOSEN`** — the operator-ratified committed-invariant relaxation of the monotone-HITL §17.1/§19.1 floor, enabling an opt-in per-step removal of a `SUB_AGENT_BOUNDARY` gate at solo-developer tier.

**What changed.** NEW `LoosenablePlacementKind` `StrEnum` with **exactly one member** (`SUB_AGENT_BOUNDARY`; `PRE_ACTION`/`VALIDATOR_ESCALATION` structurally unrepresentable — the §19.1 floor-evaluation bypass-seam + the §14.15-path wrong-layer, foreclosed at the type) (§17.1); additive `StepOverride.removed_placements: frozenset[LoosenablePlacementKind] = frozenset()` (§6.1); additive `StepEffectiveBinding.removed_placements` carried by `resolve_step_binding` (§6.2); the composer-side removal semantics (§6.2/§19.1/§14.8.2 step 4c).

**The committed invariant amended + the residual (honest).** This is the FIRST per-step override that can REDUCE gating. It relaxes the §17.1 "all cells" + §19.1 `max()` persona-tier floor, at SOLO only, per-step opt-in. Removing a `SUB_AGENT_BOUNDARY` gate downgrades that step's oversight PREVENTIVE→DETECTIVE (the mandatory fail-closed audit is the remaining containment) — a real safety-posture change the operator consciously accepted at ratification ("Ratify as designed", 2026-06-22). Bounded by: solo-only (team = registered follow-on, multi-tenant structurally foreclosed); the FLOOR-CLAMP (overrides only the persona floor + the LOCAL_MUTATION blast cell; `per_tool`/`mcp_trust` never override-able per U-CP-91 + `blast_radius` above local-mutation clamp it → a high-blast / deny-tier-tool / untrusted-MCP dispatch REFUSES the removal, the gate fires); opt-in + every applied removal auto-audited fail-closed.

**The mechanism is the NOT-a-fold directive.** The removal is a binding-carried directive honoured at the `SUB_AGENT_BOUNDARY` composer (mirroring §19.5 `HITLAutoApprovePolicy`'s floor-cell lowering at the `PRE_ACTION` composer), NOT a `fold_step_hitl_placements` mutation (the ADD-only fold is UNTOUCHED — a destructive pre-composer deletion would prevent the floor-clamp). Default empty ⇒ byte-identical + monotone. Provenance rides `binding.model_dump` (§6.6, the v1.38 `agent_role` precedent) — NO new C-IS-05 §5.2 hash field, NO IS-spec change. No new ADR / fail-class / CXA edge; the `placement-removed` audit `response` is a free-string, OD ingestion unaffected.

**Reviewed during clearance (verified by execution).** NON-VACUITY witness (advisor's blocking check): with the §19.5 persona-floor knob OFF (floor LIVE), a per-step removal skips THIS step's SUB_AGENT_BOUNDARY gate while an unremoved sibling still gates — the genuine per-step delta over §19.5's global policy. Plus: floor-clamp refusal at EXTERNAL_* blast + at an untrusted MCP host + at a deny-tier per_tool; LOCAL_MUTATION removal effective; non-solo no-op; fail-closed on unresolvable floor; the `placement-removed` audit shape (distinct from `approve`); full-chain carrier propagation (`StepOverride → resolve_step_binding → binding`) + `model_dump` provenance; negative control (empty ⇒ byte-identical). harness-cp 1175 passed + 1 xfailed; harness-runtime non-e2e 2050 passed; pyright 0/0/0 (src + changed tests); ruff clean.

## Notes

- Phase 7 consumers may rely on this version as canonical after the bundled harness-cp + harness-runtime impl + tests land together (`merge_commit` pinned at the post-merge refresh).
- No paired runtime-spec delta — the runtime composer change is impl, not a runtime contract amendment.
