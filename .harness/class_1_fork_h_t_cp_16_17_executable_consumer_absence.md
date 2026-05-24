---
fork_class: Class 1 (halt-execution — X-AL-3 surface)
fork_id: class_1_fork_h_t_cp_16_17_executable_consumer_absence
filed_at: 2026-05-23
filed_against_head: b2cf37b
status: PROPOSING — operator ratification required at §6 ambiguities
routing_target: Runtime spec revision-pass (preferred per L9-septies precedent) OR AS spec revision-pass (alternative per namespace-co-residence) — §6.A operator decision
related_substitutions: H_T-CP-16 (memory.*) + H_T-CP-17 (files.*)
related_memories: [[h-t-cp-16-17-retire-ready-gate-runtime-composer-arcs]], [[retirement-batch-11-v1-5-re-invocation]], [[fork-h-t-cp-18-phantom-retirement-cite]]
---

# Class 1 fork: H_T-CP-16 + H_T-CP-17 executable consumer absence

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
