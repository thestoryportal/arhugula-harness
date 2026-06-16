# Class 1 Fork — B2: multi-server MCP client reshape (`C-RT-04` singular→mapping + tool→server routing + per-host sandbox + identity-by-ordinal trust telemetry projection)

**Type:** Class 1 (design-substrate amendment — the cleared runtime spec commits a **singular** `HarnessContext.mcp_client_host: MCPClientHost` field + a singular stage-3a factory `materialize_mcp_client_host_stage(config) → MCPClientHost`. Multi-server requires reshaping those contracts to a mapping + minting a new tool→server routing contract + a new collision fail-class → new contract/field/semantics not in the cleared spec → X-AL-3 back-flow owed per I-2 / CLAUDE.md §4.4).

**Status:** ✅ APPLIED 2026-06-16 (B2-spec-1 leg) on Claude authority — the reshape sub-decisions are Claude-decided defaults (D1/D2/D4) + a genuine-dyadic-council-converged mapping (D3); all reversible, none sacrificing a committed decision, so adopt-and-note per CLAUDE.md §12.4.1 (no gating AUQ; the PR merge is the operator's ratification). Applied at **runtime spec v1.50 → v1.51** (C-RT-04 reshape + §14.9.1/.3/.6/.8/.9 canonical-reading amendments + NEW §14.9.10 multi-server routing contract + NEW `RT-FAIL-MCP-TOOL-NAME-COLLISION` fail-class) + **CP spec v1.33 → v1.34** (C-CP-27 NEW §27.8 identity-by-ordinal `MCPServerTrustLevel → MCPTrustTier` **telemetry** projection) + **AS spec v1.9 → v1.10** (C-AS-10 §10.3 reciprocal Class-3 cross-ref). **SPEC-ONLY** — no `harness-*/src/**` edit; the reshape is inert until B2-impl. **Clearance markers** filed for all three. **The gate-axis materialization (F2-02) + the T-B2-2 mapping-direction tension are CARVED OUT to the separate B2-spec-2 leg** (see §5).

**Halt target:** None blocking — this is the design-phase back-flow that un-blocks B2-impl. The singular contract is the gate; this fork reshapes it.

**Routing target:** `design-substrate/Spec_Harness_Runtime_v1.md` (v1.50 → v1.51, the headline) + `design-substrate/Spec_Control_Plane_v1_34.md` (NEW file; C-CP-27 §27.8) + `design-substrate/Spec_Action_Surface_v1.md` (v1.9 → v1.10, reciprocal cross-ref).

**Detection mode:** R-FS-1 B2-DESIGN leg (`.harness/r-fs-1-b2-multi-server-mcp-design-v1.md`, #579) §7 X-AL-3 classification + the filed adversarial review (`.harness/adversarial_review_b2_design.md`, APPROVE-WITH-FINDINGS). Frozen at design HEAD `c0fc9f3`; re-grounded at apply HEAD `829f89e5` (code unchanged `c0fc9f3..829f89e5` — only the #580 roadmap refresh + the #579 design doc landed).

---

## §0 — What this leg is (and is NOT)

**B2 = multi-server MCP client.** Today the harness is single-server: the bootstrap materializes exactly ONE `MCPClientHost` from `config.mcp_clients[0]`, and the dispatcher is hardwired to that one host. B2 lifts the harness to N concurrent MCP servers — discover tools across N hosts, route each `TOOL_STEP` to the owning host, and gate per-server trust against the resolved host.

**This leg (B2-spec-1) = the RESHAPE.** It amends the three specs above for the host-multiplicity reshape (D1/D2/D4) + the D3 identity-by-ordinal trust **telemetry** projection. It deliberately does NOT touch the HITL **gate**-axis composition. Why the split (advisor-confirmed, per the B1-spec→spec-1/spec-1b/spec-2 + B3-spec→spec-1/spec-2 precedent): the design §5 bundled the gate-axis work into B2 on a rationale (F2-01: "retiring the trust-projection stub un-flattens the locked T-perm-1 gate axis") that the adversarial review **demolished** — the projection output `host.trust_tier` is **telemetry-only**; the gate axis is fed by a *separate* hardcoded constant (`hitl_gate_composer.py:462`). With that rationale gone, the bundling was reflexive. The clean split is on the **ratification boundary**: the reshape (this leg) has sensible defaults + a converged council → routine; the gate-axis materialization (B2-spec-2) materializes a 4th axis of the **LOCKED T-perm-1** 5-axis composition, mints a spec-silent new mapping (`MCP_TRUST_GATE_LEVEL_FLOOR`) whose direction is a live HITL-security decision, and needs a genuine C10⊥C11 council → its own leg (a near-clone of B3-spec-1).

---

## §1 — Grounding (the singular contract surface — the hard gate)

Re-verified at apply HEAD `829f89e5` (the adversarial review byte-checked these at `c0fc9f3`; code unchanged since):

- **`Spec_Harness_Runtime_v1.md` §4 C-RT-04** (line 2282): `mcp_client_host: MCPClientHost` — a **singular** field, populated at stage 3a, "Per-MCP-server subprocess/HTTP/SSE lifecycle owner." Consumed by `tool_dispatcher` / `per_server_trust_evaluator` / `mcp_namespace_emitter` (lines 2283–2285).
- **§14.9.1 dispatch body** (lines 3851–3857): step 1 resolves `ToolContract` from `ctx.mcp_client_host.tool_registry`; step 2 gates trust via `ctx.per_server_trust_evaluator.evaluate(...)`; step 7 invokes `ctx.mcp_client_host.call_tool(...)`.
- **§14.9.3 stage 3a** (line 3874): `materialize_mcp_client_host_stage(config: RuntimeConfig) → MCPClientHost` (singular return); ingests `config.mcp_clients: list[MCPClientConfig]` (already plural) but instantiates ONE host.
- **§14.9.3 stage 5** (lines 3876–3885): `materialize_runtime_tool_dispatcher_stage` builds the bare `RuntimeToolDispatcher` against the single `ctx.mcp_client_host`.
- **§14.9.6 inv 1** (line 3916): "MCP host instance started exactly once per bootstrap … one subprocess per `MCPClientHost`; HTTP transport opens one client connection pool per host …" — per-host lifecycle language, contract-pinned to one host.
- **§14.9.8 "Deferred"** (line 3959): "Multi-server resolver composition (v1 MVP is single-server per §14.9.3 factory)." **§14.9.9** (line 3969): "Per-server-uniform."
- **Code carriers (single-server, production-wired):** `mcp_client_host_factory.py:173` (`entry = config.mcp_clients[0]`); dispatcher `:617/:624/:628/:718` (hardwired single-host reads); `runtime_tool_dispatcher_factory.py:269/:281` (`config.mcp_clients[0]` resolver + driver — the B2↔B6 seam).
- **Config is already plural:** `types.py:1242` (`RuntimeConfig.mcp_clients: list[MCPClientConfig]`); `:574-613` (per-server `client_name` / `transport` / `trust_level` / `blast_radius` / `connection_url` / `default_sandbox_*` — every per-server field exists); `:1650` (`HarnessContext.mcp_clients: dict[ClientName, MCPClient]` — precedent dict shape).
- **Multi-server-ready by construction (only ever called with one server today):** `per_server_trust_evaluator.py` (`evaluate(server_name, …)` keyed on `server_name`, unknown-server CONSERVATIVE refuse-default at `:88/:102-115`); `sandbox_tier_floor.py:141-152` (per-transport floor live + non-vacuous).

**Net:** config is plural; per-server trust + per-transport floor are multi-server-ready; the THREE genuinely-unbuilt pieces are (1) the singular `mcp_client_host` field + singular factory, (2) cross-host tool discovery (a unified routing index), (3) the dispatcher's tool→server routing — plus the vacuous trust-projection stub (D3) and ~10 downstream `ctx.mcp_client_host` consumers needing the field reshape.

---

## §2 — The reshape sub-decisions (this leg)

### D1 — `C-RT-04` reshape → `mcp_client_hosts: dict[ServerName, MCPClientHost]`
`HarnessContext.mcp_client_host: MCPClientHost` → `mcp_client_hosts: dict[ServerName, MCPClientHost]`. **Key = the host's `server_name`** (the per-deployment registry ID on `MCPHostHealth.server_name`, read by the dispatcher at `:624/:718` and the basis for the trust gate + spans), NOT `client_name` — routing resolves a tool to its OWNING server, and trust + telemetry already key on `server_name`. `HarnessContext.mcp_clients: dict[ClientName, MCPClient]` already establishes the dict-of-hosts shape; B2 adds a sibling dict for the *started* hosts. **`ServerName`** is committed as a `NewType` alias over `str` (the `server_name` registry ID). **Current-state honesty (adversarial F1-01):** at HEAD the factory sets `server_name=entry.client_name` (`mcp_client_host_factory.py:176`) — the two identities are the **same value today**; the key choice is defensible because routing + trust + spans all read `server_name`, and the `ServerName` alias preserves the config-key/runtime-identity distinction as a **forward property**, not a present-state distinction.

### D2 — discovery/registry → per-host registries + a bootstrap-built routing index; **fail-loud on tool-name collision**
Keep each host's own `list_tools`-populated `tool_registry` (per-host, already built). At stage-5 materialization, aggregate a **routing index** `dict[ToolId, ServerName]` mapping each discovered tool to its owning host. The dispatcher resolves `step.tool_id` → owning `server_name` via the index, then dispatches to `hosts[server_name]`. The index is a derived synchronized value (one-source-of-truth: the per-host registries remain the authority for each tool's `ToolContract`). **Collision policy: fail-loud at bootstrap.** A `tool_id` advertised by ≥2 servers raises a new permanent startup fail-class `RT-FAIL-MCP-TOOL-NAME-COLLISION` → bootstrap aborts. Rationale: honors the detect-then-refuse / loud-on-misconfig discipline (the §14.9.9 FR-2 + U-CP-68/69 posture); deterministic routing; minimal contract at MVP. **Adopt-and-note** (§12.4.1): clear default (fail-loud), reversible — **server-qualified addressing** (`server_name/tool_id`, to permit deliberate same-name tools) is a registered forward item (§6), not silently foreclosed.

### D3 — `MCPServerTrustLevel → MCPTrustTier` projection → **identity-by-ordinal** (retire the over-gating stub) — TELEMETRY only
Make the projection a faithful 1:1 ordinal map (`L0→LEVEL_0` … `L3→LEVEL_3`), retiring the current stub (`_trust_tier_from_level` → constant `LEVEL_0_REFUSE_REMOTE` at `mcp_client_host_factory.py:197`). The two enums are the **same closed 4-value set** (CP `MCPTrustTier` docstring: "byte-exact factor-out of the AS-owned value set" at C-AS-10 §10.3), so identity is the unique faithful realization. **No transport-aware clamp inside the projection** — transport severity is owned by the per-transport sandbox floor (`sandbox_tier_floor.py:141-152`, verified live); the narrow `level`-only signature is positive evidence transport belongs to the floor (a clamp would be a one-source-of-truth violation). The unknown/undeclared-server case is already refuse-defaulted at the evaluator's `_default_tier_resolver`. **Where it lives:** CP-side (C-CP-27 §27 trust framework; `harness-as/CLAUDE.md` §1.4: the trust-framework function lives in CP; AS declares the per-transport floor only).

**Scope correction (adversarial F2-01, verified at HEAD — load-bearing).** The projection output `host.trust_tier` is **telemetry-only** — grounded on the **code trace** (not a docstring): it is read solely at `runtime_tool_dispatcher_factory.py:184` → `MCPClientNamespaceEmitter` → the `mcp.server.trust_tier` **span attribute**, and the dispatch trust **gate** (`runtime_tool_dispatcher.py:628`) calls `evaluate(server_name, …)` via `TrustPolicy` and **never reads `host.trust_tier`** (ZERO `trust_tier`/`gate_level`/`mcp_trust` reads in the dispatcher). (The `mcp_client_host.py:128-130` docstring's telemetry half corroborates, but its trailing "…**and gate** the per-server-trust evaluation step" clause is **STALE** — the gate keys on `server_name`, not `host.trust_tier` — flagged for a B2-impl docstring fix at §6.) And the locked T-perm-1 **gate** axis `mcp_trust_tier` is fed by a **separate hardcoded constant** at `hitl_gate_composer.py:462`. **Therefore retiring the stub un-flattens the per-server trust _telemetry_, NOT the gate axis** — un-flattening the locked gate axis is a *separate* change (F2-02), carved out to B2-spec-2 (§5). The identity-by-ordinal *mapping* is independently sound (re-verified by the council + the adversarial review); only the original "un-flattens the gate axis" rationale was over-scoped. **Council-converged** (genuine dyadic C10⊥C11, dedicated agents, probe-resolved — design §6 + `.harness/council/b2-trust-projection-{c10,c11}.md`); adopt-and-note.

### D4 — B2↔B6 seam → **reshape-so-B6-composes (B2 first)**
B2 makes the sandbox resolver/driver selection **per-host** (each `MCPClientHost`'s resolver/driver built from its own `MCPClientConfig.default_sandbox_*`, replacing the `config.mcp_clients[0]` consumption at `runtime_tool_dispatcher_factory.py:269/:281`). B6 (per-tool sandbox granularity) later slots a per-tool policy map *inside* each host's resolver — they compose as nested keys (per-host outer / per-tool inner) with no rework. **B2 lands first; B6 follows** in the SHARED-RUNTIMECONFIG serial cluster (B2/B3✅/B4/B6 must not run concurrently — shared `RuntimeConfig` + stage-5 dispatch path). The §14.9.9 FR-1 driver-selection + FR-2 fail-loud invariants apply **per host** unchanged. Adopt-and-note.

### D5 — idempotent MCP-host restart → separate forward arc (NOT this leg)
Do NOT fold the idempotent-restart minor (start refuses re-start per §14.9.6 inv 1; mid-dispatch `RT-FAIL-MCP-HOST-UNREACHABLE` recovery) into B2 — it is host *lifecycle recovery*, orthogonal to host *multiplicity*. Per FULL-SPEC (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`) it is a BUILD arc, registered as its own forward arc **B2-restart** (§6), sibling to the §14.9.6 inv 1 "operator-driven restart arc" the spec already names. Not a silent defer — a registered forward item with a named spec home.

---

## §3 — Spec-amendment surface (what this leg applies)

| Spec section | Amendment (applied this leg) |
|---|---|
| `Spec_Harness_Runtime_v1.md` C-RT-04 (§4 field table) | **CANONICAL-READING AMENDMENT** — `mcp_client_host: MCPClientHost` reshaped to `mcp_client_hosts: dict[ServerName, MCPClientHost]` (D1). `ServerName` committed as a `NewType` over `str`. Body line 2282 NOT edited (delta-only convention); the change-note + NEW §14.9.10 carry the canonical shape. |
| §14.9.1 dispatch body | **CANONICAL-READING AMENDMENT** — steps 1/2/7 read the *resolved* host (`hosts[routing_index[step.tool_id]]`) instead of the singular `ctx.mcp_client_host`. `RT-FAIL-TOOL-CONTRACT-UNKNOWN` (existing) fires when the tool_id is in no host's registry. |
| §14.9.3 stage 3a | **CANONICAL-READING AMENDMENT** — `materialize_mcp_client_host_stage(config) → dict[ServerName, MCPClientHost]` (materialize ALL `config.mcp_clients`, not `[0]`); bind to `ctx.mcp_client_hosts`. |
| §14.9.3 stage 5 | **CANONICAL-READING AMENDMENT** — `materialize_runtime_tool_dispatcher_stage` builds the routing index `dict[ToolId, ServerName]` (D2) + the **per-host** resolver/driver (D4), replacing the `config.mcp_clients[0]` consumption. (F1-03: this is a SEPARATE factory from stage-3a — host-materialization vs index/per-host-resolver are distinct obligations.) |
| §14.9.5 fail-class taxonomy | NEW **`RT-FAIL-MCP-TOOL-NAME-COLLISION`** (D2; permanent; bootstrap-aborts). The existing "8 new" (§14.9.5) + "9th" (§14.9.9) counts are PRESERVED VERBATIM; this is the **10th**, declared at NEW §14.9.10 (mirroring the §14.9.9 count-preservation discipline). |
| §14.9.6 inv 1 | **CANONICAL-READING AMENDMENT** — "started exactly once per bootstrap" → "each configured host started exactly once" (N hosts); idempotent restart still out-of-scope (D5). |
| §14.9.8 / §14.9.9 deferral / per-server-uniform | **CANONICAL-READING AMENDMENT** — retire the explicit single-server resolver-composition deferral (§14.9.8 "Deferred"); commit the per-host resolver/driver composition (D4). The §14.9.8/.9 *per-server-uniform per-tool* boundary is preserved (per-tool is still B6). |
| NEW **§14.9.10** | Consolidating body section: the multi-server host-materialization + tool→server routing contract (`ServerName`, `mcp_client_hosts`, the routing index, the collision fail-class, per-host resolver/driver, the dispatch resolved-host re-reading, the inv-1 reword) — mirroring how §14.9.8 (v1.41) + §14.9.9 (v1.43) were appended as NEW sections with change-note re-reading entries pointing to them. |
| CP — C-CP-27 NEW **§27.8** | Identity-by-ordinal `MCPServerTrustLevel → MCPTrustTier` **telemetry** projection committed as the spec mapping (D3); retire the placeholder stub framing. Replaces the factory docstring's "future arc" promise. |
| AS — C-AS-10 §10.3 | Reciprocal **Class-3 cross-ref** only — the per-transport floor + trust framework are unchanged; B2 consumes them per N servers; `MCPServerTrustLevel` is projected to `MCPTrustTier` identity-by-ordinal per CP §27.8. |

**NOT applied this leg (→ B2-spec-2):** the gate-axis materialization (F2-02 — `MCP_TRUST_GATE_LEVEL_FLOOR` + `Axis.MCP_TRUST_TIER` into the locked `max()` + wiring the resolved per-server trust into `GateLevelInput.mcp_trust_tier` at `hitl_gate_composer.py:462`). See §5.

---

## §4 — X-AL-3 classification + cascade

**X-AL-3 territory — confirmed.** The C-RT-04 singular→mapping reshape + the new factory return type + the new tool→server routing contract + the new collision fail-class are new contract/field/semantics not in the cleared spec. Per I-2 / CLAUDE.md §4.4/§4.5 this leg files THIS Class 1 fork doc + lands the `design-substrate/**` amendments + clearance markers in the same PR (the bundled-absorption discipline; the X-AL-3 guard recognizes the fork doc + clearance markers as back-flow).

**Cascade:** runtime spec (the headline) + CP spec (C-CP-27 §27.8 telemetry projection) + AS spec (§10.3 reciprocal Class-3 cross-ref). **ZERO ADR / ADD / PRD change** — the reshape honors ADR-F1/F4 (multi-server MCP client under the committed stack) + ADR-D2 (the trust/sandbox axes unchanged; the gate-axis materialization that *would* touch the T-perm-1 composition is carved out to B2-spec-2). **No CXA seam touched** (adversarial §C: grep of `Cross_Axis_Composition_Document_v2_20.md` for `mcp_client_host` / `PerServerTrustEvaluator` / `MCPTrustTier` → zero matches; the field reshape does not touch a declared CXA seam — no CXA amendment owed). Impl-time cross-axis test breakage is expected (shared-IS field-shape asserts + the CXA-P1 enumeration per `[[shared-is-shape-change-ripples-cross-axis-field-asserts]]`) → B2-impl runs the broader suite.

---

## §5 — Carved out to B2-spec-2 (the gate-axis leg)

The B2-spec-2 leg owes (separate PR, its own Class 1 fork, a genuine T-B2-2 dyadic council → AUQ):

1. **F2-02 gate-axis materialization** (the site that actually un-flattens the locked T-perm-1 `per_mcp_server_trust_tier` gate axis): define `MCP_TRUST_GATE_LEVEL_FLOOR: dict[MCPTrustTier, GateLevel]` (spec-silent today at both CP §19.1 and AS §10.3 — `gate_level_rule.py:9-11/108`), add `Axis.MCP_TRUST_TIER` to the `gate_level()` `max()` composition (today composes only **3 of 5** axes — `per_tool_gate_level` + `blast_radius` + `persona_tier`; `gate_level_rule.py`), and wire the resolved per-server declared trust (the D3 projection of `MCPClientConfig.trust_level`) into `GateLevelInput.mcp_trust_tier`, replacing the inert constant at `hitl_gate_composer.py:462`. **Completeness honesty:** this moves the gate composition 3-of-5 → **4-of-5** (`per_tool_gate_level` stays inert — its own producer is the registered O-CP-3 follow-on).
2. **T-B2-2 (C10 ⊥ C11) — the mapping DIRECTION:** does a higher `mcp_trust_tier` make the HITL gate **more permissive** (a permissive remote tier lowering the gate below `ASK`, loosening HITL — the real C10⊥C11 tension), or does the mapping only **raise floors** (monotone — trust never lowers the gate below what blast-radius + persona already require)? This is a live HITL-security decision on a LOCKED permanent-tension axis → **genuine dyadic council + operator AUQ** at B2-spec-2 (the §13.4 "council that was missed," finally aimed at the action-gating layer). **C10's safe-default recommendation** (to bring to the council, NOT to adopt silently): floor-only / monotone.

**Why the split is buildable-independently (verified):** the gate-axis wiring needs the D3 per-server projection (this leg) + the resolved owning host's trust — on single-server the resolved host is the one host; the `hitl_gate_composer.py:462` `mcp_trust_tier=` is a self-contained `GateLevelInput` field, NOT coupled to the host-dict. So B2-spec-2 composes cleanly after this leg's D3 + reshape, without rework.

---

## §6 — Forward items registered (not deferred-and-dropped, per FULL-SPEC)

1. **B2-restart** — idempotent MCP-host restart/recovery (D5); sibling to the §14.9.6 inv 1 "operator-driven restart arc."
2. **server-qualified tool addressing** — `server_name/tool_id` to permit deliberate same-name tools across servers (D2 future extension); re-open trigger = a deployment that legitimately needs same-named tools.
3. **B2-spec-2** — the gate-axis materialization (F2-02) + T-B2-2 council (§5).
4. **B6** — per-tool sandbox granularity (D4 inner map), in the SHARED-RUNTIMECONFIG serial cluster after B2.
5. **B2-impl docstring fix** (decorrelated-review finding, adversarial F1-03): the `mcp_client_host.py:128-130` docstring carries a STALE trailing clause "…and gate the per-server-trust evaluation step" — the gate keys on `server_name` (via `TrustPolicy`), NOT on `host.trust_tier` (telemetry-only). Correct the docstring to telemetry-only when B2-impl reshapes this file (it already edits the `:197` stub). Naturally co-located with the D3 stub-retirement at B2-impl.

---

## §7 — Verification + filing footer

**Verification.** Every cite re-grounded at apply HEAD `829f89e5` (code unchanged `c0fc9f3..829f89e5`): the singular contract surface (C-RT-04 line 2282; §14.9.1/.3/.6/.8/.9 by §-anchor); the code carriers (factory `:173/:176/:197`, dispatcher `:617/:624/:628/:718`, factory `:269/:281`); config plurality (`types.py:1242/:574-613/:1650`); the F2-01 telemetry-only consumer trace (`host.trust_tier` read only at `runtime_tool_dispatcher_factory.py:184`; the gate constant at `hitl_gate_composer.py:462`); the split discriminator (the `:462` `mcp_trust_tier=` is a self-contained `GateLevelInput` field). Confidence **[HIGH]** on the grounding, the X-AL-3 classification, the D3 mapping (council + adversarial review both verified), and the F2-01/F2-02 correction (consumer trace conclusive). **[MODERATE]** on D2's collision policy (fail-loud-vs-server-qualified is the one genuinely deployment-dependent call — registered as a forward item, reversible).

| Field | Value |
|---|---|
| Artifact | `.harness/class_1_fork_b2_multi_server_mcp_client_reshape.md` |
| Filed at | R-FS-1 B2 sub-program, B2-spec-1 leg, 2026-06-16 |
| Authority | B2-DESIGN (`.harness/r-fs-1-b2-multi-server-mcp-design-v1.md`, #579) §2/§5/§7 + adversarial review (`.harness/adversarial_review_b2_design.md`, F2-01/F2-02 folded) + advisor split (ratification-boundary, B1/B3-spec precedent); R-FS-1 §5.0 full-spec directive |
| Co-published (this PR) | runtime spec v1.51 + CP spec v1.34 + AS spec v1.10 + 3 clearance markers + pointer refreshes (root `CLAUDE.md` §2.3, `harness-cp/CLAUDE.md`, `harness-as/CLAUDE.md`, `claude-artifact-pointers.md`). **Owed post-merge:** the §12.2.1 roadmap fixed-point refresh (terminating refresh PR). |
| Coordinated next arcs | B2-spec-2 (gate-axis F2-02 + T-B2-2 council) → B2-plan (CP/runtime atomic units) → B2-impl (~8 carriers + ~10 consumers + e2e vs ≥2 mock MCP servers). |
| Revision policy | Design-substrate amendment per CLAUDE.md §4.5; reshape sub-decisions are reversible adopt-and-note (no AUQ); the genuine T-B2-2 gate is at B2-spec-2. |

---

*End of B2 multi-server MCP client reshape fork. Design at `.harness/r-fs-1-b2-multi-server-mcp-design-v1.md`. Adversarial review at `.harness/adversarial_review_b2_design.md`. Council at `.harness/council/b2-trust-projection-{c10,c11}.md`. Gate-axis carve-out → B2-spec-2.*
