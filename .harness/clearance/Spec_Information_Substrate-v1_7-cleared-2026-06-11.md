---
artifact: design-substrate/Spec_Information_Substrate_v1.md
version: v1.7
cleared_at: 2026-06-11T22:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc (bundled-absorption — design-substrate + harness-is/src + harness-is tests + harness-is/CLAUDE.md pointer)
back_reference:
  - .harness/r-pm-1-prompts-management-design-v1.md §4.3 / §6 row #2 (R-PM-1 4-layer design — cascade PR #2; the IS versioning/authoring layer)
  - .harness/class_1_fork_prompts_management_surface_active_prompt_version.md DP-4 (the prompts-management fork, multi-version surface)
  - Project_Roadmap_v1.md §5.16 R-PM-1 + §5.17 R-CC-1 (capability-completion arc #2 — the active frontier)
  - design-substrate/Spec_Information_Substrate_v1.md v1.6 §5.2 (the PR #1 inline `content` carrier + derive-invariant this store generalizes; the per-version content-addressing it applies across a collection)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - advisor() pre-substantive decision-fork (settled #2-alone-vs-merge-#3 → ship #2 alone, genuinely minimal, honoring the ratified §6 cascade sequence; required honest "ADD a store alongside, NOT generalize content into the active version" framing — true generalization would force the §5.2 + runtime stage-5 readers to change = PR #3 blast radius; directed DROP the speculative resolve(sha)→content helper, KEEP the membership invariant as illegal-states-unrepresentable; tuple-store over sha-keyed-mapping to avoid the sha-stored-twice one-source-of-truth smell)
  - out-of-family Codex review (decorrelated, ran on the committed branch diff — independently executed the edge probes (content-addressed-unique rejection) + the prompt-manifest/snapshot/bootstrap suites; verdict "No discrete correctness issues were identified in the changed implementation or tests")
  - harness-adversarial-reviewer Phase-7 pre-merge review (dedicated-agent invocation per `[[feedback-genuine-skill-invocation-dedicated-agent]]`; VERDICT APPROVE — 0 Class 1 / 0 Class 2 / 4 Class 3 informational; empirically verified the byte-unchanged-readers + no-`.versions`-consumer + spec-`+`-only-diff + invariant-(c)-soundness + honest-framing claims). Two Class 3 findings applied pre-merge: F-01/F-03 `from_contents` builder now enforces `active ∈ contents` explicitly (the empty-`contents` short-circuit previously let a non-member active through, contradicting the builder docstring) + 2 new edge tests; F-02 the NEW §5.3 cite refreshed `runtime spec v1.44 §14.5` → `§14.5.2` (the byte-exact injection sub-section; the 3 other `§14.5` occurrences are frozen v1.6 cleared content, left untouched per delta-only verbatim-preservation). F-04 (sibling IS-plan v2.5 frozen-lineage staleness) correctly not-owed by this PR.
  - empirical code-grounding (the two live readers `procedural_tier_snapshot.py:27,113` (§5.2 hash) + `stage_5_loop_init.py:221` (injection) read `active_prompt_version`, which is byte-unchanged; the `versions` store has no reader in this diff — confirmed by grep; verify-by-execution: harness-is 153 green incl. 12 new store-coherence + builder-edge tests, runtime §5.2 reader 17 + carrier consumers 51 green, pyright strict 0/0/0, ruff clean, overlay 31/31, ledger 54/54)
  - design-phase bundled-absorption posture (workspace CLAUDE.md §11.4; X-AL-3 guard satisfied by the paired fork doc + this design artifact + this marker)
supersedes: design-substrate/Spec_Information_Substrate_v1.md v1.6
superseded_by:
---

# Clearance — `Spec_Information_Substrate v1.7`

v1.7 is the **IS versioning/authoring layer of R-PM-1** (cascade PR #2). It adds the prompts **versioned authoring store** to the `PromptManifest` carrier — the substrate the CP selection layer (PR #3) will index into. There is **no runtime consumer at PR #2**; this is an additive, forward-only carrier widening verified by carrier-coherence unit tests.

**What changed.** One additive amendment — a NEW §5.3 sub-section under C-IS-05 — plus the carrier impl + tests:

1. **`PromptManifest.versions: tuple[PromptVersion, ...] = ()`** — the content-addressed authoring store on the `PROMPTS` path-class (C-IS-01 §1, plain-text-file-in-git). Each entry carries `content` + `version_sha = prompt_version_sha(content)` (the v1.6 per-version derive-invariant applied across a collection).
2. **Internal-coherence invariants** (enforced at construction, with a non-empty store): (a) entries are authored (`version_sha != ""`); (b) content-addressed-unique (no two share a `version_sha`); (c) a non-empty `active_prompt_version` is a store member. Empty store (the default) → the #496/PR-#1 behavior verbatim, no membership obligation.
3. **`from_contents(manifest_version, contents, active)` authoring builder** — content-addresses a set of content strings into the store and selects an active member.

**Why it's an additive store, NOT a generalization-into the active version.** The R-PM-1 design (§4.3) phrases PR #2 as "generalize the inline content into the store." What is actually *forward-only* — and what v1.7 commits — is narrower: the store is added **alongside** the still-inline `active_prompt_version`. A true generalization (content moves *into* the store, `active_prompt_version` becomes a pure sha-reference) would change the §5.2 hash reader (`active_prompt_version.version_sha`) and the runtime stage-5 injection reader (`active_prompt_version.content`, runtime spec v1.44 §14.5.2) and compose with the per-role selection layer — that is PR #3 blast radius. v1.7 keeps both readers byte-unchanged. The transitional content duplication (a member active selection duplicates its store entry's content) is byte-identical **by construction** (content-addressing: equal `version_sha` ⟹ equal content), not an independent authority that can drift; PR #3 collapses the active selection to a reference and removes it.

**Why the §5.2 recipe is unchanged.** The store does not enter the §5.2 content-hash recipe — it has no §5.2 consumer. The recipe is byte-identical at v1.7 (still 3-component, still reads `active_prompt_version.version_sha`). No hash-consumer cascade.

**Carve-outs for Phase 7 consumers.**
- The v1.6 inline `content` carrier is the **foundation, not a redo** — PR #2 adds the store *around* the same `PromptVersion` shape; the per-version derive-invariant is unchanged.
- The sha→content resolution the selection layer needs is **deliberately NOT pre-built** — PR #3 (its consumer) defines the lookup it actually requires.
- §5 six-field shape / §5.1 sidecar / §5.2 recipe / §6 hash-chain / §7 read-write / §10 seam exports are **PRESERVED VERBATIM**.
- The `PromptManifest._enforce_store_invariants` validator is construction-time only (`model_copy(update=...)` bypasses `mode="after"`, mirroring the v1.6 `PromptVersion` caveat); no current caller copies a manifest to mutate the store. PR #3's mutation path (if any) must re-validate.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
