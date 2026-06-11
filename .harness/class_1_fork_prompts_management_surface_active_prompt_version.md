# Class 1 (halt-execution) — prompts-management runtime surface + `active_prompt_version` (IS C-IS-05 §5.2 third hash component)

**Filed at:** Post-MVP closure Phase 0 scope-lock (2026-06-10), HEAD `37b7c80`
**Locus:** `harness-runtime/src/harness_runtime/lifecycle/procedural_tier_snapshot.py:10-16` (2-component recipe; no `active_prompt_version` field / no `PromptManifest` carrier) vs `design-substrate/Spec_Information_Substrate_v1.md` v1.3 §5.2 "Prompts component deferred" footer (line ~349).
**Status:** ✅ APPLIED-AS-MINIMAL-BINDING (2026-06-11) — operator-ratified "Ratify — build minimal binding" (DP-1..DP-4 as recommended; mirror `RoutingManifest`). Bound at **IS spec v1.5 §5.2** (recipe widened 2→3-component) + **runtime spec v1.42 §4 C-RT-04** (`HarnessContext.prompt_manifest` field). Carriers at `harness_is.prompt_manifest`; resolver reads `ctx.prompt_manifest.active_prompt_version.version_sha`. Clearance markers `Spec_Information_Substrate-v1_5-cleared-2026-06-11.md` + `Spec_Harness_Runtime-v1_42-cleared-2026-06-11.md`. **R-CL-P4 UNBLOCKED** (this was the last open P4 blocker). The fuller prompts-management surface (multi-prompt versioning + selection) is a separate forward arc per DP-4.
**Routing:** IS-axis design-phase — runtime-spec field authoring (`active_prompt_version: PromptVersion` on `HarnessContext`) + IS spec v1.x amendment adding the third hash component, per the three §5.2 preconditions. The spec itself frames this as **"a runtime-binding-extension arc, not a spec-extension-from-scratch arc"** (§5.2).
**Precedent:** `[[grounding-reveals-claude-closeable-slice-close-honestly]]` (spec'd-but-unbuilt vs UNSPECIFIED-contract discriminator) · `[[halt-route-split-ac-pattern]]` · X-AL-3 (no silent design extension).

## The surface (why this halts before P4 builds it)

The procedural-tier snapshot content-hash (IS C-IS-05 §5.1/§5.2; the H_T-IS-2 substrate) commits a **2-component** recipe at HEAD: `(skills_versions, routing_manifest_sha)`. The spec **names a third component — `active_prompt_version` — and explicitly DEFERS it** (§5.2 Deferral footer). Grounded at P0 (2026-06-10):

- **No carrier exists.** `HarnessContext` has no `active_prompt_version` field; there is no `PromptManifest` type anywhere in `harness-*/src/`. `procedural_tier_snapshot.py:10-16` + AC #11 pin the 2-component scope.
- **The spec defers, it does not specify.** §5.2 gives the 2-component recipe and names **three preconditions** for the future component — it does NOT define what a `PromptManifest` is, its fields, or how active version is read. *"Per X-AL-3 the spec MUST NOT commit a content-hash recipe to a phantom referent."*
- **No prompts-management spec/ADR exists** in `design-substrate/`. The only prompts presence is the filesystem `PROMPTS` path-class (C-IS-01) — the operational artifact exists; the **runtime-side binding contract** is unauthored.

Building the `PromptManifest` shape + `active_prompt_version` field + read-access contract at Phase 7 would be **authoring new H_T design surface** = X-AL-3 silent-extension. Hence: halt, surface, ratify, then build at P4.

## The three preconditions the spec already names (§5.2)

1. The runtime spec authors `active_prompt_version: PromptVersion` on `HarnessContext`.
2. A `PromptManifest` carrier lands (plain-text-in-git, mirroring the routing-manifest pattern).
3. The prompts-management surface authors operational read-access to the active prompt version at write-time.

## Decision points (for design-phase resolution + operator ratification)

- **DP-1 — `PromptManifest` shape.** Mirror `RoutingManifest` (the `routing_manifest_sha` precedent): a plain-text-in-git manifest with a deterministic `.sha`/digest. Recommended: **yes, mirror the routing-manifest pattern** (consistency + the resolver already SHAs the routing manifest the same way).
- **DP-2 — `active_prompt_version` read-access.** Resolver reads it from `HarnessContext` at write-time (the U-CP-60 operator-supplied-substrate-injected-at-`__init__` precedent the resolver already uses for skills/routing). Recommended: **same injection pattern.**
- **DP-3 — hash rebase.** Adding the third component changes every procedural-tier snapshot digest (a one-time rebase, like prior hash-recipe extensions). Recommended: **rebase at the IS spec v1.x amendment; no migration of historical entries (forward-only).**
- **DP-4 — scope.** Is a prompts-management *surface* (versioning, selection) in MVP-closure scope, or only the *hash-component binding* (the minimal thing that closes §5.2)? Recommended: **minimal binding first** (close the deferral); fuller prompts-management is a separate forward arc.

## Recommendation

Author the minimal runtime-binding-extension arc: runtime-spec `active_prompt_version` field + a routing-manifest-shaped `PromptManifest` carrier + the resolver's third hash component + the IS spec v1.x amendment, all gated on operator ratification of this fork. This is a **bundled-absorption arc** (design-substrate + harness-runtime/src) → clearance marker owed at the spec-amendment PR. It is **not** greenfield — the spec sketched the path.

## Closeout posture

~~Filed, not resolved. P4 (`R-CL-P4`) is **blocked** on this fork's ratification. No code/spec change lands in this filing arc (P0 is scope-lock only).~~

**RESOLVED 2026-06-11 (APPLIED-AS-MINIMAL-BINDING).** Operator ratified the minimal-binding Recommendation (DP-1..DP-4; mirror `RoutingManifest`). The bundled-absorption arc landed: IS spec v1.4 → v1.5 (§5.2 recipe 2→3-component) + runtime spec v1.41 → v1.42 (§4 C-RT-04 `prompt_manifest` field) + impl (`harness_is.prompt_manifest` carriers; `HarnessContext.prompt_manifest`; 3-component resolver; `MutableHarnessContext` ambient carrier) + tests (participation: snapshot varies with `active_prompt_version`, holds otherwise) + 2 clearance markers + pointer cascade. **R-CL-P4 is now unblocked** (this was the last of its three sub-parts; OD buffer #490, keying-tuple #492 already closed). The fuller prompts-management surface (multi-prompt versioning + selection + a materialization stage) is a separate forward arc per DP-4.

---

## Full-surface forward arc — `R-PM-1` (DP-4 re-opened at FULL scope, 2026-06-11)

**Status:** 🟡 DESIGN-AUTHORED (2026-06-11, HEAD `a73744b`) — `R-PM-1` is arc #2 of the `R-CC-1` capability-completion program (`Project_Roadmap_v1.md` §5.16 + §5.17). Operator confirmed (2026-06-11 AUQ) **FULL-STACK-UPFRONT** scope, re-sequenced **before** R-CL-Q1 (as a capability). The DP-4 deferral above is now re-opened at full scope; the minimal binding (#496) is the **foundation, not a redo**.

**Design artifact:** `.harness/r-pm-1-prompts-management-design-v1.md` (the comprehensive 4-layer design). It resolves the two nameable tensions and sets the distributed-amendment cascade. This fork doc tracks the arc; the design doc carries the decisions.

**The four layers (full scope):** (a) **injection** (runtime — the load-bearing gap; nothing reaches the model today), (b) **selection** (CP — per-role/workload binding mirroring `RoutingManifest`), (c) **versioning/authoring** (IS — extend `PromptManifest`/`PromptVersion` identity → content + versioned store on the PROMPTS path-class), (d) **per-tier governance** (OD — SOLO/TEAM_BINDING/MULTI_TENANT prompt policy).

**Full-surface decision points (resolved in the design doc; named here for the ledger):**
- **DP-5 — injection mechanism.** RESOLVED → **bounded `HarnessContext` channel + translate-time per-provider injection** (Anthropic `system=` kwarg; OpenAI/Ollama `role:"system"` prepend). NOT a change to the frozen `ProviderAgnosticPayload` → **ADR-F1 preserved → no new ADR**. Probe-resolved on primary-source grounds (system is not uniformly representable in the neutral 3-tuple). Resolves tension (ii) C10⊥C11.
- **DP-6 — selection-ownership (IS⊥CP).** RESOLVED → **authoring/versioning = IS; per-role/step/workload selection-binding = CP** (mirrors Skills∘routing; pre-resolved by the `RoutingManifest.per_role_bindings` precedent). Resolves tension (i).
- **DP-7 — artifact structure.** RESOLVED → **distributed per-axis spec amendments** (runtime → IS → CP → OD → CXA), segmented by layer, runtime-injection first. **No new standalone spec, no new ADR** (house style = #496 + the per-axis cost-attribution chain).
- **DP-8 — structured/cached system content + mid-conversation system messages.** DEFERRED (OQ-1/OQ-4 in the design doc) → string-only base prompt at v1; structured/`cache_control` and the `mid-conversation-system` beta are bounded follow-ons.

**Cascade (the owed PR sequence):** #1 runtime injection **+ a minimal inline `content` carrier** (load-bearing, standalone-valuable, **self-provable e2e** — the inline content source ships in #1 so injection is provable before the versioned store lands; per-provider injection + **fail-loud conflict precedence** when an active prompt ⊕ a payload-carried system source collide) → #2 IS versioning/authoring (generalizes #1's inline content into the versioned PROMPTS store) → #3 CP selection → #4 OD per-tier governance → #5 CXA seam registration. Each = bundled-absorption arc (spec amendment + impl + tests + clearance) + adversarial + Codex + advisor review. *(PR #1 self-containment + fail-loud conflict precedence = decorrelated Codex review findings, applied to the design v1.)*

**Precedent:** `[[adr-vs-fork-spec-plan-granularity]]` (fork+distributed-spec, not new ADR) · `[[r-cxa-seam-wiring-is-producer-discovery]]` (seam after producers exist) · `[[verification-shape-sharpened-grep-vs-e2e]]` (injection proven e2e, not grep).
