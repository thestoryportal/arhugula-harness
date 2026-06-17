# Class 1 Fork — B4 per-role prompt threading ⊥ procedural-tier hash coherence

**Filed + RESOLVED:** 2026-06-17 · R-FS-1 arc B4 (per-role / per-step dispatch indexing), bundled-absorption posture (IS spec §5.2 + `harness-*/src`). Class 1 (cross-axis: runtime per-role prompt injection ↔ IS C-IS-05 §5.2 procedural-tier hash recipe). Resolved with rationale + decorrelated review (reversible, additive recipe extension; **no operator gate** — composes a precedented additive recipe component mirroring `routing_manifest_sha`; no ADR / six-field / §6 hash-chain / §7 read-write change; the design back-flow is FULL-SPEC-pre-authorized per `[[feedback-full-spec-beyond-mvp-nothing-deferred]]`).

**Status:** ✅ RESOLVED → 4th recipe component `prompt_selection_manifest_sha`. IS-side recorded at `Spec_Information_Substrate_v1.md` §5.2 (v1.8 → v1.9); runtime impl co-lands in the same PR (per-role prompt threading + recipe extension).

## §1 The fork

B4 makes the per-role **prompt** take effect: a fan-out branch's `step_context.agent_role` selects a per-role prompt (`PromptSelectionManifest.per_role_bindings[role]` → `version_sha` → store content) whose `content` is injected as the provider system prompt at the §14.5.2 translate seam. The per-role **model** half already landed (B1 arc #14, U-RT-114, §14.5.3); per-role prompt is the B4 increment.

The coherence problem surfaced at arc-open grounding. The C-IS-05 §5.2 procedural-tier hash recipe (v1.8) reads exactly three components:

```
active_prompt_version    = ctx.prompt_manifest.active_prompt_version.version_sha   # resolved DEFAULT-role version only
active_skills_versions   = sorted skills version_shas
routing_manifest_sha     = SHA-256 over the WHOLE ctx.routing_manifest canonical-JSON
```

The recipe does **not** hash the prompt-*selection* manifest. The default-role path stays coherent only because `reconcile_active_prompt_via_selection` *mutates* the single `active_prompt_version` (so both the §14.5.2 injection reader `.content` and the §5.2 hash reader `.version_sha` read the same selected member). A per-role injection cannot share that one slot — N roles need N versions. So a side-resolved per-role prompt that is read **only** at injection time is invisible to the hash:

> Flip `per_role_bindings["researcher"]` from `sha1` → `sha2`. The "researcher" branch's injected system-prompt content changes, but `active_prompt_version.version_sha` (and therefore the procedural-tier snapshot) is **unchanged** — the exact drift the §14.5.2 invariant forbids ("the §5.2 procedural-tier hash cannot report 'unchanged' while injected content changes"), now reintroduced for the per-role dimension.

**The discriminating tell:** the recipe *already* hashes the **whole** `routing_manifest` — so the routing manifest's `per_role_bindings` **are** hash-visible. The prompt-selection manifest's `per_role_bindings` are not. The asymmetry is the gap.

This is X-AL-3 territory: closing it requires extending a cleared IS spec contract (the §5.2 recipe). Under the FULL-SPEC directive that design back-flow is **pre-authorized** — but it must be **authored** (this fork + spec amendment + clearance + spine registration), not silently absorbed.

## §2 Resolution — 4th recipe component `prompt_selection_manifest_sha`

| Route | Mechanism | Assessment |
|---|---|---|
| **A — fold per-role shas into `active_prompt_version`** | Make the component a sorted set of `{default + per-role}` resolved shas. | **Rejected.** Breaks the single-active-version semantics the §14.5.2 injection reader (`active_prompt_version.content`) depends on; N roles can't share one inline record; high blast radius on both readers. |
| **B — hash only the *resolved* per-role versions** | Add `sorted((role, resolved_sha))` for roles that resolve for the run's workload. | **Rejected.** Incomplete (a binding that doesn't resolve for *this* run's workload is still part of the procedural config and should be hash-visible) + asymmetric with how `routing_manifest_sha` hashes the whole manifest. |
| **C — whole-selection-manifest hash** | Add `prompt_selection_manifest_sha = SHA-256 over the whole `PromptSelectionManifest` canonical-JSON bytes` (`""` when `None`), **exactly mirroring `routing_manifest_sha`**. | **CHOSEN.** Symmetric with the existing routing treatment, complete (captures default + per-role + per-workload bindings), precedented, additive, forward-only. Any change to the selection manifest is hash-visible. |

**Recipe v1.8 (3-component) → v1.9 (4-component)**, alphabetically ordered:
`{active_prompt_version, active_skills_versions, prompt_selection_manifest_sha, routing_manifest_sha}`.
`prompt_selection_manifest_sha` reads `HarnessContext.config.prompt_selection_manifest` — the operator-supplied `RuntimeConfig` field that is the selection manifest's spec'd home (`None` → `""`, the empty-selection sentinel, byte-identical to no-selection). **No new top-level `HarnessContext` carrier** (and therefore no runtime-spec §4 C-RT-04 field row): unlike `prompt_manifest`/`routing_manifest` — which are stage-0-reconciled / stage-3b-enriched, so the ctx carrier holds a *different* value than config and must be a top-level field the recipe reads — the selection manifest is NOT stage-enriched (the resolver reads the same value config carries). Adding a dedicated carrier would be impl-ahead-of-spec drift on C-RT-04 for zero benefit (advisor pre-done review caught the initial dedicated-carrier draft as exactly this drift). The stage-0 per-role *injection-map* builder (`resolve_per_role_system_prompts`) also reads `config.prompt_selection_manifest`; only the resolved `dict[AgentRole, str]` is carried on the mutable bootstrap ctx (builder-transient, consumed by the stage-5 dispatcher factory — not a frozen `HarnessContext` field).

**Forward-only rebase**, zero migration of historical entries — exactly as the §5.2 prose has anticipated since v1.3 ("Hash rebasing … is expected … snapshot-ref equality is scoped within a single recipe-version generation"). **ZERO change to** the §5 six-field shape / §5.1 sidecar / §6 hash-chain / §7 read-write / §10 seam exports — the recipe-internal component count is a §5.2 resolver detail (the same framing the v1.5 prompt-component binding used).

**Why coherent.** The selection manifest binds `version_sha`s; `version_sha` is content-derived (`== prompt_version_sha(content)`, IS §5.2 v1.6 derive-invariant); the store is content-addressed. So hashing the selection manifest captures any per-role injected-content change — the §14.5.2 invariant is restored for the per-role dimension.

## §3 Decorrelated review

advisor (pre-substantive, full transcript) — caught that the grounding sweep's "Slice 1 = impl, no fork" read missed the §5.2 hash-coherence dimension; named the discriminating check ("does the snapshot hash the selection manifest, or only `ctx.prompt_manifest`?"); confirmed impl→impl+fork once the snapshot inputs were grounded (recipe reads only the default-role `active_prompt_version.version_sha`). Plus the `routing_manifest_sha` precedent (the asymmetry that decides Route C). Codex out-of-family review at PR.

## §4 Spine registration

Registered at `.harness/beyond-mvp-capability-boundary-ledger.md` (B4 sub-fork, closed in-arc — not a defer) per `[[spine-ledger-forward-arc-registration]]`.
