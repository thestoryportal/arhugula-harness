---
artifact: design-substrate/Cross_Axis_Composition_Document_v2_20.md
version: v2.20
cleared_at: 2026-06-12T01:30:00-06:00
clearance_type: cxa-additive-forward-capability-registration
back_reference:
  - .harness/r-pm-1-prompts-management-design-v1.md §6 row #5 (the CXA-registration layer of the prompts-management cascade — "after the producers exist")
  - Project_Roadmap_v1.md §5.16 R-PM-1 / §5.17 R-CC-1 (capability-completion program; prompts-management forward arc — this PR closes the cascade)
  - design-substrate/Cross_Axis_Composition_Document_v2_19.md (predecessor — §2.1 matrix + §2.2 + §2.3.1–§2.3.7 + §2.4 + §3 preserved verbatim; v2.20 is purely additive)
  - design-substrate/Spec_Control_Plane_v1_31.md §29 (C-CP-29 prompt-selection, edge-1 consumer / edge-2 producer); design-substrate/Spec_Information_Substrate_v1.md §5.3 (C-IS-05 versioned store, edge-1 producer; delta-only file, internal version v1.7); design-substrate/Spec_Operational_Discipline_v1_29.md C-OD-34 (governance, edge-2 consumer); design-substrate/Spec_Harness_Runtime_v1.md §14.5.2 (injection seam; delta-only file, internal title v1.44)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - pre-substantive empirical grounding (direct read at HEAD) — confirmed each axis is pure (CP imports no IS; OD imports no CP/IS) and runtime is the sole composition site; derived the 2-edge enumeration + 2 deliberate non-edges
  - advisor pass 2026-06-12 (pre-authoring) — confirmed the 2-edge set (CP→IS + OD→CP, both R-class, directions respect acyclicity), the redaction/injection non-edges, and the frozen-baseline Option B structure; flagged the "materialized-live not Phase-2-deferred" labelling + the all-citation-sites-in-one-PR discipline + leave-per-axis-CLAUDE.md-alone
  - harness-adversarial-reviewer (dedicated general-purpose agent adopting the SKILL.md, 17 tool-uses, pre-merge) — APPROVE-WITH-CLASS-1; verified by direct read all import-purity claims (CP imports no IS; OD imports no CP/IS; the OD approval gate takes no prompt_manifest param → the OD→IS-for-approval non-edge holds at function-body level → no missed third edge) + the 107+2=109 arithmetic at every citation site + the frozen 37/48/22 sub-split matches v2.19 verbatim; F1-01 (clearance back_reference IS-spec filename token Spec_Information_Substrate_v1_7.md → _v1.md, delta-only convention) → FIXED pre-merge
  - just codex-review (out-of-family, decorrelated) — caught P2: §0.7(c) over-claimed "✅ this PR" for the roadmap-surface refresh (those files are NOT in this diff; the refresh is a post-merge §12.2 step) → FIXED pre-merge (§0.7(c) honestly defers; (b-bis) claude-artifact-pointers entry added)
  - advisor pass (pre-done — pending final call this arc)
  - design-phase posture session 2026-06-12 (operator directed the closure / R-CC-1 track)
supersedes: (none — additive; does not supersede the v2.19 plan-canonical baseline, which is frozen verbatim)
---

# Clearance — `Cross_Axis_Composition_Document v2.20`

v2.20 is an **additive forward-capability registration** that records the **R-PM-1 prompts-management composition** (`PROMPTS(IS) → selection(CP) → injection(runtime) → governance(OD)`) as a new, delineated cross-axis seam family at §2.3.8. It closes the R-PM-1 cascade (PR #5 of 5) — the CXA-registration layer, registered after the producers (cascade PR #1–#4: #506/#508/#509/#510) exist, per `[[r-cxa-seam-wiring-is-producer-discovery]]`.

**Two registered edges, both runtime-mediated + materialized-live at HEAD:**

1. **CP→IS** — CP prompt-selection (C-CP-29) consumes the IS versioned store (C-IS-05 §5.3): the runtime `reconcile_active_prompt_via_selection` resolves the CP-selected `version_sha` to its authored `PromptManifest.versions` member (content↔hash coherence); fail-loud `RT-FAIL-PROMPT-SELECTION-UNAUTHORED`.
2. **OD→CP** — OD prompt-governance (C-OD-34) gates the CP-selection-driven active version: the runtime stage-0 `enforce_prompt_version_approval` checks the selected `version_sha` against `RuntimeConfig.approved_prompt_version_shas` at binding tiers; fail-loud `RT-FAIL-PROMPT-VERSION-UNAPPROVED`.

Both are classed **`R-live`** — runtime-mediated composition (by the ADR-F1-faithful axis-purity design: CP imports no IS, OD imports no CP/IS; the runtime is the sole composition site), **materialized and e2e-proven at HEAD** (incl. live Ollama selection→injection), NOT Phase-2-deferred.

**Frozen-baseline structure (the load-bearing discipline).** The plan-canonical §2.1 aggregate (**107** = 37 genuine + 48 convention + 22 phase-2-runtime) is preserved **verbatim** — the prompts edges are delineated, not folded into the audited 7c buckets. This deliberately avoids recreating the count-conflation defect class that the entire v2.18→v2.19 patch existed to fix, and honours the U-\* (plan-unit) vs C-\* (contract) keying mismatch (the prompts edges have no plan-unit decomposition — they landed as a post-MVP spec-amendment cascade). Reported total: **107 plan-canonical + 2 R-PM-1 forward-capability = 109**.

**Two deliberate non-edges (excluded after grounding):** OD redaction (`prompt_content_redaction_enforced`) is *derived* from the existing `PER_PERSONA_TIER_REDACTION` gradient — composition not duplication, no new edge; translate-time injection is runtime-internal (runtime is not one of the four axes), not an axis→axis edge.

ZERO change to §2.1 / §2.2 / §2.3.1–§2.3.7 / §2.4 / §3 (all v2.3 / v2.17 / v2.19-canonical, preserved verbatim). ZERO production-code change (the producers already landed at #506/#508/#509/#510). ZERO new ADR (the composition is ADR-F1-faithful per the R-PM-1 design).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed. Canonical reading: plan-canonical §2.1 matrix = v2.19-canonical (aggregate **107**; genuine 37 / convention 48 / phase-2-runtime 22), FROZEN; plus the §2.3.8 R-PM-1 prompts forward-capability family = **2** `R-live` edges (CP→IS + OD→CP). **Total = 109.**
- Does NOT supersede the v2.19 marker — v2.20 is purely additive; the v2.19 plan-canonical baseline remains canonical verbatim.
- Per-axis `harness-{cp,od,is}/CLAUDE.md` cross-axis inventories left untouched (advisor scope discipline; v2.19 §0.8(d) precedent) — they enumerate the plan-canonical buckets, which are unchanged.
- See `.harness/clearance/README.md` for marker discipline.
