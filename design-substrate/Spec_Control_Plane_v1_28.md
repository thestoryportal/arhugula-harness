# Spec: Control Plane — v1.28 (delta over v1.27)

---

## Change-note (v1.27 → v1.28)

**Scope of revision.** Surgical amendment at v1.27 §16.5.6 audit-half stub annotation absorbing operator-ratified Reading (D) hybrid disposition of `.harness/class_2_fork_audit_stub_timestamp_universal_fix_plus_per_tier_annotation.md` (filed at this PR 2026-05-29). Operator AskUserQuestion ratification 2026-05-29:

- **Q1 = (D)** Hybrid disposition: fix `timestamp` at all 3 sibling sites (universal bug per C-CP-16 §16.2 + ADR-D5 §1.4 — `timestamp` is not tier-conditional); annotate `prior_event_hash` + signing as canonical end-state at solo-developer tier per ADR-D5 §1.4 row 1 ("no hash chain required by default ... no signing key required"); team-binding+ tier wiring stays PARTIAL with explicit deferral anchor.

**Trigger.** PR #66 Q2=(iii) carry on `emit_override_audit_entry` stub remediation reopened at session resumption 2026-05-29 (checkpoint "Remaining Work" item #2). Empirical orientation surfaced the gap as a **three-site pattern** at HEAD `8816ce9`:

| # | Site | timestamp at HEAD | prior_event_hash at HEAD |
|---|---|---|---|
| 1 | `harness-cp/src/harness_cp/per_step_override_evaluator.py:225-231` | `""` | `"0" * 64` |
| 2 | `harness-cp/src/harness_cp/sub_agent_gate_level_descent.py:199-206` | `""` | `"0" * 64` |
| 3 | `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py:713 + :753-762` | `""` local var (line 713) → field (line 760) | `_empty_summary_hash()` (`sha256(b"").hexdigest()`) |

The v1.27 §16.5.6 annotation framed remediation as singular at `emit_override_audit_entry` only. v1.28 reframes per multi-site pattern + per-tier disposition.

**Decisive structural constraint for Reading (D) hybrid.** ADR-D5 §1.4 per-persona-tier ledger cryptographic shape table row 1 (solo-developer) commits: "Append-only ledger ... no hash chain required by default ... no signing key required." Sentinel placeholders for `prior_event_hash` + signing IS the spec-canonical posture at the v1.6 MVP solo-developer default tier. Authoring chain state holder + signing wiring at solo-developer tier would be X-AL-3 silent design extension under cover of "the stubs look broken." Hash-chain participation (`prior_event_hash` linkage per C-IS-06) is required at team-binding tier per ADR-D5 §1.4 row 2; signing per C-CP-20 §20.4 is required at multi-tenant-compliance tier per ADR-D5 §1.4 row 3. Both remain DEFERRED at v1.28 per the operator-deployment-time opt-in pattern.

The `timestamp` field is **not tier-conditional** at any persona tier per C-CP-16 §16.2 (declared as `timestamp: str` with docstring "ISO-8601 timestamp"; required at every audit-ledger entry). v1.28 closes the universal `timestamp = ""` bug.

**v1.27 substantive content preserved verbatim except for the scoped §16.5.6 amendment below.** v1.27 §16.5.4 row U-CP-14 + all earlier substantive content preserved verbatim per delta-only-spec-file convention.

**Co-publication this session.** harness-cp impl (`per_step_override_evaluator.py` + `sub_agent_gate_level_descent.py` composer-site clock) + harness-runtime impl (`lifecycle/hitl_gate_composer.py` composer-site clock) + harness-cp tests + harness-runtime tests + workspace `CLAUDE.md` CP spec row bump v1.27 → v1.28 + harness-cp/CLAUDE.md CP spec row bump + fork doc `.harness/class_2_fork_audit_stub_timestamp_universal_fix_plus_per_tier_annotation.md` Status PROPOSING → ✅ APPLIED-AS-(D) + clearance marker.

**ZERO breaking change at signed-payload surfaces.** C-CP-16 §16.2 `CPAuditLedgerEntry` 8-field shape PRESERVED VERBATIM. C-CP-20 §20.4 `CPSignedAuditLedgerEntry` signing contract PRESERVED VERBATIM. `emit_override_audit_entry` at `per_step_override_evaluator.py:208-231` signature surface PRESERVED VERBATIM; ONLY the `timestamp` field value at the body changes (`""` → `datetime.now(UTC).isoformat()`). Same shape at sibling sites.

**ZERO cross-axis cascade.** IS spec UNCHANGED. OD spec UNCHANGED. AS spec UNCHANGED. Runtime spec UNCHANGED. CXA v2.16 UNCHANGED. ADR-D5 v1.4 UNCHANGED (read-only at this arc; faithful citation of pre-existing §1.4 row 1 anchor). ADR-D1/D2/D3/D4/D6/F1/F2/F3/F4/F5 UNCHANGED. ADD v1.3 + PRD v1.1 UNCHANGED. Workflow v1.13 UNCHANGED.

---

## §1 — Amended §16.5.6

### §16.5.6 — Dual-emission discipline (v1.25 PRESERVED VERBATIM at structural surface; NEW v1.28 §16.5.6.X per-tier-conditional stub field disposition supersedes v1.27 §16.5.6 single-site framing)

v1.25 §16.5.6 structural discipline PRESERVED VERBATIM (per v1.27): the §16.5 sibling composer `emit_override_state_ledger_entry` is ADDITIVE alongside the existing `emit_override_audit_entry` (LANDED at `per_step_override_evaluator.py:208-231` per v1.25 `[[impl-time-grounding-pass-pre-merge-revision]]`). The driver firing site at `resolve_step_binding(...):187` MUST invoke BOTH composers per §16.5.6 dual-emission discipline; the audit-half emits the CP-internal `CPAuditLedgerEntry` per §16.2 + §20.4 signing contract; the state-ledger-half emits the IS-anchored `EntryPayload` per §16.5.3.

**v1.27 annotation SUPERSEDED at v1.28** — the v1.27 single-site framing ("audit-half composer ... at `per_step_override_evaluator.py:208-231` is empirically a functional stub at HEAD `d8d091e`") is reframed per the multi-site pattern surfaced at v1.28 empirical orientation. The pattern spans 3 composer sites (see Change-note table above) with per-tier-conditional disposition.

#### §16.5.6.X (NEW at v1.28) — Per-tier-conditional stub field disposition

**Universal-fix scope (all persona tiers, all 3 composer sites).** The `timestamp` field on `CPAuditLedgerEntry` is non-optional per §16.2 (declared `timestamp: str` with docstring "ISO-8601 timestamp"). ADR-D5 §1.4 does NOT carve `timestamp` out at any persona tier. v1.28 closes the universal `timestamp = ""` gap at all 3 composer sites via composer-site clock — `datetime.now(UTC).isoformat()` per Q3=(a) clock-at-composer-site convention established at v1.25 §16.5.4.

**Solo-developer tier-canonical scope (preserved at HEAD).** ADR-D5 §1.4 row 1 explicitly commits: "Append-only ledger ... no hash chain required by default ... no signing key required." At v1.6 MVP solo-developer default tier, the following stub fields are **canonical end-state**, not bugs:

| Field | Solo-dev canonical value | Spec authority |
|---|---|---|
| `prior_event_hash` | `"0" * 64` sentinel (sites 1+2) OR `sha256(b"").hexdigest()` (site 3 `_empty_summary_hash()` per APPROVE response semantic) | ADR-D5 §1.4 row 1 "no hash chain required" |
| Signing | No `CPSignedAuditLedgerEntry` wrap at any of the 3 sites; entries emit as unsigned `CPAuditLedgerEntry` | ADR-D5 §1.4 row 1 "no signing key required" |

The `prior_event_hash` sentinel **carries semantic content at solo-developer tier**: it marks "no prior chain link exists" — the canonical reading of ADR-D5 §1.4 row 1's "no hash chain required by default."

**Team-binding+ tier wiring DEFERRED (PARTIAL).** ADR-D5 §1.4 row 2 (team-binding) commits "Hash-chained ledger ... with `prior_event_hash` linkage per F2 state-ledger entry shape"; ADR-D5 §1.4 row 3 (multi-tenant-compliance) commits "Hash-chained ledger + cryptographic signature per ledger entry." Closure at team-binding+ tier requires:

1. **CP-audit chain state holder** — a NEW substrate carrier tracking `prior_event_hash` sequence per persona-tier × deployment scope per ADR-D5 §1.4 row 2 / row 3. NO such substrate exists at HEAD `8816ce9`. Not authored at v1.28.
2. **Threading at 3 composer sites** — `per_step_override_evaluator.py` + `sub_agent_gate_level_descent.py` + `hitl_gate_composer.py` must each consume the chain state holder. Not threaded at v1.28.
3. **Signing wiring per C-CP-20 §20.4** — `CPSignedAuditLedgerEntry` wrap at multi-tenant-compliance tier via `f5_signing_key_resolution.py` substrate (LANDED). Not invoked at any of the 3 composer sites at HEAD. Not wired at v1.28.

Closure shape at team-binding+ tier is the **operator-deployment-time opt-in pattern** (mirror precedent: AS-8d batch-31, OD-5 batch-32, OD-6 batch-33). Operator binding to team-binding or multi-tenant-compliance tier requires substrate authoring + threading + signing wiring at a separate apply-pass arc; v1.28 documents the deferral with explicit anchor.

**`override` + `actor` input semantics at `emit_override_audit_entry` PRESERVED.** Per v1.27 framing: the ignored inputs (`_ = (override, actor)` at line 224) are preserved at v1.28 — C-CP-16 §16.2 audit-entry shape does not include an `actor` field; `override`'s fields are surfaced at the caller's `StepEffectiveBinding` per line 193-205, not into the audit entry. Future widening of the audit-entry shape to carry override metadata is a separate spec amendment arc.

**Sub-species 10 partial-applicability acknowledgement.** Workflow v1.12 §7.4.7.2 sub-species 10 `gate-text-stale-vs-production-landings` applies to the solo-developer-tier-canonical scope at v1.28: the v1.27 annotation gate-text framed `prior_event_hash="0"*64` as universally wrong (functional gap); ADR-D5 §1.4 row 1 makes it spec-canonical at solo-developer tier (the v1.6 MVP default). This is NOT a full sub-species 10 closure (timestamp gap is real + universal); it is a partial-applicability acknowledgement that the gate-text framing was over-broad. Distinct from prior sub-species 10 closures (OD-1 batch-37 + OD-7 batch-38 + IS-4 batch-39 + CP-12 batch-40 + CP-23 batch-41) which were full reclassifications.

**Status posture.** v1.28 closes the universal `timestamp` gap + clarifies per-tier disposition. Team-binding+ tier wiring carries forward as bounded-residual per X-AL-2. The `emit_override_audit_entry` + sibling sites status at v1.28 close:

- **Solo-developer tier (v1.6 MVP default):** FUNCTIONALLY COMPLETE at HEAD post-v1.28 apply (timestamp populated; sentinel `prior_event_hash` canonical per ADR-D5 §1.4 row 1; no signing required).
- **Team-binding tier:** PARTIAL — chain wiring deferred to operator-deployment-time opt-in arc.
- **Multi-tenant-compliance tier:** PARTIAL — chain wiring + signing wiring deferred to operator-deployment-time opt-in arc.

---

## §2 — Adjacent observations (NOT patched per FM-2)

- **(a)** v1.27 §16.5.6 v1.27 annotation framed the `emit_override_audit_entry` site as the singular remediation target. v1.28 §1 supersedes that framing per multi-site empirical orientation. v1.27 file body PRESERVED VERBATIM; downstream readers apply v1.28 §1 reframe when interpreting v1.27 §16.5.6 single-site framing.

- **(b)** Three composer sites with structurally-identical `timestamp = ""` pattern surface a workspace-pattern candidate at workflow v1.13 §7.4.7.2: `multi-site-pattern-not-surfaced-at-original-deferral-arc` — when PR #66 ratified Q2=(iii) singularly framed, the empirical multi-site pattern was not in scope at the original ratification. The deferred carry's scope was under-specified at the original arc. Cardinality 1; awaits second instance before catalogue authoring.

- **(c)** `hitl_gate_composer.py:761` `prior_event_hash=_empty_summary_hash()` uses a different sentinel (`sha256(b"")`) than sites 1+2's `"0"*64`. Both are spec-defensible at solo-developer tier (ADR-D5 §1.4 row 1 commits "no hash chain required" — does not commit a specific sentinel form). Convention divergence is acknowledged at v1.28 §1 without canonicalizing one sentinel form. Future C-CP-16 amendment could canonicalize the solo-developer-tier sentinel; deferred.

- **(d)** `sub_agent_gate_level_descent.py:199-206` audit construction site was NOT cited at v1.27 single-site framing. v1.27 framing inherited the original PR #65 fork doc framing which surfaced ONLY `per_step_override_evaluator.py:208-231`. Empirical orientation at v1.28 surfaced sites 2+3. Mirrors `[[advisor-before-substantive-work-for-cross-axis-blockers]]` pattern at 51 applications — pre-substantive grep against `CPAuditLedgerEntry(` exhaustive construction call sites caught the under-specification before authoring.

---

## §3 — Status

Surgical amendment at v1.27 §16.5.6 audit-half stub annotation absorbing operator-ratified Reading (D) hybrid disposition at AskUserQuestion 2026-05-29. Apply pass: this arc (delta-only spec file co-published with harness-cp impl + harness-runtime impl + tests + fork doc + workspace `CLAUDE.md` CP spec row bump per workspace `CLAUDE.md` §11.4 bundled-absorption).
