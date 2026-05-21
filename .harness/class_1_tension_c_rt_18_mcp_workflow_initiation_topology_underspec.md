# Class 1 Tension — C-RT-18 / U-RT-15: MCP workflow-initiation topology underspec

| Field | Value |
|---|---|
| Fork ID | `c_rt_18_mcp_workflow_initiation_topology_underspec` |
| Filed | 2026-05-21 at HEAD `e9b9c49` |
| Filed by | FastMCP transport-level handler arc orientation (operator-chosen path (a) full real-transport arc) |
| Trigger | Verified FastMCP SDK + Claude Code 2.1.76+ both support MCP elicitation. Stable Python SDK API: `ctx.elicit(message, schema) -> ElicitResult{action, data}` inside an in-flight `@mcp.tool()` handler. Elicitation rides outbound on the active server session back to the **caller** of the tool. |
| Class | **Class 1** (halt-execution; architectural defect; design-phase artifact requires revision) |
| Halt scope | FastMCP transport-level handler arc (joint H_T-CP-18 + H_T-CP-20 RETIRED gate). NO halt on the 23-commit stack already pushed to origin/main at `e9b9c49`. |
| Status | **RATIFIED 2026-05-21 at `e9b9c49`** — operator ratified Q1–Q5 as recommended at §9. Next: spec-writer v1.11 → v1.12 absorption + implementation-planner v2.9 → v2.10 absorption + U-RT-62 impl arc → RATIFIED → APPLIED at U-RT-62 landing. |

---

## §1 Defect statement

The 5-Q C-RT-18 binding-mechanism fork (RATIFIED 2026-05-21 at `fb545ec`) pinned the **substitution-mechanism category** at Q1: (i) MCP-server-backed per `Phase_7_Meta_Architecture_v1.md` §5.7. The five questions did **not** address **workflow-initiation topology** — i.e., who is the MCP server, who is the MCP client, and what causes the server's `ctx.elicit` to fire at the moment a HITL gate triggers during a running workflow.

This is structurally under-specified at three jointly-load-bearing sites:

| Site | Reading | Implication |
|---|---|---|
| `Spec_Harness_Runtime_v1.md` v1.11 §14.8.3 line 1596 | *"the runtime emits a tool call through an MCP host … MCP-server-side handler intercepts the call, dispatches to Claude Code's `AskUserQuestion` mechanism"* | Frames H_T as MCP **client** (emits tool call). |
| `Implementation_Plan_Harness_Runtime` v2.9 §2 L3 U-RT-15 (line 236) | *"instantiate FastMCP host; connect configured MCP clients"* | Pins H_T-side as a **consumer** of external MCP servers. |
| `Phase_7_Meta_Architecture_v1.md` §5.7 | *"MCP server-side authoring (FastMCP + Pydantic + OTel SDK)"* | Silent on whether the server-side code is H_T-hosted or external. AS-AL-2 *"all H_T tool surface lives behind MCP server boundary"* pins **where tool surface lives**, not **who initiates** when H_T consumes one. |

## §2 Protocol-level constraint that surfaces the defect

Per stable FastMCP Python SDK (`/modelcontextprotocol/python-sdk` v1.12.4, verified via context7 2026-05-21):

```python
@mcp.tool()
async def some_tool(arg: str, ctx: Context[ServerSession, None]) -> str:
    result = await ctx.elicit(message=..., schema=PydanticModel)
    if result.action == "accept": ...
```

`ctx.elicit` is available **only inside an in-flight `@mcp.tool()` handler**. The elicitation request rides outbound on the active server session and is delivered back to the **caller of that tool** — not to an arbitrary third party. There is no protocol-level path for an MCP server to push an elicitation request to a non-caller (e.g., Claude Code if H_T is the client that called the tool).

Claude Code 2.1.76 (March 2026) honors `elicitation/create` requests **as an MCP client** — i.e., Claude Code can receive elicitation requests **when it has called a tool on an MCP server that uses `ctx.elicit`**. Claude Code does NOT expose AskUserQuestion as an MCP tool callable by other parties.

Joint constraint: for the spec §14.8.3 chain *"runtime emits tool call → server handler intercepts → dispatches to Claude Code's AskUserQuestion"* to be realizable through MCP-canonical primitives, **Claude Code must be the caller of the tool, not the recipient of a side-channel dispatch**. This reverses the spec line 1596 framing.

## §3 Candidate readings (α / β / γ / δ)

Per advisor reconciliation at this fork's orientation turn:

### §3.1 Reading (α) — CC-initiates topology

- **Mechanism.** H_T runtime hosts a FastMCP server. Claude Code is registered as MCP client. Every workflow is invoked by Claude Code calling a tool (e.g., `run_workflow(workflow_id, ...)`) on H_T's server. The workflow body executes inside the tool handler's `ctx`. When HITL fires, `ctx.elicit(...)` rides the active session back to Claude Code, which renders the dialog, captures the operator response, and returns it to H_T.
- **Pro.** Clean — uses MCP elicitation as protocol-canonically intended. No side channels. Strong X-AL-1 process-isolation discipline.
- **Con.** Reverses the current H_T `run()` library-style entrypoint posture (per the U-RT-15 framing + the existing `harness-runtime/api.py:run()` operator-facing surface per Track B). The runtime becomes CC-initiated only — H_T cannot be invoked as a standalone Python library.
- **Sub-arc cost.** Substantial: design + land a `run_workflow` MCP tool on H_T's side; refactor `api.py:run()` to either delegate to the MCP path or be deprecated; CC `.mcp.json` configuration; U-RT-15 scope amendment (s/"connect configured MCP clients"/"host FastMCP server + accept CC client"/).

### §3.2 Reading (β) — H_T-initiates with persistent callback session

- **Mechanism.** H_T runtime starts both: (1) the Python `run()` library entrypoint as before, (2) a long-lived FastMCP server in the background. Claude Code connects to the server. When HITL fires inside a running workflow, the workflow pushes a request onto an internal queue + awaits an `asyncio.Future`. A second FastMCP tool (e.g., `next_hitl_prompt` polled by CC, or a server-initiated notification CC subscribes to) delivers the prompt; CC renders it (via what mechanism?); CC calls a third tool `deliver_hitl_response(prompt_id, response)`; the runtime resolves the Future.
- **Pro.** Preserves the library-style `run()` entrypoint.
- **Con.** Non-standard MCP pattern. Requires CC to poll OR subscribe to notifications. Requires CC to render the prompt via something (which something?) since the elicitation is initiated by H_T not by CC's tool call. May require Claude Code feature surface that doesn't exist.
- **Sub-arc cost.** Higher than (α); off-spec from MCP protocol intent; likely drifts to Class 1 again at impl-time.

### §3.3 Reading (γ) — Out-of-band

- **Mechanism.** Stdout-marker JSON protocol; webhook; HTTP server with CC polling; custom non-MCP transport.
- **Con.** Directly contradicts the C-RT-18 Q1 ratification (mechanism-category pinned at MCP-server). Reverts past a binding-mechanism fork already ratified. Off-spec.
- **Sub-arc cost.** Re-opens Q1 of the C-RT-18 binding-mechanism fork; spec §14.8.3 amendment required.

### §3.4 Reading (δ) — Hybrid: bootstrap library-style + workflow-time MCP-initiated

- **Mechanism.** H_T runtime hosts a FastMCP server. CC is the client. Operator can either (a) call `run_workflow` from CC (= reading (α)), or (b) start the runtime as a long-lived process via `python -m harness_runtime serve` (a *bootstrap*-style entrypoint that does not run workflows but services them). At workflow time, every workflow must be invoked through the MCP tool — there is no `run()` Python library entrypoint for workflow execution. The MCP path is the only workflow-execution path.
- **Pro.** Sharper than (β): the `run()` library entrypoint is reframed as **server-process startup**, not as **workflow execution**. The workflow-execution entrypoint is the MCP tool, matching (α) for HITL purposes.
- **Con.** Same as (α) for workflow-execution topology; library-style workflow invocation deprecated.
- **Sub-arc cost.** Similar to (α); cleaner ramp because the library entrypoint is preserved for server-process startup.

## §4 Operator-surface decision questions

### §4.1 Q1 — Workflow-initiation topology selection

Which of the 4 candidate readings backs the v1.12 H_E binding of `AskUserQuestionSurface` at production execution path?

**Default recommendation (architect mode 3 pending):** Reading (α) or (δ). Reading (β) drifts toward off-spec; reading (γ) contradicts the C-RT-18 Q1 ratification.

### §4.2 Q2 — Library-style `run()` entrypoint disposition

Under (α) or (δ), is the current `harness-runtime/api.py:run()` library-style workflow-execution entrypoint:

- (a) Deprecated entirely (CC-initiated only).
- (b) Preserved for non-HITL workflows only (workflows that declare zero HITL placements can run via `run()`; workflows with HITL placements MUST run via MCP path).
- (c) Preserved as a thin wrapper that internally invokes the MCP path (CC must be running for `run()` to function).
- (d) Preserved alongside the MCP path; HITL gate composer detects which path is active and either uses `ctx.elicit` (MCP path) or some other surface (library path).

### §4.3 Q3 — U-RT-15 scope amendment

U-RT-15 v2.9 scope reads "instantiate FastMCP host; connect configured MCP clients" (= H_T-as-client). Under (α) / (δ), U-RT-15 needs amendment to add: "host a FastMCP server; expose workflow-execution tool(s); accept CC client connection." Is this a U-RT-15 amendment (Phase 6 plan revision), or is it a new sibling unit (U-RT-NN)?

### §4.4 Q4 — `MCPHost` schema reconciliation

The current `harness-runtime/lifecycle/mcp_host.py` `MCPHost` dataclass has a single `started: bool` field (L3 placeholder). Under (α) / (δ), the `MCPHost` needs to carry **both** a server reference (the FastMCP `mcp` instance) AND a client-connection registry (the existing `MCPClient` clients). Is this:

- (a) A schema extension to `MCPHost` (add `server: FastMCP | None` field).
- (b) A new sibling primitive (`MCPServerHost` distinct from the existing `MCPHost`).
- (c) Defer to the spec amendment that ratifies Q1.

### §4.5 Q5 — Retirement event re-classification at fork APPLIED

H_T-CP-20 is currently RETIRE-READY (per batch 8). Under (α) / (δ) APPLIED, does CP-20 → RETIRED gate also on:

- (a) `run_workflow` tool registered + CC connection verified.
- (b) End-to-end test of CC → `run_workflow` → HITL fire → `ctx.elicit` → response → workflow continuation.
- (c) Operator manual verification at one real workflow execution.

And does H_T-CP-18 (MCP integration + per-server trust + `mcp.*` consumption) advance to RETIRED jointly, or does it gate separately on real client-connection verification (since under (α) H_T is server, not client — and CP-18's substitution covers H_T-as-MCP-client surface, possibly orthogonal)?

## §5 Authority-chain traceability

Per workspace `CLAUDE.md` §1.3 authority chain (ADR → ADD → PRD → spec → plan → CXA → execution):

| Artifact | Touched by this fork | Touched-how |
|---|---|---|
| ADR-D1 v1.2 (HITL primitive) | NO | HITL primitive design at ADR layer is satisfied at the H_T API surface; this fork is downstream of ADR. |
| ADR-D6 v1.2 (OTel schema) | NO | Span emission shape unaffected — `hitl.*` / `audit.*` namespaces orthogonal to MCP topology. |
| `Architectural_Design_Document_v1_3.md` | POSSIBLY | If (α)/(δ) ratified, the ADD §… runtime architecture section may need amendment to add the CC-initiated workflow-execution topology. Class 1 sub-amendment to verify at architect mode 3 resolution. |
| `Spec_Harness_Runtime_v1.md` v1.11 | **YES** | §14.8.3 narrative requires Form A NOTE-form amendment at minimum (or material amendment if (α)/(δ) ratified) to pin workflow-initiation topology. |
| `Implementation_Plan_Harness_Runtime` v2.9 | **YES** | U-RT-15 scope amendment per Q3 above. Possible new sibling unit U-RT-NN per Q3 (b). |
| `Cross_Axis_Composition_Document_v2_5.md` | NO | No new CXA edges expected — HITL composer + audit emission already covered at §2.3.7 CP→OD 2-seam bucket. |

## §6 Fork-resolution sequence (recommended)

1. **architect mode 3 5-Q resolution** per workspace `CLAUDE.md` §4.3 Class 1 routing → systems-architect skill activation against Q1–Q5 above. Chain-grounded recommendation produced.
2. **Operator ratification** at the architect-mode-3 recommendation surface.
3. **Spec amendment** at spec v1.11 → v1.12 by spec-writer skill, absorbing the ratified Q1–Q5 resolution.
4. **Plan amendment** at runtime plan v2.9 → v2.10 by implementation-planner skill, absorbing Q3 + Q4 + Q5.
5. **(Optional)** ADD §… amendment if Q1 ratification implies runtime-topology architecture extension.
6. **Implementation arc** opens against the v1.12 / v2.10 substrate.

Estimated turn count: 5–8 turns to ratification; 1–2 turns to spec amendment; 1 turn to plan amendment; then the FastMCP transport-level handler arc opens against the amended substrate.

## §7 Anti-leakage compliance + carry-forward classification

| Rule | Compliance |
|---|---|
| X-AL-1 (H_E ↔ H_T boundary at MCP server process; process isolation, not convention) | **HONORED by halt.** All 4 readings preserve MCP server process isolation; halt prevents convention-only resolution. |
| X-AL-2 (substitution retirement = (units landed) ∧ (surface no longer invoked); partial = non-retirement) | **HONORED.** H_T-CP-20 remains RETIRE-READY (per batch 8); does NOT advance to RETIRED prematurely. |
| X-AL-3 (no silent H_T design extension at Phase 7) | **HONORED by halt.** Silent commit to (α) without operator ratification would be the trap; halt + Class 1 filing surfaces the design extension. |
| CP-AL-1 (H_E sub-agent topology ≠ H_T CP-axis topology pattern) | **NOT IMPLICATED.** |

## §8 Filing footer

| Field | Value |
|---|---|
| Filed | 2026-05-21 at HEAD `e9b9c49` (worktree-u-rt-52-close, also at origin/main per the 23-commit stack push earlier this session) |
| Predecessor fork | `class_1_tension_c_rt_18_ask_user_question_surface_binding_mechanism_underspec.md` (RATIFIED 2026-05-21 at `fb545ec` — Q1 pinned mechanism category (i) MCP-server; Q1–Q5 did NOT address workflow-initiation topology) |
| Sibling fork | `class_1_tension_c_rt_18_hitl_span_attribute_carrier_drift.md` (RESOLVED at `9b6b007`) |
| Sibling fork | `class_1_tension_u_rt_60_wrap_asymmetry_sync_async_mismatch.md` (APPLIED at `e9b9c49` — this arc's predecessor) |
| Status | OPEN — pending architect mode 3 5-Q resolution + operator ratification |
| Blocks | FastMCP transport-level handler implementation arc (joint H_T-CP-18 + H_T-CP-20 RETIRED gate) |
| Does NOT block | Other Phase 7d retirement-batch arcs at unaffected substitutions (e.g., PRICE_TABLE_REF rate-table at OD-5; Q6 systemic-pattern skill-extension arc) |

*Halt filed per workspace `CLAUDE.md` §4.3 Class 1 routing discipline + advisor reconciliation 2026-05-21 (verified C-RT-18 binding-mechanism fork was silent on workflow-initiation topology; verified Meta-Arch §5.7 is silent on H_T-as-server vs H_T-as-client; surfaced load-bearing protocol-level constraint that `ctx.elicit` only fires inside in-flight tool handlers). Architecture decision is real, load-bearing, and not derivable from existing chain artifacts without re-ratification.*

---

## §9 Systems-architect mode 3 resolution recommendation

*Filed 2026-05-21 by `systems-architect` skill mode 3 against the 5-Q chain at §4. Per skill §4A.4: this is a recommendation, NOT a decision; operator holds decision authority and may counter-propose with a chain-grounded alternative reading. Per skill §4A.2 procedure: chain-grounded against the canonical authority chain at workspace `CLAUDE.md` §1.3 — earlier-in-chain artifacts canonical for later.*

### §9.1 Tension restatement (per §4A.2 step 1)

Three divergent artifacts:

| Artifact | Quote | Implied topology |
|---|---|---|
| `Spec_Harness_Runtime_v1.md` v1.11 §14.8.3 line 1596 | *"the runtime emits a tool call through an MCP host … MCP-server-side handler intercepts the call, dispatches to Claude Code's `AskUserQuestion` mechanism"* | H_T-as-client (emits tool call) |
| `Phase 2 Session 3 Track A atomic-decomposition` v2.9 §2 L3 U-RT-15 (line 236) | *"instantiate FastMCP host; connect configured MCP clients"* | H_T-as-client (consumes MCP servers) |
| `Phase_7_Meta_Architecture_v1.md` §5.7 + §7 (X-AL-1 + AS-AL-2) | *"MCP server-side authoring (FastMCP + Pydantic + OTel SDK)"* + *"H_E ↔ H_T substrate boundary at MCP server process; process isolation, not convention"* + *"all H_T tool surface lives behind MCP server boundary"* | Implicitly H_T-as-server (authors server-side; tool surface server-side) |

The protocol-level constraint (verified at `/modelcontextprotocol/python-sdk` v1.12.4 via context7 + Claude Code 2.1.76 release notes 2026-03-14): `ctx.elicit(message, schema)` is available **only inside an in-flight `@mcp.tool()` handler**, and the elicitation request rides outbound on the active server session to the **caller of that tool**. There is no protocol-level path for an MCP server to push elicitation to a non-caller. **Claude Code is an MCP client only**; it does NOT expose AskUserQuestion as an MCP tool. Therefore the spec line 1596 chain *"server handler dispatches to Claude Code's AskUserQuestion"* is realizable through standard MCP **only if Claude Code is the caller of the tool** — i.e., the H_T-as-client framing at the spec + plan is the loose reading; the H_T-as-server framing at Meta-Architecture §7 is the protocol-canonical reading.

### §9.2 Authority-chain placement (per §4A.2 step 2)

| Authority-chain layer | What it says on topology | Direction |
|---|---|---|
| ADR (F1–F5 + D1–D6) | Silent on MCP topology direction (all 11 ADRs scanned) | — |
| `Architectural_Design_Document_v1_3.md` | Silent on MCP topology direction (grep `MCP|mcp|FastMCP` returned no hits at substantive sections) | — |
| `PRD_v1_1.md` | Silent on MCP topology direction (grep returned no substantive hits) | — |
| `Phase_7_Meta_Architecture_v1.md` §5.7 + §7 (X-AL-1 + AS-AL-2) | Server-side authoring; process isolation at MCP server boundary; all H_T tool surface lives behind MCP server boundary | **Supports H_T-as-server** |
| `Spec_Harness_Runtime_v1.md` v1.11 §14.8.3 line 1596 (later in chain) | Runtime emits tool call (client-side) | Supports H_T-as-client (loose prose) |
| `Implementation_Plan_Harness_Runtime` v2.9 §2 L3 U-RT-15 (later in chain) | Instantiate host; connect configured clients | Supports H_T-as-client |

Per `CLAUDE.md` §1.3 chain discipline: **Meta-Architecture is earlier in the chain than spec and plan**. Where the chain disagrees, the earlier artifact wins. **The Meta-Architecture reading (H_T-as-server) is canonical**; the spec line 1596 + plan U-RT-15 readings are downstream drifts that the spec-writer + implementation-planner must absorb at amendment time.

### §9.3 §2 cross-mode discipline application (per §4A.2 step 3)

**Five-axis decomposition.**

- **Control plane** — the topology decision governs how the runtime is initiated and how HITL gates rejoin the operator turn. Q1 + Q2 + Q5 axis-touch.
- **Information substrate** — `MCPHost` schema reconciliation is an IS-axis-internal carrier shape decision. Q4 axis-touch.
- **Action surface** — the FastMCP server is itself a tool surface that the runtime publishes; the elicitation primitive rides on the action-surface session. Q3 axis-touch.
- **Operational discipline** — span emission + audit-entry composition + retry interaction are unaffected by topology choice (the wrap chain at stage 5 is downstream of the surface; the surface's Protocol contract is unchanged across topology readings). NO axis-touch under (α) or (δ).
- **Deployment surface** — under (α), workflow execution requires CC running. Under (δ), the runtime may also run server-only without workflow execution. Q2 + Q5 axis-touch.

**Probabilistic-deterministic boundary.** The HITL elicitation surface is deterministic (the operator's response is captured through MCP elicitation Protocol; the schema enforces 4-response palette + content fields). Topology choice doesn't move the boundary; it only changes the carrier session shape.

**Decision ordering.** This decision is **F-level** at the runtime-topology layer (it commits the runtime's deployment shape). Downstream D-level decisions (test fixture shape, MCPHost schema split) flow from this F-level commitment.

**Cross-axis verification.** No cross-axis tensions surfaced. CXA edges at v2.5 §2.3.7 (CP→OD 2-seam bucket) are downstream of the wrap chain at stage 5; the topology decision is upstream of the wrap chain (it touches construction, not span/audit emission).

### §9.4 Recommendations per Q1–Q5

#### Q1 — Workflow-initiation topology

**Recommendation: Reading (α) — CC-initiates topology.** [HIGH]

**Chain citation:**
- `Phase_7_Meta_Architecture_v1.md` §7 X-AL-1 (line 488–489): *"H_E ↔ H_T substrate boundary at MCP server process; process isolation, not convention."* The boundary is held at MCP server process. For elicitation to flow back to CC (the only entity holding AskUserQuestion), CC must be the caller — i.e., H_T is the server.
- `Phase_7_Meta_Architecture_v1.md` §7 AS-AL-2 (line 522): *"All H_T tool surface lives behind MCP server boundary."* The workflow execution surface IS H_T tool surface; therefore it lives behind H_T-as-server boundary.
- `Phase_7_Meta_Architecture_v1.md` §5.7 line 418: *"MCP server-side authoring (FastMCP + Pydantic + OTel SDK)"* — server-side authoring as the category name implies H_T-side authors server-side code (i.e., H_T hosts the server).
- Protocol-level constraint (FastMCP `ctx.elicit` only fires inside in-flight tool handler; Claude Code is MCP-client only): only (α) is physically realizable through standard MCP.

**Reinforcing:** Reading (γ) directly contradicts the C-RT-18 Q1 ratification (mechanism category (i) MCP-server). Reading (β) is non-standard MCP and would surface its own Class 1 at impl-time (which protocol-level primitive supports server-initiated push to non-caller?). Reading (δ) is (α) + library-bootstrap reframe — addressed at Q2 (it is a Q2 variation on top of (α), not a separate Q1 reading).

**Operator counter-propose surface:** If operator's reading of X-AL-1 differs (e.g., reads "process isolation" as permitting a non-MCP transport that nonetheless isolates by process), the recommendation flips — but that re-reading would require an X-AL-1 amendment first (workflow revision per `phase-7-back-flow-routing` skill §3.1 routing table → workflow channel; substantially bigger arc). Such a re-reading was already considered + rejected at the C-RT-18 binding-mechanism fork Q1 ratification 2026-05-21.

**Tiebreaker:** Single verifiable fact — confirm `Phase_7_Meta_Architecture_v1.md` §7 X-AL-1 "process isolation, not convention" has NOT been amended post the C-RT-18 binding-mechanism fork ratification at `fb545ec`. Verified at this filing: workspace `CLAUDE.md` §8 invariant I-4 reads the original wording without amendment as of HEAD `e9b9c49`. ✓

#### Q2 — `run()` entrypoint disposition under (α)

**Recommendation: Option (c) — preserve `api.py:run()` symbol as a thin wrapper that internally invokes the MCP-tool path.** [MODERATE]

**Chain citation:**
- `Spec_Harness_Runtime_v1.md` C-RT-08 contract: `run()` is the Track A operator-facing API at v1.0+ baseline. Preservation aligns with Track A continuity.
- Test substrate carrier-preservation: `harness-runtime/tests/test_bootstrap.py:750` + multiple other call sites consume `from harness_runtime.api import run` directly. Carrier-preservation per `[[spec-prose-plan-body-drift-pattern]]` discipline favors option (c) over option (a) deprecation.
- X-AL-3 (no silent H_T design extension): option (d) "preserved alongside MCP path with gate composer detection" requires a second AskUserQuestionSurface impl that does NOT use `ctx.elicit` (library path has no in-flight ctx). That second impl drifts toward convention-only (stdin prompt / Bash subshell / etc.), directly contradicting X-AL-1. Option (d) is contraindicated.

**Trade-off acknowledged:** Option (c) requires `run()` callers to be in-process with a running MCP host. The wrapper materializes an in-process MCP client + invokes the workflow-execution tool. For tests, this becomes an in-process FastMCP client + server pair (standard pattern — see SDK quickstart). The MCPHost schema (Q4) must accommodate.

**Operator counter-propose surface:** Option (a) "deprecate `run()` entirely" is also defensible (cleaner contract; smaller surface). Operator may choose (a) if the workflow-execution-via-MCP-only deployment posture is preferred and the test substrate refactor cost is acceptable. The chain doesn't pin between (a) and (c); the recommendation defaults to carrier-preservation.

**Tiebreaker:** Single verifiable fact — confirm `harness-runtime/tests/` has ≥3 direct callers of `api.run()` (test_bootstrap.py + integration tests). Verified at this filing: 4 test files import `api.run` directly; 5 use lower-level `execute_workflow` / `run_bootstrap`. ✓ Carrier-preservation supports (c).

#### Q3 — U-RT-15 scope amendment vs new sibling unit

**Recommendation: Option (b) — new sibling unit `U-RT-62` (next free slot; U-RT-60 = HITL gate composer, U-RT-61 = C-RT-19 durable-async swap).** [HIGH]

**Chain citation:**
- `Phase 2 Session 3 Track A atomic-decomposition` v2.9 §2 L3 U-RT-15 scope: *"instantiate FastMCP host; connect configured MCP clients"* — purely H_T-as-client framing. Extending the scope to also cover H_T-as-server hosting would violate the atomicity discipline at `implementation-planner` skill (per per-unit-atomic-scope discipline).
- U-RT-15 represents the H_T-as-client surface (the runtime consumes OTHER MCP servers — e.g., filesystem, GitHub, sandbox MCP servers per AS-axis spec). The new requirement (H_T-as-server hosting workflow execution + elicitation surface) is a structurally different MCP role.
- Both roles need to coexist eventually (under (α) APPLIED, H_T is a server for CC AND a client for other-purpose MCP servers).

**Sub-arc cost:** U-RT-62 scope: instantiate FastMCP server (`mcp.server.fastmcp.FastMCP` instance); register `run_workflow` tool with the workflow-execution adapter body; bind CC client connection (registered via `.mcp.json` at deployment); MCPHost (or new `MCPServerHost` per Q4) schema field. ACs: server.started=True at bootstrap; tool callable from a registered client; elicitation primitive available inside the tool handler ctx.

**Operator counter-propose surface:** Operator may prefer option (a) "amend U-RT-15 scope" to keep the FastMCP-host-related units co-located. Trade-off: U-RT-15 becomes a fat unit with two MCP roles bundled; atomicity hurt; future per-role retirement events become awkward.

**Tiebreaker:** Single verifiable fact — confirm runtime plan v2.9 §3 dependency-graph topology does not constrain unit numbering at U-RT-62 slot. Verified at this filing: §3 dependency-graph is topological-sort-ordered, not slot-restricted; U-RT-62 is a free slot. ✓

#### Q4 — `MCPHost` schema reconciliation

**Recommendation: Option (b) — new sibling primitive `HarnessMCPServer` (or `MCPServerHost`) distinct from the existing `MCPHost`.** [HIGH]

**Chain citation:**
- Current `harness-runtime/lifecycle/mcp_host.py:57-66` `MCPHost` represents the H_T-as-MCP-client host (per the L3 docstring + the dataclass shape `started: bool = False` + the MCPStage composition with `clients: dict[ClientName, MCPClient]`). The existing primitive is purpose-built for H_T-as-client.
- Conflating H_T-as-server (the new requirement under (α)) into the same primitive violates SRP — the two represent different MCP roles. `MCPHost` should remain client-side; a new `HarnessMCPServer` (or equivalent) carries the server-side responsibility.
- HarnessContext schema extension: gains a new field `mcp_server: HarnessMCPServer | None` (analog to existing `mcp_host: MCPHost | None`). Bootstrap stage 2 (AS sub-bootstrap) materializes both.

**Sub-arc cost:** New dataclass + materialize helper at the MCPServerHost or at a new module (`harness-runtime/lifecycle/mcp_server.py`). Bootstrap stage 2 extension; HarnessContext field; pyright + test substrate updates.

**Operator counter-propose surface:** Operator may prefer option (a) "schema extension to MCPHost" to keep the topology primitives co-located. Trade-off: same SRP violation as Q3 (a). The field would still need a discriminator (`is_server: bool` or similar) — adds complexity.

**Tiebreaker:** Single verifiable fact — confirm `MCPHost` is consumed at locations OTHER than the bootstrap stage 2 materializer + stage 5 MCP-backed surface construction. Verification: `grep -rn "MCPHost" harness-runtime/src/` shows consumption at stage 2 materializer + stage 5 binding + the placeholder MCP-backed surface field. Bounded blast radius; the schema split is local. ✓

#### Q5 — Retirement event re-classification at fork APPLIED

**Recommendation: H_T-CP-20 RETIRE-READY → RETIRED gate on (a) + (b) jointly. H_T-CP-18 does NOT advance jointly under (α).** [HIGH]

**Chain citation:**
- X-AL-2 (`Phase_7_Meta_Architecture_v1.md` §7.7): *"Retirement = (cited unit IDs landed) ∧ (substituted H_E surface no longer invoked at substitution site). Both conditions required."*
- Under (α), CP-20's substitution site is `await ctx.ask_user_question_surface.ask(...)` at the composer body. Criterion B verification requires:
  - (a) `HarnessMCPServer` registered + `run_workflow` tool callable + CC connection verified at runtime → criterion A condition (cited unit IDs landed).
  - (b) End-to-end test exercising CC → `run_workflow` MCP tool call → workflow execution → HITL fire → `ctx.elicit` outbound → operator response → workflow continuation → audit + span emission → workflow result returned → criterion B condition (the H_E surface is now reached via the MCP envelope; the spec-substituted `AskUserQuestion`-direct call is no longer invoked).
- Option (c) "operator manual verification" is supplementary; not reproducible in CI; not sufficient as the retirement criterion.
- **H_T-CP-18 substitution-site analysis:** CP-18 covers "MCP integration + per-server trust + `mcp.*` consumption" per `Phase_7_Meta_Architecture_v1.md` §5 line 124. CP-18's substitution site is H_T-as-client surface (the runtime consumes other MCP servers; per-server trust framework). Under (α), the new FastMCP server hosting workflow execution is H_T-as-server surface — orthogonal to CP-18's H_T-as-client substitution site. **CP-18 retirement remains a separate arc** gated on per-server-trust framework landing + `mcp.*` namespace emission at H_T-as-client surface (per `harness-as.mcp_transport_floor` consumer-side).

**Trade-off acknowledged:** The fork at §1 originally framed "joint H_T-CP-18 + H_T-CP-20 RETIRED gate." This recommendation revises that framing: CP-20 advances under (α) APPLIED; CP-18 does NOT advance. The carry-forward at batch 8 §3 ("Coupled with H_T-CP-18 retirement (MCP integration + per-server trust); both substitutions advance to RETIRED at that arc landing") is **inaccurate** under (α) and should be amended at the next retirement-event-batch record.

**Operator counter-propose surface:** Operator may argue CP-18 advances jointly under a reading where the H_T-as-server surface IS within CP-18's substitution coverage. Recommendation declines: §5 line 124 H_T-CP-18 substitution row primitive description is "MCP integration + per-server trust + `mcp.*` consumption" — *consumption* is the client-side surface, not the server-side. (Operator may amend Meta-Arch §5 line 124 if a broader CP-18 reading is preferred — that would be a Class 1 Meta-Arch revision; bigger arc.)

**Tiebreaker:** Single verifiable fact — confirm Meta-Arch §5 line 124 H_T-CP-18 substitution row body text reads "MCP integration + per-server trust + `mcp.*` consumption" verbatim. Verified at this filing: line 124 reads `"| H_T-CP-18 | MCP integration + per-server trust + mcp.* consumption | C-CP-18 §18 | U-CP-45 | AS consumer |"`. ✓ Consumption = client-side per row body.

### §9.5 Downstream artifacts that must absorb the resolution

Per §4A.2 step 4 — identify downstream artifacts; do NOT edit (that is spec-writer + implementation-planner work after sign-off):

| Artifact | Scope of absorption | Skill |
|---|---|---|
| `Spec_Harness_Runtime_v1.md` v1.11 → v1.12 | §14.8.3 narrative amendment: pin workflow-initiation topology (α); replace "the runtime emits a tool call through an MCP host" with the protocol-canonical framing ("Claude Code, as MCP client, invokes the H_T-hosted workflow-execution tool; the workflow body runs inside the tool handler; HITL gates use `ctx.elicit` to ride elicitation outbound on the active session back to CC"); §14.8 deferred-list "AskUserQuestionSurface construction timing" entry updated. Form A NOTE-form vs material amendment per spec-writer discretion. | `spec-writer` |
| `Implementation_Plan_Harness_Runtime` v2.9 → v2.10 | Add new sibling unit U-RT-62 per Q3 recommendation; ACs per Q3 sub-arc cost paragraph; dependency-graph row at §3 (U-RT-62 after U-RT-15 + U-RT-25 + U-RT-60); §6.5 substitution table row for "MCP server hosting (workflow tool + elicitation)" → U-RT-62; CXA edges unchanged. Optional: U-RT-15 change-note clarification that scope is preserved verbatim (no amendment); the new server-side responsibility lives at U-RT-62. | `implementation-planner` |
| `harness-runtime/lifecycle/mcp_host.py` (CODE) | NOT edited at this resolution turn. Edit lands at U-RT-62 implementation arc per Q4 recommendation (new `HarnessMCPServer` primitive). | (impl arc) |
| `harness-runtime/api.py` (CODE) | NOT edited at this resolution turn. Reframe to "thin wrapper invoking MCP path" lands at U-RT-62 implementation arc per Q2 recommendation. | (impl arc) |
| `harness-runtime/src/harness_runtime/lifecycle/mcp_backed_ask_user_question_surface.py` (CODE) | NOT edited at this resolution turn. The `_PlaceholderMCPCallback` is replaced with a `ServerCtxElicitCallback` (binds to the in-flight `ctx` of the workflow-execution tool handler) at U-RT-62 impl arc. | (impl arc) |
| `.harness/phase-7d-retirement-events-batch-8.md` | Carry-forward language amendment: §3 "Coupled with H_T-CP-18 retirement" reading revised per Q5 (CP-18 does NOT advance jointly under (α)). Forward-only ledger discipline per workspace `CLAUDE.md` §4.3 — amendment lands at next batch (batch 9) record, not retroactive edit. | (next retirement-batch turn) |
| `workspace CLAUDE.md` §1.1 | If `MCPHost` schema split per Q4 (b), add `harness-runtime/lifecycle/mcp_server.py` (or equivalent) pointer at §2.5 per-axis subdirectory CLAUDE.md (under harness-runtime via new path). Form A absorption owed at U-RT-62 landing. | (impl arc) |

### §9.6 Tiebreaker check (per §4A.2 step 5)

The single verifiable fact that, if confirmed, makes the **overall** recommendation determinate across Q1–Q5:

> Confirm `Phase_7_Meta_Architecture_v1.md` §7 X-AL-1 "process isolation, not convention" reading has NOT been amended post the C-RT-18 binding-mechanism fork ratification at `fb545ec` (RATIFIED 2026-05-21).

Verified at this filing 2026-05-21 at HEAD `e9b9c49`: workspace `CLAUDE.md` §8 invariant I-4 (the in-workspace pointer to X-AL-1) reads the original "process isolation, not convention" wording verbatim without amendment. ✓

**This recommendation is LOAD-BEARING at the `CLAUDE.md` invariant I-4 layer.** It requires explicit operator sign-off per §4A.2 step 5 ("if the recommendation touches a load-bearing artifact, flag that it requires explicit operator sign-off").

### §9.7 Fork classification (per §4A.2 step 6)

Per `Project_Workflow_v1_8.md` §2.7.6:

| Class | Trigger | Routing |
|---|---|---|
| **Class 1 (halt-execution)** ✓ | Architectural defect; design-phase artifact (spec + plan) requires revision before Phase 7 execution proceeds | Halt; route to design-phase channels: spec v1.11 → v1.12 (Q1 + Q5 absorption); plan v2.9 → v2.10 (Q3 + Q4 absorption); re-clearance at v1.12 + v2.10 → FastMCP transport-level handler implementation arc opens |

**Class 1 confirmed.** Halt of the FastMCP transport-level handler implementation arc remains in effect until v1.12 + v2.10 land. NO halt on:
- The 23-commit stack already pushed to `origin/main` at `e9b9c49`.
- Other Phase 7d retirement-event arcs at unaffected substitutions (PRICE_TABLE_REF rate-table at OD-5; Q6 systemic-pattern skill-extension arc; per-axis CLAUDE.md count-drift reconciliation).
- The 6 OPEN Class 3 carry-forwards filed at the U-RT-60 wrap-asymmetry fork landing.

### §9.8 Operator-decision-authority marker

Per `systems-architect` skill §4A.4: **the operator holds decision authority.** The above recommendations are grounded against the authority chain; the operator may ratify any subset, counter-propose with a chain-grounded alternative reading (including X-AL-1 amendment per Q1 operator counter-propose surface), or escalate any of the 5 questions for further deliberation.

**Sequence at operator ratification:**

1. Operator ratifies Q1 (topology direction) — chain-canonical reading (α).
2. Operator ratifies Q2 (run() disposition) — recommendation (c) or counter-proposes (a).
3. Operator ratifies Q3 + Q4 (U-RT-62 sibling unit + MCPServerHost sibling primitive) — recommendation (b) for both.
4. Operator ratifies Q5 (retirement scope) — CP-20 only under (α); CP-18 separate arc.
5. Filing of ratified resolution → `spec-writer` skill invocation against v1.11 → v1.12 amendment → `implementation-planner` skill invocation against v2.9 → v2.10 amendment → FastMCP transport-level handler implementation arc opens against the amended substrate.

Anticipated turn count: 5 ratification turns (one per Q) → 1 spec-writer turn → 1 implementation-planner turn → impl arc opens. Total ~7 turns to unblock impl arc.

---

*End of §9 systems-architect mode 3 resolution recommendation. Recommendation produced per `systems-architect` skill §4A procedure; no decision made; no artifact edited; operator holds decision authority.*

---

## §10 Operator ratification footer

| Field | Value |
|---|---|
| Ratified at | 2026-05-21 at HEAD `e9b9c49` |
| Ratified by | Operator (this session) |
| Ratification scope | Q1–Q5 ratified verbatim per §9.4 recommendations |
| Q1 ratified reading | **(α) CC-initiates topology** — H_T hosts FastMCP server; CC is client; workflow body runs inside `run_workflow` tool handler; `ctx.elicit` rides active session back to CC |
| Q2 ratified reading | **(c) preserve `api.run()` symbol as thin wrapper** invoking MCP-tool path internally |
| Q3 ratified reading | **(b) new sibling unit U-RT-62** (U-RT-15 H_T-as-client scope preserved verbatim) |
| Q4 ratified reading | **(b) new `HarnessMCPServer` primitive** distinct from `MCPHost` |
| Q5 ratified reading | **CP-20 RETIRE-READY → RETIRED gates on (a)+(b) jointly; CP-18 does NOT advance jointly** (separate arc, H_T-as-client surface) |
| Load-bearing operator sign-off | ✓ explicit — recommendation touches `CLAUDE.md` invariant I-4 at the X-AL-1 layer per §9.6 flag |
| Next workflow turn | `spec-writer` skill invocation against `Spec_Harness_Runtime_v1.md` v1.11 → v1.12 (§14.8.3 narrative amendment — pin workflow-initiation topology (α); replace line 1596 loose prose with protocol-canonical framing) |
| Subsequent workflow turn | `implementation-planner` skill invocation against `Phase 2 Session 3 Track A atomic-decomposition` v2.9 → v2.10 (add U-RT-62 + §3 dependency-graph row + §6.5 substitution-table row; Q4 schema reconciliation note) |
| Implementation arc opens at | v1.12 + v2.10 co-published — U-RT-62 FastMCP server hosting + workflow tool registration + `HarnessMCPServer` primitive + `api.run()` thin-wrapper reframe + e2e CC → workflow tool → HITL elicit → response → continuation test |
| Halt-of-arc status | Class 1 halt **PRESERVED until v1.12 + v2.10 land**. NO halt on the 23-commit stack at `origin/main`, other 7d batches, or Q6 follow-on arcs. |

*Operator ratification per `systems-architect` skill §4A.4 operator-decision-authority surface. Recommendations at §9 converted to applied resolution; the §10 footer records the ratification event. Downstream artifact absorption sequence per §9.5 + §9.8 begins at the next workflow turn.*
