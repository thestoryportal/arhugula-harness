---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.42
cleared_at: 2026-06-11T03:30:00-06:00
clearance_type: spec-writer-apply-pass (bundled-absorption — design-substrate + harness-runtime/src)
back_reference:
  - .harness/class_1_fork_prompts_management_surface_active_prompt_version.md (the fork this delta resolves — runtime-context binding side, IS §5.2 precondition 1)
  - Project_Roadmap_v1.md §5.15 R-CL-P4 (prompts-management sub-part — the last open P4 blocker)
  - design-substrate/Spec_Information_Substrate_v1.md v1.5 §C-IS-05 §5.2 (co-published recipe side; the third hash component)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - operator AskUserQuestion 2026-06-11 ("Ratify — build minimal binding")
  - advisor() decision-fork pass (confirmed minimal binding + bundled-absorption clearance owed)
  - empirical code-grounding (HarnessContext field layout; routing_manifest precedent; freeze() pass-through)
  - out-of-family Codex review (pending — this arc)
  - design-phase bundled-absorption posture (workspace CLAUDE.md §11.4)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.42`

v1.42 authors **NEW `prompt_manifest: PromptManifest` field rows at both §3 C-RT-03 `RuntimeConfig` and §4 C-RT-04 `HarnessContext`** (`harness_is.prompt_manifest`) plus the bootstrap stage-0 copy that wires them — the runtime-context binding side of the IS spec §5.2 third procedural-tier hash component (deferred at IS v1.3, bound at IS v1.5; post-MVP closure R-CL-P4). This satisfies IS §5.2 **precondition (1)** ("the runtime spec authors the `active_prompt_version` runtime binding at `HarnessContext`"). The two specs co-publish the arc: IS v1.5 owns the recipe + carrier types; runtime v1.42 owns the context field + operator-supply surface.

**Field shape — mirror `routing_manifest` (carried at both RuntimeConfig and HarnessContext).** `prompt_manifest: PromptManifest` is an operator-supplied, frozen, empty-defaultable carrier. The operator supplies it at `RuntimeConfig.prompt_manifest`; bootstrap **stage 0 PREAMBLE** copies it to `ctx.prompt_manifest` (`ctx.prompt_manifest = config.prompt_manifest`), before the first `resolve_procedural_tier_snapshot` call at stage-3b producer sites. It defaults to an empty manifest (`active_prompt_version.version_sha=""` → no active prompt), so operators that do not version prompts carry zero config burden (the `routing_manifest` `default_factory` precedent). The stage-0 copy is a direct as-supplied read, NOT a materialization/enrichment stage (there is no prompts materialization stage at minimal binding — the fuller versioning/selection surface is deferred per fork DP-4). `resolve_procedural_tier_snapshot` (U-RT-112) reads `ctx.prompt_manifest.active_prompt_version.version_sha` at write-time as the `active_prompt_version` recipe component.

**Reachable through the normal bootstrap path (Codex review).** An out-of-family Codex review of the impl diff flagged that the original draft (a §4 read surface + an empty `MutableHarnessContext` default with no operator-supply route) left every real bootstrap run hashing `active_prompt_version == ""` — the binding worked only at direct test-constructed contexts. This was reconciled against the advisor pass (which validated the design but did not probe production-reachability) by taking the Codex finding: the §3 `RuntimeConfig` operator-supply field + the stage-0 copy make the binding reachable. This corrects the `[[test-bypass-as-runtime-truth-pattern]]` / unreachable-binding defect class before merge.

**Runtime-binding-extension arc, NOT a new contract.** Zero new C-RT-NN; no §14.x body; the `PromptManifest`/`PromptVersion` carrier types are IS-axis-owned (`harness_is.prompt_manifest`, authored at IS spec v1.5 §5.2). v1.42 amends ONLY the §3 C-RT-03 + §4 C-RT-04 field tables (one new row each + the stage-0 copy that wires §3 → §4). All §14.x contract bodies are PRESERVED VERBATIM.

**Impl co-published.** `harness-runtime/src/harness_runtime/types.py` (`RuntimeConfig.prompt_manifest` + `HarnessContext.prompt_manifest` fields + import); `bootstrap/stage_0_preamble.py` (`ctx.prompt_manifest = config.prompt_manifest` copy); `bootstrap/mutable_context.py` (`MutableHarnessContext.prompt_manifest` ambient default + `freeze()` pass-through — the resolver runs against the mutable ctx at stage-3b producer sites, so the carrier must be present there, not only on the frozen ctx); `lifecycle/procedural_tier_snapshot.py` (3-component recipe). The C-RT-04 field-set conformance test (`test_harness_context_declares_all_c_rt_04_fields`) refreshed +1; a production-path bootstrap test proves an operator-supplied `config.prompt_manifest` flows into the snapshot.

**Bundled-absorption arc** (`CLAUDE.md` §11.4): design-substrate spec delta + impl + governance-pointer cascade (`.harness/claude-artifact-pointers.md` §2.3 runtime row v1.41 → v1.42; root `CLAUDE.md` §2.3 references the runtime spec by `_v1.md` filename — unchanged, no bump) + this marker.

Verification: full harness-runtime suite (1561) green incl. all bootstrap/integration real-ctx paths; pyright strict (0 errors) + ruff clean on touched files. The original field-placement error (the row first landed in `RuntimeConfig` by anchoring on the wrong `routing_manifest`) was caught by pyright (`HarnessContext` has no `prompt_manifest`) and corrected before merge — the field is on `HarnessContext` (the class the resolver reads).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- v1.41 + earlier lineage PRESERVED VERBATIM (delta-only-spec-file convention); v1.42 adds ONLY the one §4 C-RT-04 field row.
- Co-published with `Spec_Information_Substrate` v1.5 (the recipe side); see `.harness/clearance/Spec_Information_Substrate-v1_5-cleared-2026-06-11.md`.
- See `.harness/clearance/README.md` for marker discipline.
