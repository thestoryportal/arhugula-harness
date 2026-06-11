---
artifact: design-substrate/Spec_Operational_Discipline_v1_29.md
version: v1.29
cleared_at: 2026-06-12T00:00:00-06:00
clearance_type: spec-writer-apply-pass
back_reference:
  - .harness/r-pm-1-prompts-management-design-v1.md §4.4 / §6 row #4 (the per-tier governance layer of the prompts-management cascade)
  - Project_Roadmap_v1.md §5.17 R-CC-1 / §5.16 R-PM-1 (capability-completion program; prompts-management forward arc)
  - design-substrate/Spec_Control_Plane_v1_31.md §29 (the selection layer this governs); design-substrate/Spec_Information_Substrate_v1_7.md §5.3 (the versioned store); design-substrate/Spec_Harness_Runtime_v1.md §14.5.2 (the injection layer; delta-only file, internal title v1.44)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - advisor() pre-substantive decision-fork (caught the redaction-second-source-of-truth block → derive-from-gradient; resolved the approval wire-vs-defer fork via the reconciler-site discriminator). NOTE pre-done advisor() unavailable (overloaded this turn) — substituted the two decorrelated reviews below, both of which ran the tests + pyright themselves.
  - harness-adversarial-reviewer (dedicated agent, 32 tool-uses, pre-merge) — APPROVE-WITH-CLASS-3; 0 Class-1/2; verified all 3 load-bearing design claims by execution incl. a positive-control non-breaking run; 2 doc-nits (F1-01 clearance cite-path → FIXED; F1-02 §3.2 plan-coverage count = pre-existing scoped-correct, left). Report: `.harness/r-pm-1-pr4-adversarial-review.md`.
  - just codex-review (out-of-family, decorrelated) — ran targeted pytest + pyright; "no discrete correctness issues that should block the patch".
  - empirical impl-grounding pass (gen_ai.system_instructions ∈ DEFAULT_OFF; no span-producer / no change-event producer at HEAD; persona_tier in scope at stage-0 reconciler)
  - mode-agnostic / Phase-7 bundled-absorption posture (workspace CLAUDE.md §11.4)
supersedes:
superseded_by:
---

# Clearance — `Spec_Operational_Discipline v1.29`

v1.29 introduces NEW contract **C-OD-34 — per-persona-tier prompt-governance posture**, the layer-(d) governance wrapper of the R-PM-1 prompts-management cascade (injection #506 / versioning #508 / selection #509). It declares the per-tier *approval* posture for the prompt artifact class across the bridging-arc `PersonaTier` ladder: `solo-developer` no approval (local-first); `team-binding` + `multi-tenant-compliance` require operator attestation (a shared / tenant prompt is a governed artifact).

**Composition, not duplication.** The contract declares only the genuinely net-new *approval* dimension. The *redaction* dimension is NOT re-declared — the prompt-content attribute class (`gen_ai.system_instructions`) is already a `DEFAULT_OFF_CONTENT_ATTRIBUTES` member (C-OD-12 §12.1), governed per-tier by the existing `PER_PERSONA_TIER_REDACTION` gradient (C-OD-13 §13.1). C-OD-34 *derives* the prompt-class redaction posture (`prompt_content_redaction_enforced` ≡ `not toggleable`) from that single source of truth (the advisor-caught second-source-of-truth fix). No new ADR (additive posture composing ADR-D5 v1.3 §1.5 + C-OD-13 + the R-CL-P3 #481 tier-distinct proof). No edit to any §C-OD-01..§C-OD-33 surface.

**Enforcement is a real gate at a real site.** The approval posture is enforced runtime-deferred (parallel to CP §29.3) at the bootstrap stage-0 selection reconciler: at a binding tier, a *selection-driven* active prompt version whose `version_sha` is absent from `RuntimeConfig.approved_prompt_version_shas` is fail-loud `RT-FAIL-PROMPT-VERSION-UNAPPROVED` (→ `BootstrapFailure` at PREAMBLE). Inert at solo-developer + for inline-only / no-match deployments — non-breaking for all existing fixtures and the SOLO-default live e2e path. Governs only the versions the CP selection layer drives (the real currently-reachable governed action); inline-only-prompt governance + prompt-version-delta approval are documented re-open triggers (no producer at HEAD).

This is a Phase-7 bundled-absorption arc (design-substrate spec delta + `harness-od/src` + `harness-runtime/src` landed together), legitimate per workspace `CLAUDE.md` §11.4, mirroring the cascade PR #1/#3 shape (axis spec amendment + its runtime consumer).

Verification: `harness-od/tests/test_prompt_governance_gradient.py` (7 — posture totality + non-vacuous tier-distinctness + redaction-derivation + prompt-class-is-default-off); `harness-runtime/tests/test_prompt_governance_enforcement.py` (8 — gate logic incl. non-vacuous tier-distinctness); `harness-runtime/tests/test_bootstrap.py` (2 e2e — binding-tier unapproved fail-loud + approved passes through `run_bootstrap`). Full suites: harness-od 919 + harness-runtime 1613 green; live Ollama selection→injection e2e non-regressed (gate inert at SOLO). pyright strict 0/0/0 on changed files.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- C-OD-34 introduces no new CXA edge; the PROMPTS(IS)→selection(CP)→injection(runtime)→governance(OD) seam is the cascade PR #5 deliverable (§C-OD-34.4).
- See `.harness/clearance/README.md` for marker discipline.
