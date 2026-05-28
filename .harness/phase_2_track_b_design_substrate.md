# Phase 2 — Track B Operator-Facing CLI Design Substrate

**Filed:** 2026-05-28 (Phase 7 sub-phase 7b post-Phase-1-status-cascade-sweep arc at merge commit `2ffaf1a`).
**Class:** Phase 2 design substrate — authors NEW H_T design surfaces under X-AL-3 (no silent design extension at execution-time). Operator scoping session ratification gates Phase 2b implementation.
**Mode:** Implementation-planner / systems-architect joint scoping under skill discipline.
**Authority anchor:** Operator AskUserQuestion 2026-05-28 4-axis Q-set ratification (this session); fork `class_1_tension_runtime_entrypoint_design_gap.md` Track B partition (filed 2026-05-16).
**Status:** PROPOSING — operator decides on §6 sub-questions + ratifies the design before Phase 2b atomic-unit decomposition opens.

---

## §1 Authorized scope (4 operator-ratified decisions, 2026-05-28)

The operator ratified maximum-completeness across all 4 architectural axes via AskUserQuestion 2026-05-28 (this session, post-Phase-1-merge):

| Axis | Decision | Effort estimate (CC) |
|---|---|---|
| **A1 — Scope frame** | **Full-spec**: resume + OTel + audit-ledger + cost-attribution + HITL webhook + admin CLI wired at first cut | ~2 weeks |
| **A2 — CLI invocation shape** | **Both (daemon optional)**: one-shot subprocess default; optional `--daemon` flag spawns/attaches to persistent process | +~1.5 weeks |
| **A3 — Workflow file format** | **Declarative YAML/TOML**: `harness run workflow.yaml` parses declarative manifest into `WorkflowObject` | +~1 day (loader) + Class 1 fork ratification time (schema) |
| **A4 — Config source** | **Layered**: env < config file < CLI flags (3-layer precedence) | +~2 hr |

**Aggregate Phase 2 estimate:** ~3-4 weeks CC implementation; +1-2 sub-fork ratification cycles (Q-A daemon protocol; Q-B YAML manifest schema).

The 4 ratifications are the **authority anchor** for this design substrate. Down-scoping any axis requires re-ratification.

---

## §2 Pre-existing architectural anchors (DO NOT extend silently)

The Track B design lands atop a non-trivial pre-existing architectural substrate authored at Phase 2 session-3 (runtime spec v1.1 → v1.10 lineage). Material anchors:

| Anchor | Authority | Implication for Track B |
|---|---|---|
| **§14.8.3 v1.10 Q1=α CC-initiates topology** | runtime spec v1.10 `0919a9b` + memory `[[phase-7-bootstrap-status]]` | H_T hosts FastMCP server; Claude Code is registered MCP client; workflows are invoked by Claude Code calling the `run_workflow` MCP tool. **`harness run` CLI is an ADDITIONAL operator-facing entrypoint, NOT a replacement for the MCP-tool path.** |
| **§14.8.3 Q2 `api.run()` thin-wrapper** | runtime spec v1.10 | `harness_runtime.api.run(workflow, config)` is Track A Python API; internally delegates to MCP-tool path. **`harness run` CLI delegates to `api.run()`.** |
| **C-RT-08 `async def run(workflow, config=None) -> RunResult`** | runtime spec §8 | Existing operator-facing async API. **CLI is the sync-process wrapper around this.** |
| **`[project.scripts]` Track A admin stubs** | `harness-runtime/pyproject.toml:18-22` | `harness-inspect` + `harness-shutdown` already wired. **NEW `harness-run` entrypoint slots into this section.** |
| **`U-RT-62` FastMCP server hosting + `run_workflow` tool** | runtime plan v2.10 + memory `[[phase-7-bootstrap-status]]` | Daemon-mode IS the existing FastMCP server. **No new daemon protocol needed unless operator selects Q-A option β.** |
| **`RuntimeConfig` field-set canonical at v1.31** | runtime spec §3 C-RT-03 (28 fields enumerated) | Config-file loader projects file content INTO this Pydantic model. **No new RuntimeConfig fields owed at Track B; existing field-set is canonical.** |

**Critical reframe:** Given §14.8.3 Q1=α, the architected primary invocation surface is **Claude Code calling `run_workflow` MCP tool** against the H_T-hosted FastMCP server. The `harness run` CLI is operator-facing convenience for: (i) local dev/test against a workflow file; (ii) admin/CI/scripting invocation outside Claude Code; (iii) operators who do not use Claude Code as their MCP client. The 4 ratified decisions remain valid against this framing.

---

## §3 NEW H_T design surfaces being added (X-AL-3 surface enumeration)

The 4 ratified decisions surface **4 new H_T design contracts** that must be authored at runtime spec amendment + sub-fork ratification before Phase 2b implementation opens.

### §3.1 Surface S1 — `harness run` CLI contract

**Routing target:** runtime spec §13 (C-RT-13 admin stub semantics) extended with NEW §13.N operator-facing `harness run` shape.

**Contract surface:**
- CLI invocation: `harness run <workflow-file> [--config <path>] [--daemon] [--<flag>=...] [args...]`
- Argparse / Click / Typer dispatcher (implementer discretion)
- One-shot default: spawn process → load workflow → invoke `api.run()` → emit RunResult to stdout → exit
- `--daemon` flag: connect to persistent FastMCP server (S2) and submit workflow invocation via MCP client
- Exit codes: 0 = success; 1 = workflow failure (RunResult.status != COMPLETED); 2 = manifest parse error; 3 = config error; 4 = runtime bootstrap error
- Output: human-readable text default; `--output=json` switches to JSON RunResult serialization
- Logging: stderr by default; respects existing OTel collector placement per `CollectorPlacement.IN_PROCESS`

**Open sub-question (Q-Q):** `harness run` should support `--watch` / `--reload` for dev-loop ergonomics — deferred to operator decision at sub-arc.

### §3.2 Surface S2 — Daemon mode + IPC mechanism

**Routing target:** runtime spec §13 NEW §13.M `harness daemon` contract + IPC mechanism declaration.

**Open sub-question (Q-A) — operator decides at sub-fork:**
- **(α) Daemon = the existing FastMCP server.** `harness daemon` starts the same `HarnessMCPServer` per §14.8.3; `harness run --daemon` is an MCP client that submits workflow invocations via the `run_workflow` tool. **Pro:** Reuses existing architecture; ZERO new IPC mechanism; symmetric with Claude Code invocation path. **Con:** Requires MCP transport (stdio/HTTP/Unix-socket) bootstrap on operator host; operator must configure both daemon AND CLI client.
- **(β) Daemon = separate IPC mechanism** (Unix socket + lightweight RPC; or HTTP + JSON; or in-memory shared-state). `harness daemon` is NOT the FastMCP server. **Pro:** Decouples CLI from MCP protocol complexity. **Con:** NEW IPC contract = NEW X-AL-3 surface; bifurcates the workflow-invocation paths (Claude Code via MCP; CLI via custom IPC); doubles the daemon surface.

**Recommendation:** (α). Reuse the existing `HarnessMCPServer` substrate. The MCP transport at protocol level already supports stdio + HTTP + WebSocket per MCP spec; operator picks transport at config time. ZERO new IPC contract. Sub-fork doc title: `class_1_fork_harness_run_daemon_protocol.md` (files only if operator selects β).

### §3.3 Surface S3 — YAML/TOML workflow manifest schema (X-AL-3 surface)

**Routing target:** runtime spec NEW §14.N `WorkflowManifest` schema + loader contract.

**Open sub-question (Q-B) — operator decides at sub-fork ratification (REQUIRED before Phase 2b open):**

**Sub-fork file:** `class_1_fork_harness_run_yaml_manifest_schema.md` (REQUIRED — operator picking YAML at A3 ratifies that there will be a schema; the schema itself is a separate ratification per X-AL-3).

Operator must decide:
- **Q-B1 — Manifest top-level shape:**
  - (a) **Step-list**: `steps: [{kind, payload}, ...]` — linear; closest to existing `WorkflowObject.steps` Protocol shape
  - (b) **DAG**: `steps: [...]` + `edges: [...]` — explicit graph; richer; mismatches current linear-by-default driver
  - (c) **Python-module reference**: `workflow_module: my_workflow` — YAML is a thin envelope; actual workflow stays in Python
- **Q-B2 — File format:**
  - (a) YAML only (most common DevEx; PyYAML or strictyaml)
  - (b) TOML only (Python-native via tomllib; less expressive)
  - (c) Both, file-extension dispatch
- **Q-B3 — Schema versioning:**
  - (a) Top-level `version: 1` required; loader rejects unknown versions
  - (b) Implicit version 1; future versions add `version:` field; loader assumes 1 if absent
- **Q-B4 — Extensibility:**
  - (a) Closed schema — unknown fields raise
  - (b) Open schema — unknown fields passed through to driver as `step_payload`

**Recommendation:** Q-B1=(a) step-list (matches existing Protocol); Q-B2=(c) both (Python tomllib is stdlib, YAML is operator-friendly default); Q-B3=(a) explicit version (forward-compat); Q-B4=(a) closed schema (X-AL-3 discipline — unknown fields surface as errors, not silent passthrough).

### §3.4 Surface S4 — Layered config precedence + config file schema

**Routing target:** runtime spec §3 C-RT-03 NEW §3.N `RuntimeConfigSource` precedence contract.

**Open sub-question (Q-C) — config file path + format:**
- (α) **`.harness/config.toml`** at workspace root (in `.harness/` namespace; co-resident with fork records)
- (β) **`harness.toml`** at workspace root (top-level; ruff/pytest convention)
- (γ) **`[tool.harness]` section in `pyproject.toml`** (Python-tool convention; piggybacks existing file)

**Recommendation:** (β) `harness.toml` at workspace root. **Rationale:** (i) Tool-convention parity with ruff/pytest/uv; (ii) `.harness/` is for fork records (operational artifacts), not operator-authored config; (iii) `pyproject.toml` section couples harness config to Python project metadata which is wrong abstraction layer.

**Precedence (fixed at A4 ratification):** environment variables → config file → CLI flags (lowest priority → highest priority). Implementation: Pydantic v2 `BaseSettings` with env source + file source + CLI source.

---

## §4 Spec extension points (Phase 2a deliverables)

| Spec | Section | Amendment shape | Class |
|---|---|---|---|
| `Spec_Harness_Runtime_v1.md` v1.34 → v1.35 | §3 C-RT-03 + §13 C-RT-13 + NEW §14.N + NEW §14.M | NEW §14.N `WorkflowManifestLoader` contract; NEW §14.M `HarnessRunCLI` contract; §13 extended with operator-facing CLI shape; §3 extended with `RuntimeConfigSource` precedence | Substantive — requires NEW C-RT-NN contract IDs (~2-3 new C-RT-NN slots) |
| Runtime plan v2.30 → v2.31 | NEW L-cluster (sketch §7) | NEW 5-7 atomic units decomposing S1-S4 + e2e | Substantive |
| `Implementation_Plan_Action_Surface_v1_4.md` | NO amendment | AS-axis unchanged | None |
| `Implementation_Plan_Control_Plane_v2_27.md` | NO amendment | CP-axis unchanged | None |
| `Implementation_Plan_Operational_Discipline_v2_23.md` | NO amendment | OD-axis unchanged | None |
| `Implementation_Plan_Information_Substrate_v2_3.md` | NO amendment | IS-axis unchanged | None |
| `Cross_Axis_Composition_Document_v2_15.md` | NO amendment | Track B is entrypoint layer, not cross-axis | None |
| ADR-F4 v1.1 (workflow lifecycle) | NO amendment | Lifecycle contract unchanged; CLI is invocation surface for an unchanged lifecycle | None |
| ADR-D2 v1.2 (per-deployment-surface sandbox) | NO amendment | CLI is local-process surface; sandbox-tier mapping per existing ADR-D2 enum unchanged | None |
| PRD v1.1 | NO amendment | Observable behavior unchanged; CLI is invocation surface, not behavior surface | None |

**Cross-axis cascade discipline:** Track B is intra-runtime-axis. ZERO cross-axis cascade. Verified by inspection of the 4 ratified decisions against §2 anchors.

---

## §5 Sub-fork file enumeration (REQUIRED before Phase 2b open)

The 4 ratified decisions at A1-A4 surface 2 sub-forks per X-AL-3 (no silent H_T design extension). Operator ratification of these sub-forks is REQUIRED before Phase 2b atomic-unit decomposition opens.

| Sub-fork | File path | Status | Gates |
|---|---|---|---|
| **SF-1 — YAML manifest schema** | `.harness/class_1_fork_harness_run_yaml_manifest_schema.md` | TO-BE-FILED | Q-B1 + Q-B2 + Q-B3 + Q-B4 ratification; gates all loader + e2e units |
| **SF-2 — Daemon protocol** | `.harness/class_1_fork_harness_run_daemon_protocol.md` | TO-BE-FILED IF operator selects Q-A=(β) | Q-A ratification; gates daemon-mode units |

**Note:** If operator selects Q-A=(α) — daemon-is-FastMCP-server (recommended) — SF-2 is foreclosed; only SF-1 is required.

---

## §6 Open sub-questions (operator decides at sub-arc opens)

| Q | Surface | Question | Recommendation |
|---|---|---|---|
| **Q-A** | S2 daemon | Daemon = existing FastMCP server (α) vs separate IPC (β)? | **(α)** — reuse FastMCP; ZERO new IPC contract |
| **Q-B1** | S3 manifest | Top-level shape: step-list (a) vs DAG (b) vs Python-module-ref (c)? | **(a) step-list** — matches existing `WorkflowObject` Protocol |
| **Q-B2** | S3 manifest | File format: YAML only (a) vs TOML only (b) vs both (c)? | **(c) both** — file-extension dispatch |
| **Q-B3** | S3 manifest | Schema versioning: explicit `version:` (a) vs implicit v1 (b)? | **(a) explicit** — forward-compat |
| **Q-B4** | S3 manifest | Extensibility: closed schema (a) vs open passthrough (b)? | **(a) closed** — X-AL-3 discipline |
| **Q-C** | S4 config | Config file path: `.harness/config.toml` (α) vs `harness.toml` (β) vs `[tool.harness]` in pyproject (γ)? | **(β)** — tool-convention parity |
| **Q-D** | S2 daemon (gated on Q-A=α) | Resume across daemon restarts: state-ledger reload only (a) vs daemon-internal queue (b)? | **(a)** — F2-canonical state-ledger is the resume contract; no daemon-side state |
| **Q-E** | S1 CLI | HITL webhook delivery: daemon hosts webhook endpoint (a) vs external operator-supplied URL only (b)? | **(b)** — daemon doesn't host HTTP; HITL webhook is operator-supplied per existing C-RT-20 |
| **Q-F** | S1 CLI | Logging output: stderr only (a) vs stderr + structured log file (b)? | **(a)** — OTel collector handles structured emission; CLI stderr is operator-facing text |
| **Q-G** | S1 CLI | Workflow exit code semantics: COMPLETED → 0 only (a) vs COMPLETED + PARTIAL → 0 (b)? | **(a)** — strict; PARTIAL surfaces as exit 1 (operator can override per workflow) |
| **Q-H** | S3 manifest | YAML-format library: PyYAML (a) vs `strictyaml` (b) vs `ruamel.yaml` (c)? | **(b) strictyaml** — type-safe parse; rejects implicit type-coercion (e.g., "yes"/"no" → bool) per X-AL-3 discipline |
| **Q-I** | S4 config | CLI flag library: argparse (a) vs Click (b) vs Typer (c)? | **(c) Typer** — Pydantic-friendly; type annotations drive flag generation; aligns with existing Pydantic v2 stack |
| **Q-J** | S1 CLI | Subcommand structure: flat (`harness run`, `harness inspect`, `harness shutdown`) (a) vs nested (`harness workflow run`, `harness daemon start`) (b)? | **(a) flat** — preserves Track A precedent (`harness-inspect`, `harness-shutdown`); shorter typing surface |
| **Q-K** | S2 daemon (gated on Q-A=α) | MCP transport for daemon ↔ CLI: stdio (a) vs HTTP (b) vs Unix-socket (c) vs WebSocket (d)? | **(c) Unix-socket** — local-process IPC; no port-collision risk; cross-platform per MCP transport plugins |
| **Q-Q** | S1 CLI | `--watch` / `--reload` dev-loop mode: include at first cut (a) vs defer (b)? | **(b) defer** — dev-loop ergonomics is iteration-2 |

**Operator ratification routing:** All 13 sub-questions (Q-A through Q-K + Q-Q) ratified in a single AskUserQuestion round opens SF-1 + SF-2 (if needed) authoring; ratification of SF-1 + SF-2 opens Phase 2b atomic-unit decomposition.

---

## §7 Phase 2b atomic-unit decomposition (sketch — pending §6 ratification)

Pending operator ratification of §6 Q-set, the Phase 2b implementation plan adds NEW L-cluster (next free L-number per runtime plan v2.30 sequence) decomposing:

| Unit (placeholder ID) | Surface | Acceptance criteria sketch | Dependencies |
|---|---|---|---|
| **U-RT-102** | S1 CLI scaffolding | Typer app + `harness run` subcommand + arg parser + exit code mapping; no workflow execution | (none — within-cluster root) |
| **U-RT-103** | S4 config loader | `BaseSettings` 3-source loader (env + harness.toml + CLI flags); fixed precedence; YAML/TOML config-file parser | U-RT-102 |
| **U-RT-104** | S3 manifest loader | `WorkflowManifestLoader` Protocol + step-list shape implementation + version validation + closed-schema rejection | U-RT-103 |
| **U-RT-105** | S3 manifest → WorkflowObject projection | YAML/TOML manifest → `WorkflowObject` Protocol satisfaction (per existing C-RT-08 surface) | U-RT-104 |
| **U-RT-106** | S1 CLI one-shot mode | `harness run <file>` invokes `api.run(workflow, config)` synchronously; emits RunResult to stdout | U-RT-105 |
| **U-RT-107** | S2 daemon-mode CLI client | `harness run <file> --daemon` instantiates MCP client; submits via `run_workflow` tool; receives RunResult | U-RT-106 + existing U-RT-62 FastMCP server |
| **U-RT-108** | S2 daemon-mode entrypoint | `harness daemon` admin CLI starts persistent `HarnessMCPServer` with Unix-socket transport per Q-K | U-RT-107 |
| **U-RT-109** | E2E integration | Real YAML manifest → CLI invocation → real workflow execution → RunResult emission; one-shot + daemon both verified | U-RT-108 |

**Net additions:** 8 atomic units (U-RT-102 through U-RT-109); 1 NEW L-cluster; 7 within-cluster edges + 1 cluster-boundary edge to U-RT-62. ZERO cross-axis edges.

---

## §8 Implementation order (Phase 2b sequencing)

1. **Sub-fork SF-1 ratification** (Q-B Q-set) — REQUIRED; gates U-RT-104 + U-RT-105 + U-RT-109
2. **Sub-fork SF-2 ratification** (Q-A) — REQUIRED IF Q-A=(β); foreclosed if Q-A=(α)
3. **Runtime spec v1.34 → v1.35 amendment** authoring NEW §14.M + §14.N + §13.N + §3.N — implementation-planner + spec-writer arc
4. **Runtime plan v2.30 → v2.31 amendment** authoring NEW L-cluster (U-RT-102..U-RT-109) — implementation-planner arc
5. **Phase 2b implementation** following dependency-graph order:
   - U-RT-102 (CLI scaffold) → U-RT-103 (config) → U-RT-104 (manifest loader) → U-RT-105 (projection) → U-RT-106 (one-shot) → U-RT-107 (daemon client) → U-RT-108 (daemon entrypoint) → U-RT-109 (e2e)

**Critical-path estimate (CC):** SF-1 ratification (~30 min) → spec/plan amendments (~2 hr) → U-RT-102..U-RT-109 (~8-12 hr per unit ×8 units ≈ ~3 weeks CC; can parallelize U-RT-103 + U-RT-104 after U-RT-102).

---

## §9 Cross-axis cascade verification

**Verified ZERO cross-axis cascade** by grep:

| Artifact | Touched at Phase 2? | Reason |
|---|---|---|
| AS spec / plan | NO | CLI is operator entrypoint; AS-axis (tool contracts + MCP + sandbox + skills) consumed via existing api.run() chain |
| CP spec / plan | NO | CP-axis (workflow driver + routing + retry/breaker) consumed via existing api.run() chain |
| OD spec / plan | NO | OD-axis (HITL + audit + cost + observability) consumed via existing api.run() chain |
| IS spec / plan | NO | IS-axis (state-ledger + index + cache + path-class) consumed via existing api.run() chain |
| CXA | NO | Entrypoint layer is intra-runtime-axis; no new typed cross-axis edges |
| ADR | NO | No new F-class architectural decision; Track B is implementation of ADR-D2 deployment surface commitment |
| ADD | NO | Coherent architectural overview unchanged at entrypoint addition |
| PRD | NO | Observable behavior unchanged; CLI is invocation surface |
| Workspace `CLAUDE.md` | YES (post-impl) | §2.3 runtime spec row + §2.4 runtime plan row bumps at v1.35 + v2.31 publication |

---

## §10 Status posture + ratification gates

**v1.0 PROPOSING.** This design substrate is filed for operator review.

**Ratification gates (in order):**
1. **Gate G1 — §6 Q-set ratification** (operator AskUserQuestion: Q-A + Q-B1-4 + Q-C + Q-D + Q-E + Q-F + Q-G + Q-H + Q-I + Q-J + Q-K + Q-Q)
2. **Gate G2 — SF-1 filing + ratification** (`.harness/class_1_fork_harness_run_yaml_manifest_schema.md` — operator ratifies the YAML schema body)
3. **Gate G3 — SF-2 filing + ratification** (`.harness/class_1_fork_harness_run_daemon_protocol.md` — ONLY IF Q-A=(β); else foreclosed)
4. **Gate G4 — Runtime spec amendment** (v1.34 → v1.35 authoring NEW §14.M + §14.N + §13.N + §3.N)
5. **Gate G5 — Runtime plan amendment** (v2.30 → v2.31 authoring NEW L-cluster U-RT-102..U-RT-109)
6. **Gate G6 — Phase 2b implementation arc opens** (atomic-unit consumption per skill `phase-7-implementation` discipline)

**Post-G6 deliverables:**
- Closes `class_1_tension_runtime_entrypoint_design_gap.md` Track B partition
- Unblocks AS-8d + OD-5 RETIRE-READY → RETIRED via first real workflow exercise
- Enables deployment-readiness Phase 3 (substantive implementation arcs)

---

## §11 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/phase_2_track_b_design_substrate.md` |
| Authored at | 2026-05-28 (Phase 7 sub-phase 7b, post-Phase-1-status-cascade-sweep) |
| Authoring authority | Operator AskUserQuestion 2026-05-28 4-axis ratification + `class_1_tension_runtime_entrypoint_design_gap.md` Track B partition |
| Predecessor | `class_1_tension_runtime_entrypoint_design_gap.md` (filed 2026-05-16; Track A PARTIALLY-CLOSED 2026-05-20) |
| Successor consumption | Gate G1 operator ratification → Gate G2 SF-1 authoring → Gate G6 Phase 2b implementation |
| Revision policy | This file is canonical for Phase 2a scoping; revisions absorbed at delta-only-design-substrate convention |
| Cross-axis cascade | ZERO — verified §9 |
| Class | Phase 2 design substrate — NEW H_T design under X-AL-3 |
