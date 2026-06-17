---
artifact: design-substrate/Spec_Information_Substrate_v1.md
version: v1.9
cleared_at: 2026-06-17T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_b4_per_role_prompt_procedural_tier_hash_coherence.md
  - .harness/beyond-mvp-capability-boundary-ledger.md (R-FS-1 arc B4)
  - .harness/r-fs-1-remaining-arcs-grounding-sweep-v1.md (Arc B4)
merge_commit: <pending — pinned at PR merge>
reviewer_chain:
  - advisor() pre-substantive (full-transcript) — caught the §5.2 hash-coherence gap the arc-open grounding's "impl-no-fork" read missed; named the discriminating snapshot-inputs check; confirmed impl → impl+fork
  - routing_manifest_sha precedent (the asymmetry deciding Route C)
  - Codex out-of-family review at PR (high-blast-radius: §5.2 recipe + dispatch path)
supersedes: Spec_Information_Substrate-v1_8-cleared-2026-06-13.md
---

# Clearance — `Spec Information Substrate v1.9`

v1.9 widens the C-IS-05 §5.2 procedural-tier content-hash recipe from 3-component to 4-component, adding `prompt_selection_manifest_sha` (SHA-256 over the whole `PromptSelectionManifest` canonical-JSON bytes at `HarnessContext.config.prompt_selection_manifest` — the operator-supplied `RuntimeConfig` field, its spec'd home; `""` when `None`; NO new top-level carrier / runtime-spec §4 C-RT-04 row, as it is not stage-enriched), mirroring the existing `routing_manifest_sha` treatment. This is the coherence half of R-FS-1 arc **B4** (per-role / per-step dispatch indexing): B4 makes a fan-out branch's per-role prompt `content` take effect (injected at the runtime §14.5.2 translate seam keyed on `step_context.agent_role`), and the v1.8 recipe — which hashed only the resolved default-role `active_prompt_version.version_sha` — left per-role prompt-selection bindings hash-invisible, reintroducing the §14.5.2-forbidden drift (injected content changing while the procedural-tier hash reports "unchanged") for the per-role dimension. The fix restores the invariant symmetrically with how the recipe already hashes the whole routing manifest.

This is a **bundled-absorption arc**: the IS §5.2 amendment + the runtime per-role prompt threading (stage-0 per-role map build, stage-5 dispatcher binding, per-dispatch effective-system-prompt selection) co-land in the same PR. The design back-flow is FULL-SPEC-pre-authorized (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`); no operator gate (reversible additive recipe component, no ADR / six-field / §6 hash-chain / §7 read-write / §10 seam-export change). Forward-only hash rebase per the §5.2 prose (no migration of historical entries).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- The recipe widening is additive + forward-only; `None`/empty selection manifest → `""` → byte-identical procedural-tier hash to a no-selection run (pre-B4 behavior preserved).
- See `.harness/clearance/README.md` for marker discipline.
