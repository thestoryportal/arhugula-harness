# R-PM-1 — Full prompts-management surface: 4-layer design (v1)

**Authored:** 2026-06-11 · **Posture:** design-phase (authors only this `.harness/` design artifact + the paired fork-doc extension; **no `design-substrate/**` or `harness-*/src/**` edit in this PR** → X-AL-3-clean). · **Authority:** `Project_Roadmap_v1.md` §5.16 `R-PM-1` (operator-confirmed 2026-06-11 AUQ, FULL-STACK-UPFRONT) + §5.17 `R-CC-1` capability-completion program (arc #2). · **Skill:** systems-architect (Phase-7 architectural design). · **Grounding:** verified by direct read at HEAD `a73744b`; the expensive 2026-06-11 grounding preserved in §5.16 `notes:` re-confirmed here, not re-excavated.

This is the **first deliverable** of R-PM-1 (the roadmap's `close_shape: design-then-impl`). It is the coherent, reviewable 4-layer design that the **distributed per-axis spec-amendment + impl cascade** flows from. It does **not** itself amend any spec or write any impl — those are the segmented follow-on PRs sequenced in §6.

---

## 0. TL;DR (the architectural calls)

1. **Prompt injection is net-new H_T design** [HIGH] — at HEAD nothing routes a system prompt to any provider. → X-AL-3 → this design-phase artifact precedes any impl.
2. **Injection mechanism = bounded `HarnessContext` channel + translate-time per-provider injection** [HIGH] — NOT a change to the frozen `ProviderAgnosticPayload`. Resolves nameable **tension (ii)** (C10 contract-stability ⊥ C11 operator-burden) on **primary-source grounds**: a system prompt is *not uniformly representable* in the provider-neutral 3-tuple (Anthropic = top-level `system=` kwarg; OpenAI/Ollama = `role:"system"` message-list entry), so the per-provider translate functions are the correct seam. **ADR-F1 untouched** → this is a fork-resolution + distributed spec amendments, **not a new ADR**.
3. **Selection-ownership split: authoring/versioning = IS; per-role/step/workload selection-binding = CP** [HIGH] — resolves nameable **tension (i)** (IS ⊥ CP), pre-resolved by the `RoutingManifest.per_role_bindings` precedent. Mirrors exactly how Skills (IS-versioned) compose with routing (CP-bound).
4. **Artifact structure = distributed per-axis spec amendments** [HIGH] — runtime (injection) + CP (selection) + IS (versioning/authoring) + OD (per-tier governance), each its own segmented PR with the **#496 minimal binding as the foundation, not a redo**. There is no dedicated cross-cutting spec in `design-substrate/` (confirmed: cost-attribution, the comparable multi-axis chain, is specced per-axis). **No new standalone spec; no new ADR.**
5. **Both nameable tensions are probe-resolved**, so per §10.9/§13.4 the design **names the voice positions** without a full `/council-workflow` convening.

---

## 1. The grounded gap (4-layer state at HEAD `a73744b`)

All cites verified by direct read this session.

| Layer | What EXISTS at HEAD | What is MISSING |
|---|---|---|
| **(a) Injection** (runtime) | `ProviderAgnosticPayload(messages, tools, params)` — frozen, `extra="forbid"`, **no `system` field** (`harness-cp/src/harness_cp/cp_shared_types.py:89`). The 3 translate fns `_payload_to_{anthropic,openai,ollama}_kwargs(payload)` build kwargs from **exactly** `messages`+`tools`+`params` (`harness-runtime/.../lifecycle/llm_dispatch.py:917-946`). | **The load-bearing piece.** No system-prompt route reaches any provider. Nothing carries the active prompt's *content*; the translate fns have no system parameter. |
| **(b) Selection** (CP) | Precedent only: `RoutingManifest.per_role_bindings: Mapping[AgentRole, RoleRoutingBinding]` + `per_workload_overrides` (`harness-cp/src/harness_cp/routing_manifest_residence.py:118-129`; C-CP-03 §3.5 / C-CP-04 §4.1). | No prompt-selection surface. Nothing resolves *which* prompt version is active for a role/step/workload. |
| **(c) Versioning / authoring** (IS) | `PromptManifest` + `PromptVersion` (#496, IS spec v1.5; `harness-is/src/harness_is/prompt_manifest.py`) — carry a **single `active_prompt_version.version_sha`** (a version *identity*, frozen, empty-defaultable). `PROMPTS` path-class exists (C-IS-01). | The manifest carries an identity, **not content**, and holds **one** version, not a versioned store. No authoring discipline (content→sha). |
| **(d) Per-tier governance** (OD) | `PersonaTier` is first-class (bridging-arc SOLO→TEAM_BINDING→MULTI_TENANT; ADR-D5/D6; tier-distinct gate/redaction/sampler posture proven at R-CL-P3 #481). | No prompt-specific governance: no per-tier redaction/approval posture for prompts. |

**Reachability of the #496 foundation** [HIGH]: the `active_prompt_version.version_sha` already participates in the procedural-tier content hash (IS C-IS-05 §5.2, 3-component recipe) and is operator-suppliable via `RuntimeConfig.prompt_manifest` + stage-0 copy → `HarnessContext.prompt_manifest`. R-PM-1 **widens** this carrier (identity → content + versioned store) and **drives** the selected version from the new CP selection layer; it does not redo it.

---

## 2. Why injection is net-new (the X-AL-3 trigger)

The provider-translate path builds kwargs from the neutral 3-tuple only. An operator *could* smuggle a system prompt through `params` for Anthropic (`kwargs.update(payload.params)` would carry a `system` key), but:
- it is **not** a typed, first-class harness surface (it's the opaque `params` escape hatch);
- it does **not** work uniformly — OpenAI/Ollama read `system` as a `messages` entry, not a top-level kwarg;
- nothing in the harness *populates* it from an active prompt.

So a real, harness-owned, provider-correct prompt-injection capability is **net-new H_T design** → X-AL-3 → design-phase first. [HIGH]

---

## 3. Tension resolutions (both probe-resolved; voices named per §10.9/§13.4)

### 3.1 Tension (ii) — injection-mechanism blast-radius · **C10 (action-safety / contract-stability) ⊥ C11 (operator-loop / local-first burden)**

**The fork (two candidate mechanisms):**
- **Option 1 — bounded `HarnessContext` channel + translate-time injection.** Carry the active prompt *content* on the context (as `prompt_manifest` already rides the context); the dispatcher resolves the active system prompt and passes it to the per-provider translate fn, which places it correctly (Anthropic `system=` kwarg; OpenAI/Ollama prepend `{"role":"system",...}`). **No ADR change.**
- **Option 2 — add `system` to the frozen `ProviderAgnosticPayload`.** A **foundational ADR-F1 touch** (the provider-neutral thin-core 3-tuple is an ADR-F1 §Decision commitment) → Class 1 back-flow against a committed surface.

**Voice positions (named, not convened):**
- **C10 (action-safety/blast-radius):** prefers the *smallest blast radius*. Option 2 mutates a frozen, `extra="forbid"`, ADR-F1-committed contract that 40+ callsites construct — a high-blast-radius change to a foundational type. Option 1 confines the change to the runtime dispatch seam. **C10 → Option 1.**
- **C11 (operator-loop/local-first):** prefers *minimal operator config burden*. Both options are equal on operator burden (the operator supplies prompt content either way); Option 1 adds no new foundational concept to learn. **C11 → neutral/Option 1.**

**Probe-first resolution (the primary source decides — §10.9 amendment 5):** the `claude-api` skill confirms a system prompt is **not uniformly representable** in the neutral 3-tuple — Anthropic takes a **top-level `system=` kwarg**; OpenAI/Ollama take a **`role:"system"` entry in `messages`**; a `role:"system"` array entry is *not honored as a base system prompt by Anthropic* (it is a separate `mid-conversation-system-2026-04-07` beta, model-gated, cannot be `messages[0]`, 400s on unsupported models). Therefore a single `system` field on `ProviderAgnosticPayload` would be **provider-leaky** (the same field maps to a kwarg for one provider and a message-list entry for the others), which is exactly the leak ADR-F1's provider-neutral core forecloses. The asymmetry *is* the architectural rationale: per-provider injection belongs at the per-provider translate seam.

**RESOLUTION: Option 1** — bounded `HarnessContext` channel + translate-time per-provider injection. **`surfaced + probe-resolved`.** ADR-F1 preserved; this is a fork-resolution + distributed spec amendments, not a new ADR. [HIGH]

### 3.2 Tension (i) — selection-ownership · **IS ⊥ CP**

**The question:** prompt authoring/versioning is IS-native (PROMPTS path-class, content store), but per-role/step binding mirrors CP routing — who owns *selection*?

**Voice positions (named):**
- **IS:** owns persistence — the prompt content, its versions, and the content→sha digest discipline live on the `PROMPTS` path-class (C-IS-01) + extend the existing `PromptManifest`/`PromptVersion` carriers.
- **CP:** owns orchestration — *which* version is active for a given role/step/workload is a per-role binding, structurally identical to `RoutingManifest.per_role_bindings`.

**Probe-first resolution:** the `RoutingManifest` precedent (verified: `per_role_bindings: Mapping[AgentRole, RoleRoutingBinding]` + `per_workload_overrides`, C-CP-03 §3.5 / C-CP-04 §4.1, residing in `harness-cp`) **pre-resolves** the split. It mirrors how **Skills** already compose: Skills are IS-versioned (`active_skills_versions`) yet enabled/bound by CP-side discipline. Prompts follow the same seam.

**RESOLUTION:** **authoring/versioning = IS; per-role/step/workload selection-binding = CP.** The selection layer resolves `role/workload → version_sha`; the IS store resolves `version_sha → content`. **`surfaced + probe-resolved`.** [HIGH]

---

## 4. The 4-layer design

Cross-axis dataflow (a new CXA seam family):

```
  PROMPTS path-class store      per-role/workload binding       translate-time injection        per-tier policy
        (IS)                          (CP)                           (runtime)                       (OD)
  content + versions   ──sha──▶  selection: role→version_sha ──▶  resolve content,        ──gate──▶ redaction/approval
  (authoring)                    (mirrors RoutingManifest)        place per-provider                by PersonaTier
                                                                  (system= | role:system)
```

### 4.1 Layer (a) — INJECTION (runtime spec; the load-bearing piece)

**Contract (new runtime surface, e.g. a `C-RT-NN` adjoining the C-RT-15 LLM-dispatch composer at `Spec_Harness_Runtime_v1.md` §14.5):**

- `HarnessContext` (or its `prompt_manifest`) resolves to an **active system-prompt content string** (possibly empty → no injection) at dispatch time. The selection layer (§4.2) chooses the version; the IS store (§4.3) yields its content.
- **Content source for PR #1 (self-contained — Codex finding):** PR #1 cannot prove injection e2e if the content store is deferred to PR #2. So **PR #1 adds a minimal inline content carrier** — an optional `content: str` on `PromptVersion` (or directly on the manifest) — so a single operator-supplied active prompt injects + proves e2e *within PR #1*. PR #2 (versioning/authoring) then **generalizes** this inline field into the multi-version `PROMPTS`-path-class store + content-addressing. The inline carrier is the minimal thing that makes PR #1 standalone-valuable and self-provable; #2 is a superset, not a redo.
- The 3 translate fns gain a system parameter — `_payload_to_{provider}_kwargs(payload, system: str | None)` — and inject **per-provider**:
  - **Anthropic** → `if system: kwargs["system"] = system` (top-level kwarg).
  - **OpenAI / Ollama** → if `system`, **prepend** `{"role": "system", "content": system}` to the messages list.
- **Conflict precedence — fail-loud / detect-then-refuse (Codex finding):** an active prompt is the harness-owned **base** system prompt. If an active prompt is configured **AND** the payload already carries a competing system source — an OpenAI/Ollama leading `role:"system"` message, or an Anthropic `params["system"]` (the opaque escape hatch) — the two-source ambiguity is **raised as a fail-loud error**, not silently resolved (consistent with the arc-#1 `detect-then-refuse` posture, `RT-FAIL-SANDBOX-DRIVER-UNAVAILABLE`, and `[[conformance-validator-disciplines]]`). v1 does **not** silently replace/merge — silently dropping either the operator's payload system message or the configured active prompt is the failure mode. (A future explicit `merge`/`replace` policy field is a bounded follow-on if a real workload needs both sources — OQ-5.) With **no** active prompt configured, behavior is byte-identical to today (existing payload system messages pass through untouched).
- `ProviderAgnosticPayload` stays **frozen and unchanged** (ADR-F1 preserved). The system content rides the context/dispatcher, not the payload.
- **Empty/None → no injection** (zero behavior change for configs without prompts — the local-first default, C11).

**Acceptance (the load-bearing must_pass, made specifiable):**
> On a real dispatch with an active prompt configured, the active prompt's **content** arrives at the provider as a system prompt: Anthropic `messages.create` kwargs contain `system=<content>`; OpenAI/Ollama `messages[0] == {"role":"system","content":<content>}`. With no active prompt, kwargs are byte-identical to today.

Verifiable **e2e** via the free **Ollama** path (no paid call) and/or a recording mock dispatcher asserting the kwargs shape — *not* grep (`[[verification-shape-sharpened-grep-vs-e2e]]`).

### 4.2 Layer (b) — SELECTION (CP spec)

- A CP-axis prompt-selection surface mirroring `RoutingManifest`: `per_role_bindings: Mapping[AgentRole, PromptBinding]` + optional `per_workload_overrides`, resolving `role/workload → active prompt version_sha`. Reuses the `AgentRole` shared type (U-CP-00c).
- Resides in `harness-cp` (the per-role-binding precedent), operator-supplied on the manifest, read at dispatch — the U-CP-60 operator-supplied-substrate-at-`__init__` pattern the resolver already uses for skills/routing.
- **Default = empty binding** → falls through to a single/no active prompt (the #496 behavior). Selection only *adds* resolution; it doesn't gate whether dispatch runs (variability-in-values, not control-flow).
- Authored against C-CP-02 / C-CP-03 §3.5 / C-CP-04 §4.1 (delta-chain: definitions live in the last full re-table — to be byte-resolved by spec-writer at amendment time via `just overlay-query`, not from the v1.30 delta head).

### 4.3 Layer (c) — VERSIONING / AUTHORING (IS spec)

- Extend `PromptManifest` / `PromptVersion` (#496 foundation) from a **single active-version identity** to a **versioned content store**: multiple `PromptVersion`s on the `PROMPTS` path-class (C-IS-01), each carrying **content + a content-addressed `version_sha`** (sha = digest of content — the authoring discipline, mirroring the routing-manifest plain-text-in-git pattern).
- The existing `active_prompt_version.version_sha` (which feeds the C-IS-05 §5.2 procedural-tier hash) becomes "the currently-selected version's identity," now *driven by* the CP selection layer (§4.2). **No change to the 6-field ledger shape, hash-chain, or seam exports** (forward-only, as #496 was).
- Authoring = operator places prompt files on the `PROMPTS` path-class; the sha is derived deterministically. Selection (CP) references versions by sha; injection (runtime) resolves sha → content.

### 4.4 Layer (d) — PER-TIER GOVERNANCE (OD spec)

- Persona-tier-aware prompt policy composing with the bridging-arc `PersonaTier` (ADR-D5/D6; proven tier-distinct at R-CL-P3 #481), owned by OD (redaction + approval are OD primitives):
  - **SOLO** → no approval gate, no redaction (local-first, minimal burden — C11).
  - **TEAM_BINDING** → approval gate on prompt-version changes (a shared prompt is a team artifact; mirrors the SYNC/BOTH_BY_TIER gate posture proven at #481).
  - **MULTI_TENANT** → redaction (prompts may carry tenant-specific content at the collector boundary) + approval.
- Composes with, does not duplicate, the existing tier-distinct gate/redaction posture; it *extends* it to the prompt artifact class.

---

## 5. What this resolves vs. what stays open

**Resolved by this design** [HIGH]: the two nameable tensions; the injection mechanism (ADR-F1-safe); the selection-ownership split; the artifact structure (distributed amendments, no new ADR/spec); the foundation-not-redo relationship to #496.

**Deliberately deferred / open:**
- **OQ-1** [MODERATE] — should a prompt version support **structured/multi-block** system content (Anthropic supports a `system` *array* with `cache_control` breakpoints for prompt-caching), or string-only at v1? *Recommendation:* string-only at v1 (the neutral surface); structured/cache-control is a bounded follow-on. Surface at the runtime-injection amendment.
- **OQ-2** [MODERATE] — prompt-caching interaction: a stable injected system prompt is an ideal cache prefix (`shared/prompt-caching.md`). Out of scope for the capability landing; note as a perf follow-on (folds toward R-CL-Q-track).
- **OQ-3** [SPECULATIVE] — does selection belong to *per-role* binding, *per-step* override, or both? The RoutingManifest precedent has both (`per_role_bindings` + `per_workload_overrides`); v1 mirrors both, but the per-step override may be thin-latent until a workload exercises it. Confirm at the CP amendment.
- **OQ-4** [MODERATE] — `mid-conversation-system` (the Anthropic beta) for *operator instructions mid-run* is a distinct, later capability (the injection here is the *base* system prompt). Explicitly out of R-PM-1 scope; note as a forward capability.
- **OQ-5** [MODERATE] — explicit conflict-resolution policy (active prompt ⊕ payload-carried system source). v1 is **fail-loud** (§4.1). A configurable `merge` / `replace` policy field is a bounded follow-on **iff** a real workload needs both sources simultaneously; until then, fail-loud surfaces the ambiguity rather than silently picking. Surface at the runtime-injection amendment (PR #1).

None of these block the cascade; each is surfaced at its layer's amendment PR.

---

## 6. Artifact structure + cascade plan (the segmented follow-on PRs)

**Structure** [HIGH]: distributed per-axis spec amendments, **no new standalone spec, no new ADR** (Option 1 does not touch a foundational ADR). The house style is #496 (which amended IS v1.5 + runtime v1.42 for *this same* capability) and the cost-attribution chain (specced per-axis across OD+CP+runtime, no cross-cutting spec — confirmed by `ls design-substrate/`). Sequence (systems-architect design → spec-writer cascade → phase-7 impl), **runtime-injection first** (the "nothing reaches the model today" load-bearing piece):

| # | PR (bundled-absorption arc: spec amendment + impl + tests + clearance) | Layer | Why first/next |
|---|---|---|---|
| **#1** | **Runtime injection + minimal inline content** — runtime spec new `C-RT-NN` §14.5-adjacent (translate-time per-provider injection + fail-loud conflict precedence) + `HarnessContext` active-content resolution + **a minimal inline `content: str` on `PromptVersion`** (the self-contained content source); impl at `_payload_to_*_kwargs` + dispatcher; **e2e proof (Ollama/mock)** the content reaches the provider. | runtime (+ minimal IS carrier) | The load-bearing gap. Closes "nothing reaches the model"; self-provable e2e because the inline content carrier ships here (Codex finding). Standalone-valuable: a single operator-supplied prompt injects before selection/versioning land. |
| **#2** | **Versioning/authoring** — IS spec amendment: **generalize** PR #1's inline `content` into the multi-version `PROMPTS`-path-class store + content-addressed sha; authoring discipline. | IS | Generalizes the #1 inline carrier (superset, not redo); extends the #496 identity carrier to a versioned store. |
| **#3** | **Selection** — CP spec amendment: per-role/workload prompt-binding mirroring `RoutingManifest`. | CP | Drives *which* version injection resolves; depends on #2's version identities. |
| **#4** | **Per-tier governance** — OD spec amendment: SOLO/TEAM/MULTI_TENANT prompt policy. | OD | Wraps the landed surface; composes with the R-CL-P3 tier posture. |
| **#5** | **CXA seam** — register the PROMPTS(IS)→selection(CP)→injection(runtime)→governance(OD) composition in `Cross_Axis_Composition_Document` (per `[[r-cxa-seam-wiring-is-producer-discovery]]` — wire only real producer/consumer seams). | CXA | After the producers exist. |

Each PR: adversarial pre-merge review + `just codex-review` (out-of-family) + advisor; clearance marker; overlay-check; roadmap fixed-point refresh. The fork doc (§extension below) tracks the arc.

---

## 7. Acceptance criteria (R-PM-1 `must_pass`, made specifiable)

1. A comprehensive prompts-management design covers all 4 layers (injection + selection + versioning/authoring + per-tier governance), cleared via clearance markers as each layer's spec amendment lands. — *this doc is the design; the amendments carry the markers.*
2. **The active prompt's CONTENT reaches the provider as a system prompt on a real dispatch** (injection proven e2e — Anthropic `system=` kwarg / OpenAI-Ollama `role:system` message; not just version-identity in the ledger hash). — *PR #1 AC, §4.1.*
3. Selection resolves which prompt is active per role/step/workload. — *PR #3 AC, §4.2.*
4. Per-tier (persona) prompt-governance posture distinct across SOLO / TEAM_BINDING / MULTI_TENANT. — *PR #4 AC, §4.4.*

---

## 8. Provenance + reviewers

- **Grounding** (direct read, HEAD `a73744b`): `cp_shared_types.py:89` (frozen payload, no `system`); `llm_dispatch.py:917-946` (3 translate fns, messages+tools+params only); `prompt_manifest.py` (#496 identity-only carrier); `routing_manifest_residence.py:118-129` (per-role binding precedent); `ls design-substrate/` (per-axis-only specs, no cross-cutting spec).
- **Primary source** (linchpin): `claude-api` skill — Anthropic `system=` top-level kwarg; `role:"system"` array entry is a model-gated beta, not the base-prompt route. Probe-resolves tension (ii).
- **advisor()** consulted pre-authoring: affirmed design-artifact-this-session/impl-later segmentation; sharpened the injection rationale to the provider-asymmetry primary-source argument; confirmed distributed-amendments (not new ADR/spec); directed extend-the-fork-doc.
- **Reviewers owed at this design PR:** harness-adversarial-reviewer (pre-merge) + `just codex-review` (out-of-family, decorrelated) + advisor (pre-done).
- **Patterns:** `[[r-cxa-seam-wiring-is-producer-discovery]]` · `[[grounding-reveals-claude-closeable-slice-close-honestly]]` · `[[verification-shape-sharpened-grep-vs-e2e]]` · `[[adr-vs-fork-spec-plan-granularity]]` (fork+spec, not new ADR) · `[[harness-persona-is-bridging-arc-multi-tier]]` (tier governance).

---

*End R-PM-1 4-layer design v1. Next: extend the prompts-management fork doc (DP-5..DP-8 for the full-surface arc); then PR this design; then the §6 cascade, runtime-injection first.*
