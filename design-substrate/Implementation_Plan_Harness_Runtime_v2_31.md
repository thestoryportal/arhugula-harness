# Implementation Plan — Harness Runtime (v2.31)

*Delta over v2.30. v2.31 is a Phase-7 Phase-2a Gate G5 substantive amendment authoring NEW L9-sedecies 8-unit linear-chain cluster decomposing runtime spec v1.34 → v1.35 NEW §14.18 C-RT-29 `HarnessRunCLI` + NEW §14.19 C-RT-30 `WorkflowManifestLoader` + NEW §13.4 operator-facing CLI subcommand extension + NEW §3.7 `RuntimeConfigSource` 3-source layered precedence per Phase 2a design substrate G1-RATIFIED + SF-1 G2-RATIFIED en-bloc operator AskUserQuestion ratifications 2026-05-28. Unit count 99 → 107 (+8); ZERO cross-axis cascade per design substrate §9 + SF-1 §8 + spec v1.35 §14.18.5 + §14.19.6.*

## §0 Change note (v2.30 → v2.31)

### §0.1 Revision context — Track B operator-facing CLI absorption

Per `.harness/phase_2_track_b_design_substrate.md` v1.1 G1-RATIFIED (operator AskUserQuestion 2026-05-28 en-bloc ratification of all 17 sub-questions Q-A through Q-N per recommended defaults) + `.harness/class_1_fork_harness_run_yaml_manifest_schema.md` G2-RATIFIED (operator AskUserQuestion 2026-05-28 en-bloc ratification of all 6 Q-S sub-decisions Q-S1 through Q-S6 per recommended defaults) + runtime spec v1.34 → v1.35 amendment at commit `f51874a` (Gate G4). v2.31 decomposes the 4 NEW H_T design surfaces (S1 CLI / S2 daemon / S3 YAML manifest / S4 layered config) into 8 atomic units per topological-sort traversal discipline + Phase-7 sub-phase 7b axis-stream implementation governance.

The L9-sedecies cluster shape mirrors prior L9-undecies (U-RT-87/88/89 pause-resume) + L9-quaterdecies (U-RT-96/97/98 webhook-composer-binding-chain) + L9-quindecies (U-RT-99/100/101 skill-activation) precedents: substrate carrier → factory + binding chain → consumer body → e2e verification. 8-unit cardinality reflects the broader scope (S1 + S2 + S3 + S4 surfaces span 4 substrate authoring + 4 consumer-body authoring units).

### §0.2 Sections revised

§0 (this change note); §1 NEW L9-sedecies cluster authoring (U-RT-102 through U-RT-109); §2 dependency graph + DAG verification; §3 adjacent observations + carry-forward. All v2.30 unit bodies preserved verbatim per delta-only-plan-chain convention. U-RT-94 v2.30 Reading (H) absorption PRESERVED VERBATIM.

### §0.3 ZERO cross-axis cascade

Per design substrate §9 + SF-1 §8 + runtime spec v1.35 §14.18.5 + §14.19.6: Track B is intra-runtime-axis. NO CP / AS / OD / IS / CXA / ADR / ADD / PRD plan or spec amendment owed. Workspace `CLAUDE.md` §2.4 runtime plan row bump owed at v2.31 publication (sibling co-publication this arc).

---

## §1 NEW L9-sedecies cluster — U-RT-102 through U-RT-109

### §1.1 Cluster framing

| Surface | Units | Within-cluster dependencies |
|---|---|---|
| **S1 + S4 CLI scaffolding + config** | U-RT-102 → U-RT-103 | linear |
| **S3 manifest loader + projection** | U-RT-104 → U-RT-105 | linear (depends on U-RT-103 for config-supplied paths) |
| **S1 one-shot mode** | U-RT-106 | depends on U-RT-105 + U-RT-103 |
| **S2 daemon + client** | U-RT-107 → U-RT-108 | linear (entrypoint-before-client per design substrate v1.1 advisor-fix dep-order correction) |
| **E2E integration** | U-RT-109 | depends on U-RT-108 (all sibling surfaces converge at e2e) |

Total 8 atomic units; 7 within-cluster edges; 1 cluster-boundary edge to existing U-RT-62 (FastMCP server / HarnessMCPServer) consumed at U-RT-107 daemon-entrypoint.

### §1.2 U-RT-102 — CLI scaffolding (Typer parent app + subcommand stubs)

**Implements:** runtime spec v1.35 §14.18.1 subcommand surface + §13.4 operator-facing CLI subcommand extension.

**Spec:** §14.18 C-RT-29 `HarnessRunCLI`; §13.4 NEW subcommand registration discipline.

**Signatures:**
- NEW module `harness_runtime.cli` with `main()` callable
- Typer parent app: `app = typer.Typer(name="harness", help="Multi-LLM Agent Harness operator-facing CLI")`
- 3 NEW subcommand stubs at v2.31 scope: `@app.command("run")`, `@app.command("daemon")`; `inspect` + `shutdown` continue at standalone `harness-inspect` + `harness-shutdown` per §13.4 PRESERVED VERBATIM discipline
- Stub bodies: `typer.echo("Not yet implemented — landing at U-RT-NN")` + `raise typer.Exit(code=4)` (RT-FAIL placeholder)

**`[project.scripts]` extension:** NEW entry `harness = "harness_runtime.cli:main"` at `harness-runtime/pyproject.toml`.

**Dependencies (NEW dep declarations):**
- `typer>=0.12` (Q-I=c at G1)

**Acceptance criteria:**
1. `harness --help` lists `run` + `daemon` subcommands at top level
2. `harness run --help` shows arg/flag inventory per §14.18.1 (file positional + `--config` + `--daemon` + `--output` + `--provider` + `--model` + `--tenant-id`)
3. `harness daemon --help` shows daemon-mode flags (subset per Q-I)
4. `harness run <file>` exits with code 4 + stderr-echo of placeholder message (stub body)
5. `harness daemon` exits with code 4 + stderr-echo of placeholder message
6. `harness inspect` + `harness shutdown` invocations route to existing Track A standalone binaries (PRESERVED — no integration at U-RT-102)
7. Typer arg-parse failure (e.g., unknown flag) exits with code 3 + `RT-FAIL-CLI-ARG-INVALID` raised

**Files:**
- NEW `harness-runtime/src/harness_runtime/cli/__init__.py` (re-exports `main`)
- NEW `harness-runtime/src/harness_runtime/cli/app.py` (Typer parent app + subcommand stubs)
- EDIT `harness-runtime/pyproject.toml` (NEW `[project.scripts]` row + NEW `typer` dep)

**Tests (NEW at `harness-runtime/tests/test_cli_scaffold.py`):**
- `test_harness_top_help_lists_run_and_daemon_subcommands`
- `test_harness_run_help_shows_flag_inventory`
- `test_harness_daemon_help_shows_flag_inventory`
- `test_harness_run_stub_exits_code_4`
- `test_harness_daemon_stub_exits_code_4`
- `test_unknown_flag_exits_code_3_with_arg_invalid_fail_class`

**Depends on:** none (cluster root)

---

### §1.3 U-RT-103 — Config loader (pydantic-settings 3-source precedence)

**Implements:** runtime spec v1.35 §3.7 `RuntimeConfigSource` 3-source layered precedence.

**Spec:** §3.7 (NEW at v1.35) + Q-C=β ratification (harness.toml at workspace root) + Q-L=b ratification (secrets via ADR-F5 keyring, plaintext config-file REJECTED).

**Signatures:**
- NEW class `harness_runtime.config_source.RuntimeConfigSource(pydantic_settings.BaseSettings)` subclassing the existing `RuntimeConfig` field-set + binding env-var source (`HARNESS_*` prefix) + TOML config-file source (`harness.toml` at workspace root by default; overridable) + CLI-flag source
- NEW classmethod `RuntimeConfigSource.load(config_file: Path | None = None, cli_overrides: dict[str, Any] = {}) -> RuntimeConfig`
- Implements 3-source precedence: env vars (lowest) → config file → CLI flags (highest)
- Secrets exclusion: rejects `harness.toml` keys matching known-secret-field names (e.g., `*_api_key`, `secret_*`) per Q-L=b

**Dependencies (NEW dep declarations):**
- `pydantic-settings>=2.0` (per spec §3.7 implementation discipline)

**Acceptance criteria:**
1. Default load (no env / no config file / no CLI) returns `RuntimeConfig()` Pydantic defaults
2. `HARNESS_TENANT_ID=acme` env var → `config.tenant_id == "acme"`
3. `harness.toml` with `[runtime] tenant_id = "acme"` → `config.tenant_id == "acme"`
4. CLI override `cli_overrides={"tenant_id": "acme"}` → `config.tenant_id == "acme"`
5. Precedence test: env=X + file=Y + CLI=Z → `config.tenant_id == "Z"` (CLI wins)
6. Precedence test: env=X + file=Y (no CLI) → `config.tenant_id == "Y"` (file wins env)
7. Plaintext API-key field at `harness.toml` raises `RT-FAIL-CLI-CONFIG-LOAD` typed exception with reason "secrets must be sourced via ADR-F5 keyring"
8. TOML parse error raises `RT-FAIL-CLI-CONFIG-LOAD` with strictyaml-style location info
9. Type mismatch (e.g., `tenant_id = 42` integer) raises `RT-FAIL-CLI-CONFIG-LOAD` with Pydantic v2 validation error

**Files:**
- NEW `harness-runtime/src/harness_runtime/config_source.py`
- EDIT `harness-runtime/pyproject.toml` (NEW `pydantic-settings` dep)

**Tests (NEW at `harness-runtime/tests/test_config_source.py`):**
- 9 tests mapping to ACs above

**Depends on:** U-RT-102 (CLI parent app exists)

---

### §1.4 U-RT-104 — WorkflowManifestLoader (strictyaml + tomllib parsers + schema validation)

**Implements:** runtime spec v1.35 §14.19 C-RT-30 `WorkflowManifestLoader` contract surface + SF-1 §3.3 17-row projection contract + §4.3 9 invariants.

**Spec:** §14.19.1 + §14.19.2 typed exception taxonomy + §14.19.4 9 invariants.

**Signatures:**
- NEW class `harness_runtime.lifecycle.workflow_manifest_loader.WorkflowManifestLoader`
- Classmethod `load(path: Path) -> WorkflowObject`
- 7 NEW typed exceptions (per §14.19.2): `UnsupportedManifestFormatError`, `UnsupportedManifestVersionError`, `ManifestParseError`, `ManifestSchemaError`, `ManifestEnumValueError`, `ManifestStepIDCollisionError`, `ManifestAdmissibilityError` — all inheriting from `WorkflowManifestLoadError` base
- NEW intermediate Pydantic carrier `WorkflowManifest` (loader-internal) projecting to YAML/TOML schema body per SF-1 §3.1

**Dependencies (NEW dep declarations):**
- `strictyaml>=1.7` (Q-H=b at G1)
- `tomllib` (Python 3.11+ stdlib — no dep declaration needed)

**Acceptance criteria:**
1. `.yaml` / `.yml` file extension dispatches to `strictyaml.load`
2. `.toml` file extension dispatches to `tomllib.load`
3. Other extension (`.json`, `.xml`, etc.) raises `UnsupportedManifestFormatError`
4. `version` field absent OR not equal to `1` raises `UnsupportedManifestVersionError`
5. YAML/TOML syntax error at parse raises `ManifestParseError` with file path + line number
6. Closed-schema invariant: unknown top-level field raises `ManifestSchemaError` (Q-B4=a)
7. Closed-schema invariant: unknown nested field (e.g., inside `workflow:` or `steps[]:`) raises `ManifestSchemaError`
8. Required field missing raises `ManifestSchemaError` naming the missing field
9. Enum field with invalid value (e.g., `workload_class: WRONG`) raises `ManifestEnumValueError`
10. Two `steps[].step_id` values equal raises `ManifestStepIDCollisionError` naming the collision
11. Admissibility check: `(workload_class, engine_class)` not in U-CP-16 candidate mapping raises `ManifestAdmissibilityError`
12. Admissibility check: `topology_pattern` not admissible per U-CP-22 raises `ManifestAdmissibilityError`
13. Eager validation invariant (Q-N=a): all checks at `.load()`; no deferred-validation patterns
14. Idempotency invariant: `WorkflowManifestLoader.load(p)` called twice returns equal `WorkflowObject` instances

**Files:**
- NEW `harness-runtime/src/harness_runtime/lifecycle/workflow_manifest_loader.py`
- EDIT `harness-runtime/pyproject.toml` (NEW `strictyaml` dep)

**Tests (NEW at `harness-runtime/tests/test_workflow_manifest_loader.py`):**
- 14 tests mapping to ACs above (one per AC)
- Plus 5 fixture-driven tests with valid manifests (1 YAML / 1 TOML / 1 minimum-required-fields / 1 full-optional-fields / 1 multi-step)

**Depends on:** U-RT-103 (config supplies workspace root for default manifest path resolution; lightweight dep — loader can be tested standalone)

---

### §1.5 U-RT-105 — WorkflowObject projection (manifest → Protocol-conformant value)

**Implements:** runtime spec v1.35 §14.19.3 field-by-field projection contract.

**Spec:** §14.19.3 (manifest → WorkflowObject projection) + §14.19.4 invariant 6 (Pydantic-default discipline) + §14.19.4 invariant 8 (YAML↔TOML round-trip) + §14.19.4 invariant 9 (step_payload JSON-serializability).

**Signatures:**
- EXTEND `WorkflowManifestLoader.load(path)` from U-RT-104 to return a `WorkflowObject` Protocol-conformant value (not just the intermediate `WorkflowManifest` Pydantic carrier)
- NEW concrete projection class `harness_runtime.lifecycle.workflow_manifest_loader.LoadedWorkflow` (frozen Pydantic BaseModel satisfying the 5-property WorkflowObject Protocol)
- LoadedWorkflow ctor projects `WorkflowManifest` fields → `WorkflowObject` Protocol surface: `workflow_id`, `workload_class`, `manifest_entry` (constructs `WorkflowManifestEntry` from 12 manifest fields + Pydantic defaults), `steps` (tuple of `WorkflowStep` instances), `default_model_binding` (constructs `ModelBinding` from `provider` + `model`)

**Acceptance criteria:**
1. Minimum-required-fields manifest produces a `WorkflowObject` Protocol-conformant value
2. Full-optional-fields manifest produces equivalent `WorkflowObject` to the same workflow constructed manually via `WorkflowManifestEntry(...)` + `WorkflowStep(...)` constructors
3. Pydantic-default-discipline invariant (§14.19.4 #6): optional field absent from manifest → Pydantic carrier default applied at constructor; loader does NOT pre-supply defaults
4. YAML↔TOML round-trip invariant (§14.19.4 #8): equivalent inputs in YAML and TOML produce equal `WorkflowObject` instances — `test_yaml_toml_equivalent_inputs_produce_equivalent_workflow`
5. step_payload JSON-serializability invariant (§14.19.4 #9): each `steps[].step_payload` value MUST `json.dumps()` round-trip; non-serializable values (e.g., `datetime` objects) raise `ManifestSchemaError` at load time
6. Idempotency invariant: same file path → equal LoadedWorkflow instances on repeated load calls

**Files:**
- EDIT `harness-runtime/src/harness_runtime/lifecycle/workflow_manifest_loader.py` (extend with LoadedWorkflow class + projection logic)

**Tests (extend `harness-runtime/tests/test_workflow_manifest_loader.py`):**
- 6 NEW tests mapping to ACs above

**Depends on:** U-RT-104 (loader skeleton + intermediate carrier exist)

---

### §1.6 U-RT-106 — One-shot mode (`harness run <file>` synchronous invocation)

**Implements:** runtime spec v1.35 §14.18.1 one-shot subcommand mode + §14.18.3 SIGINT/SIGTERM drain discipline.

**Spec:** §14.18.1 (one-shot mode) + §14.18.2 exit code mapping + §14.18.3 drain.

**Signatures:**
- EDIT `harness-runtime/src/harness_runtime/cli/app.py` `@app.command("run")` body
- Replaces U-RT-102 stub with concrete one-shot dispatch: load config via `RuntimeConfigSource.load()` → load workflow via `WorkflowManifestLoader.load(path)` → invoke `harness_runtime.api.run(workflow, config)` synchronously via `asyncio.run(...)` → emit `RunResult` per `--output` mode → exit with appropriate code per §14.18.2
- SIGINT/SIGTERM handler installation: `signal.signal(SIGINT, _on_drain)`; `_on_drain` sets `ctx.drained_flag` per existing C-RT-11 drain semantics + propagates through existing `harness_runtime.shutdown.shutdown_sequence(ctx)` invocation

**Acceptance criteria:**
1. `harness run minimal.yaml` invokes `api.run()` + emits `RunResult` to stdout + exits code 0 (SUCCESS path)
2. `--output=json` flag emits JSON-serialized `RunResult` to stdout
3. `--output=text` flag (default) emits human-readable RunResult to stdout
4. Workflow FAILED status → exit code 1
5. Workflow DRAINED status → exit code 1
6. Manifest load error → exit code 2 + fail-class to stderr
7. Config load error → exit code 3
8. Runtime bootstrap error → exit code 4
9. SIGINT mid-workflow → drain propagates via `drained_flag` → `RunResult.status == DRAINED` → exit code 1
10. CLI flag overrides project correctly: `--provider=openai --model=gpt-4o` overrides `default_model_binding` from manifest
11. `--config <path>` loads non-default config-file path

**Files:**
- EDIT `harness-runtime/src/harness_runtime/cli/app.py`

**Tests (NEW at `harness-runtime/tests/test_cli_one_shot.py`):**
- 11 tests mapping to ACs above (some via subprocess invocation with fixture manifests + in-memory mock `api.run`)

**Depends on:** U-RT-105 (loader returns WorkflowObject) + U-RT-103 (config source loads RuntimeConfig)

---

### §1.7 U-RT-107 — Daemon entrypoint (`harness daemon` Unix-socket FastMCP server)

**Implements:** runtime spec v1.35 §14.18.1 daemon subcommand + Q-A=α (daemon = FastMCP server) + Q-K=c (Unix-socket transport).

**Spec:** §14.18.1 (daemon mode) + §14.18.5 daemon-mode concurrency invariant (per-MCP-session ctx isolation).

**Signatures:**
- EDIT `harness-runtime/src/harness_runtime/cli/app.py` `@app.command("daemon")` body
- Replaces U-RT-102 stub with concrete daemon entrypoint: load config via `RuntimeConfigSource.load()` → bootstrap `HarnessContext` via existing C-RT-02 9-stage orchestrator → start `HarnessMCPServer` (per existing U-RT-62) with **Unix-socket transport** (FastMCP `--transport unix --path /tmp/harness-daemon.sock` or equivalent) → block until SIGINT/SIGTERM → invoke existing `harness_runtime.shutdown.shutdown_sequence(ctx)` → exit code 0
- Default socket path: `/tmp/harness-daemon-{pidfile_path}.sock` (operator-configurable via `--socket-path` flag OR `[runtime] socket_path = "..."` in `harness.toml`)
- Multi-client concurrency invariant per §14.18.5: server MUST accept concurrent `run_workflow` invocations from distinct MCP client sessions; ConcurrentRunNotSupported MUST NOT raise on cross-client concurrency (each session has independent ctx)

**Acceptance criteria:**
1. `harness daemon` starts FastMCP server with Unix-socket transport at default socket path
2. `--socket-path <path>` overrides default
3. Server registers `run_workflow` MCP tool per existing U-RT-62
4. SIGINT/SIGTERM triggers `shutdown_sequence` invocation + exit code 0
5. Concurrent invariant: two MCP clients connecting simultaneously + each invoking `run_workflow` with independent workflow files → both workflows execute concurrently (no F2-05 ConcurrentRunNotSupported raise) — verified via integration test with 2 ephemeral MCP clients
6. Single-client repeat: 5 sequential `run_workflow` invocations from same client → all 5 complete successfully (per-call ctx isolation)
7. Daemon startup failure (e.g., socket path inaccessible) raises `RT-FAIL-CLI-DAEMON-CONNECTION` typed exception + exits code 4
8. PID file written to `RuntimeConfig.pidfile_path` per existing convention

**Files:**
- EDIT `harness-runtime/src/harness_runtime/cli/app.py`
- POSSIBLE EDIT `harness-runtime/src/harness_runtime/lifecycle/mcp_server.py` (if Unix-socket transport requires bootstrap-layer extension; otherwise FastMCP handles transparently)

**Tests (NEW at `harness-runtime/tests/test_cli_daemon.py`):**
- 8 tests mapping to ACs above (subprocess-driven integration tests with ephemeral socket paths in tmpdir)

**Depends on:** U-RT-106 (one-shot mode lands first; daemon reuses RuntimeConfigSource + bootstrap path) + cluster-boundary edge to existing U-RT-62 FastMCP server substrate

---

### §1.8 U-RT-108 — Daemon-client mode (`harness run <file> --daemon` MCP client)

**Implements:** runtime spec v1.35 §14.18.1 daemon-client mode (sibling to one-shot per §1.6).

**Spec:** §14.18.1 daemon-client mode + §14.18.5 ConcurrentRunNotSupported semantics.

**Signatures:**
- EDIT `harness-runtime/src/harness_runtime/cli/app.py` `@app.command("run")` body
- EXTEND U-RT-106 one-shot dispatch with `--daemon` branch: when `--daemon` flag set, INSTEAD of invoking `api.run()` directly, instantiate FastMCP client (Unix-socket transport, same socket path as `harness daemon`) → submit `run_workflow` tool call with manifest path + config dict → await response → emit `RunResult` per `--output` mode → exit per §14.18.2 mapping
- Connection error handling: socket path absent / connection refused → raises `RT-FAIL-CLI-DAEMON-CONNECTION` + exit code 4

**Acceptance criteria:**
1. `harness run minimal.yaml --daemon` connects to `harness daemon` running at default socket → submits `run_workflow` → receives RunResult → exit code 0 (SUCCESS)
2. `--socket-path` flag overrides default (must match daemon's socket path)
3. Daemon not running → `RT-FAIL-CLI-DAEMON-CONNECTION` + exit code 4
4. RunResult propagation: SUCCESS → exit 0; FAILED → exit 1; DRAINED → exit 1
5. Same workflow file → same RunResult between one-shot mode and daemon-client mode (semantic equivalence — verified via integration test with both modes against same fixture manifest)
6. CLI client SIGINT gracefully disconnects MCP session WITHOUT triggering daemon-side shutdown (daemon continues serving other clients)
7. Concurrent CLI clients: 2 `harness run ... --daemon` invocations against same daemon process → both complete independently (per-session ctx isolation per §14.18.5)

**Files:**
- EDIT `harness-runtime/src/harness_runtime/cli/app.py`

**Tests (NEW at `harness-runtime/tests/test_cli_daemon_client.py`):**
- 7 tests mapping to ACs above (subprocess-driven integration tests pairing `harness daemon` background process + `harness run --daemon` client invocations)

**Depends on:** U-RT-107 (daemon entrypoint exists; client connects to it)

---

### §1.9 U-RT-109 — E2E integration (real YAML manifest → CLI → workflow execution → RunResult)

**Implements:** Phase 2a Gate G6 closure verification — end-to-end demonstration that Track B CLI substrate operates against real workflows.

**Spec:** Cluster-close verification spanning §14.18 + §14.19 + §13.4 + §3.7 surfaces.

**Acceptance criteria:**
1. Fixture YAML manifest with INFERENCE_STEP single-step workflow + real Anthropic provider (deterministic prompt; verified RunResult.status SUCCESS) — one-shot mode
2. Same fixture in TOML format → equivalent RunResult (verifies §14.19.4 invariant 8 YAML↔TOML round-trip)
3. Same fixture in daemon mode → equivalent RunResult (verifies one-shot/daemon-client semantic equivalence)
4. Multi-step fixture (3 INFERENCE_STEPs sequential) → all 3 execute + RunResult.status SUCCESS
5. SIGINT mid-multi-step → RunResult.status DRAINED + partial-state populated + ledger-resumable next invocation
6. Daemon concurrent: 2 independent fixture workflows submitted concurrently → both complete independently
7. AS-8d skill activation: fixture with skill-activation step + operator-supplied SkillActivationHook → `skill.*` namespace span emitted (advances AS-8d toward RETIRED via real exercise)
8. OD-5 webhook delivery: fixture with HITL placement + operator-supplied webhook_config → `hitl.webhook.deliver` emission verified (advances OD-5 toward RETIRED via real exercise)
9. Manifest error path: malformed YAML → exit code 2 + fail-class to stderr
10. Config error path: invalid `harness.toml` → exit code 3 + fail-class to stderr

**Files:**
- NEW `harness-runtime/tests/integration/test_track_b_e2e.py`
- NEW `harness-runtime/tests/integration/fixtures/track_b/*.yaml` + `*.toml` (5-10 fixture manifests)

**Tests:**
- 10 integration tests mapping to ACs above
- Mechanism α/β/γ per FM-2 implementer-discretion: α=real Anthropic API (requires API key at test runtime; deselect via marker); β=mock provider (`harness_runtime.test_utils.MockProvider`); γ=mixed (real for SUCCESS-path; mock for failure-path)

**Depends on:** U-RT-108 (daemon-client mode lands; all sibling surfaces converge)

---

## §2 Dependency graph + DAG verification

### §2.1 Within-cluster edges (7)

| Edge | From | To | Type |
|---|---|---|---|
| 1 | U-RT-102 | U-RT-103 | linear (CLI parent app exists → config loader integrates) |
| 2 | U-RT-103 | U-RT-104 | linear (config supplies workspace root for default manifest path; loader tested standalone) |
| 3 | U-RT-104 | U-RT-105 | linear (loader skeleton + intermediate carrier exist → projection landing) |
| 4 | U-RT-105 | U-RT-106 | linear (LoadedWorkflow projection exists → one-shot consumes via api.run) |
| 5 | U-RT-103 | U-RT-106 | dependency (one-shot consumes RuntimeConfigSource.load) — sibling to edge 4 |
| 6 | U-RT-106 | U-RT-107 | linear (one-shot baseline exists → daemon reuses RuntimeConfigSource + bootstrap path) |
| 7 | U-RT-107 | U-RT-108 | linear (daemon entrypoint exists → client connects to it) |
| 8 | U-RT-108 | U-RT-109 | linear (all sibling surfaces converge at e2e) |

### §2.2 Cluster-boundary edges (1)

| Edge | From | To | Type |
|---|---|---|---|
| 1 | existing U-RT-62 (FastMCP server + run_workflow tool) | U-RT-107 | dependency (daemon entrypoint reuses HarnessMCPServer substrate) |

### §2.3 Cross-axis edges (0)

ZERO cross-axis edges per Phase 2a design substrate §9 + SF-1 §8 + spec v1.35 §14.18.5 + §14.19.6 verification. Track B is intra-runtime-axis.

### §2.4 DAG verification

Topological sort (Kahn's algorithm) on the 9-node graph (U-RT-102 through U-RT-109 + U-RT-62):

`U-RT-62 → U-RT-102 → U-RT-103 → U-RT-104 → U-RT-105 → U-RT-106 → U-RT-107 → U-RT-108 → U-RT-109`

Acyclic. Linear-chain shape with one cluster-boundary dependency at U-RT-107.

---

## §3 Adjacent observations (carry-forward)

(a) **AS-8d + OD-5 RETIRE-READY advancement at U-RT-109 e2e.** Per spec v1.35 §14.18 + §14.19 framing + AS-8d batch-25 + OD-5 batch-28 deployment-time-gate precedent: U-RT-109 AC #7 (skill activation) + AC #8 (webhook delivery) advance both substitutions toward RETIRED via first operator-exercised real workflow. Gate per X-AL-2: (units landed) ∧ (substituted H_E surface no longer invoked). U-RT-109 satisfies the first conjunct for both; the second conjunct (operator binds production substitution surface AT deployment) closes when operator runs `harness run` against a non-fixture workflow with real `skill_activation_hook_config` + `webhook_config` bound at `harness.toml`. Retirement event filing owed at first-real-workflow-exercise close (out-of-scope at U-RT-109 e2e which uses fixtures).

(b) **`harness inspect` + `harness shutdown` standalone-binary preservation.** Per §13.4 + Track A continuity discipline: U-RT-102 does NOT migrate `harness-inspect` (U-RT-47 LANDED) or `harness-shutdown` (U-RT-48 LANDED) under the `harness` parent dispatcher. The 2 standalone binaries continue per existing `[project.scripts]` registration. Future iteration-2 MAY add `harness inspect` + `harness shutdown` subcommands as aliases (preserves operator muscle memory). NOT in scope at v2.31.

(c) **strictyaml vs PyYAML choice.** Q-H=b at G1 ratification chose strictyaml over PyYAML for type-safe parse + rejection of implicit type coercion (e.g., `"yes"` → bool). U-RT-104 implementation MUST use strictyaml; PyYAML rejected per X-AL-3 discipline (Q-H=b rationale).

(d) **Typer vs Click vs argparse choice.** Q-I=c at G1 ratification chose Typer over Click + argparse for Pydantic-friendly type-annotation-driven flag generation + alignment with workspace Pydantic v2 stack discipline. U-RT-102 implementation MUST use Typer.

(e) **pydantic-settings vs hand-rolled choice.** §3.7 implementation discipline + CLAUDE.md §3.2 framework-pull discipline carve-out: framework-pull discipline ("Hand-rolled. Do NOT pull X") applies to retry/breaker/workflow-orchestration. General-purpose config-loading with canonical solution (pydantic-settings) is OUT of the framework-pull discipline scope. U-RT-103 implementation uses pydantic-settings; hand-rolled 3-source layering rejected.

(f) **Multi-document YAML manifests deferred to iteration-2.** Per Q-S2=no ratification at G2: single workflow per file at v1. Multi-document YAML (`---`-separated) is iteration-2 (composes with `harness run --workflow=<id>` selector). NOT in scope at v2.31.

(g) **Env-var interpolation deferred to iteration-2.** Per Q-S5=no ratification at G2: no `${VAR}` interpolation in manifest string fields at v1. Operators use `--<flag>` CLI precedence layer per A4. NOT in scope at v2.31.

(h) **JSON Schema shipping deferred to iteration-2.** Per Q-S4=no ratification at G2: no JSON Schema sidecar shipped at v1. Operator-facing schema docs at markdown only (`docs/workflow_manifest_schema.md` at Phase 2b doc arc). NOT in scope at v2.31.

(i) **NEW dep declarations (3).** U-RT-102: `typer>=0.12`; U-RT-103: `pydantic-settings>=2.0`; U-RT-104: `strictyaml>=1.7`. All 3 land at `harness-runtime/pyproject.toml` at the respective unit's landing arc. Cumulative `harness-runtime/pyproject.toml` growth: 3 NEW deps. No transitive dep concerns identified at v2.31 planning.

(j) **PR sequencing recommendation.** Given the 8-unit cluster scope + 3 NEW dep adds + e2e integration, PR-per-cluster (single PR landing U-RT-102 through U-RT-109) is the recommended shape — mirrors L9-decies / L9-undecies / L9-duodecies / L9-terdecies / L9-quaterdecies / L9-quindecies cluster precedents. Operator-discretion at impl arc opening.

(k) **`harness inspect` + `harness shutdown` interaction with `harness daemon`.** If daemon is running, what happens when operator invokes `harness-inspect` (standalone) or `harness-shutdown` (standalone)? `harness-inspect` reads PID file + admin-only state (read-only; safe). `harness-shutdown` writes shutdown signal (interacts with daemon). NOT in scope at v2.31 — existing U-RT-47 + U-RT-48 behavior preserved verbatim; interaction semantics documented at iteration-2 if surfacing as operational concern.

(l) **Adversarial review owed at G6 close.** Phase 2b implementation closure (U-RT-109 e2e LANDED) gates an adversarial review pass per workflow §4.1 discipline. Routing: per-cluster review at L9-sedecies close. Review scope: §14.18 + §14.19 + §13.4 + §3.7 contract conformance + 8-unit acceptance-criterion coverage + e2e integration completeness.

---

## §4 Filing footer

| Field | Value |
|---|---|
| Filed at | 2026-05-28 |
| Filer | Phase 7 sub-phase 7b Phase-2a Gate G5 substantive amendment authoring NEW L9-sedecies 8-unit cluster per `.harness/phase_2_track_b_design_substrate.md` v1.1 G1-RATIFIED + `.harness/class_1_fork_harness_run_yaml_manifest_schema.md` G2-RATIFIED + runtime spec v1.34 → v1.35 (G4 LANDED at `f51874a`) |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_30.md` (2026-05-28, U-RT-94 Reading-H absorption) |
| Co-publication | runtime spec v1.34 → v1.35 (G4 LANDED at `f51874a`) + workspace `CLAUDE.md` §2.4 runtime plan row bump (sibling commit this arc) |
| Cross-axis cascade | ZERO per design substrate §9 + SF-1 §8 + spec v1.35 §14.18.5 + §14.19.6 + this plan §0.3 + §2.3 |
| Unit count | 99 → 107 (+8 — U-RT-102 through U-RT-109) |
| Cluster designation | L9-sedecies (sequel to L9-quindecies at v2.28) |
| Status | ✅ FILED — Phase 2a Gate G5 closed. G6 Phase 2b implementation arc opens. |
| Gates remaining | G6 — U-RT-102 through U-RT-109 implementation per skill `phase-7-implementation` discipline; AS-8d + OD-5 deployment-time-gate close via first-real-workflow operator exercise (out-of-cluster carry per §3(a)) |
