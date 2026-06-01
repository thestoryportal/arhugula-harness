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

| # | Item | Owner action | Spec/source | Council? |
|---|---|---|---|---|
| A-1 | R-700 Phase-8 substitution review + final integer ratification | Review the R-700 draft; ratify 46–47-vs-48 + bounded-residual sign-offs | `R-700-phase-8-substitution-accounting` (BLOCKED) | no (AUQ) |
| A-2 | Bounded-residual sign-offs (AS-8e, AS-8f, OD-6) | Operator signs the 3 deferred-by-design closes | X-AL-2 §5.3; Surface VIII | no (AUQ) |
| A-3 | `R-NNN` coverage for the 5 invisible open rows (CXA-1/2/3/4 + CP-17) | Authorize an R-002-style Surface-I pass | R-700 draft §C item 2 | no |
| A-4 | `harness.toml` auto-discovery fork ratification | Ratify Reading A/B/C of the config-discovery fork | `class_1_fork_harness_toml_default_discovery_unimplemented.md` | no (AUQ) |

### Tier B — Post-Phase-8 forward activation

| # | Surface | Item | Current state | Close-out class | Council? |
|---|---|---|---|---|---|
| B-1 | IV Multi-LLM | Layered capability-aware routing activation | routing-selection stubbed; fallback-chain dispatch wired; **unexercised** (single-provider MVP) | impl + operator creds | ⚖️ yes |
| B-2 | IV Multi-LLM | Multi-provider credentials + mixed-provider exercise | only Anthropic exercised at R-100 | operator creds + fixture | no |
| B-3 | V Deployment | Real TIER_2 container sandbox execution (R-410) | tier/provider are annotations-only; in-process FastMCP regardless of tier | impl + infra (Class-1 likely) | ⚖️ yes |
| B-4 | V Deployment | TIER_3 microVM + TIER_4 full-VM execution (R-411/R-412) | not built | impl + infra | ⚖️ yes |
| B-5 | V Deployment | SELF_HOSTED_SERVER + MANAGED_CLOUD e2e (R-420/R-421) | LOCAL-only exercised | operator infra | ⚖️ (R-421) |
| B-6 | V Deployment | OTLP tail-keep collector-side validation (R-430) | buffer logic in-process; collector-side unverified | operator infra | no |
| B-7 | V Deployment | Tier-level + cloud secrets backend (R-440) | LOCAL keyring + env-fallback only | impl + operator infra | ⚖️ yes |
| B-8 | VI Multi-tenant | Non-default `tenant_id` / non-SOLO `persona_tier` deployment | fields plumbed; non-toggleability enforced; base-rate envelope live | operator deploy + impl | ⚖️ yes |
| B-9 | VI Multi-tenant | OD-4: per-session redaction toggle (§13.1) + opaque-token tokenization (§13.2) | strip-not-tokenize MVP; toggle deferred | impl (R-008) | ⚖️ yes |
| B-10 | IX External | Real external MCP server connection | **✅ R-800 RESOLVED (2026-06-01)** — `start()`/`shutdown()` wired at PR #172 (spec v1.41 §14.9.8 Gaps B/F); real external stdio e2e green & unconditional at `test_u_rt_86`. Full `api.run` path = Gap D (R-100 AC#2, operator-gated) | impl | no |
| B-11 | IX External | Files API integration (AS-8e / CP-17) | STILL-BOUNDED-INDEFINITELY by design | design-phase + impl | no |
| B-12 | IX External | managed_agents integration (AS-8f) | STILL-BOUNDED-INDEFINITELY by design | design-phase + impl | no |
| B-13 | IX External | Memory-tool production backend (CP-16) | local-fs backend landed; cloud/db deferred | impl | no |
| B-14 | CXA | Cross-axis seam completion (CXA-1/2/3/4) | CXA-1 PARTIAL, CXA-2/3 STILL-BOUNDED, CXA-4 PARTIAL | impl (mechanical) | no |
| B-15 | XI Tooling | Dashboard iteration-2 (R-XI-02/R-XI-03) | MVP live | impl | no |
| B-16 | X Research | Open architectural / speculative arcs | not decomposed | research | no |

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
- **What it is.** Spec §3.7 (`C-RT-30`) declares `harness.toml` is discovered at "workspace root" by default; the impl never wired it (`DEFAULT_CONFIG_FILE_NAME` at `config_source.py:43` is a dead constant; "workspace root" is undefined — CWD vs the config's own `repository_root`, circular). **Does NOT block the MVP** (worked around via `just run --config`).
- **Close-out steps.** Ratify one reading of `class_1_fork_harness_toml_default_discovery_unimplemented.md` (PROPOSING): **(A)** CWD discovery / **(B)** upward search / **(C)** spec amendment dropping the clause. Then a small impl arc (Claude-executable once ratified). Tracked at `R-100-mvp-config-discovery` (BLOCKED). **Council: no** (AskUserQuestion).

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
- **Current state.** R-100 e2e ran a **3-step single-provider** workflow (Anthropic Haiku) with an **empty** fallback chain (`primary=anthropic, same_family=(), cross_family=()`). OpenAI/Ollama never invoked; no failure → no fallback traversal.
- **Close-out steps.** (1) **Operator:** provision OpenAI key (`openai_key` in keyring / `OPENAI_API_KEY` env) + Ollama host; (2) author a mixed-provider fixture that forces a primary-provider failure and asserts cross-family advance (Anthropic → OpenAI) with `routing.*`/`fallback.*` span attributes + cost tracking per candidate; (3) verify across deployment surfaces (Ollama at LOCAL, hosted at SELF_HOSTED/MANAGED). **Council: no** (operator setup + test authoring).

---

## Surface V — Multi-deployment surfaces (R-400..R-499)

> Per ADR-D2 (per-deployment-surface sandbox provider) + ADR-F4 (4-tier blast-radius) + ADR-F5 (tier-aware secrets) + `C-AS-15 §15` + `C-RT-29 §14.18` (daemon). The **12-cell `deployment_matrix.py`** maps `(DeploymentSurface, BlastRadiusTier) → (SandboxTier, SandboxProviderClass)`: LOCAL/SELF_HOSTED use process/container/microVM/full-VM provider classes with **LOCAL keyring** secrets; **MANAGED_CLOUD** reserves FULL_VM at TIER_4 and **defers** its secrets backend to prod-tech. `multi-tenant-compliance × local-development` is a **closed cell** (raises `CellBindingViolation`). **This is the honest frontier of the harness: at HEAD the sandbox tier/provider are observability + policy *annotations only* — `mcp_client_host.call_tool` always uses in-process FastMCP stdio regardless of tier.**

### B-3 · Real TIER_2_CONTAINER sandbox execution (R-410) `⚖️ council-eligible`
- **What it is.** Make a tool call resolved to `TIER_2_CONTAINER` actually execute inside a container boundary (verifiable FS/network isolation), not in-process. **The honest heart of Surface V.**
- **Current state.** The `SandboxDecisionResolver` (runtime spec v1.41 §14.9.8) returns a tier *decision*, but **no code path enforces isolation** — execution is in-process regardless of tier.
- **Close-out steps.** (1) Build a real container provider (Docker/Podman/runc-class); (2) author the execution-driver contract mapping resolved-tier → actual sandbox mechanism (**unspecified beyond §14.9.8 — almost certainly opens a Class-1 fork**); (3) e2e: a TIER_2 TOOL_STEP runs in a container, tier-floor still raises on under-tier, `sandbox.enter/exit` spans carry the real provider/tech. `advisor_required: yes` per roadmap.
- **`⚖️ Council (C10 ⊥ C11) — roadmap already flags `conditional:nameable-tension`.`** Action-safety/blast-radius (C10) wants real isolation; operator-loop/local-deployment (C11) wants minimal provisioning burden. Convene the dyad when R-410 opens.

### B-4 · TIER_3 microVM + TIER_4 full-VM execution (R-411 / R-412) `⚖️ council-eligible`
- **What it is.** Extend executable isolation up the ladder: TIER_3 (gVisor/Kata, EXTERNAL_REVERSIBLE) then TIER_4 (firecracker/full-VM, EXTERNAL_IRREVERSIBLE, **MANAGED_CLOUD-only** per the matrix).
- **Current state.** Not built; depend on B-3 settling the execution-driver pattern (R-412 also co-gates on R-421 — a real MANAGED_CLOUD surface). Deferred-far per ADR-D2.
- **Close-out steps.** Provider-class additions once B-3 lands the pattern; per-tier blast-radius enforcement; e2e per tier. **`⚖️ Council (C10 ⊥ C11)`** inherited from B-3.

### B-5 · SELF_HOSTED_SERVER + MANAGED_CLOUD deployment e2e (R-420 / R-421)
- **What it is.** First real non-LOCAL surfaces. **R-420 (SELF_HOSTED_SERVER):** harness daemon (`C-RT-29 §14.18`, FastMCP Unix-socket) against a **real OTLP collector** + tier-level secrets; tail-keep wrapping active (non-LOCAL); per-cell sampler `base_rate` = the SELF_HOSTED cell. **R-421 (MANAGED_CLOUD):** cloud env + cloud secrets + FULL_VM + managed collector; in-sandbox encrypted-fs secrets per ADR-F5; MANAGED_CLOUD per-cell sampler + redaction posture (`C-OD-13 §13.1`).
- **Current state.** Only LOCAL exercised. **Operator/infra-gated** (`halt-route-to-operator`) — needs operator to provision the server, collector, and secrets backend before any execution.
- **Close-out steps.** (R-420) operator provisions server + collector + secrets → run the daemon e2e with the must_pass set; (R-421, dep R-420) provision cloud env. R-420 **unblocks R-421 + R-430 + R-440**. **`⚖️ Council (R-421 only)`** — MANAGED_CLOUD posture (C8 security ⊥ C11 deployment simplicity) when that arc opens; R-420 is operator-infra, not a design tension.

### B-6 · OTLP tail-keep preservation validation (R-430)
- **What it is.** Verify the `§10.2` classification-trigger preservation semantic against a **real** OTLP collector (the drop/keep decision is collector-side).
- **Current state.** `TailKeepSpanProcessor` buffer logic is in-process + bypassed at LOCAL by design (§9.1 head-based mandate); collector-side preservation is unverified. **This is the surface the OD-3 batch-51 audit reclassified *out* of the OD-3 retirement gate** (production-feature-validation, not an X-AL-2 criterion).
- **Close-out steps.** With a real collector (dep R-420), assert classification-trigger spans survive tail-drop. **Council: no** (validation). Infra-gated.

### B-7 · Tier-level + cloud secrets backend (R-440) `⚖️ council-eligible`
- **What it is.** A real tier-level secrets backend beyond the shipped LOCAL keyring + env-fallback. Per ADR-F5: TIER_1 process-tier = env/keyring snapshot; TIER_3/4 = in-sandbox fresh-fetch over network with a bootstrap token. `C-AS-05 §5.1` `fetch_secret(name, scope, tier)`.
- **Current state.** `provider_secrets.py` (`KeyringSecretResolver`) ships **only LOCAL keyring + env-fallback** (PR #16). Allowlist enforcement + `SecretFetchEvent` audit carrier are live; **MANAGED_CLOUD bootstrap-token protocol is DEFERRED** (prod-tech selection owed). The advanced fail-classes (`SECRET_UNAVAILABLE` breaker / `SECRET_EXPIRED` refresh-and-retry / `SECRET_LOCKED`+`SECRET_REVOKED` HITL) are carrier-declared but their behaviors are deferred.
- **Close-out steps.** (1) Operator selects prod-tech (Vault / AWS Secrets Manager / Azure Key Vault / GCP Secret Manager / Doppler / 1Password Connect) — owed at a deployment-surface D-ADR; (2) implement the tier-specific bootstrap-token protocol + in-sandbox HTTP fetch (TIER_3/4); (3) per-`{backend, scope}` breaker (C9); (4) refresh-and-retry with idempotency-key preservation (SECRET_EXPIRED); (5) HITL composition for LOCKED/REVOKED (C4).
- **`⚖️ Council (C8 ⊥ C11).`** Secrets-backend selection is a security (C8) vs deployment-simplicity/operator-burden (C11) tension; convene when R-440 opens.

---

## Surface VI — Multi-tenant (R-500..R-599, decomposition-owed)

> Per `C-OD-13 §13.1` (redaction toggleability gradient) + `C-OD-10 §10.3` (per-`(persona_tier, deployment_surface)` sampler base-rate, 8-row table) + ADR-D5/D6. Three persona tiers (SOLO_DEVELOPER / TEAM_BINDING / MULTI_TENANT_COMPLIANCE) × three surfaces.

### B-8 · Non-default `tenant_id` / non-SOLO `persona_tier` deployment `⚖️ council-eligible`
- **Current state.** **Fields plumbed:** `RuntimeConfig.tenant_id: str | None = None` + `RuntimeConfig.persona_tier: PersonaTier = SOLO_DEVELOPER` (`types.py`). **Materialized:** per-cell base-rate envelope CLOSED (`materialize_tracer_provider_stage` reads `PER_CELL_BASE_RATE_ENVELOPE[CellID(...)]`, rejects the excluded cell); multi-tenant **non-toggleability ENFORCED** at construction (`MultiTenantOverrideRefusedError` in `RedactionSpanProcessor` when an empty redaction set is supplied at MULTI_TENANT_COMPLIANCE). **Not exercised:** the harness runs SOLO × LOCAL only at MVP; the `PER_PERSONA_TIER_REDACTION` gradient (`redaction_gradient.py`) is present but not driven by a real non-SOLO deployment.
- **Close-out steps.** (1) **Operator:** deploy with non-None `tenant_id` + non-SOLO `persona_tier` at a non-LOCAL surface (gates on R-420/R-421); (2) verify the §10.3 base-rate envelope + §13.1 redaction gradient + multi-tenant non-toggleability behave per spec under real multi-tenant load; (3) multi-tenant audit-ledger separation by `tenant_id`.
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
- **Current state.** Registry + **local-filesystem backend landed** (`MemoryToolFilesystemBackend`); `CP-16` closed RETIRED-AS-BOUNDED-RESIDUAL (batch-44). Cloud-vault / managed-database backends **deferred** (operator-discretion at the managed-cloud arc; the override point `RuntimeConfig.memory_tool_backend_config` already exists).
- **Close-out steps.** (1) New backend class implementing `MemoryToolStorageBackendProtocol` (cloud-vault or managed-db); (2) operator binds it via `memory_tool_backend_config`; (3) e2e exercising read/write/delete across a workflow lifecycle. **Council: no** (impl).

---

## CXA — Cross-axis composition seam completion (B-14)

> **Status spine = the R-700 dispositions verified + merged this session (PR #207), NOT intermediate fork-doc reads.** CXA edge counts per `Cross_Axis_Composition_Document_v2_18.md` §2.3.x. These are mostly **mechanical wiring** (runtime composer landings + production caller sites), not cross-domain design tensions → **Council: no** for all.

| Seam | Disposition (R-700) | Current state | Close-out |
|---|---|---|---|
| **CXA-1** (AS→IS, 13 edges) | **PARTIAL** | `as_is_wiring.py` composer materialized + 7c-tested; **only the secret-fetch-audit edge (U-AS-27→U-IS-11) wired; zero production callers of `emit_secret_fetch_audit_entry`** (the AS secret-fetch driver path is absent at runtime). | Land the AS secret-fetch driver path so the audit composer has a production caller; thread the remaining ~12 AS source-unit audit-emission callbacks through the `AsIsWiring` surface as AS-axis 7b execution proceeds. |
| **CXA-2** (CP→IS, 36–43 edges) | **STILL-BOUNDED** | `cp_is_wiring.py` PARTIAL-LAND (1 of 17 spec §12.3 edges); the U-RT-35 wiring unit landed (batch-46) but the full typed contract stays STILL-BOUNDED; the 6 §16.5 composer methods (`U-CP-74..79`) + their caller-site invocations (`U-RT-110/111`) are the binding chain. | Complete the runtime caller-site invocations threading the 6 composer methods at their firing sites + e2e; remaining ~16 of 17 §12.3 edges (`class_1_tension_u_rt_35_cp_is_wiring_gaps.md`). |
| **CXA-3** (CP→AS, 24 edges) | **STILL-BOUNDED** | **No `lifecycle/cp_as_wiring.py` module** — consistent with spec §12 (no CP→AS runtime stage); typed edges anchored only at the 7c Pattern-P1 import surface. *(NOTE: this is a real open seam — not "N/A". The substrate-consumption relationship is genuine even though there's no composition stage.)* | Per ledger §11.1b: either **(α)** author a CP→AS runtime composer at a Files-arc design-phase opening, or **(β)** operator AskUserQuestion ratifying a Memory-only-scope narrowing of the CXA-3 retirement criterion (parallel to AS-8e/8f indefinite-defer). Neither is in-session-actionable. |
| **CXA-4** (OD→IS/AS/CP, 26 edges) | **PARTIAL** | **Grounding sweep 2026-06-01 (R-CXA-4 grounding-first) corrects the prior "~5 of 26 / ~21 remaining" framing — a stale-carry mis-framing (CLAUDE.md §10.5).** Per CXA §2.5 the 26 canonical OD-outbound edges split **1 genuine typed seam + 19 convention-level + 6 phase-2-runtime**. (1) The lone genuine **data-flow** edge (U-OD-30→U-IS-11 `audit_writer.append`) is **already wired** with 4 real producers (`cost_attribution_{llm,tool,validator,webhook}_dispatch.py:{246,299,238,198}`). (2) The 6 phase-2-runtime edges are **already materialized** at bootstrap stage 6 (`od_is/as/cp_wiring` per runtime spec §12.4–§12.6; `stage_6_cxa_wiring.py:96/104/108`). (3) The 19 convention edges are namespace/manifest/monotonicity alignment satisfied by the stage-6 `verify_*` checks + manifest-resolver; the per-unit OD→AS/OD→CP rows carry **stale `U-AS-NN`/`U-CP-NN` placeholders with no manifest carrier** (the OD aggregate manifest targets only `U-IS-17`/`U-AS-33`/`U-CP-54`/`U-CP-55`). **ZERO unmaterialized edge has a real OD-side producer** — the lone non-wired "genuine" seam U-OD-29→U-AS §12.4 is a halted-leaf symbol-import (FF-3 Class 1 fork), not a data-flow producer. Mirrors the R-CXA-1 producer-discovery outcome (`[[r-cxa-seam-wiring-is-producer-discovery]]`, 3rd instance). | **There is no wiring task** — grounding found **0 wireable edges** (1 genuine already wired; 6 phase-2 already at stage 6). The honest follow-on is a **CXA narrow-scope convention-formalization revision** (delete/remap the stale OD→AS/OD→CP placeholder `U-AS-NN`/`U-CP-NN` rows, mirroring v2.18's C3-15 OD→IS cleanup) — a **design-substrate** arc (posture shift; council-discriminator; spec-writer; clearance marker), a separate operator-owned pick. R-CXA-4 stays PARTIAL; ZERO production code from grounding. |
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

---

## 2. Provenance + method

- **Two tiers per advisor guidance:** Phase-8 *closure residuals* (Tier A — declare Phase 8 done) kept distinct from *post*-Phase-8 forward activation (Tier B); the retirements are **legitimate per X-AL-2** (the H_E scaffold was displaced; production exercise was never an X-AL-2 condition) — this register is the *next axis* of work, not a correction.
- **CXA status spine = the R-700 dispositions** verified against the ledger + merged at PR #207 (CXA-1 PARTIAL / CXA-2 STILL-BOUNDED / CXA-3 STILL-BOUNDED / CXA-4 PARTIAL / CXA-5 RETIRED). Subagent reports supplied close-out *mechanism* detail only — three subagent CXA *status* claims were rejected (CXA-3 "N/A" was a misread; CXA-4 "fully-wired" contradicted R-700 PARTIAL; an "RT-35 PR #52 awaiting merge" claim was stale).
- **Surface IV centerpiece empirically verified this session:** `routing_core_surface.infer()` raises `NotImplementedError` (`:83`/`:97`); `layered_routing_strategy.route()` has zero non-test callers; **but** `retry_breaker_fallback.py` (C-RT-16) *does* implement fallback-chain advancement (the subagent's "fallback not implemented / re-raises" claim was corrected). Accurate framing: provider construction + failure-time fallback wired; capability-aware routing-*selection* stubbed; multi-provider operation **unexercised at MVP**.
- **Council discrimination per CLAUDE.md §13.2 + §10.9:** register-compilation is descriptive synthesis (solo + advisor, not council); 7 forward arcs flagged `⚖️ council-eligible` with named two-voice tensions for when the operator opens them (the roadmap already encodes this on R-410/411/412).
- **Decomposition obligation:** this register discharges the roadmap §9 decomposition owed for Surfaces IV/VI/IX/X and supplies the substance for the `R-NNN` coverage gap (A-3 / B-14) R-700 surfaced.
- Grounded in: ADR-F1/F4/F5 + ADR-D2/D3/D5/D6; CP spec v1.30 `C-CP-01..04`; OD spec v1.27 `C-OD-10/13`; AS spec `C-AS-05/13/15`; runtime spec v1.41 `C-RT-16/22/29` + §14.9.8 + §14.C/D; CXA v2.18 §2.3.x; production source at `harness-{cp,runtime,od,as}/src/`.
