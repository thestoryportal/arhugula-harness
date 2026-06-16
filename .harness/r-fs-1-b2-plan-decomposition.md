# R-FS-1 B2-plan — Multi-Server MCP + Gate-Axis Atomic-Unit Decomposition

**Authored:** 2026-06-16 · **Arc:** R-FS-1 child arc **B2** (multi-server MCP), **B2-plan** leg · **Posture:** design-phase (authors `design-substrate/**` plan deltas + this `.harness/` companion) · **HEAD at authoring:** `b8282564`

**What this is.** The implementation-planner decomposition of the **two cleared B2 spec legs** —
**B2-spec-1** (the multi-server reshape: runtime spec **v1.51** §14.9.10 `C-RT-04` singular→mapping + tool→server routing + per-host sandbox + `RT-FAIL-MCP-TOOL-NAME-COLLISION`; CP spec **v1.34** §27.8 identity-by-ordinal trust **telemetry** projection) PLUS
**B2-spec-2** (the gate axis: CP spec **v1.35** §19.1.2 `MCP_TRUST_GATE_LEVEL_FLOOR` materializing the 4th §19.1 axis) —
into atomic units across two delta-only plan amendments: **runtime v2.46 → v2.47** (7 NEW units) + **CP v2.35 → v2.36** (1 NEW unit). Mirrors the B1-plan / B3-plan precedent (co-published plan deltas with an aggregate cross-axis DAG). Decomposes; does not author spec/code.

**Scope note (the dashboard phrasing under-describes it).** The roadmap/dashboard next-action names only the gate-axis ("`gate_level()` 4th-axis composition + composer resolved-host wiring"). That is shorthand for the most-recent spec leg. **B2-plan covers BOTH legs** — the reshape (B2-spec-1) is still SPEC-ONLY/unbuilt and the design→spec→plan→impl cascade has no other slot for its decomposition; both fork docs point B2-plan at the full reshape+gate impl (reshape fork §7: "B2-plan → B2-impl (~8 carriers + ~10 consumers)"; gate-axis fork §4: "CP/runtime atomic units for the `gate_level()` 4th-axis composition + the composer resolved-host wiring").

**Inputs re-grounded by direct read at HEAD `b8282564`:** the B2 design (`.harness/r-fs-1-b2-multi-server-mcp-design-v1.md`), both B2 fork docs (`class_1_fork_b2_multi_server_mcp_client_reshape.md` ✅ APPLIED + `class_1_fork_b2_spec_2_gate_axis_materialization.md` ✅ APPLIED), CP spec v1.35 §19.1.2, CP plan v2.35 + runtime plan v2.46, and the code carriers (`gate_level_rule.py`, `hitl_gate_composer.py:462`, `bootstrap/factories/mcp_client_host_factory.py`, `bootstrap/factories/runtime_tool_dispatcher_factory.py`, `runtime_tool_dispatcher.py`, `bootstrap/mutable_context.py`, `types.py`).

---

## §1 — The keystone homing facts

**Two homing facts drive the unit-placement split:**

1. **The reshape + the gate composer are `harness-runtime`.** The `MCPClientHost` materialization (`bootstrap/factories/mcp_client_host_factory.py`), the dispatcher (`lifecycle/runtime_tool_dispatcher.py` + `bootstrap/factories/runtime_tool_dispatcher_factory.py`), the `HarnessContext` carrier (`bootstrap/mutable_context.py:212` + `types.py:1837`), and the HITL gate composer (`lifecycle/hitl_gate_composer.py`) are all **runtime-homed**. The D3 `MCPServerTrustLevel → MCPTrustTier` projection (CP §27.8 *contract*) is realized in runtime code (`mcp_client_host_factory.py:178/:197` `_trust_tier_from_level`) → a **runtime unit citing the CP contract** (the B3 / U-RT-121 code-location homing precedent: units home where the code lives).
2. **The `gate_level()` 4-axis composition rule is `harness-cp`.** `gate_level_rule.py` (`gate_level()` + `GateLevelInput` + the floor tables) is the CP package. So the 4th-axis composition (adding `Axis.MCP_TRUST` to `per_axis_floors` + committing `MCP_TRUST_GATE_LEVEL_FLOOR`) is the **one CP unit** (U-CP-98); the runtime composer's `GateLevelInput.mcp_trust_tier` *producer* is a **runtime unit** (U-RT-131) — which, per §5.1, installs the L3 **no-floor default** at the host-less gate sites (the real per-server resolved-host feed is the registered `B-TOOL-GATE` forward arc, since no tool-step gate site exists today).

**No new cross-axis carrier edge for the gate axis.** `GateLevelInput.mcp_trust_tier` (the carrier the composer feeds) ALREADY exists (present-but-unconsumed since v2.20, `gate_level_rule.py:104`); the composer already imports `GateLevelInput` / `MCPTrustTier` from `harness_cp` (`hitl_gate_composer.py:457`). The gate axis is realized WITHOUT a new cross-axis carrier — the CP↔RT coupling is a **safety-sequencing pin** (§5), not a DAG dependency edge.

---

## §2 — Unit list

### Runtime plan v2.47 (7 NEW units — U-RT-125..131)

| Unit | Title | Depends on | B2-impl arc | Spec-cite |
|---|---|---|---|---|
| **U-RT-125** | `ServerName` `NewType` + `HarnessContext.mcp_client_hosts: dict[ServerName, MCPClientHost]` reshape (D1 carrier) | (none) | B2-impl-1 | runtime v1.51 §14.9.10 (D1); C-RT-04 (§4 field reshape) |
| **U-RT-126** | stage-3a `materialize_mcp_client_host_stage(config) → dict[ServerName, MCPClientHost]` — materialize ALL `config.mcp_clients` (retire the `[0]` at `mcp_client_host_factory.py:173`) | [U-RT-125] | B2-impl-1 | runtime v1.51 §14.9.3 + §14.9.10 (D1 factory) |
| **U-RT-127** | stage-5 bootstrap routing index `dict[ToolId, ServerName]` + `RT-FAIL-MCP-TOOL-NAME-COLLISION` fail-class (fail-loud at bootstrap on cross-host tool-name collision) | [U-RT-126] | B2-impl-2 | runtime v1.51 §14.9.10 (D2) + §14.9.5 (10th fail-class) |
| **U-RT-128** | dispatcher tool→server resolution (`hosts[routing_index[step.tool_id]]` at dispatch steps 1/2/7) + the ~10 `ctx.mcp_client_host` → `mcp_client_hosts` consumer reshapes (dispatcher + driver signatures) | [U-RT-127] | B2-impl-2 | runtime v1.51 §14.9.1 + §14.9.10 (D2 dispatch) |
| **U-RT-129** | D3 identity-by-ordinal `MCPServerTrustLevel → MCPTrustTier` projection — retire the constant-collapse stub (`_trust_tier_from_level` `mcp_client_host_factory.py:178/:197` → `L0→LEVEL_0 … L3→LEVEL_3`) + the `mcp_client_host.py:128-130` telemetry-only docstring fix (reshape fork §6 item 5 / F1-03) | (none) | B2-impl-1 | CP spec v1.34 §27.8 (D3 telemetry projection); reshape fork §6 item 5 |
| **U-RT-130** | D4 per-host sandbox resolver/driver — replace `runtime_tool_dispatcher_factory.py:269/:281` `config.mcp_clients[0]` with each host's own `MCPClientConfig.default_sandbox_*` (FR-1/FR-2 §14.9.9 applied **per host**) | [U-RT-126] | B2-impl-2 | runtime v1.51 §14.9.10 (D4); §14.9.9 FR-1/FR-2 per-host |
| **U-RT-131** | gate-axis composer **no-floor default** for the host-less gate sites — replace the **harmful** `hitl_gate_composer.py:462` `mcp_trust_tier=LEVEL_0_REFUSE_REMOTE` constant with the L3 AUTO-mapping no-floor default (the composer gates only host-less inference/sub-agent steps; no owning MCP host exists at any gate site — §5). The `per_tool_gate_level`/O-CP-3 degenerate-default analog | **(none) — leaf** | B2-impl-3 **(co-land with U-CP-98 — §5)** | CP spec v1.35 §19.1.2 inv 3; the resolved-host feed = the `B-TOOL-GATE` forward arc (§5/§6) |

### CP plan v2.36 (1 NEW unit — U-CP-98)

| Unit | Title | Depends on | B2-impl arc | Spec-cite |
|---|---|---|---|---|
| **U-CP-98** | `gate_level()` 4th-axis composition — commit `MCP_TRUST_GATE_LEVEL_FLOOR` (Table A) in `gate_level_rule.py` + add `Axis.MCP_TRUST: MCP_TRUST_GATE_LEVEL_FLOOR[input.mcp_trust_tier]` to `per_axis_floors` (3-of-4 → 4-of-4) + refresh the 5 stale-carry "spec-silent" docstrings to cite §19.1.2 (gate-axis fork §4 item 4 / F3-01) | (none) — reads the existing `GateLevelInput.mcp_trust_tier` field | B2-impl-3 **(co-land with U-RT-131 — §5; HARMFUL-if-alone)** | CP spec v1.35 §19.1.2 |

**Total: 8 NEW units** (7 RT + 1 CP) + **0 cross-axis DAG edges** (the gate-axis CP↔RT coupling is a §5 co-land sequencing pin, not a dependency edge; the reshape is RT-internal).

---

## §3 — Coverage matrix (every cleared B2 spec subsection + design item → unit or disposition)

| Cleared spec / design item | Disposition |
|---|---|
| runtime v1.51 §14.9.10 **D1** (`C-RT-04` `mcp_client_host`→`mcp_client_hosts` mapping + `ServerName` NewType + stage-3a factory materializes all hosts) | **U-RT-125** (carrier) + **U-RT-126** (factory) |
| runtime v1.51 §14.9.10 **D2** (cross-host routing index `dict[ToolId, ServerName]` + `RT-FAIL-MCP-TOOL-NAME-COLLISION` + dispatch resolved-host re-read) | **U-RT-127** (index + fail-class) + **U-RT-128** (dispatch resolution + consumers) |
| runtime v1.51 §14.9.10 **D4** (per-host sandbox resolver/driver; FR-1/FR-2 per host) | **U-RT-130** |
| CP v1.34 §27.8 **D3** (identity-by-ordinal `MCPServerTrustLevel → MCPTrustTier` telemetry projection; retire the constant stub) | **U-RT-129** (runtime realization, cites CP §27.8) |
| CP v1.35 §19.1.2 (`MCP_TRUST_GATE_LEVEL_FLOOR` table + `Axis.MCP_TRUST` into `gate_level()` `per_axis_floors`) | **U-CP-98** |
| CP v1.35 §19.1.2 inv 3 (no-floor default at the host-less gate sites — retire the harmful `hitl_gate_composer.py:462` L0 constant) | **U-RT-131** (the `per_tool_gate_level`/O-CP-3 degenerate-default analog) |
| CP v1.35 §19.1.2 **Producer ¶** (composer feeds the **resolved owning MCP host's** trust into `GateLevelInput.mcp_trust_tier` at a **tool-step** gate) | **REGISTERED forward — `B-TOOL-GATE`** (§5/§6; no tool-step gate site exists — the runtime composer gates only inference/sub-agent at `stage_5_loop_init.py:337/:431`). NOT this arc. |
| reshape fork §6 item 5 / **F1-03** (`mcp_client_host.py:128-130` stale "…and gate" telemetry docstring) | **U-RT-129** (bundled — naturally co-located with the D3 stub-retirement) |
| gate-axis fork §4 item 4 / **F3-01** (`gate_level_rule.py` 5 docstring sites asserting `MCP_TRUST` is "spec-silent / owed at follow-on arc" — factually false at v1.35) | **U-CP-98** (bundled — the same edit adds `Axis.MCP_TRUST` to `per_axis_floors`) |
| **e2e — reshape** (tool discovery across ≥2 MCP hosts + tool→server routing + collision fail-loud) | **AC-level / arc** (B2-impl-2; §6). The ≥2-mock-MCP-server fixture is the one genuinely-new build asset — called out at §6. |
| **e2e — gate axis** | **AC-level / arc** (B2-impl-3; §6). The per-tier `L0→DENY…L3→AUTO` table semantics are at the **U-CP-98 direct `gate_level()` unit test** (exercisable at the function level today — the field pre-exists). The **production** path is a **non-regression** baseline: the host-less gate composes `MCP_TRUST=AUTO` → identical to the 3-axis path (co-land safety). A real-gate `L0→DENY` needs the `B-TOOL-GATE` tool-step gate (forward). |
| **O-CP-3 + `B-TOOL-GATE`** (the TWO degenerate-default producers) | **REGISTERED forward — NOT this arc.** **Completeness honesty:** after B2, `gate_level()` composes **4-of-4** materialized §19.1 axes, but BOTH non-blast/persona axes feed a degenerate default at every production gate site until their real producers land: **(a) `per_tool_gate_level`** → default-`AUTO` until the C-AS-03 `tier` wire (pre-existing CP plan §6 **O-CP-3**); **(b) `mcp_trust`** → L3 no-floor default until a tool-step gate site exists (**`B-TOOL-GATE`**; the composer gates only host-less inference/sub-agent today). B2 materializes the §19.1 *composition* 4-of-4 but does NOT close *producer*-completeness for either axis. |
| reshape fork §6 item 1 (**B2-restart** — idempotent MCP-host restart/recovery, D5) | **REGISTERED forward — NOT this arc** (sibling to §14.9.6 inv 1 operator-driven restart arc). |
| reshape fork §6 item 2 (**server-qualified tool addressing** — `server_name/tool_id`) | **REGISTERED forward — NOT this arc** (D2 reversible extension; re-open = a deployment needing same-named tools across servers). |
| reshape fork §6 item 4 (**B6** — per-tool sandbox granularity, D4 inner map) | **REGISTERED forward — NOT this arc** (SHARED-RUNTIMECONFIG serial cluster, after B2). |
| AS spec C-AS-10 §10.3 (per-transport floor + trust framework) | **NO plan unit** — already landed; B2 *consumes* it per N hosts; the AS↔CP reciprocal cross-ref landed at AS v1.10 (B2-spec-1). No AS impl owed for B2. |

**No silent gap.** Every cleared B2 spec subsection + every design item → a unit OR an explicit registered-forward / AC-level / no-unit disposition. The one **load-bearing finding** is the U-CP-98 HARMFUL-if-alone hazard (§5).

---

## §4 — Aggregate cross-axis DAG (B2 arc)

8 nodes (1 CP + 7 RT). Cross-axis home: CP plan v2.36 §3.7.

**Per-unit deps:**
- Leaves (`(none)`): U-RT-125, U-RT-129, **U-RT-131**, **U-CP-98**
- U-RT-126 → {U-RT-125}
- U-RT-127 → {U-RT-126}
- U-RT-128 → {U-RT-127}
- U-RT-130 → {U-RT-126}

**Topological order:** `U-RT-125, U-RT-129, U-RT-131, U-CP-98` (foundational leaves) → `U-RT-126` → `{U-RT-127, U-RT-130}` → `U-RT-128`. A valid linear extension exists ⟹ **DAG**. U-RT-131 + U-CP-98 are independent leaves co-landed into B2-impl-3 by the §5 safety pin (not a topological dependency).

**Acyclicity + cross-axis cycle guard:**
- **No cross-axis DAG edge.** Unlike B1/B3 (which carried RT→CP carrier-consumption edges), B2's gate axis introduces no new cross-axis carrier — `GateLevelInput.mcp_trust_tier` pre-exists and the composer's `harness_cp` import pre-exists. U-CP-98 is an independent CP leaf (reads the existing field); U-RT-131 is RT-internal (sets a field on the existing import). So there is **no CP↔RT dependency edge** and trivially **no CP↔RT cycle**.
- The CP↔RT *safety* coupling (U-CP-98 ⊕ U-RT-131 must co-land) is a **§5 build-sequencing pin**, NOT a DAG edge. A `U-CP-98 → U-RT-131` dependency edge *would* express the safe ordering (U-RT-131 first-or-with), but it is a **CP→RT cross-axis dependency forbidden by axis-isolation** (`harness-cp` must not import `harness-runtime`) — that, not "reverse-of-a-dependency," is the load-bearing reason it cannot be a graph edge.
- **RT-internal:** every edge points to a strictly-earlier node (125/129/131 foundational leaves; 126→125; 127→126; 130→126; 128→127) → no back-edge.
- **Acyclic confirmed.** No edge to a not-yet-existing unit (all targets are co-published in v2.47 or pre-exist at HEAD).

The B1 (§3.1–§3.3) + B3 (§3.4) + E-1/E-2 (§3.5) + E-3 (§3.6) aggregates are PRESERVED VERBATIM; the B2 nodes attach without contesting them (B2 touches the MCP-host/dispatch/gate surfaces, disjoint from the engine-class/topology surfaces of the prior arcs).

---

## §5 — The one load-bearing finding (the U-CP-98 HARMFUL-if-alone hazard)

**U-CP-98 (compose `Axis.MCP_TRUST` into `gate_level()`) is HARMFUL-if-landed-alone — it MUST co-land with U-RT-131 in the final impl arc. This is the inverse of B3's G2c, which was *inert*-if-alone.**

**The hazard, byte-grounded at HEAD `b8282564`:**
- The gate is `max()` over escalation rank `AUTO(0) < ASK(1) < DENY(2)` (`gate_level_rule.py:214-221`).
- The composer pins `mcp_trust_tier=MCPTrustTier.LEVEL_0_REFUSE_REMOTE` (`hitl_gate_composer.py:462`) — admissible ONLY while `gate_level()` ignores the field (3-axis composition at HEAD).
- Table A maps `LEVEL_0_REFUSE_REMOTE → DENY` (CP spec v1.35 §19.1.2).
- **Therefore:** if U-CP-98 adds `Axis.MCP_TRUST: MCP_TRUST_GATE_LEVEL_FLOOR[input.mcp_trust_tier]` to `per_axis_floors` while the composer still pins L0, then `MCP_TRUST_GATE_LEVEL_FLOOR[L0] = DENY` enters the `max()` on **every** gate the composer evaluates → **every host-less gate becomes `DENY`** — and this is **broader than "MCP tool gates"**: the composer's `_compute_gate_decision` builds the `GateLevelInput` at `hitl_gate_composer.py:462` for **inference + sub-agent** steps (the only placements wired — `stage_5_loop_init.py:337` `PRE_ACTION` / `:431` `SUB_AGENT_BOUNDARY`; the `:448` binding guard short-circuits only test-fixture/partial bindings, NOT production — confirmed by execution-path read, Codex F2-01), none of which has an owning MCP host. So composing the axis while L0 is pinned DENY-floors every inference/sub-agent gate. This is exactly why U-RT-131 installs a **no-floor default** (L3→AUTO), not a resolved-host feed — see §5.1. **`gate_level()` consumers:** the live production call site `hitl_gate_composer.py:457`; the `test_cxa_pattern_p1.py` CXA-P1 consumer; and `five_axis_composition.py:111` (`compose_five_axis`) — currently **benign** (test-only, no production caller, passes `mcp_trust_tier` through from its input rather than pinning L0, L2-fixture + value-agnostic asserts), so U-CP-98-alone does not break it today. (NB: `five_axis_composition` is the §19.3 D2-layer *sandbox-orthogonal* product — a DIFFERENT composition from the §19.1 D5-layer HITL gate's 4-axis `max()`; the "4-of-4 §19.1 axes" count is not the "5-axis" §19.3 count.)

**Standalone analysis (mirror B3-plan §5, flipped from soft-note to mandatory-pin):**
- **U-CP-98 alone → HARMFUL** (every gate DENY). FORBIDDEN.
- **U-RT-131 alone → harmless** (the composer changes a constant `gate_level()` still ignores at the 3-axis HEAD → no behavior change vs HEAD). Permitted but pointless alone.
- **U-CP-98 ⊕ U-RT-131 together → correct** (the host-less gates compose `MCP_TRUST=AUTO` → no over-gating; `gate_level()` composes 4 axes).

**Encoding (why a build-sequencing pin, not a DAG edge — Codex F1-01 corrected):** the safety constraint is "U-CP-98 must NOT land before U-RT-131." A `U-CP-98 → U-RT-131` dependency edge (U-CP-98 depends-on U-RT-131) WOULD in fact express exactly this ordering (U-RT-131 lands first-or-with). The **load-bearing reason it cannot be a DAG edge** is that such an edge is a **CP→RT cross-axis dependency, forbidden by axis-isolation** — `harness-cp` must not import `harness-runtime` (the package dependency runs RT→CP only). So the ordering is encoded as a **hard build-sequencing pin in §6 + CP plan v2.36 §3.7 / §6 O-CP-6:** U-CP-98 and U-RT-131 land in the **same final impl arc (B2-impl-3)**; U-CP-98 MUST NOT merge in an earlier arc. (U-RT-131 is a leaf — co-landed into B2-impl-3 by the pin, not by topology; B2-impl-3 is the terminal arc regardless, so the pin costs no re-sequencing.)

**Why this is NOT a fork.** Both spec legs are cleared; the impl is conformance to the §19.1 4-axis formula. The hazard is a build-sequencing constraint the planner surfaces, not a spec/contract defect. No back-flow owed. (Surfaced to the operator in the B2-plan deliverable.)

### §5.1 — The composer-architecture sub-finding (why U-RT-131 is a no-floor default, not a resolved-host feed)

Surfaced by the adversarial review (F2-01) + direct composer-architecture re-grounding, advisor-confirmed as a **bounded re-scope of the runtime unit, NOT a Class 1 fork** (mapping onto the ratified **O-CP-3 forward-producer pattern**: an axis composes with a degenerate default while its real producer is registered forward).

**The finding (byte-grounded at HEAD `b8282564`):** the CP §19.1.2 Producer ¶ + runtime §14.8.2 step-4c say the composer populates `GateLevelInput.mcp_trust_tier` "from the resolved owning MCP host's declared trust … via the routing index." But the runtime HITL gate composer (`RuntimeHITLGateComposer`) is constructed at `stage_5_loop_init.py` for **exactly two host-less placements** — `hitl_inference` (`:337`, `PRE_ACTION`) + `hitl_sub_agent` (`:431`, `SUB_AGENT_BOUNDARY`). `TOOL_STEP`s dispatch through `runtime_tool_dispatcher.py`, which composes **no** HITL gate (zero `gate_level`/`GateLevelInput`/`hitl` references). **So no gate site has an owning MCP host** — the §19.1.2 Producer ¶ resolved-host feed has nothing to populate at HEAD.

**The disposition (advisor-confirmed):** §19.1.2 invariant 3 ("floor-only; AUTO contributes nothing to `max()`") licenses the no-floor reading — a host-less gate site legitimately contributes the AUTO-mapping tier. So **U-RT-131 is re-scoped** from "wire the resolved owning host's trust via the routing index" (unmaterializable — no such gate site) to "replace the harmful L0 constant with the L3 no-floor default," mirroring the sibling `per_tool_gate_level` axis the SAME composer construction already defaults to `GateLevel.AUTO` (`hitl_gate_composer.py:453`). U-RT-131 becomes a **leaf** (needs neither the routing index nor the D3 projection — there is no owning host to resolve). The real per-server producer — **a tool-step HITL gate site** that resolves the owning host + feeds its D3-projected `MCPTrustTier` into the gate — is registered as the **`B-TOOL-GATE`** forward BUILD arc (SPINE ledger Bucket B; runtime v2.47 §6 O-RT-7 item 2 / CP v2.36 §6 O-CP-6 item 2). This is the §19.1 *producer*-completeness gap, the exact analog of `per_tool_gate_level`/O-CP-3.

**Why NOT a fork (advisor verdict accepted):** the cleared spec is not defective — §19.1.2 invariant 3 already licenses the no-floor-when-no-host reading; the unmaterializable thing was the *unit's* over-scoped wording, not the spec. Both B2 spec legs stay cleared. No `class_1_fork` filed; reported prominently to the operator. (Per `[[cleared-spec-resolves-it-before-first-principles-fix]]` + `[[grounding-reveals-claude-closeable-slice-close-honestly]]` — the grounding revealed the cleared spec already accommodates the host-less reality; the honest close is the bounded re-scope + the forward producer, not a first-principles Optional-field refactor.)

---

## §6 — B2-impl sequencing

| Arc | Units | What it delivers |
|---|---|---|
| **B2-impl-1** (reshape foundation) | U-RT-125 + U-RT-126 + U-RT-129 | The `mcp_client_hosts` host-dict carrier + `ServerName` + stage-3a all-hosts factory + the D3 identity-by-ordinal projection (retire the constant stub) + the telemetry-only docstring fix. Foundational; no behavior change to single-server deployments (one configured host → a 1-entry dict; the projection now reports the real declared tier in telemetry). |
| **B2-impl-2** (multi-host dispatch) | U-RT-127 + U-RT-128 + U-RT-130 | The cross-host routing index + `RT-FAIL-MCP-TOOL-NAME-COLLISION` fail-loud + dispatcher tool→server resolution + the ~10 consumer reshapes + per-host sandbox resolver/driver. **e2e — reshape:** tool discovery + routing across **≥2 mock MCP servers** (the new fixture) + collision-fail-loud contrasting-baseline. **impl-AC:** run the BROADER suite — the `C-RT-04` `HarnessContext` shape change ripples to cross-axis field-shape asserts + the CXA-P1 enumeration allowlist (`test_cxa_pattern_p1.py`) per `[[shared-is-shape-change-ripples-cross-axis-field-asserts]]`; a single-package run misses both. |
| **B2-impl-3** (gate axis — FINAL; the co-land arc) | **U-CP-98 + U-RT-131 (SAFETY-COUPLED — §5)** | Compose `Axis.MCP_TRUST` into `gate_level()` (CP) AND retire the harmful L0 constant for the host-less gate sites (RT, no-floor default), **in the same arc**. **AC:** the per-tier `L0→DENY…L3→AUTO` table at the **U-CP-98 direct `gate_level()` unit test**; the **production non-regression** baseline — the host-less gate composes `MCP_TRUST=AUTO` → identical to the 3-axis path (no over-gating). Closes the §19.1 4th-axis *composition* (producer-completeness is the forward producers below). |
| **`B-TOOL-GATE` (the real per-server producer)** | tool-step HITL gate site | The §19.1.2 Producer ¶ resolved-owning-host feed; needs a tool-step gate site (the composer gates only host-less inference/sub-agent today). Registered forward (SPINE Bucket B; O-RT-7 item 2 / O-CP-6 item 2); NOT B2. **HIGH** load-bearing — it is what makes the MCP-trust axis non-vacuous in production. |
| **O-CP-3 (when AS-leg opens)** | `per_tool_gate_level` producer | The other degenerate-default §19.1 axis (default-`AUTO`); registered forward, NOT B2. |
| **B2-restart / server-qualified addressing / B6** | — | Registered forward (reshape fork §6); NOT B2. |

---

## §7 — Files written

- `design-substrate/Implementation_Plan_Harness_Runtime_v2_47.md` (delta over v2.46; +7 units U-RT-125..131 + §1 spec-inventory rows + §2.x NEW-units block + §3.1x B2 aggregate DAG nodes + §4.x coverage delta + O-RT open item; all prior content PRESERVED VERBATIM per delta-only-plan-chain convention)
- `design-substrate/Implementation_Plan_Control_Plane_v2_36.md` (delta over v2.35; +1 unit U-CP-98 + §1 spec-inventory row + §2.6 NEW-units block + §3.7 B2 aggregate cross-axis home (the co-land pin) + §4.5 coverage delta + §6 O-CP-6; all prior content PRESERVED VERBATIM)
- `.harness/r-fs-1-b2-plan-decomposition.md` (this summary)
- `.harness/adversarial-review-r-fs-1-b2-plan.md` (the dedicated-agent adversarial review record — APPROVE-WITH-FINDINGS; the F2-01 composer-architecture finding that drove the U-RT-131 re-scope, §5.1)

**Plan-head bumps:** workspace `CLAUDE.md` §2.4 + `.harness/claude-artifact-pointers.md` §2.4 (CP v2.35→v2.36; runtime v2.46→v2.47). **NOT bumped: `harness-cp/CLAUDE.md` §1.2** — its plan-row is stale at `Implementation_Plan_Control_Plane_v2_31.md` (4 versions behind), a **pre-existing drift** that B1/B3/E all left untouched (the axis-subdir CLAUDE.md is not part of the plan-bump precedent). Logged as a **Q1 doc-hygiene drift item** (`[[design-substrate-version-identity-hazards]]`), not corrected in this arc (would be scope-creep + an unrelated edit per the surgical-changes discipline). *(Corrects a Codex P2 over-claim: an earlier draft of this §7 + the runtime/CP footers asserted a harness-cp/CLAUDE.md §1.2 bump that was never made — the claim is dropped here and in both plan footers.)*

**Clearance markers:** `Implementation_Plan_Harness_Runtime-v2_47-cleared-2026-06-16.md` + `Implementation_Plan_Control_Plane-v2_36-cleared-2026-06-16.md` (filed; reviewer_chain references this companion + the adversarial-review record).

**Decorrelated review (DONE):** harness-adversarial-reviewer (dedicated agent adopting the SKILL.md — APPROVE-WITH-FINDINGS, the load-bearing F2-01 composer-architecture finding → the U-RT-131 re-scope, §5.1) + out-of-family Codex (`just codex-review` — 2×[P2]: the harness-cp/CLAUDE.md over-claim [fixed above] + the dead review-file link [fixed by adding the file]) + advisor (transcript-aware — confirmed the F2-01 disposition: bounded re-scope onto the O-CP-3 forward-producer pattern, NOT a Class 1 fork; co-land pin survives). A pre-merge Codex re-run on the final reworked diff is owed (§13.1).
