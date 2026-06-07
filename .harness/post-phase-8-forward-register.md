# Post-Phase-8 Forward Work Register

> **Status: Claude-authored register for operator planning.** Comprehensive enumeration of the integrations, implementations, and operator-led actions that remain **after** Phase-8 substitution-closure — each grounded in the design-substrate, with current production state and concrete close-out steps. **Posture: mode-agnostic** (process-substrate; reads `design-substrate/` + `harness-*/src/` + `.harness/`; authors only this `.harness/` file). Sibling to `.harness/R-700-phase-8-closure-accounting-draft.md` (the substitution accounting this register builds forward from). Compiled at HEAD `01cd0fa`, 2026-06-01.

---

## 0. Thesis — what "post-Phase-8" means for this harness

**Phase 8 closes the *substitution accounting*, not the *capability activation*.** Per the roadmap §1 + X-AL-2 (Meta-Architecture §7.7), a substitution RETIRES when (A) its cited units land **and** (B) the H_E scaffold surface is no longer invoked at the substitution site. **X-AL-2 never required the underlying capability to be exercised in production** — only that the hand-built H_T substrate displaced the Claude-Code scaffold. So the 88.9% RETIRED headline is **legitimate and not undercut by this register.**

What remains is a **different axis of work**: *activation, deployment, scale, and external integration* of capabilities that are, in many cases, **library-complete / structurally present but not yet exercised at runtime** (multi-LLM routing, real sandbox isolation, non-LOCAL deployment surfaces, multi-tenant redaction, MANAGED_CLOUD secrets, external MCP/Files/managed_agents integrations). This is **not "fixing incomplete retirements"** — it is building the production frontier the MVP deliberately stopped short of.

The register has **two tiers**, kept distinct:

- **Tier A — Phase-8 closure residuals.** Operator-owned actions needed to *declare Phase 8 done* (bounded-residual sign-offs, the R-700 review, the no-`R-NNN`-entry gap, the config-discovery fork). These are *closure* items, not forward activation.
- **Tier B — Post-Phase-8 forward activation.** The genuinely-forward surfaces (Multi-LLM IV / Multi-deployment V / Multi-tenant VI / External-integrations IX / Research X / Operator-tooling XI) + the CXA composition seams.

**This register also discharges a roadmap obligation.** Roadmap §1 marks Surfaces IV / VI / VIII–X as `decomposition-owed` (§9). This document **is** that decomposition for IV / VI / IX / X — its items can seed `R-300` / `R-500` / `R-800` / `R-900` entries, which also closes the **no-`R-NNN`-entry gap** R-700 surfaced for `CXA-1/2/3/4` + `CP-17`.

**Council note (answering the standing question).** Compiling *this register* is descriptive synthesis grounded in substrate — **not** a design decision with a nameable cross-domain tension, so per CLAUDE.md §13.2 + §10.9 it routes to solo + `advisor()`, not the council. But several **forward arcs below carry nameable two-voice tensions that ARE council-eligible the moment the operator opens them to execute** — each is flagged `⚖️ council-eligible` with the named voices. (The roadmap already encodes this on R-410/411/412 via `council_required: conditional:nameable-tension`.)

---

## 1. Front summary table

### Tier A — Phase-8 closure residuals (declare Phase 8 done)

*Status legend: ~~strike~~ = definitively closed · **[open]** = actionable now · **[blocked]** / **[deferred]** / **[proposed]** = not-closed-not-open (word = why). Mirrors the live dashboard's R-NNN board + Post-Phase-8 register sections.*

| # | Status | Item | Owner action | Spec/source | Council? |
|---|---|---|---|---|---|
| A-1 | **[blocked]** | R-700 Phase-8 substitution review + final integer ratification | Review the R-700 draft; ratify 46–47-vs-48 + bounded-residual sign-offs | `R-700-phase-8-substitution-accounting` (BLOCKED) | no (AUQ) |
| A-2 | **[open]** | Bounded-residual sign-offs (AS-8e, AS-8f, OD-6) | Operator signs the 3 deferred-by-design closes | X-AL-2 §5.3; Surface VIII | no (AUQ) |
| A-3 | **[open]** | `R-NNN` coverage for the 5 invisible open rows (CXA-1/2/3/4 + CP-17) | Authorize an R-002-style Surface-I pass | R-700 draft §C item 2 | no |
| A-4 | ~~closed~~ | ~~`harness.toml` auto-discovery fork ratification~~ | Reading A ratified 2026-06-06; implementation had already shipped at PR #279 | `R-100-mvp-config-discovery` RESOLVED | no |

### Tier B — Post-Phase-8 forward activation

| # | Status | Surface | Item | Current state | Close-out class | Council? |
|---|---|---|---|---|---|---|
| B-1 | ~~closed~~ | IV Multi-LLM | ~~Layered capability-aware routing activation~~ | **routing activation RESOLVED (R-300-multi-llm-routing-activation, PR #213)** — declarative layer live; the multi-provider *exercise* is B-2 | impl + operator creds | ⚖️ yes |
| B-2 | ~~closed~~ | IV Multi-LLM | ~~Multi-provider credentials + mixed-provider exercise~~ | **R-300 second-provider exercise RESOLVED** — deterministic fallback + live Anthropic→OpenAI (#281) + live Ollama (#283) | PR #281 + PR #283 | no |
| B-3 | ~~closed~~ | V Deployment | ~~Real TIER_2 container sandbox execution (R-410)~~ | **R-410 RESOLVED by local Docker execution driver + live TIER_2 container e2e** | this PR | ⚖️ yes |
| B-4 | **[proposed]** | V Deployment | TIER_3 microVM + TIER_4 full-VM execution (R-411/R-412) | host-fit gate explicit; current macOS x86_64 host is ineligible for the reviewed R-411 runtimes | impl + infra | ⚖️ yes |
| B-5 | ~~R-420 closed~~ / **[proposed] R-421** | V Deployment | SELF_HOSTED_SERVER + MANAGED_CLOUD e2e (R-420/R-421) | **R-420 RESOLVED by local single-node self-hosted daemon + collector + keyring live e2e; R-421 static readiness/live E2B probe surface built, still cloud-secret-backend/operator-infra gated** | this PR + future cloud | ⚖️ (R-421) |
| B-6 | **[proposed]** | V Deployment | OTLP tail-keep collector-side validation (R-430) | buffer logic in-process; collector-side validation can now use the R-420 local collector stack | impl + local infra | no |
| B-7 | ~~closed~~ | V Deployment | ~~Tier-level self-hosted secrets backend selector (R-440)~~ | **SELF_HOSTED keyring-only selector landed; cloud bootstrap-token remains R-421** | this PR | no |
| B-8 | **[proposed]** | VI Multi-tenant | Non-default `tenant_id` / non-SOLO `persona_tier` deployment | fields plumbed; non-toggleability enforced; base-rate envelope live | operator deploy + impl | ⚖️ yes |
| B-9 | **[blocked]** | VI Multi-tenant | OD-4: per-session redaction toggle (§13.1) + opaque-token tokenization (§13.2) | strip-not-tokenize MVP; toggle deferred — needs session-control substrate (R-008) | impl (R-008) | ⚖️ yes |
| B-10 | ~~closed~~ | IX External | ~~Real external MCP server connection~~ | **✅ R-800 RESOLVED (2026-06-01)** — `start()`/`shutdown()` wired at PR #172 (spec v1.41 §14.9.8 Gaps B/F); real external stdio e2e green & unconditional at `test_u_rt_86`. Full `api.run` path = Gap D (R-100 AC#2, operator-gated) | impl | no |
| B-11 | **[deferred]** | IX External | Files API integration (AS-8e / CP-17) | STILL-BOUNDED-INDEFINITELY by design (managed-cloud arc) | design-phase + impl | no |
| B-12 | **[deferred]** | IX External | managed_agents integration (AS-8f) | STILL-BOUNDED-INDEFINITELY by design (managed-cloud arc) | design-phase + impl | no |
| B-13 | **[proposed]** | IX External | Memory-tool production backend (CP-16) | SELF_HOSTED SQLite slice landed (PR #224); cloud-vault/managed-DB remainder deferred (creds) | impl | no |
| B-14 | **[partial]** | CXA | Cross-axis seam completion (CXA-1/2/3/4) | CXA-1 PARTIAL (no producer), CXA-2 STILL-BOUNDED (engine substrate), CXA-3 STILL-BOUNDED (no composer), CXA-4 PARTIAL (0-wireable, bookkeeping) — **placeholders resolved at v2.3/v2.11; v2.18 matrix defect fixed at v2.19/PR #226** | impl (mechanical) | no |
| B-15 | **[proposed]** | XI Tooling | Dashboard iteration-2 (R-XI-02/R-XI-03) | MVP live; iteration-2 nice-to-have | impl | no |
| B-16 | **[proposed]** | X Research | Open architectural / speculative arcs | not decomposed | research | no |
| B-17 | **[proposed]** | XII Methodology *(NEW)* | ICM workspace-methodology adoption | **audit landed** (`ca2bc34`, `ICM_Alignment_Audit_v1.md`): ~90% ICM-values / ~50% ICM-structure (15.5/23); root `CLAUDE.md` ~107x ICM L0 budget; no adoption decided | design (spec/plan) — reconciliation, not conversion | ⚖️ conditional |

---

# TIER A — Phase-8 closure residuals

## A-1 · R-700 Phase-8 substitution review + final-integer ratification
- **What it is.** The operator-owned Phase-8 review (`R-700-phase-8-substitution-accounting`, BLOCKED) that consumes the R-700 draft and declares all 54 substitutions RETIRED or RETIRED-AS-BOUNDED-RESIDUAL with rationale (Surface VIII closure criterion, roadmap §1).
- **Current state.** The Claude-executable draft is landed (PR #207). It found the published `48/54` over-counts by 1–2 (per-row truth `46–47`); pipeline-advanced `49/54` is solid.
- **Close-out steps.** (1) Read `.harness/R-700-phase-8-closure-accounting-draft.md`; (2) ratify the substantive-RETIRED integer (46 / 47 / keep 48 with carve-out — §C item 1); (3) sign the bounded-residual closes (A-2); (4) mark `R-700-phase-8-substitution-accounting` RESOLVED. **Council: no** — this is a ratification (advisor + AskUserQuestion), not a multi-voice design tension.

## A-2 · Bounded-residual sign-offs (AS-8e, AS-8f, OD-6)
- **What it is.** Three substitutions closed as deferred-by-design / dormant-at-MVP that need an explicit operator Phase-8 sign-off per X-AL-2 §5.3: **AS-8e** (`files.*` namespace, Files-arc Memory-only MVP scope, runtime spec v1.17 §14.C); **AS-8f** (`managed_agents.*`, production-only exclusion, `class_1_fork_as_8f_...` Q1=C); **OD-6** (local-first OTLP sqlite ingestion — `flush_to_sqlite` dormant at MVP, FIRST bounded-residual close in the ledger, batch-51).
- **Close-out steps.** Operator confirms each bounded-residual disposition is the intended Phase-8 end-state (vs. requiring substantive close before Phase-8 graduation). **Council: no** (sign-off).

## A-3 · `R-NNN` coverage for the 5 invisible open rows
- **What it is.** R-700 surfaced that `CXA-1/2/3/4` + `CP-17` have **no roadmap `R-NNN` entries** — the R-002 Surface-I decomposition surveyed only the per-axis `§4.1`, which excludes the CXA axis (no `§4.1` file) and didn't frame CP-17's batch-44 SB-INDEF reclassification as open.
- **Close-out steps.** Authorize an `R-002`-style decomposition pass over CXA + CP-17 → seed `R-NNN` entries (these map to B-14 forward work). **Note:** this register's B-14 + §0 already supplies the substance; the action is to formalize them as roadmap entries. **Council: no.**

## A-4 · `harness.toml` auto-discovery fork ratification
- **Status.** CLOSED. The operator ratified Reading **(A)** CWD discovery on 2026-06-06; empirical grounding found PR #279 (`a394032`) had already implemented that reading.
- **Closure.** `RuntimeConfigSource.load(config_file=None)` now discovers CWD-local `harness.toml`, preserves env+CLI-only behavior when absent, and lets explicit `--config` take precedence over discovery. `R-100-mvp-config-discovery` is RESOLVED; no spec amendment is owed. **Council: no** (AskUserQuestion was the only gate).

---

# TIER B — Post-Phase-8 forward activation

## Surface IV — Multi-LLM maturity (R-300..R-399, decomposition-owed)

> **The commitment (ADR-F1 v1.2 + `Target_Stack_Commitment_v1` §5.1–5.2).** Per-provider official SDKs (`anthropic` + `openai` + `ollama`) under a **capability-aware abstraction** — NOT LiteLLM — with a layered cheapest-deterministic-first routing strategy (declarative manifest → embedding classifier → LLM-as-router) and feature-preservation (Anthropic prompt-caching / extended-thinking / batch / MCP host must remain reachable, no LCD flattening). Spec surface at CP spec `C-CP-01..C-CP-04`. These correspond to substitution rows `H_T-CP-1..CP-5` (all RETIRED-as-substitution — legitimately; the library displaced the scaffold).

### B-1 · Layered capability-aware routing activation `⚖️ council-eligible`
- **Current state (empirically verified this session).** Provider construction is **live** — all 3 adapters (`AnthropicAdapter` / `OpenAIAdapter` / `OllamaAdapter`) built at bootstrap stage-3a (`providers.py`). The retry/breaker/**fallback-chain dispatch** (`C-RT-16`, `lifecycle/retry_breaker_fallback.py`) **is wired** at the stage-5 `StepDispatcher` and iterates fallback candidates (primary → same-family → cross-family → terminal) with `advance_or_raise` on per-candidate exhaustion. **But the layered routing-*selection* path is a stub:** `routing_core_surface.infer()` raises `NotImplementedError` (`routing_core_surface.py:83`/`:97`), and `layered_routing_strategy.route()` has **zero non-test callers** (verified). So *which provider to use* is taken statically from the manifest `model_binding`, not from capability-aware layered routing.
- **What this means for the harness.** Provider plumbing + failure-time fallback exist; **capability-aware provider *selection* is not active.** Combined with B-2, the multi-provider machinery is present but **unexercised at MVP**.
- **Close-out steps.** (1) Implement the `infer()` composition seam to invoke `layered_routing_strategy.route()` (declarative-layer first) before provider dispatch (CP spec C-CP-02); (2) bind per-layer time-budgets (C-CP-03 `LayerBudget`); (3) implement capability-shortfall fallback (C-CP-04 + ADR-F1 §Consequences(c)) — fall to a capable provider *before* the step fails when the primary lacks a required capability (e.g. extended-thinking).
- **`⚖️ Council (C5 ⊥ C9 ⊥ capability-preservation).`** Designing the routing-selection policy is a genuine tension: **cost** (cheapest-deterministic-first) vs **reliability/recovery** (when to fall back / breaker thresholds) vs **capability-preservation** (don't route a thinking-required step to a non-thinking model to save cost). Convene a dyad (cost-voice + reliability-voice) when this arc opens.

### B-2 · Multi-provider credentials + mixed-provider exercise
- **Status.** CLOSED 2026-06-03. The R-100 gap was closed by PR #281 (`2dc25e6`) and PR #283 (`e436252`).
- **Closure.** PR #281 added the deterministic production-path cross-family fallback fixture and the live Anthropic invalid-model → OpenAI `gpt-4o-mini` exercise (`just mvp-r300-cross-family`, live PASS 4.55s). PR #283 added the free local Ollama fallback exercise (invalid model → `llama3.2:3b`, live PASS 4.17s through `api.run`). Deterministic CI coverage remains for non-credentialed runs; the live provider halves are recorded in `.harness/roadmap_status.md`. **Council: no**.

---

## Surface V — Multi-deployment surfaces (R-400..R-499)

> Per ADR-D2 (per-deployment-surface sandbox provider) + ADR-F4 (4-tier blast-radius) + ADR-F5 (tier-aware secrets) + `C-AS-15 §15` + `C-RT-29 §14.18` (daemon). The **12-cell `deployment_matrix.py`** maps `(DeploymentSurface, BlastRadiusTier) → (SandboxTier, SandboxProviderClass)`: LOCAL/SELF_HOSTED use process/container/microVM/full-VM provider classes with **LOCAL keyring** secrets; **MANAGED_CLOUD** reserves FULL_VM at TIER_4 and **defers** its secrets backend to prod-tech. `multi-tenant-compliance × local-development` is a **closed cell** (raises `CellBindingViolation`). **R-410 now makes the first tier executable via a local Docker `ToolExecutionDriver`; higher tiers and deployment surfaces remain the honest frontier.**

### B-3 · Real TIER_2_CONTAINER sandbox execution (R-410) `⚖️ council-eligible`
- **What it is.** Make a tool call resolved to `TIER_2_CONTAINER` actually execute inside a container boundary (verifiable FS/network isolation), not in-process. **The honest heart of Surface V.**
- **Current state.** RESOLVED by this PR: `RuntimeToolDispatcher` now delegates execution through a `ToolExecutionDriver`, the default driver preserves prior MCP-host behavior, and `DockerToolRunnerExecutionDriver` runs TIER_2 calls inside a local-only Docker container by resolved immutable image id.
- **Close-out evidence.** The live e2e drives a TOOL_STEP resolved to `TIER_2_CONTAINER` through Docker, asserts outbound network is blocked, and asserts the host worktree path is not visible. Existing dispatcher tests cover under-tier rejection and sandbox.enter/exit provider/tech attribution. No provider credentials or paid calls required.
- **`⚖️ Council (C10 ⊥ C11) — roadmap already flags `conditional:nameable-tension`.`** Action-safety/blast-radius (C10) wants real isolation; operator-loop/local-deployment (C11) wants minimal provisioning burden. This slice resolves the tension narrowly with a local-only Docker driver that preserves the default in-process path unless explicitly injected.

### B-4 · TIER_3 microVM + TIER_4 full-VM execution (R-411 / R-412) `⚖️ council-eligible`
- **What it is.** Extend executable isolation up the ladder: TIER_3 (gVisor/Kata, EXTERNAL_REVERSIBLE) then TIER_4 (firecracker/full-VM, EXTERNAL_IRREVERSIBLE, **MANAGED_CLOUD-only** per the matrix).
- **Current state.** Not built; B-3 settled the execution-driver pattern. R-411 should target `google/gvisor` (`runsc`), `kata-containers/kata-containers` (`kata-runtime`), `superhq-ai/shuru`, `superradcompany/microsandbox`, or `containers/libkrun` based on host fit. Firecracker and QEMU `microvm` are tracked as R-412 FULL_VM lanes, not R-411 lanes. `mvm-sh/mvm` was reviewed and excluded because it is a Go bytecode VM/interpreter, not an isolation sandbox for arbitrary TOOL_STEP execution. E2B (`e2b-dev/e2b`) is a managed-cloud candidate for R-421/R-412, not a local R-411 runtime, and requires `E2B_API_KEY`. The repo now has a non-mutating `just sandbox-host-check <provider>` readiness probe. Current operator host grounding rechecked 2026-06-07: macOS x86_64 with no `/dev/kvm`; `r411-gvisor`, `r411-kata`, `r411-shuru`, `r411-microsandbox`, and `r411-libkrun` all fail readiness on this host. Shuru/Microsandbox/libkrun require Apple Silicon on macOS, and Firecracker/Kata/libkrun/QEMU microvm Linux paths require KVM. R-412 is explicitly deferred until a MANAGED_CLOUD/Linux-KVM surface exists.
- **Close-out steps.** Provider-class additions once B-3 lands the pattern; per-tier blast-radius enforcement; e2e per tier. **`⚖️ Council (C10 ⊥ C11)`** inherited from B-3.

### B-5 · SELF_HOSTED_SERVER + MANAGED_CLOUD deployment e2e (R-420 / R-421)
- **What it is.** First real non-LOCAL surfaces. **R-420 (SELF_HOSTED_SERVER):** harness daemon (`C-RT-29 §14.18`, FastMCP Unix-socket) against a **real OTLP collector** + tier-level secrets; tail-keep wrapping active (non-LOCAL); per-cell sampler `base_rate` = the SELF_HOSTED cell. **R-421 (MANAGED_CLOUD):** cloud env + cloud secrets + FULL_VM + managed collector; in-sandbox encrypted-fs secrets per ADR-F5; MANAGED_CLOUD per-cell sampler + redaction posture (`C-OD-13 §13.1`).
- **Current state.** R-420 is **RESOLVED** by the local single-node SELF_HOSTED_SERVER stack at `deploy/self-hosted-local/`: host-run harness daemon + Docker Compose OTel Collector Contrib, Tempo, and Grafana; `harness.selfhosted.local.example.toml` selects `SELF_HOSTED_BACKEND_COLLECTOR` and `self-hosted-keyring`; `just r420-self-hosted-stack-*` controls the backend. Closure evidence 2026-06-07: Docker stack running, `just r420-self-hosted-readiness harness.selfhosted.local.toml` passed, and `just r420-self-hosted-live-e2e harness.selfhosted.local.toml` passed with workflow `r420-self-hosted-tool-echo`, daemon status `success`, cost `0`, hosted-provider-calls `0`. The live workflow uses local Ollama plus non-secret keyring sentinel `r420_probe_key`; no hosted-provider inference is performed. R-421 remains MANAGED_CLOUD/operator-gated, but the static resume surface is now built: `just r421-managed-cloud-readiness <config> --hosted-sandbox-provider e2b`, `deploy/managed-cloud/harness.managed-cloud.e2b.example.toml`, `ProviderSecretBackend.GCP_SECRET_MANAGER`, and the explicitly approved-only `just r421-e2b-live-probe`.
- **Close-out steps.** (R-420) none remaining. (R-421, dep R-420) provision GCP credentials, the `google-cloud-secret-manager` SDK, the named Secret Manager entries, and a managed non-loopback OTLP collector endpoint; then run the approved live e2e / usage-billed E2B probe if E2B remains the hosted sandbox candidate. R-420 **unblocks R-430** and removes the self-hosted prerequisite for R-421. **`⚖️ Council (R-421 only)`** — MANAGED_CLOUD posture (C8 security ⊥ C11 deployment simplicity) when that arc opens; R-420 is closed.

### B-6 · OTLP tail-keep preservation validation (R-430)
- **What it is.** Verify the `§10.2` classification-trigger preservation semantic against a **real** OTLP collector (the drop/keep decision is collector-side).
- **Status.** CLOSED by this PR. `TailKeepSpanProcessor` buffer logic remains in-process + bypassed at LOCAL by design (§9.1 head-based mandate), but the preservation semantic is now exercised against the R-420 local real-collector substrate.
- **Closure evidence.** `just r430-tail-keep-live-e2e harness.selfhosted.local.toml` passed against the local OTel Collector/Tempo stack: trigger trace `4972258a693b5d34c32c89ecd30749bc` exposed `r430.trigger.root` + `sandbox.violation` in Tempo, plain trace `364f9516e5f95cae58f4b44219981626` stayed absent through the negative window, and the command reported `trigger-trace-preserved=true`, `non-trigger-trace-exported=false`, `cost=0`, `hosted-provider-calls=0`.
- **Residual.** None for R-430. Managed-cloud collector posture remains R-421 scope; multi-tenant/non-SOLO telemetry posture remains R-500 scope.

### B-7 · Tier-level self-hosted secrets backend selector (R-440)
- **Status.** CLOSED by this PR. `ProviderSecretsConfig` now carries a `ProviderSecretBackend` selector. The default LOCAL path remains keyring + env fallback; `self-hosted-keyring` resolves through keyring only and disables ambient env fallback.
- **Closure evidence.** Focused tests prove `self-hosted-keyring` raises `SECRET_UNKNOWN` when only `ANTHROPIC_API_KEY` is set, resolves when the keyring entry exists, preserves LOCAL env fallback, and makes `just self-hosted-readiness` pass its static R-440 gate from TOML config.
- **Residual.** Live server/collector/keyring-entry exercise remains R-420. MANAGED_CLOUD bootstrap-token / in-sandbox HTTP fetch remains R-421 managed-cloud scope.

---

## Surface VI — Multi-tenant (R-500..R-599, decomposition-owed)

> Per `C-OD-13 §13.1` (redaction toggleability gradient) + `C-OD-10 §10.3` (per-`(persona_tier, deployment_surface)` sampler base-rate, 8-row table) + ADR-D5/D6. Three persona tiers (SOLO_DEVELOPER / TEAM_BINDING / MULTI_TENANT_COMPLIANCE) × three surfaces.

### B-8 · Non-default `tenant_id` / non-SOLO `persona_tier` deployment `⚖️ council-eligible`
- **Closure.** R-500 closes the self-hosted multi-tenant exercise on the R-420 local collector stack. `RuntimeConfig.tenant_id` now materializes as authoritative OTel `tenant.id` resource attr; `just r500-multitenant-live-e2e harness.selfhosted.local.toml` overlays two non-default tenants with `multi-tenant-compliance`, verifies `base_rate=0.2`, proves non-toggleable redaction strips default-off content before Tempo while preserving structure attributes, and exercises tenant-scoped audit-ledger reads. Closure evidence 2026-06-07: tenant A trace `5c0e5916bf84933296323f2038c6680b`, tenant B trace `a847370bbc76adc41b85e3328d3279aa`, `tenant-resource-separated=true`, `content-redacted=true`, `audit-ledger-separated=true`, `cost=0`, `hosted-provider-calls=0`.
- **`⚖️ Council (C7 + C8 ⊥ C11).`** Observability/privacy (C7) + security/compliance (C8) vs operator-burden (C11): how much redaction/audit ceremony is mandatory at TEAM vs MULTI_TENANT. Convene when the multi-tenant arc opens.

### B-9 · OD-4: per-session redaction toggle (§13.1) + opaque-token tokenization (§13.2) `⚖️ council-eligible`
- **What it is.** The **one genuinely-open MVP-surface substitution** (`H_T-OD-4` PARTIAL, roadmap `R-008`). Two deferred gates: (a) §13.1 per-session redaction toggle (solo-developer operator-runtime control to opt into raw capture, auditably) — needs a **session-control substrate**; (b) §13.2 opaque-token tokenization (replace strip-not-tokenize MVP with `[REDACTED:PII]`-style placeholders + audit-ledger-only token→value mapping) — an **eval-grade pipeline**.
- **Current state.** Strip-not-tokenize MVP holds; the toggle + tokenizer are deferred (advisor 29th application scope-lock).
- **Close-out steps.** (1) Author the session-control substrate + wire a runtime override flag through `RedactionSpanProcessor`; (2) build the tokenizer component + multi-tenant audit-ledger token mapping; (3) advance OD-4 PARTIAL → RETIRE-READY.
- **`⚖️ Council (C7 ⊥ eval-utility/C11).`** Privacy-default-off (C7) vs eval-grade content-shape-reconstruction utility: tokenize vs strip is a real two-voice call. Convene when R-008 opens.

---

## Surface IX — External integrations (R-800..R-899, decomposition-owed)

### B-10 · Real external MCP server connection
- **What it is.** Connect the FastMCP client host to a **real external MCP server** for operator `api.run` TOOL_STEP execution (the TOOL_STEP path the R-100 use-the-product probe exercised).
- **✅ RESOLVED 2026-06-01 (R-800).** This "Current state" framing was **stale** — it was authored at PR #209 but describes pre-PR-#172 state. Verified empirically: the bootstrap **does** call `await ctx.mcp_client_host.start()` (`stage_3a_cp_clients.py:59`) and `host.shutdown()` is wired at teardown (`shutdown.py:484-489`) — both landed at PR #172 (spec v1.41 §14.9.8 Gaps B/F). The converter (spec v1.40, Reading B) + sandbox-decision-resolver (spec v1.41 §14.9.8, Reading B) also landed. A **real external stdio MCP server** is exercised end-to-end at `test_u_rt_86` (production factory `materialize_mcp_client_host_stage` + real subprocess + handshake + list_tools + TOOL_STEP dispatch + 7-attr `mcp.*` span) — **unconditional, no LLM, 9/9 green** (with `test_ac2_bootstrap_path_wiring`).
- **Original close-out steps (all met).** (1) `host.start()` at stage-3a — ✅ `stage_3a_cp_clients.py:59`; (2) `host.shutdown()` at teardown — ✅ `shutdown.py:484-489`; (3) operator `MCPClientConfig.connection_url` + per-server defaults — ✅ surface landed (spec v1.40/v1.41); (4) live e2e against a real external server — ✅ `test_u_rt_86` (real subprocess). **Council: no** (mechanical; confirmed not needed).
- **Residual (out of R-800 scope).** The **full `api.run` bootstrap TOOL_STEP path** (must_pass[3] strict reading) is **Gap D / R-100 AC#2** — the bootstrap pings ≥1 provider regardless of step kind, so the `api.run` echo-MCP e2e (`test_r100_ac2_tool_step_e2e`) is skipif-gated on a live provider (ollama OR `ANTHROPIC_API_KEY`) and is **operator-gated by design** (not fired unilaterally). Making the provider ping conditional on an inference step is a **Class 1 fork candidate** carrying a nameable **C9⊥C11** tension (fail-fast reliability ⊥ tool-only-workflow ergonomics) → **dyadic-council-eligible** per CLAUDE.md §10.9 if the operator opens it.

### B-11 · Files API integration (deferred per AS-8e / CP-17)
- **What it is.** Anthropic Files API (`/v1/files` upload/list/metadata/delete; `file_id` reference in message content) — ADR-D3 primitive #10; the `files.*` observability namespace (AS-8e) + the CP-16/17 Files-primitive consumption.
- **Current state.** **STILL-BOUNDED-INDEFINITELY by design** — runtime spec v1.17 §14.C indefinite-defer (Memory-only MVP scope); AS spec C-AS-13 §13.2 excludes Files at local-development; the namespace schema exists but there is **zero production producer**.
- **Close-out steps.** (1) **Design-phase:** open the Files arc → a runtime plan unit decomposing the Files API consumption contract (parallel to the Memory-tool `C-RT-22` precedent); (2) **impl:** consumer landing at a MANAGED_CLOUD binding (needs live Anthropic Platform); (3) e2e: upload + reference-by-id + Batch-API discount composition. **Council: no** (it's deferred-by-design; the decision was already taken — re-opening is operator-discretion timing, not a live tension).

### B-12 · managed_agents integration (deferred per AS-8f)
- **What it is.** Anthropic managed_agents primitive + the `managed_agents.*` 3-attribute namespace.
- **Current state.** **STILL-BOUNDED-INDEFINITELY by design** — AS-side schema landed (U-AS-31/32), but **zero runtime producer**; AS spec §13.2 excludes managed_agents at local-development; retirement criterion-B (production-surface observation) is unexercisable in-CLI (`class_1_fork_as_8f_...` Q1=C, runtime spec v1.33 §14.D).
- **Close-out steps.** Operator-discretion timing at a future MANAGED_CLOUD arc, gated on Anthropic managed_agents SDK availability + a stable integration contract. **Council: no.**

### B-13 · Memory-tool production backend (CP-16)
- **What it is.** A production storage backend for the Memory tool beyond local-filesystem. ADR-D3 #11 (Memory tool is client-side; harness implements the backend). `C-RT-22` `MemoryToolRegistry` + `MemoryToolStorageBackendProtocol`.
- **Current state.** Registry + **FILESYSTEM backend landed** (`LocalFilesystemMemoryToolBackend`; `CP-16` closed RETIRED-AS-BOUNDED-RESIDUAL batch-44) + **SELF_HOSTED_SERVER `DATABASE` backend landed** (`SqliteMemoryToolBackend`, stdlib sqlite3, R-830 this arc — implements the spec'd `MemoryToolStorageBackend.DATABASE` per §14.12.3 `connection_string`; operator binds via `memory_tool_backend_config`; full read/write/delete e2e, no creds). The **MANAGED_CLOUD cloud-vault / managed-database** backend (`S3` / real managed DB with creds) is **NOT** this — it stays **deferred / operator-gated** (`MANAGED_CLOUD` without an explicit `DATABASE` override still raises). The override point `RuntimeConfig.memory_tool_backend_config` already exists; `S3` / `ENCRYPTED_FILESYSTEM` / `OPERATOR_DEFINED` still raise at the factory.
- **Close-out steps (cloud remainder).** (1) New backend class implementing `MemoryToolStorageBackendProtocol` for a real cloud-vault / managed-db (`S3` / managed DB); (2) operator binds it via `memory_tool_backend_config` with real `connection_string` / creds; (3) e2e read/write/delete against the real cloud backend (operator-gated on creds/infra). **Council: no** (impl). *(The SQLite `DATABASE` slice landed at R-830; this remainder is the cloud production backend the B-13 title names.)*

---

## CXA — Cross-axis composition seam completion (B-14)

> **Status spine = the R-700 dispositions verified + merged this session (PR #207), NOT intermediate fork-doc reads.** CXA edge counts per `Cross_Axis_Composition_Document_v2_18.md` §2.3.x. These are mostly **mechanical wiring** (runtime composer landings + production caller sites), not cross-domain design tensions → **Council: no** for all.

| Seam | Disposition (R-700) | Current state | Close-out |
|---|---|---|---|
| **CXA-1** (AS→IS, 13 edges) | **PARTIAL** | `as_is_wiring.py` composer materialized + 7c-tested; **only the secret-fetch-audit edge (U-AS-27→U-IS-11) wired; zero production callers of `emit_secret_fetch_audit_entry`** (the AS secret-fetch driver path is absent at runtime). | Land the AS secret-fetch driver path so the audit composer has a production caller; thread the remaining ~12 AS source-unit audit-emission callbacks through the `AsIsWiring` surface as AS-axis 7b execution proceeds. |
| **CXA-2** (CP→IS, 36–43 edges) | **STILL-BOUNDED** | `cp_is_wiring.py` PARTIAL-LAND (1 of 17 spec §12.3 edges); the U-RT-35 wiring unit landed (batch-46) but the full typed contract stays STILL-BOUNDED; the 6 §16.5 composer methods (`U-CP-74..79`) + their caller-site invocations (`U-RT-110/111`) are the binding chain. | Complete the runtime caller-site invocations threading the 6 composer methods at their firing sites + e2e; remaining ~16 of 17 §12.3 edges (`class_1_tension_u_rt_35_cp_is_wiring_gaps.md`). |
| **CXA-3** (CP→AS, 24 edges) | **STILL-BOUNDED** | **No `lifecycle/cp_as_wiring.py` module** — consistent with spec §12 (no CP→AS runtime stage); typed edges anchored only at the 7c Pattern-P1 import surface. *(NOTE: this is a real open seam — not "N/A". The substrate-consumption relationship is genuine even though there's no composition stage.)* | Per ledger §11.1b: either **(α)** author a CP→AS runtime composer at a Files-arc design-phase opening, or **(β)** operator AskUserQuestion ratifying a Memory-only-scope narrowing of the CXA-3 retirement criterion (parallel to AS-8e/8f indefinite-defer). Neither is in-session-actionable. |
| **CXA-4** (OD→IS/AS/CP, 26 edges) | **PARTIAL** | **Grounding sweep 2026-06-01 (R-CXA-4 grounding-first) corrects the prior "~5 of 26 / ~21 remaining" framing — a stale-carry mis-framing (CLAUDE.md §10.5).** Per CXA §2.5 the 26 canonical OD-outbound edges split **1 genuine typed seam + 19 convention-level + 6 phase-2-runtime**. (1) The lone genuine **data-flow** edge (U-OD-30→U-IS-11 `audit_writer.append`) is **already wired** with 4 real producers (`cost_attribution_{llm,tool,validator,webhook}_dispatch.py:{246,299,238,198}`). (2) The 6 phase-2-runtime edges are **already materialized** at bootstrap stage 6 (`od_is/as/cp_wiring` per runtime spec §12.4–§12.6; `stage_6_cxa_wiring.py:96/104/108`). (3) The 19 convention edges are namespace/manifest/monotonicity alignment satisfied by the stage-6 `verify_*` checks + manifest-resolver; the per-unit OD→AS/OD→CP rows were **already resolved to real producer unit IDs at CXA v2.3 (2026-05-17) + OD plan v2.11 (2026-05-16, resolution table `.harness/cxa_7c_placeholder_resolution.md`)** — the `U-AS-NN`/`U-CP-NN` placeholders survive only in the superseded v2.1 baseline (the OD aggregate manifest targets only the 4 terminal exporters `U-IS-17`/`U-AS-33`/`U-CP-54`/`U-CP-55`, consistent with convention-level edges that need no per-row manifest carrier). **ZERO unmaterialized edge has a real OD-side producer** — the lone non-wired "genuine" seam U-OD-29→U-AS §12.4 is a halted-leaf symbol-import (FF-3 Class 1 fork), not a data-flow producer. Mirrors the R-CXA-1 producer-discovery outcome (`[[r-cxa-seam-wiring-is-producer-discovery]]`, 3rd instance). | **There is no wiring task AND no cleanup task** — grounding found **0 wireable edges** (1 genuine already wired; 6 phase-2 already at stage 6) AND the placeholders were already resolved at CXA v2.3 + OD plan v2.11. **CORRECTED 2026-06-01:** the prior "CXA convention-formalization revision owed (delete/remap stale placeholders, mirroring v2.18's C3-15)" follow-on was a **phantom** born of reading the v2.1 baseline (CLAUDE.md §10.5 wrong-version-read). The probe of that phantom follow-on instead surfaced + corrected a **real defect in v2.18**: v2.18 re-absorbed the already-done C3-15 OD→IS cleanup (same wrong-version-read), corrupting the §2.1 matrix (AS→IS 13→11, CP→OD 0→8, OD→CP 8→12) and publishing aggregate **105** (correct = **107**) → fixed at **CXA v2.19** (this PR). R-CXA-4 stays PARTIAL; ZERO production code; no further Claude-executable follow-on (full RETIRED gated on R-700 + R-CXA-2 engine-layer substrate). |
| **CXA-5** (OD→CP inversion, 1 edge) | **RETIRED** (batch-3) | Production `harness.breaker.*` emission landed (U-RT-58); inversion seam fires end-to-end. | — (closed). |

---

## Surface XI — Operator tooling (R-XI-NN)

### B-15 · Dashboard iteration-2 (R-XI-02 / R-XI-03)
- **What it is.** **R-XI-02:** dependency-graph viz + sparklines; **R-XI-03:** live-update mode (webhook or short-poll). Both depend on R-XI-01 (the MVP, RESOLVED + LIVE at `thestoryportal.github.io/arhugula-harness/`).
- **Current state.** MVP live (auto-generated from `roadmap_status.md` on merge). Iteration-2 features PROPOSED.
- **Close-out steps.** Extend `tools/dashboard/generate.py` + `roadmap.html` with the dep-graph render (the `depends_on` data is already in the `DATA` blob) and a poll/webhook refresh. **Council: no** (impl).

---

## Surface X — Existential / research (R-900..R-999, decomposition-owed)

### B-16 · Open architectural / speculative arcs
- **What it is.** Genuinely speculative, not-yet-decomposed forward research: open architectural questions, research-corpus extensions (`research/agentic-engineeriing-sdlc.md` Phase-8→Phase-9 graduation criteria; cross-cutting-concern application per the canonical SDLC), and any arc not fitting Surfaces I–IX/XI.
- **Current state.** Named with a decomposition-owed marker; **no concrete items committed** — this surface is deliberately not padded.
- **Close-out steps.** Operator-seeded when a specific research question crystallizes (e.g., the workflow-doc v1.14+ Phase-8→Phase-9 retirement-criteria evolution; the NotebookLM 28-URL research corpus). **Council: conditional** — case-by-case, only if a named cross-domain tension surfaces.

### B-17 · ICM workspace-methodology adoption *(appended 2026-06-04 at HEAD `ca2bc34`)*
- **What it is.** A potential forward effort to adopt elements of the **Interpreted Context Methodology** (ICM — "folder structure as agent architecture"; `RinDig/Interpreted-Context-Methdology` + arXiv `2603.16021`) into the workspace **governance layer**. Foundation landed this arc: `ICM_Alignment_Audit_v1.md` (read-only 4-agent audit, committed `ca2bc34`) with a tiered reconciliation roadmap at §8 (`R-ICM-1..7` + non-goals `N-ICM-1/2`). Introduces NEW surface **XII Methodology** to this register.
- **Current state.** Audit only — **no adoption decided**. Repo scores ~90% on ICM *values* (one-way refs, canonical sources, plain-text, single-job decomposition, edit-surfaces, stage-audits) / ~50% on ICM *structure* (token budgets, numbered-stage `CONTEXT.md` layering, file-size caps). Headline debt: root `CLAUDE.md` ≈ 85.7K tok (~107x ICM's ~800-tok L0 target; 2.4–4.0x ICM's own 30–50K monolithic anti-pattern). Two in-repo ICM beachheads already exist (`.harness/spec-code-overlay/` = full canonical ICM `stages/NN/CONTEXT.md`; `.harness/council/context-memory-grounding/` = numbered stages). ICM reference corpus vendored at **gitignored** `ai-docs/Interpreted-Context-Methdology/`. Memory: `icm-audit-and-adoption-foundation`.
- **Close-out steps.** Operator decides 3 gates from audit §8 **before** any spec: (1) **scope** — governance-layer-only (recommended) vs governance + selected workflows; (2) **file-size caps** — adopt ICM `<80`/`<200`-line caps where, exempt what (`design-substrate/` specs?); (3) **L0-refactor appetite** — how aggressive on `R-ICM-1` (split the ~85.7K-tok root `CLAUDE.md`), the highest-leverage but most-invasive change to a load-bearing governance doc. If pursued: seeds a formal **`R-IF-113`** arc; start from audit §8; reuse the `.harness/spec-code-overlay/` canonical-ICM template; frame as **reconciliation, not conversion** (`N-ICM-1/2`: the product H_T stays a coordination framework; ICM is sequential / anti-framework — adopt VALUES in the governance layer, not wholesale). **Council: ⚖️ conditional** — nameable two-voice tension (context-minimalism / token-budget [C2-style] ⊥ governance-completeness; the L0-split risk).

---

## 2. Provenance + method

- **Two tiers per advisor guidance:** Phase-8 *closure residuals* (Tier A — declare Phase 8 done) kept distinct from *post*-Phase-8 forward activation (Tier B); the retirements are **legitimate per X-AL-2** (the H_E scaffold was displaced; production exercise was never an X-AL-2 condition) — this register is the *next axis* of work, not a correction.
- **CXA status spine = the R-700 dispositions** verified against the ledger + merged at PR #207 (CXA-1 PARTIAL / CXA-2 STILL-BOUNDED / CXA-3 STILL-BOUNDED / CXA-4 PARTIAL / CXA-5 RETIRED). Subagent reports supplied close-out *mechanism* detail only — three subagent CXA *status* claims were rejected (CXA-3 "N/A" was a misread; CXA-4 "fully-wired" contradicted R-700 PARTIAL; an "RT-35 PR #52 awaiting merge" claim was stale).
- **Surface IV centerpiece empirically verified this session:** `routing_core_surface.infer()` raises `NotImplementedError` (`:83`/`:97`); `layered_routing_strategy.route()` has zero non-test callers; **but** `retry_breaker_fallback.py` (C-RT-16) *does* implement fallback-chain advancement (the subagent's "fallback not implemented / re-raises" claim was corrected). Accurate framing: provider construction + failure-time fallback wired; capability-aware routing-*selection* stubbed; multi-provider operation **unexercised at MVP**.
- **Council discrimination per CLAUDE.md §13.2 + §10.9:** register-compilation is descriptive synthesis (solo + advisor, not council); 7 forward arcs flagged `⚖️ council-eligible` with named two-voice tensions for when the operator opens them (the roadmap already encodes this on R-410/411/412).
- **Decomposition obligation:** this register discharges the roadmap §9 decomposition owed for Surfaces IV/VI/IX/X and supplies the substance for the `R-NNN` coverage gap (A-3 / B-14) R-700 surfaced.
- Grounded in: ADR-F1/F4/F5 + ADR-D2/D3/D5/D6; CP spec v1.30 `C-CP-01..04`; OD spec v1.27 `C-OD-10/13`; AS spec `C-AS-05/13/15`; runtime spec v1.41 `C-RT-16/22/29` + §14.9.8 + §14.C/D; CXA v2.18 §2.3.x; production source at `harness-{cp,runtime,od,as}/src/`.
