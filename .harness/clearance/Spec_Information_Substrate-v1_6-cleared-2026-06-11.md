---
artifact: design-substrate/Spec_Information_Substrate_v1.md
version: v1.6
cleared_at: 2026-06-11T18:30:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc (bundled-absorption — design-substrate + harness-is/src + harness-runtime tests)
back_reference:
  - .harness/r-pm-1-prompts-management-design-v1.md §4.1/§4.3 (R-PM-1 4-layer design — cascade PR #1; the IS-carrier provenance-tightening side)
  - .harness/class_1_fork_prompts_management_surface_active_prompt_version.md DP-5 (the prompts-management fork, re-opened at PR #1 injection scope)
  - Project_Roadmap_v1.md §5.16 R-PM-1 + §5.17 R-CC-1 (capability-completion arc #2 — the active frontier)
  - design-substrate/Spec_Harness_Runtime_v1.md v1.44 §14.5.2 (the runtime-injection side; co-published this arc)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - advisor() pre-substantive decision-fork (approved the cleared design's impl approach; required the prompt_version_sha("")=="" empty-sentinel + after-validator preserving all 3 existing version_sha="" constructors; confirmed provenance-tightening framing — recipe shape unchanged, only version_sha's provenance tightens, so no hash-consumer cascade)
  - out-of-family Codex review (pending this arc — the decorrelated diff reviewer)
  - harness-adversarial-reviewer Phase-7 pre-merge review (pending this arc)
  - empirical code-grounding (3 PromptVersion constructors at HEAD are all empty-sentinel → content: str = "" forward-compatible; procedural_tier_snapshot.py reads active_prompt_version.version_sha → the derive-invariant closes the silent-drift gap; verify-by-execution: harness-is 140 + harness-runtime 1584 green, pyright 0, ruff clean, overlay 31/31)
  - design-phase bundled-absorption posture (workspace CLAUDE.md §11.4; X-AL-3 guard satisfied by the paired fork doc + this design artifact)
supersedes: design-substrate/Spec_Information_Substrate_v1.md v1.5
superseded_by:
---

# Clearance — `Spec_Information_Substrate v1.6`

v1.6 is the **IS-carrier side of R-PM-1 cascade PR #1** (the runtime-injection side is co-published at runtime spec v1.44 §14.5.2). It **provenance-tightens** the §5.2 third procedural-tier hash component without changing the recipe.

**What changed.** Two amendments to the `PromptVersion` carrier (`harness_is.prompt_manifest`), with a §5.2 sub-paragraph recording them:

1. **Inline `content: str = ""` carrier** — the minimal, self-contained content source so a single operator-supplied active prompt injects + proves e2e within PR #1. PR #2 generalizes this to the multi-version `PROMPTS`-path-class store + content-addressing.
2. **The `content ↔ version_sha` derive-invariant** — `version_sha == prompt_version_sha(content)`, enforced at construction (detect-then-refuse). `prompt_version_sha("") == ""` (the empty-carrier sentinel), else the hex SHA-256 of the UTF-8 content bytes. The sha is no longer an independent operator-set field; `PromptVersion.from_content(content)` is the authoring helper.

**Why it's a provenance-tightening, not a recipe change.** The §5.2 content-hash recipe is byte-identical at v1.6 — still 3-component, still reads `active_prompt_version.version_sha`. ONLY how that `version_sha` is *produced* tightens (now content-derived). There is therefore NO hash-consumer cascade. The reason for the invariant is replay-integrity: the runtime cascade (v1.44) injects `content` as a per-provider system prompt, so without the invariant, injected content could change while the §5.2 hash reports "unchanged" — a silent provenance gap. With it, content and its hash component move together.

**Carve-outs for Phase 7 consumers.**
- The #496 minimal binding (v1.5) is the **foundation, not a redo**. PR #1 *amends* the just-cleared frozen `PromptVersion` shape (adds the optional `content` field) — empty-default keeps existing empty-carrier configs (`PromptVersion(version_sha="")`) valid; configs that newly supply content rebase the procedural-tier snapshot forward (forward-only, exactly as the v1.3/v1.5 prose anticipated).
- The #496-era *identity-only* construction (a non-empty `version_sha` with no `content`) is **superseded** — a non-empty sha now requires matching content. Three workspace tests that constructed identity-only shas were updated to `from_content` (the legitimate forward rebase, not a behavior regression).
- §5 six-field shape / §5.1 sidecar / §6 hash-chain / §7 read-write / §10 seam exports are **PRESERVED VERBATIM**.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
