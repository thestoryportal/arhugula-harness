# R-CL-Q1 Harness-Core Review Evidence Slice

Status: partial R-CL-Q1 evidence slice. This does not satisfy the final
`tools/q1_review_gate.py` all-package report; it records the completed
`harness-core` package review plus DevEx fixes surfaced while proving the
pre-merge check path.

Date: 2026-06-29
Branch: `r-cl-q1-harness-core-review`
Base: `origin/main` at `60334ad0`

## Scope

- `harness-core/src/harness_core/*.py`
- `harness-core/tests/*.py`
- `harness-core/pyproject.toml`
- `justfile` pre-merge check entry point
- `harness-runtime/src/harness_runtime/cli/app.py`
- `harness-runtime/tests/test_cli_daemon.py`

## Review Lanes

| Lane | Status | Evidence | Findings |
|---|---|---|---|
| `codex` | passed | Direct source/test review of all `harness-core` carriers, public exports, and package metadata. | No package-local defects found. |
| `code_review` | passed | Bug/regression review focused on enum closure, NewType identity, frozen Pydantic policy behavior, public API reexports, and test coverage. | No open findings in `harness-core`. |
| `simplify` | passed | Simplification scan for duplicate carriers, unused abstractions, TODO/FIXME markers, dead branches, and avoidable control flow. | No simplification changes needed in `harness-core`. |

## Harness-Core Observations

- `DeploymentSurface`, `PersonaTier`, `WorkflowEventClass`,
  `WorkloadClass`, `AttributeValueType`, and `Cardinality` are closed
  `StrEnum` carriers with byte-exact string values.
- `identity.py` keeps the shared identity surface as `NewType` aliases; the
  runtime-axis `SkillID` and `ClientName` aliases are exported from
  `harness_core.__all__`.
- `SandboxDecisionPolicy` is intentionally an empty frozen Pydantic v2 marker
  model with `extra="forbid"` and a `.default()` factory.
- The package tests cover enum cardinality and values, closure-by-subclassing
  failures, identity alias distinctness, public reexports, empty-marker policy
  behavior, and workload-class residency.

## DevEx Findings Fixed

### `just check` workspace sync

Fresh-environment test execution exposed that the documented pre-merge
`just check` path did not synchronize workspace editables before invoking
`uv run pytest`. The reproducer:

```bash
UV_PROJECT_ENVIRONMENT=/tmp/arhugula-q1-fresh-check-venv \
  UV_CACHE_DIR=/tmp/arhugula-uv-cache \
  uv run pytest harness-core/tests -q
```

failed during collection with `ModuleNotFoundError: No module named
'harness_core'` because the fresh environment installed root dependencies but
not the workspace packages. The existing `codex-sync` recipe already performs
the correct `uv sync --all-packages`; `just check` now depends on that sync
step before lint, typecheck, and tests.

### Daemon Unix-socket startup path

The full `just check` path also exposed a live-key local DevEx failure in
`test_ac1_e2e_daemon_subprocess_binds_socket_and_shuts_down`: with
`ANTHROPIC_API_KEY` present, the subprocess smoke test ran and passed the
daemon a pytest nested Unix-socket path long enough to trigger
`OSError: AF_UNIX path too long` on macOS. That failure also showed that
`_daemon_main` did not retrieve and wrap an exception from a completed
`uvicorn-serve` task, so the subprocess could exit 0 even though the server
never bound the socket.

The fix keeps the smoke-test socket under a short `/tmp` path and updates
`_daemon_main` to await the completed server task, wrapping bind/startup
exceptions as `DaemonStartupError`.

## Verification Evidence

- RED artifact witness: `rtk run "test -f .harness/r-cl-q1-harness-core-review.md"`
  failed before this evidence file existed.
- RED DevEx witness: the fresh-environment `uv run pytest harness-core/tests -q`
  command above failed with missing `harness_core` imports before the
  `justfile` change.
- RED daemon witness: escalated `just check` reached the live daemon smoke and
  failed with `AF_UNIX path too long`; the daemon subprocess exited before
  binding the socket with code 0 because the uvicorn task exception was not
  surfaced.
- Baseline after workspace sync:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pytest harness-core/tests -q`
  passed with `26 passed`.
- Baseline after workspace sync:
  `UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pyright harness-core`
  passed with `0 errors, 0 warnings, 0 informations`.
- Provider-free daemon regression check:
  `env -u ANTHROPIC_API_KEY -u OPENAI_API_KEY -u E2B_API_KEY -u GOOGLE_APPLICATION_CREDENTIALS -u GOOGLE_CLOUD_PROJECT UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pytest harness-runtime/tests/test_cli_daemon.py -q`
  passed with `18 passed, 1 skipped`.
- Provider-free PR gate:
  `just codex-check` passed after workspace sync, ruff, pyright, and
  `pytest -m "not e2e"` with provider credentials stripped by the recipe
  (`5143 selected`, `24 deselected`).

## Q1 Rollup Notes

This slice is ready to be folded into the eventual
`.harness/r-cl-q1-review.json` final report as the `harness-core` package
evidence. Remaining final Q1 obligations still include all other required
packages, `tools/`, `harness.toml.example`, a complete clean-checkout
walkthrough, and a passing fixed-point `just check` record. An ambient
`just check` run in this worktree loaded live provider credentials from `.env`
and was interrupted to avoid further paid/provider calls; the provider-free
gate for this slice is `just codex-check`.
