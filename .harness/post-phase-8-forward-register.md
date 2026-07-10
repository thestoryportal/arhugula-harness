# Post-Phase-8 Forward Work Register

> **Status: Claude-authored register for operator planning.** Comprehensive enumeration of the integrations, implementations, and operator-led actions that remain **after** Phase-8 substitution-closure — each grounded in the design-substrate, with current production state and concrete close-out steps. **Posture: mode-agnostic** (process-substrate; reads `design-substrate/` + `harness-*/src/` + `.harness/`; authors only this `.harness/` file). Sibling to `.harness/R-700-phase-8-closure-accounting-draft.md` (the substitution accounting this register builds forward from). Compiled at HEAD `01cd0fa`, 2026-06-01.

---

## 0. Thesis — what "post-Phase-8" means for this harness

**Phase 8 closed the *substitution accounting*, not the *capability activation*.** Per the roadmap §1 + X-AL-2 (Meta-Architecture §7.7), a substitution RETIRES when (A) its cited units land **and** (B) the H_E scaffold surface is no longer invoked at the substitution site. **X-AL-2 never required the underlying capability to be exercised in production** — only that the hand-built H_T substrate displaced the Claude-Code scaffold. The ratified Phase-8 accounting was **46/54 RETIRED (85.2%) + 49/54 pipeline-advanced (90.7%)**. Batch-52 later back-flowed the live R-810/R-820 evidence for AS-8e, AS-8f, and CP-17; batch-53 then back-flowed OD-4 and CXA-4; batch-54 lands the CP→AS runtime composer; batch-55 records CXA-2 as a counted bounded residual; batch-56 retires CXA-1 after the AS→IS producer and edge-scope audit close. The current live ledger is **54/54 RETIRED (100.0%) + 54/54 pipeline-advanced (100.0%)**.

What remains is a **different axis of work**: *activation, deployment, scale, and external integration* of capabilities that are, in many cases, **library-complete / structurally present but not yet exercised at runtime** (multi-LLM routing, real sandbox isolation, non-LOCAL deployment surfaces, multi-tenant redaction, MANAGED_CLOUD secrets, external MCP/Files/managed_agents integrations). This is **not "fixing incomplete retirements"** — it is building the production frontier the MVP deliberately stopped short of.

The register has **two tiers**, kept distinct:

- **Tier A — Phase-8 closure residuals.** These have now been dispositioned: the R-700 review declared Phase 8 closed, bounded-residual sign-offs were ratified, the invisible-row `R-NNN` coverage was authored, and the config-discovery fork was ratified. Historical detail remains below for provenance.
- **Tier B — Post-Phase-8 forward activation.** The genuinely-forward surfaces (Multi-LLM IV / Multi-deployment V / Multi-tenant VI / External-integrations IX / Research X / Operator-tooling XI) + the CXA composition seams.

**This register also discharges a roadmap obligation.** Roadmap §1 marks Surfaces IV / VI / VIII–X as `decomposition-owed` (§9). This document **is** that decomposition for IV / VI / IX / X — its items can seed `R-300` / `R-500` / `R-800` / `R-900` entries, which also closes the **no-`R-NNN`-entry gap** R-700 surfaced for `CXA-1/2/3/4` + `CP-17`.

**Council note (answering the standing question).** Compiling *this register* is descriptive synthesis grounded in substrate — **not** a design decision with a nameable cross-domain tension, so per CLAUDE.md §13.2 + §10.9 it routes to solo + `advisor()`, not the council. But several **forward arcs below carry nameable two-voice tensions that ARE council-eligible the moment the operator opens them to execute** — each is flagged `⚖️ council-eligible` with the named voices. (The roadmap already encodes this on R-410/411/412 via `council_required: conditional:nameable-tension`.)

---

## 1. Front summary table

### Tier A — Phase-8 closure residuals (declare Phase 8 done)

*Status legend: ~~strike~~ = definitively closed · **[open]** = actionable now · **[blocked]** / **[deferred]** / **[proposed]** = not-closed-not-open (word = why). Mirrors the live dashboard's R-NNN board + Post-Phase-8 register sections.*

| # | Status | Item | Owner action | Spec/source | Council? |
|---|---|---|---|---|---|
| A-1 | ~~closed~~ | ~~R-700 Phase-8 substitution review + final integer ratification~~ | Phase 8 declared closed at 46/54 retired + 49/54 pipeline-advanced; batch-56 live ledger now reports 54/54 + 54/54 | `R-700-phase-8-substitution-accounting` RESOLVED; batch-56 | no (AUQ) |
| A-2 | ~~closed~~ | ~~Bounded-residual sign-offs (AS-8e, AS-8f, OD-6)~~ | Operator ratified terminal bounded-residual dispositions | X-AL-2 §5.3; Surface VIII | no (AUQ) |
| A-3 | ~~closed~~ | ~~`R-NNN` coverage for the 5 invisible open rows (CXA-1/2/3/4 + CP-17)~~ | CXA-1/2/3/4 and CP-17 now have roadmap entries | R-700 draft §C item 2 | no |
| A-4 | ~~closed~~ | ~~`harness.toml` auto-discovery fork ratification~~ | Reading A ratified 2026-06-06; implementation had already shipped at PR #279 | `R-100-mvp-config-discovery` RESOLVED | no |

### Tier B — Post-Phase-8 forward activation

| # | Status | Surface | Item | Current state | Close-out class | Council? |
|---|---|---|---|---|---|---|
| B-1 | ~~closed~~ | IV Multi-LLM | ~~Layered capability-aware routing activation~~ | **routing activation RESOLVED (R-300-multi-llm-routing-activation, PR #213)** — declarative layer live; the multi-provider *exercise* is B-2 | impl + operator creds | ⚖️ yes |
| B-2 | ~~closed~~ | IV Multi-LLM | ~~Multi-provider credentials + mixed-provider exercise~~ | **R-300 second-provider exercise RESOLVED** — deterministic fallback + live Anthropic→OpenAI (#281) + live Ollama (#283) | PR #281 + PR #283 | no |
| B-3 | ~~closed~~ | V Deployment | ~~Real TIER_2 container sandbox execution (R-410)~~ | **R-410 RESOLVED by local Docker execution driver + live TIER_2 container e2e** | this PR | ⚖️ yes |
| B-4 | ~~closed~~ | V Deployment | ~~TIER_3 microVM + TIER_4 full-VM execution (R-411/R-412)~~ | **R-411 RESOLVED** by Docker + gVisor/runsc ToolExecutionDriver on the operator-provisioned Lima Linux VM; **R-412 RESOLVED** by the managed E2B full-VM ToolExecutionDriver + live Tier-4 dispatcher e2e | impl + infra | ⚖️ yes |
| B-5 | ~~closed~~ | V Deployment | ~~SELF_HOSTED_SERVER + MANAGED_CLOUD e2e (R-420/R-421)~~ | **R-420 RESOLVED by local single-node self-hosted daemon + collector + keyring live e2e; R-421 RESOLVED by approved E2B + GCP Secret Manager + authenticated Cloud Run collector live e2e** | this PR | ⚖️ closed |
| B-6 | ~~closed~~ | V Deployment | ~~OTLP tail-keep collector-side validation (R-430)~~ | **R-430 RESOLVED** by the R-420 local real-collector tail-keep live proof | PR #326 | no |
| B-7 | ~~closed~~ | V Deployment | ~~Tier-level self-hosted secrets backend selector (R-440)~~ | **SELF_HOSTED keyring-only selector landed; cloud bootstrap-token remains R-421** | this PR | no |
| B-8 | ~~closed~~ | VI Multi-tenant | ~~Non-default `tenant_id` / non-SOLO `persona_tier` deployment~~ | **R-500 RESOLVED** by the local self-hosted multi-tenant live proof | PR #328 | ⚖️ closed |
| B-9 | ~~closed~~ | VI Multi-tenant | ~~OD-4: per-session redaction toggle (§13.1) + opaque-token tokenization (§13.2)~~ | **R-008 + batch-53 RESOLVED** — runtime code residual closed; live ledger back-flow moves OD-4 to RETIRED | accounting/back-flow | ⚖️ closed |
| B-10 | ~~closed~~ | IX External | ~~Real external MCP server connection~~ | **✅ R-800 RESOLVED (2026-06-01)** — `start()`/`shutdown()` wired at PR #172 (spec v1.41 §14.9.8 Gaps B/F); real external stdio e2e green & unconditional at `test_u_rt_86`. Full `api.run` path = Gap D (R-100 AC#2, operator-gated) | impl | no |
| B-11 | ~~closed~~ | IX External | ~~Files API integration (AS-8e / CP-17)~~ | **R-810 RESOLVED by real Anthropic Files upload/reference/delete plus managed-cloud `files.operation` Cloud Trace proof** | this PR | no |
| B-12 | ~~closed~~ | IX External | ~~managed_agents integration (AS-8f)~~ | **R-820 RESOLVED** by the real Anthropic Managed Agents SDK/session integration plus managed-cloud `managed_agents.*` proof | PR #380 | no |
| B-13 | **[applied / pending operator e2e]** | IX External | Memory-tool production backend (CP-16) | SELF_HOSTED SQLite, live S3 cloud-vault, and provider-free managed-DB implementation are done; live managed-DB proof waits on operator PostgreSQL-compatible DSN + explicit approval | impl + operator creds/infra | no |
| B-14 | ~~closed~~ | CXA | ~~Cross-axis seam completion (CXA-1)~~ | **CXA-1 is closed by batch-56** after the workflow-time scoped secret-fetch producer, resolver-bound AS→IS write, and edge-scope audit landed. **CXA-2 is closed by batch-55** as a counted bounded residual after provider-turn HITL continuation landed and durable recovery was recorded as post-MVP hardening; **CXA-3 is closed by batch-54** after the CP→AS runtime composer landed; **CXA-4 is closed by batch-53** after 0-wireable grounding. | impl (mechanical) | no |
| B-15 | **[proposed]** | XI Tooling | Dashboard iteration-2 (R-XI-02/R-XI-03) | MVP live; iteration-2 nice-to-have | impl | no |
| B-16 | **[proposed]** | X Research | Open architectural / speculative arcs | not decomposed | research | no |
| B-17 | **[proposed]** | XII Methodology *(NEW)* | ICM workspace-methodology adoption | **audit landed** (`ca2bc34`, `ICM_Alignment_Audit_v1.md`): ~90% ICM-values / ~50% ICM-structure (15.5/23); root `CLAUDE.md` ~107x ICM L0 budget; no adoption decided | design (spec/plan) — reconciliation, not conversion | ⚖️ conditional |

---

# TIER A — Phase-8 closure residuals

## A-1 · R-700 Phase-8 substitution review + final-integer ratification
- **What it is.** The operator-owned Phase-8 review (`R-700-phase-8-substitution-accounting`, BLOCKED) that consumes the R-700 draft and declares all 54 substitutions RETIRED or RETIRED-AS-BOUNDED-RESIDUAL with rationale (Surface VIII closure criterion, roadmap §1).
- **Current state.** CLOSED. The operator lifted the hold and Phase 8 was declared closed on 2026-06-02 at 46/54 RETIRED and 49/54 pipeline-advanced. Batch-52, batch-53, batch-54, batch-55, and batch-56 are forward live-ledger supersessions, not rewrites of that declaration: R-810/R-820 evidence moves AS-8e, AS-8f, and CP-17 to RETIRED; the OD-4/CXA-4 accounting back-flow moves two more rows to RETIRED; the CP→AS runtime composer moves CXA-3 to RETIRED; the CP→IS seam moves CXA-2 to counted bounded residual; the AS→IS seam moves CXA-1 to SUBSTANTIVE_RETIRED. The live ledger now reports 54/54 RETIRED and 54/54 pipeline-advanced.
- **Close-out steps.** None. **Council: no** — this was a ratification (advisor + AskUserQuestion), not a multi-voice design tension.

## A-2 · Bounded-residual sign-offs (AS-8e, AS-8f, OD-6)
- **What it is.** Three substitutions closed as deferred-by-design / dormant-at-MVP that need an explicit operator Phase-8 sign-off per X-AL-2 §5.3: **AS-8e** (`files.*` namespace, Files-arc Memory-only MVP scope, runtime spec v1.17 §14.C); **AS-8f** (`managed_agents.*`, production-only exclusion, `class_1_fork_as_8f_...` Q1=C); **OD-6** (local-first OTLP sqlite ingestion — `flush_to_sqlite` dormant at MVP, FIRST bounded-residual close in the ledger, batch-51).
- **Close-out steps.** None for Phase-8 accounting. The operator ratified the terminal bounded-residual dispositions. Later implementation proofs for Files and managed_agents are tracked by R-810/R-820; batch-52 is the separate accounting/back-flow action that moves AS-8e, AS-8f, and CP-17 in the live ledger. **Council: no** (sign-off).

## A-3 · `R-NNN` coverage for the 5 invisible open rows
- **What it is.** R-700 surfaced that `CXA-1/2/3/4` + `CP-17` have **no roadmap `R-NNN` entries** — the R-002 Surface-I decomposition surveyed only the per-axis `§4.1`, which excludes the CXA axis (no `§4.1` file) and didn't frame CP-17's batch-44 SB-INDEF reclassification as open.
- **Close-out steps.** None. CP-17 is tracked by R-010/R-810, and CXA-1/2/3/4 are tracked by R-CXA-1..4. **Council: no.**

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
- **Current state.** R-411 is closed for the selected no-taxonomy-change path. `GVisorRunscToolRunnerExecutionDriver` extends the R-410 Docker runner substrate, requires `SandboxTier.TIER_3_MICROVM`, and invokes Docker with `--runtime=runsc`. The approved live e2e targets the operator-provisioned Lima Linux VM through `R411_GVISOR_DOCKER_COMMAND`; host readiness passed, the TOOL_STEP executed under `runsc`, network egress was blocked, and the host repo path was not visible. R-412 is closed by the operator-approved managed E2B path: `E2BManagedFullVMToolRunnerExecutionDriver` requires `SandboxTier.TIER_4_FULL_VM`, creates an E2B managed sandbox with outbound internet disabled by default, and exchanges the same JSON runner shape as the local Docker/gVisor drivers. The approved live e2e (`just r412-e2b-full-vm-live-e2e`) passed on 2026-06-08 with provider `e2b-managed` and tech `e2b-firecracker`.
- **Close-out steps.** None for R-411/R-412. Local Firecracker and QEMU `microvm` remain valid future self-managed variants, but the roadmap Tier-4 managed-cloud lane is closed by E2B. **`⚖️ Council (C10 ⊥ C11)`** inherited from B-3.

### B-5 · SELF_HOSTED_SERVER + MANAGED_CLOUD deployment e2e (R-420 / R-421)
- **What it is.** First real non-LOCAL surfaces. **R-420 (SELF_HOSTED_SERVER):** harness daemon (`C-RT-29 §14.18`, FastMCP Unix-socket) against a **real OTLP collector** + tier-level secrets; tail-keep wrapping active (non-LOCAL); per-cell sampler `base_rate` = the SELF_HOSTED cell. **R-421 (MANAGED_CLOUD):** cloud env + cloud secrets + FULL_VM + managed collector; in-sandbox encrypted-fs secrets per ADR-F5; MANAGED_CLOUD per-cell sampler + redaction posture (`C-OD-13 §13.1`).
- **Current state.** R-420 is **RESOLVED** by the local single-node SELF_HOSTED_SERVER stack at `deploy/self-hosted-local/`: host-run harness daemon + Docker Compose OTel Collector Contrib, Tempo, and Grafana; `harness.selfhosted.local.example.toml` selects `SELF_HOSTED_BACKEND_COLLECTOR` and `self-hosted-keyring`; `just r420-self-hosted-stack-*` controls the backend. Closure evidence 2026-06-07: Docker stack running, `just r420-self-hosted-readiness harness.selfhosted.local.toml` passed, and `just r420-self-hosted-live-e2e harness.selfhosted.local.toml` passed with workflow `r420-self-hosted-tool-echo`, daemon status `success`, cost `0`, hosted-provider-calls `0`. The live workflow uses local Ollama plus non-secret keyring sentinel `r420_probe_key`; no hosted-provider inference is performed. R-421 is **RESOLVED** by the approved E2B + GCP Secret Manager + authenticated Cloud Run collector live e2e: `just r421-managed-cloud-readiness /private/tmp/r421-managed-cloud.live.toml --hosted-sandbox-provider e2b` passed, the hosted E2B sandbox ran the deterministic command, authenticated OTLP export reached Cloud Run, and Cloud Trace observed trace `d848a4da6622f42407a5e58c507513c5` with spans `r421.managed_cloud.root` and `sandbox.violation`.
- **Close-out steps.** None for R-420/R-421. R-420 **unblocks R-430** and removes the self-hosted prerequisite for R-421; R-421 supplied the managed-cloud prerequisite that R-412 consumed for the selected E2B full-VM provider path. **`⚖️ Council (R-421 only)`** — closed by the selected E2B + GCP path.

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
- **What it is.** The OD-4 substitution row was `PARTIAL` / `RETIRED-AS-CROSS-AXIS-DEFERRED` in the Phase-8 accounting, but the previously open runtime gates have now been implemented and the live ledger was back-flowed at batch-53.
- **Current state.** The §13.1 solo-developer per-session toggle is closed. The 2026-06-07 R-008 slices added an OD-owned opaque-token substrate, durable audit-ledger token-map persistence, provider-free category labeling, and the runtime `EvalGradeSemanticRedactionClassifier` path for GenAI prompt/response, tool argument/result, retrieval, file, memory, skill, PII, and secret surfaces. Stage 4 now wires `MULTI_TENANT_COMPLIANCE` redaction through `OpaqueRedactionTokenizer` + `AuditLedgerRedactionTokenMap` when an audit sink is available; without an audit sink, it preserves fail-closed strip mode.
- **Close-out steps.** None. Batch-53 performs the separate accounting/back-flow decision and moves OD-4 from `PARTIAL` to `SUBSTANTIVE_RETIRED`; the `RETIRED-AS-CROSS-AXIS-DEFERRED` label remains historical Phase-8 provenance only.
- **`⚖️ Council (C7 ⊥ eval-utility/C11).`** Privacy-default-off (C7) vs eval-grade content-shape-reconstruction utility: tokenize vs strip is a real two-voice call. Convene when R-008 opens.

---

## Surface IX — External integrations (R-800..R-899, decomposition-owed)

### B-10 · Real external MCP server connection
- **What it is.** Connect the FastMCP client host to a **real external MCP server** for operator `api.run` TOOL_STEP execution (the TOOL_STEP path the R-100 use-the-product probe exercised).
- **✅ RESOLVED 2026-06-01 (R-800).** This "Current state" framing was **stale** — it was authored at PR #209 but describes pre-PR-#172 state. Verified empirically: the bootstrap **does** call `await ctx.mcp_client_host.start()` (`stage_3a_cp_clients.py:59`) and `host.shutdown()` is wired at teardown (`shutdown.py:484-489`) — both landed at PR #172 (spec v1.41 §14.9.8 Gaps B/F). The converter (spec v1.40, Reading B) + sandbox-decision-resolver (spec v1.41 §14.9.8, Reading B) also landed. A **real external stdio MCP server** is exercised end-to-end at `test_u_rt_86` (production factory `materialize_mcp_client_host_stage` + real subprocess + handshake + list_tools + TOOL_STEP dispatch + 7-attr `mcp.*` span) — **unconditional, no LLM, 9/9 green** (with `test_ac2_bootstrap_path_wiring`).
- **Original close-out steps (all met).** (1) `host.start()` at stage-3a — ✅ `stage_3a_cp_clients.py:59`; (2) `host.shutdown()` at teardown — ✅ `shutdown.py:484-489`; (3) operator `MCPClientConfig.connection_url` + per-server defaults — ✅ surface landed (spec v1.40/v1.41); (4) live e2e against a real external server — ✅ `test_u_rt_86` (real subprocess). **Council: no** (mechanical; confirmed not needed).
- **Residual (out of R-800 scope).** The **full `api.run` bootstrap TOOL_STEP path** (must_pass[3] strict reading) is **Gap D / R-100 AC#2** — the bootstrap pings ≥1 provider regardless of step kind, so the `api.run` echo-MCP e2e (`test_r100_ac2_tool_step_e2e`) is skipif-gated on a live provider (ollama OR `ANTHROPIC_API_KEY`) and is **operator-gated by design** (not fired unilaterally). Making the provider ping conditional on an inference step is a **Class 1 fork candidate** carrying a nameable **C9⊥C11** tension (fail-fast reliability ⊥ tool-only-workflow ergonomics) → **dyadic-council-eligible** per CLAUDE.md §10.9 if the operator opens it.

### B-11 · Files API integration (AS-8e / CP-17)
- **What it is.** Anthropic Files API (`/v1/files` upload/list/metadata/delete; `file_id` reference in message content) — ADR-D3 primitive #10; the `files.*` observability namespace (AS-8e) + the CP-16/17 Files-primitive consumption.
- **✅ RESOLVED 2026-06-08 (R-810).** Operator opened the previously deferred Files arc. The runtime design shape is the already-ratified FilesAPIClient/adapter + file_id-reference-composition path from `.harness/class_1_fork_h_t_cp_16_17_executable_consumer_absence.md` §13.6.C, landed by the R-810 runtime port and real Anthropic Files adapter.
- **Close-out steps (all met).** (1) **Design-phase:** Files arc opened at operator-discretion timing with the §13.6.C runtime unit shape; (2) **impl:** managed-cloud Anthropic Files client adapter + document file-reference and Batch request composition landed; (3) **e2e:** live Anthropic upload + reference-by-id + delete path passed, and `files.operation` exported through the authenticated managed collector was observed in Cloud Trace `bfd28fa8fc8ecc3ba973d1e405cdb865` with `files.*` attrs. The uploaded live file is no longer present (cleanup retry returned Anthropic 404). Temporary GCP TokenCreator IAM used for Cloud Run ID-token minting was removed.

### B-12 · managed_agents integration (AS-8f)
- **What it is.** Anthropic managed_agents primitive + the `managed_agents.*` 3-attribute namespace.
- **Current state.** **RESOLVED for the R-820 runtime/integration gate** — PR #380 added the real Anthropic Managed Agents SDK/session adapter and live managed-cloud e2e proof. Evidence: session `sesn_019aMgaF8sAW2cXhhpMTYij4` reached `session.status_idle`; `managed_agents.runtime` exported to the managed collector; Cloud Trace trace `009d7716b19c75e4ad7edb93e78f8d2b` carried `managed_agents.*` attributes. Temporary Cloud Run Token Creator IAM used for the proof was removed and verified absent.
- **Close-out steps.** R-820 is closed. Batch-52 performs the separate substitution-tally back-flow for AS-8f, moving it from the Phase-8 accepted-indefinite-defer disposition to `SUBSTANTIVE_RETIRED` in the live ledger. **Council: no.**

### B-13 · Memory-tool production backend (CP-16)
- **What it is.** A production storage backend for the Memory tool beyond local-filesystem. ADR-D3 #11 (Memory tool is client-side; harness implements the backend). `C-RT-22` `MemoryToolRegistry` + `MemoryToolStorageBackendProtocol`.
- **Current state.** **RESOLVED.** Registry + **FILESYSTEM backend landed** (`LocalFilesystemMemoryToolBackend`; `CP-16` closed RETIRED-AS-BOUNDED-RESIDUAL batch-44), **SELF_HOSTED_SERVER `DATABASE` backend landed** (`SqliteMemoryToolBackend`, stdlib sqlite3), **MANAGED_CLOUD S3 cloud-vault backend live-proven**, and **MANAGED_CLOUD PostgreSQL managed-DB backend live-proven**. The approved live S3 e2e bound `MemoryToolStorageBackend.S3` on `DeploymentSurface.MANAGED_CLOUD`, used AWS CLI profile credentials, and exercised create/view/str_replace/insert/delete through the Memory tool dispatch seam. The managed-DB backend (`ManagedSqlMemoryToolBackend`) handles PostgreSQL-compatible `postgres://` / `postgresql://` `DATABASE` bindings, the factory lazily constructs `psycopg` only for live use, and the operator-approved Neon e2e passed against the `Arhugula` project.
- **Close-out steps.** All R-830 production backend slices are closed. The managed-DB proof used `just r830-managed-db-live-e2e`, created the `memory_entries` table if needed, wrote a unique `/memories/live/...` row, exercised create/view/str_replace/insert/delete through `_invoke_protocol_callback`, and cleaned up. Gate closure is visible in `.harness/codex_credential_gates.jsonl`. **Council: no** (impl).

---

## CXA — Cross-axis composition seam completion (B-14)

> **Status spine = the live substitution ledger after batch-56, with R-700 dispositions preserved as historical provenance.** CXA edge counts per `Cross_Axis_Composition_Document_v2_18.md` §2.3.x. These are mostly **mechanical wiring** (runtime composer landings + production caller sites), not cross-domain design tensions → **Council: no** for all.

| Seam | Live disposition | Current state | Close-out |
|---|---|---|---|
| **CXA-1** (AS→IS, 13-edge legacy prose narrowed by audit) | **RETIRED** (batch-56) | `RuntimeToolDispatcher` emits scoped `SecretFetchEvent` records from active `TOOL_STEP` dispatch with non-hollow metadata; `RuntimeAsIsWiring` writes the AS→IS ledger entry with the bound R-003 procedural-tier sidecar. The edge-scope audit narrows current direct AS→IS obligations to U-AS-19/U-AS-28 read-only IS carrier imports plus the U-AS-26/U-AS-27 secret-fetch producer family. | **Closed by batch-56.** Bootstrap-value secret fetch remains excluded under Reading-D; do not invent callback surfaces for read-only carrier imports. |
| **CXA-2** (CP→IS, 36–43 edges) | **RETIRED** (batch-57; was RETIRED-AS-BOUNDED-RESIDUAL batch-55) | Workflow-layer pause/resume, override, and workload-selection producers fire from production caller sites; PR #449 added the HITL/recovery producer primitives; PR #452 bound them at stage 5 and proved direct CP→IS emissions; PR #454 wired Anthropic provider-turn HITL continuation through `ctx.hitl_tool_loop`. **The bounded residual (dormant engine recovery loop) is DISCHARGED at R-FS-1 E-impl-2 (batch-57):** the hand-rolled WAL segment-log substrate (U-RT-121) + WAL_SEGMENT materialization (U-CP-94) + engine-layer recovery-loop firing branch (U-CP-95) + durable factory bind & by-execution go-live e2e (U-RT-122) make `RuntimeEngineRecoveryLoop` fire `cp.pause-captured`/`cp.resume-attempted` against a crash-survivable store from a real WAL_SEGMENT driver — the R-CXA-2 engine-layer seam is LIVE in production. | **Closed by batch-55; residual discharged at batch-57.** The re-open trigger ("a real … WAL-segment … recovery loop lands") fired and was built — NOT a fake `workflow_driver.py` engine loop, but the genuine durable U-RT-121 substrate fired by the U-CP-95 WAL_SEGMENT driver branch. **RECONCILER_LOOP recovery (the other re-open class) is now CLOSED at R-FS-1 E-impl-3 (5/5 engine classes):** E-impl-3a #572 (U-CP-96 resumption) + E-impl-3b #574 (U-RT-123 etcd-style CAS-lease substrate) + E-impl-3c #576 (U-CP-97 engine-layer firing + U-RT-124 engine-class-aware go-live) bring R-CXA-2 LIVE for RECONCILER_LOOP against a DISTINCT durable reconciler store (no cross-contamination by construction). Non-gating residual: F1-01 WAL completed-run-retry exactly-once duplicate-emit (`.harness/r-fs-1-e-impl-3c-f1-01-wal-exactly-once.md`; symmetric fix-shape ready). |
| **CXA-3** (CP→AS, 24 edges) | **RETIRED** (batch-54) | `RuntimeCpAsWiring` materializes the CP-consumed AS terminal seam export registry at bootstrap stage 6, fail-closes on AS manifest coverage drift, and is exposed as `HarnessContext.cp_as_wiring`. | **Closed by batch-54.** The operator rejected scope narrowing and directed the runtime-composer path; focused lifecycle/bootstrap coverage proves the composer shape and context exposure. |
| **CXA-4** (OD→IS/AS/CP, 26 edges) | **RETIRED** (batch-53) | **Grounding sweep 2026-06-01 (R-CXA-4 grounding-first) corrects the prior "~5 of 26 / ~21 remaining" framing — a stale-carry mis-framing (CLAUDE.md §10.5).** Per CXA §2.5 the 26 canonical OD-outbound edges split **1 genuine typed seam + 19 convention-level + 6 phase-2-runtime**. The lone genuine data-flow edge (U-OD-30→U-IS-11 `audit_writer.append`) is already wired with production producers; the 6 phase-2 runtime edges are already materialized at bootstrap stage 6; the 19 convention edges are namespace/manifest/monotonicity alignment satisfied by stage-6 checks and manifest resolution. | **Closed by batch-53.** There is no wiring task and no cleanup task: grounding found 0 wireable edges, and placeholders were already resolved at CXA v2.3 + OD plan v2.11. Batch-53 consumes the bookkeeping/accounting residual and moves CXA-4 from `PARTIAL` to `SUBSTANTIVE_RETIRED`. |
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

## Surface XIII — Upstream decomposition-audit build arcs (2026-07-09)

*Source: `.harness/audit/Upstream_Decomposition_Audit_2026-07-09.md` — council-engaged intent→spec audit (0 silent gaps; 12 documented deferrals). Under the operator FULL-SPEC directive ("no MVP scoping; all beyond-MVP spec'd + built") the deferrals are build targets. The 9 already-tracked ones live in their existing homes (Arc R / B4 / B-TAIL / B-FALLBACK / C-AS-10 §10.3 / B3 / F-B3-2 / FM-2 / per-persona crypto — several BUILT-but-gated on a 2nd provider). The 2 net-new UNREGISTERED findings are registered here.*

### B-18 · U-1 — `cache_control` breakpoint emission *(NET-NEW, registered 2026-07-09)*
- **What it is.** The executable half of the **ADR-D3 §1.5 "prompt-cache breakpoint placement contract"** (per-cell breakpoint placement at parent-agent + per-sub-agent levels, composing D4 §1.8 concurrent-cache warm-up). The static-prefix/dynamic-suffix discipline + the observation attrs are built; the harness never AUTHORS a breakpoint — the runtime dispatch composer emits a **string-only** system prompt, so it cannot place `cache_control` markers.
- **Current state.** COMMITTED at ADR-D3 §1.5; deferred only as runtime spec §14.5.2:3620-3621 OQ-1 (string-only) + OQ-2 (perf follow-on); **in no ledger/register** (confirmed by acknowledgment-grep). Load-bearing C2 cost lever (cache-miss = 4–10× input tokens per ADR-F2 §Rationale(b)(ii)).
- **Close-out steps.** Un-defer runtime spec OQ-1 (structured/multi-block `system`-array content) + emit `cache_control` breakpoints per ADR-D3 §1.5 placement contract at the dispatch composer; tests (cache-prefix stability, breakpoint placement, ≤4-breakpoint Anthropic limit); clearance marker. Bundled design+impl. **Council: ⚖️ conditional** (C2 placement ⊥ C6 strategy per ADR-D3 §1.1 row 5 owner "C6+C2"). **ACTIVE — first build arc per operator 2026-07-09.**

### B-19 · U-2 — breaker `breaker.cause` + `breaker.cooldown_ms` attributes *(NET-NEW, registered 2026-07-09; operator-discretionary)*
- **What it is.** The two CP-side ambient breaker-state attributes (`breaker.cause` trip-cause enum + `breaker.cooldown_ms`) dropped when the CP `breaker.*` set was replaced by the OD 7-attribute *event* schema.
- **Current state.** CP spec v1→v1.1 change-note line 72 **"Semantic-loss note"** (dropped, no OD equivalent); line 47 flags re-introduction as **"operator-discretionary, forward-flagged, adjudicated NOT-FINDING at iter-2."** Unregistered. **A conscious event-vs-ambient design drop** — re-introduction is a genuine design call (does re-adding ambient-state attrs alongside the event schema cohere, or duplicate?).
- **Close-out steps.** Assess coherence of re-introducing ambient-state attrs alongside the OD event schema (possible council/architect vet); if built, extend the CP `harness.breaker.*` namespace + producer + observability. **Council: ⚖️ conditional.** DISPOSITION: build-or-skip decided at arc-open (leans build under FULL-SPEC; surface the redundancy concern first).

### R-1 confirmed-DEFERRED · Managed-cloud deployment-surface dispatch
- **Operator decision (2026-07-09):** the prior fork AS-8f **DEFER-INDEFINITELY (2026-05-28)** **STANDS** — the FULL-SPEC directive does NOT override this held decision. Managed-cloud dispatch (Persona §9/§10.2 + ADR-D2 §1.1 3-tier surface × blast-radius) remains deferred until a managed-cloud deployment. Recorded so the hold is honored, not silently reversed.

---

## 2. Provenance + method

- **Two tiers per advisor guidance:** Phase-8 *closure residuals* (Tier A — declare Phase 8 done) kept distinct from *post*-Phase-8 forward activation (Tier B); the retirements are **legitimate per X-AL-2** (the H_E scaffold was displaced; production exercise was never an X-AL-2 condition) — this register is the *next axis* of work, not a correction.
- **CXA status spine = the R-700 dispositions** verified against the ledger + merged at PR #207 (CXA-1 PARTIAL / CXA-2 STILL-BOUNDED / CXA-3 STILL-BOUNDED / CXA-4 PARTIAL / CXA-5 RETIRED). Subagent reports supplied close-out *mechanism* detail only — three subagent CXA *status* claims were rejected (CXA-3 "N/A" was a misread; CXA-4 "fully-wired" contradicted R-700 PARTIAL; an "RT-35 PR #52 awaiting merge" claim was stale).
- **Surface IV centerpiece empirically verified this session:** `routing_core_surface.infer()` raises `NotImplementedError` (`:83`/`:97`); `layered_routing_strategy.route()` has zero non-test callers; **but** `retry_breaker_fallback.py` (C-RT-16) *does* implement fallback-chain advancement (the subagent's "fallback not implemented / re-raises" claim was corrected). Accurate framing: provider construction + failure-time fallback wired; capability-aware routing-*selection* stubbed; multi-provider operation **unexercised at MVP**.
- **Council discrimination per CLAUDE.md §13.2 + §10.9:** register-compilation is descriptive synthesis (solo + advisor, not council); 7 forward arcs flagged `⚖️ council-eligible` with named two-voice tensions for when the operator opens them (the roadmap already encodes this on R-410/411/412).
- **Decomposition obligation:** this register discharges the roadmap §9 decomposition owed for Surfaces IV/VI/IX/X and supplies the substance for the `R-NNN` coverage gap (A-3 / B-14) R-700 surfaced.
- Grounded in: ADR-F1/F4/F5 + ADR-D2/D3/D5/D6; CP spec v1.30 `C-CP-01..04`; OD spec v1.27 `C-OD-10/13`; AS spec `C-AS-05/13/15`; runtime spec v1.41 `C-RT-16/22/29` + §14.9.8 + §14.C/D; CXA v2.18 §2.3.x; production source at `harness-{cp,runtime,od,as}/src/`.
