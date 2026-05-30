# Class 2 fork — CP audit-stub timestamp universal fix + per-tier annotation

**Filed:** 2026-05-29
**Status:** APPLIED-AS-(D) bundled-absorption
**Class:** 2 (in-execution operator decision; bundled-absorption per workspace CLAUDE.md §11.4)
**Trigger:** PR #66 Q2=(iii) IN-SCOPE-BUT-MARK-DEFERRED carry on `emit_override_audit_entry` stub remediation; reopened at /context-restore session 2 2026-05-29 when checkpoint "Remaining Work" item #2 was picked.

---

## §1 Reframe from Q2=(iii) original framing

PR #66 Q2=(iii) framed the deferred remediation as **singular**: "audit-half stub remediation IN-SCOPE-BUT-MARK-DEFERRED — annotate `emit_override_audit_entry` stub functional gap at §16.5.6 + per-axis CLAUDE.md + plan body; close at follow-on apply-pass arc."

Empirical orientation at this arc surfaces the gap as a **three-site pattern** with **persona-tier-conditional disposition** per ADR-D5 §1.4:

| # | Site | timestamp | prior_event_hash | gate_level | response |
|---|---|---|---|---|---|
| 1 | `harness-cp/src/harness_cp/per_step_override_evaluator.py:225-231` | `""` ❌ | `"0"*64` ✓ at solo-dev | `AUTO` ✓ | `"approve"` ✓ |
| 2 | `harness-cp/src/harness_cp/sub_agent_gate_level_descent.py:199-206` | `""` ❌ | `"0"*64` ✓ at solo-dev | dynamic ✓ | `"approve"` ✓ |
| 3 | `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py:713/753-762` | `""` ❌ | `_empty_summary_hash()` ✓ at solo-dev | `AUTO` ✓ | dynamic ✓ |

Universal gap (all 3 sites): **`timestamp = ""`** — not tier-conditional; ADR-D5 §1.4 + C-CP-16 §16.2 mandate ISO-8601 timestamp at every persona tier.

Tier-conditional fields (`prior_event_hash`, signing): ADR-D5 §1.4 row 1 explicitly states "solo-developer ... no hash chain required by default ... no signing key required." Sentinel placeholders are spec-canonical at the v1.6 MVP solo-developer default tier; remediation owed at team-binding+ tier deployment.

## §2 Disposition (D) hybrid bundled-absorption

Operator AskUserQuestion ratification 2026-05-29:

- **Q1 = (D)** Hybrid: fix `timestamp` at all 3 sibling sites (unambiguous bug per ADR-D5 §1.4 — universally required across all tiers); annotate `prior_event_hash` + signing as canonical end-state at solo-developer tier per ADR-D5 §1.4 row 1; team-binding+ tier wiring stays PARTIAL with explicit deferral anchor.

### §2.1 What this arc closes

1. **Universal `timestamp = ""` bug at 3 sites** — replaced with composer-site clock (`datetime.now(UTC).isoformat()`). Spec authority: C-CP-16 §16.2 declares `timestamp` as a non-optional field on the per-response audit-ledger entry shape; ADR-D5 §1.4 does NOT carve out timestamp at solo-developer tier (only hash chain + signature are tiered).
2. **PR #66 Q2=(iii) carry** — closed via the spec annotation at §3 below acknowledging the universal timestamp fix as the only field with non-tier-conditional remediation owed at the v1.6 MVP scope.
3. **Multi-site pattern documentation** — original singular framing at PR #66 superseded; pattern is uniform across 3 composer sites.

### §2.2 What this arc explicitly does NOT close

1. **Hash-chain participation at team-binding+ tier** — `prior_event_hash` sentinel preserved at all 3 sites. Real CP-audit chain state holder + chain construction per C-IS-06 is owed at the operator deployment-binding arc at team-binding tier per ADR-D5 §1.4 row 2.
2. **Signing per C-CP-20 §20.4** — no signing wiring at any of the 3 sites. Sentinel `CPAuditLedgerEntry` (unsigned) is canonical at solo-developer per ADR-D5 §1.4 row 1; signing wiring at team-binding+ tier per ADR-D5 §1.4 row 2-3 is owed at the operator deployment-binding arc.
3. **`override` + `actor` input semantics at `emit_override_audit_entry`** — preserved as ignored (`_ = (override, actor)`) per the v1.27 §16.5.6 annotation. The C-CP-16 §16.2 audit-entry shape does not include an `actor` field; `override`'s fields are surfaced into the `StepEffectiveBinding` per the caller at line 193-205, not into the audit entry. The ignored inputs are a signature-stability concession; future widening of the audit-entry shape to carry override metadata is a separate spec amendment arc.

### §2.3 Distinct from Reading (A) full-close

Reading (A) (Class 1 fork → ratify → apply, with CP-audit chain state holder + thread to 3 sites + signing wiring) is foreclosed at this arc per (D) ratification. Rationale:

- (A) is a multi-session arc requiring a NEW CP-axis substrate module (chain state holder) + spec amendments at C-CP-16 / C-CP-20 / threading discipline at 3 composer surfaces.
- ADR-D5 §1.4 row 1 makes (D) the spec-canonical posture at solo-developer tier — the v1.6 MVP scope. Authoring chain + signing at solo-developer tier would be X-AL-3 silent design extension under cover of "the stubs look broken."
- Tier-aware remediation aligns with workspace precedent for operator-deployment-time opt-in (AS-8d + OD-5 + OD-6 sub-species 7.deployment-time-opt-in-gate).

## §3 Co-published artifacts at this arc

| Artifact | Change shape |
|---|---|
| `design-substrate/Spec_Control_Plane_v1_28.md` | NEW delta over v1.27 — extends §16.5.6 annotation with §16.5.6.X per-tier-conditional stub field disposition |
| `harness-cp/src/harness_cp/per_step_override_evaluator.py:225-231` | `timestamp=""` → `timestamp=datetime.now(UTC).isoformat()` |
| `harness-cp/src/harness_cp/sub_agent_gate_level_descent.py:199-206` | `timestamp=""` → `timestamp=datetime.now(UTC).isoformat()` |
| `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py:713` | `timestamp = ""` placeholder → `timestamp = datetime.now(UTC).isoformat()` |
| `harness-cp/tests/test_per_step_override_evaluator.py` | NEW: assert `audit_entry.timestamp` is non-empty + parses as ISO-8601 |
| `harness-cp/tests/test_sub_agent_gate_level_descent.py` | NEW: same assertion at sub-agent descent audit entry |
| `harness-runtime/tests/test_lifecycle_hitl_gate_composer.py` | NEW: same assertion at HITL gate composer audit entry |
| Workspace `CLAUDE.md` §2.3 CP spec row | Version bump v1.27 → v1.28 |
| `harness-cp/CLAUDE.md` §1.2 spec row | Version bump |

## §4 Cross-axis cascade

ZERO. The arc is intra-CP-axis (composer + runtime); ADR-D5 §1.4 anchor is read-only at this arc. No OD/AS/IS/CXA/ADR/ADD/PRD amendment owed.

## §5 X-AL-3 silent design extension audit

ZERO X-AL-3 risk:

- Timestamp fix at impl is byte-exact alignment with C-CP-16 §16.2 field declaration (non-optional `timestamp: str` with docstring "ISO-8601 timestamp"). Production conforms to spec — no spec extension.
- Per-tier annotation at spec v1.28 §16.5.6.X is read-from-ADR-D5 §1.4 row 1 (not authored at this arc; faithful citation of pre-existing anchor).
- Team-binding+ wiring DEFERRED with explicit anchor at §16.5.6.X; no silent absorption of the gap.

## §6 Status

✅ **APPLIED-AS-(D)** — bundled-absorption arc per workspace CLAUDE.md §11.4. Mixed-posture PR (Phase 7 impl at 3 src files + design-phase spec v1.28 + tests + back-flow doc); X-AL-3 CI guard satisfied via this fork doc co-published in the same PR.

## §7 Reference

- ADR-D5.md §1.4 per-persona-tier ledger cryptographic shape table (v1.4 lineage) — solo-developer row 1 "no hash chain required by default ... no signing key required"
- CP spec v1.27 §16.5.6 audit-half stub annotation (predecessor; this arc's spec v1.28 extends)
- PR #66 Q2=(iii) ratification (predecessor deferral)
- Workspace memory `[[feedback-checkpoint-remaining-work-is-advisory-not-authoritative]]` — fourth stale-pick at this session; the (D) hybrid scope reduction was caught at advisor 51st application before authoring against the broader "audit-stub remediation" framing
- `[[advisor-before-substantive-work-for-cross-axis-blockers]]` cardinality 51
