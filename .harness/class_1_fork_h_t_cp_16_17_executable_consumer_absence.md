---
fork_class: Class 1 (halt-execution — X-AL-3 surface)
fork_id: class_1_fork_h_t_cp_16_17_executable_consumer_absence
filed_at: 2026-05-23
filed_against_head: b2cf37b
status: ✅ RATIFIED-AMENDED + PARTIAL-RETIREMENT 2026-05-23..2026-05-24 (frontmatter refreshed 2026-05-31 to match body Status refreshed 2026-05-27) — Memory-only scope per §16/§14.C; H_T-CP-16 RETIRED batch-14 `4479b07`; H_T-CP-18 + H_T-AS-2 RETIRED batch-16 `8e6311f`; H_T-CP-17 (Files) preserved PARTIAL, deferred indefinitely
routing_target: Runtime spec revision-pass (preferred per L9-septies precedent) OR AS spec revision-pass (alternative per namespace-co-residence) — §6.A operator decision
related_substitutions: H_T-CP-16 (memory.*) + H_T-CP-17 (files.*)
related_memories: [[h-t-cp-16-17-retire-ready-gate-runtime-composer-arcs]], [[retirement-batch-11-v1-5-re-invocation]], [[fork-h-t-cp-18-phantom-retirement-cite]]
---

# Class 1 fork: H_T-CP-16 + H_T-CP-17 executable consumer absence

**Status:** ✅ RATIFIED-AMENDED + PARTIAL-RETIREMENT 2026-05-23..2026-05-24 (status-line refreshed 2026-05-27) — fork RATIFIED-AMENDED per §16 (Memory-only scope per §14.C; Files arc deferred indefinitely); H_T-CP-16 RETIRED at batch-14 `4479b07` (U-RT-82 e2e vs real Anthropic API); H_T-CP-18 + H_T-AS-2 jointly RETIRED at batch-16 `8e6311f` (U-RT-86 e2e vs in-process FastMCP); H_T-CP-17 preserved PARTIAL pending Files arc operator-discretion. Species 3 stale-carry per workflow v1.9 §7.4.7.2.

## §1 Fork detection

**Trigger event.** Retirement-gate empirical re-evaluation at batch-11 v1.5 re-invocation arc + follow-on gate analysis (2026-05-23, post-`b2cf37b`). H_T-CP-16 + H_T-CP-17 transitioned STILL-BOUNDED → PARTIAL at batch-11 §2 + §3 against v1.4-augmented cite shapes (`U-AS-28 + U-AS-31`). PARTIAL → RETIRE-READY gate analysis at memory `[[h-t-cp-16-17-retire-ready-gate-runtime-composer-arcs]]` surfaces structural defect: **the gate cannot be cleared at the current spec corpus.**

**Empirical finding at HEAD `b2cf37b`.** What landed at U-AS-28 + U-AS-31 is *classification + OTel namespace schema*, NOT executable APIs:

- `harness-as/src/harness_as/anthropic_graceful_degradation.py:88` — `MemoryToolStorageBackend` enum (5 values: FILESYSTEM / ENCRYPTED_FILESYSTEM / S3 / DATABASE / OPERATOR_DEFINED)
- `harness-as/src/harness_as/anthropic_graceful_degradation.py:248` — `memory_tool_storage_backend(deployment_surface)` graceful-degradation classifier
- `harness-as/src/harness_as/anthropic_primitive_adoption.py:68` — `FILES_API` adoption-classification enum value
- AS spec v1.4 §14.6 — `files.*` 8-attribute OTel namespace schema (per-span attribute declaration)
- AS spec v1.4 §14.7 — `memory.*` 6-attribute OTel namespace schema (per-span attribute declaration)

**No executable consumer surface exists at any spec at HEAD.** There is no `MemoryToolClient.read(key)`, no `FilesAPIClient.upload(file)`, no Pythonic interface to invoke the Anthropic Memory tool or Files API. Greps confirm 0 production callsites for `memory_tool` / `MemoryTool` / `files_api` / `FilesAPI` across `harness-runtime/src` + `harness-cp/src` + `harness-cxa/src` (excluding the AS-side classification artifacts above).

## §2 X-AL-3 classification

Per `Phase_7_Meta_Architecture_v1.md` §7.7:

> **X-AL-3.** **No silent H_T design extension at Phase 7 execution.** New H_T primitives surfaced at execution-time route to design-phase back-flow (Class 1) before implementation proceeds.

**Classification: Class 1 — X-AL-3 surface.** Materializing `MemoryToolClient` / `FilesAPIClient` at Phase 7 execution-time without spec contract would constitute silent H_T design extension (specifically: introducing executable surfaces not declared at any canonical artifact). The §1 finding confirms no spec contract for these surfaces exists.

**Nuance — primitive shape exists at ADR, under-specified downstream.** ADR-D3 + C-AS-13 §13 contract the 11 Anthropic primitives at the adoption-classification level (which primitive × workload-class × storage-backend). C-AS-14 contracts the OTel namespace schemas (`memory.*` / `files.*` attribute declarations). The under-specification is downstream: no spec contracts the executable consumer signature shape (analogous to runtime spec v1.13 §14.10 C-RT-20 `MCPClientHost` contract).

Per skill §3.1 routing table: primitive shape at ADR + under-specified downstream → route to downstream-artifact revision (spec layer), NOT ADR revision.

## §3 Precedent: L9-septies MCPClientHost arc

H_T-CP-18 (MCP integration) reached RETIRE-READY at batch-10 via the L9-septies cluster which closed at `00da5ef` (workspace HEAD pre-`b2cf37b` arc). The arc materialized executable runtime consumer of the AS-contracted `mcp.*` namespace through:

| Layer | Landing |
|---|---|
| AS spec v1.4 §14.3 footer note | Producer-site reference: "the `mcp.*` 7-attribute namespace is emitted by `MCPClientNamespaceEmitter` per CP spec v1.10 §27 C-CP-27" |
| Runtime spec v1.13 §14.9 C-RT-19 | `RuntimeToolDispatcher` — executable tool-call dispatch contract |
| Runtime spec v1.13 §14.10 C-RT-20 | `MCPClientHost` — executable MCP client consumer + namespace emission contract |
| Runtime plan v2.12 U-RT-71..U-RT-75 | 5-unit cluster: RuntimeConfig + HarnessContext fields + stage-3a factory + retry dispatcher + stage-5 factory |
| Code | `harness-runtime/src/harness_runtime/lifecycle/mcp_client_host.py` + dispatcher composer body |

Post-landing, H_T-CP-18 status: structural criterion-B MET via library landing + factory wiring; operational e2e gated on operator-supplied `mcp_servers` non-empty config + external MCP server availability. **Operator-opt-in RETIRE-READY pattern** documented at `harness-cp/CLAUDE.md:177`.

## §4 Proposed arc shape (per CP-16 / CP-17, parallel structure)

Each substitution → RETIRE-READY arc, mirroring L9-septies (~5-7 commits per substitution):

| Step | Memory (CP-16) | Files (CP-17) |
|---|---|---|
| **S1** Spec extension | Runtime spec NEW §14.X C-RT-NN `MemoryToolHost` (or `MemoryToolClient`) — executable consumer of Memory tool primitive per ADR-D3 §1.1 #11 + emitter for `memory.*` per C-AS-14 §14.7 | Runtime spec NEW §14.Y C-RT-MM `FilesAPIHost` — executable consumer of Files API primitive per ADR-D3 §1.1 #10 + emitter for `files.*` per C-AS-14 §14.6 |
| **S2** AS spec footer note | C-AS-14 §14.7 footer: "`memory.*` 6-attribute namespace is emitted by `MemoryToolHost` per runtime spec §14.X" (parallel to v1.4 §14.3 mcp.* note) | C-AS-14 §14.6 footer: "`files.*` 8-attribute namespace is emitted by `FilesAPIHost` per runtime spec §14.Y" |
| **S3** Plan unit cluster | Runtime plan NEW L9-N cluster (3-5 units: type carriers + factory + dispatcher + integration) | Same shape |
| **S4** Implementation | `harness-runtime/.../memory_tool_host.py` + bootstrap stage extension + HarnessContext field | `harness-runtime/.../files_api_host.py` + same shape |
| **S5** Workflow_driver invocation | Step-kind extension (e.g., `MEMORY_READ`/`MEMORY_WRITE` step kinds) OR routing through `RuntimeToolDispatcher` extension (extends C-RT-19 to memory-tool family) | Same shape decision (FILES_READ/FILES_UPLOAD step kinds OR tool dispatch routing) |
| **S6** Span emission | Emitter wraps memory-tool-call span with U-AS-31 6-attribute schema | Same shape with 8-attribute schema |
| **S7** E2e exercise | Workflow manifest with memory step → real Anthropic API call (or mock backend per §6.C below) | Same shape with files step |
| **S8** Batch retirement filing | Batch-12 (or later) records STILL-BOUNDED → RETIRE-READY transition with structural criterion-B MET pattern + operator-opt-in gate | Same shape |

## §5 Effort estimate

Per memory `[[h-t-cp-16-17-retire-ready-gate-runtime-composer-arcs]]`:

| Arc | Commits (CC+gstack) | Spec axes touched |
|---|---|---|
| CP-16 memory arc | 5-7 | Runtime spec + AS spec footer + runtime plan |
| CP-17 files arc | 5-7 | Runtime spec + AS spec footer + runtime plan |
| Bundled CP-16+17 arc | 7-10 (amortized contract-authoring overhead) | Runtime spec + AS spec footer + runtime plan |

## §6 Architectural ambiguities — OPERATOR RATIFICATION REQUIRED

### §6.A Spec axis home

Where do the executable consumer contracts live?

| Option | Rationale | Tradeoff |
|---|---|---|
| **A.i Runtime spec** (preferred per §3 precedent) | Mirrors MCPClientHost at runtime spec v1.13 §14.10. Runtime owns executable lifecycle primitives; AS owns adoption-classification + namespace schemas. | Runtime spec accretes more contract surface (§14.X + §14.Y added). Clean separation of concern preserved. |
| A.ii AS spec extension | The namespace schemas (C-AS-14 §14.6/§14.7) already co-reside at AS; some operators may prefer co-location of namespace declaration + emitter contract. | Breaks the v1.13 precedent. AS spec accretes runtime-side lifecycle responsibility (cross-axis seepage). |
| A.iii Split — runtime owns dispatcher + lifecycle; AS owns emitter | Closest to v1.4 precedent (§14.3 footer note delegates `mcp.*` emission to CP spec §27 C-CP-27). The C-AS-14 §14.6/§14.7 footers would point at runtime spec §14.X/§14.Y for executable consumer + emit. | Same as A.i in practice — runtime owns the new contract, AS adds footer references only. **This is what L9-septies actually did at v1.4.** |

### §6.B Single-bundled vs split arcs

| Option | Tradeoff |
|---|---|
| **B.i Bundled CP-16+17 in one runtime-spec-revision + plan-revision arc** | Amortizes contract-authoring + Class 1 back-flow overhead. Both arcs touch parallel structure (§4 table mirrors line-by-line). Estimate 7-10 commits. |
| B.ii Split memory-first arc then files-arc | Smaller per-arc surface; clearer per-arc operator review. Lower amortization. Estimate 10-14 commits total. |
| B.iii Split files-first arc then memory-arc | Same as B.ii with priority inverted. |

### §6.C E2e exercise scope

What does the §4 S7 e2e exercise look like? The Anthropic Memory tool (beta `memory_20250818`, ADR-D3 §1.1 #11) is **client-side**: harness implements storage backend. So "real" e2e is ambiguous.

| Option | Tradeoff |
|---|---|
| **C.i Local filesystem storage backend** (`MemoryToolStorageBackend.FILESYSTEM`) | Cleanest e2e — round-trip through real Anthropic Memory tool API call with local-fs backend; no external storage dependency. Consistent with existing `MemoryToolStorageBackend` adoption-classification. |
| C.ii Real S3/Database backend at managed-cloud surface | Higher fidelity but introduces external storage operational dependency at retirement-gate criterion. Mirrors H_T-CP-18 "external server availability" gate. |
| C.iii Mock-backed e2e (in-process MemoryToolStorageBackend stub) | Lowest fidelity — does NOT exercise real Anthropic API call. Faster CI cycle. Risks the "mocked-test-passes-but-prod-fails" failure mode per `[[feedback_testing]]`-style discipline. |

Files API (`/v1/files` upload/list/metadata/delete, ADR-D3 §1.1 #10) is server-side at Anthropic. E2e options:

| Option | Tradeoff |
|---|---|
| **C.iv Real Files API upload/list round-trip** | Highest fidelity. Requires Anthropic API credentials at e2e environment. |
| C.v Recorded VCR-style fixtures replaying Anthropic Files API responses | Reproducible e2e without live API dependency at CI. |
| C.vi Mock-backed (in-process FilesAPI stub) | Same risk profile as C.iii. |

### §6.D Retirement-gate stringency

Mirrors H_T-CP-18 + H_T-CP-21 batch-10/11 operator-opt-in pattern?

| Option | Tradeoff |
|---|---|
| **D.i Operator-opt-in RETIRE-READY** (structural criterion-B MET as library + production invocation operator-bound at non-default config) | Consistent with batch-10 CP-18 (`mcp_servers=[]` default) + batch-11 CP-21 (`validator_framework=None` default). Promotes substitution to RETIRE-READY at landing arc; full RETIRED gates on e2e exercise at operator-bound config. |
| D.ii Strict RETIRED requires e2e exercise at landing arc | Higher bar. Single transition STILL-BOUNDED → RETIRED. Aligns with strict ledger-v2 reading. |
| D.iii Hybrid — RETIRE-READY at structural landing + RETIRED at next batch with e2e | Two-arc cadence. Preserves landing arc focus on contract + library; retirement filing arc focuses on e2e + retirement event. |

### §6.E Workflow_driver invocation site

How does workflow_driver invoke the executable consumer?

| Option | Tradeoff |
|---|---|
| **E.i New StepKind values** (`MEMORY_READ` / `MEMORY_WRITE` / `FILES_UPLOAD` / `FILES_READ` / etc.) at CP spec | First-class workflow step types. Requires CP-spec extension for StepKind enum + dispatcher binding per existing StepKindRegistry pattern. Larger scope (CP-spec touch added). |
| E.ii Tool dispatch routing through `RuntimeToolDispatcher` extension | Extends C-RT-19 to recognize memory-tool / files-api tool families. Routes via existing tool dispatch path. Smaller CP-spec impact. Anthropic Memory tool + Files API ARE Anthropic tool-call schemas → natural fit for tool dispatcher. |
| E.iii Both (E.i + E.ii) | Maximum flexibility, maximum surface area. |

### §6.F Memory vs Files prioritization (if split per §6.B)

| Option | Tradeoff |
|---|---|
| **F.i Memory first** | Memory tool is the more substantive surface (storage-backend selection per workload + multi-deployment classification already landed at U-AS-28). Files API is mechanically simpler (upload/list/metadata/delete). Memory-first builds the harder pattern; files-second is shorter. |
| F.ii Files first | Files API is simpler — faster pattern-establishment for §4 arc shape; informs memory arc design via precedent. |
| F.iii Operator-discretion ordering | Defer to operator priority on which Anthropic primitive the harness exercises in near-term workloads. |

## §7 Halt scope

**No active sub-phase to halt.** This fork is operator-initiated retirement-gate opening, not a sub-phase execution halt. The fork-doc surfaces the architectural decisions; opens spec/plan/code work only after §6 ratification.

**Bounded carry-forward acceptable.** Per Meta-Arch §5.3 + §5.2.3: H_T-CP-16/17 currently bounded-residual at PARTIAL; no downstream blocker cites either retirement. Operator can defer opening this arc to a later session without violating closure criterion (carry-forward authorized as Class 2 bounded-residual at any 7d-closure check).

## §8 Recommended disposition (subject to operator ratification)

Per the §6 enumeration:

| Question | Recommendation | Why |
|---|---|---|
| §6.A spec axis home | **A.iii Split** (runtime owns contract + dispatcher; AS adds §14 footer references) | Mirrors v1.4 mcp.* precedent exactly; preserves runtime-owns-executable-lifecycle separation; cleanest authority chain. |
| §6.B bundled vs split arcs | **B.i Bundled CP-16+17 in single arc** | Amortizes Class 1 overhead; parallel §4 structure invites single contract-authoring pass; estimated 7-10 commits is manageable. |
| §6.C e2e exercise | **C.i + C.v** (memory: local-fs backend round-trip; files: VCR-replay) | Highest fidelity without external operational dependencies at CI; consistent with existing storage-backend adoption classifier + reproducible. |
| §6.D retirement-gate stringency | **D.i operator-opt-in RETIRE-READY** | Consistent with batch-10/11 CP-18/CP-21 pattern; promotes substitution at landing; full RETIRED at e2e under operator config. |
| §6.E invocation site | **E.ii tool dispatch routing extension** | Anthropic Memory tool + Files API are tool-call schemas; natural fit for existing tool dispatch infrastructure; minimal CP-spec extension; preserves StepKind enum stability. |
| §6.F prioritization (only relevant if §6.B = split) | **F.i memory first** | Memory tool builds harder pattern; files-second informed by it. (Not relevant if §6.B = B.i bundled.) |

**Estimated arc shape under recommended disposition.** 7-10 commits in a bundled arc touching runtime spec NEW §14.X + §14.Y (executable consumer contracts) + AS spec C-AS-14 §14.6/§14.7 footer notes + runtime spec C-RT-19 RuntimeToolDispatcher extension to memory-tool/files-api families + runtime plan NEW L-N cluster (4-6 units) + implementation at `harness-runtime/.../memory_tool_host.py` + `files_api_host.py` + bootstrap stage extensions + e2e test (local-fs memory + VCR-replay files).

## §9 Authority chain

- ADR-D3 §1.1 #10 (Files API) + #11 (Memory tool) — primitive existence anchor (PRESERVED — no ADR revision)
- ADR-D3 §1.3 storage-backend per engine class — adoption classifier (PRESERVED)
- AS spec v1.4 §13 C-AS-13 — eleven-primitive adoption-classification matrix (PRESERVED)
- AS spec v1.4 §14.6 / §14.7 — files.* / memory.* OTel namespace schemas (PRESERVED; gains §14.X footer note per §6.A A.iii recommendation)
- Runtime spec v1.16 — NEW §14.X + §14.Y executable consumer contracts ADDED at the bundled arc
- Runtime plan v2.13 — NEW L-N cluster ADDED with 4-6 units

## §10 Filing footer

| Field | Value |
|---|---|
| Filed at | 2026-05-23 |
| Filed against HEAD | `b2cf37b` |
| Routing target (preferred) | Runtime spec revision-pass + plan revision-pass + AS spec footer-note revision (per §6.A A.iii) |
| Routing target (alternative) | AS spec extension (per §6.A A.ii) |
| Status | **PROPOSING** — operator ratification required at §6.A/B/C/D/E/F |
| Halt scope | None (no active sub-phase) |
| Bounded-carry-forward acceptable | Yes (per §7) |
| Predecessor pattern | L9-septies MCPClientHost arc (CP-18 RETIRE-READY at batch-10) |
| Memory entries | `[[h-t-cp-16-17-retire-ready-gate-runtime-composer-arcs]]`, `[[retirement-batch-11-v1-5-re-invocation]]` |
| Next step | Operator AskUserQuestion on §6 ambiguities; recommended disposition at §8 |

## §11 Operator ratification (2026-05-23)

| Question | Ratified | Vs recommendation |
|---|---|---|
| §6.A spec axis home | **A.iii Split** (runtime owns contract + dispatcher; AS adds §14 footer references) | Per recommendation |
| §6.B bundled vs split | **B.i Bundled CP-16+17 single arc** | Per recommendation |
| §6.C e2e exercise scope | **C.ii + C.iv Real backends** (memory: S3/Database at managed-cloud; files: live Anthropic Files API) | **Stricter than recommended** — operator chose highest fidelity; introduces external operational dependency at retirement-gate criterion (mirrors H_T-CP-18 external-server gate); requires Anthropic credentials + S3 setup at e2e environment |
| §6.D retirement-gate stringency | **D.i Operator-opt-in RETIRE-READY** | Per recommendation |
| §6.E invocation site | **E.ii Tool dispatch routing extension** via C-RT-19 RuntimeToolDispatcher | Per recommendation |
| §6.F prioritization | **N/A** (bundled arc per §6.B) | — |

**Status transition: PROPOSING → RATIFIED.** Fork-doc cleared for next arc (spec-writer + implementation-planner revision-pass per §8 estimated arc shape — bundled CP-16+17 arc, runtime spec NEW §14.X (MemoryToolHost) + NEW §14.Y (FilesAPIHost) + AS spec C-AS-14 §14.6/§14.7 footer notes + runtime spec C-RT-19 RuntimeToolDispatcher extension to memory-tool/files-api families + runtime plan NEW L-N cluster with 4-6 units + implementation + e2e test with **real S3 backend memory + live Anthropic Files API**).

**Implication of §6.C C.ii+C.iv ratification.** Retirement-gate criterion for RETIRED transition now requires:
- Operator-bound `memory_tool_host` config with non-mock S3/Database backend at managed-cloud surface
- Operator-bound Anthropic API credentials at e2e environment
- Live Anthropic Files API round-trip exercise at retirement-batch arc

This mirrors the H_T-CP-18 RETIRED gate (operator-supplied `mcp_servers` non-empty + external MCP server availability). RETIRE-READY pattern unchanged — landing arc promotes both substitutions to RETIRE-READY with structural criterion-B MET; RETIRED transition deferred to operator-bound-config + e2e exercise batch.

**Operator-discretion timing on opening the spec-writer arc.** Fork-doc RATIFIED; no commitment on when the bundled-arc opens. Per §7 bounded-carry-forward acceptable. Next arc invocation: `spec-writer` skill against runtime spec v1.16 → v1.17 (NEW §14.X + §14.Y) + AS spec v1.4 → v1.5 (§14.6/§14.7 footer notes) + `implementation-planner` against runtime plan v2.13 → v2.14 (NEW L-N cluster).

> **§11 status update (2026-05-23, post-§13 architect recommendation):** Ratification is **PROVISIONAL** pending §14 operator routing. See §12–§15 below for the spec-writer FM-1 trigger + systems-architect Mode 3 recommendation that surfaced structural-shape divergence between MCP / Memory tool / Files API.

---

## §12 Spec-writer FM-1 trigger (2026-05-23, post-ratification)

**Trigger.** On `spec-writer` skill invocation against runtime spec v1.16 to apply the §11 ratified dispositions, FM-1 surfaced: the §6.E E.ii ratification ("extend C-RT-19 RuntimeToolDispatcher to recognize memory-tool + files-api tool families") AND the §6.A A.iii ratification ("runtime owns dispatcher + lifecycle, mirroring L9-septies MCPClientHost") assume structural parallelism between MCP, Memory tool, and Files API that does not hold up against the canonical artifacts.

**Empirical asymmetry findings at HEAD `b2cf37b`** (orienting reads at runtime spec §5 C-RT-05 + §14.9 C-RT-19 + ADR-D3 §1.1 #10 + #11 + `harness-as/src/harness_as/anthropic_primitive_adoption.py:69+189` + `harness-as/src/harness_as/anthropic_graceful_degradation.py:88+248`):

| Primitive | Binding shape (canonical artifact citation) | Implication |
|---|---|---|
| **MCP** (CP-18 / C-RT-19) | Separate subprocess/HTTP/SSE transport per server; per-server tool registry resolved via `ctx.mcp_client_host.tool_registry`; per-server trust gate (`PerServerTrustEvaluator`); standalone start/health/shutdown lifecycle; `MCPClientHost.call_tool(name, args, idempotency_key)` is the dispatch surface | The L9-septies MemoryToolHost/FilesAPIHost analogy assumes this shape exists for Memory + Files. It does not. |
| **Memory tool** (CP-16) | **CLIENT-SIDE** per ADR-D3 §1.1 #11: harness implements storage backend. Tool definition (`tool type "memory_20250818"`) passed as element of `tools=[...]` arg to `anthropic.messages.create(...)`. **Anthropic SDK runs the message loop**; the SDK invokes a harness-provided callback (or polling the backend) on `view`/`create`/`delete`/`str_replace`/`insert` operations against `/memories`. No separate transport. No tool-registry resolution. No per-server trust. No subprocess. Composes with `clear_tool_uses_20250919` context editing via `exclude_tools: ["memory"]`. | **There is no tool-dispatch site to extend.** Memory tool's runtime binding is inside the LLM message-create call, not at C-RT-19. The `memory.*` namespace emits at storage-backend-callback invocation sites, NOT at `mcp.tool.call`-style dispatch spans. |
| **Files API** (CP-17) | **Server-side REST endpoint** `/v1/files` (beta `files-api-2025-04-14`) per ADR-D3 §1.1 #10. Workspace-scoped. Operations: upload / list / metadata / delete. File references via `file_id` injected into message content blocks. Composes with code execution tool's `file_ids` parameter (passed as tool-call arg payload, NOT as tool-call implementation) + Batch API for 50% discount. | **Not a tool-call loop integration at all.** Files API is a resource-manager surface — workflow step authors upload files pre-execution and reference them by `file_id` in message composition. The `files.*` namespace emits at upload/reference sites, NOT at tool dispatch. |

**The §6 ambiguities at fork-doc filing were under-specified for contract-authoring depth.** §6.A/B/E ratifications presupposed L9-septies parallelism. That parallelism holds for MCP-shaped primitives. It does not hold for Anthropic-SDK-bound primitives (Memory tool) or for Anthropic-REST-endpoint primitives (Files API). The structural shape divergence is 3-way, not 1-way.

## §13 Architectural-tension resolution (systems-architect Mode 3)

Per `systems-architect` skill §4A.2 — five-step procedure applied to the §12 tension.

### §13.1 Tension statement

Three divergent architectural assumptions surfaced at §11 ratification, contradicted by ADR-D3 §1.1 + AS-axis canonical primitive adoption code at HEAD `b2cf37b`:

- **Divergent assumption 1 (§6.A A.iii):** "Runtime spec owns NEW §14.X MemoryToolHost contract + NEW §14.Y FilesAPIHost contract; mirrors v1.4 mcp.* precedent."
  Quote from fork-doc §6.A A.iii: *"Runtime owns the new contract, AS adds footer references only. This is what L9-septies actually did at v1.4."*
- **Divergent assumption 2 (§6.B B.i):** "Bundled CP-16+17 in single arc amortizes contract-authoring overhead; parallel §4 structure invites single contract-authoring pass."
  Quote from fork-doc §4 table column header: *"Each substitution → RETIRE-READY arc, mirroring L9-septies (~5-7 commits per substitution)"* — assumes §4 table rows S1..S8 apply uniformly to both Memory and Files.
- **Divergent assumption 3 (§6.E E.ii):** "Extends C-RT-19 RuntimeToolDispatcher to recognize memory-tool + files-api tool families. Routes through existing tool dispatch path."
  Quote from fork-doc §6.E E.ii: *"Anthropic Memory tool + Files API ARE Anthropic tool-call schemas — natural fit for tool dispatcher."*

**Canonical-artifact contradiction.** ADR-D3 §1.1 #11 says Memory tool is "client-side: harness implements storage backend." This is incompatible with assumption 1 ("runtime owns the dispatcher") and assumption 3 ("tool dispatch via C-RT-19") because there is no dispatcher to own — the SDK owns the message loop. ADR-D3 §1.1 #10 says Files API references files by `file_id` in message content — not a tool-call schema, contradicting assumption 3's "ARE Anthropic tool-call schemas" classification.

### §13.2 Authority-chain placement

Per `CLAUDE.md` §1.3: ADR (F1–F5 + D1–D6) → ADD v1.3 → PRD v1.1 → per-axis spec v1.x → per-axis plan v2.x + CXA v2.1.

| Divergent artifact | Position on chain | Authority |
|---|---|---|
| ADR-D3 v1.2 §1.1 #10 + #11 | Tier 1 (foundational derivative) | **CANONICAL** — primitive shape declarations (client-side Memory, REST-endpoint Files) are at ADR layer |
| AS spec v1.4 §13 C-AS-13 + §14 C-AS-14 §14.6 + §14.7 | Tier 4 (axis spec) | Consistent with ADR-D3 — adoption-classification + namespace schemas (not executable surfaces) |
| Runtime spec v1.16 §14.9 C-RT-19 | Tier 4 (axis spec) | MCP-shaped dispatch contract; consistent with MCP shape; does not contradict ADR-D3 (MCP is a separate primitive — not 10 or 11) |
| Fork-doc §11 §6.A/B/E ratifications | NOT on canonical chain | Operator decisions at fork-doc-filing time; can be reopened per X-AL-3 (no silent H_T design extension) |

**The authority-chain reading is unambiguous.** ADR-D3 v1.2 (tier 1) is canonical and contradicts the §6.A/E assumptions. The §11 ratification was made against an under-specified §6 enumeration that elided the structural-shape divergence. Per `systems-architect` §4A.2 step 4: the resolution is "conform the divergent artifact [the §11 ratification + dependent §6 dispositions] to the chain [ADR-D3]" — not re-decide.

### §13.3 Five-axis decomposition

Per `systems-architect` §2.1:

| Axis | What this resolution touches |
|---|---|
| **Information substrate** | Memory tool storage backend = state substrate (filesystem / S3 / database storage per `MemoryToolStorageBackend`). Files API workspace-scoped files = state substrate (Anthropic-side workspace). Both consume IS-axis primitives at the binding site (filesystem PathResolver for local Memory backend; file_id reference tracking analogous to LedgerEntryRef shape). |
| **Action surface** | NOT a new tool contract. Memory tool is an Anthropic-SDK-bound primitive; Files API is an Anthropic-REST-endpoint primitive. AS-axis C-AS-13 §13 already classifies both. C-AS-14 §14.6/§14.7 namespace schemas already declared. No NEW AS-axis contract needed. |
| **Control plane** | Memory tool binds at LLM dispatch composition site (C-RT-15 §14.5 RuntimeLLMDispatcher) — sidecar callback registry. Files API binds at workflow-step authoring time (pre-execution upload) + message composition time (file_id injection). Both compose against existing CP-axis primitives without new CP-spec extension. |
| **Operational discipline** | `memory.*` 6-attr namespace + `files.*` 8-attr namespace already declared at AS spec §14.6/§14.7. Emission sites differ from MCP: memory.* emits at storage-backend-callback invocation; files.* emits at upload + at message-content-composition (when file_id injected). |
| **Deployment surface** | Memory storage backends per `MemoryToolStorageBackend` enum vary per `DeploymentSurface` (filesystem at LOCAL_DEV, S3/Database at MANAGED_CLOUD); already classified at `anthropic_graceful_degradation.py:222`. Files API is workspace-scoped per Anthropic side — single binding surface across deployments. |

**Cross-axis tension surfaced:** Files API workspace-scoped resource lifecycle composes with code execution `file_ids` (a different tool family). Additional binding-site complexity not captured at fork-doc §6.

### §13.4 Probabilistic-deterministic boundary

Per `systems-architect` §2.2:

| Primitive | Deterministic side (harness) | Probabilistic side (Anthropic SDK / LLM) |
|---|---|---|
| **Memory tool** | Storage backend implementation (filesystem/S3/database CRUD); callback registration; `memory.*` span emission at callback site; storage-backend availability per DeploymentSurface | LLM decides when/what to read/write to `/memories`; SDK runs the message loop including tool-call dispatch back to the storage backend callback |
| **Files API** | Upload composer (pre-execution); file_id reference manager; metadata/delete operations; `files.*` span emission at upload/reference sites; workspace-scope discipline | LLM decides what content to author + which file_ids to reference; uploads themselves are deterministic (operator-authored or composer-emitted) |

The harness owns the **storage backend** (Memory) and the **resource manager** (Files). The LLM/SDK owns the **invocation timing** (Memory: SDK invokes callback during message loop; Files: LLM emits file_id references in message content). This boundary is the binding-site discriminator — both are at the LLM-call boundary, but at distinct sub-surfaces (callback registry for Memory; resource manager + message composition for Files).

### §13.5 F/D/I classification

Per `systems-architect` §2.3:

| Decision | Class | Why |
|---|---|---|
| Where Memory tool binds (callback registry at C-RT-15 LLM dispatch site) | **D** (derivative) — constrained by F-decisions on ADR-F1 (multi-LLM commitment) + ADR-D3 §1.1 #11 (client-side classification) | Cannot change without revising those F/D-tier decisions |
| Where Files API binds (NEW resource-manager sibling contract to C-RT-05) | **D** (derivative) — constrained by ADR-D3 §1.1 #10 (REST-endpoint classification) | Cannot change without revising ADR-D3 |
| Whether arcs are bundled or split | **I** (independent) — operator-discretion sequencing; both arcs structurally divergent | Re-decidable without rework once individual arc shapes are clear |

### §13.6 Recommendation

The systems-architect recommendation per `systems-architect` §4A.2 step 4 — addressing fork-doc §12 questions (a)-(e):

#### §13.6.A Where do Memory tool + Files API live in the runtime contract topology?

| Primitive | Recommended binding site | Contract shape |
|---|---|---|
| **Memory tool** | **NEW callback-registry contract at runtime spec, consumed by C-RT-15 RuntimeLLMDispatcher** | Define `MemoryToolStorageBackendProtocol` (CRUD callbacks: `view(path) → bytes`, `create(path, content)`, `delete(path)`, `str_replace(path, old, new)`, `insert(path, line, content)`) + `MemoryToolRegistry` binding storage-backend implementation to deployment-surface per `MemoryToolStorageBackend` enum. C-RT-15 §14.5 amended: when LLM dispatch composes `tools=[...]` arg and step-effective-binding includes memory tool, dispatcher injects the storage-backend callback adapter. `memory.*` 6-attr namespace emitted at each callback invocation. NEW C-RT-NN contract; no extension to C-RT-19. |
| **Files API** | **NEW sibling REST-client contract at runtime, parallel to C-RT-05 ProviderClient (separate from but consumed by C-RT-15)** | Define `FilesAPIClient` Protocol (`upload(content, mime_type) → FileID`, `list() → list[FileMetadata]`, `metadata(file_id) → FileMetadata`, `delete(file_id)`) + concrete `AnthropicFilesAPIClient` adapter. Construction at stage 3a (alongside ProviderClient triple per C-RT-05). Consumed at: (i) workflow-step pre-execution (when step's `files: [{path}]` field requires upload before LLM dispatch); (ii) message composition (when LLM-dispatch composes message content with file_id references). `files.*` 8-attr namespace emitted at upload + at reference-injection sites. NEW C-RT-NN contract; no extension to C-RT-19. |

**MCPClientHost / C-RT-19 unchanged.** MCP-shaped dispatch path is correct for MCP. Memory + Files do not consume that path.

#### §13.6.B Does the §6.B B.i bundled-arc ratification survive?

**RECOMMENDATION: NO — split into 2 arcs.** Memory tool arc + Files API arc are structurally divergent at both contract-authoring level (callback-registry vs REST-client-with-resource-manager) and implementation level (no shared base abstraction). Bundling adds coordination overhead without amortization.

Sub-options for operator at §14:

- **Re-split as 2 sequential arcs.** Memory first (smaller surface; storage-backend protocol + 1 deployment-binding) then Files (resource-manager + message-composition integration). Each ~5-8 commits; sequential ratification preserves operator review surface.
- **Re-split as 2 parallel arcs.** If operator capacity permits + worktree isolation discipline holds, both can land independently. No spec-content interdependency.
- **Defer Files arc; land Memory arc only at this opening.** Memory tool is more substantive (storage-backend per workload + multi-deployment classification already landed). Files arc deferred indefinitely until operational driver surfaces (no current downstream blocker).

#### §13.6.C Revised per-arc shape estimate

| Arc | Commits (CC+gstack) | Spec/plan touch |
|---|---|---|
| **Memory arc** | 5-8 | Runtime spec NEW §14.12 C-RT-22 `MemoryToolRegistry` + `MemoryToolStorageBackendProtocol`; amend C-RT-15 §14.5 with callback-injection composer step; RuntimeConfig NEW field `memory_tool_backend_config`; HarnessContext NEW field `memory_tool_registry`; AS spec v1.4 §14.7 footer note repoint; runtime plan NEW L-M cluster (3-5 units: storage-backend protocol + filesystem implementation + S3 implementation + callback injection + e2e); harness-as plan possible touch if `MemoryToolStorageBackend` resolver needs runtime hook |
| **Files arc** | 4-6 | Runtime spec NEW §14.13 C-RT-23 `FilesAPIClient` Protocol + adapter; construction at stage 3a alongside C-RT-05; HarnessContext NEW field `files_api_client`; amend C-RT-15 §14.5 with file_id-reference-injection composer step; AS spec v1.4 §14.6 footer note repoint; runtime plan NEW L-M cluster (3-4 units: Protocol + adapter + integration + e2e) |

Lower than fork-doc §5 estimate (7-10 bundled) because each individual arc is smaller than the assumed-parallel L9-septies-shaped arc; the shared coordination overhead the bundle was supposed to amortize doesn't exist.

#### §13.6.D AS spec footer-note repoint

- AS spec v1.4 §14.7 `memory.*` footer: pointer becomes "runtime spec v1.17 §14.12 C-RT-22 `MemoryToolRegistry` storage-backend callback site" (NOT "MemoryToolHost"); semantic: storage-backend callback emits the namespace at each CRUD operation, NOT at a dispatch site.
- AS spec v1.4 §14.6 `files.*` footer: pointer becomes "runtime spec v1.17 §14.13 C-RT-23 `FilesAPIClient` upload + file_id-reference-injection sites" (NOT "FilesAPIHost"); semantic: namespace emits at TWO sites (upload + reference) not one dispatch site.

Both footer-note shapes diverge from the v1.4 §14.3 mcp.* template — the mcp.* footer points at a single canonical dispatch site (C-RT-19 §14.9.4); the memory.* + files.* footers will point at distinct emission sites that aren't a single dispatch span.

#### §13.6.E §6.C real-backends e2e implications

The §6.C C.ii+C.iv ratification ("real S3 backend memory + live Anthropic Files API") assumes MCP-like external-server gating. The actual e2e shapes differ:

- **Memory tool e2e:** Real Anthropic API `messages.create` call with `tools=[memory_tool]` + storage-backend wired to real S3 bucket. Exercise: LLM-driven write to `/memories/foo` → SDK invokes storage-backend callback → S3 PUT → subsequent message reads back. Requires Anthropic credentials + S3 credentials + S3 bucket. Mirrors H_T-CP-18 external-server gate shape acceptably.
- **Files API e2e:** Real `/v1/files` upload → reference in message content → Anthropic-side persistence verification. Requires Anthropic credentials. Workspace-scoped (no separate AWS infra). LIGHTER operational gate than Memory e2e.

**C.ii+C.iv ratification holds structurally but the operational dependencies are heavier for Memory (Anthropic + S3) than for Files (Anthropic only).** Operator may want to revisit per-arc — Files e2e is single-credential-set; Memory e2e is dual-credential-set + S3 bucket lifecycle management at retirement-gate criterion.

### §13.7 Tiebreaker check

Per `systems-architect` §4A.2 step 5: the single verifiable fact that makes the §13.6.A recommendation determinate is —

> **No existing CP-axis or runtime-axis spec contract names a `MemoryToolHost` or `FilesAPIHost` class. Empirical verification: grep `MemoryToolHost\|FilesAPIHost` across `design-substrate/*.md` returns 0 hits at HEAD `b2cf37b`.**

If such a class existed at the spec layer (i.e., the L9-septies parallelism was already partly established at a spec contract not visible at this analysis), the recommendation would need revision. Confirmed absent. The recommendation stands.

### §13.8 Fork classification

Per `Project_Workflow_v1_8.md` §2.7.6:

**This is a Class 1 fork** — the §11 ratification was made against an under-specified §6 enumeration that the architect's contract-authoring-depth review reveals to contradict ADR-D3. Re-ratification required before spec-writer can resume.

**Halt scope.** Spec-writer arc halted (no edits written; worktree clean of spec changes). No active sub-phase to halt beyond that. Fork-doc §11 ratification is **provisional** pending operator decision on the §14 routing.

### §13.9 Operator decides

Per `systems-architect` §4A.4 — the architect recommends; the operator decides. The recommendation at §13.6 is one coherent path. Operator may select alternative paths (e.g., revise ADR-D3 to declare MCP-shaped Memory/Files surfaces — but this would route to ADR-revision back-flow per `CLAUDE.md` §4.3, a substantially heavier scope than the recommended path).

## §14 Operator routing — sub-decisions to ratify

The §13 recommendation surfaces sub-decisions for operator ratification before spec-writer arc reopens:

| Sub-decision | Options |
|---|---|
| §14.A | Reopen §11 ratification entirely (re-ratify all 5 dispositions against revised §13 topology) OR amend §11 in-place (preserve §6.D where it still applies; revise §6.A→§13.6.A + §6.B→§13.6.B + §6.E→§13.6.A; revise §6.C scope per §13.6.E) |
| §14.B | Accept §13.6 architectural recommendation? Memory at NEW callback-registry contract consumed by C-RT-15; Files at NEW sibling REST-client contract; MCP unchanged at C-RT-19 |
| §14.C | Arc-split decision per §13.6.B: 2 sequential arcs OR 2 parallel arcs OR defer Files arc indefinitely (Memory-only at this opening) |
| §14.D | Memory e2e operational scope per §13.6.E: real S3 + Anthropic credentials at retirement-gate (heavier) OR local-filesystem-backend acceptable for retirement-gate with S3 deferred (lighter) |
| §14.E | Files e2e timing: open Files arc on Memory-arc close OR defer indefinitely if §14.C selects defer-Files |

## §15 Filing footer (architect recommendation)

| Field | Value |
|---|---|
| Recommendation filed at | 2026-05-23 (post-§11 ratification, same session) |
| Filed against HEAD | `b2cf37b` |
| Skill invoked | `systems-architect` Mode 3 (Phase-7 architectural-tension resolution) |
| Status | **PROPOSING** — §14 operator routing required |
| Authority chain analysis | §13.2 — ADR-D3 v1.2 §1.1 #10 + #11 canonical; §11 ratification was made against under-specified §6 enumeration; conform divergent artifact (§11) to chain (ADR-D3) per `systems-architect` §4A.2 step 4 |
| Tiebreaker | §13.7 — grep `MemoryToolHost\|FilesAPIHost` returns 0 hits at HEAD |
| Fork class | Class 1 — re-ratification required; §11 marked provisional |
| Halt scope | Spec-writer arc halted; no spec edits written; worktree clean of spec changes |
| Predecessor | §11 operator ratification (this same session, ~30 min prior) |
| Next step | Operator AskUserQuestion on §14.A/B/C/D/E; on ratification, spec-writer re-invocation with revised structural shape |
| Memory entries to update post-ratification | `[[h-t-cp-16-17-retire-ready-gate-runtime-composer-arcs]]` (revise gate-shape analysis); `[[retirement-batch-11-v1-5-re-invocation]]` (no change — batch-11 status unchanged) |

## §16 §14 operator ratification (2026-05-23, immediate post-§13)

| Sub-decision | Ratified | Per recommendation? |
|---|---|---|
| §14.A ratification scope | **Amend §11 in-place** — preserve §6.D (operator-opt-in RETIRE-READY); revise §6.A (split per primitive), §6.B (NO bundled — split), §6.C (re-scoped per §14.D), §6.E (NOT C-RT-19 extension) | Per recommendation |
| §14.B architecture | **Accept §13.6** — Memory at NEW callback-registry contract consumed by C-RT-15; Files at NEW sibling REST-client contract (deferred per §14.C); MCP / C-RT-19 unchanged | Per recommendation |
| §14.C arc split | **Memory-only at this opening; Files arc deferred indefinitely** — no current downstream blocker; operator-discretion timing for Files re-open when operational driver surfaces | Per recommendation |
| §14.D Memory e2e operational scope | **Local-filesystem backend for retirement-gate** — `MemoryToolStorageBackend.FILESYSTEM` round-trip with real Anthropic API call; single-credential-set (Anthropic only); S3 backend deferred to follow-on retirement-batch arc when S3 infra availability + operator cost-acceptance ratified separately | Per recommendation |
| §14.E Files arc timing | **N/A** (Files arc deferred indefinitely per §14.C) | — |

**§11 amendments (in-place)** per §14.A:

| §11 row | v1 disposition (PROVISIONAL) | v2 disposition (RATIFIED 2026-05-23 per §14) |
|---|---|---|
| §6.A spec axis home | A.iii Split (runtime owns NEW §14.X MemoryToolHost + §14.Y FilesAPIHost contracts; AS adds §14 footer references) — **VOID** | **A.iv per-primitive binding sites per §13.6.A** — Memory at NEW callback-registry contract (runtime spec NEW §14.12 C-RT-22 `MemoryToolRegistry` + `MemoryToolStorageBackendProtocol`) consumed by C-RT-15 RuntimeLLMDispatcher composer-step amendment; AS spec v1.4 §14.7 footer note repointed. Files arc deferred per §14.C |
| §6.B bundled vs split | B.i Bundled CP-16+17 single arc (~7-10 commits) — **VOID** | **B.iv Memory arc only** (~5-8 commits per §13.6.C); Files arc deferred indefinitely per §14.C |
| §6.C e2e exercise scope | C.ii+C.iv Real backends (S3 memory + live Anthropic Files API) — **REVISED** | **C.vii Local-filesystem memory backend** (`MemoryToolStorageBackend.FILESYSTEM`) round-trip with real Anthropic API call; single-credential-set retirement-gate; S3 backend deferred to follow-on retirement-batch arc |
| §6.D retirement-gate stringency | D.i Operator-opt-in RETIRE-READY | **PRESERVED** — structural criterion-B MET at landing arc; RETIRED gated on operator-bound config + e2e per §14.D revised scope |
| §6.E invocation site | E.ii Tool dispatch routing extension via C-RT-19 RuntimeToolDispatcher — **VOID** | **E.iv No C-RT-19 extension** per §13.6.A — Memory binds at C-RT-15 §14.5 LLM dispatcher composer-step amendment (callback-injection when `tools=[memory_tool]` in step-effective-binding); no new StepKind values |
| §6.F prioritization | N/A (was conditional on §6.B split) | N/A (Memory-only per §14.C; Files deferred) |

**Status transition: §11 PROVISIONAL → §11 RATIFIED-AMENDED.** Fork-doc cleared for spec-writer re-invocation with Memory-only scope per §16 amended dispositions.

**Revised arc shape under §16 ratification:**

1. Runtime spec v1.16 → v1.17:
   - NEW §14.12 C-RT-22 `MemoryToolStorageBackendProtocol` + `MemoryToolRegistry` contract (CRUD callbacks per ADR-D3 §1.1 #11 — `view` / `create` / `delete` / `str_replace` / `insert` on `/memories` paths; deployment-surface-keyed backend selection per `MemoryToolStorageBackend` enum)
   - C-RT-15 §14.5 amendment: callback-injection composer-step when LLM-dispatch composes `tools=[...]` arg with memory tool element in step-effective-binding; emit `memory.*` 6-attr namespace per AS spec §14.7 at each callback invocation
   - §3 C-RT-02 RuntimeConfig NEW optional field `memory_tool_backend_config: MemoryToolBackendConfig | None`
   - §4 C-RT-04 HarnessContext NEW field `memory_tool_registry: MemoryToolRegistry` (stage 5)
2. AS spec v1.4 → v1.5: §14.7 NEW producer-site reference note (parallel to v1.4 §14.3 mcp.* footer — repointed per §13.6.D); §14.6 `files.*` namespace UNCHANGED (Files arc deferred per §14.C)
3. Runtime plan v2.13 → v2.14 (separate `implementation-planner` arc): NEW L-M cluster decomposing Memory tool primitive (storage-backend protocol + filesystem implementation + callback injection + e2e — 3-5 units estimated)
4. E2e exercise (separate arc): real Anthropic API `messages.create` with `tools=[memory_tool]` + filesystem storage backend round-trip

**Operator-discretion timing.** Spec-writer + implementation-planner + implementation arcs may open this session OR defer. Files arc remains bounded-residual indefinitely (re-opens when operational driver surfaces).
