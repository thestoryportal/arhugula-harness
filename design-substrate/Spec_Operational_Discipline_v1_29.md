# `Spec_Operational_Discipline` v1.29 — delta over v1.28

**Filed:** 2026-06-12
**Authoring authority:** Phase 7 — R-PM-1 prompts-management cascade PR #4 (per-tier / persona prompt governance; `.harness/r-pm-1-prompts-management-design-v1.md` §4.4 / §6 row #4)
**Predecessor:** `Spec_Operational_Discipline_v1_28.md` (v1.28 — §C-OD-09 §9.3 bounded-buffer implementer-discretion closure)
**Revision shape:** Delta-only spec file per workspace `CLAUDE.md` §2.3 OD spec row convention. v1.28 + v1.27 + ... + v1 file bodies PRESERVED VERBATIM. v1.29 carries this change-note + the NEW §C-OD-34 contract only.

---

## Change-note (v1.28 → v1.29)

**Introduces (ADDITIVE).** A NEW top-level contract **C-OD-34 — per-persona-tier prompt-governance posture**. It declares the per-tier *approval* posture for the prompt artifact class (the operator-supplied active prompt that the R-PM-1 cascade injects [PR #1, runtime spec v1.44 §14.5.2], versions [PR #2, IS spec v1.7 §5.3], and selects [PR #3, CP spec v1.31 §29]). C-OD-34 is the layer-(d) governance wrapper of that landed surface.

**Composition, not duplication** (R-PM-1 design §4.4; CLAUDE.md §4 one-source-of-truth). The contract declares **only the approval dimension** — the genuinely net-new governance surface. The **redaction dimension is NOT re-declared**: the prompt-content attribute class (`gen_ai.system_instructions`) is already a member of the C-OD-12 §12.1 `DEFAULT_OFF_CONTENT_ATTRIBUTES` default-off set, and is therefore already governed per-tier by the C-OD-13 §13.1 `PER_PERSONA_TIER_REDACTION` gradient (the single source of truth for per-tier content-capture posture). C-OD-34 *derives* the prompt-class redaction posture from that gradient (`prompt_content_redaction_enforced`); it does not restate it. A re-declared `redaction_required` flag would be a second source of truth that could drift from the gradient — explicitly avoided.

**No new ADR.** Additive OD posture composing the existing persona-tier ladder (ADR-D5 v1.3 §1.5) with the existing redaction gradient (C-OD-13) and the R-CL-P3 (#481) tier-distinct posture proof. No foundational decision is touched (Option 1 of the R-PM-1 design — distributed per-axis amendments, no new ADR/spec).

**No existing contract changed.** ZERO edit to any §C-OD-01..§C-OD-33 surface; ZERO new namespace; ZERO change to the C-OD-12/C-OD-13 redaction surfaces (C-OD-34 *consumes* them read-only). The approval *enforcement* is a runtime-deferred check (parallel to CP spec v1.31 §29.3's runtime-deferred store-membership check) — see §C-OD-34.3.

---

## §C-OD-34 — Per-persona-tier prompt-governance posture (NEW)

### §C-OD-34.1 Posture declaration

The prompt artifact class carries a per-persona-tier governance posture across the bridging-arc persona ladder (`PersonaTier`: `solo-developer` / `team-binding` / `multi-tenant-compliance`; ADR-D5 v1.3 §1.5). The posture declares one dimension — **approval** — as a total map over the closed 3-value enum:

| Persona tier | `approval_required` | Rationale |
|---|---|---|
| `solo-developer` | `False` | Local-first; a single operator's prompt is not a shared artifact — minimal governance burden (C11). |
| `team-binding` | `True` | A shared prompt is a team artifact; activating a prompt version is a governed action requiring operator attestation. |
| `multi-tenant-compliance` | `True` | A prompt may carry tenant-specific content; activation requires attestation (and the redaction gradient already applies — §C-OD-34.2). |

Carrier: `harness-od/src/harness_od/prompt_governance_gradient.py` — `PromptGovernancePosture` (frozen Pydantic; fields `persona_tier` + `approval_required` ONLY) + `PER_PERSONA_TIER_PROMPT_GOVERNANCE` (the total map) + `resolve_prompt_governance(persona_tier)` (total resolver). The posture is **OD-owned and pure** (no CP / runtime / IS import) — mirroring the `PER_PERSONA_TIER_REDACTION` (posture, OD) ⊳ `RedactionSpanProcessor` (consumer) split.

**Non-vacuity invariant.** The posture MUST be non-vacuously tier-distinct: `solo-developer` differs from BOTH binding tiers on `approval_required` (the posture carries real governance signal, not a uniform table). Mirrors the R-CL-P3 (#481) "TEAM ≠ both neighbours" tier-distinctness discipline.

### §C-OD-34.2 Redaction dimension — DERIVED (composition with C-OD-13)

The prompt-content attribute class is `gen_ai.system_instructions`, a member of `DEFAULT_OFF_CONTENT_ATTRIBUTES` (C-OD-12 §12.1). Its per-tier redaction posture is therefore **already governed** by the C-OD-13 §13.1 `PER_PERSONA_TIER_REDACTION` gradient (`solo-developer` toggleable / operator-self-redact; `team-binding` non-toggleable at the OTLP collector boundary; `multi-tenant-compliance` non-toggleable pre-collector eval-grade pipeline). When a producer emits a system prompt's content to a span, `RedactionSpanProcessor` strips it per that gradient at the binding tiers.

C-OD-34 exposes this as a **derived** accessor, `prompt_content_redaction_enforced(persona_tier)` ≡ `not PER_PERSONA_TIER_REDACTION[persona_tier].toggleable` — `False` at solo-developer (operator-toggleable), `True` at the binding tiers (non-toggleable). It is a read of the single source of truth, not an independent declaration. The R-PM-1 design §4.4 "MULTI_TENANT → redaction" is subsumed by (and refined by) the richer 3-tier gradient: team-binding ALSO redacts (at a different posture), per the canonical C-OD-13 surface.

**Empirical posture at HEAD.** No production producer currently emits `gen_ai.system_instructions` to a span (the injected prompt reaches the provider via the translate seam, not a span attribute — runtime spec v1.44 §14.5.2). The redaction coverage is therefore defense-in-depth-ready: any future producer that DOES emit the prompt-content attribute is stripped at the binding tiers by the existing processor with no further wiring. C-OD-34 records the composition; it does not add a new redaction site.

### §C-OD-34.3 Approval enforcement — runtime-deferred (RT-FAIL-PROMPT-VERSION-UNAPPROVED)

The approval posture is enforced at the runtime bootstrap **stage-0 selection-reconciliation site** (`harness-runtime/src/harness_runtime/lifecycle/prompt_selection.py:enforce_prompt_version_approval`, consumed at `bootstrap/stage_0_preamble.py` immediately after `reconcile_active_prompt_via_selection`). This is a runtime-deferred enforcement of an OD-owned posture — parallel to CP spec v1.31 §29.3's runtime-deferred store-membership check enforced at the same site.

The gate fires (`RT-FAIL-PROMPT-VERSION-UNAPPROVED`, fail-loud / detect-then-refuse → `BootstrapFailure` at PREAMBLE) **iff all hold**:

1. `resolve_prompt_governance(config.persona_tier).approval_required` is `True` (a binding tier), AND
2. a `prompt_selection_manifest` is configured (an inline-only deployment has nothing selection-driven to govern), AND
3. selection *drives* an active version for the run's `(role, workload)` — `resolve_active_prompt_version_sha` returns a non-`None` sha (selection fall-through to the inline default is NOT selection-driven, so it is not gated), AND
4. that selection-driven `version_sha` is NOT a member of the operator-attested `RuntimeConfig.approved_prompt_version_shas` set.

Otherwise the gate is inert. Scope discipline (`[[grounding-reveals-claude-closeable-slice-close-honestly]]` + `[[r-cxa-seam-wiring-is-producer-discovery]]`): the gate governs **only the versions the CP selection layer drives** — the real, currently-reachable governed action introduced by the cascade. It does not retroactively gate a pre-existing inline-only prompt (no selection regime), and it is inert at `solo-developer` (so all existing fixtures + the SOLO-default live e2e path are unaffected). Governance of a binding-tier *inline-only* prompt, and approval of prompt-version *deltas* (a diff producer), are documented re-open triggers — no such producer exists at HEAD.

The operator attests by adding a version's `version_sha` to `RuntimeConfig.approved_prompt_version_shas` (default `frozenset()` — zero burden at solo / inline-only deployments). `RT-FAIL-PROMPT-VERSION-UNAPPROVED` is a governance/config error the operator corrects by attesting the version or not selecting it at a binding tier.

### §C-OD-34.4 Cross-axis posture

C-OD-34 introduces **no new cross-axis CXA edge** at this contract. The PROMPTS(IS)→selection(CP)→injection(runtime)→governance(OD) composition is registered at the R-PM-1 cascade PR #5 CXA seam (per `[[r-cxa-seam-wiring-is-producer-discovery]]` — register the seam after all producers exist). The runtime stage-0 enforcement consumes the OD posture + the CP resolver within the runtime (the top consumer), not via a new typed inter-axis seam. OD's 0-outbound-to-other-axes invariant (`harness-od/CLAUDE.md` §2.2) is preserved — the posture is consumed by runtime, OD itself emits no new outbound edge.

---

## §2 Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Operational_Discipline_v1_29.md` |
| Supersedes | `Spec_Operational_Discipline_v1_28.md` as canonical HEAD (delta-only chain; v1.28 body preserved verbatim) |
| New contract | C-OD-34 (per-persona-tier prompt-governance posture; approval declared + redaction derived + enforcement runtime-deferred). Chain contract count 33 → 34. |
| Carrier code | `harness-od/src/harness_od/prompt_governance_gradient.py` (posture + resolver + redaction-derivation accessor); `harness-runtime/src/harness_runtime/lifecycle/prompt_selection.py` (`enforce_prompt_version_approval` + `PromptVersionUnapprovedError` / `RT-FAIL-PROMPT-VERSION-UNAPPROVED`); `harness-runtime/src/harness_runtime/bootstrap/stage_0_preamble.py` (enforcement site); `harness-runtime/src/harness_runtime/types.py` (`RuntimeConfig.approved_prompt_version_shas`) |
| Verification | `harness-od/tests/test_prompt_governance_gradient.py` (posture totality + non-vacuous tier-distinctness + redaction-derivation + prompt-class-is-default-off); `harness-runtime/tests/test_prompt_governance_enforcement.py` (gate logic: solo-inert / binding-unapproved-fail / binding-approved-pass / no-selection-inert / fall-through-inert / non-vacuous tier-distinct); `harness-runtime/tests/test_bootstrap.py::test_bootstrap_binding_tier_unapproved_selection_fails_loud` + `::test_bootstrap_binding_tier_approved_selection_passes` (e2e through `run_bootstrap`) |
| ADR impact | None (additive OD posture; no foundational decision touched) |
| CXA impact | None at this contract (the cascade composition seam is PR #5; §C-OD-34.4) |
| Clearance | marker filed at `.harness/clearance/Spec_Operational_Discipline-v1_29-cleared-2026-06-12.md` |
| Revision policy | Canonical for this workspace; revisions route to design-phase back-flow per `harness-od/CLAUDE.md` §5.1 |
