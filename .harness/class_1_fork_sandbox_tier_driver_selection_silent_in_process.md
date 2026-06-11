# Class 1 fork — sandbox tier→driver production selection absent (claimed tier silently executes in-process)

**Status:** ✅ RATIFIED-AS-READING-A+ (deployment-surface-aware default) 2026-06-11 via operator AskUserQuestion. FR-1 (driver-selection binding) + FR-2 (fail-loud, two branches) confirmed forced; DP-1 resolved as **Reading A+** — TIER_1 honest default for `local-development`, fail-safe-high for `managed-cloud`/`self-hosted-server`. Spec §14.9 amendment + bundled-absorption impl owed next (gated on the §7 reconciliation below, added post-ratification).

**Original status (preserved for lineage):** PROPOSING — operator ratification required before the selection-binding spec amendment + impl land.
**Filed:** 2026-06-11, R-CC-1 capability-completion program arc #1 empirical orientation (`.harness/capability-completion-inventory-v1.md` §2 row 1 + §4 step 1).
**Authority anchor:** workspace `CLAUDE.md` §4.3 Class 1 routing + §4.4 X-AL-3 silent-absorption discipline + §11.4 bundled-absorption-arc discipline.
**Posture:** design-phase (this fork doc + a runtime-spec §14.9 amendment) cascading into Phase 7 impl (`harness-runtime/src`) — a §11.4 bundled-absorption arc, gated on the ratification below.
**Grounded at HEAD `8a37665`** (runtime spec v1.42; AS spec v1.6). Every cite below resolved by direct read this session, not recall.
**Discipline applications:** `[[grounding-reveals-claude-closeable-slice-close-honestly]]` (UNSPECIFIED→fork disposition); `[[advisor-before-substantive-work-for-cross-axis-blockers]]` (probe-first foreclosed a council); `[[conformance-validator-disciplines]]` (detect-then-refuse fail-loud).

---

## §1 The gap

The runtime tool dispatcher resolves a per-dispatch sandbox **decision** (tier + tech + provider) but the actual **execution mechanism** is bound once at construction and never varies by the resolved tier. Production binds nothing → it always runs **in-process**, regardless of the claimed tier.

**Code-verified chain (HEAD):**

1. `RuntimeToolDispatcher.__init__(... tool_execution_driver: ToolExecutionDriver | None = None ...)` →
   `self._tool_execution_driver = tool_execution_driver or MCPHostToolExecutionDriver()` at
   `harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py:343`.
   `MCPHostToolExecutionDriver` (`:153`) runs the tool **in-process** via `mcp_client_host.call_tool` (TIER_1 semantics).

2. The stage-5 factory `materialize_runtime_tool_dispatcher_stage` constructs the bare dispatcher at
   `harness-runtime/src/harness_runtime/bootstrap/factories/runtime_tool_dispatcher_factory.py:199-215`
   and **passes no `tool_execution_driver`** → production always gets the in-process default.

3. The factory *does* build a `SandboxDecisionResolver` (`:67-90`, `:188-192`) that returns the per-server
   `default_sandbox_tier / tech / provider` for every dispatch. The dispatcher enforces the tier-**floor**
   (`decision.tier >= contract.minimum_tier`) and emits the `sandbox.*` span attributes from that decision —
   but **nothing maps the resolved tier to the matching execution driver.**

4. The four drivers already exist and are e2e-proven, with no production caller:
   - `MCPHostToolExecutionDriver` — TIER_1 in-process (`runtime_tool_dispatcher.py:153`)
   - `DockerToolRunnerExecutionDriver` — TIER_2 container, R-410 (`docker_tool_execution_driver.py:33`)
   - `GVisorRunscToolRunnerExecutionDriver` — TIER_3 microVM, R-411 (`docker_tool_execution_driver.py:212`)
   - `E2BManagedFullVMToolRunnerExecutionDriver` — TIER_4 full-VM, R-412 (`e2b_tool_execution_driver.py:49`)
   They appear only in unit/integration tests (`test_r41{0,1,2}_*_e2e.py`). `grep` across `harness-*/src`
   confirms zero production construction sites for any of the three sandboxed drivers.

**The lie made concrete (the security-load-bearing finding).** `MCPClientConfig.default_sandbox_tier`
defaults to `SandboxTier.TIER_2_CONTAINER` (`harness-runtime/src/harness_runtime/types.py:568`), and the
field's own docstring states the reason (`types.py:585`):

> *"Default matches `default_minimum_tier`'s default so the floor passes out of the box."*

So the default configuration is engineered to make the tier-**floor check pass** (resolved TIER_2 ≥ required
TIER_2) and to emit `sandbox.tier = "container"` on the span — while execution silently runs **in-process
(TIER_1)**. A tool whose contract demands container-tier isolation receives **none**, and both the floor
gate and the observability surface report success. This is a security/observability falsehood by
construction, not a cosmetic gap.

---

## §2 Probe-first: the 4-tier blast radius is a GUARANTEE, not advisory (this forecloses a council)

Before convening anything, the discriminating probe (`CLAUDE.md` §10.9 probe-first): is the tier posture a
**guarantee** or **best-effort/advisory**? Grep of the AS spec + ADR-F4/D2 prose resolves it as a
**guarantee** — the enforcement language is unambiguous:

- `Spec_Action_Surface_v1.md:863` (STDIO transport floor): *"`tier-3-microvm` minimum regardless of declared
  blast-radius … **Sandbox is the only boundary; container-tier minimum prevents kernel-CVE-class escape into
  host filesystem**."*
- `Spec_Action_Surface_v1.md:819`: *"`code-execution-2025-08-25` beta invoked | Resolves to `tier-4-full-vm`
  (microVM minimum) at any cell; **`sandbox_tier_floor` enforces**."*
- `Spec_Action_Surface_v1.md:818`: tier-4 resolution *"**regardless of nominal blast-radius declaration**."*
- ADR-F4 v1.1 §Decision (per `:346`): a four-tier sandbox-**isolation** tier-set with per-tier capability
  requirements — isolation is the committed property, not a label.

**Consequence:** silent in-process execution under a >TIER_1 claim is a **flat violation** of the F4/D2
guarantee posture. The fail-mode is therefore **forced** — fail-loud, never silently downgrade — and there is
**no live C10⊥C11 tension to convene a council over** (the §13.4 worked-example tension dissolves once the
posture is known to be a guarantee). A dyadic council was considered and **foreclosed by this probe** — the
disciplined §13.3 "don't over-machine" outcome.

---

## §3 Why this is X-AL-3 Class 1 (net-new contract) and not pure impl-discretion wiring

The `ToolExecutionDriver` Protocol + `tool_execution_driver` parameter are a **cleared impl-discretion seam**
(the dispatcher docstring `:130-138` states container/microVM/full-VM drivers "can replace that mechanism
without changing the dispatcher surface"). But three surfaces are genuinely **net-new** and unspecified in the
cleared corpus:

1. **The factory's driver-selection obligation.** Runtime spec **§14.9.8** (v1.41, the NEW sandbox-decision-
   resolver contract) specifies that the factory MUST build a resolver returning the per-server decision, and
   that the dispatcher enforces the tier-floor. It says **nothing** about binding the execution **driver** to
   the resolved tier. Making the existing guarantee TRUE requires a new factory obligation → spec surface.

2. **The fail-mode contract.** "Tier claimed but no driver can deliver it" has no specified behavior today
   (the code silently delivers in-process). The forced resolution (fail-loud) must be written into the spec.

3. **Per-server driver-config.** A `DockerToolRunnerExecutionDriver` cannot be instantiated from the existing
   `tier/tech/provider` strings — it needs `image` + `command` (`docker_tool_execution_driver.py:41-58`); E2B
   needs a template/command + an API key (`e2b_tool_execution_driver.py`). These config fields do not exist on
   `MCPClientConfig` today. (`MCPClientConfig` is impl-declared — the spec refers to it opaquely per the v1.40
   convention — so the *fields* are impl-discretion, but the *requirement that they exist* is part of the
   selection contract.)

Per `[[grounding-reveals-claude-closeable-slice-close-honestly]]`: UNSPECIFIED surface → **fork, don't
silently absorb**. Landing the selection-binding without ratification would be the exact X-AL-3 silent-design-
extension failure mode (§4.4).

---

## §4 The resolution (one forced posture + one genuine decision)

### §4.1 Forced by the guarantee posture (not a decision — record only)

**FR-1 Driver-selection binding (factory-level, per-server-uniform).** The stage-5 factory MUST select the
`tool_execution_driver` matching the resolved per-server `default_sandbox_tier` (+ `tech` for the
TIER_3 gVisor-vs-plain-container discriminant) from a **selection registry**, and pass it to
`RuntimeToolDispatcher(...)`. Per-server-uniform — matching §14.9.8's per-server-uniform resolver granularity;
per-tool/per-dispatch driver selection is explicitly **future** (not built — §2 no-speculative).

**FR-2 Fail-loud, two branches** (`[[conformance-validator-disciplines]]` detect-then-refuse):
- **(i) selection-time / bootstrap:** if the resolved tier is > TIER_1 and no driver is registered/configurable
  for it, the factory **RAISES at bootstrap** (a clear, actionable error). It MUST NOT fall through to the
  in-process driver. *This is the branch that is broken today.*
- **(ii) dispatch-time:** if a driver is selected but its substrate is absent at call-time (Docker daemon down,
  E2B key/template missing), the dispatch **RAISES** (already the case — the Docker driver shells `docker run`
  at call-time and maps a non-zero exit to `ToolInvocationProtocolError`; it also self-guards
  `decision.tier is required_tier`). No silent in-process fallback at this branch either.

TIER_1_PROCESS resolves to the existing `MCPHostToolExecutionDriver` (honest in-process, no substrate needed).

### §4.2 The one genuine operator decision — the bare/default-config posture (DP-1)

The only real fork is **what a bare config does** once fail-loud is in place. Today `default_sandbox_tier =
TIER_2_CONTAINER` exists *specifically* to pass the floor out-of-box — which under FR-1/FR-2 would now make
**every bare config raise at bootstrap** (no Docker driver wired). Two readings:

- **Reading A — honest TIER_1 default (RECOMMENDED).** Change the `MCPClientConfig` defaults to
  `default_sandbox_tier = TIER_1_PROCESS`, `default_sandbox_tech = "host-process"`, `default_sandbox_provider
  = "host"`. A bare config then **honestly** runs in-process labeled TIER_1 (no lie, no error). Operators opt
  **up** to TIER_2+ by declaring the tier **and** a driver config; FR-2(i) fail-loud fires only on an explicit
  >TIER_1 claim without a driver. Lowest config burden; honest-by-default; matches local-development as a
  first-class deployment surface (ADR-D2) and the bridging-arc solo-developer design-time default
  (`Persona_Document_v1.md` §2.1). **Trade:** a bare config is unsandboxed — but it is *honestly labeled*
  unsandboxed, and the operator opts into isolation, which is the truthful posture.
- **Reading B — fail-safe-high default.** Keep `default_sandbox_tier = TIER_2_CONTAINER` (or raise toward the
  AS spec's recommended tier-4 posture, `Spec_Action_Surface_v1.md:503`). A bare config then **raises at
  bootstrap** with an actionable message ("`default_sandbox_tier=TIER_2_CONTAINER` requires a Docker driver;
  configure one or set `default_sandbox_tier=TIER_1_PROCESS`"). Security-default-high; higher config burden on
  every local-dev run. **Trade:** safest default, but every out-of-box run must make a choice before it works.

A deployment-surface-aware default (TIER_1 honest for local-development, fail-safe-high for managed-cloud/
multi-tenant) is a possible **Reading A+** but adds design surface; flagged, not recommended for this arc.

**Recommendation: Reading A.** It removes the lie (the load-bearing fix is FR-1/FR-2, identical under both
readings) *and* makes the default truthful with minimal burden. The AS spec's tier-4 recommendation is
explicitly a *recommendation* about the tool-contract default-tier ("specific commitment is a tool-registry
D-ADR", `:503`), not a binding commitment on the per-server resolved sandbox tier — so Reading A does not
override a committed surface.

> **SUPERSEDED 2026-06-11:** the operator ratified **Reading A+** (deployment-surface-aware), not the
> Reading-A recommendation above — `local-development → TIER_1_PROCESS` honest default; `self-hosted-server`
> / `managed-cloud → TIER_2_CONTAINER` fail-safe-high. §4.2/§6 are preserved as the **pre-ratification
> record**; the **realized decision is §7** (which floor-verifies A+ as safe). Cite §7 / the §Status header
> for the ratified posture, not this §4.2 recommendation.

---

## §5 Downstream impact (post-ratification — NOT landed in this fork PR)

| Site | Amendment shape | Trigger |
|---|---|---|
| **Runtime spec §14.9 (NEW §14.9.9 or §14.9.8 extension)** | Author the factory **driver-selection obligation** (FR-1) + the **fail-loud two-branch contract** (FR-2). Per-server-uniform; per-tool future. Cites the F4/D2 guarantee posture (§2) as the forcing authority. | Ratification of FR-1/FR-2 |
| **`MCPClientConfig` (`types.py`)** | NEW per-server driver-config fields (Docker `image`/`command`; E2B template/command; secret-ref for the E2B key). Impl-declared (spec opaque). Under Reading A, also flip the three `default_sandbox_*` defaults to the TIER_1 honest set. | Ratification of DP-1 |
| **`runtime_tool_dispatcher_factory.py`** | Build a tier(+tech)→driver **selection registry**; select + pass `tool_execution_driver=`; FR-2(i) raise on >TIER_1-without-driver. Removes the dangling `_ = sandbox_decision_policy` no-op (`:165`) by giving the policy a consumer. | Ratification |
| **Tests** | A contrasting-baseline test proving FR-2(i) RAISES (not silently in-process) when TIER_2 is claimed with no driver — the `[[conformance-validator-disciplines]]` discriminating-power test. Plus a factory test proving TIER_2 config selects the Docker driver. | Ratification |
| **Clearance marker** | `.harness/clearance/Spec_Harness_Runtime-v1_43-cleared-YYYY-MM-DD.md` pinning the §14.9 amendment + this fork's ratification (§4.5). | At amendment merge |

**Substrate-clearance note (advisor pre-check).** R-410/411/412 have **no clearance markers** —
expected, because they are Phase 7 *impl* arcs (drivers in `harness-runtime/src`), not `design-substrate`
amendments; clearance markers bind design-substrate artifact versions only. The driver substrate is
**e2e-proven** (`test_r41{0,1,2}_*_tool_execution_e2e.py`), which is the relevant "cleared, not just merged"
evidence for building selection on top of it.

---

## §6 The single batched operator gate

Per `CLAUDE.md` §4.3 Class 1 routing, this halts arc #1 impl and routes one decision to the operator:

- **DP-1 — bare/default-config posture:** Reading A (honest TIER_1 default; **recommended**) vs Reading B
  (fail-safe-high default that raises out-of-box). FR-1 (driver-selection binding) and FR-2 (fail-loud,
  no silent in-process) are **forced by the guarantee posture** and land under either reading — they are
  recorded for ratification, not offered as a choice.

On ratification: spec-writer authors the §14.9 amendment → implementation-planner/impl wires the factory
registry + config fields + contrasting-baseline tests → adversarial review (pre-merge, §10.9) → clearance
marker → bundled-absorption PR. **No impl lands before this gate** (X-AL-3).

---

## §7 Post-ratification reconciliation — Reading A+ realization vs C-AS-09 (floor-verified)

Ratified Reading A+ (deployment-surface-aware default) surfaced a primary-source reconciliation question
(advisor-flagged): the AS spec **C-AS-09 §9.1 / ADR-D2 §1.1** already specify a (deployment-surface ×
blast-radius) → tier matrix. Does a surface-keyed default collide with it?

**Discriminator: are the matrix cells raise-only FLOORS or EXACT assignments?** Verified at ADR-D2 §1.1/§1.3/
§1.6 (HEAD, direct read) → **FLOORS**:
- Tier = `max(contract.minimum_tier, blast_radius_floor, mcp_server_trust_tier_floor, operator_policy_floor)`
  per call site (ADR-D2 §Decision / `ADR-D2.md:49`) — a max-of-floors.
- §1.3: "Tier 3 container **minimum** regardless of declared blast-radius"; "sandbox-tier **follows**
  blast-radius" (`ADR-D2.md:111`).
- §1.6 cross-deployment **monotonicity**; §1.1 forcing-conditions only raise ("MUST resolve to Tier 4 microVM
  **minimum**", `:88`); §1.1 operator-policy override of the cell default is permitted (`:84`).

**Consequence — no collision; Reading A+ is safe and consistent with C-AS-09:**
- `local-development → TIER_1_PROCESS` default is **literally** the matrix's `local-development × read-only =
  tier-1-process` floor — not below any cell.
- `self-hosted-server` / `managed-cloud → fail-safe-high` only ever **raises** the default above the read-only
  floor — always safe (you may be stricter than a floor, never looser).
- The **tier-floor check is the safety net**: a low surface default + a tool whose `minimum_tier` exceeds it →
  `SandboxTierFloorViolationError` (fail-loud), so a low default never *silently* under-sandboxes
  (`[[conformance-validator-disciplines]]` detect-then-refuse).
- → **No ADR-D2 back-flow. No operator re-contact** (re-litigating a floor-safe choice is approval-fatigue).

**Scope of the "consistent with C-AS-09" claim (adversarial-review F2-01 refinement).** The "safe and consistent" claim above covers the ADR-D2 **§1.1 cell-floor only**. ADR-D2 commits a **second, independent floor at §1.3** — STDIO transports get a `tier-3-microvm` minimum "regardless of declared blast-radius" (`ADR-D2.md:108`), composed via the full `sandbox_tier_floor` (C-AS-02 §2.2). The §14.9.8 flat per-server-uniform MVP resolver this arc consumes does NOT apply that transport-floor, so a bare STDIO local-development server resolves to `TIER_1_PROCESS`, below the §1.3 floor. This is the **pre-existing §14.9.8 composition gap** (carried forward, not introduced here) — the same gap the §7 "Scope boundary" above carves out as a distinct future arc. v1.43 neither closes nor widens it; the `resolved.tier >= contract.minimum_tier` safety net still fires whenever a tool's `minimum_tier` is declared above the resolved tier. The "consistent with C-AS-09" claim is therefore precise about §1.1 and explicit that §1.3 (+ the full composition) is the deferred arc.

**Scope boundary (held hard, advisor-confirmed).** FR-1/FR-2 are "given a resolved tier, select the matching
driver or fail loud" — *independent of how the tier is derived*. A separate, deeper gap exists: the §14.9.8
resolver is a flat per-server-uniform MVP (Reading B) that **bypasses** the full `sandbox_tier_floor`
composition (it returns `default_sandbox_tier`, not the per-cell `max(...)`). **That composition gap is NOT
absorbed here** — it is a distinct future arc. This fork consumes whatever tier the existing resolver emits.

### §7.1 Realized Reading A+ default-policy (impl-discretion — recorded here, NOT new spec contract)

The deployment-surface-aware default is a **factory-level default policy**, not a static `MCPClientConfig`
field default (the surface is only known at `RuntimeConfig.deployment_surface`, available to the stage-5
factory). Realization:

- `MCPClientConfig.default_sandbox_tier` (+ `default_sandbox_tech`, `default_sandbox_provider`) → `| None`
  with `None` = "derive from `config.deployment_surface` at the factory." An explicit operator value overrides.
- Factory default policy when `None`:
  - `local-development` → `TIER_1_PROCESS` / `host-process` / `host` (honest in-process; `MCPHost` driver
    needs no substrate → runs out-of-box).
  - `self-hosted-server`, `managed-cloud` → `TIER_2_CONTAINER` default → FR-2(i) **fail-loud at bootstrap** if
    no driver configured (forces explicit isolation for production surfaces = the operator's "fail-safe-high").

**Three-field coherence reconciliation (advisor's catch).** Today `default_blast_radius = READ_ONLY` (→ tier-1
per C-AS-09) but `default_sandbox_tier = default_minimum_tier = TIER_2_CONTAINER` — mutually incoherent (the
TIER_2 was chosen to "make the floor pass", not derived; `types.py:585`). Reconcile **all three together** under
the surface-keyed policy: at `local-development`, `default_sandbox_tier` and `default_minimum_tier` resolve to
`TIER_1_PROCESS` — coherent with the `READ_ONLY` blast default. Do not flip one field and leave the
contradiction.

### §7.2 Spec-delta scope (kept minimal)

The runtime §14.9 amendment authors ONLY FR-1 (factory driver-selection obligation) + FR-2 (fail-loud
two-branch contract). The `default_*` **values** + the surface-keyed default policy + the three-field
reconciliation are `MCPClientConfig` impl-discretion (the spec refers to it opaquely per the v1.40 convention)
— recorded in this fork doc, not authored as new spec contract.
