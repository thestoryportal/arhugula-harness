---
title: Post-MVP Full Harness Closure Plan
version: v1
status: execution-plan (operator-directed post-MVP closure spine)
created: 2026-06-10
posture: mode-agnostic (process-substrate; plans design-substrate + Phase-7 work, edits neither here)
authority: operator directive 2026-06-10 ("develop the full harness to closure")
grounded_at_head: 3d8fd76
builds_on:
  - .harness/post-phase-8-forward-register.md (the forward-surface inventory)
  - Project_Roadmap_v1.md + .harness/roadmap_status.md (R-NNN tracking)
  - .harness/01-planning/01-harness-planning/00-harness-research/phase-9-retirement-criteria.md (the bounded-residual promotion decision model)
  - .harness/release-candidate-deployment-readiness-runbook.md (the RC arc this plan succeeds)
supersedes: none (this is the execution spine; the register/roadmap/phase-9 doc remain their own surfaces)
---

# Post-MVP Full Harness Closure Plan (v1)

*The step-by-step / phase-by-phase path to **full closure of the harness specification** — every spec-committed surface built, activated, tested to 100% evidence, DevEx/QA/security-reviewed, code-reviewed for clean/simple/commented code, packaged for portable deployment, and documented. This is the governing plan for the post-MVP development arc.*

---

## §0. Framing + structural decisions (revisable)

### 0.1 What "full closure" means here

Closure = for every canonical spec contract (`C-IS-*`, `C-AS-*`, `C-CP-*`, `C-OD-*`, `C-RT-*`) and every CXA seam and ADR commitment, the surface is:

1. **Built** — the spec-committed capability exists in `harness-*/src/` (not just declared/stubbed).
2. **Activated** — wired into a real production path (not library-present-but-uncalled).
3. **Verified** — 100% testing evidence *by execution* (e2e / use-the-product), not grep-or-unit-only (`[[verification-shape-sharpened-grep-vs-e2e]]`). **Honest "100%":** every *buildable* surface gets executed-path proof; *deployment-gated* surfaces (Cat-2 — the external engines) get reference/deterministic proof now + **operator-gated live-proof later** (D-2). "100%" = "100% of what's buildable without your infra is proven; the rest is proven the moment you provision it" — not a promise the deployment-gated reality can't keep.
4. **Reviewed** — clean, simplified, clearly-commented code that passes decorrelated review (advisor + codex) + adversarial review.
5. **Hardened** — DevEx + security + QA gates passed.
6. **Packaged** — portable, reproducible deployment artifacts per deployment tier.
7. **Documented** — feature/functionality, dependency, user/operator, deployment, and architecture docs.

### 0.2 The honest starting point (reframe — read first)

**MVP + the RC arc already closed almost all *capability activation*.** All 3 deployment tiers are proven live, multi-LLM fallback is exercised, multi-tenant is proven, every external integration (Files / managed-agents / memory-backends / MCP) is live, all 5 CXA seams are retired (54/54 substitutions). So this plan is **not** a from-scratch build — it closes a **specific residual frontier** plus adds the full quality/packaging/docs apparatus the MVP deliberately stopped short of.

The residual frontier (grounded at HEAD `3d8fd76`, categorized by *nature* because nature decides whether a surface is "development" at all):

| Cat | Nature | Surfaces |
|---|---|---|
| **1** | Buildable now (Claude-closeable) | Routing intelligence (EMBEDDING + LLM_AS_ROUTER layers — only DECLARATIVE-echo is bound today; **Cat-1 *iff* the layer decision-fn contracts are spec'd at C-CP-02 §2.2 — else the embedding-model / router prompt+output choices are Cat-3 design-gated → fork-before-build; resolve this build-vs-fork discriminator at P1 entry, not assumed here**); engine-recovery **driver** (PR #475 substrate is unwired); OD tail-keep bounded-buffer; the 22 CXA phase-2-runtime edges (likely mostly 0-wireable — verify); spec-prose↔impl drift hygiene |
| **2** | Deployment-gated (bind at deploy, don't vendor — I-6) | The 4 external `EngineClass` recovery adapters (Temporal / K8s / Kafka / save-point); cost-attribution rate tables; cross-SDK conformance |
| **3** | Operator-decision-gated (design, not impl) | Persona-tier breadth (TEAM_BINDING middle of the bridging-arc); prompts-management surface + `active_prompt_version` 3rd hash component (no surface exists today); keying-tuple↔entry-shape D-ADR; ICM adoption |
| **4** | Deliberately deferred (closed-at-spec via impl-discretion) | git cadence, canonicalization library binding, worktree naming, composer caching shape, validator-tier thresholds — **not pending development**; confirm-and-record, don't build |

### 0.3 Structural decisions taken (REVISE ANY — they shape the whole plan)

These two choices are load-bearing for the phase structure. I took the project-consistent default for each; redirect if you'd shape them differently.

- **D-1 — Quality-gate model = HYBRID.** Each capability phase ships with functional code + 100% test evidence + targeted decorrelated/adversarial review *before the next opens*; PLUS dedicated end-phases for the **consolidated** security audit, whole-codebase code-review/simplification sweep, portable packaging, and the docs suite. *Rationale:* per-phase gates keep quality continuous (no big-bang debt), but final security/code-review/packaging/docs genuinely benefit from stable, complete features — you cannot write final user docs or threat-model the whole against a moving target. *(Alternatives: fully-embedded per-phase quality with no end-phases; or capability-first-then-one-quality-block.)*
- **D-2 — Deployment-gated scope = BUILD-SEAM-DEFER-LIVE-PROOF.** For Cat-2 items, build the typed seam + a reference/mock adapter + deterministic tests now (Claude-closeable, framework-pull-clean); **live-proof is an operator-gated sub-step per engine**, exactly as the RC arc handled E2B/GCP/S3. *Rationale:* matches the whole project's `[[grounding-reveals-claude-closeable-slice-close-honestly]]` pattern + I-6 (don't vendor Temporal/K8s/Kafka). *(Alternative: full live-proof in-scope now — you provision real Temporal/K8s/Kafka, I drive each live.)*

### 0.4 Relationship to existing artifacts

This plan is the **execution spine**. It does not replace: the **forward register** (surface inventory), the **roadmap** (R-NNN tracking — each phase below seeds R-NNN entries), the **phase-9-retirement-criteria** doc (the bounded-residual *promotion decision model* — applied at Phase C1), or the **RC runbook** (the deployment-readiness arc this succeeds). It is process-substrate; it carries **no X-AL-3 weight** (it plans design-substrate work but edits none here).

---

## §1. Always-on disciplines (every phase, independent of the phase's content)

These are the non-negotiable per-phase mechanics — they make "100% evidence + clean code" structural rather than aspirational. They compose the workspace's existing apparatus (root `CLAUDE.md` §13–§14).

| Discipline | Rule |
|---|---|
| **Ground-first at phase entry** | Re-verify the phase's surfaces against HEAD before building — **do not trust this plan's snapshot** (`[[reground-forward-work-dont-trust-stale-slice-exhausted]]`, `[[subagent-landscape-reports-need-regrounding]]`). Use `just overlay-query` to resolve cites to carriers (§13.1). |
| **Fork-before-build on unspecified contracts** | If a surface is genuinely unspecified (e.g. prompts surface, keying-tuple D-ADR), file a Class-1 fork + route to design-phase FIRST — building against absence is X-AL-3 (`[[grounding-reveals-claude-closeable-slice-close-honestly]]`, `[[halt-route-split-ac-pattern]]`). |
| **100% evidence = by execution** | A phase closes only on an **e2e / use-the-product** proof of the real path, not a green unit test of an unreachable path (`[[use-the-product-probe-pattern]]`, `[[test-bypass-as-runtime-truth-pattern]]`). Every touched spec contract gains ≥1 executed-path proof. |
| **Decorrelated review per merge** | `advisor()` (transcript-aware) at decision-forks + pre-done; `just codex-review` (out-of-family, $0) on every concrete diff — the two are decorrelated; surface disagreements (§13.1). Codex earned its keep hard on PR #475 (6 real bugs). |
| **Adversarial + council pre-merge** | Red-team each capability arc with `harness-adversarial-reviewer` before merge; convene a **dyadic council** when the phase carries a nameable cross-domain tension (flagged `⚖️` per phase below) per §10.9 + §13.2. |
| **Clean-as-you-go** | Karpathy code-craft (§14.6): simplest thing that solves it, surgical changes, clear comments, every line traces to the spec. The big simplification sweep is Q1, but each phase ships clean. |
| **Roadmap + memory hygiene** | Per §12: post-merge audit → dashboard refresh (terminating-refresh fixed point); save patterns at cardinality ≥2; update this plan's phase status. |
| **Posture honesty** | Phase 7 (`harness-*/src`) vs design-phase (`design-substrate/**`) vs mode-agnostic (`.harness/`) — declare per arc; bundled-absorption arcs carry a clearance marker (§11). |

**Orchestration per phase (§13.2 matrix):** solo for mechanical/linear; `advisor()` at forks; `codex-review` on diffs; **council** only where a `⚖️` tension is named; **adversarial reviewer** pre-merge; **Workflow** (multi-agent) only with explicit operator opt-in for a broad parallel sweep (e.g. the Q1 whole-codebase review or the C1 coverage audit).

---

## §2. The phase map

Dependency-ordered. Capability phases (P) → cross-cutting hardening (Q) → docs (D) → closure (C). Each runs the §3 per-phase template.

### Phase 0 — Ground + scope-lock  `[gate: scope frozen]`

**Goal.** Kill the stale-snapshot risk: re-verify every Cat-1..4 surface against HEAD, freeze the authoritative work-list, and file the design-gated forks *before* any build phase opens.

**Work.**
- Re-ground each surface in §0.2 against HEAD (overlay-query + direct reads); correct any drift from this plan's snapshot.
- **Re-verify the forward register's CLOSED claims too, not just the open surfaces.** The register was stale-*optimistic* on routing (claimed activated; was an echo) — so its other "closed by this PR" marks (B-3..B-14) may also overstate. A stale-closed item silently enlarges the frontier this plan scopes; HEAD-check each closed claim with the same rigor.
- Produce a **scope-locked work-list**: per surface → {built? activated? tested? cat} with cite-to-carrier.
- **File Class-1 forks** for the genuinely-unspecified design-gated surfaces: (a) prompts-management surface + `active_prompt_version` (IS C-IS-05 §5.2); (b) keying-tuple↔entry-shape D-ADR (IS C-IS-07 §7.4). Route to design-phase; do not pre-build.
- Confirm the Cat-4 impl-discretion footers are satisfied-or-explicitly-bound (record; don't build).
- Seed R-NNN roadmap entries for every P/Q/D/C phase.

**Verification.** A reviewed scope-lock doc + the filed forks + the R-NNN seeds. **Exit:** operator ratifies the frozen scope (one AskUserQuestion).

### Phase P1 — Routing intelligence  `⚖️ council (cost ⊥ reliability ⊥ capability-preservation)`

**The #1 capability gap.** Today only `RoutingLayer.DECLARATIVE` is bound and it's an **echo-placeholder** (`llm_dispatch.py:489` `_declarative_echo`); `EMBEDDING` + `LLM_AS_ROUTER` are unbound (`routing_layer.py`). The harness is named "capability-aware multi-LLM" — this is the core unbuilt capability.

**Work (CP spec C-CP-02/03/04 + ADR-F1 §Consequences(c)).**
- Replace the DECLARATIVE echo with a real capability-matching decision (manifest-declared capability requirements → provider capability check).
- Build the `EMBEDDING` layer decision fn (cheapest-deterministic classifier) + the `LLM_AS_ROUTER` escalation layer, in the fixed `DECLARATIVE → EMBEDDING → LLM_AS_ROUTER` order with per-layer `LayerBudget` (C-CP-03).
- **Capability-shortfall fallback** (C-CP-04 + ADR-F1): route to a capable provider *before* a step fails when the primary lacks a required capability (e.g. extended-thinking), with NO LCD flattening (Anthropic prompt-caching / extended-thinking / batch / MCP-host must stay reachable).

**Build-vs-fork discriminator (resolve at entry — the CXA-2 lesson).** This phase is "buildable" *only if* C-CP-02 §2.2 actually pins the layer decision-fn contracts (which embedding model + similarity threshold for EMBEDDING; the routing-prompt + output contract for LLM_AS_ROUTER). If §2.2 only *names* the 3-layer structure and leaves those choices open, the embedding-model / router-contract decisions are **design-gated → file a Class-1 fork (or council the contract) before building**, not silent impl (X-AL-3). Verify the §2.2 cite at P1 entry per §1 ground-first; the CP spec is a delta chain, so resolve C-CP-02 to its last substantive definition, not just the v1.30 head.

**Council.** Convene the cost-voice + reliability-voice dyad (+ capability-preservation) on the selection policy — cheapest-first ⊥ when-to-escalate/fallback ⊥ don't-route-a-thinking-step-to-a-cheaper-non-thinking-model.

**Verification.** Live e2e: a step with a capability requirement the primary lacks routes to a capable provider; an embedding/LLM-router escalation fires on an ambiguous route; budgets bound each layer. Multi-provider, exercised.

### Phase P2 — Engine-recovery activation  `⚖️ council (C10 blast-radius ⊥ C11 operator-burden)`

> **STATUS: DEFERRED (entry-grounding 2026-06-10, advisor-confirmed — `.harness/r-cl-p2-engine-recovery-grounding.md`).** Grounding found the buildable, non-hollow Phase-7 slice empty. The engine-recovery **driver** is a *ratified* batch-55 bounded-residual (forward-register line 181 forbids faking it; I-6 forbids vendoring the engines that would produce engine-layer pauses) — not an open build. The **SAVE_POINT** adapter is speculative (zero consumers — the loop is dormant). **HITL OQ-5/7** are hollow (no fallback/breaker × loop composition; no per-tool-call turn journal); **OQ-6** is thin-latent (no timeout config path → captured as a Q-phase robustness latent gap). Do **not** bind the #475 Journal substrate into the factory (cosmetic; would force a closed-`PathClass`-enum extension = IS-AL-1). The roadmap entry's bundled "sandbox driver→dispatch wiring (C-1)" is **unbundled** to an R-410-family finding (production tier→driver selection is unwired — enforcement is test-injection-only; design-adjacent → file-don't-build). Re-open per the batch-55 DP-2 trigger. **Next phase = P3.**

**Goal.** Make the engine recovery loop non-dormant (closes CXA-2's re-open trigger to the buildable extent) + lay the external-engine seam.

**Work.**
- **Wire a production driver** for `RuntimeEngineRecoveryLoop`; bind the **durable F2 substrate** (PR #475 `JournalEnginePauseResumeSubstrate`) as the production substrate for `PURE_PATTERN_NO_ENGINE`/`JOURNAL_RESUME`. Decide the journal-path placement (the IS path-class question PR #475 deferred).
- Build the **external-engine adapter seam**: a `SAVE_POINT_CHECKPOINT` reference adapter (the one external class with any production substrate today — LangGraph checkpointer) + deterministic tests, as the template for `EVENT_SOURCED_REPLAY`/`RECONCILER_LOOP`/`WAL_SEGMENT` (Cat-2 — build the contract + reference, **do not vendor**; live-proof per-engine deferred per D-2).
- Activate the model-driven HITL tool-loop depth (brief OQ-5/6/7: cross-family fallback id-stability, in-loop timeout degradation, mid-loop breaker replay).

**Council.** C10 (real isolation/recovery integrity) ⊥ C11 (minimal per-deployment provisioning) on the journal-path + adapter-binding burden.

**Verification.** e2e: a real recovery cycle drives the bound durable substrate end-to-end (capture → process restart → resume); the SAVE_POINT reference adapter passes its deterministic contract test; CXA-2 disposition re-evaluated against the phase-9 promotion model (P-C1).

### Phase P3 — Persona-tier breadth  `⚖️ council (C7 observability + C8 security ⊥ C11 operator-burden)`

**Goal.** Activate + exercise the **TEAM_BINDING** middle tier of the bridging-arc (`solo → team-binding → multi-tenant-compliance`; `[[harness-persona-is-bridging-arc-multi-tier]]`). MULTI_TENANT is proven (R-500); SOLO is the MVP default; TEAM_BINDING is the gap.

**Work.**
- Exercise TEAM_BINDING across the axes: HITL gate posture (operator-approval, per `material_diff_detection.py:198`), redaction/audit ceremony, sampler base-rate (C-OD-10 §10.3 8-row table), cost-attribution per-tier.
- Reconcile the root `CLAUDE.md` §10.2 drift ("Solo developer" lossily compresses the multi-tier persona) — design-substrate posture; clearance marker.

**Council.** How much redaction/audit/HITL ceremony is mandatory at TEAM vs MULTI_TENANT vs the operator-burden cost.

**Verification.** Live multi-tier e2e: a TEAM_BINDING workflow exhibits the correct gate/redaction/sampler posture distinct from SOLO and MULTI_TENANT.

### Phase P4 — Spec-completion deferrals (design-gated)  `[depends: P0 forks ratified]`

**Goal.** Close the IS/OD spec surfaces that need design *then* build (the P0 forks must be ratified first).

**Work.**
- **Prompts-management surface** + `active_prompt_version` field + the **3rd procedural-tier hash component** (IS C-IS-05 §5.2; `procedural_tier_snapshot.py` confirms it's absent). Build the prompts manifest carrier + wire the resolver's 3rd component + rebase the hash.
- **Keying-tuple↔entry-shape D-ADR** (IS C-IS-07 §7.4) — author the deferred ADR, then absorb.
- **OD tail-keep bounded-buffer bounds** (C-OD-09 §9.3) — operator-tunable `CollectorConfig` buffer caps (currently unbounded).

**Verification.** Hash-component rebase proven (procedural-tier snapshot includes prompt version); buffer-bound e2e under a pathological producer; ADR cleared + clearance markers.

### Phase P5 — CXA phase-2 edges + cost-model + validator depth

**Goal.** Close the remaining cross-axis + cost + validator surfaces.

**Work.**
- **Ground the 22 CXA phase-2-runtime edges** (CXA v2.19 §2.3.x) — verify each (CXA-4 precedent: grounding found them 0-wireable / satisfied by stage-6 convention; do not assume work exists — `[[r-cxa-seam-wiring-is-producer-discovery]]`). Wire genuine producers; record 0-wireable ones honestly.
- **Cost-attribution rate tables** (OD C-OD-17 5-step chain): the chain is built; bind per-provider token-rate / overhead coefficients (Cat-2 deployment-config + a default table).
- **Validator-framework thresholds** (AS / ADR-D2 §1.9): bind which validator runs at which sandbox-tier threshold.

**Verification.** Per genuine edge, an executed producer proof; cost attribution produces non-zero, correct figures on a real dispatch; a validator fires at its tier threshold.

### Phase P6 — Spec-prose ↔ impl hygiene  `[design-phase posture]`

**Goal.** Reconcile the design-substrate prose that drifted from the landed impl, so the spec describes the built reality (the `[[spec-prose-plan-body-drift-pattern]]` class).

**Work.**
- AS spec `C-AS-14 §14.5/§14.6` still say Files / managed-agents are "deferred indefinitely" — but R-810/R-820 **landed** them. Refresh the spec footers (clearance markers).
- Cross-spec drift sweep: `rg` siblings for stale cite-shapes + `just overlay-check` for code↔cite / cross-axis-seam decay (§13.1).
- Confirm every Cat-4 impl-discretion footer is satisfied-or-bound and recorded.

**Verification.** `overlay-check` clean (no stale tracked snapshots, no HARD seam-missing-endpoint); cross-spec `rg` clean; clearance markers filed for each design-substrate touch.

---

## §3. Cross-cutting hardening phases (open only after P1–P6 capabilities are stable)

### Phase Q1 — DevEx + whole-codebase code-review & simplification sweep

**Goal.** Clean, simplified, clearly-commented code across the whole harness + a developer experience that's pleasant to build on.

**Work.**
- **Whole-codebase review** — correctness + reuse + simplification + comment-clarity. Per-package sweep via `just codex-review` (out-of-family) + `/code-review` (high/max effort) + `/simplify` + `harness-adversarial-reviewer`. *(This is a legitimate `Workflow` candidate — broad parallelizable audit — if the operator opts in; otherwise per-package sequential.)*
- Resolve every finding: dead code, over-abstraction (the §3.2 framework-pull discipline at code scale), unclear comments, naming drift, duplicated logic.
- **DevEx**: the developer-facing surfaces — `justfile` recipes, `harness.toml` ergonomics, CLI/`api.run` UX, error messages (typed + actionable), onboarding friction, the overlay/dashboard tooling. A new contributor can get to green from a clean checkout.

**Verification.** `just check` green (lint + typecheck-strict + full test) at a verified fixed point (`/self-heal`); a recorded review pass per package with all findings closed; a clean-checkout-to-green DevEx walkthrough.

### Phase Q2 — Security testing + review

**Goal.** The harness is secure across its threat surfaces; findings fixed.

**Work (threat-model the harness, then test + review each surface).**
- **Sandbox blast-radius** (4-tier): verify isolation is real and monotonic — FS/network egress containment at TIER_2/3/4, no host-path leakage, no tier-downgrade escape (pen-style probes against Docker/gVisor/E2B drivers).
- **Secrets**: keyring / env / GCP-SM / in-sandbox-encrypted-fs backends — no leakage to logs/spans/ledger; fail-closed on `SECRET_UNKNOWN`; rotation-metadata integrity.
- **MCP trust framework**: per-server trust tiers; no untrusted-server privilege; the X-AL-1 process-isolation boundary holds.
- **Redaction / tokenization** (OD §13): default-off content stripped before export; opaque-token map integrity; multi-tenant separation.
- **Audit integrity**: hash-chain tamper-evidence (C-IS-06); audit-ledger completeness on the 8-prefix action_id surface.
- **Supply chain**: dependency audit (pinned, known-good, no abandoned/unmaintained framework pulls — composes with I-6); `uv` lockfile integrity.
- Run `/security-review` on the diff surfaces + a dedicated security pass on the above.

**Verification.** A threat-model doc + a per-surface test result + every finding fixed-or-risk-accepted-with-rationale. No secret/PII in any telemetry/ledger artifact (proven by probe).

### Phase Q3 — QA + 100%-evidence closure

**Goal.** The full suite is green and every spec contract has executed-path evidence (not unit-only).

**Work.**
- `/self-heal` the full suite to a **verified green fixed point** (clear caches first per §14.3; distinguish env-artifact reds — e.g. the known macOS `AF_UNIX`/dotenv-secret artifacts — from genuine defects, `[[just-check-provider-secret-env-artifact]]`).
- **Coverage/evidence audit**: every `C-*` contract → ≥1 *executed-path* proof (e2e/use-the-product), not grep/unit-only. Fill gaps. *(Workflow candidate for the broad audit if opted-in.)*
- **Use-the-product probes** across all 3 deployment tiers (re-run the RC-style smokes against the now-fuller harness).
- **Flaky-test elimination** (e.g. the known `flush_to_sqlite` timing flake).

**Verification.** Full suite green + a coverage/evidence matrix showing executed-path proof per contract + tri-tier product probes pass.

### Phase Q4 — Portable packaging + deployment

**Goal.** The harness is packaged for portable, reproducible deployment per tier.

**Work.**
- **Build artifacts**: `uv build` wheels for the workspace packages; a reproducible, pinned install path; version stamping.
- **Container/deploy images** per tier: the SELF_HOSTED daemon image + compose stack (extend `deploy/self-hosted-local/`); the MANAGED_CLOUD image(s); the sandbox-tier runner images.
- **One-command bring-up per tier** (local-dev / self-hosted / managed-cloud) with a readiness check (extend the RC `just r4xx-*-readiness` recipes into a packaged installer).
- Reproducibility proof: clean-environment install → run → readiness-green.

**Verification.** A fresh environment installs from the published artifact and reaches readiness-green on each tier; image build is reproducible.

---

## §4. Documentation phase (open after features + packaging stable)

### Phase D1 — Documentation suite

**Goal.** Clear, accurate, byte-grounded docs covering every audience.

**Work (use `/document-generate` + `/document-release`; every claim verified against HEAD — no fabricated cites, §10.4).**
- **Feature / functionality docs** — what the harness does, per axis + cross-axis: routing, workflow/topology, HITL, sandbox tiers, memory/files, observability, cost, recovery.
- **Dependency docs** — the committed stack + why (Target_Stack_Commitment), the per-provider SDKs, the framework-pull discipline (what's deliberately *not* used and why), the dependency graph.
- **User / operator docs** — install, configure (`harness.toml` reference), run (`api.run` / CLI), the 3 deployment tiers, secrets setup, troubleshooting, the 4-response HITL palette.
- **Deployment / runbook docs** — per-tier bring-up, the readiness gates, upgrade/rollback, the daemon.
- **Architecture / API docs** — the 4-axis + CXA model, the contract reference (`C-*`), the public API surface, the substitution/retirement story (how H_E scaffolding was displaced), the design-authority chain.
- **High-value extras** — a "concepts" map, the overlay/dashboard usage, a contributor guide.

**Verification.** Every doc reviewed for accuracy against HEAD (cite-grounding); a docs-completeness check (every public surface + every audience covered); operator readthrough.

---

## §5. Closure phase (final)

### Phase C1 — Full-spec closure certification

**Goal.** Certify and ship full closure.

**Work.**
- **Full-spec coverage audit** — every `C-*` contract + CXA seam + ADR commitment: built ∧ activated ∧ tested ∧ reviewed ∧ documented. *(Workflow candidate — exhaustive parallel audit — if opted-in.)*
- **Final adversarial + council review** of the whole closure (not per-phase) — the completeness critic: "what's missing — a surface not built, a claim unverified, a doc not written?"
- **Apply the phase-9 promotion model** (`phase-9-retirement-criteria.md`) to any remaining bounded-residuals: promote to substantive-retired where evidence now supports it, or record with an explicit re-open trigger.
- **Roadmap/dashboard**: mark full closure; close the R-NNN closure track.
- **Ship** (`/ship` / `/land-and-deploy`): final packaged release + docs published.

**Verification.** A signed closure-certification doc (coverage matrix 100%, all gates green) + final decorrelated + adversarial sign-off + the shipped release.

---

## §6. Per-phase template (every P/Q/D/C phase runs this)

| Step | What |
|---|---|
| **Entry** | Re-ground the phase's surfaces against HEAD (§1); confirm dependencies satisfied; declare posture; open R-NNN. |
| **Design** | If a `⚖️` tension is named → dyadic council. If a surface is unspecified → fork-before-build. Else → solo + `advisor()` at the fork. |
| **Build** | Tests-first where tractable; simplest-thing-that-works; clean + commented as you go. |
| **Verify** | 100% evidence *by execution* (e2e/use-the-product); the touched contracts each gain an executed-path proof. |
| **Review** | `just codex-review` (every diff) + `advisor()` (pre-done) + `harness-adversarial-reviewer` (pre-merge); drive findings to convergence. |
| **Merge** | PR-per-phase (or per-cluster); clearance marker if design-substrate touched; X-AL-3 guard green. |
| **Refresh** | §12 post-merge audit → dashboard terminating-refresh; memory hygiene; update this plan's phase status. |
| **Exit** | Phase exit-criteria met + recorded; next phase's dependencies now satisfied. |

---

## §7. Dependency graph + sequencing

```
P0 (ground + scope-lock + file design forks)
 ├─ P1 routing intelligence ───────────────┐
 ├─ P2 engine-recovery activation ─────────┤
 ├─ P3 persona-tier breadth ───────────────┤  (P1..P3 parallelizable; independent surfaces)
 ├─ P4 spec-completion deferrals ──────────┤  (P4 depends on P0 forks ratified)
 ├─ P5 CXA phase-2 + cost + validator ─────┤
 └─ P6 spec-prose↔impl hygiene ────────────┘
            │ (all capabilities stable)
            ▼
 Q1 DevEx + code-review/simplification sweep
 Q2 security testing + review
 Q3 QA + 100%-evidence closure        (Q1..Q3 largely parallel; Q3 wants Q1/Q2 fixes folded in)
            │
            ▼
 Q4 portable packaging + deployment   (needs stable, reviewed code)
            │
            ▼
 D1 documentation suite               (needs stable features + packaging)
            │
            ▼
 C1 full-spec closure certification + ship
```

**Sequencing rationale.** Capabilities first (you can't QA/secure/document a moving target); the capability phases are mostly independent (parallelizable per the operator's appetite); quality is continuous (per-phase gates) *and* consolidated (Q-phases); packaging needs reviewed code; docs need stable features + packaging; closure certifies the whole. **P4 is gated on P0's forks being ratified** (design-before-build).

---

## §8. Tracking integration

- **Roadmap.** Each phase seeds an R-NNN entry (e.g. `R-P1-routing-intelligence` … `R-C1-closure-cert`) at `Project_Roadmap_v1.md` §5 / §5.1; the dashboard tracks them; this plan is the spine the `next_action` derivation points into during the closure arc.
- **This plan.** Phase status updated at each phase exit (per §6); `v1 → v2` if the operator revises the §0.3 structural decisions or the scope-lock materially changes the surface set.
- **Memory.** Patterns at cardinality ≥2 saved; the closure arc's recurring lessons captured.
- **Phase-9 model.** `phase-9-retirement-criteria.md` is the decision model applied at C1 for bounded-residual promotion.

---

## §9. Out of scope (deliberately not done)

- **Vendoring external frameworks** (Temporal / K8s / Kafka / LangGraph / Prefect / LiteLLM / …) — I-6 framework-pull discipline. Cat-2 builds the *seam + reference adapter*; the real engine binds at deployment.
- **Live-proving deployment-gated items without operator infra** — D-2: build-seam-defer-live-proof; live-proof is an operator-gated sub-step.
- **Re-litigating cleared decisions** — ADR/spec/plan decisions are P3-CK/P5-CK/P6-CK cleared; revision requires explicit back-flow (§4.3), not in-flight absorption.
- **Silent design extension** — any new H_T primitive surfaced mid-build routes to a Class-1 fork first (X-AL-3).
- **The eval-harness as a governance gate** — `[[eval-harness-refused-as-governance-gate]]` (R1/R2): no automated model-judge as THE acceptance gate; human review + the disciplines above are the gate.

---

*End of Post-MVP Full Harness Closure Plan v1. Structural decisions at §0.3 are revisable. This plan is process-substrate (mode-agnostic); it plans design-substrate + Phase-7 work but edits neither here. Authority: operator directive 2026-06-10.*
