# Class 1 fork — resolved sandbox tier is never enforced: no execution-driver contract (tier → isolation mechanism)

**Status:** PROPOSING (filed 2026-06-02). Deferred-far; routes to design-phase. **No AskUserQuestion fired** — resolving the Reading now unblocks nothing buildable (the e2e close co-gates on a real container runtime = R-410 infra). This fork *characterizes and tracks* the gap so it is teed up when Surface-V infra opens; it does not unblock buildable Claude work.
**Filed:** 2026-06-02, grounding the highest-value un-blocked forward item (R-410) per the no-parking directive (CLAUDE.md §12.4.1). Empirical orientation + advisor (R-410 `advisor_required: yes`) confirmed the gap is real, distinct from the two applied sibling forks, and that *building* a driver would violate X-AL-3 → **filing is the X-AL-3-clean slice.**
**Class:** 1 (architectural — the H_T sandbox-tier model promises graduated isolation (ADR-F4 / ADR-D2), but at HEAD a resolved tier maps to NO execution mechanism; closing it requires a NEW design contract for the tier→mechanism execution driver, which is a design-phase artifact, not a Phase-7 impl decision).
**Blocks:** `R-410-sandbox-tier-2-container-execution` (the design half — orthogonal to R-410's infra gate). Also the design root of `R-411-sandbox-tier-3-microvm-execution` + `R-412-sandbox-tier-4-full-vm-execution` (they inherit the same execution-driver question; **this is a one-time fork, not a fork-per-tier** — once the driver contract lands, R-411/R-412 are provider-class additions, not new forks).
**Sibling of (distinct from):**
- `.harness/class_1_fork_tool_step_no_bootstrap_sandbox_decision_resolver.md` (✅ APPLIED-AS-READING-B, spec v1.41 §14.9.8) — wires the *resolver* (decides a tier + builds a per-server default). This fork is about what happens *after* a tier is decided.
- `.harness/class_1_fork_sandbox_decision_policy_phantom_cite.md` (✅ APPLIED) — re-homes the empty-marker `SandboxDecisionPolicy` carrier. Unrelated to execution.

Neither sibling specifies how a resolved tier becomes real isolation. That contract has **no spec anchor anywhere**.

---

## 1. The divergence

The H_T design commits to **graduated-isolation sandboxing** — a 4-tier blast-radius ladder (ADR-F4 v1.1; ADR-D2 v1.2 per-deployment-surface provider classes; `deployment_matrix.py` 12-cell tier×surface map). The runtime resolves a `SandboxDispatchDecision` per dispatch and enforces a tier-*floor*. But **the resolved tier is never used to change how the tool actually executes.** Every TOOL_STEP runs in-process through the same FastMCP session regardless of whether the resolver returned `TIER_2_CONTAINER`, `TIER_3_MICROVM`, or `TIER_4_FULL_VM`.

The tier/tech/provider are **observability + policy-floor annotations only.** There is no execution-driver contract: the spec is silent on how a resolved tier maps to an actual sandbox mechanism (container / microVM / VM).

## 2. Evidence (code-level, conclusive — verified at HEAD `501acfc`)

1. **The resolved decision drives only (a) a floor check and (b) span attributes.** `harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py:452` — `sandbox_decision = self._sandbox_resolver(contract, step)`; `:454` — `if _SANDBOX_TIER_RANK[sandbox_decision.tier] < _SANDBOX_TIER_RANK[contract.minimum_tier]: raise SandboxTierFloorViolationError(...)` (floor, not mechanism); `:475`/`:477` — `_set(sandbox_enter_span, ATTR_SANDBOX_TIER, sandbox_decision.tier.value)` + `ATTR_SANDBOX_PROVIDER` (span metadata). After that the decision is read once more at `:617` for the result dict (`"sandbox_tier": sandbox_decision.tier.value`).

2. **Execution is tier-independent.** `runtime_tool_dispatcher.py:519` — `response = await self._mcp_client_host.call_tool(...)`, which delegates to `mcp_client_host.py:393 call_tool` → `await self._session.call_tool(name, merged_args)` — the **in-process MCP session**, with **no branch on `sandbox_decision.tier` / `.provider` / `.tech`** anywhere on the path.

3. **No isolation machinery exists.** `grep -ni "container|microvm|firecracker|gvisor|isolat"` over `runtime_tool_dispatcher.py` returns exactly 2 non-execution hits — the `tech`/`provider` field docstrings (`:91`/`:92`, *examples* of strings the metadata could hold: "docker" / "firecracker" / "container-d" / "fly-machines") and the `_SANDBOX_TIER_RANK` enum→int map (`:198`/`:199`, for the floor comparison). `mcp_client_host.py` returns 0. The strings are pure telemetry; nothing reads them to dispatch differently.

4. **The spec authorizes the *decision*, never the *enforcement*.** Runtime spec v1.41 §14.9.8 (the only spec anchor for the sandbox surface) authors the `SandboxDispatchDecision` carrier + `SandboxDecisionResolver` callable + the factory's obligation to build a per-server default-policy resolver. It explicitly scopes itself: "Tier-floor interaction is LIVE under Reading B. Per-server-uniform (per-tool granularity is future)." It is **silent on tier→mechanism execution.** `SandboxDispatchDecision` carries a `provider` and `tech` string, but no contract says what a non-`host` provider *does*.

So: the harness can *decide* a tier, *refuse* under-tier dispatch, and *report* the tier in telemetry — but it cannot *enforce* isolation. A `TIER_4_FULL_VM` resolution and a `TIER_1` resolution execute identically.

## 3. The decision (routes to design-phase)

This is a genuine H_T design surface that does not yet exist (X-AL-3: it must NOT be silently built at Phase-7 — defining the execution-driver contract by writing a `SandboxExecutionProvider` Protocol + wiring would be exactly the silent-design-extension failure mode). Enumerated Readings for the design-phase resolution arc:

- **Reading A — tier→provider-class registry (thin).** A declarative map `(SandboxTier, DeploymentSurface) → ExecutionProviderClass` (mirrors the existing `deployment_matrix.py` 12-cell shape), where each provider class is a small adapter wrapping `call_tool` in a mechanism (in-process / container / microVM / VM). Minimal new contract surface; the dispatcher gains one branch (`provider_class.execute(call_tool, decision)`).
- **Reading B — per-mechanism execution-driver Protocol (full).** A `SandboxExecutionDriver` Protocol with one impl per mechanism, selected by `decision.provider` / `decision.tech`, owning the full lifecycle (provision → execute → teardown) + the `sandbox.enter`/`sandbox.exit` span emission currently inline in the dispatcher. Heavier; cleanly separates policy (resolver) from mechanism (driver).
- **Reading C — defer indefinitely (bounded-residual).** Ratify that LOCAL_DEVELOPMENT MVP runs everything in-process by design (ADR-D2 graduated-isolation is a deployment-surface concern), and the execution driver is authored only when a real non-LOCAL surface (R-420/R-421) is provisioned. The tier model stays observability+floor-only at MVP, documented as a bounded residual per X-AL-2 §5.3.

**The C10 ⊥ C11 tension (council-eligible at the resolution arc).** This is the workspace's named sandbox-floor tension (CLAUDE.md §13.4 "the council that was missed"):
- **C10 (action-safety / blast-radius)** wants real isolation enforced — a resolved tier that doesn't change execution is a *safety annotation that lies*; the floor check gives false assurance (it refuses under-tier dispatch but the over-tier dispatch it permits runs with zero isolation).
- **C11 (operator-loop / local-deployment)** wants minimal provisioning burden — a solo developer at LOCAL_DEVELOPMENT should not need a container runtime to run a workflow; in-process execution is the correct MVP default, and Reading C (defer) honors that.

These do not resolve against each other from inside the spec — the resolution arc should convene a dyadic C10⊥C11 council before the operator picks A/B/C. **Recommended posture: Reading C (defer-and-document) is the honest MVP end-state**; A/B land when Surface-V infra opens. Filing this fork does not pre-judge that — it crystallizes the gap and the Readings.

## 4. Why now / why not more

- **Why file:** R-410 is the *only* forward roadmap item that is both un-blocked (`depends_on: []`) and has an un-built Claude slice; its own notes predict "Almost certainly opens a Class 1 fork: the execution-driver contract ... is unspecified." This fork is that predicted slice — and the design-fork is **orthogonal to R-410's container-runtime infra gate**, so it advances the item without needing infra. (PR #254 lumped R-410 into "infra-gated" and missed the separable design slice.)
- **Why not build:** the execution driver is an unspecified H_T contract → building it at Phase-7 = X-AL-3 silent design extension (I-2). The fork is the X-AL-3-clean response.
- **Why no AskUserQuestion:** the e2e close co-gates on real infra; resolving A/B/C now unblocks nothing buildable → forcing a decision is approval fatigue. "Default to doing + reporting" (§12.4.1). The fork sits PROPOSING until Surface-V infra opens or the operator elects to resolve the Reading early.
- **PR scope:** `.harness/`-only (this fork) + a roadmap note pointer + dashboard refresh. **No `design-substrate/**` edit, no `src/` change** → X-AL-3 guard trivially satisfied.

---

## 5. Routing

| Field | Value |
|---|---|
| Fork class | 1 (design-phase artifact required: NEW execution-driver contract) |
| Routing target | Design-phase — runtime spec §14.9.x execution-driver authoring (+ possible ADR-D2/F4 cross-ref) at the R-410 resolution arc |
| Resolution arc | `R-410-sandbox-tier-2-container-execution` (co-gates on a real container runtime for the e2e close; the design half resolves here) |
| Council | C10 ⊥ C11 dyadic, eligible at the resolution arc (not now) |
| Blocks (buildable work) | none at MVP — bounded-residual per Reading C is the honest MVP end-state |
| Re-opens / advances when | Surface-V infra (R-420 SELF_HOSTED_SERVER) opens, OR the operator elects to author the driver contract early |
