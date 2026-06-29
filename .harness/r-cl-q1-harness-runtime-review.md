# R-CL-Q1 Harness-Runtime Review Evidence Slice

Status: partial R-CL-Q1 evidence slice. This does not satisfy the final
`tools/q1_review_gate.py` all-package report; it records the completed
`harness-runtime` package review for later rollup into the final Q1 artifact.

Date: 2026-06-29
Branch: `codex/r-cl-q1-harness-runtime-review`
Base: local `main` at `6f768fba` (`ops: roadmap status refresh post-#829 (#830)`)

## Scope

- `harness-runtime/src/harness_runtime/**/*.py`
- `harness-runtime/tests/**/*.py`
- `harness-runtime/pyproject.toml`

There is no package-local `harness-runtime/AGENTS.md`; the root Codex
compatibility instructions apply to this package review.

## Review Lanes

| Lane | Status | Evidence | Findings |
|---|---|---|---|
| `codex` | passed | Direct source/test review of the runtime package inventory, package metadata, CLI/API/config surfaces, bootstrap stage composition, provider/MCP/LLM/tool/HITL lifecycle boundaries, and semantic overlay carriers for runtime contracts and units. | No package-local defects found. |
| `code_review` | passed | Bug/regression review focused on typed failure surfaces, manifest strictness, provider degradation behavior, per-run context isolation, effect fencing, sandbox/trust gates, and local-loopback integration coverage. | No open findings in `harness-runtime`. |
| `simplify` | passed | Simplification scan for TODO/FIXME markers, dead stubs, broad silent fallbacks, duplicated authority, implicit network/process effects, and over-broad runtime abstractions. | No simplification changes needed in `harness-runtime`. |

## Harness-Runtime Observations

- `harness-runtime` contains 137 source `.py` files, `py.typed`, 179 test
  `.py` files, and 110,250 total source/test lines. The package is broad
  because it is the composition root for bootstrap, provider SDK lifecycle,
  MCP client/server hosting, tracing, collector supervision, CLI/admin
  entrypoints, and workflow dispatch.
- Package metadata matches that role. `harness-runtime` depends on all axis
  packages plus provider SDKs, MCP, keyring/Google Secret Manager, OpenTelemetry,
  Typer, Pydantic settings, and PyYAML. The optional `embedding` extra isolates
  `fastembed` / `onnxruntime` from the default provider-free path.
- Console scripts are explicit: `harness`, `harness-inspect`, and
  `harness-shutdown`. CLI one-shot and daemon modes live in
  `cli/app.py`, with typed exit codes for workflow, manifest, config, and
  bootstrap failures.
- Runtime side-effect hits are expected rather than suspicious. This package is
  where provider clients, MCP transports, subprocess-backed stdio clients,
  sockets, env-backed config, keyring/secret backends, local files, and
  OpenTelemetry process-global registration are intentionally admitted. The
  review focus was therefore explicit boundary placement and fail-loud behavior,
  not absence of those effects.
- The Python API in `api.py` owns the `run()` / `resume()` operator entrypoint,
  `WorkflowObject` structural protocol, process-level concurrency/drain guards,
  resume guardrails, CP-driver invocation, and runtime `RunResult` projection.
  The API rejects invalid workflow/resume states before bootstrap instead of
  silently re-running or reporting false success.
- Config loading keeps precedence and drift visible. `config/loader.py`
  materializes `RuntimeConfig` from defaults, `HARNESS_*` env keys, and kwargs
  with kwargs last. Behavior-changing scalar gates such as effect fencing and
  routing activation are env-keyed; comments call out known non-env-keyed gaps
  instead of implying full env coverage.
- Provider secret resolution is typed. `config/provider_secrets.py` checks AS
  allowlists when a tool contract is supplied, maps keyring misses/unavailable
  backends to AS fail classes, and keeps vendor env-var fallback behind the
  configured backend path.
- Manifest loading is strict at the loader boundary. `strict_safe_loader.py`
  bans duplicate mapping keys, non-empty flow style, anchors, and aliases while
  preserving native scalar typing; `workflow_manifest_loader.py` maps parse,
  version, schema, enum, duplicate-step, and admissibility failures into typed
  CLI/runtime exceptions. YAML/TOML payloads project to frozen
  `LoadedWorkflow` values.
- Bootstrap stage 5 is the runtime composition hub. It binds override,
  topology, lifecycle, memory, skill, tool, HITL, pause/resume, webhook,
  LLM, sub-agent, inter-step, engine-output, cost, and sync-dispatcher
  surfaces in dependency order, with explicit guards when earlier stages
  should have populated required context.
- Provider construction is bounded and explicit. `providers.py` retries only
  transient provider construction failures, keeps auth/secret failures
  permanent unless the provider is marked optional, degrades optional providers
  with warnings, and raises `RT-FAIL-PROVIDER-NONE-CONFIGURED` when an
  inference workflow would otherwise have no provider.
- `mcp_server.py` separates H_T-as-MCP-server hosting from MCP client hosts,
  uses FastMCP transport security settings for allowed loopback hosts/origins,
  handles workflow-id-as-path daemon input, and isolates concurrent
  `run_workflow` invocations with `ContextVar`-scoped MCP tool context,
  inter-step channel, and cost accumulator holders.
- `mcp_client_host.py` owns the MCP client side: startup opens the selected
  stdio/streamable-http/SSE transport, performs protocol initialize,
  populates a `ToolRegistry`, and unwinds partial resources on startup failure.
  `health_check`, `shutdown`, and `call_tool` reject use before start.
- `llm_dispatch.py` keeps per-step LLM dispatch stateless around frozen
  provider/tracer/cost/prompt/routing substrates. It coerces payloads to the
  provider-agnostic shape, raises typed payload/provider/prompt-selection
  failures, emits GenAI/cost attributes, and routes memory/tool-loop/inter-step
  behavior through explicit optional substrates.
- `runtime_tool_dispatcher.py` resolves the owning MCP host through a routing
  index, validates tool payload shape, evaluates per-server trust on every
  dispatch, enforces sandbox tier floors, emits sandbox/MCP spans, resolves
  required secrets, composes idempotency keys, and applies effect fencing for
  non-idempotent effects on durable runs.
- Observability lifecycle is explicit. `tracer_provider.py` enforces one
  runtime global registration per process; `collector_daemon.py` materializes a
  supervisor scaffold with typed health and bounded stop semantics while clearly
  marking live OTLP receiver/storage as a future sub-unit.
- Tests are correspondingly broad: synced `harness-runtime/tests` covers 2,179
  passing tests, 22 skips, and 1 xfail under the provider-free/local-loopback
  run used for this slice.

## Simplification Notes

- Source-level `TODO` / `FIXME` markers were not found in the reviewed source
  scan. `deferred`, `stub`, and `NotImplemented` hits are numerous, but they are
  mostly spec-governed deferral notes, admin placeholder CLI descriptions, type
  protocol scaffolding, or test fakes. No hidden runtime TODO was identified in
  the reviewed high-risk modules.
- Broad `Any`, `cast`, and `type: ignore` usage is concentrated at runtime
  boundaries where external SDKs, OpenTelemetry handles, FastMCP, PyYAML, MCP
  transports, and cross-axis structural protocols enter. The package already
  contains typed local carriers and fail classes around those boundaries.
- The package intentionally has many lifecycle modules. Collapsing provider,
  MCP, dispatch, HITL, pause/resume, cost, memory, and sandbox logic into fewer
  files would reduce file count but increase blast radius and obscure boundary
  ownership.
- The collector daemon and admin CLI stubs remain documented framework
  scaffolds. They are not silently advertised as complete live collector/admin
  backends in this review slice.
- The runtime test suite has one environment-sensitive fixture class: local
  streamable-HTTP MCP e2e tests require permission to bind `127.0.0.1` on an
  ephemeral port. Sandboxed pytest fails that fixture with `PermissionError`;
  the escalated rerun passes the full suite.

## Overlay Grounding

- `rtk just overlay-query --contract C-RT-05` resolved to provider lifecycle
  carriers including `bootstrap/stage_3a_cp_clients.py`,
  `lifecycle/providers.py`, `lifecycle/llm_dispatch.py`, and `types.py`.
- `rtk just overlay-query --contract C-RT-06` resolved to tracing consumers
  including `lifecycle/tracer_provider.py`, `lifecycle/span_processor.py`,
  `lifecycle/llm_dispatch.py`, `lifecycle/mcp_server.py`,
  `lifecycle/retry_breaker_fallback.py`, and `lifecycle/sub_agent_dispatch.py`.
- `rtk just overlay-query --contract C-RT-07` resolved to collector/OD
  lifecycle files including `lifecycle/collector_daemon.py`,
  `lifecycle/audit_writer.py`, `lifecycle/cost_attribution.py`,
  `lifecycle/ring_buffer.py`, and `types.py`.
- `rtk just overlay-query --contract C-RT-08` resolved to `api.py`,
  `__init__.py`, `lifecycle/child_workflow_runner.py`,
  `lifecycle/collector_daemon.py`, and `lifecycle/tracer_provider.py`.
- `rtk just overlay-query --contract C-RT-15` resolved to the expected LLM
  dispatch chain: `bootstrap/stage_5_loop_init.py`,
  `lifecycle/llm_dispatch.py`, `lifecycle/hitl_gate_composer.py`,
  `lifecycle/retry_breaker_fallback.py`, `lifecycle/sync_dispatcher_facade.py`,
  memory/managed-agent modules, CP workflow driver/manifest carriers, and
  `types.py`.
- `rtk just overlay-query --contract C-RT-18` resolved to HITL composition
  files including `api.py`, `bootstrap/stage_5_loop_init.py`,
  `lifecycle/hitl_gate_composer.py`, CP HITL/validator carriers, and `types.py`.
- `rtk just overlay-query --contract C-RT-19` resolved to the tool dispatch
  chain including `bootstrap/factories/runtime_tool_dispatcher_factory.py`,
  `bootstrap/stage_5_loop_init.py`, `lifecycle/runtime_tool_dispatcher.py`,
  sandbox execution drivers, retry/tool wrappers, MCP-backed ask-user surface,
  and `types.py`.
- `rtk just overlay-query --contract C-RT-29` resolved to the CLI files:
  `cli/__init__.py`, `cli/__main__.py`, and `cli/app.py`.
- `rtk just overlay-query --contract C-RT-30` resolved to
  `lifecycle/strict_safe_loader.py` and `lifecycle/workflow_manifest_loader.py`.
- `rtk just overlay-query --contract C-RT-31` resolved to effect-fence and
  engine-output surfaces including `config/loader.py`, `config_source.py`,
  `lifecycle/effect_fence.py`, `lifecycle/engine_output_store.py`,
  `lifecycle/runtime_tool_dispatcher.py`, `lifecycle/llm_dispatch.py`,
  managed-agent dispatch, CP pause/resume/driver carriers, and `types.py`.
- `rtk just overlay-query --contract C-RT-34` resolved to inter-step/cost
  isolation surfaces including `api.py`, `bootstrap/stage_5_loop_init.py`,
  `lifecycle/inter_step_output_channel.py`, `lifecycle/cost_record_sink.py`,
  `lifecycle/llm_dispatch.py`, `lifecycle/mcp_server.py`, CP driver, and
  `types.py`.
- `rtk just overlay-query --contract C-RT-35` resolved to runtime resume
  surfaces in `api.py` and `lifecycle/mcp_server.py` plus CP pause/resume and
  workflow-driver carriers.
- Unit queries for `U-RT-52`, `U-RT-62`, `U-RT-67`, `U-RT-102`, `U-RT-104`,
  and `U-RT-105` resolved to the expected implementation files for LLM
  dispatch, MCP server/client wiring, tool dispatch, CLI scaffolding, and
  manifest loading/projection.

## Verification Evidence

- RED artifact witness:
  `rtk proxy /bin/test -f .harness/r-cl-q1-harness-runtime-review.md` failed
  before this evidence file existed.
- Source inventory:
  `rtk rg --files harness-runtime/src/harness_runtime` listed 137 source
  `.py` files under `admin`, `bootstrap`, `cli`, `config`, and `lifecycle`.
- Test inventory:
  `rtk rg --files harness-runtime/tests` listed 179 test `.py` files.
- Source/test size inventory:
  `rtk wc -l ...` over runtime source and tests reported 110,250 total
  source/test lines.
- Package-local instruction check:
  `rtk proxy /bin/test -f harness-runtime/AGENTS.md` failed; there is no
  runtime-local `AGENTS.md`, so root instructions apply.
- Fresh-worktree direct package test before workspace sync:
  `rtk proxy /usr/bin/env UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pytest harness-runtime/tests -q`
  failed during collection with missing imports for workspace packages such as
  `harness_core`, `harness_as`, `harness_cp`, `harness_is`, `harness_od`, and
  `harness_runtime`. This is the expected editable-sync boundary that
  `just codex-sync` and `just codex-check` cover.
- Fresh-worktree direct package typecheck before workspace sync:
  `rtk proxy /usr/bin/env UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pyright harness-runtime`
  failed with missing workspace imports and unknown types at the same
  editable-sync boundary.
- Pre-sync package lint:
  `rtk proxy /usr/bin/env UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run ruff check harness-runtime`
  passed with `All checks passed!`.
- Workspace sync:
  sandboxed `rtk proxy /usr/bin/env UV_CACHE_DIR=/tmp/arhugula-uv-cache just codex-sync`
  failed because `hatchling` was not in the local resolver cache and sandboxed
  DNS could not reach PyPI. Escalated rerun of the same command passed and
  installed all seven workspace packages.
- Package tests after workspace sync, sandboxed:
  `rtk proxy /usr/bin/env UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pytest harness-runtime/tests -q`
  ran the suite and failed only
  `harness-runtime/tests/integration/test_r100_ac2_tool_step_e2e.py::test_r100_ac2_tool_step_via_api_run`
  because the sandbox denied binding a local `127.0.0.1` ephemeral socket
  (`PermissionError: [Errno 1] Operation not permitted`).
- Package tests after workspace sync, local-loopback enabled:
  escalated `rtk proxy /usr/bin/env UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pytest harness-runtime/tests -q`
  passed with `2179 passed, 22 skipped, 1 xfailed, 16 warnings` in 153.99s.
  Warnings were provider-degraded notices for absent Anthropic/OpenAI keyring
  entries in optional-provider live-ollama integration paths.
- Package typecheck:
  `rtk proxy /usr/bin/env UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pyright harness-runtime`
  passed with `0 errors, 0 warnings, 0 informations`.
- Package lint:
  `rtk proxy /usr/bin/env UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run ruff check harness-runtime`
  passed with `All checks passed!`.
- Provider-free repo gate, sandboxed:
  `rtk proxy /usr/bin/env UV_CACHE_DIR=/tmp/arhugula-uv-cache just codex-check`
  passed workspace sync, ruff, and pyright, then failed only
  `test_r100_ac2_tool_step_via_api_run` because the sandbox denied the same
  local `127.0.0.1` ephemeral socket bind. The pytest lane otherwise reported
  `5131 passed, 10 skipped, 24 deselected, 1 xfailed`.
- Provider-free repo gate, local-loopback enabled:
  escalated `rtk proxy /usr/bin/env UV_CACHE_DIR=/tmp/arhugula-uv-cache just codex-check`
  passed with workspace sync, `ruff check .`, `pyright`, and provider-free
  pytest `5132 passed, 10 skipped, 24 deselected, 1 xfailed`.
- External review:
  escalated `rtk proxy /usr/bin/env UV_CACHE_DIR=/tmp/arhugula-uv-cache just codex-review-uncommitted`
  ran with session `019f1524-9d41-70a3-8942-06ca97473bf6` and reported no
  actionable defect introduced by the untracked markdown evidence slice.

## Q1 Rollup Notes

This slice is ready to be folded into the eventual
`.harness/r-cl-q1-review.json` final report as the `harness-runtime` package
evidence. Remaining final Q1 obligations still include `tools/`, `justfile`,
`harness.toml.example`, a complete clean-checkout walkthrough, and a passing
fixed-point `just check` record. The provider-free loop gate for this slice is
`just codex-check`; ambient `just check` is not run by Codex here because
`.env` may load live provider credentials and trigger paid/provider exercises
outside this package evidence slice.
