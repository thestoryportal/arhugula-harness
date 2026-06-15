Design — R-FS-1 sub-program B2: Multi-server MCP client

*Mode-agnostic design leg (authors only `.harness/` files; X-AL-3-clean). The fork doc + the actual `design-substrate/**` amendments are the NEXT (B2-spec) leg's PR, after operator ratification. Precedent: B1-DESIGN (`r-fs-1-b1-topology-orchestration-design-v1.md`, #527) + B3-DESIGN (`r-fs-1-b3-smart-hitl-design-v1.md`, #549) + R-PM-1 design (#505). Grounded at HEAD `c0fc9f3`.*

---

## §0 What B2 is, and what this PR is

**B2 = multi-server MCP client.** Today the harness is single-server: the bootstrap materializes exactly ONE `MCPClientHost` from `config.mcp_clients[0]`, and the dispatcher is hardwired to that one host. B2 lifts the harness to N concurrent MCP servers — discover tools across N hosts, route each `TOOL_STEP` to the owning host, and gate per-server trust against the resolved host.

**This PR (B2-DESIGN) authors only this design doc + the filed adversarial review.** It changes NO `design-substrate/**` and NO `harness-*/src/**`. It exists to (a) ground the current single-server surface byte-exactly, (b) decide the fork sub-decisions (with recommendations), (c) enumerate the spec-amendment surface the B2-spec leg owes, (d) classify the X-AL-3 posture, (e) make the B2↔B6 seam call, and (f) surface the genuine operator inputs (batched — the substantive one being the gate-axis trust-mapping direction, §6/§9) so the B2-spec leg can open cleanly.

**Why a fork is owed (the X-AL-3 gate, stated up front).** The cleared runtime spec commits `HarnessContext.mcp_client_host: MCPClientHost` — a **singular** field — and a stage-3a factory contract `materialize_mcp_client_host_stage(config) → MCPClientHost` that returns ONE host. Multi-server CANNOT be built without amending those contracts (singular → mapping) plus defining a tool→server routing contract. That is new contract/field/semantics not in the cleared spec ⇒ **X-AL-3 territory** ⇒ halt + Class 1 back-flow before any impl. This design leg is the pre-fork analysis; it does not itself extend H_T.

---

## §1 Grounding (current state at HEAD `c0fc9f3`)

All facts below are body-verified this session (not recalled; the #550 grounding-sweep dossier was frozen at HEAD `3835408e` and its *spec line numbers* drifted after B3+E landed — re-resolved here by §-anchor; the *code carrier* lines still hold).

**The singular contract surface (the hard gate):**
- `Spec_Harness_Runtime_v1.md` §14.9.1 dispatch body — every dispatch reads `ctx.mcp_client_host` (singular): step 1 resolves `ToolContract` from `ctx.mcp_client_host.tool_registry`; step 2 gates trust via `ctx.per_server_trust_evaluator.evaluate(...)`; step 7 invokes `ctx.mcp_client_host.call_tool(...)`.
- `Spec_Harness_Runtime_v1.md` §14.9.3 stage-3a — `materialize_mcp_client_host_stage(config: RuntimeConfig) → MCPClientHost` (singular return); ingests `config.mcp_clients: list[MCPClientConfig]` (already plural) but instantiates ONE host; binds to `ctx.mcp_client_host`.
- `Spec_Harness_Runtime_v1.md` §14.9.6 inv 1 — "MCP host instance started exactly once per bootstrap. Stage 3a starts; stage 7 SHUTDOWN drains… one subprocess per `MCPClientHost`; HTTP transport opens one client connection pool per host…". The "per host" lifecycle language *implies* N hosts, but the singular field + singular factory realize exactly one. (The #550 dossier paraphrased this as "operator materializes N instances" — imprecise; the actual text is per-host lifecycle, contract-pinned to one.) Same invariant: "Idempotent restart out of scope at v1 (deferred to operator-driven restart arc)" — the Part-2 minor (§2 D5).

**What is built + production-wired (single-server):**
- `lifecycle/mcp_client_host.py` — `MCPClientHost` implements all 3 transports (stdio / streamable_http / sse) with real `start` / `health_check` / `shutdown` / `call_tool` bodies. `start` REFUSES idempotent restart (`MCPHostAlreadyStartedError`).
- `bootstrap/factories/mcp_client_host_factory.py:173` — `entry = config.mcp_clients[0]` (single-server consumption); `:197` — `_trust_tier_from_level` always returns `LEVEL_0_REFUSE_REMOTE` (the trust stub, see §2 D3).
- `lifecycle/runtime_tool_dispatcher.py` — hardwired to ONE host: reads `self._mcp_client_host.tool_registry.get` (`:617`), `self._mcp_client_host.server_name` (`:624/:718`), `self._trust_evaluator.evaluate(self._mcp_client_host.server_name)` (`:628`). (Canonical dispatcher cite-set `:617/:624/:628/:718`, used consistently below.)
- `bootstrap/factories/runtime_tool_dispatcher_factory.py:269/:281` — builds the sandbox resolver/driver from `config.mcp_clients[0]` (the single-server consumption shared with B6).
- `bootstrap/stage_3a_cp_clients.py:60-71` — materializes the single host and starts it if `config.mcp_clients` non-empty.
- Production caller chain (REAL, not dormant): `api.run` → `run_bootstrap` → bootstrap orchestrator wires `(CP_CLIENTS, stage_3a_cp_clients)` + `(LOOP_INIT, stage_5_loop_init)`. A `TOOL_STEP` reaches `RuntimeToolDispatcher.dispatch` → trust gate → single-host `tool_registry`.

**What is built + multi-server-READY (only ever called with one server today):**
- `harness-cp/src/harness_cp/per_server_trust_evaluator.py` — `PerServerTrustEvaluator.evaluate(server_name, …)` is keyed on `server_name`, with deny-wins / allow-list / per-server-override / tier-floor branches + an unknown-server CONSERVATIVE=MIN refuse-default (`_default_tier_resolver` → `LEVEL_0_REFUSE_REMOTE`, `:88/:102-115`). Multi-server-ready by construction; only called with one `server_name` because only one host exists.
- `harness-as/.../sandbox_tier_floor.py:115-155` — the per-transport sandbox-tier FLOOR is live + non-vacuous (STDIO → `max(TIER_3_MICROVM, floor)`; remote L0 → `REFUSE`; remote L2 → `max(TIER_4_FULL_VM, floor)`; L1/L3 → `floor`). Transport severity is priced in HERE, independent of the trust tier.

**Config is already plural:**
- `harness-runtime/.../types.py:1242` — `RuntimeConfig.mcp_clients: list[MCPClientConfig]`.
- `:574-613` — `MCPClientConfig` carries per-server `client_name: ClientName` (the config key), `transport: MCPTransport`, `trust_level: MCPServerTrustLevel` (REQUIRED, no default), `blast_radius`, `connection_url`, `default_minimum_tier`, `default_sandbox_*`. Every per-server field needed for N servers already exists.
- `:1650` — `HarnessContext.mcp_clients: dict[ClientName, MCPClient]` already exists as a dict keyed on `ClientName` (precedent for the reshape key).

**Net:** config is plural; per-server trust + per-transport floor are multi-server-ready; the THREE genuinely-unbuilt pieces are (1) the singular `mcp_client_host` field + singular factory (materialization), (2) cross-host tool discovery (a unified routing index), (3) the dispatcher's tool→server routing. Plus the vacuous trust-projection stub (a placeholder this arc retires) and ~10 downstream `ctx.mcp_client_host` consumers needing the field reshape.

---

## §2 The fork sub-decisions (recommended; operator ratifies at the B2-spec leg)

Five sub-decisions. Four are Claude-decided with a recommendation (reversible; sensible default per §12.4.1 — surfaced, not gated). One (D3, the trust projection) was resolved by a genuine dyadic council (§6). NONE is a contested operator-posture choice; the operator's role is to ratify the bundle when the B2-spec Class 1 fork opens.

### D1 — `C-RT-04` reshape type → `dict[ServerName, MCPClientHost]`
**Recommendation:** reshape `HarnessContext.mcp_client_host: MCPClientHost` → `mcp_client_hosts: dict[ServerName, MCPClientHost]`. **Key = the host's `server_name`** (the per-deployment registry ID already carried on `MCPHostHealth.server_name` and read by the dispatcher at `:624/:718`), NOT `client_name`. Rationale: routing resolves a tool to its OWNING server, and the trust gate + spans key on `server_name` throughout — keying the host map on `server_name` keeps one identity for routing+trust+telemetry. `HarnessContext.mcp_clients: dict[ClientName, MCPClient]` (the config-level map) already establishes the dict-of-hosts shape; B2 adds a sibling dict for the *started* hosts. **Why not `list[MCPClientHost]`:** routing needs O(1) host lookup by identity; a list forces a linear scan + an implicit index. **Current-state honesty (per adversarial review F1-01):** at HEAD the factory sets `server_name=entry.client_name` (`mcp_client_host_factory.py:177`) — so `server_name` and `client_name` are the *same value today*; the key choice is defensible because routing + trust + spans all read `server_name`, but the "keep config-key and runtime-identity distinct" framing is a **forward property** a thin `ServerName` alias would preserve, not a present-state distinction. **Sub-decision flagged for the spec leg:** confirm `ServerName` is a `NewType`/alias over `str` (the `server_name` registry ID) vs reusing `ClientName`. *Reversible; default committed.*

### D2 — discovery/registry + routing shape → per-host registries + a bootstrap-built routing index; fail-loud on tool-name collision
**Recommendation:** keep each host's own `list_tools`-populated `tool_registry` (per-host, already built); at stage-3a/stage-5 materialization, aggregate a **routing index** `dict[ToolId, ServerName]` mapping each discovered tool to its owning host. The dispatcher resolves `step.tool_id` → owning `server_name` via the index, then dispatches to `hosts[server_name]`. **Collision policy: fail-loud at bootstrap.** A `tool_id` advertised by ≥2 servers raises a permanent startup fail-class (`RT-FAIL-MCP-TOOL-NAME-COLLISION`, new) → bootstrap aborts. Rationale: honors the workspace's detect-then-refuse / loud-on-misconfig discipline (the §14.9.9 FR-2 + U-CP-68/69 posture); keeps routing deterministic and the contract minimal at MVP. **Future extension (NOT this arc):** server-qualified addressing (`server_name/tool_id`) to permit deliberate same-name tools — register as a forward item, do not silently foreclose. *Reversible; default committed; collision-policy flagged for ratification (it's the one place a deployment could legitimately want server-qualified instead of fail-loud).*

### D3 — AS-`MCPServerTrustLevel` → CP-`MCPTrustTier` projection → **identity-by-ordinal** (retire the over-gating stub)
**Council-resolved (C10 ⊥ C11, dyadic, probe-resolved — §6).** Make the projection a faithful 1:1 ordinal map (`L0→LEVEL_0` … `L3→LEVEL_3`), retiring the current stub that constant-collapses to `LEVEL_0_REFUSE_REMOTE`. The two enums are the *same closed 4-value set* (CP `MCPTrustTier` docstring: "byte-exact factor-out of the AS-owned value set" at C-AS-10 §10.3), so identity is the unique faithful realization. **No transport-aware clamp inside the projection** — transport severity is already owned by the per-transport sandbox floor (`sandbox_tier_floor.py:141-152`, verified live), and a clamp would require widening `_trust_tier_from_level`'s signature to re-take `mcp_transport` (a one-source-of-truth violation; the narrow `level`-only signature is positive evidence transport belongs to the floor). The unknown/undeclared-server case is already refuse-defaulted at the evaluator's `_default_tier_resolver`. **Where it lives:** CP-side (the trust-framework function lives in CP per `harness-as/CLAUDE.md` §1.4; AS declares the per-transport floor only).

**Blast-radius of the stub — corrected per the filed adversarial review F2-01/F2-02 (consumer-chain traced + verified at HEAD).** The projection output `host.trust_tier` is **telemetry-only today**: it is read solely at `runtime_tool_dispatcher_factory.py:184` (into `MCPServerInfo`) → `MCPClientNamespaceEmitter` → the `mcp.server.trust_tier` **span attribute** (docstring at `mcp_client_host.py:130` says so verbatim). The dispatch trust *gate* (`runtime_tool_dispatcher.py:628`) calls `evaluate(server_name, …)` keyed on `server_name` via `TrustPolicy` and **never reads `host.trust_tier`** (zero `trust_tier`/`gate_level`/`mcp_trust` reads in the dispatcher). And the locked T-perm-1 **gate** axis `mcp_trust_tier` (`per_tool_gate_level × per_mcp_server_trust_tier × persona_tier × blast_radius_tier × sandbox_tier`, ADR-D2 §1.5 / `:69`) is fed by a **separate hardcoded constant** `mcp_trust_tier=MCPTrustTier.LEVEL_0_REFUSE_REMOTE` at `hitl_gate_composer.py:462` (the `five_axis_composition` consumer at `:116`; a configurable sibling path exists at `r_cxa_2_producer_loop_factory.py:89` via `self.mcp_trust_tier`). **Therefore the stub flattens the per-server trust *telemetry*, NOT the gate axis on its own** — un-flattening the locked gate axis additionally requires wiring the per-server declared trust into `GateLevelInput.mcp_trust_tier` at the gate-composition site (see §5, the gate-composition row). The identity-by-ordinal *mapping* is unaffected (independently re-verified in the adversarial review); only the original "un-flattens the gate axis" rationale was over-scoped. *Operator ratifies identity-by-ordinal as the spec-committed mapping at the B2-spec leg — routine, both lenses concur.*

### D4 — B2↔B6 seam → reshape-so-B6-composes (B2 first, B6 follows in the serial cluster)
**Recommendation (the call, not an open question):** B2 makes the sandbox resolver/driver selection **per-host** (each `MCPClientHost`'s resolver/driver built from its own `MCPClientConfig.default_sandbox_*`, replacing the `config.mcp_clients[0]` consumption at `runtime_tool_dispatcher_factory.py:269/:281`). B6 (per-tool sandbox granularity) later slots a per-tool policy map *inside* each host's resolver. They compose as nested keys: **per-host (outer, B2) × per-tool (inner, B6)** — no rework, no co-design barrier. Therefore **B2 lands first; B6 follows** in the SHARED-RUNTIMECONFIG serial cluster (B2/B3✅/B4/B6 must not run concurrently — shared `RuntimeConfig` + stage-5 dispatch path). *Reversible; default committed.*

### D5 — idempotent MCP-host restart (Part-2 minor) → separate forward arc, NOT folded into B2
**Recommendation:** do NOT fold the idempotent-restart minor into B2. It is orthogonal — host *lifecycle recovery* (start currently refuses re-start per §14.9.6 inv 1; mid-dispatch `RT-FAIL-MCP-HOST-UNREACHABLE` recovery), not host *multiplicity*. Folding it bloats the reshape arc and couples two independent spec gates. Per FULL-SPEC (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`, nothing deferred-and-dropped), it is a BUILD arc — registered as its OWN forward arc (provisional `B2-restart`, sibling to the §14.9.6 inv 1 "operator-driven restart arc" the spec already names), sequenced after B2. *Not a silent defer: it is a registered forward item with a named spec home.*

---

## §3 Multi-server semantics — the discovery / routing / trust triad

The three unbuilt pieces, as the impl-against-amended-spec will materialize them:

1. **Discovery.** Each `MCPClientHost.start()` already populates its own `tool_registry` via `list_tools`. B2 adds a materialization-time aggregation: walk `hosts.values()`, build the routing index `dict[ToolId, ServerName]`, fail-loud on collision (D2). The per-host registries remain the authority for each tool's `ToolContract`; the index is a derived lookup (one-source-of-truth: the index is a synchronized derived value, not a second authority).
2. **Routing.** `RuntimeToolDispatcher.dispatch` resolves `step.tool_id` → `server_name` (index) → `host = ctx.mcp_client_hosts[server_name]`. Replace the four hardwired `self._mcp_client_host` reads (`:617/:624/:628/:718`) with the resolved host. `RT-FAIL-TOOL-CONTRACT-UNKNOWN` (existing §14.9.5) fires when the tool_id is in no host's registry.
3. **Per-server trust resolution.** With the host resolved, gate `self._trust_evaluator.evaluate(host.server_name, …)` against the RESOLVED host (the evaluator is already per-server-keyed + multi-server-ready; it resolves trust from `TrustPolicy` keyed on `server_name`, NOT from `host.trust_tier`). The identity-by-ordinal projection (D3) makes the per-server `mcp.server.trust_tier` **telemetry** honest across N servers; the *gate*'s `mcp_trust_tier` axis is a separate site (`hitl_gate_composer.py:462`, hardcoded) that the trust slice must also wire to genuinely realize per-server gate intent (§5 gate-composition row + the §2 D3 blast-radius correction).

This is per-server-uniform at the tool granularity (matching the cleared §14.9.8 resolver + §14.9.9 driver per-server-uniform posture); per-tool granularity is B6.

---

## §4 The B2↔B6 seam (load-bearing — D4's detail)

Both B2 and B6 land on the SAME single-server consumption today: `runtime_tool_dispatcher_factory.py:269/:281` reads `config.mcp_clients[0]` to build the `SandboxDecisionResolver` + the `ToolExecutionDriver` (§14.9.8 + §14.9.9). The seam decision (D4) is to make this **per-host** in B2:

- **B2 obligation:** the factory builds a resolver + driver *per host* from each `MCPClientConfig`, stored alongside the host (or in a `dict[ServerName, (resolver, driver)]`). The §14.9.9 FR-1 driver-selection (delivered-tier ≥ resolved-tier) + FR-2 fail-loud invariants apply **per host** unchanged.
- **B6 composition:** B6 widens each host's *resolver* from per-server-uniform to per-tool (a `dict[ToolId, SandboxDispatchDecision]` inner map). Because B2 already keyed the resolver per host, B6's inner per-tool map nests cleanly — no B2 rework. The §14.9.9 §"Scope boundary" already frames per-tool as "a distinct future arc"; B2 preserves that boundary.

**Consequence for sequencing:** because B2's per-host reshape is a strict generalization of `[0]` that B6 extends inward, there is NO need to co-design B2+B6. B2 lands first; B6 follows. (This resolves the dossier's open question "co-design vs B2-first" → **B2-first**.)

---

## §5 Spec-amendment surface (what the B2-spec leg owes)

The B2-spec leg (next PR; files the Class 1 fork + amends `design-substrate/**`) owes, by §-anchor:

| Spec section | Amendment |
|---|---|
| `Spec_Harness_Runtime_v1.md` C-RT-04 (`HarnessContext` field table) | `mcp_client_host: MCPClientHost` → `mcp_client_hosts: dict[ServerName, MCPClientHost]` (D1). Define `ServerName`. |
| §14.9.1 dispatch body | Steps 1/2/7 read the *resolved* host (routing index lookup) instead of the singular `ctx.mcp_client_host`. |
| §14.9.3 stage-3a factory (host materialization) | `materialize_mcp_client_host_stage(config) → dict[ServerName, MCPClientHost]` (materialize ALL `config.mcp_clients`, not `[0]`); bind to `ctx.mcp_client_hosts`. |
| §14.9.3 stage-5 factory (dispatch wiring) | `materialize_runtime_tool_dispatcher_stage` builds the routing index `dict[ToolId, ServerName]` (D2) + the **per-host** resolver/driver (D4) replacing the `config.mcp_clients[0]` consumption (`runtime_tool_dispatcher_factory.py:269/:281`). (F1-03: this is a SEPARATE factory from stage-3a — the host-materialization obligation and the index/per-host-resolver obligation are distinct.) |
| §14.9.5 fail-class taxonomy | NEW `RT-FAIL-MCP-TOOL-NAME-COLLISION` (D2, permanent, bootstrap-aborts). (Preserve the existing "8 new" + "9th" verbatim counts; this is the 10th, declared in the amendment — mirror the §14.9.9 count-preservation discipline.) |
| §14.9.6 inv 1 | Reword "started exactly once per bootstrap" → "each configured host started exactly once" (N hosts); restart still out-of-scope (D5). |
| §14.9.8 / §14.9.9 "Deferred… Multi-server resolver composition" / "per-server-uniform" | Retire the explicit single-server deferral; commit the per-host resolver/driver composition (D4). |
| CP — C-CP-27 §27 trust projection home | Commit identity-by-ordinal `MCPServerTrustLevel → MCPTrustTier` as the spec mapping (the per-server **telemetry** projection); retire the placeholder stub framing (D3). Replaces the factory docstring's "future arc" promise. |
| **Gate-axis materialization `mcp_trust_tier` (F2-02 — the site that actually un-flattens the locked T-perm-1 gate axis). DECIDED: IN B2's trust slice.** | Bigger than "wire a constant." Probe-verified: `gate_level()` composes its `max()` over only **3 of the 5** declared axes — `per_tool_gate_level`, `blast_radius`, `persona_tier` (`gate_level_rule.py` "the two materialized axes" + "per_tool + mcp_trust are never [materialized]"); the `MCP_TRUST_GATE_LEVEL_FLOOR` (`MCPTrustTier → GateLevel`) mapping is **spec-silent at both CP §19.1 and AS §10.3 — "owed at follow-on spec-extension arc"** (`gate_level_rule.py:9-11/108`). So the hardcoded `mcp_trust_tier=LEVEL_0_REFUSE_REMOTE` at `hitl_gate_composer.py:462` (consumer `five_axis_composition.py:116`; configurable-sibling `r_cxa_2_producer_loop_factory.py:89`) is currently **inert** for gate computation. Realizing the per_mcp_server_trust_tier GATE axis (ADR-D2 §1.5) is therefore a **two-part spec-extension B2 owes**: (a) DEFINE `MCP_TRUST_GATE_LEVEL_FLOOR: dict[MCPTrustTier, GateLevel]` + add `Axis.MCP_TRUST_TIER` to the `gate_level()` `max()` composition (CP §19.1 amendment — the spec-silent mapping); (b) WIRE the resolved per-server declared trust (the D3 projection of `MCPClientConfig.trust_level`) into `GateLevelInput.mcp_trust_tier`, replacing the inert constant. The mapping-direction decision in (a) is the relocated C10⊥C11 tension (§6) — council-eligible at the spec leg. |
| AS — C-AS-10 §10.3 | Cross-reference only (the per-transport floor + trust framework are unchanged; B2 consumes them per N servers). Reciprocal Class 3 cross-ref. |

Likely a CP/runtime plan revision-pass for the new atomic units (multi-host materialization, routing-index discovery, dispatcher routing, per-host resolver/driver, the trust-projection fix). Impl then spans the ~8 carriers + ~10 `ctx.mcp_client_host` consumers (dispatcher_factory info-lookup, `shutdown.py` drain-all-hosts, `mutable_context`, docker/e2b drivers, `validator_escalation_composer`) + e2e against ≥2 mock MCP servers.

---

## §6 Nameable tension + disposition (§10.9)

**T-B2-1 (C10 ⊥ C11) — the trust projection: safe identity vs operator-burden.** This is the §13.4 "council that was missed" case named in root CLAUDE.md — the exact C10 (action-safety: does the projection need a safety mechanism inside it) ⊥ C11 (operator-loop: minimal per-server config burden, honor declared config) tension. **Disposition: convened (genuine dyadic council, dedicated agents per `[[feedback-genuine-skill-invocation-dedicated-agent]]`) → surfaced + probe-resolved.** Both voices independently reached **identity-by-ordinal** with HIGH confidence (contributions at `.harness/council/b2-trust-projection-c10.md` + `b2-trust-projection-c11.md`). The convening was NOT a primary-collapse: C10's veto runs *opposite* to the naive framing — C10 vetoes RETAINING the conservative-collapse stub (it vacates the required operator field) AND vetoes any transport-clamp-in-projection (one-source-of-truth). C11 converges (the stub is a "surprise override" of declared config). **Probe (per §10.9 probe-first):** the three load-bearing cites were verified at HEAD this session — floor body live (`sandbox_tier_floor.py:141-152`), evaluator unknown-server refuse-default live (`per_server_trust_evaluator.py:88/102-115`), T-perm-1 axis composition byte-exact (`ADR-D2.md:69`). The probe confirmed C10's safety concern is already discharged by the separate floor + evaluator mechanisms. **Resolution rationale:** identity-by-ordinal; safety owned by the per-transport floor (`max()` composition) + the `PerServerTrustEvaluator` (deny-wins + unknown-server CONSERVATIVE refuse), not by the projection.

**Premise correction (filed adversarial review F2-01, verified at HEAD).** Both voices' shared premise that the stub "flattens the *locked* T-perm-1 `per_mcp_server_trust_tier` **gate** axis" was partly mis-attributed: the projection output `host.trust_tier` is telemetry-only; the gate axis is fed by a *separate* hardcoded constant at `hitl_gate_composer.py:462` (§2 D3 blast-radius correction + §5 gate-composition row). The council surfaced the correct **mapping** (identity-by-ordinal — independently re-verified sound: same closed 4-value set, transport owned by the floor) on a partly-wrong **premise**. The disposition (identity-by-ordinal; safety at the separate mechanisms) is unchanged; the *causal claim* about what the projection fix un-flattens is corrected. This is exactly the decorrelated-reviewer value (§13.1): the adversarial pass caught a consumer-chain over-claim the council + author shared.

**T-B2-2 (C10 ⊥ C11) — RELOCATED to the gate-axis materialization (deferred to the B2-spec leg, flagged here).** The F2-01 correction relocates the real C10⊥C11 stake: the projection feeds *telemetry* (no action-gating stake — which is *why* the council collapsed so cleanly to identity-by-ordinal), but the **gate-axis materialization** (F2-02 part (a): defining `MCP_TRUST_GATE_LEVEL_FLOOR: dict[MCPTrustTier, GateLevel]`, spec-silent today) is where honoring operator-declared trust has teeth — it moves the HITL gate (`AUTO < ASK < DENY`). **Do NOT let the spec leg assume "identity-by-ordinal is safe" transfers from the projection to the gate.** The discriminator the spec leg MUST check when defining the mapping: **does a higher `mcp_trust_tier` make the gate more permissive?** If yes — e.g. a permissive `L3_ALLOW_WITH_AUDIT` on a remote server lowers its gate floor below `ASK`, loosening HITL — the C10⊥C11 tension is REAL at that site and warrants a genuine council convening at the B2-spec leg (the council's *original* question, finally aimed at the action-gating layer). If the mapping only ever RAISES floors (every tier maps to ≥ the blast/persona floor, never below), it resolves like the projection (safe by construction, monotone with the existing `max()`). **C10's safe-default recommendation for the mapping:** floor-only / monotone (trust never *lowers* the gate below what blast-radius + persona already require) — but this is the spec leg's call to ratify with the council, not this design leg's to decide. This is the §13.4 "council that was missed" pointed at the layer that actually gates actions.

No other nameable cross-domain tension in B2: D1/D2/D4/D5 are mechanical-design choices with sensible defaults (no two-voice tension to name); the routing/collision/reshape decisions are single-axis (CP/runtime) calls.

---

## §7 X-AL-3 classification

**B2 is X-AL-3 territory — confirmed.** The C-RT-04 singular→mapping reshape + the new factory return type + the new tool→server routing contract + the new collision fail-class are all new contract/field/semantics not in the cleared spec. Per I-2 / §4.4, the B2-spec leg MUST file a **Class 1 fork doc** (`.harness/class_1_fork_*.md`) and land the `design-substrate/**` amendments + a clearance marker in the same PR (the §4.5 bundled-absorption discipline; the X-AL-3 guard recognizes the fork doc + clearance marker as back-flow). THIS design PR is mode-agnostic (`.harness/` only) and X-AL-3-clean — it is the pre-fork analysis, not the extension. No design-substrate edit leaks into this PR.

**Not mixed:** there is no B2 capability slice buildable now with zero spec amendment. The only impl-discretion sliver (making the factory emit the "more than one configured" warning its docstring currently implies) is doc-hygiene, not a capability — not worth a separate pre-fork PR.

---

## §8 Sequencing / cascade

```
B2-DESIGN  (THIS PR; mode-agnostic; .harness/ only)
   ↓
B2-spec    (Class 1 fork + design-substrate amendments §5 + clearance marker; operator ratifies the bundle)
   ↓
B2-plan    (CP/runtime plan revision-pass → atomic units: multi-host materialization,
            routing-index discovery, dispatcher routing, per-host resolver/driver, trust-projection fix)
   ↓
B2-impl    (the ~8 carriers + ~10 consumers + e2e vs ≥2 mock MCP servers; expect cross-axis
            test breakage — shared-IS field-shape asserts + CXA-P1 enumeration per
            [[shared-is-shape-change-ripples-cross-axis-field-asserts]] → run the broader suite)
```

**Frontier position:** `E✅ → B2 → R → B4 → CA → B5 → B6 → B7 → M` (per `roadmap_status.md` + the #550 dossier). B2 is in the SHARED-RUNTIMECONFIG serial cluster (B2 / B3✅ / B4 / B6) — must not run concurrently with B4/B6 (shared `RuntimeConfig` + stage-5 dispatch). B6 follows B2 (D4). B2-restart (D5) is a registered sibling forward arc.

**Forward items registered (not deferred-and-dropped, per FULL-SPEC):** (1) **B2-restart** — idempotent MCP-host restart/recovery (D5); (2) **server-qualified tool addressing** — `server_name/tool_id` to permit deliberate same-name tools across servers (D2 future extension).

---

## §9 Verification, confidence, and open operator input

**Verification of this design leg.** Every cite re-grounded at HEAD `c0fc9f3` this session (not from the drifted #550 dossier): the singular contract surface (§14.9.1/.3/.6 by §-anchor), the code carriers (factory `:173/:176/:197`, dispatcher `:617/:624/:628/:718`, factory `:269/:281`), config plurality (`types.py:1242/:574-613/:1650`), the council's three load-bearing claims (floor body, evaluator refuse-default, T-perm-1 axis), and the **F2-01/F2-02 consumer trace** (the gate-composition hardcoded constant `hitl_gate_composer.py:462`; dispatcher has zero `trust_tier`/`gate_level`/`mcp_trust` reads; `host.trust_tier` read only at `runtime_tool_dispatcher_factory.py:184` → telemetry). Confidence **[HIGH]** on the grounding + the X-AL-3 classification + the D3 *mapping* (council + adversarial-review both verified) + the F2-01/F2-02 correction (consumer trace conclusive). **[MODERATE]** on D2's collision policy (fail-loud-vs-server-qualified is the one genuinely deployment-dependent call — flagged for ratification) and on the exact `ServerName` key choice (D1 sub-decision; `server_name == client_name` today per F1-01). The gate-axis materialization (F2-02) is **DECIDED in-B2's trust slice** (§5); the genuinely-open item is the **`MCP_TRUST_GATE_LEVEL_FLOOR` mapping DIRECTION** (F2-02 part (a)) — the relocated C10⊥C11 tension T-B2-2 (§6), council-eligible at the spec leg, NOT this design leg's to decide. **[MODERATE→HIGH]** on D4 (the per-host/per-tool nesting is clean by construction, but the B6 inner-map shape is the future arc's to confirm).

**Single genuine operator input (batched; for the B2-spec leg, NOT a blocker to merging this design PR).** When the B2-spec Class 1 fork opens, the operator ratifies the bundle:
1. **D3 — identity-by-ordinal** trust projection as the spec-committed `MCPServerTrustLevel → MCPTrustTier` mapping (council-recommended; both lenses concur; routine — this is the *telemetry* projection).
2. **T-B2-2 — the `MCP_TRUST_GATE_LEVEL_FLOOR` mapping direction** (the *gate*-axis materialization, spec-silent today): does a higher trust tier loosen the HITL gate, or only raise floors? The relocated C10⊥C11 tension (§6) — convene a genuine dyadic council at the spec leg when defining this mapping; C10's safe-default is floor-only/monotone. This is the substantive trust-posture decision (the projection one is routine).
3. **D2 — collision policy:** fail-loud-at-bootstrap (recommended) vs server-qualified addressing at MVP. The one place a deployment posture could legitimately differ.
4. (D1 `ServerName` key, D4 B2-first, D5 separate-arc are Claude-decided defaults — surfaced for visibility, not gated.)

This is one `AskUserQuestion` at the B2-spec leg, not drip-fed, and not now — this design PR is mode-agnostic and merges on its own (B1/B3-DESIGN precedent).

---

*Filed: R-FS-1 B2-DESIGN leg. Authoring posture: mode-agnostic (`.harness/` only; X-AL-3-clean). Council contributions: `.harness/council/b2-trust-projection-{c10,c11}.md`. Adversarial review: filed alongside this PR. Next leg: B2-spec (Class 1 fork + design-substrate amendments + clearance marker).*
