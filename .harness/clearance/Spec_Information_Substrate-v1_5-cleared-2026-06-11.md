---
artifact: design-substrate/Spec_Information_Substrate_v1.md
version: v1.5
cleared_at: 2026-06-11T03:30:00-06:00
clearance_type: spec-writer-apply-pass (bundled-absorption — design-substrate + harness-is/src + harness-runtime/src)
back_reference:
  - .harness/class_1_fork_prompts_management_surface_active_prompt_version.md (the fork this delta resolves — DP-1..DP-4, mirror RoutingManifest / minimal binding)
  - Project_Roadmap_v1.md §5.15 R-CL-P4 (spec-completion deferrals; prompts-management sub-part — the last open P4 blocker)
  - .harness/post-mvp-full-closure-plan-v1.md (Phase P4 — prompts-management surface + active_prompt_version 3rd hash component)
  - .harness/closure-p0-scope-lock.md C-row 36 (prompts surface = Category 3 fork → P4-blocked)
  - design-substrate/Spec_Harness_Runtime_v1.md v1.42 §4 C-RT-04 (co-published runtime-context binding side)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - operator AskUserQuestion 2026-06-11 ("Ratify — build minimal binding" — DP-1..DP-4 as recommended, mirror RoutingManifest, minimal scope per the P0-ratified P4 plan)
  - advisor() decision-fork pass (confirmed surface-the-confirm-gate not a scope menu; tension IS-fidelity ⊥ operator-burden probe-resolved by RoutingManifest default_factory → no council; banked the bundled-absorption clearance + participation acceptance criterion)
  - empirical code-grounding (RoutingManifest carrier shape; procedural_tier_snapshot.py 2-component recipe; IS spec §5.2 three preconditions)
  - out-of-family Codex review (pending — this arc)
  - design-phase bundled-absorption posture (workspace CLAUDE.md §11.4)
supersedes:
superseded_by:
---

# Clearance — `Spec_Information_Substrate v1.5`

v1.5 closes the C-IS-05 §5.2 "Prompts component deferred at v1.3" footer — the **last open R-CL-P4 blocker** (the OD tail-keep bounded-buffer sub-part shipped at PR #490; the keying-tuple sub-part resolved at PR #492 / IS v1.4). The §5.2 recipe widens from the v1.3 **2-component** form `{active_skills_versions, routing_manifest_sha}` to the **3-component** form `{active_prompt_version, active_skills_versions, routing_manifest_sha}` (alphabetically ordered; `sort_keys=True`). `active_prompt_version` is read as `HarnessContext.prompt_manifest.active_prompt_version.version_sha`.

This is a **runtime-binding-extension arc**, exactly as the v1.3 §5.2 Deferral footer framed it — NOT a spec-extension-from-scratch. The footer named three preconditions; at v1.5 all three are satisfied:

1. The runtime spec authors the `HarnessContext.prompt_manifest: PromptManifest` carrier field at runtime spec v1.42 §4 C-RT-04 (the `active_prompt_version: PromptVersion` runtime binding lives carrier-homed within the manifest, mirroring how `routing_manifest` carries `routing_manifest_sha`).
2. The `PromptManifest`/`PromptVersion` carrier types land at `harness_is.prompt_manifest` (`PromptManifest` = `manifest_version: int` + `active_prompt_version: PromptVersion`; `PromptVersion` = `version_sha: str`; both frozen + `extra="forbid"`, mirroring `RoutingManifest`).
3. `resolve_procedural_tier_snapshot` (U-RT-112) reads `ctx.prompt_manifest.active_prompt_version.version_sha` at write-time.

**Ratified scope = minimal binding (DP-4).** The operator ratified the *minimal* hash-component binding (close the §5.2 deferral), consistent with the P0-ratified P4 plan ("build the prompts manifest carrier + wire the resolver's 3rd component + rebase the hash"). The fuller prompts-management surface (multi-prompt versioning + selection, with a materialization stage) is a **separate forward arc** per fork DP-4. (This corrects the earlier "FULL prompts-management scope" expectation carried in memory + the v1.4 IS clearance note — grounding + the P0 scope-lock revealed the Claude-closeable minimal slice, `[[grounding-reveals-claude-closeable-slice-close-honestly]]`.)

**Design decision — mirror `RoutingManifest` (probe-resolved tension).** DP-1..DP-4 all resolve by mirroring the existing `routing_manifest` precedent: a frozen operator-supplied carrier on `HarnessContext` (empty-defaultable via `default_factory`), read by the resolver at write-time. The would-be IS-fidelity ⊥ operator-burden tension (a *meaningful* prompt-version component vs *minimal* operator config) is **probe-resolved** by `RoutingManifest`'s `default_factory` — the workspace's settled answer to exactly this tradeoff: the carrier exists (so the component is real) but defaults empty (`version_sha=""` → no active prompt; zero config burden). No council was convened (the §10.9 amendment-5 probe-resolved path).

**Bundled-absorption arc** (`CLAUDE.md` §11.4): the IS spec delta + the co-published runtime spec v1.42 delta land alongside their impl (`harness_is.prompt_manifest` carrier types; `RuntimeConfig.prompt_manifest` operator-supply field + `HarnessContext.prompt_manifest` runtime field — mirroring `routing_manifest`, carried at both; the stage-0 PREAMBLE `ctx.prompt_manifest = config.prompt_manifest` copy that makes the binding reachable through the normal bootstrap path; the 3-component resolver; `MutableHarnessContext` ambient carrier), the governance-pointer cascade (`harness-is/CLAUDE.md` §1.2 + `.harness/claude-artifact-pointers.md` §2.3 bumped v1.4 → v1.5 / runtime v1.41 → v1.42; root `CLAUDE.md` §2.3 references IS/Runtime by `_v1.md` filename — unchanged, no bump), the fork-doc status flip (OPEN → APPLIED), and this marker.

**ZERO change to the F-layer contracts.** The §5 six-field shape, the §5.1 `procedural_tier_snapshot_ref` sidecar field (type/semantic/constraint), the §6 hash-chain construction, the §7 read/write contracts, and the §10 seam exports are all PRESERVED VERBATIM. The recipe-internal component count is a §5.2 resolver detail, not an entry-shape change. No new C-IS-NN contract; no new entry field.

**Acceptance criterion = participation, not "hash changed."** The third component is proven to *participate*: two contexts differing only in `prompt_manifest.active_prompt_version.version_sha` produce different snapshot refs; equal version_sha → equal ref (tests `test_resolve_different_prompt_version_different_hash` + `test_resolve_same_prompt_version_same_hash`). Existing snapshot-digest assertions were rebased forward-only (the v1.3 2-component oracles updated to the v1.5 3-component recipe; no historical-entry migration).

Verification: 17 resolver tests + 4 `PromptManifest` type tests + the full harness-runtime suite (1561) + harness-is suite green; the C-RT-04 field-set conformance test (`test_harness_context_declares_all_c_rt_04_fields`) refreshed +1; pyright strict + ruff clean on all touched files. Forward-only hash rebase per §5.2 (operators MUST treat snapshot-ref equality as scoped within a single recipe-version generation — the v1.3 prose already anticipated this).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- v1.4 + v1.3 + v1.2 + v1.1 + v1 bodies are PRESERVED VERBATIM (delta-only convention); v1.5 amends ONLY §5.2's "Prompts component deferred" paragraph + the recipe block (2→3-component).
- Co-published with `Spec_Harness_Runtime` v1.42 (the runtime-context binding side); see `.harness/clearance/Spec_Harness_Runtime-v1_42-cleared-2026-06-11.md`.
- See `.harness/clearance/README.md` for marker discipline.
