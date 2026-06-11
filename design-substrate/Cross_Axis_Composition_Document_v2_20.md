# Cross-Axis Composition Document (v2.20)

*Delta over v2.19. v2.20 is an **additive forward-capability registration** (no contract change to any plan-canonical edge, no edge-semantics change to the 7c baseline) that registers the **R-PM-1 prompts-management composition** as a new, delineated cross-axis seam family. The plan-canonical §2.1 aggregate (**107** = 37 genuine + 48 convention + 22 phase-2-runtime) is **frozen verbatim** — the prompts edges are NOT folded into the audited plan buckets (that would recreate exactly the count-conflation defect v2.18→v2.19 existed to fix). Instead a NEW §2.3.8 registers **2 runtime-mediated edges** materialized at HEAD by the PR #1–#4 cascade — **CP→IS** (prompt-selection sha → IS versioned store) + **OD→CP** (per-tier prompt-governance approval → CP-selected version) — reporting **107 plan-canonical + 2 R-PM-1 forward-capability = 109 total cross-axis relationships**. ZERO change to §2.1 / §2.2 / §2.3.1–§2.3.7 / §2.4 / §3 (all v2.3/v2.17/v2.19-canonical, preserved verbatim). This closes the R-PM-1 cascade (PR #5 of 5). Authored design-phase posture; operator directed the closure track. 2026-06-12.*

## §0 Change note (v2.19 → v2.20)

### §0.1 Revision context — R-PM-1 cascade PR #5 (the prompts composition seam)

R-PM-1 (full prompts-management surface; `Project_Roadmap_v1.md` §5.16, R-CC-1 arc #2) landed as a 4-layer cascade across the axes (`.harness/r-pm-1-prompts-management-design-v1.md` §6):

| Cascade PR | Layer | Landed | Contract |
|---|---|---|---|
| #1 (#506) | INJECTION (runtime) | translate-time per-provider system-prompt injection + inline content carrier | runtime spec v1.44 §14.5.2 + IS spec v1.6 §5.2 |
| #2 (#508) | VERSIONING / AUTHORING (IS) | `PromptManifest.versions` content-addressed store | IS spec v1.7 §5.3 (C-IS-05) |
| #3 (#509) | SELECTION (CP) | `PromptSelectionManifest` per-role/workload binding | CP spec v1.31 §29 (C-CP-29) |
| #4 (#510) | PER-TIER GOVERNANCE (OD) | `PromptGovernancePosture` per-persona-tier approval | OD spec v1.29 C-OD-34 |

PR #5 (this delta) is the **CXA registration** — per `[[r-cxa-seam-wiring-is-producer-discovery]]`, registered **after the producers exist** and grounded against the **real producer/consumer seams** (direct read at HEAD, §0.4). It is documentary: the seams are already materialized at HEAD; this records them in the canonical matrix with full provenance and correct classification.

### §0.2 What is added (and what is frozen)

**Added:** §2.3.8 — a delineated **R-PM-1 prompts-management forward-capability seam family** (2 runtime-mediated edges), plus the forward-capability aggregate clause at §0.6.

**Frozen verbatim (NOT touched by v2.20):** §2.1 aggregate 4×4 matrix (107) + 37/48/22 sub-split; §2.2 axis-level dependency graph; §2.3.1–§2.3.7 per-bucket row tables; §2.4 per-axis outbound posture; §3 Pattern P1. The audited **107 plan-canonical** baseline is **inviolate** — see §0.5 for why the prompts edges are delineated rather than folded.

### §0.3 The 2 registered edges (both runtime-mediated, materialized-live at HEAD)

Direction respects the consumer→producer convention + axis acyclicity (IS < AS < CP < OD):

| # | Bucket | Consumer (axis) | Producer (axis) | What flows | Composition site | Fail-loud |
|---|---|---|---|---|---|---|
| 1 | **CP→IS** | CP prompt-selection (C-CP-29) | IS prompt store (C-IS-05 §5.3) | selected `version_sha` → authored `PromptManifest.versions` store member → content | runtime `reconcile_active_prompt_via_selection` (`harness_runtime/lifecycle/prompt_selection.py`; runtime spec v1.44 §14.5.2 / CP spec §29.3–§29.4) | `RT-FAIL-PROMPT-SELECTION-UNAUTHORED` (selected sha ∉ store) |
| 2 | **OD→CP** | OD prompt-governance (C-OD-34) | CP prompt-selection (C-CP-29) | per-persona-tier `approval_required` posture gates the CP-*selection-driven* active `version_sha` | runtime stage-0 `enforce_prompt_version_approval` (`harness_runtime/lifecycle/prompt_selection.py`; OD spec C-OD-34) | `RT-FAIL-PROMPT-VERSION-UNAPPROVED` (binding-tier selection-driven sha ∉ `RuntimeConfig.approved_prompt_version_shas`) |

### §0.4 Why R-class, and why "materialized-live" not "phase-2-deferred" (the grounding result)

The whole R-PM-1 design kept **each axis pure** and placed composition at the runtime integration layer (the explicit ADR-F1-faithful posture: per-provider feature use at the call site, no axis-to-axis import bleed). Direct read at HEAD confirms:

- `harness-cp/.../prompt_selection_manifest.py` does **not** import `harness_is` (CP-pure; the dashboard's "CP-pure / no IS import" verified).
- `harness-od/.../prompt_governance_gradient.py` imports only `harness_core` + `harness_od.redaction_gradient` (OD-pure).
- `harness-runtime/.../lifecycle/prompt_selection.py` is the **sole composition site** — it imports `harness_cp` (selection) + `harness_is` (store) + `harness_od` (governance) + `harness_core`, and its own docstring names "the CP→IS store consultation … the CXA seam registered at cascade PR #5; runtime is the consumer endpoint."

Therefore **no new genuine-typed (G) inter-axis import seam** is created — the edges are **R (runtime-mediated composition)**, the same class the 7c matrix already uses for runtime-composed edges (e.g. §2.3.4 "ledger-write composition is runtime"). **Precision (advisor-flagged):** unlike some 7c R-rows that remain *Phase-2-deferred*, these 2 are **materialized and live at HEAD** — proven e2e through `run_bootstrap` incl. the live Ollama selection→injection path (PR #3/#4). The "R" denotes *runtime-mediated by axis-purity design*, not *unbuilt*. The §2.3.8 table tags them `R-live` to make this explicit.

**Two non-edges (deliberately excluded after grounding):**
- **Redaction is NOT a new OD→IS edge.** OD's `prompt_content_redaction_enforced` *derives* from the existing `PER_PERSONA_TIER_REDACTION` gradient applied to `gen_ai.system_instructions` (already a `DEFAULT_OFF_CONTENT_ATTRIBUTES` member, C-OD-12). It reuses an existing OD-internal posture; registering a new edge would be a second source of truth (the same one-source-of-truth discipline the PR #4 code enforces). Composition, not duplication.
- **Injection is runtime-internal, not an axis→axis edge.** The translate-time placement of `active_prompt_version.content` onto each provider's call (`system=` / leading `role:"system"`) is performed by the runtime/core dispatch layer, which is **not one of the four axes**. It is the "injection(runtime)" middle node of the chain, not an axis endpoint. (An OD→IS edge for *approval* was also considered and excluded: the gate reads CP's pure resolver + a `RuntimeConfig` frozenset; the sha being an IS-store identity is data semantics, not a dependency edge.)

### §0.5 Why a delineated forward-capability family (frozen-baseline Option B), not a fold-in

Three discriminating reasons (priority order):

1. **Provenance / the v2.18 failure class.** The v2.18→v2.19 patch existed solely to fix count conflation. Folding post-MVP forward-capability edges into the plan-derived 7c buckets recreates the exact "where did this number come from" surface. Delineation keeps the audited **107** inviolate.
2. **Keying mismatch.** Every §2.3.1–§2.3.7 row is keyed by **plan unit IDs** (e.g. `U-CP-04 → U-IS-01`). The prompts edges have **no plan-unit decomposition** — they landed as a post-MVP spec-amendment cascade, keyed by **C-\*** contracts (C-CP-29 / C-IS-05 §5.3 / C-OD-34 / runtime §14.5.2). They do not fit the unit-keyed row format; a delineated subsection references contracts honestly.
3. **Lowest propagation blast radius.** Frozen-baseline keeps `CLAUDE.md` §1.1 reading "107 … 37/48/22" and merely *gains* a forward-capability clause — far lower drift risk than rewriting matrix cells (CP→IS 43→44, OD→CP 12→13) across every citation site.

This matches the design doc's own "**a new CXA seam family**" framing (§4) and the workspace's established plan-baseline-vs-forward-register model (R-CC-1 / R-PM-1) — a delineated forward count is a familiar accounting, not a second system.

### §0.6 Aggregate (plan-canonical frozen + forward-capability delineated)

| Layer | Count | Sub-split |
|---|---|---|
| **Plan-canonical (7c baseline, §2.1 — FROZEN)** | **107** | 37 genuine + 48 convention + 22 phase-2-runtime |
| **R-PM-1 prompts forward-capability (§2.3.8 — NEW)** | **2** | 2 runtime-mediated (`R-live`); CP→IS + OD→CP |
| **Total cross-axis relationships** | **109** | — |

The 107 sub-split is **unchanged** (the 2 new edges are NOT added to the 22 phase-2-runtime count — that count is the plan-canonical 7c set). The forward-capability family carries its own `R-live` count.

### §0.7 Downstream propagation corrected (same arc)

(a) Workspace `CLAUDE.md` §1.1 CXA row: pointer `…v2_19.md` → `…v2_20.md`; the frozen "107 canonical … 37/48/22" is preserved + GAINS the forward-capability clause "(+2 R-PM-1 prompts-management forward-capability seams at §2.3.8 = 109 total)". ✅ this PR.

(b) Workspace `CLAUDE.md` §2.4 CXA plan pointer: `…v2_19.md` → `…v2_20.md`. ✅ this PR.

(b-bis) `.harness/claude-artifact-pointers.md` §2.4 CXA lineage index: pointer `…v2_19.md` → `…v2_20.md` + a v2.20 lineage entry prepended (v2.19 narrative preserved as "prior"). ✅ this PR.

(c) `.harness/roadmap_status.md` dashboard + `Project_Roadmap_v1.md` §5: R-PM-1 cascade PR #5 landed → **R-PM-1 RESOLVED** (all 5 cascade PRs closed). **NOT in this diff** — the roadmap-surface refresh + R-PM-1 RESOLVED marking is a **separate post-merge step** per the §12.2 post-PR-merge audit / §12.2.1 terminating-refresh protocol (these process-substrate files are refreshed after this PR merges, never bundled into the substantive diff). Owed at the post-merge refresh, not claimed here.

(d) Per-axis `harness-{cp,od,is}/CLAUDE.md` cross-axis inventories: **left untouched** (advisor scope discipline; v2.19 §0.8(d) precedent). They are Phase-7-posture surfaces enumerating the plan-canonical buckets; the frozen-baseline keeps OD→CP = 12 / CP→IS = 43 correct (the prompts edges live in the delineated §2.3.8 family, not the plan buckets). Noted here for completeness.

### §0.8 Clearance marker

Per workspace `CLAUDE.md` §4.5: clearance marker filed at `.harness/clearance/Cross_Axis_Composition_Document-v2_20-cleared-2026-06-12.md`.

---

## §2.3.8 R-PM-1 prompts-management forward-capability seam family — NEW (v2.20)

The R-PM-1 prompts-management composition (`PROMPTS(IS) → selection(CP) → injection(runtime) → governance(OD)`) materialized at HEAD across cascade PRs #1–#4. It is registered here as a **delineated forward-capability family** (post-MVP; keyed by C-\* contracts, not plan units — §0.5). Both edges are **`R-live`** = runtime-mediated composition (by axis-purity design), **materialized and proven e2e at HEAD** (NOT Phase-2-deferred — §0.4).

Cross-axis dataflow:

```
  PROMPTS store (IS)        selection (CP)              injection (runtime)        governance (OD)
  C-IS-05 §5.3        ──┐   C-CP-29                     runtime §14.5.2            C-OD-34
  PromptManifest        │   PromptSelectionManifest     translate-time per-        PromptGovernancePosture
   .versions            │   resolve_active_prompt_      provider placement          approval_required
  (content-addressed)   │   version_sha                 (system= | role:system)    (per PersonaTier)
                        │        │                            ▲                          │
                        └─edge 1─┤ selected sha ──▶ store     │ content                  │ edge 2
                        (CP→IS)  │  member ──▶ active version ─┘                          │ (OD→CP)
                  reconcile_active_prompt_via_selection (runtime)        enforce_prompt_version_approval (runtime)
```

| # | Consumer | Producer | Contract (composition site) | Class |
|---|---|---|---|---|
| 1 | C-CP-29 prompt-selection (`harness_cp.prompt_selection_manifest`) | C-IS-05 §5.3 prompt store (`harness_is.prompt_manifest` `PromptManifest.versions`) | runtime spec v1.44 §14.5.2 / CP spec v1.31 §29.3–§29.4 — `reconcile_active_prompt_via_selection` resolves the CP-selected `version_sha` to its authored IS store member (content↔hash coherence via `model_copy` onto `active_prompt_version`); fail-loud `RT-FAIL-PROMPT-SELECTION-UNAUTHORED` on a non-member sha | **R-live** — CP→IS store consultation; runtime-mediated (CP imports no IS), materialized + e2e-proven (incl. live Ollama) at HEAD |
| 2 | C-OD-34 prompt-governance (`harness_od.prompt_governance_gradient`) | C-CP-29 prompt-selection (`harness_cp.prompt_selection_manifest`) | OD spec v1.29 C-OD-34 — runtime stage-0 `enforce_prompt_version_approval` gates the CP-*selection-driven* active `version_sha` against `RuntimeConfig.approved_prompt_version_shas` at binding tiers (`approval_required`); fail-loud `RT-FAIL-PROMPT-VERSION-UNAPPROVED`; inert at SOLO + inline-only/no-match | **R-live** — OD→CP governance gate; runtime-mediated (OD imports no CP), materialized at HEAD; preserves OD's 0-outbound-to-other-axes plan invariant (this is a forward-capability family edge, outside the §2.4 plan-canonical OD posture) |

**Family count: 2 (`R-live`).** Aggregate with the frozen plan-canonical baseline: **107 + 2 = 109** (§0.6).

*Anti-duplication note:* the redaction governance dimension (OD `prompt_content_redaction_enforced`) is **not** a registered edge — it derives from the existing `PER_PERSONA_TIER_REDACTION` gradient over `gen_ai.system_instructions` (C-OD-12 / C-OD-13), reusing an OD-internal posture (§0.4). The translate-time injection is runtime-internal (runtime is not an axis), not an axis→axis edge.

---

## §1 — Cross-arc note

v2.20 is an additive forward-capability registration in the workspace's established precedent (delineated forward-register accounting alongside the plan-canonical baseline; R-CC-1 / R-PM-1 model). It does not touch any merged + cleared plan-canonical edge — the §2.1 matrix, §2.3.1–§2.3.7 row tables, §2.4 posture, and §3 Pattern P1 are preserved verbatim from their v2.3 / v2.17 / v2.19 canonical state. The seams it registers were materialized + e2e-verified across cascade PRs #1–#4 (#506/#508/#509/#510); this delta records them with full provenance and correct classification, closing the R-PM-1 cascade (PR #5 of 5). No fork doc is filed — additive forward-capability registration against already-landed, already-cleared producers, grounded by direct read at HEAD (§0.4); the advisor pass (2026-06-12) confirmed the 2-edge enumeration, the two deliberate non-edges, and the frozen-baseline Option B structure.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Cross_Axis_Composition_Document_v2_20.md` |
| Filing event | Additive registration of the R-PM-1 prompts-management composition as a delineated forward-capability seam family (§2.3.8): 2 runtime-mediated `R-live` edges — CP→IS (prompt-selection sha → IS versioned store, `reconcile_active_prompt_via_selection`) + OD→CP (per-tier prompt-governance approval → CP-selected version, `enforce_prompt_version_approval`). Plan-canonical §2.1 aggregate 107 + 37/48/22 sub-split FROZEN verbatim; reported total 107 plan-canonical + 2 forward-capability = 109. Redaction (derived) + injection (runtime-internal) deliberately excluded as non-edges. Closes the R-PM-1 cascade (PR #5 of 5). 2026-06-12 |
| Authored at | Design-phase posture session 2026-06-12 (operator directed the closure / R-CC-1 track) |
| Authoring authority | `Project_Roadmap_v1.md` §5.16 R-PM-1 + `.harness/r-pm-1-prompts-management-design-v1.md` §6 row #5 + advisor confirmation of the 2-edge enumeration + frozen-baseline structure |
| Predecessor | `Cross_Axis_Composition_Document_v2_19.md` (§2.1 matrix + §2.2 + §2.3.1–§2.3.7 + §2.4 + §3 preserved verbatim — v2.20 is purely additive: a new §2.3.8 family + the §0.6 forward-capability aggregate clause) |
| Canonical reading | Plan-canonical §2.1 matrix = v2.19-canonical (aggregate **107**; genuine 37 / convention 48 / phase-2-runtime 22), FROZEN. Plus the R-PM-1 prompts forward-capability family at §2.3.8 = **2** `R-live` runtime-mediated edges (CP→IS + OD→CP). **Total cross-axis relationships = 109.** |
| Successor | TBD per next CXA arc |
| Clearance marker | `.harness/clearance/Cross_Axis_Composition_Document-v2_20-cleared-2026-06-12.md` |
